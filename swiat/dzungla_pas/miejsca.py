# -*- coding: utf-8 -*-
"""Miejsca, punkty orientacyjne, przejścia, domy potworów, rekwizyty, Krąg Stu Lian, brama do Pustyni i zapowiedź
Pustyni (grupy „Punkty/<Nazwa>” — w Studio Persistent — oraz „BramaPustyni/Palisada” i „BramaPustyni/Wrota”: skrypt
otwiera same wrota dla gracza).

Z lasu-pasa bez zmian: `punkty.kamien_powrotu` i `punkty.stanowisko_jajka` (ten sam Kamień Powrotu i to samo stanowisko
jajka w każdym biomie). Reszta jest nowa: ruiny i posągi własnego wzoru (posąg-głaz z twarzą, posągi strażników
z kamiennym kapturem jak kaptur Węża Stu Lian, złamane kolumny, kamienie ze znakiem), Chatka na Drzewie, Wielki Kielich,
Kaskada Gaju, Zapadła Kaplica, Świątynia Stu Lian, kaskady przy mostku, bambus, kaktusy. Układ: x = u, z = v.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale, skaly  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.dzungla_pas import rosliny  # noqa: E402
from swiat.dzungla_pas.kontekst import D  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402
from swiat.las_pas import punkty as punkty_lasu  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402


# =========================================================================== małe rzeczy ruin i obozu (własny wzór)
def posag_glaz(s, rnd, pos, k=1.0, ry=0.0):
    """Posąg-głaz: omszały głaz z wyrzeźbioną twarzą (front +Z) — ciężkie brwi, jarzące się oczy (Neon), szeroki nos,
    kreska ust, czapa mchu. Kolizja tylko w głazie. Wys. ok. 3,9·k. 8 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-4, 4), ry, rnd.uniform(-5, 5))), s.uklad(skala=k):
        s.blok("Posąg głaz", (0, 1.5, 0), (3.6, 3.0, 3.0), "dz_kamien", "Slate")
        s.blok("Posąg głaz", (0, 3.25, -0.1), (3.0, 0.8, 2.6), "dz_kamien_jasny", "Slate", rot=(0, 8, 0))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Posąg brwi", (0, 2.45, 1.52), (2.8, 0.45, 0.25), "dz_kamien_ciemny")
            for sx in (-0.7, 0.7):
                s.blok("Posąg oko", (sx, 2.0, 1.52), (0.6, 0.4, 0.1), "dz_oko", "Neon")
            s.blok("Posąg nos", (0, 1.45, 1.6), (0.7, 0.8, 0.35), "dz_kamien_ciemny")
            s.blok("Posąg usta", (0, 0.85, 1.52), (1.6, 0.25, 0.1), "tusz")
            s.blok("Mech", (0.3, 3.7, 0), (2.4, 0.3, 2.0), "dz_mech", rot=(0, 20, 0))
    return 3.9 * k, 2.0 * k


def glowa_posagu(s, rnd, pos, k=1.0, ry=0.0):
    """Zwalona głowa posągu strażnika: wielki blok przewrócony na bok, płaska maska z oczodołami (bez blasku — posąg
    martwy), kikut kamiennego kaptura, mech i liść. 7 części. Wys. ok. 3,2·k."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, rnd.uniform(70, 80))), s.uklad(skala=k):
        s.blok("Posąg głowa", (1.4, 0.0, 0), (2.8, 3.0, 3.0), "dz_kamien", "Slate")
        s.blok("Posąg maska", (1.4, 0.0, 1.55), (2.4, 2.6, 0.3), "dz_kamien_jasny", "Slate")
        with s.cechy(kolizja=False, cien=False):
            for sy in (-0.6, 0.6):
                s.blok("Posąg oczodół", (1.9, sy, 1.72), (0.5, 0.6, 0.08), "tusz")
            s.klin("Posąg kaptur", (-0.4, 0.0, -0.6), (1.2, 2.0, 2.4), "dz_kamien_ciemny", "Slate")
            s.blok("Mech", (1.4, 1.55, 0), (2.2, 0.3, 2.4), "dz_mech")
            s.blok("Liana liść", (0.4, 1.2, 1.4), (1.2, 0.25, 0.8), "dz_lisc", rot=(0, 30, 20))
    return 3.2 * k, 2.2 * k


def kolumna_ruin(s, rnd, pos, k=1.0, ry=0.0, stoi=False):
    """Złamana kolumna: baza, trzon (niski albo wysoki, gdy stoi), czapa mchu, leżący bęben obok (dwa, gdy złamana).
    Kolizja w bazie i trzonie. 5–6 części."""
    x, y, z = pos
    h = (rnd.uniform(6.0, 9.0) if stoi else rnd.uniform(1.6, 2.8)) * k
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.blok("Kolumna baza", (0, 0.3 * k, 0), (2.8 * k, 0.6 * k, 2.8 * k), "dz_kamien_ciemny", "Slate")
        s.walec("Kolumna trzon", (0, 0.6 * k + h / 2.0, 0), 1.0 * k, h, "dz_kamien", "Slate", os="y",
                rot=(rnd.uniform(-3, 3), 0, rnd.uniform(-3, 3)))
        with s.cechy(kolizja=False, cien=False):
            s.walec("Kolumna mech", (0.1, 0.6 * k + h + 0.05, 0), 0.8 * k, 0.2, "dz_mech", os="y")
        with s.cechy(kolizja=False):
            s.walec("Kolumna bęben", (2.6 * k, 0.95 * k, 0.6 * k), 0.95 * k, 1.8 * k, "dz_kamien_jasny", "Slate", os="x",
                    rot=(0, rnd.uniform(-40, 40), 0))
            if not stoi:
                s.walec("Kolumna bęben", (-2.3 * k, 0.9 * k, -1.1 * k), 0.9 * k, 1.7 * k, "dz_kamien", "Slate", os="z",
                        rot=(0, rnd.uniform(-30, 30), 0))
    return 0.6 * k + h + 0.2, 3.6 * k


def kamien_ze_znakiem(s, rnd, pos, k=1.0, ry=0.0):
    """Kamień ze znakiem (stela): zwężający się kamień, jarzący się znak (Neon, romb) na froncie (+Z), mech. 4 części.
    Wys. ok. 2,8·k."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-3, 3), ry, rnd.uniform(-4, 4))), s.uklad(skala=k):
        s.blok("Stela", (0, 1.1, 0), (1.6, 2.2, 0.9), "dz_kamien", "Slate")
        s.klin("Stela", (0, 2.5, 0), (1.4, 0.6, 0.8), "dz_kamien_jasny", "Slate", rot=(0, 90, 0))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Znak", (0, 1.4, 0.47), (0.7, 0.7, 0.06), "dz_znak", "Neon", rot=(0, 0, 45))
            s.blok("Mech", (0.2, 2.25, 0), (1.2, 0.2, 0.9), "dz_mech")
    return 2.8 * k, 1.0 * k


def pochodnia(s, pos, wys=5.0):
    """Pochodnia: kij, kamienna misa, płomień (Neon) z jasnym środkiem. 4 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, 0, 4)):
        s.walec("Pochodnia kij", (0, wys / 2.0, 0), 0.25, wys, "drewno_ciemne", "Wood", os="y")
        with s.cechy(kolizja=False):
            s.walec("Pochodnia misa", (0, wys + 0.2, 0), 0.65, 0.5, "dz_kamien_ciemny", os="y")
            with s.cechy(cien=False):
                s.blok("Płomień", (0, wys + 0.85, 0), (0.8, 1.0, 0.8), "neon_ogien", "Neon", rot=(0, 45, 0))
                s.blok("Płomień", (0, wys + 0.75, 0), (0.45, 1.25, 0.45), "dz_kwiat_jarzacy", "Neon", rot=(0, 20, 0))


def stos_kokosow(s, rnd, pos):
    """Stos kokosów: cztery kokosy w kopczyku i rozłupany kokos (skorupa z jasnym wnętrzem). Bez kolizji. 6 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False):
        for px, py, pz in ((0, 0.5, 0), (0.95, 0.5, 0.3), (0.3, 0.5, -0.95), (0.45, 1.25, -0.2)):
            s.kula("Kokos", (px, py, pz), 1.0, rnd.choice(("dz_kokos", "dz_kokos", "dz_kokos_jasny")))
        with s.cechy(cien=False):
            s.walec("Kokos skorupa", (-1.3, 0.25, 0.6), 0.5, 0.5, "dz_kokos", os="y")
            s.walec("Kokos miąższ", (-1.3, 0.52, 0.6), 0.4, 0.06, "biel", os="y")
    return 1.75, 1.6


def kaktus(s, rnd, pos, k=1.0):
    """Kaktus-słup z dwoma ramionami (zapowiedź Pustyni): trzon z 2 segmentów w kontrze, ramiona z krótkiego odcinka
    w bok i pionowego w górę, różowy kwiat. Kolizja w trzonie. 7 części. Wys. ok. 6·k."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)):
        xe, ye, _ = lamana(s, "Kaktus", [(3.4 * k, 1.1 * k, zn * rnd.uniform(2, 5)), (2.6 * k, 1.0 * k, -zn * rnd.uniform(3, 6))],
                           "dz_kaktus", "SmoothPlastic", start=(0.0, -0.2))
        with s.cechy(kolizja=False):
            for q, h0, h1 in ((-1, 1.8, 2.0), (1, 2.6, 1.6)):
                x0 = q * 0.5 * k
                s.belka("Kaktus", (x0, h0 * k, 0), (q * 1.8 * k, h0 * k + 0.3, 0), 0.75 * k, "dz_kaktus", "SmoothPlastic")
                s.belka("Kaktus", (q * 1.8 * k, h0 * k - 0.2, 0), (q * 1.9 * k, (h0 + h1) * k, 0), 0.7 * k, "dz_kaktus", "SmoothPlastic")
            with s.cechy(cien=False):
                s.blok("Kwiat", (xe, ye + 0.15, 0), (0.7, 0.35, 0.7), "dz_kwiat_rozowy", rot=(0, 45, 0))
    return ye + 0.4, 2.2 * k


def mur_ruin(s, rnd, pos, k=1.0, ry=0.0):
    """Fragment muru ruin w kulisach (front +Z ku polu gry): dwa filary różnej wysokości, pęknięte nadproże opadające
    ukosem, trzy omszałe stopnie wspinające się po lewym filarze, mech, liana. Bez kolizji (kulisy). 12–13 części.
    Wys. ok. 10·k."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.uklad(skala=k), s.cechy(kolizja=False):
        s.blok("Mur ruin", (0, 0.5, 0), (11.0, 1.0, 3.0), "dz_kamien_ciemny", "Slate")
        s.blok("Mur ruin", (-3.8, 4.6, 0), (2.4, 7.4, 2.4), "dz_kamien", "Slate", rot=(0, 0, zn * 1.5))
        s.blok("Mur ruin", (3.8, 3.6, 0), (2.4, 5.4, 2.4), cien(s, "dz_kamien", 0.92), "Slate", rot=(0, 0, -zn * 2))
        s.blok("Mur ruin", (-1.0, 8.6, 0), (6.8, 1.4, 2.6), "dz_kamien_jasny", "Slate", rot=(0, 0, -11))
        for i in range(3):
            s.blok("Schody stopień", (-6.2 + 0.0 * i, 1.5 + 1.1 * i, 1.6 - 1.1 * i), (2.0, 1.1, 1.2), "dz_kamien", "Slate")
        with s.cechy(cien=False):
            s.blok("Mech", (-3.8, 8.4, 0), (2.6, 0.3, 2.6), "dz_mech")
            s.blok("Mech", (3.8, 6.4, 0), (2.6, 0.3, 2.6), "dz_mech")
            s.blok("Mech", (-6.2, 3.85, 0.0), (2.2, 0.2, 1.4), "dz_mech")
            rosliny.liana_zwis(s, rnd, (-1.0, 8.0, 1.3), 5.5, 0.3)
    return 10.0 * k, 6.0 * k


# =========================================================================== wejście
def taras_przybycia(s, K):
    """Miejsce przybycia: kamienny taras 10 × 7,6 (wierzch 0,5) z rombem światła, fugi płyt, mech, cztery niskie słupki
    z jarzącymi się znakami w narożach (mniejszy niż pomost Bagna 12 × 12: obok leży koniec Krzywej Kładki Bagna z
    palami i drobiazgami). Obok ten sam Kamień Powrotu i to samo stanowisko jajka co w lesie i Bagnie (na posadzce)."""
    m = K.miejsca["przybycie"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Wejscie/TarasPrzybycia"):
        with s.cechy(cien=False):
            s.blok("Taras płyta", (u, 0.25, v), (10.0, 0.5, 7.6), "dz_kamien", "Slate")
        with s.cechy(kolizja=False, cien=False):
            for a in (45, 135):
                s.blok("Blask", (u, 0.53, v), (0.35, 0.06, 4.0), "neon_portal", "Neon", rot=(0, a, 0))
            for dv in (-1.9, 1.9):
                s.blok("Taras fuga", (u, 0.52, v + dv), (9.6, 0.06, 0.22), "dz_kamien_ciemny")
            for du in (-2.5, 2.5):
                s.blok("Taras fuga", (u + du, 0.525, v), (0.22, 0.06, 7.2), "dz_kamien_ciemny")
            s.blok("Mech", (u - 3.6, 0.535, v + 2.6), (2.2, 0.06, 1.6), "dz_mech", rot=(0, 15, 0))
            s.blok("Mech", (u + 3.9, 0.535, v - 2.6), (1.6, 0.06, 1.6), "dz_mech", rot=(0, 40, 0))
        for du, dv in ((-4.55, -3.35), (4.55, -3.35), (-4.55, 3.35), (4.55, 3.35)):
            s.blok("Słupek", (u + du, 0.95, v + dv), (0.8, 1.3, 0.8), "dz_kamien_ciemny", "Slate")
            with s.cechy(kolizja=False, cien=False):
                s.blok("Znak", (u + du, 1.9, v + dv), (0.55, 0.55, 0.55), "dz_znak", "Neon", rot=(35, 45, 0))
    K.zajmij(u, v, 6.5)
    punkty_lasu.kamien_powrotu(s, K)
    j = K.miejsca["jajko"]
    with s.grupa("Punkty/StanowiskoJajka"), s.cechy(cien=False):
        s.blok("Posadzka", (j["u"], 0.1, j["v"]), (15.0, 0.2, 15.0), "dz_kamien_ciemny", "Slate", rot=(0, 8, 0))
    punkty_lasu.stanowisko_jajka(s, K)
    with s.grupa("Punkty/StanowiskoJajka"), s.cechy(kolizja=False):
        for k in range(4):
            a = math.radians(30 + 90 * k)
            rosliny.swiecacy_kwiat(s, rnd, (j["u"] + 9.5 * math.cos(a), 0.0, j["v"] + 9.5 * math.sin(a)), 1.2)


# =========================================================================== punkty orientacyjne
def chatka_na_drzewie(s, K):
    """Chatka na Drzewie (2084; 30): gruby pień olbrzyma z 2 segmentów (kolizja), pomost 10 × 9 na wys. 9 z balustradą
    z lian, chatka z desek z liściastym dachem, świecącym oknem i drzwiami ku polu gry, drabinka z lian do ziemi,
    korona-parasol nad wszystkim, liany. Ok. 25 wys."""
    m = K.znaki["chatka_na_drzewie"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    h0 = 9.0
    with s.grupa("Punkty/ChatkaNaDrzewie"), s.uklad(pos=(u, 0, v), obrot=(0, 180 + 5, 0)):   # front (+Z) ku polu gry
        with s.cechy(kolizja=False):
            for i in range(4):
                with s.uklad(obrot=(0, 90 * i + 20, 0)):
                    s.klin("Korzeń skrzydło", (0, 1.6, 2.0), (0.7, 3.2, 3.0), "dz_pien", "Wood", rot=(0, 180, 0))
        xe, ye, _ = lamana(s, "Pień", [(13.0, 3.2, 3.0), (9.5, 2.5, -6.0)], "dz_pien", "Wood", start=(0.0, -0.4))
        s.blok("Pomost deska", (0, h0 + 0.2, 0.6), (10.0, 0.4, 9.0), "drewno")
        with s.cechy(kolizja=False):
            for zz in (-3.0, 0.0, 3.0):
                s.blok("Kładka deska", (0, h0 + 0.42, 0.6 + zz), (9.6, 0.05, 0.3), "drewno_ciemne")
            with s.uklad(pos=(2.8, h0 + 0.4, -1.4), obrot=(0, 0, -2)):
                s.blok("Chata ściana", (0, 2.2, 0), (4.6, 4.4, 4.6), "drewno")
                s.blok("Chatka drzwi", (-0.9, 1.5, 2.35), (1.4, 3.0, 0.2), "drewno_ciemne")
                s.blok("Chatka okienko", (1.1, 2.6, 2.35), (1.1, 1.1, 0.2), "neon_okno", "Neon")
                s.dach_dwuspadowy("Dach z liści", (0, 4.4, 0), 6.0, 2.9, 2.6, 0.5, "dz_lisc", "SmoothPlastic", okap=1.2)
                s.blok("Liść olbrzym", (0.6, 7.4, 0.2), (4.6, 0.3, 3.0), "dz_lisc_jasny", rot=(0, 25, 12))
            for x in (-4.8, 4.8):                               # balustrada z lian po bokach i z przodu
                rosliny.liana(s, rnd, (x, h0 + 1.6, -3.6), (x, h0 + 1.6, 4.8), zwis=0.4, grub=0.25, liscie=1)
            rosliny.liana(s, rnd, (-4.8, h0 + 1.6, 4.8), (1.4, h0 + 1.6, 4.8), zwis=0.4, grub=0.25, liscie=1)
            for x in (-4.8, 4.8):
                for zz in (-3.6, 4.8):
                    s.blok("Słupek", (x, h0 + 1.0, zz), (0.35, 1.6, 0.35), "drewno_ciemne")
            # drabinka z lian ku polu gry (front, po prawej stronie pomostu)
            for x in (2.6, 4.0):
                s.belka("Liana", (x, 0.0, 6.4), (x, h0 + 0.4, 5.0), 0.25, "dz_liana", "SmoothPlastic")
            for i in range(7):
                s.blok("Drabina", (3.3, 0.9 + 1.2 * i, 6.3 - 0.17 * i), (1.7, 0.2, 0.3), "drewno_ciemne")
            # korona-parasol nad chatką i liany z niej
            with s.uklad(pos=(xe, ye, 0), obrot=(0, 20, 3)):
                s.blok("Korona spód", (0, 0.5, 0), (18.0, 1.8, 15.0), "dz_korona_spod")
                s.blok("Korona wierzch", (0.6, 2.0, 0.4), (12.0, 1.5, 10.0), "dz_korona_jasna", rot=(0, 30, 0))
            for x, zz, hh in ((-6.0, 3.0, 9.0), (6.5, -2.0, 11.0), (-2.0, 6.0, 7.0)):
                rosliny.liana_zwis(s, rnd, (x, ye - 0.5, zz), hh, 0.35)
    K.zajmij(u, v, 7.0)


def wielki_kielich(s, K):
    """Wielki Kielich (2296; 32): olbrzymi kwiat — gruba łodyga z 3 segmentów do 14, trzy liście-parasole u nasady,
    kielich z ośmiu czerwonych płatków z żółtymi czubkami rozchylonych w górę (14–19), złota tarcza z jarzącymi się
    pręcikami. Ok. 21 wys."""
    m = K.znaki["wielki_kielich"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Punkty/WielkiKielich"), s.uklad(pos=(u, 0, v), obrot=(0, 180, 0)):
        xe, ye, _ = lamana(s, "Łodyga kielicha", [(5.0, 1.9, 4.0), (5.0, 1.7, -7.0), (4.4, 1.5, 5.0)], ("dz_lisc_ciemny", "dz_korona"),
                           "SmoothPlastic", start=(0.0, -0.3))
        with s.cechy(kolizja=False):
            for i in range(3):
                a = 120 * i + 30
                rosliny.lisc_parasol(s, rnd, (0.6 * math.cos(math.radians(a)), 0.0, 0.6 * math.sin(math.radians(a))), 1.0, -a,
                                     wychyl=32.0, wys=5.0, prosty=True)
            with s.uklad(pos=(xe, ye, 0)):
                s.walec("Tarcza kwiatu", (0, 0.4, 0), 2.6, 0.8, "dz_kwiat_zolty", os="y")
                for i in range(8):
                    with s.uklad(obrot=(0, 45 * i + 22.5, 0)):
                        s.blok("Płatek", (3.6, 2.0, 0), (5.2, 0.45, 3.2), "dz_kwiat_czerwony", rot=(0, 0, 36))
                        with s.cechy(cien=False):
                            s.blok("Płatek", (5.7, 3.55, 0), (1.4, 0.5, 2.6), "dz_kwiat_zolty", rot=(0, 0, 36))
                with s.cechy(cien=False):
                    for i in range(5):
                        a = math.radians(72 * i)
                        s.belka("Pręcik", (0.9 * math.cos(a), 0.7, 0.9 * math.sin(a)),
                                (1.3 * math.cos(a), 2.6, 1.3 * math.sin(a)), 0.22, "dz_lisc_jasny", "SmoothPlastic")
                        s.blok("Pręcik jarzący", (1.35 * math.cos(a), 2.75, 1.35 * math.sin(a)), (0.55, 0.55, 0.55),
                               "dz_kwiat_jarzacy", "Neon", rot=(30, 45, 0))
        for i in range(4):
            a = math.radians(90 * i + 45)
            rosliny.swiecacy_kwiat(s, rnd, (4.0 * math.cos(a), 0.0, 4.0 * math.sin(a)), 1.1)
    K.zajmij(u, v, 6.0)


def kaskada_gaju(s, K):
    """Kaskada Gaju (2504; 30): omszałe urwisko z trzech bloków w prawych kulisach (do 25 wys.), z którego spada
    wodospad (jasny pas z białymi smugami, bez przezroczystości) do turkusowej sadzawki pod ścianą; piana, kamienie
    brzegu, liany z krawędzi, paprocie."""
    m = K.znaki["kaskada_gaju"]
    u, v = m["u"], m["v"]
    zn = 1 if v > 0 else -1
    rnd = K.rnd_punkty
    with s.grupa("Punkty/KaskadaGaju"), s.uklad(pos=(u, 0, v), obrot=(0, 0 if zn > 0 else 180, 0)):   # lokalne +z = ku ścianie
        for px, w, h, rr in ((-7.0, 8.0, 21.0, -3), (0.0, 7.0, 25.0, 2), (7.5, 8.5, 19.0, 4)):
            s.blok("Urwisko", (px, h / 2.0 - 1.0, 13.0), (w, h + 2.0, 9.0), "dz_kamien" if px == 0 else "dz_kamien_ciemny", "Slate",
                   rot=(0, rnd.uniform(-5, 5), rr))
            with s.cechy(kolizja=False, cien=False):
                s.blok("Urwisko mech", (px, h + 0.3, 13.0), (w + 0.6, 1.0, 9.4), "dz_mech", rot=(0, 0, rr))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Wodospad", (0.0, 12.0, 8.3), (4.6, 25.0, 0.8), "dz_woda_jasna")
            for dx in (-1.2, 0.9):
                s.blok("Wodospad pasmo", (dx, 12.0, 7.85), (0.6, 24.6, 0.15), "dz_piana")
            s.walec("Sadzawka", (0.0, 0.14, 0.5), 5.6, 0.12, "dz_woda", os="y")
            s.walec("Sadzawka", (0.0, 0.17, 4.0), 3.4, 0.12, "dz_woda_gleboka", os="y")
            for px, pz, r in ((-0.8, 7.0, 1.4), (0.9, 6.6, 1.2), (0.0, 5.8, 1.0)):
                s.kula("Piana", (px, 0.4, pz), 2 * r, "dz_piana")
            for i in range(9):
                a = math.radians(-160 + 40 * i)
                s.blok("Kamień brzegu", (6.0 * math.cos(a), 0.25, 0.5 + 6.0 * math.sin(a)), (1.4, 0.5, 1.1),
                       rnd.choice(("dz_kamien", "dz_kamien_ciemny")), rot=(0, rnd.uniform(0, 90), 0))
            for px in (-4.5, 3.2, 8.0):
                rosliny.liana_zwis(s, rnd, (px, 20.0, 8.6), rnd.uniform(8, 12), 0.35)
        with s.cechy(kolizja=False):
            for px, pz in ((-5.5, 6.5), (6.0, 7.0)):
                rosliny.paproc(s, rnd, (px, 0.0, pz), 1.1)
            rosliny.lisc_parasol(s, rnd, (-9.5, 0.0, 6.0), 1.1, 200.0, wychyl=20.0, wys=6.5)
    K.zajmij(u, v + zn * 6.0, 9.0)
    K.zajmij(u, v + zn * 14.0, 11.0)


def zapadla_kaplica(s, K):
    """Zapadła Kaplica (2664; −30): kamienny cokół, tylna i boczne ściany (prawa złamana), front z ciemnym wejściem
    i jarzącym się znakiem nad nim, dwie kolumny (jedna złamana), zapadnięty dach (jedna płyta opiera się ukosem o
    ziemię), młode drzewo na szczycie z korzeniami po ścianie, mech i liany. Ok. 17 wys. Dom Pancernika Ruin."""
    m = K.znaki["zapadla_kaplica"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Punkty/ZapadlaKaplica"), s.uklad(pos=(u, 0, v), obrot=(0, -4, 0)):       # front (+Z) ku polu gry
        s.blok("Kaplica cokół", (0, 0.6, 0), (12.0, 1.2, 10.0), "dz_kamien_ciemny", "Slate")
        s.blok("Kaplica ściana", (0, 5.6, -4.2), (10.0, 9.0, 1.2), "dz_kamien", "Slate")
        s.blok("Kaplica ściana", (-4.4, 5.2, 0), (1.2, 8.2, 8.2), cien(s, "dz_kamien", 0.93), "Slate")
        s.blok("Kaplica ściana", (4.4, 3.4, -1.0), (1.2, 4.6, 6.2), cien(s, "dz_kamien", 0.9), "Slate", rot=(0, 0, -4))
        for x in (-3.0, 3.0):
            s.blok("Kaplica ściana", (x, 4.6, 4.2), (2.6, 7.0, 1.2), "dz_kamien", "Slate")
        s.blok("Nadproże", (0, 8.6, 4.2), (9.0, 1.4, 1.5), "dz_kamien_jasny", "Slate")
        s.blok("Kaplica dach", (-1.0, 10.0, -1.0), (9.0, 1.0, 6.5), "dz_kamien_jasny", "Slate", rot=(6, 0, 3))
        s.blok("Kaplica dach", (6.4, 3.0, 1.2), (7.0, 0.9, 6.0), "dz_kamien", "Slate", rot=(0, 10, 58))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Kaplica wejście", (0, 4.0, 4.84), (3.4, 5.6, 0.1), "tusz")
            s.blok("Znak", (0, 8.6, 5.0), (1.2, 1.2, 0.1), "dz_znak", "Neon", rot=(0, 0, 45))
            for sx in (-1, 1):
                s.blok("Znak", (sx * 3.0, 6.6, 4.84), (0.5, 0.5, 0.1), "dz_znak", "Neon", rot=(0, 0, 45))
            s.blok("Mech", (-1.0, 10.6, -1.0), (7.0, 0.3, 5.0), "dz_mech", rot=(6, 0, 3))
            s.blok("Mech", (-4.4, 9.4, 0), (1.6, 0.3, 7.0), "dz_mech")
        for x in (-5.4, 5.4):
            s.walec("Kolumna trzon", (x, 1.2 + (4.0 if x < 0 else 1.6), 4.4), 0.8, 8.0 if x < 0 else 3.2, "dz_kamien_jasny", "Slate", os="y")
        with s.cechy(kolizja=False):
            s.walec("Kolumna bęben", (7.6, 0.8, 7.0), 0.8, 1.6, "dz_kamien_jasny", "Slate", os="x", rot=(0, 30, 0))
            rosliny.figowiec(s, rnd, (-1.5, 10.6, -1.5), 0.42, 30.0)
            for x, zz in ((-3.0, -4.9), (0.5, -4.9), (-5.1, 1.5)):
                s.belka("Korzeń", (x * 0.6, 10.5, zz * 0.6), (x, 1.2, zz), 0.45, "dz_pien", "Wood")
            for x, hh in ((-3.6, 6.0), (2.8, 5.0)):
                rosliny.liana_zwis(s, rnd, (x, 9.3, 5.1), hh, 0.3)
    K.zajmij(u, v, 8.5)


def posagi_straznikow(s, K):
    """Brama Posągów (u 2684–2700): dwa posągi strażników (13) w (2692; ±16) twarzą do osi — dwustopniowy cokół, krępy
    tułów z rękami wspartymi na kamiennej tarczy ze znakiem, głowa z płaską maską i jarzącymi się oczami, za głową
    wachlarz z pięciu kamiennych płatów (jak kaptur Węża Stu Lian), mech i liany; dalej ku ścianom niskie korzenie
    i kamienie ≤ 1,2."""
    rnd = K.rnd_punkty
    for zid in ("posag_lewy", "posag_prawy"):
        m = K.znaki[zid]
        u, v = m["u"], m["v"]
        ry = 0.0 if v < 0 else 180.0                          # front (+Z) ku osi
        with s.grupa("Punkty/PosagiStraznikow"), s.uklad(pos=(u, 0, v), obrot=(0, ry, 0)):
            s.blok("Posąg cokół", (0, 0.6, 0), (3.6, 1.2, 3.4), "dz_kamien_ciemny", "Slate")
            s.blok("Posąg cokół", (0, 1.5, 0), (3.2, 0.6, 3.0), "dz_kamien_jasny", "Slate")
            with s.uklad(pos=(0, 1.8, 0), obrot=(0, 0, rnd.uniform(-2, 2))):
                s.blok("Posąg tułów", (0, 2.6, -0.1), (3.0, 5.2, 2.4), "dz_kamien", "Slate")
                s.blok("Posąg tarcza", (0, 2.2, 1.25), (2.2, 2.8, 0.4), "dz_kamien_jasny", "Slate")
                for sx in (-1, 1):
                    s.blok("Posąg ręka", (sx * 1.85, 2.9, 0.4), (0.9, 3.4, 1.1), cien(s, "dz_kamien", 0.9), "Slate", rot=(-14, 0, sx * 5))
                with s.uklad(pos=(0, 5.2, 0), obrot=(rnd.uniform(-3, 3), 0, rnd.uniform(-3, 3))):
                    s.blok("Posąg głowa", (0, 1.3, -0.1), (2.6, 2.6, 2.3), "dz_kamien", "Slate")
                    s.blok("Posąg maska", (0, 1.3, 1.1), (2.4, 2.2, 0.3), "dz_kamien_jasny", "Slate")
                    for i in range(5):
                        a = -60 + 30 * i
                        with s.uklad(pos=(0, 1.6, -0.9), obrot=(0, 0, a)):
                            s.klin("Posąg kaptur", (0, 2.0, 0), (1.0, 2.6, 0.5), "dz_kamien_ciemny", "Slate", rot=(0, 180, 0))
                    with s.cechy(kolizja=False, cien=False):
                        s.blok("Posąg brwi", (0, 1.9, 1.3), (2.2, 0.35, 0.12), "dz_kamien_ciemny")
                        for sx in (-0.55, 0.55):
                            s.blok("Posąg oko", (sx, 1.45, 1.28), (0.55, 0.35, 0.1), "dz_oko", "Neon")
                        s.blok("Posąg usta", (0, 0.65, 1.28), (1.3, 0.22, 0.1), "tusz")
                        s.blok("Mech", (0.3, 2.65, -0.1), (2.2, 0.3, 2.0), "dz_mech", rot=(0, 15, 0))
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Znak", (0, 2.4, 1.48), (0.8, 0.8, 0.06), "dz_znak", "Neon", rot=(0, 0, 45))
            with s.cechy(kolizja=False):
                rosliny.liana_zwis(s, rnd, (1.3, 9.0, -0.6), 7.0, 0.3)
                rosliny.liana_zwis(s, rnd, (-1.2, 7.6, -0.4), 5.0, 0.3)
        K.zajmij(u, v, 2.6)
    t = K.przejscia["brama_posagow"]
    with s.grupa("Przejscia/BramaPosagow"):
        for zn in (-1, 1):
            for k in range(4):
                vv = zn * (20.0 + 4.4 * k + rnd.uniform(-1, 1))
                uu = (t["u_od"] + t["u_do"]) / 2.0 + rnd.uniform(-3, 3)
                if k % 2:
                    s.belka("Korzeń", (uu - 2.0, 0.1, vv), (uu + 2.0, 0.9, vv + rnd.uniform(-1, 1)), 0.9, "dz_pien", "Wood")
                else:
                    with s.cechy(kolizja=False):
                        s.blok("Kamień", (uu, 0.5, vv), (2.2, 1.0, 1.8), rnd.choice(("dz_kamien", "dz_kamien_ciemny")), "Slate",
                               rot=(rnd.uniform(-6, 6), rnd.uniform(0, 90), rnd.uniform(-6, 6)))


def swiatynia_stu_lian(s, K):
    """Świątynia Stu Lian (2788; 27): schodkowa świątynia z czterech tarasów (16 → 7 st, po 5,5 wys.) wyrastająca z
    sadzawki Kręgu, schody z klina od frontu (ku osi) z pasami stopni, na szczycie kapliczka z ciemnym wejściem,
    jarzącym się znakiem i złotym ostrosłupem, jarzący się kamień na czubku; mech na tarasach, liany. Ok. 34 wys."""
    m = K.znaki["swiatynia_stu_lian"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Punkty/SwiatyniaStuLian"), s.uklad(pos=(u, 0, v), obrot=(0, 180, 0)):        # front (+Z) ku osi pasa
        y0 = 0.0
        for i, b in enumerate((16.0, 13.0, 10.0, 7.0)):
            kol = "dz_kamien" if i % 2 == 0 else cien(s, "dz_kamien", 0.92)
            s.blok("Świątynia taras", (0, y0 + 2.75, -0.7 * i), (b, 5.5, b), kol, "Slate")
            with s.cechy(kolizja=False, cien=False):
                s.blok("Świątynia gzyms", (0, y0 + 5.55, -0.7 * i + b / 2.0 - 0.3), (b + 0.3, 0.3, 0.7), "dz_kamien_jasny")
                s.blok("Mech", (rnd.choice((-1, 1)) * b / 4.0, y0 + 5.65, -0.7 * i - b / 5.0), (b * 0.35, 0.3, b * 0.3), "dz_mech",
                       rot=(0, rnd.uniform(-10, 10), 0))
            y0 += 5.5
        s.klin("Świątynia schody", (0, 11.0, 7.4), (4.0, 22.0, 12.0), "dz_kamien_jasny", "Slate", rot=(0, 180, 0))
        with s.cechy(kolizja=False, cien=False):
            for i in range(8):
                t = (i + 0.5) / 8.0
                s.blok("Schody stopień", (0, 22.0 * (1 - t) + 0.05, 1.4 + 12.0 * t), (4.2, 0.25, 0.35), "dz_kamien_ciemny")
        with s.uklad(pos=(0, 22.0, -2.1)):
            s.blok("Kapliczka", (0, 2.8, 0), (5.2, 5.6, 5.2), "dz_kamien", "Slate")
            s.blok("Kapliczka dach", (0, 5.95, 0), (6.4, 0.7, 6.4), "dz_kamien_jasny", "Slate")
            s.ostroslup("Kapliczka szczyt", (0, 6.3, 0), 2.6, 2.6, 4.6, "dz_zloto")
            with s.cechy(kolizja=False, cien=False):
                s.blok("Kapliczka wejście", (0, 2.1, 2.62), (1.9, 3.4, 0.1), "tusz")
                s.blok("Znak", (0, 4.5, 2.66), (1.0, 1.0, 0.08), "dz_znak", "Neon", rot=(0, 0, 45))
                s.blok("Znak", (0, 11.6, 0), (1.3, 1.3, 1.3), "dz_znak", "Neon", rot=(35, 45, 0))
        with s.cechy(kolizja=False):
            for x, zz, y, hh in ((-7.8, 5.0, 5.0, 3.5), (7.8, 3.0, 5.0, 3.0), (-6.4, 3.4, 10.6, 5.0), (5.0, 2.6, 16.2, 6.0)):
                rosliny.liana_zwis(s, rnd, (x, y, zz), hh, 0.32)
    K.zajmij(u, v, 11.0)


def krag_stu_lian(s, K):
    """Krąg Stu Lian (arena Strażnika): okrągła kamienna posadzka r 27 (wierzch 0,3) — wyspa w turkusowej sadzawce,
    jaśniejszy krąg r 10 w środku i sześć fug, osiem omszałych filarów z jarzącymi się znakami na okręgu r 26 (przerwy
    na wejście i wyjście Dróżki) połączonych girlandami lian poza wejściem i wyjściem."""
    rnd = K.rnd_punkty
    a = K.straznik["arena"]
    cu, cv = a["srodek"]
    r = a["r"]
    with s.grupa("Arena/Posadzka"):
        with s.cechy(cien=False):
            s.walec("Posadzka okrągła", (cu, 0.15, cv), r + 1.0, 0.3, "dz_kamien", os="y")
        with s.cechy(kolizja=False, cien=False):
            s.walec("Posadzka okrągła", (cu, 0.33, cv), 10.0, 0.06, "dz_kamien_jasny", os="y")
            s.walec("Posadzka okrągła", (cu, 0.34, cv), 3.0, 0.06, "dz_kamien_ciemny", os="y")
            for k in range(6):
                s.blok("Fuga", (cu, 0.32, cv), (2 * r + 1.2, 0.06, 0.3), "dz_kamien_ciemny", rot=(0, 30 * k, 0))
            for k in range(7):
                aa = math.radians(rnd.uniform(0, 360))
                rr = rnd.uniform(14, 25)
                s.blok("Mech", (cu + rr * math.cos(aa), 0.335, cv + rr * math.sin(aa)), (rnd.uniform(2, 4), 0.05, rnd.uniform(1.5, 3)),
                       "dz_mech", rot=(0, rnd.uniform(0, 180), 0))
    katy = (32, 68, 112, 148, 212, 248, 292, 328)
    szczyty = {}
    with s.grupa("Arena/Krag"):
        for kat in katy:
            aa = math.radians(kat)
            mu, mv = cu + r * math.cos(aa), cv + r * math.sin(aa)
            h = rnd.uniform(7.5, 9.5)
            s.blok("Filar kręgu", (mu, 0.3 + 0.5, mv), (2.6, 1.0, 2.6), "dz_kamien_ciemny", "Slate", rot=(0, kat, 0))
            s.blok("Filar kręgu", (mu, 0.3 + 1.0 + h / 2.0, mv), (1.8, h, 1.8), "dz_kamien", "Slate", rot=(rnd.uniform(-2, 2), kat, rnd.uniform(-2, 2)))
            with s.cechy(kolizja=False, cien=False):
                s.blok("Mech", (mu, 0.3 + 1.0 + h + 0.15, mv), (2.0, 0.3, 2.0), "dz_mech", rot=(0, kat + 20, 0))
                s.blok("Znak", (mu - 0.95 * math.cos(aa), 0.3 + 1.0 + h * 0.7, mv - 0.95 * math.sin(aa)), (0.7, 0.7, 0.7), "dz_znak",
                       "Neon", rot=(0, kat + 45, 0))
            szczyty[kat] = (mu, 0.3 + 1.0 + h - 0.4, mv)
            K.zajmij(mu, mv, 2.4)
        with s.cechy(kolizja=False):
            for k1, k2 in ((32, 68), (68, 112), (112, 148), (212, 248), (248, 292), (292, 328)):
                rosliny.liana(s, rnd, szczyty[k1], szczyty[k2], zwis=rnd.uniform(1.6, 2.6), grub=0.35, liscie=2)


# =========================================================================== przejścia
def strumyk(s, K):
    """Turkusowy strumyk (u 1944–1956): kamienie brzegu i kamienie brodu (płaskie, ≤ 0,35) w polu gry, wyższe kamienie,
    paprocie i liście-parasole na brzegach tylko w kulisach (otwarcie przejścia zostaje niskie)."""
    t = K.przejscia["turkusowy_strumyk"]
    a, b = t["woda"]
    rnd = K.rnd_przejscia
    with s.grupa("Przejscia/Strumienie"):
        with s.cechy(kolizja=False, cien=False):
            for zn in (-1, 1):
                for vv in (15.0, 18.0, 21.0, 27.0, 30.0):
                    s.walec("Kamień brodu", ((a + b) / 2.0 + rnd.uniform(-1.5, 1.5), 0.17, zn * (vv + rnd.uniform(-0.6, 0.6))),
                            rnd.uniform(0.7, 1.0), 0.34, rnd.choice(("dz_kamien", "dz_kamien_jasny")), os="y")
                for uu in (a - 0.6, b + 0.6):
                    v = 9.0
                    while v < 36.0:
                        s.blok("Kamień brzegu", (uu + rnd.uniform(-0.3, 0.3), 0.2, zn * v), (rnd.uniform(0.8, 1.4), 0.4, rnd.uniform(0.8, 1.5)),
                               rnd.choice(("dz_kamien", "dz_kamien_ciemny")), rot=(0, rnd.uniform(0, 90), 0))
                        v += rnd.uniform(3.0, 5.5)
        for zn in (-1, 1):
            v = 39.0
            while v < 60.0:
                uu = rnd.choice((a - 1.2, b + 1.2)) + rnd.uniform(-0.6, 0.6)
                with s.cechy(kolizja=False):
                    if rnd.random() < 0.5:
                        rosliny.paproc(s, rnd, (uu, 0.0, zn * v), rnd.uniform(1.0, 1.4))
                    else:
                        skaly.glaz(s, rnd, (uu, 0.0, zn * v), rnd.uniform(0.5, 0.75), rnd.uniform(0, 360), "dz_kamien", "Slate",
                                   mech=True, kolizja=False)
                v += rnd.uniform(4.0, 6.0)
            with s.cechy(kolizja=False):
                rosliny.lisc_parasol(s, rnd, (b + 2.5, 0.0, zn * 41.0), 1.2, 90.0 * zn + 180.0, wychyl=25.0, wys=7.5)
        K.zajmij((a + b) / 2.0, -50.0, 8.0)
        K.zajmij((a + b) / 2.0, 50.0, 8.0)


def kaskady(s, K):
    """Kaskady przy Mostku nad Kaskadą (u 2148–2168): po obu stronach w kulisach pięć skalnych progów (1,5 → 14 wys.)
    cofających się ku tłu, z każdego spływa ku polu gry jasny pas wody, na progach turkusowe tafle, u stóp piana —
    woda zbiega do strumienia w poprzek pasa."""
    t = K.przejscia["mostek_nad_kaskada"]
    a, b = t["woda"]
    uc = (a + b) / 2.0
    rnd = K.rnd_przejscia
    with s.grupa("Przejscia/Kaskady"):
        for zn in (-1, 1):
            h_pop = 0.2
            for i, (v0, h) in enumerate(((39.0, 1.6), (44.0, 4.2), (49.0, 7.4), (54.0, 10.8), (59.0, 14.2))):
                kol = "dz_kamien" if i % 2 == 0 else "dz_kamien_ciemny"
                for du, w in ((-7.8, 7.5), (7.8, 7.5)):
                    s.blok("Skała kaskady", (uc + du + rnd.uniform(-0.4, 0.4), h / 2.0, zn * (v0 + 2.6)), (w, h, 5.4), kol, "Slate",
                           rot=(0, rnd.uniform(-3, 3), 0))
                    with s.cechy(kolizja=False, cien=False):
                        s.blok("Mech", (uc + du, h + 0.1, zn * (v0 + 2.6)), (w + 0.3, 0.25, 5.6), "dz_mech")
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Skała kaskady", (uc, h / 2.0 - 0.3, zn * (v0 + 3.0)), (8.4, h - 0.6, 4.6), "dz_kamien_ciemny", "Slate")
                    s.blok("Woda", (uc, h - 0.15, zn * (v0 + 2.6)), (7.6, 0.2, 5.2), "dz_woda")
                    s.blok("Kaskada", (uc, (h + 0.08 + h_pop) / 2.0, zn * (v0 - 0.15)), (6.6, h + 0.08 - h_pop, 0.4), "dz_woda_jasna")
                    s.blok("Kaskada", (uc + rnd.uniform(-1.5, 1.5), (h + h_pop) / 2.0, zn * (v0 - 0.4)), (0.6, h - h_pop, 0.12), "dz_piana")
                    s.blok("Piana", (uc, h_pop + 0.17, zn * (v0 - 1.55)), (7.0, 0.3, 1.4), "dz_piana")
                h_pop = h - 0.03
            with s.cechy(kolizja=False):
                for du in (-11.5, 11.5):
                    rosliny.lisc_parasol(s, rnd, (uc + du, 0.0, zn * 40.0), 1.15, 0.0 if du < 0 else 180.0, wychyl=15.0, wys=6.0)
            for vv in (41.0, 50.0, 59.0):
                K.zajmij(uc, zn * vv, 12.5)


def bambusowa_przesieka(s, K):
    """Ściany bambusa 5–6 wys. od |v| 18 do ścian i w kulisy (u 2360–2376), dwa rzędy kęp."""
    t = K.przejscia["bambusowa_przesieka"]
    rnd = K.rnd_przejscia
    o2 = t["otwarcie"][1]
    with s.grupa("Przejscia/BambusowaPrzesieka"):
        for zn in (-1, 1):
            v = o2 + 2.6
            while v < 44.0:
                for uu in (t["u_od"] + 3.5, t["u_do"] - 3.5):
                    rosliny.bambus(s, rnd, (uu + rnd.uniform(-1.2, 1.2), 0.0, zn * v), wys=rnd.uniform(5.0, 6.2), n=3, szer=2.4,
                                   ry=rnd.uniform(0, 180))
                v += rnd.uniform(4.0, 4.8)


def kamienne_schody(s, K):
    """Omszałe schody (u 2568–2584): mur ruin z omszałych bloków 6–9 wys. od |v| 14 ku ścianom i w kulisy, po froncie
    muru (od strony Gaju) pną się kamienne stopnie; w otwarciu niski kamienny próg (0,4) z rampami; przy krawędziach
    otwarcia kamienie z jarzącym się znakiem (ostrzeżenie przed Pancernikiem)."""
    t = K.przejscia["kamienne_schody"]
    rnd = K.rnd_przejscia
    o2 = t["otwarcie"][1]
    uc = (t["u_od"] + t["u_do"]) / 2.0
    with s.grupa("Przejscia/KamienneSchody"):
        for zn in (-1, 1):
            v = o2 + 0.6
            k = 0
            while v < 44.0:
                w = rnd.uniform(3.2, 4.4)
                h = rnd.uniform(6.0, 9.0) if v < 38.0 else rnd.uniform(7.0, 10.0)
                with s.cechy(kolizja=v < 39.0):
                    s.blok("Mur ruin", (uc + rnd.uniform(-0.6, 0.6), h / 2.0, zn * (v + w / 2.0)), (rnd.uniform(9.0, 11.0), h, w),
                           rnd.choice(("dz_kamien", "dz_kamien_ciemny", cien(s, "dz_kamien", 0.95))), "Slate",
                           rot=(0, rnd.uniform(-4, 4), zn * rnd.uniform(-1.5, 1.5)))
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Mech", (uc, h + 0.1, zn * (v + w / 2.0)), (9.0, 0.3, w * 0.9), "dz_mech", rot=(0, rnd.uniform(-5, 5), 0))
                    if k % 3 == 1:
                        rosliny.liana_zwis(s, rnd, (t["u_od"] + 0.6, h - 0.2, zn * (v + w / 2.0)), h * 0.7, 0.3)
                v += w * 0.96
                k += 1
            # stopnie na froncie muru (u od strony Gaju), od |v| 21 do 31, wspinają się do wierzchu muru
            with s.cechy(kolizja=False):
                for i in range(6):
                    hi = 1.1 * (i + 1)
                    s.blok("Schody stopień", (t["u_od"] - 1.2, hi / 2.0, zn * (21.0 + 1.9 * i)), (2.4, hi, 1.9),
                           "dz_kamien_jasny" if i % 2 else "dz_kamien", "Slate")
                    if i % 2 == 0:
                        with s.cechy(cien=False):
                            s.blok("Mech", (t["u_od"] - 1.2, hi + 0.05, zn * (21.0 + 1.9 * i)), (1.6, 0.06, 1.2), "dz_mech")
            # kamień ze znakiem przy krawędzi otwarcia
            with s.cechy(kolizja=False):
                kamien_ze_znakiem(s, rnd, (t["u_od"] - 1.0, 0.0, zn * (o2 + 1.8)), 0.9, -90.0)   # front ku nadchodzącym z Gaju
        # próg w otwarciu: płyta 0,4 z rampami
        with s.cechy(cien=False):
            s.blok("Schody próg", (uc, 0.2, 0.0), (8.0, 0.4, 2 * o2 - 0.6), "dz_kamien", "Slate")
            for zn in (-1, 1):
                s.klin("Schody rampa", (uc + zn * 5.0, 0.2, 0.0), (2 * o2 - 0.6, 0.4, 2.0), "dz_kamien_ciemny", "Slate",
                       rot=(0, -90 * zn, 0))
        with s.cechy(kolizja=False, cien=False):
            for vv in (-9.0, -3.0, 3.0, 9.0):
                s.blok("Mech", (uc + rnd.uniform(-2, 2), 0.43, vv + rnd.uniform(-1, 1)), (rnd.uniform(1.5, 2.5), 0.06, rnd.uniform(1.2, 2.0)),
                       "dz_mech", rot=(0, rnd.uniform(0, 90), 0))


# =========================================================================== domy potworów
def domy(s, K, Z):
    """Dom każdej strefy w punktach z planu (pod ścianą, |v| = 34): Zwijogony — nora pod liśćmi z paprocią;
    Gębokwiaty — grządka z sadzonkami i świecącym pąkiem; Kokosowi Siłacze — legowisko z liści przy ściętej palmie
    i stos kokosów; Pancernik — nora z dwóch opartych płyt obok Zapadłej Kaplicy. Niskie (plac walki ≥ 12 od węzła
    zaczyna się na wys. 1,6), stawiane przez zasady (postaw)."""
    rnd = K.rnd_domy
    for st in K.strefy:
        for i, (u, v) in enumerate(st["dom"]["pts"]):
            zn = 1 if v > 0 else -1

            def bud(st=st, u=u, v=v, zn=zn, i=i):
                with s.grupa("Domy/%s/%d" % (st["id"], i + 1)):
                    if st["potwor"] == "Zwijogon":
                        with s.cechy(kolizja=False, cien=False):
                            s.walec("Jama otwór", (u, 0.33, v + zn * 0.6), 1.3, 0.06, "tusz", os="y")
                        with s.cechy(kolizja=False):
                            for q in (-1, 0, 1):
                                s.blok("Liść olbrzym", (u + q * 1.6, 0.75, v + zn * 1.3), (2.6, 0.25, 3.6),
                                       rnd.choice(("dz_lisc", "dz_lisc_jasny")), rot=(-zn * 28, q * 25, 0))
                            rosliny.paproc(s, rnd, (u + rnd.choice((-2.4, 2.4)), 0.0, v + zn * 1.5), 0.75)
                    elif st["potwor"] == "Gębokwiat":
                        with s.cechy(kolizja=False, cien=False):
                            s.walec("Grządka", (u, 0.2, v), 2.8, 0.2, "dz_grzadka", os="y")
                        with s.cechy(kolizja=False):
                            for q in range(3):
                                a = math.radians(120 * q + rnd.uniform(-20, 20))
                                s.kula("Pąk", (u + 1.6 * math.cos(a), 0.6, v + 1.6 * math.sin(a)), 0.9, "dz_lisc_jasny")
                            s.belka("Kwiat łodyga", (u, 0.2, v), (u, 1.2, v), 0.25, "dz_liana", "SmoothPlastic")
                            with s.cechy(cien=False):
                                s.kula("Pąk jarzący", (u, 1.35, v), 0.9, "dz_kwiat_rozowy", "Neon")
                    elif st["potwor"] == "Kokosowy Siłacz":
                        with s.cechy(kolizja=False, cien=False):
                            s.walec("Legowisko", (u, 0.32, v), 2.6, 0.08, "dz_lisc_ciemny", os="y")
                        with s.cechy(kolizja=False):
                            s.walec("Pniak", (u + 2.0, 0.6, v + zn * 0.8), 0.9, 1.2, "dz_palma", "Wood", os="y")
                            s.walec("Pniak słoje", (u + 2.0, 1.22, v + zn * 0.8), 0.75, 0.06, "dz_palma_jasna", os="y")
                            stos_kokosow(s, rnd, (u - 1.6, 0.0, v + zn * 0.6))
                    else:
                        with s.cechy(kolizja=False, cien=False):
                            s.walec("Jama otwór", (u, 0.33, v + zn * 0.5), 1.4, 0.06, "tusz", os="y")
                        with s.cechy(kolizja=False):
                            for q in (-1, 1):
                                s.blok("Płyta ruin", (u + q * 1.2, 0.8, v + zn * 1.0), (2.2, 2.0, 0.6), "dz_kamien", "Slate",
                                       rot=(0, 90 + q * 30, q * 35))
                            s.blok("Mech", (u, 1.25, v + zn * 1.0), (2.0, 0.2, 1.0), "dz_mech")
            if not postaw(s, Z, bud):
                with s.grupa("Domy/%s/%d" % (st["id"], i + 1)), s.cechy(kolizja=False, cien=False):
                    s.walec("Jama otwór", (u, 0.33, v), 1.2, 0.06, "tusz", os="y")
            K.zajmij(u, v, 4.0)


# =========================================================================== rekwizyty przegród
def ozdoby(s, K, Z):
    """Rekwizyty przegród pod ścianami i w rogach kojców (miejsce: K.miejsce_ok + zasady na częściach). Zwraca liczby."""
    rnd = K.rnd_przegrody
    wynik = {}

    def rozsiej(qid, ile, r, wys, budowa, v_od=-34.0, v_do=34.0, kolizja=False, grupa=None):
        q = K.przegrody[qid]
        n = 0
        for _ in range(ile * 12):
            if n >= ile:
                break
            u = rnd.uniform(q["u_od"] + 2, q["u_do"] - 2)
            v = rnd.uniform(v_od, v_do)
            if not K.miejsce_ok(u, v, r, wys, kolizja=kolizja):
                continue

            def bud(u=u, v=v):
                with s.grupa(grupa or "Ozdoby/%s" % qid):
                    budowa(u, v)
            if postaw(s, Z, bud):
                K.zajmij(u, v, r)
                n += 1
        wynik[qid + ("/" + grupa.split("/")[-1] if grupa else "")] = n

    def kwiat_sw(u, v):
        rosliny.swiecacy_kwiat(s, rnd, (u, 0.0, v), rnd.uniform(0.9, 1.25))

    def kwiaty(u, v):
        rosliny.kepa_kwiatow(s, rnd, (u, 0.0, v), rnd.choice((("dz_kwiat_czerwony", "dz_kwiat_zolty"),
                                                             ("dz_kwiat_czerwony", "dz_kwiat_czerwony"), ("dz_kwiat_zolty", "biel"))))

    def paproc(u, v):
        rosliny.paproc(s, rnd, (u, 0.0, v), rnd.uniform(0.85, 1.2))

    def krzew(u, v):
        rosliny.krzew_dzungli(s, rnd, (u, 0.0, v), rnd.uniform(0.7, 0.95),
                              kwiat=rnd.choice((None, "dz_kwiat_czerwony", "dz_kwiat_zolty", "owoc")))

    def kloda(u, v):
        with s.cechy(kolizja=False):
            detale.kloda(s, rnd, (u, 0.0, v), rnd.uniform(0.7, 0.95))

    def glaz(u, v):
        skaly.glaz(s, rnd, (u, 0.0, v), rnd.uniform(0.6, 0.85), rnd.uniform(0, 360), "dz_kamien", "Slate", mech=True, kolizja=False)

    def posag(u, v):
        with s.cechy(kolizja=False):
            posag_glaz(s, rnd, (u, 0.0, v), rnd.uniform(0.8, 1.0), math.degrees(math.atan2(0.0, -v)) + rnd.uniform(-20, 20))

    def kokosy(u, v):
        stos_kokosow(s, rnd, (u, 0.0, v))

    def pniak_palmy(u, v):
        with s.cechy(kolizja=False):
            s.walec("Pniak", (u, 0.6, v), 0.9, 1.2, "dz_palma", "Wood", os="y", rot=(rnd.uniform(-5, 5), 0, rnd.uniform(-5, 5)))
            with s.cechy(cien=False):
                s.walec("Pniak słoje", (u, 1.22, v), 0.75, 0.06, "dz_palma_jasna", os="y")
            s.kula("Kokos", (u + 1.3, 0.45, v + 0.4), 0.9, "dz_kokos")

    def kolumna(u, v):
        kolumna_ruin(s, rnd, (u, 0.0, v), rnd.uniform(0.8, 1.0), rnd.uniform(0, 360))

    def glowa(u, v):
        glowa_posagu(s, rnd, (u, 0.0, v), rnd.uniform(0.85, 1.0), rnd.uniform(0, 360))

    def stela(u, v):
        with s.cechy(kolizja=False):
            kamien_ze_znakiem(s, rnd, (u, 0.0, v), rnd.uniform(0.8, 1.0), math.degrees(math.atan2(0.0, -v)))

    def kosc(u, v):
        detale.kosc(s, rnd, (u, 0.0, v))

    def poch(u, v):
        pochodnia(s, (u, 0.0, v), rnd.uniform(4.2, 5.2))

    def grzybki(u, v):
        detale.grzybki(s, rnd, (u, 0.0, v), rnd.choice((("dz_owoc", "biel"), ("dz_kwiat_rozowy", "biel"), ("drewno_jasne", "biel"))))

    def palma(u, v):
        rosliny.palma(s, rnd, (u, 0.0, v), rnd.uniform(0.9, 1.05), rnd.uniform(0, 360), kokosy=rnd.choice((1, 2)))

    def paproc_drz(u, v):
        rosliny.paproc_drzewiasta(s, rnd, (u, 0.0, v), rnd.uniform(0.8, 1.0), rnd.uniform(0, 360))

    def parasole(u, v):
        rosliny.kepa_parasoli(s, rnd, (u, 0.0, v), rnd.uniform(0.8, 1.0), rnd.uniform(0, 360))

    # piętro średnie w polu gry: pod ścianami, poza placami walki (palmy Gaju, paprocie drzewiaste Polany, liście Kwietnika)
    rozsiej("kokosy", 6, 2.0, 16.0, palma, v_od=-35.0, v_do=35.0, kolizja=True, grupa="Ozdoby/kokosy/Palmy")
    rozsiej("zwijogony", 5, 1.6, 9.0, paproc_drz, v_od=-35.0, v_do=35.0, kolizja=True, grupa="Ozdoby/zwijogony/PaprocieDrzewiaste")
    rozsiej("gebokwiaty", 4, 2.0, 8.0, parasole, v_od=-35.0, v_do=35.0, grupa="Ozdoby/gebokwiaty/Parasole")
    rozsiej("zwijogony", 12, 1.4, 1.3, kwiaty, v_od=-35.0, v_do=35.0, grupa="Ozdoby/zwijogony/Kwiaty")
    rozsiej("zwijogony", 10, 1.6, 1.8, paproc, v_od=-35.0, v_do=35.0, grupa="Ozdoby/zwijogony/Paprocie")
    rozsiej("zwijogony", 6, 0.8, 2.6, kwiat_sw, grupa="Ozdoby/zwijogony/Swiecace")
    rozsiej("zwijogony", 5, 2.0, 3.2, krzew, grupa="Ozdoby/zwijogony/Krzewy")
    rozsiej("zwijogony", 4, 3.5, 1.4, kloda, grupa="Ozdoby/zwijogony/Klody")
    rozsiej("zwijogony", 3, 2.2, 3.9, posag, grupa="Ozdoby/zwijogony/Posagi")
    rozsiej("gebokwiaty", 10, 1.4, 1.3, kwiaty, grupa="Ozdoby/gebokwiaty/Kwiaty")
    rozsiej("gebokwiaty", 12, 0.8, 2.6, kwiat_sw, grupa="Ozdoby/gebokwiaty/Swiecace")
    rozsiej("gebokwiaty", 6, 1.0, 1.2, grzybki, grupa="Ozdoby/gebokwiaty/Grzybki")
    rozsiej("gebokwiaty", 5, 2.0, 3.2, krzew, grupa="Ozdoby/gebokwiaty/Krzewy")
    rozsiej("kokosy", 7, 1.8, 1.75, kokosy, v_od=-35.0, v_do=35.0, grupa="Ozdoby/kokosy/Kokosy")
    rozsiej("kokosy", 5, 1.6, 1.3, pniak_palmy, grupa="Ozdoby/kokosy/Pniaki")
    rozsiej("kokosy", 6, 2.0, 3.2, krzew, grupa="Ozdoby/kokosy/Krzewy")
    rozsiej("kokosy", 6, 1.6, 1.8, paproc, grupa="Ozdoby/kokosy/Paprocie")
    rozsiej("kokosy", 4, 1.6, 1.4, glaz, grupa="Ozdoby/kokosy/Glazy")
    rozsiej("kokosy", 4, 0.8, 2.6, kwiat_sw, grupa="Ozdoby/kokosy/Swiecace")
    rozsiej("ruiny", 6, 3.6, 3.6, kolumna, kolizja=True, grupa="Ozdoby/ruiny/Kolumny")
    rozsiej("ruiny", 2, 2.4, 3.2, glowa, grupa="Ozdoby/ruiny/Glowy")
    rozsiej("ruiny", 3, 1.2, 2.8, stela, grupa="Ozdoby/ruiny/Stele")
    rozsiej("ruiny", 6, 1.6, 1.8, paproc, grupa="Ozdoby/ruiny/Paprocie")
    rozsiej("ruiny", 5, 0.8, 2.6, kwiat_sw, grupa="Ozdoby/ruiny/Swiecace")
    rozsiej("ruiny", 5, 1.0, 0.6, kosc, grupa="Ozdoby/ruiny/Kosci")
    rozsiej("ruiny", 2, 1.0, 6.5, poch, grupa="Ozdoby/ruiny/Pochodnie")
    rozsiej("wejscie", 8, 1.4, 1.3, kwiaty, v_od=-35.0, v_do=35.0, grupa="Ozdoby/wejscie/Kwiaty")
    rozsiej("wejscie", 3, 1.0, 6.5, poch, grupa="Ozdoby/wejscie/Pochodnie")
    rozsiej("wejscie", 4, 0.8, 2.6, kwiat_sw, grupa="Ozdoby/wejscie/Swiecace")
    rozsiej("krag", 6, 0.8, 2.6, kwiat_sw, grupa="Ozdoby/krag/Swiecace")
    return wynik


def parasole_nad_sciezka(s, K, Z):
    """Liście-parasole nad Dróżką: łodyga stoi obok Dróżki (|dv| 6,5–8), wychyla się ku niej, liść wisi nad nią wyżej
    niż 7 (zasada ścieżki: nic na wys. 0,6–7 na Dróżce). Tylko tam, gdzie nie ma placów walki (zasada placu odrzuca
    resztę) i przelot kamery jest wysoko. Zwraca liczbę."""
    from swiat.dzungla_pas.kontekst import ODCINKI_SCIEZKI, v_sciezki
    rnd = K.rnd_parasole
    n = 0
    for a, b in ODCINKI_SCIEZKI:
        u = a + rnd.uniform(2, 6)
        zn = 1
        while u < b - 2:
            postawiony = False
            for strona in (-zn, zn):
                v = v_sciezki(u) + strona * rnd.uniform(6.6, 8.0)
                if abs(v) > 34.0 or not K.miejsce_ok(u, v, 1.0, 1.6, sciezka_zapas=1.6, otwarcia=True):
                    continue

                def bud(u=u, v=v, strona=strona):
                    with s.grupa("Ozdoby/Parasole"):
                        rosliny.lisc_parasol(s, rnd, (u, 0.0, v), rnd.uniform(1.15, 1.35), 90.0 * strona + rnd.uniform(-12, 12),
                                             wychyl=rnd.uniform(20, 26), wys=rnd.uniform(11.6, 12.8))
                if postaw(s, Z, bud):
                    K.zajmij(u, v, 1.2)
                    n += 1
                    zn = strona
                    postawiony = True
                    break
            u += rnd.uniform(11.0, 16.0) if postawiony else 1.5
    return n


def przedbramie(s, K):
    """Przedbramie (strefa spokoju): ławka, pochodnie, skrzynie, tabliczka „wkrótce Pustynia” (tekst wypisuje gra)."""
    rnd = K.rnd_przegrody
    with s.grupa("Przedbramie"):
        zestaw.lawka(s, (1862.0 + D, 0.0, -24.0), ry=90.0, dl=6.0)
        pochodnia(s, (1866.0 + D, 0.0, -28.0), 5.2)
        pochodnia(s, (1858.0 + D, 0.0, 26.0), 4.8)
        zestaw.skrzynia(s, (1860.0 + D, 0.0, 28.0), ry=20.0, dl=3.2, a=2.6)
        zestaw.skrzynia(s, (1859.0 + D, 0.0, 31.6), ry=-12.0, dl=2.6, a=2.2)
        detale.tabliczka(s, rnd, (1868.0 + D, 0.0, -12.0), 90.0, "laka")
        stos_kokosow(s, rnd, (1864.0 + D, 0.0, -31.0))
    for u, v in ((1862.0, -24.0), (1866.0, -28.0), (1858.0, 26.0), (1860.0, 28.0), (1859.0, 31.6), (1868.0, -12.0), (1864.0, -31.0)):
        K.zajmij(u + D, v, 2.5)


# =========================================================================== brama do Pustyni i zapowiedź
def brama_pustyni(s, K):
    """Brama do Pustyni (u 2814): mur ruin z omszałych bloków ok. 10 wys. przez cały pas (aż w kulisy), oplątany lianami;
    przy wrotach dwa filary 14,6 z nadprożem i jarzącym się znakiem słońca (zapowiedź Pustyni), pochodnie; wrota 16 szer.
    to OSOBNA grupa „BramaPustyni/Wrota” (skrzydła z desek przewiązane bambusem, z kolizją, łańcuch, kłódka) — jak brama
    do Dżungli w Bagnie."""
    m = K.miejsca["brama_pustyni"]
    u = m["u"]
    o1, o2 = m["otwarcie"]
    pol = (o2 - o1) / 2.0
    rnd = K.rnd_punkty
    with s.grupa("BramaPustyni/Palisada"):
        for zn in (-1, 1):
            v = pol + 2.4
            k = 0
            gory = []
            while v < 45.0:
                w = rnd.uniform(3.0, 3.8)
                h = rnd.uniform(8.6, 11.0)
                s.blok("Mur bramy", (u + rnd.uniform(-0.2, 0.2), h / 2.0 - 0.4, zn * (v + w / 2.0)), (2.2, h + 0.8, w + 0.1),
                       rnd.choice(("dz_kamien", "dz_kamien_ciemny", cien(s, "dz_kamien", 0.95))), "Slate",
                       rot=(0, rnd.uniform(-2, 2), rnd.uniform(-1.5, 1.5)))
                with s.cechy(kolizja=False, cien=False):
                    if k % 2 == 0:
                        s.blok("Mech", (u, h - 0.3, zn * (v + w / 2.0)), (2.4, 0.3, w * 0.9), "dz_mech")
                gory.append((u - 1.2, h - 1.2, zn * (v + w / 2.0)))
                v += w * 0.97
                k += 1
            with s.cechy(kolizja=False):
                for p1, p2 in zip(gory[::2], gory[1::2]):
                    rosliny.liana(s, rnd, p1, p2, zwis=rnd.uniform(1.5, 3.0), grub=0.4, liscie=1)
                for i in range(0, len(gory), 3):
                    s.blok("Liść olbrzym", (u - 1.4, gory[i][1] - 1.0, gory[i][2]), (0.3, 2.4, 3.8),
                           rnd.choice(("dz_lisc", "dz_lisc_jasny")), rot=(rnd.uniform(-20, 20), 0, rnd.uniform(30, 60)))
            s.blok("Filar bramy", (u, 7.3, zn * (pol + 1.2)), (3.0, 14.6, 2.4), "dz_kamien_jasny", "Slate")
            with s.cechy(kolizja=False):
                s.blok("Filar bramy", (u, 14.9, zn * (pol + 1.2)), (3.6, 0.8, 3.0), "dz_kamien", "Slate")
                pochodnia(s, (u - 2.0, 0.0, zn * (pol + 1.9)), 5.6)
                with s.cechy(cien=False):
                    s.blok("Znak", (u - 1.55, 9.5, zn * (pol + 1.2)), (0.1, 0.9, 0.9), "dz_znak", "Neon", rot=(45, 0, 0))
        with s.cechy(kolizja=False):
            s.blok("Nadproże", (u, 13.6, 0.0), (2.6, 1.8, 2 * pol + 5.4), "dz_kamien", "Slate", rot=(rnd.uniform(-1, 1), 0, 0))
            with s.cechy(cien=False):
                s.blok("Mech", (u, 14.6, 1.5), (2.8, 0.3, 8.0), "dz_mech")
                s.blok("Znak słońca", (u - 1.36, 13.6, 0.0), (0.1, 1.5, 1.5), "neon_okno", "Neon", rot=(45, 0, 0))
                for i in range(8):
                    a = math.radians(45 * i)
                    s.blok("Znak słońca", (u - 1.35, 13.6 + 1.4 * math.sin(a), 1.4 * math.cos(a)), (0.08, 0.35, 0.35), "neon_okno", "Neon",
                           rot=(45, 0, 0))
            for zz in (-3.0, 0.5, 3.6):
                rosliny.liana_zwis(s, rnd, (u - 1.0, 12.7, zz), rnd.uniform(2.0, 3.5), 0.3)
    with s.grupa("BramaPustyni/Wrota"):
        for zn in (-1, 1):
            c = zn * (pol - 0.05) / 2.0
            s.blok("Wrota belka", (u, 4.7, c), (0.8, 9.4, pol - 0.15), "drewno", "WoodPlanks")
            with s.cechy(kolizja=False):
                for y in (2.2, 7.2):
                    s.walec("Bambus", (u - 0.6, y, c), 0.3, pol - 0.3, "dz_bambus", "Wood", os="z")
                s.belka("Wrota belka", (u - 0.6, 2.4, zn * 0.6), (u - 0.6, 7.0, zn * (pol - 0.5)), 0.35, "drewno_ciemne",
                        "SmoothPlastic", 0.8)
                with s.cechy(cien=False):
                    s.blok("Szczelina", (u - 0.42, 4.7, zn * pol / 2.0), (0.1, 8.8, 0.25), "tusz")
        with s.cechy(kolizja=False):
            for k, vv in enumerate((-2.7, -0.9, 0.9, 2.7)):
                s.blok("Łańcuch", (u - 0.75, 5.0 - 0.35 * math.cos(vv), vv), (0.5, 0.55, 1.9), "metal_ciemny",
                       rot=(0 if k % 2 else 90, 0, 0))
            s.blok("Kłódka", (u - 1.0, 4.0, 0.0), (0.9, 2.8, 2.6), "zloto")
            s.blok("Kłódka kabłąk", (u - 1.0, 5.9, 0.0), (0.4, 1.3, 1.6), "metal_ciemny")
            with s.cechy(cien=False):
                s.blok("Kłódka dziurka", (u - 1.5, 3.7, 0.0), (0.1, 1.1, 0.55), "tusz")
    K.zajmij(u, 0, pol + 2)


def zapowiedz_pustyni(s, K, Z):
    """Za bramą (u 2816–2846, osobna grupa ZapowiedzPustyni — do usunięcia, gdy powstanie Pustynia): piasek, niskie
    wydmy z klinów, kaktusy-słupy, piaskowe głazy, sucha trawa, wybielona czaszka i kości, samotna palma oazy;
    niewidzialna ściana na u 2845, żeby przez wrota nie było widać pustki. Tabliczkę „PUSTYNIA — WKRÓTCE” wypisuje gra."""
    rnd = K.rnd_pustynia
    with s.grupa("ZapowiedzPustyni"):
        with s.cechy(kolizja=False, cien=False):
            s.blok("Plama piasku", (1891.0 + D, 0.09, 0.0), (29.0, 0.1, 120.0), "dz_piasek")
            s.blok("Plama piasku", (1891.0 + D, 0.12, 0.0), (29.0, 0.1, 8.0), "dz_droga_pustyni")
        for u, v, k, h in ((1888.0, -20.0, 1.0, 1.2), (1896.0, 14.0, 1.3, 1.4), (1899.0, -36.0, 2.2, 4.0), (1893.0, 42.0, 2.6, 5.0),
                           (1886.0, 30.0, 1.6, 1.4), (1900.0, 52.0, 3.0, 6.0), (1897.0, -52.0, 3.0, 6.0), (1902.0, -6.0, 1.6, 1.3)):
            def bud(u=u, v=v, k=k, h=h):
                with s.cechy(kolizja=False, cien=False):
                    with s.uklad(pos=(u + D, 0.0, v), obrot=(0, rnd.uniform(-25, 25) + (90 if v > 0 else -90), 0)):
                        s.klin("Wydma", (0, h / 2.0, -2.0 * k), (6.0 * k, h, 4.0 * k), "dz_piasek")
                        s.klin("Wydma", (0, h / 2.0, 2.0 * k), (6.0 * k, h, 4.0 * k), cien(s, "dz_piasek", 0.92), rot=(0, 180, 0))
            postaw(s, Z, bud)
        for u, v, k in ((1885.0, -27.0, 1.1), (1894.0, 24.0, 1.3), (1901.0, -14.0, 0.9), (1890.0, 36.0, 1.5), (1898.0, -42.0, 1.6)):
            def bud(u=u, v=v, k=k):
                kaktus(s, rnd, (u + D, 0.0, v), k)
            postaw(s, Z, bud)
        for u, v in ((1889.0, 10.0), (1895.0, -30.0)):
            def bud(u=u, v=v):
                skaly.glaz(s, rnd, (u + D, 0.0, v), rnd.uniform(0.6, 0.8), rnd.uniform(0, 360), "dz_ochra", mech=False, kolizja=False)
            postaw(s, Z, bud)

        def bud_palma():
            rosliny.palma(s, rnd, (1900.0 + D, 0.0, 26.0), 1.1, rnd.uniform(0, 360), kokosy=1)
        postaw(s, Z, bud_palma)
        with s.cechy(kolizja=False, cien=False):
            for q in range(10):
                detale.kepka(s, rnd, (rnd.uniform(1879, 1903) + D, 0.1, rnd.choice((-1, 1)) * rnd.uniform(6, 34)),
                             ("trawa_sucha", "dz_droga_pustyni", "dz_ochra"), k=rnd.uniform(0.8, 1.2))
        with s.cechy(kolizja=False):
            detale.czaszka(s, rnd, (1887.0 + D, 0.0, -9.0), 60.0)
            for q in range(3):
                detale.kosc(s, rnd, (1887.0 + D + rnd.uniform(-2, 2), 0.0, -9.0 + rnd.uniform(-2.5, 2.5)))
        with s.cechy(cien=False):
            s.blok("Niewidzialna ściana", (1905.0 + D, 40.0, 0.0), (2.0, 80.0, 120.0), "biel", alfa=1.0)
