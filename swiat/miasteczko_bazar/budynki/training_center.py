# -*- coding: utf-8 -*-
"""Training Center — jeden budynek, jedno wejście, wybór mini-gry z jednej tablicy (D-063, D-074; w mieście wg D-085).

Miętowa bryła z różowym dachem (kod „koło” z palety — koła fortuny na bazarze nie ma, więc kolor jest wolny, a czerwień
zostaje dla karczmy). W środku na tylnej ścianie TABLICA WYBORU z sześcioma medalionami statystyk (Siła — miecz, Kondycja — serce,
Inteligencja — księga, Zręczność — strzała, Szczęście — koniczyna, Pancerz — tarcza), obok trener wskazujący tablicę
(E → okno wyboru mini-gry, które przenosi do mini-gry). Do tego słomiany manekin, mata i worek. Szyld: wielka
hantla przed piętrem i tarcza strzelnicza.

Sala treningowa (25.11.2026, sesja główna Karola i Pawła): budynek rozszerzony „w lewo” (patrząc z uliczki, −x modułu)
o salę na sześć stanowisk treningu AFK Pawła (src/server/TreningAFK.server.luau buduje je w Workspace/TreningAFK;
miejsca: STANOWISKA niżej → znaczniki.json „trening_afk” → src/shared/TreningAFKDane.luau). Sala jest otwarta od frontu
(bez słupów w świetle 24 st), lewy bok budynku ma przejście do sali pod podciągiem, a dach sali to szkło na krokwiach
(przezroczystość 0,55 — kamera gracza Roblox, Poppercam, przechodzi przez części przezroczyste ≥ 0,25, więc nie
wjeżdża w sufit i widać przez niego stanowiska).
Sala zajmuje miejsce niebieskiego domu placyku (dom_placyk_pn) — opis kolizji i wyboru w README pakietu.

Dwa rzędy po trzy z przejściem pośrodku (26.11.2026, prośba Pawła przekazana przez Karola: „wydłużając go lekko, żeby
te stanowiska AFK ze środka przenieść za pozostałe, żeby były 2 rzędy po 3 i przestrzeń po środku” — odczytane tak:
rzędy wzdłuż lewego i prawego boku sali, od frontu do tylnej ściany, wolne przejście pośrodku od placyku do tylnej
ściany; dwa stanowiska ze środka sali stoją teraz na końcu rzędów). Sala wydłużona o 3,2 st do tyłu (głębokość 16,8 →
20,0; tył 3,2 st za tylną ścianą budynku — dalej okap domu z kulis, a niewidzialna ściana pola gry stoi tuż za salą),
z prawym bokiem za budynkiem (ściana w linii jego lewej ściany). Lewy rząd (od frontu): Pancerz twarzą do placyku (NPC
z pomidorami 11 st przed graczem stoi na placyku), Szczęście i Zręczność twarzą do lewej ściany (stolik i bieżnia pod
ścianą — przodem do tyłu nie zmieściłyby się jeden za drugim); prawy rząd: Siła, Inteligencja, Kondycja twarzą do tylnej
ściany jak dotąd. Przejście 8,2 st (x −26,1 … −17,9 modułu, zmierzone na stanowiskach zbudowanych w Play), lampy nad nim.
Uwaga: podpowiedzi E stanowisk mają zasięg 10 st (skrypt Pawła), więc gracz podchodzący do Siły albo Inteligencji od
frontu dostaje podpowiedź następnego stanowiska w rzędzie; z przejścia każde startuje dobrze (README pakietu).
"""
import math
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.krzywe_miasteczko import zestaw  # noqa: E402
from swiat.krzywe_miasteczko.paleta import cien  # noqa: E402
from swiat.miasteczko_bazar import postacie, wspolne  # noqa: E402
from swiat.miasteczko_bazar.wspolne import Y_PODLOGI  # noqa: E402

NAZWA = "TrainingCenter"
OBRYS = (22, 20)
WYSOKOSC = 30
BUDZET = 360
SCIANA, DACH = "tynk_mieta", "dach_kolo"
ZB = -10.0 + 1.2
TRENER = (7.4, -5.6)
STATYSTYKI = ("sila", "kondycja", "inteligencja", "zrecznosc", "szczescie", "pancerz")
# sala treningowa po lewej (układ modułu): x od lewej ściany sali do lewego boku budynku, z od tyłu do frontu sali
# (front sali cofnięty o 3,2 względem frontu budynku — ławka placyku zostaje na swoim miejscu). 26.11.2026: tył z −10,0
# na −13,2 (3,2 st za tylną ścianą budynku; dalej o 0,9 okap domu z kulis, kalenica sali kończy się 0,1 przed nim)
SALA_X = (-35.2, -11.0)
SALA_Z = (-13.2, 6.8)
H_SALI = (16.4, 14.4)           # wysokość ściany tylnej i belki frontu (dach szklany opada ku frontowi)
# stanowiska treningu AFK: (id z TreningAFKDane, x, z, obrót względem budynku w stopniach: 0 = twarzą do tylnej ściany,
# 90 = do lewej ściany, 180 = do placyku). 26.11.2026: dwa rzędy po trzy wzdłuż boków sali, przejście pośrodku
# (x −26,1 … −17,9). Odstępy z wymiarów rekwizytów w src/server/TreningAFK.server.luau: tabliczka za graczem (z +3,05
# … +3,35, x −4,4 … −0,8 stanowiska), punkt zejścia 3 st za graczem, stolik Szczęścia 3,9 przed graczem, bieżnia 3,2,
# ławka 3,05; Pancerz najdalej w lewo, ile pozwala cokół (mata 4,4).
STANOWISKA = (("Pancerz", -31.5, 3.0, 180), ("Szczescie", -29.5, -3.2, 90), ("Zrecznosc", -29.5, -8.8, 90),
              ("Sila", -13.5, 3.0, 0), ("Inteligencja", -13.5, -2.75, 0), ("Kondycja", -13.5, -8.5, 0))
LAMPY_SALI = (-22.0, (-8.4, -2.6, 3.0))     # x przejścia i z lamp nad nim
OKNA_SALI = ((-8.8, 6, DACH), (-3.0, -5, None), (2.9, 4, None))   # lewa ściana: z, przechył, okiennica
OBRYSY_DODATKOWE = (((SALA_X[0] + SALA_X[1]) / 2.0, (SALA_Z[0] + SALA_Z[1]) / 2.0, SALA_X[1] - SALA_X[0],
                     SALA_Z[1] - SALA_Z[0]),                  # dla bruku: sala to też obrys budynku
                    (SALA_X[1] + 0.6, (SALA_Z[0] - OBRYS[1] / 2.0) / 2.0, 1.2, -OBRYS[1] / 2.0 - SALA_Z[0]))  # prawy bok za budynkiem


def buduj(s, rnd):
    info = wspolne.skorupa(s, rnd, 22, 20, SCIANA, DACH, H0=14.0, otwor=14.0, otwor_x=1.0, H_otw=12.6, hp=5.5,
                           nawis=(2.2, 0.4, 1.0, 0.8), rz_p=-5.0, ry_p=4.0, dach_h=8.0, rz_d=9.0, okap=2.6, podzial=0.6,
                           markiza=(DACH, "biel"), okna_pietra=("prostokat",), duet="rycerz", na_pietrze=_szyld,
                           okna_boczne=(0, 1), otwarty_bok=(-1, ZB, SALA_Z[1]))  # przejście od tylnej ściany budynku
    _sala(s)
    _tablica_wyboru(s)
    postacie.postac(s, "trener", NAZWA + "/Trener", (TRENER[0], Y_PODLOGI, TRENER[1]), ry=-28)
    wspolne.punkt_e(s, NAZWA, "training_center", (2.6, -1.6), (TRENER[0] - 0.3, Y_PODLOGI + 4.6, TRENER[1] + 0.5),
                    typ="training_center", sklep="training_center", nazwa="Training Center — wybór mini-gry",
                    okno="Okno wyboru mini-gry (Paweł)", postac="trener", model=NAZWA + "/Trener", statystyki=list(STATYSTYKI),
                    kier=(0, 0, 1))
    wspolne.lampa(s, (-3.0, 13.45, -1.0), lancuch=1.6)
    wspolne.lampa(s, (4.5, 13.45, 1.5), lancuch=2.2)
    _sprzet(s)
    zf = info["front"]
    zestaw.lata(s, (11.0, 4.0, 1.5), 2.6, 2.2, "dach_twierdza", ry=90)
    zestaw.wypadniety_klocek(s, (-9.0, 2.3, zf), (-9.8, 0, zf + 1.3), SCIANA)
    zestaw.kwiaty(s, (7.4, 0, zf + 1.3), ry=-3, kolory=("czerwien", "biel"))


def _hantla(s):
    """Hantla 10 × 4 (szyld): drążek metal_ciemny i po dwa krążki w kolorze kodu z rantem tuszem."""
    s.walec("Hantla drążek", (0, 0, 0), 0.45, 9.0, "metal_ciemny", os="x")
    for sx in (-1, 1):
        s.walec("Hantla krążek", (sx * 3.0, 0, 0), 2.0, 1.0, DACH, os="x")
        s.walec("Hantla krążek", (sx * 4.0, 0, 0), 1.6, 0.9, cien(s, DACH, 0.85), os="x")
        s.walec("Hantla rant", (sx * 3.0, 0, 0), 2.2, 0.4, "tusz", os="x")
    s.walec("Hantla uchwyt", (0, 0, 0), 0.55, 3.0, "biel", os="x")


def _szyld(s, p):
    wspolne.szyld_na_pietrze(s, p, 0.2 * p["W1"], _hantla, skala=1.0, ry=24, rz=12, wysun=2.4)
    with s.uklad(pos=(-0.05 * p["W1"], p["hp"] * 0.48, p["D1"] / 2.0 + 0.2), obrot=(0, 0, 8)), s.cechy(kolizja=False):
        s.walec("Tarcza strzelnicza", (0, 0, 0.0), 2.5, 0.3, "tusz", os="z")
        s.walec("Tarcza strzelnicza", (0, 0, 0.15), 2.2, 0.3, "biel", os="z")
        s.walec("Tarcza strzelnicza", (0, 0, 0.3), 1.45, 0.3, DACH, os="z")
        s.walec("Tarcza strzelnicza", (0, 0, 0.45), 0.7, 0.3, "biel", os="z")
        with s.uklad(pos=(0.3, 0.2, 0.6), obrot=(-20, 25, 0)):
            s.blok("Strzała", (0, 0, 1.6), (0.35, 0.35, 3.2), "drewno_jasne")
            s.blok("Strzała lotka", (0, 0, 3.0), (0.25, 1.1, 1.0), "zloto")


def _medalion(s, nr, kolor):
    """Medalion statystyki Ø 3,2 z symbolem z klocków (bez liter)."""
    s.walec("Medalion obrys", (0, 0, 0.0), 1.8, 0.3, "tusz", os="z")
    s.walec("Medalion", (0, 0, 0.2), 1.6, 0.3, kolor, os="z")
    z = 0.45
    with s.cechy(cien=False):
        if nr == 0:                                            # Siła — miecz
            s.blok("Symbol miecz", (0.15, 0.15, z), (0.45, 2.2, 0.2), "tynk_blekit", rot=(0, 0, -40))
            s.blok("Symbol jelec", (-0.45, -0.45, z + 0.05), (1.1, 0.35, 0.2), "zloto", rot=(0, 0, 50))
        elif nr == 1:                                          # Kondycja — serce
            s.blok("Symbol serce", (0, -0.25, z), (1.15, 1.15, 0.2), "czerwien", rot=(0, 0, 45))
            for sx in (-1, 1):
                s.walec("Symbol serce", (sx * 0.42, 0.25, z), 0.55, 0.2, "czerwien", os="z")
        elif nr == 2:                                          # Inteligencja — otwarta księga
            for sx in (-1, 1):
                s.blok("Symbol księga", (sx * 0.55, 0, z), (1.0, 1.3, 0.2), "biel", rot=(0, 0, -sx * 8))
            s.blok("Symbol grzbiet", (0, -0.1, z + 0.05), (0.25, 1.4, 0.2), "dach_sklep")
        elif nr == 3:                                          # Zręczność — strzała
            s.blok("Symbol strzała", (-0.1, -0.1, z), (0.3, 2.0, 0.2), "drewno_jasne", rot=(0, 0, -45))
            s.klin("Symbol grot", (0.6, 0.6, z), (0.2, 0.7, 0.8), "tynk_blekit", rot=(0, 90, -45))
        elif nr == 4:                                          # Szczęście — koniczyna
            for x, y in ((0, 0.45), (0.45, 0), (0, -0.45), (-0.45, 0)):
                s.walec("Symbol listek", (x, y + 0.15, z), 0.42, 0.2, "lisc_jasny", os="z")
            s.blok("Symbol łodyżka", (0.25, -0.75, z), (0.2, 0.8, 0.2), "lisc_ciemny", rot=(0, 0, 25))
        else:                                                  # Pancerz — tarcza
            s.walec("Symbol tarcza", (0, 0, z), 0.8, 0.2, "dach_zbrojownia", os="z")
            s.walec("Symbol tarcza rant", (0, 0, z - 0.05), 0.95, 0.2, "zloto", os="z")


def _tablica_wyboru(s):
    kolory = ("dach_karczma", "dach_wylegarnia", "dach_sklep", "dach_lochy", "zloto", "dach_twierdza")
    with s.uklad(pos=(-1.0, 7.6, ZB), obrot=(0, 0, -2)), s.cechy(kolizja=False):
        s.blok("Tablica wyboru rama", (0, 0, 0.2), (13.4, 8.4, 0.4), "tusz")
        s.blok("Tablica wyboru", (0, 0, 0.5), (12.6, 7.6, 0.4), "drewno_jasne", "WoodPlanks")
        s.klin("Tablica wyboru daszek", (0, 4.7, 0.9), (14.0, 1.3, 1.6), DACH)
        s.blok("Tablica wyboru daszek rant", (0, 4.1, 0.9), (14.2, 0.3, 1.8), "tusz")
        for i in range(6):
            x, y = (-4.0 + 4.0 * (i % 3), 1.8 - 3.6 * (i // 3))
            with s.uklad(pos=(x, y, 0.75), obrot=(0, 0, (4, -6, 3, -3, 6, -5)[i])):
                _medalion(s, i, kolory[i])


def _sprzet(s):
    with s.cechy(kolizja=False, cien=False):
        s.blok("Mata", (-1.5, Y_PODLOGI + 0.06, 1.5), (9.0, 0.12, 7.0), cien(s, DACH, 0.9), "Fabric")
        s.blok("Mata pas", (-1.5, Y_PODLOGI + 0.1, 1.5), (9.4, 0.1, 0.6), "biel", "Fabric")
    # słomiany manekin z tarczą (prawa strona głównej izby, między trenerem a workiem, poza osią wejście → tablica).
    # 26.11.2026: z lewego przodu (−5,9; 5,0) przeniesiony tutaj — kamera gracza za plecami na stoisku E trenera
    # stała w głowie manekina (próba bazaru B06: zasłona „Manekin głowa”; części bez kolizji Poppercam nie omija)
    with s.uklad(pos=(7.6, Y_PODLOGI, 0.5), obrot=(0, -30, 0)):
        s.blok("Manekin podstawa", (0, 0.3, 0), (2.4, 0.6, 2.4), "drewno_ciemne", "Wood")
        with s.cechy(kolizja=False):
            s.blok("Manekin słup", (0, 2.5, 0), (0.5, 4.0, 0.5), "drewno", "Wood")
            s.blok("Manekin słoma", (0, 5.2, 0), (2.4, 3.0, 1.6), "dach_stajnia", rot=(0, 0, 6))
            s.blok("Manekin rzemień", (0, 5.2, 0), (2.5, 0.5, 1.7), "drewno_ciemne", rot=(0, 0, 32))
            s.blok("Manekin głowa", (0.2, 7.4, 0), (1.6, 1.6, 1.4), "biel", rot=(0, 0, -8))
            s.walec("Manekin cel", (0, 5.3, 0.85), 0.8, 0.2, DACH, os="z")
            s.blok("Manekin ramię", (0, 6.1, 0), (4.2, 0.5, 0.5), "drewno", "Wood", rot=(0, 0, -10))
    # worek treningowy (wisi ze stropu, spód nad głową gracza); stojak z hantlami spod lewej ściany zastąpiła sala
    with s.cechy(kolizja=False):
        s.blok("Worek lina", (6.8, 12.1, 5.0), (0.25, 2.4, 0.25), "tusz")
        s.walec("Worek", (6.8, 8.6, 5.0), 1.15, 4.6, "drewno_jasne", os="y")
        s.walec("Worek pas", (6.8, 9.6, 5.0), 1.22, 0.4, DACH, os="y")


def _sala(s):
    """Sala treningowa po lewej stronie budynku: posadzka, tylna i lewa ściana z cokołem i oknami, otwarty front
    z belką (bez słupów), dach ze szkła na krokwiach, różowy okap i kalenica, lampy, hantla-szyld nad frontem.
    Za tylną ścianą budynku (26.11.2026) prawy bok sali to ściana w linii lewej ściany budynku (x1 … x1 + T), a tylna
    ściana i dach sięgają do niej. Stanowiska stawia skrypt Pawła; tu tylko ich miejsca (STANOWISKA →
    wspolne.DODATKI["trening_afk"])."""
    x0, x1 = SALA_X
    z0, z1 = SALA_Z
    hT, hF = H_SALI
    T = 1.2
    zb = -OBRYS[1] / 2.0                       # tylna ściana budynku (lico zewnętrzne)
    xr = x1 + T if z0 < zb - 0.05 else x1      # prawy skraj sali za budynkiem
    sx, sz = (x0 + x1) / 2.0, (z0 + z1) / 2.0
    dl = z1 - z0

    def h_dachu(z):                            # spód szkła dachu nad punktem z (dach opada od tyłu ku frontowi)
        return hF + (hT - hF) * (z1 - z) / dl

    # posadzka na równi z posadzką budynku (ta kończy się na x −10,9)
    s.blok("Posadzka", (sx - 0.05, (Y_PODLOGI - 0.15) / 2.0, sz), (x1 - x0 + 0.1, Y_PODLOGI + 0.15, z1 - z0 - 0.2),
           "drewno_jasne", "WoodPlanks")
    s.blok("Próg", (sx + 0.05, 0.125, z1 - 0.3), (x1 - x0 - 1.4, 0.35, 0.6), "kamien_cokol", "Cobblestone")
    # cokół, ściana tylna, ściana lewa (prosta do wysokości frontu + klin pod spadek dachu)
    s.blok("Cokół", ((x0 - 0.25 + xr + (0.25 if xr > x1 else 0.0)) / 2.0, 0.6, z0 + T / 2.0),
           (xr - x0 + 0.25 + (0.25 if xr > x1 else 0.0), 1.4, T + 0.5), "kamien_cokol", "Cobblestone")
    s.blok("Cokół", (x0 + T / 2.0, 0.6, sz), (T + 0.5, 1.4, z1 - z0 + 0.5), "kamien_cokol", "Cobblestone")
    s.blok("Ściana tył", ((x0 + T + xr) / 2.0, hT / 2.0, z0 + T / 2.0), (xr - x0 - T, hT, T), SCIANA)
    s.blok("Ściana bok", (x0 + T / 2.0, hF / 2.0, sz), (T, hF, z1 - z0), SCIANA)
    s.klin("Ściana szczyt", (x0 + T / 2.0, hF + (hT - hF) / 2.0, sz), (T, hT - hF, z1 - z0), SCIANA, rot=(0, 180, 0))
    if xr > x1:
        # prawy bok za budynkiem: od tylnej ściany sali do tylnej ściany budynku, w linii jego lewej ściany
        a, b = z0 + T, zb
        h = h_dachu(a)
        s.blok("Cokół", (x1 + T / 2.0, 0.6, (z0 + T + 0.25 + zb - 0.25) / 2.0), (T + 0.5, 1.4, zb - z0 - T - 0.5),
               "kamien_cokol", "Cobblestone")
        s.blok("Ściana bok", (x1 + T / 2.0, h / 2.0, (a + b) / 2.0), (T, h, b - a), SCIANA)
    # nad przejściem z budynku: ściana pod piętrem budynku (zakrywa szczelinę między podciągiem a piętrem) — tylko
    # w obrysie budynku (od jego tylnej ściany do 1,8 st przed frontem sali)
    with s.cechy(kolizja=False):
        s.blok("Kolanko", (x1 - 0.55, (14.0 + hT) / 2.0 + 0.3, (zb - 0.2 + z1 - 1.8) / 2.0),
               (1.1, hT - 14.0 + 0.6, z1 - 1.8 - zb + 0.2), SCIANA)
    # front: belka nad otwartym frontem (kolizja — kamera zatrzymuje się na niej, nie za nią), pod nią rant tuszem
    s.blok("Nadproże", (sx, hF - 0.6, z1 - 0.5), (x1 - x0, 1.2, 1.0), SCIANA)
    with s.cechy(kolizja=False):
        s.blok("Rama otworu", (sx, hF - 1.35, z1 - 0.45), (x1 - x0, 0.35, 1.15), "tusz")
        for x, z in ((x0 + 0.5, z0 + 0.5), (x0 + 0.5, z1 - 0.5)):
            s.blok("Narożnik", (x, (1.3 + hF) / 2.0, z), (1.3, hF - 1.0, 1.3), "tusz")
        s.blok("Narożnik", (x1 - 0.55, (1.3 + hF) / 2.0, z1 - 0.55), (1.1, hF - 1.0, 1.1), "tusz")
        if xr > x1:
            s.blok("Narożnik", (xr - 0.5, (1.3 + hF) / 2.0, z0 + 0.5), (1.3, hF - 1.0, 1.3), "tusz")
        with s.cechy(cien=False):
            s.blok("Pas cienia", (x0 - 0.1, hF - 0.6, sz), (0.2, 0.9, z1 - z0 - 2.0), cien(s, SCIANA))
    # okna w lewej ścianie (na zewnątrz) + poświata od środka; nad stanowiskami zwróconymi do tej ściany
    for z, k, okiennica in OKNA_SALI:
        zestaw.okno(s, (x0, 7.5, z), 3.0, 4.0, przechyl=k, swiatlo="neon_okno", ry=-90, okiennica=okiennica,
                    strona_okiennicy=1)
        with s.cechy(kolizja=False, cien=False):
            s.blok("Okno od środka", (x0 + T + 0.1, 7.5, z), (0.2, 3.6, 2.6), "neon_okno", "Neon")
    # dach: szkło na krokwiach, spadek od tylnej ściany ku frontowi; prawy skraj w piętrze budynku (x1 + 0,3), a za
    # budynkiem nad prawą ścianą sali (xr + 0,3)
    kat = math.degrees(math.atan2(hT - hF, dl))
    L = math.hypot(dl, hT - hF)
    xp = xr + 0.3
    with s.uklad(pos=(sx, (hT + hF) / 2.0 + 0.1, sz), obrot=(kat, 0, 0)):
        s.blok("Szyba dachu", ((x0 + xp) / 2.0 - sx, 0, 0.3), (xp - x0, 0.2, L + 1.0), "D8F2EC", "SmoothPlastic", alfa=0.55)
        with s.cechy(kolizja=False):
            for x in (x0 + 0.3, x0 + 6.3, x0 + 12.3, x0 + 18.3, x1 - 0.3):
                s.blok("Belka krokiew", (x - sx, 0.3, 0.3), (0.5, 0.4, L + 1.0), "tusz")
            s.blok("Belka płatew", ((x0 + xp) / 2.0 - sx, 0.3, 0.3), (xp - x0, 0.35, 0.45), "tusz")
            # okap i kalenica od lica lewej ściany (nad nią nic nie wystaje ku okapowi domu zachodniego) do xr + 0,6
            s.blok("Okap", ((x0 + xp + 0.3) / 2.0 - sx, 0.05, L / 2.0 + 0.95), (xp + 0.3 - x0, 0.8, 0.7), DACH)
            s.blok("Dach kalenica", ((x0 + xp + 0.3) / 2.0 - sx, 0.25, -L / 2.0 - 0.1), (xp + 0.3 - x0, 0.7, 1.4), DACH)
    # lampy nad przejściem między rzędami stanowisk (punkt zawieszenia tuż nad spodem szkła)
    xl, zl = LAMPY_SALI
    for z in zl:
        wspolne.lampa(s, (xl, h_dachu(z) + 0.2, z), lancuch=1.2)
    # szyld nad frontem sali: hantla jak na piętrze budynku (mniejsza)
    with s.uklad(pos=(sx, hF + 1.9, z1 + 0.2), obrot=(0, 0, 6), skala=0.55), s.cechy(kolizja=False):
        _hantla(s)
    # miejsca stanowisk (świat Studio): środek maty na posadzce i obrót stanowiska w stopniach (jak D.obrot u Pawła)
    kx, _, kz = wspolne.kierunek(s, (0, 0, 1))
    ry_bud = math.degrees(math.atan2(kx, kz))
    lista = []
    for id_, x, z, o in STANOWISKA:
        a = math.radians(o)                    # gracz patrzy w −Z stanowiska obróconego o o stopni wokół Y
        lista.append({"id": id_, "pozycja": wspolne.swiat(s, (x, Y_PODLOGI, z)), "obrot": round(ry_bud + o, 2),
                      "przod": wspolne.kierunek(s, (round(-math.sin(a), 6), 0, round(-math.cos(a), 6)))})
    wspolne.DODATKI["trening_afk"] = {
        "opis": "miejsca sześciu stanowisk treningu AFK w sali Training Center (środek maty na posadzce, świat Studio; "
                "obrot = stopnie obrotu stanowiska w Roblox, gracz patrzy w −Z stanowiska = „przod”). Wpisane do "
                "src/shared/TreningAFKDane.luau (D.miejsca).",
        "stanowiska": lista}
