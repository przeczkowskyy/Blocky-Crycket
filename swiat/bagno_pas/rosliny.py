# -*- coding: utf-8 -*-
"""Rodziny roślin Bagna z klocków (nowe; rodziny lasu bierzemy z swiat/biom_las/rosliny.py bez zmian).

Te same przykazania co w lesie (swiat/biom_las/rosliny.py): zero prostych pni (segmenty w kontrze), korona jak czapa
(spód ciemny, wierzch jasny), tuszowy pierścień u stopy (tu na tafli wody), kolizję mają tylko pnie. Różnica Bagna to
sylwetki: cypryśnik z rozszerzoną stopą, „kolanami” i płaską koroną z brodą mchu, wierzba płacząca z zasłoną zwisów,
korzeniak na szczudłach korzeni, kępy wysokiej trzciny, liście grzybieni, błędne ogniki.

Każda funkcja buduje w BIEŻĄCYM układzie wywołującego: pos = podstawa na ziemi, ry = obrót wokół pionu. Zwraca
(wysokość, promień korony). Liczba części przy funkcji.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny as rosliny_lasu  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402

odcien = rosliny_lasu.odcien
Y_TUSZ = 0.24                        # pierścień u stopy leży na tafli wody (0,2)


def _kontra(rnd, a, b):
    return rnd.choice((-1, 1)) * rnd.uniform(a, b)


def cyprys(s, rnd, pos, k=1.0, ry=0.0, f=1.0):
    """Cypryśnik: szeroka stopa (walec), pień z 2 segmentów w kontrze, płaska korona z 3 cienkich czap, pasmo mchu
    zwisające spod korony, jedno „kolano” wystające z wody. Wys. ok. 24·k. 9 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            s.walec("Pień", (0, 1.0 * k, 0), 2.3 * k, 2.4 * k, "bagno_kora", "Wood", os="y")
            xe, ye, _ = lamana(s, "Pień", [(8.0 * k, 1.9 * k, zn * rnd.uniform(4, 7)), (8.0 * k, 1.3 * k, -zn * rnd.uniform(8, 12))],
                               "bagno_kora", "Wood", start=(0.0, 1.8 * k))
        with s.cechy(kolizja=False, cien=False):
            s.walec("Pień tusz", (0, Y_TUSZ, 0), 2.4 * k, 0.08, "tusz", os="y")
        with s.cechy(kolizja=False):
            kor = (odcien(s, cien(s, "bagno_korona", 0.82), f), odcien(s, "bagno_korona", f), odcien(s, "bagno_korona_jasna", f))
            with s.uklad(pos=(xe, ye, 0), obrot=(rnd.uniform(-3, 3), rnd.uniform(0, 90), -zn * rnd.uniform(3, 6))):
                s.blok("Korona spód", (0, 0.1 * k, 0), (14.0 * k, 1.1 * k, 12.0 * k), kor[0])
                s.blok("Korona", (0.8 * zn * k, 1.2 * k, 0.4 * k), (10.0 * k, 1.0 * k, 8.6 * k), kor[1], rot=(0, 30, 0))
                s.blok("Korona wierzch", (-0.5 * zn * k, 2.2 * k, -0.3 * k), (5.6 * k, 0.9 * k, 5.2 * k), kor[2], rot=(0, 55, 0))
                s.blok("Mech zwis", (zn * 4.4 * k, -3.0 * k, zn * 2.4 * k), (0.8 * k, 5.6 * k, 1.8 * k), "bagno_broda",
                       rot=(0, rnd.uniform(0, 90), zn * 4))
            a = math.radians(rnd.uniform(0, 360))
            s.klin("Korzeń", (3.0 * k * math.cos(a), 0.7 * k, 3.0 * k * math.sin(a)), (1.1 * k, 1.6 * k, 1.1 * k), "bagno_kora",
                   "Wood", rot=(0, rnd.uniform(0, 360), 0))
    return 24.0 * k, 6.5 * k


def wierzba(s, rnd, pos, k=1.0, ry=0.0, f=1.0):
    """Wierzba płacząca: gruby krzywy pień z 2 segmentów, okrągła korona z 2 czap i dwie zasłony zwisów do połowy
    wysokości. Wys. ok. 15·k. 7 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Pień", [(4.2 * k, 2.2 * k, zn * rnd.uniform(8, 12)), (3.4 * k, 1.6 * k, -zn * rnd.uniform(14, 18))],
                               "drewno_ciemne", "Wood", start=(0.0, -0.4))
        with s.cechy(kolizja=False, cien=False):
            s.walec("Pień tusz", (0, Y_TUSZ, 0), 1.8 * k, 0.08, "tusz", os="y")
        with s.cechy(kolizja=False):
            with s.uklad(pos=(xe, ye, 0), obrot=(0, rnd.uniform(0, 90), -zn * rnd.uniform(3, 7))):
                s.blok("Korona spód", (0, 1.4 * k, 0), (11.0 * k, 3.6 * k, 10.0 * k), odcien(s, cien(s, "bagno_wierzba", 0.78), f))
                s.blok("Korona wierzch", (0.4 * zn * k, 4.0 * k, 0.2 * k), (7.4 * k, 2.8 * k, 7.0 * k), odcien(s, "bagno_wierzba", f),
                       rot=(0, 35, 0))
                for i in range(2):
                    a = math.radians(120 * i + 60 + rnd.uniform(-20, 20))
                    s.blok("Korona zwis", (4.4 * k * math.cos(a), -2.4 * k, 4.4 * k * math.sin(a)), (4.2 * k, 6.4 * k, 0.6 * k),
                           odcien(s, "bagno_wierzba", f * 0.92), rot=(0, -math.degrees(a) + 90, rnd.uniform(-4, 4)))
    return 15.0 * k, 5.6 * k


def korzeniak(s, rnd, pos, k=1.0, ry=0.0, f=1.0):
    """Korzeniak (drzewo na szczudłach): pień uniesiony na czterech ukośnych korzeniach, krótki pień w kontrze, ciemna
    korona z 2 czap. Wys. ok. 13·k. 8 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    h0 = 3.0 * k
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=False):
            for i in range(4):
                a = math.radians(90 * i + 45 + rnd.uniform(-12, 12))
                s.belka("Korzeń", (2.8 * k * math.cos(a), -0.2, 2.8 * k * math.sin(a)), (0.2 * math.cos(a), h0 + 0.3, 0.2 * math.sin(a)),
                        0.55 * k, "bagno_kora", "Wood")
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Pień", [(4.6 * k, 1.2 * k, zn * rnd.uniform(6, 10)), (3.2 * k, 0.9 * k, -zn * rnd.uniform(10, 16))],
                               "bagno_kora", "Wood", start=(0.0, h0))
        with s.cechy(kolizja=False):
            with s.uklad(pos=(xe, ye, 0), obrot=(0, rnd.uniform(0, 90), -zn * rnd.uniform(3, 6))):
                s.blok("Korona spód", (0, 0.9 * k, 0), (8.0 * k, 2.6 * k, 7.6 * k), odcien(s, cien(s, "bagno_korona", 0.75), f))
                s.blok("Korona wierzch", (0.3 * zn * k, 2.8 * k, 0), (5.2 * k, 2.0 * k, 5.0 * k), odcien(s, "bagno_korona_jasna", f),
                       rot=(0, 40, 0))
    return 13.0 * k, 4.2 * k


def suchy_omszaly(s, rnd, pos, k=1.0, ry=0.0):
    """Suche drzewo lasu (rosliny.suchy) z brodą mchu na konarze. 6–7 części."""
    h, r = rosliny_lasu.suchy(s, rnd, pos, k, ry)
    x, y, z = pos
    with s.cechy(kolizja=False), s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.blok("Mech zwis", (rnd.uniform(-1.5, 1.5) * k, 9.0 * k, rnd.uniform(-1.0, 1.0) * k), (0.8 * k, 3.6 * k, 1.3 * k),
               "bagno_sylweta_2", rot=(0, rnd.uniform(0, 90), 0))
    return h, r


def kepa_trzciny(s, rnd, pos, wys=5.0, szer=4.0, pelna=True):
    """Gęsta kępa wysokiej trzciny i pałek (bez kolizji): płaskie snopy w ochrze i zieleni skręcone względem siebie
    + kolby. pelna: 3 snopy + 2 kolby (5 części), inaczej 2 + 1 (3 części, skraj kulis)."""
    x, y, z = pos
    kolory = ("bagno_trzcina", "trzcina", cien(s, "bagno_trzcina", 0.82)) if pelna else (rnd.choice(("bagno_trzcina", "trzcina")),
                                                                                        cien(s, "bagno_trzcina", 0.82))
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(kolizja=False):
        for i, kol in enumerate(kolory):
            h = wys * rnd.uniform(0.75, 1.0)
            s.blok("Trzcina", (rnd.uniform(-0.8, 0.8), h / 2.0, (i - 1) * szer * 0.28), (szer * rnd.uniform(0.6, 0.9), h, 0.5),
                   kol, rot=(rnd.uniform(-6, 6), 30 * i + 45 * (not pelna) + rnd.uniform(-10, 10), rnd.uniform(-7, 7)))
        for q in ((-1, 1) if pelna else (rnd.choice((-1, 1)),)):
            h = wys * rnd.uniform(0.85, 1.08)
            s.blok("Pałka", (q * szer * 0.25, h, rnd.uniform(-0.6, 0.6)), (0.6, 1.5, 0.6), "bagno_palka", rot=(0, 0, q * 6))


def grzybien(s, rnd, pos, r=1.0, kwiat=None):
    """Liść grzybienia (lilii wodnej) na tafli, opcjonalny kwiat. Bez kolizji i cienia. 1–2 części."""
    x, y, z = pos
    with s.cechy(kolizja=False, cien=False):
        s.walec("Lilia", (x, y + 0.03, z), r, 0.08, rnd.choice(("lisc", "lisc_ciemny", "bagno_trawa_jasna")), os="y")
        if kwiat:
            s.blok("Lilia kwiat", (x + 0.2 * r, y + 0.25, z), (0.7 * r, 0.4, 0.7 * r), kwiat, rot=(0, 45, 0))


def ognik(s, pos, d=0.7):
    """Błędny ognik: mała świecąca kostka (Neon), bez kolizji i cienia. 1 część."""
    with s.cechy(kolizja=False, cien=False):
        s.blok("Świetlik", pos, (d, d, d), "neon_ognik", "Neon", rot=(35, 45, 0))
