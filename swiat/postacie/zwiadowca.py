# -*- coding: utf-8 -*-
"""ZWIADOWCA — druga klasa gracza (obok Wojownika-Rycerza i Maga): zwinny leśny zwiadowca z łukiem i sztyletem.

Opis klasy (tools/walka/dane_walki.json, id „zwiadowca”): styl „unik i krytyk”, umiejętności: uderzenie z góry,
zatruta strzała, skupienie. Wygląd to własny projekt (propozycja, nie kanon).

CIAŁO BAZOWE + STRÓJ Z PRZEDMIOTÓW (D-071, kontrakt swiat/postacie/EKWIPUNEK.md):
  cialo()      goły Zwiadowca („zwiadowca_cialo”): te same klocki, kości, zaczepy i klipy; twarz Zwiadowcy z piegami
               i grzywką (trzy kosmyki są częścią twarzy), rozczochrana ciemnobrązowa czupryna (osobne akcesorium
               zwiadowca_wlosy na HairAttachment, kaptur ją chowa), lniana koszula z podwiniętymi rękawami,
               sznurowanym dekoltem i wyszytym listkiem, zielone krótkie spodenki z troczkami, bose stopy;
  przedmioty() kaptur z krótką peleryną (Helmet), skórzany kirys z tuniką, chustą, naramiennikami, karwaszami
               i połami tuniki (Chest), spodnie (część kirysu), pas z sakwą (Belt), rękawice bez palców (Gloves),
               buty z wywiniętą cholewą (Boots), sztylet (Weapon), łuk z kołczanem na plecach (OffHand: łuk w lewej
               dłoni + kołczan z pasem na skos na tułowiu) — segmenty kostne w układzie środka klocka kości albo
               akcesorium na zaczepie (broń);
  ubierz()     zakłada przedmioty na ciało (powłoka zastępuje gołe bryły kości, kaptur chowa włosy);
  zbuduj()     jak dotąd: [Zwiadowca w pełnym stroju kanonicznym (KANON), łuk, sztylet];
  warianty()   stroje z STROJE, segmenty i ikony całych przedmiotów dla przebuduj.py (wynik/zwiadowca/ekwipunek/).
Klipy liczą się RAZ na postaci odniesienia (ODNIESIENIE_KLIPOW = pełny strój = dawny model: stopy płasko na ziemi,
nic pod ziemią, leżenie na brzuchu) i są kopiowane bez zmian na ciało i każdy strój — ten sam ruch niezależnie
od ubrania.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zwiadowca.py --wyj <folder> --klip unik
    python -B swiat/postacie/zwiadowca.py --kontrola             # kontrola przenikania we wszystkich strojach (bez Blendera)
    python -B swiat/postacie/zwiadowca.py --kontrola --stroj golas upadek    # jeden strój, wybrane klipy

Bryła: szkielet R15 w tych samych wymiarach klocków co Rycerz (ciało „czlowiek”: te same zaczepy, kości i klocki,
więc przedmioty obu bohaterów pasują na oba ciała), ok. 5,8 studa z kapturem.
Sylwetka do rozpoznania z daleka: spiczasty kaptur z końcem odchylonym do tyłu, krótka peleryna z brzegiem ciętym
w liście, kołczan na plecach z pomarańczowymi lotkami nad prawym barkiem, wysoki łuk w lewej dłoni, sztylet w prawej.
Lekki skórzany pancerz z pasem kołczanu na skos, tunika (jej poły siedzą na udach, więc nie przebijają nóg w biegu),
wysokie buty z wywiniętą cholewą. Twarz pogodna i bystra: duże oczy, jedna brew uniesiona, uśmiech z kącikiem
w górę, piegi.

Paleta (6 rodzin + akcent): zieleń lasu (kaptur, peleryna, tunika — dwa odcienie), skóra pancerza (trzy brązy),
drewno łuku, karnacja, tusz (oczy, usta), AKCENT: jasnopomarańczowa chusta i lotki strzał; goły Zwiadowca: len
koszuli (jak u Rycerza), spodenki w zieleni spodni (lisc_ciemny), ciemnobrązowe włosy.

Broń: dwa osobne przedmioty, jak miecz Rycerza (w FBX postaci ich nie ma, w renderach i filmach są w dłoniach):
  zwiadowca_luk     — na LeftGripAttachment (uchwyt w (0,0,0), ramiona łuku wzdłuż ±Y, brzuch łuku +Z, cięciwa −Z),
  zwiadowca_sztylet — na RightGripAttachment (rękojeść w (0,0,0), ostrze w +Y, płaz do przodu +Z).
Przedmiot „Łuk z kołczanem” (zwiadowca_luk) ma dwa segmenty: łuk na LeftGripAttachment i kołczan z pasem na skos
wtapiany w tułów (wierzchnia warstwa) — bez łuku nie ma też kołczanu.

Klipy (30 kl./s; postać patrzy w +Z i w tę stronę atakuje):
  idle (pętla), ruch (lekki bieg, pętla), atak (pchnięcie sztyletem z wypadem), umiejetnosc (zatruta strzała:
  lewym barkiem do celu, łuk wyciągnięty na wysokości barku, naciąg z łokciem w tył, wypuszczenie z odrzutem),
  uderzenie_z_gory (drugi klip umiejętności: wyskok i cios sztyletem z góry), trafienie (szarpnięcie w tył), unik
  (znak klasy: boczne salto w lewo i powrót), upadek (pada na kolana i twarzą w dół, kończy się leżeniem), wiwat
  (pętla: łuk w górę, podskoki).
Klipy są zapisane jako pozy kluczowe (funkcja _sekwencja zamienia je na klucz w każdej klatce): stopy stoją płasko
na ziemi, w powietrzu nic nie schodzi pod ziemię. Zmiany rób w pozach kluczowych w tym pliku, nie w Blenderze.
Bez łuku lewa ręka robi ten sam ruch pustą dłonią, bez sztyletu prawa — pustą pięścią.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie.biblioteka.postac import (I3, R15_KOSCI, Akcesorium, Postac, katy_z_macierzy, macierz_obrotu,
                                              mnoz, razy_wektor)
try:                                    # wspólny kod ekwipunku (EKWIPUNEK.md pkt 4): docelowo ekwipunek.py,
    from swiat.postacie.ekwipunek import Przedmiot, kopiuj_klipy, ubierz, zaczep_ekwipunku
except ModuleNotFoundError as e:        # na razie w sekcji „ekwipunek: wspólne” w rycerz.py
    if e.name != "swiat.postacie.ekwipunek":
        raise
    from swiat.postacie.rycerz import Przedmiot, kopiuj_klipy, ubierz, zaczep_ekwipunku

ID = "zwiadowca"
NAZWA = "Zwiadowca"

PALETA = {
    "lisc": "3F9B4A", "lisc_ciemny": "26633A",                       # kaptur, peleryna, tunika / podszewka, spodnie
    "skorzany": "8A5530", "skorzany_ciemny": "553319", "skorzany_jasny": "C49A62",
    "wlosy": "4A2C17", "piegi": "C7835A",
    "drewno": "A8692E",
    "akcent": "FF9F1C",                                               # chusta, lotki strzał
    "stal": "B9C3D0", "stal_cien": "7F8A9A",
    # goły Zwiadowca (ciało bazowe): len koszuli, cień lnu, ściągacz spodenek, ciemne pasma włosów
    "len": "EDE3CC", "len_cien": "D3C4A2", "lisc_cien": "1C4A2B", "wlosy_ciemne": "34200F",
}

# te same klocki co Rycerz (te same zaczepy ekwipunku, ten sam wzrost ciała)
WYMIARY = {"Head": (1.6, 1.5, 1.45),
           "UpperTorso": (2.2, 1.5, 1.2), "LowerTorso": (2.2, 0.4, 1.2),
           "UpperArm": (0.95, 0.95, 0.95), "LowerArm": (0.95, 0.75, 0.95), "Hand": (0.9, 0.35, 0.9),
           "UpperLeg": (1.05, 0.8, 1.05), "LowerLeg": (1.05, 0.75, 1.05), "Foot": (1.05, 0.35, 1.35)}


# --------------------------------------------------------------------------- broń (osobne przedmioty)
def luk():
    """Łuk: uchwyt w (0, 0, 0) (schowany w pięści), ramiona wzdłuż ±Y wygięte ku łucznikowi (−Z), cięciwa z tyłu."""
    a = Akcesorium("zwiadowca_luk", "Łuk Zwiadowcy", zaczep="LeftGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(0, -60, 0))
    a.blok("Majdan", (0, 0, 0.0), (0.24, 1.0, 0.3), "skorzany_ciemny", "matowy", faza=0.04)
    for y in (-0.28, 0.0, 0.28):
        a.blok("Owijka", (0, y, 0.0), (0.28, 0.07, 0.34), "skorzany_jasny", "matowy", faza=0.0)
    # ramię łuku: trzy odcinki (długość, przyrost odgięcia ku cięciwie −Z w stopniach, szerokość, grubość);
    # ostatni odcinek odgięty z powrotem do przodu (refleks) — kształt jak nawias „(”
    odcinki = ((0.55, 16, 0.2, 0.26), (0.45, 24, 0.17, 0.22), (0.25, -50, 0.14, 0.17))
    koniec = (0.0, 0.0)
    for zn, s in ((1, "gora"), (-1, "dol")):
        y, zz, kat = 0.48, 0.0, 0.0
        for i, (dl, dk, sz, gr) in enumerate(odcinki):
            kat += dk
            r = math.radians(kat)
            sy, sz_ = math.cos(r) * dl, -math.sin(r) * dl
            a.blok("Ramie %d %s" % (i, s), (0, zn * (y + sy / 2), zz + sz_ / 2), (sz, dl + 0.06, gr), "drewno",
                   "matowy", rot=(-zn * kat, 0, 0), faza=0.04)
            y, zz = y + sy, zz + sz_
        a.blok("Okucie " + s, (0, zn * y, zz), (0.17, 0.12, 0.2), "skorzany_jasny", "matowy", faza=0.02)
        a.blok("Pierscien " + s, (0, zn * 0.53, 0.0), (0.27, 0.08, 0.32), "skorzany_ciemny", "matowy", faza=0.0)
        koniec = (y, zz)
    # cięciwa: prosta, między końcami ramion (łuk w spoczynku; naciąg pokazuje tylko ręka — patrz SLABOSCI)
    a.blok("Cieciwa", (0, 0, koniec[1]), (0.04, 2 * koniec[0], 0.04), "skorzany_jasny", "matowy", faza=0.0)
    return a


def sztylet():
    """Długi sztylet w kształcie liścia: rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z)."""
    a = Akcesorium("zwiadowca_sztylet", "Sztylet Zwiadowcy", zaczep="RightGripAttachment", typ="Bron", paleta=PALETA,
                   ikona_obrot=(0, 0, -45))
    a.blok("Rekojesc", (0, 0, 0), (0.2, 1.0, 0.2), "skorzany_ciemny", "matowy", faza=0.04)
    for y in (-0.25, 0.05, 0.35):
        a.blok("Owijka", (0, y, 0), (0.24, 0.07, 0.24), "skorzany", "matowy", faza=0.0)
    a.blok("Glowica", (0, -0.57, 0), (0.3, 0.2, 0.3), "skorzany_jasny", "matowy", faza=0.06)
    a.blok("Glowica kamien", (0, -0.57, 0.16), (0.12, 0.1, 0.04), "akcent", "polysk", faza=0.0)
    a.blok("Jelec", (0, 0.56, 0), (0.62, 0.14, 0.24), "stal_cien", "metal", faza=0.04)
    for zn in (1, -1):
        a.blok("Jelec koniec", (zn * 0.33, 0.62, 0), (0.12, 0.24, 0.24), "stal_cien", "metal", faza=0.03)
    # ostrze-liść: szerokie w połowie, zwężone przy jelcu i ku sztychowi
    a.ostroslup("Ostrze dol", (0, 0.86, 0), (0.42, 0.46, 0.1), "stal", "metal", rot=(180, 0, 0), gora=(0.24, 0.1))
    a.ostroslup("Ostrze gora", (0, 1.43, 0), (0.42, 0.68, 0.1), "stal", "metal", gora=(0.0, 0.06))
    a.blok("Zbrocze", (0, 1.05, 0), (0.07, 0.62, 0.12), "stal_cien", "metal", faza=0.0)
    return a


# --------------------------------------------------------------------------- ciało bazowe („goły” Zwiadowca)
CIALO_TYP = "czlowiek"
KLASY = ("zwiadowca",)
# przedmioty pełnego stroju kanonicznego (zbuduj()) = dawny model; łuk przed sztyletem (kolejność założonych jak dawniej)
KANON = ("zwiadowca_kaptur", "zwiadowca_kurtka", "zwiadowca_spodnie", "zwiadowca_pas", "zwiadowca_rekawice",
         "zwiadowca_buty", "zwiadowca_luk", "zwiadowca_sztylet")
ODNIESIENIE_KLIPOW = KANON                     # geometria, na której liczą się klipy (= dawny model z łukiem i sztyletem)
# stroje do plansz i kontroli (przebuduj.py -> wynik/zwiadowca/ekwipunek/); nazwa stroju nie może dać id przedmiotu
STROJE = {"golas": (),
          "pelny": KANON,
          "bez_kaptura": ("zwiadowca_kurtka", "zwiadowca_spodnie", "zwiadowca_pas", "zwiadowca_rekawice",
                          "zwiadowca_buty", "zwiadowca_luk", "zwiadowca_sztylet"),
          "lekki": ("zwiadowca_kurtka", "zwiadowca_spodnie", "zwiadowca_buty", "zwiadowca_luk"),
          "kaptur_i_sztylet": ("zwiadowca_kaptur", "zwiadowca_sztylet")}
NAZWY_STROJOW = {"golas": "goły (ciało bazowe)", "pelny": "pełny strój", "bez_kaptura": "bez kaptura i peleryny",
                 "lekki": "kirys, buty i łuk", "kaptur_i_sztylet": "sam kaptur i sztylet"}
PLANSZA_ZBIORCZA = ("golas", "pelny", "lekki", "kaptur_i_sztylet")      # goły | pełny | dwa częściowe
# filmy w stroju (strój, klip): dowód, że przedmioty idą za kośćmi, a goły Zwiadowca rusza się dobrze bez stroju
FILMY_EKWIPUNKU = (("golas", "idle"), ("golas", "atak"), ("golas", "upadek"), ("lekki", "umiejetnosc"),
                   ("kaptur_i_sztylet", "unik"), ("bez_kaptura", "uderzenie_z_gory"))


def _postac(id, nazwa):
    """Postać R15 o klockach Zwiadowcy (kości, stawy, 18 zaczepów R15), jeszcze bez brył."""
    return Postac(id, nazwa, typ="r15", faza=0.05, paleta=PALETA, wymiary=WYMIARY)


def _twarz(p):
    """Klocek głowy („Twarz”) z oczami, piegami, brwiami, uśmiechem i grzywką spod kaptura (zostaje w każdym
    stroju; bryły jak w dawnym modelu)."""
    with p.na("Head", od="srodek"):
        w, h, d = p.wymiary("Head")
        z = d / 2
        p.blok("Twarz", (0, 0, 0), (w, h, d), "skora")
        # oczy: duże, czarne, z dwoma błyskami
        for zn, s in ((1, "L"), (-1, "P")):
            x = zn * 0.3
            p.blok("Oko " + s, (x, 0.0, z + 0.02), (0.26, 0.4, 0.06), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (x - 0.05, 0.1, z + 0.055), (0.1, 0.12, 0.03), "bialy", faza=0.0)
            p.blok("Blysk maly " + s, (x + 0.06, -0.1, z + 0.055), (0.05, 0.05, 0.03), "bialy", faza=0.0)
            p.blok("Rumieniec " + s, (zn * 0.5, -0.22, z + 0.01), (0.16, 0.08, 0.03), "rumieniec", "matowy", faza=0.0)
            for i, (dx, dy) in enumerate(((-0.06, 0.02), (0.06, -0.03))):
                p.blok("Pieg %s%d" % (s, i), (zn * (0.4 + dx), -0.1 + dy, z + 0.012), (0.06, 0.06, 0.03),
                       "piegi", "matowy", faza=0.0)
        # brwi: lewa (od postaci) wyżej, uniesiona łukiem — bystra, zaczepna mina; prawa niżej, prawie prosto
        p.blok("Brew L", (0.31, 0.31, z + 0.03), (0.34, 0.09, 0.07), "wlosy", "matowy", rot=(0, 0, -10), faza=0.02)
        p.blok("Brew P", (-0.31, 0.25, z + 0.03), (0.32, 0.09, 0.07), "wlosy", "matowy", rot=(0, 0, 5), faza=0.02)
        p.blok("Nos", (0, -0.15, z + 0.05), (0.16, 0.16, 0.1), "skora_cien", "matowy", faza=0.03)
        # uśmiech: otwarty, z zębami, lewy kącik wyżej (łobuzerski)
        # jedna bryła w kształcie „D” (szeroka u góry), pas zębów, różowy język; lewy kącik uniesiony
        p.ostroslup("Usta", (0.02, -0.37, z + 0.02), (0.52, 0.2, 0.05), "tusz", rot=(0, 0, 180),
                    gora=(0.3, 0.05), faza=0.0)
        p.blok("Zeby", (0.02, -0.305, z + 0.05), (0.44, 0.06, 0.03), "bialy", faza=0.0)
        p.blok("Jezyk", (0.02, -0.43, z + 0.05), (0.18, 0.05, 0.03), "D9534A", "matowy", faza=0.0)
        p.blok("Kacik L", (0.3, -0.29, z + 0.02), (0.07, 0.13, 0.05), "tusz", rot=(0, 0, 35), faza=0.0)
        # grzywka spod kaptura: trzy kanciaste kosmyki (część twarzy — bez kaptura wiszą z czupryny)
        for i, (x, kat, dl) in enumerate(((-0.42, -14, 0.24), (-0.12, 8, 0.3), (0.2, -6, 0.22))):
            p.blok("Kosmyk %d" % i, (x, 0.58, z + 0.04), (0.32, dl, 0.08), "wlosy", "matowy", rot=(0, 0, kat),
                   faza=0.02)


def wlosy():
    """Rozczochrana ciemnobrązowa czupryna gołego Zwiadowcy (akcesorium Hair na HairAttachment = środek górnej
    ściany głowy): czapa na czubku, tył do karku zakończony trzema szpicami, boki nad uszami, opaska grzywki nad
    czołem (spod niej wiszą trzy kosmyki twarzy), trzy kosmyki sterczące na czubku do tyłu i jeden nad lewym uchem.
    Kaptur ją chowa (znacznik „Wlosy”)."""
    a = Akcesorium("zwiadowca_wlosy", "Włosy Zwiadowcy", zaczep="HairAttachment", typ="Hair", paleta=PALETA,
                   przymierz=False)
    a.znacznik = "Wlosy"
    w, h, d = WYMIARY["Head"]
    x, z = w / 2, d / 2                                       # boki i przód głowy względem zaczepu
    a.blok("Czupryna", (0, 0.09, -0.03), (w + 0.1, 0.22, d + 0.1), "wlosy", "matowy", faza=0.06)
    a.blok("Tyl", (0, -0.44, -z - 0.04), (w + 0.1, 0.92, 0.1), "wlosy", "matowy", faza=0.04)
    for i, xk in enumerate((-0.5, 0.0, 0.5)):                 # kark: trzy szpice w dół
        a.ostroslup("Kark %d" % i, (xk, -0.98, -z - 0.04), (0.5, 0.16, 0.1), "wlosy", "matowy", rot=(180, 0, 0),
                    gora=(0.0, 0.08), faza=0.0)
    for zn, s in ((1, "L"), (-1, "P")):
        a.blok("Bok " + s, (zn * (x + 0.025), -0.26, -0.16), (0.06, 0.56, d - 0.42), "wlosy", "matowy", faza=0.02)
        a.blok("Bok pasmo " + s, (zn * (x + 0.035), -0.2, -0.36), (0.04, 0.4, 0.12), "wlosy_ciemne", "matowy",
               faza=0.0)
    a.blok("Grzywka", (0, -0.06, z + 0.02), (w + 0.06, 0.14, 0.06), "wlosy", "matowy", faza=0.02)
    # sterczące kosmyki: ostrosłupy szpicem w górę i do tyłu (zwiadowca czesze się wiatrem)
    for i, (xk, zk, kat, kz, wys) in enumerate(((-0.42, 0.25, -34, 10, 0.3), (0.05, 0.05, -42, -6, 0.36),
                                                (0.45, -0.2, -30, -14, 0.28))):
        a.ostroslup("Czub %d" % i, (xk, 0.19 + wys / 2 - 0.04, zk), (0.4, wys, 0.36),
                    "wlosy_ciemne" if i == 1 else "wlosy", "matowy", rot=(kat, 0, kz), gora=(0.0, 0.0), faza=0.0)
    a.ostroslup("Kosmyk bok", (x + 0.1, -0.12, 0.05), (0.18, 0.26, 0.2), "wlosy", "matowy", rot=(0, 0, -70),
                gora=(0.0, 0.04), faza=0.0)
    return a


def _golas(id, nazwa, zaczepy_ekwipunku=False):
    """Goły Zwiadowca bez klipów: twarz z grzywką, lniana koszula z podwiniętymi rękawami, zielone krótkie spodenki,
    bose stopy, włosy. Klocki pełnego rozmiaru, ubranie wystaje 0,02–0,03 studa, spodenki 0,01 (bez wcięć i szpar)."""
    p = _postac(id, nazwa)
    p.typ_ciala = CIALO_TYP
    _twarz(p)
    p.klocek("UpperTorso", "len")
    p.klocek("LowerTorso", "lisc_ciemny")
    for strona in ("Left", "Right"):
        for kosc in ("UpperArm", "LowerArm", "Hand", "UpperLeg", "LowerLeg", "Foot"):
            p.klocek(strona + kosc, "skora")
    with p.na("UpperTorso", od="srodek"):                         # koszula: sznurowany dekolt, listek, rąbek
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.ostroslup("Dekolt", (0, h / 2 - 0.2, z + 0.015), (0.36, 0.4, 0.03), "skora", "matowy",
                    rot=(0, 0, 180), gora=(0.06, 0.03), faza=0.0)
        for i, y in enumerate((h / 2 - 0.12, h / 2 - 0.26)):
            for zn in (1, -1):
                p.blok("Sznurowanie %d" % i, (0, y, z + 0.03), (0.3, 0.035, 0.03), "skorzany", "matowy",
                       rot=(0, 0, zn * 24), faza=0.0)
        # wyszyty listek na lewej piersi (znak zwiadowcy, bez napisów)
        p.blok("Listek", (0.58, 0.12, z + 0.015), (0.2, 0.2, 0.03), "lisc", "matowy", rot=(0, 0, 45), faza=0.0)
        p.blok("Listek zylka", (0.58, 0.1, z + 0.03), (0.03, 0.22, 0.03), "lisc_ciemny", "matowy", rot=(0, 0, 10),
               faza=0.0)
        p.blok("Rabek koszuli", (0, -h / 2 + 0.07, 0), (w + 0.04, 0.12, d + 0.04), "len_cien", "matowy", faza=0.02)
    # spodenki wystają tylko 0,01 studa (ściągacz, nogawka): pas z sakwą i poły tuniki leżą o 0,02 nad klockiem —
    # w tej samej odległości ściany migotałyby, gdy kirys albo pas są założone bez spodni
    with p.na("LowerTorso", od="srodek"):                         # spodenki: ściągacz i troczki
        w, h, d = p.wymiary("LowerTorso")
        z = d / 2
        p.blok("Sciagacz", (0, h / 2 - 0.08, 0), (w + 0.02, 0.14, d + 0.02), "lisc_cien", "matowy", faza=0.02)
        for zn in (1, -1):
            p.blok("Troczek", (zn * 0.08, h / 2 - 0.2, z + 0.03), (0.06, 0.2, 0.03), "len", "matowy",
                   rot=(0, 0, zn * 10), faza=0.0)
    for strona in ("Left", "Right"):
        with p.na(strona + "UpperArm", od="srodek"):              # krótki rękaw z podwinięciem
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Rekaw", (0, h / 2 - 0.22, 0), (w + 0.04, 0.48, d + 0.04), "len", "matowy", faza=0.04)
            p.blok("Rekaw podwiniecie", (0, h / 2 - 0.5, 0), (w + 0.06, 0.14, d + 0.06), "len_cien", "matowy",
                   faza=0.03)
        with p.na(strona + "UpperLeg", od="srodek"):              # nogawka spodenek, rąbek nad kolanem
            w, h, d = p.wymiary(strona + "UpperLeg")
            # góra nogawki 0,02 nad klockiem (poły tuniki kończą się 0,01 nad nim — bez wspólnej ściany)
            p.blok("Nogawka", (0, h / 2 - 0.235, 0), (w + 0.02, 0.51, d + 0.02), "lisc_ciemny", "matowy", faza=0.04)
            p.blok("Nogawka rabek", (0, h / 2 - 0.5, 0), (w + 0.04, 0.08, d + 0.04), "lisc_cien", "matowy",
                   faza=0.02)
        with p.na(strona + "Foot", od="srodek"):                  # bosa stopa: zarys palców
            w, h, d = p.wymiary(strona + "Foot")
            for i in (-1, 0, 1):
                p.blok("Palec", (i * 0.3, -h / 2 + 0.075, d / 2 + 0.01), (0.035, 0.13, 0.03), "skora_cien",
                       "matowy", faza=0.0)
    for c in p.czesci:
        c["golas"] = True                                         # gołe bryły (zdejmuje je powłoka na tej kości)
    p.zaloz(wlosy())                                              # osobna siatka (w FBX ciała), kaptur ją chowa
    if zaczepy_ekwipunku:
        for kosc in R15_KOSCI:
            p.zaczep(zaczep_ekwipunku(kosc), kosc, p.srodek(kosc))
    return p


# --------------------------------------------------------------------------- przedmioty stroju
class _Przedmiot(Przedmiot):
    """Przedmiot Zwiadowcy. Różnica tylko w ikonie przedmiotu z segmentem kostnym I segmentem na zaczepie (łuk
    z kołczanem): wspólna ikona bierze same segmenty kostne, więc łuk dokładamy obok kołczanu, pionowo (cięciwą
    do kołczanu), a ikonę pokazujemy od tyłu (kołczan nosi się na plecach)."""

    IKONA_ZACZEPIONYCH = {"zwiadowca_luk": ((1.3, 3.05, -0.8), (0, 90, 0), (0, 213, 0))}   # (pos, obrot, ikona_obrot)

    def ikona(self):
        kostne = [s for s in self.segmenty if s["kosc"]]
        zacz = [s for s in self.segmenty if s["kosc"] is None]
        if not (kostne and zacz and self.id in self.IKONA_ZACZEPIONYCH):
            return Przedmiot.ikona(self)
        a = Przedmiot.ikona(self)                                 # segmenty kostne w pozie spoczynku
        pos, obrot, io = self.IKONA_ZACZEPIONYCH[self.id]
        R = macierz_obrotu(*obrot)
        for s in zacz:
            a.czesci.extend(Akcesorium._czesc_w(c, R, pos) for c in s["akc"].czesci)
        a.ikona_obrot = tuple(float(v) for v in io)
        return a


def przedmioty():
    """Wszystkie przedmioty Zwiadowcy — rozbiór dawnego modelu z EKWIPUNEK.md pkt 3. Bryły są te same co w dawnym
    zbuduj() (te same liczby), tylko pogrupowane w segmenty po kościach (układ segmentu = środek klocka kości,
    jak dawne `with p.na(kosc, od="srodek")`)."""
    m = _postac(ID + "_miara", NAZWA)
    W = m.wymiary

    def nowy(id, nazwa, slot, kategoria, **k):
        return _Przedmiot(id, nazwa, slot, kategoria, m, cialo=CIALO_TYP, klasy=KLASY, zestaw=ID, paleta=PALETA, **k)

    # --- kaptur z krótką peleryną (Helmet): kaptur na głowie (nakładka, chowa włosy, grzywka twarzy zostaje)
    #     i peleryna z kołnierzem kaptura na tułowiu (wierzchnia)
    kap = nowy("zwiadowca_kaptur", "Kaptur z peleryną", "Helmet", "Armor", ukrywa=("Wlosy",))
    a = kap.segment("Head")
    w, h, d = W("Head")
    z = d / 2
    # kaptur: płaszcz wokół głowy (boki, tył, wierzch), ciemniejsza podszewka wokół twarzy, spiczasty koniec
    kd = d + 0.26                                   # głębokość kaptura
    kz = -0.08                                      # środek kaptura (przód 0,05 przed twarzą)
    kw = w + 0.24                                   # szerokość kaptura
    for zn, s in ((1, "L"), (-1, "P")):
        a.blok("Kaptur bok " + s, (zn * (w / 2 + 0.06), -0.02, kz), (0.12, h + 0.02, kd), "lisc", "matowy",
               faza=0.1)
        a.blok("Podszewka " + s, (zn * (w / 2 - 0.01), -0.08, z + 0.035), (0.1, h - 0.2, 0.08), "lisc_ciemny",
               "matowy", faza=0.02)
    a.blok("Kaptur tyl", (0, -0.02, kz - kd / 2 + 0.06), (kw, h + 0.02, 0.12), "lisc", "matowy", faza=0.1)
    a.blok("Kaptur tyl szew", (0, 0.0, kz - kd / 2 - 0.015), (0.1, h - 0.1, 0.04), "lisc_ciemny", "matowy",
           faza=0.0)
    # czubek: ścięty ostrosłup zwężający się ku górze i cofnięty do tyłu, z niego wyrasta długi szpic
    a.ostroslup("Kaptur czubek", (0, h / 2 + 0.17, kz - 0.06), (kw, 0.38, kd + 0.1), "lisc", "matowy",
                gora=(kw * 0.5, kd * 0.5), przes_gory=(0.0, -0.24))
    a.blok("Podszewka gora", (0, h / 2 - 0.06, z + 0.05), (w + 0.12, 0.2, 0.12), "lisc_ciemny", "matowy",
           faza=0.03)
    a.blok("Daszek", (0, h / 2 + 0.06, z + 0.06), (kw + 0.02, 0.16, 0.14), "lisc", "matowy", faza=0.05)
    # szpic daszka nad czołem (kaptur od przodu czyta się jak kaptur, a nie hełm)
    a.blok("Daszek szpic", (0, h / 2 - 0.02, z + 0.1), (0.34, 0.34, 0.08), "lisc", "matowy", rot=(0, 0, 45),
           faza=0.03)
    # spiczasty koniec kaptura: sterczy do tyłu, lekko w górę (znak sylwetki z boku i w kadrze 3/4); głowa
    # z kapturem mieści się w 2 studach wysokości (limit części ciała awatara)
    with a.uklad(pos=(0, h / 2 + 0.14, kz - 0.46), obrot=(-76, 0, 0)):
        a.ostroslup("Kaptur szpic", (0, 0.3, 0), (0.84, 0.64, 0.6), "lisc", "matowy", gora=(0.5, 0.36))
        with a.uklad(pos=(0, 0.6, -0.02), obrot=(4, 0, 0)):
            a.ostroslup("Kaptur szpic koniec", (0, 0.32, 0), (0.52, 0.66, 0.38), "lisc", "matowy",
                        gora=(0.0, 0.0), przes_gory=(0.0, -0.06))
    a = kap.segment("UpperTorso")
    w, h, d = W("UpperTorso")
    z = d / 2
    # kołnierz kaptura: opada z karku na barki (kaptur „siedzi” na pelerynie, a nie na szyi jak hełm)
    a.ostroslup("Kaptur kolnierz", (0, h / 2 + 0.1, -0.04), (1.98, 0.3, 1.34), "lisc", "matowy",
                gora=(1.62, 1.16))
    # krótka peleryna: na barkach, z tyłu do pasa, brzeg cięty w trzy liście
    a.blok("Peleryna barki", (0, h / 2 - 0.04, -0.04), (w + 0.1, 0.18, d + 0.14), "lisc", "matowy", faza=0.06)
    for zn in (1, -1):
        a.blok("Peleryna przod", (zn * 0.82, h / 2 - 0.3, z + 0.07), (0.44, 0.44, 0.06), "lisc", "matowy",
               faza=0.02)
        a.blok("Peleryna przod lisc", (zn * 0.82, h / 2 - 0.52, z + 0.065), (0.31, 0.31, 0.05), "lisc", "matowy",
               rot=(0, 0, 45), faza=0.0)
    a.blok("Peleryna plecy", (0, -0.05, -z - 0.06), (w + 0.04, h - 0.1, 0.08), "lisc", "matowy", faza=0.02)
    for i, x in enumerate((-0.72, 0.0, 0.72)):
        a.blok("Peleryna lisc %d" % i, (x, -h / 2 + 0.02, -z - 0.06), (0.52, 0.52, 0.08), "lisc", "matowy",
               rot=(0, 0, 45), faza=0.0)
        a.blok("Peleryna zylka %d" % i, (x, -h / 2 + 0.06, -z - 0.11), (0.05, 0.4, 0.03), "lisc_ciemny",
               "matowy", faza=0.0)

    # --- skórzany kirys z tuniką (Chest): tułów, ramiona, przedramiona (powłoka) i poły tuniki na udach (nakładka)
    kur = nowy("zwiadowca_kurtka", "Skórzany kirys z tuniką", "Chest", "Armor")
    a = kur.segment("UpperTorso", zakrywa=True)
    w, h, d = W("UpperTorso")
    z = d / 2
    a.blok("Tunika", (0, 0, 0), (w - 0.06, h, d - 0.06), "lisc")
    # lekki skórzany pancerz: kirys z przeszyciem i sznurowaniem
    a.blok("Kirys", (0, -0.14, 0), (w + 0.02, h - 0.3, d + 0.04), "skorzany", "matowy")
    a.blok("Kirys brzeg", (0, -h / 2 + 0.2, 0), (w + 0.06, 0.1, d + 0.08), "skorzany_ciemny", "matowy", faza=0.02)
    a.blok("Przeszycie", (0.42, -0.1, z + 0.035), (0.05, 0.8, 0.04), "skorzany_ciemny", "matowy", faza=0.0)
    for i, y in enumerate((0.05, -0.2)):
        a.blok("Sznurowanie %d" % i, (0.42, y, z + 0.055), (0.22, 0.05, 0.03), "skorzany_jasny", "matowy",
               rot=(0, 0, 25), faza=0.0)
    # chusta (akcent) wokół szyi z węzłem i końcem na piersi
    a.blok("Chusta", (0, h / 2 + 0.04, 0.1), (1.3, 0.28, 1.06), "akcent", "matowy", faza=0.06)
    a.blok("Chusta wezel", (0.3, h / 2 - 0.14, z + 0.07), (0.3, 0.24, 0.14), "akcent", "matowy", faza=0.05)
    with a.uklad(pos=(0.36, h / 2 - 0.24, z + 0.07), obrot=(0, 0, 14)):
        a.ostroslup("Chusta koniec", (0, -0.24, 0), (0.28, 0.5, 0.06), "akcent", "matowy", rot=(180, 0, 0),
                    gora=(0.08, 0.06), faza=0.0)
    for strona, zn in (("Left", 1), ("Right", -1)):
        a = kur.segment(strona + "UpperArm", zakrywa=True)
        w, h, d = W(strona + "UpperArm")
        a.blok("Rekaw", (0, -0.02, 0), (w - 0.06, h - 0.04, d - 0.06), "lisc")
        # mały skórzany naramiennik, lekko opadający na zewnątrz (nie „półka”)
        a.blok("Naramiennik", (zn * 0.05, h / 2 - 0.12, 0), (w + 0.02, 0.26, d + 0.06), "skorzany", "matowy",
               rot=(0, 0, -zn * 8), faza=0.1)
        a.blok("Naramiennik brzeg", (zn * 0.08, h / 2 - 0.27, 0), (w - 0.04, 0.1, d + 0.02), "skorzany_ciemny",
               "matowy", rot=(0, 0, -zn * 8), faza=0.03)
        a = kur.segment(strona + "LowerArm", zakrywa=True)
        w, h, d = W(strona + "LowerArm")
        a.blok("Karwasz", (0, 0, 0), (w - 0.04, h, d - 0.04), "skorzany", "matowy")
        a.blok("Karwasz brzeg", (0, h / 2 - 0.06, 0), (w + 0.02, 0.12, d + 0.02), "skorzany_ciemny", "matowy",
               faza=0.03)
        for i, y in enumerate((0.12, -0.12)):
            a.blok("Karwasz sznur %d" % i, (zn * (w / 2 - 0.0), y, 0), (0.04, 0.06, 0.5), "skorzany_jasny",
                   "matowy", faza=0.0)
    for strona, zn in (("Left", 1), ("Right", -1)):
        # poły tuniki siedzą na udzie (idą z nogą — nie przebijają jej w biegu ani w wypadzie)
        a = kur.segment(strona + "UpperLeg")
        w, h, d = W(strona + "UpperLeg")
        a.blok("Pola", (0, h / 2 - 0.2, 0), (w + 0.04, 0.42, d + 0.04), "lisc", "matowy", faza=0.03)
        a.blok("Pola lisc", (zn * 0.12, h / 2 - 0.42, d / 2 + 0.01), (0.3, 0.3, 0.04), "lisc", "matowy",
               rot=(0, 0, 45), faza=0.0)
        a.blok("Pola lisc tyl", (zn * 0.12, h / 2 - 0.42, -d / 2 - 0.01), (0.3, 0.3, 0.04), "lisc", "matowy",
               rot=(0, 0, 45), faza=0.0)

    # --- spodnie (część kirysu): biodra i uda
    spo = nowy("zwiadowca_spodnie", "Spodnie Zwiadowcy", "Chest", "Armor", czesc_od="zwiadowca_kurtka")
    a = spo.segment("LowerTorso", zakrywa=True)
    w, h, d = W("LowerTorso")
    a.blok("Biodra", (0, 0, 0), (w - 0.06, h, d - 0.06), "lisc_ciemny")
    for strona in ("Left", "Right"):
        a = spo.segment(strona + "UpperLeg", zakrywa=True)
        w, h, d = W(strona + "UpperLeg")
        a.blok("Udo", (0, 0, 0), (w - 0.06, h, d - 0.06), "lisc_ciemny")

    # --- pas z sakwą (Belt): nakładka na biodrach
    pas = nowy("zwiadowca_pas", "Pas z sakwą", "Belt", "Armor")
    a = pas.segment("LowerTorso")
    w, h, d = W("LowerTorso")
    z = d / 2
    a.blok("Pas", (0, 0.04, 0), (w + 0.04, 0.26, d + 0.04), "skorzany_ciemny", "matowy", faza=0.03)
    a.blok("Klamra", (0, 0.04, z + 0.04), (0.34, 0.28, 0.06), "skorzany_jasny", "matowy", faza=0.03)
    a.blok("Klamra srodek", (0, 0.04, z + 0.075), (0.16, 0.12, 0.03), "skorzany_ciemny", faza=0.0)
    a.blok("Sakwa", (0.78, -0.12, -z - 0.12), (0.46, 0.42, 0.26), "skorzany", "matowy", faza=0.06)
    a.blok("Sakwa klapka", (0.78, 0.02, -z - 0.26), (0.48, 0.18, 0.04), "skorzany_ciemny", "matowy", faza=0.0)

    # --- rękawice bez palców (Gloves): dłoń w kolorze skóry z mankietem rękawicy
    rek = nowy("zwiadowca_rekawice", "Rękawice bez palców", "Gloves", "Armor")
    for strona in ("Left", "Right"):
        a = rek.segment(strona + "Hand", zakrywa=True)
        w, h, d = W(strona + "Hand")
        a.blok("Dlon", (0, 0, 0), (w - 0.04, h, d - 0.04), "skora")
        a.blok("Rekawica", (0, h / 2 - 0.05, 0), (w, 0.12, d), "skorzany_ciemny", "matowy", faza=0.02)

    # --- buty z wywiniętą cholewą (Boots): golenie i stopy
    but = nowy("zwiadowca_buty", "Buty z wywiniętą cholewą", "Boots", "Armor")
    for strona in ("Left", "Right"):
        a = but.segment(strona + "LowerLeg", zakrywa=True)
        w, h, d = W(strona + "LowerLeg")
        a.blok("Cholewa", (0, -0.04, 0), (w - 0.06, h - 0.08, d - 0.06), "skorzany", "matowy")
        a.blok("Cholewa wywiniecie", (0, h / 2 - 0.1, 0), (w + 0.06, 0.2, d + 0.06), "skorzany_jasny", "matowy",
               faza=0.04)
        a.blok("Cholewa pasek", (0, -0.12, d / 2 - 0.01), (w - 0.2, 0.08, 0.06), "skorzany_ciemny", "matowy",
               faza=0.0)
        a = but.segment(strona + "Foot", zakrywa=True)
        w, h, d = W(strona + "Foot")
        a.blok("But", (0, 0.02, 0), (w - 0.06, h - 0.04, d), "skorzany_ciemny")
        a.blok("Podeszwa", (0, -h / 2 + 0.04, 0.02), (w, 0.08, d + 0.04), "skorzany", "matowy", faza=0.0)
        a.blok("Czubek", (0, -0.02, d / 2 + 0.02), (w - 0.24, 0.24, 0.1), "skorzany_ciemny", "matowy", faza=0.03)

    # --- łuk z kołczanem (druga ręka): kołczan z pasem na skos na tułowiu (wierzchnia) + łuk na LeftGripAttachment
    lu = nowy("zwiadowca_luk", "Łuk z kołczanem", "OffHand", "Weapons")
    a = lu.segment("UpperTorso")
    w, h, d = W("UpperTorso")
    z = d / 2
    # pas kołczanu na skos: z prawego barku (−X) do lewego biodra (+X), z przodu i z tyłu
    for zk, s in ((1, ""), (-1, " tyl")):
        a.blok("Pas kolczanu" + s, (-0.05, -0.02, zk * (z + 0.05)), (2.0, 0.2, 0.05), "skorzany_ciemny", "matowy",
               rot=(0, 0, -42), faza=0.0)
    a.blok("Sprzaczka pasa", (-0.32, 0.27, z + 0.085), (0.2, 0.2, 0.04), "skorzany_jasny", "matowy",
           rot=(0, 0, -42), faza=0.0)
    # kołczan na plecach (na skos: dno przy lewym biodrze, wylot za prawym barkiem) i lotki strzał
    with a.uklad(pos=(-0.16, 0.08, -z - 0.36), obrot=(0, 0, 50)):
        a.blok("Kolczan", (0, 0, 0), (0.56, 1.8, 0.46), "skorzany", "matowy", faza=0.08)
        a.blok("Kolczan dno", (0, -0.86, 0), (0.6, 0.14, 0.5), "skorzany_ciemny", "matowy", faza=0.04)
        a.blok("Kolczan wylot", (0, 0.86, 0), (0.62, 0.14, 0.52), "skorzany_ciemny", "matowy", faza=0.04)
        a.blok("Kolczan pas", (0, 0.2, -0.24), (0.6, 0.12, 0.04), "skorzany_ciemny", "matowy", faza=0.0)
        for i, (x, zz, dl, kat) in enumerate(((-0.13, 0.08, 0.8, 8), (0.1, -0.08, 0.95, -6), (0.0, 0.12, 0.68, 0))):
            with a.uklad(pos=(x, 0.9, zz), obrot=(0, 0, kat)):
                a.blok("Drzewce %d" % i, (0, dl / 2, 0), (0.06, dl, 0.06), "skorzany_jasny", "matowy", faza=0.0)
                a.blok("Lotka %d" % i, (0, dl - 0.12, 0), (0.2, 0.3, 0.04), "akcent", "matowy", faza=0.0)
                a.blok("Lotka %d b" % i, (0, dl - 0.12, 0), (0.04, 0.3, 0.2), "akcent", "matowy", faza=0.0)
    lu.na_zaczepie(luk())

    # --- sztylet (Weapon)
    sz = nowy("zwiadowca_sztylet", "Sztylet Zwiadowcy", "Weapon", "Weapons")
    sz.na_zaczepie(sztylet())
    return [kap, kur, spo, pas, rek, but, lu, sz]


def wybierz(ids, wszystkie=None):
    """Przedmioty o podanych id (w tej kolejności) z listy `wszystkie` (domyślnie świeże przedmioty())."""
    wszystkie = {x.id: x for x in (wszystkie or przedmioty())}
    return [wszystkie[i] for i in ids]


# --------------------------------------------------------------------------- klipy, ciało, stroje
_ODNIESIENIE = []


def postac_odniesienia():
    """Dawny model (pełny strój z łukiem i sztyletem) z klipami policzonymi tak jak przed D-071 — źródło klipów
    każdego stroju. Liczona raz na proces (klipy zależą od geometrii: stopy płasko na ziemi, nic pod ziemią)."""
    if not _ODNIESIENIE:
        p = ubierz(_golas(ID, NAZWA), wybierz(ODNIESIENIE_KLIPOW), id=ID, nazwa=NAZWA)
        _klipy(p)
        p.ustaw_poze_renderu("idle", 0)
        _ODNIESIENIE.append(p)
    return _ODNIESIENIE[0]


def cialo(zaczepy_ekwipunku=False):
    """Goły Zwiadowca „zwiadowca_cialo” z klipami postaci odniesienia. zaczepy_ekwipunku=True — dodatkowo 15 zaczepów
    Ekw<Kosc>Attachment (środek klocka kości) dla eksportu ciała do gry; w zbuduj() ich nie ma."""
    return kopiuj_klipy(postac_odniesienia(), _golas(ID + "_cialo", NAZWA + " (ciało bazowe)", zaczepy_ekwipunku))


def stroj(nazwa, wszystkie=None):
    """Zwiadowca w stroju z STROJE: postać „zwiadowca_<nazwa>”."""
    return ubierz(cialo(), wybierz(STROJE[nazwa], wszystkie), id="%s_%s" % (ID, nazwa),
                  nazwa="%s — %s" % (NAZWA, NAZWY_STROJOW[nazwa]))


def zbuduj():
    """[Zwiadowca w pełnym stroju kanonicznym (id „zwiadowca”), łuk, sztylet] — jak przed D-071."""
    prz = przedmioty()
    p = ubierz(cialo(), wybierz(KANON, prz), id=ID, nazwa=NAZWA)
    po_id = {x.id: x for x in prz}
    # łuk i sztylet: osobne przedmioty (przedmioty/zwiadowca_luk.fbx, zwiadowca_sztylet.fbx); w FBX postaci ich nie
    # ma (eksport=False), w renderach i filmach są w dłoniach; kołczan jest wtopiony w tułów jak dawniej
    luk_akc = next(s["akc"] for s in po_id["zwiadowca_luk"].segmenty if s["kosc"] is None)
    return [p, luk_akc, po_id["zwiadowca_sztylet"].segmenty[0]["akc"]]


def warianty(rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/zwiadowca/ekwipunek/): „plansze” — postacie ze STROJE (id zwiadowca_<strój>)
    i ikony całych przedmiotów; „eksport” — gołe ciało z zaczepami Ekw… (tylko klip idle: pozostałe klipy są
    w zwiadowca__<klip>.fbx, te same kości) i każdy segment kostny osobno."""
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
            "wlosy": {"id": "zwiadowca_wlosy", "zaczep": "HairAttachment", "znacznik": "Wlosy"},
            "przedmioty": [x.opis() for x in przedmioty()]}


SLABOSCI = [
    "D-071: model główny (zwiadowca.fbx, plansza, filmy) to pełny strój kanoniczny — wygląd bez zmian. Strój jest "
    "wtapiany w bryły kości (te same siatki <Kosc>_Geo), więc w zwiadowca.fbx nadal jest częścią ciała. Ubieranie "
    "w grze ma iść przez gołe ciało (ekwipunek/zwiadowca_cialo.fbx z zaczepami Ekw<Kosc>Attachment) i segmenty "
    "z ekwipunek/przedmioty/ — ta droga nie była sprawdzana w Studio (przezroczystość gołych brył pod powłoką, "
    "AddAccessory z własnymi nazwami zaczepów).",
    "Łuk i sztylet są osobnymi przedmiotami (przedmioty/zwiadowca_luk.fbx, zwiadowca_sztylet.fbx) — w FBX postaci ich "
    "nie ma; w grze trzeba je dać jako Tool albo akcesoria na LeftGripAttachment i RightGripAttachment. Przedmiot "
    "„Łuk z kołczanem” ma jeszcze segment kołczanu z pasem na skos (ekwipunek/przedmioty/zwiadowca_luk_tulow) — "
    "w grze zakłada się oba razem (slot OffHand to propozycja, EKWIPUNEK.md pkt 8).",
    "Goły Zwiadowca (ciało bazowe): rozczochrana czupryna (osobne akcesorium zwiadowca_wlosy, kaptur ją chowa), "
    "lniana koszula z podwiniętymi rękawami, sznurowanym dekoltem i wyszytym listkiem, zielone spodenki z troczkami "
    "i bose stopy — propozycja do oceny (plansza ekwipunek/zwiadowca_ekwipunek_plansza.jpg). Grzywka (trzy kosmyki) "
    "jest częścią twarzy jak dawniej, więc w każdym stroju wygląda tak samo; bez kaptura wisi spod opaski czupryny.",
    "Kaptur z peleryną to jeden przedmiot (Helmet): bez kaptura nie ma też peleryny, a kołczan (część łuku) leży "
    "wtedy wprost na kirysie. Bez kirysu pas kołczanu leży na lnianej koszuli (0,025 studa nad jej ścianą; nad "
    "kirysem, jak dawniej, tylko 0,005).",
    "Upadek w różnych strojach (klip wspólny, liczony na pełnym stroju): Zwiadowca leży na brzuchu oparty na "
    "dłoniach i przedramionach, więc w każdym stroju leży na ziemi (ostatnia klatka: pełny strój i strój bez "
    "kaptura 0,000; goły, „lekki” i „kaptur_i_sztylet” −0,025 — gołe dłonie są o 0,02 grubsze niż dłonie "
    "w rękawicach). Tułów jest nad ziemią: w kirysie 0,26 studa, w samej koszuli 0,30–0,35 (jak dawniej: leży na "
    "rękach, nie na piersi). Najgłębiej pod ziemią w trakcie klipów: goły −0,056 (upadek kl. 21), pełny −0,033 "
    "(dawny model tak samo).",
    "zwiadowca_cialo.fbx/.glb ma tylko klip idle (reszta klipów: zwiadowca__<klip>.fbx, te same kości i nazwy).",
    "Strzał z łuku to sam ruch: łuk się nie ugina, cięciwa jest sztywna i nie dochodzi do dłoni, strzały ani zielonej "
    "smugi trucizny nie ma (efekt do dorobienia w grze). Z boku i z tyłu (kamera gracza) strzał czyta się dobrze; "
    "w kadrze 3/4 z przodu widać łuk wyciągnięty do kamery, a dłoń naciągającą zasłania tułów; od przodu pięść z łukiem "
    "jest przed dolną częścią twarzy (postać celuje w widza — tylko zasłanianie, bez przenikania).",
    "Sztylet zostaje w prawej dłoni także przy strzale — cięciwę „naciąga” pięść ze sztyletem ostrzem w dół i na "
    "zewnątrz. Barki R15 są szerokie (3,15 studa), a ręka krótka (1,45 studa do nadgarstka), więc dłoń nie sięga "
    "twarzy ani linii strzały: naciąg to pięść wysoko przy prawym barku z łokciem cofniętym w tył.",
    "Bryły są sztywno przypięte do kości: kaptur, peleryna i chusta nie falują; poły tuniki siedzą na udach (idą z "
    "nogą, nie przebijają jej). Upadek kończy się leżeniem na brzuchu (na plecach ciało wisiało na kołczanie).",
    "Twarz nie ma mimiki — ten sam pogodny uśmiech przy trafieniu i upadku.",
    "Unik i uderzenie z góry przesuwają postać w samym klipie (kość LowerTorso): salto ok. 3,25 studa w bok i odskok "
    "z powrotem, wypad ok. 0,5 studa do przodu; klip kończy się w punkcie startu. W salcie biodra obracają się o "
    "−360° (ostatnia klatka ma kąt −360 = ta sama orientacja co 0) — do sprawdzenia przy imporcie klipu do Roblox.",
    "Kontrola przenikania (python -B swiat/postacie/zwiadowca.py --kontrola) liczy każdą bryłę głowy (z kapturem "
    "i włosami), tułowia (z peleryną i kołczanem) i bioder jako skrzynkę (ostrosłupy jak skrzynki, czyli ostrożnie), "
    "margines 0,06 studa; ruchome: łuk, sztylet, przedramiona i dłonie. Działa na każdym stroju z STROJE. Wynik "
    "15.11: w żadnym z pięciu strojów nic nie przenika (dawny model też nie). Nie sprawdza broni względem nóg ani "
    "łuku względem własnego przedramienia.",
    "Wspólny kadr filmów obejmuje salto w bok, więc w filmach i arkuszach klatek postać jest mniejsza niż na planszy.",
    "Klipy to szkice (0,67–2 s), nie gotowa animacja. Bieg jest w miejscu (stopy ślizgają się względem ziemi).",
    "LowerTorso i Root nie są w 0,0,0 (biodra na wysokości 1,9) — tak jak u Rycerza; dla postaci w grze bez "
    "znaczenia, ciało awatara może tego wymagać (sprawdzić przy pierwszym imporcie).",
]


# ---------------------------------------------------------------------------------------------------- animacje
KOSCI = ("LowerTorso", "UpperTorso", "Head", "LeftUpperArm", "LeftLowerArm", "LeftHand", "RightUpperArm",
         "RightLowerArm", "RightHand", "LeftUpperLeg", "LeftLowerLeg", "LeftFoot", "RightUpperLeg", "RightLowerLeg",
         "RightFoot")
STOPY = ("LeftFoot", "RightFoot")


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


def _punkty(p):
    """Punkty kontrolne brył ciała (narożniki i środki ścian skrzynek) na kościach, w układzie stawu kości."""
    if getattr(p, "_pkt", None) is None:
        pk = {}
        for c in p.czesci:
            Rc = macierz_obrotu(*c["r"])
            h = [v / 2 for v in c["s"]]
            for a in (-1, 0, 1):
                for b in (-1, 0, 1):
                    for e in (-1, 0, 1):
                        lok = razy_wektor(Rc, (a * h[0], b * h[1], e * h[2]))
                        pk.setdefault(c["kosc"], []).append(tuple(c["p"][i] + lok[i] for i in range(3)))
        p._pkt = pk
    return p._pkt


def _najnizej(p, W, kosci):
    pk, mn = _punkty(p), 1e9
    for n in kosci:
        R, t = W[n]
        for q in pk.get(n, ()):
            mn = min(mn, razy_wektor(R, q)[1] + t[1])
    return mn


def _stopy_plasko(p, pz):
    """Stopy, których poza nie ustawia: płasko na ziemi, palcami tam, gdzie patrzą biodra (z ewentualnym skrętem
    uda); kierunek z bioder, nie z goleni — goleń mocno zgięta w tył patrzy przodem w ziemię."""
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
    na ziemi; ziemia="cialo": całe ciało dociągnięte do ziemi po najniższym punkcie (siad, leżenie); ziemia=False:
    lot (biodra jak w pozie, ale nic nie schodzi pod ziemię)."""
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
    """Dociąga pozę do ziemi według pz["_ziemia"] (patrz _poza)."""
    z = pz["_ziemia"]
    if z is True:
        _stopy_plasko(p, pz)
        dno = _najnizej(p, _fk(p, pz), STOPY)
    elif z == "cialo":
        dno = _najnizej(p, _fk(p, pz), KOSCI)
    else:
        dno = min(0.0, _najnizej(p, _fk(p, pz), KOSCI))
    x, y, zz = pz["LowerTorso"]["przes"]
    pz["LowerTorso"]["przes"] = (x, round(y - dno, 4), zz)


# ------------------------------------------------------------------ ręka celuje: prosta odwrotna kinematyka (2 kości)
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


def _reka(p, pz, strona, cel, biegun, os=None, przod=None, swiat=False):
    """Ustawia w pozie pz ramię, przedramię i dłoń strony („Left”/„Right”) tak, żeby nadgarstek trafił w cel.
    cel = przesunięcie od stawu barku, biegun = kierunek, w którą stronę wychodzi łokieć — w osiach tułowia
    (swiat=False) albo w osiach modelu (swiat=True). os / przod = kierunek broni w dłoni (oś broni = +Y przedmiotu:
    ostrze sztyletu, ramiona łuku; przód broni = +Z przedmiotu: płaz sztyletu, brzuch łuku) w tych samych osiach.
    Łokieć zgina się tylko w zawiasie (obrót przedramienia = sam rx), jak w klipach pisanych ręcznie."""
    W = _fk(p, pz)
    Rt = W["UpperTorso"][0]
    S = W[strona + "UpperArm"][1]
    do_sw = (lambda v: v) if swiat else (lambda v: razy_wektor(Rt, v))
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
        A = _n(do_sw(os))
        F = do_sw(przod)
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
    """Klucz w KAŻDEJ klatce między pozami kluczowymi (wynik _poza albo słownik; {} = spoczynek). Kąty przechodzą
    z łagodnym wejściem i wyjściem (wyg = {numer pozy: "liniowo"} — odcinek od tej pozy jednostajnie); gdy obie
    sąsiednie pozy stoją na ziemi, stopy są w każdej klatce płasko na ziemi; przy siadzie i leżeniu ciało leży na
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


def _klipy(p):
    idle(p)
    ruch(p)
    atak(p)
    umiejetnosc(p)
    uderzenie_z_gory(p)
    trafienie(p)
    unik(p)
    upadek(p)
    wiwat(p)


# poza gotowości: lekko ugięte kolana, łuk pionowo z boku (cięciwą do ciała), sztylet nisko przed prawym biodrem
GOTOWOSC = {"UpperTorso": (6, -8, 0), "Head": (-4, 8, 0),
            "LeftUpperArm": (-20, 0, 24), "LeftLowerArm": (-60, 0, 0), "LeftHand": (-2, 0, -30),
            "RightUpperArm": (-8, 0, -12), "RightLowerArm": (-52, 0, 0), "RightHand": (-10, 0, 0),
            "LeftUpperLeg": (-14, 0, 6), "LeftLowerLeg": (24, 0, 0),
            "RightUpperLeg": (-6, 0, -6), "RightLowerLeg": (16, 0, 0),
            "LowerTorso": {"obrot": (0, -10, 0)}}


def _z(baza, **zmiany):
    d = dict(baza)
    d.update(zmiany)
    return d


def idle(p, dl=60):
    """Spoczynek w gotowości (pętla 2 s): sprężysty oddech na ugiętych kolanach, głowa rozgląda się."""
    k = p.klip("idle", dl, petla=True)
    a = _poza(p, GOTOWOSC)
    b = _poza(p, _z(GOTOWOSC, UpperTorso=(9, -6, 1), Head=(-6, 2, 2), LeftUpperLeg=(-17, 0, 6),
                    LeftLowerLeg=(30, 0, 0), RightUpperLeg=(-9, 0, -6), RightLowerLeg=(22, 0, 0),
                    LeftLowerArm=(-63, 0, 0), RightLowerArm=(-56, 0, 0)))
    _sekwencja(k, (0, dl // 2, dl), (a, b, a))
    return k


def ruch(p, dl=20):
    """Lekki bieg w miejscu (pętla 0,67 s na dwa kroki): pochylony tułów, wysokie kolano, ręce z bronią pracują
    na przemian; biodra podskakują same (najniższa stopa zawsze na ziemi)."""
    k = p.klip("ruch", dl, petla=True)

    def krok(s):                       # s = 1: lewa noga z przodu; −1: prawa
        L, R = ("Left", "Right") if s > 0 else ("Right", "Left")
        return {"LowerTorso": {"obrot": (8, -s * 10, 0)}, "UpperTorso": (14, s * 14, 0), "Head": (-16, s * 4, 0),
                L + "UpperLeg": (-42, 0, 0), L + "LowerLeg": (22, 0, 0),
                R + "UpperLeg": (30, 0, 0), R + "LowerLeg": (62, 0, 0), R + "Foot": (40, 0, 0),
                # ręka przeciwna do nogi z przodu idzie do przodu
                "LeftUpperArm": (s * 38 - 6, 0, 16), "LeftLowerArm": (-62, 0, 0), "LeftHand": (-2, 0, -30),
                "RightUpperArm": (-s * 40 - 8, 0, -14), "RightLowerArm": (-70, 0, 0), "RightHand": (-10, 0, 0)}

    def przejscie(s):                  # s = 1: lewa noga podporowa, prawa przechodzi wysoko do przodu
        L, R = ("Left", "Right") if s > 0 else ("Right", "Left")
        return {"LowerTorso": {"obrot": (8, 0, 0)}, "UpperTorso": (16, 0, 0), "Head": (-18, 0, 0),
                L + "UpperLeg": (-4, 0, 0), L + "LowerLeg": (14, 0, 0),
                R + "UpperLeg": (-46, 0, 0), R + "LowerLeg": (100, 0, 0), R + "Foot": (10, 0, 0),
                "LeftUpperArm": (-6, 0, 16), "LeftLowerArm": (-62, 0, 0), "LeftHand": (-2, 0, -30),
                "RightUpperArm": (-8, 0, -14), "RightLowerArm": (-74, 0, 0), "RightHand": (-10, 0, 0)}

    pozy = (krok(1), przejscie(-1), krok(-1), przejscie(1), krok(1))
    _sekwencja(k, (0, 5, 10, 15, dl), pozy, wyg={i: "liniowo" for i in range(4)})
    return k


def atak(p, dl=28):
    """Pchnięcie sztyletem (0,93 s): skręt i przysiad z ostrzem cofniętym przy prawym biodrze (kl. 7) → szybki wypad
    prawą nogą i pchnięcie na wysokości piersi przeciwnika, trafienie w kl. 11, dwie klatki zatrzymania → powrót.
    Łuk w lewej ręce odchodzi do tyłu dla równowagi."""
    k = p.klip("atak", dl, petla=False)
    zamach = _poza(p, {"LowerTorso": {"obrot": (2, -30, 0), "przes": (0, 0, -0.2)}, "UpperTorso": (4, -28, 0),
                       "Head": (-6, 50, 0),
                       "LeftUpperLeg": (-32, 0, 8), "LeftLowerLeg": (48, 0, 0),
                       "RightUpperLeg": (-2, 0, -10), "RightLowerLeg": (40, 0, 0),
                       "LeftUpperArm": (-22, 0, 58), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30),
                       # ostrze cofnięte daleko za prawe biodro, na zewnątrz od tułowia (wyraźny zamach z boku i 3/4)
                       "RightUpperArm": (40, 0, -30), "RightLowerArm": (-60, 0, 0), "RightHand": (-24, 0, 0)})
    pchniecie = _poza(p, {"LowerTorso": {"obrot": (8, 22, 0), "przes": (0, 0, 0.55)}, "UpperTorso": (12, 18, 0),
                          "Head": (-12, -34, 0),
                          "RightUpperLeg": (-58, 0, -4), "RightLowerLeg": (48, 0, 0),
                          "LeftUpperLeg": (30, 0, 6), "LeftLowerLeg": (34, 0, 0),
                          "LeftUpperArm": (28, 0, 40), "LeftLowerArm": (-36, 0, 0), "LeftHand": (-2, 0, -30)})
    _reka(p, pchniecie, "Right", cel=(0.25, -0.3, 1.42), biegun=(-0.6, -1, 0), os=(0.05, -0.12, 1), przod=(0, 1, 0),
          swiat=True)
    dobicie = _poza(p, _z({n: v["obrot"] for n, v in pchniecie.items() if n in KOSCI and n not in STOPY},
                          LowerTorso={"obrot": (9, 24, 0), "przes": (0, 0, 0.6)}))
    _reka(p, dobicie, "Right", cel=(0.22, -0.34, 1.45), biegun=(-0.6, -1, 0), os=(0.05, -0.16, 1), przod=(0, 1, 0),
          swiat=True)
    powrot = _poza(p, {"LowerTorso": {"obrot": (4, 8, 0), "przes": (0, 0, 0.25)}, "UpperTorso": (8, 4, 0),
                       "Head": (-6, -6, 0), "RightUpperLeg": (-28, 0, -6), "RightLowerLeg": (30, 0, 0),
                       "LeftUpperLeg": (10, 0, 6), "LeftLowerLeg": (24, 0, 0),
                       "LeftUpperArm": (-6, 0, 30), "LeftLowerArm": (-50, 0, 0), "LeftHand": (-2, 0, -30),
                       "RightUpperArm": (-40, 0, -14), "RightLowerArm": (-50, 0, 0), "RightHand": (-10, 0, 0)})
    _sekwencja(k, (0, 7, 11, 13, 20, dl), (GOTOWOSC, zamach, pchniecie, dobicie, powrot, GOTOWOSC),
               wyg={1: "liniowo"})
    return k


def _strzal(p, naciag, tulow=(0, -28, 0), biodra=(0, -46, 0), glowa=(-4, 64, 4), luk_cel=(-0.55, 0.2, 1.4),
            biegun=(-0.5, 0.9, -1), luk_os=(0.12, 1, 0), noz_os=(-0.6, -0.8, 0.05)):
    """Poza strzału: szeroki rozkrok, lewy bark do celu (biodra i tułów skręcone razem ok. 75°), głowa patrzy
    wzdłuż ręki z łukiem. Lewa ręka wyprostowana w stronę celu (+Z) na wysokości barku, łuk pionowo, brzuchem do
    celu (luk_cel = przesunięcie nadgarstka od lewego barku, osie modelu). Prawa dłoń (ze sztyletem ostrzem w dół
    i na zewnątrz, z dala od twarzy i tułowia) w miejscu `naciag` (od prawego barku, osie tułowia), łokieć wysoko i w tył (biegun)."""
    pz = _poza(p, {"LowerTorso": {"obrot": biodra}, "UpperTorso": tulow, "Head": glowa,
                   "LeftUpperLeg": (-18, 0, 20), "LeftLowerLeg": (22, 0, 0),
                   "RightUpperLeg": (10, 0, -20), "RightLowerLeg": (16, 0, 0)})
    _reka(p, pz, "Left", cel=luk_cel, biegun=(0.3, -1, -0.3), os=luk_os, przod=(0, 0, 1), swiat=True)
    _reka(p, pz, "Right", cel=naciag, biegun=biegun, os=noz_os, przod=(0, 0, 1))
    return pz


def umiejetnosc(p, dl=54):
    """Zatruta strzała (1,8 s), wyraźnie inna niż atak sztyletem: obrót lewym barkiem do celu i łuk wyrzucony
    przed siebie na wysokość barku (kl. 9), prawa dłoń sięga do cięciwy, naciąg z łokciem wysoko w tył (kl. 19),
    celowanie z lekkim drżeniem, wypuszczenie z odrzutem (kl. 31: prawa dłoń odskakuje w tył, łuk podbity w górę),
    zatrzymanie i powrót. Samej strzały i zielonej smugi trucizny nie ma (efekt w grze)."""
    k = p.klip("umiejetnosc", dl, petla=False)
    # barki R15 są szerokie, a ręce krótkie: dłoń naciągająca nie sięga twarzy, więc „naciąg” to pięść wysoko przy
    # prawym barku z łokciem cofniętym w tył (czytelny kształt z boku i z tyłu, nic nie wchodzi w tułów ani kaptur)
    # wyrzut: łuk idzie do celu, prawa dłoń ze sztyletem ostrzem naprzód wychodzi przed brzuch (ostrze nie
    # przechodzi przez tułów w drodze z gotowości do cięciwy)
    wyrzut = _strzal(p, naciag=(-0.3, -0.6, 0.8), tulow=(3, -10, 0), biodra=(0, -20, 0), glowa=(-3, 26, 0),
                     luk_cel=(0.4, -0.2, 1.2), biegun=(-1, -0.3, 0), noz_os=(-0.5, 0.2, 1))
    przyklad = _strzal(p, naciag=(0.15, 0.1, 1.15), tulow=(2, -18, 0), biodra=(0, -34, 0), glowa=(-2, 46, 2),
                       biegun=(-1, -0.3, -0.2))
    naciag = _strzal(p, naciag=(-0.4, 0.5, 0.2), biegun=(-0.3, 0.3, -1))
    celuje = _strzal(p, naciag=(-0.45, 0.45, 0.25), tulow=(1, -30, 0), luk_cel=(-0.53, 0.24, 1.4),
                     biegun=(-0.4, 0.4, -1))
    wypuszcza = _strzal(p, naciag=(-0.55, 0.5, -0.4), tulow=(-3, -32, 0), glowa=(-8, 68, 4),
                        luk_cel=(-0.55, 0.55, 1.3), biegun=(0.3, 0.2, -1), luk_os=(0.2, 1, -0.25))
    zostaje = _strzal(p, naciag=(-0.55, 0.45, -0.3), tulow=(-1, -31, 0), luk_cel=(-0.55, 0.4, 1.35),
                      biegun=(0.2, 0.2, -1))
    opuszcza = _strzal(p, naciag=(-0.35, -1.05, 0.5), tulow=(4, -14, 0), biodra=(0, -24, 0), glowa=(-4, 30, 0),
                       luk_cel=(0.5, -0.8, 1.0), biegun=(-1, 0, -0.3), noz_os=(-0.3, 0.3, 1))
    _sekwencja(k, (0, 4, 9, 13, 19, 30, 32, 40, 47, dl),
               (GOTOWOSC, wyrzut, przyklad, przyklad, naciag, celuje, wypuszcza, zostaje, opuszcza, GOTOWOSC),
               wyg={5: "liniowo"})
    return k


def uderzenie_z_gory(p, dl=46):
    """Uderzenie z góry (drugi klip umiejętności, 1,5 s): przysiad (kl. 7), wyskok z sztyletem uniesionym wysoko
    nad prawym barkiem (szczyt kl. 15), cios z góry w dół przed siebie przy lądowaniu w głębokim wypadzie (kl. 20),
    zatrzymanie i powrót."""
    k = p.klip("uderzenie_z_gory", dl, petla=False)
    przysiad = _poza(p, {"LowerTorso": {"obrot": (10, -6, 0)}, "UpperTorso": (18, -6, 0), "Head": (-20, 6, 0),
                         "LeftUpperLeg": (-60, 0, 8), "LeftLowerLeg": (92, 0, 0),
                         "RightUpperLeg": (-56, 0, -8), "RightLowerLeg": (88, 0, 0),
                         "LeftUpperArm": (30, 0, 30), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30),
                         "RightUpperArm": (36, 0, -24), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0)})
    szczyt = _poza(p, {"LowerTorso": {"obrot": (-6, -10, 0), "przes": (0, 1.7, 0.2)}, "UpperTorso": (-10, -12, 0),
                       "Head": (4, 14, 0),
                       "LeftUpperLeg": (-70, 0, 10), "LeftLowerLeg": (110, 0, 0), "LeftFoot": (20, 0, 0),
                       "RightUpperLeg": (-30, 0, -8), "RightLowerLeg": (90, 0, 0), "RightFoot": (25, 0, 0),
                       "LeftUpperArm": (-40, 0, 70), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30)},
                   ziemia=False)
    # dłoń wysoko nad prawym barkiem, na zewnątrz od kaptura; ostrze w górę i na zewnątrz
    _reka(p, szczyt, "Right", cel=(-0.62, 1.3, 0.12), biegun=(-1, 0.1, -0.3), os=(-0.4, 1, 0.1), przod=(0, 0, 1))
    cios = _poza(p, {"LowerTorso": {"obrot": (18, 10, 0), "przes": (0, 0, 0.45)}, "UpperTorso": (24, 8, 0),
                     "Head": (-30, -14, 0),
                     "RightUpperLeg": (-74, 0, -6), "RightLowerLeg": (80, 0, 0),
                     "LeftUpperLeg": (10, 0, 10), "LeftLowerLeg": (64, 0, 0),
                     "LeftUpperArm": (-10, 0, 62), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30)})
    _reka(p, cios, "Right", cel=(0.15, -0.75, 1.25), biegun=(-1, -0.4, 0), os=(0, -0.62, 0.78), przod=(-1, 0, 0),
          swiat=True)
    trzyma = _poza(p, _z({n: v["obrot"] for n, v in cios.items() if n in KOSCI and n not in STOPY},
                         LowerTorso={"obrot": (20, 10, 0), "przes": (0, 0, 0.45)}, UpperTorso=(27, 8, 0)))
    _reka(p, trzyma, "Right", cel=(0.15, -0.82, 1.22), biegun=(-1, -0.4, 0), os=(0, -0.66, 0.75), przod=(-1, 0, 0),
          swiat=True)
    wstaje = _poza(p, {"LowerTorso": {"obrot": (6, 4, 0), "przes": (0, 0, 0.2)}, "UpperTorso": (8, 0, 0),
                       "Head": (-8, 0, 0), "RightUpperLeg": (-34, 0, -6), "RightLowerLeg": (40, 0, 0),
                       "LeftUpperLeg": (-6, 0, 8), "LeftLowerLeg": (30, 0, 0),
                       "LeftUpperArm": (-10, 0, 30), "LeftLowerArm": (-50, 0, 0), "LeftHand": (-2, 0, -30),
                       "RightUpperArm": (-30, 0, -14), "RightLowerArm": (-50, 0, 0), "RightHand": (-10, 0, 0)})
    _sekwencja(k, (0, 7, 15, 20, 27, 36, dl), (GOTOWOSC, przysiad, szczyt, cios, trzyma, wstaje, GOTOWOSC),
               wyg={2: "liniowo"})
    return k


def trafienie(p, dl=20):
    """Reakcja na cios (0,67 s): szarpnięcie tułowia i głowy w tył (kl. 4), ręce odlatują na boki, krok w tył,
    powrót do gotowości."""
    k = p.klip("trafienie", dl, petla=False)
    szarp = _poza(p, {"LowerTorso": {"obrot": (-6, -4, 0), "przes": (0, 0, -0.4)}, "UpperTorso": (-18, 10, 4),
                      "Head": (-22, -14, 8),
                      "LeftUpperArm": (-34, 0, 48), "LeftLowerArm": (-40, 0, 0), "LeftHand": (-2, 0, -30),
                      "RightUpperArm": (-24, 0, -46), "RightLowerArm": (-46, 0, 0), "RightHand": (-10, 0, 0),
                      "RightUpperLeg": (18, 0, -6), "RightLowerLeg": (26, 0, 0),
                      "LeftUpperLeg": (-16, 0, 6), "LeftLowerLeg": (18, 0, 0)})
    wraca = _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (-2, -8, 0), "przes": (0, 0, -0.15)}, UpperTorso=(-4, -2, 1),
                        Head=(-8, 0, 2), RightUpperLeg=(6, 0, -6)))
    _sekwencja(k, (0, 4, 11, dl), (GOTOWOSC, szarp, wraca, GOTOWOSC), wyg={0: "liniowo"})
    return k


def unik(p, dl=40):
    """Unik — znak rozpoznawczy klasy (1,33 s): przysiad i wybicie w lewo (+X), boczne salto w powietrzu (pełny
    obrót w płaszczyźnie przodu, nogi podkulone, ręce z bronią rozłożone na zewnątrz — nic nie mija głowy),
    lądowanie w niskim przysiadzie ok. 3,2 studa w bok, krótki odskok z powrotem na linię ciosu."""
    k = p.klip("unik", dl, petla=False)
    rece_lot = {"LeftUpperArm": (0, 0, 110), "LeftLowerArm": (-20, 0, 0), "LeftHand": (-2, 0, -30),
                "RightUpperArm": (0, 0, -110), "RightLowerArm": (-20, 0, 0), "RightHand": (-10, 0, 0)}
    nogi_lot = {"LeftUpperLeg": (-80, 0, 14), "LeftLowerLeg": (110, 0, 0), "LeftFoot": (20, 0, 0),
                "RightUpperLeg": (-74, 0, -14), "RightLowerLeg": (104, 0, 0), "RightFoot": (20, 0, 0)}
    przysiad = _poza(p, {"LowerTorso": {"obrot": (8, 0, -12), "przes": (0.25, 0, 0)}, "UpperTorso": (14, 0, -8),
                         "Head": (-12, 0, 10),
                         "LeftUpperLeg": (-50, 0, 18), "LeftLowerLeg": (84, 0, 0),
                         "RightUpperLeg": (-46, 0, -2), "RightLowerLeg": (80, 0, 0),
                         "LeftUpperArm": (10, 0, 40), "LeftLowerArm": (-40, 0, 0), "LeftHand": (-2, 0, -30),
                         "RightUpperArm": (14, 0, -50), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0)})
    # lot: obrót bioder rz od 0 do −360 (głowa idzie w stronę +X), środek ciała po łuku w bok i w górę
    lot = []
    for kat, x, y in ((-50, 0.9, 1.05), (-130, 1.6, 2.45), (-215, 2.3, 2.7), (-295, 2.9, 1.7)):
        lot.append(_poza(p, dict(rece_lot, **nogi_lot, LowerTorso={"obrot": (0, 0, kat), "przes": (x, y, 0)},
                                 UpperTorso=(10, 0, 0), Head=(-10, 0, 0)), ziemia=False))
    ladowanie = _poza(p, {"LowerTorso": {"obrot": (10, 0, -366), "przes": (3.25, 0, 0)}, "UpperTorso": (16, 0, 6),
                          "Head": (-16, 0, -4),
                          "LeftUpperLeg": (-50, 0, 14), "LeftLowerLeg": (76, 0, 0),
                          "RightUpperLeg": (-44, 0, -6), "RightLowerLeg": (72, 0, 0),
                          "LeftUpperArm": (-30, 0, 80), "LeftLowerArm": (-30, 0, 0), "LeftHand": (-2, 0, -30),
                          "RightUpperArm": (-30, 0, -60), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0)})
    odskok = _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (2, -10, -360), "przes": (1.6, 0.75, 0)},
                         UpperTorso=(4, -8, -6), LeftUpperLeg=(-24, 0, 10), LeftLowerLeg=(40, 0, 0),
                         RightUpperLeg=(-20, 0, -10), RightLowerLeg=(36, 0, 0), LeftFoot=(18, 0, 0),
                         RightFoot=(18, 0, 0)), ziemia=False)
    koniec = _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (0, -10, -360)}))
    _sekwencja(k, (0, 5, 9, 12, 15, 18, 21, 26, 31, 35, dl),
               (GOTOWOSC, przysiad, lot[0], lot[1], lot[2], lot[3], ladowanie, ladowanie, odskok,
                _poza(p, _z(GOTOWOSC, LowerTorso={"obrot": (4, -10, -360), "przes": (0.1, 0, 0)},
                            LeftUpperLeg=(-24, 0, 6), LeftLowerLeg=(40, 0, 0), RightUpperLeg=(-16, 0, -6),
                            RightLowerLeg=(32, 0, 0))), koniec),
               wyg={1: "liniowo", 2: "liniowo", 3: "liniowo", 4: "liniowo", 5: "liniowo"})
    return k


def upadek(p, dl=60):
    """Pokonanie (2 s): szarpnięcie, chwiejny krok w tył, kolana się uginają, pada na kolana i dalej twarzą w dół,
    z rękami rozrzuconymi na boki i podkulonymi łydkami (komiksowo); głowa odwrócona w bok, więc twarz widać.
    Ostatnia klatka: leży (do utrzymania w grze). Na brzuchu, nie na plecach — leżąc na plecach ciało opierało się
    na kołczanie i wisiało nad ziemią."""
    k = p.klip("upadek", dl, petla=False)
    szarp = _poza(p, {"LowerTorso": {"obrot": (-6, -4, 0), "przes": (0, 0, -0.35)}, "UpperTorso": (-16, 10, 4),
                      "Head": (-24, -10, 8),
                      "LeftUpperArm": (-30, 0, 50), "LeftLowerArm": (-40, 0, 0), "LeftHand": (-2, 0, -30),
                      "RightUpperArm": (-22, 0, -48), "RightLowerArm": (-40, 0, 0), "RightHand": (-10, 0, 0),
                      "RightUpperLeg": (16, 0, -6), "RightLowerLeg": (24, 0, 0), "LeftUpperLeg": (-14, 0, 6)})
    chwiej = _poza(p, {"LowerTorso": {"obrot": (-4, 8, 6), "przes": (0, 0, -0.6)}, "UpperTorso": (14, -6, -8),
                       "Head": (24, 10, -12),
                       "LeftUpperArm": (0, 0, 20), "LeftLowerArm": (-20, 0, 0), "LeftHand": (-2, 0, -30),
                       "RightUpperArm": (6, 0, -16), "RightLowerArm": (-20, 0, 0), "RightHand": (-10, 0, 0),
                       "LeftUpperLeg": (8, 0, 4), "LeftLowerLeg": (20, 0, 0),
                       "RightUpperLeg": (-12, 0, -10), "RightLowerLeg": (26, 0, 0)})
    # kolana się uginają, głowa opada, ręce wiszą bezwładnie
    ugina = _poza(p, {"LowerTorso": {"obrot": (6, 4, 4), "przes": (0, 0, -0.6)}, "UpperTorso": (16, -4, -4),
                      "Head": (22, 6, -8),
                      "LeftUpperLeg": (-50, 0, 10), "LeftLowerLeg": (88, 0, 0),
                      "RightUpperLeg": (-44, 0, -10), "RightLowerLeg": (84, 0, 0),
                      "LeftUpperArm": (-14, 0, 22), "LeftLowerArm": (-24, 0, 0), "LeftHand": (-2, 0, -30),
                      "RightUpperArm": (-10, 0, -22), "RightLowerArm": (-24, 0, 0), "RightHand": (-10, 0, 0)})
    # na kolanach, tułów leci do przodu jak ścięte drzewo, ręce rozrzucone na boki, broń wzdłuż rąk (przy padaniu
    # obraca się tylko wokół własnej osi, więc nie wchodzi w ziemię)
    kolana = _poza(p, {"LowerTorso": {"obrot": (40, 2, 2), "przes": (0, 0, -0.35)}, "UpperTorso": (14, -4, 0),
                       "Head": (-30, 24, 0),
                       "LeftUpperLeg": (-38, 0, 10), "LeftLowerLeg": (100, 0, 0),
                       "RightUpperLeg": (-34, 0, -10), "RightLowerLeg": (96, 0, 0),
                       "LeftUpperArm": (-20, 0, 76), "LeftLowerArm": (-14, 0, 0), "LeftHand": (90, 90, 0),
                       "RightUpperArm": (-20, 0, -78), "RightLowerArm": (-14, 0, 0), "RightHand": (90, 0, 0)},
                   ziemia="cialo")
    # leży twarzą w dół; głowa uniesiona i odwrócona w bok (do kamery 3/4), łydki podkulone w górę; dłonie obrócone
    # tak, że łuk i sztylet leżą płasko na ziemi (a nie sterczą w niebo ani nie wchodzą w ziemię)
    lezy = {"LowerTorso": {"obrot": (88, 0, 0), "przes": (0, 0, 0.3)}, "UpperTorso": (2, 0, 0), "Head": (-70, 50, 0),
            "LeftUpperLeg": (4, 0, 10), "LeftLowerLeg": (75, 0, 0),
            "RightUpperLeg": (0, 0, -12), "RightLowerLeg": (45, 0, 0),
            "LeftUpperArm": (-20, -4, 80), "LeftLowerArm": (-14, 0, 0), "LeftHand": (90, 90, 0),
            "RightUpperArm": (-20, 4, -82), "RightLowerArm": (-14, 0, 0), "RightHand": (90, 0, 0)}
    # ostatnie drgnięcie: łydki podskakują, głowa unosi się i opada (tułów i ręce leżą, broń nie wchodzi w ziemię)
    odbicie = _z(lezy, Head=(-62, 44, 0), LeftLowerLeg=(95, 0, 0), RightLowerLeg=(66, 0, 0))
    lezy = _poza(p, lezy, ziemia="cialo")
    odbicie = _poza(p, odbicie, ziemia="cialo")
    _sekwencja(k, (0, 4, 12, 22, 30, 38, 43, 50, dl),
               (GOTOWOSC, szarp, chwiej, ugina, kolana, lezy, odbicie, lezy, lezy), wyg={4: "liniowo"})
    return k


def wiwat(p, dl=48):
    """Radość po wygranej (pętla 1,6 s): dwa podskoki, lewa ręka wyrzucona w bok i w górę z łukiem pionowo
    (wygięciem na zewnątrz — od przodu widać kształt łuku), prawa pięść ze sztyletem pompuje w górę, na zewnątrz od
    głowy; uśmiech do kamery."""
    k = p.klip("wiwat", dl, petla=True)
    dol = _poza(p, {"LowerTorso": {"obrot": (4, 0, 0)}, "UpperTorso": (8, 0, 0), "Head": (2, 0, -5),
                    "LeftUpperLeg": (-26, 0, 8), "LeftLowerLeg": (48, 0, 0),
                    "RightUpperLeg": (-24, 0, -8), "RightLowerLeg": (44, 0, 0)})
    _reka(p, dol, "Left", cel=(1.28, 0.3, 0.35), biegun=(0.2, -1, 0), os=(0, 1, 0), przod=(1, 0, 0.25))
    _reka(p, dol, "Right", cel=(-0.55, -0.3, 0.75), biegun=(-1, -0.5, 0), os=(-0.45, 1, 0.3), przod=(0, 0, 1))
    gora = _poza(p, {"LowerTorso": {"obrot": (-4, 0, 0), "przes": (0, 0.5, 0)}, "UpperTorso": (-8, 0, 0),
                     "Head": (-16, 0, 6),
                     "LeftUpperLeg": (-12, 0, 6), "LeftLowerLeg": (26, 0, 0), "LeftFoot": (22, 0, 0),
                     "RightUpperLeg": (-8, 0, -6), "RightLowerLeg": (22, 0, 0), "RightFoot": (22, 0, 0)},
                 ziemia=False)
    _reka(p, gora, "Left", cel=(1.02, 1.0, 0.25), biegun=(0.4, -1, 0), os=(-0.18, 1, 0), przod=(1, 0.2, 0.25))
    _reka(p, gora, "Right", cel=(-0.85, 1.12, 0.3), biegun=(-1, -0.2, 0), os=(-0.35, 1, 0.2), przod=(0, 0, 1))
    _sekwencja(k, (0, 12, 24, 36, dl), (dol, gora, dol, gora, dol))
    return k


# ---------------------------------------------------------------------------------------------------- kontrola
CIALO = ("Head", "UpperTorso", "LowerTorso")                    # tu broń, przedramię ani dłoń nie może wejść
KONCZYNY = ("LeftLowerArm", "LeftHand", "RightLowerArm", "RightHand")
BRON = ("zwiadowca_luk", "zwiadowca_sztylet")


def _bryly_kontroli(p):
    """Bryły ciała i założonych akcesoriów w układzie stawu swojej kości: {kosc, c, R, h, n, zrodlo ("cialo" albo
    id akcesorium)}. Ostrosłupy liczą się jak ich skrzynki (ostrożnie)."""
    d = p.json()
    wynik = []

    def dodaj(c, zrodlo):
        st = p.kosci[c["kosc"]]["staw"]
        wynik.append({"kosc": c["kosc"], "c": tuple(c["p"][i] - st[i] for i in range(3)), "R": macierz_obrotu(*c["r"]),
                      "h": tuple(v / 2.0 for v in c["s"]), "n": c["n"], "zrodlo": zrodlo})
    for c in d["czesci"]:
        dodaj(c, "cialo")
    for a in d["akcesoria"]:
        for c in a["czesci"]:
            dodaj(c, a["id"])
    return wynik


def _siatka_bryly(b, krok):
    """Punkty skrzynki bryły w układzie stawu: co najwyżej `krok` studa (w tym narożniki i ściany)."""
    osie = []
    for i in range(3):
        n = max(2, int(math.ceil(2 * b["h"][i] / krok)))
        osie.append([(-1 + 2.0 * j / n) * b["h"][i] for j in range(n + 1)])
    pk = []
    for x in osie[0]:
        for y in osie[1]:
            for z in osie[2]:
                lok = razy_wektor(b["R"], (x, y, z))
                pk.append(tuple(b["c"][i] + lok[i] for i in range(3)))
    return pk


def kontrola(p, margines=0.06, krok_broni=0.1, krok_ciala=0.25, klipy_=None):
    """Liczbowa kontrola klipów postaci (dowolny strój): czy łuk albo sztylet (punkty co krok_broni) albo przedramię
    i dłoń (punkty co krok_ciala) wchodzą w którąś bryłę głowy (z kapturem i włosami), tułowia (z peleryną, pasem
    i kołczanem) albo bioder (z pasem i sakwą) głębiej niż `margines` (każda bryła jako skrzynka); najniższy punkt
    ciała (bez broni) i z bronią w każdej klatce; w ostatniej klatce każdego klipu jednorazowego najniższy punkt ciała
    (upadek: na jakiej wysokości leży). Wartości kluczy modułu: klipy walki mają klucz w każdej klatce.
    Zwraca {klip: {"klatki", "bron": [(kl., co, kość, bryła, punkty, głębokość)], "konczyny": [...],
    "najnizej": (y, kl.), "najnizej_cialo": (y, kl.), "koniec": y}}."""
    br = _bryly_kontroli(p)
    cele = [b for b in br if b["kosc"] in CIALO]
    for b in cele:
        b["Rt"] = _tr(b["R"])
    ruchome = []
    for b in br:
        if b["zrodlo"] in BRON:
            ruchome.append((b["zrodlo"], b["kosc"], _siatka_bryly(b, krok_broni)))
        elif b["zrodlo"] == "cialo" and b["kosc"] in KONCZYNY:
            ruchome.append((b["kosc"], b["kosc"], _siatka_bryly(b, krok_ciala)))
    pudla = {}                                    # wstępny odsiew: skrzynka brył-celów kości (układ jej stawu)
    for b in cele:
        mn, mx = pudla.setdefault(b["kosc"], ([1e9] * 3, [-1e9] * 3))
        for i in range(3):
            pol = sum(abs(b["R"][i][j]) * b["h"][j] for j in range(3))
            mn[i], mx[i] = min(mn[i], b["c"][i] - pol), max(mx[i], b["c"][i] + pol)
    ciala = [(b["kosc"], _siatka_bryly(b, 10.0)) for b in br if b["zrodlo"] == "cialo"]
    wynik = {}
    for kl in p.klipy:
        if klipy_ and kl.nazwa not in klipy_:
            continue
        w = {"klatki": kl.dlugosc + 1, "bron": [], "konczyny": [], "najnizej": (1e9, -1),
             "najnizej_cialo": (1e9, -1), "koniec": None}
        for f in range(kl.dlugosc + 1):
            poza = {}
            for n in p.kosci:
                for kanal in ("obrot", "przes"):
                    v = kl.wartosc(n, kanal, f)
                    if v is not None:
                        poza.setdefault(n, {})[kanal] = tuple(v)
            W = _fk(p, poza)
            odw = {n: (_tr(W[n][0]), W[n][1]) for n in pudla}
            licz = {}
            for co, kosc, pkt in ruchome:
                R, t = W[kosc]
                for q in pkt:
                    s = razy_wektor(R, q)
                    s = (s[0] + t[0], s[1] + t[1], s[2] + t[2])
                    if s[1] < w["najnizej"][0]:
                        w["najnizej"] = (round(s[1], 3), f)
                    for n, (mn, mx) in pudla.items():
                        Rt, tn = odw[n]
                        l = razy_wektor(Rt, (s[0] - tn[0], s[1] - tn[1], s[2] - tn[2]))
                        if any(l[i] < mn[i] + margines or l[i] > mx[i] - margines for i in range(3)):
                            continue
                        for b in cele:
                            if b["kosc"] != n:
                                continue
                            u = razy_wektor(b["Rt"], (l[0] - b["c"][0], l[1] - b["c"][1], l[2] - b["c"][2]))
                            g = min(b["h"][i] - abs(u[i]) for i in range(3))
                            if g > margines:
                                cel = b["n"] if b["zrodlo"] == "cialo" else b["zrodlo"]
                                ile, gm = licz.get((co, n, cel), (0, 0.0))
                                licz[(co, n, cel)] = (ile + 1, max(gm, g))
            for (co, n, cel), (ile, gm) in sorted(licz.items()):
                w["bron" if co in BRON else "konczyny"].append((f, co, n, cel, ile, round(gm, 3)))
            dno = 1e9
            for kosc, pkt in ciala:                           # najniższy punkt samego ciała (stopy, leżenie)
                R, t = W[kosc]
                for q in pkt:
                    dno = min(dno, R[1][0] * q[0] + R[1][1] * q[1] + R[1][2] * q[2] + t[1])
            if dno < w["najnizej_cialo"][0]:
                w["najnizej_cialo"] = (round(dno, 3), f)
            if dno < w["najnizej"][0]:
                w["najnizej"] = (round(dno, 3), f)
            if f == kl.dlugosc:
                w["koniec"] = round(dno, 3)
        wynik[kl.nazwa] = w
    return wynik


def _wypisz_kontrole(wynik):
    """Wypisuje wynik kontroli; zwraca liczbę klatek z błędem (broń albo dłoń/przedramię w głowie; przedramię i dłoń
    przy tułowiu i biodrach to uwaga — tak liczy się też dawny model)."""
    zle = 0
    for nazwa, w in wynik.items():
        kb = sorted({x[0] for x in w["bron"]})
        glowa = [x for x in w["konczyny"] if x[2] == "Head"]
        kg = sorted({x[0] for x in glowa})
        zle += len(set(kb) | set(kg))
        print("%-17s %3d kl.  broń w głowie, tułowiu, biodrach: %s" % (
            nazwa, w["klatki"], "BRAK" if not kb else "%d kl., najgłębiej %.2f studa, np. %s" % (
                len(kb), max(x[5] for x in w["bron"]), w["bron"][:3])))
        print("%-17s          dłoń / przedramię w głowie: %s" % ("", "BRAK" if not kg else "%d kl., najgłębiej %.2f, "
                                                                 "np. %s" % (len(kg), max(x[5] for x in glowa), glowa[:3])))
        tul = [x for x in w["konczyny"] if x[2] != "Head"]
        print("%-17s          dłoń / przedramię w tułowiu i biodrach (uwaga): %s" % ("", "BRAK" if not tul else
              "%d kl., najgłębiej %.2f, np. %s" % (len({x[0] for x in tul}), max(x[5] for x in tul), tul[:3])))
        print("%-17s          najniższy punkt: ciało y = %.3f (kl. %d), z bronią y = %.3f (kl. %d); ostatnia klatka: "
              "ciało y = %.3f" % ("", w["najnizej_cialo"][0], w["najnizej_cialo"][1], w["najnizej"][0],
                                  w["najnizej"][1], w["koniec"]))
    return zle


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--kontrola" in sys.argv:
        # --stroj <nazwa> — jeden strój z STROJE (domyślnie wszystkie); pozostałe argumenty bez „--” — wybrane klipy
        argumenty = sys.argv[1:]
        stroje = list(STROJE)
        if "--stroj" in argumenty:
            i = argumenty.index("--stroj")
            stroje = [argumenty[i + 1]]
            del argumenty[i:i + 2]
        wybrane = [a for a in argumenty if not a.startswith("--")]
        zle = 0
        for s in stroje:
            print("=== strój „%s” (%s): %s" % (s, NAZWY_STROJOW[s], ", ".join(STROJE[s]) or "bez przedmiotów"))
            zle += _wypisz_kontrole(kontrola(stroj(s), klipy_=wybrane or None))
        sys.exit(1 if zle else 0)
    zbuduj()
