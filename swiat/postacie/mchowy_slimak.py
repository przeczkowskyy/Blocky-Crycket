# -*- coding: utf-8 -*-
"""MCHOWY ŚLIMAK — pet zwykły z leśnego jajka (próba swiat/pety_proba; status: propozycja).

Przebudowa 25/26.11.2026 według arkusza obrotów Pawła (`mchowy_slimak_obroty.jpg`: cztery widoki 3/4 z buzią, BEZ
widoku z tyłu — tył uzupełniony z boków i z modelu z 17.11). Wzór wyglądu: bladozielony ślimak (ok. 2,4 studa
długości, 2,3 studa wysokości z grzybkiem) z DUŻĄ głową w kształcie kostki (szerszą niż wysoka, buzia z przodu:
oczy z odblaskiem, uśmiech, rumieńce), na niej dwa czułki z zielonymi kulkami; długa stopa z jaśniejszą podeszwą,
zwężona w ogonek; kanciasta brązowa muszla z kwadratową spiralą na obu bokach, czapa mchu w kępkach i czerwony
grzybek w białe kropki na grzbiecie. Kości, nazwy kości i klipy jak w modelu z 17.11.

    python -B swiat/postacie/przebuduj.py mchowy_slimak --bez-filmow

Budowa (typ="stwor", patrzy w +Z, lewa = +X):
  Root > Cialo > {Glowa > {CzulekL, CzulekP}, Muszla > Grzybek}
Klipy: spoczynek, chod (sunięcie z falowaniem stopy, pętla), radosc, wyklucie.
"""
from swiat.postacie.biblioteka.postac import Postac
from swiat.postacie.pety_lesne import klip_radosc, klip_wyklucie, lata, model, naklejka

ID = "mchowy_slimak"

PALETA = {
    "cialo": "A8CF8C", "cialo_jasne": "D6ECC2", "cialo_ciemne": "86B26C",
    "muszla": "7A4A28", "muszla_ciemna": "4A2A14", "muszla_jasna": "9A6338",
    "mech": "5FA83A", "mech_jasny": "82C94E",
    "grzyb": "D9412F", "kropka": "FFF4E6", "trzon": "F2E6CC",
    "oko": "1E1A14", "rumieniec": "F3A0A0", "buzia": "2E3A1E",
}

STOPA = ((0.0, 0.34, -0.22), (0.98, 0.68, 2.44))        # elipsoida stopy: środek, średnice
GLOWA = ((0.0, 1.03, 0.55), (1.1, 1.0, 0.9))          # „kostka” głowy: środek, rozmiar
MUSZLA = ((0.0, 0.98, -0.4), (1.02, 1.2, 1.24))
Y_STOPY, Z_STOPY = 0.3, 0.0


def _plasko(p, nazwa, x, y, size, kolor, mat="matowy", ksztalt="kula", obrot=0.0, wysun=0.0):
    """Bryła płaska na przedniej ścianie głowy-kostki (z = przód głowy)."""
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    pos = (x, y, gz + gd / 2 + size[2] / 2 - 0.012 + wysun)
    if ksztalt == "kula":
        return p.kula(nazwa, pos, size, kolor, mat, rot=(0, 0, obrot), segm=12)
    return p.blok(nazwa, pos, size, kolor, mat, rot=(0, 0, obrot), faza=0.0)


def zbuduj():
    p = Postac(ID, "Mchowy Ślimak", typ="stwor", skala=1.0, faza=0.07, paleta=PALETA)
    (sx, sy, sz), (sw, sh, sd) = STOPA
    (gx, gy, gz), (gw, gh, gd) = GLOWA
    (mx, my, mz), (mw, mh, md) = MUSZLA
    p.kosc("Cialo", "Root", staw=(0, Y_STOPY, Z_STOPY), czesc=(sw, sh, sd), srodek=(sx, sy - Y_STOPY, sz - Z_STOPY))
    p.kosc("Glowa", "Cialo", staw=(0, 0.5, gz), czesc=(gw, gh, gd), srodek=(0, gy - 0.5, 0))
    for s, zn in (("L", 1), ("P", -1)):
        p.kosc("Czulek" + s, "Glowa", staw=(zn * 0.27, gy + gh / 2 - 0.04, gz + 0.12), czesc=(0.09, 0.4, 0.09),
               srodek=(0, 0.2, 0))
    p.kosc("Muszla", "Cialo", staw=(0, 0.45, -0.32), czesc=(mw, mh, md), srodek=(0, my - 0.45, mz + 0.32))
    p.kosc("Grzybek", "Muszla", staw=(0.1, my + mh / 2 + 0.2, -0.52), czesc=(0.5, 0.48, 0.5), srodek=(0, 0.24, 0))

    # ------------------------------------------------------------------ stopa: długa, zwężona w ogonek, jasna podeszwa
    with model(p, "Cialo"):
        p.kula("Stopa", (sx, sy, sz), (sw, sh, sd), "cialo", segm=24)
        p.kula("Spod stopy", *lata(STOPA, (0, -1, 0.25), 0.45, s=0.12), "cialo_jasne", "matowy", segm=24)
        p.kula("Ogonek stopy", (0, 0.15, -1.22), (0.46, 0.28, 0.84), "cialo", rot=(-6, 0, 0), segm=16)

    # ------------------------------------------------------------------ głowa-kostka z buzią
    with model(p, "Glowa"):
        p.blok("Glowa", (gx, gy, gz), (gw, gh, gd), "cialo", faza=0.16)
        for zn, s in ((1, "L"), (-1, "P")):
            _plasko(p, "Oko " + s, zn * 0.24, gy - 0.01, (0.15, 0.19, 0.05), "oko", "polysk")
            _plasko(p, "Blysk " + s, zn * 0.24 + 0.03, gy + 0.035, (0.06, 0.06, 0.025), "bialy", "swiecacy",
                    wysun=0.02)
            _plasko(p, "Rumieniec " + s, zn * 0.36, gy - 0.15, (0.15, 0.07, 0.03), "rumieniec")
        _plasko(p, "Buzia", 0, gy - 0.17, (0.08, 0.035, 0.03), "buzia", ksztalt="blok")
        for zn in (1, -1):
            _plasko(p, "Buzia", zn * 0.065, gy - 0.152, (0.07, 0.035, 0.03), "buzia", ksztalt="blok", obrot=zn * 35)

    # ------------------------------------------------------------------ czułki z zielonymi kulkami (oczka z kropką)
    for s, zn in (("L", 1), ("P", -1)):
        with p.na("Czulek" + s, od="staw"), p.uklad(obrot=(-8, 0, -zn * 10)):
            p.walec("Czulek", (0, 0.19, 0), (0.08, 0.4, 0.08), "cialo", segm=8, faza=0.0)
            p.kula("Kulka", (0, 0.44, 0), (0.21, 0.21, 0.21), "cialo", segm=14)
            naklejka(p, "Kropka oka", ((0, 0.44, 0), (0.21, 0.21, 0.21)), 0, 0.44, (0.09, 0.1, 0.04), "oko", "polysk")

    # ------------------------------------------------------------------ muszla: kanciasta, kwadratowa spirala na bokach
    with model(p, "Muszla"):
        p.blok("Muszla", (mx, my, mz), (mw, mh, md), "muszla", faza=0.22)
        R, t, g = 0.36, 0.09, 0.2                       # połowa boku spirali, grubość rowka, odstęp zwojów
        odcinki = [((0, R), (2 * R + t, t)), ((R, 0), (t, 2 * R + t)), ((0, -R), (2 * R + t, t)),
                   ((-R, -g / 2), (t, 2 * R - g + t)), ((-g / 2, R - g), (2 * R - g + t, t)),
                   ((R - g, 0), (t, 2 * R - 2 * g + t)), ((R - 1.5 * g, -R + g), (g + t, t))]
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * (mw / 2 + 0.012)
            for (u, v), (du, dv) in odcinki:
                # u wzdłuż boku (+u ku przodowi), v w górę; po prawej stronie lustrzanie, żeby spirala kręciła się tak samo
                p.blok("Spirala " + s, (x, my + v, mz + zn * u), (0.03, dv, du), "muszla_ciemna", "matowy", faza=0.0)
        p.kula("Mech", (0, my + mh / 2 + 0.0, mz), (mw + 0.14, 0.42, md + 0.14), "mech", "matowy", segm=16)
        for x, z, r in ((0.26, 0.3, 0.46), (-0.24, -0.32, 0.5), (0.22, -0.36, 0.4), (-0.26, 0.26, 0.42)):
            p.kula("Mech kepka", (x, my + mh / 2 + 0.12, mz + z), (r, 0.26, r), "mech_jasny" if x * z > 0 else "mech",
                   "matowy", segm=12)

    # ------------------------------------------------------------------ czerwony grzybek w białe kropki
    with p.na("Grzybek", od="staw"):
        p.walec("Trzon", (0, 0.11, 0), (0.17, 0.3, 0.17), "trzon", "matowy", segm=10, faza=0.02)
        KAP = ((0, 0.33, 0), (0.52, 0.34, 0.52))
        p.kula("Kapelusz", KAP[0], KAP[1], "grzyb", segm=16)
        for x, y in ((0.12, 0.42), (-0.14, 0.38), (0.02, 0.33)):
            naklejka(p, "Kropka", KAP, x, y, (0.09, 0.08, 0.03), "kropka")

    p.zaczep("RootAttachment", "Cialo", (0, -Y_STOPY, -Z_STOPY))
    p.zaczep("GlowaAttachment", "Muszla", (0, 1.92, -0.1))
    _klipy(p)
    p.ustaw_poze_renderu("spoczynek", 10)
    return p


SLABOSCI = [
    "Na arkuszu nie ma widoku z tyłu: tył (koniec stopy, tylna ściana muszli z mchem) jest dorobiony z boków arkusza.",
    "Głowa i muszla to klocki z fazą — w Blenderze zaokrąglone, w Roblox (Part) mają ostre krawędzie.",
    "Spirala na muszli to płaskie listewki (po sześć na bok), nie rowek.",
    "Stopa jest jedną sztywną bryłą — falowanie przy sunięciu robi przesunięcie kości, nie zginanie.",
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
