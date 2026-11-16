# -*- coding: utf-8 -*-
"""Punkty orientacyjne i miejsca z planu pasa (grupy „Punkty/<Nazwa>” — w Studio ModelStreamingMode = Persistent) oraz
Brama do Bagna (osobne grupy „BramaBagna/Palisada” i „BramaBagna/Wrota” — skrypt otwiera same wrota dla gracza).

Bryły wzorowane na lokacjach starego lasu (swiat/biom_las/lokacje), przeskalowane do wymiarów z plan_pasa.json:
Brama Pniaków i Kamień Powrotu (laka.py), stanowisko jajka (gniazdo z serce.py), Wielki Kapelusz (kapeluszowo.py),
Wilcza Skała (ostepy.py), głazy legowiska z kotłem (wawoz.py), filar z kryształem i krąg menhirów (korona.py), wrota
(ostepy.wrota_bagna). Funkcje starych lokacji budują w stałych miejscach starego lasu (ogniska, drogowskazy do jego
podbiomów), więc tu składamy te same prymitywy (rosliny, skaly, wspolne, zestaw) od nowa. Układ: x = u, z = v.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import skaly  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402


def brama_pniakow(s, K):
    """Dwa pnie (v ±10, ok. 22 wys.) kłaniają się sobie nad drogą za plecami przybywającego; lina z lampionem,
    chorągiewki duetu. Niższe niż w starym lesie: nad bramą startuje przelot kamery (28 nad gruntem)."""
    m = K.znaki["pien_lewy"]
    u = m["u"]
    rv = abs(m["v"])
    with s.grupa("Punkty/BramaPniakow"), s.uklad(pos=(u, 0, 0), obrot=(0, 90, 0)):   # lokalne x = −v, z = +u
        for zn in (-1, 1):
            with s.uklad(pos=(zn * rv, 0, 0)):
                xe, ye, _ = lamana(s, "Pień bramy", [(7.0, 3.4, zn * 5), (6.0, 2.9, zn * 8), (5.0, 2.4, zn * 10)],
                                   "drewno", "Wood", start=(0.0, -0.6))
                s.blok("Pień bramy korzeń", (zn * 2.0, 0.8, 1.3), (3.4, 1.9, 2.6), "drewno_ciemne", rot=(0, 30 * zn, zn * 20))
                s.blok("Pień bramy korzeń", (zn * 1.2, 0.7, -1.6), (2.8, 1.6, 2.2), "drewno_ciemne", rot=(0, -40 * zn, zn * 16))
                with s.cechy(kolizja=False):
                    s.blok("Czapa", (xe - zn * 0.8, ye + 1.2, 0), (7.6, 3.4, 6.8), "lisc_ciemny", rot=(6, 20 * zn, -zn * 8))
                    s.blok("Czapa", (xe - zn * 0.3, ye + 3.5, 0.3), (5.0, 2.6, 4.6), "lisc", rot=(0, 45, zn * 6))
                    s.blok("Czapa wierzch", (xe, ye + 5.2, -0.3), (3.0, 1.8, 2.8), "lisc_jasny", rot=(0, 15, 0))
                with s.cechy(kolizja=False, cien=False):
                    s.blok("Pnie tusz", (0, 0.12, 0), (4.4, 0.3, 4.4), "tusz")
        with s.cechy(kolizja=False):
            s.belka("Lina", (-6.4, 16.4, 0), (0, 15.4, 0), 0.45, "drewno_ciemne", "SmoothPlastic")
            s.belka("Lina", (0, 15.4, 0), (6.4, 16.4, 0), 0.45, "drewno_ciemne", "SmoothPlastic")
            s.blok("Lampion łańcuch", (0, 14.4, 0), (0.3, 2.0, 0.3), "metal_ciemny")
            s.blok("Lampion", (0, 12.6, 0), (1.5, 2.0, 1.5), "neon_okno", "Neon", rot=(0, 45, 0))
            s.blok("Lampion daszek", (0, 13.8, 0), (2.2, 0.5, 2.2), "dach_karczma", rot=(0, 45, 0))
        zestaw.choragiewka_duetu(s, (-8.0, 9.5, 1.1), "rycerz", ry=0, przechyl=-12)
        zestaw.choragiewka_duetu(s, (8.0, 9.5, 1.1), "kot", ry=180, przechyl=-12)
    for zn in (-1, 1):
        K.zajmij(u, zn * rv, 4.0)


def kamien_powrotu(s, K):
    """Kamień Powrotu (E → miasteczko): omszały głaz z rombem światła zwróconym do ścieżki; obok ognisko."""
    m = K.miejsca["kamien_powrotu"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    zn = 1 if v < 0 else -1                                    # strona ścieżki
    with s.grupa("Punkty/KamienPowrotu"):
        skaly.glaz(s, rnd, (u, 0, v), 1.3, 0.0, "kamien_cieply", mech=True)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Kamień Powrotu romb", (u, 3.1, v + zn * 3.35), (1.7, 1.7, 0.4), "neon_portal", "Neon", rot=(0, 0, 45))
        wspolne.punkt_e(s, "Punkty/KamienPowrotu", (u + 0.5, 0, v + zn * 5.5))
    wspolne.ognisko(s, rnd, (u + 11.0, 0, v - zn * 5.0))     # grupa „Piny/Ogniska” (wspolne.ognisko)
    K.zajmij(u, v, 4.6)
    K.zajmij(u + 11.0, v - zn * 5.0, 3.0)


def stanowisko_jajka(s, K):
    """Samo miejsce na jajko peta (D-060, D-076, D-086): kamienny podest 12 × 12, gniazdo z korzeni z mchem (puste —
    jajko stawia skrypt), punkt E od strony ścieżki, trzy wiaderka farby (farbowanie) i lampion."""
    m = K.miejsca["jajko"]
    u, v = m["u"], m["v"]
    zn = 1 if v < 0 else -1                                    # w stronę ścieżki
    rnd = K.rnd_punkty
    with s.grupa("Punkty/StanowiskoJajka"), s.uklad(pos=(u, 0, v), obrot=(0, 8, 0)):
        s.blok("Płyta kamienna", (0, 0.25, 0), (12.0, 0.5, 12.0), "kamien_cieply")
        with s.cechy(kolizja=False, cien=False):
            s.blok("Krawężnik", (0, 0.12, 0), (12.8, 0.3, 12.8), "tusz")
        for k in range(6):
            a = math.radians(k * 60 + 15)
            s.blok("Korzeń gniazda", (3.2 * math.cos(a), 1.15, 3.2 * math.sin(a)), (3.6, 1.3, 1.4), "drewno_ciemne", "Wood",
                   rot=(0, -math.degrees(a) + 90, rnd.uniform(-12, 12)))
        s.walec("Gniazdo dno", (0, 0.65, 0), 2.6, 0.3, "drewno", os="y")
        with s.cechy(kolizja=False, cien=False):
            s.walec("Mech", (0, 0.84, 0), 2.2, 0.12, "mech", os="y")
            for i, (x, z, kol) in enumerate(((4.3, -zn * 3.9, "czerwien"), (3.1, -zn * 4.6, "zloto"), (4.6, -zn * 2.3, "dach_twierdza"))):
                s.walec("Wiaderko", (x, 1.1, z), 0.7, 1.2, kol, os="y", rot=(0, 0, 0))
                s.blok("Kropka", (x - 0.9 - 0.3 * i, 0.53, z + zn * 0.6), (0.9, 0.06, 0.7), kol, rot=(0, 25 * i, 0))
        wspolne.lampion(s, (-5.0, 0.5, -zn * 4.8), 5.0)
        wspolne.punkt_e(s, "Punkty/StanowiskoJajka", (0.0, 0.5, zn * 4.2))
    K.zajmij(u, v, 8.6)


def krag_przybycia(s, K):
    """Miejsce przybycia teleportem: płaski kamienny krąg z rombem światła na ścieżce i krąg grzybków wokół (z boków
    ścieżki — nic nie wchodzi w drogę)."""
    from swiat.biom_las.detale import grzybki
    m = K.miejsca["przybycie"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Polana/KragPrzybycia"):
        with s.cechy(cien=False):
            s.walec("Płyta kamienna", (u, 0.26, v), 3.4, 0.2, "kamien_cieply", os="y")
        with s.cechy(kolizja=False, cien=False):
            for a in (45, 135):
                s.blok("Blask", (u, 0.39, v), (0.35, 0.06, 3.6), "neon_portal", "Neon", rot=(0, a, 0))
            for a in (60, 90, 120, 240, 270, 300):
                r = 7.6
                grzybki(s, rnd, (u + r * math.cos(math.radians(a)), 0.0, v + r * math.sin(math.radians(a))),
                        rnd.choice((("czerwien", "biel"), ("biel", "tynk_krem"), ("dach_sklep", "biel"))))
    K.zajmij(u, v, 4.0)


def pasnik(s, K):
    """Paśnik-wieża z galaretą (Zagroda, ok. 16 wys.): cztery pochylone słupy, pomost, beczka pełna galarety, która się
    przelewa i kapie, drabinka od strony ścieżki."""
    m = K.znaki["pasnik"]
    u, v = m["u"], m["v"]
    zn = 1 if v < 0 else -1
    with s.grupa("Punkty/Pasnik"), s.uklad(pos=(u, 0, v + 0.5 * (-zn)), obrot=(0, 12, 0)):
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.belka("Słup", (sx * 2.4, -0.3, sz * 2.4), (sx * 1.8, 11.0, sz * 1.8), 0.8, "drewno", "Wood")
        with s.cechy(kolizja=False):
            s.belka("Płot żerdź", (-2.3, 1.5, 2.3), (2.0, 8.5, 2.0), 0.45, "drewno_ciemne", "SmoothPlastic")
            s.belka("Płot żerdź", (2.3, 1.5, -2.3), (-2.0, 8.5, -2.0), 0.45, "drewno_ciemne", "SmoothPlastic")
            for x in (-0.7, 0.7):                              # drabinka od strony ścieżki
                s.belka("Płot żerdź", (x, 0.0, zn * 3.4), (x, 11.0, zn * 2.2), 0.3, "drewno_ciemne", "SmoothPlastic")
            for k in range(4):
                y = 2.2 + 2.3 * k
                zz = zn * (3.4 - 1.2 * y / 11.0)
                s.blok("Płot żerdź", (0, y, zz), (1.7, 0.25, 0.3), "drewno_jasne")
        s.blok("Pomost deska", (0, 11.2, 0), (5.6, 0.5, 5.6), "drewno_jasne", rot=(0, 0, 2))
        s.walec("Beczka", (0, 12.75, 0), 2.1, 2.6, "drewno", os="y")
        with s.cechy(kolizja=False):
            for y in (12.0, 13.6):
                s.walec("Beczka obręcz", (0, y, 0), 2.35, 0.4, "metal_ciemny", os="y")
            s.blok("Galareta", (0, 14.6, 0), (5.0, 2.0, 5.0), "galareta", rot=(6, 20, 8))
            s.blok("Galareta", (0.5, 16.0, -0.3), (3.4, 1.8, 3.4), "galareta", rot=(-8, 50, 4))
            s.blok("Galareta", (-0.2, 17.1, 0.2), (1.8, 1.2, 1.8), "galareta", rot=(10, 10, 12))
            s.blok("Galareta", (2.3, 12.6, 0.7), (0.8, 3.0, 1.1), "galareta", rot=(0, 0, -6))
            s.blok("Galareta", (-2.2, 12.2, -1.0), (0.7, 2.4, 0.9), "galareta", rot=(0, 0, 5))
            s.blok("Galareta", (-1.3, 10.6, zn * 2.1), (0.6, 1.8, 0.6), "galareta")
            with s.cechy(cien=False):
                s.blok("Bąbel", (1.2, 15.8, 1.3), (0.8, 0.8, 0.8), "biel", rot=(0, 30, 0))
                s.blok("Bąbel", (-1.0, 16.4, 0.9), (0.6, 0.6, 0.6), "biel", rot=(0, 60, 0))
                s.walec("Kałuża galarety", (2.6, 0.12, 1.4), 1.6, 0.2, "galareta", os="y")
    K.zajmij(u, v, 4.2)


def wielki_kapelusz(s, K):
    """Wielki Kapelusz (Lasek, ok. 30 wys.): trzon z trzech walców w kontrze, kapelusz r 12 przekrzywiony zawadiacko
    (spód na ok. 20 — nad placami walki, które sięgają do 18), kropki, lampiony zarodników u stopy."""
    m = K.znaki["wielki_kapelusz"]
    u, v = m["u"], m["v"]
    zn = 1 if v < 0 else -1
    with s.grupa("Punkty/WielkiKapelusz"), s.uklad(pos=(u, 0, v - zn * 0.5)):
        segs = [(8.0, 3.4, 4.0), (8.0, 3.0, -7.0), (6.5, 2.6, 6.0)]
        y0, x0, kat = 0.0, 0.0, 0.0
        for dl, r, k in segs:
            kat += k
            a = math.radians(kat)
            cx, cy = x0 - math.sin(a) * dl / 2.0, y0 + math.cos(a) * dl / 2.0
            s.walec("Trzon", (cx, cy, 0), r, dl + 1.2, "tynk_krem", os="y", rot=(0, 0, kat))
            x0, y0 = x0 - math.sin(a) * dl, y0 + math.cos(a) * dl
        with s.uklad(pos=(x0, y0 - 0.2, 0), obrot=(-zn * 7, 20, -6)):  # spód kapelusza unosi się nad polem gry
            s.walec("Kapelusz spód", (0, -0.2, 0), 12.5, 0.5, "tusz", os="y")
            s.walec("Kapelusz", (0, 1.6, 0), 12.0, 3.4, "czerwien", os="y")
            s.walec("Kapelusz czubek", (0.8, 4.3, 0), 8.0, 2.4, "czerwien", os="y")
            s.walec("Kapelusz szczyt", (1.2, 6.0, 0.3), 4.0, 1.4, "czerwien", os="y")
            with s.cechy(kolizja=False, cien=False):
                for k in range(8):
                    a = math.radians(k * 45 + 10)
                    r = 9.6 if k % 2 else 5.8
                    s.blok("Kropka", (0.6 + r * math.cos(a), 3.35 if r > 8 else 5.55, r * math.sin(a)), (2.4, 0.4, 2.4), "biel",
                           rot=(0, k * 23, 0))
    with s.grupa("Lasek/WielkiKapelusz"):
        for k, a in enumerate((200, 330)):
            aa = math.radians(a)
            wspolne.lampion(s, (u + 6.5 * math.cos(aa), 0, v + 6.5 * math.sin(aa)), 5.0, "neon_zarodnik")
    K.zajmij(u, v, 5.0)
    K.zajmij(u, v - zn * 10.0, 14.0)                         # pod kapeluszem i obok niego żadnych drzew kulis


def wilcza_skala(s, K):
    """Wilcza Skała (Zarośla, ok. 30 wys.): łupkowa iglica z trzech brył zwężających się ku górze, każda przechylona
    mocniej, wilcze ucho z klina narożnego, jasny rant od słońca (zachód, −u), bursztynowe oczy patrzą na ścieżkę."""
    m = K.znaki["wilcza_skala"]
    u, v = m["u"], m["v"]
    zn = 1 if v > 0 else -1                                   # na zewnątrz pasa
    with s.grupa("Punkty/WilczaSkala"), s.uklad(pos=(u, 0, v + zn * 3.5), obrot=(0, 0 if zn > 0 else 180, 0)):
        # lokalne +z = na zewnątrz pasa, −z = ku ścieżce
        with s.uklad(obrot=(4, 0, 0)):
            s.blok("Skała", (0, 5.5, 0), (9.0, 13.0, 13.0), "kamien_lochu", "Slate")
            with s.cechy(kolizja=False):
                s.blok("Rant", (-4.65 * zn, 5.5, 0), (0.4, 11.5, 13.1), "kamien_cieply", "Slate")
            with s.uklad(pos=(0.6 * zn, 12.0, 0.8), obrot=(-5, 12, 7)):
                s.blok("Skała", (0, 4.75, 0), (7.0, 9.5, 9.5), "kamien_lochu", "Slate")
                with s.cechy(kolizja=False):
                    s.blok("Rant", (-3.65 * zn, 4.75, 0), (0.4, 8.5, 9.6), "kamien_cieply", "Slate")
                    with s.cechy(cien=False):
                        for xx in (-1.6, 1.6):
                            s.blok("Oko", (xx, 6.4, -4.85), (2.0, 0.7, 0.35), "neon_okno", "Neon", rot=(0, 0, -xx * 5))
                with s.uklad(pos=(-0.4 * zn, 9.5, 0.3), obrot=(4, -10, -8)):
                    s.blok("Skała", (0, 3.5, 0), (5.0, 7.0, 6.5), "kamien_lochu", "Slate")
                    s.naroznik("Wilcze ucho", (0, 8.4, 0), (4.6, 3.4, 5.0), "kamien_lochu", "Slate", rot=(0, 90, 0))
                    with s.cechy(kolizja=False):
                        s.blok("Rant", (-2.65 * zn, 3.5, 0), (0.4, 6.0, 6.6), "kamien_cieply", "Slate")
    K.zajmij(u, v + zn * 3.5, 7.5)


def glazy_legowiska(s, K):
    """Głazy legowiska z kotłem (Leże Trolla, ok. 20 wys.): stos trzech głazów w kontrze z czapami mchu i kocioł z zupą
    z galarety na ogniu, z dymem — przed stosem, od strony ścieżki."""
    m = K.znaki["glazy_legowiska"]
    u, v = m["u"], m["v"]
    zn = 1 if v > 0 else -1
    with s.grupa("Punkty/GlazyLegowiska"), s.uklad(pos=(u, 0, v + zn * 1.5)):
        with s.uklad(obrot=(3, 15, 6)):
            s.blok("Głaz", (0, 3.4, 0), (11.0, 8.2, 9.6), cien(s, "kamien_cieply", 0.8))
            with s.cechy(kolizja=False, cien=False):
                s.blok("Mech cień", (-1.2, 7.6, 1.0), (5.0, 0.3, 4.6), cien(s, "mech", 0.6), rot=(0, 20, 0))
                s.blok("Mech", (-1.2, 7.85, 1.0), (4.8, 0.45, 4.4), "mech", rot=(0, 20, 0))
            with s.uklad(pos=(0.8, 7.4, -0.6), obrot=(-4, -20, -9)):
                s.blok("Głaz", (0, 3.0, 0), (8.4, 6.6, 7.4), "kamien_cieply")
                with s.uklad(pos=(-0.5, 6.0, 0.4), obrot=(6, 30, 10)):
                    s.blok("Głaz", (0, 2.6, 0), (5.6, 5.4, 5.0), cien(s, "kamien_cieply", 0.9))
                    s.naroznik("Głaz wierzch", (0, 6.2, 0), (4.6, 2.4, 4.2), "kamien_cieply", rot=(0, 90, 0))
                    with s.cechy(kolizja=False, cien=False):
                        s.blok("Mech", (0.4, 5.4, -1.6), (2.4, 0.4, 1.6), "mech", rot=(0, 10, 0))
    # kocioł przed stosem (od strony ścieżki)
    ku, kv = u - 3.0, v - zn * 7.5
    with s.grupa("Punkty/GlazyLegowiska"):
        with s.cechy(kolizja=False):
            for k in range(3):
                a = k * 2.1
                s.belka("Polano", (ku - 1.6 * math.cos(a), 0.25, kv - 1.6 * math.sin(a)), (ku + 0.4 * math.cos(a), 0.9, kv + 0.4 * math.sin(a)),
                        0.5, "drewno", "Wood")
            with s.cechy(cien=False):
                s.naroznik("Ogień", (ku, 0.6, kv), (1.6, 1.2, 1.6), "neon_ogien", "Neon", rot=(0, 30, 0))
        s.walec("Kocioł", (ku, 1.9, kv), 2.2, 2.4, "metal_ciemny", os="y")
        with s.cechy(kolizja=False):
            s.walec("Kocioł brzeg", (ku, 3.2, kv), 2.5, 0.4, "tusz", os="y")
            s.walec("Galareta", (ku, 3.1, kv), 1.9, 0.3, "galareta", os="y")
            for i in range(3):                                 # trzy nóżki kotła
                a = math.radians(30 + 120 * i)
                s.blok("Kocioł", (ku + 1.9 * math.cos(a), 0.4, kv + 1.9 * math.sin(a)), (0.5, 0.9, 0.5), "metal_ciemny")
        zestaw.dym(s, (ku + 0.3, 4.6, kv), n=3, skala=0.8, dryf=(0.6, -zn * 0.4))
    K.zajmij(u, v + zn * 1.5, 7.6)
    K.zajmij(ku, kv, 2.8)


def menhiry_bramy(s, K):
    """Brama menhirów (u 812): dwa menhiry 14 wys. po bokach ścieżki (w osi u; trochę dalej niż v ±16, żeby przechył nie
    wszedł w otwarcie 28 st), z czapami mchu."""
    rnd = K.rnd_punkty
    with s.grupa("Punkty/BramaMenhirow"):
        for pid in ("menhir_lewy", "menhir_prawy"):
            m = K.znaki[pid]
            u, v = m["u"], m["v"]
            vv = v + (1.0 if v > 0 else -1.0)
            skaly.menhir(s, rnd, (u, 0, vv), m["wys"], 0.0, "dach_dom_lupek", przechyl=9)
            with s.cechy(kolizja=False, cien=False):
                s.blok("Menhir mech", (u, m["wys"] + 0.3, vv), (3.0, 0.7, 2.4), "mech")
            K.zajmij(u, vv, 3.0)


def arena(s, K):
    """Arena Strażnika: posadzka kręgu r 27 (0,3), osiem menhirów na okręgu r 26 z przerwami na wejście i wyjście ścieżki,
    filar z zielonym kryształem (ok. 40 n.p.m.) za Strażnikiem."""
    rnd = K.rnd_punkty
    a = K.straznik["arena"]
    cu, cv = a["srodek"]
    r = a["r"]
    with s.grupa("Arena/Krag"):
        with s.cechy(cien=False):
            s.walec("Krąg posadzka", (cu, 0.15, cv), r + 1.0, 0.3, "kamien_cieply", os="y")
            with s.cechy(kolizja=False):
                s.walec("Krąg posadzka środek", (cu, 0.33, cv), 9.0, 0.06, cien(s, "kamien_cieply", 0.85), os="y")
        for k, kat in enumerate((32, 68, 112, 148, 212, 248, 292, 328)):
            aa = math.radians(kat)
            mu, mv = cu + r * math.cos(aa), cv + r * math.sin(aa)
            h = rnd.uniform(9.0, 12.0)
            ry = math.degrees(math.atan2(math.cos(aa), math.sin(aa)))
            skaly.menhir(s, rnd, (mu, 0.3, mv), h, ry, "dach_dom_lupek", przechyl=9)
            with s.cechy(kolizja=False, cien=False):
                s.blok("Menhir mech", (mu, 0.3 + h + 0.2, mv), (3.0, 0.7, 2.4), "mech", rot=(0, ry, 0))
            K.zajmij(mu, mv, 3.0)
    m = K.znaki["filar_krysztal"]
    fu, fv = m["u"], m["v"]
    with s.grupa("Punkty/FilarKrysztal"), s.uklad(pos=(fu, 0.3, fv)):
        for i, (b, h, rz) in enumerate(((7.0, 6.5, 0), (6.0, 6.5, 5), (5.0, 5.5, -6))):
            s.blok("Filar", (0, 3.25 + 6.0 * i, 0), (b, h + 0.6, b), cien(s, "dach_dom_lupek", 0.9 + 0.08 * i), "Slate",
                   rot=(0, 20 * i, rz))
        with s.cechy(kolizja=False):
            s.blok("Kryształ", (0.3, 26.5, 0), (4.6, 18.0, 4.6), "neon_portal", "Neon", rot=(5, 45, 4))
            s.naroznik("Kryształ czubek", (1.1, 37.8, 0), (4.4, 5.0, 4.4), "neon_portal", "Neon", rot=(0, 45, 4))
            s.blok("Kryształ odłamek", (3.0, 20.5, 1.2), (2.2, 9.0, 2.2), "neon_portal", "Neon", rot=(18, 10, -24))
            s.blok("Kryształ odłamek", (-2.6, 19.5, -1.0), (1.8, 7.0, 1.8), "neon_portal", "Neon", rot=(-16, 30, 22))
    K.zajmij(fu, fv, 5.2)


def brama_bagna(s, K):
    """Brama do Bagna (u 934): palisada z pali ok. 10 wys. przez cały pas (aż w kulisy) i wrota 16 szer. z łańcuchem
    i złotą kłódką. Wrota to OSOBNA grupa „BramaBagna/Wrota” (skrzydła z kolizją + łańcuch i kłódka) — skrypt otwiera je
    tylko graczowi, który pokonał Strażnika; reszta bramy jest w „BramaBagna/Palisada”."""
    m = K.miejsca["brama_bagna"]
    u = m["u"]
    o1, o2 = m["otwarcie"]
    pol = (o2 - o1) / 2.0
    rnd = K.rnd_punkty
    with s.grupa("BramaBagna/Palisada"):
        for zn in (-1, 1):
            v = pol + 2.2
            k = 0
            while v < 45.0:
                h = rnd.uniform(8.6, 10.6)
                s.walec("Pal", (u + rnd.uniform(-0.25, 0.25), h / 2.0 - 0.4, zn * v), 0.9, h + 0.8, "drewno_ciemne", os="y",
                        rot=(rnd.uniform(-3, 3), 0, rnd.uniform(-3, 3)))
                if k % 3 == 0:
                    with s.cechy(kolizja=False, cien=False):
                        s.walec("Pal mech", (u, h + 0.1, zn * v), 1.05, 0.6, "mech", os="y")
                v += 1.82
                k += 1
            with s.cechy(kolizja=False):
                for y in (2.6, 6.8):
                    s.belka("Belka bramy", (u - 1.1, y, zn * (pol + 1.5)), (u - 1.1, y + rnd.uniform(-0.4, 0.4), zn * 44.5), 0.7,
                            "drewno", "Wood")
            s.walec("Pal", (u, 7.0, zn * (pol + 0.9)), 1.3, 14.0, "drewno", os="y", rot=(0, 0, zn * 2))
            with s.cechy(kolizja=False, cien=False):
                s.walec("Pal mech", (u, 14.1, zn * (pol + 0.9)), 1.55, 0.8, "mech", os="y")
        with s.cechy(kolizja=False):
            s.belka("Belka bramy", (u, 12.9, -(pol + 2.6)), (u, 13.6, pol + 2.6), 1.3, "drewno", "Wood")
            for zn in (-1, 1):
                s.blok("Lampion łańcuch", (u - 0.6, 11.9, zn * 4.5), (0.3, 1.6, 0.3), "metal_ciemny")
                s.blok("Lampion", (u - 0.6, 10.5, zn * 4.5), (1.2, 1.6, 1.2), "neon_okno", "Neon", rot=(0, 45, 0))
    with s.grupa("BramaBagna/Wrota"):
        for zn in (-1, 1):
            c = zn * (pol - 0.05) / 2.0
            s.blok("Wrota belka", (u, 4.6, c), (0.8, 9.2, pol - 0.15), "drewno_jasne", "WoodPlanks", rot=(0, 0, 0))
            with s.cechy(kolizja=False):
                for y in (2.2, 7.0):
                    s.blok("Wrota belka", (u - 0.55, y, c), (0.35, 0.9, pol - 0.4), "drewno_ciemne")
                s.belka("Wrota belka", (u - 0.6, 2.4, zn * 0.6), (u - 0.6, 6.8, zn * (pol - 0.5)), 0.35, "drewno_ciemne", "SmoothPlastic", 0.8)
                with s.cechy(cien=False):
                    s.blok("Szczelina", (u - 0.42, 4.6, zn * pol / 2.0 + 0.0), (0.1, 8.6, 0.25), "tusz")
        with s.cechy(kolizja=False):
            for k, vv in enumerate((-2.7, -0.9, 0.9, 2.7)):
                s.blok("Łańcuch", (u - 0.75, 4.9 - 0.35 * math.cos(vv), vv), (0.5, 0.55, 1.9), "metal_ciemny",
                       rot=(0 if k % 2 else 90, 0, 0))
            s.blok("Kłódka", (u - 1.0, 3.9, 0.0), (0.9, 2.8, 2.6), "zloto")
            s.blok("Kłódka kabłąk", (u - 1.0, 5.8, 0.0), (0.4, 1.3, 1.6), "metal_ciemny")
            with s.cechy(cien=False):
                s.blok("Kłódka dziurka", (u - 1.5, 3.6, 0.0), (0.1, 1.1, 0.55), "tusz")
    K.zajmij(u, 0, pol + 2)


def zapowiedz_bagna(s, K):
    """Za bramą (u 934–965, osobna grupa ZapowiedzBagna — do usunięcia, gdy powstanie Bagno): błotnisty grunt, kałuże,
    mgła z białych kul, suche drzewa i niewidzialna ściana na końcu, żeby przez wrota nie było widać pustki."""
    from swiat.biom_las import rosliny
    rnd = K.rnd_bagno
    with s.grupa("ZapowiedzBagna"):
        with s.cechy(kolizja=False, cien=False):
            s.blok("Ślad bagna", (950.0, 0.0, 0.0), (31.0, 0.16, 120.0), "lisc_ciemny")
            for uu, vv, r in ((942.0, -14.0, 3.2), (951.0, 9.0, 4.0), (958.0, -24.0, 3.0), (946.0, 26.0, 2.6), (960.0, 15.0, 2.4)):
                s.walec("Kałuża woda", (uu, 0.12, vv), r, 0.1, "woda_gleboka", os="y")
            for k in range(5):
                s.kula("Mgła bagna", (rnd.uniform(944, 962), rnd.uniform(3.0, 7.0), rnd.uniform(-26, 26)), rnd.uniform(8, 12), "biel",
                       alfa=0.3)
        for uu, vv in ((946.0, -21.0), (956.0, 27.0), (961.0, -4.0)):
            if abs(vv) < 8:
                vv = 9.0
            rosliny.suchy(s, rnd, (uu, 0.0, vv), rnd.uniform(0.9, 1.15), rnd.uniform(0, 360))
        for uu, vv in ((941.0, -30.0), (944.0, 31.0), (953.0, -9.0), (957.0, 20.0)):
            for q in range(2):
                rosliny.trzcina(s, rnd, (uu + rnd.uniform(-1.5, 1.5), 0.0, vv + rnd.uniform(-1.5, 1.5)))
        with s.cechy(cien=False):
            s.blok("Niewidzialna ściana", (965.0, 40.0, 0.0), (2.0, 80.0, 120.0), "biel", alfa=1.0)
