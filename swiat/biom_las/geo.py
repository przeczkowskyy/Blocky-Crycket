# -*- coding: utf-8 -*-
"""Geometria i model wysokości biomu Las — wspólne dla generuj.py, sprawdz.py, wezly.py i plan.py.

Układ lasu: środek Starego Ukłonu (0; 0), północ lasu = −Z, y = 0 to poziom łąki. Punkty płaskie zapisujemy (x, z).

Teren (uklad.json → „teren”) to lista elementów w kolejności nakładania:
- „poziom”: prosty wielokąt z wierzchem na y (w Studio pryzmat z klinów od ziemi do y; wyższe poziomy mogą stać na niższych,
  zatoki w wielokącie odsłaniają poziom pod spodem — tam stoją rampy);
- „kopiec”: walec r z wierzchem na y i pierścień zbocza do r_stopy (z klinów);
- „rampa”: klin od punktu (x, z, y) do punktu (x, z, y) o szerokości szer; nadpisuje wszystko pod sobą.
Wysokość H(x, z) liczy się w tej samej kolejności: ostatni pasujący poziom wygrywa, kopiec działa tylko na gruncie 0,
rampa zawsze. Ta sama funkcja steruje budową, kontrolą i planem, więc kontrola sprawdza dokładnie to, co powstaje.
"""
import json
import math
import os

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
BIEG = 16.0                     # bieg gracza, studs/s
WZROST_GRACZA = 5.7


def wczytaj(nazwa):
    with open(os.path.join(TU, nazwa), encoding="utf-8") as f:
        return json.load(f)


# =========================================================================== płaska geometria
def w_wielokacie(p, w):
    x, z = p
    wew = False
    j = len(w) - 1
    for i in range(len(w)):
        xi, zi = w[i]
        xj, zj = w[j]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi:
            wew = not wew
        j = i
    return wew


def w_wielokacie_np(X, Z, w):
    wew = np.zeros(X.shape, dtype=bool)
    n = len(w)
    for i in range(n):
        xi, zi = w[i]
        xj, zj = w[i - 1]
        if zi == zj:
            continue
        m = (zi > Z) != (zj > Z)
        xc = (xj - xi) * (Z - zi) / (zj - zi) + xi
        wew ^= m & (X < xc)
    return wew


def odl_odcinek(p, a, b):
    ax, az = a
    dx, dz = b[0] - ax, b[1] - az
    l2 = dx * dx + dz * dz
    t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - az) * dz) / l2))
    return math.hypot(p[0] - (ax + t * dx), p[1] - (az + t * dz))


def odl_lamana(p, pts, zamknieta=False):
    pp = list(pts) + ([pts[0]] if zamknieta else [])
    return min(odl_odcinek(p, pp[i], pp[i + 1]) for i in range(len(pp) - 1))


def odl_lamana_np(X, Z, pts):
    d = np.full(X.shape, 1e9)
    for i in range(len(pts) - 1):
        ax, az = pts[i]
        bx, bz = pts[i + 1]
        dx, dz = bx - ax, bz - az
        l2 = dx * dx + dz * dz or 1e-9
        t = np.clip(((X - ax) * dx + (Z - az) * dz) / l2, 0.0, 1.0)
        d = np.minimum(d, np.hypot(X - (ax + t * dx), Z - (az + t * dz)))
    return d


def odl_wielokat(p, w):
    """Odległość ze znakiem od brzegu wielokąta: ujemna w środku."""
    d = odl_lamana(p, w, zamknieta=True)
    return -d if w_wielokacie(p, w) else d


def dlugosc(pts):
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def przeciecie(a, b, c, d):
    def cr(o, p, q):
        return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])
    d1, d2, d3, d4 = cr(c, d, a), cr(c, d, b), cr(a, b, c), cr(a, b, d)
    if (d1 > 0) != (d2 > 0) and (d3 > 0) != (d4 > 0):
        t = d1 / (d1 - d2)
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return None


def samoprzeciecia(w):
    """Lista par krawędzi wielokąta, które się przecinają (pusta = wielokąt prosty)."""
    n = len(w)
    zle = []
    for i in range(n):
        a, b = w[i], w[(i + 1) % n]
        for j in range(i + 1, n):
            if j == i or (j + 1) % n == i or (i + 1) % n == j:
                continue
            c, d = w[j], w[(j + 1) % n]
            if przeciecie(a, b, c, d):
                zle.append((i, j))
    return zle


def pole(w):
    return 0.5 * sum(w[i - 1][0] * w[i][1] - w[i][0] * w[i - 1][1] for i in range(len(w)))


def okrag(c, r, n=24):
    return [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def punkty_co(pts, krok):
    """Punkty łamanej co `krok` (z końcami) i kierunek w każdym: [(x, z, dx, dz), …]."""
    wyn = []
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        dl = math.dist(a, b)
        if dl < 1e-6:
            continue
        n = max(1, int(math.ceil(dl / krok)))
        ex, ez = (b[0] - a[0]) / dl, (b[1] - a[1]) / dl
        for k in range(n):
            t = k / n
            wyn.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]), ex, ez))
    if len(pts) >= 2:
        a, b = pts[-2], pts[-1]
        dl = math.dist(a, b) or 1.0
        wyn.append((b[0], b[1], (b[0] - a[0]) / dl, (b[1] - a[1]) / dl))
    return wyn


def triangulacja(w):
    """Ear clipping prostego wielokąta → lista trójkątów (trzy punkty)."""
    pts = [tuple(p) for p in w]
    if pole(pts) < 0:
        pts.reverse()
    idx = list(range(len(pts)))
    tr = []

    def wypukly(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) > 1e-9

    def w_trojkacie(p, a, b, c):
        def s(p1, p2, p3):
            return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
        d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
        return not ((d1 < 0 or d2 < 0 or d3 < 0) and (d1 > 0 or d2 > 0 or d3 > 0))

    proby = 0
    while len(idx) > 3 and proby < 10000:
        proby += 1
        n = len(idx)
        ucho = False
        for k in range(n):
            i0, i1, i2 = idx[k - 1], idx[k], idx[(k + 1) % n]
            a, b, c = pts[i0], pts[i1], pts[i2]
            if not wypukly(a, b, c):
                continue
            if any(w_trojkacie(pts[j], a, b, c) for j in idx if j not in (i0, i1, i2)):
                continue
            tr.append((a, b, c))
            idx.pop(k)
            ucho = True
            break
        if not ucho:
            raise ValueError("triangulacja: wielokąt nie jest prosty")
    tr.append(tuple(pts[i] for i in idx))
    return tr


def wygladz(pts, podzial=4):
    """Catmull-Rom przez punkty łamanej (końce zostają)."""
    if len(pts) < 3:
        return [tuple(p) for p in pts]
    p = [pts[0]] + list(pts) + [pts[-1]]
    wyn = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(podzial):
            t = k / podzial
            t2, t3 = t * t, t * t * t
            wyn.append(tuple(0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    wyn.append(tuple(pts[-1]))
    return wyn


# =========================================================================== model wysokości
class Teren:
    """Wysokość gruntu H(x, z) z elementów „teren” w uklad.json."""

    def __init__(self, U):
        self.U = U
        self.elementy = U["teren"]
        self.poziomy = [e for e in self.elementy if e["rodzaj"] == "poziom"]
        self.kopce = [e for e in self.elementy if e["rodzaj"] == "kopiec"]
        self.rampy = [e for e in self.elementy if e["rodzaj"] == "rampa"]
        self._siatka = None

    @staticmethod
    def kopiec_h(e, r):
        if r <= e["r"]:
            return float(e["y"])
        if r >= e["r_stopy"]:
            return 0.0
        return e["y"] * (e["r_stopy"] - r) / (e["r_stopy"] - e["r"])

    @staticmethod
    def rampa_t(e, x, z):
        (ax, az, ay), (bx, bz, by) = e["od"], e["do"]
        dx, dz = bx - ax, bz - az
        dl = math.hypot(dx, dz)
        t = ((x - ax) * dx + (z - az) * dz) / (dl * dl)
        lat = abs((x - ax) * (-dz) + (z - az) * dx) / dl
        return t, lat

    def poziom_w(self, x, z):
        """Element „poziom”, na którym stoi punkt (ostatni pasujący), albo None."""
        wyn = None
        for e in self.poziomy:
            if w_wielokacie((x, z), e["wielokat"]):
                wyn = e
        return wyn

    def rampa_w(self, x, z, zapas=0.0):
        for e in self.rampy:
            t, lat = self.rampa_t(e, x, z)
            if -zapas / 60.0 <= t <= 1.0 + zapas / 60.0 and lat <= e["szer"] / 2.0 + zapas:
                return e
        return None

    def H(self, x, z):
        p = self.poziom_w(x, z)
        h = float(p["y"]) if p else 0.0
        if p is None:
            for e in self.kopce:
                h = max(h, self.kopiec_h(e, math.hypot(x - e["srodek"][0], z - e["srodek"][1])))
        for e in self.rampy:
            t, lat = self.rampa_t(e, x, z)
            if 0.0 <= t <= 1.0 and lat <= e["szer"] / 2.0:
                h = e["od"][2] + t * (e["do"][2] - e["od"][2])
        return h

    def H_np(self, X, Z):
        h = np.zeros(X.shape)
        jest = np.zeros(X.shape, dtype=bool)
        for e in self.poziomy:
            m = w_wielokacie_np(X, Z, e["wielokat"])
            h[m] = e["y"]
            jest |= m
        for e in self.kopce:
            r = np.hypot(X - e["srodek"][0], Z - e["srodek"][1])
            hk = np.clip((e["r_stopy"] - r) / (e["r_stopy"] - e["r"]), 0.0, 1.0) * e["y"]
            h = np.where(jest, h, np.maximum(h, hk))
        for e in self.rampy:
            (ax, az, ay), (bx, bz, by) = e["od"], e["do"]
            dx, dz = bx - ax, bz - az
            dl = math.hypot(dx, dz)
            t = ((X - ax) * dx + (Z - az) * dz) / (dl * dl)
            lat = np.abs((X - ax) * (-dz) + (Z - az) * dx) / dl
            m = (t >= 0) & (t <= 1) & (lat <= e["szer"] / 2.0)
            h = np.where(m, ay + t * (by - ay), h)
        return h

    def siatka(self, krok=2.0, zakres=500.0):
        """(xs, zs, H) — wysokości w środkach kratek krok × krok na płycie ±zakres (z pamięcią)."""
        if self._siatka is None or self._siatka[0] != (krok, zakres):
            xs = np.arange(-zakres + krok / 2, zakres, krok)
            X, Z = np.meshgrid(xs, xs)            # H[i, j]: z = xs[i], x = xs[j]
            self._siatka = ((krok, zakres), xs, self.H_np(X, Z))
        return self._siatka[1], self._siatka[1], self._siatka[2]

    def plaskosc(self, x, z, r):
        """(min, max) wysokości w kole o promieniu r (próbki co 2)."""
        hs = [self.H(x + dx, z + dz) for dx in np.arange(-r, r + 0.01, 2.0) for dz in np.arange(-r, r + 0.01, 2.0)
              if dx * dx + dz * dz <= r * r]
        return min(hs), max(hs)


def profil(teren, pts, krok=1.0):
    """Wysokości wzdłuż łamanej co krok: [(x, z, h), …]."""
    return [(x, z, teren.H(x, z)) for x, z, _, _ in punkty_co(pts, krok)]


def uskoki(teren, pts, krok=1.0, maks=0.6):
    """Miejsca, gdzie wysokość na łamanej skacze o więcej niż `maks` na krok (urwisko na drodze)."""
    pr = profil(teren, pts, krok)
    return [(pr[i][0], pr[i][1], pr[i + 1][2] - pr[i][2]) for i in range(len(pr) - 1)
            if abs(pr[i + 1][2] - pr[i][2]) > maks]


# =========================================================================== woda
def woda_odl(U, x, z):
    """Odległość od brzegu najbliższej wody (ujemna w wodzie)."""
    best = 1e9
    for w in U["woda"]:
        if w["rodzaj"] == "struga":
            pol = max(w["szer"]) / 2.0
            best = min(best, odl_lamana((x, z), w["pts"]) - pol)
        elif "wielokat" in w:
            best = min(best, odl_wielokat((x, z), w["wielokat"]))
        else:
            best = min(best, math.hypot(x - w["srodek"][0], z - w["srodek"][1]) - w["r"])
    return best


# =========================================================================== sieć ścieżek i czasy biegu
def czasy_od_wejscia(U):
    """Najkrótsze drogi po ścieżkach od punktu wejścia: (słownik węzeł → studs, funkcja lokacja → sekundy)."""
    import heapq
    kraw = {}

    def wezel(p):
        return (round(p[0], 1), round(p[1], 1))

    for sc in U["sciezki"]:
        for i in range(len(sc["pts"]) - 1):
            a, b = wezel(sc["pts"][i]), wezel(sc["pts"][i + 1])
            d = math.dist(a, b)
            kraw.setdefault(a, []).append((b, d))
            kraw.setdefault(b, []).append((a, d))
    start = wezel(U["wejscie"]["punkt"])
    dist = {start: 0.0}
    q = [(0.0, start)]
    while q:
        d, u = heapq.heappop(q)
        if d > dist[u]:
            continue
        for v, w in kraw.get(u, []):
            if d + w < dist.get(v, 1e18):
                dist[v] = d + w
                heapq.heappush(q, (d + w, v))

    def do_lokacji(l):
        best = None
        for k, d in dist.items():
            r = math.hypot(k[0] - l["x"], k[1] - l["z"])
            if r > l["r"] + 25:
                continue
            c = d + max(0.0, r - l["r"])
            best = c if best is None else min(best, c)
        return None if best is None else best / BIEG

    return dist, kraw, do_lokacji
