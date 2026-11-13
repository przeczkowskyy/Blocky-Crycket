# -*- coding: utf-8 -*-
"""Sklep magiczny (PROJEKT.md, karta 5.3) — smukła, łamana wieżyczka w wielkim kapeluszu czarodzieja.

Sylwetka: prosty parter 14 × 14, dwa piętra przechylone w lewo i skręcone na przemian (łamany trzon), na górze
dach-kapelusz: szerokie rondo Ø 22 i stożek z trzech ostrosłupów zginających się do tyłu i skręcających (czubek
złamany o 26°) ze złotą gwiazdką na sprężynce. Szyld: krzywy kostur z lewitującym kryształem podpiera lewy narożnik
pochylonego piętra. Żart: z okna piętra wystaje pomarańczowy koci ogon zakręcony w znak zapytania. Echo: rama okna
na górnym piętrze oderwała się od ściany i wisi w powietrzu.

Układ lokalny: środek działki 24 × 24 na ziemi = (0, 0, 0), front z wejściem ku +Z (lico frontu parteru z = +6).
Status: propozycja (noc 13.11.2026), nie kanon.

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/sklep_magiczny.py --wyj <folder> --szer 1000
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "SklepMagiczny"
OBRYS = (24, 24)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 42                    # wierzch gwiazdki na czubku kapelusza
BUDZET = 290
INTERAKCJA = (-3.0, 16.0)        # przed drzwiami, 4 study przed krawędzią działki
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

SCIANA, DACH = "tynk_lawenda", "dach_sklep"
SZKLO = "neon_magia"             # okna świecące (Neon)
CIEMNE = "dach_sklep"            # ciemna szyba bez Neonu (tył i boki)


def buduj(s, rnd):
    W0, H0 = 14.0, 12.0          # parter 14 × 14, wys. 12, środek (0; −1), front z = +6
    with s.uklad(pos=(0, 0, -1.0)):
        _parter(s, W0, H0)
        # piętro 1: 15,5 × 15,5 × 7, nawis z frontu średnio 1,5 (lewy narożnik 2,3, prawy 0,7), ry +6°, rz +5°
        with s.uklad(pos=(-0.5, H0 - 0.78, 0.79), obrot=(0, 6, 5)):
            _pietro1(s)
            # piętro 2: 12 × 12 × 6, względem piętra 1 ry −5°, rz +4° (łamany trzon)
            with s.uklad(pos=(1.3, 6.9, 0.5), obrot=(0, -5, 4)):
                _pietro2(s)
                # kapelusz: rondo w kontrze (rz −5° względem piętra 2 → +4° bezwzględnie), skręt +8°
                with s.uklad(pos=(1.5, 5.35, 0.8), obrot=(0, 8, -5)):
                    _kapelusz(s)
        _kostur(s, rnd)
    _rekwizyty(s)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- parter (prosty, z kolizją)
def _parter(s, W0, H0):
    h = W0 / 2.0
    s.blok("Cokół", (0, 0.6, 0), (W0 + 0.8, 1.2, W0 + 0.8), "kamien_cokol", "Cobblestone")
    with s.cechy(kolizja=False):
        s.blok("Cokół rant", (0, 1.25, 0), (W0 + 1.0, 0.4, W0 + 1.0), "tusz")
    s.blok("Parter", (0, (H0 + 0.1) / 2.0, 0), (W0, H0 - 0.1, W0), SCIANA)
    with s.cechy(kolizja=False):
        for sx in (-1, 1):
            for sz in (-1, 1):                                 # od 1,55 (nad rantem cokołu) do 12,1
                s.blok("Narożnik", (sx * (h - 0.25), 6.825, sz * (h - 0.25)), (1.3, 10.55, 1.3), "tusz")
        # pas cienia pod nawisem piętra — równoległy do przechylonego piętra
        with s.uklad(pos=(-0.5, H0 - 0.78, h + 0.05), obrot=(0, 0, 5)):
            s.blok("Pas cienia", (0.4, -0.7, 0), (W0 - 2.0, 1.4, 0.2), cien(s, SCIANA))
        # kroksztyny pod nawisem (kliny wysoką krawędzią przy ścianie)
        for x, y in ((3.2, H0 - 0.95), (6.0, H0 - 0.7)):
            s.klin("Kroksztyn", (x, y - 0.8, h + 0.75), (0.8, 1.6, 1.5), "drewno_ciemne", rot=(0, 180, 180))
    # drzwi łukowe 8 × 10 przesunięte w lewo (−2,5 = 18 % fasady), złota gwiazda na skrzydle
    zestaw.drzwi(s, (-2.5, 0, h + 0.25), 8.0, 10.0, "drewno_ciemne", luk=True, prog="kamien_cokol")
    with s.cechy(kolizja=False, cien=False):
        for k in (0, 45):
            s.blok("Drzwi gwiazda", (-2.5, 7.4, h + 0.25 + 0.6), (1.7, 1.7, 0.3), "zloto", rot=(0, 0, k))
    # front: małe okrągłe okno po prawej od drzwi
    zestaw.okno(s, (4.3, 7.4, h), 2.4, ksztalt="okragle", przechyl=0, swiatlo=SZKLO)
    # lewy bok: duże okno świecące; prawy bok: wypadnięty klocek; tył: ciemne okno i łata
    zestaw.okno(s, (-h, 6.4, -1.2), 3.0, 4.0, przechyl=-6, swiatlo=SZKLO, ry=-90)
    zestaw.wypadniety_klocek(s, (h, 3.0, 1.5), (h + 1.9, 0, 3.4), SCIANA, ry=90, obrot_klocka=24)
    zestaw.okno(s, (h, 7.6, 2.9), 2.6, 3.4, przechyl=7, swiatlo=CIEMNE, ry=90)
    _schowek(s, h)
    zestaw.okno(s, (1.8, 6.2, -h), 3.0, 4.0, przechyl=5, swiatlo=CIEMNE, ry=180)
    zestaw.lata(s, (-3.6, 4.4, -h), 2.6, 2.2, "pomarancz", ry=180, przechyl=-9)
    zestaw.wypadniety_klocek(s, (4.6, 2.9, -h), (2.4, 0, -h - 1.7), SCIANA, ry=180, obrot_klocka=-18)


# --------------------------------------------------------------------------- piętro 1 (rz +5°, ry +6°)
def _pietro1(s):
    W, Hp = 15.5, 7.0
    h = W / 2.0
    s.blok("Piętro 1", (0, Hp / 2.0, 0), (W, Hp, W), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Belka stropowa", (0, 0.45, 0), (W + 0.6, 1.1, W + 0.6), "tusz")
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik piętra", (sx * (h - 0.15), 4.1, sz * (h - 0.15)), (1.2, 6.2, 1.2), "tusz")
        s.blok("Gzyms piętra", (0, 7.2, 0), (W + 0.8, 0.6, W + 0.8), DACH)
    # front: okno z kocim ogonem (z okiennicą zwisającą w lewo) i małe okrągłe okno
    zestaw.okno(s, (2.6, 3.5, h), 3.0, 3.6, przechyl=6, swiatlo=SZKLO, okiennica=DACH, strona_okiennicy=-1)
    zestaw.okno(s, (-4.2, 4.3, h), 2.6, ksztalt="okragle", przechyl=0, swiatlo=SZKLO)
    _koci_ogon(s, h)
    # boki i tył: ciemne szyby
    zestaw.okno(s, (-h, 3.9, 1.0), 2.8, 3.4, przechyl=5, swiatlo=CIEMNE, ry=-90, tanie=True)
    _wykusz(s, h)
    zestaw.okno(s, (-1.5, 3.8, -h), 3.0, 3.6, przechyl=-7, swiatlo=CIEMNE, ry=180, okiennica=DACH, strona_okiennicy=1)


def _wykusz(s, h):
    """Wykusz na prawym boku piętra 1: skrzynka 2,6 × 4,4 × 5,4 na wsporniku-klinie, daszek z klina w kolorze dachu
    z rantem tusz, słupki tusz, okno świecące (tanie). 8 części."""
    x = h + 1.2
    with s.cechy(kolizja=False):
        s.blok("Wykusz", (x, 3.8, -1.0), (2.6, 4.4, 5.4), SCIANA)
        s.klin("Wykusz wspornik", (x - 0.1, 0.7, -1.0), (5.0, 1.8, 2.4), cien(s, SCIANA), rot=(0, -90, 180))
        s.blok("Wykusz rant", (x + 0.2, 6.15, -1.0), (3.4, 0.4, 6.2), "tusz")
        s.klin("Wykusz daszek", (x + 0.25, 7.15, -1.0), (6.4, 1.6, 3.5), DACH, rot=(0, -90, 0))
        for z in (-3.35, 1.35):
            s.blok("Wykusz słupek", (x + 0.95, 3.8, z), (0.9, 4.4, 0.9), "tusz")
    zestaw.okno(s, (h + 2.5, 3.9, -1.0), 2.4, 2.8, przechyl=-5, swiatlo=SZKLO, ry=90, tanie=True)


def _koci_ogon(s, h):
    """Pomarańczowy koci ogon z 5 segmentów (razem 8,1) wychodzący z okna i zakręcony w znak zapytania; podkładka tusz.
    10 części."""
    seg = [(1.8, 1.0, -70), (1.9, 0.95, 60), (1.6, 0.9, 40), (1.4, 0.85, 60), (1.3, 0.8, 55)]
    with s.cechy(kolizja=False):
        podkl = [(dl + (0.3 if i == len(seg) - 1 else 0.0), g + 0.5, k) for i, (dl, g, k) in enumerate(seg)]
        zestaw.lamana(s, "Ogon podkładka", podkl, "tusz", start=(3.7, 2.2), z=h + 0.5, glebokosc=0.8)
        kol = ["pomarancz"] * 4 + [cien(s, "pomarancz", 0.8)]
        zestaw.lamana(s, "Koci ogon", seg, kol, start=(3.7, 2.2), z=h + 0.85, glebokosc=1.0)


# --------------------------------------------------------------------------- piętro 2 (łamany trzon)
def _pietro2(s):
    W, Hp = 12.0, 6.0
    h = W / 2.0
    s.blok("Piętro 2", (0, Hp / 2.0, 0), (W, Hp, W), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Belka piętra 2", (0, 0.95, 0), (W + 0.6, 0.6, W + 0.6), "tusz")
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik wieży", (sx * (h - 0.15), 3.6, sz * (h - 0.15)), (1.1, 4.8, 1.1), "tusz")
    # echo: rama okna oderwana 1,5 od ściany i obrócona o 12° — szyba i parapet zostały na ścianie
    x0, y0 = -1.3, 3.4
    with s.cechy(kolizja=False):
        with s.cechy(cien=False):
            s.blok("Okno szyba", (x0, y0, h + 0.2), (2.6, 3.0, 0.4), SZKLO, "Neon")
        s.blok("Okno parapet", (x0, y0 - 2.1, h + 0.5), (4.2, 0.55, 1.2), "drewno_jasne")
        with s.uklad(pos=(x0 + 0.5, y0 + 0.5, h + 1.9), obrot=(0, 10, 12)):
            s.ramka("Okno latające", (0, 0, 0), 2.6, 3.0, "tusz", grub=0.6, gleb=0.4)
    zestaw.lata(s, (3.4, 3.3, h), 2.4, 2.0, DACH, przechyl=10)
    zestaw.okno(s, (-h, 3.4, 0.5), 2.2, ksztalt="okragle", przechyl=0, swiatlo=CIEMNE, ry=-90, tanie=True)
    zestaw.okno(s, (h, 3.2, -0.8), 2.2, ksztalt="okragle", przechyl=0, swiatlo=CIEMNE, ry=90, tanie=True)


# --------------------------------------------------------------------------- kapelusz
def _kapelusz(s):
    """Rondo Ø 22 z podkładką, stożek z 3 ostrosłupów (13 → 8,2 → 5,2; wys. 9 → 8 → 7; każdy z 45 % wysokości
    poprzedniego, zgięty o 13° do tyłu i skręcony o 20°), opaska ze złotą klamrą, gwiazdka na sprężynce."""
    with s.cechy(kolizja=False):
        s.walec("Rondo podkładka", (0, 0.2, 0), 11.4, 0.4, "tusz", os="y")
        s.walec("Rondo", (0, 0.7, 0), 11.0, 0.8, DACH, os="y")
        y0 = 1.0
        s.ostroslup("Kapelusz stożek", (0, y0, 0), 6.5, 6.5, 9.0, DACH)
        s.blok("Opaska", (0, y0 + 0.75, 0), (13.3, 1.5, 13.3), "zloto")
        with s.cechy(cien=False):
            s.blok("Klamra", (0, y0 + 0.75, 6.8), (3.0, 3.0, 0.3), "tusz")
            s.blok("Klamra", (0, y0 + 0.75, 6.95), (1.9, 1.9, 0.3), "zloto")
            s.blok("Klamra", (0, y0 + 0.75, 7.1), (0.9, 0.9, 0.3), "tusz")
        zestaw.choragiewka_duetu(s, (7.6, 1.1, -5.8), "kot", ry=-30, przechyl=-12)
        with s.uklad(pos=(0, y0 + 4.05, 0), obrot=(-13, 0, 0)), s.uklad(obrot=(0, 20, 0)):
            s.ostroslup("Kapelusz stożek", (0, 0, 0), 3.8, 3.8, 8.0, cien(s, DACH, 0.9))
            with s.uklad(pos=(0, 3.6, 0), obrot=(-13, 0, 0)), s.uklad(obrot=(0, 20, 0)):
                s.ostroslup("Kapelusz czubek", (0, 0, 0), 2.4, 2.4, 7.0, DACH)
                # sprężynka z 3 zygzaków i gwiazdka (twarzą do frontu)
                with s.uklad(obrot=(0, -48, 0)):
                    xe, ye, _ = zestaw.lamana(s, "Sprężynka", [(0.8, 0.4, 35), (0.8, 0.4, -70), (0.8, 0.4, 70)], "tusz",
                                              start=(0, 6.0))
                    with s.uklad(pos=(xe, ye + 1.1, 0)), s.cechy(cien=False):
                        for k in (0, 45):
                            s.blok("Gwiazdka", (0, 0, 0.1), (2.3, 2.3, 0.5), "zloto", rot=(0, 0, k))
                            s.blok("Gwiazdka obrys", (0, 0, -0.25), (2.9, 2.9, 0.3), "tusz", rot=(0, 0, k))


# --------------------------------------------------------------------------- szyld: kostur z kryształem
def _kostur(s, rnd):
    """Krzywy kostur 16 oparty pod 11° o lewy przedni narożnik piętra (dotyka go na wys. ok. 11), głowica odgięta
    od ściany; kryształ (2 ostrosłupy, górny Neon) unosi się 1 nad końcem, wokół złote iskry. Układ parteru."""
    # lokalne −X kostura = ku narożnikowi (+X, −Z budynku); lamana zgina się w tej samej płaszczyźnie
    with s.uklad(pos=(-9.7, 0, 11.5), obrot=(0, -135, 0)), s.uklad(obrot=(0, 0, 11)), s.cechy(kolizja=False):
        xe, ye, kat = zestaw.lamana(s, "Kostur", [(6.0, 0.9, 0), (5.5, 0.85, 4), (4.5, 0.8, -30)], "drewno", "Wood",
                                    start=(0, -0.3))
        with s.uklad(pos=(xe, ye, 0), obrot=(0, 0, kat)):
            s.blok("Kostur okucie", (0, -0.6, 0), (1.3, 0.6, 1.3), "zloto")
            for zn in (-1, 1):
                s.blok("Kostur pazur", (zn * 0.55, 0.35, 0), (0.4, 1.3, 0.5), "zloto", rot=(0, 0, -zn * 25))
            with s.uklad(pos=(0, 3.2, 0), obrot=(0, 20, -kat - 5)):
                with s.uklad(obrot=(180, 0, 0)):
                    s.ostroslup("Kryształ dół", (0, 0.05, 0), 1.7, 1.7, 2.2, DACH)
                with s.cechy(cien=False):
                    s.ostroslup("Kryształ", (0, 0, 0), 1.7, 1.7, 3.6, SZKLO, "Neon")
            with s.cechy(cien=False):
                for x, y, z in ((-2.4, 3.8, 0.4), (2.3, 1.8, 0.3), (1.6, 5.6, -0.6)):
                    s.blok("Iskra", (x, y, z), (0.6, 0.6, 0.6), "zloto", rot=(45, 0, 45))
    zestaw.kamien(s, (-9.7, 0, 11.5), rnd, rozmiar=2.2, dwa=False, kolizja=False)


# --------------------------------------------------------------------------- schowek na miotły (prawy bok)
def _schowek(s, h):
    """Drewniana przybudówka 3,4 × 6 × 6 przy prawym boku parteru, daszek-klin w kolorze dachu, oparta miotła.
    Łamie pudełkowy parter w sylwetce (forma średnia). 12 części."""
    x0, x1, z0, z1, H = h - 0.1, h + 3.4, -6.0, 0.0, 6.0
    xc, zc = (x0 + x1) / 2.0, (z0 + z1) / 2.0
    s.blok("Schowek", (xc, H / 2.0 + 0.05, zc), (x1 - x0, H - 0.1, z1 - z0), "drewno", "WoodPlanks")
    with s.cechy(kolizja=False):
        s.blok("Schowek rant", (xc + 0.3, H + 0.1, zc), (x1 - x0 + 1.2, 0.4, z1 - z0 + 1.0), "tusz")
        s.klin("Schowek daszek", (xc + 0.4, H + 1.35, zc), (z1 - z0 + 0.8, 2.1, x1 - x0 + 1.4), DACH, rot=(0, -90, 0))
        for z in (z0, z1):
            s.blok("Schowek słupek", (x1 - 0.1, H / 2.0 + 0.1, z), (0.9, H - 0.4, 0.9), "drewno_jasne")
    zestaw.lata(s, (x1, 3.4, zc - 0.6), 2.2, 1.9, "pomarancz", ry=90, przechyl=7)
    # miotła oparta o przedni narożnik schowka: kij łamany, wiązanie tusz, miotła złota (słoma)
    with s.uklad(pos=(x1 + 0.6, 0, z1 + 1.3), obrot=(0, 30, 0)), s.uklad(obrot=(-10, 0, 9)), s.cechy(kolizja=False):
        s.klin("Miotła", (0, 1.2, 0), (1.8, 2.4, 1.0), "zloto", rot=(0, 0, 180))
        s.blok("Miotła wiązanie", (0, 2.5, 0), (1.0, 0.5, 0.9), "tusz")
        zestaw.lamana(s, "Miotła kij", [(3.0, 0.45, 0), (2.6, 0.4, -6)], "drewno", "Wood", start=(0, 2.6))


# --------------------------------------------------------------------------- rekwizyty przy wejściu
def _rekwizyty(s):
    zestaw.kwiaty(s, (4.9, 0, 7.7), ry=-4, kolory=(DACH, "zloto"))
    zestaw.skrzynia(s, (9.2, 0, 7.2), ry=-22, dl=3.6, a=3.2, przechyl=8, kolor="drewno")
    with s.cechy(kolizja=False):                               # stos ksiąg z zaklęciami: duża–średnia–mała
        for i, (sx, sz, k, kol) in enumerate(((2.8, 2.0, 12, DACH), (2.4, 1.8, -10, "pomarancz"), (2.0, 1.5, 25, "drewno_jasne"))):
            s.blok("Księga", (9.9 + 0.15 * i, 0.4 + 0.8 * i, 10.6 - 0.1 * i), (sx, 0.8, sz), kol, rot=(0, k, 4 * (i - 1)))
        s.blok("Księga", (8.8, 3.6, 7.0), (2.0, 0.7, 1.5), "zloto", rot=(6, 30, 8))
