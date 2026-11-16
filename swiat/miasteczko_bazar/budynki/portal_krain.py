# -*- coding: utf-8 -*-
"""Portal do krain — po lewej ręce gracza stojącego na starcie (D-085: „portal do biomów, np. po lewej”).

Dwa krzywe kamienne filary pochylone ku sobie, krzywe nadproże z dwuspadowym daszkiem w kolorze „brama” (paleta:
dach_brama — kod wyjścia do krain z dzisiejszej bramy miejskiej), złoty zwornik i trzy żetony krain na daszku
(drzewko = Las, kryształ, płomień — zapowiedź dalszych biomów z D-061). Między filarami wir: świecący dysk Neon
z białym pierścieniem i złotymi ramionami. Przed portalem dwa stopnie i drogowskaz z trzema strzałkami bez napisów.
E przed portalem → przejście przez chmury i wybór krainy (D-075; dziś Las — Polana Przybycia).
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import wspolne  # noqa: E402

NAZWA = "PortalKrain"
OBRYS = (22, 12)
WYSOKOSC = 26
BUDZET = 170
KOD, WIR = "dach_brama", "neon_slime"
KAMIEN = "kamien_cieply"


def buduj(s, rnd):
    # stopnie (≤ 0,5 każdy)
    s.blok("Stopień", (0, 0.25, 0.5), (20.0, 0.5, 11.0), "kamien_cokol", "Cobblestone")
    s.blok("Stopień", (0, 0.75, -0.8), (16.0, 0.5, 7.6), "bruk_ciemny")
    with s.cechy(kolizja=False, cien=False):
        s.blok("Stopień rant", (0, 1.04, 2.96), (16.2, 0.12, 0.25), "tusz")
    # filary: lewy ku prawej, prawy ku lewej (kontra), kamienie na przemian jasne i cień
    kam = [KAMIEN, cien(s, KAMIEN, 0.85)]
    for x, seg in ((-7.2, [(5.4, 3.3, -3), (5.2, 3.1, -6), (4.8, 2.9, -5)]),
                   (7.2, [(5.0, 3.3, 4), (5.6, 3.1, 5), (4.6, 2.9, 7)])):
        with s.uklad(pos=(x, 1.0, -0.8)):
            s.blok("Filar cokół", (0, 0.6, 0), (4.4, 1.2, 4.4), "kamien_cokol", "Cobblestone")
            zestaw.lamana(s, "Filar", seg, kam, start=(0.0, 1.0), glebokosc=3.4)
    # nadproże z daszkiem, zwornik, żetony krain
    with s.uklad(pos=(0.3, 17.4, -0.8), obrot=(0, 0, -4)):
        s.blok("Nadproże", (0, 0, 0), (19.0, 2.8, 4.2), KAMIEN)
        with s.cechy(kolizja=False):
            s.blok("Nadproże rant", (0, -1.55, 0), (19.4, 0.5, 4.6), "tusz")
            s.klin("Daszek", (0, 2.6, 1.15), (20.4, 2.4, 2.3), KOD, rot=(0, 180, 0))
            s.klin("Daszek", (0, 2.6, -1.15), (20.4, 2.4, 2.3), cien(s, KOD, 0.85))
            s.blok("Daszek kalenica", (0, 3.85, 0), (20.8, 0.6, 0.9), "tusz")
            s.blok("Daszek rant", (0, 1.3, 0), (20.9, 0.35, 5.0), "tusz")
            s.klin("Zwornik", (0, -0.4, 2.3), (2.6, 2.6, 0.6), "zloto", rot=(180, 0, 0))
            # żetony krain na kalenicy: drzewko, kryształ, płomień
            s.blok("Żeton drzewko pień", (-6.0, 4.6, 0), (0.6, 1.2, 0.6), "drewno")
            s.blok("Żeton drzewko", (-6.0, 5.9, 0), (2.0, 2.0, 2.0), "lisc", rot=(0, 30, 12))
            s.ostroslup("Żeton kryształ", (0.0, 4.1, 0), 0.9, 0.9, 3.0, "dach_sklep")
            with s.cechy(cien=False):
                s.blok("Żeton płomień", (6.0, 5.0, 0), (1.5, 1.8, 1.5), "neon_ogien", "Neon", rot=(0, 45, 0))
                s.ostroslup("Żeton płomień", (6.0, 5.85, 0), 0.6, 0.6, 1.6, "zloto")
    # wir portalu (bez kolizji — gracz wchodzi w niego albo klika E)
    with s.uklad(pos=(0, 8.6, -0.8)), s.cechy(kolizja=False):
        s.walec("Wir podkład", (0, 0, -0.35), 6.1, 0.3, "tusz", os="z")
        with s.cechy(cien=False):
            s.walec("Wir", (0, 0, 0), 5.6, 0.4, WIR, "Neon", os="z")
            s.walec("Wir pierścień", (0, 0, 0.25), 3.9, 0.15, "biel", os="z")
            s.walec("Wir środek", (0, 0, 0.35), 2.4, 0.15, WIR, "Neon", os="z")
            s.walec("Wir oko", (0, 0, 0.45), 0.9, 0.15, "biel", os="z")
            for i in range(4):
                a = math.radians(30 + 90 * i)
                s.blok("Wir ramię", (3.2 * math.cos(a), 3.2 * math.sin(a), 0.4), (2.6, 0.5, 0.15), "zloto",
                       rot=(0, 0, math.degrees(a) + 65))
    # drogowskaz z trzema strzałkami (bez liter) po prawej przed portalem
    with s.uklad(pos=(9.6, 0.5, 4.6), obrot=(0, -18, 3)):
        s.blok("Drogowskaz słup", (0, 3.5, 0), (0.7, 7.0, 0.7), "drewno", "Wood")
        with s.cechy(kolizja=False):
            for i, (y, kier, kol) in enumerate(((6.0, 1, "lisc"), (4.9, -1, "woda_gleboka"), (3.8, 1, "zloto"))):
                with s.uklad(pos=(kier * 1.6, y, 0.45), obrot=(0, 0, (6, -8, 4)[i])):
                    s.blok("Strzałka", (0, 0, 0), (3.0, 0.9, 0.3), "drewno_jasne", "WoodPlanks")
                    s.klin("Strzałka grot", (kier * 1.95, 0, 0), (0.3, 1.3, 1.0), kol, rot=(0, 90 * kier, 90))
                    s.blok("Strzałka kolor", (-kier * 0.6, 0, 0.18), (1.2, 0.5, 0.1), kol)
    wspolne.punkt_e(s, NAZWA, "portal_krain", (0, 7.5), (0, 4.8, 2.0), typ="portal", nazwa="Portal do krain",
                    cel="przejście przez chmury → wybór krainy (D-075); dziś: Las — Polana Przybycia",
                    kier=(0, 0, 1))
    wspolne.znacznik(s, "portal_srodek", "portal_krain_wir", (0, 8.6, -0.8), kier=(0, 0, 1), promien=5.6,
                     opis="środek wiru (strefa wejścia, jeśli portal ma działać przez dotyk)")
    zestaw.wypadniety_klocek(s, (-7.2, 3.0, 1.0), (-9.4, 0.5, 4.2), KAMIEN)
