# -*- coding: utf-8 -*-
"""Kulisy Dżungli: gęsta ściana zieleni po obu stronach pola gry (|v| 36–58), tło za nią (|v| 63–80), niewidzialne
ściany, liany między drzewami, wiszące mosty z lian, ruiny w kulisach i drobiazgi przy Dróżce. Rzędy jak w lesie-pasie
i Bagnie: skraj (podszyt, bez kolizji), przód (kolizja pnia), drugi rząd i głąb (bez kolizji), tło (bez kolizji
i cienia) — piętra: podszyt (krzewy, paprocie, kwiaty) → średnie (paprocie drzewiaste, kępy liści-parasoli, palmy)
→ olbrzymy (drzewa dżungli, figowce) → tło.

Kulisy Dżungli zaczynają się na u 1910: do u 1906 stoją kulisy Bagna-pasa (za jego bramą zostają jako skraj Bagna).
Grupy: Kulisy/<Lewa|Prawa>/O_<nn> i Tlo/<Lewa|Prawa>/O_<nn> co 64 st (w Studio LevelOfDetail = StreamingMesh).
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale, rosliny as rosliny_lasu, skaly  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.dzungla_pas import miejsca, rosliny  # noqa: E402
from swiat.dzungla_pas.kontekst import D, ODCINKI_SCIEZKI, U_MAX, U_MIN, U_SCIANY, v_sciezki  # noqa: E402
from swiat.las_pas.kontekst import SZER_SCIEZKI, WIDOCZNA_SCIANA  # noqa: E402
from swiat.las_pas.kulisy import ODCIEN, _losuj, bez_kolizji  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

U_KULIS = 970.0 + D
ODCINEK_KULIS = 64.0
DRZ, FIG, PAL, PAR, PAP, BAM, KAK = "drzewo", "figowiec", "palma", "parasole", "paproc_drzewiasta", "bambus", "kaktus"
ZESTAW = {
    "wejscie":  {"przod": [(DRZ, 2, (0.9, 1.1)), (PAL, 2, (0.95, 1.15)), (PAR, 2, (0.95, 1.2)), (PAP, 1, (0.9, 1.1))], "krok": 8.0,
                 "skraj": [("kwiat", 2), ("krzew", 2), ("paproc", 2)], "glab": (DRZ, "dz_sylweta_1")},
    "turkusowy_strumyk": {"przod": [(PAR, 2, (1.0, 1.2)), (PAP, 1, (0.9, 1.1))], "krok": 8.0, "skraj": [("paproc", 1)],
                          "glab": (DRZ, "dz_sylweta_1")},
    "zwijogony": {"przod": [(DRZ, 3, (0.9, 1.15)), (PAR, 2, (1.0, 1.25)), (PAP, 2, (0.95, 1.2)), (FIG, 1, (0.9, 1.05))], "krok": 7.5,
                  "skraj": [("krzew", 3), ("paproc", 3), ("kwiat", 1), ("swiecacy", 1)], "glab": (DRZ, "dz_sylweta_1")},
    "mostek_nad_kaskada": {"przod": [(PAR, 1, (1.0, 1.2)), (PAP, 1, (0.9, 1.1))], "krok": 8.0, "skraj": [("paproc", 1)],
                           "glab": (DRZ, "dz_sylweta_1")},
    "gebokwiaty": {"przod": [(FIG, 2, (0.9, 1.1)), (DRZ, 2, (0.9, 1.1)), (PAR, 2, (1.0, 1.2)), (PAP, 1, (0.9, 1.1))], "krok": 7.5,
                   "skraj": [("swiecacy", 2), ("kwiaty", 3), ("krzew", 2), ("paproc", 1)], "glab": (FIG, "dz_sylweta_1")},
    "bambusowa_przesieka": {"przod": [(BAM, 1, (1.0, 1.2))], "krok": 8.0, "skraj": [], "glab": (DRZ, "dz_sylweta_1")},
    "kokosy":   {"przod": [(PAL, 4, (0.95, 1.25)), (DRZ, 1, (0.9, 1.05)), (PAR, 1, (1.0, 1.2))], "krok": 7.0,
                 "skraj": [("krzew", 2), ("kokosy", 1), ("paproc", 2)], "glab": (PAL, "dz_sylweta_1")},
    "kamienne_schody": {"przod": [(DRZ, 1, (0.9, 1.1))], "krok": 9.0, "skraj": [], "glab": ("kulisa", "dz_sylweta_1")},
    "ruiny":    {"przod": [(FIG, 2, (0.95, 1.15)), (DRZ, 2, (0.9, 1.1)), (PAP, 1, (0.9, 1.1))], "krok": 8.0,
                 "skraj": [("glaz", 2), ("paproc", 2), ("swiecacy", 1)], "glab": ("kulisa", "dz_sylweta_1")},
    "brama_posagow": {"przod": [(DRZ, 1, (0.95, 1.1))], "krok": 8.0, "skraj": [("paproc", 1)], "glab": (DRZ, "dz_sylweta_1")},
    "krag":     {"przod": [(DRZ, 3, (1.0, 1.25)), (FIG, 1, (0.95, 1.1)), (PAL, 1, (1.0, 1.15)), (PAR, 1, (1.0, 1.2))], "krok": 8.0,
                 "skraj": [("swiecacy", 2), ("paproc", 2)], "glab": (DRZ, "dz_sylweta_1")},
    "przedbramie": {"przod": [(PAL, 2, (0.95, 1.15)), (DRZ, 1, (0.9, 1.05)), (PAR, 1, (1.0, 1.2))], "krok": 8.0,
                    "skraj": [("krzew", 2), ("kwiat", 1)], "glab": (DRZ, "dz_sylweta_1")},
    "pustynia": {"przod": [(PAL, 2, (1.0, 1.2)), (KAK, 2, (1.1, 1.5))], "krok": 7.0, "skraj": [("sucha", 2)],
                 "glab": (PAL, "dz_sylweta_2")},
}


def zestaw(K, u):
    o = K.odcinek(u)
    if o == "krag" and u >= 1848.0 + D:
        o = "przedbramie"
    if o == "krag" and u >= 1876.0 + D or o == "pustynia":
        o = "pustynia"
    if o not in ZESTAW:
        o = "wejscie"
    z = ZESTAW[o]
    return o, z


def drzewo(s, rnd, rodzina, pos, k, lekka=False):
    """Jedna roślina kulis z rodzin Dżungli (swiat/dzungla_pas/rosliny.py) albo kaktus zapowiedzi Pustyni. lekka = dalsze
    rzędy: palma bez kokosów i z 4 liśćmi, drzewo bez liany, figowiec bez owoców."""
    ry = 15.0 * rnd.randint(0, 23)
    f = rnd.choice(ODCIEN)
    if rodzina == DRZ:
        rosliny.drzewo_dzungli(s, rnd, pos, k, ry, f, liana_=(not lekka) and rnd.random() < 0.35, korzenie=2 if lekka else 3,
                               tusz=not lekka)
    elif rodzina == FIG:
        rosliny.figowiec(s, rnd, pos, k, ry, f, owoce=(not lekka) and rnd.random() < 0.5)
    elif rodzina == PAL:
        rosliny.palma(s, rnd, pos, k, ry, f, liscie=5, kokosy=0 if lekka else rnd.choice((0, 1, 1)), proste=lekka)
    elif rodzina == PAR:
        rosliny.kepa_parasoli(s, rnd, pos, k, ry, f)
    elif rodzina == PAP:
        rosliny.paproc_drzewiasta(s, rnd, pos, k, ry, f)
    elif rodzina == BAM:
        rosliny.bambus(s, rnd, pos, wys=6.5 * k, n=3, ry=ry, szer=2.8)
    elif rodzina == KAK:
        miejsca.kaktus(s, rnd, pos, k)
    else:
        raise ValueError(rodzina)


def drobne(s, rnd, rodzina, pos):
    """Rzecz skraju (podszyt, niska, bez kolizji)."""
    x, y, z = pos
    if rodzina == "krzew":
        rosliny.krzew_dzungli(s, rnd, pos, rnd.uniform(0.75, 1.1), kwiat=rnd.choice((None, None, "dz_kwiat_czerwony", "dz_kwiat_zolty", "owoc")))
    elif rodzina == "paproc":
        rosliny.paproc(s, rnd, pos, rnd.uniform(1.0, 1.4))
    elif rodzina == "kwiat":
        rosliny.kepa_kwiatow(s, rnd, pos, rnd.choice((("dz_kwiat_czerwony", "dz_kwiat_zolty"), ("dz_kwiat_zolty", "biel"))))
    elif rodzina == "kwiaty":
        rosliny.kepa_kwiatow(s, rnd, pos, ("dz_kwiat_czerwony", "dz_kwiat_czerwony"))
    elif rodzina == "swiecacy":
        rosliny.swiecacy_kwiat(s, rnd, pos, rnd.uniform(1.0, 1.3))
    elif rodzina == "kokosy":
        miejsca.stos_kokosow(s, rnd, pos)
    elif rodzina == "glaz":
        skaly.glaz(s, rnd, pos, rnd.uniform(0.7, 0.95), rnd.uniform(0, 360), "dz_kamien", "Slate", mech=True, kolizja=False)
    elif rodzina == "sucha":
        rosliny_lasu.krzak(s, rnd, pos, rnd.uniform(0.5, 0.75), kolory=("trawa_sucha", "dz_ochra", "dz_droga_pustyni"))
    else:
        raise ValueError(rodzina)


def _grupa(strona, u, rodzaj="Kulisy"):
    n = int((u - U_MIN) // ODCINEK_KULIS)
    return "%s/%s/O_%02d" % (rodzaj, "Prawa" if strona > 0 else "Lewa", n)


def kulisy(s, K, Z):
    rnd = K.rnd_kulisy
    stat = {"przod": 0, "przod_odrzucone": 0, "skraj": 0, "srodek": 0, "glab": 0, "liany": 0}
    for zn in (-1, 1):
        # --- przód: drzewa z kolizją pnia; co któreś sąsiednie drzewa łączy liana
        u = U_KULIS + rnd.uniform(0, 3)
        poprzednie = None
        while u < U_MAX - 6.0:
            o, z = zestaw(K, u)
            if K.w_wodzie(u, 2.0):
                u += 4.0
                continue
            rodzina, _, (k0, k1) = _losuj(rnd, z["przod"])
            k = rnd.uniform(k0, k1)
            ok = False
            for proba in range(5):
                v = zn * (rnd.uniform(40.8, 44.5) + 2.2 * proba)
                kk = k * (0.92 ** proba)
                if not K.wolne(u, v, 2.4):
                    continue

                def bud(u=u, v=v, kk=kk, rodzina=rodzina):
                    with s.grupa(_grupa(zn, u)):
                        drzewo(s, rnd, rodzina, (u, 0.0, v), kk)
                if postaw(s, Z, bud):
                    K.zajmij(u, v, 2.2)
                    ok = True
                    if poprzednie and rodzina in (DRZ, FIG) and poprzednie[3] in (DRZ, FIG) and u - poprzednie[0] < 16 \
                            and rnd.random() < 0.55:
                        h = rnd.uniform(9.0, 13.0)

                        def bud_l(p=poprzednie, u=u, v=v, h=h):
                            with s.grupa(_grupa(zn, u)):
                                rosliny.liana(s, rnd, (p[0] + 0.6, h, p[1]), (u - 0.6, h + rnd.uniform(-1, 1), v),
                                              zwis=rnd.uniform(2.0, 3.5), grub=0.4, liscie=2)
                        if postaw(s, Z, bud_l):
                            stat["liany"] += 1
                    poprzednie = (u, v, kk, rodzina)
                    break
            stat["przod" if ok else "przod_odrzucone"] += 1
            u += z["krok"] * rnd.uniform(0.85, 1.25)
        # --- skraj: podszyt, bez kolizji, przy granicy pola gry
        u = U_KULIS + 1.0 + rnd.uniform(0, 3)
        while u < U_MAX - 1.0:
            o, z = zestaw(K, u)
            if not z["skraj"]:
                u += 5.0
                continue
            rodzina = _losuj(rnd, z["skraj"])[0]
            for proba in range(3):
                v = zn * (rnd.uniform(36.9, 39.3) + 1.2 * proba)
                if not K.wolne(u, v, 1.6):
                    continue

                def bud(u=u, v=v, rodzina=rodzina):
                    with s.grupa(_grupa(zn, u)), s.cechy(kolizja=False):
                        drobne(s, rnd, rodzina, (u, 0.0, v))
                if postaw(s, Z, bud):
                    stat["skraj"] += 1
                    K.zajmij(u, v, 1.2)
                    break
            u += rnd.uniform(6.5, 9.0)
        # --- środek: drugi rząd (bez kolizji) — piętro średnie i olbrzymy
        u = U_KULIS + 4.0 + rnd.uniform(0, 4)
        while u < U_MAX - 8.0:
            o, z = zestaw(K, u)
            rodzina, _, (k0, k1) = _losuj(rnd, z["przod"])
            for proba in range(3):
                v = zn * (rnd.uniform(45.5, 48.5) + 1.5 * proba)
                if not K.wolne(u, v, 2.0):
                    continue

                def bud(u=u, v=v, rodzina=rodzina, k=rnd.uniform(k0, k1) * rnd.uniform(1.0, 1.15)):
                    n0 = len(s.czesci)
                    with s.grupa(_grupa(zn, u)):
                        drzewo(s, rnd, rodzina, (u, 0.0, v), k, lekka=True)
                    bez_kolizji(s, n0)
                if postaw(s, Z, bud):
                    K.zajmij(u, v, 1.8)
                    stat["srodek"] += 1
                    break
            u += rnd.uniform(13.0, 16.0)
        # --- głąb: wysokie, bez kolizji
        u = U_KULIS + 6.0 + rnd.uniform(0, 3)
        while u < U_MAX - 8.0:
            o, z = zestaw(K, u)
            rodzaj, kolor = z["glab"]
            v = zn * rnd.uniform(49.0, 57.0)
            if not K.wolne(u, v, 3.0):                         # kaskady, Kaskada Gaju, wiszące mosty, ruiny
                u += rnd.uniform(3.0, 5.0)
                continue

            def bud(u=u, v=v, rodzaj=rodzaj, kolor=kolor, z=z):
                n0 = len(s.czesci)
                with s.grupa(_grupa(zn, u)), s.cechy(kolizja=False):
                    los = rnd.random()
                    if rodzaj != "kulisa" and los < 0.22:
                        drzewo(s, rnd, rodzaj, (u, 0.0, v), rnd.uniform(1.2, 1.5), lekka=True)
                    elif los < 0.32:
                        rodzina, _, (k0, k1) = _losuj(rnd, z["przod"])
                        drzewo(s, rnd, rodzina, (u, 0.0, v), rnd.uniform(k0, k1) * rnd.uniform(1.15, 1.35), lekka=True)
                    else:
                        kol = kolor if rnd.random() < 0.55 else cien(s, kolor, 0.85)
                        rosliny_lasu.kulisa(s, rnd, (u, 0.0, v), rnd.uniform(1.1, 1.35), rnd.uniform(0, 90), kol, "dz_pien",
                                            wys=rnd.uniform(26, 34))
                bez_kolizji(s, n0)
            if postaw(s, Z, bud):
                stat["glab"] += 1
            u += rnd.uniform(7.0, 9.5)
    return stat


def tlo(s, K, Z):
    """Sylwetki za kulisami (bez kolizji i cienia), jaśniejące w mgłę: bliższy rząd |v| 63–74, dalszy 76–80; dżungla
    jest wyższa niż Bagno (26–48)."""
    rnd = K.rnd_tlo
    n = 0
    for zn in (-1, 1):
        for v0, v1, k0, k1, krok, h0, h1, kolory in ((63.0, 74.0, 1.3, 1.6, (12.0, 16.0), 30, 42, ("dz_sylweta_2", "dz_sylweta_1")),
                                                    (76.0, 80.0, 1.1, 1.3, (14.0, 19.0), 36, 48, ("dz_sylweta_3", "dz_sylweta_2"))):
            u = U_KULIS + 4.0 + rnd.uniform(0, 4)
            while u < U_MAX - 8.0:
                v = zn * rnd.uniform(v0, v1)
                kol = kolory[0] if rnd.random() < 0.6 else kolory[-1]
                if u > 1876.0 + D:
                    kol = "dz_ochra" if rnd.random() < 0.5 else "dz_piasek"
                if v0 < 70 and not K.wolne(u, v, 4.0):            # szczyt kaskad przy Mostku
                    u += rnd.uniform(3.0, 5.0)
                    continue

                def bud(u=u, v=v, kol=kol, k=rnd.uniform(k0, k1), h=rnd.uniform(h0, h1)):
                    with s.grupa(_grupa(zn, u, "Tlo")), s.cechy(kolizja=False, cien=False):
                        rosliny_lasu.kulisa(s, rnd, (u, 0.0, v), k, rnd.uniform(0, 90), kol, "dz_sylweta_1", wys=h)
                if postaw(s, Z, bud):
                    n += 1
                u += rnd.uniform(*krok)
    return n


def mosty_z_lian(s, K, Z):
    """Wiszące mosty z lian w kulisach (|v| ok. 48–50): dwa drzewa dżungli i między nimi pomost z trzech odcinków desek
    zwisający łukiem na wys. ok. 12, poręcze z lian, liny od pni do pomostu, zwisające liany. Bez kolizji (za
    niewidzialną ścianą). Zwraca liczbę mostów."""
    rnd = K.rnd_mosty
    n = 0
    miejsca_ = [(1050.0, -1), (1150.0, 1), (1265.0, -1), (1470.0, -1), (1590.0, -1), (1800.0, -1)]
    for u, zn in miejsca_:
        u += D
        v1, v2 = zn * rnd.uniform(47.0, 49.0), zn * rnd.uniform(48.5, 51.0)
        if not (K.wolne(u - 9.0, v1, 3.0) and K.wolne(u + 9.0, v2, 3.0)):
            continue
        h = rnd.uniform(11.5, 13.0)

        def bud(u=u, v1=v1, v2=v2, h=h):
            n0 = len(s.czesci)
            with s.grupa(_grupa(zn, u) + "/Most"):
                for uu, vv in ((u - 9.0, v1), (u + 9.0, v2)):
                    rosliny.drzewo_dzungli(s, rnd, (uu, 0.0, vv), rnd.uniform(1.1, 1.25), rnd.uniform(0, 360), rnd.choice(ODCIEN), liana_=False)
                a = (u - 7.4, h, v1)
                b = (u + 7.4, h + rnd.uniform(-0.6, 0.6), v2)
                pts = []
                for i in range(4):
                    t = i / 3.0
                    zw = 1.6 * math.sin(math.pi * t)
                    pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - zw, a[2] + (b[2] - a[2]) * t))
                for p, q in zip(pts, pts[1:]):
                    s.belka("Wiszący most deska", p, q, 0.3, "drewno", "Wood", szer=2.4)
                for dz in (-1.2, 1.2):
                    for p, q in zip(pts, pts[1:]):
                        s.belka("Liana", (p[0], p[1] + 1.3, p[2] + dz), (q[0], q[1] + 1.3, q[2] + dz), 0.22, "dz_liana", "SmoothPlastic")
                for p in pts[1:-1]:
                    rosliny.liana_zwis(s, rnd, (p[0], p[1] - 0.1, p[2] + rnd.uniform(-1, 1)), rnd.uniform(3.0, 5.5), 0.28)
            bez_kolizji(s, n0)
        if postaw(s, Z, bud):
            K.zajmij(u - 9.0, v1, 3.5)
            K.zajmij(u + 9.0, v2, 3.5)
            K.zajmij(u, (v1 + v2) / 2.0, 4.0)
            n += 1
    return n


def ruiny_w_kulisach(s, K, Z):
    """Fragmenty muru ruin z omszałymi schodami w kulisach Ruin Pancernika i Kręgu (|v| 44–54), front ku polu gry.
    Zwraca liczbę."""
    rnd = K.rnd_mosty
    n = 0
    for u, zn in ((1652.0, 1), (1672.0, -1), (1700.0, 1), (1736.0, -1), (1770.0, 1), (1796.0, -1)):
        u += D
        v = zn * rnd.uniform(46.0, 52.0)
        if not K.wolne(u, v, 5.0):
            continue

        def bud(u=u, v=v):
            with s.grupa(_grupa(zn, u) + "/Ruiny"):
                miejsca.mur_ruin(s, rnd, (u, 0.0, v), rnd.uniform(0.9, 1.15), 0.0 if zn < 0 else 180.0)
        if postaw(s, Z, bud):
            K.zajmij(u, v, 6.0)
            n += 1
    return n


def niewidzialne_sciany(s, K):
    """Niewidzialne ściany (przezroczystość 1, z kolizją, bez cienia) wzdłuż pasa na |v| = 38 od u 1904 (tam kończą się
    ściany Bagna-pasa) do u 2844. Koniec zamyka ściana zapowiedzi Pustyni (u 2845)."""
    w = WIDOCZNA_SCIANA
    u0, u1 = 964.0 + D, U_SCIANY - 1.0
    with s.grupa("Kulisy/Niewidzialne"), s.cechy(cien=False):
        for zn in (-1, 1):
            s.blok("Niewidzialna ściana", ((u0 + u1) / 2.0, 40.0, zn * w), (u1 - u0, 80.0, 2.0), "biel", alfa=1.0)


def detale_drozki(s, K, Z):
    """Drobiazgi przy Dróżce (|dv| 4,8–7): kępki, paprotki, grzybki, świecące kwiatki, kamyki; im dalej od wejścia,
    tym gęściej. Zwraca liczbę."""
    rnd = K.rnd_detale
    n = 0
    for a, b in ODCINKI_SCIEZKI:
        u = a + 2.0
        while u < b - 2.0:
            zn = rnd.choice((-1, 1))
            v = v_sciezki(u) + zn * (SZER_SCIEZKI / 2.0 + rnd.uniform(0.9, 3.0))
            rodz = _losuj(rnd, [("kepka", 4), ("paproc", 2), ("grzybki", 1), ("swiecacy", 1), ("kamyki", 1)])[0]

            def bud(u=u, v=v, rodz=rodz):
                with s.grupa("Detale/Drozka"), s.cechy(kolizja=False):
                    if rodz == "kepka":
                        detale.kepka(s, rnd, (u, 0.0, v), ("dz_trawa", "dz_trawa_jasna", "dz_lisc_ciemny"), k=rnd.uniform(0.8, 1.2))
                    elif rodz == "paproc":
                        rosliny.paproc(s, rnd, (u, 0.0, v), rnd.uniform(0.45, 0.6))
                    elif rodz == "grzybki":
                        detale.grzybki(s, rnd, (u, 0.0, v), rnd.choice((("dz_owoc", "biel"), ("dz_kwiat_rozowy", "biel"))))
                    elif rodz == "swiecacy":
                        rosliny.swiecacy_kwiat(s, rnd, (u, 0.0, v), rnd.uniform(0.55, 0.7))
                    else:
                        skaly.kamyki(s, rnd, (u, 0.0, v), "dz_kamien", "Slate", n=3, k=0.6)
            if K.miejsce_ok(u, v, 0.8, 0.6, sciezka_zapas=0.3) and postaw(s, Z, bud):
                K.zajmij(u, v, 0.8)
                n += 1
            u += rnd.uniform(4.4, 7.4) if u < 1400 + D else rnd.uniform(3.8, 6.2)
    return n


def runo(s, K, Z, ile=120):
    """Kępki trawy, liści i paprotek w polu gry (poza Dróżką i pętlami; niskie, więc mogą stać przy placach walki)."""
    rnd = K.rnd_detale
    n = 0
    for _ in range(ile * 4):
        if n >= ile:
            break
        u = rnd.uniform(944.0 + D, 1876.0 + D)
        v = rnd.uniform(-35.0, 35.0)
        if not K.miejsce_ok(u, v, 0.9, 1.2, sciezka_zapas=0.8):
            continue
        o = K.odcinek(u)
        kol = {"gebokwiaty": ("dz_lisc_ciemny", "dz_kwiat_czerwony", "dz_korona"),
               "kokosy": ("trawa_sucha", "dz_trawa", "dz_lisc_jasny"),
               "ruiny": ("dz_mech", "dz_trawa", "dz_lisc_ciemny")}.get(o, ("dz_trawa", "dz_trawa_jasna", "dz_lisc_ciemny"))

        def bud(u=u, v=v, kol=kol):
            with s.grupa("Detale/Runo"), s.cechy(kolizja=False):
                detale.kepka(s, rnd, (u, 0.0, v), kol, k=rnd.uniform(0.8, 1.3))
        if postaw(s, Z, bud):
            K.zajmij(u, v, 0.9)
            n += 1
    return n
