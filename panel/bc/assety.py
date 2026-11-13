# -*- coding: utf-8 -*-
"""Assety: okno (tylko do odczytu) na rejestr grafik gry — assets/manifest.json.

Rejestr prowadzi pipeline grafik (skill `.claude/skills/asset/`, narzędzie `tools/manifest.py`). Każdy asset idzie
tą samą drogą: generowanie → obróbka → Figma → ZGODA CZŁOWIEKA → Roblox. Ten moduł niczego nie zmienia, nie wgrywa
i nie zatwierdza: czyta manifest, tłumaczy statusy na polski i oddaje gotowe obrazy z assets/processed/.
Zgodę na upload do Roblox daje wyłącznie człowiek w rozmowie z agentem (agent zapisuje ją poleceniem
`python tools/manifest.py approve <Nazwa>` dopiero po wyraźnym „tak”) — panel pokazuje tylko, co na nią czeka.

Trasy (same GET):
    /api/assety                      rejestr: assety, liczniki statusów, etapy pipeline'u
    /api/assety/plik/<nazwa>         gotowy obraz assetu (plik z pola `processed` manifestu)
    /api/assety/miniatura/<nazwa>    pomniejszony obraz do siatki kart (z biblioteką Pillow; bez niej pełny plik)

Bezpieczeństwo plików: adres zawiera tylko NAZWĘ assetu, nigdy ścieżkę. Ścieżkę bierzemy z manifestu i sprawdzamy,
że po rozwiązaniu („..”, dowiązania, litery dysków) leży w assets/processed/ w repozytorium i ma rozszerzenie obrazu.
Nic z assets/raw/, nic spoza repozytorium. Miniatury żyją tylko w pamięci serwera (zero zapisu na dysk).
"""
import datetime
import hashlib
import io
import json
import os
import re
import stat
import struct
import threading
import urllib.parse

from . import rdzen
from .http import Odp
from .rdzen import BladHTTP

ZRODLO = "assets/manifest.json"
KATALOG_OBRAZOW = "assets/processed"
ROZSZERZENIA_OBRAZOW = (".png", ".jpg", ".jpeg", ".webp", ".gif")
LIMIT_MANIFESTU = 16 * 1024 * 1024                             # większego pliku nie czytamy (to nie jest rejestr)
LIMIT_ASSETOW = 5000
BOK_MINIATURY = 384                                            # dłuższy bok miniatury w pikselach
LIMIT_PLIKU_MINIATURY = 64 * 1024 * 1024
LIMIT_PIKSELI_MINIATURY = 40 * 1000 * 1000                     # ponad 40 Mpx (ok. 160 MB w RGBA) — bez miniatury
LIMIT_PAMIECI_MINIATUR = 400                                   # tyle miniatur trzymamy w pamięci naraz
MAKS_TEKST = 4000

# Etapy pipeline'u w kolejności. `etap` assetu to indeks na tej liście.
ETAPY = (
    {"id": "generowanie", "nazwa": "Generowanie", "skrot": "Generacja",
     "opis": "Plan assetu i warianty z Higgsfield."},
    {"id": "obrobka", "nazwa": "Obróbka", "skrot": "Obróbka",
     "opis": "Wycięcie tła, przycięcie i rozmiar docelowy."},
    {"id": "figma", "nazwa": "Figma", "skrot": "Figma",
     "opis": "Biblioteka assetów albo komponent w pliku projektu."},
    {"id": "zgoda", "nazwa": "Zgoda człowieka", "skrot": "Zgoda", "bramka": True,
     "opis": "Człowiek ogląda gotowy obraz i mówi agentowi „tak”."},
    {"id": "roblox", "nazwa": "Roblox", "skrot": "Roblox",
     "opis": "Upload, numer obrazu i moduł AssetIds."},
)

# Statusy z tools/manifest.py: status -> (nazwa po polsku, indeks etapu albo None, wyjaśnienie).
STATUSY = {
    "planned": ("zaplanowany", 0, "Zaplanowany — jeszcze nic nie wygenerowano."),
    "generated": ("wygenerowany", 0, "Warianty są wygenerowane — czekają na wybór i obróbkę."),
    "processed": ("obrobiony", 1, "Obrobiony (tło, przycięcie, rozmiar) — następna jest Figma."),
    "in_figma": ("w Figmie", 2, "Jest w Figmie — następna jest zgoda człowieka przed Roblox."),
    "awaiting_approval": ("czeka na zgodę", 3,
                          "Czeka na zgodę człowieka. Bez wyraźnego „tak” w rozmowie z agentem nic nie trafi do Roblox."),
    "approved": ("zatwierdzony", 3, "Człowiek się zgodził — agent może wgrać obraz do Roblox."),
    "pending_studio": ("czeka na Studio", 4,
                       "Wgrany do Roblox, ale Studio było niedostępne — brakuje numeru obrazu albo wpisu w AssetIds."),
    "in_roblox": ("w Roblox", 4, "Jest w Roblox i ma numer obrazu."),
    "done": ("gotowy", 4, "Gotowy — cały pipeline zakończony."),
    "rejected": ("odrzucony", None, "Odrzucony — nie trafi do gry."),
}

KATEGORIE = {"icon": "ikona", "button": "przycisk", "item": "przedmiot", "pet": "pet", "currency": "waluta",
             "frame": "ramka", "background": "tło", "keyart": "key art"}

# Pola wpisu, które panel rozumie; pozostałe proste wartości trafiają do `inne` (bez niczego, co wygląda na sekret).
POLA_ZNANE = {"category", "status", "usage", "notes", "processed", "raw", "prompt", "figma_node", "roblox_target",
              "roblox_decal", "roblox_image", "moderation", "created_at", "updated_at", "history", "approved_by_user",
              "approved_sha256", "approved_at"}
POLA_CZASU_HISTORII = ("replaced_at", "at", "time", "date", "czas")
OPISY_HISTORII = {"roblox_image": "Poprzedni numer obrazu Roblox", "roblox_decal": "Poprzedni numer decala Roblox"}

RX_STERUJACE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
RX_SEKRET = re.compile(r"key|token|secret|sekret|hasl|hasł|passw|klucz|credential|cookie|bearer|authoriz", re.I)
RX_FIGMA_PLIK = re.compile(r"^[A-Za-z0-9]{10,64}$")
RX_FIGMA_WEZEL = re.compile(r"^[A-Za-z0-9:;\-]{1,120}$")
# nazwa w adresie obrazu musi być też poprawną nazwą pliku na Windows (lustro zapisuje obraz pod tym adresem):
# bez ukośników, ? # %, znaków sterujących, < > : " | * i bez kropki albo spacji na końcu
RX_NAZWA_W_ADRESIE = re.compile(r"^[^/\\?#%<>:\"|*\x00-\x1f\x7f]{0,119}[^/\\?#%<>:\"|*\x00-\x1f\x7f. ]$")
RX_NAZWA_PLIKU = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,99}$")

_blokada = threading.Lock()
_pamiec = {"klucz": None, "dane": None, "blad": None, "indeks": None, "indeks_dla": None}
_obrazy = {}                                                   # pełna ścieżka -> informacje o pliku obrazu
_miniatury = {}                                                # (ścieżka, mtime_ns, rozmiar) -> (bajty, mime) | None
_pil = {"sprawdzono": False, "format": None}


# --------------------------------------------------------------------------- manifest
def plik_manifestu():
    return os.path.join(rdzen.REPO, "assets", "manifest.json")


def manifest():
    """Czyta assets/manifest.json. Zwraca (dane, blad): dane = słownik z pliku albo None; blad = komunikat po polsku,
    gdy plik jest, ale nie da się go odczytać. Brak pliku to (None, None) — rejestr po prostu jeszcze nie powstał.

    Pamięć podręczna po czasie modyfikacji i rozmiarze pliku: bez zmiany na dysku nic nie jest czytane ponownie."""
    sciezka = plik_manifestu()
    try:
        st = os.stat(sciezka)
    except OSError:
        return None, None
    klucz = (sciezka, st.st_mtime_ns, st.st_size)
    with _blokada:
        if _pamiec["klucz"] == klucz:
            return _pamiec["dane"], _pamiec["blad"]
    dane, blad = None, None
    if st.st_size > LIMIT_MANIFESTU:
        blad = "Plik %s jest za duży (%.1f MB) — panel go nie czyta." % (ZRODLO, st.st_size / 1048576)
    else:
        try:
            with open(sciezka, encoding="utf-8-sig") as f:
                dane = json.load(f)
        except json.JSONDecodeError as e:
            blad = ("Nie mogę odczytać %s: błąd składni w wierszu %d, kolumnie %d. Plik jest uszkodzony albo "
                    "właśnie zapisywany." % (ZRODLO, e.lineno, e.colno))
        except UnicodeDecodeError:
            blad = "Nie mogę odczytać %s: plik nie jest zapisany w UTF-8." % ZRODLO
        except OSError as e:
            # bez str(e): komunikat systemu niesie pełną ścieżkę na tym komputerze, a `blad` widzi gość i lustro
            blad = "Nie mogę odczytać %s (%s)." % (ZRODLO, e.strerror or e.__class__.__name__)
        except (ValueError, RecursionError) as e:
            blad = "Nie mogę odczytać %s (%s)." % (ZRODLO, str(e)[:120] or e.__class__.__name__)
        else:
            if not isinstance(dane, dict):
                dane, blad = None, "Plik %s ma nieoczekiwany kształt: powinien być obiektem z polem „assets”." % ZRODLO
    with _blokada:
        _pamiec.update(klucz=klucz, dane=dane, blad=blad, indeks=None, indeks_dla=None)
    return dane, blad


def _tekst(v, maks=MAKS_TEKST):
    """Wartość z manifestu → tekst bez znaków sterujących, przycięty do `maks`. Słowniki, listy i None dają ""."""
    if v is None or isinstance(v, (dict, list)):
        return ""
    if isinstance(v, bool):
        return "tak" if v else "nie"
    if isinstance(v, float) and v.is_integer():
        v = int(v)                                             # numer zapisany jako liczba: 1.33e14 -> 133130837278176
    return RX_STERUJACE.sub("", str(v)).strip()[:maks]


def _czas(v):
    """Znacznik czasu z manifestu: zwraca go bez zmian, jeśli jest w ISO 8601, inaczej None."""
    if not isinstance(v, str) or not v.strip():
        return None
    v = v.strip()[:40]
    try:
        datetime.datetime.fromisoformat(v[:-1] + "+00:00" if v.endswith(("Z", "z")) else v)
    except ValueError:
        return None
    return v


def _wpisy(dane):
    """Manifest → lista (nazwa, wpis). Format z tools/manifest.py to słownik nazwa → wpis; na wszelki wypadek czytamy
    też listę wpisów z polem „name”. Wpis, który nie jest słownikiem, traktujemy jak pusty; powtórzone nazwy pomijamy."""
    surowe = dane.get("assets") if isinstance(dane, dict) else None
    if isinstance(surowe, dict):
        pary = list(surowe.items())
    elif isinstance(surowe, list):
        pary = [(w.get("name") or w.get("nazwa"), w) for w in surowe if isinstance(w, dict)]
    else:
        pary = []
    wynik, widziane = [], set()
    for nazwa, wpis in pary[:LIMIT_ASSETOW]:
        nazwa = _tekst(nazwa, 120)
        if not nazwa or nazwa in widziane:
            continue
        widziane.add(nazwa)
        wynik.append((nazwa, wpis if isinstance(wpis, dict) else {}))
    return wynik


def _indeks():
    """Słownik nazwa → wpis dla aktualnego manifestu (None, gdy manifestu nie ma). Budowany raz na wersję pliku."""
    dane, _ = manifest()
    if dane is None:
        return None
    with _blokada:
        if _pamiec["indeks_dla"] is dane and _pamiec["indeks"] is not None:
            return _pamiec["indeks"]
    indeks = dict(_wpisy(dane))
    with _blokada:
        _pamiec.update(indeks=indeks, indeks_dla=dane)
    return indeks


# --------------------------------------------------------------------------- pliki obrazów
def _katalog_obrazow():
    """Rozwiązana ścieżka assets/processed/ albo None, gdy sam katalog prowadzi poza repozytorium."""
    return rdzen.w_katalogu(rdzen.REPO, KATALOG_OBRAZOW)


def sciezka_obrazu(zapis, baza=None):
    """Pole `processed` z manifestu → (pełna ścieżka, ścieżka w repozytorium, None) albo (None, None, powód odmowy).

    Pusta wartość daje (None, None, None). Dopuszczamy wyłącznie pliki, które po rozwiązaniu ścieżki leżą w
    assets/processed/ i mają rozszerzenie obrazu. Plik nie musi istnieć — to sprawdza wołający."""
    if not isinstance(zapis, str) or not zapis.strip():
        return None, None, None
    baza = baza or _katalog_obrazow()
    pelna = rdzen.w_katalogu(rdzen.REPO, zapis.strip())
    if not baza or not pelna or not os.path.normcase(pelna).startswith(os.path.normcase(baza) + os.sep):
        return None, None, ("Ścieżka obrazu w manifeście nie leży w %s/ — panel takiego pliku nie pokazuje."
                            % KATALOG_OBRAZOW)
    czesci = [c for c in zapis.strip().replace("\\", "/").split("/") if c not in ("", ".")]
    # rozszerzenie sprawdzamy dwa razy: w zapisie z manifestu i w pliku, do którego ten zapis naprawdę prowadzi
    # (dowiązanie albo windowsowe „obraz.png.” potrafią wskazywać coś innego, niż sugeruje nazwa)
    for nazwa_pliku in (czesci[-1], pelna):
        if os.path.splitext(nazwa_pliku)[1].lower() not in ROZSZERZENIA_OBRAZOW:
            return None, None, "Plik z manifestu nie jest obrazem PNG, JPG, WEBP ani GIF — panel go nie pokazuje."
    return pelna, "/".join(czesci), None


def wymiary_obrazu(sciezka):
    """(szerokość, wysokość) z nagłówka pliku PNG, GIF, WEBP albo JPG; None, gdy się nie da. Czyta tylko początek
    pliku i nie potrzebuje Pillow."""
    try:
        with open(sciezka, "rb") as f:
            b = f.read(32)
            wynik = None
            if b[:8] == b"\x89PNG\r\n\x1a\n" and b[12:16] == b"IHDR":
                wynik = struct.unpack(">II", b[16:24])
            elif b[:6] in (b"GIF87a", b"GIF89a"):
                wynik = struct.unpack("<HH", b[6:10])
            elif b[:4] == b"RIFF" and b[8:12] == b"WEBP" and len(b) >= 30:
                rodzaj = b[12:16]
                if rodzaj == b"VP8X":
                    wynik = (1 + int.from_bytes(b[24:27], "little"), 1 + int.from_bytes(b[27:30], "little"))
                elif rodzaj == b"VP8L":
                    bity = int.from_bytes(b[21:25], "little")
                    wynik = ((bity & 0x3FFF) + 1, ((bity >> 14) & 0x3FFF) + 1)
                elif rodzaj == b"VP8 ":
                    wynik = (int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF)
            elif b[:2] == b"\xff\xd8":
                f.seek(2)
                for _ in range(400):                           # kolejne segmenty JPG aż do ramki z wymiarami (SOF)
                    bajt = f.read(1)
                    while bajt and bajt != b"\xff":
                        bajt = f.read(1)
                    while bajt == b"\xff":
                        bajt = f.read(1)
                    if not bajt:
                        break
                    kod = bajt[0]
                    if kod in (0x01, 0xD8) or 0xD0 <= kod <= 0xD7:
                        continue                               # znaczniki bez długości
                    if kod in (0xD9, 0xDA):
                        break                                  # koniec nagłówków bez ramki
                    dl = f.read(2)
                    if len(dl) < 2:
                        break
                    if 0xC0 <= kod <= 0xCF and kod not in (0xC4, 0xC8, 0xCC):
                        d = f.read(5)
                        if len(d) == 5:
                            wynik = (struct.unpack(">H", d[3:5])[0], struct.unpack(">H", d[1:3])[0])
                        break
                    f.seek(struct.unpack(">H", dl)[0] - 2, 1)
    except (OSError, struct.error, ValueError):
        return None
    if wynik and 0 < wynik[0] <= 100000 and 0 < wynik[1] <= 100000:
        return int(wynik[0]), int(wynik[1])
    return None


def _info_obrazu(pelna):
    """Rozmiar, czas zmiany i wymiary pliku obrazu albo None, gdy pliku nie ma. Wymiary pamiętamy do zmiany pliku."""
    try:
        st = os.stat(pelna)
    except OSError:
        return None
    if not stat.S_ISREG(st.st_mode):
        return None
    klucz = (st.st_mtime_ns, st.st_size)
    with _blokada:
        w = _obrazy.get(pelna)
        if w and w["klucz"] == klucz:
            return w
    w = {"klucz": klucz, "rozmiar": st.st_size, "wersja": st.st_mtime_ns // 1000000,
         "wymiary": wymiary_obrazu(pelna), "sha256": None}
    with _blokada:
        if len(_obrazy) > 4 * LIMIT_ASSETOW:
            _obrazy.clear()
        _obrazy[pelna] = w
    return w


def _sha256(pelna, info):
    """Suma sha256 pliku (liczona tylko wtedy, gdy manifest ma zapisaną zgodę do porównania; pamiętana z plikiem)."""
    if info.get("sha256") is None:
        h = hashlib.sha256()
        try:
            with open(pelna, "rb") as f:
                for kawalek in iter(lambda: f.read(1 << 20), b""):
                    h.update(kawalek)
        except OSError:
            return None
        info["sha256"] = h.hexdigest()
    return info["sha256"]


def format_miniatur():
    """Format miniatur: "webp" albo "png", gdy na komputerze jest biblioteka Pillow (opcjonalna); None bez niej.
    Sprawdzane raz, przy pierwszym użyciu — import Pillow nie obciąża startu panelu."""
    if not _pil["sprawdzono"]:
        fmt = None
        try:
            from PIL import features
            fmt = "webp" if features.check("webp") else "png"
        except Exception:
            fmt = None
        _pil.update(format=fmt, sprawdzono=True)
    return _pil["format"]


def _warto_miniature(info, fmt):
    """Czy miniatura da coś ponad pełny plik: WEBP zawsze (kilka razy lżejszy), PNG tylko dla dużych obrazów."""
    if not fmt:
        return False
    return fmt == "webp" or bool(info.get("wymiary") and max(info["wymiary"]) > BOK_MINIATURY)


def miniatura(pelna):
    """(bajty, typ MIME) pomniejszonego obrazu albo None, gdy lepiej oddać oryginał (brak Pillow, plik nieczytelny,
    miniatura nie wyszła lżejsza). Wynik żyje tylko w pamięci serwera — moduł niczego nie zapisuje na dysku."""
    fmt = format_miniatur()
    if not fmt:
        return None
    try:
        st = os.stat(pelna)
    except OSError:
        return None
    klucz = (pelna, st.st_mtime_ns, st.st_size)
    with _blokada:
        if klucz in _miniatury:
            return _miniatury[klucz]
    wynik = None
    if st.st_size <= LIMIT_PLIKU_MINIATURY:
        try:
            from PIL import Image
            with Image.open(pelna) as obraz:
                # wymiary z nagłówka, zanim cokolwiek zostanie rozpakowane: mały plik potrafi rozwinąć się do gigabajtów
                if obraz.size[0] * obraz.size[1] > LIMIT_PIKSELI_MINIATURY:
                    raise ValueError("obraz %d × %d px jest za duży na miniaturę" % obraz.size)
                obraz.load()
                if fmt == "webp" or max(obraz.size) > BOK_MINIATURY:
                    przezroczysty = obraz.mode in ("RGBA", "LA", "PA") or "transparency" in obraz.info
                    obraz = obraz.convert("RGBA" if przezroczysty else "RGB")
                    obraz.thumbnail((BOK_MINIATURY, BOK_MINIATURY), getattr(Image, "Resampling", Image).LANCZOS)
                    bufor = io.BytesIO()
                    if fmt == "webp":
                        obraz.save(bufor, "WEBP", quality=88, method=4)
                    else:
                        obraz.save(bufor, "PNG", optimize=True)
                    if bufor.tell() < st.st_size:
                        wynik = (bufor.getvalue(), "image/webp" if fmt == "webp" else "image/png")
        except Exception as e:                                 # uszkodzony albo nietypowy obraz — oddamy oryginał
            powod = str(e).replace(pelna, os.path.basename(pelna))[:200] or e.__class__.__name__
            rdzen.log("assety: nie udało się zrobić miniatury %s (%s)" % (os.path.basename(pelna), powod))
    with _blokada:
        if len(_miniatury) >= LIMIT_PAMIECI_MINIATUR:
            _miniatury.clear()
        _miniatury[klucz] = wynik
    return wynik


# --------------------------------------------------------------------------- opis jednego assetu
def adres_figmy(plik, wezel, nazwa=""):
    """Adres węzła w Figmie (https://www.figma.com/design/<plik>/<nazwa>?node-id=10-1563) albo None, gdy klucz pliku
    lub identyfikator węzła nie wyglądają poprawnie — z niepewnych danych nie budujemy linku."""
    if not isinstance(plik, str) or not RX_FIGMA_PLIK.match(plik):
        return None
    if not isinstance(wezel, str) or not RX_FIGMA_WEZEL.match(wezel) or not any(c.isdigit() for c in wezel):
        return None
    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(nazwa or "")).strip("-")[:60] or "asset"
    return "https://www.figma.com/design/%s/%s?node-id=%s" % (
        plik, slug, urllib.parse.quote(wezel.replace(":", "-"), safe="-"))


def _nazwa_do_adresu(nazwa):
    """Czy nazwę assetu da się bezpiecznie włożyć do adresu obrazu (bez ukośników, „..”, %, znaków sterujących)."""
    return isinstance(nazwa, str) and bool(RX_NAZWA_W_ADRESIE.match(nazwa)) and nazwa not in (".", "..")


def _adres_obrazu(rodzaj, nazwa, rozszerzenie, wersja):
    return "/api/assety/%s/%s%s?v=%d" % (rodzaj, urllib.parse.quote(nazwa, safe="-_.!~*'()"), rozszerzenie, wersja)


def _historia(lista):
    """Pole `history` → [{opis, pole?, wartosc?, kiedy?}]. tools/manifest.py dopisuje tam poprzednie numery Roblox
    ({pole: stara wartość, replaced_at}); inne kształty przepuszczamy ostrożnie, bez wywracania się."""
    wynik = []
    if not isinstance(lista, list):
        return wynik
    for w in lista[-50:]:
        if isinstance(w, dict):
            kiedy = next((_czas(w.get(k)) for k in POLA_CZASU_HISTORII if _czas(w.get(k))), None)
            for k, v in w.items():
                if k in POLA_CZASU_HISTORII or not isinstance(k, str) or RX_SEKRET.search(k):
                    continue
                wartosc = _tekst(v, 300)
                if not wartosc:
                    continue
                wpis = {"opis": OPISY_HISTORII.get(k) or "Poprzednia wartość pola „%s”" % _tekst(k, 60),
                        "pole": _tekst(k, 60), "wartosc": wartosc}
                if kiedy:
                    wpis["kiedy"] = kiedy
                wynik.append(wpis)
        else:
            opis = _tekst(w, 300)
            if opis:
                wynik.append({"opis": opis})
    return wynik


def _asset(nazwa, wpis, figma, baza, fmt):
    """Wpis manifestu → słownik dla interfejsu. Brakujące pola dają puste wartości, nieznane trafiają do `inne`."""
    status = _tekst(wpis.get("status"), 40).lower().replace("-", "_").replace(" ", "_") or "brak"
    znany = STATUSY.get(status)
    kategoria = _tekst(wpis.get("category"), 40).lower()
    a = {"nazwa": nazwa, "kategoria": kategoria,
         "kategoria_opis": KATEGORIE.get(kategoria) or kategoria or "bez kategorii",
         "status": status,
         "status_opis": znany[0] if znany else ("bez statusu" if status == "brak" else status),
         "status_wyjasnienie": znany[2] if znany else (
             "Wpis nie ma statusu." if status == "brak" else "Status spoza pipeline'u — panel go nie zna."),
         "etap": znany[1] if znany else None,
         "uzycie": _tekst(wpis.get("usage")), "notatki": _tekst(wpis.get("notes")),
         "obraz": None, "miniatura": None}
    if not znany:
        a["status_nieznany"] = True
    uwagi = []

    # --- obraz: tylko z assets/processed/, tylko gdy plik istnieje
    pelna, wzgledna, odmowa = sciezka_obrazu(wpis.get("processed"), baza)
    info = _info_obrazu(pelna) if pelna else None
    if odmowa:
        uwagi.append(odmowa)
    elif pelna:
        a["plik"] = wzgledna
        if info is None:
            uwagi.append("Manifest wskazuje plik %s, ale nie ma go na dysku." % wzgledna)
        elif not _nazwa_do_adresu(nazwa):
            uwagi.append("Nazwa assetu zawiera znaki, których panel nie obsługuje w adresie obrazu.")
        else:
            rozszerzenie = os.path.splitext(pelna)[1].lower()
            a["obraz"] = _adres_obrazu("plik", nazwa, rozszerzenie, info["wersja"])
            a["miniatura"] = (_adres_obrazu("miniatura", nazwa, "." + fmt, info["wersja"])
                              if _warto_miniature(info, fmt) else a["obraz"])
            a["rozmiar"] = info["rozmiar"]
            if info["wymiary"]:
                a["wymiary"] = list(info["wymiary"])

    # --- Roblox, Figma, czasy
    for pole, klucz in (("roblox_id", "roblox_image"), ("roblox_decal", "roblox_decal"),
                        ("roblox_cel", "roblox_target"), ("moderacja", "moderation"),
                        ("figma_wezel", "figma_node"), ("prompt", "prompt"), ("surowe", "raw")):
        v = _tekst(wpis.get(klucz))
        if v:
            a[pole] = v
    adres = adres_figmy(figma, a.get("figma_wezel"), nazwa)
    if adres:
        a["figma_adres"] = adres
    for pole, klucz in (("utworzono", "created_at"), ("zmieniono", "updated_at")):
        v = _czas(wpis.get(klucz))
        if v:
            a[pole] = v
    a["historia"] = _historia(wpis.get("history"))

    # --- bramka: zgoda człowieka przed Roblox (panel jej nie daje — tylko pokazuje stan z manifestu)
    zatwierdzony = wpis.get("approved_by_user") is True
    zgoda = None
    if "approved_by_user" in wpis or status in ("awaiting_approval", "approved"):
        zgoda = {"jest": zatwierdzony}
        kiedy = _czas(wpis.get("approved_at"))
        if kiedy:
            zgoda["kiedy"] = kiedy
        suma = wpis.get("approved_sha256")
        if zatwierdzony and isinstance(suma, str) and suma.strip() and pelna and info:
            biezaca = _sha256(pelna, info)
            if biezaca:
                zgoda["aktualna"] = biezaca == suma.strip().lower()
        a["zgoda"] = zgoda
    nieaktualna = bool(zgoda) and zgoda.get("aktualna") is False
    if nieaktualna:
        uwagi.append("Plik zmienił się po akceptacji — zgoda wygasła. Agent musi pokazać obraz ponownie "
                     "i dostać nowe „tak”.")
    elif status == "approved" and not zatwierdzony:
        uwagi.append("Status „zatwierdzony”, ale w manifeście nie ma ważnej zgody — przed uploadem trzeba ją "
                     "potwierdzić ponownie.")
    a["czeka_na_zgode"] = status == "awaiting_approval" or (status == "approved" and (not zatwierdzony or nieaktualna))

    if status in ("in_roblox", "done") and not a.get("roblox_id"):
        uwagi.append("Status mówi „%s”, ale w manifeście nie ma numeru obrazu Roblox." % a["status_opis"])
    if "reject" in a.get("moderacja", "").lower():
        uwagi.append("Moderacja Roblox odrzuciła ten obraz.")

    # --- pola, których panel nie zna: tylko proste wartości, bez niczego, co wygląda na sekret
    inne = {}
    for k, v in wpis.items():
        if len(inne) >= 12:
            break
        if not isinstance(k, str) or k in POLA_ZNANE or RX_SEKRET.search(k):
            continue
        wartosc = _tekst(v, 300)
        if wartosc and _tekst(k, 60):
            inne[_tekst(k, 60)] = wartosc
    if inne:
        a["inne"] = inne
    if uwagi:
        a["uwagi"] = uwagi

    # --- cel komentarzy (typ „plik”): ścieżka obrazu w repozytorium; zanim obraz powstanie — ta, pod którą trafi
    cel = a.get("plik") or ""
    if not cel or len(cel) > 300:
        cel = ("%s/%s.png" % (KATALOG_OBRAZOW, nazwa)) if RX_NAZWA_PLIKU.match(nazwa) else "%s#%s" % (ZRODLO, nazwa)
    a["cel_komentarzy"] = cel
    return a


# --------------------------------------------------------------------------- rejestr
def rejestr():
    """Odpowiedź GET /api/assety. Nie rzuca: brak manifestu opisuje pole `brak_manifestu`, uszkodzony — pole `blad`."""
    dane, blad = manifest()
    wynik = {"zrodlo": ZRODLO}
    assety = []
    if dane is None:
        if blad:
            wynik["blad"] = blad
        else:
            wynik["brak_manifestu"] = True
    else:
        figma = dane.get("figma_file")
        figma = figma if isinstance(figma, str) and RX_FIGMA_PLIK.match(figma) else None
        if figma:
            wynik["figma_plik"] = figma
        zaktualizowano = _czas(dane.get("updated_at"))
        if not zaktualizowano:
            try:
                zaktualizowano = datetime.datetime.fromtimestamp(
                    os.path.getmtime(plik_manifestu())).astimezone().isoformat(timespec="seconds")
            except OSError:
                zaktualizowano = None
        if zaktualizowano:
            wynik["zaktualizowano"] = zaktualizowano
        baza = _katalog_obrazow()
        fmt = format_miniatur()
        assety = [_asset(nazwa, wpis, figma, baza, fmt) for nazwa, wpis in _wpisy(dane)]

    liczniki = {}
    for a in assety:
        liczniki[a["status"]] = liczniki.get(a["status"], 0) + 1
    etapy = []
    for i, e in enumerate(ETAPY):
        e = dict(e)
        e["liczba"] = sum(1 for a in assety if a["etap"] == i)
        etapy.append(e)
    statusy = [{"id": k, "nazwa": v[0], "etap": v[1], "opis": v[2], "liczba": liczniki.get(k, 0)}
               for k, v in STATUSY.items()]
    for k, n in liczniki.items():
        if k not in STATUSY:
            statusy.append({"id": k, "nazwa": "bez statusu" if k == "brak" else k, "etap": None, "nieznany": True,
                            "opis": "Status spoza pipeline'u — panel go nie zna.", "liczba": n})
    wynik.update(assety=assety, liczniki=liczniki, etapy=etapy, statusy=statusy,
                 czeka=sum(1 for a in assety if a["czeka_na_zgode"]))
    return wynik


# --------------------------------------------------------------------------- trasy
def plik_assetu(nazwa):
    """Pełna ścieżka gotowego obrazu assetu o nazwie z adresu (sama nazwa albo z rozszerzeniem obrazu: „Teleport.png”).
    BladHTTP 404: nie ma assetu albo obrazu; 403: manifest wskazuje plik spoza assets/processed/ albo nie obraz."""
    indeks = _indeks()
    if indeks is None:
        raise BladHTTP(404, "Nie ma rejestru assetów (%s)" % ZRODLO)
    wpis = None
    if isinstance(nazwa, str):
        # Najpierw nazwa bez rozszerzenia: tak buduje adresy rejestr („Coin” -> „Coin.png”). Gdyby w manifeście był
        # też asset o nazwie „Coin.png”, dopasowanie dokładne oddałoby obraz cudzego assetu (jego adres to „Coin.png.png”).
        bez_rozszerzenia, rozszerzenie = os.path.splitext(nazwa)
        if rozszerzenie.lower() in ROZSZERZENIA_OBRAZOW and _nazwa_do_adresu(bez_rozszerzenia):
            wpis = indeks.get(bez_rozszerzenia)
        if wpis is None and _nazwa_do_adresu(nazwa):
            wpis = indeks.get(nazwa)
    if wpis is None:
        raise BladHTTP(404, "Nie ma takiego assetu")
    pelna, _, odmowa = sciezka_obrazu(wpis.get("processed"))
    if odmowa:
        raise BladHTTP(403, odmowa)
    if not pelna:
        raise BladHTTP(404, "Ten asset nie ma jeszcze gotowego obrazu")
    if not os.path.isfile(pelna):
        raise BladHTTP(404, "Nie ma pliku obrazu tego assetu")
    return pelna


def _get_rejestr(z):
    return rejestr()


def _get_plik(z):
    return Odp.plik(plik_assetu(z.params.get("nazwa")), pamiec_s=86400)   # adres w rejestrze ma wersję pliku (?v=)


def _get_miniatura(z):
    pelna = plik_assetu(z.params.get("nazwa"))
    gotowa = miniatura(pelna)
    if gotowa is None:
        return Odp.plik(pelna, pamiec_s=86400)
    return Odp.bajty(gotowa[0], gotowa[1])


def zarejestruj(app):
    app.dodaj("GET", "/api/assety", _get_rejestr)
    app.dodaj("GET", "/api/assety/plik/<nazwa>", _get_plik)
    app.dodaj("GET", "/api/assety/miniatura/<nazwa>", _get_miniatura)


def zdrowie():
    r = rejestr()
    wynik = {"manifest": not r.get("brak_manifestu"), "assety": len(r["assety"]),
             "bez_obrazu": sum(1 for a in r["assety"] if not a.get("obraz")), "czeka_na_zgode": r["czeka"]}
    if r.get("blad"):
        wynik["blad"] = r["blad"]
    return wynik
