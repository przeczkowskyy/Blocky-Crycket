# -*- coding: utf-8 -*-
"""Grunt Dżungli: płyta z kolizją (wierzch 0), plamy gruntu (łąka, ciemne runo, wilgotna ziemia Kwietnika, piasek Gaju,
łąka Kręgu), turkusowe strumienie przejść i sadzawka Kręgu bez kolizji (brodzi się), polanki pod kojcami, grządki
i żywopłoty kwiatowe Kwietnika, posadzka ruin, Dróżka (ubita ziemia, w ruinach kamienne płyty), wydeptane pętle,
plamy światła, mgiełka nad wodą i liście na wodzie.

Poziomy wierzchów (odstęp ≥ 0,02 między płaszczyznami różnych kolorów, jak w lesie i Bagnie): plama gruntu 0,06;
grządka 0,10; kałuża 0,13; woda 0,18; brzeg polanki 0,24; polanka / posadzka 0,28; pętla 0,32; plama światła 0,34;
Dróżka 0,36/0,38 na przemian (z kolizją, koleiny +0,03 ≤ 0,45 = grunt w zasadach), mostki 0,41–0,44, posadzka Kręgu 0,30.
Gracz stoi na płycie (y 0), na Dróżce albo na mostku; tafla wody sięga mu do kostek. Prymitywy płaskie (wstęga, dysk,
wielokąt) i plama — z modułów starego lasu.
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
from swiat.dzungla_pas import rosliny  # noqa: E402
from swiat.dzungla_pas.kontekst import D, ODCINKI_SCIEZKI, ROWY, U_PLYTY, V_MAX, v_sciezki  # noqa: E402
from swiat.las_pas.kontekst import SZER_SCIEZKI  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

Y_PLAMA, Y_GRZADKA, Y_KALUZA, Y_WODA, Y_BRZEG, Y_POLANKA, Y_TROP, Y_SWIATLO = 0.06, 0.10, 0.13, 0.18, 0.24, 0.28, 0.32, 0.34
POLE_V = 37.5
WODA_NAZWY = ("Woda", "Toń", "Brzeg wody", "Kałuża woda", "Sadzawka", "Kaskada", "Wodospad", "Piana", "Blik", "Mgiełka")
# odcinki u z wodą na całej szerokości (pole gry + kulisy do |v| 62): (u od, u do, nazwa, kolor)
WODY = [
    (1004.0 + D, 1016.0 + D, "Woda", "dz_woda"),          # Turkusowy strumyk (sam nurt: ROWY[0])
    (1208.0 + D, 1228.0 + D, "Woda", "dz_woda"),          # Mostek nad Kaskadą
    (1756.0 + D, 1850.0 + D, "Sadzawka", "dz_woda"),      # Krąg Stu Lian — wyspa w sadzawce
]
# grunt bez wody (plamy na płycie): (u od, u do, nazwa, kolor)
PLAMY = [
    (936.0 + D, 1004.0 + D, "Plama trawy", "dz_trawa"),         # Taras Przybycia: łąka
    (1016.0 + D, 1208.0 + D, "Plama runa", "dz_runo"),          # Polana Zwijogonów: ciemne runo, jasne polanki
    (1228.0 + D, 1420.0 + D, "Plama ziemi", "dz_ziemia"),       # Kwietnik Gębokwiatów: wilgotna ziemia
    (1420.0 + D, 1436.0 + D, "Plama runa", "dz_runo"),          # bambusowa przesieka
    (1436.0 + D, 1628.0 + D, "Plama piasku", "dz_piasek_gaju"),  # Gaj Kokosów
    (1628.0 + D, 1756.0 + D, "Plama runa", "dz_runo_jasne"),    # schody, Ruiny Pancernika, Brama Posągów
    (1850.0 + D, 1906.0 + D, "Plama trawy", "dz_trawa"),        # przedbramie i zapowiedź Pustyni (piasek w zapowiedzi)
]


def plyta_i_plamy(s, K):
    """Płyta z kolizją od u 1906 (Bagno ma swoją do 1906) i plamy gruntu pola gry; pod kulisami ciemne runo."""
    u0, u1 = U_PLYTY
    with s.grupa("Teren/Grunt"), s.cechy(cien=False):
        s.blok("Płyta", ((u0 + u1) / 2.0, -1.0, 0.0), (u1 - u0, 2.0, 2 * V_MAX), "dz_podloze")
    with s.grupa("Teren/Plamy"), s.cechy(kolizja=False, cien=False):
        for a, b, nazwa, kol in PLAMY:
            s.blok(nazwa, ((a + b) / 2.0, Y_PLAMA - 0.1, 0.0), (b - a, 0.2, 2 * POLE_V), kol)
        for a, b, _, _ in PLAMY + [(w[0], w[1], 0, 0) for w in WODY]:
            for zn in (-1, 1):
                s.blok("Plama runa", ((a + b) / 2.0, Y_PLAMA - 0.1, zn * 62.0), (b - a, 0.2, 49.0), "dz_runo_ciemne")


def wody(s, K):
    """Tafle turkusowej wody bez kolizji przez pole gry i kulisy (|v| ≤ 62) i bliki; nurty strumieni (głębszy kolor)."""
    rnd = K.rnd_woda
    with s.grupa("Teren/Woda"), s.cechy(kolizja=False, cien=False):
        for a, b, nazwa, kol in WODY:
            s.blok(nazwa, ((a + b) / 2.0, Y_WODA - 0.1, 0.0), (b - a, 0.2, 124.0), kol)
            for i in range(max(2, int((b - a) / 6))):
                s.blok("Blik", (rnd.uniform(a + 2, b - 2), Y_WODA + 0.03, rnd.uniform(-34, 34)),
                       (0.5, 0.06, rnd.uniform(2.0, 3.2)), "dz_piana", rot=(0, rnd.uniform(-25, 25), 0))
    with s.grupa("Przejscia/Strumienie"), s.cechy(kolizja=False, cien=False):
        for a, b in ROWY:
            s.blok("Woda", ((a + b) / 2.0, Y_WODA + 0.035, 0.0), (b - a, 0.2, 124.0), "dz_woda_gleboka")
            for i in range(6):                                 # smugi nurtu w poprzek (woda płynie od kaskad do środka)
                s.blok("Blik", ((a + b) / 2.0 + rnd.uniform(-2, 2), Y_WODA + 0.07, rnd.uniform(-30, 30)),
                       (0.45, 0.06, rnd.uniform(3.0, 5.0)), "dz_woda_jasna", rot=(0, rnd.uniform(-8, 8), 0))


def polanki(s, K):
    """Polanki pod kojcami (wyspy jaśniejszego gruntu z brzegiem): słoneczne pod Zwijogonami, mchowe pod Gębokwiatami,
    trawiaste pod Kokosowymi Siłaczami; pod Pancernikiem spękana kamienna posadzka z mchem. Wejście i przedbramie mają
    zwartą łąkę."""
    rnd = K.rnd_teren
    kol = {"zwijogony": ("dz_trawa_jasna", "dz_trawa"), "gebokwiaty": ("dz_mech", "dz_grzadka"),
           "kokosy": ("dz_runo_jasne", "dz_palma")}
    for st in K.strefy:
        cu, cv = st["srodek"]
        if st["podbiom"] == "ruiny":
            posadzka_ruin(s, K, st)
            continue
        k_w, k_b = kol[st["podbiom"]]
        w = wspolne.plama(rnd, cu, cv, 25.0, 30.5, 12, 0.12)
        w = [(x, max(-35.5, min(35.5, z))) for x, z in w]
        wb = [(cu + (x - cu) * 1.07, max(-36.5, min(36.5, cv + (z - cv) * 1.07))) for x, z in w]
        with s.grupa("Teren/Polanki/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
            wielokat(s, "Polanka brzeg", wb, Y_BRZEG, 0.12, k_b)
            wielokat(s, "Polanka", w, Y_POLANKA, 0.12, k_w)
    for nazwa, cu, r0, r1 in (("wejscie", 978.0 + D, 30.0, 34.0), ("przedbramie", 1868.0 + D, 14.0, 18.0)):
        w = [(x, max(-35.5, min(35.5, z))) for x, z in wspolne.plama(rnd, cu, 0.0, r0, r1, 12, 0.1)]
        with s.grupa("Teren/Polanki/%s" % nazwa), s.cechy(kolizja=False, cien=False):
            wielokat(s, "Polanka", w, Y_POLANKA - 0.06, 0.12, "dz_trawa_jasna" if nazwa == "wejscie" else "dz_trawa")


def posadzka_ruin(s, K, st):
    """Spękana posadzka ruin pod pętlą Pancernika: siatka płyt 5,5 st w trzech kamieniach (część brakuje, część
    przekrzywiona w poziomie), łaty mchu. Wszystko płaskie (wierzch 0,28), bez kolizji."""
    rnd = K.rnd_teren
    cu, cv = st["srodek"]
    with s.grupa("Teren/Posadzka/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
        krok = 5.6
        n = 0
        for i in range(-6, 7):
            for j in range(-6, 7):
                u, v = cu + i * krok + rnd.uniform(-0.3, 0.3), cv + j * krok + rnd.uniform(-0.3, 0.3)
                if abs(v) > 34.5 or ((u - cu) / 32.0) ** 2 + ((v - cv) / 31.0) ** 2 > 1.0 or rnd.random() < 0.18:
                    continue
                kol = rnd.choice(("dz_kamien", "dz_kamien", "dz_kamien_jasny", "dz_kamien_ciemny"))
                s.blok("Posadzka", (u, Y_POLANKA - 0.06, v), (krok - 0.5, 0.12, krok - 0.5), kol, rot=(0, rnd.uniform(-6, 6), 0))
                n += 1
                if rnd.random() < 0.22:
                    s.blok("Mech", (u + rnd.uniform(-1, 1), Y_POLANKA - 0.0, v + rnd.uniform(-1, 1)),
                           (rnd.uniform(1.6, 3.2), 0.06, rnd.uniform(1.4, 2.8)), "dz_mech", rot=(0, rnd.uniform(0, 90), 0))
    return n


def kwietnik(s, K):
    """Kwietnik Gębokwiatów: grządki (ciemna ziemia z rzędem kwiatów) między kojcami i pod ścianami, niskie żywopłoty
    kwiatowe 0,8 dzielą trzy kojce (przerwa 24 na środku — jak trzcina Trzęsawiska Bagna)."""
    rnd = K.rnd_teren
    q = K.przegrody["gebokwiaty"]
    granice = [q["u_od"] + 64.0, q["u_od"] + 128.0]
    with s.grupa("Kwietnik/Przegrodki"), s.cechy(kolizja=False):
        for u in granice:
            for zn in (-1, 1):
                v = 12.0
                while v < 36.0:
                    dl = rnd.uniform(3.2, 4.4)
                    s.blok("Żywopłot", (u + rnd.uniform(-0.3, 0.3), 0.4, zn * (v + dl / 2.0)), (1.6, 0.8, dl),
                           rnd.choice(("dz_lisc_ciemny", "dz_korona", cien(s, "dz_lisc_ciemny", 0.9))),
                           rot=(0, rnd.uniform(-6, 6), rnd.uniform(-3, 3)))
                    with s.cechy(cien=False):
                        s.blok("Kwiat", (u + rnd.uniform(-0.4, 0.4), 0.85, zn * (v + dl * rnd.uniform(0.2, 0.8))), (0.8, 0.25, 0.8),
                               rnd.choice(("dz_kwiat_czerwony", "dz_kwiat_zolty")), rot=(0, 45, 0))
                    v += dl * 0.9
                K.zajmij(u, zn * 24.0, 2.0)
    # grządki pod ścianami: po obu stronach żywopłotów i na skrajach Kwietnika (|v| 26–35), na nich kępy kwiatów
    pasy = [u + du for u in granice for du in (-2.6, 2.6)] + [q["u_od"] + 3.0, q["u_do"] - 3.0]
    for u in pasy:
        for zn in (-1, 1):
            with s.grupa("Kwietnik/Grzadki"), s.cechy(kolizja=False, cien=False):
                s.blok("Grządka", (u, Y_GRZADKA - 0.06, zn * 30.5), (2.2, 0.12, 9.0), "dz_grzadka")
                for v in (27.5, 30.5, 33.5):
                    rosliny.kepa_kwiatow(s, rnd, (u + rnd.uniform(-0.3, 0.3), Y_GRZADKA, zn * (v + rnd.uniform(-0.6, 0.6))),
                                         rnd.choice((("dz_kwiat_czerwony", "dz_kwiat_zolty"), ("dz_kwiat_czerwony", "dz_kwiat_czerwony"),
                                                     ("dz_kwiat_zolty", "dz_owoc"))))
            K.zajmij(u, zn * 30.5, 2.0)


def drozka(s, K, Z):
    """Dróżka: ubita ziemia po osi (v_sciezki) odcinkami ok. 10–13 st; każdy lekko skręcony i na przemian 0,36 / 0,38,
    z kolizją (gracz po niej chodzi); dwie ciemniejsze koleiny wzdłuż; w ruinach i przed Kręgiem kamienne płyty zamiast
    ziemi. Nad strumieniami mostki (grupa Przejscia/Mostki): z desek nad Turkusowym strumykiem, kamienny z balustradą
    do 1,4 nad Kaskadą. Zwraca liczbę odcinków."""
    rnd = K.rnd_sciezka
    n = 0
    u_kamien = 1628.0 + D                                    # od omszałych schodów Dróżka jest z kamiennych płyt
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
                y = 0.38 if n % 2 == 0 else 0.36
                szer = SZER_SCIEZKI + rnd.uniform(0.2, 0.6)
                pa, pb = (u0 - 0.6, y, v_sciezki(u0)), (u1 + 0.6, y, v_sciezki(u1))
                kamien = u0 >= u_kamien
                with s.cechy(cien=False):
                    wstega(s, "Dróżka kamienna" if kamien else "Dróżka", pa, pb, szer, 0.3,
                           "dz_kamien_ciemny" if kamien else ("dz_droga" if n % 3 else cien(s, "dz_droga", 0.93)),
                           rot_dod=rnd.uniform(-1.5, 1.5))
                with s.cechy(kolizja=False, cien=False):
                    if kamien:
                        x = u0 + 0.8
                        while x < u1 - 1.0:
                            dl = rnd.uniform(1.8, 2.8)
                            for dv in (-2.1, 2.1):
                                vv = v_sciezki(x + dl / 2.0) + dv + rnd.uniform(-0.3, 0.3)
                                s.blok("Płyta ścieżki", (x + dl / 2.0, y + 0.03, vv), (dl - 0.25, 0.06, 3.8),
                                       rnd.choice(("dz_kamien", "dz_kamien_jasny", "dz_kamien")), rot=(0, rnd.uniform(-5, 5), 0))
                            x += dl
                    else:
                        for dv in (-1.9, 1.9):
                            wstega(s, "Koleina", (pa[0] + 0.4, y + 0.03, pa[2] + dv), (pb[0] - 0.4, y + 0.03, pb[2] + dv), 0.5, 0.05,
                                   "dz_droga_ciemna")
                n += 1
    # mostki nad strumieniami
    with s.grupa("Przejscia/Mostki"):
        for k, (a, b) in enumerate(ROWY):
            u0, u1 = a - 2.5, b + 2.5
            if k == 0:
                with s.cechy(cien=False):
                    wstega(s, "Kładka deska", (u0, 0.41, 0.0), (u1, 0.41, 0.0), 12.0, 0.28, "drewno")
                with s.cechy(kolizja=False, cien=False):
                    for vv in (-4.2, -1.4, 1.4, 4.2):
                        wstega(s, "Kładka deska", (u0 + 0.3, 0.44, vv), (u1 - 0.3, 0.44, vv), 0.3, 0.05, "drewno_ciemne")
                for uu in (u0 + 0.8, (u0 + u1) / 2.0, u1 - 0.8):
                    for vv in (-6.3, 6.3):
                        s.walec("Kładka pal", (uu, 0.35, vv), 0.4, 1.1, "drewno_ciemne", "Wood", os="y")
                with s.cechy(kolizja=False):
                    for vv in (-6.3, 6.3):                        # liny z liany zamiast poręczy (≤ 1,1)
                        rosliny.liana(s, rnd, (u0 + 0.8, 0.95, vv), (u1 - 0.8, 0.95, vv), zwis=0.3, grub=0.22, liscie=1)
            else:
                with s.cechy(cien=False):
                    wstega(s, "Mostek kamień", (u0, 0.42, 0.0), (u1, 0.42, 0.0), 12.0, 0.4, "dz_kamien")
                with s.cechy(kolizja=False, cien=False):
                    for vv in (-3.0, 0.0, 3.0):
                        wstega(s, "Płyta ścieżki", (u0 + 0.4, 0.45, vv), (u1 - 0.4, 0.45, vv), 2.6, 0.05, "dz_kamien_jasny")
                for vv in (-6.3, 6.3):
                    s.blok("Mostek balustrada", ((u0 + u1) / 2.0, 0.85, vv), (u1 - u0 - 1.0, 0.9, 0.7), "dz_kamien_ciemny", "Slate")
                    for uu in (u0 + 0.6, u1 - 0.6):
                        s.blok("Mostek słupek", (uu, 0.7, vv), (1.0, 1.4, 1.0), "dz_kamien", "Slate")
                        with s.cechy(kolizja=False, cien=False):
                            s.blok("Znak", (uu, 1.25, vv - math.copysign(0.52, vv)), (0.5, 0.5, 0.06), "dz_znak", "Neon",
                                   rot=(0, 0, 45))
                with s.cechy(kolizja=False, cien=False):
                    for vv in (-6.3, 6.3):
                        s.blok("Mech", ((u0 + u1) / 2.0 + rnd.uniform(-4, 4), 1.33, vv), (rnd.uniform(3, 6), 0.1, 0.8), "dz_mech")
            K.zajmij((a + b) / 2.0, 0.0, 7.0)
    return n


def tropy(s, K):
    """Wydeptana pętla 2,4 st po węzłach każdej strefy (widać, gdzie chodzą potwory)."""
    kol = {"zwijogony": cien(s, "dz_trawa", 0.8), "gebokwiaty": cien(s, "dz_grzadka", 0.95),
           "kokosy": cien(s, "dz_piasek_gaju", 0.82), "ruiny": cien(s, "dz_kamien_ciemny", 0.9)}
    for st in K.strefy:
        with s.grupa("Teren/Tropy/%s" % st["id"]), s.cechy(kolizja=False, cien=False):
            pts = st["trasa"] + [st["trasa"][0]]
            for a, b in zip(pts, pts[1:]):
                wstega(s, "Bruzda", (a[0], Y_TROP, a[1]), (b[0], Y_TROP, b[1]), 2.4, 0.06, kol[st["podbiom"]])
            for a in st["trasa"]:
                dysk(s, "Bruzda", a[0], Y_TROP - 0.002, a[1], 1.2, 0.06, kol[st["podbiom"]])


def plamy_swiatla(s, K, ile=70):
    """Plamy światła na ziemi (słońce przez dziury w koronach): płaskie jasnożółte łaty bez Neonu w polu gry, najwięcej
    na Polanie Zwijogonów i w Gaju. Płaskie, więc mogą leżeć na placach walki. Zwraca liczbę."""
    rnd = K.rnd_teren
    wagi = {"zwijogony": 3.0, "kokosy": 2.0, "gebokwiaty": 1.2, "ruiny": 1.5, "wejscie": 1.0, "krag": 0.6}
    n = 0
    for _ in range(ile * 8):
        if n >= ile:
            break
        u = rnd.uniform(944.0 + D, 1846.0 + D)
        v = rnd.uniform(-33.0, 33.0)
        o = K.odcinek(u)
        if rnd.random() * 3.0 > wagi.get(o, 0.0) or K.w_wodzie(u, 3.0) or K.min_pole("d_sciezka", u, v, 3.5) < 0.5:
            continue
        if any(a <= u <= b for a, b, _, _ in WODY):
            continue
        with s.grupa("Teren/Swiatlo"), s.cechy(kolizja=False, cien=False):
            r = rnd.uniform(1.6, 3.4)
            dysk(s, "Plama światła", u, Y_SWIATLO, v, r, 0.06, "dz_swiatlo")
        n += 1
    return n


def mgla(s, K, Z, ile=12):
    """Mgiełka nad wodą: płaskie półprzezroczyste ławice (0,75–1,25 nad gruntem — poniżej placu walki 1,6) nad
    strumieniami, przy kaskadach, pod wodospadem i nad sadzawką Kręgu. Zwraca liczbę."""
    rnd = K.rnd_mgla
    miejsca = []
    for a, b in ROWY:
        for zn in (-1, 1):
            miejsca.append(((a + b) / 2.0, zn * rnd.uniform(14, 28), rnd.uniform(6, 9), 1.0))
            miejsca.append(((a + b) / 2.0, zn * rnd.uniform(44, 52), rnd.uniform(8, 11), 1.8))
    zk = K.znaki["kaskada_gaju"]
    miejsca.append((zk["u"] + rnd.uniform(-2, 2), zk["v"] - 1.0, 6.5, 1.1))
    for i in range(5):
        a = math.radians(30 + 72 * i + rnd.uniform(-15, 15))
        cu, cv = K.straznik["arena"]["srodek"]
        miejsca.append((cu + 33.0 * math.cos(a), cv + 33.0 * math.sin(a), rnd.uniform(7, 10), 1.0))
    n = 0
    with s.grupa("Mgla"), s.cechy(kolizja=False, cien=False):
        for u, v, r, y in miejsca[:ile]:
            def bud(u=u, v=v, r=r, y=y):
                s.walec("Mgiełka", (u, y, v), r, 0.5, "dz_mgla", os="y", alfa=0.72)
            n += 1 if postaw(s, Z, bud) else 0
    return n


def lilie(s, K, Z):
    """Liście na wodzie (strumienie poza mostkami, sadzawka Kręgu poza posadzką), czasem z kwiatem. Zwraca liczbę."""
    rnd = K.rnd_woda
    n = 0
    cu, cv = K.straznik["arena"]["srodek"]
    for a, b, _, _ in WODY:
        for i in range(int((b - a) / 2.2)):
            u = rnd.uniform(a + 1, b - 1)
            v = rnd.uniform(-58, 58)
            if abs(v) < 8.0 or math.hypot(u - cu, v - cv) < 29.0:
                continue
            with s.grupa("Detale/Lilie"):
                rosliny.lisc_wodny(s, rnd, (u, Y_WODA, v), rnd.uniform(0.7, 1.4),
                                   kwiat=rnd.choice((None, None, "biel", "dz_kwiat_rozowy", "dz_kwiat_zolty")))
            n += 1
    return n
