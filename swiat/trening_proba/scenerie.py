#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator scenerii mini-gier Training Center (D-108): każda gra w innym otoczeniu w stylu krain → scenerie.json.

    python -B swiat/trening_proba/scenerie.py             # generuje scenerie.json, wypisuje liczby i pominięte rekwizyty
    python -B swiat/trening_proba/scenerie.py --sprawdz   # kod 1, gdy scenerie.json jest nieaktualny
    python -B swiat/trening_proba/scenerie.py --raport    # tylko liczby (bez zapisu)

Sześć scenerii w jednym pasie (ustawienia.json → „scenerie”), po dwie na krainę:
    Łąka pod dębem (Szczęście) i Polana drwali (Siła) — Las; Grobla przez Bagno (Kondycja) i Pomost nad topielą
    (Zręczność) — Bagno; Krąg strażnika (Pancerz) i Świątynia run (Inteligencja) — Dżungla.
Styl i klocki są z map krain — rodziny roślin, skał i budowli tylko IMPORTUJEMY (bez zmian w tamtych pakietach):
swiat/biom_las (drzewa, krzaki, grzyby, skały, detale), swiat/bagno_pas (cypryśniki, wierzby, trzciny, grzybienie),
swiat/dzungla_pas (drzewa, palmy, olbrzymie liście, bambus), swiat/areny_walki/rekwizyty.py (chata na palach, wieża,
łódka, brama ruin, posąg, świątynia, wodospad, olbrzymi pień — i wspólna paleta). Własne są tylko proste rzeczy,
których tam nie ma: wał kulis, łaty gruntu, kładki, dynie, posadzka kręgu.

Każdy rekwizyt przechodzi przed postawieniem kontrolę wolnej przestrzeni gry (dekoracje.Straznik: pole gry, promienie
oko kamery → pole gry i postać, przedpole kadrów wszystkich ujęć) — rekwizyt, który ją łamie, jest pomijany i wypisany.
Wynik (części w układzie areny, bez kolizji) czyta scena.py; zmiana ustawień stanowisk albo rodzin w mapach krain
wymaga ponownego uruchomienia generatora (pilnuje tego --sprawdz i test 4k).
"""
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

from swiat.biblioteka.scena import Scena, ku_srodkowi, macierz_obrotu  # noqa: E402
from swiat.areny_walki import rekwizyty as R  # noqa: E402  (rodziny aren walki i wspólna paleta krain — tylko import)
from swiat.biom_las import detale as DT  # noqa: E402
from swiat.biom_las import rosliny as RL  # noqa: E402
from swiat.biom_las import skaly as SK  # noqa: E402
from swiat.bagno_pas import rosliny as RB  # noqa: E402
from swiat.dzungla_pas import rosliny as RD  # noqa: E402
import dane as DANE  # noqa: E402
import dekoracje as DEK  # noqa: E402
import scena as SCENA  # noqa: E402

PLIK = SCENA.PLIK_SCENERII
KSZTALT = {0: "B", 1: "K", 2: "C", 3: "W", 4: "N"}
ZIARNO = {"szczescie": 11, "sila": 23, "kondycja": 37, "zrecznosc": 41, "pancerz": 53, "inteligencja": 67}
GRUPA = {"sila": "Sila", "pancerz": "Pancerz", "kondycja": "Kondycja", "zrecznosc": "Zrecznosc", "inteligencja": "Inteligencja",
         "szczescie": "Szczescie"}
PALETA = dict(R.PALETA)
PALETA.update({
    "tr_dynia": "F08A24", "tr_dynia_ciemna": "D9701A", "tr_ogonek": "3F8F35",
    "tr_wal_las": "2F6E35", "tr_wal_las_2": "3F7F4A", "tr_wal_bagno": "47573A", "tr_wal_bagno_2": "556B2F",
    "tr_wal_dzungla": "235E2E", "tr_wal_dzungla_2": "236E33",
    "tr_laka": "6FB546", "tr_laka_jasna": "8FC04A", "tr_sciezka": "B98A5A",
})
# tło krainy: wał (dwa odcienie), dalekie sylwety, łaty gruntu
TLO = {
    "las": {"wal": ("tr_wal_las", "tr_wal_las_2"), "sylweta": ("sylweta_2", "sylweta_3"), "laty": ("tr_laka", "runo_boru", "tr_laka_jasna")},
    "bagno": {"wal": ("tr_wal_bagno", "tr_wal_bagno_2"), "sylweta": ("bagno_sylweta_2", "bagno_sylweta_3"),
              "laty": ("bagno_ton", "bagno_rzesa", "bagno_ton")},
    "dzungla": {"wal": ("tr_wal_dzungla", "tr_wal_dzungla_2"), "sylweta": ("dzungla_sylweta_2", "dzungla_sylweta_3"),
                "laty": ("dz_runo_jasne", "dz_runo_ciemne", "dz_swiatlo")},
}


# ------------------------------------------------------------------------------------------------ własne proste rodziny
def wal(s, rnd, p1, p2, wys, kolory, gl=5.0, n=5, y0=-0.5, czuby=True):
    """Wał kulis — ciemna ściana zieleni od p1 do p2 (x, z): n bloków zachodzących na siebie, różne wysokości, lekko
    skręcone; co drugi z węższym, jaśniejszym czubem (linia koron zamiast muru). Bez cienia."""
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    dl = math.hypot(dx, dz)
    ry = math.degrees(math.atan2(-dz, dx))
    with s.cechy(kolizja=False, cien=False):
        for i in range(n):
            t = (i + 0.5) / n
            h = wys * rnd.uniform(0.88, 1.12)
            x, z = p1[0] + dx * t, p1[1] + dz * t
            s.blok("Wał kulis", (x, y0 + h / 2.0, z), (dl / n * 1.14, h, gl * rnd.uniform(0.9, 1.1)), kolory[i % 2],
                   rot=(0, ry + rnd.uniform(-3, 3), 0))
            if czuby and i % 2 == 0:
                s.blok("Wał czub", (x + rnd.uniform(-1.5, 1.5), y0 + h + 1.2, z), (dl / n * 0.55, 3.4, gl * 0.7), kolory[1],
                       rot=(0, ry + rnd.uniform(-8, 8), rnd.uniform(-4, 4)))


def lata(s, rnd, pos, r, kolor, gr=0.08):
    """Płaska łata gruntu (trawa, mech, błoto, plama światła): krążek tuż nad podłożem. 1 część."""
    with s.cechy(kolizja=False, cien=False):
        s.walec("Łata", (pos[0], pos[1] + gr / 2.0 + 0.01, pos[2]), r, gr, kolor, os="y")


def pas_gruntu(s, rnd, p1, p2, szer, kolor, y=0.02, gr=0.08, mat="SmoothPlastic"):
    """Płaski pas na ziemi (ścieżka, posadzka) od p1 do p2 (x, z). 1 część."""
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    with s.cechy(kolizja=False, cien=False):
        s.blok("Pas gruntu", ((p1[0] + p2[0]) / 2.0, y + gr / 2.0, (p1[1] + p2[1]) / 2.0), (math.hypot(dx, dz), gr, szer), kolor, mat,
               rot=(0, math.degrees(math.atan2(-dz, dx)), 0))


def dynia(s, rnd, pos, k=1.0):
    """Dynia: spłaszczona kula i zielony ogonek. 2 części."""
    x, y, z = pos
    d = 1.5 * k
    with s.cechy(kolizja=False):
        s.kula("Dynia", (x, y + d * 0.45, z), d, rnd.choice(("tr_dynia", "tr_dynia", "tr_dynia_ciemna")))
        s.blok("Dynia ogonek", (x, y + d * 0.95, z), (0.3 * k, 0.45 * k, 0.3 * k), "tr_ogonek", rot=(rnd.uniform(-12, 12), 0, rnd.uniform(-12, 12)))


def pien_z_dynia(s, rnd, pos, k=1.0, ry=0.0):
    """Pniak z dynią na wierzchu (cele ciosów drwali — tło Polany). 4 części."""
    RL.pniak(s, rnd, pos, k, ry)
    dynia(s, rnd, (pos[0], pos[1] + 2.0 * k, pos[2]), 0.85 * k)


def kladka(s, rnd, p1, p2, szer=4.4, gora=0.2, woda=-1.3, pale=3, kolor="bagno_deska"):
    """Kładka z desek nad wodą od p1 do p2 (x, z), płaska (wierzch ≤ próg płaskości): pomost, dwie ciemne belki
    brzegowe i pary pali schowanych pod deskami. 3 + 2·pale części."""
    dx, dz = p2[0] - p1[0], p2[1] - p1[1]
    dl = math.hypot(dx, dz)
    ry = math.degrees(math.atan2(-dz, dx))
    sx, sz = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
    with s.uklad(pos=(sx, 0, sz), obrot=(0, ry, 0)), s.cechy(kolizja=False, cien=False):
        s.blok("Kładka deski", (0, gora - 0.2, 0), (dl, 0.4, szer), kolor, "WoodPlanks")
        for zn in (-1, 1):
            s.blok("Kładka belka", (0, gora - 0.16, zn * (szer / 2.0 + 0.15)), (dl, 0.4, 0.5), "bagno_deska_ciemna", "Wood")
        for i in range(pale):
            x = -dl / 2.0 + dl * (i + 0.5) / pale
            for zn in (-1, 1):
                s.walec("Kładka pal", (x, (woda - 1.0 + gora - 0.05) / 2.0, zn * (szer / 2.0 - 0.3)), 0.4, gora - 0.05 - (woda - 1.0),
                        "bagno_kora", "Wood", os="y")


def posadzka_kregu(s, rnd, pos, r):
    """Kamienna posadzka kręgu: dwa współśrodkowe krążki, cztery płyty-promienie i łaty mchu — wszystko płaskie."""
    x, _, z = pos
    with s.cechy(kolizja=False, cien=False):
        s.walec("Posadzka kręgu", (x, 0.04, z), r, 0.06, "dz_kamien_ciemny", "Slate", os="y")
        s.walec("Posadzka kręgu", (x, 0.07, z), r * 0.8, 0.08, "dz_kamien", "Slate", os="y")
        for i in range(4):
            a = math.radians(45 + 90 * i)
            s.blok("Posadzka płyta", (x + math.cos(a) * r * 0.9, 0.09, z + math.sin(a) * r * 0.9), (r * 0.22, 0.1, 1.6), "dz_kamien_jasny",
                   "Slate", rot=(0, -math.degrees(a), 0))
        for i in range(5):
            a = rnd.uniform(0, 2 * math.pi)
            rr = r * rnd.uniform(0.35, 0.95)
            s.walec("Posadzka mech", (x + math.cos(a) * rr, 0.13, z + math.sin(a) * rr), rnd.uniform(0.8, 1.6), 0.06, "dz_mech", os="y")


def sylweta(s, rnd, kraina, pos, k, kolor):
    """Daleka sylweta drzewa w barwie mgły krainy (2–3 części, bez cienia)."""
    if kraina == "las":
        with s.cechy(kolizja=False, cien=False):
            RL.kulisa(s, rnd, pos, k, rnd.uniform(0, 360), kolor, R.mieszaj(s, kolor, "drewno_ciemne", 0.35))
    elif kraina == "bagno":
        R.sylweta_cyprysu(s, rnd, pos, k, kolor)
    else:
        R.korona_daleka(s, rnd, pos, k, kolor)


# ------------------------------------------------------------------------------------------------ budowa
def katy_xyz(rx, ry, rz):
    """Obrót biblioteki map (radiany, R = Ry·Rx·Rz jak CFrame.fromOrientation) → stopnie dla części treningu
    (CFrame.Angles(rx, ry, rz) = Rx·Ry·Rz, jak scena.macierz)."""
    M = macierz_obrotu(math.degrees(rx), math.degrees(ry), math.degrees(rz))
    sb = max(-1.0, min(1.0, M[0][2]))
    b = math.asin(sb)
    if abs(sb) > 0.999999:
        a, c = math.atan2(M[2][1], M[1][1]), 0.0
    else:
        a, c = math.atan2(-M[1][2], M[2][2]), math.atan2(-M[0][1], M[0][0])
    return [round(math.degrees(v), 2) for v in (a, b, c)]


def czesc_z_wiersza(s, w, r, przes):
    """Wiersz biblioteki map → część treningu (położenie przesunięte o `przes`)."""
    ks, _g, x, y, z, rx, ry, rz, sx, sy, sz, kolor, m, alfa, nazwa = w[:15]
    flagi = w[15] if len(w) > 15 else 0
    d = {"n": nazwa, "r": r, "k": KSZTALT[ks], "p": [round(x + przes[0], 3), round(y + przes[1], 3), round(z + przes[2], 3)],
         "s": [max(sx, 0.05), max(sy, 0.05), max(sz, 0.05)], "c": kolor, "m": s.materialy[m]}
    o = katy_xyz(rx, ry, rz)
    if any(abs(v) > 0.01 for v in o):
        d["o"] = o
    if alfa:
        d["t"] = alfa
    if flagi & 2:
        d["bc"] = True
    return d


class Bud:
    """Budowa jednej scenerii w układzie stanowiska (podest = (0, 0, 0), x na wschód, z na południe — ku kamerom)."""

    def __init__(self, D, K, gra, np):
        A = K["arena"]
        self.gra, self.kraina = gra, K["scenerie"][gra]["kraina"]
        self.pd = K["stanowiska"][gra]["podest"]
        self.c0 = A["srodek"]
        self.pol = A["komorka"] / 2.0
        self.zn, self.zs = float(A["polnoc"]), float(A["poludnie"])
        self.woda = A["woda_y"]
        self.y = self.woda if self.kraina == "bagno" else 0.0
        self.s = Scena("A", paleta=PALETA)
        self.rnd = random.Random(ZIARNO[gra])
        self.straz = DEK.Straznik(D, gra, np)
        self.prog = self.c0[1] + DEK.PLASKIE
        self.grupy = []
        self.pominiete = []
        self.zajete = []  # (x, z, promień) — miejsca dużych rekwizytów, które omijają rzędy kulis
        kol = K["scenerie"]["kolejnosc"]
        self.pierwsza, self.ostatnia = gra == kol[0], gra == kol[-1]

    def _swiat(self):
        return [self.c0[i] + self.pd[i] for i in range(3)]

    def p(self, grupa, fn, *a, **kw):
        """Stawia rekwizyt rodziny fn(s, rnd, …) w grupie; gdy łamie wolną przestrzeń gry — cofa go i zapisuje powód.
        zajmij=(x, z, r) rezerwuje miejsce przed rzędami kulis."""
        zajmij = kw.pop("zajmij", None)
        n0 = len(self.s.czesci)
        fn(self.s, self.rnd, *a, **kw)
        nowe = self.s.czesci[n0:]
        przes = self._swiat()
        pudla = []
        for w in nowe:
            c = czesc_z_wiersza(self.s, w, grupa, przes)
            if c.get("t", 0) >= 0.95:
                continue
            mn, mx = DEK._pudlo(c)
            if mx[1] > self.prog + 1e-6:
                pudla.append((c["n"], mn, mx))
        u = self.straz.zle(pudla)
        if u:
            del self.s.czesci[n0:]
            self.pominiete.append("%s/%s: %s" % (grupa, getattr(fn, "__name__", "?"), u[0]))
            return False
        self.grupy += [grupa] * len(nowe)
        if zajmij:
            self.zajete.append(zajmij)
        return True

    def wolne(self, x, z, r):
        return all(math.hypot(x - a, z - b) >= r + c for a, b, c in self.zajete)

    def czesci(self):
        """Części scenerii w układzie ARENY (bez środka areny), z nazwami bez powtórzeń w grupie."""
        wynik, licznik = [], {}
        korzen = "Arena/Dekoracje/" + GRUPA[self.gra]
        for w, g in zip(self.s.czesci, self.grupy):
            c = czesc_z_wiersza(self.s, w, korzen + "/" + g, self.pd)
            k = (c["r"], c["n"])
            licznik[k] = licznik.get(k, 0) + 1
            if licznik[k] > 1:
                c["n"] = "%s %d" % (c["n"], licznik[k])
            wynik.append(c)
        return wynik


# rzędy drzew kulis: (rodzina, skala, dodatkowe argumenty) — po kolei, z przesunięciem losowym
def _dz(s, rnd, pos, k, ry):
    RD.drzewo_dzungli(s, rnd, pos, k, ry, 1.0, tusz=False)


def _palma(s, rnd, pos, k, ry):
    RD.palma(s, rnd, pos, k, ry, 1.0, proste=True)


def _figowiec(s, rnd, pos, k, ry):
    RD.figowiec(s, rnd, pos, k, ry)


def _paproc_drz(s, rnd, pos, k, ry):
    RD.paproc_drzewiasta(s, rnd, pos, k, ry)


DRZEWA = {
    "las": [(RL.dab, 1.1), (RL.smukly, 1.0), (RL.okraglak, 1.3), (RL.swierk, 1.05), (RL.dab, 0.95), (RL.sosna, 1.15), (RL.brzozka, 1.25)],
    "bagno": [(RB.cyprys, 1.1), (RB.wierzba, 1.45), (RB.cyprys, 1.25), (RB.korzeniak, 1.3), (RB.suchy_omszaly, 1.25), (RB.cyprys, 0.95)],
    "dzungla": [(_dz, 0.95), (_palma, 1.2), (_figowiec, 1.1), (_dz, 1.1), (_paproc_drz, 1.5), (_palma, 1.05), (_figowiec, 0.95)],
}


def _niskie(b, x, z):
    """Niska roślina przed rzędem kulis (krzak, paproć, trzcina, olbrzymi liść) — wg krainy."""
    rnd = b.rnd
    p = (x, b.y, z)
    if b.kraina == "las":
        w = rnd.choice(("krzak", "krzak", "paproc", "jezyna", "kwiaty"))
        if w == "krzak":
            return b.p("Runo", RL.krzak, p, rnd.uniform(0.9, 1.4), jagoda=rnd.choice((None, None, "czerwien")))
        if w == "paproc":
            return b.p("Runo", RL.paproc, p, rnd.uniform(1.0, 1.5))
        if w == "jezyna":
            return b.p("Runo", RL.jezyna, p, rnd.uniform(0.9, 1.2))
        return b.p("Runo", RL.kwiaty, p, rnd.choice((("zloto", "biel"), ("czerwien", "zloto"), ("biel", "dach_sklep"))))
    if b.kraina == "bagno":
        w = rnd.choice(("trzcina", "trzcina_niska", "trzcina_niska", "kepa"))
        if w == "trzcina":
            return b.p("Szuwary", R.trzcina_zdzbla, p, rnd.uniform(4.6, 6.2), 3.4, True)
        if w == "trzcina_niska":
            return b.p("Szuwary", R.trzcina_zdzbla, p, rnd.uniform(2.6, 3.6), 2.6, False)
        return b.p("Szuwary", R.kepa, p, rnd.uniform(2.2, 3.4), rnd.uniform(0.9, 1.4), b.woda)
    w = rnd.choice(("krzew", "krzew", "paproc", "parasol", "kepa_parasoli"))
    if w == "krzew":
        return b.p("Poszycie", RD.krzew_dzungli, p, rnd.uniform(1.0, 1.5), rnd.choice((None, "dz_kwiat_czerwony", "dz_kwiat_zolty")))
    if w == "paproc":
        return b.p("Poszycie", RD.paproc, p, rnd.uniform(1.0, 1.5))
    if w == "parasol":
        return b.p("Poszycie", RD.lisc_parasol, p, rnd.uniform(0.9, 1.2), rnd.uniform(0, 360))
    return b.p("Poszycie", RD.kepa_parasoli, p, rnd.uniform(0.8, 1.0), rnd.uniform(0, 360))


def kulisy(b):
    """Zamknięcie scenerii: wał zieleni (północ, zachód, południe; wschód tylko w ostatniej komórce — dalej stoi wał
    sąsiada), rząd drzew krainy od północy i zachodu, kilka od wschodu, dalekie sylwety za wałem i niskie rośliny przed
    rzędem. Miejsca zajęte przez duże rekwizyty (b.zajete) rzędy omijają."""
    rnd, kr, y, P = b.rnd, b.kraina, b.y, b.pol
    T = TLO[kr]
    zw = b.zn + 15.0   # oś wału północnego
    # --- wał
    b.p("Kulisy", wal, (-P - 0.5, zw), (P + 0.5, zw), 12.0, T["wal"], 6.0, 5, y - 0.5)
    b.p("Kulisy", wal, (-P + 1.5, zw - 2), (-P + 1.5, b.zs - 1.5), 10.5, T["wal"], 4.0, 6, y - 0.5)
    b.p("Kulisy", wal, (-P - 0.5, b.zs - 2.5), (P + 0.5, b.zs - 2.5), 8.0, T["wal"], 3.5, 5, y - 0.5, False)
    if b.ostatnia:
        b.p("Kulisy", wal, (P - 1.5, zw - 2), (P - 1.5, b.zs - 1.5), 10.5, T["wal"], 4.0, 6, y - 0.5)
    # --- dalekie sylwety za wałem północnym (i za zachodnim w pierwszej komórce, wschodnim w ostatniej)
    for i in range(6):
        x = -P + 6 + i * (2 * P - 12) / 5.0 + rnd.uniform(-2, 2)
        b.p("Tlo", sylweta, kr, (x, y, zw - 7.5 + rnd.uniform(-1, 1)), rnd.uniform(1.25, 1.6), T["sylweta"][i % 2])
    if b.pierwsza or b.ostatnia:
        zn = -1 if b.pierwsza else 1
        for i in range(4):
            b.p("Tlo", sylweta, kr, (zn * (P + 1.5), y, -34 + i * 16 + rnd.uniform(-2, 2)), rnd.uniform(1.1, 1.4), T["sylweta"][i % 2])
    for i in range(4):  # południe (za plecami kamer): same sylwety przed wałem
        b.p("Tlo", sylweta, kr, (-P + 9 + i * (2 * P - 18) / 3.0 + rnd.uniform(-2, 2), y, b.zs - 7.5), rnd.uniform(0.75, 0.95), T["wal"][1])
    # --- rzędy drzew
    D = DRZEWA[kr]

    def drzewo(i, x, z, r=4.5, k=1.0):
        if not b.wolne(x, z, r):
            return False
        fn, skala = D[i % len(D)]
        return b.p("Drzewa", fn, (x, y, z), skala * k * rnd.uniform(0.92, 1.08), rnd.uniform(0, 360))
    for i in range(7):   # północ
        drzewo(i, -P + 5 + i * (2 * P - 10) / 6.0 + rnd.uniform(-1.5, 1.5), zw + 8.5 + rnd.uniform(-2.5, 2.5))
    for i in range(4):   # północ, drugi rząd (mniejsze, bliżej)
        drzewo(i + 3, -P + 11 + i * (2 * P - 22) / 3.0 + rnd.uniform(-2, 2), zw + 15.5 + rnd.uniform(-1.5, 1.5), 4.0, 0.72)
    for i in range(6):   # zachód
        drzewo(i + 2, -P + 7.5 + rnd.uniform(-1.5, 2.0), zw + 17 + i * 9.5 + rnd.uniform(-1.5, 1.5))
    for i in range(4):   # wschód (widać go w zbliżeniach po rundzie)
        drzewo(i + 5, P - 6.5 + rnd.uniform(-1.5, 1.5), zw + 12 + i * 12.5 + rnd.uniform(-2, 2), 4.5, 0.9)
    # --- niskie rośliny przed rzędami
    for i in range(8):
        _niskie(b, -P + 8 + i * (2 * P - 16) / 7.0 + rnd.uniform(-2, 2), zw + 20.5 + rnd.uniform(-2, 2))
    for i in range(5):
        _niskie(b, -P + 12.5 + rnd.uniform(-1.5, 1.5), zw + 26 + i * 8 + rnd.uniform(-2, 2))
    for i in range(3):
        _niskie(b, P - 11 + rnd.uniform(-1.5, 1.5), zw + 22 + i * 11 + rnd.uniform(-2, 2))
    # --- łaty gruntu (płaskie): jaśniejsze i ciemniejsze plamy, żeby podłoże nie było jedną barwą
    for i in range(12):
        x, z = rnd.uniform(-P + 3, P - 3), rnd.uniform(zw + 4, b.zs - 5)
        b.p("Grunt", lata, (x, y, z), rnd.uniform(2.5, 6.0), T["laty"][i % 3])


# ------------------------------------------------------------------------------------------------ sześć scenerii
def _ku(x, z, cel=(0.0, -6.0)):
    return ku_srodkowi(x, z, cel)


def szczescie(b):
    """Łąka pod dębem (Las): kwietna łąka wokół starego dębu, z którego spadają koniczyny; płotek, ule kwiatów, grzyby."""
    rnd = b.rnd
    for x, z, r in ((0, -4, 13.5), (-12, -16, 6), (13, -14, 7), (2, -24, 8)):
        b.p("Grunt", lata, (x, 0, z), r, "tr_laka_jasna")
    b.p("Grunt", pas_gruntu, (0, 6), (0, 30), 3.2, "tr_sciezka")
    for x, z, ry in ((-13, -20, 8), (12.5, -21.5, -6)):
        b.p("Lakowe", DT.plotek, (x, 0, z), ry)
    for x, z in ((-8, -17), (7.5, -18), (-17, -9), (17, -4), (-3, -22), (4, -15), (-13, -3), (14, -11), (-9, 9), (11, 6)):
        b.p("Lakowe", RL.kwiaty, (x, 0, z), rnd.choice((("zloto", "biel"), ("czerwien", "zloto"), ("biel", "dach_sklep"))))
    for x, z in ((-6, -12), (6.5, -12.5), (-11, -12), (16, -17), (-18, -15)):
        b.p("Lakowe", DT.lan_kwiatow, (x, 0, z), rnd.choice((("zloto", "biel"), ("czerwien", "biel"))))
    b.p("Lakowe", R.wysepka_lasu, (-19, 0, -21), 1.0, 30, zajmij=(-19, -21, 4))
    b.p("Lakowe", R.wysepka_lasu, (20, 0, -22), 1.0, 200, zajmij=(20, -22, 4))
    b.p("Lakowe", RL.grzyb, (-23, 0, -12), 0.55, 20, "czerwien", True, "biel", zajmij=(-23, -12, 3))
    b.p("Lakowe", RL.grzyb, (-21, 0, -8.5), 0.34, 120, "czerwien", True, "biel")
    b.p("Lakowe", SK.glaz, (18, 0, -9), 0.9, 40, "kamien_cieply", "SmoothPlastic", True, False)
    b.p("Lakowe", DT.stos_drewna, (15.5, 0, -6.5), 20)
    b.p("Lakowe", RL.krzak, (-15.5, 0, -6), 1.2)
    b.p("Lakowe", RL.krzak, (21, 0, -15), 1.3, jagoda="czerwien")
    b.p("Swiatlo", R.promien_swiatla, (-14, 0, -24), 26.0, 3.5, 20, 16)
    b.p("Swiatlo", R.promien_swiatla, (15, 0, -26), 24.0, 3.0, -30, 14)
    kulisy(b)


def sila(b):
    """Polana drwali (Las): pniaki z dyniami, stosy kłód, olbrzymi stary pień na skraju, grzyby i paprocie."""
    rnd = b.rnd
    for x, z, r in ((0, -6, 12.5), (10, -16, 7), (-10, -17, 6.5), (0, 8, 6)):
        b.p("Grunt", lata, (x, 0, z), r, "arena_ziemia" if r > 10 else "arena_ziemia_jasna")
    b.p("Grunt", pas_gruntu, (0, 6), (0, 30), 3.4, "arena_ziemia_jasna")
    b.p("Olbrzym", R.olbrzym, (-29, 0, -15), 0.8, 25, 200, zajmij=(-29, -15, 8))
    for x, z, k, ry in ((10.5, -15.5, 1.0, 10), (13.5, -12.5, 0.85, 80), (-10.5, -16.5, 1.05, 40), (-13, -13, 0.8, 160), (16, -17.5, 0.9, 0)):
        b.p("Pniaki", pien_z_dynia, (x, 0, z), k, ry)
    for x, z, k in ((9, -11.5, 0.8), (12, -18.5, 1.0), (-8.5, -13, 0.75), (15.5, -14.5, 0.7)):
        b.p("Pniaki", dynia, (x, 0, z), k)
    b.p("Drewno", DT.kloda, (-16, 0, -20), 1.1, True)
    b.p("Drewno", DT.kloda, (18, 0, -22), 1.0, True)
    b.p("Drewno", DT.stos_drewna, (-17.5, 0, -15.5), 30)
    b.p("Drewno", DT.stos_drewna, (19.5, 0, -12), -40)
    b.p("Drewno", DT.stos_drewna, (-12.5, 0, -21.5), 100)
    b.p("Drewno", RL.pniak, (14, 0, -4.5), 1.1, 0)
    b.p("Drewno", RL.pniak, (-15, 0, -1.5), 0.9, 50)
    b.p("Drewno", DT.plotek, (17, 0, -27), 4)
    b.p("Runo", R.kepa_grzybow, (-22, 0, -9), 1.0, 0, zajmij=(-22, -9, 3))
    b.p("Runo", SK.glaz, (22, 0, -6), 1.0, 70, "kamien_cieply", "SmoothPlastic", True, False)
    for x, z in ((-19, -4), (20, -17), (-6, -24), (7, -25), (23, 2), (-23, 3)):
        b.p("Runo", RL.paproc, (x, 0, z), rnd.uniform(1.0, 1.5))
    for x, z in ((-11, -8), (12, -8), (5, -21), (-4, -20.5)):
        b.p("Runo", RL.kwiaty, (x, 0, z), rnd.choice((("zloto", "biel"), ("czerwien", "zloto"))))
    b.p("Swiatlo", R.promien_swiatla, (12, 0, -27), 26.0, 3.5, 200, 15)
    kulisy(b)


def kondycja(b):
    """Grobla przez Bagno: kładka z desek biegnie przez wodę do chaty na palach; latarnie, łódka, grzybienie, szuwary."""
    rnd, w = b.rnd, b.woda
    b.p("Kladka", kladka, (0, 11.4), (0, 31), 4.6, 0.2, w, 4)        # ku kamerze (płaska, pod kadrem)
    b.p("Kladka", kladka, (0, -7.6), (0, -19), 4.4, 0.2, w, 3)       # za szyldem — w głąb Bagna
    b.p("Kladka", kladka, (-1.2, -19), (-5.5, -24), 3.6, 0.2, w, 2)
    b.p("Chata", R.chata_na_palach, (-7, 0, -29), 1.0, 14, 5.0, w, zajmij=(-7, -29, 8))
    b.p("Chata", R.latarnia_pal, (3.4, 0, -10.5), 6.0, 180, w)
    b.p("Chata", R.latarnia_pal, (-3.4, 0, -17), 5.4, 0, w)
    b.p("Chata", R.latarnia_pal, (11.6, 0, -5.2), 5.0, 180, w)
    b.p("Chata", R.lodka, (13.5, 0, 1.0), 25, w)
    b.p("Chata", R.zatopiony_pien, (-13, 0, -9), 1.0, 30, w)
    b.p("Chata", R.zatopiony_pien, (15, 0, -17), 0.9, 110, w)
    b.p("Chata", R.wieza_obserwacyjna, (20, 0, -30), 0.8, -20, w, zajmij=(20, -30, 5))
    for x, z, r in ((-9, -3, 1.2), (-11.5, -5, 0.9), (-7.5, 4, 1.0), (9, -12, 1.1), (7, 7, 0.9), (-14, 8, 1.2), (-6, -13, 1.0),
                    (16, 7, 1.1), (-17, -15, 0.9), (5.5, -22, 1.0), (-19, -2, 1.0)):
        b.p("Woda", RB.grzybien, (x, w, z), r, rnd.choice((None, None, "bagno_kwiat", "biel")))
    for x, z in ((-12, -1), (10.5, -15.5), (-16, -10), (8, -25)):
        b.p("Szuwary", R.kepa_z_trzcina, (x, 0, z), rnd.uniform(0.8, 1.1), 0.0, w)
    for x, z in ((-15, -19), (14, -22), (-20, 5), (22, -14), (17.5, 3)):
        b.p("Szuwary", R.trzcina_zdzbla, (x, w, z), rnd.uniform(4.6, 6.0), 3.4, True)
    for x, y, z in ((-9, 2.2, -8), (8, 1.6, -19), (-15, 2.6, -15), (14, 2.0, -12), (-4, 1.8, -22)):
        b.p("Ogniki", lambda s, r_, p=(x, y, z): RB.ognik(s, p, 0.7))
    b.p("Mgla", R.mgla_plat, (-12, 0, -18), 26, 12, w + 0.12, 0.72)
    b.p("Mgla", R.mgla_plat, (14, 0, -24), 24, 11, w + 0.12, 0.76)
    kulisy(b)


def zrecznosc(b):
    """Pomost nad topielą (Bagno): okrągły pomost na palach wśród cypryśników; kładki, wieża obserwacyjna, chata, łódka."""
    rnd, w = b.rnd, b.woda
    b.p("Kladka", kladka, (0, 4.3), (0, 31), 4.4, 0.16, w, 5)          # dojście od południa (płaskie)
    b.p("Kladka", kladka, (-9.5, -6.6), (-11, -6.6), 3.0, 0.1, w, 1)   # mostek do pomostu drwala
    for i in range(12):                                                # pale wokół pomostu (od strony kamery pomijane)
        a = math.radians(15 + 30 * i)
        b.p("Pale", R.pal, (math.cos(a) * 12.0, 0.1, -7 + math.sin(a) * 12.0), rnd.uniform(1.1, 1.7), 0.42, "bagno_kora", w - 1.0)
    b.p("Wieza", R.wieza_obserwacyjna, (-19, 0, -25), 0.95, 30, w, zajmij=(-19, -25, 5.5))
    b.p("Wieza", R.chata_na_palach, (17, 0, -27), 0.85, -18, 4.6, w, zajmij=(17, -27, 7))
    b.p("Wieza", R.lodka, (-15.5, 0, 2.5), -35, w)
    b.p("Wieza", R.latarnia_pal, (13.2, 0, -10), 5.6, 200, w)
    b.p("Wieza", R.latarnia_pal, (-3.2, 0, -19.8), 5.2, 0, w)
    b.p("Wieza", R.zatopiony_pien, (15, 0, -1.5), 1.0, 70, w)
    b.p("Wieza", R.zatopiony_pien, (-8, 0, -23), 0.9, 10, w)
    for x, z, r in ((14, -4, 1.2), (16.5, -6.5, 0.9), (-14, -13, 1.1), (-16, 6, 1.0), (13, 6, 0.9), (9, -21, 1.1), (-12, -19, 0.9), (19, -14, 1.2),
                    (-20, -4, 1.0), (2, -22.5, 0.8), (-22, -13, 1.1)):
        b.p("Woda", RB.grzybien, (x, w, z), r, rnd.choice((None, None, "bagno_kwiat", "biel")))
    for x, z in ((-17, -9), (18, -9.5), (12.5, -17), (-22, 1)):
        b.p("Szuwary", R.kepa_z_trzcina, (x, 0, z), rnd.uniform(0.8, 1.1), 0.0, w)
    for x, z in ((-15, -17), (15.5, 3), (7, -24), (-21, 9), (22, -20)):
        b.p("Szuwary", R.trzcina_zdzbla, (x, w, z), rnd.uniform(4.4, 6.0), 3.4, True)
    for x, y, z in ((-14, 2.4, -11), (13, 1.8, -14), (-6, 2.0, -21.5), (17, 2.6, -3), (-18, 1.6, 4)):
        b.p("Ogniki", lambda s, r_, p=(x, y, z): RB.ognik(s, p, 0.7))
    b.p("Mgla", R.mgla_plat, (12, 0, -21), 26, 11, w + 0.12, 0.74)
    b.p("Mgla", R.mgla_plat, (-16, 0, -14), 22, 12, w + 0.12, 0.76)
    kulisy(b)


def pancerz(b):
    """Krąg strażnika (Dżungla): kamienna posadzka, menhiry wokół, brama ruin i posągi w zaroślach, świecące kwiaty."""
    rnd = b.rnd
    b.p("Krag", posadzka_kregu, (0, 0, -4.5), 15.0)
    b.p("Grunt", pas_gruntu, (0, 10.5), (0, 30), 3.6, "dz_kamien", 0.02, 0.08, "Slate")
    # menhiry kręgu: ciemniejsze od golema i odsunięte od niego — obramowują bramę ruin, nie zlewają się ze strażnikiem
    for x, z, h in ((-25, -14, 10.0), (-5.5, -28, 11.0), (4, -22.5, 8.5), (-22, 2.5, 9.0), (19, -19.5, 9.5)):
        b.p("Krag", SK.menhir, (x, 0, z), h, _ku(x, z, (0, -4.5)), "dz_kamien_ciemny", "Slate", 7.0)
    b.p("Ruiny", R.brama_ruin, (-17.5, 0, -25), 0.95, _ku(-17.5, -25, (0, -4.5)), zajmij=(-17.5, -25, 9))
    b.p("Ruiny", R.posag_dzungli, (-23.5, 0, -8), 1.0, _ku(-23.5, -8, (0, -4.5)), zajmij=(-23.5, -8, 3.5))
    b.p("Ruiny", R.posag_dzungli, (12, 0, -26), 1.0, _ku(12, -26, (0, -4.5)), zajmij=(12, -26, 3.5))
    b.p("Ruiny", R.kolumna_zlamana, (22.5, 0, -12), 1.0, 30, True)
    b.p("Ruiny", R.kolumna_zlamana, (-21, 0, 4), 1.0, 200, True)
    b.p("Ruiny", R.kolumna_zlamana, (10, 0, -19.5), 1.0, 100, False)
    b.p("Ruiny", R.kolumna_zlamana, (-12, 0, 9), 0.9, 300, False)
    b.p("Ruiny", R.kolumna_zlamana, (17.5, 0, -6), 0.9, 240, False)
    for x, z in ((-19, -15.5), (7, -21.5), (-21, -1.5), (19, -21)):
        b.p("Kwiaty", R.kepa_swiecacych, (x, 0, z), 1.0, rnd.uniform(0, 360))
    for x, z in ((-13.5, -20.5), (16, -11), (-18.5, 6.5), (1.5, -23), (21.5, -9), (-10, -22)):
        b.p("Poszycie", RD.krzew_dzungli, (x, 0, z), rnd.uniform(1.0, 1.4), rnd.choice((None, "dz_kwiat_czerwony", "dz_kwiat_zolty")))
    for x, z in ((-22, -19), (22.5, -18), (-23, 10), (9.5, -27.5)):
        b.p("Poszycie", RD.lisc_parasol, (x, 0, z), rnd.uniform(0.9, 1.2), rnd.uniform(0, 360))
    for x, z in ((-16, -9), (15, -19.5), (-8, -20), (22, 1)):
        b.p("Poszycie", RD.paproc, (x, 0, z), rnd.uniform(1.0, 1.5))
    kulisy(b)


def inteligencja(b):
    """Świątynia run (Dżungla): za ścianą tablic piętrzy się świątynia, obok wodospad; kolumny, posągi, bambus."""
    rnd = b.rnd
    b.p("Grunt", pas_gruntu, (3, -6.8), (3, 6), 12.5, "dz_kamien", 0.02, 0.08, "Slate")
    b.p("Grunt", pas_gruntu, (0, 6), (0, 30), 3.6, "dz_kamien", 0.02, 0.08, "Slate")
    b.p("Grunt", lata, (3, 0, -1), 9.5, "dz_kamien_ciemny", 0.04)
    b.p("Swiatynia", R.swiatynia, (9, 0, -30), 0.8, 0, zajmij=(9, -30, 18))
    b.p("Wodospad", R.wodospad, (-24, 0, -29), 0.62, _ku(-24, -29, (0, -4)), zajmij=(-24, -29, 12))
    for x, z, stoi in ((-10.5, -9.5, True), (14, -9.5, True), (-13.5, -3, True), (17, -3.5, True), (-9, -15, False), (15.5, -15, False)):
        b.p("Ruiny", R.kolumna_zlamana, (x, 0, z), 1.0, rnd.uniform(0, 360), stoi)
    b.p("Ruiny", R.posag_dzungli, (-17, 0, -12), 1.0, _ku(-17, -12, (2, 0)), zajmij=(-17, -12, 3.5))
    b.p("Ruiny", R.posag_dzungli, (21, 0, -11), 1.0, _ku(21, -11, (2, 0)), zajmij=(21, -11, 3.5))
    b.p("Ruiny", SK.menhir, (-20.5, 0, -2), 10.0, 20, "dz_kamien", "Slate", 9.0)
    for x, z in ((-12.5, -12), (11.5, -13), (-19, -7), (19.5, -17.5)):
        b.p("Kwiaty", R.kepa_swiecacych, (x, 0, z), 1.0, rnd.uniform(0, 360))
    b.p("Poszycie", RD.bambus, (-21, 0, 5), 7.0, 5, 30, 2.6)
    b.p("Poszycie", RD.bambus, (22, 0, 2), 6.4, 5, 100, 2.6)
    for x, z in ((-15, -17), (17.5, -8), (-22.5, -16), (23, -6), (-11, 8), (13, 9)):
        b.p("Poszycie", RD.krzew_dzungli, (x, 0, z), rnd.uniform(1.0, 1.4), rnd.choice((None, "dz_kwiat_czerwony", "dz_kwiat_zolty")))
    for x, z in ((-18, 1), (20, -1), (-14, -21), (24, -14)):
        b.p("Poszycie", RD.lisc_parasol, (x, 0, z), rnd.uniform(0.9, 1.2), rnd.uniform(0, 360))
    kulisy(b)


BUDOWY = {"szczescie": szczescie, "sila": sila, "kondycja": kondycja, "zrecznosc": zrecznosc, "pancerz": pancerz,
          "inteligencja": inteligencja}


# ------------------------------------------------------------------------------------------------ generowanie
def generuj():
    """→ (dane do scenerie.json, {gra: lista pominiętych rekwizytów})."""
    import numpy as np
    K, D = DANE.wczytaj()
    czesci, pominiete, liczby = [], {}, {}
    for gra in K["scenerie"]["kolejnosc"]:
        b = Bud(D, K, gra, np)
        BUDOWY[gra](b)
        cz = b.czesci()
        czesci += cz
        pominiete[gra] = b.pominiete
        liczby[gra] = len(cz)
    dane = {"wersja": 1, "opis": "WYGENEROWANE przez swiat/trening_proba/scenerie.py — nie edytuj ręcznie. Części scenerii "
                                 "mini-gier (D-108) w układzie areny (bez środka areny), wszystkie bez kolizji.",
            "liczby": liczby, "czesci": czesci}
    return dane, pominiete


def tekst(dane):
    wiersze = ",\n".join(json.dumps(c, ensure_ascii=False, separators=(",", ":")) for c in dane["czesci"])
    glowa = json.dumps({k: v for k, v in dane.items() if k != "czesci"}, ensure_ascii=False, separators=(",", ":"))
    return glowa[:-1] + ',"czesci":[\n' + wiersze + "\n]}\n"


def aktualny():
    dane, _ = generuj()
    if not os.path.isfile(PLIK):
        return False, dane
    with open(PLIK, encoding="utf-8") as f:
        return f.read() == tekst(dane), dane


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    if "--sprawdz" in argv:
        ok, dane = aktualny()
        print("scenerie.json: %s (%d części)" % ("aktualny" if ok else "NIEAKTUALNY — uruchom scenerie.py", len(dane["czesci"])))
        return 0 if ok else 1
    dane, pominiete = generuj()
    if "--raport" not in argv:
        with open(PLIK, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst(dane))
    K = DANE._czytaj_json(DANE.USTAWIENIA)
    razem = 0
    for gra in K["scenerie"]["kolejnosc"]:
        n = dane["liczby"][gra]
        razem += n
        print("%-13s %-22s %-8s %4d części, pominięte rekwizyty: %d" % (gra, K["scenerie"][gra]["nazwa"], K["scenerie"][gra]["kraina"],
                                                                      n, len(pominiete[gra])))
        for x in pominiete[gra]:
            print("    - " + x)
    print("razem scenerie: %d części%s" % (razem, "" if "--raport" in argv else " → " + os.path.relpath(PLIK, REPO).replace("\\", "/")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
