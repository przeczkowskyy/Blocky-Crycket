# -*- coding: utf-8 -*-
"""Zagroda petów — miejsce, gdzie gracz odstawia pety, które zwykle chodzą za bohaterem (D-085; pety z kanonu: pies,
slime, smok). Otwarty wybieg za płotkiem z bramką na uliczkę, budka opiekunki z daszkiem w kolorze petów, legowiska,
miski, koryto i siano. Opiekunka stoi przy korycie (E → okno zagrody, okno w HUD robi Paweł). Sześć miejsc na odstawione
pety zapisuje się w znacznikach. Jajek tu nie ma: jajka są w inkubatorach biomów (D-060), w Lesie przy przybyciu.
Szyld: wielka łapa nad bramką.
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402

NAZWA = "ZagrodaPetow"
OBRYS = (26, 20)
WYSOKOSC = 17
BUDZET = 330
KOD = "dach_wylegarnia"
Y_WYBIEGU = 0.2
OPIEKUNKA = (2.5, -5.4)
MIEJSCA = ((-9.5, -1.5), (-9.0, 6.0), (-5.0, 7.0), (6.5, 7.0), (10.0, 2.0), (9.5, -4.5))   # odstawione pety


def buduj(s, rnd):
    W, D = OBRYS
    # wybieg: ziemia + kępy trawy (płaskie, bez kolizji ponad grunt)
    s.blok("Wybieg", (0, (Y_WYBIEGU - 0.15) / 2.0, 0), (W - 0.4, Y_WYBIEGU + 0.15, D - 0.4), "ziemia")
    with s.cechy(kolizja=False, cien=False):
        for x, z, a, b, k in ((-7.5, 2.0, 7.0, 5.0, 10), (7.0, 4.0, 6.0, 4.5, -14), (-2.0, 7.5, 5.0, 2.6, 4),
                              (8.5, -6.0, 5.0, 3.5, 20)):
            s.blok("Łata trawy", (x, Y_WYBIEGU + 0.05, z), (a, 0.1, b), "trawa", rot=(0, k, 0))
    # płotek (do przeskoczenia, 3) z bramką 10 na środku frontu
    zestaw.plot(s, [(-W / 2.0 + 0.5, D / 2.0 - 0.6), (-5.0, D / 2.0 - 0.6)], rnd)
    zestaw.plot(s, [(5.0, D / 2.0 - 0.6), (W / 2.0 - 0.5, D / 2.0 - 0.6)], rnd)
    zestaw.plot(s, [(-W / 2.0 + 0.5, D / 2.0 - 0.6), (-W / 2.0 + 0.5, -D / 2.0 + 0.5)], rnd)
    zestaw.plot(s, [(W / 2.0 - 0.5, D / 2.0 - 0.6), (W / 2.0 - 0.5, -D / 2.0 + 0.5)], rnd)
    zestaw.plot(s, [(-W / 2.0 + 0.5, -D / 2.0 + 0.5), (W / 2.0 - 0.5, -D / 2.0 + 0.5)], rnd, wys=3.4)
    _bramka(s)
    _budka(s)
    # opiekunka przy korycie
    ox, oz = OPIEKUNKA
    s.blok("Koryto", (ox + 3.6, 1.0, oz + 0.6), (4.2, 1.6, 1.8), "drewno", "WoodPlanks")
    with s.cechy(kolizja=False, cien=False):
        s.blok("Koryto woda", (ox + 3.6, 1.75, oz + 0.6), (3.6, 0.15, 1.3), "woda")
    postacie.postac(s, "opiekunka", NAZWA + "/Opiekunka", (ox, Y_WYBIEGU, oz), ry=-12)
    wspolne.punkt_e(s, NAZWA, "zagroda_petow", (ox - 0.5, oz + 5.6), (ox, Y_WYBIEGU + 4.6, oz + 0.6), typ="zagroda",
                    sklep="zagroda_petow", nazwa="Zagroda petów (opiekunka)", okno="Okno zagrody petów (Paweł)",
                    postac="opiekunka", model=NAZWA + "/Opiekunka", kier=(0, 0, 1))
    # pety z kanonu i ich legowiska, miski, siano
    postacie.pies(s, NAZWA + "/Pety/Pies", (-6.8, Y_WYBIEGU, 2.4), ry=40)
    postacie.slime(s, NAZWA + "/Pety/Slime", (7.2, Y_WYBIEGU, 4.6), ry=-30)
    postacie.smok(s, NAZWA + "/Pety/Smok", (8.6, Y_WYBIEGU, -2.4), ry=-70)
    with s.cechy(kolizja=False):
        for x, z, kol in ((-9.0, 6.0, "dach_kolo"), (10.0, 2.0, "dach_twierdza"), (9.5, -4.5, "pomarancz")):
            s.walec("Legowisko", (x, Y_WYBIEGU + 0.25, z), 1.7, 0.5, kol, "Fabric", os="y")
            s.walec("Legowisko rant", (x, Y_WYBIEGU + 0.45, z), 1.9, 0.3, cien(s, kol, 0.8), "Fabric", os="y")
        for x, z in ((-4.2, 6.6), (4.4, 6.8)):
            s.walec("Miska", (x, Y_WYBIEGU + 0.35, z), 0.9, 0.7, KOD, os="y")
            s.blok("Kość", (x + 0.1, Y_WYBIEGU + 0.8, z), (1.3, 0.3, 0.3), "biel", rot=(0, 35, 0))
    for i, (x, z, k) in enumerate(((10.4, -8.0, 8), (8.2, -8.2, -6))):
        s.blok("Siano", (x, Y_WYBIEGU + 1.0, z), (2.4, 2.0, 1.8), "dach_stajnia", rot=(0, k, 0))
    with s.cechy(kolizja=False):
        s.blok("Siano", (9.3, Y_WYBIEGU + 2.6, -8.1), (2.2, 1.6, 1.6), cien(s, "dach_stajnia", 0.9), rot=(0, 3, 6))
    for i, (x, z) in enumerate(MIEJSCA):
        wspolne.znacznik(s, "miejsce_peta", "zagroda_miejsce_%d" % (i + 1), (x, Y_WYBIEGU, z),
                         opis="miejsce na odstawionego peta (Zagroda petów)")
    zestaw.wypadniety_klocek(s, (-W / 2.0 + 2.5, 1.6, D / 2.0 - 0.3), (-W / 2.0 + 3.0, 0, D / 2.0 + 0.9), "biel")


def _lapa(s):
    """Wielka łapa (szyld) w płaszczyźnie XY: poduszka i cztery palce w pomarańczu przechodzą przez płetwę tuszem, więc
    łapę widać z obu stron (jak szyld dzisiejszej wylęgarni). Bez liter."""
    s.walec("Łapa obrys", (0, -1.0, -0.3), 2.9, 0.4, "tusz", os="z")
    s.walec("Łapa poduszka", (0, -1.0, -0.3), 2.5, 1.4, "pomarancz", os="z")
    for a in (-55, -20, 20, 55):
        r = math.radians(a)
        p = (3.2 * math.sin(r), -1.0 + 3.3 * math.cos(r))
        s.walec("Łapa obrys", (p[0], p[1], -0.3), 1.3, 0.4, "tusz", os="z")
        s.walec("Łapa palec", (p[0], p[1], -0.3), 0.95, 1.4, "pomarancz", os="z")


def _bramka(s):
    """Dwa słupki bramki, krzywa poprzeczka i łapa-szyld nad przejściem 10 (prześwit 9)."""
    z = OBRYS[1] / 2.0 - 0.6
    for x, k in ((-5.4, 4), (5.4, -5)):
        s.blok("Słupek bramki", (x, 4.6, z), (0.9, 9.2, 0.9), "drewno", "Wood", rot=(0, 0, k))
    with s.cechy(kolizja=False):
        s.blok("Poprzeczka", (0, 9.4, z), (12.4, 0.9, 1.0), "drewno_ciemne", "Wood", rot=(0, 0, -3))
        with s.uklad(pos=(0.4, 12.6, z + 0.2), obrot=(-6, 0, 9)):
            _lapa(s)
        zestaw.choragiewka_duetu(s, (-5.8, 9.4, z), "kot", przechyl=-12)


def _budka(s):
    """Budka opiekunki w lewym tyle: biała, z dachem w kolorze petów, okienkiem i psią budą obok."""
    with s.uklad(pos=(-6.0, 0, -6.4), obrot=(0, 4, 0)):
        s.blok("Budka", (0, 3.6, 0), (9.0, 7.2, 5.6), "biel")
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * 4.3, 3.7, sz * 2.6), (0.9, 7.0, 0.9), "tusz")
            s.blok("Cokół", (0, 0.5, 0), (9.4, 1.0, 6.0), "kamien_cokol", "Cobblestone")
        zestaw.okno(s, (1.6, 4.6, 2.8), 3.0, 2.6, przechyl=5, swiatlo="neon_slime", okiennica=KOD, strona_okiennicy=1)
        zestaw.drzwi(s, (-2.4, 0, 2.95), 3.0, 5.4, kolor=KOD, nadproze=None, tanie=True)
        with s.uklad(pos=(0, 7.2, 0), obrot=(0, 0, -6)):
            zestaw.dach_czapa(s, 9.0, 5.6, 4.6, KOD, okap=1.4, okap_bok=1.0, podzial=0.58, szczyt="biel")
            with s.cechy(kolizja=False):
                postacie.slime(s, NAZWA + "/Pety/SlimeNaDachu", (2.2, 4.1, -0.4), ry=20, skala=0.7)
    # psia buda przy płocie
    with s.uklad(pos=(-10.6, 0, 1.4), obrot=(0, 76, 0)):
        s.blok("Buda", (0, 1.6, 0), (3.6, 3.2, 3.4), "drewno", "WoodPlanks")
        with s.cechy(kolizja=False):
            s.blok("Buda otwór", (0, 1.3, 1.65), (1.6, 2.0, 0.2), "tusz")
            s.klin("Buda dach", (0, 3.9, 0.95), (4.2, 1.6, 2.2), "dach_karczma", rot=(0, 180, 0))
            s.klin("Buda dach", (0, 3.9, -0.95), (4.2, 1.6, 2.2), cien(s, "dach_karczma", 0.85))
