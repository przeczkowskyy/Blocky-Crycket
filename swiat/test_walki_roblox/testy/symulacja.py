#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrolny port silnika walki (zrodla/SilnikWalki.luau) — do strojenia statystyk i szukania ziaren pokazowych.

    python -B swiat/test_walki_roblox/testy/symulacja.py                 # rozkład wyników dla 20 000 ziaren
    python -B swiat/test_walki_roblox/testy/symulacja.py --ziarno 2026   # dziennik jednej walki (JSON)
    python -B swiat/test_walki_roblox/testy/symulacja.py --szukaj        # ziarna pokazowe (wygrana z 4 akcjami, przegrana)

Port jest dosłowny: ten sam generator (Park–Miller), ta sama kolejność rzutów i te same zaokrąglenia,
więc dla tego samego ziarna daje ten sam dziennik co Luau (sprawdza to testy/test_silnika.luau w Studio).
Statystyki testowe muszą być takie same jak w zrodla/SerwerWalki.server.luau.
"""
import argparse
import collections
import json
import math
import sys

MIN_WYMIAN, MAKS_WYMIAN = 4, 6
MIN_CZAS, MAKS_CZAS = 8.0, 10.0
CZAS_WSTEPU, CZAS_FINALU = 1.1, 1.9
PRZED = {"cios": 0.58, "blok": 0.58, "unik": 0.58, "krytyk": 0.85}
PO = {"cios": 0.56, "blok": 0.56, "unik": 0.50, "krytyk": 0.90}
CZESC_PRZEZ_BLOK = 0.18
ESKALACJA = 0.45
MODUL = 2147483647

GRACZ = {"nazwa": "Rycerz", "poziom": 3, "hp": 480, "atak": 150, "obrona": 30, "szybkosc": 12,
         "krytyk": 0.22, "mnoznikKrytyka": 3.0, "blok": 0.30, "unik": 0.06}
WROG = {"nazwa": "Zbir", "poziom": 2, "hp": 450, "atak": 125, "obrona": 15, "szybkosc": 9,
        "krytyk": 0.12, "mnoznikKrytyka": 2.5, "blok": 0.10, "unik": 0.12}


def nowy_los(ziarno):
    stan = int(math.floor(abs(ziarno))) % MODUL
    if stan == 0:
        stan = 20261113

    def los():
        nonlocal stan
        stan = (stan * 48271) % MODUL
        return (stan - 1) / (MODUL - 1)

    for _ in range(8):
        los()
    return los


def zaokraglij(x):
    return math.floor(x + 0.5)


def symuluj(gracz, wrog, ziarno):
    los = nowy_los(ziarno)
    strony = {"gracz": gracz, "wrog": wrog}
    hp = {"gracz": math.floor(gracz["hp"]), "wrog": math.floor(wrog["hp"])}
    dziennik = []
    kolej = "gracz" if los() < gracz["szybkosc"] / (gracz["szybkosc"] + wrog["szybkosc"]) else "wrog"
    zwyciezca = None
    for nr in range(1, MAKS_WYMIAN + 1):
        ostatnia = nr == MAKS_WYMIAN
        if ostatnia:
            kolej = "gracz" if hp["gracz"] / gracz["hp"] >= hp["wrog"] / wrog["hp"] else "wrog"
        atakujacy = kolej
        broniacy = "wrog" if kolej == "gracz" else "gracz"
        A, D = strony[atakujacy], strony[broniacy]
        rozrzut = 0.85 + 0.30 * los()
        rzut = los()
        mnoznik = 1 + ESKALACJA * max(0, nr - 3)
        baza = A["atak"] * rozrzut * (100 / (100 + D["obrona"])) * mnoznik
        if ostatnia:
            akcja, obrazenia = "krytyk", max(zaokraglij(baza * A["mnoznikKrytyka"]), hp[broniacy])
        elif rzut < D["unik"]:
            akcja, obrazenia = "unik", 0
        elif rzut < D["unik"] + A["krytyk"]:
            akcja, obrazenia = "krytyk", max(1, zaokraglij(baza * A["mnoznikKrytyka"]))
        elif rzut < D["unik"] + A["krytyk"] + D["blok"]:
            akcja, obrazenia = "blok", max(1, zaokraglij(baza * CZESC_PRZEZ_BLOK))
        else:
            akcja, obrazenia = "cios", max(1, zaokraglij(baza))
        if nr < MIN_WYMIAN and obrazenia >= hp[broniacy]:
            obrazenia = hp[broniacy] - 1
        hp[broniacy] = max(0, hp[broniacy] - obrazenia)
        dziennik.append({"t": 0, "kto": atakujacy, "akcja": akcja, "obrazenia": obrazenia, "hp_po": hp[broniacy]})
        if hp[broniacy] <= 0:
            zwyciezca = atakujacy
            break
        kolej = broniacy
    suma = sum(PRZED[z["akcja"]] + PO[z["akcja"]] for z in dziennik)
    czas = min(max(CZAS_WSTEPU + suma + CZAS_FINALU, MIN_CZAS), MAKS_CZAS)
    skala = (czas - CZAS_WSTEPU - CZAS_FINALU) / suma
    t = CZAS_WSTEPU
    for z in dziennik:
        t += PRZED[z["akcja"]] * skala
        z["t"] = zaokraglij(t * 100) / 100
        t += PO[z["akcja"]] * skala
    wygrana = zwyciezca == "gracz"
    poziom = max(1, math.floor(wrog.get("poziom", 1)))
    rz, rd, rj = los(), los(), los()
    if wygrana:
        lup = {"zloto": zaokraglij(poziom * 45 * (0.9 + 0.6 * rz)), "doswiadczenie": zaokraglij(poziom * 18 * (1 + 0.5 * rd)),
               "jajko": 1 if rj < 0.4 else 0}
    else:
        lup = {"zloto": 0, "doswiadczenie": zaokraglij(poziom * 4 * (1 + 0.5 * rd)), "jajko": 0}
    return {"wersja": 1, "ziarno": ziarno,
            "strony": {"gracz": {"nazwa": gracz["nazwa"], "poziom": gracz["poziom"], "hp": math.floor(gracz["hp"])},
                       "wrog": {"nazwa": wrog["nazwa"], "poziom": wrog["poziom"], "hp": math.floor(wrog["hp"])}},
            "dziennik": dziennik, "wynik": "wygrana" if wygrana else "przegrana", "lup": lup,
            "czas": zaokraglij(czas * 100) / 100}


def skrot(w):
    return " ".join("%s:%s%s" % (z["kto"][0], z["akcja"], ("-%d" % z["obrazenia"]) if z["obrazenia"] else "") for z in w["dziennik"])


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kontrolny port silnika walki")
    ap.add_argument("--ziarno", type=int)
    ap.add_argument("--szukaj", action="store_true")
    ap.add_argument("--ile", type=int, default=20000)
    a = ap.parse_args()
    if a.ziarno is not None:
        print(json.dumps(symuluj(GRACZ, WROG, a.ziarno), ensure_ascii=False, indent=1))
        return
    if a.szukaj:
        znalezione = collections.defaultdict(list)
        for z in range(1, 200000):
            w = symuluj(GRACZ, WROG, z)
            akcje = [x["akcja"] for x in w["dziennik"]]
            d = w["dziennik"]
            if (w["wynik"] == "wygrana" and len(d) == 5 and set(akcje) == {"cios", "blok", "unik", "krytyk"}
                    and d[0]["kto"] == "gracz" and d[0]["akcja"] == "cios" and d[1]["akcja"] == "blok"
                    and d[-1]["akcja"] == "krytyk" and w["lup"]["jajko"] == 1):
                znalezione["pokaz: wygrana, 5 wymian, cios-blok-…-krytyk, jajko"].append(z)
            if w["wynik"] == "przegrana" and len(d) == 4:
                znalezione["przegrana w 4 wymianach"].append(z)
            if w["wynik"] == "przegrana" and len(d) == 6:
                znalezione["przegrana w 6 wymianach"].append(z)
            if w["wynik"] == "wygrana" and len(d) == 4:
                znalezione["wygrana w 4 wymianach"].append(z)
            if w["wynik"] == "wygrana" and len(d) == 6:
                znalezione["wygrana w 6 wymianach"].append(z)
        for k, v in znalezione.items():
            print("%s: %d ziaren, pierwsze: %s" % (k, len(v), v[:8]))
            for z in v[:3]:
                w = symuluj(GRACZ, WROG, z)
                print("    %d: %s | czas %.2f | łup %s" % (z, skrot(w), w["czas"], w["lup"]))
        return
    wyniki, dlugosci, akcje, czasy = collections.Counter(), collections.Counter(), collections.Counter(), []
    for z in range(1, a.ile + 1):
        w = symuluj(GRACZ, WROG, z)
        wyniki[w["wynik"]] += 1
        dlugosci[len(w["dziennik"])] += 1
        czasy.append(w["czas"])
        for x in w["dziennik"]:
            akcje[x["akcja"]] += 1
        assert MIN_WYMIAN <= len(w["dziennik"]) <= MAKS_WYMIAN and MIN_CZAS <= w["czas"] <= MAKS_CZAS
        assert w["dziennik"][-1]["hp_po"] == 0
    n = a.ile
    print("ziaren:", n)
    print("wynik:", {k: "%.1f%%" % (100 * v / n) for k, v in wyniki.items()})
    print("wymian:", {k: "%.1f%%" % (100 * v / n) for k, v in sorted(dlugosci.items())})
    print("akcje:", {k: "%.1f%%" % (100 * v / sum(akcje.values())) for k, v in akcje.items()})
    print("czas: min %.2f, śr. %.2f, maks %.2f" % (min(czasy), sum(czasy) / n, max(czasy)))


if __name__ == "__main__":
    main()
