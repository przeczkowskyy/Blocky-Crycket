#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bronie Maga i Zwiadowcy (pula Lv 1–10, D-142 / D-167) jako PRZEDMIOTY GRY -> bronie_klas_sklep.json.
Status: propozycja; LICZBY ROBOCZE (cena, wymagany poziom, statystyki) — do zmiany kalkulatorem balansu.

    python -B swiat/postacie/bronie_klas_sklep.py             # zapisuje bronie_klas_sklep.json
    python -B swiat/postacie/bronie_klas_sklep.py --sprawdz   # kod 1, gdy plik jest nieaktualny albo dane się nie zgadzają

Drugi katalog obok sklep_przedmioty.json (ten zostaje bez zmian: jego testy i symulacja przejścia liczą komplety
stopni, a pula idzie według poziomu). Wpis ma te same pola co katalog sklepu (umowa: sklep_przedmioty.json →
„umowa”), plus:
  - pula = "Lv 1-10"; akcesorium = nazwa modelu w ReplicatedStorage/BronieKlas (Accessory z bronie_klas_roblox.py);
  - ikona_roblox = obraz z ikony_broni.json (wgrany 27.11.2026); chwyt, lapa — z bronie_klas.py;
  - czesci = [] — broń nie ma brył przymierzalni; na postaci zakłada się akcesorium z BronieKlas.
Stopień: cała pula leży w stopniu leśnym (nr 1) — kowal i okna liczą stopnie (zakładanie po kupnie, zakładki), a
w jednym stopniu kolejność idzie według wymaganego poziomu.

Liczby robocze: prosta interpolacja po poziomie między bronią startową (Lv 1, Broń +0), leśną (Lv 7: Broń +2,
350 Rybek, Mag 500) i bagienną (Lv 15: Broń +4, 850 Rybek, Mag 1100) z katalogu sklepu; Mag dostaje Inteligencję
jak jego kostury, Zwiadowca Szczęście jak jego łuki; waga ulepszeń jak u broni klasy (Mag 1,75, Zwiadowca 1).
Czyta: bronie_klas.py (BRONIE, ZESTAWY), ikony_broni.json, sklep_przedmioty.json (stopnie, statystyki). Bez Blendera.
"""
import json
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

WYNIK = os.path.join(TU, "bronie_klas_sklep.json")
IKONY = os.path.join(TU, "ikony_broni.json")
KATALOG_SKLEPU = os.path.join(TU, "sklep_przedmioty.json")
STOPIEN = "las"
KONTENER = "ReplicatedStorage/BronieKlas"

# LICZBY ROBOCZE: id -> (wymagany poziom, cena w Rybkach, baza +0, krok za ulepszenie)
LICZBY = {
    "mag_rozdzka_z_patyka": (1, 50, {"bron": 1}, {"bron": 1, "Intelligence": 1}),
    "mag_kostur_z_miotly": (3, 175, {"bron": 1, "Intelligence": 1}, {"bron": 1, "Intelligence": 1}),
    "mag_walek_czarodziejski": (5, 325, {"bron": 2, "Intelligence": 1}, {"bron": 1, "Intelligence": 1}),
    "mag_rozdzka_ze_swieczki": (7, 500, {"bron": 2, "Intelligence": 2}, {"bron": 1, "Intelligence": 1}),
    "mag_kostur_ucznia": (10, 725, {"bron": 3, "Intelligence": 3}, {"bron": 1, "Intelligence": 1}),
    "zwiad_proca_z_galezi": (1, 35, {"bron": 1}, {"bron": 1}),
    "zwiad_luk_z_wieszaka": (3, 125, {"bron": 1, "Luck": 1}, {"bron": 1}),
    "zwiad_noz_do_masla": (5, 225, {"bron": 2, "Luck": 1}, {"bron": 1}),
    "zwiad_sztylet_z_szyszki": (7, 350, {"bron": 2, "Luck": 2}, {"bron": 1}),
    "zwiad_luk_tropiciela": (10, 550, {"bron": 3, "Luck": 2}, {"bron": 1}),
}
WAGA = {"mag": 1.75, "zwiadowca": 1}
LAPA = {"luk": "lewa"}
ZACZEP = {"prawa": "RightGripAttachment", "lewa": "LeftGripAttachment"}


class BladDanych(Exception):
    pass


def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def _bronie():
    """(id, nazwa, klasa, chwyt, plik ikony, zestaw) z bronie_klas.BRONIE — bez importu budowania modeli."""
    from swiat.postacie import bronie_klas as BK
    return list(BK.BRONIE), dict(BK.ZESTAWY)


def zbierz():
    bronie, zestawy = _bronie()
    ikony = _json(IKONY)["ikony"]
    KS = _json(KATALOG_SKLEPU)
    nr = {s["id"]: s["nr"] for s in KS["stopnie"]}
    staty = {s[0] for s in KS["statystyki"]}
    if STOPIEN not in nr:
        raise BladDanych("stopień %s spoza katalogu sklepu" % STOPIEN)
    zajete = {p["id"] for p in KS["przedmioty"]}
    ids = [b[0] for b in bronie]
    if sorted(ids) != sorted(LICZBY):
        raise BladDanych("LICZBY ≠ bronie_klas.BRONIE: brak %s, nadmiar %s"
                         % (sorted(set(ids) - set(LICZBY)), sorted(set(LICZBY) - set(ids))))
    przedmioty = []
    for pid, nazwa, klasa, chwyt, plik_ikony, zestaw in bronie:
        if pid in zajete:
            raise BladDanych("przedmiot %s już jest w sklep_przedmioty.json" % pid)
        ik = ikony.get(plik_ikony)
        if not ik or not ik.get("obraz") or ik.get("model") != pid:
            raise BladDanych("przedmiot %s: brak wgranej ikony %s w ikony_broni.json" % (pid, plik_ikony))
        poziom, cena, baza, krok = LICZBY[pid]
        for k in list(baza) + list(krok):
            if k not in staty:
                raise BladDanych("przedmiot %s: nieznana statystyka %s" % (pid, k))
        lapa = LAPA.get(chwyt, "prawa")
        przedmioty.append({
            "id": pid, "nazwa": nazwa,
            "opis": "broń puli Lv 1-10 (D-142, D-167): model z ikony, %s" % ("przedmiot zestawu" if zestaw else "pojedyncza"),
            "klasa": klasa, "stopien": STOPIEN, "nr_stopnia": nr[STOPIEN], "slot": "Weapon", "sprzedawany": True,
            "cena": cena, "poziom": poziom, "podstawowy": False, "waga": WAGA[klasa], "baza": baza, "krok": krok,
            "kategoria": "Weapons", "cialo": "dowolne", "klasy": [klasa], "czesc_od": None, "ukrywa": [],
            "zestaw": zestawy[klasa] if zestaw else None, "czesci": [],
            "ikona": "assets/processed/%s.png" % plik_ikony,
            "pula": "Lv 1-10", "akcesorium": pid, "chwyt": chwyt, "lapa": lapa, "zaczep": ZACZEP[lapa],
            "ikona_roblox": "rbxassetid://%s" % ik["obraz"],
        })
    for klasa in WAGA:
        wl = sorted((p for p in przedmioty if p["klasa"] == klasa), key=lambda p: p["poziom"])
        for a, b in zip(wl, wl[1:]):
            moc_a, moc_b = sum(a["baza"].values()), sum(b["baza"].values())
            if not (b["poziom"] > a["poziom"] and b["cena"] > a["cena"] and moc_b > moc_a):
                raise BladDanych("klasa %s: %s → %s — poziom, cena i statystyki mają rosnąć" % (klasa, a["id"], b["id"]))
    return {"opis": "Bronie Maga i Zwiadowcy (pula Lv 1-10) jako przedmioty gry — drugi katalog obok "
                    "sklep_przedmioty.json, te same pola wpisu. WYGENEROWANE przez swiat/postacie/bronie_klas_sklep.py "
                    "— nie edytować ręcznie. Status: propozycja, LICZBY ROBOCZE.",
            "status": "propozycja", "wersja": 1, "kontener": KONTENER, "przedmioty": przedmioty}


def tekst(dane):
    return json.dumps(dane, ensure_ascii=False, indent=1) + "\n"


def wczytaj():
    """Zapisany katalog broni (kowal, przymierzalnia) — pusta lista, gdy pliku nie ma."""
    if not os.path.isfile(WYNIK):
        return {"przedmioty": []}
    return _json(WYNIK)


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
    if "--sprawdz" in argv:
        ok = os.path.isfile(WYNIK) and open(WYNIK, encoding="utf-8").read() == t
        print("bronie_klas_sklep.json: %s (%d broni)" % ("aktualny" if ok else "NIEAKTUALNY", len(dane["przedmioty"])))
        return 0 if ok else 1
    with open(WYNIK, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)
    print("zapisano swiat/postacie/bronie_klas_sklep.json (%d broni)" % len(dane["przedmioty"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
