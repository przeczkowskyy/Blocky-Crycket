# -*- coding: utf-8 -*-
"""Kontekst generatora Dżungli: plan (plan.py), układ pasa, maski miejsca, oś Dróżki, paleta i zasady na częściach.

Ten sam układ co las-pas i Bagno: u wzdłuż (ciągnie się od początku lasu; Dżungla ma u 1874…2820), v w poprzek, świat
Studio = (1100 + u; y; −700 + v), bez obrotu. Moduły budują w `s.uklad(pos=(X0, 0, Z0))`, więc w kodzie x = u, z = v.
Wszystkie liczby wzdłuż pasa to liczby Bagna (swiat/bagno_pas/kontekst.py) + 940.

Z lasu-pasa bierzemy bez kopiowania klasę `Pas` (maski, `pole`, `zajmij`, `wolne`, `min_pole`, `otwarcie_w`, `odcinek`)
i `Zasady` (plac walki, otwarcia przejść, pętle potworów, przelot kamery). Własne: zakres siatki i pasa (u 1876…2846), oś
Dróżki, strumienie w przejściach, zasada ścieżki/granic w `ZasadyDzungli` oraz zasada „styk z Bagnem”: za bramą Bagna
(u 1874–1906) stoją części Bagna-pasa (skraj kulis, drobiazgi przy Krzywej Kładce, palisada) — generator nie stawia na
nich niczego wyższego niż grunt (grupa ZapowiedzDzungli Bagna się nie liczy: ma zniknąć przed budową Dżungli).
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
from swiat.biom_las.paleta import PALETA as PALETA_LASU  # noqa: E402
from swiat.las_pas.kontekst import PLAC_R, SZER_SCIEZKI, Pas  # noqa: E402
from swiat.las_pas.zasady import GRUNT_MAX, SCIEZKA_Y, SCIEZKA_ZAPAS, V_GRANICA, Zasady, aabb, punkty  # noqa: E402
from swiat.dzungla_pas import plan as plan_dzungli  # noqa: E402

D = plan_dzungli.D                    # 940 — przesunięcie względem Bagna
KONTENER = "Workspace/DzunglaPas"
U_MIN, U_MAX = 936.0 + D, 1906.0 + D  # części Dżungli (Bagno-pas kończy się na u 1906; jego ZapowiedzDzungli do usunięcia)
V_MAX = 88.0
SIATKA_U = (932.0 + D, 1910.0 + D)
SIATKA_V = 92.0
U_PLYTY = (966.0 + D, 1906.0 + D)     # płyta Dżungli styka się z płytą Bagna (u 966…1906)
U_SCIANY = 1905.0 + D                 # niewidzialna ściana na końcu zapowiedzi Pustyni
ODCINKI_SCIEZKI = ((960.0 + D, 1793.0 + D), (1847.0 + D, 1902.0 + D))   # przerwa na okrągłą posadzkę Kręgu (r 27 wokół 2760)
ROWY = ((1006.0 + D, 1014.0 + D), (1211.0 + D, 1225.0 + D))             # woda przejść (plan: przejscia → woda)
WYGASZ = ((954.0 + D, 24.0), (1010.0 + D, 16.0), (1218.0 + D, 22.0), (1428.0 + D, 16.0), (1636.0 + D, 16.0),
          (1752.0 + D, 18.0), (1793.0 + D, 20.0), (1874.0 + D, 26.0))
CZESCI_BAGNA = os.path.join(REPO, "swiat", "bagno_pas", "czesci.json")
U_STYKU = 1912.0                      # do tego u generator i kontrola pilnują styku z częściami Bagna-pasa

# paleta Dżungli: paleta lasu (z miasteczkiem) bez zmian + kolory Dżungli z prefiksem dz_ (nie zderzają się z paletą
# lasu, Bagna ani aren — arena może dołożyć KOLORY_DZUNGLI do swojej palety i pożyczyć rośliny z rosliny.py).
# Grunt, podłoże i droga jak makieta przejścia przez chmury (swiat/teleport_chmury/krainy.json, kraina dzungla:
# 2FA34A / 5C3A22 / B07A44); korony i cienie przyciemnione w stronę areny Dżungli (swiat/areny_walki, 2E7D3A / 3F9A45).
KOLORY_DZUNGLI = {
    "dz_trawa": "2FA34A",           # grunt (makieta krain), łąka wejścia
    "dz_trawa_jasna": "6CCB4A",     # słoneczne polanki Zwijogonów
    "dz_runo": "2E7D3A",            # ciemne runo pod koronami (arena: grunt)
    "dz_runo_jasne": "3F9A45",      # jaśniejsze runo (arena: grunt jasny), polanki Gaju
    "dz_runo_ciemne": "235E2E",     # runo pod kulisami
    "dz_podloze": "5C3A22",         # płyta (makieta: podłoże)
    "dz_droga": "B07A44",           # Dróżka (makieta: droga)
    "dz_droga_ciemna": "8A5C32",    # koleiny i brzegi Dróżki
    "dz_ziemia": "4E3A24",          # wilgotna ziemia Kwietnika
    "dz_grzadka": "6A4428",         # grządki
    "dz_piasek_gaju": "D2AE76",     # piaszczysta ziemia Gaju Kokosów
    "dz_pien": "5C3A22",            # pnie drzew (jak podłoże i futro Siłacza)
    "dz_pien_jasny": "7A5232",
    "dz_palma": "8C6A44",           # pnie palm
    "dz_palma_jasna": "A88658",
    "dz_korona_spod": "236E33",     # spody koron (ciemne — jak arena)
    "dz_korona": "2E8A3E",
    "dz_korona_jasna": "5CAC3F",    # wierzchy koron
    "dz_lisc": "2FA34A",            # olbrzymie liście (plan)
    "dz_lisc_jasny": "6CCB4A",
    "dz_lisc_ciemny": "1F7A36",
    "dz_liana": "3E7D2E",           # liany (arena)
    "dz_bambus": "9DBF4A",
    "dz_bambus_ciemny": "6E8F32",
    "dz_bambus_wezel": "C8D27A",
    "dz_woda": "2EC4B6",            # turkus wody (plan)
    "dz_woda_gleboka": "1C9A92",
    "dz_woda_jasna": "8FE3EC",      # spadająca woda kaskad
    "dz_piana": "EFFCF8",
    "dz_kwiat_czerwony": "E5392B",  # kwiaty (plan)
    "dz_kwiat_zolty": "F2B030",
    "dz_kwiat_rozowy": "FF5FA2",    # świecące kwiaty (arena, Neon)
    "dz_kwiat_jarzacy": "FFD84A",   # świecące środki kwiatów (arena, Neon)
    "dz_owoc": "F08A24",            # pomarańczowe owoce (plan)
    "dz_kokos": "6B4526",
    "dz_kokos_jasny": "9C6B3C",
    "dz_kamien": "8E9A82",          # omszały kamień ruin (arena)
    "dz_kamien_ciemny": "667260",
    "dz_kamien_jasny": "B5BDA3",
    "dz_mech": "5DAA45",            # mech (arena)
    "dz_zloto": "C9A44A",
    "dz_znak": "3FE0D0",            # jarzące się znaki ruin (Neon)
    "dz_oko": "FFD84A",             # oczy posągów (Neon)
    "dz_swiatlo": "D9E27A",         # plamy światła na ziemi (płaskie, bez Neonu)
    "dz_mgla": "8FC79A",            # ciepła zielona mgła (arena: Atmosphere)
    "dz_sylweta_1": "2F6B3A",       # kulisy i tło: trzy rzędy jaśniejące w mgłę (arena)
    "dz_sylweta_2": "568E5E",
    "dz_sylweta_3": "8DB894",
    "dz_piasek": "F2CC7E",          # zapowiedź Pustyni (makieta krain: grunt Pustyni)
    "dz_ochra": "C08A55",           # makieta: podłoże Pustyni
    "dz_droga_pustyni": "D9A85E",   # makieta: droga Pustyni
    "dz_kaktus": "5E8C3A",
    "dz_kosc": "F3E6C8",
}
PALETA = dict(PALETA_LASU)
for _k, _v in KOLORY_DZUNGLI.items():
    assert _k not in PALETA, "klucz Dżungli zderza się z kluczem lasu: " + _k
    PALETA[_k] = _v


def v_sciezki(u):
    """Oś Dróżki: fala ±4 (łagodniejsza niż Krzywa Kładka Bagna, inne okresy), wygaszona przy przybyciu, mostkach,
    zwężeniach, wejściu na posadzkę Kręgu i przy bramie — tam Dróżka trafia w środek otwarć. Ta sama funkcja steruje
    budową i kontrolą."""
    t = 2.7 * math.sin(2 * math.pi * u / 89.0 + 1.1) + 1.3 * math.sin(2 * math.pi * u / 157.0 + 0.3)
    a = 1.0
    for u0, w in WYGASZ:
        a = min(a, abs(u - u0) / w)
    return t * a


def na_sciezce(u):
    return any(a <= u <= b for a, b in ODCINKI_SCIEZKI)


def czesci_bagna(u_od=U_STYKU - 46.0, plik=CZESCI_BAGNA):
    """Skrzynki (min, max) części Bagna-pasa za jego bramą (u ≥ u_od), wyższych niż grunt i widocznych — bez grupy
    ZapowiedzDzungli (do usunięcia przed budową Dżungli). Brak pliku Bagna = pusta lista."""
    if not os.path.isfile(plik):
        return []
    with open(plik, encoding="utf-8") as f:
        d = json.load(f)
    X0 = 1100.0
    wyn = []
    for c in d["czesci"]:
        g = d["grupy"][c[1]]
        if "/ZapowiedzDzungli" in g or c[13] >= 0.98:
            continue
        mn, mx = aabb(c)
        if mx[0] - X0 < u_od or mx[1] <= GRUNT_MAX:
            continue
        wyn.append((mn, mx, c[14], g.split("/", 2)[-1]))
    return wyn


class Dzungla(Pas):
    """`Pas` lasu z planem Dżungli i własną siatką (u 1872…2850). Metody masek (pole, zajmij, wolne, min_pole,
    otwarcie_w, odcinek) dziedziczone bez zmian; nadpisane tylko te, które w lesie mają wpisane liczby lasu."""
    KROK = 1.0

    def __init__(self, ziarno=11, plan=None):                    # noqa: super().__init__ celowo pominięte (stały plik lasu)
        self.P = P = plan or plan_dzungli.zbuduj()
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
                      "mgla", "pustynia", "parasole", "mosty"):
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
        # części Bagna-pasa za jego bramą: zajęte (rzeczy losowe ich omijają; zasada „bagno” pilnuje reszty)
        self.bagno = czesci_bagna()
        for mn, mx, _, _ in self.bagno:
            u0, u1, v0, v1 = mn[0] - self.X0, mx[0] - self.X0, mn[2] - self.Z0, mx[2] - self.Z0
            if u1 < SIATKA_U[0]:
                continue
            self.zajmij((u0 + u1) / 2.0, (v0 + v1) / 2.0, max(0.6, math.hypot(u1 - u0, v1 - v0) / 2.0))

    def _ij(self, u, v):
        i = int((u - SIATKA_U[0]) / self.KROK)
        j = int((v + SIATKA_V) / self.KROK)
        return min(max(i, 0), len(self.us) - 1), min(max(j, 0), len(self.vs) - 1)

    def odcinek(self, u):
        if u < 940.0 + D:
            return "brama_bagna"
        o = Pas.odcinek(self, u)
        return "pustynia" if o == "bagno" else o

    def w_wodzie(self, u, r=0.0):
        """Strumień przejścia (woda w poprzek pasa) — rzeczy w polu gry nie stawiamy w strumieniach."""
        return any(a - 1.0 - r < u < b + 1.0 + r for a, b in ROWY)

    def miejsce_ok(self, u, v, r, wys, kolizja=False, sciezka_zapas=0.6, pole_gry=True, woda=False, otwarcia=True):
        """Jak `Pas.miejsce_ok` lasu, z granicami Dżungli."""
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


class ZasadyDzungli(Zasady):
    """`Zasady` lasu-pasa (plac walki, otwarcia, pętle, przelot — bez zmian) + własne granice, Dróżka i styk z Bagnem."""

    def __init__(self, K):
        super().__init__(K)
        self.odcinki = [(K.X0 + a, K.X0 + b) for a, b in ODCINKI_SCIEZKI]
        self.bagno = [(mn, mx) for mn, mx, _, _ in getattr(K, "bagno", [])]
        self.u_styku = K.X0 + U_STYKU

    def naruszenia(self, c, grupa, tylko=None):
        chce = set(("granice", "plac", "sciezka", "otwarcie", "petla", "kamera", "bagno") if tylko is None else tylko)
        mn, mx = aabb(c)
        if "granice" in chce:
            if mn[0] - self.X0 < U_MIN - 0.05 or mx[0] - self.X0 > U_MAX + 0.05 or abs(mn[2] - self.Z0) > V_GRANICA \
                    or abs(mx[2] - self.Z0) > V_GRANICA:
                return ["granice pasa"]
        reszta = tuple(t for t in ("plac", "otwarcie", "petla", "kamera") if t in chce)
        wyn = Zasady.naruszenia(self, c, grupa, tylko=reszta) if reszta else []
        if "bagno" in chce and self.bagno and mn[0] < self.u_styku and mx[1] > GRUNT_MAX + 1e-6 and c[13] < 0.98:
            for bmn, bmx in self.bagno:
                if np.all(mn < bmx - 0.05) and np.all(bmn < mx - 0.05):
                    wyn.append("styk z Bagnem-pasem")
                    break
        if "sciezka" not in chce or c[13] >= 0.98 or mx[1] <= GRUNT_MAX + 1e-6 or 0.0 < c[13] < 0.98:
            return wyn
        if "/BramaPustyni/" in grupa or c[14].startswith("Most ") or mx[1] < SCIEZKA_Y[0] or mn[1] > SCIEZKA_Y[1]:
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
