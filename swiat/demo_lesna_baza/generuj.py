#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Demo „Leśna baza startowa z karczmą” — generator sceny z klocków.

Jedno źródło prawdy dla trzech miejsc: Blender (podgląd i edycja), Roblox Studio (części) i podgląd 3D w panelu.
Wynik: `czesci.json` w formacie panelu (panel/README.md → „czesci.json”): jednostka = stud, Y w górę, przód = −Z.

    python swiat/demo_lesna_baza/generuj.py            # zapisuje czesci.json obok tego pliku
    python swiat/demo_lesna_baza/generuj.py --wyj X.json

Układ: plac ze spawnem w (0, 0, 0); północ = −Z (tam stoi karczma, frontem do placu); południe = +Z (brama).
Geometria kształtów (klin, klin narożny, walec) — patrz panel/luau/KSZTALTY.md.
"""
import argparse
import json
import math
import os
import random

BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4

# --- paleta (nasycony, ciepły cartoon; nazwy materiałów = Enum.Material w Roblox)
K = {
    "trawa": "5FB548", "trawa2": "4E9E3C", "trawa3": "79C95A", "ziemia": "B58A5A", "ziemia2": "A17848",
    "bruk": "9AA0A8", "bruk2": "858B94", "bruk3": "B4B9BF", "kamien": "8D949C", "kamien2": "6C727A", "kamien3": "A7ADB4",
    "drewno_c": "5A3A22", "drewno": "8A5A34", "drewno_j": "B07A48", "deski": "C49A62", "deski2": "A9824F",
    "tynk": "F2E2B6", "tynk2": "E6D3A0", "dach": "C9472F", "dach2": "A83A26", "dach_nieb": "3F7FBF", "dach_fiol": "7B4FB5",
    "dach_pom": "D98A2B", "lisc": "3F9B3A", "lisc2": "2F8232", "lisc3": "56B84A", "igla": "2C7A3D", "igla2": "236533",
    "igla3": "37904A", "jesien": "E0A030", "woda": "4AA8E0", "okno": "FFD98A", "lampa": "FFD76A", "portal": "A45CFF",
    "portal2": "D9B8FF", "ogien": "FF8A2A", "ogien2": "FFD23F", "czerwien": "E23B3B", "biel": "F7F2E6", "kosc": "F3EAD7",
    "zloto": "F5B82E", "zelazo": "5B6470", "zelazo_j": "AEB6C2", "siano": "E7C65A", "siano2": "D4AE43", "niebieski": "4EA8FF",
    "roz": "FF9AD5", "blekit": "6FD3FF", "zielen_j": "9BE36B", "fiolet": "8B5CF6", "piwo": "F2B233", "piana": "FFF8E7",
    "czarny": "2A2420", "brazowy_kon": "9A6A3E", "grzywa": "3C2A1C", "baner": "C4302B", "baner2": "2F5FB5",
}


class Scena:
    def __init__(self, korzen="Workspace/DemoLesnaBaza"):
        self.korzen = korzen
        self.grupy, self.materialy, self.czesci = [], [], []

    def _idx(self, lista, wartosc):
        if wartosc not in lista:
            lista.append(wartosc)
        return lista.index(wartosc)

    def dodaj(self, ksztalt, grupa, nazwa, pos, size, kolor, mat="SmoothPlastic", rot=(0, 0, 0), alfa=0.0):
        g = self._idx(self.grupy, self.korzen + "/" + grupa)
        m = self._idx(self.materialy, mat)
        kolor = K.get(kolor, kolor).lstrip("#").upper()
        self.czesci.append([ksztalt, g, round(pos[0], 3), round(pos[1], 3), round(pos[2], 3),
                            round(math.radians(rot[0]), 4), round(math.radians(rot[1]), 4), round(math.radians(rot[2]), 4),
                            round(abs(size[0]), 3), round(abs(size[1]), 3), round(abs(size[2]), 3), kolor, m, round(alfa, 2),
                            nazwa[:40]])

    # --- prymitywy
    def blok(self, g, n, pos, size, kolor, mat="SmoothPlastic", rot=(0, 0, 0), alfa=0.0):
        self.dodaj(BLOK, g, n, pos, size, kolor, mat, rot, alfa)

    def kula(self, g, n, pos, srednica, kolor, mat="SmoothPlastic", alfa=0.0):
        self.dodaj(KULA, g, n, pos, (srednica, srednica, srednica), kolor, mat, (0, 0, 0), alfa)

    def klin(self, g, n, pos, size, kolor, mat="SmoothPlastic", rot=(0, 0, 0), alfa=0.0):
        self.dodaj(KLIN, g, n, pos, size, kolor, mat, rot, alfa)

    def walec_pion(self, g, n, x, y0, z, r, h, kolor, mat="SmoothPlastic", przechyl=(0, 0), alfa=0.0):
        """Walec stojący: podstawa w y0, promień r, wysokość h. przechyl = (stopnie wokół X, stopnie wokół Z dodatkowo)."""
        self.dodaj(WALEC, g, n, (x, y0 + h / 2, z), (h, 2 * r, 2 * r), kolor, mat, (przechyl[0], 0, 90 + przechyl[1]), alfa)

    def walec_os(self, g, n, pos, r, dl, kolor, mat="SmoothPlastic", os_="x", alfa=0.0):
        """Walec leżący: oś wzdłuż X albo Z."""
        self.dodaj(WALEC, g, n, pos, (dl, 2 * r, 2 * r), kolor, mat, (0, 90, 0) if os_ == "z" else (0, 0, 0), alfa)

    def ostroslup(self, g, n, cx, y0, cz, a, h, kolor, mat="SmoothPlastic", obrot=0.0):
        """Ostrosłup o podstawie 2a × 2a z czterech klinów narożnych (wierzchołek nad środkiem)."""
        for k in range(4):
            kat = math.radians(90 * k + obrot)
            qx, qz = -a / 2, a / 2
            x = qx * math.cos(kat) + qz * math.sin(kat)
            z = -qx * math.sin(kat) + qz * math.cos(kat)
            self.dodaj(NAROZNIK, g, n, (cx + x, y0 + h / 2, cz + z), (a, h, a), kolor, mat, (0, 90 * k + obrot, 0))

    def belka(self, g, n, p1, p2, grub, kolor, mat="Wood", szer=None):
        """Belka między dwoma punktami (długa oś = lokalne Z)."""
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        dl = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dl < 1e-6:
            return
        rx = math.degrees(math.asin(max(-1.0, min(1.0, -dy / dl))))
        ry = math.degrees(math.atan2(dx, dz))
        self.blok(g, n, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2), (szer or grub, grub, dl), kolor, mat,
                  (rx, ry, 0))

    def dach_x(self, g, n, cx, y_okap, cz, dl_x, pol, wznios, grub, kolor, mat="Slate", nadmiar=1.2):
        """Dach dwuspadowy z dwóch płyt, kalenica wzdłuż X; pol = połowa głębokości (z okapem)."""
        kat = math.degrees(math.atan2(wznios, pol))
        dl = math.hypot(pol, wznios) + nadmiar
        for znak in (1, -1):
            self.blok(g, n, (cx, y_okap + wznios / 2 + grub * 0.35, cz + znak * (pol / 2 + nadmiar * 0.32)), (dl_x, grub, dl),
                      kolor, mat, (znak * kat, 0, 0))
        self.blok(g, n + " kalenica", (cx, y_okap + wznios + grub * 0.55, cz), (dl_x + 0.6, grub * 0.9, grub * 1.6), "dach2", mat)

    def dach_z(self, g, n, cx, y_okap, cz, dl_z, pol, wznios, grub, kolor, mat="Slate", nadmiar=1.2):
        """Dach dwuspadowy, kalenica wzdłuż Z."""
        kat = math.degrees(math.atan2(wznios, pol))
        dl = math.hypot(pol, wznios) + nadmiar
        for znak in (1, -1):
            self.blok(g, n, (cx + znak * (pol / 2 + nadmiar * 0.32), y_okap + wznios / 2 + grub * 0.35, cz), (dl, grub, dl_z),
                      kolor, mat, (0, 0, -znak * kat))
        self.blok(g, n + " kalenica", (cx, y_okap + wznios + grub * 0.55, cz), (grub * 1.6, grub * 0.9, dl_z + 0.6), "dach2", mat)

    def szczyt_x(self, g, n, x, y0, cz, pol, wznios, grub, kolor, mat="SmoothPlastic"):
        """Trójkątna ściana szczytowa w płaszczyźnie YZ (dla dachu z kalenicą wzdłuż X)."""
        self.klin(g, n, (x, y0 + wznios / 2, cz - pol / 2), (grub, wznios, pol), kolor, mat)
        self.klin(g, n, (x, y0 + wznios / 2, cz + pol / 2), (grub, wznios, pol), kolor, mat, (0, 180, 0))

    def szczyt_z(self, g, n, cx, y0, z, pol, wznios, grub, kolor, mat="SmoothPlastic"):
        """Trójkątna ściana szczytowa w płaszczyźnie XY (dla dachu z kalenicą wzdłuż Z)."""
        self.klin(g, n, (cx - pol / 2, y0 + wznios / 2, z), (grub, wznios, pol), kolor, mat, (0, 90, 0))
        self.klin(g, n, (cx + pol / 2, y0 + wznios / 2, z), (grub, wznios, pol), kolor, mat, (0, -90, 0))

    def json(self):
        return {"wersja": 1, "grupy": self.grupy, "materialy": self.materialy, "czesci": self.czesci}


# =========================================================================== elementy wielokrotnego użytku
def beczka(s, g, x, y0, z, r=1.5, h=3.6, przechyl=(0, 0)):
    s.walec_pion(g, "Beczka", x, y0, z, r, h, "drewno_j", "WoodPlanks", przechyl)
    for dy in (0.55, h - 0.55):
        s.walec_pion(g, "Beczka obręcz", x, y0 + dy - 0.2, z, r + 0.12, 0.4, "zelazo", "Metal", przechyl)


def skrzynia(s, g, x, y0, z, a=3.0, obrot=0.0):
    s.blok(g, "Skrzynia", (x, y0 + a / 2, z), (a, a, a), "deski", "WoodPlanks", (0, obrot, 0))
    for dx, dz in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        kat = math.radians(obrot)
        ox, oz = dx * (a / 2 - 0.15), dz * (a / 2 - 0.15)
        s.blok(g, "Skrzynia listwa", (x + ox * math.cos(kat) + oz * math.sin(kat), y0 + a / 2, z - ox * math.sin(kat) + oz * math.cos(kat)),
               (0.45, a + 0.12, 0.45), "drewno_c", "Wood", (0, obrot, 0))


def latarnia(s, g, x, z, wys=9.0, strona=1):
    s.walec_pion(g, "Latarnia słup", x, 0.8, z, 0.35, wys, "drewno_c", "Wood")
    s.blok(g, "Latarnia ramię", (x + strona * 1.1, 0.8 + wys - 0.5, z), (2.4, 0.35, 0.35), "drewno_c", "Wood")
    s.blok(g, "Latarnia daszek", (x + strona * 2.0, 0.8 + wys - 0.9, z), (1.5, 0.3, 1.5), "zelazo", "Metal")
    s.blok(g, "Latarnia światło", (x + strona * 2.0, 0.8 + wys - 1.7, z), (1.0, 1.3, 1.0), "lampa", "Neon")
    s.blok(g, "Latarnia spód", (x + strona * 2.0, 0.8 + wys - 2.45, z), (1.2, 0.2, 1.2), "zelazo", "Metal")


def sosna(s, g, x, z, rnd, skala=1.0):
    h_pnia = rnd.uniform(5.0, 7.5) * skala
    r = rnd.uniform(0.9, 1.3) * skala
    s.walec_pion(g, "Sosna pień", x, 0.6, z, r, h_pnia, "drewno_c", "Wood", (rnd.uniform(-2, 2), rnd.uniform(-2, 2)))
    y = 0.6 + h_pnia - 1.2 * skala
    a = rnd.uniform(5.2, 6.6) * skala
    kol = rnd.choice(["igla", "igla2", "igla3"])
    obrot = rnd.uniform(0, 90)
    for i in range(3):
        h = rnd.uniform(7.0, 8.5) * skala * (1.0 - 0.08 * i)
        s.ostroslup(g, "Sosna igły", x, y, z, a, h, kol if i != 1 else rnd.choice(["igla", "igla3"]), "Grass", obrot + 45 * i)
        y += h * 0.52
        a *= 0.72


def drzewo(s, g, x, z, rnd, skala=1.0, jesien=False):
    h = rnd.uniform(7.0, 10.0) * skala
    r = rnd.uniform(1.1, 1.6) * skala
    s.walec_pion(g, "Drzewo pień", x, 0.6, z, r, h, "drewno", "Wood", (rnd.uniform(-3, 3), rnd.uniform(-3, 3)))
    kol = ["jesien", "dach_pom"] if jesien else ["lisc", "lisc2", "lisc3"]
    baza = rnd.uniform(6.4, 7.8) * skala
    s.blok(g, "Drzewo korona", (x, 0.6 + h + baza * 0.3, z), (baza, baza * 0.85, baza), rnd.choice(kol), "Grass",
           (rnd.uniform(-8, 8), rnd.uniform(0, 90), rnd.uniform(-8, 8)))
    n = rnd.randint(5, 6)
    for i in range(n):
        kat, odl = math.tau * i / n + rnd.uniform(-0.4, 0.4), rnd.uniform(2.8, 4.2) * skala
        a = rnd.uniform(3.6, 5.2) * skala
        s.blok(g, "Drzewo korona", (x + math.cos(kat) * odl, 0.6 + h + rnd.uniform(-0.8, 3.4) * skala, z + math.sin(kat) * odl),
               (a, a * rnd.uniform(0.8, 1.0), a), rnd.choice(kol), "Grass",
               (rnd.uniform(-12, 12), rnd.uniform(0, 90), rnd.uniform(-12, 12)))
    a = rnd.uniform(3.4, 4.4) * skala
    s.blok(g, "Drzewo korona", (x + rnd.uniform(-1, 1), 0.6 + h + baza * 0.78, z + rnd.uniform(-1, 1)), (a, a * 0.9, a), rnd.choice(kol),
           "Grass", (rnd.uniform(-10, 10), rnd.uniform(0, 90), rnd.uniform(-10, 10)))


def krzak(s, g, x, z, rnd, skala=1.0):
    for _ in range(rnd.randint(2, 3)):
        a = rnd.uniform(2.2, 3.6) * skala
        s.blok(g, "Krzak", (x + rnd.uniform(-1.3, 1.3), 0.8 + a * 0.36, z + rnd.uniform(-1.3, 1.3)), (a, a * 0.75, a),
               rnd.choice(["lisc", "lisc2", "lisc3"]), "Grass", (rnd.uniform(-6, 6), rnd.uniform(0, 90), rnd.uniform(-6, 6)))


def glaz(s, g, x, z, rnd, skala=1.0):
    a = rnd.uniform(2.2, 4.6) * skala
    s.blok(g, "Głaz", (x, 0.8 + a * 0.3, z), (a, a * 0.7, a * rnd.uniform(0.7, 1.1)), rnd.choice(["kamien", "kamien2", "kamien3"]),
           "Slate", (rnd.uniform(-10, 10), rnd.uniform(0, 90), rnd.uniform(-10, 10)))
    if rnd.random() < 0.5:
        b = a * 0.55
        s.blok(g, "Głaz", (x + a * 0.55, 0.8 + b * 0.3, z + rnd.uniform(-1, 1)), (b, b * 0.7, b), rnd.choice(["kamien", "kamien3"]),
               "Slate", (rnd.uniform(-10, 10), rnd.uniform(0, 90), rnd.uniform(-10, 10)))


def grzyb(s, g, x, z, rnd, skala=1.0):
    h = rnd.uniform(0.9, 1.5) * skala
    s.walec_pion(g, "Grzyb trzon", x, 0.8, z, 0.3 * skala, h, "kosc")
    r = rnd.uniform(0.85, 1.25) * skala
    s.walec_pion(g, "Grzyb kapelusz", x, 0.8 + h, z, r, 0.55 * skala, "czerwien")
    s.walec_pion(g, "Grzyb kapelusz", x, 0.8 + h + 0.5 * skala, z, r * 0.6, 0.35 * skala, "czerwien")
    for _ in range(3):
        kat, odl = rnd.uniform(0, math.tau), r * 0.55
        s.blok(g, "Grzyb kropka", (x + math.cos(kat) * odl, 0.8 + h + 0.58 * skala, z + math.sin(kat) * odl),
               (0.3 * skala, 0.1, 0.3 * skala), "biel")


def kwiaty(s, g, x, z, rnd):
    for _ in range(rnd.randint(2, 4)):
        fx, fz = x + rnd.uniform(-1.4, 1.4), z + rnd.uniform(-1.4, 1.4)
        s.blok(g, "Kwiat łodyga", (fx, 1.15, fz), (0.14, 0.7, 0.14), "lisc2")
        s.blok(g, "Kwiat", (fx, 1.6, fz), (0.5, 0.3, 0.5), rnd.choice(["biel", "zloto", "roz", "blekit", "czerwien"]))


def plot(s, g, punkty, wys=3.2):
    """Płot ze słupków i dwóch żerdzi wzdłuż łamanej."""
    for i, (x, z) in enumerate(punkty):
        s.blok(g, "Płot słupek", (x, 0.8 + wys / 2, z), (0.7, wys, 0.7), "drewno_c", "Wood")
        if i:
            px, pz = punkty[i - 1]
            for y in (0.8 + wys * 0.42, 0.8 + wys * 0.82):
                s.belka(g, "Płot żerdź", (px, y, pz), (x, y, z), 0.35, "drewno", "Wood")


# =========================================================================== budowle
def teren(s, rnd):
    g = "Teren"
    s.blok(g, "Polana", (0, 0.4, 0), (230, 0.8, 230), "trawa", "Grass")
    for _ in range(26):                                        # łaty trawy w innych odcieniach
        x, z = rnd.uniform(-105, 105), rnd.uniform(-105, 105)
        a = rnd.uniform(9, 22)
        s.blok(g, "Łata trawy", (x, 0.83, z), (a, 0.08, a * rnd.uniform(0.6, 1.0)), rnd.choice(["trawa2", "trawa3"]), "Grass",
               (0, rnd.uniform(0, 90), 0))
    # drogi: brama (południe) → plac → karczma; plac → arena (zachód); plac → portal (wschód)
    for i in range(11):
        z = 26 + i * 5.4
        s.blok(g, "Droga", (rnd.uniform(-0.8, 0.8), 0.86, z), (9.5 + rnd.uniform(-1, 1), 0.1, 5.8), rnd.choice(["ziemia", "ziemia2"]),
               "Ground", (0, rnd.uniform(-4, 4), 0))
    for i in range(4):
        s.blok(g, "Droga", (rnd.uniform(-0.6, 0.6), 0.86, -24 - i * 3.2), (9.0, 0.1, 3.6), rnd.choice(["ziemia", "ziemia2"]), "Ground",
               (0, rnd.uniform(-4, 4), 0))
    for znak in (-1, 1):
        for i in range(9):
            x = znak * (25 + i * 5.2)
            s.blok(g, "Droga", (x, 0.86, -6 + rnd.uniform(-0.8, 0.8)), (5.6, 0.1, 7.5 + rnd.uniform(-1, 1)),
                   rnd.choice(["ziemia", "ziemia2"]), "Ground", (0, rnd.uniform(-4, 4), 0))
    # pagórki na obrzeżach
    for _ in range(9):
        kat = rnd.uniform(0, math.tau)
        odl = rnd.uniform(84, 104)
        a = rnd.uniform(16, 28)
        x, z = math.cos(kat) * odl, math.sin(kat) * odl
        s.blok(g, "Pagórek", (x, 0.8 + 1.0, z), (a, 2.0, a * 0.8), "trawa2", "Grass", (0, rnd.uniform(0, 90), 0))
        s.blok(g, "Pagórek", (x + rnd.uniform(-2, 2), 0.8 + 2.6, z + rnd.uniform(-2, 2)), (a * 0.6, 1.4, a * 0.5), "trawa3", "Grass",
               (0, rnd.uniform(0, 90), 0))


def plac(s, rnd):
    g = "Plac"
    s.walec_pion(g, "Plac podkład", 0, 0.78, 0, 24.6, 0.06, "bruk2", "Cobblestone")
    # ozdobna płyta nad istniejącym SpawnLocation (12×1×12 w środku — zostaje nietknięty pod spodem)
    s.blok(g, "Spawn płyta", (0, 1.08, 0), (12.6, 0.16, 12.6), "bruk3", "Cobblestone")
    s.blok(g, "Spawn herb", (0, 1.2, 0), (5.2, 0.1, 5.2), "zloto", "SmoothPlastic", (0, 45, 0))
    s.blok(g, "Spawn herb", (0, 1.26, 0), (3.0, 0.1, 3.0), "baner", "SmoothPlastic", (0, 45, 0))
    # bruk w pierścieniach wokół spawnu
    for i in range(16):
        kat = math.tau * i / 16
        x, z = math.cos(kat) * 10.6, math.sin(kat) * 10.6
        s.blok(g, "Bruk", (x, 0.9, z), (5.2, 0.2, 4.4), rnd.choice(["bruk", "bruk2", "bruk3"]), "Cobblestone",
               (0, -math.degrees(kat) + 90, 0))
    for i in range(26):
        kat = math.tau * i / 26
        x, z = math.cos(kat) * 16.4, math.sin(kat) * 16.4
        s.blok(g, "Bruk", (x, 0.88, z), (5.6, 0.16, 4.2), rnd.choice(["bruk", "bruk2", "bruk3"]), "Cobblestone",
               (0, -math.degrees(kat) + 90, 0))
    for i in range(34):
        kat = math.tau * i / 34
        x, z = math.cos(kat) * 21.6, math.sin(kat) * 21.6
        s.blok(g, "Bruk", (x, 0.86, z), (5.2, 0.12, 4.0), rnd.choice(["bruk", "bruk2", "bruk3"]), "Cobblestone",
               (0, -math.degrees(kat) + 90, 0))
    # obwódka spawnu
    for dx, dz, sx, sz in ((0, 6.8, 14.6, 1.0), (0, -6.8, 14.6, 1.0), (6.8, 0, 1.0, 12.6), (-6.8, 0, 1.0, 12.6)):
        s.blok(g, "Spawn obwódka", (dx, 1.0, dz), (sx, 0.4, sz), "zloto", "SmoothPlastic")
    # studnia (na wschód od spawnu)
    wx, wz = 13.5, 9.5
    for i in range(10):
        kat = math.tau * i / 10
        s.blok(g, "Studnia cembrowina", (wx + math.cos(kat) * 3.0, 2.0, wz + math.sin(kat) * 3.0), (2.1, 2.4, 1.1),
               rnd.choice(["kamien", "kamien2", "kamien3"]), "Cobblestone", (0, -math.degrees(kat) + 90, 0))
    s.walec_pion(g, "Studnia woda", wx, 1.0, wz, 2.6, 1.5, "woda", "SmoothPlastic", alfa=0.25)
    for znak in (-1, 1):
        s.blok(g, "Studnia słup", (wx + znak * 3.1, 4.9, wz), (0.6, 8.2, 0.6), "drewno_c", "Wood")
    s.walec_os(g, "Studnia wał", (wx, 7.6, wz), 0.35, 6.2, "drewno", "Wood", "x")
    s.dach_x(g, "Studnia daszek", wx, 8.6, wz, 8.2, 2.8, 2.0, 0.5, "dach", "Slate", 0.6)
    s.blok(g, "Studnia lina", (wx + 0.6, 5.6, wz), (0.14, 3.6, 0.14), "kosc", "Fabric")
    s.walec_pion(g, "Studnia wiadro", wx + 0.6, 3.2, wz, 0.6, 1.0, "drewno_j", "WoodPlanks")
    # ławki przy placu
    for kat_st in (200, 250, 290):
        kat = math.radians(kat_st)
        x, z = math.cos(kat) * 19.0, math.sin(kat) * 19.0
        obrot = -kat_st + 90
        s.blok(g, "Ławka siedzisko", (x, 2.2, z), (6.0, 0.4, 1.8), "deski", "WoodPlanks", (0, obrot, 0))
        s.blok(g, "Ławka oparcie", (x + math.cos(kat) * 0.9, 3.4, z + math.sin(kat) * 0.9), (6.0, 1.6, 0.35), "deski2", "WoodPlanks",
               (0, obrot, 0))
        for d in (-2.4, 2.4):
            ox = d * math.cos(math.radians(obrot))
            oz = -d * math.sin(math.radians(obrot))
            s.blok(g, "Ławka noga", (x + ox, 1.5, z + oz), (0.5, 1.4, 1.6), "drewno_c", "Wood", (0, obrot, 0))


def karczma(s, rnd):
    g = "Karczma"
    cx, cz = 0.0, -50.0                                        # środek bryły; front (drzwi) na +Z, czyli od strony placu
    W, D = 40.0, 28.0                                          # szerokość (X) i głębokość (Z) parteru
    y0 = 0.8
    front = cz + D / 2
    # podmurówka
    s.blok(g, "Podmurówka", (cx, y0 + 1.5, cz), (W + 2.4, 3.0, D + 2.4), "kamien", "Cobblestone")
    for i in range(9):
        x = cx - (W + 2.4) / 2 + 2.6 + i * 4.9
        s.blok(g, "Podmurówka kamień", (x, y0 + 1.5, front + 1.25), (3.4, 2.2 + rnd.uniform(-0.3, 0.3), 0.3),
               rnd.choice(["kamien2", "kamien3"]), "Cobblestone")
    yp = y0 + 3.0                                              # poziom podłogi parteru
    # parter: tynk + belki
    hp = 11.0
    s.blok(g, "Ściany parteru", (cx, yp + hp / 2, cz), (W, hp, D), "tynk", "SmoothPlastic")
    for x in (cx - W / 2, cx - W / 4, cx, cx + W / 4, cx + W / 2):
        for z in (front, cz - D / 2):
            s.blok(g, "Belka pionowa", (x + (0.35 if x < cx else -0.35 if x > cx else 0), yp + hp / 2, z + (0.2 if z > cz else -0.2)),
                   (1.1, hp, 0.7), "drewno_c", "Wood")
    for z in (front, cz - D / 2):
        for y in (yp + 0.5, yp + hp - 0.5):
            s.blok(g, "Belka pozioma", (cx, y, z + (0.25 if z > cz else -0.25)), (W + 0.8, 1.0, 0.7), "drewno_c", "Wood")
    for x in (cx - W / 2, cx + W / 2):
        for z in (cz - D / 4, cz, cz + D / 4):
            s.blok(g, "Belka pionowa", (x + (0.2 if x > cx else -0.2), yp + hp / 2, z), (0.7, hp, 1.1), "drewno_c", "Wood")
        for y in (yp + 0.5, yp + hp - 0.5):
            s.blok(g, "Belka pozioma", (x + (0.25 if x > cx else -0.25), y, cz), (0.7, 1.0, D + 0.8), "drewno_c", "Wood")
    # zastrzały (ukośne belki) na froncie
    for x1, x2 in ((cx - W / 2 + 1, cx - W / 4 - 1), (cx + W / 2 - 1, cx + W / 4 + 1)):
        s.belka(g, "Zastrzał", (x1, yp + 1.0, front + 0.3), (x2, yp + hp - 1.0, front + 0.3), 0.7, "drewno_c", "Wood")
    # drzwi (środek frontu) + schody
    s.blok(g, "Drzwi futryna", (cx, yp + 4.6, front + 0.35), (7.4, 9.2, 0.8), "drewno_c", "Wood")
    s.blok(g, "Drzwi", (cx, yp + 4.1, front + 0.6), (5.6, 8.2, 0.6), "drewno", "WoodPlanks")
    for dx in (-1.9, 0, 1.9):
        s.blok(g, "Drzwi deska", (cx + dx, yp + 4.1, front + 0.95), (1.5, 7.8, 0.12), "drewno_j", "WoodPlanks")
    for y in (yp + 1.6, yp + 6.4):
        s.blok(g, "Drzwi okucie", (cx, y, front + 1.05), (5.8, 0.5, 0.14), "zelazo", "Metal")
    s.kula(g, "Drzwi klamka", (cx + 2.0, yp + 4.0, front + 1.2), 0.7, "zloto", "Metal")
    s.blok(g, "Drzwi nadproże", (cx, yp + 9.5, front + 0.7), (8.6, 1.0, 1.2), "drewno_c", "Wood")
    for i, (sz, sy) in enumerate(((3.4, 1.0), (2.2, 2.0), (1.0, 3.0))):
        s.blok(g, "Schody", (cx, y0 + sy / 2, front + 1.2 + sz), (10.0 - i * 0.6, sy, 1.3), "kamien3" if i % 2 else "kamien",
               "Cobblestone")
    # okna parteru (front): 2 po każdej stronie drzwi, z okiennicami i skrzynką kwiatów
    for x in (cx - 14.5, cx - 7.6, cx + 7.6, cx + 14.5):
        s.blok(g, "Okno rama", (x, yp + 5.6, front + 0.35), (4.4, 5.0, 0.7), "drewno_c", "Wood")
        s.blok(g, "Okno szyba", (x, yp + 5.6, front + 0.6), (3.4, 4.0, 0.3), "okno", "Neon")
        s.blok(g, "Okno szpros", (x, yp + 5.6, front + 0.8), (0.3, 4.0, 0.15), "drewno_c", "Wood")
        s.blok(g, "Okno szpros", (x, yp + 5.6, front + 0.8), (3.4, 0.3, 0.15), "drewno_c", "Wood")
        for znak in (-1, 1):
            s.blok(g, "Okiennica", (x + znak * 2.75, yp + 5.6, front + 0.55), (1.1, 4.6, 0.3), "lisc2", "WoodPlanks", (0, znak * -12, 0))
        s.blok(g, "Skrzynka na kwiaty", (x, yp + 2.7, front + 1.0), (4.2, 0.9, 1.1), "drewno", "WoodPlanks")
        for dx in (-1.3, 0, 1.3):
            s.blok(g, "Kwiat w skrzynce", (x + dx, yp + 3.4, front + 1.0), (0.8, 0.7, 0.8), rnd.choice(["czerwien", "roz", "zloto", "biel"]),
                   "Grass", (0, rnd.uniform(0, 45), 0))
    # piętro (nadwieszone)
    hpi = 9.5
    ypi = yp + hp
    Wp, Dp = W + 3.0, D + 3.0
    frontp = cz + Dp / 2
    s.blok(g, "Belki stropu", (cx, ypi + 0.5, cz), (Wp + 0.6, 1.0, Dp + 0.6), "drewno_c", "Wood")
    for i in range(11):
        x = cx - Wp / 2 + 1.0 + i * (Wp - 2.0) / 10
        s.blok(g, "Belka stropu czoło", (x, ypi + 0.2, frontp + 0.5), (0.9, 0.9, 1.4), "drewno", "Wood")
    s.blok(g, "Ściany piętra", (cx, ypi + 1.0 + hpi / 2, cz), (Wp, hpi, Dp), "tynk2", "SmoothPlastic")
    for x in (cx - Wp / 2, cx - Wp / 6, cx + Wp / 6, cx + Wp / 2):
        s.blok(g, "Belka piętra", (x + (0.3 if x < cx else -0.3), ypi + 1.0 + hpi / 2, frontp + 0.2), (1.0, hpi, 0.7), "drewno_c", "Wood")
        s.blok(g, "Belka piętra", (x + (0.3 if x < cx else -0.3), ypi + 1.0 + hpi / 2, cz - Dp / 2 - 0.2), (1.0, hpi, 0.7), "drewno_c", "Wood")
    s.blok(g, "Belka piętra góra", (cx, ypi + 0.6 + hpi, frontp + 0.25), (Wp + 0.8, 1.0, 0.7), "drewno_c", "Wood")
    for x1, x2 in ((cx - Wp / 2 + 1, cx - Wp / 6 - 1), (cx + Wp / 6 + 1, cx + Wp / 2 - 1)):
        s.belka(g, "Krzyżak", (x1, ypi + 1.6, frontp + 0.3), (x2, ypi + hpi, frontp + 0.3), 0.6, "drewno_c", "Wood")
        s.belka(g, "Krzyżak", (x2, ypi + 1.6, frontp + 0.3), (x1, ypi + hpi, frontp + 0.3), 0.6, "drewno_c", "Wood")
    for x in (cx - 3.6, cx + 3.6):
        s.blok(g, "Okno piętra rama", (x, ypi + 5.4, frontp + 0.35), (4.6, 4.8, 0.7), "drewno_c", "Wood")
        s.blok(g, "Okno piętra szyba", (x, ypi + 5.4, frontp + 0.6), (3.6, 3.8, 0.3), "okno", "Neon")
        s.blok(g, "Okno piętra szpros", (x, ypi + 5.4, frontp + 0.8), (0.3, 3.8, 0.15), "drewno_c", "Wood")
    for x in (cx - Wp / 2 - 0.2, cx + Wp / 2 + 0.2):
        for z in (cz - 6.5, cz + 6.5):
            s.blok(g, "Okno boczne rama", (x, ypi + 5.4, z), (0.7, 4.6, 4.2), "drewno_c", "Wood")
            s.blok(g, "Okno boczne szyba", (x + (0.25 if x > cx else -0.25), ypi + 5.4, z), (0.3, 3.6, 3.2), "okno", "Neon")
    # dach główny (kalenica wzdłuż X) + ściany szczytowe
    yd = ypi + 1.0 + hpi
    pol, wznios = Dp / 2 + 2.2, 15.5
    s.szczyt_x(g, "Szczyt", cx - Wp / 2 + 0.5, yd, cz, Dp / 2, wznios * (Dp / 2) / pol, 1.0, "tynk2")
    s.szczyt_x(g, "Szczyt", cx + Wp / 2 - 0.5, yd, cz, Dp / 2, wznios * (Dp / 2) / pol, 1.0, "tynk2")
    for x in (cx - Wp / 2 - 0.1, cx + Wp / 2 + 0.1):
        s.blok(g, "Szczyt belka", (x, yd + 4.2, cz), (0.6, 0.9, 16.0), "drewno_c", "Wood")
        s.blok(g, "Szczyt słupek", (x, yd + 5.4, cz), (0.6, 9.6, 0.9), "drewno_c", "Wood")
        s.blok(g, "Okienko strychu", (x + (0.2 if x > cx else -0.2), yd + 2.4, cz), (0.4, 2.4, 2.4), "okno", "Neon")
    s.dach_x(g, "Dach", cx, yd - 0.4, cz, Wp + 5.0, pol, wznios, 1.5, "dach", "Slate", 1.6)
    # lukarna nad wejściem
    s.blok(g, "Lukarna ściana", (cx, yd + 5.0, frontp - 6.0), (7.0, 5.0, 6.0), "tynk", "SmoothPlastic")
    s.blok(g, "Lukarna okno", (cx, yd + 5.2, frontp - 2.9), (3.6, 3.0, 0.3), "okno", "Neon")
    s.blok(g, "Lukarna rama", (cx, yd + 5.2, frontp - 3.05), (4.4, 3.8, 0.3), "drewno_c", "Wood")
    s.dach_z(g, "Lukarna dach", cx, yd + 7.3, frontp - 6.0, 7.6, 4.3, 3.0, 0.8, "dach2", "Slate", 0.8)
    s.szczyt_z(g, "Lukarna szczyt", cx, yd + 7.5, frontp - 3.0, 3.5, 2.4, 0.5, "tynk")
    # komin (lekko krzywy) i dym
    kx, kz = cx + 12.5, cz - 5.0
    s.blok(g, "Komin", (kx, yd + 10.5, kz), (4.2, 17.0, 4.2), "kamien2", "Cobblestone", (0, 0, 3.5))
    s.blok(g, "Komin czapa", (kx - 0.55, yd + 19.3, kz), (5.4, 1.2, 5.4), "kamien", "Cobblestone", (0, 0, 3.5))
    for i, (dy, dx, d) in enumerate(((2.4, 0.4, 2.6), (5.2, 1.5, 3.4), (8.6, 3.2, 4.4), (12.4, 5.6, 5.4))):
        s.kula(g, "Dym", (kx - 0.6 + dx, yd + 19.3 + dy, kz + (i % 2) * 0.8), d, "biel", "SmoothPlastic", 0.35 + i * 0.12)
    # szyld z kuflem na wysięgniku (po lewej od drzwi)
    sx_ = cx - 12.0
    sz_ = front + 4.6
    s.blok(g, "Szyld wysięgnik", (sx_, ypi - 0.6, front + 2.6), (0.7, 0.7, 5.6), "drewno_c", "Wood")
    s.belka(g, "Szyld zastrzał", (sx_, ypi - 4.0, front + 0.6), (sx_, ypi - 0.9, front + 3.6), 0.5, "drewno_c", "Wood")
    for dx in (-2.2, 2.2):
        s.blok(g, "Szyld łańcuch", (sx_ + dx, ypi - 1.7, sz_), (0.18, 1.6, 0.18), "zelazo", "Metal")
    s.blok(g, "Szyld deska", (sx_, ypi - 5.4, sz_), (6.4, 6.0, 0.5), "drewno_j", "WoodPlanks", (0, 0, -3))
    s.blok(g, "Szyld rama", (sx_, ypi - 5.4, sz_), (7.0, 6.6, 0.3), "drewno_c", "Wood", (0, 0, -3))
    for strona in (0.36, -0.36):                               # kufel po obu stronach deski
        z = sz_ + strona
        s.blok(g, "Kufel", (sx_ - 0.4, ypi - 5.9, z), (2.6, 3.2, 0.3), "piwo", "SmoothPlastic", (0, 0, -3))
        s.blok(g, "Kufel piana", (sx_ - 0.4, ypi - 3.9, z), (3.1, 1.1, 0.34), "piana", "SmoothPlastic", (0, 0, -3))
        s.blok(g, "Kufel piana", (sx_ + 0.5, ypi - 4.6, z), (0.9, 0.9, 0.34), "piana", "SmoothPlastic", (0, 0, -3))
        s.blok(g, "Kufel ucho", (sx_ + 1.6, ypi - 5.3, z), (0.5, 2.0, 0.3), "piwo", "SmoothPlastic", (0, 0, -3))
        s.blok(g, "Kufel ucho", (sx_ + 1.25, ypi - 4.5, z), (0.8, 0.45, 0.3), "piwo", "SmoothPlastic", (0, 0, -3))
        s.blok(g, "Kufel ucho", (sx_ + 1.25, ypi - 6.2, z), (0.8, 0.45, 0.3), "piwo", "SmoothPlastic", (0, 0, -3))
    # lampy przy drzwiach
    for znak in (-1, 1):
        x = cx + znak * 5.0
        s.blok(g, "Lampa wspornik", (x, yp + 8.2, front + 1.0), (0.4, 0.4, 1.6), "zelazo", "Metal")
        s.blok(g, "Lampa", (x, yp + 7.3, front + 1.7), (1.1, 1.5, 1.1), "lampa", "Neon")
        s.blok(g, "Lampa daszek", (x, yp + 8.2, front + 1.7), (1.5, 0.3, 1.5), "zelazo", "Metal")
    # przybudówka (spiżarnia) po prawej, z dachem jednospadowym
    px = cx + W / 2 + 6.0
    s.blok(g, "Przybudówka podmurówka", (px, y0 + 1.0, cz + 2.0), (12.4, 2.0, 16.4), "kamien", "Cobblestone")
    s.blok(g, "Przybudówka ściany", (px, y0 + 6.0, cz + 2.0), (11.6, 8.0, 15.6), "deski2", "WoodPlanks")
    s.klin(g, "Przybudówka dach", (px + 0.5, y0 + 12.6, cz + 2.0), (18.0, 5.4, 14.4), "dach2", "Slate", (0, -90, 0))
    s.blok(g, "Przybudówka drzwi", (px, y0 + 5.2, cz + 9.9), (4.0, 6.4, 0.4), "drewno", "WoodPlanks")
    # beczki, skrzynie, stoły przed karczmą
    beczka(s, g, cx - 19.0, y0, front + 3.4)
    beczka(s, g, cx - 16.0, y0, front + 4.6, 1.3, 3.2)
    beczka(s, g, cx - 18.2, y0 + 3.6, front + 3.6, 1.2, 3.0, (0, 6))
    skrzynia(s, g, cx + 17.5, y0, front + 3.6, 3.2, 12)
    skrzynia(s, g, cx + 20.6, y0, front + 5.0, 2.6, -20)
    skrzynia(s, g, cx + 18.2, y0 + 3.2, front + 4.0, 2.2, 30)
    for tx, tz in ((cx - 9.5, front + 12.5), (cx + 10.0, front + 13.5)):
        s.walec_pion(g, "Stół blat", tx, y0 + 2.8, tz, 3.0, 0.5, "deski", "WoodPlanks")
        s.walec_pion(g, "Stół noga", tx, y0, tz, 0.6, 2.8, "drewno_c", "Wood")
        for kat_st in (30, 150, 270):
            kat = math.radians(kat_st)
            s.walec_pion(g, "Stołek", tx + math.cos(kat) * 4.3, y0, tz + math.sin(kat) * 4.3, 0.9, 1.7, "drewno", "Wood")
        s.blok(g, "Kufel na stole", (tx + 0.9, y0 + 3.9, tz - 0.6), (0.8, 1.2, 0.8), "piwo", "SmoothPlastic")
        s.blok(g, "Kufel na stole piana", (tx + 0.9, y0 + 4.6, tz - 0.6), (0.9, 0.3, 0.9), "piana", "SmoothPlastic")


def tablica_zlecen(s, rnd):
    g = "TablicaZlecen"
    x, z = 16.0, -27.5
    for dx in (-3.4, 3.4):
        s.blok(g, "Tablica słup", (x + dx, 4.6, z), (0.8, 7.6, 0.8), "drewno_c", "Wood")
    s.blok(g, "Tablica", (x, 5.6, z), (7.4, 4.6, 0.5), "deski", "WoodPlanks")
    s.dach_x(g, "Tablica daszek", x, 8.4, z, 9.4, 1.6, 1.2, 0.4, "dach", "Slate", 0.4)
    for i, (dx, dy) in enumerate(((-2.2, 0.8), (0.2, 1.0), (2.3, 0.6), (-1.2, -0.9), (1.4, -0.8))):
        s.blok(g, "Zlecenie", (x + dx, 5.6 + dy, z + 0.32), (1.6, 1.5, 0.08), "kosc" if i != 1 else "zloto", "SmoothPlastic",
               (0, 0, rnd.uniform(-9, 9)))
        s.blok(g, "Zlecenie pinezka", (x + dx, 5.6 + dy + 0.55, z + 0.4), (0.22, 0.22, 0.1), "czerwien", "SmoothPlastic")


def kolo_fortuny(s, rnd):
    g = "KoloFortuny"
    x, z = -17.0, -27.0
    s.blok(g, "Koło podest", (x, 1.2, z), (9.0, 0.8, 5.0), "deski", "WoodPlanks")
    for dx in (-2.4, 2.4):
        s.belka(g, "Koło noga", (x + dx, 1.6, z + 1.6), (x, 8.0, z), 0.6, "drewno_c", "Wood")
    s.walec_os(g, "Koło tarcza", (x, 8.0, z + 0.6), 4.6, 0.6, "biel", "SmoothPlastic", "z")
    s.walec_os(g, "Koło obręcz", (x, 8.0, z + 0.5), 4.9, 0.3, "zloto", "Metal", "z")
    kolory = ["czerwien", "zloto", "niebieski", "zielen_j", "fiolet", "dach_pom", "roz", "blekit"]
    for i in range(8):
        kat = math.radians(i * 45 + 22.5)
        s.blok(g, "Koło pole", (x + math.cos(kat) * 2.6, 8.0 + math.sin(kat) * 2.6, z + 0.95), (3.0, 1.9, 0.14), kolory[i], "SmoothPlastic",
               (0, 0, i * 45 + 22.5))
    s.walec_os(g, "Koło piasta", (x, 8.0, z + 1.1), 0.8, 0.5, "zloto", "Metal", "z")
    s.klin(g, "Koło wskaźnik", (x, 13.2, z + 1.0), (0.5, 1.6, 1.4), "czerwien", "SmoothPlastic", (90, 0, 0))
    s.blok(g, "Koło daszek", (x, 14.4, z + 0.4), (11.0, 0.6, 3.4), "dach_fiol", "Fabric", (-8, 0, 0))
    for dx in (-5.0, 5.0):
        s.blok(g, "Koło słup", (x + dx, 7.6, z - 0.9), (0.6, 13.2, 0.6), "drewno_c", "Wood")


def sklep(s, rnd):
    g = "Sklep"
    x, z = 36.0, 14.0                                          # stragan frontem na zachód (do placu)
    s.blok(g, "Sklep podest", (x, 1.1, z), (10.0, 0.6, 14.0), "deski2", "WoodPlanks")
    s.blok(g, "Sklep lada", (x - 3.6, 2.9, z), (2.2, 3.2, 12.0), "deski", "WoodPlanks")
    s.blok(g, "Sklep blat", (x - 3.8, 4.7, z), (3.0, 0.4, 12.6), "drewno_j", "WoodPlanks")
    for dz in (-6.4, 6.4):
        for dx in (-4.4, 4.4):
            s.blok(g, "Sklep słup", (x + dx, 6.2, z + dz), (0.7, 10.0, 0.7), "drewno_c", "Wood")
    s.blok(g, "Sklep tył", (x + 4.4, 5.4, z), (0.5, 8.0, 12.6), "deski2", "WoodPlanks")
    for i in range(7):                                         # markiza w pasy
        s.blok(g, "Sklep markiza", (x - 0.6, 11.6, z - 6.0 + i * 2.0), (12.4, 0.4, 2.0), "dach_nieb" if i % 2 == 0 else "biel", "Fabric",
               (0, 0, 14))
    for i, kol in enumerate(["czerwien", "niebieski", "zielen_j", "fiolet"]):   # mikstury na ladzie
        s.walec_pion(g, "Mikstura", x - 3.8, 4.9, z - 4.2 + i * 1.4, 0.4, 1.0, kol, "Glass", alfa=0.2)
        s.walec_pion(g, "Mikstura korek", x - 3.8, 5.9, z - 4.2 + i * 1.4, 0.2, 0.35, "drewno_j", "Wood")
    s.blok(g, "Tarcza", (x + 4.0, 7.4, z - 3.0), (0.3, 2.8, 2.4), "baner2", "Metal")
    s.blok(g, "Tarcza okucie", (x + 3.8, 7.4, z - 3.0), (0.2, 0.6, 0.6), "zloto", "Metal")
    s.blok(g, "Miecz ostrze", (x + 4.0, 7.6, z + 2.4), (0.2, 4.4, 0.6), "zelazo_j", "Metal", (20, 0, 0))
    s.blok(g, "Miecz jelec", (x + 4.0, 5.9, z + 1.75), (0.25, 0.4, 1.8), "zloto", "Metal", (20, 0, 0))
    s.blok(g, "Skrzynia skarbów", (x - 3.8, 5.4, z + 4.0), (1.6, 1.0, 2.2), "drewno", "WoodPlanks")
    s.blok(g, "Skrzynia skarbów okucie", (x - 3.8, 5.95, z + 4.0), (1.7, 0.25, 2.3), "zloto", "Metal")
    beczka(s, g, x - 5.4, 0.8, z + 8.6, 1.3, 3.2)
    skrzynia(s, g, x - 5.0, 0.8, z - 8.8, 2.6, 15)


def stajnia(s, rnd):
    g = "Stajnia"
    x, z = -42.0, 18.0
    s.blok(g, "Stajnia podłoga", (x, 1.0, z), (18.0, 0.4, 14.0), "ziemia2", "Ground")
    for dx in (-8.4, 0, 8.4):
        for dz in (-6.4, 6.4):
            s.blok(g, "Stajnia słup", (x + dx, 5.4, z + dz), (0.9, 9.0, 0.9), "drewno_c", "Wood")
    s.blok(g, "Stajnia ściana", (x, 5.2, z - 6.6), (17.6, 8.4, 0.5), "deski2", "WoodPlanks")
    for dx in (-8.6, 8.6):
        s.blok(g, "Stajnia ściana", (x + dx, 4.0, z - 1.8), (0.5, 6.0, 9.6), "deski2", "WoodPlanks")
    s.dach_x(g, "Stajnia dach", x, 9.6, z, 21.0, 8.6, 5.2, 0.9, "dach_pom", "Slate", 1.0)
    s.szczyt_x(g, "Stajnia szczyt", x - 8.8, 9.8, z, 6.6, 4.0, 0.5, "deski2", "WoodPlanks")
    s.szczyt_x(g, "Stajnia szczyt", x + 8.8, 9.8, z, 6.6, 4.0, 0.5, "deski2", "WoodPlanks")
    for i, (dx, dz) in enumerate(((-5.6, -4.0), (-5.0, -4.2), (5.8, -4.2))):
        s.blok(g, "Siano", (x + dx, 2.2 + (2.2 if i == 1 else 0), z + dz), (3.2, 2.2, 2.6), "siano" if i != 1 else "siano2", "Fabric",
               (0, rnd.uniform(-8, 8), 0))
    s.blok(g, "Koryto", (x + 6.0, 1.9, z + 4.6), (5.0, 1.4, 1.8), "drewno", "WoodPlanks")
    s.blok(g, "Koryto woda", (x + 6.0, 2.5, z + 4.6), (4.4, 0.3, 1.2), "woda", "SmoothPlastic", alfa=0.2)
    # klockowy koń (zapowiedź wierzchowców)
    kx, kz = x - 0.5, z + 1.5
    s.blok(g, "Koń tułów", (kx, 4.6, kz), (5.6, 2.6, 2.2), "brazowy_kon")
    for dx in (-2.1, 2.1):
        for dz in (-0.7, 0.7):
            s.blok(g, "Koń noga", (kx + dx, 2.2, kz + dz), (0.8, 2.6, 0.8), "brazowy_kon")
            s.blok(g, "Koń kopyto", (kx + dx, 1.0, kz + dz), (0.9, 0.5, 0.9), "czarny")
    s.blok(g, "Koń szyja", (kx + 3.0, 6.2, kz), (1.4, 3.0, 1.5), "brazowy_kon", rot=(0, 0, -28))
    s.blok(g, "Koń głowa", (kx + 4.4, 7.4, kz), (2.6, 1.5, 1.5), "brazowy_kon", rot=(0, 0, -12))
    s.blok(g, "Koń grzywa", (kx + 2.4, 6.6, kz), (0.5, 3.2, 0.7), "grzywa", rot=(0, 0, -28))
    s.blok(g, "Koń ogon", (kx - 3.1, 4.4, kz), (0.6, 2.6, 0.7), "grzywa", rot=(0, 0, -18))
    for dz in (-0.6, 0.6):
        s.blok(g, "Koń ucho", (kx + 3.9, 8.3, kz + dz), (0.4, 0.7, 0.4), "brazowy_kon")
    s.blok(g, "Siodło", (kx - 0.2, 6.05, kz), (2.2, 0.5, 2.4), "baner", "Fabric")
    plot(s, g, [(x - 9.0, z + 7.0), (x - 9.0, z + 16.0), (x + 9.0, z + 16.0), (x + 9.0, z + 7.0)])


def wylegarnia(s, rnd):
    g = "Wylegarnia"
    x, z = -33.0, -20.0
    for i in range(12):
        kat = math.tau * i / 12
        s.blok(g, "Gniazdo", (x + math.cos(kat) * 5.0, 1.7, z + math.sin(kat) * 5.0), (3.2, 1.9, 1.7), rnd.choice(["drewno", "drewno_j", "siano2"]),
               "Wood", (rnd.uniform(-10, 10), -math.degrees(kat) + 90, rnd.uniform(-8, 8)))
    s.walec_pion(g, "Gniazdo siano", x, 0.8, z, 4.6, 0.9, "siano", "Fabric")
    for (dx, dz, d, kol, kropki) in ((-1.6, 0.6, 3.6, "biel", "blekit"), (1.8, -0.9, 3.0, "blekit", "biel"), (0.6, 2.1, 2.6, "roz", "fiolet")):
        s.kula(g, "Jajo", (x + dx, 1.6 + d * 0.5, z + dz), d, kol)
        s.kula(g, "Jajo", (x + dx, 1.6 + d * 0.95, z + dz), d * 0.78, kol)
        for k in range(4):
            kat = math.tau * k / 4 + 0.5
            s.kula(g, "Jajo kropka", (x + dx + math.cos(kat) * d * 0.44, 1.6 + d * (0.5 + 0.18 * (k % 2)), z + dz + math.sin(kat) * d * 0.44),
                   d * 0.2, kropki)
    for dx, dz in ((-6.4, -4.4), (6.4, -4.4)):
        s.blok(g, "Wylęgarnia słup", (x + dx, 4.6, z + dz), (0.7, 7.6, 0.7), "drewno_c", "Wood")
    s.blok(g, "Wylęgarnia szyld", (x, 7.4, z - 4.4), (9.0, 2.2, 0.4), "deski", "WoodPlanks")
    s.kula(g, "Wylęgarnia szyld jajo", (x, 7.4, z - 4.0), 1.5, "biel")
    for dx in (-2.8, 2.8):
        s.blok(g, "Wylęgarnia szyld łapka", (x + dx, 7.4, z - 4.1), (1.0, 1.0, 0.2), "roz")


def arena(s, rnd):
    g = "Arena"
    x, z = -74.0, -6.0                                         # brama areny na zachodzie
    for dz in (-7.0, 7.0):
        s.blok(g, "Arena filar", (x, 8.3, z + dz), (6.0, 15.0, 6.0), "kamien", "Cobblestone")
        s.blok(g, "Arena głowica", (x, 16.4, z + dz), (7.2, 1.4, 7.2), "kamien3", "Cobblestone")
        s.ostroslup(g, "Arena zwieńczenie", x, 17.1, z + dz, 3.2, 4.0, "dach2", "Slate")
        s.blok(g, "Arena baner", (x + 3.2, 9.6, z + dz), (0.3, 8.0, 3.4), "baner", "Fabric")
        s.blok(g, "Arena baner znak", (x + 3.4, 10.4, z + dz), (0.2, 1.6, 1.6), "zloto", "Metal", (45, 0, 0))
    s.blok(g, "Arena nadproże", (x, 15.4, z), (5.0, 2.6, 9.0), "kamien2", "Cobblestone")
    for znak in (-1, 1):                                       # skrzyżowane miecze nad bramą
        s.blok(g, "Arena miecz ostrze", (x + 2.7, 18.6, z), (0.3, 7.6, 0.9), "zelazo_j", "Metal", (znak * 42, 0, 0))
        s.blok(g, "Arena miecz jelec", (x + 2.75, 16.5, z + znak * -1.9), (0.35, 0.5, 2.4), "zloto", "Metal", (znak * 42, 0, 0))
    for i in range(7):                                         # fragment muru areny za bramą
        kat = math.radians(118 + i * 21)
        mx, mz = x - 16 + math.cos(kat) * 18, z + math.sin(kat) * 18
        s.blok(g, "Arena mur", (mx, 5.0, mz), (5.0, 8.4, 7.4), rnd.choice(["kamien", "kamien2", "kamien3"]), "Cobblestone",
               (0, -math.degrees(kat), 0))
        s.blok(g, "Arena blanka", (mx, 9.9, mz), (5.2, 1.6, 3.0), "kamien3", "Cobblestone", (0, -math.degrees(kat), 0))
    s.walec_pion(g, "Arena piasek", x - 16, 0.8, z, 15.0, 0.2, "siano2", "Sand")
    for dz in (-3.4, 3.4):
        s.walec_pion(g, "Arena pochodnia", x + 4.6, 0.8, z + dz * 3.2, 0.4, 5.6, "drewno_c", "Wood")
        s.blok(g, "Arena ogień", (x + 4.6, 7.0, z + dz * 3.2), (1.0, 1.4, 1.0), "ogien", "Neon")


def portal_lochow(s, rnd):
    g = "PortalLochow"
    x, z = 74.0, -6.0                                          # portal na wschodzie, wlot od strony placu (−X)
    s.blok(g, "Portal podest", (x, 1.4, z), (12.0, 1.2, 16.0), "kamien2", "Cobblestone")
    for i in range(3):
        s.blok(g, "Portal stopień", (x - 6.6 - i * 1.3, 1.2 - i * 0.2, z), (1.4, 0.8 - i * 0.2, 12.0 - i), "kamien", "Cobblestone")
    n = 11
    for i in range(n):                                         # łuk z kamieni
        kat = math.radians(-8 + i * (196 / (n - 1)))
        px = z + math.cos(kat) * 6.2
        py = 2.4 + math.sin(kat) * 8.4 + 1.2
        s.blok(g, "Portal kamień", (x, py, px), (3.0, 3.0, 2.7), rnd.choice(["kamien", "kamien2", "kamien3"]), "Cobblestone",
               (math.degrees(kat) - 90, 0, 0))
    s.blok(g, "Portal tafla", (x, 6.2, z), (0.5, 9.4, 9.2), "portal", "Neon", alfa=0.3)
    s.walec_os(g, "Portal wir", (x - 0.2, 6.6, z), 3.2, 0.3, "portal2", "Neon", "x", 0.2)
    s.walec_os(g, "Portal wir", (x - 0.4, 6.6, z), 1.6, 0.3, "biel", "Neon", "x", 0.1)
    for i in range(6):                                         # runy
        kat = math.radians(20 + i * 28)
        s.blok(g, "Portal runa", (x - 1.6, 2.4 + math.sin(kat) * 8.4 + 1.2, z + math.cos(kat) * 6.2), (0.2, 0.8, 0.8), "portal2", "Neon",
               (rnd.uniform(0, 45), 0, 0))
    for dz in (-9.5, 9.5):
        s.blok(g, "Portal obelisk", (x - 3.0, 4.6, z + dz), (2.4, 7.6, 2.4), "kamien2", "Cobblestone", (0, 0, rnd.uniform(-5, 5)))
        s.ostroslup(g, "Portal obelisk szczyt", x - 3.0, 8.4, z + dz, 1.2, 2.2, "portal", "Neon")
    for dx, dz, a in ((-5.0, -12.5, 1.6), (-8.0, 11.5, 1.2), (2.0, 13.0, 2.0)):   # kryształy
        s.ostroslup(g, "Kryształ", x + dx, 0.8, z + dz, a, a * 3.4, "portal2", "Glass")
        s.ostroslup(g, "Kryształ", x + dx + a * 1.2, 0.8, z + dz + 0.6, a * 0.6, a * 2.0, "portal", "Glass")


def brama(s, rnd):
    g = "Brama"
    z = 84.0
    for znak in (-1, 1):
        s.walec_pion(g, "Brama słup", znak * 8.0, 0.8, z, 1.6, 17.0, "drewno_c", "Wood", (0, znak * -2))
        s.ostroslup(g, "Brama szpic", znak * 8.0 + znak * 0.3, 17.6, z, 1.9, 3.4, "drewno", "Wood")
        s.blok(g, "Brama pochodnia", (znak * 8.0, 9.0, z + 2.0), (0.5, 0.5, 2.0), "zelazo", "Metal")
        s.blok(g, "Brama ogień", (znak * 8.0, 10.0, z + 2.8), (1.1, 1.6, 1.1), "ogien", "Neon")
        s.blok(g, "Brama ogień", (znak * 8.0, 11.0, z + 2.8), (0.6, 0.9, 0.6), "ogien2", "Neon")
    s.blok(g, "Brama belka", (0, 15.2, z), (20.0, 1.6, 1.8), "drewno", "Wood")
    s.blok(g, "Brama belka", (0, 12.6, z), (18.0, 1.2, 1.4), "drewno_c", "Wood")
    s.blok(g, "Brama szyld", (0, 9.8, z + 0.3), (11.0, 3.6, 0.5), "deski", "WoodPlanks", (0, 0, 2))
    for dx in (-4.6, 4.6):
        s.blok(g, "Brama łańcuch", (dx, 11.8, z + 0.3), (0.2, 1.2, 0.2), "zelazo", "Metal")
    s.blok(g, "Brama herb", (0, 9.8, z + 0.65), (2.6, 2.6, 0.2), "zloto", "Metal", (0, 0, 45))
    s.blok(g, "Brama herb", (0, 9.8, z + 0.8), (1.4, 1.4, 0.2), "baner", "SmoothPlastic", (0, 0, 45))
    # palisada po obu stronach bramy
    for znak in (-1, 1):
        pts = []
        for i in range(8):
            kat = math.radians(90 - znak * (7 + i * 6.2))
            pts.append((math.cos(kat) * 84.5, math.sin(kat) * 84.5))
        for i, (px, pz) in enumerate(pts):
            h = 8.0 + (i % 3) * 0.9
            s.walec_pion(g, "Palisada pal", px, 0.8, pz, 1.25, h, rnd.choice(["drewno", "drewno_c"]), "Wood", (rnd.uniform(-2, 2), rnd.uniform(-2, 2)))
            s.ostroslup(g, "Palisada szpic", px, 0.8 + h, pz, 1.25, 2.2, "drewno_j", "Wood")
            if i:
                qx, qz = pts[i - 1]
                s.belka(g, "Palisada żerdź", (qx, 5.4, qz), (px, 5.4, pz), 0.6, "drewno_c", "Wood")


def ognisko(s, rnd):
    g = "Ognisko"
    x, z = -17.0, 24.0
    for i in range(9):
        kat = math.tau * i / 9
        s.blok(g, "Ognisko kamień", (x + math.cos(kat) * 2.6, 1.25, z + math.sin(kat) * 2.6), (1.5, 0.9, 1.1), rnd.choice(["kamien", "kamien2", "kamien3"]),
               "Slate", (0, -math.degrees(kat) + 90, rnd.uniform(-8, 8)))
    for kat_st in (20, 80, 140):
        kat = math.radians(kat_st)
        s.belka(g, "Ognisko polano", (x - math.cos(kat) * 1.8, 1.1, z - math.sin(kat) * 1.8), (x + math.cos(kat) * 1.8, 1.9, z + math.sin(kat) * 1.8),
                0.7, "drewno_c", "Wood")
    s.ostroslup(g, "Ogień", x, 1.2, z, 1.3, 3.4, "ogien", "Neon")
    s.ostroslup(g, "Ogień", x + 0.2, 1.4, z - 0.1, 0.8, 2.6, "ogien2", "Neon", obrot=45)
    for kat_st in (200, 320):
        kat = math.radians(kat_st)
        bx, bz = x + math.cos(kat) * 6.4, z + math.sin(kat) * 6.4
        s.walec_os(g, "Kłoda do siedzenia", (bx, 1.7, bz), 1.0, 6.0, "drewno", "Wood", "z" if abs(math.cos(kat)) > 0.7 else "x")
    s.blok(g, "Rożen słupek", (x - 3.2, 2.6, z + 0.2), (0.3, 3.6, 0.3), "drewno_c", "Wood")
    s.blok(g, "Rożen słupek", (x + 3.2, 2.6, z + 0.2), (0.3, 3.6, 0.3), "drewno_c", "Wood")
    s.blok(g, "Rożen", (x, 4.2, z + 0.2), (6.8, 0.2, 0.2), "zelazo", "Metal")
    s.blok(g, "Kociołek", (x, 3.4, z + 0.2), (1.6, 1.3, 1.6), "czarny", "Metal")


def staw(s, rnd):
    g = "Staw"
    x, z = 44.0, 52.0
    s.walec_pion(g, "Staw woda", x, 0.62, z, 13.0, 0.3, "woda", "SmoothPlastic", alfa=0.2)
    s.walec_pion(g, "Staw woda", x + 9.0, 0.62, z + 5.0, 8.0, 0.3, "woda", "SmoothPlastic", alfa=0.2)
    s.walec_pion(g, "Staw dno", x, 0.5, z, 13.6, 0.36, "ziemia2", "Ground")
    s.walec_pion(g, "Staw dno", x + 9.0, 0.5, z + 5.0, 8.6, 0.36, "ziemia2", "Ground")
    for i in range(14):
        kat = math.tau * i / 14 + rnd.uniform(-0.1, 0.1)
        s.blok(g, "Staw kamień", (x + math.cos(kat) * 13.4, 1.0, z + math.sin(kat) * 13.4), (rnd.uniform(1.6, 3.0), 0.9, rnd.uniform(1.4, 2.4)),
               rnd.choice(["kamien", "kamien3"]), "Slate", (0, rnd.uniform(0, 90), 0))
    for dx, dz in ((-4.0, 3.0), (3.0, -4.6), (10.0, 6.0)):
        s.walec_pion(g, "Lilia", x + dx, 0.9, z + dz, 1.3, 0.12, "lisc3", "Grass")
        s.blok(g, "Lilia kwiat", (x + dx + 0.3, 1.2, z + dz), (0.6, 0.4, 0.6), "roz")
    # pomost
    for i in range(6):
        s.blok(g, "Pomost deska", (x - 15.5 + i * 2.0, 1.5, z - 1.0), (1.8, 0.3, 4.6), "deski" if i % 2 else "deski2", "WoodPlanks")
    for dx in (-15.6, -9.6, -5.0):
        for dz in (-3.0, 1.0):
            s.walec_pion(g, "Pomost pal", x + dx, 0.2, z + dz, 0.4, 2.2, "drewno_c", "Wood")
    s.blok(g, "Wędka", (x - 5.2, 3.6, z - 1.6), (0.14, 5.0, 0.14), "drewno_j", "Wood", (0, 0, -38))
    for i in range(5):                                         # tatarak
        kat = rnd.uniform(0, math.tau)
        s.blok(g, "Tatarak", (x + math.cos(kat) * 12.4, 2.2, z + math.sin(kat) * 12.4), (0.3, 3.0, 0.3), "lisc2", "Grass",
               (rnd.uniform(-8, 8), 0, rnd.uniform(-8, 8)))


def latarnie(s):
    g = "Latarnie"
    for z in (34.0, 52.0, 70.0):
        latarnia(s, g, -6.4, z, 9.0, 1)
        latarnia(s, g, 6.4, z + 9.0, 9.0, -1)
    for x in (-34.0, -56.0, 34.0, 56.0):
        latarnia(s, g, x, -11.6 if x < 0 else -0.4, 9.0, 1 if x < 0 else -1)
    latarnia(s, g, -8.0, -29.0, 9.0, 1)
    latarnia(s, g, 8.0, -29.0, 9.0, -1)


# obszary, w których nie sadzimy lasu: (x, z, promień)
WOLNE = [(0, 0, 33), (0, -50, 34), (26, -48, 16), (36, 14, 13), (-42, 22, 20), (-33, -20, 11), (-80, -6, 26), (76, -6, 17), (-17, 24, 11),
         (48, 54, 21), (16, -27, 7), (-17, -27, 9)]


def _wolne(x, z, margines=0.0):
    for wx, wz, r in WOLNE:
        if (x - wx) ** 2 + (z - wz) ** 2 < (r + margines) ** 2:
            return False
    if abs(x) < 9.5 + margines and 22 < z < 120:              # droga do bramy i przedpole za bramą
        return False
    if abs(x) < 7.5 + margines and -40 < z < -20:              # droga do karczmy
        return False
    if abs(z + 6) < 7.5 + margines and 22 < abs(x) < 72:       # drogi wschód–zachód
        return False
    return True


def las(s, rnd):
    g = "Las"
    posadzone = []

    def miejsce(rmin, rmax, odstep, proby=60):
        for _ in range(proby):
            kat, odl = rnd.uniform(0, math.tau), rnd.uniform(rmin, rmax)
            x, z = math.cos(kat) * odl, math.sin(kat) * odl
            if abs(x) > 108 or abs(z) > 108 or not _wolne(x, z, 2.0):
                continue
            if all((x - px) ** 2 + (z - pz) ** 2 > odstep ** 2 for px, pz in posadzone):
                posadzone.append((x, z))
                return x, z
        return None

    for _ in range(58):                                        # gęsty pierścień zewnętrzny — naturalna granica świata
        m = miejsce(86, 112, 8.5)
        if m:
            (sosna if rnd.random() < 0.7 else drzewo)(s, g, m[0], m[1], rnd, rnd.uniform(1.15, 1.55))
    for _ in range(34):                                        # rzadszy las bliżej środka
        m = miejsce(30, 86, 11.5)
        if m:
            if rnd.random() < 0.55:
                sosna(s, g, m[0], m[1], rnd, rnd.uniform(0.9, 1.25))
            else:
                drzewo(s, g, m[0], m[1], rnd, rnd.uniform(0.85, 1.15), jesien=rnd.random() < 0.18)
    g2 = "Runo"
    for _ in range(40):
        m = miejsce(24, 104, 5.0)
        if m:
            krzak(s, g2, m[0], m[1], rnd, rnd.uniform(0.8, 1.3))
    for _ in range(24):
        m = miejsce(24, 104, 5.0)
        if m:
            glaz(s, g2, m[0], m[1], rnd, rnd.uniform(0.7, 1.4))
    for _ in range(26):
        m = miejsce(22, 100, 3.5)
        if m:
            grzyb(s, g2, m[0], m[1], rnd, rnd.uniform(0.8, 1.8))
            if rnd.random() < 0.5:
                grzyb(s, g2, m[0] + rnd.uniform(-1.6, 1.6), m[1] + rnd.uniform(-1.6, 1.6), rnd, rnd.uniform(0.6, 1.0))
    for _ in range(44):
        m = miejsce(20, 100, 3.0)
        if m:
            kwiaty(s, g2, m[0], m[1], rnd)
    for _ in range(8):                                         # pieńki
        m = miejsce(26, 80, 6.0)
        if m:
            s.walec_pion(g2, "Pieniek", m[0], 0.8, m[1], rnd.uniform(1.2, 1.8), rnd.uniform(1.0, 1.8), "drewno", "Wood")


def zbuduj(ziarno=20261112):
    rnd = random.Random(ziarno)
    s = Scena()
    teren(s, rnd)
    plac(s, rnd)
    karczma(s, rnd)
    tablica_zlecen(s, rnd)
    kolo_fortuny(s, rnd)
    sklep(s, rnd)
    stajnia(s, rnd)
    wylegarnia(s, rnd)
    arena(s, rnd)
    portal_lochow(s, rnd)
    brama(s, rnd)
    ognisko(s, rnd)
    staw(s, rnd)
    latarnie(s)
    las(s, rnd)
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wyj", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "czesci.json"))
    ap.add_argument("--ziarno", type=int, default=20261112)
    a = ap.parse_args()
    s = zbuduj(a.ziarno)
    with open(a.wyj, "w", encoding="utf-8", newline="\n") as f:
        json.dump(s.json(), f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    grupy = {}
    for c in s.czesci:
        grupy[s.grupy[c[1]]] = grupy.get(s.grupy[c[1]], 0) + 1
    print("czesci: %d, grup: %d -> %s" % (len(s.czesci), len(s.grupy), a.wyj))
    for nazwa, n in sorted(grupy.items(), key=lambda kv: -kv[1]):
        print("  %5d  %s" % (n, nazwa))


if __name__ == "__main__":
    main()
