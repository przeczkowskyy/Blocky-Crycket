# -*- coding: utf-8 -*-
"""Brama miejska z murem — mapa v2 „Krzywe Miasteczko” (PROJEKT.md, karta 5.10). Status: propozycja, nie kanon.

Krawędź świata i rama ulicy Bramnej. Dwie wieże nie do pary rozchylone na zewnątrz jak ramiona: lewa kwadratowa
(trzon pionowy do 10,5, wyżej szersza „głowa” rz +6° pod ostrym dachem-ostrosłupem `dach_brama`), prawa okrągła
(głowa rz −5° pod stożkiem-gwiazdą). Między nimi ganek straży: kamienna podłoga na 14 (prześwit 14 na całej szerokości
przejścia 16), szachulcowe skrzydła z nawisem ku miastu, dach-czapa 30°. Szyld: wielki złoty dzwon alarmowy w ciemnej
wnęce ganku, nad samym przejściem. Żart: z okna prawej wieży wystają dwa wielkie buty śpiącego strażnika, na parapecie
jego hełm z piórem; na dole czeka pusta ławka i oparta o wieżę włócznia. Echo: krata podniesiona krzywo (lewa strona
niżej o 1,5, dół ≥ 14) — widać jej zęby pod nawisem ganku. Po bokach odcinki muru (korpus 4 × 14, rant tusz, blanki).

Układ lokalny: (0, 0, 0) = środek działki 46 × 14 na ziemi, front (ku miastu) = +Z, tył działki (z = −7) przylega do
lica muru miejskiego (oś muru generatora leży ok. z = −9,35).
Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/brama_miejska.py --wyj <folder> --szer 1000
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "BramaMiejska"
OBRYS = (46, 14)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 27                    # czubek dachu lewej wieży
BUDZET = 250
INTERAKCJA = (0.0, 11.0)         # przed przejściem — zapas na przyszłe wyjście do krain
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

KAMIEN, COKOL, TYNK, DACH, BELKA = "kamien_cieply", "kamien_cokol", "tynk_krem", "dach_brama", "drewno_ciemne"

ZT, FT = -1.5, 3.0               # środek wież w z i lico ich frontu
H0 = 10.5                        # pionowy trzon wież (przykazanie 3: dolne 10 studów proste)
PRZ = 14.0                       # prześwit przejścia = spód podłogi ganku
YP = 15.0                        # wierzch podłogi ganku
YN = 17.8                        # spód nawisu (skrzydeł ganku)
YG = 20.6                        # górna krawędź ścian ganku
ZG0, ZG1 = -3.4, 4.6             # ganek: tył i lico nawisu
ZW = -0.6                        # lico wnęki dzwonu (front tylnej bryły ganku)
ZPF = 1.6                        # lico frontu podłogi
ZK = 2.2                         # płaszczyzna kraty (środek)
WN = 4.4                         # połowa szerokości wnęki dzwonu
XL, XP = -10.3, 10.1             # zasięg ganku w x (wchodzi w obie wieże)
DZ = (0.0, 3.4)                  # dzwon: (x, z) osi
KRATA_KAT = math.degrees(math.atan2(1.5, 16.0))   # 5,4° — lewa strona niżej o 1,5 na 16 studach


def buduj(s, rnd):
    _przejscie(s)
    _wieza_lewa(s)
    _wieza_prawa(s)
    _mury(s)
    _ganek(s)
    _krata(s)
    with s.cechy(kolizja=False):
        _dzwon(s)
    _rekwizyty(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- przejście
def _przejscie(s):
    """Bruk w przejściu z dwiema koleinami — droga wyraźnie „wychodzi” za mur."""
    s.blok("Przejście bruk", (0, 0.15, 0), (16.0, 0.2, 14.0), "bruk_ciemny")
    with s.cechy(kolizja=False, cien=False):
        for x in (-2.6, 2.9):
            s.blok("Przejście koleina", (x, 0.25, 0), (1.3, 0.2, 13.6), cien(s, "bruk_ciemny", 0.85))


# --------------------------------------------------------------------------- lewa wieża (kwadratowa)
def _wieza_lewa(s):
    cx = -13.0
    s.blok("Wieża L cokół", (cx, 0.75, ZT), (9.8, 1.5, 9.8), COKOL, "Cobblestone")
    s.blok("Wieża L trzon", (cx, (H0 + 0.3) / 2.0, ZT), (9.0, H0 - 0.3, 9.0), KAMIEN)
    with s.cechy(kolizja=False):
        s.blok("Wieża L cokół rant", (cx, 1.7, ZT), (10.0, 0.4, 10.0), "tusz")
        s.blok("Wieża L gzyms", (cx, H0 + 0.1, ZT), (9.8, 0.8, 9.8), "tusz")
        # strzelnica w trzonie (front) i znak miasteczka: wypadnięty klocek
        s.blok("Wieża L strzelnica", (cx - 1.8, 6.0, FT + 0.1), (0.8, 3.2, 0.3), "tusz")
        zestaw.wypadniety_klocek(s, (cx + 2.4, 3.2, FT), (cx + 3.6, 0, FT + 1.1), KAMIEN, obrot_klocka=24)
        # latarnia na wysięgniku przy przejściu (front w cieniu — ciepłe światło przy wejściu)
        _latarnia_scienna(s, (cx + 3.4, 9.0, FT))
    # głowa wieży: szersza, przechylona na zewnątrz (rz +6) i skręcona (ry +5)
    with s.uklad(pos=(cx - 0.8, H0, ZT), obrot=(0, 5, 6)):
        W1, H1 = 9.8, 10.0
        s.blok("Wieża L głowa", (0, H1 / 2.0 - 0.4, 0), (W1, H1 + 0.8, W1), KAMIEN)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Wieża L narożnik", (sx * (W1 / 2.0 - 0.25), H1 / 2.0, sz * (W1 / 2.0 - 0.25)),
                           (1.3, H1 - 0.4, 1.3), "tusz")
            s.blok("Wieża L wieniec", (0, H1 + 0.1, 0), (W1 + 0.8, 0.8, W1 + 0.8), "tusz")
            zestaw.okno(s, (-1.3, 4.6, W1 / 2.0), 2.4, 3.2, ksztalt="luk", przechyl=-6)
            zestaw.okno(s, (1.6, 5.2, -W1 / 2.0), 2.2, 2.6, przechyl=7, swiatlo="woda_gleboka", ry=180, tanie=True)
            # dach-ostrosłup (smukły „szpic”, 48°) w kontrze (rz −4 względem głowy), skręcony o 9°
            with s.uklad(pos=(0, H1 + 0.3, 0), obrot=(0, 9, -4)):
                s.ostroslup("Wieża L dach", (0, 0, 0), 5.6, 5.6, 5.8, DACH)
                s.blok("Wieża L okap", (0, 0.05, 0), (11.8, 0.4, 11.8), "tusz")
                s.blok("Wieża L gałka", (0, 5.55, 0), (0.9, 0.9, 0.9), "zloto", rot=(45, 0, 45))


def _latarnia_scienna(s, pos):
    """Latarnia na wysięgniku z lica ściany (pos = punkt mocowania na licu, +Z na zewnątrz). 5 części."""
    x, y, z = pos
    s.blok("Latarnia wysięgnik", (x, y, z + 0.9), (0.4, 0.4, 1.8), "tusz")
    s.blok("Latarnia daszek", (x, y - 0.6, z + 1.7), (1.8, 0.5, 1.8), "tusz", rot=(0, 45, 0))
    with s.cechy(cien=False):
        s.blok("Latarnia światło", (x, y - 1.7, z + 1.7), (1.2, 1.6, 1.2), "neon_okno", "Neon")
    s.blok("Latarnia spód", (x, y - 2.7, z + 1.7), (1.5, 0.4, 1.5), "tusz", rot=(0, 45, 0))
    s.blok("Latarnia hak", (x, y - 0.1, z + 1.7), (0.3, 0.6, 0.3), "tusz")


# --------------------------------------------------------------------------- prawa wieża (okrągła)
def _wieza_prawa(s):
    cx, r0 = 13.0, 4.5
    s.walec("Wieża P cokół", (cx, 0.75, ZT), r0 + 0.4, 1.5, COKOL, "Cobblestone")
    s.walec("Wieża P trzon", (cx, H0 / 2.0, ZT), r0, H0, KAMIEN)
    with s.cechy(kolizja=False):
        s.walec("Wieża P cokół rant", (cx, 1.7, ZT), r0 + 0.45, 0.4, "tusz")
        s.walec("Wieża P gzyms", (cx, H0 + 0.1, ZT), r0 + 0.4, 0.8, "tusz")
        s.blok("Wieża P strzelnica", (cx + 1.2, 5.4, ZT + r0 - 0.1), (0.8, 3.0, 0.6), "tusz")
    with s.uklad(pos=(cx + 0.6, H0, ZT), obrot=(0, -6, -5)):
        r1, H1 = 4.8, 7.5
        s.walec("Wieża P głowa", (0, H1 / 2.0 - 0.2, 0), r1, H1 + 0.4, KAMIEN)
        with s.cechy(kolizja=False):
            s.walec("Wieża P wieniec", (0, H1 + 0.15, 0), r1 + 0.5, 0.7, "tusz")
            _okno_strazy(s, 28.0, 3.4, r1)
            # stożek „gwiazda”: dwa ostrosłupy obrócone o 45°, drugi o 0,05 wyżej, w dwóch tonach; w kontrze rz +4
            with s.uklad(pos=(0, H1 + 0.5, 0), obrot=(0, 0, 4)):
                s.ostroslup("Wieża P stożek", (0, 0, 0), 4.7, 4.7, 5.0, DACH)
                with s.uklad(obrot=(0, 45, 0)):
                    s.ostroslup("Wieża P stożek", (0, 0.05, 0), 4.7, 4.7, 5.0, cien(s, DACH, 0.8))
                zestaw.choragiewka_duetu(s, (0, 4.3, 0), "rycerz", ry=-20, przechyl=-12)
            s.blok("Wieża P strzelnica tył", (0.6, 3.6, -r1 + 0.15), (0.8, 2.6, 0.6), "tusz")


def _okno_strazy(s, kat, y, r):
    """Okno prawej wieży na licu walca o promieniu r, obrócone o `kat`° od frontu ku prawej (buty nie wiszą nad
    przejściem): ciepłe światło, z którego wystają dwa wielkie buty śpiącego strażnika (podeszwy do miasta, czubki
    w górę), na parapecie jego hełm z piórem."""
    a = math.radians(kat)
    with s.uklad(pos=(r * math.sin(a), y, r * math.cos(a)), obrot=(0, kat, 0)):
        s.blok("Okno straży rama", (0, 0, -0.55), (6.2, 5.0, 1.8), "tusz")
        with s.cechy(cien=False):
            s.blok("Okno straży światło", (0, 0, 0.4), (5.0, 3.8, 0.3), "neon_okno", "Neon")
        s.blok("Okno straży parapet", (1.2, -2.75, 0.55), (8.4, 0.6, 1.8), "drewno_jasne")
        s.blok("Okno straży wspornik", (4.6, -3.35, -1.0), (0.7, 0.7, 3.4), BELKA, "Wood")
        # buty: cholewa poziomo z okna, stopa pionowo (czubek w górę), ciemna podeszwa z obcasem, jasny mankiet;
        # w lewej podeszwie dziura, przez którą widać skarpetę
        # nogi wyciągnięte prosto, stopy opadły na boki (V): pięty razem, czubki osobno — nie jak okiennice
        for i, (bx, by, ry, rz) in enumerate(((-1.25, -1.3, -6, 24), (1.25, -1.1, 7, -20))):
            with s.uklad(pos=(bx, by, 0.4), obrot=(-6, ry, rz)):
                s.blok("But cholewa", (0, 0, 1.1), (2.0, 2.0, 2.4), BELKA)
                s.blok("But mankiet", (0, 0, 0.3), (2.4, 2.4, 0.6), "drewno_jasne")
                s.blok("But stopa", (0, 1.0, 3.2), (2.8, 3.6, 1.8), BELKA)
                s.walec("But czubek", (0, 2.8, 3.2), 1.4, 1.8, BELKA, os="z")
                s.blok("But podeszwa", (0, 0.9, 4.3), (3.0, 3.4, 0.4), "tusz")
                s.walec("But podeszwa", (0, 2.6, 4.3), 1.5, 0.4, "tusz", os="z")
                s.blok("But obcas", (0, -0.3, 4.75), (2.4, 1.2, 0.6), "tusz")
                if i == 0:
                    with s.cechy(cien=False):
                        s.blok("But dziura", (0.3, 1.9, 4.6), (1.1, 1.1, 0.2), "biel", rot=(0, 0, 12))
        # hełm strażnika na parapecie: rondo, dzwon, kopułka; pióro z dwóch łamanych segmentów
        with s.uklad(pos=(4.3, -2.45 + 0.3 + 0.2, 0.9), obrot=(0, 20, -14)):
            s.walec("Hełm rondo", (0, 0.0, 0), 1.75, 0.35, "tynk_blekit")
            s.walec("Hełm dzwon", (0, 0.75, 0), 1.2, 1.3, "tynk_blekit")
            s.kula("Hełm kopułka", (0, 1.35, 0), 2.4, "tynk_blekit")
            with s.cechy(cien=False):
                zestaw.lamana(s, "Hełm pióro", [(1.6, 0.6, 28), (1.8, 0.5, 30)], DACH, start=(0.2, 2.2), z=0.0)


# --------------------------------------------------------------------------- mury
def _mury(s):
    """Odcinki muru wg wzorca 4.3: korpus 4 × 14 z tyłu działki (z −7…−3), skarpa u stopy od miasta, rant tusz na 14,
    blanki 2 × 2 (co drugi +0,3 i w cieniu). Za wieżami mur biegnie dalej do krawędzi przejścia (cieńszy, bez blanków)."""
    zc, d = -5.0, 4.0
    for zn, x0, x1 in ((-1, -23.0, -17.2), (1, 17.0, 23.0)):
        L, xc = x1 - x0, (x0 + x1) / 2.0
        s.blok("Mur korpus", (xc, 6.85, zc), (L, 14.3, d), KAMIEN)
        s.klin("Mur skarpa", (xc, 1.5, zc + d / 2.0 + 0.6), (L, 3.0, 1.2), COKOL, rot=(0, 180, 0))
        with s.cechy(kolizja=False):
            s.blok("Mur rant", (xc, 14.3, zc), (L + 0.1, 0.6, d + 0.5), "tusz")
            # blanki od krawędzi działki do wieży
            xs = [x1 - 1.0 - 3.6 * i for i in range(2)] if zn > 0 else [x0 + 1.0 + 3.6 * i for i in range(2)]
            for i, x in enumerate(xs):
                h = 2.0 + 0.3 * (i % 2)
                s.blok("Mur blank", (x, 14.6 + h / 2.0, zc), (2.0, h, d - 0.4), KAMIEN if i % 2 == 0 else cien(s, KAMIEN))
    # za wieżami: mur do krawędzi przejścia (widać go od strony pól)
    for x0, x1 in ((-17.3, -8.6), (8.6, 17.1)):
        L, xc = x1 - x0, (x0 + x1) / 2.0
        s.blok("Mur za wieżą", (xc, 6.85, -6.3), (L, 14.3, 1.4), KAMIEN)
        with s.cechy(kolizja=False):
            s.blok("Mur za wieżą rant", (xc, 14.4, -6.3), (L + 0.1, 0.6, 1.9), "tusz")


# --------------------------------------------------------------------------- ganek straży
def _ganek(s):
    # podłoga = strop przejścia: trzy płyty (wnęka na dzwon w środku), spód dokładnie na 14
    hp = YP - PRZ
    for x0, x1, z0, z1 in ((XL, -WN, -6.9, ZPF), (WN, XP, -6.9, ZPF), (-WN, WN, -6.9, -0.8)):
        s.blok("Ganek podłoga", ((x0 + x1) / 2.0, PRZ + hp / 2.0, (z0 + z1) / 2.0), (x1 - x0, hp, z1 - z0), KAMIEN)
    with s.cechy(kolizja=False):
        for x0, x1 in ((XL + 0.4, -WN - 0.1), (WN + 0.1, XP - 0.4)):
            s.blok("Ganek podłoga rant", ((x0 + x1) / 2.0, PRZ + 0.4, ZPF + 0.15), (x1 - x0, 0.8, 0.3), "tusz")
        s.blok("Ganek podłoga rant tył", (0, PRZ + 0.4, -7.05), (2 * 8.4, 0.8, 0.3), "tusz")
    # tylna bryła ganku (od wnęki do tyłu)
    s.blok("Ganek bryła", ((XL + XP) / 2.0, (YP + YG) / 2.0, (ZG0 + ZW) / 2.0), (XP - XL, YG - YP, ZW - ZG0), TYNK)
    with s.cechy(kolizja=False):
        # ciemna wnęka dzwonu (działa jak podkładka pod złoty dzwon)
        s.blok("Ganek wnęka", (0, (YP + YG) / 2.0, ZW + 0.15), (2 * WN, YG - YP, 0.3), "tusz")
        # dolny pas za kratą (cień pod nawisem) i skrzydła z nawisem ku miastu
        for zn, x0, x1 in ((-1, XL, -WN), (1, WN, XP)):
            xc, L = (x0 + x1) / 2.0, x1 - x0
            s.blok("Ganek pas cienia", (xc, (YP + YN) / 2.0, (ZW + 1.3) / 2.0), (L, YN - YP, 1.3 - ZW), cien(s, TYNK, 0.78))
    for zn, x0, x1 in ((-1, XL, -WN), (1, WN, XP)):
        xc, L = (x0 + x1) / 2.0, x1 - x0
        s.blok("Ganek skrzydło", (xc, (YN + YG) / 2.0, (ZW + ZG1) / 2.0), (L, YG - YN, ZG1 - ZW), TYNK)
        with s.cechy(kolizja=False):
            s.blok("Ganek belka stropowa", (xc, YN + 0.2, ZG1 + 0.2), (L, 0.8, 0.5), "tusz")
            s.blok("Ganek słup", (zn * (WN + 0.35), (YN + YG) / 2.0 + 0.1, ZG1 + 0.25), (0.9, YG - YN + 0.2, 0.7), BELKA, "Wood")
            # wspornik pod nawisem przy wieży
            xw = zn * 9.3
            s.blok("Ganek wspornik", (xw, YN - 0.7, (1.3 + ZG1) / 2.0 + 0.2), (0.9, 1.4, ZG1 - 1.3 + 0.4), BELKA, "Wood")
    with s.cechy(kolizja=False):
        # szachulec: każde skrzydło inaczej (asymetria)
        yb = YN + 0.6
        s.belka("Ganek zastrzał", (-9.0, yb, ZG1 + 0.15), (-5.6, YG - 0.4, ZG1 + 0.15), 0.8, BELKA, "Wood", 0.3)
        s.blok("Ganek rygiel", (-7.3, YN + 1.6, ZG1 + 0.1), (5.9, 0.7, 0.3), BELKA, "Wood")
        s.belka("Ganek zastrzał", (7.6, yb, ZG1 + 0.15), (9.4, YG - 0.4, ZG1 + 0.15), 0.8, BELKA, "Wood", 0.3)
        zestaw.lata(s, (6.2, YN + 1.4, ZG1), 2.2, 1.6, DACH, przechyl=-9)
        # tył ganku (widok od pól): dwa słupy, zastrzał, ciemne okienko
        for x in (-6.5, 4.0):
            s.blok("Ganek słup tył", (x, (YP + YG) / 2.0, ZG0 - 0.15), (0.9, YG - YP, 0.3), BELKA, "Wood")
        s.belka("Ganek zastrzał tył", (-6.0, YP + 0.6, ZG0 - 0.15), (0.5, YG - 0.6, ZG0 - 0.15), 0.8, BELKA, "Wood", 0.3)
        zestaw.okno(s, (6.8, YP + 3.2, ZG0), 2.0, 2.4, przechyl=-6, swiatlo="woda_gleboka", ry=180, tanie=True)
    # od pól: chodnik straży za gankiem z blankami (ciąg dalszy rantu muru)
    for i, x in enumerate((-6.6, -1.4, 3.9)):
        h = 1.8 + 0.3 * (i % 2)
        s.blok("Ganek blank", (x, YP + h / 2.0, -6.2), (2.0, h, 1.2), KAMIEN if i % 2 == 0 else cien(s, KAMIEN))
    # dach-czapa na ganku: połać frontowa 30°, tylna 42°, skręcony o 6° (lewy koniec okapu bardziej ku miastu)
    gl = ZG1 - ZG0
    with s.uklad(pos=((XL + XP) / 2.0, YG, (ZG0 + ZG1) / 2.0), obrot=(0, -6, 0)):
        p, ok = 0.66, 1.8
        wys = (p * gl + ok) * math.tan(math.radians(30))
        info = zestaw.dach_czapa(s, XP - XL, gl, wys, DACH, okap=ok, okap_bok=0.6, podzial=p)
        # rura piecyka strażnicy na tylnej połaci (ktoś tu mieszka) — łamie długą kalenicę
        zt = info["z_kalenicy"] - 1.4
        yt = wys - 1.4 * math.tan(math.radians(info["kat_tyl"])) - 0.6
        zestaw.komin(s, (5.6, yt, zt), segmenty=((1.9, 1.0, 9.0), (1.4, 0.9, -13.0)), kolor=("metal_ciemny", None),
                     mat="SmoothPlastic", dym_n=2, dym_skala=0.6)


def _krata(s):
    """Krata podniesiona krzywo w płaszczyźnie przed podłogą ganku: lewa strona niżej o 1,5, zęby ≥ 14. Górna część
    chowa się w nawisie skrzydeł; za dzwonem krata jest przerwana (i tak jej tam nie widać)."""
    with s.uklad(pos=(0, PRZ + 0.80, ZK), obrot=(0, 0, KRATA_KAT)), s.cechy(kolizja=False):
        for zn in (-1, 1):
            for x in (4.75, 6.5, 8.25):
                s.blok("Krata pręt", (zn * x, 2.75, 0), (0.6, 4.1, 0.4), "metal_ciemny")
                s.blok("Krata ząb", (zn * x, 0.72, 0), (0.75, 0.75, 0.4), "metal_ciemny", rot=(0, 0, 45))
            for y in (2.2, 3.6):
                s.blok("Krata poprzeczka", (zn * 6.6, y, 0.25), (4.3, 0.5, 0.3), "metal_ciemny")


# --------------------------------------------------------------------------- dzwon (szyld)
def _dzwon(s):
    """Dzwon alarmowy Ø 8 × 8 (`zloto`) w ciemnej wnęce ganku: warga z ciemnym pierścieniem, korpus, bark, korona
    na jarzmie; serce z tuszu; spód 14,3 (≥ 14), środek ok. 17,3. Lekko rozkołysany (rz 7°)."""
    x, z = DZ
    with s.uklad(pos=(x, YG - 0.6, z)):
        s.blok("Dzwon jarzmo", (0, 0, 0), (2 * WN + 1.6, 0.8, 0.9), BELKA, "Wood")
    with s.uklad(pos=(x, YG - 0.8, z), obrot=(0, 0, 7)):        # obrót wokół osi zawieszenia
        y0 = 14.3 - (YG - 0.8) + 0.25                          # spód dzwonu w układzie zawieszenia
        s.walec("Dzwon pierścień", (0, y0 + 0.15, 0), 4.05, 0.3, "tusz")
        s.walec("Dzwon warga", (0, y0 + 0.75, 0), 4.0, 0.9, "zloto")
        s.walec("Dzwon korpus", (0, y0 + 2.8, 0), 3.3, 3.3, "zloto")
        s.walec("Dzwon bark", (0, y0 + 4.85, 0), 2.6, 0.9, "zloto")
        s.walec("Dzwon czapa", (0, y0 + 5.6, 0), 1.9, 0.7, cien(s, "zloto", 0.85))
        s.blok("Dzwon korona", (0, y0 + 6.3, 0), (1.4, 1.0, 1.0), "tusz")
        with s.cechy(cien=False):
            s.blok("Dzwon blik", (-1.6, y0 + 3.0, 2.95), (0.5, 2.0, 0.3), "biel", rot=(0, -25, -8))
            s.blok("Dzwon serce", (0.3, y0 + 0.65, 0), (1.3, 1.3, 1.3), "tusz", rot=(0, 30, 45))


# --------------------------------------------------------------------------- rekwizyty przy wejściu
def _rekwizyty(s, rnd):
    # lewa: pusta ławka strażnika i oparta o wieżę włócznia (strażnik śpi na górze)
    zestaw.lawka(s, (-13.4, 0, FT + 1.6), ry=-4, dl=5.6)
    with s.uklad(pos=(-17.2, 0, FT + 1.6), obrot=(-9, 0, -8)), s.cechy(kolizja=False):
        s.blok("Włócznia drzewce", (0, 5.6, 0), (0.5, 11.2, 0.5), "drewno", "Wood")
        s.blok("Włócznia grot obrys", (0, 12.1, -0.12), (1.6, 2.6, 0.3), "tusz", rot=(0, 0, 0))
        s.blok("Włócznia grot", (0, 12.3, 0.1), (1.2, 1.2, 0.4), "tynk_blekit", rot=(0, 0, 45))
        s.blok("Włócznia tuleja", (0, 11.1, 0), (0.8, 0.6, 0.8), "metal_ciemny")
    # prawa: trójka beczka – skrzynia – mała skrzynia przy okrągłej wieży
    zestaw.beczka(s, (16.6, 0, 4.7), "jablka", przechyl=(0, -6))
    zestaw.skrzynia(s, (12.0, 0, 4.9), ry=-10, dl=3.4, a=2.8, przechyl=7)
    zestaw.skrzynia(s, (19.8, 0, 4.4), ry=25, dl=2.4, a=2.2, przechyl=-9, kolor="drewno_jasne")
    # znak miasteczka: łata na murze po lewej
    zestaw.lata(s, (-20.4, 8.4, -3.0), 2.6, 2.2, "tynk_blekit", przechyl=10)
    zestaw.wypadniety_klocek(s, (20.6, 5.2, -3.0), (21.4, 0, -0.6), KAMIEN, obrot_klocka=-20)
