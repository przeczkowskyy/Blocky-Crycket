# -*- coding: utf-8 -*-
"""OGNIK — pet epicki z jajka Bagna (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Błędny ognik z mokradeł (ok. 2,5 studa, unosi się): okrągły, bladozielony „płomyk” z buzią, nad nim zakręcony
czubek płomienia z trzech świecących języków, dwa płomykowe rączki-wąsy po bokach i zwężający się ogonek-smuga
pod spodem. Wokół krążą dwie iskierki. Sylwetka: kropla do góry nogami bez nóg — epicki, więc świeci, ale tylko
płomień, rączki i iskry (cały świecący pet to plama światła — wniosek z jelonka 17.11).

    python -B swiat/postacie/przebuduj.py ognik --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Plomien > Plomyk, RaczkaL, RaczkaP, Smuga > Smuga2, Iskra1, Iskra2}
  Iskry mają staw w środku tułowia, a bryłę ok. 1,1 studa dalej — obrót kości wokół pionu = krążenie.
Klipy: spoczynek (unosi się, płomień faluje, iskry krążą), chod (sunie pochylony, smuga się wije), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "ognik"

PALETA = {
    "cialo": "C9F5D2", "cialo_cien": "A6E3B5", "plomien": "C8FF6A", "plomien_jasny": "E4FF7A", "plomien_ciemny": "7ED957",
    "rumieniec": "FF9EC2", "buzia": "2E4A26", "iskra": "E4FF6A",
}

Y_SRODKA = 1.45       # środek ciała (unosi się)
CIALO = (1.2, 1.1, 1.1)
ISKRY = [("Iskra1", 1.1, 0.25, 20), ("Iskra2", 1.0, -0.2, 200)]


def zbuduj():
    p = Postac(ID, "Ognik", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_SRODKA, 0), czesc=CIALO, srodek=(0, 0, 0))
    # płomień wyrasta z czubka ciała (podstawa schowana w elipsoidzie) i zawija się do tyłu
    p.kosc("Plomien", "Tulow", staw=(0, Y_SRODKA + 0.35, 0), czesc=(0.7, 1.05, 0.7), srodek=(0, 0.52, -0.1))
    p.kosc("Plomyk", "Plomien", staw=(0, Y_SRODKA + 0.95, -0.22), czesc=(0.26, 0.5, 0.26), srodek=(0, 0.25, -0.05))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Raczka" + s, "Tulow", staw=(zn * 0.55, Y_SRODKA - 0.05, 0.05), czesc=(0.4, 0.22, 0.22),
               srodek=(zn * 0.2, 0.05, 0))
    p.kosc("Smuga", "Tulow", staw=(0, Y_SRODKA - 0.4, -0.05), czesc=(0.6, 0.7, 0.6), srodek=(0, -0.3, -0.05))
    p.kosc("Smuga2", "Smuga", staw=(0, Y_SRODKA - 1.0, -0.12), czesc=(0.18, 0.3, 0.18), srodek=(0, -0.1, -0.04))
    for nazwa, _r, _y, _kat in ISKRY:
        p.kosc(nazwa, "Tulow", staw=(0, Y_SRODKA, 0), czesc=None, srodek=(0, 0, 0))

    with p.na("Tulow", od="srodek"):
        p.kula("Cialo", (0, 0, 0), CIALO, "cialo", "zwykly", segm=16)
        p.kula("Cialo spod", (0, -0.28, -0.04), (0.9, 0.6, 0.86), "cialo_cien", "zwykly", segm=12)
        # przód elipsoidy: z ≈ 0,51 przy oczach, 0,44 przy rumieńcach, 0,53 przy buzi — bryły wystają ponad nią
        oczy(p, 0.2, 0.08, 0.5, szer=0.2, wys=0.28)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Rumieniec " + s, (zn * 0.34, -0.1, 0.45), (0.14, 0.07, 0.04), "rumieniec", "matowy", faza=0.0)
        p.blok("Buzia", (0, -0.14, 0.535), (0.14, 0.06, 0.04), "buzia", "matowy", faza=0.0)
    with p.na("Plomien", od="staw"):                             # wielki język płomienia i dwa boczne
        p.ostroslup("Jezyk", (0, 0.52, -0.02), (0.7, 1.05, 0.7), "plomien", "swiecacy", przes_gory=(0, -0.28), faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            p.ostroslup("Jezyk boczny " + s, (zn * 0.3, 0.24, 0.0), (0.34, 0.6, 0.34), "plomien_ciemny", "swiecacy",
                        rot=(0, 0, -zn * 25), przes_gory=(0, -0.08), faza=0.0)
    with p.na("Plomyk", od="staw"):                              # zawijas na czubku (migocze osobno)
        p.ostroslup("Plomyk", (0, 0.22, -0.02), (0.26, 0.5, 0.26), "plomien_jasny", "swiecacy",
                    przes_gory=(0, -0.1), faza=0.0)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Raczka" + s, od="srodek"):
            p.kula("Raczka", (0, 0, 0), (0.38, 0.22, 0.22), "plomien", "swiecacy", segm=8)
            p.ostroslup("Raczka czubek", (zn * 0.2, 0.1, 0), (0.18, 0.26, 0.16), "plomien", "swiecacy",
                        rot=(0, 0, -zn * 40), faza=0.0)
    with p.na("Smuga", od="srodek"):                             # ciało zwęża się w smugę (odwrócony ostrosłup)
        p.ostroslup("Smuga", (0, 0, 0), (0.6, 0.7, 0.6), "cialo_cien", "zwykly", rot=(180, 0, 0),
                    przes_gory=(0, 0.1), faza=0.0)
    with p.na("Smuga2", od="srodek"):
        p.kula("Smuga koniec", (0, 0, 0), (0.18, 0.3, 0.18), "plomien_ciemny", "swiecacy", segm=8)
    for nazwa, r, y, kat in ISKRY:
        a = math.radians(kat)
        with p.na(nazwa, od="staw"):
            p.blok("Iskra", (r * math.sin(a), y, r * math.cos(a)), (0.16, 0.16, 0.16), "iskra", "swiecacy",
                   rot=(45, 45, 0), faza=0.0)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_SRODKA, 0))
    p.zaczep("GlowaAttachment", "Plomyk", (0, 0.6, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 6)
    return p


SLABOSCI = [
    "Płomień to ostrosłupy Neon (kanciaste języki); poświata dookoła to PointLight w grze.",
    "Uwaga raportu „pętla skoczy” przy kościach iskier jest oczekiwana: obrót 0° → 360° to ta sama poza.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.14, 0), czestosc=1)
    k.cykl("Plomien", "obrot", (0, 0, 8), czestosc=2)
    k.cykl("Plomyk", "obrot", (6, 0, 14), czestosc=3, faza=0.2)
    k.cykl("RaczkaL", "obrot", (0, 0, 14), czestosc=2)
    k.cykl("RaczkaP", "obrot", (0, 0, -14), czestosc=2, faza=0.25)
    k.cykl("Smuga", "obrot", (0, 0, 10), czestosc=1, faza=0.3)
    k.cykl("Smuga2", "obrot", (0, 0, -16), czestosc=1, faza=0.5)
    _iskry(k, 60, 1)

    k = p.klip("chod", 24, petla=True)
    k.cykl("Tulow", "przes", (0, 0.1, 0), czestosc=2, srodek=(0, 0.1, 0))
    k.cykl("Tulow", "obrot", (3, 0, 4), czestosc=1, srodek=(10, 0, 0))           # sunie pochylony w przód
    k.cykl("Plomien", "obrot", (8, 0, 6), czestosc=2, srodek=(-14, 0, 0))        # płomień odwiewany do tyłu
    k.cykl("Plomyk", "obrot", (8, 0, 10), czestosc=2, faza=0.2, srodek=(-12, 0, 0))
    k.cykl("Smuga", "obrot", (6, 0, 14), czestosc=1, srodek=(-12, 0, 0))
    k.cykl("Smuga2", "obrot", (6, 0, -20), czestosc=1, faza=0.4, srodek=(-10, 0, 0))
    k.cykl("RaczkaL", "obrot", (0, 0, 20), czestosc=2, srodek=(-20, 0, 0))
    k.cykl("RaczkaP", "obrot", (0, 0, -20), czestosc=2, srodek=(-20, 0, 0))
    _iskry(k, 24, 1)

    def dodatki(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Raczka" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "Raczka" + s, obrot=(0, 0, zn * 70))
            k.klucz(koniec, "Raczka" + s, obrot=(0, 0, 0))
        k.klucz(0, "Plomien", obrot=(0, 0, 0))
        k.klucz(szczyt, "Plomien", obrot=(-20, 0, 0))
        k.klucz(koniec, "Plomien", obrot=(0, 0, 0))
        _iskry(k, koniec, 2)

    klip_radosc(p, "Tulow", wysokosc=0.9, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.6, wyskok=1.0, dodatki=lambda k: dodatki(k, 12, 30))


def _iskry(k, dl, obroty):
    """Krążenie iskier: pełne obroty kości wokół pionu (liniowo), w przeciwne strony, z falowaniem w pionie."""
    for i, (nazwa, _r, _y, _kat) in enumerate(ISKRY):
        kier = (1, -1)[i] * obroty
        k.klucz(0, nazwa, obrot=(0, 0, 0), wyg="liniowo")
        k.klucz(dl / 2.0, nazwa, obrot=(0, 180 * kier, 0), wyg="liniowo")
        k.klucz(dl, nazwa, obrot=(0, 360 * kier, 0), wyg="liniowo")
        k.cykl(nazwa, "przes", (0, 0.14, 0), czestosc=2 if dl >= 30 else 1, faza=i * 0.4)
