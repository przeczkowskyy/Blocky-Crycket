# -*- coding: utf-8 -*-
"""RYCERZ „Blocky” — jeden z dwóch bohaterów-maskotek (kanon: B&C/Postacie/Rycerz.md, obraz KeyArt.png).

Kanciasty ludzik R15 w stalowej zbroi płytowej (naramienniki, napierśnik z obojczykiem, nałokcice, nakolanniki,
nagolenniki), stalowy hełm z otwartą twarzą (zadziorny uśmiech, grube brwi), niebieski tabard ze złotą lamówką,
brązowy pas ze stalową klamrą i wielki miecz w prawej dłoni (akcesorium na RightGripAttachment). Tarcza
(klasa Wojownik: blok tarczą) jest przedmiotem drugiej ręki: widać ją tylko wtedy, gdy jest założona (D-071).

CIAŁO BAZOWE + STRÓJ Z PRZEDMIOTÓW (D-071, kontrakt swiat/postacie/EKWIPUNEK.md):
  cialo()      goły Rycerz („rycerz_cialo”): te same klocki, kości, zaczepy i klipy; twarz Rycerza, krótka brązowa
               czupryna (osobne akcesorium rycerz_wlosy na HairAttachment, hełm ją chowa), lniana koszula
               z krótkim rękawem i dekoltem, niebieskie krótkie spodenki, bose stopy;
  przedmioty() hełm, zbroja z tabardem, nogawice (część zbroi), pas, rękawice, trzewiki z nagolennikami, miecz,
               tarcza — każdy przedmiot to segmenty (sztywne akcesoria, po jednym na kość, w układzie środka
               klocka kości) albo akcesorium na zaczepie (broń);
  ubierz()     zakłada przedmioty na ciało (powłoka zastępuje gołe bryły kości, hełm chowa włosy);
  zbuduj()     jak dotąd: [Rycerz w pełnym stroju kanonicznym (KANON, bez tarczy), miecz, tarcza];
  warianty()   stroje z STROJE, segmenty i ikony całych przedmiotów dla przebuduj.py (wynik/rycerz/ekwipunek/).
Wspólny kod ekwipunku (Przedmiot, ubierz, kopiuj_klipy, zaczep_ekwipunku) jest w swiat/postacie/ekwipunek.py
(do 15.11 w sekcji „ekwipunek: wspólne” w rycerz.py).
Klipy liczą się RAZ na postaci odniesienia (ODNIESIENIE_KLIPOW = pełny strój z tarczą, czyli dawny model) i są
kopiowane bez zmian na ciało i każdy strój — ten sam ruch niezależnie od ubrania.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/rycerz.py --wyj <folder> --klip idle
    python -B swiat/postacie/rycerz.py --kontrola          # kontrola przenikania we wszystkich strojach (bez Blendera)
    python -B swiat/postacie/rycerz.py --kontrola --stroj bojowy

Klipy (30 kl./s; postać patrzy w +Z i w tę stronę atakuje):
  idle (oddech, miecz w gotowości, pętla), chod (pętla), atak_miecz (zamach znad głowy, trafienie kl. 15),
  wiwat (miecz w górę, pętla) — szkice pisane kluczami co kilka klatek;
  klipy walki (pozy kluczowe zamieniane na klucz w KAŻDEJ klatce, jak w zwiadowca.py):
    blok            zasłona tarczą, cios w tarczę kl. 11 (0,37 s — tak, jak gra prototyp walki v2);
    unik            ciężki odskok w lewo (ok. 1,7 studa) i powrót na miejsce startu;
    trafienie       szarpnięcie w tył kl. 4 i powrót;
    upadek          pada na plecy (ciałem na ukos), miecz obok, tarcza przy lewej ręce; kończy się leżeniem;
    ciecie          Potężne cięcie: szeroki poziomy zamach z obrotem tułowia, trafienie kl. 18;
    miazdzacy_cios  wyskok i cios z góry: klinga na wysokości piersi celu kl. 22 (trafienie), sztych w ziemi kl. 23;
    kamienna_skora  tupnięcie kl. 14 i poza obronna (tarcza przed siebie, miecz nad tarczą) trzymana do kl. 34.
  Klatki trafienia są też w słowniku CHWILE. Każdy klip walki zaczyna się i kończy w pozie z klatki 0 klipu idle
  (płynne przejście do spoczynku). Opisy z tarczą dotyczą stroju „bojowy”; bez tarczy (pełny strój kanoniczny,
  goły) lewa ręka robi ten sam ruch: zasłona przedramieniem w rękawicy.
Proporcje przerysowane: duża głowa w hełmie (ok. 1/3 wzrostu), szeroka klatka, krótkie masywne nogi.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie.biblioteka.postac import (R15_KOSCI, Akcesorium, Postac, katy_z_macierzy, macierz_obrotu, mnoz,
                                              razy_wektor)
# wspólny kod ekwipunku (EKWIPUNEK.md pkt 4); SKROTY_KOSCI i ZACZEPY_CHWYTU zostają widoczne także jako rycerz.*
# (do 15.11 sekcja „ekwipunek: wspólne” była w tym pliku)
from swiat.postacie.ekwipunek import (SKROTY_KOSCI, ZACZEPY_CHWYTU, Przedmiot, kopiuj_klipy,  # noqa: F401
                                      ubierz, zaczep_ekwipunku)

ID = "rycerz"
NAZWA = "Rycerz Blocky"
# stal zbroi trochę ciemniejsza i chłodniejsza niż w palecie biblioteki (jak na obrazie referencyjnym);
# len, spodenki i włosy — goły Rycerz (ciało bazowe)
PALETA = {"stal": "A8B4C8", "stal_cien": "75839C", "stal_ciemna": "4D576D", "niebieski": "2C6BE0",
          "len": "EDE3CC", "len_cien": "D3C4A2", "wlosy": "7A4A24", "wlosy_ciemne": "5A3519"}

# klatki trafienia / chwili efektu w klipach walki (dla odtwarzacza walki; 30 kl./s)
CHWILE = {"atak_miecz": 15, "blok": 11, "trafienie": 4, "ciecie": 18, "miazdzacy_cios": 22, "kamienna_skora": 14}


# --------------------------------------------------------------------------- miecz (akcesorium na prawej dłoni)
def miecz():
    """Wielki miecz: rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z)."""
    a = Akcesorium("rycerz_miecz", "Wielki miecz Rycerza", zaczep="RightGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(0, 0, -45))
    a.blok("Rekojesc", (0, 0, 0), (0.24, 1.05, 0.24), "brazowy_ciemny", "matowy", faza=0.04)
    for y in (-0.3, 0.0, 0.3):
        a.blok("Owijka", (0, y, 0), (0.28, 0.07, 0.28), "brazowy", "matowy", faza=0.0)
    a.blok("Glowica", (0, -0.66, 0), (0.42, 0.3, 0.42), "zloto", "metal", faza=0.08)
    a.blok("Glowica kamien", (0, -0.66, 0.23), (0.16, 0.14, 0.06), "niebieski_jasny", "swiecacy", faza=0.02)
    # jelec: końce zadarte ku ostrzu; rozpiętość 1,4 (szerszy przechodził przez przedramię w wiwacie i ataku)
    a.blok("Jelec", (0, 0.64, 0), (1.1, 0.24, 0.36), "stal_ciemna", "metal", faza=0.06)
    for zn in (1, -1):
        a.blok("Jelec koniec", (zn * 0.58, 0.74, 0), (0.24, 0.44, 0.4), "zloto", "metal", faza=0.06)
    a.blok("Jelec srodek", (0, 0.66, 0), (0.46, 0.4, 0.44), "zloto", "metal", faza=0.08)
    a.blok("Klejnot", (0, 0.66, 0.235), (0.2, 0.2, 0.06), "niebieski", "swiecacy", faza=0.02)
    a.blok("Klejnot tyl", (0, 0.66, -0.235), (0.2, 0.2, 0.06), "niebieski", "swiecacy", faza=0.02)
    # klinga: szeroka, z ciemniejszym zbroczem po obu stronach płazu
    a.blok("Klinga", (0, 2.21, 0), (0.62, 2.7, 0.16), "stal", "metal", faza=0.04)
    a.blok("Zbrocze", (0, 2.0, 0), (0.14, 2.2, 0.2), "stal_cien", "metal", faza=0.0)
    a.ostroslup("Sztych", (0, 3.86, 0), (0.62, 0.6, 0.16), "stal", "metal", gora=(0.0, 0.16))
    return a


# --------------------------------------------------------------------------- tarcza (akcesorium na lewej dłoni)
def tarcza():
    """Tarcza trójkątna (heater) w kolorach Rycerza: złota rama, niebieskie pole, stalowa głowica tarczy i złoty romb
    z granatowym środkiem (jak godło na tabardzie). Wzór: tarcza zestawu rycerza (zestaw_rycerz.py), dopasowana do
    klocków Blocky'ego. Układ dłoni (blok `uklad(obrot=(−90, 0, 0))` znosi obrót zaczepu): y wzdłuż przedramienia
    ku łokciowi, +X na zewnątrz, +Z przód. Lico tarczy patrzy w +X (skręcone o 10° do przodu), więc przy zwisającej
    ręce tarcza wisi przy boku; w bloku dłoń obraca się tak, że lico patrzy przed postać."""
    a = Akcesorium("rycerz_tarcza", "Tarcza Rycerza", zaczep="LeftGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(90, -80, 0))
    with a.uklad(obrot=(-90, 0, 0)):
        for y in (0.3, 0.7):
            a.blok("Pas", (0.6, y, 0), (0.24, 0.12, 0.44), "brazowy_ciemny", "matowy", faza=0.0)
        with a.uklad(pos=(0.78, 0.4, 0), obrot=(0, 80, 0)):           # lico tarczy = lokalne +Z
            a.blok("Rama", (0, 0.45, 0), (1.5, 0.7, 0.12), "zloto", "metal", faza=0.04)
            a.ostroslup("Rama szpic", (0, -0.45, 0), (1.5, 1.1, 0.12), "zloto", "metal", rot=(0, 0, 180),
                        gora=(0.0, 0.12), faza=0.0)
            a.blok("Pole", (0, 0.44, 0.07), (1.28, 0.64, 0.06), "niebieski", "matowy", faza=0.0)
            a.ostroslup("Pole szpic", (0, -0.36, 0.07), (1.28, 0.96, 0.06), "niebieski", "matowy", rot=(0, 0, 180),
                        gora=(0.0, 0.06), faza=0.0)
            a.blok("Glowa tarczy", (0, 0.62, 0.085), (1.28, 0.26, 0.06), "stal", "metal", faza=0.02)
            a.blok("Nit", (0.5, 0.62, 0.12), (0.08, 0.08, 0.04), "zloto", "metal", faza=0.0)
            a.blok("Nit 2", (-0.5, 0.62, 0.12), (0.08, 0.08, 0.04), "zloto", "metal", faza=0.0)
            a.blok("Godlo", (0, 0.02, 0.11), (0.5, 0.5, 0.05), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
            a.blok("Godlo srodek", (0, 0.02, 0.14), (0.24, 0.24, 0.04), "niebieski_ciemny", "polysk", rot=(0, 0, 45),
                   faza=0.0)
            a.blok("Tyl", (0, 0.25, -0.08), (0.9, 0.8, 0.06), "stal_ciemna", "metal", faza=0.0)
    return a


# --------------------------------------------------------------------------- Rycerz: ciało bazowe („goły”)
CIALO_TYP = "czlowiek"
KLASY = ("wojownik",)
WYMIARY = {"Head": (1.6, 1.5, 1.45),
           "UpperTorso": (2.2, 1.5, 1.2), "LowerTorso": (2.2, 0.4, 1.2),
           "UpperArm": (0.95, 0.95, 0.95), "LowerArm": (0.95, 0.75, 0.95), "Hand": (0.9, 0.35, 0.9),
           "UpperLeg": (1.05, 0.8, 1.05), "LowerLeg": (1.05, 0.75, 1.05), "Foot": (1.05, 0.35, 1.35)}
# przedmioty pełnego stroju kanonicznego (zbuduj()); tarcza poza kanonem — widać ją tylko po założeniu (D-071)
KANON = ("rycerz_helm", "rycerz_zbroja", "rycerz_nogawice", "rycerz_pas", "rycerz_rekawice", "rycerz_buty",
         "rycerz_miecz")
ODNIESIENIE_KLIPOW = KANON + ("rycerz_tarcza",)      # geometria, na której liczą się klipy (= dawny model z tarczą)
# stroje do plansz i kontroli (przebuduj.py -> wynik/rycerz/ekwipunek/)
STROJE = {"golas": (),
          "pelny": KANON,
          "bojowy": KANON + ("rycerz_tarcza",),
          "lekki": ("rycerz_zbroja", "rycerz_nogawice", "rycerz_buty", "rycerz_miecz"),
          "helm_i_miecz": ("rycerz_helm", "rycerz_miecz")}
NAZWY_STROJOW = {"golas": "goły (ciało bazowe)", "pelny": "pełny strój", "bojowy": "pełny strój z tarczą",
                 "lekki": "zbroja bez hełmu i rękawic", "helm_i_miecz": "sam hełm i miecz"}
PLANSZA_ZBIORCZA = ("golas", "pelny", "lekki", "helm_i_miecz")      # goły | pełny | dwa częściowe
# filmy w stroju (strój, klip): dowód, że przedmioty idą za kośćmi; blok i kamienna skóra z tarczą i bez niej
FILMY_EKWIPUNKU = (("golas", "idle"), ("golas", "ciecie"), ("golas", "upadek"), ("bojowy", "blok"),
                   ("bojowy", "kamienna_skora"), ("pelny", "blok"), ("lekki", "miazdzacy_cios"),
                   ("helm_i_miecz", "unik"))


def _postac(id, nazwa):
    """Postać R15 o klockach Rycerza (kości, stawy, 18 zaczepów R15), jeszcze bez brył."""
    return Postac(id, nazwa, typ="r15", faza=0.05, paleta=PALETA, wymiary=WYMIARY)


def _twarz(p):
    """Twarz Rycerza na klocku głowy (zostaje w każdym stroju)."""
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2                                                   # przednia ściana głowy (skóra)
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.27
            p.blok("Oko " + s, (x, 0.1, z + 0.02), (0.2, 0.3, 0.08), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.04, 0.18, z + 0.07), (0.08, 0.09, 0.04), "bialy", faza=0.0)
            # grube brwi, lekko skośne (7°) — pewna siebie, nie zła mina
            p.blok("Brew " + s, (zn * 0.28, 0.33, z + 0.03), (0.38, 0.13, 0.1), "brazowy_ciemny", "matowy",
                   rot=(0, 0, zn * 7), faza=0.02)
            p.blok("Rumieniec " + s, (zn * 0.5, -0.17, z + 0.01), (0.14, 0.08, 0.04), "rumieniec", "matowy", faza=0.0)
        p.blok("Nos", (0, -0.04, z + 0.05), (0.2, 0.2, 0.12), "skora_cien", "matowy", faza=0.03)
        # szeroki, pewny siebie uśmiech: ciemne usta 0,9 × 0,22 z białym pasem zębów, oba kąciki uniesione
        p.blok("Usta", (0.0, -0.38, z + 0.02), (0.9, 0.22, 0.06), "tusz", faza=0.02)
        p.blok("Zeby", (0.0, -0.33, z + 0.05), (0.78, 0.1, 0.04), "bialy", faza=0.0)
        p.blok("Jezyk", (0.0, -0.45, z + 0.04), (0.36, 0.07, 0.04), "D9534A", "matowy", faza=0.0)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Kacik " + s, (zn * 0.47, -0.3, z + 0.02), (0.12, 0.2, 0.06), "tusz", faza=0.0,
                   rot=(0, 0, zn * 35))
        p.blok("Podbrodek", (0.0, -0.58, z + 0.02), (0.3, 0.06, 0.04), "skora_cien", "matowy", faza=0.0)


def wlosy():
    """Krótka brązowa czupryna gołego Rycerza (akcesorium Hair na HairAttachment = środek górnej ściany głowy):
    czapa na czubku, tył do połowy głowy, boki nad uszami z bakami, grzywka z trójkątnych kosmyków nad brwiami
    (kosmyki kończą się ok. 0,05 studa nad brwią) i sterczący kosmyk na czubku. Hełm ją chowa (znacznik „Wlosy”)."""
    a = Akcesorium("rycerz_wlosy", "Włosy Rycerza", zaczep="HairAttachment", typ="Hair", paleta=PALETA,
                   przymierz=False)
    a.znacznik = "Wlosy"
    w, h, d = WYMIARY["Head"]
    x, z = w / 2, d / 2                                       # boki i przód głowy względem zaczepu
    a.blok("Czupryna", (0, 0.08, -0.035), (w + 0.1, 0.2, d + 0.11), "wlosy", "matowy", faza=0.06)
    a.blok("Tyl", (0, -0.42, -z - 0.04), (w + 0.1, 0.86, 0.1), "wlosy", "matowy", faza=0.04)
    for zn, s in ((1, "L"), (-1, "P")):
        a.blok("Bok " + s, (zn * (x + 0.025), -0.3, -0.12), (0.06, 0.62, d - 0.33), "wlosy", "matowy", faza=0.02)
        a.blok("Baczek " + s, (zn * (x + 0.025), -0.66, z - 0.36), (0.06, 0.3, 0.16), "wlosy_ciemne", "matowy",
               faza=0.0)
    a.blok("Grzywka", (0, -0.08, z + 0.02), (w + 0.06, 0.16, 0.06), "wlosy", "matowy", faza=0.02)
    # kosmyki grzywki: trójkąty szpicem w dół, lekko zaczesane w prawo rycerza
    for xk, wys, szer in ((0.58, 0.2, 0.36), (0.2, 0.24, 0.42), (-0.2, 0.22, 0.4), (-0.58, 0.18, 0.34)):
        a.ostroslup("Kosmyk", (xk, -0.06 - wys / 2, z + 0.03), (szer, wys, 0.06), "wlosy", "matowy",
                    rot=(0, 0, 180 + 10), gora=(0.0, 0.06), faza=0.0)
    a.ostroslup("Czub", (-0.2, 0.26, 0.25), (0.34, 0.26, 0.34), "wlosy_ciemne", "matowy", rot=(-18, 0, 14),
                gora=(0.0, 0.0), faza=0.0)
    return a


def _golas(id, nazwa, zaczepy_ekwipunku=False):
    """Goły Rycerz bez klipów: twarz, lniana koszula z krótkim rękawem, krótkie spodenki, bose stopy, włosy.
    Klocki pełnego rozmiaru (jak w zbroi), ubranie wystaje 0,02–0,035 studa, spodenki 0,01 (bez wcięć i szpar)."""
    p = _postac(id, nazwa)
    p.typ_ciala = CIALO_TYP
    p.cialo({"glowa": "skora", "tulow": "len", "pas": "niebieski", "ramiona": "skora", "dlonie": "skora",
             "nogi": "skora", "stopy": "skora"})
    _twarz(p)
    with p.na("UpperTorso", od="srodek"):                         # lniana koszula: dekolt w szpic, łata, rąbek
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.ostroslup("Dekolt obszycie", (0, h / 2 - 0.22, z + 0.01), (0.62, 0.44, 0.03), "len_cien", "matowy",
                    rot=(0, 0, 180), gora=(0.0, 0.03), faza=0.0)
        p.ostroslup("Dekolt", (0, h / 2 - 0.17, z + 0.02), (0.44, 0.34, 0.03), "skora", "matowy",
                    rot=(0, 0, 180), gora=(0.0, 0.03), faza=0.0)
        for zn in (1, -1):
            p.blok("Sznurek", (0, h / 2 - 0.36, z + 0.035), (0.2, 0.04, 0.03), "brazowy", "matowy",
                   rot=(0, 0, zn * 28), faza=0.0)
        p.blok("Lata", (0.58, -0.3, z + 0.015), (0.32, 0.3, 0.03), "len_cien", "matowy", rot=(0, 0, 8), faza=0.0)
        p.blok("Rabek koszuli", (0, -h / 2 + 0.07, 0), (w + 0.04, 0.12, d + 0.04), "len_cien", "matowy", faza=0.02)
    # spodenki wystają tylko 0,01 studa (ściągacz, nogawka): pas i poły przedmiotów leżą o 0,02 nad klockiem —
    # w tej samej odległości ściany migotałyby (np. pas Zwiadowcy albo poły jego tuniki założone bez spodni)
    with p.na("LowerTorso", od="srodek"):                         # spodenki: ściągacz i troczki
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Sciagacz", (0, h / 2 - 0.08, 0), (w + 0.02, 0.14, d + 0.02), "niebieski_ciemny", "matowy", faza=0.02)
        for zn in (1, -1):
            p.blok("Troczek", (zn * 0.08, h / 2 - 0.2, z + 0.03), (0.06, 0.2, 0.03), "len", "matowy",
                   rot=(0, 0, zn * 10), faza=0.0)
    for strona in ("Left", "Right"):
        with p.na(strona + "UpperArm", od="srodek"):              # krótki rękaw (do połowy ramienia)
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Rekaw", (0, h / 2 - 0.24, 0), (w + 0.04, 0.52, d + 0.04), "len", "matowy", faza=0.04)
            p.blok("Rekaw rabek", (0, h / 2 - 0.55, 0), (w + 0.04, 0.1, d + 0.04), "len_cien", "matowy", faza=0.02)
        with p.na(strona + "UpperLeg", od="srodek"):              # nogawka spodenek, rąbek nad kolanem
            w, h, d = p.wymiary(strona + "UpperLeg")
            p.blok("Nogawka", (0, h / 2 - 0.22, 0), (w + 0.02, 0.48, d + 0.02), "niebieski", "matowy", faza=0.04)
            p.blok("Nogawka rabek", (0, h / 2 - 0.5, 0), (w + 0.04, 0.08, d + 0.04), "niebieski_ciemny", "matowy",
                   faza=0.02)
        with p.na(strona + "Foot", od="srodek"):                  # bosa stopa: zarys palców
            w, h, d = p.wymiary(strona + "Foot")
            for i in (-1, 0, 1):
                p.blok("Palec", (i * 0.3, -h / 2 + 0.075, d / 2 + 0.01), (0.035, 0.13, 0.03), "skora_cien",
                       "matowy", faza=0.0)
    for c in p.czesci:
        c["golas"] = True                                         # gołe bryły (zdejmuje je powłoka na tej kości)
    p.zaloz(wlosy())                                              # osobna siatka (w FBX ciała), hełm ją chowa
    if zaczepy_ekwipunku:
        for kosc in R15_KOSCI:
            p.zaczep(zaczep_ekwipunku(kosc), kosc, p.srodek(kosc))
    return p


# --------------------------------------------------------------------------- Rycerz: przedmioty stroju
def przedmioty():
    """Wszystkie przedmioty Rycerza (z tarczą) — rozbiór dawnego modelu z EKWIPUNEK.md pkt 3. Bryły są te same co
    w dawnym zbuduj() (te same liczby), tylko pogrupowane w segmenty po kościach."""
    m = _postac(ID + "_miara", NAZWA)
    W = m.wymiary

    def nowy(id, nazwa, slot, kategoria, **k):
        return Przedmiot(id, nazwa, slot, kategoria, m, cialo=CIALO_TYP, klasy=KLASY, zestaw=ID, paleta=PALETA, **k)

    # --- hełm z otwartą twarzą: kubeł z zaokrągloną kopułą, szeroki otwór na twarz, obręcz dookoła
    helm = nowy("rycerz_helm", "Hełm Rycerza", "Helmet", "Armor", ukrywa=("Wlosy",))
    a = helm.segment("Head")
    w, h, d = W("Head")
    z = d / 2
    hw, hd, hh = w + 0.32, d + 0.32, h + 0.1
    for zn, s in ((1, "L"), (-1, "P")):
        a.blok("Helm bok " + s, (zn * (w / 2 + 0.08), -0.0, 0), (0.16, hh, hd), "stal", "metal")
        a.blok("Policzek " + s, (zn * 0.72, -0.07, z + 0.08), (0.24, 0.86, 0.16), "stal", "metal")
        a.blok("Nit " + s, (zn * 0.72, 0.22, z + 0.18), (0.09, 0.09, 0.05), "stal_ciemna", "metal", faza=0.0)
        a.blok("Obrecz bok " + s, (zn * (w / 2 + 0.18), h / 2 - 0.12, 0), (0.06, 0.18, hd + 0.04),
               "stal_cien", "metal", faza=0.0)
        for zz in (-0.45, 0.0):
            a.blok("Nit bok " + s, (zn * (w / 2 + 0.18), -0.25, zz), (0.05, 0.1, 0.1), "stal_ciemna", "metal",
                   faza=0.0)
    a.blok("Helm tyl", (0, 0, -z - 0.08), (hw, hh, 0.16), "stal", "metal")
    a.blok("Obrecz tyl", (0, h / 2 - 0.12, -z - 0.18), (hw + 0.04, 0.18, 0.06), "stal_cien", "metal", faza=0.0)
    a.blok("Helm tyl listwa", (0, -0.12, -z - 0.18), (0.22, h - 0.5, 0.06), "stal_cien", "metal", faza=0.0)
    a.blok("Helm kopula", (0, h / 2 + 0.1, 0), (hw, 0.3, hd), "stal", "metal", faza=0.12)
    a.blok("Helm czubek", (0, h / 2 + 0.28, 0), (w - 0.2, 0.14, d - 0.2), "stal", "metal", faza=0.06)
    a.blok("Grzebien", (0, h / 2 + 0.34, -0.02), (0.22, 0.14, d + 0.08), "stal_cien", "metal", faza=0.05)
    a.blok("Czolo", (0, h / 2 - 0.1, z + 0.08), (hw, 0.24, 0.16), "stal", "metal")
    a.blok("Czolo obrecz", (0, h / 2 - 0.12, z + 0.18), (hw + 0.04, 0.18, 0.06), "stal_cien", "metal", faza=0.0)

    # --- zbroja: napierśnik z obojczykiem (gorget) i tabardem, naramienniki, nałokcice, poły tabardu
    zbr = nowy("rycerz_zbroja", "Zbroja Rycerza z tabardem", "Chest", "Armor")
    a = zbr.segment("UpperTorso", zakrywa=True, klocek="stal")
    w, h, d = W("UpperTorso")
    z = d / 2
    a.blok("Obojczyk", (0, h / 2 - 0.06, 0), (1.5, 0.28, d + 0.12), "stal_cien", "metal")
    a.blok("Tabard", (0, -0.08, z + 0.03), (1.3, h - 0.16, 0.06), "niebieski", "matowy", faza=0.0)
    a.blok("Tabard tyl", (0, -0.08, -z - 0.03), (1.3, h - 0.16, 0.06), "niebieski", "matowy", faza=0.0)
    for zn in (1, -1):
        a.blok("Lamowka", (zn * 0.68, -0.08, z + 0.045), (0.1, h - 0.16, 0.06), "zloto", "metal", faza=0.0)
        a.blok("Lamowka tyl", (zn * 0.68, -0.08, -z - 0.045), (0.1, h - 0.16, 0.06), "zloto", "metal", faza=0.0)
    a.blok("Godlo", (0, 0.05, z + 0.07), (0.34, 0.34, 0.05), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
    a.blok("Godlo srodek", (0, 0.05, z + 0.1), (0.16, 0.16, 0.04), "niebieski_ciemny", "polysk", rot=(0, 0, 45),
           faza=0.0)
    for strona, zn in (("Left", 1), ("Right", -1)):
        a = zbr.segment(strona + "UpperArm", zakrywa=True, klocek="stal_ciemna")
        w, h, d = W(strona + "UpperArm")
        a.blok("Naramiennik", (zn * 0.1, h / 2 - 0.06, 0), (1.32, 0.36, 1.32), "stal", "metal", faza=0.12)
        a.blok("Naramiennik lama 1", (zn * 0.16, h / 2 - 0.3, 0), (1.22, 0.2, 1.24), "stal_cien", "metal",
               faza=0.06)
        a.blok("Naramiennik lama 2", (zn * 0.2, h / 2 - 0.48, 0), (1.1, 0.18, 1.14), "stal", "metal", faza=0.05)
        a.blok("Naramiennik nit", (zn * 0.78, h / 2 - 0.06, 0.3), (0.06, 0.1, 0.1), "zloto", "metal", faza=0.0)
        a.blok("Naramiennik nit 2", (zn * 0.78, h / 2 - 0.06, -0.3), (0.06, 0.1, 0.1), "zloto", "metal", faza=0.0)
        a = zbr.segment(strona + "LowerArm", zakrywa=True, klocek="stal")
        w, h, d = W(strona + "LowerArm")
        a.blok("Nalokcica", (zn * 0.06, h / 2 - 0.05, -0.08), (0.95, 0.26, 0.9), "stal_cien", "metal", faza=0.06)
    # poła tabardu (przód i tył): sztywna, lekko odchylona od nóg (przy kroku noga nie przebija materiału)
    a = zbr.segment("LowerTorso")
    w, h, d = W("LowerTorso")
    z = d / 2
    for zk, s, kat in ((1, "", -15), (-1, " tyl", 15)):
        with a.uklad(pos=(0, -h / 2 + 0.02, zk * (z + 0.07)), obrot=(kat, 0, 0)):
            a.blok("Pola" + s, (0, -0.32, 0), (1.24, 0.64, 0.08), "niebieski", "matowy", faza=0.0)
            for zn in (1, -1):
                a.blok("Pola lamowka" + s, (zn * 0.62, -0.32, 0), (0.1, 0.64, 0.12), "zloto", "metal", faza=0.0)
            # dolny szpic (romb do połowy schowany pod połą) i złoty rąbek tuż za nim
            a.blok("Pola szpic" + s, (0, -0.64, -zk * 0.012), (0.62, 0.62, 0.06), "niebieski", "matowy",
                   rot=(0, 0, 45), faza=0.0)
            a.blok("Pola rabek" + s, (0, -0.69, -zk * 0.025), (0.74, 0.74, 0.06), "zloto", "metal",
                   rot=(0, 0, 45), faza=0.0)
            a.blok("Pola rabek poziom" + s, (0, -0.64, -zk * 0.025), (1.34, 0.1, 0.06), "zloto", "metal",
                   faza=0.0)

    # --- nogawice (część zbroi): brązowe biodra i stalowe uda z płytą
    nog = nowy("rycerz_nogawice", "Nogawice Rycerza", "Chest", "Armor", czesc_od="rycerz_zbroja")
    nog.segment("LowerTorso", zakrywa=True, klocek="brazowy")
    for strona in ("Left", "Right"):
        a = nog.segment(strona + "UpperLeg", zakrywa=True, klocek="stal")
        w, h, d = W(strona + "UpperLeg")
        a.blok("Udo plyta", (0, 0.05, d / 2 + 0.03), (0.8, 0.6, 0.06), "stal_cien", "metal", faza=0.02)

    # --- pas: stalowa klamra (brązowy pas biodrowy to klocek nogawic)
    pas = nowy("rycerz_pas", "Pas Rycerza", "Belt", "Armor")
    a = pas.segment("LowerTorso")
    w, h, d = W("LowerTorso")
    z = d / 2
    a.blok("Klamra", (0, 0, z + 0.04), (0.42, 0.34, 0.08), "stal", "metal", faza=0.03)
    a.blok("Klamra srodek", (0, 0, z + 0.08), (0.2, 0.16, 0.04), "brazowy_ciemny", faza=0.0)

    # --- rękawice: stalowe dłonie z mankietem
    rek = nowy("rycerz_rekawice", "Rękawice Rycerza", "Gloves", "Armor")
    for strona in ("Left", "Right"):
        a = rek.segment(strona + "Hand", zakrywa=True, klocek="stal_ciemna")
        w, h, d = W(strona + "Hand")
        a.blok("Mankiet", (0, h / 2 + 0.02, 0), (1.04, 0.2, 1.04), "stal", "metal", faza=0.05)

    # --- trzewiki z nagolennikami i nakolannikami
    but = nowy("rycerz_buty", "Trzewiki z nagolennikami", "Boots", "Armor")
    for strona in ("Left", "Right"):
        a = but.segment(strona + "LowerLeg", zakrywa=True, klocek="stal")
        w, h, d = W(strona + "LowerLeg")
        a.blok("Nakolannik", (0, h / 2 - 0.08, d / 2 + 0.06), (0.72, 0.36, 0.2), "stal_cien", "metal", faza=0.07)
        a.blok("Nagolennik", (0, -0.12, d / 2 + 0.03), (0.62, 0.42, 0.06), "stal", "metal", faza=0.02)
        a = but.segment(strona + "Foot", zakrywa=True, klocek="stal_ciemna")
        w, h, d = W(strona + "Foot")
        a.blok("Czubek", (0, -0.02, d / 2 + 0.03), (w - 0.1, 0.28, 0.1), "stal_cien", "metal", faza=0.03)
        a.blok("Podeszwa", (0, -h / 2 + 0.04, 0), (w + 0.04, 0.08, d + 0.04), "brazowy_ciemny", "matowy", faza=0.0)

    # --- broń: miecz (Weapon) i tarcza (druga ręka, tylko Wojownik — D-062)
    mie = nowy("rycerz_miecz", "Wielki miecz Rycerza", "Weapon", "Weapons")
    mie.na_zaczepie(miecz())
    tar = nowy("rycerz_tarcza", "Tarcza Rycerza", "OffHand", "Weapons")
    tar.na_zaczepie(tarcza())
    return [helm, zbr, nog, pas, rek, but, mie, tar]


def wybierz(ids, wszystkie=None):
    """Przedmioty o podanych id (w tej kolejności) z listy `wszystkie` (domyślnie świeże przedmioty())."""
    wszystkie = {x.id: x for x in (wszystkie or przedmioty())}
    return [wszystkie[i] for i in ids]


# --------------------------------------------------------------------------- Rycerz: klipy, ciało, stroje
_ODNIESIENIE = []


def postac_odniesienia():
    """Dawny model (pełny strój z tarczą) z klipami policzonymi tak jak przed D-071 — źródło klipów każdego stroju.
    Liczona raz na proces (klipy zależą od geometrii: stopy na ziemi, nic pod ziemią)."""
    if not _ODNIESIENIE:
        p = ubierz(_golas(ID, NAZWA), wybierz(ODNIESIENIE_KLIPOW), id=ID, nazwa=NAZWA)
        idle(p)
        chod(p)
        atak_miecz(p)
        wiwat(p)
        blok(p)
        unik(p)
        trafienie(p)
        upadek(p)
        ciecie(p)
        miazdzacy_cios(p)
        kamienna_skora(p)
        p.ustaw_poze_renderu("idle", 0)
        _ODNIESIENIE.append(p)
    return _ODNIESIENIE[0]


def cialo(zaczepy_ekwipunku=False):
    """Goły Rycerz „rycerz_cialo” z klipami postaci odniesienia. zaczepy_ekwipunku=True — dodatkowo 15 zaczepów
    Ekw<Kosc>Attachment (środek klocka kości) dla eksportu ciała do gry; w zbuduj() ich nie ma."""
    return kopiuj_klipy(postac_odniesienia(), _golas(ID + "_cialo", NAZWA + " (ciało bazowe)", zaczepy_ekwipunku))


def stroj(nazwa, wszystkie=None):
    """Rycerz w stroju z STROJE: postać „rycerz_<nazwa>”."""
    return ubierz(cialo(), wybierz(STROJE[nazwa], wszystkie), id="%s_%s" % (ID, nazwa),
                  nazwa="%s — %s" % (NAZWA, NAZWY_STROJOW[nazwa]))


def zbuduj():
    """[Rycerz w pełnym stroju kanonicznym (id „rycerz”, bez tarczy), miecz, tarcza] — jak przed D-071."""
    prz = przedmioty()
    p = ubierz(cialo(), wybierz(KANON, prz), id=ID, nazwa=NAZWA)
    po_id = {x.id: x for x in prz}
    # miecz i tarcza: osobne przedmioty (przedmioty/rycerz_miecz.fbx, rycerz_tarcza.fbx); w FBX postaci ich nie ma
    # (eksport=False), w renderach i filmach miecz jest w dłoni, tarczy nie ma (zakłada ją tylko strój „bojowy”)
    return [p, po_id["rycerz_miecz"].segmenty[0]["akc"], po_id["rycerz_tarcza"].segmenty[0]["akc"]]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rycerz/ekwipunek/): „plansze” — postacie ze STROJE (id rycerz_<strój>)
    i ikony całych przedmiotów; „eksport” — gołe ciało z zaczepami Ekw… (tylko klip idle: pozostałe klipy są
    w rycerz__<klip>.fbx, te same kości) i każdy segment kostny osobno."""
    prz = przedmioty()
    if rodzaj == "plansze":
        return [stroj(n, prz) for n in STROJE] + [x.ikona() for x in prz]
    if rodzaj == "eksport":
        c = cialo(zaczepy_ekwipunku=True)
        c.klipy = [k for k in c.klipy if k.nazwa == "idle"]
        return [c] + [s["akc"] for x in prz for s in x.segmenty if s["kosc"]]
    raise ValueError("rodzaj: plansze albo eksport")


def ekwipunek_json():
    """Dane ekwipunku bohatera (EKWIPUNEK.md pkt 5); ścieżki plików i trójkąty dopisuje przebuduj.py."""
    return {"bohater": ID, "cialo": CIALO_TYP, "klasy": list(KLASY), "kanon": list(KANON),
            "odniesienie_klipow": list(ODNIESIENIE_KLIPOW), "stroje": {k: list(v) for k, v in STROJE.items()},
            "wlosy": {"id": "rycerz_wlosy", "zaczep": "HairAttachment", "znacznik": "Wlosy"},
            "przedmioty": [x.opis() for x in przedmioty()]}


SLABOSCI = [
    "D-071: model główny (rycerz.fbx, plansza, filmy) to pełny strój kanoniczny BEZ tarczy — tarcza jest "
    "przedmiotem drugiej ręki, widać ją tylko w stroju „bojowy” (ekwipunek/rycerz_bojowy_*). Klipy liczy postać "
    "odniesienia z tarczą (dawny model) i kopiuje bez zmian, więc w blok i kamienna_skora bez tarczy lewa ręka "
    "robi zasłonę samym przedramieniem w rękawicy (nadgarstek zgięty ok. 90° — bez tarczy to zgięcie widać).",
    "Ciało bazowe i stroje: zbroja jest wtapiana w bryły kości (te same siatki <Kosc>_Geo), więc w rycerz.fbx strój "
    "nadal jest częścią ciała. Ubieranie w grze ma iść przez gołe ciało (ekwipunek/rycerz_cialo.fbx z zaczepami "
    "Ekw<Kosc>Attachment) i segmenty z ekwipunek/przedmioty/ — ta droga nie była sprawdzana w Studio "
    "(przezroczystość gołych brył pod powłoką, AddAccessory z własnymi nazwami zaczepów).",
    "Upadek bez zbroi i bez hełmu (goły): klip liczony na postaci odniesienia kładzie ciało na tylnej pole tabardu "
    "i na hełmie, więc goły Rycerz leży ok. 0,25 studa nad ziemią (najniżej głowa 0,247; w stroju pełnym 0,000). "
    "Z samym hełmem albo z samą zbroją leży na ziemi. Poprawka wymaga decyzji: osobny klip upadku dla ciała albo "
    "przesunięcie korzenia w grze zależne od stroju (kontrakt: klipy są wspólne).",
    "rycerz_cialo.fbx/.glb ma tylko klip idle (reszta klipów: rycerz__<klip>.fbx, te same kości i nazwy).",
    "Pas Rycerza po rozbiorze to sama klamra (brązowy pas biodrowy to klocek nogawic); szerszy pas jako nakładka "
    "zmieniłby wygląd kanonu — do decyzji właściciela. Nogawice są częścią zbroi (slot Chest, czesc_od) do decyzji "
    "o slocie Legs (EKWIPUNEK.md pkt 8).",
    "Goły Rycerz: fryzura, len koszuli (EDE3CC), niebieskie spodenki w kolorze tabardu i bose stopy z zarysem palców "
    "to propozycja do oceny. Włosy siedzą na HairAttachment (osobna siatka), hełm je chowa; w stroju bez hełmu "
    "(„lekki”) widać włosy przy naramiennikach — naramienniki stykają się z bokami włosów jak dotąd z hełmem.",
    "Miecz i tarcza są osobnymi przedmiotami (przedmioty/rycerz_miecz.fbx, rycerz_tarcza.fbx) — w FBX postaci ich "
    "nie ma; w grze trzeba je dać jako Tool albo akcesoria na RightGripAttachment i LeftGripAttachment.",
    "Tarczy nie ma na obrazie KeyArt ani w notatce kanonu — dodana jako przedmiot dla klasy Wojownik (blok tarczą); "
    "do oceny Game Directora. Jest przypięta do dłoni, nie do przedramienia: w bloku i w kamiennej skórze nadgarstek "
    "jest zgięty ok. 90°, żeby lico patrzyło przed siebie (zgięcie zasłania sama tarcza). Lico jest skręcone o 25° "
    "ku prawej stronie rycerza (SKOS_TARCZY), żeby z kamery walki (z prawego boku) było widać tarczę, nie krawędź; "
    "w kadrze 3/4 od lewej tarcza jest przez to trochę węższa i częściowo za lewym ramieniem.",
    "Bryły sztywno przypięte do kości: naramienniki stykają się z bokami hełmu już w spoczynku, a przy uniesionej "
    "ręce albo skręcie głowy wchodzą w hełm do 0,18 studa (atak_miecz, ciecie; blok 0,15 po zmniejszeniu skrętu głowy, "
    "reszta klipów 0,08–0,15). To bryły ramienia, nie broń; poprawka wymagałaby zmiany brył naramienników albo hełmu "
    "(kanon wyglądu).",
    "atak_miecz (stary szkic, bez zmian): w kl. 16–26 prawa dłoń i przedramię wchodzą w tułów do 0,15 studa (miecz "
    "nie przenika), a stopy schodzą do −0,14 studa pod ziemię. Zgodnie z zasadą stary klip zmienia się tylko, gdy "
    "przenika broń — do decyzji, czy go przerobić na wzór klipów walki.",
    "Klipy walki przesuwają postać w samym klipie (kość LowerTorso): blok do 0,42 studa w tył, unik 1,7 studa "
    "w lewo, ciecie i miazdzacy_cios wypad 0,45 i 0,9 studa w przód — wszystkie kończą w punkcie startu. Upadek "
    "kończy się leżeniem 1,3 studa za punktem startu, ciałem lekko na ukos (−25°): z kamery walki leży w poprzek "
    "kadru, z kadru 3/4 od lewej widać go od strony nóg pod kątem (twarz słabo widoczna).",
    "Upadek: hełm jest głębszy niż tułów, więc leżący rycerz opiera się na hełmie i tylnej pole tabardu, a plecy są "
    "ok. 0,3 studa nad ziemią; tarcza leży licem w dół (widać jej spód), miecz leży na sztorc obok prawej ręki.",
    "Głębokie przysiady (miazdzacy_cios kl. 7, upadek kl. 19): tylna krawędź klocka goleni schodzi do 0,035 studa "
    "pod ziemię przy płaskiej stopie (sama bryła nogi). Chód (stary klip) do 0,064.",
    "Tabard i poły są sztywne (nie falują w chodzie); w atak_miecz poła tnie uda. Twarz bez mimiki (ten sam uśmiech "
    "przy trafieniu i upadku).",
    "Klipy to szkice (0,67–2 s), nie gotowa animacja; ciosy nie mają efektu cięcia (smugi), uderzenia w tarczę "
    "i tupnięcie — iskier ani fali (efekty w grze).",
    "Kontrola przenikania (python -B swiat/postacie/rycerz.py --kontrola) liczy skrzynki brył (ostrosłupy jak "
    "skrzynki), margines 0,06 studa; hełm z głową, tułów i pas to po jednej skrzynce na kość (pas bez poł, włosy "
    "w skrzynce głowy). Działa na każdym stroju z STROJE: „bojowy” daje dokładnie dawny wynik, w pozostałych "
    "przenika tylko stary atak_miecz (goły i sam hełm 0,12, lekki 0,10, pełny 0,15 studa). Nie sprawdza rąk "
    "z nogami; broń z nogami i miecz z tarczą sprawdzone osobnym skryptem (bez przecięć).",
    "LowerTorso i Root nie są w 0,0,0 (biodra na wysokości 1,9) — dla NPC bez znaczenia, ciało awatara może tego "
    "wymagać (sprawdzić przy pierwszym imporcie).",
]


# --------------------------------------------------------------------------- animacje
TRZYMA = {"RightUpperArm": (-12, 0, -4), "RightLowerArm": (-68, 0, 0)}   # miecz w gotowości (ostrze w górę-przód)


def idle(p):
    k = p.klip("idle", 60, petla=True)
    k.poza(0, TRZYMA)
    k.cykl("UpperTorso", "obrot", (2.0, 0, 0))
    k.cykl("UpperTorso", "obrot", (0, 2.0, 1.0), faza=0.25)
    k.cykl("Head", "obrot", (-1.5, 0, 1.5), faza=0.1)
    k.cykl("LeftUpperArm", "obrot", (0, 0, 2.5), srodek=(0, 0, 5))
    k.cykl("LeftLowerArm", "obrot", (-2.0, 0, 0), srodek=(-8, 0, 0), faza=0.1)
    # przedramię trzyma miecz w gotowości: jawny środek cyklu (−68°), żeby cykl nigdy nie zszedł do pozy wiszącej
    k.kanaly.pop(("RightLowerArm", "obrot"), None)
    k.cykl("RightLowerArm", "obrot", (-3.0, 0, 0), faza=0.15, srodek=TRZYMA["RightLowerArm"])
    k.kanaly.pop(("RightUpperArm", "obrot"), None)
    k.cykl("RightUpperArm", "obrot", (0, 0, -1.5), faza=0.15, srodek=TRZYMA["RightUpperArm"])
    return k


def chod(p, dlugosc=24, krok=32.0, ramiona=38.0):
    import math
    k = p.klip("chod", dlugosc, petla=True)
    k.cykl("LeftUpperLeg", "obrot", (krok, 0, 0), faza=0.0)
    k.cykl("RightUpperLeg", "obrot", (krok, 0, 0), faza=0.5)
    k.cykl("LeftUpperArm", "obrot", (ramiona, 0, 0), faza=0.5, srodek=(0, 0, 4))
    k.cykl("RightUpperArm", "obrot", (8, 0, 0), faza=0.0, srodek=TRZYMA["RightUpperArm"])
    k.cykl("RightLowerArm", "obrot", (-4, 0, 0), faza=0.0, srodek=TRZYMA["RightLowerArm"])
    for strona, faza in (("Left", 0.0), ("Right", 0.5)):
        for i in range(9):
            t = i / 8.0
            sn = math.sin(2 * math.pi * (t + faza))
            k.klucz(dlugosc * t, strona + "LowerLeg", obrot=(max(0.0, -sn) * krok * 1.4, 0, 0))
            k.klucz(dlugosc * t, strona + "Foot", obrot=(-max(0.0, sn) * 10, 0, 0))
    for i in range(9):
        t = i / 8.0
        sn = math.sin(2 * math.pi * (t + 0.5))
        k.klucz(dlugosc * t, "LeftLowerArm", obrot=(-12 - 10 * max(0.0, sn), 0, 0))
    k.cykl("LowerTorso", "przes", (0, 0.07, 0), czestosc=2, faza=0.25, srodek=(0, 0.07, 0))
    k.cykl("LowerTorso", "obrot", (0, 6, 0), faza=0.0)
    k.cykl("UpperTorso", "obrot", (0, -9, 0), faza=0.0, srodek=(4, 0, 0))
    k.cykl("Head", "obrot", (0, 3, 0), faza=0.0, srodek=(-3, 0, 0))
    return k


def atak_miecz(p):
    """Cięcie z góry: wzięcie z boku nad barkiem (ręka odchylona na zewnątrz, z dala od hełmu), łuk w dół
    z nadgarstkiem dociśniętym w uderzeniu (ostrze kładzie się do przodu), 2 klatki zatrzymania, powrót."""
    k = p.klip("atak_miecz", 32, petla=False)
    cz = (0.36, 0.48, 0.62)
    k.zamach("RightUpperArm", spocz=TRZYMA["RightUpperArm"], wziecie=(-150, 0, -40), uderzenie=(-48, 0, 6),
             czasy=cz, dobicie=0.0)
    k.zamach("RightLowerArm", spocz=TRZYMA["RightLowerArm"], wziecie=(-30, 0, 0), uderzenie=(-8, 0, 0), czasy=cz,
             dobicie=0.0)
    k.zamach("RightHand", wziecie=(55, 0, 0), uderzenie=(70, 0, 0), czasy=cz, dobicie=0.0)   # ostrze kładzie się do przodu
    # zatrzymanie po uderzeniu: 2 klatki w pozie uderzenia
    for kosc, w in (("RightUpperArm", (-48, 0, 6)), ("RightLowerArm", (-8, 0, 0)), ("RightHand", (70, 0, 0))):
        k.klucz(32 * cz[1] + 2, kosc, obrot=w)
    k.zamach("UpperTorso", wziecie=(-8, -14, 0), uderzenie=(14, 16, 0), czasy=cz)
    k.zamach("Head", wziecie=(-8, 8, 0), uderzenie=(4, -8, 0), czasy=cz)
    k.zamach("LeftUpperArm", wziecie=(-28, 0, 22), uderzenie=(20, 0, 14), czasy=cz)
    k.zamach("LeftLowerArm", wziecie=(-30, 0, 0), uderzenie=(-10, 0, 0), czasy=cz)
    k.zamach("LeftUpperLeg", wziecie=(-6, 0, 0), uderzenie=(-22, 0, 0), czasy=cz)
    k.zamach("LeftLowerLeg", wziecie=(4, 0, 0), uderzenie=(18, 0, 0), czasy=cz)
    k.zamach("RightUpperLeg", wziecie=(4, 0, 0), uderzenie=(12, 0, 0), czasy=cz)
    k.zamach("LowerTorso", wziecie=(0, -8, 0), uderzenie=(0, 10, 0), czasy=cz)
    return k


def wiwat(p, dlugosc=36):
    """Radość po zwycięstwie: miecz pionowo w górę, lewa pięść pompuje, dwa podskoki na pętlę."""
    k = p.klip("wiwat", dlugosc, petla=True)
    gora = {"RightUpperArm": (-170, 0, -16), "RightLowerArm": (-10, 0, 0), "RightHand": (84, 0, 0),
            "LeftUpperArm": (-160, 0, 22), "LeftLowerArm": (-18, 0, 0),
            "UpperTorso": (-7, 0, 0), "Head": (-12, 0, 0)}
    nizej = {"RightUpperArm": (-148, 0, -24), "RightLowerArm": (-28, 0, 0), "RightHand": (82, 0, 0),
             "LeftUpperArm": (-112, 0, 30), "LeftLowerArm": (-55, 0, 0),
             "UpperTorso": (3, 0, 0), "Head": (0, 0, 0)}
    for f, poza in ((0, nizej), (9, gora), (18, nizej), (27, gora)):
        k.poza(f, poza)
    # podskok: szczyt w klatkach 9 i 27 (razem z rękami w górze), stopy nigdy pod ziemią
    k.cykl("LowerTorso", "przes", (0, 0.16, 0), czestosc=2, faza=-0.25, srodek=(0, 0.16, 0))
    for strona in ("Left", "Right"):
        k.cykl(strona + "UpperLeg", "obrot", (-9, 0, 0), czestosc=2, faza=-0.25, srodek=(-9, 0, 0))
        k.cykl(strona + "LowerLeg", "obrot", (14, 0, 0), czestosc=2, faza=-0.25, srodek=(14, 0, 0))
    return k


# ---------------------------------------------------------------------------------------------------- klipy walki
# Pozy kluczowe zamieniane na klucz w KAŻDEJ klatce (jak w zwiadowca.py): stopy stoją płasko na ziemi, w powietrzu
# i przy padaniu nic (także miecz i tarcza) nie schodzi pod ziemię, a dłoń z bronią ustawia prosta odwrotna
# kinematyka (cel nadgarstka + kierunek klingi albo lica tarczy) — tor broni jest policzony, a nie zgadywany z kątów.
# Zmiany rób w pozach kluczowych w tym pliku, nie w Blenderze; po zmianie: python -B swiat/postacie/rycerz.py --kontrola
KOSCI = ("LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm",
         "RightLowerArm", "RightHand", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg",
         "RightFoot")
STOPY = ("LeftFoot", "RightFoot")
CIALO = ("Head", "UpperTorso", "LowerTorso")            # w te bryły (hełm, tułów, pas) broń ani dłoń nie może wejść
KONCZYNY = ("LeftLowerArm", "LeftHand", "RightLowerArm", "RightHand")
SKOS_TARCZY = 25        # o ile stopni lico tarczy w bloku i kamiennej skórze skręca z przodu ku prawej stronie rycerza
PLAZ_GOTOW = (0, 0, 1)  # płaz miecza w gotowości: do przodu jak w idle (bez obrotu klingi w dłoni na starcie klipu)


def _fk(p, poza):
    """Kinematyka wprost: {kość: (obrót w świecie, staw w świecie)} dla pozy {kość: {"obrot", "przes"}}."""
    W = {}
    for n, k in p.kosci.items():                          # rodzic zawsze przed dzieckiem
        v = poza.get(n, {})
        Rl = macierz_obrotu(*v.get("obrot", (0, 0, 0)))
        pr = v.get("przes", (0, 0, 0))
        if k["rodzic"] is None:
            W[n] = (Rl, tuple(k["staw"][i] + pr[i] for i in range(3)))
        else:
            Rp, tp = W[k["rodzic"]]
            st = p.kosci[k["rodzic"]]["staw"]
            dd = razy_wektor(Rp, tuple(k["staw"][i] - st[i] + pr[i] for i in range(3)))
            W[n] = (mnoz(Rp, Rl), tuple(tp[i] + dd[i] for i in range(3)))
    return W


def _bryly(p):
    """Wszystkie bryły (ciało i założone akcesoria) w układzie stawu swojej kości: lista słowników
    {kosc, c (środek), R (obrót), h (połowy wymiarów), n (nazwa), zrodlo ("cialo" albo id akcesorium), pkt (27 punktów:
    narożniki, środki krawędzi i ścian)}. Ostrosłupy i walce liczą się jako ich skrzynki (ostrożnie)."""
    if getattr(p, "_bryly", None) is None:
        d = p.json()
        s = p.skala or 1.0
        wynik = []

        def dodaj(c, zrodlo):
            st = p.kosci[c["kosc"]]["staw"]
            b = {"kosc": c["kosc"], "c": tuple(c["p"][i] / s - st[i] for i in range(3)), "R": macierz_obrotu(*c["r"]),
                 "h": tuple(v / s / 2.0 for v in c["s"]), "n": c["n"], "zrodlo": zrodlo}
            b["pkt"] = _siatka(b, None)
            wynik.append(b)
        for c in d["czesci"]:
            dodaj(c, "cialo")
        for a in d["akcesoria"]:
            for c in a["czesci"]:
                dodaj(c, a["id"])
        p._bryly = wynik
    return p._bryly


def _siatka(b, krok):
    """Punkty skrzynki bryły w układzie stawu: krok=None — 3×3×3, inaczej gęsto (co najwyżej `krok` studa)."""
    osie = []
    for i in range(3):
        n = 2 if krok is None else max(2, int(math.ceil(2 * b["h"][i] / krok)))
        osie.append([(-1 + 2.0 * j / n) * b["h"][i] for j in range(n + 1)])
    pk = []
    for x in osie[0]:
        for y in osie[1]:
            for z in osie[2]:
                lok = razy_wektor(b["R"], (x, y, z))
                pk.append(tuple(b["c"][i] + lok[i] for i in range(3)))
    return pk


def _najnizej(p, W, kosci, bron=True):
    mn = 1e9
    for b in _bryly(p):
        if b["kosc"] not in kosci or (b["zrodlo"] != "cialo" and not bron):
            continue
        R, t = W[b["kosc"]]
        for q in b["pkt"]:
            mn = min(mn, R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1])
    return mn


def _stopy_plasko(p, pz):
    """Stopy, których poza nie ustawia: płasko na ziemi, palcami tam, gdzie patrzą biodra (z ewentualnym skrętem
    uda)."""
    W = _fk(p, pz)
    for s in ("Left", "Right"):
        if s + "Foot" in pz.get("_wlasne", ()):
            continue
        Rg = W[s + "LowerLeg"][0]
        f = razy_wektor(mnoz(W["LowerTorso"][0], macierz_obrotu(0, pz[s + "UpperLeg"]["obrot"][1], 0)), (0, 0, 1))
        cel = macierz_obrotu(0, math.degrees(math.atan2(f[0], f[2])), 0)
        Rt = tuple(tuple(Rg[j][i] for j in range(3)) for i in range(3))
        pz[s + "Foot"] = {"obrot": tuple(round(v, 3) for v in katy_z_macierzy(mnoz(Rt, cel)))}


def _poza(p, poza, ziemia=True):
    """Poza kluczowa: {kość: (rx, ry, rz)} albo {kość: {"obrot":…, "przes":…}}; kość spoza słownika — spoczynek.
    ziemia=True: stopy (jeśli poza ich nie ustawia) płasko, a biodra jadą w pionie tak, by najniższy punkt stóp był
    na ziemi; ziemia="cialo": ciało RAZEM z bronią dociągnięte do ziemi po najniższym punkcie (siad, leżenie);
    ziemia=False: lot (biodra jak w pozie, ale nic, także broń, nie schodzi pod ziemię)."""
    pz = {"_wlasne": tuple(n for n in poza)}
    for n in KOSCI:
        v = poza.get(n, (0, 0, 0))
        pz[n] = dict(v) if isinstance(v, dict) else {"obrot": tuple(v)}
        pz[n].setdefault("obrot", (0, 0, 0))
    pz["LowerTorso"].setdefault("przes", (0, 0, 0))
    pz["_ziemia"] = ziemia
    _na_ziemi(p, pz)
    return pz


def _na_ziemi(p, pz):
    z = pz["_ziemia"]
    if z is True:
        _stopy_plasko(p, pz)
        dno = _najnizej(p, _fk(p, pz), STOPY, bron=False)
    elif z == "cialo":
        dno = _najnizej(p, _fk(p, pz), KOSCI)
    else:
        dno = min(0.0, _najnizej(p, _fk(p, pz), KOSCI))
    x, y, zz = pz["LowerTorso"]["przes"]
    pz["LowerTorso"]["przes"] = (x, round(y - dno, 4), zz)


def _n(v):
    d = math.sqrt(sum(x * x for x in v)) or 1.0
    return tuple(x / d for x in v)


def _kr(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _sk(a, b):
    return sum(a[i] * b[i] for i in range(3))


def _tr(m):
    return tuple(tuple(m[j][i] for j in range(3)) for i in range(3))


def _kolumny(x, y, z):
    return ((x[0], y[0], z[0]), (x[1], y[1], z[1]), (x[2], y[2], z[2]))


def _reka(p, pz, strona, cel, biegun, os=None, przod=None, swiat=False, swiat_broni=None):
    """Ustawia w pozie pz ramię, przedramię i dłoń strony („Left”/„Right”) tak, żeby nadgarstek trafił w cel
    (przesunięcie od stawu barku), a łokieć wyszedł w stronę `biegun` — w osiach tułowia (swiat=False) albo modelu
    (swiat=True). os / przod = kierunek broni w dłoni: miecz — os = klinga (+Y miecza), przod = płaz (+Z miecza);
    tarcza — os = kierunek, w który patrzy „palec” dłoni (oś Z dłoni), przod = −(oś Y dłoni); lico tarczy patrzy
    wtedy w (oś Y dłoni) × os. Osie broni liczą się w układzie swiat_broni (domyślnie jak swiat). Łokieć zgina się
    tylko w zawiasie (obrót przedramienia = sam rx), jak w klipach pisanych ręcznie."""
    W = _fk(p, pz)
    Rt = W["UpperTorso"][0]
    do_sw = (lambda v: v) if swiat else (lambda v: razy_wektor(Rt, v))
    sb = swiat if swiat_broni is None else swiat_broni
    do_sw_b = (lambda v: v) if sb else (lambda v: razy_wektor(Rt, v))
    a = math.dist(p.staw(strona + "LowerArm"), p.staw(strona + "UpperArm"))
    b = math.dist(p.staw(strona + "Hand"), p.staw(strona + "LowerArm"))
    d = do_sw(cel)
    dl = max(abs(a - b) + 0.05, min(a + b - 0.02, math.sqrt(_sk(d, d))))
    dh = _n(d)
    bg = do_sw(biegun)
    n = _n(tuple(bg[i] - _sk(bg, dh) * dh[i] for i in range(3)))
    ca = (a * a + dl * dl - b * b) / (2 * a * dl)
    sa = math.sqrt(max(0.0, 1 - ca * ca))
    u = tuple(ca * dh[i] + sa * n[i] for i in range(3))                 # kierunek ramienia (bark -> łokieć)
    E = tuple(a * u[i] for i in range(3))
    v = _n(tuple(dh[i] * dl - E[i] for i in range(3)))                  # kierunek przedramienia
    zc = tuple(v[i] - _sk(v, u) * u[i] for i in range(3))
    if _sk(zc, zc) < 1e-6:
        zc = tuple(-x for x in n)
    Y = tuple(-x for x in u)
    Z = _n(zc)
    X = _kr(Y, Z)
    Rua = _kolumny(X, Y, Z)
    pz[strona + "UpperArm"] = {"obrot": katy_z_macierzy(mnoz(_tr(Rt), Rua))}
    th = -math.degrees(math.acos(max(-1.0, min(1.0, _sk(u, v)))))
    pz[strona + "LowerArm"] = {"obrot": (th, 0.0, 0.0)}
    if os is not None:
        Rla = mnoz(Rua, macierz_obrotu(th, 0, 0))
        A = _n(do_sw_b(os))
        F = do_sw_b(przod)
        F = _n(tuple(F[i] - _sk(F, A) * A[i] for i in range(3)))
        Yh = tuple(-x for x in F)
        Rh = _kolumny(_kr(Yh, A), Yh, A)
        pz[strona + "Hand"] = {"obrot": katy_z_macierzy(mnoz(_tr(Rla), Rh))}
    return pz


def _ciaglosc(ob, poprz):
    """Ten sam obrót zapisany kątami najbliższymi poprzedniemu kluczowi (bez skoku −170° → +170° przez zero):
    (rx, ry, rz) ≡ (180 − rx, ry + 180, rz + 180), każdy kąt także ± 360."""
    if poprz is None:
        return tuple(ob)

    def blisko(a, b):
        return a + 360.0 * round((b - a) / 360.0)
    najl = None
    for c in (tuple(ob), (180.0 - ob[0], ob[1] + 180.0, ob[2] + 180.0)):
        c = tuple(blisko(c[i], poprz[i]) for i in range(3))
        dd = sum(abs(c[i] - poprz[i]) for i in range(3))
        if najl is None or dd < najl[0] - 1e-6:
            najl = (dd, c)
    return najl[1]


def _sekwencja(k, czasy, pozy, wyg=None):
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (wynik _poza albo słownik). Kąty przechodzą z łagodnym
    wejściem i wyjściem (wyg = {numer pozy: "liniowo"} — odcinek od tej pozy jednostajnie); gdy obie sąsiednie
    pozy stoją na ziemi, stopy są w każdej klatce płasko na ziemi; przy siadzie i leżeniu ciało z bronią leży na
    ziemi; w pozostałych odcinkach nic nie schodzi pod ziemię."""
    p = k.postac
    pozy = [pz if "_ziemia" in pz else _poza(p, pz) for pz in pozy]
    poprz = {}
    for pz in pozy:                                       # kąty póz najbliżej poprzedniej pozy (krótsza droga)
        for n in KOSCI:
            pz[n]["obrot"] = _ciaglosc(pz[n]["obrot"], poprz.get(n))
            poprz[n] = pz[n]["obrot"]
    poprz = {}
    for f in range(int(czasy[0]), int(czasy[-1]) + 1):
        i = max(j for j in range(len(czasy) - 1) if czasy[j] <= f) if f < czasy[-1] else len(czasy) - 2
        t = (f - czasy[i]) / float(czasy[i + 1] - czasy[i])
        e = t if (wyg or {}).get(i) == "liniowo" else t * t * (3 - 2 * t)
        a, b = pozy[i], pozy[i + 1]
        pz = {n: {"obrot": tuple(a[n]["obrot"][j] + (b[n]["obrot"][j] - a[n]["obrot"][j]) * e for j in range(3))}
              for n in KOSCI}
        p0, p1 = a["LowerTorso"]["przes"], b["LowerTorso"]["przes"]
        pz["LowerTorso"]["przes"] = tuple(p0[j] + (p1[j] - p0[j]) * e for j in range(3))
        z0, z1 = a["_ziemia"], b["_ziemia"]
        pz["_wlasne"] = tuple(set(a["_wlasne"]) | set(b["_wlasne"]))
        pz["_ziemia"] = z0 if z0 == z1 else False
        _na_ziemi(p, pz)
        for n in KOSCI:
            ob = _ciaglosc(pz[n]["obrot"], poprz.get(n))
            poprz[n] = ob
            k.klucz(f, n, obrot=tuple(round(v, 3) for v in ob), wyg="liniowo")
        k.klucz(f, "LowerTorso", przes=tuple(round(v, 4) for v in pz["LowerTorso"]["przes"]), wyg="liniowo")


def _baza(p):
    """Poza z klatki 0 klipu idle (miecz w gotowości): każdy klip walki w niej zaczyna się i kończy."""
    k = next(k for k in p.klipy if k.nazwa == "idle")
    return {kosc: tuple(round(v, 3) for v in k.wartosc(kosc, kanal, 0)) for (kosc, kanal) in k.kanaly
            if kanal == "obrot"}


def _z(baza, **zmiany):
    d = dict(baza)
    d.update(zmiany)
    return d


def _tarcza_przed(p, pz, cel=(0.1, -0.45, 1.36), skos=SKOS_TARCZY):
    """Lewa ręka: tarcza przed sobą (szpic w dół); cel nadgarstka w osiach tułowia. Lico patrzy w przód modelu
    skręcone o `skos` stopni w prawo (ku mieczowi) — jak tarcza równoległa do piersi przy lewym barku wysuniętym
    do przodu; dzięki temu z kamery walki (z prawego boku rycerza) widać lico tarczy, a nie samą krawędź."""
    a = math.radians(skos)
    return _reka(p, pz, "Left", cel=cel, biegun=(1, -0.6, 0), os=(-math.cos(a), 0, -math.sin(a)), przod=(0, -1, 0),
                 swiat_broni=True)


def blok(p, dl=30):
    """Zasłona tarczą (1 s): lewy bark do przodu, tarcza przed piersią, ugięte kolana (kl. 7); cios trafia w tarczę
    w kl. 11 (0,37 s: prototyp walki v2 startuje klip bloku 0,38 s przed trafieniem) — rycerz odjeżdża ok. 0,4 studa
    w tył, tułów odchyla się, tarcza dociśnięta do ciała; garda trzymana do kl. 21 i powrót do spoczynku (na miejsce
    startu). Miecz cały czas w gotowości za tarczą."""
    k = p.klip("blok", dl, petla=False)
    B = _baza(p)
    nogi = dict(LeftUpperLeg=(-26, 0, 6), LeftLowerLeg=(30, 0, 0), RightUpperLeg=(14, 0, -8), RightLowerLeg=(24, 0, 0))

    # głowa skręcona w lewo tylko o 6° (przy 16° lewy naramiennik wchodził w bok hełmu do 0,2 studa)
    def garda(przes, tulow=(8, -12, 0), glowa=(-6, 6, -2), biodra=(2, -22, 0), cel=(0.1, -0.45, 1.36)):
        pz = _poza(p, _z(B, LowerTorso={"obrot": biodra, "przes": przes}, UpperTorso=tulow, Head=glowa, **nogi))
        # miecz za tarczą: dłoń przed prawym biodrem, klinga w górę, w przód i na zewnątrz (z dala od hełmu)
        _reka(p, pz, "Right", cel=(-0.3, -0.75, 0.75), biegun=(-1, -0.5, 0), os=(-0.35, 0.75, 0.55), przod=PLAZ_GOTOW,
              swiat_broni=True)
        return _tarcza_przed(p, pz, cel)
    g1 = garda((0, 0, 0))
    uderz = garda((0, 0, -0.35), tulow=(0, -12, 0), glowa=(2, 6, -2), biodra=(-4, -22, 0), cel=(0.1, -0.4, 1.22))
    odbicie = garda((0, 0, -0.42), tulow=(4, -12, 0), glowa=(-2, 6, -2), cel=(0.1, -0.45, 1.3))
    g2 = garda((0, 0, -0.3))
    _sekwencja(k, (0, 7, 11, 15, 21, dl), (B, g1, uderz, odbicie, g2, B), wyg={1: "liniowo"})
    return k


def unik(p, dl=30):
    """Unik w zbroi (1 s), ciężej niż u Zwiadowcy: przysiad z przechyłem (kl. 5), niski odskok w lewo (+X, ok. 0,45
    studa nad ziemią), ciężkie lądowanie w przysiadzie ok. 1,7 studa w bok (kl. 14), chwila, krótki podskok z powrotem
    i spoczynek w punkcie startu. Tarcza prowadzi (lewa ręka na zewnątrz), miecz w gotowości."""
    k = p.klip("unik", dl, petla=False)
    B = _baza(p)
    przysiad = _poza(p, _z(B, LowerTorso={"obrot": (8, 0, 6), "przes": (-0.15, 0, 0)}, UpperTorso=(12, 0, 4),
                           Head=(-10, 0, -4),
                           LeftUpperLeg=(-40, 0, 6), LeftLowerLeg=(66, 0, 0), RightUpperLeg=(-36, 0, -4),
                           RightLowerLeg=(62, 0, 0),
                           LeftUpperArm=(-14, 0, 22), LeftLowerArm=(-30, 0, 0)))
    lot = _poza(p, _z(B, LowerTorso={"obrot": (2, 0, -14), "przes": (0.9, 0.45, 0)}, UpperTorso=(4, 0, -6),
                      Head=(-4, 0, 10),
                      LeftUpperLeg=(-24, 0, 22), LeftLowerLeg=(40, 0, 0), RightUpperLeg=(-14, 0, 8),
                      RightLowerLeg=(50, 0, 0),
                      LeftUpperArm=(-24, 0, 46), LeftLowerArm=(-30, 0, 0)), ziemia=False)
    laduje = _poza(p, _z(B, LowerTorso={"obrot": (10, 0, -8), "przes": (1.7, 0, 0)}, UpperTorso=(14, 0, -4),
                         Head=(-12, 0, 6),
                         LeftUpperLeg=(-46, 0, 16), LeftLowerLeg=(72, 0, 0), RightUpperLeg=(-34, 0, 6),
                         RightLowerLeg=(60, 0, 0),
                         LeftUpperArm=(-30, 0, 34), LeftLowerArm=(-36, 0, 0)))
    trzyma = _poza(p, _z(B, LowerTorso={"obrot": (6, 0, -6), "przes": (1.65, 0, 0)}, UpperTorso=(10, 0, -2),
                         Head=(-10, 0, 4),
                         LeftUpperLeg=(-38, 0, 14), LeftLowerLeg=(60, 0, 0), RightUpperLeg=(-28, 0, 6),
                         RightLowerLeg=(50, 0, 0),
                         LeftUpperArm=(-26, 0, 30), LeftLowerArm=(-34, 0, 0)))
    krok = _poza(p, _z(B, LowerTorso={"obrot": (4, 0, 4), "przes": (0.7, 0.3, 0)}, UpperTorso=(6, 0, 2),
                       LeftUpperLeg=(-20, 0, 4), LeftLowerLeg=(30, 0, 0), RightUpperLeg=(-24, 0, -6),
                       RightLowerLeg=(36, 0, 0),
                       LeftUpperArm=(-10, 0, 16), LeftLowerArm=(-20, 0, 0)), ziemia=False)
    for pz in (przysiad, lot, laduje, trzyma, krok):
        _miecz_gotow(p, pz)
    _sekwencja(k, (0, 5, 10, 14, 19, 24, dl), (B, przysiad, lot, laduje, trzyma, krok, B),
               wyg={1: "liniowo", 2: "liniowo"})
    return k


def _miecz_gotow(p, pz, cel=(-0.3, -0.8, 0.8), os=(-0.35, 0.85, 0.4), przod=PLAZ_GOTOW):
    """Prawa ręka: miecz w gotowości (jak w idle), klinga w górę, lekko w przód i na zewnątrz — w osiach modelu,
    więc przechył tułowia (unik) nie kładzie klingi nad hełmem. Płaz do przodu jak w idle, żeby na starcie klipu
    miecz nie obracał się w dłoni."""
    return _reka(p, pz, "Right", cel=cel, biegun=(-1, -0.5, 0), os=os, przod=przod, swiat_broni=True)


def _szarpniecie(p, B):
    """Szarpnięcie po ciosie: tułów i głowa w tył, krok w tył, tarcza w bok, miecz odlatuje w prawo i w górę."""
    pz = _poza(p, _z(B, LowerTorso={"obrot": (-8, 6, 0), "przes": (0, 0, -0.4)}, UpperTorso=(-16, 8, 3),
                     Head=(-18, -10, 6), LeftUpperArm=(-20, 0, 40), LeftLowerArm=(-40, 0, 0),
                     RightUpperLeg=(16, 0, -4), RightLowerLeg=(20, 0, 0), LeftUpperLeg=(-12, 0, 4),
                     LeftLowerLeg=(12, 0, 0)))
    return _reka(p, pz, "Right", cel=(-1.1, 0.15, 0.25), biegun=(-0.3, -1, 0), os=(-0.75, 0.65, 0.1), przod=(0, 0, 1),
                 swiat_broni=True)


def trafienie(p, dl=20):
    """Reakcja na cios (0,67 s): szarpnięcie tułowia i głowy w tył z krokiem w tył (kl. 4), tarcza i miecz odlatują
    na boki, powrót do spoczynku na miejsce startu."""
    k = p.klip("trafienie", dl, petla=False)
    B = _baza(p)
    szarp = _szarpniecie(p, B)
    wraca = _poza(p, _z(B, LowerTorso={"obrot": (-3, 2, 0), "przes": (0, 0, -0.2)}, UpperTorso=(-5, 4, 1),
                        Head=(-6, -2, 2), LeftUpperArm=(-6, 0, 16), LeftLowerArm=(-20, 0, 0),
                        RightUpperLeg=(6, 0, -2), RightLowerLeg=(8, 0, 0)))
    _miecz_gotow(p, wraca, cel=(-0.45, -0.6, 0.7), os=(-0.45, 0.85, 0.3))
    _sekwencja(k, (0, 4, 11, dl), (B, szarp, wraca, B), wyg={0: "liniowo"})
    return k


def upadek(p, dl=60, ODCHYL=-25):
    """Pokonanie (2 s): szarpnięcie, chwiejny krok w tył, kolana się uginają, siada ciężko i pada na plecy (kl. 36),
    nogi podbite, ostatnie drgnięcie; leży z rękami rozrzuconymi, ciałem lekko na ukos (ODCHYL = −25°: z kamery
    walki z prawego boku rycerza ciało leży w poprzek kadru, a z kadru 3/4 od lewej nie widać samych podeszew;
    przy +65° ciało leżało prawie wzdłuż osi obu kamer i czytało się jak kupka klocków) — miecz leży obok prawej
    ręki wzdłuż ciała, tarcza płasko na ziemi przy lewej (licem w dół). Ostatnia klatka: leżenie (do utrzymania)."""
    k = p.klip("upadek", dl, petla=False)
    B = _baza(p)
    szarp = _szarpniecie(p, B)
    chwiej = _poza(p, _z(B, LowerTorso={"obrot": (-6, -10, 6), "przes": (0, 0, -0.6)}, UpperTorso=(10, -6, -6),
                         Head=(18, -8, -8), LeftUpperArm=(-8, 0, 26), LeftLowerArm=(-20, 0, 0),
                         RightUpperArm=(-16, 0, -30), RightLowerArm=(-46, 0, 0),
                         RightUpperLeg=(14, 0, -6), RightLowerLeg=(22, 0, 0), LeftUpperLeg=(-10, 0, 4),
                         LeftLowerLeg=(16, 0, 0)))
    ugina = _poza(p, _z(B, LowerTorso={"obrot": (4, -6, 2), "przes": (0, 0, -0.7)}, UpperTorso=(14, -4, -2),
                        Head=(20, -8, -6),
                        LeftUpperLeg=(-50, 0, 8), LeftLowerLeg=(86, 0, 0), RightUpperLeg=(-44, 0, -8),
                        RightLowerLeg=(80, 0, 0),
                        LeftUpperArm=(-6, 0, 30), LeftLowerArm=(-20, 0, 0), RightUpperArm=(-10, 0, -34),
                        RightLowerArm=(-30, 0, 0)))
    siad = _poza(p, {"LowerTorso": {"obrot": (-30, ODCHYL / 2, 0), "przes": (0, 0, -1.0)}, "UpperTorso": (-8, 0, 0),
                     "Head": (10, 0, 0),
                     "LeftUpperLeg": (-70, 0, 12), "LeftLowerLeg": (64, 0, 0), "RightUpperLeg": (-64, 0, -12),
                     "RightLowerLeg": (56, 0, 0),
                     "LeftUpperArm": (-4, 0, 44), "LeftLowerArm": (-20, 0, 0),
                     "RightUpperArm": (-4, 0, -46), "RightLowerArm": (-24, 0, 0)}, ziemia="cialo")

    Ry = macierz_obrotu(0, ODCHYL, 0)

    def o(v):                                     # kierunek względem leżącego ciała -> osie modelu
        return razy_wektor(Ry, v)

    def lezy(biodra=(-86, ODCHYL, 0), glowa=(16, -12, 0),
             nogi=((-6, 0, 10), (10, 0, 0), (-40, 0, -8), (62, 0, 0))):
        pz = {"LowerTorso": {"obrot": biodra, "przes": (0, 0, -1.3)}, "UpperTorso": (-4, 0, 0), "Head": glowa,
              "LeftUpperLeg": nogi[0], "LeftLowerLeg": nogi[1], "RightUpperLeg": nogi[2], "RightLowerLeg": nogi[3]}
        pz = _poza(p, pz, ziemia="cialo")
        # prawa: miecz leży obok ciała, klinga ku stopom; lewa: tarcza płasko licem w dół przy lewej ręce
        _reka(p, pz, "Right", cel=o((-1.25, -0.27, 0.35)), biegun=o((0, 0.3, -1)), os=o((0.08, -0.08, 1)),
              przod=o((-1, 0, 0)), swiat=True)
        _reka(p, pz, "Left", cel=o((1.25, -0.03, 0.3)), biegun=o((0, 0.3, -1)), os=o((0, 0, -1)), przod=o((1, 0, 0)),
              swiat=True)
        pz["_wlasne"] = tuple(set(pz["_wlasne"]) | {"LeftHand", "RightHand", "LeftUpperArm", "RightUpperArm"})
        _na_ziemi(p, pz)
        return pz
    lezy1 = lezy()
    odbicie = lezy(biodra=(-78, ODCHYL, 0), glowa=(6, -12, 0), nogi=((-20, 0, 10), (14, 0, 0), (-52, 0, -8), (70, 0, 0)))
    _sekwencja(k, (0, 4, 12, 20, 28, 36, 40, 46, dl),
               (B, szarp, chwiej, ugina, siad, lezy1, odbicie, lezy1, lezy1), wyg={0: "liniowo", 4: "liniowo"})
    return k


def ciecie(p, dl=48):
    """Potężne cięcie (1,6 s), wyraźnie większe niż atak_miecz: skręt tułowia w prawo o ok. 60° z mieczem wyciągniętym
    daleko w bok i w tył (kl. 12), szeroki poziomy zamach na wysokości barku z obrotem tułowia w lewo i wypadem —
    klinga przechodzi przed rycerzem na wprost w kl. 18 (trafienie), dobicie w lewo (kl. 21), zatrzymanie i powrót.
    Ręka z mieczem cały czas na zewnątrz tułowia; płaz poziomo (tnie ostrze)."""
    k = p.klip("ciecie", dl, petla=False)
    B = _baza(p)
    # kl. 6: miecz idzie w górę i w prawo (klinga z dala od twarzy), tułów zaczyna skręt
    unosi = _poza(p, _z(B, LowerTorso={"obrot": (0, -12, 0)}, UpperTorso=(2, -12, 0), Head=(-2, 0, 3),
                        LeftUpperLeg=(-12, 0, 6), LeftLowerLeg=(16, 0, 0), RightUpperLeg=(6, 0, -8),
                        RightLowerLeg=(12, 0, 0),
                        LeftUpperArm=(-24, 0, 14), LeftLowerArm=(-30, 0, 0)))
    _reka(p, unosi, "Right", cel=(-1.0, 0.35, 0.25), biegun=(0, -1, 0), os=(-0.55, 0.8, -0.2), przod=(0, 0, 1),
          swiat_broni=True)
    zamach = _poza(p, _z(B, LowerTorso={"obrot": (0, -30, 0), "przes": (0, 0, -0.15)}, UpperTorso=(4, -30, 0),
                         Head=(-4, 40, 10),
                         LeftUpperLeg=(-24, 0, 10), LeftLowerLeg=(30, 0, 0), RightUpperLeg=(14, 0, -12),
                         RightLowerLeg=(22, 0, 0),
                         LeftUpperArm=(-38, 0, 30), LeftLowerArm=(-40, 0, 0)))
    _reka(p, zamach, "Right", cel=(-1.1, 0.25, -0.8), biegun=(0, -1, 0.2), os=(-0.45, 0.15, -1), przod=(0, 1, 0),
          swiat_broni=True)
    srodek = _poza(p, _z(B, LowerTorso={"obrot": (3, -8, 0), "przes": (0, 0, 0.05)}, UpperTorso=(6, -6, 0),
                         Head=(-6, 14, 0),
                         LeftUpperLeg=(-32, 0, 9), LeftLowerLeg=(36, 0, 0), RightUpperLeg=(20, 0, -11),
                         RightLowerLeg=(22, 0, 0),
                         LeftUpperArm=(-30, 0, 32), LeftLowerArm=(-36, 0, 0)))
    _reka(p, srodek, "Right", cel=(-1.3, 0.05, 0.5), biegun=(0, -1, 0), os=(-1, 0.05, 0.25), przod=(0, 1, 0),
          swiat_broni=True)
    uderz = _poza(p, _z(B, LowerTorso={"obrot": (6, 24, 0), "przes": (0, 0, 0.4)}, UpperTorso=(8, 20, 0),
                        Head=(-8, -34, 0),
                        LeftUpperLeg=(-42, 0, 8), LeftLowerLeg=(44, 0, 0), RightUpperLeg=(26, 0, -10),
                        RightLowerLeg=(22, 0, 0),
                        LeftUpperArm=(-10, 0, 40), LeftLowerArm=(-30, 0, 0)))
    _reka(p, uderz, "Right", cel=(-0.2, -0.1, 1.38), biegun=(-1, -0.5, 0), os=(0.2, 0, 1), przod=(0, 1, 0),
          swiat=True)
    dobicie = _poza(p, _z(B, LowerTorso={"obrot": (6, 40, 0), "przes": (0, 0, 0.45)}, UpperTorso=(8, 30, 0),
                          Head=(-8, -54, 0),
                          LeftUpperLeg=(-42, 0, 8), LeftLowerLeg=(44, 0, 0), RightUpperLeg=(26, 0, -10),
                          RightLowerLeg=(22, 0, 0),
                          LeftUpperArm=(-4, 0, 44), LeftLowerArm=(-28, 0, 0)))
    _reka(p, dobicie, "Right", cel=(0.75, -0.15, 1.15), biegun=(-1, -0.5, 0), os=(1, 0, 0.45), przod=(0, 1, 0),
          swiat=True)
    trzyma = _poza(p, _z(B, LowerTorso={"obrot": (4, 38, 0), "przes": (0, 0, 0.4)}, UpperTorso=(6, 28, 0),
                         Head=(-6, -50, 0),
                         LeftUpperLeg=(-40, 0, 8), LeftLowerLeg=(42, 0, 0), RightUpperLeg=(24, 0, -10),
                         RightLowerLeg=(22, 0, 0),
                         LeftUpperArm=(-6, 0, 40), LeftLowerArm=(-28, 0, 0)))
    _reka(p, trzyma, "Right", cel=(0.7, -0.25, 1.1), biegun=(-1, -0.5, 0), os=(1, -0.1, 0.5), przod=(0, 1, 0),
          swiat=True)
    powrot = _poza(p, _z(B, LowerTorso={"obrot": (2, 12, 0), "przes": (0, 0, 0.15)}, UpperTorso=(4, 8, 0),
                         Head=(-4, -16, 0),
                         LeftUpperLeg=(-14, 0, 4), LeftLowerLeg=(16, 0, 0), RightUpperLeg=(8, 0, -4),
                         RightLowerLeg=(10, 0, 0),
                         LeftUpperArm=(-10, 0, 12), LeftLowerArm=(-20, 0, 0)))
    _miecz_gotow(p, powrot, cel=(-0.2, -0.8, 0.85), os=(0.3, 0.8, 0.5))
    _sekwencja(k, (0, 6, 12, 15, 18, 21, 27, 38, dl), (B, unosi, zamach, srodek, uderz, dobicie, trzyma, powrot, B),
               wyg={2: "liniowo", 3: "liniowo", 4: "liniowo"})
    return k


def miazdzacy_cios(p, dl=50):
    """Miażdżący cios (1,67 s): przysiad z mieczem wzniesionym nad prawym barkiem (kl. 8), wyskok ok. 1,2 studa
    z klingą za głową (kl. 16), miecz pionowo w górę w szczycie (kl. 19), cios z góry przy lądowaniu w głębokim
    wypadzie — klinga przechodzi przed nim na wysokości piersi celu w kl. 22 (trafienie; tu też sztych najdalej
    w przód), sztych uderza w ziemię przed rycerzem w kl. 23, zatrzymanie, powrót.
    Tor klingi biegnie z prawej strony hełmu (dłoń na zewnątrz barku), tarcza odchylona w bok dla równowagi."""
    k = p.klip("miazdzacy_cios", dl, petla=False)
    B = _baza(p)
    przysiad = _poza(p, _z(B, LowerTorso={"obrot": (10, -6, 0)}, UpperTorso=(14, -6, 0), Head=(-16, 6, -14),
                           LeftUpperLeg=(-40, 0, 8), LeftLowerLeg=(70, 0, 0), RightUpperLeg=(-36, 0, -8),
                           RightLowerLeg=(66, 0, 0),
                           LeftUpperArm=(-30, 0, 46), LeftLowerArm=(-30, 0, 0)))
    _reka(p, przysiad, "Right", cel=(-1.2, 0.75, -0.1), biegun=(-1, 0, -0.3), os=(-0.15, 0.6, -0.8),
          przod=(-1, 0, 0))
    skok = _poza(p, _z(B, LowerTorso={"obrot": (-8, -4, 0), "przes": (0, 1.2, 0.45)}, UpperTorso=(-12, -4, 0),
                       Head=(-2, 4, -14),
                       LeftUpperLeg=(-56, 0, 8), LeftLowerLeg=(96, 0, 0), RightUpperLeg=(-30, 0, -8),
                       RightLowerLeg=(80, 0, 0),
                       LeftUpperArm=(-50, 0, 60), LeftLowerArm=(-30, 0, 0)), ziemia=False)
    _reka(p, skok, "Right", cel=(-1.25, 0.75, -0.1), biegun=(-1, 0, -0.3), os=(-0.1, 0.45, -1), przod=(-1, 0, 0))
    szczyt = _poza(p, _z(B, LowerTorso={"obrot": (4, 0, 0), "przes": (0, 0.9, 0.75)}, UpperTorso=(8, 0, 0),
                         Head=(-12, 0, -14),
                         LeftUpperLeg=(-40, 0, 8), LeftLowerLeg=(50, 0, 0), RightUpperLeg=(-10, 0, -8),
                         RightLowerLeg=(40, 0, 0),
                         LeftUpperArm=(-40, 0, 60), LeftLowerArm=(-30, 0, 0)), ziemia=False)
    _reka(p, szczyt, "Right", cel=(-1.15, 0.85, 0.35), biegun=(-1, 0, -0.3), os=(-0.1, 1, 0.25), przod=(-1, 0, 0))

    def cios(glebiej):
        pz = _poza(p, _z(B, LowerTorso={"obrot": (20 + glebiej, 0, 0), "przes": (0, 0, 0.9)},
                         UpperTorso=(24 + glebiej, 0, 0), Head=(-30, 0, 0),
                         LeftUpperLeg=(-64, 0, 8), LeftLowerLeg=(74, 0, 0), RightUpperLeg=(22, 0, -8),
                         RightLowerLeg=(44, 0, 0),
                         LeftUpperArm=(-20, 0, 58), LeftLowerArm=(-30, 0, 0)))
        return _reka(p, pz, "Right", cel=(0.1, -0.95 - glebiej * 0.02, 1.3), biegun=(-1, -0.2, 0),
                     os=(0.08, -0.4, 1), przod=(-1, 0, 0), swiat=True)
    uderz, trzyma = cios(0), cios(2)
    # wstaje: miecz unosi się z ziemi sztychem w przód i w górę (nie przechodzi pod ziemią)
    wstaje = _poza(p, _z(B, LowerTorso={"obrot": (6, 0, 0), "przes": (0, 0, 0.4)}, UpperTorso=(8, 0, 0),
                         Head=(-8, 0, 0),
                         LeftUpperLeg=(-30, 0, 6), LeftLowerLeg=(36, 0, 0), RightUpperLeg=(10, 0, -6),
                         RightLowerLeg=(24, 0, 0),
                         LeftUpperArm=(-10, 0, 20), LeftLowerArm=(-20, 0, 0)))
    _reka(p, wstaje, "Right", cel=(-0.15, -0.7, 0.95), biegun=(-1, -0.4, 0), os=(0, 0.55, 1), przod=(-1, 0, 0),
          swiat=True)
    _sekwencja(k, (0, 8, 16, 19, 23, 30, 40, dl), (B, przysiad, skok, szczyt, uderz, trzyma, wstaje, B),
               wyg={2: "liniowo", 3: "liniowo"})
    return k


def kamienna_skora(p, dl=44):
    """Kamienna skóra — wzmocnienie na siebie (1,47 s): rycerz unosi prawe kolano (kl. 9) i tupie w szerokim
    rozkroku (kl. 14 — chwila efektu), tarcza wysunięta przed siebie, miecz nad tarczą sztychem do przodu (poza
    obronna jak w szyku); poza trzymana z napięciem (lekkie drżenie tułowia) do kl. 34, potem powrót do spoczynku."""
    k = p.klip("kamienna_skora", dl, petla=False)
    B = _baza(p)

    def oslona(pz, nizej=0.0):
        _tarcza_przed(p, pz, cel=(0.1, -0.45 - nizej, 1.36))
        return _reka(p, pz, "Right", cel=(-0.6, 0.75 - nizej, 0.3), biegun=(-1, -0.4, -0.2), os=(0.12, 0.2, 1),
                     przod=(-1, 0, 0), swiat_broni=True)
    podnosi = oslona(_poza(p, _z(B, LowerTorso={"obrot": (2, -10, 0)}, UpperTorso=(4, -8, 0), Head=(-4, 8, 4),
                                 LeftUpperLeg=(-8, 0, 8), LeftLowerLeg=(14, 0, 0), RightUpperLeg=(-66, 0, -10),
                                 RightLowerLeg=(70, 0, 0))))

    def stoi(tulow, glowa):
        return oslona(_poza(p, _z(B, LowerTorso={"obrot": (6, -10, 0)}, UpperTorso=tulow, Head=glowa,
                                  LeftUpperLeg=(-22, 0, 16), LeftLowerLeg=(30, 0, 0), RightUpperLeg=(-4, 0, -18),
                                  RightLowerLeg=(30, 0, 0))), 0.08)
    tup = stoi((10, -8, 0), (-10, 8, 4))

    def bok(tulow):
        pz = _poza(p, _z(B, LowerTorso={"obrot": (1, -5, 0)}, UpperTorso=tulow, Head=(-2, 2, 4),
                         LeftUpperArm=(-30, 0, 14), LeftLowerArm=(-40, 0, 0)))
        return _miecz_gotow(p, pz, cel=(-0.7, 0.0, 0.6), os=(-0.45, 0.9, 0.2))
    _sekwencja(k, (0, 4, 9, 14, 18, 22, 26, 30, 34, 39, dl),
               (B, bok((2, -4, 0)), podnosi, tup, stoi((8, -8, 0), (-8, 8, 4)), stoi((11, -8, 1), (-12, 6, 4)),
                stoi((8, -8, -1), (-9, 9, 4)), stoi((11, -8, 1), (-12, 6, 4)), tup, bok((4, -4, 0)), B),
               wyg={2: "liniowo"})
    return k


# ---------------------------------------------------------------------------------------------------- kontrola
def kontrola(p, probki=None, margines=0.06, krok=0.25):
    """Liczbowa kontrola wszystkich klipów: czy broń (miecz, tarcza) albo przedramię/dłoń wchodzi w hełm z głową,
    tułów albo pas (skrzynka brył kości, pas bez poł tabardu) głębiej niż `margines`, oraz najniższy punkt ciała
    i broni w każdej klatce. probki = {klip: {kość: {"obrot": [...], "przes": [...]}}} (np. z Blendera), inaczej
    wartości z kluczy modułu (klipy walki mają klucz w każdej klatce, więc to dokładnie to, co gra Blender).
    Zwraca {klip: {"klatki": n, "przenikanie": [(klatka, co, w co, ile punktów)], "najnizej": (y, klatka),
    "pola": [(klatka, co, ile)], "naramiennik": [(klatka, ile)]}}."""
    br = _bryly(p)
    pudla = {}
    for b in br:
        # akcesoria na hełmie / tułowiu / pasie (włosy gołego Rycerza) liczą się do skrzynki swojej kości
        if b["kosc"] in CIALO and not (b["zrodlo"] == "cialo" and b["n"].startswith("Pola")):
            mn, mx = pudla.setdefault(b["kosc"], ([1e9] * 3, [-1e9] * 3))
            for q in b["pkt"]:
                for i in range(3):
                    mn[i], mx[i] = min(mn[i], q[i]), max(mx[i], q[i])
    pola = [b for b in br if b["zrodlo"] == "cialo" and b["n"].startswith("Pola")]
    ruchome = []
    for b in br:
        if b["zrodlo"] != "cialo" and b["kosc"] not in CIALO:
            ruchome.append((b["zrodlo"], b["kosc"], _siatka(b, krok)))
        elif b["kosc"] in KONCZYNY:
            ruchome.append((b["kosc"], b["kosc"], _siatka(b, krok)))
    naramienniki = [(b["kosc"], b["pkt"]) for b in br if b["zrodlo"] == "cialo" and b["kosc"].endswith("UpperArm")]
    wynik = {}
    for kl in p.klipy:
        pr = (probki or {}).get(kl.nazwa)
        w = {"klatki": kl.dlugosc + 1, "przenikanie": [], "pola": [], "naramiennik": [], "najnizej": (1e9, -1)}
        for f in range(kl.dlugosc + 1):
            poza = {}
            for n in p.kosci:
                for kanal in ("obrot", "przes"):
                    if pr is not None:
                        v = pr.get(n, {}).get(kanal)
                        v = v[min(f, len(v) - 1)] if v else None
                    else:
                        v = kl.wartosc(n, kanal, f)
                    if v is not None:
                        poza.setdefault(n, {})[kanal] = tuple(v)
            W = _fk(p, poza)
            odw = {n: (_tr(W[n][0]), W[n][1]) for n in CIALO}

            def lok(n, q):
                Rt, t = odw[n]
                return razy_wektor(Rt, (q[0] - t[0], q[1] - t[1], q[2] - t[2]))
            licz, licz_pola = {}, {}
            for co, kosc, pkt in ruchome:
                R, t = W[kosc]
                for q in pkt:
                    s = razy_wektor(R, q)
                    s = (s[0] + t[0], s[1] + t[1], s[2] + t[2])
                    if s[1] < w["najnizej"][0]:
                        w["najnizej"] = (round(s[1], 3), f)
                    for n, (mn, mx) in pudla.items():
                        g = _glebokosc(lok(n, s), mn, mx)
                        if g > margines:
                            ile, gm = licz.get((co, n), (0, 0.0))
                            licz[(co, n)] = (ile + 1, max(gm, g))
                    if co in ("rycerz_miecz", "rycerz_tarcza"):
                        l = lok("LowerTorso", s)
                        for b in pola:
                            d = (l[0] - b["c"][0], l[1] - b["c"][1], l[2] - b["c"][2])
                            d = razy_wektor(_tr(b["R"]), d)
                            if all(abs(d[i]) < b["h"][i] - margines for i in range(3)):
                                licz_pola[co] = licz_pola.get(co, 0) + 1
                                break
            for (co, n), (ile, gm) in sorted(licz.items()):
                w["przenikanie"].append((f, co, n, ile, round(gm, 3)))
            for co, ile in sorted(licz_pola.items()):
                w["pola"].append((f, co, ile))
            ile, gm, strona = 0, 0.0, ""
            for kosc, pkt in naramienniki:
                R, t = W[kosc]
                for q in pkt:
                    s = razy_wektor(R, q)
                    g = _glebokosc(lok("Head", (s[0] + t[0], s[1] + t[1], s[2] + t[2])), *pudla["Head"])
                    if g > margines:
                        ile += 1
                        if g > gm:
                            gm, strona = g, kosc
            if ile:
                w["naramiennik"].append((f, ile, round(gm, 3), strona))
            for b in br:                                   # najniższy punkt całego ciała (stopy, leżenie)
                if b["zrodlo"] == "cialo":
                    R, t = W[b["kosc"]]
                    for q in b["pkt"]:
                        y = R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1]
                        if y < w["najnizej"][0]:
                            w["najnizej"] = (round(y, 3), f)
        wynik[kl.nazwa] = w
    return wynik


def _glebokosc(l, mn, mx):
    """Jak głęboko punkt l siedzi w skrzynce (mn, mx): odległość do najbliższej ściany; ≤ 0 = na zewnątrz."""
    return min(min(l[i] - mn[i], mx[i] - l[i]) for i in range(3))


def _wypisz_kontrole(wynik):
    zle = 0
    for nazwa, w in wynik.items():
        klatki = sorted({f for f, *_ in w["przenikanie"]})
        zle += len(klatki)
        print("%-15s %3d kl.  przenikanie broni/dłoni w hełm, tułów, pas: %s" % (
            nazwa, w["klatki"], "BRAK" if not klatki else "%d kl., najgłębiej %.2f studa, np. %s" % (
                len(klatki), max(x[4] for x in w["przenikanie"]), w["przenikanie"][:3])))
        print("%-15s          najniższy punkt (ciało i broń): y = %.3f w kl. %d" % ("", w["najnizej"][0],
                                                                                  w["najnizej"][1]))
        if w["pola"]:
            print("%-15s          broń przez poły tabardu: %d kl., np. %s" % ("", len({f for f, *_ in w["pola"]}),
                                                                             w["pola"][:3]))
        if w["naramiennik"]:
            print("%-15s          naramiennik/rękaw w hełmie albo głowie (bryła ramienia, nie broń): %d kl., "
                  "najgłębiej %.2f studa"
                  % ("", len(w["naramiennik"]), max(x[2] for x in w["naramiennik"])))
    return zle


if __name__ == "__main__":
    if "--kontrola" in sys.argv:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        stroje = [sys.argv[sys.argv.index("--stroj") + 1]] if "--stroj" in sys.argv else list(STROJE)
        zle = 0
        for s in stroje:
            print("=== strój „%s” (%s): %s" % (s, NAZWY_STROJOW[s], ", ".join(STROJE[s]) or "bez przedmiotów"))
            zle += _wypisz_kontrole(kontrola(stroj(s)))
        sys.exit(1 if zle else 0)
