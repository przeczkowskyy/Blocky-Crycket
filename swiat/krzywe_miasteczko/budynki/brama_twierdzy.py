# -*- coding: utf-8 -*-
"""Brama do twierdzy gracza mapy v2 „Krzywe Miasteczko” (PROJEKT.md, karta 5.7).

Brama z rozłożonymi „ramionami”: dwie baszty nie do pary pochylone na zewnątrz — lewa okrągła (3 walce zwężane
schodkowo, gzymsy tusz), prawa kwadratowa zwężana ku górze — obie z blankami i bez dachów. Między nimi przejście
10 × 12 z łukiem z 9 klińców, w głębi złoty portal (Neon) z sylwetką twierdzy, krzywo podniesiona krata.
Szyld: drewniany żuraw na prawej baszcie z kamiennym klockiem na linie (zapowiedź budowania). Sztandar Rycerza
z łatą na lewej baszcie, złoty klucz na haku (echo) i żart: wycieraczka przed bramą twierdzy.

Konwencja (PROJEKT 5.0): (0, 0, 0) = środek działki na ziemi, front z wejściem ku +Z, działka x ∈ ±16, z ∈ ±9,
wys. ≤ 36; tył przy z = −9 (brama wbudowana w mur — mur dobudowuje generator).

Odstępstwa od karty (świadome):
- dolne 14 studów lewej i dolne 10 prawej baszty są pionowe (przykazanie 3 — po pochylonej ścianie postać weszłaby na
  mur); pochylenie zaczyna się nad dolnym gzymsem: lewa +6° i dalej +4° (razem 10° na szczycie), prawa −7°;
- lewa baszta: walce 14 / 10,5 / 7,5 zamiast 14 / 11 / 8 (blanki zmieściły się w wysokości 36);
- wysięgnik żurawia ma ok. 19 (w tym ogon z przeciwwagą 3): od masztu na prawej baszcie do miejsca nad przejściem jest
  ok. 15, bo maszt stoi nad prawą basztą, a klocek wisi nad lewą połową przejścia (nie zasłania kraty ani zwornika).

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/brama_twierdzy.py --wyj <folder> --szer 1000
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor  # noqa: E402
from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "BramaTwierdzy"
OBRYS = (32, 18)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 36
BUDZET = 280                     # twardy sufit 350
INTERAKCJA = (0.0, 13.0)         # 4 study przed krawędzią działki, na osi przejścia
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

KAMIEN, COKOL, KOD = "kamien_cieply", "kamien_cokol", "dach_twierdza"

# lewa baszta (okrągła) i prawa (kwadratowa) — środki z karty
LX, LZ, LR = -10.3, -2.0, (5.5, 4.75, 4.1)     # karta: −10,5; o 0,2 bliżej, żeby blanki zmieściły się w działce
LH = (14.0, 10.5, 7.5)
RX, RZ = 11.0, -2.0
# przejście i łuk
LUK_Y, LUK_R, LUK_G = 12.0, 5.0, 2.4      # środek łuku na wys. 12 (prosta część 12), promień wewn. 5, kliniec 2,4
Z_LICO = 1.0                               # lico kurtyny
Z_PORTAL = -1.05                           # płyta portalu (2 w głębi za licem)
KURT_TOP = 21.0
Z_TYL = -8.6                               # tył kurtyny (z rantem i strzelnicami do −8,9)


# --------------------------------------------------------------------------- układy liczone także „na papierze”
class _Rama:
    """Układ lokalny, który umie też przeliczać punkty do układu budynku (do lin, sztandaru i haka żurawia)."""

    def __init__(self, pos=(0.0, 0.0, 0.0), obrot=(0.0, 0.0, 0.0), rodzic=None):
        R = macierz_obrotu(*obrot)
        if rodzic is None:
            self.R, self.t = R, tuple(float(v) for v in pos)
        else:
            self.R = mnoz(rodzic.R, R)
            self.t = rodzic(pos)

    def __call__(self, p):
        v = razy_wektor(self.R, p)
        return (self.t[0] + v[0], self.t[1] + v[1], self.t[2] + v[2])

    def kierunek(self, d):
        return razy_wektor(self.R, d)

    def uklad(self, s):
        return s.uklad(pos=self.t, obrot=katy_z_macierzy(self.R))


L0 = _Rama((LX, 0.0, LZ))
L1 = _Rama((-0.35, LH[0], 0.0), (0, 0, 6), L0)         # każde piętro także przesunięte na zewnątrz
L2 = _Rama((-0.15, LH[1], 0.0), (0, 0, 4), L1)
T0 = _Rama((RX, 0.0, RZ))
T1 = _Rama((0.0, 10.0, 0.0), (0, 0, -7), T0)


def _na_walcu(r, kat, y, wysun=0.0):
    """Punkt na powierzchni walca (oś Y) pod kątem `kat` od +Z ku +X; zwraca (pos, ry) dla elementu ściennego."""
    a = math.radians(kat)
    return (math.sin(a) * (r + wysun), y, math.cos(a) * (r + wysun)), kat


def buduj(s, rnd):
    ciemny = cien(s, KAMIEN, 0.8)                              # kurtyna cofnięta = ciemniejsza (głębia bez światła)
    _kurtyna(s, ciemny)
    _luk_i_portal(s)
    _krata(s)
    _baszta_lewa(s, ciemny)
    _baszta_prawa(s, ciemny)
    _zuraw(s)
    _sztandar(s)
    _klucz(s)
    _wycieraczka(s)
    _znaki(s, rnd, ciemny)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- kurtyna (ściana z przejściem)
def _kurtyna(s, ciemny):
    zt = (Z_PORTAL - 0.25 + Z_TYL) / 2.0                       # bryła za portalem: z −8,6 … −1,3 (spody zagłębione)
    s.blok("Kurtyna tył", (0.5, (KURT_TOP - 0.3) / 2.0, zt), (17.0, KURT_TOP + 0.3, (Z_PORTAL - 0.25) - Z_TYL), ciemny)
    zf = (Z_LICO + Z_PORTAL - 0.25) / 2.0
    d = Z_LICO - (Z_PORTAL - 0.25)
    s.blok("Ościeże lewe", (-6.5, 8.35, zf), (3.0, 17.3, d), ciemny)
    s.blok("Ościeże prawe", (6.75, 8.35, zf), (3.5, 17.3, d), ciemny)
    s.blok("Kurtyna nad łukiem", (0.5, 18.9, zf), (17.0, 4.2, d), ciemny)
    s.blok("Próg", (0, 0.15, (Z_PORTAL + 1.7) / 2.0), (12.0, 0.5, 2.75), COKOL, "Cobblestone")
    with s.cechy(kolizja=False):
        for x in (-5.0, 5.0):                                  # tuszowe krawędzie otworu (0,2 przed licem)
            s.blok("Ościeże obrys", (x, 6.125, 0.6), (0.8, 12.55, 1.2), "tusz")
        s.blok("Kurtyna rant", (0.5, 20.85, 1.1), (16.0, 0.7, 0.5), "tusz")
        s.blok("Kurtyna rant tył", (0.5, 20.85, Z_TYL - 0.15), (16.0, 0.7, 0.5), "tusz")
        for i, x in enumerate((-6.2, -3.6, -1.0, 1.6, 4.2, 6.9)):   # blanki kurtyny, co drugi wyższy i ciemniejszy
            h = 1.6 + (0.25 if i % 2 else 0.0)
            s.blok("Kurtyna blanka", (x, KURT_TOP + h / 2.0, 0.45), (1.6, h, 1.3), KAMIEN if i % 2 == 0 else cien(s, KAMIEN))
        # ciosy na kurtynie i ciemne strzelnice z tyłu (tył też jest oglądany)
        with s.cechy(cien=False):
            for x, y, w in ((-4.2, 19.6, 2.2), (4.6, 18.2, 1.8), (6.1, 13.6, 1.2)):
                s.blok("Cios", (x, y, Z_LICO + 0.12), (w, 0.9, 0.3), KAMIEN)
            for x in (-3.0, 3.5):
                s.blok("Strzelnica tył", (x, 15.0, Z_TYL - 0.12), (0.9, 3.0, 0.3), "tusz")
        for x in (-7.6, 8.6):                                  # tylne narożniki kurtyny tuszem (tył też jest oglądany)
            s.blok("Kurtyna narożnik", (x, 10.3, Z_TYL + 0.2), (1.2, 20.6, 1.2), "tusz")


def _luk_i_portal(s):
    """Łuk z 9 klińców (co drugi głębszy o 0,2, zwornik złoty) na tuszowym pierścieniu i złoty portal w głębi 2."""
    n = 9
    rm = LUK_R + LUK_G / 2.0
    w = 2.0 * (LUK_R + LUK_G) * math.tan(math.pi / (2.0 * n)) * 1.02
    w_t = 2.0 * (LUK_R + LUK_G + 0.4) * math.tan(math.pi / (2.0 * n)) * 1.02
    z0 = Z_PORTAL + 0.05                                        # tył klińców tuż przed portalem
    with s.cechy(kolizja=False):
        for i in range(n):
            fi = math.pi * (i + 0.5) / n
            x, y = rm * math.cos(fi), LUK_Y + rm * math.sin(fi)
            rz = math.degrees(fi) - 90.0
            s.blok("Łuk obrys", (x, y, 0.575), (w_t, LUK_G + 0.8, 1.15), "tusz", rot=(0, 0, rz))
            if i == n // 2:
                zf = 2.0
                s.blok("Łuk zwornik", (0, LUK_Y + rm + LUK_G * 0.18, (z0 + zf) / 2.0), (w * 1.25, LUK_G * 1.36, zf - z0), "zloto")
            else:
                zf = 1.35 + (0.2 if i % 2 else 0.0)
                s.blok("Łuk kliniec", (x, y, (z0 + zf) / 2.0), (w, LUK_G, zf - z0), KAMIEN if i % 2 == 0 else cien(s, KAMIEN, 0.93),
                       rot=(0, 0, rz))
    # portal: płyta 10 × 12 + półkole, Neon; ma kolizję (za nim i tak jest mur)
    with s.cechy(cien=False):
        s.blok("Portal", (0, (LUK_Y - 0.2) / 2.0, Z_PORTAL), (10.4, LUK_Y + 0.2, 0.3), "neon_okno", "Neon")
        s.walec("Portal łuk", (0, LUK_Y, Z_PORTAL), LUK_R + 0.1, 0.3, "neon_okno", "Neon", os="z")
        # w portalu sylwetka twierdzy na wzgórzu (kolor Rycerza) — „za bramą jest twoja twierdza”
        with s.cechy(kolizja=False):
            zp = Z_PORTAL + 0.3
            s.blok("Portal wzgórze", (0.4, 1.5, zp), (10.2, 3.0, 0.25), "lisc", rot=(0, 0, 5))
            s.blok("Portal twierdza", (0.6, 4.0, zp + 0.05), (4.2, 3.6, 0.25), KOD)
            s.blok("Portal wieża", (-1.9, 5.0, zp + 0.1), (1.6, 5.6, 0.25), KOD)
            s.blok("Portal wieża", (3.0, 4.6, zp + 0.1), (1.4, 4.4, 0.25), KOD, rot=(0, 0, -6))
            s.blok("Portal chorągiewka", (-1.3, 8.3, zp + 0.1), (1.6, 0.9, 0.25), "czerwien", rot=(0, 0, 8))


def _krata(s):
    """Krata podniesiona krzywo: dolna krawędź (szpice) z lewej na 14,5, z prawej o 1,5 niżej (13,0)."""
    kat = -math.degrees(math.atan2(1.5, 10.0))
    with s.uklad(pos=(0, 13.75, -0.45), obrot=(0, 0, kat)), s.cechy(kolizja=False):
        for x in (-4.0, -2.0, 0.0, 2.0, 4.0):
            s.blok("Krata pręt", (x, 4.0, 0), (0.6, 6.4, 0.5), "metal_ciemny")
            with s.cechy(cien=False):
                s.blok("Krata szpic", (x, 0.55, 0), (0.75, 0.75, 0.45), "metal_ciemny", rot=(0, 0, 45))
        for y in (1.7, 4.3):
            s.blok("Krata poprzeczka", (0, y, 0.12), (10.6, 0.55, 0.4), "metal_ciemny")


# --------------------------------------------------------------------------- baszty
def _baszta_lewa(s, ciemny):
    """Okrągła: walce Ø 11 / 9,5 / 8,2, gzymsy tusz Ø +0,9, dół pionowy, wyżej +6° i +4° (razem 10° na zewnątrz)."""
    with L0.uklad(s):
        s.walec("Baszta L cokół", (0, 0.75, 0), LR[0] + 0.45, 1.5, COKOL, "Cobblestone", os="y")
        with s.cechy(kolizja=False):
            s.walec("Baszta L cokół rant", (0, 1.4, 0), LR[0] + 0.6, 0.4, "tusz", os="y")
        s.walec("Baszta L", (0, LH[0] / 2.0, 0), LR[0], LH[0], KAMIEN, os="y")
        with s.cechy(kolizja=False):
            s.walec("Baszta L gzyms", (0, LH[0], 0), LR[0] + 0.45, 0.7, "tusz", os="y")
            for kat, y, w in ((-62, 3.8, 2.2), (-25, 11.8, 1.8), (-150, 8.0, 2.4), (120, 5.5, 2.0)):
                pos, ry = _na_walcu(LR[0], kat, y, -0.12)
                s.blok("Cios", pos, (w, 0.9, 0.5), cien(s, KAMIEN, 0.8), rot=(0, ry, 0))
            pos, ry = _na_walcu(LR[0], -8, 8.6, -0.2)
            s.blok("Strzelnica", pos, (0.9, 3.0, 0.6), "tusz", rot=(0, ry, 0))
    with L1.uklad(s):
        zak = LR[1] * math.tan(math.radians(6)) + 0.05
        s.walec("Baszta L piętro", (0, (LH[1] - zak) / 2.0, 0), LR[1], LH[1] + zak, KAMIEN, os="y")
        with s.cechy(kolizja=False):
            s.walec("Baszta L gzyms", (0, LH[1], 0), LR[1] + 0.45, 0.7, "tusz", os="y")
            pos, ry = _na_walcu(LR[1], 28, 5.2, -0.2)
            zestaw.okno(s, pos, 3.0, ksztalt="okragle", przechyl=0, ry=ry)
            for kat, y, w in ((-40, 2.2, 2.0), (75, 8.2, 1.8), (175, 4.0, 2.2)):
                pos, ry = _na_walcu(LR[1], kat, y, -0.12)
                s.blok("Cios", pos, (w, 0.9, 0.5), cien(s, KAMIEN, 0.8), rot=(0, ry, 0))
            pos, ry = _na_walcu(LR[1], 180, 6.0, -0.2)
            s.blok("Strzelnica tył", pos, (0.9, 2.8, 0.6), "tusz", rot=(0, ry, 0))
    with L2.uklad(s):
        r = LR[2]
        zak = r * math.tan(math.radians(4)) + 0.05
        s.walec("Baszta L szczyt", (0, (LH[2] - zak) / 2.0, 0), r, LH[2] + zak, KAMIEN, os="y")
        with s.cechy(kolizja=False):
            s.walec("Baszta L głowica rant", (0, LH[2] + 0.1, 0), r + 1.1, 0.8, "tusz", os="y")
            s.walec("Baszta L głowica", (0, LH[2] + 0.85, 0), r + 0.8, 1.0, KAMIEN, os="y")
            yb = LH[2] + 1.35
            for i in range(8):
                kat = 22.5 + 45.0 * i
                h = 1.6 + (0.25 if i % 2 else 0.0)
                pos, ry = _na_walcu(r + 0.8, kat, yb + h / 2.0, -0.35)
                s.blok("Baszta L blanka", pos, (2.3, h, 1.0), KAMIEN if i % 2 == 0 else cien(s, KAMIEN), rot=(0, ry, 0))
            pos, ry = _na_walcu(r, 10, 3.6, -0.2)
            s.blok("Strzelnica", pos, (0.9, 2.6, 0.6), "tusz", rot=(0, ry, 0))


def _baszta_prawa(s, ciemny):
    """Kwadratowa 10 × 10: dół pionowy do 10, wyżej ostrosłup ścięty 10 → 8 pochylony −7°, blanki, bez dachu."""
    with T0.uklad(s):
        s.blok("Baszta P cokół", (0, 0.65, 0), (10.6, 1.7, 10.6), COKOL, "Cobblestone")
        with s.cechy(kolizja=False):
            s.blok("Baszta P cokół rant", (0, 1.4, 0), (10.8, 0.4, 10.8), "tusz")
        s.blok("Baszta P", (0, 4.95, 0), (10.0, 10.1, 10.0), KAMIEN)
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.blok("Baszta P narożnik", (sx * 4.7, 5.6, sz * 4.7), (1.2, 8.0, 1.2), "tusz")
            s.blok("Baszta P gzyms", (0, 10.1, 0), (11.2, 1.2, 11.2), "tusz")
            s.blok("Strzelnica", (1.2, 6.2, 5.12), (0.9, 3.2, 0.3), "tusz")
            s.blok("Strzelnica bok", (5.12, 6.0, -1.0), (0.3, 3.2, 0.9), "tusz")
            s.blok("Strzelnica tył", (-0.5, 6.0, -5.12), (0.9, 3.2, 0.3), "tusz")
            with s.cechy(cien=False):
                for x, y, z, w in ((-2.6, 3.4, 5.12, 2.2), (3.0, 8.4, 5.12, 1.8), (5.12, 3.0, 2.2, 2.0), (5.12, 8.0, -3.4, 2.2)):
                    if abs(z) > 5:
                        s.blok("Cios", (x, y, z), (w, 0.9, 0.3), cien(s, KAMIEN, 0.8))
                    else:
                        s.blok("Cios", (x, y, z), (0.3, 0.9, w), cien(s, KAMIEN, 0.8))
            zestaw.lata(s, (-3.0, 7.4, 5.0), 2.6, 2.2, KOD, przechyl=-9)
    h, a, t = 13.4, 4.0, 1.0
    with T1.uklad(s):
        _sciety(s, "Baszta P góra", (0, -0.4, 0), a, a, h, t, KAMIEN)
        y_top = h - 0.4
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                for sz in (-1, 1):
                    s.belka("Baszta P krawędź", (sx * (a + t), -0.4, sz * (a + t)), (sx * a, y_top, sz * a), 0.9, "tusz", "SmoothPlastic")
            s.blok("Baszta P gzyms", (0, y_top + 0.1, 0), (2 * a + 2.0, 0.7, 2 * a + 2.0), "tusz")
            s.blok("Baszta P głowica", (0, y_top + 1.25, 0), (2 * a + 1.4, 1.8, 2 * a + 1.4), KAMIEN)
            yb = y_top + 2.15
            i = 0
            for sx in (-1, 0, 1):
                for sz in (-1, 0, 1):
                    if (sx, sz) == (0, 0):
                        continue
                    hz = 1.6 + (0.25 if (sx + sz) % 2 else 0.0)
                    s.blok("Baszta P blanka", (sx * (a + 0.2), yb + hz / 2.0, sz * (a + 0.2)), (1.6, hz, 1.6),
                           KAMIEN if (sx + sz) % 2 == 0 else cien(s, KAMIEN))
                    i += 1
            # okno na pochylonym froncie (lico zwęża się o 1 na 13,4 → rx −4,3°)
            kat = -math.degrees(math.atan2(t, h))
            zc = a + t * (1 - 6.6 / h)
            with s.uklad(pos=(0.4, 6.2, zc), obrot=(kat, 0, 0)):
                zestaw.okno(s, (0, 0, 0), 2.6, 3.4, przechyl=-6, okiennica=KOD, strona_okiennicy=-1)
            zestaw.choragiewka_duetu(s, (2.6, yb, 2.4), "kot", ry=180, przechyl=-12)


def _sciety(s, nazwa, srodek_podstawy, a, b, h, t, kolor, mat="SmoothPlastic"):
    """Ostrosłup ścięty (przepisy.md 4.3): góra 2a × 2b, każda ściana rozszerza się ku dołowi o t. 9 części."""
    cx, y0, cz = srodek_podstawy
    y = y0 + h / 2.0
    s.blok(nazwa, (cx, y, cz), (2 * a, h, 2 * b), kolor, mat)
    s.klin(nazwa, (cx, y, cz + b + t / 2.0), (2 * a, h, t), kolor, mat, (0, 180, 0))
    s.klin(nazwa, (cx, y, cz - b - t / 2.0), (2 * a, h, t), kolor, mat, (0, 0, 0))
    s.klin(nazwa, (cx + a + t / 2.0, y, cz), (2 * b, h, t), kolor, mat, (0, -90, 0))
    s.klin(nazwa, (cx - a - t / 2.0, y, cz), (2 * b, h, t), kolor, mat, (0, 90, 0))
    s.naroznik(nazwa, (cx - a - t / 2.0, y, cz + b + t / 2.0), (t, h, t), kolor, mat, (0, 0, 0))
    s.naroznik(nazwa, (cx + a + t / 2.0, y, cz + b + t / 2.0), (t, h, t), kolor, mat, (0, 90, 0))
    s.naroznik(nazwa, (cx + a + t / 2.0, y, cz - b - t / 2.0), (t, h, t), kolor, mat, (0, 180, 0))
    s.naroznik(nazwa, (cx - a - t / 2.0, y, cz - b - t / 2.0), (t, h, t), kolor, mat, (0, 270, 0))


# --------------------------------------------------------------------------- szyld: żuraw z klockiem
def _zuraw(s):
    y_glow = 13.0 + 2.15                                        # wierzch głowicy prawej baszty (układ T1)
    mx, mz = -1.5, -1.0
    with s.cechy(kolizja=False):
        with T1.uklad(s):
            s.blok("Żuraw maszt", (mx, y_glow + 4.6, mz), (1.2, 9.2, 1.2), "drewno", "Wood")
            s.walec("Żuraw kołowrót", (mx + 1.6, y_glow + 1.1, mz), 0.6, 2.0, "drewno_jasne", os="z")
            s.blok("Żuraw korba", (mx + 1.6, y_glow + 1.1, mz + 1.25), (0.4, 1.8, 0.4), "tusz", rot=(0, 0, 30))
        p1 = T1((mx, y_glow + 6.6, mz))                         # mocowanie wysięgnika na maszcie
        top = T1((mx, y_glow + 9.0, mz))                        # czubek masztu
        p2 = (-3.3, p1[1] + 1.3, 3.6)                           # koniec wysięgnika: nad lewą połową przejścia
        dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
        dl = math.sqrt(dx * dx + dy * dy + dz * dz)
        u = (dx / dl, dy / dl, dz / dl)
        p0 = (p1[0] - 3.0 * u[0], p1[1] - 3.0 * u[1], p1[2] - 3.0 * u[2])
        s.belka("Żuraw wysięgnik", p0, p2, 1.0, "drewno", "Wood")
        s.blok("Żuraw przeciwwaga", (p0[0], p0[1] - 1.1, p0[2]), (1.8, 1.8, 1.8), COKOL, rot=(0, 20, 0))
        pz = T1((mx, y_glow + 2.4, mz))
        pb = (p1[0] + 0.33 * dx, p1[1] + 0.33 * dy - 0.4, p1[2] + 0.33 * dz)
        s.belka("Żuraw zastrzał", pz, pb, 0.7, "drewno_jasne", "Wood")
        with s.cechy(cien=False):
            s.belka("Żuraw cięgno", top, (p2[0], p2[1] + 0.4, p2[2]), 0.3, "tusz", "SmoothPlastic")
            y_hak = 20.3
            s.blok("Żuraw lina", (p2[0], (p2[1] - 0.45 + y_hak) / 2.0, p2[2]), (0.3, p2[1] - 0.45 - y_hak, 0.3), "tusz")
            s.blok("Żuraw hak", (p2[0], y_hak - 0.3, p2[2]), (0.8, 0.9, 0.8), "tusz")
        # klocek 4 × 4 × 4 na zawiesiu, dół na 14, lekko obrócony i przechylony (huśta się)
        K = _Rama((p2[0], 16.3, p2[2]), (0, 14, 5))
        hak = (p2[0], y_hak - 0.7, p2[2])
        with s.cechy(cien=False):
            for sx in (-1, 1):
                s.belka("Żuraw zawiesie", hak, K((sx * 1.5, 2.0, 0.0)), 0.3, "tusz", "SmoothPlastic")
        with K.uklad(s):
            s.blok("Klocek budowy", (0, 0, 0), (4.0, 4.0, 4.0), KAMIEN)
            s.blok("Klocek obrys", (0, 0, -2.25), (4.8, 4.8, 0.4), "tusz")
            s.blok("Klocek obrys spód", (0, -2.25, 0.0), (4.8, 0.4, 4.0), "tusz")
            s.ramka("Klocek obrys", (0, 0, 2.05), 3.4, 3.4, "tusz", grub=0.4, gleb=0.3)
            for x in (-1.0, 1.0):
                for z in (-1.0, 1.0):
                    s.walec("Klocek wypustka", (x, 2.3, z), 0.7, 0.6, KAMIEN, os="y")


# --------------------------------------------------------------------------- sztandar Rycerza na lewej baszcie
def _sztandar(s):
    kat = -14.0
    a = math.radians(kat)
    d = (math.sin(a), 0.0, math.cos(a))
    y = 4.6
    p_in = L2((d[0] * (LR[2] - 0.4), y, d[2] * (LR[2] - 0.4)))
    p_out = L2((d[0] * (LR[2] + 2.1), y, d[2] * (LR[2] + 2.1)))
    dg = L2.kierunek(d)
    ry = math.degrees(math.atan2(dg[0], dg[2]))
    with s.cechy(kolizja=False):
        s.belka("Sztandar drąg", p_in, p_out, 0.6, "tusz", "SmoothPlastic")
        with s.uklad(pos=p_out, obrot=(0, ry, 0)):
            s.blok("Sztandar poprzeczka", (0, 0, 0.0), (6.2, 0.6, 0.6), "tusz")
            with s.cechy(cien=False):
                for x in (-3.4, 3.4):
                    s.blok("Sztandar gałka", (x, 0, 0), (0.9, 0.9, 0.9), "zloto", rot=(45, 0, 45))
            # trzy segmenty łamane ±8° (płat faluje), złota podkładka = jasny obrys ciemnego błękitu
            with s.uklad(pos=(0, -0.3, 0.0), obrot=(-8, 0, 0)):
                _plat(s, 4.2)
                with s.uklad(pos=(0, -4.2, 0), obrot=(16, 0, 0)):
                    _plat(s, 4.0)
                    zestaw.lata(s, (0.2, -2.0, 0.15), 2.2, 2.2, "zloto", przechyl=8)
                    with s.uklad(pos=(0, -4.0, 0), obrot=(-16, 0, 0)):
                        _plat(s, 2.6)
                        with s.uklad(pos=(0, -2.6 + 0.05, 0), obrot=(0, 0, -90)):   # ogon-szpic w dół
                            for zn, rz in ((1, 0), (-1, 180)):
                                s.klin("Sztandar szpic", (1.0, zn * 1.25, 0), (0.3, 2.5, 2.0), KOD, "Fabric", rot=(0, -90, rz))


def _plat(s, h):
    s.blok("Sztandar", (0, -h / 2.0, 0.0), (5.0, h + 0.05, 0.3), KOD, "Fabric")
    with s.cechy(cien=False):
        s.blok("Sztandar obrys", (0, -h / 2.0, -0.22), (5.6, h, 0.2), "zloto")


# --------------------------------------------------------------------------- echo: złoty klucz 12 na haku
def _klucz(s):
    pos, ry = _na_walcu(LR[0], 42, 14.4 - 0.9, 0.0)
    with L0.uklad(s), s.cechy(kolizja=False):
        with s.uklad(pos=pos, obrot=(0, ry, 0)):
            s.blok("Klucz hak", (0, 0, 0.8), (0.6, 0.6, 2.0), "tusz")
            with s.uklad(pos=(0, -0.2, 1.5), obrot=(0, 0, 8)):  # klucz kołysze się na haku
                s.walec("Klucz ucho", (0, -2.3, 0), 2.3, 0.8, "zloto", os="z")
                s.walec("Klucz ucho otwór", (0, -2.3, 0.15), 0.9, 0.7, "tusz", os="z")
                s.walec("Klucz obrys", (0, -2.3, -0.45), 2.8, 0.3, "tusz", os="z")
                s.blok("Klucz pierścień", (0, -4.8, 0), (2.0, 0.6, 1.0), "tusz")
                s.blok("Klucz trzon", (0, -8.4, 0), (1.2, 7.2, 0.8), "zloto")
                s.blok("Klucz trzon obrys", (0.4, -9.2, -0.45), (3.4, 6.2, 0.3), "tusz")
                s.blok("Klucz pióro", (1.15, -11.3, 0), (1.5, 1.2, 0.8), "zloto")
                s.blok("Klucz pióro", (0.95, -9.6, 0), (1.1, 0.9, 0.8), "zloto")


# --------------------------------------------------------------------------- żart: wycieraczka przed bramą twierdzy
def _wycieraczka(s):
    with s.uklad(pos=(0.3, 0, 4.3), obrot=(0, 6, 0)), s.cechy(kolizja=False, cien=False):
        s.blok("Wycieraczka rant", (0, 0.2, 0), (8.6, 0.3, 4.6), "zloto")
        s.blok("Wycieraczka", (0, 0.3, 0), (8.0, 0.3, 4.0), KOD, "Fabric")
        # na środku złota sylwetka twierdzy (bez liter): mur i dwie wieżyczki
        s.blok("Wycieraczka znak", (0, 0.5, 0.35), (3.0, 0.2, 0.9), "zloto")
        for x, h in ((-1.6, 2.0), (1.6, 1.6)):
            s.blok("Wycieraczka znak", (x, 0.5, 0.35 - (h - 0.9) / 2.0), (0.9, 0.2, h), "zloto")
        s.naroznik("Wycieraczka róg", (3.55, 0.75, 1.55), (1.0, 0.6, 1.0), cien(s, KOD, 0.8), rot=(0, 90, 0))


# --------------------------------------------------------------------------- znaki miasteczka i rekwizyty przy wejściu
def _znaki(s, rnd, ciemny):
    # wypadnięty klocek z lewej baszty (wnęka na walcu) i klocek na ziemi
    pos, ry = _na_walcu(LR[0], -38, 4.0, 0.12)
    p = L0(pos)
    zestaw.wypadniety_klocek(s, p, (-13.4, 0, 5.4), KAMIEN, ry=ry, obrot_klocka=24)
    # chorągiewka Rycerza na kurtynie, między blankami
    zestaw.choragiewka_duetu(s, (2.9, KURT_TOP, -0.6), "rycerz", przechyl=12)
    # latarnia przy prawym ościeżu (wysięgnik ku przejściu, poza osią portalu)
    zestaw.latarnia(s, (8.4, 0, 5.4), wys=9.0, lustro=True, plama_r=3.0)
    # materiał na twierdzę: sterta klocków (duży–średni–mały) przy prawej baszcie
    with s.cechy(kolizja=False):
        with s.uklad(pos=(12.4, 0, 5.2), obrot=(0, -14, 0)):
            s.blok("Sterta klocek", (0, 1.0, 0), (4.4, 2.0, 2.4), KAMIEN)
            for x in (-1.2, 0.0, 1.2):
                s.walec("Sterta wypustka", (x, 2.25, 0.0), 0.45, 0.5, KAMIEN, os="y")
            with s.uklad(pos=(-0.6, 2.0, 0.1), obrot=(0, 28, 0)):
                s.blok("Sterta klocek", (0, 1.0, 0), (2.4, 2.0, 2.4), KOD)
                s.walec("Sterta wypustka", (0, 2.25, 0), 0.55, 0.5, KOD, os="y")
            with s.uklad(pos=(2.3, -0.1, 1.3), obrot=(0, 40, 9)):
                s.blok("Sterta klocek", (0, 0.6, 0), (2.0, 1.2, 2.0), "zloto")
    zestaw.kamien(s, (-11.2, 0, 7.4), rnd, 2.4, dwa=False)
    # grządka przy lewym ościeżu — „własny dom” mimo murów (razem z wycieraczką)
    zestaw.kwiaty(s, (-6.8, 0, 5.6), ry=8, kolory=("czerwien", "zloto"))
