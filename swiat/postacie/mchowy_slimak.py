# -*- coding: utf-8 -*-
"""MCHOWY ŚLIMAK — pet zwykły z leśnego jajka (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Bladozielony ślimak (ok. 2,4 studa długości, 2 studa wysokości z grzybkiem): długa, niska stopa, uniesiona główka
z oczami na czułkach, kanciasta brązowa muszla z kwadratową „spiralą” na bokach, czapa mchu na grzbiecie muszli
i mały czerwony grzybek w białe kropki. Sylwetka: niska i podłużna — zupełnie inna niż żołądź i lis.

    python -B swiat/postacie/przebuduj.py mchowy_slimak --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Cialo > {Glowa > {CzulekL, CzulekP}, Muszla > Grzybek}
Klipy: spoczynek, chod (sunięcie z falowaniem stopy, pętla), radosc, wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie

ID = "mchowy_slimak"

PALETA = {
    "cialo": "A8C98A", "cialo_ciemne": "7FA866", "podeszwa": "D9EBC4",
    "muszla": "8A5A3A", "muszla_ciemna": "5E3A22", "muszla_jasna": "B9844F",
    "mech": "5E9B3A", "mech_jasny": "7CC04A",
    "grzyb": "D94A3A", "kropka": "FFF4E0", "trzon": "F2E6CC",
    "rumieniec": "F08C8C", "buzia": "3E5A2A",
}

STOPA = (0.95, 0.42, 2.0)
Y_STOPY = 0.24
Z_STOPY = -0.15


def zbuduj():
    p = Postac(ID, "Mchowy Ślimak", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Cialo", "Root", staw=(0, Y_STOPY, Z_STOPY), czesc=STOPA, srodek=(0, 0, 0))
    p.kosc("Glowa", "Cialo", staw=(0, 0.4, 0.55), czesc=(0.8, 0.74, 0.7), srodek=(0, 0.34, 0.15))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Czulek" + s, "Glowa", staw=(zn * 0.2, 1.08, 0.78), czesc=(0.12, 0.5, 0.12), srodek=(0, 0.25, 0))
    p.kosc("Muszla", "Cialo", staw=(0, 0.45, -0.35), czesc=(1.15, 1.2, 1.25), srodek=(0, 0.58, -0.05))
    p.kosc("Grzybek", "Muszla", staw=(0.18, 1.62, -0.5), czesc=(0.62, 0.55, 0.62), srodek=(0, 0.27, 0))

    # ------------------------------------------------------------------ stopa
    with p.na("Cialo", od="srodek"):
        w, h, d = STOPA
        p.blok("Stopa", (0, 0, 0), STOPA, "cialo", faza=0.12)
        p.blok("Podeszwa", (0, -h / 2 + 0.05, 0), (w + 0.06, 0.1, d + 0.04), "podeszwa", "matowy", faza=0.03)
        p.blok("Ogonek stopy", (0, -0.06, -d / 2 - 0.12), (0.6, 0.26, 0.4), "cialo_ciemne", faza=0.06)

    # ------------------------------------------------------------------ główka z buzią
    with p.na("Glowa", od="srodek"):
        w, h, d = 0.8, 0.74, 0.7
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "cialo", faza=0.14)
        p.blok("Buzia", (0, -0.1, z + 0.02), (0.26, 0.06, 0.04), "buzia", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Kacik", (zn * 0.15, -0.07, z + 0.02), (0.06, 0.06, 0.04), "buzia", "matowy", faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.28, -0.02, z + 0.02), (0.16, 0.09, 0.04), "rumieniec", "matowy", faza=0.0)

    # ------------------------------------------------------------------ oczy na czułkach
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Czulek" + s, od="staw"):
            p.blok("Czulek", (0, 0.24, 0), (0.12, 0.5, 0.12), "cialo_ciemne", faza=0.03)
            p.blok("Oko", (0, 0.56, 0.02), (0.3, 0.3, 0.3), "bialy", "polysk", faza=0.07)
            p.blok("Zrenica", (-zn * 0.03, 0.55, 0.18), (0.15, 0.18, 0.04), "tusz", "polysk", faza=0.0)

    # ------------------------------------------------------------------ muszla z mchem
    with p.na("Muszla", od="srodek"):
        w, h, d = 1.15, 1.2, 1.25
        p.blok("Muszla", (0, 0, 0), (w, h, d), "muszla", faza=0.16)
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * (w / 2 + 0.02)
            p.blok("Spirala " + s, (x, -0.04, 0.02), (0.05, 0.9, 0.95), "muszla_ciemna", "matowy", faza=0.0)
            p.blok("Spirala srodek " + s, (x + zn * 0.02, 0.0, -0.04), (0.05, 0.52, 0.55), "muszla_jasna", "matowy",
                   faza=0.0)
            p.blok("Spirala oczko " + s, (x + zn * 0.04, 0.04, -0.08), (0.05, 0.2, 0.2), "muszla_ciemna", "matowy",
                   faza=0.0)
        p.blok("Mech", (0, h / 2 + 0.05, -0.02), (1.0, 0.2, 1.08), "mech", "matowy", faza=0.06)
        p.blok("Mech kepka", (0.22, h / 2 + 0.17, 0.25), (0.42, 0.16, 0.4), "mech_jasny", "matowy", faza=0.05)
        p.blok("Mech zwis", (0, h / 2 - 0.12, -d / 2 - 0.03), (0.7, 0.32, 0.08), "mech", "matowy", faza=0.02)

    # ------------------------------------------------------------------ grzybek
    with p.na("Grzybek", od="staw"):
        p.blok("Trzon", (0, 0.16, 0), (0.2, 0.32, 0.2), "trzon", "matowy", faza=0.04)
        p.blok("Kapelusz", (0, 0.4, 0), (0.62, 0.22, 0.62), "grzyb", faza=0.07)
        p.blok("Kropka", (0.14, 0.52, 0.1), (0.14, 0.04, 0.14), "kropka", "matowy", faza=0.0)
        p.blok("Kropka", (-0.12, 0.52, -0.12), (0.12, 0.04, 0.12), "kropka", "matowy", faza=0.0)

    p.zaczep("RootAttachment", "Cialo", (0, -Y_STOPY, -Z_STOPY))
    p.zaczep("GlowaAttachment", "Muszla", (0, 1.4, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 10)
    return p


SLABOSCI = [
    "Stopa jest jedną sztywną bryłą — falowanie przy sunięciu robi przesunięcie kości, nie zginanie.",
    "Muszla i stopa to kanciaste klocki; „spirala” jest płaska (kwadraty na bokach).",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("CzulekL", "obrot", (6, 0, 10), czestosc=1)
    k.cykl("CzulekP", "obrot", (6, 0, -10), czestosc=1, faza=0.25)
    k.cykl("Glowa", "obrot", (3, 0, 0), czestosc=1, faza=0.1)
    k.cykl("Muszla", "przes", (0, 0.025, 0), czestosc=2)
    k.cykl("Grzybek", "obrot", (0, 0, 7), czestosc=2)

    k = p.klip("chod", 24, petla=True)
    k.cykl("Cialo", "przes", (0, 0, 0.05), czestosc=1)
    k.cykl("Glowa", "przes", (0, 0, 0.08), czestosc=1, faza=0.15)
    k.cykl("Glowa", "obrot", (5, 0, 0), czestosc=1, faza=0.15)
    k.cykl("Muszla", "obrot", (0, 4, 0), czestosc=1)
    k.cykl("Muszla", "przes", (0, 0.03, 0), czestosc=2)
    k.cykl("CzulekL", "obrot", (14, 0, 0), czestosc=2)
    k.cykl("CzulekP", "obrot", (14, 0, 0), czestosc=2, faza=0.2)
    k.cykl("Grzybek", "obrot", (0, 0, 10), czestosc=2, faza=0.3)

    def czulki(k, szczyt, koniec, start_zlozone=False):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Czulek" + s, obrot=(-80, 0, 0) if start_zlozone else (0, 0, 0))
            k.klucz(szczyt, "Czulek" + s, obrot=(-10, 0, zn * 40))
            k.klucz(szczyt + 6, "Czulek" + s, obrot=(10, 0, -zn * 20))
            k.klucz(koniec, "Czulek" + s, obrot=(0, 0, 0))
        k.klucz(0, "Grzybek", przes=(0, 0, 0))
        k.klucz(szczyt, "Grzybek", przes=(0, 0.25, 0))
        k.klucz(szczyt + 5, "Grzybek", przes=(0, -0.04, 0))
        k.klucz(koniec, "Grzybek", przes=(0, 0, 0))

    klip_radosc(p, "Cialo", wysokosc=0.55, dodatki=lambda k: czulki(k, 15, 36))
    klip_wyklucie(p, "Cialo", glebokosc=1.0, wyskok=0.8, dodatki=lambda k: czulki(k, 12, 30, start_zlozone=True))
