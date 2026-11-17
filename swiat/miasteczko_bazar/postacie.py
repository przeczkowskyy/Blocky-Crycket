# -*- coding: utf-8 -*-
"""Sprzedawcy i pety bazaru — proste postacie z klocków w stylu Krzywego Miasteczka (D-041, D-084).

Każda postać to Model w Studio: grupa `<Budynek>/<Postac>` z niewidzialną częścią „Korzeń” (stopy, oś obrotu; pierwsza
część grupy, więc tools/studio_buduj.py robi z niej Model) i nazwane podgrupy:
    Glowa (głowa i twarz), Tulow (tułów, pas, fartuch), Rece, Nogi, Kapelusz (nakrycie głowy), Rekwizyt (to, co trzyma).
Kolizję mają Tulow i Nogi (gracz nie przechodzi przez sprzedawcę) oraz Glowa i Kapelusz (kamera gracza nie wchodzi w
głowę sprzedawcy — Poppercam widzi tylko części z kolizją; 17.11.2026); ręce i rekwizyty bez kolizji.

Układ postaci: stopy w (0, 0, 0), twarz ku +Z; wysokość ok. 8 przed skalą (domyślnie ×0,85 → ok. 6,8, gracz ma ok. 5,3 —
głowa większa od nóg, przerysowanie jak w przykazaniach stylu). Kolory tylko z palety miasteczka (skóra = tynk_brzoskwinia).
Postacie są nasze: żadnych cudzych bohaterów ani sprzedawców z gry-inspiracji.
"""
import os
import sys

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

SKORA = "tynk_brzoskwinia"
SKALA = 0.85
PODGRUPY = ("Glowa", "Tulow", "Rece", "Nogi")                 # obowiązkowe (sprawdz.py)


class _R:
    """Pomocnik: dodaje części do podgrupy postaci i pilnuje cech (kolizja tylko tułów i nogi)."""

    def __init__(self, s, g):
        self.s, self.g = s, g

    def __call__(self, pod, kolizja=False):
        # głowa i nakrycie głowy też z kolizją (17.11.2026): kamera gracza (Poppercam) zatrzymuje się tylko na częściach
        # z kolizją — bez tego przy obróconej kamerze przy ladzie stawała W głowie maga (sprzedawca stoi przy półce)
        if pod in ("Glowa", "Kapelusz"):
            kolizja = True
        return _Pod(self.s, self.g + "/" + pod, kolizja)


class _Pod:
    def __init__(self, s, g, kolizja):
        self.s, self.g, self.k = s, g, kolizja

    def __enter__(self):
        self._a = self.s.grupa(self.g)
        self._b = self.s.cechy(kolizja=self.k)
        self._a.__enter__()
        self._b.__enter__()
        return self.s

    def __exit__(self, *e):
        self._b.__exit__(*e)
        self._a.__exit__(*e)


# --------------------------------------------------------------------------- części wspólne
def _nogi(s, R, spodnie, buty, siedzi=False, szer=1.1):
    with R("Nogi", kolizja=True):
        for sx in (-1, 1):
            x = sx * 0.75
            if siedzi:
                s.blok("Udo", (x, 2.25, 0.85), (szer + 0.05, 1.1, 2.1), spodnie)
                s.blok("Łydka", (x, 1.25, 1.75), (szer, 2.1, 1.1), spodnie)
                s.blok("But", (x, 0.4, 2.05), (1.25, 0.8, 1.8), buty)
            else:
                s.blok("Noga", (x, 1.7, 0), (szer, 1.9, 1.15), spodnie)
                s.blok("But", (x, 0.4, 0.2), (1.3, 0.8, 1.85), buty)


def _tulow(s, R, kolor, yb=2.6, szer=3.0, gl=1.9, pas="tusz"):
    with R("Tulow", kolizja=True):
        s.blok("Tułów", (0, yb + 1.4, 0), (szer, 2.8, gl), kolor)
        if pas:
            s.blok("Pas", (0, yb + 0.3, 0), (szer + 0.16, 0.5, gl + 0.16), pas)


USTAW_REKI = {"bok": (0, 9), "lada": (-58, -6), "biodro": (-10, 38), "gora": (0, 150), "trzyma": (-75, 4)}
DL_REKI = 2.4


def _ramie(s, pivot, rx, rz, rekaw, dlon=SKORA, grub=0.9, dl=DL_REKI, karwasz=None):
    """Ręka z barku `pivot`: rękaw w dół od barku i dłoń; rx < 0 = ręka do przodu, rz > 0 = dłoń ku +X."""
    with s.uklad(pos=pivot, obrot=(rx, 0, rz)):
        s.blok("Ręka", (0, -dl / 2.0 + 0.2, 0), (grub, dl, grub), rekaw)
        s.blok("Dłoń", (0, -dl - 0.2, 0), (1.0, 1.0, 1.0), dlon)
        if karwasz:
            s.blok("Karwasz", (0, -dl + 0.45, 0), (grub + 0.3, 0.7, grub + 0.3), karwasz)


def dlon(poza, sx, yb=2.6, szer=3.0, grub=0.9):
    """Położenie dłoni (x, y, z) w układzie postaci przed skalą — do zaczepienia rekwizytu."""
    import math
    rx, rz = USTAW_REKI[poza]
    rz *= sx
    y = -DL_REKI - 0.2
    x1, y1 = -math.sin(math.radians(rz)) * y, math.cos(math.radians(rz)) * y
    a = math.radians(rx)
    return (sx * (szer / 2.0 + grub / 2.0) + x1, yb + 2.5 + y1 * math.cos(a), y1 * math.sin(a))


def _rece(s, R, rekaw, yb=2.6, szer=3.0, poza=("bok", "bok"), grub=0.9, karwasz=None):
    """poza = (lewa, prawa): "bok" (opuszczona), "lada" (dłoń na ladzie przed sobą), "biodro", "gora" (uniesiona),
    "trzyma" (zgięta do przodu, coś trzyma). rz liczone na zewnątrz dla każdej ręki."""
    with R("Rece"):
        for sx in (-1, 1):
            rx, rz = USTAW_REKI[poza[0 if sx < 0 else 1]]
            _ramie(s, (sx * (szer / 2.0 + grub / 2.0), yb + 2.5, 0), rx, sx * rz, rekaw, grub=grub, karwasz=karwasz)


def _twarz(s, R, yh, skora=SKORA, usmiech=True, brwi="tusz", patrz=0.08, glowa=(2.7, 2.6, 2.5), usta=True):
    W, H, D = glowa
    zf = D / 2.0
    with R("Glowa"):
        s.blok("Głowa", (0, yh, 0), (W, H, D), skora)
        for sx in (-1, 1):
            s.blok("Ucho", (sx * (W / 2.0 + 0.12), yh - 0.1, -0.1), (0.4, 0.8, 0.65), cien(s, skora, 0.92))
            s.blok("Oko", (sx * 0.62, yh + 0.25, zf + 0.05), (0.72, 0.86, 0.3), "biel")
            s.blok("Źrenica", (sx * 0.62 + patrz, yh + 0.18, zf + 0.22), (0.38, 0.5, 0.2), "tusz")
            if brwi:
                s.blok("Brew", (sx * 0.64, yh + 0.86, zf + 0.07), (0.9, 0.3, 0.26), brwi, rot=(0, 0, -sx * 9))
        s.blok("Nos", (0, yh - 0.2, zf + 0.3), (0.66, 0.78, 0.62), cien(s, skora, 0.88))
        if not usta:
            pass
        elif usmiech:
            s.blok("Usta", (-0.3, yh - 0.78, zf + 0.05), (0.75, 0.28, 0.3), "tusz", rot=(0, 0, -12))
            s.blok("Usta", (0.3, yh - 0.78, zf + 0.05), (0.75, 0.28, 0.3), "tusz", rot=(0, 0, 12))
        else:
            s.blok("Usta", (0, yh - 0.8, zf + 0.05), (1.0, 0.28, 0.3), "tusz")


def _korzen(s, g):
    """Pierwsza część Modelu postaci: niewidzialny „Korzeń” pod stopami (oś obrotu i zaczep dla skryptów)."""
    with s.grupa(g), s.cechy(kolizja=False, cien=False):
        s.blok("Korzeń", (0, 0.17, 0), (1.9, 0.2, 1.9), "biel", alfa=1.0)


# --------------------------------------------------------------------------- sprzedawcy
def barman(s, g):
    """Gruby karczmarz — własny projekt (17.11.2026, zamiast wąsacza w czerwieni i bieli, który za bardzo przypominał
    znaną postać z cudzych gier): łysy, krótka ruda broda z bakami BEZ wąsów, czerwona opaska karczmy zawiązana z tyłu
    (bez czapki z daszkiem), złoty kolczyk, zielona koszula, wielki brzuch, skórzany fartuch na szelkach, ręcznik na
    ramieniu; lewa dłoń na ladzie, w prawej kufel z pianą."""
    R = _R(s, g)
    _nogi(s, R, "drewno_ciemne", "tusz")
    _tulow(s, R, "dach_gildia", szer=3.5, gl=2.3, pas="drewno_ciemne")
    with R("Tulow", kolizja=True):
        s.kula("Brzuch", (0, 4.0, 0.6), 3.1, "dach_gildia")
        s.blok("Fartuch", (0, 2.05, 1.35), (3.1, 2.3, 0.4), "drewno")
        s.blok("Fartuch szew", (0, 1.0, 1.57), (3.1, 0.22, 0.1), "drewno_ciemne")
        s.blok("Fartuch kieszeń", (-0.75, 2.25, 1.58), (1.0, 0.8, 0.12), "drewno_ciemne")
    with R("Tulow"):
        for sx in (-1, 1):
            s.blok("Szelka", (sx * 0.9, 4.6, 1.42), (0.42, 2.6, 0.2), "drewno", rot=(-20, 0, 0))
        s.blok("Ręcznik", (-1.3, 5.55, 0.15), (0.9, 0.3, 2.4), "tynk_krem")
        s.blok("Ręcznik", (-1.3, 4.65, 1.35), (0.85, 1.7, 0.3), "tynk_krem", rot=(0, 0, 6))
    _rece(s, R, "dach_gildia", szer=3.5, poza=("lada", "trzyma"), grub=1.05)
    with R("Rekwizyt"):
        xd, yd, zd = dlon("trzyma", 1, szer=3.5, grub=1.05)
        with s.uklad(pos=(xd, yd - 0.2, zd + 0.15)):
            s.walec("Kufel", (0, 0.3, 0), 0.62, 1.5, "drewno_jasne", os="y")
            for yo in (-0.2, 0.75):
                s.walec("Kufel obręcz", (0, yo, 0), 0.66, 0.16, "metal_ciemny", os="y")
            s.walec("Kufel piana", (0, 1.12, 0), 0.68, 0.35, "biel", os="y")
            s.blok("Kufel ucho", (-0.78, 0.35, 0), (0.25, 0.9, 0.3), "drewno_ciemne")
    yh = 6.69
    _twarz(s, R, yh, usmiech=True, brwi="pomarancz", glowa=(2.9, 2.6, 2.6), usta=False)
    with R("Glowa"):
        s.blok("Broda", (0, yh - 1.62, 0.95), (2.8, 1.25, 1.1), "pomarancz")
        # szeroki uśmiech z zębami nisko w brodzie; wspólne usta z _twarz (dwie ukośne kreski tuż pod nosem)
        # czytały się u niego jak czarne wąsy, a wąsów ma nie mieć
        s.blok("Usta", (0, yh - 1.36, 1.52), (1.5, 0.5, 0.12), "tusz")
        s.blok("Zęby", (0, yh - 1.25, 1.56), (1.2, 0.24, 0.1), "biel")
        s.blok("Broda", (0, yh - 2.35, 1.05), (1.7, 0.6, 0.8), cien(s, "pomarancz", 0.85))
        for sx in (-1, 1):
            s.blok("Bak", (sx * 1.38, yh - 0.75, 0.45), (0.36, 1.5, 1.3), "pomarancz")
        s.blok("Policzek", (-0.95, yh - 0.35, 1.32), (0.55, 0.4, 0.2), "dach_karczma")
        s.blok("Policzek", (0.95, yh - 0.35, 1.32), (0.55, 0.4, 0.2), "dach_karczma")
        s.blok("Łysina blik", (0.5, yh + 1.33, 0.2), (1.0, 0.12, 0.7), "biel", rot=(0, 20, 0))
        s.walec("Kolczyk", (1.62, yh - 0.6, -0.1), 0.22, 0.12, "zloto", os="x")
    with R("Kapelusz"):
        s.blok("Opaska", (0, yh + 0.72, -0.02), (3.04, 0.5, 2.74), "dach_karczma")
        s.blok("Opaska węzeł", (0, yh + 0.72, -1.45), (0.6, 0.55, 0.3), cien(s, "dach_karczma", 0.85))
        for sx in (-1, 1):
            s.blok("Opaska koniec", (sx * 0.32, yh + 0.1, -1.5), (0.4, 1.1, 0.14), "dach_karczma", rot=(0, 0, sx * 18))


def mistrz_gier(s, g):
    """Mistrz gier planszowych (D-053): chudy, siedzi przy stole, okrągłe okulary, bródka bez wąsów, miękki beret
    w kolorze koła fortuny ze złotą kostką, kamizelka w szachownicę. (17.11.2026: bez cylindra, monokla i podkręconego
    wąsika — razem z muszką za bardzo przypominały maskotkę znanej gry planszowej.)"""
    R = _R(s, g)
    _nogi(s, R, "dach_twierdza", "tusz", siedzi=True, szer=1.0)
    yb = 2.3
    _tulow(s, R, "biel", yb=yb, szer=2.6, gl=1.7)
    with R("Tulow"):
        for i, (x, y) in enumerate(((-0.62, 1.0), (0.62, 1.0), (-0.62, 2.0), (0.62, 2.0))):
            s.blok("Kamizelka", (x, yb + y, 0.9), (1.2, 1.0, 0.3), "dach_kolo" if i in (0, 3) else "zloto")
        s.blok("Muszka", (0, yb + 2.6, 0.95), (1.1, 0.45, 0.3), "tusz", rot=(0, 0, 4))
    _rece(s, R, "dach_twierdza", yb=yb, szer=2.6, poza=("lada", "lada"), grub=0.8)
    yh = yb + 2.8 + 1.25
    _twarz(s, R, yh, usmiech=False, glowa=(2.5, 2.5, 2.4))
    with R("Glowa"):
        s.blok("Bródka", (0, yh - 1.3, 1.05), (0.9, 0.75, 0.45), "drewno_ciemne")
        for sx in (-1, 1):  # oprawki wokół oczu (same ramki — oczy widać)
            xo, yo = sx * 0.62, yh + 0.22
            for dy in (-0.55, 0.55):
                s.blok("Okular ramka", (xo, yo + dy, 1.47), (1.06, 0.12, 0.1), "metal_ciemny")
            for dx in (-0.47, 0.47):
                s.blok("Okular ramka", (xo + dx, yo, 1.47), (0.12, 1.22, 0.1), "metal_ciemny")
            s.blok("Okular zausznik", (sx * 1.3, yo + 0.4, 0.6), (0.12, 0.14, 1.75), "metal_ciemny")
        s.blok("Okular mostek", (0, yh + 0.4, 1.47), (0.3, 0.12, 0.1), "metal_ciemny")
    with R("Kapelusz"):
        with s.uklad(pos=(0.25, yh + 1.35, -0.1), obrot=(0, 0, -10)):
            s.walec("Beret", (0, 0, 0), 1.75, 0.55, "dach_kolo", os="y")
            s.walec("Beret otok", (0, -0.3, 0), 1.4, 0.25, cien(s, "dach_kolo", 0.8), os="y")
            s.blok("Beret ogonek", (0, 0.45, 0), (0.25, 0.4, 0.25), "dach_kolo")
            with s.cechy(cien=False):
                s.blok("Beret kostka", (0.9, 0.05, 1.2), (0.55, 0.55, 0.55), "zloto", rot=(20, 30, 0))


def zbrojmistrz(s, g):
    """Zbrojmistrz: krępy, ruda broda do piersi, hełm z nosalem, skórzany fartuch, gołe ręce z karwaszami,
    młot oparty na ramieniu."""
    R = _R(s, g)
    _nogi(s, R, "drewno", "drewno_ciemne", szer=1.25)
    _tulow(s, R, "dach_zbrojownia", szer=3.8, gl=2.3, pas="zloto")
    with R("Tulow", kolizja=True):
        s.blok("Fartuch", (0, 3.4, 1.2), (3.0, 4.2, 0.35), "drewno_ciemne")
        s.blok("Fartuch kieszeń", (0.6, 2.7, 1.42), (1.2, 0.9, 0.2), cien(s, "drewno_ciemne", 0.8))
        s.blok("Klamra", (0, 2.9, 1.47), (0.7, 0.55, 0.2), "zloto")
    _rece(s, R, SKORA, szer=3.8, poza=("lada", "trzyma"), grub=1.2, karwasz="metal_ciemny")
    with R("Rekwizyt"):
        with s.uklad(pos=dlon("trzyma", 1, szer=3.8, grub=1.2), obrot=(-38, 0, -10)):
            s.blok("Młot trzonek", (0, 1.2, 0), (0.5, 5.0, 0.5), "drewno", "Wood")
            s.blok("Młot obuch", (0, 3.9, 0), (2.4, 1.3, 1.4), "metal_ciemny")
            s.blok("Młot obuch rant", (0, 3.9, 0), (2.6, 0.35, 1.55), "tusz")
    yh = 6.69
    _twarz(s, R, yh, usmiech=False, brwi="dach_brama", glowa=(2.9, 2.6, 2.6), usta=False)
    with R("Glowa"):
        s.blok("Broda", (0, yh - 1.45, 1.05), (2.6, 2.1, 0.9), "dach_brama")
        s.blok("Broda", (0, yh - 2.5, 1.2), (1.8, 1.0, 0.7), cien(s, "dach_brama", 0.85), rot=(0, 0, 6))
        for sx in (-1, 1):
            s.blok("Wąs", (sx * 0.65, yh - 0.5, 1.6), (1.3, 0.55, 0.45), "dach_brama", rot=(0, 0, -sx * 12))
    with R("Kapelusz"):
        s.blok("Hełm", (0, yh + 1.25, -0.05), (3.15, 1.2, 2.85), "metal_ciemny")
        s.blok("Hełm rant", (0, yh + 0.75, -0.05), (3.3, 0.45, 3.0), "zloto")
        s.blok("Hełm czubek", (0, yh + 2.05, -0.05), (1.6, 0.6, 1.6), "metal_ciemny", rot=(0, 45, 0))
        s.blok("Nosal", (0, yh + 0.3, 1.45), (0.4, 1.3, 0.3), "metal_ciemny")


def mag(s, g):
    """Mag-sklepikarz: długa fioletowa szata ze złotym brzegiem, spiczasty kapelusz zgięty w czubku z gwiazdką, biała broda
    do pasa i krzaczaste brwi; jedna dłoń na ladzie, w drugiej kostur z kryształem."""
    R = _R(s, g)
    with R("Nogi", kolizja=True):
        s.blok("Szata dół", (0, 1.4, 0), (3.0, 2.6, 2.3), "dach_sklep")
        s.blok("Szata brzeg", (0, 0.3, 0), (3.15, 0.5, 2.45), "zloto")
        for sx in (-1, 1):
            s.blok("But", (sx * 0.7, 0.25, 1.2), (1.0, 0.5, 0.9), "tusz")
    _tulow(s, R, "dach_sklep", szer=2.9, gl=2.0, pas="zloto")
    _rece(s, R, cien(s, "dach_sklep", 0.85), szer=2.9, poza=("trzyma", "lada"), grub=1.05)
    with R("Rekwizyt"):
        xd, _, zd = dlon("trzyma", -1, szer=2.9, grub=1.05)
        with s.uklad(pos=(xd, 0.0, zd), obrot=(0, 0, 4)):
            xe, ye, _ = zestaw.lamana(s, "Kostur", [(4.5, 0.55, 0), (3.2, 0.5, -6), (1.4, 0.45, 25)], "drewno", "Wood")
            with s.cechy(cien=False):
                s.blok("Kostur kryształ", (xe, ye + 0.7, 0), (1.1, 1.6, 1.1), "neon_magia", "Neon", rot=(0, 45, 12))
    yh = 6.69
    _twarz(s, R, yh, usmiech=False, brwi="biel", glowa=(2.6, 2.6, 2.5))
    with R("Glowa"):
        s.blok("Broda", (0, yh - 1.55, 1.0), (2.3, 2.3, 0.8), "biel")
        s.blok("Broda", (0.15, yh - 2.95, 1.1), (1.6, 1.2, 0.6), cien(s, "biel", 0.9), rot=(0, 0, -8))
        for sx in (-1, 1):
            s.blok("Wąs", (sx * 0.6, yh - 0.5, 1.58), (1.25, 0.5, 0.45), "biel", rot=(0, 0, sx * 14))
            s.blok("Brew krzak", (sx * 0.75, yh + 0.95, 1.2), (1.0, 0.45, 0.4), "biel", rot=(0, 0, -sx * 18))
    with R("Kapelusz"):
        s.walec("Kapelusz rondo", (0, yh + 1.4, 0), 2.1, 0.35, cien(s, "dach_sklep", 0.85), os="y")
        s.walec("Kapelusz opaska", (0, yh + 1.8, 0), 1.25, 0.55, "zloto", os="y")
        with s.uklad(pos=(0, yh + 1.55, 0), obrot=(-6, 0, 5)):
            s.ostroslup("Kapelusz stożek", (0, 0, 0), 1.25, 1.25, 3.4, "dach_sklep")
            with s.uklad(pos=(0, 2.9, 0), obrot=(-30, 0, 0)):
                s.ostroslup("Kapelusz czubek", (0, 0, 0), 0.55, 0.55, 2.0, "dach_sklep")
                with s.cechy(cien=False):
                    s.blok("Gwiazdka", (0, 2.1, 0.2), (0.9, 0.9, 0.25), "zloto", rot=(0, 0, 45))
                    s.blok("Gwiazdka", (0, 2.1, 0.22), (0.9, 0.9, 0.25), "zloto")


def trener(s, g):
    """Trener Training Center: płaski czub, niebieska opaska na pot (17.11.2026: była czerwona — z białą koszulką za
    blisko znanego wojownika z bijatyk, a czerwoną opaskę ma już karczmarz), gwizdek na sznurku, podkoszulek z pasem,
    krótkie spodenki, wielkie ramiona; jedna ręka wskazuje tablicę wyboru, druga na biodrze."""
    R = _R(s, g)
    with R("Nogi", kolizja=True):
        for sx in (-1, 1):
            s.blok("Spodenki", (sx * 0.75, 2.2, 0), (1.25, 0.9, 1.25), "dach_twierdza")
            s.blok("Noga", (sx * 0.75, 1.3, 0), (1.0, 1.2, 1.0), SKORA)
            s.blok("But", (sx * 0.75, 0.4, 0.2), (1.35, 0.8, 1.9), "biel")
            s.blok("But pas", (sx * 0.75, 0.55, 0.2), (1.4, 0.3, 1.95), "dach_arena")
    _tulow(s, R, "biel", szer=3.6, gl=2.0, pas="dach_twierdza")
    with R("Tulow"):
        s.blok("Pas koszulki", (0, 4.4, 1.03), (3.4, 0.7, 0.2), "dach_arena", rot=(0, 0, -8))
        s.blok("Sznurek", (0.35, 4.9, 1.05), (0.15, 1.3, 0.15), "tusz", rot=(0, 0, 25))
        s.blok("Gwizdek", (0.65, 4.2, 1.15), (0.55, 0.45, 0.8), "zloto")
    _rece(s, R, SKORA, szer=3.6, poza=("biodro", "gora"), grub=1.25)
    yh = 6.69
    _twarz(s, R, yh, usmiech=True, glowa=(2.8, 2.6, 2.5))
    with R("Glowa"):
        s.blok("Podbródek", (0, yh - 1.15, 0.9), (1.6, 0.6, 0.8), cien(s, SKORA, 0.95))
    with R("Kapelusz"):
        s.blok("Czub", (0, yh + 1.65, 0), (2.85, 0.8, 2.6), "tusz")
        s.blok("Opaska", (0, yh + 1.0, 0), (2.95, 0.5, 2.65), "dach_twierdza")
        s.blok("Opaska pasek", (0, yh + 1.0, 1.34), (2.0, 0.16, 0.06), "biel")


def opiekunka(s, g):
    """Opiekunka zagrody petów: słomkowy kapelusz, rude warkocze, morskie ogrodniczki, w jednej ręce wiadro z kością,
    druga macha."""
    R = _R(s, g)
    _nogi(s, R, "dach_wylegarnia", "drewno_ciemne")
    _tulow(s, R, "biel", szer=3.0, gl=1.9, pas=None)
    with R("Tulow"):
        s.blok("Ogrodniczki", (0, 3.4, 0.99), (2.4, 1.8, 0.2), "dach_wylegarnia")
        s.blok("Ogrodniczki", (0, 2.9, 0), (3.1, 0.8, 2.0), "dach_wylegarnia")
        for sx in (-1, 1):
            s.blok("Szelka", (sx * 0.85, 4.75, 1.0), (0.4, 1.3, 0.2), "dach_wylegarnia")
            s.blok("Guzik", (sx * 0.85, 4.15, 1.12), (0.4, 0.4, 0.2), "zloto")
    _rece(s, R, "biel", szer=3.0, poza=("trzyma", "gora"), grub=0.9)
    with R("Rekwizyt"):
        xd, yd, zd = dlon("trzyma", -1, szer=3.0, grub=0.9)
        with s.uklad(pos=(xd, yd - 1.3, zd + 0.2)):
            s.walec("Wiadro", (0, 0, 0), 0.8, 1.5, "drewno", os="y")
            s.walec("Wiadro obręcz", (0, 0.45, 0), 0.88, 0.28, "metal_ciemny", os="y")
            s.blok("Wiadro kabłąk", (0, 1.05, 0), (1.7, 0.2, 0.2), "metal_ciemny")
            s.blok("Kość", (0, 0.95, 0.1), (1.5, 0.35, 0.35), "biel", rot=(0, 30, 20))
    yh = 6.69
    _twarz(s, R, yh, usmiech=True, glowa=(2.7, 2.6, 2.5))
    with R("Glowa"):
        s.blok("Włosy", (0, yh + 1.1, -0.15), (2.85, 0.7, 2.6), "pomarancz")
        for sx in (-1, 1):
            s.blok("Warkocz", (sx * 1.55, yh - 0.7, -0.2), (0.6, 2.2, 0.6), "pomarancz", rot=(0, 0, sx * 8))
            s.blok("Wstążka", (sx * 1.62, yh - 1.65, -0.2), (0.75, 0.35, 0.75), "dach_wylegarnia")
            s.blok("Pieg", (sx * 0.95, yh - 0.35, 1.3), (0.25, 0.25, 0.2), "dach_brama")
    with R("Kapelusz"):
        s.walec("Kapelusz rondo", (0, yh + 1.5, 0), 2.2, 0.3, "dach_stajnia", os="y", rot=(0, 0, 6))
        s.walec("Kapelusz główka", (0.1, yh + 2.05, 0), 1.35, 1.0, "dach_stajnia", os="y", rot=(0, 0, 6))
        s.walec("Kapelusz opaska", (0.07, yh + 1.8, 0), 1.4, 0.35, "dach_wylegarnia", os="y", rot=(0, 0, 6))


TYPY = {"barman": barman, "mistrz_gier": mistrz_gier, "zbrojmistrz": zbrojmistrz, "mag": mag, "trener": trener,
        "opiekunka": opiekunka}


def postac(s, typ, grupa, pos, ry=0.0, skala=SKALA):
    """Stawia postać `typ` w grupie `grupa` (np. "Karczma/Barman"): stopy w `pos` (układ wywołującego), twarz ku ry."""
    with s.uklad(pos=pos, obrot=(0, ry, 0), skala=skala):
        _korzen(s, grupa)
        TYPY[typ](s, grupa)


# --------------------------------------------------------------------------- pety z kanonu (Pety.md: pies, slime, smok)
def pies(s, grupa, pos, ry=0.0, skala=1.0):
    """Pies: brązowy i kanciasty, obroża w błękicie Rycerza, ogon w górę."""
    with s.uklad(pos=pos, obrot=(0, ry, 0), skala=skala):
        _korzen(s, grupa)
        with s.grupa(grupa + "/Cialo"), s.cechy(kolizja=False):
            s.blok("Pies tułów", (0, 1.75, 0), (1.8, 1.5, 3.0), "drewno")
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Pies łapa", (sx * 0.6, 0.55, sz * 1.0), (0.6, 1.1, 0.6), "drewno_ciemne")
            with s.uklad(pos=(0, 2.4, -1.5), obrot=(-40, 0, 0)):
                s.blok("Pies ogon", (0, 0.7, 0), (0.45, 1.5, 0.45), "drewno_ciemne")
            s.blok("Pies obroża", (0, 2.45, 1.45), (1.5, 0.4, 0.6), "dach_twierdza")
        with s.grupa(grupa + "/Glowa"), s.cechy(kolizja=False):
            s.blok("Pies głowa", (0, 2.95, 1.75), (1.7, 1.55, 1.6), "drewno")
            s.blok("Pies pysk", (0, 2.6, 2.75), (1.0, 0.8, 0.8), "drewno_jasne")
            s.blok("Pies nos", (0, 2.85, 3.18), (0.5, 0.4, 0.2), "tusz")
            for sx in (-1, 1):
                s.blok("Pies ucho", (sx * 0.95, 3.0, 1.6), (0.35, 1.2, 0.7), "drewno_ciemne", rot=(0, 0, sx * 12))
                s.blok("Pies oko", (sx * 0.42, 3.25, 2.58), (0.32, 0.4, 0.15), "tusz")


def slime(s, grupa, pos, ry=0.0, skala=1.0):
    """Slime: świecąca cyjanowa kostka (Neon) z oczami i uśmiechem w tuszu."""
    with s.uklad(pos=pos, obrot=(0, ry, 0), skala=skala):
        _korzen(s, grupa)
        with s.grupa(grupa + "/Cialo"), s.cechy(kolizja=False):
            with s.cechy(cien=False):
                s.blok("Slime", (0, 1.25, 0), (2.5, 2.5, 2.5), "neon_slime", "Neon", rot=(0, 0, 4))
            s.blok("Slime blik", (-0.6, 2.35, 0.7), (0.8, 0.25, 0.6), "biel")
            for sx in (-1, 1):
                s.blok("Slime oko", (sx * 0.5, 1.55, 1.3), (0.35, 0.55, 0.15), "tusz")
            s.blok("Slime usta", (0, 0.95, 1.3), (0.8, 0.22, 0.15), "tusz")


def smok(s, grupa, pos, ry=0.0, skala=1.0):
    """Mały czerwony smok: kanciasty, złote różki i brzuch, skrzydełka w czerwieni karczmy, ogon z kolcem."""
    with s.uklad(pos=pos, obrot=(0, ry, 0), skala=skala):
        _korzen(s, grupa)
        with s.grupa(grupa + "/Cialo"), s.cechy(kolizja=False):
            s.blok("Smok tułów", (0, 1.6, 0), (1.6, 1.5, 2.4), "czerwien")
            s.blok("Smok brzuch", (0, 1.4, 0.6), (1.2, 1.0, 1.4), "zloto")
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Smok łapa", (sx * 0.55, 0.45, sz * 0.8), (0.55, 0.9, 0.6), "dach_karczma")
                with s.uklad(pos=(sx * 0.8, 2.3, -0.2), obrot=(0, sx * 20, sx * 35)):
                    s.klin("Smok skrzydło", (sx * 0.9, 0, 0), (1.8, 0.25, 1.6), "dach_karczma", rot=(0, 90 * sx, 0))
            with s.uklad(pos=(0, 1.7, -1.2), obrot=(25, 0, 0)):
                s.blok("Smok ogon", (0, 0, -0.8), (0.6, 0.6, 1.8), "czerwien")
                s.klin("Smok kolec", (0, 0.1, -1.95), (0.9, 0.7, 0.6), "zloto", rot=(0, 180, 0))
        with s.grupa(grupa + "/Glowa"), s.cechy(kolizja=False):
            s.blok("Smok głowa", (0, 2.75, 1.45), (1.4, 1.3, 1.5), "czerwien")
            s.blok("Smok pysk", (0, 2.5, 2.35), (1.0, 0.7, 0.8), "czerwien")
            for sx in (-1, 1):
                s.blok("Smok oko", (sx * 0.38, 3.0, 2.22), (0.3, 0.38, 0.15), "tusz")
                s.klin("Smok róg", (sx * 0.45, 3.65, 1.2), (0.35, 0.8, 0.6), "zloto", rot=(-15, 0, 0))
