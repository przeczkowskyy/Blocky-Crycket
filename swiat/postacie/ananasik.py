# -*- coding: utf-8 -*-
"""ANANASIK — pet pospolity z jajka Dżungli (próba swiat/pety_proba, 18.11.2026; status: propozycja, własny projekt).

Mały ananas na nóżkach (ok. 2,4 studa z koroną): pękaty, złocisty owoc w ciemniejsze łuski-romby, z buzią i rumieńcami,
na czubku korona z sześciu sztywnych liści, z boków dwa listki-rączki, nóżki krótkie i zielone. Sylwetka: pękata
beczułka z pióropuszem liści — inna niż Żołędziak (okrągły żołądź w czapeczce) i Pałkuś (wąska kolba na łodyżce).

    python -B swiat/postacie/przebuduj.py ananasik --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X): Root > Tulow (owoc) > {Korona, RekaL, RekaP, NogaL, NogaP}
Klipy: spoczynek, chod (drobne kroczki z kołysaniem korony), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "ananasik"

PALETA = {
    "owoc": "F2B030", "owoc_ciemny": "C98A1E", "luska": "A86A14", "lisc": "2FA34A", "lisc_jasny": "6CCB4A",
    "noga": "3E7D2E", "rumieniec": "F08C6C", "buzia": "4A2A10",
}

Y_TULOWIA = 0.42      # spód owocu (wierzch nóżek)
OWOC = (1.1, 1.2, 1.05)


def zbuduj():
    p = Postac(ID, "Ananasik", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    w, h, d = OWOC
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=OWOC, srodek=(0, h / 2, 0))
    p.kosc("Korona", "Tulow", staw=(0, Y_TULOWIA + h - 0.06, 0), czesc=(0.9, 0.85, 0.9), srodek=(0, 0.4, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Reka" + s, "Tulow", staw=(zn * 0.5, Y_TULOWIA + 0.62, 0.05), czesc=(0.36, 0.14, 0.22),
               srodek=(zn * 0.2, -0.05, 0))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.24, Y_TULOWIA + 0.04, 0), czesc=(0.24, 0.46, 0.3), srodek=(0, -0.22, 0.03))

    with p.na("Tulow", od="srodek"):
        p.kula("Owoc", (0, 0, 0), OWOC, "owoc", "matowy", segm=16)
        p.kula("Owoc spod", (0, -h * 0.3, 0), (w * 0.86, h * 0.5, d * 0.86), "owoc_ciemny", "matowy", segm=12)
        # łuski-romby: małe obrócone kwadraty na przodzie i bokach owocu
        for rzad, y in enumerate((-0.32, -0.04, 0.24)):
            for i in range(-2, 3):
                a = math.radians(i * 28 + (14 if rzad % 2 else 0))
                r = (w / 2) * math.sqrt(max(0.0, 1 - (y / (h / 2)) ** 2)) - 0.02
                if abs(i) == 0 and rzad == 1:
                    continue                                           # buzia
                p.blok("Luska", (r * math.sin(a), y, r * math.cos(a) * d / w), (0.13, 0.13, 0.04), "luska", "matowy",
                       rot=(0, math.degrees(a), 45), faza=0.0)
        z = d / 2
        oczy(p, 0.2, 0.08, z - 0.06, szer=0.17, wys=0.23)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.33, -0.08, z - 0.12), (0.13, 0.07, 0.04), "rumieniec", "matowy",
                   rot=(0, zn * 28, 0), faza=0.0)
        p.blok("Buzia", (0, -0.1, z - 0.02), (0.14, 0.05, 0.04), "buzia", "matowy", faza=0.0)
    with p.na("Korona", od="staw"):
        p.walec("Korona nasada", (0, 0.06, 0), (0.42, 0.14, 0.42), "lisc", "matowy", segm=8, faza=0.0)
        for i in range(6):                                             # sześć sztywnych liści w pióropuszu
            a = math.radians(i * 60 + 15)
            pochyl = 22 if i % 2 else 12
            dl = 0.62 if i % 2 else 0.8
            with p.uklad(pos=(0.08 * math.cos(a), 0.08, 0.08 * math.sin(a)), obrot=(0, -math.degrees(a) + 90, 0)):
                p.klin("Lisc korony", (0, dl / 2, 0.1), (0.16, dl, 0.22), "lisc" if i % 2 else "lisc_jasny", "matowy",
                       rot=(pochyl, 0, 0), faza=0.0)
        p.klin("Lisc szczyt", (0, 0.5, 0), (0.14, 0.86, 0.2), "lisc_jasny", "matowy", faza=0.0)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka" + s, od="srodek"):
            p.blok("Listek reka", (0, 0, 0), (0.36, 0.08, 0.2), "lisc", "matowy", rot=(0, 0, -zn * 20), faza=0.02)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Noga", (0, 0.04, 0), (0.2, 0.4, 0.22), "noga", "matowy", faza=0.04)
            p.blok("Stopka", (0, -0.17, 0.07), (0.26, 0.1, 0.36), "lisc", "matowy", faza=0.03)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Korona", (0, 1.0, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = ["Łuski to płaskie romby na powierzchni kuli — z bliska widać, że leżą na owocu, nie są w nim wycięte."]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.025, 0), czestosc=2)
    k.cykl("Tulow", "obrot", (0, 0, 3), czestosc=1)
    k.cykl("Korona", "obrot", (0, 0, 7), czestosc=2, faza=0.2)
    k.cykl("RekaL", "obrot", (0, 0, 10), czestosc=1)
    k.cykl("RekaP", "obrot", (0, 0, -10), czestosc=1, faza=0.2)

    k = p.klip("chod", 20, petla=True)
    k.cykl("NogaL", "obrot", (34, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (34, 0, 0), czestosc=1, faza=0.5)
    k.cykl("Tulow", "przes", (0, 0.06, 0), czestosc=2, srodek=(0, 0.05, 0))
    k.cykl("Tulow", "obrot", (3, 0, 6), czestosc=1)
    k.cykl("Korona", "obrot", (6, 0, 10), czestosc=2, faza=0.25)
    k.cykl("RekaL", "obrot", (-28, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaP", "obrot", (-28, 0, 0), czestosc=1)

    def rece(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Reka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Reka" + s, obrot=(0, 0, zn * 70))
            k.klucz(koniec, "Reka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Korona", przes=(0, 0, 0))
        k.klucz(szczyt, "Korona", przes=(0, 0.18, 0))
        k.klucz(szczyt + 5, "Korona", przes=(0, -0.04, 0))
        k.klucz(koniec, "Korona", przes=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.75, dodatki=lambda k: rece(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.0, wyskok=0.9, dodatki=lambda k: rece(k, 12, 30))
