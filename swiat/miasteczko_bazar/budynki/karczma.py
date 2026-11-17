# -*- coding: utf-8 -*-
"""Karczma bazaru — zadania u Karczmarza (kanon: Karczma (Questy)) i stół mistrza gier planszowych (D-053).

Wnętrze 23,6 × 19,6, strop 14,7. Za ladą po lewej gruby barman (E → okno karczmy z zadaniami), za nim półki z kakao
i plackami, w kącie kocioł z parą (symbol gospody z dzisiejszego miasteczka), na tylnej ścianie tablica zleceń z trzema
kartkami. Po prawej okrągły stół z planszą i kostką, przy nim siedzi mistrz gier (E → okno planszy). Gospoda z jedzeniem,
nie z trunkiem (przykazania miasteczka). Szyld: pieczony udziec z dzisiejszej karczmy (import _udziec, nie kopia).
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.budynki import karczma as stara_karczma  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402
from swiat.miasteczko_bazar.wspolne import Y_PODLOGI, H_LADY  # noqa: E402

NAZWA = "Karczma"
OBRYS = (26, 22)
WYSOKOSC = 37
BUDZET = 430
SCIANA, DACH = "tynk_krem", "dach_karczma"
BARMAN = (-4.5, -7.0)            # stopy barmana (x, z)
ZB = -11.0 + 1.2                 # lico tylnej ściany od środka
STOL = (6.0, -3.0)               # środek stołu mistrza gier


def buduj(s, rnd):
    info = wspolne.skorupa(s, rnd, 26, 22, SCIANA, DACH, otwor=15.0, otwor_x=-1.5, hp=8.0, nawis=(2.6, 0.6, 1.2, 0.8),
                           rz_p=5.0, ry_p=-3.0, dach_h=12.0, rz_d=-9.0, markiza=(DACH, "biel"), komin=1, duet="kot",
                           okna_boczne=(1, 1), okna_pietra=("prostokat",), na_pietrze=_szyld)
    zf = info["front"]
    zestaw.okno(s, (9.0, 7.0, zf), 3.0, 4.0, przechyl=6, okiennica="dach_karczma", strona_okiennicy=1)
    _bar(s, rnd)
    _tablica_zlecen(s)
    _stol_mistrza(s)
    wspolne.lampa(s, (-4.5, 14.45, -3.2))
    wspolne.lampa(s, (STOL[0], 14.45, STOL[1] + 0.5))
    # znaki miasteczka i rekwizyty przy wejściu (bez kolizji, poza uliczką)
    zestaw.lata(s, (-13.0, 4.5, 2.0), 2.6, 2.2, "dach_twierdza", ry=-90)
    zestaw.wypadniety_klocek(s, (-11.0, 2.4, zf), (-11.6, 0, zf + 1.4), SCIANA)
    zestaw.kwiaty(s, (9.0, 0, zf + 1.3), ry=3, kolory=("czerwien", "zloto"))
    with s.cechy(kolizja=False):
        zestaw.beczka(s, (9.6, Y_PODLOGI, 7.8), "jablka", przechyl=(0, 6), kolizja=False)
        zestaw.skrzynia(s, (9.6, Y_PODLOGI, 4.4), ry=14, dl=3.0, a=2.6, przechyl=8, kolizja=False)


def _szyld(s, p):
    """Pieczony udziec z dzisiejszej karczmy (import _udziec) przed prawą częścią piętra, obrócony ku placowi."""
    wspolne.szyld_na_pietrze(s, p, 0.2 * p["W1"], stara_karczma._udziec, skala=0.95, ry=22, rz=-10, wysun=2.2)


def _bar(s, rnd):
    bx, bz = BARMAN
    wspolne.lada(s, (bx - 0.5, Y_PODLOGI, bz + 2.85), 11.0, akcent=DACH)
    postacie.postac(s, "barman", NAZWA + "/Barman", (bx, Y_PODLOGI, bz), ry=0)
    wspolne.punkt_e(s, NAZWA, "karczma", (bx, bz + 6.6), (bx, Y_PODLOGI + 4.6, bz + 0.6), typ="sklep",
                    sklep="karczma", nazwa="Karczma — zadania (Karczmarz)", okno="Okno Karczmy (Paweł)",
                    postac="barman", model=NAZWA + "/Barman", kier=(0, 0, 1))
    zb = ZB + 0.05
    with s.cechy(kolizja=False):
        # półki z jedzeniem: kubki kakao, placki, bochenki (bez butelek i kufli)
        wspolne.polka(s, (bx, 6.4, zb), 9.0)
        wspolne.polka(s, (bx, 9.4, zb), 9.0)
        for i, x in enumerate((-3.3, -2.0, -0.7)):
            s.walec("Kubek", (bx + x, 7.25, zb + 0.7), 0.5, 1.3, ("zloto", "biel", "dach_karczma")[i], os="y")
        s.walec("Placek", (bx + 1.4, 6.85, zb + 0.75), 1.1, 0.5, "drewno_jasne", os="y")
        s.walec("Placek nadzienie", (bx + 1.4, 7.12, zb + 0.75), 0.85, 0.1, "dach_karczma", os="y")
        s.blok("Bochenek", (bx + 3.1, 7.05, zb + 0.75), (1.9, 0.9, 1.0), "drewno_jasne", rot=(0, 10, 0))
        s.blok("Ser", (bx - 2.8, 10.05, zb + 0.7), (1.6, 0.9, 1.0), "zloto", rot=(0, -12, 0))
        s.walec("Słoik", (bx - 0.6, 10.2, zb + 0.7), 0.5, 1.2, "dach_wylegarnia", os="y")
        s.walec("Słoik", (bx + 0.6, 10.1, zb + 0.7), 0.45, 1.0, "pomarancz", os="y")
        s.klin("Chochla", (bx + 2.6, 10.6, zb + 0.4), (0.4, 2.2, 0.6), "metal_ciemny")
        # kocioł z parą w kącie za ladą
        kx, kz = -9.6, -7.9
        s.walec("Kocioł", (kx, Y_PODLOGI + 2.0, kz), 1.75, 2.6, "metal_ciemny", os="y")
        s.walec("Kocioł rant", (kx, Y_PODLOGI + 3.35, kz), 1.95, 0.4, "tusz", os="y")
        s.walec("Kocioł zupa", (kx, Y_PODLOGI + 3.25, kz), 1.55, 0.3, "pomarancz", os="y")
        for x in (-1.0, 1.0):
            s.blok("Kocioł nóżka", (kx + x, Y_PODLOGI + 0.4, kz), (0.5, 0.8, 0.5), "tusz")
        with s.cechy(cien=False):
            s.walec("Żar", (kx, Y_PODLOGI + 0.2, kz), 1.2, 0.3, "neon_ogien", "Neon", os="y")
        zestaw.dym(s, (kx + 0.2, Y_PODLOGI + 4.1, kz), n=3, skala=0.45, ksztalt="kula", dryf=(0.5, 0.4))


def _tablica_zlecen(s):
    """Tablica zleceń na tylnej ścianie obok barmana: deska z ramą, daszek w kolorze karczmy, trzy kartki z kształtami."""
    zb = ZB
    # cała tablica Z KOLIZJĄ (wisi na ścianie nad głową gracza): kamera gracza (Poppercam) zatrzymuje się tylko na
    # częściach z kolizją — bez niej po obróceniu kamery przy mistrzu gier wchodziła między ścianę a deskę albo między
    # deskę a kartki zleceń i cały ekran zasłaniał tył deski lub kartki (próby w Studio 17.11.2026)
    with s.uklad(pos=(4.4, 7.6, zb), obrot=(0, 0, 3)), s.cechy(kolizja=True):
        s.blok("Tablica rama", (0, 0, 0.2), (8.0, 5.6, 0.4), "tusz")
        s.blok("Tablica deska", (0, 0, 0.5), (7.2, 4.8, 0.4), "drewno_jasne", "WoodPlanks")
        s.klin("Tablica daszek", (0, 3.3, 0.9), (8.8, 1.2, 1.6), DACH)
        s.blok("Tablica daszek rant", (0, 2.75, 0.9), (9.0, 0.3, 1.8), "tusz")
        with s.cechy(cien=False):
            for i, (x, kol, k) in enumerate(((-2.4, "biel", -6), (0.0, "zloto", 4), (2.4, "tynk_blekit", 22))):
                s.blok("Zlecenie", (x, -0.2, 0.78), (1.9, 2.5, 0.15), kol, rot=(0, 0, k))
                s.blok("Zlecenie pinezka", (x, 0.95, 0.9), (0.4, 0.4, 0.2), "czerwien")
                if i == 0:
                    s.walec("Zlecenie znak", (x, -0.3, 0.9), 0.5, 0.12, "tusz", os="z")
                elif i == 1:
                    s.blok("Zlecenie znak", (x, -0.3, 0.9), (1.1, 0.25, 0.12), "tusz", rot=(0, 0, 45))
                    s.blok("Zlecenie znak", (x, -0.3, 0.92), (1.1, 0.25, 0.12), "tusz", rot=(0, 0, -45))
                else:
                    s.klin("Zlecenie znak", (x + 0.2, -0.3, 0.9), (0.12, 0.9, 1.0), "tusz", rot=(0, 90, 22))


def _stol_mistrza(s):
    sx, sz = STOL
    s.walec("Stół noga", (sx, Y_PODLOGI + 1.3, sz), 0.55, 2.6, "drewno_ciemne", "Wood", os="y")
    s.walec("Stół blat", (sx, Y_PODLOGI + 2.75, sz), 2.6, 0.4, "drewno", "Wood", os="y")
    with s.cechy(kolizja=False):
        s.walec("Stół rant", (sx, Y_PODLOGI + 2.55, sz), 2.75, 0.2, "tusz", os="y")
        # plansza 3 × 3 i pionki, kostka sześcienna (D-053: nagrody pól zawsze dodatnie, bez stawek)
        with s.uklad(pos=(sx, Y_PODLOGI + 3.0, sz + 0.4), obrot=(0, 8, 0)):
            s.blok("Plansza", (0, 0, 0), (3.6, 0.15, 3.6), "tusz")
            with s.cechy(cien=False):
                for i in range(3):
                    for j in range(3):
                        s.blok("Plansza pole", (-1.1 + 1.1 * i, 0.1, -1.1 + 1.1 * j), (1.0, 0.1, 1.0),
                               ("biel", "dach_kolo", "zloto")[(i + j) % 3])
            s.walec("Pionek", (-1.1, 0.55, 0.0), 0.3, 0.8, "dach_twierdza", os="y")
            s.walec("Pionek", (1.1, 0.55, -1.1), 0.3, 0.8, "pomarancz", os="y")
        with s.uklad(pos=(sx + 1.6, Y_PODLOGI + 3.4, sz + 1.6), obrot=(0, 25, 0)):
            s.blok("Kostka", (0, 0, 0), (0.9, 0.9, 0.9), "biel")
            with s.cechy(cien=False):
                s.blok("Kostka oczko", (0, 0.46, 0), (0.25, 0.05, 0.25), "tusz")
                s.blok("Kostka oczko", (0, 0, 0.46), (0.22, 0.22, 0.05), "tusz")
    s.walec("Stołek", (sx, Y_PODLOGI + 0.72, sz - 3.2), 1.0, 1.45, "drewno", "Wood", os="y")
    postacie.postac(s, "mistrz_gier", NAZWA + "/MistrzGier", (sx, Y_PODLOGI, sz - 3.0), ry=0)
    wspolne.punkt_e(s, NAZWA, "mistrz_gier", (sx, sz + 5.0), (sx, Y_PODLOGI + 4.4, sz - 2.6), typ="sklep",
                    sklep="mistrz_gier", nazwa="Mistrz gier planszowych (D-053)", okno="Okno planszy (Paweł)",
                    postac="mistrz_gier", model=NAZWA + "/MistrzGier", kier=(0, 0, 1))
