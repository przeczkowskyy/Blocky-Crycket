#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator smoka z klocków (bez wgrywania): jeden generator, osiem stadiów z parametrów w ustawienia.json → "smok".

    python -B swiat/ewolucja/smok.py            # liczba części na stadium

Układ jak we wzorcach Pet Areny: ziemia y = 0, przód −Z, część „Korzen” w (0, 0, 0) jako PrimaryPart. Każda część ma
grupę ruchu (atrybut „Grupa”): 1–4 nogi (LP, PP, LT, PT), 6 głowa, 7 szczęka, 8/9 skrzydło L/P, 11+ kolejne segmenty
ogona; model ma atrybuty „Pivot<k>” (punkt obrotu grupy w skali 1). Ręcznie zrobiony model z takimi nazwami grup
i punktami obrotu wejdzie bez zmian w kodzie.
"""
import math


def _c(L, n, poz, roz, kolor, mat="SmoothPlastic", ksztalt="Block", obrot=(0, 0, 0), przez=0, grupa=0):
    L.append({"n": n, "p": [round(x, 3) for x in poz], "s": [round(max(0.05, x), 3) for x in roz], "c": kolor, "m": mat, "k": ksztalt,
              "r": [round(x, 4) for x in obrot], "t": przez, "g": grupa})


def stadium(P):
    """P: parametry stadium (proporcje, dodatki, kolory) → {"czesci": [...], "pivoty": {k: [x, y, z]}, "promien", "wysokosc"}."""
    L, piv = [], {}
    g = P.get("grubosc", 1.0)
    Lg = 1.0 * P.get("nogi", 1.0)
    Hb, Wb, Lb = 1.2 * g, 1.4 * g, 2.4 * P.get("dlugosc", 1.0)
    k1, k2, k3, k4 = P["kolor"], P["brzuch"], P["blona"], P["rogi_kolor"]
    swiat = P.get("swiecenie")
    mat_ciala = P.get("material", "SmoothPlastic")
    yb = Lg + Hb / 2
    _c(L, "Korzen", (0, 0, 0), (1, 1, 1), k1, przez=1)
    _c(L, "Korpus", (0, yb, 0), (Wb, Hb, Lb), k1, mat_ciala)
    _c(L, "Brzuch", (0, Lg + 0.12, 0), (Wb * 0.82, 0.26, Lb * 0.8), k2)
    _c(L, "Piers", (0, yb - 0.05, -Lb / 2 - 0.2), (Wb * 0.86, Hb * 0.9, 0.5), k2)
    # szyja i głowa
    ns = P.get("szyja", 1)
    x, y, z = 0.0, Lg + Hb * 0.72, -Lb / 2 - 0.25
    for i in range(ns):
        z -= 0.5
        y += 0.32
        _c(L, "Szyja%d" % (i + 1), (0, y, z), (0.75 * g, 0.75 * g, 0.75), k1, mat_ciala)
    hs = P.get("glowa", 1.0)
    hz, hy = z - 0.35 - hs * 0.5, y + hs * 0.25
    piv[6] = [0, y, z]
    _c(L, "Glowa", (0, hy, hz), (hs * 1.0, hs * 0.85, hs * 1.1), k1, mat_ciala, grupa=6)
    _c(L, "Pysk", (0, hy + hs * 0.05, hz - hs * 0.8), (hs * 0.78, hs * 0.42, hs * 0.65), k1, mat_ciala, grupa=6)
    _c(L, "Nozdrza", (0, hy + hs * 0.28, hz - hs * 1.05), (hs * 0.5, hs * 0.08, hs * 0.12), "1B1424", grupa=6)
    piv[7] = [0, hy - hs * 0.2, hz - hs * 0.45]
    _c(L, "Szczeka", (0, hy - hs * 0.28, hz - hs * 0.75), (hs * 0.7, hs * 0.22, hs * 0.62), k2, grupa=7)
    for s in (-1, 1):
        oko = "FFE14D" if not swiat else "7FF8FF"
        _c(L, "Oko", (s * hs * 0.42, hy + hs * 0.16, hz - hs * 0.45), (hs * 0.16, hs * 0.2, hs * 0.2), oko, "Neon", grupa=6)
        rg = P.get("rogi", 0.5) * hs
        if rg > 0:
            _c(L, "Rog", (s * hs * 0.32, hy + hs * 0.5 + rg * 0.2, hz + hs * 0.35 + rg * 0.35), (hs * 0.18, hs * 0.18, rg), k4, "SmoothPlastic", "Block",
               (math.radians(35), s * math.radians(12), 0), grupa=6)
    if P.get("grzebien"):
        for i in range(3):
            _c(L, "Grzebien", (0, hy + hs * 0.5 + 0.12, hz - hs * 0.2 + i * hs * 0.32), (hs * 0.12, hs * (0.42 - i * 0.08), hs * 0.25), k3,
               "Neon" if swiat else "SmoothPlastic", grupa=6)
    # nogi (1 LP, 2 PP, 3 LT, 4 PT) — biodro to punkt obrotu
    for k, (sx, sz) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1)), 1):
        lx, lz = sx * Wb * 0.36, sz * Lb * 0.3
        piv[k] = [lx, Lg, lz]
        _c(L, "Noga", (lx, Lg - Lg * 0.27, lz), (0.55 * g, Lg * 0.6, 0.62 * g), k1, mat_ciala, grupa=k)
        _c(L, "Lydka", (lx, Lg * 0.32, lz + 0.05), (0.46 * g, Lg * 0.42, 0.5 * g), k1, mat_ciala, grupa=k)
        _c(L, "Stopa", (lx, 0.12, lz - 0.14), (0.62 * g, 0.24, 0.82 * g), k4, grupa=k)
    # ogon: segmenty łańcuchem (grupy 11+), czubek z kolcem
    nt = P.get("ogon", 4)
    ty, tz = Lg + Hb * 0.45, Lb / 2
    for i in range(nt):
        sz = 0.72 * g * (1 - i / (nt + 1)) + 0.14
        piv[11 + i] = [0, ty, tz]
        _c(L, "Ogon%d" % (i + 1), (0, ty - 0.04, tz + 0.42), (sz, sz, 0.9), k1, mat_ciala, grupa=11 + i)
        tz += 0.82
        ty -= 0.08
    _c(L, "OgonKolec", (0, ty, tz + 0.15), (0.12, 0.42, 0.42), k4 if not swiat else k3, "Neon" if swiat else "SmoothPlastic", "Wedge",
       (0, 0, 0), grupa=10 + nt)
    # skrzydła (8 L, 9 P): złożone wzdłuż boku; ramię + błony
    sk = P.get("skrzydla", 0.0)
    for k, s in ((8, -1), (9, 1)):
        rx, ry, rz = s * Wb * 0.42, Lg + Hb * 0.95, -Lb * 0.18
        piv[k] = [rx, ry, rz]
        if sk < 0.3:
            _c(L, "Paczek", (rx + s * 0.1, ry + 0.12, rz + 0.2), (0.22, 0.3, 0.45), k3, grupa=k)
            continue
        dl = 1.8 * sk
        _c(L, "Ramie", (rx + s * 0.08, ry + 0.25, rz + dl * 0.45), (0.22, 0.22, dl), k1, mat_ciala, "Block", (math.radians(-10), 0, 0), grupa=k)
        for j in range(2):
            _c(L, "Blona", (rx + s * 0.12, ry - 0.05 - j * 0.05, rz + dl * (0.3 + 0.38 * j)), (0.08, 0.75 * sk, dl * 0.5), k3, "SmoothPlastic",
               "Block", (0, 0, s * math.radians(14)), grupa=k)
    # kolce na grzbiecie
    nk = P.get("kolce", 0)
    for i in range(nk):
        f = (i + 0.5) / max(1, nk)
        _c(L, "Kolec", (0, Lg + Hb + 0.18, -Lb * 0.45 + Lb * 0.95 * f), (0.16, 0.42 + 0.1 * (i % 2), 0.36), k3 if swiat else k4,
           "Neon" if swiat else "SmoothPlastic", "Wedge", (0, math.pi, 0))
    if P.get("plyty"):
        for s in (-1, 1):
            for z0 in (-Lb * 0.25, Lb * 0.2):
                _c(L, "Plyta", (s * (Wb / 2 + 0.05), yb + 0.1, z0), (0.14, Hb * 0.7, Lb * 0.3), P.get("plyty_kolor", "6A6E7E"), "Metal")
    if swiat:
        for s in (-1, 1):
            _c(L, "Poswiata", (s * (Wb / 2 + 0.02), Lg + 0.3, 0), (0.06, 0.12, Lb * 0.85), k3, "Neon")
    xs = [abs(c["p"][0]) + c["s"][0] / 2 for c in L]
    zs = [c["p"][2] for c in L]
    return {"czesci": L, "pivoty": {str(k): [round(v, 3) for v in p] for k, p in piv.items()},
            "promien": round(max(Wb / 2 + 0.3, (Lb + 1.2) * 0.38), 3), "wysokosc": round(max(c["p"][1] + c["s"][1] / 2 for c in L), 3),
            "dlugosc": round(max(zs) - min(zs), 2), "szerokosc": round(2 * max(xs), 2)}


if __name__ == "__main__":
    import json
    import os
    U = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ustawienia.json"), encoding="utf-8"))
    for F in U["formy_smok"]:
        S = stadium(F["smok"])
        print("%-15s części %3d  promień %.2f  wysokość %.2f" % (F["nazwa"], len(S["czesci"]), S["promien"], S["wysokosc"]))
