#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przeciwnicy Dżungli dla silnika walki v3 — dane BEZ zmiany silnika i bez zmiany tools/walka/dane_walki.json.

    python -B swiat/dzungla_pas_gra/przeciwnicy.py            # tabela: wygrane trzech klas wzorcowych z każdym gatunkiem
    python -B swiat/dzungla_pas_gra/przeciwnicy.py --ziaren 400

Skąd liczby (propozycja, „przyjęte, do zmiany”) — ten sam przepis co Bagno (swiat/bagno_pas_gra/przeciwnicy.py):
  • Potwór Dżungli = potwór lasu o podobnej roli przemnożony mnożnikiem biomu k = 1,19 (kalkulator balansu 17.11,
    tools/walka/BALANS_1711.md, część 1, plan rosnący: Dżungla 17 → 23, k = 1,19): broń i Siła × k, modyfikator życia
    (1 + życie) × k − 1, Pancerz bez zmian.
  • Do tego jedna cecha na gatunek, której nie ma żaden potwór lasu ani Bagna — tylko z tego, co silnik już umie
    (umiejętności z dane_walki.json, modyfikatory z zamkniętej listy); prototyp walki zna choreografie tych umiejętności.
  • Nacisk Dżungli (swiat/biomy/PLAN_BIOMOW.md): zwinni przeciwnicy, którzy często unikają i ranią krwawieniem —
    opłaca się Szczęście (krytyk) i Kondycja; nikt nie jest wymaganą klasą (D-069).
  • Poziomy stref są w generuj_dane.py (POZIOMY_STREF): Dżungla 17 → 23 według kalkulatora (gracz wchodzi z Bagna na
    ok. 17. poziomie, wychodzi na ok. 24.; rzadki potwór i strażnik na 23).

Silnik: kontener Dżungli dostaje kopię modułu Dane z dopisanymi przeciwnikami Dżungli (generuj_dane.py →
silnik/DaneWalkiDzungli.luau), reszta silnika bez zmian.
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
K_BIOMU = 1.19   # BALANS_1711.md, część 1: Dżungla (plan rosnący)
# 27.11.2026 (Karol: „Tak, +25%”, pytanie 70; swiat/przejscie_gry/BALANS_2711.md — czeka na Pawła): doświadczenie z każdego
# potwora Dżungli × tyle (baza i przyrost na poziom łupu lasu). Powrót: 1.0
MNOZNIK_DOSWIADCZENIA = 1.25
KRAINA = "dzungla"

# przepis: potwór lasu (baza) × k, potem zmiany (nadpisania pól i modyfikatorów)
PRZEPISY = [
    {
        "id": "zwijogon", "nazwa": "Zwijogon", "ranga": "zwykly", "baza": "cierniowy_wilk", "klasa": "zwiadowca",
        "charakter": "kameleon z liści: wtapia się w gąszcz i najczęściej ze wszystkich unika, pazurami rani do krwi",
        "wyglad": "Kameleon z liści na pazurzastych łapach, ze zwiniętym w spiralę ogonem i oczami na wieżyczkach; "
                  "na grzbiecie czerwony grzebień.",
        "umiejetnosci": ["skupienie", "rozszarpanie"],
        "modyfikatory": {"unik": 0.06, "zycie": -0.48},
        "cecha": "Skupienie (wtapia się w liście) przed rozszarpaniem i najczęstszy unik w grze (+10 pp); wilk lasu "
                 "tylko rani, Rechotek Bagna skacze z góry",
    },
    {
        "id": "gebokwiat", "nazwa": "Gębokwiat", "ranga": "zwykly", "baza": "muchomornik", "klasa": "mag",
        "charakter": "kwiat z paszczą: pluje usypiającym pyłkiem, który spowalnia; kruchy, ale trudno go trafić",
        "wyglad": "Wielki czerwony kwiat z paszczą i żółtym środkiem na krótkich korzeniach-nóżkach.",
        "umiejetnosci": ["lodowy_pocisk"],
        "modyfikatory": {"odpornosc": -0.3, "zycie": -0.36, "unik": 0.04},
        "cecha": "usypiający pyłek (lodowy pocisk: spowolnienie) — w lesie i na Bagnie nikt nie spowalnia; częstszy "
                 "unik niż Muchomornik",
    },
    {
        "id": "kokosowy_silacz", "nazwa": "Kokosowy Siłacz", "ranga": "zwykly", "baza": "lesny_troll",
        "klasa": "wojownik",
        "charakter": "krępa małpa-siłacz: kokosami bije mocno i z góry, nie blokuje, za to rzadko daje się trafić z boku",
        "wyglad": "Krępa brązowa małpa-siłacz z dwoma kokosami w pięściach.",
        "umiejetnosci": ["ciecie"],
        "modyfikatory": {"zycie": -0.22, "cios": -0.02},
        "cecha": "Potężne cięcie (oba kokosy z góry, 2,06 × obrażeń) — najmocniejszy pojedynczy cios zwykłego potwora; "
                 "Kłodokłap Bagna blokuje i zdziera pancerz",
    },
    {
        "id": "pancernik_ruin", "nazwa": "Pancernik Ruin", "ranga": "rzadki", "baza": "lesny_troll", "klasa": "wojownik",
        "charakter": "rzadki pancernik obrośnięty płytami ruin: zwija się w kamienną kulę i przeczekuje ciosy",
        "wyglad": "Pancernik z płyt starego kamienia z rytami i mchem, ze świecącymi turkusowymi szczelinami.",
        "umiejetnosci": ["kamienna_skora"],
        "modyfikatory": {"zycie": 0.4, "cios": 0.15, "pancerz": 0.3},
        "cecha": "Kamienna skóra (na siebie) i gruby Pancerz — rzadki Troll lasu ogłusza, Ropucha Bagna truje",
    },
    {
        "id": "waz_stu_lian", "nazwa": "Wąż Stu Lian", "ranga": "straznik", "baza": "straznik_lasu",
        "klasa": "straznik",
        "charakter": "strażnik Dżungli: ogromny wąż z lian, pluje jadem i kąsa do krwi, wije się poza zasięgiem ciosów",
        "wyglad": "Ogromny wąż spleciony z lian i pnączy, z wielkim czerwono-żółtym kwiatem na głowie jak kaptur, zwinięty "
                  "w spiralę.",
        "umiejetnosci": ["zatruta_strzala", "rozszarpanie"],
        # życie: D-111 (Karol 19.11) −15% — było 0,3 (2852 na poz. 23), jest (1 + 0,3) × 0,85 − 1 = 0,105 (2424)
        "modyfikatory": {"unik": 0.05, "zysk_many": 0.25, "zycie": 0.105},
        "cecha": "jad (trucizna) i ukąszenie (krwawienie) na zmianę, częsty unik; Strażnik Gaju unieruchamia korzeniami, "
                 "Strażnik Topieli ogłusza",
    },
]

# łup jak u bazy (pary [baza, na poziom] rosną same z poziomem); kraina Dżungli (tokeny Dżungli)
LUP_PO_RANDZE = {"zwykly": "cierniowy_wilk", "rzadki": "lesny_troll", "straznik": "straznik_lasu"}


def dane_lasu():
    with open(PLIK_WALKI, encoding="utf-8") as f:
        return json.load(f)


def przeciwnicy(dane=None):
    """Lista przeciwników Dżungli w formacie tools/walka/dane_walki.json → przeciwnicy."""
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
        d["lup"]["doswiadczenie"] = [round(x * MNOZNIK_DOSWIADCZENIA, 4) for x in d["lup"]["doswiadczenie"]]
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


def dane_walki_dzungli():
    """Dane silnika dla kontenera Dżungli: dane lasu bez zmian + przeciwnicy Dżungli na końcu listy."""
    d = dane_lasu()
    d["przeciwnicy"] = d["przeciwnicy"] + przeciwnicy(d)
    return d


def zaladuj_do_silnika(silnik):
    """Dopisuje przeciwników Dżungli do portu w Pythonie (tylko w pamięci procesu; do testów i tabeli)."""
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
    "zwijogon": [(17, 17), (19, 19)],
    "gebokwiat": [(19, 19), (21, 21)],
    "kokosowy_silacz": [(21, 21), (23, 23)],
    "pancernik_ruin": [(23, 23), (23, 24)],
    "waz_stu_lian": [(23, 23), (23, 24)],
}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Przeciwnicy Dżungli: tabela wygranych klas wzorcowych")
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
