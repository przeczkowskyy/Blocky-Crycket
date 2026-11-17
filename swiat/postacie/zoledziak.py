# -*- coding: utf-8 -*-
"""ŻOŁĘDZIAK — pet pospolity z leśnego jajka (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Pulchny żołądź na krótkich nóżkach (ok. 1,75 studa z ogonkiem): kanciasty orzech z jaśniejszym brzuszkiem i spiczastym
spodem, czapeczka w paski z daszkiem, ogonek z listkiem, patyczkowe rączki, duże błyszczące oczy i rumieńce.
Sylwetka: pionowa „kropla” — najmniejszy i najprostszy z piątki (pospolity = najskromniejszy).

    python -B swiat/postacie/przebuduj.py zoledziak --bez-filmow

Budowa (typ="stwor", 1 jednostka = 1 stud, patrzy w +Z, lewa = +X):
  Root > Tulow > {Czapka > Ogonek, RekaL, RekaP, NogaL, NogaP}
Klipy: spoczynek (pętla), chod (kaczy chód z podskokiem, pętla), radosc (podskok z obrotem), wyklucie (z jajka).
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "zoledziak"

PALETA = {
    "orzech": "C98A3E", "orzech_jasny": "E8BC72", "orzech_ciemny": "8E5A26",
    "czapka": "7A5230", "czapka_ciemna": "5A3B20", "czapka_jasna": "9A7046",
    "lisc": "6DB33F", "rumieniec": "F08C8C", "buzia": "5A2A18",
}

CIALO = (1.2, 1.0, 1.1)       # orzech: szer, wys, głęb
Y_STAW = 0.42                 # staw tułowia (nisko — kołysze się od spodu)
Y_SRODEK = 0.8                # środek orzecha nad ziemią


def zbuduj():
    p = Postac(ID, "Żołędziak", typ="stwor", skala=1.0, faza=0.08, paleta=PALETA)
    w, h, d = CIALO
    p.kosc("Tulow", "Root", staw=(0, Y_STAW, 0), czesc=CIALO, srodek=(0, Y_SRODEK - Y_STAW, 0))
    y_gora = Y_SRODEK + h / 2
    p.kosc("Czapka", "Tulow", staw=(0, y_gora - 0.08, 0), czesc=(1.45, 0.46, 1.35), srodek=(0, 0.2, 0))
    p.kosc("Ogonek", "Czapka", staw=(0, y_gora + 0.34, 0), czesc=(0.2, 0.4, 0.2), srodek=(0, 0.18, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Reka" + s, "Tulow", staw=(zn * (w / 2 + 0.02), Y_SRODEK + 0.02, 0.05), czesc=(0.14, 0.44, 0.14),
               srodek=(zn * 0.07, -0.18, 0))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.3, 0.3, 0.02), czesc=(0.36, 0.24, 0.46), srodek=(0, -0.18, 0.04))

    # ------------------------------------------------------------------ orzech
    with p.na("Tulow", od="srodek"):
        z = d / 2
        p.blok("Orzech", (0, 0, 0), CIALO, "orzech", faza=0.14)
        p.blok("Spod", (0, -h / 2 - 0.08, 0), (0.78, 0.24, 0.74), "orzech_ciemny", faza=0.08)
        p.blok("Czubek spodu", (0, -h / 2 - 0.22, 0), (0.34, 0.14, 0.32), "orzech_ciemny", faza=0.04)
        oczy(p, 0.3, 0.12, z, szer=0.2, wys=0.28)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.45, -0.06, z + 0.02), (0.18, 0.09, 0.04), "rumieniec", "matowy", faza=0.0)
        p.blok("Buzia", (0, -0.06, z + 0.03), (0.14, 0.06, 0.04), "buzia", "matowy", faza=0.0)

    # ------------------------------------------------------------------ czapeczka: kopułka z łuskami
    with p.na("Czapka", od="srodek"):
        p.blok("Czapka", (0, -0.04, 0), (1.45, 0.34, 1.35), "czapka", faza=0.1)
        p.blok("Kopula", (0, 0.18, 0), (1.12, 0.2, 1.04), "czapka", faza=0.08)
        p.blok("Szczyt", (0, 0.31, 0), (0.62, 0.1, 0.58), "czapka_jasna", faza=0.04)
        p.blok("Daszek", (0, -0.2, 0.02), (1.56, 0.1, 1.46), "czapka_ciemna", faza=0.04)
        # łuski: jasne kropki w szachownicę (dwa rzędy) — faktura kapelusza żołędzia
        for x, y in ((-0.48, 0.04), (0.0, 0.04), (0.48, 0.04), (-0.24, -0.1), (0.24, -0.1)):
            p.blok("Luska", (x, y, 0.69), (0.12, 0.09, 0.03), "czapka_jasna", "matowy", faza=0.0)
        for zn in (1, -1):
            for zz, y in ((-0.3, 0.04), (0.3, 0.04), (0.0, -0.1)):
                p.blok("Luska", (zn * 0.74, y, zz), (0.03, 0.09, 0.12), "czapka_jasna", "matowy", faza=0.0)

    # ------------------------------------------------------------------ ogonek z listkiem
    with p.na("Ogonek", od="staw"):
        p.blok("Ogonek", (0.02, 0.18, 0), (0.2, 0.4, 0.2), "czapka_ciemna", rot=(0, 0, -10), faza=0.04)
        p.blok("Listek", (0.3, 0.32, 0.0), (0.5, 0.05, 0.3), "lisc", "matowy", rot=(0, 25, 28), faza=0.0)

    # ------------------------------------------------------------------ rączki i nóżki
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka" + s, od="srodek"):
            p.blok("Raczka", (0, 0, 0), (0.14, 0.44, 0.14), "orzech_ciemny", rot=(0, 0, zn * 22), faza=0.03)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Nozka", (0, 0, 0), (0.36, 0.24, 0.46), "orzech_ciemny", faza=0.06)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_STAW, 0))
    p.zaczep("GlowaAttachment", "Czapka", (0, 0.75, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = [
    "Kości własne (nie R15) — klipy idą przez Motor6D w grze (prototyp z klocków).",
    "Brak nóg w klipie wyklucia: w jajku żołądź siedzi cały, nóżki są schowane w skorupce.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.03, 0), czestosc=2)
    k.cykl("Tulow", "obrot", (0, 0, 3), czestosc=1)
    k.cykl("Czapka", "obrot", (0, 0, -4), czestosc=1, faza=0.1)
    k.cykl("Ogonek", "obrot", (0, 0, 12), czestosc=2)
    k.cykl("RekaL", "obrot", (0, 0, 9), czestosc=1)
    k.cykl("RekaP", "obrot", (0, 0, -9), czestosc=1, faza=0.15)

    k = p.klip("chod", 20, petla=True)
    k.cykl("Tulow", "obrot", (0, 0, 9), czestosc=1)                              # kaczy chód
    k.cykl("Tulow", "przes", (0, 0.07, 0), czestosc=2, srodek=(0, 0.07, 0))      # podskok przy każdym kroku
    k.cykl("NogaL", "obrot", (32, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (32, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaL", "obrot", (-28, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaP", "obrot", (-28, 0, 0), czestosc=1)
    k.cykl("Czapka", "obrot", (0, 0, -6), czestosc=1, faza=0.1)
    k.cykl("Ogonek", "obrot", (0, 0, 16), czestosc=2, faza=0.2)

    def rece(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Reka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Reka" + s, obrot=(0, 0, zn * 120))
            k.klucz(koniec, "Reka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Czapka", obrot=(0, 0, 0))
        k.klucz(szczyt, "Czapka", obrot=(-22, 0, 0))
        k.klucz(szczyt + 6, "Czapka", obrot=(10, 0, 0))
        k.klucz(koniec, "Czapka", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.75, dodatki=lambda k: rece(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=0.95, wyskok=0.95, dodatki=lambda k: rece(k, 12, 30))
