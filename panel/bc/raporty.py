# -*- coding: utf-8 -*-
"""Raporty z wdrożeń, decyzje ludzi i komentarze (jeden plik na wpis — git nie ma konfliktów).

Układ plików (rdzen.DANE = panel/dane):
    raporty/<id>.json            raport (bez pola status — status wylicza się przy odczycie)
    raporty/<id>.decyzja.json    decyzja człowieka {kto, czas, wartosc, komentarz}
                                 (wartosc: zaakceptowane | do_poprawy | nieaktualne — ostatnia decyzja wygrywa)
    raporty/<id>/                załączniki (zrzuty ekranu)
    komentarze/<id>.json         komentarz {id, cel:{typ, cel, etykieta?}, kto, czas, tekst, zrodlo}

Funkcje publiczne (dla CLI `narzedzia/raport.py` i innych modułów):
    dodaj_raport(tytul, opis_md="", rodzaj="wdrozenie", komponenty=None, migawka=None, pytanie=None, kto=None,
                 zrzuty=None, gra=None)  -> raport  (zrzuty = ścieżki obrazów na dysku do skopiowania;
                                                     gra = identyfikator z rejestru gier, bc/gry.py)
    lista_raportow()          -> [raport…] (najnowszy pierwszy)
    raport(rid)               -> raport albo None
    zapisz_decyzje(rid, wartosc, kto, komentarz=None) -> raport
    dodaj_komentarz(cel, tekst, kto, zrodlo="tekst") -> komentarz      (cel = {typ, cel, etykieta?})
    komentarze(typ=None, cel=None) -> [komentarz…]  (z celem: cały wątek od najstarszego; bez: 100 najnowszych)

Błędy walidacji to rdzen.BladHTTP(400, "…") z komunikatem po polsku (CLI pokazuje sam komunikat).
"""
import datetime
import os
import re
import threading
import time

from . import gry, rdzen
from .http import Odp
from .rdzen import BladHTTP

RODZAJE = ("wdrozenie", "pytanie", "informacja")
DECYZJE = ("zaakceptowane", "do_poprawy", "nieaktualne")       # nieaktualne (14.11): zdjęty z kolejki, nie poprawiać
TYPY_KOMPONENTU = ("studio", "notatka", "plik", "migawka")
TYPY_CELU = ("raport", "studio", "notatka", "migawka", "plik")   # „plik” = ścieżka w repo (np. obraz assetu)
ZRODLA = ("tekst", "glos")

MAX_TYTUL = 140
MAX_OPIS = 8000
MAX_KOMENTARZ = 4000
MAX_KOMPONENTY = 12
MAX_PYTANIE = 2000
MAX_CEL = 300
MAX_ETYKIETA = 120
MAX_KTO = 40
MAX_ZRZUTY = 8
MAX_ZRZUT_BAJTY = 3 * 1024 * 1024                              # limit jednego załącznika po obróbce
MAX_ZRZUT_WEJSCIE = 60 * 1024 * 1024                           # większych plików nawet nie czytamy
BOK_ZRZUTU = 1600

# „gra” (25.11): jawna gra raportu z rejestru gier (bc/gry.py); raport bez pola dostaje grę przy odczycie (po tytule)
POLA_RAPORTU = ("tytul", "opis_md", "kto", "rodzaj", "komponenty", "migawka", "zrzuty", "pytanie", "gra")
POLA_WYLICZANE = ("status", "komentarzy", "gra_skad")          # przysłane przez klienta są pomijane
RX_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
RX_PLIK = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$")
ROZSZERZENIA_OBRAZOW = (".png", ".jpg", ".jpeg", ".webp", ".gif")

_zapis_lock = threading.Lock()


# --------------------------------------------------------------------------- ścieżki
def _kat_raportow():
    return os.path.join(rdzen.DANE, "raporty")


def _kat_komentarzy():
    return os.path.join(rdzen.DANE, "komentarze")


def _sciezka_raportu(rid):
    return os.path.join(_kat_raportow(), rid + ".json")


def _sciezka_decyzji(rid):
    return os.path.join(_kat_raportow(), rid + ".decyzja.json")


def _kat_zalacznikow(rid):
    return os.path.join(_kat_raportow(), rid)


def _sprawdz_id(rid, co="raportu"):
    if not isinstance(rid, str) or not RX_ID.match(rid):
        raise BladHTTP(400, "Niepoprawny identyfikator %s" % co)
    return rid


# --------------------------------------------------------------------------- pamięć podręczna katalogu
class _Katalog:
    """Pamięć podręczna plików JSON w katalogu. Pełne przejrzenie tylko, gdy zmienił się czas modyfikacji katalogu
    (dodanie / podmiana / usunięcie pliku) albo minęło 10 s; każdy plik parsowany ponownie tylko, gdy zmienił się
    jego czas lub rozmiar. Kilkaset raportów = jeden scandir i zero parsowania przy kolejnych odczytach."""

    def __init__(self, kat_fn):
        self._kat_fn = kat_fn
        self._lock = threading.Lock()
        self._kat = None
        self._mtime = None
        self._t = 0.0
        self._pliki = {}                                       # nazwa -> (mtime_ns, rozmiar, dane)
        self._wersja = 0

    def uniewaznij(self):
        with self._lock:
            self._mtime = None

    def czas_zapisu(self, nazwa):
        """mtime_ns pliku z ostatniego przejrzenia (0, gdy nieznany) — rozstrzyga kolejność wpisów z tej samej sekundy."""
        with self._lock:
            w = self._pliki.get(nazwa)
            return w[0] if w else 0

    def wpisy(self):
        """Zwraca (wersja, {nazwa: dane}) — wersja rośnie przy każdej zmianie zawartości."""
        kat = self._kat_fn()
        with self._lock:
            if kat != self._kat:                               # testy podmieniają rdzen.DANE
                self._kat, self._mtime, self._pliki = kat, None, {}
                self._wersja += 1
            try:
                mt = os.stat(kat).st_mtime_ns
            except OSError:
                if self._pliki:
                    self._pliki = {}
                    self._wersja += 1
                self._mtime = None
                return self._wersja, {}
            if mt == self._mtime and time.time() - self._t < 10:
                return self._wersja, {k: v[2] for k, v in self._pliki.items()}
            nowe = {}
            zmiana = False
            try:
                with os.scandir(kat) as it:
                    for e in it:
                        if not e.name.endswith(".json") or not e.is_file():
                            continue
                        try:
                            st = e.stat()
                        except OSError:
                            continue
                        stare = self._pliki.get(e.name)
                        if stare and stare[0] == st.st_mtime_ns and stare[1] == st.st_size:
                            nowe[e.name] = stare
                            continue
                        dane = rdzen.czytaj_json(e.path)
                        if not isinstance(dane, dict):
                            continue                           # uszkodzony albo w trakcie zapisu — pomiń
                        nowe[e.name] = (st.st_mtime_ns, st.st_size, dane)
                        zmiana = True
            except OSError:
                pass
            if zmiana or set(nowe) != set(self._pliki):
                self._wersja += 1
            self._pliki, self._mtime, self._t = nowe, mt, time.time()
            return self._wersja, {k: v[2] for k, v in nowe.items()}


_raporty_kat = _Katalog(_kat_raportow)
_komentarze_kat = _Katalog(_kat_komentarzy)
_lista_cache = {"klucz": None, "lista": None}
_lista_lock = threading.Lock()


# --------------------------------------------------------------------------- pomocnicze
def _czas_klucz(iso):
    """Znacznik czasu do sortowania (różne strefy czasowe porównywane poprawnie)."""
    try:
        return datetime.datetime.fromisoformat(str(iso)).timestamp()
    except (TypeError, ValueError):
        return 0.0


def _tekst(dane, pole, maks, wymagane=False, nazwa=None):
    nazwa = nazwa or pole
    v = dane.get(pole)
    if v is None:
        if wymagane:
            raise BladHTTP(400, "Brak pola „%s”" % nazwa)
        return None
    if not isinstance(v, str):
        raise BladHTTP(400, "Pole „%s” musi być tekstem" % nazwa)
    v = v.replace("\r\n", "\n").strip()
    if wymagane and not v:
        raise BladHTTP(400, "Pole „%s” nie może być puste" % nazwa)
    if len(v) > maks:
        raise BladHTTP(400, "Pole „%s” jest za długie (%d znaków, najwyżej %d)" % (nazwa, len(v), maks))
    return v


def _kto(kto):
    kto = re.sub(r"[\x00-\x1f\x7f]", "", str(kto or "")).strip()[:MAX_KTO]
    return kto or rdzen.git_uzytkownik()


def _domyslna_etykieta(cel):
    return str(cel).rstrip("/").replace("\\", "/").split("/")[-1][:MAX_ETYKIETA] or str(cel)[:MAX_ETYKIETA]


def _sprawdz_komponenty(lista):
    if lista is None:
        return []
    if not isinstance(lista, list):
        raise BladHTTP(400, "Pole „komponenty” musi być listą")
    if len(lista) > MAX_KOMPONENTY:
        raise BladHTTP(400, "Za dużo komponentów (%d, najwyżej %d)" % (len(lista), MAX_KOMPONENTY))
    out = []
    for i, k in enumerate(lista, 1):
        if not isinstance(k, dict):
            raise BladHTTP(400, "Komponent nr %d musi być obiektem {typ, cel, etykieta}" % i)
        nieznane = set(k) - {"typ", "cel", "etykieta"}
        if nieznane:
            raise BladHTTP(400, "Komponent nr %d ma nieznane pola: %s" % (i, ", ".join(sorted(nieznane))))
        typ = k.get("typ")
        if typ not in TYPY_KOMPONENTU:
            raise BladHTTP(400, "Komponent nr %d: typ musi być jednym z: %s" % (i, ", ".join(TYPY_KOMPONENTU)))
        cel = _tekst(k, "cel", MAX_CEL, wymagane=True, nazwa="cel komponentu nr %d" % i)
        etykieta = _tekst(k, "etykieta", MAX_ETYKIETA, nazwa="etykieta komponentu nr %d" % i) or _domyslna_etykieta(cel)
        out.append({"typ": typ, "cel": cel, "etykieta": etykieta})
    return out


def _sprawdz_cel(cel):
    if not isinstance(cel, dict):
        raise BladHTTP(400, "Pole „cel” musi być obiektem {typ, cel, etykieta?}")
    nieznane = set(cel) - {"typ", "cel", "etykieta"}
    if nieznane:
        raise BladHTTP(400, "Cel komentarza ma nieznane pola: %s" % ", ".join(sorted(nieznane)))
    typ = cel.get("typ")
    if typ not in TYPY_CELU:
        raise BladHTTP(400, "Typ celu komentarza musi być jednym z: %s" % ", ".join(TYPY_CELU))
    wartosc = _tekst(cel, "cel", MAX_CEL, wymagane=True, nazwa="cel")
    if typ in ("raport", "migawka") and not RX_ID.match(wartosc):
        raise BladHTTP(400, "Niepoprawny identyfikator w polu „cel”")
    out = {"typ": typ, "cel": wartosc}
    etykieta = _tekst(cel, "etykieta", MAX_ETYKIETA, nazwa="etykieta")
    if etykieta:
        out["etykieta"] = etykieta
    return out


# --------------------------------------------------------------------------- załączniki (zrzuty)
def _rozpoznaj_obraz(poczatek):
    if poczatek.startswith(b"\x89PNG\r\n\x1a\n"):
        return ".png"
    if poczatek.startswith(b"\xff\xd8\xff"):
        return ".jpg"
    if poczatek[:4] == b"RIFF" and poczatek[8:12] == b"WEBP":
        return ".webp"
    if poczatek[:6] in (b"GIF87a", b"GIF89a"):
        return ".gif"
    return None


def _przygotuj_zrzut(sciezka):
    """Czyta obraz z dysku i zwraca (rozszerzenie, bajty) gotowe do zapisania jako załącznik.
    Z biblioteką Pillow: zmniejsza do 1600 px i zapisuje jako JPG; bez niej kopiuje plik bez zmian."""
    if not os.path.isfile(sciezka):
        raise BladHTTP(400, "Nie ma pliku zrzutu: %s" % sciezka)
    rozmiar = os.path.getsize(sciezka)
    if rozmiar > MAX_ZRZUT_WEJSCIE:
        raise BladHTTP(400, "Zrzut %s jest za duży (%.1f MB)" % (os.path.basename(sciezka), rozmiar / 1048576))
    with open(sciezka, "rb") as f:
        dane = f.read()
    ext = _rozpoznaj_obraz(dane[:16])
    if not ext:
        raise BladHTTP(400, "Plik %s nie jest obrazem PNG, JPG, WEBP ani GIF" % os.path.basename(sciezka))
    try:
        import io
        from PIL import Image                                  # opcjonalnie — panel działa i bez Pillow
        with Image.open(io.BytesIO(dane)) as obraz:
            obraz.load()
            if obraz.mode in ("RGBA", "LA", "P"):
                obraz = obraz.convert("RGBA")
                tlo = Image.new("RGB", obraz.size, (18, 20, 28))
                tlo.paste(obraz, mask=obraz.split()[-1])
                obraz = tlo
            elif obraz.mode != "RGB":
                obraz = obraz.convert("RGB")
            obraz.thumbnail((BOK_ZRZUTU, BOK_ZRZUTU))
            wyj = io.BytesIO()
            obraz.save(wyj, "JPEG", quality=85, optimize=True)
            jpg = wyj.getvalue()
        if len(jpg) <= MAX_ZRZUT_BAJTY:
            return ".jpg", jpg
    except ImportError:
        pass
    except Exception as e:                                     # uszkodzony obraz itp. — spróbuj skopiować bez zmian
        rdzen.log("raporty: Pillow nie przetworzył %s: %s" % (sciezka, e))
    if len(dane) > MAX_ZRZUT_BAJTY:
        raise BladHTTP(400, "Zrzut %s ma %.1f MB — limit to 3 MB (zainstaluj Pillow, żeby panel sam go zmniejszał)"
                       % (os.path.basename(sciezka), len(dane) / 1048576))
    return (".jpg" if ext == ".jpg" else ext), dane


# --------------------------------------------------------------------------- raporty
def _uzupelnij(r, decyzja, liczniki):
    """Dokłada pola wyliczane: decyzja, status, komentarzy."""
    out = dict(r)
    out.pop("status", None)
    if decyzja:
        out["decyzja"] = decyzja
        out["status"] = decyzja.get("wartosc") if decyzja.get("wartosc") in DECYZJE else "czeka"
    else:
        out.pop("decyzja", None)
        out["status"] = "informacja" if r.get("rodzaj") == "informacja" else "czeka"
    out.setdefault("komponenty", [])
    out.setdefault("zrzuty", [])
    out["komentarzy"] = liczniki.get(r.get("id"), 0)
    return gry.oznacz_raport(out)                              # `gra`, `gra_skad` (bez rejestru gier — bez zmian)


def _liczniki_komentarzy():
    wersja, wpisy = _komentarze_kat.wpisy()
    licz = {}
    for k in wpisy.values():
        cel = k.get("cel")
        if isinstance(cel, dict) and cel.get("typ") == "raport" and isinstance(cel.get("cel"), str):
            licz[cel["cel"]] = licz.get(cel["cel"], 0) + 1
    return wersja, licz


def lista_raportow():
    """Wszystkie raporty, najnowszy pierwszy (ze statusem, decyzją i liczbą komentarzy)."""
    wr, wpisy = _raporty_kat.wpisy()
    wk, liczniki = _liczniki_komentarzy()
    klucz = (rdzen.DANE, wr, wk, gry.podpis())                 # zmiana rejestru gier = nowa klasyfikacja raportów
    with _lista_lock:
        if _lista_cache["klucz"] == klucz:
            return list(_lista_cache["lista"])
    decyzje = {}
    raporty = []
    for nazwa, dane in wpisy.items():
        if nazwa.endswith(".decyzja.json"):
            decyzje[nazwa[:-len(".decyzja.json")]] = dane
        elif ".tmp" not in nazwa and dane.get("id") == nazwa[:-5]:
            raporty.append(dane)
    wynik = [_uzupelnij(r, decyzje.get(r["id"]), liczniki) for r in raporty]
    wynik.sort(key=lambda r: (_czas_klucz(r.get("czas")), _raporty_kat.czas_zapisu(str(r.get("id")) + ".json"),
                              r.get("id") or ""), reverse=True)
    with _lista_lock:
        _lista_cache.update(klucz=klucz, lista=wynik)
    return list(wynik)


def raport(rid):
    """Jeden raport (z polami wyliczanymi) albo None."""
    if not isinstance(rid, str) or not RX_ID.match(rid):
        return None
    r = rdzen.czytaj_json(_sciezka_raportu(rid))
    if not isinstance(r, dict):
        return None
    _, liczniki = _liczniki_komentarzy()
    return _uzupelnij(r, rdzen.czytaj_json(_sciezka_decyzji(rid)), liczniki)


def sprawdz_raport(dane):
    """Walidacja pól raportu (jak w POST /api/raporty). Zwraca słownik oczyszczonych pól."""
    if not isinstance(dane, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON z polami raportu")
    nieznane = set(dane) - set(POLA_RAPORTU) - set(POLA_WYLICZANE)
    if nieznane:
        raise BladHTTP(400, "Nieznane pola raportu: %s" % ", ".join(sorted(nieznane)))
    out = {"tytul": _tekst(dane, "tytul", MAX_TYTUL, wymagane=True, nazwa="tytuł"),
           "opis_md": _tekst(dane, "opis_md", MAX_OPIS, nazwa="opis") or ""}
    rodzaj = dane.get("rodzaj") or "wdrozenie"
    if rodzaj not in RODZAJE:
        raise BladHTTP(400, "Rodzaj raportu musi być jednym z: %s" % ", ".join(RODZAJE))
    out["rodzaj"] = rodzaj
    out["komponenty"] = _sprawdz_komponenty(dane.get("komponenty"))
    migawka = _tekst(dane, "migawka", 80, nazwa="migawka")
    if migawka:
        if not RX_ID.match(migawka):
            raise BladHTTP(400, "Niepoprawny identyfikator migawki")
        out["migawka"] = migawka
    pytanie = _tekst(dane, "pytanie", MAX_PYTANIE, nazwa="pytanie")
    if pytanie:
        out["pytanie"] = pytanie
    kto = _tekst(dane, "kto", 200, nazwa="kto")
    if kto:
        out["kto"] = kto
    gra = gry.sprawdz_gre(dane.get("gra"))                    # tylko gra z rejestru (bc/gry.py)
    if gra:
        out["gra"] = gra
    zrzuty = dane.get("zrzuty")
    if zrzuty not in (None, []):
        raise BladHTTP(400, "Zrzuty dołącza się poleceniem: python panel/narzedzia/raport.py dodaj --zrzut plik.png")
    return out


def dodaj_raport(tytul, opis_md="", rodzaj="wdrozenie", komponenty=None, migawka=None, pytanie=None, kto=None,
                 zrzuty=None, gra=None):
    """Tworzy raport. `zrzuty` = lista ścieżek obrazów na dysku (kopiowane do załączników), `gra` = identyfikator
    z rejestru gier (bc/gry.py; bez niego gra wynika z tytułu przy odczycie). Zwraca raport."""
    dane = {"tytul": tytul, "opis_md": opis_md or "", "rodzaj": rodzaj or "wdrozenie", "komponenty": komponenty or []}
    if migawka:
        dane["migawka"] = migawka
    if pytanie:
        dane["pytanie"] = pytanie
    if gra:
        dane["gra"] = gra
    czyste = sprawdz_raport(dane)
    if czyste.get("migawka"):                                  # raport może wskazywać tylko istniejącą migawkę
        from . import podglad
        if not podglad.folder_migawki(czyste["migawka"]):
            raise BladHTTP(400, "Nie ma migawki %s w panel/dane/podglad. Najpierw ją zrób: "
                                "python panel/narzedzia/migawka.py --tytul \"…\"" % czyste["migawka"])
    sciezki = list(zrzuty or [])
    if len(sciezki) > MAX_ZRZUTY:
        raise BladHTTP(400, "Za dużo zrzutów (%d, najwyżej %d)" % (len(sciezki), MAX_ZRZUTY))
    gotowe = [_przygotuj_zrzut(s) for s in sciezki]            # najpierw wszystko sprawdź, potem zapisuj
    with _zapis_lock:
        for _ in range(50):
            rid = rdzen.nowe_id("r")
            if not os.path.exists(_sciezka_raportu(rid)) and not os.path.exists(_kat_zalacznikow(rid)):
                break
            time.sleep(0.01)
        nazwy = []
        for i, (ext, bajty) in enumerate(gotowe, 1):
            nazwa = "zrzut_%d%s" % (i, ext)
            rdzen.zapisz_bajty(os.path.join(_kat_zalacznikow(rid), nazwa), bajty)
            nazwy.append(nazwa)
        r = {"id": rid, "tytul": czyste["tytul"], "opis_md": czyste["opis_md"], "kto": _kto(kto), "czas": rdzen.teraz(),
             "rodzaj": czyste["rodzaj"], "komponenty": czyste["komponenty"], "zrzuty": nazwy}
        for pole in ("migawka", "pytanie", "gra"):
            if czyste.get(pole):
                r[pole] = czyste[pole]
        rdzen.zapisz_json(_sciezka_raportu(rid), r)
    _raporty_kat.uniewaznij()
    rdzen.log("raporty: nowy raport %s (%s) od %s" % (rid, r["tytul"][:60], r["kto"]))
    return raport(rid)


def zapisz_decyzje(rid, wartosc, kto, komentarz=None):
    _sprawdz_id(rid)
    if not os.path.isfile(_sciezka_raportu(rid)):
        raise BladHTTP(404, "Nie ma takiego raportu")
    if wartosc not in DECYZJE:
        raise BladHTTP(400, "Decyzja musi być jedną z: %s" % ", ".join(DECYZJE))
    komentarz = _tekst({"k": komentarz}, "k", MAX_KOMENTARZ, nazwa="komentarz") or ""
    d = {"kto": _kto(kto), "czas": rdzen.teraz(), "wartosc": wartosc, "komentarz": komentarz}
    rdzen.zapisz_json(_sciezka_decyzji(rid), d)
    _raporty_kat.uniewaznij()
    rdzen.log("raporty: decyzja %s dla %s (%s)" % (wartosc, rid, d["kto"]))
    return raport(rid)


# --------------------------------------------------------------------------- komentarze
def dodaj_komentarz(cel, tekst, kto, zrodlo="tekst"):
    """cel = {typ, cel, etykieta?}; zwraca zapisany komentarz."""
    cel = _sprawdz_cel(cel)
    tekst = _tekst({"t": tekst}, "t", MAX_KOMENTARZ, wymagane=True, nazwa="tekst")
    zrodlo = zrodlo or "tekst"
    if zrodlo not in ZRODLA:
        raise BladHTTP(400, "Źródło komentarza musi być jednym z: %s" % ", ".join(ZRODLA))
    if cel["typ"] == "raport" and not os.path.isfile(_sciezka_raportu(cel["cel"])):
        raise BladHTTP(404, "Nie ma raportu, do którego ma trafić komentarz")
    with _zapis_lock:
        for _ in range(50):
            kid = rdzen.nowe_id("k")
            sciezka = os.path.join(_kat_komentarzy(), kid + ".json")
            if not os.path.exists(sciezka):
                break
            time.sleep(0.01)
        k = {"id": kid, "cel": cel, "kto": _kto(kto), "czas": rdzen.teraz(), "tekst": tekst, "zrodlo": zrodlo}
        rdzen.zapisz_json(sciezka, k)
    _komentarze_kat.uniewaznij()
    return k


def _wszystkie_komentarze():
    _, wpisy = _komentarze_kat.wpisy()
    out = [k for n, k in wpisy.items() if ".tmp" not in n and isinstance(k.get("cel"), dict) and isinstance(k["cel"].get("cel"), str)
           and k.get("id") == n[:-5]]
    out.sort(key=lambda k: (_czas_klucz(k.get("czas")), _komentarze_kat.czas_zapisu(str(k.get("id")) + ".json"),
                            k.get("id") or ""))
    return out


def komentarze(typ=None, cel=None, limit=100):
    """Z `cel` (i `typ`): cały wątek od najstarszego. Bez `cel`: `limit` najnowszych (najnowszy pierwszy),
    opcjonalnie tylko danego typu."""
    wszystkie = _wszystkie_komentarze()
    if cel:
        return [k for k in wszystkie if k["cel"].get("cel") == cel and (not typ or k["cel"].get("typ") == typ)]
    if typ:
        wszystkie = [k for k in wszystkie if k["cel"].get("typ") == typ]
    return list(reversed(wszystkie[-limit:])) if limit else list(reversed(wszystkie))


# --------------------------------------------------------------------------- trasy HTTP
def _get_lista(z):
    lista = lista_raportow()
    return {"raporty": lista, "czeka": sum(1 for r in lista if r.get("status") == "czeka")}


def _get_raport(z):
    rid = _sprawdz_id(z.params["id"])
    r = raport(rid)
    if not r:
        raise BladHTTP(404, "Nie ma takiego raportu")
    r["komentarze"] = komentarze("raport", rid)
    return r


def _post_raport(z):
    dane = z.json
    czyste = sprawdz_raport(dane)
    r = dodaj_raport(czyste["tytul"], czyste["opis_md"], czyste["rodzaj"], czyste["komponenty"], czyste.get("migawka"),
                     czyste.get("pytanie"), kto=czyste.get("kto") or z.kto, gra=czyste.get("gra"))
    return 201, r


def _post_decyzja(z):
    rid = _sprawdz_id(z.params["id"])
    dane = z.json
    if not isinstance(dane, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON {wartosc, komentarz?}")
    nieznane = set(dane) - {"wartosc", "komentarz"}
    if nieznane:
        raise BladHTTP(400, "Nieznane pola decyzji: %s" % ", ".join(sorted(nieznane)))
    if "wartosc" not in dane:
        raise BladHTTP(400, "Brak pola „wartosc” (zaakceptowane, do_poprawy albo nieaktualne)")
    return zapisz_decyzje(rid, dane.get("wartosc"), z.kto, dane.get("komentarz"))


def _get_plik(z):
    rid = _sprawdz_id(z.params["id"])
    nazwa = z.params["nazwa"]
    if not RX_PLIK.match(nazwa) or os.path.splitext(nazwa)[1].lower() not in ROZSZERZENIA_OBRAZOW:
        raise BladHTTP(404, "Nie ma takiego pliku")
    sciezka = rdzen.w_katalogu(_kat_zalacznikow(rid), nazwa)
    return Odp.plik(sciezka, pamiec_s=86400)


def _get_komentarze(z):
    typ = (z.q("typ") or "").strip() or None
    cel = (z.q("cel") or "").strip() or None
    if typ and typ not in TYPY_CELU:
        raise BladHTTP(400, "Nieznany typ celu: %s" % typ)
    return {"komentarze": komentarze(typ, cel)}


def _post_komentarz(z):
    dane = z.json
    if not isinstance(dane, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON {cel, tekst, zrodlo?}")
    nieznane = set(dane) - {"cel", "tekst", "zrodlo"}
    if nieznane:
        raise BladHTTP(400, "Nieznane pola komentarza: %s" % ", ".join(sorted(nieznane)))
    if "cel" not in dane:
        raise BladHTTP(400, "Brak pola „cel”")
    return 201, dodaj_komentarz(dane.get("cel"), dane.get("tekst"), z.kto, dane.get("zrodlo") or "tekst")


def zarejestruj(app):
    app.dodaj("GET", "/api/raporty", _get_lista)
    app.dodaj("POST", "/api/raporty", _post_raport)
    app.dodaj("GET", "/api/raporty/<id>", _get_raport)
    app.dodaj("POST", "/api/raporty/<id>/decyzja", _post_decyzja)
    app.dodaj("GET", "/api/raporty/<id>/plik/<nazwa>", _get_plik)
    app.dodaj("GET", "/api/komentarze", _get_komentarze)
    app.dodaj("POST", "/api/komentarze", _post_komentarz)


def zdrowie():
    lista = lista_raportow()
    return {"raporty": len(lista), "czeka": sum(1 for r in lista if r.get("status") == "czeka"),
            "komentarze": len(_wszystkie_komentarze()), "katalog": rdzen.wzgledem_repo(_kat_raportow())}
