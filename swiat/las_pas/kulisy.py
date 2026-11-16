# -*- coding: utf-8 -*-
"""Kulisy pasa: gęsta ściana lasu po obu stronach pola gry (|v| 36–60), tło za nią (|v| 62–80), ściana zamykająca za
plecami przybywającego (u −34…0) i niewidzialne ściany. Każda przegroda ma własne rodziny roślin i skał (rozpoznawalna
z daleka), rodziny z swiat/biom_las/rosliny.py i skaly.py.

Rzędy (od pola gry na zewnątrz):
- skraj   |v| 36,6–39,5  niskie krzaki, jeżyny, paprocie, kwiaty, kamienie (bez kolizji) — zakrywają styk pola i kulis;
- przód   |v| 40,5–47    drzewa przegrody z kolizją pnia (plan: kolizja tylko na pierwszym rzędzie);
- głąb    |v| 48–58      wysokie kulisy (pień + czapa, bez kolizji), w Lasku grzyby-olbrzymy;
- tło     |v| 63–78      sylwetki jaśniejące ku horyzontowi (perspektywa powietrzna), bez kolizji i cienia.
Kolizję zamyka niewidzialna ściana na |v| = 38 (od u −4 do 964) i ściana za bramą Pniaków (u −4).
Drzewo, które łamie zasady (korona nad placem walki albo w otwarciu przejścia, nad ścieżką, w przelocie kamery), jest
wycofywane i próbowane dalej od pola gry albo mniejsze (zasady.postaw).

Grupy: Kulisy/<Lewa|Prawa>/O_<nn> i Tlo/<Lewa|Prawa>/O_<nn> co 64 st wzdłuż pasa — w Studio LevelOfDetail =
StreamingMesh (lista w znaczniki.json).
"""
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import rosliny, skaly  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.las_pas.kontekst import U_MAX, U_MIN, WIDOCZNA_SCIANA  # noqa: E402
from swiat.las_pas.zasady import postaw  # noqa: E402

ODCINEK_KULIS = 64.0
# zasięg korony ku polu gry (≈ pół przekątnej korony · k) — pierwsze przybliżenie; ostatnie słowo mają zasady na częściach
R_KOR = {"okraglak": 7.2, "dab": 10.0, "sosna": 7.1, "smukly": 4.4, "sosna_smukla": 5.2, "swierk": 6.4, "suchy": 5.2,
         "brzozka": 5.4, "brzozka_podwojna": 6.2, "jarzebina": 5.0, "grzyb": 6.4, "glaz": 3.6, "kulisa": 6.4}
# odcinek (id przegrody/przejścia) → zestaw kulis
ZESTAW = {
    "sciana":   {"pb": "laka", "przod": [("okraglak", 2, (0.9, 1.15)), ("dab", 1, (0.8, 1.0))], "krok": 9.0,
                 "skraj": [("krzak", 1)], "glab": ("kulisa", "sylweta_1")},
    "wejscie":  {"pb": "laka", "przod": [("okraglak", 3, (0.9, 1.2)), ("smukly", 2, (0.9, 1.15)), ("dab", 1, (0.75, 0.95))],
                 "krok": 8.5, "skraj": [("krzak", 3), ("kwiaty", 2)], "glab": ("kulisa", "sylweta_1")},
    "plot_z_furtka": "wejscie",
    "zagroda":  {"pb": "laka", "przod": [("okraglak", 3, (0.85, 1.15)), ("smukly", 2, (0.9, 1.15)), ("jarzebina", 1, (0.9, 1.1))],
                 "krok": 8.5, "skraj": [("krzak", 2)], "skraj_v": (39.2, 40.2), "glab": ("kulisa", "sylweta_1")},
    "strumyk_z_mostkiem": {"pb": "laka", "przod": [("okraglak", 1, (0.85, 1.05)), ("smukly", 1, (0.9, 1.1))], "krok": 8.0,
                           "skraj": [("krzak", 1)], "skraj_v": (38.8, 40.0), "glab": ("kulisa", "sylweta_1")},
    "lasek":    {"pb": "kapeluszowo", "przod": [("grzyb", 3, (1.2, 1.65)), ("dab", 2, (0.8, 1.0)), ("jarzebina", 1, (0.9, 1.1))],
                 "krok": 8.0, "skraj": [("paproc", 2), ("krzak", 1), ("grzybki", 2)], "glab": ("grzyb", "sylweta_1")},
    "jezynowe_zwezenie": {"pb": "ostepy", "przod": [("sosna", 1, (1.0, 1.3))], "krok": 8.0, "skraj": [],
                          "glab": ("kulisa", "igla")},
    "zarosla":  {"pb": "ostepy", "przod": [("sosna", 4, (1.0, 1.5)), ("swierk", 2, (0.9, 1.3)), ("sosna_smukla", 1, (0.95, 1.2)),
                                           ("suchy", 1, (0.9, 1.1))],
                 "krok": 7.5, "skraj": [("jezyna", 4), ("paproc", 2)], "glab": ("kulisa", "igla")},
    "kamienny_prog": {"pb": "wawoz", "przod": [("sosna", 1, (1.0, 1.3)), ("glaz", 1, (1.6, 2.2))], "krok": 8.0,
                      "skraj": [("kanciak", 1)], "glab": ("kulisa", "igla")},
    "leze":     {"pb": "wawoz", "przod": [("sosna_smukla", 3, (0.9, 1.15)), ("suchy", 2, (0.9, 1.1)), ("glaz", 2, (1.5, 2.3)),
                                          ("sosna", 1, (1.0, 1.3))],
                 "krok": 8.0, "skraj": [("kanciak", 2), ("krzaczek", 1), ("glaz_maly", 1)], "glab": ("kulisa", "sylweta_1")},
    "brama_menhirow": {"pb": "korona", "przod": [("brzozka", 1, (0.9, 1.2))], "krok": 8.0, "skraj": [("kanciak", 1)],
                       "glab": ("kulisa", "lisc")},
    "arena":    {"pb": "korona", "przod": [("brzozka", 3, (0.95, 1.3)), ("brzozka_podwojna", 2, (0.9, 1.15)),
                                           ("jarzebina", 1, (0.9, 1.1)), ("glaz", 1, (1.0, 1.5))],
                 "krok": 8.0, "skraj": [("kwiaty_biale", 2), ("krzak", 2)], "glab": ("kulisa", "lisc")},
    "przedbramie": {"pb": "ostepy", "przod": [("suchy", 2, (0.9, 1.1)), ("sosna_smukla", 2, (0.9, 1.1)), ("brzozka", 1, (0.9, 1.1))],
                    "krok": 8.0, "skraj": [("trzcina", 2), ("paproc", 1)], "glab": ("kulisa", "igla")},
    "bagno":    {"pb": "ostepy", "przod": [("suchy", 2, (0.9, 1.15)), ("sosna_smukla", 1, (0.9, 1.1))], "krok": 8.0,
                 "skraj": [("trzcina", 2)], "glab": ("kulisa", "runo_ciemne")},
}
ODCIEN = (0.9, 0.96, 1.0, 1.0, 1.05)


def zestaw(K, u):
    o = K.odcinek(u)
    if o == "arena" and u >= 908.0:
        o = "przedbramie"
    z = ZESTAW[o]
    if isinstance(z, str):
        z = ZESTAW[z]
    return o, z


def _losuj(rnd, lista):
    suma = sum(x[1] for x in lista)
    t = rnd.uniform(0, suma)
    for x in lista:
        t -= x[1]
        if t <= 0:
            return x
    return lista[-1]


def drzewo(s, rnd, rodzina, pos, k, pb):
    """Jedna roślina albo skała z rodzin starego lasu (pos = podstawa na ziemi)."""
    ry = 15.0 * rnd.randint(0, 23)
    f = rnd.choice(ODCIEN)
    kor = tuple(rosliny.odcien(s, c, f) for c in rosliny.KORONY[pb])
    if rodzina == "okraglak":
        rosliny.okraglak(s, rnd, pos, k, ry, kor)
    elif rodzina == "dab":
        rosliny.dab(s, rnd, pos, k, ry, kor)
    elif rodzina == "sosna":
        rosliny.sosna(s, rnd, pos, k, ry, ciemna=pb == "ostepy", f=f)
    elif rodzina == "smukly":
        rosliny.smukly(s, rnd, pos, k, ry, kor)
    elif rodzina == "sosna_smukla":
        rosliny.sosna_smukla(s, rnd, pos, k, ry, ciemna=pb in ("ostepy",), f=f, przechyl=rnd.uniform(3, 8) if pb == "wawoz" else rnd.uniform(0, 4))
    elif rodzina == "swierk":
        rosliny.swierk(s, rnd, pos, k, ry, f=f)
    elif rodzina == "suchy":
        rosliny.suchy(s, rnd, pos, k, ry)
    elif rodzina == "brzozka":
        rosliny.brzozka(s, rnd, pos, k, ry)
    elif rodzina == "brzozka_podwojna":
        rosliny.brzozka_podwojna(s, rnd, pos, k, ry)
    elif rodzina == "jarzebina":
        rosliny.jarzebina(s, rnd, pos, k, ry, kolory=tuple(rosliny.odcien(s, c, f) for c in ("lisc_ciemny", "lisc")))
    elif rodzina == "grzyb":
        kap = rnd.choice(("czerwien", "czerwien", "czerwien", "drewno", "tynk_krem"))
        rosliny.grzyb(s, rnd, pos, k, ry, kapelusz=kap, kropki=kap == "czerwien", trzon="biel" if kap != "tynk_krem" else "drewno_jasne")
    elif rodzina == "glaz":
        skaly.glaz(s, rnd, pos, k, ry, "kamien_cieply" if pb != "ostepy" else "kamien_lochu",
                   "SmoothPlastic" if pb != "ostepy" else "Slate", mech=rnd.random() < 0.6)
    else:
        raise ValueError(rodzina)


def drobne(s, rnd, rodzina, pos, pb):
    """Rzecz skraju (niska, bez kolizji)."""
    from swiat.biom_las import detale
    x, y, z = pos
    if rodzina == "krzak":
        rosliny.krzak(s, rnd, pos, rnd.uniform(0.8, 1.2), jagoda=rnd.choice((None, None, "czerwien", "zloto")))
    elif rodzina == "kwiaty":
        rosliny.kwiaty(s, rnd, pos, rnd.choice((("zloto", "biel"), ("czerwien", "zloto"), ("biel", "dach_sklep"))))
    elif rodzina == "kwiaty_biale":
        rosliny.kwiaty(s, rnd, pos, rnd.choice((("biel", "biel"), ("biel", "dach_sklep"), ("biel", "zloto"))))
    elif rodzina == "paproc":
        rosliny.paproc(s, rnd, pos, rnd.uniform(0.9, 1.25))
    elif rodzina == "jezyna":
        rosliny.jezyna(s, rnd, pos, rnd.uniform(0.85, 1.15))
    elif rodzina == "grzybki":
        detale.grzybki(s, rnd, pos, rnd.choice(detale.GRZYBY["kapeluszowo"]))
    elif rodzina == "kanciak":
        with s.cechy(kolizja=False):
            skaly.kanciak(s, rnd, pos, rnd.uniform(0.9, 1.4), rnd.uniform(0, 360), kolizja=False)
    elif rodzina == "glaz_maly":
        skaly.glaz(s, rnd, pos, rnd.uniform(0.7, 0.95), rnd.uniform(0, 360), "kamien_cieply", mech=True, kolizja=False)
    elif rodzina == "krzaczek":
        rosliny.krzak(s, rnd, pos, rnd.uniform(0.5, 0.7), kolory=("lisc_ciemny", "trawa", "trawa_sucha"))
    elif rodzina == "trzcina":
        for q in range(2):
            rosliny.trzcina(s, rnd, (x + rnd.uniform(-1.2, 1.2), y, z + rnd.uniform(-0.8, 0.8)))
    else:
        raise ValueError(rodzina)


def _grupa(strona, u, rodzaj="Kulisy"):
    n = int((u - U_MIN) // ODCINEK_KULIS)
    return "%s/%s/O_%02d" % (rodzaj, "Prawa" if strona > 0 else "Lewa", n)


def kulisy(s, K, Z):
    rnd = K.rnd_kulisy
    stat = {"przod": 0, "przod_odrzucone": 0, "skraj": 0, "glab": 0}
    for zn in (-1, 1):
        # --- przód: drzewa z kolizją pnia
        u = U_MIN + 2.0 + rnd.uniform(0, 4)
        while u < U_MAX - 8.0:
            o, z = zestaw(K, u)
            if o == "sciana":
                u += z["krok"]
                continue
            rodzina, _, (k0, k1) = _losuj(rnd, z["przod"])
            k = rnd.uniform(k0, k1)
            postawione = False
            for proba in range(5):
                v = zn * (rnd.uniform(40.8, 44.5) + 2.2 * proba)
                kk = k * (0.92 ** proba)
                if not K.wolne(u, v, 2.4):
                    continue

                def bud(u=u, v=v, kk=kk, rodzina=rodzina, pb=z["pb"]):
                    with s.grupa(_grupa(zn, u)):
                        drzewo(s, rnd, rodzina, (u, 0.0, v), kk, pb)
                if postaw(s, Z, bud):
                    K.zajmij(u, v, 2.2)
                    postawione = True
                    break
            stat["przod"] += 1 if postawione else 0
            stat["przod_odrzucone"] += 0 if postawione else 1
            u += z["krok"] * rnd.uniform(0.8, 1.2)
        # --- skraj: niskie, bez kolizji, przy granicy pola gry
        u = U_MIN + 4.0 + rnd.uniform(0, 3)
        while u < U_MAX - 1.0:
            o, z = zestaw(K, u)
            if not z["skraj"] or o == "sciana":
                u += 5.0
                continue
            rodzina = _losuj(rnd, z["skraj"])[0]
            v0, v1 = z.get("skraj_v", (36.9, 39.3))
            for proba in range(3):
                v = zn * (rnd.uniform(v0, v1) + 1.2 * proba)
                if not K.wolne(u, v, 1.6):
                    continue

                def bud(u=u, v=v, rodzina=rodzina, pb=z["pb"]):
                    with s.grupa(_grupa(zn, u)), s.cechy(kolizja=False):
                        drobne(s, rnd, rodzina, (u, 0.0, v), pb)
                if postaw(s, Z, bud):
                    stat["skraj"] += 1
                    K.zajmij(u, v, 1.2)
                    break
            u += rnd.uniform(4.5, 6.5)
        # --- środek: drugi rząd drzew przegrody (bez kolizji) — zasłania prześwity między przodem a głębią
        u = U_MIN + 6.0 + rnd.uniform(0, 4)
        while u < U_MAX - 8.0:
            o, z = zestaw(K, u)
            rodziny = [x for x in z["przod"] if x[0] != "glaz"]
            if o != "sciana" and rodziny:
                rodzina, _, (k0, k1) = _losuj(rnd, rodziny)
                for proba in range(3):
                    v = zn * (rnd.uniform(45.5, 48.5) + 1.5 * proba)
                    if not K.wolne(u, v, 2.0):
                        continue

                    def bud(u=u, v=v, rodzina=rodzina, k=rnd.uniform(k0, k1) * rnd.uniform(1.0, 1.15), pb=z["pb"]):
                        n0 = len(s.czesci)
                        with s.grupa(_grupa(zn, u)):
                            drzewo(s, rnd, rodzina, (u, 0.0, v), k, pb)
                        bez_kolizji(s, n0)
                    if postaw(s, Z, bud):
                        K.zajmij(u, v, 1.8)
                        stat["srodek"] = stat.get("srodek", 0) + 1
                        break
            u += rnd.uniform(9.0, 12.0)
        # --- głąb: wysokie kulisy bez kolizji
        u = U_MIN + 9.0 + rnd.uniform(0, 3)
        while u < U_MAX - 9.0:
            o, z = zestaw(K, u)
            rodzaj, kolor = z["glab"]
            v = zn * rnd.uniform(48.5, 56.5)

            def bud(u=u, v=v, rodzaj=rodzaj, kolor=kolor, z=z):
                n0 = len(s.czesci)
                with s.grupa(_grupa(zn, u)), s.cechy(kolizja=False):
                    los = rnd.random()
                    rodziny = [x for x in z["przod"] if x[0] != "glaz"]
                    if rodzaj == "grzyb" and los < 0.55:
                        drzewo(s, rnd, "grzyb", (u, 0.0, v), rnd.uniform(1.5, 1.9), z["pb"])
                    elif los < 0.6 and rodziny:
                        rodzina, _, (k0, k1) = _losuj(rnd, rodziny)
                        drzewo(s, rnd, rodzina, (u, 0.0, v), rnd.uniform(k0, k1) * rnd.uniform(1.15, 1.35), z["pb"])
                    else:
                        kol = kolor if rnd.random() < 0.55 else cien(s, kolor, 0.85)
                        rosliny.kulisa(s, rnd, (u, 0.0, v), rnd.uniform(1.05, 1.3), rnd.uniform(0, 90), kol, "drewno_ciemne",
                                       wys=rnd.uniform(24, 34))
                bez_kolizji(s, n0)
            if postaw(s, Z, bud):
                stat["glab"] += 1
            u += rnd.uniform(6.5, 9.0)
    return stat


def bez_kolizji(s, n0):
    """Części od n0 bez kolizji (rodziny roślin same włączają kolizję pnia — w głębi kulis jej nie chcemy)."""
    for c in s.czesci[n0:]:
        if len(c) > 15:
            c[15] |= 1
        else:
            c.append(1)


def tlo(s, K, Z):
    """Sylwetki za kulisami, bez kolizji i cienia: bliższy rząd `sylweta_2` / `sylweta_3` na |v| 63–74 (wys. 30–44)
    i dalszy, jaśniejszy `sylweta_3` na |v| 76–80 (wys. 36–48) — z przelotu kamery nie widać pustki za lasem."""
    rnd = K.rnd_tlo
    n = 0
    for zn in (-1, 1):
        for v0, v1, k0, k1, krok, h0, h1, kolory in ((63.0, 74.0, 1.25, 1.5, (11.0, 15.0), 30, 44, ("sylweta_2", "sylweta_3")),
                                                    (76.0, 80.0, 1.05, 1.25, (14.0, 19.0), 36, 48, ("sylweta_3",))):
            u = U_MIN + 10.0 + rnd.uniform(0, 4)
            while u < U_MAX - 10.0:
                v = zn * rnd.uniform(v0, v1)
                kol = kolory[0] if rnd.random() < 0.6 else kolory[-1]

                def bud(u=u, v=v, kol=kol, k=rnd.uniform(k0, k1), h=rnd.uniform(h0, h1)):
                    with s.grupa(_grupa(zn, u, "Tlo")), s.cechy(kolizja=False, cien=False):
                        rosliny.kulisa(s, rnd, (u, 0.0, v), k, rnd.uniform(0, 90), kol, "sylweta_1", wys=h)
                if postaw(s, Z, bud):
                    n += 1
                u += rnd.uniform(*krok)
    return n


def sciana_zamykajaca(s, K, Z):
    """Za plecami przybywającego (u −34…−3): skały „muru” (blok + jaśniejszy wierzch z klina narożnego) — niższe na osi,
    bo nad nimi startuje przelot kamery (28) — krzaki i kamienie u stopy, wysokie kulisy za skałami."""
    rnd = K.rnd_kulisy
    with s.grupa("Kulisy/ScianaZamykajaca"):
        v = -62.0
        while v < 62.0:
            szer = rnd.uniform(11.0, 15.0)
            vc = v + szer / 2.0
            h = rnd.uniform(9.0, 12.0) if abs(vc) < 20 else rnd.uniform(15.0, 24.0)
            u = rnd.uniform(-15.0, -11.0)
            kol = "kamien_cieply" if rnd.random() < 0.6 else cien(s, "kamien_cieply", 0.85)
            with s.uklad(pos=(u, 0, vc), obrot=(rnd.uniform(-6, 6), rnd.uniform(-15, 15) + 90, rnd.uniform(-8, 8))):
                s.blok("Skała muru", (0, h / 2.0 - 1.0, 0), (szer + 1.0, h + 2.0, rnd.uniform(9, 12)), kol)
                with s.cechy(kolizja=False):
                    s.naroznik("Skała muru wierzch", (0, h + 1.0, 0), (rnd.uniform(7, 10), 2.4, rnd.uniform(6, 8)), cien(s, kol, 1.05),
                               rot=(0, rnd.choice((0, 90, 180, 270)), 0))
                    if rnd.random() < 0.6:
                        with s.cechy(cien=False):
                            s.blok("Mech", (rnd.uniform(-2, 2), h + 0.2, rnd.uniform(-1, 1)), (szer * 0.5, 0.45, 3.5), "mech",
                                   rot=(0, rnd.uniform(-15, 15), 0))
            v += szer * rnd.uniform(0.82, 0.95)
        for k in range(13):
            vv = -38.0 + 6.2 * k + rnd.uniform(-1.5, 1.5)
            uu = rnd.uniform(-5.5, -3.8)
            with s.cechy(kolizja=False):
                if k % 2:
                    rosliny.krzak(s, rnd, (uu, 0.0, vv), rnd.uniform(0.9, 1.3), jagoda=rnd.choice((None, "czerwien")))
                else:
                    skaly.kanciak(s, rnd, (uu, 0.0, vv), rnd.uniform(1.0, 1.5), rnd.uniform(0, 360), kolizja=False)
        for k in range(12):
            vv = -60.0 + 10.5 * k + rnd.uniform(-2, 2)
            with s.cechy(kolizja=False):
                rosliny.kulisa(s, rnd, (rnd.uniform(-25.0, -22.0), 0.0, vv), rnd.uniform(1.0, 1.2), rnd.uniform(0, 90),
                               "sylweta_1" if k % 2 else cien(s, "sylweta_1", 0.85), "drewno_ciemne", wys=rnd.uniform(26, 34))


def niewidzialne_sciany(s, K):
    """Niewidzialne ściany (przezroczystość 1, z kolizją, bez cienia): wzdłuż pasa na |v| = 38 (od u −4 do 964) i w
    poprzek za bramą Pniaków (u −4). Za bramą Bagna zamyka ZapowiedzBagna (u 965)."""
    w = WIDOCZNA_SCIANA
    u0, u1 = -4.0, 964.0
    with s.grupa("Kulisy/Niewidzialne"), s.cechy(cien=False):
        for zn in (-1, 1):
            s.blok("Niewidzialna ściana", ((u0 + u1) / 2.0, 40.0, zn * w), (u1 - u0, 80.0, 2.0), "biel", alfa=1.0)
        s.blok("Niewidzialna ściana", (u0 - 1.0, 40.0, 0.0), (2.0, 80.0, 2 * w + 2.0), "biel", alfa=1.0)
