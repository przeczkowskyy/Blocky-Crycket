# -*- coding: utf-8 -*-
"""Zasady miejsca w pasie liczone NA PRAWDZIWYCH CZĘŚCIACH (generator odrzuca rzecz, która je łamie; sprawdz.py
zgłasza złamania jako błędy). Jedna implementacja dla obu, więc kontrola sprawdza dokładnie to, czego pilnował generator.

Część zamieniamy w chmurę punktów wypełniającą jej bryłę (siatka co ok. 1 st, przycięta do kształtu: blok, kula,
walec o osi X, klin, klin narożny — geometria z panel/luau/KSZTALTY.md) i pytamy o punkty:
- PLAC   żaden punkt na wysokości 1,6–18 nie leży bliżej niż 12 (poziomo) od węzła walki ani miejsca Strażnika;
- SCIEZKA żaden punkt na wysokości 0,6–7 nie leży na ścieżce (pas 8 st + 0,3 zapasu) — poza mostkiem (pomost jest
          drogą), bramą Bagna (zamknięta z założenia) i półprzezroczystą mgłą;
- OTWARCIE w otwarciu przejścia nic nie sięga wyżej niż `wys_w_otwarciu` z planu (+0,1), do 12 nad gruntem;
- PETLA   pętle potworów wolne: nic na wysokości 0,6–6 bliżej niż 2 od pętli;
- KAMERA  krzywa przelotu kamery (ta sama co w sprawdz_plan.py, próbki co 0,05 s) nie wchodzi bliżej niż 2 w żadną część;
- GRANICE skrzynka części mieści się w pasie z kulisami i tłem (u −34…966, |v| ≤ 90).
Grunt (wierzch ≤ 0,45) i części niewidzialne (przezroczystość ≥ 0,98) nie łamią tych zasad.
"""
import math
import os
import sys

import numpy as np

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las.pas.sprawdz_plan import krzywa_kamery  # noqa: E402
from swiat.las_pas.kontekst import ODCINKI_SCIEZKI, PLAC_R, SZER_SCIEZKI, U_MAX, U_MIN, v_sciezki  # noqa: E402

BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4
GRUNT_MAX = 0.45
PLAC_Y = (1.6, 18.0)
SCIEZKA_Y = (0.6, 7.0)
SCIEZKA_ZAPAS = 0.3
PETLA_R, PETLA_Y = 2.0, (0.6, 6.0)
KAMERA_R = 2.0
OTWARCIE_Y_MAX = 12.0
V_GRANICA = 90.0


def macierz(rx, ry, rz):
    """R = Ry · Rx · Rz (radiany) — jak CFrame.fromOrientation (scena.macierz_obrotu w stopniach)."""
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return np.array(((cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx),
                     (cx * sz, cx * cz, -sx),
                     (-sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx)))


def polowki(c):
    """Połówki wymiarów bryły w układzie części (kula: średnica = min, walec: oś X, promień = min(sy, sz)/2)."""
    ks, sx, sy, sz = c[0], c[8], c[9], c[10]
    if ks == KULA:
        d = min(sx, sy, sz)
        return np.array((d / 2.0, d / 2.0, d / 2.0))
    if ks == WALEC:
        r = min(sy, sz) / 2.0
        return np.array((sx / 2.0, r, r))
    return np.array((sx / 2.0, sy / 2.0, sz / 2.0))


def aabb(c):
    """(min xyz, max xyz) skrzynki osiowej części (z obrotem)."""
    R = macierz(c[5], c[6], c[7])
    E = polowki(c)
    h = np.abs(R) @ E
    p = np.array((c[2], c[3], c[4]))
    return p - h, p + h


def punkty(c, krok=1.0, maks=36):
    """Chmura punktów wypełniająca bryłę części (świat). Siatka z brzegami, przycięta do kształtu."""
    E = polowki(c)
    osie = []
    for h in E:
        n = int(min(maks, max(2, math.ceil(2 * h / krok) + 1)))
        osie.append(np.linspace(-h, h, n))
    L = np.stack(np.meshgrid(*osie, indexing="ij"), axis=-1).reshape(-1, 3)
    ks = c[0]
    hx, hy, hz = E
    e = 1e-6
    if ks == KULA:
        L = L[np.linalg.norm(L, axis=1) <= hx + e]
    elif ks == WALEC:
        L = L[np.hypot(L[:, 1], L[:, 2]) <= hy + e]
    elif ks == KLIN and hz > 0:
        L = L[L[:, 1] <= hy * L[:, 2] / hz + e]
    elif ks == NAROZNIK and hx > 0 and hz > 0:
        L = L[L[:, 1] <= np.minimum(hy * L[:, 0] / hx, -hy * L[:, 2] / hz) + e]
    if not len(L):
        L = np.zeros((1, 3))
    R = macierz(c[5], c[6], c[7])
    return L @ R.T + np.array((c[2], c[3], c[4]))


def _probki_lamanej(pts, krok):
    wyn = []
    for (ax, az), (bx, bz) in zip(pts, pts[1:]):
        dl = math.hypot(bx - ax, bz - az)
        n = max(1, int(math.ceil(dl / krok)))
        for k in range(n):
            t = k / n
            wyn.append((ax + (bx - ax) * t, az + (bz - az) * t))
    wyn.append(tuple(pts[-1]))
    return wyn


class Zasady:
    """Dane zasad w układzie ŚWIATA (części w czesci.json są w świecie)."""

    def __init__(self, K):
        X0, Z0 = K.X0, K.Z0
        self.X0, self.Z0 = X0, Z0
        self.wezly = np.array([(X0 + u, Z0 + v) for u, v in K.wezly])
        self.wezly_opis = ["%s (%.0f;%.0f)" % (st["id"], u, v) for st in K.strefy for u, v in st["trasa"]] + \
                          ["Strażnik (%.0f;%.0f)" % tuple(K.straznik["miejsce"])]
        self.odcinki = [(X0 + a, X0 + b) for a, b in ODCINKI_SCIEZKI]
        petle = []
        for st in K.strefy:
            for x, z in _probki_lamanej(st["trasa"] + [st["trasa"][0]], 1.0):
                petle.append((X0 + x, Z0 + z, st["id"]))
        self.petle = np.array([(a, b) for a, b, _ in petle])
        self.petle_id = [i for _, _, i in petle]
        self.otwarcia = []
        for t in K.P["przejscia"]:
            o1, o2 = t["otwarcie"]
            self.otwarcia.append((t["id"], X0 + t["u_od"], X0 + t["u_do"], Z0 + o1 + 0.2, Z0 + o2 - 0.2,
                                  t["wys_w_otwarciu"] + 0.1))
        kam = krzywa_kamery(K.P["przelot_kamery"]["punkty"])
        self.kamera = np.array([(X0 + u, y, Z0 + v) for _, u, v, y in kam])
        self.kamera_t = [t for t, _, _, _ in kam]

    # --- zwolnienia
    def naruszenia(self, c, grupa, tylko=None):
        """Lista złamanych zasad przez część c (wiersz czesci.json) w grupie `grupa` (pełna ścieżka)."""
        mn, mx = aabb(c)
        if tylko is None or "granice" in tylko:
            if mn[0] - self.X0 < U_MIN - 0.05 or mx[0] - self.X0 > U_MAX + 0.05 or abs(mn[2] - self.Z0) > V_GRANICA                     or abs(mx[2] - self.Z0) > V_GRANICA:
                return ["granice pasa"]
        if c[13] >= 0.98:
            return []
        if mx[1] <= GRUNT_MAX + 1e-6:
            return []
        wyn = []
        P = None

        def pkt():
            nonlocal P
            if P is None:
                P = punkty(c)
            return P

        nazwa = c[14]
        most = nazwa.startswith("Most ")
        brama = "/BramaBagna/" in grupa
        mgla = 0.0 < c[13] < 0.98
        # PLAC
        if (tylko is None or "plac" in tylko) and mx[1] >= PLAC_Y[0] and mn[1] <= PLAC_Y[1]:
            cx, cz = (mn[0] + mx[0]) / 2.0, (mn[2] + mx[2]) / 2.0
            zasieg = math.hypot(mx[0] - mn[0], mx[2] - mn[2]) / 2.0 + PLAC_R
            bliskie = np.nonzero(np.hypot(self.wezly[:, 0] - cx, self.wezly[:, 1] - cz) < zasieg)[0]
            if len(bliskie):
                Q = pkt()
                Q = Q[(Q[:, 1] >= PLAC_Y[0]) & (Q[:, 1] <= PLAC_Y[1])]
                for i in bliskie:
                    if len(Q) and np.min(np.hypot(Q[:, 0] - self.wezly[i, 0], Q[:, 2] - self.wezly[i, 1])) < PLAC_R:
                        wyn.append("plac walki %s" % self.wezly_opis[i])
        # ŚCIEŻKA
        if (tylko is None or "sciezka" in tylko) and not (most or brama or mgla) and mx[1] >= SCIEZKA_Y[0] \
                and mn[1] <= SCIEZKA_Y[1]:
            for a, b in self.odcinki:
                if mx[0] < a or mn[0] > b:
                    continue
                Q = pkt()
                Q = Q[(Q[:, 1] >= SCIEZKA_Y[0]) & (Q[:, 1] <= SCIEZKA_Y[1]) & (Q[:, 0] >= a) & (Q[:, 0] <= b)]
                if not len(Q):
                    continue
                os_ = np.array([v_sciezki(x - self.X0) for x in Q[:, 0]]) + self.Z0
                if np.any(np.abs(Q[:, 2] - os_) < SZER_SCIEZKI / 2.0 + SCIEZKA_ZAPAS):
                    wyn.append("ścieżka (u ≈ %.0f)" % (float(np.median(Q[:, 0])) - self.X0))
                    break
        # OTWARCIA
        if tylko is None or "otwarcie" in tylko:
            for tid, u1, u2, z1, z2, ymax in self.otwarcia:
                if mx[0] <= u1 or mn[0] >= u2 or mx[2] <= z1 or mn[2] >= z2 or mx[1] <= ymax or mn[1] >= OTWARCIE_Y_MAX:
                    continue
                Q = pkt()
                if np.any((Q[:, 0] > u1) & (Q[:, 0] < u2) & (Q[:, 2] > z1) & (Q[:, 2] < z2) & (Q[:, 1] > ymax)
                          & (Q[:, 1] < OTWARCIE_Y_MAX)):
                    wyn.append("otwarcie przejścia %s (wyżej niż %.1f)" % (tid, ymax - 0.1))
        # PĘTLE
        if (tylko is None or "petla" in tylko) and not mgla and mx[1] >= PETLA_Y[0] and mn[1] <= PETLA_Y[1]:
            blisko = np.nonzero((self.petle[:, 0] > mn[0] - PETLA_R) & (self.petle[:, 0] < mx[0] + PETLA_R)
                                & (self.petle[:, 1] > mn[2] - PETLA_R) & (self.petle[:, 1] < mx[2] + PETLA_R))[0]
            if len(blisko):
                Q = pkt()
                Q = Q[(Q[:, 1] >= PETLA_Y[0]) & (Q[:, 1] <= PETLA_Y[1])]
                if len(Q):
                    for i in blisko:
                        if np.min(np.hypot(Q[:, 0] - self.petle[i, 0], Q[:, 2] - self.petle[i, 1])) < PETLA_R:
                            wyn.append("pętla potworów %s" % self.petle_id[i])
                            break
        # KAMERA
        if tylko is None or "kamera" in tylko:
            blisko = np.nonzero((self.kamera[:, 0] > mn[0] - KAMERA_R) & (self.kamera[:, 0] < mx[0] + KAMERA_R)
                                & (self.kamera[:, 1] > mn[1] - KAMERA_R) & (self.kamera[:, 1] < mx[1] + KAMERA_R)
                                & (self.kamera[:, 2] > mn[2] - KAMERA_R) & (self.kamera[:, 2] < mx[2] + KAMERA_R))[0]
            if len(blisko):
                Q = pkt()
                for i in blisko:
                    if np.min(np.linalg.norm(Q - self.kamera[i], axis=1)) < KAMERA_R:
                        wyn.append("przelot kamery (t ≈ %.1f s)" % self.kamera_t[i])
                        break
        return wyn

    def ok(self, s, n0):
        """Czy wszystkie części dodane od indeksu n0 spełniają zasady (generator: postaw albo wycofaj)."""
        for c in s.czesci[n0:]:
            if self.naruszenia(c, s.grupy[c[1]]):
                return False
        return True


def postaw(s, Z, budowa):
    """Zbuduj rzecz; jeśli łamie zasady, wycofaj jej części. Zwraca True, gdy rzecz została."""
    n0 = len(s.czesci)
    budowa()
    if Z.ok(s, n0):
        return True
    del s.czesci[n0:]
    return False
