#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/cutscenka_biomu (bez Studio, bez Luau w systemie).

    python -B swiat/cutscenka_biomu/sprawdz_luau_cutscenki.py

Kod wyjścia 1 przy błędzie. Reguły:
  1–4. jak swiat/las_potwory/sprawdz_luau.py (tylko odczyt modułu): bilans bloków i nawiasów, pierwsza instrukcja =
       strażnik Studio, zakazane usługi i globalne wait( spawn( delay(;
  5.   bez rzutowań `::` i napisów z odwrotnym apostrofem (każdy plik parsuje interpreter luau_mini);
  6.   parsowanie parserem tools/walka/luau_mini.py (gdy jest);
  7.   bez położeń w kodzie: w Vector3.new / CFrame.new żadnej liczby ≥ 10 (liczby świata tylko w danych);
  8.   cudze instancje: :Destroy() tylko na własnych obiektach; SetAttribute tylko na własnym kontenerze, własnych
       ekranach, graczu (serwer: pamięć i blokada walki) i — u klienta — lokalnie na kontenerze gry biomu (mgła);
  9.   bez zapisu i sieci: żadnego DataStore, HttpService, TeleportService, MarketplaceService, InsertService;
       identyfikator dźwięku tylko z katalogu DzwiekGra (jedno złożenie adresu w kliencie).
"""
import glob
import importlib.util
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


SL = _modul("sprawdz_luau_las_potwory", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))  # tylko odczyt

WYGENEROWANY = "DaneCutscenki.luau"
SET_ATTRIBUTE = {
    "SerwerCutscenki.server.luau": {"kontener", "gracz"},
    "KlientCutscenki.client.luau": {"kontener", "ekranTla", "ekranNapisow", "gra"},
    "LogikaCutscenki.luau": set(),
}
DESTROY = {
    "SerwerCutscenki.server.luau": {"script.Parent"},
    "KlientCutscenki.client.luau": {"ekranTla", "ekranNapisow", "d"},
    "LogikaCutscenki.luau": set(),
}
ZAKAZANE = ["DataStoreService", "HttpService", "TeleportService", "MarketplaceService", "InsertService", "GetAsync",
            "PostAsync", "http://", "https://", "SetAsync", "UpdateAsync"]
ADRES_DZWIEKU = {"KlientCutscenki.client.luau": 1}


def luau_mini():
    sciezka = os.path.join(REPO, "tools", "walka")
    if not os.path.isfile(os.path.join(sciezka, "luau_mini.py")):
        return None
    if sciezka not in sys.path:
        sys.path.append(sciezka)
    try:
        import luau_mini as lm  # noqa: E402
    except Exception:  # noqa: BLE001
        return None
    return lm


def _linia(tekst, poz):
    return tekst.count("\n", 0, poz) + 1


def sprawdz_tekst(tekst, nazwa, lm=None):
    bez_kom, bez_kom_nap = SL.rozbierz(tekst)
    bledy = SL.bilans(bez_kom_nap, nazwa)
    bledy += SL.straznik(tekst, nazwa)
    bledy += SL.zakazane(bez_kom, bez_kom_nap, nazwa)
    for m in re.finditer(r"::", bez_kom_nap):
        bledy.append("%s:%d: rzutowanie `::`" % (nazwa, _linia(bez_kom_nap, m.start())))
    if "`" in bez_kom:
        bledy.append("%s:%d: napis z odwrotnym apostrofem" % (nazwa, _linia(bez_kom, bez_kom.find("`"))))
    if lm is not None:
        try:
            lm.Parser(tekst, nazwa, lm.Interpreter()).program()
        except lm.BladSkladni as e:
            bledy.append("%s: składnia (luau_mini): %s" % (nazwa, e))
    for z in ZAKAZANE:
        if z in bez_kom:
            bledy.append("%s: zakazana usługa / adres „%s”" % (nazwa, z))
    plik = os.path.basename(nazwa)
    if bez_kom.count("rbxassetid://") != ADRES_DZWIEKU.get(plik, 0):
        bledy.append("%s: rbxassetid:// występuje %d razy (dozwolone: %d — tylko dźwięk z katalogu DzwiekGra)"
                     % (nazwa, bez_kom.count("rbxassetid://"), ADRES_DZWIEKU.get(plik, 0)))
    if plik == WYGENEROWANY:
        return bledy
    for m in re.finditer(r"(?:Vector3|CFrame)\.new\(([^()]*)\)", bez_kom_nap):
        for x in re.findall(r"(?<![\w.\[])(\d+(?:\.\d+)?)(?![\w.\]])", m.group(1)):
            if float(x) >= 10:
                bledy.append("%s:%d: liczba %s w Vector3/CFrame — liczby świata tylko w danych"
                             % (nazwa, _linia(bez_kom_nap, m.start()), x))
    if plik in SET_ATTRIBUTE:
        for m in re.finditer(r"([\w.]+):SetAttribute\(", bez_kom):
            if m.group(1) not in SET_ATTRIBUTE[plik]:
                bledy.append("%s:%d: SetAttribute na %s — wolno tylko %s"
                             % (nazwa, _linia(bez_kom, m.start()), m.group(1), sorted(SET_ATTRIBUTE[plik]) or "nic"))
        for m in re.finditer(r"([\w.]+):Destroy\(\)", bez_kom):
            if m.group(1) not in DESTROY[plik]:
                bledy.append("%s:%d: %s:Destroy() — wolno tylko %s"
                             % (nazwa, _linia(bez_kom, m.start()), m.group(1), sorted(DESTROY[plik]) or "nic"))
    return bledy


def pliki_pakietu():
    return sorted(glob.glob(os.path.join(TU, "zrodla", "*.luau")))


def sprawdz_pliki(sciezki, wypisz=None):
    """→ (lista błędów, czy był parser luau_mini)."""
    wypisz = wypisz or print
    lm = luau_mini()
    if lm is None:
        wypisz("  uwaga: brak tools/walka/luau_mini.py — bez parsowania (reguła 6 pominięta)")
    bledy = []
    for s in sciezki:
        nazwa = os.path.relpath(s, REPO).replace("\\", "/")
        try:
            tekst = SL.wczytaj(s)
        except OSError as e:
            bledy.append("%s: nie mogę przeczytać (%s)" % (nazwa, e))
            continue
        bledy += sprawdz_tekst(tekst, nazwa, lm)
    return bledy, lm is not None


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    pliki = [a for a in argv if not a.startswith("--")] or pliki_pakietu()
    bledy, parser = sprawdz_pliki(pliki)
    for b in bledy:
        print("  " + b)
    print("sprawdz_luau_cutscenki: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                      " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
