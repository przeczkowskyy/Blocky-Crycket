# -*- coding: utf-8 -*-
"""LENIWCZYK — pet zwykły z jajka Dżungli (próba swiat/pety_proba, 18.11.2026; status: propozycja, własny projekt).

Mały leniwiec (ok. 1,9 studa): kudłaty, piaskowobrązowy tułów, okrągła jasna buzia z ciemnymi „opaskami” wokół oczu
i błogim uśmiechem, bardzo długie przednie łapy z trzema jasnymi pazurkami, krótkie tylne łapki, na szyi szalik
z liany z listkami, za uchem czerwony kwiat. Chodzi pochylony, wolno, długie łapy prawie sięgają ziemi. Sylwetka:
przygarbiona kulka z długimi rękami — inna niż żółwik Nenufarek, ślimak lasu i małpa-siłacz Dżungli (krępa, z kokosami).

    python -B swiat/postacie/przebuduj.py leniwczyk --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X): Root > Tulow > {Glowa > Kwiat, RekaL, RekaP, NogaL, NogaP}
Klipy: spoczynek (drzemka: głowa opada i wraca), chod (powolne człapanie na tylnych łapkach), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "leniwczyk"

PALETA = {
    "futro": "9C7A54", "futro_ciemne": "6E5236", "buzia": "E8D5B0", "opaska": "4A3424", "pazur": "F2E6C8",
    "liana": "3E7D2E", "lisc": "6CCB4A", "kwiat": "E5392B", "kwiat_srodek": "FFD84A", "nos": "2A1A10",
}

Y_TULOWIA = 0.5
TULOW = (1.0, 0.95, 0.9)
GLOWA = (0.82, 0.72, 0.7)


def zbuduj():
    p = Postac(ID, "Leniwczyk", typ="stwor", skala=1.0, faza=0.08, paleta=PALETA)
    w, h, d = TULOW
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, h / 2, -0.05))
    p.kosc("Glowa", "Tulow", staw=(0, Y_TULOWIA + h - 0.05, 0.22), czesc=GLOWA, srodek=(0, 0.3, 0.12))
    p.kosc("Kwiat", "Glowa", staw=(0.3, Y_TULOWIA + h + 0.55, 0.2), czesc=(0.36, 0.2, 0.36), srodek=(0, 0.06, 0))
    for s, zn in (("L", 1), ("P", -1)):
        # długie przednie łapy wiszą z barków prawie do ziemi
        p.kosc("Reka" + s, "Tulow", staw=(zn * 0.5, Y_TULOWIA + 0.78, 0.18), czesc=(0.24, 1.05, 0.26),
               srodek=(zn * 0.06, -0.5, 0.06))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.26, Y_TULOWIA + 0.05, -0.05), czesc=(0.28, 0.5, 0.32),
               srodek=(0, -0.22, 0.04))

    with p.na("Tulow", od="srodek"):
        p.kula("Tulow", (0, 0, 0), TULOW, "futro", "matowy", segm=12)
        p.kula("Brzuch", (0, -0.08, d / 2 - 0.16), (0.62, 0.62, 0.3), "futro_ciemne", "matowy", segm=10)
        for zn in (1, -1):                                             # kudły na bokach
            p.blok("Kudel", (zn * 0.46, 0.05, -0.05), (0.12, 0.42, 0.5), "futro_ciemne", "matowy",
                   rot=(0, 0, zn * 12), faza=0.04)
        # szalik z liany z listkami
        p.walec("Liana szalik", (0, h / 2 - 0.08, 0.04), (0.92, 0.14, 0.84), "liana", "matowy", segm=10, faza=0.0)
        for zn in (1, -1):
            p.blok("Listek szalika", (zn * 0.24, h / 2 - 0.16, d / 2 - 0.02), (0.22, 0.06, 0.14), "lisc", "matowy",
                   rot=(0, 0, zn * 30), faza=0.0)
    with p.na("Glowa", od="srodek"):
        gw, gh, gd = GLOWA
        z = gd / 2
        p.kula("Glowa", (0, 0, 0), GLOWA, "futro", "matowy", segm=12)
        p.kula("Buzia", (0, -0.04, z - 0.12), (0.64, 0.52, 0.3), "buzia", "matowy", segm=12)
        for zn, s in ((1, "L"), (-1, "P")):                            # ciemne opaski skośnie w dół, ku uszom
            p.blok("Opaska " + s, (zn * 0.17, 0.02, z + 0.01), (0.3, 0.13, 0.05), "opaska", "matowy",
                   rot=(0, 0, -zn * 18), faza=0.03)
        oczy(p, 0.14, 0.04, z + 0.02, szer=0.11, wys=0.12)
        p.blok("Nos", (0, -0.1, z + 0.04), (0.14, 0.08, 0.05), "nos", "polysk", faza=0.02)
        p.blok("Usmiech", (0, -0.2, z + 0.02), (0.2, 0.035, 0.04), "nos", "matowy", faza=0.0)
    with p.na("Kwiat", od="staw"):
        for i in range(5):
            a = math.radians(i * 72)
            p.blok("Platek", (0.11 * math.cos(a), 0.05, 0.11 * math.sin(a)), (0.18, 0.06, 0.13), "kwiat", "matowy",
                   rot=(0, -math.degrees(a), 18), faza=0.0)
        p.blok("Precik", (0, 0.11, 0), (0.05, 0.16, 0.05), "kwiat_srodek", "matowy", faza=0.0)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka" + s, od="srodek"):
            p.blok("Reka", (0, 0.04, 0), (0.22, 0.96, 0.24), "futro", "matowy", faza=0.08)
            for i, dx in enumerate((-0.07, 0.0, 0.07)):                # trzy pazurki
                p.blok("Pazur", (dx, -0.5, 0.1), (0.05, 0.16, 0.06), "pazur", "matowy", rot=(-30, 0, 0), faza=0.0)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Noga", (0, 0.04, 0), (0.26, 0.42, 0.3), "futro_ciemne", "matowy", faza=0.06)
            p.blok("Stopka", (0, -0.2, 0.08), (0.28, 0.1, 0.38), "futro_ciemne", "matowy", faza=0.03)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 0.95, 0.1))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = ["Futro to gładkie elipsoidy z dwoma płaskimi kudłami — z bliska leniwiec jest raczej pluszowy niż kudłaty."]


def _klipy(p):
    k = p.klip("spoczynek", 90, petla=True)                       # drzemka: głowa wolno opada i wraca
    k.cykl("Glowa", "obrot", (12, 0, 4), czestosc=1)
    k.cykl("Tulow", "przes", (0, 0.02, 0), czestosc=2)
    k.cykl("RekaL", "obrot", (6, 0, 4), czestosc=1, faza=0.1)
    k.cykl("RekaP", "obrot", (6, 0, -4), czestosc=1, faza=0.3)
    k.cykl("Kwiat", "obrot", (0, 0, 8), czestosc=2)

    k = p.klip("chod", 30, petla=True)                            # powoli: dłuższy krok, mały podskok
    k.cykl("NogaL", "obrot", (26, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (26, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaL", "obrot", (22, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaP", "obrot", (22, 0, 0), czestosc=1)
    k.cykl("Tulow", "obrot", (4, 0, 6), czestosc=1, srodek=(6, 0, 0))
    k.cykl("Tulow", "przes", (0, 0.04, 0), czestosc=2, srodek=(0, 0.02, 0))
    k.cykl("Glowa", "obrot", (4, 6, 0), czestosc=1, faza=0.2)

    def rece(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Reka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Reka" + s, obrot=(-150, 0, zn * 20))         # obie łapy w górę
            k.klucz(koniec, "Reka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Glowa", obrot=(0, 0, 0))
        k.klucz(szczyt, "Glowa", obrot=(-12, 0, 0))
        k.klucz(koniec, "Glowa", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.6, dodatki=lambda k: rece(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=0.95, wyskok=0.85, dodatki=lambda k: rece(k, 12, 30))
