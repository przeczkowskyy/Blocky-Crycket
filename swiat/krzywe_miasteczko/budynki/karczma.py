# -*- coding: utf-8 -*-
"""Karczma — „Gospoda Pod Pękatym Kotłem” (mapa v2 „Krzywe Miasteczko”, karta PROJEKT.md 5.1).

Dominanta miasteczka: pękaty parter 38 × 22 (pionowy, skręt −4°), nawisające piętro 41 × 25 przechylone w lewo (rz +6°,
skręt +4°), wielka czerwona czapa dachu w kontrze (rz −4°, połacie ok. 46° i 57°), łamana na trzy części (rz +5° / 0° /
−4°, środek kalenicy niżej o 1,5). Żart: komin-kocioł z chochlą i parą na połaci FRONTOWEJ po lewej (po krytyce: z tyłu
nie było go widać z rynku). Szyld: pieczony udziec na wysięgniku z prawego narożnika. Przed fasadą po lewej tablica zleceń
z trzema kartkami (własne piktogramy: miecz, jajo, klucz) i parującym kubkiem kakao na daszku (echo). Bez alkoholu
i bez liter.

Konwencja: (0, 0, 0) = środek działki 46 × 38 na wierzchu podium, front z drzwiami ku +Z. Podium, schody i latarnie
stawia generator. Status: propozycja (noc 13.11.2026), nie kanon.

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/karczma.py --wyj <folder> --szer 1000
"""
import contextlib
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.biblioteka.scena import macierz_obrotu, mnoz, razy_wektor  # noqa: E402

NAZWA = "Karczma"
OBRYS = (46, 38)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 50                    # wierzch pary nad kotłem
BUDZET = 470
INTERAKCJA = ((6.0, 9.0), (-11.0, 17.0))   # przed drzwiami i przed tablicą zleceń
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

SCIANA, DACH = "tynk_krem", "dach_karczma"

# --- bryła (karta 5.1)
W0, D0, H0, ZP0, RY0 = 38.0, 22.0, 12.0, -6.0, -4.0            # parter: x ±19, z −17…+5
W1, D1, H1 = 41.0, 25.0, 9.0                                     # piętro: nawis front 3, lewo 2, prawo 1
P1 = (-0.5, H0, -4.5)                                            # środek podstawy piętra
O1 = (0.0, 4.0, 6.0)                                             # piętro: ry +4°, rz +6° (bezwzględnie)
ZAG1 = (W1 / 2.0) * math.tan(math.radians(6.0)) + 0.1            # zagłębienie wyższego końca piętra
DACH_WYS, DACH_OKAP, DACH_BOK, DACH_PODZIAL = 18.5, 2.5, 2.5, 0.62
DACH_UNIES = 1.3                                                 # dach nad krawędzią ścian piętra
O_DACH = (0.0, 0.0, -10.0)                                       # względem piętra → bezwzględnie rz −4° (kontra)
SKALA_SZYLDU = 1.2                                               # udziec 12 × 6 (karta: 10 × 5 — za mały z rynku)
DY_KOTLA = -2.0                                                  # obniżenie kotła (wierzch pary ≤ 50)
DACH_L = W1 + 2 * DACH_BOK                                       # długość dachu wzdłuż X
DACH_SEG = ((5.0, 0.0), (0.0, -1.5), (-4.0, 0.0))                # 3 części połaci: (rz°, obniżenie kalenicy)
SEG_L = DACH_L / 3.0


class _Ramy(object):
    """Liczy położenie punktu z zagnieżdżonych układów (pos, obrot) w układzie budynku — do zaczepiania łańcuchów
    i wysięgników między bryłami o różnych przechyłach."""

    def __init__(self, *ramy):
        self.ramy = ramy

    def __call__(self, p):
        R, t = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), (0.0, 0.0, 0.0)
        for pos, obrot in self.ramy:
            dt = razy_wektor(R, pos)
            t = (t[0] + dt[0], t[1] + dt[1], t[2] + dt[2])
            R = mnoz(R, macierz_obrotu(*obrot))
        v = razy_wektor(R, p)
        return (t[0] + v[0], t[1] + v[1], t[2] + v[2])


def buduj(s, rnd):
    _parter(s)
    _pietro_i_dach(s)
    _szyld_udziec(s)
    with s.grupa(NAZWA + "/Tablica"):
        _tablica(s)
    _otoczenie(s, rnd)
    for p in INTERAKCJA:
        zestaw.punkt_interakcji(s, NAZWA, p)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# =========================================================================== parter
def _parter(s):
    with s.uklad(pos=(0, 0, ZP0), obrot=(0, RY0, 0)):
        s.blok("Cokół", (0, 0.6, 0), (W0 + 0.8, 1.2, D0 + 0.8), "kamien_cokol", "Cobblestone")
        with s.cechy(kolizja=False):
            s.blok("Cokół rant", (0, 1.3, 0), (W0 + 1.0, 0.4, D0 + 1.0), "tusz")
        s.blok("Parter", (0, H0 / 2.0, 0), (W0, H0, D0), SCIANA)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * (W0 / 2.0 - 0.25), H0 / 2.0 + 0.4, sz * (D0 / 2.0 - 0.25)), (1.3, H0 - 0.6, 1.3), "tusz")
            # pas „cienia z klocka” pod nawisem; zarazem wypełnia klin między parterem a przechylonym piętrem
            s.blok("Pas cienia", (0, 11.5, 0), (W0 + 0.2, 1.4, D0 + 0.2), cien(s, SCIANA))
            # klin domyka szczelinę pod prawą (wyższą) połową przechylonego piętra
            s.klin("Pas cienia klin", (10.25, 13.35, 0), (D0 + 0.2, 2.3, 17.7), cien(s, SCIANA), rot=(0, 90, 0))
        F = D0 / 2.0
        # --- front: drzwi łukowe po prawej (x = +6), okna różne
        zestaw.drzwi(s, (6.0, 0, F + 0.25), 8.0, 11.0, luk=True, nadproze=None)
        zestaw.okno(s, (14.6, 6.4, F), 4.0, 5.0, przechyl=-6, okiennica=DACH, strona_okiennicy=1)
        zestaw.okno(s, (-0.6, 7.2, F), 3.0, ksztalt="okragle", przechyl=0)
        zestaw.okno(s, (-13.0, 6.0, F), 3.0, 4.0, przechyl=5, swiatlo="woda_gleboka")       # za tablicą
        # --- bok lewy (−X)
        zestaw.okno(s, (-W0 / 2.0, 6.2, 3.5), 3.4, 4.2, przechyl=7, ry=-90, swiatlo="woda_gleboka")
        zestaw.lata(s, (-W0 / 2.0, 3.8, -6.0), 2.8, 2.2, "dach_twierdza", ry=-90, przechyl=-9)
        # --- bok prawy (+X)
        zestaw.okno(s, (W0 / 2.0, 6.0, -2.5), 4.0, 4.0, przechyl=-5, ry=90)
        zestaw.wypadniety_klocek(s, (W0 / 2.0, 2.6, -7.5), (W0 / 2.0 + 1.7, 0, -4.2), SCIANA, ry=90, obrot_klocka=24)
        # --- tył: drzwi kuchenne, okna, łata
        zestaw.drzwi(s, (11.0, 0, -F - 0.25), 6.0, 8.0, ry=180, tanie=True, przechyl_nadproza=6)
        zestaw.okno(s, (-6.0, 6.6, -F), 3.2, 4.0, przechyl=6, ry=180)
        zestaw.okno(s, (2.5, 7.0, -F), 2.6, 3.0, przechyl=-5, ry=180, swiatlo="woda_gleboka", tanie=True)
        zestaw.lata(s, (-14.5, 4.0, -F), 2.6, 2.4, "pomarancz", ry=180, przechyl=10)
        # patelnia na haku przy drzwiach kuchennych
        with s.uklad(pos=(5.6, 6.2, -F), obrot=(0, 180, 0)), s.cechy(kolizja=False, cien=False):
            s.blok("Patelnia hak", (0, 2.3, 0.2), (0.4, 0.8, 0.4), "tusz")
            s.blok("Patelnia trzonek", (0, 1.1, 0.35), (0.6, 2.4, 0.4), "drewno_ciemne", rot=(0, 0, 8))
            s.walec("Patelnia", (0.15, -1.2, 0.35), 1.5, 0.4, "metal_ciemny", os="z")


# =========================================================================== piętro i dach
def _pietro_i_dach(s):
    zg = ZAG1
    with s.uklad(pos=P1, obrot=O1):
        with s.cechy(kolizja=False):
            s.blok("Wieniec", (0, 0.35, 0), (W1 + 0.5, 0.9, D1 + 0.5), "tusz")
        s.blok("Piętro", (0, (H1 - zg) / 2.0, 0), (W1, H1 + zg, D1), SCIANA)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                top = H1 + 0.25 if sx > 0 else H1 + 1.6
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * (W1 / 2.0 - 0.25), (0.8 + top) / 2.0, sz * (D1 / 2.0 - 0.25)), (1.3, top - 0.8, 1.3), "tusz")
            # belki: krzywe zastrzały w ciemnym drewnie (bez symetrycznych X)
            F = D1 / 2.0
            for (x1, y1), (x2, y2) in (((-19.4, 1.0), (-15.6, 8.4)), ((-7.4, 1.0), (-4.6, 8.6)), ((4.8, 8.5), (1.8, 1.0)),
                                      ((14.0, 1.0), (17.6, 8.3))):
                s.belka("Zastrzał", (x1, y1, F + 0.2), (x2, y2, F + 0.2), 0.9, "drewno_ciemne", "Wood", 0.5)
            for (z1, y1), (z2, y2) in (((-9.5, 1.0), (-5.2, 8.4)), ((6.0, 8.4), (10.5, 1.0))):
                s.belka("Zastrzał", (-W1 / 2.0 - 0.2, y1, z1), (-W1 / 2.0 - 0.2, y2, z2), 0.9, "drewno_ciemne", "Wood", 0.5)
            s.belka("Zastrzał", (W1 / 2.0 + 0.2, 1.0, 3.0), (W1 / 2.0 + 0.2, 8.3, 7.4), 0.9, "drewno_ciemne", "Wood", 0.5)
        # okna piętra: trzy różne na froncie, po jednym na bokach i z tyłu
        yo = 4.8
        zestaw.okno(s, (-11.4, yo, D1 / 2.0), 4.0, 4.6, przechyl=-7)
        zestaw.okno(s, (-1.4, yo + 0.4, D1 / 2.0), 3.4, ksztalt="okragle")
        zestaw.okno(s, (9.0, yo - 0.2, D1 / 2.0), 3.0, 3.8, przechyl=8)
        zestaw.okno(s, (-W1 / 2.0, yo, -1.5), 3.0, 4.0, przechyl=-6, ry=-90)
        zestaw.okno(s, (W1 / 2.0, yo, -4.0), 3.0, ksztalt="okragle", ry=90, swiatlo="woda_gleboka")
        zestaw.okno(s, (-8.0, yo, -D1 / 2.0), 3.6, 4.2, przechyl=-5, ry=180, swiatlo="woda_gleboka")
        zestaw.okno(s, (10.0, yo + 0.3, -D1 / 2.0), 2.8, 3.4, ry=180, przechyl=7, swiatlo="woda_gleboka")
        # skrzynka z kwiatami na parapecie lewego okna piętra
        with s.uklad(pos=(-11.4, 2.0, D1 / 2.0 + 1.0), obrot=(0, 0, -7)), s.cechy(kolizja=False, cien=False):
            s.blok("Okno kwiaty liście", (0, 0.75, 0.1), (4.2, 0.7, 0.8), "lisc")
            for i, (x, k) in enumerate(((-1.4, 20), (0.1, 45), (1.5, 10))):
                s.blok("Okno kwiat", (x, 1.35, 0.15), (0.9, 0.9, 0.9), ("czerwien", "zloto", "czerwien")[i], rot=(15, k, 10))
        # kroksztyny pod wielkim lewym nawisem (klin: płaska góra pod piętrem, pion przy ścianie parteru)
        with s.cechy(kolizja=False):
            for x in (-17.6, -7.0):
                d = 3.0 - 0.1378 * x + 0.4                         # nawis frontu w tym miejscu + wpuszczenie w ścianę
                h = max(2.2, min(3.6, 0.7 * d))
                s.klin("Kroksztyn", (x, -0.1 - h / 2.0, D1 / 2.0 - 0.3 - d / 2.0), (1.2, h, d), "drewno_ciemne", "Wood",
                       rot=(0, 180, 180))
        # --- dach-czapa w kontrze
        with s.uklad(pos=(0, H1 + DACH_UNIES, 0), obrot=O_DACH):
            ext = (W1 / 2.0) * math.sin(math.radians(10.0)) + DACH_UNIES + 0.4
            with s.cechy(kolizja=False):
                s.blok("Kolanko", (0, -ext / 2.0 + 0.05, 0), (W1 - 0.8, ext, D1 - 0.8), SCIANA)
            info = _dach_lamany(s)
            _dach_detale(s, info)
            # okienka w szczytach (ciemna szyba) — boki nie są gołe
            xs = SEG_L / 2.0 + 0.3
            with _segment(s, 2):
                zestaw.okno(s, (xs, 6.4, info["z_kalenicy"] + 0.6), 2.6, 3.2, przechyl=-7, ry=90, swiatlo="woda_gleboka", tanie=True)
            with _segment(s, 0):
                zestaw.okno(s, (-xs, 5.6, info["z_kalenicy"] - 0.4), 3.0, 2.6, przechyl=6, ry=-90, swiatlo="woda_gleboka", tanie=True)
                zestaw.lata(s, (-xs, 10.6, info["z_kalenicy"] + 1.2), 2.2, 1.8, "dach_twierdza", ry=-90, przechyl=14)
            _kociol(s, info)


def _seg_nr(x):
    return 0 if x < -SEG_L / 2.0 else (2 if x > SEG_L / 2.0 else 1)


@contextlib.contextmanager
def _segment(s, i):
    """Układ i-tej części dachu łamanego (0 lewa, 1 środek, 2 prawa): środek części na y = 0, obrót rz z DACH_SEG.
    Współrzędne x w środku liczy się względem środka części (x − (i − 1)·SEG_L)."""
    with s.uklad(pos=((i - 1) * SEG_L, 0, 0), obrot=(0, 0, DACH_SEG[i][0])):
        yield


def _wys_seg(i):
    return DACH_WYS + DACH_SEG[i][1]


def _dach_lamany(s):
    """Dach-czapa łamany na 3 części (po krytyce: 46 studów prostej kalenicy dominanty): każda część to 2 kliny połaci,
    rant i kalenica, części skręcone rz +5° / 0° / −4°, kalenica środka niżej o 1,5; skrajne zachodzą 0,4 na środek.
    Szczyty (tynk) tylko na końcach. Zwraca dict jak zestaw.dach_czapa."""
    gl, okap, podzial = D1, DACH_OKAP, DACH_PODZIAL
    zr = gl / 2.0 - podzial * gl
    Pf, Pb = podzial * gl + okap, (1.0 - podzial) * gl + okap
    for i in range(3):
        H = _wys_seg(i)
        dl = SEG_L + (0.8 if i != 1 else 0.0)
        dx = 0.4 if i == 0 else (-0.4 if i == 2 else 0.0)
        with _segment(s, i):
            s.klin("Dach połać", (dx, H / 2.0, zr + Pf / 2.0), (dl, H, Pf), DACH, rot=(0, 180, 0))
            s.klin("Dach połać", (dx, H / 2.0, zr - Pb / 2.0), (dl, H, Pb), cien(s, DACH, 0.85))
            with s.cechy(kolizja=False):
                s.blok("Dach rant", (dx, -0.2 - 0.06 * (i != 1), 0), (dl + 0.5 * (i != 1), 0.45, gl + 2 * okap + 0.6), "tusz")
                s.blok("Dach kalenica", (dx, H - 0.1, zr), (dl + 0.6 * (i != 1), 0.9, 1.5), "tusz")
                if i != 1:                                             # tynkowany szczyt na końcu dachu
                    kf, kb = math.atan2(H, Pf), math.atan2(H, Pb)
                    x = (1 if i == 2 else -1) * (SEG_L / 2.0 + 0.15)
                    for k, rot, zn in ((kf, (0, 180, 0), 1), (kb, (0, 0, 0), -1)):
                        yt = H - 0.9 / math.cos(k)
                        h = yt - 0.3
                        d = h / math.tan(k)
                        s.klin("Dach szczyt", (x, 0.3 + h / 2.0, zr + zn * d / 2.0), (0.3, h, d), SCIANA, rot=rot)
    return {"kat_przod": math.degrees(math.atan2(DACH_WYS, Pf)), "kat_tyl": math.degrees(math.atan2(DACH_WYS, Pb)),
            "z_kalenicy": zr, "wys": DACH_WYS}


@contextlib.contextmanager
def _na_polaci(s, info, x, t, przod=True):
    """Układ na połaci dachu łamanego w punkcie x (dach) i t (0 okap, 1 kalenica); lokalne +Y = normalna połaci."""
    i = _seg_nr(x)
    zr, H = info["z_kalenicy"], _wys_seg(i)
    if przod:
        z0 = D1 / 2.0 + DACH_OKAP
        kat = math.degrees(math.atan2(H, z0 - zr))
    else:
        z0 = -D1 / 2.0 - DACH_OKAP
        kat = -math.degrees(math.atan2(H, zr - z0))
    z = z0 + (zr - z0) * t
    with _segment(s, i), s.uklad(pos=(x - (i - 1) * SEG_L, H * t, z), obrot=(kat, 0, 0)):
        yield


def _rzad(s, info, nazwa, t, x0, x1, grub, kolor, przod=True):
    """Rząd dachówek od x0 do x1, pocięty na części dachu łamanego."""
    for i in range(3):
        a, b = max(x0, (i - 1.5) * SEG_L + 0.3), min(x1, (i - 0.5) * SEG_L - 0.3)
        if b - a < 1.0:
            continue
        with _na_polaci(s, info, (a + b) / 2.0, t, przod):
            s.blok(nazwa, (0, 0.12, 0), (b - a, grub, 1.0), kolor)


def _dach_detale(s, info):
    """Rzędy dachówek (cień), odstające dachówki, lukarna z okrągłym oknem, chorągiewka duetu na kalenicy."""
    with s.cechy(kolizja=False):
        ciemny = cien(s, DACH, 0.86)
        # rzędy frontu omijają kocioł (x −17…−5, t 0,2…0,55)
        for t, x0, x1 in ((0.30, -4.0, 4.0), (0.33, 4.6, 22.5), (0.62, -22.5, -6.0), (0.58, 9.5, 22.5), (0.12, -22.5, -4.5)):
            _rzad(s, info, "Rząd dachówek", t, x0, x1, 0.45, ciemny)
        for x, t, k in ((-3.0, 0.45, 18), (15.5, 0.75, -24)):
            with _na_polaci(s, info, x, t):
                s.blok("Odstająca dachówka", (0, 0.35, 0), (2.4, 0.4, 1.8), DACH, rot=(-14, k, 6))
        # tylna połać: dwa rzędy i łata
        for t, x0, x1 in ((0.35, -22.5, -2.0), (0.4, 3.0, 22.5)):
            _rzad(s, info, "Rząd dachówek", t, x0, x1, 0.45, cien(s, DACH, 0.72), przod=False)
        with _na_polaci(s, info, 12.0, 0.6, przod=False):
            with s.uklad(obrot=(-90, 0, 0)):
                zestaw.lata(s, (0, 0, 0.05), 3.0, 2.6, "zloto", przechyl=12)
    # lukarna na połaci frontowej, po prawej od osi (w środkowej części dachu łamanego)
    zr = info["z_kalenicy"]
    zf = D1 / 2.0 + DACH_OKAP
    H1s = _wys_seg(1)
    xl, zl = 3.8, 9.0                                         # przód lukarny
    yl = H1s * (zf - zl) / (zf - zr)                            # wysokość połaci w przodzie lukarny
    with _segment(s, 1), s.uklad(pos=(xl, 0, zl), obrot=(0, -6, 0)):
        with s.cechy(kolizja=False):
            s.blok("Lukarna", (0, yl + 2.2, -2.6), (5.6, 5.6 + 2.0, 5.2), SCIANA)
            for sx in (-1, 1):
                s.blok("Lukarna narożnik", (sx * 2.6, yl + 2.4, 0.05), (0.8, 5.6, 0.8), "tusz")
            with s.uklad(pos=(0, yl + 5.6, -2.0), obrot=(0, 0, 5)):
                s.klin("Lukarna daszek", (-1.85, 1.1, 0), (7.6, 2.2, 3.7), DACH, rot=(0, 90, 0))
                s.klin("Lukarna daszek", (1.85, 1.1, 0), (7.6, 2.2, 3.7), cien(s, DACH, 0.85), rot=(0, -90, 0))
                s.blok("Lukarna rant", (0, -0.15, 0.2), (7.9, 0.4, 8.2), "tusz")
                s.blok("Lukarna kalenica", (0, 2.2, 0.1), (0.8, 0.6, 7.9), "tusz")
        zestaw.okno(s, (0, yl + 2.9, 0.1), 2.6, ksztalt="okragle", przechyl=0)
    # chorągiewka duetu na prawym końcu kalenicy
    with _segment(s, 2):
        zestaw.choragiewka_duetu(s, (17.0 - SEG_L, DACH_WYS + 0.3, zr), "kot", przechyl=-12)


def _kociol(s, info):
    """Komin-kocioł na połaci FRONTOWEJ (po krytyce: z tylnej było widać z rynku tylko rant i chochlę): ceglany cokół
    wyrastający z połaci, kocioł Ø 9 z brzuchem Ø 11 (metal_ciemny, rant tusz) pochylony o 12° ku rynkowi, żar pod dnem,
    chochla 12 pod 30° i para z 4 klocków 3/4/5/6 odpływająca w lewo. W lewej części dachu łamanego."""
    xk, zk = -11.0 + SEG_L, 5.0                    # x względem środka lewej części dachu
    with _segment(s, 0), s.cechy(kolizja=False):
        s.blok("Kocioł cokół", (xk, 10.3, zk - 0.2), (5.4, 5.4, 4.6), "kamien_cokol", "Brick", rot=(0, 8, 5))
        s.blok("Kocioł podstawa", (xk + 0.2, 15.0 + DY_KOTLA, zk - 0.2), (6.6, 0.6, 6.0), "tusz", rot=(0, 8, 5))
        with s.uklad(pos=(xk + 0.4, 15.25 + DY_KOTLA, zk), obrot=(12, 0, 8)):
            for kat in (30, 150, 270):
                a = math.radians(kat)
                s.blok("Kocioł nóżka", (2.4 * math.cos(a), 0.55, 2.4 * math.sin(a)), (1.0, 1.4, 1.0), "tusz")
            with s.cechy(cien=False):
                s.blok("Kocioł żar", (0, 0.55, 0), (3.2, 0.8, 3.2), "neon_ogien", "Neon", rot=(0, 20, 0))
            s.walec("Kocioł", (0, 4.0, 0), 4.5, 6.0, "metal_ciemny", os="y")
            s.walec("Kocioł brzuch", (0, 3.6, 0), 5.5, 2.6, "metal_ciemny", os="y")
            s.walec("Kocioł rant", (0, 7.05, 0), 5.0, 0.9, "tusz", os="y")
            s.walec("Kocioł zupa", (0, 7.3, 0), 4.1, 0.6, "pomarancz", os="y")             # wierzch 0,1 nad rantem
            for sx in (-1, 1):
                s.blok("Kocioł ucho", (sx * 5.7, 5.6, 0), (1.0, 1.8, 1.6), "tusz")
            with s.cechy(cien=False):
                s.blok("Kocioł blik", (-1.8, 3.9, 5.25), (0.6, 2.0, 0.3), "biel", rot=(0, -20, 8))
                s.blok("Kocioł blik", (-3.0, 3.5, 4.5), (0.5, 1.0, 0.3), "biel", rot=(0, -36, 8))
            # chochla: trzonek wychodzi z zupy, odchylony o 30° w prawo, z hakiem na końcu
            with s.uklad(pos=(1.0, 1.4, -0.6), obrot=(-8, 0, -39)):
                s.blok("Chochla trzonek", (0, 6.0, 0), (0.8, 12.0, 0.8), "drewno_jasne", "Wood")
                s.blok("Chochla hak", (-0.45, 12.1, 0), (1.6, 0.8, 0.8), "tusz", rot=(0, 0, 30))
            # para: cztery klocki 3 / 4 / 5 / 6 przelewają się przez rant w lewo i lekko w górę (wierzch ≤ 50)
            with s.cechy(cien=False):
                for i, ((dx, dy, dz), d) in enumerate((((-2.2, 9.6, 0.4), 3.0), ((-4.6, 10.6, 0.0), 4.0),
                                                        ((-7.6, 11.3, -0.4), 5.0), ((-11.2, 11.7, -0.6), 6.0))):
                    s.blok("Para", (dx, dy, dz), (d, d * 0.85, d), "biel", rot=(10 * i, 25 + 20 * i, 12 - 8 * i))


# =========================================================================== szyld: pieczony udziec
def _szyld_udziec(s):
    pietro = _Ramy((P1, O1))
    with s.cechy(kolizja=False):
        # wysięgnik z prawego narożnika piętra: belka ku frontowi + zastrzał
        a = pietro((W1 / 2.0 - 0.4, 6.4, D1 / 2.0 - 0.6))
        b = pietro((W1 / 2.0 - 0.2, 6.4, D1 / 2.0 + 5.2))
        c = pietro((W1 / 2.0 - 0.4, 2.0, D1 / 2.0 + 0.2))
        s.belka("Wysięgnik", a, b, 1.0, "tusz", "SmoothPlastic", 1.0)
        s.belka("Wysięgnik zastrzał", c, (b[0] * 0.5 + a[0] * 0.5, b[1] - 0.3, b[2] * 0.5 + a[2] * 0.5), 0.7, "tusz",
                "SmoothPlastic", 0.7)
        s.blok("Wysięgnik gałka", (b[0], b[1], b[2] + 0.2), (1.4, 1.4, 1.4), "zloto", rot=(45, 0, 45))
        poz, ob = (b[0] - 0.8, 15.0, b[2] - 0.2), (10, 28, -12)
        szyld = _Ramy((poz, ob))
        with s.uklad(pos=poz, obrot=ob, skala=SKALA_SZYLDU):
            _udziec(s)
        # łańcuchy z wysięgnika do dwóch punktów na udźcu
        for lok, t in (((-2.8, 2.6, 0.0), 0.35), ((2.6, 0.9, 0.0), 0.9)):
            p = szyld(tuple(v * SKALA_SZYLDU for v in lok))
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - 0.4, a[2] + (b[2] - a[2]) * t)
            with s.cechy(cien=False):
                s.belka("Łańcuch", p, q, 0.35, "metal_ciemny", "SmoothPlastic", 0.35)


def _udziec(s):
    """Pieczony udziec 10 × 5 w płaszczyźnie XY (front +Z): mięso `drewno` ze skórką `drewno_ciemne` (cienki ciemny brzeg
    zamiast „plastra pnia”), kość biel z dwiema gałkami, płetwa tusz w płaszczyźnie środka, jeden sierp-blik
    `drewno_jasne` i dwa kłęby pary. Po krytyce bez pasków przypieczenia (układały się w „Il” / „Gl”)."""
    # płetwa (obrys) — większa o ok. 0,55
    s.walec("Udziec płetwa", (-2.3, 0, 0), 3.05, 0.4, "tusz", os="z")
    s.blok("Udziec płetwa", (0.0, 0, 0), (4.6, 4.3, 0.4), "tusz", rot=(0, 0, 0))
    s.blok("Udziec płetwa", (3.0, 0.1, 0), (3.6, 2.2, 0.4), "tusz", rot=(0, 0, 6))
    s.blok("Udziec płetwa", (4.65, 0.2, 0), (2.7, 3.7, 0.4), "tusz", rot=(0, 0, 6))
    # mięso: tarcza + blok zwężający się ku kości
    s.walec("Udziec skórka", (-2.3, 0, 0), 2.5, 2.2, "drewno_ciemne", os="z")
    s.walec("Udziec mięso", (-2.3, 0.1, 0), 2.25, 2.6, "drewno", os="z")
    s.blok("Udziec mięso", (-0.4, 0, 0), (3.6, 3.8, 2.0), "drewno")
    s.klin("Udziec mięso", (1.9, 0.75, 0), (1.9, 1.3, 1.0), "drewno", rot=(0, -90, 0))
    s.klin("Udziec mięso", (1.9, -0.95, 0), (1.9, 1.0, 1.0), "drewno", rot=(0, -90, 180))
    # kość z gałkami
    s.blok("Udziec kość", (3.2, 0.1, 0), (2.8, 1.2, 1.2), "biel", rot=(0, 0, 6))
    for y in (0.75, -0.55):
        s.walec("Udziec gałka", (4.6, y + 0.1, 0), 0.8, 1.4, "biel", os="z")
    # sierp-blik (z przodu) i para nad udźcem
    with s.cechy(cien=False):
        s.blok("Udziec blik", (-3.0, 1.2, 1.45), (2.6, 0.7, 0.3), "drewno_jasne", rot=(0, 0, 25))
        s.blok("Udziec blik", (-1.7, 1.75, 1.45), (1.0, 0.6, 0.3), "drewno_jasne", rot=(0, 0, -5))
        s.blok("Udziec para", (-2.6, 3.9, 0), (1.2, 1.2, 1.2), "biel", rot=(20, 35, 15))
        s.blok("Udziec para", (-1.3, 5.0, 0.2), (1.2, 1.2, 1.2), "biel", rot=(10, 10, 40))


# =========================================================================== tablica zleceń
def _tablica(s):
    """Tablica zleceń przed lewą częścią fasady: deska 16 × 10 na krzywych słupach, daszek, 3 kartki, kubek kakao."""
    with s.uklad(pos=(-12.0, 0, 13.0), obrot=(0, 12, 0)):
        for x, k in ((-7.4, 5), (7.4, -5)):
            with s.uklad(pos=(x, 0, 0), obrot=(0, 0, k)):
                s.blok("Tablica słup", (0, 7.4, -0.6), (1.0, 14.8, 1.0), "drewno", "Wood")
        with s.cechy(kolizja=False):
            for x in (-7.4, 7.4):
                s.blok("Tablica podstawa", (x * 1.06, 0.3, -0.6), (1.8, 0.6, 1.8), "kamien_cokol")
            with s.uklad(pos=(0, 9.0, 0), obrot=(0, 0, -4)):
                s.blok("Tablica rama", (0, 0, -0.05), (17.6, 11.6, 0.4), "tusz")
                s.blok("Tablica deska", (0, 0, 0.35), (16.0, 10.0, 0.6), "drewno_jasne", "WoodPlanks")
                _kartki(s)
            # daszek dwuspadowy w kolorze kodu
            with s.uklad(pos=(0.0, 14.75, -0.6), obrot=(0, 0, 4)):
                s.blok("Tablica daszek rant", (0, 0, 0), (19.6, 0.4, 4.4), "tusz")
                s.klin("Tablica daszek", (0, 1.05, 1.05), (19.0, 1.7, 2.1), DACH, rot=(0, 180, 0))
                s.klin("Tablica daszek", (0, 1.05, -1.05), (19.0, 1.7, 2.1), cien(s, DACH, 0.85))
                s.blok("Tablica daszek kalenica", (0, 1.95, 0), (19.4, 0.5, 0.8), "tusz")
                _kubek(s, (5.6, 2.2, 0.0))


def _kartki(s):
    """Trzy kartki 3 × 4 na desce (lico deski z = 0,65) z własnymi piktogramami pętli gry (po krytyce: koło, X i trójkąt
    to symbole przycisków cudzej konsoli): biała z mieczem, złota z jajem, błękitna z kluczem; ostatnia wisi krzywo
    na jednej pinezce (25°)."""
    z = 0.65
    with s.cechy(cien=False):
        # 1. biała z mieczem (ostrze, jelec, rękojeść)
        with s.uklad(pos=(-4.6, 0.8, z), obrot=(0, 0, 6)):
            s.blok("Kartka", (0, 0, 0.1), (3.0, 4.0, 0.2), "biel")
            with s.uklad(pos=(0.1, -0.1, 0.25), obrot=(0, 0, -42)):     # ukośnie, ostrzem w górę (nie jak krzyż)
                s.blok("Kartka znak miecz", (0, 0.5, 0), (0.6, 2.4, 0.2), "tusz")
                s.blok("Kartka znak miecz sztych", (0, 1.7, 0), (0.42, 0.42, 0.2), "tusz", rot=(0, 0, 45))
                s.blok("Kartka znak jelec", (0, -0.75, 0.03), (1.8, 0.5, 0.2), "tusz")
                s.blok("Kartka znak rękojeść", (0, -1.3, 0), (0.5, 0.7, 0.2), "drewno_ciemne")
                s.blok("Kartka znak głowica", (0, -1.75, 0.03), (0.6, 0.6, 0.2), "tusz", rot=(0, 0, 45))
            s.blok("Pinezka", (0, 1.6, 0.35), (0.6, 0.6, 0.4), "czerwien")
        # 2. złota z jajem (jajo biel na podkładce tusz)
        with s.uklad(pos=(0.4, -0.6, z), obrot=(0, 0, -5)):
            s.blok("Kartka", (0, 0, 0.1), (3.0, 4.0, 0.2), "zloto")
            # jajo: okrągły dół i spiczasty czubek (kwadrat na rogu), na podkładce tusz, z kropką koloru wylęgarni
            s.walec("Kartka znak jajo obrys", (0, -0.45, 0.25), 1.25, 0.2, "tusz", os="z")
            s.blok("Kartka znak jajo obrys", (0, 0.35, 0.25), (1.75, 1.75, 0.2), "tusz", rot=(0, 0, 45))
            s.walec("Kartka znak jajo", (0, -0.45, 0.45), 1.0, 0.2, "biel", os="z")
            s.blok("Kartka znak jajo", (0, 0.35, 0.45), (1.3, 1.3, 0.2), "biel", rot=(0, 0, 45))
            s.blok("Kartka znak jajo kropka", (0.3, -0.2, 0.6), (0.6, 0.6, 0.2), "dach_wylegarnia")
            s.blok("Pinezka", (-1.0, 1.6, 0.35), (0.6, 0.6, 0.4), "czerwien")
            s.blok("Pinezka", (1.0, 1.6, 0.35), (0.6, 0.6, 0.4), "czerwien")
        # 3. błękitna z kluczem — na jednej pinezce, obrócona o 25°
        with s.uklad(pos=(4.6, 2.6, z), obrot=(0, 0, 25)):
            s.blok("Kartka", (0.9, -1.6, 0.1), (3.0, 4.0, 0.2), "tynk_blekit")
            with s.uklad(pos=(0.9, -1.6, 0.25), obrot=(0, 0, -25)):
                s.walec("Kartka znak klucz", (0, 0.75, 0), 0.7, 0.2, "tusz", os="z")
                s.walec("Kartka znak klucz oczko", (0, 0.75, 0.15), 0.3, 0.2, "tynk_blekit", os="z")
                s.blok("Kartka znak klucz pręt", (0, -0.6, 0), (0.5, 2.2, 0.2), "tusz")
                s.blok("Kartka znak klucz ząb", (0.45, -1.3, 0), (0.6, 0.5, 0.2), "tusz")
            s.blok("Pinezka", (0, 0, 0.35), (0.6, 0.6, 0.4), "czerwien")


def _kubek(s, pos):
    """Parujący kubek kakao na kalenicy daszka (echo, ×1,6): kubek w kolorze dachu z pasem biel, kakao drewno_ciemne,
    przechylony ku rynkowi (widać kakao), ucho „C” z 3 bloków, para z klocków. Po krytyce: biały walec czytał się jak rolka."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(15, -30, -4)):
        s.blok("Kubek podstawka", (0, 0.1, 0), (4.4, 0.4, 4.4), "tusz")
        s.walec("Kubek", (0, 2.0, 0), 1.9, 3.4, DACH, os="y")
        s.walec("Kubek pas", (0, 1.7, 0), 2.0, 0.6, "biel", os="y")
        s.walec("Kubek kakao", (0, 3.68, 0), 1.6, 0.3, "drewno_ciemne", os="y")
        for (bx, by), (sx, sy) in (((2.25, 2.8), (1.3, 0.6)), ((2.6, 1.9), (0.6, 1.8)), ((2.25, 1.0), (1.3, 0.6))):
            s.blok("Kubek ucho", (bx, by, 0), (sx, sy, 0.6), "tusz")
    zestaw.dym(s, (x + 0.6, y + 5.4, z + 0.8), n=3, skala=0.8, dryf=(0.6, 0.0), ksztalt="klocek")


# =========================================================================== otoczenie przy wejściu
def _otoczenie(s, rnd):
    with s.uklad(pos=(0, 0, ZP0), obrot=(0, RY0, 0)):
        F = D0 / 2.0
        zestaw.lawka(s, (14.6, 0, F + 1.6), ry=0, dl=6.0)
        zestaw.kwiaty(s, (-0.8, 0, F + 1.7), ry=-3, kolory=("czerwien", "zloto"))
    # trójka przy prawym narożniku: skrzynia (duża), beczka z jabłkami (średnia), skrzynka (mała)
    zestaw.skrzynia(s, (19.9, 0, 9.4), ry=-14, dl=4.0, a=3.4, przechyl=8)
    zestaw.beczka(s, (20.3, 0, 13.6), "jablka", r=1.6, h=4.0, przechyl=(0, -7))
    zestaw.skrzynia(s, (18.4, 0, 14.8), ry=26, dl=2.4, a=2.2, przechyl=-10, kolor="drewno_jasne")
    # sąg drewna pod lewą ścianą (kuchnia gospody)
    with s.uklad(pos=(-21.0, 0, -4.0), obrot=(0, -4, 0)):
        with s.cechy(kolizja=False):
            s.blok("Sąg podkład", (0, 0.3, 0), (2.6, 0.6, 9.0), "drewno_ciemne")
        for i, (y, dz, k) in enumerate(((1.35, -2.0, 5), (1.35, 2.2, -6), (2.95, 0.2, 7))):
            with s.cechy(kolizja=(i < 2)):
                s.blok("Sąg polana", (0, y, dz), (2.4, 1.5, 4.4), "drewno", "Wood", rot=(k, 0, 0))
        with s.cechy(kolizja=False, cien=False):
            for dz in (-3.2, -0.8, 1.4, 3.4):
                s.blok("Sąg czoło", (1.25, 1.4 + 0.5 * (dz > 0), dz), (0.3, 1.2, 1.2), "drewno_jasne", rot=(45, 0, 0))
