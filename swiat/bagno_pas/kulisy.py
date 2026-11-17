# -*- coding: utf-8 -*-
"""Kulisy Bagna: ściana mokradła po obu stronach pola gry (|v| 36–58), tło za nią (|v| 63–80), niewidzialne ściany i
drobiazgi przy Krzywej Kładce. Rzędy jak w lesie-pasie (swiat/las_pas/kulisy.py): skraj (bez kolizji), przód (kolizja
pnia), drugi rząd i głąb (bez kolizji), tło (bez kolizji i cienia). Rodziny: cypryśnik, wierzba płacząca, korzeniak,
suche drzewo z mchem (swiat/bagno_pas/rosliny.py) i rodziny lasu przez `las_pas.kulisy.drzewo` / `drobne`.

Kulisy Bagna zaczynają się na u 970: do u 966 stoją kulisy lasu-pasa (za bramą zostają jako skraj lasu).
Grupy: Kulisy/<Lewa|Prawa>/O_<nn> i Tlo/<Lewa|Prawa>/O_<nn> co 64 st (w Studio LevelOfDetail = StreamingMesh).
"""
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale, rosliny as rosliny_lasu  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.bagno_pas import miejsca, rosliny  # noqa: E402
from swiat.bagno_pas.kontekst import ODCINKI_SCIEZKI, U_MAX, U_MIN, U_SCIANY, v_sciezki  # noqa: E402
from swiat.las_pas.kontekst import SZER_SCIEZKI, WIDOCZNA_SCIANA  # noqa: E402
from swiat.las_pas.kulisy import ODCIEN, _losuj, bez_kolizji, drobne as drobne_lasu, drzewo as drzewo_lasu  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

U_KULIS = 970.0
ODCINEK_KULIS = 64.0
CYP, WIE, KOR, SUC = "cyprys", "wierzba", "korzeniak", "suchy"
ZESTAW = {
    "wejscie":  {"przod": [(WIE, 3, (0.95, 1.15)), (CYP, 2, (0.85, 1.0)), (SUC, 1, (0.9, 1.05))], "krok": 8.5,
                 "skraj": [("kepa", 3), ("palki", 2)], "glab": ("kulisa", "bagno_sylweta_1")},
    "row_z_kladka": "wejscie",
    "oczka":    {"przod": [(CYP, 3, (0.9, 1.15)), (WIE, 2, (0.9, 1.1)), (KOR, 1, (0.9, 1.1))], "krok": 8.0,
                 "skraj": [("kepa", 3), ("palki", 3)], "glab": (CYP, "bagno_sylweta_1")},
    "kladka_nad_topiela": {"przod": [(KOR, 1, (0.9, 1.1)), (CYP, 1, (0.9, 1.05))], "krok": 8.0, "skraj": [("kepa", 1)],
                           "glab": (CYP, "bagno_sylweta_1")},
    "trzesawisko": {"przod": [(SUC, 3, (0.95, 1.25)), (KOR, 1, (0.9, 1.1)), (CYP, 1, (0.85, 1.0)), (WIE, 1, (0.85, 1.0))],
                    "krok": 8.0, "skraj": [("kepa", 3), ("palki", 1), ("kanciak", 1)], "glab": ("kulisa", "bagno_sylweta_1")},
    "trzcinowa_przesieka": {"przod": [(CYP, 1, (0.9, 1.1))], "krok": 9.0, "skraj": [], "glab": (CYP, "bagno_sylweta_1")},
    "kepy":     {"przod": [(KOR, 3, (0.95, 1.2)), (CYP, 3, (0.95, 1.2)), (SUC, 1, (0.9, 1.1))], "krok": 7.5,
                 "skraj": [("kepa", 2), ("palki", 2)], "glab": (CYP, "bagno_sylweta_1")},
    "zatopione_pnie": {"przod": [(SUC, 1, (1.0, 1.2))], "krok": 9.0, "skraj": [], "glab": ("kulisa", "bagno_sylweta_1")},
    "chatka":   {"przod": [(SUC, 2, (0.95, 1.2)), (WIE, 2, (0.9, 1.1)), (CYP, 1, (0.85, 1.0))], "krok": 8.0,
                 "skraj": [("kepa", 2), ("glaz_maly", 1), ("palki", 1)], "glab": ("kulisa", "bagno_sylweta_1")},
    "latarnie_topieli": {"przod": [(CYP, 1, (0.9, 1.1))], "krok": 8.0, "skraj": [("kepa", 1)], "glab": (CYP, "bagno_sylweta_1")},
    "topiel":   {"przod": [(CYP, 3, (1.0, 1.25)), (SUC, 2, (1.0, 1.2)), (KOR, 1, (0.9, 1.1))], "krok": 8.0,
                 "skraj": [("kepa", 2), ("palki", 2)], "glab": (CYP, "bagno_sylweta_1")},
    "przedbramie": {"przod": [(CYP, 2, (0.9, 1.1)), (WIE, 1, (0.9, 1.05)), ("palma", 1, (1.0, 1.15))], "krok": 8.0,
                    "skraj": [("kepa", 2), ("dzungla", 1)], "glab": (CYP, "bagno_sylweta_1")},
    "dzungla":  {"przod": [("palma", 2, (1.05, 1.25)), ("dzungla", 2, (1.1, 1.4))], "krok": 7.0, "skraj": [("dzungla", 2)],
                 "glab": ("palma", "dzungla_lisc")},
}


def zestaw(K, u):
    o = K.odcinek(u)
    if o == "topiel" and u >= 1848.0:
        o = "przedbramie"
    if o not in ZESTAW:
        o = "wejscie"
    z = ZESTAW[o]
    if isinstance(z, str):
        z = ZESTAW[z]
    return o, z


def drzewo(s, rnd, rodzina, pos, k):
    """Jedna roślina kulis: rodziny Bagna albo (inne nazwy) rodziny lasu przez las_pas.kulisy.drzewo."""
    ry = 15.0 * rnd.randint(0, 23)
    f = rnd.choice(ODCIEN)
    if rodzina == CYP:
        rosliny.cyprys(s, rnd, pos, k, ry, f)
    elif rodzina == WIE:
        rosliny.wierzba(s, rnd, pos, k, ry, f)
    elif rodzina == KOR:
        rosliny.korzeniak(s, rnd, pos, k, ry, f)
    elif rodzina == SUC:
        rosliny.suchy_omszaly(s, rnd, pos, k, ry)
    elif rodzina == "palma":
        miejsca.palma(s, rnd, pos, k)
    elif rodzina == "dzungla":
        miejsca.roslina_dzungli(s, rnd, pos, k)
    else:
        drzewo_lasu(s, rnd, rodzina, pos, k, "ostepy")


def drobne(s, rnd, rodzina, pos):
    x, y, z = pos
    if rodzina == "kepa":
        rosliny.kepa_trzciny(s, rnd, pos, rnd.uniform(1.4, 2.6), 2.6, pelna=False)
    elif rodzina == "palki":
        for q in range(2):
            rosliny_lasu.trzcina(s, rnd, (x + rnd.uniform(-1.2, 1.2), y, z + rnd.uniform(-0.8, 0.8)))
    elif rodzina == "dzungla":
        miejsca.roslina_dzungli(s, rnd, pos, rnd.uniform(0.6, 0.8))
    else:
        drobne_lasu(s, rnd, rodzina, pos, "wawoz")


def _grupa(strona, u, rodzaj="Kulisy"):
    n = int((u - U_MIN) // ODCINEK_KULIS)
    return "%s/%s/O_%02d" % (rodzaj, "Prawa" if strona > 0 else "Lewa", n)


def kulisy(s, K, Z):
    rnd = K.rnd_kulisy
    stat = {"przod": 0, "przod_odrzucone": 0, "skraj": 0, "srodek": 0, "glab": 0}
    for zn in (-1, 1):
        # --- przód: drzewa z kolizją pnia
        u = U_KULIS + rnd.uniform(0, 3)
        while u < U_MAX - 6.0:
            o, z = zestaw(K, u)
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
                    break
            stat["przod" if ok else "przod_odrzucone"] += 1
            u += z["krok"] * rnd.uniform(0.8, 1.2)
        # --- skraj: niskie, bez kolizji, przy granicy pola gry
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
        # --- środek: drugi rząd (bez kolizji)
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
                        drzewo(s, rnd, rodzina, (u, 0.0, v), k)
                    bez_kolizji(s, n0)
                if postaw(s, Z, bud):
                    K.zajmij(u, v, 1.8)
                    stat["srodek"] += 1
                    break
            u += rnd.uniform(11.0, 14.0)
        # --- głąb: wysokie, bez kolizji
        u = U_KULIS + 6.0 + rnd.uniform(0, 3)
        while u < U_MAX - 8.0:
            o, z = zestaw(K, u)
            rodzaj, kolor = z["glab"]
            v = zn * rnd.uniform(48.5, 56.5)

            def bud(u=u, v=v, rodzaj=rodzaj, kolor=kolor, z=z):
                n0 = len(s.czesci)
                with s.grupa(_grupa(zn, u)), s.cechy(kolizja=False):
                    los = rnd.random()
                    if rodzaj != "kulisa" and los < 0.35:
                        drzewo(s, rnd, rodzaj, (u, 0.0, v), rnd.uniform(1.15, 1.45))
                    elif los < 0.5:
                        rodzina, _, (k0, k1) = _losuj(rnd, z["przod"])
                        drzewo(s, rnd, rodzina, (u, 0.0, v), rnd.uniform(k0, k1) * rnd.uniform(1.15, 1.35))
                    else:
                        kol = kolor if rnd.random() < 0.55 else cien(s, kolor, 0.85)
                        rosliny_lasu.kulisa(s, rnd, (u, 0.0, v), rnd.uniform(1.05, 1.3), rnd.uniform(0, 90), kol, "bagno_kora",
                                            wys=rnd.uniform(22, 30))
                bez_kolizji(s, n0)
            if postaw(s, Z, bud):
                stat["glab"] += 1
            u += rnd.uniform(6.5, 9.0)
    return stat


def tlo(s, K, Z):
    """Sylwetki za kulisami (bez kolizji i cienia), jaśniejące w mgłę: bliższy rząd |v| 63–74, dalszy 76–80."""
    rnd = K.rnd_tlo
    n = 0
    for zn in (-1, 1):
        for v0, v1, k0, k1, krok, h0, h1, kolory in ((63.0, 74.0, 1.25, 1.5, (13.0, 17.0), 26, 38, ("bagno_sylweta_2", "bagno_sylweta_3")),
                                                    (76.0, 80.0, 1.05, 1.25, (14.0, 19.0), 32, 44, ("bagno_sylweta_3",))):
            u = U_KULIS + 4.0 + rnd.uniform(0, 4)
            while u < U_MAX - 8.0:
                v = zn * rnd.uniform(v0, v1)
                kol = kolory[0] if rnd.random() < 0.6 else kolory[-1]

                def bud(u=u, v=v, kol=kol, k=rnd.uniform(k0, k1), h=rnd.uniform(h0, h1)):
                    with s.grupa(_grupa(zn, u, "Tlo")), s.cechy(kolizja=False, cien=False):
                        rosliny_lasu.kulisa(s, rnd, (u, 0.0, v), k, rnd.uniform(0, 90), kol, "bagno_sylweta_1", wys=h)
                if postaw(s, Z, bud):
                    n += 1
                u += rnd.uniform(*krok)
    return n


def niewidzialne_sciany(s, K):
    """Niewidzialne ściany (przezroczystość 1, z kolizją, bez cienia) wzdłuż pasa na |v| = 38 od u 964 (tam kończą się
    ściany lasu-pasa) do u 1904. Koniec zamyka ściana zapowiedzi Dżungli (u 1905)."""
    w = WIDOCZNA_SCIANA
    u0, u1 = 964.0, U_SCIANY - 1.0
    with s.grupa("Kulisy/Niewidzialne"), s.cechy(cien=False):
        for zn in (-1, 1):
            s.blok("Niewidzialna ściana", ((u0 + u1) / 2.0, 40.0, zn * w), (u1 - u0, 80.0, 2.0), "biel", alfa=1.0)


def detale_kladki(s, K, Z):
    """Drobiazgi przy Krzywej Kładce (|dv| 4,8–7): kępki turzycy, grzybki, ogniki nisko, pałki; im dalej od wejścia,
    tym gęściej. Zwraca liczbę."""
    rnd = K.rnd_detale
    n = 0
    for a, b in ODCINKI_SCIEZKI:
        u = a + 2.0
        while u < b - 2.0:
            zn = rnd.choice((-1, 1))
            v = v_sciezki(u) + zn * (SZER_SCIEZKI / 2.0 + rnd.uniform(0.9, 3.0))
            rodz = _losuj(rnd, [("kepka", 4), ("grzybki", 2), ("palki", 2), ("ognik", 1)])[0]

            def bud(u=u, v=v, rodz=rodz):
                with s.grupa("Detale/Kladka"), s.cechy(kolizja=False):
                    if rodz == "kepka":
                        detale.kepka(s, rnd, (u, 0.0, v), ("bagno_trawa", "bagno_trawa_jasna", "trawa_sucha"), k=rnd.uniform(0.8, 1.2))
                    elif rodz == "grzybki":
                        detale.grzybki(s, rnd, (u, 0.0, v), rnd.choice((("drewno", "tynk_krem"), ("bagno_kwiat", "biel"),
                                                                       ("drewno_jasne", "biel"))))
                    elif rodz == "palki":
                        rosliny_lasu.trzcina(s, rnd, (u, 0.0, v))
                    else:
                        rosliny.ognik(s, (u, rnd.uniform(0.9, 1.4), v), 0.5)
            if K.miejsce_ok(u, v, 0.8, 0.6, sciezka_zapas=0.3) and postaw(s, Z, bud):
                K.zajmij(u, v, 0.8)
                n += 1
            u += rnd.uniform(3.4, 6.0) if u < 1400 else rnd.uniform(2.9, 5.0)
    return n


def runo(s, K, Z, ile=150):
    """Kępki turzycy i trawy w polu gry (poza ścieżką i pętlami; niskie, więc mogą stać przy placach walki)."""
    rnd = K.rnd_detale
    n = 0
    for _ in range(ile * 4):
        if n >= ile:
            break
        u = rnd.uniform(944.0, 1876.0)
        v = rnd.uniform(-35.0, 35.0)
        if not K.miejsce_ok(u, v, 0.9, 1.2, sciezka_zapas=0.8):
            continue
        o = K.odcinek(u)
        kol = ("bagno_trawa", "bagno_trawa_jasna", "trawa_sucha") if o in ("wejscie", "oczka", "kepy", "topiel") else \
              ("bagno_trzcina", "trawa_sucha", "bagno_mech")

        def bud(u=u, v=v, kol=kol):
            with s.grupa("Detale/Runo"), s.cechy(kolizja=False):
                detale.kepka(s, rnd, (u, 0.0, v), kol, k=rnd.uniform(0.8, 1.3))
        if postaw(s, Z, bud):
            K.zajmij(u, v, 0.9)
            n += 1
    return n
