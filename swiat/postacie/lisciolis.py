# -*- coding: utf-8 -*-
"""LIŚCIOLIS — pet rzadki z leśnego jajka (próba swiat/pety_proba, 17.11.2026; status: propozycja, własny projekt).

Mały pomarańczowy lis (ok. 2,5 studa z uszami, 2,5 studa długości z ogonem): duża głowa z kremowym pyszczkiem,
uszy w kształcie zielonych liści, ciemne „skarpetki”, puszysty ogon zakończony liściem i liściasty kołnierzyk.
Sylwetka: czworonóg z wielkim ogonem i szpiczastymi uszami — rzadki, więc żywsze kolory niż pospolite pety.

    python -B swiat/postacie/przebuduj.py lisciolis --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa > {UchoL, UchoP}, LapaPrzodL/P, LapaTylL/P, Ogon > OgonLisc}
Klipy: spoczynek, chod (kłus po przekątnej, pętla), radosc (podskok z merdaniem), wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "lisciolis"

PALETA = {
    "lis": "E8792E", "lis_ciemny": "B85A1E", "krem": "FFE6C7", "skarpetki": "5A3420",
    "lisc": "5DBB4A", "lisc_ciemny": "3E8A34", "lisc_jasny": "8BD866", "nos": "1A1210",
}

TULOW = (0.9, 0.72, 1.35)
Y_TULOWIA = 0.85
GLOWA = (1.05, 0.88, 0.9)
LAPY = [("Przod", 0.42), ("Tyl", -0.48)]


def _lisc(p, nazwa, dl, szer, grub, kolor, kolor_zylki):
    """Liść pionowy (płaszczyzna XY bieżącego układu): podstawa w (0, 0, 0), czubek w górę (+Y). 4 bryły."""
    p.blok(nazwa, (0, dl * 0.3, 0), (szer, dl * 0.6, grub), kolor, "matowy", faza=0.03)
    p.klin(nazwa + " czubek", (szer * 0.25, dl * 0.8, 0), (grub, dl * 0.4, szer * 0.5), kolor, "matowy",
           rot=(0, -90, 0), faza=0.0)
    p.klin(nazwa + " czubek", (-szer * 0.25, dl * 0.8, 0), (grub, dl * 0.4, szer * 0.5), kolor, "matowy",
           rot=(0, 90, 0), faza=0.0)
    p.blok(nazwa + " zylka", (0, dl * 0.45, grub / 2 + 0.01), (0.05, dl * 0.75, 0.02), kolor_zylki, "matowy", faza=0.0)


def zbuduj():
    p = Postac(ID, "Liściolis", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, 0, -0.05))
    p.kosc("Glowa", "Tulow", staw=(0, 1.15, 0.5), czesc=GLOWA, srodek=(0, 0.3, 0.3))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Ucho" + s, "Glowa", staw=(zn * 0.33, 1.84, 0.74), czesc=(0.42, 0.7, 0.14), srodek=(zn * 0.04, 0.32, 0))
        for przod, z in LAPY:
            p.kosc("Lapa%s%s" % (przod, s), "Tulow", staw=(zn * 0.27, 0.6, z), czesc=(0.26, 0.6, 0.28),
                   srodek=(0, -0.3, 0))
    p.kosc("Ogon", "Tulow", staw=(0, 1.0, -0.68), czesc=(0.52, 0.52, 0.9), srodek=(0, 0.28, -0.34))
    p.kosc("OgonLisc", "Ogon", staw=(0, 1.55, -1.36), czesc=(0.12, 0.8, 0.6), srodek=(0, 0.3, -0.1))

    # ------------------------------------------------------------------ tułów
    with p.na("Tulow", od="srodek"):
        w, h, d = TULOW
        p.blok("Tulow", (0, 0, 0), TULOW, "lis", faza=0.12)
        p.blok("Piers", (0, -0.02, d / 2 + 0.02), (0.62, 0.52, 0.08), "krem", "matowy", faza=0.03)
        p.blok("Brzuch", (0, -h / 2 - 0.02, 0.1), (0.6, 0.06, 0.9), "krem", "matowy", faza=0.02)
        p.blok("Kolnierz", (0, 0.3, d / 2 - 0.2), (w + 0.1, 0.2, 0.46), "lisc", "matowy", faza=0.05)
        for zn in (1, -1):
            p.blok("Kolnierz listek", (zn * 0.36, 0.18, d / 2 + 0.03), (0.3, 0.26, 0.06), "lisc_jasny", "matowy",
                   rot=(0, 0, zn * 35), faza=0.0)

    # ------------------------------------------------------------------ głowa
    with p.na("Glowa", od="srodek"):
        w, h, d = GLOWA
        z = d / 2
        p.blok("Glowa", (0, 0, 0), GLOWA, "lis", faza=0.14)
        p.blok("Pyszczek", (0, -0.2, z + 0.16), (0.46, 0.3, 0.4), "krem", "matowy", faza=0.07)
        p.blok("Nos", (0, -0.09, z + 0.37), (0.16, 0.12, 0.07), "nos", "polysk", faza=0.03)
        oczy(p, 0.25, 0.12, z, szer=0.2, wys=0.27)
        p.blok("Maska", (0, -0.27, 0.2), (w + 0.04, 0.3, 0.54), "krem", "matowy", faza=0.08)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Policzek " + s, (zn * (w / 2 + 0.06), -0.3, 0.16), (0.12, 0.18, 0.3), "krem", "matowy",
                   rot=(0, 0, zn * 28), faza=0.03)

    # ------------------------------------------------------------------ uszy-liście
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Ucho" + s, od="staw"), p.uklad(obrot=(0, 0, -zn * 14)):
            _lisc(p, "Ucho", 0.72, 0.42, 0.14, "lisc", "lisc_ciemny")

    # ------------------------------------------------------------------ łapy (ciemne skarpetki)
    for s in ("L", "P"):
        for przod, _z in LAPY:
            with p.na("Lapa%s%s" % (przod, s), od="srodek"):
                p.blok("Lapa", (0, 0.06, 0), (0.26, 0.48, 0.28), "lis_ciemny" if przod == "Tyl" else "lis", faza=0.05)
                p.blok("Skarpetka", (0, -0.22, 0.02), (0.3, 0.18, 0.34), "skarpetki", "matowy", faza=0.04)

    # ------------------------------------------------------------------ puszysty ogon z liściem na końcu
    with p.na("Ogon", od="staw"), p.uklad(obrot=(38, 0, 0)):
        p.blok("Ogon", (0, 0, -0.42), (0.54, 0.54, 0.92), "lis", faza=0.14)
        p.blok("Ogon pasek", (0, 0, -0.84), (0.5, 0.5, 0.12), "krem", "matowy", faza=0.06)
    with p.na("OgonLisc", od="staw"), p.uklad(obrot=(-20, 0, 0)):
        _lisc(p, "Lisc ogona", 0.8, 0.5, 0.12, "lisc", "lisc_ciemny")

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 1.25, 0.3))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 12)
    return p


SLABOSCI = [
    "Łapy są jednoczęściowe (bez kolan) — kłus to wymach całej łapy.",
    "Liście uszu i ogona są płaskie (grubość 0,12–0,14) — z boku cienkie.",
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
