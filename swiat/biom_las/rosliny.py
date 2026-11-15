# -*- coding: utf-8 -*-
"""Rodziny roślin biomu Las z klocków (PROJEKT.md rozdz. 8): drzewa, grzyby, krzaki, runo, kulisy.

Każda funkcja buduje w BIEŻĄCYM układzie wywołującego: pos = podstawa na ziemi (x, y, z), ry = obrót wokół pionu.
Zwraca (wysokość, promień korony) — generator używa ich do maski korytarzy i miejsc walki.
Przykazania: zero prostych pni (segmenty 5–12° w kontrze), korona jak czapa (spód ciemny, wierzch jasny), tusz u stopy
pnia i pod kapeluszem, kolizję mają tylko pnie i trzony; liście, kwiaty i drobiazgi są bez kolizji, drobiazgi bez cienia.
Liczba części podana przy każdej funkcji.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402

# zestawy kolorów koron (spód, środek, wierzch) — liście ciemnieją z południa na północ
KORONY = {
    "laka": ("lisc", "lisc_jasny", "lisc_jasny"),
    "kapeluszowo": ("lisc_ciemny", "lisc", "lisc_jasny"),
    "serce": ("lisc_ciemny", "lisc", "lisc_jasny"),
    "ostepy": ("igla", "lisc_ciemny", "lisc"),
    "wawoz": ("lisc_ciemny", "lisc", "lisc_jasny"),
    "korona": ("lisc", "lisc_jasny", "lisc_jasny"),
}


def _kontra(rnd, a, b):
    return rnd.choice((-1, 1)) * rnd.uniform(a, b)


def okraglak(s, rnd, pos, k=1.0, ry=0.0, kolory=KORONY["laka"]):
    """A Okrąglak łąkowy: pień z 2 segmentów (+6…9° / −10…14°), korona z 3 czap, tuszowy pierścień. Wys. ok. 15·k. 6 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, kat = lamana(s, "Pień", [(4.2 * k, 1.7 * k, zn * rnd.uniform(6, 9)), (3.6 * k, 1.3 * k, -zn * rnd.uniform(10, 14))],
                                 "drewno", "Wood", start=(0.0, -0.4))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Pień tusz", (0, 0.1, 0), (2.5 * k, 0.4, 2.5 * k), "tusz")
        with s.cechy(kolizja=False):
            kc = -zn * rnd.uniform(4, 8)                      # kontra korony
            with s.uklad(pos=(xe, ye, 0), obrot=(rnd.uniform(-4, 4), rnd.uniform(0, 90), kc)):
                s.blok("Korona spód", (0.6 * zn * k, 1.6 * k, 0), (10.5 * k, 4.2 * k, 9.5 * k), kolory[0])
                s.blok("Korona", (-0.4 * zn * k, 4.6 * k, 0.4 * k), (8.4 * k, 3.6 * k, 8.0 * k), kolory[1], rot=(0, 25, 0))
                s.blok("Korona wierzch", (0.5 * zn * k, 7.0 * k, -0.3 * k), (5.2 * k, 2.6 * k, 5.0 * k), kolory[2], rot=(0, 50, 0))
    return 15.0 * k, 5.3 * k


def dab(s, rnd, pos, k=1.0, ry=0.0, kolory=KORONY["serce"]):
    """B Krzywy Dąb: pień z 3 segmentów w kontrze, konar w bok, korona z 4 czap. Wys. ok. 21·k. 9 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, kat = lamana(s, "Pień", [(5.0 * k, 2.6 * k, zn * rnd.uniform(7, 10)), (4.4 * k, 2.1 * k, -zn * rnd.uniform(12, 16)),
                                             (3.4 * k, 1.6 * k, zn * rnd.uniform(6, 9))], "drewno", "Wood", start=(0.0, -0.5))
        with s.cechy(kolizja=False):
            s.belka("Konar", (xe * 0.5, ye * 0.62, 0), (xe * 0.5 + zn * 5.5 * k, ye * 0.62 + 3.2 * k, 1.2 * k), 1.1 * k, "drewno", "Wood")
            with s.cechy(cien=False):
                s.blok("Pień tusz", (0, 0.1, 0), (3.6 * k, 0.4, 3.6 * k), "tusz")
            with s.uklad(pos=(xe, ye, 0), obrot=(rnd.uniform(-4, 4), rnd.uniform(0, 90), -zn * rnd.uniform(4, 8))):
                s.blok("Korona spód", (0.8 * zn * k, 1.8 * k, 0), (14.0 * k, 4.6 * k, 12.5 * k), kolory[0])
                s.blok("Korona", (-0.8 * zn * k, 5.2 * k, 0.6 * k), (11.0 * k, 4.0 * k, 10.0 * k), kolory[1], rot=(0, 20, 0))
                s.blok("Korona wierzch", (0.6 * zn * k, 8.0 * k, -0.4 * k), (6.8 * k, 3.0 * k, 6.4 * k), kolory[2], rot=(0, 45, 0))
            s.blok("Korona boczna", (xe * 0.5 + zn * 6.5 * k, ye * 0.62 + 4.6 * k, 1.2 * k), (6.0 * k, 3.6 * k, 5.6 * k), kolory[1],
                   rot=(0, rnd.uniform(0, 90), zn * 8))
    return 21.0 * k, 7.0 * k


def sosna(s, rnd, pos, k=1.0, ry=0.0, ciemna=True):
    """C Sosna stożkowa: pień, trzy piętra igieł skręcone o 45° (dół ciemniejszy), krzywy czubek z klina narożnego.
    Wys. ok. 19·k. 5 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-3, 3), ry, _kontra(rnd, 4, 6))):
        with s.cechy(kolizja=True):
            s.blok("Pień", (0, 2.0 * k - 0.4, 0), (1.7 * k, 4.0 * k + 0.8, 1.7 * k), "drewno_ciemne", "Wood")
        kol = (cien(s, "igla", 0.8), "igla", "lisc_ciemny") if ciemna else (cien(s, "igla", 0.9), "igla", "lisc")
        with s.cechy(kolizja=False):
            for i, (a, h) in enumerate(((10.0, 5.2), (7.6, 4.6), (5.2, 4.0))):
                s.blok("Igły", (0.25 * i * k, (4.0 + 2.6 + 4.1 * i) * k, 0), (a * k, h * k, a * k), kol[i],
                       rot=(0, 45 * i + rnd.uniform(-8, 8), _kontra(rnd, 3, 6)))
            s.naroznik("Czubek", (0.6 * k, 19.0 * k - 2.2 * k, 0), (3.4 * k, 4.4 * k, 3.4 * k), "lisc_ciemny",
                       rot=(0, rnd.uniform(0, 360), 0))
    return 19.0 * k, 5.0 * k


def brzozka(s, rnd, pos, k=1.0, ry=0.0):
    """D Brzózka Korony: biały pień z 2 segmentów z paskami tuszu, jasna korona z 2 czap. Wys. ok. 15·k. 6 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Pień", [(5.5 * k, 1.1 * k, zn * rnd.uniform(5, 8)), (4.5 * k, 0.9 * k, -zn * rnd.uniform(9, 12))],
                               "biel", start=(0.0, -0.3))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Pasek", (-zn * 0.25 * k, 2.6 * k, 0), (1.25 * k, 0.45 * k, 1.25 * k), "tusz", rot=(0, 0, zn * 7))
            s.blok("Pasek", (xe * 0.75, 6.8 * k, 0), (1.05 * k, 0.4 * k, 1.05 * k), "tusz", rot=(0, 0, -zn * 4))
        with s.cechy(kolizja=False):
            with s.uklad(pos=(xe, ye, 0), obrot=(0, rnd.uniform(0, 90), -zn * rnd.uniform(4, 8))):
                s.blok("Korona", (0, 2.0 * k, 0), (7.5 * k, 4.6 * k, 7.0 * k), "lisc")
                s.blok("Korona wierzch", (0.4 * zn * k, 5.0 * k, 0.3 * k), (5.0 * k, 3.0 * k, 4.6 * k), "lisc_jasny", rot=(0, 35, 0))
    return 16.0 * k, 3.8 * k


def grzyb(s, rnd, pos, k=1.0, ry=0.0, kapelusz="czerwien", kropki=True, trzon="tynk_krem"):
    """E Grzyb-olbrzym: trzon (walec) przechylony 6–12°, kapelusz z dwóch walców przekrzywiony w kontrze 10–15°,
    podkładka tuszu pod spodem, 4 białe kropki. Wys. ok. 10·k. 8 części (bez kropek 4)."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    prz = zn * rnd.uniform(6, 12)
    h = 7.0 * k
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.uklad(obrot=(0, 0, prz)):
            with s.cechy(kolizja=True):
                s.walec("Trzon", (0, h / 2.0 - 0.4, 0), 0.9 * k, h + 0.8, trzon, os="y")
            with s.uklad(pos=(0, h, 0), obrot=(rnd.uniform(-5, 5), 0, -zn * rnd.uniform(16, 22))), s.cechy(kolizja=False):
                s.walec("Kapelusz spód", (0, -0.15, 0), 4.6 * k, 0.35, "tusz", os="y")
                s.walec("Kapelusz", (0, 0.75 * k, 0), 4.4 * k, 1.5 * k, kapelusz, os="y")
                s.walec("Kapelusz czubek", (0.3 * k, 1.9 * k, 0), 3.0 * k, 1.2 * k, kapelusz, os="y")
                if kropki:
                    with s.cechy(cien=False):
                        for a in range(4):
                            kat = math.radians(a * 90 + rnd.uniform(-20, 20))
                            r = rnd.uniform(1.6, 3.2) * k
                            s.blok("Kropka", (r * math.cos(kat), (1.55 if r > 2.9 * k else 2.55) * k, r * math.sin(kat)),
                                   (0.9 * k, 0.3, 0.9 * k), "biel", rot=(0, rnd.uniform(0, 90), 0))
    return 10.0 * k, 4.6 * k


def pniak(s, rnd, pos, k=1.0, ry=0.0):
    """F Pniak: walec z jasnym ściętym wierzchem. 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-6, 6), ry, rnd.uniform(-6, 6))):
        s.walec("Pniak", (0, 0.8 * k, 0), 1.7 * k, 2.4 * k, "drewno", "Wood", os="y")
        with s.cechy(kolizja=False, cien=False):
            s.walec("Pniak słoje", (0, 2.05 * k, 0), 1.45 * k, 0.2, "drewno_jasne", os="y")
    return 2.0 * k, 1.7 * k


def kulisa(s, rnd, pos, k=1.0, ry=0.0, kolor="sylweta_1", pien="drewno_ciemne", wys=None):
    """Kulisa (obrzeża, środki połaci): pień z kolizją + jedna wysoka czapa bez kolizji i cienia. 2 części."""
    x, y, z = pos
    h = wys or 20.0 * k
    with s.uklad(pos=(x, y, z), obrot=(0, ry, _kontra(rnd, 4, 8))):
        s.blok("Kulisa pień", (0, h * 0.25 - 0.4, 0), (1.8 * k, h * 0.5 + 0.8, 1.8 * k), pien)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Kulisa korona", (0, h * 0.68, 0), (9.0 * k, h * 0.62, 8.0 * k), kolor, rot=(0, 45, _kontra(rnd, 4, 7)))
    return h, 4.5 * k


def krzak(s, rnd, pos, k=1.0, kolory=("lisc_ciemny", "lisc", "lisc_jasny"), jagoda=None):
    """Krzak: 3 bryły (ciemna, środkowa, jasna) obrócone 15–40°, opcjonalna jagoda. Bez kolizji. 3–4 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), 0)), s.cechy(kolizja=False, cien=False):
        s.blok("Krzak", (0, 1.2 * k, 0), (4.0 * k, 2.6 * k, 3.6 * k), kolory[0], rot=(rnd.uniform(-8, 8), 20, rnd.uniform(-8, 8)))
        s.blok("Krzak", (1.2 * k, 2.0 * k, 0.5 * k), (3.0 * k, 2.2 * k, 2.8 * k), kolory[1], rot=(12, 35, 0))
        with s.cechy(cien=False):
            s.blok("Krzak", (-0.5 * k, 2.8 * k, -0.3 * k), (2.2 * k, 1.8 * k, 2.2 * k), kolory[2], rot=(0, 15, 14))
            if jagoda:
                s.blok("Jagoda", (1.8 * k, 2.6 * k, 1.3 * k), (0.9, 0.9, 0.9), jagoda, rot=(30, 30, 0))


def kwiaty(s, rnd, pos, kolory=("zloto", "biel")):
    """Kępa kwiatów: kępka liści i dwa kwiaty-kostki. Bez kolizji i cienia. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), 0)), s.cechy(kolizja=False, cien=False):
        s.blok("Kępka", (0, 0.45, 0), (2.4, 0.9, 1.8), "lisc_ciemny", rot=(0, 0, 6))
        s.blok("Kwiat", (-0.5, 1.35, 0.2), (0.9, 0.9, 0.9), kolory[0], rot=(15, 30, 10))
        s.blok("Kwiat", (0.7, 1.1, -0.3), (0.8, 0.8, 0.8), kolory[-1], rot=(10, 60, -12))


def paproc(s, rnd, pos, k=1.0):
    """Paproć: dwa liście z klinów w rozkroku. Bez kolizji i cienia. 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(kolizja=False, cien=False):
        s.klin("Paproć", (0, 1.0 * k, 1.1 * k), (1.6 * k, 2.0 * k, 2.6 * k), "lisc", rot=(-18, 0, 0))
        s.klin("Paproć", (0.3, 0.9 * k, -1.1 * k), (1.6 * k, 1.8 * k, 2.4 * k), "lisc_ciemny", rot=(-14, 180, 0))


def jezyna(s, rnd, pos, k=1.0):
    """Kępa jeżyn ≤ 5: dwie bryły pędów `jezyna` i jasny kolec. Kolizja tylko do 1 (płaski spód). 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), _kontra(rnd, 4, 8))), s.cechy(kolizja=False):
        s.blok("Jeżyna", (0, 1.3 * k, 0), (4.4 * k, 2.6 * k, 3.6 * k), "jezyna", rot=(0, 15, 0))
        s.blok("Jeżyna", (0.9 * k, 2.8 * k, 0.4 * k), (2.6 * k, 1.6 * k, 2.4 * k), cien(s, "jezyna", 1.2), rot=(10, 40, 0))
        with s.cechy(cien=False):
            s.naroznik("Kolec", (-1.2 * k, 2.9 * k, 0.6 * k), (0.8, 1.4, 0.8), "jezyna_kolec", rot=(0, 30, 0))


def trzcina(s, rnd, pos):
    """Trzcina: dwa źdźbła z pałką. Bez kolizji i cienia. 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), _kontra(rnd, 4, 10))), s.cechy(kolizja=False, cien=False):
        s.blok("Trzcina", (0, 2.0, 0), (0.35, 4.0, 0.35), "trzcina")
        s.blok("Pałka", (0, 4.2, 0), (0.6, 1.3, 0.6), "drewno")
