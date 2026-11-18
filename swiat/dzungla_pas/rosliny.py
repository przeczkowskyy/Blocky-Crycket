# -*- coding: utf-8 -*-
"""Rodziny roślin Dżungli z klocków (nowe; rodziny lasu bierzemy z swiat/biom_las/rosliny.py bez zmian).

Te same przykazania co w lesie i Bagnie: zero prostych pni (segmenty w kontrze), korona jak czapa (spód ciemny, wierzch
jasny), tuszowy pierścień u stopy, kolizję mają tylko pnie. Różnica Dżungli to piętra zieleni: drzewo-olbrzym
z korzeniami-skrzydłami i koroną-parasolem, figowiec z korzeniami powietrznymi, palma z kokosami, paproć drzewiasta,
olbrzymie liście-parasole na łodygach, kępy bambusa, krzewy z kwiatami i owocami, świecące kwiaty i liany.

Każda funkcja buduje w BIEŻĄCYM układzie wywołującego: pos = podstawa na ziemi, ry = obrót wokół pionu, k = skala.
Zwraca (wysokość, promień na ziemi/korony). Liczba części przy funkcji. Kolory to klucze palety Dżungli
(swiat/dzungla_pas/kontekst.KOLORY_DZUNGLI, prefiks dz_) — kto pożycza rośliny (np. arena walki), dokłada ten słownik
do swojej palety.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny as rosliny_lasu  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402

odcien = rosliny_lasu.odcien


def _kontra(rnd, a, b):
    return rnd.choice((-1, 1)) * rnd.uniform(a, b)


# =========================================================================== liście i liany
def lisc_parasol(s, rnd, pos, k=1.0, ry=0.0, f=1.0, wychyl=0.0, wys=None, prosty=False):
    """Olbrzymi liść-parasol na łodydze: łodyga z 2 segmentów w kontrze, wychylona o `wychyl`° ku lokalnemu +X (po
    obrocie ry), na szczycie płaski liść 6,4·k × 4,6·k z ciemną żyłką i opadającym czubkiem. Bez kolizji. Wys. ok. 7·k
    (albo `wys`). 5 części (prosty: łodyga z 1 belki, liść bez żyłki i czubka — 2 części)."""
    x, y, z = pos
    h = float(wys) if wys else 7.0 * k
    zn = rnd.choice((-1, 1))
    kol = odcien(s, rnd.choice(("dz_lisc", "dz_lisc", "dz_lisc_jasny")), f)
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.cechy(kolizja=False):
        if prosty:
            a = math.radians(wychyl)
            xe, ye = h * math.sin(a), h * math.cos(a)
            s.belka("Liść łodyga", (0.0, -0.2, 0.0), (xe, ye, 0.0), 0.32 * k + 0.1, "dz_lisc_ciemny", "SmoothPlastic")
        else:
            a1 = -wychyl * 0.5 + zn * rnd.uniform(2, 5)
            a2 = -wychyl * 0.5 - zn * rnd.uniform(2, 5)
            xe, ye, _ = lamana(s, "Liść łodyga", [(h * 0.55, 0.36 * k + 0.1, a1), (h * 0.48, 0.28 * k + 0.08, a2)],
                               "dz_lisc_ciemny", "SmoothPlastic", start=(0.0, -0.2))
        off = 1.0 * k + (1.0 * k if wychyl > 0 else 0.0)
        with s.uklad(pos=(xe, ye, 0), obrot=(rnd.uniform(-5, 5), rnd.uniform(-25, 25), -5.0 - 0.2 * wychyl)):
            s.blok("Liść olbrzym", (off, 0.15, 0), (6.4 * k, 0.3, 4.6 * k), kol)
            if not prosty:
                with s.cechy(cien=False):
                    s.blok("Liść żyłka", (off, 0.32, 0), (6.0 * k, 0.06, 0.35 * k), "dz_lisc_ciemny")
                s.blok("Liść olbrzym", (off + 3.9 * k, -0.45 * k, 0), (2.0 * k, 0.28, 3.4 * k), kol, rot=(0, 0, -32))
    return ye + 0.4, 4.0 * k


def kepa_parasoli(s, rnd, pos, k=1.0, ry=0.0, f=1.0, n=3):
    """Kępa olbrzymich liści-parasoli: n prostych liści (łodyga + liść) rozchylonych na boki, różnej wysokości, i liść u
    nasady (klin). Bez kolizji. 2·n + 1 części (n = 3: 7)."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.cechy(kolizja=False):
        hmax = 0.0
        for i in range(n):
            a = 360.0 / n * i + rnd.uniform(-25, 25)
            h, _ = lisc_parasol(s, rnd, (0.4 * math.cos(math.radians(a)), 0.0, 0.4 * math.sin(math.radians(a))),
                                k * rnd.uniform(0.75, 1.05), -a, f, wychyl=rnd.uniform(18, 34), wys=rnd.uniform(4.5, 8.0) * k,
                                prosty=True)
            hmax = max(hmax, h)
        s.klin("Liść u nasady", (0, 0.5 * k, 0), (2.6 * k, 1.0 * k, 2.0 * k), "dz_lisc_ciemny", rot=(0, rnd.uniform(0, 360), 0))
    return hmax, 5.5 * k


def liana(s, rnd, p1, p2, zwis=1.5, grub=0.35, liscie=2, kolor="dz_liana"):
    """Liana zwisająca łukiem między punktami p1 i p2 (dwie belki do najniższego punktu w połowie, niżej o `zwis`) i
    `liscie` liści na niej. Bez kolizji i cienia. 2 + liscie części."""
    m = ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0 - zwis, (p1[2] + p2[2]) / 2.0)
    with s.cechy(kolizja=False, cien=False):
        s.belka("Liana", p1, m, grub, kolor, "SmoothPlastic")
        s.belka("Liana", m, p2, grub, kolor, "SmoothPlastic")
        for i in range(liscie):
            t = (i + 1.0) / (liscie + 1.0)
            a, b = (p1, m) if t < 0.5 else (m, p2)
            tt = t * 2 if t < 0.5 else (t - 0.5) * 2
            q = tuple(a[j] + (b[j] - a[j]) * tt for j in range(3))
            s.blok("Liana liść", (q[0], q[1] - 0.35, q[2]), (1.1, 0.22, 0.75), rnd.choice(("dz_lisc", "dz_lisc_jasny")),
                   rot=(rnd.uniform(-25, 25), rnd.uniform(0, 180), rnd.uniform(15, 35)))
    return 2 + liscie


def liana_zwis(s, rnd, pos, h, grub=0.3, liscie=1, kolor="dz_liana"):
    """Liana zwisająca z punktu pos w dół o h (dwa odcinki z lekkim załamaniem) z liściem. Bez kolizji i cienia.
    2 + liscie części."""
    x, y, z = pos
    a = rnd.uniform(0, 2 * math.pi)
    p_mid = (x + 0.5 * math.cos(a), y - h * 0.55, z + 0.5 * math.sin(a))
    p_end = (x + 0.2 * math.cos(a + 1.2), y - h, z + 0.2 * math.sin(a + 1.2))
    with s.cechy(kolizja=False, cien=False):
        s.belka("Liana", (x, y, z), p_mid, grub, kolor, "SmoothPlastic")
        s.belka("Liana", p_mid, p_end, grub * 0.85, kolor, "SmoothPlastic")
        for i in range(liscie):
            t = rnd.uniform(0.3, 0.9)
            s.blok("Liana liść", (x + (p_end[0] - x) * t, y - h * t, z + (p_end[2] - z) * t), (1.0, 0.2, 0.7),
                   rnd.choice(("dz_lisc", "dz_lisc_jasny")), rot=(rnd.uniform(-20, 20), rnd.uniform(0, 180), rnd.uniform(20, 40)))
    return 2 + liscie


# =========================================================================== drzewa
def drzewo_dzungli(s, rnd, pos, k=1.0, ry=0.0, f=1.0, liana_=True, korzenie=3, tusz=True):
    """Drzewo-olbrzym dżungli: trzy korzenie-skrzydła u stopy (kliny), wysoki pień z 2 segmentów w kontrze, korona-parasol
    z 2 płaskich czap (ciemny spód, jasny wierzch) i niższa boczna czapa, opadająca liana z liściem. Kolizję ma tylko
    pień. Wys. ok. 26·k. 12 części (bez liany 9; korzenie = liczba skrzydeł, tusz = pierścień u stopy)."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    kor = (odcien(s, "dz_korona_spod", f), odcien(s, "dz_korona", f), odcien(s, "dz_korona_jasna", f))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=False):
            for i in range(korzenie):
                with s.uklad(obrot=(0, 360.0 / max(1, korzenie) * i + rnd.uniform(-20, 20), 0)):
                    s.klin("Korzeń skrzydło", (0, 1.3 * k, 1.5 * k), (0.55 * k, 2.6 * k, 2.4 * k), "dz_pien", "Wood", rot=(0, 180, 0))
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Pień", [(12.0 * k, 1.8 * k, zn * rnd.uniform(3, 6)), (10.5 * k, 1.4 * k, -zn * rnd.uniform(5, 9))],
                               "dz_pien", "Wood", start=(0.0, -0.4))
        if tusz:
            with s.cechy(kolizja=False, cien=False):
                s.blok("Pień tusz", (0, 0.1, 0), (2.6 * k, 0.3, 2.6 * k), "tusz")
        with s.cechy(kolizja=False):
            with s.uklad(pos=(xe, ye, 0), obrot=(rnd.uniform(-3, 3), rnd.uniform(0, 90), -zn * rnd.uniform(2, 5))):
                s.blok("Korona spód", (0, 0.4 * k, 0), (16.0 * k, 1.8 * k, 14.0 * k), kor[0])
                s.blok("Korona wierzch", (0.6 * zn * k, 1.9 * k, 0.4 * k), (10.5 * k, 1.5 * k, 9.5 * k), kor[2], rot=(0, 30, 0))
                s.blok("Korona boczna", (-zn * 6.0 * k, -4.2 * k, 2.0 * k), (8.0 * k, 1.4 * k, 7.0 * k), kor[1], rot=(0, 15, zn * 6))
            if liana_:
                liana_zwis(s, rnd, (xe + zn * 5.0 * k, ye - 0.6 * k, 2.5 * k), ye * 0.55, 0.38 * k)
    return ye + 2.5 * k, 8.0 * k


def figowiec(s, rnd, pos, k=1.0, ry=0.0, f=1.0, owoce=True):
    """Figowiec dusiciel: krótki gruby pień z 2 segmentów, wokół niego 4 ukośne korzenie powietrzne (belki od korony do
    ziemi), szeroka korona z 3 czap i dwa pomarańczowe owoce. Kolizję ma tylko pień. Wys. ok. 19·k. 13 części (bez owoców 11)."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    kor = (odcien(s, "dz_korona_spod", f * 0.95), odcien(s, "dz_korona", f), odcien(s, "dz_korona_jasna", f))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Pień", [(7.0 * k, 2.6 * k, zn * rnd.uniform(4, 8)), (6.0 * k, 2.0 * k, -zn * rnd.uniform(6, 10))],
                               "dz_pien_jasny", "Wood", start=(0.0, -0.4))
        with s.cechy(kolizja=False):
            for i in range(4):
                a = math.radians(90 * i + 45 + rnd.uniform(-15, 15))
                s.belka("Korzeń", (xe * 0.6 + 1.2 * k * math.cos(a), ye * 0.85, 1.2 * k * math.sin(a)),
                        (3.6 * k * math.cos(a), -0.2, 3.6 * k * math.sin(a)), 0.5 * k, "dz_pien", "Wood")
            with s.cechy(cien=False):
                s.blok("Pień tusz", (0, 0.1, 0), (3.4 * k, 0.3, 3.4 * k), "tusz")
            with s.uklad(pos=(xe, ye, 0), obrot=(rnd.uniform(-4, 4), rnd.uniform(0, 90), -zn * rnd.uniform(3, 6))):
                s.blok("Korona spód", (0, 1.0 * k, 0), (15.0 * k, 3.0 * k, 13.0 * k), kor[0])
                s.blok("Korona", (0.8 * zn * k, 3.4 * k, 0.5 * k), (11.0 * k, 2.6 * k, 10.0 * k), kor[1], rot=(0, 25, 0))
                s.blok("Korona wierzch", (-0.6 * zn * k, 5.4 * k, -0.4 * k), (6.4 * k, 1.8 * k, 6.0 * k), kor[2], rot=(0, 50, 0))
                for q in ((-1, 1) if owoce else ()):
                    s.blok("Owoc", (q * 4.2 * k, -0.7 * k, 2.4 * k), (0.9, 0.9, 0.9), "dz_owoc", rot=(30, 30, 0))
    return ye + 6.3 * k, 7.5 * k


def palma(s, rnd, pos, k=1.0, ry=0.0, f=1.0, liscie=5, kokosy=2, proste=False):
    """Palma: pień z 3 segmentów wygięty łukiem (w jedną stronę, jak palma nad wodą) w dwóch odcieniach, korona z
    `liscie` liści (każdy: wznoszący się trzonek i opadająca końcówka), `kokosy` kokosów pod koroną. Kolizję ma tylko
    pień. Wys. ok. 16·k. 4 + 2·liscie + kokosy części (domyślnie 16; proste: liść z jednego opadającego bloku, bez
    tuszu — 3 + liscie + kokosy)."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, kat = lamana(s, "Palma pień", [(6.0 * k, 1.2 * k, zn * rnd.uniform(3, 6)), (5.5 * k, 1.05 * k, zn * rnd.uniform(5, 8)),
                                                   (4.5 * k, 0.9 * k, zn * rnd.uniform(4, 7))],
                                 ("dz_palma", "dz_palma_jasna"), "Wood", start=(0.0, -0.3))
        if not proste:
            with s.cechy(kolizja=False, cien=False):
                s.blok("Pień tusz", (0, 0.1, 0), (2.0 * k, 0.3, 2.0 * k), "tusz")
        with s.cechy(kolizja=False):
            with s.uklad(pos=(xe, ye, 0)):
                for i in range(liscie):
                    a = 360.0 / liscie * i + rnd.uniform(-12, 12)
                    kol = odcien(s, "dz_lisc" if i % 2 else "dz_lisc_jasny", f)
                    with s.uklad(obrot=(0, a, 0)):
                        if proste:
                            s.blok("Palma liść", (3.6 * k, -0.3 * k, 0), (7.4 * k, 0.25, 1.5 * k), kol, rot=(0, 0, -16))
                            continue
                        s.blok("Palma liść", (2.2 * k, 0.55 * k, 0), (4.6 * k, 0.25, 1.5 * k), kol, rot=(0, 0, 14))
                        s.blok("Palma liść", (5.8 * k, 0.15 * k, 0), (3.4 * k, 0.22, 1.2 * k), odcien(s, "dz_lisc_ciemny", f),
                               rot=(0, 0, -28))
                for i in range(kokosy):
                    a = math.radians(140 * i + rnd.uniform(0, 60))
                    s.kula("Kokos", (0.75 * k * math.cos(a), -0.7 * k, 0.75 * k * math.sin(a)), 1.0 * k, "dz_kokos")
    return ye + 1.2 * k, 7.0 * k


def paproc_drzewiasta(s, rnd, pos, k=1.0, ry=0.0, f=1.0):
    """Paproć drzewiasta: cienki włóknisty pień z 2 segmentów w kontrze i rozeta 6 łukowatych liści-piór (każde to blok
    wznoszący się ku środkowi i opadający na zewnątrz). Kolizję ma tylko pień. Wys. ok. 9·k. 8 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            xe, ye, _ = lamana(s, "Pień", [(4.4 * k, 0.9 * k, zn * rnd.uniform(4, 8)), (3.8 * k, 0.75 * k, -zn * rnd.uniform(6, 10))],
                               "dz_pien", "Wood", start=(0.0, -0.3))
        with s.cechy(kolizja=False):
            with s.uklad(pos=(xe, ye, 0)):
                for i in range(6):
                    a = 60 * i + rnd.uniform(-10, 10)
                    kol = odcien(s, "dz_lisc" if i % 2 else "dz_korona", f)
                    with s.uklad(obrot=(0, a, 0)):
                        s.blok("Paproć", (2.6 * k, -0.1 * k, 0), (5.4 * k, 0.25, 1.3 * k), kol, rot=(0, 0, -12 - rnd.uniform(0, 10)))
    return ye + 0.6 * k, 5.4 * k


def bambus(s, rnd, pos, wys=6.0, n=5, ry=0.0, szer=2.6):
    """Kępa bambusa: n prostych łodyg (walce) lekko rozchylonych, na każdej jasne kolanko, dwie kiście liści-pasków u
    góry. Bez kolizji. 2·n + 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.cechy(kolizja=False):
        for i in range(n):
            a = 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
            r = szer * rnd.uniform(0.15, 0.5)
            h = wys * rnd.uniform(0.75, 1.05)
            px, pz = r * math.cos(a), r * math.sin(a)
            kol = rnd.choice(("dz_bambus", "dz_bambus", "dz_bambus_ciemny"))
            with s.uklad(pos=(px, 0.0, pz), obrot=(rnd.uniform(-5, 5), 0, rnd.uniform(-5, 5))):
                s.walec("Bambus", (0, h / 2.0, 0), 0.32, h, kol, "Wood", os="y")
                with s.cechy(cien=False):
                    s.walec("Bambus kolanko", (0, h * rnd.uniform(0.45, 0.65), 0), 0.38, 0.22, "dz_bambus_wezel", os="y")
        for q in (-1, 1):
            s.blok("Bambus liście", (q * szer * 0.25, wys * 0.95, rnd.uniform(-0.5, 0.5)), (szer * 0.9, 0.3, 1.6),
                   rnd.choice(("dz_lisc", "dz_lisc_jasny")), rot=(rnd.uniform(-15, 15), rnd.uniform(0, 180), q * rnd.uniform(15, 30)))
    return wys, szer * 0.6


# =========================================================================== podszyt i kwiaty
def krzew_dzungli(s, rnd, pos, k=1.0, kwiat=None):
    """Krzew podszytu: 3 bryły liści (ciemna, średnia, jasna) obrócone względem siebie, opcjonalnie dwa kwiaty (kolor
    `kwiat`) albo pomarańczowe owoce (kwiat="owoc"). Bez kolizji. 3–5 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), 0)), s.cechy(kolizja=False):
        s.blok("Krzak", (0, 1.0 * k, 0), (3.8 * k, 2.2 * k, 3.4 * k), "dz_lisc_ciemny", rot=(rnd.uniform(-8, 8), 20, rnd.uniform(-8, 8)))
        s.blok("Krzak", (1.1 * k, 1.7 * k, 0.5 * k), (2.8 * k, 1.9 * k, 2.6 * k), "dz_korona", rot=(12, 35, 0))
        with s.cechy(cien=False):
            s.blok("Krzak", (-0.5 * k, 2.4 * k, -0.3 * k), (2.1 * k, 1.6 * k, 2.1 * k), "dz_lisc", rot=(0, 15, 14))
            if kwiat:
                nazwa, kol = ("Owoc", "dz_owoc") if kwiat == "owoc" else ("Kwiat", kwiat)
                s.blok(nazwa, (1.7 * k, 2.3 * k, 1.2 * k), (0.9, 0.5 if nazwa == "Kwiat" else 0.9, 0.9), kol, rot=(20, 40, 10))
                s.blok(nazwa, (-1.4 * k, 1.9 * k, 1.4 * k), (0.8, 0.45 if nazwa == "Kwiat" else 0.8, 0.8), kol, rot=(-15, 70, 10))
    return 3.2 * k, 2.0 * k


def swiecacy_kwiat(s, rnd, pos, k=1.0, ry=0.0, kolor=None):
    """Świecący kwiat: wygięta łodyga, liść u nasady (klin), kielich z płatków (różowy albo żółty) i jarzący się środek
    (Neon). Bez kolizji i cienia. 4 części."""
    x, y, z = pos
    kol = kolor or rnd.choice(("dz_kwiat_rozowy", "dz_kwiat_rozowy", "dz_kwiat_jarzacy"))
    h = rnd.uniform(1.4, 2.4) * k
    a = rnd.uniform(0, 2 * math.pi)
    px, pz = 0.5 * k * math.cos(a), 0.5 * k * math.sin(a)
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.cechy(kolizja=False, cien=False):
        s.belka("Kwiat łodyga", (0, 0, 0), (px, h, pz), 0.18 * k + 0.05, "dz_liana", "SmoothPlastic")
        s.klin("Kwiat liść", (0.0, 0.3 * k, 0.0), (1.4 * k, 0.6 * k, 1.0 * k), "dz_lisc", rot=(0, rnd.uniform(0, 360), 0))
        s.blok("Kwiat kielich", (px, h + 0.1 * k, pz), (1.0 * k, 0.45 * k, 1.0 * k), kol, rot=(rnd.uniform(-12, 12), 45, rnd.uniform(-12, 12)))
        s.blok("Kwiat jarzący", (px, h + 0.35 * k, pz), (0.45 * k, 0.4 * k, 0.45 * k), kol, "Neon", rot=(0, 20, 0))
    return h + 0.6 * k, 0.9 * k


def kepa_kwiatow(s, rnd, pos, kolory=("dz_kwiat_czerwony", "dz_kwiat_zolty")):
    """Kępa zwykłych kwiatów dżungli: liście (klin) i dwa płaskie kwiaty-talerzyki. Bez kolizji i cienia. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), 0)), s.cechy(kolizja=False, cien=False):
        s.klin("Kępka", (0, 0.5, 0), (2.4, 1.0, 1.8), "dz_lisc_ciemny", rot=(0, 0, 6))
        s.blok("Kwiat", (-0.5, 1.05, 0.2), (1.2, 0.32, 1.2), kolory[0], rot=(12, 75, 8))
        s.blok("Kwiat", (0.7, 0.95, -0.3), (1.05, 0.3, 1.05), kolory[-1], rot=(8, 105, -10))
    return 1.2, 1.3


def paproc(s, rnd, pos, k=1.0):
    """Niska paproć dżungli: trzy łukowate liście (kliny) w rozkroku. Bez kolizji i cienia. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(kolizja=False, cien=False):
        for i in range(3):
            with s.uklad(obrot=(0, 120 * i + rnd.uniform(-15, 15), 0)):
                s.klin("Paproć", (0, 0.9 * k, 1.2 * k), (1.5 * k, 1.8 * k, 2.6 * k), rnd.choice(("dz_lisc", "dz_korona", "dz_lisc_jasny")),
                       rot=(-16, 0, 0))
    return 1.8 * k, 2.4 * k


def lisc_wodny(s, rnd, pos, r=1.0, kwiat=None):
    """Liść na wodzie (okrągły, z wcięciem — walec) i opcjonalny kwiat. Bez kolizji i cienia. 1–2 części."""
    x, y, z = pos
    with s.cechy(kolizja=False, cien=False):
        s.walec("Lilia", (x, y + 0.03, z), r, 0.08, rnd.choice(("dz_lisc", "dz_lisc_jasny", "dz_runo_jasne")), os="y")
        if kwiat:
            s.blok("Lilia kwiat", (x + 0.2 * r, y + 0.25, z), (0.7 * r, 0.4, 0.7 * r), kwiat, rot=(0, 45, 0))
