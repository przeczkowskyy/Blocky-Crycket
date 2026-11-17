# -*- coding: utf-8 -*-
"""Rodziny rekwizytów aren walki z klocków (układ SCENY walki, pos = podstawa na ziemi, ry = obrót wokół pionu).

Bierzemy bez zmian rodziny z map biomów (tylko import): drzewa, grzyby, krzaki i skały lasu (swiat/biom_las/rosliny.py,
skaly.py, detale.py), rośliny Bagna (swiat/bagno_pas/rosliny.py), rekwizyty miasteczka (swiat/krzywe_miasteczko/zestaw.py).
Własne są rzeczy, których mapy nie mają: olbrzymie pnie polany, korony nad polaną, smugi światła, pomost-plac Bagna,
chatki na palach i wieża w wersji tła, manekiny, tarcze, stojaki, bele, trybuna, namiot, domki i mury miasteczka w
wersji tła oraz dalekie sylwety (wzgórza, korony, dachy, zamek) w kolorach jaśniejących ku mgle.

Każda rodzina zwraca (wysokość, promień na ziemi) — generator liczy z nich pierwsze miejsce poza wolną przestrzenią
kamer, a ostatnie słowo ma kontrola na punktach części (generuj.Budowa.postaw).
Kolizji arena nie potrzebuje (nikt po niej nie chodzi — aktorzy to lokalne klony): generator wyłącza ją wszystkim
częściom na końcu, więc cechy kolizji z rodzin map nie mają tu znaczenia.
"""
import math
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biom_las import detale as det_lasu  # noqa: E402
from swiat.biom_las import rosliny as ros_lasu  # noqa: E402
from swiat.biom_las import skaly  # noqa: E402
from swiat.biom_las.paleta import PALETA as PALETA_LASU  # noqa: E402
from swiat.bagno_pas import rosliny as ros_bagna  # noqa: E402
from swiat.bagno_pas.kontekst import KOLORY_BAGNA  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.krzywe_miasteczko.zestaw import lamana  # noqa: E402

# paleta aren: paleta lasu (z miasteczkiem) + Bagno + kilka kolorów aren (tylko nowe klucze)
KOLORY_AREN = {
    "arena_ziemia": "BE9363",       # ubita, nasłoneczniona ziemia polany (plac lasu; Studio 17.11: było A9805A — szaro)
    "arena_ziemia_jasna": "D9B27E",
    "arena_slonce": "8FC04A",       # nasłoneczniona trawa wokół placu
    "arena_promien": "FFF1B8",      # smuga światła (Neon, półprzezroczysta)
    "arena_piasek": "E6C489",       # piasek placu ćwiczeń
    "arena_piasek_ciemny": "C9A56E",
    "arena_kreda": "FFF8EC",        # kredowe linie placu ćwiczeń
    "arena_sloma": "E8C35A",        # słoma manekinów i bel
    "arena_sloma_ciemna": "C49A3A",
    "arena_worek": "D9C29A",        # worek manekina
    "arena_mgla_las": "C9DDC4",     # daleka sylweta lasu w mgle (najjaśniejsza)
    "arena_mgla_bagno": "AEB9A6",
    "arena_mgla_miasto": "E7D9C2",
    "arena_wzgorze_las": "7FA77F",
    "arena_wzgorze_bagno": "6F7D66",
    "arena_wzgorze_miasto": "9DBB7A",
    "arena_dach_daleki": "C98A6E",
}
PALETA = dict(PALETA_LASU)
for _k, _v in list(KOLORY_BAGNA.items()) + list(KOLORY_AREN.items()):
    assert _k not in PALETA, "klucz zderza się z istniejącym kluczem palety: " + _k
    PALETA[_k] = _v


def _kontra(rnd, a, b):
    return rnd.choice((-1, 1)) * rnd.uniform(a, b)


def mieszaj(s, a, b, t):
    """Kolor a → b w proporcji t (0…1), oba jako klucze palety albo RRGGBB."""
    ha, hb = s.paleta.get(a, a), s.paleta.get(b, b)
    return "%02X%02X%02X" % tuple(int(round(int(ha[i:i + 2], 16) * (1 - t) + int(hb[i:i + 2], 16) * t)) for i in (0, 2, 4))


# =========================================================================== LAS — polana pod koronami
def olbrzym(s, rnd, pos, k=1.0, ry=0.0, korona_ku=None):
    """Olbrzymi stary pień (znak polany): walec Ø 7·k do 30·k, stopa z czterech korzeni-klinów, dwa pasy kory, pęknięcie
    z mchem, dwa konary i dwie wielkie czapy korony WYSOKO (od 30·k) — korona wychodzi ku `korona_ku` (kąt w stopniach
    układu, None = losowo), żeby nad polaną została dziura nieba. Wys. ok. 46·k. 15 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    d = 7.0 * k
    h = 31.0 * k
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        with s.uklad(obrot=(rnd.uniform(-2, 2), 0, zn * rnd.uniform(1.5, 3.5))):
            s.walec("Olbrzym pień", (0, h / 2.0 - 0.6, 0), d / 2.0, h + 1.2, "drewno", "Wood", os="y")
            s.walec("Olbrzym kora", (0, 5.0 * k, 0), d / 2.0 + 0.35, 1.6 * k, "drewno_ciemne", "Wood", os="y")
            s.walec("Olbrzym kora", (0, 17.0 * k, 0), d / 2.0 + 0.3, 1.2 * k, "drewno_ciemne", "Wood", os="y")
            with s.cechy(cien=False):
                s.blok("Olbrzym pęknięcie", (0, 10.0 * k, d / 2.0 - 0.1), (1.0 * k, 7.0 * k, 0.6), "tusz", rot=(0, 0, zn * 4))
                s.blok("Olbrzym mech", (0, 8.0 * k, d / 2.0 + 0.05), (2.6 * k, 3.2 * k, 0.5), "mech", rot=(0, 0, -zn * 8))
            for i in range(4):                                   # stopa: cztery korzenie-kliny rozchodzące się od pnia
                a = 90.0 * i + rnd.uniform(-20, 20)
                with s.uklad(obrot=(0, a, 0)):
                    s.klin("Olbrzym korzeń", (0, 1.6 * k, d / 2.0 + 1.6 * k), (2.2 * k, 3.6 * k, 3.6 * k), "drewno", "Wood",
                           rot=(0, 180, 0))
            kier = math.radians(korona_ku if korona_ku is not None else rnd.uniform(0, 360)) - math.radians(ry)
            ux, uz = math.cos(kier), math.sin(kier)
            for i, (t, dl, dy) in enumerate(((0.62, 9.0, 5.0), (0.82, 7.0, 6.5))):
                s.belka("Olbrzym konar", (0, h * t, 0), (ux * dl * k * (1 + 0.4 * i), h * t + dy * k, uz * dl * k * (1 + 0.4 * i)),
                        1.6 * k, "drewno", "Wood")
            with s.uklad(pos=(ux * 5.0 * k, h, uz * 5.0 * k), obrot=(rnd.uniform(-3, 3), rnd.uniform(0, 90), _kontra(rnd, 2, 5))):
                s.blok("Olbrzym korona spód", (0, 1.6 * k, 0), (26.0 * k, 4.4 * k, 22.0 * k), "lisc_ciemny")
                s.blok("Olbrzym korona", (zn * 1.5 * k, 5.4 * k, 0.8 * k), (20.0 * k, 4.2 * k, 18.0 * k), "lisc", rot=(0, 22, 0))
                s.blok("Olbrzym korona wierzch", (-zn * 1.0 * k, 8.8 * k, -0.6 * k), (12.0 * k, 3.4 * k, 11.0 * k), "lisc_jasny",
                       rot=(0, 48, 0))
                s.blok("Olbrzym korona boczna", (ux * 10.0 * k, 3.6 * k, uz * 10.0 * k), (12.0 * k, 4.0 * k, 11.0 * k), "lisc",
                       rot=(0, rnd.uniform(0, 90), 0))
    return 46.0 * k, d / 2.0 + 3.4 * k


def korona_nad(s, rnd, pos, dl, szer, grub=4.0, ry=0.0, kolory=("lisc_ciemny", "lisc")):
    """Płat korony nad polaną (wysoko, poza wolną przestrzenią kamer): ciemny spód i jaśniejszy wierzch. 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-4, 4), ry, rnd.uniform(-4, 4))), s.cechy(cien=False):
        s.blok("Korona nad polaną", (0, 0, 0), (dl, grub, szer), kolory[0])
        s.blok("Korona nad polaną wierzch", (rnd.uniform(-2, 2), grub * 0.75, rnd.uniform(-2, 2)), (dl * 0.7, grub * 0.8, szer * 0.72),
               kolory[1], rot=(0, rnd.uniform(-25, 25), 0))
    return y + grub, max(dl, szer) / 2.0


def promien_swiatla(s, rnd, pos, h=30.0, szer=4.0, ry=0.0, pochyl=18.0):
    """Smuga światła z prześwitu w koronach: wysoki, cienki, półprzezroczysty klocek Neon pochylony od słońca. 1 część."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, pochyl)), s.cechy(cien=False):
        s.blok("Smuga światła", (0, h / 2.0, 0), (szer, h, szer * 0.5), "arena_promien", "Neon", alfa=0.8)
    return h, szer


def kepa_grzybow(s, rnd, pos, k=1.0, ry=0.0):
    """Kępa grzybów przy placu: jeden średni muchomor (k 0,45–0,6 grzyba-olbrzyma) i grzybki wokół. ok. 12 części."""
    x, y, z = pos
    ros_lasu.grzyb(s, rnd, (x, y, z), 0.42 * k, ry, kapelusz="czerwien", kropki=True, trzon="biel")
    for i in range(2):
        a = rnd.uniform(0, 2 * math.pi)
        det_lasu.grzybki(s, rnd, (x + 2.4 * k * math.cos(a), y, z + 2.4 * k * math.sin(a)), ("czerwien", "biel"))
    return 4.4 * k, 2.6 * k


def wysepka_lasu(s, rnd, pos, k=1.0, ry=0.0):
    """Wysepka przy polanie (zamiast rozsypanych drobiazgów): pniak albo kłoda, dwie paprocie, grzybki, kwiaty i łata
    mchu w jednej kępie — niska (≤ ok. 2,6). ok. 12–16 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        mech_plat(s, rnd, (0, 0, 0), 3.4 * k)
        if rnd.random() < 0.5:
            ros_lasu.pniak(s, rnd, (0.4, 0, -0.6), 0.9 * k, rnd.uniform(0, 360))
        else:
            det_lasu.kloda(s, rnd, (0, 0, -0.8), 0.75 * k, mech=True)
        ros_lasu.paproc(s, rnd, (-2.2 * k, 0, 0.8), 1.1 * k)
        ros_lasu.paproc(s, rnd, (2.0 * k, 0, 1.2), 0.95 * k)
        det_lasu.grzybki(s, rnd, (1.2 * k, 0, 2.0 * k), ("czerwien", "biel"))
        ros_lasu.kwiaty(s, rnd, (-1.0 * k, 0, 2.4 * k), rnd.choice((("zloto", "biel"), ("biel", "dach_sklep"))))
    return 2.6 * k, 4.0 * k


def kepa_z_trzcina(s, rnd, pos, k=1.0, ry=0.0, y_wody=-1.8):
    """Kępa na wodzie z trzciną i liśćmi grzybieni (zamiast pojedynczych trzcin w otwartej wodzie). ok. 9–11 części."""
    x, _, z = pos
    kepa(s, rnd, (x, 0, z), 2.6 * k, rnd.uniform(0.8, 1.2), y_wody)
    top = y_wody + 0.9
    trzcina_zdzbla(s, rnd, (x + rnd.uniform(-0.8, 0.8), top, z + rnd.uniform(-0.8, 0.8)), rnd.uniform(2.6, 3.4), 2.8, False)
    for _ in range(2):
        a = rnd.uniform(0, 2 * math.pi)
        ros_bagna.grzybien(s, rnd, (x + 3.6 * k * math.cos(a), y_wody, z + 3.6 * k * math.sin(a)), rnd.uniform(0.8, 1.2),
                           kwiat=rnd.choice((None, "bagno_kwiat", "biel")))
    return top + 3.4, 3.0 * k


def brama_miejska(s, rnd, pos, ry=0.0, wys=10.0):
    """Brama w murze (front +Z ku placowi): dwie kwadratowe baszty z dachami, łuk z belką, wrota, tarcza herbowa. ok. 14 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        for zn in (-1, 1):
            s.blok("Brama baszta", (zn * 6.0, (wys + 6.0) / 2.0, 0), (5.0, wys + 6.0, 5.0), "kamien_cieply", "Cobblestone",
                   rot=(0, 0, zn * 1.5))
            s.ostroslup("Brama dach", (zn * 6.0, wys + 6.0, 0), 3.2, 3.2, 5.0, "dach_twierdza")
            with s.cechy(cien=False):
                s.blok("Brama okno", (zn * 6.0, wys + 1.5, 2.55), (1.0, 1.8, 0.2), "neon_okno", "Neon")
        s.blok("Brama nadproże", (0, wys - 0.4, 0), (7.4, 3.2, 4.0), "kamien_cieply", "Cobblestone")
        s.blok("Brama belka", (0, wys - 2.2, 2.05), (7.6, 0.8, 0.3), "drewno_ciemne")
        with s.cechy(cien=False):
            s.blok("Brama wrota", (0, (wys - 2.6) / 2.0, 0.4), (6.6, wys - 2.6, 0.4), "drewno", "WoodPlanks")
            s.blok("Brama wrota okucie", (0, (wys - 2.6) * 0.3, 0.65), (6.8, 0.4, 0.15), "metal_ciemny")
            s.blok("Brama wrota okucie", (0, (wys - 2.6) * 0.7, 0.65), (6.8, 0.4, 0.15), "metal_ciemny")
            s.walec("Brama herb", (0, wys + 0.2, 2.1), 1.1, 0.25, "dach_karczma", os="z")
            s.walec("Brama herb", (0, wys + 0.2, 2.25), 0.5, 0.2, "zloto", os="z")
    return wys + 11.0, 9.0


def wal_horyzontu(s, rnd, r, wys, kolor, n=24, y0=-1.0):
    """Ciągły niski wał na skraju świata (r, wysokość `wys`): n długich klinów grzbietem ku środkowi, zachodzących na
    siebie — gwarantuje, że nisko nad krawędzią gruntu nigdy nie widać pustki. n części."""
    for i in range(n):
        kat = 360.0 * i / n
        a = math.radians(kat)
        dl = 2 * math.pi * r / n * 1.18
        with s.uklad(pos=(r * math.cos(a), y0, r * math.sin(a)), obrot=(0, 90.0 - kat, 0)), s.cechy(cien=False):
            # klin: pionowa ściana na +Z lokalnym = na zewnątrz, skos opada ku środkowi areny (jak zbocze)
            s.klin("Wał horyzontu", (0, wys / 2.0, 0), (dl, wys, wys * 1.6), cien(s, kolor, rnd.uniform(0.94, 1.0)))
    return wys, r


def kamien_obreczy(s, rnd, pos, k=1.0, ry=0.0, kolor="kamien_cieply"):
    """Niski płaski kamień obręczy placu (≤ 1 wys.): przechylony blok i klin. 2 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-5, 5), ry, rnd.uniform(-6, 6))), s.cechy(cien=False):
        s.blok("Kamień obręczy", (0, 0.32 * k, 0), (2.6 * k, 0.9 * k, 1.8 * k), cien(s, kolor, 0.86), "Slate")
        s.klin("Kamień obręczy", (1.2 * k, 0.3 * k, 0.4 * k), (1.2 * k, 0.75 * k, 1.4 * k), kolor, "Slate", rot=(0, rnd.uniform(0, 360), 0))
    return 0.8 * k, 1.6 * k


def mech_plat(s, rnd, pos, r=2.0):
    """Płaska łata mchu / kwiatów na ziemi. 1 część."""
    x, y, z = pos
    with s.cechy(cien=False):
        s.walec("Łata mchu", (x, y + 0.04, z), r, 0.08, rnd.choice(("mech", "lisc_jasny", "arena_slonce")), os="y")
    return 0.1, r


def wzgorze(s, rnd, pos, szer, wys, kolor, ry=0.0, gl=None):
    """Daleka sylweta wzgórza: dwa kliny grzbietem do siebie (dach-grzbiet) i kopuła z kuli spłaszczonej blokiem. 3 części."""
    x, y, z = pos
    g = gl or szer * 0.6
    with s.uklad(pos=(x, y, z), obrot=(0, ry, rnd.uniform(-2, 2))), s.cechy(cien=False):
        s.klin("Wzgórze", (0, wys / 2.0, -g / 4.0), (szer, wys, g / 2.0), kolor)
        s.klin("Wzgórze", (0, wys / 2.0, g / 4.0), (szer, wys, g / 2.0), cien(s, kolor, 0.93), rot=(0, 180, 0))
        s.kula("Wzgórze kopuła", (szer * rnd.uniform(-0.2, 0.2), wys * 0.55, 0), min(szer * 0.7, wys * 1.4), kolor)
    return wys + 0.2 * wys, szer / 2.0


def korona_daleka(s, rnd, pos, k, kolor, pien=None):
    """Daleka sylweta drzewa: pień i czapa (bez cienia). 2 części."""
    x, y, z = pos
    h = 26.0 * k
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), _kontra(rnd, 2, 6))), s.cechy(cien=False):
        s.blok("Sylweta pień", (0, h * 0.25, 0), (2.4 * k, h * 0.5, 2.4 * k), pien or cien(s, kolor, 0.7))
        s.blok("Sylweta korona", (0, h * 0.66, 0), (13.0 * k, h * 0.62, 12.0 * k), kolor, rot=(0, 45, _kontra(rnd, 3, 6)))
    return h, 6.5 * k


def drzewo_lasu(s, rnd, rodzina, pos, k, ry, f=1.0):
    """Drzewo ściany lasu z rodzin starego lasu (barwy koron z podbiomu „kapeluszowo”); f < 1 = ciemniejsze wnętrze
    lasu za polaną (polana jaśniejsza od ściany — postacie czytają się na ciemniejszym tle)."""
    kor = tuple(ros_lasu.odcien(s, c, f) for c in ros_lasu.KORONY["kapeluszowo"])
    if rodzina == "dab":
        return ros_lasu.dab(s, rnd, pos, k, ry, kor)
    if rodzina == "okraglak":
        return ros_lasu.okraglak(s, rnd, pos, k, ry, kor)
    if rodzina == "sosna":
        return ros_lasu.sosna(s, rnd, pos, k, ry, ciemna=True, f=f * rnd.uniform(0.94, 1.04))
    if rodzina == "smukly":
        return ros_lasu.smukly(s, rnd, pos, k, ry, kor)
    if rodzina == "swierk":
        return ros_lasu.swierk(s, rnd, pos, k, ry, f=f * rnd.uniform(0.94, 1.04))
    if rodzina == "jarzebina":
        return ros_lasu.jarzebina(s, rnd, pos, k, ry, kolory=kor[:2])
    if rodzina == "brzozka":
        return ros_lasu.brzozka(s, rnd, pos, k, ry)
    if rodzina == "grzyb":
        kap = rnd.choice(("czerwien", "czerwien", "czerwien", "dach_karczma"))
        return ros_lasu.grzyb(s, rnd, pos, k, ry, kapelusz=kap, kropki=True, trzon="biel")
    raise ValueError(rodzina)


# =========================================================================== BAGNO — pomost nad wodą
def pal(s, rnd, pos, h=2.6, r=0.42, kolor="bagno_kora", y0=-2.2):
    """Pal wbity w dno, wystaje do `h` nad pomostem (y0 = dno pod wodą). 1–2 części."""
    x, y, z = pos
    s.walec("Pal", (x, (y0 + y + h) / 2.0, z), r, (y + h) - y0, kolor, "Wood", os="y",
            rot=(rnd.uniform(-4, 4), 0, rnd.uniform(-4, 4)))
    with s.cechy(cien=False):
        s.walec("Pal czapa", (x, y + h + 0.05, z), r * 0.85, 0.12, "drewno_jasne", os="y")
    return h, r


def kepa(s, rnd, pos, r=3.0, wys=1.2, y_wody=-1.8):
    """Kępa trawy na wodzie: spłaszczony walec i jaśniejszy wierzch. 2 części."""
    x, y, z = pos
    with s.cechy(cien=False):
        s.walec("Kępa", (x, y_wody + wys / 2.0 - 0.3, z), r, wys + 0.6, "bagno_trawa", os="y")
        s.walec("Kępa wierzch", (x + rnd.uniform(-0.4, 0.4), y_wody + wys + 0.02, z + rnd.uniform(-0.4, 0.4)), r * 0.72, 0.16,
                "bagno_trawa_jasna", os="y")
    return y_wody + wys, r


def trzcina_zdzbla(s, rnd, pos, wys=5.0, szer=3.0, pelna=True):
    """Kępa trzciny z wąskich źdźbeł (poprawka po zrzutach ze Studio 17.11: płaskie snopy z map Bagna czytały się z kamer
    walki jak deski): 5 albo 3 źdźbła 0,32 × wys różnie pochylone, w trzech odcieniach, i 2 albo 1 pałka. 7 / 4 części."""
    x, y, z = pos
    n = 5 if pelna else 3
    kolory = ("bagno_trzcina", "trzcina", cien(s, "bagno_trzcina", 0.8), "trzcina", "bagno_trzcina")
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 180), 0)), s.cechy(cien=False):
        for i in range(n):
            a = 2 * math.pi * i / n + rnd.uniform(-0.4, 0.4)
            r = szer * rnd.uniform(0.12, 0.4)
            h = wys * rnd.uniform(0.7, 1.0)
            px, pz = r * math.cos(a), r * math.sin(a)
            with s.uklad(pos=(px, 0, pz), obrot=(rnd.uniform(-12, 12), rnd.uniform(0, 90), rnd.uniform(-12, 12))):
                s.blok("Trzcina źdźbło", (0, h / 2.0, 0), (0.34, h, 0.24), kolory[i])
                if i < (2 if pelna else 1):
                    s.blok("Pałka", (0, h + 0.5, 0), (0.6, 1.4, 0.6), "bagno_palka")
    return wys + 1.2, szer / 2.0


def chata_na_palach(s, rnd, pos, k=1.0, ry=0.0, h0=5.0, y_wody=-1.8, swiatlo=True):
    """Krzywa chatka na palach (front +Z ku placowi): sześć pali, pomost, przechylona ściana z desek, drzwi, świecące okno,
    strzecha z dwóch płyt, krzywy komin i drabina do wody. Wys. ok. (h0 + 11)·k. ok. 20 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y_wody, z), obrot=(0, ry, 0)):
        with s.uklad(skala=k):
            for px in (-3.6, 0.0, 3.6):
                for pz in (-3.0, 3.0):
                    s.walec("Chata pal", (px, h0 / 2.0 - 0.3, pz), 0.45, h0 + 0.6, "bagno_kora", "Wood", os="y",
                            rot=(rnd.uniform(-5, 5), 0, rnd.uniform(-5, 5)))
            s.blok("Chata pomost", (0, h0 + 0.2, 0.6), (9.6, 0.4, 8.4), "bagno_deska")
            with s.uklad(pos=(0, h0 + 0.4, -0.4), obrot=(0, rnd.uniform(-4, 4), zn * rnd.uniform(3, 6))):
                s.blok("Chata ściana", (0, 2.6, 0), (7.4, 5.2, 5.6), "drewno")
                with s.cechy(cien=False):
                    for i in range(3):
                        s.blok("Chata deska", (0, 0.9 + 1.7 * i, 2.82), (7.5, 0.18, 0.12), "drewno_ciemne")
                    s.blok("Chata drzwi", (-1.7, 1.75, 2.88), (1.8, 3.4, 0.2), "drewno_ciemne")
                    s.blok("Chata okno", (1.8, 3.0, 2.88), (1.5, 1.3, 0.2), "neon_okno" if swiatlo else "tusz",
                           "Neon" if swiatlo else "SmoothPlastic")
                s.dach_dwuspadowy("Chata strzecha", (0, 5.2, 0), 8.8, 3.3, 3.2, 0.6, "bagno_trzcina", okap=1.0)
                lamana(s, "Chata komin", [(2.2, 1.0, zn * 6), (1.8, 0.9, -zn * 12)], "kamien_cokol", start=(2.4, 6.2), z=-1.4)
            for i in range(5):
                s.blok("Chata drabina", (3.0, 0.9 + 1.0 * i, 4.6 + 0.12 * i), (1.8, 0.2, 0.3), "drewno_ciemne")
    return (h0 + 11.0) * k + y_wody, 6.0 * k


def wieza_obserwacyjna(s, rnd, pos, k=1.0, ry=0.0, y_wody=-1.8):
    """Krzywa wieża na palach z latarnią na szczycie (sylwetka nad mgłą). ok. 14 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y_wody, z), obrot=(0, ry, _kontra(rnd, 2, 4))), s.uklad(skala=k):
        for px, pz in ((-2.2, -2.2), (2.2, -2.2), (-2.2, 2.2), (2.2, 2.2)):
            s.belka("Wieża pal", (px * 1.3, -0.2, pz * 1.3), (px * 0.55, 24.0, pz * 0.55), 0.8, "bagno_kora", "Wood")
        for yy in (6.0, 14.0):
            s.blok("Wieża pomost", (0, yy, 0), (5.2 - 0.06 * yy, 0.4, 5.2 - 0.06 * yy), "bagno_deska_ciemna", rot=(0, 10, 0))
        s.blok("Wieża pomost", (0, 24.2, 0), (4.6, 0.5, 4.6), "bagno_deska", rot=(0, 25, 0))
        with s.cechy(cien=False):
            s.blok("Wieża latarnia", (0, 26.6, 0), (2.6, 3.8, 2.6), "neon_ognik", "Neon", rot=(0, 45, 0))
        s.ostroslup("Wieża dach", (0, 28.6, 0), 2.4, 2.4, 3.8, "bagno_deska_ciemna")
        s.blok("Wieża mech", (1.6, 20.0, -1.0), (0.8, 5.0, 1.3), "bagno_broda")
    return (32.0 * k) + y_wody, 4.0 * k


def latarnia_pal(s, rnd, pos, h=6.0, ry=0.0, y_wody=-1.8):
    """Pal z wysięgnikiem i wiszącą zieloną latarnią (Neon). 6 części."""
    x, y, z = pos
    zn = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y_wody, z), obrot=(0, ry, 0)):
        xe, ye, _ = lamana(s, "Latarnia słup", [(h * 0.6 - y_wody, 0.55, zn * 3), (h * 0.4, 0.45, -zn * 7)], "drewno_ciemne", "Wood",
                           start=(0.0, -0.3))
        s.belka("Latarnia ramię", (xe, ye - 0.4, 0), (xe + zn * 2.2, ye - 0.1, 0), 0.35, "drewno_ciemne", "Wood")
        s.blok("Latarnia łańcuch", (xe + zn * 2.0, ye - 1.0, 0), (0.22, 1.2, 0.22), "metal_ciemny")
        with s.cechy(cien=False):
            s.blok("Latarnia", (xe + zn * 2.0, ye - 2.3, 0), (1.2, 1.5, 1.2), "neon_ognik", "Neon", rot=(0, 45, 0))
        s.blok("Latarnia daszek", (xe + zn * 2.0, ye - 1.4, 0), (1.8, 0.4, 1.8), "bagno_deska_ciemna", rot=(0, 45, 0))
    return h, 2.6


def lodka(s, rnd, pos, ry=0.0, y_wody=-1.8):
    """Mała łódka przycumowana przy pomoście: dno, dwie burty, rufa, dziób-klin, ławka, wiosło. 7 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y_wody + 0.15, z), obrot=(rnd.uniform(-3, 3), ry, rnd.uniform(-4, 4))):
        s.blok("Łódka dno", (0, 0.1, 0), (2.6, 0.3, 7.0), "drewno_ciemne", "Wood")
        for zn in (-1, 1):
            s.blok("Łódka burta", (zn * 1.35, 0.6, 0), (0.3, 1.0, 7.2), "drewno", "Wood", rot=(0, 0, zn * 10))
        s.blok("Łódka rufa", (0, 0.6, -3.6), (2.8, 1.0, 0.3), "drewno", "Wood")
        s.klin("Łódka dziób", (0, 0.6, 4.3), (2.8, 1.1, 1.6), "drewno", "Wood", rot=(0, 180, 0))
        s.blok("Łódka ławka", (0, 0.75, 0.6), (2.6, 0.2, 0.8), "drewno_jasne")
        s.belka("Łódka wiosło", (-0.8, 0.9, -2.0), (1.6, 0.5, 3.4), 0.2, "drewno_jasne", "Wood")
    return 1.4, 3.6


def zatopiony_pien(s, rnd, pos, k=1.0, ry=0.0, y_wody=-1.8):
    """Zatopiony pień sterczący ukosem z wody, z brodą mchu. 3 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y_wody - 0.5, z), obrot=(0, ry, 0)):
        s.walec("Zatopiony pień", (0, 0, 0), 0.9 * k, 9.0 * k, "bagno_suche", "Wood", os="x", rot=(0, 0, rnd.uniform(22, 38)))
        s.blok("Zatopiony mech", (2.2 * k, 2.0 * k, 0), (0.6 * k, 2.6 * k, 1.2 * k), "bagno_broda", rot=(0, 0, 10))
        s.walec("Zatopiony słoje", (4.1 * k, 2.6 * k, 0), 0.75 * k, 0.15, "drewno_jasne", os="x", rot=(0, 0, 30))
    return 3.6 * k, 4.6 * k


def sylweta_cyprysu(s, rnd, pos, k, kolor):
    """Daleka sylweta cypryśnika w mgle: smukły pień i płaska szeroka korona. 3 części."""
    x, y, z = pos
    h = 22.0 * k
    with s.uklad(pos=(x, y, z), obrot=(0, rnd.uniform(0, 90), _kontra(rnd, 2, 6))), s.cechy(cien=False):
        s.blok("Sylweta pień", (0, h * 0.42, 0), (1.8 * k, h * 0.84, 1.8 * k), cien(s, kolor, 0.8))
        s.blok("Sylweta korona", (0, h * 0.86, 0), (15.0 * k, 2.4 * k, 12.0 * k), kolor, rot=(0, 30, _kontra(rnd, 2, 4)))
        s.blok("Sylweta broda", (3.0 * k, h * 0.68, 0), (0.8 * k, 4.6 * k, 1.6 * k), cien(s, kolor, 0.9))
    return h, 7.5 * k


def mgla_plat(s, rnd, pos, dl, szer, y=-1.2, alfa=0.72, kolor="bagno_mgla"):
    """Płat mgły nad wodą: dwa płaskie, półprzezroczyste krążki (bez cienia) — z kamer walki niska smuga przy wodzie. 2 części."""
    x, _, z = pos
    with s.cechy(cien=False):
        s.walec("Mgła nad wodą", (x, y, z), dl / 2.0, 0.3, kolor, os="y", alfa=alfa)
        s.walec("Mgła nad wodą", (x + rnd.uniform(-0.3, 0.3) * dl, y + 0.35, z + rnd.uniform(-0.3, 0.3) * szer), szer / 2.0, 0.3, kolor,
                os="y", alfa=min(0.9, alfa + 0.08))
    return y + 0.5, dl / 2.0


# =========================================================================== PRÓBA — plac ćwiczeń przy miasteczku
def manekin(s, rnd, pos, k=1.0, ry=0.0):
    """Manekin ćwiczebny (front +Z ku placowi): pal, poprzeczka-ramiona, worek-tułów ze słomy, głowa-garnek, pas i tarcza
    namalowana na worku. Wys. ok. 6,2·k. 9 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(rnd.uniform(-3, 3), ry, _kontra(rnd, 2, 6))), s.uklad(skala=k):
        s.blok("Manekin pal", (0, 2.2, 0), (0.6, 4.4, 0.6), "drewno_ciemne", "Wood")
        s.blok("Manekin podstawa", (0, 0.25, 0), (2.4, 0.5, 2.4), "drewno", "Wood", rot=(0, 45, 0))
        s.blok("Manekin worek", (0, 3.4, 0), (2.4, 2.8, 1.8), "arena_worek", "Fabric", rot=(0, 0, rnd.uniform(-5, 5)))
        s.blok("Manekin pas", (0, 2.6, 0), (2.5, 0.35, 1.9), "drewno_ciemne", rot=(0, 0, rnd.uniform(-6, 6)))
        s.belka("Manekin ramiona", (-2.4, 4.1, 0), (2.4, 4.4, 0), 0.45, "drewno", "Wood")
        with s.cechy(cien=False):
            s.walec("Manekin cel", (0, 3.5, 0.95), 0.6, 0.12, "czerwien", os="z")
            s.walec("Manekin cel środek", (0, 3.5, 1.02), 0.25, 0.1, "arena_kreda", os="z")
        s.walec("Manekin głowa", (0, 5.35, 0), 0.75, 1.2, "metal_ciemny", "Metal", os="y", rot=(rnd.uniform(-10, 10), 0, rnd.uniform(-12, 12)))
        s.blok("Manekin słoma", (0, 6.0, 0), (1.4, 0.3, 1.4), "arena_sloma", rot=(0, 30, 0))
    return 6.2 * k, 2.6 * k


def tarcza_lucznicza(s, rnd, pos, k=1.0, ry=0.0):
    """Tarcza łucznicza na sztaludze (front +Z): trzy nogi, słomiany krąg z pierścieniami i dwie wbite strzały. 10 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.uklad(skala=k):
        for px, pz, rx in ((-1.4, 0.4, -8), (1.4, 0.4, -8), (0.0, -1.6, 18)):
            s.blok("Tarcza noga", (px, 2.0, pz), (0.35, 4.2, 0.35), "drewno", "Wood", rot=(rx, 0, -px * 6))
        with s.uklad(pos=(0, 3.4, 0.3), obrot=(-12, 0, 0)):
            s.walec("Tarcza", (0, 0, 0), 1.9, 0.6, "arena_sloma", os="z")
            with s.cechy(cien=False):
                for i, (r, kol) in enumerate(((1.55, "biel"), (1.15, "czerwien"), (0.75, "biel"), (0.35, "zloto"))):
                    s.walec("Tarcza pierścień", (0, 0, 0.32 + 0.02 * i), r, 0.06, kol, os="z")
            for dx, dy in ((0.4, 0.2), (-0.7, -0.5)):
                s.belka("Strzała", (dx, dy, 0.3), (dx + 0.2, dy + 0.1, 2.2), 0.12, "drewno_jasne", "Wood")
    return 5.4 * k, 2.2 * k


def stojak_broni(s, rnd, pos, k=1.0, ry=0.0):
    """Stojak z drewnianymi mieczami i tarczą (front +Z). ok. 11 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, _kontra(rnd, 1, 4))), s.uklad(skala=k):
        for px in (-2.2, 2.2):
            s.blok("Stojak noga", (px, 1.6, 0), (0.4, 3.2, 1.2), "drewno_ciemne", "Wood")
        s.blok("Stojak belka", (0, 2.9, 0), (5.0, 0.35, 0.5), "drewno", "Wood")
        s.blok("Stojak dół", (0, 0.4, 0.2), (5.0, 0.3, 1.0), "drewno", "Wood")
        for i, px in enumerate((-1.5, -0.5, 0.5)):
            with s.uklad(pos=(px, 0.5, 0.3), obrot=(rnd.uniform(-10, -4), 0, rnd.uniform(-6, 6))):
                s.blok("Miecz drewniany", (0, 1.7, 0), (0.35, 3.0, 0.15), "drewno_jasne")
                s.blok("Miecz jelec", (0, 0.5, 0), (1.0, 0.25, 0.3), "drewno_ciemne")
        with s.uklad(pos=(1.6, 1.8, 0.45), obrot=(-10, 0, 8)):
            s.walec("Tarcza ćwiczebna", (0, 0, 0), 1.0, 0.25, "dach_twierdza", os="z")
            with s.cechy(cien=False):
                s.walec("Tarcza ćwiczebna guz", (0, 0, 0.15), 0.35, 0.12, "zloto", os="z")
    return 3.6 * k, 2.8 * k


def bela_siana(s, rnd, pos, k=1.0, ry=0.0, dwie=False):
    """Bela słomy (walec leżący) z jaśniejszym czołem; opcjonalnie druga na wierzchu. 3–5 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.walec("Bela", (0, 1.1 * k, 0), 1.1 * k, 2.6 * k, "arena_sloma", "Fabric", os="x")
        with s.cechy(cien=False):
            s.walec("Bela czoło", (1.32 * k, 1.1 * k, 0), 0.9 * k, 0.06, "arena_sloma_ciemna", os="x")
            s.blok("Bela sznurek", (0, 1.1 * k, 0), (0.15, 2.25 * k, 2.25 * k), "drewno_ciemne")
        if dwie:
            s.walec("Bela", (0.3 * k, 3.1 * k, 0.2 * k), 1.0 * k, 2.4 * k, "arena_sloma", "Fabric", os="z", rot=(0, rnd.uniform(-20, 20), 0))
            with s.cechy(cien=False):
                s.walec("Bela czoło", (0.3 * k, 3.1 * k, 1.42 * k), 0.82 * k, 0.06, "arena_sloma_ciemna", os="z")
    return (4.2 if dwie else 2.2) * k, 1.6 * k


def barierka(s, rnd, p1, p2, wys=0.95):
    """Niska barierka obręczy placu: dwa słupki i żerdź (≤ 1 wys.), krzywo jak w miasteczku. 3 części."""
    with s.cechy(cien=False):
        for (x, z) in (p1, p2):
            s.blok("Barierka słupek", (x, wys / 2.0, z), (0.5, wys, 0.5), "drewno", "Wood", rot=(0, rnd.uniform(0, 90), rnd.uniform(-5, 5)))
        s.belka("Barierka żerdź", (p1[0], wys * 0.72 + rnd.uniform(-0.08, 0.08), p1[1]), (p2[0], wys * 0.72 + rnd.uniform(-0.08, 0.08), p2[1]),
                0.32, "drewno_jasne", "Wood")
    return wys, 0.5


def trybuna(s, rnd, pos, ry=0.0, dl=14.0):
    """Mała trybuna z desek (front +Z ku placowi): trzy stopnie, poręcz, daszek z płótna w pasy na słupkach. ok. 14 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, _kontra(rnd, 0.5, 2))):
        for i in range(3):
            s.blok("Trybuna stopień", (0, 0.6 + 1.2 * i, 1.6 - 1.5 * i), (dl, 1.2 + 2.4 * i, 1.6), "drewno" if i % 2 else "drewno_jasne",
                   "WoodPlanks")
        for px in (-dl / 2.0 + 0.4, dl / 2.0 - 0.4):
            s.blok("Trybuna słup", (px, 4.6, -2.0), (0.5, 9.2, 0.5), "drewno_ciemne")
            s.blok("Trybuna słup", (px, 3.4, 2.4), (0.5, 6.8, 0.5), "drewno_ciemne")
        for i in range(4):
            kol = "dach_karczma" if i % 2 == 0 else "biel"
            s.blok("Trybuna daszek", (-dl / 2.0 + dl / 8.0 + i * dl / 4.0, 8.0, 0.2), (dl / 4.0 + 0.05, 0.3, 5.6), kol, "Fabric",
                   rot=(-20, 0, 0))
        s.blok("Trybuna rant", (0, 6.9, 2.75), (dl + 0.4, 0.5, 0.3), "tusz")
    return 9.0, dl / 2.0


def namiot(s, rnd, pos, ry=0.0, kolory=("dach_karczma", "biel")):
    """Namiot w pasy: cztery kliny ostrosłupa naprzemiennie w dwóch kolorach, maszt z chorągiewką, wejście. 8 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.walec("Namiot ściana", (0, 1.6, 0), 4.4, 3.2, kolory[1], "Fabric", os="y")
        a, h = 4.8, 4.6
        yy = 3.2 + h / 2.0
        for i, (px, pz, rr) in enumerate(((-a / 2.0, a / 2.0, 0), (a / 2.0, a / 2.0, 90), (a / 2.0, -a / 2.0, 180), (-a / 2.0, -a / 2.0, 270))):
            s.naroznik("Namiot dach", (px, yy, pz), (a, h, a), kolory[i % 2], "Fabric", rot=(0, rr, 0))
        with s.cechy(cien=False):
            s.blok("Namiot wejście", (0, 1.4, 4.35), (2.2, 2.8, 0.2), "tusz")
        zestaw.choragiewka_duetu(s, (0, 3.2 + h - 0.2, 0), kto=rnd.choice(("rycerz", "kot")), ry=rnd.uniform(0, 360))
    return 3.2 + h + 4.0, 4.8


def domek_tla(s, rnd, pos, ry=0.0, szer=10.0, gl=8.0, wys=9.0, dach="dach_dom_ceglasty", sciana="tynk_krem", okna=2, komin=True):
    """Krzywy domek tła (front +Z ku placowi): cokół, ściana, narożniki tuszem, okna (jedno świecące), drzwi, dach-czapa
    w kontrze z kalenicą, komin łamany. ok. 16–20 części."""
    x, y, z = pos
    sg = rnd.choice((-1, 1))
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)):
        s.blok("Dom cokół", (0, 0.5, 0), (szer + 0.6, 1.0, gl + 0.6), "kamien_cokol", "Cobblestone")
        with s.uklad(obrot=(0, 0, sg * rnd.uniform(1.5, 3.5))):
            s.blok("Dom ściana", (0, wys / 2.0, 0), (szer, wys, gl), sciana)
            with s.cechy(cien=False):
                for sx in (-1, 1):
                    s.blok("Dom narożnik", (sx * (szer / 2.0 - 0.2), wys / 2.0, gl / 2.0 - 0.2), (0.9, wys, 0.9), "tusz")
                s.blok("Dom pas cienia", (0, wys - 0.6, gl / 2.0 + 0.05), (szer - 1.2, 1.0, 0.2), cien(s, sciana))
                s.blok("Dom drzwi", (sg * szer * 0.25, 2.0, gl / 2.0 + 0.08), (2.2, 4.0, 0.2), "drewno_ciemne")
                for i in range(okna):
                    ox = -sg * szer * 0.22 + (i - (okna - 1) / 2.0) * 3.0 * (1 if okna > 1 else 0)
                    oy = wys * 0.58 + (0.8 if i % 2 else 0)
                    swieci = i == 0 and rnd.random() < 0.6
                    s.blok("Dom okno", (ox, oy, gl / 2.0 + 0.1), (1.8, 2.0, 0.2), "neon_okno" if swieci else "woda_gleboka",
                           "Neon" if swieci else "SmoothPlastic", rot=(0, 0, rnd.uniform(-6, 6)))
            with s.uklad(pos=(0, wys, 0), obrot=(0, rnd.uniform(-4, 4), -sg * rnd.uniform(3, 6))):
                zestaw.dach_czapa(s, szer, gl, wys * 0.62, dach, okap=1.4, okap_bok=1.0, szczyt=sciana)
                if komin:
                    lamana(s, "Dom komin", [(2.4, 1.4, sg * 7), (1.8, 1.2, -sg * 11)], "kamien_cokol", start=(-sg * szer * 0.28, wys * 0.3),
                           z=-gl * 0.18)
    return wys * 1.62 + (3.0 if komin else 0.0), max(szer, gl) / 2.0 + 1.5


def mur_odcinek(s, rnd, p1, p2, wys=9.0, kolor="kamien_cieply"):
    """Odcinek muru miejskiego od p1 do p2 (x, z) z blankami. 2 + n części."""
    x1, z1 = p1
    x2, z2 = p2
    dl = math.hypot(x2 - x1, z2 - z1)
    ry = math.degrees(math.atan2(x2 - x1, z2 - z1))
    with s.uklad(pos=((x1 + x2) / 2.0, 0, (z1 + z2) / 2.0), obrot=(0, ry, _kontra(rnd, 0.5, 1.5))):
        s.blok("Mur", (0, wys / 2.0, 0), (3.0, wys, dl + 0.4), kolor, "Cobblestone")
        with s.cechy(cien=False):
            s.blok("Mur rant", (0, wys + 0.15, 0), (3.4, 0.3, dl + 0.6), "tusz")
        n = max(1, int(dl / 3.2))
        for i in range(n):
            if i % 2 == 0:
                s.blok("Mur blanka", (0, wys + 1.1, -dl / 2.0 + (i + 0.5) * dl / n), (3.0, 1.8, dl / n * 0.9), cien(s, kolor, 0.9), "Cobblestone")
    return wys + 2.0, 1.7


def wieza_miejska(s, rnd, pos, ry=0.0, wys=18.0, dach="dach_twierdza", kolor="kamien_cieply"):
    """Okrągła wieża muru z dachem-stożkiem z klinów i chorągiewką. 8–10 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, _kontra(rnd, 1, 2.5))):
        s.walec("Wieża", (0, wys / 2.0, 0), 3.6, wys, kolor, "Cobblestone", os="y")
        s.walec("Wieża gzyms", (0, wys + 0.3, 0), 4.0, 0.6, cien(s, kolor, 0.85), os="y")
        with s.cechy(cien=False):
            s.blok("Wieża okno", (0, wys * 0.7, 3.55), (1.0, 1.8, 0.2), "neon_okno", "Neon")
        s.ostroslup("Wieża dach", (0, wys + 0.6, 0), 4.3, 4.3, 7.0, dach)
        zestaw.choragiewka_duetu(s, (0, wys + 7.4, 0), kto="rycerz", ry=rnd.uniform(0, 360))
    return wys + 11.0, 4.3


def zamek_daleki(s, rnd, pos, k=1.0, ry=0.0, kolor="arena_mgla_miasto", dach="arena_dach_daleki"):
    """Daleka sylweta twierdzy na wzgórzu: blok murów, trzy wieże z dachami, środkowa wyższa. ok. 12 części."""
    x, y, z = pos
    with s.uklad(pos=(x, y, z), obrot=(0, ry, 0)), s.uklad(skala=k), s.cechy(cien=False):
        s.blok("Zamek mur", (0, 6.0, 0), (40.0, 12.0, 10.0), kolor)
        for px, h in ((-18.0, 22.0), (0.0, 32.0), (18.0, 24.0)):
            s.blok("Zamek wieża", (px, h / 2.0, 0), (7.0, h, 7.0), cien(s, kolor, 0.94))
            s.ostroslup("Zamek dach", (px, h, 0), 4.2, 4.2, 8.0, dach)
        s.blok("Zamek brama", (6.0, 3.4, 5.1), (5.0, 6.8, 0.2), cien(s, kolor, 0.8))
    return 40.0 * k, 22.0 * k


def dach_daleki(s, rnd, pos, k=1.0, ry=0.0, kolor="arena_dach_daleki", sciana="arena_mgla_miasto"):
    """Daleki domek: blok ściany i dach z dwóch klinów (sylweta miasteczka za murem). 3 części."""
    x, y, z = pos
    w, g, h = 9.0 * k, 7.0 * k, rnd.uniform(7.0, 11.0) * k
    with s.uklad(pos=(x, y, z), obrot=(0, ry, _kontra(rnd, 1, 4))), s.cechy(cien=False):
        s.blok("Daleki dom", (0, h / 2.0, 0), (w, h, g), sciana)
        s.klin("Daleki dach", (0, h + 2.4 * k, -g / 4.0 - 0.3), (w + 1.2, 4.8 * k, g / 2.0 + 0.6), kolor)
        s.klin("Daleki dach", (0, h + 2.4 * k, g / 4.0 + 0.3), (w + 1.2, 4.8 * k, g / 2.0 + 0.6), cien(s, kolor, 0.88), rot=(0, 180, 0))
    return h + 4.8 * k, max(w, g) / 2.0


def drzewo_miasta(s, rnd, pos, k=1.0, ry=0.0):
    """Drzewo przy miasteczku (rodzina „okrąglak” starego lasu w barwach łąki). 6 części."""
    return ros_lasu.okraglak(s, rnd, pos, k, ry, ros_lasu.KORONY["laka"])


def girlanda(s, rnd, p1, p2, y1, y2, n=7, kolory=("czerwien", "zloto", "dach_twierdza", "biel")):
    """Sznur z chorągiewkami między dwoma masztami (zwis łukiem). 1 + n części."""
    x1, z1 = p1
    x2, z2 = p2
    with s.cechy(cien=False):
        s.belka("Girlanda sznur", (x1, y1, z1), ((x1 + x2) / 2.0, min(y1, y2) - 1.4, (z1 + z2) / 2.0), 0.12, "tusz", "SmoothPlastic")
        s.belka("Girlanda sznur", ((x1 + x2) / 2.0, min(y1, y2) - 1.4, (z1 + z2) / 2.0), (x2, y2, z2), 0.12, "tusz", "SmoothPlastic")
        ry = math.degrees(math.atan2(x2 - x1, z2 - z1))
        for i in range(n):
            t = (i + 1) / float(n + 1)
            px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t
            py = y1 + (y2 - y1) * t - 1.4 * (1 - (2 * t - 1) ** 2) - 0.7
            s.klin("Chorągiewka", (px, py, pz), (0.15, 1.3, 1.2), kolory[i % len(kolory)], "Fabric", rot=(180, ry + 90, 0))
    return max(y1, y2), 0.5
