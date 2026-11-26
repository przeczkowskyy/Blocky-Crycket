# -*- coding: utf-8 -*-
"""JELONEK GAJU — pet legendarny z leśnego jajka (próba swiat/pety_proba; status: propozycja).

Przebudowa 25/26.11.2026 według arkusza obrotów Pawła (`jelonek_gaju_obroty.jpg`: przód, bok, tył, drugi bok). Wzór
wyglądu: „chibi” jelonek (ok. 3,6 studa z porożem): DUŻA okrągła głowa z kremową maską i małym noskiem, wielkie uszy
na boki z różowym środkiem, kryształowe poroże (cyjan) z różowymi kwiatkami, wianek z liści na krótkiej szyi
z zielonym świecącym klejnotem z przodu, krótki tułów z kremową piersią i białymi cętkami na grzbiecie, smukłe nogi
ze ZŁOTYMI dolnymi częściami i kopytkami, mały zadarty ogonek. Kości, nazwy kości i klipy jak w modelu z 17.11.

    python -B swiat/postacie/przebuduj.py jelonek_gaju --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Szyja > Glowa > {UchoL, UchoP, Poroze}, NogaPrzodL/P, NogaTylL/P, Ogonek}
Klipy: spoczynek, chod (stęp po przekątnej, pętla), radosc (podskok z obrotem i podkulonymi nogami), wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, lata, model, naklejka, oczy_okragle

ID = "jelonek_gaju"

PALETA = {
    "siersc": "D08A4E", "siersc_ciemna": "A8683A", "krem": "FFF1DC", "cetka": "FFFBF2", "nos": "3A2418",
    "kopyto": "FFC93C", "kryszt": "7DF2FF", "kryszt_ciemny": "38D9E8",
    "kwiat": "FF8FC8", "lisc": "5CC94A", "lisc_ciemny": "3E9A34", "klejnot": "7DFF5A", "ucho_srodek": "F5B0A8",
    "oko": "3A2216",
}

TULOW = ((0.0, 1.15, -0.1), (0.92, 0.82, 1.35))      # elipsoida tułowia
GLOWA = ((0.0, 2.22, 0.45), (1.18, 1.04, 1.04))         # elipsoida głowy
Y_TULOWIA = 1.15
NOGI = [("Przod", 0.3), ("Tyl", -0.5)]


def zbuduj():
    p = Postac(ID, "Jelonek Gaju", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    (tx, ty, tz), (tw, th, td) = TULOW
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=(tw, th, td), srodek=(tx, ty - Y_TULOWIA, tz))
    p.kosc("Szyja", "Tulow", staw=(0, 1.38, 0.3), czesc=(0.42, 0.5, 0.42), srodek=(0, 0.24, 0.06))
    p.kosc("Glowa", "Szyja", staw=(0, 1.76, 0.42), czesc=(gw, gh, gd), srodek=(gx, gy - 1.76, gz - 0.42))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Ucho" + s, "Glowa", staw=(zn * 0.46, gy + 0.2, gz - 0.02), czesc=(0.7, 0.3, 0.12),
               srodek=(zn * 0.33, 0.05, 0))
        for przod, z in NOGI:
            p.kosc("Noga%s%s" % (przod, s), "Tulow", staw=(zn * 0.24, 0.95, z), czesc=(0.2, 0.95, 0.2),
                   srodek=(0, -0.47, 0))
    p.kosc("Poroze", "Glowa", staw=(0, gy + gh / 2 - 0.08, gz - 0.05), czesc=(1.2, 1.0, 0.3), srodek=(0, 0.45, 0))
    p.kosc("Ogonek", "Tulow", staw=(0, 1.4, -0.74), czesc=(0.22, 0.34, 0.16), srodek=(0, 0.1, -0.05))

    # ------------------------------------------------------------------ tułów: kremowa pierś, białe cętki na grzbiecie
    with model(p, "Tulow"):
        p.kula("Tulow", (tx, ty, tz), (tw, th, td), "siersc", segm=20)
        p.kula("Piers", *lata(TULOW, (0, -0.45, 1), 0.3, s=0.12), "krem", "matowy", segm=20)
        for x, y, zn in ((0.2, 1.47, 1), (-0.22, 1.45, -1), (0.26, 1.4, -1), (-0.1, 1.52, 1)):
            naklejka(p, "Cetka", TULOW, x, y, (0.14, 0.1, 0.03), "cetka", z_znak=zn)

    # ------------------------------------------------------------------ krótka szyja z wiankiem i klejnotem
    with model(p, "Szyja"):
        p.walec("Szyja", (0, 1.62, 0.38), (0.42, 0.5, 0.42), "siersc", rot=(15, 0, 0), segm=12, faza=0.04)
        p.kula("Wianek", (0, 1.56, 0.42), (0.78, 0.22, 0.74), "lisc", "matowy", segm=16)
        for kat in (-50, 50, 180):
            a = math.radians(kat)
            p.kula("Wianek lisc", (0.34 * math.sin(a), 1.53, 0.42 + 0.32 * math.cos(a)), (0.24, 0.12, 0.4),
                   "lisc_ciemny", "matowy", rot=(0, kat + 60, 0), segm=10)
        p.blok("Klejnot", (0, 1.44, 0.8), (0.21, 0.21, 0.11), "klejnot", "swiecacy", rot=(0, 0, 45), faza=0.02)

    # ------------------------------------------------------------------ głowa: kremowa maska, nosek, oczy
    with model(p, "Glowa"):
        p.kula("Glowa", (gx, gy, gz), (gw, gh, gd), "siersc", segm=22)
        MASKA = lata(GLOWA, (0, -0.25, 1), 0.3, s=0.12)
        p.kula("Maska", *MASKA, "krem", "matowy", segm=22)
        PYSK = ((0, gy - 0.2, gz + 0.52), (0.4, 0.28, 0.3))
        p.kula("Pyszczek", *PYSK, "krem", "matowy", segm=14)
        p.kula("Nos", (0, gy - 0.13, gz + 0.66), (0.16, 0.11, 0.09), "nos", "polysk", segm=10)
        for zn in (1, -1):
            naklejka(p, "Buzia", PYSK, zn * 0.045, gy - 0.27, (0.08, 0.025, 0.025), "nos", ksztalt="blok",
                     obrot=zn * 25)
        oczy_okragle(p, MASKA, 0.25, gy + 0.05, szer=0.18, wys=0.23, kolor="oko", grub=0.07, blysk_maly=False)

    # ------------------------------------------------------------------ duże uszy na boki z różowym środkiem
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Ucho" + s, od="staw"), p.uklad(obrot=(0, -zn * 15, zn * 14)):
            p.kula("Ucho", (zn * 0.32, 0, 0), (0.66, 0.3, 0.12), "siersc", segm=12)
            p.kula("Ucho srodek", (zn * 0.34, 0, 0.045), (0.46, 0.17, 0.05), "ucho_srodek", "matowy", segm=10)

    # ------------------------------------------------------------------ kryształowe poroże z kwiatkami
    with p.na("Poroze", od="staw"):
        for zn, s in ((1, "L"), (-1, "P")):
            with p.uklad(pos=(zn * 0.24, 0, 0), obrot=(-10, 0, -zn * 22)):
                p.blok("Poroze " + s, (0, 0.4, 0), (0.2, 0.82, 0.2), "kryszt", "polysk", rot=(0, 45, 0), faza=0.04)
                with p.uklad(pos=(0, 0.42, 0), obrot=(0, 0, zn * 44)):
                    p.blok("Odnoga " + s, (0, 0.22, 0), (0.16, 0.46, 0.16), "kryszt", "polysk", rot=(0, 45, 0),
                           faza=0.03)
                with p.uklad(pos=(0, 0.2, 0), obrot=(0, 0, -zn * 50)):       # druga, niższa odnoga na zewnątrz
                    p.blok("Odnoga " + s, (0, 0.17, 0), (0.14, 0.36, 0.14), "kryszt", "polysk", rot=(0, 45, 0),
                           faza=0.03)
                p.blok("Krysztal " + s, (0, 0.92, 0), (0.22, 0.3, 0.22), "kryszt_ciemny", "swiecacy",
                       rot=(0, 45, 0), faza=0.03)
                p.kula("Kwiatek " + s, (zn * 0.04, 0.32, 0.12), (0.22, 0.22, 0.07), "kwiat", "matowy", segm=10)

    # ------------------------------------------------------------------ smukłe nogi ze złotymi dolnymi częściami
    for s in ("L", "P"):
        for przod, _z in NOGI:
            with p.na("Noga%s%s" % (przod, s), od="staw"):
                p.walec("Noga", (0, -0.27, 0), (0.2, 0.56, 0.2), "siersc" if przod == "Przod" else "siersc_ciemna",
                        segm=12, faza=0.03)
                p.walec("Kopytko", (0, -0.74, 0.01), (0.22, 0.42, 0.22), "kopyto", "metal", segm=12, faza=0.03)

    with p.na("Ogonek", od="staw"):
        p.kula("Ogonek", (0, 0.1, -0.05), (0.22, 0.34, 0.16), "cetka", "matowy", rot=(-30, 0, 0), segm=10)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Poroze", (0, 1.2, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 14)
    return p


SLABOSCI = [
    "Świecą kryształy na końcach poroża i klejnot (Neon w Roblox); gałęzie poroża są błyszczące, nie świecące — "
    "w grze cały Neon zlewał się z bliska w jedną cyjanową plamę (próba 17.11).",
    "Poroże ma po jednej odnodze na stronę (rysunek: dwie–trzy) i po jednym kwiatku — limit 45 części peta w grze.",
    "Nogi bez kolan (jedna bryła na kość) — stęp to wymach całych nóg; złota dolna część to osobny walec.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.02, 0), czestosc=2)
    k.cykl("Szyja", "obrot", (3, 0, 0), czestosc=1)
    k.cykl("Glowa", "obrot", (3, 6, 0), czestosc=1, faza=0.3)
    k.cykl("UchoL", "obrot", (0, 0, 10), czestosc=3)
    k.cykl("UchoP", "obrot", (0, 0, -10), czestosc=3, faza=0.4)
    k.cykl("Ogonek", "obrot", (22, 0, 0), czestosc=3)

    k = p.klip("chod", 24, petla=True)
    for s in ("L", "P"):
        for przod, _z in NOGI:
            faza = 0.0 if (s == "L") == (przod == "Przod") else 0.5
            k.cykl("Noga%s%s" % (przod, s), "obrot", (26, 0, 0), czestosc=1, faza=faza)
    k.cykl("Tulow", "przes", (0, 0.04, 0), czestosc=2, srodek=(0, 0.02, 0))
    k.cykl("Szyja", "obrot", (4, 0, 0), czestosc=2)
    k.cykl("UchoL", "obrot", (6, 0, 0), czestosc=2, faza=0.2)
    k.cykl("UchoP", "obrot", (6, 0, 0), czestosc=2, faza=0.25)
    k.cykl("Ogonek", "obrot", (14, 0, 0), czestosc=2)

    def dodatki(k, szczyt, koniec):
        for s in ("L", "P"):
            for przod, _z in NOGI:
                zn = -1 if przod == "Przod" else 1
                k.klucz(0, "Noga%s%s" % (przod, s), obrot=(0, 0, 0))
                k.klucz(szczyt, "Noga%s%s" % (przod, s), obrot=(zn * 40, 0, 0))
                k.klucz(koniec, "Noga%s%s" % (przod, s), obrot=(0, 0, 0))
        k.klucz(0, "Szyja", obrot=(0, 0, 0))
        k.klucz(szczyt, "Szyja", obrot=(-16, 0, 0))
        k.klucz(szczyt + 6, "Szyja", obrot=(8, 0, 0))
        k.klucz(koniec, "Szyja", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.85, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.6, wyskok=1.1, dodatki=lambda k: dodatki(k, 12, 30))
