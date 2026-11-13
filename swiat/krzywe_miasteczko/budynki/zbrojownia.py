# -*- coding: utf-8 -*-
"""Zbrojownia z kuźnią — mapa v2 „Krzywe Miasteczko” (PROJEKT.md, karta 5.2). Status: propozycja, nie kanon.

Ciężka, przysadzista kamienna bryła 24 × 18 × 13 (x −15…+9, z −11…+7) pod ciemnym, „wgniecionym” dachem
czterospadowym (kalenica z 3 odcinków, środkowy niżej o 1,5; przechył rz −6°, skręt ry +5°; złota kalenica, narożniki
i okap). Szyld: wielki miecz wbity w połać frontową po prawej (15° od pionu, wokół odstające dachówki). Żart: pod okapem
na lewo od drzwi tarcza „przetestowana” trzema strzałami. Po prawej otwarta kuźnia pod daszkiem pulpitowym na dwóch
krzywych słupach: palenisko z żarem, kowadło na pniu ze świecącą sztabą, beczka z wodą. Komin z tyłu po lewej
łamany w prawo (3 × −4°), z iskrami i ciemnym dymem.

Układ lokalny: (0, 0, 0) = środek działki 32 × 26 na ziemi, front z drzwiami ku +Z (drzwi w x = +4).
Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/zbrojownia.py --wyj <folder> --szer 1000
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "Zbrojownia"
OBRYS = (32, 26)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 30                    # wierzch czapy komina; dym wyżej
BUDZET = 320
INTERAKCJA = (4.0, 17.0)         # przed drzwiami, 4 study przed krawędzią działki
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz/złoto)

SCIANA, COKOL, DACH = "kamien_cieply", "kamien_cokol", "dach_zbrojownia"

# korpus
X0, X1, Z0, Z1, H = -15.0, 9.0, -11.0, 7.0, 13.0
CX, CZ, W, D = (X0 + X1) / 2.0, (Z0 + Z1) / 2.0, X1 - X0, Z1 - Z0
# dach (układ: środek górnej krawędzi ścian podniesiony o kolanko, obrót (0, +5, −6))
HR = 14.6                        # poziom podstawy dachu w osi korpusu
OKAP, OKAP_BOK = 3.0, 2.0
HD, HD_WGN = 9.0, 7.0            # wysokość dachu i wgniecionego środka (karta: −1,5; −2 czyta się z oczu gracza)
PF, PB = 12.6, 11.4              # poziomy wysięg połaci frontowej i tylnej (z okapem) → 35,5° i 38,3° (karta: 37°)
PS = 7.0                         # poziomy wysięg połaci bocznych (z okapem) → 52°
DACH_ROT = (0.0, 5.0, -6.0)
WGN = (1.0, 5.5)                 # wgnieciony odcinek kalenicy (x lokalne dachu), po prawej od osi — tam wbity miecz


def buduj(s, rnd):
    _korpus(s)
    _otwory(s)
    with s.uklad(pos=(CX, HR, CZ), obrot=DACH_ROT):
        info = _dach(s)
        # szyld: miecz wbity w połać frontową po prawej — to on wgniótł dach (spadł we wgniecenie)
        e = (WGN[0] + 2.3, 2.2, info["z_r"] + (HD_WGN - 2.2) / HD_WGN * PF)
        with s.cechy(kolizja=False):
            with s.uklad(pos=e, obrot=(info["kat_wgn"], 0, 0)):
                _dachowki(s)
            with s.uklad(pos=e, obrot=(8, -20, -6)):
                _miecz(s)
        zestaw.choragiewka_duetu(s, (-5.2, HD + 0.4, info["z_r"]), "rycerz", ry=10, przechyl=14)
    _komin(s)
    with s.cechy(kolizja=False):
        with s.uklad(pos=(-6.2, 10.0, Z1), obrot=(0, 0, 8)):
            _tarcza(s)
    _kuznia(s)
    _rekwizyty(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# =========================================================================== bryła
def _korpus(s):
    s.blok("Cokół", (CX, 0.75, CZ), (W + 0.8, 1.5, D + 0.8), COKOL, "Cobblestone")
    s.blok("Korpus", (CX, (H + 0.1) / 2.0, CZ), (W, H - 0.1, D), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Cokół rant", (CX, 1.55, CZ), (W + 1.0, 0.4, D + 1.0), "tusz")
        for sx, x in ((-1, X0), (1, X1)):
            for sz, z in ((-1, Z0), (1, Z1)):
                if sx > 0 and sz > 0:
                    continue                                   # róg przy drzwiach: obrys robi rama drzwi
                s.blok("Narożnik", (x - sx * 0.25, H / 2.0 + 0.4, z - sz * 0.25), (1.4, H - 0.6, 1.4), "tusz")
        # kolanko pod przekrzywionym dachem (lewa strona wyżej) — w tonie cienia pod okapem
        hk = 4.0
        s.blok("Kolanko", (CX, HR - (hk / 2.0 + 0.1) / 0.9945, CZ), (W - 0.6, hk, D - 0.6), cien(s, SCIANA), rot=(0, 0, -6))
        # ciosy kamienne (lekko wystające, ciemniejszy ton) — faktura muru bez tekstury
        cios = cien(s, SCIANA, 0.88)
        for x, y in ((-13.0, 11.6), (-2.4, 2.6)):
            s.blok("Cios", (x, y, Z1 + 0.1), (2.3, 1.1, 0.4), cios)
        for z, y in ((-8.5, 11.2), (-9.4, 2.7), (5.0, 5.4), (-0.5, 11.6)):
            s.blok("Cios", (X0 - 0.1, y, z), (0.4, 1.1, 2.3), cios)
        for x, y in ((-1.5, 11.2), (-10.6, 2.6), (7.2, 4.4), (1.5, 6.8)):
            s.blok("Cios", (x, y, Z0 - 0.1), (2.3, 1.1, 0.4), cios)
    # przypory z tyłu (ciężka stopa; wys. 6 — do przeskoczenia)
    for x in (-12.6, 5.4):
        s.klin("Przypora", (x, 3.0, Z0 - 0.9), (2.4, 6.0, 2.0), COKOL, "Cobblestone")


def _otwory(s):
    zestaw.drzwi(s, (4.0, 0, Z1 + 0.25), 8.0, 10.0, "drewno_ciemne", nadproze="drewno", przechyl_nadproza=-5)
    zestaw.okno(s, (-12.2, 5.5, Z1), 3.0, 4.0, przechyl=6)
    zestaw.okno(s, (X0, 8.4, -3.6), 3.4, ksztalt="okragle", przechyl=0, ry=-90)
    zestaw.okno(s, (-6.0, 6.0, Z0), 3.0, 3.4, ksztalt="luk", przechyl=-6, okiennica=DACH, strona_okiennicy=1, ry=180)
    # znaki miasteczka
    zestaw.lata(s, (X0, 4.2, 2.6), 2.6, 2.2, "pomarancz", ry=-90, przechyl=-9)
    zestaw.lata(s, (2.6, 9.2, Z0), 2.8, 2.2, "dach_twierdza", ry=180, przechyl=7)
    zestaw.wypadniety_klocek(s, (-8.4, 2.8, Z1), (-7.6, 0, 9.4), SCIANA, obrot_klocka=24)


# =========================================================================== dach
def _dach(s):
    """Dach czterospadowy z klinów i klinów narożnych; układ: (0,0,0) = środek podstawy dachu, kalenica wzdłuż X."""
    L = W + 2 * OKAP_BOK
    zr = (D / 2.0 + OKAP) - PF                                 # kalenica przesunięta ku tyłowi
    xr = L / 2.0 - PS                                          # koniec kalenicy (±)
    tyl = cien(s, DACH, 0.85)
    odc = ((-xr, WGN[0], HD), (WGN[0], WGN[1], HD_WGN), (WGN[1], xr, HD))   # 3 odcinki kalenicy; środkowy wgnieciony
    for x0, x1, h in odc:
        xc, dl = (x0 + x1) / 2.0, x1 - x0
        s.klin("Dach połać", (xc, h / 2.0, zr + PF / 2.0), (dl, h, PF), DACH, rot=(0, 180, 0))
        s.klin("Dach połać", (xc, h / 2.0, zr - PB / 2.0), (dl, h, PB), tyl)
    a = PS
    s.naroznik("Dach naroże", (-xr - a / 2.0, HD / 2.0, zr + PF / 2.0), (a, HD, PF), DACH, rot=(0, 0, 0))
    s.naroznik("Dach naroże", (xr + a / 2.0, HD / 2.0, zr + PF / 2.0), (PF, HD, a), DACH, rot=(0, 90, 0))
    s.naroznik("Dach naroże", (xr + a / 2.0, HD / 2.0, zr - PB / 2.0), (a, HD, PB), tyl, rot=(0, 180, 0))
    s.naroznik("Dach naroże", (-xr - a / 2.0, HD / 2.0, zr - PB / 2.0), (PB, HD, a), tyl, rot=(0, 270, 0))
    with s.cechy(kolizja=False):
        # jasny obrys ciemnego dachu: okap, kalenica, naroża — zloto
        s.blok("Dach okap", (0, -0.25, zr + (PF - PB) / 2.0), (L + 0.6, 0.6, PF + PB + 0.6), "zloto")
        for x0, x1, h in odc:
            s.blok("Dach kalenica", ((x0 + x1) / 2.0, h - 0.1, zr), (x1 - x0 + 0.3, 1.0, 1.6), "zloto")
        ez = (zr + PF, zr - PB)
        for sx in (-1, 1):
            for z in ez:
                s.belka("Dach naroże listwa", (sx * (L / 2.0 + 0.1), 0.1, z + (0.1 if z > 0 else -0.1)),
                        (sx * xr, HD - 0.05, zr), 0.9, "zloto", "SmoothPlastic")

    return {"z_r": zr, "kat_przod": math.degrees(math.atan2(HD, PF)), "kat_tyl": math.degrees(math.atan2(HD, PB)),
            "kat_wgn": math.degrees(math.atan2(HD_WGN, PF))}


def _dachowki(s):
    """4 odstające dachówki wokół miejsca wbicia miecza (układ połaci: XZ = płaszczyzna dachu)."""
    with s.cechy(cien=False):
        for (x, z, rx, rz, ry), k in zip(((-2.1, -0.4, -28, 12, 10), (2.0, -0.9, -22, -26, -8), (-1.6, 1.7, 30, 18, -14),
                                          (1.9, 1.5, 24, -30, 18)),
                                         (DACH, cien(s, DACH, 0.8), cien(s, DACH, 0.8), DACH)):
            s.blok("Dachówka", (x, 0.35, z), (2.4, 0.5, 2.0), k, rot=(rx, ry, rz))


def _miecz(s):
    """Miecz-szyld wbity sztychem w dach: długość 14,9 (3,5 schowane w połaci), oś +Y, płaz ku +Z. 12 części."""
    stal = "tynk_blekit"
    s.blok("Miecz ostrze", (0, 1.0, 0), (2.6, 9.0, 0.8), stal)
    s.blok("Miecz płetwa", (0, 1.28, 0), (3.7, 9.55, 0.35), "tusz")
    s.blok("Miecz zbrocze", (0, 1.8, 0), (0.7, 6.5, 1.0), cien(s, stal, 0.78))
    s.blok("Miecz jelec", (0, 6.1, 0), (7.0, 1.2, 1.4), "zloto")
    s.blok("Miecz jelec obrys", (0, 6.1, 0), (7.8, 2.0, 0.45), "tusz")
    for zn in (-1, 1):
        s.blok("Miecz jelec koniec", (zn * 3.6, 6.75, 0), (1.2, 1.9, 1.3), "zloto", rot=(0, 0, -zn * 20))
    s.blok("Miecz rękojeść", (0, 8.0, 0), (1.3, 2.6, 1.3), "drewno_ciemne")
    with s.cechy(cien=False):
        for y in (7.4, 8.6):
            s.blok("Miecz owijka", (0, y, 0), (1.5, 0.45, 1.5), "drewno_jasne")
    s.kula("Miecz głowica", (0, 10.2, 0), 2.3, "zloto")
    s.kula("Miecz głowica obrys", (0, 10.2, -0.4), 2.65, "tusz")


def _komin(s):
    """Komin z tyłu po lewej: 3 segmenty ok. 4 × 4 (Brick), każdy +4° w prawo, czapa tusz na ok. 30, iskry i dym."""
    with s.uklad(pos=(-10.4, 14.0, -8.6)), s.cechy(kolizja=False):
        xe, ye, kat = zestaw.lamana(s, "Komin", [(5.15, 4.2, -4.0), (5.15, 4.0, -4.0), (5.15, 3.8, -4.0)],
                                    [COKOL, cien(s, COKOL)], "Brick")
        s.blok("Komin czapa", (xe, ye + 0.2, 0), (4.8, 0.7, 4.8), "tusz", rot=(0, 0, kat))
        with s.cechy(cien=False):
            for x, y, z, k in ((0.9, 1.5, 0.7, 20), (-1.1, 2.3, -0.5, 40), (0.2, 3.3, 1.1, 10)):
                s.blok("Komin iskra", (xe + x, ye + y, z), (0.7, 0.7, 0.7), "neon_ogien", "Neon", rot=(k, k, 30))
        # dym z kuźni: szare klocki (po krytyce: 3 ciemne kule czytały się jak bomby)
        zestaw.dym(s, (xe + 0.5, ye + 2.6, 0.2), n=3, skala=1.1, kolor=cien(s, "biel", 0.72), ksztalt="klocek")


def _tarcza(s):
    """Tarcza Ø 8 „przetestowana” trzema strzałami; układ: środek tarczy na licu ściany, +Z na zewnątrz. 14 części."""
    s.walec("Tarcza obrys", (0, 0, 0.25), 4.85, 0.3, "tusz", os="z")
    s.walec("Tarcza rant", (0, 0, 0.55), 4.4, 0.5, "zloto", os="z")
    s.walec("Tarcza", (0, 0, 0.95), 4.0, 0.5, DACH, os="z")
    s.blok("Tarcza guz", (0, 0, 1.35), (1.8, 1.8, 0.5), "zloto", rot=(0, 0, 45))
    s.blok("Tarcza szczerba", (3.0, 2.9, 0.7), (1.5, 1.5, 1.2), SCIANA, rot=(0, 0, 40))
    for (x, y, rx, ry), lot in zip(((-1.7, 1.6, -18, -24), (1.9, -0.6, 22, 30), (-0.8, -2.2, 30, -8)),
                                   ("czerwien", "biel", "czerwien")):
        with s.uklad(pos=(x, y, 1.2), obrot=(rx, ry, 0)):
            s.blok("Strzała", (0, 0, 2.2), (0.45, 0.45, 5.0), "drewno_jasne")
            with s.cechy(cien=False):
                s.blok("Strzała lotka", (0, 0, 4.0), (0.3, 1.4, 1.6), lot)
                s.blok("Strzała lotka", (0, 0, 4.15), (1.4, 0.3, 1.6), lot)


# =========================================================================== kuźnia
def _kuznia(s):
    """Otwarta przybudówka po prawej (x +9…+16, z −8…+7): podłoga, murek, daszek pulpitowy na 2 krzywych słupach,
    palenisko z okapem, kowadło na pniu, narzędzia na ścianie."""
    s.blok("Kuźnia podłoga", (12.6, 0.15, -0.6), (6.8, 0.3, 15.6), COKOL, "Cobblestone")
    s.blok("Kuźnia murek", (12.35, 3.05, -8.6), (7.1, 5.5, 1.0), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Kuźnia murek rant", (12.35, 5.95, -8.6), (7.1, 0.4, 1.3), "tusz")
        for x, z, seg in ((14.4, -7.4, [(4.3, 1.0, 6), (3.9, 0.9, -12)]), (14.4, 6.4, [(4.1, 1.0, -7), (4.1, 0.9, 13)])):
            zestaw.lamana(s, "Kuźnia słup", seg, "drewno_ciemne", "Wood", start=(x, 0.3), z=z)
        s.belka("Kuźnia płatew", (14.4, 8.95, -8.6), (14.4, 8.95, 7.6), 1.0, "drewno_ciemne")
        s.blok("Kuźnia daszek okap", (15.45, 9.4, -0.4), (0.6, 1.1, 17.6), "zloto", rot=(0, 0, -21))
    s.blok("Kuźnia daszek", (12.2, 10.67, -0.4), (7.7, 0.8, 17.2), DACH, rot=(0, 0, -21))
    with s.cechy(kolizja=False):
        s.blok("Kuźnia daszek rant", (12.2, 10.67, 7.95), (7.7, 1.0, 0.4), "zloto", rot=(0, 0, -21))
    # palenisko przy murku
    s.blok("Palenisko", (11.8, 1.8, -6.15), (4.4, 3.0, 4.0), COKOL, "Cobblestone")
    with s.cechy(kolizja=False):
        s.blok("Palenisko rant", (11.8, 3.2, -6.15), (4.8, 0.5, 4.4), "tusz")
        with s.cechy(cien=False):
            s.blok("Palenisko żar", (11.8, 3.6, -6.0), (3.6, 0.7, 3.0), "neon_ogien", "Neon")
        s.blok("Palenisko okap rant", (11.8, 6.7, -6.4), (5.0, 0.4, 4.0), "tusz")
        s.blok("Palenisko okap", (11.8, 7.5, -6.5), (4.6, 1.4, 3.6), COKOL, rot=(-8, 0, 0))
        s.blok("Palenisko przewód", (11.8, 9.85, -7.0), (2.0, 3.6, 2.0), cien(s, COKOL), "Brick")
        # narzędzia na ścianie korpusu (lico x = +9, ku +X)
        s.blok("Wieszak", (9.2, 9.0, 0.5), (0.4, 0.5, 6.0), "tusz")
        with s.cechy(cien=False):
            for k in (-12, 12):
                s.blok("Obcęgi", (9.35, 7.3, -1.5), (0.4, 3.6, 0.4), "tusz", rot=(k, 0, 0))
            s.blok("Młot trzonek", (9.4, 7.2, 2.6), (0.4, 3.2, 0.4), "drewno", rot=(-6, 0, 0))
            s.blok("Młot obuch", (9.6, 5.6, 2.8), (0.9, 1.0, 1.9), "metal_ciemny")
    _szlifierka(s, (11.6, 0.3, 1.5), ry=-18)        # po krytyce zamiana: toczydło w głąb kuźni, kowadło przed nią


def _kowadlo(s, pos):
    """Kowadło 6 × 3 × 3 (metal_ciemny, bez materiału Metal) na pniu, świecąca sztaba i młot na wierzchu. 8 części."""
    with s.uklad(pos=pos, obrot=(0, 6, 0)):
        s.walec("Pień", (0, 0.9, 0), 1.7, 1.8, "drewno", "Wood", os="y")
        s.blok("Kowadło stopa", (0, 2.2, 0), (4.2, 0.8, 2.6), "metal_ciemny")
        with s.cechy(kolizja=False):
            s.blok("Kowadło talia", (0, 3.1, 0), (2.6, 1.0, 1.8), cien(s, "metal_ciemny", 0.85))
            s.blok("Kowadło głowa", (-0.2, 4.2, 0), (3.8, 1.2, 3.0), "metal_ciemny")
            s.klin("Kowadło róg", (2.8, 4.2, 0), (1.8, 1.2, 2.2), "metal_ciemny", rot=(0, -90, 180))
            with s.cechy(cien=False):
                s.blok("Sztaba żarząca", (0.2, 5.2, -0.5), (3.6, 0.7, 0.9), "neon_ogien", "Neon", rot=(0, 16, 0))
                s.blok("Młot trzonek", (-0.6, 5.05, 0.8), (3.4, 0.5, 0.5), "drewno", rot=(0, -25, 0))
                s.blok("Młot obuch", (-2.1, 5.25, 1.5), (1.0, 1.0, 1.9), "metal_ciemny", rot=(0, -25, 0))


# =========================================================================== rekwizyty przy wejściu
def _rekwizyty(s, rnd):
    zestaw.beczka(s, (13.8, 0.3, -3.4), "woda", przechyl=(0, 6))
    with s.uklad(pos=(11.4, 0, 10.6), obrot=(0, 180, 0), skala=1.25):   # kowadło w słońcu, rogiem ku drzwiom
        _kowadlo(s, (0, 0, 0))
    zestaw.latarnia(s, (14.3, 0, 9.6), wys=9.0, ry=180, plama_r=3.0)
    # beczka z bronią (duży), hełm (mały) — przy oknie, z dala od drzwi i pola interakcji
    zestaw.beczka(s, (-13.9, 0, 10.4), None, r=1.7, h=3.8, przechyl=(5, 0))
    with s.cechy(kolizja=False):
        for x, z, rx, rz, kol in ((-14.3, 10.0, -8, -7, "tynk_blekit"), (-13.3, 10.9, 6, 9, "zloto")):
            with s.uklad(pos=(x, 3.0, z), obrot=(rx, 0, rz)):
                s.blok("Włócznia drzewce", (0, 2.6, 0), (0.5, 5.6, 0.5), "drewno_jasne")
                s.blok("Włócznia grot", (0, 6.0, 0), (1.1, 1.1, 0.5), kol, rot=(0, 0, 45))
        with s.uklad(pos=(-13.6, 3.0, 9.9), obrot=(-14, 0, 6)):
            s.blok("Miecz w beczce", (0, 2.2, 0), (0.9, 4.4, 0.35), "tynk_blekit")
            s.blok("Miecz w beczce jelec", (0, 4.6, 0), (2.4, 0.5, 0.6), "zloto")
        with s.uklad(pos=(-10.2, 0, 10.4), obrot=(14, 30, -10)):
            s.kula("Hełm", (0, 0.9, 0), 2.4, "tynk_blekit")
            s.blok("Hełm rondo", (0, 0.45, 0), (2.9, 0.4, 2.9), cien(s, "tynk_blekit", 0.8))
            with s.cechy(cien=False):
                s.blok("Hełm pióro", (0, 2.2, 0), (0.5, 0.9, 2.0), "czerwien")
    # sąg drewna za kuźnią (tył też jest dokończony)
    with s.cechy(kolizja=False):
        for i, (y, z, ry) in enumerate(((0.6, -10.6, 2), (0.6, -11.9, -3), (1.8, -11.2, 5))):
            s.blok("Sąg", (12.6, y, z), (5.0, 1.2, 1.2), "drewno" if i != 2 else "drewno_jasne", "Wood", rot=(0, ry, 0))


def _szlifierka(s, pos, ry=0.0):
    """Toczydło (kamień szlifierski) przed kuźnią: koło Ø 4 na osi, kozioł z 2 krzywych nóg, korytko z wodą, korba.
    pos = środek na ziemi; koło w płaszczyźnie XY (widać je z frontu). 8 części."""
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        s.blok("Toczydło korytko", (0, 0.8, 0), (4.4, 1.6, 2.4), "drewno", "WoodPlanks")
        with s.cechy(kolizja=False):
            with s.cechy(cien=False):
                s.blok("Toczydło woda", (0, 1.62, 0), (3.8, 0.2, 1.8), "woda")
            for zn, k in ((-1, 7), (1, -9)):
                s.blok("Toczydło noga", (zn * 1.6, 2.4, 0), (0.6, 3.6, 0.6), "drewno_ciemne", "Wood", rot=(0, 0, k))
            s.walec("Toczydło oś", (0, 3.6, 0), 0.3, 4.4, "tusz", os="x")
            s.walec("Toczydło koło", (0, 3.6, 0), 2.0, 0.9, "kamien_cieply", os="x", rot=(0, 90, 0))
            s.walec("Toczydło koło obrys", (0, 3.6, 0), 2.35, 0.5, "tusz", os="x", rot=(0, 90, 0))
            s.blok("Toczydło korba", (2.45, 3.0, 0), (0.4, 1.4, 0.4), "zloto", rot=(0, 0, 25))
