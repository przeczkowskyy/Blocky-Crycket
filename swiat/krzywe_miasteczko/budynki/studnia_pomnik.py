# -*- coding: utf-8 -*-
"""Studnia-pomnik Pierwszego Klocka (`studnia_pomnik`, grupa StudniaPomnik) — środek rynku, karta PROJEKT.md 5.11.

Miasto zaczęło się od jednego klocka, który do dziś stoi krzywo: złoty klocek-olbrzym balansuje na jednym rogu na
szczycie krzywej kolumny wyrastającej z wody studni, a przed przewróceniem chroni go jeden cieniutki patyk.
Od frontu (+Z) krzywy kołowrót z wiadrem — studnia działa (codzienna nagroda, punkt interakcji (0; 13)).

Status: propozycja (noc 13.11.2026), nie kanon.
Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/studnia_pomnik.py --wyj <folder>
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import macierz_obrotu, razy_wektor  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "StudniaPomnik"
OBRYS = (18, 18)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 22
BUDZET = 150                     # karta; twardy sufit 188
INTERAKCJA = (0.0, 13.0)         # przed kołowrotem, 4 study przed krawędzią działki
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

KAMIEN = "kamien_cieply"
R_CEMB = 7.0                     # promień okręgu cembrowiny (środki kamieni)
Y_RANT = 0.7                     # wierzch rantu tusz pod kamieniami
Y_WODY = 2.1                     # wierzch tafli (≈ 1,1 poniżej rantu kamieni, jak w karcie 1,6 przy kamieniach od ziemi)
SLUPY_KAT = (8.0, -11.0, 7.0)    # bezwzględne przechyły segmentów kolumny (rz, °)
SLUPY_R = (1.5, 1.35, 1.2)       # Ø 3 → 2,7 → 2,4
SLUPY_DL = (3.9, 3.7, 2.8)       # długości segmentów (wierzch kapitelu ≈ 14)
Y_KAMIENI = Y_RANT - 0.25       # spód kamieni (wpuszczone w rant, żeby przechylone nie odstawały)
# (rx, rz) każdego kamienia: ręcznie układane, 0° albo ≥ 4° (przykazanie 1); poziome pod słupami kołowrotu (i = 1, 10)
# i pod leżącym klockiem (i = 2)
KAMIENIE_PRZECHYL = [(0, 5), (0, 0), (0, 0), (-4, -6), (0, 4), (0, 0), (4, -5), (0, 6), (0, 0), (-5, -4), (0, 0), (4, 5)]
KLOCEK_ROT = (15.0, 12.0, -25.0)  # przód 15° (wypustki ku frontowi), skręt 12°, w bok 25° (lewy koniec w górze)


def _kamienie(s):
    """Cembrowina: 12 kamieni 3,6 × 2,6 × 1,6 na okręgu r = 7, co drugi wyższy i grubszy o 0,25 i w cieniu."""
    n = 12
    for i in range(n):
        k = 15.0 + 360.0 * i / n                           # styk kamieni w osi frontu (z = +7), kamienie po bokach
        d = 0.25 if i % 2 else 0.0
        h = 2.6 + d
        a = math.radians(k)
        kol = cien(s, KAMIEN) if i % 2 else KAMIEN
        rx, rz = KAMIENIE_PRZECHYL[i]
        s.blok("Cembrowina kamień", (R_CEMB * math.sin(a), Y_KAMIENI + h / 2.0, R_CEMB * math.cos(a)),
               (3.6, h, 1.6 + d), kol, rot=(rx, k, rz))


def _kolumna(s):
    """Krzywa kolumna z trzech walców (przechyły +8°, −11°, +7°) z gzymsami tusz; zwraca środek wierzchu kapitelu
    i kąt ostatniego segmentu. Wszystko w płaszczyźnie XY (zgięcia wokół Z)."""
    x, y = 0.3, Y_WODY - 0.1
    s.walec("Kolumna stopa", (x, y + 0.25, 0), 2.0, 0.5, "tusz", os="y")          # obrys na linii wody
    with s.cechy(kolizja=False, cien=False):
        s.walec("Woda fala", (x - 0.15, y + 0.18, 0.1), 2.45, 0.2, "biel", os="y")  # biały pierścień fali wokół stopy
    x, y = x, y + 0.5
    kat = 0.0
    gzymsy = []
    for i, (k, r, dl) in enumerate(zip(SLUPY_KAT, SLUPY_R, SLUPY_DL)):
        kat = k
        a = math.radians(k)
        dx, dy = -math.sin(a), math.cos(a)
        zak = 0.6                                                                  # wpuszczony w gzyms poniżej
        cx, cy = x + dx * (dl - zak) / 2.0, y + dy * (dl - zak) / 2.0
        s.walec("Kolumna segment", (cx, cy, 0), r, dl + zak, KAMIEN if i != 1 else cien(s, KAMIEN, 0.9), os="y",
                rot=(0, 0, k))
        if i == len(SLUPY_KAT) - 1:                                                # pęknięcie pod ciężarem klocka
            with s.uklad(pos=(cx, cy, 0), obrot=(0, 0, k)), s.cechy(kolizja=False, cien=False):
                for px, py, pk in ((0.25, 0.95, 32), (-0.05, 0.25, -38), (0.2, -0.45, 30)):
                    s.blok("Kolumna pęknięcie", (px, py, r - 0.08), (0.3, 0.95, 0.3), "tusz", rot=(0, 0, pk))
        x, y = x + dx * dl, y + dy * dl
        if i < len(SLUPY_KAT) - 1:
            s.walec("Kolumna gzyms", (x, y, 0), r + 0.4, 0.5, "tusz", os="y", rot=(0, 0, k))
            gzymsy.append((x, y, k, r + 0.4))
    # kapitel: gzyms tusz + płyta kamienna, oba w przechyle ostatniego segmentu
    a = math.radians(kat)
    dx, dy = -math.sin(a), math.cos(a)
    with s.uklad(pos=(x, y, 0), obrot=(0, 0, kat)):
        s.blok("Kapitel gzyms", (0, 0.1, 0), (3.4, 0.5, 3.4), "tusz")
        s.blok("Kapitel", (0, 0.75, 0), (3.0, 0.9, 3.0), KAMIEN)
    return (x + dx * 1.2, y + dy * 1.2, 0.0), gzymsy


def _klocek(s, kontakt):
    """Klocek-olbrzym 8 × 4 × 4 `zloto` z 8 wypustkami i obrysem krawędzi tusz, stojący na jednym rogu (najniższy
    wierzchołek wpuszczony 0,4 w kapitel). Zwraca funkcję lokalne→budynek, żeby podeprzeć go patykiem."""
    R = macierz_obrotu(*KLOCEK_ROT)
    rogi = [(sx * 4.0, sy * 2.0, sz * 2.0) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    najnizszy = min(rogi, key=lambda v: razy_wektor(R, v)[1])
    w = razy_wektor(R, najnizszy)
    srodek = (kontakt[0] - w[0], kontakt[1] - 0.4 - w[1], kontakt[2] - w[2])

    def do_budynku(v):
        p = razy_wektor(R, v)
        return (srodek[0] + p[0], srodek[1] + p[1], srodek[2] + p[2])

    with s.uklad(pos=srodek, obrot=KLOCEK_ROT):
        s.blok("Pierwszy Klocek", (0, 0, 0), (8.0, 4.0, 4.0), "zloto")
        with s.cechy(kolizja=False):
            g, e = 0.5, 0.3                                                      # obrys krawędzi: grubość, zapas na końcach
            for y in (-2.0, 2.0):
                for z in (-2.0, 2.0):
                    s.blok("Klocek obrys", (0, y, z), (8.0 + e, g, g), "tusz")
            for x in (-4.0, 4.0):
                for z in (-2.0, 2.0):
                    s.blok("Klocek obrys", (x, 0, z), (g, 4.0 + e, g), "tusz")
                for y in (-2.0, 2.0):
                    s.blok("Klocek obrys", (x, y, 0), (g, g, 4.0 + e), "tusz")
            for x in (-3.0, -1.0, 1.0, 3.0):
                for z in (-1.0, 1.0):
                    s.walec("Klocek wypustka", (x, 2.35, z), 0.8, 0.8, "zloto", os="y")
    return do_budynku


def _kolowrot(s):
    """Krzywy kołowrót od frontu: słupy ±4° różnej wysokości, wałek pod 5°, nawinięta lina, wiadro z obręczą, korba."""
    yk = Y_KAMIENI + 2.85 - 0.15                                              # wierzch kamieni (te pod słupami są wyższe)
    zs = 5.0
    with s.cechy():
        with s.uklad(pos=(-4.1, yk, zs), obrot=(0, 0, -4)):
            s.blok("Kołowrót słup", (0, 3.0, 0), (0.9, 6.0, 0.9), "drewno_ciemne", "Wood")
            s.blok("Kołowrót czapka", (0, 6.1, 0), (1.3, 0.4, 1.3), "drewno_jasne")
            zestaw.choragiewka_duetu(s, (0, 6.2, 0), "kot", ry=180, przechyl=-12)
        with s.uklad(pos=(4.1, yk, zs), obrot=(0, 0, 4)):
            s.blok("Kołowrót słup", (0, 3.4, 0), (0.9, 6.8, 0.9), "drewno_ciemne", "Wood")
            s.blok("Kołowrót czapka", (0, 6.9, 0), (1.3, 0.4, 1.3), "drewno_jasne")
            zestaw.choragiewka_duetu(s, (0, 7.0, 0), "rycerz", przechyl=-12)
    # wałek między słupami: lewy koniec na ~8,7, prawy na ~9,4 → 5°
    yl, yp = yk + 5.4, yk + 6.1
    kat = math.degrees(math.atan2(yp - yl, 8.4))
    with s.uklad(pos=(0, (yl + yp) / 2.0, zs), obrot=(0, 0, kat)), s.cechy(kolizja=False):
        s.walec("Kołowrót wałek", (0, 0, 0), 0.4, 9.6, "drewno", "Wood", os="x")
        s.walec("Kołowrót lina zwój", (-0.8, 0, 0), 0.65, 1.6, "drewno_jasne", os="x")
        # korba na prawym końcu, na zewnątrz słupa
        s.blok("Korba ramię", (5.0, -0.9, 0), (0.4, 2.2, 0.4), "metal_ciemny")
        s.blok("Korba rączka", (5.5, -1.8, 0), (1.4, 0.45, 0.45), "drewno_jasne")
    # lina i wiadro (wisi nad wodą, 1 studa za rantem)
    with s.cechy(kolizja=False):
        xl = -0.8
        yw = (yl + yp) / 2.0 + math.tan(math.radians(kat)) * xl
        yb = yk + 0.9
        s.blok("Kołowrót lina", (xl, (yw + yb + 1.2) / 2.0, zs), (0.3, yw - yb - 1.2, 0.3), "drewno_jasne")
        with s.uklad(pos=(xl, yb, zs), obrot=(6, 0, -5)):
            s.walec("Wiadro", (0, 0, 0), 0.95, 1.7, "drewno", "WoodPlanks", os="y")
            s.walec("Wiadro obręcz", (0, 0.35, 0), 1.08, 0.35, "metal_ciemny", os="y")
            s.blok("Wiadro pałąk", (0, 1.15, 0), (2.0, 0.3, 0.3), "tusz")


def buduj(s, rnd):
    # --- podstawa: gruby rant tusz (ciemny walor przy jasnym bruku) i cembrowina
    s.walec("Cembrowina rant", (0.2, Y_RANT / 2.0, 0.1), 8.25, Y_RANT, "tusz", os="y")
    _kamienie(s)
    # --- woda warstwami: toń (pas przy kamieniach) → tafla → bliki
    s.walec("Woda toń", (0, (0.5 + Y_WODY - 0.1) / 2.0, 0), 6.6, Y_WODY - 0.1 - 0.5, "woda_gleboka", os="y")
    with s.cechy(kolizja=False):
        s.walec("Woda tafla", (-0.3, Y_WODY - 0.1, 0.3), 5.3, 0.2, "woda", os="y")
        with s.cechy(cien=False):
            for x, z, k in ((-3.0, 1.9, 30), (2.6, 2.6, -20), (-1.6, -3.2, 65)):
                s.blok("Woda blik", (x, Y_WODY + 0.08, z), (0.5, 0.25, 2.4), "biel", rot=(0, k, 0))
    # --- kolumna i pomnik
    kontakt, gzymsy = _kolumna(s)
    klocek = _klocek(s, kontakt)
    # --- żart: cały klocek trzyma jeden cieniutki patyk postawiony na półce górnego gzymsu kolumny
    gx, gy, gk, gr = gzymsy[-1]
    a = math.radians(gk)
    dol = (gx - math.cos(a) * (gr - 0.3), gy - math.sin(a) * (gr - 0.3) + 0.2, 0.3)   # na wierzchu gzymsu, lewa półka
    gora = klocek((-2.9, -2.0, 0.3))
    with s.cechy(kolizja=False):
        s.belka("Patyk podpórka", dol, gora, 0.4, "drewno", "Wood")
    # --- funkcja studni od frontu
    _kolowrot(s)
    # --- echo: mały złoty klocek, który odpadł i leży na cembrowinie (prawy-przedni kamień)
    a = math.radians(75.0)
    with s.uklad(pos=(R_CEMB * math.sin(a), Y_KAMIENI + 2.6, R_CEMB * math.cos(a)), obrot=(0, 75 + 22, -8)), \
            s.cechy(kolizja=False):
        s.blok("Klocek echo", (0, 0.5, 0), (2.0, 1.0, 2.0), "zloto")
        for x in (-0.5, 0.5):
            for z in (-0.5, 0.5):
                s.walec("Echo wypustka", (x, 1.15, z), 0.38, 0.3, "zloto", os="y")
    # --- trzeci, najmniejszy klocek (trójka duży–średni–mały) wpadł do wody i sterczy z niej rogiem
    with s.uklad(pos=(-3.4, Y_WODY - 0.2, -1.6), obrot=(-20, 35, 28)), s.cechy(kolizja=False):
        s.blok("Klocek w wodzie", (0, 0.4, 0), (2.0, 1.0, 1.0), "zloto")
        s.walec("Klocek w wodzie wypustka", (0.5, 1.05, 0), 0.38, 0.3, "zloto", os="y")
    # --- znaki miasteczka z tyłu i z boku: dwie łaty z fastrygą na poziomych kamieniach (różne kolory i przechyły)
    for kat, kol, prz in ((165.0, "pomarancz", 8), (255.0, "dach_twierdza", -6)):
        a = math.radians(kat)
        r = R_CEMB + (1.85 if int((kat - 15) / 30) % 2 else 1.6) / 2.0 + 0.02
        zestaw.lata(s, (r * math.sin(a), Y_KAMIENI + 1.55, r * math.cos(a)), 2.4, 1.8, kol, ry=kat, przechyl=prz)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()
