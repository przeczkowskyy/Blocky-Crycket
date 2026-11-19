#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Katalog sklepu z przedmiotami -> swiat/postacie/sklep_przedmioty.json (D-106; propozycja do oceny).

    python -B swiat/postacie/sklep_katalog.py             # zapisuje sklep_przedmioty.json
    python -B swiat/postacie/sklep_katalog.py --sprawdz   # kod 1, gdy plik jest nieaktualny albo dane się nie zgadzają
    python -B swiat/postacie/sklep_katalog.py --md        # tabele katalogu (Markdown) do SKLEP_PRZEDMIOTY.md

Składa w jeden plik (do wczytania przez symulację przejścia gry, przymierzalnię, kowala i przyszły sklep):
  - wygląd i dopasowanie do ciała: stopnie.py i moduły bohaterów (Przedmiot.opis() — te same pola co wpisy
    bohaterów w przedmioty.json: slot, kategoria, cialo, klasy, czesc_od, ukrywa, zestaw, czesci);
  - liczby: sklep_liczby.json z kalkulatora sklep_ceny.py (cena, wymagany poziom, podstawowy, waga, baza, krok —
    baza i krok w tych samych rodzajach i skali co przedmioty kowala, swiat/kowal_proba/ustawienia.json).
Umowa dla sklepu (pola wpisu): SKLEP_PRZEDMIOTY.md. Bez Blendera i bez Studio.
"""
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie import stopnie  # noqa: E402

LICZBY = os.path.join(TU, "sklep_liczby.json")
KATALOG_BOHATEROW = os.path.join(TU, "przedmioty.json")
WYNIK = os.path.join(TU, "sklep_przedmioty.json")
STATYSTYKI = [["bron", "Broń"], ["pancerz", "Pancerz"], ["tarcza", "Blok tarczy"], ["Strength", "Siła"],
              ["Constitution", "Kondycja"], ["Intelligence", "Inteligencja"], ["Dexterity", "Zręczność"],
              ["Luck", "Szczęście"]]
SLOTY = {"Helmet": "Nakrycie głowy", "Chest": "Zbroja", "Gloves": "Rękawice", "Boots": "Buty", "Belt": "Pas",
         "Weapon": "Broń", "OffHand": "Druga ręka"}
UMOWA = {
    "id": "identyfikator przedmiotu (ten sam w przymierzalni, u kowala i w sklepie)",
    "nazwa": "nazwa dla gracza", "opis": "krótki opis wyglądu",
    "klasa": "wojownik | zwiadowca | mag — tylko ta klasa może kupić i założyć",
    "stopien": "start | las | bagno | dzungla", "nr_stopnia": "0–3",
    "slot": "Helmet | Chest | Gloves | Boots | Belt | Weapon | OffHand",
    "sprzedawany": "false = część innego przedmiotu (nogawice, spodnie): gracz dostaje ją razem z przedmiotem "
                   "z pola czesc_od, w sklepie nie ma osobnej pozycji",
    "cena": "Złoto; 0 = gracz ma przedmiot od startu (zestaw podstawowy)",
    "poziom": "wymagany poziom postaci",
    "podstawowy": "true = zestaw podstawowy klasy (liczy się jak dzisiejszy wzór poziomu)",
    "waga": "mnożnik kosztów ulepszeń u kowala (Mag 1,75 — ma cztery przedmioty)",
    "baza": "statystyki przedmiotu przy ulepszeniu +0 (klucze jak u kowala; tarcza = ułamek bloku)",
    "krok": "przyrost statystyk za każdy poziom ulepszenia u kowala",
    "czesci": "segmenty modelu: kość, powłoka, zaczep (dane przymierzalni; geometria w stopnie.py i modułach "
              "bohaterów)",
    "ikona": "plik ikony w repozytorium (po przebudowie w Blenderze)",
}


class BladDanych(Exception):
    pass


def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def zbierz():
    L = _json(LICZBY)
    liczby = L["przedmioty"]
    ikony_startu = {p["id"]: p.get("plik_ikony") for p in _json(KATALOG_BOHATEROW)["przedmioty"]}
    nr = {s["id"]: s["nr"] for s in L["stopnie"]}
    if list(nr) != list(stopnie.WSZYSTKIE_STOPNIE):
        raise BladDanych("stopnie w sklep_liczby.json (%s) ≠ stopnie.py (%s)" % (list(nr), stopnie.WSZYSTKIE_STOPNIE))
    klasy, przedmioty, uzyte = {}, [], set()
    for klasa, mod in stopnie.MODULY.items():
        po_id = stopnie.wszystkie(klasa)
        korekty = getattr(mod, "KOREKTY_CHWYTU", None)
        komplety = {st: list(stopnie.komplet(klasa, st)) for st in stopnie.WSZYSTKIE_STOPNIE}
        klasy[klasa] = {"bohater": stopnie.BOHATER[klasa], "cialo": mod.CIALO_TYP, "komplety": komplety}
        for st in stopnie.WSZYSTKIE_STOPNIE:
            for i in komplety[st]:
                x = po_id[i]
                o = x.opis(korekty)
                wpis = {"id": i, "nazwa": x.nazwa,
                        "opis": "dzisiejszy przedmiot bohatera" if st == "start" else stopnie.opis(i)[1],
                        "klasa": klasa, "stopien": st, "nr_stopnia": nr[st], "slot": x.slot,
                        "sprzedawany": x.czesc_od is None}
                if x.czesc_od is None:
                    if i not in liczby:
                        raise BladDanych("przedmiot %s nie ma liczb w sklep_liczby.json" % i)
                    n = liczby[i]
                    for pole, wartosc in (("klasa", klasa), ("stopien", st), ("slot", x.slot)):
                        if n[pole] != wartosc:
                            raise BladDanych("przedmiot %s: %s w liczbach (%r) ≠ model (%r)" % (i, pole, n[pole], wartosc))
                    uzyte.add(i)
                    for pole in ("cena", "poziom", "podstawowy", "waga", "baza", "krok"):
                        wpis[pole] = n[pole]
                for pole in ("kategoria", "cialo", "klasy", "czesc_od", "ukrywa", "zestaw", "czesci"):
                    wpis[pole] = o[pole]
                wpis["ikona"] = (ikony_startu.get(i) if st == "start"
                                 else "wynik/stopnie_%s/ikony/%s_ikona.png" % (klasa, i))
                przedmioty.append(wpis)
    zbedne = sorted(set(liczby) - uzyte)
    if zbedne:
        raise BladDanych("sklep_liczby.json ma przedmioty bez modelu: %s" % ", ".join(zbedne))
    return {"opis": "Katalog sklepu z przedmiotami trzech klas: komplet startowy i trzy stopnie (las, Bagno, Dżungla). "
                    "WYGENEROWANE przez swiat/postacie/sklep_katalog.py ze stopnie.py i sklep_liczby.json — nie "
                    "edytować ręcznie. Status: propozycja do oceny (D-106).",
            "status": "propozycja", "wersja": 1, "umowa": UMOWA, "statystyki": STATYSTYKI, "sloty": SLOTY,
            "stopnie": L["stopnie"], "klasy": klasy, "przedmioty": przedmioty}


def tekst(dane):
    return json.dumps(dane, ensure_ascii=False, indent=1) + "\n"


def wczytaj():
    """Zapisany katalog (dla symulacji i testów — bez budowania modeli)."""
    return _json(WYNIK)


def _stat(d):
    nazwy = dict(STATYSTYKI)
    czesci = []
    for k, _ in STATYSTYKI:
        if k in d:
            czesci.append("Blok +%g pp" % round(d[k] * 100, 2) if k == "tarcza" else "%s +%g" % (nazwy[k], d[k]))
    return " · ".join(czesci).replace(".", ",") or "—"


def markdown(dane):
    """Tabele katalogu do SKLEP_PRZEDMIOTY.md (z zapisanego albo świeżego katalogu)."""
    nazwy_klas = {"wojownik": "Wojownik", "zwiadowca": "Zwiadowca", "mag": "Mag"}
    stopnie_n = {s["id"]: s["nazwa"] for s in dane["stopnie"]}
    L = []
    for klasa in dane["klasy"]:
        L += ["### %s" % nazwy_klas[klasa], "",
              "| Stopień | Slot | Przedmiot (id) | Wygląd | Statystyki +0 | Za ulepszenie | Poziom | Cena |",
              "|---|---|---|---|---|---|---:|---:|"]
        for p in dane["przedmioty"]:
            if p["klasa"] != klasa:
                continue
            if not p["sprzedawany"]:
                L.append("| %s | %s | %s (`%s`) | %s | w cenie: `%s` | | | |" % (
                    stopnie_n[p["stopien"]], dane["sloty"][p["slot"]], p["nazwa"], p["id"], p["opis"], p["czesc_od"]))
                continue
            L.append("| %s | %s | %s (`%s`) | %s | %s | %s | %d | %s |" % (
                stopnie_n[p["stopien"]], dane["sloty"][p["slot"]], p["nazwa"], p["id"], p["opis"],
                ("jak dziś (wzór poziomu)" if p["podstawowy"] and not p["baza"] else _stat(p["baza"])),
                _stat(p["krok"]), p["poziom"], "od startu" if p["cena"] == 0 else "{:,}".format(p["cena"]).replace(",", " ")))
        L.append("")
    return chr(10).join(L)


def main(argv):
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    try:
        dane = zbierz()
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1
    t = tekst(dane)
    n = len(dane["przedmioty"])
    sprzed = sum(1 for p in dane["przedmioty"] if p["sprzedawany"])
    if "--md" in argv:
        print(markdown(dane))
        return 0
    if "--sprawdz" in argv:
        ok = os.path.isfile(WYNIK) and open(WYNIK, encoding="utf-8").read() == t
        print("sklep_przedmioty.json: %s (%d wpisów, %d sprzedawanych)" % ("aktualny" if ok else "NIEAKTUALNY", n, sprzed))
        return 0 if ok else 1
    with open(WYNIK, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print("zapisano swiat/postacie/sklep_przedmioty.json (%d wpisów, %d sprzedawanych)" % (n, sprzed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
