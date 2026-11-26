# -*- coding: utf-8 -*-
"""ŚWIETLIKÓWKA — pet epicki z leśnego jajka (próba swiat/pety_proba; status: propozycja).

Przebudowa 25/26.11.2026 według arkusza obrotów Pawła (`swietlikowka_obroty.jpg`: przód, 3/4, przód z zamkniętymi
oczami, tył — BEZ widoku z boku; bok uzupełniony z widoku 3/4 i z modelu z 17.11). Wzór wyglądu: ciemnośliwkowa
sówka (ok. 2,7 studa z piórkami): wielka głowa-kostka z zaokrąglonymi rogami, jasna maska z dwóch kół wokół
świecących pomarańczowych oczu, mały zakrzywiony dziób, pierzaste uszka wygięte na boki; okrągły tułów z jasnym
brzuszkiem, na którym WISI LATARENKA (daszek z uchwytem i świecąca bańka); duże pierzaste skrzydła wzdłuż boków,
krótkie fioletowe nóżki (bez pomarańczowych stóp), z tyłu krótki ogonek; obok krążą świetliki ze skrzydełkami.
Kości, nazwy kości i klipy jak w modelu z 17.11.

    python -B swiat/postacie/przebuduj.py swietlikowka --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa > {PiorkoL, PiorkoP}, SkrzydloL, SkrzydloP, Swietlik1, Swietlik2, Swietlik3}
  Świetliki mają staw w środku tułowia, a bryłę ok. 1,15 studa dalej — obrót kości wokół pionu = krążenie.
Klipy: spoczynek (rozgląda się, świetliki krążą), chod (trzepocze i unosi się, pętla), radosc, wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, lata, model

ID = "swietlikowka"

PALETA = {
    "pioro": "5B3F8F", "pioro_ciemne": "40296B", "pioro_jasne": "7A5DB0", "brzuch": "DCC79A",
    "tarcza": "F2E6C8", "teczowka": "F26A00", "dziob": "F0962E", "blask": "C8F53C", "swietlik": "F6FF7A",
    "latarnia": "4A5A48", "skrzydelko": "D8F0FF",
}

TULOW = ((0.0, 0.72, 0.0), (1.3, 1.0, 1.1))           # elipsoida tułowia
GLOWA = ((0.0, 1.8, 0.02), (1.6, 1.3, 1.3))           # głowa-kostka: środek, rozmiar
Y_STAWU = 0.6
Y_SRODKA = 0.8                                        # środek orbit świetlików
# (kość, promień orbity, wysokość, kąt w spoczynku: 0 = przód +Z, 90 = lewy bok +X)
SWIETLIKI = [("Swietlik1", 1.15, 1.05, 90), ("Swietlik2", 1.2, 1.3, 270), ("Swietlik3", 1.25, 0.75, 200)]


def _twarz(p, nazwa, x, y, size, kolor, mat="matowy", wysun=0.0, obrot=0.0):
    """Płaska bryła (kula) na przedniej ścianie głowy-kostki."""
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    return p.kula(nazwa, (x, y, gz + gd / 2 + size[2] / 2 - 0.012 + wysun), size, kolor, mat, rot=(0, 0, obrot),
                  segm=14)


def zbuduj():
    p = Postac(ID, "Świetlikówka", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    (tx, ty, tz), (tw, th, td) = TULOW
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    p.kosc("Tulow", "Root", staw=(0, Y_STAWU, 0), czesc=(tw, th, td), srodek=(tx, ty - Y_STAWU, tz))
    p.kosc("Glowa", "Tulow", staw=(0, 1.16, 0), czesc=(gw, gh, gd), srodek=(gx, gy - 1.16, gz))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Piorko" + s, "Glowa", staw=(zn * 0.6, gy + gh / 2 - 0.08, 0.05), czesc=(0.36, 0.34, 0.12),
               srodek=(zn * 0.1, 0.15, 0))
        p.kosc("Skrzydlo" + s, "Tulow", staw=(zn * 0.62, 1.12, -0.05), czesc=(0.18, 0.92, 0.72),
               srodek=(zn * 0.12, -0.44, -0.02))
    for nazwa, r, y, kat in SWIETLIKI:
        p.kosc(nazwa, "Tulow", staw=(0, Y_SRODKA, 0), czesc=None, srodek=(0, 0, 0))

    # ------------------------------------------------------------------ tułów: jasny brzuszek, latarenka, nóżki, ogonek
    with model(p, "Tulow"):
        p.kula("Tulow", (tx, ty, tz), (tw, th, td), "pioro", segm=22)
        p.kula("Brzuszek", *lata(TULOW, (0, -0.1, 1), 0.45, s=0.12), "brzuch", "matowy", segm=22)
        zb = tz + td / 2 * 0.9                         # przód brzuszka na wysokości latarenki
        p.walec("Latarenka uchwyt", (0, 0.99, zb + 0.06), (0.11, 0.11, 0.03), "latarnia", "metal", rot=(90, 0, 0),
                segm=10, faza=0.0)
        p.walec("Latarenka daszek", (0, 0.9, zb + 0.1), (0.22, 0.09, 0.22), "latarnia", "metal", segm=10, faza=0.02)
        p.kula("Latarenka", (0, 0.72, zb + 0.12), (0.26, 0.32, 0.24), "blask", "swiecacy", segm=14)
        for zn in (1, -1):
            p.walec("Nozka", (zn * 0.24, 0.13, 0.05), (0.27, 0.28, 0.27), "pioro_ciemne", segm=12, faza=0.04)
        p.kula("Ogonek", (0, 0.4, -0.55), (0.34, 0.42, 0.12), "pioro_ciemne", rot=(-25, 0, 0), segm=12)

    # ------------------------------------------------------------------ głowa: maska z dwóch kół, świecące oczy, dziób
    with model(p, "Glowa"):
        p.blok("Glowa", (gx, gy, gz), (gw, gh, gd), "pioro", faza=0.32)
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.28
            _twarz(p, "Tarcza " + s, x, gy - 0.04, (0.66, 0.78, 0.05), "tarcza")
            _twarz(p, "Teczowka " + s, x, gy - 0.06, (0.36, 0.36, 0.05), "teczowka", "swiecacy", wysun=0.03)
            _twarz(p, "Blysk " + s, x + 0.07, gy + 0.03, (0.1, 0.1, 0.03), "bialy", "swiecacy", wysun=0.06)
            _twarz(p, "Blysk " + s, x - 0.07, gy - 0.13, (0.05, 0.05, 0.02), "bialy", "swiecacy", wysun=0.06)
        _twarz(p, "Tarcza dol", 0, gy - 0.3, (0.5, 0.36, 0.05), "tarcza")
        _twarz(p, "Dziob", 0, gy - 0.26, (0.2, 0.24, 0.16), "dziob", "zwykly", wysun=0.02)
        _twarz(p, "Dziob czubek", 0, gy - 0.36, (0.1, 0.12, 0.1), "dziob", "zwykly", wysun=0.08)

    # ------------------------------------------------------------------ pierzaste uszka wygięte na boki
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Piorko" + s, od="staw"):
            p.kula("Piorko", (zn * 0.05, 0.14, 0), (0.18, 0.4, 0.12), "pioro_ciemne", rot=(0, 0, -zn * 22), segm=10)
            p.kula("Piorko", (zn * 0.2, 0.1, 0), (0.16, 0.32, 0.11), "pioro", rot=(0, 0, -zn * 52), segm=10)

    # ------------------------------------------------------------------ duże pierzaste skrzydła wzdłuż boków
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Skrzydlo" + s, od="staw"), p.uklad(obrot=(4, -zn * 25, zn * 24)):
            p.kula("Skrzydlo", (zn * 0.05, -0.4, 0.04), (0.24, 0.96, 0.9), "pioro_ciemne", segm=14)
            # lotki: trzy zachodzące na siebie pióra rozłożone wachlarzem w dół (z przodu jedna postrzępiona krawędź)
            for dz, dl, kat in ((0.2, 0.36, -18), (0.0, 0.44, 0), (-0.2, 0.36, 18)):
                with p.uklad(pos=(zn * 0.07, -0.66, dz), obrot=(kat, 0, zn * 6)):
                    p.kula("Lotka", (0, -dl / 2 + 0.04, 0), (0.12, dl, 0.26), "pioro", segm=8)

    # ------------------------------------------------------------------ świetliki ze skrzydełkami (krążą wokół tułowia)
    for nazwa, r, y, kat in SWIETLIKI:
        a = math.radians(kat)
        with p.na(nazwa, od="staw"), p.uklad(pos=(r * math.sin(a), y - Y_SRODKA, r * math.cos(a)), obrot=(0, kat, 0)):
            p.kula("Swietlik", (0, -0.02, 0), (0.15, 0.17, 0.15), "swietlik", "swiecacy", segm=10)
            for zn in (1, -1):                         # skrzydełka w „V” nad świecącym odwłokiem
                p.kula("Swietlik skrzydelko", (zn * 0.07, 0.08, 0), (0.16, 0.05, 0.1), "skrzydelko", "polysk",
                       rot=(0, 0, zn * 35), segm=8)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_STAWU, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, gy + gh / 2 + 0.45 - 1.16, 0))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 0)
    return p


SLABOSCI = [
    "Na arkuszu nie ma widoku z boku: bok jest dorobiony z widoku 3/4 (skrzydło, latarenka, głowa-kostka).",
    "Mina „oczy zamknięte” z arkusza nie jest odwzorowana — model ma jedną minę (oczy otwarte, świecące).",
    "Świecenie (oczy, latarenka, świetliki) w Roblox to materiał Neon; poświata dookoła — PointLight w grze.",
    "Głowa to klocek z fazą — w Blenderze zaokrąglony, w Roblox (Part) ma ostre krawędzie.",
    "Latarenka jest przyczepiona do tułowia (bez własnej kości) — nie kołysze się.",
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
