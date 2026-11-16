#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wzorce zgodnosci Luau-Python (silnik v3): dzienniki z portu w Pythonie dla ustalonego zestawu wejsc i ziaren.

    python -B tools/walka/wzorce.py            # zapisuje tools/walka/wzorce.json
    python -B tools/walka/wzorce.py --sprawdz  # sprawdza, czy wzorce.json zgadza sie z obecnym silnikiem

Plik wzorcow czyta tools/walka/zgodnosc_studio.py: liczy w Studio TE SAME walki modulami Luau i porownuje
podpisy. Podpis to napis z kazdym polem kazdego zdarzenia, wynikiem, liczba tur, lupem i czasem (format ponizej
musi byc identyczny w Luau — patrz funkcja podpis w zgodnosc_studio.py).
Po kazdej zmianie danych albo wzorow trzeba wzorce wygenerowac na nowo (test pilnuje, ze sa aktualne).
"""
import copy
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import silnik  # noqa: E402
import wzorcowe  # noqa: E402

PLIK = os.path.join(TU, "wzorce.json")
ZIARNA = [1, 2, 3, 77, 2026, 123456789]
POZIOMY = [1, 5, 10]


def setne(x):
    return int(math.floor(x * 100 + 0.5))


def podpis(w):
    czesci = []
    for z in w["dziennik"]:
        czesci.append("%s:%s>%s:%d/%d:%d/%d@%d+%d:%s:%s:%s:%d:%d:%d:%d:%d/%d" % (
            z["typ"], z["kto"], z["cel"], z["obrazenia"], z["pochloniete"], z["hp_gracz"], z["hp_wrog"],
            setne(z["t"]), setne(z["trwa"]), z["umiejetnosc"], z["efekt"], z["rodzaj"], 1 if z["krytyk"] else 0,
            z["wartosc"], z["tury"], z["stosy"], z["mana_gracz"], z["mana_wrog"]))
    L = w["lup"]
    return "%s|%s|%d|%d|%d/%d/%d/%d/%d/%s|%d|%d/%d|%d/%d" % (
        ",".join(czesci), w["wynik"], w["tury"], 1 if w["bezpiecznik"] else 0,
        L["zloto"], L["doswiadczenie"], L["tokeny_krainy"], L["gemy"], L["shard_ewolucji"], L["kraina"],
        setne(w["czas"]), w["strony"]["gracz"]["zycie"], w["strony"]["wrog"]["zycie"],
        w["strony"]["gracz"]["mana"], w["strony"]["wrog"]["mana"])


def skrot(napis):
    h = 7
    for b in napis.encode("utf-8"):
        h = (h * 131 + b) % 2147483647
    return h


def postacie_i_przeciwnicy():
    postacie, przeciwnicy, przypadki = [], [], []
    for L in POZIOMY:
        for k in wzorcowe.KLASY:
            postacie.append(wzorcowe.postac(k, L))
    # postacie z zakleciem broni, pasywkami, petem i bez umiejetnosci
    postacie.append(wzorcowe.postac("wojownik", 5, zaklecie="trucizna", pasywki={"sila": 0.05, "kondycja": 0.1},
                                    pet={"pancerz": 0.04}))
    postacie.append(wzorcowe.postac("mag", 5, zaklecie="podpalenie", pet={"inteligencja": 0.06}))
    postacie.append(wzorcowe.postac("zwiadowca", 5, ile_slotow=0, zaklecie="trucizna"))
    postacie.append(wzorcowe.postac("wojownik", 10, tarcza=False, ile_slotow=3, dodatkowe={"zrecznosc": 40}))
    # v3: pasywne umiejetnosci w slotach, premie z przedmiotow (mana), pasywki broni, 3 pasywne bez aktywnych
    postacie.append(wzorcowe.postac("mag", 5, umiejetnosci=["kula_ognia", "kumulowanie_trucizny"], zaklecie="trucizna",
                                    pasywka_broni="jadowity_kostur"))
    postacie.append(wzorcowe.postac("zwiadowca", 5, umiejetnosci=["zatruta_strzala", "skupienie"],
                                    premie={"zysk_many": 0.4, "koszt_many": 0.2, "mana_startowa": 30}))
    postacie.append(wzorcowe.postac("wojownik", 10, umiejetnosci=["kolos", "mur_tarczy", "rozdzieracz"],
                                    pasywka_broni="topor_rzeznika"))
    # wskrzeszenie (propozycja D-094): legendarna pasywka w slocie
    postacie.append(wzorcowe.postac("zwiadowca", 5, umiejetnosci=["uderzenie_z_gory", "wskrzeszenie"], zaklecie="trucizna"))
    postacie.append(wzorcowe.postac("wojownik", 10, umiejetnosci=["wskrzeszenie", "ciecie", "kolos"]))
    postacie.append(wzorcowe.postac("mag", 10, umiejetnosci=["bariera", "lodowy_pocisk", "przeplyw_many"],
                                    zaklecie="podpalenie", pasywka_broni="ognista_rozdzka",
                                    premie={"unik": 0.03, "blok": 0.02, "krytyk": 0.04, "pancerz": 0.1}))
    for L in POZIOMY:
        for p in silnik.PRZECIWNICY_LISTA:
            przeciwnicy.append({"potwor": p["id"], "poziom": L})
        for k in wzorcowe.KLASY:
            przeciwnicy.append({"postac": wzorcowe.postac(k, L)})
    na_poziom = len(silnik.PRZECIWNICY_LISTA) + len(wzorcowe.KLASY)
    for ip, p in enumerate(postacie[:9]):
        L = p["poziom"]
        baza = POZIOMY.index(L) * na_poziom
        for jp in range(baza, baza + na_poziom):
            for z in ZIARNA:
                przypadki.append([ip, jp, z])
    # postacie specjalne: z kazdym przeciwnikiem 5. poziomu, dwa ziarna
    baza5 = POZIOMY.index(5) * na_poziom
    for ip in range(9, len(postacie)):
        for jp in range(baza5, baza5 + na_poziom):
            for z in ZIARNA[:2]:
                przypadki.append([ip, jp, z])
    return postacie, przeciwnicy, przypadki


# Zle wejscia: baza (klasa wzorcowa na 5. poziomie przeciw Lesnemu Slime'owi 5. poziomu) + jedna zmiana.
# "wartosc" {"specjalna": "nan" | "inf" | "brak"} — NaN, nieskonczonosc albo usuniecie pola (JSON nie ma NaN).
ZLE_WEJSCIA = [
    {"opis": "nieznana klasa", "baza": "wojownik", "strona": "gracz", "sciezka": ["klasa"], "wartosc": "paladyn"},
    {"opis": "tarcza u Maga", "baza": "mag", "strona": "gracz", "sciezka": ["tarcza"], "wartosc": {"blok": 0.2}},
    {"opis": "tarcza u Zwiadowcy", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["tarcza"], "wartosc": {"blok": 0.2}},
    {"opis": "cztery sloty", "baza": "wojownik", "strona": "gracz", "sciezka": ["umiejetnosci"],
     "wartosc": ["ciecie", "miazdzacy_cios", "kamienna_skora", "ciecie"]},
    {"opis": "umiejetnosc innej klasy", "baza": "wojownik", "strona": "gracz", "sciezka": ["umiejetnosci"], "wartosc": ["kula_ognia"]},
    {"opis": "umiejetnosc potwora", "baza": "mag", "strona": "gracz", "sciezka": ["umiejetnosci"], "wartosc": ["uscisk_korzeni"]},
    {"opis": "ta sama umiejetnosc dwa razy", "baza": "mag", "strona": "gracz", "sciezka": ["umiejetnosci"],
     "wartosc": ["kula_ognia", "kula_ognia"]},
    {"opis": "nieznana umiejetnosc", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["umiejetnosci"], "wartosc": ["deszcz_strzal"]},
    {"opis": "ujemna Sila", "baza": "wojownik", "strona": "gracz", "sciezka": ["statystyki", "sila"], "wartosc": -5},
    {"opis": "Kondycja NaN", "baza": "wojownik", "strona": "gracz", "sciezka": ["statystyki", "kondycja"], "wartosc": {"specjalna": "nan"}},
    {"opis": "Szczescie nieskonczone", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["statystyki", "szczescie"], "wartosc": {"specjalna": "inf"}},
    {"opis": "brak Zrecznosci", "baza": "mag", "strona": "gracz", "sciezka": ["statystyki", "zrecznosc"], "wartosc": {"specjalna": "brak"}},
    {"opis": "Zrecznosc jako napis", "baza": "mag", "strona": "gracz", "sciezka": ["statystyki", "zrecznosc"], "wartosc": "10"},
    {"opis": "nieznana statystyka", "baza": "wojownik", "strona": "gracz", "sciezka": ["statystyki", "szybkosc"], "wartosc": 5},
    {"opis": "bron bez obrazen", "baza": "wojownik", "strona": "gracz", "sciezka": ["bron", "obrazenia"], "wartosc": 0},
    {"opis": "nieznane zaklecie", "baza": "mag", "strona": "gracz", "sciezka": ["bron", "zaklecie"], "wartosc": "lod"},
    {"opis": "poziom 0", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["poziom"], "wartosc": 0},
    {"opis": "poziom ulamkowy", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["poziom"], "wartosc": 2.5},
    {"opis": "ujemny pancerz przedmiotow", "baza": "wojownik", "strona": "gracz", "sciezka": ["pancerz_przedmiotow"], "wartosc": -1},
    {"opis": "ujemna pasywka", "baza": "wojownik", "strona": "gracz", "sciezka": ["pasywki"], "wartosc": {"sila": -0.1}},
    {"opis": "pet z nieznana statystyka", "baza": "mag", "strona": "gracz", "sciezka": ["pet"], "wartosc": {"magia": 0.1}},
    {"opis": "tarcza z za duzym blokiem", "baza": "wojownik", "strona": "gracz", "sciezka": ["tarcza", "blok"], "wartosc": 0.9},
    {"opis": "brak gracza", "baza": "wojownik", "strona": "gracz", "sciezka": [], "wartosc": {"specjalna": "brak"}},
    {"opis": "nieznany potwor", "baza": "wojownik", "strona": "przeciwnik", "sciezka": ["potwor"], "wartosc": "smok"},
    {"opis": "potwor poziomu 0", "baza": "wojownik", "strona": "przeciwnik", "sciezka": ["poziom"], "wartosc": 0},
    {"opis": "potwor i postac naraz", "baza": "wojownik", "strona": "przeciwnik", "sciezka": ["postac"], "wartosc": "WZORCOWY_MAG"},
    {"opis": "przeciwnik bez potwora i postaci", "baza": "wojownik", "strona": "przeciwnik", "sciezka": ["potwor"],
     "wartosc": {"specjalna": "brak"}},
    {"opis": "postac-przeciwnik: Mag z tarcza", "baza": "wojownik", "strona": "przeciwnik", "sciezka": [],
     "wartosc": "MAG_Z_TARCZA_JAKO_PRZECIWNIK"},
    {"opis": "ziarno NaN", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": {"specjalna": "nan"}},
    {"opis": "ziarno nieskonczone", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": {"specjalna": "inf"}},
    {"opis": "ziarno jako napis", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": "abc"},
    # ziarna, przy ktorych Luau (double) i Python (dokladne int) liczylyby inny stan generatora albo ktore nie sa
    # liczba calkowita z [0, 2^31) — oba porty maja je odrzucic tym samym bledem
    {"opis": "ziarno 1e20", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": 1e20},
    {"opis": "ziarno 2^31", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": 2147483648},
    {"opis": "ziarno ulamkowe", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": 2.5},
    {"opis": "ziarno ujemne", "baza": "wojownik", "strona": "ziarno", "sciezka": [], "wartosc": -7},
    # umiejetnosci jako tabela z kluczami-napisami zamiast listy (w Luau #um == 0 — dawniej przechodzilo walidacje)
    {"opis": "umiejetnosci jako slownik z umiejetnoscia innej klasy", "baza": "wojownik", "strona": "gracz",
     "sciezka": ["umiejetnosci"], "wartosc": {"x": "kula_ognia"}},
    {"opis": "umiejetnosci jako slownik z nieznana umiejetnoscia", "baza": "wojownik", "strona": "gracz",
     "sciezka": ["umiejetnosci"], "wartosc": {"x": "nieznana"}},
    {"opis": "umiejetnosci z dziura (klucze 1 i 3)", "baza": "mag", "strona": "gracz",
     "sciezka": ["umiejetnosci"], "wartosc": "UMIEJETNOSCI_Z_DZIURA"},
    # v3: pasywki w slotach, premie (modyfikatory z przedmiotow i drzewka), pasywki broni
    {"opis": "pasywka innej klasy w slocie", "baza": "wojownik", "strona": "gracz", "sciezka": ["umiejetnosci"],
     "wartosc": ["ciecie", "kumulowanie_trucizny"]},
    {"opis": "ta sama pasywka dwa razy", "baza": "mag", "strona": "gracz", "sciezka": ["umiejetnosci"],
     "wartosc": ["przeplyw_many", "przeplyw_many"]},
    {"opis": "cztery sloty z pasywkami", "baza": "mag", "strona": "gracz", "sciezka": ["umiejetnosci"],
     "wartosc": ["kula_ognia", "przeplyw_many", "skupiona_magia", "kumulowanie_trucizny"]},
    {"opis": "premie jako liczba", "baza": "wojownik", "strona": "gracz", "sciezka": ["premie"], "wartosc": 5},
    {"opis": "premie: nieznany modyfikator", "baza": "wojownik", "strona": "gracz", "sciezka": ["premie"],
     "wartosc": {"mana": 0.2}},
    {"opis": "premie: zysk many za duzy", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["premie"],
     "wartosc": {"zysk_many": 50}},
    {"opis": "premie: ujemna znizka kosztu", "baza": "mag", "strona": "gracz", "sciezka": ["premie"],
     "wartosc": {"koszt_many": -0.2}},
    {"opis": "premie: unik jako napis", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["premie"],
     "wartosc": {"unik": "0.1"}},
    {"opis": "nieznana pasywka broni", "baza": "mag", "strona": "gracz", "sciezka": ["bron", "pasywka"],
     "wartosc": "miecz_swietlny"},
    {"opis": "pasywka broni innej klasy", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["bron", "pasywka"],
     "wartosc": "ognista_rozdzka"},
    {"opis": "pasywka broni jako liczba", "baza": "wojownik", "strona": "gracz", "sciezka": ["bron", "pasywka"], "wartosc": 3},
    {"opis": "wskrzeszenie jako premia (tylko slot)", "baza": "mag", "strona": "gracz", "sciezka": ["premie"],
     "wartosc": {"wskrzeszenie": 0.25}},
    {"opis": "wskrzeszenie jako pasywka broni", "baza": "wojownik", "strona": "gracz", "sciezka": ["bron", "pasywka"],
     "wartosc": "wskrzeszenie"},
    {"opis": "wskrzeszenie dwa razy w slotach", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["umiejetnosci"],
     "wartosc": ["wskrzeszenie", "wskrzeszenie"]},
    # kontrola 16/17.11: zamkniete listy pol — literowka nie moze przejsc po cichu (dawniej silnik ja pomijal)
    {"opis": "literowka: premia zamiast premie", "baza": "wojownik", "strona": "gracz", "sciezka": ["premia"],
     "wartosc": {"cios": 0.5}},
    {"opis": "mana jako pole postaci", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["mana"], "wartosc": 100},
    {"opis": "nieznane pole broni (pasywki zamiast pasywka)", "baza": "mag", "strona": "gracz", "sciezka": ["bron", "pasywki"],
     "wartosc": "kostur_many"},
    {"opis": "nieznane pole tarczy", "baza": "wojownik", "strona": "gracz", "sciezka": ["tarcza", "pancerz"], "wartosc": 5},
    {"opis": "nieznane pole przeciwnika (premie potwora)", "baza": "wojownik", "strona": "przeciwnik", "sciezka": ["premie"],
     "wartosc": {"cios": 0.5}},
    {"opis": "premie: NaN", "baza": "mag", "strona": "gracz", "sciezka": ["premie"], "wartosc": {"specjalna": "nan_w_premii"}},
    {"opis": "umiejetnosci jako liczba", "baza": "mag", "strona": "gracz", "sciezka": ["umiejetnosci"], "wartosc": 3},
    {"opis": "nazwa jako liczba", "baza": "zwiadowca", "strona": "gracz", "sciezka": ["nazwa"], "wartosc": 7},
]


def rozwin_wartosc(v):
    """Zamienia znaczniki z ZLE_WEJSCIA na prawdziwe wartosci (to samo robi kod Luau w zgodnosc_studio.py)."""
    if v == "WZORCOWY_MAG":
        return wzorcowe.postac("mag", 5)
    if v == "MAG_Z_TARCZA_JAKO_PRZECIWNIK":
        mag = wzorcowe.postac("mag", 5)
        mag["tarcza"] = {"blok": 0.2}
        return {"postac": mag}
    if v == "UMIEJETNOSCI_Z_DZIURA":
        # w Luau: { [1] = "kula_ognia", [3] = "bariera" } (JSON nie zapisze kluczy liczbowych, stad znacznik)
        return {1: "kula_ognia", 3: "bariera"}
    return copy.deepcopy(v)


def zle_wejscie(spec):
    """-> (gracz, przeciwnik, ziarno) dla jednego zlego wejscia. BRAK = usuniete pole."""
    gracz = wzorcowe.postac(spec["baza"], 5)
    przeciwnik = {"potwor": "lesny_slime", "poziom": 5}
    ziarno = 1
    v = spec["wartosc"]
    specjalna = v.get("specjalna") if isinstance(v, dict) else None
    if specjalna == "nan":
        v = float("nan")
    elif specjalna == "nan_w_premii":
        v = {"cios": float("nan")}
    elif specjalna == "inf":
        v = float("inf")
    elif specjalna != "brak":
        v = rozwin_wartosc(v)
    if spec["strona"] == "ziarno":
        return gracz, przeciwnik, v
    korzen = {"gracz": gracz, "przeciwnik": przeciwnik}
    if not spec["sciezka"]:
        korzen[spec["strona"]] = None if specjalna == "brak" else v
    else:
        cel = korzen[spec["strona"]]
        for k in spec["sciezka"][:-1]:
            cel = cel[k]
        if specjalna == "brak":
            cel.pop(spec["sciezka"][-1], None)
        else:
            cel[spec["sciezka"][-1]] = v
    return korzen["gracz"], korzen["przeciwnik"], ziarno


def zbuduj():
    postacie, przeciwnicy, przypadki = postacie_i_przeciwnicy()
    podpisy = []
    for ip, jp, z in przypadki:
        w = silnik.symuluj(postacie[ip], przeciwnicy[jp], z)
        podpisy.append(podpis(w))
    return {
        "_opis": "Wzorce zgodnosci silnika walki v3: wejscia, ziarna i podpisy dziennikow z portu w Pythonie. "
                 "Generuje: python -B tools/walka/wzorce.py. Sprawdza w Studio: python -B tools/walka/zgodnosc_studio.py (bez Studio: --offline).",
        "wzorcowa_mag": wzorcowe.postac("mag", 5),
        "postacie": postacie,
        "przeciwnicy": przeciwnicy,
        "przypadki": przypadki,
        "podpisy": podpisy,
        "skroty": [skrot(p) for p in podpisy],
        "zle_wejscia": ZLE_WEJSCIA,
        "bazy_zlych": {k: wzorcowe.postac(k, 5) for k in wzorcowe.KLASY},
    }


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    dane = zbuduj()
    tekst = json.dumps(dane, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if "--sprawdz" in sys.argv:
        try:
            with open(PLIK, encoding="utf-8") as f:
                stary = f.read()
        except OSError:
            stary = None
        if stary != tekst:
            print("wzorce.json NIEAKTUALNE — uruchom: python -B tools/walka/wzorce.py")
            sys.exit(1)
        print("wzorce.json aktualne (%d przypadkow)" % len(dane["przypadki"]))
        return
    with open(PLIK, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    print("zapisano %d przypadkow do %s" % (len(dane["przypadki"]), os.path.relpath(PLIK, os.path.dirname(os.path.dirname(TU)))))


if __name__ == "__main__":
    main()
