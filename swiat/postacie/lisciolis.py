# -*- coding: utf-8 -*-
"""LIŚCIOLIS — pet rzadki z leśnego jajka (próba swiat/pety_proba; status: propozycja).

Przebudowa 25/26.11.2026 według arkusza obrotów Pawła (`lisciolis_obroty.jpg`: przód, bok, tył, drugi bok). Wzór
wyglądu: bardzo „chibi” lisek (ok. 2,6 studa z uszami): WIELKA kanciasta głowa z płaskim czubkiem, szersza na dole
(puszyste policzki na boki), kremowa dolna połowa pyszczka z małym noskiem, kremowe plamki-brwi, uszy z dużych
zielonych liści, kołnierz z liści na szyi, mały tułów z kremową piersią, krótkie łapki w ciemnych skarpetkach,
puszysty ogon zadarty w górę z liściem na końcu. Kości, nazwy kości i klipy jak w modelu z 17.11.

    python -B swiat/postacie/przebuduj.py lisciolis --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa > {UchoL, UchoP}, LapaPrzodL/P, LapaTylL/P, Ogon > OgonLisc}
Klipy: spoczynek, chod (kłus po przekątnej, pętla), radosc (podskok z merdaniem), wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, lata, model

ID = "lisciolis"

PALETA = {
    "lis": "EE8838", "lis_ciemny": "C96A26", "krem": "FFE3C2", "skarpetki": "5A3420",
    "lisc": "4FAE3C", "lisc_ciemny": "2F7A2A", "lisc_jasny": "7CCB55", "nos": "2A1A14", "oko": "3A2216",
}

TULOW = ((0.0, 0.66, -0.1), (0.86, 0.6, 1.1))        # elipsoida tułowia
GLOWA = ((0.0, 1.45, 0.22), (1.22, 1.05, 1.15))      # kanciasta głowa: środek, rozmiar
Y_TULOWIA = 0.62
LAPY = [("Przod", 0.25), ("Tyl", -0.42)]


def _lisc(p, nazwa, dl, szer, grub, kolor, kolor_zylki):
    """Liść w płaszczyźnie XY bieżącego układu: nasada w (0, 0, 0), czubek w +Y; elipsoida + żyłka (2 bryły)."""
    p.kula(nazwa, (0, dl / 2, 0), (szer, dl, grub), kolor, "matowy", segm=14)
    p.blok(nazwa + " zylka", (0, dl * 0.48, grub / 2 - 0.005), (0.04, dl * 0.8, 0.02), kolor_zylki, "matowy", faza=0.0)


def _twarz(p, nazwa, x, y, size, kolor, mat="matowy", ksztalt="kula", z=None):
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    pos = (x, y, (gz + gd / 2 if z is None else z) + size[2] / 2 - 0.012)
    if ksztalt == "kula":
        return p.kula(nazwa, pos, size, kolor, mat, segm=12)
    return p.blok(nazwa, pos, size, kolor, mat, faza=0.0)


def zbuduj():
    p = Postac(ID, "Liściolis", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    (tx, ty, tz), (tw, th, td) = TULOW
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=(tw, th, td), srodek=(tx, ty - Y_TULOWIA, tz))
    p.kosc("Glowa", "Tulow", staw=(0, 0.9, 0.25), czesc=(gw, gh, gd), srodek=(gx, gy - 0.9, gz - 0.25))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Ucho" + s, "Glowa", staw=(zn * 0.38, gy + gh / 2 - 0.04, 0.12), czesc=(0.5, 0.66, 0.08),
               srodek=(zn * 0.1, 0.32, 0))
        for przod, z in LAPY:
            p.kosc("Lapa%s%s" % (przod, s), "Tulow", staw=(zn * 0.25, 0.45, z), czesc=(0.26, 0.45, 0.26),
                   srodek=(0, -0.22, 0))
    p.kosc("Ogon", "Tulow", staw=(0, 0.8, -0.58), czesc=(0.5, 0.5, 0.95), srodek=(0, 0.37, -0.26))
    KAT_OGONA = 68.0
    ka = math.radians(KAT_OGONA)
    dl_ogona = 0.86
    koniec = (0, 0.8 + dl_ogona * math.sin(ka), -0.58 - dl_ogona * math.cos(ka))
    p.kosc("OgonLisc", "Ogon", staw=koniec, czesc=(0.34, 0.5, 0.08), srodek=(0, 0.24, 0))

    # ------------------------------------------------------------------ tułów z kremową piersią i kołnierzem z liści
    with model(p, "Tulow"):
        p.kula("Tulow", (tx, ty, tz), (tw, th, td), "lis", segm=20)
        p.kula("Piers", *lata(TULOW, (0, -0.35, 1), 0.35, s=0.12), "krem", "matowy", segm=20)
        p.kula("Kolnierz", (0, 0.9, 0.2), (0.98, 0.16, 0.86), "lisc", "matowy", segm=16)
        for kat in (-70, -35, 0, 35, 70):
            a = math.radians(kat)
            with p.uklad(pos=(0.42 * math.sin(a), 0.86, 0.2 + 0.4 * math.cos(a)), obrot=(0, kat, 0)):
                with p.uklad(obrot=(-145, 0, 0)):          # liść zwisa w dół i lekko na zewnątrz
                    p.kula("Kolnierz lisc", (0, 0.13, 0), (0.22, 0.3, 0.06),
                           "lisc_jasny" if kat == 0 else "lisc", "matowy", segm=10)

    # ------------------------------------------------------------------ głowa: kostka, puszyste policzki, kremowy pyszczek
    with model(p, "Glowa"):
        p.blok("Glowa", (gx, gy, gz), (gw, gh, gd), "lis", faza=0.2)
        p.blok("Maska", (0, gy - 0.33, gz + 0.3), (gw + 0.02, 0.38, gd - 0.56), "krem", "matowy", faza=0.12)
        p.blok("Maska szczyt", (0, gy - 0.12, gz + gd / 2 - 0.02), (0.26, 0.26, 0.06), "krem", "matowy",
               rot=(0, 0, 45), faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            p.kula("Policzek " + s, (zn * 0.6, gy - 0.4, gz + 0.3), (0.32, 0.17, 0.32), "krem", "matowy",
                   rot=(0, 0, -zn * 22), segm=12)
            _twarz(p, "Oko " + s, zn * 0.29, gy - 0.02, (0.16, 0.2, 0.05), "oko", "polysk")
            _twarz(p, "Blysk " + s, zn * 0.29 + 0.035, gy + 0.03, (0.065, 0.065, 0.025), "bialy", "swiecacy",
                   z=gz + gd / 2 + 0.02)
            _twarz(p, "Blysk " + s, zn * 0.29 - 0.035, gy - 0.07, (0.03, 0.03, 0.02), "bialy", "swiecacy",
                   z=gz + gd / 2 + 0.02)
            _twarz(p, "Brew " + s, zn * 0.3, gy + 0.22, (0.15, 0.08, 0.03), "krem")
        p.blok("Pyszczek", (0, gy - 0.26, gz + gd / 2 + 0.08), (0.36, 0.24, 0.2), "krem", "matowy", faza=0.07)
        p.kula("Nos", (0, gy - 0.19, gz + gd / 2 + 0.19), (0.14, 0.1, 0.08), "nos", "polysk", segm=10)
        zp = gz + gd / 2 + 0.18                            # przód pyszczka: pyszczek „ω” z trzech kresek
        p.blok("Buzia", (0, gy - 0.29, zp + 0.005), (0.03, 0.08, 0.03), "nos", "matowy", faza=0.0)
        for zn in (1, -1):
            p.blok("Buzia", (zn * 0.05, gy - 0.335, zp + 0.005), (0.09, 0.03, 0.03), "nos", "matowy",
                   rot=(0, 0, zn * 28), faza=0.0)

    # ------------------------------------------------------------------ uszy-liście
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Ucho" + s, od="staw"), p.uklad(obrot=(-6, zn * 22, -zn * 30)):
            _lisc(p, "Ucho", 0.72, 0.5, 0.07, "lisc", "lisc_ciemny")

    # ------------------------------------------------------------------ łapki w ciemnych skarpetkach
    for s in ("L", "P"):
        for przod, _z in LAPY:
            with p.na("Lapa%s%s" % (przod, s), od="staw"):
                p.walec("Lapa", (0, -0.2, 0), (0.25, 0.42, 0.25), "lis", segm=12, faza=0.03)
                p.walec("Skarpetka", (0, -0.355, 0.01), (0.28, 0.2, 0.29), "skarpetki", "matowy", segm=12, faza=0.04)

    # ------------------------------------------------------------------ puszysty ogon zadarty w górę, liść na końcu
    with p.na("Ogon", od="staw"), p.uklad(obrot=(KAT_OGONA, 0, 0)):
        p.kula("Ogon", (0, 0.02, -0.44), (0.64, 0.64, 0.92), "lis", segm=18)
    with p.na("OgonLisc", od="staw"), p.uklad(obrot=(-25, 0, 0)):
        _lisc(p, "Lisc ogona", 0.52, 0.32, 0.07, "lisc", "lisc_ciemny")

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, gy + gh / 2 + 0.75 - 0.9, gz - 0.25))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 12)
    return p


SLABOSCI = [
    "Łapy są jednoczęściowe (bez kolan) — kłus to wymach całej łapy.",
    "Głowa to klocek z fazą — w Blenderze zaokrąglony, w Roblox (Part) ma ostre krawędzie (arkusz: „kanciasta głowa”).",
    "Liście (uszy, ogon, kołnierz) to spłaszczone elipsoidy — końce są zaokrąglone, nie szpiczaste jak na rysunku.",
]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.02, 0), czestosc=2)
    k.cykl("Glowa", "obrot", (3, 0, 5), czestosc=1, faza=0.25)
    k.cykl("UchoL", "obrot", (0, 0, 7), czestosc=2)
    k.cykl("UchoP", "obrot", (0, 0, -7), czestosc=2, faza=0.1)
    k.cykl("Ogon", "obrot", (4, 14, 0), czestosc=1)
    k.cykl("OgonLisc", "obrot", (0, 0, 10), czestosc=2, faza=0.2)

    k = p.klip("chod", 20, petla=True)
    for s in ("L", "P"):
        for przod, _z in LAPY:
            # kłus: lewa przednia z prawą tylną, prawa przednia z lewą tylną
            faza = 0.0 if (s == "L") == (przod == "Przod") else 0.5
            k.cykl("Lapa%s%s" % (przod, s), "obrot", (32, 0, 0), czestosc=1, faza=faza)
    k.cykl("Tulow", "przes", (0, 0.05, 0), czestosc=2, srodek=(0, 0.03, 0))
    k.cykl("Tulow", "obrot", (3, 0, 0), czestosc=2)
    k.cykl("Glowa", "obrot", (4, 0, 0), czestosc=2, faza=0.1)
    k.cykl("UchoL", "obrot", (8, 0, 0), czestosc=2, faza=0.2)
    k.cykl("UchoP", "obrot", (8, 0, 0), czestosc=2, faza=0.25)
    k.cykl("Ogon", "obrot", (0, 12, 0), czestosc=1, srodek=(-8, 0, 0))
    k.cykl("OgonLisc", "obrot", (0, 0, 14), czestosc=2)

    def dodatki(k, szczyt, koniec, uszy_zlozone=False):
        for s, zn in (("L", 1), ("P", -1)):
            k.klucz(0, "Ucho" + s, obrot=(60, 0, 0) if uszy_zlozone else (0, 0, 0))
            k.klucz(szczyt, "Ucho" + s, obrot=(-20, 0, zn * 20))
            k.klucz(szczyt + 6, "Ucho" + s, obrot=(10, 0, -zn * 10))
            k.klucz(koniec, "Ucho" + s, obrot=(0, 0, 0))
            k.klucz(0, "LapaPrzod" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "LapaPrzod" + s, obrot=(-45, 0, 0))
            k.klucz(koniec, "LapaPrzod" + s, obrot=(0, 0, 0))
        for i, f in enumerate(range(0, koniec, 4)):                                   # szybkie merdanie
            k.klucz(f, "Ogon", obrot=(0, 0 if f == 0 else (28 if i % 2 else -28), 0))
        k.klucz(koniec, "Ogon", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.7, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.05, wyskok=0.95, dodatki=lambda k: dodatki(k, 12, 30, uszy_zlozone=True))
