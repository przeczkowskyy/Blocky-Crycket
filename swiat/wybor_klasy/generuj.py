#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scena wyboru klasy w 3D — sala karczmy-zamku z okrągłym podestem, na którym stoją bohaterowie (koło postaci).
    python -B swiat/wybor_klasy/generuj.py            # → czesci.json + efekty.json + ujecia.json

Wersja 2 (polecenie Pawła 16.11.2026: bogatszy wystrój wg referencji karczmy, mocniejsza kreska):
- sala jest OBRÓCONA o OBROT° wokół podestu względem kamery — widać ją „w narożnik”, jak na ilustracji: tylna ściana
  ucieka w lewo, a prawa (kominek, lada z regałem) jest odsłonięta. Lewą ćwiartkę ekranu zasłania karta statystyk,
  środek u góry tabliczka z tytułem, więc bogate rzeczy stoją po prawej i w pasie nad głowami bohaterów;
- kreska: mury z kamieni na ciemnej fudze, podkładki tuszu pod belkami, ramy okna i regału w tuszu, a do tego obrys
  sylwetki (Highlight) dla grup z listy `obrysy` (studio_buduj.py --obrysy);
- światła, snop światła nad podestem i pyłki zapisuje `efekty.json` (układ świata) — stawia je
  tools/studio/deploy_classselect.py w Workspace/WyborKlasy/Efekty.

Układ sali (przed obrotem): środek podestu na podłodze = (0, 0, 0), kamera od strony +Z, tylna ściana na −Z,
prawa ściana na +X. W Studio scena stoi w kontenerze Workspace/WyborKlasy, przesunięta o PRZESUNIECIE.
Zasada zespołu: żadnych liter i skojarzeń z alkoholem — na półkach eliksiry, słoje, kufle, chleb i jabłka.
Projekt: B&C/UI/Selektor bohatera.md. Biblioteka: swiat/biblioteka/scena.py.
"""
import json
import math
import os
import random
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from swiat.biblioteka.scena import Scena, macierz_obrotu, razy_wektor  # noqa: E402

KONTENER = "Workspace/WyborKlasy"
PRZESUNIECIE = (0.0, 400.0, 4000.0)   # świat Studio: sala wysoko i daleko od map (zamknięta, nie widać jej z gry)
GORA_PODESTU = 2.15                   # wysokość blatu podestu nad podłogą — tu stają bohaterowie
KAMERA = ((0.0, 7.5, 21.0), (0.0, 5.5, -3.0))   # ujęcie gracza względem środka podestu (ClassData.Scene)

OBROT = 22.0                 # obrót sali wokół podestu (ry): prawa ściana skręca ku środkowi kadru
W = 23.0                     # połowa szerokości sali
TYL, PRZOD = 27.0, 27.0      # tylna ściana z = −TYL, przednia z = +PRZOD (za kamerą)
WYS = 16.0                   # ściany do okapu
WZNIOS = 11.0                # wznios dachu
COKOL = 5.6                  # kamienny cokół

PALETA = {
    "tusz": "1D1916",
    # kamień — chłodny, fioletowo-szary jak na ilustracji
    "fuga": "2E2936", "kamien": "8F8799", "kamien2": "7A7286", "kamien3": "A9A2B3", "kamien_cien": "5B546A",
    "plyta": "8C8494", "plyta2": "7B7385", "plyta3": "9D96A4", "wneka": "3B3548", "sadza": "241F28",
    # tynk i drewno
    "tynk": "DCC7A2", "tynk2": "C9B28A", "drewno": "8C5A30", "drewno2": "A8703E", "drewno_ciemne": "5A3820",
    "drewno_jasne": "CE9658", "deski": "6E4526", "deski_dachu": "4E3220",
    # metal i złoto
    "zelazo": "3A3840", "stal": "C4CEDD", "zloto": "F2B93C", "zloto2": "C98F2A", "zloto_lam": "F4C650",
    # tkaniny
    "czerwien": "C8322E", "turkus": "1E968E", "fiolet": "7B3FBA", "roz": "D878AA", "granat": "2C4EA8",
    "dywan": "9E2B34", "dywan2": "7A1F2C",
    # noc i światło (Neon)
    "noc": "1F3378", "gwiazda": "FFF4C8", "ksiezyc": "FFEDB0",
    "ogien": "FF7A1C", "ogien2": "FFD24A", "zar": "FF4A14",
    "eliksir_r": "FF4FA0", "eliksir_t": "3FE6D8", "eliksir_z": "7BE84A", "eliksir_f": "B46CFF",
    # rekwizyty
    "swieca": "F6EED8", "beczka": "86522A", "skrzynia": "A87440", "kufel": "CFC8BA", "biel": "FFF6E0",
    "chleb": "C98A48", "ser": "F2C84A", "jablko": "D8382E", "lisc": "4E9E3A", "lisc2": "76BE44", "ksiega1": "8E2F3A", "ksiega2": "2F6A8E",
    "ksiega3": "3E7A44",
    # podest
    "podest": "9C95A4", "podest_gora": "C9C2CC", "podest_srodek": "D6D0D6", "podest_cien": "6A6378",
}

EFEKTY = {"swiatla": [], "snopy": [], "pylki": []}


# --------------------------------------------------------------------------- narzędzia
def swiat(s, pos):
    """Punkt z bieżącego układu lokalnego → układ świata (zaokrąglony)."""
    R, t, sk = s._stos[-1]
    p = razy_wektor(R, pos)
    return [round(t[i] + sk * p[i], 3) for i in range(3)]


def swiatlo(s, nazwa, pos, zasieg, jasnosc, kolor="FFA858", cienie=False, migot=0.0, cel=None, kat=None):
    """Światło w bieżącym układzie: punktowe albo (gdy podasz cel i kąt) reflektor. migot = siła migotania 0–1."""
    d = {"n": nazwa, "p": swiat(s, pos), "zasieg": zasieg, "jasnosc": jasnosc, "kolor": kolor, "cienie": bool(cienie),
         "migot": migot}
    if cel is not None:
        d["cel"], d["kat"] = swiat(s, cel), kat or 45
    EFEKTY["swiatla"].append(d)


_KLINY = []
for _rx in (0, 90, 180, 270):
    for _ry in (0, 90, 180, 270):
        for _rz in (0, 90, 180, 270):
            _R = macierz_obrotu(_rx, _ry, _rz)
            _KLINY.append(((_rx, _ry, _rz),
                           tuple(int(round(v)) for v in razy_wektor(_R, (1, 0, 0))),     # oś wyciągnięcia klina
                           tuple(int(round(v)) for v in razy_wektor(_R, (0, 0, -1))),    # przyprostokątna „głębokość”
                           tuple(int(round(v)) for v in razy_wektor(_R, (0, 1, 0)))))    # przyprostokątna „wysokość”


def trojkat(s, nazwa, rog, dx, dy, z, grub, kolor, mat="SmoothPlastic", alfa=0.0):
    """Trójkąt prostokątny w płaszczyźnie XY (grubość `grub` wzdłuż Z, środek w z): kąt prosty w `rog` = (x, y),
    przyprostokątne idą od niego o dx wzdłuż X i o dy wzdłuż Y (ze znakiem). Obrót klina dobiera sam."""
    sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
    for rot, w, a, b in _KLINY:
        if w[2] == 0:
            continue
        if a == (sx, 0, 0) and b == (0, sy, 0):
            size = (grub, abs(dy), abs(dx))
        elif a == (0, sy, 0) and b == (sx, 0, 0):
            size = (grub, abs(dx), abs(dy))
        else:
            continue
        s.klin(nazwa, (rog[0] + dx / 2.0, rog[1] + dy / 2.0, z), size, kolor, mat, rot, alfa)
        return
    raise RuntimeError("brak orientacji klina")


def kamienie(s, rnd, x0, x1, y0, y1, z=0.0, rzad=1.55, kolory=("kamien", "kamien", "kamien2", "kamien3"), mat="Slate"):
    """Mur z kamieni na licu z (płaszczyzna XY, kamienie wystają ku +z): rzędy z przesunięciem, między nimi ciemna fuga."""
    y, i = y0, 0
    while y + 0.7 < y1:
        h = min(rzad + rnd.uniform(-0.18, 0.18), y1 - y)
        if y1 - (y + h) < 0.7:
            h = y1 - y
        x = x0 - (rnd.uniform(0.6, 2.4) if i % 2 else 0.0)
        while x < x1 - 0.3:
            w = rnd.uniform(2.3, 4.4)
            a, b = max(x, x0), min(x + w, x1)
            if b - a > 0.8:
                g = 0.28 + rnd.uniform(0.0, 0.18)
                s.blok("Kamień", ((a + b) / 2.0, y + h / 2.0, z + g / 2.0), (b - a - 0.26, h - 0.26, g), rnd.choice(kolory), mat)
            x += w
        y += h
        i += 1


def portal(s, rnd, xl, xr, y_sp, y_top, c, t, z0, z1, kolory=("kamien", "kamien2", "kamien3")):
    """Kamienna rama otworu ze ściętymi narożami (klockowy łuk): światło otworu x ∈ [xl, xr], pion do y_sp, skosy `c`
    do y_top. Rama ma grubość t na zewnątrz światła i zajmuje z ∈ [z0, z1]; pod kamieniami ciemny podkład (fuga)."""
    zs, gs = (z0 + z1 - 0.25) / 2.0, (z1 - 0.25 - z0)
    zc, gc = (z0 + z1) / 2.0, z1 - z0
    for xa, xb, kier in ((xl - t, xl, 1), (xr, xr + t, -1)):
        s.blok("Rama podkład", ((xa + xb) / 2.0, (y_top + t) / 2.0, zs), (t, y_top + t, gs), "fuga")
        trojkat(s, "Rama naroże", (xl if kier > 0 else xr, y_top), kier * c, -c, zs, gs, "fuga")
        n = max(2, int(round(y_sp / 1.45)))
        h = (y_sp - 0.1) / n
        for k in range(n):
            szer = t + (0.4 if k % 2 == 0 else 0.0)
            xs = (xl - szer / 2.0 - 0.02) if kier > 0 else (xr + szer / 2.0 + 0.02)
            s.blok("Rama kamień", (xs, 0.1 + h * (k + 0.5), zc), (szer - 0.1, h - 0.16, gc),
                   kolory[(k + (0 if kier > 0 else 1)) % len(kolory)], "Slate")
        dl = c * math.sqrt(2.0)                                 # dwa kamienie na skosie
        for k in range(2):
            u = (k + 0.5) / 2.0
            px = (xl + c * u) if kier > 0 else (xr - c * u)
            py = y_sp + c * u
            ox, oy = (-kier * t / 2.0 / math.sqrt(2.0)), (t / 2.0 / math.sqrt(2.0))
            s.blok("Rama kamień skos", (px + ox, py + oy, zc + 0.04 * (k + 1)), (dl / 2.0 - 0.14, t - 0.1, gc),
                   kolory[(k + 1) % len(kolory)], "Slate", rot=(0, 0, kier * 45))
    s.blok("Rama podkład", ((xl + xr) / 2.0, y_top + t / 2.0, zs), (xr - xl, t, gs), "fuga")
    a, b = xl + c + 0.25, xr - c - 0.25
    zw = 1.5                                                    # zwornik
    for (p, q) in ((a, (a + b) / 2.0 - zw / 2.0), ((a + b) / 2.0 + zw / 2.0, b)):
        if q - p > 0.5:
            s.blok("Rama kamień", ((p + q) / 2.0, y_top + t / 2.0, zc), (q - p - 0.14, t - 0.1, gc), rnd.choice(kolory), "Slate")
    s.blok("Rama zwornik", ((a + b) / 2.0, y_top + t / 2.0 + 0.2, zc + 0.1), (zw - 0.14, t + 0.5, gc + 0.2), "kamien3", "Slate")


# --------------------------------------------------------------------------- podłoga i podest
def podloga(s, rnd):
    with s.grupa("Podloga"):
        s.blok("Podłoga podkład", (0, -0.6, 0), (2 * W + 3, 1.2, TYL + PRZOD + 3), "fuga")
        with s.cechy(cien=False):
            z = -TYL + 0.55
            while z < PRZOD - 1.0:
                gl = rnd.choice((4.2, 4.8, 5.4))
                x = -W + 0.55 - rnd.uniform(0.0, 3.0)
                while x < W - 0.55:
                    sz = rnd.uniform(4.0, 7.0)
                    a, b = max(x, -W + 0.55), min(x + sz, W - 0.55)
                    cx, cz = (a + b) / 2.0, z + gl / 2.0
                    if b - a > 1.2 and math.hypot(cx, cz) > 5.5:
                        h = 0.14 + rnd.uniform(0.0, 0.06)
                        s.blok("Płyta", (cx, h / 2.0, cz), (b - a - 0.32, h, gl - 0.32),
                               rnd.choice(("plyta", "plyta", "plyta2", "plyta3")), "Slate")
                        if rnd.random() < 0.16 and b - a > 3.5:     # pęknięcie narysowane tuszem
                            kat = rnd.uniform(0, 180)
                            px, pz = cx + rnd.uniform(-0.8, 0.8), cz + rnd.uniform(-0.8, 0.8)
                            s.blok("Pęknięcie", (px, h, pz), (1.5, 0.08, 0.13), "tusz", rot=(0, kat, 0))
                            s.blok("Pęknięcie", (px + 0.55 * math.cos(math.radians(kat + 40)), h,
                                                 pz - 0.55 * math.sin(math.radians(kat + 40))), (0.9, 0.08, 0.11), "tusz",
                                   rot=(0, kat + 40, 0))
                    x += sz
                z += gl


def podest(s):
    with s.grupa("Podest"):
        s.walec("Stopień", (0, 0.35, 0), 7.9, 0.7, "podest_cien", "Slate", os="y")
        s.walec("Bęben podkład", (0, 1.25, 0), 7.0, 1.1, "fuga", os="y")
        n = 16
        for i in range(n):                                       # kamienie obwodu — między nimi ciemna fuga
            a = 2 * math.pi * (i + 0.5) / n
            s.blok("Kamień podestu", (7.0 * math.sin(a), 1.25, 7.0 * math.cos(a)), (2.45, 0.92, 0.6),
                   "podest" if i % 3 else "kamien3", "Slate", rot=(0, math.degrees(a), 0))
        s.walec("Rant tusz", (0, 1.8, 0), 7.3, 0.14, "tusz", os="y")
        s.walec("Złota obwódka", (0, 1.98, 0), 7.05, 0.22, "zloto", os="y")
        s.walec("Blat tusz", (0, 2.02, 0), 6.5, 0.2, "tusz", os="y")
        s.walec("Blat podestu", (0, 2.05, 0), 6.32, 0.2, "podest_gora", "Slate", os="y")
        with s.cechy(cien=False):
            s.walec("Pierścień złoty", (0, 2.11, 0), 4.05, 0.1, "zloto2", os="y")
            s.walec("Środek podestu", (0, 2.12, 0), 3.85, 0.1, "podest_srodek", "Slate", os="y")
    s.obrys_sylwetki("Podest")


# --------------------------------------------------------------------------- ściany (układ ściany: lico z = 0, +z do wnętrza)
def mur(s, rnd, x0, x1, bogaty=True):
    cx, dl = (x0 + x1) / 2.0, x1 - x0
    with s.grupa("Mury"):
        s.blok("Mur cokół", (cx, COKOL / 2.0, -0.7), (dl, COKOL, 1.4), "fuga")
        s.blok("Mur tynk", (cx, (COKOL + WYS) / 2.0, -0.75), (dl, WYS - COKOL, 1.3), "tynk", "Plaster")
        if bogaty:
            kamienie(s, rnd, x0, x1, 0.32, COKOL - 0.08)
        else:
            s.blok("Mur kamień", (cx, COKOL / 2.0 + 0.1, 0.15), (dl - 0.2, COKOL - 0.5, 0.3), "kamien2", "Slate")


def cegly(s, rnd, x, y, n=3):
    """Łata odsłoniętych cegieł na tynku (jak na ilustracji): kilka cegieł na podkładce tuszu. (x, y) = lewy dół."""
    with s.grupa("Mury"), s.cechy(cien=False):
        uklad = (((0, 0), (1.55, 0), (0.75, 0.7)), ((0, 0), (0.8, 0.7), (2.3, 0.7)), ((0.4, 0), (1.95, 0), (0, 0.7), (1.5, 0.7)))
        for k, (dx, dy) in enumerate(rnd.choice(uklad)[:n + 1]):
            s.blok("Cegła tusz", (x + dx + 0.7, y + dy + 0.3, -0.02), (1.62, 0.76, 0.16), "tusz")
            s.blok("Cegła", (x + dx + 0.7, y + dy + 0.3, 0.06), (1.38, 0.52, 0.2), ("kamien3", "kamien", "tynk2")[k % 3], "Slate")


def girlanda(s, x0, x1, y, z, n=9):
    """Girlanda liści z jagodami (akcent zieleni jak na referencji): rząd kul wzdłuż X."""
    with s.cechy(kolizja=False, cien=False):
        for k in range(n):
            u = k / float(n - 1)
            px = x0 + (x1 - x0) * u
            py = y - 0.55 * math.sin(math.pi * u) + (0.18 if k % 2 else 0.0)
            s.kula("Liście", (px, py, z + (0.15 if k % 3 == 0 else 0.0)), (1.25, 1.0, 1.4)[k % 3], ("lisc", "lisc2", "lisc")[k % 3])
            if k % 3 == 1:
                s.kula("Jagoda", (px + 0.3, py - 0.35, z + 0.45), 0.36, "jablko")


def szkielet(s, slupy, rygle, x0, x1, zastrzaly=()):
    """Belki ściany: słupy (lista x), rygiel dolny i gzyms cokołu w odcinkach `rygle`, oczep na całej długości, zastrzały
    (x słupa, kierunek ±1). Każda belka ma z tyłu szerszą podkładkę tuszu — to jest kreska."""
    cx, dl = (x0 + x1) / 2.0, x1 - x0
    with s.grupa("Szkielet"):
        for x in slupy:
            s.blok("Słup", (x, WYS / 2.0, 0.45), (1.4, WYS, 1.1), "drewno", "Wood")
            s.blok("Słup tusz", (x, WYS / 2.0, 0.2), (1.95, WYS, 0.6), "tusz")
            s.blok("Słup stopa", (x, 0.75, 0.62), (2.2, 1.5, 1.5), "kamien3", "Slate")
            s.blok("Słup stopa tusz", (x, 0.87, 0.5), (2.6, 1.74, 1.4), "tusz")
        for (a, b) in rygle:
            s.blok("Gzyms cokołu", ((a + b) / 2.0, COKOL + 0.25, 0.27), (b - a, 0.5, 0.95), "kamien3", "Slate")
            s.blok("Rygiel", ((a + b) / 2.0, COKOL + 0.95, 0.3), (b - a, 0.9, 0.8), "drewno", "Wood")
            s.blok("Rygiel tusz", ((a + b) / 2.0, COKOL + 1.06, 0.12), (b - a, 1.12, 0.45), "tusz")
        s.blok("Oczep", (cx, WYS - 0.55, 0.35), (dl, 1.1, 0.9), "drewno", "Wood")
        s.blok("Oczep tusz", (cx, WYS - 0.66, 0.15), (dl, 1.32, 0.52), "tusz")
        for (x, k) in zastrzaly:
            p1, p2 = (x + k * 0.7, WYS - 5.0, 0.32), (x + k * 3.9, WYS - 1.1, 0.32)
            s.belka("Zastrzał", p1, p2, 0.8, "drewno2", "Wood", szer=0.66)
            s.belka("Zastrzał tusz", (p1[0], p1[1], 0.14), (p2[0], p2[1], 0.14), 1.24, "tusz", "SmoothPlastic", szer=0.3)


def pochodnia(s, nazwa, migot=0.22):
    """Pochodnia na ścianie: (0, 0, 0) = punkt na licu (albo na słupie), +z do wnętrza."""
    with s.grupa("Pochodnie"), s.cechy(kolizja=False):
        s.blok(nazwa + " okucie", (0, 0, 0.14), (1.0, 2.0, 0.28), "zelazo", "Metal")
        s.blok(nazwa + " obejma", (0, 0.1, 0.7), (0.85, 0.5, 1.0), "zelazo", "Metal")
        kat, dl = 26.0, 3.0
        with s.uklad(pos=(0, -0.7, 0.75), obrot=(kat, 0, 0)):
            s.walec(nazwa + " trzonek", (0, dl / 2.0, 0), 0.27, dl, "drewno2", "Wood", os="y")
            s.walec(nazwa + " kosz", (0, dl - 0.2, 0), 0.52, 0.7, "zelazo", "Metal", os="y")
        ty, tz = -0.7 + dl * math.cos(math.radians(kat)), 0.75 + dl * math.sin(math.radians(kat))
        with s.grupa("Plomienie"), s.cechy(kolizja=False, cien=False):
            s.kula(nazwa + " płomień", (0, ty + 0.55, tz), 1.25, "ogien", "Neon", alfa=0.25)
            s.kula(nazwa + " płomień", (0.05, ty + 1.2, tz), 0.85, "ogien", "Neon", alfa=0.25)
            s.kula(nazwa + " płomień", (-0.05, ty + 1.72, tz), 0.48, "ogien", "Neon", alfa=0.2)
            s.kula(nazwa + " żar", (0, ty + 0.5, tz), 0.78, "ogien2", "Neon")
            s.kula(nazwa + " żar", (0.03, ty + 1.05, tz), 0.42, "ogien2", "Neon")
        swiatlo(s, nazwa, (0, ty + 0.9, tz + 0.4), 14, 0.4, "FFA050", migot=migot)


def choragiew(s, nazwa, kolor, szer=3.2, dl=6.4, znak="zloto_lam"):
    """Chorągiew: (0, 0, 0) = środek drążka, płat wisi w dół w płaszczyźnie XY, lico ku +z. Złota lamówka i znak."""
    with s.grupa("Choragwie"), s.cechy(kolizja=False):
        zab, m = 1.5, 0.3
        s.walec(nazwa + " drążek", (0, 0, 0), 0.22, szer + 1.2, "drewno_ciemne", "Wood", os="x")
        for d in (-1, 1):
            s.kula(nazwa + " gałka", (d * (szer / 2.0 + 0.6), 0, 0), 0.62, "zloto")
        y0 = -0.15
        s.blok(nazwa + " lamówka", (0, y0 - dl / 2.0, 0), (szer, dl, 0.2), "zloto_lam", "Fabric")
        s.blok(nazwa, (0, y0 - dl / 2.0, 0.1), (szer - 2 * m, dl, 0.2), kolor, "Fabric")
        lx = szer / 2.0 - m - 0.3
        ly = zab * lx / (szer / 2.0)
        for d in (-1, 1):
            trojkat(s, nazwa + " ząb lamówka", (d * szer / 2.0, y0 - dl), -d * szer / 2.0, -zab, 0, 0.2, "zloto_lam", "Fabric")
            trojkat(s, nazwa + " ząb", (d * (szer / 2.0 - m), y0 - dl), -d * lx, -ly, 0.1, 0.2, kolor, "Fabric")
        with s.cechy(cien=False):
            s.blok(nazwa + " znak", (0, y0 - dl * 0.42, 0.22), (1.15, 1.15, 0.1), znak, "Fabric", rot=(0, 0, 45))
            s.blok(nazwa + " pas", (0, y0 - 0.55, 0.22), (szer - 2 * m, 0.35, 0.1), znak, "Fabric")


def okno(s):
    """Potrójne okno z nocnym niebem na tylnej ścianie: (0, 0, 0) = środek dołu kamiennej oprawy na licu tynku."""
    with s.grupa("Okno"), s.cechy(kolizja=False):
        szer, wys = 11.2, 6.4
        s.blok("Okno tusz", (0, wys / 2.0, 0.02), (szer + 0.7, wys + 0.7, 0.25), "tusz")
        s.blok("Okno oprawa", (0, wys / 2.0, 0.2), (szer, wys, 0.4), "kamien3", "Slate")
        s.blok("Parapet tusz", (0, -0.18, 0.5), (szer + 1.9, 0.5, 1.3), "tusz")
        s.blok("Parapet", (0, -0.12, 0.62), (szer + 1.5, 0.62, 1.4), "kamien", "Slate")
        pw, ph, y0 = 2.5, 3.1, 0.9
        with s.cechy(cien=False):
            for k in (-1, 0, 1):
                x = k * 3.35
                s.blok("Szyba tusz", (x, y0 + ph / 2.0, 0.42), (pw + 0.56, ph + 0.3, 0.14), "tusz")
                s.walec("Szyba tusz łuk", (x, y0 + ph, 0.42), pw / 2.0 + 0.28, 0.14, "tusz", os="z")
                s.blok("Szyba", (x, y0 + ph / 2.0, 0.5), (pw, ph, 0.14), "noc", "Neon")
                s.walec("Szyba łuk", (x, y0 + ph, 0.5), pw / 2.0, 0.14, "noc", "Neon", os="z")
                s.blok("Szpros", (x, y0 + ph, 0.6), (pw, 0.22, 0.1), "tusz")
                s.blok("Szpros", (x, y0 + ph / 2.0, 0.6), (0.2, ph, 0.1), "tusz")
            rnd = random.Random(3)
            for k in (-1, 0, 1):
                for _ in range(4):
                    gx, gy = k * 3.35 + rnd.choice((-0.75, -0.55, 0.55, 0.75)), y0 + rnd.uniform(0.4, ph + 0.5)
                    a = rnd.choice((0.16, 0.2, 0.26))
                    s.blok("Gwiazda", (gx, gy, 0.6), (a, a, 0.1), "gwiazda", "Neon", rot=(0, 0, 45))
            s.walec("Księżyc", (0.6, y0 + ph + 0.45, 0.63), 0.72, 0.1, "ksiezyc", "Neon", os="z")
            s.walec("Księżyc cień", (0.92, y0 + ph + 0.63, 0.68), 0.58, 0.1, "noc", "Neon", os="z")
        swiatlo(s, "Księżyc okna", (0, 3.6, 3.2), 20, 1.3, "7FA8FF")
    s.obrys_sylwetki("Okno")


# --------------------------------------------------------------------------- rekwizyty (układ własny, y = 0 na podłodze)
def beczka(s, nazwa, pos, r=1.5, h=3.5, lezy=False, jablka=False, ry=0.0):
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        if lezy:
            s.walec(nazwa, (0, r + 0.15, 0), r, h, "beczka", "Wood", os="x")
            s.walec(nazwa + " brzuch", (0, r + 0.15, 0), r + 0.16, h * 0.42, "beczka", "Wood", os="x")
            for d in (-1, 1):
                s.walec(nazwa + " obręcz", (d * h * 0.36, r + 0.15, 0), r + 0.2, 0.3, "zelazo", os="x")
                s.walec(nazwa + " dno", (d * (h / 2.0 + 0.03), r + 0.15, 0), r - 0.22, 0.1, "drewno_jasne", "Wood", os="x")
                s.blok(nazwa + " klin", (d * h * 0.3, 0.3, 0), (0.6, 0.6, 2 * r + 0.3), "drewno_ciemne", "Wood")
        else:
            s.walec(nazwa, (0, h / 2.0, 0), r, h, "beczka", "Wood", os="y")
            s.walec(nazwa + " brzuch", (0, h / 2.0, 0), r + 0.16, h * 0.42, "beczka", "Wood", os="y")
            for d in (0.16, 0.84):
                s.walec(nazwa + " obręcz", (0, h * d, 0), r + 0.2, 0.3, "zelazo", os="y")
            s.walec(nazwa + " wieko", (0, h + 0.03, 0), r - 0.22, 0.1, "drewno_jasne", "Wood", os="y")
            if jablka:
                with s.cechy(kolizja=False, cien=False):
                    for k, (ax, az) in enumerate(((0, 0), (0.55, 0.2), (-0.5, 0.3), (0.1, -0.55), (-0.3, -0.35))):
                        s.kula(nazwa + " jabłko", (ax, h + 0.28 + (0.3 if k == 0 else 0.0), az), 0.62, "jablko")


def skrzynia(s, nazwa, pos, a=3.0, ry=0.0):
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.blok(nazwa, (0, a / 2.0, 0), (a, a, a), "skrzynia", "WoodPlanks")
        g = 0.42
        for dx in (-1, 1):
            for dz in (-1, 1):
                s.blok(nazwa + " narożnik", (dx * (a / 2.0 - g / 2.0 + 0.09), a / 2.0, dz * (a / 2.0 - g / 2.0 + 0.09)),
                       (g, a + 0.12, g), "drewno_ciemne", "Wood")
        for yy in (g / 2.0 - 0.02, a - g / 2.0 + 0.02):
            s.blok(nazwa + " rama", (0, yy, 0), (a + 0.1, g, a + 0.1), "drewno_ciemne", "Wood")
        k = a / 2.0 - g
        s.belka(nazwa + " ukos", (-k, g, a / 2.0 + 0.04), (k, a - g, a / 2.0 + 0.04), 0.4, "drewno_ciemne", "Wood", szer=0.14)
        s.belka(nazwa + " ukos", (a / 2.0 + 0.04, g, k), (a / 2.0 + 0.04, a - g, -k), 0.4, "drewno_ciemne", "Wood", szer=0.14)


def stolek(s, pos, h=2.5, faza=0.0):
    x, y, z = pos
    s.walec("Stołek siedzisko", (x, y + h, z), 1.05, 0.45, "drewno2", "Wood", os="y")
    s.walec("Stołek rant", (x, y + h - 0.28, z), 1.14, 0.14, "tusz", os="y")
    for k in range(3):
        a = 2 * math.pi * k / 3.0 + faza
        s.belka("Stołek noga", (x + 0.4 * math.cos(a), y + h - 0.2, z + 0.4 * math.sin(a)),
                (x + 1.0 * math.cos(a), y, z + 1.0 * math.sin(a)), 0.34, "drewno", "Wood")


def swieca(s, nazwa, pos, h=0.9, r=0.2, jasnosc=None):
    x, y, z = pos
    s.walec(nazwa, (x, y + h / 2.0, z), r, h, "swieca", os="y")
    with s.grupa("Plomienie"), s.cechy(kolizja=False, cien=False):
        s.kula(nazwa + " płomień", (x, y + h + 0.24, z), 0.4, "ogien2", "Neon")
        s.kula(nazwa + " płomień", (x, y + h + 0.5, z), 0.22, "ogien", "Neon")
    if jasnosc:
        swiatlo(s, nazwa, (x, y + h + 0.6, z), 9, jasnosc * 0.5, "FFC070", migot=0.15)


def eliksir(s, pos, kolor, r=0.42, neon=False):
    x, y, z = pos
    mat = "Neon" if neon else "SmoothPlastic"
    s.kula("Eliksir", (x, y + r, z), 2 * r, kolor, mat)
    s.walec("Eliksir szyjka", (x, y + 2 * r + 0.12, z), 0.15, 0.42, kolor, mat, os="y")
    s.walec("Eliksir korek", (x, y + 2 * r + 0.4, z), 0.19, 0.18, "drewno_jasne", os="y")


def sloj(s, pos, kolor, r=0.45, h=0.95):
    x, y, z = pos
    s.walec("Słój", (x, y + h / 2.0, z), r, h, kolor, os="y")
    s.walec("Słój wieko", (x, y + h + 0.08, z), r + 0.06, 0.16, "drewno", "Wood", os="y")


def kufel(s, pos, ry=0.0):
    x, y, z = pos
    s.walec("Kufel", (x, y + 0.45, z), 0.4, 0.9, "kufel", os="y")
    s.walec("Kufel rant", (x, y + 0.86, z), 0.45, 0.12, "biel", os="y")
    a = math.radians(ry)
    s.blok("Kufel ucho", (x + 0.52 * math.cos(a), y + 0.45, z + 0.52 * math.sin(a)), (0.3, 0.5, 0.16), "kufel", rot=(0, -ry, 0))


def ksiazki(s, pos, n=3):
    x, y, z = pos
    kol = ("ksiega1", "ksiega2", "ksiega3", "fiolet", "zloto2")
    for k in range(n):
        h = (1.25, 1.05, 1.4, 1.15)[k % 4]
        s.blok("Księga", (x + k * 0.36, y + h / 2.0, z), (0.3, h, 0.85), kol[k % len(kol)])


# --------------------------------------------------------------------------- tylna ściana
AX0, AX1 = -10.2, -1.6        # otwór wnęki w tylnej ścianie (razem z ramą)
OKNO_X = 11.0


def sciana_tylna(s, rnd):
    mur(s, rnd, -W - 1.4, AX0)
    mur(s, rnd, AX1, W + 1.4)
    with s.grupa("Mury"):
        s.blok("Mur nad wnęką", ((AX0 + AX1) / 2.0, (9.6 + WYS) / 2.0, -0.75), (AX1 - AX0, WYS - 9.6, 1.3), "tynk", "Plaster")
    szkielet(s, (-W + 0.7, -16.6, AX0 - 0.75, AX1 + 0.75, 4.4, 17.6, W - 0.7),
             ((-W, AX0 - 0.05), (AX1 + 0.05, W)), -W, W, zastrzaly=((-16.6, -1), (-16.6, 1), (W - 0.7, -1)))
    # --- wnęka z beczkami (prawdziwa głębia)
    with s.grupa("Wneka"):
        gl = 7.5
        cx, sz = (AX0 + AX1) / 2.0, AX1 - AX0
        s.blok("Wnęka podłoga", (cx, -0.6, -gl / 2.0 - 0.5), (sz + 2, 1.2, gl + 1.0), "fuga")
        s.blok("Wnęka płyta", (cx, 0.08, -gl / 2.0 - 0.6), (sz - 0.5, 0.16, gl - 1.0), "plyta2", "Slate")
        s.blok("Wnęka tył", (cx, 5.2, -gl - 1.4), (sz + 2, 10.6, 1.0), "wneka")
        for d in (-1, 1):
            s.blok("Wnęka bok", (cx + d * (sz / 2.0 + 0.5), 5.2, -gl / 2.0 - 1.4), (1.0, 10.6, gl - 0.9), "wneka")
        s.blok("Wnęka strop", (cx, 10.1, -gl / 2.0 - 0.7), (sz + 2, 1.0, gl + 1.4), "wneka")
        kamienie(s, rnd, AX0 + 0.2, AX1 - 0.2, 0.3, 9.4, z=-gl - 0.9, kolory=("kamien_cien", "kamien_cien", "kamien2"))
        portal(s, rnd, AX0 + 1.05, AX1 - 1.05, 5.6, 8.0, 2.3, 1.05, -1.4, 0.5)
        beczka(s, "Beczka wnęki", (cx - 1.5, 0.16, -5.0), 1.5, 3.5, jablka=True)
        beczka(s, "Beczka wnęki 2", (cx + 1.7, 0.16, -5.4), 1.35, 3.1)
        beczka(s, "Beczka leżąca", (cx + 0.2, 0.16, -2.6), 1.15, 2.7, lezy=True, ry=8)
        with s.cechy(kolizja=False):
            s.blok("Latarenka wnęki hak", (cx + 0.4, 9.0, -3.6), (0.16, 1.3, 0.16), "zelazo", "Metal")
            s.blok("Latarenka wnęki daszek", (cx + 0.4, 8.25, -3.6), (1.0, 0.25, 1.0), "zelazo", "Metal")
            s.blok("Latarenka wnęki dno", (cx + 0.4, 7.15, -3.6), (0.9, 0.2, 0.9), "zelazo", "Metal")
            with s.grupa("Plomienie"), s.cechy(cien=False):
                s.blok("Latarenka wnęki światło", (cx + 0.4, 7.7, -3.6), (0.7, 0.9, 0.7), "ogien2", "Neon")
        swiatlo(s, "Latarenka wnęki", (cx + 0.4, 7.2, -3.4), 11, 0.45, "FFB060", migot=0.1)
    s.obrys_sylwetki("Wneka")
    # --- okno z księżycem, chorągwie, pochodnie na słupach
    with s.uklad(pos=(OKNO_X, 7.55, -0.1)):
        okno(s)
    with s.uklad(pos=(1.4, 14.3, 0.75)):
        choragiew(s, "Chorągiew czerwona", "czerwien", 3.0, 5.6)
    with s.uklad(pos=(20.4, 14.3, 0.75)):
        choragiew(s, "Chorągiew turkusowa", "turkus", 3.0, 5.6)
    with s.uklad(pos=(-13.4, 14.3, 0.75)):
        choragiew(s, "Chorągiew różowa", "roz", 3.2, 6.0)
    for i, x in enumerate((4.4, 17.6, -16.6)):
        with s.uklad(pos=(x, 9.6, 1.0)):
            pochodnia(s, "Pochodnia T%d" % i)
    for (x, y) in ((-0.2, 8.2), (19.0, 7.6), (-21.6, 11.0), (-14.6, 7.7), (20.6, 14.0 - 6.9)):
        cegly(s, rnd, x, y)
    # --- lewy róg (widać go tylko na szerokich ekranach): beczki i skrzynia
    with s.grupa("Beczki"):
        beczka(s, "Beczka rogu", (-19.5, 0.16, 3.2), 1.6, 3.7, ry=20)
        beczka(s, "Beczka rogu 2", (-16.2, 0.16, 2.6), 1.35, 3.1, jablka=True)
    with s.grupa("Skrzynie"):
        skrzynia(s, "Skrzynia rogu", (-13.0, 0.16, 2.8), 2.8, ry=-12)


# --------------------------------------------------------------------------- prawa ściana: kominek i lada z regałem
KOMINEK_X = -14.0             # w układzie prawej ściany x = z sali
LADA_X0, LADA_X1 = -5.6, 4.6


def kominek(s, rnd):
    """Kominek w układzie ściany: (0, 0, 0) = środek na licu ściany przy podłodze, +z do wnętrza."""
    D, MH = 3.4, 7.6
    with s.grupa("Kominek"):
        for d in (-1, 1):
            s.blok("Kominek filar", (d * 5.0, MH / 2.0, D / 2.0), (2.0, MH, D), "fuga")
        s.blok("Kominek nadproże", (0, (6.5 + MH) / 2.0, D / 2.0), (8.0, MH - 6.5, D), "fuga")
        s.blok("Kominek tył", (0, 3.3, 0.45), (8.0, 6.6, 0.9), "sadza")
        portal(s, rnd, -2.9, 2.9, 3.4, 5.4, 2.0, 1.1, 0.9, D + 0.3)
        for d in (-1, 1):
            kamienie(s, rnd, d * 5.0 - 1.0, d * 5.0 + 1.0, 0.5, MH - 0.3, z=D, rzad=1.5)
        kamienie(s, rnd, -4.0, 4.0, 6.65, MH - 0.3, z=D, rzad=1.2)
        with s.uklad(pos=(6.0, 0, D / 2.0), obrot=(0, 90, 0)):      # bok od strony kamery
            kamienie(s, rnd, -D / 2.0, D / 2.0, 0.5, MH - 0.3, z=0.0, rzad=1.5)
        s.blok("Palenisko płyta tusz", (0, 0.2, D / 2.0 + 0.95), (13.7, 0.4, D + 2.3), "tusz")
        s.blok("Palenisko płyta", (0, 0.27, D / 2.0 + 0.85), (13.2, 0.54, D + 1.7), "kamien3", "Slate")
        # gzyms z cieniem tuszu i wspornikami
        s.blok("Gzyms tusz", (0, MH - 0.12, D / 2.0 + 0.35), (13.6, 0.36, D + 0.75), "tusz")
        s.blok("Gzyms", (0, MH + 0.5, D / 2.0 + 0.5), (14.2, 0.9, D + 1.1), "drewno2", "Wood")
        for d in (-1, 1):
            s.blok("Wspornik", (d * 5.9, MH - 0.75, D + 0.55), (0.9, 1.0, 0.7), "drewno", "Wood")
        # komin zwężający się ku górze
        KD = MH + 5.6                                            # góra dolnego członu komina
        s.blok("Komin dół", (0, (MH + 0.9 + KD) / 2.0, 1.3), (9.2, KD - MH - 0.9, 2.6), "kamien2", "Slate")
        for d in (-1, 1):
            trojkat(s, "Komin ramię", (d * 3.4, KD), d * 1.2, 1.9, 1.1, 2.2, "kamien2", "Slate")
            s.blok("Komin narożnik", (d * 4.35, (MH + 0.9 + KD) / 2.0, 1.42), (0.7, KD - MH - 1.3, 2.6), "kamien3", "Slate")
        s.blok("Komin góra", (0, (KD + WYS + 4.0) / 2.0, 1.1), (6.8, WYS + 4.0 - KD, 2.2), "kamien2", "Slate")
        s.blok("Komin tusz", (0, KD + 0.05, 1.35), (9.5, 0.3, 2.8), "tusz")
        kamienie(s, rnd, -3.3, 3.3, KD + 0.5, WYS + 1.0, z=2.2, rzad=1.7, kolory=("kamien", "kamien3"))
        # polana
        for (lx, ly, lz, rr) in ((-0.2, 0.95, 1.7, 8), (0.3, 0.95, 2.6, -10), (0.0, 1.6, 2.15, 4)):
            s.walec("Polano", (lx, ly, lz), 0.42, 3.6, "drewno_ciemne", "Wood", os="x", rot=(0, rr, 0))
        # na gzymsie
        swieca(s, "Świeca gzymsu", (-5.6, MH + 0.95, D + 0.1), 1.1, 0.22)
        swieca(s, "Świeca gzymsu 2", (-4.9, MH + 0.95, D + 0.4), 0.7, 0.22)
        eliksir(s, (5.2, MH + 0.95, D + 0.2), "eliksir_z", 0.45, neon=True)
        sloj(s, (4.0, MH + 0.95, D + 0.1), "kufel", 0.5, 1.0)
        ksiazki(s, (-3.4, MH + 0.95, D - 0.2), 3)
    with s.grupa("Plomienie"), s.cechy(kolizja=False, cien=False):
        for (fx, fy, fz, fd) in ((0, 1.9, 2.1, 2.5), (-0.55, 2.95, 2.1, 1.7), (0.45, 3.6, 2.1, 1.1), (-0.1, 4.25, 2.1, 0.62)):
            s.kula("Ogień kominka", (fx, fy, fz), fd, "ogien", "Neon", alfa=0.25)
        s.kula("Ogień kominka żar", (0, 1.75, 2.1), 1.6, "ogien2", "Neon")
        s.kula("Ogień kominka żar", (-0.35, 2.7, 2.1), 0.95, "ogien2", "Neon")
        for (fx, fz) in ((-1.5, 2.9), (1.4, 2.5), (0.6, 3.2)):
            s.kula("Żar", (fx, 0.75, fz), 0.5, "zar", "Neon")
    swiatlo(s, "Kominek", (0, 2.6, D + 1.6), 30, 1.1, "FF8A3C", cienie=True, migot=0.3)
    # tarcza ze skrzyżowanymi mieczami na kominie
    with s.grupa("Tarcza"), s.cechy(kolizja=False), s.uklad(pos=(0, MH + 3.25, 2.6)):
        for d in (-1, 1):
            with s.uklad(obrot=(0, 0, d * 42)):
                s.blok("Miecz głownia", (0, 0.5, 0.2), (0.42, 4.8, 0.14), "stal")
                s.blok("Miecz jelec", (0, -1.9, 0.26), (1.5, 0.3, 0.24), "zloto")
                s.blok("Miecz rękojeść", (0, -2.5, 0.24), (0.3, 1.0, 0.22), "drewno_ciemne")
                s.kula("Miecz głowica", (0, -3.1, 0.24), 0.5, "zloto")
        s.walec("Tarcza tusz", (0, 0, 0.42), 1.75, 0.14, "tusz", os="z")
        s.walec("Tarcza rant", (0, 0, 0.5), 1.55, 0.2, "zloto", os="z")
        s.walec("Tarcza pole", (0, 0, 0.56), 1.22, 0.2, "czerwien", os="z")
        s.blok("Tarcza pas", (0, 0, 0.66), (0.5, 2.3, 0.1), "zloto_lam")
        s.kula("Tarcza guz", (0, 0, 0.7), 0.6, "zloto")
    s.obrys_sylwetki("Kominek")
    s.obrys_sylwetki("Tarcza")


def regal_i_lada(s):
    """Regał na ścianie i lada przed nim (układ prawej ściany). Na półkach: eliksiry, słoje, kufle, chleb, ser, księgi."""
    cx, dl = (LADA_X0 + LADA_X1) / 2.0, LADA_X1 - LADA_X0
    polki = (8.0, 10.4, 12.8)
    with s.grupa("Regal"), s.cechy(kolizja=False):
        s.blok("Regał tusz", (cx, 10.9, 0.0), (dl + 1.0, 7.9, 0.3), "tusz")
        s.blok("Regał plecy", (cx, 10.9, 0.12), (dl + 0.4, 7.3, 0.3), "deski", "WoodPlanks")
        for d in (-1, 1):
            s.blok("Regał bok", (cx + d * (dl / 2.0 + 0.05), 10.9, 0.8), (0.5, 7.5, 1.5), "drewno", "Wood")
        s.blok("Regał daszek", (cx, 14.75, 0.85), (dl + 1.3, 0.5, 1.8), "drewno2", "Wood")
        girlanda(s, LADA_X0 - 0.2, LADA_X1 + 0.2, 14.6, 1.9)
        for y in polki:
            s.blok("Półka", (cx, y - 0.18, 0.85), (dl + 0.1, 0.36, 1.5), "drewno2", "Wood")
            s.blok("Półka tusz", (cx, y - 0.45, 0.75), (dl + 0.1, 0.18, 1.4), "tusz")
        z = 0.95
        x = LADA_X0 + 0.9
        # dolna półka
        kufel(s, (x, polki[0], z), 40)
        kufel(s, (x + 1.1, polki[0], z + 0.1), 120)
        for k in range(4):
            s.walec("Talerz", (x + 2.5, polki[0] + 0.07 + 0.13 * k, z), 0.62, 0.11, "biel", os="y")
        s.walec("Chleb", (x + 4.2, polki[0] + 0.42, z), 0.42, 1.3, "chleb", os="x")
        trojkat(s, "Ser", (x + 5.2, polki[0]), 0.9, 0.75, z, 0.8, "ser")
        sloj(s, (x + 6.9, polki[0], z), "eliksir_t", 0.48, 1.05)
        kufel(s, (x + 8.2, polki[0], z), 60)
        # środkowa półka
        for k, (dx, kol, neon) in enumerate(((0.0, "eliksir_r", True), (1.1, "eliksir_t", False), (2.2, "eliksir_f", True))):
            eliksir(s, (x + dx, polki[1], z), kol, 0.42 if k != 1 else 0.5, neon)
        sloj(s, (x + 3.7, polki[1], z), "ser", 0.5, 1.1)
        ksiazki(s, (x + 4.9, polki[1], z), 4)
        eliksir(s, (x + 7.3, polki[1], z), "eliksir_z", 0.48, True)
        sloj(s, (x + 8.4, polki[1], z), "kufel", 0.45, 0.9)
        # górna półka
        sloj(s, (x + 0.2, polki[2], z), "roz", 0.5, 1.0)
        eliksir(s, (x + 1.5, polki[2], z), "eliksir_f", 0.45, False)
        s.walec("Kosz", (x + 3.4, polki[2] + 0.3, z), 0.75, 0.6, "drewno_jasne", "Wood", os="y")
        with s.cechy(cien=False):
            for (ax, az) in ((-0.3, 0.1), (0.3, -0.1), (0.0, 0.3)):
                s.kula("Jabłko", (x + 3.4 + ax, polki[2] + 0.75, z + az), 0.55, "jablko")
        ksiazki(s, (x + 5.0, polki[2], z), 3)
        eliksir(s, (x + 6.9, polki[2], z), "eliksir_t", 0.42, True)
        sloj(s, (x + 8.1, polki[2], z), "zloto2", 0.42, 0.85)
    with s.grupa("Lada"):
        zl = 5.3                                                 # oś lady: 5,3 studa od ściany
        s.blok("Lada korpus", (cx, 1.9, zl), (dl, 3.8, 2.0), "deski", "WoodPlanks")
        s.blok("Lada cokół tusz", (cx, 0.25, zl), (dl + 0.3, 0.5, 2.3), "tusz")
        n = 5
        for k in range(n):                                       # płyciny frontu
            px = LADA_X0 + dl * (k + 0.5) / n
            s.blok("Lada płycina", (px, 2.05, zl + 1.06), (dl / n - 0.5, 2.6, 0.2), "drewno", "Wood")
        s.blok("Lada płycina bok", (LADA_X1 + 0.06, 2.05, zl), (0.2, 2.6, 1.3), "drewno", "Wood")
        s.blok("Lada blat tusz", (cx, 3.75, zl + 0.1), (dl + 1.0, 0.24, 3.1), "tusz")
        s.blok("Lada blat", (cx, 4.1, zl + 0.1), (dl + 1.3, 0.5, 3.4), "drewno2", "Wood")
        b = 4.35
        with s.cechy(kolizja=False):
            kufel(s, (LADA_X0 + 1.0, b, zl + 0.3), 30)
            kufel(s, (LADA_X0 + 2.1, b, zl - 0.2), 150)
            s.walec("Talerz lady", (cx + 0.2, b + 0.07, zl + 0.3), 0.85, 0.14, "biel", os="y")
            s.walec("Chleb lady", (cx + 0.2, b + 0.5, zl + 0.3), 0.42, 1.25, "chleb", os="x", rot=(0, 25, 0))
            s.walec("Misa", (LADA_X1 - 1.5, b + 0.25, zl + 0.1), 0.85, 0.5, "drewno_jasne", "Wood", os="y")
            with s.cechy(cien=False):
                for (ax, az) in ((-0.35, 0.1), (0.3, -0.15), (0.0, 0.35), (0.02, 0.0)):
                    s.kula("Jabłko lady", (LADA_X1 - 1.5 + ax, b + (0.95 if ax == 0.02 else 0.62), zl + 0.1 + az), 0.58, "jablko")
            swieca(s, "Świeca lady", (cx - 2.2, b, zl + 0.5), 0.9, 0.2, jasnosc=0.7)
    with s.grupa("Stolki"):
        for k, px in enumerate((LADA_X0 + 1.4, cx + 0.3, LADA_X1 - 1.0)):
            stolek(s, (px, 0.16, 8.3 + (0.4 if k == 1 else 0.0)), 2.7, faza=0.7 * k)
    # latarnie na wysięgnikach nad ladą
    with s.grupa("Latarnie"), s.cechy(kolizja=False):
        for k, px in enumerate((LADA_X0 + 1.6, LADA_X1 - 1.4)):
            s.blok("Wysięgnik", (px, 15.3, 2.8), (0.5, 0.5, 5.6), "drewno_ciemne", "Wood")
            s.belka("Wysięgnik zastrzał", (px, 13.2, 0.3), (px, 15.1, 3.2), 0.4, "drewno_ciemne", "Wood")
            y = 12.0 + 0.5 * k
            s.blok("Latarnia łańcuch", (px, (y + 1.15 + 15.05) / 2.0, 5.2), (0.16, 15.05 - y - 1.15, 0.16), "zelazo", "Metal")
            s.blok("Latarnia daszek", (px, y + 0.85, 5.2), (1.5, 0.3, 1.5), "zelazo", "Metal")
            s.blok("Latarnia czubek", (px, y + 1.1, 5.2), (0.8, 0.26, 0.8), "zelazo", "Metal")
            s.blok("Latarnia dno", (px, y - 0.85, 5.2), (1.35, 0.26, 1.35), "zelazo", "Metal")
            for dx in (-1, 1):
                for dz in (-1, 1):
                    s.blok("Latarnia pręt", (px + dx * 0.55, y, 5.2 + dz * 0.55), (0.16, 1.5, 0.16), "zelazo", "Metal")
            with s.grupa("Plomienie"), s.cechy(cien=False):
                s.blok("Latarnia światło", (px, y, 5.2), (0.95, 1.4, 0.95), "ogien2", "Neon")
            swiatlo(s, "Latarnia lady %d" % k, (px, y - 0.4, 5.6), 13, 0.4, "FFC060", migot=0.08)
    for g in ("Regal", "Lada", "Stolki", "Latarnie"):
        s.obrys_sylwetki(g)


def sciana_prawa(s, rnd):
    mur(s, rnd, -TYL, 9.0)
    mur(s, rnd, 9.0, PRZOD, bogaty=False)
    szkielet(s, (-TYL + 0.7, -21.2, -6.8, 5.8, 14.0, 22.0, PRZOD - 0.7), ((-TYL, PRZOD),), -TYL, PRZOD,
             zastrzaly=((-TYL + 0.7, 1), (5.8, 1)))
    with s.uklad(pos=(KOMINEK_X, 0, 0)):
        kominek(s, rnd)
    regal_i_lada(s)
    for i, x in enumerate((-21.2, -6.8)):
        with s.uklad(pos=(x, 10.4, 1.0)):
            pochodnia(s, "Pochodnia P%d" % i)
    with s.uklad(pos=(-24.0, 14.3, 0.75)):
        choragiew(s, "Chorągiew fioletowa", "fiolet", 2.8, 5.4)
    for (x, y) in ((-25.6, 7.6), (-6.0, 7.4), (6.9, 9.5), (9.6, 12.6)):
        cegly(s, rnd, x, y)
    # skrzynie i beczka w rogu, stos drewna między kominkiem a ladą
    with s.grupa("Skrzynie"):
        skrzynia(s, "Skrzynia", (-24.0, 0.16, 3.4), 3.2, ry=8)
        skrzynia(s, "Skrzynia 2", (-23.6, 3.36, 3.2), 2.4, ry=-14)
    with s.grupa("Beczki"):
        beczka(s, "Beczka", (-23.2, 0.16, 7.2), 1.4, 3.3, jablka=True)
        for (dx, dy) in ((0, 0), (0.95, 0), (1.9, 0), (0.48, 0.82), (1.43, 0.82), (0.95, 1.64)):
            s.walec("Polano stosu", (-7.7, 0.62 + dy, 1.4 + dx), 0.45, 2.4, "drewno", "Wood", os="x")
            s.walec("Polano stosu słój", (-6.48, 0.62 + dy, 1.4 + dx), 0.33, 0.06, "drewno_jasne", "Wood", os="x")


def sciana_prosta(s, rnd, x0, x1, slupy):
    """Ściana, której gracz nie widzi (albo ledwo): bez drobnych kamieni."""
    mur(s, rnd, x0, x1, bogaty=False)
    szkielet(s, slupy, ((x0, x1),), x0, x1)


# --------------------------------------------------------------------------- dach, żyrandole, stół, dywan
def dach(s):
    kat = math.degrees(math.atan2(WZNIOS, W))
    dl = math.hypot(W, WZNIOS)
    with s.grupa("Wiezba"):
        for z in (-TYL + 0.4, -20.0, -12.0, -4.0, 4.0, 12.0, 20.0, PRZOD - 0.4):
            s.blok("Ściąg", (0, WYS + 0.55, z), (2 * W + 1.0, 1.1, 1.1), "drewno", "Wood")
            for d in (-1, 1):
                s.belka("Krokiew", (d * (W + 0.3), WYS + 0.5, z), (0, WYS + WZNIOS, z), 1.0, "drewno", "Wood")
                s.belka("Miecz więźby", (d * 6.5, WYS + 1.0, z), (d * 12.0, WYS + WZNIOS * (1 - 12.0 / W) - 0.2, z), 0.8,
                        "drewno2", "Wood")
            s.blok("Słupek", (0, WYS + 1.1 + (WZNIOS - 1.5) / 2.0, z), (1.0, WZNIOS - 1.5, 1.0), "drewno2", "Wood")
        s.blok("Kalenica", (0, WYS + WZNIOS - 0.5, 0), (1.2, 1.2, TYL + PRZOD), "drewno_ciemne", "Wood")
        for d in (-1, 1):
            for u in (0.36, 0.7):
                s.blok("Płatew", (d * W * u, WYS + WZNIOS * (1 - u) + 0.75, 0), (0.9, 0.9, TYL + PRZOD), "drewno_ciemne",
                       "Wood", rot=(0, 0, -d * kat))
    with s.grupa("Dach"):
        for d in (-1, 1):
            s.blok("Deski dachu", (d * W / 2.0, WYS + 0.25 + WZNIOS / 2.0 + 1.25, 0), (dl + 3.0, 0.7, TYL + PRZOD + 3.5),
                   "deski_dachu", "WoodPlanks", rot=(0, 0, -d * kat))
            s.blok("Okap zamknięcie", (d * (W + 0.75), WYS + 1.0, 0), (1.5, 2.6, TYL + PRZOD + 2.8), "fuga")
    for z, nazwa in ((-TYL - 0.7, "Szczyt tył"), (PRZOD + 0.7, "Szczyt przód")):
        with s.grupa("Dach"), s.uklad(pos=(0, 0, z), obrot=(0, 90, 0)):
            s.szczyt(nazwa, (0, WYS, 0), W + 1.6, WZNIOS + 0.9, 1.4, "tynk2", "Plaster")
    s.obrys_sylwetki("Wiezba")


def zyrandol(s, nazwa, pos, r, y_hak, swiec=8, jasnosc=1.4, zasieg=26):
    x, y, z = pos
    with s.grupa("Zyrandole"), s.cechy(kolizja=False):
        n = 12
        for i in range(n):
            a = 2 * math.pi * i / n
            s.blok(nazwa + " obręcz", (x + r * math.cos(a), y, z + r * math.sin(a)), (2 * r * math.sin(math.pi / n) + 0.2, 0.6, 0.62),
                   "drewno_ciemne", "Wood", rot=(0, -math.degrees(a) + 90, 0))
        for i in range(2):
            a = math.pi * i / 2.0 + 0.4
            s.belka(nazwa + " szprycha", (x + r * math.cos(a), y, z + r * math.sin(a)), (x - r * math.cos(a), y, z - r * math.sin(a)),
                    0.3, "zelazo", "Metal")
        for i in range(4):
            a = math.pi * i / 2.0 + 0.4
            s.belka(nazwa + " łańcuch", (x + r * math.cos(a), y + 0.3, z + r * math.sin(a)), (x, y + r * 0.9, z), 0.2, "zelazo", "Metal")
        s.blok(nazwa + " hak", (x, (y + r * 0.9 + y_hak) / 2.0, z), (0.24, y_hak - y - r * 0.9, 0.24), "zelazo", "Metal")
        for i in range(swiec):
            a = 2 * math.pi * (i + 0.5) / swiec
            cx, cz = x + r * math.cos(a), z + r * math.sin(a)
            s.walec(nazwa + " miseczka", (cx, y + 0.36, cz), 0.42, 0.14, "zelazo", "Metal", os="y")
            s.walec(nazwa + " świeca", (cx, y + 0.95, cz), 0.23, 1.05, "swieca", os="y")
            with s.grupa("Plomienie"), s.cechy(cien=False):
                s.kula(nazwa + " płomień", (cx, y + 1.72, cz), 0.46, "ogien2", "Neon")
                s.kula(nazwa + " płomień", (cx, y + 2.02, cz), 0.26, "ogien", "Neon")
    swiatlo(s, nazwa, (x, y + 0.6, z), zasieg, jasnosc, "FFC878", migot=0.07)


def stol(s, pos, ry=0.0):
    x, y, z = pos
    with s.grupa("Stol"), s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.walec("Stół blat", (0, 3.45, 0), 3.1, 0.5, "drewno2", "Wood", os="y")
        s.walec("Stół blat tusz", (0, 3.1, 0), 3.22, 0.22, "tusz", os="y")
        s.walec("Stół noga", (0, 1.6, 0), 0.55, 3.0, "drewno", "Wood", os="y")
        s.blok("Stół stopa", (0, 0.3, 0), (3.6, 0.6, 0.8), "drewno", "Wood")
        s.blok("Stół stopa", (0, 0.31, 0), (0.8, 0.62, 3.6), "drewno", "Wood")
        with s.cechy(kolizja=False):
            b = 3.7
            s.walec("Świecznik stołu", (0.2, b + 0.1, -0.3), 0.5, 0.2, "zelazo", "Metal", os="y")
            swieca(s, "Świeca stołu", (0.2, b + 0.2, -0.3), 1.2, 0.24, jasnosc=0.9)
            kufel(s, (-1.4, b, 0.6), 200)
            kufel(s, (1.5, b, 0.9), 320)
            s.walec("Talerz stołu", (-0.6, b + 0.07, -1.5), 0.8, 0.14, "biel", os="y")
            trojkat(s, "Ser stołu", (-1.0, b + 0.14), 0.9, 0.7, -1.5, 0.75, "ser")
            with s.cechy(cien=False):
                s.kula("Jabłko stołu", (1.2, b + 0.3, -1.0), 0.6, "jablko")
        stolek(s, (-4.3, 0.0, 0.8), 2.3, faza=0.3)
        stolek(s, (1.2, 0.0, -4.5), 2.3, faza=1.2)
    s.obrys_sylwetki("Stol")


def dywan(s, pos, dl, szer, ry=0.0):
    x, y, z = pos
    with s.grupa("Dywan"), s.cechy(kolizja=False, cien=False), s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.blok("Dywan tusz", (0, 0.05, 0), (szer + 0.5, 0.1, dl + 0.5), "tusz", "Fabric")
        s.blok("Dywan lamówka", (0, 0.1, 0), (szer, 0.12, dl), "zloto2", "Fabric")
        s.blok("Dywan pole", (0, 0.14, 0), (szer - 1.0, 0.12, dl - 1.0), "dywan", "Fabric")
        s.blok("Dywan pas", (0, 0.18, 0), (szer - 2.4, 0.1, dl - 2.4), "dywan2", "Fabric")
        for k in (-1, 0, 1):
            s.blok("Dywan romb", (0, 0.22, k * dl * 0.27), (1.5, 0.08, 1.5), "zloto_lam", "Fabric", rot=(0, 45, 0))
        for d in (-1, 1):
            for k in range(7):
                s.blok("Dywan frędzel", (-szer / 2.0 + 0.5 + k * (szer - 1.0) / 6.0, 0.06, d * (dl / 2.0 + 0.55)), (0.28, 0.1, 0.7),
                       "zloto_lam", "Fabric")
    s.obrys_sylwetki("Dywan")


# --------------------------------------------------------------------------- całość
def sala(s):
    rnd = random.Random(16)
    podloga(s, rnd)
    with s.uklad(pos=(0, 0, -TYL)):
        sciana_tylna(s, rnd)
    with s.uklad(pos=(W, 0, 0), obrot=(0, -90, 0)):
        sciana_prawa(s, rnd)
    with s.uklad(pos=(-W, 0, 0), obrot=(0, 90, 0)):
        sciana_prosta(s, rnd, -PRZOD, TYL, (-PRZOD + 0.7, -18.0, -9.0, 0.0, 9.0, 18.0, TYL - 0.7))
        with s.uklad(pos=(18.0, 10.2, 1.0)):
            pochodnia(s, "Pochodnia L0")
    with s.uklad(pos=(0, 0, PRZOD), obrot=(0, 180, 0)):
        sciana_prosta(s, rnd, -W - 1.4, W + 1.4, (-W + 0.7, -11.5, 0.0, 11.5, W - 0.7))
    dach(s)
    # żyrandole: duży nad przejściem między kominkiem a ladą, mały w głębi po lewej
    zyrandol(s, "Żyrandol duży", (14.0, 13.0, -4.0), 3.5, WYS + 0.1, 8, 0.42, 24)
    zyrandol(s, "Żyrandol mały", (-12.0, 13.0, -12.0), 2.5, WYS + 0.1, 6, 0.32, 20)
    s.obrys_sylwetki("Zyrandole")
    # chorągwie wiszące ze ściągów (lewa góra kadru, nad kartą statystyk)
    with s.uklad(pos=(-12.6, WYS - 0.1, -3.5)):
        choragiew(s, "Chorągiew wisząca granat", "granat", 3.4, 6.2)
    with s.uklad(pos=(-7.0, WYS - 0.1, -11.5)):
        choragiew(s, "Chorągiew wisząca czerwona", "czerwien", 3.2, 5.6)
    for g in ("Choragwie", "Pochodnie", "Beczki", "Skrzynie"):
        s.obrys_sylwetki(g)
    # pierwszy plan: stół ze świecą (prawy dolny róg kadru), dywan przed kominkiem i ladą
    stol(s, (10.3, 0.16, 10.0), ry=20)
    dywan(s, (12.6, 0.2, -3.5), 13.0, 6.4)


def buduj(s):
    with s.uklad(obrot=(0, OBROT, 0)):
        sala(s)
    podest(s)
    # światło sceny: reflektor z góry na bohaterów, chłodny kontr z okna, miękkie wypełnienie od kamery
    swiatlo(s, "Reflektor podestu", (0, 21.0, 4.0), 40, 2.2, "FFE2B0", cienie=True, cel=(0, GORA_PODESTU + 2.5, 0), kat=48)
    swiatlo(s, "Wypełnienie przód", (0, 9.5, 15.0), 30, 0.5, "FFE8D0")
    with s.uklad(obrot=(0, OBROT, 0)):
        swiatlo(s, "Kontra z okna", (OKNO_X - 2.0, 12.5, -TYL + 3.0), 46, 1.5, "86AEFF", cel=(0, 5.0, 0), kat=38)
    gora, dol = swiat(s, (0, 26, 0.5)), swiat(s, (0, 2.2, 0.5))
    for nazwa, w0, w1, kolor, alfa in (("Snop wąski", 2.5, 8.0, "FFE9B4", 0.74), ("Snop średni", 4.5, 11.0, "FFE2A0", 0.84),
                                      ("Snop szeroki", 6.5, 14.0, "FFD890", 0.92)):
        EFEKTY["snopy"].append({"n": nazwa, "p0": gora, "p1": dol, "w0": w0, "w1": w1, "kolor": kolor, "alfa": alfa})
    EFEKTY["pylki"].append({"n": "Pyłki w snopie", "p": swiat(s, (0, 3.0, 0.5)), "rozmiar": [11.0, 0.4, 11.0], "ile": 5,
                            "zycie": [4.0, 7.0], "predkosc": [0.5, 1.1], "wielkosc": 0.55, "kolor": "FFF0B4"})


def main():
    s = Scena(KONTENER, paleta=PALETA)
    with s.uklad(pos=PRZESUNIECIE):
        buduj(s)
    wyj = os.path.join(TU, "czesci.json")
    s.zapisz(wyj)
    with open(os.path.join(TU, "efekty.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(EFEKTY, f, ensure_ascii=False, indent=1)
        f.write("\n")
    px, py, pz = PRZESUNIECIE
    (kx, ky, kz), (cx, cy, cz) = KAMERA
    ujecia = [["a_gracz", [px + kx, py + ky, pz + kz], [px + cx, py + cy, pz + cz], 22, None],
              ["b_szeroko", [px + 6, py + 13, pz + 24], [px + 4, py + 6, pz - 8], 22, None]]
    with open(os.path.join(TU, "ujecia.json"), "w", encoding="utf-8") as f:
        json.dump(ujecia, f)
    st = s.statystyki()
    print("ok: %d części, %d grup, obrysów %d, świateł %d" % (st["czesci"], len(st["grupy"]), len(s.obrysy), len(EFEKTY["swiatla"])))
    print("grupy:", ", ".join("%s %d" % (k.split("/")[-1], v) for k, v in sorted(st["grupy"].items(), key=lambda kv: -kv[1])))
    print("zakres:", st["zakres"])
    uw = s.sprawdz(min_y=PRZESUNIECIE[1] - 6)
    if uw:
        print("kontrola (%d):" % len(uw))
        for u in uw[:40]:
            print("  -", u)


if __name__ == "__main__":
    main()
