# -*- coding: utf-8 -*-
"""Rekwizyty wspólne lokacji lasu: drogowskaz z ramionami-rekwizytami, ognisko pinu, lampion, Kamień Powrotu,
domy potworów (kałuża galarety, chatka-grzyb, jama w jeżynach, szpara w głazach), podkładka strefy walki,
zastępcza bryła potwora (tylko w podglądzie ze znacznikami).

Wszystko w bieżącym układzie wywołującego; pos = (x, y, z) na ziemi. Bez liter — rekwizyt zamiast napisu.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_TU)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny, skaly  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402

REKWIZYT_RAMIENIA = {"laka": "galareta", "kapeluszowo": "kapelusz", "ostepy": "ucho", "wawoz": "maczuga", "korona": "krysztal",
                     "serce": "uklon"}


def rekwizyt(s, rodzaj, pos):
    """Mały rekwizyt-symbol podbiomu na końcu ramienia drogowskazu (ok. 1,5 st). 1–2 części."""
    x, y, z = pos
    with s.cechy(kolizja=False):
        if rodzaj == "galareta":
            s.blok("Galareta", (x, y, z), (1.5, 1.5, 1.5), "galareta", rot=(10, 30, 8))
        elif rodzaj == "kapelusz":
            s.walec("Kapelusik", (x, y, z), 1.1, 0.7, "czerwien", os="y", rot=(0, 0, 12))
            s.blok("Kropka", (x, y + 0.4, z), (0.5, 0.2, 0.5), "biel")
        elif rodzaj == "ucho":
            s.naroznik("Wilcze ucho", (x, y, z), (1.2, 1.8, 1.0), "dach_sklep", rot=(0, 30, 0))
        elif rodzaj == "maczuga":
            s.belka("Maczuga", (x - 0.8, y - 0.6, z), (x + 0.8, y + 0.6, z), 0.7, "drewno_ciemne", "Wood", 0.7)
            s.blok("Maczuga głowica", (x + 0.9, y + 0.8, z), (1.2, 1.2, 1.2), "drewno_ciemne", rot=(20, 30, 10))
        elif rodzaj == "krysztal":
            s.naroznik("Kryształ", (x, y, z), (0.9, 2.0, 0.9), "neon_portal", "Neon", rot=(0, 45, 0))
        else:
            s.blok("Mały Ukłon", (x, y, z), (1.4, 1.4, 1.4), "lisc_rudy", rot=(0, 20, 14))


def drogowskaz(s, rnd, pos, ramiona, latarenka=True):
    """Słup-drogowskaz: krzywy słup i ramiona ku celom; ramiona = [(kąt ry ku celowi, podbiom), …]. Ok. 3 + 3/ramię części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, 0, rnd.choice((-5, 5)))):
        with s.cechy(kolizja=True):
            s.blok("Drogowskaz słup", (0, 3.6, 0), (0.9, 7.6, 0.9), "drewno", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Drogowskaz czapka", (0, 7.6, 0), (1.5, 0.5, 1.5), "drewno_ciemne", rot=(0, 45, 0))
            for i, (ry, pb) in enumerate(ramiona):
                yy = 6.4 - 1.1 * i
                with s.uklad(pos=(0, yy, 0), obrot=(0, ry, rnd.choice((-6, 6)))):
                    s.blok("Ramię", (0, 0, 2.2), (0.45, 0.7, 4.0), "drewno_jasne")
                    s.blok("Ramię grot", (0, 0, 4.4), (0.5, 0.9, 0.9), "drewno_jasne", rot=(45, 0, 0))
                    rekwizyt(s, REKWIZYT_RAMIENIA.get(pb, "uklon"), (0, 1.0, 4.4))
            if latarenka:
                s.blok("Latarenka", (0.9, 5.0, 0), (0.8, 1.0, 0.8), "neon_okno", "Neon")


def ognisko(s, rnd, pos):
    """Ognisko pinu (zapala się przy pierwszej wizycie): krąg kamieni, trzy polana, płomień Neon. 9 części."""
    x, y, z = pos
    with s.grupa("Piny/Ogniska"), s.uklad(pos=(x, y, z)):
        for k in range(5):
            a = 2 * math.pi * k / 5
            skaly.kanciak(s, rnd, (2.2 * math.cos(a), 0, 2.2 * math.sin(a)), 0.55, rnd.uniform(0, 360), "kamien_cokol",
                          kolizja=False) if k % 2 == 0 else None
        with s.cechy(kolizja=False):
            for k in range(3):
                s.belka("Polano", (-1.4 * math.cos(k * 2.1), 0.3, -1.4 * math.sin(k * 2.1)),
                        (0.4 * math.cos(k * 2.1), 1.3, 0.4 * math.sin(k * 2.1)), 0.5, "drewno", "Wood")
            with s.cechy(cien=False):
                s.naroznik("Płomień", (0, 1.6, 0), (1.3, 2.2, 1.3), "neon_ogien", "Neon", rot=(0, 30, 0))


def lampion(s, pos, wys=6.0, kolor="neon_okno"):
    """Lampion na krzywym kiju: kij, poprzeczka, lampion Neon. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, 0, 6)):
        s.blok("Lampion kij", (0, wys / 2.0, 0), (0.5, wys, 0.5), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Lampion ramię", (0.9, wys - 0.3, 0), (2.2, 0.35, 0.35), "drewno_ciemne")
            s.blok("Lampion", (1.7, wys - 1.2, 0), (0.9, 1.3, 0.9), kolor, "Neon")


def punkt_e(s, nazwa, pos):
    """Niewidzialny zaczep podpowiedzi E (ProximityPrompt). 1 część."""
    zestaw.punkt_interakcji(s, nazwa, pos)


# --------------------------------------------------------------------------- domy potworów
def kaluza_galarety(s, rnd, pos):
    """Dom slime'a: płaska kałuża galarety z kilkoma bąblami. Bez kolizji. 4 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), 0)), s.cechy(kolizja=False, cien=False):
        s.walec("Kałuża brzeg", (0, 0.12, 0), 3.4, 0.2, cien(s, "galareta", 0.6), os="y")
        s.walec("Kałuża galarety", (0.2, 0.2, 0), 3.0, 0.2, "galareta", os="y")
        s.blok("Bąbel", (1.0, 0.5, 0.6), (0.8, 0.6, 0.8), "galareta", rot=(0, 30, 0))
        s.blok("Bąbel", (-0.9, 0.4, -0.7), (0.6, 0.5, 0.6), "biel", rot=(0, 60, 0))


def chatka_grzyb(s, rnd, pos, ry=0.0, k=1.0, kapelusz="czerwien"):
    """Dom muchomornika: chatka-grzyb (pień-ściana, drzwi, okienko Neon, przekrzywiony kapelusz z kropkami). ~11 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.uklad(obrot=(0, 0, rnd.choice((-6, 6)))):
            s.walec("Chatka", (0, 3.0 * k - 0.4, 0), 3.0 * k, 6.0 * k + 0.8, "tynk_krem", os="y")
            with s.cechy(kolizja=False):
                s.blok("Chatka drzwi", (0, 1.8 * k, 2.85 * k), (1.8 * k, 3.4 * k, 0.4), "drewno_ciemne")
                s.blok("Chatka okienko", (1.9 * k, 3.9 * k, 2.2 * k), (0.9 * k, 0.9 * k, 0.3), "neon_okno", "Neon", rot=(0, 40, 0))
                with s.uklad(pos=(0, 6.0 * k, 0), obrot=(rnd.uniform(-6, 6), 0, rnd.choice((-14, 14)))):
                    s.walec("Chatka kapelusz spód", (0, -0.1, 0), 4.9 * k, 0.3, "tusz", os="y")
                    s.walec("Chatka kapelusz", (0, 0.9 * k, 0), 4.7 * k, 1.8 * k, kapelusz, os="y")
                    s.walec("Chatka kapelusz czubek", (0, 2.2 * k, 0), 3.0 * k, 1.2 * k, kapelusz, os="y")
                    with s.cechy(cien=False):
                        for a in (20, 140, 260):
                            s.blok("Kropka", (2.6 * k * math.cos(math.radians(a)), 1.85 * k, 2.6 * k * math.sin(math.radians(a))),
                                   (1.0, 0.3, 1.0), "biel")


def jama(s, rnd, pos, ry=0.0):
    """Dom wilka: kopiec jeżyn z ciemnym otworem i jasnymi kolcami. ~6 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=True):
            s.blok("Jama kopiec", (0, 2.2, -1.0), (8.0, 4.4, 6.0), "jezyna", rot=(0, 0, 4))
        with s.cechy(kolizja=False):
            s.blok("Jama kopiec", (2.6, 4.4, -1.6), (4.4, 2.6, 4.0), cien(s, "jezyna", 1.2), rot=(8, 30, 0))
            # po przeglądzie: z półki jama wyglądała jak fioletowe pudło — garby liści na wierzchu i kij nad otworem
            s.blok("Jama liście", (-1.8, 4.7, -1.4), (4.6, 1.8, 4.2), "lisc_ciemny", rot=(6, -20, -8))
            s.blok("Jama liście", (1.2, 5.6, -2.2), (3.4, 1.6, 3.0), "runo_ciemne", rot=(-6, 35, 6))
            s.belka("Jama kij", (-2.4, 3.1, 2.3), (2.4, 3.4, 2.3), 0.5, "drewno_ciemne", "Wood")
            s.blok("Jama otwór", (0, 1.5, 2.0), (3.2, 2.8, 0.4), "tusz")
            with s.cechy(cien=False):
                for xx in (-3.0, 0.4, 2.8):
                    s.naroznik("Kolec", (xx, 4.7, 0.4), (0.8, 1.4, 0.8), "jezyna_kolec", rot=(0, 45, 0))


def szpara(s, rnd, pos, ry=0.0, kolor="kamien_cieply"):
    """Dom wilka w kamieniu: dwa głazy z ciemną szparą między nimi. ~8 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        skaly.glaz(s, rnd, (-3.0, 0, 0), 1.3, 20, kolor, mech=False)
        skaly.glaz(s, rnd, (3.0, 0, -0.5), 1.1, -15, kolor, mech=True)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Szpara", (0, 1.6, 1.0), (1.4, 3.0, 0.4), "tusz")


def plama(rnd, cx, cz, r0, r1, n, rozrzut=0.06):
    """Nieregularny gwiaździsty wielokąt (x, z): promień płynnie faluje między r0 i r1 (dwie harmoniczne o losowej fazie),
    kąty wierzchołków lekko rozrzucone. Wielokąt jest prosty (kąty rosną), więc triangulacja ma n − 2 trójkątów."""
    f1, f2 = rnd.uniform(0, 2 * math.pi), rnd.uniform(0, 2 * math.pi)
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-rozrzut, rozrzut)
        t = 0.5 + 0.3 * math.sin(2 * a + f1) + 0.2 * math.sin(3 * a + f2)
        r = r0 + (r1 - r0) * t
        pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def podkladka(s, rnd, nazwa, x, y, z, r, kolor, wezly=()):
    """Podkładka strefy walki (ΔL* ≥ 20 pod potworem). Wersja 2: zamiast „kół z kół” nieregularne plamy-wielokąty:
    pod każdym węzłem walki plama r 13,6–20 (promień faluje, więc z góry nie widać wielokąta foremnego), między dalekimi
    węzłami łącznik, przy co trzecim węźle strzęp na zewnątrz. Plamy leżą na wysokościach różniących się o 0,006
    (wierzch 0,100–0,112 nad gruntem), żeby nachodzące na siebie faktury nie migotały. Plama węzła ma 8 wierzchołków
    (6 trójkątów = 12 klinów); r 13,6 × cos(π/8 + 0,08) = 12,1 > 12, więc plac walki jest cały na podkładce.
    ok. 12–20 części na węzeł."""
    from swiat.biom_las.teren import wielokat
    with s.cechy(kolizja=False, cien=False):
        n = len(wezly)
        for i, (wx, wz) in enumerate(wezly):
            wielokat(s, nazwa, plama(rnd, wx, wz, 13.6, 20.0, 8, 0.08), y + 0.10 + 0.006 * (i % 3), 0.2, kolor)
            if i % 3 == 0:
                a = math.atan2(wz - z, wx - x) + rnd.uniform(-0.9, 0.9)
                wielokat(s, nazwa, plama(rnd, wx + 14.5 * math.cos(a), wz + 14.5 * math.sin(a), 3.5, 6.0, 5, 0.15),
                         y + 0.103 + 0.006 * (i % 2), 0.2, kolor)
            if n > 1:
                bx, bz = wezly[(i + 1) % n]
                if math.hypot(bx - wx, bz - wz) > 30:
                    wielokat(s, nazwa, plama(rnd, (wx + bx) / 2.0, (wz + bz) / 2.0, 6.0, 9.0, 6, 0.12),
                             y + 0.109 - 0.006 * (i % 2), 0.2, kolor)


def zastepczy_potwor(s, nazwa, pos, rodzaj):
    """Zastępcza bryła potwora w skali (tylko w podglądzie ze znacznikami): slime 2,7, wilk 4,4 × 7,7, muchomornik 3,6,
    troll 9,9, strażnik 14,5."""
    x, y, z = pos
    with s.cechy(kolizja=False):
        if rodzaj == "Leśny Slime":
            s.blok(nazwa, (x, y + 1.35, z), (2.7, 2.7, 2.7), "7EDB57")
        elif rodzaj == "Bursztynowy Slime":
            s.blok(nazwa, (x, y + 1.35, z), (2.7, 2.7, 2.7), "zloto")
        elif rodzaj == "Muchomornik":
            s.blok(nazwa, (x, y + 1.0, z), (1.8, 2.0, 1.8), "biel")
            s.walec(nazwa, (x, y + 2.8, z), 1.5, 1.4, "czerwien", os="y")
        elif rodzaj == "Cierniowy Wilk":
            s.blok(nazwa, (x, y + 2.2, z), (2.4, 3.0, 7.0), "kamien_lochu")
            s.blok(nazwa, (x, y + 3.6, z + 3.6), (1.8, 1.8, 1.8), "kamien_lochu")
        elif rodzaj == "Leśny Troll":
            s.blok(nazwa, (x, y + 4.95, z), (8.0, 9.9, 6.0), "drewno")
        else:
            s.blok(nazwa, (x, y + 7.25, z), (8.9, 14.5, 6.0), "kamien_cieply")
