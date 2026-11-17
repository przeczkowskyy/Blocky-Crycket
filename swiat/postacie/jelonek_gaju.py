# -*- coding: utf-8 -*-
"""JELONEK GAJU — pet legendarny z leśnego jajka (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny
projekt).

Smukły jelonek (ok. 3,3 studa z porożem): płowa sierść z białymi cętkami, duże oczy, uszy na boki, złote kopytka,
liściasty wianek ze świecącym klejnotem na szyi i — najważniejsze — świecące kryształowe poroże z kwiatkami i listkami.
Sylwetka: wysoki, na długich nogach, z porożem — najbardziej efektowny z piątki (legendarny: świeci najmocniej).

    python -B swiat/postacie/przebuduj.py jelonek_gaju --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Szyja > Glowa > {UchoL, UchoP, Poroze}, NogaPrzodL/P, NogaTylL/P, Ogonek}
Klipy: spoczynek, chod (stęp po przekątnej, pętla), radosc (podskok z obrotem i podkulonymi nogami), wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "jelonek_gaju"

PALETA = {
    "siersc": "C98B55", "siersc_ciemna": "9E6436", "krem": "FFF1DC", "cetka": "FFF8EA", "nos": "2A1A12",
    "kopyto": "FFD34D", "kopyto_ciemne": "D9A62E", "kryszt": "7DF9FF", "kryszt_ciemny": "38D9E8",
    "kwiat": "FF8FC8", "kwiat_srodek": "FFE066", "lisc": "6DD45A", "klejnot": "9BFF6A", "ucho_srodek": "F5B7A0",
}

TULOW = (0.85, 0.75, 1.5)
Y_TULOWIA = 1.25
NOGI = [("Przod", 0.5), ("Tyl", -0.55)]


def zbuduj():
    p = Postac(ID, "Jelonek Gaju", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, 0, -0.05))
    p.kosc("Szyja", "Tulow", staw=(0, 1.5, 0.55), czesc=(0.42, 0.75, 0.42), srodek=(0, 0.3, 0.1))
    p.kosc("Glowa", "Szyja", staw=(0, 2.05, 0.72), czesc=(0.82, 0.74, 0.84), srodek=(0, 0.22, 0.16))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Ucho" + s, "Glowa", staw=(zn * 0.36, 2.45, 0.76), czesc=(0.5, 0.2, 0.28), srodek=(zn * 0.22, 0.02, 0))
        for przod, z in NOGI:
            p.kosc("Noga%s%s" % (przod, s), "Tulow", staw=(zn * 0.26, 1.0, z), czesc=(0.22, 1.0, 0.24),
                   srodek=(0, -0.5, 0))
    p.kosc("Poroze", "Glowa", staw=(0, 2.62, 0.82), czesc=(1.4, 1.0, 0.3), srodek=(0, 0.45, 0))
    p.kosc("Ogonek", "Tulow", staw=(0, 1.5, -0.8), czesc=(0.26, 0.32, 0.16), srodek=(0, 0.0, -0.06))

    # ------------------------------------------------------------------ tułów
    with p.na("Tulow", od="srodek"):
        w, h, d = TULOW
        p.blok("Tulow", (0, 0, 0), TULOW, "siersc", faza=0.12)
        p.blok("Brzuch", (0, -h / 2 - 0.02, 0.05), (0.66, 0.06, 1.1), "krem", "matowy", faza=0.02)
        p.blok("Piers", (0, -0.05, d / 2 + 0.02), (0.6, 0.5, 0.06), "krem", "matowy", faza=0.03)
        for x, z in ((0.2, 0.35), (-0.18, 0.05), (0.15, -0.3), (-0.22, -0.55)):
            p.blok("Cetka", (x, h / 2 + 0.02, z), (0.17, 0.04, 0.17), "cetka", "matowy", faza=0.0)

    # ------------------------------------------------------------------ szyja z wiankiem i klejnotem
    with p.na("Szyja", od="srodek"):
        p.blok("Szyja", (0, 0, 0), (0.42, 0.75, 0.42), "siersc", rot=(18, 0, 0), faza=0.08)
        p.blok("Wianek", (0, -0.22, 0.02), (0.58, 0.16, 0.56), "lisc", "matowy", faza=0.04)
        p.blok("Klejnot", (0, -0.28, 0.32), (0.18, 0.18, 0.08), "klejnot", "swiecacy", rot=(0, 0, 45), faza=0.0)

    # ------------------------------------------------------------------ głowa
    with p.na("Glowa", od="srodek"):
        w, h, d = 0.82, 0.74, 0.84
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "siersc", faza=0.12)
        p.blok("Pyszczek", (0, -0.18, z + 0.16), (0.4, 0.3, 0.42), "krem", "matowy", faza=0.06)
        p.blok("Nos", (0, -0.08, z + 0.38), (0.16, 0.11, 0.06), "nos", "polysk", faza=0.03)
        oczy(p, 0.22, 0.1, z, szer=0.2, wys=0.27)

    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Ucho" + s, od="srodek"):
            p.blok("Ucho", (zn * 0.04, 0, 0), (0.6, 0.24, 0.34), "siersc_ciemna", rot=(0, 0, zn * 18), faza=0.05)
            p.blok("Ucho srodek", (zn * 0.06, 0.01, 0.15), (0.42, 0.13, 0.06), "ucho_srodek", "matowy",
                   rot=(0, 0, zn * 18), faza=0.0)

    # ------------------------------------------------------------------ kryształowe poroże z kwiatkami
    with p.na("Poroze", od="staw"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Poroze " + s, (zn * 0.2, 0.28, 0), (0.12, 0.62, 0.12), "kryszt", "polysk", rot=(0, 0, -zn * 26),
                   faza=0.0)
            p.blok("Odnoga gorna " + s, (zn * 0.42, 0.72, 0), (0.1, 0.46, 0.1), "kryszt", "polysk",
                   rot=(0, 0, zn * 8), faza=0.0)
            p.blok("Odnoga boczna " + s, (zn * 0.55, 0.4, 0), (0.1, 0.34, 0.1), "kryszt", "polysk",
                   rot=(0, 0, -zn * 62), faza=0.0)
            p.blok("Krysztal " + s, (zn * 0.44, 1.0, 0), (0.2, 0.26, 0.2), "kryszt_ciemny", "swiecacy",
                   rot=(0, 45, 0), faza=0.03)
            p.blok("Kwiatek " + s, (zn * 0.27, 0.42, 0.08), (0.18, 0.18, 0.08), "kwiat", "matowy", rot=(0, 0, 45),
                   faza=0.0)
            p.blok("Listek " + s, (zn * 0.12, 0.12, 0.04), (0.26, 0.06, 0.14), "lisc", "matowy",
                   rot=(0, zn * 20, zn * 30), faza=0.0)

    # ------------------------------------------------------------------ nogi ze złotymi kopytkami
    for s in ("L", "P"):
        for przod, _z in NOGI:
            with p.na("Noga%s%s" % (przod, s), od="srodek"):
                p.blok("Noga", (0, 0.06, 0), (0.2, 0.88, 0.22), "siersc" if przod == "Przod" else "siersc_ciemna",
                       faza=0.04)
                p.blok("Kopytko", (0, -0.42, 0.02), (0.25, 0.16, 0.29), "kopyto", "metal", faza=0.03)

    with p.na("Ogonek", od="srodek"):
        p.blok("Ogonek", (0, 0, 0), (0.26, 0.32, 0.16), "cetka", "matowy", rot=(-25, 0, 0), faza=0.05)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Poroze", (0, 1.25, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 14)
    return p


SLABOSCI = [
    "Świecą kryształy na końcach poroża i klejnot (Neon w Roblox); gałęzie poroża są błyszczące, nie świecące — "
    "w grze cały Neon zlewał się z bliska w jedną cyjanową plamę (próba 17.11).",
    "Nogi bez kolan (jedna bryła) — stęp to wymach całych nóg.",
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
