# -*- coding: utf-8 -*-
"""Detale biomu Las (wersja 2 mapy): to, na co gracz patrzy z bliska. Kontrakt: PROJEKT.md, rozdz. 15 „Detale”.

    brzegi_sciezek(s, G)     kamyki, kępki, kwiatki, grzybki, korzenie, paprocie, pnącza przy krawędziach ścieżek
                             (liczba na 100 st ścieżki zależy od podbiomu — GESTOSC_SCIEZEK)
    runo(s, G)               kępy runa między drzewami: łany kwiatów, wysoka trawa, kretowiska, grzybki, paprocie,
                             pnącza, kamyki (RUNO) i powalone kłody
    garby(s, G)              łagodne nierówności terenu (niskie ostrosłupy w kolorze i fakturze gruntu)
    rekwizyty_lokacji(s, G)  płotki, lampiony, skrzynki, beczki, kosze, stosy drewna i kamieni, tabliczki BEZ napisów

Zasady (jak w rozsiewie roślin, generuj.py): nic na ścieżce, w wodzie, na rampie ani na urwisku; place walki (r 12)
wolne z zapasem — detale ≥ 13 + promień detalu od węzła; wyższe detale (kłody, rekwizyty) także z dala od tras potworów,
patroli i trolla. Drobiazgi bez kolizji i bez cienia; kolizję mają tylko kłody i korpusy rekwizytów. Losowość z ziarna
generatora (G.rnd_detale). Wszystko w układzie lasu.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import geo, rosliny, skaly, teren  # noqa: E402
from swiat.biom_las.lokacje import wspolne  # noqa: E402
from swiat.biom_las.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402

GRUPA = {"laka": "Laka", "kapeluszowo": "Kapeluszowo", "serce": "Serce", "ostepy": "Ostepy", "wawoz": "Wawoz", "korona": "Korona"}

# podbiom: (sztuk na 100 st ścieżki, obie strony razem; {rodzina: waga})
GESTOSC_SCIEZEK = {
    "laka":        (14, {"kepka": 4, "kwiatek": 4, "kamyki": 2, "wysoka_trawa": 2, "kretowisko": 1}),
    "kapeluszowo": (14, {"grzybki": 4, "paproc": 3, "kepka": 2, "korzen": 2, "kamyki": 1, "pnacze": 1}),
    "serce":       (10, {"kwiatek": 3, "kepka": 3, "korzen": 2, "grzybki": 1}),
    "ostepy":      (14, {"paproc": 4, "korzen": 3, "pnacze": 2, "kamyki": 2, "grzybki": 2, "patyk": 1}),
    "wawoz":       (12, {"kamyki": 4, "kepka_sucha": 3, "krzaczek": 2, "patyk": 1, "kosc": 1}),
    "korona":      (12, {"kamyki": 3, "kwiatek": 3, "kepka": 3, "korzen": 1}),
}
# podbiom: (kępy runa, {rodzina: waga}, kłody) — kępa = 2–3 drobiazgi w promieniu ok. 3
RUNO = {
    "laka":        (60, {"lan_kwiatow": 3, "wysoka_trawa": 3, "kretowisko": 1, "kamyki": 1}, 8),
    "kapeluszowo": (70, {"grzybki": 3, "paproc": 3, "pnacze": 2, "kwiatek": 1}, 12),
    "serce":       (30, {"kwiatek": 2, "paproc": 2, "grzybki": 1}, 4),
    "ostepy":      (80, {"paproc": 4, "pnacze": 3, "grzybki": 2, "patyk": 1, "kamyki": 1}, 18),
    "wawoz":       (50, {"kepka_sucha": 3, "krzaczek": 3, "kamyki": 2, "patyk": 1}, 4),
    "korona":      (55, {"kwiatek": 3, "kepka": 2, "kamyki": 2, "paproc": 1}, 6),
}
# etap 3: o połowę mniej garbów (na zrzutach ze Studio prawie niewidoczne — w tym samym kolorze i fakturze co grunt);
# oszczędzone części poszły w darń rantu półek, jezioro i labirynt
GARBY = {"laka": 22, "kapeluszowo": 18, "serce": 4, "ostepy": 22, "wawoz": 8, "korona": 10}

KEPKA = {"laka": ("lisc", "trawa", "lisc_jasny"), "kapeluszowo": ("lisc_ciemny", "lisc", "runo"),
         "serce": ("lisc", "lisc_ciemny", "trawa"), "ostepy": ("lisc_ciemny", "igla", "runo"),
         "wawoz": ("lisc_ciemny", "trawa_sucha", "trawa"), "korona": ("lisc", "lisc_jasny", "trawa")}
# etap 3: suche kępki Wąwozu dostały oliwkową zieleń — słoma na słomianej półce znikała (zrzut l24)
KWIATY = {"laka": ("zloto", "biel", "czerwien", "dach_sklep"), "kapeluszowo": ("biel", "czerwien"), "serce": ("zloto", "pomarancz", "biel"),
          "ostepy": ("dach_sklep", "biel"), "wawoz": ("zloto",), "korona": ("biel", "dach_sklep", "zloto")}
GRZYBY = {"kapeluszowo": (("czerwien", "biel"), ("drewno", "tynk_krem"), ("tynk_krem", "biel")),
          "ostepy": (("drewno", "tynk_krem"), ("dach_sklep", "tynk_krem"), ("drewno_jasne", "biel")),
          "serce": (("drewno_jasne", "tynk_krem"), ("czerwien", "biel")), "laka": (("drewno_jasne", "tynk_krem"),),
          "korona": (("drewno", "tynk_krem"),), "wawoz": (("drewno", "tynk_krem"),)}


def _kamien(pb):
    return ("kamien_lochu", "Slate") if pb == "ostepy" else ("kamien_cieply", "SmoothPlastic")


# =========================================================================== rodziny drobiazgów (pos = środek na ziemi)
def kepka(s, rnd, pos, kolory, nazwa="Kępka", k=1.0):
    """Kępka trawy: trzy cienkie kliny rozchylone w wachlarz. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        for i in range(3):
            h = rnd.uniform(0.9, 1.7) * k
            with s.uklad(obrot=(0, 120 * i + rnd.uniform(-20, 20), 0)):
                s.klin(nazwa, (0, h / 2.0 - 0.05, 0.35), (0.35, h, rnd.uniform(0.9, 1.4) * k), kolory[i % len(kolory)],
                       rot=(rnd.uniform(-14, -4), 0, rnd.uniform(-8, 8)))


def kwiatek(s, rnd, pos, kolor):
    """Kwiatek: niska kępka liści i jeden płaski kwiat-talerzyk. 2 części. (W Studio kwiat-kostka 0,7 wyglądał jak
    kostka do gry — talerzyk 0,95 × 0,28 obrócony o 45° czyta się jak kielich z góry i z oczu gracza.)
    Etap 3: kępka to klin (liść odchylony od kwiatu), nie płaska kostka — zielona cegiełka z kafelkiem wyglądała jak klocek."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), 0)), s.cechy(kolizja=False, cien=False):
        s.klin("Kępka", (-0.1, 0.4, -0.15), (0.9, 0.8 + rnd.uniform(-0.06, 0.06), 1.3), "lisc_ciemny", rot=(0, 0, 0))
        s.blok("Kwiatek", (0.2, 0.68, 0.1), (0.95, 0.28, 0.95), kolor, rot=(9, 45 + rnd.uniform(0, 90), 6))


def lan_kwiatow(s, rnd, pos, kolory):
    """Łan kwiatów (Łąka): długa niska kępa liści i 5–6 kwiatów w smudze. 6–7 części."""
    x, y, z = pos
    dl = rnd.uniform(6.0, 8.5)
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(kolizja=False, cien=False):
        # etap 3: grzbiet liści z dwóch klinów zamiast płaskiej zielonej deski (z oczu gracza „klocek z kafelkami”)
        r_ = (0, rnd.uniform(-6, 6), rnd.uniform(-4, 4))
        with s.uklad(obrot=r_):
            s.klin("Kępka", (0.65, 0.5, 0), (dl, 1.0, 1.3), "lisc_ciemny", rot=(0, -90, 0))
            s.klin("Kępka", (-0.65, 0.5, 0), (dl, 1.0, 1.3), "lisc", rot=(0, 90, 0))
        n = rnd.randint(5, 6)
        for i in range(n):
            t = (i + 0.5) / n - 0.5
            fx = rnd.uniform(-0.6, 0.6)
            s.blok("Kwiatek", (fx, 0.62 + 0.9 * (1.0 - abs(fx) / 1.3) - 0.3 + rnd.uniform(0.0, 0.08), t * dl * 0.9), (0.85, 0.26, 0.85),
                   kolory[(i + rnd.randint(0, 1)) % len(kolory)], rot=(rnd.uniform(0, 10), 45 + rnd.uniform(0, 90), rnd.uniform(0, 8)))


def wysoka_trawa(s, rnd, pos, kolory):
    """Wysoka trawa (Łąka): cztery smukłe źdźbła 2–3,2 wychylone na boki. 4 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        for i in range(4):
            h = rnd.uniform(2.0, 3.2)
            a = math.radians(90 * i + rnd.uniform(-25, 25))
            with s.uklad(pos=(0.5 * math.cos(a), 0, 0.5 * math.sin(a)), obrot=(rnd.uniform(-12, 12), 0, rnd.uniform(-14, 14))):
                s.blok("Wysoka trawa", (0, h / 2.0 - 0.1, 0), (0.3, h, 0.3), kolory[i % len(kolory)])


def grzybki(s, rnd, pos, kolory):
    """Grzybki: 2–3 małe grzyby (trzonek i kapelusik), przechylone w różne strony. 4–6 części."""
    x, y, z = pos
    kap, trz = kolory
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        for i in range(rnd.choice((2, 2, 3))):
            h = rnd.uniform(0.6, 1.3)
            with s.uklad(pos=(0.9 * i - 0.5, 0, rnd.uniform(-0.6, 0.6)), obrot=(rnd.uniform(-10, 10), 0, rnd.uniform(-14, 14))):
                s.blok("Grzybek", (0, h / 2.0 - 0.05, 0), (0.35, h, 0.35), trz)
                s.walec("Grzybek kapelusz", (0, h, 0), rnd.uniform(0.45, 0.75), 0.35, kap, os="y")


def korzen(s, rnd, pos, k=1.0):
    """Korzeń wychodzący z ziemi łukiem (dwie belki). 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        s.belka("Korzeń ścieżki", (-1.7 * k, -0.25, 0), (0.0, 0.5 * k, 0.3), 0.55 * k, "drewno_ciemne", "Wood")
        s.belka("Korzeń ścieżki", (0.0, 0.5 * k, 0.3), (1.9 * k, -0.25, 0.7), 0.45 * k, "drewno_ciemne", "Wood")


def patyk(s, rnd, pos):
    """Gałązka na ziemi, czasem z kępką liści. 1–2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        s.belka("Gałązka", (-1.3, 0.12, 0), (1.3, 0.22, 0.3), 0.25, "drewno", "Wood")
        if rnd.random() < 0.5:
            s.blok("Gałązka liście", (1.1, 0.3, 0.4), (0.9, 0.35, 0.7), "lisc_ciemny", rot=(0, 30, 8))


def pnacze(s, rnd, pos, kolory=("lisc_ciemny", "runo_ciemne")):
    """Pnącze płożące się po ziemi: 3–4 płaskie liście na wijącym się pędzie, lekko przechylone. 4–5 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 360), 0)), s.cechy(kolizja=False, cien=False):
        s.belka("Pnącze", (-2.2, 0.16, 0), (2.2, 0.2, rnd.uniform(-0.8, 0.8)), 0.15, "drewno_ciemne", "Wood")
        for i in range(rnd.choice((3, 4))):
            t = -1.8 + 1.2 * i
            s.blok("Liść pnącza", (t, 0.22, rnd.choice((-0.4, 0.4))), (1.0, 0.14, 0.7), kolory[i % 2],
                   rot=(rnd.uniform(-12, 12), rnd.uniform(0, 90), rnd.uniform(-10, 10)))


def kretowisko(s, rnd, pos):
    """Kretowisko (Łąka): kopczyk ziemi z dwóch klinów i grudka. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(kolizja=False, cien=False):
        s.klin("Kretowisko", (0, 0.35, -0.55), (1.8, 0.7, 1.1), "ziemia")
        s.klin("Kretowisko", (0, 0.35, 0.55), (1.8, 0.7, 1.1), "ziemia", rot=(0, 180, 0))
        s.blok("Ziemia kretowiska", (0.9, 0.12, 0.6), (0.5, 0.25, 0.4), cien(s, "ziemia", 0.85), rot=(0, 30, 0))


def kosc(s, rnd, pos):
    """Kość na ziemi (Wąwóz): drążek z dwiema gałkami. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(kolizja=False, cien=False):
        s.blok("Kość", (0, 0.2, 0), (1.6, 0.35, 0.35), "biel")
        for zn in (-1, 1):
            s.blok("Kość", (zn * 0.85, 0.25, 0), (0.45, 0.45, 0.7), "biel")


def kloda(s, rnd, pos, k=1.0, mech=True):
    """Powalona kłoda: walec z kolizją wtopiony 0,25 w ziemię, jasne słoje na czole, pas mchu, czasem grzybki.
    3–6 części."""
    x, y, z = pos
    r = rnd.uniform(0.85, 1.25) * k
    dl = rnd.uniform(6.0, 10.0) * k
    with s.uklad(pos=(x, y + r - 0.25, z), obrot=(0, rnd.uniform(0, 180), rnd.uniform(-3, 3))):
        with s.cechy(kolizja=True):
            s.walec("Kłoda", (0, 0, 0), r, dl, "drewno", "Wood", os="z")
        with s.cechy(kolizja=False, cien=False):
            s.walec("Kłoda słoje", (0, 0, dl / 2.0 + 0.05), r * 0.85, 0.15, "drewno_jasne", os="z")
            if mech:
                s.blok("Mech", (0, r - 0.05, rnd.uniform(-1, 1)), (r * 1.1, 0.3, dl * 0.55), "mech", rot=(0, rnd.uniform(-4, 4), 0))
            if rnd.random() < 0.5:
                s.blok("Sęk", (r * 0.9, 0.2, -dl * 0.25), (0.8, 0.5, 0.5), "drewno_ciemne", rot=(0, 0, 20))


def drobiazg(s, rnd, rodzina, pos, pb):
    """Postaw jeden drobiazg rodziny `rodzina` w podbiomie `pb`. Zwraca promień zajęty na ziemi."""
    x, y, z = pos
    if rodzina == "kepka":
        kepka(s, rnd, pos, KEPKA[pb])
        return 1.0
    if rodzina == "kepka_sucha":
        kepka(s, rnd, pos, KEPKA["wawoz"], "Kępka sucha", k=rnd.uniform(0.8, 1.1))
        return 1.0
    if rodzina == "kwiatek":
        kwiatek(s, rnd, pos, rnd.choice(KWIATY[pb]))
        return 0.9
    if rodzina == "lan_kwiatow":
        lan_kwiatow(s, rnd, pos, rnd.sample(KWIATY["laka"], 2))
        return 4.5
    if rodzina == "wysoka_trawa":
        wysoka_trawa(s, rnd, pos, ("lisc", "trawa", "lisc_jasny"))
        return 1.2
    if rodzina == "kamyki":
        kol, mat = _kamien(pb)
        skaly.kamyki(s, rnd, pos, kol, mat)
        return 1.4
    if rodzina == "grzybki":
        grzybki(s, rnd, pos, rnd.choice(GRZYBY.get(pb, GRZYBY["serce"])))
        return 1.4
    if rodzina == "korzen":
        korzen(s, rnd, pos, rnd.uniform(0.8, 1.2))
        return 2.2
    if rodzina == "patyk":
        patyk(s, rnd, pos)
        return 1.4
    if rodzina == "pnacze":
        pnacze(s, rnd, pos)
        return 2.4
    if rodzina == "paproc":
        rosliny.paproc(s, rnd, pos, rnd.uniform(0.7, 1.0))
        return 1.4
    if rodzina == "kretowisko":
        kretowisko(s, rnd, pos)
        return 1.2
    if rodzina == "kosc":
        kosc(s, rnd, pos)
        return 1.0
    if rodzina == "krzaczek":
        rosliny.krzak(s, rnd, pos, rnd.uniform(0.42, 0.6), kolory=("lisc_ciemny", "trawa", "trawa_sucha"))
        return 1.6
    raise ValueError("nieznana rodzina detalu: " + rodzina)


# ok. 30% miejsc odpada (place walki, rdzenie lokacji, pnie, zbocza) — losujemy częściej, żeby wyszło blisko celu
NADDATEK = 1.4
# zasięg drobiazgu na ziemi (do odstępu od krawędzi ścieżki; paproć i korzeń sięgają dalej niż kępka)
ZASIEG = {"krzaczek": 1.6, "lan_kwiatow": 4.5, "korzen": 2.2, "pnacze": 2.4, "paproc": 2.0, "kamyki": 1.4, "grzybki": 1.5, "patyk": 1.5,
          "wysoka_trawa": 1.2, "kretowisko": 1.2}


def _losuj(rnd, wagi):
    suma = sum(wagi.values())
    t = rnd.uniform(0, suma)
    for k, w in wagi.items():
        t -= w
        if t <= 0:
            return k
    return k


# =========================================================================== kontrola miejsca
def miejsce_ok(G, x, z, r, wysoki=False, sciezka_min=0.25, spadek=0.9):
    """Czy drobiazg o promieniu r może stanąć w (x, z): poza ścieżką, wodą, rampą, urwiskiem i placami walki, nie w rdzeniu
    lokacji ani w pniu drzewa; wysoki (kłoda) także z dala od tras potworów, patroli i trolla. `spadek` = największa
    różnica wysokości w oknie 8 × 8 st (0,9 przepuszcza łagodne zbocze polany 1 : 10, odrzuca urwiska i zbocze Pagórka)."""
    if max(abs(x), abs(z)) > 428:
        return False
    if G.siatka("d_sciezka", x, z) < r + sciezka_min or G.siatka("d_woda", x, z) < r + 0.4:
        return False
    if G.siatka("d_walka", x, z) < 13.0 + r or G.siatka("d_rampa", x, z) < r + 1.5:
        return False
    if any(G.siatka("nierownosc", x + dx, z + dz) > spadek for dx, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r))):
        return False
    if wysoki and (G.siatka("d_trasa", x, z) < 5 + r or G.siatka("d_patrol", x, z) < 6 + r or G.siatka("d_troll", x, z) < 6 + r):
        return False
    if not G.wolne_w(G.lokacje_maska, x, z, r) or not G.wolne_w(G.pnie, x, z, r):
        return False
    if any(math.hypot(x - sp["srodek"][0], z - sp["srodek"][1]) < 14 for sp in G.spokoj if sp["id"].startswith("pin_")):
        return False
    return True


# =========================================================================== przebiegi
def brzegi_sciezek(s, G):
    """Drobiazgi przy krawędziach ścieżek (GESTOSC_SCIEZEK, sztuk na 100 st). Krok co 2 st, strona losowa, odsunięcie
    0,9–3,0 od krawędzi (krawężnik Łąki leży 0,3–0,9 od krawędzi). Sekretnej ścieżki nie ruszamy (ma być ukryta)."""
    rnd = G.rnd_detale
    stat = {}
    dlug = {}
    for sc in G.U["sciezki"]:
        if sc["rodzaj"] == "sekretna":
            continue
        pol = sc["szer"] / 2.0
        for x, z, dx, dz in geo.punkty_co(sc["pts"], 2.0):
            pb = G.podbiom_szybko(x, z)
            if pb is None:
                continue
            dlug[pb] = dlug.get(pb, 0.0) + 2.0
            gest, wagi = GESTOSC_SCIEZEK[pb]
            if rnd.random() > gest / 100.0 * 2.0 * NADDATEK:
                continue
            rodzina = _losuj(rnd, wagi)
            r = ZASIEG.get(rodzina, 1.0)
            for proba in range(4):                             # druga strona, dalej od krawędzi — zanim zrezygnujemy
                zn = rnd.choice((-1, 1))
                off = pol + rnd.uniform(0.9, 3.0) + 0.6 * proba
                px, pz = x - dz * zn * off, z + dx * zn * off
                if miejsce_ok(G, px, pz, r * 0.85, sciezka_min=0.3) and G.wolne_w(G.detale_maska, px, pz, 0.8):
                    break
            else:
                continue
            with s.grupa("%s/Detale/Sciezki" % GRUPA[pb]):
                drobiazg(s, rnd, rodzina, (px, G.T.H(px, pz), pz), pb)
            G.zajmij_w(G.detale_maska, px, pz, 1.0)
            stat[pb] = stat.get(pb, 0) + 1
    return stat, dlug


def runo(s, G):
    """Kępy runa między drzewami (2–3 drobiazgi w promieniu ok. 3), gęściej bliżej ścieżek (85% w pasie 30 st),
    i powalone kłody (z kolizją, z dala od tras potworów)."""
    rnd = G.rnd_detale
    stat = {}
    for pb, (n, wagi, n_klod) in RUNO.items():
        w = G.pod[pb]["wielokat"]
        xs, zs = [p[0] for p in w], [p[1] for p in w]
        postawione = proby = 0
        while postawione < n and proby < n * 80:
            proby += 1
            x, z = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(zs), max(zs))
            if G.podbiom_szybko(x, z) != pb:
                continue
            dsc = G.siatka("d_sciezka", x, z)
            if dsc > 30 and rnd.random() > 0.15:
                continue
            if pb == "serce" and math.hypot(x, z) < 75:
                continue
            if not miejsce_ok(G, x, z, 3.0, sciezka_min=2.6):
                continue
            with s.grupa("%s/Detale/Runo" % GRUPA[pb]):
                for i in range(rnd.choice((2, 2, 3))):
                    a = rnd.uniform(0, 2 * math.pi)
                    rr = 0.0 if i == 0 else rnd.uniform(1.6, 3.0)
                    px, pz = x + rr * math.cos(a), z + rr * math.sin(a)
                    drobiazg(s, rnd, _losuj(rnd, wagi), (px, G.T.H(px, pz), pz), pb)
            G.zajmij_w(G.detale_maska, x, z, 3.5)
            postawione += 1
        klody = proby = 0
        while klody < n_klod and proby < n_klod * 200:
            proby += 1
            x, z = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(zs), max(zs))
            if G.podbiom_szybko(x, z) != pb or G.siatka("d_sciezka", x, z) > 25:
                continue
            if not miejsce_ok(G, x, z, 5.5, wysoki=True, sciezka_min=1.0, spadek=0.05) or not G.wolne_w(G.detale_maska, x, z, 5.0):
                continue
            with s.grupa("%s/Detale/Runo" % GRUPA[pb]):
                kloda(s, rnd, (x, G.siatka("H", x, z), z), rnd.uniform(0.85, 1.15), mech=pb != "wawoz")
            G.zajmij_w(G.detale_maska, x, z, 5.5)
            G.zajmij_w(G.pnie, x, z, 4.5)
            klody += 1
        stat[pb] = (postawione, n, klody, n_klod)
    return stat


def kolor_gruntu(G, x, z, pb):
    p = G.T.poziom_w(x, z)
    if p is not None:
        return teren.KOLOR_POZIOMU.get(p["id"], "runo")
    return teren.KOLOR_PODBIOMU[pb]


def garby(s, G):
    """Łagodne nierówności (wersja 2): niskie ostrosłupy (4 kliny narożne) 8–16 × 8–14 i wysokie 0,5–1,1 (spadek ≤ 1 : 4),
    w kolorze i fakturze gruntu pod spodem, bez kolizji i cienia; tylko na płaskim gruncie, z dala od ścieżek, wody,
    ramp, urwisk, placów walki i tras potworów."""
    rnd = G.rnd_detale
    stat = {}
    for pb, n in GARBY.items():
        w = G.pod[pb]["wielokat"]
        xs, zs = [p[0] for p in w], [p[1] for p in w]
        postawione = proby = 0
        while postawione < n and proby < n * 100:
            proby += 1
            x, z = rnd.uniform(min(xs), max(xs)), rnd.uniform(min(zs), max(zs))
            if G.podbiom_szybko(x, z) != pb or (pb == "serce" and math.hypot(x, z) < 80):
                continue
            a, b = rnd.uniform(4.0, 8.0), rnd.uniform(4.0, 7.0)
            r = math.hypot(a, b)
            if G.siatka("d_sciezka", x, z) < r + 1.5 or G.siatka("d_woda", x, z) < r + 1.0 or G.siatka("d_walka", x, z) < 14 + r:
                continue
            if G.siatka("d_trasa", x, z) < 4 + r or G.siatka("d_patrol", x, z) < 4 + r or G.siatka("d_troll", x, z) < 6 + r:
                continue
            if G.siatka("d_rampa", x, z) < r + 3 or any(G.siatka("nierownosc", x + dx, z + dz) > 0.05
                                                         for dx, dz in ((0, 0), (r, 0), (-r, 0), (0, r), (0, -r))):
                continue
            if not G.wolne_w(G.lokacje_maska, x, z, r) or not G.wolne_w(G.garby_maska, x, z, r + 2):
                continue
            h0 = G.siatka("H", x, z)
            hb = rnd.uniform(0.5, 1.1)
            with s.grupa("%s/Detale/Garby" % GRUPA[pb]), s.cechy(kolizja=False, cien=False):
                with s.uklad(pos=(x, h0, z), obrot=(0, rnd.uniform(0, 90), 0)):
                    s.ostroslup("Garb", (0, 0, 0), a, b, hb, kolor_gruntu(G, x, z, pb))
            G.zajmij_w(G.garby_maska, x, z, r)
            postawione += 1
        stat[pb] = (postawione, n)
    return stat


# =========================================================================== rekwizyty przy lokacjach
def plotek(s, rnd, pos, ry):
    """Płotek z 1–2 przęseł (zestaw miasteczka): sztachety z kolizją, żerdzie bez. 5–10 części."""
    x, y, z = pos
    n = rnd.choice((1, 2))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        pts = [(-2.8 * n, 0.0), (0.0, rnd.uniform(-0.8, 0.8)), (2.8 * n, rnd.uniform(-0.6, 0.6))] if n == 2 else [(-2.8, 0.0), (2.8, 0.3)]
        zestaw.plot(s, pts, rnd, wys=2.6, przeslo=5.6)
    return 3.0 * n


def skrzynka(s, rnd, pos, ry):
    """Skrzynka: korpus z kolizją, wieko, listwa. 3 części."""
    x, y, z = pos
    a = rnd.uniform(1.8, 2.4)
    with s.uklad(pos=(x, y, z), obrot=(0, ry, rnd.uniform(-5, 5))):
        s.blok("Skrzynia", (0, a / 2.0 - 0.1, 0), (a * 1.25, a, a), "drewno", "WoodPlanks")
        with s.cechy(kolizja=False):
            s.blok("Skrzynia wieko", (0, a + 0.05, 0), (a * 1.25 + 0.3, 0.35, a + 0.3), "drewno_jasne")
            s.blok("Skrzynia listwa", (0, a / 2.0, a / 2.0 + 0.05), (a * 1.25, 0.4, 0.15), "drewno_ciemne")
    return 1.8


def beczka(s, rnd, pos, ry):
    zestaw.beczka(s, pos, rnd.choice((None, "jablka", "woda")), r=1.3, h=3.0, przechyl=(0.0, rnd.uniform(-5, 5)), ry=ry)
    return 1.6


def kosz(s, rnd, pos, ry):
    """Kosz z owocami: korpus i 2–3 owoce. 3–4 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.cechy(kolizja=False):
            s.blok("Kosz", (0, 0.55, 0), (1.8, 1.1, 1.4), "drewno_jasne", "WoodPlanks", rot=(0, 0, rnd.uniform(-4, 4)))
            with s.cechy(cien=False):
                for i in range(rnd.choice((2, 3))):
                    s.blok("Kosz jabłko", (-0.5 + 0.5 * i, 1.25, rnd.uniform(-0.3, 0.3)), (0.6, 0.6, 0.6),
                           rnd.choice(("czerwien", "zloto")), rot=(15, 30 * i, 10))
    return 1.3


def stos_drewna(s, rnd, pos, ry):
    """Stos polan: trzy krótkie kłody 2 + 1, dolne z kolizją. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        for i, (dx, dy) in enumerate(((-0.75, 0.6), (0.75, 0.6), (0.0, 1.6))):
            with s.cechy(kolizja=i < 2):
                s.walec("Stos drewna", (dx, dy, 0), 0.62, rnd.uniform(3.2, 3.8), "drewno" if i != 1 else "drewno_ciemne", "Wood", os="z",
                        rot=(0, rnd.uniform(-6, 6), 0))
    return 2.0


def stos_kamieni(s, rnd, pos, ry, pb="wawoz"):
    """Kopczyk kamieni (kopiec-znak): trzy kamienie jeden na drugim, bez kolizji. 3 części."""
    x, y, z = pos
    kol, mat = _kamien(pb)
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.cechy(kolizja=False):
        yy = 0.0
        for i, a in enumerate((2.0, 1.5, 1.0)):
            h = a * 0.6
            s.blok("Stos kamieni", (rnd.uniform(-0.15, 0.15), yy + h / 2.0, 0), (a, h, a * 0.85), kol if i % 2 == 0 else cien(s, kol, 0.85),
                   mat, rot=(rnd.uniform(-8, 8), rnd.uniform(0, 90), rnd.uniform(-8, 8)))
            yy += h - 0.08
    return 1.2


ZNAK_PODBIOMU = {"laka": ("galareta", "Galareta"), "kapeluszowo": ("czerwien", "Kapelusik"), "serce": ("lisc_rudy", "Liść"),
                 "ostepy": ("dach_sklep", "Ucho"), "wawoz": ("dach_brama", "Maczuga"), "korona": ("biel", "Kryształ")}


def tabliczka(s, rnd, pos, ry, pb="laka"):
    """Tabliczka-rekwizyt BEZ NAPISU: słup, pusta deska i naklejony znak podbiomu (kształt w kolorze kodu). 3 części."""
    x, y, z = pos
    kol, _ = ZNAK_PODBIOMU[pb]
    with s.uklad(pos=(x, y, z), obrot=(0, ry, rnd.choice((-5, 5)))):
        s.blok("Tabliczka słup", (0, 1.6, 0), (0.45, 3.4, 0.45), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Tabliczka", (0, 2.8, 0.3), (2.6, 1.5, 0.25), "drewno_jasne", rot=(0, 0, rnd.uniform(-6, 6)))
            with s.cechy(cien=False):
                s.naroznik("Tabliczka znak", (0, 2.8, 0.47), (0.8, 0.8, 0.12), kol, rot=(0, 0, 45))
    return 1.2


def czaszka(s, rnd, pos, ry):
    """Pal z czaszką-klockiem (ostrzeżenie bez napisu). 4 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, rnd.choice((-6, 6)))):
        s.blok("Tabliczka słup", (0, 1.9, 0), (0.5, 4.0, 0.5), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Czaszka-klocek", (0, 4.3, 0), (1.6, 1.4, 1.5), "biel", rot=(0, 0, 8))
            with s.cechy(cien=False):
                for xx in (-0.35, 0.35):
                    s.blok("Oczodół", (xx, 4.4, 0.76), (0.42, 0.42, 0.1), "tusz")
    return 1.0


def lampion(s, rnd, pos, ry):
    with s.uklad(pos=pos, obrot=(0, ry, 0)):
        wspolne.lampion(s, (0, 0, 0), rnd.uniform(4.6, 5.6))
    return 1.4


REKWIZYTY = {   # lokacja: rodzaje rekwizytów (stawiane na pierścieniu r+3 … r+14 wokół lokacji)
    "brama_pniakow": ["plotek", "plotek", "beczka", "skrzynka", "kosz", "tabliczka"],
    "oczko_galaretek": ["plotek", "kosz", "skrzynka", "tabliczka"],
    "most_rechotek": ["tabliczka", "lampion"],
    "przewrocony_woz": ["beczka", "skrzynka", "kosz", "stos_drewna"],
    "pagorek_klocka": ["tabliczka", "stos_kamieni"],
    "kladka_z_pnia": ["tabliczka", "stos_drewna"],
    "wielki_kapelusz": ["plotek", "plotek", "skrzynka", "skrzynka", "beczka", "kosz", "stos_drewna", "tabliczka"],
    "krag_zarodnikow": ["lampion", "tabliczka", "kosz"],
    "gniazdo_w_korzeniach": ["skrzynka", "kosz", "lampion"],
    "dziupla_turniejowa": ["skrzynka", "beczka", "plotek", "lampion"],
    "korzenna_gardziel": ["czaszka", "lampion", "stos_kamieni"],
    "wilcza_skala": ["czaszka", "stos_kamieni", "stos_drewna"],
    "jezynowy_labirynt": ["czaszka", "tabliczka"],
    "szumiacy_prog": ["stos_kamieni"],
    "wrota_bagna": ["lampion", "czaszka"],
    "schody_glazow": ["stos_kamieni", "czaszka"],
    "wyschnieta_kaluza": ["tabliczka", "beczka", "stos_drewna"],
    "trollowa_tama": ["beczka", "beczka", "skrzynka", "stos_kamieni"],
    "rozstaj_pod_sowa": ["plotek", "skrzynka"],
    "kamienny_krag": ["stos_kamieni"],
    "lawka_z_widokiem": ["lampion", "kosz"],
}
BUDOWNICZY = {"plotek": plotek, "skrzynka": skrzynka, "beczka": beczka, "kosz": kosz, "stos_drewna": stos_drewna,
              "stos_kamieni": stos_kamieni, "tabliczka": tabliczka, "czaszka": czaszka, "lampion": lampion}
PROMIEN = {"plotek": 6.0, "skrzynka": 1.8, "beczka": 1.6, "kosz": 1.3, "stos_drewna": 2.0, "stos_kamieni": 1.2, "tabliczka": 1.2,
           "czaszka": 1.0, "lampion": 2.0}


def rekwizyty_lokacji(s, G):
    """Drobne rekwizyty przy lokacjach (REKWIZYTY): na pierścieniu r+3 … r+14 wokół środka, blisko ścieżki (1,5–9 st od
    krawędzi), na płaskim gruncie, poza placami walki (≥ 14 + promień), trasami potworów, wodą i rampami; zwrócone
    frontem do najbliższej ścieżki (z rozrzutem). Wywoływane PRZED rozsiewem — drzewa omijają rekwizyty."""
    rnd = G.rnd_detale
    lok = {l["id"]: l for l in G.U["lokacje"]}
    n_ok, braki = 0, []
    for lid, rodzaje in REKWIZYTY.items():
        L = lok[lid]
        pb = L["podbiom"]
        for rodzaj in rodzaje:
            rr = PROMIEN[rodzaj]
            best = None
            for proba in range(400):
                a = rnd.uniform(0, 2 * math.pi)
                d = L["r"] + rnd.uniform(3.0, 14.0 + 10.0 * (proba >= 200))
                x, z = L["x"] + d * math.cos(a), L["z"] + d * math.sin(a)
                if max(abs(x), abs(z)) > 426:
                    continue
                dsc = G.siatka("d_sciezka", x, z)
                if not (1.5 + rr <= dsc <= 9.0 + rr):
                    continue
                if G.siatka("d_woda", x, z) < rr + 1.0 or G.siatka("d_walka", x, z) < 14.0 + rr or G.siatka("d_rampa", x, z) < rr + 3:
                    continue
                if G.siatka("d_trasa", x, z) < 5 + rr or G.siatka("d_patrol", x, z) < 6 + rr or G.siatka("d_troll", x, z) < 6 + rr:
                    continue
                if any(G.siatka("nierownosc", x + dx, z + dz) > (0.05 if rodzaj == "plotek" else 0.9)
                       for dx, dz in ((0, 0), (rr, 0), (-rr, 0), (0, rr), (0, -rr))):
                    continue
                if not G.wolne(x, z, rr + 0.5):
                    continue
                best = (x, z)
                break
            if best is None:
                braki.append("%s/%s" % (lid, rodzaj))
                continue
            x, z = best
            # front ku najbliższej krawędzi ścieżki: sprawdź 16 kierunków
            kier = min(range(16), key=lambda k: G.siatka("d_sciezka", x + 4 * math.sin(k * math.pi / 8), z + 4 * math.cos(k * math.pi / 8)))
            ry = kier * 22.5 + rnd.uniform(-20, 20)
            if rodzaj == "plotek":
                ry += 90.0                                     # płotek bokiem do ścieżki
            with s.grupa("%s/Lokacje/Rekwizyty" % GRUPA[pb]):
                f = BUDOWNICZY[rodzaj]
                pos = (x, G.T.H(x, z) - 0.05, z)
                if rodzaj in ("tabliczka", "stos_kamieni"):
                    f(s, rnd, pos, ry, pb)
                else:
                    f(s, rnd, pos, ry)
            G.zajmij(x, z, rr + 0.5)
            G.zajmij_w(G.lokacje_maska, x, z, rr + 0.3)
            n_ok += 1
    return n_ok, braki
