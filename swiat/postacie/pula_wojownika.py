# -*- coding: utf-8 -*-
"""PULA WOJOWNIKA Lv 1–10 — przedmioty kota-wojownika z arkuszy Pawła (24–25.11.2026): 5 arkuszy po 6 przedmiotów
(miecz, hełm, klata, rękawice, buty, pas). Status: propozycja (nazwy czekają na akceptację — pytanie 94; statystyki,
ceny i szanse dobierze kalkulator, tu ich nie ma).

Wzór: arkusze `zestaw_<nazwa>.jpg` (assets/refs/przedmioty_rycerz/ po połączeniu gałęzi; inny folder — zmienna
środowiska BC_WZORY_PRZEDMIOTOW). Opis puli: B&C/Gra/Przedmioty — pula Lv 1–10, 5 na slot (propozycja).md.
Karol (pytanie 93): „przedmiotami zajmuję się ja”; ciało to kot (D-145), przedmiot nie wchodzi na pyszczek.

Jak to jest zbudowane (kontrakt swiat/postacie/EKWIPUNEK.md, bez nowego systemu):
  - ciało: goły rudy kot = Kot-Mag (kot_mag.cialo(): te same klocki, kości, zaczepy i klipy) — tak jak Koci Rycerz
    z kot_klasy.py (D-145); plików kot_mag.py i kot_klasy.py nie zmieniamy, czytamy prywatną kopię kot_mag;
  - przedmiot = ekwipunek.Przedmiot (cialo „kot”, klasa „wojownik”): segmenty kostne w układzie ŚRODKA KLOCKA kości
    (powłoka zakrywa=True zdejmuje gołe futro tej kości) albo akcesorium na zaczepie;
  - właściciele powłok jak u kota: zbroja — UpperTorso, ramiona (UpperArm) i biodra (LowerTorso); rękawice — Hand;
    buty — Foot. Cholewa butów to NAKŁADKA na łydce (LowerLeg kota nie ma właściciela, futro zostaje pod spodem);
  - hełm i miecz na zaczepach HatAttachment / RightGripAttachment z korektą kota (KOREKTY_CHWYTU: kości nośne
    HatPivot i StaffPivot — w upadku hełm zsuwa się z głowy, a miecz wypada z łapy, jak kapelusz i kostur Kota-Maga);
  - hełm zostawia odkrytą twarz: obręcz kończy się nad oczami, osłony policzków stoją za płaszczyzną wąsów;
  - hełm ZAKRYWA USZY (Paweł 26.11.2026) i zostawia SYLWETKĘ KOTA (Karol 26.11.2026): niska kopuła jak na arkuszu
    i dwie osłony w kształcie kocich uszu w materiale hełmu (_oslony_uszu); osłony mieszczą całe uszy w pozie
    spoczynku (pomiar: --uszy), hełm deklaruje ukrywa=("Uszy",) — ubierz() zdejmuje gołe bryły kości
    LeftEar/RightEar (EKWIPUNEK.md pkt 14), w danych gry pole „ukrywa”: ["Uszy"];
  - broń deklaruje RODZAJ CHWYTU (Akcesorium.chwyt, Karol 26.11.2026): pięć mieczy puli to „miecz” (tabela rodzajów
    i korekty kota: swiat/postacie/chwyty.py, EKWIPUNEK.md pkt 15). Pochylenie dobrane kontrolą --ruch: broń
    względem wszystkich brył ciała i ziemi w chodzie i spoczynku (zapas ≥ 0,05) i ziemia w klipach walki.
Id: kot_rycerz_<zestaw>_<rzecz> (rzecz: helm, zbroja, pas, rekawice, buty, miecz); segment: <id>_<skrót kości>.
Bryły: same bloki, kliny i walce (bez ostrosłupów), żeby komplet mieścił się w limicie brył bohatera w świecie (220).

    python -B swiat/postacie/pula_wojownika.py               # lista przedmiotów, bryły i części Roblox (bez Blendera)
    python -B swiat/postacie/pula_wojownika.py --kontrola    # to samo + sprawdzian postaci w każdym komplecie
    python -B swiat/postacie/pula_wojownika.py --przenikanie # broń w głowie, hełmie i tułowiu w klipach walki kota
    python -B swiat/postacie/pula_wojownika.py --uszy        # czy hełmy mieszczą uszy kota (zapas w studach)
    python -B swiat/postacie/pula_wojownika.py --ruch        # broń vs całe ciało i ziemia, klatka po klatce, każdy
                                                             # klip kota (miecze zestawów + pozostałe rodzaje chwytu);
                                                             # upadek: broń, hełm i przedmiot lewej łapy z korektą
                                                             # upadku względem ziemi co pół klatki (kod 1 pod progiem)
    python -B swiat/postacie/pula_wojownika.py --razem       # plansza zbiorcza zrobionych zestawów (po przebudowach)
    python -B swiat/postacie/przebuduj.py pula_wojownika_giermek --bez-filmow     # modele, ikony, plansze zestawu
    python -B swiat/postacie/przebuduj.py pula_wojownika_chwyty --bez-filmow      # plansze: chwyty, hełm z uszami
"""
import copy
import importlib.util
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if __package__ in (None, ""):
    sys.path.insert(0, REPO)

from swiat.postacie import chwyty as CH  # noqa: E402
from swiat.postacie.biblioteka.postac import Akcesorium, katy_z_macierzy, macierz_obrotu, razy_wektor  # noqa: E402
from swiat.postacie.ekwipunek import ZNACZNIKI_CIALA, Przedmiot, ubierz  # noqa: E402

BOHATER = "kot_rycerz"
KLASY = ("wojownik",)
RZECZY = ("helm", "zbroja", "pas", "rekawice", "buty", "miecz")       # kolejność zakładania
UKLAD_ARKUSZA = ("miecz", "helm", "zbroja", "rekawice", "buty", "pas")  # kolejność rysunków na arkuszu Pawła
SLOTY = {"helm": ("Helmet", "Armor"), "zbroja": ("Chest", "Armor"), "pas": ("Belt", "Armor"),
         "rekawice": ("Gloves", "Armor"), "buty": ("Boots", "Armor"), "miecz": ("Weapon", "Weapons")}
# co przedmiot chowa na ciele (EKWIPUNEK.md pkt 14): hełm mieści uszy kota i je zdejmuje
UKRYWA = {"helm": ("Uszy",)}
# rodzaj chwytu broni każdego zestawu (chwyty.py): wszystkie pięć to broń jednoręczna trzymana jak miecz
CHWYT_BRONI = {"giermek": "miecz", "podworkowy": "miecz", "targowy": "miecz", "kuchenny": "miecz",
               "mleczarz": "miecz"}
# ikony przedmiotów z segmentów kostnych: przód lekko ku kamerze (kamera ikon patrzy z góry)
IKONA_OBROT = {"pas": (30, 0, 0), "buty": (0, 65, 0), "zbroja": (-10, 20, 0)}
PODGLADY = os.path.join(TU, "wynik", "_pula_wojownika")              # plansze <prefiks>*.jpg
PREFIKS_PLANSZ = "d2611_"          # 26.11.2026: hełmy z uszami i chwyt miecza; plansze noc2511_* zostają do porównania

# zestaw (arkusz) -> kolumna w tabeli Pawła, nazwa arkusza, plik wzoru, nazwy przedmiotów (propozycja, pytanie 94)
ZESTAWY = {
    "giermek": {"kolumna": 5, "nazwa": "Zestaw Giermka", "plik": "zestaw_giermek.jpg", "komplet": True,
                "przedmioty": {"miecz": "Miecz Giermka", "helm": "Hełm Giermka", "zbroja": "Kirys Giermka",
                               "pas": "Pas Giermka", "buty": "Trzewiki Giermka", "rekawice": "Rękawice Giermka"}},
    "podworkowy": {"kolumna": 1, "nazwa": "Podwórkowy", "plik": "zestaw_podworkowy.jpg", "komplet": False,
                   "przedmioty": {"miecz": "Miecz ze Sztachety", "helm": "Garnek po Zupie",
                                  "zbroja": "Napierśnik z Tary", "pas": "Sznurek do Snopków",
                                  "buty": "Kalosze Dziadka", "rekawice": "Rękawice z Dziurawych Skarpet"}},
    "targowy": {"kolumna": 2, "nazwa": "Targowy", "plik": "zestaw_targowy.jpg", "komplet": False,
                "przedmioty": {"miecz": "Tasak Rzeźnika Bolka", "helm": "Durszlak Bojowy",
                               "zbroja": "Kolczuga z Kapsli", "pas": "Pas z Uprzęży", "buty": "Trepy z Podkową",
                               "rekawice": "Rękawice Ogrodnika"}},
    "kuchenny": {"kolumna": 3, "nazwa": "Kuchenny", "plik": "zestaw_kuchenny.jpg", "komplet": False,
                 "przedmioty": {"miecz": "Pogrzebacz z Kominka", "helm": "Kask z Kubła",
                                "zbroja": "Napierśnik z Patelni", "pas": "Pas z Łańcucha Studni",
                                "buty": "Kapcie Pancerne", "rekawice": "Mitenki z Łańcucha"}},
    "mleczarz": {"kolumna": 4, "nazwa": "Mleczarz", "plik": "zestaw_mleczarz.jpg", "komplet": False,
                 "przedmioty": {"miecz": "Zardzewiały Kordelas", "helm": "Hełm z Bańki na Mleko",
                                "zbroja": "Przeszywanica Babci", "pas": "Pas z Klamrą Patelni",
                                "buty": "Buty Mleczarza", "rekawice": "Rękawice Szermiercze"}},
}

# jedna paleta dla wszystkich arkuszy (kolory z rysunków Pawła, przyciemnione / nasycone jak reszta gry)
PALETA = {
    "stal": "A9B3C4", "stal_cien": "8592A8", "stal_ciemna": "4F596E", "stal_jasna": "D3DBE7",
    "niebieski": "3F6DB3", "niebieski_ciemny": "284A85", "pioro": "4C79C9", "pioro_ciemne": "2D4F94",
    "skora": "8C5631", "skora_ciemna": "5A361D", "skora_jasna": "A9703F",
    "zloto": "E8B93A", "zloto_ciemne": "B98A22",
    "plotno": "9E8E6B", "plotno_ciemne": "75684B",
    # podworkowy
    "farba_biala": "EEE8DC", "drewno": "9A6A3C", "drewno_jasne": "C29B62", "drewno_ciemne": "6A4526",
    "sznurek": "D8B26A", "sznurek_cien": "A88645", "klos": "E3B547", "emalia": "D2382E", "emalia_ciemna": "A1261F",
    "emalia_biala": "F4EFE6", "rdza": "8A4A22", "makaron": "F3D98B", "guma": "3F6D33", "guma_ciemna": "2A4C23",
    "bloto": "5C4026", "otwor": "2B2018", "skarpeta": "EFE0C2", "skarpeta_pasek": "C8504A",
    "skarpeta_ciemna": "9C3934", "latka": "5D8FD0",
    # targowy
    "mosiadz": "C9A13A", "mosiadz_ciemny": "9A7A22", "siatka": "4A4955", "kapsel_czerwony": "D63A35",
    "kapsel_niebieski": "3A6FD0", "kapsel_zielony": "3E9A45", "kapsel_zolty": "E9C23A", "bawelna": "DACEB1",
    "bawelna_cien": "B8AA8A", "ziemia": "6B4A2E", "zielony_mankiet": "4E8A3A", "kielek": "6CC04A",
    "drewno_trepa": "B07A44", "drewno_trepa_cien": "8A5C30",
    # kuchenny
    "zelazo": "4A4750", "zelazo_jasne": "77737D", "rdza_jasna": "B0683A", "len": "CDBEA2", "len_cien": "A8987C",
    "welna": "D08A3E", "welna_ciemna": "A9672A", "futro_kapci": "D9A867", "futro_kapci_jasne": "EBC88E",
    "wiadro": "9EA6B4",
    # mleczarz
    "rdza_pomaranczowa": "D9772E", "biala_guma": "E9ECF2", "biala_cien": "BFC5D0", "niebieski_gumy": "3D63B8",
    "mleko": "FBF8EE", "serce": "D8383E", "latka_roz": "E58AA8", "latka_zolta": "F0CB55", "latka_zielona": "7DBA6A",
    "latka_niebieska": "6E9BD8", "latka_krem": "F3E6CC", "latka_fiolet": "B48AD0", "latka_czerwona": "D45B5B",
    "lamowka": "8A5A34",
}


def _kot_mag():
    """Prywatna kopia modułu kot_mag (ciało, klocki, klipy, korekty chwytu) — prawdziwy Kot-Mag bez zmian."""
    spec = importlib.util.spec_from_file_location("kot_mag_dla_puli_wojownika", os.path.join(TU, "kot_mag.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


KM = _kot_mag()
# korekty kota: dawne (nakrycie głowy na HatPivot, broń bez rodzaju na StaffPivot jak kostur) + rodzaje chwytu
KOREKTY_CHWYTU = dict(KM.KOREKTY_CHWYTU, **CH.KOREKTY_KOTA)
MIARA = KM._postac(BOHATER + "_miara", "Kot-wojownik (miara)")
W = MIARA.wymiary


# --------------------------------------------------------------------------- pomocnicze
def _id(zestaw, rzecz):
    return "%s_%s_%s" % (BOHATER, zestaw, rzecz)


def _nowy(zestaw, rzecz):
    z = ZESTAWY[zestaw]
    slot, kat = SLOTY[rzecz]
    return Przedmiot(_id(zestaw, rzecz), z["przedmioty"][rzecz], slot, kat, MIARA, cialo=KM.CIALO_TYP, klasy=KLASY,
                     zestaw=("%s_%s" % (BOHATER, zestaw)) if z["komplet"] else None, paleta=PALETA,
                     ukrywa=UKRYWA.get(rzecz, ()))


def _helm(zestaw):
    """Akcesorium hełmu: (0,0,0) = HatAttachment (środek górnej ściany głowy kota; głowa 1,65 × 1,3 × 1,4, jej
    środek w (0, −0,65, 0)); oczy sięgają do y = −0,30, wąsy i mordka leżą przy z = +0,70…0,75."""
    return Akcesorium(_id(zestaw, "helm"), ZESTAWY[zestaw]["przedmioty"]["helm"], zaczep="HatAttachment", typ="Hat",
                      paleta=PALETA, ikona_obrot=(-22, 25, 0))      # przód hełmu ku kamerze ikon (patrzy z góry)


def _bron(zestaw):
    """Akcesorium broni: (0,0,0) = środek łapy (RightGripAttachment), klinga w +Y, płaz do przodu (+Z); rodzaj
    chwytu z CHWYT_BRONI (chwyty.py) — u kota korekta tego rodzaju zamiast chwytu kostura."""
    return Akcesorium(_id(zestaw, "miecz"), ZESTAWY[zestaw]["przedmioty"]["miecz"], zaczep="RightGripAttachment",
                      typ="Bron", paleta=PALETA, ikona_obrot=(0, 0, -45), chwyt=CHWYT_BRONI[zestaw])


def _grot(a, nazwa, pos, szer, h, grub, kolor, mat="metal"):
    """Płaski trójkąt (grot klingi, pióro) z dwóch klinów: podstawa w pos, wierzchołek o h wyżej (+Y), szerokość w X,
    grubość w Z — dwie części Roblox."""
    x, y, z = pos
    a.klin(nazwa, (x + szer / 4, y + h / 2, z), (grub, h, szer / 2), kolor, mat, rot=(0, -90, 0), faza=0.0)
    a.klin(nazwa, (x - szer / 4, y + h / 2, z), (grub, h, szer / 2), kolor, mat, rot=(0, 90, 0), faza=0.0)


def _pioro_yz(a, nazwa, h, szer, grub, kolor):
    """Płaskie pióro w płaszczyźnie YZ (widać je z boku): nasada w (0,0,0), czubek w +Y; dwa kliny."""
    a.klin(nazwa, (0, h / 2, szer / 4), (grub, h, szer / 2), kolor, "matowy", rot=(0, 180, 0), faza=0.0)
    a.klin(nazwa, (0, h / 2, -szer / 4), (grub, h, szer / 2), kolor, "matowy", faza=0.0)


def _obrecz(s, nazwa, y, szer, glab, wys, grub, kolor, mat="matowy", faza=0.02):
    """Pas wokół bioder jako cztery deski (przód, tył, boki) zamiast pełnego klocka: na postaci wygląda tak samo,
    a w ikonie widać dziurę — pas czyta się jak pas, nie jak pudełko. Cztery części Roblox."""
    for zk, sfx in ((1, " przod"), (-1, " tyl")):
        s.blok(nazwa + sfx, (0, y, zk * (glab - grub) / 2), (szer, wys, grub), kolor, mat, faza=faza)
    for zn, sfx in ((1, " bok L"), (-1, " bok P")):
        s.blok(nazwa + sfx, (zn * (szer - grub) / 2, y, 0), (grub, wys, glab - 2 * grub + 0.002), kolor, mat,
               faza=faza)


STRONY = (("Left", 1), ("Right", -1))        # strona kota i znak „na zewnątrz” w osi X (lewa = +X)


def _oslony_uszu(a, kolor, mat="metal", ozdoba=None):
    """Dwie osłony w kształcie kocich uszu (trójkątne graniastosłupy z dwóch klinów, _grot) w ramce kości ucha kota:
    staw ucha u nasady (x ±0,6; 0,09 nad czubkiem głowy, czyli 0,07 w układzie hełmu z korektą 0,02; z −0,05), ucho
    odchylone o 28° na zewnątrz. Osłona jest większa od ucha o ok. 0,1 z każdej strony (0,8 u podstawy, 0,98 wysokości,
    0,5 grubości), więc mieści całe ucho (pomiar: --uszy). ozdoba(a, zn) — detal w układzie osłony (nit, kropka,
    dziurka): (0, 0) = środek podstawy osłony na stawie ucha, +Y ku czubkowi, lico w z = +0,265; zn = +1 lewa (+X)."""
    for zn in (1, -1):
        with a.uklad(pos=(zn * 0.6, 0.07, -0.05), obrot=(0, 0, -zn * 28)):
            _grot(a, "Oslona ucha", (zn * 0.04, -0.06, 0.015), 0.8, 0.98, 0.5, kolor, mat)
            if ozdoba is not None:
                ozdoba(a, zn)


# --------------------------------------------------------------------------- 5. ZESTAW GIERMKA
def _giermek():
    """Arkusz `zestaw_giermek.jpg`: stalowy hełm z nitami, obręczą, osłonami policzków i niebieskim piórem; stalowy
    kirys na niebieskiej przeszywanicy (krótkie rękawy, brązowe szelki, paski z klamrami na boku, niebieska spódnica
    z brązowym obszyciem); brązowe rękawice z szerokim mankietem i stalową płytką; wysokie brązowe trzewiki
    z wywiniętą cholewą, złotymi klamrami, stalowym czubkiem i piętą; brązowy pas z nitami, złotą klamrą i sakiewką;
    krótki szeroki miecz z wyszczerbioną klingą, złotym jelcem, owijaną rękojeścią i głowicą-pierścieniem."""
    Z = "giermek"
    wynik = {}

    # --- hełm: niska kopuła jak na arkuszu i dwie osłony w kształcie kocich uszu (Karol 26.11.2026: sylwetka kota
    # zostaje); osłony mieszczą uszy, uszy schowane (ukrywa „Uszy”)
    prz = _nowy(Z, "helm")
    a = _helm(Z)
    # obręcz i dolny pas obejmują kanciastą głowę; nad głową kopuła z ośmiokątnych walców (okrąglejsza sylwetka,
    # każdy walec to jedna część Roblox)
    a.blok("Obrecz", (0, -0.19, -0.01), (1.94, 0.14, 1.7), "stal_cien", "metal", faza=0.03)
    a.blok("Kopula dol", (0, -0.04, -0.01), (1.86, 0.2, 1.62), "stal", "metal", faza=0.04)
    a.walec("Kopula", (0, 0.16, -0.01), (1.84, 0.22, 1.6), "stal", "metal", faza=0.05)
    a.walec("Kopula srodek", (0, 0.36, -0.01), (1.46, 0.2, 1.26), "stal", "metal", faza=0.05)
    a.walec("Kopula gora", (0, 0.53, -0.01), (0.98, 0.16, 0.84), "stal", "metal", faza=0.04)
    # jaśniejszy pas przez środek kopuły (przód, wierzch, tył) z nitami
    a.blok("Pas kopuly przod", (0, 0.05, 0.815), (0.2, 0.38, 0.05), "stal_jasna", "metal", faza=0.0)
    a.blok("Pas schodka przod", (0, 0.36, 0.635), (0.2, 0.2, 0.05), "stal_jasna", "metal", faza=0.0)
    a.blok("Pas kopuly wierzch", (0, 0.625, -0.01), (0.2, 0.03, 0.88), "stal_jasna", "metal", faza=0.0)
    a.blok("Pas kopuly tyl", (0, 0.05, -0.835), (0.2, 0.38, 0.05), "stal_jasna", "metal", faza=0.0)
    for i, y in enumerate((-0.04, 0.15)):
        a.blok("Nit pasa %d" % i, (0, y, 0.85), (0.07, 0.07, 0.04), "zloto", "metal", faza=0.0)
    for x in (-0.66, -0.33, 0.33, 0.66):
        a.blok("Nit obreczy", (x, -0.19, 0.88), (0.07, 0.07, 0.04), "zloto", "metal", faza=0.0)
    for zn in (1, -1):
        # osłony policzków: nad kępkami futra (y > −0,74), przednia krawędź 0,14 za płaszczyzną twarzy
        a.blok("Oslona policzka", (zn * 0.94, -0.45, 0.22), (0.1, 0.42, 0.7), "stal", "metal",
               rot=(0, 0, zn * 6), faza=0.03)
        a.blok("Nit oslony", (zn * 1.0, -0.33, 0.44), (0.04, 0.07, 0.07), "zloto", "metal", faza=0.0)
    a.blok("Oslona karku", (0, -0.42, -0.83), (1.66, 0.36, 0.1), "stal", "metal", rot=(8, 0, 0), faza=0.03)
    # niebieskie pióro na złotej gałce: spłaszczone elipsoidy (jedna część Roblox każda), wygięte do tyłu,
    # płaszczyzna skręcona o 40°, żeby z 3/4 było widać szeroki bok
    a.kula("Galka", (0, 0.67, -0.05), (0.18, 0.14, 0.18), "zloto", "metal")
    with a.uklad(pos=(0, 0.69, -0.08), obrot=(0, 40, 0)):
        with a.uklad(obrot=(-22, 0, 0)):
            a.kula("Pioro", (0, 0.36, 0), (0.09, 0.78, 0.4), "pioro", "matowy", segm=8)
            with a.uklad(pos=(0, 0.66, 0), obrot=(-62, 0, 0)):
                a.kula("Pioro koniec", (0, 0.16, 0), (0.08, 0.42, 0.26), "pioro_ciemne", "matowy", segm=8)
    # osłony uszu: stal ze złotym nitem (uszy kota schowane, sylwetka kota zostaje)
    _oslony_uszu(a, "stal", ozdoba=lambda a, zn: a.blok("Oslona ucha nit", (zn * 0.03, 0.12, 0.275),
                                                         (0.07, 0.07, 0.04), "zloto", "metal", faza=0.0))
    prz.na_zaczepie(a)
    wynik["helm"] = prz

    # --- kirys: stal na niebieskiej przeszywanicy
    prz = _nowy(Z, "zbroja")
    w, h, d = W("UpperTorso")
    s = prz.segment("UpperTorso", zakrywa=True)
    s.blok("Przeszywanica", (0, 0, 0), (w + 0.04, h + 0.01, d + 0.04), "niebieski", "matowy")
    s.blok("Napiersnik", (0, -0.07, 0), (w + 0.08, h - 0.13, d + 0.16), "stal", "metal", faza=0.08)
    s.blok("Grzbiet napiersnika", (0, -0.09, (d + 0.16) / 2 + 0.012), (0.06, h - 0.27, 0.03), "stal_jasna", "metal",
           faza=0.0)
    for zn in (1, -1):
        for zk, sfx in ((1, ""), (-1, " tyl")):
            s.blok("Szelka" + sfx, (zn * 0.38, h / 2 - 0.16, zk * ((d + 0.16) / 2 + 0.02)), (0.16, 0.32, 0.04),
                   "skora", "matowy", faza=0.0)
        s.blok("Nit szelki", (zn * 0.38, h / 2 - 0.28, (d + 0.16) / 2 + 0.045), (0.06, 0.06, 0.03), "zloto",
               "metal", faza=0.0)
        for i, y in enumerate((-0.04, -0.24)):
            s.blok("Pasek boku %d" % i, (zn * ((w + 0.08) / 2 + 0.015), y, -0.04), (0.03, 0.07, 0.36),
                   "skora_ciemna", "matowy", faza=0.0)
        s.blok("Klamra boku", (zn * ((w + 0.08) / 2 + 0.025), -0.04, 0.16), (0.04, 0.1, 0.08), "zloto", "metal",
               faza=0.0)
    for strona, zn in STRONY:
        s = prz.segment(strona + "UpperArm", zakrywa=True)
        wr, hr, dr = W(strona + "UpperArm")
        s.blok("Rekaw", (0, 0, 0), (wr + 0.06, hr, dr + 0.06), "niebieski", "matowy", faza=0.06)
        s.blok("Rekaw pikowanie", (0, 0.04, 0), (wr + 0.08, 0.04, dr + 0.08), "niebieski_ciemny", "matowy", faza=0.0)
        s.blok("Rekaw obszycie", (0, -hr / 2 + 0.03, 0), (wr + 0.1, 0.07, dr + 0.1), "skora", "matowy", faza=0.02)
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso", zakrywa=True)
    s.blok("Przeszywanica dol", (0, 0, 0), (w + 0.04, h + 0.01, d + 0.04), "niebieski", "matowy")
    # spódnica z pasów: przód i tył odchylone od nóg, boki na zewnątrz ud
    for zk, sfx, kat in ((1, "", -10), (-1, " tyl", 10)):
        with s.uklad(pos=(0, -h / 2 + 0.02, zk * ((d + 0.04) / 2 + 0.03)), obrot=(kat, 0, 0)):
            s.blok("Spodnica" + sfx, (0, -0.15, 0), (w - 0.1, 0.3, 0.05), "niebieski", "matowy", faza=0.0)
            for x in (-0.2, 0.2):
                s.blok("Spodnica szew" + sfx, (x, -0.15, 0.0), (0.04, 0.3, 0.07), "niebieski_ciemny", "matowy",
                       faza=0.0)
            s.blok("Spodnica obszycie" + sfx, (0, -0.3, 0), (w - 0.08, 0.05, 0.07), "skora", "matowy", faza=0.0)
    for zn in (1, -1):
        with s.uklad(pos=(zn * ((w + 0.04) / 2 + 0.03), -h / 2 + 0.02, 0), obrot=(0, 0, zn * 10)):
            s.blok("Spodnica bok", (0, -0.13, 0), (0.05, 0.26, d - 0.15), "niebieski", "matowy", faza=0.0)
    wynik["zbroja"] = prz

    # --- pas: nakładka na biodrach (na zewnątrz przeszywanicy o 0,05)
    prz = _nowy(Z, "pas")
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso")
    zp = (d + 0.26) / 2
    _obrecz(s, "Pas", -0.01, w + 0.2, d + 0.26, 0.16, 0.08, "skora")
    for x in (-0.52, -0.36, 0.36):
        s.blok("Nit pasa", (x, -0.01, zp + 0.012), (0.06, 0.06, 0.03), "zloto", "metal", faza=0.0)
    s.blok("Klamra", (0, -0.01, zp + 0.02), (0.28, 0.24, 0.05), "zloto", "metal", faza=0.02)
    s.blok("Klamra srodek", (0, -0.01, zp + 0.04), (0.14, 0.12, 0.03), "skora_ciemna", "matowy", faza=0.0)
    s.blok("Koniec pasa", (-0.24, -0.01, zp + 0.025), (0.2, 0.12, 0.03), "skora_ciemna", "matowy", faza=0.0)
    s.blok("Sakiewka", (0.5, -0.15, zp + 0.06), (0.24, 0.26, 0.14), "plotno", "matowy", faza=0.05)
    s.blok("Sakiewka klapka", (0.5, -0.05, zp + 0.075), (0.26, 0.1, 0.16), "plotno_ciemne", "matowy", faza=0.03)
    s.blok("Sakiewka guzik", (0.5, -0.09, zp + 0.16), (0.05, 0.05, 0.03), "zloto", "metal", faza=0.0)
    wynik["pas"] = prz

    # --- rękawice: brązowa skóra, szeroki rozkloszowany mankiet, stalowa płytka z nitami na wierzchu łapy (przód)
    prz = _nowy(Z, "rekawice")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Hand", zakrywa=True)
        s.blok("Rekawica", (0, -0.08, 0), (0.43, 0.3, 0.43), "skora", "matowy", faza=0.06)
        s.blok("Palce", (0, -0.21, 0.14), (0.38, 0.1, 0.2), "skora", "matowy", faza=0.03)
        for x in (-0.07, 0.07):
            s.blok("Palce szpara", (x, -0.21, 0.245), (0.025, 0.08, 0.02), "skora_ciemna", "matowy", faza=0.0)
        s.blok("Mankiet", (0, 0.13, 0), (0.54, 0.16, 0.54), "skora", "matowy", faza=0.03)
        s.blok("Mankiet brzeg", (0, 0.2, 0), (0.56, 0.04, 0.56), "skora_ciemna", "matowy", faza=0.0)
        s.blok("Plytka", (0, -0.05, 0.235), (0.3, 0.2, 0.05), "stal", "metal", faza=0.02)
        for x in (-0.1, 0.1):
            s.blok("Nit plytki", (x, -0.05, 0.265), (0.05, 0.05, 0.03), "zloto", "metal", faza=0.0)
    wynik["rekawice"] = prz

    # --- trzewiki: łapa (Foot, powłoka) i cholewa na łydce (nakładka)
    prz = _nowy(Z, "buty")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Foot", zakrywa=True)
        s.blok("But", (0, 0.02, 0.205), (0.56, 0.19, 1.12), "skora", "matowy", faza=0.06)
        s.blok("Podeszwa", (0, -0.07, 0.205), (0.58, 0.05, 1.14), "skora_ciemna", "matowy", faza=0.0)
        s.blok("Czubek", (0, 0.005, 0.64), (0.6, 0.19, 0.3), "stal", "metal", faza=0.07)
        s.blok("Pieta", (0, 0.0, -0.36), (0.6, 0.16, 0.1), "stal", "metal", faza=0.03)
        s.blok("Pasek", (0, 0.125, 0.22), (0.6, 0.04, 0.14), "skora_ciemna", "matowy", faza=0.0)
        s.blok("Klamra", (zn * 0.31, 0.06, 0.22), (0.04, 0.11, 0.11), "zloto", "metal", faza=0.0)
        s = prz.segment(strona + "LowerLeg")
        wl, hl, dl = W(strona + "LowerLeg")
        s.blok("Cholewa", (0, 0, 0), (wl + 0.07, 0.3, dl + 0.07), "skora", "matowy", faza=0.04)
        s.blok("Wywiniecie", (0, 0.125, 0), (wl + 0.19, 0.16, dl + 0.19), "skora_jasna", "matowy", faza=0.03)
        s.blok("Klamra cholewy", (zn * ((wl + 0.19) / 2 + 0.015), 0.125, 0.08), (0.03, 0.09, 0.11), "zloto",
               "metal", faza=0.0)
    wynik["buty"] = prz

    # --- miecz: krótki i szeroki (kot: czubek mniej więcej na wysokości czubka głowy)
    prz = _nowy(Z, "miecz")
    a = _bron(Z)
    a.blok("Rekojesc", (0, -0.03, 0), (0.16, 0.52, 0.16), "skora", "matowy", faza=0.03)
    for y in (-0.17, 0.1):
        a.blok("Owijka", (0, y, 0), (0.19, 0.05, 0.19), "skora_ciemna", "matowy", faza=0.0)
    a.walec("Glowica", (0, -0.42, 0), (0.32, 0.1, 0.32), "stal", "metal", rot=(90, 0, 0))
    a.walec("Glowica otwor", (0, -0.42, 0), (0.13, 0.12, 0.13), "stal_ciemna", "metal", rot=(90, 0, 0))
    a.blok("Jelec", (0, 0.29, 0), (0.62, 0.14, 0.24), "zloto", "metal", faza=0.05)
    a.blok("Jelec srodek", (0, 0.29, 0), (0.2, 0.2, 0.28), "zloto_ciemne", "metal", faza=0.04)
    a.blok("Klinga", (0, 0.98, 0), (0.46, 1.24, 0.08), "stal", "metal", faza=0.02)
    a.blok("Zbrocze", (0, 0.92, 0), (0.1, 1.0, 0.11), "stal_jasna", "metal", faza=0.0)
    _grot(a, "Sztych", (0, 1.6, 0), 0.46, 0.4, 0.08, "stal")
    for i, (x, y) in enumerate(((0.21, 0.75), (-0.21, 1.25))):       # wyszczerbienia na ostrzach
        a.blok("Szczerba %d" % i, (x, y, 0), (0.09, 0.07, 0.1), "stal_ciemna", "metal", rot=(0, 0, 40), faza=0.0)
    prz.na_zaczepie(a)
    wynik["miecz"] = prz
    return wynik


# --------------------------------------------------------------------------- 1. PODWÓRKOWY
def _podworkowy():
    """Arkusz `zestaw_podworkowy.jpg`: miecz z białej sztachety (odpryski farby, gwóźdź, poprzeczka-jelec, rękojeść
    owinięta sznurkiem); czerwony garnek w białe kropki z uchwytami, odpryskami i nitką makaronu przy brzegu;
    tara do prania na piersi (drewniana rama, falista blacha, sznur wokół tułowia); skarpety w pasy jako rękawice
    (dziura, łata, postrzępiony ściągacz); zielone kalosze z łatą i błotem; sznurek do snopków z kokardą i kłosami."""
    Z = "podworkowy"
    wynik = {}

    # --- hełm: garnek do góry dnem (kanciasty, zaokrąglony fazą, obejmuje głowę; brzeg tuż nad oczami) i dwie
    # emaliowane osłony w kształcie kocich uszu (uszy schowane, ukrywa „Uszy”)
    prz = _nowy(Z, "helm")
    a = _helm(Z)
    a.blok("Garnek", (0, -0.09, -0.01), (1.92, 0.36, 1.68), "emalia", "polysk", faza=0.04)
    a.walec("Garnek gora", (0, 0.25, -0.01), (1.92, 0.34, 1.68), "emalia", "polysk", faza=0.06)
    a.walec("Dno", (0, 0.44, -0.01), (1.5, 0.05, 1.3), "emalia_ciemna", "polysk", faza=0.02)
    a.blok("Brzeg", (0, -0.25, -0.01), (1.98, 0.07, 1.74), "emalia_biala", "polysk", faza=0.02)
    for zn in (1, -1):                                         # uchwyty-pętle po bokach
        a.blok("Uchwyt", (zn * 1.11, 0.0, 0), (0.06, 0.24, 0.32), "emalia", "polysk", faza=0.02)
        for y in (-0.1, 0.1):
            a.blok("Uchwyt ramie", (zn * 1.02, y, 0), (0.16, 0.06, 0.32), "emalia", "polysk", faza=0.02)
    for i, (x, y, zz) in enumerate(((-0.6, -0.1, 0.835), (0.0, -0.12, 0.835), (0.58, -0.08, 0.835),
                                     (-0.2, 0.3, 0.835), (0.22, 0.2, 0.835))):
        a.blok("Kropka %d" % i, (x, y, zz), (0.16, 0.15, 0.03), "emalia_biala", "polysk", faza=0.0)
    for zn in (1, -1):
        for zz, y in ((0.3, -0.1), (-0.2, 0.3)):
            a.blok("Kropka bok", (zn * 0.975, y, zz), (0.03, 0.15, 0.16), "emalia_biala", "polysk", faza=0.0)
    a.blok("Kropka tyl", (0.3, 0.1, -0.855), (0.16, 0.15, 0.03), "emalia_biala", "polysk", faza=0.0)
    a.blok("Odprysk", (0.32, 0.03, 0.835), (0.22, 0.1, 0.03), "rdza", "matowy", rot=(0, 0, 14), faza=0.0)
    a.blok("Odprysk bok", (-0.975, -0.12, -0.2), (0.03, 0.12, 0.26), "rdza", "matowy", faza=0.0)
    # nitka makaronu zwisa z przedniego rogu garnka, tuż za krawędzią twarzy (poza oczami i policzkiem, nad wąsami)
    with a.uklad(pos=(0.9, -0.28, 0.8)):
        a.blok("Makaron", (0, -0.12, 0), (0.065, 0.26, 0.06), "makaron", "polysk", rot=(0, 0, 12), faza=0.0)
        a.blok("Makaron dol", (0.0, -0.35, 0.01), (0.065, 0.26, 0.06), "makaron", "polysk", rot=(0, 0, -18),
               faza=0.0)
        a.blok("Makaron koniec", (0.05, -0.5, 0.02), (0.065, 0.12, 0.06), "makaron", "polysk", rot=(0, 0, 30),
               faza=0.0)
    # osłony uszu: czerwona emalia z białą kropką, jak garnek
    _oslony_uszu(a, "emalia", "polysk", ozdoba=lambda a, zn: a.blok("Oslona ucha kropka", (zn * 0.03, 0.16, 0.275),
                                                                   (0.15, 0.14, 0.03), "emalia_biala", "polysk",
                                                                   faza=0.0))
    prz.na_zaczepie(a)
    wynik["helm"] = prz

    # --- napierśnik z tary: nakładka na piersi (futro zostaje), sznur dookoła tułowia
    prz = _nowy(Z, "zbroja")
    w, h, d = W("UpperTorso")
    zf = d / 2
    s = prz.segment("UpperTorso")
    for x in (-0.43, 0.43):
        s.blok("Noga tary", (x, -0.09, zf + 0.1), (0.13, 0.98, 0.12), "drewno", "matowy", faza=0.03)
    s.blok("Gorna listwa", (0, 0.33, zf + 0.11), (1.0, 0.14, 0.13), "drewno_jasne", "matowy", faza=0.03)
    s.blok("Dolna listwa", (0, -0.47, zf + 0.1), (0.98, 0.1, 0.12), "drewno", "matowy", faza=0.03)
    s.blok("Blacha", (0, -0.07, zf + 0.07), (0.74, 0.7, 0.05), "stal", "metal", faza=0.0)
    for i in range(5):
        s.blok("Fala %d" % i, (0, -0.33 + 0.12 * i, zf + 0.105), (0.74, 0.05, 0.05), "stal_jasna", "metal",
               faza=0.0)
    s.blok("Rdza", (0.2, -0.2, zf + 0.135), (0.18, 0.1, 0.02), "rdza", "matowy", rot=(0, 0, -10), faza=0.0)
    for x in (-0.44, 0.44):
        s.kula("Wezel", (x, 0.33, zf + 0.2), (0.13, 0.11, 0.1), "sznurek", "matowy")
    for zn in (1, -1):
        s.blok("Sznur bok", (zn * (w / 2 + 0.025), 0.28, 0.02), (0.05, 0.05, d + 0.06), "sznurek", "matowy",
               faza=0.0)
    s.blok("Sznur tyl", (0, 0.28, -zf - 0.03), (w + 0.1, 0.05, 0.05), "sznurek", "matowy", faza=0.0)
    s.blok("Sznur koniec", (-0.5, 0.15, zf + 0.2), (0.05, 0.24, 0.05), "sznurek", "matowy", rot=(0, 0, -8), faza=0.0)
    s.blok("Sznur pedzelek", (-0.52, 0.0, zf + 0.2), (0.08, 0.08, 0.06), "sznurek_cien", "matowy", faza=0.0)
    wynik["zbroja"] = prz

    # --- sznurek do snopków z kokardą i kłosami
    prz = _nowy(Z, "pas")
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso")
    zp = (d + 0.24) / 2
    _obrecz(s, "Sznurek", 0.02, w + 0.2, d + 0.24, 0.13, 0.08, "sznurek", faza=0.04)
    s.blok("Drugi zwoj", (0, -0.07, zp - 0.02), (w + 0.14, 0.07, 0.07), "sznurek_cien", "matowy", faza=0.02)
    with s.uklad(pos=(-0.26, 0.0, zp + 0.06)):
        s.kula("Supel", (0, 0, 0), (0.17, 0.16, 0.13), "sznurek_cien", "matowy")
        for zn in (1, -1):
            s.kula("Petla", (zn * 0.21, 0.04, 0), (0.36, 0.2, 0.08), "sznurek", "matowy", rot=(0, 0, -zn * 18))
            s.blok("Koniec", (zn * 0.08, -0.2, 0.01), (0.06, 0.3, 0.05), "sznurek", "matowy", rot=(0, 0, zn * 14),
                   faza=0.0)
    for i, (x, kat) in enumerate(((0.34, 12), (0.45, -4), (0.55, -20))):
        with s.uklad(pos=(x, 0.05, zp + 0.03), obrot=(0, 0, kat)):
            s.blok("Zdzblo %d" % i, (0, 0.22, 0), (0.035, 0.44, 0.035), "klos", "matowy", faza=0.0)
            s.kula("Klos %d" % i, (0, 0.5, 0), (0.1, 0.26, 0.08), "klos", "matowy")
    wynik["pas"] = prz

    # --- rękawice z dziurawych skarpet w pasy
    prz = _nowy(Z, "rekawice")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Hand", zakrywa=True)
        s.blok("Skarpeta", (0, -0.08, 0), (0.44, 0.32, 0.44), "skarpeta", "matowy", faza=0.06)
        for y in (-0.16, -0.03):
            s.blok("Pasek", (0, y, 0), (0.46, 0.06, 0.46), "skarpeta_pasek", "matowy", faza=0.02)
        s.blok("Palce", (0, -0.2, 0.15), (0.38, 0.11, 0.2), "skarpeta_pasek", "matowy", faza=0.03)
        s.blok("Sciagacz", (0, 0.13, 0), (0.48, 0.13, 0.48), "skarpeta_pasek", "matowy", faza=0.02)
        s.blok("Sciagacz prazek", (0, 0.15, 0), (0.5, 0.03, 0.5), "skarpeta_ciemna", "matowy", faza=0.0)
        for x in (-0.14, 0.12):
            s.blok("Strzep", (x, 0.225, 0.22), (0.05, 0.07, 0.03), "skarpeta", "matowy", rot=(0, 0, 20), faza=0.0)
        s.blok("Dziura", (zn * 0.08, -0.1, 0.225), (0.09, 0.08, 0.02), "otwor", "matowy", faza=0.0)
        if zn == 1:
            s.blok("Lata", (0.225, -0.1, 0.0), (0.02, 0.15, 0.17), "latka", "matowy", faza=0.0)
    wynik["rekawice"] = prz

    # --- kalosze dziadka: zielona guma, błoto, łata na lewym
    prz = _nowy(Z, "buty")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Foot", zakrywa=True)
        s.blok("Kalosz", (0, 0.025, 0.205), (0.56, 0.2, 1.12), "guma", "polysk", faza=0.07)
        s.blok("Podeszwa", (0, -0.065, 0.205), (0.58, 0.06, 1.14), "bloto", "matowy", faza=0.0)
        s.blok("Bloto czubek", (0, -0.025, 0.66), (0.6, 0.09, 0.26), "bloto", "matowy", faza=0.03)
        s.blok("Bloto pieta", (0, -0.035, -0.3), (0.6, 0.07, 0.14), "bloto", "matowy", faza=0.02)
        s = prz.segment(strona + "LowerLeg")
        wl, hl, dl = W(strona + "LowerLeg")
        # wysoka cholewa: do 0,1 ponad koniec klocka łydki (granica nakładki przy stawie kolana)
        s.blok("Cholewa", (0, 0.04, 0), (wl + 0.08, 0.39, dl + 0.08), "guma", "polysk", faza=0.03)
        s.blok("Brzeg", (0, 0.21, 0), (wl + 0.12, 0.05, dl + 0.12), "guma_ciemna", "polysk", faza=0.0)
        s.blok("Bloto cholewy", (0, -0.13, 0), (wl + 0.1, 0.05, dl + 0.1), "bloto", "matowy", faza=0.0)
        if zn == 1:
            s.blok("Lata", ((wl + 0.08) / 2 + 0.015, -0.02, 0.05), (0.03, 0.13, 0.15), "emalia", "matowy", faza=0.0)
    wynik["buty"] = prz

    # --- miecz ze sztachety: biała deska z odpryskami, gwóźdź, poprzeczka, rękojeść w sznurku
    prz = _nowy(Z, "miecz")
    a = _bron(Z)
    a.blok("Rekojesc", (0, -0.05, 0), (0.22, 0.54, 0.1), "drewno", "matowy", faza=0.02)
    for i, y in enumerate((-0.2, -0.06, 0.08)):
        a.blok("Sznurek", (0, y, 0), (0.25, 0.06, 0.13), "sznurek" if i % 2 == 0 else "sznurek_cien", "matowy",
               rot=(0, 0, 8 - 16 * (i % 2)), faza=0.0)
    a.kula("Koniec", (0, -0.36, 0), (0.26, 0.18, 0.13), "farba_biala", "matowy")
    a.blok("Poprzeczka", (0, 0.3, 0.02), (0.74, 0.13, 0.15), "farba_biala", "matowy", rot=(0, 0, -6), faza=0.02)
    a.blok("Poprzeczka odprysk", (0.22, 0.31, 0.1), (0.16, 0.08, 0.02), "drewno", "matowy", faza=0.0)
    a.blok("Deska", (0, 0.98, 0), (0.44, 1.24, 0.1), "farba_biala", "matowy", faza=0.02)
    _grot(a, "Szpic", (0, 1.6, 0), 0.44, 0.34, 0.1, "farba_biala", "matowy")
    for i, (x, y, hh) in enumerate(((-0.1, 0.75, 0.24), (0.12, 1.15, 0.16), (-0.05, 1.42, 0.12))):
        a.blok("Odprysk %d" % i, (x, y, 0.06), (0.14, hh, 0.02), "drewno", "matowy", faza=0.0)
    a.blok("Odprysk tyl", (0.08, 1.0, -0.06), (0.16, 0.3, 0.02), "drewno", "matowy", faza=0.0)
    a.walec("Gwozdz", (0.1, 1.36, 0.14), (0.04, 0.2, 0.04), "stal_ciemna", "metal", rot=(80, 0, 0))
    a.walec("Gwozdz glowka", (0.1, 1.38, 0.24), (0.12, 0.03, 0.12), "stal_ciemna", "metal", rot=(80, 0, 0))
    prz.na_zaczepie(a)
    wynik["miecz"] = prz
    return wynik


# --------------------------------------------------------------------------- 2. TARGOWY
KAPSLE = ("kapsel_czerwony", "kapsel_niebieski", "kapsel_zielony", "kapsel_zolty")


def _kapsle(s, nazwa, xs, ys, z, przod=True, przes=0):
    """Siatka kapsli (płaskie walce, jedna część Roblox każdy) na ścianie przedniej (przod) albo tylnej."""
    zn = 1 if przod else -1
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            kolor = KAPSLE[(i + 2 * j + przes) % 4]
            s.walec(nazwa, (x, y, zn * z), (0.2, 0.045, 0.2), kolor, "polysk", rot=(90, 0, 0), faza=0.01)


def _targowy():
    """Arkusz `zestaw_targowy.jpg`: tasak rzeźnika (szeroka prostokątna klinga z otworem i szczerbami, drewniana
    rękojeść z mosiężnymi nitami); durszlak do góry dnem (dziurki, uchwyty, rozpięty skórzany pasek pod brodę);
    kolczuga z kolorowych kapsli na ciemnej siatce; płócienne rękawice ogrodnika w plamach ziemi z zielonym
    mankietem i kiełkiem; drewniane trepy z podkową na czubku; skórzany pas z uprzęży z mosiężnymi kółkami,
    klamrą i dzwoneczkiem."""
    Z = "targowy"
    wynik = {}

    # --- hełm: durszlak (kopuła z ośmiokątnych walców nad głową, dziurki, uchwyty, stopka na wierzchu) i dwie
    # dziurkowane osłony w kształcie kocich uszu (uszy schowane, ukrywa „Uszy”)
    prz = _nowy(Z, "helm")
    a = _helm(Z)
    a.blok("Brzeg", (0, -0.24, -0.01), (2.04, 0.07, 1.8), "stal_jasna", "metal", faza=0.02)
    a.blok("Durszlak", (0, -0.08, -0.01), (1.88, 0.28, 1.64), "stal", "metal", faza=0.04)
    a.walec("Kopula", (0, 0.14, -0.01), (1.84, 0.2, 1.6), "stal", "metal", faza=0.05)
    a.walec("Kopula gora", (0, 0.32, -0.01), (1.44, 0.18, 1.24), "stal", "metal", faza=0.05)
    a.walec("Stopka", (0, 0.46, -0.01), (0.92, 0.1, 0.8), "stal_cien", "metal", faza=0.02)
    a.walec("Stopka brzeg", (0, 0.52, -0.01), (0.98, 0.03, 0.86), "stal_jasna", "metal", faza=0.0)
    for i, (x, y) in enumerate(((-0.6, -0.1), (-0.3, -0.02), (0.0, -0.12), (0.3, -0.02), (0.6, -0.1),
                                (-0.45, 0.14), (-0.15, 0.17), (0.15, 0.14), (0.45, 0.17),
                                (-0.2, 0.33), (0.2, 0.33))):
        zz = 0.825 if y < 0.04 else (0.8 if y < 0.25 else 0.62)
        a.blok("Dziurka %d" % i, (x, y, zz), (0.07, 0.07, 0.03), "otwor", "matowy", faza=0.0)
    for zn in (1, -1):
        for zz in (0.25, -0.3):
            a.blok("Dziurka bok", (zn * 0.955, -0.06, zz), (0.03, 0.07, 0.07), "otwor", "matowy", faza=0.0)
        a.blok("Uchwyt", (zn * 1.12, -0.06, 0), (0.06, 0.2, 0.3), "stal_jasna", "metal", faza=0.02)
        for y in (-0.15, 0.03):
            a.blok("Uchwyt ramie", (zn * 1.03, y, 0), (0.16, 0.05, 0.3), "stal_jasna", "metal", faza=0.01)
        # rozpięty pasek pod brodę: zwisa przy policzku przed kępkami futra, nad wąsami
        a.blok("Pasek", (zn * 0.99, -0.52, 0.56), (0.05, 0.52, 0.1), "skora", "matowy", rot=(0, 0, zn * 4),
               faza=0.0)
    a.blok("Pasek klamra", (-1.02, -0.66, 0.56), (0.05, 0.1, 0.13), "mosiadz", "metal", faza=0.0)
    # osłony uszu: stal durszlaka z dwiema dziurkami
    def _dziurki(a, zn):
        for y in (0.1, 0.36):
            a.blok("Oslona ucha dziurka", (zn * 0.035, y, 0.275), (0.07, 0.07, 0.03), "otwor", "matowy", faza=0.0)
    _oslony_uszu(a, "stal", ozdoba=_dziurki)
    prz.na_zaczepie(a)
    wynik["helm"] = prz

    # --- kolczuga z kapsli: ciemna siatka (powłoka tułowia i bioder) z kolorowymi kapslami
    prz = _nowy(Z, "zbroja")
    w, h, d = W("UpperTorso")
    s = prz.segment("UpperTorso", zakrywa=True)
    s.blok("Siatka", (0, 0, 0), (w + 0.04, h + 0.01, d + 0.04), "siatka", "matowy", faza=0.04)
    zk = (d + 0.04) / 2 + 0.02
    _kapsle(s, "Kapsel", (-0.45, -0.15, 0.15, 0.45), (0.27, 0.05, -0.17, -0.37), zk)
    _kapsle(s, "Kapsel tyl", (-0.3, 0.0, 0.3), (0.2, -0.1), zk, przod=False, przes=1)
    for zn in (1, -1):
        for j, (y, zz) in enumerate(((0.12, 0.2), (-0.2, -0.15))):
            s.walec("Kapsel bok", (zn * ((w + 0.04) / 2 + 0.02), y, zz), (0.2, 0.045, 0.2),
                    KAPSLE[(j + (zn > 0)) % 4], "polysk", rot=(0, 0, 90), faza=0.01)
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso", zakrywa=True)
    s.blok("Siatka dol", (0, -0.03, 0), (w + 0.04, h + 0.07, d + 0.04), "siatka", "matowy", faza=0.03)
    _kapsle(s, "Kapsel dol", (-0.45, -0.15, 0.15, 0.45), (-0.09,), (d + 0.04) / 2 + 0.02, przes=2)
    wynik["zbroja"] = prz

    # --- pas z uprzęży: skóra, mosiężne kółka, klamra, dzwoneczek
    prz = _nowy(Z, "pas")
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso")
    zp = (d + 0.26) / 2
    _obrecz(s, "Pas", -0.01, w + 0.2, d + 0.26, 0.16, 0.08, "skora")
    s.blok("Klamra", (-0.05, -0.01, zp + 0.02), (0.26, 0.22, 0.05), "mosiadz", "metal", faza=0.02)
    s.blok("Klamra srodek", (-0.05, -0.01, zp + 0.04), (0.13, 0.11, 0.03), "skora_ciemna", "matowy", faza=0.0)
    for x in (-0.5, 0.32):
        s.walec("Kolko", (x, -0.01, zp + 0.03), (0.22, 0.05, 0.22), "mosiadz", "metal", rot=(90, 0, 0), faza=0.0)
        s.walec("Kolko srodek", (x, -0.01, zp + 0.045), (0.11, 0.04, 0.11), "skora_ciemna", "matowy",
                rot=(90, 0, 0), faza=0.0)
    for zn in (1, -1):
        s.walec("Kolko bok", (zn * ((w + 0.2) / 2 + 0.02), -0.01, 0.0), (0.22, 0.05, 0.22), "mosiadz", "metal",
                rot=(0, 0, 90), faza=0.0)
    s.walec("Dzwonek ucho", (0.32, -0.15, zp + 0.05), (0.06, 0.08, 0.06), "mosiadz", "metal", faza=0.0)
    s.kula("Dzwonek", (0.32, -0.26, zp + 0.05), (0.17, 0.16, 0.17), "mosiadz", "metal")
    s.blok("Dzwonek brzeg", (0.32, -0.33, zp + 0.05), (0.19, 0.04, 0.19), "mosiadz_ciemny", "metal", faza=0.0)
    wynik["pas"] = prz

    # --- rękawice ogrodnika: płótno w plamach ziemi, zielony mankiet, kiełek na lewej
    prz = _nowy(Z, "rekawice")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Hand", zakrywa=True)
        s.blok("Rekawica", (0, -0.08, 0), (0.43, 0.3, 0.43), "bawelna", "matowy", faza=0.06)
        s.blok("Palce", (0, -0.21, 0.14), (0.38, 0.1, 0.2), "bawelna_cien", "matowy", faza=0.03)
        s.blok("Mankiet", (0, 0.12, 0), (0.48, 0.14, 0.48), "zielony_mankiet", "matowy", faza=0.03)
        for i, (x, y, zz) in enumerate(((0.08, -0.12, 0.225), (-0.1, -0.02, 0.225), (zn * 0.225, -0.15, -0.05))):
            ss = (0.1, 0.08, 0.02) if abs(zz) > 0.2 else (0.02, 0.08, 0.1)
            s.blok("Plama %d" % i, (x, y, zz), ss, "ziemia", "matowy", faza=0.0)
        if zn == 1:
            s.blok("Kielek", (0.12, 0.27, 0.1), (0.03, 0.16, 0.03), "kielek", "matowy", faza=0.0)
            for kz in (1, -1):
                s.kula("Listek", (0.12 + kz * 0.06, 0.35, 0.1), (0.1, 0.05, 0.06), "kielek", "matowy",
                       rot=(0, 0, kz * 25))
    wynik["rekawice"] = prz

    # --- trepy z podkową: drewniane chodaki z zadartym, spiczastym czubkiem, podkowa przybita na czubku
    prz = _nowy(Z, "buty")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Foot", zakrywa=True)
        s.blok("Trep", (0, 0.03, 0.06), (0.58, 0.22, 0.86), "drewno_trepa", "matowy", faza=0.08)
        s.blok("Trep obcas", (0, -0.065, -0.24), (0.5, 0.06, 0.24), "drewno_trepa_cien", "matowy", faza=0.02)
        s.blok("Brzeg trepa", (0, 0.145, -0.08), (0.6, 0.04, 0.6), "drewno_trepa_cien", "matowy", faza=0.0)
        with s.uklad(pos=(0, -0.02, 0.5), obrot=(-16, 0, 0)):
            s.blok("Czubek", (0, 0.02, 0.15), (0.52, 0.18, 0.36), "drewno_trepa", "matowy", faza=0.07)
            with s.uklad(pos=(0, 0.0, 0.32), obrot=(-22, 0, 0)):
                s.blok("Czubek nos", (0, 0.02, 0.05), (0.32, 0.12, 0.16), "drewno_trepa", "matowy", faza=0.05)
            # podkowa leży na wierzchu czubka, otwarta ku tyłowi
            for x in (-0.15, 0.15):
                s.blok("Podkowa ramie", (x, 0.125, 0.12), (0.07, 0.04, 0.24), "stal", "metal", faza=0.0)
            s.blok("Podkowa luk", (0, 0.125, 0.26), (0.37, 0.04, 0.07), "stal", "metal", faza=0.0)
    wynik["buty"] = prz

    # --- tasak rzeźnika Bolka: klinga na zewnątrz łapy (−X), otwór przy grzbiecie, szczerby na ostrzu
    prz = _nowy(Z, "miecz")
    a = _bron(Z)
    a.blok("Rekojesc", (0, -0.06, 0), (0.2, 0.6, 0.16), "drewno", "matowy", faza=0.04)
    for y in (-0.26, -0.06, 0.14):
        a.walec("Nit", (0, y, 0.085), (0.07, 0.03, 0.07), "mosiadz", "metal", rot=(90, 0, 0), faza=0.0)
    a.blok("Okucie", (0, 0.28, 0), (0.22, 0.08, 0.18), "stal_cien", "metal", faza=0.02)
    a.blok("Klinga", (-0.24, 0.84, 0), (0.7, 1.04, 0.07), "stal", "metal", faza=0.02)
    a.blok("Ostrze", (-0.55, 0.84, 0), (0.09, 1.0, 0.075), "stal_jasna", "metal", faza=0.0)
    a.blok("Grzbiet", (0.09, 0.84, 0), (0.05, 1.04, 0.08), "stal_cien", "metal", faza=0.0)
    a.walec("Otwor", (-0.02, 1.2, 0), (0.15, 0.08, 0.15), "otwor", "matowy", rot=(90, 0, 0), faza=0.0)
    for i, y in enumerate((0.6, 1.05)):
        a.blok("Szczerba %d" % i, (-0.58, y, 0), (0.08, 0.07, 0.09), "stal_ciemna", "metal", rot=(0, 0, 35),
               faza=0.0)
    prz.na_zaczepie(a)
    wynik["miecz"] = prz
    return wynik


# --------------------------------------------------------------------------- 3. KUCHENNY
def _kuchenny():
    """Arkusz `zestaw_kuchenny.jpg` (napis tytułu na arkuszu pominięty): żeliwny pogrzebacz z hakiem, wygiętym
    jelcem i owiniętą płótnem rękojeścią; blaszany kubeł z dwiema dziurami na oczy i kabłąkiem z drewnianym
    uchwytem; dwie żeliwne patelnie na piersi przewiązane sznurem; wełniane mitenki z przykręconym łańcuchem;
    puchate kapcie z blaszanymi opaskami na sznurku; zardzewiały łańcuch od studni z wiaderkiem jako pas.
    Odstępstwa dla kota: kubeł siedzi NAD oczami (dziury na oczy są na blasze nad prawdziwymi oczami, twarz zostaje
    odkryta), kabłąk jest przerzucony do tyłu za głowę (pod brodą przechodziłby przez pyszczek); trzonki patelni są
    krótkie i odchylone na boki — pod brodą kota nie ma miejsca na długie trzonki ku górze."""
    Z = "kuchenny"
    wynik = {}

    # --- hełm: kubeł do góry dnem, lekko zsunięty na tył głowy, i dwie blaszane osłony w kształcie kocich uszu
    # (uszy schowane, ukrywa „Uszy”)
    prz = _nowy(Z, "helm")
    a = _helm(Z)
    with a.uklad(obrot=(-6, 0, 0)):
        a.blok("Brzeg", (0, -0.25, -0.01), (2.0, 0.07, 1.76), "stal_jasna", "metal", faza=0.02)
        a.blok("Kubel", (0, -0.1, -0.01), (1.92, 0.3, 1.68), "stal", "metal", faza=0.03)
        a.walec("Kubel srodek", (0, 0.21, -0.01), (1.84, 0.34, 1.6), "stal", "metal", faza=0.03)
        a.walec("Kubel gora", (0, 0.48, -0.01), (1.66, 0.22, 1.44), "stal", "metal", faza=0.03)
        a.walec("Kubel dno", (0, 0.61, -0.01), (1.5, 0.05, 1.3), "stal_cien", "metal", faza=0.02)
        for i, y in enumerate((0.03, 0.37)):
            a.walec("Przetloczenie %d" % i, (0, y, -0.01), (1.87, 0.03, 1.63), "stal_cien", "metal", faza=0.0)
        for zn in (1, -1):                                  # dziury „na oczy” — na blasze nad oczami kota
            a.walec("Dziura", (zn * 0.36, -0.08, 0.83), (0.24, 0.04, 0.2), "otwor", "matowy", rot=(90, 0, 0),
                    faza=0.0)
            a.blok("Ucho kabla", (zn * 0.975, -0.12, 0.0), (0.04, 0.12, 0.12), "stal_ciemna", "metal", faza=0.0)
        a.blok("Wgniecenie", (0.3, 0.5, 0.715), (0.2, 0.12, 0.03), "stal_ciemna", "metal", rot=(0, 0, 25), faza=0.0)
        # kabłąk przerzucony do tyłu: boki wzdłuż skroni, łuk za potylicą, drewniany uchwyt
        for zn in (1, -1):
            a.blok("Kablak bok", (zn * 1.01, -0.32, -0.42), (0.04, 0.04, 0.86), "stal_ciemna", "metal",
                   rot=(-28, 0, 0), faza=0.0)
        a.blok("Kablak tyl", (0, -0.52, -0.84), (2.02, 0.04, 0.04), "stal_ciemna", "metal", faza=0.0)
        a.walec("Uchwyt kablaka", (0, -0.52, -0.84), (0.1, 0.5, 0.1), "drewno", "matowy", rot=(0, 0, 90))
    # osłony uszu: blacha kubła z wgnieceniem (na uszach głowy, bez przechylenia kubła)
    _oslony_uszu(a, "stal", ozdoba=lambda a, zn: a.blok("Oslona ucha wgniecenie", (zn * 0.02, 0.2, 0.275),
                                                         (0.14, 0.1, 0.03), "stal_ciemna", "metal",
                                                         rot=(0, 0, zn * 20), faza=0.0))
    prz.na_zaczepie(a)
    wynik["helm"] = prz

    # --- napierśnik z patelni: dwie patelnie na piersi (nakładka), sznur dookoła tułowia
    prz = _nowy(Z, "zbroja")
    w, h, d = W("UpperTorso")
    zf = d / 2
    s = prz.segment("UpperTorso")
    for zn in (1, -1):
        x = zn * 0.33
        s.walec("Patelnia", (x, -0.04, zf + 0.07), (0.68, 0.12, 0.68), "zelazo", "metal", rot=(90, 0, 0), faza=0.03)
        s.walec("Patelnia dno", (x, -0.04, zf + 0.135), (0.52, 0.03, 0.52), "zelazo_jasne", "metal",
                rot=(90, 0, 0), faza=0.0)
        s.blok("Rdza", (x - zn * 0.08, 0.06, zf + 0.155), (0.14, 0.1, 0.02), "rdza_jasna", "matowy", faza=0.0)
        with s.uklad(pos=(zn * 0.52, 0.2, zf + 0.12), obrot=(0, 0, -zn * 42)):
            s.blok("Trzonek", (0, 0.11, 0), (0.1, 0.26, 0.07), "zelazo", "metal", faza=0.02)
            s.blok("Trzonek otwor", (0, 0.17, 0.037), (0.04, 0.07, 0.02), "otwor", "matowy", faza=0.0)
    _obrecz(s, "Sznur", -0.02, w + 0.1, d + 0.36, 0.06, 0.06, "sznurek", faza=0.0)
    s.blok("Sznur drugi zwoj", (0, -0.13, zf + 0.19), (w - 0.05, 0.06, 0.06), "sznurek_cien", "matowy", faza=0.0)
    wynik["zbroja"] = prz

    # --- pas z łańcucha studni z wiaderkiem
    prz = _nowy(Z, "pas")
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso")
    zp = (d + 0.24) / 2
    _obrecz(s, "Lancuch spod", 0.0, w + 0.18, d + 0.22, 0.06, 0.05, "rdza", faza=0.0)
    for i in range(7):                                      # ogniwa na przodzie: płasko i bokiem na przemian
        x = -0.6 + 0.2 * i
        if i % 2 == 0:
            s.blok("Ogniwo", (x, 0.0, zp + 0.01), (0.2, 0.11, 0.05), "rdza", "metal", faza=0.02)
        else:
            s.blok("Ogniwo bokiem", (x, 0.0, zp + 0.01), (0.06, 0.12, 0.12), "rdza_jasna", "metal", faza=0.01)
    for zn in (1, -1):
        for zz in (0.25, -0.15):
            s.blok("Ogniwo boku", (zn * ((w + 0.18) / 2 + 0.01), 0.0, zz), (0.05, 0.11, 0.2), "rdza", "metal",
                   faza=0.02)
    s.blok("Ogniwo wiaderka", (0.3, -0.12, zp + 0.04), (0.05, 0.13, 0.1), "rdza_jasna", "metal", faza=0.01)
    s.blok("Kablak wiaderka", (0.3, -0.21, zp + 0.06), (0.22, 0.04, 0.04), "stal_ciemna", "metal", faza=0.0)
    s.walec("Wiaderko", (0.3, -0.34, zp + 0.07), (0.24, 0.22, 0.2), "wiadro", "metal", faza=0.02)
    s.walec("Wiaderko brzeg", (0.3, -0.235, zp + 0.07), (0.27, 0.03, 0.23), "stal_jasna", "metal", faza=0.0)
    wynik["pas"] = prz

    # --- mitenki z łańcucha: wełna, kciuk, ściągacz, łańcuch na skos między dwiema blaszkami
    prz = _nowy(Z, "rekawice")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Hand", zakrywa=True)
        s.blok("Mitenka", (0, -0.09, 0.02), (0.44, 0.34, 0.46), "welna", "matowy", faza=0.08)
        s.blok("Kciuk", (-zn * 0.2, -0.02, 0.12), (0.12, 0.17, 0.15), "welna", "matowy", faza=0.04)
        s.blok("Sciagacz", (0, 0.12, 0), (0.47, 0.13, 0.47), "welna_ciemna", "matowy", faza=0.02)
        for x in (-0.1, 0.0, 0.1):
            s.blok("Prazek", (x, 0.12, 0.24), (0.025, 0.12, 0.02), "welna", "matowy", faza=0.0)
        with s.uklad(pos=(0, -0.08, 0.255), obrot=(0, 0, zn * 35)):
            s.blok("Blaszka", (0, 0.15, 0), (0.18, 0.06, 0.03), "stal", "metal", faza=0.0)
            s.blok("Blaszka", (0, -0.15, 0), (0.18, 0.06, 0.03), "stal", "metal", faza=0.0)
            for j, y in enumerate((-0.07, 0.0, 0.07)):
                ss = (0.05, 0.09, 0.035) if j % 2 == 0 else (0.03, 0.09, 0.05)
                s.blok("Ogniwo", (0, y, 0.005), ss, "stal_ciemna", "metal", faza=0.0)
    wynik["rekawice"] = prz

    # --- kapcie pancerne: puchate kapcie, blaszane opaski przywiązane sznurkiem
    prz = _nowy(Z, "buty")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Foot", zakrywa=True)
        s.blok("Kapec", (0, 0.015, 0.2), (0.6, 0.2, 1.12), "futro_kapci", "matowy", faza=0.08)
        s.blok("Podeszwa", (0, -0.07, 0.2), (0.6, 0.05, 1.12), "drewno_ciemne", "matowy", faza=0.0)
        s.blok("Futerko", (0, 0.12, -0.1), (0.64, 0.07, 0.56), "futro_kapci_jasne", "matowy", faza=0.03)
        s.blok("Opaska", (0, 0.1, 0.33), (0.64, 0.08, 0.22), "stal", "metal", faza=0.02)
        s.blok("Opaska czubka", (0, 0.06, 0.62), (0.64, 0.08, 0.2), "stal", "metal", faza=0.02)
        for kat in (30, -30):
            s.blok("Sznurek", (0, 0.145, 0.47), (0.05, 0.03, 0.5), "sznurek", "matowy", rot=(0, kat, 0), faza=0.0)
    wynik["buty"] = prz

    # --- pogrzebacz z kominka: żeliwny pręt z hakiem, wygięty jelec, rękojeść owinięta płótnem
    prz = _nowy(Z, "miecz")
    a = _bron(Z)
    a.blok("Rekojesc", (0, -0.05, 0), (0.15, 0.56, 0.15), "len", "matowy", faza=0.03)
    for y in (-0.22, 0.0, 0.17):
        a.blok("Owijka", (0, y, 0), (0.17, 0.04, 0.17), "len_cien", "matowy", rot=(0, 0, 12), faza=0.0)
    a.kula("Galka", (0, -0.4, 0), (0.2, 0.2, 0.2), "zelazo", "metal")
    for zn in (1, -1):                                       # jelec: dwa ramiona wygięte ku górze
        with a.uklad(pos=(zn * 0.06, 0.29, 0), obrot=(0, 0, -zn * 62)):
            a.blok("Jelec", (0, 0.14, 0), (0.08, 0.3, 0.08), "zelazo", "metal", faza=0.02)
            a.blok("Jelec koniec", (0, 0.3, 0), (0.07, 0.12, 0.07), "zelazo_jasne", "metal", rot=(0, 0, zn * 50),
                   faza=0.0)
    a.blok("Pret", (0, 1.15, 0), (0.1, 1.7, 0.1), "zelazo", "metal", faza=0.02)
    a.blok("Pret blysk", (-0.03, 1.15, 0.045), (0.03, 1.5, 0.02), "zelazo_jasne", "metal", faza=0.0)
    with a.uklad(pos=(0, 2.0, 0), obrot=(0, 0, 55)):        # hak: łuk w bok i grot w dół
        a.blok("Hak", (0, 0.12, 0), (0.1, 0.28, 0.1), "zelazo", "metal", faza=0.02)
        with a.uklad(pos=(0, 0.25, 0), obrot=(0, 0, 70)):
            a.blok("Hak luk", (0, 0.08, 0), (0.09, 0.2, 0.09), "zelazo", "metal", faza=0.02)
            with a.uklad(pos=(0, 0.17, 0), obrot=(0, 0, 60)):
                _grot(a, "Hak grot", (0, 0.0, 0), 0.12, 0.16, 0.08, "zelazo")
    prz.na_zaczepie(a)
    wynik["miecz"] = prz
    return wynik


# --------------------------------------------------------------------------- 4. MLECZARZ
LATKI = ("latka_roz", "latka_zolta", "latka_zielona", "latka_niebieska", "latka_krem", "latka_fiolet",
         "latka_czerwona")


def _latki(s, nazwa, xs, ys, z, rozmiar, przes=0, przod=True):
    """Siatka kolorowych łatek pikowanej kamizelki na ścianie przedniej albo tylnej (po jednej części Roblox)."""
    zn = 1 if przod else -1
    for j, y in enumerate(ys):
        for i, x in enumerate(xs):
            s.blok(nazwa, (x, y, zn * z), (rozmiar[0], rozmiar[1], 0.04), LATKI[(i + 3 * j + przes) % len(LATKI)],
                   "matowy", faza=0.02)


def _mleczarz():
    """Arkusz `zestaw_mleczarz.jpg`: zardzewiały kordelas (zakrzywiona klinga w plamach rdzy, mosiężny kabłąk
    osłaniający dłoń); bańka na mleko jako hełm (wąska szyjka z pokrywką, uchwyty, wizjer); pikowana przeszywanica
    babci z kolorowych łatek z guzikami i brązową lamówką; białe rękawice szermiercze z wysokim mankietem i czerwonym
    serduszkiem; białe gumowce mleczarza z niebieskim brzegiem i rozlanym mlekiem; pas z małą patelnią jako klamrą.
    Odstępstwo dla kota: bańka siedzi NAD oczami (wizjer jest na blasze nad prawdziwymi oczami, twarz zostaje
    odkryta), uszy wychodzą obok wąskiej szyjki bańki."""
    Z = "mleczarz"
    wynik = {}

    # --- hełm: bańka na mleko i dwie blaszane osłony w kształcie kocich uszu po bokach szyjki (uszy schowane,
    # ukrywa „Uszy”)
    prz = _nowy(Z, "helm")
    a = _helm(Z)
    a.blok("Brzeg", (0, -0.25, -0.01), (2.0, 0.07, 1.76), "stal_cien", "metal", faza=0.02)
    a.blok("Banka", (0, -0.1, -0.01), (1.92, 0.32, 1.68), "stal", "metal", faza=0.03)
    a.walec("Banka gora", (0, 0.24, -0.01), (1.92, 0.36, 1.68), "stal", "metal", faza=0.04)
    a.walec("Ramiona banki", (0, 0.47, -0.01), (1.46, 0.12, 1.28), "stal", "metal", faza=0.05)
    a.walec("Szyjka", (0, 0.66, -0.01), (0.74, 0.28, 0.66), "stal", "metal", faza=0.02)
    a.walec("Pokrywka brzeg", (0, 0.83, -0.01), (0.94, 0.08, 0.84), "stal_cien", "metal", faza=0.02)
    a.walec("Pokrywka", (0, 0.89, -0.01), (0.78, 0.05, 0.7), "stal_jasna", "metal", faza=0.02)
    a.blok("Wizjer", (0, -0.07, 0.835), (0.95, 0.11, 0.03), "otwor", "matowy", faza=0.0)
    a.blok("Blysk", (-0.55, 0.2, 0.8), (0.12, 0.34, 0.03), "stal_jasna", "metal", faza=0.0)
    for zn in (1, -1):                       # uchwyty na brzuchu bańki (nad nim boki zajmują osłony uszu)
        a.blok("Uchwyt", (zn * 1.12, -0.08, 0), (0.06, 0.2, 0.3), "stal_jasna", "metal", faza=0.02)
        for y in (-0.17, 0.01):
            a.blok("Uchwyt ramie", (zn * 1.03, y, 0), (0.16, 0.05, 0.3), "stal_jasna", "metal", faza=0.01)
    # osłony uszu: blacha bańki z jasnym błyskiem, po bokach szyjki
    _oslony_uszu(a, "stal", ozdoba=lambda a, zn: a.blok("Oslona ucha blysk", (-zn * 0.06, 0.18, 0.275),
                                                         (0.06, 0.3, 0.03), "stal_jasna", "metal",
                                                         rot=(0, 0, zn * 10), faza=0.0))
    prz.na_zaczepie(a)
    wynik["helm"] = prz

    # --- przeszywanica babci: pikowana kamizelka z kolorowych łatek (powłoka tułowia i bioder, bez rękawów)
    prz = _nowy(Z, "zbroja")
    w, h, d = W("UpperTorso")
    s = prz.segment("UpperTorso", zakrywa=True)
    s.blok("Kamizelka", (0, 0, 0), (w + 0.06, h + 0.01, d + 0.06), "latka_krem", "matowy", faza=0.06)
    zl = (d + 0.06) / 2 + 0.015
    _latki(s, "Latka", (-0.44, -0.15, 0.17, 0.45), (0.2, -0.06, -0.3), zl, (0.27, 0.24))
    _latki(s, "Latka tyl", (-0.32, 0.0, 0.32), (0.18, -0.12), zl, (0.3, 0.27), przes=2, przod=False)
    s.blok("Lamowka", (0.02, -0.02, zl + 0.02), (0.06, h - 0.02, 0.03), "lamowka", "matowy", faza=0.0)
    s.blok("Lamowka gora", (0, h / 2 - 0.03, 0), (w + 0.1, 0.05, d + 0.1), "lamowka", "matowy", faza=0.0)
    for zn in (1, -1):
        s.blok("Lamowka pacha", (zn * ((w + 0.06) / 2 + 0.015), 0.1, 0), (0.03, 0.42, d - 0.1), "lamowka", "matowy",
               faza=0.0)
    for i, (y, kolor) in enumerate(((0.24, "latka_czerwona"), (0.06, "zloto"), (-0.12, "latka_zielona"),
                                    (-0.3, "latka_niebieska"))):
        s.walec("Guzik %d" % i, (-0.07, y, zl + 0.04), (0.1, 0.03, 0.1), kolor, "polysk", rot=(90, 0, 0), faza=0.0)
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso", zakrywa=True)
    s.blok("Kamizelka dol", (0, -0.04, 0), (w + 0.06, h + 0.09, d + 0.06), "latka_krem", "matowy", faza=0.04)
    _latki(s, "Latka dol", (-0.44, -0.15, 0.17, 0.45), (-0.04,), (d + 0.06) / 2 + 0.015, (0.27, 0.22), przes=5)
    s.blok("Lamowka dol", (0, -h / 2 - 0.07, 0), (w + 0.1, 0.05, d + 0.1), "lamowka", "matowy", faza=0.0)
    wynik["zbroja"] = prz

    # --- pas z klamrą-patelnią
    prz = _nowy(Z, "pas")
    w, h, d = W("LowerTorso")
    s = prz.segment("LowerTorso")
    zp = (d + 0.28) / 2
    _obrecz(s, "Pas", -0.02, w + 0.22, d + 0.28, 0.15, 0.08, "skora")
    for x in (-0.55, -0.45, -0.35):
        s.blok("Dziurka", (x, -0.02, zp + 0.005), (0.04, 0.04, 0.02), "otwor", "matowy", faza=0.0)
    s.blok("Szlufka", (0.32, -0.02, zp + 0.01), (0.07, 0.19, 0.03), "skora_ciemna", "matowy", faza=0.0)
    s.walec("Patelenka", (0.0, -0.03, zp + 0.04), (0.46, 0.07, 0.46), "zelazo", "metal", rot=(90, 0, 0), faza=0.02)
    s.walec("Patelenka dno", (0.0, -0.03, zp + 0.08), (0.34, 0.02, 0.34), "zelazo_jasne", "metal", rot=(90, 0, 0),
            faza=0.0)
    with s.uklad(pos=(0.2, -0.15, zp + 0.05), obrot=(0, 0, 40)):
        s.blok("Trzonek", (0.17, 0, 0), (0.36, 0.08, 0.06), "zelazo", "metal", faza=0.01)
        s.blok("Trzonek otwor", (0.28, 0, 0.032), (0.07, 0.035, 0.01), "otwor", "matowy", faza=0.0)
    wynik["pas"] = prz

    # --- rękawice szermiercze: białe, wysoki rozkloszowany mankiet, czerwone serduszko na lewej
    prz = _nowy(Z, "rekawice")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Hand", zakrywa=True)
        s.blok("Rekawica", (0, -0.08, 0), (0.43, 0.3, 0.43), "biala_guma", "polysk", faza=0.06)
        s.blok("Palce", (0, -0.21, 0.14), (0.38, 0.1, 0.2), "biala_guma", "polysk", faza=0.03)
        s.blok("Palce szpara", (0, -0.21, 0.245), (0.025, 0.08, 0.02), "biala_cien", "matowy", faza=0.0)
        s.blok("Mankiet", (0, 0.13, 0), (0.58, 0.16, 0.58), "biala_guma", "polysk", faza=0.03)
        s.blok("Mankiet cien", (0, 0.05, 0), (0.5, 0.04, 0.5), "biala_cien", "matowy", faza=0.0)
        if zn == 1:
            for kz in (1, -1):
                s.blok("Serce", (kz * 0.035, -0.06, 0.225), (0.09, 0.09, 0.02), "serce", "matowy", rot=(0, 0, kz * 45),
                       faza=0.0)
    wynik["rekawice"] = prz

    # --- buty mleczarza: białe gumowce z niebieskim brzegiem i podeszwą, plama mleka na czubku
    prz = _nowy(Z, "buty")
    for strona, zn in STRONY:
        s = prz.segment(strona + "Foot", zakrywa=True)
        s.blok("Gumowiec", (0, 0.025, 0.205), (0.56, 0.2, 1.12), "biala_guma", "polysk", faza=0.07)
        s.blok("Podeszwa", (0, -0.065, 0.205), (0.58, 0.06, 1.14), "niebieski_gumy", "polysk", faza=0.0)
        if zn == -1:
            s.kula("Mleko", (0.05, 0.12, 0.55), (0.3, 0.05, 0.24), "mleko", "polysk")
            s.kula("Mleko kropla", (-0.17, 0.11, 0.7), (0.1, 0.04, 0.08), "mleko", "polysk")
        s = prz.segment(strona + "LowerLeg")
        wl, hl, dl = W(strona + "LowerLeg")
        s.blok("Cholewa", (0, 0.04, 0), (wl + 0.08, 0.39, dl + 0.08), "biala_guma", "polysk", faza=0.03)
        s.blok("Brzeg", (0, 0.21, 0), (wl + 0.12, 0.05, dl + 0.12), "niebieski_gumy", "polysk", faza=0.0)
        s.blok("Fala", (0, -0.1, 0), (wl + 0.1, 0.03, dl + 0.1), "biala_cien", "matowy", faza=0.0)
    wynik["buty"] = prz

    # --- zardzewiały kordelas: klinga zakrzywiona na zewnątrz (−X), plamy rdzy, mosiężny kabłąk przy łapie
    prz = _nowy(Z, "miecz")
    a = _bron(Z)
    a.blok("Rekojesc", (0, -0.04, 0), (0.15, 0.5, 0.15), "skora", "matowy", faza=0.03)
    for y in (-0.18, 0.0, 0.15):
        a.blok("Owijka", (0, y, 0), (0.17, 0.04, 0.17), "skora_ciemna", "matowy", rot=(0, 0, 14), faza=0.0)
    a.blok("Glowica", (0, -0.33, 0), (0.2, 0.1, 0.2), "mosiadz", "metal", faza=0.03)
    a.blok("Jelec", (0, 0.27, 0), (0.42, 0.08, 0.16), "mosiadz", "metal", faza=0.02)
    # kabłąk: od jelca łukiem do głowicy po stronie ostrza (−X, na zewnątrz łapy; od 26.11.2026 — po stronie +X
    # wchodził w przedramię kota, kontrola --ruch)
    a.blok("Kablak", (-0.27, -0.03, 0), (0.06, 0.5, 0.07), "mosiadz", "metal", faza=0.0)
    for y, kat in ((0.24, 40), (-0.3, -40)):
        a.blok("Kablak luk", (-0.2, y, 0), (0.06, 0.16, 0.07), "mosiadz", "metal", rot=(0, 0, kat), faza=0.0)
    poz, kat = (0.0, 0.31), 0.0
    for i, (dl, dk) in enumerate(((0.5, 6), (0.45, 12), (0.4, 18))):      # klinga z trzech odcinków, coraz bardziej
        with a.uklad(pos=(poz[0], poz[1], 0), obrot=(0, 0, kat + dk)):    # wygięta ku −X
            a.blok("Klinga %d" % i, (0, dl / 2, 0), (0.38 - 0.03 * i, dl + 0.02, 0.07), "stal", "metal", faza=0.01)
            a.blok("Grzbiet %d" % i, (0.17 - 0.015 * i, dl / 2, 0), (0.05, dl + 0.02, 0.08), "stal_cien", "metal",
                   faza=0.0)
        kat += dk
        poz = (poz[0] - dl * math.sin(math.radians(kat)), poz[1] + dl * math.cos(math.radians(kat)))
    with a.uklad(pos=(poz[0], poz[1], 0), obrot=(0, 0, kat + 14)):
        _grot(a, "Sztych", (0.04, 0, 0), 0.32, 0.36, 0.07, "stal")
    for i, (x, y, r) in enumerate(((-0.05, 0.6, 0.11), (-0.12, 0.95, 0.09), (-0.3, 1.25, 0.12), (-0.06, 0.85, 0.07))):
        for zk in (1, -1):
            a.blok("Rdza %d" % i, (x, y, zk * 0.04), (r, r * 0.8, 0.02), "rdza_pomaranczowa", "matowy",
                   rot=(0, 0, 20 * i), faza=0.0)
    a.blok("Szczerba", (-0.25, 0.98, 0), (0.08, 0.06, 0.09), "stal_ciemna", "metal", rot=(0, 0, 40), faza=0.0)
    prz.na_zaczepie(a)
    wynik["miecz"] = prz
    return wynik

_BUDOWA = {"giermek": _giermek, "podworkowy": _podworkowy, "targowy": _targowy, "kuchenny": _kuchenny, "mleczarz": _mleczarz}


# --------------------------------------------------------------------------- API
def zrobione():
    """Zestawy, które mają już modele (kolejność kolumn Pawła)."""
    return [z for z in sorted(ZESTAWY, key=lambda k: ZESTAWY[k]["kolumna"]) if z in _BUDOWA]


def przedmioty(zestaw):
    """Sześć przedmiotów arkusza w kolejności zakładania (świeże obiekty Przedmiot)."""
    d = _BUDOWA[zestaw]()
    return [d[r] for r in RZECZY]


def komplet(zestaw):
    return tuple(_id(zestaw, r) for r in RZECZY)


def cialo(zaczepy_ekwipunku=False):
    """Goły rudy kot (Kot-Mag rasy Człowiek, jak Koci Rycerz) z klipami Kota-Maga."""
    return KM.cialo(zaczepy_ekwipunku)


def postac(zestaw, id=None, prz=None, tylko_idle=False):
    """Kot-wojownik w sześciu przedmiotach arkusza."""
    p = ubierz(cialo(), prz or przedmioty(zestaw), id=id or "%s_%s" % (BOHATER, zestaw),
               nazwa="Kot-wojownik — %s" % ZESTAWY[zestaw]["nazwa"], korekty=KOREKTY_CHWYTU)
    if tylko_idle:
        p.klipy = [k for k in p.klipy if k.nazwa == "idle"]
    return p


def modele(zestaw, id_modulu):
    """Dla przebuduj.py (zbuduj modułu zestawu): kot w komplecie (tylko klip idle — ruch jest wspólny z Kotem-Magiem)
    oraz hełm i broń jako osobne przedmioty (przedmioty/<id>.fbx/.glb) — jak kapelusz i kostur w kot_mag.zbuduj()."""
    prz = przedmioty(zestaw)
    p = postac(zestaw, id=id_modulu, prz=prz, tylko_idle=True)
    return [p] + [prz[RZECZY.index(r)].segmenty[0]["akc"] for r in ("helm", "miecz")]


def warianty(zestaw, id_modulu, rodzaj="plansze"):
    """Jak kot_mag.warianty: „plansze” — goły kot i kot w komplecie (id <moduł>_golas / <moduł>_komplet) oraz ikony
    całych przedmiotów; „eksport” — gołe ciało z zaczepami Ekw<Kosc>Attachment (tylko idle) i każdy segment kostny."""
    prz = przedmioty(zestaw)
    if rodzaj == "plansze":
        golas = copy.deepcopy(cialo())
        golas.id, golas.nazwa = id_modulu + "_golas", "Kot-wojownik — goły"
        golas.klipy = [k for k in golas.klipy if k.nazwa == "idle"]
        ikony = []
        for x in prz:
            ik = x.ikona()
            rzecz = x.id.rsplit("_", 1)[1]
            if rzecz in IKONA_OBROT and x.segmenty[0]["kosc"]:
                ik.ikona_obrot = IKONA_OBROT[rzecz]
            ikony.append(ik)
        return [golas, postac(zestaw, id=id_modulu + "_komplet", prz=prz, tylko_idle=True)] + ikony
    if rodzaj == "eksport":
        c = cialo(zaczepy_ekwipunku=True)
        c.id, c.nazwa = id_modulu + "_cialo", "Kot-wojownik (ciało bazowe)"
        c.klipy = [k for k in c.klipy if k.nazwa == "idle"]
        return [c] + [s["akc"] for x in prz for s in x.segmenty if s["kosc"]]
    raise ValueError("rodzaj: plansze albo eksport")


def ekwipunek_json(zestaw, id_modulu):
    """Dane ekwipunku (EKWIPUNEK.md pkt 5): jak kot_mag.ekwipunek_json, przedmioty na zaczepie z korektą kota;
    część na zaczepie ma też „korekta_upadku” (chwyty.py, KOREKTA UPADKU: grupa, od_klatki, do_klatki, pos, rot
    w ramce tego samego zaczepu; null — w upadku zostaje korekta chwytu), a bohater pole „upadek” (zasada)."""
    z = ZESTAWY[zestaw]
    prz = przedmioty(zestaw)
    opisy = [x.opis(KOREKTY_CHWYTU) for x in prz]
    for x, o in zip(prz, opisy):
        for s, cz in zip(x.segmenty, o["czesci"]):
            if s["kosc"] is None:
                kor = korekta_upadku(s["akc"])
                cz["korekta_upadku"] = None if kor is None else {
                    k: kor[k] for k in ("grupa", "od_klatki", "do_klatki", "pos", "rot")}
    return {"bohater": BOHATER, "cialo": KM.CIALO_TYP, "klasy": list(KLASY), "pula": "Lv 1-10",
            "arkusz": z["nazwa"], "kolumna_arkusza": z["kolumna"], "komplet_z_premia": z["komplet"],
            "kanon": list(komplet(zestaw)), "stroje": {"golas": [], "komplet": list(komplet(zestaw))},
            "korekty_chwytu": {k: {"zaczep": zz, "pos": list(pos), "rot": list(ob)}
                               for k, (zz, pos, ob) in KOREKTY_CHWYTU.items()},
            # klucze korekt: zaczep przedmiotu albo rodzaj chwytu broni (pole „chwyt” części broni, chwyty.py)
            "rodzaje_chwytu": CH.dla_gry(KOREKTY_CHWYTU),
            # znaczniki z pola „ukrywa” przedmiotów, które chowają części ciała (gra: Transparency = 1 tych kości)
            "znaczniki_ciala": {k: list(v) for k, v in ZNACZNIKI_CIALA.items()},
            # klip upadku: przejście spawu przedmiotu z korekty chwytu na „korekta_upadku” części (chwyty.py)
            "upadek": CH.upadek_dla_gry(),
            "przedmioty": opisy}


# --------------------------------------------------------------------------- liczby (bez Blendera)
def czesci_roblox(czesci):
    """Ile części Roblox da lista brył (ten sam rozkład co budowa z klocków w Studio)."""
    from swiat.postacie.biblioteka.roblox_klocki import rozloz
    return sum(len(rozloz(c)) for c in czesci)


def liczby(zestaw):
    """[(rzecz, id, nazwa, slot, bryły, części Roblox)] i (części gołego kota, części kota w komplecie)."""
    wiersze = []
    for x in przedmioty(zestaw):
        cz = [c for s in x.segmenty for c in s["akc"].czesci]
        wiersze.append((x.id[len(BOHATER) + len(zestaw) + 2:], x.id, x.nazwa, x.slot, len(cz), czesci_roblox(cz)))
    golas = cialo()
    p = postac(zestaw)
    zal = [c for a, *_ in p.zalozone for c in a.czesci]
    return wiersze, (czesci_roblox(golas.czesci), czesci_roblox(p.czesci) + czesci_roblox(zal))


# --------------------------------------------------------------------------- uszy w hełmie (bez Blendera)
def _w_srodku(czesci, Q):
    """Maska punktów Q (tablica N×3, układ hełmu) leżących w sumie brył hełmu. Walec i kula jak w Roblox (gładka
    elipsa / elipsoida — mniejsza niż ośmiokąt z Blendera, więc to ostrzejszy warunek); klin jak WedgePart (wysoka
    ściana +Z, skos ku −Z); reszta jako skrzynka (faza krawędzi pominięta)."""
    import numpy as np
    w = np.zeros(len(Q), dtype=bool)
    for c in czesci:
        L = (Q - np.asarray(c["p"])) @ np.asarray(c["R"])        # współrzędne w układzie bryły: R^T (q − p)
        x, y, z = L[:, 0], L[:, 1], L[:, 2]
        hx, hy, hz = (v / 2.0 for v in c["s"])
        if c["k"] == "walec":
            m = (np.abs(y) <= hy) & ((x / hx) ** 2 + (z / hz) ** 2 <= 1.0)
        elif c["k"] == "kula":
            m = (x / hx) ** 2 + (y / hy) ** 2 + (z / hz) ** 2 <= 1.0
        else:
            m = (np.abs(x) <= hx) & (np.abs(y) <= hy) & (np.abs(z) <= hz)
            if c["k"] == "klin":
                m &= (y + hy) * hz <= (z + hz) * hy
        w |= m
    return w


def _kierunki():
    """26 kierunków (osie, przekątne ścian i sześcianu), znormalizowane."""
    import numpy as np
    d = np.array([(a, b, c) for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1) if (a, b, c) != (0, 0, 0)],
                 dtype=float)
    return d / np.linalg.norm(d, axis=1)[:, None]


def _zapas(czesci, Q, krok=0.005, do=0.2):
    """Zapas mieszczenia punktów Q w sumie brył: dla każdego punktu najmniejsza (po 26 kierunkach) odległość, o którą
    można go przesunąć, nie wychodząc z hełmu (co `krok`, do `do`); punkt poza hełmem — wartość ujemna: −(najmniejsze
    przesunięcie, które wprowadza go do środka). Odporne na szwy między bryłami (kopuła z kilku walców). Zwraca
    (najmniejszy zapas, punkt)."""
    import numpy as np
    D = _kierunki()
    kroki = np.arange(krok, do + 1e-9, krok)
    w0 = _w_srodku(czesci, Q)
    zap = np.full(len(Q), do)
    for d in D:
        jeszcze = w0.copy()
        for t in kroki:
            if not jeszcze.any():
                break
            idx = np.nonzero(jeszcze)[0]
            wyszedl = ~_w_srodku(czesci, Q[idx] + t * d)
            zap[idx[wyszedl]] = np.minimum(zap[idx[wyszedl]], t - krok)
            jeszcze[idx[wyszedl]] = False
    poza = np.nonzero(~w0)[0]
    if len(poza):
        wejscie = np.full(len(poza), do)
        for d in D:
            nie = np.ones(len(poza), dtype=bool)
            for t in kroki:
                if not nie.any():
                    break
                idx = np.nonzero(nie)[0]
                wszedl = _w_srodku(czesci, Q[poza[idx]] + t * d)
                wejscie[idx[wszedl]] = np.minimum(wejscie[idx[wszedl]], t)
                nie[idx[wszedl]] = False
        zap[poza] = -wejscie
    i = int(np.argmin(zap))
    return float(zap[i]), tuple(float(v) for v in Q[i])


def _punkty_uszu(gestosc=6):
    """Punkty wypełniające bryły uszu gołego kota (ostrosłupy ścięte: interpolacja trójliniowa między podstawą
    a górą) w układzie modelu, w pozie spoczynku: [(kość, punkt)]."""
    pk = []
    for c in cialo().json()["czesci"]:
        if c["kosc"] not in ZNACZNIKI_CIALA["Uszy"]:
            continue
        sx, sy, sz = c["s"]
        gx, gz = c.get("gora") or (sx, sz)
        pgx, pgz = c.get("pg") or (0.0, 0.0)
        R = macierz_obrotu(*c["r"])
        n = gestosc
        for i in range(n + 1):
            for j in range(n + 1):
                for k in range(n + 1):
                    u, v, w = i / n, j / n, k / n               # v: od podstawy (0) do góry (1)
                    x = (1 - v) * (u - 0.5) * sx + v * (pgx + (u - 0.5) * gx)
                    z = (1 - v) * (w - 0.5) * sz + v * (pgz + (w - 0.5) * gz)
                    lok = razy_wektor(R, (x, (v - 0.5) * sy, z))
                    pk.append((c["kosc"], tuple(c["p"][t] + lok[t] for t in range(3))))
    return pk


def uszy_w_helmie(prz, klipy=True):
    """Zapas, z jakim hełm (Przedmiot na HatAttachment) mieści uszy kota (_zapas: studa; < 0 — ucho wystaje o tyle).
    Spoczynek (bryły uszu wypełnione punktami co ok. 0,1) oraz — informacyjnie, bo uszy pod hełmem są schowane —
    każda klatka klipów kota poza upadkiem (w upadku hełm zsuwa się z głowy; tylko wierzchołki brył uszu)."""
    import numpy as np
    p0 = cialo()
    zh = p0.zaczepy["HatAttachment"]
    st = p0.kosci[zh["kosc"]]["staw"]
    _, pos, _ob = KOREKTY_CHWYTU["HatAttachment"]
    hp = tuple(st[i] + zh["p"][i] + pos[i] for i in range(3))   # ramka hełmu w spoczynku (obrót zerowy)
    czesci = [dict(c, R=macierz_obrotu(*c["r"])) for c in prz.segmenty[0]["akc"].czesci_w()]
    punkty = _punkty_uszu()
    spoczynek = _zapas(czesci, np.array([[q[i] - hp[i] for i in range(3)] for _k, q in punkty]))
    ruch = {}
    if klipy:
        rogi = _punkty_uszu(1)
        for kl in p0.klipy:
            if kl.nazwa == "upadek":
                continue
            Q = []
            for f in range(kl.dlugosc + 1):
                W = KM._fk(p0, KM._poza_klatki(p0, kl, f))
                Rh, th = W["HatPivot"]
                for kosc, q in rogi:
                    R, t = W[kosc]
                    s0 = p0.kosci[kosc]["staw"]
                    v = razy_wektor(R, tuple(q[i] - s0[i] for i in range(3)))
                    w = tuple(t[i] + v[i] - th[i] for i in range(3))
                    l = tuple(sum(Rh[j][i] * w[j] for j in range(3)) for i in range(3))
                    Q.append([l[i] - pos[i] for i in range(3)])
            ruch[kl.nazwa] = _zapas(czesci, np.array(Q), krok=0.01)
    return spoczynek, ruch


# --------------------------------------------------------------------------- broń w ruchu: całe ciało i ziemia
KLIPY_RUCHU = ("idle", "chod")      # kot nie ma klipu biegu (bieg w świecie liczy gra: swiat/bohater_swiat)
KLIPY_WALKI = ("czar", "wiwat", "atak", "kula_ognia", "lodowy_pocisk", "bariera", "unik", "trafienie")
ZAPAS_RUCHU = 0.05                  # studa: najmniejszy odstęp broni od ciała i ziemi, który uznajemy za czysty
# strefa chwytu: punkty broni bliżej niż tyle od środka łapy, która ją trzyma (rękojeść, jelec), mogą wchodzić
# w przedramię tej łapy — to pięść z nadgarstkiem; kanoniczny kostur Kota-Maga siedzi w mankiecie rękawa na 0,24
# studa w każdym klipie. Dalej (ostrze, drzewce) przedramię liczy się jak każda inna bryła.
STREFA_CHWYTU = 0.45


def _odleglosc(b, L):
    """Odległość ze znakiem punktów L (N×3, układ stawu kości bryły b z kot_mag._bryly) od bryły b: > 0 na zewnątrz,
    < 0 w środku (głębokość). Skrzynka dokładnie; walec i kula jak gładkie elipsy Roblox (przybliżenie od dołu);
    klin jak WedgePart (skos ku −Z); stożek i ostrosłup — skrzynka zwężana ku górze."""
    import numpy as np
    d = (L - np.asarray(b["c"])) @ np.asarray(b["R"])
    x, y, z = d[:, 0], d[:, 1], d[:, 2]
    hx, hy, hz = b["h"]

    def pudlo(qx, qy, qz):
        q = np.stack([qx, qy, qz], axis=1)
        zew = np.linalg.norm(np.maximum(q, 0.0), axis=1)
        return zew + np.minimum(q.max(axis=1), 0.0)
    if b["k"] == "walec":
        m = min(hx, hz)
        qr = (np.sqrt((x / hx) ** 2 + (z / hz) ** 2) - 1.0) * m
        qy = np.abs(y) - hy
        q = np.stack([qr, qy], axis=1)
        return np.linalg.norm(np.maximum(q, 0.0), axis=1) + np.minimum(q.max(axis=1), 0.0)
    if b["k"] == "kula":
        return (np.sqrt((x / hx) ** 2 + (y / hy) ** 2 + (z / hz) ** 2) - 1.0) * min(hx, hy, hz)
    if b["g"] is not None:                                   # stożek / ostrosłup: zwężenie ku +Y
        t = np.clip((y + hy) / (2 * hy), 0.0, 1.0)
        sx = hx * (1 - t * (1 - b["g"][0]))
        sz = hz * (1 - t * (1 - b["g"][1]))
        return pudlo(np.abs(x - b["pg"][0] * t) - sx, np.abs(y) - hy, np.abs(z - b["pg"][1] * t) - sz)
    w = pudlo(np.abs(x) - hx, np.abs(y) - hy, np.abs(z) - hz)
    if b["k"] == "klin":                                     # wysoka ściana +Z, skos ku −Z
        n = math.hypot(2 * hy, 2 * hz)
        w = np.maximum(w, ((y + hy) * 2 * hz - (z + hz) * 2 * hy) / n)
    return w


def bron_w_ruchu(p, bron, dlon, klipy=None, krok=0.04, strefa=STREFA_CHWYTU, upadek=True):
    """Broń (id akcesorium) na postaci p względem WSZYSTKICH brył ciała, stroju i nakrycia głowy (bez kości dłoni,
    która ją trzyma — rękojeść siedzi w łapie z założenia; przedramię tej łapy tylko poza strefą chwytu, patrz
    STREFA_CHWYTU; punkty broni schowane w tej łapie się nie liczą — ich styk to styk łapy) i względem ziemi (y = 0),
    w każdej klatce klipów kota (kinematyka kot_mag._fk). Zwraca
    {klip: {"cialo": (odstęp, bryła, kość, klatka, bryła broni), "ziemia": (y, klatka),
    "chwyt": (odstęp w strefie chwytu, bryła, klatka)}};
    odstęp < 0 — broń wchodzi w bryłę na tyle studa; „bron” = która bryła broni jest najbliżej. Punkty broni: siatka
    co `krok` w bryłach broni. upadek=True: w klipie upadku broń z korektą upadku (korekta_upadku, jak w grze)."""
    import numpy as np
    br = KM._bryly(p)
    bryly_broni = [b for b in br if b["zrodlo"] == bron]
    if not bryly_broni:
        raise ValueError("Postać %s nie ma broni %s" % (p.id, bron))
    kosc_broni = bryly_broni[0]["kosc"]
    pkt, czyje = [], []
    for i, b in enumerate(bryly_broni):
        P = np.array(KM._siatka(b, krok))
        P = P[_odleglosc(b, P) <= 1e-6]                      # bez rogów skrzynki poza walcem / klinem
        pkt.append(P)
        czyje += [i] * len(P)
    P0 = np.concatenate(pkt)
    wpis = next(z for z in p.zalozone if z[0].id == bron)
    kor_up = korekta_upadku(wpis[0]) if upadek else None
    Rs, ts = _rama_korekty(p, wpis[1], wpis[2], wpis[3])
    cialo = [b for b in br if b["zrodlo"] != bron and b["kosc"] != dlon]
    lapa = [b for b in br if b["zrodlo"] != bron and b["kosc"] == dlon]
    przedramie = p.kosci[dlon]["rodzic"]
    sr_dloni = np.asarray(p.srodek(dlon))
    for b in cialo:
        b["_r"] = float(np.linalg.norm(b["h"]))
    wynik = {}
    for kl in p.klipy:
        if klipy and kl.nazwa not in klipy:
            continue
        najc, najz, najch = (9.0, "", "", -1, ""), (9.0, -1), (9.0, "", -1)
        for f in range(kl.dlugosc + 1):
            W = KM._fk(p, KM._poza_klatki(p, kl, f))
            Rw, tw = W[kosc_broni]
            P = P0
            if kor_up and kl.nazwa == KLIP_UPADKU:           # korekta upadku tej klatki (jak w grze)
                Rf, tf = _rama_korekty(p, wpis[1], *korekta_w_klatce(kor_up, (wpis[2], wpis[3]), f))
                Rd = Rf @ Rs.T
                P = P0 @ Rd.T + (tf - Rd @ ts)
            S = P @ np.asarray(Rw).T + np.asarray(tw)        # punkty broni w świecie
            yz = float(S[:, 1].min())                         # ziemia: cała broń (także w łapie)
            if yz < najz[0]:
                najz = (yz, f)
            srodek = S.mean(axis=0)
            rw = float(np.linalg.norm(S - srodek, axis=1).max())
            Rd, td = W[dlon]
            chwyt = np.linalg.norm(S - (np.asarray(Rd) @ sr_dloni + np.asarray(td)), axis=1) <= strefa
            # punkty broni schowane w łapie, która ją trzyma (rękojeść w pięści): to, czego dotykają, dotyka łapa
            Ld = (S - np.asarray(td)) @ np.asarray(Rd)
            w_lapie = np.zeros(len(S), dtype=bool)
            for b in lapa:
                w_lapie |= _odleglosc(b, Ld) <= 0.0
            for b in cialo:
                Rk, tk = W[b["kosc"]]
                Rk = np.asarray(Rk)
                cs = Rk @ np.asarray(b["c"]) + np.asarray(tk)
                if np.linalg.norm(cs - srodek) > rw + b["_r"] + 0.3:
                    continue
                L = (S - np.asarray(tk)) @ Rk                # układ stawu kości bryły
                od = np.where(w_lapie, 9.0, _odleglosc(b, L))
                if b["kosc"] == przedramie:                  # pięść z nadgarstkiem: osobno, poza wynikiem ciała
                    if chwyt.any() and float(od[chwyt].min()) < najch[0]:
                        najch = (float(od[chwyt].min()), b["n"], f)
                    od = np.where(chwyt, 9.0, od)
                i = int(od.argmin())
                if od[i] < najc[0]:
                    najc = (float(od[i]), b["n"], b["kosc"], f, bryly_broni[czyje[i]]["n"])
        wynik[kl.nazwa] = {"cialo": najc, "ziemia": najz, "chwyt": najch}
    return wynik


def wypisz_ruch(nazwa, w, zapas=ZAPAS_RUCHU):
    """Wiersze raportu bron_w_ruchu; zwraca liczbę klipów poniżej zapasu (ciało albo ziemia)."""
    zle = 0
    print("== %s" % nazwa)
    for kl, v in w.items():
        o, n, k, f, nb = v["cialo"]
        yz, fz = v["ziemia"]
        # upadek: broń ma leżeć NA ziemi (korekta upadku) — próg chwyty.PROG_UPADKU, odstęp od ciała informacyjnie
        zly = yz < CH.PROG_UPADKU if kl == KLIP_UPADKU else (o < zapas or yz < zapas)
        zle += zly
        ch = v["chwyt"]
        print("  %-14s ciało %+.3f (%s → %s/%s, kl. %d)   ziemia %+.3f (kl. %d)   chwyt %+.3f%s"
              % (kl, o, nb, k, n, f, yz, fz, min(ch[0], 9.0),
                 ("  <-- poniżej %.2f" % (CH.PROG_UPADKU if kl == KLIP_UPADKU else zapas)) if zly else ""))
    return zle


# --------------------------------------------------------------------------- upadek: korekta upadku (bez Blendera)
# Paweł 26.11.2026: „poprawić, żeby nie były pod ziemią” — przedmioty kota w klipie upadku (EKWIPUNEK.md pkt 15,
# zasada i dane dla gry: chwyty.py, KOREKTA UPADKU). Klip ciała zostaje wspólny; przedmiot dostaje drugą korektę
# w ramce swojego zaczepu, na którą gra przechodzi w klipie upadku (chwyty.miesz_korekte). Tu: liczenie tej korekty
# z geometrii przedmiotu, poza przedmiotu w każdej klatce (ta sama funkcja dla kontroli i dla renderów plansz)
# i kontrola względem ziemi.
KLIP_UPADKU = "upadek"
KROK_UPADKU = 0.5                    # kontrola: co pół klatki (gra w 60 kl./s pokazuje klip 30 kl./s co pół klatki)
_KOREKTY_UPADKU = {}                 # pamięć: id akcesorium -> korekta upadku (liczona na gołym kocie)


def _sprawdz_klatki_upadku():
    """Klatki grup kości nośnych w chwyty.UPADEK_KOTA = tory w kot_mag.UPADEK_LOT (wspólny klip się nie zmienia)."""
    for kosc, f0, f1, *_ in KM.UPADEK_LOT:
        g = next(d for d in CH.UPADEK_KOTA.values() if d["kosc"] == kosc)
        if (g["od_klatki"], g["do_klatki"]) != (f0, f1):
            raise ValueError("chwyty.UPADEK_KOTA[%s] ≠ kot_mag.UPADEK_LOT (%d, %d)" % (kosc, f0, f1))


def _rama_korekty(p, zaczep, pos, rot):
    """(R, t): ramka MODELU przedmiotu w układzie stawu kości zaczepu dla korekty (pos, rot) — jak Postac.json."""
    import numpy as np
    z = p.zaczepy[zaczep]
    Ra = np.asarray(macierz_obrotu(*z["r"]))
    return Ra @ np.asarray(macierz_obrotu(*rot)), np.asarray(z["p"], dtype=float) + Ra @ np.asarray(pos, dtype=float)


def _punkty_bryly(b, krok, powloka=False):
    """Punkty bryły (układ stawu): siatka co `krok` w środku bryły, a walec i kula dodatkowo gęsto po obwodzie
    (najniższy punkt leżącego walca nie musi leżeć w węźle siatki). powloka=True — tylko węzły przy ścianach (do
    szybkiego wyboru korekty: najniższy punkt zawsze leży na ścianie)."""
    import numpy as np
    P = np.array(KM._siatka(b, krok))
    od = _odleglosc(b, P)
    P = P[(od <= 1e-6) & (od >= -1.01 * krok)] if powloka else P[od <= 1e-6]
    if b["k"] in ("walec", "kula"):
        hx, hy, hz = b["h"]
        ka = np.linspace(0.0, 2 * np.pi, 36, endpoint=False)
        if b["k"] == "walec":
            L = np.array([(hx * math.cos(a), y, hz * math.sin(a))
                          for y in np.linspace(-hy, hy, max(2, int(math.ceil(2 * hy / krok)) + 1)) for a in ka])
        else:
            L = np.array([(hx * math.cos(a) * math.cos(e), hy * math.sin(e), hz * math.sin(a) * math.cos(e))
                          for e in np.linspace(-math.pi / 2, math.pi / 2, 13) for a in ka])
        P = np.concatenate([P, L @ np.asarray(b["R"]).T + np.asarray(b["c"])])
    return P


def punkty_przedmiotu(p, akc_id, krok=0.04, powloka=False):
    """Przedmiot założony na zaczepie postaci p: (kość, zaczep, korekta chwytu (pos, rot), punkty w układzie MODELU
    przedmiotu N×3 — siatka brył co `krok`, walce i kule także po obwodzie)."""
    import numpy as np
    wpis = next((z for z in p.zalozone if z[0].id == akc_id), None)
    if wpis is None:
        raise ValueError("Postać %s nie ma przedmiotu %s na zaczepie" % (p.id, akc_id))
    _akc, zaczep, pos, rot, _eksport = wpis
    br = [b for b in KM._bryly(p) if b["zrodlo"] == akc_id]
    P = np.concatenate([_punkty_bryly(b, krok, powloka) for b in br])
    R, t = _rama_korekty(p, zaczep, pos, rot)
    return br[0]["kosc"], zaczep, (tuple(pos), tuple(rot)), (P - t) @ R


def korekta_w_klatce(kor, kor_chwytu, klatka):
    """Korekta (pos, rot) przedmiotu w klatce klipu upadku: przejście z korekty chwytu na korektę upadku
    (chwyty.miesz_korekte — CFrame:Lerp gry); kor = korekta_upadku(...) albo None (zostaje korekta chwytu).
    Tej samej funkcji używają kontrola (--ruch) i rendery plansz upadku."""
    if not kor:
        return tuple(kor_chwytu[0]), tuple(kor_chwytu[1])
    return CH.miesz_korekte(kor_chwytu, (kor["pos"], kor["rot"]),
                            CH.alfa_upadku(klatka, kor["od_klatki"], kor["do_klatki"]))


def _swiat(p, kl, f):
    return KM._fk(p, KM._poza_klatki(p, kl, f))


def _w_swiecie(p, W, kosc, zaczep, kor, Q):
    """Punkty modelu Q przedmiotu w świecie dla korekty kor = (pos, rot) i pozy W (kot_mag._fk)."""
    import numpy as np
    Rm, tm = _rama_korekty(p, zaczep, *kor)
    Rb, tb = W[kosc]
    return (Q @ Rm.T + tm) @ np.asarray(Rb).T + np.asarray(tb)


def _klatki(kl, od=0.0, krok=KROK_UPADKU):
    n = int(round((kl.dlugosc - od) / krok))
    return [od + i * krok for i in range(n + 1)]


def _odstep_od_ciala(p, W, S, bez_zrodla, bez_kosci=()):
    """Najmniejszy odstęp punktów S (świat) od brył postaci (ciało, strój, inne przedmioty; bez brył przedmiotu
    `bez_zrodla` i kości `bez_kosci`): (odstęp, bryła, kość); < 0 — wchodzi na tyle studa."""
    import numpy as np
    sr = S.mean(axis=0)
    rw = float(np.linalg.norm(S - sr, axis=1).max())
    naj = (9.0, "", "")
    for b in KM._bryly(p):
        if b["zrodlo"] == bez_zrodla or b["kosc"] in bez_kosci:
            continue
        Rk, tk = W[b["kosc"]]
        Rk = np.asarray(Rk)
        if np.linalg.norm(Rk @ np.asarray(b["c"]) + np.asarray(tk) - sr) > rw + float(np.linalg.norm(b["h"])) + 0.1:
            continue
        od = _odleglosc(b, (S - np.asarray(tk)) @ Rk)
        i = int(od.argmin())
        if od[i] < naj[0]:
            naj = (float(od[i]), b["n"], b["kosc"])
    return naj


def _podnies(p, W, kosc, zaczep, Q, kor):
    """Korekta kor = (pos, rot) przesunięta w pionie świata (w ostatniej klatce) tak, żeby najniższy punkt
    przedmiotu w pozach W (lista wyników kot_mag._fk) był dokładnie ZAPAS_UPADKU nad ziemią (do trzech przybliżeń:
    kość może się jeszcze lekko ruszać, np. lewa łapa w odbiciu)."""
    import numpy as np
    z = p.zaczepy[zaczep]
    Ra = np.asarray(macierz_obrotu(*z["r"]))
    Rb = np.asarray(W[-1][kosc][0])
    pos = np.asarray(kor[0], dtype=float)
    for _ in range(3):
        y = min(float(_w_swiecie(p, w, kosc, zaczep, (tuple(pos), kor[1]), Q)[:, 1].min()) for w in W)
        if abs(y - CH.ZAPAS_UPADKU) < 1e-4:
            break
        pos = pos + Ra.T @ Rb.T @ np.array([0.0, CH.ZAPAS_UPADKU - y, 0.0])
    return tuple(float(v) for v in pos), tuple(kor[1])


def _ziemia_w_klipie(p, kl, kosc, zaczep, Q, kor, kor_chwytu, klatki):
    """(najniższy punkt przedmiotu nad ziemią, klatka) w klatkach `klatki` z przejściem korekty."""
    naj = (9.0, -1.0)
    for f in klatki:
        y = float(_w_swiecie(p, _swiat(p, kl, f), kosc, zaczep, korekta_w_klatce(kor, kor_chwytu, f), Q)[:, 1].min())
        if y < naj[0]:
            naj = (y, f)
    return naj


def _przedmiot_na_zaczepie(akc):
    """Goły kot z tym jednym przedmiotem (korekty kota; hełm chowa uszy jak hełmy puli) i samym klipem upadku."""
    prz = Przedmiot("upadek_" + akc.id, akc.nazwa, "Weapon", "Weapons", MIARA, cialo=KM.CIALO_TYP,
                    ukrywa=UKRYWA["helm"] if akc.zaczep == "HatAttachment" else ())
    prz.na_zaczepie(akc)
    p = ubierz(cialo(), [prz], id="upadek_" + akc.id, korekty=KOREKTY_CHWYTU)
    p.klipy = [k for k in p.klipy if k.nazwa == KLIP_UPADKU]
    return p


# okna przejścia (od_klatki, do_klatki) do wyboru: broń w prawej łapie — tor kostura (stałe); hełm — od zsunięcia
# z głowy (albo trochę wcześniej: hełm podskakuje), krócej niż lot kapelusza, żeby szybciej zszedł z głowy; lewa łapa —
# przejście musi skończyć się, zanim łapa zejdzie nisko (łapa nie puszcza przedmiotu)
OKNA = {"prawa": [(22, 33)],
        "helm": [(od, do) for od in (30, 28, 26) for do in (40, 38, 36, 34, 32) if do - od >= 4],
        "lewa": [(od, do) for od in (20, 18, 22, 16, 14, 12, 24) for do in (32, 30, 28, 26, 34) if do - od >= 6]}


def korekta_upadku(akc):
    """Korekta upadku przedmiotu na zaczepie kota (chwyty.UPADEK_KOTA): {"grupa", "zaczep", "od_klatki",
    "do_klatki", "pos", "rot", "ziemia", "cialo", "przejscie_cialo"} albo None (przedmiot lewej łapy, który w stałym
    chwycie nie schodzi pod ziemię, i zaczepy bez grupy). Liczona na gołym kocie z tym jednym przedmiotem — nie
    zależy od reszty stroju (tor kości nośnej i ruch łapy są wspólne). Ułożenie po upadku:
      prawa — obrót kostura Kota-Maga (KM.KOREKTY_CHWYTU, „ułożenie kostura”), rękojeść tam, gdzie rękojeść kostura;
      helm  — prosto, kopułą do góry (obrót wokół pionu jak kapelusz w kot_mag.UPADEK_LOT);
      lewa  — płasko pod łapą: najcieńsza oś przedmiotu (PCA punktów) pionowo, skręt wokół pionu co 15°;
    do tego przesunięcie w poziomie (prawa i hełm do 0,5 studa, lewa do 0,25, co 0,25), a potem pion: najniższy
    punkt po lądowaniu = ZAPAS_UPADKU. Okno przejścia: z OKNA (hełm i lewa łapa — kilka do wyboru). Wybór:
    najmniejszy koszt = głębokość wejścia w leżącego kota po lądowaniu + 0,5 × wejście w kota w trakcie przejścia
    głębsze niż w noszeniu + 0,2/stud przesunięcia + 0,001/° obrotu względem chwytu (lewa) + 0,002/klatkę odejścia
    od domyślnego okna, pod twardym warunkiem: w każdej pół klatce klipu najniższy punkt ≥ PROG_UPADKU (+0,002).
    „ziemia” = najniższy punkt w całym klipie (y, klatka), „cialo” = najmniejszy odstęp od kota od do_klatki
    (odstęp, bryła, kość, klatka), „przejscie_cialo” = to samo w trakcie przejścia (od 2. klatki okna),
    „noszenie_cialo” = odstęp w noszeniu (kl. 0) — informacyjnie."""
    import numpy as np
    if akc.id in _KOREKTY_UPADKU:
        return copy.deepcopy(_KOREKTY_UPADKU[akc.id])
    _sprawdz_klatki_upadku()
    p = _przedmiot_na_zaczepie(akc)
    kl = p.klipy[0]
    kosc, zaczep, Ks, Q = punkty_przedmiotu(p, akc.id)
    Qp = punkty_przedmiotu(p, akc.id, 0.06, powloka=True)[3]       # wybór: ściany co 0,06
    g = CH.grupa_upadku(zaczep)
    F = _klatki(kl)
    Wf = {f: _swiat(p, kl, f) for f in F}

    def ziemia(kor, od, do, klatki=F):
        k = None if kor is None else {"pos": kor[0], "rot": kor[1], "od_klatki": od, "do_klatki": do}
        return min((float(_w_swiecie(p, Wf[f], kosc, zaczep, korekta_w_klatce(k, Ks, f), Q)[:, 1].min()), f)
                   for f in klatki)

    if g == "lewa" and ziemia(None, 0, 1)[0] >= CH.PROG_UPADKU:
        g = None                                                     # w łapie i tak nad ziemią: bez korekty
    if g is None:
        _KOREKTY_UPADKU[akc.id] = None
        return None
    d = CH.UPADEK_KOTA[g]
    od0, do0 = d["od_klatki"], d["do_klatki"]
    bez = (kosc,) if g == "lewa" else ()
    Wk = Wf[float(kl.dlugosc)]
    Rb, tb = np.asarray(Wk[kosc][0]), np.asarray(Wk[kosc][1])
    Ra = np.asarray(macierz_obrotu(*p.zaczepy[zaczep]["r"]))
    pa = np.asarray(p.zaczepy[zaczep]["p"], dtype=float)
    Rs, ts = _rama_korekty(p, zaczep, *Ks)

    def w_ramce(o, Rk):
        """Korekta (pos, rot) dla rękojeści w punkcie o (świat, ostatnia klatka) i obrotu Rk w ramce zaczepu."""
        return tuple(float(v) for v in Ra.T @ (Rb.T @ (o - tb) - pa)), tuple(katy_z_macierzy(Rk.tolist()))

    obroty = []                                                      # (obrót w ramce zaczepu, koszt)
    if g == "prawa":
        _z, pos0, rot0 = KM.KOREKTY_CHWYTU["RightGripAttachment"]   # ułożenie kostura Kota-Maga
        o0 = Rb @ (Ra @ np.asarray(pos0, dtype=float) + pa) + tb
        obroty.append((np.asarray(macierz_obrotu(*rot0)), 0.0))
    else:
        o0 = Rb @ ts + tb                                            # rękojeść w stałym chwycie
        if g == "helm":
            lot = next(x for x in KM.UPADEK_LOT if x[0] == kosc)
            obroty.append((Ra.T @ Rb.T @ np.asarray(macierz_obrotu(0.0, lot[3][1], 0.0)), 0.0))
        else:
            _w, V = np.linalg.eigh(np.cov((Q - Q.mean(axis=0)).T))
            n, a = V[:, 0], V[:, 2]                                  # najcieńsza i najdłuższa oś modelu
            for zn in (1.0, -1.0):
                B = np.stack([a, zn * n, np.cross(a, zn * n)])       # wiersze: oś -> X świata, normalna -> góra
                for yaw in range(0, 360, 15):
                    Rk = Ra.T @ Rb.T @ np.asarray(macierz_obrotu(0.0, float(yaw), 0.0)) @ B
                    kat = math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(Rs.T @ Ra @ Rk) - 1) / 2))))
                    obroty.append((Rk, 0.001 * kat))
    sas = (-0.25, 0.0, 0.25) if g == "lewa" else (-0.5, -0.25, 0.0, 0.25, 0.5)
    po = [f for f in F if f >= do0 and f == int(f)]
    Wpo = [Wf[f] for f in po]
    Wcialo = [Wf[f] for f in sorted({float(do0), 37.0, 44.0, 52.0, float(kl.dlugosc)})]
    Qs = Qp                                                          # wybór: same ściany (odstęp od kota, ziemia)
    bez_przej = bez + (("RightHand",) if g == "prawa" else ())       # broń wypada z tej łapy
    ocenione = []
    for Rk, koszt in obroty:
        for dx in sas:
            for dz in sas:
                kor = _podnies(p, [Wk], kosc, zaczep, Qs, w_ramce(o0 + np.array([dx, 0.0, dz]), Rk))
                glab = max(0.0, -min(_odstep_od_ciala(p, w, _w_swiecie(p, w, kosc, zaczep, kor, Qs), akc.id, bez)[0]
                                     for w in Wcialo))
                ocenione.append((glab + koszt + 0.2 * math.hypot(dx, dz), kor))
    ocenione.sort(key=lambda x: x[0])
    okna = OKNA[g]
    y_stale = {f: float(_w_swiecie(p, Wf[f], kosc, zaczep, Ks, Qs)[:, 1].min()) for f in F}
    # jak głęboko przedmiot siedzi w ciele w noszeniu (kl. 0; hełm obejmuje głowę, rękojeść w pięści) — w trakcie
    # przejścia liczy się tylko wejście GŁĘBSZE niż to (od 2. klatki okna: przedmiot dopiero schodzi z głowy / łapy)
    noszenie = min(0.0, _odstep_od_ciala(p, Wf[0.0], _w_swiecie(p, Wf[0.0], kosc, zaczep, Ks, Qs), akc.id,
                                         bez_przej)[0])
    najl = None
    for i, (koszt, kor) in enumerate(ocenione):
        if i >= 12 and najl is not None and najl[0] == "ok":
            break                                                    # 12 najtańszych, dalej tylko bez ważnej
        kor = _podnies(p, Wpo, kosc, zaczep, Qs, kor)
        y_kon = {f: float(_w_swiecie(p, Wf[f], kosc, zaczep, kor, Qs)[:, 1].min()) for f in F}
        for od, do in okna:
            k = {"pos": kor[0], "rot": kor[1], "od_klatki": od, "do_klatki": do}
            y = min(min([y_stale[f] for f in F if f <= od] + [9.0]), min([y_kon[f] for f in F if f >= do] + [9.0]),
                    min([float(_w_swiecie(p, Wf[f], kosc, zaczep, korekta_w_klatce(k, Ks, f), Qs)[:, 1].min())
                         for f in F if od < f < do] + [9.0]))
            if y < CH.PROG_UPADKU + 0.002:
                if najl is None or (najl[0] == "zle" and y > najl[1]):
                    najl = ("zle", y, kor, od, do)
                continue
            przej = min(_odstep_od_ciala(p, Wf[f], _w_swiecie(p, Wf[f], kosc, zaczep, korekta_w_klatce(k, Ks, f), Qs),
                                         akc.id, bez_przej)[0] for f in range(od + 2, do + 1, 2))
            calk = koszt + 0.5 * max(0.0, noszenie - przej) + 0.002 * (abs(od - od0) + abs(do - do0))
            if najl is None or najl[0] == "zle" or calk < najl[1]:
                najl = ("ok", calk, kor, od, do)
    _stan, _k, kor, od, do = najl
    kor = _podnies(p, Wpo, kosc, zaczep, Q, kor)                     # pion jeszcze raz na pełnej siatce
    wynik = {"grupa": g, "zaczep": zaczep, "od_klatki": od, "do_klatki": do,
             "pos": [round(v, 4) + 0.0 for v in kor[0]], "rot": [round(v, 3) + 0.0 for v in kor[1]]}
    y, f = ziemia((wynik["pos"], wynik["rot"]), od, do)
    c, cp = (9.0, "", "", -1.0), (9.0, "", "", -1.0)
    for fw in F[::2]:
        S = _w_swiecie(p, Wf[fw], kosc, zaczep, korekta_w_klatce(wynik, Ks, fw), Q)
        if fw >= do:
            c = min(c, _odstep_od_ciala(p, Wf[fw], S, akc.id, bez) + (fw,), key=lambda x: x[0])
        elif fw >= od + 2:
            cp = min(cp, _odstep_od_ciala(p, Wf[fw], S, akc.id, bez_przej) + (fw,), key=lambda x: x[0])
    wynik["ziemia"] = [round(y, 4), f]
    wynik["cialo"] = [round(c[0], 3), c[1], c[2], c[3]]
    wynik["przejscie_cialo"] = [round(cp[0], 3), cp[1], cp[2], cp[3]]
    wynik["noszenie_cialo"] = round(noszenie, 3)
    _KOREKTY_UPADKU[akc.id] = wynik
    return copy.deepcopy(wynik)


def korekty_w_klatce_upadku(przedmioty, klatka, korekty=None):
    """Korekty chwytu bohatera (jak KOREKTY_CHWYTU) dla JEDNEJ klatki klipu upadku: wpis każdego przedmiotu na
    zaczepie z korektą upadku zastąpiony korektą tej klatki (korekta_w_klatce). Do renderów plansz upadku:
    ubierz(cialo(), przedmioty, korekty=…) i poza z klipu upadku w tej klatce = to, co pokaże gra."""
    from swiat.postacie.ekwipunek import korekta as _korekta
    k = dict(korekty or KOREKTY_CHWYTU)
    for prz in przedmioty:
        for s in prz.segmenty:
            if s["kosc"]:
                continue
            klucz = s["akc"].chwyt if getattr(s["akc"], "chwyt", None) in k else s["zaczep"]
            z, pos, rot = _korekta(k, s)
            kor = korekta_upadku(s["akc"])
            if kor:
                k[klucz] = (z,) + korekta_w_klatce(kor, (pos, rot), klatka)
    return k


def upadek_na_postaci(p, krok=0.04):
    """Kontrola klipu upadku: wszystko, co postać nosi na zaczepach (broń, hełm, przedmiot lewej łapy), z korektą
    upadku (korekta_upadku) względem ziemi co pół klatki i względem kota po lądowaniu. Zwraca
    {id: {"grupa", "korekta", "ziemia": (y, klatka), "koniec": y w ostatniej klatce, "cialo": (odstęp, bryła, kość,
    klatka) — po lądowaniu (od do_klatki; bez korekty od kl. 32), bez kości, na której przedmiot wisi}}."""
    kl = next(k for k in p.klipy if k.nazwa == KLIP_UPADKU)
    wynik = {}
    for akc, _z, _pos, _rot, _e in p.zalozone:
        kosc, zaczep, Ks, Q = punkty_przedmiotu(p, akc.id, krok)
        kor = korekta_upadku(akc)
        y, f = _ziemia_w_klipie(p, kl, kosc, zaczep, Q, kor, Ks, _klatki(kl))
        koniec = float(_w_swiecie(p, _swiat(p, kl, kl.dlugosc), kosc, zaczep,
                                  korekta_w_klatce(kor, Ks, kl.dlugosc), Q)[:, 1].min())
        od = float(kor["do_klatki"] if kor else 32)
        c = (9.0, "", "", -1.0)
        for fw in _klatki(kl, od, 2.0):
            W = _swiat(p, kl, fw)
            o = _odstep_od_ciala(p, W, _w_swiecie(p, W, kosc, zaczep, korekta_w_klatce(kor, Ks, fw), Q), akc.id,
                                 (kosc,) if not kosc.endswith("Pivot") else ())
            if o[0] < c[0]:
                c = o + (fw,)
        wynik[akc.id] = {"grupa": CH.grupa_upadku(zaczep), "korekta": kor, "ziemia": (y, f), "koniec": koniec,
                         "cialo": c}
    return wynik


def cialo_w_upadku(p):
    """(najniższy punkt brył ciała i stroju — bez przedmiotów na zaczepach — w klipie upadku, klatka): klip ciała
    kładzie gołego kota na ziemi; powłoki stroju są grubsze od futra (informacyjnie, bez korekty)."""
    import numpy as np
    kl = next(k for k in p.klipy if k.nazwa == KLIP_UPADKU)
    br = [b for b in KM._bryly(p) if b["zrodlo"] == "cialo"]
    naj = (9.0, -1)
    for f in range(kl.dlugosc + 1):
        W = _swiat(p, kl, f)
        y = min(float((np.asarray(b["pkt"]) @ np.asarray(W[b["kosc"]][0]).T)[:, 1].min() + W[b["kosc"]][1][1])
                for b in br)
        if y < naj[0]:
            naj = (y, f)
    return naj


def wypisz_upadek(nazwa, w):
    """Wiersze raportu upadek_na_postaci; zwraca liczbę przedmiotów pod progiem PROG_UPADKU w którejś klatce."""
    zle = 0
    print("== %s" % nazwa)
    for aid, v in w.items():
        y, f = v["ziemia"]
        zly = y < CH.PROG_UPADKU
        zle += zly
        kor = v["korekta"]
        o, n, k, fc = v["cialo"]
        print("  %-30s %-5s ziemia min %+.3f (kl. %4.1f), koniec %+.3f   kot po lądowaniu %+.3f (%s/%s, kl. %d)   %s%s"
              % (aid, v["grupa"] or "-", y, f, v["koniec"], o, k, n, fc,
                 "korekta kl. %d→%d" % (kor["od_klatki"], kor["do_klatki"]) if kor else "bez korekty",
                 "  <-- POD ZIEMIĄ (próg %.2f)" % CH.PROG_UPADKU if zly else ""))
    return zle


def zgodnosc_renderu(p, przedmioty, klatki=(22.0, 26.5, 33.0, 60.0)):
    """Rendery plansz upadku budują postać przez ubierz(..., korekty_w_klatce_upadku(...)), a kontrola liczy pozę
    przedmiotu z korekty klatki — ta sama funkcja korekta_w_klatce. Sprawdzenie: największa różnica położenia
    punktów przedmiotów (studa) między jednym a drugim sposobem w podanych klatkach."""
    import numpy as np
    kl = next(k for k in p.klipy if k.nazwa == KLIP_UPADKU)
    mx = 0.0
    for f in klatki:
        q = ubierz(cialo(), przedmioty, korekty=korekty_w_klatce_upadku(przedmioty, f))
        W = _swiat(p, kl, f)
        for wpis in q.zalozone:
            akc = wpis[0]
            kosc, zaczep, Ks, Q = punkty_przedmiotu(p, akc.id)
            S1 = _w_swiecie(p, W, kosc, zaczep, korekta_w_klatce(korekta_upadku(akc), Ks, f), Q)
            S2 = _w_swiecie(q, W, kosc, wpis[1], (wpis[2], wpis[3]), Q)
            mx = max(mx, float(np.abs(S1 - S2).max()))
    return mx


# --------------------------------------------------------------------------- przenikanie w klipach walki (bez Blendera)
def przenikanie(zestaw, gestosc=0.5):
    """Hełm i miecz w klipach walki kota: narzędzie swiat/postacie/przenikanie (to samo co przenikanie_stopni.py) na
    danych walki klasy „mag” (kot: te same kości i klipy co kot-wojownik), z bryłami kota w komplecie zestawu. Broń =
    miecz na kości StaffPivot (tam, gdzie kostur), nakrycie = hełm na HatPivot. Odniesienie: Kot-Mag w komplecie
    startowym (kapelusz, kostur). Zwraca {(scenariusz, strefa): (głębokość, co w co, chwila)} dla zestawu i startu."""
    from swiat.postacie import przenikanie_stopni as PS          # noqa: F401  (ustawia sys.path narzędzia)
    import aktorzy as A
    import pomiar as PM
    from swiat.postacie.biblioteka import roblox_klocki as RK
    wpis, d0 = A.PO_KLUCZU["mag"], A.wczytaj("mag")
    wzor = PM.SPEC["mag"]

    def jeden(p, bron):
        if wpis.get("skala"):
            p.skala = float(wpis["skala"])
        r = RK.rig(p)
        if r["kosci"] != d0["kosci"]:
            raise SystemExit("kości kota w komplecie ≠ kości danych walki maga")
        d = dict(d0)
        d["czesci"], d["grupy"], d["materialy"] = r["czesci"], r["grupy"], r["materialy"]
        pm = PM.Pomiar(d, {"bron_grupy": [bron], "glowa": list(wzor["glowa"]), "tulow": list(wzor["tulow"]),
                           "nakrycie": list(wzor["nakrycie"])})
        wynik = {}
        for w in PM.zmierz(pm, PM.scenariusze(pm.a, wpis, gestosc)):
            for strefa, st in w["strefy"].items():
                wynik[(w["nazwa"], strefa)] = (max(0.0, -st["m"]), "%s → %s" % (st["bron"], st["cialo"]),
                                              st["t"] or 0.0)
        return wynik, {z.nazwa: z.prog for z in pm.strefy}

    start, progi = jeden(KM.zbuduj()[0], "kot_mag_kostur")
    nowy, _ = jeden(postac(zestaw), _id(zestaw, "miecz"))
    return nowy, start, progi


# --------------------------------------------------------------------------- plansze (PIL, po przebudowie)
def _wzory():
    return os.environ.get("BC_WZORY_PRZEDMIOTOW") or os.path.join(REPO, "assets", "refs", "przedmioty_rycerz")


def _czcionki():
    from PIL import ImageFont
    try:
        return (ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22),
                ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 34),
                ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 18))
    except OSError:
        f = ImageFont.load_default()
        return f, f, f


TLO, KAFEL, TEKST, SZARY = "#1d1729", "#3a3152", "#ffffff", "#d9d0ee"


def plansza_arkusza(zestaw, cel_modulu, plik):
    """Arkusz Pawła (lewo) i ikony modeli 3D w tym samym układzie 3 × 2 (prawo), z liczbą części Roblox."""
    from PIL import Image, ImageDraw
    fn, fb, fm = _czcionki()
    z = ZESTAWY[zestaw]
    wiersze, (golas, razem) = liczby(zestaw)
    po_rzeczy = {w[0]: w for w in wiersze}
    H = 900
    im = Image.new("RGB", (1612 + 3 * 330 + 40, H + 150), TLO)
    dr = ImageDraw.Draw(im)
    dr.text((24, 16), "%s — arkusz Pawła (lewo) i modele 3D na kota (prawo) · propozycja" % z["nazwa"], font=fb,
            fill=TEKST)
    wz = os.path.join(_wzory(), z["plik"])
    if os.path.isfile(wz):
        ark = Image.open(wz).convert("RGB")
        ark.thumbnail((1580, H), Image.LANCZOS)
        im.paste(ark, (16, 80 + (H - ark.height) // 2))
    else:
        dr.rectangle((16, 80, 1596, 80 + H), outline=KAFEL, width=3)
        dr.text((60, 80 + H // 2), "brak pliku wzoru %s" % z["plik"], font=fn, fill=SZARY)
    K = 330
    x0 = 1612 + 10
    for i, r in enumerate(UKLAD_ARKUSZA):
        x, y = x0 + (i % 3) * K, 80 + (i // 3) * (K + 120)
        dr.rounded_rectangle((x + 6, y + 6, x + K - 6, y + K - 6), radius=16, fill=KAFEL)
        ik = os.path.join(cel_modulu, "ekwipunek", "ikony", "%s_ikona.png" % _id(zestaw, r))
        if os.path.isfile(ik):
            ob = Image.open(ik).convert("RGBA")
            ob.thumbnail((K - 30, K - 30), Image.LANCZOS)
            im.paste(ob, (x + (K - ob.width) // 2, y + (K - ob.height) // 2), ob)
        w = po_rzeczy[r]
        for j, t in enumerate((w[2], "%s · %d części Roblox" % (w[3], w[5]))):
            f = fn if j == 0 else fm
            dr.text((x + (K - dr.textlength(t, font=f)) // 2, y + K + 4 + 30 * j), t, font=f,
                    fill=TEKST if j == 0 else SZARY)
    stopka = ("Kot-wojownik: goły %d części Roblox, w komplecie %d (limit bohatera w świecie 220). "
              "Rysunek = wzór wyglądu; nazwy czekają na akceptację (pytanie 94)." % (golas, razem))
    dr.text((24, H + 100), stopka, font=fn, fill=SZARY)
    im.save(plik, quality=88)


def plansza_na_kocie(zestaw, cel_modulu, id_modulu, plik):
    """Kot-wojownik w komplecie: plansza z przebudowy (3/4, przód z manekinem skali, bok, tył) obok gołego kota."""
    from PIL import Image, ImageDraw
    fn, fb, fm = _czcionki()
    z = ZESTAWY[zestaw]
    pl = os.path.join(cel_modulu, "%s_plansza.jpg" % id_modulu)
    golas = os.path.join(cel_modulu, "ekwipunek", "%s_golas_bohater.jpg" % id_modulu)
    ob = Image.open(pl).convert("RGB")
    ob.thumbnail((1500, 1500), Image.LANCZOS)
    gw = 0
    g = None
    if os.path.isfile(golas):
        g = Image.open(golas).convert("RGB")
        g.thumbnail((520, ob.height), Image.LANCZOS)
        gw = g.width + 20
    im = Image.new("RGB", (ob.width + gw + 32, ob.height + 140), TLO)
    dr = ImageDraw.Draw(im)
    dr.text((16, 14), "%s na kocie-wojowniku — 3/4, przód (z manekinem skali R15), bok, tył" % z["nazwa"],
            font=fb, fill=TEKST)
    if g is not None:
        im.paste(g, (16, 76))
        dr.text((16 + (g.width - dr.textlength("goły kot (dla porównania)", font=fm)) // 2, 80 + g.height),
                "goły kot (dla porównania)", font=fm, fill=SZARY)
    im.paste(ob, (16 + gw, 76))
    nazwy = ", ".join(ZESTAWY[zestaw]["przedmioty"][r] for r in UKLAD_ARKUSZA)
    dr.text((16, ob.height + 92), nazwy, font=fn, fill=SZARY)
    im.save(plik, quality=88)


def plansze(zestaw, cel_modulu, id_modulu):
    """po_przebudowie modułu zestawu: dwie plansze w wynik/_pula_wojownika/ (arkusz obok modeli, kot w komplecie).
    Zwraca nazwy plików względem wynik/<moduł>/."""
    os.makedirs(PODGLADY, exist_ok=True)
    nazwy = []
    p1 = os.path.join(PODGLADY, "%szestaw_%s.jpg" % (PREFIKS_PLANSZ, zestaw))
    plansza_arkusza(zestaw, cel_modulu, p1)
    p2 = os.path.join(PODGLADY, "%szestaw_%s_na_kocie.jpg" % (PREFIKS_PLANSZ, zestaw))
    plansza_na_kocie(zestaw, cel_modulu, id_modulu, p2)
    for p in (p1, p2):
        nazwy.append("../_pula_wojownika/" + os.path.basename(p))
    return nazwy


def plansza_razem(plik=None):
    """Wszystkie zrobione zestawy: kadr bohaterski kota w komplecie i pod nim sześć ikon."""
    from PIL import Image, ImageDraw
    fn, fb, fm = _czcionki()
    zz = [z for z in zrobione() if os.path.isfile(os.path.join(TU, "wynik", "pula_wojownika_" + z,
                                                                  "pula_wojownika_%s_bohater.jpg" % z))]
    if not zz:
        raise SystemExit("Brak przebudowanych zestawów (wynik/pula_wojownika_<zestaw>/).")
    K, I = 560, 92
    im = Image.new("RGB", (len(zz) * K + 32, 80 + K + 2 * I + 120), TLO)
    dr = ImageDraw.Draw(im)
    dr.text((16, 14), "Pula wojownika Lv 1–10 — zestawy na kocie (propozycja)", font=fb, fill=TEKST)
    for i, z in enumerate(zz):
        cel = os.path.join(TU, "wynik", "pula_wojownika_" + z)
        ob = Image.open(os.path.join(cel, "pula_wojownika_%s_bohater.jpg" % z)).convert("RGB")
        ob.thumbnail((K - 12, K - 12), Image.LANCZOS)
        x = 16 + i * K
        im.paste(ob, (x + (K - ob.width) // 2, 76))
        t = "%d · %s" % (ZESTAWY[z]["kolumna"], ZESTAWY[z]["nazwa"])
        dr.text((x + (K - dr.textlength(t, font=fn)) // 2, 80 + K), t, font=fn, fill=TEKST)
        for j, r in enumerate(UKLAD_ARKUSZA):
            ik = os.path.join(cel, "ekwipunek", "ikony", "%s_ikona.png" % _id(z, r))
            if os.path.isfile(ik):
                o = Image.open(ik).convert("RGBA")
                o.thumbnail((I - 6, I - 6), Image.LANCZOS)
                xx = x + (K - 3 * I) // 2 + (j % 3) * I
                yy = 120 + K + (j // 3) * I
                dr.rounded_rectangle((xx + 2, yy + 2, xx + I - 2, yy + I - 2), radius=8, fill=KAFEL)
                im.paste(o, (xx + (I - o.width) // 2, yy + (I - o.height) // 2), o)
    plik = plik or os.path.join(PODGLADY, PREFIKS_PLANSZ + "zestawy_razem.jpg")
    os.makedirs(os.path.dirname(plik), exist_ok=True)
    im.save(plik, quality=88)
    return plik


SLABOSCI = [
    "Propozycja wyglądu z arkuszy Pawła; nazwy czekają na akceptację (pytanie 94), statystyk i cen tu nie ma.",
    "Ciało to goły Kot-Mag (rasa Człowiek), tak jak Koci Rycerz z kot_klasy.py; inne rasy kota mają te same klocki, "
    "więc przedmioty pasują na każdą z nich (sprawdzone tylko na rudym kocie).",
    "Hełm i miecz siedzą na kościach nośnych kota (HatPivot, StaffPivot): w klipie upadku hełm zsuwa się z głowy, "
    "a miecz wypada z łapy — jak kapelusz i kostur Kota-Maga.",
    "Cholewy butów to nakładka na łydce (kot nie ma właściciela powłoki na LowerLeg) — futro łydki zostaje pod "
    "cholewą; to jedyne rozszerzenie względem tabeli właścicieli w EKWIPUNEK.md.",
    "Hełmy (26.11.2026): niska kopuła i dwie osłony w kształcie kocich uszu, które mieszczą uszy (zapas 0,065 studa "
    "w spoczynku, --uszy); uszy schowane (ukrywa „Uszy”). W klipie upadku hełm zsuwa się, a uszu nie ma przez cały "
    "klip (eksport nie przełącza widoczności) — w grze odsłoni je dopiero skrypt.",
    "Upadek (Paweł 26.11.2026: „poprawić, żeby nie były pod ziemią”): tor lotu kości nośnych liczono dla kapelusza "
    "i kostura Kota-Maga, więc hełm kończył upadek do 0,79, a miecz do 0,54 studa pod ziemią. Teraz przedmiot ma "
    "KOREKTĘ UPADKU (chwyty.py; pole korekta_upadku w ekwipunek.json): w grze skrypt przestawia spaw z korekty "
    "chwytu na nią w oknie klatek klipu upadku (CFrame:Lerp) — miecz leży płasko przed kotem, hełm stoi obok "
    "głowy, nic nie schodzi pod ziemię (--ruch). Eksport FBX/GLB zna tylko korektę chwytu; skryptu w grze jeszcze "
    "nie ma. Hełm w trakcie zsuwania z głowy dalej przechodzi przez głowę (tor kapelusza, wspólny klip).",
    "Miecze trzyma chwyt „miecz” (chwyty.py, --ruch): w chodzie i spoczynku broń nie dotyka ciała (zapas ≥ 0,07) ani "
    "ziemi. W klipach walki atak, kula_ognia i lodowy_pocisk głowica (Giermek, Mleczarz) wchodzi do 0,11 studa "
    "w rękaw ramienia, gdy łapa jest przy barku (przed 26.11 do 0,18).",
    "Przenikanie broni w głowę, hełm i tułów w klipach walki: --przenikanie (dane walki maga, próg głowy 0,02, "
    "tułowia 0,10); całe ciało i ziemia klatka po klatce: --ruch. Kot nie ma klipu biegu — bieg w świecie liczy "
    "gra (swiat/bohater_swiat), tu niesprawdzany.",
    "W Roblox Studio nic z tego nie było budowane ani oglądane; nic nie zostało wgrane.",
]


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--razem" in sys.argv:
        print(plansza_razem())
        raise SystemExit(0)
    if "--ruch" in sys.argv:
        # miecze zestawów na swoich kotach (kryterium: chód i spoczynek ≥ ZAPAS_RUCHU — kod wyjścia), potem pozostałe
        # rodzaje chwytu z planszy chwytów na gołym kocie i na kocie w Zestawie Giermka (tylko raport)
        from swiat.postacie import pula_wojownika_chwyty as _PC
        _zle = 0
        for _z in zrobione():
            _w = bron_w_ruchu(postac(_z), _id(_z, "miecz"), "RightHand")
            wypisz_ruch("%s — %s (chwyt „miecz”)" % (ZESTAWY[_z]["nazwa"], ZESTAWY[_z]["przedmioty"]["miecz"]), _w)
            _zle += sum(1 for _k in KLIPY_RUCHU if min(_w[_k]["cialo"][0], _w[_k]["ziemia"][0]) < ZAPAS_RUCHU)
        _kontrolne = list(_PC.postacie_kontroli())
        for _opis, _p, _id_broni, _dlon, _strefa in _kontrolne:
            wypisz_ruch(_opis, bron_w_ruchu(_p, _id_broni, _dlon, strefa=_strefa))
        # upadek (Paweł 26.11.2026: „poprawić, żeby nie były pod ziemią”): wszystko, co kot nosi na zaczepach,
        # z korektą upadku, względem ziemi co pół klatki — kod wyjścia 1, gdy coś schodzi poniżej PROG_UPADKU
        print("\nUPADEK — broń, hełm i przedmiot lewej łapy z korektą upadku (chwyty.py); ziemia co pół klatki, "
              "próg %.2f; „kot po lądowaniu” = najmniejszy odstęp od ciała i stroju (informacyjnie)" % CH.PROG_UPADKU)
        _zle_up = 0
        for _z in zrobione():
            _p = postac(_z)
            _zle_up += wypisz_upadek("%s — miecz i hełm" % ZESTAWY[_z]["nazwa"], upadek_na_postaci(_p))
            _y, _f = cialo_w_upadku(_p)
            print("  (ciało ze strojem w upadku najniżej %+.3f, kl. %d — klip ciała, bez korekty; goły kot %+.3f)"
                  % (_y, _f, cialo_w_upadku(cialo())[0]))
        for _opis, _p, _id_broni, _dlon, _strefa in _kontrolne:
            _zle_up += wypisz_upadek(_opis, upadek_na_postaci(_p))
        _mx = zgodnosc_renderu(postac("giermek"), przedmioty("giermek"))
        _pc = [x for x in _kontrolne if x[2] in ("zwiadowca_luk_kot", "rycerz_tarcza_kot")]
        for _opis, _p, _id_broni, _dlon, _strefa in _pc:
            _a = next(z[0] for z in _p.zalozone if z[0].id == _id_broni)
            _mx = max(_mx, zgodnosc_renderu(_p, [_PC._bron_przedmiot(_a.chwyt, _a)]))
        print("zgodność kadrów plansz upadku z kontrolą (ta sama korekta klatki): największa różnica %.1e studa"
              % _mx)
        print("miecze zestawów: klipów chodu/spoczynku poniżej zapasu %.2f: %d; upadek: przedmiotów pod progiem "
              "%.2f: %d" % (ZAPAS_RUCHU, _zle, CH.PROG_UPADKU, _zle_up))
        raise SystemExit(1 if _zle or _zle_up or _mx > 1e-4 else 0)
    if "--uszy" in sys.argv:
        _helmy = [(ZESTAWY[_z]["nazwa"], przedmioty(_z)[RZECZY.index("helm")]) for _z in zrobione()]
        _zle = 0
        for _n, _h in _helmy:
            (_m, _q), _ruch = uszy_w_helmie(_h)
            _zle += _m < 0.04
            print("== %s: uszy w hełmie w spoczynku — zapas %.3f studa (najciaśniej przy x %.2f, y %.2f, z %.2f)"
                  % (_n, _m, _q[0], _q[1], _q[2]))
            print("   w ruchu (informacyjnie, uszy są schowane): " + ", ".join(
                "%s %.2f" % (_k, _v[0]) for _k, _v in sorted(_ruch.items(), key=lambda kv: kv[1][0])))
        raise SystemExit(1 if _zle else 0)
    if "--przenikanie" in sys.argv:
        for _z in zrobione():
            _n, _s, _pr = przenikanie(_z)
            _zle = sorted(((v[0], k, v) for k, v in _n.items()
                           if v[0] > _pr[k[1]] or v[0] - _s.get(k, (0,))[0] > 0.02), reverse=True)
            print("== %s: %d pomiarów, ponad próg albo gorzej niż Kot-Mag z kosturem: %d"
                  % (ZESTAWY[_z]["nazwa"], len(_n), len(_zle)))
            for _st in sorted({k[1] for k in _n}):
                _w = max(((v[0], k[0], v[1], v[2]) for k, v in _n.items() if k[1] == _st), default=(0, "", "", 0))
                _b = max((v[0] for k, v in _s.items() if k[1] == _st), default=0.0)
                print("  strefa %-8s najgłębiej %.3f (próg %.2f; Kot-Mag z kosturem najgłębiej %.3f)%s"
                      % (_st, _w[0], _pr[_st], _b, "  %s, %s, t=%.2f s" % (_w[1], _w[2], _w[3]) if _w[0] > 0 else ""))
            for _g, (_sc, _st), _v in _zle[:12]:
                print("  %-26s %-8s %.3f (Kot-Mag %.3f, próg %.2f)  %s  t=%.2f s"
                      % (_sc, _st, _g, _s.get((_sc, _st), (0,))[0], _pr[_st], _v[1], _v[2]))
        raise SystemExit(0)
    for _z in zrobione():
        _w, (_g, _r) = liczby(_z)
        print("== %s (kolumna %d) — kot goły %d części Roblox, w komplecie %d" % (ZESTAWY[_z]["nazwa"],
                                                                              ZESTAWY[_z]["kolumna"], _g, _r))
        for _x in _w:
            print("  %-9s %-32s %-34s %-7s %3d brył %3d części" % _x)
        if "--kontrola" in sys.argv:
            _p = postac(_z)
            _b, _u = _p.sprawdz()
            print("  sprawdzian postaci: błędy %d, uwagi %d" % (len(_b), len(_u)))
            for _x in _b + _u[:8]:
                print("   -", _x)
