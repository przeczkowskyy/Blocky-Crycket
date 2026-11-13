# -*- coding: utf-8 -*-
"""Migawki świata gry (części + zrzuty ekranu) dla podglądu 3D.

Migawka = folder `panel/dane/podglad/<id>/` (jeden folder na wpis — git bez konfliktów):
    meta.json     opis migawki (format w README, sekcja „Studio i podgląd”)
    czesci.json   lista części w zwartym formacie (bez wcięć — potrafi mieć tysiące wierszy)
    zrzut_N.jpg   zrzuty widoku Studio (albo .png, gdy nie ma Pillow i Studio oddało PNG)
    scena.glb     opcjonalnie: model z zewnątrz (migawka ze źródła „blender”) — serwujemy, co leży w folderze

Części eksportuje `panel/luau/migawka.luau` (tylko czyta DataModel), stronami, bo Studio ucina wynik execute_luau
na ~100 000 znaków. Python skleja strony i przelicza indeksy grup i materiałów na wspólne listy.
"""
import json
import math
import os
import re
import shutil
import threading

from . import rdzen
from .http import Odp
from .rdzen import BladHTTP

PLIK_SZABLONU = os.path.join(rdzen.PANEL, "luau", "migawka.luau")
NA_STRONE = 800
LIMIT_ZNAKOW_STRONY = 90000            # Studio ucina wynik na ~100 000 znaków — zostawiamy zapas na nagłówek
MAKS_STRON = 1000
SZEROKOSC_ZRZUTU = 1600
RX_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,100}$")
RX_NAZWA = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,150}$")
ROZSZERZENIA_PLIKOW = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".glb"}

_blokada_migawki = threading.Lock()


# --------------------------------------------------------------------------- ścieżki i bezpieczne nazwy
def katalog_podgladu(katalog=None):
    """Folder z migawkami: `katalog` (testy, CLI) albo rdzen.DANE/podglad."""
    return katalog or os.path.join(rdzen.DANE, "podglad")


def bezpieczne_id(mid):
    return isinstance(mid, str) and bool(RX_ID.match(mid)) and ".." not in mid


def bezpieczna_nazwa(nazwa):
    """Nazwa pliku migawki: bez ukośników, bez „..”, tylko znane rozszerzenia (obrazy, GLB)."""
    if not isinstance(nazwa, str) or not RX_NAZWA.match(nazwa) or ".." in nazwa:
        return False
    return os.path.splitext(nazwa)[1].lower() in ROZSZERZENIA_PLIKOW


def folder_migawki(mid, katalog=None):
    """Bezwzględna ścieżka folderu migawki albo None (złe id / brak folderu)."""
    if not bezpieczne_id(mid):
        return None
    pelna = rdzen.w_katalogu(katalog_podgladu(katalog), mid)
    return pelna if pelna and os.path.isdir(pelna) else None


# --------------------------------------------------------------------------- lista
def lista_migawek(katalog=None):
    """Meta wszystkich migawek, najnowsza pierwsza. Czyta WYŁĄCZNIE meta.json (czesci.json bywa duży)."""
    baza = katalog_podgladu(katalog)
    try:
        nazwy = os.listdir(baza)
    except OSError:
        return []
    wynik = []
    for nazwa in nazwy:
        if not bezpieczne_id(nazwa):
            continue
        meta = rdzen.czytaj_json(os.path.join(baza, nazwa, "meta.json"))
        if not isinstance(meta, dict):
            continue                                       # folder w trakcie zapisu albo uszkodzony
        meta = dict(meta)
        meta["id"] = nazwa                                 # folder jest źródłem prawdy
        wynik.append(meta)
    wynik.sort(key=lambda m: (str(m.get("czas") or ""), m["id"]), reverse=True)
    return wynik


# --------------------------------------------------------------------------- Luau
def literal_luau(tekst):
    """Tekst → bezpieczny literał Luau w cudzysłowie (bajty spoza drukowalnego ASCII jako \\ddd)."""
    out = ['"']
    for b in str(tekst).encode("utf-8"):
        if b in (0x22, 0x5C):
            out.append("\\" + chr(b))
        elif 0x20 <= b < 0x7F:
            out.append(chr(b))
        else:
            out.append("\\%03d" % b)
    out.append('"')
    return "".join(out)


def kod_strony(korzen="Workspace", od=0, ile=NA_STRONE, limit=LIMIT_ZNAKOW_STRONY, szablon=None):
    """Szablon migawka.luau z podstawionymi parametrami."""
    if szablon is None:
        szablon = rdzen.czytaj_tekst(PLIK_SZABLONU)
        if not szablon:
            raise BladHTTP(500, "Brak pliku panel/luau/migawka.luau")
    # znaczniki występują też w komentarzu nagłówka — podmieniamy wszystkie wystąpienia (w komentarzu nie szkodzi)
    kod = szablon.replace('"__KORZEN__"', literal_luau(korzen))
    kod = kod.replace("__OD__", str(int(od))).replace("__ILE__", str(int(ile)))
    return kod.replace("__LIMIT__", str(int(limit)))


def sprawdz_korzen(korzen):
    """Ścieżka korzenia z żądania → znormalizowany tekst albo BladHTTP(400)."""
    korzen = str(korzen or "Workspace").strip().replace("\\", "/").strip("/")
    if not korzen:
        korzen = "Workspace"
    if len(korzen) > 300 or re.search(r"[\x00-\x1f\x7f]", korzen):
        raise BladHTTP(400, "Niepoprawna ścieżka korzenia (np. Workspace/DemoLesnaBaza)")
    return korzen


def sklej_strony(strony):
    """Strony z migawka.luau → {"wersja":1, "grupy", "materialy", "czesci"} z indeksami we wspólnych listach.
    Grupy i materiały w kolejności pierwszego wystąpienia."""
    grupy, ig, materialy, im, czesci = [], {}, [], {}, []
    for s in strony:
        mapa_g = []
        for g in s.get("grupy") or []:
            if g not in ig:
                ig[g] = len(grupy)
                grupy.append(g)
            mapa_g.append(ig[g])
        mapa_m = []
        for m in s.get("materialy") or []:
            if m not in im:
                im[m] = len(materialy)
                materialy.append(m)
            mapa_m.append(im[m])
        for w in s.get("czesci") or []:
            w = list(w)
            w[1] = mapa_g[int(w[1])]
            w[12] = mapa_m[int(w[12])]
            czesci.append(w)
    return {"wersja": 1, "grupy": grupy, "materialy": materialy, "czesci": czesci}


def pobierz_czesci(korzen="Workspace"):
    """Wszystkie strony części z otwartego Studio → (czesci_json, info z pierwszej strony, uwagi)."""
    from . import studio
    szablon = rdzen.czytaj_tekst(PLIK_SZABLONU)
    if not szablon:
        raise BladHTTP(500, "Brak pliku panel/luau/migawka.luau")
    uwagi = []
    for proba in range(2):
        strony, od, razem, zmiana = [], 0, None, False
        for _ in range(MAKS_STRON):
            tekst = studio.luau(kod_strony(korzen, od, szablon=szablon), timeout=120)
            try:
                d = json.loads(tekst)
            except ValueError:
                raise BladHTTP(502, "Studio zwróciło niepełną odpowiedź (strona części od %d). Spróbuj ponownie." % od)
            if not isinstance(d, dict):
                raise BladHTTP(502, "Nieoczekiwana odpowiedź ze Studio")
            if d.get("blad"):
                raise BladHTTP(400, d["blad"])
            if razem is None:
                razem = d.get("razem")
            elif d.get("razem") != razem:
                zmiana = True                              # ktoś w Team Create dodał/usunął części między stronami
            strony.append(d)
            nastepny = d.get("nastepny")
            if nastepny is None:
                break
            if int(nastepny) <= od:
                raise BladHTTP(502, "Eksport części utknął (strona od %d). Spróbuj ponownie." % od)
            od = int(nastepny)
        else:
            raise BladHTTP(502, "Za dużo stron części — zawęź korzeń migawki.")
        if not zmiana:
            break
        if proba == 1:
            uwagi.append("Świat zmieniał się w trakcie migawki (ktoś pracuje w Studio) — kilka części mogło się "
                         "powtórzyć albo pominąć.")
    return sklej_strony(strony), strony[0], uwagi


# --------------------------------------------------------------------------- geometria
def _macierz(rx, ry, rz):
    """Macierz obrotu CFrame.fromOrientation(rx, ry, rz) = Ry · Rx · Rz."""
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    ry_ = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rx_ = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    rz_ = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]

    def mn(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    return mn(mn(ry_, rx_), rz_)


def pudelko(w):
    """Wiersz części → (min[3], max[3]) jej obróconego prostopadłościanu w układzie świata."""
    x, y, z, rx, ry, rz, sx, sy, sz = (float(v) for v in w[2:11])
    m = _macierz(rx, ry, rz)
    h = (sx / 2, sy / 2, sz / 2)
    e = [sum(abs(m[i][j]) * h[j] for j in range(3)) for i in range(3)]
    p = (x, y, z)
    return [p[i] - e[i] for i in range(3)], [p[i] + e[i] for i in range(3)]


def zakres(czesci):
    """Zakres (AABB) wszystkich części: {"min":[x,y,z], "max":[x,y,z]}."""
    if not czesci:
        return {"min": [0, 0, 0], "max": [0, 0, 0]}
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    for w in czesci:
        a, b = pudelko(w)
        for i in range(3):
            lo[i] = min(lo[i], a[i])
            hi[i] = max(hi[i], b[i])
    return {"min": [round(v, 3) for v in lo], "max": [round(v, 3) for v in hi]}


def _percentyl(posortowane, q):
    if not posortowane:
        return 0.0
    i = min(len(posortowane) - 1, max(0, int(round(q * (len(posortowane) - 1)))))
    return posortowane[i]


def ujecia(czesci):
    """Trzy ujęcia kamery [(nazwa, pozycja, cel)] wyliczone z zakresu części: izometryczne z góry po przekątnej,
    od frontu (od strony −Z) i z poziomu gracza w pobliżu środka. Wielkie płyty (Baseplate) nie zawyżają kadru."""
    if not czesci:
        return [("izometria", [60, 50, 60], [0, 0, 0]), ("front", [0, 20, -70], [0, 5, 0]),
                ("gracz", [0, 5, -20], [0, 4, 0])]
    pudla = [pudelko(w) for w in czesci]
    duze = [i for i, w in enumerate(czesci) if max(float(w[8]), float(w[10])) >= 256]
    zbior_duzych = set(duze)
    wybrane = [p for i, p in enumerate(pudla) if i not in zbior_duzych] or pudla
    if len(wybrane) >= 50:                                 # obetnij samotne części daleko od reszty
        lo = [_percentyl(sorted(p[0][i] for p in wybrane), 0.02) for i in range(3)]
        hi = [_percentyl(sorted(p[1][i] for p in wybrane), 0.98) for i in range(3)]
    else:
        lo = [min(p[0][i] for p in wybrane) for i in range(3)]
        hi = [max(p[1][i] for p in wybrane) for i in range(3)]
    c = [(lo[i] + hi[i]) / 2 for i in range(3)]
    rozm = [max(1.0, hi[i] - lo[i]) for i in range(3)]
    r = 0.5 * math.sqrt(sum(v * v for v in rozm))
    dyst = max(r / math.tan(math.radians(35)), 25.0) * 0.85   # pole widzenia Studio: 70° w pionie, kadr szeroki

    def norm(v):
        d = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / d for x in v]
    k_iso = norm([1.0, 0.8, 1.0])
    k_front = norm([0.0, 0.35, -1.0])
    iso = [c[i] + k_iso[i] * dyst for i in range(3)]
    front = [c[i] + k_front[i] * dyst for i in range(3)]
    gracz, cel_gracza = _widok_gracza(pudla, c, rozm, lo[1])
    zaokr = lambda v: [round(x, 2) for x in v]  # noqa: E731
    return [("izometria", zaokr(iso), zaokr(c)), ("front", zaokr(front), zaokr(c)),
            ("gracz", zaokr(gracz), zaokr(cel_gracza))]


def _ziemia(pudla, x, z, domyslnie):
    """Wysokość podłoża w punkcie (x, z): wierzch najwyższej płaskiej, szerokiej części pod nim
    (płaska = co najmniej 3 razy szersza niż wysoka w obu kierunkach, np. Baseplate, płyta terenu, posadzka)."""
    wierzchy = [b[1] for a, b in pudla
                if a[0] <= x <= b[0] and a[2] <= z <= b[2] and (b[0] - a[0]) * (b[2] - a[2]) >= 64
                and min(b[0] - a[0], b[2] - a[2]) >= 3 * (b[1] - a[1])]
    return max(wierzchy) if wierzchy else domyslnie


def _wolna_droga(przeszkody, x, z, dx, dz, maks):
    """Odległość wzdłuż poziomego promienia (x,z)+t·(dx,dz) do pierwszej przeszkody (prostokąty XZ), najwyżej maks."""
    najblizej = maks
    for x0, z0, x1, z1 in przeszkody:
        t0, t1 = 0.0, najblizej
        for p, d, lo_, hi_ in ((x, dx, x0, x1), (z, dz, z0, z1)):
            if abs(d) < 1e-9:
                if p < lo_ or p > hi_:
                    t0, t1 = 1.0, 0.0
                    break
            else:
                ta, tb = (lo_ - p) / d, (hi_ - p) / d
                if ta > tb:
                    ta, tb = tb, ta
                t0, t1 = max(t0, ta), min(t1, tb)
                if t0 > t1:
                    break
        if t0 <= t1:
            najblizej = min(najblizej, t0)
    return najblizej


def _widok_gracza(pudla, c, rozm, ziemia_domyslna):
    """Kamera na wysokości oczu (ziemia + 5) w pobliżu środka, skierowana tam, gdzie widać najdalej
    (żeby nie patrzeć z bliska w ścianę)."""
    zasieg = max(30.0, 0.6 * max(rozm[0], rozm[2]))
    najlepszy = None
    for fx, fz in ((0, 0), (0.2, 0), (-0.2, 0), (0, 0.2), (0, -0.2), (0.3, 0.3), (-0.3, -0.3)):
        x, z = c[0] + fx * rozm[0], c[2] + fz * rozm[2]
        oko = _ziemia(pudla, x, z, ziemia_domyslna) + 5.0
        # przeszkody = części przecinające poziom oczu (bez płyt podłoża)
        przeszkody = [(a[0], a[2], b[0], b[2]) for a, b in pudla if a[1] < oko < b[1]]
        if any(x0 <= x <= x1 and z0 <= z <= z1 for x0, z0, x1, z1 in przeszkody):
            continue                                       # kamera w środku czegoś
        for k in range(8):
            kat = k * math.pi / 4
            dx, dz = math.sin(kat), -math.cos(kat)         # k=0: patrzymy w −Z (przód świata Roblox)
            wolne = _wolna_droga(przeszkody, x, z, dx, dz, zasieg)
            wynik = wolne - 0.3 * math.hypot(x - c[0], z - c[2])
            if najlepszy is None or wynik > najlepszy[0] + 1e-6:
                najlepszy = (wynik, [x, oko, z], [x + dx * 20, oko - 0.5, z + dz * 20])
    if najlepszy is None:
        oko = ziemia_domyslna + 5.0
        return [c[0], oko, c[2] - max(0.35 * rozm[2], 12.0)], [c[0], oko - 0.5, c[2]]
    return najlepszy[1], najlepszy[2]


# --------------------------------------------------------------------------- zrzuty
def _pillow():
    try:
        from PIL import Image  # noqa: F401
        return True
    except Exception:
        return False


def przygotuj_zrzut(dane):
    """Bajty obrazu ze Studio → (bajty, rozszerzenie, pusty). Z Pillow: szerokość ≤ 1600 px, JPG jakości 85,
    i sprawdzenie, czy obraz nie jest jednolitą plamą (Studio w tle nie rysuje świata). Bez Pillow: bez zmian."""
    ext = ".jpg" if dane[:3] == b"\xff\xd8\xff" else ".png" if dane[:8] == b"\x89PNG\r\n\x1a\n" else ".png"
    try:
        import io
        from PIL import Image, ImageStat
    except Exception:
        return dane, ext, False
    try:
        im = Image.open(io.BytesIO(dane))
        im = im.convert("RGB")
        if im.width > SZEROKOSC_ZRZUTU:
            wys = max(1, round(im.height * SZEROKOSC_ZRZUTU / im.width))
            im = im.resize((SZEROKOSC_ZRZUTU, wys), Image.LANCZOS)
        # bez górnego pasa (kostka widoku Studio w prawym górnym rogu jest rysowana zawsze)
        maly = im.crop((0, int(im.height * 0.12), im.width, im.height))
        maly.thumbnail((160, 160))
        pusty = max(ImageStat.Stat(maly.convert("L")).stddev) < 1.5
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85, optimize=True)
        return buf.getvalue(), ".jpg", pusty
    except Exception as e:
        rdzen.log("Podgląd: nie mogę przetworzyć zrzutu (%s) — zapisuję bez zmian" % e)
        return dane, ext, False


# --------------------------------------------------------------------------- migawka
def zrob_migawke(tytul, opis, kto, zrzuty=True, korzen="Workspace", katalog=None):
    """Robi migawkę z otwartego Studio i zapisuje ją w folderze. Zwraca meta. Rzuca BladHTTP (503 bez Studio,
    409 gdy inna migawka trwa)."""
    from . import studio
    korzen = sprawdz_korzen(korzen)
    if not _blokada_migawki.acquire(blocking=False):
        raise BladHTTP(409, "Inna migawka właśnie się robi. Poczekaj chwilę.")
    try:
        st = studio.stan(odswiez=True)
        if not st.get("polaczone"):
            raise BladHTTP(503, st.get("blad") or "Roblox Studio nie jest połączone.")
        dane, pierwsza, uwagi = pobierz_czesci(korzen)
        mid = rdzen.nowe_id()
        folder = os.path.join(katalog_podgladu(katalog), mid)
        rdzen.upewnij_katalog(folder)
        try:
            nazwy_zrzutow = _zrob_zrzuty(folder, dane["czesci"], uwagi) if zrzuty else []
            meta = zbuduj_meta(mid, dane, tytul, opis, kto, nazwy_zrzutow, korzen,
                               miejsce=pierwsza.get("miejsce") or {}, studio_info=st.get("studio") or {}, uwagi=uwagi)
            zapisz_migawke(folder, meta, dane)
        except BaseException:
            shutil.rmtree(folder, ignore_errors=True)      # niedokończona migawka nie może zostać w danych
            raise
        rdzen.log("Podgląd: migawka %s (%d części, %d zrzutów)" % (mid, meta["czesci"], len(nazwy_zrzutow)))
        return meta
    finally:
        _blokada_migawki.release()


def _zrob_zrzuty(folder, czesci, uwagi):
    """Trzy ujęcia ze Studio → pliki zrzut_N.jpg w folderze. Błędy i puste obrazy trafiają do `uwagi`."""
    from . import studio
    nazwy, puste = [], 0
    if not czesci:
        return nazwy
    nieudane = 0
    for nazwa, poz, cel in ujecia(czesci):
        surowe = None
        for proba in range(2):                             # Studio bywa chwilowo zajęte — jedno ponowienie
            try:
                surowe = studio.zrzut(poz, cel, timeout=30)
                break
            except BladHTTP as e:
                blad = e
                if e.status != 503:
                    break
        if surowe is None:
            uwagi.append("Zrzut „%s” się nie udał: %s" % (nazwa, blad.komunikat))
            nieudane += 1
            if nieudane >= 2:
                uwagi.append("Pominięto pozostałe zrzuty — Studio nie odpowiada.")
                break
            continue
        bajty, ext, pusty = przygotuj_zrzut(surowe)
        if pusty:
            puste += 1
            continue
        plik = "zrzut_%d%s" % (len(nazwy) + 1, ext)
        rdzen.zapisz_bajty(os.path.join(folder, plik), bajty)
        nazwy.append(plik)
    if puste:
        uwagi.append("Studio oddało puste zrzuty (%d z 3) — okno Studio jest pewnie zminimalizowane albo zamiast "
                     "widoku 3D jest otwarta karta skryptu." % puste)
    return nazwy


def zbuduj_meta(mid, dane, tytul, opis, kto, zrzuty, korzen, miejsce=None, studio_info=None, uwagi=None,
                zrodlo="studio"):
    """meta.json migawki (format z README)."""
    czesci = dane.get("czesci") or []
    licznik = {}
    for w in czesci:
        licznik[w[1]] = licznik.get(w[1], 0) + 1
    grupy = sorted(({"sciezka": dane["grupy"][i], "czesci": n} for i, n in licznik.items()),
                   key=lambda g: g["sciezka"].lower())
    miejsce, studio_info = miejsce or {}, studio_info or {}
    meta = {
        "id": mid,
        "tytul": (str(tytul or "").strip() or "Migawka %s" % rdzen.teraz()[:16].replace("T", " "))[:200],
        "opis": str(opis or "").strip()[:4000],
        "kto": str(kto or "").strip()[:60] or rdzen.git_uzytkownik(),
        "czas": rdzen.teraz(),
        "zrodlo": zrodlo,
        "czesci": len(czesci),
        "grupy": grupy,
        "zrzuty": list(zrzuty),
        "zakres": zakres(czesci),
        "miejsce": {"placeId": miejsce.get("placeId") or studio_info.get("placeId"),
                    "nazwa": studio_info.get("nazwa") or miejsce.get("nazwa")},
        "korzen": korzen,
    }
    if uwagi:
        meta["uwagi"] = list(uwagi)
    return meta


def zapisz_migawke(folder, meta, dane):
    """czesci.json zwarto (bez wcięć), potem meta.json — meta na końcu znaczy „migawka kompletna”."""
    rdzen.zapisz_bajty(os.path.join(folder, "czesci.json"),
                       json.dumps(dane, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    rdzen.zapisz_json(os.path.join(folder, "meta.json"), meta)


# --------------------------------------------------------------------------- trasy
def _lista(z):
    migawki = lista_migawek()
    return {"migawki": migawki, "najnowsza": migawki[0] if migawki else None}


def _nowa(z):
    if not z.lokalny:
        raise BladHTTP(403, "Migawkę można zrobić tylko na komputerze, na którym działa panel i Roblox Studio.")
    d = z.json or {}
    if not isinstance(d, dict):
        raise BladHTTP(400, "Oczekiwano obiektu JSON")
    zrzuty = d.get("zrzuty", True)
    zrzuty = zrzuty if isinstance(zrzuty, bool) else str(zrzuty).lower() not in ("0", "false", "nie", "")
    return zrob_migawke(d.get("tytul"), d.get("opis"), z.kto, zrzuty=zrzuty, korzen=d.get("korzen") or "Workspace")


def _czesci(z):
    folder = folder_migawki(z.params.get("id"))
    if not folder:
        raise BladHTTP(404, "Nie ma takiej migawki")
    sciezka = os.path.join(folder, "czesci.json")
    if not os.path.isfile(sciezka):
        raise BladHTTP(404, "Ta migawka nie ma listy części")
    return Odp.plik(sciezka, "application/json; charset=utf-8", pamiec_s=86400)


def _plik(z):
    folder = folder_migawki(z.params.get("id"))
    nazwa = z.params.get("nazwa")
    if not folder or not bezpieczna_nazwa(nazwa):
        raise BladHTTP(404, "Nie ma takiego pliku")
    sciezka = rdzen.w_katalogu(folder, nazwa)
    if not sciezka or not os.path.isfile(sciezka):
        raise BladHTTP(404, "Nie ma takiego pliku")
    return Odp.plik(sciezka, pamiec_s=86400)


def zarejestruj(app):
    app.dodaj("GET", "/api/podglad", _lista)
    app.dodaj("POST", "/api/podglad/migawka", _nowa)
    app.dodaj("GET", "/api/podglad/<id>/czesci", _czesci)
    app.dodaj("GET", "/api/podglad/<id>/plik/<nazwa>", _plik)


def zdrowie():
    return {"migawki": len(lista_migawek()), "pillow": _pillow(),
            "szablon": os.path.isfile(PLIK_SZABLONU)}
