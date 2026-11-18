# -*- coding: utf-8 -*-
"""JAGUAREK — pet legendarny z jajka Dżungli (próba swiat/pety_proba, 18.11.2026; status: propozycja, własny projekt).

Kocię jaguara (ok. 2 studa, 2,8 studa długości z ogonem): złociste futro w czarne rozety ze świecącym turkusowym
środkiem, kremowy pyszczek i brzuch, okrągłe uszy, grube łapy, wianek z czerwonych i żółtych kwiatów na szyi i długi
ogon owinięty liną z listkiem i świecącym różowym kwiatkiem na końcu. Sylwetka: czworonóg z okrągłymi uszami i długim,
podniesionym ogonem — inny niż lis (szpiczaste uszy-liście, puszysty ogon) i jelonek (długie nogi, poroże).

    python -B swiat/postacie/przebuduj.py jaguarek --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Tulow > {Glowa, LapaPrzodL/P, LapaTylL/P, Ogon > OgonKoniec}
Klipy: spoczynek (ogon faluje), chod (skradanie po przekątnej), radosc (podskok z machnięciem ogona), wyklucie.
"""
import math

from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, oczy

ID = "jaguarek"

PALETA = {
    "futro": "E9B23A", "futro_ciemne": "C98E24", "krem": "FFF0D2", "rozeta": "2B2018", "rozeta_srodek": "2EC4B6",
    "nos": "6A3A2A", "kwiat_czerwony": "E5392B", "kwiat_zolty": "F2B030", "liana": "3E7D2E",
    "kwiat_jarzacy": "FF5FA2", "teczowka": "7FE0B0",
}

TULOW = (0.9, 0.7, 1.4)
Y_TULOWIA = 0.8
GLOWA = (1.0, 0.86, 0.86)
LAPY = [("Przod", 0.44), ("Tyl", -0.46)]
# rozety: (x, y, z) w układzie środka tułowia — czarny pierścień z turkusowym środkiem
ROZETY = ((0.46, 0.1, 0.3), (0.46, -0.06, -0.3), (-0.46, 0.08, 0.15), (-0.46, -0.04, -0.38), (0.0, 0.36, -0.1))


def _rozeta(p, x, y, z, bok):
    """Rozeta na ścianie bryły: bok = "x" (ściana boczna) albo "y" (grzbiet)."""
    if bok == "x":
        p.blok("Rozeta", (x, y, z), (0.04, 0.22, 0.22), "rozeta", "matowy", faza=0.03)
        p.blok("Rozeta srodek", (x + math.copysign(0.015, x), y, z), (0.04, 0.1, 0.1), "rozeta_srodek", "swiecacy",
               faza=0.0)
    else:
        p.blok("Rozeta", (x, y, z), (0.22, 0.04, 0.22), "rozeta", "matowy", faza=0.03)
        p.blok("Rozeta srodek", (x, y + 0.015, z), (0.1, 0.04, 0.1), "rozeta_srodek", "swiecacy", faza=0.0)


def zbuduj():
    p = Postac(ID, "Jaguarek", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    p.kosc("Tulow", "Root", staw=(0, Y_TULOWIA, 0), czesc=TULOW, srodek=(0, 0, 0))
    p.kosc("Glowa", "Tulow", staw=(0, 1.08, 0.62), czesc=GLOWA, srodek=(0, 0.26, 0.3))
    for s, zn in (("L", 1), ("P", -1)):
        for przod, z in LAPY:
            p.kosc("Lapa%s%s" % (przod, s), "Tulow", staw=(zn * 0.28, 0.6, z), czesc=(0.3, 0.6, 0.32),
                   srodek=(0, -0.3, 0.02))
    p.kosc("Ogon", "Tulow", staw=(0, 0.95, -0.7), czesc=(0.22, 0.22, 1.0), srodek=(0, 0.2, -0.45))
    p.kosc("OgonKoniec", "Ogon", staw=(0, 1.62, -1.42), czesc=(0.3, 0.6, 0.3), srodek=(0, 0.25, 0))

    with p.na("Tulow", od="srodek"):
        w, h, d = TULOW
        p.blok("Tulow", (0, 0, 0), TULOW, "futro", faza=0.14)
        p.blok("Brzuch", (0, -h / 2 - 0.02, 0.05), (0.62, 0.06, 1.0), "krem", "matowy", faza=0.02)
        p.blok("Piers", (0, -0.06, d / 2 + 0.02), (0.6, 0.46, 0.06), "krem", "matowy", faza=0.03)
        for x, y, z in ROZETY:
            _rozeta(p, math.copysign(w / 2 + 0.01, x) if x else 0.0, y if x else h / 2 + 0.01, z, "x" if x else "y")
        # wianek z kwiatów na szyi
        for i in range(5):
            a = math.radians(-80 + i * 40)
            p.blok("Kwiat wianka", (0.42 * math.sin(a), 0.16 + 0.1 * math.cos(a), d / 2 + 0.04),
                   (0.18, 0.18, 0.12), "kwiat_czerwony" if i % 2 else "kwiat_zolty", "matowy", rot=(0, 0, 45), faza=0.02)
    with p.na("Glowa", od="srodek"):
        gw, gh, gd = GLOWA
        z = gd / 2
        p.blok("Glowa", (0, 0, 0), GLOWA, "futro", faza=0.16)
        p.blok("Pyszczek", (0, -0.2, z + 0.12), (0.5, 0.3, 0.3), "krem", "matowy", faza=0.08)
        p.blok("Nos", (0, -0.08, z + 0.28), (0.18, 0.1, 0.06), "nos", "polysk", faza=0.03)
        oczy(p, 0.24, 0.1, z, szer=0.2, wys=0.24, teczowka="teczowka")
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Ucho " + s, (zn * 0.34, gh / 2 + 0.1, -0.05), (0.28, 0.26, 0.12), "rozeta", faza=0.08)
    for s in ("L", "P"):
        for przod, _z in LAPY:
            with p.na("Lapa%s%s" % (przod, s), od="srodek"):
                p.blok("Lapa", (0, 0.06, 0), (0.28, 0.5, 0.3), "futro" if przod == "Przod" else "futro_ciemne", faza=0.06)
                p.blok("Stopa", (0, -0.24, 0.05), (0.34, 0.14, 0.4), "krem", "matowy", faza=0.05)
    with p.na("Ogon", od="staw"), p.uklad(obrot=(42, 0, 0)):
        p.blok("Ogon", (0, 0, -0.5), (0.22, 0.22, 1.0), "futro", faza=0.08)
        p.blok("Liana ogona", (0, 0, -0.5), (0.26, 0.06, 0.62), "liana", "matowy", rot=(0, 0, 30), faza=0.0)
    with p.na("OgonKoniec", od="staw"):
        p.blok("Ogon koniec", (0, 0.15, 0), (0.22, 0.4, 0.22), "futro_ciemne", faza=0.06)
        for i in range(4):
            a = math.radians(i * 90 + 45)
            p.blok("Platek", (0.1 * math.cos(a), 0.44, 0.1 * math.sin(a)), (0.15, 0.05, 0.12), "kwiat_jarzacy",
                   "swiecacy", rot=(0, -math.degrees(a), 22), faza=0.0)

    p.zaczep("RootAttachment", "Tulow", (0, -Y_TULOWIA, 0))
    p.zaczep("GlowaAttachment", "Glowa", (0, 1.2, 0.3))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 12)
    return p


SLABOSCI = ["Łapy jednoczęściowe (bez kolan) — skradanie to wymach całej łapy, jak u Liściolisa."]


def _klipy(p):
    k = p.klip("spoczynek", 60, petla=True)
    k.cykl("Tulow", "przes", (0, 0.02, 0), czestosc=2)
    k.cykl("Glowa", "obrot", (3, 8, 0), czestosc=1, faza=0.25)
    k.cykl("Ogon", "obrot", (6, 18, 0), czestosc=1)
    k.cykl("OgonKoniec", "obrot", (0, 0, 16), czestosc=2, faza=0.2)

    k = p.klip("chod", 22, petla=True)
    for s in ("L", "P"):
        for przod, _z in LAPY:
            faza = 0.0 if (s == "L") == (przod == "Przod") else 0.5
            k.cykl("Lapa%s%s" % (przod, s), "obrot", (30, 0, 0), czestosc=1, faza=faza)
    k.cykl("Tulow", "przes", (0, 0.04, 0), czestosc=2, srodek=(0, 0.02, 0))
    k.cykl("Tulow", "obrot", (0, 4, 3), czestosc=1)
    k.cykl("Glowa", "obrot", (3, -4, 0), czestosc=1, faza=0.1)
    k.cykl("Ogon", "obrot", (6, 16, 0), czestosc=1, srodek=(-6, 0, 0))
    k.cykl("OgonKoniec", "obrot", (0, 0, 18), czestosc=2)

    def dodatki(k, szczyt, koniec):
        for s in ("L", "P"):
            k.klucz(0, "LapaPrzod" + s, obrot=(0, 0, 0))
            k.klucz(szczyt, "LapaPrzod" + s, obrot=(-50, 0, 0))
            k.klucz(koniec, "LapaPrzod" + s, obrot=(0, 0, 0))
        k.klucz(0, "Ogon", obrot=(0, 0, 0))
        k.klucz(szczyt, "Ogon", obrot=(-35, 0, 0))
        k.klucz(szczyt + 6, "Ogon", obrot=(10, 25, 0))
        k.klucz(koniec, "Ogon", obrot=(0, 0, 0))

    klip_radosc(p, "Tulow", wysokosc=0.75, dodatki=lambda k: dodatki(k, 15, 36))
    klip_wyklucie(p, "Tulow", glebokosc=1.05, wyskok=0.95, dodatki=lambda k: dodatki(k, 12, 30))
