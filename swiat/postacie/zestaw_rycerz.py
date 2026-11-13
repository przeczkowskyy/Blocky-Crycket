# -*- coding: utf-8 -*-
"""ZESTAW „RYCERZ” — ekwipunek gracza (poziom średni) dla klockowego awatara R15.

Kanon wyglądu: B&C/Postacie/Rycerz.md (stalowa zbroja, niebieski tabard, wielki miecz) i obraz KeyArt.png.
Kolory zestawu: stal, błękit, złoto. Herb zestawu (na tarczy): złota krokiew z rombem nad nią.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zestaw_rycerz.py --wyj <folder>
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zestaw_rycerz.py --wyj <folder> --eksport

Każdy przedmiot to osobne SZTYWNE akcesorium (jedna siatka, (0, 0, 0) = punkt zaczepienia). Rękawice i buty są
parami: jeden przedmiot w plecaku = dwie siatki (lewa i prawa), każda na swoim zaczepie. Opis przedmiotów (id,
nazwa, slot, kategoria plecaka, zaczep) jest w PRZEDMIOTY niżej.

zbuduj() zwraca przymiarkę (szary manekin R15 „zestaw_rycerz” z założonym kompletem, poza „trzymanie”) oraz
wszystkie akcesoria osobno (każde dostaje ikonę i własny eksport). Sygnet nie jest zakładany na przymiarkę
(schowałby się w rękawicy) — to przedmiot do ikony.

Dopasowanie (domyślny klockowy R15 biblioteki, 5,25 studa): głowa 1,25³, tułów 2×1,6×1, pas 2×0,4×1, ręce i nogi
1×1 w przekroju. Bryły leżą 0,03–0,05 nad skórą manekina; jedyne miejsca styku to szwy tułów–ręka (napierśnik
i pas są o 0,03–0,04 szersze niż tułów, tak jak klocki ramion przylegają do tułowia).

Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Akcesorium, manekin_r15

# stal trochę chłodniejsza niż w palecie biblioteki (jak u postaci Rycerza), plus jasna krawędź klingi
FILMY = ["chod"]                     # przebuduj.py: film i arkusz klatek tylko dla chodu przymiarki

PALETA = {"stal": "A8B4C8", "stal_cien": "75839C", "stal_ciemna": "4D576D", "stal_jasna": "DCE3EE",
          "niebieski": "2C6BE0", "niebieski_ciemny": "1E4AA8"}

GLOWA = 1.25          # klocek głowy manekina (sześcian)

# --------------------------------------------------------------------------- opis przedmiotów (dla gry / plecaka)
# slot: Helmet, Chest, Gloves, Boots, Belt, Weapon, OffHand, Amulet, Ring, Trinket
# kategoria plecaka: Weapons, Armor, Amulets, Others
# siatki: (id akcesorium = nazwa pliku FBX/GLB, punkt zaczepienia na ciele R15)
PRZEDMIOTY = [
    {"id": "zr_helm", "nazwa": "Hełm Rycerza z pióropuszem", "slot": "Helmet", "kategoria": "Armor",
     "zaczep": "HatAttachment", "siatki": [("zr_helm", "HatAttachment")]},
    {"id": "zr_napiersnik", "nazwa": "Napierśnik Rycerza z tabardem", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "NeckAttachment",
     "siatki": [("zr_napiersnik", "NeckAttachment"), ("zr_naramiennik_l", "LeftShoulderAttachment"),
                ("zr_naramiennik_p", "RightShoulderAttachment"), ("zr_pola", "WaistFrontAttachment")]},
    {"id": "zr_rekawice", "nazwa": "Stalowe rękawice Rycerza", "slot": "Gloves", "kategoria": "Armor",
     "zaczep": "Left/RightGripAttachment",
     "siatki": [("zr_rekawica_l", "LeftGripAttachment"), ("zr_rekawica_p", "RightGripAttachment")]},
    {"id": "zr_buty", "nazwa": "Stalowe buty z ostrogą", "slot": "Boots", "kategoria": "Armor",
     "zaczep": "Left/RightFootAttachment",
     "siatki": [("zr_but_l", "LeftFootAttachment"), ("zr_but_p", "RightFootAttachment")]},
    {"id": "zr_pas", "nazwa": "Szeroki pas Rycerza", "slot": "Belt", "kategoria": "Armor",
     "zaczep": "WaistCenterAttachment", "siatki": [("zr_pas", "WaistCenterAttachment")]},
    {"id": "zr_miecz", "nazwa": "Wielki miecz Rycerza", "slot": "Weapon", "kategoria": "Weapons",
     "zaczep": "RightGripAttachment", "siatki": [("zr_miecz", "RightGripAttachment")]},
    {"id": "zr_tarcza", "nazwa": "Tarcza z herbem", "slot": "OffHand", "kategoria": "Weapons",
     "zaczep": "LeftGripAttachment", "siatki": [("zr_tarcza", "LeftGripAttachment")]},
    {"id": "zr_amulet", "nazwa": "Amulet z niebieskim klejnotem", "slot": "Amulet", "kategoria": "Amulets",
     "zaczep": "NeckAttachment", "siatki": [("zr_amulet", "NeckAttachment")]},
    {"id": "zr_sygnet", "nazwa": "Sygnet Rycerza", "slot": "Ring", "kategoria": "Others",
     "zaczep": "LeftGripAttachment", "siatki": [("zr_sygnet", "LeftGripAttachment")]},
    {"id": "zr_ostroga", "nazwa": "Złota ostroga", "slot": "Trinket", "kategoria": "Others",
     "zaczep": "WaistCenterAttachment", "siatki": [("zr_ostroga", "WaistCenterAttachment")]},
]


def _akc(id, nazwa, zaczep, typ, ikona_obrot=(0, 0, 0), **kw):
    return Akcesorium(id, nazwa, zaczep=zaczep, typ=typ, paleta=PALETA, ikona_obrot=ikona_obrot, **kw)


def _herb(a, pos, skala=1.0, grubosc=0.04):
    """Herb zestawu (przód = +Z), pos = środek herbu: złota krokiew (apex w górze) i romb nad nią."""
    with a.uklad(pos=pos, skala=skala):
        for zn in (1, -1):
            a.blok("Krokiew", (zn * 0.19, -0.16, 0), (0.17, 0.62, grubosc), "zloto", "metal",
                   rot=(0, 0, zn * 43.5), faza=0.02)
        a.blok("Romb", (0, 0.36, 0), (0.24, 0.24, grubosc), "zloto", "metal", rot=(0, 0, 45), faza=0.02)


# --------------------------------------------------------------------------- hełm (HatAttachment)
def helm():
    """Otwarty hełm: kopuła, boki i tył zamknięte, okno na twarz; złota opaska, niebieski pióropusz łukiem w tył.
    (0, 0, 0) = środek górnej ściany głowy; głowa: y −1,25…0, x/z ±0,625. Wnętrze ma ciemną podszewkę (leży
    między głową a blachą), żeby w ikonie okno twarzy czytało się jako otwór."""
    a = _akc("zr_helm", "Hełm Rycerza z pióropuszem", "HatAttachment", "Hat", ikona_obrot=(-14, 15, 0))
    g, e, t = GLOWA / 2, 0.04, 0.13          # pół głowy, luz, grubość blachy
    w = g + e + t                            # zewnętrzna połowa szerokości (0,795)
    a.blok("Kopula", (0, 0.13, 0), (2 * w, 0.2, 2 * w), "stal", "metal")
    a.ostroslup("Kopula skos", (0, 0.34, 0), (2 * w, 0.22, 2 * w), "stal", "metal", gora=(1.2, 1.2))
    a.ostroslup("Czubek", (0, 0.5, 0), (1.2, 0.1, 1.2), "stal", "metal", gora=(0.8, 0.8), faza=0.02)
    # okno twarzy 1,0 × 0,8 studa (x ±0,5, y −0,32…−1,12) — jak w hełmie postaci Rycerza: twarz gracza widać
    zf = g + e + t / 2
    for zn in (1, -1):
        a.blok("Bok", (zn * (g + e + t / 2), -0.6, 0), (t, 1.24, 2 * w), "stal", "metal")
        a.blok("Policzek", (zn * 0.6475, -0.72, zf), (0.295, 0.8, t), "stal", "metal")
        a.blok("Nit", (zn * (w + 0.02), -0.3, 0.42), (0.05, 0.13, 0.13), "zloto", "metal", faza=0.0)
        a.blok("Nit", (zn * (w + 0.02), -0.3, -0.42), (0.05, 0.13, 0.13), "zloto", "metal", faza=0.0)
        a.blok("Podszewka bok", (zn * (g + 0.025), -0.62, 0), (0.02, 1.2, 2 * g), "stal_ciemna", "matowy", faza=0.0)
    a.blok("Tyl", (0, -0.6, -(g + e + t / 2)), (2 * g + 2 * e, 1.24, t), "stal", "metal")
    a.blok("Podszewka tyl", (0, -0.62, -(g + 0.025)), (2 * g, 1.2, 0.02), "stal_ciemna", "matowy", faza=0.0)
    a.blok("Czolo", (0, -0.17, zf), (2 * g + 2 * e, 0.3, t), "stal", "metal")
    a.blok("Czolo rant", (0, -0.31, zf + 0.06), (1.06, 0.06, 0.04), "zloto", "metal", faza=0.0)
    a.blok("Opaska", (0, -0.02, 0), (2 * w + 0.08, 0.16, 2 * w + 0.08), "zloto", "metal")
    a.blok("Podbrodek", (0, -1.18, zf), (2 * g + 2 * e, 0.12, t), "stal", "metal")
    # pióropusz: tulejka i pięć pęków po łuku (środek łuku C, promień R; pęk w kącie f: rx = −f)
    a.walec("Tulejka", (0, 0.62, 0.12), (0.36, 0.16, 0.36), "zloto", "metal", segm=8)
    C, R = (0.0, 0.78, -0.5), 0.62
    peki = [(20, 0.5, 0.46, "niebieski"), (55, 0.48, 0.44, "niebieski_jasny"), (90, 0.44, 0.4, "niebieski"),
            (125, 0.38, 0.36, "niebieski_jasny")]
    for i, (f, szer, grub, kol) in enumerate(peki):
        r = math.radians(f)
        a.blok("Pek%d" % (i + 1), (0, C[1] + R * math.sin(r), C[2] + R * math.cos(r)), (szer, 0.5, grub), kol,
               "matowy", rot=(-f, 0, 0), faza=0.04)
    r = math.radians(162)
    a.ostroslup("Pek5", (0, C[1] + R * math.sin(r), C[2] + R * math.cos(r)), (0.32, 0.5, 0.32), "niebieski",
                "matowy", rot=(-162, 0, 0), gora=(0.0, 0.1), faza=0.0)
    return a


# --------------------------------------------------------------------------- napierśnik z tabardem (NeckAttachment)
def napiersnik():
    """Napierśnik + naramienniki + niebieski tabard (przód i tył) ze złotą lamówką.
    (0, 0, 0) = środek górnej ściany tułowia; tułów: y −1,6…0, x ±1, z ±0,5; ręce x 1…2, góra ręki y = 0."""
    """Sam napierśnik z tabardem do linii bioder (X ±1,03, y ≥ −2,05). Naramienniki są osobnymi akcesoriami na
    ramionach (idą za ręką w ataku), a długa poła tabardu — osobną częścią na WaistFrontAttachment."""
    a = _akc("zr_napiersnik", "Napierśnik Rycerza z tabardem", "NeckAttachment", "Shoulder", ikona_obrot=(0, 20, 0))
    a.blok("Napiersnik", (0, -0.62, 0), (2.06, 1.2, 1.16), "stal", "metal")
    a.blok("Fartuch", (0, -1.42, 0), (2.02, 0.4, 1.1), "stal_cien", "metal")
    a.blok("Obojczyk", (0, -0.07, 0.6), (1.9, 0.09, 0.06), "zloto", "metal", faza=0.0)
    zt = 0.625                                   # tabard leży przed napierśnikiem (z 0,595…0,655)
    for strona, zz in (("przod", 1), ("tyl", -1)):
        a.blok("Tabard " + strona, (0, -1.07, zz * zt), (1.16, 1.96, 0.06), "niebieski", "matowy", faza=0.02)
        a.blok("Tabard rabek " + strona, (0, -2.01, zz * (zt + 0.02)), (1.24, 0.08, 0.08), "zloto", "metal", faza=0.0)
        for zn in (1, -1):
            a.blok("Lamowka", (zn * 0.6, -1.07, zz * (zt + 0.02)), (0.08, 1.96, 0.08), "zloto", "metal", faza=0.0)
    return a


def naramiennik(strona):
    """Naramiennik na Left/RightShoulderAttachment (środek góry ramienia): wypukła płyta 0,1 nad barkiem i dwie
    lamy na zewnątrz; szerokość ≤ 1,3."""
    zn = 1 if strona == "l" else -1
    zaczep = "LeftShoulderAttachment" if zn > 0 else "RightShoulderAttachment"
    a = _akc("zr_naramiennik_" + strona, "Naramiennik Rycerza (%s)" % ("lewy" if zn > 0 else "prawy"), zaczep,
             "Shoulder", ikona_obrot=(0, zn * 40, 0))
    a.ostroslup("Naramiennik", (zn * 0.04, 0.17, 0), (1.2, 0.3, 1.26), "stal", "metal", gora=(0.8, 0.96),
                przes_gory=(-zn * 0.1, 0), faza=0.04)
    a.blok("Lama", (zn * 0.45, -0.02, 0), (0.36, 0.16, 1.24), "stal", "metal", rot=(0, 0, -zn * 35))
    a.blok("Lama bok", (zn * 0.57, -0.24, 0), (0.12, 0.4, 1.2), "stal_cien", "metal")
    a.blok("Rant", (zn * 0.58, -0.45, 0), (0.14, 0.06, 1.22), "zloto", "metal", faza=0.0)
    for zz in (0.34, -0.34):
        a.blok("Nit", (zn * 0.645, -0.24, zz), (0.04, 0.12, 0.12), "zloto", "metal", faza=0.0)
    return a


def pola():
    """Długa poła tabardu na WaistFrontAttachment (przód pasa): szerokość 0,9, wysunięta 0,25 przed biodro — uda
    w chodzie i w ataku przechodzą za nią, nie przez nią."""
    a = _akc("zr_pola", "Poła tabardu Rycerza", "WaistFrontAttachment", "Waist", ikona_obrot=(0, 20, 0))
    with a.uklad(pos=(0, -0.12, 0.28), obrot=(-8, 0, 0)):
        a.blok("Pola", (0, -0.42, 0), (0.86, 0.84, 0.06), "niebieski", "matowy", faza=0.02)
        a.ostroslup("Pola szpic", (0, -0.98, 0), (0.86, 0.28, 0.06), "niebieski", "matowy", rot=(0, 0, 180),
                    gora=(0.0, 0.06), faza=0.0)
        for zn in (1, -1):
            a.blok("Lamowka", (zn * 0.43, -0.42, 0.02), (0.06, 0.84, 0.08), "zloto", "metal", faza=0.0)
            a.blok("Lamowka szpic", (zn * 0.22, -0.98, 0.02), (0.06, 0.5, 0.08), "zloto", "metal",
                   rot=(0, 0, zn * 57), faza=0.0)
        a.blok("Zawieszenie", (0, 0.02, -0.12), (0.9, 0.12, 0.3), "brazowy_ciemny", "matowy", faza=0.02)
        _herb(a, (0, -0.45, 0.05), skala=0.45)
    return a


# --------------------------------------------------------------------------- rękawice (Left/RightGripAttachment)
def rekawica(strona):
    """Rękawica: płyta na dłoń z kciukiem, rozszerzony mankiet ze złotym rantem i niebieskim klejnotem.
    Zaczep Grip ma obrót (90, 0, 0), więc bryły idą w układzie obróconym z powrotem — wtedy osie są jak w modelu
    przy zwisającej ręce: (0, 0, 0) = środek dłoni, dłoń y −0,15…0,15, przedramię y 0,15…0,9, x/z ±0,5."""
    zn = 1 if strona == "l" else -1                   # zewnętrzna strona ręki: lewa +X, prawa −X
    zaczep = "LeftGripAttachment" if zn > 0 else "RightGripAttachment"
    nazwa = "Rękawica Rycerza (%s)" % ("lewa" if zn > 0 else "prawa")
    # ikona od grzbietu dłoni, otwór mankietu odchylony od kamery
    a = _akc("zr_rekawica_" + strona, nazwa, zaczep, "Inne", ikona_obrot=(55, 0, 0) if zn > 0 else (125, 180, 0))
    c = zn * 0.07                                     # od strony tułowia najwyżej 0,48 od środka dłoni
    with a.uklad(obrot=(-90, 0, 0)):
        a.blok("Dlon", (c, 0.0, 0.02), (1.1, 0.34, 1.12), "stal", "metal")
        a.blok("Kostki", (c, -0.19, 0.03), (1.08, 0.08, 1.1), "stal_cien", "metal", faza=0.0)
        for i in range(4):                               # cztery palce w rzędzie od przodu do tyłu dłoni
            a.blok("Palec", (c, -0.31, 0.39 - i * 0.26), (0.98, 0.2, 0.22), "stal", "metal", faza=0.03)
        a.blok("Kciuk", (-zn * 0.31, -0.02, 0.64), (0.32, 0.36, 0.2), "stal", "metal", faza=0.04)
        a.blok("Grzbiet", (c + zn * 0.58, 0.0, 0.04), (0.07, 0.22, 0.86), "zloto", "metal", faza=0.0)
        a.ostroslup("Mankiet", (c, 0.47, 0), (1.1, 0.6, 1.16), "stal", "metal", gora=(1.22, 1.36),
                    przes_gory=(zn * 0.07, 0), faza=0.03)
        a.blok("Rant", (c + zn * 0.07, 0.79, 0), (1.24, 0.07, 1.4), "zloto", "metal", faza=0.0)
        a.blok("Otwor", (c + zn * 0.07, 0.833, 0), (1.08, 0.02, 1.22), "stal_ciemna", "matowy", faza=0.0)
        a.blok("Klejnot", (c + zn * 0.64, 0.5, 0), (0.05, 0.2, 0.2), "niebieski_jasny", "swiecacy", rot=(45, 0, 0),
               faza=0.0)
    return a


# --------------------------------------------------------------------------- buty (Left/RightFootAttachment)
def but(strona):
    """But: podeszwa, stopa z noskiem, rozszerzona cholewa ze złotym rantem, pasek i ostroga z gwiazdką na pięcie.
    (0, 0, 0) = spód stopy; stopa y 0…0,35, podudzie y 0,35…1,15, x/z ±0,5."""
    zn = 1 if strona == "l" else -1
    zaczep = "LeftFootAttachment" if zn > 0 else "RightFootAttachment"
    nazwa = "But Rycerza (%s)" % ("lewy" if zn > 0 else "prawy")
    a = _akc("zr_but_" + strona, nazwa, zaczep, "Inne",
             ikona_obrot=(0, -70, 0) if zn > 0 else (0, 110, 0))      # z boku: nosek, cholewa i ostroga
    c = zn * 0.08                                     # asymetrycznie: od drugiej nogi najwyżej 0,48, na zewnątrz 0,64
    a.blok("Podeszwa", (c, 0.04, 0.14), (1.12, 0.12, 1.4), "stal_ciemna", "matowy")
    a.blok("Stopa", (c, 0.24, 0), (1.1, 0.34, 1.12), "stal", "metal")
    a.klin("Nosek", (c, 0.22, 0.7), (1.08, 0.28, 0.28), "stal", "metal", rot=(0, 180, 0))
    a.ostroslup("Cholewa", (c, 0.72, 0), (1.12, 0.66, 1.12), "stal", "metal", gora=(1.12, 1.2), faza=0.03)
    a.blok("Rant", (c + zn * 0.04, 1.07, 0), (1.2, 0.08, 1.28), "zloto", "metal", faza=0.0)
    a.blok("Otwor", (c, 1.115, 0), (1.02, 0.02, 1.14), "stal_ciemna", "matowy", faza=0.0)
    a.blok("Nagolennik", (c, 0.74, 0.62), (0.5, 0.48, 0.06), "stal_cien", "metal", faza=0.02)
    a.blok("Klejnot", (c, 0.74, 0.66), (0.18, 0.18, 0.04), "niebieski_jasny", "swiecacy", rot=(0, 0, 45), faza=0.0)
    a.blok("Pasek", (c, 0.43, 0), (1.12, 0.08, 1.16), "brazowy_ciemny", "matowy", faza=0.0)
    # ostroga: szyjka w tył i gwiazdka (kółko + kolce w płaszczyźnie YZ)
    a.blok("Ostroga szyjka", (0, 0.43, -0.7), (0.09, 0.09, 0.3), "zloto", "metal", faza=0.0)
    a.walec("Ostroga kolko", (0, 0.43, -0.9), (0.2, 0.05, 0.2), "zloto", "metal", rot=(0, 0, 90), segm=8)
    for k in (0, 45, 90, 135):
        a.blok("Ostroga kolec", (0, 0.43, -0.9), (0.04, 0.4, 0.05), "zloto", "metal", rot=(k, 0, 0), faza=0.0)
    return a


# --------------------------------------------------------------------------- pas (WaistCenterAttachment)
def pas():
    """Szeroki brązowy pas: obwód przy ciele, nakładki przód/tył na tabardzie, duża złota klamra.
    (0, 0, 0) = środek LowerTorso (y −0,2…0,2, x ±1, z ±0,5); tabard leży na z ±0,6…0,66."""
    a = _akc("zr_pas", "Szeroki pas Rycerza", "WaistCenterAttachment", "Waist", ikona_obrot=(0, 25, 0))
    a.blok("Pas", (0, 0, 0), (2.08, 0.46, 1.16), "brazowy", "matowy")
    for zz in (1, -1):
        a.blok("Nakladka", (0, 0, zz * 0.64), (1.42, 0.46, 0.14), "brazowy", "matowy")
        for zn in (1, -1):
            a.blok("Cwiek", (zn * 0.55, 0, zz * 0.73), (0.1, 0.1, 0.05), "zloto", "metal", faza=0.0)
    a.blok("Klamra", (0, 0, 0.75), (0.72, 0.62, 0.1), "zloto", "metal", faza=0.04)
    a.blok("Klamra srodek", (0, 0, 0.81), (0.4, 0.3, 0.04), "brazowy_ciemny", "matowy", faza=0.0)
    a.blok("Kolec", (0, 0, 0.84), (0.08, 0.36, 0.04), "zloto", "metal", faza=0.0)
    a.blok("Klejnot", (0, 0.22, 0.82), (0.12, 0.12, 0.04), "niebieski_jasny", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return a


# --------------------------------------------------------------------------- miecz (RightGripAttachment)
def miecz():
    """Wielki miecz: rękojeść w (0, 0, 0), ostrze w +Y, płaz do przodu (+Z). Klinga z jasnymi krawędziami
    i ciemnym zbroczem, jelec z zadartymi końcami, niebieska skórzana rękojeść, tarczowa głowica z klejnotem."""
    a = _akc("zr_miecz", "Wielki miecz Rycerza", "RightGripAttachment", "Bron", ikona_obrot=(0, 0, -45))
    a.walec("Rekojesc", (0, 0, 0), (0.25, 1.24, 0.25), "niebieski_ciemny", "matowy", segm=8)
    for y in (-0.3, 0.3):
        a.walec("Okucie", (0, y, 0), (0.3, 0.07, 0.3), "zloto", "metal", segm=8, faza=0.0)
    a.walec("Glowica", (0, -0.74, 0), (0.48, 0.2, 0.48), "zloto", "metal", rot=(90, 0, 0), segm=8)
    a.blok("Glowica klejnot", (0, -0.74, 0.12), (0.16, 0.16, 0.04), "niebieski_jasny", "swiecacy",
           rot=(0, 0, 45), faza=0.0)
    a.blok("Jelec", (0, 0.7, 0), (1.3, 0.2, 0.3), "zloto", "metal", faza=0.04)
    for zn in (1, -1):
        a.blok("Jelec koniec", (zn * 0.74, 0.8, 0), (0.3, 0.22, 0.32), "zloto", "metal", rot=(0, 0, zn * 32),
               faza=0.04)
    a.blok("Jelec srodek", (0, 0.72, 0), (0.46, 0.4, 0.4), "stal_ciemna", "metal", faza=0.06)
    for zz in (1, -1):
        a.blok("Klejnot", (0, 0.72, zz * 0.21), (0.2, 0.2, 0.04), "niebieski", "swiecacy", rot=(0, 0, 45), faza=0.0)
    a.blok("Klinga", (0, 2.32, 0), (0.6, 2.84, 0.16), "stal", "metal", faza=0.03)
    for zn in (1, -1):
        a.blok("Krawedz", (zn * 0.33, 2.32, 0), (0.08, 2.84, 0.1), "stal_jasna", "metal", faza=0.0)
    a.blok("Zbrocze", (0, 2.1, 0), (0.14, 2.2, 0.2), "stal_cien", "metal", faza=0.0)
    a.ostroslup("Sztych", (0, 4.04, 0), (0.76, 0.6, 0.16), "stal_jasna", "metal", gora=(0.0, 0.1), faza=0.0)
    return a


# --------------------------------------------------------------------------- tarcza (LeftGripAttachment)
def tarcza():
    """Tarcza trójkątna (heater) z herbem na zewnętrznej stronie lewego przedramienia. W układzie ręki (jak
    rękawica) lico tarczy patrzy w +X, skręcone o 10° do przodu; dwa pasy łączą ją z przedramieniem."""
    a = _akc("zr_tarcza", "Tarcza z herbem", "LeftGripAttachment", "Bron", ikona_obrot=(90, -80, 0))
    with a.uklad(obrot=(-90, 0, 0)):
        for y in (0.3, 0.72):
            a.blok("Pas", (0.6, y, 0), (0.24, 0.12, 0.42), "brazowy_ciemny", "matowy", faza=0.0)
        with a.uklad(pos=(0.78, 0.42, 0), obrot=(0, 80, 0)):           # lico tarczy = lokalne +Z
            a.blok("Rama", (0, 0.45, 0), (1.5, 0.7, 0.12), "zloto", "metal", faza=0.04)
            a.ostroslup("Rama szpic", (0, -0.45, 0), (1.5, 1.1, 0.12), "zloto", "metal", rot=(0, 0, 180),
                        gora=(0.0, 0.12), faza=0.0)
            a.blok("Pole", (0, 0.44, 0.07), (1.28, 0.64, 0.06), "niebieski", "matowy", faza=0.0)
            a.ostroslup("Pole szpic", (0, -0.36, 0.07), (1.28, 0.96, 0.06), "niebieski", "matowy", rot=(0, 0, 180),
                        gora=(0.0, 0.06), faza=0.0)
            a.blok("Glowa tarczy", (0, 0.62, 0.085), (1.28, 0.26, 0.06), "stal", "metal", faza=0.02)
            _herb(a, (0, 0.0, 0.115), skala=0.75)
            a.blok("Tyl", (0, 0.25, -0.08), (0.9, 0.8, 0.06), "stal_ciemna", "metal", faza=0.0)
    return a


# --------------------------------------------------------------------------- amulet (NeckAttachment)
def amulet():
    """Złoty łańcuch w szpic na piersi i romb ze złota z niebieskim klejnotem; leży na napierśniku/tabardzie.
    (0, 0, 0) = środek górnej ściany tułowia. Łańcuch obchodzi szyję poza klockiem głowy (|x| ≥ 0,67)."""
    a = _akc("zr_amulet", "Amulet z niebieskim klejnotem", "NeckAttachment", "Neck", ikona_obrot=(10, 0, 0))
    zc = 0.7
    for zn in (1, -1):
        a.blok("Lancuch przod", (zn * 0.37, -0.22, zc), (0.06, 0.66, 0.06), "zloto", "metal",
               rot=(0, 0, -zn * 57), faza=0.0)
        a.blok("Lancuch bok", (zn * 0.69, 0.0, 0.12), (0.06, 0.06, 1.1), "zloto", "metal", faza=0.0)
        a.blok("Lancuch naroze", (zn * 0.56, -0.02, -0.55), (0.06, 0.06, 0.42), "zloto", "metal",
               rot=(0, zn * 45, 0), faza=0.0)
    a.blok("Lancuch tyl", (0, -0.03, -0.66), (0.86, 0.06, 0.06), "zloto", "metal", faza=0.0)
    a.blok("Uszko", (0, -0.4, zc + 0.01), (0.1, 0.14, 0.06), "zloto", "metal", faza=0.0)
    a.blok("Oprawa", (0, -0.74, zc + 0.02), (0.6, 0.6, 0.08), "zloto", "metal", rot=(0, 0, 45), faza=0.03)
    a.blok("Klejnot", (0, -0.74, zc + 0.08), (0.4, 0.4, 0.08), "niebieski_jasny", "swiecacy",
           rot=(0, 0, 45), faza=0.03)
    a.blok("Kropla", (0, -1.2, zc + 0.02), (0.14, 0.14, 0.06), "niebieski", "swiecacy", rot=(0, 0, 45), faza=0.0)
    return a


# --------------------------------------------------------------------------- sygnet (LeftGripAttachment, do ikony)
def sygnet():
    """Sygnet: ośmiokątna obrączka (otwór wzdłuż Z) i masywna główka z niebieską pieczęcią i złotym rombem."""
    a = _akc("zr_sygnet", "Sygnet Rycerza", "LeftGripAttachment", "Inne", ikona_obrot=(20, 0, 0), przymierz=False)
    r = 0.28
    for k in range(45, 360, 45):                         # na górze (0°) siedzi główka
        f = math.radians(k)
        a.blok("Obraczka", (r * math.sin(f), r * math.cos(f), 0), (0.27, 0.1, 0.16), "zloto", "metal",
               rot=(0, 0, -k), faza=0.0)
    a.blok("Glowka", (0, 0.36, 0), (0.42, 0.18, 0.26), "zloto", "metal", faza=0.04)
    a.blok("Pieczec", (0, 0.465, 0), (0.3, 0.04, 0.18), "niebieski", "polysk", faza=0.0)
    a.blok("Pieczec przod", (0, 0.36, 0.14), (0.26, 0.11, 0.03), "niebieski", "polysk", faza=0.0)
    a.blok("Romb", (0, 0.36, 0.165), (0.08, 0.08, 0.03), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
    return a


# --------------------------------------------------------------------------- ostroga (WaistCenterAttachment)
def ostroga():
    """Złota ostroga-talizman zawieszona na pasie z przodu, nad lewym udem. Wisi pionowo: kabłąk (U) u góry,
    szyjka w dół, gwiazdka na dole; w ikonie obrócona poziomo (profil ostrogi: kabłąk — szyjka — gwiazdka)."""
    # wisi na prawym boku pasa (x = −1,06: tuż za udem, nie w kroku), płaszczyzną na zewnątrz
    a = _akc("zr_ostroga", "Złota ostroga", "WaistCenterAttachment", "Waist", ikona_obrot=(0, -90, 90))
    with a.uklad(pos=(-1.06, -0.36, 0.0), obrot=(0, -90, 0)):
        a.blok("Zawieszka", (-0.21, 0.39, -0.01), (0.05, 0.16, 0.04), "zloto_ciemne", "metal", faza=0.0)
        a.blok("Kablak dol", (0, 0.0, 0), (0.48, 0.08, 0.06), "zloto", "metal", faza=0.0)
        for zn in (1, -1):
            a.blok("Kablak ramie", (zn * 0.21, 0.14, 0), (0.08, 0.32, 0.06), "zloto", "metal", faza=0.0)
            a.blok("Kablak guz", (zn * 0.21, 0.3, 0), (0.13, 0.08, 0.08), "zloto_ciemne", "metal", faza=0.0)
        a.blok("Szyjka", (0, -0.15, 0), (0.08, 0.24, 0.06), "zloto", "metal", faza=0.0)
        a.walec("Kolko", (0, -0.38, 0), (0.2, 0.05, 0.2), "zloto", "metal", rot=(90, 0, 0), segm=8)
        for k in (0, 45, 90, 135):
            a.blok("Kolec", (0, -0.38, 0), (0.045, 0.42, 0.04), "zloto", "metal", rot=(0, 0, k), faza=0.0)
        a.blok("Klejnot", (0, -0.38, 0.04), (0.09, 0.09, 0.03), "niebieski_jasny", "swiecacy", rot=(0, 0, 45),
               faza=0.0)
    return a


# --------------------------------------------------------------------------- zestaw
def akcesoria():
    return [helm(), napiersnik(), naramiennik("l"), naramiennik("p"), pola(), rekawica("l"), rekawica("p"),
            but("l"), but("p"), pas(), miecz(), tarcza(), amulet(), sygnet(), ostroga()]


SLABOSCI = [
    "Każdy przedmiot to sztywne akcesorium dopasowane do klockowego R15 biblioteki (5,25 studa); na innym ciele "
    "(Rthro) nie będzie przylegać.",
    "Hełm ma tylko wariant z otwartą twarzą; przyłbica (zamknięty wariant) to osobna propozycja, niezrobiona.",
    "Napierśnik to 4 akcesoria (napierśnik, 2 naramienniki, poła); naramienniki idą za ramieniem, więc przy "
    "uniesionej ręce odsłaniają bark.",
    "Sygnet nie jest zakładany na przymiarkę (w rękawicy byłby niewidoczny) — przedmiot do ikony i eksportu.",
]


def zbuduj():
    from swiat.postacie.biblioteka.postac import przymiarka
    akc = akcesoria()
    p = przymiarka("zestaw_rycerz_przymiarka", akc, "Zestaw Rycerza — przymiarka na manekinie R15")
    return [p] + akc
