# -*- coding: utf-8 -*-
"""Wzorcowe postacie do tabeli balansu, testow i wzorcow zgodnosci.

Zasada rownosci (U10): na danym poziomie kazda klasa ma TE SAMA pule punktow statystyk, te sama bron, ten sam
pancerz z przedmiotow i tyle samo slotow umiejetnosci. Rozni sie tylko tym, jak rozklada punkty (styl klasy),
oraz cecha klasy (Wojownik nosi tarcze). Liczby sa robocze — to model do strojenia, nie kanon.
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
           pasywki=None, pet=None):
    """Wzorcowa postac klasy na poziomie. `dodatkowe` = {statystyka: punkty} dodane PONAD pule (test wrazliwosci)."""
    st = rozdziel(rozklad or ROZKLADY[klasa], pula(poziom))
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
        "umiejetnosci": UMIEJETNOSCI[klasa][:n],
    }
    if zaklecie:
        p["bron"]["zaklecie"] = zaklecie
    if klasa == "wojownik" and tarcza:
        p["tarcza"] = {"blok": BLOK_TARCZY}
    if pasywki:
        p["pasywki"] = pasywki
    if pet:
        p["pet"] = pet
    return p
