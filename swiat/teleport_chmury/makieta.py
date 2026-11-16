#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Makieta pasa krain z klocków — geometria dla zbuduj.py (bez Studio).

    python -B swiat/teleport_chmury/makieta.py     # liczba części na krainę i w chmurach

Wszystko w układzie LOKALNYM makiety (krainy.json → makieta.opis): x wzdłuż pasa (miasteczko z lewej, kryształy
z prawej), y w górę (0 = wierzch płytek), z ku kamerze. Budowa w Studio mnoży każdą ramkę przez obrót i środek
makiety. Styl jak w Krzywym Miasteczku (swiat/krzywe_miasteczko/PROJEKT.md): kolory z paleta.py tam, gdzie pasują,
gładki plastik, ciemny „tusz” na krawędzi płytek i pod tabliczkami, Neon tylko w lawie i kryształach.

Każda część to słownik:
  n  nazwa              k  klasa (Part / WedgePart)       s  kształt (Block / Ball / Cylinder)
  r  rozmiar [x, y, z]  cf [x, y, z, R00 … R22] (macierz wierszami, jak CFrame.new z 12 liczbami)
  c  kolor RRGGBB       m  materiał (Enum.Material)       t  przezroczystość
  g  grupa: "Krainy/<id>", "Krainy/<id>/Klodka", "Chmury", "Wskaznik", "Pinezka"
  rola: grunt | akcent | neon | klodka | tabliczka | tusz | chmura | wskaznik | pinezka
  cien  CastShadow;  napis (tylko tabliczka)
"""
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, os.path.join(REPO, "swiat", "krzywe_miasteczko"))
from paleta import PALETA  # noqa: E402  (tylko odczyt: wspólna paleta miasteczka)

P = PALETA
TUSZ = P["tusz"]


# ------------------------------------------------------------------ macierze 3 × 3 (wiersze)
def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def mm(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def mv(a, v):
    return [sum(a[i][k] * v[k] for k in range(3)) for i in range(3)]


def orient(rx=0.0, ry=0.0, rz=0.0):
    """Jak Orientation w Roblox (CFrame.fromOrientation): obrót Y, potem X, potem Z (stopnie)."""
    return mm(mm(_ry(math.radians(ry)), _rx(math.radians(rx))), _rz(math.radians(rz)))


def kolumny(x, y, z):
    """Macierz z osi (prawo, góra, tył) — kolumny, jak CFrame.fromMatrix."""
    return [[x[0], y[0], z[0]], [x[1], y[1], z[1]], [x[2], y[2], z[2]]]


JEDN = orient()


class Rama:
    """Położenie i obrót (dla podzespołów: kłódka, tabliczka, strzałka)."""

    def __init__(self, poz=(0, 0, 0), R=None):
        self.poz = list(poz)
        self.R = R or JEDN

    def razy(self, poz=(0, 0, 0), R=None):
        R = R or JEDN
        p = mv(self.R, list(poz))
        return Rama([self.poz[i] + p[i] for i in range(3)], mm(self.R, R))


def _norm(v):
    d = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / d for x in v]


def _krzyz(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def ku_kamerze(nachylenie_stopnie):
    """Obrót, po którym przód części (−Z, ściana Front) patrzy na kamerę makiety (z góry pod kątem nachylenia)."""
    a = math.radians(nachylenie_stopnie)
    przod = [0.0, math.sin(a), math.cos(a)]          # kierunek do kamery
    tyl = [-x for x in przod]                        # oś Z części (LookVector = −Z = przod)
    gora = _norm(_krzyz(tyl, [1.0, 0.0, 0.0]))       # Y = Z × X
    gora = gora if gora[1] > 0 else [-x for x in gora]
    prawo = _norm(_krzyz(gora, tyl))
    return kolumny(prawo, gora, tyl)


# ------------------------------------------------------------------ zbiór części
class Zbior:
    def __init__(self):
        self.czesci = []

    def dodaj(self, n, r, rama, c, g, rola="akcent", k="Part", s="Block", m="SmoothPlastic", t=0.0, cien=True, **dod):
        R = rama.R
        cf = [round(x, 4) for x in rama.poz] + [round(R[i][j], 6) for i in range(3) for j in range(3)]
        cz = {"n": n, "k": k, "s": s, "r": [round(x, 3) for x in r], "cf": cf, "c": c.upper(), "m": m,
              "t": t, "g": g, "rola": rola, "cien": cien}
        cz.update(dod)
        self.czesci.append(cz)
        return cz

    def blok(self, n, r, poz, c, g, obr=(0, 0, 0), baza=None, **kw):
        baza = baza or Rama()
        return self.dodaj(n, r, baza.razy(poz, orient(*obr)), c, g, **kw)

    def kula(self, n, d, poz, c, g, baza=None, **kw):
        return self.blok(n, (d, d, d), poz, c, g, baza=baza, s="Ball", **kw)

    def walec(self, n, wys, sred, poz, c, g, obr=(0, 0, 0), baza=None, **kw):
        """Walec pionowy (oś Roblox to X — obracamy o 90° wokół Z)."""
        baza = baza or Rama()
        R = mm(orient(*obr), orient(0, 0, 90))
        return self.dodaj(n, (wys, sred, sred), baza.razy(poz, R), c, g, s="Cylinder", **kw)


# ------------------------------------------------------------------ akcenty krain (współrzędne względem środka płytki)
def drzewo(z, g, b, x, zz, wys=4.0, kor=6.0, ton=None, obr=0.0):
    ton = ton or (P["lisc"], P["lisc_jasny"])
    z.blok("Pień", (1.3, wys, 1.3), (x, wys / 2, zz), P["drewno"], g, (0, 0, obr), baza=b)
    sx = x - math.sin(math.radians(obr)) * wys
    z.kula("Korona", kor, (sx, wys + kor * 0.35, zz), ton[0], g, baza=b)
    z.kula("Korona — blask", kor * 0.55, (sx - kor * 0.15, wys + kor * 0.72, zz + kor * 0.12), ton[1], g, baza=b)


def iglak(z, g, b, x, zz, sk=1.0):
    z.blok("Pień", (0.6 * sk, 1.4 * sk, 0.6 * sk), (x, 0.7 * sk, zz), P["drewno"], g, baza=b)
    for i, (w, h) in enumerate(((3.2, 1.6), (2.4, 1.5), (1.5, 1.4))):
        z.blok("Igliwie", (w * sk, h * sk, w * sk), (x, (1.4 + 0.8 + i * 1.35) * sk, zz), P["igla"], g,
               (0, 20 * i, 0), baza=b)


def akcent_miasteczko(z, g, b):
    domy = [  # x, z, szer, wys, głęb, ściana, dach, przechył rz, skręt ry
        (-9.5, -6.0, 7.0, 6.0, 6.0, P["tynk_krem"], P["dach_karczma"], 6, 8),
        (-1.5, -7.5, 6.0, 8.5, 5.5, P["tynk_blekit"], P["dach_twierdza"], -7, -6),
        (6.5, -5.5, 6.5, 5.0, 5.0, P["tynk_mieta"], P["dach_kolo"], 5, 12),
    ]
    for x, zz, sz, wy, gl, sciana, dach, rz, ry in domy:
        dom = b.razy((x, 0, zz), orient(0, ry, 0))
        z.blok("Cokół", (sz + 0.4, 1.0, gl + 0.4), (0, 0.5, 0), P["kamien_cokol"], g, baza=dom)
        gora = dom.razy((0, 1.0, 0), orient(0, 0, rz))
        z.blok("Ściana", (sz, wy, gl), (0, wy / 2, 0), sciana, g, baza=gora)
        bok = gl * 0.78
        z.blok("Dach", (sz + 1.4, bok, bok), (0, wy + 0.2, 0), dach, g, (45, 0, 0), baza=gora)
        z.blok("Kalenica", (sz + 1.6, 0.6, 0.6), (0, wy + 0.2 + bok * 0.7071, 0), P["zloto"], g, baza=gora)
        z.blok("Okno", (1.4, 1.6, 0.3), (-sz * 0.22, wy * 0.55, gl / 2 + 0.1), P["neon_okno"], g, baza=gora,
               m="Neon", rola="neon")
    wieza = b.razy((11.5, 0, -9.0), orient(0, 15, 0))
    z.blok("Wieża", (4.0, 12.0, 4.0), (0, 6.0, 0), P["kamien_cieply"], g, (0, 0, -8), baza=wieza)
    z.blok("Dach wieży", (3.6, 3.6, 3.6), (-1.6, 12.6, 0), P["dach_brama"], g, (45, 45, -8), baza=wieza)
    z.blok("Pomnik — klocek", (2.4, 2.4, 2.4), (-4.0, 1.6, 7.0), P["zloto"], g, (12, 25, 18), baza=b)
    z.walec("Studnia", 1.4, 4.2, (-4.0, 0.7, 7.0), P["kamien_cieply"], g, baza=b)
    drzewo(z, g, b, -12.0, 8.0, 3.5, 5.0)
    drzewo(z, g, b, 11.5, 7.0, 3.0, 4.6, obr=-8)
    z.blok("Chorągiewka", (0.4, 6.0, 0.4), (4.0, 3.0, 8.5), TUSZ, g, baza=b)
    z.blok("Płat", (2.6, 1.6, 0.3), (5.3, 5.2, 8.5), P["dach_twierdza"], g, (0, 0, -12), baza=b)


def akcent_las(z, g, b):
    # Stary Ukłon: wielkie drzewo, które się kłania
    z.blok("Pień Ukłonu", (2.4, 12.0, 2.4), (-1.0, 6.0, -6.0), P["drewno"], g, (0, 0, 16), baza=b)
    z.kula("Korona Ukłonu", 10.0, (-4.8, 13.6, -6.0), P["lisc_ciemny"], g, baza=b)
    z.kula("Korona Ukłonu — blask", 6.0, (-6.2, 16.4, -4.6), P["lisc"], g, baza=b)
    for x, zz, w, k, o in ((-11, -8, 4.0, 6.0, 4), (9, -8, 5.0, 6.6, -6), (12.5, -2.5, 3.2, 4.6, 0),
                           (-12.5, 7.5, 3.0, 4.6, 6), (8.5, 8.0, 3.4, 5.2, -4), (2.5, -10, 3.0, 4.2, 0)):
        drzewo(z, g, b, x, zz, w, k, ton=(P["lisc"], P["lisc_jasny"]), obr=o)
    # muchomor
    z.walec("Trzon muchomora", 2.6, 1.6, (-5.5, 1.3, 7.0), P["biel"], g, baza=b)
    z.walec("Kapelusz muchomora", 1.2, 5.0, (-5.5, 3.0, 7.0), P["czerwien"], g, (0, 0, 8), baza=b)
    for dx, dz in ((-1.2, 0.8), (1.0, -0.6), (0.2, 1.6)):
        z.kula("Kropka", 0.8, (-5.5 + dx, 3.6, 7.0 + dz), P["biel"], g, baza=b)
    z.kula("Krzak", 3.0, (3.0, 1.0, 7.5), P["lisc_ciemny"], g, baza=b)
    z.kula("Krzak", 2.4, (0.8, 0.8, 8.8), P["lisc"], g, baza=b)


def akcent_bagno(z, g, b):
    for x, zz, d in ((-6.5, -6.0, 9.0), (7.5, 6.5, 7.0), (9.0, -7.0, 6.0), (-10.0, 7.0, 4.5)):
        z.walec("Woda", 0.3, d, (x, 0.08, zz), "35706A", g, baza=b)
        z.walec("Woda — toń", 0.32, d * 0.55, (x, 0.1, zz), "24524E", g, baza=b)
    for x, zz in ((-3.0, -3.5), (-2.0, -8.5), (-10.5, -3.8), (4.0, 7.0), (10.5, 4.0), (5.5, -8.5), (11.5, -4.0)):
        z.blok("Trzcina", (0.4, 4.2, 0.4), (x, 2.1, zz), P["drewno_jasne"], g, (0, 0, (x * 7) % 14 - 7), baza=b)
        z.blok("Pałka", (0.8, 1.4, 0.8), (x, 4.3, zz), P["drewno_ciemne"], g, baza=b)
    martwe = b.razy((-11.0, 0, 5.0))
    z.blok("Martwe drzewo", (1.5, 9.0, 1.5), (0, 4.5, 0), "4A3F2A", g, (0, 0, -8), baza=martwe)
    z.blok("Konar", (0.8, 4.5, 0.8), (1.6, 7.0, 0), "4A3F2A", g, (0, 0, -55), baza=martwe)
    z.blok("Konar", (0.7, 3.5, 0.7), (-0.6, 8.0, 0), "4A3F2A", g, (0, 0, 40), baza=martwe)
    for x, zz in ((-7.5, -4.5), (-4.5, -7.5), (8.0, 5.5)):
        z.walec("Liść lilii", 0.25, 2.2, (x, 0.2, zz), "5FA83E", g, baza=b)
    z.kula("Kępa", 3.4, (1.0, 0.6, -9.0), "5E7A2E", g, baza=b)
    z.kula("Kępa", 2.6, (12.0, 0.5, 9.0), "5E7A2E", g, baza=b)


def akcent_dzungla(z, g, b):
    for x, zz, kier in ((-8.0, -6.5, 1), (2.0, -8.0, -1), (10.0, -5.0, 1), (-11.5, 7.0, -1)):
        p = b.razy((x, 0, zz))
        y = 0.0
        przes = 0.0
        for i in range(3):
            pochyl = kier * (6 + 7 * i)
            z.blok("Pień palmy", (1.2, 3.6, 1.2), (przes, y + 1.8, 0), "8B6A3E", g, (0, 0, -pochyl), baza=p)
            przes += math.sin(math.radians(pochyl)) * 3.4
            y += 3.4
        szczyt = p.razy((przes, y + 0.3, 0))
        for j in range(5):
            z.blok("Liść palmy", (6.5, 0.4, 2.0), (2.6, -0.6, 0), "3CC85A" if j % 2 else "2E9E46", g,
                   baza=szczyt.razy((0, 0, 0), orient(0, j * 72 + 18, -18)))
        z.kula("Kokos", 1.0, (przes, y - 0.2, 0.6), P["drewno"], g, baza=p)
    for x, zz, d in ((5.5, 6.5, 4.6), (-4.0, 7.5, 4.0), (11.5, 8.5, 3.4), (-2.5, -11.0, 3.6), (6.0, -11.0, 3.0)):
        z.kula("Krzew", d, (x, d * 0.3, zz), "1E8F3E", g, baza=b)
    for x, zz, c in ((4.0, 8.5, P["czerwien"]), (-6.0, 6.0, P["pomarancz"]), (12.0, 6.0, P["dach_kolo"])):
        z.kula("Kwiat", 1.3, (x, 1.6, zz), c, g, baza=b)
    z.blok("Ruina", (4.0, 4.5, 3.0), (-1.5, 2.25, 8.5), "8A9A7A", g, (0, 18, 4), baza=b)
    z.blok("Mech", (4.4, 0.6, 3.4), (-1.5, 4.6, 8.5), "4CAF50", g, (0, 18, 4), baza=b)


def akcent_pustynia(z, g, b):
    pir = b.razy((-6.0, 0, -5.0), orient(0, 10, 0))
    for i, (w, c) in enumerate(((11.0, "E2B860"), (8.0, "D9A84E"), (5.2, "E2B860"), (2.6, "D9A84E"))):
        z.blok("Piramida — stopień", (w, 2.2, w), (0, 1.1 + i * 2.2, 0), c, g, baza=pir)
    z.blok("Złota czapa", (1.6, 1.4, 1.6), (0, 9.5, 0), P["zloto"], g, (0, 45, 0), baza=pir)
    for x, zz, wys in ((8.0, -6.0, 7.0), (11.5, 6.5, 5.0), (-11.5, 6.0, 4.0)):
        k = b.razy((x, 0, zz))
        z.walec("Kaktus", wys, 1.7, (0, wys / 2, 0), "3E9A4A", g, baza=k)
        z.blok("Ramię kaktusa", (2.2, 0.9, 0.9), (1.4, wys * 0.45, 0), "3E9A4A", g, baza=k)
        z.blok("Ramię kaktusa", (0.9, 2.4, 0.9), (2.1, wys * 0.45 + 1.2, 0), "3E9A4A", g, baza=k)
        z.blok("Ramię kaktusa", (1.8, 0.8, 0.8), (-1.2, wys * 0.62, 0), "3E9A4A", g, baza=k)
        z.blok("Ramię kaktusa", (0.8, 1.8, 0.8), (-1.8, wys * 0.62 + 0.9, 0), "3E9A4A", g, baza=k)
    for x, zz, d in ((4.0, 7.0, 8.0), (-3.0, 8.5, 6.0), (11.0, -10.0, 6.5)):
        z.kula("Wydma", d, (x, -d * 0.28, zz), "E8B860", g, baza=b)
    z.blok("Kość", (3.0, 0.5, 0.5), (1.5, 0.3, 4.0), P["biel"], g, (0, 30, 0), baza=b)
    z.kula("Kość — główka", 0.9, (2.8, 0.4, 3.25), P["biel"], g, baza=b)


def akcent_gory(z, g, b):
    def gora(x, zz, w0, wys, ry):
        m = b.razy((x, 0, zz), orient(0, ry, 0))
        n = 4
        for i in range(n):
            f = 1 - i / n
            w = w0 * f
            c = "8A8F9C" if i < n - 1 else "F4F8FF"
            if i == n - 2:
                c = "A3A8B3"
            z.blok("Skała" if i < n - 1 else "Śnieg", (w, wys / n, w), (0, wys / n * (i + 0.5), 0), c, g,
                   (0, 45 + i * 9, 0), baza=m)
        z.blok("Czapa śniegu", (w0 * 0.22, wys / n * 0.8, w0 * 0.22), (0, wys + 0.2, 0), "FFFFFF", g, (0, 45, 0), baza=m)
    gora(-5.0, -6.0, 9.0, 14.0, 0)
    gora(6.5, -7.0, 7.0, 10.0, 12)
    gora(12.0, -9.0, 4.6, 6.5, -8)
    for x, zz, sk in ((-11.5, 7.0, 1.2), (-7.5, 9.0, 1.0), (9.5, 7.5, 1.1), (12.5, 9.5, 0.9), (3.0, 9.0, 0.9)):
        iglak(z, g, b, x, zz, sk)
    for x, zz, w in ((-2.0, 6.5, 4.0), (5.5, 4.5, 3.0)):
        z.blok("Mszysta tundra", (w, 0.25, w * 0.7), (x, 0.12, zz), "C9D1A8", g, (0, 20, 0), baza=b)
    z.kula("Głaz", 2.4, (-1.0, 0.8, 9.5), "8A8F9C", g, baza=b)


def akcent_lodowiec(z, g, b):
    for x, zz, r, obr in ((-7.0, -7.0, (8.0, 6.0, 5.0), (4, 12, 6)), (3.0, -8.0, (6.0, 9.0, 5.0), (-3, -10, -4)),
                          (10.5, -5.0, (5.0, 4.0, 4.0), (0, 20, 5))):
        z.blok("Bryła lodu", r, (x, r[1] / 2 - 0.3, zz), "A8E0FF", g, obr, baza=b, m="Ice")
        z.blok("Czapa śniegu", (r[0] + 0.3, 0.8, r[2] + 0.3), (x, r[1] - 0.2, zz), "FFFFFF", g, obr, baza=b)
    for x, zz, h, rz in ((-2.0, -3.5, 6.0, 12), (-11.0, -2.5, 5.0, -15), (7.0, -1.0, 4.0, 18), (12.0, 8.0, 5.5, -10)):
        z.blok("Sopel", (1.2, h, 1.2), (x, h / 2, zz), "D8F4FF", g, (8, 30, rz), baza=b, m="Glass", t=0.1)
    z.blok("Szczelina", (1.2, 0.2, 9.0), (-4.0, 0.05, 7.0), "2A4A8A", g, (0, 32, 0), baza=b)
    z.kula("Igloo", 6.0, (8.5, -0.6, 7.0), "FFFFFF", g, baza=b)
    z.blok("Wejście igloo", (1.8, 1.8, 1.0), (8.5, 0.9, 9.9), "5A7AA8", g, baza=b)
    z.kula("Śnieżka", 2.0, (-10.0, 0.6, 8.0), "FFFFFF", g, baza=b)


def akcent_wulkan(z, g, b):
    w = b.razy((-2.0, 0, -5.0))
    y0 = 0.0
    for h, d, c in ((3.0, 14.0, "4A3B36"), (3.0, 10.6, "5C4840"), (3.0, 7.6, "4A3B36"), (2.0, 5.4, "5C4840")):
        z.walec("Stożek", h, d, (0, y0 + h / 2, 0), c, g, baza=w)
        y0 += h
    z.walec("Krater", 0.4, 4.0, (0, 11.2, 0), P["neon_ogien"], g, baza=w, m="Neon", rola="neon")
    for y0, dz, dl in ((10.0, 2.4, 2.4), (7.5, 4.0, 2.6), (4.5, 5.4, 2.8), (1.5, 6.8, 2.8)):
        z.blok("Lawa", (1.2, 0.5, dl), (0.8, y0, dz), P["neon_ogien"], g, (-35, 0, 0), baza=w, m="Neon", rola="neon")
    for i, (dx, y, d) in enumerate(((0.5, 14.0, 3.0), (-1.2, 16.5, 3.8), (0.8, 19.0, 4.6))):
        z.kula("Dym", d, (dx, y, 0.2 * i), "6E6A6A", g, baza=w, cien=False)
    z.walec("Jezioro lawy", 0.3, 6.0, (9.0, 0.1, 6.5), P["neon_ogien"], g, baza=b, m="Neon", rola="neon")
    for x, zz, d in ((6.0, 4.0, 2.4), (12.5, 3.5, 2.0), (11.0, -8.0, 3.2), (-11.0, 7.0, 3.0), (-12.0, -9.0, 2.6)):
        z.kula("Bazalt", d, (x, d * 0.25, zz), "2E2424", g, baza=b)


def akcent_krysztal(z, g, b):
    gr = [  # x, z, szer, wys, obrót, kolor, materiał
        (-2.0, -6.0, 2.6, 11.0, (0, 30, 12), P["neon_magia"], "Neon"),
        (2.5, -5.0, 1.9, 7.5, (0, -20, -18), P["neon_slime"], "Neon"),
        (-5.5, -4.0, 1.6, 5.5, (10, 45, 25), P["tynk_lawenda"], "Glass"),
        (0.0, -9.5, 1.5, 6.0, (-12, 10, 5), P["dach_sklep"], "SmoothPlastic"),
        (9.0, -7.0, 1.8, 6.5, (0, 15, -14), P["neon_magia"], "Neon"),
        (11.0, 6.0, 1.4, 4.5, (6, 0, 16), P["neon_slime"], "Neon"),
        (-10.0, 7.5, 1.6, 5.0, (0, 40, -12), P["tynk_lawenda"], "Glass"),
        (-11.5, -6.5, 1.4, 4.0, (0, 0, 18), P["dach_sklep"], "SmoothPlastic"),
        (5.0, 8.0, 1.2, 3.4, (12, 20, -8), P["neon_magia"], "Neon"),
    ]
    for x, zz, s, h, obr, c, m in gr:
        rola = "neon" if m == "Neon" else "akcent"
        z.blok("Kryształ", (s, h, s), (x, h * 0.42, zz), c, g, obr, baza=b, m=m, rola=rola,
               t=0.15 if m == "Glass" else 0.0)
    z.kula("Skała matka", 6.0, (-1.0, -1.2, -6.0), "4A3A78", g, baza=b)
    z.kula("Skała matka", 3.6, (9.5, -0.8, -6.5), "4A3A78", g, baza=b)


AKCENTY = {"miasteczko": akcent_miasteczko, "las": akcent_las, "bagno": akcent_bagno, "dzungla": akcent_dzungla,
           "pustynia": akcent_pustynia, "gory": akcent_gory, "lodowiec": akcent_lodowiec, "wulkan": akcent_wulkan,
           "krysztal": akcent_krysztal}


# ------------------------------------------------------------------ elementy wspólne
def plytka(z, g, b, k, w, d, grub):
    z.blok("Wierzch", (w, 1.2, d), (0, -0.6, 0), k["kolor_gruntu"], g, baza=b, rola="grunt")
    z.blok("Tusz krawędzi", (w + 0.8, 0.5, d + 0.8), (0, -1.3, 0), TUSZ, g, baza=b, rola="tusz")
    z.blok("Podłoże", (w - 1.0, grub - 1.4, d - 1.0), (0, -1.4 - (grub - 1.4) / 2, 0), k["kolor_podloza"], g,
           baza=b, rola="grunt")
    z.blok("Korzeń wyspy", (w - 7.0, 2.6, d - 7.0), (0, -grub - 1.0, 0), k["kolor_podloza"], g, baza=b,
           rola="grunt")
    z.blok("Droga", (w, 0.2, 4.0), (0, 0.1, 0), k["kolor_drogi"], g, baza=b, rola="grunt")


def tabliczka(z, g, b, k, d, wym, nachylenie):
    sz, wy = wym
    a = math.radians(nachylenie)
    gora = [0.0, math.cos(a), -math.sin(a)]                   # oś „w górę” tabliczki (prostopadła do kierunku na kamerę)
    szczyt = [0.0, -0.4, d / 2 + 0.5]                          # górna krawędź tuż pod przednią krawędzią płytki
    srodek = [szczyt[i] - gora[i] * wy / 2 for i in range(3)]
    R = ku_kamerze(nachylenie)
    rama = b.razy(srodek, R)
    z.dodaj("Tabliczka", (sz, wy, 0.6), rama, P["drewno_jasne"], g, rola="tabliczka", napis=k["napis"])
    z.dodaj("Tusz tabliczki", (sz + 0.9, wy + 0.9, 0.4), rama.razy((0, 0, 0.45)), TUSZ, g, rola="tusz")
    for sx in (-sz * 0.36, sz * 0.36):
        z.dodaj("Uchwyt", (0.8, 2.4, 0.8), rama.razy((sx, wy / 2 + 0.6, 0.7)), P["drewno_ciemne"], g)


def klodka(z, g, b, y, nachylenie):
    rama = b.razy((0, y, 6.0), ku_kamerze(nachylenie * 0.6))
    gk = g + "/Klodka"
    z.dodaj("Kłódka — tusz", (7.2, 6.0, 0.6), rama.razy((0, 0, 0.9)), TUSZ, gk, rola="klodka", cien=False)
    z.dodaj("Kłódka", (6.4, 5.2, 2.2), rama, P["zloto"], gk, rola="klodka", cien=False)
    z.dodaj("Dziurka", (1.1, 1.1, 0.3), rama.razy((0, 0.6, -1.15)), TUSZ, gk, rola="klodka", cien=False)
    z.dodaj("Dziurka — szpara", (0.5, 1.4, 0.3), rama.razy((0, -0.5, -1.15)), TUSZ, gk, rola="klodka", cien=False)
    for sx in (-2.0, 2.0):
        z.dodaj("Kabłąk", (1.0, 3.4, 1.0), rama.razy((sx, 3.6, 0)), P["tynk_blekit"], gk, rola="klodka", cien=False)
    z.dodaj("Kabłąk", (5.0, 1.0, 1.0), rama.razy((0, 5.3, 0)), P["tynk_blekit"], gk, rola="klodka", cien=False)


def wskaznik(z, x0, y, nachylenie):
    """Złota strzałka nad wskazaną krainą (dwa kliny tworzą grot skierowany w dół)."""
    # pochylona jak kłódka (0,55 kąta kamery): zwrócona wprost do kamery, ze słońcem za kamerą, cała łapała
    # odblask i w grze wyglądała na wyblakłą (zrzuty 17.11.2026)
    rama = Rama((x0, y, 0), ku_kamerze(nachylenie * 0.55))
    g = "Wskaznik"
    k = 1.6  # skala strzałki (na telefonie musi być widać ją z daleka)
    z.dodaj("Trzon", (2.0 * k, 4.4 * k, 1.2 * k), rama.razy((0, 2.2 * k, 0)), P["zloto"], g, rola="wskaznik", cien=False)
    z.dodaj("Trzon — tusz", (2.8 * k, 5.0 * k, 0.6), rama.razy((0, 2.2 * k, 0.8 * k)), TUSZ, g, rola="wskaznik",
            cien=False)
    h, d = 4.0 * k, 3.4 * k
    # klin lewy i prawy (patrz opis w README: wierzchołek kąta prostego w (0; 0), czubek w (0; −h))
    lewy = kolumny([0, 0, 1], [0, -1, 0], [1, 0, 0])
    prawy = kolumny([0, 0, -1], [0, -1, 0], [-1, 0, 0])
    z.dodaj("Grot", (1.2 * k, h, d), rama.razy((-d / 2, -h / 2, 0), lewy), P["zloto"], g, k="WedgePart",
            rola="wskaznik", cien=False)
    z.dodaj("Grot", (1.2 * k, h, d), rama.razy((d / 2, -h / 2, 0), prawy), P["zloto"], g, k="WedgePart",
            rola="wskaznik", cien=False)
    z.dodaj("Grot — tusz", (0.6, h + 1.4, d + 1.3), rama.razy((-(d + 1.3) / 2, -(h + 1.4) / 2 + 0.35, 0.8 * k), lewy),
            TUSZ, g, k="WedgePart", rola="wskaznik", cien=False)
    z.dodaj("Grot — tusz", (0.6, h + 1.4, d + 1.3), rama.razy(((d + 1.3) / 2, -(h + 1.4) / 2 + 0.35, 0.8 * k), prawy),
            TUSZ, g, k="WedgePart", rola="wskaznik", cien=False)
    return rama


def pinezka(z, x0, d):
    """Czerwona chorągiewka „tu jesteś” na przednim lewym rogu płytki."""
    g = "Pinezka"
    b = Rama((x0 - 11.5, 0, d / 2 - 2.5))
    z.blok("Maszt", (0.6, 9.0, 0.6), (0, 4.5, 0), TUSZ, g, baza=b, rola="pinezka", cien=False)
    z.blok("Flaga", (4.2, 2.6, 0.4), (2.2, 7.6, 0), P["czerwien"], g, (0, 0, -6), baza=b, rola="pinezka", cien=False)
    z.blok("Flaga — tusz", (4.8, 3.2, 0.2), (2.2, 7.6, -0.3), TUSZ, g, (0, 0, -6), baza=b, rola="pinezka", cien=False)
    z.kula("Gałka", 1.2, (0, 9.2, 0), P["zloto"], g, baza=b, rola="pinezka", cien=False)
    return b


def chmury(z, dane, polowa):
    md = dane["makieta"]
    los = random.Random(md["chmury_ziarno"])
    y0 = md["chmury_morze_y"]
    biel = dane["chmury"]["kolor"]
    cien = dane["chmury"]["kolor_cienia"]
    g = "Chmury"
    z.blok("Morze chmur", (2048, 2, 2048), (0, y0 - 1, 0), "F2F6FF", g, rola="chmura", cien=False)
    w, d = md["plytka"]

    def oblok(x, y, zz, s):
        """Komiksowy obłok: duża kula z czterema mniejszymi dookoła; spód chowa się w morzu chmur."""
        rama = Rama((x, y, zz), orient(0, los.uniform(0, 360), 0))
        for dx, dy, dz, f in ((0, 0.12, 0, 1.0), (-0.52, -0.02, 0.06, 0.72), (0.5, -0.04, -0.04, 0.66),
                              (0.12, 0.02, -0.3, 0.78), (-0.15, -0.08, 0.34, 0.52)):
            z.kula("Obłok", s * f, (dx * s, dy * s, dz * s), biel if f > 0.6 else cien, g, baza=rama, rola="chmura",
                   cien=False)

    # obłoki między płytkami i pod nimi (wierzch poniżej spodu płytek), trochę z przodu i z tyłu pasa
    for i in range(16):
        x = -polowa - 30 + (2 * polowa + 60) * (i + los.uniform(0.1, 0.9)) / 16
        zz = los.choice((-1, 1)) * los.uniform(d / 2 + 4, 40)
        s = los.uniform(14, 24)
        oblok(x, min(y0 + s * 0.15, -8 - s * 0.62), zz, s)
    # wielkie obłoki za końcami pasa i daleko za pasem — nigdy między kamerą a płytkami
    for i in range(10):
        s = los.uniform(40, 70)
        if i % 2:
            x = (1 if i % 4 == 1 else -1) * los.uniform(polowa + 20 + s * 0.6, polowa + 230)
            zz = los.uniform(-150, 40)
        else:
            x = los.uniform(-polowa - 150, polowa + 150)
            zz = -los.uniform(90, 260)
        oblok(x, y0 + s * 0.12, zz, s)
    # pierwszy plan: obłoki u dołu kadru (bliżej kamery), poniżej linii wzroku na tabliczki
    for i in range(6):
        x = -polowa + 2 * polowa * (i + los.uniform(0.2, 0.8)) / 6
        oblok(x, y0 + 4, los.uniform(55, 95), los.uniform(22, 34))


# ------------------------------------------------------------------ całość
def polowa_dlugosci(dane):
    md = dane["makieta"]
    w = md["plytka"][0]
    n = len(dane["krainy"])
    return (n * w + (n - 1) * md["przerwa"]) / 2


def srodki(dane):
    md = dane["makieta"]
    w = md["plytka"][0]
    krok = w + md["przerwa"]
    n = len(dane["krainy"])
    return [(i - (n - 1) / 2) * krok for i in range(n)]


def zbuduj_czesci(dane):
    md = dane["makieta"]
    nach = dane["kamera"]["nachylenie_stopnie"]
    w, d = md["plytka"]
    z = Zbior()
    xs = srodki(dane)
    licz = {}
    for i, (k, x0) in enumerate(zip(dane["krainy"], xs)):
        g = "Krainy/" + k["id"]
        b = Rama((x0, 0, 0))
        przed = len(z.czesci)
        plytka(z, g, b, k, w, d, md["grubosc"])
        AKCENTY[k["id"]](z, g, b)
        tabliczka(z, g, b, k, d, md["tabliczka"], nach)
        if k["id"] != "miasteczko":
            klodka(z, g, b, md["klodka_y"], nach)
        if i < len(xs) - 1:
            gap = md["przerwa"]
            z.blok("Mostek", (gap + 0.6, 0.5, 4.0), (x0 + w / 2 + gap / 2, -0.25, 0), P["drewno"], g, rola="grunt")
            z.blok("Mostek — tusz", (gap + 0.6, 0.3, 4.6), (x0 + w / 2 + gap / 2, -0.6, 0), TUSZ, g, rola="tusz")
        licz[k["id"]] = len(z.czesci) - przed
    przed = len(z.czesci)
    chmury(z, dane, polowa_dlugosci(dane))
    licz["chmury"] = len(z.czesci) - przed
    przed = len(z.czesci)
    wskaznik(z, xs[0], md["wskaznik_y"], nach)
    pinezka(z, xs[0], d)
    licz["wskaznik i pinezka"] = len(z.czesci) - przed
    info = {"srodki_x": xs, "polowa_dlugosci": polowa_dlugosci(dane), "liczba": licz, "razem": len(z.czesci)}
    return z.czesci, info


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(TU, "krainy.json"), encoding="utf-8") as f:
        dane = json.load(f)
    czesci, info = zbuduj_czesci(dane)
    for k, v in info["liczba"].items():
        print("  %-20s %4d części" % (k, v))
    print("razem: %d części; półdługość pasa %.1f; środki x: %s" % (
        info["razem"], info["polowa_dlugosci"], ", ".join("%.0f" % x for x in info["srodki_x"])))


if __name__ == "__main__":
    main()
