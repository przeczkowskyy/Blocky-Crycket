#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/wskazowki_gry (bez Studio, bez Luau w systemie).

    python -B swiat/wskazowki_gry/sprawdz_luau_wskazowek.py             # zrodla/*.luau tego pakietu
    python -B swiat/wskazowki_gry/sprawdz_luau_wskazowek.py plik.luau …  # wybrane pliki

Kod wyjścia 1 przy błędzie. Reguły:
  1–4. jak swiat/las_potwory/sprawdz_luau.py (tylko odczyt modułu): bilans bloków i nawiasów, pierwsza instrukcja =
       strażnik Studio, zakazane PathfindingService / Lighting / loadstring / getfenv / setfenv / InvokeClient
       i globalne wait( spawn( delay(;
  5.   bez rzutowań `::` i napisów z odwrotnym apostrofem; parsowanie parserem tools/walka/luau_mini.py (gdy jest);
  6.   bez liczb ≥ 100 w kodzie (położenia i rozmiary tylko w danych);
  7.   cudze instancje tylko do odczytu: SetAttribute wyłącznie na własnym kontenerze, :Destroy() tylko własnych
       obiektów, bez FireServer / InvokeServer (klient niczego nie wysyła), bez Enabled = na cudzych ekranach;
  8.   bez zasobów spoza Robloxa (rbxassetid://, InsertService, MarketplaceService, http).
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

WYGENEROWANY = "DaneWskazowek.luau"
SET_ATTRIBUTE = {"kontener"}
DESTROY = {"gui", "znacznik"}
WLASNE_ENABLED = {"znacznik"}  # Enabled = tylko na własnym BillboardGui
ZAKAZANE = ["rbxassetid://", "InsertService", "MarketplaceService", "GetAsync", "PostAsync", "http://", "https://",
            "FireServer", "InvokeServer"]


def luau_mini():
    sciezka = os.path.join(REPO, "tools", "walka")
    if not os.path.isfile(os.path.join(sciezka, "luau_mini.py")):
        return None
    if sciezka not in sys.path:
        sys.path.insert(0, sciezka)
    try:
        import luau_mini  # noqa: E402
    except Exception:  # noqa: BLE001
        return None
    return luau_mini


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
            bledy.append("%s: zakazane „%s”" % (nazwa, z))
    if os.path.basename(nazwa) == WYGENEROWANY:
        return bledy
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", bez_kom_nap):
        if float(m.group(1)) >= 100:
            bledy.append("%s:%d: liczba %s w kodzie — tylko w danych" % (nazwa, _linia(bez_kom_nap, m.start()), m.group(1)))
    for m in re.finditer(r"([\w.]+):SetAttribute\(", bez_kom):
        if m.group(1) not in SET_ATTRIBUTE:
            bledy.append("%s:%d: SetAttribute na %s — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                     sorted(SET_ATTRIBUTE)))
    for m in re.finditer(r"([\w.]+):Destroy\(\)", bez_kom):
        if m.group(1) not in DESTROY:
            bledy.append("%s:%d: %s:Destroy() — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1), sorted(DESTROY)))
    for m in re.finditer(r"([\w.]+)\.Enabled\s*=(?!=)", bez_kom):
        if m.group(1) not in WLASNE_ENABLED:
            bledy.append("%s:%d: %s.Enabled = — cudzych ekranów nie przełączamy" % (nazwa, _linia(bez_kom, m.start()), m.group(1)))
    return bledy


def sprawdz_pliki(sciezki, wypisz=None):
    """→ (lista błędów, czy był parser luau_mini)."""
    wypisz = wypisz or print
    lm = luau_mini()
    if lm is None:
        wypisz("  uwaga: brak tools/walka/luau_mini.py — bez parsowania")
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


def pliki_pakietu():
    return sorted(glob.glob(os.path.join(TU, "zrodla", "*.luau")))


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    pliki = [a for a in argv if not a.startswith("--")] or pliki_pakietu()
    if not pliki:
        print("BŁĄD: brak plików do sprawdzenia")
        return 1
    bledy, parser = sprawdz_pliki(pliki)
    for b in bledy:
        print("  " + b)
    print("sprawdz_luau_wskazowek: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                      " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
