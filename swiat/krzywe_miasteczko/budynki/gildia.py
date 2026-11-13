# -*- coding: utf-8 -*-
"""Siedziba gildii — „wkrótce” (PROJEKT.md, karta 5.8) — zamknięta, ale kusząca, łamana wieża z koroną i zielonym hełmem.

Sylwetka: prosty parter 16 × 16, nad nim trzy kondygnacje skręcane na przemian (piętro 2 ry +6°, piętro 3 ry −6° i rz −6°,
korona z blankami w kontrze rz +5°, ry +5°), na koronie ostrosłup 20 × 20 w kolorze gildii ze złotymi krawędziami i gałką.
Szyld: wielki sztandar gildii z trzech falujących segmentów z herbem „trzy kształty” (koło, kwadrat, trójkąt) zwisa
z drążka przy prawym narożniku korony — w połowie poza bryłą. „Wkrótce” bez liter: drzwi zabite trzema deskami,
złota kłódka i klepsydra. Żart: ktoś odnawia siedzibę — rusztowanie po lewej, wiszące wiadro, niebieskie zacieki świeżej
farby na starym, ciemniejszym tynku i kałuża farby. Echo: złoty róg heroldów na balkonie piętra 2. Kuszenie: w najwyższym
oknie pali się światło.

Układ lokalny: środek działki 28 × 28 na ziemi = (0, 0, 0), front z wejściem ku +Z (lico frontu parteru z = +6).
Odstępstwa od karty (świadome): piętro 3 rz −6° zamiast −4° i korona rz +5° zamiast +3° (przykazanie 1 — kąty 1–3°
wyglądają jak błąd, a −4°/+3° ginęły w renderze); hełm 20 × 20 × 7,6 zamiast 9 (limit wysokości 40 z gałką); sztandar
wisi przy prawym przednim narożniku korony (ry 35°), a nie na fasadzie, żeby nie zasłaniał zabitych drzwi i okien.
Status: propozycja (noc 13.11.2026), nie kanon.

Podgląd:  python -B swiat/biblioteka/podglad.py --modul swiat/krzywe_miasteczko/budynki/gildia.py --wyj <folder> --szer 1000
"""
import contextlib
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402

NAZWA = "Gildia"
OBRYS = (28, 28)                 # szer (lokalne X) × gł (lokalne Z)
WYSOKOSC = 40                    # wierzch gałki hełmu
BUDZET = 280
INTERAKCJA = (2.0, 18.0)         # przed zabitymi drzwiami, 4 study przed krawędzią działki
OBRYS_SYLWETKI = False           # PROJEKT 5.0 p. 4: Highlight w budynkach zakazany — obrys robimy z klocków (tusz)

SCIANA, DACH = "tynk_blekit", "dach_gildia"
CIEMNA = "woda_gleboka"          # ciemna szyba bez Neonu (gildia zamknięta — świeci tylko najwyższe okno)


# --------------------------------------------------------------------------- narzędzie: punkt z bieżącego układu w układzie bazy
def _do_bazy(s, baza, p):
    """Współrzędne punktu `p` z bieżącego układu lokalnego przeliczone do układu `baza` (= s._stos[-1] z początku buduj)."""
    R0, t0, k0 = baza
    R, t, k = s._stos[-1]
    w = [t[i] + k * (R[i][0] * p[0] + R[i][1] * p[1] + R[i][2] * p[2]) for i in range(3)]
    d = [w[i] - t0[i] for i in range(3)]
    return tuple((R0[0][i] * d[0] + R0[1][i] * d[1] + R0[2][i] * d[2]) / k0 for i in range(3))


def buduj(s, rnd):
    baza = s._stos[-1]
    kotwice = {}
    with s.uklad(pos=(0, 0, -2.0)):                               # parter 16 × 16, środek (0; −2), front z = +6
        _parter(s)
        # piętro 2: 17,5 × 17,5 × 8, ry +6°, wysunięte 0,8 ku frontowi (nawis 0,6–2,4, nierówno)
        with s.uklad(pos=(0.3, 12.0, 0.8), obrot=(0, 6, 0)):
            _pietro2(s)
            # piętro 3: 16 × 16 × 7, ry −6° bezwzględnie (−12° względem piętra 2), rz −6° (góra w prawo)
            with s.uklad(pos=(-0.4, 8.0 - 0.95, -0.3), obrot=(0, -12, -6)):
                _pietro3(s)
                # korona 18 × 18 × 4 w kontrze: rz +5° bezwzględnie (+11° względem piętra 3), ry +5° bezwzględnie
                with s.uklad(pos=(0.6, 7.0 - 1.7, 0.0), obrot=(0, 11, 11)):
                    _korona(s)
                    kotwice["korona_rog"] = _do_bazy(s, baza, (8.4, 0.4, 8.4))
        _rusztowanie(s)
    _sztandar(s, kotwice)
    _rekwizyty(s, rnd)
    zestaw.punkt_interakcji(s, NAZWA, INTERAKCJA)
    if OBRYS_SYLWETKI:
        s.obrys_sylwetki()


# --------------------------------------------------------------------------- parter (prosty, z kolizją)
def _parter(s):
    W, H = 16.0, 12.0
    h = W / 2.0
    s.blok("Cokół", (0, 0.6, 0), (W + 0.8, 1.2, W + 0.8), "kamien_cokol", "Cobblestone")
    with s.cechy(kolizja=False):
        s.blok("Cokół rant", (0, 1.25, 0), (W + 1.0, 0.4, W + 1.0), "tusz")
    s.blok("Parter", (0, (H + 0.1) / 2.0, 0), (W, H - 0.1, W), SCIANA)
    with s.cechy(kolizja=False):
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik", (sx * (h - 0.25), 6.825, sz * (h - 0.25)), (1.3, 10.55, 1.3), "tusz")
        s.blok("Pas cienia", (3.2, 11.25, h + 0.05), (8.6, 1.3, 0.2), cien(s, SCIANA))
    # drzwi 8 × 10 w x = +2, zabite deskami — „wkrótce” bez liter
    zestaw.drzwi(s, (2.0, 0, h + 0.25), 8.0, 10.0, "drewno_ciemne", nadproze="drewno", przechyl_nadproza=-5)
    _zabite_drzwi(s, 2.0, h + 0.25 + 1.4)
    # żart: stary, ciemniejszy tynk z zaciekami świeżej farby (front po lewej i lewy bok za rusztowaniem)
    _farba(s, h)
    # prawy bok: okno z okiennicą, łata, wypadnięty klocek; tył: tanie okno i łata
    zestaw.okno(s, (h, 6.6, -3.2), 3.0, 4.0, przechyl=6, swiatlo=CIEMNA, ry=90, okiennica=DACH, strona_okiennicy=-1)
    zestaw.lata(s, (h, 3.6, 3.4), 2.6, 2.2, "zloto", ry=90, przechyl=-8)
    zestaw.wypadniety_klocek(s, (h, 2.8, -6.2), (h + 1.9, 0, -4.4), SCIANA, ry=90, obrot_klocka=24)
    zestaw.okno(s, (-2.5, 6.4, -h), 3.0, 4.0, przechyl=-5, swiatlo=CIEMNA, ry=180, tanie=True)
    zestaw.lata(s, (3.8, 4.0, -h), 2.4, 2.0, "czerwien", ry=180, przechyl=9)
    zestaw.okno(s, (-h, 8.0, -5.2), 2.4, 3.0, przechyl=6, swiatlo=CIEMNA, ry=-90, tanie=True)


def _zabite_drzwi(s, x0, z0):
    """Trzy deski drewno_jasne na krzyż (±20°) i poziomo, złota kłódka 4 × 5 na skrzyżowaniu, klepsydra 4 na dolnej
    desce. z0 = lico ramy drzwi. 17 części."""
    with s.cechy(kolizja=False):
        s.blok("Deska", (x0, 6.7, z0 + 0.25), (10.8, 1.3, 0.4), "drewno_jasne", "WoodPlanks", rot=(0, 0, 20))
        s.blok("Deska", (x0, 6.7, z0 + 0.7), (10.8, 1.3, 0.4), "drewno_jasne", "WoodPlanks", rot=(0, 0, -20))
        s.blok("Deska", (x0, 2.9, z0 + 0.25), (10.6, 1.3, 0.4), "drewno_jasne", "WoodPlanks", rot=(0, 0, -4))
        with s.cechy(cien=False):
            for x, y, z in ((-4.4, 4.9, 0.5), (4.4, 8.5, 0.5), (4.6, 2.55, 0.5)):
                s.blok("Gwóźdź", (x0 + x, y, z0 + z), (0.5, 0.5, 0.3), "metal_ciemny", rot=(0, 0, 45))
        # kłódka: korpus zloto z podkładką, pałąk metal_ciemny, dziurka tusz
        zk = z0 + 1.5
        s.blok("Kłódka podkładka", (x0, 5.6, zk - 0.45), (4.0, 3.6, 0.3), "tusz")
        s.blok("Kłódka", (x0, 5.6, zk), (3.4, 3.0, 1.0), "zloto")
        for zn in (-1, 1):
            s.blok("Kłódka pałąk", (x0 + zn * 1.05, 7.75, zk), (0.6, 1.4, 0.6), "metal_ciemny")
        s.blok("Kłódka pałąk", (x0, 8.6, zk), (2.7, 0.6, 0.6), "metal_ciemny")
        with s.cechy(cien=False):
            s.blok("Kłódka dziurka", (x0, 5.4, zk + 0.55), (0.6, 1.2, 0.2), "tusz")
        # klepsydra 4: dwa ostrosłupy zloto (górny odwrócony), ramy tusz, strużka piasku bruk
        with s.uklad(pos=(x0 + 4.4, 0.9, z0 + 1.35), obrot=(0, 0, 7)):
            s.blok("Klepsydra rama", (0, 0.2, 0), (3.0, 0.4, 1.8), "tusz")
            s.blok("Klepsydra rama", (0, 3.8, 0), (3.0, 0.4, 1.8), "tusz")
            s.ostroslup("Klepsydra", (0, 0.4, 0), 1.2, 0.7, 1.6, "zloto")
            with s.uklad(pos=(0, 3.6, 0), obrot=(180, 0, 0)):
                s.ostroslup("Klepsydra", (0, 0, 0), 1.2, 0.7, 1.6, "zloto")
            with s.cechy(cien=False):
                s.blok("Klepsydra piasek", (0, 2.0, 0), (0.35, 1.2, 0.35), "bruk")
                s.blok("Klepsydra piasek", (0, 0.75, 0.6), (1.4, 0.5, 0.3), "bruk")


def _farba(s, h):
    """Stary tynk cien(tynk_blekit) z zaciekami świeżej farby tynk_blekit spływającymi z odnowionej górnej części ściany."""
    stary = cien(s, SCIANA, 0.75)
    with s.cechy(kolizja=False, cien=False):
        # front po lewej od drzwi
        s.blok("Stary tynk", (-5.15, 4.75, h + 0.1), (3.6, 6.3, 0.2), stary)
        for x, dl in ((-6.2, 2.6), (-5.0, 4.2), (-3.9, 1.6)):
            s.blok("Zaciek", (x, 7.9 - dl / 2.0, h + 0.3), (0.8, dl, 0.2), SCIANA)
            s.blok("Kropla", (x, 7.9 - dl - 0.2, h + 0.3), (1.2, 1.0, 0.2), SCIANA, rot=(0, 0, 45))
        # lewy bok (za rusztowaniem)
        s.blok("Stary tynk", (-h - 0.1, 4.75, 0.2), (0.2, 6.3, 13.0), stary)
        for z, dl in ((4.6, 3.4), (1.3, 1.8), (-2.6, 4.6)):
            s.blok("Zaciek", (-h - 0.3, 7.9 - dl / 2.0, z), (0.2, dl, 0.8), SCIANA)
            s.blok("Kropla", (-h - 0.3, 7.9 - dl - 0.2, z), (0.2, 1.0, 1.2), SCIANA, rot=(45, 0, 0))


# --------------------------------------------------------------------------- piętro 2 (ry +6°) z balkonem i rogiem
def _pietro2(s):
    W, Hp = 17.5, 8.0
    h = W / 2.0
    s.blok("Piętro 2", (0, Hp / 2.0, 0), (W, Hp, W), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Belka stropowa", (0, 0.5, 0), (W + 0.6, 1.1, W + 0.6), "tusz")   # −0,05…1,05: nie w płaszczyźnie piętra ani balkonu
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik piętra", (sx * (h - 0.15), 4.4, sz * (h - 0.15)), (1.2, 6.6, 1.2), "tusz")
        s.blok("Pas cienia", (0, 7.2, h + 0.05), (W - 2.4, 1.2, 0.2), cien(s, SCIANA))
    # balkon od frontu po lewej: drzwiczki, podłoga, balustrada tusz, wsporniki
    xb = -3.6
    zestaw.drzwi(s, (xb, 1.1, h), 3.0, 4.6, "drewno_ciemne", nadproze=None, prog=None, tanie=True, gleb=0.6)
    with s.cechy(kolizja=False):
        s.blok("Balkon", (xb, 0.75, h + 1.5), (6.0, 0.7, 3.0), "drewno_jasne", "WoodPlanks")
        for zn in (-1, 1):
            s.klin("Balkon wspornik", (xb + zn * 2.2, -0.6, h + 1.2), (0.8, 2.0, 2.4), "drewno_ciemne", rot=(0, 180, 180))
        s.blok("Balustrada", (xb, 3.35, h + 2.75), (6.4, 0.5, 0.5), "tusz")
        for zn in (-1, 1):
            s.blok("Balustrada bok", (xb + zn * 2.95, 3.35, h + 1.5), (0.5, 0.5, 2.6), "tusz")
        for x in (-2.95, -1.0, 1.0, 2.95):
            s.blok("Tralka", (xb + x, 2.2, h + 2.75), (0.5, 2.2, 0.5), "tusz")
        # róg heroldów oparty o balustradę, czarą w lewo i w górę
        with s.uklad(pos=(xb + 3.3, 3.7, h + 1.7), obrot=(0, 180, 6)):
            _rog(s)
    # front po prawej: okno z zwisającą okiennicą; boki i tył
    zestaw.okno(s, (3.6, 4.0, h), 3.0, 3.6, przechyl=-6, swiatlo=CIEMNA, okiennica="drewno", strona_okiennicy=1)
    zestaw.okno(s, (-h, 4.2, -1.5), 3.0, 3.6, przechyl=7, swiatlo=CIEMNA, ry=-90, tanie=True)
    zestaw.okno(s, (h, 4.0, 1.0), 2.6, ksztalt="okragle", przechyl=0, swiatlo=CIEMNA, ry=90, tanie=True)
    zestaw.lata(s, (h, 2.6, -5.0), 2.4, 2.0, "czerwien", ry=90, przechyl=10)
    with s.cechy(kolizja=False):                               # kroksztyny pod nawisem frontu
        for x in (2.6, 6.4):
            s.klin("Kroksztyn", (x, -0.8, h - 0.9), (0.8, 1.6, 1.6), "drewno_ciemne", rot=(0, 180, 180))
    zestaw.okno(s, (2.0, 4.2, -h), 3.0, 3.6, przechyl=5, swiatlo=CIEMNA, ry=180, tanie=True)
    zestaw.lata(s, (-4.0, 3.6, -h), 2.6, 2.2, "pomarancz", ry=180, przechyl=-7)


def _rog(s):
    """Róg z 5 walców Ø 1,5 → 5 (wąska rura i nagła czara), łamanych co ok. 15° (razem ok. 10), zloto, z ciemną czarą i ustnikiem. Oś rogu = lokalne +X.
    Czerwony pas-temblak zwisa pod rogiem (żeby nie czytał się jak luneta). 9 części."""
    with s.cechy(kolizja=False):
        s.belka("Róg pas", (0.9, -0.5, 0.0), (3.4, -2.5, -0.6), 0.4, "czerwien", "Fabric", szer=0.7)
        s.belka("Róg pas", (3.4, -2.5, -0.6), (5.4, 0.2, -1.5), 0.4, "czerwien", "Fabric", szer=0.7)
    with s.cechy(kolizja=False), contextlib.ExitStack() as st:
        s.walec("Róg ustnik", (-0.3, 0, 0), 0.5, 0.8, "tusz", os="x")
        for i, (d, dl) in enumerate(((1.5, 2.4), (1.75, 2.3), (2.2, 2.2), (3.0, 1.9), (5.0, 1.1))):
            if i:
                st.enter_context(s.uklad(obrot=(0, 11, 10)))    # łamany co ok. 15° (11° ku frontowi + 10° w górę)
            s.walec("Róg", (dl / 2.0, 0, 0), d / 2.0, dl + 0.1, "zloto", os="x")
            st.enter_context(s.uklad(pos=(dl, 0, 0)))
        s.walec("Róg czara", (0.08, 0, 0), 1.9, 0.3, "tusz", os="x")


# --------------------------------------------------------------------------- piętro 3 (ry −6°, rz −6°) — najwyższe okno świeci
def _pietro3(s):
    W, Hp = 16.0, 7.0
    h = W / 2.0
    s.blok("Piętro 3", (0, Hp / 2.0, 0), (W, Hp, W), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Belka piętra 3", (0, 0.85, 0), (W + 0.6, 1.0, W + 0.6), "tusz")
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.blok("Narożnik piętra 3", (sx * (h - 0.15), 3.9, sz * (h - 0.15)), (1.2, 5.2, 1.2), "tusz")
    zestaw.okno(s, (-2.2, 3.5, h), 2.8, 2.4, ksztalt="luk", przechyl=5, swiatlo="neon_okno")
    zestaw.okno(s, (3.4, 3.2, h), 2.0, ksztalt="okragle", przechyl=0, swiatlo=CIEMNA, tanie=True)
    zestaw.okno(s, (-h, 3.4, 1.5), 2.6, 3.0, przechyl=-6, swiatlo=CIEMNA, ry=-90, tanie=True)
    zestaw.okno(s, (h, 3.6, -1.0), 2.4, 2.8, przechyl=-7, swiatlo=CIEMNA, ry=90, tanie=True)
    zestaw.okno(s, (1.0, 3.4, -h), 2.6, 3.0, przechyl=7, swiatlo=CIEMNA, ry=180, tanie=True)


# --------------------------------------------------------------------------- korona z blankami i hełm-ostrosłup
def _korona(s):
    """Korona 18 × 18: rant tusz, pas tynku, gzyms tusz, 12 blanek (co druga wyższa i w cieniu) i 4 narożne filarki
    niosące hełm; między blankami ciemny rdzeń. Hełm 20 × 20 × 7,6 dach_gildia na złotej desce czołowej, złote krawędzie
    i gałka. 29 części."""
    W = 18.0
    y0 = 5.6                                                    # spód ostrosłupa hełmu
    with s.cechy(kolizja=False):
        s.blok("Korona rant", (0, 0.3, 0), (W + 0.6, 0.6, W + 0.6), "tusz")
        s.blok("Korona", (0, 1.45, 0), (W, 2.3, W), SCIANA)
        s.blok("Korona gzyms", (0, 2.75, 0), (W + 0.5, 0.5, W + 0.5), "tusz")
        s.blok("Korona rdzeń", (0, (2.6 + y0 - 0.5) / 2.0, 0), (W - 3.0, y0 - 0.5 - 2.6, W - 3.0), "tusz")
        for sx in (-1, 1):                                      # narożne filarki od gzymsu do rantu hełmu
            for sz in (-1, 1):
                s.blok("Filarek", (sx * 8.1, (3.0 + y0 - 0.75) / 2.0, sz * 8.1), (1.8, y0 - 0.75 - 3.0, 1.8), SCIANA)
        i = 0
        for u in (-4.0, 0.0, 4.0):
            for x, z in ((u, 8.3), (u, -8.3), (8.3, u), (-8.3, u)):
                wys = 1.2 + 0.3 * (i % 2)
                kol = SCIANA if i % 2 == 0 else cien(s, SCIANA, 0.88)
                s.blok("Blanka", (x, 3.0 + wys / 2.0, z), (1.8, wys, 1.8), kol)
                i += 1
        # hełm: rant tusz, deska czołowa zloto, ostrosłup, krawędzie i gałka
        H = 7.6
        s.blok("Hełm rant", (0, y0 - 0.6, 0), (20.4, 0.35, 20.4), "tusz")
        s.blok("Hełm deska", (0, y0 - 0.2, 0), (20.8, 0.5, 20.8), "zloto")
        s.ostroslup("Hełm", (0, y0, 0), 10.0, 10.0, H, DACH)
        for sx in (-1, 1):
            for sz in (-1, 1):
                s.belka("Hełm krawędź", (sx * 10.1, y0 + 0.15, sz * 10.1), (0, y0 + H + 0.2, 0), 0.8, "zloto", "SmoothPlastic")
        s.blok("Gałka szyjka", (0, y0 + H + 0.3, 0), (1.0, 0.6, 1.0), "zloto")
        s.kula("Gałka", (0, y0 + H + 1.0, 0), 1.4, "zloto")


# --------------------------------------------------------------------------- szyld: sztandar gildii (w układzie bazy, zwisa pionowo)
def _sztandar(s, kotwice):
    """Sztandar 6 × 14 z 3 segmentów falujących ±8° na drążku zawieszonym wspornikiem pod prawym przednim narożnikiem
    korony, obrócony ku frontowi i w prawo (ry 35°) — cały poza bryłą wieży, nie zasłania drzwi ani okien. Płetwa tusz,
    na segmentach herb z trzech wielkich kształtów (koło zloto, kwadrat biel, trójkąt czerwien), złota frędzla i ogon
    jaskółczy. Środek ok. 17,5 nad ziemią. 27 części."""
    kx, ky, kz = kotwice["korona_rog"]
    xs, zs = 12.0, 9.4                                          # środek sztandaru w planie
    yd = ky - 0.5                                               # drążek wisi pod narożnikiem korony
    with s.cechy(kolizja=False):
        s.belka("Sztandar wspornik", (kx - 0.6, ky + 0.2, kz - 0.6), (xs, yd + 0.2, zs), 0.7, "tusz", "SmoothPlastic")
        s.belka("Sztandar zastrzał", (kx - 0.6, ky - 2.6, kz - 0.6), (xs - 0.8, yd, zs - 0.6), 0.5, "tusz", "SmoothPlastic")
        with s.uklad(pos=(xs, yd, zs), obrot=(0, 35, 0)):
            s.walec("Sztandar drążek", (0, 0, 0), 0.4, 7.8, "drewno_ciemne", "Wood", os="x")
            for zn in (-1, 1):
                s.blok("Sztandar gałka", (zn * 4.2, 0, 0), (1.0, 1.0, 1.0), "zloto", rot=(45, 0, 45))
            with contextlib.ExitStack() as st:
                st.enter_context(s.uklad(pos=(0, -0.35, 0)))
                L = 4.4
                for i, k in enumerate((8, -16, 16)):
                    st.enter_context(s.uklad(obrot=(k, 0, 0)))
                    s.blok("Sztandar", (0, -L / 2.0, 0), (6.0, L + 0.12, 0.4), DACH, "Fabric")
                    s.blok("Sztandar płetwa", (0, -L / 2.0, -0.35), (6.8, L + 0.3, 0.3), "tusz")
                    _herb(s, i, -L / 2.0)
                    st.enter_context(s.uklad(pos=(0, -L, 0)))
                s.blok("Sztandar frędzla", (0, 0.05, 0.05), (6.4, 0.6, 0.55), "zloto")
                for zn in (-1, 1):                              # ogon jaskółczy: dwa trójkąty ostrzem w dół
                    s.klin("Sztandar ogon", (zn * 1.5, -0.95, 0), (0.4, 1.8, 3.0), DACH, "Fabric", rot=(0, -zn * 90, 180))


def _herb(s, i, yc):
    """Jeden kształt herbu na segmencie i (lico segmentu z = +0,2): 0 koło zloto, 1 kwadrat biel, 2 trójkąt czerwien;
    każdy z podkładką tusz. 2 części (trójkąt 4)."""
    with s.cechy(cien=False):
        if i == 0:
            s.walec("Herb koło podkładka", (0, yc, 0.3), 1.85, 0.2, "tusz", os="z")
            s.walec("Herb koło", (0, yc, 0.5), 1.5, 0.3, "zloto", os="z")
        elif i == 1:
            s.blok("Herb kwadrat podkładka", (0, yc, 0.3), (3.4, 3.4, 0.2), "tusz", rot=(0, 0, 10))
            s.blok("Herb kwadrat", (0, yc, 0.5), (2.7, 2.7, 0.3), "biel", rot=(0, 0, 10))
        else:                                                   # trójkąt ostrzem w górę (dwa kliny, wysokie krawędzie w środku)
            for zn in (-1, 1):
                s.klin("Herb trójkąt podkładka", (zn * 0.95, yc - 0.1, 0.3), (0.2, 3.4, 1.9), "tusz", rot=(0, -zn * 90, 0))
                s.klin("Herb trójkąt", (zn * 0.75, yc - 0.15, 0.5), (0.3, 2.6, 1.5), "czerwien", rot=(0, -zn * 90, 0))


# --------------------------------------------------------------------------- żart: rusztowanie malarza (lewy bok, układ parteru)
def _rusztowanie(s):
    """4 krzywe słupy drewno, 3 pomosty drewno_jasne, zastrzały, wysięgnik z wiadrem na linie, kapiąca farba, kałuża,
    pędzel, chorągiewka duetu na słupie. Bez kolizji. Układ parteru (front = z +8)."""
    xs = (-12.7, -9.9)
    zs = (-1.0, 10.2)
    with s.cechy(kolizja=False):
        for i, x in enumerate(xs):
            for j, z in enumerate(zs):
                k = (4 if (i + j) % 2 else -5)
                wys = 16.5 if j == 0 else 15.0
                zestaw.lamana(s, "Rusztowanie słup", [(wys * 0.55, 0.6, k), (wys * 0.45, 0.55, -2 * k)], "drewno", "Wood",
                              start=(x, -0.2), z=z)
        for y in (4.6, 9.2, 13.8):
            s.blok("Pomost", (-11.3, y, 4.6), (3.6, 0.5, 12.2), "drewno_jasne", "WoodPlanks")
        s.belka("Zastrzał", (-13.15, 0.6, -0.6), (-13.15, 9.0, 9.8), 0.5, "drewno", "Wood")
        s.belka("Zastrzał", (-13.15, 9.6, -0.6), (-13.15, 13.4, 9.8), 0.5, "drewno", "Wood")
        s.belka("Zastrzał", (-12.4, 1.0, 10.6), (-9.6, 8.6, 10.6), 0.5, "drewno", "Wood")
        # wysięgnik z liną i wiadrem farby przed frontem
        s.blok("Wysięgnik", (-11.0, 14.3, 11.8), (0.5, 0.5, 4.0), "drewno", "Wood", rot=(0, 0, 0))
        s.blok("Lina", (-11.0, 11.6, 13.4), (0.3, 5.0, 0.3), "tusz")
        with s.uklad(pos=(-11.0, 7.4, 13.4), obrot=(0, 20, 16)):
            s.walec("Wiadro", (0, 1.1, 0), 1.2, 2.2, "metal_ciemny", os="y")
            s.walec("Wiadro farba", (0, 2.18, 0), 0.95, 0.2, SCIANA, os="y")
            s.blok("Wiadro kabłąk", (0, 2.9, 0), (2.6, 0.3, 0.3), "tusz", rot=(0, 0, 0))
        with s.cechy(cien=False):
            s.blok("Kapiąca farba", (-12.2, 5.6, 13.5), (0.6, 0.9, 0.6), SCIANA, rot=(0, 0, 45))
            s.blok("Kapiąca farba", (-12.4, 3.0, 13.5), (0.5, 0.7, 0.5), SCIANA, rot=(0, 0, 45))
            s.walec("Kałuża farby", (-12.0, 0.25, 13.2), 1.7, 0.2, SCIANA, os="y")
        # pędzel oparty o słup
        with s.uklad(pos=(-9.0, 0, 11.3), obrot=(0, 25, -16)):
            s.blok("Pędzel trzonek", (0, 1.6, 0), (0.4, 3.2, 0.4), "drewno_jasne")
            s.blok("Pędzel włosie", (0, 3.6, 0), (1.2, 1.0, 0.5), SCIANA)
        zestaw.choragiewka_duetu(s, (-12.7 + 0.6, 16.4, -1.0), "rycerz", ry=0, przechyl=12)


# --------------------------------------------------------------------------- rekwizyty przy wejściu
def _rekwizyty(s, rnd):
    zestaw.beczka(s, (10.8, 0, 6.4), "woda", przechyl=(0, -6))
    zestaw.skrzynia(s, (11.2, 0, 2.2), ry=-14, dl=3.6, a=3.0, przechyl=8)
    with s.cechy(kolizja=False):                               # puszki farby: duża–mała, jedna przewrócona
        s.walec("Puszka farby", (-7.2, 0.9, 9.8), 1.0, 1.8, "biel", os="y")
        s.walec("Puszka farby wieko", (-7.2, 1.9, 9.8), 1.05, 0.2, SCIANA, os="y")
        s.blok("Pędzel leżący", (-5.9, 0.35, 11.0), (2.6, 0.5, 0.5), "drewno_jasne", rot=(0, 30, 0))
    zestaw.kwiaty(s, (-5.5, 0, 7.6), ry=0, kolory=("zloto", "biel"))
