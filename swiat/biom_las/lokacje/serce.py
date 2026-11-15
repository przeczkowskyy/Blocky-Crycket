# -*- coding: utf-8 -*-
"""Lokacje Serca Boru (strefa spokoju): Gniazdo w Korzeniach (inkubatory petów), Dziupla Turniejowa (walki petów),
Korzenna Gardziel (loch z kłódką), lampiony polany. Stary Ukłon: stary_uklon.py."""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_TU)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402


def _ku(x, z, cel=(0.0, 0.0)):
    return math.degrees(math.atan2(cel[0] - x, cel[1] - z))


def gniazdo_w_korzeniach(s, G, rnd, L):
    """Dwa wielkie jaja w gniazdach z korzeni: zielone w liście i brązowe w kropki, ze świecącym kapslem; przed każdym
    wolny plac 8 × 8 i punkt E (inkubator, D-060)."""
    x, z = L["x"], L["z"]
    y = G.T.H(x, z)
    with s.grupa("Serce/Lokacje/GniazdoWKorzeniach"), s.uklad(pos=(x, y, z), obrot=(0, _ku(x, z), 0)):
        for zn, (kol, wzor) in ((-1, ("lisc_jasny", "lisc_ciemny")), (1, ("drewno_jasne", "czerwien"))):
            with s.uklad(pos=(zn * 7.0, 0, -2.0)):
                for k in range(5):
                    a = math.radians(k * 72 + 10)
                    s.blok("Korzeń gniazda", (4.2 * math.cos(a), 0.9, 4.2 * math.sin(a)), (5.0, 1.8, 1.8), "drewno_ciemne", "Wood",
                           rot=(0, -math.degrees(a) + 90, rnd.uniform(-10, 10)))
                s.blok("Jajo", (0, 4.6, 0), (5.6, 7.2, 5.6), kol, rot=(rnd.uniform(-6, 6), 25, zn * 8))
                with s.cechy(kolizja=False, cien=False):
                    if zn < 0:
                        for yy, ry in ((3.2, 10), (5.6, 55)):
                            s.blok("Jajo liść", (0, yy, 2.85), (3.0, 0.9, 0.3), wzor, rot=(0, 25, zn * 8 + 20))
                    else:
                        for yy, xx in ((3.0, -1.2), (5.0, 1.0), (6.2, -0.6)):
                            s.blok("Jajo kropka", (xx, yy, 2.85), (1.1, 1.1, 0.3), wzor, rot=(0, 25, 45))
                    s.blok("Kapsel", (0, 8.5, 0), (2.8, 1.0, 2.8), "dach_wylegarnia", rot=(0, 25, zn * 8))
                    s.blok("Kapsel światło", (0, 9.2, 0), (1.6, 0.6, 1.6), "neon_slime", "Neon", rot=(0, 25, zn * 8))
                wspolne.punkt_e(s, "Serce/Lokacje/GniazdoWKorzeniach", (0, 0, 7.0))
    G.zajmij(x, z, 14)


def dziupla_turniejowa(s, G, rnd, L):
    """Leżący, wydrążony pień (Ø 16, dł. 52) wzdłuż poziomicy polany: ciemny otwór od strony Ukłonu (wejście do walk
    petów, E), girlanda chorągiewek i tron z szyszki na grzbiecie."""
    x, z = L["x"], L["z"]
    ry = math.degrees(math.atan2(-z, x))                      # oś pnia wzdłuż stycznej do polany
    y = min(G.T.H(x, z), 0.6)
    with s.grupa("Serce/Lokacje/DziuplaTurniejowa"), s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.walec("Dziupla pień", (0, 7.2, 0), 8.0, 52.0, "drewno", "Wood", os="z")
        with s.cechy(kolizja=False):
            for zz, zn in ((-26.1, -1), (26.1, 1)):
                s.walec("Dziupla słoje", (0, 7.2, zz), 8.2, 0.4, "drewno_jasne", os="z")
                s.walec("Dziupla otwór", (0, 6.4, zz + zn * 0.15), 5.6, 0.4, "tusz", os="z")
            s.blok("Dziupla mech", (0, 15.1, 4.0), (6.0, 0.6, 30.0), "mech")
            # girlanda chorągiewek wzdłuż grzbietu
            kol = ["czerwien", "zloto", "dach_twierdza", "pomarancz", "dach_sklep", "biel"]
            s.blok("Girlanda", (5.6, 13.6, 0), (0.25, 0.25, 44.0), "tusz", rot=(0, 0, 0))
            with s.cechy(cien=False):
                for i in range(9):
                    zz = -20 + 5 * i
                    s.naroznik("Chorągiewka", (5.8, 12.6, zz), (0.3, 1.8, 2.2), kol[i % len(kol)], "Fabric", rot=(0, 90, 180))
            # tron z szyszki
            with s.uklad(pos=(0, 15.2, -8.0), obrot=(0, 20, 0)):
                for i, (a, h) in enumerate(((5.0, 2.4), (4.0, 2.2), (2.8, 2.0), (1.6, 1.6))):
                    s.blok("Szyszka", (0, 1.2 + 2.0 * i, -1.6), (a, h, a), "drewno_ciemne" if i % 2 else "drewno", rot=(0, 45 * i, 0))
                s.blok("Tron siedzisko", (0, 0.8, 1.2), (3.6, 1.0, 3.2), "dach_karczma")
        wspolne.punkt_e(s, "Serce/Lokacje/DziuplaTurniejowa", (0, 0, -27.5))
    G.zajmij(x, z, 28)


def korzenna_gardziel(s, G, rnd, L):
    """Ciemna paszcza pod talerzem korzeni zwalonego olbrzyma, zielony blask w głębi i wrota z kłódką (loch, D-042)."""
    x, z = L["x"], L["z"]
    y = G.T.H(x, z)
    with s.grupa("Serce/Lokacje/KorzennaGardziel"), s.uklad(pos=(x, y, z), obrot=(0, _ku(x, z), 0)):
        s.walec("Talerz korzeni", (0, 8.5, -1.0), 10.5, 3.0, "drewno_ciemne", "Wood", os="z", rot=(-8, 0, 0))
        s.walec("Zwalony pień", (2.0, 6.0, -18.0), 6.0, 30.0, "drewno", "Wood", os="z", rot=(-6, 8, 0))
        with s.cechy(kolizja=False):
            for k in range(7):
                a = math.radians(k * 51 + 10)
                s.belka("Korzeń", (6.0 * math.cos(a), 8.5 + 6.0 * math.sin(a), 0.6),
                        (13.0 * math.cos(a), 8.5 + 12.0 * math.sin(a) + 1.5, 2.5), 1.6, "drewno_ciemne", "Wood")
            s.blok("Paszcza", (0, 3.4, 0.6), (8.0, 6.8, 0.6), "tusz")
            s.blok("Blask", (0, 2.6, 0.3), (5.0, 3.6, 0.4), "neon_portal", "Neon")
            for xx in (-4.4, 4.4):
                s.blok("Wrota słup", (xx, 3.8, 1.4), (1.2, 7.6, 1.2), "drewno_ciemne", rot=(0, 0, -xx * 0.8))
            for yy in (2.0, 4.4, 6.6):
                s.blok("Wrota belka", (0, yy, 1.5), (8.6, 0.6, 0.5), "drewno", rot=(0, 0, 3 if yy > 3 else -3))
            s.blok("Kłódka", (0, 3.4, 2.0), (1.8, 2.0, 0.6), "zloto")
            s.blok("Kłódka kabłąk", (0, 4.8, 2.0), (1.2, 0.9, 0.3), "metal_ciemny")
            s.blok("Kłódka dziurka", (0, 3.1, 2.35), (0.4, 0.8, 0.1), "tusz")
        wspolne.punkt_e(s, "Serce/Lokacje/KorzennaGardziel", (0, 0, 6.0))
    G.zajmij(x, z, 16)


def lampiony_polany(s, G, rnd):
    """Sześć lampionów na pierścieniu polany, z dala od pięciu dróg."""
    with s.grupa("Serce/Lokacje/Polana"):
        for a in (22, 70, 112, 160, 202, 290):
            r = 58.0
            px, pz = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            if G.na_sciezce(px, pz, 2.5):
                continue
            wspolne.lampion(s, (px, G.T.H(px, pz), pz), 6.0)


LOKACJE = {"gniazdo_w_korzeniach": gniazdo_w_korzeniach, "dziupla_turniejowa": dziupla_turniejowa,
           "korzenna_gardziel": korzenna_gardziel}
