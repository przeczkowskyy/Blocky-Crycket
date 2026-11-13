# -*- coding: utf-8 -*-
"""Stajnia wierzchowców (`stajnia`, grupa Stajnia) — mapa v2 „Krzywe Miasteczko”, karta PROJEKT.md 5.6.

Długa, niska stajnia z ciemnych desek (jasne narożniki i ramy zamiast tuszu — front stoi w cieniu) pod wielką,
złocistą strzechą z pasów (krawędź okapu poszarpana, kalenica „w siodło”, spód okapu i kalenica w tuszu).
Nad drzwiami, po lewej, wysunięty szczyt w kontrze do dachu; wokół drzwi złota podkowa-brama z 7 hufnalami.
Po prawej trzy boksy z połówkowymi drzwiczkami; z lukarny z zaklinowaną belą siana i widłami wysuwa się wędka
z marchewką, do której z boksu wyciąga łeb koń. Echo: koryto z wodą przy prawym boku.

Układ: (0, 0, 0) = środek działki 38 × 22 na ziemi, front z drzwiami ku +Z. Korpus 32 × 16 ma środek w (0; −1),
więc buduję w układzie K przesuniętym o −1 w Z (lico frontu K z = +8, czyli z = +7 w działce).

Odstępstwa od karty (świadome):
- dach ry +4° zamiast −4°: przy −4° prawy okap wysuwa się nad boksy i żyłka z marchewką musiałaby wisieć poza działką;
  skręt jest w połowie oddany długością okapów (SKRET_KOMP), żeby narożniki okapu nie wychodziły > 2 poza działkę;
- połacie 36° / 46° (średnio 41°) zamiast jednej 42°: przykazanie 5 (połacie różnią się o ≥ 10°);
- ściany do 8,6 (z cokołem), wierzch ≈ 20 z wiatrowskazem; okap nad boksami 2–3 „nadgryziony” (2,2 i 1,5 zamiast 3,5);
- drzwi 8 × 10 nie mieszczą się w ścianie 9, więc stoją w wysuniętym szczycie (ryzalit 16,5 × 10,6) nad lewą częścią;
  lukarna z belą przesunięta na prawo od niego (x 0…6,5), bela Ø 5,4 × 4,5 w kolorze `zloto` (na strzesze
  `dach_stajnia` ginęła), koń `drewno_jasne` zamiast `drewno` (front w cieniu, ciemny łeb ginął na ciemnych deskach);
- okapy (wys. 5–7) wystają do 2 poza działkę — karta sama stawia okap 3,5 przy ścianie 9, więc nie da się ich trzymać
  powyżej 10; widły i kalenica wystają ≤ 0,9 powyżej 10.

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/stajnia.py --wyj <folder> --szer 1000
Status: propozycja (noc 13.11.2026), nie kanon.
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.biblioteka.scena import macierz_obrotu, razy_wektor, mnoz  # noqa: E402

NAZWA = "Stajnia"
OBRYS = (38, 22)
WYSOKOSC = 20
BUDZET = 270
INTERAKCJA = (-8.0, 15.0)
OBRYS_SYLWETKI = False          # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany, obrys robimy z klocków

SC, JAS, DACH = "drewno_ciemne", "drewno_jasne", "dach_stajnia"

# --- korpus (układ K = działka przesunięta o −1 w Z)
W, D = 32.0, 16.0               # x ±16, z ±8 (lico frontu z = +8)
HS = 8.6                        # wierzch ścian
# --- dach główny (układ R: nad środkiem korpusu, rz +4°, ry +4°)
Y_DACH = 8.95
KF0, KB0 = 36.0, 46.0           # połać frontowa / tylna (średnio 41°, różnica 10°)
T = 1.8                         # grubość strzechy
OKAP_P, OKAP_T = 3.5, 2.0       # okap z frontu / z tyłu (poziomo poza lico)
_tf, _tb = math.tan(math.radians(KF0)), math.tan(math.radians(KB0))
B_RUN = D / (1.0 + _tb / _tf)   # bieg połaci tylnej
A_RUN = D - B_RUN               # bieg połaci frontowej
H_DACH = A_RUN * _tf            # wzniesienie kalenicy (spód połaci) nad krawędzią ścian
Z_KAL = D / 2.0 - A_RUN         # z kalenicy (spód) w układzie R
# pasy strzechy: granice w X (okap z boków 3 → ±19) i obniżenie kalenicy — „siodło” najniżej w x 6…14
PASY_X = (-19.0, -16.5, -11.2, -7.0, -0.5, 6.0, 10.5, 14.0, 16.5, 19.0)
PASY_D = (0.0, -0.2, -0.4, -0.6, -0.8, -1.5, -1.5, -0.8, 0.0)
PASY_UCIETE = (0, 1, 2, 3)      # pasy frontu nad wysuniętym szczytem — kończą się wyżej, pod jego dachem
OKAP_PAS = {5: 2.2, 6: 1.5}     # „nadgryziony” okap nad boksami z koniem — żyłka z marchewką wisi przed nim
SKRET_KOMP = 0.5                # część skrętu dachu (ry) oddana przy okapach, żeby nie wyjść daleko poza działkę
Z_CIECIA = 3.5
# --- wysunięty szczyt nad drzwiami (układ G, rz −6° = kontra do dachu)
BAY_X0, BAY_X1, BAY_Z1, BAY_H = -16.0, -0.5, 10.5, 10.6
DRZWI_X = -8.0
KG = 28.0
# --- boksy
BOKSY_X = (2.4, 7.6, 12.8)


# =========================================================================== narzędzia
def _lancuch(ogniwa, p):
    """Punkt p z najgłębszego układu do zewnętrznego: ogniwa = [(pos, obrot), …] od zewnętrznego do wewnętrznego."""
    R = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    t = (0.0, 0.0, 0.0)
    for pos, obrot in ogniwa:
        dp = razy_wektor(R, pos)
        t = (t[0] + dp[0], t[1] + dp[1], t[2] + dp[2])
        R = mnoz(R, macierz_obrotu(*obrot))
    q = razy_wektor(R, p)
    return (t[0] + q[0], t[1] + q[1], t[2] + q[2])


def _katy(d):
    hd = H_DACH + d
    return math.atan2(hd, A_RUN), math.atan2(hd, B_RUN)


def _wierzcholek(kf, kb):
    """(z, y) przecięcia wierzchów obu połaci (spody spotykają się w (Z_KAL, H+d))."""
    tf, tb = math.tan(kf), math.tan(kb)
    z = (T / math.cos(kf) - T / math.cos(kb) + 8.0 * tf - 8.0 * tb) / (tf + tb)
    return z, T / math.cos(kf) - (z - 8.0) * tf


def _blok_na_polaci(s, nazwa, x0, x1, k, sig0, sig1, off, grub, kolor, przod=True, mat="SmoothPlastic"):
    """Blok leżący na połaci (układ R): spód połaci przechodzi przez krawędź ściany (z = ±8, y = 0) pod kątem k;
    sig = odległość wzdłuż spadku od krawędzi ściany (+ = ku okapowi); off = przesunięcie spodu bloku wzdłuż normalnej."""
    sc = 0.5 * (sig0 + sig1)
    c, sn = math.cos(k), math.sin(k)
    if przod:
        zc, yc = 8.0 + sc * c + (off + grub / 2.0) * sn, -sc * sn + (off + grub / 2.0) * c
        rot = (math.degrees(k), 0, 0)
    else:
        zc, yc = -8.0 - sc * c - (off + grub / 2.0) * sn, -sc * sn + (off + grub / 2.0) * c
        rot = (math.degrees(k), 180, 0)
    s.blok(nazwa, (0.5 * (x0 + x1), yc, zc), (x1 - x0, grub, sig1 - sig0), kolor, mat, rot=rot)


# =========================================================================== budowa
def buduj(s, rnd):
    with s.uklad(pos=(0, 0, -1.0)):
        _korpus(s)
        _boksy(s)
        _kon(s)
        _wysuniety_szczyt(s)
        with s.uklad(pos=(0, Y_DACH, 0), obrot=(0, 4, 4)), s.cechy(kolizja=False):
            _dach(s)
            _szczyty_dachu(s)
            _lukarna(s)
            _konik(s)
        _wedka(s)
        _tyl_i_boki(s)
    _rekwizyty(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


def _korpus(s):
    s.blok("Cokół", (0, 0.5, 0), (W + 0.8, 1.0, D + 0.8), "kamien_cokol", "Cobblestone")
    s.blok("Ściany", (0, (HS + 0.3) / 2.0, 0), (W, HS - 0.3, D), SC, "WoodPlanks")
    with s.cechy(kolizja=False):
        s.blok("Podwalina", (0, 1.2, 0), (W + 1.0, 0.5, D + 1.0), JAS)
        h = HS + 0.4 - 1.45
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik", (sx * (W / 2.0 - 0.3), 1.45 + h / 2.0, sz * (D / 2.0 - 0.3)), (1.2, h, 1.2), JAS, "Wood")
        for sz in (-1, 1):
            s.blok("Wieniec", (0, HS - 0.25, sz * (D / 2.0 + 0.05)), (W + 0.4, 0.6, 0.5), JAS)
        for sx in (-1, 1):
            s.blok("Wieniec", (sx * (W / 2.0 + 0.05), HS - 0.25, 0), (0.5, 0.6, D + 0.4), JAS)


def _boksy(s):
    """Trzy boksy z połówkowymi drzwiczkami `biel` w ramach `drewno_jasne`: 1 zamknięty, 2 z koniem (ciepłe światło),
    3 z otwartą górną połówką (ciemne wnętrze)."""
    y0, y1, ym = 1.45, 7.2, 4.55
    w = 3.2
    with s.cechy(kolizja=False):
        for i, xb in enumerate(BOKSY_X):
            for sx in (-1, 1):
                s.blok("Boks rama", (xb + sx * (w / 2.0 + 0.5), (y0 + 8.2) / 2.0, 8.1), (1.0, 8.2 - y0, 0.6), JAS)
            s.blok("Boks rama", (xb, 7.7, 8.1), (w + 2.0, 1.0, 0.6), JAS)
            s.blok("Boks drzwiczki", (xb, (y0 + ym) / 2.0, 8.15), (w, ym - y0, 0.3), "biel")
            with s.cechy(cien=False):
                kier = 1 if i % 2 == 0 else -1
                s.belka("Boks zastrzał", (xb - kier * 1.2, y0 + 0.4, 8.4), (xb + kier * 1.2, ym - 0.4, 8.4), 0.45, JAS, "SmoothPlastic", 0.25)
            if i == 0:                                         # górna połówka zamknięta
                s.blok("Boks drzwiczki", (xb, (ym + y1) / 2.0 + 0.03, 8.15), (w, y1 - ym - 0.06, 0.3), "biel")
                with s.cechy(cien=False):
                    s.belka("Boks zastrzał", (xb + 1.2, ym + 0.35, 8.4), (xb - 1.2, y1 - 0.35, 8.4), 0.45, JAS, "SmoothPlastic", 0.25)
            else:
                swiatlo = "neon_okno" if i == 1 else "tusz"
                with s.cechy(cien=False):
                    s.blok("Boks wnętrze", (xb, (ym + y1) / 2.0, 8.1), (w, y1 - ym, 0.2), swiatlo, "Neon" if i == 1 else "SmoothPlastic")
                # otwarta górna połówka na zawiasie (2: lewy, 3: prawy), odchylona o 70°
                st = -1 if i == 1 else 1
                with s.uklad(pos=(xb + st * w / 2.0, (ym + y1) / 2.0, 8.35), obrot=(0, -st * -70, 0)):
                    s.blok("Boks drzwiczki", (-st * w / 2.0, 0, 0.15), (w, y1 - ym - 0.1, 0.3), "biel")


def _kon(s):
    """Koń z klocków (×1,3) wychyla się z boksu 2: szyja z grzywą w przód, łeb skręcony w prawo — z frontu widać
    jego profil (oko, chrapy, uszy, strzałka `biel`) wpatrzony w marchewkę. Maść `drewno_jasne`: front stoi w cieniu,
    ciemny koń zginąłby na ciemnych deskach."""
    kon = "drewno_jasne"
    xb = BOKSY_X[1]
    with s.cechy(kolizja=False):
        s.belka("Koń szyja", (xb - 0.2, 4.9, 7.6), (xb + 0.5, 6.4, 9.6), 1.8, kon, "SmoothPlastic", 1.6)
        s.belka("Koń grzywa", (xb - 0.75, 5.8, 7.7), (xb - 0.1, 7.4, 9.35), 0.6, "tusz", "SmoothPlastic", 0.7)
        with s.uklad(pos=(xb + 0.6, 6.6, 9.6), obrot=(8, 70, 0)):
            s.blok("Koń łeb", (0, 0, 1.0), (1.7, 1.8, 2.6), kon)
            s.blok("Koń pysk", (0, -0.25, 2.55), (1.85, 1.4, 1.1), cien(s, kon, 0.8))
            s.blok("Koń ucho", (-0.5, 1.35, -0.35), (0.6, 1.5, 0.55), kon, rot=(-28, 0, 14))
            s.blok("Koń ucho", (0.5, 1.35, -0.15), (0.6, 1.5, 0.55), kon, rot=(-28, 0, -14))
            with s.cechy(cien=False):
                s.blok("Koń grzywka", (0, 1.0, 0.25), (1.0, 0.5, 0.8), "tusz", rot=(0, 0, 10))
                s.blok("Koń strzałka", (0, 0.95, 1.5), (0.55, 0.25, 1.8), "biel")
                s.blok("Koń oko", (-0.87, 0.35, 0.6), (0.25, 0.85, 0.85), "biel")
                s.blok("Koń źrenica", (-0.99, 0.4, 0.82), (0.2, 0.45, 0.45), "tusz")
                s.blok("Koń chrapa", (-0.96, -0.05, 2.75), (0.2, 0.4, 0.4), "tusz")
                s.blok("Koń pyszczek", (-0.96, -0.75, 2.6), (0.2, 0.25, 1.0), "tusz")


def _wysuniety_szczyt(s):
    """Wysunięty szczyt nad drzwiami: prosty ryzalit 16 × 10,6 (pion) od lewego narożnika, drzwi 8 × 10 w x = −8,
    podkowa-brama, nad nim szczyt i dach 28° w układzie G przechylonym o −6° (kontra do dachu głównego)."""
    xc = 0.5 * (BAY_X0 + BAY_X1)
    xd = DRZWI_X
    wb = BAY_X1 - BAY_X0
    zc = 0.5 * (7.0 + BAY_Z1)
    s.blok("Ryzalit", (xc, (BAY_H + 0.3) / 2.0, zc), (wb, BAY_H - 0.3, BAY_Z1 - 7.0), SC, "WoodPlanks")
    for x0, x1 in ((BAY_X0 - 0.4, xd - 4.2), (xd + 4.2, BAY_X1 + 0.4)):
        s.blok("Cokół", (0.5 * (x0 + x1), 0.5, 0.5 * (7.2 + BAY_Z1 + 0.4)), (x1 - x0, 1.0, BAY_Z1 + 0.4 - 7.2), "kamien_cokol", "Cobblestone")
    s.blok("Drzwi próg", (xd, 0.2, BAY_Z1 + 0.5), (8.6, 0.4, 1.0), "kamien_cokol")
    with s.cechy(kolizja=False):
        for x in (BAY_X0 + 0.3, BAY_X1 - 0.3):
            s.blok("Narożnik", (x, 1.0 + 4.9, BAY_Z1 - 0.3), (1.2, 9.8, 1.2), JAS, "Wood")
        s.blok("Wieniec", (xc, BAY_H - 0.2, BAY_Z1 + 0.15), (wb + 0.4, 0.6, 0.5), JAS)
        # drzwi: dwa skrzydła `drewno` z zastrzałami „Z” w tę samą stronę (asymetria)
        for xs in (xd - 2.0, xd + 2.0):
            s.blok("Drzwi skrzydło", (xs, 5.4, BAY_Z1 + 0.15), (3.95, 10.0, 0.3), "drewno", "WoodPlanks")
            with s.cechy(cien=False):
                for y in (1.7, 9.2):
                    s.blok("Drzwi listwa", (xs, y, BAY_Z1 + 0.42), (3.5, 0.6, 0.2), JAS)
                s.belka("Drzwi zastrzał", (xs - 1.4, 2.1, BAY_Z1 + 0.42), (xs + 1.4, 8.8, BAY_Z1 + 0.42), 0.6, JAS, "SmoothPlastic", 0.2)
        _podkowa(s, xd)
        # wypadnięty kawałek lewego narożnika ryzalitu (znak miasteczka)
        with s.cechy(cien=False):
            s.blok("Klocek wnęka", (BAY_X0 + 0.3, 3.4, BAY_Z1 - 0.3), (1.32, 1.5, 1.32), "tusz")
        with s.uklad(pos=(BAY_X0 - 1.5, 0, 9.3), obrot=(0, 24, 0)):
            s.blok("Klocek wypadnięty", (0, 0.6, 0), (1.5, 1.2, 1.2), JAS)
            for x in (-0.35, 0.35):
                s.walec("Klocek wypustka", (x, 1.4, 0), 0.35, 0.4, JAS, os="y")
    # szczyt i dach w układzie G
    run = (wb / 2.0)
    kg = math.radians(KG)
    hg = run * math.tan(kg)
    c, sn = math.cos(kg), math.sin(kg)
    with s.uklad(pos=(xc, BAY_H, 0), obrot=(0, 0, -6)), s.cechy(kolizja=False):
        s.blok("Kolanko", (0, -1.275, 5.7), (wb - 0.4, 3.05, 9.4), SC, "WoodPlanks")
        ht = hg - 0.3
        pb = ht / math.tan(kg)
        for zn in (-1, 1):
            s.klin("Szczyt", (zn * pb / 2.0, ht / 2.0, BAY_Z1 - 0.3), (0.6, ht, pb), SC, "WoodPlanks", rot=(0, -zn * 90, 0))
        sig_top = (-run - T * sn) / c
        sig_okap = 1.5 / c
        for zn in (-1, 1):
            for z0, z1, off, kol in ((5.0, BAY_Z1 + 0.6, 0.0, DACH), (-1.0, 5.05, -0.25, cien(s, DACH, 0.9))):
                sc = 0.5 * (sig_top + sig_okap)
                x = zn * (run + sc * c + (off + T / 2.0) * sn)
                y = -sc * sn + (off + T / 2.0) * c
                s.blok("Strzecha szczytu", (x, y, 0.5 * (z0 + z1)), (sig_okap - sig_top, T, z1 - z0), kol, rot=(0, 0, -zn * KG))
            su0, su1 = -1.0, sig_okap + 0.3
            sc = 0.5 * (su0 + su1)
            x = zn * (run + sc * c + (-0.55) * sn)
            y = -sc * sn + (-0.55) * c
            s.blok("Strzecha spód", (x, y, 5.2), (su1 - su0, 0.45, 12.6), "tusz", rot=(0, 0, -zn * KG))
        ya = hg + T / c
        s.blok("Kalenica szczytu", (0, ya - 0.15, 5.1), (1.5, 0.9, 12.4), "tusz")


def _podkowa(s, xc):
    """Podkowa-brama 12,6 × 12,6 wokół drzwi: łuk 240° z 9 bloków `zloto` (pas 1,8), pięty do ziemi, 7 hufnali `tusz`;
    przechylona o 5° (krzywo powieszona). Przejście między piętami 8,3."""
    Ro, pas = 6.3, 1.8
    Rm = Ro - pas / 2.0
    n, rozp = 9, 240.0
    dl = 2.0 * Ro * math.tan(math.radians(rozp / n / 2.0)) * 1.02
    with s.uklad(pos=(xc, Ro, 0), obrot=(0, 0, 5)):
        for i in range(n):
            f = math.radians(-30.0 + rozp * (i + 0.5) / n)
            g = 0.2 * (i % 2)
            s.blok("Podkowa", (Rm * math.cos(f), Rm * math.sin(f), BAY_Z1 + 0.45 + g / 2.0), (dl, pas, 1.2 + g), "zloto",
                   rot=(0, 0, math.degrees(f) - 90))
        for zn in (-1, 1):
            xh = zn * (Rm * math.cos(math.radians(30)) + 0.2)
            yt = -Rm * math.sin(math.radians(30)) + 0.6
            yb = -Ro - 0.7
            s.blok("Podkowa pięta", (xh, 0.5 * (yt + yb), BAY_Z1 + 0.45), (pas, yt - yb, 1.2), "zloto")
        with s.cechy(cien=False):
            for j in range(7):
                f = math.radians(-30.0 + rozp * (j + 0.5) / 7)
                s.blok("Podkowa hufnal", (Rm * math.cos(f), Rm * math.sin(f), BAY_Z1 + 1.2), (0.75, 0.75, 0.5), "tusz",
                       rot=(0, 0, math.degrees(f)))


def _dach(s):
    """Strzecha z 9 pasów na każdej połaci; co drugi pas niżej o 0,3 i dłuższy (poszarpany okap), dwa tony;
    pod okapem ciemny spód, na kalenicy tusz. Układ R: (0, 0, 0) = środek krawędzi ścian."""
    tony_p = (DACH, cien(s, DACH, 0.9))
    tony_t = (cien(s, DACH, 0.85), cien(s, DACH, 0.77))
    for i in range(len(PASY_D)):
        x0, x1 = PASY_X[i] - 0.05, PASY_X[i + 1] + 0.05
        kf, kb = _katy(PASY_D[i])
        za, ya = _wierzcholek(kf, kb)
        nisko = i % 2 == 1
        off = -0.3 if nisko else 0.0
        ext = 0.35 if nisko else 0.0
        # front
        sig0 = (za - 8.0 - T * math.sin(kf)) / math.cos(kf)
        xc = 0.5 * (x0 + x1)
        kmp = SKRET_KOMP * xc * math.tan(math.radians(4.0))
        if i in PASY_UCIETE:
            sig1 = (Z_CIECIA - 8.0) / math.cos(kf)
        else:
            sig1 = (OKAP_PAS.get(i, OKAP_P) + ext + kmp) / math.cos(kf)
        _blok_na_polaci(s, "Strzecha", x0, x1, kf, sig0, sig1, off, T, tony_p[i % 2], True)
        if i not in PASY_UCIETE:
            u0, u1 = -1.2 / math.cos(kf), sig1 + 0.3
            xu0, xu1 = (x0 - 0.3 if i == 0 else x0), (x1 + 0.3 if i == len(PASY_D) - 1 else x1)
            _blok_na_polaci(s, "Strzecha spód", xu0, xu1, kf, u0, u1, off - 0.5, 0.45, "tusz", True)
        # tył
        sig0 = (-8.0 - T * math.sin(kb) - za) / math.cos(kb)
        sig1 = (OKAP_T + ext - kmp) / math.cos(kb)
        _blok_na_polaci(s, "Strzecha", x0, x1, kb, sig0, sig1, off, T, tony_t[i % 2], False)
        u0, u1 = -1.2 / math.cos(kb), sig1 + 0.3
        xu0, xu1 = (x0 - 0.3 if i == 0 else x0), (x1 + 0.3 if i == len(PASY_D) - 1 else x1)
        _blok_na_polaci(s, "Strzecha spód", xu0, xu1, kb, u0, u1, off - 0.5, 0.45, "tusz", False)
        # kalenica
        s.blok("Kalenica", (0.5 * (x0 + x1), ya - 0.15, za), (x1 - x0 + 0.1, 0.9, 1.6), "tusz")
    # kolanko: wypełnia szczelinę między ścianami a krzywym dachem (wewnątrz obrysu ścian)
    s.blok("Kolanko", (0, -1.1, 0), (30.0, 3.0, 13.6), SC, "WoodPlanks")


def _szczyty_dachu(s):
    """Trójkątne szczyty pod skrajnymi pasami (d = 0) z jasnymi deskami wiatrowymi, na kolankach; w prawym (od
    słońca, widocznym z ulicy) klapa na siano."""
    kf, kb = _katy(0.0)
    tf, tb = math.tan(kf), math.tan(kb)
    m, zl = 0.35, 6.9
    y0 = max((8.0 - zl) * tf, (8.0 - zl) * tb) - m
    zf0 = 8.0 - (y0 + m) / tf
    zb0 = (y0 + m) / tb - 8.0
    H = H_DACH - m - y0
    for zn in (-1, 1):
        x = zn * 15.2
        s.blok("Kolanko szczytu", (x, 0.5 * (y0 - 2.6), 0), (0.6, y0 + 2.6, 2 * zl), SC, "WoodPlanks")
        s.klin("Szczyt", (x, y0 + H / 2.0, 0.5 * (Z_KAL + zf0)), (0.6, H, zf0 - Z_KAL), SC, "WoodPlanks", rot=(0, 180, 0))
        s.klin("Szczyt", (x, y0 + H / 2.0, 0.5 * (Z_KAL + zb0)), (0.6, H, Z_KAL - zb0), SC, "WoodPlanks")
        xd = zn * 15.65
        s.belka("Deska wiatrowa", (xd, y0 - 0.1, zf0 + 0.2), (xd, H_DACH - m - 0.1, Z_KAL), 0.6, JAS, "SmoothPlastic", 0.3)
        s.belka("Deska wiatrowa", (xd, y0 - 0.1, zb0 - 0.2), (xd, H_DACH - m - 0.1, Z_KAL), 0.6, JAS, "SmoothPlastic", 0.3)
    with s.cechy(cien=False):
        s.blok("Klapa rama", (15.6, 2.8, Z_KAL + 0.8), (0.4, 3.2, 3.0), JAS)
        s.blok("Klapa", (15.8, 2.8, Z_KAL + 0.8), (0.3, 2.4, 2.2), "drewno", "WoodPlanks")


def _lukarna(s):
    """Lukarna 6,4 × 5 nad lewą częścią boksów (układ R), przekrzywiona: w otworze krzywo zaklinowana bela siana
    Ø 5,4 × 4,5 (`zloto`, słoje na czole, kępki słomy) z wbitymi widłami 8; za belą ciepłe światło strychu."""
    with s.uklad(pos=(3.25, 0, 6.6), obrot=(0, 6, -10)):
        s.blok("Lukarna", (0, 4.3, -3.2), (6.4, 6.2, 6.4), SC, "WoodPlanks")
        with s.cechy(cien=False):
            s.blok("Lukarna światło", (0, 5.0, 0.1), (4.0, 3.4, 0.2), "neon_okno", "Neon")
        for sx in (-1, 1):
            s.blok("Lukarna rama", (sx * 2.3, 5.0, 0.2), (0.6, 4.2, 0.4), JAS)
        s.blok("Lukarna rama", (0, 7.0, 0.2), (5.2, 0.6, 0.4), JAS)
        with s.uklad(pos=(0, 7.4, 0), obrot=(-12, 0, 0)):
            s.blok("Strzecha lukarny", (0, 0.5, -2.75), (7.4, 1.0, 7.5), DACH)
            s.blok("Strzecha spód", (0, -0.25, -2.6), (7.7, 0.4, 7.8), "tusz")
        rb, lb = 2.7, 4.5
        ciem = cien(s, "zloto", 0.72)
        with s.uklad(pos=(0, 4.4, 1.55), obrot=(0, 25, 0)):
            s.walec("Bela", (0, 0, 0), rb, lb, "zloto", os="z")
            s.walec("Bela obrys", (0, 0, lb / 2.0 - 0.5), rb + 0.35, 0.3, "tusz", os="z")
            for i, (r, kol) in enumerate(((2.0, ciem), (1.6, "zloto"), (0.9, ciem), (0.5, "zloto"))):
                s.walec("Bela słoje", (0, 0, lb / 2.0 + 0.1 + 0.11 * i), r, 0.2, kol, os="z")
            s.walec("Bela sznurek", (0, 0, -0.6), rb + 0.12, 0.4, SC, os="z")
            with s.cechy(cien=False):
                for x, y, k in ((2.45, 1.1, -40), (-2.35, -0.9, 50), (0.9, 2.6, 12), (-1.6, 2.2, 35)):
                    s.blok("Słoma", (x, y, lb / 2.0 - 0.3), (0.3, 1.3, 0.3), DACH, rot=(0, 0, k))
                for x, k in ((-0.9, 8), (1.1, -12)):
                    s.blok("Słoma zwis", (x, -rb - 0.5, lb / 2.0 - 0.6), (0.35, 1.6, 0.35), DACH, rot=(0, 0, k))
                # widły wbite w czoło beli, trzonek w górę i w lewo
                d = (-0.6, 0.8, 0.0)
                n = math.sqrt(sum(v * v for v in d))
                d = tuple(v / n for v in d)
                b = (-0.9, 0.8, lb / 2.0 + 0.5)

                def pk(t):
                    return tuple(b[i] + t * d[i] for i in range(3))
                s.belka("Widły trzonek", pk(0.9), pk(6.3), 0.4, JAS, "SmoothPlastic")
                u = (d[1], -d[0], 0.0)
                nu = math.sqrt(u[0] ** 2 + u[1] ** 2)
                u = (u[0] / nu, u[1] / nu, 0.0)
                c0 = pk(0.75)
                s.belka("Widły", tuple(c0[i] - 1.0 * u[i] for i in range(3)), tuple(c0[i] + 1.0 * u[i] for i in range(3)), 0.35,
                        "metal_ciemny", "SmoothPlastic")
                for k in (-0.8, 0.0, 0.8):
                    a = tuple(c0[i] + k * u[i] for i in range(3))
                    s.belka("Widły ząb", a, tuple(a[i] - 1.9 * d[i] for i in range(3)), 0.3, "metal_ciemny", "SmoothPlastic")


def _konik(s):
    """Wiatrowskaz-konik (wys. ok. 2,6) na kalenicy w dołku siodła (tusz na tle nieba, strzałka `zloto`)."""
    i = 5
    kf, kb = _katy(PASY_D[i])
    za, ya = _wierzcholek(kf, kb)
    x = 0.5 * (PASY_X[i] + PASY_X[i + 1]) + 0.6
    with s.uklad(pos=(x, ya + 0.3, za), obrot=(0, 20, -12), skala=0.85), s.cechy(kolizja=False, cien=False):
        s.blok("Wiatrowskaz", (0, 0.7, 0), (0.3, 1.4, 0.3), "tusz")
        s.blok("Wiatrowskaz strzałka", (0, 1.25, 0), (3.2, 0.3, 0.3), "zloto")
        s.blok("Konik", (0, 2.0, 0), (1.7, 0.8, 0.3), "tusz", rot=(0, 0, 6))
        s.blok("Konik szyja", (0.85, 2.55, 0), (0.55, 1.0, 0.3), "tusz", rot=(0, 0, -25))
        s.blok("Konik łeb", (1.35, 2.95, 0), (1.0, 0.5, 0.3), "tusz", rot=(0, 0, -15))
        s.blok("Konik noga", (0.6, 1.45, 0), (0.3, 0.9, 0.3), "tusz", rot=(0, 0, -30))
        s.blok("Konik noga", (-0.6, 1.45, 0), (0.3, 0.9, 0.3), "tusz", rot=(0, 0, 30))
        s.blok("Konik ogon", (-1.0, 2.3, 0), (0.35, 0.9, 0.3), "tusz", rot=(0, 0, 35))


def _wedka(s):
    """Żart: z lukarny (nad belą) wysuwa się wędka, na żyłce marchewka wisi przed ciemnym boksem 3, 1,3 przed pyskiem
    konia — o włos za daleko (układ K)."""
    ogn = [((0, Y_DACH, 0), (0, 4, 4)), ((3.25, 0, 6.6), (0, 6, -10))]
    p0 = _lancuch(ogn, (1.5, 6.6, -1.5))                       # rękojeść w głębi otworu
    p1 = _lancuch(ogn, (1.6, 6.8, 0.9))                        # wylot z otworu, nad belą
    xt, zt = 12.4, 10.6
    tip = (xt, 17.6, zt)
    mid = (0.5 * (p1[0] + xt) - 0.3, max(p1[1], tip[1]) + 0.6, 0.5 * (p1[2] + zt) + 0.3)
    yk = 10.6
    with s.cechy(kolizja=False, cien=False):
        s.belka("Wędka", p0, mid, 0.4, JAS, "SmoothPlastic", 0.4)
        s.belka("Wędka", mid, tip, 0.35, JAS, "SmoothPlastic", 0.35)
        s.blok("Żyłka", (xt, 0.5 * (tip[1] + yk), zt), (0.2, tip[1] - yk, 0.2), "tusz")
        with s.uklad(pos=(xt, yk, zt), obrot=(0, 0, 8)):
            for k in (-28, 0, 26):
                s.blok("Nać", (math.sin(math.radians(-k)) * 0.5, -0.5, 0), (0.35, 1.4, 0.35), "lisc_jasny", rot=(0, 0, k))
            s.blok("Marchewka", (0, -1.95, 0), (1.5, 1.6, 1.5), "pomarancz", rot=(0, 45, 0))
            s.blok("Marchewka", (0, -3.4, 0), (1.05, 1.5, 1.05), "pomarancz", rot=(0, 10, 0))
            s.blok("Marchewka", (0, -4.6, 0), (0.6, 1.1, 0.6), cien(s, "pomarancz", 0.9), rot=(0, 45, 0))


def _tyl_i_boki(s):
    """Tył (ku padokowi): drzwi do padoku, dwa okienka, łata `pomarancz`; lewy bok (ku ulicy): okno z okiennicą
    i łata `zloto`."""
    zb = -D / 2.0
    with s.cechy(kolizja=False):
        with s.uklad(pos=(6.0, 0, zb), obrot=(0, 180, 0)):
            s.blok("Drzwi tylne", (0, 1.45 + 3.3, 0.15), (5.0, 6.6, 0.3), "drewno", "WoodPlanks")
            for sx in (-1, 1):
                s.blok("Drzwi tylne rama", (sx * 3.0, 1.45 + 3.6, 0.25), (1.0, 7.2, 0.5), JAS)
            s.blok("Drzwi tylne rama", (0, 1.45 + 7.0, 0.25), (7.0, 0.8, 0.5), JAS)
            with s.cechy(cien=False):
                s.belka("Drzwi tylne zastrzał", (-1.9, 2.2, 0.42), (1.9, 7.4, 0.42), 0.55, JAS, "SmoothPlastic", 0.2)
            for x, prz in ((10.5, 6), (16.5, -5)):
                with s.uklad(pos=(x, 5.6, 0), obrot=(0, 0, prz)), s.cechy(cien=False):
                    s.blok("Okienko rama", (0, 0, 0.2), (3.8, 3.0, 0.4), JAS)
                    s.blok("Okienko", (0, 0, 0.35), (2.8, 2.0, 0.3), "neon_okno", "Neon")
                    s.blok("Okienko szpros", (0, 0, 0.55), (0.35, 2.0, 0.2), JAS)
            zestaw.lata(s, (-5.0, 4.4, 0), 2.6, 2.2, "pomarancz", przechyl=-9)
        with s.uklad(pos=(-W / 2.0, 0, 0), obrot=(0, -90, 0)):
            with s.uklad(pos=(-4.5, 5.4, 0), obrot=(0, 0, -6)), s.cechy(cien=False):
                s.blok("Okienko rama", (0, 0, 0.2), (3.6, 3.4, 0.4), JAS)
                s.blok("Okienko", (0, 0, 0.35), (2.6, 2.4, 0.3), "woda_gleboka")
                s.blok("Okienko szpros", (0, 0, 0.55), (2.6, 0.35, 0.2), JAS)
                with s.uklad(pos=(1.95, 0, 0.3), obrot=(0, -14, -13)):
                    s.blok("Okiennica", (0.85, 0, 0.15), (1.7, 3.0, 0.3), "biel")
            zestaw.lata(s, (-0.6, 6.0, 0), 2.4, 2.0, "zloto", przechyl=8)
        # prawy bok (od słońca): mała podkowa „na szczęście” nad korytem — drugie echo szyldu
        with s.uklad(pos=(W / 2.0, 5.6, -0.4), obrot=(0, 90, 12)), s.cechy(cien=False):
            s.blok("Gwóźdź", (0, 1.25, 0.3), (0.35, 0.35, 0.6), "metal_ciemny")
            for zn in (-1, 1):
                s.blok("Podkówka", (zn * 0.95, 0.15, 0.2), (0.6, 2.2, 0.4), "zloto", rot=(0, 0, -zn * 8))
                s.blok("Podkówka", (zn * 0.55, -1.15, 0.22), (1.0, 0.6, 0.4), "zloto", rot=(0, 0, zn * 35))
            s.blok("Podkówka", (0, -1.4, 0.25), (0.8, 0.6, 0.4), "zloto")


def _rekwizyty(s, rnd):
    """Echo: koryto z wodą przy prawym boku (wys. 2); trójka kostek siana przy lewym boku z chorągiewką Kota-Maga."""
    with s.uklad(pos=(17.6, 0, -1.5), obrot=(0, 7, 0)):
        s.blok("Koryto", (0, 0.95, 0), (2.4, 1.9, 5.8), "drewno", "WoodPlanks")
        with s.cechy(kolizja=False):
            for sx in (-1, 1):
                s.blok("Koryto burta", (sx * 1.0, 2.15, 0), (0.45, 0.5, 6.0), JAS)
            for sz in (-1, 1):
                s.blok("Koryto burta", (0, 2.15, sz * 2.8), (1.6, 0.5, 0.45), JAS)
            with s.cechy(cien=False):
                s.blok("Koryto woda", (0, 2.0, 0), (1.6, 0.3, 5.2), "woda")
    with s.cechy(kolizja=False):
        for (x, y, z, sx, sy, sz, ry, rz) in ((-17.6, 1.1, 4.4, 2.2, 2.2, 3.4, 8, 0), (-17.5, 3.25, 4.0, 2.0, 2.0, 3.0, -14, 4),
                                              (-17.5, 0.85, 0.9, 1.7, 1.7, 2.4, 30, 0)):
            with s.uklad(pos=(x, y, z), obrot=(0, ry, rz)):
                s.blok("Siano", (0, 0, 0), (sx, sy, sz), DACH)
                with s.cechy(cien=False):
                    s.blok("Siano sznurek", (0, 0, 0), (sx + 0.1, sy + 0.1, 0.35), SC)
    zestaw.choragiewka_duetu(s, (-17.3, 3.9, 3.3), "kot", ry=-90, przechyl=12)
