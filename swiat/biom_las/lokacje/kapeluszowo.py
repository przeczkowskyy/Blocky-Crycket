# -*- coding: utf-8 -*-
"""Lokacje Kapeluszowa: Kładka z Pnia, Wielki Kapelusz (wioska muchomorników), Krąg Zarodników.
Chatki-grzyby muchomorników stoją w domach stref z04, z05, z14 (stawia je generuj.py z potwory.json)."""
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


def kladka_z_pnia(s, G, rnd, L):
    """Omszały pień przerzucony nad strugą wzdłuż Dróżki Kapeluszowej, z czerwonymi kropkami i grzybkami na boku."""
    x, z = L["x"], L["z"]
    ry = math.degrees(math.atan2(-180 - (-35.4), 180 - 35.4))
    with s.grupa("Kapeluszowo/Lokacje/KladkaZPnia"), s.uklad(pos=(x, 0, z), obrot=(0, ry, 0)):
        s.walec("Kładka pień", (0, 0.6, 0), 2.0, 24.0, "drewno", "Wood", os="z")
        with s.cechy(kolizja=False):
            s.blok("Kładka mech", (0, 2.45, 0), (2.6, 0.4, 20.0), "mech")
            s.walec("Kładka korzenie", (0, 2.0, -12.6), 3.8, 1.2, "drewno_ciemne", os="z")
            s.walec("Kładka słoje", (0, 0.6, 12.1), 1.8, 0.3, "drewno_jasne", os="z")
            with s.cechy(cien=False):
                for i in range(6):
                    zz = -9 + 3.6 * i
                    s.blok("Kropka", (2.0 if i % 2 else -2.0, 1.2, zz), (0.3, 1.0, 1.0), "czerwien")
            for zz, k in ((-5.0, 0.35), (2.0, 0.28), (7.0, 0.32)):
                rosliny.grzyb(s, rnd, (2.4, 0.4, zz), k, rnd.uniform(0, 90))
    G.zajmij(x, z, 10)


def wielki_kapelusz(s, G, rnd, L):
    """Muchomor 45 z kapeluszem przekrzywionym zawadiacko: trzon z trzech segmentów w kontrze, kapelusz r 17 z kropkami;
    wokół trzonu spirala małych kapeluszy-stopni (co 4,5 w górę) aż na kapelusz, gdzie stoi skrzynia ratusza (E)."""
    x, z = L["x"], L["z"]
    with s.grupa("Punkty/WielkiKapelusz"), s.uklad(pos=(x, 0, z)):
        # trzon: trzy walce przechylone w kontrze
        segs = [(14.0, 4.6, 6.0), (13.0, 4.0, -9.0), (11.0, 3.4, 7.0)]
        y0, x0, kat = 0.0, 0.0, 0.0
        for dl, r, k in segs:
            kat += k
            a = math.radians(kat)
            cx, cy = x0 - math.sin(a) * dl / 2.0, y0 + math.cos(a) * dl / 2.0
            s.walec("Trzon", (cx, cy, 0), r, dl + 1.2, "tynk_krem", os="y", rot=(0, 0, kat))
            x0, y0 = x0 - math.sin(a) * dl, y0 + math.cos(a) * dl
        with s.uklad(pos=(x0, y0, 0), obrot=(6, 20, -14)):
            s.walec("Kapelusz spód", (0, -0.2, 0), 17.6, 0.5, "tusz", os="y")
            s.walec("Kapelusz", (0, 1.8, 0), 17.0, 4.0, "czerwien", os="y")
            s.walec("Kapelusz czubek", (1.5, 5.0, 0), 11.5, 3.0, "czerwien", os="y")
            s.walec("Kapelusz szczyt", (2.0, 7.2, 0.5), 6.0, 1.8, "czerwien", os="y")
            with s.cechy(kolizja=False, cien=False):
                for k in range(8):
                    a = math.radians(k * 45 + 10)
                    r = 13.5 if k % 2 else 8.5
                    s.blok("Kropka", (1.0 + r * math.cos(a), 3.95 if r > 11.6 else 6.6, r * math.sin(a)), (3.0, 0.4, 3.0), "biel",
                           rot=(0, k * 23, 0))
            zestaw.skrzynia(s, (2.0, 8.1, 0.5), ry=20, dl=3.2, a=2.6, przechyl=6, kolor="drewno")
            wspolne.punkt_e(s, "Punkty/WielkiKapelusz", (2.0, 8.1, 3.5))
    with s.grupa("Kapeluszowo/Lokacje/WielkiKapelusz"), s.uklad(pos=(x, 0, z)):
        # stopnie: małe kapelusze wokół trzonu (co 4,5 w górę, 40° dalej)
        n = 9
        for i in range(n):
            y = 4.5 * (i + 1)
            a = math.radians(200 + 40 * i)
            r = 7.8 + 12.6 * i / (n - 1)                       # stopnie odchodzą na zewnątrz, żeby ominąć rondo kapelusza
            px, pz = r * math.cos(a) - 0.05 * y, r * math.sin(a)
            s.walec("Stopień-kapelusz", (px, y - 0.6, pz), 2.8, 1.2, "czerwien" if i % 2 else "dach_stajnia", os="y")
            with s.cechy(kolizja=False):
                s.belka("Stopień trzonek", (px * 0.55, y - 2.6, pz * 0.55), (px, y - 1.2, pz), 0.8, "tynk_krem", "SmoothPlastic")
        with s.cechy(kolizja=False):
            for k in range(3):
                a = math.radians(30 + 120 * k)
                wspolne.lampion(s, (13.0 * math.cos(a), 0, 13.0 * math.sin(a)), 5.5, "neon_zarodnik")
    wspolne.ognisko(s, rnd, (-240, 0, 232))
    G.zajmij(x, z, 16)


def krag_zarodnikow(s, G, rnd, L):
    """Idealne koło dziewięciu grzybów wokół omszałego kamienia, w środku mgiełka świecących zarodników (Neon)."""
    x, z = L["x"], L["z"]
    with s.grupa("Kapeluszowo/Lokacje/KragZarodnikow"), s.uklad(pos=(x, 0, z)):
        for k in range(9):
            a = 2 * math.pi * k / 9
            rosliny.grzyb(s, rnd, (12.0 * math.cos(a), 0, 12.0 * math.sin(a)), rnd.uniform(0.7, 0.9), rnd.uniform(0, 360),
                          kapelusz="czerwien" if k % 3 else "dach_sklep")
        skaly.glaz(s, rnd, (0, 0, 0), 1.2, 30, "kamien_cieply", mech=True)
        with s.cechy(kolizja=False, cien=False):
            for k in range(14):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(3, 10)
                s.blok("Zarodnik", (r * math.cos(a), rnd.uniform(1.5, 6.5), r * math.sin(a)), (0.45, 0.45, 0.45), "neon_zarodnik", "Neon",
                       rot=(30, 45, 0))
        wspolne.punkt_e(s, "Kapeluszowo/Lokacje/KragZarodnikow", (0, 0, 6.0))
    G.zajmij(x, z, 18)


LOKACJE = {"kladka_z_pnia": kladka_z_pnia, "wielki_kapelusz": wielki_kapelusz, "krag_zarodnikow": krag_zarodnikow}
