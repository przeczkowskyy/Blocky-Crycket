#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przeciwnicy Bagna dla silnika walki v3 — dane BEZ zmiany silnika i bez zmiany tools/walka/dane_walki.json.

    python -B swiat/bagno_pas_gra/przeciwnicy.py            # tabela: wygrane trzech klas wzorcowych z każdym gatunkiem
    python -B swiat/bagno_pas_gra/przeciwnicy.py --ziaren 400

Skąd liczby (propozycja, „przyjęte, do zmiany”):
  • Potwór Bagna = potwór lasu o podobnej roli przemnożony mnożnikiem biomu k = 1,14 (kalkulator balansu 17.11,
    tools/walka/BALANS_1711.md, część 1, plan rosnący: Bagno k = 1,14) — tym samym przepisem co
    tools/walka/progresja.potwor_biomu: broń i Siła × k, modyfikator życia (1 + życie) × k − 1, Pancerz bez zmian.
  • Do tego jedna cecha w walce na gatunek, której nie ma żaden potwór lasu — tylko z tego, co silnik już umie
    (istniejące umiejętności, modyfikatory z zamkniętej listy, szansa bloku), więc odtwarzacz walki prototypu zna
    nazwy i choreografie umiejętności i nic w silniku ani w prototypie nie trzeba dopisywać.
  • Poziomy stref są w generuj_dane.py (POZIOMY_STREF): Bagno 10 → 16 według kalkulatora (gracz wchodzi z lasu na
    ok. 10. poziomie, wychodzi na ok. 17.; troll i strażnik o poziom niżej niż gracz na wyjściu).

Silnik: każdy kontener ma KOPIĘ silnika (src/server/Walka). Kontener Bagna dostaje kopię modułu Dane z dopisanymi
przeciwnikami Bagna (generuj_dane.py → silnik/DaneWalkiBagna.luau), reszta silnika bez zmian. Testy silnika
(tools/walka) dalej liczą tylko las — przeciwników Bagna tam nie ma (ich testy wymagają m.in. jednego strażnika).
"""
import argparse
import copy
import json
import os
import statistics
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "tools", "walka")
if WALKA not in sys.path:
    sys.path.insert(0, WALKA)

PLIK_WALKI = os.path.join(WALKA, "dane_walki.json")
K_BIOMU = 1.14   # BALANS_1711.md, część 1: Bagno (plan rosnący)
KRAINA = "bagno"

# przepis: potwór lasu (baza) × k, potem zmiany (nadpisania pól i modyfikatorów)
PRZEPISY = [
    {
        "id": "rechotek", "nazwa": "Rechotek", "ranga": "zwykly", "baza": "cierniowy_wilk", "klasa": "zwiadowca",
        "charakter": "skacze susami: często unika, a z góry spada całym ciałem z dużą szansą na krytyk",
        "wyglad": "Przysadzista oliwkowa ropucha z klocków w ciemne plamy, z żółtym brzuchem, płaskim szerokim łbem i "
                  "pomarańczowymi oczami na czubku głowy; skacze susami po kępach.",
        "umiejetnosci": ["uderzenie_z_gory"],
        "modyfikatory": {"unik": 0.06},
        "cecha": "Uderzenie z góry (sus i plaśnięcie, premia krytyka) + częstszy unik; w lesie zwiadowcy zdzierają "
                 "pancerz (Slime) i ranią do krwi (Wilk)",
    },
    {
        "id": "bulgotnik", "nazwa": "Bulgotnik", "ranga": "zwykly", "baza": "muchomornik", "klasa": "mag",
        "charakter": "błotny szaman: osłania się bańką gazu, a chmurą trującego oparu przeciąga walkę",
        "wyglad": "Mały kopczyk z błota na krótkich nóżkach; głowa to bańka gazu z dwojgiem oczu w środku, w łapce "
                  "krzywy kij z zielonożółtym ognikiem.",
        "umiejetnosci": ["bariera", "chmura_zarodnikow"],
        "modyfikatory": {"odpornosc": -0.35, "zycie": -0.27},
        "cecha": "Bariera (tarcza procentowa na siebie) obok trującej chmury; Muchomornik lasu tylko truje",
    },
    {
        "id": "klodoklap", "nazwa": "Kłodokłap", "ranga": "zwykly", "baza": "lesny_troll", "klasa": "wojownik",
        "charakter": "żywa kłoda: gruby Pancerz, blokuje korą, nie unika; miażdżące kłapnięcie zdziera pancerz",
        "wyglad": "Długa omszała kłoda na czterech łapach-korzeniach; przód rozcięty w paszczę z jasnymi kołkami-zębami, "
                  "na grzbiecie pomarańczowy grzybek.",
        "umiejetnosci": ["miazdzacy_cios"],
        "tarcza": 0.15,
        "modyfikatory": {"zycie": -0.14, "cios": -0.02, "pancerz": 0.2, "unik": -0.5},
        "cecha": "blok korą (szansa bloku 15% + 5% klasy) i gruby Pancerz, zero uniku; Miażdżący cios zdziera "
                 "pancerz — w lesie nikt nie blokuje",
    },
    {
        "id": "ropucha_z_chatka", "nazwa": "Ropucha z Chatką", "ranga": "rzadki", "baza": "lesny_troll", "klasa": "mag",
        "charakter": "rzadka, stara ropucha z chatką na grzbiecie: dym z komina truje, ciężki sus rani fizycznie",
        "wyglad": "Ogromna stara ropucha w brodawkach z krzywą chatką z desek na grzbiecie; z kamiennego komina bucha "
                  "dym, okienko świeci ciepło.",
        "umiejetnosci": ["chmura_zarodnikow", "uderzenie_z_gory"],
        "modyfikatory": {"zycie": -0.05, "cios": -0.08, "odpornosc": 0.2},
        "statystyki_zmiana": {"inteligencja": [7.0, 2.4]},
        "cecha": "rzadki Mag z dwiema umiejętnościami (trucizna z komina i sus) — rzadki potwór lasu (Troll) to "
                 "wojownik, który ogłusza",
    },
    {
        "id": "straznik_topieli", "nazwa": "Strażnik Topieli", "ranga": "straznik", "baza": "straznik_lasu",
        "klasa": "straznik",
        "charakter": "strażnik Bagna: olbrzym z błota i korzeni, uderza w taflę i ogłusza, odporny na magię",
        "wyglad": "Olbrzym z błota i korzeni wynurzony z wody, z przewróconą łódką jak kapeluszem, zieloną latarnią w "
                  "piersi i brodą z mchu.",
        "umiejetnosci": ["ogluszajace_uderzenie"],
        "modyfikatory": {"odpornosc": 0.3, "zysk_many": 0.25, "zycie": 0.6},
        "cecha": "fizyczne uderzenie w taflę (60% ogłuszenia) częściej niż Strażnik Gaju (zysk many +25%) i "
                 "odporność na magię; Strażnik Gaju unieruchamia magicznymi korzeniami",
    },
]

# łup jak u bazy (pary [baza, na poziom] rosną same z poziomem); kraina Bagna (tokeny Bagna)
LUP_PO_RANDZE = {"zwykly": "cierniowy_wilk", "rzadki": "lesny_troll", "straznik": "straznik_lasu"}


def dane_lasu():
    with open(PLIK_WALKI, encoding="utf-8") as f:
        return json.load(f)


def przeciwnicy(dane=None):
    """Lista przeciwników Bagna w formacie tools/walka/dane_walki.json → przeciwnicy."""
    dane = dane or dane_lasu()
    po_id = {p["id"]: p for p in dane["przeciwnicy"]}
    mod_id = {m["id"]: m for m in dane["modyfikatory"]}
    wynik = []
    for p in PRZEPISY:
        b = copy.deepcopy(po_id[p["baza"]])
        k = K_BIOMU
        d = {
            "id": p["id"], "nazwa": p["nazwa"], "ranga": p["ranga"], "kraina": KRAINA,
            "charakter": p["charakter"], "wyglad": p["wyglad"], "klasa": p["klasa"],
            "statystyki": b["statystyki"],
            "bron": [round(b["bron"][0] * k, 4), round(b["bron"][1] * k, 4)],
            "pancerz_przedmiotow": b["pancerz_przedmiotow"],
            "tarcza": p.get("tarcza", b["tarcza"]),
            "modyfikatory": dict(b["modyfikatory"]),
            "umiejetnosci": list(p["umiejetnosci"]),
            "lup": copy.deepcopy(po_id[LUP_PO_RANDZE[p["ranga"]]]["lup"]),
        }
        d["statystyki"]["sila"] = [round(x * k, 4) for x in d["statystyki"]["sila"]]
        for nazwa, para in (p.get("statystyki_zmiana") or {}).items():
            d["statystyki"][nazwa] = list(para)
        # przepis kalkulatora: życie (1 + m) × k − 1 — potem zmiany gatunku (podane jako wartość końcowa)
        d["modyfikatory"]["zycie"] = round((1 + d["modyfikatory"].get("zycie", 0)) * k - 1, 4)
        d["modyfikatory"].update(p.get("modyfikatory") or {})
        for klucz, w in d["modyfikatory"].items():
            m = mod_id[klucz]
            if not m["min"] <= w <= m["max"]:
                raise ValueError("%s: modyfikator %s = %s poza %s…%s" % (p["id"], klucz, w, m["min"], m["max"]))
        for u in d["umiejetnosci"]:
            if u not in dane["umiejetnosci"] and u not in dane["pasywne"]:
                raise ValueError("%s: nieznana umiejętność %s (silnik jej nie zna)" % (p["id"], u))
        if not 0 <= d["tarcza"] <= dane["stale"]["blok_maks"]:
            raise ValueError("%s: tarcza poza 0…blok_maks" % p["id"])
        wynik.append(d)
    return wynik


def dane_walki_bagna():
    """Dane silnika dla kontenera Bagna: dane lasu bez zmian + przeciwnicy Bagna na końcu listy."""
    d = dane_lasu()
    d["przeciwnicy"] = d["przeciwnicy"] + przeciwnicy(d)
    return d


def zaladuj_do_silnika(silnik):
    """Dopisuje przeciwników Bagna do portu w Pythonie (tylko w pamięci procesu; do testów i tabeli)."""
    for d in przeciwnicy():
        silnik.PRZECIWNICY[d["id"]] = d
    return silnik


def tabela(ziaren=300, poziomy=None):
    """[(id, poziom potwora, poziom gracza, {klasa: % wygranych})]."""
    import silnik
    import wzorcowe
    zaladuj_do_silnika(silnik)
    poziomy = poziomy or POZIOMY_TABELI
    wiersze = []
    for pid, pary in poziomy.items():
        for L_potwor, L_gracz in pary:
            wyn = {}
            for kl in wzorcowe.KLASY:
                g = wzorcowe.postac(kl, L_gracz)
                n = sum(silnik.symuluj(g, {"potwor": pid, "poziom": L_potwor}, z)["wynik"] == "wygrana"
                        for z in range(1, ziaren + 1))
                wyn[kl] = 100.0 * n / ziaren
            wiersze.append((pid, L_potwor, L_gracz, wyn))
    return wiersze


# poziom potwora, poziom gracza: wejście do przegrody (gracz = potwór) i gracz o poziom wyżej
POZIOMY_TABELI = {
    "rechotek": [(10, 10), (12, 12)],
    "bulgotnik": [(12, 12), (14, 14)],
    "klodoklap": [(14, 14), (16, 16)],
    "ropucha_z_chatka": [(16, 16), (16, 17)],
    "straznik_topieli": [(16, 16), (16, 17)],
    # dla porównania: las na końcu (gracz 10)
    "cierniowy_wilk": [(10, 10)],
    "lesny_troll": [(9, 10)],
    "straznik_lasu": [(10, 10)],
}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przeciwnicy Bagna: tabela wygranych klas wzorcowych")
    ap.add_argument("--ziaren", type=int, default=300)
    a = ap.parse_args()
    print("| gatunek | poz. potwora | poz. gracza | Wojownik | Zwiadowca | Mag | średnio | rozstęp klas |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|")
    for pid, Lp, Lg, w in tabela(a.ziaren):
        sr = statistics.mean(w.values())
        print("| %s | %d | %d | %.0f%% | %.0f%% | %.0f%% | %.0f%% | %.0f pp |" % (
            pid, Lp, Lg, w["wojownik"], w["zwiadowca"], w["mag"], sr, max(w.values()) - min(w.values())))


if __name__ == "__main__":
    main()
