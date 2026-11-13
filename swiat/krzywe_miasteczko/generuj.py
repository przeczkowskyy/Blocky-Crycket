#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator mapy v2 „Krzywe Miasteczko” — składa całe miasto z modułów budynków i zestawu wspólnego.

    python -B swiat/krzywe_miasteczko/generuj.py [--przesun 0,0,-700] [--ziarno 7] [--wyj swiat/krzywe_miasteczko/czesci.json]

Kontrakt: PROJEKT.md (rozdz. 4 — układ, 6 — elementy wspólne), współrzędne z uklad.json. Układ miasta: środek rynku (0, 0),
ziemia y = 0, północ = −Z; w świecie Studio całość przesunięta o PRZESUNIECIE (domyślnie (0, 0, −700)).
Każdy budynek główny stoi we własnej grupie (NAZWA modułu), reszta w grupach tematycznych: Teren, Rynek, Ulice, Mur, DomyTla,
Stragany, Zielen, Tlo, Chmury, Rekwizyty, Spawn. Wynik deterministyczny (random.Random(ziarno)).

Poziomy nawierzchni (odstęp ≥ 0,05 między płaszczyznami różnych kolorów): trawa 0; podwórka (ziemia) 0,04; Podmurna 0,10;
szprychy 0,17; rynek i przedpola 0,25; płyty wzoru rynku 0,31; ścieżki-kody 0,38; krawężniki tusz 0,45.
Status: propozycja (noc 13.11.2026), nie kanon.
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

from swiat.biblioteka.scena import Scena, katy_z_macierzy, KULA, WALEC  # noqa: E402
from swiat.krzywe_miasteczko.paleta import PALETA, cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402

with open(os.path.join(TU, "uklad.json"), encoding="utf-8") as _f:
    U = json.load(_f)

# Stragany przestawione względem uklad.json: w PROJEKT 4.7 stragan_1 i stragan_5 zwężały wylot Bramnej do ok. 5 studów,
# stragan_2 stał w osi wylotu Arenowej, a stragan_3 zasłaniał wejście sklepu magicznego (kwadrat 8 × 8 przed drzwiami).
PRZESTAWIONE_STRAGANY = {"stragan_1": (-29.5, -15.5, 58.0), "stragan_2": (-29.0, 23.0, 128.0), "stragan_3": (27.5, -19.0, -55.0),
                         "stragan_5": (-9.5, -31.0, 17.0)}
for _st in U["stragany"]:
    if _st["id"] in PRZESTAWIONE_STRAGANY:
        _st["x"], _st["z"], _st["rot"] = PRZESTAWIONE_STRAGANY[_st["id"]]

MODULY = ["karczma", "zbrojownia", "sklep_magiczny", "wylegarnia", "brama_lochow", "stajnia", "brama_twierdzy", "gildia",
          "arena", "brama_miejska", "studnia_pomnik", "kolo_fortuny"]
G = {g["id"]: g for g in U["glowne"]}
ULICE = {u["id"]: u for u in U["ulice"]}
KOD = {"lochowa": "dach_lochy", "twierdzowa": "dach_twierdza", "gildyjna": "dach_gildia", "arenowa": "dach_arena",
       "bramna": "dach_brama"}
NAWIERZCHNIA = {"bramna": "bruk", "podmurna": "ziemia"}       # reszta: bruk_ciemny
Y_TRAWA, Y_PODWORKO, Y_PODMURNA, Y_SZPRYCHA, Y_RYNEK, Y_WZOR, Y_KOD, Y_KRAWEZNIK = 0.0, 0.04, 0.10, 0.17, 0.25, 0.31, 0.38, 0.45
SPAWN = tuple(U["spawn"])
KONIEC_LOCHOWEJ = 2                                             # Lochowa jako ulica do (76,3; 16,2), dalej rampa i niecka


# =========================================================================== geometria płaska (x, z)
def lok2sw(g, x, z):
    t = math.radians(g["rot"])
    c, s_ = math.cos(t), math.sin(t)
    return g["x"] + c * x + s_ * z, g["z"] - s_ * x + c * z


def sw2lok(g, px, pz):
    t = math.radians(g["rot"])
    c, s_ = math.cos(t), math.sin(t)
    dx, dz = px - g["x"], pz - g["z"]
    return c * dx - s_ * dz, s_ * dx + c * dz


def w_wielokacie(px, pz, wiel):
    wynik = False
    n = len(wiel)
    for i in range(n):
        (x1, z1), (x2, z2) = wiel[i], wiel[(i + 1) % n]
        if (z1 > pz) != (z2 > pz):
            xi = x1 + (pz - z1) * (x2 - x1) / (z2 - z1)
            if px < xi:
                wynik = not wynik
    return wynik


def odl_odcinek(px, pz, a, b):
    ex, ez = b[0] - a[0], b[1] - a[1]
    l2 = ex * ex + ez * ez
    t = 0.0 if l2 < 1e-9 else max(0.0, min(1.0, ((px - a[0]) * ex + (pz - a[1]) * ez) / l2))
    return math.hypot(px - a[0] - t * ex, pz - a[1] - t * ez)


def odl_lamana(px, pz, pts, zamknieta=False):
    n = len(pts)
    m = n if zamknieta else n - 1
    return min(odl_odcinek(px, pz, pts[i], pts[(i + 1) % n]) for i in range(m))


def odl_wielokat(px, pz, wiel):
    """Odległość ze znakiem: < 0 w środku wielokąta."""
    d = odl_lamana(px, pz, wiel, True)
    return -d if w_wielokacie(px, pz, wiel) else d


def pts_ulicy(uid):
    u = ULICE[uid]
    return u["pts"][:KONIEC_LOCHOWEJ + 1] if uid == "lochowa" else u["pts"]


# =========================================================================== rejestr zajętych miejsc (kontrola rozrzutu)
class Obrys:
    def __init__(self, nazwa, x, z, rot, w, d):
        self.nazwa, self.g, self.w, self.d = nazwa, {"x": x, "z": z, "rot": rot}, w, d

    def zawiera(self, px, pz, zapas=0.0):
        lx, lz = sw2lok(self.g, px, pz)
        return abs(lx) <= self.w / 2.0 + zapas and abs(lz) <= self.d / 2.0 + zapas


OBRYSY = []
for _g in U["glowne"]:
    OBRYSY.append(Obrys(_g["id"], _g["x"], _g["z"], _g["rot"], _g["w"], _g["d"]))
for _d in U["domy"]:
    OBRYSY.append(Obrys(_d["id"], _d["x"], _d["z"], _d["rot"], _d["w"], _d["d"]))
for _st in U["stragany"]:
    OBRYSY.append(Obrys(_st["id"], _st["x"], _st["z"], _st["rot"], _st["w"] + 2, _st["d"] + 2))
_K = G["karczma"]
_sx, _sz = lok2sw(_K, -3.0, 24.5)
OBRYSY.append(Obrys("schody_karczmy", _sx, _sz, _K["rot"], 28.0, 11.0))
_L = G["brama_lochow"]
_nx, _nz = lok2sw(_L, 0.0, 12.0)
OBRYSY.append(Obrys("niecka", _nx, _nz, _L["rot"], 34.0, 46.0))


def kolizja(px, pz, r=1.0, ulice=True, rynek=False, mur=True, pomin=()):
    """Nazwa pierwszej przeszkody w kole (px, pz, r) albo None."""
    for o in OBRYSY:
        if o.nazwa not in pomin and o.zawiera(px, pz, r):
            return o.nazwa
    if ulice:
        for uid, u in ULICE.items():
            if uid not in pomin and odl_lamana(px, pz, pts_ulicy(uid)) < u["szer"] / 2.0 + r + 0.5:
                return uid
    if rynek and odl_wielokat(px, pz, U["rynek"]) < r + 0.5:
        return "rynek"
    if mur and odl_lamana(px, pz, U["mur"], True) < 2.0 + r + 1.5:
        return "mur"
    if math.hypot(px - SPAWN[0], pz - SPAWN[1]) < 4.0 + r:
        return "spawn"
    return None


def wolne_miejsce(x, z, r, maks=12.0, ulice=True, korytarz=True, rynek=True):
    """Najbliższe wolne miejsce (spirala co 1,5) wokół (x, z) dla rekwizytu o promieniu r; None, gdy brak."""
    for k in range(0, int(maks / 1.5) + 1):
        rr = 1.5 * k
        n = max(1, int(2 * math.pi * rr / 1.5))
        for i in range(n):
            a = 2 * math.pi * i / n
            px, pz = x + rr * math.cos(a), z + rr * math.sin(a)
            if kolizja(px, pz, r, ulice=ulice, rynek=rynek) or (korytarz and w_korytarzu(px, pz)) or w_niecce(px, pz, r + 1.0):
                continue
            return px, pz
    return None


def w_korytarzu(px, pz, zapas=3.0):
    """Korytarze widoku (PROJEKT 4.8): trójkąt spawn–front podium karczmy i pasy 8 do punktów interakcji."""
    if odl_wielokat(px, pz, U["korytarz_karczmy"]) < zapas:
        return True
    for cel in ((18.4, 37.3), (42.5, 2.4), (95.9, 20.4)):
        if odl_odcinek(px, pz, SPAWN, cel) < 4.0:
            return True
    return False


# =========================================================================== prymitywy płaskie
def pas(s, nazwa, a, b, y_gora, grub, szer, kolor, mat="SmoothPlastic", przedluz=0.0, rot_dod=0.0):
    """Płaski pas (blok) od punktu a do b (x, z) z wierzchem na y_gora."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    dl = math.hypot(dx, dz)
    if dl < 0.05:
        return
    ry = math.degrees(math.atan2(dx, dz))
    s.blok(nazwa, ((a[0] + b[0]) / 2.0, y_gora - grub / 2.0, (a[1] + b[1]) / 2.0), (szer, grub, dl + 2 * przedluz), kolor, mat,
           (0, ry + rot_dod, 0))


def _prostokatny(s, nazwa, F, K, R, y_gora, grub, kolor, mat):
    vx, vz = K[0] - F[0], K[1] - F[1]
    d = math.hypot(vx, vz)
    ux, uz = R[0] - F[0], R[1] - F[1]
    h = math.hypot(ux, uz)
    if d < 0.05 or h < 0.05:
        return
    v, u = (vx / d, vz / d), (ux / h, uz / h)
    Y = (u[0], 0.0, u[1])
    Z = (-v[0], 0.0, -v[1])
    X = (0.0, u[0] * v[1] - u[1] * v[0], 0.0)
    m = ((X[0], Y[0], Z[0]), (X[1], Y[1], Z[1]), (X[2], Y[2], Z[2]))
    rx, ry, rz = katy_z_macierzy(m)
    cx = F[0] + u[0] * h / 2.0 + v[0] * d / 2.0
    cz = F[1] + u[1] * h / 2.0 + v[1] * d / 2.0
    s.klin(nazwa, (cx, y_gora - grub / 2.0, cz), (grub, h, d), kolor, mat, (rx, ry, rz))


def trojkat(s, nazwa, A, B, C, y_gora, grub, kolor, mat="SmoothPlastic"):
    """Płaski trójkąt (x, z) z dwóch klinów leżących na boku — dokładne wypełnienie wielokątów."""
    p = [A, B, C]
    i, j, k = max(((0, 1, 2), (1, 2, 0), (2, 0, 1)),
                  key=lambda e: (p[e[0]][0] - p[e[1]][0]) ** 2 + (p[e[0]][1] - p[e[1]][1]) ** 2)
    P, Q, R = p[i], p[j], p[k]
    ex, ez = Q[0] - P[0], Q[1] - P[1]
    l2 = ex * ex + ez * ez
    if l2 < 1e-6:
        return
    t = ((R[0] - P[0]) * ex + (R[1] - P[1]) * ez) / l2
    F = (P[0] + t * ex, P[1] + t * ez)
    _prostokatny(s, nazwa, F, P, R, y_gora, grub, kolor, mat)
    _prostokatny(s, nazwa, F, Q, R, y_gora, grub, kolor, mat)


def krawezniki(s, nazwa, a, b, wolny, y_gora=Y_KRAWEZNIK, szer=0.6, kolor="tusz", krok=0.5):
    """Krawężnik wzdłuż odcinka a–b, pocięty tam, gdzie wolny(px, pz) zwraca False (wjazdy ulic, budynki)."""
    dl = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(dl / krok))
    ok = []
    for i in range(n + 1):
        t = i / float(n)
        ok.append(wolny(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    i = 0
    while i <= n:
        if not ok[i]:
            i += 1
            continue
        j = i
        while j + 1 <= n and ok[j + 1]:
            j += 1
        t0, t1 = i / float(n), j / float(n)
        if (t1 - t0) * dl >= 0.8:
            pa = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            pb = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            pas(s, nazwa, pa, pb, y_gora, y_gora + 0.1, szer, kolor)
        i = j + 1


def odsun(a, b, d):
    """Odcinek a–b przesunięty w bok o d (dodatnie = w lewo patrząc od a do b, w płaszczyźnie XZ)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    dl = math.hypot(dx, dz)
    nx, nz = -dz / dl, dx / dl
    return (a[0] + nx * d, a[1] + nz * d), (b[0] + nx * d, b[1] + nz * d)


# =========================================================================== TEREN
DZIURA_LOK = [(-16.0, -10.0), (16.0, -10.0), (16.0, 18.0), (6.0, 18.0), (6.0, 34.0), (-6.0, 34.0), (-6.0, 18.0), (-16.0, 18.0)]


def w_niecce(px, pz, zapas=0.0):
    lx, lz = sw2lok(_L, px, pz)
    if -16 - zapas <= lx <= 16 + zapas and -10 - zapas <= lz <= 18 + zapas:
        return True
    return -6 - zapas <= lx <= 6 + zapas and 18 <= lz <= 34 + zapas


def teren(s, rnd):
    with s.grupa("Teren"):
        # --- płyta gruntu 440 × 440 z otworem na nieckę lochów (otwór osiowy H, wokół niego płyty w układzie bramy)
        dz = [lok2sw(_L, x, z) for x, z in DZIURA_LOK]
        hx0, hx1 = min(p[0] for p in dz) - 1.0, max(p[0] for p in dz) + 1.0
        hz0, hz1 = min(p[1] for p in dz) - 1.0, max(p[1] for p in dz) + 1.0
        for x, z in ((hx0, hz0), (hx0, hz1), (hx1, hz0), (hx1, hz1)):
            lx, lz = sw2lok(_L, x, z)
            assert -40 <= lx <= 40 and -36 <= lz <= 50, "płyty wokół niecki nie zakrywają otworu"
        R0 = 220.0

        def plyta(nazwa, x0, x1, z0, z1, kolor="trawa"):
            with s.cechy(cien=False):
                s.blok(nazwa, ((x0 + x1) / 2.0, Y_TRAWA - 1.0, (z0 + z1) / 2.0), (x1 - x0, 2.0, z1 - z0), kolor)

        plyta("Grunt", -R0, hx0, -R0, R0)
        plyta("Grunt", hx1, R0, -R0, R0)
        plyta("Grunt", hx0, hx1, -R0, hz0)
        plyta("Grunt", hx0, hx1, hz1, R0)
        with s.uklad(pos=(_L["x"], 0, _L["z"]), obrot=(0, _L["rot"], 0)):
            for x0, x1, z0, z1 in ((-40, -16, -36, 50), (16, 40, -36, 50), (-16, 16, -36, -10), (-16, -6, 18, 50), (6, 16, 18, 50),
                                   (-6, 6, 34, 50)):
                plyta("Grunt", x0, x1, z0, z1)
        # --- niecka lochów (dno −4, ściany oporowe z jasnym rantem, rampa 1 : 4, pęknięcia z Neonem)
        with s.grupa("Teren/Niecka"), s.uklad(pos=(_L["x"], 0, _L["z"]), obrot=(0, _L["rot"], 0)):
            s.blok("Dno niecki", (0, -4.6, 4.0), (32.0, 1.2, 28.0), "kamien_lochu", "Slate")
            for x0, x1, z0, z1 in ((-16, -15, -10, 18), (15, 16, -10, 18), (-15, 15, -10, -9), (-16, -6, 17, 18), (6, 16, 17, 18),
                                   (-6.9, -6, 18, 34), (6, 6.9, 18, 34)):
                s.blok("Ściana oporowa", ((x0 + x1) / 2.0, -2.25, (z0 + z1) / 2.0), (x1 - x0, 4.5, z1 - z0), "kamien_lochu", "Slate")
            with s.cechy(kolizja=False):
                for (x0, x1, z0, z1) in ((-16.6, -14.6, -10.6, 18.6), (14.6, 16.6, -10.6, 18.6), (-14.6, 14.6, -10.6, -8.6),
                                         (-16.6, -5.4, 17.0, 18.6), (5.4, 16.6, 17.0, 18.6), (-7.4, -5.6, 18.6, 34.0),
                                         (5.6, 7.4, 18.6, 34.0)):
                    s.blok("Rant niecki", ((x0 + x1) / 2.0, 0.3, (z0 + z1) / 2.0), (x1 - x0, 0.6, z1 - z0), "kamien_cieply")
            s.klin("Rampa", (0, -2.0, 26.0), (12.0, 4.0, 16.0), "bruk_ciemny")
            with s.cechy(kolizja=False, cien=False):
                for (x1, z1), (x2, z2), (x3, z3) in (((-4, 12), (-8.5, 9), (-11, 13)), ((5, 11), (9, 14.5), (12.5, 12)),
                                                     ((-1, 15.5), (1.5, 16.6), (-2, 17.4))):
                    s.belka("Pęknięcie", (x1, -3.9, z1), (x2, -3.9, z2), 0.3, "neon_portal", "Neon", 0.5)
                    s.belka("Pęknięcie", (x2, -3.9, z2), (x3, -3.9, z3), 0.3, "neon_portal", "Neon", 0.5)
            # skała za murem: bryły Slate 20–30 nad ziemią, dwie z czapą mchu
            with s.cechy(kolizja=False):
                for i, (x, z, w, h, d, ry, rz) in enumerate(((-24, -21, 14, 24, 12, 18, 8), (-12, -24, 12, 30, 12, -12, -6),
                                                             (2, -26, 16, 27, 12, 8, 5), (15, -23, 12, 22, 12, -20, -9),
                                                             (27, -20, 12, 20, 10, 25, 7), (-34, -17, 10, 18, 10, -8, -10))):
                    s.blok("Skała", (x, h / 2.0 - 3.0, z), (w, h, d), "kamien_lochu", "Slate", (rnd.uniform(-6, 6), ry, rz))
                    if i in (1, 3):
                        s.blok("Skała mech", (x, h - 2.6, z), (w * 0.8, 1.2, d * 0.8), "dach_lochy", rot=(0, ry, rz))
        # --- podium karczmy z pięcioma stopniami (wierzch bruk na +4)
        with s.grupa("Teren/Podium"), s.uklad(pos=(_K["x"], 0, _K["z"]), obrot=(0, _K["rot"], 0)):
            s.blok("Podium", (0, 1.8, 0), (46.0, 3.6, 38.0), "kamien_cokol", "Cobblestone")
            with s.cechy(kolizja=False):
                s.blok("Podium rant", (0, 3.55, 0), (46.8, 0.5, 38.8), "tusz")
            s.blok("Podium wierzch", (0, 3.85, 0), (46.3, 0.3, 38.3), "bruk")
            for i in range(5):
                top = Y_RYNEK + (4.0 - Y_RYNEK) * (5 - i) / 6.0
                z0, z1 = 19.0 + 2.0 * i, 21.0 + 2.0 * i
                s.blok("Stopień", (-3.0, top / 2.0, (z0 + z1) / 2.0 - 0.2), (28.0 - 0.3 * i, top, 2.0 + 0.4), "bruk" if i % 2 else "bruk_ciemny")
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Stopień rant", (-3.0, top + 0.02, z1 - 0.1), (28.0 - 0.3 * i + 0.1, 0.25, 0.45), "tusz")
            with s.cechy(kolizja=False):
                for x in (-17.4, 11.4):                        # policzki schodów
                    s.klin("Schody policzek", (x, 2.0, 24.2), (0.8, 4.0, 10.4), "kamien_cokol", rot=(0, 180, 0))
        # --- podwórka (ziemia) pod domami i strefami zieleni
        with s.grupa("Teren/Podworka"), s.cechy(cien=False):
            for d in U["domy"]:
                with s.uklad(pos=(d["x"], 0, d["z"]), obrot=(0, d["rot"], 0)):
                    s.blok("Podwórko", (0, Y_PODWORKO - 0.1, -0.5), (d["w"] + 5.0, 0.2, d["d"] + 4.0), "ziemia")
            for (x, z, w, d, r) in ((67.5, -39.0, 22, 16, -40), (89.2, 80.3, 20, 16, 45), (-62.4, -31.8, 14, 12, 20)):
                with s.uklad(pos=(x, 0, z), obrot=(0, r, 0)):
                    s.blok("Podwórko", (0, Y_PODWORKO - 0.1, 0), (w, 0.2, d), "ziemia")
        # --- pagórki w trawie (łagodne czasze, bez kolizji ze ścieżkami)
        with s.grupa("Teren/Pagorki"), s.cechy(kolizja=True):
            for x, z, a, h in ((104, -28, 9, 2.4), (-104, 52, 10, 2.8), (40, 110, 11, 2.6), (-50, -100, 9, 2.2), (-110, -24, 7, 2.0),
                               (112, 34, 6, 1.8)):
                R = (a * a + h * h) / (2.0 * h)
                s.kula("Pagórek", (x, h - R, z), 2 * R, cien(s, "trawa", 0.9))


# =========================================================================== RYNEK
def rynek(s, rnd):
    wiel = U["rynek"]
    with s.grupa("Rynek"):
        # --- nawierzchnia: wachlarz trójkątów z klinów (dokładny wielokąt), przedpola przed fasadami
        n = len(wiel)
        for i in range(n):
            with s.cechy(cien=False):
                trojkat(s, "Bruk", (0.0, 0.0), tuple(wiel[i]), tuple(wiel[(i + 1) % n]), Y_RYNEK, 0.55, "bruk")
        for bid, (x0, x1, z0, z1) in PRZEDPOLA.items():
            g = G[bid]
            with s.uklad(pos=(g["x"], 0, g["z"]), obrot=(0, g["rot"], 0)), s.cechy(cien=False):
                s.blok("Przedpole", ((x0 + x1) / 2.0, Y_RYNEK - 0.275, (z0 + z1) / 2.0), (x1 - x0, 0.55, z1 - z0), "bruk")
        # --- pierścień wokół studni (12 płyt) i promienie-ścieżki w kolorach kodów
        with s.cechy(kolizja=False, cien=False):
            for i in range(12):
                a = math.radians(i * 30 + 7)
                r = 12.4
                s.blok("Pierścień", (r * math.cos(a), Y_WZOR - 0.15, r * math.sin(a)), (2.6, 0.3, 2 * 13.7 * math.tan(math.radians(15)) + 0.1),
                       "bruk_ciemny", rot=(0, -math.degrees(a), 0))
            kreski = []
            for kod, trasa in SCIEZKI:
                L = 0.0
                segs = []
                for a, b in zip(trasa, trasa[1:]):
                    segs.append((a, b, L))
                    L += math.hypot(b[0] - a[0], b[1] - a[1])
                t = 0.0
                while t + 4.0 <= L:
                    p1, p2 = _punkt_na(segs, t), _punkt_na(segs, t + 4.0)
                    mid = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)
                    if odl_wielokat(mid[0], mid[1], wiel) < -1.2 or _w_przedpolu(mid[0], mid[1]):
                        pas(s, "Ścieżka-kod", p1, p2, Y_KOD, 0.3, 2.0, kod)
                        kreski.append((p1, p2))
                    t += 6.0
            # płyty w trzech tonach (4–8), z dala od studni, spawnu i ścieżek
            plyty = []
            proby = 0
            while len(plyty) < 34 and proby < 4000:
                proby += 1
                x, z = rnd.uniform(-42, 56), rnd.uniform(-38, 49)
                w, d = rnd.choice((4.0, 5.0, 6.0, 8.0)), rnd.choice((4.0, 5.0, 6.0))
                r = math.hypot(w, d) / 2.0
                if math.hypot(x, z) < 16 + r or math.hypot(x - SPAWN[0], z - SPAWN[1]) < 5 + r:
                    continue
                if odl_wielokat(x, z, wiel) > -(r + 1.0):
                    continue
                if any(odl_odcinek(x, z, a, b) < r + 1.4 for a, b in kreski):
                    continue
                if any(math.hypot(x - px, z - pz) < r + pr + 0.6 for px, pz, pr in plyty):
                    continue
                plyty.append((x, z, r))
                s.blok("Płyta bruku", (x, Y_WZOR - 0.15, z), (w, 0.3, d), rnd.choice(("bruk_ciemny", cien(s, "bruk", 0.9))),
                       rot=(0, rnd.uniform(-14, 14), 0))
        # --- krawężnik tuszem na granicy bruk / trawa
        def wolny(px, pz):
            for uid, u in ULICE.items():
                if odl_lamana(px, pz, pts_ulicy(uid)) < u["szer"] / 2.0 + 0.2:
                    return False
            if _w_przedpolu(px, pz, 0.2):
                return False
            for o in OBRYSY:
                if o.nazwa in ("schody_karczmy",) and o.zawiera(px, pz, 0.3):
                    return False
            return True
        with s.cechy(kolizja=False, cien=False):
            for i in range(n):
                krawezniki(s, "Krawężnik", tuple(wiel[i]), tuple(wiel[(i + 1) % n]), wolny)
            for bid, (x0, x1, z0, z1) in PRZEDPOLA.items():
                g = G[bid]
                rogi = [lok2sw(g, x0, z0), lok2sw(g, x1, z0), lok2sw(g, x1, z1), lok2sw(g, x0, z1)]
                for a, b in zip(rogi, rogi[1:] + rogi[:1]):
                    krawezniki(s, "Krawężnik", a, b, lambda px, pz, _b=bid: wolny(px, pz) and odl_wielokat(px, pz, wiel) > 0.3
                               and not _w_przedpolu(px, pz, 0.2, pomin=_b) and not G_OBRYS[_b].zawiera(px, pz, -0.6))
    # --- płyta wejścia
    with s.grupa("Spawn"):
        with s.uklad(pos=(SPAWN[0], 0, SPAWN[1]), obrot=(0, U["spawn_orientation_y_studio"], 0)):
            s.blok("SpawnLocation", (0, 0.3, 0), (6.0, 1.0, 6.0), "zloto")
            with s.cechy(kolizja=False, cien=False):
                s.blok("SpawnLocation obrys", (0, 0.2, 0), (6.8, 0.6, 6.8), "tusz")


# przedpola (bruk) przed fasadami stojącymi tuż za krawędzią rynku: lokalnie (x0, x1, z0, z1) w układzie budynku
PRZEDPOLA = {"wylegarnia": (-14.0, 9.0, 12.0, 21.0), "sklep_magiczny": (-10.0, 9.0, 11.0, 17.0),
             "stajnia": (-15.0, 4.0, 10.0, 16.0), "zbrojownia": (-9.0, 15.0, 12.0, 17.5)}
G_OBRYS = {o.nazwa: o for o in OBRYSY}


def _w_przedpolu(px, pz, zapas=0.0, pomin=None):
    for bid, (x0, x1, z0, z1) in PRZEDPOLA.items():
        if bid == pomin:
            continue
        lx, lz = sw2lok(G[bid], px, pz)
        if x0 - zapas <= lx <= x1 + zapas and z0 - zapas <= lz <= z1 + zapas:
            return True
    return False


def _punkt_na(segs, t):
    for a, b, L0 in segs:
        dl = math.hypot(b[0] - a[0], b[1] - a[1])
        if t <= L0 + dl + 1e-9:
            u = (t - L0) / dl if dl else 0.0
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    a, b, _ = segs[-1]
    return b


def _od_studni(cel, r=14.5):
    d = math.hypot(cel[0], cel[1])
    return (cel[0] / d * r, cel[1] / d * r)


_SCH = lok2sw(_K, -3.0, 29.5)
SCIEZKI = [
    ("dach_lochy", [_od_studni((37.1, 15.0)), (37.1, 15.0)]),
    ("dach_arena", [_od_studni((7.3, -37.3)), (8.6, -37.0)]),
    ("dach_gildia", [_od_studni((-37.6, -5.3)), (-38.5, -5.3)]),
    ("dach_brama", [_od_studni((-25.4, -28.2)), (-26.0, -29.0)]),
    ("dach_twierdza", [(2.0, 14.4), (3.0, 31.0), (-6.0, 38.6), (-13.7, 39.0)]),
    ("dach_karczma", [_od_studni((26.0, 30.0)), (26.0, 31.0), _SCH]),
]


# =========================================================================== ULICE
def ulice(s, rnd):
    with s.grupa("Ulice"):
        for uid, u in ULICE.items():
            pts = pts_ulicy(uid)
            w = u["szer"]
            y = Y_PODMURNA if uid == "podmurna" else Y_SZPRYCHA
            kol = NAWIERZCHNIA.get(uid, "bruk_ciemny")
            with s.cechy(cien=False):
                for a, b in zip(pts, pts[1:]):
                    pas(s, "Ulica", tuple(a), tuple(b), y, 0.5, w, kol)
                for p in pts[1:-1]:
                    s.walec("Ulica zakręt", (p[0], y - 0.25, p[1]), w / 2.0, 0.5, kol, os="y")

            def wolny(px, pz, _uid=uid, _pts=pts, _w=w):
                if odl_wielokat(px, pz, U["rynek"]) < 0.3 or _w_przedpolu(px, pz, 0.2):
                    return False
                if w_niecce(px, pz, 0.5):
                    return False
                if odl_lamana(px, pz, _pts) < _w / 2.0 - 0.15:
                    return False
                for vid, v in ULICE.items():
                    if vid != _uid and odl_lamana(px, pz, pts_ulicy(vid)) < v["szer"] / 2.0 + 0.2:
                        return False
                for o in OBRYSY:
                    if o.nazwa in G and o.zawiera(px, pz, -0.5):
                        return False
                if odl_lamana(px, pz, U["mur"], True) < 2.3:
                    return False
                return True
            with s.cechy(kolizja=False, cien=False):
                for a, b in zip(pts, pts[1:]):
                    for strona in (1, -1):
                        pa, pb = odsun(tuple(a), tuple(b), strona * (w / 2.0 + 0.3))
                        krawezniki(s, "Krawężnik", pa, pb, wolny, Y_KRAWEZNIK - (Y_RYNEK - y) * 0)
                # kamienie milowe co 8 studów w kolorze kodu celu (tylko szprychy)
                if uid in KOD:
                    segs, L = [], 0.0
                    for a, b in zip(pts, pts[1:]):
                        segs.append((tuple(a), tuple(b), L))
                        L += math.hypot(b[0] - a[0], b[1] - a[1])
                    t = 6.0
                    while t < L - 2.0:
                        x, z = _punkt_na(segs, t)
                        if odl_wielokat(x, z, U["rynek"]) > 1.0:
                            s.blok("Kamień milowy", (x, y + 0.04, z), (1.3, 0.3, 1.3), KOD[uid], rot=(0, 45 + rnd.uniform(-8, 8), 0))
                        t += 8.0


# =========================================================================== MUR i BASZTY
WBUDOWANE = {"brama_miejska": (23.4, -14.0, 8.0), "arena": (24.3, -24.0, 16.0)}   # cięcie muru: |x| ≤ a, z0 ≤ z ≤ z1 (lokalnie)


def _ciecie_muru(px, pz):
    for bid, (a, z0, z1) in WBUDOWANE.items():
        lx, lz = sw2lok(G[bid], px, pz)
        if abs(lx) <= a and z0 <= lz <= z1:
            return True
    return False


def mur(s, rnd):
    pts = U["mur"]
    n = len(pts)
    k_c = cien(s, "kamien_cieply")
    with s.grupa("Mur"):
        for i in range(n):
            A, B = pts[i], pts[(i + 1) % n]
            dx, dz = B[0] - A[0], B[1] - A[1]
            dl = math.hypot(dx, dz)
            ex, ez = dx / dl, dz / dl
            nx, nz = -ez, ex
            mx, mz = (A[0] + B[0]) / 2.0, (A[1] + B[1]) / 2.0
            if nx * -mx + nz * -mz < 0:                      # normalna ku środkowi miasta
                nx, nz = -nx, -nz
            N = max(2, int(dl / 0.5))
            ok = [not _ciecie_muru(A[0] + dx * j / N, A[1] + dz * j / N) for j in range(N + 1)]
            j = 0
            while j <= N:
                if not ok[j]:
                    j += 1
                    continue
                k = j
                while k + 1 <= N and ok[k + 1]:
                    k += 1
                t0, t1 = j / float(N), k / float(N)
                e0 = 1.2 if j == 0 else 0.0                  # zakładka na załamaniu muru
                e1 = 1.2 if k == N else 0.0
                p0 = (A[0] + dx * t0 - ex * e0, A[1] + dz * t0 - ez * e0)
                p1 = (A[0] + dx * t1 + ex * e1, A[1] + dz * t1 + ez * e1)
                _odcinek_muru(s, p0, p1, (nx, nz), k_c, ciete=(j != 0, k != N))
                j = k + 1
        # niewidzialna blokada w przejściu bramy miejskiej (dopóki nie ma wyjścia do krain)
        with s.grupa("Mur/_Blokada"), s.cechy(cien=False):
            g = G["brama_miejska"]
            with s.uklad(pos=(g["x"], 0, g["z"]), obrot=(0, g["rot"], 0)):
                s.blok("Blokada przejścia", (0, 8.0, -8.6), (17.0, 16.0, 1.0), "tusz", alfa=1.0)
        with s.grupa("Mur/Baszty"):
            for i, (x, z) in enumerate(U["baszty"]):
                baszta(s, rnd, x, z, 1 if i % 2 else -1, "rycerz" if i % 2 else "kot")


def _odcinek_muru(s, p0, p1, nrm, k_c, ciete):
    dx, dz = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dz)
    if L < 1.0:
        return
    ry = math.degrees(math.atan2(nrm[0], nrm[1]))             # lokalne +Z = do miasta, X wzdłuż muru
    mx, mz = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
    pod_ziemia = any(w_niecce(p0[0] + dx * t, p0[1] + dz * t, 3.0) for t in (0.0, 0.25, 0.5, 0.75, 1.0))
    ydol = -4.6 if pod_ziemia else 0.0
    with s.uklad(pos=(mx, 0, mz), obrot=(0, ry, 0)):
        if not pod_ziemia:                                    # podwale: pas ziemi u stopy muru (mniej trawy w mieście)
            with s.cechy(kolizja=True, cien=False):
                s.blok("Podwale", (0, Y_PODWORKO - 0.1, 5.5), (L, 0.2, 7.0), "ziemia")
        s.blok("Mur korpus", (0, (ydol + 13.6) / 2.0, 0), (L, 13.6 - ydol, 4.0), "kamien_cieply")
        with s.cechy(kolizja=False):
            s.blok("Mur rant", (0, 13.9, 0), (L + 0.1, 0.6, 4.6), "tusz")
            # skarpa u stopy od strony miasta (bez niej przy niecce i przy budynkach wbudowanych)
            n = max(1, int(L / 6.0))
            for i in range(n):
                xa, xb = -L / 2.0 + L * i / n, -L / 2.0 + L * (i + 1) / n
                xs = (xa + xb) / 2.0
                wx = mx + xs * math.cos(math.radians(ry)) + 3.0 * math.sin(math.radians(ry))
                wz = mz - xs * math.sin(math.radians(ry)) + 3.0 * math.cos(math.radians(ry))
                if pod_ziemia or any(o.zawiera(wx, wz, 0.5) for o in OBRYSY if o.nazwa in G):
                    continue
                s.klin("Mur skarpa", (xs, 1.5, 2.6), (xb - xa + 0.05, 3.0, 1.2), "kamien_cokol", rot=(0, 180, 0))
            # blanki co 4 (2 × 2, co drugi wyższy o 0,3 i w cieniu)
            m = int((L - 2.6) / 4.0)
            if m >= 1:
                x0 = -(m - 1) * 4.0 / 2.0
                for i in range(m):
                    h = 2.0 + (0.3 if i % 2 else 0.0)
                    with s.cechy(cien=False):
                        s.blok("Mur blank", (x0 + 4.0 * i, 14.2 + h / 2.0, 0), (2.0, h, 3.8), "kamien_cieply" if i % 2 == 0 else k_c)


def baszta(s, rnd, x, z, znak, kto):
    with s.uklad(pos=(x, 0, z), obrot=(0, rnd.uniform(0, 360), 0)):
        s.walec("Baszta cokół", (0, 0.75, 0), 6.4, 1.5, "kamien_cokol", "Cobblestone", os="y")
        s.walec("Baszta", (0, 6.0, 0), 6.0, 12.0, "kamien_cieply", os="y")
        with s.cechy(kolizja=False):
            s.walec("Baszta gzyms", (0, 12.2, 0), 6.5, 0.6, "tusz", os="y")
            with s.uklad(pos=(0, 12.4, 0), obrot=(0, 0, 4.0 * znak)):
                s.walec("Baszta", (0, 3.9, 0), 5.4, 7.8, cien(s, "kamien_cieply", 0.93), os="y")
                s.walec("Baszta gzyms", (0, 7.9, 0), 5.9, 0.6, "tusz", os="y")
                with s.uklad(pos=(0, 8.1, 0), obrot=(0, 0, -6.0 * znak)):
                    s.walec("Baszta", (0, 2.4, 0), 5.0, 4.8, "kamien_cieply", os="y")
                    s.walec("Baszta gzyms", (0, 4.9, 0), 5.5, 0.6, "tusz", os="y")
                    for i in range(6):
                        a = math.radians(i * 60)
                        h = 1.8 + (0.35 if i % 2 else 0.0)
                        s.blok("Baszta blank", (4.3 * math.cos(a), 5.2 + h / 2.0, 4.3 * math.sin(a)), (1.4, h, 2.2),
                               "kamien_cieply" if i % 2 == 0 else cien(s, "kamien_cieply"), rot=(0, -math.degrees(a), 0))
                    zestaw.choragiewka_duetu(s, (0, 5.2, 0), kto, ry=rnd.uniform(0, 360), przechyl=12 * znak)


# =========================================================================== BUDYNKI GŁÓWNE
def budynki(s, ziarno):
    for i, mid in enumerate(MODULY):
        mod = importlib.import_module("swiat.krzywe_miasteczko.budynki." + mid)
        g = G[mid]
        with s.uklad(pos=(g["x"], g["y0"], g["z"]), obrot=(0, g["rot"], 0), grupa=mod.NAZWA):
            mod.buduj(s, random.Random(ziarno * 1000 + i))


# =========================================================================== DOMY TŁA i STRAGANY
WARIANTY_DOMOW = ["a", "b", "c", "b", "a", "c", "b", "a", "b"]
OKIENNICE = ["dach_twierdza", "pomarancz", "dach_wylegarnia", "dach_kolo", "zloto", "dach_karczma", "dach_gildia", "pomarancz",
             "dach_twierdza"]


def domy(s, rnd):
    for i, d in enumerate(U["domy"]):
        with s.uklad(pos=(d["x"], 0, d["z"]), obrot=(0, d["rot"], 0), grupa="DomyTla/Dom%d" % (i + 1)):
            zestaw.dom_mieszkalny(s, random.Random(rnd.randint(0, 10 ** 6)), WARIANTY_DOMOW[i], d["dach"], d["sciana"],
                                  d["w"], d["d"], d["h"], pochyl=1 if i % 2 == 0 else -1, neon_okna=1 + (i % 3 == 0),
                                  okiennica=OKIENNICE[i], znak="klocek" if i % 2 else "lata")


TOWARY = {"stragan_1": (("dach_karczma", "biel"), "jablka"), "stragan_2": (("dach_stajnia", "biel"), "chleby"),
          "stragan_3": (("dach_sklep", "biel"), "krysztaly"), "stragan_4": (("dach_twierdza", "biel"), "tkaniny"),
          "stragan_5": (("dach_kolo", "biel"), "klocki")}


def stragany(s, rnd):
    with s.grupa("Stragany"):
        for st in U["stragany"]:
            if st["id"] in TOWARY:
                kolory, towar = TOWARY[st["id"]]
                zestaw.stragan(s, (st["x"], Y_RYNEK, st["z"]), st["rot"], kolory, towar)


# =========================================================================== STAW
def staw(s, rnd):
    sx, sz = U["staw"]["srodek"]
    with s.grupa("Staw"), s.uklad(pos=(sx, 0, sz)), s.cechy(kolizja=False):
        kola = ((-2.2, 0.6, 6.0), (2.6, -0.8, 5.2))
        with s.cechy(cien=False):
            for x, z, r in kola:
                s.walec("Staw brzeg", (x, 0.06, z), r + 1.3, 0.24, "kamien_cieply", os="y")
            for x, z, r in kola:
                s.walec("Staw toń", (x, 0.14, z), r + 0.5, 0.24, "woda_gleboka", os="y")
            for x, z, r in kola:
                s.walec("Staw tafla", (x, 0.22, z), r, 0.24, "woda", os="y")
            s.walec("Staw głębia", (-1.2, 0.3, 0.2), 2.8, 0.24, "woda_gleboka", os="y")
            for x, z, k in ((-4.5, 2.0, 20), (1.5, -3.6, -15), (4.8, 1.2, 35)):
                s.blok("Staw blik", (x, 0.43, z), (0.4, 0.2, 2.6), "biel", rot=(0, k, 0))
        for i in range(8):
            a = math.radians(i * 45 + rnd.uniform(-12, 12))
            r = 7.6 if math.cos(a) < 0.2 else 7.0
            zestaw.kamien(s, (r * math.cos(a) + (0.6 if math.cos(a) > 0 else -0.6), 0, r * math.sin(a) * 0.95), rnd,
                          rnd.uniform(1.6, 2.4), dwa=False, kolizja=False)
        # pomost 2 × 6 od południowego brzegu
        with s.uklad(pos=(1.5, 0, -6.8), obrot=(0, 192, 0)):
            s.blok("Pomost", (0, 0.75, -2.2), (2.4, 0.4, 6.4), "drewno_jasne", "WoodPlanks")
            for x, z in ((-1.0, -4.8), (1.0, -4.8)):
                s.blok("Pomost pal", (x, 0.6, z), (0.5, 1.4, 0.5), "drewno", "Wood")
        # trzy kaczki z klocków
        for x, z, ry, k in ((-4.0, -1.0, 30, 1.0), (0.4, 1.8, -60, 0.85), (3.2, -1.8, 150, 0.7)):
            with s.uklad(pos=(x, 0.32, z), obrot=(0, ry, 0), skala=k), s.cechy(cien=False):
                s.blok("Kaczka", (0, 0.5, 0), (1.4, 1.0, 2.2), "zloto")
                s.blok("Kaczka głowa", (0, 1.4, 0.75), (1.0, 1.0, 1.0), "zloto", rot=(0, 0, 0))
                s.blok("Kaczka dziób", (0, 1.3, 1.45), (0.6, 0.35, 0.6), "pomarancz")


# =========================================================================== ZIELEŃ
def drzewa_strefy(s, rnd, srodek, n, promien, skala=(0.85, 1.0), owoce=False, ulice=True):
    postawione = 0
    proby = 0
    while postawione < n and proby < 300:
        proby += 1
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, promien)
        x, z = srodek[0] + r * math.cos(a), srodek[1] + r * math.sin(a)
        if kolizja(x, z, 3.0, ulice=ulice) or w_korytarzu(x, z) or odl_wielokat(x, z, U["rynek"]) < 3.0:
            continue
        if any(math.hypot(x - px, z - pz) < 7.0 for px, pz in DRZEWA):
            continue
        DRZEWA.append((x, z))
        zestaw.drzewo_lisciaste(s, (x, 0, z), rnd, rnd.uniform(*skala), owoce=owoce)
        postawione += 1
    if postawione < n:
        print("UWAGA: strefa %s — postawiono %d z %d drzew" % (srodek, postawione, n))


DRZEWA = []


def krzaki(s, rnd, srodek, n, promien):
    proby = 0
    k = 0
    while k < n and proby < 300:
        proby += 1
        a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, promien)
        x, z = srodek[0] + r * math.cos(a), srodek[1] + r * math.sin(a)
        if kolizja(x, z, 1.6) or odl_wielokat(x, z, U["rynek"]) < 1.5:
            continue
        zestaw.krzak(s, (x, 0, z), rnd, rnd.uniform(0.9, 1.25))
        k += 1


def zielen(s, rnd):
    with s.grupa("Zielen"):
        drzewa_strefy(s, rnd, (67.5, -39.0), 2, 9)                      # Z1 podwórko kuźni
        drzewa_strefy(s, rnd, (-18.6, -69.5), 3, 9, owoce=True)          # Z2 sad
        drzewa_strefy(s, rnd, (-62.4, -31.8), 2, 7)                      # Z3 łąka przy bramie
        drzewa_strefy(s, rnd, (-64.0, 52.0), 2, 12)                      # Z4 przy padoku
        drzewa_strefy(s, rnd, (31.5, 77.9), 2, 8)                        # Z5 ogród przy stawie
        drzewa_strefy(s, rnd, (92.0, 82.0), 2, 14)                       # Z6 zaplecze karczmy
        drzewa_strefy(s, rnd, (-100.0, 42.0), 1, 8)
        for c, n, r in (((67.5, -39.0), 4, 10), ((-18.6, -69.5), 3, 10), ((-62.4, -31.8), 3, 8), ((31.5, 77.9), 3, 8),
                        ((89.2, 80.3), 2, 8), ((-9.1, 74.4), 3, 11), ((95.0, -20.0), 2, 8), ((-88.0, 40.0), 2, 8),
                        ((40.0, -80.0), 2, 8)):
            krzaki(s, rnd, c, n, r)
        # ogród przy stawie: grządki z dyniami i sałatą
        with s.grupa("Zielen/Ogrod"), s.uklad(pos=(31.5, 0, 77.9), obrot=(0, 20, 0)):
            for i, (z, owoc) in enumerate(((-3.0, "pomarancz"), (1.0, "lisc_jasny"), (5.0, "pomarancz"))):
                s.blok("Grządka", (0, 0.25, z), (10.0, 0.5, 2.4), "ziemia")
                with s.cechy(kolizja=False):
                    for j, x in enumerate((-3.4, 0.0, 3.4)):
                        rozm = 1.6 if owoc == "pomarancz" else 1.2
                        s.blok("Dynia" if owoc == "pomarancz" else "Sałata", (x + 0.3 * (i % 2), 0.5 + rozm / 2.0, z), (rozm * 1.2, rozm, rozm * 1.2),
                               owoc, rot=(0, 20 * j + 10 * i, 0))
        # kwiaty przy wejściach (≤ 2 na budynek)
        for bid, kand, ry in (("wylegarnia", ((6.0, 16.5),), 4), ("sklep_magiczny", ((-9.0, 13.5), (5.5, 14.5)), -6),
                              ("zbrojownia", ((-8.0, 15.5),), 5), ("stajnia", ((8.0, 13.5),), -4)):
            g = G[bid]
            for x, z in kand:
                px, pz = lok2sw(g, x, z)
                if not kolizja(px, pz, 1.5, pomin=(bid,), ulice=False):
                    break
            else:
                print("UWAGA: kwiaty przy %s kolidują z %s" % (bid, kolizja(px, pz, 1.5, pomin=(bid,), ulice=False)))
                continue
            with s.uklad(pos=(g["x"], 0, g["z"]), obrot=(0, g["rot"], 0)):
                y_k = Y_RYNEK - 0.05 if (_w_przedpolu(px, pz) or odl_wielokat(px, pz, U["rynek"]) < 0) else 0.0
                zestaw.kwiaty(s, (x, y_k, z), ry, (("czerwien", "zloto"), ("biel", "dach_sklep"), ("zloto", "biel"),
                                                            ("czerwien", "biel"))[len(s.czesci) % 4])


# =========================================================================== TŁO i CHMURY
def tlo(s, rnd):
    with s.grupa("Tlo"), s.cechy(kolizja=False, cien=False):
        kolory = ["lisc_ciemny", "igla", "trawa", "lisc_ciemny", "igla", "lisc", "lisc_ciemny", "trawa"]
        for i in range(16):
            a = math.radians(i * 22.5 + rnd.uniform(-5, 5))
            R = rnd.uniform(48, 60)
            h = rnd.uniform(26, 44)
            r = max(rnd.uniform(168, 198), 140.0 + math.sqrt(R * R - (R - h) ** 2))   # podnóże za murem i pasem drzew
            x, z = r * math.cos(a), r * math.sin(a)
            s.kula("Wzgórze", (x, h - R, z), 2 * R, kolory[i % len(kolory)])
            if i % 4 == 1:
                Rc = R * 0.55
                s.kula("Wzgórze czapa", (x, h + 1.4 - Rc, z), 2 * Rc, "lisc_jasny")
        n_ig = 0
        proby = 0
        while n_ig < 36 and proby < 2000:
            proby += 1
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(134, 166)
            x, z = r * math.cos(a), r * math.sin(a)
            if w_niecce(x, z, 14.0) or odl_lamana(x, z, U["mur"], True) < 8.0:
                continue
            if any(math.hypot(x - px, z - pz) < 9.0 for px, pz in DRZEWA):
                continue
            DRZEWA.append((x, z))
            zestaw.drzewo_iglaste(s, (x, 0, z), rnd, rnd.uniform(1.15, 1.6))
            n_ig += 1
        n_d = 0
        while n_d < 12 and proby < 4000:
            proby += 1
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(132, 160)
            x, z = r * math.cos(a), r * math.sin(a)
            if w_niecce(x, z, 14.0) or odl_lamana(x, z, U["mur"], True) < 8.0:
                continue
            if any(math.hypot(x - px, z - pz) < 10.0 for px, pz in DRZEWA):
                continue
            DRZEWA.append((x, z))
            zestaw.drzewo_lisciaste(s, (x, 0, z), rnd, rnd.uniform(1.2, 1.5))
            n_d += 1
    with s.grupa("Chmury"):
        for i in range(10):
            a = math.radians(i * 36 + rnd.uniform(-10, 10))
            r = rnd.uniform(125, 215)
            zestaw.chmura(s, (r * math.cos(a), rnd.uniform(110, 150), r * math.sin(a)), rnd, rnd.uniform(1.0, 1.6))


# =========================================================================== REKWIZYTY
def siano(s, pos, ry=0.0, przechyl=6.0, dl=3.2):
    with s.uklad(pos=(pos[0], pos[1], pos[2]), obrot=(0, ry, przechyl)):
        s.blok("Siano", (0, 1.15, 0), (dl, 2.4, 2.4), "dach_stajnia")
        with s.cechy(kolizja=False, cien=False):
            for x in (-dl * 0.25, dl * 0.25):
                s.blok("Siano sznurek", (x, 1.15, 0), (0.3, 2.5, 2.5), "drewno")


def trojka(s, rnd, x, z, ry, typ="mieszana"):
    """Trójka duży–średni–mały (PROJEKT 4.9): skrzynia, beczka, siano. pos = środek grupy."""
    with s.uklad(pos=(x, 0, z), obrot=(0, ry, 0)):
        if typ == "siano":
            siano(s, (0, 0, 0), 5, 6, 3.6)
            siano(s, (3.2, 0, 1.6), -20, -8, 3.0)
            siano(s, (0.6, 2.35, 0.2), 30, 0, 2.6)
        elif typ == "beczki":
            zestaw.beczka(s, (0, 0, 0), "woda", przechyl=(0, 6))
            zestaw.beczka(s, (3.6, 0, 1.0), "jablka", r=1.5, h=3.6, przechyl=(5, 0))
            zestaw.skrzynia(s, (-1.0, 0, 3.4), ry=15, dl=2.6, a=2.2, przechyl=9)
        else:
            zestaw.skrzynia(s, (0, 0, 0), ry=8, przechyl=7)
            zestaw.beczka(s, (3.8, 0, 0.6), "jablka" if rnd.random() < 0.5 else "woda", r=1.5, h=3.6, przechyl=(0, -6))
            zestaw.skrzynia(s, (1.2, 0, 3.4), ry=-20, dl=2.4, a=2.0, przechyl=11)


def latarnia(s, pos, wys=9.0, ry=0.0, lustro=False, plama_r=3.0):
    """zestaw.latarnia bez jej plamy 0,1 (za cienka — zasada ≥ 0,2) + własna plama Ø 2·plama_r grubości 0,2 pod światłem,
    wierzch 0,25 nad podstawą (ponad szprychami 0,17, pod krawężnikiem 0,45)."""
    zestaw.latarnia(s, pos, wys, ry, plama=False, lustro=lustro)
    zn = -1.0 if lustro else 1.0
    xe, kat = 0.0, 0.0
    for dl, k in ((wys * 0.55, 5 * zn), (wys * 0.3, -9 * zn), (wys * 0.26, -38 * zn)):
        kat += k
        xe -= math.sin(math.radians(kat)) * dl
    with s.uklad(pos=pos, obrot=(0, ry, 0)), s.cechy(kolizja=False, cien=False):
        s.walec("Latarnia plama", (xe, 0.15, 0), plama_r, 0.2, "tynk_krem", os="y")


def rekwizyty(s, rnd):
    with s.grupa("Rekwizyty"):
        # --- latarnie: wzdłuż szprych co 16 (naprzemiennie), na brzegu rynku i przy schodach karczmy
        latarnie = []
        for uid in ("bramna", "lochowa", "twierdzowa", "gildyjna", "arenowa"):
            pts = pts_ulicy(uid)
            w = ULICE[uid]["szer"]
            segs, L = [], 0.0
            for a, b in zip(pts, pts[1:]):
                segs.append((tuple(a), tuple(b), L))
                L += math.hypot(b[0] - a[0], b[1] - a[1])
            t, strona = 10.0, 1
            while t < L - 12.0:
                p = _punkt_na(segs, t)
                q = _punkt_na(segs, min(L, t + 0.5))
                dx, dz = q[0] - p[0], q[1] - p[1]
                dl = math.hypot(dx, dz) or 1.0
                nx, nz = -dz / dl * strona, dx / dl * strona
                x, z = p[0] + nx * (w / 2.0 + 1.3), p[1] + nz * (w / 2.0 + 1.3)
                przeszk = kolizja(x, z, 1.0, ulice=False)
                if not przeszk and odl_wielokat(x, z, U["rynek"]) > 1.0:
                    ry = math.degrees(math.atan2(nz, -nx))         # wysięgnik (+X) nad ulicę
                    latarnia(s, (x, 0, z), 9.0, ry, plama_r=3.0)
                    latarnie.append((x, z))
                t += 16.0
                strona = -strona
        for x, z in ((-36.0, 16.0), (-37.0, -8.5), (-18.0, -33.0), (36.0, -20.0), (38.0, -9.0), (8.0, 36.0)):
            if kolizja(x, z, 1.0, ulice=False, mur=False) or w_korytarzu(x, z):
                print("UWAGA: latarnia rynku w (%.1f, %.1f) koliduje z %s" % (x, z, kolizja(x, z, 1.0, ulice=False, mur=False)))
            latarnia(s, (x, Y_RYNEK, z), 9.0, math.degrees(math.atan2(z, -x)), plama_r=3.0)   # wysięgnik ku studni
            latarnie.append((x, z))
        with s.uklad(pos=(_K["x"], 0, _K["z"]), obrot=(0, _K["rot"], 0)):
            latarnia(s, (-18.8, 0, 27.0), 9.0, 0.0, lustro=True, plama_r=3.0)
            latarnia(s, (12.8, 0, 27.0), 9.0, 0.0, plama_r=3.0)
        # --- chorągwie w kolorach kodów u wylotów szprych
        for uid in ("bramna", "lochowa", "twierdzowa", "gildyjna", "arenowa"):
            pts = pts_ulicy(uid)
            w = ULICE[uid]["szer"]
            segs, L = [], 0.0
            for a, b in zip(pts, pts[1:]):
                segs.append((tuple(a), tuple(b), L))
                L += math.hypot(b[0] - a[0], b[1] - a[1])
            postawione = 0
            ostatnie = {1: None, -1: None}
            for proba, strona in enumerate((1, -1, 1, -1)):
                if postawione >= 2 or (proba >= 2 and ostatnie[strona] is None):
                    continue                                   # druga chorągiew po tej samej stronie, gdy drugiej strony brak
                t = 5.0 if ostatnie[strona] is None else ostatnie[strona] + 14.0
                while t < L - 3.0:
                    p, q = _punkt_na(segs, t), _punkt_na(segs, t + 0.5)
                    dl = math.hypot(q[0] - p[0], q[1] - p[1]) or 1.0
                    ex, ez = (q[0] - p[0]) / dl, (q[1] - p[1]) / dl
                    x = p[0] - ez * strona * (w / 2.0 + 1.6)
                    z = p[1] + ex * strona * (w / 2.0 + 1.6)
                    if not (kolizja(x, z, 1.0, ulice=False) or w_korytarzu(x, z, 7.0) or odl_wielokat(x, z, U["rynek"]) < 1.0
                            or any(math.hypot(x - lx, z - lz) < 3.0 for lx, lz in latarnie)):
                        zestaw.choragiew(s, (x, 0, z), KOD[uid], wys=12.0 + (1.0 if strona > 0 else 0.0),
                                         ry=math.degrees(math.atan2(ex, ez)) + 90 + rnd.uniform(-20, 20))
                        postawione += 1
                        ostatnie[strona] = t
                        break
                    t += 3.0
            if postawione < 2:
                print("UWAGA: przy ulicy %s stoi %d chorągwi" % (uid, postawione))
        # --- trójki beczek, skrzyń i siana
        for (x, z, ry, typ) in ((72.0, -44.0, -30, "mieszana"), (62.0, -33.0, 40, "beczki"), (101.0, 84.0, 30, "beczki"),
                                (93.0, 86.0, -50, "mieszana"), (-57.5, 52.5, 40, "siano"), (-66.0, -36.0, 10, "siano"),
                                (-62.0, -76.0, 30, "beczki"), (-30.0, -36.0, 60, "mieszana"), (36.0, 56.0, -20, "beczki"),
                                (-80.0, 22.0, 80, "mieszana")):
            p = wolne_miejsce(x, z, 3.6)
            if p is None:
                print("UWAGA: brak miejsca na trójkę przy (%.1f, %.1f)" % (x, z))
                continue
            trojka(s, rnd, p[0] - 1.5, p[1] - 1.5, ry, typ)
        # --- ławki przy studni i przy stawie
        for a in (115, 160, 205, 250, 295):
            r = 17.0
            x, z = r * math.cos(math.radians(a)), r * math.sin(math.radians(a))
            ry = math.degrees(math.atan2(-x, -z))
            konf = kolizja(x, z, 2.0, ulice=False, mur=False)
            if konf:
                print("UWAGA: ławka przy studni koliduje z %s" % konf)
                continue
            zestaw.lawka(s, (x, Y_RYNEK, z), ry)
        sx, sz = U["staw"]["srodek"]
        for x, z in ((sx - 11.5, sz - 3.0), (sx + 10.5, sz + 4.5)):
            zestaw.lawka(s, (x, 0, z), math.degrees(math.atan2(sx - x, sz - z)))
        zestaw.lawka(s, (-14.0, 0, -64.0), 200)
        # --- płot padoku i łąki
        with s.uklad(pos=(G["stajnia"]["x"], 0, G["stajnia"]["z"]), obrot=(0, G["stajnia"]["rot"], 0)):
            zestaw.plot(s, [(-10.0, -12.5), (-10.0, -21.0), (8.0, -21.0), (8.0, -12.5)], rnd)
            with s.uklad(pos=(-1.0, 0, -16.5)):
                s.blok("Padok", (0, Y_PODWORKO - 0.1, 0), (18.0, 0.2, 8.5), "ziemia")
                with s.cechy(kolizja=False):
                    s.blok("Koryto", (3.0, 0.9, -1.0), (5.0, 1.6, 1.8), "drewno", "WoodPlanks", rot=(0, 8, 0))
                    with s.cechy(cien=False):
                        s.blok("Koryto woda", (3.0, 1.62, -1.0), (4.2, 0.2, 1.1), "woda", rot=(0, 8, 0))
        zestaw.plot(s, [(-56.0, -37.0), (-62.0, -40.5), (-68.5, -40.0)], rnd)
        # --- kamienie i wypadnięte klocki
        miejsca = [(100, -40), (-98, -55), (-108, 8), (60, 104), (-14, 110), (106, 60), (76, -84), (-40, 102), (8, -100),
                   (-86, 70), (116, 0), (35, 112)]
        for x, z in miejsca:
            if kolizja(x, z, 2.5, mur=False):
                continue
            zestaw.kamien(s, (x, 0, z), rnd, rnd.uniform(2.2, 3.6))
        kolory = ["dach_karczma", "dach_twierdza", "dach_wylegarnia", "dach_kolo", "dach_sklep", "zloto", "dach_lochy", "dach_arena",
                  "pomarancz", "dach_gildia"]
        k = 0
        proby = 0
        while k < 10 and proby < 400:
            proby += 1
            a, r = rnd.uniform(0, 2 * math.pi), rnd.uniform(70, 110)
            x, z = r * math.cos(a), r * math.sin(a)
            if kolizja(x, z, 1.5) or odl_lamana(x, z, U["mur"], True) < 4.0 or w_niecce(x, z, 3.0):
                continue
            with s.uklad(pos=(x, 0, z), obrot=(0, rnd.uniform(0, 90), rnd.choice((-8, 8)))), s.cechy(kolizja=False):
                s.blok("Klocek wypadnięty", (0, 0.45, 0), (2.0, 1.0, 2.0), kolory[k])
                for xx in (-0.5, 0.5):
                    s.walec("Klocek wypustka", (xx, 1.1, 0), 0.4, 0.4, kolory[k], os="y")
            k += 1


# =========================================================================== CAŁOŚĆ
def generuj(przesun=(0.0, 0.0, -700.0), ziarno=7):
    s = Scena("Workspace/KrzyweMiasteczko", paleta=PALETA)
    rnd = random.Random(ziarno)
    DRZEWA.clear()
    with s.uklad(pos=przesun):
        teren(s, random.Random(rnd.randint(0, 10 ** 6)))
        rynek(s, random.Random(rnd.randint(0, 10 ** 6)))
        ulice(s, random.Random(rnd.randint(0, 10 ** 6)))
        mur(s, random.Random(rnd.randint(0, 10 ** 6)))
        budynki(s, ziarno)
        domy(s, random.Random(rnd.randint(0, 10 ** 6)))
        stragany(s, random.Random(rnd.randint(0, 10 ** 6)))
        staw(s, random.Random(rnd.randint(0, 10 ** 6)))
        zielen(s, random.Random(rnd.randint(0, 10 ** 6)))
        tlo(s, random.Random(rnd.randint(0, 10 ** 6)))
        rekwizyty(s, random.Random(rnd.randint(0, 10 ** 6)))
    return s


def raport(s):
    pref = len(s.korzen) + 1
    grupy = {}
    for c in s.czesci:
        g = s.grupy[c[1]][pref:].split("/")[0]
        grupy[g] = grupy.get(g, 0) + 1
    print("CZĘŚCI: %d" % len(s.czesci))
    for g in sorted(grupy, key=lambda k: -grupy[k]):
        print("  %-16s %5d" % (g, grupy[g]))
    mats = s.materialy
    kule = sum(1 for c in s.czesci if c[0] == KULA)
    walce = sum(1 for c in s.czesci if c[0] == WALEC)
    neon = sum(1 for c in s.czesci if mats[c[12]] == "Neon")
    przezr = sum(1 for c in s.czesci if 0 < c[13] < 1)
    bez_kol = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 1)
    bez_cien = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 2)
    smooth = sum(1 for c in s.czesci if mats[c[12]] == "SmoothPlastic")
    n = float(len(s.czesci))
    print("SUFITY: kule %d (≤150), walce %d (≤600), Neon %d (≤150), przezroczyste %d (≤10), z kolizją %.0f%% (≤40%%), "
          "bez cienia %.0f%% (≥40%%), SmoothPlastic %.0f%%" % (kule, walce, neon, przezr, 100 * (n - bez_kol) / n, 100 * bez_cien / n,
                                                                100 * smooth / n))
    return grupy


def main():
    ap = argparse.ArgumentParser(description="Generator mapy v2 „Krzywe Miasteczko”")
    ap.add_argument("--przesun", default="0,0,-700")
    ap.add_argument("--ziarno", type=int, default=7)
    ap.add_argument("--wyj", default=os.path.join(TU, "czesci.json"))
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    przes = tuple(float(v) for v in a.przesun.split(","))
    s = generuj(przes, a.ziarno)
    s.zapisz(a.wyj)
    raport(s)
    uwagi = s.sprawdz(limit_czesci=6500)
    print("SPRAWDZ: %d ostrzeżeń" % len(uwagi))
    for u in uwagi:
        print("  UWAGA:", u)
    print("ZAPISANO:", a.wyj)
    return 0


if __name__ == "__main__":
    sys.exit(main())
