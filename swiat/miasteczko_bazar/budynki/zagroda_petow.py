# -*- coding: utf-8 -*-
"""Zagroda petów — miejsce, gdzie gracz odstawia pety, które zwykle chodzą za bohaterem (D-085). Sama zagroda: otwarty
wybieg za płotkiem z bramką na uliczkę, osiem legowisk = osiem miejsc na odstawione pety (znaczniki
`zagroda_miejsce_1…8`, w kształcie litery U wokół przejścia od bramki: po trzy przy bocznych płotach, dwa przy tylnym),
miski, koryto i siano. Opiekunka Jagoda stoi PRZED zagrodą, obok bramki od strony uliczki (E → okno zagrody, okno
w HUD robi Paweł), więc nie zasłania petów. Jajek tu nie ma: jajka są w inkubatorach biomów (D-060).
Szyld: wielka łapa nad bramką.

Zmiana 25.11.2026 (sesja główna Karola i Pawła, „zagroda ma być tylko zagrodą”): bez ozdobnego psa, smoka, slime'a,
budki opiekunki i psiej budy; osiem miejsc zamiast sześciu; obrys zagrody bez zmian (26 × 20).
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402

NAZWA = "ZagrodaPetow"
OBRYS = (26, 20)
WYSOKOSC = 17
BUDZET = 330
KOD = "dach_wylegarnia"
Y_WYBIEGU = 0.2
# opiekunka przed zagrodą: na bruku uliczki (y 0 = wierzch bruku), obok prawego słupka bramki, twarzą do uliczki
OPIEKUNKA = (7.6, 11.8)
# osiem miejsc na odstawione pety (układ modułu: +z = bramka i uliczka): 1–2 przy bramce, potem w głąb, 7–8 przy tylnym
# płocie; kolejność = kolejność odblokowania (2 → 4 → 6 → 8)
MIEJSCA = ((-8.0, 4.6), (8.0, 4.6), (-8.0, -0.6), (8.0, -0.6), (-8.0, -5.8), (8.0, -5.8), (-3.4, -5.6), (3.4, -5.6))
KOLORY_LEGOWISK = ("dach_kolo", "dach_twierdza", "pomarancz", "dach_sklep", "dach_karczma", "dach_brama", "dach_gildia",
                   "dach_wylegarnia")


def buduj(s, rnd):
    W, D = OBRYS
    # wybieg: ziemia + kępy trawy (płaskie, bez kolizji ponad grunt)
    s.blok("Wybieg", (0, (Y_WYBIEGU - 0.15) / 2.0, 0), (W - 0.4, Y_WYBIEGU + 0.15, D - 0.4), "ziemia")
    with s.cechy(kolizja=False, cien=False):
        for x, z, a, b, k in ((-7.5, 2.0, 7.0, 5.0, 10), (7.0, 4.0, 6.0, 4.5, -14), (-2.0, 7.5, 5.0, 2.6, 4),
                              (8.5, -6.0, 5.0, 3.5, 20)):
            s.blok("Łata trawy", (x, Y_WYBIEGU + 0.05, z), (a, 0.1, b), "trawa", rot=(0, k, 0))
    # płotek (do przeskoczenia, 3) z bramką 10 na środku frontu
    zestaw.plot(s, [(-W / 2.0 + 0.5, D / 2.0 - 0.6), (-5.0, D / 2.0 - 0.6)], rnd)
    zestaw.plot(s, [(5.0, D / 2.0 - 0.6), (W / 2.0 - 0.5, D / 2.0 - 0.6)], rnd)
    zestaw.plot(s, [(-W / 2.0 + 0.5, D / 2.0 - 0.6), (-W / 2.0 + 0.5, -D / 2.0 + 0.5)], rnd)
    zestaw.plot(s, [(W / 2.0 - 0.5, D / 2.0 - 0.6), (W / 2.0 - 0.5, -D / 2.0 + 0.5)], rnd)
    zestaw.plot(s, [(-W / 2.0 + 0.5, -D / 2.0 + 0.5), (W / 2.0 - 0.5, -D / 2.0 + 0.5)], rnd, wys=3.4)
    _bramka(s)
    # opiekunka PRZED zagrodą, przy bramce (na bruku), lekko zwrócona ku przejściu
    ox, oz = OPIEKUNKA
    postacie.postac(s, "opiekunka", NAZWA + "/Opiekunka", (ox, 0.0, oz), ry=-14)
    wspolne.punkt_e(s, NAZWA, "zagroda_petow", (ox - 0.8, 0.0, oz + 4.6), (ox - 0.2, 4.6, oz + 0.6), typ="zagroda",
                    sklep="zagroda_petow", nazwa="Zagroda petów (opiekunka)", okno="Okno zagrody petów (Paweł)",
                    postac="opiekunka", model=NAZWA + "/Opiekunka", kier=(0, 0, 1))
    # legowiska = miejsca na odstawione pety (bez kolizji: pet i gracz stają na nich)
    with s.cechy(kolizja=False):
        for (x, z), kol in zip(MIEJSCA, KOLORY_LEGOWISK):
            s.walec("Legowisko", (x, Y_WYBIEGU + 0.25, z), 1.7, 0.5, kol, "Fabric", os="y")
            s.walec("Legowisko rant", (x, Y_WYBIEGU + 0.45, z), 1.9, 0.3, cien(s, kol, 0.8), "Fabric", os="y")
        # miski z kością przy bramce (w przejściu, nie na legowiskach)
        for x, z in ((-3.6, 7.4), (3.8, 7.6)):
            s.walec("Miska", (x, Y_WYBIEGU + 0.35, z), 0.9, 0.7, KOD, os="y")
            s.blok("Kość", (x + 0.1, Y_WYBIEGU + 0.8, z), (1.3, 0.3, 0.3), "biel", rot=(0, 35, 0))
    # koryto z wodą przy tylnym płocie, między miejscami 7 i 8; siano w tylnych narożnikach
    s.blok("Koryto", (0, 1.0, -8.3), (3.0, 1.6, 1.6), "drewno", "WoodPlanks")
    with s.cechy(kolizja=False):
        s.blok("Koryto woda", (0, 1.75, -8.3), (2.4, 0.15, 1.1), "woda")
    for x, k in ((11.0, 8), (-11.0, -6)):
        s.blok("Siano", (x, Y_WYBIEGU + 1.0, -8.4), (2.4, 2.0, 1.8), "dach_stajnia", rot=(0, k, 0))
    for i, (x, z) in enumerate(MIEJSCA):
        wspolne.znacznik(s, "miejsce_peta", "zagroda_miejsce_%d" % (i + 1), (x, Y_WYBIEGU, z),
                         opis="miejsce na odstawionego peta (Zagroda petów)")
    zestaw.wypadniety_klocek(s, (-W / 2.0 + 2.5, 1.6, D / 2.0 - 0.3), (-W / 2.0 + 3.0, 0, D / 2.0 + 0.9), "biel")


def _lapa(s):
    """Wielka łapa (szyld) w płaszczyźnie XY: poduszka i cztery palce w pomarańczu przechodzą przez płetwę tuszem, więc
    łapę widać z obu stron (jak szyld dzisiejszej wylęgarni). Bez liter."""
    s.walec("Łapa obrys", (0, -1.0, -0.3), 2.9, 0.4, "tusz", os="z")
    s.walec("Łapa poduszka", (0, -1.0, -0.3), 2.5, 1.4, "pomarancz", os="z")
    for a in (-55, -20, 20, 55):
        r = math.radians(a)
        p = (3.2 * math.sin(r), -1.0 + 3.3 * math.cos(r))
        s.walec("Łapa obrys", (p[0], p[1], -0.3), 1.3, 0.4, "tusz", os="z")
        s.walec("Łapa palec", (p[0], p[1], -0.3), 0.95, 1.4, "pomarancz", os="z")


def _bramka(s):
    """Dwa słupki bramki, krzywa poprzeczka i łapa-szyld nad przejściem 10 (prześwit 9)."""
    z = OBRYS[1] / 2.0 - 0.6
    for x, k in ((-5.4, 4), (5.4, -5)):
        s.blok("Słupek bramki", (x, 4.6, z), (0.9, 9.2, 0.9), "drewno", "Wood", rot=(0, 0, k))
    with s.cechy(kolizja=False):
        s.blok("Poprzeczka", (0, 9.4, z), (12.4, 0.9, 1.0), "drewno_ciemne", "Wood", rot=(0, 0, -3))
        with s.uklad(pos=(0.4, 12.6, z + 0.2), obrot=(-6, 0, 9)):
            _lapa(s)
        zestaw.choragiewka_duetu(s, (-5.8, 9.4, z), "kot", przechyl=-12)
