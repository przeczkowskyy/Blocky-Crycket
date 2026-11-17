# -*- coding: utf-8 -*-
"""PAŁKUŚ — pet pospolity z jajka Bagna (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Duszek pałki wodnej (ok. 2,7 studa): na zielonej łodyżce stoi brązowa, aksamitna kolba-walec z buzią, na jej czubku
cienki szpic i trzy kłaczki puchu, z boków zwisają długie liście-rączki, a nóżki to dwa listki. Sylwetka: wąska,
wysoka kolba na łodyżce — inna niż okrągły Żołędziak (szeroki żołądź w czapeczce) i niż przysadziste potwory Bagna.

    python -B swiat/postacie/przebuduj.py palkus --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X): Root > Tulow (łodyżka) > {Kolba > Szpic, RekaL, RekaP, NogaL, NogaP}
Klipy: spoczynek, chod (drobne kroczki z kołysaniem kolby), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "palkus"

PALETA = {
    "kolba": "7A4B2A", "kolba_ciemna": "5A3520", "lodyga": "6FA84A", "lisc": "5E9B3E", "lisc_ciemny": "467A2E",
    "puch": "F2E8D0", "rumieniec": "F08C8C", "buzia": "3A2416",
}

Y_TULOWIA = 0.6       # wierzch nóżek, dół łodyżki
Y_KOLBY = 1.02        # spód kolby
KOLBA = (0.76, 1.3)   # średnica, wysokość


def zbuduj():
    p = Postac(ID, "Pałkuś", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    d, h = KOLBA
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=(0.3, Y_KOLBY - Y_TULOWIA, 0.3),
           srodek=(0, (Y_KOLBY - Y_TULOWIA) / 2, 0))
    p.kosc("Kolba", "Tulow", staw=(0, Y_KOLBY, 0), czesc=(d, h, d), srodek=(0, h / 2, 0))
    p.kosc("Szpic", "Kolba", staw=(0, Y_KOLBY + h, 0), czesc=(0.14, 0.42, 0.14), srodek=(0, 0.2, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Reka" + s, "Kolba", staw=(zn * 0.36, Y_KOLBY + 0.5, 0.02), czesc=(0.1, 0.86, 0.28),
               srodek=(zn * 0.24, -0.3, 0))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.17, Y_TULOWIA, 0), czesc=(0.26, 0.6, 0.36), srodek=(0, -0.3, 0.04))

    with p.na("Tulow", od="srodek"):
        p.walec("Lodyzka", (0, 0, 0), (0.26, Y_KOLBY - Y_TULOWIA + 0.06, 0.26), "lodyga", "matowy", segm=8, faza=0.0)
    with p.na("Kolba", od="srodek"):
        p.walec("Kolba", (0, 0, 0), (d, h, d), "kolba", "matowy", segm=12, faza=0.08)
        p.walec("Kolba spod", (0, -h / 2 - 0.04, 0), (d * 0.78, 0.1, d * 0.78), "kolba_ciemna", "matowy", segm=12, faza=0.0)
        p.walec("Kolba wierzch", (0, h / 2 + 0.04, 0), (d * 0.78, 0.1, d * 0.78), "kolba_ciemna", "matowy", segm=12,
                faza=0.0)
        z = d / 2                                                      # przód walca
        oczy(p, 0.16, 0.16, z - 0.01, szer=0.16, wys=0.24)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.24, -0.04, z - 0.05), (0.12, 0.07, 0.04), "rumieniec", "matowy", faza=0.0)
        p.blok("Buzia", (0, -0.06, z + 0.01), (0.12, 0.05, 0.04), "buzia", "matowy", faza=0.0)
    with p.na("Szpic", od="staw"):
        p.walec("Szpic", (0, 0.2, 0), (0.1, 0.42, 0.1), "lodyga", "matowy", rot=(0, 0, 6), segm=6, faza=0.0)
        for i in range(3):                                             # kłaczki puchu przy szpicu
            a = math.radians(i * 120 + 30)
            p.kula("Puch", (0.16 * math.cos(a), 0.06, 0.16 * math.sin(a)), (0.2, 0.16, 0.2), "puch", "matowy", segm=8)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka" + s, od="srodek"):
            p.blok("Lisc reka", (0, 0, 0), (0.08, 0.86, 0.24), "lisc", "matowy", rot=(0, 0, zn * 24), faza=0.02)
            p.blok("Lisc reka zylka", (zn * 0.012, 0.02, 0.0), (0.09, 0.66, 0.04), "lisc_ciemny", "matowy",
                   rot=(0, 0, zn * 24), faza=0.0)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Lisc noga", (0, 0.02, 0), (0.2, 0.56, 0.28), "lisc", "matowy", faza=0.04)
            p.blok("Stopka", (0, -0.25, 0.1), (0.28, 0.1, 0.46), "lisc_ciemny", "matowy", faza=0.03)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Szpic", (0, 0.6, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = ["Liście-rączki są płaskie (0,08) — z boku cienkie kreski."]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Kolba", "obrot", (0, 0, 4), czestosc=1)
    k.cykl("Szpic", "obrot", (0, 0, 10), czestosc=2, faza=0.2)
    k.cykl("RekaL", "obrot", (0, 0, 8), czestosc=1)
    k.cykl("RekaP", "obrot", (0, 0, -8), czestosc=1, faza=0.2)
    k.cykl("Tulow", "przes", (0, 0.025, 0), czestosc=2)

    k = p.klip("chod", 20, petla=True)
    k.cykl("NogaL", "obrot", (34, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (34, 0, 0), czestosc=1, faza=0.5)
    k.cykl("Tulow", "przes", (0, 0.06, 0), czestosc=2, srodek=(0, 0.06, 0))
    k.cykl("Kolba", "obrot", (4, 0, 7), czestosc=1)
    k.cykl("RekaL", "obrot", (-24, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaP", "obrot", (-24, 0, 0), czestosc=1)
    k.cykl("Szpic", "obrot", (0, 0, 12), czestosc=2, faza=0.3)

    def rece(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Reka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Reka" + s, obrot=(0, 0, zn * 110))
            k.klucz(koniec, "Reka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Szpic", obrot=(0, 0, 0))
        k.klucz(szczyt, "Szpic", obrot=(0, 0, 25))
        k.klucz(szczyt + 6, "Szpic", obrot=(0, 0, -15))
        k.klucz(koniec, "Szpic", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.75, dodatki=lambda k: rece(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.1, wyskok=0.95, dodatki=lambda k: rece(k, 12, 30))
