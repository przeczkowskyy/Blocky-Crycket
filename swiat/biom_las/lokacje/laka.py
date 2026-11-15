# -*- coding: utf-8 -*-
"""Lokacje Łąki Galaretek: Brama Pniaków, Oczko Galaretek, Most Rechotek, Przewrócony Wóz, Pagórek Wypadniętego Klocka.

Każda funkcja: f(s, G, rnd, L) — L = lokacja z uklad.json; buduje w układzie lasu (sama ustawia swoje miejsce).
Punkty orientacyjne mają główne bryły w grupie „Punkty/<Nazwa>” (w Studio: ModelStreamingMode = Persistent).
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_TU)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny, skaly  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402


def brama_pniakow(s, G, rnd, L):
    """Dwa olbrzymie pnie kłaniają się sobie nad drogą (jak odźwierni), w miejscu spotkania lampion i chorągiewki duetu;
    obok Kamień Powrotu (E) i ognisko pinu. Brama stoi za plecami gracza w punkcie wejścia — patrzy on na Ukłon."""
    x, z = L["x"], L["z"]
    with s.grupa("Punkty/BramaPniakow"), s.uklad(pos=(x, 0, z), obrot=(0, 0, 0)):
        for zn in (-1, 1):
            with s.uklad(pos=(zn * 16.0, 0, 0), obrot=(0, 0, 0)):
                xe, ye, _ = lamana(s, "Pień bramy", [(9.0, 3.8, zn * 9), (8.0, 3.2, zn * 12), (7.0, 2.6, zn * 16)],
                                   "drewno", "Wood", start=(0.0, -0.6))
                s.blok("Pień bramy korzeń", (zn * 2.4, 0.9, 1.4), (4.0, 2.2, 3.0), "drewno_ciemne", rot=(0, 30 * zn, zn * 20))
                with s.cechy(kolizja=False):
                    s.blok("Czapa", (xe - zn * 1.0, ye + 1.4, 0), (9.0, 4.0, 8.0), "lisc_ciemny", rot=(6, 20 * zn, -zn * 8))
                    s.blok("Czapa", (xe - zn * 0.4, ye + 4.2, 0.4), (6.0, 3.0, 5.4), "lisc", rot=(0, 45, zn * 6))
                    s.blok("Czapa wierzch", (xe, ye + 6.2, -0.3), (3.6, 2.0, 3.4), "lisc_jasny", rot=(0, 15, 0))
    with s.grupa("Laka/Lokacje/BramaPniakow"), s.uklad(pos=(x, 0, z)):
        with s.cechy(kolizja=False):
            s.belka("Lina", (-8.5, 21.0, 0), (0, 20.0, 0), 0.5, "drewno_ciemne", "SmoothPlastic")
            s.belka("Lina", (0, 20.0, 0), (8.5, 21.0, 0), 0.5, "drewno_ciemne", "SmoothPlastic")
            s.blok("Lampion łańcuch", (0, 18.6, 0), (0.3, 2.8, 0.3), "metal_ciemny")
            s.blok("Lampion", (0, 16.2, 0), (1.6, 2.2, 1.6), "neon_okno", "Neon", rot=(0, 45, 0))
            s.blok("Lampion daszek", (0, 17.6, 0), (2.4, 0.5, 2.4), "dach_karczma", rot=(0, 45, 0))
            s.blok("Pnie tusz", (-16, 0.12, 0), (5.0, 0.3, 5.0), "tusz")
            s.blok("Pnie tusz", (16, 0.12, 0), (5.0, 0.3, 5.0), "tusz")
        zestaw.choragiewka_duetu(s, (-11.5, 13.5, 0.8), "rycerz", ry=0, przechyl=-12)
        zestaw.choragiewka_duetu(s, (11.5, 13.5, 0.8), "kot", ry=180, przechyl=-12)
        # Kamień Powrotu (E): głaz z rombem światła — wraca do miasteczka
        skaly.glaz(s, rnd, (22.0, 0, -3.0), 1.3, -30, "kamien_cieply", mech=True)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Kamień Powrotu romb", (21.0, 3.2, -0.8), (1.6, 1.6, 0.4), "neon_portal", "Neon", rot=(0, -30, 45))
        wspolne.punkt_e(s, "Laka/Lokacje/BramaPniakow", (20.0, 0, 1.5))
        wspolne.ognisko(s, rnd, (-22.0, 0, -4.0))
        wspolne.drogowskaz(s, rnd, (24.0, 0, -24.0), [(math.degrees(math.atan2(-200, -400)), "serce"),
                                                       (math.degrees(math.atan2(50, -110)), "laka"),
                                                       (math.degrees(math.atan2(-490, -20)), "kapeluszowo")])
    G.zajmij(x, z, 24)


def oczko_galaretek(s, G, rnd, L):
    """Staw (teren.py) z pomostem od zachodu, przechyloną wędką z galaretowym spławikiem, grzybieniami i kamieniami
    brodu przy ujściu strugi. Pomost niski (≤ 1), więc nie psuje placów walki wokół stawu."""
    cx, cz = 250.0, 300.0
    with s.grupa("Laka/Lokacje/OczkoGalaretek"):
        with s.uklad(pos=(cx, 0, cz), obrot=(0, 90, 0)):       # lokalne +Z = wschód; pomost od zachodu (−Z)
            for i in range(5):
                zz = -31.0 + 3.6 * i
                s.blok("Pomost deska", (0, 0.75, zz), (5.0, 0.4, 3.2), "drewno_jasne" if i % 2 else "drewno", rot=(0, rnd.uniform(-4, 4), 0))
            with s.cechy(kolizja=False):
                for xx in (-2.6, 2.6):
                    for zz in (-31.0, -16.6):
                        s.walec("Pomost pal", (xx, 0.5, zz), 0.35, 1.6, "drewno_ciemne", os="y")
                s.belka("Wędka", (1.6, 1.2, -15.0), (2.6, 5.0, -8.0), 0.3, "drewno_ciemne", "Wood")
                s.blok("Żyłka", (2.6, 2.6, -8.0), (0.1 + 0.15, 4.8, 0.15), "biel")
                s.blok("Spławik", (2.6, 0.45, -8.0), (0.9, 0.9, 0.9), "galareta", rot=(0, 30, 10))
                s.blok("Wiaderko", (-1.4, 1.5, -29.0), (1.4, 1.2, 1.4), "dach_twierdza", rot=(0, 20, 0))
        with s.cechy(kolizja=False, cien=False):
            for k in range(7):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(6, 21)
                px, pz = cx + r * math.cos(a), cz + r * math.sin(a)
                if px < cx - 8 and abs(pz - cz) < 5:
                    continue
                s.walec("Grzybień", (px, 0.32, pz), rnd.uniform(1.2, 1.9), 0.15, "lisc", os="y")
                if k % 3 == 0:
                    s.blok("Grzybień kwiat", (px + 0.4, 0.6, pz), (0.7, 0.5, 0.7), "biel", rot=(0, 45, 0))
        # kamienie brodu na ujściu strugi
        for i, (px, pz) in enumerate(((210, 282), (214, 278), (218.5, 275), (222, 271))):
            with s.uklad(pos=(px, 0, pz), obrot=(0, 30 * i, rnd.uniform(-5, 5))):
                s.blok("Kamień brodu", (0, 0.35, 0), (3.0, 0.7, 2.6), "kamien_cieply")
    G.zajmij(cx, cz, 30)


def most_rechotek(s, G, rnd, L):
    """Garbaty most (deska w górę, płasko, w dół) z poręczami i kamienna żaba wielkości chatki z otwartym pyskiem."""
    x, z = L["x"], L["z"]
    ry = math.degrees(math.atan2(-37, -61))                     # oś mostu wzdłuż Szlaku Ukłonu
    with s.grupa("Laka/Lokacje/MostRechotek"), s.uklad(pos=(x, 0, z), obrot=(0, ry, 0)):
        for z0, z1, y0, y1 in ((-12, -4, 0.3, 2.6), (-4, 4, 2.6, 2.6), (4, 12, 2.6, 0.3)):
            dl = math.hypot(z1 - z0, y1 - y0)
            rx = -math.degrees(math.atan2(y1 - y0, z1 - z0))
            s.blok("Most pomost", (0, (y0 + y1) / 2.0 - 0.3, (z0 + z1) / 2.0), (11.0, 0.6, dl + 0.3), "drewno_jasne", "WoodPlanks",
                   rot=(rx, 0, 0))
        with s.cechy(kolizja=False):
            for zn in (-1, 1):
                s.klin("Most łuk", (zn * 5.0, 1.0, -6.0), (1.2, 2.4, 6.0), "kamien_cieply", rot=(0, 180, 0))
                s.klin("Most łuk", (zn * 5.0, 1.0, 6.0), (1.2, 2.4, 6.0), "kamien_cieply")
                for zz, yy in ((-11, 1.3), (-4, 3.4), (4, 3.4), (11, 1.3)):
                    s.blok("Most słupek", (zn * 5.4, yy + 0.8, zz), (0.6, 1.8, 0.6), "drewno_ciemne")
                s.belka("Most poręcz", (zn * 5.4, 2.4, -11), (zn * 5.4, 4.5, -4), 0.4, "drewno", "Wood")
                s.belka("Most poręcz", (zn * 5.4, 4.5, -4), (zn * 5.4, 4.5, 4), 0.4, "drewno", "Wood")
                s.belka("Most poręcz", (zn * 5.4, 4.5, 4), (zn * 5.4, 2.4, 11), 0.4, "drewno", "Wood")
    # żaba z głazów: przysiadła na brzegu, pysk otwarty ku ścieżce
    fx, fz = 40.0, 232.0
    fry = math.degrees(math.atan2(110 - fx, 262 - fz))
    with s.grupa("Laka/Lokacje/MostRechotek/Zaba"), s.uklad(pos=(fx, 0, fz), obrot=(0, fry, 0)):
        s.blok("Żaba", (0, 2.6, -0.5), (8.0, 5.4, 7.5), "dach_gildia", rot=(-8, 0, 3))
        s.blok("Żaba brzuch", (0, 1.8, 3.0), (6.0, 3.4, 1.2), "lisc_jasny", rot=(-8, 0, 0))
        for zn in (-1, 1):
            s.blok("Żaba łapa", (zn * 4.2, 1.0, 1.0), (2.6, 2.0, 5.0), "dach_gildia", rot=(0, zn * 12, 0))
            with s.cechy(kolizja=False):
                s.blok("Żaba oko", (zn * 2.4, 6.9, 1.6), (2.4, 2.4, 2.4), "biel", rot=(0, zn * 10, 0))
                s.blok("Żaba źrenica", (zn * 2.4, 6.9, 2.85), (1.0, 1.4, 0.3), "tusz")
        with s.cechy(kolizja=False):
            s.blok("Żaba pysk", (0, 4.2, 3.4), (6.2, 1.2, 0.6), "czerwien")
            s.blok("Żaba warga", (0, 5.0, 3.5), (6.8, 0.5, 0.6), "tusz")
            s.blok("Żaba język", (0, 3.6, 4.4), (1.4, 0.4, 2.4), "czerwien", rot=(-15, 0, 0))
    G.zajmij(x, z, 14)
    G.zajmij(fx, fz, 8)


def przewrocony_woz(s, G, rnd, L):
    """Wóz handlarza na boku, koło oparte o burtę, rozsypane skrzynie, z piasty koła wyrasta słonecznik. Miejsce zadań (E)."""
    x, z = L["x"], L["z"]
    with s.grupa("Laka/Lokacje/PrzewroconyWoz"), s.uklad(pos=(x, 0, z), obrot=(0, 25, 0)):
        with s.uklad(pos=(0, 0, 0), obrot=(0, 0, 78)):
            s.blok("Wóz skrzynia", (2.6, -0.4, 0), (5.0, 0.6, 11.0), "drewno", "WoodPlanks")
            s.blok("Wóz burta", (0.2, 2.2, 0), (0.6, 5.2, 11.0), "drewno_jasne", "WoodPlanks")
            s.blok("Wóz burta", (4.9, 2.2, 0), (0.6, 5.2, 11.0), "drewno_jasne", "WoodPlanks")
            s.blok("Wóz dyszel", (2.6, -1.0, 8.5), (0.6, 0.6, 7.0), "drewno_ciemne")
        with s.cechy(kolizja=False):
            s.walec("Koło", (-1.0, 2.4, -3.5), 2.4, 0.6, "drewno_ciemne", os="x", rot=(0, 0, 0))
            s.walec("Koło piasta", (-1.4, 2.4, -3.5), 0.7, 0.9, "metal_ciemny", os="x")
            s.walec("Koło", (6.0, 0.3, 4.0), 2.4, 0.6, "drewno_ciemne", os="y")
            s.belka("Słonecznik łodyga", (6.0, 0.6, 4.0), (5.4, 6.0, 4.4), 0.4, "lisc_ciemny", "SmoothPlastic")
            s.walec("Słonecznik", (5.3, 6.3, 4.6), 1.6, 0.4, "zloto", os="z", rot=(-15, 0, 0))
            s.walec("Słonecznik środek", (5.3, 6.3, 4.85), 0.8, 0.3, "drewno_ciemne", os="z", rot=(-15, 0, 0))
        zestaw.skrzynia(s, (4.5, 0, -7.0), ry=30, dl=3.0, a=2.6, przechyl=14)
        zestaw.skrzynia(s, (-5.0, 0, 3.0), ry=-20, dl=2.6, a=2.2, przechyl=-10)
        with s.cechy(kolizja=False, cien=False):
            for i in range(5):
                s.blok("Jabłko", (rnd.uniform(-6, 7), 0.45, rnd.uniform(-9, 9)), (0.8, 0.8, 0.8), "czerwien", rot=(20, 40 * i, 10))
        wspolne.punkt_e(s, "Laka/Lokacje/PrzewroconyWoz", (0, 0, 8.0))
    G.zajmij(x, z, 13)


def pagorek_klocka(s, G, rnd, L):
    """Wielki złoty klocek 12 × 6 × 6 wbity w szczyt pagórka pod kątem 25°, z dwiema wypustkami; obok strzałka w niebo."""
    x, z = L["x"], L["z"]
    y = 6.0
    with s.grupa("Punkty/PagorekKlocka"), s.uklad(pos=(x, y, z), obrot=(0, -35, 25)):
        s.blok("Złoty klocek", (0, 1.4, 0), (12.0, 6.0, 6.0), "zloto")
        for xx in (-3.0, 3.0):
            s.walec("Klocek wypustka", (xx, 4.9, 0), 1.6, 1.2, "zloto", os="y")
        with s.cechy(kolizja=False):
            s.blok("Klocek cień", (0, 1.4, 3.05), (12.1, 6.05, 0.2), cien(s, "zloto", 0.82))
    with s.grupa("Laka/Lokacje/PagorekKlocka"), s.uklad(pos=(x, y, z)):
        with s.cechy(kolizja=False):
            s.blok("Strzałka", (-7.0, 6.0, 5.0), (0.8, 12.0, 0.8), "czerwien", rot=(0, 0, -8))
            s.naroznik("Strzałka grot", (-7.85, 13.1, 5.0), (2.4, 2.6, 2.4), "czerwien", rot=(0, 45, -8))
            s.walec("Krater", (2.0, 0.08, 0.0), 6.5, 0.2, "ziemia", os="y")
        for k in range(4):
            a = rnd.uniform(0, 2 * math.pi)
            skaly.kanciak(s, rnd, (7.5 * math.cos(a), 0, 7.5 * math.sin(a)), rnd.uniform(0.6, 1.0), rnd.uniform(0, 360), "zloto")
    G.zajmij(x, z, 12)


LOKACJE = {"brama_pniakow": brama_pniakow, "oczko_galaretek": oczko_galaretek, "most_rechotek": most_rechotek,
           "przewrocony_woz": przewrocony_woz, "pagorek_klocka": pagorek_klocka}
