# -*- coding: utf-8 -*-
"""NENUFAREK — pet zwykły z jajka Bagna (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Mały żółwik (ok. 1,5 studa, 2 studa długości) z pancerzem z liścia grzybienia: miętowa skóra, okrągła główka
z wielkimi oczami, cztery krótkie płetwonóżki, na pancerzu-liściu różowy kwiat nenufaru. Sylwetka: płaska, szeroka
kopułka — inna niż długi ślimak lasu i niż ropuchy Bagna.

    python -B swiat/postacie/przebuduj.py nenufarek --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X): Root > Tulow > {Glowa, Kwiat, NogaPrzodL/P, NogaTylL/P, Ogonek}
Klipy: spoczynek, chod (człapanie z kołysaniem pancerza), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "nenufarek"

PALETA = {
    "skora": "9BD3B6", "skora_ciemna": "6FAE8F", "pancerz": "5A9A7C", "lisc": "4E9A3E", "lisc_jasny": "79C25E",
    "kwiat": "F59AC0", "kwiat_jasny": "FFC6DD", "kwiat_srodek": "FFE066", "rumieniec": "F08C8C", "buzia": "2E4A3A",
}

Y_TULOWIA = 0.6
NOGI = [("Przod", 0.42), ("Tyl", -0.42)]


def zbuduj():
    p = Postac(ID, "Nenufarek", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=(1.3, 0.55, 1.4), srodek=(0, 0.05, 0))
    p.kosc("Glowa", "Tulow", staw=(0, 0.62, 0.62), czesc=(0.72, 0.62, 0.66), srodek=(0, 0.12, 0.3))
    p.kosc("Kwiat", "Tulow", staw=(0.15, 0.99, -0.1), czesc=(0.5, 0.36, 0.5), srodek=(0, 0.15, 0))
    p.kosc("Ogonek", "Tulow", staw=(0, 0.5, -0.72), czesc=(0.2, 0.16, 0.3), srodek=(0, 0, -0.12))
    for s, zn in (("L", 1), ("P", -1)):
        for przod, z in NOGI:
            p.kosc("Noga%s%s" % (przod, s), "Tulow", staw=(zn * 0.5, 0.41, z), czesc=(0.3, 0.42, 0.34),
                   srodek=(zn * 0.06, -0.2, 0))

    with p.na("Tulow", od="srodek"):
        p.blok("Brzuch", (0, -0.14, 0), (1.1, 0.3, 1.2), "skora_ciemna", "matowy", faza=0.08)
        p.blok("Pancerz", (0, 0.06, 0), (1.3, 0.42, 1.4), "pancerz", faza=0.16)
        p.blok("Pancerz gora", (0, 0.3, 0), (0.9, 0.18, 1.0), "pancerz", faza=0.08)
        # liść grzybienia na grzbiecie (dwa skośne klocki = okrągły liść z klinowym wcięciem z tyłu)
        p.blok("Lisc", (0, 0.4, 0), (1.42, 0.06, 1.42), "lisc", "matowy", faza=0.02)
        p.blok("Lisc skos", (0, 0.41, 0), (1.42, 0.06, 1.42), "lisc", "matowy", rot=(0, 45, 0), faza=0.02)
        for a in (0, 60, 120):
            p.blok("Lisc zylka", (0, 0.45, 0), (1.16, 0.02, 0.05), "lisc_jasny", "matowy", rot=(0, a, 0), faza=0.0)
    with p.na("Glowa", od="srodek"):
        w, h, d = 0.72, 0.62, 0.66
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "skora", faza=0.14)
        oczy(p, 0.18, 0.08, z, szer=0.18, wys=0.24)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.27, -0.1, z + 0.02), (0.12, 0.06, 0.04), "rumieniec", "matowy", faza=0.0)
        p.blok("Buzia", (0, -0.14, z + 0.02), (0.18, 0.04, 0.04), "buzia", "matowy", faza=0.0)
    with p.na("Kwiat", od="staw"):
        for i in range(5):
            a = math.radians(i * 72)
            p.blok("Platek", (0.15 * math.cos(a), 0.12, 0.15 * math.sin(a)), (0.24, 0.12, 0.2), "kwiat" if i % 2
                   else "kwiat_jasny", "matowy", rot=(0, -math.degrees(a), 25), faza=0.02)
        p.blok("Kwiat srodek", (0, 0.2, 0), (0.14, 0.1, 0.14), "kwiat_srodek", "matowy", faza=0.02)
    with p.na("Ogonek", od="srodek"):
        p.blok("Ogonek", (0, 0, 0), (0.18, 0.14, 0.3), "skora_ciemna", "matowy", faza=0.04)
    for s in ("L", "P"):
        for przod, _z in NOGI:
            with p.na("Noga%s%s" % (przod, s), od="srodek"):
                p.blok("Noga", (0, 0, 0), (0.3, 0.42, 0.34), "skora", faza=0.08)
                p.blok("Pletwa", (0, -0.17, 0.06), (0.36, 0.08, 0.44), "skora_ciemna", "matowy", faza=0.02)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Kwiat", (0, 0.65, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 6)
    return p


SLABOSCI = ["Liść grzybienia to dwa skośne płaskie klocki — z bliska ośmiokąt, nie koło."]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Glowa", "obrot", (4, 10, 0), czestosc=1)
    k.cykl("Kwiat", "obrot", (0, 0, 6), czestosc=2)
    k.cykl("Tulow", "przes", (0, 0.02, 0), czestosc=2)
    k.cykl("Ogonek", "obrot", (0, 18, 0), czestosc=2)

    k = p.klip("chod", 24, petla=True)
    for s in ("L", "P"):
        for przod, _z in NOGI:
            faza = 0.0 if (s == "L") == (przod == "Przod") else 0.5
            k.cykl("Noga%s%s" % (przod, s), "obrot", (30, 0, 0), czestosc=1, faza=faza)
    k.cykl("Tulow", "obrot", (0, 0, 5), czestosc=1)
    k.cykl("Tulow", "przes", (0, 0.04, 0), czestosc=2, srodek=(0, 0.02, 0))
    k.cykl("Glowa", "obrot", (5, 0, 0), czestosc=2)
    k.cykl("Kwiat", "obrot", (0, 0, 9), czestosc=2, faza=0.25)

    def dodatki(k, szczyt, koniec):
        for s in ("L", "P"):
            for przod, _z in NOGI:
                zn = 1 if s == "L" else -1
                k.klucz(0, "Noga%s%s" % (przod, s), obrot=(0, 0, 0))
                k.klucz(szczyt, "Noga%s%s" % (przod, s), obrot=(0, 0, zn * 45))
                k.klucz(koniec, "Noga%s%s" % (przod, s), obrot=(0, 0, 0))
        k.klucz(0, "Kwiat", przes=(0, 0, 0))
        k.klucz(szczyt, "Kwiat", przes=(0, 0.22, 0))
        k.klucz(szczyt + 5, "Kwiat", przes=(0, -0.03, 0))
        k.klucz(koniec, "Kwiat", przes=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.6, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=0.9, wyskok=0.8, dodatki=lambda k: dodatki(k, 12, 30))
