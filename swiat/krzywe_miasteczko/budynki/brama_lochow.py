# -*- coding: utf-8 -*-
"""Brama lochów mapy v2 „Krzywe Miasteczko” — paszcza w skale (PROJEKT.md, karta 5.5).

Masyw z krzywych bloków `kamien_lochu` (lewa część wyższa, prawa niższa, góra szersza od dołu), w nim gardziel 12 × 14
z łukiem z 11 klińców na jasnym obrysie `kamien_cieply`, zęby, oczy, czapy mchu, kryształy, język, szyld-trójkąt
z czaszką i żart: zerwany łańcuch z otwartą kłódką na ziemi — ktoś już wszedł.

Konwencja (PROJEKT 5.0): (0, 0, 0) = środek działki na dnie niecki, front z wejściem ku +Z (lico masywu ok. z = +6),
działka x ∈ ±15, z ∈ ±10, wys. ≤ 36. Niecka, rampa i skała za murem — generator miasta.

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/brama_lochow.py --wyj <folder> --szer 1000
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "BramaLochow"
OBRYS = (30, 20)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 36
BUDZET = 290                     # twardy sufit 363
INTERAKCJA = (0.0, 14.0)         # przed językiem, na osi przejścia
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków

SKALA = "kamien_lochu"
JASNY = "kamien_cieply"          # jasny obrys na ciemnym kamieniu (tusz na kamien_lochu ma tylko 1,9 : 1)
MECH = "dach_lochy"

# gardziel: łuk nad przejściem 12 × 14
AX, AY = 0.08, 9.6               # środek łuku (filary pochylone do środka, więc ich szczyty zbliżają się do osi)
R_IN = 5.08                      # promień wewnętrzny klińców
GRUB = 3.2                       # głębokość promieniowa klińca
RIM = 0.8                        # jasny obrys łuku
Z_TYL, Z_LICO = 3.4, 6.3         # klińce i filary od z = 3,4 do 6,3 (co drugi kliniec do 6,5)
Z_PORTAL = 3.0                   # płyta neon_portal w głębi 3


def buduj(s, rnd):
    ciemny = cien(s, SKALA, 0.84)
    _masyw(s, ciemny)
    _gardziel(s, ciemny)
    _twarz(s)
    _krysztaly(s)
    _szyld(s)
    _zart(s)
    _znaki(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- pomocnicze
def _czapa_mchu(s, w, d, y, kapki=(), kapki_tyl=(), dx=0.0):
    """Czapa mchu na wierzchu bloku (w bieżącym układzie bloku, y = wierzch bloku): podkładka tusz pod spodem
    (ciemny rant widoczny od dołu i na tle nieba) + płyta mchu + kapki spływające po licu i tyle (x, długość)."""
    # po krytyce: płyta mchu nie przykrywa całego wierzchu (był „budynek z zielonym wiekiem”), kapki dłuższe — mech spływa
    with s.cechy(kolizja=False):
        s.blok("Mech rant", (dx - 0.12 * w, y + 0.15, 0), (0.72 * w + 1.0, 0.5, d + 1.0), "tusz")
        s.blok("Mech", (dx - 0.12 * w, y + 0.7, 0), (0.72 * w + 0.5, 0.7, d + 0.5), MECH)
        with s.cechy(cien=False):
            for zn, lista in ((1, kapki), (-1, kapki_tyl)):
                for x, dl in lista:
                    dl2 = dl * 1.6
                    s.blok("Mech kapka", (dx + x, y + 0.6 - dl2 / 2.0, zn * (d / 2.0 + 0.35)), (1.2, dl2, 0.5), MECH)


def _krawedz(s, nazwa, x, y0, y1, z, zn=1):
    """Jasna krawędź pionowa z dwóch odcinków złamanych o 5° (ręcznie rysowany blik, nie listwa). 2 części."""
    h = y1 - y0
    with s.cechy(kolizja=False, cien=False):
        s.blok(nazwa, (x, y0 + h * 0.3, z), (0.9, h * 0.6, 0.9), JASNY)
        with s.uklad(pos=(x, y0 + h * 0.58, z), obrot=(0, 0, 5 * zn)):
            s.blok(nazwa, (0, h * 0.2, 0.05), (0.9, h * 0.42, 0.9), JASNY)


def _rysa(s, pos, ry, segmenty):
    """Pęknięcie skały: jasny zygzak z łamanej (dł, kąt względny°) grubości 0,6 na licu; pos = początek na licu,
    ry = obrót lica (90 = ściana +X, −90 = −X, 180 = tył). n części."""
    with s.uklad(pos=pos, obrot=(0, ry, 0)), s.cechy(kolizja=False, cien=False):
        zestaw.lamana(s, "Rysa", [(dl, 0.6, k) for dl, k in segmenty], JASNY, z=0.1, glebokosc=0.4)


def _kolec(s, nazwa, pos, h, a, obrot, kolor):
    """Kolec skalny / kryształ: ostrosłup 2a × 2a × h w układzie pochylonym, podstawa wpuszczona 0,4. 4 części."""
    with s.uklad(pos=pos, obrot=obrot), s.cechy(kolizja=False):
        s.ostroslup(nazwa, (0, -0.4, 0), a, a, h + 0.4, kolor, "Neon" if kolor.startswith("neon_") else "SmoothPlastic")


# --------------------------------------------------------------------------- masyw
def _masyw(s, ciemny):
    """Bloki skały: każdy obrócony o 4–10°, lewa część do 34, prawa do 26, góra szersza od dołu (paszcza = trójkąt w dół)."""
    # rdzeń za portalem (ukryty z przodu, widoczny z tyłu)
    with s.uklad(pos=(0.0, 0.0, -4.2), obrot=(0, 5, 0)):
        s.blok("Skała rdzeń", (0, 9.0, 0), (13.0, 18.0, 10.0), ciemny)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Skała rdzeń krawędź", (0, 17.7, -5.05), (11.6, 0.9, 0.9), JASNY)
    # dół (szczęki): pionowe, tylko skręt ry; węższe od góry
    with s.uklad(pos=(-9.9, 0.0, -1.5), obrot=(0, -6, 0)):
        s.blok("Skała lewa dół", (0, 6.75, 0), (7.6, 13.5, 14.5), SKALA)
        _krawedz(s, "Skała lewa krawędź", -3.55, 0.2, 13.2, 7.0, -1)
        _krawedz(s, "Skała lewa krawędź", -3.55, 0.2, 12.6, -7.0, -1)
    with s.uklad(pos=(9.9, 0.0, -1.5), obrot=(0, 7, 0)):
        s.blok("Skała prawa dół", (0, 6.0, 0), (7.6, 12.0, 14.5), SKALA)
        _krawedz(s, "Skała prawa krawędź", 3.55, 0.2, 11.7, 7.0, 1)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Skała prawa półka", (-0.4, 12.0, 7.0), (6.4, 0.9, 0.9), JASNY)
    # góra (policzki): szersza, wystaje na boki ponad szczęki
    with s.uklad(pos=(-10.3, 12.5, -1.6), obrot=(-4, 7, 6)):
        s.blok("Skała lewa góra", (0, 7.5, 0), (10.0, 15.0, 13.0), ciemny)
        _krawedz(s, "Skała lewa góra krawędź", -4.75, 0.3, 14.6, 6.7, 1)
        _krawedz(s, "Skała lewa góra krawędź", -4.75, 0.3, 13.8, -6.7, 1)
        _czapa_mchu(s, 10.0, 13.0, 15.0, kapki_tyl=((-3.4, 3.2), (1.6, 1.8)))       # kołnierz mchu pod koroną
        with s.cechy(kolizja=False, cien=False):
            s.blok("Skała lewa góra spód", (-0.3, 0.3, 6.7), (9.0, 0.9, 0.9), JASNY)
    with s.uklad(pos=(10.3, 11.5, -1.6), obrot=(-5, -7, -7)):
        s.blok("Skała prawa góra", (0, 6.0, 0), (10.0, 12.0, 13.0), ciemny)
        _krawedz(s, "Skała prawa góra krawędź", 4.75, 0.3, 11.6, 6.7, -1)
        _krawedz(s, "Skała prawa góra krawędź", 4.75, 0.3, 11.0, -6.7, -1)
        _czapa_mchu(s, 10.0, 13.0, 12.0, kapki=((3.8, 2.0),), kapki_tyl=((-2.6, 2.4), (3.0, 3.4)))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Skała prawa góra spód", (0.3, 0.3, 6.7), (9.0, 0.9, 0.9), JASNY)
        _kolec(s, "Kryształ", (4.6, 9.0, 0.4), 3.8, 1.0, (-25, 15, -22), MECH)        # kryształy z boku policzka:
        _kolec(s, "Kryształ", (4.6, 6.4, -2.6), 2.5, 0.75, (20, -10, -30), MECH)     # łamią prawą sylwetkę
    # czoło nad paszczą (18,4–28,4): nawis nad łukiem, na nim oczy
    with s.uklad(pos=(-0.6, 18.4, 1.4), obrot=(-4, 6, 5)):
        s.blok("Skała czoło", (0, 5.0, 0), (15.0, 10.0, 12.0), SKALA)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Czoło warga", (0, 0.3, 6.1), (14.4, 0.9, 0.9), JASNY)
        _czapa_mchu(s, 8.0, 12.0, 10.0, kapki=((-2.0, 2.6), (2.4, 1.6)), kapki_tyl=((0.5, 2.2),), dx=3.4)
        _kolec(s, "Kolec skalny", (3.4, 10.6, -2.4), 3.0, 1.2, (-8, 30, -13), ciemny)
        # po krytyce: poszarpana korona zamiast płaskich tarasów (kliny narożne 3–5 skręcone ±15°)
        s.naroznik("Skała ząb", (-4.6, 11.6, -1.2), (5.0, 4.0, 5.0), SKALA, rot=(0, 15, 0))
    # lewa korona (do 34 z kolcem)
    with s.uklad(pos=(-8.6, 26.9, -1.2), obrot=(6, -10, -11)):
        s.blok("Skała lewa korona", (0, 2.4, 0), (11.0, 4.8, 11.0), SKALA)
        _czapa_mchu(s, 11.0, 11.0, 4.8, kapki=((-3.6, 3.0), (1.0, 1.8), (3.8, 2.4)), kapki_tyl=((-2.0, 2.6), (2.6, 1.6)))
        _kolec(s, "Kolec skalny", (-3.2, 5.3, 1.6), 2.4, 1.5, (10, 15, 16), SKALA)
        s.naroznik("Skała ząb", (2.8, 5.9, -2.0), (4.5, 3.0, 4.5), ciemny, rot=(0, 165, 0))
    # prawa korona (do 26)
    with s.uklad(pos=(10.4, 22.4, -2.4), obrot=(5, 11, -9)):
        s.blok("Skała prawa korona", (0, 1.6, 0), (8.6, 3.2, 9.0), SKALA)
        _czapa_mchu(s, 8.6, 9.0, 3.2, kapki=((-2.2, 2.2), (2.0, 1.4)), kapki_tyl=((1.0, 2.0),))
        s.naroznik("Skała ząb", (-1.4, 5.3, 0.8), (5.0, 5.0, 5.0), SKALA, rot=(0, 15, 0))
        s.naroznik("Skała ząb", (2.8, 4.3, -2.4), (3.5, 3.0, 3.5), ciemny, rot=(0, -105, 0))


# --------------------------------------------------------------------------- gardziel: filary, łuk, portal, zęby, język
def _gardziel(s, ciemny):
    zc = (Z_TYL + Z_LICO) / 2.0
    gl = Z_LICO - Z_TYL
    # filary: lewy rz −6°, prawy rz +5° (szczyty pochylone do środka — paszcza zwęża się ku górze)
    for strona, x0, rz in ((-1, -6.0, -6.0), (1, 6.0, 5.0)):
        with s.uklad(pos=(x0, 0.0, zc), obrot=(0, 0, rz)):
            s.blok("Filar", (strona * 1.6, 4.9, 0), (3.2, 9.8, gl), SKALA)
            with s.cechy(kolizja=False, cien=False):          # jasny obrys krawędzi przejścia, 0,3 za licem
                s.blok("Filar obrys", (-strona * 0.2, 5.05, -0.1), (1.2, 9.9, gl - 0.4), JASNY)
    # łuk: 11 klińców (co drugi głębszy o 0,2 i ciemniejszy) na jasnym pierścieniu
    n = 11
    st_k = 2.0 * (R_IN + GRUB) * math.tan(math.radians(90.0 / n)) * 1.02
    r_out = R_IN + GRUB + RIM
    st_r = 2.0 * r_out * math.tan(math.radians(90.0 / n)) * 1.02
    for i in range(n):
        phi = 180.0 * (i + 0.5) / n
        c, sn = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        rk = R_IN + GRUB / 2.0
        z0 = Z_TYL - (0.1 if i % 2 else 0.0)
        gleb = Z_LICO + (0.2 if i % 2 else 0.0) - z0
        with s.uklad(pos=(AX + rk * c, AY + rk * sn, 0.0), obrot=(0, 0, phi - 90.0)):
            s.blok("Kliniec", (0, 0, z0 + gleb / 2.0), (st_k, GRUB, gleb), SKALA if i % 2 == 0 else ciemny)
        rr = (R_IN - RIM + r_out) / 2.0
        with s.uklad(pos=(AX + rr * c, AY + rr * sn, 0.0), obrot=(0, 0, phi - 90.0)), s.cechy(kolizja=False, cien=False):
            s.blok("Łuk obrys", (0, 0, (Z_TYL + 0.1 + Z_LICO - 0.3) / 2.0), (st_r, r_out - R_IN + RIM, Z_LICO - 0.3 - Z_TYL - 0.1), JASNY)
    # portal: płyta neon_portal 12 × 14 w głębi 3 i wir z czterech kwadratów skręcanych coraz mocniej
    wir = cien(s, MECH, 0.62)
    with s.cechy(kolizja=False, cien=False):
        s.blok("Portal", (AX, 7.1, Z_PORTAL), (12.4, 14.2, 0.3), "neon_portal", "Neon")
        for i, (a, kol, kat, dx, dy) in enumerate(((9.6, wir, 12, 0.0, 7.3), (7.2, "neon_portal", 33, 0.2, 7.5),
                                                    (4.8, wir, 57, 0.35, 7.7), (2.4, "neon_portal", 84, 0.45, 7.85))):
            s.blok("Portal wir", (AX + dx, dy, Z_PORTAL + 0.25 + 0.22 * i), (a, a, 0.2), kol,
                   "Neon" if kol.startswith("neon_") else "SmoothPlastic", rot=(0, 0, kat))
    # zęby górne: rząd 7 kłów 1,5–3 (każdy inny, dwa „kły” najdłuższe), korzenie schowane za jasnym obrysem łuku
    r_rim = R_IN - RIM
    zeby = ((-3.75, 2.0, 1.3, 0), (-2.5, 2.9, 1.5, 6), (-1.25, 1.6, 1.2, -4), (0.0, 1.5, 1.4, 3),
            (1.25, 1.8, 1.2, -5), (2.5, 3.0, 1.6, -7), (3.75, 2.2, 1.3, 4))
    for i, (x, dl, sz, kat) in enumerate(zeby):
        y = AY + math.sqrt(r_rim ** 2 - (x - AX) ** 2) + 0.45
        with s.uklad(pos=(AX + x, y, 5.45 + 0.1 * (i % 2)), obrot=(0, 0, kat)):
            _zab(s, dl + 0.45, sz, w_dol=True)
    # zęby dolne: tylko po bokach progu
    for x, dl, sz, kat in ((-4.7, 2.2, 1.6, -9), (4.8, 1.7, 1.4, 10)):
        with s.uklad(pos=(x, 0.0, Z_LICO - 0.4), obrot=(0, 0, kat)):
            _zab(s, dl, sz, w_dol=False)
    # język: płyta 8 × 0,3 od progu do krawędzi działki, zaokrąglony koniuszek, bruzda
    with s.cechy(kolizja=False, cien=False):
        s.blok("Język", (AX, 0.15, 4.75), (7.6, 0.3, 3.1), "dach_kolo")
        s.walec("Język koniec", (AX, 0.15, 6.0), 3.8, 0.3, "dach_kolo", os="y")
        s.blok("Język bruzda", (AX, 0.36, 6.4), (0.5, 0.2, 4.6), cien(s, "dach_kolo", 0.75))
    # pochodnie z zielonym ogniem po bokach paszczy
    for x, zn in ((-8.6, 1), (8.7, -1)):
        with s.uklad(pos=(x, 7.2, 6.0), obrot=(0, 0, 8 * zn)), s.cechy(kolizja=False):
            s.blok("Pochodnia uchwyt", (0, -0.9, 0.5), (0.6, 2.4, 0.6), JASNY)
            s.blok("Pochodnia czasza", (0, 0.5, 0.6), (1.6, 0.8, 1.6), "zloto", rot=(0, 45, 0))
            with s.cechy(cien=False):
                s.blok("Pochodnia ogień", (0, 1.7, 0.6), (1.3, 1.3, 1.3), "neon_portal", "Neon", rot=(35, 45, 0))
                s.blok("Pochodnia iskra", (0.5 * zn, 3.0, 0.6), (0.6, 0.6, 0.6), MECH, rot=(20, 30, 40))


def _zab(s, dl, sz, w_dol=True):
    """Kieł równoramienny w płaszczyźnie XY z 2 klinów (podstawa sz, długość dl): (0,0,0) = środek podstawy, w_dol →
    szpic ku lokalnemu −Y. Biel z podkładką tusz (większa o 0,4, cofnięta 0,35). 4 części."""
    zn_y = -1 if w_dol else 1
    rz = 180 if w_dol else 0
    with s.cechy(kolizja=False):
        for kol, d_l, d_s, z in (("tusz", 0.8, 0.8, -0.55), ("biel", 0.0, 0.0, 0.0)):
            L, W = dl + d_l, sz + d_s
            yc = zn_y * (L / 2.0 - (0.25 if d_l else 0.0))
            with s.cechy(cien=(kol == "tusz")):                # lewa połówka: pion po +X (ry 90), prawa: po −X
                s.klin("Ząb obrys" if d_l else "Ząb", (-W / 4.0, yc, z), (0.5, L, W / 2.0), kol, rot=(0, 90, rz))
                s.klin("Ząb obrys" if d_l else "Ząb", (W / 4.0, yc, z), (0.5, L, W / 2.0), kol, rot=(0, -90, rz))


# --------------------------------------------------------------------------- twarz: oczy i brwi
def _twarz(s):
    """Oczy Ø 4 na 27 (lewe) i 24 (prawe), źrenice patrzą w różne strony; brwi z mchu, jedna uniesiona."""
    with s.cechy(kolizja=False):
        for nazwa, (x, y, z), kier, brew in (
                ("lewe", (-4.4, 27.0, 7.4), (0.42, -0.38, 0.82), (14, 2.9, 5.2)),
                ("prawe", (3.6, 24.0, 7.7), (-0.25, 0.48, 0.84), (-9, 2.6, 4.4))):
            s.kula("Oko " + nazwa, (x, y, z), 4.0, "biel")
            d = math.sqrt(sum(v * v for v in kier))
            k = [v / d for v in kier]
            rx = -math.degrees(math.asin(k[1]))
            ry = math.degrees(math.atan2(k[0], k[2]))
            with s.uklad(pos=(x + k[0] * 1.75, y + k[1] * 1.75, z + k[2] * 1.75), obrot=(rx, ry, 0)), s.cechy(cien=False):
                s.walec("Źrenica", (0, 0, 0), 0.85, 0.7, "tusz", os="z")
            kat, dy, dl = brew
            with s.uklad(pos=(x, y + dy, z - 0.3), obrot=(0, 0, kat)):
                s.blok("Brew", (0, 0, 0), (dl, 1.0, 1.6), MECH)
                s.blok("Brew rant", (0, -0.25, -0.15), (dl + 0.5, 0.9, 1.6), "tusz")


# --------------------------------------------------------------------------- kryształy
def _krysztaly(s):
    """Ostrosłupy 2–7 po bokach paszczy: największy neon_portal, reszta dach_lochy."""
    _kolec(s, "Kryształ wielki", (-12.0, 0.0, 6.4), 7.0, 1.35, (6, 40, 14), "neon_portal")
    _kolec(s, "Kryształ", (-9.6, 0.0, 8.3), 3.0, 0.8, (-12, 20, -18), MECH)
    _kolec(s, "Kryształ", (-13.6, 0.0, 3.6), 2.0, 0.6, (10, 60, 22), MECH)
    _kolec(s, "Kryształ", (11.6, 0.0, 7.0), 5.0, 1.1, (6, 30, -16), MECH)
    _kolec(s, "Kryształ", (9.6, 0.0, 8.4), 2.6, 0.7, (-8, 10, 20), MECH)
    _kolec(s, "Kryształ", (12.4, 0.0, -3.4), 4.0, 0.9, (8, 25, -12), MECH)
    _kolec(s, "Kryształ", (-11.4, 0.0, -7.6), 3.4, 0.9, (-10, 15, 14), MECH)


# --------------------------------------------------------------------------- szyld: krzywy trójkąt ostrzegawczy z czaszką
def _szyld(s):
    """Trójkąt 9 (`zloto`, rama `tusz`) na jednym gwoździu, obrót −25° (zwisa na zewnątrz, poza bryłę), przechył 11° ku
    rynkowi; środek na 16, po lewej. 14 części."""
    with s.uklad(pos=(-11.9, 19.8, 6.9), obrot=(11, 8, -25)), s.cechy(kolizja=False):
        _trojkat(s, "Szyld rama", 9.0, 1.0, -0.25, 0.4, "tusz")
        _trojkat(s, "Szyld", 7.6, 0.19, 0.2, 0.4, "zloto")
        with s.cechy(cien=False):
            s.walec("Szyld gwóźdź", (0, -1.2, 0.5), 0.45, 0.9, "tusz", os="z")
            cy = -4.0
            s.blok("Czaszka obrys", (0, cy, 0.5), (3.4, 2.8, 0.2), "tusz")
            s.blok("Czaszka obrys", (0, cy - 1.55, 0.5), (2.3, 1.6, 0.2), "tusz")
            s.blok("Czaszka", (0, cy, 0.65), (2.8, 2.2, 0.3), "biel")
            s.blok("Czaszka szczęka", (0, cy - 1.55, 0.65), (1.7, 1.0, 0.3), "biel")
            for x in (-0.65, 0.65):
                s.blok("Czaszka oczodół", (x, cy + 0.05, 0.85), (0.8, 0.8, 0.2), "tusz")
                s.blok("Czaszka ząb", (x * 0.55, cy - 1.55, 0.85), (0.25, 0.6, 0.2), "tusz")
            s.blok("Czaszka nos", (0, cy - 0.75, 0.85), (0.4, 0.4, 0.2), "tusz", rot=(0, 0, 45))


def _trojkat(s, nazwa, bok, y_gora, z, grub, kolor):
    """Trójkąt równoboczny wierzchołkiem w górę w płaszczyźnie XY z 2 klinów; y_gora = wierzchołek."""
    h = bok * math.sqrt(3) / 2.0
    for zn in (1, -1):
        s.klin(nazwa, (-zn * bok / 4.0, y_gora - h / 2.0, z), (grub, h, bok / 2.0), kolor, rot=(0, 90 * zn, 0))


# --------------------------------------------------------------------------- żart: zerwany łańcuch i otwarta kłódka
def _zart(s):
    """Łańcuch z 8 ogniw zwisa z łuku po lewej, przed portalem (ciemny na zielonym), zerwane ogniwo i otwarta kłódka
    leżą na języku. 20 części."""
    phi = 156.0
    x0 = AX + (R_IN - RIM + 0.2) * math.cos(math.radians(phi))
    y0 = AY + (R_IN - RIM + 0.2) * math.sin(math.radians(phi))
    with s.uklad(pos=(x0, y0, 6.55), obrot=(0, 0, 5)), s.cechy(kolizja=False, cien=False):
        s.blok("Łańcuch skoba", (0, 0.2, 0), (1.4, 0.7, 0.8), "metal_ciemny")
        for i in range(8):
            y = -0.9 - 1.15 * i
            if i % 2 == 0:                                     # ogniwo widziane z przodu: dwa boki
                for x in (-0.42, 0.42):
                    s.blok("Ogniwo", (x, y, 0), (0.3, 1.6, 0.35), "metal_ciemny")
            else:                                              # ogniwo widziane z boku
                s.blok("Ogniwo", (0, y, 0), (0.35, 1.6, 0.9), "metal_ciemny")
    # zerwane ogniwo na ziemi
    with s.uklad(pos=(-1.6, 0.0, 9.0), obrot=(0, 35, 0)), s.cechy(kolizja=False, cien=False):
        for x in (-0.42, 0.42):
            s.blok("Ogniwo zerwane", (x, 0.5, 0), (0.3, 0.35, 1.6), "metal_ciemny")
    # kłódka: korpus zloto, otwarty pałąk, dziurka; leży przechylona obok języka
    with s.uklad(pos=(-4.6, 0.0, 8.4), obrot=(0, 24, -14)), s.cechy(kolizja=False):
        s.blok("Kłódka", (0, 1.2, 0), (2.8, 2.4, 1.4), "zloto")
        with s.cechy(cien=False):
            s.blok("Kłódka dziurka", (0, 1.05, 0.75), (0.5, 0.9, 0.2), "tusz")
            s.blok("Kłódka pałąk", (-0.9, 3.0, 0), (0.5, 1.8, 0.6), "metal_ciemny")
            with s.uklad(pos=(-0.9, 3.8, 0), obrot=(0, 0, -50)):
                s.blok("Kłódka pałąk", (0.9, 0, 0), (2.2, 0.5, 0.6), "metal_ciemny")
                s.blok("Kłódka pałąk", (1.8, -0.7, 0), (0.5, 1.5, 0.6), "metal_ciemny")


# --------------------------------------------------------------------------- znaki miasteczka i drobiazgi
def _znaki(s, rnd):
    # łata z fastrygą na lewym dole (ktoś zacerował pęknięcie w skale)
    with s.uklad(pos=(-9.9, 0.0, -1.5), obrot=(0, -6, 0)):
        zestaw.lata(s, (-0.6, 8.2, 7.25), 2.8, 2.4, JASNY, przechyl=-9)
    # druga łata (złota) na prawym policzku
    with s.uklad(pos=(10.3, 11.5, -1.6), obrot=(-5, -7, -7)):
        zestaw.lata(s, (-1.2, 6.2, 6.5), 2.6, 2.2, "zloto", przechyl=11)
    # wypadnięty klocek z prawego dołu
    with s.uklad(pos=(9.9, 0.0, -1.5), obrot=(0, 7, 0)):
        zestaw.wypadniety_klocek(s, (1.2, 4.2, 7.25), (2.4, 0.0, 9.0), SKALA, obrot_klocka=24)
    # chorągiewka Rycerza wbita w prawą koronę
    with s.uklad(pos=(10.4, 22.4, -2.4), obrot=(5, 11, -9)):
        zestaw.choragiewka_duetu(s, (2.0, 3.6, 1.0), "rycerz", przechyl=-12)
    # rysy (jasne zygzaki) na bokach i z tyłu — budynek oglądany z każdej strony; mech spływający z tyłu
    with s.uklad(pos=(10.3, 11.5, -1.6), obrot=(-5, -7, -7)):                   # prawy bok prawej góry
        _rysa(s, (5.2, 1.8, 2.0), 90, ((2.6, 30), (2.2, -55), (2.4, 45), (1.6, -40)))
    with s.uklad(pos=(-10.3, 12.5, -1.6), obrot=(-4, 7, 6)):                    # lewy bok lewej góry
        _rysa(s, (-5.2, 3.0, -1.5), -90, ((2.4, -25), (2.6, 50), (2.0, -45)))
    with s.uklad(pos=(0.0, 0.0, -4.2), obrot=(0, 5, 0)):                        # tył rdzenia
        _rysa(s, (2.0, 5.0, -5.2), 180, ((2.8, 20), (2.4, -50), (2.6, 45), (2.0, -35)))
        with s.cechy(kolizja=False, cien=False):
            s.blok("Mech strużka", (-3.0, 14.4, -5.35), (1.6, 7.0, 0.5), MECH)
            s.blok("Mech strużka", (-2.2, 10.6, -5.35), (1.0, 2.4, 0.5), MECH, rot=(0, 0, 12))
    with s.uklad(pos=(9.9, 0.0, -1.5), obrot=(0, 7, 0)):                        # prawy bok prawego dołu
        _rysa(s, (3.95, 2.0, -3.0), 90, ((2.2, -20), (2.4, 45), (1.8, -50)))
    # kamienie u stóp
    zestaw.kamien(s, (12.0, 0, 2.4), rnd, 3.0, SKALA, "Slate")
    zestaw.kamien(s, (-12.6, 0, -6.0), rnd, 3.0, SKALA, "Slate")
    zestaw.kamien(s, (12.0, 0, -7.4), rnd, 2.6, SKALA, "Slate", dwa=False)
