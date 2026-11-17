#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator aren walki zależnych od biomu: plan.py → <arena>/czesci.json + <arena>/znaczniki.json + zrodla/DaneAren.luau.

    python -B swiat/areny_walki/generuj.py               # wszystkie areny
    python -B swiat/areny_walki/generuj.py --tylko bagno  # jedna

Jedna arena = jedna scena (format czesci.json jak mapy z klocków: Blender, Studio, podgląd 3D panelu). Części są
w ŚWIECIE (arena stoi daleko od map, w punkcie `O` z planu); generator buduje je w układzie SCENY walki i na końcu
obraca o 180° wokół pionu (scena = CFrame.lookAt(O, O + (0, 0, 1)), jak Ustawienia.scena() prototypu walki).

Każdy obiekt jest stawiany przez Budowa.postaw: pierwsze miejsce poza wolną przestrzenią kamer z profilu (kamery.py),
potem kontrola na punktach WSZYSTKICH jego części (geom.punkty) — część w wolnej przestrzeni = obiekt cofnięty i
postawiony dalej (warstwy z `dosun`) albo pominięty. Ta sama kontrola działa w sprawdz.py na gotowym pliku.
Na końcu wszystkie części tracą kolizję (aktorzy to lokalne klony, po arenie nikt nie chodzi), a dalekie — cień.
"""
import argparse
import json
import math
import os
import random
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import numpy as np  # noqa: E402

from swiat.biblioteka.scena import Scena, ku_srodkowi  # noqa: E402
from swiat.biom_las import detale as det_lasu  # noqa: E402
from swiat.biom_las import rosliny as ros_lasu  # noqa: E402
from swiat.biom_las import skaly  # noqa: E402
from swiat.bagno_pas import rosliny as ros_bagna  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
import geom  # noqa: E402
import kamery  # noqa: E402
import plan as P  # noqa: E402
import rekwizyty as R  # noqa: E402

GRUNT_Y = 0.12             # część z wierzchem ≤ tyle nad płytą placu = grunt (nie łamie wolnej przestrzeni)
ZAPAS = 1.0                # odstęp bryły od wolnej przestrzeni kamer
PLAC_ZAPAS = 0.3           # nad placem (r ≤ 22,3) nic poza gruntem
DALEKO = 110.0             # dalej części bez cienia


# --------------------------------------------------------------------------- rodziny: (budowa, wys(k), promień(k))
def _y(b):
    return b.A["grunt"]["y"]


RODZINY = {
    # las
    "paproc": (lambda b, s, r, p, k, ry, o: ros_lasu.paproc(s, r, p, k), lambda k: 2.2 * k, lambda k: 1.6 * k),
    "kepa_grzybow": (lambda b, s, r, p, k, ry, o: R.kepa_grzybow(s, r, p, k, ry), lambda k: 4.6 * k, lambda k: 2.8 * k),
    "kloda": (lambda b, s, r, p, k, ry, o: det_lasu.kloda(s, r, p, k), lambda k: 2.6 * k, lambda k: 5.2 * k),
    "pniak": (lambda b, s, r, p, k, ry, o: ros_lasu.pniak(s, r, p, k, ry), lambda k: 2.2 * k, lambda k: 1.8 * k),
    "kwiaty": (lambda b, s, r, p, k, ry, o: ros_lasu.kwiaty(s, r, p, r.choice((("zloto", "biel"), ("czerwien", "zloto"),
                                                                                   ("biel", "dach_sklep")))),
               lambda k: 1.3, lambda k: 1.4),
    "grzybki": (lambda b, s, r, p, k, ry, o: det_lasu.grzybki(s, r, p, ("czerwien", "biel")), lambda k: 1.5, lambda k: 1.3),
    "kanciak": (lambda b, s, r, p, k, ry, o: skaly.kanciak(s, r, p, k, ry, kolizja=False), lambda k: 1.6 * k, lambda k: 1.7 * k),
    "mech_plat": (lambda b, s, r, p, k, ry, o: R.mech_plat(s, r, p, k), lambda k: 0.1, lambda k: k),
    "grzyb": (lambda b, s, r, p, k, ry, o: ros_lasu.grzyb(s, r, p, k, ry, kapelusz=r.choice(("czerwien", "czerwien", "dach_karczma")),
                                                       kropki=True, trzon="biel"), lambda k: 10.5 * k, lambda k: 4.8 * k),
    "glaz": (lambda b, s, r, p, k, ry, o: skaly.glaz(s, r, p, k, ry, "kamien_cieply", mech=True), lambda k: 4.6 * k, lambda k: 2.8 * k),
    "krzak": (lambda b, s, r, p, k, ry, o: ros_lasu.krzak(s, r, p, k, jagoda=r.choice((None, None, "czerwien"))),
              lambda k: 3.8 * k, lambda k: 2.4 * k),
    "drzewo_lasu": (lambda b, s, r, p, k, ry, o: R.drzewo_lasu(s, r, o["wariant"], p, k, ry, o.get("f", 1.0)), None, None),
    "wysepka_lasu": (lambda b, s, r, p, k, ry, o: R.wysepka_lasu(s, r, p, k, ry), lambda k: 2.6 * k, lambda k: 4.2 * k),
    "kepa_z_trzcina": (lambda b, s, r, p, k, ry, o: R.kepa_z_trzcina(s, r, p, k, ry, _y(b)), lambda k: 2.6, lambda k: 3.6 * k),
    "stragan": (lambda b, s, r, p, k, ry, o: zestaw.stragan(s, p, ry, tuple(o.get("kolory", ("dach_karczma", "biel"))),
                                                         o.get("towar", "jablka"), tani=True), lambda k: 10.0, lambda k: 6.5),
    "brama_miejska": (lambda b, s, r, p, k, ry, o: R.brama_miejska(s, r, p, ry, o.get("wys", 10.0)), lambda k: 21.0, lambda k: 9.0),
    "olbrzym": (lambda b, s, r, p, k, ry, o: R.olbrzym(s, r, p, k, ry, o.get("korona_ku")), lambda k: 30.0 * k, lambda k: 7.0 * k),
    "promien_swiatla": (lambda b, s, r, p, k, ry, o: R.promien_swiatla(s, r, p, o.get("h", 30), o.get("szer", 4), ry, o.get("pochyl", 16)),
                        lambda k: 30.0, lambda k: 4.0),
    # bagno
    "grzybien": (lambda b, s, r, p, k, ry, o: ros_bagna.grzybien(s, r, p, k, kwiat=r.choice((None, None, "bagno_kwiat", "biel"))),
                 lambda k: 0.0, lambda k: k),
    "kepa": (lambda b, s, r, p, k, ry, o: R.kepa(s, r, p, k, r.uniform(0.9, 1.5), _y(b)), lambda k: 0.0, lambda k: k),
    "kepa_trzciny": (lambda b, s, r, p, k, ry, o: R.trzcina_zdzbla(s, r, p, r.uniform(4.6, 6.4), 3.6, True),
                     lambda k: 7.6 + -1.8, lambda k: 2.2),
    "kepa_trzciny_niska": (lambda b, s, r, p, k, ry, o: R.trzcina_zdzbla(s, r, p, r.uniform(2.6, 3.6), 2.6, False),
                           lambda k: 4.8 - 1.8, lambda k: 1.6),
    "korzeniak": (lambda b, s, r, p, k, ry, o: ros_bagna.korzeniak(s, r, p, k, ry), lambda k: 13.0 * k - 1.8, lambda k: 4.4 * k),
    "drzewo_bagna": (lambda b, s, r, p, k, ry, o: _drzewo_bagna(s, r, o["wariant"], p, k, ry), None, None),
    "zatopiony_pien": (lambda b, s, r, p, k, ry, o: R.zatopiony_pien(s, r, p, k, ry, _y(b)), lambda k: 3.6 * k, lambda k: 4.8 * k),
    "latarnia_pal": (lambda b, s, r, p, k, ry, o: R.latarnia_pal(s, r, p, o.get("h", 6.0), ry, _y(b)), lambda k: 6.0, lambda k: 2.8),
    "chata_na_palach": (lambda b, s, r, p, k, ry, o: R.chata_na_palach(s, r, p, k, ry, o.get("h0", 5.0), _y(b)),
                        lambda k: 16.0 * k, lambda k: 6.4 * k),
    "wieza_obserwacyjna": (lambda b, s, r, p, k, ry, o: R.wieza_obserwacyjna(s, r, p, k, ry, _y(b)), lambda k: 30.0 * k, lambda k: 4.5 * k),
    "lodka": (lambda b, s, r, p, k, ry, o: R.lodka(s, r, p, ry, _y(b)), lambda k: 0.0, lambda k: 3.0),
    # próba
    "bela_siana": (lambda b, s, r, p, k, ry, o: R.bela_siana(s, r, p, k, ry), lambda k: 2.2 * k, lambda k: 1.7 * k),
    "bela_siana_dwie": (lambda b, s, r, p, k, ry, o: R.bela_siana(s, r, p, k, ry, dwie=True), lambda k: 4.2 * k, lambda k: 1.8 * k),
    "manekin": (lambda b, s, r, p, k, ry, o: R.manekin(s, r, p, k, ry), lambda k: 6.3 * k, lambda k: 2.6 * k),
    "stojak_broni": (lambda b, s, r, p, k, ry, o: R.stojak_broni(s, r, p, k, ry), lambda k: 3.6 * k, lambda k: 2.8 * k),
    "tarcza_lucznicza": (lambda b, s, r, p, k, ry, o: R.tarcza_lucznicza(s, r, p, k, ry), lambda k: 5.4 * k, lambda k: 2.2 * k),
    "drzewo_miasta": (lambda b, s, r, p, k, ry, o: R.drzewo_miasta(s, r, p, k, ry), lambda k: 15.0 * k, lambda k: 5.6 * k),
    "domek_tla": (lambda b, s, r, p, k, ry, o: R.domek_tla(s, r, p, ry, o["szer"], o["gl"], o["wys"], o["dach"], o["sciana"],
                                                          o.get("okna", 2)),
                  None, None),
    "trybuna": (lambda b, s, r, p, k, ry, o: R.trybuna(s, r, p, ry, o.get("dl", 14.0)), lambda k: 9.0, lambda k: 8.0),
    "namiot": (lambda b, s, r, p, k, ry, o: R.namiot(s, r, p, ry, tuple(o.get("kolory", ("dach_karczma", "biel")))),
               lambda k: 12.0, lambda k: 5.0),
    "choragiew": (lambda b, s, r, p, k, ry, o: _choragiew(s, p, o, ry), lambda k: 15.0, lambda k: 4.0),
}

TWARZA = ("chata_na_palach", "trybuna", "namiot", "domek_tla", "manekin", "stojak_broni", "tarcza_lucznicza", "brama_miejska", "stragan")
DACHY = ["dach_karczma", "dach_dom_ceglasty", "dach_twierdza", "dach_sklep", "dach_wylegarnia", "dach_stajnia", "dach_dom_lupek"]
SCIANY = ["tynk_krem", "tynk_brzoskwinia", "tynk_mieta", "tynk_lawenda", "tynk_blekit"]
WYS_DRZEW = {"dab": (21.0, 7.0), "okraglak": (15.0, 5.3), "sosna": (19.0, 5.0), "smukly": (23.0, 3.6), "swierk": (21.0, 4.8),
             "jarzebina": (12.0, 3.6), "brzozka": (16.0, 3.8), "grzyb": (10.5, 4.8),
             "cyprys": (24.0, 7.0), "wierzba": (15.0, 5.8), "korzeniak": (13.0, 4.4), "suchy_omszaly": (17.0, 3.2)}


def _drzewo_bagna(s, rnd, wariant, pos, k, ry):
    f = rnd.uniform(0.9, 1.06)
    if wariant == "cyprys":
        return ros_bagna.cyprys(s, rnd, pos, k, ry, f)
    if wariant == "wierzba":
        return ros_bagna.wierzba(s, rnd, pos, k, ry, f)
    if wariant == "korzeniak":
        return ros_bagna.korzeniak(s, rnd, pos, k, ry, f)
    if wariant == "suchy_omszaly":
        return ros_bagna.suchy_omszaly(s, rnd, pos, k, ry)
    raise ValueError(wariant)


def _choragiew(s, pos, o, ry):
    zestaw.choragiew(s, pos, o.get("kolor", "dach_twierdza"), None, o.get("wys", 14.0), ry, 6.0, 3.4)
    return o.get("wys", 14.0) + 1.0, 4.0


# --------------------------------------------------------------------------- budowa jednej areny
class Budowa:
    def __init__(self, klucz, A, prof):
        self.klucz, self.A, self.prof = klucz, A, prof
        self.s = Scena("Workspace/ArenyWalki/" + A["model"], paleta=R.PALETA)
        self.rnd = random.Random(A["ziarno"])
        self.zajete = []                                    # (x, z, promień, grupa) — postawione obiekty
        self.stat = {"postawione": {}, "pominiete": {}, "dosuniete": 0}
        self.kotwice = {}                                   # grupa → lista (x, y, z, wys) dla detali nastroju
        self.ostatnie = []

    # ---- wolna przestrzeń
    def rmin(self, kat, wys, polszer):
        """Najmniejszy promień, przy którym obiekt (krąg `polszer`, wysokość `wys`) stoi poza wolną przestrzenią."""
        pr = self.prof
        iy1 = int(min(pr.ny - 1, max(0, math.ceil(max(wys, 0.0) / pr.ky))))
        r = P.R_PLAC + PLAC_ZAPAS + polszer + 0.4
        for _ in range(8):
            d = math.degrees(math.atan2(polszer, max(r, 1.0))) + pr.kk
            a0, a1 = kat - d, kat + d
            ik = [int(((a0 + i * pr.kk) % 360.0) / pr.kk) % pr.nk for i in range(int((a1 - a0) / pr.kk) + 2)]
            m = float(pr.r[ik, :iy1 + 1].max()) if iy1 >= 0 else 0.0
            nowy = max(r, m + polszer + ZAPAS)
            if abs(nowy - r) < 0.05:
                break
            r = nowy
        return r

    def narusza(self, n0, n1=None):
        """Czy któraś część z s.czesci[n0:n1] (układ sceny) leży w wolnej przestrzeni kamer albo nad placem."""
        return len(naruszenia(self.s.czesci[n0:n1], self.prof)) > 0

    def wolne_miejsce(self, x, z, p, grupa, odstep):
        for (qx, qz, qp, qg) in self.zajete:
            d = math.hypot(x - qx, z - qz)
            if qg == grupa and d < odstep:
                return False
            if p > 1.2 and qp > 1.2 and d < 0.7 * (p + qp):
                return False
        return True

    def postaw(self, grupa, rodzina, kat, r, k=1.0, ry=None, opcje=None, dosun=True, pchniec=6, krok=3.0, twarza=False,
               odstep=0.0, zajmij=True, r_maks=None):
        """Stawia obiekt rodziny na kącie `kat` w odległości ≥ r (dosunięty poza wolną przestrzeń). True = postawiony."""
        o = dict(opcje or {})
        bud, fh, fp = RODZINY[rodzina]
        if rodzina in ("drzewo_lasu", "drzewo_bagna"):
            h, p = WYS_DRZEW[o["wariant"]]
            h, p = h * k, p * k
        elif rodzina == "domek_tla":
            h, p = o["wys"] * 1.62 + 3.0, max(o["szer"], o["gl"]) / 2.0 + 1.5
        else:
            h, p = fh(k), fp(k)
        h += _y(self) if rodzina in ("korzeniak", "drzewo_bagna") else 0.0
        if dosun:
            r = max(r, self.rmin(kat, h, p))
        for proba in range(pchniec + 1):
            if r_maks is not None and r > r_maks:
                break
            a = math.radians(kat)
            x, z = r * math.cos(a), r * math.sin(a)
            if zajmij and not self.wolne_miejsce(x, z, p, grupa, odstep):
                if not dosun:
                    break
                r += krok
                continue
            obrot = ry
            if twarza:
                obrot = ku_srodkowi(x, z) + (ry or 0.0)
            elif obrot is None:
                obrot = self.rnd.uniform(0, 360)
            n0 = len(self.s.czesci)
            with self.s.grupa(grupa):
                bud(self, self.s, self.rnd, (x, _y(self), z), k, obrot, o)
            if not self.narusza(n0):
                if zajmij:
                    self.zajete.append((x, z, p, grupa))
                self.stat["postawione"][rodzina] = self.stat["postawione"].get(rodzina, 0) + 1
                self.stat["dosuniete"] += 1 if proba else 0
                self.ostatnie = (x, z, h, obrot)
                return True
            del self.s.czesci[n0:]
            if not dosun:
                break
            r += krok
        self.stat["pominiete"][rodzina] = self.stat["pominiete"].get(rodzina, 0) + 1
        return False

    # ---- warstwy
    def grunt(self):
        g = self.A["grunt"]
        y = g["y"]
        s = self.s
        with s.grupa("Grunt"), s.cechy(cien=False):
            s.walec("Grunt", (0, y - 0.6, 0), P.R_GRUNT, 1.2, g["kolor"], g["mat"], os="y")
            for i, l in enumerate(g.get("laty", [])):
                s.walec("Grunt łata", (0, y + 0.02 + 0.025 * i, 0), l["r"], 0.05, l["kolor"], l["mat"], os="y")
            pl = g.get("plamy")
            if pl:
                for _ in range(pl["n"]):
                    a = self.rnd.uniform(0, 2 * math.pi)
                    rr = self.rnd.uniform(*pl["r"])
                    s.walec("Grunt plama", (rr * math.cos(a), y + 0.06, rr * math.sin(a)), self.rnd.uniform(*pl["rozmiar"]), 0.04,
                            self.rnd.choice(pl["kolory"]), g["mat"], os="y")

    def plac(self):
        A, s = self.A, self.s
        styl = A["plac"]["styl"]
        k0, k1, k2 = A["plac"]["kolory"]
        mat = A["plac"].get("material", "Ground")
        y = A["grunt"]["y"]
        Rp = P.R_PLAC
        with s.grupa("Plac"), s.cechy(cien=False):
            if styl in ("ziemia", "piasek"):
                dol = y - 0.4
                s.walec("Plac", (0, dol / 2.0, 0), Rp, -dol, k0, mat if styl == "ziemia" else "Sand", os="y")
                s.walec("Plac obrys", (0, (dol + y + 0.32) / 2.0, 0), Rp + 0.55, (y + 0.32) - dol, k2, os="y")
                if styl == "ziemia":
                    s.walec("Plac obrzeże", (0, 0.02, 0), Rp - 2.0, 0.04, k1, mat, os="y")
                    s.walec("Plac środek", (0, 0.045, 0), Rp - 3.4, 0.04, k0, mat, os="y")
                    s.walec("Plac środek jasny", (0, 0.07, 0), 6.0, 0.04, k1, mat, os="y")
                    s.walec("Plac środek", (0, 0.095, 0), 4.8, 0.04, k0, mat, os="y")
                else:
                    s.walec("Plac kreda", (0, 0.02, 0), Rp - 2.2, 0.04, k1, "SmoothPlastic", os="y")
                    s.walec("Plac piasek", (0, 0.045, 0), Rp - 2.8, 0.04, k0, "Sand", os="y")
                    s.walec("Plac kreda środek", (0, 0.07, 0), 2.6, 0.04, k1, "SmoothPlastic", os="y")
                    s.walec("Plac piasek środek", (0, 0.095, 0), 2.0, 0.04, k0, "Sand", os="y")
            elif styl == "pomost":
                s.walec("Pomost", (0, -0.25, 0), Rp, 0.5, k0, "WoodPlanks", os="y")
                s.walec("Pomost spód", (0, -1.45, 0), Rp - 0.4, 1.9, k1, "Wood", os="y")
                for i in range(-7, 8):                         # deski (ciemne szczeliny) wzdłuż Z, przycięte do koła
                    d = i * 2.8
                    dl = 2.0 * math.sqrt(max(0.0, (Rp - 1.2) ** 2 - d * d))
                    if dl > 1.0:
                        s.blok("Pomost szczelina", (d, 0.015, 0), (0.22, 0.04, dl), k1)
                n = 14
                for i in range(n):                             # obręcz z belek (wieloboki) — wyższa o 0,08
                    a = 2 * math.pi * (i + 0.5) / n
                    dl = 2 * (Rp - 0.45) * math.sin(math.pi / n) + 0.25
                    s.blok("Pomost belka", ((Rp - 0.45) * math.cos(a), 0.04, (Rp - 0.45) * math.sin(a)), (dl, 0.08, 0.9), k1,
                           "Wood", rot=(0, -math.degrees(a) + 90, 0))
                s.walec("Pomost środek", (0, 0.02, 0), 5.0, 0.04, R.cien(s, k0, 0.9), "WoodPlanks", os="y")
        self.stat["plac"] = styl

    def obrecz(self):
        A, s, rnd = self.A, self.s, self.rnd
        o = A["obrecz"]
        n, r0 = o["n"], o["r"]
        przerwy = o.get("przerwy", [])

        def wolny(kat):
            return not any(_w_luku(kat, a, b) for a, b in przerwy)
        katy = [360.0 * (i + 0.5) / n + rnd.uniform(-2, 2) for i in range(n)]
        if o["rodzina"] == "kamien_obreczy":
            for kat in katy:
                if wolny(kat):
                    a = math.radians(kat)
                    rr = r0 + rnd.uniform(-0.2, 0.6)
                    n0 = len(s.czesci)
                    with s.grupa("Obrecz"):
                        R.kamien_obreczy(s, rnd, (rr * math.cos(a), A["grunt"]["y"] + 0.1, rr * math.sin(a)), rnd.uniform(*o["k"]),
                                         -kat + 90 + rnd.uniform(-15, 15))
                    if self.narusza(n0):
                        del s.czesci[n0:]
                        self.stat["pominiete"]["kamien_obreczy"] = self.stat["pominiete"].get("kamien_obreczy", 0) + 1
        elif o["rodzina"] in ("pal_obreczy", "barierka"):
            pkt = [(kat, r0 * math.cos(math.radians(kat)), r0 * math.sin(math.radians(kat))) for kat in katy]
            for i, (kat, x, z) in enumerate(pkt):
                kat2, x2, z2 = pkt[(i + 1) % len(pkt)]
                if not wolny(kat):
                    continue
                n0 = len(s.czesci)
                with s.grupa("Obrecz"):
                    if o["rodzina"] == "pal_obreczy":
                        R.pal(s, rnd, (x, 0.0, z), h=rnd.uniform(0.75, 1.0), r=0.42, y0=A["grunt"]["y"] - 0.6)
                        if wolny(kat2) and wolny((kat + kat2) / 2.0):
                            with s.cechy(cien=False):
                                s.belka("Lina", (x, 0.62, z), (x2, 0.62, z2), 0.14, "bagno_trzcina", "SmoothPlastic")
                    else:
                        if wolny(kat2) and wolny((kat + kat2) / 2.0):
                            R.barierka(s, rnd, (x, z), (x2, z2), wys=0.95)
                if self.narusza(n0):
                    del s.czesci[n0:]
                    self.stat["pominiete"][o["rodzina"]] = self.stat["pominiete"].get(o["rodzina"], 0) + 1

    def warstwa(self, w):
        rnd = self.rnd
        luki = w["luki"]
        dl_lukow = [((b - a) % 360.0) or 360.0 for a, b in luki]
        razem = sum(dl_lukow)
        dosun = w.get("dosun", False)
        postawione = 0
        for i in range(w["n"]):
            for _ in range(14):
                t = rnd.uniform(0, razem)
                for (a, b), d in zip(luki, dl_lukow):
                    if t <= d:
                        kat = (a + t) % 360.0
                        break
                    t -= d
                r = rnd.uniform(*w["r"])
                k = rnd.uniform(*w["k"])
                o = {}
                if "warianty" in w:
                    o["wariant"] = rnd.choice(w["warianty"])
                if "cien" in w:
                    o["f"] = rnd.uniform(*w["cien"])
                if w["rodzina"] == "domek_tla":
                    o.update(szer=rnd.uniform(9.0, 13.0), gl=rnd.uniform(7.0, 9.5), wys=rnd.uniform(7.5, 10.5), dach=rnd.choice(DACHY),
                             sciana=rnd.choice(SCIANY), okna=rnd.choice((1, 2, 2)))
                if self.postaw(w["grupa"], w["rodzina"], kat, r, k, None, o, dosun=dosun, twarza=w.get("twarza", False),
                               odstep=w.get("min_odstep", 0.0), r_maks=w["r"][1] + (30.0 if dosun else 0.0), pchniec=8 if dosun else 0):
                    postawione += 1
                    break
        return postawione

    def punkty(self):
        rnd = self.rnd
        for pk in self.A.get("punkty", []):
            rod = pk["rodzina"]
            if rod == "kladka":
                self.kladka(pk)
                continue
            if rod == "girlanda":
                self.girlanda(pk)
                continue
            if rod == "mur_luk":
                self.mur_luk(pk)
                continue
            twarza = rod in TWARZA
            ry = pk.get("ry", None if rod not in ("olbrzym", "promien_swiatla") else 0.0)
            if rod == "lodka":                                 # łódka bokiem do pomostu (stycznie)
                a = math.radians(pk["kat"])
                ry = ku_srodkowi(pk["r"] * math.cos(a), pk["r"] * math.sin(a)) + 90.0 + pk.get("ry", 0.0)
            o = {k: v for k, v in pk.items() if k not in ("grupa", "rodzina", "kat", "r", "k", "ry")}
            ok = self.postaw(pk["grupa"], rod, pk["kat"], pk["r"], pk.get("k", 1.0), ry if not twarza else pk.get("ry", 0.0), o,
                             dosun=pk.get("dosun", True), twarza=twarza, pchniec=12, krok=2.0, odstep=0.0)
            if ok:
                x, z, h, obrot = self.ostatnie
                self.kotwice.setdefault(pk["grupa"], []).append({"rodzina": rod, "x": round(x, 2), "z": round(z, 2), "h": round(h, 2),
                                                                 "ry": round(obrot, 1), "opcje": {k: v for k, v in o.items()
                                                                                                  if isinstance(v, (int, float))}})

    def kladka(self, pk):
        """Kładka z pomostu ku chacie: deski na wysokości pomostu (grunt), pale pod nią w wodzie, poprzeczki."""
        s = self.s
        a = math.radians(pk["kat"])
        r0, r1 = pk["r_od"], pk["r_do"]
        dl = r1 - r0
        sr = (r0 + r1) / 2.0
        ry = 90.0 - pk["kat"]
        with s.grupa(pk["grupa"]), s.cechy(cien=False), s.uklad(pos=(sr * math.cos(a), 0, sr * math.sin(a)), obrot=(0, ry, 0)):
            s.blok("Kładka", (0, -0.2, 0), (4.0, 0.4, dl + 0.6), "bagno_deska", "WoodPlanks")
            for i in range(int(dl / 1.6)):
                zz = -dl / 2.0 + 0.8 + i * 1.6
                s.blok("Kładka szczelina", (0, 0.015, zz), (4.0, 0.04, 0.16), "bagno_deska_ciemna")
            for i in range(int(dl / 6.0) + 1):
                zz = -dl / 2.0 + 1.0 + i * 6.0
                for zn in (-1, 1):
                    s.walec("Kładka pal", (zn * 2.1, -1.2, zz), 0.32, 2.2, "bagno_kora", "Wood", os="y")
        self.zajete.append((sr * math.cos(a), sr * math.sin(a), 2.5, pk["grupa"]))

    def girlanda(self, pk):
        a1, a2 = math.radians(pk["kat1"]), math.radians(pk["kat2"])
        p1 = (pk["r1"] * math.cos(a1), pk["r1"] * math.sin(a1))
        p2 = (pk["r2"] * math.cos(a2), pk["r2"] * math.sin(a2))
        n0 = len(self.s.czesci)
        with self.s.grupa(pk["grupa"]):
            R.girlanda(self.s, self.rnd, p1, p2, pk["y"], pk["y"], n=9)
        if self.narusza(n0):
            del self.s.czesci[n0:]
            self.stat["pominiete"]["girlanda"] = 1

    def mur_luk(self, pk):
        """Mur miejski po łuku (odcinki co ok. 9°), opcjonalna brama (kąt) i baszty."""
        a0, a1 = pk["luk"]
        r = pk["r"]
        brama = pk.get("brama")
        n = max(2, int(((a1 - a0) % 360) / 9.0))
        katy = [a0 + (a1 - a0) * i / n for i in range(n + 1)]
        s = self.s
        odcinki = []
        for k1, k2 in zip(katy, katy[1:]):
            if brama is not None:
                pol = math.degrees(6.0 / r) + 0.5             # przerwa na bramę (baszty bramy domykają mur)
                if k2 > brama - pol and k1 < brama + pol:
                    if k1 < brama - pol - 0.5:
                        odcinki.append((k1, brama - pol))
                    if k2 > brama + pol + 0.5:
                        odcinki.append((brama + pol, k2))
                    continue
            odcinki.append((k1, k2))
        with s.grupa(pk["grupa"]):
            for k1, k2 in odcinki:
                p1 = (r * math.cos(math.radians(k1)), r * math.sin(math.radians(k1)))
                p2 = (r * math.cos(math.radians(k2)), r * math.sin(math.radians(k2)))
                R.mur_odcinek(s, self.rnd, p1, p2, pk["wys"])
            if brama is not None:
                a = math.radians(brama)
                x, z = r * math.cos(a), r * math.sin(a)
                R.brama_miejska(s, self.rnd, (x, 0, z), ku_srodkowi(x, z), pk["wys"])
            for kat in pk.get("wieze", []):
                a = math.radians(kat)
                R.wieza_miejska(s, self.rnd, (r * math.cos(a), 0, r * math.sin(a)), ku_srodkowi(r * math.cos(a), r * math.sin(a)),
                                pk["wys"] + 9.0, self.rnd.choice(("dach_twierdza", "dach_karczma", "dach_gildia")))
        self.stat["postawione"]["mur"] = self.stat["postawione"].get("mur", 0) + 1

    def korony_nad(self):
        kn = self.A.get("korony_nad")
        if not kn:
            return
        s, rnd = self.s, self.rnd
        n = kn["n"]
        for i in range(n):
            kat = 360.0 * (i + rnd.uniform(-0.3, 0.3)) / n
            szer = rnd.uniform(*kn["szer"])
            dl = rnd.uniform(*kn["dl"])
            r = max(kn["r_wew"] + szer / 2.0, rnd.uniform(kn["r_wew"] + szer / 2.0, kn["r_zew"] - szer / 2.0))
            if i % 2:
                r = kn["r_wew"] + szer / 2.0 + rnd.uniform(0, 6)
            a = math.radians(kat)
            y = rnd.uniform(*kn["y"])
            n0 = len(s.czesci)
            with s.grupa("Korony"):
                R.korona_nad(s, rnd, (r * math.cos(a), y, r * math.sin(a)), dl, szer, rnd.uniform(3.0, 4.6), 90.0 - kat,
                             tuple(rnd.choice(kn["kolory"])))
            if self.narusza(n0):
                del s.czesci[n0:]
                self.stat["pominiete"]["korona_nad"] = self.stat["pominiete"].get("korona_nad", 0) + 1

    def sylwety(self):
        s, rnd = self.s, self.rnd
        y0 = _y(self)
        for w in self.A.get("sylwety", []):
            rod = w["rodzina"]
            with s.grupa("Dal"):
                if rod == "wal":
                    R.wal_horyzontu(s, rnd, w["r"], w["wys"], w["kolor"], w.get("n", 24), y0 - 0.8)
                    continue
                if rod == "zamek_daleki":
                    a = math.radians(w["kat"])
                    x, z = w["r"] * math.cos(a), w["r"] * math.sin(a)
                    R.wzgorze(s, rnd, (x, y0 - 1.0, z), 110.0, w["y"] + 4.0, "arena_wzgorze_miasto", 90.0 - w["kat"])
                    R.zamek_daleki(s, rnd, (x, y0 + w["y"] - 2.0, z), w["k"], 90.0 - w["kat"])
                    continue
                kroki = int(round(360.0 / w["krok_kata"]))
                for i in range(kroki):
                    kat = (i + rnd.uniform(-0.3, 0.3)) * w["krok_kata"]
                    if "luki" in w and not any(_w_luku(kat, a0, a1) for a0, a1 in w["luki"]):
                        continue
                    r = rnd.uniform(*w["r"])
                    a = math.radians(kat)
                    x, z = r * math.cos(a), r * math.sin(a)
                    if rod == "wzgorze":
                        R.wzgorze(s, rnd, (x, y0 - 1.0, z), rnd.uniform(*w["szer"]), rnd.uniform(*w["wys"]), w["kolor"],
                                  90.0 - kat + rnd.uniform(-10, 10))
                    elif rod == "korona_daleka":
                        R.korona_daleka(s, rnd, (x, y0, z), rnd.uniform(*w["k"]), w["kolor"])
                    elif rod == "sylweta_cyprysu":
                        R.sylweta_cyprysu(s, rnd, (x, y0, z), rnd.uniform(*w["k"]), w["kolor"])
                    elif rod == "dach_daleki":
                        R.dach_daleki(s, rnd, (x, y0, z), rnd.uniform(*w["k"]), 90.0 - kat)
                    else:
                        raise ValueError(rod)

    def mgla_platy(self):
        m = self.A.get("mgla_platy")
        if not m:
            return
        s, rnd = self.s, self.rnd
        with s.grupa("Mgla"):
            for _ in range(m["n"]):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(*m["r"])
                R.mgla_plat(s, rnd, (r * math.cos(a), 0, r * math.sin(a)), rnd.uniform(*m["dl"]), rnd.uniform(*m["szer"]), m["y"], m["alfa"])

    # ---- całość
    def buduj(self):
        self.grunt()
        self.plac()
        self.obrecz()
        self.punkty()
        kolejnosc = sorted(self.A["warstwy"], key=lambda w: {"Kulisy": 0, "Sciana": 1, "Bliskie": 2}.get(w["grupa"], 3))
        for w in kolejnosc:
            self.warstwa(w)
        self.korony_nad()
        self.sylwety()
        self.mgla_platy()
        # wykończenie: bez kolizji wszędzie, bez cienia daleko
        for c in self.s.czesci:
            cechy = (c[15] if len(c) > 15 else 0) | 1
            if math.hypot(c[2], c[4]) > DALEKO:
                cechy |= 2
            if len(c) > 15:
                c[15] = cechy
            else:
                c.append(cechy)
        return self


def _w_luku(kat, a, b):
    kat, a, b = kat % 360.0, a % 360.0, b % 360.0
    return a <= kat <= b if a <= b else (kat >= a or kat <= b)


# --------------------------------------------------------------------------- kontrola na częściach (też sprawdz.py)
def naruszenia(czesci_sceny, prof, zapas=ZAPAS):
    """Lista (indeks, nazwa, ile punktów, najgłębiej) części w układzie sceny, które łamią wolną przestrzeń kamer
    albo stoją nad placem. Grunt (wierzch ≤ GRUNT_Y) i części niewidzialne nie łamią."""
    wynik = []
    for i, c in enumerate(czesci_sceny):
        if c[13] >= 0.98 or geom.gora(c) <= GRUNT_Y:
            continue
        E = geom.polowki(c)
        krok = max(0.7, float(E.max()) * 2.0 / 14.0)
        pts = geom.punkty(c, krok=krok, maks=18)
        x, y, z = pts[:, 0], pts[:, 1], pts[:, 2]
        r = np.hypot(x, z)
        granica = prof.promien(x, z, y)
        zle = ((granica > 0) & (r < granica + zapas)) | ((r < P.R_PLAC + PLAC_ZAPAS) & (y > GRUNT_Y))
        if zle.any():
            glebia = float(np.max(np.where(zle, np.maximum(granica + zapas - r, 0.0), 0.0)))
            wynik.append((i, c[14], int(zle.sum()), round(glebia, 2)))
    return wynik


# --------------------------------------------------------------------------- zapis
def znaczniki(b):
    A = b.A
    O = A["O"]
    st = b.s.statystyki()
    return {
        "opis": ("Znaczniki areny walki „%s” (swiat/areny_walki, generuj.py). Układ SCENY: X w prawo na ekranie, Y w górę od "
                 "płyty placu, Z ku kamerze planu ogólnego; świat = (Ox − x, Oy + y, Oz − z)." % A["nazwa"]),
        "arena": b.klucz, "nazwa": A["nazwa"], "model": "Workspace/ArenyWalki/" + A["model"], "biom": A["biom"],
        "zrodla": A["zrodla"],
        "scena": {"pozycja": list(O), "patrz": [0, 0, 1], "uwaga": "CFrame.lookAt(pozycja, pozycja + (0, 0, 1)) = cfSceny odtwarzacza"},
        "plac": {"r": P.R_PLAC, "wierzch_y": 0.0},
        "pudlo": {"srodek": [O[0], O[1] + 60.0, O[2]], "rozmiar": [2 * P.R_GRUNT + 20, 220.0, 2 * P.R_GRUNT + 20]},
        "czesci": len(b.s.czesci), "budzet": P.BUDZET, "budzet_twardy": P.BUDZET_TWARDY,
        "grupy": {g.split("/", 3)[-1]: n for g, n in sorted(st["grupy"].items())},
        "zakres_swiat": None,
        "postawione": b.stat["postawione"], "pominiete": b.stat["pominiete"], "dosuniete": b.stat["dosuniete"],
        "nastroj": A["nastroj"], "detale": A.get("detale", []), "kotwice": b.kotwice,
    }


def do_swiata_json(b):
    d = b.s.json()
    O = b.A["O"]
    d["czesci"] = [geom.do_swiata(c, O) for c in b.s.czesci]
    return d


def luau_wartosc(v, wciecie=1):
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "nil"
    if isinstance(v, (int, float)):
        return repr(round(v, 4)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    t = "\t" * wciecie
    if isinstance(v, (list, tuple)):
        if all(isinstance(x, (int, float, str)) for x in v):
            return "{ " + ", ".join(luau_wartosc(x) for x in v) + " }"
        return "{\n" + "".join(t + "\t" + luau_wartosc(x, wciecie + 1) + ",\n" for x in v) + t + "}"
    if isinstance(v, dict):
        czesci = []
        for k, x in v.items():
            klucz = k if k.isidentifier() else "[%s]" % json.dumps(k, ensure_ascii=False)
            czesci.append(t + "\t" + klucz + " = " + luau_wartosc(x, wciecie + 1) + ",\n")
        return "{\n" + "".join(czesci) + t + "}"
    raise TypeError(type(v))


def dane_luau(wyniki):
    """zrodla/DaneAren.luau — dane dla modułu ArenyWalki (bez instancji; testowane interpreterem)."""
    areny = {}
    for klucz, z in wyniki.items():
        A = P.ARENY[klucz]
        areny[klucz] = {"nazwa": A["nazwa"], "model": A["model"], "biom": A["biom"], "czesci": z["czesci"], "yGruntu": A["grunt"]["y"],
                        "scena": z["scena"]["pozycja"], "pudloSrodek": z["pudlo"]["srodek"], "pudloRozmiar": z["pudlo"]["rozmiar"],
                        "nastroj": A["nastroj"], "detale": A.get("detale", []),
                        "kotwice": {g: [[q["x"], q["z"], q["h"]] for q in lista] for g, lista in z["kotwice"].items()}}
    zrodla = {zr: k for k, A in P.ARENY.items() for zr in A["zrodla"] if k in wyniki}
    tekst = ("-- Wygenerowane przez swiat/areny_walki/generuj.py z plan.py — nie edytuj ręcznie.\n"
             "-- Dane aren walki zależnych od biomu (D-095): źródło walki → arena, nastrój i detale. Pozycje kotwic w układzie\n"
             "-- SCENY (x w prawo na ekranie, y w górę od płyty placu, z ku kamerze planu ogólnego).\n"
             "if not game:GetService(\"RunService\"):IsStudio() then\n\treturn {}\nend\n\n"
             "return {\n\twersja = %s,\n\trPlacu = %s,\n\tzrodla = %s,\n\tareny = %s,\n}\n"
             % (json.dumps(time.strftime("%Y-%m-%d")), repr(P.R_PLAC), luau_wartosc(zrodla), luau_wartosc(areny)))
    return tekst


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Generator aren walki (plan.py → czesci.json, znaczniki.json, DaneAren.luau)")
    ap.add_argument("--tylko", default="", help="klucze aren po przecinku (domyślnie wszystkie)")
    a = ap.parse_args()
    t0 = time.time()
    prof = kamery.profil()
    print("profil kamer: %d położeń, r_max %.1f, y_max %.1f" % (prof.kamer, prof.r_max_kamery, prof.y_max_kamery))
    tylko = [k for k in a.tylko.split(",") if k]
    wyniki = {}
    for klucz, A in P.ARENY.items():
        plik_z = os.path.join(TU, klucz, "znaczniki.json")
        if tylko and klucz not in tylko:
            if os.path.isfile(plik_z):
                with open(plik_z, encoding="utf-8") as f:
                    wyniki[klucz] = json.load(f)
            continue
        t1 = time.time()
        b = Budowa(klucz, A, prof).buduj()
        os.makedirs(os.path.join(TU, klucz), exist_ok=True)
        d = do_swiata_json(b)
        with open(os.path.join(TU, klucz, "czesci.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
        z = znaczniki(b)
        mn = [min(c[2 + i] for c in d["czesci"]) for i in range(3)]
        mx = [max(c[2 + i] for c in d["czesci"]) for i in range(3)]
        z["zakres_swiat"] = {"min": [round(v, 1) for v in mn], "max": [round(v, 1) for v in mx]}
        with open(plik_z, "w", encoding="utf-8", newline="\n") as f:
            json.dump(z, f, ensure_ascii=False, indent=1)
            f.write("\n")
        wyniki[klucz] = z
        print("%-6s %-32s %4d części (budżet %d) · pominięte %s · dosunięte %d (%.1f s)"
              % (klucz, A["nazwa"], len(b.s.czesci), P.BUDZET, b.stat["pominiete"] or "—", b.stat["dosuniete"], time.time() - t1))
    with open(os.path.join(TU, "zrodla", "DaneAren.luau"), "w", encoding="utf-8", newline="\n") as f:
        f.write(dane_luau(wyniki))
    print("gotowe w %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
