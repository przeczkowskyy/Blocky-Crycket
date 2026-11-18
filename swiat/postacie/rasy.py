# -*- coding: utf-8 -*-
"""RASY POSTACI — wspólny kod i dane sześciu ras (D-079, D-080, D-104; opis i pytania: swiat/postacie/RASY.md).

Status: propozycja, nie kanon. Zbudowane i obejrzane w Blenderze jest wszystkie sześć ras: elf i ork (pilotaż A1),
mroczny elf, demon, goblin i półbóg (etap A2) — moduły rasa_<id>.py. Roblox Studio: nic nie było robione.

Założenia (propozycja prowadzącego, RASY.md pkt 1):
  1. Rasa = ciało typu „czlowiek” na klockach, kościach, zaczepach i stawach gołego Rycerza i Zwiadowcy
     (WYMIARY = rycerz.WYMIARY). Każdy przedmiot „czlowiek” pasuje bez przeróbek (ekwipunek.ubierz), a klipy klas
     działają bez przeliczania.
  2. Rasę odróżniają: paleta skóry, twarz, uszy, włosy, rogi, kły, nos, ogon, aureola i kolor spodenek. Dodatki są
     sztywnymi bryłami na istniejących kościach (bez nowych kości).
  3. Skala rasy (ork 1,08, goblin 0,88) jest DANĄ (RASY[...]["skala"], atrybut Postac.skala_rasy) — nie jest
     wypieczona w klocki; pokazuje ją plansza skali (rasy_plansze.py), w grze byłaby to skala całego modelu.
  4. Strój bazowy z rzutów: lniana koszula z krótkim rękawem i wycięciem w serek, spodenki w kolorze rasy, brązowe
     buty. To warstwa 0 ciała (bryły „golas”): powłoka przedmiotu na tej samej kości ją zdejmuje — zbroja koszulę,
     spodnie spodenki, a przedmiot ze slotu Boots brązowe buty.
  5. Cechy rasy (twarz, uszy, kły, rogi, ogon, aureola) NIE mają znacznika „golas” (mają „cecha”): nie znikają
     pod żadną powłoką.
     Włosy są akcesorium ciała ze znacznikiem „Wlosy” (hełm i kaptur je chowają), jak rycerz_wlosy.
  6. Klipy: idle, chod i wiwat skopiowane (kanały = deepcopy, bez przeliczania) z ciała odniesienia człowieka —
     rycerz.postac_odniesienia(). W grze rasa gra klipy swojej klasy (te same kości).

API (moduł rasy rasa_<id>.py tylko je wywołuje):
  cialo(rasa)      gołe ciało rasy „rasa_<id>_cialo” z trzema klipami (zaczepy_ekwipunku=True: + 15 zaczepów Ekw…)
  model(rasa)      to samo ciało jako model główny „rasa_<id>” (zbuduj() modułu rasy)
  stroj(rasa, n)   przymiarka: rasa w komplecie Rycerza albo Zwiadowcy (STROJE)
  warianty(rasa)   modele dla przebuduj.py (wynik/rasa_<id>/ekwipunek/)
  w_skali(p)       kopia modelu pomnożona przez skalę rasy (tylko do planszy skali)
  test bez Blendera: python -B swiat/postacie/biblioteka/test_rasy.py
"""
import copy
import math
import os
import sys

if __name__ == "__main__":                                       # uruchomienie wprost: korzeń repozytorium na ścieżce
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from swiat.postacie import rycerz as _rycerz
from swiat.postacie import zwiadowca as _zwiadowca
from swiat.postacie.biblioteka.postac import R15_KOSCI, Akcesorium, Postac
from swiat.postacie.ekwipunek import kopiuj_klipy, ubierz, zaczep_ekwipunku

CIALO_TYP = "czlowiek"
WYMIARY = _rycerz.WYMIARY                    # te same klocki co goły Rycerz i Zwiadowca (EKWIPUNEK.md pkt 1)
ZRODLO_KLIPOW = "rycerz"                     # ciało odniesienia człowieka: rycerz.postac_odniesienia()
KLIPY = ("idle", "chod", "wiwat")            # spoczynek, chód, wiwat — nazwy jak w klipach Rycerza
RZUTY = "assets/processed/RaceTurnarounds"   # rysunki referencyjne Pawła (cztery widoki)
IKONY = "assets/processed/RaceSelect"

# stroje do przymiarki (przebuduj.py -> wynik/rasa_<id>/ekwipunek/): przedmioty „czlowiek” obu bohaterów
STROJE = {"golas": (), "rycerz": tuple(_rycerz.KANON), "zwiadowca": tuple(_zwiadowca.KANON)}
NAZWY_STROJOW = {"golas": "strój bazowy rasy", "rycerz": "komplet Rycerza", "zwiadowca": "komplet Zwiadowcy"}
PLANSZA_ZBIORCZA = ("golas", "rycerz", "zwiadowca")

# kolory wspólne wszystkich ras: len koszuli jak u gołego Rycerza, brązowe buty z rzutów
PALETA_WSPOLNA = {"len": "EDE3CC", "len_cien": "D3C4A2", "but": "8E5B33", "but_ciemny": "5E3A1A",
                  "but_jasny": "A9703F"}

# --------------------------------------------------------------------------- dane sześciu ras (jedno miejsce)
# skala      jednolita skala całej postaci (propozycja); klocki zostają te same
# paleta     skóra, włosy, oczy, spodenki… (klucze używane przez bryły tej rasy)
# glowa      cechy głowy: twarz, uszy, wlosy, kly, rogi, nos, aureola; ogon siedzi na biodrach (LowerTorso)
# spodenki   opis koloru z rzutu / zamówienia; zbudowana = jest moduł rasa_<id>.py obejrzany w renderze
RASY = {
    "elf": {
        "nazwa": "Elf", "zbudowana": True, "skala": 1.0,
        "rzut": RZUTY + "/elf.jpg", "ikona": IKONY + "/RaceElf.png",
        "paleta": {"skora": "F9CFAE", "skora_cien": "E3A988", "ucho_srodek": "EDA690", "usta": "8A4A36",
                   "wlosy": "F4BC2E", "wlosy_cien": "D6921A", "wlosy_blask": "FFDD6E", "oko": "3FA650",
                   "brew": "C48A22", "spodenki": "A6DA7E", "spodenki_cien": "7DBB5B"},
        "glowa": {"twarz": "lagodna", "uszy": "dlugie", "wlosy": "dlugie", "kly": None, "rogi": None,
                  "nos": "maly", "aureola": None},
        "ogon": None, "spodenki": "jasnozielone",
        "opis": "jasna skóra, długie spiczaste uszy na boki, długie złote włosy do łopatek z przedziałkiem, "
                "zielone oczy, jasnozielone spodenki",
    },
    "ork": {
        "nazwa": "Ork", "zbudowana": True, "skala": 1.08,
        "rzut": RZUTY + "/ork.jpg", "ikona": IKONY + "/RaceOrc.png",
        "paleta": {"skora": "8D9B35", "skora_cien": "6E7A27", "skora_ciemna": "4F5A1D", "ucho_srodek": "6E7A27",
                   "usta": "2A2A1C", "wlosy": "25222D", "wlosy_cien": "3D3948", "wiazanie": "8B5A2B",
                   "bialko": "F2EBCB", "kiel": "F6EFD9", "brew": "25222D",
                   "spodenki": "9C6B3C", "spodenki_cien": "7A5230"},
        "glowa": {"twarz": "ork", "uszy": "krotkie", "wlosy": "kok", "kly": "dolne", "rogi": None,
                  "nos": "szeroki", "aureola": None},
        "ogon": None, "spodenki": "brązowe (zamówienie; na rzucie wyszły wielokolorowe)",
        "opis": "oliwkowa skóra, dwa kły z dolnej szczęki, czarny kok na czubku głowy, grube brwi, krótkie "
                "spiczaste uszy, masywna szczęka; brązowe spodenki",
    },
    "mroczny_elf": {
        "nazwa": "Mroczny elf", "zbudowana": True, "skala": 1.0,
        "rzut": RZUTY + "/mroczny_elf.jpg", "ikona": IKONY + "/RaceDarkElf.png",
        "paleta": {"skora": "8E8AB6", "skora_cien": "6F6B98", "ucho_srodek": "7A76A4", "usta": "3B3760",
                   "wlosy": "CACADD", "wlosy_cien": "A3A3BD", "wlosy_blask": "ECECF7", "oko": "8E5BD0",
                   "brew": "B9B9CC", "spodenki": "5B2C82", "spodenki_cien": "44205F"},
        "glowa": {"twarz": "lagodna", "uszy": "dlugie", "wlosy": "dlugie", "kly": None, "rogi": None,
                  "nos": "maly", "aureola": None},
        "ogon": None, "spodenki": "fioletowe",
        "opis": "jak elf: skóra lawendowo-szara, długie srebrne włosy, fioletowe oczy i spodenki",
    },
    "demon": {
        "nazwa": "Demon", "zbudowana": True, "skala": 1.0,
        "rzut": RZUTY + "/demon.jpg", "ikona": IKONY + "/RaceDemon.png",
        "paleta": {"skora": "CC3650", "skora_cien": "9E2439", "usta": "5A1020", "rogi": "2B2530",
                   "rogi_cien": "3A3442", "oko": "FFC83A", "oko_blask": "FFF2B0", "kiel": "F6EFD9",
                   "brew": "5A1020", "rumieniec": "E8667E",
                   "spodenki": "2A2730", "spodenki_cien": "3F3B47"},
        "glowa": {"twarz": "demon", "uszy": None, "wlosy": None, "kly": "jeden", "rogi": "male",
                  "nos": None, "aureola": None},
        "ogon": "z_grotem", "spodenki": "czarne",
        "opis": "czerwona skóra, czarne rogi, ogon z grotem, złote świecące oczy, jeden kieł, głowa-klocek bez "
                "włosów; czarne spodenki (ikona wyboru rasy ma spiczaste uszy, rzut ich nie ma)",
    },
    "goblin": {
        "nazwa": "Goblin", "zbudowana": True, "skala": 0.88,
        "rzut": RZUTY + "/goblin.jpg", "rzut_wariant2": RZUTY + "/goblin_wariant2.jpg",
        "ikona": IKONY + "/RaceGoblin.png",
        "paleta": {"skora": "C6D92E", "skora_cien": "9DB01F", "ucho_srodek": "9DB01F", "usta": "2A2A1C",
                   "nos": "E9B93A", "zeby": "F4F1EA", "brew": "2A2A1C",
                   "spodenki": "F06A22", "spodenki_cien": "C94E12"},
        "glowa": {"twarz": "goblin", "uszy": "wielkie", "wlosy": None, "kly": None, "rogi": None,
                  "nos": "dlugi", "aureola": None},
        "ogon": None, "spodenki": "pomarańczowe",
        "opis": "żółtozielona skóra, wielkie uszy na boki, długi nos, szeroki uśmiech z zębami, głowa bez włosów; "
                "pomarańczowe spodenki (dwa warianty rzutu — wybór do decyzji)",
    },
    "polbog": {
        "nazwa": "Półbóg", "zbudowana": True, "skala": 1.0,
        "rzut": RZUTY + "/polbog.jpg", "ikona": IKONY + "/RaceDemigod.png",
        "paleta": {"skora": "F2B63C", "skora_cien": "D08F22", "usta": "8A5A14", "wlosy": "F0DDB0",
                   "wlosy_cien": "D4BA84", "wlosy_blask": "FFF3D2", "oko": "36B4FF", "brew": "D4BA84",
                   "powieka": "8A5A14",
                   "aureola": "FFC62E", "spodenki": "F4F4FA", "spodenki_cien": "F2C230"},
        "glowa": {"twarz": "lagodna", "uszy": None, "wlosy": "fale", "kly": None, "rogi": None,
                  "nos": "maly", "aureola": "pierscien"},
        "ogon": None, "spodenki": "białe ze złotą lamówką",
        "opis": "złota skóra, aureola nad głową, jasne falowane włosy, świecące niebieskie oczy; białe spodenki "
                "ze złotą lamówką (wygląd zależy od pytania 47 / D-080)",
    },
}
ZBUDOWANE = tuple(r for r, d in RASY.items() if d["zbudowana"])
POLA_RASY = ("nazwa", "zbudowana", "skala", "rzut", "ikona", "paleta", "glowa", "ogon", "spodenki", "opis")
POLA_GLOWY = ("twarz", "uszy", "wlosy", "kly", "rogi", "nos", "aureola")
POLA_PALETY = ("skora", "skora_cien", "usta", "brew", "spodenki", "spodenki_cien")


def id_rasy(rasa):
    """Id modelu rasy (i nazwa modułu): rasa_<id>."""
    return "rasa_" + rasa


def paleta(rasa):
    """Paleta wspólna + paleta rasy (klucze kolorów brył)."""
    return dict(PALETA_WSPOLNA, **RASY[rasa]["paleta"])


def _postac(rasa, id, nazwa):
    """Postać R15 o klockach ciała „czlowiek” (kości, stawy i 18 zaczepów jak goły Rycerz), jeszcze bez brył."""
    return Postac(id, nazwa, typ="r15", faza=0.05, paleta=paleta(rasa), wymiary=WYMIARY)


# --------------------------------------------------------------------------- strój bazowy (warstwa 0, „golas”)
def _stroj_bazowy(p, buty=True):
    """Klocki ciała i strój bazowy z rzutów: lniana koszula z krótkim rękawem i wycięciem w serek, spodenki
    w kolorze rasy, brązowe buty. Odległości od ściany klocka jak u gołego Rycerza (EKWIPUNEK.md pkt 1): koszula
    0,02–0,035, spodenki 0,01 — żadnych wcięć. buty=False: bose stopy w kolorze skóry (jak goły Rycerz)."""
    p.cialo({"glowa": "skora", "tulow": "len", "pas": "spodenki", "ramiona": "skora", "dlonie": "skora",
             "nogi": "skora", "stopy": "but" if buty else "skora"})
    with p.na("UpperTorso", od="srodek"):                         # koszula: wycięcie w serek z rozcięciem, rąbek
        w, h, d = p.wymiary("UpperTorso")
        z = d / 2
        p.ostroslup("Dekolt obszycie", (0, h / 2 - 0.24, z + 0.01), (0.66, 0.48, 0.03), "len_cien", "matowy",
                    rot=(0, 0, 180), gora=(0.0, 0.03), faza=0.0)
        p.ostroslup("Dekolt", (0, h / 2 - 0.19, z + 0.02), (0.48, 0.38, 0.03), "skora", "matowy",
                    rot=(0, 0, 180), gora=(0.0, 0.03), faza=0.0)
        p.blok("Dekolt rozciecie", (0, h / 2 - 0.5, z + 0.02), (0.04, 0.14, 0.03), "len_cien", "matowy", faza=0.0)
        p.blok("Rabek koszuli", (0, -h / 2 + 0.07, 0), (w + 0.04, 0.12, d + 0.04), "len_cien", "matowy", faza=0.02)
    with p.na("LowerTorso", od="srodek"):                         # spodenki: ściągacz (0,01 nad klockiem)
        w, h, d = p.wymiary("LowerTorso")
        p.blok("Sciagacz", (0, h / 2 - 0.08, 0), (w + 0.02, 0.14, d + 0.02), "spodenki_cien", "matowy", faza=0.02)
    for strona in ("Left", "Right"):
        with p.na(strona + "UpperArm", od="srodek"):              # krótki szeroki rękaw (do 2/3 ramienia)
            w, h, d = p.wymiary(strona + "UpperArm")
            p.blok("Rekaw", (0, h / 2 - 0.28, 0), (w + 0.04, 0.6, d + 0.04), "len", "matowy", faza=0.04)
            p.blok("Rekaw rabek", (0, h / 2 - 0.62, 0), (w + 0.04, 0.1, d + 0.04), "len_cien", "matowy", faza=0.02)
        with p.na(strona + "UpperLeg", od="srodek"):              # nogawka spodenek prawie do kolana
            w, h, d = p.wymiary(strona + "UpperLeg")
            # góra nogawki 0,02 nad klockiem jak u gołych bohaterów (poły tuniki kończą się 0,01 nad nim)
            p.blok("Nogawka", (0, h / 2 - 0.295, 0), (w + 0.02, 0.63, d + 0.02), "spodenki", "matowy", faza=0.04)
            p.blok("Nogawka rabek", (0, h / 2 - 0.62, 0), (w + 0.04, 0.08, d + 0.04), "spodenki_cien", "matowy",
                   faza=0.02)
        with p.na(strona + "Foot", od="srodek"):
            w, h, d = p.wymiary(strona + "Foot")
            if buty:                                              # niski brązowy but: podeszwa, nosek, cholewka
                p.blok("Podeszwa", (0, -h / 2 + 0.04, 0), (w + 0.04, 0.08, d + 0.04), "but_ciemny", "matowy",
                       faza=0.0)
                p.blok("Nosek", (0, -0.01, d / 2 + 0.015), (w - 0.14, 0.2, 0.05), "but_jasny", "matowy", faza=0.02)
                p.blok("Cholewka", (0, h / 2 - 0.03, -(d - w) / 2), (w + 0.06, 0.08, w + 0.06), "but_ciemny",
                       "matowy", faza=0.02)
            else:                                                 # bosa stopa: zarys palców (jak goły Rycerz)
                for i in (-1, 0, 1):
                    p.blok("Palec", (i * 0.3, -h / 2 + 0.075, d / 2 + 0.01), (0.035, 0.13, 0.03), "skora_cien",
                           "matowy", faza=0.0)
    for c in p.czesci:
        c["golas"] = True                                         # warstwa 0: zdejmuje ją powłoka na tej kości


# --------------------------------------------------------------------------- cechy głowy (nie znikają)
def _belka(p, nazwa, a, b, grub, kolor, mat="zwykly", faza=None, zapas=0.06):
    """Klocek od punktu a do punktu b (oś Y klocka wzdłuż odcinka), grub = (szer, głęb) — do łamanych z kilku
    klocków: rogi, ogon. zapas wydłuża klocek, żeby sąsiednie odcinki zachodziły na siebie w zgięciu."""
    v = [b[i] - a[i] for i in range(3)]
    dl = math.sqrt(sum(c * c for c in v))
    u = [c / dl for c in v]
    rz = -math.degrees(math.asin(max(-1.0, min(1.0, u[0]))))
    rx = math.degrees(math.atan2(u[2], u[1]))
    sr = [(a[i] + b[i]) / 2 for i in range(3)]
    return p.blok(nazwa, sr, (grub[0], dl + zapas, grub[1]), kolor, mat, rot=(rx, 0, rz), faza=faza)


def _uszy(p, dl, wys, gl, y, kat_gora, kat_tyl, wysun=0.0, wglab=0.05):
    """Spiczaste uszy po bokach głowy (bryły kości Head). dl = długość na zewnątrz, wys = wysokość nasady,
    gl = grubość, y = wysokość środka nasady od środka głowy, kat_gora / kat_tyl = odchylenie czubka w górę
    i do tyłu (stopnie), wysun = przesunięcie czubka ku górnej krawędzi ucha (górna krawędź bardziej pozioma),
    wglab = o ile nasada siedzi w głowie (więcej przy uszach stromo w górę)."""
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            # układ ucha: +Y = od głowy na zewnątrz (i w górę), +Z ≈ przód; lokalne +X lewego ucha patrzy w dół
            with p.uklad(pos=(zn * (w / 2 - wglab), y, 0.0), obrot=(0, zn * kat_tyl, -zn * (90 - kat_gora))):
                p.ostroslup("Ucho " + s, (0, dl / 2, 0), (wys, dl, gl), "skora", gora=(0.0, gl * 0.45),
                            przes_gory=(-zn * wysun, 0.0), faza=0.0)
                p.ostroslup("Ucho srodek " + s, (0, dl * 0.4, gl / 2 + 0.005), (wys * 0.5, dl * 0.62, 0.03),
                            "ucho_srodek", "matowy", gora=(0.0, 0.03), przes_gory=(-zn * wysun * 0.5, 0.0), faza=0.0)


def _oczy(p, x=0.31, y=0.07, bialko=(0.37, 0.31), teczowka=(0.25, 0.27), swieca=False):
    """Oczy „z rzutów”: białko, kolorowa tęczówka (paleta „oko”), źrenica, błysk i górna powieka (kolor „powieka”
    z palety rasy albo tusz). swieca=True: całe oko świeci kolorem „oko” (półbóg), bez źrenicy — emisja trafia do
    tekstury-palety modelu."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    powieka = "powieka" if "powieka" in p.paleta else "tusz"
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            if swieca:
                p.blok("Oko " + s, (zn * x, y, z + 0.02), (bialko[0], bialko[1], 0.04), "oko", "swiecacy", faza=0.03)
                p.blok("Powieka " + s, (zn * x, y + bialko[1] / 2 + 0.015, z + 0.03), (bialko[0] + 0.04, 0.05, 0.06),
                       powieka, "matowy", faza=0.0, rot=(0, 0, zn * 4))
                p.blok("Blysk " + s, (zn * x - 0.05, y + 0.03, z + 0.045), (0.12, 0.1, 0.02), "bialy", "swiecacy",
                       faza=0.0)
            else:
                p.blok("Bialko " + s, (zn * x, y, z + 0.015), (bialko[0], bialko[1], 0.04), "bialy", "polysk",
                       faza=0.03)
                p.blok("Teczowka " + s, (zn * x, y - 0.01, z + 0.03), (teczowka[0], teczowka[1], 0.04), "oko",
                       "polysk", faza=0.03)
                p.blok("Zrenica " + s, (zn * x, y - 0.01, z + 0.045), (0.12, 0.15, 0.03), "tusz", "polysk", faza=0.0)
                p.blok("Blysk " + s, (zn * x - 0.06, y + 0.06, z + 0.06), (0.07, 0.07, 0.02), "bialy", faza=0.0)
                p.blok("Powieka " + s, (zn * x, y + bialko[1] / 2 + 0.015, z + 0.03), (bialko[0] + 0.04, 0.05, 0.06),
                       powieka, faza=0.0, rot=(0, 0, zn * 4))


def _twarz_lagodna(p, swieca=False):
    """Twarz elfa, mrocznego elfa i półboga: duże oczy z kolorową tęczówką (półbóg: świecące), cienkie brwi
    w kolorze włosów, mały nos, łagodny zamknięty uśmiech z uniesionymi kącikami."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    if swieca:
        _oczy(p, x=0.31, y=0.08, bialko=(0.32, 0.22), swieca=True)
    else:
        _oczy(p)
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Brew " + s, (zn * 0.32, 0.31 if swieca else 0.36, z + 0.03), (0.38, 0.08, 0.06), "brew",
                   "matowy", rot=(0, 0, zn * 6), faza=0.02)
            p.blok("Kacik " + s, (zn * 0.24, -0.385, z + 0.02), (0.1, 0.05, 0.04), "usta", "matowy",
                   rot=(0, 0, zn * 32), faza=0.0)
        p.blok("Nos", (0, -0.1, z + 0.04), (0.14, 0.2, 0.1), "skora_cien", "matowy", faza=0.03)
        p.blok("Usta", (0, -0.41, z + 0.02), (0.42, 0.05, 0.04), "usta", "matowy", faza=0.0)
        p.blok("Warga", (0, -0.5, z + 0.015), (0.2, 0.04, 0.03), "skora_cien", "matowy", faza=0.0)


def _twarz_ork(p):
    """Twarz orka: szersza, wysunięta szczęka (masywność oddana głową — klocki ciała zostają), wał brwiowy
    z grubymi skośnymi brwiami, małe oczy, szeroki nos, szeroka kreska ust i dwa kły z dolnej szczęki."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    zs = 0.2 + 0.6                                                  # przednia ściana szczęki (0,075 przed twarzą)
    with p.na("Head", od="srodek"):
        p.blok("Szczeka", (0, -0.46, 0.2), (w + 0.1, 0.56, 1.2), "skora", faza=0.07)
        # wał i brwi mieszczą się w otworze twarzy hełmu Rycerza (policzki hełmu zaczynają się na x = ±0,60)
        p.blok("Wal brwiowy", (0, 0.3, z + 0.03), (1.18, 0.22, 0.1), "skora", faza=0.04)
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Brew " + s, (zn * 0.32, 0.3, z + 0.09), (0.5, 0.17, 0.06), "brew", "matowy",
                   rot=(0, 0, zn * 15), faza=0.02)
            p.blok("Bialko " + s, (zn * 0.32, 0.09, z + 0.015), (0.24, 0.13, 0.04), "bialko", "polysk", faza=0.02)
            p.blok("Zrenica " + s, (zn * 0.3, 0.09, z + 0.035), (0.13, 0.13, 0.03), "tusz", "polysk", faza=0.0)
            p.blok("Blysk " + s, (zn * 0.3 - 0.035, 0.115, z + 0.05), (0.04, 0.04, 0.02), "bialy", faza=0.0)
            p.blok("Nozdrze " + s, (zn * 0.1, -0.2, z + 0.15), (0.08, 0.05, 0.02), "skora_ciemna", "matowy",
                   faza=0.0)
            # kły: z dolnej szczęki w górę, czubek lekko na zewnątrz
            p.ostroslup("Kiel " + s, (zn * 0.36, -0.285, zs + 0.055), (0.14, 0.27, 0.11), "kiel", "polysk",
                        gora=(0.0, 0.0), przes_gory=(zn * 0.02, 0.0), faza=0.0)
        p.blok("Nos", (0, -0.1, z + 0.07), (0.42, 0.3, 0.16), "skora_cien", "matowy", faza=0.05)
        p.blok("Usta", (0, -0.42, zs + 0.01), (0.9, 0.06, 0.03), "usta", "matowy", faza=0.0)
        p.blok("Kacik L", (0.47, -0.39, zs + 0.01), (0.1, 0.06, 0.03), "usta", "matowy", rot=(0, 0, 30), faza=0.0)
        p.blok("Warga", (0, -0.55, zs + 0.01), (0.46, 0.05, 0.03), "skora_cien", "matowy", faza=0.0)


def _twarz_demon(p):
    """Twarz demona: złote świecące skośne oczy w ciemnej obwódce, skośne brwi, szeroki uśmiech w łuk, jeden kieł
    z górnej wargi (po lewej stronie postaci), bez nosa i uszu (głowa-klocek jak na rzucie)."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Oko obwodka " + s, (zn * 0.33, 0.1, z + 0.012), (0.38, 0.24, 0.03), "usta", "matowy",
                   rot=(0, 0, zn * 14), faza=0.03)
            p.blok("Oko " + s, (zn * 0.33, 0.1, z + 0.03), (0.28, 0.15, 0.04), "oko", "swiecacy",
                   rot=(0, 0, zn * 14), faza=0.03)
            p.blok("Blysk " + s, (zn * 0.33, 0.1, z + 0.055), (0.1, 0.08, 0.02), "oko_blask", "swiecacy", faza=0.0)
            p.blok("Brew " + s, (zn * 0.35, 0.31, z + 0.04), (0.48, 0.1, 0.07), "brew", "matowy",
                   rot=(0, 0, zn * 22), faza=0.02)
            p.blok("Usta bok " + s, (zn * 0.42, -0.33, z + 0.02), (0.3, 0.06, 0.04), "usta", "matowy",
                   rot=(0, 0, zn * 24), faza=0.0)
            p.blok("Kacik " + s, (zn * 0.58, -0.24, z + 0.02), (0.1, 0.06, 0.04), "usta", "matowy",
                   rot=(0, 0, zn * 50), faza=0.0)
            p.blok("Rumieniec " + s, (zn * 0.6, -0.08, z + 0.01), (0.14, 0.07, 0.03), "rumieniec", "matowy", faza=0.0)
        p.blok("Usta", (0, -0.39, z + 0.02), (0.6, 0.06, 0.04), "usta", "matowy", faza=0.0)
        p.ostroslup("Kiel", (0.24, -0.47, z + 0.04), (0.12, 0.16, 0.05), "kiel", "polysk", rot=(0, 0, 180),
                    gora=(0.0, 0.0), faza=0.0)


def _twarz_goblin(p):
    """Twarz goblina (pierwszy rzut): grube skośne brwi, małe czarne oczy, długi nos opadający nad usta
    z żółtawym czubkiem, szeroki uśmiech z rzędem zębów i uniesionymi kącikami."""
    w, h, d = p.wymiary("Head")
    z = d / 2
    with p.na("Head", od="srodek"):
        for zn, s in ((1, "L"), (-1, "P")):
            p.blok("Oko " + s, (zn * 0.36, 0.13, z + 0.02), (0.17, 0.2, 0.05), "tusz", "polysk", faza=0.03)
            p.blok("Blysk " + s, (zn * 0.36 - 0.03, 0.18, z + 0.05), (0.05, 0.05, 0.02), "bialy", faza=0.0)
            p.blok("Brew " + s, (zn * 0.38, 0.33, z + 0.04), (0.5, 0.12, 0.07), "brew", "matowy",
                   rot=(0, 0, zn * 22), faza=0.02)
            p.blok("Kacik " + s, (zn * 0.57, -0.3, z + 0.02), (0.2, 0.07, 0.04), "usta", "matowy",
                   rot=(0, 0, zn * 42), faza=0.0)
            p.blok("Policzek " + s, (zn * 0.62, -0.12, z + 0.01), (0.16, 0.05, 0.03), "skora_cien", "matowy",
                   rot=(0, 0, zn * 30), faza=0.0)
        p.blok("Usta", (0, -0.43, z + 0.02), (1.02, 0.24, 0.05), "usta", "matowy", faza=0.03)
        p.blok("Zeby", (0, -0.385, z + 0.05), (0.9, 0.13, 0.03), "zeby", faza=0.0)
        for i in (-1.5, -0.5, 0.5, 1.5):
            p.blok("Zab przerwa", (i * 0.225, -0.385, z + 0.07), (0.025, 0.13, 0.02), "usta", "matowy", faza=0.0)
        # nos: nasada między oczami, grzbiet wysunięty do przodu i w dół, żółtawy czubek nad ustami
        p.blok("Nos nasada", (0, 0.05, z + 0.08), (0.3, 0.3, 0.2), "skora", faza=0.06)
        p.blok("Nos", (0, -0.1, z + 0.27), (0.34, 0.36, 0.46), "skora", rot=(32, 0, 0), faza=0.08)
        p.blok("Nos czubek", (0, -0.27, z + 0.47), (0.36, 0.32, 0.28), "nos", rot=(42, 0, 0), faza=0.07)


def _kly_rogi_aureola(p, g):
    """Dodatki głowy: rogi demona (każdy z dwóch klocków i szpica, łuk na zewnątrz i z powrotem ku środkowi)
    i aureola półboga (świecący pierścień z dwunastu belek nad głową, pochylony do przodu). Sztywne bryły kości
    Head: zostają pod każdym strojem."""
    w, h, d = p.wymiary("Head")
    with p.na("Head", od="srodek"):
        if g["rogi"]:
            for zn, s in ((1, "L"), (-1, "P")):
                a, b, c, e = ((zn * 0.5, h / 2 - 0.06, 0.14), (zn * 0.68, h / 2 + 0.24, 0.14),
                              (zn * 0.66, h / 2 + 0.5, 0.14), (zn * 0.5, h / 2 + 0.78, 0.14))
                _belka(p, "Rog " + s, a, b, (0.32, 0.32), "rogi", faza=0.06)
                _belka(p, "Rog srodek " + s, b, c, (0.26, 0.26), "rogi_cien", faza=0.05)
                v = (e[0] - c[0], e[1] - c[1])
                p.ostroslup("Rog szpic " + s, ((c[0] + e[0]) / 2, (c[1] + e[1]) / 2, 0.14),
                            (0.22, math.hypot(*v) + 0.04, 0.22), "rogi",
                            rot=(0, 0, -math.degrees(math.atan2(v[0], v[1]))), gora=(0.0, 0.0), faza=0.0)
        if g["aureola"]:
            r, n = 0.62, 12
            with p.uklad(pos=(0, h / 2 + 0.68, 0), obrot=(16, 0, 0)):
                for i in range(n):
                    k = 2 * math.pi * i / n
                    p.blok("Aureola %d" % i, (r * math.sin(k), 0, r * math.cos(k)),
                           (2 * r * math.tan(math.pi / n) + 0.03, 0.08, 0.11), "aureola", "swiecacy",
                           rot=(0, math.degrees(k), 0), faza=0.02)


def _ogon(p):
    """Ogon demona z grotem — sztywna łamana z klocków na kości LowerTorso (bez nowych kości, bez znacznika
    „golas”, więc spodnie go nie zdejmują). Wychodzi ze środka pleców bioder, idzie do tyłu, w lewą stronę postaci
    i w dół poza obrys nogi (noga w chodzie go nie tnie), a grot zadziera do góry obok lewej łydki."""
    w, h, d = p.wymiary("LowerTorso")
    z = -d / 2
    pkt = ((0.0, -0.02, z + 0.08), (0.0, -0.06, z - 0.36), (0.56, -0.32, z - 0.42), (1.3, -0.78, z - 0.4),
           (1.56, -1.36, z - 0.36), (1.86, -1.5, z - 0.36), (2.06, -1.22, z - 0.36))
    with p.na("LowerTorso", od="srodek"):
        for i, gr in enumerate((0.2, 0.18, 0.16, 0.15, 0.14, 0.13)):
            _belka(p, "Ogon %d" % i, pkt[i], pkt[i + 1], (gr, gr), "skora", faza=0.04)
        a, b = pkt[-2], pkt[-1]
        v = (b[0] - a[0], b[1] - a[1])
        dl = math.hypot(*v)
        u = (v[0] / dl, v[1] / dl)
        p.ostroslup("Ogon grot", (b[0] + u[0] * 0.2, b[1] + u[1] * 0.2, b[2]), (0.46, 0.44, 0.1), "skora_cien",
                    rot=(0, 0, -math.degrees(math.atan2(u[0], u[1]))), gora=(0.0, 0.1), faza=0.0)


TWARZE = {"lagodna": _twarz_lagodna, "ork": _twarz_ork, "demon": _twarz_demon, "goblin": _twarz_goblin}
# uszy: dl, wys, gl, y, kat_gora, kat_tyl, wysun
USZY = {"dlugie": (0.92, 0.44, 0.16, 0.1, 24, 14, 0.14), "krotkie": (0.58, 0.42, 0.16, -0.08, 44, 10, 0.06, 0.1),
        "wielkie": (1.0, 0.8, 0.16, 0.1, 14, 10, 0.2)}


def _cechy_glowy(p, rasa):
    """Twarz, uszy, kły, rogi, nos, aureola — bryły kości Head bez znacznika „golas” (zostają w każdym stroju)."""
    g = RASY[rasa]["glowa"]
    if g["twarz"] == "lagodna":
        _twarz_lagodna(p, swieca=(rasa == "polbog"))
    else:
        TWARZE[g["twarz"]](p)
    if g["uszy"]:
        _uszy(p, *USZY[g["uszy"]])
    _kly_rogi_aureola(p, g)


# --------------------------------------------------------------------------- włosy (akcesorium ciała, znacznik Wlosy)
def _akc_wlosy(rasa):
    a = Akcesorium(id_rasy(rasa) + "_wlosy", "Włosy — " + RASY[rasa]["nazwa"], zaczep="HairAttachment", typ="Hair",
                   paleta=paleta(rasa), przymierz=False)
    a.znacznik = "Wlosy"                                          # hełm i kaptur (ukrywa=("Wlosy",)) je zdejmują
    return a


def wlosy_dlugie(rasa):
    """Długie proste włosy elfa i mrocznego elfa: schodkowa kopuła z przedziałkiem, grzywka rozczesana na boki,
    po bokach głowy trzy pasma różnej długości ze szpicami i skos przy skroni (ucho wychodzi między pasmami),
    pasma wzdłuż żuchwy i dwa pasma na pierś (poza obrysem twarzy), tył w warstwach: potylica, szeroka warstwa
    na ramionach i najdłuższa środkowa ze szpicem do łopatek. Układ zaczepu: (0, 0, 0) = środek górnej ściany
    głowy. Sztywne z głową (bez kości) — przy skłonie pasma wchodzą w tors."""
    a = _akc_wlosy(rasa)
    w, h, d = WYMIARY["Head"]
    x, z = w / 2, d / 2
    a.blok("Czupryna", (0, 0.09, -0.02), (w + 0.14, 0.24, d + 0.12), "wlosy", faza=0.08)
    a.blok("Czupryna gora", (0, 0.25, -0.04), (w - 0.16, 0.14, d - 0.14), "wlosy", faza=0.07)
    a.blok("Czupryna czubek", (0, 0.335, -0.06), (w - 0.62, 0.08, d - 0.5), "wlosy", faza=0.04)
    a.blok("Przedzialek", (0, 0.38, -0.02), (0.05, 0.03, 0.66), "wlosy_cien", "matowy", faza=0.0)
    for zn, s in ((1, "L"), (-1, "P")):
        a.blok("Grzywka " + s, (zn * 0.45, -0.13, z + 0.035), (0.86, 0.3, 0.09), "wlosy", rot=(0, 0, -zn * 16),
               faza=0.03)
        a.blok("Blask " + s, (zn * 0.42, -0.02, z + 0.085), (0.4, 0.05, 0.02), "wlosy_blask", rot=(0, 0, -zn * 16),
               faza=0.0)
        # bok: trzy pasma (od tyłu do skroni) coraz krótsze ku twarzy, dwa przednie zakończone szpicem
        for i, (zc, gl, dl, dx, kon) in enumerate(((-0.56, 0.42, 1.5, 0.05, 0.0), (-0.16, 0.46, 1.28, 0.08, 0.24),
                                                   (0.2, 0.36, 1.18, 0.05, 0.22))):
            a.blok("Bok %s%d" % (s, i), (zn * (x + dx), 0.02 - dl / 2, zc), (0.14, dl, gl), "wlosy", faza=0.05)
            if kon:
                a.ostroslup("Bok koniec %s%d" % (s, i), (zn * (x + dx), 0.03 - dl - kon / 2, zc),
                            (0.14, kon, gl), "wlosy", rot=(0, 0, 180), gora=(0.14, 0.0),
                            przes_gory=(0.0, -gl / 4), faza=0.0)
        a.blok("Bok cien " + s, (zn * (x + 0.125), -0.62, -0.37), (0.02, 1.1, 0.04), "wlosy_cien", "matowy", faza=0.0)
        a.ostroslup("Bok skron " + s, (zn * (x + 0.04), -0.43, 0.5), (0.12, 0.9, 0.26), "wlosy", rot=(180, 0, 0),
                    gora=(0.12, 0.0), przes_gory=(0.0, 0.13), faza=0.0)
        # pasma: wzdłuż żuchwy do przodu i w dół na pierś, przed ramieniem (poza obrysem twarzy, jak na rzucie)
        a.blok("Pasmo zuchwa " + s, (zn * (x + 0.04), -1.33, 0.59), (0.12, 0.32, 0.48), "wlosy", faza=0.04)
        a.blok("Pasmo przod " + s, (zn * (x - 0.03), -1.785, 0.76), (0.34, 0.73, 0.14), "wlosy", faza=0.05)
        a.ostroslup("Pasmo przod koniec " + s, (zn * (x - 0.03), -2.325, 0.76), (0.34, 0.36, 0.14), "wlosy",
                    rot=(0, 0, 180), gora=(0.0, 0.07), przes_gory=(zn * 0.09, 0.0), faza=0.0)
        a.blok("Pasmo przod cien " + s, (zn * (x - 0.11), -1.8, 0.835), (0.04, 0.62, 0.02), "wlosy_cien",
               "matowy", faza=0.0)
        a.blok("Pasmo przod krotkie " + s, (zn * (x + 0.2), -1.66, 0.74), (0.18, 0.46, 0.1), "wlosy", faza=0.04)
        a.ostroslup("Pasmo krotkie koniec " + s, (zn * (x + 0.2), -2.02, 0.74), (0.18, 0.28, 0.1), "wlosy",
                    rot=(0, 0, 180), gora=(0.0, 0.05), przes_gory=(zn * 0.05, 0.0), faza=0.0)
    # tył w warstwach: potylica (wypukła), szeroka warstwa na ramionach, najdłuższa środkowa ze szpicem
    a.blok("Tyl", (0, -0.55, -z - 0.12), (w + 0.2, 1.3, 0.28), "wlosy", faza=0.09)
    a.blok("Tyl potylica", (0, -0.42, -z - 0.3), (w - 0.14, 0.72, 0.14), "wlosy", faza=0.07)
    a.blok("Tyl ramiona", (0, -1.42, -z - 0.15), (w + 0.5, 0.86, 0.3), "wlosy", faza=0.1)
    a.blok("Tyl srodek", (0, -1.7, -z - 0.11), (w + 0.1, 0.9, 0.3), "wlosy", faza=0.08)
    a.ostroslup("Tyl szpic", (0, -2.375, -z - 0.11), (w + 0.1, 0.46, 0.3), "wlosy", rot=(0, 0, 180),
                gora=(0.3, 0.12), faza=0.0)
    for xk, dl in ((-0.42, 0.66), (0.44, 0.6)):
        a.blok("Pasmo tyl", (xk, -1.08 - dl / 2, -z - 0.305), (0.05, dl, 0.02), "wlosy_cien", "matowy", faza=0.0)
    a.blok("Blask tyl", (0, -0.24, -z - 0.375), (0.9, 0.09, 0.02), "wlosy_blask", faza=0.0)
    return a


def wlosy_kok(rasa):
    """Czarne włosy orka: czapa z klinem nad czołem, tył do karku, boki nad uszami i za nimi, baczki, a na czubku
    kok — obły węzeł związany brązowym rzemieniem, z kosmykiem opadającym łukiem za głowę (klocki z fazą)."""
    a = _akc_wlosy(rasa)
    w, h, d = WYMIARY["Head"]
    x, z = w / 2, d / 2
    a.blok("Czapa", (0, 0.07, -0.03), (w + 0.1, 0.2, d + 0.1), "wlosy", "matowy", faza=0.06)
    a.blok("Tyl", (0, -0.5, -z - 0.04), (w + 0.1, 1.0, 0.1), "wlosy", "matowy", faza=0.04)
    a.blok("Linia wlosow", (0, -0.05, z + 0.02), (w + 0.06, 0.14, 0.06), "wlosy", "matowy", faza=0.02)
    a.ostroslup("Klin nad czolem", (0, -0.2, z + 0.02), (0.5, 0.18, 0.06), "wlosy", "matowy", rot=(0, 0, 180),
                gora=(0.0, 0.06), faza=0.0)
    for zn, s in ((1, "L"), (-1, "P")):
        a.blok("Bok " + s, (zn * (x + 0.025), -0.29, -0.2), (0.06, 0.6, d - 0.42), "wlosy", "matowy", faza=0.02)
        a.blok("Bok tyl " + s, (zn * (x + 0.025), -0.78, -0.47), (0.06, 0.44, 0.5), "wlosy", "matowy", faza=0.02)
        a.blok("Baczek " + s, (zn * (x + 0.025), -0.68, 0.22), (0.06, 0.26, 0.14), "wlosy", "matowy", faza=0.0)
    # kok: rzemień, obły węzeł (kula z ośmiu ścian) i kosmyk z trzech coraz cieńszych klocków, łukiem za głowę
    a.walec("Kok rzemien", (0, 0.25, -0.28), (0.46, 0.14, 0.46), "wiazanie", "matowy")
    a.kula("Kok", (0, 0.58, -0.3), (0.7, 0.58, 0.7), "wlosy", "matowy", segm=8)
    a.blok("Kok pasmo", (0.0, 0.84, -0.3), (0.16, 0.06, 0.4), "wlosy_cien", "matowy", faza=0.02)
    a.blok("Kok kosmyk 1", (0, 0.68, -0.7), (0.4, 0.44, 0.36), "wlosy", "matowy", rot=(-108, 0, 0), faza=0.08)
    a.blok("Kok kosmyk 2", (0, 0.46, -0.98), (0.34, 0.42, 0.3), "wlosy", "matowy", rot=(-146, 0, 0), faza=0.07)
    a.blok("Kok kosmyk 3", (0, 0.16, -1.1), (0.26, 0.36, 0.22), "wlosy", "matowy", rot=(-172, 0, 0), faza=0.05)
    return a


def wlosy_fale(rasa):
    """Jasne falowane włosy półboga do karku: schodkowa kopuła, grzywka zaczesana na bok z dwóch fal, po bokach
    trzy fale na przemian wysunięte (zakrywają miejsce uszu), tył w dwóch warstwach z falistym dołem."""
    a = _akc_wlosy(rasa)
    w, h, d = WYMIARY["Head"]
    x, z = w / 2, d / 2
    a.blok("Czupryna", (0, 0.1, -0.02), (w + 0.2, 0.28, d + 0.18), "wlosy", faza=0.1)
    a.blok("Czupryna gora", (0.05, 0.28, -0.04), (w - 0.1, 0.16, d - 0.1), "wlosy", faza=0.08)
    a.blok("Czupryna fala", (-0.2, 0.37, 0.1), (0.7, 0.1, 0.8), "wlosy_blask", rot=(0, 14, 0), faza=0.04)
    # grzywka: dwie fale zaczesane w prawą stronę postaci (przedziałek po lewej)
    a.blok("Grzywka", (0.18, -0.12, z + 0.05), (1.0, 0.3, 0.12), "wlosy", rot=(0, 0, 12), faza=0.06)
    a.blok("Grzywka fala", (-0.52, -0.2, z + 0.05), (0.56, 0.3, 0.12), "wlosy", rot=(0, 0, -24), faza=0.06)
    a.blok("Grzywka blask", (0.2, -0.05, z + 0.115), (0.5, 0.05, 0.02), "wlosy_blask", rot=(0, 0, 12), faza=0.0)
    for zn, s in ((1, "L"), (-1, "P")):
        for i, (y, dx, gl, kolor) in enumerate(((-0.28, 0.08, d - 0.1, "wlosy"), (-0.66, 0.14, d - 0.2, "wlosy_cien"),
                                                (-1.02, 0.07, d - 0.36, "wlosy"))):
            a.blok("Fala %s%d" % (s, i), (zn * (x + dx), y, -0.12), (0.2, 0.46, gl), kolor, faza=0.08)
    a.blok("Tyl", (0, -0.5, -z - 0.1), (w + 0.24, 1.0, 0.24), "wlosy", faza=0.09)
    a.blok("Tyl dol", (0, -1.1, -z - 0.13), (w + 0.1, 0.5, 0.26), "wlosy", faza=0.09)
    for xk, wys in ((-0.6, 0.2), (0.0, 0.26), (0.58, 0.18)):
        a.blok("Tyl fala", (xk, -1.3 - wys / 2, -z - 0.13), (0.5, wys, 0.24), "wlosy_cien" if xk == 0.0
               else "wlosy", faza=0.07)
    return a


WLOSY = {"dlugie": wlosy_dlugie, "kok": wlosy_kok, "fale": wlosy_fale}


def wlosy(rasa):
    """Akcesorium włosów rasy (id rasa_<id>_wlosy, zaczep HairAttachment, znacznik „Wlosy”) albo None."""
    rodzaj = RASY[rasa]["glowa"]["wlosy"]
    return WLOSY[rodzaj](rasa) if rodzaj else None


# --------------------------------------------------------------------------- ciało rasy, klipy, stroje
def _golas(rasa, id, nazwa, zaczepy_ekwipunku=False, buty=True):
    """Ciało rasy bez klipów: klocki i strój bazowy (bryły „golas”), cechy rasy (zostają zawsze), włosy."""
    if rasa not in RASY:
        raise ValueError("Nieznana rasa %r (są: %s)" % (rasa, ", ".join(RASY)))
    p = _postac(rasa, id, nazwa)
    p.typ_ciala = CIALO_TYP
    p.rasa = rasa
    p.skala_rasy = float(RASY[rasa]["skala"])                     # dana, NIE Postac.skala (klocki bez zmian)
    _stroj_bazowy(p, buty=buty)
    n = len(p.czesci)
    _cechy_glowy(p, rasa)
    if RASY[rasa]["ogon"]:
        _ogon(p)
    for c in p.czesci[n:]:
        c["cecha"] = True                                         # cecha rasy: bez „golas”, zostaje w każdym stroju
    wl = wlosy(rasa)
    if wl is not None:
        p.zaloz(wl)                                               # osobna siatka (w FBX ciała), hełm ją chowa
    if zaczepy_ekwipunku:
        for kosc in R15_KOSCI:
            p.zaczep(zaczep_ekwipunku(kosc), kosc, p.srodek(kosc))
    return p


def cialo(rasa, zaczepy_ekwipunku=False, buty=True):
    """Gołe ciało rasy „rasa_<id>_cialo” z klipami KLIPY skopiowanymi z ciała odniesienia człowieka (Rycerz, klucze
    co do wartości). Poza renderów: spoczynek. zaczepy_ekwipunku=True — dodatkowo 15 zaczepów Ekw<Kosc>Attachment."""
    p = _golas(rasa, id_rasy(rasa) + "_cialo", RASY[rasa]["nazwa"] + " (ciało rasy)", zaczepy_ekwipunku, buty)
    kopiuj_klipy(_rycerz.postac_odniesienia(), p)
    p.klipy = [k for k in p.klipy if k.nazwa in KLIPY]
    p.poza_renderu = None
    return p


def model(rasa):
    """Model główny rasy (id rasa_<id>): ciało rasy w stroju bazowym, w pozie spoczynku."""
    return ubierz(cialo(rasa), [], id=id_rasy(rasa), nazwa=RASY[rasa]["nazwa"])


def przedmioty_klas():
    """{id: Przedmiot} — przedmioty „czlowiek” Rycerza i Zwiadowcy (do przymiarek; rasa nie ma własnych)."""
    return {x.id: x for x in _rycerz.przedmioty() + _zwiadowca.przedmioty()}


def stroj(rasa, nazwa, wszystkie=None):
    """Przymiarka: rasa w stroju ze STROJE (postać rasa_<id>_<strój>). Komplet z bronią stoi w pozie idle (kl. 0)."""
    ids = STROJE[nazwa]
    wszystkie = wszystkie or przedmioty_klas()
    p = ubierz(cialo(rasa), [wszystkie[i] for i in ids], id="%s_%s" % (id_rasy(rasa), nazwa),
               nazwa="%s — %s" % (RASY[rasa]["nazwa"], NAZWY_STROJOW[nazwa]))
    if ids:
        p.ustaw_poze_renderu("idle", 0)
    return p


def warianty(rasa, rodzaj="plansze"):
    """Modele dla przebuduj.py (wynik/rasa_<id>/ekwipunek/): „plansze” — strój bazowy i przymiarki ze STROJE;
    „eksport” — ciało rasy z zaczepami Ekw… (tylko klip idle; pozostałe: rasa_<id>__<klip>.fbx, te same kości)."""
    if rodzaj == "plansze":
        prz = przedmioty_klas()
        return [stroj(rasa, n, prz) for n in STROJE]
    if rodzaj == "eksport":
        c = cialo(rasa, zaczepy_ekwipunku=True)
        c.klipy = [k for k in c.klipy if k.nazwa == "idle"]
        return [c]
    raise ValueError("rodzaj: plansze albo eksport")


def ekwipunek_json(rasa):
    """Dane ciała rasy dla gry (propozycja; układ jak ekwipunek_json() bohaterów, bez własnych przedmiotów)."""
    r = RASY[rasa]
    return {"rasa": rasa, "id": id_rasy(rasa), "nazwa": r["nazwa"], "cialo": CIALO_TYP, "skala": r["skala"],
            "klipy": list(KLIPY), "zrodlo_klipow": ZRODLO_KLIPOW, "glowa": dict(r["glowa"]), "ogon": r["ogon"],
            "stroj_bazowy": {"koszula": "len", "spodenki": r["spodenki"], "buty": "brązowe (warstwa ciała)"},
            "wlosy": ({"id": id_rasy(rasa) + "_wlosy", "zaczep": "HairAttachment", "znacznik": "Wlosy"}
                      if r["glowa"]["wlosy"] else None),
            "stroje": {k: list(v) for k, v in STROJE.items()}, "przedmioty": []}


def w_skali(p, skala=None, id=None):
    """Kopia modelu pomnożona przez skalę rasy (kości, bryły, zaczepy i założone akcesoria) — TYLKO do planszy
    skali; eksporty i przymiarki zostają w skali 1 (klocki ciała „czlowiek”)."""
    s = float(p.skala_rasy if skala is None else skala)
    k = copy.deepcopy(p)
    k.id = id or (p.id + "_w_skali")
    k.skala = s
    for akc, *_ in k.zalozone:
        akc.skala = s
    return k


def slabosci(rasa):
    """Wspólne znane słabości modelu rasy (do raport.txt modułu rasy)."""
    r = RASY[rasa]
    return [
        "Status: propozycja (D-104, etapy A1–A2). Rasa = ciało typu „czlowiek” na klockach gołego Rycerza: "
        "sylwetka jest klockowa i szersza niż na rzucie (tułów z rękami ok. 0,78 wzrostu, na rysunku ok. 0,45) — "
        "to skutek założenia „te same klocki”, nie błąd głowy.",
        "Skala rasy %s jest tylko daną (RASY[...][\"skala\"], Postac.skala_rasy) — model, eksporty i przymiarki są "
        "w skali 1; skalę pokazuje plansza %s_skala.jpg." % (("%.2f" % r["skala"]).replace(".", ","), id_rasy(rasa)),
        "Klipy idle, chod i wiwat są skopiowane z Rycerza (prawa ręka w gotowości do miecza — bez broni wygląda jak "
        "uniesiona pięść). W grze rasa gra klipy swojej klasy; neutralnego spoczynku dla ekranu wyboru rasy nie ma.",
        "Brązowe buty są warstwą ciała (bryły „golas” na stopach): każdy przedmiot ze slotu Boots je zdejmuje. "
        "Goły Rycerz i Zwiadowca mają bose stopy — do decyzji, czy człowiek też dostaje buty (RASY.md).",
        "Włosy, uszy i inne dodatki głowy są sztywne (bez kości): przy skłonie i skręcie głowy długie pasma wchodzą "
        "w tors i ramiona. Hełm i kaptur chowają włosy w całości (znacznik „Wlosy”), uszy i kły zostają.",
        "Przymiarki (ekwipunek/%s_ekwipunek_plansza.jpg): %srękawice Zwiadowcy mają w powłoce klocek dłoni "
        "w kolorze skóry człowieka, więc na rasie o innej skórze dłonie robią się ludzkie. Pełna lista: RASY.md "
        "pkt 8." % (id_rasy(rasa), "uszy przechodzą przez boki hełmu Rycerza i kaptura Zwiadowcy; "
                    if r["glowa"]["uszy"] else ""),
        "Twarz bez mimiki; oczy, brwi i usta to bryły 0,02–0,09 studa przed ścianą głowy.",
        "Import do Roblox Studio nie był robiony (etap A1 jest tylko w Blenderze).",
    ]
