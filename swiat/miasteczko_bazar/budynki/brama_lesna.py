# -*- coding: utf-8 -*-
"""Brama Leśna — wschodni koniec bazaru, punkt połączenia z pasem Lasu (D-075: miasteczko jest pierwszym blokiem pasa,
zaraz za nim zaczyna się Las). Dwa krzywe pnie kłaniające się sobie, kłoda-nadproże z kępą liści i żołędziem,
zamknięte wrota z desek z okuciami. Dziś przejście pieszo kończy się na ścianie zamykającej Lasu (jego generator ma
skały i niewidzialną ścianę za Polaną Przybycia), więc wrota są zamknięte, a E przed nimi zabiera do Lasu — czy otworzyć
przejście pieszo, decydują ludzie (PROJEKT.md, wybory).
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import wspolne  # noqa: E402

NAZWA = "BramaLesna"
OBRYS = (24, 6)
WYSOKOSC = 22
BUDZET = 110


def buduj(s, rnd):
    pnie = (("drewno", "drewno_ciemne"))
    for x, seg in ((-9.6, [(6.0, 2.8, -4), (5.0, 2.5, -7), (4.6, 2.2, -12)]), (9.6, [(5.6, 2.8, 5), (5.4, 2.5, 8), (4.0, 2.2, 10)])):
        with s.uklad(pos=(x, 0, 0)):
            zestaw.lamana(s, "Pień", seg, list(pnie), "Wood", start=(0.0, -0.2), glebokosc=2.8)
            with s.cechy(kolizja=False):
                for k in (-1, 1):
                    s.klin("Korzeń", (k * 1.9, 0.7, 0), (2.4, 1.4, 1.6), "drewno_ciemne", rot=(0, -90 * k, 0))
    with s.uklad(pos=(0, 15.2, 0), obrot=(0, 0, 3)):
        s.walec("Kłoda", (0, 0, 0), 1.3, 23.0, "drewno", "Wood", os="x")
        with s.cechy(kolizja=False):
            s.walec("Kłoda słoje", (-11.55, 0, 0), 1.0, 0.2, "drewno_jasne", os="x")
            s.walec("Kłoda słoje", (11.55, 0, 0), 1.0, 0.2, "drewno_jasne", os="x")
            for x, y, a, kol, k in ((-6.5, 2.0, 4.5, "lisc_ciemny", 12), (-2.0, 2.6, 5.5, "lisc", -8), (3.0, 2.3, 5.0, "lisc", 20),
                                    (7.0, 1.9, 4.0, "lisc_ciemny", -15), (0.5, 4.6, 3.6, "lisc_jasny", 35)):
                s.blok("Liście", (x, y, 0), (a, a * 0.75, a * 0.9), kol, rot=(8, k, 6))
            # żołądź-szyld nad wrotami
            with s.uklad(pos=(0.2, -2.4, 1.6), obrot=(0, 0, -10)):
                s.blok("Żołądź", (0, -0.4, 0), (2.4, 2.8, 2.0), "drewno_jasne")
                s.blok("Żołądź czapka", (0, 1.2, 0), (2.9, 1.0, 2.4), "drewno_ciemne")
                s.blok("Żołądź ogonek", (0.2, 2.0, 0), (0.4, 0.9, 0.4), "drewno_ciemne", rot=(0, 0, -20))
    # zamknięte wrota (kolizja) z okuciami i kołatkami
    for sx in (-1, 1):
        with s.uklad(pos=(sx * 3.75, 0, 0), obrot=(0, sx * 2, 0)):
            s.blok("Wrota", (0, 6.2, 0), (7.3, 12.0, 0.8), "drewno", "WoodPlanks")
            with s.cechy(kolizja=False):
                for y in (3.0, 9.2):
                    s.blok("Wrota okucie", (0, y, 0.5), (7.0, 0.7, 0.3), "metal_ciemny")
                s.blok("Wrota listwa", (sx * -3.2, 6.2, 0.5), (0.6, 11.6, 0.3), "drewno_ciemne")
                s.walec("Kołatka", (-sx * 1.2, 6.5, 0.7), 0.6, 0.25, "zloto", os="z")
                s.blok("Wrota liść", (sx * 1.0, 11.4, 0.55), (1.4, 0.5, 0.2), "lisc_jasny", rot=(0, 0, 30 * sx))
    with s.cechy(kolizja=False, cien=False):
        s.blok("Wrota szpara", (0, 6.2, 0.05), (0.3, 11.6, 0.9), "tusz")
    zestaw.choragiewka_duetu(s, (9.0, 16.5, 0), "kot", przechyl=-12)
    wspolne.punkt_e(s, NAZWA, "brama_lesna", (0, 6.0), (0, 4.6, 1.2), typ="las", nazwa="Brama Leśna — do Lasu",
                    cel="pas Lasu: Polana Przybycia (swiat/las_pas, punkt przybycia u 14)", kier=(0, 0, 1))
