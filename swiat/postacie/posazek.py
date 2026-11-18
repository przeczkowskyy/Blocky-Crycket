# -*- coding: utf-8 -*-
"""POSĄŻEK — pet epicki z jajka Dżungli (próba swiat/pety_proba, 18.11.2026; status: propozycja, własny projekt).

Mały ożywiony bożek z dawnych ruin Dżungli (ok. 2,3 studa): kanciasty kamienny tułów i wielka kwadratowa głowa
z wyrzeźbioną twarzą, świecącymi turkusowymi oczami i runami na piersi, płaty mchu, owinięta wokół liana z listkami,
na głowie kamienny pióropusz z liści i świecący różowy kwiat. Krótkie kamienne rączki i nóżki — chodzi ciężko,
kołysząc się na boki. Sylwetka: kanciasty totem z głową większą od tułowia — inna niż wszystkie pety (obłe zwierzątka)
i niż Pancernik Ruin (niski czworonóg z płyt).

    python -B swiat/postacie/przebuduj.py posazek --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X): Root > Tulow > {Glowa > Pioropusz, RekaL, RekaP, NogaL, NogaP}
Klipy: spoczynek (runy „oddychają” — kołysanie głowy), chod (ciężkie kroki z przechyłem), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie

ID = "posazek"

PALETA = {
    "kamien": "8F8A7A", "kamien_ciemny": "6B6658", "kamien_jasny": "A8A392", "mech": "5E8F45", "run": "2EC4B6",
    "liana": "3E7D2E", "lisc": "2FA34A", "lisc_jasny": "6CCB4A", "kwiat": "FF5FA2", "kwiat_srodek": "FFD84A",
    "ryt": "4A463C",
}

Y_TULOWIA = 0.45
TULOW = (0.92, 0.75, 0.7)
GLOWA = (1.12, 0.95, 0.92)


def zbuduj():
    p = Postac(ID, "Posążek", typ="stwor", skala=1.0, faza=0.04, paleta=PALETA)
    w, h, d = TULOW
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, h / 2, 0))
    p.kosc("Glowa", "Tulow", staw=(0, Y_TULOWIA + h, 0.02), czesc=GLOWA, srodek=(0, GLOWA[1] / 2, 0.02))
    p.kosc("Pioropusz", "Glowa", staw=(0, Y_TULOWIA + h + GLOWA[1], 0), czesc=(1.2, 0.7, 0.4), srodek=(0, 0.3, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Reka" + s, "Tulow", staw=(zn * 0.52, Y_TULOWIA + 0.62, 0.02), czesc=(0.26, 0.5, 0.28),
               srodek=(zn * 0.04, -0.2, 0.02))
        p.kosc("Noga" + s, "Tulow", staw=(zn * 0.24, Y_TULOWIA + 0.02, 0), czesc=(0.32, 0.47, 0.36),
               srodek=(0, -0.22, 0.02))

    with p.na("Tulow", od="srodek"):
        p.blok("Tulow", (0, 0, 0), TULOW, "kamien", "matowy", faza=0.08)
        p.blok("Pas", (0, -h / 2 + 0.1, 0), (w + 0.06, 0.16, d + 0.06), "kamien_ciemny", "matowy", faza=0.04)
        # runy na piersi: świecące turkusowe kreski (romb i pionowa linia)
        p.blok("Run", (0, 0.08, d / 2 + 0.01), (0.06, 0.34, 0.03), "run", "swiecacy", faza=0.0)
        for zn in (1, -1):
            p.blok("Run", (zn * 0.1, 0.08, d / 2 + 0.01), (0.2, 0.05, 0.03), "run", "swiecacy", rot=(0, 0, zn * 45),
                   faza=0.0)
        p.blok("Mech", (0.28, 0.3, -0.1), (0.4, 0.1, 0.5), "mech", "matowy", faza=0.03)
        # liana owinięta skośnie przez pierś
        p.blok("Liana", (0, 0.0, d / 2 + 0.03), (0.12, 1.0, 0.08), "liana", "matowy", rot=(0, 0, 40), faza=0.0)
        p.blok("Listek liany", (-0.3, -0.24, d / 2 + 0.06), (0.22, 0.06, 0.14), "lisc_jasny", "matowy",
               rot=(-60, 0, 20), faza=0.0)
    with p.na("Glowa", od="srodek"):
        gw, gh, gd = GLOWA
        z = gd / 2
        p.blok("Glowa", (0, 0, 0), GLOWA, "kamien_jasny", "matowy", faza=0.08)
        p.blok("Czolo", (0, gh / 2 - 0.1, z + 0.02), (gw + 0.04, 0.16, 0.08), "kamien_ciemny", "matowy", faza=0.03)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Oczodol " + s, (zn * 0.24, 0.08, z + 0.01), (0.3, 0.22, 0.04), "ryt", "matowy", faza=0.02)
            p.blok("Oko " + s, (zn * 0.24, 0.08, z + 0.035), (0.18, 0.13, 0.03), "run", "swiecacy", faza=0.0)
            p.blok("Ucho " + s, (zn * (gw / 2 + 0.06), 0.0, 0.0), (0.12, 0.42, 0.3), "kamien", "matowy", faza=0.03)
        p.blok("Nos", (0, -0.08, z + 0.05), (0.16, 0.2, 0.1), "kamien", "matowy", faza=0.02)
        p.blok("Usta", (0, -0.28, z + 0.01), (0.46, 0.08, 0.04), "ryt", "matowy", faza=0.0)
        p.blok("Mech glowy", (-0.3, gh / 2 + 0.02, 0.1), (0.42, 0.08, 0.46), "mech", "matowy", faza=0.03)
    with p.na("Pioropusz", od="staw"):
        p.blok("Opaska", (0, 0.06, 0), (0.9, 0.14, 0.5), "kamien_ciemny", "matowy", faza=0.02)
        for i, (x, a) in enumerate(((-0.36, 28), (-0.14, 10), (0.14, -10), (0.36, -28))):
            p.klin("Lisc pioropusza", (x, 0.38, -0.04), (0.18, 0.62, 0.2), "lisc" if i % 2 else "lisc_jasny", "matowy",
                   rot=(-8, 0, a), faza=0.0)
        for i in range(5):                                              # świecący różowy kwiat z przodu opaski
            a = math.radians(i * 72)
            p.blok("Platek", (0.1 * math.cos(a), 0.16 + 0.1 * math.sin(a), 0.27), (0.14, 0.12, 0.05), "kwiat",
                   "swiecacy", rot=(0, 0, math.degrees(a)), faza=0.0)
        p.blok("Kwiat srodek", (0, 0.16, 0.3), (0.08, 0.08, 0.04), "kwiat_srodek", "swiecacy", faza=0.0)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Reka" + s, od="srodek"):
            p.blok("Reka", (0, 0.03, 0), (0.24, 0.42, 0.26), "kamien", "matowy", faza=0.05)
            p.blok("Dlon", (0, -0.24, 0.02), (0.28, 0.14, 0.3), "kamien_ciemny", "matowy", faza=0.03)
        with p.na("Noga" + s, od="srodek"):
            p.blok("Noga", (0, 0.03, 0), (0.3, 0.4, 0.32), "kamien_ciemny", "matowy", faza=0.05)
            p.blok("Stopa", (0, -0.2, 0.06), (0.34, 0.1, 0.44), "kamien", "matowy", faza=0.03)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Pioropusz", (0, 0.95, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = ["Kwiat na pióropuszu to pięć płaskich płatków na jednej płaszczyźnie — z boku cienki."]


def _klipy(p):
    k = p.klip("spoczynek", 72, petla=True)
    k.cykl("Glowa", "obrot", (3, 8, 0), czestosc=1)
    k.cykl("Pioropusz", "obrot", (0, 0, 5), czestosc=2, faza=0.25)
    k.cykl("Tulow", "przes", (0, 0.015, 0), czestosc=2)
    k.cykl("RekaL", "obrot", (6, 0, 0), czestosc=1)
    k.cykl("RekaP", "obrot", (6, 0, 0), czestosc=1, faza=0.5)

    k = p.klip("chod", 24, petla=True)                            # ciężko, z przechyłem na boki
    k.cykl("NogaL", "obrot", (28, 0, 0), czestosc=1)
    k.cykl("NogaP", "obrot", (28, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaL", "obrot", (-22, 0, 0), czestosc=1, faza=0.5)
    k.cykl("RekaP", "obrot", (-22, 0, 0), czestosc=1)
    k.cykl("Tulow", "obrot", (0, 0, 8), czestosc=1)
    k.cykl("Tulow", "przes", (0, 0.05, 0), czestosc=2, srodek=(0, 0.03, 0))
    k.cykl("Glowa", "obrot", (0, 0, -5), czestosc=1, faza=0.1)

    def rece(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Reka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Reka" + s, obrot=(-160, 0, zn * 10))
            k.klucz(koniec, "Reka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Pioropusz", przes=(0, 0, 0))
        k.klucz(szczyt, "Pioropusz", przes=(0, 0.15, 0))
        k.klucz(koniec, "Pioropusz", przes=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.55, dodatki=lambda k: rece(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.0, wyskok=0.8, dodatki=lambda k: rece(k, 12, 30))
