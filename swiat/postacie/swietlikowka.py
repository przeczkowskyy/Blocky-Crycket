# -*- coding: utf-8 -*-
"""ŚWIETLIKÓWKA — pet epicki z leśnego jajka (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Puszysta śliwkowa sówka (ok. 2,6 studa z piórkami): wielka głowa z jasnymi tarczami wokół bursztynowych, świecących
oczu, dziób, piórka-uszy, skrzydła wzdłuż boków, a na brzuszku świecąca „latarenka” jak u świetlika. Wokół niej
krążą trzy świetliki. Sylwetka: pionowa, szeroka głowa z różkami — epicki, więc świeci (oczy, brzuszek, świetliki).

    python -B swiat/postacie/przebuduj.py swietlikowka --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa > {PiorkoL, PiorkoP}, SkrzydloL, SkrzydloP, Swietlik1, Swietlik2, Swietlik3}
  Świetliki mają staw w środku tułowia, a bryłę ok. 1,2 studa dalej — obrót kości wokół pionu = krążenie.
Klipy: spoczynek (rozgląda się, świetliki krążą), chod (trzepocze i unosi się, pętla), radosc, wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie

ID = "swietlikowka"

PALETA = {
    "pioro": "5B4A8A", "pioro_ciemne": "3E2F66", "pioro_jasne": "7E6BB0", "brzuch": "D8C9A8",
    "tarcza": "F2E6C8", "teczowka": "FFB31A", "dziob": "F2A93B", "blask": "E4FF6A", "swietlik": "F6FF7A",
}

TULOW = (1.15, 1.1, 0.95)
Y_STAWU = 0.8
Y_SRODKA = 0.85
SWIETLIKI = [("Swietlik1", 1.25, 0.45, 0), ("Swietlik2", 1.15, 1.45, 130), ("Swietlik3", 1.35, 0.95, 250)]


def zbuduj():
    p = Postac(ID, "Świetlikówka", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_STAWU, 0), czesc=TULOW, srodek=(0, Y_SRODKA - Y_STAWU, 0))
    p.kosc("Glowa", "Tulow", staw=(0, 1.38, 0), czesc=(1.25, 1.0, 1.0), srodek=(0, 0.45, 0.02))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Piorko" + s, "Glowa", staw=(zn * 0.45, 2.26, 0.0), czesc=(0.24, 0.45, 0.2), srodek=(zn * 0.06, 0.2, 0))
        p.kosc("Skrzydlo" + s, "Tulow", staw=(zn * 0.56, 1.3, -0.05), czesc=(0.22, 0.82, 0.84),
               srodek=(zn * 0.1, -0.36, -0.06))
    for nazwa, r, y, kat in SWIETLIKI:
        p.kosc(nazwa, "Tulow", staw=(0, Y_SRODKA, 0), czesc=None, srodek=(0, 0, 0))

    # ------------------------------------------------------------------ tułów z latarenką
    with p.na("Tulow", od="srodek"):
        w, h, d = TULOW
        z = d / 2
        p.blok("Tulow", (0, 0, 0), TULOW, "pioro", faza=0.16)
        p.blok("Brzuszek", (0, -0.08, z + 0.02), (0.8, 0.8, 0.06), "brzuch", "matowy", faza=0.04)
        p.blok("Latarenka", (0, -0.16, z + 0.05), (0.5, 0.46, 0.04), "blask", "swiecacy", faza=0.02)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Pazurki " + s, (zn * 0.24, -h / 2 - 0.12, 0.14), (0.26, 0.3, 0.34), "dziob", faza=0.05)

    # ------------------------------------------------------------------ głowa
    with p.na("Glowa", od="srodek"):
        w, h, d = 1.25, 1.0, 1.0
        z = d / 2
        p.blok("Glowa", (0, 0, 0), (w, h, d), "pioro", faza=0.16)
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.28
            p.blok("Tarcza " + s, (x, 0.0, z + 0.01), (0.52, 0.54, 0.06), "tarcza", "matowy", faza=0.03)
            p.blok("Teczowka " + s, (x, 0.0, z + 0.05), (0.34, 0.36, 0.04), "teczowka", "swiecacy", faza=0.02)
            p.blok("Zrenica " + s, (x - zn * 0.02, -0.02, z + 0.08), (0.17, 0.22, 0.03), "tusz", "polysk", faza=0.0)
            p.blok("Blysk " + s, (x - zn * 0.08, 0.09, z + 0.1), (0.08, 0.08, 0.02), "bialy", "swiecacy", faza=0.0)
            p.blok("Brew " + s, (zn * 0.3, 0.33, z + 0.03), (0.42, 0.1, 0.06), "pioro_ciemne", "matowy",
                   rot=(0, 0, -zn * 16), faza=0.0)
        p.blok("Dziob", (0, -0.2, z + 0.08), (0.18, 0.24, 0.16), "dziob", faza=0.04)
        p.blok("Dziob czubek", (0, -0.34, z + 0.1), (0.1, 0.1, 0.1), "dziob", faza=0.02)

    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Piorko" + s, od="srodek"):
            p.blok("Piorko", (0, 0, 0), (0.24, 0.45, 0.2), "pioro_ciemne", rot=(0, 0, -zn * 24), faza=0.04)
        with p.na("Skrzydlo" + s, od="srodek"):
            with p.uklad(obrot=(8, 0, zn * 9)):
                p.blok("Skrzydlo", (0, 0, 0), (0.2, 0.82, 0.84), "pioro_ciemne", faza=0.08)
                p.blok("Skrzydlo pasek", (zn * 0.02, -0.18, 0.02), (0.22, 0.14, 0.86), "pioro_jasne", "matowy",
                       faza=0.02)
                p.klin("Lotka", (0, -0.5, -0.12), (0.18, 0.24, 0.5), "pioro_ciemne", rot=(180, 0, 0), faza=0.0)

    # ------------------------------------------------------------------ świetliki (krążą wokół tułowia)
    import math
    for nazwa, r, y, kat in SWIETLIKI:
        a = math.radians(kat)
        with p.na(nazwa, od="staw"):
            p.blok("Swietlik", (r * math.sin(a), y - Y_SRODKA, r * math.cos(a)), (0.17, 0.17, 0.17), "swietlik",
                   "swiecacy", faza=0.03)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_STAWU, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 1.05, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 8)
    return p


SLABOSCI = [
    "Świecenie (oczy, brzuszek, świetliki) w Roblox to materiał Neon; poświata dookoła — PointLight w grze.",
    "Skrzydła to płaskie klocki przy bokach — przy machaniu nie mają rozłożonych lotek.",
    "Uwaga raportu „pętla skoczy” przy kościach świetlików jest oczekiwana: obrót 0° → 360° to ta sama poza.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.klucz(0, "Glowa", obrot=(0, 0, 0))
    k.klucz(14, "Glowa", obrot=(0, 28, 4))
    k.klucz(30, "Glowa", obrot=(0, 0, 0))
    k.klucz(44, "Glowa", obrot=(0, -28, -4))
    k.klucz(60, "Glowa", obrot=(0, 0, 0))
    k.cykl("Tulow", "przes", (0, 0.03, 0), czestosc=2)
    k.cykl("SkrzydloL", "obrot", (0, 0, 5), czestosc=2)
    k.cykl("SkrzydloP", "obrot", (0, 0, -5), czestosc=2)
    k.cykl("PiorkoL", "obrot", (0, 0, 7), czestosc=2, faza=0.1)
    k.cykl("PiorkoP", "obrot", (0, 0, -7), czestosc=2, faza=0.15)
    _swietliki(k, 60, 1)

    k = p.klip("chod", 24, petla=True)
    k.cykl("SkrzydloL", "obrot", (0, 0, 55), czestosc=2, srodek=(0, 0, 45))
    k.cykl("SkrzydloP", "obrot", (0, 0, -55), czestosc=2, srodek=(0, 0, -45))
    k.cykl("Tulow", "przes", (0, 0.14, 0), czestosc=2, srodek=(0, 0.35, 0))       # unosi się nad ziemią
    k.cykl("Tulow", "obrot", (3, 0, 0), czestosc=2, srodek=(10, 0, 0))            # pochylona w lot
    k.cykl("Glowa", "obrot", (-4, 0, 0), czestosc=2, srodek=(-8, 0, 0))
    _swietliki(k, 24, 1)

    def skrzydla(k, szczyt, koniec):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Skrzydlo" + s, obrot=(0, 0, 0))
            k.klucz(szczyt - 4, "Skrzydlo" + s, obrot=(0, 0, zn * 120))
            k.klucz(szczyt, "Skrzydlo" + s, obrot=(0, 0, zn * 60))
            k.klucz(szczyt + 4, "Skrzydlo" + s, obrot=(0, 0, zn * 120))
            k.klucz(koniec, "Skrzydlo" + s, obrot=(0, 0, 0))
        _swietliki(k, koniec, 2)

    klip_radosc(p, "Tulow", wysokosc=0.9, dodatki=lambda k: skrzydla(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.25, wyskok=1.0, dodatki=lambda k: skrzydla(k, 12, 30))


def _swietliki(k, dl, obroty):
    """Krążenie świetlików: pełne obroty kości wokół pionu (liniowo), każdy w swoją stronę, z falowaniem w pionie."""
    for i, (nazwa, _r, _y, _kat) in enumerate(SWIETLIKI):
        kier = (1, -1, 2)[i] * obroty
        k.klucz(0, nazwa, obrot=(0, 0, 0), wyg="liniowo")
        k.klucz(dl / 2.0, nazwa, obrot=(0, 180 * kier, 0), wyg="liniowo")
        k.klucz(dl, nazwa, obrot=(0, 360 * kier, 0), wyg="liniowo")
        k.cykl(nazwa, "przes", (0, 0.12, 0), czestosc=2 if dl >= 30 else 1, faza=i * 0.3)
