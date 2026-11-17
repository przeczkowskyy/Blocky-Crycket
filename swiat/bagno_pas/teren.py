# -*- coding: utf-8 -*-
"""Grunt Bagna: płyta z kolizją (wierzch 0), tafle wody bez kolizji (brodzi się), kępy-wyspy pod kojcami, błoto
Trzęsawiska, rowy przejść, Krzywa Kładka (ścieżka z desek), wydeptane pętle i niska mgła.

Poziomy wierzchów (odstęp ≥ 0,02 między płaszczyznami różnych kolorów, jak w lesie): plama gruntu 0,06; polanka błota
0,10; kałuża 0,13; woda/toń 0,18; brzeg kępy 0,24; kępa 0,28; oczko na kępie 0,30; pętla na kępie 0,32 (na błocie
0,14); kładka 0,40/0,42 na przemian, pasy desek +0,03 (≤ 0,45 = grunt w zasadach), pomost Topieli 0,30. Gracz stoi na płycie (y 0) albo na
kładce; tafla wody sięga mu do kostek. Prymitywy płaskie (wstęga, dysk, wielokąt) i plama — z modułów starego lasu.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.biom_las.teren import dysk, wielokat, wstega  # noqa: E402
from swiat.bagno_pas import rosliny  # noqa: E402
from swiat.bagno_pas.kontekst import ODCINKI_SCIEZKI, ROWY, U_PLYTY, V_MAX, v_sciezki  # noqa: E402
from swiat.las_pas.kontekst import SZER_SCIEZKI  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

Y_PLAMA, Y_POLANKA, Y_KALUZA, Y_WODA, Y_BRZEG, Y_KEPA, Y_OCZKO, Y_TROP = 0.06, 0.10, 0.13, 0.18, 0.24, 0.28, 0.30, 0.32
POLE_V = 37.5
# odcinki u z wodą na całej szerokości (pole gry + kulisy do |v| 62): (u od, u do, nazwa, kolor)
WODY = [
    (1004.0, 1016.0, "Woda", "bagno_woda"),       # rów z kładką (sam rów: ROWY[0])
    (1016.0, 1208.0, "Woda", "bagno_woda"),       # Rechotne Oczka
    (1208.0, 1228.0, "Toń", "bagno_ton"),         # Kładka nad Topielą
    (1436.0, 1628.0, "Toń", "bagno_ton"),         # Kłapiące Kępy
    (1756.0, 1850.0, "Toń", "bagno_ton"),         # Topiel Strażnika
]
# grunt bez wody (plamy na płycie): (u od, u do, nazwa, kolor)
PLAMY = [
    (936.0, 1004.0, "Plama kępy", "bagno_trawa"),          # Pomost Przybycia: zwarta łąka
    (1228.0, 1436.0, "Plama błota", "bagno_bloto"),        # Trzęsawisko i trzcinowa przesieka
    (1628.0, 1756.0, "Plama błota", "7E6A4A"),            # zatopione pnie i Leże Ropuchy: jaśniejsze, udeptane
    (1850.0, 1906.0, "Plama kępy", "bagno_trawa"),         # przedbramie i zapowiedź Dżungli
]


def plyta_i_plamy(s, K):
    """Płyta z kolizją od u 966 (las ma swoją do 966) i plamy gruntu pola gry."""
    u0, u1 = U_PLYTY
    with s.grupa("Teren/Grunt"), s.cechy(cien=False):
        s.blok("Płyta", ((u0 + u1) / 2.0, -1.0, 0.0), (u1 - u0, 2.0, 2 * V_MAX), "bagno_podloze")
    with s.grupa("Teren/Plamy"), s.cechy(kolizja=False, cien=False):
        for a, b, nazwa, kol in PLAMY:
            s.blok(nazwa, ((a + b) / 2.0, Y_PLAMA - 0.1, 0.0), (b - a, 0.2, 2 * POLE_V), kol)
        # pod kulisami przy łące: ciemniejsze błoto, żeby las nie stał na trawie
        for a, b, _, _ in PLAMY:
            for zn in (-1, 1):
                s.blok("Plama błota", ((a + b) / 2.0, Y_PLAMA - 0.1, zn * 62.0), (b - a, 0.2, 49.0), "bagno_bloto")


def wody(s, K):
    """Tafle wody bez kolizji przez pole gry i kulisy (|v| ≤ 62), rzęsa i bliki; rowy przejść."""
    rnd = K.rnd_woda
    with s.grupa("Teren/Woda"), s.cechy(kolizja=False, cien=False):
        for a, b, nazwa, kol in WODY:
            s.blok(nazwa, ((a + b) / 2.0, Y_WODA - 0.1, 0.0), (b - a, 0.2, 124.0), kol)
            n = int((b - a) / 9)
            for i in range(n):
                u = rnd.uniform(a + 2, b - 2)
                v = rnd.uniform(-58, 58)
                s.blok("Rzęsa", (u, Y_WODA + 0.02, v), (rnd.uniform(2.5, 6), 0.06, rnd.uniform(1.5, 4)), "bagno_rzesa",
                       rot=(0, rnd.uniform(0, 180), 0))
            for i in range(max(1, n // 2)):
                s.blok("Blik", (rnd.uniform(a + 2, b - 2), Y_WODA + 0.03, rnd.uniform(-34, 34)),
                       (0.5, 0.06, rnd.uniform(2.0, 3.2)), "bagno_mgla", rot=(0, rnd.uniform(-25, 25), 0))
    # rowy: ciemniejszy pas wzdłuż osi rowu (głębsza woda) — widać, że to przejście
    with s.grupa("Przejscia/Rowy"), s.cechy(kolizja=False, cien=False):
        for a, b in ROWY:
            kol = cien(s, "bagno_ton", 0.78) if b - a > 10 else cien(s, "bagno_woda", 0.8)
            s.blok("Toń", ((a + b) / 2.0, Y_WODA + 0.035, 0.0), (b - a, 0.2, 124.0), kol)


def kepy(s, K):
    """Kępy (wyspy trawy) pod kojcami Oczek i Kęp, z ciemnym brzegiem; małe oczka wody na kępach Oczek; przedbramie i
    wejście mają zwartą łąkę (plamy). Kępa leży w polu gry (|v| ≤ 35,5)."""
    rnd = K.rnd_teren
    for st in K.strefy:
        if st["podbiom"] not in ("oczka", "kepy"):
            continue
        cu, cv = st["srodek"]
        kol = "bagno_trawa_jasna" if st["podbiom"] == "oczka" else "bagno_mech"
        w = wspolne.plama(rnd, cu, cv, 25.0, 30.5, 16, 0.12)
        w = [(x, max(-35.5, min(35.5, z))) for x, z in w]
        wb = [(cu + (x - cu) * 1.07, max(-36.5, min(36.5, cv + (z - cv) * 1.07))) for x, z in w]
        with s.grupa("Teren/Kepy/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
            wielokat(s, "Kępa brzeg", wb, Y_BRZEG, 0.12, "bagno_mech" if st["podbiom"] == "oczka" else "bagno_kora")
            wielokat(s, "Kępa", w, Y_KEPA, 0.12, kol)
            if st["podbiom"] == "oczka":
                for q in range(3):
                    a = rnd.uniform(0, 2 * math.pi)
                    r = rnd.uniform(4.0, 9.0)
                    dysk(s, "Woda", cu + r * math.cos(a), Y_OCZKO, cv + r * math.sin(a), rnd.uniform(2.0, 3.4), 0.06, "bagno_woda")
    # przedbramie i wejście — kępa wokół przybycia i przed bramą (dla kształtu brzegu przy wodzie)
    for nazwa, cu, r0, r1 in (("wejscie", 978.0, 30.0, 34.0), ("przedbramie", 1864.0, 18.0, 22.0)):
        w = [(x, max(-35.5, min(35.5, z))) for x, z in wspolne.plama(rnd, cu, 0.0, r0, r1, 14, 0.1)]
        with s.grupa("Teren/Kepy/%s" % nazwa), s.cechy(kolizja=False, cien=False):
            wielokat(s, "Kępa", w, Y_KEPA - 0.06, 0.12, "bagno_trawa")


def trzesawisko(s, K):
    """Bulgotne Trzęsawisko i Leże Ropuchy: jaśniejsze polanki błota pod pętlami, kałuże z bąblami, w Trzęsawisku niska
    trzcina 0,8 między kojcami z przerwą 24 na środku (jak żywopłot w Zagrodzie lasu)."""
    rnd = K.rnd_teren
    for st in K.strefy:
        if st["podbiom"] not in ("trzesawisko", "chatka"):
            continue
        cu, cv = st["srodek"]
        ru = max(abs(p[0] - cu) for p in st["trasa"])
        w = [(x, max(-35.5, min(35.5, z))) for x, z in wspolne.plama(rnd, cu, cv, ru + 2.0, ru + 8.0, 14, 0.14)]
        with s.grupa("Teren/Polanki/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
            wielokat(s, "Błoto", w, Y_POLANKA + 0.006 * (len(st["id"]) % 2), 0.12, "bagno_bloto_jasne")
            for q in range(4 if st["podbiom"] == "trzesawisko" else 7):
                a = rnd.uniform(0, 2 * math.pi)
                r = rnd.uniform(5.0, 12.0) if st["podbiom"] == "trzesawisko" else rnd.uniform(6.0, 30.0)
                x, z = cu + r * math.cos(a), cv + r * math.sin(a)
                dysk(s, "Kałuża woda", x, Y_KALUZA + 0.002 * q, z, rnd.uniform(1.6, 3.0), 0.06, "bagno_woda")
                for b in range(2):
                    s.kula("Bąbel", (x + rnd.uniform(-1, 1), Y_KALUZA + 0.12, z + rnd.uniform(-1, 1)), rnd.uniform(0.35, 0.6),
                           "bagno_mgla")
    with s.grupa("Trzesawisko/Przegrodki"), s.cechy(kolizja=False):
        for u in (1292.0, 1356.0):
            for zn in (-1, 1):
                v = 12.0
                while v < 36.0:
                    dl = rnd.uniform(3.2, 4.4)
                    s.blok("Trzcina", (u + rnd.uniform(-0.4, 0.4), 0.4, zn * (v + dl / 2.0)), (1.6, 0.8, dl),
                           rnd.choice(("bagno_trzcina", "trzcina", cien(s, "bagno_trzcina", 0.85))),
                           rot=(0, rnd.uniform(-8, 8), rnd.uniform(-4, 4)))
                    v += dl * 0.9
                K.zajmij(u, zn * 24.0, 2.0)


def kladka(s, K, Z):
    """Krzywa Kładka: pomost z desek po osi (v_sciezki) odcinkami ok. 10–13 st; każdy odcinek lekko skręcony i na przemian
    0,40 / 0,42; dwa ciemne pasy desek wzdłuż, pale przy stykach (wycofywane, gdy wchodzą w pętlę potworów); nad rowami
    przejść kładka 12 szer., nad Topielą z poręczami do 1,4. Zwraca liczbę odcinków."""
    rnd = K.rnd_sciezka
    n = 0
    with s.grupa("Sciezka"):
        for a, b in ODCINKI_SCIEZKI:
            pts = [a]
            u = a
            while u < b - 1e-6:
                u = min(b, u + rnd.uniform(10.0, 13.0))
                if b - u < 4.0:
                    u = b
                pts.append(u)
            for u0, u1 in zip(pts, pts[1:]):
                y = 0.42 if n % 2 == 0 else 0.40
                szer = SZER_SCIEZKI + rnd.uniform(0.2, 0.6)
                pa, pb = (u0 - 0.6, y, v_sciezki(u0)), (u1 + 0.6, y, v_sciezki(u1))
                with s.cechy(cien=False):
                    wstega(s, "Kładka deska", pa, pb, szer, 0.3, "bagno_deska" if n % 3 else cien(s, "bagno_deska", 0.93),
                           rot_dod=rnd.uniform(-1.5, 1.5))
                with s.cechy(kolizja=False, cien=False):
                    for dv in (-1.7, 1.9):
                        wstega(s, "Kładka deska", (pa[0] + 0.4, y + 0.03, pa[2] + dv), (pb[0] - 0.4, y + 0.03, pb[2] + dv), 0.35, 0.05,
                               "bagno_deska_ciemna")
                n += 1
                if n % 2 == 0:
                    for zn in (-1, 1):
                        vv = v_sciezki(u0) + zn * (szer / 2.0 + 0.3)

                        def bud(u0=u0, vv=vv):
                            s.walec("Kładka pal", (u0, 0.4, vv), 0.35, 1.2, "bagno_deska_ciemna", "Wood", os="y",
                                    rot=(rnd.uniform(-6, 6), 0, rnd.uniform(-6, 6)))
                        postaw(s, Z, bud)
    # nad rowami: szersza kładka (12) z palami w wodzie; nad Topielą poręcze ≤ 1,4
    with s.grupa("Przejscia/Kladki"):
        for k, (a, b) in enumerate(ROWY):
            u0, u1 = a - 2.5, b + 2.5
            with s.cechy(cien=False):
                wstega(s, "Kładka deska", (u0, 0.41, 0.0), (u1, 0.41, 0.0), 12.0, 0.28, "bagno_deska")
            with s.cechy(kolizja=False, cien=False):
                for vv in (-4.2, -1.4, 1.4, 4.2):
                    wstega(s, "Kładka deska", (u0 + 0.3, 0.44, vv), (u1 - 0.3, 0.44, vv), 0.3, 0.05, "bagno_deska_ciemna")
            for uu in (u0 + 0.8, (u0 + u1) / 2.0, u1 - 0.8):
                for vv in (-6.3, 6.3):
                    h = 1.4 if k == 1 else 0.9
                    s.walec("Kładka pal", (uu, h / 2.0 - 0.1, vv), 0.4, h + 0.2, "bagno_deska_ciemna", "Wood", os="y")
            if k == 1:
                with s.cechy(kolizja=False):
                    for vv in (-6.3, 6.3):
                        s.belka("Kładka poręcz", (u0 + 0.8, 1.25, vv), (u1 - 0.8, 1.2, vv), 0.3, "bagno_deska", "Wood")
            K.zajmij((a + b) / 2.0, 0.0, 7.0)
    return n


def tropy(s, K):
    """Wydeptana pętla 2,4 st po węzłach każdej strefy (widać, gdzie chodzą potwory)."""
    for st in K.strefy:
        na_kepie = st["podbiom"] in ("oczka", "kepy")
        y = Y_TROP if na_kepie else Y_POLANKA + 0.04
        kol = cien(s, "bagno_trawa", 0.78) if na_kepie else cien(s, "bagno_bloto_jasne", 0.82)
        with s.grupa("Teren/Tropy/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
            pts = st["trasa"] + [st["trasa"][0]]
            for a, b in zip(pts, pts[1:]):
                wstega(s, "Bruzda", (a[0], y, a[1]), (b[0], y, b[1]), 2.4, 0.06, kol)
            for a in st["trasa"]:
                dysk(s, "Bruzda", a[0], y - 0.002, a[1], 1.2, 0.06, kol)


def mgla(s, K, Z, ile_pole=14, ile_kulisy=12):
    """Niska mgła: płaskie półprzezroczyste ławice-dyski (0,75–1,25 nad gruntem — poniżej placu walki 1,6) nad polem gry i w
    kulisach. Ławice nad polem gry nie sięgają ścieżki wyżej niż 1,25 (ścieżka zwalnia mgłę z zasady). Zwraca liczbę."""
    rnd = K.rnd_mgla
    n = 0
    with s.grupa("Mgla"), s.cechy(kolizja=False, cien=False):
        for i in range(ile_pole):
            u = 1000.0 + (840.0 / ile_pole) * (i + rnd.uniform(0.2, 0.8))
            v = rnd.uniform(-20, 20)

            def bud(u=u, v=v):
                s.walec("Mgła bagna", (u, 1.0, v), rnd.uniform(11, 17), 0.5, "bagno_mgla", os="y", alfa=0.72)
            n += 1 if postaw(s, Z, bud) else 0
        for i in range(ile_kulisy):
            u = 990.0 + (860.0 / ile_kulisy) * (i + rnd.uniform(0.1, 0.9))
            zn = -1 if i % 2 else 1

            def bud(u=u, zn=zn):
                s.walec("Mgła bagna", (u, rnd.uniform(1.8, 3.2), zn * rnd.uniform(46, 54)), rnd.uniform(14, 20),
                        rnd.uniform(1.4, 2.2), "bagno_mgla", os="y", alfa=0.62)
            n += 1 if postaw(s, Z, bud) else 0
    return n


def lilie(s, K, Z):
    """Liście grzybieni na wodzie (pole gry poza kępami i w kulisach), czasem z kwiatem. Zwraca liczbę."""
    rnd = K.rnd_woda
    n = 0
    for a, b, _, _ in WODY:
        for i in range(int((b - a) / 4.5)):
            u = rnd.uniform(a + 1, b - 1)
            v = rnd.uniform(-60, 60)
            if abs(v) < 36 and a > 1015 and (b - a) > 100:
                # na kępach liści nie ma — tylko w wodzie między kępami (blisko granic kojców) albo przy ścianach
                kojec = min((abs(u - st["srodek"][0]) for st in K.strefy), default=99)
                if kojec < 26 and abs(v) < 30:
                    continue
            with s.grupa("Detale/Lilie"):
                rosliny.grzybien(s, rnd, (u, 0.18, v), rnd.uniform(0.7, 1.4),
                                 kwiat=rnd.choice((None, None, None, "biel", "bagno_kwiat", "tynk_brzoskwinia")))
            n += 1
    return n
