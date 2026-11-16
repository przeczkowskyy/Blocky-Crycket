# -*- coding: utf-8 -*-
"""Mała tablica ogłoszeń z rankingiem serwera (D-085), po premierze z panelem gildii (D-067).

Deska na dwóch krzywych słupach z daszkiem w kolorze gildii (paleta: dach_gildia — tablica przejmie rolę siedziby
gildii), złota korona na szczycie i trzy plakietki podium (złota, srebrna, brązowa) z medalami i kreskami zamiast
imion. Napisów w świecie nie ma (zasada miasteczka) — ranking pokaże SurfaceGui na powierzchni zapisanej w znaczniku
„tablica_ranking” (środek, normalna, rozmiar). E przy tablicy jest opcjonalny (pełny ranking w oknie 2D).
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import wspolne  # noqa: E402

NAZWA = "Tablica"
OBRYS = (8, 4)
WYSOKOSC = 13
BUDZET = 70
KOD = "dach_gildia"


def buduj(s, rnd):
    for x, k in ((-3.3, 4), (3.3, -5)):
        s.blok("Tablica słup", (x, 4.6, 0), (0.9, 9.2, 0.9), "drewno", "Wood", rot=(0, 0, k))
        with s.cechy(kolizja=False):
            s.blok("Tablica podstawa", (x * 1.04, 0.35, 0), (1.8, 0.7, 1.8), "kamien_cokol", "Cobblestone")
    with s.uklad(pos=(0, 5.6, 0.3), obrot=(-4, 0, 2)), s.cechy(kolizja=False):
        s.blok("Tablica rama", (0, 0, 0), (7.2, 5.6, 0.4), "tusz")
        s.blok("Tablica deska", (0, 0, 0.3), (6.5, 4.9, 0.4), "drewno_jasne", "WoodPlanks")
        with s.cechy(cien=False):
            for i, (y, kol, szer) in enumerate(((1.55, "zloto", 5.8), (0.0, "tynk_blekit", 5.3), (-1.55, cien(s, "drewno_jasne", 0.75), 4.8))):
                s.blok("Plakietka", (0, y, 0.55), (szer, 1.2, 0.15), kol)
                s.walec("Medal", (-szer / 2.0 + 0.9, y, 0.7), 0.5, 0.15, kol if i else "dach_karczma", os="z")
                for j in range(2):
                    s.blok("Kreska", (0.4 + j * 1.6 - 0.3 * i, y + 0.05, 0.68), (1.3 - 0.3 * j, 0.35, 0.1), "tusz")
        # daszek w kolorze gildii z jasną kalenicą (ciemny dach — przykazanie 6)
        with s.uklad(pos=(0, 3.1, 0.1)):
            s.klin("Tablica daszek", (0, 0.75, 0.75), (8.0, 1.5, 1.5), KOD, rot=(0, 180, 0))
            s.klin("Tablica daszek", (0, 0.75, -0.75), (8.0, 1.5, 1.5), cien(s, KOD, 0.85))
            s.blok("Tablica daszek kalenica", (0, 1.55, 0), (8.3, 0.45, 0.7), "zloto")
            s.blok("Tablica daszek rant", (0, -0.05, 0), (8.4, 0.25, 3.3), "tusz")
            # korona
            with s.uklad(pos=(0, 2.0, 0), obrot=(0, 0, -7)):
                s.blok("Korona", (0, 0.5, 0), (2.6, 1.0, 1.0), "zloto")
                for x in (-1.0, 0.0, 1.0):
                    s.ostroslup("Korona ząb", (x, 1.0, 0), 0.35, 0.35, 1.0 + 0.3 * (x == 0), "zloto")
                s.blok("Korona klejnot", (0, 0.5, 0.55), (0.45, 0.45, 0.2), "dach_karczma")
    zestaw.choragiewka_duetu(s, (-3.6, 9.1, 0), "rycerz", przechyl=10)
    wspolne.znacznik(s, "tablica", "tablica_ranking", (0, 5.6, 0.85), normalna=(0, 0, 1), rozmiar=[6.4, 4.8],
                     opis="powierzchnia na SurfaceGui z rankingiem serwera (najwyższy poziom, największe zdolności); "
                          "po premierze panel gildii (D-067)")
    wspolne.punkt_e(s, NAZWA, "tablica", (0, 5.0), (0, 4.0, 1.0), typ="tablica", nazwa="Tablica ogłoszeń (ranking)",
                    okno="Pełny ranking / panel gildii (opcjonalnie)", kier=(0, 0, 1))
