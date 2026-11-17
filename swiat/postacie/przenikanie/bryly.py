# -*- coding: utf-8 -*-
"""Bryły rigu z klocków (wiersze `czesci` z roblox_klocki.rig()) jako dokładne kształty Roblox: odległość ze znakiem
(SDF), punkty próbne, przecięcie z promieniem. Wszystko w numpy, w układzie LOKALNYM bryły.

Geometria kształtów wg pomiarów w Studio (panel/luau/KSZTALTY.md, 12.11.2026):
  blok        prostopadłościan ±h
  kula        (Shape = Ball) kula o średnicy min(sx, sy, sz)
  walec       (Shape = Cylinder) oś wzdłuż X, długość sx, średnica min(sy, sz)
  klin        (WedgePart) blok ∩ {y ≤ hy·z/hz} — pionowa ściana po stronie +Z, skos opada ku −Z
  naroznik    (CornerWedgePart) blok ∩ {y ≤ hy·x/hx} ∩ {y ≤ −hy·z/hz} — wierzchołek (hx, hy, −hz)
  elipsoida   blok z SpecialMesh „Sphere” (półosie h)
  walec_elip  blok z SpecialMesh „Cylinder” (oś X jak walec części — tak zakłada roblox_klocki.rozloz; półosie hy, hz)

SDF < 0 wewnątrz. Dla bloku, walca i kuli jest dokładny po obu stronach; dla klina i narożnika to max(blok, płaszczyzny):
wewnątrz DOKŁADNY (odległość do brzegu przecięcia zbiorów wypukłych = najmniejsza z odległości do ich brzegów), na
zewnątrz przy krawędzi skosu zaniża odległość (bezpiecznie: „bliżej, niż jest”). Elipsoida i walec eliptyczny —
przybliżenie (żaden bohater ich nie ma; są u Trolla i Muchomornika).
"""
import math

import numpy as np

BLOK, KULA, WALEC, KLIN, NAROZNIK, ELIPSOIDA, WALEC_ELIP = range(7)
NAZWY_KSZTALTOW = ["blok", "kula", "walec", "klin", "naroznik", "elipsoida", "walec_elip"]


def rodzaj(ks, siatka):
    """Kolumny `czesci` (ks = kształt części, siatka = typ SpecialMesh albo "") -> rodzaj bryły."""
    if siatka == "Sphere":
        return ELIPSOIDA
    if siatka == "Cylinder":
        return WALEC_ELIP
    if siatka == "Wedge":
        return KLIN
    if siatka == "CornerWedge":
        return NAROZNIK
    return {0: BLOK, 1: KULA, 2: WALEC, 3: KLIN, 4: NAROZNIK}[int(ks)]


# --------------------------------------------------------------------------- SDF
def _sdf_blok(p, h):
    q = np.abs(p) - h
    zew = np.sqrt(np.sum(np.maximum(q, 0.0) ** 2, axis=-1))
    wew = np.minimum(np.max(q, axis=-1), 0.0)
    return zew + wew


def sdf(r, h, p):
    """Odległość ze znakiem punktów p (..., 3) od bryły rodzaju r o połówkach h (3,) albo (..., 3)."""
    h = np.asarray(h, dtype=float)
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    hx, hy, hz = h[..., 0], h[..., 1], h[..., 2]
    if r == BLOK:
        return _sdf_blok(p, h)
    if r == KLIN:
        s1 = _sdf_blok(p, h)
        s2 = (y * hz - z * hy) / np.sqrt(hy * hy + hz * hz)
        return np.maximum(s1, s2)
    if r == NAROZNIK:
        s1 = _sdf_blok(p, h)
        s2 = (y * hx - x * hy) / np.sqrt(hx * hx + hy * hy)
        s3 = (y * hz + z * hy) / np.sqrt(hz * hz + hy * hy)
        return np.maximum(s1, np.maximum(s2, s3))
    if r == WALEC:
        rad = np.minimum(hy, hz)
        d1 = np.abs(x) - hx
        d2 = np.sqrt(y * y + z * z) - rad
        return np.minimum(np.maximum(d1, d2), 0.0) + np.sqrt(np.maximum(d1, 0.0) ** 2 + np.maximum(d2, 0.0) ** 2)
    if r == KULA:
        rad = np.minimum(np.minimum(hx, hy), hz)
        return np.sqrt(x * x + y * y + z * z) - rad
    if r == ELIPSOIDA:
        k0 = np.sqrt((x / hx) ** 2 + (y / hy) ** 2 + (z / hz) ** 2)
        k1 = np.sqrt((x / hx ** 2) ** 2 + (y / hy ** 2) ** 2 + (z / hz ** 2) ** 2)
        mn = np.minimum(np.minimum(hx, hy), hz)
        return np.where(k1 > 1e-12, k0 * (k0 - 1.0) / np.maximum(k1, 1e-12), -mn)
    if r == WALEC_ELIP:
        d1 = np.abs(x) - hx
        k0 = np.sqrt((y / hy) ** 2 + (z / hz) ** 2)
        k1 = np.sqrt((y / hy ** 2) ** 2 + (z / hz ** 2) ** 2)
        d2 = np.where(k1 > 1e-12, k0 * (k0 - 1.0) / np.maximum(k1, 1e-12), -np.minimum(hy, hz))
        return np.minimum(np.maximum(d1, d2), 0.0) + np.sqrt(np.maximum(d1, 0.0) ** 2 + np.maximum(d2, 0.0) ** 2)
    raise ValueError("nieznany rodzaj bryły %r" % r)


# --------------------------------------------------------------------------- punkty próbne
def wierzcholki(r, h):
    hx, hy, hz = h
    if r == KLIN:
        return [(sx * hx, -hy, sz * hz) for sx in (-1, 1) for sz in (-1, 1)] + [(sx * hx, hy, hz) for sx in (-1, 1)]
    if r == NAROZNIK:
        return [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (hx, hy, -hz)]
    if r in (BLOK,):
        return [(sx * hx, sy * hy, sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    if r in (WALEC, WALEC_ELIP):
        a = min(hy, hz) if r == WALEC else None
        wyn = []
        for i in range(16):
            t = 2 * math.pi * i / 16
            ry, rz = (a, a) if r == WALEC else (hy, hz)
            for sx in (-1, 1):
                wyn.append((sx * hx, ry * math.cos(t), rz * math.sin(t)))
        return wyn
    if r in (KULA, ELIPSOIDA):
        if r == KULA:
            a = min(h)
            hh = (a, a, a)
        else:
            hh = h
        wyn = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    v = np.array([i, j, k], dtype=float)
                    n = np.linalg.norm(v)
                    if n > 0:
                        wyn.append(tuple(v / n * np.array(hh)))
        return wyn
    return []


def punkty_probne(r, h, krok):
    """Siatka punktów WEWNĄTRZ bryły (z brzegiem) co najwyżej co `krok` studa + wierzchołki kształtu, układ lokalny."""
    h = np.asarray(h, dtype=float)
    osie = [np.linspace(-h[i], h[i], max(2, int(math.ceil(2 * h[i] / krok)) + 1)) for i in range(3)]
    g = np.stack(np.meshgrid(*osie, indexing="ij"), axis=-1).reshape(-1, 3)
    if r != BLOK:
        g = g[sdf(r, h, g) <= 1e-9]
    w = np.array(wierzcholki(r, tuple(h)), dtype=float).reshape(-1, 3)
    return np.concatenate([g, w], axis=0) if len(w) else g


def w_srodku(r, h, p, tol=1e-9):
    return sdf(r, h, p) <= tol


# --------------------------------------------------------------------------- promienie (kamera i podgląd)
def _plaszczyzny(r, h):
    """Bryła wielościenna jako przecięcie półprzestrzeni n·p ≤ d (lista (n, d)) albo None (bryły krzywe)."""
    hx, hy, hz = h
    pl = [((1, 0, 0), hx), ((-1, 0, 0), hx), ((0, 1, 0), hy), ((0, -1, 0), hy), ((0, 0, 1), hz), ((0, 0, -1), hz)]
    if r == BLOK:
        return pl
    if r == KLIN:
        n = np.array([0.0, hz, -hy])
        return pl + [(tuple(n / np.linalg.norm(n)), 0.0)]
    if r == NAROZNIK:
        n1 = np.array([-hy, hx, 0.0])
        n2 = np.array([0.0, hz, hy])
        return pl + [(tuple(n1 / np.linalg.norm(n1)), 0.0), (tuple(n2 / np.linalg.norm(n2)), 0.0)]
    return None


def przedzialy(r, h, o, d):
    """Przedział [t_we, t_wy] prostej o + t·d (t dowolnego znaku) wewnątrz bryły, układ lokalny; brak = (inf, −inf).
    Tylko bryły wielościenne i kule/elipsoidy/walce (wszystkie rodzaje). o, d: (N, 3)."""
    h = np.asarray(h, dtype=float)
    n = len(o)
    pl = _plaszczyzny(r, tuple(h))
    if pl is not None:
        t_we = np.full(n, -np.inf)
        t_wy = np.full(n, np.inf)
        for nv, dd in pl:
            nv = np.array(nv, dtype=float)
            den = d @ nv
            num = dd - o @ nv
            rown = np.abs(den) < 1e-12
            t = np.where(rown, 0.0, num / np.where(rown, 1.0, den))
            t_we = np.where(den < -1e-12, np.maximum(t_we, t), t_we)
            t_wy = np.where(den > 1e-12, np.minimum(t_wy, t), t_wy)
            t_wy = np.where(rown & (num < 0), -np.inf, t_wy)
        brak = t_we > t_wy
        return np.where(brak, np.inf, t_we), np.where(brak, -np.inf, t_wy)
    if r in (KULA, ELIPSOIDA):
        hh = np.array([min(h)] * 3) if r == KULA else h
        os_, ds = o / hh, d / hh
        a = np.sum(ds * ds, axis=1)
        b = 2 * np.sum(os_ * ds, axis=1)
        c = np.sum(os_ * os_, axis=1) - 1
        delta = b * b - 4 * a * c
        sq = np.sqrt(np.maximum(delta, 0))
        ok = delta >= 0
        return np.where(ok, (-b - sq) / (2 * a), np.inf), np.where(ok, (-b + sq) / (2 * a), -np.inf)
    ry, rz = (min(h[1], h[2]),) * 2 if r == WALEC else (h[1], h[2])
    hx = h[0]
    oy, oz, dy, dz = o[:, 1] / ry, o[:, 2] / rz, d[:, 1] / ry, d[:, 2] / rz
    a = dy * dy + dz * dz
    b = 2 * (oy * dy + oz * dz)
    c = oy * oy + oz * oz - 1
    delta = b * b - 4 * a * c
    sq = np.sqrt(np.maximum(delta, 0))
    zly = a < 1e-14
    a_ = np.where(zly, 1.0, a)
    tc0 = np.where(zly, np.where(c <= 0, -np.inf, np.inf), (-b - sq) / (2 * a_))
    tc1 = np.where(zly, np.where(c <= 0, np.inf, -np.inf), (-b + sq) / (2 * a_))
    tc0 = np.where(~zly & (delta < 0), np.inf, tc0)
    tc1 = np.where(~zly & (delta < 0), -np.inf, tc1)
    dx, ox = d[:, 0], o[:, 0]
    rx = np.abs(dx) < 1e-12
    dx_ = np.where(rx, 1.0, dx)
    tx0 = np.where(rx, np.where(np.abs(ox) <= hx, -np.inf, np.inf), np.minimum((-hx - ox) / dx_, (hx - ox) / dx_))
    tx1 = np.where(rx, np.where(np.abs(ox) <= hx, np.inf, -np.inf), np.maximum((-hx - ox) / dx_, (hx - ox) / dx_))
    t_we, t_wy = np.maximum(tc0, tx0), np.minimum(tc1, tx1)
    brak = t_we > t_wy
    return np.where(brak, np.inf, t_we), np.where(brak, -np.inf, t_wy)


KIERUNKI_26 = np.array([(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)],
                       dtype=float)
KIERUNKI_26 /= np.linalg.norm(KIERUNKI_26, axis=1, keepdims=True)


def glebokosc_w_sumie(P, R_osi, bryly_strefy):
    """Głębokość punktów P (n, 3, świat) w SUMIE brył strefy: najmniejsza po kierunkach odległość do wyjścia z sumy
    (promień z punktu, kolejne przedziały brył sklejane). Kierunki: 26 w osiach R_osi (n, 3, 3 — osie bryły, w której
    punkt siedzi najgłębiej: dla pojedynczego bloku wynik dokładny) i 26 w osiach świata. Wynik ≥ prawdziwej
    głębokości (najwyżej o ok. 10% przy sumie o skośnych ścianach), 0 dla punktów na zewnątrz.
    bryly_strefy = [(rodzaj, połówki, R (3, 3), t (3,))]."""
    n = len(P)
    if n == 0:
        return np.zeros(0)
    D_lok = np.einsum("nij,kj->nki", R_osi, KIERUNKI_26)                 # (n, 26, 3) świat
    D = np.concatenate([D_lok, np.broadcast_to(KIERUNKI_26, (n, 26, 3))], axis=1).reshape(-1, 3)
    O = np.repeat(P, 52, axis=0)
    przedz = []
    for r, h, R, t in bryly_strefy:
        o = (O - t) @ R
        d = D @ R
        przedz.append(przedzialy(r, h, o, d))
    t_we = np.stack([p[0] for p in przedz], axis=1)                       # (m, K)
    t_wy = np.stack([p[1] for p in przedz], axis=1)
    e = np.where((t_we <= 1e-9) & (t_wy > 0), t_wy, 0.0).max(axis=1)      # wyjście z brył, w których punkt jest
    for _ in range(len(bryly_strefy)):
        nowe = np.where((t_we <= e[:, None] + 1e-6) & (t_wy > e[:, None]), t_wy, 0.0).max(axis=1)
        nowe = np.maximum(nowe, e)
        if np.all(nowe <= e + 1e-12):
            break
        e = nowe
    return e.reshape(n, 52).min(axis=1)


def przeciecie_promieni(r, h, o, d):
    """Pierwsze wejście promieni o + t·d (t > 0) w bryłę (układ lokalny). Zwraca (t, normalna) — t = inf: chybia.
    o, d: (N, 3)."""
    h = np.asarray(h, dtype=float)
    n = len(o)
    inf = np.full(n, np.inf)
    pl = _plaszczyzny(r, tuple(h))
    if pl is not None:
        t_we = np.full(n, -np.inf)
        t_wy = np.full(n, np.inf)
        nrm = np.zeros((n, 3))
        for nv, dd in pl:
            nv = np.array(nv, dtype=float)
            den = d @ nv
            num = dd - o @ nv
            rown = np.abs(den) < 1e-12
            t = np.where(rown, 0.0, num / np.where(rown, 1.0, den))
            wchodzi = den < -1e-12
            wychodzi = den > 1e-12
            lepsze = wchodzi & (t > t_we)
            t_we = np.where(lepsze, t, t_we)
            nrm[lepsze] = nv
            t_wy = np.where(wychodzi, np.minimum(t_wy, t), t_wy)
            # promień równoległy do płaszczyzny i na zewnątrz — chybia
            t_wy = np.where(rown & (num < 0), -np.inf, t_wy)
        traf = (t_we <= t_wy) & (t_wy > 1e-6)
        t = np.where(traf, np.maximum(t_we, 0.0), inf)
        return t, nrm
    if r in (KULA, ELIPSOIDA):
        hh = np.array([min(h)] * 3) if r == KULA else h
        os_ = o / hh
        ds = d / hh
        a = np.sum(ds * ds, axis=1)
        b = 2 * np.sum(os_ * ds, axis=1)
        c = np.sum(os_ * os_, axis=1) - 1
        delta = b * b - 4 * a * c
        ok = delta >= 0
        sq = np.sqrt(np.maximum(delta, 0))
        t0 = (-b - sq) / (2 * a)
        t1 = (-b + sq) / (2 * a)
        t = np.where(t0 > 1e-6, t0, np.where(t1 > 1e-6, 0.0, np.inf))
        t = np.where(ok, t, np.inf)
        p = o + d * np.where(np.isfinite(t), t, 0)[:, None]
        nrm = p / (hh * hh)
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
        return t, nrm
    # walec wzdłuż X (okrągły albo eliptyczny)
    ry, rz = (min(h[1], h[2]),) * 2 if r == WALEC else (h[1], h[2])
    hx = h[0]
    oy, oz, dy, dz = o[:, 1] / ry, o[:, 2] / rz, d[:, 1] / ry, d[:, 2] / rz
    a = dy * dy + dz * dz
    b = 2 * (oy * dy + oz * dz)
    c = oy * oy + oz * oz - 1
    delta = b * b - 4 * a * c
    sq = np.sqrt(np.maximum(delta, 0))
    zly = (a < 1e-14)
    a_ = np.where(zly, 1.0, a)
    tc0 = np.where(zly, np.where(c <= 0, -np.inf, np.inf), (-b - sq) / (2 * a_))
    tc1 = np.where(zly, np.where(c <= 0, np.inf, -np.inf), (-b + sq) / (2 * a_))
    tc0 = np.where(delta < 0, np.inf, tc0)
    tc1 = np.where(delta < 0, -np.inf, tc1)
    dx = d[:, 0]
    ox = o[:, 0]
    rx = np.abs(dx) < 1e-12
    dx_ = np.where(rx, 1.0, dx)
    tx0 = np.where(rx, np.where(np.abs(ox) <= hx, -np.inf, np.inf), np.minimum((-hx - ox) / dx_, (hx - ox) / dx_))
    tx1 = np.where(rx, np.where(np.abs(ox) <= hx, np.inf, -np.inf), np.maximum((-hx - ox) / dx_, (hx - ox) / dx_))
    t_we = np.maximum(tc0, tx0)
    t_wy = np.minimum(tc1, tx1)
    traf = (t_we <= t_wy) & (t_wy > 1e-6)
    t = np.where(traf, np.maximum(t_we, 0.0), np.inf)
    p = o + d * np.where(np.isfinite(t), t, 0)[:, None]
    nrm = np.zeros((n, 3))
    na_scianie = np.abs(np.abs(p[:, 0]) - hx) < 1e-6 * max(1.0, hx) + 1e-6
    nrm[:, 0] = np.where(na_scianie, np.sign(p[:, 0]), 0.0)
    nrm[:, 1] = np.where(na_scianie, 0.0, p[:, 1] / (ry * ry))
    nrm[:, 2] = np.where(na_scianie, 0.0, p[:, 2] / (rz * rz))
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    return t, nrm
