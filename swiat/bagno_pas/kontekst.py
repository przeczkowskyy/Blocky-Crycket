# -*- coding: utf-8 -*-
"""Kontekst generatora Bagna: plan (plan.py), układ pasa, maski miejsca, oś Krzywej Kładki i zasady na częściach.

Ten sam układ co las-pas: u wzdłuż (ciągnie się od początku lasu; Bagno ma u 934…1880), v w poprzek, świat Studio =
(1100 + u; y; −700 + v), bez obrotu. Moduły budują w `s.uklad(pos=(X0, 0, Z0))`, więc w kodzie x = u, z = v.

Z lasu-pasa bierzemy bez kopiowania: klasę `Pas` (maski, `pole`, `zajmij`, `wolne`, `min_pole`, `otwarcie_w`, `odcinek`)
i `Zasady` (plac walki, otwarcia przejść, pętle potworów, przelot kamery — liczone na chmurze punktów części). Własne są
tylko rzeczy, które las ma wpisane na stałe: zakres siatki i pasa (u 936…1906), oś ścieżki (Krzywa Kładka), rowy z wodą
w przejściach i zasada ścieżki/granic w `ZasadyBagna` (reszta zasad to `Zasady.naruszenia` lasu).
"""
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
from swiat.biom_las.paleta import PALETA as PALETA_LASU  # noqa: E402
from swiat.las_pas.kontekst import PLAC_R, SZER_SCIEZKI, Pas  # noqa: E402
from swiat.las_pas.zasady import GRUNT_MAX, SCIEZKA_Y, SCIEZKA_ZAPAS, V_GRANICA, Zasady, aabb, punkty  # noqa: E402
from swiat.bagno_pas import plan as plan_bagna  # noqa: E402

KONTENER = "Workspace/BagnoPas"
U_MIN, U_MAX = 936.0, 1906.0          # części Bagna (las-pas kończy się na u 966; ZapowiedzBagna lasu do usunięcia)
V_MAX = 88.0
SIATKA_U = (932.0, 1910.0)
SIATKA_V = 92.0
U_PLYTY = (966.0, 1906.0)             # płyta Bagna styka się z płytą lasu (u −34…966)
U_SCIANY = 1905.0                     # niewidzialna ściana na końcu zapowiedzi Dżungli
ODCINKI_SCIEZKI = ((960.0, 1793.0), (1847.0, 1902.0))   # przerwa na okrągły pomost Topieli (r 27 wokół 1820)
ROWY = ((1006.0, 1014.0), (1211.0, 1225.0))             # woda przejść (plan: przejscia → woda)
WYGASZ = ((954.0, 24.0), (1010.0, 16.0), (1218.0, 22.0), (1428.0, 16.0), (1636.0, 16.0), (1752.0, 18.0),
          (1793.0, 20.0), (1874.0, 26.0))

# paleta Bagna: paleta lasu (z miasteczkiem) bez zmian + kolory Bagna (makieta przejścia przez chmury, swiat/teleport_chmury:
# grunt 7E8C3E, podłoże 4A3F2A, droga 9C7A4A)
KOLORY_BAGNA = {
    "bagno_trawa": "7E8C3E",       # kępy (jak makieta krain)
    "bagno_trawa_jasna": "9DAA52",  # wierzch kęp, place walki Rechotków
    "bagno_mech": "6F7A3A",        # mech na pniach i palach
    "bagno_bloto": "5B4A34",       # błoto Trzęsawiska
    "bagno_bloto_jasne": "7A6446",  # udeptane błoto pod Bulgotnikami
    "bagno_podloze": "4A3F2A",     # płyta pod kulisami (makieta)
    "bagno_woda": "4E6E5E",        # płytka, herbaciano-zielona woda
    "bagno_ton": "2E4A44",         # ciemna toń (Kępy, Topiel)
    "bagno_rzesa": "8FB548",       # rzęsa na wodzie
    "bagno_deska": "9C7A4A",       # deski Krzywej Kładki (makieta: droga)
    "bagno_deska_ciemna": "6E5434",
    "bagno_kora": "6B5A44",        # pnie cypryśników
    "bagno_suche": "8C857A",       # martwe drewno
    "bagno_korona": "556B2F",      # korony cypryśników
    "bagno_korona_jasna": "7A8C3A",
    "bagno_wierzba": "8EA65A",     # zwisy wierzb
    "bagno_trzcina": "B59A52",     # trzcina, strzecha
    "bagno_palka": "6E4A2E",       # kolby pałek
    "bagno_kwiat": "8C5A9E",       # fioletowe kwiaty bagienne
    "bagno_mgla": "D8E2CF",        # niska mgła
    "bagno_broda": "A9B48E",       # „broda” mchu zwisająca z cypryśników (jasna, żeby czytała się na koronie)
    "neon_ognik": "C8E05A",        # błędne ogniki, latarnie Topieli (Neon)
    "bagno_sylweta_1": "47573A",   # kulisy i tło: trzy rzędy jaśniejące w mgłę
    "bagno_sylweta_2": "71806A",
    "bagno_sylweta_3": "A3AE9C",
    "dzungla_lisc": "2FA34A",      # zapowiedź Dżungli za bramą
    "dzungla_lisc_jasny": "6CCB4A",
}
PALETA = dict(PALETA_LASU)
for _k, _v in KOLORY_BAGNA.items():
    assert _k not in PALETA, "klucz Bagna zderza się z kluczem lasu: " + _k
    PALETA[_k] = _v


def v_sciezki(u):
    """Oś Krzywej Kładki: fala ±4,8 (mocniejsza niż w lesie), wygaszona przy przybyciu, kładkach przejść, zwężeniach,
    wejściu na pomost Topieli i przy bramie — tam kładka trafia w środek otwarć. Ta sama funkcja steruje budową i kontrolą."""
    t = 3.2 * math.sin(2 * math.pi * u / 97.0 + 0.4) + 1.6 * math.sin(2 * math.pi * u / 173.0 + 1.9)
    a = 1.0
    for u0, w in WYGASZ:
        a = min(a, abs(u - u0) / w)
    return t * a


def na_sciezce(u):
    return any(a <= u <= b for a, b in ODCINKI_SCIEZKI)


class Bagno(Pas):
    """`Pas` lasu z planem Bagna i własną siatką (u 932…1910). Metody masek (pole, zajmij, wolne, min_pole, otwarcie_w,
    odcinek) dziedziczone bez zmian; nadpisane tylko te, które w lesie mają wpisane liczby lasu."""
    KROK = 1.0

    def __init__(self, ziarno=11, plan=None):                    # noqa: super().__init__ celowo pominięte (stały plik lasu)
        self.P = P = plan or plan_bagna.zbuduj()
        pas = P["pas"]
        self.pol = pas["szerokosc"] / 2.0
        self.kulisy = pas["kulisy"]
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
                      "mgla", "dzungla"):
            setattr(self, "rnd_" + nazwa, random.Random(r.randint(0, 10 ** 9)))
        self.us = np.arange(SIATKA_U[0] + 0.5, SIATKA_U[1], self.KROK)
        self.vs = np.arange(-SIATKA_V + 0.5, SIATKA_V, self.KROK)
        V, U = np.meshgrid(self.vs, self.us)
        self.U, self.V = U, V
        self.wezly = [tuple(w) for st in self.strefy for w in st["trasa"]] + [tuple(self.straznik["miejsce"])]
        d = np.full(U.shape, 1e9)
        for (wu, wv) in self.wezly:
            d = np.minimum(d, np.hypot(U - wu, V - wv))
        self.d_wezel = d
        dt = np.full(U.shape, 1e9)
        for st in self.strefy:
            dt = np.minimum(dt, geo.odl_lamana_np(U, V, st["trasa"] + [st["trasa"][0]]))
        self.d_trasa = dt
        ds = np.full(U.shape, 1e9)
        os_v = np.vectorize(v_sciezki)(self.us)
        for a, b in ODCINKI_SCIEZKI:
            m = (self.us >= a) & (self.us <= b)
            ds[m, :] = np.minimum(ds[m, :], np.abs(V[m, :] - os_v[m, None]) - SZER_SCIEZKI / 2.0)
        self.d_sciezka = ds
        self.zajete = np.zeros(U.shape, dtype=bool)

    def _ij(self, u, v):
        i = int((u - SIATKA_U[0]) / self.KROK)
        j = int((v + SIATKA_V) / self.KROK)
        return min(max(i, 0), len(self.us) - 1), min(max(j, 0), len(self.vs) - 1)

    def odcinek(self, u):
        if u < 940.0:
            return "brama_lasu"
        o = Pas.odcinek(self, u)
        return "dzungla" if o == "bagno" else o

    def w_wodzie(self, u, r=0.0):
        """Rów przejścia (woda w poprzek pasa) — rzeczy w polu gry nie stawiamy w rowach."""
        return any(a - 1.0 - r < u < b + 1.0 + r for a, b in ROWY)

    def miejsce_ok(self, u, v, r, wys, kolizja=False, sciezka_zapas=0.6, pole_gry=True, woda=False, otwarcia=True):
        """Jak `Pas.miejsce_ok` lasu, z granicami Bagna."""
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


class ZasadyBagna(Zasady):
    """`Zasady` lasu-pasa (plac walki, otwarcia, pętle, przelot — bez zmian) + własne granice i ścieżka Bagna."""

    def __init__(self, K):
        super().__init__(K)
        self.odcinki = [(K.X0 + a, K.X0 + b) for a, b in ODCINKI_SCIEZKI]

    def naruszenia(self, c, grupa, tylko=None):
        chce = set(("granice", "plac", "sciezka", "otwarcie", "petla", "kamera") if tylko is None else tylko)
        mn, mx = aabb(c)
        if "granice" in chce:
            if mn[0] - self.X0 < U_MIN - 0.05 or mx[0] - self.X0 > U_MAX + 0.05 or abs(mn[2] - self.Z0) > V_GRANICA \
                    or abs(mx[2] - self.Z0) > V_GRANICA:
                return ["granice pasa"]
        reszta = tuple(t for t in ("plac", "otwarcie", "petla", "kamera") if t in chce)
        wyn = Zasady.naruszenia(self, c, grupa, tylko=reszta) if reszta else []
        if "sciezka" not in chce or c[13] >= 0.98 or mx[1] <= GRUNT_MAX + 1e-6 or 0.0 < c[13] < 0.98:
            return wyn
        if "/BramaDzungli/" in grupa or c[14].startswith("Most ") or mx[1] < SCIEZKA_Y[0] or mn[1] > SCIEZKA_Y[1]:
            return wyn
        for a, b in self.odcinki:
            if mx[0] < a or mn[0] > b:
                continue
            Q = punkty(c)
            Q = Q[(Q[:, 1] >= SCIEZKA_Y[0]) & (Q[:, 1] <= SCIEZKA_Y[1]) & (Q[:, 0] >= a) & (Q[:, 0] <= b)]
            if not len(Q):
                continue
            os_ = np.array([v_sciezki(x - self.X0) for x in Q[:, 0]]) + self.Z0
            if np.any(np.abs(Q[:, 2] - os_) < SZER_SCIEZKI / 2.0 + SCIEZKA_ZAPAS):
                wyn.append("ścieżka (u ≈ %.0f)" % (float(np.median(Q[:, 0])) - self.X0))
                break
        return wyn
