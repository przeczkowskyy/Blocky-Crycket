# -*- coding: utf-8 -*-
"""Karczma — „Gospoda Pod Pękatym Kotłem” (mapa v2 „Krzywe Miasteczko”, karta PROJEKT.md 5.1).

Dominanta miasteczka: pękaty parter 38 × 22 (pionowy, skręt −4°), nawisające piętro 41 × 25 przechylone w lewo (rz +6°,
skręt +4°), wielka czerwona czapa dachu w kontrze (rz −4°, połacie ok. 46° i 57°). Żart: komin-kocioł z chochlą i parą
na tylnej połaci po lewej. Szyld: pieczony udziec na wysięgniku z prawego narożnika. Przed fasadą po lewej tablica zleceń
z trzema kartkami (koło, X, trójkąt) i parującym kubkiem kakao na daszku (echo). Bez alkoholu i bez liter.

Konwencja: (0, 0, 0) = środek działki 46 × 38 na wierzchu podium, front z drzwiami ku +Z. Podium, schody i latarnie
stawia generator. Status: propozycja (noc 13.11.2026), nie kanon.

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/karczma.py --wyj <folder> --szer 1000
"""
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
DY_KOTLA = -1.5                                                  # obniżenie kotła (wierzch pary ≤ 50)


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
            info = zestaw.dach_czapa(s, W1, D1, DACH_WYS, DACH, okap=DACH_OKAP, okap_bok=DACH_BOK, podzial=DACH_PODZIAL,
                                     szczyt=SCIANA)
            _dach_detale(s, info)
            # okienka w szczytach (ciemna szyba) — boki nie są gołe
            xs = W1 / 2.0 + DACH_BOK + 0.3
            zestaw.okno(s, (xs, 6.4, info["z_kalenicy"] + 0.6), 2.6, 3.2, przechyl=-7, ry=90, swiatlo="woda_gleboka", tanie=True)
            zestaw.okno(s, (-xs, 5.6, info["z_kalenicy"] - 0.4), 3.0, 2.6, przechyl=6, ry=-90, swiatlo="woda_gleboka", tanie=True)
            zestaw.lata(s, (-xs, 10.6, info["z_kalenicy"] + 1.2), 2.2, 1.8, "dach_twierdza", ry=-90, przechyl=14)
            _kociol(s, info)


def _na_polaci(s, info, x, t, przod=True):
    """Układ na połaci: t = 0 okap, 1 kalenica; lokalne +Y = normalna połaci; zwraca (pos, obrot)."""
    zr, H = info["z_kalenicy"], DACH_WYS
    if przod:
        z0 = D1 / 2.0 + DACH_OKAP
        z = z0 + (zr - z0) * t
        kat = math.degrees(math.atan2(H, z0 - zr))
        return (x, H * t, z), (kat, 0, 0)
    z0 = -D1 / 2.0 - DACH_OKAP
    z = z0 + (zr - z0) * t
    kat = math.degrees(math.atan2(H, zr - z0))
    return (x, H * t, z), (-kat, 0, 0)


def _dach_detale(s, info):
    """Rzędy dachówek (cień), odstające dachówki, lukarna z okrągłym oknem, chorągiewka duetu na kalenicy."""
    with s.cechy(kolizja=False):
        ciemny = cien(s, DACH, 0.86)
        for t, x0, x1 in ((0.30, -22.5, 4.0), (0.33, 4.6, 22.5), (0.62, -22.5, -6.0), (0.58, 9.5, 22.5)):
            pos, ob = _na_polaci(s, info, (x0 + x1) / 2.0, t)
            with s.uklad(pos=pos, obrot=ob):
                s.blok("Rząd dachówek", (0, 0.12, 0), (x1 - x0, 0.45, 1.0), ciemny)
        for x, t, k in ((-14.0, 0.45, 18), (15.5, 0.75, -24)):
            pos, ob = _na_polaci(s, info, x, t)
            with s.uklad(pos=pos, obrot=ob):
                s.blok("Odstająca dachówka", (0, 0.35, 0), (2.4, 0.4, 1.8), DACH, rot=(-14, k, 6))
        # tylna połać: dwa rzędy i łata
        for t, x0, x1 in ((0.35, -22.5, -2.0), (0.4, 3.0, 22.5)):
            pos, ob = _na_polaci(s, info, (x0 + x1) / 2.0, t, przod=False)
            with s.uklad(pos=pos, obrot=ob):
                s.blok("Rząd dachówek", (0, 0.12, 0), (x1 - x0, 0.45, 1.0), cien(s, DACH, 0.72))
        pos, ob = _na_polaci(s, info, 12.0, 0.6, przod=False)
        with s.uklad(pos=pos, obrot=ob):
            with s.uklad(obrot=(-90, 0, 0)):
                zestaw.lata(s, (0, 0, 0.05), 3.0, 2.6, "zloto", przechyl=12)
    # lukarna na połaci frontowej, po prawej od osi
    zr = info["z_kalenicy"]
    zf = D1 / 2.0 + DACH_OKAP
    kat = math.atan2(DACH_WYS, zf - zr)
    xl, zl = 7.0, 9.0                                         # przód lukarny
    yl = DACH_WYS * (zf - zl) / (zf - zr)                       # wysokość połaci w przodzie lukarny
    with s.uklad(pos=(xl, 0, zl), obrot=(0, -6, 0)):
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
    zestaw.choragiewka_duetu(s, (17.0, DACH_WYS + 0.3, zr), "kot", przechyl=-12)


def _kociol(s, info):
    """Komin-kocioł: ceglany cokół z połaci, kocioł Ø 9 × 7 (metal_ciemny, rant tusz) przechylony o 10°, żar pod dnem,
    chochla 12 pod 30° i para Ø 3/4/5. Wszystko w układzie dachu (rz −4° bezwzględnie)."""
    xk, zk = -14.0, -7.2
    with s.cechy(kolizja=False):
        s.blok("Kocioł cokół", (xk, 11.6 + DY_KOTLA / 2.0, zk + 0.4), (5.4, 7.0 + DY_KOTLA, 5.4), "kamien_cokol", "Brick", rot=(0, 8, 5))
        s.blok("Kocioł podstawa", (xk + 0.2, 15.0 + DY_KOTLA, zk + 0.4), (6.6, 0.6, 6.6), "tusz", rot=(0, 8, 5))
        with s.uklad(pos=(xk + 0.4, 15.25 + DY_KOTLA, zk + 0.4), obrot=(7, 0, 13)):
            for kat in (30, 150, 270):
                a = math.radians(kat)
                s.blok("Kocioł nóżka", (2.4 * math.cos(a), 0.55, 2.4 * math.sin(a)), (1.0, 1.4, 1.0), "tusz")
            with s.cechy(cien=False):
                s.blok("Kocioł żar", (0, 0.55, 0), (3.2, 0.8, 3.2), "neon_ogien", "Neon", rot=(0, 20, 0))
            s.walec("Kocioł", (0, 4.0, 0), 4.5, 6.0, "metal_ciemny", os="y")
            s.walec("Kocioł brzuch", (0, 3.6, 0), 4.85, 2.6, "metal_ciemny", os="y")
            s.walec("Kocioł rant", (0, 7.05, 0), 5.0, 0.9, "tusz", os="y")
            s.walec("Kocioł zupa", (0, 7.3, 0), 4.1, 0.6, "pomarancz", os="y")             # wierzch 0,1 nad rantem
            for sx in (-1, 1):
                s.blok("Kocioł ucho", (sx * 5.05, 5.6, 0), (1.0, 1.8, 1.6), "tusz")
            with s.cechy(cien=False):
                s.blok("Kocioł blik", (-1.6, 4.4, 4.7), (0.6, 2.6, 0.3), "biel", rot=(0, -20, 8))
                s.blok("Kocioł blik", (-2.8, 3.9, 3.95), (0.5, 1.2, 0.3), "biel", rot=(0, -36, 8))
            # chochla: trzonek wychodzi z zupy, odchylony o 30° w prawo, z hakiem na końcu
            with s.uklad(pos=(1.0, 1.4, -0.6), obrot=(-8, 0, -39)):
                s.blok("Chochla trzonek", (0, 6.0, 0), (0.8, 12.0, 0.8), "drewno_jasne", "Wood")
                s.blok("Chochla hak", (-0.45, 12.1, 0), (1.6, 0.8, 0.8), "tusz", rot=(0, 0, 30))
        # para: trzy kłęby Ø 3 / 4 / 5 przelewają się przez rant w lewo i w górę (wierzch ≤ 50)
        with s.cechy(cien=False):
            for (dx, dy, dz), d in (((-3.0, 23.0, 0.6), 3.0), ((-5.2, 23.9, 0.0), 4.0), ((-7.6, 24.4, -0.8), 5.0)):
                s.kula("Para", (xk + dx, dy + DY_KOTLA, zk + dz), d, "biel")


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
    """Pieczony udziec 10 × 5 w płaszczyźnie XY (front +Z): mięso drewno_jasne z przypieczeniem, kość biel z dwiema
    gałkami, płetwa tusz w płaszczyźnie środka (obrys z przodu i z tyłu). 20 części."""
    # płetwa (obrys) — większa o ok. 0,55
    s.walec("Udziec płetwa", (-2.3, 0, 0), 3.05, 0.4, "tusz", os="z")
    s.blok("Udziec płetwa", (0.0, 0, 0), (4.6, 4.3, 0.4), "tusz", rot=(0, 0, 0))
    s.blok("Udziec płetwa", (3.0, 0.1, 0), (3.6, 2.2, 0.4), "tusz", rot=(0, 0, 6))
    s.blok("Udziec płetwa", (4.65, 0.2, 0), (2.7, 3.7, 0.4), "tusz", rot=(0, 0, 6))
    # mięso: tarcza + blok zwężający się ku kości
    s.walec("Udziec skórka", (-2.3, 0, 0), 2.5, 2.2, "drewno", os="z")
    s.walec("Udziec mięso", (-2.3, 0.1, 0), 1.95, 2.6, "drewno_jasne", os="z")
    s.blok("Udziec mięso", (-0.4, 0, 0), (3.6, 3.8, 2.0), "drewno_jasne")
    s.klin("Udziec mięso", (1.9, 0.75, 0), (1.9, 1.3, 1.0), "drewno_jasne", rot=(0, -90, 0))
    s.klin("Udziec mięso", (1.9, -0.95, 0), (1.9, 1.0, 1.0), "drewno_jasne", rot=(0, -90, 180))
    # kość z gałkami
    s.blok("Udziec kość", (3.2, 0.1, 0), (2.8, 1.2, 1.2), "biel", rot=(0, 0, 6))
    for y in (0.75, -0.55):
        s.walec("Udziec gałka", (4.6, y + 0.1, 0), 0.8, 1.4, "biel", os="z")
    # przypieczenie i blik (z przodu i z tyłu)
    with s.cechy(cien=False):
        for zn in (1, -1):
            for x, y, k, z in ((-3.1, 0.3, 35, 1.42), (-1.6, -0.3, 35, 1.42), (0.5, 0.8, 35, 1.15)):
                s.blok("Udziec przypieczenie", (x, y, zn * z), (0.5, 2.0 if z > 1.3 else 2.4, 0.3), "drewno", rot=(0, 0, k))
        s.blok("Udziec blik", (-3.0, 1.35, 1.45), (1.2, 0.45, 0.3), "biel", rot=(0, 0, 20))


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
    """Trzy kartki 3 × 4 na desce (lico deski z = 0,65): biel z kołem, zloto z X, tynk_blekit z trójkątem;
    ostatnia wisi krzywo na jednej pinezce (25°)."""
    z = 0.65
    with s.cechy(cien=False):
        # 1. biała z kołem
        with s.uklad(pos=(-4.6, 0.8, z), obrot=(0, 0, 6)):
            s.blok("Kartka", (0, 0, 0.1), (3.0, 4.0, 0.2), "biel")
            s.walec("Kartka znak koło", (0, 0.3, 0.25), 0.85, 0.2, "tusz", os="z")
            s.blok("Pinezka", (0, 1.6, 0.35), (0.6, 0.6, 0.4), "czerwien")
        # 2. złota z X
        with s.uklad(pos=(0.4, -0.6, z), obrot=(0, 0, -5)):
            s.blok("Kartka", (0, 0, 0.1), (3.0, 4.0, 0.2), "zloto")
            for k in (45, -45):
                s.blok("Kartka znak X", (0, 0.1, 0.25 + 0.03 * (k > 0)), (0.5, 2.4, 0.2), "tusz", rot=(0, 0, k))
            s.blok("Pinezka", (-1.0, 1.6, 0.35), (0.6, 0.6, 0.4), "czerwien")
            s.blok("Pinezka", (1.0, 1.6, 0.35), (0.6, 0.6, 0.4), "czerwien")
        # 3. błękitna z trójkątem — na jednej pinezce, obrócona o 25°
        with s.uklad(pos=(4.6, 2.6, z), obrot=(0, 0, 25)):
            s.blok("Kartka", (0.9, -1.6, 0.1), (3.0, 4.0, 0.2), "tynk_blekit")
            s.klin("Kartka znak trójkąt", (0.4, -1.75, 0.25), (0.2, 1.8, 1.0), "tusz", rot=(0, 90, 0))
            s.klin("Kartka znak trójkąt", (1.4, -1.75, 0.25), (0.2, 1.8, 1.0), "tusz", rot=(0, -90, 0))
            s.blok("Pinezka", (0, 0, 0.35), (0.6, 0.6, 0.4), "czerwien")


def _kubek(s, pos):
    """Parujący kubek kakao na kalenicy daszka (echo): kubek biel z pasem dach_karczma, kakao drewno_ciemne, ucho, para."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, 20, -4)):
        s.blok("Kubek podstawka", (0, 0.1, 0), (2.8, 0.4, 2.8), "tusz")
        s.walec("Kubek", (0, 1.6, 0), 1.2, 2.6, "biel", os="y")
        s.walec("Kubek kakao", (0, 2.85, 0), 1.0, 0.3, "drewno_ciemne", os="y")
        s.blok("Kubek ucho", (1.55, 1.7, 0), (0.7, 1.6, 0.5), "tusz")
    zestaw.dym(s, (x + 0.2, y + 4.2, z), n=2, skala=0.55, dryf=(0.6, 0.0), ksztalt="klocek")


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
