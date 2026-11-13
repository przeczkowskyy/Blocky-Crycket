# -*- coding: utf-8 -*-
"""Arena „wkrótce” mapy v2 „Krzywe Miasteczko” — wycinek wielkiego pierścienia wbudowany w mur (PROJEKT.md, karta 5.9).

Mur areny z 6 krzywych segmentów na łuku wypukłym ku rynkowi (górne części pochylone na przemian w przód i w tył,
co drugi wyższy i w cieniu), na koronie kolce `dach_arena`, na stykach proporce czerwono-białe. Brama: dwa filary nie
do pary (lewy wyższy, rz +5°, prawy niższy, rz −7°), nadproże i hełm-olbrzym z pióropuszem jako szyld. „Wkrótce” bez
liter: skrzydła zabite deskami na krzyż, dwa łańcuchy z kłódką, w szparze ciepłe światło. Żart: odcisk ludzika w murze
z gruzem pod spodem. Echo: gong na krzywych słupach po prawej. Kuszenie: zza muru wystaje złoty puchar z plastrem.

Konwencja (PROJEKT 5.0): (0, 0, 0) = środek działki na ziemi, front z wejściem ku +Z, działka x ∈ ±24, z ∈ ±16,
wys. ≤ 34. Tył (końce pierścienia w z ≈ −16) styka się z murem miejskim.

Odstępstwo od karty: okrąg R 30 ze środkiem (0; −22) i segmenty na ±13° nie mieszczą bramy 12 + dwóch filarów
(między segmentami ±13° zostaje 6,6 studa), a pełne 6 segmentów 7-studowych na R 30 wychodzi poza działkę 48.
Dlatego łuk ma R 21 ze środkiem (0; −12): brama na osi, segmenty na ±44,5°, ±63,5°, ±82,5°, końce pierścienia
dochodzą do tylnej krawędzi działki (do muru miejskiego).

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/arena.py --wyj <folder> --szer 1000
"""
import contextlib
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "Arena"
OBRYS = (48, 32)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 34
BUDZET = 330                     # twardy sufit 413
INTERAKCJA = (0.0, 20.0)         # przed bramą, na osi przejścia
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków

KAMIEN = "kamien_cieply"
KOD = "dach_arena"

# łuk muru areny
R, CZ = 21.0, -12.0              # promień linii środka muru i środek okręgu (z)
GRUB = 4.0                       # grubość muru (promieniowo)
SEG_W = 7.4                      # szerokość segmentu (stycznie)
# segmenty od lewej (−X) do prawej: (kąt°, wysokość, pochylenie górnej części rx°, przechył rz°)
SEGMENTY = (
    (-82.5, 16.0, 5.0, 0.0),
    (-63.5, 18.0, -4.0, 4.0),
    (-44.5, 16.0, 6.0, 0.0),
    (44.5, 18.0, -5.0, -4.0),
    (63.5, 16.0, 5.0, 0.0),
    (82.5, 18.0, -4.0, 5.0),
)
DOL = 10.5                       # dolna część muru pionowa (przykazanie 3)

# brama
FIL_W, FIL_D, FIL_Z = 7.0, 7.0, 8.0          # filar: szerokość, głębokość, środek z
PRZ = 12.0                                   # szerokość przejścia
PRZ_H = 14.0                                 # prześwit


@contextlib.contextmanager
def _na_luku(s, kat, r=R):
    """Układ na łuku muru: (0, 0, 0) na okręgu o promieniu r pod kątem `kat`, lokalne +Z = na zewnątrz (ku rynkowi)."""
    a = math.radians(kat)
    with s.uklad(pos=(r * math.sin(a), 0.0, CZ + r * math.cos(a)), obrot=(0, kat, 0)):
        yield s


def buduj(s, rnd):
    _mur(s)
    _wnetrze(s)
    _filary(s)
    _przejscie(s)
    with s.cechy(kolizja=False):
        _helm(s)
        _proporce(s)
        _odcisk(s, rnd)
        _puchar(s)
    _gong(s)
    _znaki_i_rekwizyty(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- mur areny
def _mur(s):
    """6 segmentów: cokół, prosty dół do 10,5, pochylona góra (rx/rz z tabeli), pas tuszu pod koroną, 2 kolce.
    Końce pierścienia przedłużone prostymi przyczółkami do tylnej krawędzi działki (styk z murem miejskim)."""
    for i, (kat, h, rx, rz) in enumerate(SEGMENTY):
        kol = KAMIEN if i % 2 == 0 else cien(s, KAMIEN)
        with _na_luku(s, kat):
            s.blok("Mur cokół", (0, 1.0, 0), (SEG_W + 0.3, 2.0, GRUB + 0.8), "kamien_cokol", "Cobblestone")
            s.blok("Mur dół", (0, 0.3 + DOL / 2.0, 0), (SEG_W, DOL, GRUB), kol)
            with s.uklad(pos=(0, DOL - 0.3, 0), obrot=(rx, 0, rz)):
                hg = h - DOL + 0.3                                   # wierzch muru w układzie górnej części
                s.blok("Mur góra", (0, hg / 2.0 - 0.3, 0), (SEG_W - 0.2, hg + 0.6, GRUB - 0.3), kol)
                with s.cechy(kolizja=False):
                    s.blok("Mur pas", (0, hg - 1.0, 0), (SEG_W + 0.15, 0.7, GRUB + 0.15), "tusz")
                    # arkada: ciemne okno łukowe (echo koloseum), co drugie przesunięte w bok
                    xa = (-1.3, 1.1, -0.9, 1.4, -1.2, 0.8)[i]
                    za = (GRUB - 0.3) / 2.0 + 0.1
                    with s.cechy(cien=False):
                        if i in (1, 5):                              # dwie arkady świecą: w środku coś się szykuje
                            s.blok("Mur arkada rama", (xa, 1.95, za), (3.0, 2.7, 0.3), "tusz")
                            s.walec("Mur arkada rama", (xa, 3.1, za), 1.5, 0.3, "tusz", os="z")
                            s.blok("Mur arkada światło", (xa, 2.0, za + 0.12), (2.2, 2.3, 0.3), "neon_okno", "Neon")
                            s.walec("Mur arkada światło", (xa, 3.1, za + 0.12), 1.1, 0.3, "neon_okno", "Neon", os="z")
                        else:
                            s.blok("Mur arkada", (xa, 1.95, za), (2.2, 2.3, 0.3), "tusz")
                            s.walec("Mur arkada", (xa, 3.1, za), 1.1, 0.3, "tusz", os="z")
                    for x in (-1.85, 1.85):
                        s.ostroslup("Mur kolec", (x, hg - 0.4, 0), 1.0, 1.0, 3.4, KOD)
    # przyczółki: końce łuku (z ≈ −13) → tylna krawędź działki (z = −16), wys. muru miejskiego 14 + rant
    for zn in (-1, 1):
        with s.uklad(pos=(zn * 20.9, 0, -14.0), obrot=(0, zn * 4, 0)):
            s.blok("Przyczółek cokół", (0, 1.0, 0), (4.6, 2.0, 3.0), "kamien_cokol", "Cobblestone")
            s.blok("Przyczółek", (0, 7.6, 0), (4.0, 14.8, 2.8), cien(s, KAMIEN, 0.9))
            with s.cechy(kolizja=False):
                s.blok("Przyczółek rant", (0, 13.6, 0), (4.3, 0.6, 3.1), "tusz")


def _wnetrze(s):
    """Wnętrze za murem (widać je z góry i zza muru): ubity piasek areny i dwie drewniane ławy trybun przy bokach."""
    with s.cechy(kolizja=False, cien=False):
        s.blok("Arena piasek", (0, 0.02, -5.0), (21.0, 0.2, 21.0), "ziemia")
        s.blok("Arena piasek", (0, 0.0, -9.0), (34.0, 0.2, 13.0), "ziemia")
        for zn in (-1, 1):
            s.blok("Arena piasek", (zn * 13.5, -0.02, -0.5), (6.0, 0.2, 6.0), "ziemia", rot=(0, 45, 0))
    for kat in (-72.0, 73.0):
        with _na_luku(s, kat, R - GRUB / 2.0 - 1.6):
            s.blok("Trybuna", (0, 1.6, 0), (12.5, 3.2, 3.0), "drewno", "WoodPlanks")
            s.blok("Trybuna", (0, 3.4, 1.5), (12.0, 6.8, 1.6), "drewno_jasne", "WoodPlanks")


# --------------------------------------------------------------------------- brama
def _filar(s, x, ry, rz, h_gora, kol_gora, szczyt, zn):
    """Filar bramy: prosty dół do 11,5 (cokół, narożniki zewnętrzne tuszem, gzyms) i pochylona góra z pasem
    `dach_arena` i czapą; szczyt(s, y) dobudowuje wierzchołek w układzie pochylonej góry (y = wierzch czapy).
    zn = −1 lewy, +1 prawy (strona zewnętrzna dostaje narożniki sylwetki)."""
    with s.uklad(pos=(x, 0, FIL_Z), obrot=(0, ry, 0)):
        s.blok("Filar cokół", (0, 1.1, 0), (FIL_W + 1.0, 2.2, FIL_D + 1.0), "kamien_cokol", "Cobblestone")
        s.blok("Filar dół", (0, 6.25, 0), (FIL_W, 10.5, FIL_D), KAMIEN)
        with s.cechy(kolizja=False):
            s.blok("Filar cokół rant", (0, 2.3, 0), (FIL_W + 1.3, 0.45, FIL_D + 1.3), "tusz")
            s.blok("Filar gzyms", (0, 11.6, 0), (FIL_W + 0.8, 1.2, FIL_D + 0.8), "tusz")
            # narożne ciosy na przedniej krawędzi zewnętrznej (3) i wewnętrznej (2), na przemian dłuższe w bok i w głąb
            ciosy = ((zn, 3.5, 2.6, 1.8), (zn, 6.4, 1.8, 2.6), (zn, 9.3, 2.6, 1.8), (-zn, 4.6, 1.8, 2.4), (-zn, 8.2, 2.4, 1.8))
            for sx, y, a, b in ciosy:
                s.blok("Filar cios", (sx * (FIL_W / 2.0 - a / 2.0 + 0.15), y, FIL_D / 2.0 - b / 2.0 + 0.15), (a, 1.9, b),
                       cien(s, KAMIEN, 0.8))
        with s.uklad(pos=(0, 11.4, 0), obrot=(0, 0, rz)):
            s.blok("Filar góra", (0, h_gora / 2.0 - 0.25, 0), (FIL_W - 0.6, h_gora + 0.5, FIL_D - 0.6), kol_gora)
            with s.cechy(kolizja=False):
                s.blok("Filar pas", (0, h_gora - 2.4, 0), (FIL_W - 0.2, 1.6, FIL_D - 0.2), KOD, "Fabric")
                s.blok("Filar czapa", (0, h_gora + 0.3, 0), (FIL_W + 0.2, 1.0, FIL_D + 0.2), "tusz")
                szczyt(s, h_gora + 0.8)


def _filary(s):
    xf = PRZ / 2.0 + FIL_W / 2.0

    def kolec(s, y):
        s.ostroslup("Filar kolec", (0, y - 0.1, 0), 2.0, 2.0, 4.2, KOD)

    def choragiewka(s, y):
        zestaw.choragiewka_duetu(s, (0.6, y - 0.2, 0.6), "rycerz", przechyl=-12)

    _filar(s, -xf, -4, 5, 11.6, KAMIEN, kolec, -1)              # lewy: 24 wys. (+ kolec), góra rz +5°
    _filar(s, xf, 5, -7, 7.6, cien(s, KAMIEN), choragiewka, 1)  # prawy: 20 wys., góra rz −7°


def _przejscie(s):
    """Nadproże nad przejściem 12 × 14, skrzydła zabite deskami, szpara ze światłem, łańcuchy z kłódką."""
    z0 = FIL_Z
    s.blok("Nadproże", (0, PRZ_H + 1.05, z0 + 0.3), (PRZ + 2.6, 1.7, 5.6), KAMIEN)
    # skrzydła bramy z wąską szparą pośrodku; za szparą światło, za światłem zaślepka (od strony areny).
    # Skrzydła i zaślepka MAJĄ kolizję: brama „wkrótce” jest zamknięta (inaczej trybuny są schodami na mur).
    zs = z0 + 1.2
    for zn in (-1, 1):
        s.blok("Brama skrzydło", (zn * 3.25, PRZ_H / 2.0, zs), (5.7, PRZ_H - 0.1, 0.6), "drewno_ciemne", "WoodPlanks")
    s.blok("Brama zaślepka", (0, PRZ_H / 2.0, zs - 0.9), (3.0, PRZ_H - 0.3, 0.4), "drewno_ciemne", "WoodPlanks")
    with s.cechy(kolizja=False):
        s.blok("Nadproże spód", (0, PRZ_H + 0.2, z0 + 0.3), (PRZ + 2.2, 0.4, 6.0), "tusz")
        with s.cechy(cien=False):
            s.blok("Brama światło", (0, PRZ_H / 2.0, zs - 0.45), (1.6, PRZ_H - 0.6, 0.3), "neon_okno", "Neon")
        # deski na krzyż (dwie warstwy) i jedna pozioma
        for i, k in enumerate((39, -37)):
            s.blok("Brama deska", (0, 7.0, zs + 0.6 + 0.45 * i), (1.6, 17.0, 0.4), "drewno_jasne", "WoodPlanks", rot=(0, 0, k))
        s.blok("Brama deska", (0.3, 10.6, zs + 1.75), (13.0, 1.5, 0.4), "drewno_jasne", "WoodPlanks", rot=(0, 0, -5))
        # dwa łańcuchy od filarów do kłódki
        zl = zs + 2.35
        for (xa, ya), (xb, yb) in (((-6.0, 11.4), (-0.6, 6.1)), ((6.0, 9.4), (0.6, 6.1))):
            n = 4
            for j in range(n):
                t0, t1 = j / float(n), (j + 1) / float(n)
                p1 = (xa + (xb - xa) * t0, ya + (yb - ya) * t0 - 0.5 * math.sin(math.pi * t0), zl)
                p2 = (xa + (xb - xa) * t1, ya + (yb - ya) * t1 - 0.5 * math.sin(math.pi * t1), zl)
                s.belka("Brama łańcuch", p1, p2, 0.5 if j % 2 == 0 else 0.9, "metal_ciemny", "SmoothPlastic",
                        szer=0.9 if j % 2 == 0 else 0.4)
        with s.uklad(pos=(0, 5.0, zl + 0.3), obrot=(0, 0, 8)):
            s.blok("Kłódka płetwa", (0, 0, -0.35), (3.6, 3.8, 0.3), "tusz")
            s.blok("Kłódka", (0, 0, 0.1), (2.8, 3.0, 1.0), "zloto")
            for zn in (-1, 1):
                s.blok("Kłódka pałąk", (zn * 0.9, 2.2, 0.1), (0.6, 1.6, 0.6), "tusz")
            s.blok("Kłódka pałąk", (0, 2.85, 0.1), (2.4, 0.6, 0.6), "tusz")
            with s.cechy(cien=False):
                s.blok("Kłódka dziurka", (0, -0.2, 0.7), (0.6, 1.2, 0.3), "tusz")


# --------------------------------------------------------------------------- szyld: hełm-olbrzym
def _helm(s):
    """Hełm 14 × 12 nad przejściem: dzwon + kopuła (walec), płetwa tusz, przyłbica w kształcie T, złoty rant i grzebień,
    pióropusz z 5 płyt `dach_arena` rozwiany w prawo (nad niższym filarem)."""
    with s.uklad(pos=(0.3, PRZ_H + 1.9 + 5.2, FIL_Z + 0.6), obrot=(10, -4, 8)):
        s.blok("Hełm dzwon", (0, -2.6, 0), (14.0, 5.2, 8.0), "tynk_blekit")
        s.walec("Hełm kopuła", (0, 0, 0), 6.8, 7.6, "tynk_blekit", os="z")
        s.blok("Hełm płetwa", (0, -2.6, 0), (15.0, 6.2, 0.4), "tusz")
        s.walec("Hełm płetwa", (0, 0, 0), 7.3, 0.4, "tusz", os="z")
        s.blok("Hełm rant", (0, -5.0, 0), (14.4, 0.9, 8.4), "zloto")
        s.blok("Hełm grzebień", (0, 6.8, -0.3), (1.2, 1.2, 7.0), "zloto")
        # przyłbica: dwie osobne szpary na oczy i złoty nosal między nimi (bez czarnego „T”, które czytało się jak litera)
        for zn in (-1, 1):
            s.blok("Hełm przyłbica", (zn * 2.8, -1.4, 4.15), (4.5, 1.0, 0.4), "tusz")
        s.blok("Hełm nosal", (0, -1.6, 4.35), (1.4, 6.0, 0.4), "zloto")
        with s.cechy(cien=False):
            for x, y in ((3.2, -2.9), (4.4, -3.5), (3.4, -4.1)):
                s.blok("Hełm otwór", (x, y, 4.12), (0.7, 0.7, 0.3), "tusz")
        # pióropusz: płyty od 30° do prawie poziomu (95°) w prawo, odchylone do tyłu — rozwiany wiatrem ku +X
        with s.uklad(pos=(0.4, 6.9, -0.8), obrot=(-14, 0, 0)):
            s.blok("Pióropusz zaczep", (0, 0.3, 0), (1.8, 1.4, 1.8), "zloto")
            for i, (k, dl) in enumerate(((-32, 5.2), (-48, 5.9), (-63, 7.0), (-79, 6.8), (-95, 5.4))):
                with s.uklad(pos=(0, 0.4, 0.12 * (i % 2)), obrot=(0, 0, k)):
                    s.blok("Pióropusz", (0, dl / 2.0, 0), (2.3, dl, 0.8), KOD if i % 2 == 0 else cien(s, KOD, 0.85), "Fabric")


# --------------------------------------------------------------------------- proporce na stykach segmentów
def _proporce(s):
    """Proporce 3 × 10 (Fabric) na stykach segmentów, na przemian `dach_arena` i `biel`, z ogonem jaskółczym
    i rombem w drugim kolorze; drążek tuszem wpuszczony w mur."""
    katy = [sg[0] for sg in SEGMENTY]
    styki = [(katy[0] + katy[1]) / 2.0, (katy[1] + katy[2]) / 2.0, (katy[3] + katy[4]) / 2.0, (katy[4] + katy[5]) / 2.0]
    pol = abs(katy[1] - katy[0]) / 2.0
    r = (R + GRUB / 2.0) / math.cos(math.radians(pol)) + 0.45      # lico muru na styku + odstęp
    for i, kat in enumerate(styki):
        kol, kol2 = (KOD, "biel") if i % 2 == 0 else ("biel", KOD)
        with _na_luku(s, kat, r):
            top = 15.4
            s.blok("Proporzec drążek", (0, top + 0.3, -0.25), (3.9, 0.6, 1.4), "tusz")
            s.blok("Proporzec", (0, top - 4.1, 0), (3.0, 8.2, 0.4), kol, "Fabric")
            for zn in (-1, 1):
                s.klin("Proporzec ogon", (zn * 0.75, top - 8.2 - 0.9, 0), (0.36, 1.8, 1.5), kol,
                       rot=(0, zn * 90, 180))
            with s.cechy(cien=False):
                s.blok("Proporzec romb", (0, top - 3.2, 0.3), (1.5, 1.5, 0.3), kol2, rot=(0, 0, 45))


# --------------------------------------------------------------------------- żart: odcisk ludzika
def _odcisk(s, rnd):
    """Odcisk ludzika 6 × 7,5 w tuszu na licu segmentu obok bramy (pozycja „gwiazdy” — wyleciał przez ścianę),
    z rysami i gruzem pod spodem."""
    kat = SEGMENTY[2][0]
    with _na_luku(s, kat, R + GRUB / 2.0):
        with s.uklad(pos=(0.6, 6.4, 0.12)), s.cechy(cien=False):
            s.blok("Odcisk głowa", (0.3, 2.85, 0), (1.9, 1.9, 0.3), "tusz", rot=(0, 0, 8))
            s.blok("Odcisk tułów", (0, 0.6, 0), (2.3, 2.8, 0.3), "tusz")
            s.blok("Odcisk ręka", (-2.0, 1.85, 0), (0.95, 3.0, 0.3), "tusz", rot=(0, 0, 55))
            s.blok("Odcisk ręka", (2.0, 2.0, 0), (0.95, 3.0, 0.3), "tusz", rot=(0, 0, -62))
            s.blok("Odcisk noga", (-0.85, -1.95, 0), (0.95, 3.0, 0.3), "tusz", rot=(0, 0, -17))
            s.blok("Odcisk noga", (0.9, -1.95, 0), (0.95, 3.0, 0.3), "tusz", rot=(0, 0, 22))
            for x, y, k in ((-3.3, 3.4, 30), (3.4, -0.6, -70), (-2.0, -3.6, -40)):
                s.blok("Odcisk rysa", (x, y, 0), (0.3, 1.6, 0.25), "tusz", rot=(0, 0, k))
        for x, z, a, k in ((-1.2, 1.8, 1.6, 20), (0.9, 2.6, 1.2, -35), (2.0, 1.5, 0.9, 50)):
            s.blok("Gruz", (x, a * 0.35, z), (a, a * 0.8, a), KAMIEN, rot=(12, k, 9))


# --------------------------------------------------------------------------- kuszenie: puchar zza muru
def _puchar(s):
    """Złoty puchar ok. 9 wys. na postumencie za murem (widać kielich ponad koroną), z plastrem na krzyż `biel`."""
    with _na_luku(s, -60.0, 14.5):
        s.blok("Puchar postument", (0, 10.9, 0), (4.0, 21.8, 4.0), "kamien_cokol")   # +3: kielich ma wystawać ponad koronę
        with s.uklad(pos=(0, 21.8, 0), obrot=(0, 50, -6)):
            s.blok("Puchar stopa", (0, 0.5, 0), (4.2, 1.0, 4.2), "zloto")
            s.walec("Puchar nóżka", (0, 2.0, 0), 0.8, 2.4, cien(s, "zloto", 0.85), os="y")
            s.walec("Puchar czasza", (0, 4.0, 0), 2.2, 1.6, "zloto", os="y")
            s.walec("Puchar czasza", (0, 6.6, 0), 3.2, 4.0, "zloto", os="y")
            s.blok("Puchar płetwa", (0, 5.9, 0), (11.4, 5.6, 0.4), "tusz")
            for zn in (-1, 1):
                s.blok("Puchar ucho", (zn * 4.1, 7.3, 0), (0.8, 3.0, 0.8), "zloto")
                s.blok("Puchar ucho", (zn * 3.6, 8.5, 0), (1.6, 0.8, 0.8), "zloto")
                s.blok("Puchar ucho", (zn * 3.6, 6.1, 0), (1.6, 0.8, 0.8), "zloto")
            with s.cechy(cien=False):
                s.blok("Puchar plaster", (0.3, 6.8, 3.2), (2.6, 0.9, 0.3), "biel", rot=(0, 0, 35))
                s.blok("Puchar plaster", (0.3, 6.8, 3.32), (2.6, 0.9, 0.3), "biel", rot=(0, 0, -35))


# --------------------------------------------------------------------------- echo: gong
def _gong(s):
    """Gong Ø 10 (`zloto`, podkładka tusz) na dwóch krzywych słupach po prawej, z pałką opartą o słup."""
    with s.uklad(pos=(18.4, 0, 10.85), obrot=(0, -42, 0)):
        konce = []
        for x, ks in ((-5.6, (5, -9)), (5.6, (-6, 10))):
            with s.uklad(pos=(x, 0, 0)):
                xe, ye, _ = zestaw.lamana(s, "Gong słup", [(7.0, 1.2, ks[0]), (6.0, 1.0, ks[1])], "drewno_ciemne", "Wood")
                konce.append((x + xe, ye))
        with s.cechy(kolizja=False):
            (x1, y1), (x2, y2) = konce
            s.belka("Gong belka", (x1 - 0.9, y1 - 0.2, 0), (x2 + 0.3, y2 - 0.2, 0), 1.1, "drewno", "Wood", szer=1.3)
            ym = (y1 + y2) / 2.0 - 0.8
            for x in (-1.6, 1.6):
                s.blok("Gong sznur", (x, ym - 0.7, 0), (0.3, 1.6, 0.3), "tusz")
            yc = ym - 1.5 - 5.0
            s.walec("Gong", (0, yc, 0.05), 5.0, 0.6, "zloto", os="z")
            s.walec("Gong podkładka", (0, yc, -0.35), 5.5, 0.4, "tusz", os="z")
            s.walec("Gong guz", (0, yc, 0.45), 1.7, 0.4, cien(s, "zloto", 0.8), os="z")
            # pałka oparta o prawy słup
            with s.uklad(pos=(4.2, 0, 1.2), obrot=(0, 0, 14)):
                s.blok("Gong pałka", (0, 3.4, 0), (0.6, 6.8, 0.6), "drewno_jasne", "Wood")
                s.blok("Gong pałka głowa", (0, 7.2, 0), (1.9, 1.9, 1.9), KOD, "Fabric", rot=(0, 20, 0))


# --------------------------------------------------------------------------- znaki miasteczka i rekwizyty
def _znaki_i_rekwizyty(s, rnd):
    with _na_luku(s, SEGMENTY[1][0], R + GRUB / 2.0):          # L2: wypadnięty klocek
        zestaw.wypadniety_klocek(s, (1.5, 3.4, 0.0), (2.6, 0, 2.2), KAMIEN, obrot_klocka=24)
    with _na_luku(s, SEGMENTY[4][0], R + GRUB / 2.0):          # R2: łata
        zestaw.lata(s, (-1.0, 7.8, 0.0), 2.8, 2.3, "dach_twierdza", przechyl=-8)
    with _na_luku(s, SEGMENTY[0][0], R + GRUB / 2.0):          # L3: łata
        zestaw.lata(s, (0.8, 5.0, 0.0), 2.4, 2.1, "pomarancz", przechyl=9)
    # trójka przy lewym filarze: skrzynia, beczka z wodą, kamień
    zestaw.skrzynia(s, (-15.6, 0, 11.6), ry=24, dl=4.0, a=3.4, przechyl=8)
    zestaw.beczka(s, (-12.2, 0, 13.9), "woda", przechyl=(0, -7))
    zestaw.kamien(s, (-17.6, 0, 14.3), rnd, rozmiar=2.2, dwa=False)
