# -*- coding: utf-8 -*-
"""Training Center — jeden budynek, jedno wejście, wybór mini-gry z jednej tablicy (D-063, D-074; w mieście wg D-085).

Miętowa bryła z różowym dachem (kod „koło” z palety — koła fortuny na bazarze nie ma, więc kolor jest wolny, a czerwień
zostaje dla karczmy). W środku na tylnej ścianie TABLICA WYBORU z sześcioma medalionami statystyk (Siła — miecz, Kondycja — serce,
Inteligencja — księga, Zręczność — strzała, Szczęście — koniczyna, Pancerz — tarcza), obok trener wskazujący tablicę
(E → okno wyboru mini-gry, które przenosi do mini-gry). Do tego słomiany manekin, hantle, mata i worek. Szyld: wielka
hantla przed piętrem i tarcza strzelnicza.
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402
from swiat.miasteczko_bazar.wspolne import Y_PODLOGI  # noqa: E402

NAZWA = "TrainingCenter"
OBRYS = (22, 20)
WYSOKOSC = 30
BUDZET = 360
SCIANA, DACH = "tynk_mieta", "dach_kolo"
ZB = -10.0 + 1.2
TRENER = (7.4, -5.6)
STATYSTYKI = ("sila", "kondycja", "inteligencja", "zrecznosc", "szczescie", "pancerz")


def buduj(s, rnd):
    info = wspolne.skorupa(s, rnd, 22, 20, SCIANA, DACH, H0=14.0, otwor=14.0, otwor_x=1.0, H_otw=12.6, hp=5.5,
                           nawis=(2.2, 0.4, 1.0, 0.8), rz_p=-5.0, ry_p=4.0, dach_h=8.0, rz_d=9.0, okap=2.6, podzial=0.6,
                           markiza=(DACH, "biel"), okna_pietra=("prostokat",), duet="rycerz", na_pietrze=_szyld)
    _tablica_wyboru(s)
    postacie.postac(s, "trener", NAZWA + "/Trener", (TRENER[0], Y_PODLOGI, TRENER[1]), ry=-28)
    wspolne.punkt_e(s, NAZWA, "training_center", (2.6, -1.6), (TRENER[0] - 0.3, Y_PODLOGI + 4.6, TRENER[1] + 0.5),
                    typ="training_center", sklep="training_center", nazwa="Training Center — wybór mini-gry",
                    okno="Okno wyboru mini-gry (Paweł)", postac="trener", model=NAZWA + "/Trener", statystyki=list(STATYSTYKI),
                    kier=(0, 0, 1))
    wspolne.lampa(s, (-3.0, 13.45, -1.0), lancuch=1.6)
    wspolne.lampa(s, (4.5, 13.45, 1.5), lancuch=2.2)
    _sprzet(s)
    zf = info["front"]
    zestaw.lata(s, (11.0, 4.0, 1.5), 2.6, 2.2, "dach_twierdza", ry=90)
    zestaw.wypadniety_klocek(s, (-9.0, 2.3, zf), (-9.8, 0, zf + 1.3), SCIANA)
    zestaw.kwiaty(s, (7.4, 0, zf + 1.3), ry=-3, kolory=("czerwien", "biel"))


def _hantla(s):
    """Hantla 10 × 4 (szyld): drążek metal_ciemny i po dwa krążki w kolorze kodu z rantem tuszem."""
    s.walec("Hantla drążek", (0, 0, 0), 0.45, 9.0, "metal_ciemny", os="x")
    for sx in (-1, 1):
        s.walec("Hantla krążek", (sx * 3.0, 0, 0), 2.0, 1.0, DACH, os="x")
        s.walec("Hantla krążek", (sx * 4.0, 0, 0), 1.6, 0.9, cien(s, DACH, 0.85), os="x")
        s.walec("Hantla rant", (sx * 3.0, 0, 0), 2.2, 0.4, "tusz", os="x")
    s.walec("Hantla uchwyt", (0, 0, 0), 0.55, 3.0, "biel", os="x")


def _szyld(s, p):
    wspolne.szyld_na_pietrze(s, p, 0.2 * p["W1"], _hantla, skala=1.0, ry=24, rz=12, wysun=2.4)
    with s.uklad(pos=(-0.05 * p["W1"], p["hp"] * 0.48, p["D1"] / 2.0 + 0.2), obrot=(0, 0, 8)), s.cechy(kolizja=False):
        s.walec("Tarcza strzelnicza", (0, 0, 0.0), 2.5, 0.3, "tusz", os="z")
        s.walec("Tarcza strzelnicza", (0, 0, 0.15), 2.2, 0.3, "biel", os="z")
        s.walec("Tarcza strzelnicza", (0, 0, 0.3), 1.45, 0.3, DACH, os="z")
        s.walec("Tarcza strzelnicza", (0, 0, 0.45), 0.7, 0.3, "biel", os="z")
        with s.uklad(pos=(0.3, 0.2, 0.6), obrot=(-20, 25, 0)):
            s.blok("Strzała", (0, 0, 1.6), (0.35, 0.35, 3.2), "drewno_jasne")
            s.blok("Strzała lotka", (0, 0, 3.0), (0.25, 1.1, 1.0), "zloto")


def _medalion(s, nr, kolor):
    """Medalion statystyki Ø 3,2 z symbolem z klocków (bez liter)."""
    s.walec("Medalion obrys", (0, 0, 0.0), 1.8, 0.3, "tusz", os="z")
    s.walec("Medalion", (0, 0, 0.2), 1.6, 0.3, kolor, os="z")
    z = 0.45
    with s.cechy(cien=False):
        if nr == 0:                                            # Siła — miecz
            s.blok("Symbol miecz", (0.15, 0.15, z), (0.45, 2.2, 0.2), "tynk_blekit", rot=(0, 0, -40))
            s.blok("Symbol jelec", (-0.45, -0.45, z + 0.05), (1.1, 0.35, 0.2), "zloto", rot=(0, 0, 50))
        elif nr == 1:                                          # Kondycja — serce
            s.blok("Symbol serce", (0, -0.25, z), (1.15, 1.15, 0.2), "czerwien", rot=(0, 0, 45))
            for sx in (-1, 1):
                s.walec("Symbol serce", (sx * 0.42, 0.25, z), 0.55, 0.2, "czerwien", os="z")
        elif nr == 2:                                          # Inteligencja — otwarta księga
            for sx in (-1, 1):
                s.blok("Symbol księga", (sx * 0.55, 0, z), (1.0, 1.3, 0.2), "biel", rot=(0, 0, -sx * 8))
            s.blok("Symbol grzbiet", (0, -0.1, z + 0.05), (0.25, 1.4, 0.2), "dach_sklep")
        elif nr == 3:                                          # Zręczność — strzała
            s.blok("Symbol strzała", (-0.1, -0.1, z), (0.3, 2.0, 0.2), "drewno_jasne", rot=(0, 0, -45))
            s.klin("Symbol grot", (0.6, 0.6, z), (0.2, 0.7, 0.8), "tynk_blekit", rot=(0, 90, -45))
        elif nr == 4:                                          # Szczęście — koniczyna
            for x, y in ((0, 0.45), (0.45, 0), (0, -0.45), (-0.45, 0)):
                s.walec("Symbol listek", (x, y + 0.15, z), 0.42, 0.2, "lisc_jasny", os="z")
            s.blok("Symbol łodyżka", (0.25, -0.75, z), (0.2, 0.8, 0.2), "lisc_ciemny", rot=(0, 0, 25))
        else:                                                  # Pancerz — tarcza
            s.walec("Symbol tarcza", (0, 0, z), 0.8, 0.2, "dach_zbrojownia", os="z")
            s.walec("Symbol tarcza rant", (0, 0, z - 0.05), 0.95, 0.2, "zloto", os="z")


def _tablica_wyboru(s):
    kolory = ("dach_karczma", "dach_wylegarnia", "dach_sklep", "dach_lochy", "zloto", "dach_twierdza")
    with s.uklad(pos=(-1.0, 7.6, ZB), obrot=(0, 0, -2)), s.cechy(kolizja=False):
        s.blok("Tablica wyboru rama", (0, 0, 0.2), (13.4, 8.4, 0.4), "tusz")
        s.blok("Tablica wyboru", (0, 0, 0.5), (12.6, 7.6, 0.4), "drewno_jasne", "WoodPlanks")
        s.klin("Tablica wyboru daszek", (0, 4.7, 0.9), (14.0, 1.3, 1.6), DACH)
        s.blok("Tablica wyboru daszek rant", (0, 4.1, 0.9), (14.2, 0.3, 1.8), "tusz")
        for i in range(6):
            x, y = (-4.0 + 4.0 * (i % 3), 1.8 - 3.6 * (i // 3))
            with s.uklad(pos=(x, y, 0.75), obrot=(0, 0, (4, -6, 3, -3, 6, -5)[i])):
                _medalion(s, i, kolory[i])


def _sprzet(s):
    with s.cechy(kolizja=False, cien=False):
        s.blok("Mata", (-1.5, Y_PODLOGI + 0.06, 1.5), (9.0, 0.12, 7.0), cien(s, DACH, 0.9), "Fabric")
        s.blok("Mata pas", (-1.5, Y_PODLOGI + 0.1, 1.5), (9.4, 0.1, 0.6), "biel", "Fabric")
    # słomiany manekin z tarczą (lewy przód, poza osią wejście → tablica)
    with s.uklad(pos=(-6.8, Y_PODLOGI, 4.6), obrot=(0, 35, 0)):
        s.blok("Manekin podstawa", (0, 0.3, 0), (2.4, 0.6, 2.4), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Manekin słup", (0, 2.5, 0), (0.5, 4.0, 0.5), "drewno", "Wood")
            s.blok("Manekin słoma", (0, 5.2, 0), (2.4, 3.0, 1.6), "dach_stajnia", rot=(0, 0, 6))
            s.blok("Manekin rzemień", (0, 5.2, 0), (2.5, 0.5, 1.7), "drewno_ciemne", rot=(0, 0, 32))
            s.blok("Manekin głowa", (0.2, 7.4, 0), (1.6, 1.6, 1.4), "biel", rot=(0, 0, -8))
            s.walec("Manekin cel", (0, 5.3, 0.85), 0.8, 0.2, DACH, os="z")
            s.blok("Manekin ramię", (0, 6.1, 0), (4.2, 0.5, 0.5), "drewno", "Wood", rot=(0, 0, -10))
    # stojak z hantlami (lewa ściana) i worek treningowy (wisi ze stropu, spód nad głową gracza)
    with s.uklad(pos=(-8.4, Y_PODLOGI, -3.8), obrot=(0, 90, 0)):
        s.blok("Stojak", (0, 1.2, 0), (5.0, 2.4, 1.4), "drewno", "WoodPlanks")
        with s.cechy(kolizja=False):
            for x in (-1.4, 1.4):
                s.walec("Hantelka", (x, 2.75, 0), 0.25, 2.0, "metal_ciemny", os="z")
                for dz in (-0.75, 0.75):
                    s.walec("Hantelka krążek", (x, 2.75, dz), 0.6, 0.4, DACH, os="z")
    with s.cechy(kolizja=False):
        s.blok("Worek lina", (6.8, 12.1, 5.0), (0.25, 2.4, 0.25), "tusz")
        s.walec("Worek", (6.8, 8.6, 5.0), 1.15, 4.6, "drewno_jasne", os="y")
        s.walec("Worek pas", (6.8, 9.6, 5.0), 1.22, 0.4, DACH, os="y")
