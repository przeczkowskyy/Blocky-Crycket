# -*- coding: utf-8 -*-
"""PERŁOWA WYDRA — pet legendarny z jajka Bagna (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Wydra stojąca na tylnych łapkach (ok. 2,7 studa z perłą): smukłe, czekoladowe ciało, kremowy pyszczek z wąsami
i noskiem, okrągłe uszka, długi płaski ogon-ster, a w przednich łapkach — przed brzuszkiem — otwarta różowa
muszla ze świecącą perłą. Na głowie wianuszek z trzech płatków grzybienia ze złotym środkiem, na szyi sznur małych
pereł. Sylwetka: pionowa, smukła, z długim ogonem — inna niż jelonek (rogi, cztery nogi) i niż żaby Bagna.
Legendarna, więc ma najwięcej blasku: perła i naszyjnik z pereł (Neon), złoty błysk i środek wianka (metal),
muszla (połysk).

    python -B swiat/postacie/przebuduj.py perlowa_wydra --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa, LapaL, LapaP, NogaL, NogaP, Ogon > Ogon2, Perla}
Klipy: spoczynek (podrzuca perłę i łapie, ogon się wije), chod (kołysze się na krótkich łapkach, perła płynie
przed nią), radosc, wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "perlowa_wydra"

PALETA = {
    "futro": "7A4A2E", "futro_ciemne": "5A3420", "futro_jasne": "9A6440", "pyszczek": "F0DEC0", "nos": "2A1A14",
    "perla": "FFE6F4", "muszla": "F2D2DC", "muszla_ciemna": "D8A6B8", "obrecz": "F2C230", "wianek": "F59AC0",
    "wianek_jasny": "FFC6DD",
    "wasy": "F4F1EA", "rumieniec": "F08C8C", "naszyjnik": "EDE6FF",
}

TULOW = (0.92, 1.2, 0.78)
Y_TULOWIA = 0.62      # staw tułowia (biodra)


def zbuduj():
    p = Postac(ID, "Perłowa Wydra", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, 0.55, 0))
    p.kosc("Glowa", "Tulow", staw=(0, 1.72, 0.04), czesc=(0.9, 0.78, 0.8), srodek=(0, 0.36, 0.04))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Lapa" + s, "Tulow", staw=(zn * 0.42, 1.52, 0.18), czesc=(0.24, 0.6, 0.24), srodek=(zn * 0.02, -0.26, 0.1))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.26, 0.5, 0.02), czesc=(0.32, 0.5, 0.42), srodek=(0, -0.25, 0.06))
    p.kosc("Ogon", "Tulow", staw=(0, 0.66, -0.3), czesc=(0.36, 0.2, 0.9), srodek=(0, -0.12, -0.44))
    p.kosc("Ogon2", "Ogon", staw=(0, 0.36, -1.16), czesc=(0.46, 0.14, 0.7), srodek=(0, -0.08, -0.32))
    p.kosc("Perla", "Tulow", staw=(0, 1.16, 0.62), czesc=(0.62, 0.5, 0.5), srodek=(0, 0, 0))

    with p.na("Tulow", od="srodek"):
        w, h, d = TULOW
        p.blok("Tulow", (0, 0, 0), TULOW, "futro", faza=0.2)
        p.blok("Brzuszek", (0, -0.06, d / 2 + 0.01), (0.6, 0.86, 0.06), "pyszczek", "matowy", faza=0.04)
        p.blok("Biodra", (0, -0.42, -0.04), (1.0, 0.4, 0.82), "futro", faza=0.14)
        for x in (-0.22, 0.0, 0.22):                                       # sznur pereł na szyi
            y = h / 2 - 0.1 - (0.06 if x == 0.0 else 0.0)
            p.kula("Naszyjnik perla", (x, y, d / 2 + 0.04 - abs(x) * 0.3), 0.15, "naszyjnik", "swiecacy", segm=8)
    with p.na("Glowa", od="srodek"):
        w, h, d = 0.9, 0.78, 0.8
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "futro", faza=0.22)
        p.blok("Pyszczek", (0, -0.16, z + 0.04), (0.56, 0.34, 0.16), "pyszczek", "matowy", faza=0.08)
        p.blok("Nosek", (0, -0.06, z + 0.13), (0.18, 0.12, 0.08), "nos", "polysk", faza=0.03)
        p.blok("Buzia", (0, -0.24, z + 0.125), (0.14, 0.04, 0.03), "nos", "matowy", faza=0.0)
        oczy(p, 0.22, 0.1, z, szer=0.17, wys=0.22)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.32, -0.12, z + 0.01), (0.12, 0.06, 0.04), "rumieniec", "matowy", faza=0.0)
            for i, (dy, kat) in enumerate(((-0.12, 8), (-0.2, -8))):
                p.blok("Was " + s, (zn * 0.42, dy, z + 0.1), (0.4, 0.025, 0.025), "wasy", "matowy",
                       rot=(0, 0, zn * kat), faza=0.0)
            p.kula("Ucho " + s, (zn * 0.38, h / 2 - 0.02, -0.08), (0.24, 0.22, 0.12), "futro_ciemne", "matowy", segm=8)
        # wianuszek: trzy płatki grzybienia ze złotym środkiem
        for i, (x, kat) in enumerate(((-0.2, 22), (0.0, 0), (0.2, -22))):
            p.blok("Wianek platek", (x, h / 2 + 0.08, 0.02), (0.18, 0.12, 0.26), "wianek" if i != 1 else "wianek_jasny",
                   "matowy", rot=(0, 0, kat), faza=0.03)
        p.kula("Wianek srodek", (0, h / 2 + 0.16, 0.02), 0.13, "obrecz", "metal", segm=8)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Lapa" + s, od="srodek"), p.uklad(obrot=(-38, 0, zn * 14)):   # łapki wyciągnięte ku perle
            p.blok("Lapa", (0, 0, 0), (0.24, 0.6, 0.24), "futro", faza=0.08)
            p.blok("Lapa dlon", (0, -0.28, 0), (0.26, 0.14, 0.26), "futro_ciemne", "matowy", faza=0.05)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Noga", (0, 0.04, -0.04), (0.32, 0.42, 0.36), "futro", faza=0.1)
            p.blok("Stopa", (0, -0.2, 0.08), (0.34, 0.12, 0.5), "futro_ciemne", "matowy", faza=0.04)
    with p.na("Ogon", od="srodek"), p.uklad(obrot=(-14, 0, 0)):            # ogon schodzi od bioder ku ziemi
        p.blok("Ogon", (0, 0, 0), (0.36, 0.2, 0.9), "futro_ciemne", faza=0.08)
    with p.na("Ogon2", od="srodek"), p.uklad(obrot=(-5, 0, 0)):
        p.blok("Ogon ster", (0, 0, 0), (0.46, 0.14, 0.7), "futro_ciemne", faza=0.07)
        p.blok("Ogon pasek", (0, 0.075, -0.05), (0.3, 0.02, 0.4), "futro_jasne", "matowy", faza=0.0)
    with p.na("Perla", od="srodek"):                                       # perła w otwartej muszli
        p.kula("Muszla dol", (0, -0.17, 0), (0.62, 0.16, 0.5), "muszla", "polysk", segm=12)
        with p.uklad(pos=(0, -0.12, -0.2), obrot=(62, 0, 0)):
            p.kula("Muszla gora", (0, 0, 0.22), (0.62, 0.12, 0.5), "muszla", "polysk", segm=12)
            for x in (-0.14, 0.0, 0.14):
                p.blok("Muszla prazek", (x, 0.06, 0.22), (0.04, 0.03, 0.4), "muszla_ciemna", "matowy", faza=0.0)
        p.kula("Perla", (0, 0.02, 0.02), 0.36, "perla", "swiecacy", segm=12)
        p.kula("Perla blask", (0.07, 0.11, 0.13), 0.1, "obrecz", "metal", segm=8)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 0.72, 0.04))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 10)
    return p


SLABOSCI = [
    "Muszla to dwie spłaszczone elipsoidy — z boku cienkie; perła świeci tylko materiałem Neon (bez światła).",
    "Wąsy są cienkie (0,025) — z daleka znikają.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.klucz(0, "Perla", przes=(0, 0, 0), obrot=(0, 0, 0))     # podrzuca perłę i łapie
    k.klucz(14, "Perla", przes=(0, 0.42, 0), obrot=(0, 180, 0))
    k.klucz(26, "Perla", przes=(0, 0, 0), obrot=(0, 360, 0))
    k.klucz(30, "Perla", przes=(0, -0.04, 0), obrot=(0, 360, 0))
    k.klucz(60, "Perla", przes=(0, 0, 0), obrot=(0, 360, 0))
    for s in ("L", "P"):
        k.klucz(0, "Lapa" + s, obrot=(0, 0, 0))
        k.klucz(8, "Lapa" + s, obrot=(-20, 0, 0))
        k.klucz(14, "Lapa" + s, obrot=(-28, 0, 0))
        k.klucz(26, "Lapa" + s, obrot=(-6, 0, 0))
        k.klucz(30, "Lapa" + s, obrot=(0, 0, 0))
        k.klucz(60, "Lapa" + s, obrot=(0, 0, 0))
    k.cykl("Glowa", "obrot", (-6, 0, 0), czestosc=1, faza=0.1)
    k.cykl("Tulow", "przes", (0, 0.03, 0), czestosc=2)
    k.cykl("Ogon", "obrot", (0, 10, 0), czestosc=1)
    k.cykl("Ogon2", "obrot", (0, 16, 0), czestosc=1, faza=0.2)

    k = p.klip("chod", 20, petla=True)
    k.cykl("NogaL", "obrot", (36, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (36, 0, 0), czestosc=1, faza=0.5)
    k.cykl("Tulow", "obrot", (0, 6, 6), czestosc=1)
    k.cykl("Tulow", "przes", (0, 0.06, 0), czestosc=2, srodek=(0, 0.05, 0))
    k.cykl("Glowa", "obrot", (0, -5, -5), czestosc=1)
    k.cykl("Ogon", "obrot", (0, 14, 0), czestosc=1, faza=0.2)
    k.cykl("Ogon2", "obrot", (0, 20, 0), czestosc=1, faza=0.4)
    k.cykl("Perla", "przes", (0, 0.08, 0), czestosc=2, faza=0.3)

    def dodatki(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Lapa" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Lapa" + s, obrot=(-150, 0, zn * 20))
            k.klucz(koniec, "Lapa" + s, obrot=(0, 0, 0))
        k.klucz(0, "Perla", przes=(0, 0, 0))
        k.klucz(szczyt, "Perla", przes=(0, 1.1, -0.3))
        k.klucz(koniec, "Perla", przes=(0, 0, 0))
        k.klucz(0, "Ogon", obrot=(0, 0, 0))
        k.klucz(szczyt, "Ogon", obrot=(30, 0, 0))
        k.klucz(koniec, "Ogon", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.8, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.3, wyskok=1.0, dodatki=lambda k: dodatki(k, 12, 30))
