# -*- coding: utf-8 -*-
"""Miejsca, punkty orientacyjne, przejścia, domy potworów, rekwizyty, Topiel i brama do Dżungli (grupy „Punkty/<Nazwa>”
— w Studio Persistent — oraz „BramaDzungli/Palisada” i „BramaDzungli/Wrota”: skrypt otwiera same wrota dla gracza).

Z lasu-pasa bez zmian: `punkty.kamien_powrotu` i `punkty.stanowisko_jajka` (ten sam Kamień Powrotu i to samo stanowisko
jajka w każdym biomie — gracz od razu je rozpoznaje). Reszta jest nowa i składa prymitywy lasu (rosliny, skaly, detale,
wspolne, zestaw miasteczka). Układ: x = u, z = v.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale, rosliny as rosliny_lasu, skaly  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.bagno_pas import rosliny  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402
from swiat.las_pas import punkty as punkty_lasu  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402


# =========================================================================== wejście
def pomost_przybycia(s, K):
    """Miejsce przybycia: kwadratowy pomost 12 × 12 (wierzch 0,45) z rombem światła, cztery niskie pale z ognikami
    w narożach; obok ten sam Kamień Powrotu i to samo stanowisko jajka co w lesie (na drewnianym podeście)."""
    m = K.miejsca["przybycie"]
    u, v = m["u"], m["v"]
    with s.grupa("Wejscie/PomostPrzybycia"):
        with s.cechy(cien=False):
            s.blok("Pomost deska", (u, 0.3, v), (12.0, 0.3, 12.0), "bagno_deska", rot=(0, 2, 0))
        with s.cechy(kolizja=False, cien=False):
            for dv in (-3.6, 0.0, 3.6):
                s.blok("Kładka deska", (u, 0.47, v + dv), (11.4, 0.05, 0.3), "bagno_deska_ciemna", rot=(0, 2, 0))
            for a in (45, 135):
                s.blok("Blask", (u, 0.5, v), (0.35, 0.06, 4.0), "neon_portal", "Neon", rot=(0, a, 0))
        for du, dv in ((-5.6, -5.6), (5.6, -5.6), (-5.6, 5.6), (5.6, 5.6)):
            s.walec("Kładka pal", (u + du, 0.55, v + dv), 0.4, 1.1, "bagno_deska_ciemna", "Wood", os="y")
            rosliny.ognik(s, (u + du, 1.5, v + dv), 0.55)
    K.zajmij(u, v, 8.5)
    punkty_lasu.kamien_powrotu(s, K)
    j = K.miejsca["jajko"]
    with s.grupa("Punkty/StanowiskoJajka"), s.cechy(cien=False):
        s.blok("Pomost deska", (j["u"], 0.1, j["v"]), (15.0, 0.2, 15.0), "bagno_deska_ciemna", rot=(0, 8, 0))
    punkty_lasu.stanowisko_jajka(s, K)
    rnd = K.rnd_punkty
    with s.grupa("Punkty/StanowiskoJajka"), s.cechy(kolizja=False):
        for k in range(4):
            a = math.radians(30 + 90 * k)
            rosliny.kepa_trzciny(s, rnd, (j["u"] + 9.5 * math.cos(a), 0.0, j["v"] + 9.5 * math.sin(a)), rnd.uniform(2.6, 3.6), 3.0)


# =========================================================================== punkty orientacyjne
def chata_na_palach(s, K):
    """Chata na Palach (1144; 30): sześć pali do 7, pomost, chatka z desek z drzwiami i świecącym oknem, strzecha,
    drabina ku polu gry, sieć rybacka na żerdzi. Ok. 17 wys."""
    m = K.znaki["chata_na_palach"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    h0 = 7.0
    with s.grupa("Punkty/ChataNaPalach"), s.uklad(pos=(u, 0, v), obrot=(0, 180 + 6, 0)):   # front (+Z) ku polu gry
        for x in (-3.6, 0.0, 3.6):
            for z in (-3.0, 3.0):
                s.walec("Chata pal", (x, h0 / 2.0 - 0.2, z), 0.45, h0 + 0.4, "bagno_kora", "Wood", os="y",
                        rot=(rnd.uniform(-4, 4), 0, rnd.uniform(-4, 4)))
        s.blok("Pomost deska", (0, h0 + 0.2, 0.6), (9.6, 0.4, 8.4), "bagno_deska")
        with s.uklad(pos=(0, h0 + 0.4, -0.4), obrot=(0, 0, -3)):
            s.blok("Chata ściana", (0, 2.5, 0), (7.4, 5.0, 5.6), "drewno")
            with s.cechy(kolizja=False):
                s.blok("Chatka drzwi", (-1.6, 1.7, 2.85), (1.8, 3.4, 0.2), "drewno_ciemne")
                s.blok("Chatka okienko", (1.7, 2.9, 2.85), (1.5, 1.3, 0.2), "neon_okno", "Neon")
                s.dach_dwuspadowy("Strzecha", (0, 5.0, 0), 8.8, 3.3, 3.2, 0.6, "bagno_trzcina", okap=1.0)
                s.belka("Komin", (2.4, 6.0, -1.4), (2.9, 9.2, -1.6), 1.0, "kamien_cokol", "SmoothPlastic")
        with s.cechy(kolizja=False):
            for i in range(6):                                  # drabina ku polu gry (front)
                s.blok("Drabina", (3.0, 1.0 + 1.1 * i, 4.7 + 0.18 * i), (1.8, 0.2, 0.3), "drewno_ciemne")
            for x in (2.2, 3.8):
                s.belka("Drabina", (x, 0.0, 4.6), (x, h0 + 0.2, 5.7), 0.25, "drewno_ciemne", "Wood")
            s.belka("Pal", (-4.8, 0.0, 4.2), (-5.0, 5.0, 4.4), 0.3, "drewno_ciemne", "Wood")
            s.blok("Sieć", (-4.9, 3.0, 3.2), (0.1, 3.4, 2.4), "bagno_mgla", rot=(0, 0, 4))
    K.zajmij(u, v, 7.0)


def stary_cyprys(s, K):
    """Stary Cypryś (1356; 32): olbrzymi cypryśnik (rodzina `cyprys` ×1,3, ok. 31 wys.), wieniec „kolan” i trzy ogniki."""
    m = K.znaki["stary_cyprys"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Punkty/StaryCypryś"):
        rosliny.cyprys(s, rnd, (u, 0.0, v), 1.3, 20.0)
        with s.cechy(kolizja=False):
            for k in range(6):
                a = math.radians(60 * k + rnd.uniform(-15, 15))
                r = rnd.uniform(4.0, 5.6)
                h = rnd.uniform(1.0, 2.2)
                s.klin("Korzeń", (u + r * math.cos(a), h / 2.0, v + r * math.sin(a)), (1.2, h, 1.2), "bagno_kora", "Wood",
                       rot=(0, rnd.uniform(0, 360), 0))
        for k in range(3):
            rosliny.ognik(s, (u + rnd.uniform(-5, 5), rnd.uniform(3.0, 6.0), v + rnd.uniform(-6, 2)))
    K.zajmij(u, v, 6.0)


def wrak_lodzi(s, K):
    """Wrak Łodzi (1564; 30): rufa łodzi sterczy ukosem (35°) z wody — stępka, dwie burty, pawęż, ławka; złamany maszt
    z podartym żaglem, lina do pala. Ok. 19 wys."""
    m = K.znaki["wrak_lodzi"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    with s.grupa("Punkty/WrakLodzi"):
        with s.uklad(pos=(u, 0.0, v), obrot=(0, 24, 0)):
            with s.uklad(pos=(0, 0.0, 0), obrot=(-36, 0, 6)):          # łódź wbita dziobem w muł, rufa w górze
                s.blok("Łódka stępka", (0, 0.6, 5.0), (0.9, 0.9, 13.0), "drewno_ciemne", "Wood")
                for zn in (-1, 1):
                    s.blok("Wrak burta", (zn * 2.1, 2.2, 5.0), (0.5, 3.2, 13.0), "drewno", rot=(0, 0, zn * 14))
                s.blok("Wrak burta", (0, 2.4, 11.4), (4.8, 3.4, 0.5), "drewno_jasne")
                with s.cechy(kolizja=False):
                    for z in (3.0, 7.5):
                        s.blok("Łódka żebro", (0, 1.4, z), (4.0, 0.4, 0.5), "drewno_ciemne")
                    s.blok("Ławka deska", (0, 2.3, 9.0), (3.6, 0.3, 1.2), "drewno_jasne")
            with s.cechy(kolizja=False):
                s.slup("Maszt", 0.6, 0.0, -2.0, 0.5, 13.0, "drewno_ciemne", "Wood", przechyl=(-14, 9))
                s.blok("Żagiel", (1.2, 9.0, -0.6), (0.15, 6.0, 3.6), "tynk_krem", rot=(-14, 0, 9))
                s.blok("Żagiel", (1.0, 6.0, 0.4), (0.15, 2.4, 2.0), cien(s, "tynk_krem", 0.85), rot=(-20, 0, 12))
                s.belka("Lina", (0.2, 11.0, -3.6), (-5.5, 0.6, -6.0), 0.25, "bagno_trzcina", "SmoothPlastic")
            s.walec("Pal", (-5.6, 1.0, -6.2), 0.45, 2.4, "drewno_ciemne", "Wood", os="y")
        for k in range(4):
            rosliny.grzybien(s, rnd, (u + rnd.uniform(-6, 6), 0.18, v + rnd.uniform(-5, 5)), rnd.uniform(0.8, 1.2))
    K.zajmij(u, v, 8.0)


def ropusza_chata(s, K):
    """Ropusza Chata (1724; −30): niska chata na palach (pomost 2,6), krzywy komin z dymem, kocioł z ogniem na błocie,
    beczki i stos chrustu. Ok. 18 wys. To dom Ropuchy z Chatką."""
    m = K.znaki["ropusza_chata"]
    u, v = m["u"], m["v"]
    rnd = K.rnd_punkty
    h0 = 2.6
    with s.grupa("Punkty/RopuszaChata"), s.uklad(pos=(u, 0, v), obrot=(0, -4, 0)):       # front (+Z) ku polu gry
        for x in (-4.0, 0.0, 4.0):
            for z in (-3.2, 3.2):
                s.walec("Chata pal", (x, h0 / 2.0 - 0.2, z), 0.5, h0 + 0.4, "bagno_kora", "Wood", os="y")
        s.blok("Pomost deska", (0, h0 + 0.2, 0.5), (10.4, 0.4, 8.6), "bagno_deska_ciemna")
        with s.uklad(pos=(0, h0 + 0.4, -0.5), obrot=(0, 0, 4)):
            s.blok("Chata ściana", (0, 3.0, 0), (8.6, 6.0, 6.4), cien(s, "drewno", 0.86))
            with s.cechy(kolizja=False):
                s.blok("Chatka drzwi", (0.0, 1.9, 3.25), (2.4, 3.8, 0.2), "drewno_ciemne")
                for x in (-2.8, 2.8):
                    s.blok("Chatka okienko", (x, 3.4, 3.25), (1.3, 1.2, 0.2), "neon_ognik", "Neon")
                s.dach_dwuspadowy("Strzecha", (0, 6.0, 0), 10.0, 3.7, 3.8, 0.7, cien(s, "bagno_trzcina", 0.9), okap=1.2)
            xe, ye, _ = lamana(s, "Komin", [(3.0, 1.6, 4), (2.6, 1.4, -10), (2.2, 1.2, 9)], "kamien_cokol", "SmoothPlastic",
                               start=(-2.8, 7.0), z=-1.6)
            zestaw.dym(s, (xe - 0.4, ye + 1.4, -1.6), n=3, skala=0.9, kolor="biel", dryf=(0.6, 0.4), ksztalt="klocek")
        with s.cechy(kolizja=False):
            s.walec("Kocioł", (5.8, 1.0, 7.2), 1.6, 2.0, "metal_ciemny", os="y")
            s.walec("Kocioł brzeg", (5.8, 2.05, 7.2), 1.75, 0.2, "tusz", os="y")
            s.walec("Galareta", (5.8, 2.0, 7.2), 1.45, 0.15, "bagno_rzesa", os="y")
            s.blok("Ogień", (5.8, 0.25, 7.2), (2.0, 0.5, 2.0), "neon_ogien", "Neon", rot=(0, 45, 0))
        zestaw.beczka(s, (-6.0, 0.0, 5.6), "woda", r=1.2, h=2.6, kolizja=False)
        zestaw.beczka(s, (-4.0, 0.0, 6.8), "woda", r=1.0, h=2.2, kolizja=False)
        detale.stos_drewna(s, rnd, (7.6, 0.0, 3.0), 30.0)
    K.zajmij(u, v, 8.5)


def latarnie_topieli(s, K):
    """Dwa krzywe słupy (14) z ramieniem i wiszącą zieloną latarnią po bokach osi (1752; ±16) i niskie korzenie ≤ 1,2
    dalej ku ścianom."""
    rnd = K.rnd_punkty
    for zid in ("latarnia_lewa", "latarnia_prawa"):
        m = K.znaki[zid]
        u, v = m["u"], m["v"]
        zn = 1 if v > 0 else -1
        with s.grupa("Punkty/LatarnieTopieli"), s.uklad(pos=(u, 0, v), obrot=(0, 90, 0)):   # lokalne x = −v
            s.walec("Pniak", (0, 0.6, 0), 1.6, 1.2, "bagno_kora", "Wood", os="y")
            xe, ye, _ = lamana(s, "Latarnia słup", [(5.0, 1.0, zn * 3), (5.0, 0.85, -zn * 6), (3.8, 0.7, zn * 5)], "drewno_ciemne",
                               "Wood", start=(0.0, 1.0))
            with s.cechy(kolizja=False):                       # ramię ku ścianie (lokalne −x = +v po prawej), poza otwarciem
                s.belka("Lampion ramię", (xe, ye - 0.5, 0), (xe - zn * 2.6, ye - 0.2, 0), 0.4, "drewno_ciemne", "Wood")
                s.blok("Lampion łańcuch", (xe - zn * 2.4, ye - 1.3, 0), (0.25, 1.4, 0.25), "metal_ciemny")
                s.blok("Lampion", (xe - zn * 2.4, ye - 2.8, 0), (1.5, 1.8, 1.5), "neon_ognik", "Neon", rot=(0, 45, 0))
                s.blok("Lampion daszek", (xe - zn * 2.4, ye - 1.7, 0), (2.2, 0.45, 2.2), "bagno_deska_ciemna", rot=(0, 45, 0))
                s.blok("Mech zwis", (-zn * 0.4, 8.0, 0.5), (0.7, 3.0, 1.2), "bagno_sylweta_2")
        K.zajmij(u, v, 2.5)
    t = K.przejscia["latarnie_topieli"]
    with s.grupa("Przejscia/LatarnieTopieli"):
        for zn in (-1, 1):
            for k in range(4):
                vv = zn * (19.0 + 4.6 * k + rnd.uniform(-1, 1))
                uu = (t["u_od"] + t["u_do"]) / 2.0 + rnd.uniform(-3, 3)
                s.belka("Korzeń", (uu - 2.0, 0.1, vv), (uu + 2.0, 0.9, vv + rnd.uniform(-1, 1)), 0.9, "bagno_kora", "Wood")


def topiel_arena(s, K):
    """Topiel Strażnika: okrągły pomost z desek r 27 (wierzch 0,3) na ciemnej wodzie, jaśniejszy krąg w środku, osiem
    pni z latarniami na okręgu r 26 z przerwami na wejście i wyjście kładki, Wieża Topieli (ok. 40) z boku osi."""
    rnd = K.rnd_punkty
    a = K.straznik["arena"]
    cu, cv = a["srodek"]
    r = a["r"]
    with s.grupa("Arena/Pomost"):
        with s.cechy(cien=False):
            s.walec("Pomost okrągły", (cu, 0.15, cv), r + 1.0, 0.3, "bagno_deska", os="y")
        with s.cechy(kolizja=False, cien=False):
            s.walec("Pomost okrągły", (cu, 0.33, cv), 10.0, 0.06, cien(s, "bagno_deska", 0.84), os="y")
            for k in range(6):
                s.blok("Kładka deska", (cu, 0.32, cv), (2 * r + 1.2, 0.06, 0.3), "bagno_deska_ciemna", rot=(0, 30 * k, 0))
    with s.grupa("Arena/Krag"):
        for kat in (32, 68, 112, 148, 212, 248, 292, 328):
            aa = math.radians(kat)
            mu, mv = cu + r * math.cos(aa), cv + r * math.sin(aa)
            h = rnd.uniform(7.5, 10.0)
            zn = 1 if mv >= 0 else -1
            s.walec("Pniak", (mu, 0.3 + 0.9, mv), 1.5, 1.8, "bagno_suche", "Wood", os="y")
            with s.cechy(kolizja=False, cien=False):
                s.walec("Pniak słoje", (mu, 2.12, mv), 1.2, 0.06, "drewno_jasne", os="y")
            s.slup("Latarnia słup", mu, 2.1, mv, 0.35, h - 2.0, "drewno_ciemne", "Wood", przechyl=(rnd.uniform(-5, 5), zn * 5))
            with s.cechy(kolizja=False):
                s.blok("Lampion", (mu, 0.3 + h - 0.6, mv + zn * 0.6), (1.1, 1.4, 1.1), "neon_ognik", "Neon", rot=(0, 45, 0))
                s.blok("Lampion daszek", (mu, 0.3 + h + 0.3, mv + zn * 0.6), (1.7, 0.4, 1.7), "bagno_deska_ciemna", rot=(0, 45, 0))
            K.zajmij(mu, mv, 2.4)
    m = K.znaki["wieza_topieli"]
    fu, fv = m["u"], m["v"]
    with s.grupa("Punkty/WiezaTopieli"), s.uklad(pos=(fu, 0.0, fv), obrot=(0, 15, 0)):
        for x, z in ((-2.2, -2.2), (2.2, -2.2), (-2.2, 2.2), (2.2, 2.2)):
            s.belka("Wieża pal", (x * 1.3, -0.2, z * 1.3), (x * 0.55, 30.0, z * 0.55), 0.9, "bagno_kora", "Wood")
        with s.cechy(kolizja=False):
            for y, b in ((9.0, 5.4), (19.0, 4.2)):
                s.blok("Wieża pomost", (0, y, 0), (b, 0.4, b), "bagno_deska_ciemna", rot=(0, 10, 0))
            for y in (5.0, 14.0, 24.0):
                s.belka("Wieża pal", (-2.5 + 0.03 * y, y, -2.5 + 0.03 * y), (2.5 - 0.03 * y, y + 3.0, 2.5 - 0.03 * y), 0.4,
                        "drewno_ciemne", "Wood")
            s.blok("Wieża pomost", (0, 30.2, 0), (4.6, 0.5, 4.6), "bagno_deska", rot=(0, 25, 0))
            s.blok("Latarnia klosz", (0, 33.3, 0), (3.2, 5.0, 3.2), "neon_ognik", "Neon", rot=(0, 45, 0))
            s.ostroslup("Strzecha", (0, 35.8, 0), 2.6, 2.6, 4.2, "bagno_deska_ciemna")
            s.blok("Mech zwis", (1.8, 26.0, -1.2), (0.8, 6.0, 1.4), "bagno_sylweta_2")
    K.zajmij(fu, fv, 5.0)


# =========================================================================== przejścia
def trzcinowa_przesieka(s, K):
    """Ściany wysokiej trzciny i pałek 5–6 wys. od |v| 16 do ścian i w kulisy (u 1420–1436)."""
    t = K.przejscia["trzcinowa_przesieka"]
    rnd = K.rnd_przejscia
    o2 = t["otwarcie"][1]
    with s.grupa("Przejscia/TrzcinowaPrzesieka"):
        for zn in (-1, 1):
            v = o2 + 2.9
            while v < 44.0:
                for uu in (t["u_od"] + 3.5, t["u_do"] - 3.5):
                    rosliny.kepa_trzciny(s, rnd, (uu + rnd.uniform(-1.5, 1.5), 0.0, zn * v), rnd.uniform(4.6, 6.0), 4.2)
                v += rnd.uniform(3.4, 4.2)


def zatopione_pnie(s, K):
    """Zwalone, omszałe pnie i karpy korzeni 6–9 wys. od |v| 14 ku ścianom (u 1628–1644); kości i pal z czaszką przy
    otwarciu — ostrzeżenie przed Ropuchą."""
    t = K.przejscia["zatopione_pnie"]
    rnd = K.rnd_przejscia
    o2 = t["otwarcie"][1]
    uc = (t["u_od"] + t["u_do"]) / 2.0
    with s.grupa("Przejscia/ZatopionePnie"):
        for zn in (-1, 1):
            v = o2 + 2.0
            k = 0
            while v < 40.0:
                h = rnd.uniform(5.0, 8.5)
                with s.uklad(pos=(uc + rnd.uniform(-2.5, 2.5), 0.0, zn * v), obrot=(0, rnd.uniform(-25, 25), 0)):
                    if k % 2 == 0:                          # karpa: talerz korzeni stojący na sztorc + pień leżący
                        s.walec("Talerz korzeni", (0, h / 2.0, 0), h / 2.0, 1.4, "bagno_kora", "Wood", os="z")
                        s.walec("Zwalony pień", (0, 1.4, zn * 4.6), 1.5, 8.0, "bagno_kora", "Wood", os="z", rot=(6, 0, 0))
                    else:
                        s.walec("Zwalony pień", (0, h * 0.35, 0), 1.6, 12.0, "bagno_suche", "Wood", os="x",
                                rot=(0, 0, rnd.uniform(28, 40) * rnd.choice((-1, 1))))
                    with s.cechy(kolizja=False, cien=False):
                        s.blok("Mech", (0, h * 0.75, 0), (2.6, 0.5, 2.6), "bagno_mech", rot=(0, 20, 0))
                v += rnd.uniform(5.0, 6.5)
                k += 1
        with s.cechy(kolizja=False):
            for zn in (-1, 1):
                s.walec("Pal", (uc - 4.0, 1.6, zn * (o2 + 1.6)), 0.35, 3.2, "drewno_ciemne", "Wood", os="y")
                detale.czaszka(s, rnd, (uc - 4.0, 3.2, zn * (o2 + 1.6)), 90.0 if zn > 0 else -90.0)
            for q in range(3):
                detale.kosc(s, rnd, (uc + rnd.uniform(-5, 5), 0.0, rnd.choice((-1, 1)) * rnd.uniform(o2 + 3, o2 + 9)))


def ozdoby_rowow(s, K):
    """Kępy trzciny na brzegach rowów tylko w kulisach (otwarcie przejścia ma zostać niskie, jak strumyk lasu), w polu
    gry grzybienie na wodzie."""
    rnd = K.rnd_przejscia
    with s.grupa("Przejscia/Rowy"):
        for t in (K.przejscia["row_z_kladka"], K.przejscia["kladka_nad_topiela"]):
            a, b = t["woda"]
            for zn in (-1, 1):
                v = 38.0
                while v < 60.0:
                    uu = rnd.choice((a - 0.6, b + 0.6)) + rnd.uniform(-0.6, 0.6)
                    with s.cechy(kolizja=False):
                        rosliny.kepa_trzciny(s, rnd, (uu, 0.0, zn * v), rnd.uniform(3.0, 5.0), 2.6)
                    v += rnd.uniform(3.5, 5.5)
                for q in range(3):
                    rosliny.grzybien(s, rnd, ((a + b) / 2.0 + rnd.uniform(-2, 2), 0.2, zn * rnd.uniform(9, 30)), rnd.uniform(0.7, 1.1),
                                     kwiat=rnd.choice((None, "biel", "bagno_kwiat")))


# =========================================================================== domy potworów
def domy(s, K):
    """Dom każdej strefy w punktach z planu (pod ścianą, |v| = 34): Rechotki — oczko z liściem i pałkami; Bulgotniki —
    bąblujący kopiec błota z dziurą; Kłodokłapy — na wpół zatopiona kłoda z korzeniami; Ropucha — błotna kotlinka przy
    Ropuszej Chacie."""
    rnd = K.rnd_domy
    for st in K.strefy:
        for i, (u, v) in enumerate(st["dom"]["pts"]):
            zn = 1 if v > 0 else -1
            with s.grupa("Domy/%s/%d" % (st["id"], i + 1)):
                if st["potwor"] == "Rechotek":
                    with s.cechy(kolizja=False, cien=False):
                        s.walec("Brzeg wody", (u, 0.33, v), 3.6, 0.06, "bagno_mech", os="y")
                        s.walec("Woda", (u, 0.35, v), 3.0, 0.06, "bagno_woda", os="y")
                    rosliny.grzybien(s, rnd, (u + 0.8, 0.36, v - zn * 0.6), 1.3, kwiat="bagno_kwiat")
                    for q in range(2):
                        rosliny_lasu.trzcina(s, rnd, (u + rnd.uniform(-2.5, 2.5), 0.0, v + zn * rnd.uniform(1.0, 2.0)))
                elif st["potwor"] == "Bulgotnik":
                    s.kula("Kopiec błota", (u, 0.2, v), 4.4, "bagno_bloto")
                    with s.cechy(kolizja=False, cien=False):
                        s.blok("Jama otwór", (u, 0.9, v - zn * 1.9), (1.6, 1.2, 0.3), "tusz")
                        for q in range(3):
                            s.kula("Bąbel", (u + rnd.uniform(-1.4, 1.4), rnd.uniform(1.8, 2.6), v + rnd.uniform(-1, 1)),
                                   rnd.uniform(0.4, 0.8), "bagno_mgla")
                elif st["potwor"] == "Kłodokłap":
                    with s.uklad(pos=(u, 0, v), obrot=(0, rnd.uniform(-20, 20), 0)):
                        s.walec("Kłoda", (0, 0.25, 0), 1.2, 7.0, "bagno_kora", "Wood", os="x", rot=(0, 0, 3))
                        with s.cechy(kolizja=False, cien=False):
                            s.walec("Kłoda słoje", (3.55, 0.25, 0), 0.95, 0.08, "drewno_jasne", os="x")
                            s.blok("Mech", (-0.6, 1.42, 0), (3.4, 0.3, 1.4), "bagno_mech")
                        with s.cechy(kolizja=False):
                            for q in (-1, 1):
                                s.belka("Korzeń", (-3.4, 0.6, 0), (-5.0, 0.0, q * 1.6), 0.5, "bagno_kora", "Wood")
                else:
                    with s.cechy(kolizja=False, cien=False):
                        s.walec("Błoto", (u, 0.2, v + 1.0), 4.0, 0.08, "bagno_bloto", os="y")
                    for q in range(3):
                        rosliny.kepa_trzciny(s, rnd, (u + rnd.uniform(-3.5, 3.5), 0.0, v - zn * rnd.uniform(-0.5, 0.5)), 2.2, 2.4)
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

    def ognik(u, v):
        rosliny.ognik(s, (u, rnd.uniform(1.6, 3.4), v))

    def palki(u, v):
        for q in range(2):
            rosliny_lasu.trzcina(s, rnd, (u + rnd.uniform(-1, 1), 0.0, v + rnd.uniform(-0.8, 0.8)))

    def kepa(u, v):
        rosliny.kepa_trzciny(s, rnd, (u, 0.0, v), rnd.uniform(1.0, 1.35), 2.6)

    def lodka(u, v):
        with s.uklad(pos=(u, 0.0, v), obrot=(rnd.uniform(-4, 4), rnd.uniform(0, 180), rnd.uniform(-8, 8))):
            s.blok("Łódka stępka", (0, 0.35, 0), (5.2, 0.5, 2.2), "drewno")
            with s.cechy(kolizja=False):
                for zn in (-1, 1):
                    s.blok("Wrak burta", (0, 0.75, zn * 1.05), (5.0, 0.6, 0.25), "drewno_ciemne")
                s.blok("Ławka deska", (0, 0.8, 0), (0.8, 0.15, 2.0), "drewno_jasne")

    def beczka(u, v):
        zestaw.beczka(s, (u, 0.0, v), "woda", r=1.0, h=2.2, przechyl=(0.0, rnd.uniform(4, 12)), ry=rnd.uniform(0, 360), kolizja=False)

    def lampion(u, v):
        wspolne.lampion(s, (u, 0.0, v), rnd.uniform(4.0, 5.5), "neon_ognik")

    def pniak(u, v):
        with s.cechy(kolizja=False):
            rosliny_lasu.pniak(s, rnd, (u, 0.0, v), rnd.uniform(0.8, 1.2), rnd.uniform(0, 360))

    def glaz(u, v):
        skaly.glaz(s, rnd, (u, 0.0, v), rnd.uniform(0.6, 0.85), rnd.uniform(0, 360), "kamien_cokol", mech=True, kolizja=False)

    def kloda(u, v):
        with s.cechy(kolizja=False):
            detale.kloda(s, rnd, (u, 0.0, v), rnd.uniform(0.7, 0.95))

    for qid in ("oczka", "kepy"):
        rozsiej(qid, 10, 1.4, 1.2, palki, v_od=-35.0, v_do=35.0, grupa="Ozdoby/%s/Palki" % qid)
        rozsiej(qid, 6, 1.6, 1.4, kepa, v_od=-35.0, v_do=35.0, grupa="Ozdoby/%s/Kepy" % qid)
        rozsiej(qid, 7, 0.6, 3.5, ognik, v_od=-34.0, v_do=34.0, grupa="Ozdoby/%s/Ogniki" % qid)
    rozsiej("oczka", 3, 3.0, 1.0, lodka, v_od=-34.0, v_do=34.0, grupa="Ozdoby/oczka/Lodki")
    rozsiej("kepy", 5, 2.2, 1.4, pniak, v_od=-34.0, v_do=34.0, grupa="Ozdoby/kepy/Pniaki")
    rozsiej("kepy", 4, 3.5, 1.4, kloda, v_od=-34.0, v_do=34.0, grupa="Ozdoby/kepy/Klody")
    rozsiej("trzesawisko", 8, 1.6, 1.4, kepa, grupa="Ozdoby/trzesawisko/Kepy")
    rozsiej("trzesawisko", 8, 0.6, 3.5, ognik, grupa="Ozdoby/trzesawisko/Ogniki")
    rozsiej("trzesawisko", 4, 1.4, 6.0, lampion, v_od=-34.0, v_do=34.0, grupa="Ozdoby/trzesawisko/Lampiony")
    rozsiej("trzesawisko", 4, 1.4, 2.4, beczka, grupa="Ozdoby/trzesawisko/Beczki")
    def kosc(u, v):
        detale.kosc(s, rnd, (u, 0.0, v))

    rozsiej("chatka", 7, 1.6, 1.4, glaz, grupa="Ozdoby/chatka/Glazy")
    rozsiej("chatka", 4, 1.4, 2.4, beczka, grupa="Ozdoby/chatka/Beczki")
    rozsiej("chatka", 10, 1.6, 1.4, kepa, grupa="Ozdoby/chatka/Kepy")
    rozsiej("chatka", 4, 2.2, 1.4, pniak, grupa="Ozdoby/chatka/Pniaki")
    rozsiej("chatka", 3, 3.5, 1.4, kloda, grupa="Ozdoby/chatka/Klody")
    rozsiej("chatka", 5, 1.0, 0.6, kosc, grupa="Ozdoby/chatka/Kosci")
    rozsiej("trzesawisko", 4, 2.2, 1.4, pniak, grupa="Ozdoby/trzesawisko/Pniaki")
    rozsiej("chatka", 4, 0.6, 3.5, ognik, grupa="Ozdoby/chatka/Ogniki")
    rozsiej("wejscie", 6, 1.6, 1.4, kepa, v_od=-35.0, v_do=35.0, grupa="Ozdoby/wejscie/Kepy")
    rozsiej("wejscie", 3, 1.4, 6.0, lampion, v_od=-34.0, v_do=34.0, grupa="Ozdoby/wejscie/Lampiony")
    rozsiej("topiel", 6, 0.6, 3.5, ognik, grupa="Ozdoby/topiel/Ogniki")
    return wynik


def przedbramie(s, K):
    """Przedbramie (strefa spokoju): ławka, lampiony, skrzynie, tabliczka „wkrótce Dżungla” z liściem."""
    rnd = K.rnd_przegrody
    with s.grupa("Przedbramie"):
        zestaw.lawka(s, (1862.0, 0.0, -24.0), ry=90.0, dl=6.0)
        wspolne.lampion(s, (1866.0, 0.0, -28.0), 5.5, "neon_ognik")
        wspolne.lampion(s, (1858.0, 0.0, 26.0), 5.0, "neon_ognik")
        zestaw.skrzynia(s, (1860.0, 0.0, 28.0), ry=20.0, dl=3.2, a=2.6)
        zestaw.skrzynia(s, (1856.5, 0.0, 30.0), ry=-12.0, dl=2.6, a=2.2)
        detale.tabliczka(s, rnd, (1868.0, 0.0, -12.0), 90.0, "laka")
    for u, v in ((1862.0, -24.0), (1866.0, -28.0), (1858.0, 26.0), (1860.0, 28.0), (1856.5, 30.0), (1868.0, -12.0)):
        K.zajmij(u, v, 2.5)


# =========================================================================== brama do Dżungli i zapowiedź
def brama_dzungli(s, K):
    """Brama do Dżungli (u 1874): palisada z pni cypryśnika ok. 10 wys. przez cały pas (aż w kulisy), oplątana lianami
    z wielkimi liśćmi (zapowiedź Dżungli); wrota 16 szer. to OSOBNA grupa „BramaDzungli/Wrota” (skrzydła z kolizją,
    łańcuch, kłódka) — jak brama do Bagna w lesie."""
    m = K.miejsca["brama_dzungli"]
    u = m["u"]
    o1, o2 = m["otwarcie"]
    pol = (o2 - o1) / 2.0
    rnd = K.rnd_punkty
    with s.grupa("BramaDzungli/Palisada"):
        for zn in (-1, 1):
            v = pol + 2.2
            k = 0
            while v < 45.0:
                h = rnd.uniform(8.8, 11.0)
                s.walec("Pal bramy", (u + rnd.uniform(-0.3, 0.3), h / 2.0 - 0.4, zn * v), 0.95, h + 0.8, "bagno_kora", os="y",
                        rot=(rnd.uniform(-3, 3), 0, rnd.uniform(-3, 3)))
                if k % 3 == 1:
                    with s.cechy(kolizja=False):
                        s.blok("Liść olbrzym", (u - 1.4, h - 1.0, zn * v), (0.3, 2.2, 4.0), "dzungla_lisc",
                               rot=(rnd.uniform(-20, 20), 0, rnd.uniform(30, 60)))
                v += 1.86
                k += 1
            with s.cechy(kolizja=False):
                for y in (2.4, 6.6):
                    s.belka("Liana", (u - 1.15, y, zn * (pol + 1.5)), (u - 1.15, y + rnd.uniform(-0.8, 0.8), zn * 44.5), 0.5,
                            "dzungla_lisc", "SmoothPlastic")
            s.walec("Pal bramy", (u, 7.3, zn * (pol + 0.9)), 1.35, 14.6, "bagno_kora", os="y", rot=(0, 0, zn * 2))
            with s.cechy(kolizja=False):
                s.blok("Liść olbrzym", (u - 0.8, 14.6, zn * (pol + 0.9)), (4.6, 0.3, 3.0), "dzungla_lisc_jasny", rot=(0, 20 * zn, 12))
                s.blok("Liść olbrzym", (u + 0.6, 14.3, zn * (pol + 1.6)), (3.8, 0.3, 2.6), "dzungla_lisc", rot=(0, -30 * zn, -14))
        with s.cechy(kolizja=False):
            s.belka("Belka bramy", (u, 13.0, -(pol + 2.6)), (u, 13.5, pol + 2.6), 1.3, "bagno_kora", "Wood")
            for zn in (-1, 1):
                s.blok("Lampion łańcuch", (u - 0.6, 12.0, zn * 4.5), (0.3, 1.6, 0.3), "metal_ciemny")
                s.blok("Lampion", (u - 0.6, 10.6, zn * 4.5), (1.2, 1.6, 1.2), "neon_ognik", "Neon", rot=(0, 45, 0))
    with s.grupa("BramaDzungli/Wrota"):
        for zn in (-1, 1):
            c = zn * (pol - 0.05) / 2.0
            s.blok("Wrota belka", (u, 4.7, c), (0.8, 9.4, pol - 0.15), "bagno_deska", "WoodPlanks")
            with s.cechy(kolizja=False):
                for y in (2.2, 7.2):
                    s.blok("Wrota belka", (u - 0.55, y, c), (0.35, 0.9, pol - 0.4), "bagno_deska_ciemna")
                s.belka("Wrota belka", (u - 0.6, 2.4, zn * 0.6), (u - 0.6, 7.0, zn * (pol - 0.5)), 0.35, "bagno_deska_ciemna",
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


def roslina_dzungli(s, rnd, pos, k=1.0):
    """Kępa olbrzymich liści na łodygach (zapowiedź Dżungli): trzy łodygi, trzy liście-parasole. 6 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False):
        for i in range(3):
            a = math.radians(120 * i + rnd.uniform(-20, 20))
            h = rnd.uniform(4.0, 7.0) * k
            p1, p2 = (0.0, 0.0, 0.0), (2.4 * k * math.cos(a), h, 2.4 * k * math.sin(a))
            s.belka("Liść łodyga", p1, p2, 0.3 * k, "dzungla_lisc", "SmoothPlastic")
            s.blok("Liść olbrzym", (p2[0], p2[1] + 0.2, p2[2]), (5.0 * k, 0.3, 3.2 * k),
                   "dzungla_lisc_jasny" if i % 2 else "dzungla_lisc", rot=(rnd.uniform(-14, 14), -math.degrees(a), rnd.uniform(8, 18)))


def palma(s, rnd, pos, k=1.0):
    """Palma (zapowiedź Dżungli): pień z 3 segmentów w kontrze, pięć liści z klinów. 8 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)):
        xe, ye, _ = lamana(s, "Palma pień", [(6.0 * k, 1.1 * k, zn * 8), (6.0 * k, 0.95 * k, zn * 6), (5.0 * k, 0.8 * k, -zn * 4)],
                           "drewno", "Wood", start=(0.0, -0.3))
        with s.cechy(kolizja=False):
            for i in range(5):
                a = 72 * i + rnd.uniform(-10, 10)
                with s.uklad(pos=(xe, ye, 0), obrot=(0, a, 0)):
                    s.klin("Palma liść", (0, -0.6 * k, 2.8 * k), (1.6 * k, 1.2 * k, 6.0 * k), "dzungla_lisc", rot=(18, 0, 0))


def zapowiedz_dzungli(s, K, Z):
    """Za bramą (u 1876–1906, osobna grupa ZapowiedzDzungli — do usunięcia, gdy powstanie Dżungla): soczysta trawa,
    olbrzymie liście, dwie palmy, kilka czerwonych kwiatów i niewidzialna ściana na u 1905, żeby przez wrota nie było
    widać pustki."""
    rnd = K.rnd_dzungla
    with s.grupa("ZapowiedzDzungli"):
        with s.cechy(kolizja=False, cien=False):
            s.blok("Plama kępy", (1891.0, 0.09, 0.0), (29.0, 0.1, 120.0), "dzungla_lisc")
        for u, v, k in ((1882.0, -16.0, 1.1), (1886.0, 21.0, 1.25), (1896.0, -30.0, 1.4), (1894.0, 9.0, 1.0), (1899.0, 32.0, 1.5),
                        (1882.0, 34.0, 1.0), (1890.0, -40.0, 1.3), (1898.0, -8.0, 1.2)):
            def bud(u=u, v=v, k=k):
                roslina_dzungli(s, rnd, (u, 0.0, v), k)
            postaw(s, Z, bud)
        for u, v in ((1892.0, -22.0), (1900.0, 18.0)):
            def bud(u=u, v=v):
                palma(s, rnd, (u, 0.0, v), 1.15)
            postaw(s, Z, bud)
        with s.cechy(kolizja=False, cien=False):
            for q in range(8):
                rosliny_lasu.kwiaty(s, rnd, (rnd.uniform(1880, 1902), 0.1, rnd.choice((-1, 1)) * rnd.uniform(8, 34)),
                                    ("czerwien", "zloto"))
        with s.cechy(cien=False):
            s.blok("Niewidzialna ściana", (1905.0, 40.0, 0.0), (2.0, 80.0, 120.0), "biel", alfa=1.0)
