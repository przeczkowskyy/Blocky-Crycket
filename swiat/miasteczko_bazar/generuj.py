#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator „Miasteczko jako ciasny bazar” — składa scenę z klocków z uklad.json.

    python -B swiat/miasteczko_bazar/generuj.py            # → czesci.json + znaczniki.json + raport części
    python -B swiat/miasteczko_bazar/generuj.py --wyj X    # części do innego pliku (znaczniki zawsze obok generatora)

Kontener w Studio: Workspace/MiasteczkoBazar (osobny od Workspace/KrzyweMiasteczko, które zostaje do porównania).
W pliku części wszystko stoi już tam, gdzie ma stanąć w świecie Studio: świat = (X0 + x; y; Z0 + z), bez obrotu
(X0 = 994, Z0 = −700 z uklad.json; wschodni brzeg bazaru x 72 = X 1066 = początek pasa Lasu).
Wynik deterministyczny (random.Random(ziarno)). Kolejność: teren → budynki (moduły) → domy → stragany → łączniki i mury
→ rekwizyty → kulisy i tło → niewidzialne ściany → bruk (omija obrysy budynków) → ścieżki-kody i start → zapis.
Status: propozycja (16.11.2026), nie kanon.
"""
import argparse
import importlib
import json
import math
import os
import random
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import Scena, KULA, WALEC  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import PALETA, cien  # noqa: E402
from swiat.miasteczko_bazar import wspolne  # noqa: E402

PLIK_UKLADU = os.path.join(TU, "uklad.json")
LIMIT, CEL = 12000, 8000


def wczytaj_uklad(plik=PLIK_UKLADU):
    with open(plik, encoding="utf-8") as f:
        return json.load(f)


def modul(nazwa):
    if nazwa.startswith("stare:"):
        return importlib.import_module("swiat.krzywe_miasteczko.budynki." + nazwa[6:])
    return importlib.import_module("swiat.miasteczko_bazar.budynki." + nazwa)


class Obrys:
    """Prostokąt obrotowy w płaszczyźnie (x, z) bazaru: środek, obrót ry (°), szer × gł (+ zapas)."""

    def __init__(self, nazwa, x, z, ry, w, d, zapas=0.0):
        self.nazwa, self.x, self.z = nazwa, x, z
        self.c, self.s = math.cos(math.radians(ry)), math.sin(math.radians(ry))
        self.w, self.d, self.zapas = w / 2.0 + zapas, d / 2.0 + zapas, zapas

    def zawiera(self, px, pz):
        dx, dz = px - self.x, pz - self.z
        lx = dx * self.c - dz * self.s                          # świat → lokalne (odwrotność obrotu ry)
        lz = dx * self.s + dz * self.c
        return abs(lx) <= self.w and abs(lz) <= self.d


# =========================================================================== teren
def teren(s, U):
    g = U["granice"]
    x0, x1 = g["czesci_x"]
    z0, z1 = g["czesci_z"]
    P = U["poziomy"]
    with s.grupa("Teren"):
        s.blok("Grunt", ((x0 + x1) / 2.0, P["grunt"] / 2.0, (z0 + z1) / 2.0), (x1 - x0, P["grunt"], z1 - z0), "trawa")
        px0, px1 = g["pole_gry_x"]
        pz0, pz1 = g["pole_gry_z"]
        s.blok("Fuga bruku", ((px0 + px1) / 2.0, (P["grunt"] + P["fuga"]) / 2.0, 0.0),
               (px1 - px0 + 1.0, P["fuga"] - P["grunt"], pz1 - pz0 + 1.0), cien(s, "bruk", 0.6))


def bruk(s, U, rnd, obrysy):
    """Płyty bruku 3,7 × (3,7–7,7) w trzech tonach na całym polu gry poza obrysami budynków; szczeliny 0,3 pokazują
    ciemną fugę (komiksowy rysunek nawierzchni)."""
    g, P = U["granice"], U["poziomy"]
    px0, px1 = g["pole_gry_x"]
    pz0, pz1 = g["pole_gry_z"]
    tony = ["bruk"] * 6 + ["bruk_ciemny"] * 3 + [cien(s, "bruk", 0.9)]
    n = 0
    with s.grupa("Uliczka/Bruk"), s.cechy(cien=False):
        x = px0
        while x < px1 - 0.5:
            szer = min(4.0, px1 - x)
            z = pz0 + rnd.uniform(0, 2.0) * (n % 2)
            if z > pz0:
                z = pz0
            while z < pz1 - 0.5:
                dl = min(rnd.choice((4.0, 5.0, 6.0, 8.0)), pz1 - z)
                cx, cz = x + szer / 2.0, z + dl / 2.0
                if not any(o.zawiera(cx, cz) for o in obrysy):
                    s.blok("Bruk", (cx, (P["fuga"] + P["bruk"]) / 2.0, cz), (szer - 0.3, P["bruk"] - P["fuga"], dl - 0.3),
                           rnd.choice(tony))
                z += dl
            x += szer
            n += 1


# =========================================================================== budynki
def blokada_lochow(s):
    """Kłódka i łańcuchy na krzyż przed gardzielą Wrót lochów (D-042): grupa BramaLochow/Blokada — skrypt pokazuje ją
    każdemu graczowi osobno i chowa po odblokowaniu (animacja spadającej kłódki / cutscenka). Bez kolizji."""
    with s.grupa("BramaLochow/Blokada"), s.cechy(kolizja=False):
        for a, b in (((-6.5, 13.0), (6.5, 1.5)), ((6.5, 13.0), (-6.5, 1.5))):
            s.belka("Łańcuch blokady", (a[0], a[1], 7.4), (b[0], b[1], 7.4), 0.7, "metal_ciemny", "SmoothPlastic", 0.45)
        s.blok("Kłódka", (0, 6.6, 7.9), (3.6, 3.4, 1.2), "zloto")
        s.blok("Kłódka obrys", (0, 6.6, 7.55), (4.2, 4.0, 0.6), "tusz")
        s.blok("Kłódka dziurka", (0, 6.3, 8.55), (0.6, 1.2, 0.2), "tusz")
        for x in (-1.1, 1.1):
            s.blok("Kłódka pałąk", (x, 9.0, 7.9), (0.6, 1.8, 0.6), "metal_ciemny")
        s.blok("Kłódka pałąk", (0, 9.85, 7.9), (2.8, 0.6, 0.6), "metal_ciemny")


def budynki(s, U, obrysy):
    P = U["poziomy"]
    raport = {}
    for b in U["budynki"]:
        m = modul(b["modul"])
        stary = b["modul"].startswith("stare:")
        y0 = P["stare_y0"] if stary else P["budynki_y0"]
        n0 = len(s.czesci)
        with s.uklad(pos=(b["x"], y0, b["z"]), obrot=(0, b["ry"], 0), grupa=m.NAZWA):
            m.buduj(s, random.Random(sum(map(ord, b["id"]))))
            if stary and "interakcja" in b:
                ix, iz = b["interakcja"]
                pola = dict(stoisko=(ix, 0.0, iz), podpowiedz=(ix, 4.6, iz - 1.0), grupa_zaczepu=s.korzen + "/" + m.NAZWA + "/_Interakcja",
                            czesc_stoiska="Punkt interakcji", nazwa=b.get("nazwa"), kier=(0, 0, 1))
                wspolne.znacznik(s, b.get("typ", "inne"), b["id"], (ix, 0.0, iz), **pola)
            if stary and "wejscie" in b:
                wspolne.znacznik(s, "wejscie", "wejscie_" + m.NAZWA, (0.0, 0.0, m.OBRYS[1] / 2.0 - 4.0), kier=(0, 0, 1),
                                 szer=b["wejscie"]["szer"], wys=b["wejscie"]["wys"], budynek=m.NAZWA,
                                 opis="przejście bramy (karta budynku w swiat/krzywe_miasteczko/PROJEKT.md)")
            if b["id"] == "brama_lochow":
                blokada_lochow(s)
                wspolne.znacznik(s, "blokada", "lochy_klodka", (0.0, 6.6, 7.9), grupa=s.korzen + "/BramaLochow/Blokada",
                                 opis="kłódka i łańcuchy (D-042): widoczne osobno dla każdego gracza, znikają po odblokowaniu")
        raport[m.NAZWA] = len(s.czesci) - n0
        w, d = m.OBRYS
        obrysy.append(Obrys(m.NAZWA, b["x"], b["z"], b["ry"], w, d, 0.2))
    return raport


def domy(s, U, rnd, obrysy):
    P = U["poziomy"]
    n0 = len(s.czesci)
    for i, d in enumerate(U["domy"]):
        with s.uklad(pos=(d["x"], P["budynki_y0"], d["z"]), obrot=(0, d["ry"], 0), grupa="Domy/" + d["id"]):
            zestaw.dom_mieszkalny(s, random.Random(100 + i), wariant=d["wariant"], kolor_dachu=d["dach"],
                                  kolor_sciany=d["sciana"], szer=d["szer"], gl=d["gl"], wys=d["wys"], pochyl=d["pochyl"],
                                  neon_okna=1, okiennica=None, znak="lata" if i % 2 else "klocek", dym_n=2 if i == 0 else 0)
        obrysy.append(Obrys(d["id"], d["x"], d["z"], d["ry"], d["szer"], d["gl"], 0.2))
    n1 = len(s.czesci)
    for i, d in enumerate(U["kulisy_domy"]):
        with s.uklad(pos=(d["x"], P["budynki_y0"], d["z"]), obrot=(0, d["ry"], 0), grupa="Kulisy/Domy"):
            zestaw.dom_mieszkalny(s, random.Random(200 + i), wariant=d["wariant"], kolor_dachu=d["dach"],
                                  kolor_sciany=d["sciana"], szer=16, gl=14, wys=d["wys"], pochyl=1 if i % 2 else -1,
                                  neon_okna=1, znak="lata", dym_n=2 if i in (1, 8) else 0)
    for i, d in enumerate(U.get("kulisy_domy_2", [])):          # drugi rząd tła: dachy widać nad pierwszym
        with s.uklad(pos=(d["x"], U["poziomy"]["grunt"], d["z"]), obrot=(0, d["ry"], 0), grupa="Kulisy/Domy"):
            zestaw.dom_mieszkalny(s, random.Random(300 + i), wariant=d["wariant"], kolor_dachu=d["dach"],
                                  kolor_sciany=d["sciana"], szer=16, gl=14, wys=d["wys"], pochyl=-1 if i % 2 else 1,
                                  neon_okna=1, znak="klocek", dym_n=2 if i in (2, 5) else 0)
    return {"Domy": n1 - n0, "Kulisy/Domy": len(s.czesci) - n1}


def stragany(s, U):
    P = U["poziomy"]
    n0 = len(s.czesci)
    for i, st in enumerate(U["stragany"]):
        with s.grupa("Stragany/Stragan%d" % (i + 1)):
            zestaw.stragan(s, (st["x"], P["budynki_y0"], st["z"]), ry=st["ry"], kolory=tuple(st["kolory"]), towar=st["towar"])
    return len(s.czesci) - n0


def mur(s, a, b, wys, rnd):
    """Odcinek muru: korpus kamien_cieply z kolizją, cokół, rant tuszem i blanki co 3,2 (co drugi niższy i w cieniu)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dz)
    ry = math.degrees(math.atan2(-dz, dx))
    with s.uklad(pos=((a[0] + b[0]) / 2.0, 0.3, (a[1] + b[1]) / 2.0), obrot=(0, ry, 0)):
        s.blok("Mur", (0, wys / 2.0, 0), (L, wys, 1.8), "kamien_cieply")
        with s.cechy(kolizja=False):
            s.blok("Mur cokół", (0, 0.7, 0), (L + 0.2, 1.4, 2.3), "kamien_cokol", "Cobblestone")
            s.blok("Mur rant", (0, wys + 0.2, 0), (L + 0.3, 0.4, 2.1), "tusz")
            k = 0
            x = -L / 2.0 + 1.0
            while x < L / 2.0 - 0.8:
                h = 1.4 if k % 2 == 0 else 1.1
                s.blok("Mur blanka", (x, wys + 0.4 + h / 2.0, 0), (1.6, h, 1.9),
                       "kamien_cieply" if k % 2 == 0 else cien(s, "kamien_cieply", 0.85))
                x += 3.2
                k += 1


def laczniki_i_mury(s, U, rnd):
    n0 = len(s.czesci)
    P = U["poziomy"]
    with s.grupa("Mury"):
        for l in U["laczniki"]:
            wspolne.scianka(s, (l["x"], P["budynki_y0"], l["z"]), l["dl"], wys=10.0, kolor="kamien_cieply", gl=1.6)
        for m in U["mury"]:
            mur(s, m["a"], m["b"], m["wys"], rnd)
    return len(s.czesci) - n0


# =========================================================================== rekwizyty
def trojka(s, rnd, x, z, ry, y=0.3):
    """Trójka duży–średni–mały: beczka z jabłkami, beczka z wodą, skrzynia (kolizja tylko korpusów, wys. ≥ 2,5)."""
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        zestaw.beczka(s, (0, 0, 0), "jablka", przechyl=(0, 6))
        zestaw.beczka(s, (3.4, 0, 0.6), "woda", r=1.5, h=3.6, przechyl=(4, -5))
        zestaw.skrzynia(s, (1.6, 0, -2.8), ry=rnd.uniform(-20, 20), dl=3.2, a=2.8, przechyl=8)


def rekwizyty(s, U, rnd):
    n0 = len(s.czesci)
    P = U["poziomy"]
    y = P["budynki_y0"]
    with s.grupa("Rekwizyty/Latarnie"):
        for l in U["latarnie"]:
            zestaw.latarnia(s, (l["x"], y, l["z"]), wys=9.0, ry=(-90 if l["strona"] == "pn" else 90), plama_r=3.0)
    with s.grupa("Rekwizyty/Girlandy"):
        for g in U["girlandy"]:
            wspolne.girlanda(s, g["a"], g["b"], g["kolory"], ugiecie=1.8, n=11)
    with s.grupa("Rekwizyty/Plac"):
        trojka(s, rnd, 13.4, -30.0, 10, y)                       # kąt pn.-wsch. placu, przy murze
        zestaw.lawka(s, (15.0, y, -20.5), ry=-6)
        zestaw.choragiew(s, (-12.6, y, -33.0), kolor="dach_gildia", wys=13.0, ry=-20)
        zestaw.choragiew(s, (18.0, y, -33.0), kolor="dach_brama", wys=12.0, ry=200)
        zestaw.skrzynia(s, (-17.0, y, -30.5), ry=-15, dl=3.4, a=3.0, przechyl=6)
        zestaw.beczka(s, (-13.6, y, -29.0), "woda", przechyl=(0, -7))
    with s.grupa("Rekwizyty/Placyk"):
        zestaw.lawka(s, (-81.0, y, -14.5), ry=0)
        zestaw.lawka(s, (-81.0, y, 14.5), ry=180)
        zestaw.drzewo_lisciaste(s, (-92.0, y, -29.5), random.Random(11), skala=0.9)
        zestaw.drzewo_lisciaste(s, (-92.0, y, 29.5), random.Random(12), skala=0.95, owoce=True)
        zestaw.kwiaty(s, (-92.0, y, -3.0), ry=90, kolory=("czerwien", "biel"))
        zestaw.kwiaty(s, (-92.0, y, 3.0), ry=90, kolory=("dach_sklep", "zloto"))
    with s.grupa("Rekwizyty/Zaulki"):
        trojka(s, rnd, 61.0, -30.0, -80, y)                     # kąt pn.-wsch. przy Bramie Leśnej
        trojka(s, rnd, 61.0, 30.0, 100, y)                      # kąt pd.-wsch.
        zestaw.skrzynia(s, (61.5, y, -21.0), ry=10, dl=3.0, a=2.6, przechyl=8)
        zestaw.beczka(s, (61.6, y, 22.0), "jablka", przechyl=(0, 5))
        trojka(s, rnd, -62.0, 30.0, 175, y)                     # za straganami
        zestaw.skrzynia(s, (-55.0, y, 30.5), ry=4, dl=3.6, a=3.0, przechyl=6)
        zestaw.kwiaty(s, (27.0, y, 15.4), ry=180, kolory=("czerwien", "zloto"))
    return len(s.czesci) - n0


# =========================================================================== kulisy i tło
def kulisy_i_tlo(s, U, rnd):
    n0 = len(s.czesci)
    y = U["poziomy"]["grunt"]
    with s.grupa("Kulisy/Drzewa"):
        for zn in (-1, 1):
            x = -104.0
            k = 0
            while x < 64.0:
                z = zn * rnd.uniform(56.0, 60.0) if k % 2 else zn * rnd.uniform(71.0, 77.0)
                if k % 2 and any(abs(x - d["x"]) < 10.0 and d["z"] * zn > 0 for d in U.get("kulisy_domy_2", [])):
                    x += rnd.uniform(7.0, 10.0)
                    k += 1
                    continue
                if k % 3 == 1:
                    zestaw.drzewo_iglaste(s, (x, y, z), rnd, skala=rnd.uniform(0.95, 1.15))
                else:
                    zestaw.drzewo_lisciaste(s, (x, y, z), rnd, skala=rnd.uniform(0.95, 1.15))
                x += rnd.uniform(7.0, 10.0)
                k += 1
        # za Bramą Twierdzy — zielony prześwit „działki” zamiast domów
        for x, z in ((-8.0, 42.0), (6.0, 44.0), (-1.0, 50.0)):
            zestaw.drzewo_lisciaste(s, (x, y, z), rnd, skala=1.05)
        for x, z in ((-103.0, -30.0), (-103.0, 0.0), (-103.0, 30.0)):
            zestaw.drzewo_iglaste(s, (x, y, z), rnd, skala=1.1)
    with s.grupa("Tlo"), s.cechy(kolizja=False, cien=False):
        # pagórki z trzech klocków (schodkowe, jak w stylu miasteczka) — nic nie schodzi pod grunt (Baseplate pod spodem)
        kol = (("lisc_ciemny", "igla", "lisc"), ("igla", "lisc_ciemny", "lisc_jasny"))
        for i, x in enumerate((-96.0, -70.0, -44.0, -16.0, 12.0, 38.0)):
            for zn in (-1, 1):
                a = rnd.uniform(18.0, 24.0)
                with s.uklad(pos=(x + rnd.uniform(-3, 3), U["poziomy"]["grunt"], zn * (88.0 - a * 0.5)),
                             obrot=(0, rnd.uniform(-25, 25), 0)):
                    k = kol[(i + (zn > 0)) % 2]
                    for j, (f, h) in enumerate(((1.0, 5.0), (0.68, 4.5), (0.38, 3.5))):
                        s.blok("Pagórek", (rnd.uniform(-1, 1) * j, 5.0 * (j > 0) + 4.5 * (j > 1) + h / 2.0, 0),
                               (a * f, h, a * f * 0.8), k[j], rot=(0, 15 * j, 0))
    with s.grupa("Chmury"):
        for x, z, yy in ((-80.0, -72.0, 96.0), (-20.0, -76.0, 104.0), (30.0, -70.0, 92.0), (52.0, -76.0, 100.0)):
            zestaw.chmura(s, (x, yy, z), rnd, skala=0.9)
    return len(s.czesci) - n0


def niewidzialne(s, U):
    g = U["granice"]
    px0, px1 = g["pole_gry_x"]
    pz0, pz1 = g["pole_gry_z"]
    with s.grupa("Niewidzialne"), s.cechy(cien=False):
        for z in (pz0 - 1.5, pz1 + 1.5):
            s.blok("Niewidzialna ściana", ((px0 + px1) / 2.0, 30.0, z), (px1 - px0 + 4.0, 60.0, 2.0), "biel", alfa=1.0)
        for x in (px0 - 1.5, px1 + 1.5):
            s.blok("Niewidzialna ściana", (x, 30.0, (pz0 + pz1) / 2.0), (2.0, 60.0, pz1 - pz0 + 4.0), "biel", alfa=1.0)
    return 4


# =========================================================================== start i ścieżki-kody
def start(s, U):
    st, P = U["start"], U["poziomy"]
    x, z = st["x"], st["z"]
    with s.grupa("Start"), s.cechy(kolizja=False, cien=False):
        s.walec("Start obrys", (x, P["bruk"] + 0.05, z), 3.4, 0.1, "tusz", os="y")
        s.walec("Start", (x, P["bruk"] + 0.1, z), 3.0, 0.12, "zloto", os="y")
        s.walec("Start środek", (x, P["bruk"] + 0.16, z), 1.6, 0.1, "biel", os="y")
        with s.uklad(pos=(x, P["bruk"] + 0.2, z), obrot=(0, 25, 0)):
            s.blok("Start klocek", (0, 0.15, 0), (2.0, 0.3, 1.0), "dach_karczma")
            for xx in (-0.5, 0.5):
                s.walec("Start wypustka", (xx, 0.35, 0), 0.3, 0.2, "dach_karczma", os="y")
        s.blok("Punkt startu", (x, P["bruk"] + 0.4, z), (2.0, 0.2, 2.0), "biel", alfa=1.0)
    k = math.radians(st["patrz_deg"])
    wspolne.znacznik(s, "start", "start", (x, P["bruk"], z), kier=(math.sin(k), 0, math.cos(k)),
                     opis="miejsce startu gracza (SpawnLocation w następnym etapie); patrzy wzdłuż uliczki ku Lasowi",
                     czesc="Punkt startu", grupa=s.korzen + "/Start")


def kody(s, U, X0, Z0):
    """Ścieżki-kody (orientacja bez napisów, jak w dzisiejszym miasteczku): przerywane pasy 1,2 szer. w kolorze dachu celu
    od kręgu startu do wejścia. Płaskie, bez kolizji i cienia."""
    st, P = U["start"], U["poziomy"]
    sx, sz = st["x"], st["z"]
    cele = {}
    for zn in wspolne.ZNACZNIKI:
        if zn["typ"] == "wejscie":
            cele[zn["budynek"]] = zn["swiat"]
        if zn["id"] == "portal_krain":
            cele["PortalKrain"] = zn["swiat"]
    nazwy = {"portal_krain": "PortalKrain", "brama_twierdzy": "BramaTwierdzy", "karczma": "Karczma",
             "sklep_magiczny": "SklepMagiczny", "zbrojownia": "Zbrojownia", "zagroda_petow": "ZagrodaPetow",
             "training_center": "TrainingCenter", "brama_lochow": "BramaLochow"}
    n0 = len(s.czesci)
    with s.grupa("Uliczka/Kody"), s.cechy(kolizja=False, cien=False):
        for k in U["kody"]:
            c = cele.get(nazwy[k["do"]])
            if not c:
                continue
            tx, tz = c[0] - X0, c[2] - Z0
            dx, dz = tx - sx, tz - sz
            L = math.hypot(dx, dz)
            ux, uz = dx / L, dz / L
            ry = math.degrees(math.atan2(ux, uz))
            t = 4.2
            while t < L - 3.0:
                dl = min(2.4, L - 3.0 - t)
                if dl > 0.8:
                    s.blok("Kod", (sx + ux * (t + dl / 2.0), P["kody"] - 0.04, sz + uz * (t + dl / 2.0)), (1.2, 0.08, dl),
                           k["kolor"], rot=(0, ry, 0))
                t += 4.0
    return len(s.czesci) - n0


# =========================================================================== znaczniki
def _na_bazar(p, X0, Z0):
    return [round(p[0] - X0, 3), round(p[1], 3), round(p[2] - Z0, 3)]


def zapisz_znaczniki(U, plik, raport):
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    wszystkie = []
    for z in wspolne.ZNACZNIKI:
        z = dict(z)
        for k in ("swiat", "stoisko", "podpowiedz"):
            if k in z:
                z[k.replace("swiat", "bazar") if k == "swiat" else k + "_bazar"] = _na_bazar(z[k], X0, Z0)
        wszystkie.append(z)
    po_typie = {}
    for z in wszystkie:
        po_typie.setdefault(z["typ"], []).append(z)
    d = {
        "opis": "Znaczniki bazaru dla następnego etapu (SpawnLocation, ProximityPrompt „E” na sprzedawcach i uchwyt dla okien "
                "2D Pawła, portal krain → teleport, przejście na działkę, zagroda petów, tablica z rankingiem, Training "
                "Center, Wrota lochów, połączenie z Lasem). Punkty `swiat` = świat Studio [X, Y, Z]; `bazar` = układ bazaru "
                "(swiat − (X0; 0; Z0)). Każdy punkt E to dwie niewidzialne części w grupie `grupa_zaczepu`: "
                "`czesc_stoiska` (gdzie staje gracz) i `czesc_podpowiedzi` (gdzie wstawić ProximityPrompt). "
                "Generuje swiat/miasteczko_bazar/generuj.py z uklad.json.",
        "status": "propozycja",
        "kontener": {"nazwa": U["swiat"]["kontener"], "X0": X0, "Z0": Z0, "obrot_y": 0,
                     "wzor": U["swiat"]["wzor"]},
        "uklad": "swiat/miasteczko_bazar/uklad.json",
        "bieg_st_s": U["bieg_st_s"],
        "start": po_typie.get("start", [None])[0],
        "sklepy": po_typie.get("sklep", []),
        "training_center": po_typie.get("training_center", [None])[0],
        "zagroda": {"punkt_e": po_typie.get("zagroda", [None])[0], "miejsca_petow": po_typie.get("miejsce_peta", [])},
        "portal_krain": [z for z in wszystkie if z["typ"] in ("portal", "portal_srodek")],
        "dzialka": po_typie.get("dzialka", [None])[0],
        "lochy": {"punkt_e": po_typie.get("lochy", [None])[0], "blokada": po_typie.get("blokada", [None])[0]},
        "tablica": [z for z in wszystkie if z["typ"] == "tablica"],
        "las": {"brama_lesna": po_typie.get("las", [None])[0], "polaczenie": po_typie.get("polaczenie_las", [None])[0]},
        "wejscia": po_typie.get("wejscie", []),
        "ozdoby": po_typie.get("ozdoba", []),
        "czesci_na_budynek": raport,
        "wszystkie": wszystkie,
    }
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


# =========================================================================== całość
def generuj(U=None):
    U = U or wczytaj_uklad()
    wspolne.ZNACZNIKI.clear()
    X0, Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
    s = Scena(U["swiat"]["kontener"], paleta=PALETA)
    rnd = random.Random(U["ziarno"])
    raport = {}
    obrysy = []
    with s.uklad(pos=(X0, 0.0, Z0)):
        n = len(s.czesci)
        teren(s, U)
        raport["Teren"] = len(s.czesci) - n
        raport.update(budynki(s, U, obrysy))
        raport.update(domy(s, U, random.Random(rnd.randint(0, 10 ** 6)), obrysy))
        raport["Stragany"] = stragany(s, U)
        raport["Mury"] = laczniki_i_mury(s, U, random.Random(rnd.randint(0, 10 ** 6)))
        raport["Rekwizyty"] = rekwizyty(s, U, random.Random(rnd.randint(0, 10 ** 6)))
        raport["Kulisy i tło"] = kulisy_i_tlo(s, U, random.Random(rnd.randint(0, 10 ** 6)))
        raport["Niewidzialne"] = niewidzialne(s, U)
        n = len(s.czesci)
        bruk(s, U, random.Random(rnd.randint(0, 10 ** 6)), obrysy)
        raport["Uliczka (bruk)"] = len(s.czesci) - n
        n = len(s.czesci)
        start(s, U)
        raport["Start"] = len(s.czesci) - n
        raport["Uliczka (kody)"] = kody(s, U, X0, Z0)
        g = U["granice"]
        wspolne.znacznik(s, "polaczenie_las", "polaczenie_las", (g["czesci_x"][1], U["poziomy"]["bruk"], 0.0),
                         kier=(1, 0, 0), las_od_X=U["swiat"]["las_od_X"],
                         opis="wschodni brzeg bazaru = początek pasa Lasu (u −34, ściana zamykająca Lasu); Brama Leśna stoi "
                              "7,5 st przed nim")
    return s, raport


def wypisz_raport(s, raport):
    mats = s.materialy
    n = len(s.czesci)
    print("CZĘŚCI: %d (cel ok. %d, twardy limit %d)" % (n, CEL, LIMIT))
    for k in sorted(raport, key=lambda k: -raport[k]):
        print("  %-22s %5d" % (k, raport[k]))
    kule = sum(1 for c in s.czesci if c[0] == KULA)
    walce = sum(1 for c in s.czesci if c[0] == WALEC)
    neon = sum(1 for c in s.czesci if mats[c[12]] == "Neon")
    przezr = sum(1 for c in s.czesci if 0 < c[13] < 1)
    bez_kol = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 1)
    bez_cien = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 2)
    smooth = sum(1 for c in s.czesci if mats[c[12]] == "SmoothPlastic")
    print("SUFITY: kule %d, walce %d, Neon %d, półprzezroczyste %d, z kolizją %.0f%%, bez cienia %.0f%%, SmoothPlastic %.0f%%"
          % (kule, walce, neon, przezr, 100.0 * (n - bez_kol) / n, 100.0 * bez_cien / n, 100.0 * smooth / n))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Generator „Miasteczko jako ciasny bazar”")
    ap.add_argument("--wyj", default=os.path.join(TU, "czesci.json"))
    a = ap.parse_args()
    U = wczytaj_uklad()
    s, raport = generuj(U)
    s.zapisz(a.wyj)
    zapisz_znaczniki(U, os.path.join(TU, "znaczniki.json"), raport)
    wypisz_raport(s, raport)
    if len(s.czesci) > LIMIT:
        print("BŁĄD: przekroczony twardy limit części")
        return 1
    print("ZAPISANO:", os.path.relpath(a.wyj, REPO).replace(os.sep, "/"), "i swiat/miasteczko_bazar/znaczniki.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
