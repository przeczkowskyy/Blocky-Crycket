# -*- coding: utf-8 -*-
"""TUKANIK — pet rzadki z jajka Dżungli (próba swiat/pety_proba, 18.11.2026; status: propozycja, własny projekt).

Pisklę tukana (ok. 2,1 studa): okrągły, czarny tułów z kremowożółtym śliniaczkiem, głowa z turkusową obwódką oczu,
ogromny dziób — zielony u nasady, pomarańczowy, z czerwonym czubkiem — krótkie skrzydełka z turkusowym brzegiem,
niebieskie nóżki, ogonek z trzech piór i czerwony kwiatek-czubek na głowie. Skacze obunóż. Sylwetka: kula z wielkim
dziobem — inna niż sówka Świetlikówka (okrągła, z brzuszkiem-latarenką) i niż latające Ważeczka i Ognik.

    python -B swiat/postacie/przebuduj.py tukanik --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X): Root > Tulow > {Glowa > Dziob, SkrzydloL, SkrzydloP, NogaL, NogaP, Ogon}
Klipy: spoczynek (kiwanie dziobem), chod (podskoki obunóż), radosc (trzepot skrzydełek), wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "tukanik"

PALETA = {
    "pioro": "1F1F24", "pioro_jasne": "34343C", "sliniaczek": "FFE7A0", "obwodka": "2EC4B6", "dziob": "F28C1E",
    "dziob_nasada": "6CCB4A", "dziob_czubek": "E5392B", "dziob_kreska": "1F1F24", "noga": "4FA3D9",
    "kwiat": "E5392B", "kwiat_srodek": "FFD84A",
}

Y_TULOWIA = 0.48
TULOW = (1.0, 1.0, 0.95)
GLOWA = (0.78, 0.72, 0.74)


def zbuduj():
    p = Postac(ID, "Tukanik", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    w, h, d = TULOW
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, h / 2, 0))
    p.kosc("Glowa", "Tulow", staw=(0, Y_TULOWIA + h - 0.12, 0.12), czesc=GLOWA, srodek=(0, 0.3, 0.05))
    p.kosc("Dziob", "Glowa", staw=(0, Y_TULOWIA + h + 0.12, 0.45), czesc=(0.42, 0.42, 0.95), srodek=(0, -0.04, 0.45))
    p.kosc("Ogon", "Tulow", staw=(0, Y_TULOWIA + 0.35, -0.42), czesc=(0.4, 0.12, 0.5), srodek=(0, 0, -0.22))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Skrzydlo" + s, "Tulow", staw=(zn * 0.48, Y_TULOWIA + 0.72, -0.02), czesc=(0.14, 0.56, 0.6),
               srodek=(zn * 0.04, -0.24, -0.04))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.2, Y_TULOWIA + 0.06, 0.04), czesc=(0.14, 0.5, 0.3),
               srodek=(0, -0.24, 0.05))

    with p.na("Tulow", od="srodek"):
        p.kula("Tulow", (0, 0, 0), TULOW, "pioro", "zwykly", segm=14)
        p.kula("Sliniaczek", (0, 0.08, d / 2 - 0.18), (0.66, 0.62, 0.34), "sliniaczek", "matowy", segm=12)
        p.kula("Brzuszek", (0, -0.3, d / 2 - 0.26), (0.5, 0.3, 0.2), "pioro_jasne", "matowy", segm=8)
    with p.na("Glowa", od="srodek"):
        gw, gh, gd = GLOWA
        z = gd / 2
        p.kula("Glowa", (0, 0, 0), GLOWA, "pioro", "zwykly", segm=14)
        for zn, s in ((1, "L"), (-1, "P")):                            # turkusowa obwódka oka (oko z boku dzioba)
            p.blok("Obwodka " + s, (zn * 0.28, 0.16, z - 0.14), (0.24, 0.26, 0.06), "obwodka", "matowy",
                   rot=(0, zn * 30, 0), faza=0.03)
        oczy(p, 0.28, 0.16, z - 0.1, szer=0.13, wys=0.16)
        with p.uklad(pos=(0, gh / 2 + 0.02, -0.02)):                   # czubek: czerwony kwiatek
            for i in range(5):
                a = math.radians(i * 72)
                p.blok("Platek", (0.1 * math.cos(a), 0.04, 0.1 * math.sin(a)), (0.16, 0.06, 0.12), "kwiat", "matowy",
                       rot=(0, -math.degrees(a), 20), faza=0.0)
            p.blok("Precik", (0, 0.1, 0), (0.06, 0.14, 0.06), "kwiat_srodek", "matowy", faza=0.0)
    with p.na("Dziob", od="staw"):
        # wielki dziób: nasada zielona, środek pomarańczowy, czubek czerwony, czarna kreska wzdłuż
        p.blok("Dziob nasada", (0, 0, 0.12), (0.4, 0.4, 0.24), "dziob_nasada", "matowy", faza=0.08)
        p.blok("Dziob", (0, -0.02, 0.5), (0.36, 0.36, 0.56), "dziob", "polysk", faza=0.1)
        p.blok("Dziob czubek", (0, -0.08, 0.86), (0.26, 0.24, 0.2), "dziob_czubek", "polysk", rot=(14, 0, 0), faza=0.06)
        p.blok("Dziob kreska", (0, -0.12, 0.5), (0.38, 0.03, 0.62), "dziob_kreska", "matowy", faza=0.0)
    with p.na("Ogon", od="staw"), p.uklad(obrot=(-20, 0, 0)):
        for i, a in enumerate((-18, 0, 18)):
            p.blok("Pioro ogona", (0.08 * (i - 1), 0, -0.24), (0.14, 0.06, 0.5), "pioro", "matowy",
                   rot=(0, a, 0), faza=0.02)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Skrzydlo" + s, od="srodek"):
            p.blok("Skrzydlo", (0, 0, 0), (0.12, 0.52, 0.58), "pioro", "zwykly", rot=(0, 0, zn * 6), faza=0.08)
            p.blok("Skrzydlo brzeg", (zn * 0.01, -0.22, -0.02), (0.13, 0.1, 0.52), "obwodka", "matowy",
                   rot=(0, 0, zn * 6), faza=0.02)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Noga", (0, 0.04, 0), (0.1, 0.4, 0.1), "noga", "matowy", faza=0.0)
            p.blok("Stopka", (0, -0.2, 0.08), (0.22, 0.08, 0.3), "noga", "matowy", faza=0.02)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 1.0, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = ["Dziób to trzy klocki (bez zakrzywienia) — z boku prosty, nie łukowaty jak u prawdziwego tukana."]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Glowa", "obrot", (8, 10, 0), czestosc=1)
    k.cykl("Tulow", "przes", (0, 0.02, 0), czestosc=2)
    k.cykl("Ogon", "obrot", (0, 14, 0), czestosc=2)
    k.cykl("SkrzydloL", "obrot", (0, 0, 5), czestosc=2)
    k.cykl("SkrzydloP", "obrot", (0, 0, -5), czestosc=2)

    k = p.klip("chod", 16, petla=True)                            # podskoki obunóż
    k.klucz(0, "Tulow", przes=(0, 0, 0), obrot=(0, 0, 0))
    k.klucz(4, "Tulow", przes=(0, 0.22, 0), obrot=(-6, 0, 0))
    k.klucz(8, "Tulow", przes=(0, 0, 0), obrot=(4, 0, 0))
    k.klucz(12, "Tulow", przes=(0, 0.22, 0), obrot=(-6, 0, 0))
    k.klucz(16, "Tulow", przes=(0, 0, 0), obrot=(0, 0, 0))
    for s, zn in (("L", 1), ("P", -1)):
        k.cykl("Noga" + s, "obrot", (18, 0, 0), czestosc=2)
        k.cykl("Skrzydlo" + s, "obrot", (0, 0, zn * 14), czestosc=2, faza=0.25)
    k.cykl("Glowa", "obrot", (6, 0, 0), czestosc=2, faza=0.4)
    k.cykl("Ogon", "obrot", (12, 0, 0), czestosc=2, faza=0.2)

    def skrzydla(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Skrzydlo" + s, obrot=(0, 0, 0))
            for i, f in enumerate(range(3, koniec - 2, 3)):              # trzepot
                k.klucz(f, "Skrzydlo" + s, obrot=(0, 0, zn * (70 if i % 2 == 0 else 30)))
            k.klucz(koniec, "Skrzydlo" + s, obrot=(0, 0, 0))
        k.klucz(0, "Dziob", obrot=(0, 0, 0))
        k.klucz(szczyt, "Dziob", obrot=(-25, 0, 0))
        k.klucz(koniec, "Dziob", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.8, dodatki=lambda k: skrzydla(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.0, wyskok=0.95, dodatki=lambda k: skrzydla(k, 12, 30))
