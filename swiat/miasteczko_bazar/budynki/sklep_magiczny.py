# -*- coding: utf-8 -*-
"""Sklep magiczny bazaru — mag-sklepikarz za ladą z kryształową kulą (D-084), zaraz obok zbrojowni (D-085).

Lawendowa bryła z łamanym trzonem: parter z wnętrzem, przechylone piętro, węższa wieżyczka skręcona w drugą stronę i na
niej dach-kapelusz z dzisiejszego sklepu magicznego (import _kapelusz, pomniejszony ×0,7) — sylwetka czytelna z daleka.
W środku półki z księgami, kryształami i zwojami, gwiazdka nad ladą, fioletowe światło. Bez butelek i kotła
(przykazania sklepu z dzisiejszego miasteczka).
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.budynki import sklep_magiczny as stary_sklep  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402
from swiat.miasteczko_bazar.wspolne import Y_PODLOGI  # noqa: E402

NAZWA = "SklepMagiczny"
OBRYS = (18, 20)
WYSOKOSC = 42
BUDZET = 360
SCIANA, DACH, SWIATLO = "tynk_lawenda", "dach_sklep", "neon_magia"
SPRZEDAWCA = (-0.5, -6.6)
ZB = -10.0 + 1.2


def buduj(s, rnd):
    info = wspolne.skorupa(s, rnd, 18, 20, SCIANA, DACH, H0=14.0, otwor=12.0, otwor_x=-0.5, H_otw=12.6, hp=5.5,
                           nawis=(1.8, 0.4, 0.6, 1.0), rz_p=6.0, ry_p=-5.0, dach_h=0.0, rz_d=-10.0,
                           markiza=(DACH, "biel"), okna_pietra=("okragle", "prostokat"), swiatlo=SWIATLO, duet=None,
                           na_dachu=_wieza)
    _wnetrze(s, rnd)
    zf = info["front"]
    zestaw.lata(s, (-9.0, 4.2, 1.0), 2.4, 2.0, "pomarancz", ry=-90)
    zestaw.wypadniety_klocek(s, (7.4, 2.2, zf), (8.2, 0, zf + 1.2), SCIANA)
    zestaw.kwiaty(s, (-7.0, 0, zf + 1.3), ry=-4, kolory=("dach_sklep", "zloto"))


def _wieza(s, d):
    """Węższa wieżyczka 12 × 5 × 12 (skręt i przechył w kontrze do piętra) z okrągłym oknem i dach-kapelusz."""
    with s.uklad(pos=(0.4, 0, 0.5), obrot=(0, 9, 14)):
        s.blok("Wieżyczka", (0, 2.3, 0), (11.0, 5.6, 11.0), SCIANA)
        with s.cechy(kolizja=False):
            s.blok("Wieżyczka wieniec", (0, -0.2, 0), (11.6, 0.8, 11.6), "tusz")
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Narożnik", (sx * 5.3, 2.4, sz * 5.3), (1.1, 4.6, 1.1), "tusz")
        zestaw.okno(s, (1.2, 2.5, 5.5), 2.6, ksztalt="okragle", swiatlo=SWIATLO, przechyl=0)
        with s.uklad(pos=(0, 5.0, 0), skala=0.7):
            stary_sklep._kapelusz(s)


def _wnetrze(s, rnd):
    bx, bz = SPRZEDAWCA
    wspolne.lada(s, (bx, Y_PODLOGI, bz + 2.85), 8.0, kolor="tynk_lawenda", blat="dach_sklep", akcent="zloto")
    postacie.postac(s, "mag", NAZWA + "/Mag", (bx, Y_PODLOGI, bz), ry=0)
    wspolne.punkt_e(s, NAZWA, "sklep_magiczny", (bx, bz + 6.6), (bx, Y_PODLOGI + 4.6, bz + 0.6), typ="sklep",
                    sklep="sklep_magiczny", nazwa="Sklep magiczny", okno="Okno sklepu (Paweł)", postac="mag",
                    model=NAZWA + "/Mag", kier=(0, 0, 1))
    wspolne.lampa(s, (-4.5, 13.45, -1.5), swiatlo=SWIATLO, lancuch=1.6)
    wspolne.lampa(s, (4.0, 13.45, -3.0), swiatlo=SWIATLO, lancuch=2.4)
    with s.cechy(kolizja=False):
        # kryształowa kula na ladzie
        ly = Y_PODLOGI + 3.2
        s.walec("Kula podstawka", (bx + 2.6, ly + 0.2, bz + 2.6), 0.75, 0.4, "zloto", os="y")
        with s.cechy(cien=False):
            s.kula("Kryształowa kula", (bx + 2.6, ly + 1.1, bz + 2.6), 1.5, SWIATLO, "Neon")
        s.blok("Księga na ladzie", (bx - 2.6, ly + 0.3, bz + 2.8), (1.8, 0.5, 1.3), "dach_gildia", rot=(0, 18, 0))
        # gwiazdka nad ladą
        with s.uklad(pos=(bx + 1.0, 10.8, bz + 2.0)), s.cechy(cien=False):
            for k in (0, 45):
                s.blok("Gwiazdka", (0, 0, 0), (1.6, 1.6, 0.4), "zloto", rot=(0, 20, k))
        zb = ZB + 0.05
        for y in (6.3, 9.3):
            wspolne.polka(s, (bx, y, zb), 9.5, kolor="drewno_ciemne", wsporniki="zloto")
        kolory = ("dach_karczma", "dach_gildia", "dach_twierdza", "zloto", "dach_wylegarnia")
        x = bx - 4.2
        # księgi i kryształy dolnej półki Z KOLIZJĄ (wysoko, nad głową gracza): kamera gracza zatrzymuje się tylko na
        # częściach z kolizją — bez niej po obróceniu kamery przy ladzie wchodziła między ścianę a księgi (próba 17.11.2026)
        with s.cechy(kolizja=True):
            for i in range(6):                                 # księgi na dolnej półce
                h = 1.6 + 0.3 * (i % 3)
                s.blok("Księga", (x, 6.5 + h / 2.0, zb + 0.75), (0.7, h, 1.2), kolory[i % 5], rot=(0, 0, (0, 6, -4, 0, 10, 0)[i]))
                x += 0.8
            for i, xx in enumerate((1.3, 2.9)):                # kryształy
                s.ostroslup("Kryształ", (bx + xx, 6.5, zb + 0.75), 0.5, 0.5, 1.8 + 0.5 * i, DACH)
            with s.cechy(cien=False):
                s.ostroslup("Kryształ", (bx + 2.1, 6.5, zb + 0.75), 0.6, 0.6, 2.6, SWIATLO, "Neon")
        for i in range(3):                                     # zwoje na górnej półce
            s.walec("Zwój", (bx - 3.0 + i * 1.6, 9.95, zb + 0.75), 0.4, 1.4, "biel", os="z", rot=(0, (8 * i) - 8, 0))
            s.walec("Zwój pieczęć", (bx - 3.0 + i * 1.6, 9.95, zb + 1.5), 0.25, 0.15, "dach_karczma", os="z")
        s.blok("Klepsydra", (bx + 2.4, 10.4, zb + 0.75), (0.9, 1.6, 0.9), "zloto", rot=(0, 45, 0))
    # skrzynia z towarem i stos ksiąg przy lewej ścianie (poza drogą do lady)
    zestaw.skrzynia(s, (-6.6, Y_PODLOGI, 2.5), ry=80, dl=3.2, a=2.6, przechyl=7, kolor="dach_sklep")
    with s.cechy(kolizja=False):
        for i in range(3):
            s.blok("Stos ksiąg", (6.8, Y_PODLOGI + 0.35 + 0.6 * i, 1.8), (2.0, 0.6, 1.5), ("dach_twierdza", "zloto", "dach_karczma")[i],
                   rot=(0, 12 * i - 8, 0))
