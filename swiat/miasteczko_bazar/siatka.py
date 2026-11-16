# -*- coding: utf-8 -*-
"""Siatka chodzenia po bazarze (wspólna dla sprawdz.py i podglad.py): przeszkody z czesci.json, poszerzenie o promień
postaci, odległości z miejsca startu (Dijkstra, 8 kierunków) i czasy biegu przy 16 st/s.

Przeszkoda = część z kolizją, której bryła wchodzi w pas ciała gracza: od 1,4 nad zerem (wyżej niż stopnie, progi
i posadzki — te się przechodzi) do 0,3 + 5,6 (wzrost postaci ok. 5,3 + zapas). Rzut na ziemię = obwiednia wypukła
wierzchołków bryły (dla bloków i klinów dokładna, dla walców i kul — prostokąt opisany, czyli ostrożnie).
"""
import heapq
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import macierz_obrotu  # noqa: E402

KROK = 0.5
PROMIEN = 2.0              # pół szerokości postaci z rękami (ok. 4)
Y_STOPIEN = 1.4            # wszystko, co kończy się niżej, da się przejść (stopnie ≤ 0,5, progi, posadzki)
Y_GLOWA = 0.3 + 5.6        # wszystko, co zaczyna się wyżej, jest nad głową


def wierzcholki(c):
    hx, hy, hz = c[8] / 2.0, c[9] / 2.0, c[10] / 2.0
    R = np.array(macierz_obrotu(math.degrees(c[5]), math.degrees(c[6]), math.degrees(c[7])))
    V = np.array([(sx * hx, sy * hy, sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
    return V @ R.T + np.array((c[2], c[3], c[4]))


def _otoczka(p):
    """Obwiednia wypukła punktów 2D (monotoniczny łańcuch)."""
    p = sorted(set(map(tuple, np.round(p, 4))))
    if len(p) <= 2:
        return p

    def krzyz(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    dol, gora = [], []
    for q in p:
        while len(dol) >= 2 and krzyz(dol[-2], dol[-1], q) <= 0:
            dol.pop()
        dol.append(q)
    for q in reversed(p):
        while len(gora) >= 2 and krzyz(gora[-2], gora[-1], q) <= 0:
            gora.pop()
        gora.append(q)
    return dol[:-1] + gora[:-1]


class Siatka:
    def __init__(self, dane, U, krok=KROK, promien=PROMIEN):
        self.X0, self.Z0 = U["swiat"]["X0"], U["swiat"]["Z0"]
        g = U["granice"]
        self.x0, self.x1 = g["pole_gry_x"][0] - 3.0, g["pole_gry_x"][1] + 3.0
        self.z0, self.z1 = g["pole_gry_z"][0] - 3.0, g["pole_gry_z"][1] + 3.0
        self.krok = krok
        self.nx = int(round((self.x1 - self.x0) / krok))
        self.nz = int(round((self.z1 - self.z0) / krok))
        img = Image.new("L", (self.nx, self.nz), 0)
        d = ImageDraw.Draw(img)
        self.przeszkody = []                                  # (indeks części, nazwa, grupa)
        for i, c in enumerate(dane["czesci"]):
            if len(c) > 15 and int(c[15]) & 1:
                continue                                      # bez kolizji
            W = wierzcholki(c)
            ymin, ymax = W[:, 1].min(), W[:, 1].max()
            if ymax <= Y_STOPIEN or ymin >= Y_GLOWA:
                continue
            xs, zs = W[:, 0] - self.X0, W[:, 2] - self.Z0
            if xs.max() < self.x0 or xs.min() > self.x1 or zs.max() < self.z0 or zs.min() > self.z1:
                continue
            ot = _otoczka(np.stack(((xs - self.x0) / krok, (zs - self.z0) / krok), axis=1))
            if len(ot) >= 3:
                d.polygon(ot, fill=255)
            else:
                d.line(ot, fill=255, width=1)
            self.przeszkody.append((i, c[14], dane["grupy"][c[1]]))
        self.surowe = np.array(img) > 0                       # [iz, ix]
        r = int(math.ceil(promien / krok))
        yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
        kolo = (xx * xx + yy * yy) * krok * krok <= promien * promien
        pad = np.pad(self.surowe, r, constant_values=True)
        zaj = np.zeros_like(self.surowe)
        for dy, dx in zip(*np.nonzero(kolo)):
            zaj |= pad[dy:dy + self.nz, dx:dx + self.nx]
        self.zajete = zaj
        self.odl = None

    def komorka(self, x, z):
        return int((z - self.z0) / self.krok), int((x - self.x0) / self.krok)

    def punkt(self, iz, ix):
        return self.x0 + (ix + 0.5) * self.krok, self.z0 + (iz + 0.5) * self.krok

    def najblizsza_wolna(self, x, z, maks=2.0):
        iz, ix = self.komorka(x, z)
        r = int(maks / self.krok)
        best = None
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                a, b = iz + dz, ix + dx
                if 0 <= a < self.nz and 0 <= b < self.nx and not self.zajete[a, b]:
                    dd = dx * dx + dz * dz
                    if best is None or dd < best[0]:
                        best = (dd, a, b)
        return None if best is None else (best[1], best[2], math.sqrt(best[0]) * self.krok)

    def z_punktu(self, x, z):
        """Dijkstra (8 kierunków) z punktu (x, z) bazaru po wolnych komórkach → tablica odległości w studach."""
        start = self.najblizsza_wolna(x, z)
        if start is None:
            raise ValueError("start w przeszkodzie")
        odl = np.full((self.nz, self.nx), np.inf)
        odl[start[0], start[1]] = 0.0
        kol = [(0.0, start[0], start[1])]
        k = self.krok
        ruchy = [(-1, 0, k), (1, 0, k), (0, -1, k), (0, 1, k), (-1, -1, k * 1.41421), (-1, 1, k * 1.41421),
                 (1, -1, k * 1.41421), (1, 1, k * 1.41421)]
        zaj = self.zajete
        while kol:
            dd, a, b = heapq.heappop(kol)
            if dd > odl[a, b]:
                continue
            for da, db, w in ruchy:
                na, nb = a + da, b + db
                if 0 <= na < self.nz and 0 <= nb < self.nx and not zaj[na, nb]:
                    if da and db and (zaj[a, nb] or zaj[na, b]):
                        continue
                    nd = dd + w
                    if nd < odl[na, nb]:
                        odl[na, nb] = nd
                        heapq.heappush(kol, (nd, na, nb))
        self.odl = odl
        return odl

    def droga_do(self, x, z, tolerancja=1.5):
        """Odległość (study) z ostatniego z_punktu do (x, z): najbliższa osiągnięta komórka w promieniu `tolerancja`."""
        iz, ix = self.komorka(x, z)
        r = int(tolerancja / self.krok)
        best = math.inf
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                a, b = iz + dz, ix + dx
                if 0 <= a < self.nz and 0 <= b < self.nx and np.isfinite(self.odl[a, b]):
                    best = min(best, self.odl[a, b] + math.hypot(dx, dz) * self.krok)
        return best

    def sciezka(self, x, z):
        """Najkrótsza droga (lista punktów bazaru) z ostatniego z_punktu do (x, z) — spadek po tablicy odległości."""
        iz, ix = self.komorka(x, z)
        r = int(1.5 / self.krok)
        best = None
        for dz in range(-r, r + 1):
            for dx in range(-r, r + 1):
                a, b = iz + dz, ix + dx
                if 0 <= a < self.nz and 0 <= b < self.nx and np.isfinite(self.odl[a, b]):
                    if best is None or self.odl[a, b] < best[0]:
                        best = (self.odl[a, b], a, b)
        if best is None:
            return []
        _, a, b = best
        pts = [self.punkt(a, b)]
        for _ in range(20000):
            if self.odl[a, b] == 0:
                break
            nxt = None
            for da in (-1, 0, 1):
                for db in (-1, 0, 1):
                    na, nb = a + da, b + db
                    if (da or db) and 0 <= na < self.nz and 0 <= nb < self.nx and self.odl[na, nb] < self.odl[a, b]:
                        if nxt is None or self.odl[na, nb] < self.odl[nxt[0], nxt[1]]:
                            nxt = (na, nb)
            if nxt is None:
                break
            a, b = nxt
            pts.append(self.punkt(a, b))
        return pts[::-1]
