# -*- coding: utf-8 -*-
"""Kontekst generatora „Las jako wąski pas”: plan z swiat/biom_las/pas/plan_pasa.json, układ pasa i maski miejsca.

Układ pasa (jak w planie): u wzdłuż (0 = początek lasu, rośnie ku Bagnu), v w poprzek (v > 0 po prawej ręce idącego do
bramy), y w górę. Świat Studio = (X0 + u; y; Z0 + v) = (1100 + u; y; −700 + v), BEZ obrotu — generator buduje wszystko
w układzie lokalnym `s.uklad(pos=(X0, 0, Z0))`, więc w kodzie modułów x = u, z = v.

Maski (siatka co 1 st na u −36…970, v −92…92, numpy):
- d_wezel  odległość do najbliższego węzła walki (pętle stref + miejsce Strażnika) — plac walki r 12 ma zostać pusty;
- d_trasa  odległość do pętli potworów (łamane zamknięte; troll też);
- d_sciezka odległość od krawędzi ścieżki (ujemna na ścieżce);
- zajete   miejsca zajęte przez postawione rzeczy (rekwizyty, domy, pnie) — następne omijają je.
Zasada miejsca (`miejsce_ok`): rzecz wyższa niż 1,4 nie wchodzi w plac walki (≥ 12 + promień od węzła), nic poza płaskim
gruntem nie stoi na ścieżce, w otwarciach przejść ani na pętli potworów (rzeczy z kolizją albo wysokie).
"""
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

from swiat.biom_las import geo  # noqa: E402

PLIK_PLANU = os.path.join(REPO, "swiat", "biom_las", "pas", "plan_pasa.json")
KONTENER = "Workspace/LasPas"         # osobny od Workspace/BiomLas (stary las zostaje nietknięty)

# granice wszystkiego, co stawia generator (układ pasa). Od dołu: plan_pasa.json → świat od X0 + u_od − 10 = X 1066
# (Baseplate kończy się na X 1024); w poprzek: polowa_szerokosci_z_tlem = 90. U góry: 24 st „zapowiedzi Bagna” za bramą
# (u 940–964) — osobna grupa ZapowiedzBagna, do usunięcia, gdy powstanie Bagno.
U_MIN, U_MAX = -34.0, 966.0
V_MAX = 88.0
PLAC_R = 12.0                         # plac walki wokół węzła (zasada „plaski_grunt” z swiat/las_potwory)
SZER_SCIEZKI = 8.0
WIDOCZNA_SCIANA = 38.0                # niewidzialna ściana na |v| = 38 (plan: kulisy_opis)
# odcinki ścieżki (u od, u do): przerwa na mostek (sam mostek jest drogą) i na posadzkę kręgu areny (r 27 wokół 880)
ODCINKI_SCIEZKI = ((0.0, 266.0), (290.0, 853.0), (907.0, 960.0))
WODA_U = (273.0, 283.0)               # plan: przejscia → strumyk_z_mostkiem → woda
ROZMIAR_POTWORA = {"Leśny Slime": 2.7, "Muchomornik": 3.6, "Cierniowy Wilk": 7.7, "Leśny Troll": 12.7, "Strażnik Gaju": 8.9}


def wczytaj_plan(plik=PLIK_PLANU):
    with open(plik, encoding="utf-8") as f:
        return json.load(f)


def v_sciezki(u):
    """Oś ścieżki: lekka fala ±2,7 (zero kąta prostego), wygaszona przy mostku, furtce, wejściu do kręgu i bramie Bagna,
    żeby ścieżka trafiała w środek otwarć. Ta sama funkcja steruje budową i kontrolą."""
    t = 1.65 * math.sin(2 * math.pi * u / 83.0 + 0.7) + 1.05 * math.sin(2 * math.pi * u / 151.0 + 2.1)
    a = min(1.0, abs(u - 278.0) / 26.0, abs(u - 70.0) / 18.0, abs(u - 854.0) / 26.0, abs(u - 934.0) / 30.0,
            abs(u - 14.0) / 22.0)
    return t * a


class Pas:
    KROK = 1.0

    def __init__(self, ziarno=7, plik=PLIK_PLANU):
        self.P = P = wczytaj_plan(plik)
        pas = P["pas"]
        self.pol = pas["szerokosc"] / 2.0                       # 36
        self.kulisy = pas["kulisy"]                             # 24
        self.u_od, self.u_do = float(pas["u_od"]), float(pas["u_do"])
        self.X0, self.Z0 = float(P["swiat"]["X0"]), float(P["swiat"]["Z0"])
        self.przegrody = {q["id"]: q for q in P["przegrody"]}
        self.przejscia = {t["id"]: t for t in P["przejscia"]}
        self.miejsca = {m["id"]: m for m in P["miejsca"]}
        self.znaki = {z["id"]: z for z in P["punkty_orientacyjne"]}
        self.strefy = P["strefy"]
        self.straznik = P["straznik"]
        r = random.Random(ziarno)
        for nazwa in ("teren", "sciezka", "woda", "punkty", "przegrody", "przejscia", "domy", "kulisy", "tlo", "detale",
                      "bagno"):
            setattr(self, "rnd_" + nazwa, random.Random(r.randint(0, 10 ** 9)))
        # siatka
        self.us = np.arange(-36.0 + 0.5, 970.0, self.KROK)
        self.vs = np.arange(-92.0 + 0.5, 92.0, self.KROK)
        V, U = np.meshgrid(self.vs, self.us)
        self.U, self.V = U, V
        wezly = [tuple(w) for st in self.strefy for w in st["trasa"]] + [tuple(self.straznik["miejsce"])]
        self.wezly = wezly
        d = np.full(U.shape, 1e9)
        for (wu, wv) in wezly:
            d = np.minimum(d, np.hypot(U - wu, V - wv))
        self.d_wezel = d
        dt = np.full(U.shape, 1e9)
        for st in self.strefy:
            dt = np.minimum(dt, geo.odl_lamana_np(U, V, st["trasa"] + [st["trasa"][0]]))
        self.d_trasa = dt
        ds = np.full(U.shape, 1e9)
        vs_os = np.vectorize(v_sciezki)(self.us)
        for a, b in ODCINKI_SCIEZKI:
            m = (self.us >= a) & (self.us <= b)
            ds[m, :] = np.minimum(ds[m, :], np.abs(V[m, :] - vs_os[m, None]) - SZER_SCIEZKI / 2.0)
        self.d_sciezka = ds
        self.zajete = np.zeros(U.shape, dtype=bool)

    # --- układ i siatka
    def swiat(self, u, y, v):
        return (self.X0 + u, y, self.Z0 + v)

    def _ij(self, u, v):
        i = int((u + 36.0) / self.KROK)
        j = int((v + 92.0) / self.KROK)
        return min(max(i, 0), len(self.us) - 1), min(max(j, 0), len(self.vs) - 1)

    def pole(self, nazwa, u, v):
        i, j = self._ij(u, v)
        return float(getattr(self, nazwa)[i, j])

    def _okno(self, u, v, r):
        i0, j0 = self._ij(u - r, v - r)
        i1, j1 = self._ij(u + r, v + r)
        sub = (self.U[i0:i1 + 1, j0:j1 + 1] - u) ** 2 + (self.V[i0:i1 + 1, j0:j1 + 1] - v) ** 2 <= r * r
        return (slice(i0, i1 + 1), slice(j0, j1 + 1)), sub

    def zajmij(self, u, v, r):
        okno, sub = self._okno(u, v, max(r, 0.5))
        self.zajete[okno] |= sub

    def wolne(self, u, v, r):
        okno, sub = self._okno(u, v, max(r, 0.5))
        return not bool((self.zajete[okno] & sub).any())

    def min_pole(self, nazwa, u, v, r):
        """Najmniejsza wartość pola w kole r (dla dużych rzeczy — sam środek to za mało)."""
        okno, sub = self._okno(u, v, max(r, 0.5))
        w = getattr(self, nazwa)[okno][sub]
        return float(w.min()) if w.size else self.pole(nazwa, u, v)

    # --- gdzie jesteśmy
    def odcinek(self, u):
        """Id przegrody albo przejścia pod u (ściana zamykająca: „sciana”, za bramą: „bagno”)."""
        if u < 0:
            return "sciana"
        for q in list(self.P["przegrody"]) + list(self.P["przejscia"]):
            if q["u_od"] <= u < q["u_do"]:
                return q["id"]
        return "bagno"

    def otwarcie_w(self, u, v, r=0.0):
        """Przejście, w którego otwarcie (u od–do × otwarcie v) wchodzi koło (u, v, r) — albo None."""
        for t in self.P["przejscia"]:
            o1, o2 = t["otwarcie"]
            if t["u_od"] - r < u < t["u_do"] + r and o1 - r < v < o2 + r:
                return t
        return None

    def w_wodzie(self, u, r=0.0):
        return WODA_U[0] - 1.6 - r < u < WODA_U[1] + 1.6 + r

    # --- reguła miejsca dla rzeczy w polu gry
    def miejsce_ok(self, u, v, r, wys, kolizja=False, sciezka_zapas=0.6, pole_gry=True, woda=False, otwarcia=True):
        """Czy rzecz o promieniu r (na ziemi) i wysokości `wys` może stanąć w (u, v)."""
        if not (U_MIN + r <= u <= U_MAX - r) or abs(v) + r > V_MAX:
            return False
        if pole_gry and abs(v) + r > self.pol + 1.5:
            return False
        if wys > 1.4 and self.min_pole("d_wezel", u, v, r) < PLAC_R + 0.6:
            return False
        if wys > 0.45 and self.min_pole("d_sciezka", u, v, r) < sciezka_zapas:
            return False
        if (kolizja or wys > 1.4) and self.min_pole("d_trasa", u, v, r) < 2.5:
            return False
        if otwarcia and wys > 0.45:
            t = self.otwarcie_w(u, v, r)
            if t is not None and wys > t["wys_w_otwarciu"]:
                return False
        if not woda and self.w_wodzie(u, r):
            return False
        return self.wolne(u, v, r)
