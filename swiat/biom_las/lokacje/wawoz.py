# -*- coding: utf-8 -*-
"""Lokacje Suchego Wąwozu: Schody Głazów (rampa na koronę tamy), Wyschnięta Kałuża, Trollowa Tama z legowiskiem,
Jezioro za Tamą (wysepka), próg przy Ujściu (kości, drogowskaz z maczugą)."""
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


def _tama(G):
    e = next(p for p in G.T.poziomy if p["id"] == "tama")
    WL, ER, DNE, DNW = [tuple(p) for p in e["wielokat"]]
    return WL, ER, DNE, DNW


def schody_glazow(s, G, rnd, L):
    """Rampa wzdłuż zachodniej ściany rynny (teren.py) obłożona od strony rynny głazami-stopniami; na dnie ciemna
    bruzda po maczudze trolla wzdłuż jego trasy; na wschodniej ścianie płaskie półki w kaskadzie."""
    r = next(e for e in G.T.rampy if e["id"] == "schody_glazow")
    (ax, az, _), (bx, bz, by) = r["od"], r["do"]
    dl = math.hypot(bx - ax, bz - az)
    ex, ez = (bx - ax) / dl, (bz - az) / dl
    nx, nz = ez, -ex                                           # w stronę środka rynny (na wschód)
    with s.grupa("Wawoz/Lokacje/SchodyGlazow"):
        for i in range(5):
            t = (i + 0.5) / 5
            px, pz = ax + ex * dl * t + nx * 7.5, az + ez * dl * t + nz * 7.5
            h = by * t
            with s.uklad(pos=(px, 0, pz), obrot=(0, math.degrees(math.atan2(ex, ez)) + rnd.uniform(-8, 8), rnd.choice((-5, 5)))):
                s.blok("Głaz-stopień", (0, (h + 1.5) / 2.0 - 0.5, 0), (4.0, h + 2.5, 8.5), cien(s, "kamien_cieply", 0.85 if i % 2 else 1.0))
        tr = G.P["troll"]["trasa"]
        with s.cechy(kolizja=False, cien=False):
            for a, b in zip(tr[:5], tr[1:5]):
                from swiat.biom_las.teren import wstega
                wstega(s, "Bruzda", (a[0], 0.12, a[1]), (b[0], 0.12, b[1]), 2.2, 0.2, "kamien_cokol")
        # półki na wschodniej ścianie rynny w okolicy (318;-120)
        for i, (px, pz, y) in enumerate(((326, -100, 2.0), (329, -88, 4.2), (331, -76, 6.4), (333, -64, 8.6))):
            s.blok("Półka skalna", (px, y - 0.5, pz), (6.0, 1.0, 9.0), "kamien_cieply", rot=(0, 12, rnd.uniform(-4, 4)))


def wyschnieta_kaluza(s, G, rnd, L):
    """Ciemne, popękane błoto (podkładka strefy z12 — bursztynowe slime'y dobrze na nim widać), mała kałuża
    i wyblakły szkielet łódki."""
    x, z = L["x"], L["z"]
    with s.grupa("Wawoz/Lokacje/WyschnietaKaluza"), s.uklad(pos=(x, 0, z)), s.cechy(kolizja=False, cien=False):
        s.walec("Kałuża woda", (-2.0, 0.22, 3.0), 3.4, 0.2, "woda", os="y")
        for k in range(9):
            a = rnd.uniform(0, 2 * math.pi)
            r = rnd.uniform(6, 26)
            s.blok("Pęknięcie", (r * math.cos(a), 0.16, r * math.sin(a)), (0.4, 0.1, rnd.uniform(4, 9)), "tusz",
                   rot=(0, rnd.uniform(0, 180), 0))
    # szkielet łódki (poza placami walki, w rdzeniu lokacji)
    with s.grupa("Wawoz/Lokacje/WyschnietaKaluza"), s.uklad(pos=(x + 3.0, 0, z - 3.0), obrot=(0, 35, 8)), s.cechy(kolizja=False):
        s.blok("Łódka stępka", (0, 0.4, 0), (0.8, 0.8, 9.0), "drewno_jasne")
        for i in range(5):
            zz = -3.6 + 1.8 * i
            for zn in (-1, 1):
                s.belka("Łódka żebro", (0, 0.4, zz), (zn * 2.0, 2.4 - abs(zz) * 0.2, zz), 0.45, "biel", "SmoothPlastic")


def trollowa_tama(s, G, rnd, L):
    """Tama z nierównych głazów: czoło od dna rynny do korony (12) i wysokie głazy na końcach (do 25), z otworem
    legowiska (kocioł, ukradziony szyld, kości), cienką strużką wody i rzędem głazów od strony jeziora (chodnik
    po koronie zostaje wolny)."""
    WL, ER, DNE, DNW = _tama(G)
    fx, fz = ER[0] - WL[0], ER[1] - WL[1]
    flen = math.hypot(fx, fz)
    ux, uz = fx / flen, fz / flen                              # wzdłuż czoła (z zachodu na wschód)
    nx, nz = -(DNW[0] - WL[0]) / 14.0, -(DNW[1] - WL[1]) / 14.0   # na zewnątrz czoła (ku dnu rynny)
    ry_czola = math.degrees(math.atan2(nx, nz))
    with s.grupa("Punkty/TrollowaTama"):
        for i in range(8):
            t = (i + 0.5) / 8
            if 0.38 < t < 0.62 or t < 0.2:                     # otwór legowiska i miejsce na górny koniec rampy
                continue
            px, pz = WL[0] + fx * t + nx * 1.5, WL[1] + fz * t + nz * 1.5
            h = rnd.uniform(9, 13.5)
            with s.uklad(pos=(px, 0, pz), obrot=(rnd.uniform(-6, 6), ry_czola + rnd.uniform(-10, 10), rnd.choice((-7, 7)))):
                s.blok("Głaz tamy", (0, h / 2.0 - 0.5, -1.5), (flen / 8 + 2.0, h + 1.0, 6.0), cien(s, "kamien_cieply", 0.8 + 0.1 * (i % 2)))
        for (px, pz), h in (((DNE[0] + ux * 2, DNE[1] + uz * 2), 17.0), ((ER[0] + ux * 3, ER[1] + uz * 3), 14.0),
                             ((DNW[0] - ux * 3, DNW[1] - uz * 3), 13.0)):
            with s.uklad(pos=(px, 12.0, pz), obrot=(0, rnd.uniform(0, 90), rnd.choice((-8, 8)))):
                s.blok("Głaz szczytowy", (0, h / 2.0 - 0.5, 0), (8.0, h + 1.0, 7.0), "kamien_cieply")
                s.naroznik("Głaz szczytowy", (0, h + 1.0, 0), (6.0, 3.0, 5.0), cien(s, "kamien_cieply", 0.85), rot=(0, 90, 0))
        # rząd głazów po stronie jeziora
        for i in range(4):
            t = 0.12 + 0.22 * i
            px, pz = DNW[0] + (DNE[0] - DNW[0]) * t - nx * 1.0, DNW[1] + (DNE[1] - DNW[1]) * t - nz * 1.0
            skaly.glaz(s, rnd, (px, 12.0, pz), rnd.uniform(0.8, 1.1), rnd.uniform(0, 360), "kamien_cieply", mech=i % 2 == 0)
    cx, cz = WL[0] + fx * 0.5, WL[1] + fz * 0.5
    with s.grupa("Wawoz/Lokacje/TrollowaTama"), s.uklad(pos=(cx, 0, cz), obrot=(0, ry_czola, 0)):
        with s.cechy(kolizja=False):
            s.blok("Legowisko", (0, 4.5, 0.25), (11.0, 9.0, 0.5), "tusz")
            for xx in (-6.6, 6.6):
                s.blok("Legowisko węgar", (xx, 5.0, 0.9), (2.2, 10.0, 1.8), "kamien_cokol", rot=(0, 0, xx * 0.6))
            s.blok("Legowisko nadproże", (0, 10.0, 1.0), (15.0, 2.2, 2.2), "kamien_cokol", rot=(0, 0, 3))
            s.walec("Kocioł", (-3.0, 1.4, 5.0), 2.2, 2.6, "metal_ciemny", os="y")
            s.walec("Kocioł brzeg", (-3.0, 2.8, 5.0), 2.5, 0.4, "tusz", os="y")
            with s.cechy(cien=False):
                s.naroznik("Ogień", (-3.0, 0.5, 5.0), (1.6, 1.2, 1.6), "neon_ogien", "Neon", rot=(0, 30, 0))
            # ukradziony szyld z miasteczka (czerwona rama karczmy, złoty bochenek)
            s.blok("Szyld słup", (4.6, 3.0, 4.0), (0.6, 6.0, 0.6), "drewno_ciemne", rot=(0, 0, -8))
            s.blok("Szyld", (5.2, 5.4, 4.3), (4.6, 3.0, 0.4), "tynk_krem", rot=(0, 0, -8))
            s.ramka("Szyld rama", (5.2, 5.4, 4.6), 4.6, 3.0, "dach_karczma", 0.4, 0.3)
            s.blok("Szyld bochenek", (5.2, 5.4, 4.7), (2.2, 1.2, 0.2), "zloto", rot=(0, 0, -8))
            with s.cechy(cien=False):
                for k in range(5):
                    s.blok("Kość", (rnd.uniform(-6, 6), 0.3, rnd.uniform(2, 9)), (2.4, 0.45, 0.6), "biel", rot=(0, rnd.uniform(0, 180), 0))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Strużka", (5.2, 6.0, 0.4), (1.0, 12.0, 0.3), "woda")
            s.walec("Strużka rozlewisko", (5.2, 0.22, 2.0), 2.2, 0.2, "woda", os="y")
    wspolne.ognisko(s, rnd, (205, 12.0, -212))
    G.zajmij(cx, cz, 14)


def jezioro_za_tama(s, G, rnd, L):
    """Wysepka z jedną krzywą sosną i złota kaczka-klocek (echo stawu w miasteczku)."""
    x, z = 345.0, -350.0
    with s.grupa("Wawoz/Lokacje/JezioroZaTama"):
        s.walec("Wysepka", (x, 10.75, z), 8.0, 2.5, "bruk_ciemny", os="y")
        with s.cechy(kolizja=False, cien=False):
            s.walec("Wysepka trawa", (x, 12.08, z), 7.0, 0.2, "trawa", os="y")
        rosliny.sosna(s, rnd, (x + 1.0, 12.0, z), 0.9, 30)
        with s.uklad(pos=(x - 30.0, 11.0, z + 26.0), obrot=(0, 40, 0)), s.cechy(kolizja=False):
            s.blok("Kaczka", (0, 0.5, 0), (2.0, 1.4, 3.0), "zloto")
            s.blok("Kaczka głowa", (0, 1.8, 1.0), (1.4, 1.4, 1.4), "zloto")
            s.blok("Kaczka dziób", (0, 1.7, 2.0), (0.8, 0.5, 0.8), "pomarancz")


def prog_ujscia(s, G, rnd):
    """Wyraźny próg przy wylocie rynny Ujścia na łąkę: łuk z dwóch żeber-kości nad dróżką i drogowskaz z maczugą
    (dalej mieszkają potwory 6.–9. poziomu)."""
    px, pz = 349.0, 168.0
    with s.grupa("Wawoz/Lokacje/ProgUjscia"), s.uklad(pos=(px, 0, pz), obrot=(0, 2, 0)):
        for zn in (-1, 1):
            s.belka("Żebro", (zn * 8.5, 0, 0), (zn * 6.5, 9.0, 0.5), 1.6, "biel", "SmoothPlastic")
            with s.cechy(kolizja=False):
                s.belka("Żebro", (zn * 6.5, 9.0, 0.5), (zn * 1.0, 12.5, 0.8), 1.3, "biel", "SmoothPlastic")
        with s.cechy(kolizja=False):
            s.blok("Czaszka-klocek", (0, 13.2, 0.8), (3.0, 2.6, 2.6), "biel", rot=(0, 10, 6))
            for xx in (-0.7, 0.7):
                s.blok("Oczodół", (xx, 13.4, 2.15), (0.8, 0.8, 0.2), "tusz")
        wspolne.drogowskaz(s, rnd, (12.0, 0, 3.0), [(0.0, "wawoz"), (180.0, "laka")], latarenka=False)
        s.blok("Maczuga w ziemi", (-12.0, 2.5, 2.0), (1.2, 5.0, 1.2), "drewno_ciemne", rot=(0, 20, 12))
        s.blok("Maczuga głowica", (-12.6, 5.6, 2.0), (2.4, 2.4, 2.4), "drewno_ciemne", rot=(20, 30, 14))


LOKACJE = {"schody_glazow": schody_glazow, "wyschnieta_kaluza": wyschnieta_kaluza, "trollowa_tama": trollowa_tama,
           "jezioro_za_tama": jezioro_za_tama}
