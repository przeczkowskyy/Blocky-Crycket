# -*- coding: utf-8 -*-
"""Rekwizyty legowiska w stylu smoka — statyczne rigi z części (jedna kość „Podstawa”): skarb w trzech rozmiarach,
cokół trofeum, gniazdo z jajami. Strumień ognia służy tylko do obrazów strony gry (w grze ogień robią cząsteczki).

    from swiat.ewolucja.modele import rekwizyty
    rekwizyty.wszystkie()        # lista Postac: skarb_1, skarb_2, skarb_3, cokol, gniazdo
"""
import math
import random

from swiat.ewolucja.modele.smok_model import Smok

PALETA = {"zloto": "FFC934", "zloto_c": "E09A1A", "zloto_j": "FFE680", "kamien": "5A5470", "kamien_c": "3B3650",
          "kamien_j": "7C7696", "zar": "FF7A2A", "zar_j": "FFD98A", "rubin": "FF3D6A", "szmaragd": "35DD8A",
          "szafir": "4FA8FF", "skorupa": "FFF6E0", "plama": "FFC02E", "sloma": "C9A86A"}


def _nowy(id, nazwa):
    p = Smok(id, nazwa, typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    p.kosc("Podstawa", "Root", (0, 0, 0), czesc=(2, 1, 2), srodek=(0, 0.5, 0))
    return p


def skarb(rozmiar=2):
    """Kopiec złota: trzy warstwy, na nich monety, sztaby, stosy monet i świecące klejnoty. Rozmiar 1–3."""
    R = {1: 2.2, 2: 3.6, 3: 5.6}[rozmiar]
    p = _nowy("skarb_%d" % rozmiar, "Skarb %d" % rozmiar)
    los = random.Random(40 + rozmiar)
    with p.na("Podstawa"):
        for i, (r_, h, y) in enumerate(((R, R * 0.22, 0.0), (R * 0.68, R * 0.22, R * 0.2), (R * 0.36, R * 0.2, R * 0.4))):
            p.walec("Kopiec %d" % i, (R * 0.06 * (i % 2), y + h / 2, -R * 0.05 * i), (r_ * 2, h, r_ * 2.1),
                    "zloto" if i % 2 == 0 else "zloto_c", "metal", rot=(0, 22.5 * i, 0), segm=8)
        for i in range(rozmiar * 3):                             # monety rozsypane wokół kopca
            a, rr = los.uniform(0, 2 * math.pi), los.uniform(1.05, 1.3) * R
            p.walec("Moneta luzem", (rr * math.cos(a), 0.07, rr * math.sin(a)), (0.8, 0.14, 0.8), "zloto_j", "metal", segm=8)
        for i in range({1: 8, 2: 16, 3: 30}[rozmiar]):
            a, rr = los.uniform(0, 2 * math.pi), los.uniform(0.2, 0.92) * R
            x, z = rr * math.cos(a), rr * math.sin(a)
            y = R * (0.22 if rr > R * 0.68 else (0.42 if rr > R * 0.36 else 0.6))
            if i % 4 == 0:
                p.walec("Moneta", (x, y + 0.06, z), (0.75, 0.12, 0.75), "zloto_j", "metal",
                        rot=(los.uniform(-14, 14), 0, los.uniform(-14, 14)), segm=8)
            elif i % 4 == 1:
                p.blok("Sztaba", (x, y + 0.16, z), (1.05, 0.32, 0.52), "zloto_c", "metal", rot=(0, los.uniform(0, 180), 0))
            elif i % 4 == 2:
                p.blok("Klejnot", (x, y + 0.3, z), (0.46, 0.46, 0.46), los.choice(("rubin", "szmaragd", "szafir")),
                       "swiecacy", rot=(45, los.uniform(0, 90), 45), faza=0.0)
            else:
                p.walec("Stos monet", (x, y + 0.22, z), (0.62, 0.44, 0.62), "zloto", "metal", segm=8)
        if rozmiar == 3:                                        # kielich z wielkim klejnotem na szczycie
            p.walec("Kielich noga", (0, R * 0.6 + 0.4, 0), (0.5, 0.8, 0.5), "zloto_c", "metal", segm=8)
            p.walec("Kielich", (0, R * 0.6 + 1.1, 0), (1.4, 0.7, 1.4), "zloto_j", "metal", segm=8)
            p.blok("Klejnot szczytu", (0, R * 0.6 + 1.9, 0), (0.9, 0.9, 0.9), "rubin", "swiecacy", rot=(45, 20, 45), faza=0.0)
    p.zaczep("SzczytAttachment", "Podstawa", (0, R * 0.6 + 0.1, 0))
    return p


def cokol():
    """Cokół trofeum: dwa kamienne stopnie z żarem w szczelinach (jak łuski smoka) i płyta na trofeum 5 × 5."""
    p = _nowy("cokol", "Cokół trofeum")
    with p.na("Podstawa"):
        p.blok("Stopien 1", (0, 0.3, 0), (6.4, 0.6, 6.4), "kamien_c", "matowy", faza=0.1)
        p.blok("Zar", (0, 0.66, 0), (5.8, 0.14, 5.8), "zar", "swiecacy", faza=0.0)
        p.blok("Stopien 2", (0, 1.05, 0), (5.4, 0.7, 5.4), "kamien", "matowy", faza=0.1)
        p.blok("Zar rdzen", (0, 1.44, 0), (4.7, 0.1, 4.7), "zar_j", "swiecacy", faza=0.0)
        p.blok("Plyta", (0, 1.62, 0), (5.0, 0.3, 5.0), "kamien_j", "matowy", faza=0.08)
        for i, (sx, sz) in enumerate(((1, 1), (-1, 1), (-1, -1), (1, -1))):
            p.klin("Krysztal", (sx * 2.95, 1.05, sz * 2.95), (0.42, 1.5, 0.56), "zloto_j", "polysk", rot=(0, 45 + 90 * i, 0),
                   faza=0.02)
    p.zaczep("TrofeumAttachment", "Podstawa", (0, 1.77, 0))
    return p


def gniazdo():
    """Gniazdo: krąg kamieni, słoma, żar pod spodem i trzy jaja."""
    p = _nowy("gniazdo", "Gniazdo z jajami")
    with p.na("Podstawa"):
        for i in range(8):
            a = math.radians(i * 45)
            p.blok("Kamien", (2.7 * math.cos(a), 0.42 + 0.08 * (i % 2), 2.7 * math.sin(a)), (2.0, 0.84 + 0.16 * (i % 2), 1.05),
                   "kamien" if i % 2 else "kamien_c", "matowy", rot=(0, -i * 45 - 90, 0), faza=0.1)
        p.walec("Sloma", (0, 0.2, 0), (4.8, 0.4, 4.8), "sloma", "matowy", segm=8)
        p.walec("Zar", (0, 0.43, 0), (3.2, 0.06, 3.2), "zar", "swiecacy", segm=8)
        for j, (x, z, rz) in enumerate(((0.0, 0.55, 0), (-1.05, -0.5, 14), (1.1, -0.4, -12))):
            with p.uklad(pos=(x, 0.4, z), obrot=(0, 40 * j, rz)):
                p.walec("Jajo 1", (0, 0.3, 0), (1.0, 0.6, 1.0), "skorupa", "matowy", segm=8)
                p.walec("Jajo 2", (0, 0.85, 0), (1.3, 0.6, 1.3), "skorupa", "matowy", segm=8)
                p.walec("Plama", (0, 0.9, 0), (1.34, 0.18, 1.34), "plama", "matowy", segm=8)
                p.walec("Jajo 3", (0, 1.4, 0), (1.0, 0.5, 1.0), "skorupa", "matowy", segm=8)
    return p


def ogien(dl=9.0):
    """Strumień ognia wzdłuż +Z (tylko do obrazów): rosnące świecące bryły od białego żaru do czerwieni."""
    p = _nowy("ogien", "Strumień ognia")
    kolory = ("FFFBE0", "FFF09A", "FFD84A", "FFB52E", "FF8A2A", "FF6A1A", "F0481A", "D8301A")
    with p.na("Podstawa"):
        for i, kolor in enumerate(kolory):
            f = i / (len(kolory) - 1.0)
            s_ = 0.5 + 2.4 * f
            p.blok("Ogien %d" % i, (0, 0.2 * math.sin(i * 1.7), dl * (0.04 + 0.96 * f)), (s_, s_, s_ * 1.25), kolor,
                   "swiecacy", rot=(0, 0, 45 + 20 * i), faza=0.0)
    return p


def ogien2(dl=9.0):
    # Strumień ognia do obrazów (wersja 2): jasny rdzeń z obłych brył, wokół języki ognia (ostrosłupy szpicem w przód,
    # odchylone na zewnątrz) od żółtych przy osi po czerwone na obrzeżu i końcu, na końcu iskry.
    p = _nowy("ogien", "Strumień ognia")
    los = random.Random(5)
    with p.na("Podstawa"):
        for i, kolor in enumerate(("FFFDF0", "FFF7C8", "FFEE9A", "FFE070", "FFD050")):
            f = i / 4.0
            p.kula("Rdzen", (0, 0, dl * (0.06 + 0.5 * f)), (0.7 + 1.6 * f, 0.7 + 1.4 * f, dl * 0.22), kolor, "swiecacy", segm=12)
        for i in range(52):
            f = los.random() ** 0.8
            r_max = 0.25 + 1.9 * f
            a, rr = los.uniform(0, 2 * math.pi), r_max * los.uniform(0.3, 1.0)
            dlug, gr = (1.0 + 2.4 * f) * los.uniform(0.7, 1.3), (0.3 + 0.8 * f) * los.uniform(0.7, 1.2)
            brzeg = rr / r_max
            kolor = "FFE680" if (brzeg < 0.45 and f < 0.7) else ("FFA62E" if (brzeg < 0.75 or f < 0.45) else ("FF6A1A" if f < 0.85 else "E8381A"))
            th = math.radians(10 + 16 * brzeg)
            rx = -math.degrees(math.asin(math.sin(th) * math.sin(a)))
            ry = math.degrees(math.asin(max(-1.0, min(1.0, math.sin(th) * math.cos(a) / math.cos(math.radians(rx))))))
            with p.uklad(pos=(rr * math.cos(a), rr * math.sin(a), dl * (0.08 + 0.9 * f)), obrot=(rx, ry, 0)):
                p.ostroslup("Jezyk ognia", (0, 0, dlug / 2), (gr, dlug, gr), kolor, "swiecacy", rot=(90, 0, 0), gora=(0.0, 0.0), faza=0.0)
        for i in range(14):
            a, rr = los.uniform(0, 2 * math.pi), los.uniform(1.0, 2.8)
            p.blok("Iskra", (rr * math.cos(a), rr * math.sin(a), dl * los.uniform(0.75, 1.15)), (0.22, 0.22, 0.22), "FFE680", "swiecacy",
                   rot=(45, los.uniform(0, 90), 45), faza=0.0)
    return p


def wszystkie():
    return [skarb(1), skarb(2), skarb(3), cokol(), gniazdo()]
