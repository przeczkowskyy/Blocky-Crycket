# -*- coding: utf-8 -*-
"""WAŻECZKA — pet rzadki z jajka Bagna (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Mała ważka (ok. 2,4 studa długości, unosi się ok. 1,3 studa nad ziemią): turkusowa głowa z wielkimi oczami-kopułami,
krótki tułów, długi odwłok w paski zakończony różowym „ogonkiem”, cztery szklistobłękitne skrzydła w poziomie.
Sylwetka: pozioma kreska ze skrzydłami w krzyż — jedyny pet „w powietrzu” bez nóg (las ma sówkę z głową-tarczą,
Bagno — przysadziste potwory).

    python -B swiat/postacie/przebuduj.py wazeczka --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa, Odwlok > Ogon, SkrzydloPrzodL/P, SkrzydloTylL/P}
Klipy: spoczynek (zawisa i lekko faluje odwłokiem, skrzydła drgają), chod (szybkie bzyczenie, pochylona w lot),
radosc (pętla w powietrzu), wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie

ID = "wazeczka"

PALETA = {
    "pancerz": "2FBFA8", "pancerz_ciemny": "1E8A7A", "pancerz_jasny": "7FE6CF", "pasek": "15584F",
    "oko": "3FD6FF", "oko_ciemne": "1A6E9E", "skrzydlo": "CDEFFF", "zylka": "8CC8E6", "ogonek": "FF7FB0",
    "nozki": "1E3A36",
}

Y_LOTU = 1.3          # wysokość tułowia nad ziemią (unosi się)
SKRZYDLA = [("PrzodL", 1, 0.12), ("PrzodP", -1, 0.12), ("TylL", 1, -0.24), ("TylP", -1, -0.24)]


def zbuduj():
    p = Postac(ID, "Ważeczka", typ="stwor", skala=1.0, faza=0.06, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_LOTU, 0), czesc=(0.5, 0.5, 0.62), srodek=(0, 0, 0))
    p.kosc("Glowa", "Tulow", staw=(0, Y_LOTU + 0.05, 0.3), czesc=(0.78, 0.62, 0.6), srodek=(0, 0.06, 0.28))
    p.kosc("Odwlok", "Tulow", staw=(0, Y_LOTU, -0.3), czesc=(0.26, 0.26, 0.9), srodek=(0, 0, -0.45))
    p.kosc("Ogon", "Odwlok", staw=(0, Y_LOTU, -1.2), czesc=(0.2, 0.2, 0.62), srodek=(0, 0, -0.31))
    for s, zn, z in SKRZYDLA:
        p.kosc("Skrzydlo" + s, "Tulow", staw=(zn * 0.22, Y_LOTU + 0.24, z), czesc=(1.3, 0.04, 0.34),
               srodek=(zn * 0.65, 0, 0))

    with p.na("Tulow", od="srodek"):
        p.blok("Tulow", (0, 0, 0), (0.5, 0.5, 0.62), "pancerz", faza=0.12)
        p.blok("Tulow grzbiet", (0, 0.22, 0), (0.34, 0.1, 0.5), "pancerz_jasny", "matowy", faza=0.03)
        for zn in (1, -1):                                       # trzy pary maleńkich nóżek pod tułowiem
            for z in (0.16, 0.0, -0.16):
                p.blok("Nozka", (zn * 0.16, -0.32, z), (0.05, 0.22, 0.05), "nozki", "matowy",
                       rot=(0, 0, zn * 20), faza=0.0)
    with p.na("Glowa", od="srodek"):
        w, h, d = 0.78, 0.62, 0.6
        z = d / 2
        p.blok("Glowa", (0, -0.04, 0), (0.56, 0.5, 0.6), "pancerz", faza=0.14)
        for zn, s in ((1, "L"), (-1, "P")):                      # wielkie oczy-kopuły po bokach
            p.kula("Oko " + s, (zn * 0.24, 0.08, 0.06), (0.4, 0.44, 0.44), "oko", "polysk", segm=12)
            p.kula("Zrenica " + s, (zn * 0.26, 0.06, 0.24), (0.16, 0.2, 0.12), "oko_ciemne", "polysk", segm=8)
            p.blok("Blysk " + s, (zn * 0.2, 0.2, 0.25), (0.08, 0.08, 0.04), "bialy", "swiecacy", faza=0.0)
        p.blok("Buzia", (0, -0.17, z + 0.01), (0.14, 0.04, 0.04), "pasek", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Rumieniec", (zn * 0.17, -0.1, z + 0.01), (0.1, 0.05, 0.03), "ogonek", "matowy", faza=0.0)
    with p.na("Odwlok", od="srodek"):
        p.blok("Odwlok", (0, 0, 0), (0.26, 0.26, 0.9), "pancerz", faza=0.08)
        for z in (0.24, -0.04, -0.32):
            p.blok("Pasek", (0, 0, z), (0.28, 0.28, 0.08), "pasek", "matowy", faza=0.02)
    with p.na("Ogon", od="srodek"):
        p.blok("Ogon", (0, 0, 0.02), (0.2, 0.2, 0.58), "pancerz_ciemny", faza=0.06)
        p.blok("Ogonek", (0, 0.02, -0.32), (0.26, 0.16, 0.16), "ogonek", "matowy", faza=0.04)
    for s, zn, _z in SKRZYDLA:
        tyl = s.startswith("Tyl")
        with p.na("Skrzydlo" + s, od="srodek"), p.uklad(obrot=(0, zn * (-12 if tyl else 10), 0)):
            p.blok("Skrzydlo", (0, 0, 0), (1.3, 0.04, 0.34 if not tyl else 0.3), "skrzydlo", "polysk", faza=0.0)
            p.blok("Skrzydlo zylka", (0, 0.025, 0), (1.2, 0.02, 0.04), "zylka", "matowy", faza=0.0)
            p.blok("Skrzydlo plamka", (zn * 0.5, 0.025, 0), (0.16, 0.02, 0.16), "pancerz_jasny", "matowy", faza=0.0)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_LOTU, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 0.6, 0.28))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 4)
    return p


SLABOSCI = [
    "Skrzydła to płaskie klocki „polysk” — w Robloksie bez przezroczystości (klocki rigu jej nie niosą).",
    "Unosi się stale ok. 1,3 studa nad ziemią: cień pod nią to jedyny ślad podłoża.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.12, 0), czestosc=1)
    k.cykl("Tulow", "obrot", (3, 0, 2), czestosc=1, faza=0.25)
    k.cykl("Odwlok", "obrot", (6, 0, 0), czestosc=1, faza=0.15)
    k.cykl("Ogon", "obrot", (9, 0, 0), czestosc=1, faza=0.3)
    k.cykl("Glowa", "obrot", (0, 10, 0), czestosc=1)
    for s, zn, _z in SKRZYDLA:
        k.cykl("Skrzydlo" + s, "obrot", (0, 0, zn * 14), czestosc=6, faza=0.0 if "Przod" in s else 0.5)

    k = p.klip("chod", 20, petla=True)
    k.cykl("Tulow", "przes", (0, 0.08, 0), czestosc=2, srodek=(0, 0.15, 0))
    k.cykl("Tulow", "obrot", (2, 0, 3), czestosc=1, srodek=(8, 0, 0))            # pochylona w lot
    k.cykl("Odwlok", "obrot", (5, 0, 0), czestosc=2, srodek=(-6, 0, 0))
    k.cykl("Ogon", "obrot", (6, 0, 0), czestosc=2, faza=0.2, srodek=(-5, 0, 0))
    for s, zn, _z in SKRZYDLA:
        k.cykl("Skrzydlo" + s, "obrot", (0, 0, zn * 26), czestosc=5, faza=0.0 if "Przod" in s else 0.5)

    def dodatki(k, szczyt, koniec):
        for s, zn, _z in SKRZYDLA:
            k.klucz(0, "Skrzydlo" + s, obrot=(0, 0, 0))
            for f in range(3, koniec, 3):
                k.klucz(f, "Skrzydlo" + s, obrot=(0, 0, zn * (30 if (f // 3) % 2 else -20)))
            k.klucz(koniec, "Skrzydlo" + s, obrot=(0, 0, 0))
        k.klucz(0, "Odwlok", obrot=(0, 0, 0))
        k.klucz(szczyt, "Odwlok", obrot=(-25, 0, 0))
        k.klucz(koniec, "Odwlok", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.9, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.4, wyskok=0.9, dodatki=lambda k: dodatki(k, 12, 30))
