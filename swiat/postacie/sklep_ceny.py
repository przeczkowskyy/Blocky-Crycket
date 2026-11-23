#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kalkulator sklepu z przedmiotami (D-106): ceny, wymagane poziomy i statystyki przedmiotów trzech klas w czterech
stopniach (startowy, lasu, Bagna, Dżungli). PROPOZYCJA liczb do oceny, nie kanon.

    python -B swiat/postacie/sklep_ceny.py             # liczy i zapisuje sklep_liczby.json (obok tego pliku)
    python -B swiat/postacie/sklep_ceny.py --sprawdz   # kod 1, gdy plik jest nieaktualny albo katalog niespójny
    python -B swiat/postacie/sklep_ceny.py --md        # rachunek w Markdownie na ekran (źródła liczb i wynik)
    python -B swiat/postacie/sklep_ceny.py --md --z-pliku   # ten sam rachunek z zapisanego pliku (bez liczenia)
    python -B swiat/postacie/sklep_ceny.py --spojnosc  # tylko spójność zapisanego pliku (szybko, bez modułów gry)

Uwaga: liczby źródłowe są czytane z plików gry w chwili uruchomienia. Gdy ktoś zmieni przegrody, łup albo czasy
odrodzenia potworów (np. prace nad D-107), --sprawdz zgłosi plik jako nieaktualny — wtedy przelicz i obejrzyj ceny.

Skąd liczby (wszystko tylko czytane, w czystym Pythonie, jeden proces, kilkanaście sekund):
  przegrody i poziomy potworów   swiat/las_pas_gra, bagno_pas_gra, dzungla_pas_gra (zrodla/DanePotworow*.luau);
  łup Złota potworów             tools/walka/dane_walki.json i przeciwnicy.py Bagna i Dżungli (w pamięci silnika);
  walki                          tools/walka/silnik.py (prawdziwy silnik), bohater i modyfikatory z swiat/stan_gracza
                                 (opis_bohatera, czysty_modyfikator, opis_z_modyfikatorami — jak Sygnaly/Bohater);
  gracz w krainie                polityka jak swiat/stan_gracza/symulacja_lasu.py i swiat/kowal_proba/balans_kowala.py
                                 (idzie dalej, gdy ma poziom przegrody; po dwóch przegranych wraca; Strażnik na końcu);
  przedmioty startowe            swiat/kowal_proba/ustawienia.json (baza, krok, podstawowy, waga, koszty ulepszeń)
                                 i swiat/postacie/przedmioty.json (slot, klasa);
  ceny jajek                     swiat/pety_proba/ustawienia.json (D-105).

Co jest przyjęte ręcznie (stałe niżej, opisane w rachunku --md jako wybory do oceny): jaka część Złota krainy idzie
na sklep (UDZIAL_SKLEPU), podział ceny kompletu na sloty (UDZIAL_SLOTU), wymagane poziomy (POZIOM_SLOTU, od
najniższego poziomu potworów krainy), rodzaje statystyk w slocie (PRZEPIS — te same co u kowala) i ich wielkość
w stopniu (MNOZNIK — dobrana tak, żeby komplet stopnia dawał w swojej krainie ok. 70% wygranych zamiast ok. 50%).

Identyfikatory: stopień startowy <prefiks>_<rzecz> (dzisiejsze przedmioty), kupowane <prefiks>_<stopień>_<rzecz>.
Ciężkie moduły gry wczytują się dopiero przy liczeniu (funkcja gra()), a wynik jest zwykłym plikiem JSON — kto chce
tylko dane, czyta sklep_liczby.json.
"""
import argparse
import json
import os
import random
import statistics
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PLIK = os.path.join(TU, "sklep_liczby.json")
PLIK_KOWALA = os.path.join(REPO, "swiat", "kowal_proba", "ustawienia.json")
PLIK_KATALOGU = os.path.join(TU, "przedmioty.json")
PLIK_PETOW = os.path.join(REPO, "swiat", "pety_proba", "ustawienia.json")

# ------------------------------------------------------------------------------------------------ układ katalogu
KLASY = (("wojownik", "rycerz", "Wojownik"), ("zwiadowca", "zwiadowca", "Zwiadowca"), ("mag", "kot_mag", "Mag"))
# slot -> nazwa rzeczy w identyfikatorze (kolejność = kolejność w tabelach)
RZECZY = {
    "wojownik": (("Helmet", "helm"), ("Chest", "zbroja"), ("Belt", "pas"), ("Gloves", "rekawice"), ("Boots", "buty"),
                 ("Weapon", "miecz"), ("OffHand", "tarcza")),
    "zwiadowca": (("Helmet", "kaptur"), ("Chest", "kurtka"), ("Belt", "pas"), ("Gloves", "rekawice"),
                  ("Boots", "buty"), ("Weapon", "sztylet"), ("OffHand", "luk")),
    "mag": (("Helmet", "kapelusz"), ("Chest", "szata"), ("Belt", "pas"), ("Weapon", "kostur")),
}
SLOTY_PL = {"Helmet": "nakrycie głowy", "Chest": "tors (z nogami)", "Belt": "pas", "Gloves": "rękawice",
            "Boots": "buty", "Weapon": "broń", "OffHand": "druga ręka"}
STOPNIE = (("start", 0, "Startowy", None), ("las", 1, "Leśny", "las"), ("bagno", 2, "Bagienny", "bagno"),
           ("dzungla", 3, "Dżungli", "dzungla"))
KRAINY = ("las", "bagno", "dzungla")
KRAINY_PL = {"las": "Las", "bagno": "Bagno", "dzungla": "Dżungla"}
STATYSTYKI_PL = {"bron": "Broń", "pancerz": "Pancerz", "tarcza": "Blok", "Strength": "Siła",
                 "Constitution": "Kondycja", "Intelligence": "Inteligencja", "Dexterity": "Zręczność",
                 "Luck": "Szczęście"}

# ------------------------------------------------------------------------------------------------ wybory do oceny
# Część Złota z walk w krainie (do wygranej ze Strażnikiem, mediana graczy), którą kosztuje komplet stopnia tej krainy.
# Reszta zostaje na jajka (D-105) i ulepszenia u kowala; przy połowie Złota odkładanej na sklep komplet jest gotowy
# po ok. 80% drogi do Strażnika, czyli przydaje się jeszcze w tej samej krainie.
UDZIAL_SKLEPU = 0.4
# Część Złota z wygranych, którą gracz w symulacji „ze sklepem” odkłada na sklep (jak wariant „połowa Złota” kowala).
UDZIAL_SAKIEWKI = 0.5
ZAOKRAGLENIE_KOMPLETU = 100
ZAOKRAGLENIE_CENY = 50
# Podział ceny kompletu na sloty (suma = 1 w każdej klasie). Mag ma cztery przedmioty, więc każdy jest droższy;
# komplet każdej klasy kosztuje tyle samo.
UDZIAL_SLOTU = {
    "wojownik": {"Weapon": 0.24, "Chest": 0.24, "Helmet": 0.14, "OffHand": 0.14, "Gloves": 0.08, "Boots": 0.08,
                 "Belt": 0.08},
    "zwiadowca": {"Weapon": 0.24, "Chest": 0.24, "Helmet": 0.14, "OffHand": 0.14, "Gloves": 0.08, "Boots": 0.08,
                  "Belt": 0.08},
    "mag": {"Weapon": 0.34, "Chest": 0.30, "Helmet": 0.20, "Belt": 0.16},
}
# Przedmioty startowe spoza zestawu podstawowego (dziś tylko z łupu): komplet brakujących sztuk kosztuje tyle Złota,
# ile daje WYGRANYCH_NA_START wygranych w pierwszej przegrodzie lasu — po równo na sztukę, tak samo dla każdej klasy.
WYGRANYCH_NA_START = 8
ZAOKRAGLENIE_STARTU = 5
# Wymagany poziom = najniższy poziom potworów krainy + przesunięcie slotu (tańsze sloty wcześniej, broń na końcu).
# Stopień lasu zaczyna się od 2. poziomu (na 1. gracz ma dopiero zestaw podstawowy i pierwszą walkę).
POZIOM_STARTU_LASU = 2
PRZESUNIECIE_SLOTU = {"Belt": 0, "Gloves": 1, "Boots": 2, "Helmet": 3, "OffHand": 3, "Chest": 4, "Weapon": 5}
# Rodzaje statystyk w slocie — te same co u kowala (swiat/kowal_proba/ustawienia.json); liczba = jednostki na 1,0
# mnożnika stopnia. Blok tarczy nie rośnie z mnożnikiem: +2 pp na stopień.
PRZEPIS = {
    "wojownik": {"Weapon": {"bron": 2}, "Chest": {"pancerz": 4}, "OffHand": {"Constitution": 1},
                 "Helmet": {"pancerz": 2, "Constitution": 2}, "Gloves": {"Strength": 3}, "Boots": {"Dexterity": 3},
                 "Belt": {"Constitution": 2}},
    "zwiadowca": {"Weapon": {"bron": 2}, "Chest": {"pancerz": 4}, "OffHand": {"bron": 2, "Luck": 2},
                  "Helmet": {"pancerz": 2, "Dexterity": 3}, "Gloves": {"Strength": 3}, "Boots": {"Dexterity": 3},
                  "Belt": {"Constitution": 2}},
    "mag": {"Weapon": {"bron": 2, "Intelligence": 2}, "Chest": {"pancerz": 5, "Constitution": 2},
            "Helmet": {"Constitution": 2, "Intelligence": 3}, "Belt": {"Constitution": 2, "Strength": 2}},
}
# Dobór przepisów: przy tych liczbach komplet stopnia daje trzem klasom w swojej krainie szanse różne najwyżej
# o kilka punktów procentowych (rachunek --md, tabela 5). Mag ma cztery przedmioty — każdy niesie dwie statystyki.
BLOK_TARCZY_NA_STOPIEN = 0.02
MNOZNIK = {"las": 1.0, "bagno": 2.0, "dzungla": 3.0}
# Przyrost za poziom ulepszenia: stopień lasu jak przedmiot startowy tego slotu (kowal), wyższe stopnie — przyrost
# broni i statystyk × numer stopnia, pancerz +1 na stopień; blok tarczy zawsze +1 pp.
KROK_PANCERZA_NA_STOPIEN = 1

# ------------------------------------------------------------------------------------------------ symulacja
GRACZY = 60            # graczy na klasę (tor: las → Bagno → Dżungla)
WALK = 300             # walk na komórkę tabeli szans
ZIARNO = 1
WIZYTA_S = 40.0        # s: Kamień Powrotu → bazar → sklep → powrót (jak wizyta u kowala w balans_kowala.py)
WIZYTA_CO_S = 300.0    # najwyżej jedna wizyta w sklepie na 5 minut gry
_GRA = {}


def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def gra():
    """Moduły gry (tylko odczyt) i dane: silnik walki, logika stanu gracza, przegrody trzech krain."""
    if _GRA:
        return _GRA
    for s in (os.path.join(REPO, "swiat", "pety_proba"), os.path.join(REPO, "swiat", "stan_gracza"),
              os.path.join(REPO, "tools", "walka")):
        if s not in sys.path:
            sys.path.insert(0, s)
    import ekonomia_jajek as EJ  # noqa: E402  (przegrody Bagna i Dżungli, przeciwnicy w pamięci silnika)
    import logika_stanu as LS  # noqa: E402
    import silnik  # noqa: E402
    import symulacja_lasu as SL  # noqa: E402
    import dane as DANE_STANU  # noqa: E402  (swiat/stan_gracza/dane.py)
    EJ.zaladuj_przeciwnikow()
    _, D = DANE_STANU.dane_z_przypadkami()
    _GRA.update(EJ=EJ, LS=LS, SL=SL, silnik=silnik, D=D,
                P={"las": SL.przegrody(), "bagno": EJ.przegrody_bagna(), "dzungla": EJ.przegrody_dzungli()},
                X={"las": SL.przybycie_i_przelot(), "bagno": EJ.przybycie_i_przelot_bagna(),
                   "dzungla": EJ.przybycie_i_przelot_dzungli()},
                K={"las": ("lesny_troll", SL.DOJSCIE, SL.LIMIT_MIN),
                   "bagno": (EJ.TROLL_BAGNA, EJ.DOJSCIE_BAGNA, EJ.LIMIT_BAGNA_MIN),
                   "dzungla": (EJ.TROLL_DZUNGLI, EJ.DOJSCIE_DZUNGLI, EJ.LIMIT_DZUNGLI_MIN)})
    return _GRA


# ------------------------------------------------------------------------------------------------ katalog
def id_przedmiotu(prefiks, stopien, rzecz):
    return "%s_%s" % (prefiks, rzecz) if stopien == "start" else "%s_%s_%s" % (prefiks, stopien, rzecz)


def _liczba(v):
    """Liczba do JSON: całkowita bez części ułamkowej, ułamek do 4 miejsc."""
    v = round(float(v), 4)
    return int(v) if v == int(v) else v


def statystyki_stopnia(klasa, slot, nr, stopien, krok_startu):
    """(baza, krok) przedmiotu kupowanego: PRZEPIS × MNOZNIK (zaokrąglone, najmniej 1), tarcza Wojownika + blok."""
    baza = {}
    for k, w in PRZEPIS[klasa][slot].items():
        baza[k] = max(1, int(round(w * MNOZNIK[stopien])))
    if klasa == "wojownik" and slot == "OffHand":
        baza["tarcza"] = _liczba(BLOK_TARCZY_NA_STOPIEN * nr)
    krok = {}
    for k, v in krok_startu.items():
        if k == "tarcza":
            krok[k] = v
        elif k == "pancerz":
            krok[k] = v + KROK_PANCERZA_NA_STOPIEN * (nr - 1)
        else:
            krok[k] = v * nr
    return baza, krok


def moc(st):
    """Jedna liczba do porównań stopni: suma statystyk, blok tarczy w punktach procentowych."""
    return round(sum(v * 100 if k == "tarcza" else v for k, v in st.items()), 4)


def katalog_bez_cen():
    """72 wpisy bez cen: stopień startowy z ustawień kowala i katalogu, stopnie kupowane z PRZEPIS × MNOZNIK."""
    kowal = _json(PLIK_KOWALA)
    kat = {p["id"]: p for p in _json(PLIK_KATALOGU)["przedmioty"]}
    G = gra()
    poziom_krainy = {"las": POZIOM_STARTU_LASU}
    for kr in ("bagno", "dzungla"):
        poziom_krainy[kr] = min(p["od"] for p in G["P"][kr])
    w = {}
    for klasa, prefiks, _n in KLASY:
        for slot, rzecz in RZECZY[klasa]:
            pid = id_przedmiotu(prefiks, "start", rzecz)
            if pid not in kowal["przedmioty"]:
                raise ValueError("Przedmiot startowy %s: brak w swiat/kowal_proba/ustawienia.json" % pid)
            if pid not in kat or kat[pid]["slot"] != slot or kat[pid]["klasy"] != [klasa] or kat[pid]["czesc_od"]:
                raise ValueError("Przedmiot startowy %s: katalog przedmioty.json ma inny slot albo klasę" % pid)
            K = kowal["przedmioty"][pid]
            w[pid] = {"klasa": klasa, "stopien": "start", "slot": slot, "cena": 0, "poziom": 1,
                      "podstawowy": bool(K["podstawowy"]), "waga": _liczba(K["waga"]),
                      "baza": {k: _liczba(v) for k, v in K["baza"].items()},
                      "krok": {k: _liczba(v) for k, v in K["krok"].items()}}
            for stopien, nr, _nazwa, kraina in STOPNIE[1:]:
                baza, krok = statystyki_stopnia(klasa, slot, nr, stopien, K["krok"])
                w[id_przedmiotu(prefiks, stopien, rzecz)] = {
                    "klasa": klasa, "stopien": stopien, "slot": slot, "cena": 0,
                    "poziom": poziom_krainy.get(kraina, 0) + PRZESUNIECIE_SLOTU[slot], "podstawowy": False,
                    "waga": _liczba(K["waga"]), "baza": {k: _liczba(v) for k, v in baza.items()},
                    "krok": {k: _liczba(v) for k, v in krok.items()}}
    obce = set(kowal["przedmioty"]) - set(w)
    if obce:
        raise ValueError("Kowal ma przedmioty spoza układu sklepu: %s" % ", ".join(sorted(obce)))
    return w


def komplet(przedmioty, klasa, stopien, tylko_podstawowe=False):
    return [pid for pid, p in przedmioty.items() if p["klasa"] == klasa and p["stopien"] == stopien
            and (p["podstawowy"] or not tylko_podstawowe)]


# ------------------------------------------------------------------------------------------------ bohater i walki
def bohater(klasa, L, przedmioty=None, zalozone=(), ulepszenie=0):
    """Opis bohatera dla silnika: wzór poziomu + suma statystyk założonych przedmiotów (wpis jak źródło „kowal”
    w Sygnaly/Modyfikatory: bron, pancerz, tarcza, statystyki), złożony prawdziwą logiką stanu gracza."""
    G = gra()
    LS, D = G["LS"], G["D"]
    o = LS.opis_bohatera(D, klasa, L, LS.rozdziel(D, D["rozklady"][klasa], LS.pula(D, L)))
    suma = {}
    for pid in zalozone:
        p = przedmioty[pid]
        for k in set(p["baza"]) | (set(p["krok"]) if ulepszenie else set()):
            suma[k] = suma.get(k, 0) + p["baza"].get(k, 0) + ulepszenie * p["krok"].get(k, 0)
    m, st = {}, {}
    for k, v in suma.items():
        if v == 0:
            continue
        if k in ("bron", "pancerz"):
            m[k] = int(v)
        elif k == "tarcza":
            m[k] = round(v, 4)
        else:
            st[k] = int(v)
    if st:
        m["statystyki"] = st
    if not m:
        return o
    czysty, powod = LS.czysty_modyfikator(D, m)
    if czysty is None:
        raise ValueError("Modyfikatory odrzuciłyby wpis sklepu: %s %s" % (powod, m))
    return LS.opis_z_modyfikatorami(D, o, LS.zloz_modyfikatory(D, [czysty]))


def szansa(o, gatunek, od, do, n, los):
    silnik = gra()["silnik"]
    w = 0
    for _ in range(n):
        r = silnik.symuluj(o, {"potwor": gatunek, "poziom": los.randint(od, do)}, los.randrange(1, 2 ** 31 - 1))
        w += r["wynik"] == "wygrana"
    return 100.0 * w / n


def szanse_w_krainach(przedmioty, n=WALK, ziarno=ZIARNO):
    """Szansa wygranej (%) w każdej krainie: bohater na najniższym poziomie przegrody, potwór z jej zakresu
    (jak balans_kowala.py część 1). Warianty stroju: zestaw podstawowy (= dzisiejszy wzór), komplet poprzedniego
    stopnia, komplet stopnia tej krainy (+0) i ten sam komplet ulepszony do +5. → {kraina: {klasa: {wariant:
    {"potwory": średnia po przegrodach bez Strażnika, "straznik": …}}}}"""
    G = gra()
    wynik = {}
    stopnie = [s[0] for s in STOPNIE]
    for kraina in KRAINY:
        nr = stopnie.index(kraina)
        wynik[kraina] = {}
        for klasa, _p, _n in KLASY:
            warianty = (("podstawowy", komplet(przedmioty, klasa, "start", True), 0),
                        ("poprzedni", komplet(przedmioty, klasa, stopnie[nr - 1]), 0),
                        ("komplet", komplet(przedmioty, klasa, kraina), 0),
                        ("komplet_plus5", komplet(przedmioty, klasa, kraina), 5))
            wynik[kraina][klasa] = {}
            for nazwa, zal, ul in warianty:
                los = random.Random("sklep-szanse-%s-%s-%s-%d" % (kraina, klasa, nazwa, ziarno))
                zw, st = [], None
                for p in G["P"][kraina]:
                    s = szansa(bohater(klasa, p["od"], przedmioty, zal, ul), p["gatunek"], p["od"], p["do"], n, los)
                    if p["straznik"]:
                        st = s
                    else:
                        zw.append(s)
                wynik[kraina][klasa][nazwa] = {"potwory": round(statistics.mean(zw), 1), "straznik": round(st, 1)}
    return wynik


def gracz_w_krainie(kraina, klasa, los, L, xp, przedmioty=None, stan=None):
    """Jeden gracz od wejścia do krainy do wygranej ze Strażnikiem (polityka symulacja_lasu.jeden_gracz: ta sama
    kolejność losowań). stan = None: bohater ze wzoru (dziś, bez sklepu). stan = {"zloto", "ma": {slot: id},
    "wizyta"}: po wygranej część Złota (UDZIAL_SAKIEWKI) idzie do sakiewki sklepu; przy wizycie (najwyżej co
    WIZYTA_CO_S, trwa WIZYTA_S) gracz kupuje najtańsze przedmioty najwyższego dostępnego stopnia, na które go stać
    i które ma prawo nosić (poziom). → słownik wyników albo None (limit czasu krainy)."""
    G = gra()
    LS, SL, D, silnik = G["LS"], G["SL"], G["D"], G["silnik"]
    P = G["P"][kraina]
    troll, dojscie, limit_min = G["K"][kraina]
    x0, przelot = G["X"][kraina]
    nr_krainy = [s[0] for s in STOPNIE].index(kraina)
    nr_stopnia = {s[0]: s[1] for s in STOPNIE}
    czas = przelot + abs(P[0]["x"] - x0) / SL.PREDKOSC
    i = z_rzedu = farma = 0
    troll_od = 0.0
    walki = przegrane = zloto = kupione = 0
    komplet_po = None
    oferta = []
    if stan is not None:
        oferta = sorted((p["cena"], pid) for pid, p in przedmioty.items()
                        if p["klasa"] == klasa and 0 < nr_stopnia[p["stopien"]] <= nr_krainy)
    while czas <= limit_min * 60:
        p = P[i]
        cel = p
        if p["gatunek"] == troll and czas < troll_od:
            cel = P[i - 1]
        hi = cel["do"] if cel["straznik"] else max(cel["od"], min(cel["do"], L + 1))
        pz = los.randint(cel["od"], hi)
        o = bohater(klasa, L, przedmioty, list(stan["ma"].values()) if stan else ())
        r = silnik.symuluj(o, {"potwor": cel["gatunek"], "poziom": pz}, los.randrange(1, 2 ** 31 - 1))
        walki += 1
        czas += r["czas"] + SL.EKRAN_WYNIKU + dojscie[cel["gatunek"]]
        L, xp, _ = LS.awans(D, L, xp, r["lup"]["doswiadczenie"])
        if r["wynik"] == "wygrana":
            zloto += r["lup"]["zloto"]
            if stan is not None:
                stan["zloto"] += r["lup"]["zloto"] * UDZIAL_SAKIEWKI
                if czas - stan["wizyta"] >= WIZYTA_CO_S:
                    kupil = False
                    for cena, pid in oferta:
                        q = przedmioty[pid]
                        stary = stan["ma"].get(q["slot"])
                        if (cena <= stan["zloto"] and q["poziom"] <= L and nr_stopnia[q["stopien"]] == nr_krainy
                                and (stary is None or nr_stopnia[przedmioty[stary]["stopien"]] < nr_krainy)):
                            stan["zloto"] -= cena
                            stan["ma"][q["slot"]] = pid
                            kupione += 1
                            kupil = True
                    if kupil:
                        stan["wizyta"] = czas
                        czas += WIZYTA_S
                        if komplet_po is None and all(przedmioty[x]["stopien"] == kraina for x in stan["ma"].values()):
                            komplet_po = czas
            z_rzedu = 0
            if p["straznik"]:
                return {"czas": czas, "walki": walki, "przegrane": przegrane, "zloto": zloto, "L": L, "xp": xp,
                        "kupione": kupione, "komplet_po": komplet_po}
            if cel is p and p["gatunek"] == troll:
                troll_od = czas + p["odrodzenie"]
            if farma > 0:
                farma -= 1
                if farma == 0:
                    czas += abs(P[i + 1]["x"] - p["x"]) / SL.PREDKOSC
                    i += 1
                continue
            if i + 1 < len(P) and L >= P[i + 1]["od"]:
                czas += abs(P[i + 1]["x"] - p["x"]) / SL.PREDKOSC
                i += 1
            continue
        przegrane += 1
        z_rzedu += 1
        if p["straznik"]:
            czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
            i -= 1
            farma = SL.ZAPAS_FARMY
        elif z_rzedu >= 2 and i > 0:
            czas += abs(P[i - 1]["x"] - p["x"]) / SL.PREDKOSC
            i -= 1
            z_rzedu = 0
    return None


def tor(przedmioty=None, graczy=GRACZY, ziarno=ZIARNO):
    """Gracze każdej klasy po kolei przez las, Bagno i Dżunglę. przedmioty = None: dziś (bez sklepu); katalog z cenami:
    ze sklepem (gracz zaczyna z zestawem podstawowym). → {kraina: [wyniki graczy + klasa, poziom wejścia]}."""
    wyniki = {k: [] for k in KRAINY}
    for klasa, _p, _n in KLASY:
        los = random.Random("sklep-tor-%s-%s-%d" % (klasa, "sklep" if przedmioty else "dzis", ziarno))
        for _ in range(graczy):
            L, xp = 1, 0
            stan = None
            if przedmioty is not None:
                stan = {"zloto": 0.0, "wizyta": -1e9,
                        "ma": {przedmioty[pid]["slot"]: pid for pid in komplet(przedmioty, klasa, "start", True)}}
            for kraina in KRAINY:
                g = gracz_w_krainie(kraina, klasa, los, L, xp, przedmioty, stan)
                if g is None:
                    break
                g.update(klasa=klasa, L0=L)
                wyniki[kraina].append(g)
                L, xp = g["L"], g["xp"]
    return wyniki


def _mediana(lista, pole, dziel=1.0):
    xs = [x[pole] / dziel for x in lista if x[pole] is not None]
    return statistics.median(xs) if xs else None


def podsumuj_tor(wyniki, graczy):
    w = {}
    for kraina in KRAINY:
        lista = wyniki[kraina]
        walk = sum(x["walki"] for x in lista)
        w[kraina] = {
            "graczy": len(lista), "graczy_na_starcie": graczy * len(KLASY),
            "minut_do_straznika": round(_mediana(lista, "czas", 60.0), 1),
            "walk_do_straznika": _liczba(_mediana(lista, "walki")),
            "przegranych": _liczba(_mediana(lista, "przegrane")),
            "zloto_do_straznika": _liczba(_mediana(lista, "zloto")),
            "zloto_na_walke": round(sum(x["zloto"] for x in lista) / walk, 1),
            "zloto_na_minute": round(sum(x["zloto"] for x in lista) / sum(x["czas"] for x in lista) * 60.0, 1),
            "poziom_wejscia": _liczba(_mediana(lista, "L0")), "poziom_po_strazniku": _liczba(_mediana(lista, "L")),
            "minut_wg_klas": {k: round(statistics.median(x["czas"] / 60.0 for x in lista if x["klasa"] == k), 1)
                              for k, _p, _n in KLASY if any(x["klasa"] == k for x in lista)}}
    return w


# ------------------------------------------------------------------------------------------------ ceny
def _zaokr(v, do):
    return int(do * round(float(v) / do))


def wycen(przedmioty, dochod, lup_pierwszej_przegrody):
    """Wpisuje ceny: komplet stopnia = UDZIAL_SKLEPU × Złoto krainy (mediana do Strażnika), zaokrąglone do setek;
    sloty według UDZIAL_SLOTU, do ZAOKRAGLENIE_CENY; resztę z zaokrągleń bierze broń, żeby komplet każdej klasy
    kosztował dokładnie tyle samo. Przedmioty startowe spoza zestawu podstawowego — po równo z kwoty startowej."""
    komplety = {}
    for stopien, _nr, _nazwa, kraina in STOPNIE[1:]:
        K = _zaokr(UDZIAL_SKLEPU * dochod[kraina]["zloto_do_straznika"], ZAOKRAGLENIE_KOMPLETU)
        komplety[stopien] = K
        for klasa, prefiks, _n in KLASY:
            ceny = {slot: _zaokr(K * UDZIAL_SLOTU[klasa][slot], ZAOKRAGLENIE_CENY) for slot, _r in RZECZY[klasa]}
            ceny["Weapon"] += K - sum(ceny.values())
            for slot, rzecz in RZECZY[klasa]:
                przedmioty[id_przedmiotu(prefiks, stopien, rzecz)]["cena"] = ceny[slot]
    start = _zaokr(WYGRANYCH_NA_START * lup_pierwszej_przegrody, ZAOKRAGLENIE_KOMPLETU)
    komplety["start"] = start
    for klasa, _p, _n in KLASY:
        brak = [pid for pid in komplet(przedmioty, klasa, "start") if not przedmioty[pid]["podstawowy"]]
        for pid in brak:
            przedmioty[pid]["cena"] = _zaokr(start / len(brak), ZAOKRAGLENIE_STARTU)
        przedmioty[brak[0]]["cena"] += start - sum(przedmioty[pid]["cena"] for pid in brak)
    return komplety


# ------------------------------------------------------------------------------------------------ spójność
def sprawdz_spojnosc(przedmioty):
    """Lista błędów (pusta = dobrze): każdy slot klasy obsadzony w każdym stopniu; w slocie cena, poziom i suma
    statystyk bazowych rosną ze stopniem; komplet stopnia kosztuje tyle samo w każdej klasie; klucze statystyk i
    wagi jak u kowala."""
    bledy = []
    znane = [s[0] for s in _json(PLIK_KOWALA)["statystyki"]]
    for klasa, prefiks, _n in KLASY:
        for slot, rzecz in RZECZY[klasa]:
            poprz = None
            for stopien, _nr, _nazwa, _kr in STOPNIE:
                pid = id_przedmiotu(prefiks, stopien, rzecz)
                p = przedmioty.get(pid)
                if p is None:
                    bledy.append("brak przedmiotu %s (slot %s klasy %s w stopniu %s)" % (pid, slot, klasa, stopien))
                    continue
                if p["klasa"] != klasa or p["slot"] != slot or p["stopien"] != stopien:
                    bledy.append("%s: klasa, slot albo stopień nie zgadza się z identyfikatorem" % pid)
                for pole in ("baza", "krok"):
                    for k, v in p[pole].items():
                        if k not in znane or not (v > 0):
                            bledy.append("%s: %s.%s = %r spoza statystyk kowala albo nie dodatnie" % (pid, pole, k, v))
                if p["waga"] not in (1, 1.75) or not isinstance(p["cena"], int) or not isinstance(p["poziom"], int):
                    bledy.append("%s: waga 1 albo 1,75, cena i poziom całkowite" % pid)
                if stopien == "start":
                    if p["podstawowy"] != (p["cena"] == 0):
                        bledy.append("%s: cena 0 tylko dla zestawu podstawowego" % pid)
                elif p["podstawowy"] or p["cena"] <= 0 or not p["baza"] or not p["krok"]:
                    bledy.append("%s: przedmiot kupowany musi mieć cenę, bazę i krok" % pid)
                if poprz is not None:
                    q = przedmioty[poprz]
                    if not (p["cena"] > q["cena"] and p["poziom"] > q["poziom"] and moc(p["baza"]) > moc(q["baza"])):
                        bledy.append("%s: cena, poziom i suma statystyk muszą być większe niż w %s" % (pid, poprz))
                    for k, v in q["baza"].items():
                        if p["baza"].get(k, 0) < v:
                            bledy.append("%s: statystyka %s mniejsza niż w %s" % (pid, k, poprz))
                    for k, v in q["krok"].items():
                        if p["krok"].get(k, 0) < v:
                            bledy.append("%s: przyrost %s mniejszy niż w %s" % (pid, k, poprz))
                poprz = pid
    if len(przedmioty) != sum(len(RZECZY[k]) for k, _p, _n in KLASY) * len(STOPNIE):
        bledy.append("liczba wpisów %d ≠ sloty klas × stopnie" % len(przedmioty))
    for stopien, _nr, _nazwa, _kr in STOPNIE:
        sumy = {klasa: sum(przedmioty[pid]["cena"] for pid in komplet(przedmioty, klasa, stopien))
                for klasa, _p, _n in KLASY}
        if len(set(sumy.values())) != 1:
            bledy.append("komplet stopnia %s kosztuje różnie w klasach: %s" % (stopien, sumy))
    return bledy


# ------------------------------------------------------------------------------------------------ całość
def policz(graczy=GRACZY, walk=WALK, ziarno=ZIARNO):
    """Pełny rachunek → słownik zapisywany do sklep_liczby.json."""
    G = gra()
    D, silnik = G["D"], G["silnik"]
    kowal, pety = _json(PLIK_KOWALA), _json(PLIK_PETOW)
    krainy = {}
    for kraina in KRAINY:
        przegrody = []
        for p in G["P"][kraina]:
            L = silnik.PRZECIWNICY[p["gatunek"]]["lup"]["zloto"]
            przegrody.append({"id": p["id"], "potwor": p["gatunek"], "nazwa": silnik.PRZECIWNICY[p["gatunek"]]["nazwa"],
                              "ranga": silnik.PRZECIWNICY[p["gatunek"]]["ranga"], "poziomy": [p["od"], p["do"]],
                              "straznik": bool(p["straznik"]),
                              "zloto_za_wygrana": [_liczba(L[0] + L[1] * p["od"]), _liczba(L[0] + L[1] * p["do"])]})
        krainy[kraina] = {"przegrody": przegrody, "poziom_potworow": [min(p["od"] for p in G["P"][kraina]),
                                                                       max(p["do"] for p in G["P"][kraina])],
                          "poziom_straznika": next(p["od"] for p in G["P"][kraina] if p["straznik"])}
    dzis = podsumuj_tor(tor(None, graczy, ziarno), graczy)
    przedmioty = katalog_bez_cen()
    p0 = krainy["las"]["przegrody"][0]
    komplety = wycen(przedmioty, dzis, statistics.mean(p0["zloto_za_wygrana"]))
    bledy = sprawdz_spojnosc(przedmioty)
    if bledy:
        raise ValueError("Katalog niespójny:\n  " + "\n  ".join(bledy))
    szanse = szanse_w_krainach(przedmioty, walk, ziarno)
    ze_sklepem_surowe = tor(przedmioty, graczy, ziarno)
    ze_sklepem = podsumuj_tor(ze_sklepem_surowe, graczy)
    for kraina in KRAINY:
        lista = ze_sklepem_surowe[kraina]
        ze_sklepem[kraina]["kupionych_do_straznika"] = _liczba(_mediana(lista, "kupione"))
        gotowi = [x["komplet_po"] / 60.0 for x in lista if x["komplet_po"] is not None]
        ze_sklepem[kraina]["komplet_przed_straznikiem_procent"] = round(100.0 * len(gotowi) / len(lista)) if lista else 0
        ze_sklepem[kraina]["komplet_po_minutach"] = round(statistics.median(gotowi), 1) if gotowi else None
    for kraina in KRAINY:
        krainy[kraina].update(dzis=dzis[kraina], ze_sklepem=ze_sklepem[kraina], szansa_wygranej=szanse[kraina])
    jajka = {j["kraina"]: j["cena"]["stala"] for j in pety["jajka"] if j["cena"].get("tryb") == "stala"}
    W = D["wzor"]
    stopnie = []
    for sid, nr, nazwa, kraina in STOPNIE:
        poziomy = [p["poziom"] for p in przedmioty.values() if p["stopien"] == sid]
        stopnie.append({"id": sid, "nr": nr, "nazwa": nazwa, "kraina": kraina, "poziom": min(poziomy),
                        "poziom_do": max(poziomy), "cena_kompletu": komplety[sid]})
    return {
        "opis": "Sklep z przedmiotami (D-106): ceny, wymagane poziomy i statystyki przedmiotów trzech klas w czterech "
                "stopniach. WYGENEROWANE przez swiat/postacie/sklep_ceny.py (nie edytuj ręcznie). baza = statystyki "
                "przy +0, krok = przyrost za poziom ulepszenia — klucze i skala jak w swiat/kowal_proba/ustawienia.json "
                "(tarcza = ułamek bloku). cena 0 = gracz ma od startu. Propozycja do oceny, nie kanon.",
        "status": "propozycja",
        "wersja": 1,
        "stopnie": stopnie,
        "zrodla": {
            "pliki": {
                "przegrody": ["swiat/las_pas_gra/zrodla/DanePotworowPasa.luau",
                              "swiat/bagno_pas_gra/zrodla/DanePotworowBagna.luau",
                              "swiat/dzungla_pas_gra/zrodla/DanePotworowDzungli.luau"],
                "lup": ["tools/walka/dane_walki.json", "swiat/bagno_pas_gra/przeciwnicy.py",
                        "swiat/dzungla_pas_gra/przeciwnicy.py"],
                "silnik": "tools/walka/silnik.py", "bohater": "swiat/stan_gracza/logika_stanu.py",
                "przedmioty_startowe": "swiat/kowal_proba/ustawienia.json", "jajka": "swiat/pety_proba/ustawienia.json"},
            "wzor_poziomu": {"bron": [W["bron_baza"], W["bron_na_poziom"]],
                             "pancerz": [W["pancerz_baza"], W["pancerz_na_poziom"]],
                             "blok_tarczy_wojownika": _liczba(W["blok_tarczy"])},
            "ceny_jajek": jajka,
            "kowal_ulepszenia": {"zloto": kowal["ulepszenie"]["zloto"], "materialy": kowal["ulepszenie"]["materialy"],
                                 "maks": kowal["ulepszenie"]["maks"]},
            "symulacja": {"graczy_na_klase": graczy, "walk_na_komorke": walk, "ziarno": ziarno,
                          "wizyta_w_sklepie_s": WIZYTA_S, "wizyta_najwyzej_co_s": WIZYTA_CO_S},
            "zalozenia": {"udzial_sklepu": UDZIAL_SKLEPU, "udzial_sakiewki_w_symulacji": UDZIAL_SAKIEWKI,
                          "udzial_slotu": UDZIAL_SLOTU,
                          "wygranych_na_komplet_startowy": WYGRANYCH_NA_START,
                          "poziom_startu_lasu": POZIOM_STARTU_LASU, "przesuniecie_poziomu_slotu": PRZESUNIECIE_SLOTU,
                          "przepis_statystyk": PRZEPIS, "mnoznik_stopnia": MNOZNIK,
                          "blok_tarczy_na_stopien": BLOK_TARCZY_NA_STOPIEN,
                          "krok_pancerza_na_stopien": KROK_PANCERZA_NA_STOPIEN},
            "krainy": krainy},
        "przedmioty": przedmioty,
    }


def tekst_json(dane):
    return json.dumps(dane, ensure_ascii=False, indent=1) + "\n"


def wczytaj():
    """Zapisany wynik (sklep_liczby.json) — bez liczenia i bez modułów gry."""
    return _json(PLIK)


# ------------------------------------------------------------------------------------------------ Markdown
def _zl(v):
    return "{:,}".format(int(v)).replace(",", " ")


def _f(v, n=1):
    return ("%.*f" % (n, v)).replace(".", ",")


def _g(v):
    return ("%g" % v).replace(".", ",")


def _st(st):
    if not st:
        return "— (ze wzoru poziomu)"
    return " · ".join("%s +%s" % (STATYSTYKI_PL[k], ("%d%%" % round(v * 100)) if k == "tarcza" else ("%d" % v))
                      for k, v in st.items())


def markdown(dane):
    Z = dane["zrodla"]
    P = dane["przedmioty"]
    S = Z["symulacja"]
    A = Z["zalozenia"]
    w = ["## Rachunek cen, poziomów i statystyk (`sklep_ceny.py`, propozycja do oceny)", ""]
    w += ["### 1. Źródła: potwory krain, ich poziomy i Złoto za wygraną", "",
          "Złoto za wygraną = baza + przyrost × poziom potwora (średnio; silnik losuje 80–120% tej liczby). "
          "Przegrody z pakietów krain (`zrodla/DanePotworow*.luau`), łup z `tools/walka/dane_walki.json` i "
          "`przeciwnicy.py` Bagna i Dżungli.", "",
          "| Kraina | Przegroda | Potwór | Poziomy | Złoto za wygraną |", "|---|---|---|---|---|"]
    for kr in KRAINY:
        for p in Z["krainy"][kr]["przegrody"]:
            zl = p["zloto_za_wygrana"]
            w.append("| %s | %s | %s%s | %s | %s |" % (
                KRAINY_PL[kr], p["id"], p["nazwa"],
                " (Strażnik)" if p["straznik"] else (" (rzadki)" if p["ranga"] == "rzadki" else ""),
                ("%d" % p["poziomy"][0]) if p["poziomy"][0] == p["poziomy"][1] else "%d–%d" % tuple(p["poziomy"]),
                _zl(zl[0]) if zl[0] == zl[1] else "%s–%s" % (_zl(zl[0]), _zl(zl[1]))))
    w += ["", "### 2. Dochód Złota dziś (bez sklepu)", "",
          "%d graczy na klasę przechodzi po kolei las, Bagno i Dżunglę prawdziwym silnikiem walki; bohater ze wzoru "
          "poziomu (broń %s + %s × poziom, pancerz %s + %s × poziom), polityka gracza jak w `symulacja_lasu.py`. "
          "Mediany; Złoto na walkę liczone ze wszystkich walk (także przegranych). Bez petów, łupu przedmiotów i "
          "ulepszeń — to dolna granica dochodu." % (
              S["graczy_na_klase"], _g(Z["wzor_poziomu"]["bron"][0]), _g(Z["wzor_poziomu"]["bron"][1]),
              _g(Z["wzor_poziomu"]["pancerz"][0]), _g(Z["wzor_poziomu"]["pancerz"][1])), "",
          "| Kraina | Poziom na wejściu → po Strażniku | Minut do Strażnika | Walk | Przegranych | Złoto z walk | "
          "Złoto na walkę | Złoto na minutę | Cena jajka |", "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for kr in KRAINY:
        d = Z["krainy"][kr]["dzis"]
        w.append("| %s | %d → %d | %s | %d | %d | %s | %s | %s | %s |" % (
            KRAINY_PL[kr], d["poziom_wejscia"], d["poziom_po_strazniku"], _f(d["minut_do_straznika"]),
            d["walk_do_straznika"], d["przegranych"], _zl(d["zloto_do_straznika"]), _f(d["zloto_na_walke"], 0),
            _f(d["zloto_na_minute"], 0), _zl(Z["ceny_jajek"].get(kr, 0))))
    u = A["udzial_slotu"]
    w += ["", "### 3. Ceny", "",
          "Komplet stopnia = %d%% Złota, które kraina daje do wygranej ze Strażnikiem (tabela 2), zaokrąglone do %d. "
          "Reszta zostaje na jajka i ulepszenia u kowala (jeden przedmiot do +%d: %s Złota). Podział na sloty: "
          "broń %d%%, tors %d%%, nakrycie głowy %d%%, druga ręka %d%%, rękawice, buty i pas po %d%%; Mag ma cztery "
          "przedmioty (broń %d%%, tors %d%%, nakrycie głowy %d%%, pas %d%%), więc komplet każdej klasy kosztuje tyle "
          "samo. Ceny zaokrąglone do %d, resztę z zaokrągleń bierze broń." % (
              round(A["udzial_sklepu"] * 100), ZAOKRAGLENIE_KOMPLETU, Z["kowal_ulepszenia"]["maks"],
              _zl(sum(Z["kowal_ulepszenia"]["zloto"])),
              round(u["wojownik"]["Weapon"] * 100), round(u["wojownik"]["Chest"] * 100),
              round(u["wojownik"]["Helmet"] * 100), round(u["wojownik"]["OffHand"] * 100),
              round(u["wojownik"]["Belt"] * 100), round(u["mag"]["Weapon"] * 100), round(u["mag"]["Chest"] * 100),
              round(u["mag"]["Helmet"] * 100), round(u["mag"]["Belt"] * 100), ZAOKRAGLENIE_CENY), "",
          "| Stopień | Wymagany poziom | Komplet | Walk na komplet | Minut na komplet | Część Złota krainy | "
          "Jajek za tę samą kwotę |", "|---|---|---:|---:|---:|---:|---:|"]
    for s in dane["stopnie"][1:]:
        d = Z["krainy"][s["kraina"]]["dzis"]
        jajko = Z["ceny_jajek"].get(s["kraina"])
        w.append("| %s (%s) | %d–%d | %s | %s | %s | %s%% | %s |" % (
            s["nazwa"], KRAINY_PL[s["kraina"]], s["poziom"], s["poziom_do"], _zl(s["cena_kompletu"]),
            _f(s["cena_kompletu"] / d["zloto_na_walke"], 0), _f(s["cena_kompletu"] / d["zloto_na_minute"], 0),
            _f(100.0 * s["cena_kompletu"] / d["zloto_do_straznika"], 0),
            _f(s["cena_kompletu"] / jajko) if jajko else "—"))
    w += ["", "Stopień startowy: zestaw podstawowy (broń, tors, tarcza Wojownika) gracz ma od początku, cena 0. "
          "Pozostałe przedmioty startowe (dziś tylko z łupu) kosztują razem %s Złota w każdej klasie — tyle, ile daje "
          "%d wygranych w pierwszej przegrodzie lasu — po równo na sztukę (Wojownik 4 sztuki, Zwiadowca 5, Mag 2)." % (
              _zl(dane["stopnie"][0]["cena_kompletu"]), A["wygranych_na_komplet_startowy"]), "",
          "| Slot | Wymagany poziom: las / Bagno / Dżungla | Wojownik i Zwiadowca: start / las / Bagno / Dżungla | "
          "Walk na sztukę: las / Bagno / Dżungla | Mag: start / las / Bagno / Dżungla |", "|---|---|---|---|---|"]
    for slot, rzecz in RZECZY["wojownik"]:
        ids = [id_przedmiotu("rycerz", s[0], rzecz) for s in STOPNIE]
        idz = [id_przedmiotu("zwiadowca", s[0], dict(RZECZY["zwiadowca"])[slot]) for s in STOPNIE]
        ceny = " / ".join(_zl(P[a]["cena"]) if P[a]["cena"] == P[b]["cena"]
                          else "%s (Zwiadowca %s)" % (_zl(P[a]["cena"]), _zl(P[b]["cena"])) for a, b in zip(ids, idz))
        mag = "—"
        if slot in dict(RZECZY["mag"]):
            mag = " / ".join(_zl(P[id_przedmiotu("kot_mag", s[0], dict(RZECZY["mag"])[slot])]["cena"]) for s in STOPNIE)
        walk = " / ".join(_f(P[ids[n]]["cena"] / Z["krainy"][kr]["dzis"]["zloto_na_walke"])
                          for n, kr in enumerate(KRAINY, 1))
        w.append("| %s | %s | %s | %s | %s |" % (SLOTY_PL[slot], " / ".join("%d" % P[i]["poziom"] for i in ids[1:]),
                                                ceny, walk, mag))
    m = A["mnoznik_stopnia"]
    w += ["", "### 4. Statystyki (+0 → przyrost za poziom ulepszenia)", "",
          "Rodzaje statystyk w slocie jak u kowala. Stopień lasu = przepis slotu × %s, Bagna × %s, Dżungli × %s — "
          "wzór poziomu rośnie liniowo (broń ze wzoru w połowie lasu %s, Bagna %s, Dżungli %s), więc stałe dodatki "
          "rosną z krainą w tym samym tempie i komplet znaczy w każdej krainie mniej więcej tyle samo. Blok tarczy "
          "+%d pp na stopień. Broń i tors startowe liczą się ze wzoru poziomu, a przedmioty stopni dodają ponad wzór. "
          "Przyrost za ulepszenie: stopień lasu jak przedmiot startowy, wyżej × numer stopnia (pancerz +%d na "
          "stopień, blok zawsze +1 pp)." % ((_g(m["las"]), _g(m["bagno"]), _g(m["dzungla"])) + tuple(
              _g(Z["wzor_poziomu"]["bron"][0] + Z["wzor_poziomu"]["bron"][1] * (sum(Z["krainy"][kr]["poziom_potworow"]) // 2))
              for kr in KRAINY) + (round(A["blok_tarczy_na_stopien"] * 100), A["krok_pancerza_na_stopien"])), ""]
    for klasa, prefiks, nazwa in KLASY:
        w += ["**%s**" % nazwa, "", "| Slot | Startowy | Leśny | Bagienny | Dżungli |", "|---|---|---|---|---|"]
        for slot, rzecz in RZECZY[klasa]:
            kom = []
            for s in STOPNIE:
                p = P[id_przedmiotu(prefiks, s[0], rzecz)]
                kom.append("%s → %s" % (_st(p["baza"]), _st(p["krok"])))
            w.append("| %s | %s |" % (SLOTY_PL[slot], " | ".join(kom)))
        w.append("")
    w += ["### 5. Szansa wygranej w krainie (%d walk na przegrodę)" % S["walk_na_komorke"], "",
          "Bohater na najniższym poziomie przegrody, potwór z jej zakresu (jak w kalkulatorze kowala), więc Strażnik "
          "wypada tu trudniej niż w grze, gdzie gracz przychodzi do niego o poziom–dwa wyżej. „Potwory” = średnia po "
          "przegrodach bez Strażnika. Zestaw podstawowy = dzisiejszy wzór poziomu. Zapis: potwory / Strażnik.", "",
          "| Kraina | Klasa | Zestaw podstawowy | Komplet poprzedniego stopnia | Komplet stopnia krainy +0 | "
          "Komplet stopnia krainy +5 |", "|---|---|---:|---:|---:|---:|"]
    for kr in KRAINY:
        for klasa, _p, nazwa in KLASY:
            x = Z["krainy"][kr]["szansa_wygranej"][klasa]
            w.append("| %s | %s | %s |" % (KRAINY_PL[kr], nazwa, " | ".join(
                "%s%% / %s%%" % (_f(x[v]["potwory"], 0), _f(x[v]["straznik"], 0))
                for v in ("podstawowy", "poprzedni", "komplet", "komplet_plus5"))))
    roznice = []
    for kr in KRAINY:
        x = Z["krainy"][kr]["szansa_wygranej"]
        v = [x[k]["komplet"]["potwory"] for k, _p, _n in KLASY]
        roznice.append("%s %s pp" % (KRAINY_PL[kr], _f(max(v) - min(v))))
    w += ["", "Różnica między klasami w komplecie stopnia krainy (potwory): %s." % ", ".join(roznice), "",
          "### 6. Gracz ze sklepem (te same krainy, %d graczy na klasę)" % S["graczy_na_klase"], "",
          "%d%% Złota z wygranych idzie do sakiewki sklepu; przy wizycie (najwyżej co %s min, trwa %s s) gracz kupuje "
          "najtańsze przedmioty stopnia krainy, na które go stać i które wolno mu nosić. Bez łupu przedmiotów, "
          "ulepszeń, jajek i petów — sam wpływ sklepu." % (
              round(A["udzial_sakiewki_w_symulacji"] * 100), _f(S["wizyta_najwyzej_co_s"] / 60.0, 0),
              _f(S["wizyta_w_sklepie_s"], 0)), "",
          "| Kraina | Minut do Strażnika: dziś → ze sklepem | Przegranych: dziś → ze sklepem | Kupionych do Strażnika | "
          "Komplet przed Strażnikiem | Minut ze sklepem: Wojownik / Zwiadowca / Mag |", "|---|---|---|---:|---|---|"]
    for kr in KRAINY:
        a, b = Z["krainy"][kr]["dzis"], Z["krainy"][kr]["ze_sklepem"]
        w.append("| %s | %s → %s | %d → %d | %d | %d%% graczy%s | %s |" % (
            KRAINY_PL[kr], _f(a["minut_do_straznika"]), _f(b["minut_do_straznika"]), a["przegranych"], b["przegranych"],
            b["kupionych_do_straznika"], b["komplet_przed_straznikiem_procent"],
            (", mediana po %s min" % _f(b["komplet_po_minutach"], 0)) if b["komplet_po_minutach"] else "",
            " / ".join(_f(b["minut_wg_klas"][k]) for k, _p, _n in KLASY)))
    w += ["", "### 7. Co przyjęte ręcznie (wybory do oceny)", "",
          "1. **Komplet = %d%% Złota krainy.** Mniej — sklep przestaje być celem; więcej — nie zostaje na jajka "
          "i kowala." % round(A["udzial_sklepu"] * 100),
          "2. **Podział ceny na sloty** (broń i tors najdroższe, pas, rękawice i buty najtańsze — pierwszy zakup po "
          "jednej–dwóch wygranych) i **równa cena kompletu w każdej klasie** (Mag: cztery droższe sztuki).",
          "3. **Wymagane poziomy:** od najniższego poziomu potworów krainy (las od %d.), sloty co poziom w kolejności "
          "pas, rękawice, buty, nakrycie głowy i druga ręka, tors, broń. Bez wymagań gracz kupiłby komplet Dżungli "
          "za Złoto nazbierane w Bagnie." % A["poziom_startu_lasu"],
          "4. **Wielkość statystyk:** mnożniki stopni %s / %s / %s i przepisy slotów — dobrane tak, żeby komplet "
          "podnosił szansę z potworami swojej krainy z ok. 60%% do ok. 80%%, a ze Strażnikiem z ok. 10–40%% do ok. 35–60%% (tabela 5); klasy "
          "wyrównane doborem przepisów." % (_g(m["las"]), _g(m["bagno"]), _g(m["dzungla"])),
          "5. **Przedmiot wyższego stopnia przy +0 jest słabszy niż poprzedni ulepszony do +2 i wyżej.** Do decyzji: "
          "czy ulepszenia przechodzą na nowy przedmiot, czy stary idzie do rozbiórki na materiały.",
          "6. **Przedmioty startowe spoza zestawu podstawowego za Złoto** (razem %s w klasie) — dziś wypadają tylko "
          "z łupu; cena jest dopłatą dla tych, którzy nie chcą czekać na łup." % _zl(dane["stopnie"][0]["cena_kompletu"]),
          "7. **Koszty ulepszeń u kowala bez zmian** (te same dla każdego stopnia, waga Maga 1,75) — przy droższych "
          "stopniach ulepszenie robi się względnie tanie; osobny wybór dla kowala.",
          "8. **D-107** (walka bez przestojów, więcej potworów) skróci czas między walkami, więc Złoto na minutę "
          "wzrośnie, a Złoto na walkę i ceny liczone w walkach zostaną.", "",
          "_python -B swiat/postacie/sklep_ceny.py (graczy %d, walk %d, ziarno %d)_" % (
              S["graczy_na_klase"], S["walk_na_komorke"], S["ziarno"]), ""]
    return "\n".join(w)


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Sklep z przedmiotami: ceny, poziomy, statystyki (propozycja)")
    ap.add_argument("--sprawdz", action="store_true", help="kod 1, gdy sklep_liczby.json jest nieaktualny")
    ap.add_argument("--md", action="store_true", help="rachunek w Markdownie na ekran (bez zapisu)")
    ap.add_argument("--z-pliku", action="store_true", help="z --md: rachunek z zapisanego pliku, bez liczenia od nowa")
    ap.add_argument("--spojnosc", action="store_true",
                    help="sprawdza tylko spójność zapisanego pliku (bez liczenia i bez modułów gry); kod 1 = błąd")
    a = ap.parse_args()
    t0 = time.time()
    if a.spojnosc or (a.md and a.z_pliku):
        if not os.path.isfile(PLIK):
            print("BŁĄD: brak swiat/postacie/sklep_liczby.json — uruchom python -B swiat/postacie/sklep_ceny.py")
            return 1
        dane = wczytaj()
        if a.md:
            print(markdown(dane))
            return 0
        bledy = sprawdz_spojnosc(dane["przedmioty"])
        for b in bledy:
            print("BŁĄD: %s" % b)
        print("sklep_liczby.json: %d przedmiotów, spójność %s" % (len(dane["przedmioty"]), "BŁĘDY" if bledy else "OK"))
        return 1 if bledy else 0
    try:
        dane = policz()
    except ValueError as e:
        print("BŁĄD: %s" % e)
        return 1
    tekst = tekst_json(dane)
    if a.md:
        print(markdown(dane))
        return 0
    if a.sprawdz:
        stary = None
        if os.path.isfile(PLIK):
            with open(PLIK, encoding="utf-8") as f:       # końce wierszy bez znaczenia (git może je zmienić)
                stary = f.read()
        ok = stary == tekst
        print("sklep_liczby.json: %s (%d przedmiotów, %.0f s)" % ("aktualny" if ok else "NIEAKTUALNY — uruchom "
              "python -B swiat/postacie/sklep_ceny.py", len(dane["przedmioty"]), time.time() - t0))
        return 0 if ok else 1
    with open(PLIK, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    print("zapisano swiat/postacie/sklep_liczby.json (%d przedmiotów, %.0f s)" % (len(dane["przedmioty"]), time.time() - t0))
    for s in dane["stopnie"]:
        print("  %-8s poziom %2d–%2d  komplet %6d Złota" % (s["id"], s["poziom"], s["poziom_do"], s["cena_kompletu"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
