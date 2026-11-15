#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator biomu Las „Bór Pod Ukłonem” — składa mapę z klocków z uklad.json i potwory.json.

    python -B swiat/biom_las/generuj.py                     # → czesci.json, znaczniki.json, ujecia_swiat.json
    python -B swiat/biom_las/generuj.py --znaczniki-widoczne --wyj <folder>/czesci_znaczniki.json
                                                            # podgląd z zastępczymi bryłami potworów i placami walki

Kontrakt: PROJEKT.md. Układ lasu: środek Ukłonu (0; 0), północ lasu = −Z, łąka y = 0. W pliku części las stoi tam,
gdzie ma stanąć w Studio: kontener Workspace/BiomLas, środek (0; 0; −2000), obrót 180° wokół pionu, czyli punkt lasu
(x; y; z) → świat (−x; y; −2000 − z). znaczniki.json (strefy, węzły walki, domy, patrole, troll, strażnik, punkty E,
piny, grupy stale wczytane i z niskim detalem) jest w układzie lasu — następny krok (potwory w Studio) przelicza tym
samym wzorem. Wynik deterministyczny (random.Random(ziarno)).

Kolejność: teren (płyta, plamy, poziomy, urwiska z warstwami i piargiem, kopce, rampy) → woda → ścieżki → lokacje →
domy potworów i podkładki stref → drogowskazy → rekwizyty przy lokacjach (detale.py) → rozsiew roślin i kamieni
(z maską: ścieżki, woda, place walki r 12 + korona, trasy potworów, rampy, urwiska) → garby, brzegi ścieżek, runo
i kłody (detale.py) → mur → tło → FAKTURY (faktury.naloz: materiał według roli każdej części) → kontrola placów walki
NA PRAWDZIWYCH CZĘŚCIACH → zapis i raport (części, sufity, udział materiałów, detale na 100 st ścieżki).
"""
import argparse
import json
import math
import os
import random
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import Scena, macierz_obrotu, KULA, WALEC  # noqa: E402
from swiat.biom_las import detale, faktury, geo, rosliny, skaly, teren  # noqa: E402
from swiat.biom_las.lokacje import REJESTR, wspolne  # noqa: E402
from swiat.biom_las.lokacje.serce import lampiony_polany  # noqa: E402
from swiat.biom_las.lokacje.wawoz import prog_ujscia  # noqa: E402
from swiat.biom_las.paleta import PALETA  # noqa: E402

KONTENER = "Workspace/BiomLas"
SRODEK_SWIATA = (0.0, 0.0, -2000.0)
OBROT_Y = 180.0
LIMIT = 25000
GRUPA_PODBIOMU = {"laka": "Laka", "kapeluszowo": "Kapeluszowo", "serce": "Serce", "ostepy": "Ostepy", "wawoz": "Wawoz",
                  "korona": "Korona"}


def do_swiata(x, y, z):
    return (SRODEK_SWIATA[0] - x, y, SRODEK_SWIATA[2] - z)


# =========================================================================== kontekst: dane, maski, rezerwacje
class Kontekst:
    KROK = 2.0

    def __init__(self, ziarno):
        self.U, self.P = geo.wczytaj("uklad.json"), geo.wczytaj("potwory.json")
        self.T = geo.Teren(self.U)
        self.pod = {b["id"]: b for b in self.U["podbiomy"]}
        self.GRUPA_PODBIOMU = GRUPA_PODBIOMU
        r = random.Random(ziarno)
        for nazwa in ("teren", "woda", "sciezki", "mur", "tlo", "lokacje", "domy", "rozsiew", "detale"):   # nowe strumienie
            setattr(self, "rnd_" + nazwa, random.Random(r.randint(0, 10 ** 9)))                          # tylko na końcu
        k = self.KROK
        self.xs = np.arange(-500 + k / 2, 500, k)
        X, Z = np.meshgrid(self.xs, self.xs)
        self.X, self.Z = X, Z
        self.H = self.T.H_np(X, Z)
        d = np.full(X.shape, 1e9)
        for sc in self.U["sciezki"]:
            d = np.minimum(d, geo.odl_lamana_np(X, Z, sc["pts"]) - sc["szer"] / 2.0)
        self.d_sciezka = d
        dw = np.full(X.shape, 1e9)
        for w in self.U["woda"]:
            if w["rodzaj"] == "struga":
                dw = np.minimum(dw, geo.odl_lamana_np(X, Z, geo.wygladz(w["pts"], 3)) - max(w["szer"]) / 2.0 - 1.2)
            elif "wielokat" in w:
                wew = geo.w_wielokacie_np(X, Z, w["wielokat"])
                dw = np.minimum(dw, np.where(wew, -1.0, geo.odl_lamana_np(X, Z, w["wielokat"] + [w["wielokat"][0]])))
            else:
                dw = np.minimum(dw, np.hypot(X - w["srodek"][0], Z - w["srodek"][1]) - w["r"] - 1.6)
        self.d_woda = dw
        dn = np.full(X.shape, 1e9)
        dt = np.full(X.shape, 1e9)
        for st in self.P["strefy"]:
            for x, z in st["trasa"]:
                dn = np.minimum(dn, np.hypot(X - x, Z - z))
            tr = st["trasa"] + ([st["trasa"][0]] if st["id"] != "z09" else [])
            dt = np.minimum(dt, geo.odl_lamana_np(X, Z, tr))
        self.d_walka = dn
        self.d_trasa = dt
        dp = np.full(X.shape, 1e9)
        for p in self.P.get("patrole", []):
            dp = np.minimum(dp, geo.odl_lamana_np(X, Z, p["trasa"]))
        self.d_patrol = dp
        self.d_troll = geo.odl_lamana_np(X, Z, self.P["troll"]["trasa"])
        ramp = np.full(X.shape, 1e9)
        for e in self.T.rampy:
            ramp = np.minimum(ramp, geo.odl_lamana_np(X, Z, [e["od"][:2], e["do"][:2]]) - e["szer"] / 2.0)
        self.d_rampa = ramp
        # nierówność: różnica wysokości w promieniu ok. 4 (krawędzie poziomów, zbocza)
        hp = np.pad(self.H, 2, mode="edge")
        n = self.H.shape[0]
        mx = np.max([hp[2 + di:2 + di + n, 2 + dj:2 + dj + n] for di in (-2, 0, 2) for dj in (-2, 0, 2)], axis=0)
        mn = np.min([hp[2 + di:2 + di + n, 2 + dj:2 + dj + n] for di in (-2, 0, 2) for dj in (-2, 0, 2)], axis=0)
        self.nierownosc = mx - mn
        self.zajete = np.zeros(X.shape, dtype=bool)
        # wersja 2: osobne maski dla detali — rdzenie lokacji i rekwizyty (kopia `zajete` przed rozsiewem), pnie drzew
        # i głazów (detal nie wchodzi w pień, ale może leżeć pod koroną), kępy runa i garby (odstęp między nimi)
        self.lokacje_maska = np.zeros(X.shape, dtype=bool)
        self.pnie = np.zeros(X.shape, dtype=bool)
        self.detale_maska = np.zeros(X.shape, dtype=bool)
        self.garby_maska = np.zeros(X.shape, dtype=bool)
        self.pb_ids = list(self.pod.keys())
        pbg = np.full(X.shape, -1, dtype=int)
        for i, k in enumerate(self.pb_ids):
            pbg[geo.w_wielokacie_np(X, Z, self.pod[k]["wielokat"])] = i
        self.pb_siatka = pbg
        self.spokoj = [s for s in self.U["strefy_spokoju"] if "srodek" in s]

    # --- dostęp do siatek
    def _ij(self, x, z):
        i = int((z + 500) / self.KROK)
        j = int((x + 500) / self.KROK)
        n = len(self.xs)
        return min(max(i, 0), n - 1), min(max(j, 0), n - 1)

    def siatka(self, nazwa, x, z):
        i, j = self._ij(x, z)
        return float(getattr(self, nazwa)[i, j])

    def zajmij_w(self, maska, x, z, r):
        i0, j0 = self._ij(x - r, z - r)
        i1, j1 = self._ij(x + r, z + r)
        sub = (self.X[i0:i1 + 1, j0:j1 + 1] - x) ** 2 + (self.Z[i0:i1 + 1, j0:j1 + 1] - z) ** 2 <= r * r
        maska[i0:i1 + 1, j0:j1 + 1] |= sub

    def wolne_w(self, maska, x, z, r):
        i0, j0 = self._ij(x - r, z - r)
        i1, j1 = self._ij(x + r, z + r)
        sub = (self.X[i0:i1 + 1, j0:j1 + 1] - x) ** 2 + (self.Z[i0:i1 + 1, j0:j1 + 1] - z) ** 2 <= r * r
        return not bool((maska[i0:i1 + 1, j0:j1 + 1] & sub).any())

    def zajmij(self, x, z, r):
        self.zajmij_w(self.zajete, x, z, r)

    def wolne(self, x, z, r):
        return self.wolne_w(self.zajete, x, z, r)

    def podbiom_szybko(self, x, z):
        i, j = self._ij(x, z)
        v = int(self.pb_siatka[i, j])
        return None if v < 0 else self.pb_ids[v]

    # --- pytania używane przez teren.py i lokacje
    def na_sciezce(self, x, z, zapas=0.0, pomin=None):
        if pomin is None:
            return self.siatka("d_sciezka", x, z) < zapas
        return any(geo.odl_lamana((x, z), sc["pts"]) < sc["szer"] / 2.0 + zapas for sc in self.U["sciezki"] if sc is not pomin)

    def woda_odl(self, x, z):
        return geo.woda_odl(self.U, x, z)

    def przy_przeprawie(self, x, z, r):
        return any(math.hypot(x - p["x"], z - p["z"]) < r for p in self.U["przeprawy"])

    def w_przerwie_muru(self, x, z):
        return x < -425 and -200 < z < -160                    # Wrota Bagna

    def podbiom(self, x, z):
        for k, b in self.pod.items():
            if geo.w_wielokacie((x, z), b["wielokat"]):
                return k
        return None


# =========================================================================== domy potworów, podkładki, drogowskazy
PODKLADKI = {"z01": "runo", "z02": "runo", "z16": "runo", "z03": "runo", "z06": "runo", "z04": "mech", "z05": "mech",
             "z14": "mech", "z12": "kamien_cokol",
             # wersja 2: Ostępy mają ciemne runo boru — place wilków to jaśniejsze polanki `runo` (ΔL* 26 jak w wersji 1)
             "z07": "runo", "z08": "runo", "z09": "runo", "z10": "runo"}


def potwory_na_mapie(s, G, widoczne):
    rnd = G.rnd_domy
    for st in G.P["strefy"]:
        pb = GRUPA_PODBIOMU[st["podbiom"]]
        y = float(st["y"])
        cx, cz = st["srodek"]
        with s.grupa("%s/Strefy/%s" % (pb, st["id"])):
            if st["id"] in PODKLADKI:
                wspolne.podkladka(s, rnd, "Podkładka strefy", cx, y + teren.Y_PODKLADKA - 0.1, cz, st["r"], PODKLADKI[st["id"]], st["trasa"])
            for hx, hz in st["dom"]["pts"]:
                if st["id"] == "z01":
                    continue                                   # dom = woda Oczka
                ry = math.degrees(math.atan2(cx - hx, cz - hz))
                if st["potwor"] == "Leśny Slime":
                    wspolne.kaluza_galarety(s, rnd, (hx, y, hz))
                elif st["potwor"] == "Muchomornik":
                    wspolne.chatka_grzyb(s, rnd, (hx, y, hz), ry, rnd.uniform(0.9, 1.15))
                elif st["podbiom"] in ("wawoz", "korona") and st["id"] != "z13":
                    wspolne.szpara(s, rnd, (hx, y, hz), ry)
                else:
                    wspolne.jama(s, rnd, (hx, y, hz), ry)
                G.zajmij(hx, hz, 7)
            if widoczne:
                with s.grupa("_Znaczniki/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
                    nazwa = "Bursztynowy Slime" if st.get("wariant") else st["potwor"]
                    for x, z in st["trasa"]:
                        s.walec("Plac walki r12", (x, y + 0.45, z), 12.0, 0.1, "czerwien", alfa=0.55, os="y")
                        wspolne.zastepczy_potwor(s, "Potwór", (x, y + 0.5, z), nazwa)
                    for hx, hz in st["dom"]["pts"]:
                        s.blok("Dom", (hx, y + 4.0, hz), (0.8, 8.0, 0.8), "neon_magia", "Neon")
    if widoczne:
        with s.grupa("_Znaczniki/troll"), s.cechy(kolizja=False, cien=False):
            tx, tz = G.P["troll"]["dom"]
            wspolne.zastepczy_potwor(s, "Troll", (tx, 0.0, tz), "Leśny Troll")
            tr = G.P["troll"]["trasa"]
            for a, b in zip(tr, tr[1:]):
                teren.wstega(s, "Trasa trolla", (a[0], G.T.H(*a) + 0.55, a[1]), (b[0], G.T.H(*b) + 0.55, b[1]), 1.0, 0.1, "drewno_ciemne")
        with s.grupa("_Znaczniki/straznik"), s.cechy(kolizja=False, cien=False):
            st = G.P["straznik"]
            wspolne.zastepczy_potwor(s, "Strażnik", (st["miejsce"][0], 32.0, st["miejsce"][1]), "Strażnik Gaju")
        with s.grupa("_Znaczniki/patrole"), s.cechy(kolizja=False, cien=False):
            for p in G.P.get("patrole", []):
                x, z = p["trasa"][len(p["trasa"]) // 2]
                wspolne.zastepczy_potwor(s, "Patrol", (x, G.T.H(x, z), z), p["potwor"])


DROGOWSKAZY = [  # (x, z na rozwidleniu, [cele (x, z, podbiom)])
    ((0, 50), [((0, 0), "serce"), ((200, 400), "laka")]),
    ((-35.4, 35.4), [((-290, 270), "kapeluszowo"), ((0, 0), "serce")]),
    ((-35.4, -35.4), [((-300, -50), "ostepy"), ((0, 0), "serce")]),
    ((0, -50), [((0, -385), "korona"), ((0, 0), "serce")]),
    ((50, 0), [((250, -195), "wawoz"), ((0, 0), "serce")]),
    ((110, 262), [((0, 0), "serce"), ((250, 300), "laka"), ((0, 395), "laka")]),
    ((-290, -130), [((-418, -180), "ostepy"), ((-300, -50), "ostepy"), ((-200, -262), "ostepy")]),
    ((-260, -200), [((0, -150), "korona"), ((-200, -262), "ostepy"), ((-300, -50), "ostepy")]),
    ((296, -6), [((250, -195), "wawoz"), ((342, 105), "wawoz"), ((0, 0), "serce")]),
    ((-290, 270), [((-370, 160), "kapeluszowo"), ((200, 400), "laka"), ((0, 0), "serce")]),
    ((350, 200), [((370, 240), "laka"), ((250, 300), "laka"), ((296, -6), "wawoz")]),
    ((100, -378), [((0, -385), "korona"), ((62, -424), "korona"), ((250, -195), "wawoz")]),
]


def drogowskazy(s, G):
    rnd = G.rnd_lokacje
    with s.grupa("Sciezki/Drogowskazy"):
        for (fx, fz), cele in DROGOWSKAZY:
            best = None
            for r in (9.0, 11.0, 13.0, 15.0, 18.0, 22.0):
                for k in range(16):
                    a = 2 * math.pi * k / 16
                    x, z = fx + r * math.cos(a), fz + r * math.sin(a)
                    d = G.siatka("d_sciezka", x, z)
                    if d < 2.0 or not G.wolne(x, z, 2.0) or G.siatka("nierownosc", x, z) > 0.3 or G.siatka("d_walka", x, z) < 13:
                        continue
                    if best is None or d < best[0]:
                        best = (d, x, z)
                if best:
                    break
            if not best:
                print("UWAGA: drogowskaz przy (%.0f;%.0f) — brak miejsca" % (fx, fz))
                continue
            _, x, z = best
            ramiona = [(math.degrees(math.atan2(tx - x, tz - z)), pb) for (tx, tz), pb in cele]
            wspolne.drogowskaz(s, rnd, (x, G.T.H(x, z), z), ramiona)
            G.zajmij(x, z, 2.5)


# =========================================================================== rozsiew roślin i kamieni
# (podbiom, warunek wysokości, rodzina, liczba, skala, odstęp, waga pasa przy ścieżkach)
ROZSIEW = [
    # wersja 2: w każdym podbiomie 3–4 sylwetki drzew (rosliny.py G–L), różna skala i odcień korony
    ("laka", (0, 0), "okraglak", 70, (0.8, 1.4), 13, 0.85),
    ("laka", (0, 0), "smukly", 18, (0.85, 1.2), 11, 0.8),
    ("laka", (0, 0), "dab", 10, (0.8, 1.05), 16, 0.6),
    ("laka", (0, 0), "krzak", 110, (0.8, 1.3), 5, 0.8),
    ("laka", (0, 0), "kwiaty", 70, None, 4, 0.8),
    ("laka", (0, 0), "kanciak", 40, (0.8, 1.4), 4, 0.6),
    ("kapeluszowo", (0, 0), "grzyb", 75, (0.8, 2.2), 11, 0.8),
    ("kapeluszowo", (0, 0), "dab", 36, (0.85, 1.3), 15, 0.7),
    ("kapeluszowo", (0, 0), "jarzebina", 12, (0.9, 1.2), 10, 0.7),
    ("kapeluszowo", (0, 0), "sosna_smukla", 6, (0.9, 1.1), 11, 0.6),
    ("kapeluszowo", (0, 0), "paproc", 90, (0.8, 1.3), 3, 0.6),
    ("kapeluszowo", (0, 0), "krzak", 40, (0.8, 1.2), 5, 0.7),
    ("kapeluszowo", (0, 0), "kwiaty_biale", 30, None, 4, 0.7),
    ("serce", (0, 4.5), "dab", 20, (0.9, 1.35), 15, 0.6),
    ("serce", (0, 4.5), "smukly", 8, (0.9, 1.2), 11, 0.6),
    ("serce", (0, 4.5), "jarzebina", 6, (0.9, 1.15), 10, 0.6),
    ("serce", (0, 4.5), "krzak", 45, (0.8, 1.2), 5, 0.7),
    ("serce", (0, 4.5), "kwiaty", 25, None, 4, 0.7),
    ("serce", (0, 4.5), "paproc", 25, (0.8, 1.2), 3, 0.6),
    ("ostepy", (0, 0), "sosna", 215, (1.0, 1.8), 10, 0.75),
    ("ostepy", (0, 0), "swierk", 60, (0.9, 1.4), 10, 0.75),
    ("ostepy", (0, 0), "sosna_smukla", 30, (0.95, 1.25), 10, 0.7),
    ("ostepy", (0, 0), "suchy", 14, (0.9, 1.2), 10, 0.6),
    ("ostepy", (0, 0), "jezyna", 90, (0.8, 1.2), 5, 0.7),
    ("ostepy", (0, 0), "paproc", 80, (0.8, 1.3), 3, 0.6),
    ("ostepy", (0, 0), "glaz", 35, (0.8, 1.4), 7, 0.5),
    ("ostepy", (32, 32), "sosna", 28, (0.9, 1.3), 12, 0.0),
    ("wawoz", (12, 12), "sosna", 85, (0.9, 1.55), 11, 0.5),
    ("wawoz", (12, 12), "sosna_smukla", 25, (0.9, 1.2), 11, 0.5),
    ("wawoz", (12, 12), "suchy", 6, (0.8, 1.1), 10, 0.5),
    ("wawoz", (12, 12), "jezyna", 30, (0.8, 1.1), 6, 0.5),
    ("wawoz", (0, 0), "glaz", 28, (0.9, 1.5), 8, 0.5),
    ("wawoz", (0, 0), "kanciak", 30, (0.8, 1.4), 4, 0.5),
    ("korona", (12, 32), "brzozka", 120, (0.85, 1.4), 10, 0.6),
    ("korona", (12, 32), "brzozka_podwojna", 18, (0.9, 1.2), 11, 0.6),
    ("korona", (12, 32), "jarzebina", 14, (0.85, 1.15), 10, 0.6),
    ("korona", (12, 32), "glaz", 50, (0.8, 1.4), 7, 0.4),
    ("korona", (12, 32), "kwiaty_biale", 30, None, 4, 0.6),
    ("korona", (0, 0), "dab", 8, (0.8, 1.0), 15, 0.5),
    ("korona", (0, 0), "krzak", 25, (0.8, 1.2), 5, 0.6),
]
KORONA = {"okraglak": 9.0, "dab": 15.0, "sosna": 9.0, "brzozka": 6.5, "grzyb": 8.0, "glaz": 3.6,   # pół przekątnej korony
          "smukly": 5.0, "sosna_smukla": 6.0, "swierk": 7.0, "suchy": 5.5, "brzozka_podwojna": 7.5, "jarzebina": 5.5}
WYSOKIE = set(KORONA)
PIEN = {"okraglak": 1.6, "dab": 2.4, "sosna": 1.2, "brzozka": 1.0, "grzyb": 1.4, "glaz": 3.0, "smukly": 1.2, "sosna_smukla": 1.1,
        "swierk": 1.1, "suchy": 1.3, "brzozka_podwojna": 1.6, "jarzebina": 1.0, "krzak": 2.0, "jezyna": 2.4, "kanciak": 1.6}
ODCIEN = (0.9, 0.96, 1.0, 1.0, 1.05)                         # odcień korony jednego drzewa (las nie z jednej formy)


def _postaw(s, G, rnd, rodzina, x, y, z, k, pb):
    ry = 15.0 * rnd.randint(0, 23)
    f = rnd.choice(ODCIEN)
    kor = tuple(rosliny.odcien(s, c, f) for c in rosliny.KORONY[pb])
    if rodzina == "okraglak":
        rosliny.okraglak(s, rnd, (x, y, z), k, ry, kor)
    elif rodzina == "dab":
        rosliny.dab(s, rnd, (x, y, z), k, ry, kor)
    elif rodzina == "sosna":
        rosliny.sosna(s, rnd, (x, y, z), k, ry, ciemna=pb == "ostepy", f=f)
    elif rodzina == "smukly":
        rosliny.smukly(s, rnd, (x, y, z), k, ry, kor)
    elif rodzina == "sosna_smukla":
        rosliny.sosna_smukla(s, rnd, (x, y, z), k, ry, ciemna=pb == "ostepy", f=f,
                             przechyl=rnd.uniform(4, 9) if pb == "wawoz" else rnd.uniform(0, 4))
    elif rodzina == "swierk":
        rosliny.swierk(s, rnd, (x, y, z), k, ry, f=f)
    elif rodzina == "suchy":
        rosliny.suchy(s, rnd, (x, y, z), k, ry)
    elif rodzina == "brzozka_podwojna":
        rosliny.brzozka_podwojna(s, rnd, (x, y, z), k, ry)
    elif rodzina == "jarzebina":
        rosliny.jarzebina(s, rnd, (x, y, z), k, ry, kolory=tuple(rosliny.odcien(s, c, f) for c in ("lisc_ciemny", "lisc")))
    elif rodzina == "brzozka":
        rosliny.brzozka(s, rnd, (x, y, z), k, ry)
    elif rodzina == "grzyb":
        kap = rnd.choice(("czerwien", "czerwien", "czerwien", "drewno", "tynk_krem"))
        rosliny.grzyb(s, rnd, (x, y, z), k, ry, kapelusz=kap, kropki=kap == "czerwien",
                      trzon="biel" if kap != "tynk_krem" else "drewno_jasne")
    elif rodzina == "krzak":
        rosliny.krzak(s, rnd, (x, y, z), k, jagoda=rnd.choice((None, "czerwien", "zloto")))
        if pb == "laka" and rnd.random() < 0.5:               # wersja 2: krzaki Łąki w kępach (mniej „parkowo”)
            a = rnd.uniform(0, 2 * math.pi)
            px, pz = x + 3.2 * k * math.cos(a), z + 3.2 * k * math.sin(a)
            if (G.siatka("d_sciezka", px, pz) > 2.5 and G.siatka("d_walka", px, pz) > 17.0 and G.siatka("d_trasa", px, pz) > 3.0
                    and G.siatka("d_woda", px, pz) > 1.5 and G.siatka("nierownosc", px, pz) <= 0.05):
                rosliny.krzak(s, rnd, (px, y, pz), k * rnd.uniform(0.6, 0.8))
    elif rodzina == "kwiaty":
        rosliny.kwiaty(s, rnd, (x, y, z), rnd.choice((("zloto", "biel"), ("czerwien", "zloto"), ("biel", "dach_sklep"))))
    elif rodzina == "kwiaty_biale":
        rosliny.kwiaty(s, rnd, (x, y, z), rnd.choice((("biel", "biel"), ("biel", "dach_sklep"), ("biel", "zloto"))))
    elif rodzina == "paproc":
        rosliny.paproc(s, rnd, (x, y, z), k)
    elif rodzina == "jezyna":
        rosliny.jezyna(s, rnd, (x, y, z), k)
    elif rodzina == "glaz":
        skaly.glaz(s, rnd, (x, y, z), k, ry, "kamien_cieply" if pb != "ostepy" else "kamien_lochu",
                   "SmoothPlastic" if pb != "ostepy" else "Slate", mech=rnd.random() < 0.6)
    elif rodzina == "kanciak":
        skaly.kanciak(s, rnd, (x, y, z), k, ry)


def rozsiew(s, G):
    rnd = G.rnd_rozsiew
    stat = {}
    for pb, (h0, h1), rodzina, n, skala, odstep, pas in ROZSIEW:
        w = G.pod[pb]["wielokat"]
        xs = [p[0] for p in w]
        zs = [p[1] for p in w]
        postawione = proby = 0
        rk = KORONA.get(rodzina, 2.0)
        while postawione < n and proby < n * 60:
            proby += 1
            x, z = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(zs), max(zs))
            if max(abs(x), abs(z)) > 428 or not geo.w_wielokacie((x, z), w):
                continue
            h = G.siatka("H", x, z)
            if not (h0 - 0.01 <= h <= h1 + 0.01) or G.siatka("nierownosc", x, z) > 0.05:
                continue
            k = rnd.uniform(*skala) if skala else 1.0
            dsc = G.siatka("d_sciezka", x, z)
            if dsc > 45 and rnd.random() > (1.0 - pas):        # gęsto w pasie przy ścieżkach, rzadziej w środku połaci
                continue
            wys = rodzina in WYSOKIE
            r_kor = rk * k
            if dsc < (max(3.0, r_kor * 0.9) if wys else 1.5):
                continue
            if G.siatka("d_woda", x, z) < (3.0 if wys else 1.0):
                continue
            if G.siatka("d_walka", x, z) < 14.0 + (r_kor if wys else 3.6):
                continue
            if G.siatka("d_trasa", x, z) < (5.0 if wys else 2.5) or G.siatka("d_patrol", x, z) < (12.0 if wys else 4.0):
                continue
            if G.siatka("d_troll", x, z) < (9.0 if wys else 3.0) or G.siatka("d_rampa", x, z) < 4.0:
                continue
            if pb == "serce" and math.hypot(x, z) < 80:
                continue
            if any(math.hypot(x - sp["srodek"][0], z - sp["srodek"][1]) < sp["r"] * 0.6 for sp in G.spokoj):
                continue
            if not G.wolne(x, z, odstep * 0.5 if wys else odstep * 0.6):
                continue
            # kępa w trójkach (duży–średni–mały) dla drobiazgów
            grupa = "%s/Las_%d_%d" % (GRUPA_PODBIOMU[pb], int((x + 500) // 125), int((z + 500) // 125))
            with s.grupa(grupa):
                _postaw(s, G, rnd, rodzina, x, h, z, k, pb)
                # po przeglądzie: z oczu gracza bór miał jasne runo jak Łąka. Pod sosnami Ostępów ciemne igliwie
                # (płaty runo_ciemne na 0,12, między plamą 0,06 a brzegiem wody 0,14; Ostępy nie mają podkładek stref),
                # więc place walki na jaśniejszym runie wyglądają jak polanki, a wilk na nich zostaje widoczny (ΔL* 26).
                # wersja 2: płat igliwia (Ground) także pod świerkami; nie sięga bliżej niż 13 od węzła walki (podkładka
                # placu zostaje jasna), leży na 0,115–0,13 (różne wysokości: nachodzące faktury nie migoczą)
                if pb == "ostepy" and rodzina in ("sosna", "swierk") and h0 == 0 and G.siatka("d_woda", x, z) > 10.0:
                    a = min(rnd.uniform(8.0, 11.0) * k, (G.siatka("d_walka", x, z) - 13.0) * 1.3)
                    if a > 4.0:
                        with s.cechy(kolizja=False, cien=False):
                            s.blok("Igliwie", (x, h + 0.015 + rnd.uniform(0.0, 0.015), z), (a, 0.2, a * rnd.uniform(0.75, 0.95)),
                                   "runo_ciemne", rot=(0, rnd.uniform(0, 90), 0))
            G.zajmij(x, z, odstep * 0.5 if wys else odstep * 0.4)
            G.zajmij_w(G.pnie, x, z, PIEN.get(rodzina, 0.0) * k if rodzina in PIEN else 0.0)
            postawione += 1
        stat["%s %s" % (pb, rodzina)] = (postawione, n)
    return stat


# =========================================================================== kontrola placów walki na częściach
def bryly(czesci):
    """Środki, macierze obrotu i połówki wymiarów części (prostopadłościany otaczające w układzie części)."""
    C = np.array([[c[2], c[3], c[4]] for c in czesci])
    R = np.zeros((len(czesci), 3, 3))
    E = np.zeros((len(czesci), 3))
    for i, c in enumerate(czesci):
        R[i] = np.array(macierz_obrotu(math.degrees(c[5]), math.degrees(c[6]), math.degrees(c[7])))
        sx, sy, sz = c[8], c[9], c[10]
        if c[0] == KULA:
            sx = sy = sz = min(sx, sy, sz)
        elif c[0] == WALEC:
            sy = sz = min(sy, sz)
        E[i] = (sx / 2.0, sy / 2.0, sz / 2.0)
    return C, R, E


def kontrola_placow(s, G):
    """Każdy węzeł walki: żadna część nie wchodzi w walec r 12 od 1,5 do 18 nad placem (pnie, ściany, skały, rekwizyty,
    nisko zawieszone korony). Odległość liczona do obróconej bryły części (nie do skrzynki osiowej)."""
    C, R, E = bryly(s.czesci)
    # pryzmaty poziomów, rampy i kopce sprawdza model wysokości (wezly.py, sprawdz.py: grunt ±0,5 w r 14)
    pomin = np.array([s.grupy[c[1]].split("/")[2] in ("_Znaczniki", "Mur", "Tlo", "Chmury")
                      or s.grupy[c[1]].split("/")[2:4] in (["Teren", "Poziomy"], ["Teren", "Rampy"], ["Teren", "Kopce"])
                      or (c[13] >= 1.0) for c in s.czesci])
    zasieg = np.linalg.norm(E, axis=1)
    bledy = []
    for st in G.P["strefy"]:
        y = float(st["y"])
        for x, z in st["trasa"]:
            wx, _, wz = do_swiata(x, y, z)
            kand = np.nonzero(~pomin & (np.hypot(C[:, 0] - wx, C[:, 2] - wz) < 12.0 + zasieg))[0]
            if not len(kand):
                continue
            os_ = np.array([[wx, y + h, wz] for h in np.arange(1.5, 18.01, 1.5)])
            d = os_[None, :, :] - C[kand][:, None, :]
            lok = np.einsum("nji,nkj->nki", R[kand], d)
            Ek = E[kand][:, None, :]
            nad_lok = lok - np.clip(lok, -Ek, Ek)                         # od najbliższego punktu bryły do punktu osi
            nad = np.einsum("nij,nkj->nki", R[kand], nad_lok)            # z powrotem do świata
            # bryła wchodzi w walec, gdy jakiś punkt osi (co 1,5) leży w poziomie < 12 od niej i prawie na jej wysokości
            dist = np.min(np.hypot(nad[:, :, 0], nad[:, :, 2]) + 100.0 * (np.abs(nad[:, :, 1]) > 0.05), axis=1)
            for i in kand[dist < 12.0][:3]:
                c = s.czesci[i]
                bledy.append("%s węzeł (%.0f;%.0f): „%s” w %s" % (st["id"], x, z, c[14], s.grupy[c[1]].split("/", 2)[-1]))
    return bledy


# =========================================================================== zapis
def znaczniki(s, G, plik):
    U, P = G.U, G.P
    punkty_e = []
    for c in s.czesci:
        g = s.grupy[c[1]]
        if g.endswith("/_Interakcja"):
            x, y, z = -c[2] + SRODEK_SWIATA[0], c[3], SRODEK_SWIATA[2] - c[4]
            punkty_e.append({"grupa": g[len(KONTENER) + 1:].rsplit("/_Interakcja", 1)[0], "punkt": [round(x, 1), round(y, 1), round(z, 1)]})
    grupy = sorted({g[len(KONTENER) + 1:] for g in s.grupy})
    stale = sorted({"/".join(g.split("/")[:2]) for g in grupy if g.startswith("Punkty/")})
    lod = sorted({"/".join(g.split("/")[:2]) for g in grupy if "/Las_" in g} | {g for g in grupy if g.startswith(("Mur/", "Tlo/"))})

    def zy(x, z, y=None):
        return [x, round(G.T.H(x, z) if y is None else y, 2), z]

    d = {
        "opis": "Znaczniki dla kroku „potwory w Studio”: strefy, węzły walki, domy, patrole, troll, strażnik, punkty E, piny. "
                "Współrzędne w UKŁADZIE LASU; świat Studio = (−x; y; −2000 − z) (kontener obrócony o 180°). Generuje generuj.py.",
        "kontener": {"nazwa": KONTENER, "srodek_swiata": list(SRODEK_SWIATA), "obrot_y": OBROT_Y,
                     "wzor": "swiat = (−x, y, −2000 − z)"},
        "wejscie": zy(*U["wejscie"]["punkt"]), "patrz_na": U["wejscie"]["patrz_na"],
        "odrodzenie_po_przegranej": zy(*U["odrodzenie_po_przegranej"]),
        "piny": [dict(p, punkt=zy(*p["punkt"])) for p in U["piny"]],
        "strefy_spokoju": U["strefy_spokoju"],
        "strefy": [{"id": st["id"], "podbiom": st["podbiom"], "potwor": st["potwor"], "wariant": st.get("wariant"),
                    "poziomy": st["poziomy"], "naraz": st["naraz"], "max": st["max"], "srodek": [st["srodek"][0], st["y"], st["srodek"][1]],
                    "r": st["r"], "wezly": [[x, st["y"], z] for x, z in st["trasa"]], "domy": [[x, st["y"], z] for x, z in st["dom"]["pts"]],
                    "odrodzenie_s": st["odrodzenie_s"], "grupa": st["grupa"], "zachowanie": st["zachowanie"]} for st in P["strefy"]],
        "patrole": [dict(p, trasa=[zy(x, z) for x, z in p["trasa"]]) for p in P.get("patrole", [])],
        "troll": dict(P["troll"], trasa=[zy(x, z) for x, z in P["troll"]["trasa"]]),
        "straznik": P["straznik"],
        "zasady": P["zasady"],
        "punkty_e": punkty_e,
        "grupy_stale_wczytane": {"ModelStreamingMode": "Persistent", "grupy": stale,
                                 "dlaczego": "sylwetki punktów orientacyjnych nie znikają z daleka przy streamingu"},
        "grupy_niski_detal": {"LevelOfDetail": "StreamingMesh", "grupy": lod,
                              "dlaczego": "kępy lasu, mur i tło widać z daleka jako uproszczoną bryłę, gdy wyjdą poza promień streamingu"},
    }
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
        f.write("\n")


def ujecia_swiata(plik_wej, plik_wyj):
    with open(plik_wej, encoding="utf-8") as f:
        uj = json.load(f)
    wyn = []
    for n, cam, cel, ogn, orto in uj:
        wyn.append([n, list(do_swiata(*cam)), list(do_swiata(*cel)), ogn, orto])
    with open(plik_wyj, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join(" " + json.dumps(u, ensure_ascii=False) for u in wyn) + "\n]\n")


PRZEZROCZYSTE_MAX = 40       # wersja 2: tafle jezior i stawów (ok. 24 części) + mgła — PROJEKT.md rozdz. 14


def raport(s):
    pref = len(s.korzen) + 1
    gl = {}
    for c in s.czesci:
        g = s.grupy[c[1]][pref:].split("/")[0]
        gl[g] = gl.get(g, 0) + 1
    print("CZĘŚCI: %d (limit %d, cel wersji 2 ok. 22 000)" % (len(s.czesci), LIMIT))
    for g in sorted(gl, key=lambda k: -gl[k]):
        print("  %-14s %6d" % (g, gl[g]))
    mats = s.materialy
    n = float(len(s.czesci))
    neon = sum(1 for c in s.czesci if mats[c[12]] == "Neon")
    kule = sum(1 for c in s.czesci if c[0] == KULA)
    walce = sum(1 for c in s.czesci if c[0] == WALEC)
    przezr = sum(1 for c in s.czesci if 0 < c[13] < 1)
    bez_kol = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 1)
    bez_cien = sum(1 for c in s.czesci if len(c) > 15 and c[15] & 2)
    print("SUFITY: Neon %d (≤300), kule %d (≤300), walce %d (≤3000), przezroczyste %d (≤%d), z kolizją %.0f%% (≤25%%), "
          "bez cienia %.0f%% (≥50%%)" % (neon, kule, walce, przezr, PRZEZROCZYSTE_MAX, 100 * (n - bez_kol) / n, 100 * bez_cien / n))
    ud = faktury.udzialy(s)
    razem = ud["razem"]
    print("MATERIAŁY (udział w częściach): " + ", ".join("%s %.1f%%" % (m, 100 * v / n) for m, v in
                                                         sorted(razem.items(), key=lambda kv: -kv[1])))
    for g in sorted(gl, key=lambda k: -gl[k]):
        m = ud[g]
        print("  %-12s %s" % (g, ", ".join("%s %d" % (k, v) for k, v in sorted(m.items(), key=lambda kv: -kv[1]))))
    return gl


# =========================================================================== całość
def generuj(ziarno=7, widoczne=False):
    s = Scena(KONTENER, paleta=PALETA)
    G = Kontekst(ziarno)
    with s.uklad(pos=SRODEK_SWIATA, obrot=(0, OBROT_Y, 0)):
        teren.grunt(s, G)
        teren.woda(s, G)
        teren.sciezki(s, G)
        for l in G.U["lokacje"]:
            f = REJESTR.get(l["id"])
            if f is None:
                if not l.get("wewnatrz"):
                    print("UWAGA: brak modułu lokacji", l["id"])
                continue
            f(s, G, random.Random(G.rnd_lokacje.randint(0, 10 ** 9)), l)
        lampiony_polany(s, G, G.rnd_lokacje)
        for t in range(0, 101, 10):                            # korytarz widoku z Ławki na las (bez drzew na płaskowyżu)
            G.zajmij(62 - 0.35 * t, -418 + t, 14 + 0.25 * t)
        G.zajmij(258, -100, 12)                                # Wartownia: widok z półki w rynnę (ujęcie l17)
        prog_ujscia(s, G, G.rnd_lokacje)
        G.zajmij(349, 168, 14)
        potwory_na_mapie(s, G, widoczne)
        drogowskazy(s, G)
        G.lokacje_maska |= G.zajete                            # wersja 2: rdzenie lokacji, domy, drogowskazy — bez detali
        stat = {"rekwizyty": detale.rekwizyty_lokacji(s, G)}
        stat["rozsiew"] = rozsiew(s, G)
        stat["garby"] = detale.garby(s, G)
        stat["sciezki"] = detale.brzegi_sciezek(s, G)
        stat["runo"] = detale.runo(s, G)
        teren.mur(s, G)
        teren.tlo(s, G)
    return s, G, stat


def main():
    ap = argparse.ArgumentParser(description="Generator biomu Las")
    ap.add_argument("--ziarno", type=int, default=7)
    ap.add_argument("--wyj", default=os.path.join(TU, "czesci.json"))
    ap.add_argument("--znaczniki-widoczne", action="store_true", help="dodaj zastępcze bryły potworów i place walki (tylko podgląd)")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    s, G, stat = generuj(a.ziarno, a.znaczniki_widoczne)
    brak_roli = faktury.naloz(s)
    s.zapisz(a.wyj)
    katalog = os.path.dirname(os.path.abspath(a.wyj))
    if not a.znaczniki_widoczne:
        znaczniki(s, G, os.path.join(TU, "znaczniki.json"))
    ujecia_swiata(os.path.join(TU, "ujecia.json"), os.path.join(katalog, "ujecia_swiat.json"))
    raport(s)
    roz = stat["rozsiew"]
    niepelne = ["%s %d/%d" % (k, v[0], v[1]) for k, v in roz.items() if v[0] < v[1]]
    print("ROZSIEW: %d rodzin%s" % (len(roz), ("; niepełne: " + ", ".join(niepelne)) if niepelne else ", wszystkie pełne"))
    n_rek, braki = stat["rekwizyty"]
    print("DETALE: rekwizyty przy lokacjach %d%s" % (n_rek, ("; bez miejsca: " + ", ".join(braki)) if braki else ""))
    st_sc, dlug = stat["sciezki"]
    print("  brzegi ścieżek (sztuk / 100 st): " + ", ".join("%s %d (%.1f)" % (k, st_sc.get(k, 0), 100.0 * st_sc.get(k, 0) / v)
                                                         for k, v in sorted(dlug.items())))
    print("  kępy runa i kłody: " + ", ".join("%s %d/%d + %d/%d" % ((k,) + v) for k, v in stat["runo"].items()))
    print("  garby: " + ", ".join("%s %d/%d" % ((k,) + v) for k, v in stat["garby"].items()))
    print("FAKTURY: %s" % ("każda część ma rolę" if not brak_roli else "BEZ ROLI: " + ", ".join(brak_roli)))
    bl = kontrola_placow(s, G)
    print("PLACE WALKI (na częściach, r 12, 1,5–18 nad gruntem): %s" % ("czyste" if not bl else "%d problemów" % len(bl)))
    for b in bl[:40]:
        print("  BŁĄD:", b)
    uwagi = s.sprawdz(min_y=-12.0, limit_czesci=LIMIT)
    print("SPRAWDZ (biblioteka): %d ostrzeżeń" % len(uwagi))
    for u in uwagi[:40]:
        print("  UWAGA:", u)
    print("ZAPISANO:", a.wyj)
    return 1 if bl or brak_roli else 0


if __name__ == "__main__":
    sys.exit(main())
