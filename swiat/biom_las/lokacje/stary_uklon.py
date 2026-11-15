# -*- coding: utf-8 -*-
"""Stary Ukłon — dominanta lasu (95 nad polaną) i Bocianie Gniazdo w czubku.

Pień z trzech segmentów pochylony razem 12° na wschód (+X) z kontrą w górnym, korzenie-ławki wokół stopy, spirala
konarów-stopni (co 5 w górę, na zewnątrz pnia) przez rdzawo-miodową czapę na jej wierzch, gdzie leży gniazdo z belek
ze złotym jajem-klockiem. Złote owoce-klocki pod czapą, świetliki (Neon) w koronie.
Pień i czapa to „Punkty/StaryUklon” (stale wczytane); konary, korzenie i drobiazgi w „Serce/Lokacje/StaryUklon”.

    python swiat/biblioteka/podglad.py --modul swiat/biom_las/lokacje/stary_uklon.py --wyj <folder>
"""
import math
import os
import random
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_TU)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402

NAZWA = "StaryUklon"
OBRYS = (90.0, 90.0)
SEG = [(30.0, 12.0, -7.0), (28.0, 9.5, -9.0), (24.0, 7.5, 5.0)]      # (długość, grubość, kąt°): ujemny = góra na wschód (+X)


def os_pnia():
    """Punkty osi pnia [(x, y), …] od stopy do czubka (w płaszczyźnie XY)."""
    pts = [(0.0, 0.0)]
    x, y, kat = 0.0, 0.0, 0.0
    for dl, g, k in SEG:
        kat += k
        a = math.radians(kat)
        x, y = x - math.sin(a) * dl, y + math.cos(a) * dl
        pts.append((x, y))
    return pts


def srodek_na(y):
    pts = os_pnia()
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return x0 + t * (x1 - x0), SEG[min(2, pts.index((x0, y0)))][1] / 2.0
    return pts[-1][0], SEG[-1][1] / 2.0


def buduj(s, rnd, grupa_punktu="Punkty/StaryUklon", grupa="Serce/Lokacje/StaryUklon", ognisko=True):
    from swiat.krzywe_miasteczko.zestaw import lamana
    with s.grupa(grupa_punktu):
        xe, ye, _ = lamana(s, "Pień Ukłonu", SEG, ["drewno", "drewno_ciemne", "drewno"], "Wood", start=(0.0, -1.0))
        with s.uklad(pos=(xe, ye - 6.0, 0), obrot=(0, 0, 4)), s.cechy(kolizja=False):
            s.blok("Czapa spód", (0, 4.0, 0), (58.0, 12.0, 52.0), "lisc_rdza")
            # zwisające kępy na obwodzie: łamią płaski spód czapy (z dołu nie wygląda jak stół)
            for k in range(7):
                a = math.radians(k * 360 / 7 + 12)
                r = 27.0 + 3.0 * (k % 2)
                s.blok("Czapa kępa", (r * math.cos(a), 1.0 + 2.5 * (k % 3), r * math.sin(a)), (19.0, 11.0, 16.0),
                       "lisc_rdza" if k % 2 else "lisc_rudy", rot=(rnd.uniform(-8, 8), -math.degrees(a) + rnd.uniform(-20, 20), rnd.uniform(-8, 8)))
            s.blok("Czapa", (-3.0, 13.5, 2.0), (50.0, 11.0, 46.0), "lisc_rudy", rot=(0, 18, 0))
            for k in range(4):
                a = math.radians(k * 90 + 40)
                s.blok("Czapa kępa", (19.0 * math.cos(a), 15.5, 19.0 * math.sin(a)), (16.0, 9.0, 14.0),
                       "lisc_miodowy" if k % 2 else "lisc_rudy", rot=(0, k * 31, rnd.uniform(-6, 6)))
            with s.cechy(kolizja=True):                        # wierzch czapy nosi Bocianie Gniazdo
                s.blok("Czapa wierzch", (-1.0, 19.5, -1.0), (34.0, 7.0, 30.0), "lisc_miodowy", rot=(0, 40, 0))
            s.blok("Czapa czubek", (8.0, 24.0, 6.0), (10.0, 3.0, 9.0), "lisc_miodowy", rot=(0, 10, 0))
            # Bocianie Gniazdo na wierzchu czapy
            with s.uklad(pos=(-7.0, 23.0, -5.0)):
                with s.cechy(kolizja=True):
                    s.walec("Gniazdo dno", (0, 0.4, 0), 5.0, 0.8, "drewno", os="y")
                for k in range(6):
                    a = math.radians(k * 60)
                    s.belka("Gniazdo belka", (5.0 * math.cos(a), 1.0, 5.0 * math.sin(a)),
                            (5.0 * math.cos(a + 1.05), 1.8, 5.0 * math.sin(a + 1.05)), 1.0, "drewno_jasne", "Wood")
                s.blok("Złote jajo", (0.5, 2.6, 0), (2.6, 3.4, 2.6), "zloto", rot=(8, 20, 6))
                s.walec("Jajo wypustka", (0.5, 4.5, 0), 0.6, 0.5, "zloto", os="y")
    with s.grupa(grupa):
        # korzenie-ławki (siedzisko ok. 2,5)
        for k in range(7):
            a = math.radians(k * 360 / 7 + 15)
            r0, r1 = 5.0, rnd.uniform(18, 23)
            with s.uklad(pos=((r0 + r1) / 2.0 * math.cos(a), 0, (r0 + r1) / 2.0 * math.sin(a)),
                         obrot=(0, math.degrees(math.atan2(math.cos(a), math.sin(a))), 0)):
                s.blok("Korzeń", (0, 1.2, 0), (4.2, 3.4, r1 - r0), "drewno_ciemne", "Wood", rot=(-6, 0, rnd.choice((-5, 5))))
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Korzeń wierzch", (0, 2.95, 0), (3.2, 0.2, r1 - r0 - 2.0), "drewno_jasne", rot=(-6, 0, 0))
        # po przeglądzie: dolny segment pnia był prostym blokiem — stopa z czterech przypór (kliny) i pasy kory
        for k in range(4):
            a = k * 90
            with s.uklad(obrot=(0, a, 0)):
                s.klin("Przypora", (0, 5.0, 8.4), (6.0, 11.0, 5.4), "drewno_ciemne", "Wood", rot=(0, 180, 0))
        with s.cechy(kolizja=False):
            s.blok("Stopa", (0.4, 2.5, 0), (14.5, 5.0, 14.5), "drewno_ciemne", "Wood", rot=(0, 45, 0))
            for k, (dx, dz, h) in enumerate(((6.1, -2.5, 16.0), (6.1, 2.8, 11.0), (-6.1, 1.0, 14.0), (1.5, 6.1, 13.0), (-2.0, -6.1, 15.0))):
                s.blok("Kora", (dx + 0.122 * (6.0 + h / 2.0), 6.0 + h / 2.0, dz), (1.0 if abs(dx) > 5 else 2.2, h, 2.2 if abs(dx) > 5 else 1.0),
                       "drewno_ciemne" if k % 2 else cien(s, "drewno", 0.8), "Wood", rot=(0, 0, -7))
        with s.cechy(kolizja=False, cien=False):
            s.walec("Pień tusz", (0, 0.1, 0), 11.0, 0.3, "tusz", os="y")
        # spirala konarów-stopni: co 5 w górę, 38° dalej, coraz dalej od osi; ostatnie wychodzą poza czapę
        n = 19
        for i in range(n):
            y = 5.0 * (i + 1)
            cx, pol = srodek_na(min(y, 80.0))
            a = math.radians(60 + 38 * i)
            r = pol + 3.5 + (max(0, y - 55) * 0.5)          # w koronie stopnie odchodzą od osi, ostatni obok wierzchu czapy
            px, pz = cx + r * math.cos(a), r * math.sin(a)
            s.blok("Konar-stopień", (px, y - 0.7, pz), (6.5, 1.4, 4.4), "drewno", "Wood",
                   rot=(0, -math.degrees(a) + 90, rnd.uniform(-4, 4)))
            with s.cechy(kolizja=False):
                s.belka("Konar", (cx + pol * 0.6 * math.cos(a), y - 4.0, pol * 0.6 * math.sin(a)), (px, y - 1.2, pz), 1.4, "drewno_ciemne", "Wood")
        # złote owoce-klocki i świetliki
        with s.cechy(kolizja=False, cien=False):
            for k in range(8):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(14, 28)
                s.blok("Owoc", (srodek_na(70)[0] + r * math.cos(a), 63.0 + rnd.uniform(-1, 1), r * math.sin(a)), (1.6, 1.6, 1.6), "zloto",
                       rot=(20, rnd.uniform(0, 90), 10))
            for k in range(10):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(20, 36)
                s.blok("Świetlik", (srodek_na(70)[0] + r * math.cos(a), rnd.uniform(58, 80), r * math.sin(a)), (0.5, 0.5, 0.5),
                       "neon_swietlik", "Neon")
        if ognisko:
            wspolne.ognisko(s, rnd, (-14.0, 0, 60.0))


def stary_uklon(s, G, rnd, L):
    y = G.T.H(L["x"], L["z"])
    with s.uklad(pos=(L["x"], y, L["z"])):
        buduj(s, rnd, ognisko=False)
    wspolne.ognisko(s, rnd, (-14.0, G.T.H(-14, 60), 60.0))
    G.zajmij(L["x"], L["z"], 24)


LOKACJE = {"stary_uklon": stary_uklon}

if __name__ == "__main__":
    from swiat.biblioteka.scena import Scena
    from swiat.biom_las.paleta import PALETA
    sc = Scena("Workspace/Podglad", PALETA)
    buduj(sc, random.Random(7))
    print(len(sc.czesci), sc.statystyki()["zakres"])
