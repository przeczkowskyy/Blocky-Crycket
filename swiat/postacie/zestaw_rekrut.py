FILMY = ["chod"]                     # przebuduj.py: film i arkusz klatek tylko dla chodu przymiarki

# -*- coding: utf-8 -*-
"""ZESTAW „REKRUT” — startowy ekwipunek gracza (awatar R15): skórzana czapka z nausznikami, pikowana przeszywanica
z czerwoną łatą, skórzane rękawice, połatane buty, sznurek z sakiewką, drewniany miecz ćwiczebny oraz trzy drobiazgi
tylko do ikon (ząb na rzemyku, miedziany pierścień, zardzewiała podkowa).

    python -B swiat/postacie/biblioteka/podglad_postaci.py --modul swiat/postacie/zestaw_rekrut.py --wyj <folder> --klip chod

Status: propozycja (nic tu nie jest kanonem gry; styl wg B&C/Styl/Kierunek artystyczny.md i obrazu referencyjnego).
Kolory: brązy i beże, jeden akcent czerwony (łata na przeszywanicy).

Budowa:
- każdy przedmiot to osobne SZTYWNE akcesorium (jedna siatka, (0,0,0) = punkt zaczepienia) dopasowane do klockowego
  manekina R15 biblioteki (5,25 studa: tułów 2×1,6×1, dłoń 1×0,3×1, stopa 1×0,35×1);
- ręce klockowego R15 przylegają do tułowia (wewnętrzna ściana ręki na x = ±1,0), a nogi do siebie (x = 0) —
  dlatego przeszywanica i pas mieszczą się w szerokości ±0,98 (pogrubiają tułów tylko z przodu i z tyłu),
  a rękawice i buty nie wystają po wewnętrznej stronie dłoni/nogi;
- rękawice i buty są parami: do noszenia osobno lewa i prawa (rekrut_rekawica_l/_p, rekrut_but_l/_p), a do ikony
  slotu osobny model pary (rekrut_rekawice, rekrut_buty — nieeksportowany na manekina);
- rękawica siedzi na Left/RightGripAttachment, który ma obrót (90, 0, 0) — bryły są modelowane w osiach ciała
  w układzie z obrotem (−90, 0, 0), a ikona odwraca to przez ikona_obrot=(90, 0, 0);
- miecz: konwencja broni biblioteki (rękojeść w (0,0,0), klinga w +Y, płaz do +Z);
- drobiazgi (Amulet, Ring, Trinket) to modele do ikon: ułożone frontem do kamery, nie zakładane na manekina
  (klockowa głowa siedzi wprost na tułowiu, więc rzemyk „na szyi” musiałby przenikać przez głowę).

PRZEDMIOTY (id, nazwa, slot, kategoria plecaka, punkt zaczepienia) — patrz lista ZESTAW niżej.
"""
import math

from swiat.postacie.biblioteka.postac import Akcesorium, manekin_r15

ID = "zestaw_rekrut"

# --------------------------------------------------------------------------- kolory (brązy, beże, jeden czerwony)
SKORA = "9A6234"          # skóra średnia
SKORA_J = "C08A55"        # skóra jasna
SKORA_C = "5E3A1A"        # skóra ciemna
BEZ = "EBD3A2"            # len, filc
BEZ_C = "C9A46C"          # len w cieniu, szwy pikowania
LINA = "D2B47E"           # sznurek
LINA_C = "9C7B48"
CZERWONY = "D7382C"       # jedyny akcent czerwony: łata
DREWNO = "D9A964"
DREWNO_C = "A06A36"
DREWNO_SL = "B9864A"      # słoje
MIEDZ = "D07A3E"
MIEDZ_C = "9C5226"
RDZA = "B65A2A"
RDZA_C = "74381C"
RDZA_J = "E39048"
ZAB = "F2EBD8"
KAMIEN = "6E4424"         # oczko pierścienia (ciemny bursztyn)
SZWY = "4A2C14"
PODESZWA = "3E2614"

# Lista slotów (jak w oknie ekwipunku). „noszony” = zakładany na manekina przymiarki; „ikona_slotu” = model,
# którego ikona idzie do okna ekwipunku.
ZESTAW = [
    {"id": "rekrut_czapka", "nazwa": "Skórzana czapka rekruta", "slot": "Helmet", "kategoria": "Armor",
     "zaczep": "HatAttachment", "noszony": True, "ikona_slotu": True},
    {"id": "rekrut_przeszywanica", "nazwa": "Przeszywanica rekruta", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "BodyFrontAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_przeszywanica_cala", "nazwa": "Przeszywanica rekruta (z rękawami)", "slot": "Chest",
     "kategoria": "Armor", "zaczep": "BodyFrontAttachment", "noszony": False, "ikona_slotu": True},
    {"id": "rekrut_rekaw_l", "nazwa": "Rękaw przeszywanicy (lewy)", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "LeftShoulderAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_rekaw_p", "nazwa": "Rękaw przeszywanicy (prawy)", "slot": "Chest", "kategoria": "Armor",
     "zaczep": "RightShoulderAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_rekawica_l", "nazwa": "Skórzana rękawica (lewa)", "slot": "Gloves", "kategoria": "Armor",
     "zaczep": "LeftGripAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_rekawica_p", "nazwa": "Skórzana rękawica (prawa)", "slot": "Gloves", "kategoria": "Armor",
     "zaczep": "RightGripAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_rekawice", "nazwa": "Skórzane rękawice rekruta", "slot": "Gloves", "kategoria": "Armor",
     "zaczep": "RightGripAttachment", "noszony": False, "ikona_slotu": True},
    {"id": "rekrut_but_l", "nazwa": "Połatany but (lewy)", "slot": "Boots", "kategoria": "Armor",
     "zaczep": "LeftFootAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_but_p", "nazwa": "Połatany but (prawy)", "slot": "Boots", "kategoria": "Armor",
     "zaczep": "RightFootAttachment", "noszony": True, "ikona_slotu": False},
    {"id": "rekrut_buty", "nazwa": "Połatane buty rekruta", "slot": "Boots", "kategoria": "Armor",
     "zaczep": "RightFootAttachment", "noszony": False, "ikona_slotu": True},
    {"id": "rekrut_pas", "nazwa": "Sznurek z sakiewką", "slot": "Belt", "kategoria": "Armor",
     "zaczep": "WaistCenterAttachment", "noszony": True, "ikona_slotu": True},
    {"id": "rekrut_miecz", "nazwa": "Drewniany miecz ćwiczebny", "slot": "Weapon", "kategoria": "Weapons",
     "zaczep": "RightGripAttachment", "noszony": True, "ikona_slotu": True},
    {"id": "rekrut_amulet", "nazwa": "Ząb na rzemyku", "slot": "Amulet", "kategoria": "Amulets",
     "zaczep": "NeckAttachment", "noszony": False, "ikona_slotu": True},
    {"id": "rekrut_pierscien", "nazwa": "Miedziany pierścień", "slot": "Ring", "kategoria": "Amulets",
     "zaczep": "RightGripAttachment", "noszony": False, "ikona_slotu": True},
    {"id": "rekrut_podkowa", "nazwa": "Zardzewiała podkowa", "slot": "Trinket", "kategoria": "Others",
     "zaczep": "WaistCenterAttachment", "noszony": False, "ikona_slotu": True},
]
_PO_ID = {z["id"]: z for z in ZESTAW}


def _akc(id_, typ, ikona_obrot=(0, 0, 0)):
    z = _PO_ID[id_]
    return Akcesorium(id_, z["nazwa"], zaczep=z["zaczep"], typ=typ, ikona_obrot=ikona_obrot)


def _odcinek(a, nazwa, p1, p2, grub, glebia, kolor, mat="matowy", faza=0.0, z=0.0):
    """Belka w płaszczyźnie XY od p1 do p2 (rzemyk, łuk podkowy, obrączka)."""
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    dl = math.hypot(dx, dy)
    kat = math.degrees(math.atan2(dy, dx))
    a.blok(nazwa, ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, z), (dl, grub, glebia), kolor, mat,
           rot=(0, 0, kat), faza=faza)


# --------------------------------------------------------------------------- Helmet
def czapka():
    """Skórzana czapka z nausznikami i lnianą opaską. (0,0,0) = HatAttachment (środek góry głowy 1,25³;
    środek głowy (0, −0,625, 0), przód głowy z = 0,625, oczy manekina sięgają do y ≈ −0,41)."""
    a = _akc("rekrut_czapka", "Hat")
    a.blok("Czapa", (0, -0.1, 0), (1.46, 0.42, 1.46), SKORA, "matowy", faza=0.14)          # y −0,31…0,11
    a.ostroslup("Wierzch", (0, 0.25, 0), (1.46, 0.3, 1.46), SKORA, "matowy", gora=(0.62, 0.62))  # kopułka
    for zn in (1, -1):                                          # szwy klinów czapki na skosach kopułki
        a.blok("Szew", (zn * 0.53, 0.262, 0), (0.5, 0.05, 0.07), SKORA_C, "matowy", rot=(0, 0, -zn * 35.5), faza=0.0)
        a.blok("Szew", (0, 0.262, zn * 0.53), (0.07, 0.05, 0.5), SKORA_C, "matowy", rot=(zn * 35.5, 0, 0), faza=0.0)
    a.blok("Guzik", (0, 0.43, 0), (0.22, 0.1, 0.22), SKORA_C, "matowy", faza=0.03)
    a.blok("Obszycie", (0, -0.3, 0), (1.5, 0.12, 1.5), SKORA_C, "matowy", faza=0.03)
    a.blok("Futro przod", (0, -0.23, 0.79), (1.34, 0.26, 0.16), BEZ, "matowy", rot=(-12, 0, 0), faza=0.07)
    for x in (-0.36, 0.0, 0.36):                                # kępki futra
        a.blok("Kepka", (x, -0.1, 0.83), (0.2, 0.08, 0.1), BEZ_C, "matowy", rot=(-12, 0, 0), faza=0.0)
    for zn in (1, -1):                                        # szerokie nauszniki z futrzanym brzegiem
        with a.uklad(pos=(zn * 0.76, -0.55, 0.02), obrot=(0, 0, zn * 5)):
            a.blok("Nausznik", (0, 0, 0), (0.18, 0.6, 0.96), SKORA, "matowy", faza=0.06)     # zachodzi na czapę
            a.blok("Futro dol", (0.01 * zn, -0.3, 0), (0.22, 0.14, 1.0), BEZ, "matowy", faza=0.05)
            a.blok("Futro przod", (0.01 * zn, -0.02, 0.48), (0.22, 0.56, 0.1), BEZ, "matowy", faza=0.03)
            a.blok("Szew", (0.1 * zn, 0.0, -0.05), (0.03, 0.34, 0.06), SKORA_C, "matowy", faza=0.0)
    a.blok("Karkowiec", (0, -0.56, -0.72), (1.36, 0.44, 0.15), SKORA, "matowy", faza=0.05)
    a.blok("Karkowiec futro", (0, -0.8, -0.73), (1.4, 0.1, 0.19), BEZ, "matowy", faza=0.03)
    return a


# --------------------------------------------------------------------------- Chest
def przeszywanica():
    """Pikowana lniana przeszywanica z czerwoną łatą. (0,0,0) = BodyFrontAttachment (środek przedniej ściany
    UpperTorso 2×1,6×1, czyli środek tułowia w (0, 0, −0,5)); dół zachodzi na LowerTorso (do y = −1,18).
    Szerokość ±0,98 — ręce klockowego R15 przylegają do tułowia na x = ±1."""
    a = _akc("rekrut_przeszywanica", "Front")
    _przeszywanica_bryly(a)
    return a


def _przeszywanica_bryly(a):
    zc = -0.5                                                  # środek tułowia
    a.blok("Korpus", (0, -0.2, zc), (1.96, 1.96, 1.16), BEZ_C, "matowy", faza=0.06)   # y −1,18…0,78
    a.blok("Otwor szyi", (0, 0.785, zc), (1.0, 0.02, 0.8), SZWY, "matowy", faza=0.0)  # pod głową — widać w ikonie
    for zn in (1, -1):
        a.blok("Naramiennik", (zn * 0.805, 0.8, zc), (0.35, 0.2, 1.2), BEZ, "matowy", faza=0.05)
        for x in (0.28, 0.66):                                 # pionowe kanały pikowania z przodu i z tyłu
            a.blok("Kanal przod", (zn * x, -0.25, 0.1), (0.34, 1.7, 0.08), BEZ, "matowy", faza=0.035)
            a.blok("Kanal tyl", (zn * x, -0.25, zc - 0.6), (0.34, 1.7, 0.08), BEZ, "matowy", faza=0.0)
    a.blok("Kolnierz", (0, 0.7, 0.13), (1.3, 0.14, 0.1), BEZ, "matowy", faza=0.03)
    a.blok("Rozciecie", (0, -0.2, 0.1), (0.08, 1.6, 0.06), SZWY, "matowy", faza=0.0)
    for y in (0.4, 0.0, -0.4):                                 # wiązania na środku
        a.blok("Wiazanie", (0, y, 0.15), (0.3, 0.06, 0.04), SKORA_C, "matowy", faza=0.0)
    a.blok("Lamowka", (0, -1.12, zc), (1.98, 0.1, 1.2), SKORA, "matowy", faza=0.03)
    # łata — jedyny czerwony akcent zestawu (lewa pierś noszącego = +X)
    a.blok("Lata", (0.5, 0.28, 0.165), (0.46, 0.42, 0.05), CZERWONY, "matowy", rot=(0, 0, 9), faza=0.02)
    with a.uklad(pos=(0.5, 0.28, 0.2), obrot=(0, 0, 9)):
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            a.blok("Scieg laty", (sx * 0.17, sy * 0.15, 0), (0.08, 0.035, 0.03), BEZ, "matowy", faza=0.0)


def _rekaw_bryly(a, zn):
    # rękaw do łokcia (y −0,86…0,06): między rękawem a wysokim mankietem rękawicy nie prześwituje manekin
    a.blok("Rekaw", (zn * 0.04, -0.4, 0), (1.07, 0.92, 1.12), BEZ_C, "matowy", faza=0.06)
    for dz in (-0.27, 0.0, 0.27):                               # kanały pikowania na zewnętrznym boku
        a.blok("Kanal", (zn * 0.6, -0.38, dz), (0.06, 0.78, 0.22), BEZ, "matowy", faza=0.0)
    for zz in (1, -1):                                          # i z przodu / z tyłu
        a.blok("Kanal", (zn * 0.04, -0.38, zz * 0.585), (0.6, 0.78, 0.05), BEZ, "matowy", faza=0.0)
    a.blok("Lamowka", (zn * 0.05, -0.85, 0), (1.1, 0.1, 1.16), SKORA, "matowy", faza=0.03)


def rekaw(strona):
    """Krótki pikowany rękaw — część slotu Chest, sztywny na Left/RightShoulderAttachment (środek góry UpperArm
    1×0,95×1), więc idzie za ramieniem. Od strony tułowia ściana na 0,495 (nie wchodzi w przeszywanicę)."""
    zn = 1 if strona == "l" else -1
    a = _akc("rekrut_rekaw_" + strona, "Shoulder")
    _rekaw_bryly(a, zn)
    return a


def przeszywanica_cala():
    """Model do ikony slotu Chest: korpus + oba rękawy odchylone na boki (sylwetka kaftana)."""
    a = _akc("rekrut_przeszywanica_cala", "Inne")
    _przeszywanica_bryly(a)
    for zn in (1, -1):                                          # ShoulderAttachment w układzie BodyFront
        with a.uklad(pos=(zn * 1.52, 0.8, -0.5), obrot=(0, 0, zn * 9)):
            _rekaw_bryly(a, zn)
    return a


# --------------------------------------------------------------------------- Gloves
def _rekawica(a, zn):
    """Rękawica w osiach ciała, (0,0,0) = środek klocka dłoni 1×0,3×1 (pod przedramieniem 1×0,75×1).
    zn = +1 lewa (ręka na +X, wnętrze w stronę −X), −1 prawa. Od strony tułowia ściana na 0,505 (nie wystaje)."""
    wn = -zn                                                   # kierunek do tułowia
    # Klockowa dłoń zwisa „palcami w dół”: palce to cztery klocki pod dłonią, kciuk z przodu.
    a.blok("Dlon", (zn * 0.035, -0.02, 0.01), (1.08, 0.38, 1.1), SKORA_J, "matowy", faza=0.06)
    for i, (z, dl) in enumerate(((0.36, 0.2), (0.12, 0.24), (-0.12, 0.23), (-0.36, 0.18))):
        a.blok("Palec", (zn * 0.06, -0.2 - dl / 2, z), (0.8, dl, 0.21), SKORA_J, "matowy", faza=0.06)
    a.blok("Kciuk", (wn * 0.18, -0.12, 0.64), (0.3, 0.42, 0.22), SKORA_J, "matowy", rot=(-15, 0, 0), faza=0.06)
    # mankiet-rękawica rozszerzony na zewnątrz, z przodu i z tyłu (od strony tułowia płasko)
    # mankiet rozszerza się ku górze (ostrosłup odwrócony), od strony tułowia ściana zostaje pionowa na 0,5
    # wysoki mankiet (+0,3): sięga prawie do łokcia
    a.ostroslup("Mankiet", (zn * 0.05, 0.5, 0), (1.1, 0.66, 1.14), SKORA, "matowy", gora=(1.24, 1.28),
                przes_gory=(zn * 0.07, 0))
    a.blok("Wywiniecie", (zn * 0.12, 0.86, 0), (1.26, 0.08, 1.3), SKORA_C, "matowy", faza=0.03)
    a.blok("Otwor", (zn * 0.12, 0.905, 0), (1.04, 0.02, 1.08), SZWY, "matowy", faza=0.0)
    a.blok("Rzemyk", (zn * 0.66, 0.45, 0), (0.04, 0.08, 0.8), BEZ_C, "matowy", rot=(0, 0, zn * 18), faza=0.0)
    a.blok("Lata", (zn * 0.575, -0.02, 0.1), (0.04, 0.22, 0.34), SKORA, "matowy", faza=0.0)


def rekawica(strona):
    zn = 1 if strona == "l" else -1
    a = _akc("rekrut_rekawica_" + strona, "Inne", ikona_obrot=(55, 0, 0) if zn > 0 else (125, 180, 0))
    with a.uklad(obrot=(-90, 0, 0)):                           # Grip ma obrót (90,0,0) — wracamy do osi ciała
        _rekawica(a, zn)
    return a


def rekawice_para():
    a = _akc("rekrut_rekawice", "Inne")
    for zn in (1, -1):                                         # palcami do góry, kciukami do siebie
        with a.uklad(pos=(-zn * 0.7, 0, zn * 0.1), obrot=(0, -zn * 12, 180)):
            _rekawica(a, zn)
    return a


# --------------------------------------------------------------------------- Boots
def _but(a, zn):
    """But w osiach ciała, (0,0,0) = FootAttachment (środek spodu stopy 1×0,35×1; nad nią podudzie 1×0,8×1).
    Od strony drugiej nogi ściana na 0,495 (nogi klockowego R15 stykają się na x = 0)."""
    a.blok("Podeszwa", (zn * 0.035, 0.03, 0.24), (1.07, 0.1, 1.62), PODESZWA, "matowy", faza=0.03)  # z −0,57…1,05
    a.blok("Obcas", (zn * 0.035, 0.05, -0.4), (1.07, 0.16, 0.36), PODESZWA, "matowy", faza=0.0)
    a.blok("Przyszwa", (zn * 0.04, 0.22, 0.14), (1.07, 0.3, 1.44), SKORA_C, "matowy", faza=0.1)  # z −0,58…0,86
    a.ostroslup("Nosek", (zn * 0.04, 0.22, 0.86), (1.0, 0.3, 0.36), SKORA_C, "matowy", gora=(0.84, 0.14),
                przes_gory=(0, -0.08))                           # zadarty, zaokrąglony nosek
    a.blok("Lata nosek", (zn * 0.1, 0.33, 0.68), (0.36, 0.06, 0.26), SKORA_J, "matowy", rot=(0, 10, 0), faza=0.01)
    a.blok("Cholewa", (zn * 0.04, 0.73, 0), (1.07, 0.74, 1.08), SKORA, "matowy", faza=0.05)    # y 0,36…1,10
    a.blok("Wywiniecie", (zn * 0.06, 1.06, 0), (1.13, 0.2, 1.14), SKORA_J, "matowy", faza=0.05)
    a.blok("Otwor", (zn * 0.06, 1.165, 0), (0.86, 0.02, 0.86), SZWY, "matowy", faza=0.0)        # ciemny wlot
    a.blok("Pasek", (zn * 0.04, 0.55, 0), (1.1, 0.08, 1.11), SKORA_C, "matowy", faza=0.0)
    a.blok("Sprzaczka", (zn * 0.04, 0.55, 0.565), (0.18, 0.15, 0.04), "B9C3D0", "metal", faza=0.0)
    a.blok("Lata", (zn * 0.575, 0.78, 0.08), (0.05, 0.3, 0.34), SKORA_J, "matowy", rot=(10, 0, 0), faza=0.015)
    for dz in (-0.12, 0.12):
        a.blok("Scieg", (zn * 0.6, 0.78, 0.08 + dz), (0.03, 0.06, 0.06), SZWY, "matowy", faza=0.0)


def but(strona):
    zn = 1 if strona == "l" else -1
    a = _akc("rekrut_but_" + strona, "Inne", ikona_obrot=(0, -55, 0))     # ikona: profil z noskiem w lewo
    _but(a, zn)
    return a


def buty_para():
    a = _akc("rekrut_buty", "Inne")
    for i, zn in enumerate((-1, 1)):                           # para w profilu, jeden za drugim (drugi wyżej w kadrze)
        with a.uklad(pos=(0.2 - i * 0.25, 0, 0.55 - i * 1.15), obrot=(0, -57 + i * 8, 0)):
            _but(a, zn)
    return a


# --------------------------------------------------------------------------- Belt
def pas():
    """Sznurek z węzłem i skórzaną sakiewką. (0,0,0) = WaistCenterAttachment (środek LowerTorso 2×0,4×1).
    Przeszywanica sięga tu do z = ±0,58, x = ±0,98. Sakiewka stoi przed udem (z ≥ 0,72) — noga w chodzie (30°)
    sięga najwyżej z ≈ 0,62."""
    a = _akc("rekrut_pas", "Waist", ikona_obrot=(0, 64, 0))     # ikona: sakiewka zwrócona do kamery
    a.blok("Sznur przod", (0, 0.02, 0.64), (1.96, 0.16, 0.12), LINA, "matowy", faza=0.04)
    a.blok("Sznur tyl", (0, 0.02, -0.64), (1.96, 0.16, 0.12), LINA, "matowy", faza=0.04)
    for zn in (1, -1):                                         # boki pod rękami (na ciele ukryte, w ikonie domykają pętlę)
        a.blok("Sznur bok", (zn * 0.92, 0.02, 0), (0.12, 0.16, 1.2), LINA, "matowy", faza=0.04)
    for i in range(7):                                         # skręt sznura
        x = -0.84 + i * 0.28
        if abs(x - 0.42) < 0.2:
            continue
        a.blok("Skret", (x, 0.02, 0.71), (0.05, 0.19, 0.04), LINA_C, "matowy", rot=(0, 0, 35), faza=0.0)
    a.blok("Wezel", (0.42, 0.02, 0.76), (0.26, 0.24, 0.18), LINA, "matowy", faza=0.06)
    for i, (dx, kat, dl) in enumerate(((-0.06, -8, 0.42), (0.08, 12, 0.34))):
        a.blok("Koniec", (0.42 + dx, -0.12 - dl / 2, 0.78), (0.07, dl, 0.07), LINA, "matowy", rot=(0, 0, kat),
               faza=0.0)
    # sakiewka po prawej stronie noszącego (−X)
    a.blok("Sakiewka", (-0.55, -0.38, 0.92), (0.62, 0.56, 0.38), SKORA, "matowy", faza=0.1)   # z 0,73…1,11
    a.blok("Klapa", (-0.55, -0.15, 0.93), (0.66, 0.16, 0.42), SKORA_C, "matowy", faza=0.04)
    a.blok("Klapa jezyk", (-0.55, -0.28, 1.125), (0.24, 0.24, 0.05), SKORA_C, "matowy", faza=0.02)
    a.blok("Guzik", (-0.55, -0.36, 1.16), (0.1, 0.1, 0.05), BEZ, "matowy", faza=0.0)
    a.blok("Troczek", (-0.55, -0.02, 0.8), (0.08, 0.18, 0.08), LINA_C, "matowy", faza=0.0)
    return a


# --------------------------------------------------------------------------- Weapon
def miecz():
    """Drewniany miecz ćwiczebny: tępy, zaokrąglony sztych, prosty jelec z kołkiem, rękojeść owinięta rzemieniem.
    (0,0,0) = RightGripAttachment: rękojeść w (0,0,0), klinga w +Y, płaz do przodu (+Z)."""
    a = _akc("rekrut_miecz", "Bron", ikona_obrot=(0, 0, -45))
    a.blok("Rekojesc", (0, 0, 0), (0.24, 1.0, 0.24), SKORA_C, "matowy", faza=0.04)
    for y in (-0.3, 0.0, 0.3):
        a.blok("Owijka", (0, y, 0), (0.28, 0.07, 0.28), SKORA_J, "matowy", faza=0.0)
    a.blok("Glowica", (0, -0.64, 0), (0.42, 0.3, 0.42), DREWNO_C, "matowy", faza=0.1)
    a.blok("Jelec", (0, 0.66, 0), (1.25, 0.26, 0.34), DREWNO_C, "matowy", faza=0.08)
    for zn in (1, -1):
        a.blok("Kolek", (0, 0.66, zn * 0.18), (0.1, 0.1, 0.03), SKORA_C, "matowy", faza=0.0)
    a.blok("Klinga", (0, 1.85, 0), (0.6, 2.12, 0.22), DREWNO, "matowy", faza=0.06)        # y 0,79…2,91
    a.ostroslup("Sztych", (0, 3.07, 0), (0.6, 0.32, 0.22), DREWNO, "matowy", gora=(0.28, 0.22))
    for zn in (1, -1):                                          # słoje na obu płazach
        a.blok("Sloj", (0.12, 1.75, zn * 0.12), (0.045, 1.5, 0.04), DREWNO_SL, "matowy", faza=0.0)
        a.blok("Sloj krotki", (-0.13, 2.2, zn * 0.12), (0.045, 0.9, 0.04), DREWNO_SL, "matowy", faza=0.0)
    a.blok("Szczerba", (0.31, 2.3, 0), (0.04, 0.18, 0.16), DREWNO_C, "matowy", faza=0.0)
    return a


# --------------------------------------------------------------------------- Amulet / Ring / Trinket (do ikon)
def amulet():
    """Ząb na rzemyku — model do ikony (frontem do kamery). Zaczep nominalny: NeckAttachment."""
    a = _akc("rekrut_amulet", "Neck")
    g = 0.07
    pts = [(-0.55, 0.65), (0.55, 0.65), (0.6, 0.0), (0.12, -0.5), (-0.12, -0.5), (-0.6, 0.0)]
    _odcinek(a, "Rzemyk gora", pts[0], pts[1], g, g, SKORA_C)
    _odcinek(a, "Rzemyk L", pts[1], pts[2], g, g, SKORA_C)
    _odcinek(a, "Rzemyk L dol", pts[2], pts[3], g, g, SKORA_C)
    _odcinek(a, "Rzemyk P", pts[5], pts[0], g, g, SKORA_C)
    _odcinek(a, "Rzemyk P dol", pts[5], pts[4], g, g, SKORA_C)
    for x, y in ((0.58, 0.32), (-0.58, 0.32)):
        a.blok("Paciorek", (x, y, 0), (0.15, 0.15, 0.15), DREWNO, "matowy", faza=0.03)
    a.blok("Oplot", (0, -0.55, 0), (0.3, 0.14, 0.16), SKORA_C, "matowy", faza=0.03)
    a.stozek("Zab", (0, -0.86, 0), (0.3, 0.5, 0.2), ZAB, "polysk", rot=(0, 0, 168), segm=8)
    return a


def pierscien():
    """Miedziany pierścień z ciemnym oczkiem — model do ikony. Zaczep nominalny: RightGripAttachment."""
    a = _akc("rekrut_pierscien", "Inne")
    n, r = 8, 0.34
    pts = [(r * math.sin(2 * math.pi * (i + 0.5) / n), r * math.cos(2 * math.pi * (i + 0.5) / n)) for i in range(n)]
    for i in range(n):
        p1, p2 = pts[i], pts[(i + 1) % n]
        p1 = (p1[0] * 1.08, p1[1] * 1.08)
        p2 = (p2[0] * 1.08, p2[1] * 1.08)
        _odcinek(a, "Obraczka", p1, p2, 0.12, 0.2, MIEDZ, "metal", faza=0.02)
    a.blok("Oprawa", (0, 0.42, 0), (0.3, 0.14, 0.26), MIEDZ_C, "metal", faza=0.03)
    a.blok("Oczko", (0, 0.5, 0), (0.18, 0.08, 0.16), KAMIEN, "polysk", faza=0.03)
    return a


def podkowa():
    """Zardzewiała podkowa ramionami do góry — model do ikony. Zaczep nominalny: WaistCenterAttachment."""
    a = _akc("rekrut_podkowa", "Inne")
    # łuk podkowy z odcinków (środek łuku w (0, 0)), ramiona proste do góry
    r, n = 0.5, 6
    luk = [(r * math.cos(math.pi + math.pi * i / n), r * math.sin(math.pi + math.pi * i / n) * 1.1) for i in range(n + 1)]
    for i in range(n):
        _odcinek(a, "Luk", luk[i], luk[i + 1], 0.24, 0.12, RDZA, "metal", faza=0.025)
    for zn in (1, -1):
        a.blok("Ramie", (zn * r, 0.3, 0), (0.24, 0.62, 0.12), RDZA, "metal", faza=0.025)
        a.blok("Pietka", (zn * r, 0.64, 0), (0.3, 0.1, 0.14), RDZA_C, "metal", faza=0.02)
        for y in (0.1, 0.38):
            a.blok("Otwor", (zn * r, y, 0.065), (0.07, 0.1, 0.03), RDZA_C, "matowy", faza=0.0)
    for x, y, s in ((0.32, -0.38, 0.12), (-0.43, -0.12, 0.1), (0.5, 0.52, 0.09), (-0.2, -0.53, 0.08)):
        a.blok("Rdza", (x, y, 0.07), (s, s * 0.8, 0.03), RDZA_J, "matowy", faza=0.0)
    return a


# --------------------------------------------------------------------------- zestaw
def przedmioty():
    return [czapka(), przeszywanica(), przeszywanica_cala(), rekaw("l"), rekaw("p"), rekawica("l"), rekawica("p"), rekawice_para(), but("l"), but("p"),
            buty_para(), pas(), miecz(), amulet(), pierscien(), podkowa()]


SLABOSCI = [
    "Każdy przedmiot to sztywne akcesorium dopasowane do klockowego R15 biblioteki (5,25 studa).",
    "Lniane spodnie na przymiarce to tylko podgląd (część manekina przymiarki), nie przedmiot zestawu.",
    "Drobiazgi (amulet, pierścień, podkowa) to modele do ikon — nie są zakładane na przymiarkę.",
]


def zbuduj():
    from swiat.postacie.biblioteka.postac import przymiarka
    akc = przedmioty()
    m = przymiarka("zestaw_rekrut_przymiarka", [x for x in akc if _PO_ID[x.id]["noszony"]],
                   "Przymiarka zestawu Rekrut na manekinie R15")
    # proste lniane spodnie TYLKO na przymiarce (podgląd katalogu, nie przedmiot): szare uda wyglądały na niedokończone
    for s in ("Left", "Right"):
        m.klocek(s + "UpperLeg", "D8C8A0", "matowy", powieksz=(0.04, 0.0, 0.04), nazwa="Spodnie")
        m.klocek(s + "LowerLeg", "CDBC92", "matowy", powieksz=(0.04, 0.0, 0.04), nazwa="Nogawka")
    m.klocek("LowerTorso", "D8C8A0", "matowy", powieksz=(0.04, 0.0, 0.04), nazwa="Spodnie pas")
    return [m] + akc
