# -*- coding: utf-8 -*-
"""Wzorcowe postacie i buildy do tabeli balansu, testow, wzorcow zgodnosci i modelu tempa.

Zasada rownosci (U10): na danym poziomie kazda klasa ma TE SAMA pule punktow statystyk, te sama bron, ten sam
pancerz z przedmiotow i tyle samo slotow umiejetnosci. Rozni sie tylko tym, jak rozklada punkty (styl klasy),
oraz cecha klasy (Wojownik nosi tarcze). Liczby sa robocze — to model do strojenia, nie kanon.

Postac wzorcowa (funkcja postac bez dodatkowych argumentow) jest TA SAMA co w silniku v2 — prototyp w Studio
(swiat/test_walki2/zrodla/Wzorcowe.luau) buduje ja tak samo, wiec nie wymaga zmian. Nowe rzeczy z sesji 16.11
(premie z przedmiotow, pasywki broni, pasywne umiejetnosci w slotach, buildy) sa dodatkowymi argumentami.
"""

PUNKTY_START = 30       # pula punktow statystyk na 1. poziomie
PUNKTY_NA_POZIOM = 10   # tyle punktow daje kazdy kolejny poziom (D-057: poziom daje punkty statystyk)
BLOK_TARCZY = 0.2828       # stala szansa bloku zwyklej tarczy (cecha przedmiotu, D-062)

# styl klasy = rozklad puli (udzialy sumuja sie do 1); kolejnosc statystyk jak w dane_walki.json
ROZKLADY = {
    "wojownik": {"sila": 0.26, "kondycja": 0.30, "inteligencja": 0.12, "zrecznosc": 0.08, "szczescie": 0.10, "pancerz": 0.14},
    "zwiadowca": {"sila": 0.27, "kondycja": 0.27, "inteligencja": 0.10, "zrecznosc": 0.14, "szczescie": 0.13, "pancerz": 0.09},
    "mag": {"sila": 0.24, "kondycja": 0.22, "inteligencja": 0.24, "zrecznosc": 0.10, "szczescie": 0.10, "pancerz": 0.10},
}
STATYSTYKI = ["sila", "kondycja", "inteligencja", "zrecznosc", "szczescie", "pancerz"]
KLASY = ["wojownik", "zwiadowca", "mag"]
UMIEJETNOSCI = {
    "wojownik": ["ciecie", "miazdzacy_cios", "kamienna_skora"],
    "zwiadowca": ["uderzenie_z_gory", "zatruta_strzala", "skupienie"],
    "mag": ["kula_ognia", "lodowy_pocisk", "bariera"],
}


def pula(poziom):
    return PUNKTY_START + PUNKTY_NA_POZIOM * (poziom - 1)


def sloty(poziom):
    # robocze zalozenie do balansu: drzewko odblokowuje 1 slot od razu, 2 od 5. poziomu, 3 od 10. (D-055: 0-3)
    if poziom >= 10:
        return 3
    if poziom >= 5:
        return 2
    return 1


def rozdziel(rozklad, punkty):
    """Udzialy -> calkowite punkty o sumie dokladnie `punkty` metoda najwiekszych reszt: brakujace punkty dostaja
    statystyki z najwieksza czescia ulamkowa. Dzieki temu zaokraglenie nie zabiera klasie np. Kondycji na jednym
    poziomie i nie oddaje jej na nastepnym (przy malej puli to dawalo skoki o kilka punktow procentowych)."""
    dokladne = {s: rozklad[s] * punkty for s in STATYSTYKI}
    st = {s: int(dokladne[s] + 1e-9) for s in STATYSTYKI}
    reszta = punkty - sum(st.values())
    kolejnosc = sorted(STATYSTYKI, key=lambda s: (-(dokladne[s] - st[s]), -rozklad[s], STATYSTYKI.index(s)))
    i = 0
    while reszta > 0:
        st[kolejnosc[i % len(kolejnosc)]] += 1
        reszta -= 1
        i += 1
    return st


def bron(poziom):
    return 8 + 4 * poziom


def pancerz_przedmiotow(poziom):
    return 3 + 1.5 * poziom


def postac(klasa, poziom, rozklad=None, ile_slotow=None, zaklecie=None, tarcza=True, dodatkowe=None,
           pasywki=None, pet=None, umiejetnosci=None, premie=None, pasywka_broni=None, blok_tarczy=None,
           punkty=None):
    """Wzorcowa postac klasy na poziomie. `dodatkowe` = {statystyka: punkty} dodane PONAD pule (test wrazliwosci);
    `umiejetnosci` = wlasna lista slotow (aktywne i pasywne); `premie` = modyfikatory z przedmiotow i drzewka;
    `punkty` = wlasna pula zamiast pula(poziom) (model tempa: punkty z poziomu + z treningu)."""
    st = rozdziel(rozklad or ROZKLADY[klasa], pula(poziom) if punkty is None else punkty)
    for s, v in (dodatkowe or {}).items():
        st[s] += v
    n = sloty(poziom) if ile_slotow is None else ile_slotow
    p = {
        "nazwa": klasa.capitalize(),
        "klasa": klasa,
        "poziom": poziom,
        "statystyki": st,
        "bron": {"obrazenia": bron(poziom)},
        "pancerz_przedmiotow": pancerz_przedmiotow(poziom),
        "umiejetnosci": list(umiejetnosci) if umiejetnosci is not None else UMIEJETNOSCI[klasa][:n],
    }
    if zaklecie:
        p["bron"]["zaklecie"] = zaklecie
    if pasywka_broni:
        p["bron"]["pasywka"] = pasywka_broni
    if klasa == "wojownik" and tarcza:
        p["tarcza"] = {"blok": BLOK_TARCZY if blok_tarczy is None else blok_tarczy}
    if pasywki:
        p["pasywki"] = pasywki
    if pet:
        p["pet"] = pet
    if premie:
        p["premie"] = premie
    return p


# ------------------------------------------------------------------------------------------------ buildy (C)
# Build = rozklad punktow + sloty (aktywne/pasywne) + premie z przedmiotow (amulet, pierscien, zbroja) + bron
# (zaklecie, pasywka). Kazdy build PLACI za swoja specjalnosc:
# - premie i zaklecie z przedmiotow sa „zamiast” zwyklych przedmiotow ze statystykami, ktore ma postac wzorcowa —
#   model: build z premiami oddaje KOSZT_PREMII puli punktow (to zalozenie modelu, nie zasada silnika);
# - pasywki broni maja wade (np. mocny zwykly cios, ale wolniejsza mana);
# - pasywka w slocie zajmuje miejsce umiejetnosci aktywnej;
# - przesuniecie rozkladu bierze punkty z innych statystyk.
KOSZT_PREMII = 0.10
# build pod mane: ile puli oddaje za przedmioty many — strojone tak, zeby byl rowny wzorcowej swojej klasy
# (szybsza mana jest warta duzo: umiejetnosc jest mocniejsza od zwyklego ciosu)
# Kontrola 16/17.11: pasywki many w slocie (Bitewny rytm, Przyplyw adrenaliny, Przeplyw many) byly za mocne jak na
# DARMOWY wybor slotu (zestaw „1-2 aktywne + pasywka many” wygrywal z wzorcowa 63-67%), wiec w danych oslabione
# z +0,30/0,35 zysku i +35 many na start do +0,10 i +15. Zeby build pod mane mial tyle many co przedtem, czesc many
# przeszla z pasywki do przedmiotow modelu (PREMIE_MANY: zysk 0,35 -> 0,60, start 50 -> 70), za ktore build placi pula.
KOSZT_MANY = {"wojownik": 0.225, "zwiadowca": 0.20, "mag": 0.26}
BRON_MANY = {"wojownik": "miecz_runiczny", "zwiadowca": "luk_runiczny", "mag": "kostur_many"}
BRON_CIEZKA = {"wojownik": "topor_rzeznika", "zwiadowca": "luk_mysliwego", "mag": "ciezka_rozdzka"}
PASYWKA_MANY = {"wojownik": "bitewny_rytm", "zwiadowca": "przyplyw_adrenaliny", "mag": "przeplyw_many"}
PASYWKA_CIOSU = {"wojownik": "furia", "zwiadowca": "seria", "mag": "magiczny_pocisk"}
PREMIE_MANY = {"zysk_many": 0.6, "koszt_many": 0.15, "mana_startowa": 70}


def przesun(rozklad, zmiany):
    """Nowy rozklad: zmiany = {statystyka: +/- udzial}; suma zmian = 0, zaden udzial ponizej 0."""
    r = dict(rozklad)
    for s, v in zmiany.items():
        r[s] = r[s] + v
    assert abs(sum(r.values()) - 1) < 1e-9 and min(r.values()) >= 0, r
    return r


def _sloty(poziom, kolejnosc):
    return kolejnosc[:sloty(poziom)]


def build(nazwa, klasa, poziom):
    """Postac z buildem `nazwa` (klucze BUILDY_KLAS) klasy na poziomie. None = build nie dotyczy tej klasy."""
    pula_ = pula(poziom)
    akt = UMIEJETNOSCI[klasa]
    if nazwa == "wzorcowa":
        return postac(klasa, poziom)
    if nazwa == "mana":
        # szybsza mana z przedmiotow (amulet i pierscien many), bron many, pasywka many w ostatnim slocie (od 2 slotow)
        um = _sloty(poziom, [akt[0], PASYWKA_MANY[klasa], akt[1]])
        return postac(klasa, poziom, umiejetnosci=um, premie=dict(PREMIE_MANY), pasywka_broni=BRON_MANY[klasa],
                      punkty=round(pula_ * (1 - KOSZT_MANY[klasa])))
    if nazwa == "zwykle":
        # zwykle ciosy: ciezka bron (mocny cios, wolniejsza mana), pasywka ciosu w drugim slocie,
        # wiecej Sily i Szczescia kosztem Inteligencji (umiejetnosci uzywa rzadko)
        r = przesun(ROZKLADY[klasa], {"sila": 0.05, "szczescie": 0.03, "inteligencja": -0.08})
        um = _sloty(poziom, [akt[0], PASYWKA_CIOSU[klasa], akt[1]])
        return postac(klasa, poziom, rozklad=r, umiejetnosci=um, pasywka_broni=BRON_CIEZKA[klasa])
    if nazwa == "unik" and klasa == "zwiadowca":
        r = przesun(ROZKLADY[klasa], {"zrecznosc": 0.14, "sila": -0.05, "kondycja": -0.05, "inteligencja": -0.04})
        um = _sloty(poziom, [akt[0], "zwinnosc", akt[2]])
        return postac(klasa, poziom, rozklad=r, umiejetnosci=um, pasywka_broni="luk_wiatru")
    if nazwa == "pancerz" and klasa == "wojownik":
        r = przesun(ROZKLADY[klasa], {"pancerz": 0.12, "kondycja": 0.04, "sila": -0.08, "szczescie": -0.04,
                                      "zrecznosc": -0.04})
        um = _sloty(poziom, [akt[0], "mur_tarczy", akt[2]])
        return postac(klasa, poziom, rozklad=r, umiejetnosci=um)
    if nazwa == "trucizna" and klasa == "mag":
        # kumulowanie trucizny (Pawel): zaklecie trucizny + jadowity kostur + pasywka kumulowania
        um = _sloty(poziom, [akt[0], "kumulowanie_trucizny", akt[1]])
        return postac(klasa, poziom, umiejetnosci=um, zaklecie="trucizna", pasywka_broni="jadowity_kostur",
                      punkty=round(pula_ * (1 - KOSZT_PREMII)))
    return None


BUILDY_KLAS = {"wojownik": ["mana", "zwykle", "pancerz"], "zwiadowca": ["mana", "zwykle", "unik"],
               "mag": ["mana", "zwykle", "trucizna"]}
NAZWY_BUILDOW = {"wzorcowa": "wzorcowa", "mana": "pod manę", "zwykle": "pod zwykłe ataki", "unik": "pod unik",
                 "pancerz": "pod Pancerz i blok", "trucizna": "pod truciznę"}
