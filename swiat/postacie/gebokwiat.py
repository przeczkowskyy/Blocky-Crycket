# -*- coding: utf-8 -*-
"""GĘBOKWIAT — zwykły przeciwnik Dżungli (Kwietnik Gębokwiatów): wielki kwiat z paszczą na krótkich
korzeniach-nóżkach, ok. 5,0 studa (gracz ma 5,7).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/gebokwiat.py --wyj <folder> --klip umiejetnosc

Opis z zarysu biomów (swiat/biomy/PLAN_BIOMOW.md, rozdz. „2. Dżungla”): kwiat z paszczą na krótkich
korzeniach-nóżkach, sypie usypiający pyłek. Klasa w przegrodzie: Mag. Zwykły cios = kłapnięcie paszczą; umiejętność
silnika `lodowy_pocisk` = w grze usypiający pyłek: kwiat zamyka płatki w pąk, nabiera powietrza i z rozwartej paszczy
wypluwa kulę pyłku (punkt Pocisk w paszczy).

Sylwetka (z daleka): czerwona tarcza ośmiu płatków (E5392B) na grubej zielonej łodydze, w środku żółta tarcza
(F2B030) przecięta paszczą z kremowymi zębami i para oczu nad nią; po bokach łodygi dwa wielkie liście-ręce; na dole
cebulka z liśćmi i dwie krótkie nóżki z rozczapierzonych korzeni (pnie 5C3A22). Płatki mają ciemniejszą nasadę
i żółte czubki (czytelne na zielonym tle).

Paleta (Dżungla): zieleń 2FA34A i 6CCB4A (łodyga, liście, cebulka), pnie 5C3A22 (korzenie), kwiaty E5392B / F2B030
(płatki, tarcza), turkus 2EC4B6 (krople rosy na liściach), wnętrze paszczy ciemna czerwień, kremowe zęby.

Szkielet (typ „stwor”; L = lewa = +X, P = prawa = −X):
    Root > Cialo > {NogaL > StopaL, NogaP > StopaP,
                    Lodyga1 > {LiscL, LiscP, Lodyga2 > Glowa > {Szczeka, PlatkiG, PlatkiD, PlatkiL, PlatkiP}}}
- `Cialo` = cebulka (niesie całość); Stopa* trzymane płasko na ziemi (liczone w module);
- `Glowa` = górna połowa żółtej tarczy z oczami, `Szczeka` = dolna połowa (paszcza otwiera się w dół i do przodu);
- cztery kości płatków (góra, dół, lewo, prawo) obracają się na krawędzi tarczy: płatki składają się w pąk do przodu
  albo odchylają do tyłu (bez kanału skali).

Klipy (30 kl./s; kwiat patrzy w +Z):
  idle (pętla 2,4 s: łodyga kołysze się, płatki oddychają na zmianę, liście falują), ruch (pętla 1,0 s: drepcze na
  korzeniach, łodyga kiwa się w przeciwfazie), atak (zamach w tył z rozwartą paszczą i kłapnięcie przed sobą,
  trafienie kl. 13, 0,9 s), umiejetnosc (usypiający pyłek: płatki zamykają się w pąk, kwiat nabiera powietrza
  i drży, płatki rozkwitają, paszcza rozwarta — wypluwa pyłek kl. 30; 1,8 s), trafienie (szarpnięcie w tył, płatki
  trzepoczą, 0,6 s), unik (podskok w lewo 1,5 studa i powrót, 0,9 s), upadek (więdnie: łodyga gnie się w tył i na
  bok, kwiat opada na ziemię, płatki zwisają; 2 s, leży w ostatniej klatce), wiwat (pętla 2 s: podskoki, liście
  w górze, płatki trzepoczą).
Klipy są zapisane jako pozy kluczowe zamienione na klucz w KAŻDEJ klatce (wygładzanie „liniowo”).
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Postac, katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor

ID = "gebokwiat"

PALETA = {
    "lodyga": "2FA34A", "lodyga_jasna": "6CCB4A", "lodyga_ciemna": "1F7A36", "zylka": "A6E07A",
    "platek": "E5392B", "platek_nasada": "B32424", "platek_czubek": "F2B030",
    "tarcza": "F2B030", "tarcza_ciemna": "D98E1E", "paszcza": "6E1420", "jezyk": "D9667A",
    "zab": "F4EEDC", "tusz": "17121F", "bialy": "FFFFFF", "korzen": "5C3A22", "korzen_jasny": "7A5232",
    "rosa": "2EC4B6",
}

CHWILE = {"atak": 13, "umiejetnosc": 30, "trafienie": 4, "unik": 12}

SLABOSCI = [
    "Kości Gębokwiatu nie są R15 (własny szkielet: Root + 15 kości) — import do Roblox Studio nie był testowany.",
    "Pyłku nie ma w klipie: w grze pocisk umiejętności lodowy_pocisk rysuje odtwarzacz (dziś jako lodowy pocisk — "
    "wygląd pyłku wymaga osobnego wpisu w Choreografie/Efekty3D, poza tym modułem).",
    "Płatki to cztery sztywne grupy na krawędzi tarczy — przy zamknięciu w pąk sąsiednie płatki lekko na siebie "
    "zachodzą.",
    "Nóżki są jednoczęściowe (bez kolan): krok to wymach całej nóżki i kołysanie cebulki; stopy w podporze ślizgają się.",
    "Liście-ręce są płaskie (bez wygięcia), żyłka to jaśniejszy pasek.",
]

# ----------------------------------------------------------------------------------------------- szkielet (studs)
CIALO = (0.0, 0.9, 0.0)
BIODRO = (0.45, 0.62, 0.0)
KOSTKA = (0.55, 0.16, 0.06)
LODYGA1 = (0.0, 1.45, 0.0)
LODYGA2 = (0.0, 2.45, 0.08)
GLOWA = (0.0, 3.15, 0.22)
TARCZA = (0.0, 3.38, 0.48)          # środek żółtej tarczy (paszcza na wysokości środka)
SZCZEKA = (0.0, 3.38, 0.32)         # zawias paszczy (tył tarczy, na linii ust)
R_TARCZY = 0.7
LISC = (0.26, 2.15, 0.06)            # nasada lewego liścia na łodydze
KONIEC_LISCIA = (1.55, 2.75, 0.3)

GLOWNA = "Cialo"
PLASKIE = ("StopaL", "StopaP")
POMIN_ZIEMIA = ()


def _lu(v, zn):
    return (zn * v[0], v[1], v[2])


def _roznica(a, b):
    return tuple(b[i] - a[i] for i in range(3))


def _na_tarczy(kat, r, dz=0.0):
    """Punkt w płaszczyźnie tarczy (kąt od lewej, przeciwnie do wskazówek patrząc od przodu)."""
    a = math.radians(kat)
    return (TARCZA[0] + r * math.cos(a), TARCZA[1] + r * math.sin(a), TARCZA[2] + dz)


def _os_kosci():
    o = {}
    for s, zn in (("L", 1.0), ("P", -1.0)):
        o["Noga" + s] = _roznica(_lu(BIODRO, zn), _lu(KOSTKA, zn))
        o["Lisc" + s] = _roznica(_lu(LISC, zn), _lu(KONIEC_LISCIA, zn))
    o["Lodyga1"] = _roznica(LODYGA1, LODYGA2)
    o["Lodyga2"] = _roznica(LODYGA2, GLOWA)
    return o


OS = _os_kosci()


def _model(p, kosc, obrot=(0, 0, 0), pos=(0, 0, 0)):
    """Układ MODELU (0, 0, 0 = ziemia pod środkiem) na kości: bryły podaje się we współrzędnych modelu."""
    s = p.staw(kosc)
    return p.na(kosc, pos=(pos[0] - s[0], pos[1] - s[1], pos[2] - s[2]), obrot=obrot)


def zbuduj():
    p = Postac(ID, "Gębokwiat", typ="stwor", skala=1.0, faza=0.05, paleta=PALETA)

    p.kosc("Cialo", "Root", staw=CIALO, dl=0.5)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Noga" + s, "Cialo", staw=_lu(BIODRO, zn), dl=0.3)
        p.kosc("Stopa" + s, "Noga" + s, staw=_lu(KOSTKA, zn), dl=0.2)
    p.kosc("Lodyga1", "Cialo", staw=LODYGA1, dl=0.8)
    for s, zn in (("L", 1.0), ("P", -1.0)):
        p.kosc("Lisc" + s, "Lodyga1", staw=_lu(LISC, zn), dl=0.6)
    p.kosc("Lodyga2", "Lodyga1", staw=LODYGA2, dl=0.6)
    p.kosc("Glowa", "Lodyga2", staw=GLOWA, dl=0.5)
    p.kosc("Szczeka", "Glowa", staw=SZCZEKA, dl=0.4)
    p.kosc("PlatkiG", "Glowa", staw=_na_tarczy(90, R_TARCZY, -0.1), dl=0.3)
    p.kosc("PlatkiD", "Glowa", staw=_na_tarczy(270, R_TARCZY, -0.1), dl=0.3)
    p.kosc("PlatkiL", "Glowa", staw=_na_tarczy(0, R_TARCZY, -0.1), dl=0.3)
    p.kosc("PlatkiP", "Glowa", staw=_na_tarczy(180, R_TARCZY, -0.1), dl=0.3)

    _nogi(p)
    _cebulka(p)
    _lodyga(p)
    _liscie(p)
    _tarcza(p)
    _platki(p)

    p.zaczep("RootAttachment", "Cialo", (-CIALO[0], -CIALO[1], -CIALO[2]))
    # cel trafienia: środek tarczy kwiatu
    p.zaczep("GlowaAttachment", "Glowa", _roznica(GLOWA, (0.0, 3.45, 0.55)))
    # paszcza: tuż przed zębami na linii ust (Bron przy kłapnięciu, Pocisk = skąd leci pyłek)
    p.zaczep("PaszczaAttachment", "Glowa", _roznica(GLOWA, (0.0, 3.45, 0.82)))

    _klipy(p)
    p.ustaw_poze_renderu("idle", 0)
    return p


# ---------------------------------------------------------------------------------------------------- bryły
def _plyta(p, nazwa, a, b, szer, grub, kolor, mat="matowy", skret=0.0, faza=0.0):
    """Płaska płytka od a do b (szerokość w poprzek, grubość cienka), skręcona wokół swojej osi o `skret` stopni."""
    d = tuple(b[i] - a[i] for i in range(3))
    L = math.sqrt(sum(x * x for x in d))
    sr = tuple((a[i] + b[i]) / 2.0 for i in range(3))
    rot = katy_z_macierzy(_obrot_miedzy((0.0, 1.0, 0.0), d))
    with p.uklad(pos=sr, obrot=rot):
        p.blok(nazwa, (0, 0, 0), (szer, L, grub), kolor, mat, rot=(0, skret, 0), faza=faza)
    return sr, rot


def _nogi(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Noga" + s):
            _belka(p, "Nozka", _lu((0.45, 0.72, 0.0), zn), _lu(KOSTKA, zn), 0.42, 0.42, "korzen", "matowy", nad=0.05)
            _belka(p, "Wlokno", _lu((0.62, 0.62, 0.12), zn), _lu((0.68, 0.24, 0.16), zn), 0.12, 0.12, "korzen_jasny",
                   "matowy")
        with _model(p, "Stopa" + s):
            p.blok("Stopa", _lu((0.55, 0.1, 0.12), zn), (0.5, 0.2, 0.55), "korzen", "matowy", faza=0.06)
            # rozczapierzone korzonki-palce
            for i, (ry, dl) in enumerate(((-40, 0.55), (-5, 0.65), (35, 0.55), (150, 0.45))):
                kat = math.radians(ry * zn)
                a = (zn * 0.55, 0.07, 0.15)
                b = (a[0] + math.sin(kat) * dl, 0.05, a[2] + math.cos(kat) * dl)
                _belka(p, "Korzonek %d" % i, a, b, 0.13, 0.13, "korzen", "matowy", nad=0.04)


def _cebulka(p):
    with _model(p, "Cialo"):
        p.kula("Cebulka", (0, 1.02, 0.0), (1.62, 1.12, 1.5), "lodyga_ciemna", "matowy", segm=10)
        p.walec("Cebulka gora", (0, 1.52, 0.0), (0.8, 0.22, 0.8), "lodyga", "matowy", segm=8)
        p.walec("Cebulka dol", (0, 0.52, 0.0), (1.0, 0.16, 0.9), "korzen", "matowy", segm=8)
        # pasy na cebulce (jak łuski)
        for zn in (1, -1):
            p.blok("Luska", (zn * 0.4, 1.04, 0.62), (0.1, 0.42, 0.06), "lodyga", "matowy", rot=(0, zn * 25, 0),
                   faza=0.0)
        p.blok("Luska srodek", (0, 1.04, 0.73), (0.1, 0.42, 0.04), "lodyga_jasna", "matowy", faza=0.0)
        # liście u nasady (niskie, sterczą na boki i do tyłu)
        for i, (kat, h) in enumerate(((20, 0.55), (160, 0.5), (215, 0.6), (325, 0.55), (265, 0.45))):
            a = math.radians(kat)
            baza = (0.5 * math.cos(a), 1.25, 0.45 * math.sin(a))
            koniec = (1.05 * math.cos(a), 1.25 + h, 0.9 * math.sin(a))
            _plyta(p, "Lisc nasady %d" % i, baza, koniec, 0.34, 0.06, "lodyga_jasna" if i % 2 else "lodyga",
                   skret=kat + 90)


def _lodyga(p):
    with _model(p, "Lodyga1"):
        _belka(p, "Lodyga dol", LODYGA1, LODYGA2, 0.55, 0.55, "lodyga", "matowy", nad=0.1)
        p.blok("Wezel", (0, 2.2, 0.06), (0.66, 0.16, 0.66), "lodyga_ciemna", "matowy", faza=0.04)
        p.blok("Pasek lodygi", (0, 1.95, 0.32), (0.12, 0.8, 0.04), "lodyga_jasna", "matowy", faza=0.0)
    with _model(p, "Lodyga2"):
        _belka(p, "Lodyga gora", LODYGA2, GLOWA, 0.48, 0.48, "lodyga", "matowy", nad=0.12)
        p.blok("Pasek lodygi 2", (0, 2.8, 0.38), (0.11, 0.6, 0.04), "lodyga_jasna", "matowy", rot=(-10, 0, 0),
               faza=0.0)


def _liscie(p):
    for s, zn in (("L", 1.0), ("P", -1.0)):
        with _model(p, "Lisc" + s):
            a, b = _lu(LISC, zn), _lu(KONIEC_LISCIA, zn)
            _belka(p, "Ogonek liscia", a, _lu((0.55, 2.3, 0.1), zn), 0.14, 0.14, "lodyga_ciemna", "matowy")
            sr, rot = _plyta(p, "Lisc", _lu((0.45, 2.25, 0.09), zn), b, 0.62, 0.07, "lodyga", skret=zn * 50)
            _plyta(p, "Zylka liscia", _lu((0.5, 2.27, 0.1), zn), _lu((1.45, 2.71, 0.29), zn), 0.07, 0.1, "zylka",
                   skret=zn * 50)
            # czubek liścia (klin) i kropla rosy
            with p.uklad(pos=sr, obrot=rot):
                p.blok("Czubek liscia", (0, 0.68, 0), (0.36, 0.3, 0.07), "lodyga_jasna", "matowy",
                       rot=(0, zn * 50, 45), faza=0.0)
            p.kula("Rosa", _lu((1.1, 2.62, 0.38), zn), 0.12, "rosa", "polysk", segm=6)


def _tarcza(p):
    """Żółta tarcza w dwóch połowach (paszcza na linii środka), oczy na górnej połowie, zęby, gardło."""
    x, y, z = TARCZA
    with _model(p, "Glowa"):
        p.blok("Kielich", (0, y, z - 0.32), (1.2, 1.2, 0.3), "lodyga", "matowy", faza=0.08)
        p.blok("Szyja kwiatu", (0, 3.22, 0.18), (0.5, 0.5, 0.36), "lodyga", "matowy", faza=0.05)
        p.blok("Tarcza gora", (0, y + 0.37, z), (2 * R_TARCZY, 0.74, 0.36), "tarcza", faza=0.1)
        p.blok("Brzeg gora", (0, y + 0.7, z + 0.03), (2 * R_TARCZY - 0.2, 0.1, 0.36), "tarcza_ciemna", "matowy",
               faza=0.02)
        p.blok("Gardlo", (0, y, z - 0.08), (1.15, 0.5, 0.12), "paszcza", "matowy", faza=0.0)
        p.blok("Podniebienie", (0, y + 0.02, z), (1.2, 0.04, 0.3), "paszcza", "matowy", faza=0.0)
        p.blok("Warga", (0, y + 0.01, z + 0.185), (1.3, 0.05, 0.02), "paszcza", "matowy", faza=0.0)
        for i, xx in enumerate((-0.48, -0.24, 0.0, 0.24, 0.48)):
            p.klin("Zab gora %d" % i, (xx, y - 0.06, z + 0.13), (0.14, 0.14, 0.1), "zab", rot=(180, 0, 0), faza=0.0)
        for zn in (1, -1):
            p.blok("Oko", (zn * 0.3, y + 0.42, z + 0.19), (0.26, 0.3, 0.04), "bialy", "polysk", faza=0.0)
            p.blok("Zrenica", (zn * 0.27, y + 0.4, z + 0.215), (0.13, 0.17, 0.03), "tusz", "polysk", faza=0.0)
            p.blok("Brew", (zn * 0.32, y + 0.62, z + 0.2), (0.3, 0.06, 0.03), "tusz", rot=(0, 0, -zn * 18), faza=0.0)
            # kropki pyłku na tarczy
            for j, (dx, dy) in enumerate(((0.55, 0.2), (0.45, 0.55), (0.15, 0.62))):
                p.blok("Kropka %d" % j, (zn * dx, y + dy, z + 0.185), (0.08, 0.08, 0.02), "tarcza_ciemna", "matowy",
                       faza=0.0)
    with _model(p, "Szczeka"):
        p.blok("Tarcza dol", (0, y - 0.37, z), (2 * R_TARCZY, 0.74, 0.36), "tarcza", faza=0.1)
        p.blok("Brzeg dol", (0, y - 0.7, z + 0.03), (2 * R_TARCZY - 0.2, 0.1, 0.36), "tarcza_ciemna", "matowy",
               faza=0.02)
        p.blok("Jezyk", (0, y - 0.06, z - 0.02), (0.6, 0.08, 0.3), "jezyk", "polysk", faza=0.02)
        p.blok("Dno paszczy", (0, y - 0.03, z), (1.2, 0.04, 0.3), "paszcza", "matowy", faza=0.0)
        for i, xx in enumerate((-0.36, -0.12, 0.12, 0.36)):
            p.klin("Zab dol %d" % i, (xx, y + 0.05, z + 0.13), (0.13, 0.12, 0.1), "zab", faza=0.0)


def _platek(p, nazwa, kat, dl=0.9, szer=0.62):
    """Płatek w płaszczyźnie tarczy (lekko odchylony do tyłu), nasada ciemniejsza, czubek żółty."""
    a = math.radians(kat)
    u = (math.cos(a), math.sin(a), 0.0)
    baza = _na_tarczy(kat, R_TARCZY - 0.12, -0.12)
    with p.uklad(pos=baza, obrot=(0, 0, kat - 90)):
        with p.uklad(obrot=(-14, 0, 0)):
            p.blok(nazwa, (0, dl / 2, 0), (szer, dl, 0.14), "platek", faza=0.05)
            p.blok(nazwa + " nasada", (0, 0.14, 0.02), (szer * 0.8, 0.28, 0.16), "platek_nasada", "matowy", faza=0.02)
            p.ostroslup(nazwa + " czubek", (0, dl + 0.15, 0), (szer * 0.86, 0.3, 0.14), "platek_czubek", "matowy",
                        gora=(0.0, 0.14), faza=0.0)
            p.blok(nazwa + " zylka", (0, dl * 0.55, 0.075), (0.08, dl * 0.6, 0.02), "platek_nasada", "matowy",
                   faza=0.0)
    return u


def _platki(p):
    grupy = {"PlatkiG": (45, 90, 135), "PlatkiL": (0, 330), "PlatkiP": (180, 210), "PlatkiD": (240, 270, 300)}
    for kosc, katy in grupy.items():
        with _model(p, kosc):
            for kat in katy:
                _platek(p, "Platek %d" % kat, kat)
    # tylne działki kielicha (zielone, widać je zza płatków)
    with _model(p, "Glowa"):
        for i, kat in enumerate((22, 112, 202, 292)):
            a = math.radians(kat)
            c = _na_tarczy(kat, 0.95, -0.35)
            p.blok("Dzialka %d" % i, c, (0.42, 0.42, 0.08), "lodyga_ciemna", "matowy", rot=(0, 0, kat + 45), faza=0.0)


# ---------------------------------------------------------------------------------------------------- klipy
def _z(*czesci, **kosci):
    out = {}
    for c in czesci:
        out.update(c)
    out.update(kosci)
    return out


def _platki_poz(zamknij=0.0, g=None, d=None, l=None, pp=None):
    """Płatki: zamknij > 0 składa je do przodu w pąk (stopnie), < 0 odchyla do tyłu (rozkwit). Osobno g/d/l/pp."""
    g = zamknij if g is None else g
    d = zamknij if d is None else d
    l = zamknij if l is None else l
    pp = zamknij if pp is None else pp
    return {"PlatkiG": (g, 0, 0), "PlatkiD": (-d, 0, 0), "PlatkiL": (0, -l, 0), "PlatkiP": (0, pp, 0)}


def _liscie_poz(rzL=0.0, rzP=None, rx=0.0):
    """Liście-ręce: rz > 0 unosi liść w górę (lewy i prawy w lustrze), rx > 0 do przodu."""
    rzP = rzL if rzP is None else rzP
    return {"LiscL": (-rx, 0, rzL), "LiscP": (-rx, 0, -rzP)}


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


def idle(p, dl=72):
    """Spoczynek (2,4 s): łodyga kołysze się na boki, kwiat kiwa, płatki oddychają na zmianę, liście falują."""
    k = p.klip("idle", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        pz = {"Lodyga1": (1.5 * c, 0, 3 * a), "Lodyga2": (-1.0 * c, 0, -3 * a), "Glowa": (2 * c, 4 * a, -1.5 * a),
              "Szczeka": (3 * max(0.0, math.sin(4 * math.pi * t)) ** 2, 0, 0)}
        pz.update(_platki_poz(g=4 * math.sin(2 * math.pi * t), d=4 * math.sin(2 * math.pi * t + 1.6),
                              l=4 * math.sin(2 * math.pi * t + 3.1), pp=4 * math.sin(2 * math.pi * t + 4.7)))
        pz.update(_liscie_poz(6 * math.sin(2 * math.pi * t + 0.5), 6 * math.sin(2 * math.pi * t + 2.0)))
        return pz
    _petla(k, poza)
    return k


def ruch(p, dl=30):
    """Drepcze w miejscu (1,0 s): nóżki na przemian w przód i w tył, cebulka kołysze się na boki, łodyga i kwiat
    w przeciwfazie, liście machają jak ręce."""
    k = p.klip("ruch", dl, petla=True)

    def poza(t):
        a = math.sin(2 * math.pi * t)
        c = math.cos(2 * math.pi * t)
        pz = {"NogaL": (-22 * a, 0, 0), "NogaP": (22 * a, 0, 0), "Cialo": {"o": (0, 6 * a, 5 * c), "p": (0, 0, 0)},
              "Lodyga1": (4, -4 * a, -6 * c), "Lodyga2": (2, 0, 3 * c), "Glowa": (-3 + 3 * math.sin(4 * math.pi * t), 3 * a, 0),
              "_h": 0.08 * max(0.0, math.sin(4 * math.pi * t))}
        pz.update(_platki_poz(-3 * math.sin(4 * math.pi * t)))
        pz.update(_liscie_poz(4, 4, rx=0.0))
        pz["LiscL"] = (-18 * a, 0, 4)
        pz["LiscP"] = (18 * a, 0, -4)
        return pz
    _petla(k, poza)
    return k


def atak(p, dl=27):
    """Kłapnięcie (0,9 s): łodyga odchyla się w tył, paszcza rozwarta, płatki odgięte (kl. 0–8), wypad całym kwiatem
    w przód i zatrzaśnięcie paszczy (kl. 13 = trafienie), powrót."""
    k = p.klip("atak", dl, petla=False)
    spocz = {}
    zamach = _z(_platki_poz(-18), _liscie_poz(18, 18, rx=-10),
                Cialo={"o": (-4, 0, 0), "p": (0, 0, -0.1)}, Lodyga1=(-14, 0, 0), Lodyga2=(-12, 0, 0), Glowa=(-14, 0, 0),
                Szczeka=(38, 0, 0))
    wypad = _z(_platki_poz(-24), _liscie_poz(-6, -6, rx=25),
               Cialo={"o": (5, 0, 0), "p": (0, 0, 0.25)}, Lodyga1=(12, 0, 0), Lodyga2=(14, 0, 0), Glowa=(-28, 0, 0),
               Szczeka=(42, 0, 0))
    klap = _z(_platki_poz(8), _liscie_poz(-8, -8, rx=30),
              Cialo={"o": (6, 0, 0), "p": (0, 0, 0.32)}, Lodyga1=(16, 0, 0), Lodyga2=(18, 0, 0), Glowa=(-36, 0, 0),
              Szczeka=(0, 0, 0))
    powrot = _z(_platki_poz(-4), Cialo={"o": (2, 0, 0), "p": (0, 0, 0.1)}, Lodyga1=(4, 0, 0), Lodyga2=(4, 0, 0),
                Glowa=(-8, 0, 0), Szczeka=(6, 0, 0))
    _sekwencja(k, (0, 8, 11, 13, 19, 27), (spocz, zamach, wypad, klap, powrot, spocz),
               wyg={1: "we", 2: "we", 3: "wy"})
    return k


def umiejetnosc(p, dl=54):
    """Usypiający pyłek (1,8 s): płatki zamykają się w pąk, a łodyga odchyla w tył — kwiat nabiera powietrza (kl. 0–16),
    drży (kl. 16–24), płatki rozkwitają szeroko, paszcza rozwarta, wyrzut w przód — pyłek leci z paszczy (kl. 30),
    chwila z otwartą paszczą i powrót."""
    k = p.klip("umiejetnosc", dl, petla=False)
    spocz = {}
    pak = _z(_platki_poz(62), _liscie_poz(25, 25, rx=-15),
             Cialo={"o": (-3, 0, 0), "p": (0, 0, -0.1)}, Lodyga1=(-10, 0, 0), Lodyga2=(-14, 0, 0), Glowa=(-18, 0, 0))
    drzy = _z(pak, Lodyga1=(-11, 0, 3), Glowa=(-20, 4, 0), **_platki_poz(66))
    drzy2 = _z(pak, Lodyga1=(-11, 0, -3), Glowa=(-20, -4, 0), **_platki_poz(64))
    rozkwit = _z(_platki_poz(-34), _liscie_poz(-10, -10, rx=30),
                 Cialo={"o": (5, 0, 0), "p": (0, 0, 0.2)}, Lodyga1=(12, 0, 0), Lodyga2=(14, 0, 0), Glowa=(-32, 0, 0),
                 Szczeka=(48, 0, 0))
    trzyma = _z(rozkwit, Glowa=(-28, 0, 0), Szczeka=(40, 0, 0), **_platki_poz(-28))
    _sekwencja(k, (0, 14, 18, 21, 24, 30, 40, 54), (spocz, pak, drzy, drzy2, drzy, rozkwit, trzyma, spocz),
               wyg={0: "s", 4: "we", 5: "wy"})
    return k


def trafienie(p, dl=18):
    """Szarpnięcie w tył (0,6 s, najdalej kl. 4): kwiat odchylony, paszcza uchylona, płatki trzepoczą."""
    k = p.klip("trafienie", dl, petla=False)
    spocz = {}
    szarp = _z(_platki_poz(-20, g=-26), _liscie_poz(20, 20, rx=-10),
               Cialo={"o": (-6, 0, 0), "p": (0, 0, -0.3)}, Lodyga1=(-10, 0, 0), Lodyga2=(-12, 0, 0), Glowa=(-14, 0, 0),
               Szczeka=(16, 0, 0))
    odbicie = _z(_platki_poz(8), Cialo={"o": (3, 0, 0), "p": (0, 0, -0.1)}, Lodyga1=(4, 0, 0), Glowa=(4, 0, 0))
    _sekwencja(k, (0, 4, 10, 18), (spocz, szarp, odbicie, spocz), wyg={0: "wy"})
    return k


def unik(p, dl=27):
    """Podskok w lewo o 1,5 studa (najdalej kl. 12) i powrót (0,9 s): kwiat przechyla się na bok, liście jak skrzydła."""
    k = p.klip("unik", dl, petla=False)
    spocz = {}
    przys = _z(Cialo={"o": (0, 0, -6), "p": (0, 0, 0)}, Lodyga1=(0, 0, 6), NogaL=(0, 0, 8), NogaP=(0, 0, 8))
    lot = _z(_liscie_poz(30, 30), _platki_poz(-10),
             Cialo={"o": (0, 0, 12), "p": (0.8, 0, 0)}, Lodyga1=(0, 0, -8), Lodyga2=(0, 0, -6), NogaL=(0, 0, -14),
             NogaP=(0, 0, -14), _h=0.5)
    lad = _z(Cialo={"o": (0, -10, 4), "p": (1.5, 0, 0)}, Lodyga1=(0, 0, 6), Glowa=(0, -10, 0))
    lot2 = _z(lot, Cialo={"o": (0, 0, -8), "p": (0.75, 0, 0)}, _h=0.35, **_z(_liscie_poz(26, 26)))
    _sekwencja(k, (0, 3, 8, 12, 17, 22, 27), (spocz, przys, lot, lad, lot2, przys, spocz),
               wyg={1: "wy", 2: "we", 4: "we"})
    return k


def upadek(p, dl=60):
    """Upadek (2 s): kwiat chwieje się, łodyga gnie się w tył i na bok, kwiat pada na ziemię, płatki zwisają, liście
    opadają (kl. 60 = leży)."""
    k = p.klip("upadek", dl, petla=False)
    spocz = {}
    chwiej = _z(_platki_poz(-10), Cialo={"o": (-4, 0, 6), "p": (0, 0, -0.2)}, Lodyga1=(-10, 0, 8), Lodyga2=(-8, 0, 6),
                Glowa=(-10, 10, 0), Szczeka=(14, 0, 0))
    chwiej2 = _z(_platki_poz(6), Cialo={"o": (4, 0, -6), "p": (0, 0, -0.1)}, Lodyga1=(8, 0, -10), Lodyga2=(10, 0, -8),
                 Glowa=(14, -10, 0), Szczeka=(6, 0, 0))
    wiednie = _z(_platki_poz(-20), _liscie_poz(-30, -30),
                 Cialo={"o": (-6, 0, 10), "p": (0, 0, -0.2)}, Lodyga1=(-28, 0, 24), Lodyga2=(-30, 0, 20),
                 Glowa=(-20, 0, 10), Szczeka=(20, 0, 0), _wolne=True)
    lezy = _z(_platki_poz(-40, g=-55), _liscie_poz(-50, -45),
              Cialo={"o": (-10, 0, 14), "p": (0, 0, -0.3)}, Lodyga1=(-40, 0, 32), Lodyga2=(-38, 0, 26),
              Glowa=(-22, 0, 12), Szczeka=(26, 0, 0), _wolne=True)
    _sekwencja(k, (0, 8, 18, 34, 46, 60), (spocz, chwiej, chwiej2, wiednie, lezy, lezy),
               wyg={2: "we", 3: "wy", 4: "l"})
    return k


def wiwat(p, dl=60):
    """Radość (pętla 2 s): dwa podskoki z liśćmi w górze, płatki trzepoczą, paszcza w uśmiechu, kwiat kręci się
    w prawo i w lewo."""
    k = p.klip("wiwat", dl, petla=True)
    spocz = {}
    przys = _z(_platki_poz(6), Cialo=(4, 0, 0), Lodyga1=(6, 0, 0), Glowa=(4, 0, 0), NogaL=(-10, 0, 0),
               NogaP=(-10, 0, 0))
    hop = _z(_platki_poz(-24), _liscie_poz(55, 55, rx=-10),
             Cialo=(-4, 0, 0), Lodyga1=(-6, 0, 0), Lodyga2=(-6, 0, 0), Glowa=(-12, 18, 0), Szczeka=(22, 0, 0), _h=0.55)
    lad = _z(przys, **_liscie_poz(20, 20))
    hop2 = _z(hop, Glowa=(-12, -18, 0))
    _sekwencja(k, (0, 5, 14, 22, 30, 35, 44, 52, 60),
               (spocz, przys, hop, lad, spocz, przys, hop2, lad, spocz),
               wyg={1: "wy", 2: "we", 5: "wy", 6: "we"})
    return k


# =============================================================== animacja: pozy kluczowe -> klucz w każdej klatce
# (ten sam zestaw pomocników co w modułach potworów Bagna — rechotek, bulgotnik, klodoklap, ropucha_z_chatka,
#  straznik_topieli — i Dżungli: zwijogon, gebokwiat, kokosowy_silacz, pancernik_ruin, waz_stu_lian). Poza = {kość: (rx, ry, rz) | {"o": obrót, "p": przesunięcie, "k": kierunek osi OS[kość] w
#  świecie}}; "_h" = wysokość najniższego punktu ciała nad ziemią (domyślnie 0), "_wolne" = kości PLASKIE nie są
#  trzymane poziomo (lot, przewrót); w Dżungli "_wolne" może też być krotką nazw kości — wtedy tylko one idą za
#  rodzicem (np. łapa uniesiona do ciosu), a reszta zostaje płasko. Brak kości w pozie = spoczynek tej kości.
I3 = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
ZERO = (0.0, 0.0, 0.0)


def _T(R):
    return tuple(tuple(R[j][i] for j in range(3)) for i in range(3))


def _norm(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return tuple(x / n for x in v)


def _obrot_miedzy(a, b):
    """Macierz najkrótszego obrotu, który przenosi kierunek a na kierunek b."""
    a, b = _norm(a), _norm(b)
    o = (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    s, c = math.sqrt(sum(x * x for x in o)), sum(a[i] * b[i] for i in range(3))
    if s < 1e-9:
        return I3
    x, y, z = (v / s for v in o)
    t = 1.0 - c
    return ((t * x * x + c, t * x * y - s * z, t * x * z + s * y),
            (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
            (t * x * z - s * y, t * y * z + s * x, t * z * z + c))


def _belka(p, nazwa, a, b, szer, gleb, kolor, mat="zwykly", nad=0.0, faza=None, ksztalt="blok"):
    """Klocek (albo elipsoida: ksztalt="kula", walec: "walec") od punktu a do punktu b (bieżący układ; oś Y bryły
    wzdłuż a→b, nad = wydłużenie z obu końców). Zwraca (środek, obrót) — układ do dokładania brył wzdłuż belki."""
    d = tuple(b[i] - a[i] for i in range(3))
    L = math.sqrt(sum(x * x for x in d))
    sr = tuple((a[i] + b[i]) / 2.0 for i in range(3))
    rot = katy_z_macierzy(_obrot_miedzy((0.0, 1.0, 0.0), d))
    if ksztalt == "kula":
        p.kula(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot)
    elif ksztalt == "walec":
        p.walec(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot, faza=faza)
    else:
        p.blok(nazwa, sr, (szer, L + 2 * nad, gleb), kolor, mat, rot=rot, faza=faza)
    return sr, rot


def _krok(p, W, n, o, pr):
    k = p.kosci[n]
    Rl = macierz_obrotu(*o)
    if k["rodzic"] is None:
        W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
    else:
        Rp, tp = W[k["rodzic"]]
        st = p.kosci[k["rodzic"]]["staw"]
        d = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
        W[n] = (mnoz(Rp, Rl), tuple(tp[i] + d[i] for i in range(3)))


def _fk(p, lok):
    W = {}
    for n in p.kosci:
        o, pr = lok.get(n, (ZERO, ZERO))
        _krok(p, W, n, o, pr)
    return W


def _naroza(p):
    """Narożniki brył względem stawu ich kości (do dociągania do ziemi), liczone raz."""
    if getattr(p, "_bagno_naroza", None) is None:
        out = {}
        for c in p.czesci:
            R = macierz_obrotu(*c["r"])
            h = [v / 2.0 for v in c["s"]]
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        q = razy_wektor(R, (sx * h[0], sy * h[1], sz * h[2]))
                        out.setdefault(c["kosc"], []).append(tuple(c["p"][i] + q[i] for i in range(3)))
        p._bagno_naroza = out
    return p._bagno_naroza


def _najnizej(p, W, pomin=()):
    mn = 1e9
    for kosc, pkt in _naroza(p).items():
        if kosc in pomin:
            continue
        R, t = W[kosc]
        for q in pkt:
            y = R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1]
            if y < mn:
                mn = y
    return mn


def _rozwiaz(p, poza):
    """Poza kluczowa -> {kość: (obrót lokalny, przesunięcie)}; kierunki "k" zamienione na obroty lokalne."""
    lok, W = {}, {}
    for n, k in p.kosci.items():
        v = poza.get(n)
        o, pr, kier = ZERO, ZERO, None
        if isinstance(v, dict):
            o, pr, kier = tuple(v.get("o", ZERO)), tuple(v.get("p", ZERO)), v.get("k")
        elif v is not None:
            o = tuple(v)
        if kier is not None:
            Rp = W[k["rodzic"]][0] if k["rodzic"] else I3
            o = katy_z_macierzy(mnoz(_T(Rp), _obrot_miedzy(OS[n], kier)))
        lok[n] = (tuple(o), tuple(pr))
        _krok(p, W, n, lok[n][0], lok[n][1])
    return lok


def _plasko(p, lok, wolne=()):
    """Kości PLASKIE (bez `wolne`): poziomo w świecie, z odchyleniem (yaw) rodzica."""
    W = {}
    for n, k in p.kosci.items():
        o, pr = lok.get(n, (ZERO, ZERO))
        if n in PLASKIE and n not in wolne:
            Rp = W[k["rodzic"]][0]
            f = razy_wektor(Rp, (0.0, 0.0, 1.0))
            yaw = math.degrees(math.atan2(f[0], f[2])) if abs(f[0]) + abs(f[2]) > 1e-6 else 0.0
            o = katy_z_macierzy(mnoz(_T(Rp), macierz_obrotu(0.0, yaw, 0.0)))
            lok[n] = (o, pr)
        _krok(p, W, n, o, pr)
    return W


def _wolne(*pozy):
    """(płasko?, wolne kości) z pól "_wolne" póz: True = żadna kość PLASKIE nie jest trzymana poziomo."""
    wolne = set()
    for pz in pozy:
        w = pz.get("_wolne")
        if w is True:
            return False, ()
        if w:
            wolne.update(w)
    return True, tuple(wolne)


def _uziem(p, lok, h, plasko=True, wolne=()):
    W = _plasko(p, lok, wolne) if plasko else _fk(p, lok)
    dno = _najnizej(p, W, POMIN_ZIEMIA)
    o, pr = lok[GLOWNA]
    lok[GLOWNA] = (o, (pr[0], pr[1] + h - dno, pr[2]))


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku przez ±180°)."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    najl = None
    for c in (tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)):
        c = tuple(blisko(c[i], poprz[i]) for i in range(3))
        d = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or d < najl[0] - 1e-6:
            najl = (d, c)
    return najl[1]


def _cr(a, b, c, d, t):
    return 0.5 * (2 * b + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3)


def _kw(R):
    """Macierz obrotu -> kwaternion (w, x, y, z)."""
    tr = R[0][0] + R[1][1] + R[2][2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = (0.25 * s, (R[2][1] - R[1][2]) / s, (R[0][2] - R[2][0]) / s, (R[1][0] - R[0][1]) / s)
    elif R[0][0] > R[1][1] and R[0][0] > R[2][2]:
        s = math.sqrt(1.0 + R[0][0] - R[1][1] - R[2][2]) * 2
        q = ((R[2][1] - R[1][2]) / s, 0.25 * s, (R[0][1] + R[1][0]) / s, (R[0][2] + R[2][0]) / s)
    elif R[1][1] > R[2][2]:
        s = math.sqrt(1.0 + R[1][1] - R[0][0] - R[2][2]) * 2
        q = ((R[0][2] - R[2][0]) / s, (R[0][1] + R[1][0]) / s, 0.25 * s, (R[1][2] + R[2][1]) / s)
    else:
        s = math.sqrt(1.0 + R[2][2] - R[0][0] - R[1][1]) * 2
        q = ((R[1][0] - R[0][1]) / s, (R[0][2] + R[2][0]) / s, (R[1][2] + R[2][1]) / s, 0.25 * s)
    return _norm(q)


def _z_kw(q):
    w, x, y, z = _norm(q)
    return ((1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)),
            (2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)),
            (2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)))


def _bliski(q, wzor):
    return q if sum(q[i] * wzor[i] for i in range(4)) >= 0 else tuple(-v for v in q)


def _slerp(a, b, t):
    b = _bliski(b, a)
    c = max(-1.0, min(1.0, sum(a[i] * b[i] for i in range(4))))
    kat = math.acos(c)
    if kat < 1e-5:
        return _norm(tuple(a[i] + (b[i] - a[i]) * t for i in range(4)))
    sa, sb = math.sin((1 - t) * kat) / math.sin(kat), math.sin(t * kat) / math.sin(kat)
    return tuple(sa * a[i] + sb * b[i] for i in range(4))


def _wygladz(t, tryb):
    if tryb == "l":
        return t
    if tryb == "we":
        return t * t
    if tryb == "wy":
        return 1.0 - (1.0 - t) * (1.0 - t)
    return t * t * (3.0 - 2.0 * t)


def _zapisz(k, f, lok):
    for n, (o, pr) in lok.items():
        if n == "Root":
            continue
        k.klucz(f, n, obrot=tuple(round(x, 3) for x in o), przes=tuple(round(x, 4) for x in pr), wyg="liniowo")


def _ciagle_katy(lok, poprz):
    """Kąty każdej kości zapisane najbliżej poprzedniej klatki (Euler bez skoków)."""
    for n, (o, pr) in lok.items():
        o = _ciaglosc(o, poprz.get(n))
        poprz[n] = o
        lok[n] = (o, pr)


def _sekwencja(k, czasy, pozy, wyg=None, domyslnie="s", ziemia=True, po=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (obroty kości przez kwaterniony, więc duże obroty łap nie
    kręcą się po kątach). wyg = {numer odcinka: "s" | "l" | "we" | "wy" | "cr"}: s = łagodnie, l = jednostajnie,
    we = przyspiesza (w uderzenie), wy = hamuje (po wybiciu), cr = płynnie przez pozy. ziemia = najniższy punkt
    brył (bez POMIN_ZIEMIA) na wysokości "_h" pozy. po(f, lok) — dopiski w klatce. Klip zapętlony: ostatnia klatka
    = pierwsza."""
    p = k.postac
    n_poz = len(pozy)
    kosci = [n for n in p.kosci if n != "Root"]
    tab = []
    for pz in pozy:
        lok = _rozwiaz(p, pz)
        tab.append({n: (_kw(macierz_obrotu(*lok[n][0])), lok[n][1]) for n in kosci})
    for i in range(1, n_poz):
        for n in kosci:
            tab[i][n] = (_bliski(tab[i][n][0], tab[i - 1][n][0]), tab[i][n][1])

    def sasiad(i):
        if k.petla:
            if i < 0:
                return i + n_poz - 1
            if i > n_poz - 1:
                return i - n_poz + 1
            return i
        return max(0, min(n_poz - 1, i))

    poprz, pierwsza = {}, None
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        if k.petla and f == k.dlugosc and pierwsza is not None:
            _zapisz(k, f, pierwsza)
            continue
        i = max(j for j in range(n_poz - 1) if czasy[j] <= f) if f < czasy[-1] else n_poz - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        tryb = (wyg or {}).get(i, domyslnie)
        e = _wygladz(t, tryb)
        lok = {}
        for n in kosci:
            if tryb == "cr":
                ia, id_ = sasiad(i - 1), sasiad(i + 2)
                qb = tab[i][n][0]
                qa, qc, qd = (_bliski(tab[ia][n][0], qb), _bliski(tab[i + 1][n][0], qb),
                              _bliski(tab[id_][n][0], qb))
                q = _norm(tuple(_cr(qa[j], qb[j], qc[j], qd[j], t) for j in range(4)))
                pa, pb, pc, pd = (tab[ia][n][1], tab[i][n][1], tab[i + 1][n][1], tab[id_][n][1])
                pr = tuple(_cr(pa[j], pb[j], pc[j], pd[j], t) for j in range(3))
            else:
                q = _slerp(tab[i][n][0], tab[i + 1][n][0], e)
                a, b = tab[i][n][1], tab[i + 1][n][1]
                pr = tuple(a[j] + (b[j] - a[j]) * e for j in range(3))
            lok[n] = (katy_z_macierzy(_z_kw(q)), pr)
        h0, h1 = pozy[i].get("_h", 0.0), pozy[i + 1].get("_h", 0.0)
        plasko, wolne = _wolne(pozy[i], pozy[i + 1])
        if ziemia:
            _uziem(p, lok, h0 + (h1 - h0) * e, plasko, wolne)
        elif plasko:
            _plasko(p, lok, wolne)
        if po:
            po(f, lok)
        _ciagle_katy(lok, poprz)
        if pierwsza is None:
            pierwsza = dict(lok)
        _zapisz(k, f, lok)
    return k


def _petla(k, poza, ziemia=True):
    """Klip zapętlony z funkcji poza(t), t = 0…1 (okresowa); ostatnia klatka = pierwsza (bez szwu)."""
    p = k.postac
    pierwsza, poprz = None, {}
    for f in range(k.dlugosc):
        pz = poza(f / float(k.dlugosc))
        lok = _rozwiaz(p, pz)
        if ziemia:
            plasko, wolne = _wolne(pz)
            _uziem(p, lok, pz.get("_h", 0.0), plasko, wolne)
        _ciagle_katy(lok, poprz)
        _zapisz(k, f, lok)
        if pierwsza is None:
            pierwsza = dict(lok)
    _zapisz(k, k.dlugosc, pierwsza)
    return k
