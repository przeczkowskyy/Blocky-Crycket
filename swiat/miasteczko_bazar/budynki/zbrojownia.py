# -*- coding: utf-8 -*-
"""Zbrojownia bazaru — jeden sklep z bronią i pancerzem (odpowiedź Karola na pytanie 28: „Targ to to samo co sklep
z bronią i armorem — łączymy”), wnętrze z ladą i zbrojmistrzem (D-084).

Przysadzista kamienna bryła z ciemnym dachem i złotą kalenicą (kod „oręż” z palety). Szyld z dzisiejszej zbrojowni:
miecz wbity w połać (import _miecz) i tarcza „przetestowana” strzałami (import _tarcza) na piętrze. W środku: stojak
z mieczami i tarczami na tylnej ścianie, manekin w napierśniku, kowadło przy wejściu (tylko ozdoba — kowal jest
w Twierdzy, D-051).
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.budynki import zbrojownia as stara_zbrojownia  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402
from swiat.miasteczko_bazar.wspolne import Y_PODLOGI  # noqa: E402

NAZWA = "Zbrojownia"
OBRYS = (20, 20)
WYSOKOSC = 36
BUDZET = 360
SCIANA, DACH = "kamien_cieply", "dach_zbrojownia"
SPRZEDAWCA = (0.5, -6.6)
ZB = -10.0 + 1.2


def buduj(s, rnd):
    info = wspolne.skorupa(s, rnd, 20, 20, SCIANA, DACH, H0=14.0, otwor=13.0, otwor_x=0.5, H_otw=12.6, hp=6.0,
                           nawis=(2.0, 0.5, 0.8, 1.2), rz_p=-5.0, ry_p=5.0, dach_h=8.5, rz_d=9.0, okap=2.8, podzial=0.58,
                           markiza=(DACH, "biel"), okna_pietra=("okragle",), komin=-1, duet="rycerz",
                           na_pietrze=_tarcza, na_dachu=_miecz)
    _wnetrze(s, rnd)
    zf = info["front"]
    zestaw.lata(s, (10.0, 4.0, -2.0), 2.6, 2.2, "pomarancz", ry=90)
    zestaw.wypadniety_klocek(s, (-8.6, 2.4, zf), (-9.2, 0, zf + 1.3), SCIANA)


def _tarcza(s, p):
    """Tarcza ze strzałami z dzisiejszej zbrojowni na prawej części piętra, pomniejszona do Ø 6."""
    with s.uklad(pos=(0.22 * p["W1"], p["hp"] * 0.5, p["D1"] / 2.0 + 0.1), obrot=(0, 0, -6), skala=0.75), \
            s.cechy(kolizja=False):
        stara_zbrojownia._tarcza(s)


def _miecz(s, d):
    """Miecz-szyld wbity w połać frontową po prawej (ok. 15° od pionu, ostrze ku uliczce)."""
    info = d["info"]
    zr, zfe = info["z_kalenicy"], d["D1"] / 2.0 + d["okap"]
    t = 0.4
    z = zr + (zfe - zr) * t
    y = d["dach_h"] * (1 - t)
    with s.uklad(pos=(0.18 * d["W1"], y - 2.6, z), obrot=(10, 15, -14)), s.cechy(kolizja=False):
        stara_zbrojownia._miecz(s)


def _wnetrze(s, rnd):
    bx, bz = SPRZEDAWCA
    wspolne.lada(s, (bx, Y_PODLOGI, bz + 2.85), 9.0, akcent=DACH, kolor="drewno", blat="drewno_ciemne")
    postacie.postac(s, "zbrojmistrz", NAZWA + "/Zbrojmistrz", (bx, Y_PODLOGI, bz), ry=0)
    wspolne.punkt_e(s, NAZWA, "zbrojownia", (bx, bz + 6.6), (bx, Y_PODLOGI + 4.6, bz + 0.6), typ="sklep",
                    sklep="zbrojownia", nazwa="Zbrojownia — broń i pancerz", okno="Okno sklepu (Paweł)",
                    postac="zbrojmistrz", model=NAZWA + "/Zbrojmistrz", kier=(0, 0, 1))
    wspolne.lampa(s, (0.0, 13.45, -2.5), lancuch=1.6)
    zb = ZB + 0.05
    with s.cechy(kolizja=False):
        # stojak na tylnej ścianie: belka, trzy miecze ostrzem w górę, dwie okrągłe tarcze
        s.blok("Stojak", (bx, 4.2, zb + 0.5), (12.0, 0.6, 1.0), "drewno_ciemne", "Wood")
        s.blok("Stojak", (bx, 9.6, zb + 0.5), (12.0, 0.6, 1.0), "drewno_ciemne", "Wood")
        for i, x in enumerate((-4.4, -2.6, 2.6, 4.4)):
            with s.uklad(pos=(bx + x, 4.5, zb + 0.9), obrot=(0, 0, (-4, 5, -6, 3)[i])):
                s.blok("Miecz ostrze", (0, 2.8, 0), (0.8, 4.6, 0.3), "tynk_blekit")
                s.blok("Miecz obrys", (0, 2.75, -0.1), (1.2, 4.9, 0.2), "tusz")
                s.blok("Miecz jelec", (0, 0.4, 0.05), (2.0, 0.45, 0.45), "zloto")
                s.blok("Miecz rękojeść", (0, -0.4, 0.05), (0.45, 1.3, 0.45), "drewno")
        for x, kol in ((-7.0, DACH), (7.4, "dach_karczma")):
            s.walec("Tarcza obrys", (bx + x, 7.6, zb + 0.25), 2.05, 0.3, "tusz", os="z")
            s.walec("Tarcza", (bx + x, 7.6, zb + 0.5), 1.8, 0.4, kol, os="z")
            s.walec("Tarcza rant", (bx + x, 7.6, zb + 0.55), 1.95, 0.25, "zloto", os="z")
            s.blok("Tarcza guz", (bx + x, 7.6, zb + 0.85), (0.9, 0.9, 0.4), "zloto", rot=(0, 0, 45))
    # manekin w napierśniku po lewej i kowadło po prawej (przy ścianach, poza drogą do lady)
    with s.uklad(pos=(-6.4, Y_PODLOGI, 1.5), obrot=(0, 35, 0)):
        s.blok("Manekin podstawa", (0, 0.3, 0), (2.2, 0.6, 2.2), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Manekin słup", (0, 2.8, 0), (0.5, 4.6, 0.5), "drewno", "Wood")
            s.blok("Napierśnik", (0, 5.6, 0), (2.8, 2.6, 1.6), "tynk_blekit")
            s.blok("Napierśnik pas", (0, 5.0, 0.0), (2.95, 0.5, 1.75), "zloto")
            s.blok("Napierśnik naramiennik", (-1.6, 6.7, 0), (1.2, 0.8, 1.7), cien(s, "tynk_blekit", 0.85), rot=(0, 0, 15))
            s.blok("Napierśnik naramiennik", (1.6, 6.7, 0), (1.2, 0.8, 1.7), cien(s, "tynk_blekit", 0.85), rot=(0, 0, -15))
            s.blok("Hełm", (0, 7.8, 0), (1.8, 1.6, 1.8), "metal_ciemny")
            s.blok("Hełm grzebień", (0, 8.8, 0), (0.4, 0.6, 1.9), "dach_karczma")
    with s.uklad(pos=(6.6, Y_PODLOGI, 3.0), obrot=(0, -20, 0)):
        s.walec("Pień", (0, 1.0, 0), 1.2, 2.0, "drewno", "Wood", os="y")
        with s.cechy(kolizja=False):
            s.blok("Kowadło", (0, 2.6, 0), (2.8, 1.2, 1.3), "metal_ciemny")
            s.klin("Kowadło róg", (1.9, 2.75, 0), (1.3, 0.9, 1.0), "metal_ciemny", rot=(0, -90, 0))
            s.blok("Kowadło rant", (0, 3.25, 0), (2.9, 0.12, 1.4), "tusz")
            with s.cechy(cien=False):
                s.blok("Sztaba", (-0.5, 3.4, 0.1), (1.6, 0.3, 0.4), "neon_ogien", "Neon", rot=(0, 15, 0))
