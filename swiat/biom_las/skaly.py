# -*- coding: utf-8 -*-
"""Rodziny skał biomu Las z klocków (PROJEKT.md rozdz. 8): głaz-pięść, kanciak, menhir, skała urwiska.

pos = środek podstawy na ziemi, ry = obrót wokół pionu. Kanciaste bryły przechylone w kontrze 6–15°, mech tylko jako
czapa z ciemnym pasem pod spodem (para kamień/mech ma za mały kontrast), na ciemnym kamieniu jasny rant.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las.paleta import cien  # noqa: E402


def _z(rnd):
    return rnd.choice((-1, 1))


def glaz(s, rnd, pos, k=1.0, ry=0.0, kolor="kamien_cieply", mat="SmoothPlastic", mech=True, kolizja=True):
    """Głaz-pięść: ciemniejsza podstawa, jaśniejszy skośny wierzch (klin narożny), czapa mchu z pasem cienia.
    Wys. ok. 4,5·k. 3–5 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-10, 10), ry, _z(rnd) * rnd.uniform(6, 14))), s.cechy(kolizja=kolizja):
        s.blok("Głaz", (0, 1.4 * k - 0.6, 0), (5.0 * k, 2.8 * k + 1.2, 4.2 * k), cien(s, kolor, 0.82), mat)
        s.naroznik("Głaz wierzch", (0.2 * k, 3.6 * k - 0.4, 0), (4.4 * k, 2.0 * k, 3.8 * k), kolor, mat,
                   rot=(0, rnd.choice((0, 90, 180, 270)), 0))
        if mech:
            with s.cechy(kolizja=False, cien=False):
                s.blok("Mech cień", (-0.4 * k, 2.85 * k, 0.2 * k), (3.2 * k, 0.3, 2.8 * k), cien(s, "mech", 0.6), rot=(0, 20, 0))
                s.blok("Mech", (-0.4 * k, 3.1 * k, 0.2 * k), (3.0 * k, 0.45, 2.6 * k), "mech", rot=(0, 20, 0))
    return 4.5 * k, 2.6 * k


def kanciak(s, rnd, pos, k=1.0, ry=0.0, kolor="kamien_cieply", mat="SmoothPlastic", kolizja=True):
    """Kanciak (mały kamień): przechylony blok i klin obok. 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-12, 12), ry, _z(rnd) * rnd.uniform(10, 18))), s.cechy(kolizja=kolizja, cien=False):
        s.blok("Kamień", (0, 0.45 * k, 0), (2.4 * k, 1.5 * k, 2.0 * k), cien(s, kolor, 0.85), mat)
        s.klin("Kamień", (1.5 * k, 0.4 * k, 0.6 * k), (1.4 * k, 1.2 * k, 1.6 * k), kolor, mat, rot=(0, rnd.uniform(0, 360), 0))
    return 1.5 * k, 1.6 * k


def menhir(s, rnd, pos, h=12.0, ry=0.0, kolor="kamien_cieply", mat="Slate", przechyl=8.0):
    """Menhir: wysoki, pochylony blok, jaśniejszy rant od słońca, ścięty czubek. 3 części."""
    x, y, z = pos
    zn = _z(rnd)
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-4, 4), ry, zn * przechyl)):
        s.blok("Menhir", (0, h / 2.0 - 0.8, 0), (3.6, h + 1.6, 2.8), cien(s, kolor, 0.85), mat)
        with s.cechy(kolizja=False):
            s.blok("Menhir rant", (1.85, h / 2.0, 0), (0.35, h - 1.0, 2.9), kolor, mat)
            s.naroznik("Menhir czubek", (0, h + 0.9, 0), (3.6, 1.8, 2.8), kolor, mat, rot=(0, 90 if zn > 0 else 270, 0))
    return h, 2.0


def _jasniej(s, kolor, f):
    h = s.paleta.get(kolor, kolor)
    return "%02X%02X%02X" % tuple(max(0, min(255, int(int(h[i:i + 2], 16) * f))) for i in (0, 2, 4))


def skala_urwiska(s, rnd, p, kier_ry, y_dol, y_gora, kolor="kamien_cieply", mat="SmoothPlastic", dl=None, wystaje=1.0,
                  warstwy=True, kolor_zwisu="mech", darn=None):
    """Skała na krawędzi poziomu: blok wzdłuż krawędzi (dl 11–16) od y_dol do y_gora + 0,5–3, wystaje `wystaje` poza
    krawędź, przechylony w kontrze; co druga z jaśniejszym klinem na wierzchu. p = punkt krawędzi (x, z);
    kier_ry = obrót, przy którym lokalne +Z patrzy NA ZEWNĄTRZ poziomu. 1–2 części.

    Wersja 2 (warstwy=True, ściana ≥ 5): dwie WARSTWY skalne na licu (pasy ciemniejszy i jaśniejszy, wystają 0,35, na
    wysokości ok. 1/3 i 2/3 — sąsiednie skały mają je prawie na tej samej wysokości, więc ściana czyta się jak uwarstwiona,
    a przechył bloków łamie linię), w co trzeciej skale pionowa SZCZELINA tuszu, w co drugiej–trzeciej ZWIS mchu albo
    suchej trawy przewieszony przez rant. +2–4 części.

    Etap 3 (darn = kolor wierzchu poziomu): na wierzchu skały cienka DARŃ w kolorze i fakturze wierzchu poziomu, cofnięta
    o 0,9 od lica — z bliska rant nie jest już rzędem dużych gładkich jasnych płyt (zrzut ze Studio, półka nad rynną),
    tylko trawiastą wargą z kamiennym brzegiem. Bez losowania (reszta mapy zostaje bez zmian). +1 część."""
    dl = dl or rnd.uniform(11, 16)
    gl = rnd.uniform(6.5, 8.5)
    nad = rnd.uniform(0.2, 1.1)                                # niski rant (≤ 1,5 nad poziomem): nie psuje placów walki
    h = (y_gora + nad) - y_dol
    with s.uklad(pos=(p[0], y_dol, p[1]), obrot=(0, kier_ry, 0)):
        with s.uklad(pos=(0, 0, wystaje - gl / 2.0), obrot=(-rnd.uniform(2, 5), rnd.uniform(-6, 6), _z(rnd) * rnd.uniform(3, 6))):
            kol = kolor if rnd.random() < 0.5 else cien(s, kolor, 0.88)
            s.blok("Skała", (0, h / 2.0 - 0.5, 0), (dl, h + 1.0, gl), kol, mat)
            if darn:
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Rant darń", (0, h + 0.12, -0.45), (dl * 0.97, 0.3, gl - 0.9), darn)
            if rnd.random() < 0.5:
                with s.cechy(kolizja=False, cien=False):
                    s.naroznik("Skała wierzch", (0, h + 0.1, 0.3), (dl * 0.7, 0.8, gl * 0.7), cien(s, kolor, 1.06) if kolor != "biel" else kolor,
                               mat, rot=(0, rnd.choice((0, 90, 180, 270)), 0))
            if warstwy and h >= 5.0:
                with s.cechy(kolizja=False):
                    for yb, f in ((h * rnd.uniform(0.25, 0.33), 0.78), (h * rnd.uniform(0.58, 0.68), 1.1)):
                        tb = rnd.uniform(1.3, 2.2)
                        s.blok("Warstwa", (rnd.uniform(-0.6, 0.6), yb, gl / 2.0 - 0.15), (dl * rnd.uniform(0.85, 1.02), tb, 0.8),
                               _jasniej(s, kolor, f), mat, rot=(0, 0, rnd.uniform(-2.5, 2.5)))
                    with s.cechy(cien=False):
                        if rnd.random() < 0.35:
                            s.blok("Szczelina", (rnd.uniform(-dl / 3.0, dl / 3.0), h * 0.42, gl / 2.0 + 0.04),
                                   (0.35, h * rnd.uniform(0.35, 0.55), 0.2), "tusz", rot=(0, 0, rnd.uniform(-8, 8)))
                        if rnd.random() < 0.45:
                            for i in range(2):
                                s.blok("Mech zwis", (rnd.uniform(-dl / 3.0, dl / 3.0), h - 0.35, gl / 2.0 + 0.1),
                                       (dl * rnd.uniform(0.1, 0.2), rnd.uniform(0.8, 1.6), 0.35), kolor_zwisu, rot=(0, 0, rnd.uniform(-8, 8)))
                        # kępka na rancie: razem z rantem ≤ 1,2 nad poziomem (place walki na poziomach zostają czyste)
                        th = min(1.0, 1.2 - nad)
                        if rnd.random() < 0.5 and th >= 0.5:
                            for i in range(2):
                                s.klin("Trawa rantu", (rnd.uniform(-dl / 5.0, dl / 5.0), h + th / 2.0 - 0.05, gl / 2.0 - rnd.uniform(0.6, 1.6)),
                                       (0.3, th, rnd.uniform(0.8, 1.3)), kolor_zwisu, rot=(rnd.uniform(-10, 10), rnd.uniform(0, 360), rnd.uniform(-12, 12)))


def kamyki(s, rnd, pos, kolor="kamien_cieply", mat="SmoothPlastic", n=None, k=1.0):
    """Kamyki (detal przy ścieżce, piarg pod ścianą): 2–3 małe przechylone bryłki ≤ 0,8·k wysokie, bez kolizji i cienia.
    2–3 części."""
    x, y, z = pos
    n = n or rnd.choice((2, 2, 3))
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        for i in range(n):
            a = 2.4 * i + rnd.uniform(-0.5, 0.5)
            r = 0.0 if i == 0 else rnd.uniform(0.7, 1.3) * k
            sx, sy, sz = rnd.uniform(0.8, 1.5) * k, rnd.uniform(0.4, 0.8) * k, rnd.uniform(0.6, 1.2) * k
            s.blok("Kamyk", (r * math.cos(a), sy * 0.35, r * math.sin(a)), (sx, sy, sz), kolor if i % 2 == 0 else cien(s, kolor, 0.84),
                   mat, rot=(rnd.uniform(-10, 10), rnd.uniform(0, 90), rnd.uniform(-14, 14)))
