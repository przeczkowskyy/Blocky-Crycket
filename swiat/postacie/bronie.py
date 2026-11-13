# -*- coding: utf-8 -*-
"""ZBROJOWNIA — osiem broni do prawej dłoni klockowego awatara R15, w rosnącej „randze”.

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/bronie.py --wyj <folder>
    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/bronie.py --wyj <folder> --eksport

Każda broń to osobne SZTYWNE akcesorium (jedna siatka, ≤ ok. 800 trójkątów) na RightGripAttachment, modelowane
jak w wzor_ekwipunku.py: (0, 0, 0) = środek dłoni (punkt zaczepienia), rękojeść wzdłuż osi Y, głowica/ostrze w +Y,
płaz (lico) do przodu (+Z), oś X = bok. W ramce Grip (obrót 90, 0, 0) dłoń manekina zajmuje x ±0,5, y ±0,5,
z ±0,15 — dlatego jelce, okucia i głowice zaczynają się dopiero za |y| ≥ 0,55, a wszystko poniżej dłoni (−Y)
jest cieńsze niż 1 stud w osi X (nie wchodzi w nogę w pozie „trzymanie”). Ostrza topora, młota i chorągiewka
wystają na −X, czyli NA ZEWNĄTRZ od prawego boku postaci.

zbuduj() zwraca osiem przymiarek (szary manekin R15 z jedną bronią w pozie „trzymanie”) i osiem akcesoriów
(każde dostaje ikonę 512 px i własny eksport). Opis dla gry / plecaka: lista PRZEDMIOTY.

Własne projekty (bez wzorowania się na przedmiotach z innych gier), bez napisów i liter.
Status: propozycja (nie kanon) — do oceny przez Game Directora.
"""
import math

from swiat.postacie.biblioteka.postac import Akcesorium, manekin_r15, klip_trzymanie_r15, klip_spoczynek_r15

FILMY = []                 # przebuduj.py: bez filmów (przymiarki są tylko do plansz)
EKSPORT_MODELI = False     # przebuduj.py: z przymiarek tylko plansze JPG (bez FBX/GLB/.blend manekina)
SLABOSCI = [
    "Każda broń to jedno sztywne akcesorium na RightGripAttachment; jako Tool trzeba ustawić Grip ręcznie "
    "(albo z attachment_pos z przedmioty.json).",
    "Płomienie miecza i lód kostura świecą tylko w renderze; w grze dać Neon albo ParticleEmitter.",
    "Przymiarki (szary manekin z bronią w pozie trzymanie) są tylko planszami, bez eksportu.",
]

ZACZEP = "RightGripAttachment"

PALETA = {
    "drewno": "9A6234", "drewno_jasne": "C98E52", "drewno_ciemne": "5E3A1A",
    "stal": "B4BFCE", "stal_cien": "7A879A", "stal_ciemna": "4A5468", "stal_jasna": "E2E8F1",
    "zelazo": "3A3F4C", "zelazo_jasne": "5D6577",
    "bandaz": "E9DDC2",
    "jajko": "FBF8F0", "zoltko": "FFB81C",
    "ogien_zolty": "FFE65A", "ogien": "FF6A00", "ogien_czerwony": "D9260C", "rubin": "E0223A",
    "lod": "34BDFF", "lod_jasny": "B5F1FF", "lod_ciemny": "1E7FE0", "srebro": "D5DCE6",
    "zupa": "E8552C", "marchew": "FF7A1F", "zielenina": "5ACD4A",
}

# Opis dla gry / plecaka. slot: Weapon (wszystkie); kategoria plecaka: Weapons; zaczep: RightGripAttachment.
# ranga 1…8 = kolejność odblokowania (od najsłabszej).
PRZEDMIOTY = [
    {"id": "palka_gwozdz", "nazwa": "Pałka z gwoździem", "ranga": 1},
    {"id": "patelnia", "nazwa": "Patelnia z jajkiem", "ranga": 2},
    {"id": "mlot_bojowy", "nazwa": "Młot bojowy", "ranga": 3},
    {"id": "topor_dwureczny", "nazwa": "Topór dwuręczny", "ranga": 4},
    {"id": "wlocznia_choragiew", "nazwa": "Włócznia z chorągiewką", "ranga": 5},
    {"id": "miecz_plomienisty", "nazwa": "Miecz płomienisty", "ranga": 6},
    {"id": "kostur_lodu", "nazwa": "Kostur lodu", "ranga": 7},
    {"id": "chochla_mistrza", "nazwa": "Wielka chochla mistrza", "ranga": 8},
]
for _p in PRZEDMIOTY:
    _p.update({"slot": "Weapon", "kategoria": "Weapons", "zaczep": ZACZEP})


def _akc(id, ikona_obrot=(0, 0, -45)):
    nazwa = next(p["nazwa"] for p in PRZEDMIOTY if p["id"] == id)
    return Akcesorium(id, nazwa, zaczep=ZACZEP, typ="Bron", paleta=PALETA, ikona_obrot=ikona_obrot)


def _uchwyt(a, dol, gora, kolor, sr=0.26, owijki=()):
    """Rękojeść / drzewce: walec wzdłuż Y od dol do gora (+ opcjonalne ciemniejsze owijki (y, kolor))."""
    a.walec("Uchwyt", (0, (dol + gora) / 2, 0), (sr, gora - dol, sr), kolor, "matowy", segm=8)
    for i, (y, kol) in enumerate(owijki):
        a.walec("Owijka %d" % i, (0, y, 0), (sr + 0.06, 0.09, sr + 0.06), kol, "matowy", segm=8, faza=0.0)


# --------------------------------------------------------------------------- 1. pałka z gwoździem
def palka_gwozdz():
    """Najprostsza broń: krzywa drewniana pałka rozszerzająca się ku górze, bandaż na rękojeści,
    trzy wbite gwoździe (jeden krzywy) i plaster na pęknięciu."""
    a = _akc("palka_gwozdz", ikona_obrot=(0, 0, -40))
    _uchwyt(a, -0.75, 0.7, "drewno")
    for i, y in enumerate((-0.5, -0.25, 0.0, 0.25, 0.5)):
        a.blok("Bandaz %d" % i, (0, y, 0), (0.32, 0.13, 0.32), "bandaz", "matowy", rot=(0, 0, 12), faza=0.02)
    a.blok("Bandaz koniec", (0.12, -0.72, 0.1), (0.1, 0.3, 0.06), "bandaz", "matowy", rot=(0, 0, 20), faza=0.0)
    with a.uklad(pos=(0, 0.6, 0), obrot=(0, 0, 4)):                   # lekko krzywy trzon
        a.ostroslup("Trzon", (0, 0.75, 0), (0.32, 1.5, 0.32), "drewno", "matowy", gora=(0.6, 0.6), faza=0.04)
        a.blok("Leb", (0, 1.82, 0), (0.62, 0.64, 0.62), "drewno", "matowy", rot=(0, 10, 0), faza=0.08)
        a.blok("Leb gora", (0, 2.17, 0), (0.5, 0.1, 0.5), "drewno_jasne", "matowy", rot=(0, 10, 0), faza=0.03)
        a.blok("Slady", (0.01, 1.2, 0.0), (0.46, 0.06, 0.46), "drewno_ciemne", "matowy", faza=0.0)
        # gwoździe: łebek + trzpień wystający na zewnątrz (−X, przód, tył)
        for i, (pos, rot) in enumerate((((-0.42, 1.9, 0.05), (0, 0, 90)), ((0.1, 1.68, 0.42), (90, 0, 0)),
                                        ((0.32, 2.05, -0.26), (-60, 0, -40)))):
            with a.uklad(pos=pos, obrot=rot):
                a.blok("Gwozdz leb %d" % i, (0, -0.1, 0), (0.17, 0.04, 0.17), "stal_cien", "metal", faza=0.0)
                a.blok("Gwozdz %d" % i, (0, 0.13, 0), (0.06, 0.42, 0.06), "stal", "metal", faza=0.0)
        a.blok("Plaster", (0.0, 1.5, 0.33), (0.3, 0.12, 0.04), "bandaz", "matowy", rot=(0, 0, 25), faza=0.0)
    return a


# --------------------------------------------------------------------------- 2. patelnia
def patelnia():
    """Żeliwna patelnia z drewnianą rączką; w środku sadzone jajko (białko + żółtko). Lico (dno w środku) do +Z."""
    a = _akc("patelnia", ikona_obrot=(0, 0, -35))
    _uchwyt(a, -0.7, 0.6, "drewno_ciemne", sr=0.28)
    a.walec("Pierscien", (0, -0.78, 0), (0.3, 0.08, 0.3), "zelazo_jasne", "metal", segm=8, faza=0.0)
    a.blok("Trzonek", (0, 0.85, 0), (0.2, 0.55, 0.14), "zelazo", "metal", faza=0.03)
    yc = 1.95                                                     # środek patelni
    a.walec("Patelnia", (0, yc, -0.02), (2.0, 0.26, 2.0), "zelazo", "metal", rot=(90, 0, 0), segm=12)
    a.walec("Dno", (0, yc, 0.12), (1.66, 0.04, 1.66), "zelazo_jasne", "metal", rot=(90, 0, 0), segm=12, faza=0.0)
    a.kula("Bialko", (0.1, yc - 0.06, 0.16), (1.0, 0.9, 0.12), "jajko", "polysk", segm=8)
    a.kula("Bialko 2", (-0.22, yc + 0.18, 0.16), (0.62, 0.5, 0.1), "jajko", "polysk", segm=8)
    a.kula("Zoltko", (0.02, yc + 0.02, 0.24), (0.42, 0.42, 0.2), "zoltko", "polysk", segm=8)
    a.blok("Dziobek", (-0.98, yc + 0.18, 0.0), (0.12, 0.3, 0.24), "zelazo", "metal", faza=0.03)
    return a


# --------------------------------------------------------------------------- 3. młot bojowy
def mlot_bojowy():
    """Młot: drewniane stylisko z rzemieniem, stalowy obuch z płaskim bijakiem na zewnątrz (−X), dziób na +X,
    złote opaski i szpic na czubku."""
    a = _akc("mlot_bojowy", ikona_obrot=(0, 0, -40))
    _uchwyt(a, -0.95, 2.45, "drewno", sr=0.26, owijki=((-0.62, "brazowy_ciemny"), (0.62, "brazowy_ciemny")))
    a.walec("Glowica", (0, -1.02, 0), (0.36, 0.16, 0.36), "stal_ciemna", "metal", segm=8)
    for i, y in enumerate((1.1, 1.8)):
        a.walec("Opaska %d" % i, (0, y, 0), (0.32, 0.1, 0.32), "zloto", "metal", segm=8, faza=0.0)
    yh = 2.62
    a.blok("Obuch", (0, yh, 0), (1.0, 0.78, 0.78), "stal", "metal", faza=0.06)
    a.blok("Bijak", (-0.62, yh, 0), (0.3, 0.98, 0.98), "stal", "metal", faza=0.06)
    a.blok("Bijak lico", (-0.79, yh, 0), (0.04, 0.78, 0.78), "stal_jasna", "metal", faza=0.0)
    a.ostroslup("Dziob", (0.82, yh, 0), (0.36, 0.7, 0.5), "stal_cien", "metal", rot=(0, 0, -90), gora=(0.0, 0.12))
    for zz in (1, -1):
        a.blok("Opaska obucha", (0, yh, zz * 0.4), (0.3, 0.84, 0.04), "zloto", "metal", faza=0.0)
        a.blok("Nit", (-0.3, yh, zz * 0.41), (0.12, 0.12, 0.04), "zloto", "metal", faza=0.0)
    a.ostroslup("Szpic", (0, yh + 0.6, 0), (0.36, 0.42, 0.36), "stal_cien", "metal", gora=(0, 0))
    for zz in (1, -1):
        a.blok("Okucie", (0, yh - 0.62, zz * 0.16), (0.2, 0.5, 0.04), "stal_ciemna", "metal", faza=0.0)
    return a


# --------------------------------------------------------------------------- 4. topór dwuręczny
def _ostrze_topora(a, zn, skala):
    """Półksiężycowe ostrze po stronie zn (−1 = −X, na zewnątrz): szyjka od tulei, wachlarz, wypukła jasna
    krawędź z trzech odcinków i rogi zawinięte w stronę styliska."""
    with a.uklad(skala=skala):
        a.ostroslup("Szyjka", (zn * 0.45, 0, 0), (0.62, 0.5, 0.14), "stal_ciemna", "metal", rot=(0, 0, zn * 90),
                    gora=(0.6, 0.14), faza=0.02)
        a.ostroslup("Wachlarz", (zn * 0.98, 0, 0), (2.0, 0.62, 0.14), "stal", "zwykly", rot=(0, 0, zn * 90),
                    gora=(0.62, 0.14), faza=0.02)
        # wypukła krawędź: środek + dwa łuki wychodzące poza rogi wachlarza
        a.blok("Krawedz", (zn * 1.36, 0, 0), (0.2, 1.1, 0.18), "stal_jasna", "metal", faza=0.0)
        for zy in (1, -1):
            a.blok("Krawedz luk", (zn * 1.2, zy * 0.86, 0), (0.2, 0.78, 0.18), "stal_jasna", "metal",
                   rot=(0, 0, zn * zy * 32), faza=0.0)


def topor_dwureczny():
    """Długie stylisko na dwie ręce, podwójne ostrze: duży półksiężyc na zewnątrz (−X) i mniejszy na +X,
    złoty romb na tulei, czerwone owijki, szpic na czubku i stalowy trzewik."""
    a = _akc("topor_dwureczny", ikona_obrot=(0, 0, -40))
    _uchwyt(a, -1.45, 3.35, "drewno_ciemne", sr=0.26,
            owijki=((-0.62, "czerwony"), (0.62, "czerwony"), (-1.25, "czerwony"), (1.0, "czerwony")))
    a.ostroslup("Trzewik", (0, -1.62, 0), (0.3, 0.28, 0.3), "stal_ciemna", "metal", rot=(180, 0, 0), gora=(0.12, 0.12))
    yh = 2.85
    a.blok("Tuleja", (0, yh, 0), (0.46, 1.0, 0.42), "stal_ciemna", "metal", faza=0.05)
    with a.uklad(pos=(0, yh, 0)):
        _ostrze_topora(a, -1, 1.0)
        _ostrze_topora(a, 1, 0.72)
    for zz in (1, -1):
        a.blok("Zdobienie", (0, yh, zz * 0.22), (0.26, 0.26, 0.04), "zloto", "metal", rot=(0, 0, 45), faza=0.0)
    a.walec("Pierscien", (0, yh - 0.56, 0), (0.36, 0.1, 0.36), "zloto", "metal", segm=8, faza=0.0)
    a.ostroslup("Szpic", (0, 3.62, 0), (0.32, 0.55, 0.22), "stal", "metal", gora=(0.0, 0.0))
    return a


# --------------------------------------------------------------------------- 5. włócznia z chorągiewką
def wlocznia_choragiew():
    """Bardzo długie drzewce, liściasty grot ze skrzydełkami, pod nim niebieska chorągiewka z jaskółczym ogonem
    i złotym rombem (na zewnątrz, −X), złote okucia."""
    a = _akc("wlocznia_choragiew", ikona_obrot=(0, 0, -45))
    _uchwyt(a, -1.9, 4.1, "drewno_jasne", sr=0.26, owijki=((-0.62, "niebieski_ciemny"), (0.62, "niebieski_ciemny")))
    a.stozek("Trzewik", (0, -2.07, 0), (0.28, 0.34, 0.28), "zloto", "metal", rot=(180, 0, 0), gora=0.3, segm=8)
    a.walec("Okucie", (0, 4.18, 0), (0.34, 0.36, 0.34), "zloto", "metal", segm=8)
    for zn in (1, -1):
        a.blok("Skrzydelko", (zn * 0.3, 4.36, 0), (0.44, 0.12, 0.12), "stal_cien", "metal", rot=(0, 0, zn * 30),
               faza=0.0)
    a.ostroslup("Grot dol", (0, 4.6, 0), (0.86, 0.3, 0.14), "stal", "metal", rot=(180, 0, 0), gora=(0.24, 0.14),
                faza=0.0)
    a.ostroslup("Grot", (0, 5.4, 0), (0.86, 1.3, 0.14), "stal", "metal", gora=(0.0, 0.04), faza=0.0)
    a.blok("Grot zebro", (0, 5.1, 0), (0.1, 0.9, 0.18), "stal_jasna", "metal", faza=0.0)
    # chorągiewka na zewnątrz (−X)
    yc = 3.25
    a.blok("Choragiew", (-0.86, yc, 0), (1.5, 1.1, 0.06), "niebieski", "matowy", faza=0.02)
    for zn in (1, -1):
        a.ostroslup("Ogon", (-1.85, yc + zn * 0.275, 0), (0.55, 0.5, 0.06), "niebieski", "matowy",
                    rot=(0, 0, 90), gora=(0.0, 0.06), faza=0.0)
    a.blok("Lamowka", (-1.0, yc + 0.59, 0), (1.8, 0.1, 0.1), "zloto", "metal", faza=0.0)
    a.blok("Lamowka dol", (-0.86, yc - 0.57, 0), (1.5, 0.06, 0.08), "zloto", "metal", faza=0.0)
    for zz in (1, -1):
        a.blok("Romb", (-0.88, yc - 0.02, zz * 0.045), (0.46, 0.46, 0.04), "zloto", "metal", rot=(0, 0, 45),
               faza=0.0)
        a.blok("Romb srodek", (-0.88, yc - 0.02, zz * 0.07), (0.2, 0.2, 0.03), "czerwony", "matowy", rot=(0, 0, 45),
               faza=0.0)
    for i, y in enumerate((yc - 0.4, yc + 0.4)):
        a.walec("Uchwyt flagi %d" % i, (0, y, 0), (0.32, 0.1, 0.32), "zloto", "metal", segm=8, faza=0.0)
    return a


# --------------------------------------------------------------------------- 6. miecz płomienisty
def miecz_plomienisty():
    """Świecąca żółto-pomarańczowa klinga z językami ognia na obu krawędziach i płomiennym sztychem, jelec
    z ciemnego żelaza w kształcie płomieni z rubinem, czerwona rękojeść."""
    a = _akc("miecz_plomienisty", ikona_obrot=(0, 0, -45))
    _uchwyt(a, -0.62, 0.62, "czerwony_ciemny", sr=0.26, owijki=((-0.3, "zelazo"), (0.3, "zelazo")))
    a.ostroslup("Glowica", (0, -0.86, 0), (0.42, 0.3, 0.42), "zelazo", "metal", rot=(180, 45, 0), gora=(0.0, 0.0))
    a.blok("Glowica rubin", (0, -0.7, 0), (0.24, 0.24, 0.24), "rubin", "swiecacy", rot=(45, 0, 45), faza=0.0)
    a.blok("Jelec", (0, 0.74, 0), (0.9, 0.24, 0.34), "zelazo", "metal", faza=0.04)
    for zn in (1, -1):
        a.ostroslup("Jelec plomien", (zn * 0.55, 0.92, 0), (0.34, 0.6, 0.3), "zelazo", "metal",
                    rot=(0, 0, -zn * 35), gora=(0.0, 0.08), faza=0.0)
    a.blok("Rubin", (0, 0.76, 0.18), (0.24, 0.24, 0.06), "rubin", "swiecacy", rot=(0, 0, 45), faza=0.0)
    a.blok("Rubin tyl", (0, 0.76, -0.18), (0.24, 0.24, 0.06), "rubin", "swiecacy", rot=(0, 0, 45), faza=0.0)
    # klinga
    a.blok("Klinga", (0, 2.25, 0), (0.56, 2.8, 0.14), "ogien", "swiecacy", faza=0.03)
    a.blok("Rdzen", (0, 2.15, 0), (0.22, 2.4, 0.18), "ogien_zolty", "swiecacy", faza=0.0)
    for i, (y, zn, s) in enumerate(((1.25, 1, 0.5), (1.6, -1, 0.55), (2.05, 1, 0.6), (2.45, -1, 0.6),
                                    (2.9, 1, 0.55), (3.25, -1, 0.5))):
        a.ostroslup("Jezyk %d" % i, (zn * 0.34, y, 0), (0.32, s, 0.12), "ogien_czerwony" if i % 2 else "ogien",
                    "swiecacy", rot=(0, 0, -zn * 30), gora=(0.0, 0.06), faza=0.0)
    a.ostroslup("Sztych", (0, 3.95, 0), (0.56, 0.6, 0.14), "ogien", "swiecacy", gora=(0.0, 0.06),
                przes_gory=(0.12, 0), faza=0.0)
    a.ostroslup("Sztych rdzen", (0, 3.6, 0), (0.22, 0.5, 0.18), "ogien_zolty", "swiecacy", gora=(0.0, 0.0), faza=0.0)
    return a


# --------------------------------------------------------------------------- 7. kostur lodu
def kostur_lodu():
    """Srebrne drzewce z błękitną owijką, u góry trzy srebrne szpony trzymające wielki błękitny kryształ
    otoczony odłamkami; na dole lodowy szpic."""
    a = _akc("kostur_lodu", ikona_obrot=(0, 0, -40))
    _uchwyt(a, -1.5, 3.0, "srebro", sr=0.26, owijki=((-0.62, "lod_ciemny"), (0.62, "lod_ciemny"), (2.3, "lod_ciemny")))
    a.walec("Owijka", (0, 1.45, 0), (0.31, 0.7, 0.31), "lod_ciemny", "matowy", segm=8, faza=0.0)
    a.ostroslup("Lodowy szpic", (0, -1.75, 0), (0.34, 0.5, 0.34), "lod", "swiecacy", rot=(180, 45, 0), gora=(0, 0))
    a.walec("Kolnierz", (0, 3.05, 0), (0.56, 0.24, 0.56), "srebro", "metal", segm=8)
    for i, ry in enumerate((0, 120, 240)):
        with a.uklad(pos=(0, 3.15, 0), obrot=(0, ry, 0)):
            a.blok("Szpon %d" % i, (0, 0.4, 0.4), (0.14, 0.78, 0.14), "srebro", "metal", rot=(32, 0, 0), faza=0.02)
            a.ostroslup("Szpon szpic %d" % i, (0, 0.92, 0.6), (0.14, 0.34, 0.14), "srebro", "metal", rot=(-12, 0, 0),
                        gora=(0, 0))
    yk = 4.0
    a.ostroslup("Krysztal dol", (0, yk - 0.38, 0), (0.95, 0.76, 0.95), "lod", "swiecacy", rot=(180, 45, 0),
                gora=(0, 0))
    a.ostroslup("Krysztal gora", (0, yk + 0.7, 0), (0.95, 1.4, 0.95), "lod", "swiecacy", rot=(0, 45, 0), gora=(0, 0))
    a.blok("Krysztal blask", (0.0, yk + 0.25, 0.0), (0.16, 0.8, 0.7), "lod_jasny", "swiecacy", rot=(0, 45, 0),
           faza=0.0)
    for i, (x, y, rz, s) in enumerate(((-0.7, yk + 0.25, 38, 0.8), (0.7, yk + 0.1, -38, 0.75),
                                       (-0.5, yk - 0.5, 75, 0.5), (0.52, yk + 0.85, -22, 0.55))):
        a.ostroslup("Odlamek %d" % i, (x, y, 0.06 * (i % 2)), (0.3, s, 0.3), "lod_ciemny" if i % 2 else "lod",
                    "swiecacy", rot=(0, 45, rz), gora=(0, 0))
    return a


# --------------------------------------------------------------------------- 8. wielka chochla mistrza
def chochla_mistrza():
    """Żart na koniec drabinki: ogromna złota chochla. Głęboka czasza z gorącą zupą pomidorową
    i warzywami, złoty trzonek z fioletową owijką i klejnotami, koronka przy czaszy, ucho do wieszania na dole."""
    a = _akc("chochla_mistrza", ikona_obrot=(0, 45, -30))       # ikona z ukosa: widać głębię czaszy, nie „talerz”
    _uchwyt(a, -1.2, 2.5, "zloto", sr=0.26)
    a.walec("Owijka", (0, 0.0, 0), (0.32, 1.1, 0.32), "fiolet", "matowy", segm=8)
    for i, y in enumerate((-0.6, 0.6)):
        a.walec("Okucie %d" % i, (0, y, 0), (0.36, 0.1, 0.36), "zloto_ciemne", "metal", segm=8, faza=0.0)
    # ucho na dole (pierścień z czterech klocków w płaszczyźnie XY)
    for i, (x, y, sx, sy) in enumerate(((0, -1.25, 0.56, 0.12), (0, -1.8, 0.56, 0.12), (-0.22, -1.52, 0.12, 0.5),
                                         (0.22, -1.52, 0.12, 0.5))):
        a.blok("Ucho %d" % i, (x, y, 0), (sx, sy, 0.14), "zloto", "metal", faza=0.0)
    for i, y in enumerate((1.2, 1.85)):
        for zz in (1, -1):
            a.blok("Klejnot %d" % i, (0, y, zz * 0.13), (0.2, 0.2, 0.06), "fiolet_jasny", "swiecacy",
                   rot=(0, 0, 45), faza=0.0)
    # koronka przy czaszy
    a.walec("Korona", (0, 2.4, 0), (0.5, 0.16, 0.5), "zloto", "metal", segm=8)
    for i, ry in enumerate((0, 90, 180, 270)):
        with a.uklad(pos=(0, 2.5, 0), obrot=(0, ry + 45, 0)):
            a.ostroslup("Zabek %d" % i, (0, 0.12, 0.18), (0.14, 0.24, 0.08), "zloto", "metal", gora=(0, 0))
    # szyjka: trzonek odgina się do tyłu (−Z) i wchodzi w dno czaszy — z boku sylwetka „J” chochli
    a.blok("Szyjka", (0, 2.92, -0.24), (0.26, 0.86, 0.26), "zloto", "metal", rot=(-50, 0, 0), faza=0.04)
    # czasza: ścięty stożek (wąskie dno, szeroki wylot), wylot odchylony o 35° ku górze — tak chochla „nabiera”,
    # a z przodu widać zarówno zupę, jak i złoty bok czaszy; gruby rant, zupa pomidorowa z warzywami
    # czasza pochylona o 60° (nabiera do przodu) — z boku i z ukosa czyta się jak chochla, nie lizak
    with a.uklad(pos=(0, 3.75, -0.32), obrot=(-60, 0, 0)):
        a.stozek("Czasza", (0, 0, 0), (1.2, 1.0, 1.2), "zloto", "metal", rot=(90, 0, 0), gora=1.75, segm=12)
        a.walec("Dno", (0, 0, -0.55), (0.84, 0.12, 0.84), "zloto_ciemne", "metal", rot=(90, 0, 0), segm=8, faza=0.0)
        a.walec("Rant", (0, 0, 0.55), (2.36, 0.18, 2.36), "zloto_ciemne", "metal", rot=(90, 0, 0), segm=12,
                faza=0.03)
        a.walec("Wnetrze", (0, 0, 0.62), (2.06, 0.06, 2.06), "zloto_ciemne", "metal", rot=(90, 0, 0), segm=12,
                faza=0.0)                                          # ścianka czaszy 0,15 widoczna nad zupą
        a.walec("Zupa", (0, 0, 0.64), (1.76, 0.06, 1.76), "zupa", "polysk", rot=(90, 0, 0), segm=12, faza=0.0)
        for i, (x, y, kol) in enumerate(((-0.42, 0.3, "marchew"), (0.4, -0.22, "marchew"), (0.08, 0.52, "zielenina"),
                                         (-0.25, -0.44, "zielenina"), (0.5, 0.34, "jajko"))):
            a.blok("Warzywo %d" % i, (x, y, 0.72), (0.26, 0.26, 0.12), kol, "zwykly", rot=(0, 0, 20 + 30 * i),
                   faza=0.0)
        a.blok("Klejnot czaszy", (0, -1.2, 0.5), (0.32, 0.32, 0.08), "fiolet_jasny", "swiecacy", rot=(0, 0, 45),
               faza=0.0)
    return a


# --------------------------------------------------------------------------- zbrojownia
BUDOWNICZE = [palka_gwozdz, patelnia, mlot_bojowy, topor_dwureczny, wlocznia_choragiew, miecz_plomienisty,
              kostur_lodu, chochla_mistrza]


def akcesoria():
    return [f() for f in BUDOWNICZE]


def przymiarka(a):
    """Szary manekin R15 z jedną bronią w prawej dłoni (poza „trzymanie”)."""
    p = manekin_r15("przym_" + a.id, "Przymiarka: " + a.nazwa, klipy=False)
    klip_spoczynek_r15(p)
    klip_trzymanie_r15(p)
    p.zaloz(a)
    p.ustaw_poze_renderu("trzymanie", 0)
    return p


def zbuduj():
    akc = akcesoria()
    return [przymiarka(a) for a in akc] + akc
