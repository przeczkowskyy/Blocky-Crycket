# -*- coding: utf-8 -*-
"""Koło fortuny (PROJEKT.md 5.12) — kiosk z darmowym kołem: prezenty za czas i aktywność, nie stawki.

Sylwetka: wielkie koło-słońce Ø 14 (z promieniami Ø ok. 19) na krzywym stojaku-trójkącie, nad nim dłoń wskazująca
palcem złote pole, przed nim niska lada z markizą w pasy `dach_kolo` / `biel`. Kod koloru: `dach_kolo` (magenta).
Żart: na ladzie przewrócone pudełko-prezent z uchylonym wieczkiem, z którego wytacza się jajko (zapowiedź peta).
Echo: chorągiewka `dach_kolo` na czubku stojaka. Zakaz: kości, karty, żetony, monety, dźwignie — nic z tego tu nie ma.

Układ lokalny: (0, 0, 0) = środek działki 18 × 14 na ziemi, front (lada, punkt interakcji) ku +Z.
Podgląd: python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/kolo_fortuny.py --wyj <folder>
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "KoloFortuny"
OBRYS = (18, 14)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 25                    # czubek chorągiewki
BUDZET = 170                     # karta; twardy sufit 213
INTERAKCJA = (0.0, 11.0)         # przed ladą, na osi koła
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

KOD = "dach_kolo"
POLA = (KOD, "tynk_blekit", "zloto", "pomarancz")      # pole nr 2 (na górze, pod palcem) = złoto
PROMIENIE = (3.0, 2.0, 3.0, 2.5, 2.0, 3.0, 2.5, 2.0)   # od 22,5° co 45°; boczne dolne krótkie (działka)


def buduj(s, rnd):
    zestaw._pal(s)
    # --- cokół stojaka (kolizja)
    s.blok("Cokół", (-0.2, 0.5, -3.8), (8.4, 1.0, 6.2), "kamien_cokol", "Cobblestone")
    with s.cechy(kolizja=False):
        s.blok("Cokół rant", (-0.2, 0.8, -3.8), (8.6, 0.3, 6.4), "tusz")
    # --- stojak + koło + dłoń: cały zestaw pochylony w prawo (karta: pochylenie −, słup rz −6°)
    with s.uklad(pos=(-0.3, 1.0, -3.8), obrot=(0, 0, -6)):
        _stojak(s)
        with s.uklad(pos=(0, 10.0, 1.9), obrot=(-8, 0, 0)):        # koło odchylone 8° do tyłu
            _kolo(s)
    # znak miasteczka: chorągiewka duetu (Kot-Mag) wbita w tylny lewy róg cokołu
    zestaw.choragiewka_duetu(s, (-3.9, 0.95, -6.4), "kot", ry=200, przechyl=12)
    # --- lada z markizą (kontra: skręt +4°, markiza rz +4°)
    with s.uklad(pos=(-0.3, 0, 4.4), obrot=(0, 4, 0)):
        _lada(s)
    # --- nagrody w trójce duży–średni–mały przy prawym końcu lady
    _prezenty(s)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


def _stojak(s):
    """Odwrócone V z dwóch nóg 1,5 (±12°) krzyżujących się na wysokości osi, poprzeczka, tylna zastrzałka
    i słup koła łamany do góry (za kołem), na nim wysięgnik z dłonią-wskaźnikiem i chorągiewka."""
    for zn in (-1, 1):                                           # nogi: stopa w x = ±2,2, krzyżują się na y ≈ 10
        L = 12.0
        a = math.radians(12)
        x0, y0 = zn * 2.2, -0.4
        s.blok("Noga stojaka", (x0 - zn * (L / 2) * math.sin(a), y0 + (L / 2) * math.cos(a), -0.2), (1.5, L, 1.5),
               "drewno", "Wood", rot=(0, 0, zn * 12))
    with s.cechy(kolizja=False):
        s.blok("Poprzeczka", (0, 3.0, 0.75), (4.6, 0.9, 0.5), "drewno_ciemne", "Wood", rot=(0, 0, 4))
        s.belka("Zastrzałka", (0, 9.8, -0.9), (0, -0.4, -2.4), 1.2, "drewno")
        xe, ye, kat = zestaw.lamana(s, "Słup koła", [(7.5, 1.2, 0), (5.0, 1.0, -8)], "drewno_ciemne", "Wood",
                                    start=(0.0, 8.5), z=-1.3)
        # dłoń przed kołem: palec wskazuje złote pole u góry, rękaw biegnie w górę-w prawo do wysięgnika
        kd = -32.0
        dx, dy = math.sin(math.radians(-kd)), math.cos(math.radians(kd))     # kierunek „w górę ręki”
        cx, cy, cz = 2.6, 19.2, 3.8
        s.belka("Wysięgnik", (xe, ye - 0.5, -1.3), (cx + 3.2 * dx, cy + 3.2 * dy, cz - 0.6), 0.8, "drewno_ciemne")
        with s.uklad(pos=(cx, cy, cz), obrot=(-8, 0, kd)):
            _dlon(s)
        # echo: chorągiewka koła na czubku słupa
        with s.uklad(pos=(xe, ye - 0.2, -1.3), obrot=(0, 0, kat + 10)), s.cechy(cien=False):
            s.blok("Chorągiewka maszt", (0, 1.3, 0), (0.4, 3.0, 0.4), "tusz")
            s.klin("Chorągiewka", (1.6, 2.3, 0), (0.3, 1.2, 2.8), KOD, "Fabric", rot=(0, -90, 0))
            s.klin("Chorągiewka", (1.6, 1.1, 0), (0.3, 1.2, 2.8), "biel", "Fabric", rot=(0, -90, 180))


def _dlon(s):
    """Komiksowa dłoń wskazująca (front +Z, palec ku lokalnemu −Y): rękaw w kolorze koła, biały mankiet, pięść,
    długi palec, kciuk na ukos przez pięść, płetwa tusz za całością. 8 części."""
    s.blok("Dłoń rękaw", (0, 2.75, 0), (2.6, 1.9, 2.2), KOD, "Fabric")
    s.blok("Dłoń mankiet", (0, 1.55, 0), (3.3, 0.9, 2.7), "biel")
    s.blok("Dłoń pięść", (0, 0, 0), (2.8, 2.4, 2.2), "tynk_krem")
    s.blok("Dłoń palec", (-0.8, -2.7, 0.2), (1.1, 3.4, 1.1), "tynk_krem")
    s.blok("Dłoń kciuk", (0.35, -0.55, 1.2), (0.9, 2.0, 0.6), "tynk_krem", rot=(0, 0, 62))
    with s.cechy(cien=False):
        s.blok("Dłoń paznokieć", (-0.8, -4.0, 0.8), (0.7, 0.6, 0.2), "biel")
    s.blok("Dłoń płetwa", (0, 1.3, -1.6), (3.9, 5.4, 0.4), "tusz")
    s.blok("Dłoń płetwa palca", (-0.8, -2.6, -0.65), (1.8, 4.2, 0.4), "tusz")


def _kolo(s):
    """Koło w płaszczyźnie XY, front +Z: podkładka tusz Ø 15, tarcza biel Ø 14, 8 pól, piasta, 8 promieni, żarówki."""
    s.walec("Koło podkładka", (0, 0, -0.5), 7.5, 0.6, "tusz", os="z")     # kolizję ma tylko tarcza z podkładką
    s.walec("Koło tarcza", (0, 0, 0.0), 7.0, 0.8, "biel", os="z")
    with s.cechy(kolizja=False):
        _kolo_detale(s)


def _kolo_detale(s):
    s.walec("Koło tył", (0, 0, -0.95), 6.5, 0.2, cien(s, KOD), os="z")
    for k in range(8):                                           # pola-szprychy 2,8 × 6,4, co drugie wyżej o 0,1
        a = 45.0 * k
        with s.uklad(obrot=(0, 0, a - 90)), s.cechy(cien=False):
            s.blok("Koło pole", (0, 3.6, 0.5 + 0.1 * (k % 2)), (2.8, 6.2, 0.3), POLA[k % 4])
    for k in range(8):                                           # promienie-romby za podkładką, 2 i 3 poza obręcz
        a = 22.5 + 45.0 * k
        wyst = PROMIENIE[k]                                      # ile wystaje poza obręcz (2–3, nierówno)
        bok = 1.4 + 0.6 * wyst
        d = bok * math.sqrt(2)
        r = 7.5 + wyst - d / 2.0
        with s.uklad(obrot=(0, 0, a - 90)):
            s.blok("Koło promień", (0, r, -0.5), (bok, bok, 0.4), KOD, rot=(0, 0, 45))
    with s.cechy(cien=False):
        for k in range(8):                                       # żarówki Neon na obręczy (bez górnej — tam palec)
            if k == 2:
                continue
            a = math.radians(45.0 * k)
            s.blok("Koło żarówka", (7.25 * math.cos(a), 7.25 * math.sin(a), 0.15), (1.0, 1.0, 0.7), "neon_okno", "Neon",
                   rot=(0, 0, 45))
        s.walec("Koło piasta obrys", (0, 0, 0.9), 2.1, 0.3, "tusz", os="z")
        s.walec("Koło piasta", (0, 0, 0.95), 1.5, 1.0, "zloto", os="z")
        s.walec("Koło oś", (0, 0, 1.55), 0.55, 0.3, "tusz", os="z")
    zestaw.lata(s, (-3.6, -2.6, -1.05), 2.8, 2.2, "zloto", ry=180, przechyl=-9)    # łata na plecach koła
    for a in (70, 160):                                          # plecy: krzyż zastrzałów (tył nie jest gołym dyskiem)
        s.blok("Koło zastrzał", (0, 0, -1.3), (0.9, 12.4, 0.4), "drewno_ciemne", "Wood", rot=(0, 0, a - 90))


def _lada(s):
    """Lada 12 × 3 × 3,5 (front lokalnie z = +1,5) z ramą tusz, blatem, markizą 7 pasów na krzywych słupkach
    i żartem: przewrócony prezent z jajkiem."""
    s.blok("Lada", (0, 1.75, 0), (12.0, 3.5, 3.0), "drewno_jasne", "WoodPlanks")
    with s.cechy(kolizja=False):
        s.blok("Lada blat", (0, 3.7, 0.1), (12.8, 0.4, 3.6), "drewno")
        s.ramka("Lada rama", (0, 1.75, 1.6), 10.6, 2.6, "tusz", 0.5, 0.3)
        # lada jak wielki prezent: krzyż wstążek złota z kokardą na skrzyżowaniu
        s.blok("Lada wstążka", (2.6, 1.75, 1.62), (1.0, 2.6, 0.3), "zloto")
        s.blok("Lada wstążka", (0, 1.75, 1.62), (10.6, 0.8, 0.3), "zloto")
        for k in (30, -30):
            s.blok("Lada kokarda", (2.6 + (0.85 if k > 0 else -0.85), 1.95, 1.95), (1.6, 1.0, 0.4), "zloto", rot=(0, 0, k))
        s.blok("Lada kokarda węzeł", (2.6, 1.75, 2.05), (0.8, 0.8, 0.4), cien(s, "zloto"))
        # znak miasteczka: wypadnięty klocek z lewego boku lady
        zestaw.wypadniety_klocek(s, (-6.0, 1.9, -0.2), (-7.0, 0, 0.4), "drewno_jasne", ry=-90, obrot_klocka=24)
        # markiza 7 pasów pod 11°, przesunięta w prawo (lewy koniec lady wolny — tam żart), rz +4° w kontrze do koła
        n, Wm, Dm, mx, my = 7, 11.2, 4.8, 1.0, 8.7
        pas = Wm / n
        rx, rz = 11.0, 4.0
        for zn, xs, k1, k2 in ((-1, mx - Wm / 2.0 + 0.6, 5, -10), (1, mx + Wm / 2.0 - 0.6, -4, 9)):
            zl = -1.9                                            # słupki za ladą
            cel = (my + math.sin(math.radians(rx)) * (-0.5 - zl)
                   + math.sin(math.radians(rz)) * (xs - mx) - 0.05)
            L1 = 4.6
            L2 = (cel - L1 * math.cos(math.radians(k1))) / math.cos(math.radians(k1 + k2))
            zestaw.lamana(s, "Słupek markizy", [(L1, 0.7, k1), (L2, 0.6, k2)], "drewno_ciemne", "Wood",
                          start=(xs, 0.0), z=zl)
        with s.uklad(pos=(mx, my, -0.5), obrot=(rx, 0, rz)):
            for i in range(n):
                x = -Wm / 2.0 + pas * (i + 0.5)
                kol = KOD if i % 2 == 0 else "biel"
                s.blok("Markiza pas", (x, 0.06 * (i % 2), 0), (pas, 0.4, Dm), kol, "Fabric")
                with s.cechy(cien=False):
                    s.blok("Markiza ząbek", (x, -0.55, Dm / 2.0 + 0.05), (pas - 0.35, 0.9, 0.3), kol, "Fabric")
            s.blok("Markiza rant", (0, -0.25, 0), (Wm + 0.6, 0.25, Dm + 0.6), "tusz")
            # łata z fastrygą na markizie (wierzch = lokalne +Y)
            with s.uklad(pos=(-1.6, 0.26, -0.6), obrot=(-90, 0, 0)):
                zestaw.lata(s, (0, 0, 0), 2.4, 1.8, "tynk_blekit", przechyl=10)
        # żart: przewrócony prezent na lewym końcu blatu, z uchylonego wieczka wytacza się jajko
        with s.uklad(pos=(-3.3, 3.9 + 1.68, -0.4), obrot=(0, -78, 10)):
            _prezent_z_jajkiem(s)


def _prezent_z_jajkiem(s):
    """Pudełko 3 × 3 × 3 leżące na boku: otwór ku lokalnemu +Z, wieczko na zawiasie przy górnej krawędzi otworu."""
    s.blok("Prezent", (0, 0, 0), (3.0, 3.0, 3.0), KOD)
    with s.cechy(cien=False):
        s.blok("Prezent wnętrze", (0, 0, 1.45), (2.5, 2.5, 0.3), "tusz")
        s.blok("Prezent wstążka", (0, 0, -0.1), (0.7, 3.2, 3.0), "zloto")
        s.blok("Prezent wstążka", (0, 0, -0.1), (3.2, 0.7, 3.0), "zloto")
        with s.uklad(pos=(-1.6, 0, 1.6), obrot=(0, -140, 0)):          # wieczko na zawiasie przy lewej krawędzi
            s.blok("Prezent wieczko", (1.7, 0, 0.25), (3.4, 3.4, 0.5), KOD)
            s.blok("Prezent wieczko wstążka", (1.7, 0, 0.55), (3.5, 0.7, 0.2), "zloto")
        for k in (30, -30):
            s.blok("Prezent kokarda", ((0.6 if k > 0 else -0.6), 1.9, -0.3), (1.4, 0.8, 0.6), "zloto", rot=(0, 0, k))
        s.kula("Jajko", (0.5, -0.25, 2.05), 2.5, "biel")
        s.blok("Jajko kropka", (0.0, 0.25, 3.15), (0.6, 0.6, 0.3), "dach_wylegarnia", rot=(0, 0, 20))
        s.blok("Jajko kropka", (1.1, -0.7, 3.1), (0.5, 0.5, 0.3), "dach_wylegarnia", rot=(0, 0, -15))


def _prezenty(s):
    """Trójka nagród: duży, średni, mały (na dużym) — każdy z krzyżem wstążek. Bez kolizji."""
    with s.cechy(kolizja=False):
        for pos, a, kol, wst, ry, rz in (((6.9, 0, 2.4), 3.2, "zloto", KOD, 14, 0),
                                         ((6.9, 0, -0.9), 2.4, "tynk_blekit", KOD, -20, 0),
                                         ((6.8, 3.2, 2.5), 1.8, "pomarancz", "biel", 40, 8)):
            with s.uklad(pos=pos, obrot=(0, ry, rz)):
                s.blok("Nagroda", (0, a / 2.0, 0), (a, a, a), kol)
                with s.cechy(cien=False):
                    s.blok("Nagroda wstążka", (0, a / 2.0 + 0.05, 0), (0.6, a + 0.2, a + 0.2), wst)
                    s.blok("Nagroda wstążka", (0, a / 2.0 + 0.05, 0), (a + 0.2, a + 0.2, 0.6), wst)
