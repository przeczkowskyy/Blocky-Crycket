# -*- coding: utf-8 -*-
"""Zawartość przegród i przejść pasa (bez kulis i drobnych detali): rekwizyty Polany, płoty i kojce Zagrody, grzyby
Lasku, wykroty Zarośli, głazy i łupy Leża, przedbramie; płot z furtką, jeżynowe zwężenie, kamienny próg, niskie kamienie
bramy menhirów; domy potworów pod ścianami (z planu: dom.pts) — kałuże galarety, chatki-grzyby, jamy w jeżynach,
szpary w głazach, legowisko trolla.

Rzeczy w polu gry stawiamy przez zasady.postaw (place walki, ścieżka, pętle, otwarcia, przelot kamery — liczone na
częściach), a miejsca wybieramy maską kontekstu (kontekst.Pas.miejsce_ok). Rekwizyty z modułów starego lasu
(detale.py, lokacje/wspolne.py, rosliny.py, skaly.py) i miasteczka (zestaw.py). Układ: x = u, z = v.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale, rosliny, skaly  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

GRUPA = {"wejscie": "Polana", "zagroda": "Zagroda", "lasek": "Lasek", "zarosla": "Zarosla", "leze": "Leze", "arena": "Arena"}


def _ku_sciezce(u, v):
    """ry, przy którym front (+Z lokalne) patrzy w stronę osi pasa (v = 0)."""
    return 0.0 if v < 0 else 180.0


def plot_prosty(s, rnd, u, v0, v1, wys=1.2, krok=4.6, pal="Pal"):
    """Prosty płot w poprzek pasa (u stałe) od v0 do v1: pale co ok. `krok` z kolizją i dwie żerdzie na przęsło.
    Ok. 3 części na przęsło."""
    n = max(1, int(round(abs(v1 - v0) / krok)))
    for i in range(n + 1):
        v = v0 + (v1 - v0) * i / n
        h = wys + rnd.uniform(-0.1, 0.15)
        s.blok(pal, (u + rnd.uniform(-0.15, 0.15), h / 2.0 - 0.2, v), (0.6, h + 0.4, 0.6), "drewno", rot=(0, rnd.uniform(0, 30), rnd.uniform(-4, 4)))
    with s.cechy(kolizja=False):
        for i in range(n):
            a = v0 + (v1 - v0) * i / n
            b = v0 + (v1 - v0) * (i + 1) / n
            for y, dy in ((wys * 0.42, 0.08), (wys * 0.82, -0.08)):
                s.belka("Płot żerdź", (u, y + dy, a), (u, y - dy, b), 0.32, "drewno_jasne", "SmoothPlastic", 0.3)


def plot_wzdluz(s, rnd, v, u0, u1, wys=2.4, krok=7.0):
    """Płot wzdłuż pasa (v stałe) od u0 do u1: pale z kolizją, dwie żerdzie. Ok. 3 części na przęsło."""
    n = max(1, int(round(abs(u1 - u0) / krok)))
    for i in range(n + 1):
        u = u0 + (u1 - u0) * i / n
        h = wys + rnd.uniform(-0.2, 0.25)
        s.blok("Pal", (u, h / 2.0 - 0.2, v + rnd.uniform(-0.15, 0.15)), (0.7, h + 0.4, 0.7), "drewno",
               rot=(rnd.uniform(-4, 4), rnd.uniform(0, 30), 0))
    with s.cechy(kolizja=False):
        for i in range(n):
            a = u0 + (u1 - u0) * i / n
            b = u0 + (u1 - u0) * (i + 1) / n
            for y, dy in ((wys * 0.38, 0.1), (wys * 0.78, -0.12)):
                s.belka("Płot żerdź", (a, y + dy, v), (b, y - dy, v), 0.4, "drewno_jasne", "SmoothPlastic", 0.35)


# =========================================================================== przejścia
def plot_z_furtka(s, K):
    """Płot 1,2 w poprzek pasa (da się przeskoczyć), furtka 16 st zawsze otwarta: słupki z lampionami przy otwarciu,
    skrzydło otwarte do Zagrody wzdłuż płotu po prawej, tabliczka ze znakiem galarety po lewej."""
    t = K.przejscia["plot_z_furtka"]
    rnd = K.rnd_przejscia
    u = (t["u_od"] + t["u_do"]) / 2.0
    o = t["otwarcie"][1]
    with s.grupa("Przejscia/PlotZFurtka"):
        for zn in (-1, 1):
            plot_prosty(s, rnd, u, zn * (o + 2.2), zn * 41.0, wys=t["wys_reszty"])
            s.blok("Wrota słup", (u, 1.5, zn * (o + 1.3)), (0.9, 3.4, 0.9), "drewno_ciemne", rot=(0, 0, zn * 4))
            with s.cechy(kolizja=False):
                s.blok("Lampion daszek", (u, 3.35, zn * (o + 1.3)), (1.5, 0.4, 1.5), "dach_karczma", rot=(0, 45, 0))
                s.blok("Lampion", (u, 2.95, zn * (o + 1.3)), (0.8, 0.8, 0.8), "neon_okno", "Neon", rot=(0, 45, 0))
        # skrzydło furtki otwarte do środka Zagrody, wzdłuż ścieżki po prawej (poza otwarciem)
        with s.uklad(pos=(u + 0.6, 0, o + 2.1), obrot=(0, 8, 0)):
            for x in (0.3, 5.6):
                s.blok("Wrota słup", (x, 1.1, 0), (0.5, 2.0, 0.5), "drewno_jasne")
            with s.cechy(kolizja=False):
                for y in (0.6, 1.6):
                    s.blok("Furtka", (2.95, y, 0), (5.6, 0.35, 0.3), "drewno_jasne")
                s.belka("Furtka", (0.3, 0.5, 0), (5.6, 1.8, 0), 0.3, "drewno", "SmoothPlastic", 0.25)
        detale.tabliczka(s, rnd, (u - 2.0, 0, -(o + 4.5)), -90 + 12, "laka")
    for zn in (-1, 1):
        K.zajmij(u, zn * (o + 1.3), 1.5)
    K.zajmij(u + 3.0, o + 2.1, 3.0)
    K.zajmij(u - 2.0, -(o + 4.5), 1.4)


def jezynowe_zwezenie(s, K):
    """Kępy jeżyn 6 wys. od obu ścian zwężają przejście do 32 st: fioletowe ściany z garbami, jasne kolce, zwisy liści."""
    t = K.przejscia["jezynowe_zwezenie"]
    rnd = K.rnd_przejscia
    u = (t["u_od"] + t["u_do"]) / 2.0
    o = t["otwarcie"][1]
    h = t["wys_reszty"]
    with s.grupa("Przejscia/JezynoweZwezenie"):
        for zn in (-1, 1):
            for i, (v0, v1, dh, du) in enumerate(((o + 1.4, o + 9.5, 0.0, 0.0), (o + 8.5, o + 17.5, -0.8, 1.2), (o + 16.5, 44.0, 0.6, -0.8))):
                vc = zn * (v0 + v1) / 2.0
                dl = v1 - v0
                hh = h + dh
                with s.uklad(pos=(u + du, 0, vc), obrot=(0, rnd.uniform(-5, 5), 0)):
                    s.blok("Ściana jeżyn", (0, hh / 2.0 - 0.3, 0), (10.5 - i * 0.6, hh + 0.6, dl), "jezyna")
                    with s.cechy(kolizja=False):
                        s.blok("Jeżyna garb", (rnd.uniform(-1.5, 1.5), hh + 0.2, rnd.uniform(-dl / 5, dl / 5)), (6.0, 1.6, dl * 0.55),
                               cien(s, "jezyna", 1.2), rot=(rnd.uniform(-6, 6), rnd.uniform(-20, 20), rnd.uniform(-6, 6)))
                        with s.cechy(cien=False):
                            for k in range(3):
                                s.naroznik("Kolec", (rnd.uniform(-4.0, 4.0), hh + rnd.uniform(-0.6, 0.9), rnd.uniform(-dl / 2.4, dl / 2.4)),
                                           (0.8, 1.4, 0.8), "jezyna_kolec", rot=(0, rnd.uniform(0, 90), 0))
                            for sx in (-1, 1):
                                s.klin("Jeżyna zwis", (sx * (5.3 - i * 0.3), hh - 0.9, rnd.uniform(-dl / 4, dl / 4)), (dl * 0.4, 1.8, 0.5),
                                       "lisc_ciemny", rot=(0, 90 * sx, 180))
                K.zajmij(u + du, vc, 4.0)


def kamienny_prog(s, K):
    """Głazy 8–10 od obu ścian zwężają przejście do 28 st; kości w trawie (płasko), ukradziony szyld karczmy z miasteczka
    i pal z czaszką — ostrzeżenie przed trollem."""
    t = K.przejscia["kamienny_prog"]
    rnd = K.rnd_przejscia
    u = (t["u_od"] + t["u_do"]) / 2.0
    o = t["otwarcie"][1]
    with s.grupa("Przejscia/KamiennyProg"):
        for zn in (-1, 1):
            for i, (vv, w, h, d) in enumerate(((o + 5.0, 7.0, 9.5, 9.0), (o + 12.0, 8.0, 8.2, 11.0), (o + 19.5, 7.5, 10.0, 10.0),
                                               (o + 26.5, 6.0, 7.0, 9.0))):
                with s.uklad(pos=(u + rnd.uniform(-0.8, 0.8), 0, zn * vv), obrot=(rnd.uniform(-4, 4), rnd.uniform(-15, 15), zn * rnd.uniform(4, 8))):
                    s.blok("Głaz", (0, h / 2.0 - 0.6, 0), (d, h + 1.2, w), cien(s, "kamien_cieply", 0.8 + 0.06 * (i % 2)))
                    with s.cechy(kolizja=False):
                        s.naroznik("Głaz wierzch", (0.3, h + 0.6, 0), (d * 0.7, 1.8, w * 0.7), "kamien_cieply", rot=(0, 90 * (i % 4), 0))
                        if i % 2 == 0:
                            with s.cechy(cien=False):
                                s.blok("Mech", (-0.6, h + 0.1, 0.4), (d * 0.5, 0.4, w * 0.45), "mech", rot=(0, 15, 0))
                K.zajmij(u, zn * vv, 4.5)
        with s.cechy(kolizja=False, cien=False):
            for k in range(6):
                s.blok("Kość", (u + rnd.uniform(-6, 6), 0.22, rnd.uniform(-11, 11)), (2.2, 0.4, 0.55), "biel", rot=(0, rnd.uniform(0, 180), 0))
        # ukradziony szyld (czerwona rama karczmy, złoty bochenek) — wbity krzywo po lewej, przodem do Zarośli
        with s.uklad(pos=(u - 7.6, 0, -(o + 3.2)), obrot=(0, -90 + 14, 0)):
            s.blok("Szyld słup", (0, 2.6, 0), (0.6, 5.2, 0.6), "drewno_ciemne", rot=(0, 0, -8))
            with s.cechy(kolizja=False):
                s.blok("Szyld", (0.4, 4.4, 0.4), (4.0, 2.6, 0.4), "tynk_krem", rot=(0, 0, -8))
                s.ramka("Szyld rama", (0.4, 4.4, 0.7), 4.0, 2.6, "dach_karczma", 0.4, 0.3)
                s.blok("Szyld bochenek", (0.4, 4.4, 0.8), (2.0, 1.0, 0.2), "zloto", rot=(0, 0, -8))
        K.zajmij(u - 7.6, -(o + 3.2), 2.6)
        detale.czaszka(s, rnd, (u - 6.0, 0, o + 2.6), -90)
        K.zajmij(u - 6.0, o + 2.6, 1.2)


def brama_menhirow_kamienie(s, K):
    """Niskie kamienie (≤ 1,2) od menhirów do ścian bramy — widać przez nie arenę i kryształ."""
    t = K.przejscia["brama_menhirow"]
    rnd = K.rnd_przejscia
    u = (t["u_od"] + t["u_do"]) / 2.0
    with s.grupa("Przejscia/BramaMenhirow"):
        for zn in (-1, 1):
            v = 20.5
            while v < 42:
                skaly.kanciak(s, rnd, (u + rnd.uniform(-3.5, 3.5), 0, zn * v), rnd.uniform(0.75, 0.95), rnd.uniform(0, 360))
                K.zajmij(u, zn * v, 1.6)
                v += rnd.uniform(3.6, 5.0)


# =========================================================================== domy potworów
def domy(s, K):
    """Domy potworów w punktach `dom.pts` z planu (|v| = 34, pod ścianą). Bryły wyższe niż 1,4 stoją głębiej, za linią
    pola gry (|v| ≈ 40, w kulisach), drzwiami / otworem do ścieżki — potwór wychodzi w punkcie z planu."""
    rnd = K.rnd_domy
    for st in K.strefy:
        pot = st["potwor"]
        for (hu, hv) in st["dom"]["pts"]:
            zn = 1 if hv > 0 else -1
            ry = _ku_sciezce(hu, hv)
            with s.grupa("Domy/%s" % st["id"]):
                if pot == "Leśny Slime":
                    wspolne.kaluza_galarety(s, rnd, (hu, 0.02, hv))
                    K.zajmij(hu, hv, 3.4)
                elif pot == "Muchomornik":
                    wspolne.chatka_grzyb(s, rnd, (hu, 0, zn * 40.5), ry, rnd.uniform(0.95, 1.08))
                    K.zajmij(hu, zn * 40.5, 5.5)
                elif pot == "Cierniowy Wilk" and st["id"] != "w3":
                    wspolne.jama(s, rnd, (hu, 0, zn * 41.5), ry)
                    K.zajmij(hu, zn * 41.0, 5.5)
                elif pot == "Cierniowy Wilk":
                    wspolne.szpara(s, rnd, (hu, 0, zn * 41.0), ry, "kamien_lochu")
                    K.zajmij(hu, zn * 41.0, 5.5)
                else:
                    legowisko_trolla(s, K, hu, hv)


def legowisko_trolla(s, K, hu, hv):
    """Dom trolla: grota z dwóch głazów i nadproża pod lewą ścianą, ciemny otwór do ścieżki, kości i kij przed wejściem."""
    zn = 1 if hv > 0 else -1
    rnd = K.rnd_domy
    with s.uklad(pos=(hu, 0, zn * 42.5), obrot=(0, _ku_sciezce(hu, hv), 0)):
        for sx in (-1, 1):
            s.blok("Głaz", (sx * 6.2, 4.4, 0), (5.2, 10.0, 7.0), cien(s, "kamien_cieply", 0.78 + 0.06 * (sx > 0)),
                   rot=(0, sx * 10, -sx * 6))
        s.blok("Legowisko nadproże", (0, 9.6, 0.2), (15.0, 2.4, 6.4), "kamien_cokol", rot=(0, 0, 3))
        with s.cechy(kolizja=False):
            s.blok("Legowisko", (0, 4.6, -1.0), (8.0, 8.6, 0.5), "tusz")
            s.blok("Głaz wierzch", (1.0, 11.4, 0.0), (8.0, 1.6, 5.0), "kamien_cieply", rot=(0, 0, 4))
            with s.cechy(cien=False):
                s.blok("Mech", (-2.5, 11.0, 0.6), (5.0, 0.4, 3.6), "mech", rot=(0, 12, 3))
                for k in range(4):
                    s.blok("Kość", (rnd.uniform(-4, 4), 0.22, rnd.uniform(4.5, 7.5)), (2.2, 0.4, 0.55), "biel", rot=(0, rnd.uniform(0, 180), 0))
    K.zajmij(hu, zn * 42.5, 9.0)


# =========================================================================== przegrody
def polana(s, K, Z):
    """Polana Przybycia: drogowskaz z pięcioma ramionami (rekwizyty kolejnych przegród), beczka, skrzynka, kosz,
    lampiony przy ścieżce."""
    rnd = K.rnd_przegrody
    with s.grupa("Polana/Rekwizyty"):
        ram = [(90 + d, pb) for d, pb in ((-7, "laka"), (5, "kapeluszowo"), (-3, "ostepy"), (8, "wawoz"), (-1, "korona"))]
        wspolne.drogowskaz(s, rnd, (47.0, 0, -13.5), ram)
        K.zajmij(47.0, -13.5, 2.5)
        zestaw.beczka(s, (55.0, 0, -31.0), "jablka", r=1.3, h=3.0, przechyl=(0.0, 5.0), ry=20)
        K.zajmij(55.0, -31.0, 2.0)
        detale.skrzynka(s, rnd, (51.0, 0, -32.5), 30)
        K.zajmij(51.0, -32.5, 2.0)
        detale.kosz(s, rnd, (58.5, 0, -28.0), 10)
        K.zajmij(58.5, -28.0, 1.5)
        for (u, v) in ((26.0, -9.0), (41.0, 11.0), (60.0, 9.5)):
            wspolne.lampion(s, (u, 0, v), rnd.uniform(4.8, 5.6))
            K.zajmij(u, v, 2.0)
        detale.stos_drewna(s, rnd, (24.0, 0, 31.5), 80)
        K.zajmij(24.0, 31.5, 2.4)


def zagroda(s, K, Z):
    """Zagroda Slime'ów: płot wzdłuż obu ścian (|v| = 37,5), niskie przegródki z żywopłotu 0,8 między kojcami z przerwą
    24 na środku, w każdym kojcu koryto z galaretą i worek/skrzynka w wolnym rogu."""
    rnd = K.rnd_przegrody
    q = K.przegrody["zagroda"]
    with s.grupa("Zagroda/Plot"):
        for zn in (-1, 1):
            plot_wzdluz(s, rnd, zn * 37.6, q["u_od"] + 1.0, q["u_do"] - 1.5, wys=2.4, krok=7.2)
    with s.grupa("Zagroda/Przegrodki"):
        for p in q["pod"][1:]:
            u = p["u_od"]
            for zn in (-1, 1):
                v = 12.0
                while v < 36.5:
                    dl = min(5.5, 36.5 - v)
                    if dl > 1.0 and K.wolne(u, zn * (v + dl / 2.0), dl / 2.0 - 0.2):
                        with s.uklad(pos=(u + rnd.uniform(-0.2, 0.2), 0, zn * (v + dl / 2.0)), obrot=(0, rnd.uniform(-5, 5), 0)):
                            with s.cechy(kolizja=False):
                                s.blok("Żywopłot", (0, 0.36, 0), (1.3, 0.8, dl), "lisc_ciemny")
                                with s.cechy(cien=False):
                                    s.blok("Żywopłot", (0.1, 0.62, rnd.uniform(-0.5, 0.5)), (1.0, 0.36, dl * 0.7), "lisc",
                                           rot=(0, rnd.uniform(-6, 6), 0))
                    v += dl
    # koryto z galaretą i worek/skrzynka w wolnych rogach każdego kojca
    for p in q["pod"]:
        jest = False
        for du, zn in ((5.0, -1), (p["u_do"] - p["u_od"] - 5.0, 1), (5.0, 1), (p["u_do"] - p["u_od"] - 5.0, -1)):
            if jest:
                break
            u = p["u_od"] + du
            for vv in (29.5, 31.0, 33.0):
                v = zn * vv
                if K.miejsce_ok(u, v, 2.8, 1.6, kolizja=True):
                    def koryto(u=u, v=v):
                        with s.grupa("Zagroda/Koryta"), s.uklad(pos=(u, 0, v), obrot=(0, rnd.uniform(-15, 15), 0)):
                            s.blok("Skrzynia", (0, 0.5, 0), (4.6, 1.0, 1.9), "drewno", "WoodPlanks")
                            with s.cechy(kolizja=False):
                                s.blok("Galareta", (0, 1.05, 0), (4.0, 0.3, 1.4), "galareta")
                                s.blok("Bąbel", (1.2, 1.3, 0.2), (0.6, 0.5, 0.6), "galareta", rot=(0, 30, 0))
                                for sx in (-1, 1):
                                    s.blok("Skrzynia listwa", (sx * 2.3, 0.55, 0), (0.4, 1.2, 2.1), "drewno_ciemne")
                    if postaw(s, Z, koryto):
                        K.zajmij(u, v, 3.0)
                        jest = True
                        break
        u = p["u_od"] + 4.5 if p["id"] != "kojec_1" else p["u_od"] + 6.0
        for vv in (31.0, 33.0):
            v = vv
            if K.miejsce_ok(u, v, 2.0, 2.6, kolizja=True):
                if postaw(s, Z, lambda u=u, v=v: _skrzynka_w_grupie(s, rnd, u, v, "Zagroda/Rekwizyty")):
                    K.zajmij(u, v, 2.2)
                    break


def _skrzynka_w_grupie(s, rnd, u, v, grupa):
    with s.grupa(grupa):
        detale.skrzynka(s, rnd, (u, 0, v), rnd.uniform(0, 90))


def lasek(s, K, Z):
    """Lasek Muchomorowy: w wolnych rogach polanek grzyby-olbrzymy (kapelusze ponad placami walki), na granicach polanek
    niskie kręgi grzybków (≤ 1,4), lampiony zarodników przy ścianach."""
    rnd = K.rnd_przegrody
    q = K.przegrody["lasek"]
    granice = [q["u_od"]] + [p["u_do"] for p in q["pod"]]
    # grzyby-olbrzymy w rogach
    for g in granice:
        for zn in (-1, 1):
            for vv in (31.0, 29.0, 33.0):
                u, v = g + rnd.uniform(-2.5, 2.5), zn * vv
                if not K.miejsce_ok(u, v, 2.0, 0.4, kolizja=True):
                    continue
                k = rnd.uniform(1.05, 1.35)
                kap = rnd.choice(("czerwien", "czerwien", "tynk_krem"))

                def grzyb(u=u, v=v, k=k, kap=kap):
                    with s.grupa("Lasek/Grzyby"):
                        rosliny.grzyb(s, rnd, (u, 0, v), k, rnd.uniform(0, 360), kapelusz=kap, kropki=kap == "czerwien",
                                      trzon="biel" if kap != "tynk_krem" else "drewno_jasne")
                if postaw(s, Z, grzyb):
                    K.zajmij(u, v, 2.5)
                    break
    # niskie kręgi grzybków na granicach polanek
    for g in granice[1:-1]:
        for zn in (-1, 1):
            for vv in (13.5, 19.0, 25.0):
                u, v = g + rnd.uniform(-1.5, 1.5), zn * (vv + rnd.uniform(-1, 1))
                if K.miejsce_ok(u, v, 1.6, 0.4):
                    if postaw(s, Z, lambda u=u, v=v: _grzybki_w_grupie(s, rnd, u, v)):
                        K.zajmij(u, v, 1.6)
    # lampiony zarodników
    for u, zn in ((300.0, -1), (366.0, 1), (430.0, -1), (474.0, 1)):
        for vv in (34.0, 32.5):
            v = zn * vv
            if K.miejsce_ok(u, v, 1.8, 5.6, kolizja=True):
                def lamp(u=u, v=v):
                    with s.grupa("Lasek/Lampiony"):
                        wspolne.lampion(s, (u, 0, v), rnd.uniform(4.8, 5.4), "neon_zarodnik")
                if postaw(s, Z, lamp):
                    K.zajmij(u, v, 2.0)
                    break


def _grzybki_w_grupie(s, rnd, u, v):
    from swiat.biom_las.detale import grzybki
    with s.grupa("Lasek/Grzybki"):
        grzybki(s, rnd, (u, 0, v), rnd.choice((("czerwien", "biel"), ("czerwien", "biel"), ("tynk_krem", "biel"))))


def wykrot(s, rnd, u, v, zn):
    """Wykrot: stojący talerz korzeni zwalonego drzewa (dziura w ziemi), pień leżący wzdłuż ściany, korzenie, mech."""
    with s.uklad(pos=(u, 0, v), obrot=(0, rnd.uniform(-12, 12), 0)):
        s.walec("Talerz korzeni", (0, 3.4, 0), 3.6, 1.4, "drewno_ciemne", "Wood", os="x", rot=(0, 0, zn * 6))
        s.walec("Zwalony pień", (5.8, 1.15, zn * 0.6), 1.25, 10.0, "drewno", "Wood", os="x", rot=(0, zn * 4, 3))
        with s.cechy(kolizja=False):
            for k in range(5):
                a = math.radians(k * 72 + 20)
                s.belka("Korzeń", (-0.3, 3.4 + 2.2 * math.sin(a), 2.2 * math.cos(a)),
                        (-1.4, 3.4 + 4.2 * math.sin(a), 4.2 * math.cos(a)), 0.7, "drewno_ciemne", "Wood")
            with s.cechy(cien=False):
                s.blok("Mech", (5.8, 2.35, zn * 0.6), (7.0, 0.3, 1.3), "mech", rot=(0, zn * 4, 3))
                s.walec("Jama otwór", (-1.6, 0.08, 0), 2.6, 0.1, "tusz", os="y")
                s.walec("Kłoda słoje", (10.85, 1.15, zn * 0.95), 1.05, 0.15, "drewno_jasne", os="x", rot=(0, zn * 4, 3))


def zarosla(s, K, Z):
    """Wilcze Zarośla: wykroty w wolnych rogach przy ścianach, pale z czaszką przy wejściu, kępy jeżyn w polu."""
    rnd = K.rnd_przegrody
    q = K.przegrody["zarosla"]
    n = 0
    for u in (502.0, 557.0, 566.0, 622.0, 682.0, 530.0):
        for zn in ((-1, 1) if n % 2 == 0 else (1, -1)):
            for vv in (31.0, 32.5):
                v = zn * vv
                if K.miejsce_ok(u + 4.0, v, 6.0, 4.5, kolizja=True) and K.miejsce_ok(u, v, 4.0, 7.0, kolizja=True):
                    def w(u=u, v=v, zn=zn):
                        with s.grupa("Zarosla/Wykroty"):
                            wykrot(s, rnd, u, v, zn)
                    if postaw(s, Z, w):
                        K.zajmij(u + 4.0, v, 6.5)
                        n += 1
                        break
            else:
                continue
            break
    for zn in (-1, 1):
        for du in (0.0, 1.5, 3.0):
            u, v = q["u_od"] + 1.5 + du, zn * 24.0
            if K.miejsce_ok(u, v, 1.0, 5.8, kolizja=True):
                def cz(u=u, v=v, zn=zn):
                    with s.grupa("Zarosla/Ostrzezenia"):
                        detale.czaszka(s, rnd, (u, 0, v), -90 + zn * 10)
                if postaw(s, Z, cz):
                    K.zajmij(u, v, 1.2)
                    break
    # kępy jeżyn w wolnych miejscach przy ścianach pola
    for k in range(16):
        u = rnd.uniform(q["u_od"] + 3, q["u_do"] - 3)
        v = rnd.choice((-1, 1)) * rnd.uniform(28.0, 34.0)
        if K.miejsce_ok(u, v, 2.8, 4.5):
            def j(u=u, v=v):
                with s.grupa("Zarosla/Jezyny"):
                    rosliny.jezyna(s, rnd, (u, 0, v), rnd.uniform(0.8, 1.1))
            if postaw(s, Z, j):
                K.zajmij(u, v, 2.8)


def leze(s, K, Z):
    """Leże Trolla: głazy przy ścianach pola, łupy trolla (beczka i skrzynia z miasteczka, stos drewna, maczuga wbita
    w ziemię), kości."""
    rnd = K.rnd_przegrody
    q = K.przegrody["leze"]
    # głazy przy ścianach
    for k in range(26):
        u = rnd.uniform(q["u_od"] + 3, q["u_do"] - 3)
        zn = rnd.choice((-1, 1))
        kk = rnd.uniform(1.0, 1.9)
        v = zn * rnd.uniform(30.0, 34.5)
        if K.miejsce_ok(u, v, 2.8 * kk, 4.5 * kk, kolizja=True):
            def g(u=u, v=v, kk=kk):
                with s.grupa("Leze/Glazy"):
                    skaly.glaz(s, rnd, (u, 0, v), kk, rnd.uniform(0, 360), "kamien_cieply", mech=rnd.random() < 0.6)
            if postaw(s, Z, g):
                K.zajmij(u, v, 2.8 * kk)
    # łupy przy prawej ścianie (naprzeciw legowiska)
    lupy = [("beczka", 2.0), ("skrzynia", 3.0), ("stos", 2.2), ("maczuga", 1.6), ("beczka", 2.0), ("kosc", 1.2)]
    for rodzaj, r in lupy:
        for proba in range(40):
            u = rnd.uniform(q["u_od"] + 4, q["u_do"] - 4)
            v = rnd.uniform(27.0, 34.0) * (1 if proba % 3 else -1)
            if not K.miejsce_ok(u, v, r, 3.5, kolizja=True):
                continue

            def lup(u=u, v=v, rodzaj=rodzaj):
                with s.grupa("Leze/Lupy"):
                    if rodzaj == "beczka":
                        zestaw.beczka(s, (u, 0, v), rnd.choice(("woda", None)), r=1.4, h=3.2, przechyl=(rnd.uniform(-6, 6), 8.0),
                                      ry=rnd.uniform(0, 90))
                    elif rodzaj == "skrzynia":
                        zestaw.skrzynia(s, (u, 0, v), ry=rnd.uniform(0, 90), dl=3.6, a=2.8, przechyl=9)
                    elif rodzaj == "stos":
                        detale.stos_drewna(s, rnd, (u, 0, v), rnd.uniform(0, 180))
                    elif rodzaj == "maczuga":
                        s.blok("Maczuga w ziemi", (u, 2.4, v), (1.1, 4.8, 1.1), "drewno_ciemne", rot=(0, 20, 12))
                        with s.cechy(kolizja=False):
                            s.blok("Maczuga głowica", (u - 0.6, 5.4, v), (2.3, 2.3, 2.3), "drewno_ciemne", rot=(20, 30, 14))
                    else:
                        detale.czaszka(s, rnd, (u, 0, v), rnd.uniform(-120, -60))
            if postaw(s, Z, lup):
                K.zajmij(u, v, r)
                break
    with s.grupa("Leze/Kosci"), s.cechy(kolizja=False, cien=False):
        for k in range(14):
            u, v = rnd.uniform(q["u_od"] + 3, q["u_do"] - 3), rnd.uniform(-33, 33)
            if K.pole("d_sciezka", u, v) > 0.6:
                s.blok("Kość", (u, 0.22, v), (2.0, 0.4, 0.5), "biel", rot=(0, rnd.uniform(0, 180), 0))


def przedbramie(s, K, Z):
    """Przedbramie (strefa spokoju za areną): ławka, lampiony, stos kamieni, trzcina i suche drzewo — zapowiedź Bagna."""
    rnd = K.rnd_przegrody
    with s.grupa("Przedbramie"):
        zestaw.lawka(s, (921.0, 0, -15.5), ry=0, dl=6.0)
        K.zajmij(921.0, -15.5, 3.6)
        for u, v in ((913.0, 10.5), (928.0, -9.5)):
            wspolne.lampion(s, (u, 0, v), 5.4)
            K.zajmij(u, v, 2.0)
        detale.stos_kamieni(s, rnd, (916.0, 0, 26.0), 30, "wawoz")
        K.zajmij(916.0, 26.0, 1.4)
    for u, v in ((925.0, 31.0), (911.0, -31.0)):
        if K.miejsce_ok(u, v, 3.0, 17.0, kolizja=True):
            def sd(u=u, v=v):
                with s.grupa("Przedbramie"):
                    rosliny.suchy(s, rnd, (u, 0, v), rnd.uniform(0.85, 1.0), rnd.uniform(0, 360))
            if postaw(s, Z, sd):
                K.zajmij(u, v, 2.0)


def ozdoby(s, K, Z):
    """Drobne znaki przegród w wolnych miejscach pola gry: kałuże galarety w kojcach, świecące zarodniki w Lasku, płaty
    igliwia w Zaroślach, pniaki w Leżu, odłamki kryształu wokół areny. Każda przez zasady.postaw."""
    rnd = K.rnd_przegrody
    stat = {}

    def rozsiej(qid, ile, r, wys, budowa, v_od=-34.0, v_do=34.0, kolizja=False):
        q = K.przegrody[qid]
        n = proby = 0
        while n < ile and proby < ile * 60:
            proby += 1
            u = rnd.uniform(q["u_od"] + 2, q["u_do"] - 2)
            v = rnd.choice((-1, 1)) * rnd.uniform(v_od, v_do) if v_od >= 0 else rnd.uniform(v_od, v_do)
            if not K.miejsce_ok(u, v, r, wys, kolizja=kolizja):
                continue
            if postaw(s, Z, lambda u=u, v=v: budowa(u, v)):
                K.zajmij(u, v, r)
                n += 1
        stat[qid] = stat.get(qid, 0) + n

    def kaluza(u, v):
        with s.grupa("Zagroda/Kaluze"):
            wspolne.kaluza_galarety(s, rnd, (u, 0.02, v))
    rozsiej("zagroda", 12, 3.4, 0.9, kaluza)

    def zarodnik(u, v):
        with s.grupa("Lasek/Zarodniki"), s.cechy(kolizja=False, cien=False):
            for i in range(rnd.choice((2, 3))):
                s.blok("Zarodnik", (u + rnd.uniform(-1.5, 1.5), rnd.uniform(2.2, 5.0), v + rnd.uniform(-1.5, 1.5)),
                       (0.6, 0.6, 0.6), "neon_zarodnik", "Neon", rot=(rnd.uniform(0, 45), rnd.uniform(0, 90), rnd.uniform(0, 45)))
    rozsiej("lasek", 9, 2.0, 5.5, zarodnik, 30.0, 35.0)

    def igliwie(u, v):
        with s.grupa("Zarosla/Igliwie"), s.cechy(kolizja=False, cien=False):
            a = rnd.uniform(6.0, 10.0)
            s.blok("Igliwie", (u, 0.075 + rnd.uniform(0.0, 0.01), v), (a, 0.1, a * rnd.uniform(0.6, 0.9)), "runo_ciemne",
                   rot=(0, rnd.uniform(0, 90), 0))
    rozsiej("zarosla", 14, 4.0, 0.2, igliwie, 26.0, 34.0)

    def pniak(u, v):
        with s.grupa("Leze/Pniaki"):
            rosliny.pniak(s, rnd, (u, 0.0, v), rnd.uniform(0.9, 1.3), rnd.uniform(0, 90))
    rozsiej("leze", 7, 2.4, 3.2, pniak, 22.0, 34.0, kolizja=True)

    def odlamek(u, v):
        with s.grupa("Arena/Odlamki"), s.cechy(kolizja=False):
            for i in range(rnd.choice((1, 2))):
                h = rnd.uniform(1.6, 3.2)
                s.blok("Kryształ odłamek", (u + 0.9 * i, h / 2.0 - 0.2, v + rnd.uniform(-0.6, 0.6)), (0.8, h, 0.8), "neon_portal", "Neon",
                       rot=(rnd.uniform(-20, 20), rnd.uniform(0, 90), rnd.uniform(-20, 20)))
    rozsiej("arena", 8, 1.6, 3.4, odlamek, 24.0, 34.0)
    return stat
