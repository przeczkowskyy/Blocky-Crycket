# -*- coding: utf-8 -*-
"""ZESTAW EKWIPUNKU „MAG” (poziom średni, alternatywa) dla awatara gracza R15 — fiolet i złoto, turkusowe kryształy.

Każdy przedmiot to osobne SZTYWNE akcesorium (jedna siatka, (0, 0, 0) = punkt zaczepienia), dopasowane do
klockowego manekina R15 z biblioteki (5,25 studa: głowa 1,25³, tułów 2 × 1,6 × 1, ręce i nogi 1 × … × 1).
Przedmioty, które muszą iść za dwiema kośćmi (rękawice, buty, rękawy szaty), są parami osobnych akcesoriów
z tym samym slotem. Opis przedmiotów (id, nazwa, slot, kategoria plecaka, zaczep): lista PRZEDMIOTY niżej.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zestaw_mag.py --wyj <folder> --eksport

Sposób modelowania: większość brył jest podana we WSPÓŁRZĘDNYCH MODELU manekina (stopy na y = 0, przód +Z,
lewa strona +X), a układ `uklad(pos=-zaczep)` przenosi je do układu zaczepu. Zaczepy Grip mają obrót (90, 0, 0),
więc przedmioty na dłoni są dodatkowo w `uklad(obrot=(-90, 0, 0))` (wtedy oś Y modelu znów jest pionem), a ich
ikona dostaje ikona_obrot=(90, 0, 0), żeby stała prosto. Kostur jest wyjątkiem: modelowany jak broń z wzoru
(rękojeść w (0, 0, 0), drzewce w +Y).

Status: propozycja (nie kanon). Bez napisów i liter; runa to własny prosty znak geometryczny. Kolory: fiolet i złoto,
turkus tylko na kryształach i klejnotach.
"""
import math

from swiat.postacie.biblioteka.postac import Akcesorium

# --------------------------------------------------------------------------- miary manekina R15 (biblioteka)
GLOWA = 1.25                          # sześcian głowy; HatAttachment = środek górnej ściany (y = 5,25)
ZACZEPY = {                           # położenie zaczepów w układzie modelu manekina (stopy na y = 0)
    "HatAttachment": (0.0, 5.25, 0.0),
    "NeckAttachment": (0.0, 4.0, 0.0),
    "BodyFrontAttachment": (0.0, 3.2, 0.5),
    "WaistCenterAttachment": (0.0, 2.2, 0.0),
    "LeftShoulderAttachment": (1.5, 4.0, 0.0),
    "RightShoulderAttachment": (-1.5, 4.0, 0.0),
    "LeftGripAttachment": (1.5, 2.15, 0.0),
    "RightGripAttachment": (-1.5, 2.15, 0.0),
    "LeftFootAttachment": (0.5, 0.0, 0.0),
    "RightFootAttachment": (-0.5, 0.0, 0.0),
}

FILMY = ["chod"]                     # przebuduj.py: film i arkusz klatek tylko dla chodu przymiarki

PALETA = {
    "kremowy": "F3E4BE",              # kartki księgi
    "szklo": "BFF6F3",                # szkło fiolek i klepsydry
    "limonka": "A6EE3A",              # trzecia mikstura
    "rozowy": "FF5C8A",               # pierwsza mikstura
}

# Opis zestawu dla gry / plecaka. slot: Helmet, Chest, Gloves, Boots, Belt, Weapon, OffHand, Amulet, Ring, Trinket;
# kategoria plecaka: Weapons, Armor, Amulets, Others; zaczep = punkt zaczepienia R15 (nazwa jak w Studio).
PRZEDMIOTY = [
    {"id": "mag_kapelusz", "nazwa": "Kapelusz maga", "slot": "Helmet", "kategoria": "Armor",
     "zaczep": "HatAttachment"},
    {"id": "mag_szata", "nazwa": "Szata maga", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "BodyFrontAttachment"},
    {"id": "mag_szata_dol", "nazwa": "Szata maga — dół", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "WaistCenterAttachment", "czesc_od": "mag_szata"},
    {"id": "mag_rekaw_l", "nazwa": "Szata maga — lewy rękaw", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "LeftShoulderAttachment", "czesc_od": "mag_szata"},
    {"id": "mag_rekaw_p", "nazwa": "Szata maga — prawy rękaw", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "RightShoulderAttachment", "czesc_od": "mag_szata"},
    {"id": "mag_rekawica_l", "nazwa": "Rękawica runiczna (lewa)", "slot": "Gloves", "kategoria": "Armor",
     "zaczep": "LeftGripAttachment"},
    {"id": "mag_rekawica_p", "nazwa": "Rękawica runiczna (prawa)", "slot": "Gloves", "kategoria": "Armor",
     "zaczep": "RightGripAttachment", "czesc_od": "mag_rekawica_l"},
    {"id": "mag_cizma_l", "nazwa": "Zakręcona ciżma (lewa)", "slot": "Boots", "kategoria": "Armor",
     "zaczep": "LeftFootAttachment"},
    {"id": "mag_cizma_p", "nazwa": "Zakręcona ciżma (prawa)", "slot": "Boots", "kategoria": "Armor",
     "zaczep": "RightFootAttachment", "czesc_od": "mag_cizma_l"},
    {"id": "mag_pas", "nazwa": "Pas z fiolkami", "slot": "Belt", "kategoria": "Armor",
     "zaczep": "WaistCenterAttachment"},
    {"id": "mag_kostur", "nazwa": "Kostur turkusowego kryształu", "slot": "Weapon", "kategoria": "Weapons",
     "zaczep": "RightGripAttachment"},
    {"id": "mag_ksiega", "nazwa": "Księga zaklęć", "slot": "OffHand", "kategoria": "Weapons",
     "zaczep": "LeftGripAttachment"},
    {"id": "mag_amulet", "nazwa": "Amulet fioletowego kryształu", "slot": "Amulet", "kategoria": "Amulets",
     "zaczep": "NeckAttachment"},
    {"id": "mag_pierscien", "nazwa": "Pierścień z fioletowym kamieniem", "slot": "Ring", "kategoria": "Amulets",
     "zaczep": "RightGripAttachment"},
    {"id": "mag_klepsydra", "nazwa": "Klepsydra", "slot": "Trinket", "kategoria": "Others",
     "zaczep": "WaistCenterAttachment"},
]


def _akc(id, typ=None, ikona_obrot=(0, 0, 0), faza=0.04, **kw):
    opis = next(p for p in PRZEDMIOTY if p["id"] == id)
    return Akcesorium(id, opis["nazwa"], zaczep=opis["zaczep"], typ=typ, faza=faza, paleta=PALETA,
                      ikona_obrot=ikona_obrot, **kw)


def _w_modelu(a, obrot_grip=False):
    """Układ: współrzędne modelu manekina -> układ zaczepu akcesorium."""
    zx, zy, zz = ZACZEPY[a.zaczep]
    if obrot_grip:
        zewn = a.uklad(obrot=(-90, 0, 0))
        zewn.__enter__()
        wewn = a.uklad(pos=(-zx, -zy, -zz))
        wewn.__enter__()
        return (zewn, wewn)
    wewn = a.uklad(pos=(-zx, -zy, -zz))
    wewn.__enter__()
    return (wewn,)


def _wyjdz(uklady):
    for u in reversed(uklady):
        u.__exit__(None, None, None)


def _gwiazda(a, nazwa, pos, rozmiar, obrot=(0, 0, 0), kolor="zloto", srodek="turkus"):
    """Gwiazdka-iskra o czterech ramionach + klejnot w środku; płaszczyzna XY, przód +Z.
    Ramiona to ostrosłupy ze ściętym czubkiem (bez zdegenerowanego szpica)."""
    ramie = rozmiar / 2
    with a.uklad(pos=pos, obrot=obrot):
        for i, rz in enumerate((0, 90, 180, 270)):
            with a.uklad(obrot=(0, 0, rz)):
                a.ostroslup("%s ramie %d" % (nazwa, i), (0, ramie / 2 + 0.04, 0), (rozmiar * 0.3, ramie, 0.07),
                            kolor, "metal", gora=(0.03, 0.05), faza=0.0)
        a.blok(nazwa + " srodek", (0, 0, 0), (rozmiar * 0.32, rozmiar * 0.32, 0.08), kolor, "metal", rot=(0, 0, 45),
               faza=0.0)
        a.blok(nazwa + " klejnot", (0, 0, 0.045), (rozmiar * 0.17, rozmiar * 0.17, 0.05), srodek, "swiecacy",
               rot=(0, 0, 45), faza=0.0)


# --------------------------------------------------------------------------- Helmet
def kapelusz():
    a = _akc("mag_kapelusz", typ="Hat")
    # układ zaczepu: (0, 0, 0) = środek górnej ściany głowy; głowa: y −1,25…0, x/z ±0,625
    a.walec("Rondo", (0, -0.36, 0), (2.5, 0.12, 2.5), "fiolet_ciemny", "matowy", segm=8)
    a.walec("Rondo lamowka", (0, -0.43, 0), (2.56, 0.05, 2.56), "zloto", "metal", segm=8, faza=0.0)
    a.blok("Opaska", (0, -0.13, 0), (1.52, 0.36, 1.52), "fiolet_ciemny", "matowy")
    a.blok("Opaska zloto", (0, 0.07, 0), (1.56, 0.08, 1.56), "zloto", "metal", faza=0.0)
    a.ostroslup("Glowica 1", (0, 0.45, 0), (1.46, 0.72, 1.46), "fiolet", "matowy", gora=(0.96, 0.96),
                przes_gory=(0.0, -0.05))
    a.ostroslup("Glowica 2", (-0.02, 1.06, -0.06), (0.98, 0.52, 0.98), "fiolet", "matowy", gora=(0.52, 0.52),
                przes_gory=(-0.08, -0.14))
    a.ostroslup("Szpic", (-0.1, 1.55, -0.2), (0.54, 0.5, 0.54), "fiolet", "matowy", gora=(0, 0),
                przes_gory=(-0.22, -0.34))
    a.blok("Pasek zloto", (-0.02, 0.84, -0.06), (1.02, 0.08, 1.02), "zloto", "metal", faza=0.0)
    # gwiazdka na skośnej przedniej ścianie główki (skos przodu 22,6°: zwężenie 0,25 + przesunięcie 0,05 na 0,72)
    _gwiazda(a, "Gwiazda", (0, 0.4, 0.645), 0.62, obrot=(-22.6, 0, 0))
    return a


# --------------------------------------------------------------------------- Chest (góra, dół, dwa rękawy)
def szata():
    a = _akc("mag_szata", typ="Front")
    u = _w_modelu(a)
    # tułów manekina: x ±1, y 2,4…4,0, z ±0,5; ręce tuż obok (x 1…2), więc boki szaty są niemal na równi z tułowiem
    a.blok("Tulow", (0, 3.2, 0), (2.04, 1.66, 1.16), "fiolet", "matowy")
    a.blok("Pas srodek", (0, 2.95, 0.6), (0.34, 1.2, 0.06), "fiolet_ciemny", "matowy", faza=0.015)
    for zn in (1, -1):
        # wyłogi w kształcie V: ciemny fiolet ze złotą lamówką 0,08 (turkus tylko na kryształach)
        a.blok("Wylog", (zn * 0.3, 3.5, 0.61), (0.17, 1.12, 0.06), "fiolet_ciemny", "matowy", rot=(0, 0, -zn * 33),
               faza=0.015)
        a.blok("Wylog zloto", (zn * 0.42, 3.52, 0.6), (0.08, 1.18, 0.06), "zloto", "metal", rot=(0, 0, -zn * 33),
               faza=0.0)
        # boczne skrzydła kołnierza (głowa x ±0,625)
        a.blok("Kolnierz bok", (zn * 0.78, 4.22, -0.28), (0.12, 0.5, 0.74), "fiolet_ciemny", "matowy",
               rot=(0, 0, -zn * 14), faza=0.02)
    for i, y in enumerate((2.62, 2.92)):          # złote guziki na środkowym pasie
        a.blok("Guzik %d" % i, (0, y, 0.645), (0.13, 0.13, 0.05), "zloto", "metal", rot=(0, 0, 45), faza=0.01)
    # wysoki kołnierz z tyłu głowy (głowa z ±0,625)
    a.blok("Kolnierz tyl", (0, 4.24, -0.74), (1.72, 0.56, 0.14), "fiolet_ciemny", "matowy", rot=(15, 0, 0))
    a.blok("Kolnierz lamowka", (0, 4.52, -0.82), (1.76, 0.06, 0.18), "zloto", "metal", rot=(15, 0, 0), faza=0.0)
    # tył: złota lamówka pionowa i gwiazdka (czytelne z tyłu)
    a.blok("Plecy pas", (0, 3.1, -0.6), (0.08, 1.4, 0.06), "zloto", "metal", faza=0.0)
    _gwiazda(a, "Gwiazda plecy", (0, 3.45, -0.64), 0.6, obrot=(0, 180, 0))
    _wyjdz(u)
    return a


def szata_dol():
    """Dół szaty na LowerTorso (WaistCenterAttachment) — idzie za biodrami, nogi wychodzą spod rozszerzonego dołu."""
    a = _akc("mag_szata_dol", typ="Waist")
    u = _w_modelu(a)
    # krótka spódnica: od pasa (y 2,42) do y 1,75 (0,45 pod WaistCenter), rozszerzona ku dołowi o 0,2 —
    # uda w chodzie nie przechodzą przez jej przód; od spodu ciemne wnętrze zamiast pustej skorupy
    a.ostroslup("Spodnica", (0, 2.085, 0), (2.44, 0.67, 1.56), "fiolet", "matowy", gora=(2.04, 1.16))
    a.blok("Wnetrze", (0, 1.765, 0), (2.36, 0.02, 1.48), "fiolet_ciemny", "matowy", faza=0.0)
    a.ostroslup("Lamowka zloto", (0, 1.8, 0), (2.48, 0.08, 1.6), "zloto", "metal", gora=(2.46, 1.58), faza=0.0)
    # pas z przodu i z tyłu na skosie spódnicy (skos ok. 16,6°)
    a.blok("Pas przod", (0, 2.1, 0.68), (0.34, 0.62, 0.06), "fiolet_ciemny", "matowy", rot=(-16.6, 0, 0),
           faza=0.015)
    a.blok("Pas tyl", (0, 2.1, -0.68), (0.08, 0.62, 0.06), "zloto", "metal", rot=(16.6, 0, 0), faza=0.0)
    for zn in (1, -1):                              # gwiazdki na bokach przodu
        _gwiazda(a, "Gwiazdka", (zn * 0.72, 2.0, 0.72), 0.26, obrot=(-16.6, 0, 0))
    _wyjdz(u)
    return a


def rekaw(strona):
    zn = 1 if strona == "l" else -1
    a = _akc("mag_rekaw_" + strona, typ="Shoulder")
    u = _w_modelu(a)
    x = zn * 1.5                                   # środek ręki; ramię y 3,05…4,0, przedramię 2,3…3,05
    # wszystko od strony tułowia najwyżej 0,48 od środka ręki (x ≥ 1,02) — rękaw nie wchodzi w tułów
    a.blok("Naramiennik", (x + zn * 0.07, 3.86, 0), (1.06, 0.34, 1.1), "fiolet", "matowy")
    a.blok("Naramiennik zloto", (x + zn * 0.07, 4.05, 0), (1.02, 0.08, 1.04), "zloto", "metal", faza=0.0)
    # dzwon zwisający z ramienia: góra 1,06 (przy ręce), dół 1,5, wysokość 1,3, rozszerza się NA ZEWNĄTRZ
    # (od tułowia prosto w dół), spod niego wychodzi dłoń
    xd = x + zn * 0.27                             # środek dołu dzwonu: wewnętrzna krawędź x = 1,02
    a.ostroslup("Dzwon", (xd, 3.2, 0), (1.5, 1.3, 1.4), "fiolet", "matowy", gora=(1.06, 1.06),
                przes_gory=(-zn * 0.22, 0))
    a.ostroslup("Mankiet", (xd, 2.6, 0), (1.5, 0.12, 1.4), "fiolet_ciemny", "matowy", gora=(1.48, 1.38), faza=0.02)
    a.blok("Mankiet zloto", (xd, 2.69, 0), (1.48, 0.08, 1.38), "zloto", "metal", faza=0.0)
    a.blok("Otwor", (xd, 2.535, 0), (1.3, 0.02, 1.2), "2A1A40", "matowy", faza=0.0)
    # gwiazdka na zewnętrznej ścianie naramiennika
    _gwiazda(a, "Gwiazdka", (x + zn * 0.61, 3.84, 0), 0.3, obrot=(0, zn * 90, 0))
    _wyjdz(u)
    return a


def _runa(a, pos, obrot, s=1.0):
    """Własny znak: romb z kropką (płaszczyzna XY, przód +Z)."""
    with a.uklad(pos=pos, obrot=obrot, skala=s):
        for i, (dx, dy, r) in enumerate(((0.07, 0.07, 45), (-0.07, 0.07, -45), (0.07, -0.07, -45),
                                         (-0.07, -0.07, 45))):
            a.blok("Runa %d" % i, (dx, dy, 0), (0.05, 0.22, 0.05), "zloto", "metal", rot=(0, 0, r), faza=0.0)
        a.blok("Runa kropka", (0, 0, 0), (0.07, 0.07, 0.05), "turkus", "swiecacy", rot=(0, 0, 45), faza=0.0)


# --------------------------------------------------------------------------- Gloves
def rekawica(strona):
    zn = 1 if strona == "l" else -1
    # ikona od grzbietu dłoni (runa), nie od otworu mankietu
    a = _akc("mag_rekawica_" + strona, typ="Inne", ikona_obrot=(55, 0, 0) if zn > 0 else (125, 180, 0))
    u = _w_modelu(a, obrot_grip=True)
    x = zn * 1.5                                   # dłoń: x 1…2, y 2,0…2,3, z ±0,5
    c = x + zn * 0.11                              # od strony tułowia najwyżej 0,48 od środka dłoni, na zewnątrz 0,7
    a.blok("Dlon", (c, 2.13, 0), (1.18, 0.42, 1.1), "fiolet_ciemny", "matowy")
    a.blok("Kciuk", (x - zn * 0.3, 2.12, 0.6), (0.3, 0.3, 0.16), "fiolet_ciemny", "matowy", faza=0.03)
    a.ostroslup("Mankiet", (c, 2.49, 0), (1.18, 0.3, 1.12), "fiolet", "matowy", gora=(1.26, 1.3),
                przes_gory=(zn * 0.04, 0), faza=0.02)
    a.blok("Mankiet zloto", (c + zn * 0.04, 2.665, 0), (1.26, 0.08, 1.32), "zloto", "metal", faza=0.0)
    a.blok("Otwor", (c + zn * 0.04, 2.71, 0), (1.06, 0.02, 1.1), "2A1A40", "matowy", faza=0.0)
    # runa na zewnętrznej ścianie (wierzch dłoni) i mniejsza na przodzie
    _runa(a, (c + zn * 0.605, 2.14, 0), (0, zn * 90, 0), 0.95)
    _runa(a, (c, 2.14, 0.575), (0, 0, 0), 0.75)
    _wyjdz(u)
    return a


# --------------------------------------------------------------------------- Boots
def cizma(strona):
    zn = 1 if strona == "l" else -1
    a = _akc("mag_cizma_" + strona, typ="Inne", ikona_obrot=(0, -60, 0))   # ikona: profil z zawijasem
    u = _w_modelu(a)
    x = zn * 0.5                                   # stopa: x 0…1, y 0…0,35, z ±0,5; podudzie y 0,35…1,15
    # but asymetryczny: od strony drugiej nogi najwyżej 0,48 od środka stopy, na zewnątrz do 0,64–0,68
    c = x + zn * 0.08
    a.blok("Podeszwa", (c, 0.06, 0.03), (1.12, 0.12, 1.18), "brazowy_ciemny", "matowy")
    a.blok("Stopa", (c, 0.28, 0.02), (1.1, 0.34, 1.12), "fiolet", "matowy")
    a.ostroslup("Cholewa", (c, 0.69, 0), (1.1, 0.56, 1.1), "fiolet", "matowy", gora=(1.12, 1.22))
    a.blok("Wywiniecie", (c + zn * 0.02, 1.04, 0), (1.16, 0.18, 1.28), "fiolet_ciemny", "matowy")
    a.blok("Wywiniecie zloto", (c + zn * 0.02, 0.94, 0), (1.14, 0.08, 1.25), "zloto", "metal", faza=0.0)
    a.blok("Otwor", (c, 1.14, 0), (1.0, 0.02, 1.06), "2A1A40", "matowy", faza=0.0)
    # zakręcony nosek: klin do przodu, potem szpic zawinięty w górę i do tyłu, na końcu złota kulka
    a.ostroslup("Nosek", (x, 0.21, 0.88), (0.9, 0.6, 0.4), "fiolet", "matowy", rot=(90, 0, 0),
                gora=(0.36, 0.2), przes_gory=(0, -0.1))
    a.ostroslup("Zawijas", (x, 0.6, 1.14), (0.36, 0.56, 0.26), "fiolet", "matowy", gora=(0.12, 0.1),
                przes_gory=(0, -0.2), faza=0.02)
    a.blok("Zawijas pasek", (x, 0.45, 1.16), (0.34, 0.07, 0.25), "turkus", "zwykly", faza=0.0)
    a.kula("Kulka", (x, 0.93, 0.92), 0.18, "zloto", "metal", segm=8)
    a.blok("Klamra", (x, 0.5, 0.57), (0.3, 0.2, 0.06), "zloto", "metal", faza=0.015)
    a.blok("Klamra klejnot", (x, 0.5, 0.605), (0.1, 0.1, 0.04), "turkus", "swiecacy", rot=(0, 0, 45), faza=0.0)
    _wyjdz(u)
    return a


# --------------------------------------------------------------------------- Belt
def pas():
    a = _akc("mag_pas", typ="Waist", ikona_obrot=(10, 0, 0))        # ikona: z przodu, z klamrą i fiolkami
    u = _w_modelu(a)
    # pętla z czterech pasków, szerokość 2,02 (dłonie wiszą od x = ±1,0 — szerszy pas wchodził w dłonie)
    a.blok("Pas przod", (0, 2.2, 0.62), (2.02, 0.26, 0.12), "brazowy_ciemny", "matowy", faza=0.03)
    a.blok("Pas tyl", (0, 2.2, -0.62), (2.02, 0.26, 0.12), "brazowy_ciemny", "matowy", faza=0.03)
    for zn in (1, -1):
        a.blok("Pas bok", (zn * 0.95, 2.2, 0), (0.12, 0.26, 1.12), "brazowy_ciemny", "matowy", faza=0.0)
    a.blok("Klamra", (0, 2.2, 0.7), (0.46, 0.36, 0.08), "zloto", "metal", faza=0.02)
    a.blok("Klamra klejnot", (0, 2.2, 0.75), (0.17, 0.17, 0.05), "turkus", "swiecacy", rot=(0, 0, 45), faza=0.01)
    # dwie fiolki w uchwytach na prawym przodzie (x < 0, w zakresie ±0,9), w kolorach zestawu
    for i, (xf, kol) in enumerate(((-0.4, "fiolet_jasny"), (-0.7, "zloto"))):
        a.blok("Uchwyt %d" % i, (xf, 2.2, 0.71), (0.18, 0.3, 0.06), "brazowy", "matowy", faza=0.015)
        a.kula("Fiolka %d" % i, (xf, 1.92, 0.87), (0.28, 0.3, 0.28), kol, "swiecacy", segm=8)
        a.walec("Szyjka %d" % i, (xf, 2.15, 0.87), (0.11, 0.24, 0.11), "szklo", "polysk", segm=8, faza=0.0)
        a.walec("Korek %d" % i, (xf, 2.31, 0.87), (0.15, 0.1, 0.15), "brazowy_jasny", "matowy", segm=8, faza=0.0)
    # sakiewka na lewym boku przodu
    a.blok("Sakiewka", (0.62, 2.04, 0.76), (0.42, 0.4, 0.2), "brazowy", "matowy", faza=0.04)
    a.blok("Sakiewka klapa", (0.62, 2.2, 0.79), (0.46, 0.14, 0.2), "brazowy_ciemny", "matowy", faza=0.03)
    a.blok("Sakiewka guzik", (0.62, 2.12, 0.885), (0.1, 0.1, 0.04), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
    _wyjdz(u)
    return a


# --------------------------------------------------------------------------- Weapon
def kostur():
    a = _akc("mag_kostur", typ="Bron", ikona_obrot=(0, 0, -35), chwyt="drzewce")   # w chodzie stoi pionowo
    # układ broni: rękojeść w (0, 0, 0), drzewce w +Y, przód +Z
    a.walec("Drzewce", (0, 0.55, 0), (0.24, 4.2, 0.24), "brazowy_ciemny", "matowy", segm=8)
    a.walec("Okucie", (0, -1.58, 0), (0.3, 0.14, 0.3), "zloto", "metal", segm=8)
    a.stozek("Szpikulec", (0, -1.75, 0), (0.24, 0.2, 0.24), "zloto", "metal", rot=(180, 0, 0), segm=8)
    for i, y in enumerate((-0.62, 0.62, 1.7)):
        a.walec("Pierscien %d" % i, (0, y, 0), (0.32, 0.1, 0.32), "zloto", "metal", segm=8, faza=0.0)
    a.walec("Owijka", (0, 1.25, 0), (0.29, 0.5, 0.29), "fiolet", "matowy", segm=8, faza=0.0)
    # głowica: złoty kołnierz, cztery pazury i turkusowy kryształ
    a.walec("Kolnierz", (0, 2.72, 0), (0.46, 0.2, 0.46), "zloto", "metal", segm=8)
    for i, ry in enumerate((45, 135, 225, 315)):
        with a.uklad(pos=(0, 2.8, 0), obrot=(0, ry, 0)):
            a.blok("Pazur %d" % i, (0, 0.28, 0.24), (0.1, 0.5, 0.1), "zloto", "metal", rot=(22, 0, 0), faza=0.02)
    a.ostroslup("Krysztal dol", (0, 3.06, 0), (0.56, 0.36, 0.56), "turkus", "swiecacy", rot=(180, 45, 0),
                gora=(0, 0))
    a.ostroslup("Krysztal gora", (0, 3.6, 0), (0.56, 0.72, 0.56), "turkus", "swiecacy", rot=(0, 45, 0),
                gora=(0, 0))
    # fioletowa wstążka pod głowicą
    a.blok("Wstazka", (0.17, 2.32, 0.0), (0.08, 0.6, 0.18), "fiolet", "matowy", rot=(0, 0, -12), faza=0.02)
    a.klin("Wstazka koniec", (0.24, 1.94, 0.0), (0.08, 0.22, 0.18), "fiolet", "matowy", rot=(0, 0, -12), faza=0.0)
    return a


# --------------------------------------------------------------------------- OffHand
def ksiega():
    a = _akc("mag_ksiega", typ="Inne", ikona_obrot=(90, 0, 0))
    u = _w_modelu(a, obrot_grip=True)
    # przed lewą dłonią (dłoń x 1…2, z do 0,55), okładką do przodu, grzbiet od strony ciała
    x, y, z = 1.58, 2.02, 0.79
    a.blok("Okladka tyl", (x, y, z - 0.15), (0.9, 1.1, 0.06), "fiolet_ciemny", "matowy", faza=0.02)
    a.blok("Okladka przod", (x, y, z + 0.15), (0.9, 1.1, 0.06), "fiolet_ciemny", "matowy", faza=0.02)
    a.blok("Kartki", (x + 0.03, y, z), (0.82, 1.02, 0.26), "kremowy", "matowy", faza=0.0)
    a.blok("Grzbiet", (x - 0.44, y, z), (0.1, 1.12, 0.38), "fiolet", "matowy", faza=0.03)
    for i, dy in enumerate((-0.32, 0.32)):
        a.blok("Grzbiet zloto %d" % i, (x - 0.47, y + dy, z), (0.06, 0.07, 0.4), "zloto", "metal", faza=0.0)
    for i, (dx, dy) in enumerate(((0.36, 0.46), (0.36, -0.46), (-0.36, 0.46), (-0.36, -0.46))):
        a.blok("Naroznik %d" % i, (x + dx, y + dy, z + 0.18), (0.2, 0.2, 0.04), "zloto", "metal", faza=0.0)
    a.blok("Ramka", (x, y, z + 0.18), (0.42, 0.42, 0.04), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
    a.blok("Klejnot", (x, y, z + 0.215), (0.2, 0.2, 0.05), "turkus", "swiecacy", rot=(0, 0, 45), faza=0.01)
    a.blok("Zapiecie", (x + 0.43, y, z + 0.06), (0.1, 0.18, 0.34), "zloto", "metal", faza=0.015)
    _wyjdz(u)
    return a


# --------------------------------------------------------------------------- Amulet, Ring, Trinket
def amulet():
    a = _akc("mag_amulet", typ="Neck", ikona_obrot=(10, 0, 0))
    u = _w_modelu(a)
    # sznur od szyi (głowa x ±0,625): boki przy szyi, potem w V do zawieszki; zawieszka przylega do piersi
    # (tył z = 0,52 — bez szaty nie wisi w powietrzu; z szatą, przód z = 0,58, wystaje jej przód)
    for zn in (1, -1):
        a.blok("Sznur bok", (zn * 0.68, 3.98, 0.1), (0.05, 0.05, 0.8), "fiolet_ciemny", "matowy", faza=0.0)
        a.blok("Sznur", (zn * 0.36, 3.79, 0.52), (0.05, 0.62, 0.05), "fiolet_ciemny", "matowy",
               rot=(0, 0, -zn * 52), faza=0.0)
    a.blok("Uszko", (0, 3.6, 0.55), (0.1, 0.12, 0.06), "zloto", "metal", faza=0.0)
    # fioletowy kryształ w złotej oprawie (jak kryształ kostura Kota-Maga)
    a.blok("Oprawa", (0, 3.3, 0.56), (0.42, 0.42, 0.08), "zloto", "metal", rot=(0, 0, 45), faza=0.03)
    for zn in (1, -1):
        a.blok("Pazurek", (zn * 0.2, 3.3, 0.6), (0.08, 0.14, 0.06), "zloto", "metal", faza=0.0)
    a.ostroslup("Krysztal", (0, 3.3, 0.66), (0.3, 0.12, 0.3), "fiolet", "polysk", rot=(90, 45, 0),
                gora=(0.1, 0.1), faza=0.0)
    a.blok("Krysztal blysk", (-0.05, 3.35, 0.725), (0.06, 0.08, 0.02), "fiolet_jasny", "swiecacy", faza=0.0)
    _wyjdz(u)
    return a


def pierscien():
    a = _akc("mag_pierscien", typ="Inne", ikona_obrot=(90, 0, 0), faza=0.0)
    u = _w_modelu(a, obrot_grip=True)
    # na przedniej ścianie prawej rękawicy (z = 0,55): obręcz w płaszczyźnie XY, kamień na górze
    cx, cy, cz = -1.5, 2.08, 0.62
    r = 0.17
    for i in range(8):
        k = math.radians(i * 45 + 22.5)
        a.blok("Obrecz %d" % i, (cx + r * math.cos(k), cy + r * math.sin(k), cz), (0.07, 0.15, 0.08), "zloto", "metal",
               rot=(0, 0, i * 45 + 22.5))
    a.blok("Oprawa", (cx, cy + 0.24, cz), (0.22, 0.08, 0.14), "zloto", "metal")
    a.ostroslup("Kamien dol", (cx, cy + 0.33, cz), (0.26, 0.1, 0.26), "fiolet_ciemny", "polysk", rot=(180, 45, 0),
                gora=(0.12, 0.12))
    a.ostroslup("Kamien gora", (cx, cy + 0.43, cz), (0.26, 0.1, 0.26), "fiolet", "polysk", rot=(0, 45, 0),
                gora=(0.12, 0.12))
    a.blok("Kamien blysk", (cx - 0.04, cy + 0.485, cz + 0.03), (0.05, 0.02, 0.05), "fiolet_jasny", "swiecacy",
           faza=0.0)
    _wyjdz(u)
    return a


def klepsydra():
    a = _akc("mag_klepsydra", typ="Waist")
    u = _w_modelu(a)
    # wisi na lewym przodzie bioder, przy samym ciele (tył z ≈ 0,56; bez pasa i szaty nie wisi w powietrzu)
    a.blok("Rzemyk", (0.3, 2.0, 0.6), (0.06, 0.3, 0.06), "brazowy", "matowy", faza=0.0)
    with a.uklad(pos=(0.3, 1.66, 0.7), skala=0.82):
        a.walec("Gora", (0, 0.24, 0), (0.34, 0.06, 0.34), "zloto", "metal", segm=8, faza=0.0)
        a.walec("Dol", (0, -0.24, 0), (0.34, 0.06, 0.34), "zloto", "metal", segm=8, faza=0.0)
        for i, ry in enumerate((0, 120, 240)):
            with a.uklad(obrot=(0, ry, 0)):
                a.blok("Slupek %d" % i, (0, 0, 0.14), (0.04, 0.44, 0.04), "zloto_ciemne", "metal", faza=0.0)
        a.stozek("Banka gora", (0, 0.11, 0), (0.24, 0.2, 0.24), "szklo", "polysk", rot=(180, 0, 0), gora=0.18,
                 segm=8)
        a.stozek("Banka dol", (0, -0.11, 0), (0.24, 0.2, 0.24), "szklo", "polysk", gora=0.18, segm=8)
        a.stozek("Piasek", (0, -0.155, 0), (0.2, 0.11, 0.2), "zloto", "swiecacy", gora=0.25, segm=8)
        a.stozek("Piasek gora", (0, 0.045, 0), (0.1, 0.08, 0.1), "zloto", "swiecacy", rot=(180, 0, 0), gora=0.3,
                 segm=8)
    _wyjdz(u)
    return a


def szata_cala(czesci):
    """Model TYLKO do ikony przedmiotu „Szata maga”: góra, dół i oba rękawy złożone w jedną bryłę (w 64 px same
    rękawy i dół czytały się jak pudełka). Nie zakładany na przymiarkę; w grze szata to cztery akcesoria."""
    a = Akcesorium("mag_szata_cala", "Szata maga (cała, do ikony)", zaczep="BodyFrontAttachment", typ="Front",
                   paleta=PALETA, ikona_obrot=(0, 25, 0), przymierz=False)
    I = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    bx, by, bz = ZACZEPY["BodyFrontAttachment"]
    for c in czesci:
        zx, zy, zz = ZACZEPY[c.zaczep]
        for cz in c.czesci:
            a.czesci.append(Akcesorium._czesc_w(cz, I, (zx - bx, zy - by, zz - bz)))
    return a


SLABOSCI = [
    "Każdy przedmiot to sztywne akcesorium dopasowane do klockowego R15 biblioteki (5,25 studa); na innym ciele "
    "(Rthro) nie będzie przylegać.",
    "Dół szaty jest krótki (do 0,45 pod pasem), żeby uda nie przechodziły przez niego w chodzie; dłuższej, "
    "falującej szaty sztywne akcesorium nie da.",
    "Rękawy-dzwony wiszą z ramienia: przy uniesionej ręce (atak) dzwon obraca się z ramieniem.",
    "Klepsydra wisi przy samym ciele, więc z założonym dołem szaty częściowo chowa się w spódnicy.",
    "mag_szata_cala to model tylko do ikony (w przedmioty.json nie jest częścią do założenia).",
]


def zbuduj():
    gora, dol, rl, rp = szata(), szata_dol(), rekaw("l"), rekaw("p")
    return [kapelusz(), gora, dol, rl, rp, rekawica("l"), rekawica("p"), cizma("l"), cizma("p"),
            pas(), kostur(), ksiega(), amulet(), pierscien(), klepsydra(), szata_cala([gora, dol, rl, rp])]
