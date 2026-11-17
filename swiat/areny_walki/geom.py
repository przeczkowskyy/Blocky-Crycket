# -*- coding: utf-8 -*-
"""Geometria części z czesci.json dla aren walki: obrót jak CFrame.fromOrientation, chmura punktów bryły, przejście
między układem SCENY walki a światem Studio.

Układ sceny (jak Ustawienia.scena() w swiat/test_walki2): początek = środek płyty placu, X w prawo na ekranie (gracz
po lewej, przeciwnik po prawej), Y w górę, Z ku kamerze planu ogólnego. Scena stoi w świecie jako
CFrame.lookAt(O, O + (0, 0, 1)) — obrót o 180° wokół pionu: świat = (Ox − x, Oy + y, Oz − z).
Kształty: panel/luau/KSZTALTY.md (kula = min wymiaru, walec o osi X z promieniem min(sy, sz)/2, klin, klin narożny).
"""
import math

import numpy as np

BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4


def macierz(rx, ry, rz):
    """R = Ry · Rx · Rz (radiany) — jak CFrame.fromOrientation."""
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return np.array(((cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx),
                     (cx * sz, cx * cz, -sx),
                     (-sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx)))


def katy(R):
    """Odwrotność `macierz`: (rx, ry, rz) w radianach (jak CFrame:ToOrientation)."""
    sx = max(-1.0, min(1.0, -R[1][2]))
    rx = math.asin(sx)
    if abs(sx) > 0.999999:
        return rx, math.atan2(-R[2][0], R[0][0]), 0.0
    return rx, math.atan2(R[0][2], R[2][2]), math.atan2(R[1][0], R[1][1])


def polowki(c):
    ks, sx, sy, sz = c[0], c[8], c[9], c[10]
    if ks == KULA:
        d = min(sx, sy, sz)
        return np.array((d / 2.0, d / 2.0, d / 2.0))
    if ks == WALEC:
        r = min(sy, sz) / 2.0
        return np.array((sx / 2.0, r, r))
    return np.array((sx / 2.0, sy / 2.0, sz / 2.0))


def punkty(c, krok=1.0, maks=28):
    """Chmura punktów wypełniająca bryłę części (siatka z brzegami, przycięta do kształtu), w układzie części → świat
    pliku (tym samym, w którym zapisano część)."""
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
    return L @ macierz(c[5], c[6], c[7]).T + np.array((c[2], c[3], c[4]))


def gora(c):
    """Najwyższy punkt części (skrzynka z obrotem)."""
    R = macierz(c[5], c[6], c[7])
    return c[3] + float((np.abs(R) @ polowki(c))[1])


def dol(c):
    R = macierz(c[5], c[6], c[7])
    return c[3] - float((np.abs(R) @ polowki(c))[1])


R180 = macierz(0.0, math.pi, 0.0)


def do_swiata(c, O):
    """Wiersz części z układu sceny do świata (scena = CFrame.lookAt(O, O + (0, 0, 1)))."""
    w = list(c)
    w[2], w[3], w[4] = round(O[0] - c[2], 3), round(O[1] + c[3], 3), round(O[2] - c[4], 3)
    rx, ry, rz = katy(R180 @ macierz(c[5], c[6], c[7]))
    w[5], w[6], w[7] = round(rx, 4), round(ry, 4), round(rz, 4)
    return w


def do_sceny_punkty(P, O):
    """Punkty świata (n, 3) → układ sceny."""
    P = np.asarray(P, float)
    return np.stack((O[0] - P[:, 0], P[:, 1] - O[1], O[2] - P[:, 2]), axis=1)


def do_sceny(c, O):
    """Wiersz części ze świata do układu sceny (odwrotność do_swiata — ten sam obrót 180°)."""
    w = list(c)
    w[2], w[3], w[4] = O[0] - c[2], c[3] - O[1], O[2] - c[4]
    rx, ry, rz = katy(R180 @ macierz(c[5], c[6], c[7]))
    w[5], w[6], w[7] = rx, ry, rz
    return w
