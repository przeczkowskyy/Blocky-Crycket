# -*- coding: utf-8 -*-
"""Grunt pasa: płyta, plamy przegród, strzępy na granicach, ścieżka, strumyk z mostkiem i brodem, wydeptane pętle
potworów i polanki stref. Teren płaski (y = 0), bez dziur: jedna płyta z kolizją pod całym pasem z kulisami.

Poziomy nawierzchni nad gruntem (jak w swiat/biom_las/teren.py, odstęp ≥ 0,02 między płaszczyznami różnych kolorów):
plamy przegród 0,06; strzępy na granicach 0,08; polanki stref 0,10–0,11; wydeptane pętle 0,13; brzeg wody 0,14;
woda 0,18; ścieżka 0,30 (+0,01 co drugi odcinek, czapki −0,012). Kształty i kolory; materiały nadaje faktury.py.
Prymitywy płaskie (wstęga, dysk, wielokąt z klinów) i plama-wielokąt — z modułów starego lasu.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.biom_las.teren import dysk, wielokat, wstega, Y_BRZEG, Y_PLAMA, Y_WODA, Y_SCIEZKA  # noqa: E402
from swiat.las_pas.kontekst import ODCINKI_SCIEZKI, SZER_SCIEZKI, U_MAX, U_MIN, V_MAX, WODA_U, v_sciezki  # noqa: E402

# grunt pola gry (|v| ≤ 37,5) od u do u: (nazwa części = rola w faktury.py, kolor). Płyta pod resztą ma `runo_ciemne`
# (cień pod kulisami, ściana zamykająca, przedbramie).
PLAMY = [
    (0.0, 278.0, "Plama laka", "trawa"),          # Polana Przybycia i Zagroda Slime'ów: jasna łąka
    (278.0, 488.0, "Plama kapeluszowo", "runo_ciemne"),   # Lasek Muchomorowy: wilgotne ciemne runo pod czerwone kapelusze
    (488.0, 696.0, "Plama ostepy", "32672D"),     # Wilcze Zarośla: ciemny bór (runo_boru × 0,85)
    (696.0, 812.0, "Plama wawoz", "8E6A48"),      # Leże Trolla: ciemna, udeptana ziemia (cien ziemi)
    (812.0, 908.0, "Plama korona", "runo"),       # Arena Strażnika: jasne runo Korony
]
POLE_V = 37.5
# kolor ścieżki na odcinku (role faktury: bruk → Cobblestone, ziemia → Ground, kamien_cieply → żwir Pebble)
KOLOR_SCIEZKI = [(0.0, "bruk"), (76.0, "ziemia"), (704.0, "kamien_cieply"), (804.0, "bruk")]
# polanki stref (Podkładka strefy: runo → Grass, mech → Grass, kamien_cokol → błoto Mud) i kolor wydeptanej pętli
POLANKI = {"lasek": "mech", "zarosla": "runo", "leze": "kamien_cokol"}
TROP = {"zagroda": ("trawa", 0.8), "lasek": ("mech", 0.72), "zarosla": ("runo", 0.78), "leze": ("kamien_cokol", 0.8)}


def plyta_i_plamy(s, K):
    rnd = K.rnd_teren
    du, dv = U_MAX - U_MIN, 2 * V_MAX
    with s.grupa("Teren/Grunt"), s.cechy(cien=False):
        s.blok("Płyta", ((U_MIN + U_MAX) / 2.0, -1.0, 0.0), (du, 2.0, dv), "runo_ciemne")
    with s.grupa("Teren/Plamy"), s.cechy(kolizja=False, cien=False):
        for u0, u1, nazwa, kol in PLAMY:
            s.blok(nazwa, ((u0 + u1) / 2.0, Y_PLAMA - 0.15, 0.0), (u1 - u0, 0.3, 2 * POLE_V), kol)
        # strzępy na granicach plam: nieregularne łaty obu kolorów zamiast prostej kreski przez pas (4 na granicę)
        for (a0, a1, an, ak), (b0, b1, bn, bk) in zip(PLAMY, PLAMY[1:]):
            g = a1
            for i, vv in enumerate((-27.0, -12.0, 13.0, 28.0)):
                nazwa, kol, du_ = (an, ak, 3.5) if i % 2 == 0 else (bn, bk, -3.5)
                w = wspolne.plama(rnd, g + du_ + rnd.uniform(-1.5, 1.5), vv + rnd.uniform(-2, 2), 3.5, 7.0, 6, 0.12)
                wielokat(s, nazwa, w, Y_PLAMA + 0.02, 0.2, kol)


def kolor_sciezki(u):
    k = KOLOR_SCIEZKI[0][1]
    for u0, kol in KOLOR_SCIEZKI:
        if u >= u0:
            k = kol
    return k


def sciezka(s, K):
    """Dróżka 8 st po osi pasa (lekka fala z kontekst.v_sciezki): odcinki co ok. 12 st z okrągłymi czapkami na stykach,
    kolor zmienia się na granicach przegród (bruk na Polanie i w Arenie, ziemia, żwir w Leżu Trolla)."""
    licznik = 0
    granice = sorted({u0 for u0, _ in KOLOR_SCIEZKI})
    with s.grupa("Sciezka"), s.cechy(cien=False):
        for a, b in ODCINKI_SCIEZKI:
            pts = [a]
            u = a
            while u < b - 1e-6:
                nast = min(b, u + 12.0)
                for g in granice:                              # punkt na granicy koloru
                    if u < g < nast:
                        nast = g
                pts.append(nast)
                u = nast
            for u0, u1 in zip(pts, pts[1:]):
                kol = kolor_sciezki((u0 + u1) / 2.0)
                dy = 0.01 * (licznik % 2)
                licznik += 1
                wstega(s, "Ścieżka", (u0, Y_SCIEZKA + dy, v_sciezki(u0)), (u1, Y_SCIEZKA + dy, v_sciezki(u1)), SZER_SCIEZKI,
                       0.5, kol)
            for u in pts:
                dysk(s, "Ścieżka", u, Y_SCIEZKA - 0.012, v_sciezki(u), SZER_SCIEZKI / 2.0, 0.5, kolor_sciezki(min(u + 0.5, b)))
    return licznik


# =========================================================================== strumyk z mostkiem i brodem
def u_wody(v):
    """Środek koryta strumyka (lekko kręty, w granicach WODA_U)."""
    return (WODA_U[0] + WODA_U[1]) / 2.0 + 1.2 * math.sin(v / 9.0) * min(1.0, abs(v) / 12.0)


def strumyk(s, K):
    """Płytka woda 10 st w poprzek całego pasa (bez kolizji — przejdzie się wszędzie), ciemny brzeg, bliki, lilie, łachy
    żwiru; garbaty mostek 12 szer. na osi (najwyżej 1,6 nad gruntem — plan: wys_w_otwarciu), kamienie brodu przy
    ścianach (v ±24), trzcina tylko w kulisach (otwarcie przejścia ma zostać niskie)."""
    rnd = K.rnd_woda
    szer = WODA_U[1] - WODA_U[0]
    vv = [-62.0 + 8.0 * i for i in range(16)] + [62.0]
    with s.grupa("Przejscia/Strumyk/Woda"), s.cechy(kolizja=False, cien=False):
        for a, b in zip(vv, vv[1:]):
            wstega(s, "Brzeg wody", (u_wody(a), Y_BRZEG, a), (u_wody(b), Y_BRZEG, b), szer + 2.6, 0.2, "woda_gleboka", rot_dod=0)
            wstega(s, "Woda", (u_wody(a), Y_WODA, a), (u_wody(b), Y_WODA, b), szer, 0.2, "woda")
        for v in vv[1:-1]:
            dysk(s, "Brzeg wody", u_wody(v), Y_BRZEG, v, (szer + 2.6) / 2.0, 0.2, "woda_gleboka")
            dysk(s, "Woda", u_wody(v), Y_WODA, v, szer / 2.0, 0.2, "woda")
        for v in (-44.0, -31.0, -15.0, 17.0, 33.0, 47.0):
            s.blok("Blik", (u_wody(v) + rnd.uniform(-2.5, 2.5), Y_WODA + 0.05, v), (0.6, 0.1, rnd.uniform(2.2, 3.2)), "biel",
                   rot=(0, rnd.uniform(-20, 20), 0))
        for v in (-52.0, -36.5, -29.0, 30.0, 40.0, 55.0):
            for q in range(rnd.choice((1, 2))):
                s.walec("Lilia", (u_wody(v) + rnd.uniform(-3, 3), Y_WODA + 0.05, v + q * 1.8), rnd.uniform(0.6, 0.95), 0.1, "lisc",
                        os="y")
        for v, zn in ((-20.0, 1), (11.0, -1), (26.0, 1), (-33.0, -1)):
            for q in range(2):
                s.blok("Żwir", (u_wody(v) + zn * (szer / 2.0 - 0.8) + q * 0.6, Y_WODA + 0.04, v + q * 1.5),
                       (rnd.uniform(1.2, 2.0), 0.22, rnd.uniform(0.8, 1.3)), cien(s, "kamien_cieply", rnd.choice((0.72, 0.8))),
                       rot=(rnd.uniform(-6, 6), rnd.uniform(0, 180), rnd.uniform(-6, 6)))
    # bród: płaskie kamienie z kolizją (wierzch ≤ 0,8) w poprzek wody przy obu ścianach
    with s.grupa("Przejscia/Strumyk/Brod"):
        for v0 in (-24.0, 24.0):
            for i, du in enumerate((-4.6, -1.5, 1.6, 4.7)):
                u = u_wody(v0) + du
                s.blok("Kamień brodu", (u, 0.3, v0 + rnd.uniform(-0.8, 0.8)), (rnd.uniform(2.2, 2.7), 0.7, rnd.uniform(2.0, 2.6)),
                       "kamien_cieply" if i % 2 else cien(s, "kamien_cieply", 0.86), rot=(rnd.uniform(-3, 3), rnd.uniform(0, 90), 0))
            K.zajmij(u_wody(v0), v0, 6.0)
    # mostek garbaty: pomost z 4 desek-wstęg (rampa 0,3 → 1,35 → 1,5 na środku), przyczółki z kamienia na brzegach,
    # słupki na rogach do 1,5 (nic nad 1,6 — przez strumyk widać Lasek)
    u0, u1 = 266.5, 289.5
    with s.grupa("Przejscia/Strumyk/Mostek"):
        profil = [(u0, 0.32), (272.6, 1.32), (278.0, 1.5), (283.4, 1.32), (u1, 0.32)]
        for (a, ya), (b, yb) in zip(profil, profil[1:]):
            wstega(s, "Most pomost", (a, ya, 0.0), (b, yb, 0.0), 12.0, 0.5, "drewno_jasne")
        with s.cechy(kolizja=False, cien=False):
            for vv_ in (-3.6, 0.2, 3.9):                    # ciemniejsze deski-pasy wzdłuż pomostu
                for (a, ya), (b, yb) in zip(profil, profil[1:]):
                    wstega(s, "Most pomost", (a, ya + 0.04, vv_), (b, yb + 0.04, vv_), 0.5, 0.1, "drewno")
        for u in (271.6, 284.4):
            s.blok("Most łuk", (u, 0.55, 0.0), (2.6, 1.3, 13.0), cien(s, "kamien_cieply", 0.86), rot=(0, 0, 0))
        for u in (u0 + 0.4, u1 - 0.4):
            for v in (-6.4, 6.4):
                s.blok("Most słupek", (u, 0.75, v), (0.7, 1.5, 0.7), "drewno_ciemne")
    K.zajmij(278.0, 0.0, 8.0)
    # trzcina w kępach — tylko pod kulisami (|v| ≥ 37)
    with s.grupa("Przejscia/Strumyk/Trzcina"):
        for v0 in (-58.0, -49.0, -40.0, 39.0, 46.0, 54.0):
            for q in range(rnd.choice((2, 3))):
                zn = rnd.choice((-1, 1))
                rosliny.trzcina(s, rnd, (u_wody(v0) + zn * rnd.uniform(5.6, 6.6), 0.0, v0 + rnd.uniform(-1.5, 1.5)))


# =========================================================================== wydeptane pętle i polanki stref
def tropy_i_polanki(s, K):
    """Każda strefa: wydeptana pętla 2,4 st po jej węzłach (widać, gdzie chodzą potwory) i — w Lasku, Zaroślach i Leżu —
    polanka pod całym kojcem (nieregularna plama; w ciemnym borze place wilków to jaśniejsze polanki, jak w wersji 2)."""
    rnd = K.rnd_teren
    for st in K.strefy:
        pb = st["podbiom"]
        tr = st["trasa"]
        cu, cv = st["srodek"]
        if pb in POLANKI:
            with s.grupa("Teren/Polanki/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
                ru = max(abs(p[0] - cu) for p in tr)
                r0, r1 = (ru + 1.0, ru + 7.0) if pb != "leze" else (ru + 2.0, ru + 9.0)
                w = wspolne.plama(rnd, cu, cv, r0, r1, 14, 0.14)
                w = [(x, max(-35.5, min(35.5, z))) for x, z in w]          # w polu gry
                wielokat(s, "Podkładka strefy", w, Y_PLAMA + 0.04 + 0.006 * (len(st["id"]) % 2), 0.2, POLANKI[pb])
        kol, f = TROP.get(pb, ("ziemia", 0.9))
        kol_t = cien(s, kol, f)
        with s.grupa("Teren/Tropy/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
            pts = tr + [tr[0]]
            for a, b in zip(pts, pts[1:]):
                wstega(s, "Bruzda", (a[0], Y_PLAMA + 0.07, a[1]), (b[0], Y_PLAMA + 0.07, b[1]), 2.4, 0.2, kol_t)
            for a in tr:
                dysk(s, "Bruzda", a[0], Y_PLAMA + 0.068, a[1], 1.2, 0.2, kol_t)
