#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/miasteczko_bazar_gra (bez Studio, bez Luau w systemie).

    python -B swiat/miasteczko_bazar_gra/sprawdz_luau_bazaru.py             # zrodla/*.luau tego pakietu
    python -B swiat/miasteczko_bazar_gra/sprawdz_luau_bazaru.py plik.luau …  # wybrane pliki

Kod wyjścia 1 przy błędzie. Reguły:
  1–4. jak swiat/las_potwory/sprawdz_luau.py (ten sam rozbiór komentarzy i napisów, tylko odczyt modułu): bilans
       bloków i nawiasów, pierwsza instrukcja = strażnik Studio, zakazane PathfindingService / Lighting / loadstring /
       getfenv / setfenv / InvokeClient i globalne wait( spawn( delay(;
  5.   bez rzutowań `::` i napisów z odwrotnym apostrofem (wtedy każdy plik parsuje interpreter luau_mini);
  6.   parsowanie parserem tools/walka/luau_mini.py, gdy jest (plik innego agenta, nieśledzony w git — gdy go nie ma,
       reguła 6 jest pomijana z uwagą);
  7.   bez liczb położeń w kodzie: literał dziesiętny ≥ 100 (bez wykładnika) poza wygenerowanym DaneBazaru.luau to
       błąd — położenia są tylko w danych (znaczniki.json → dane.py);
  8.   cudze instancje: SetAttribute tylko na kontenerze pakietu i na graczu (serwer), na kontenerze (klient);
       klient zmienia w cudzych częściach wyłącznie LocalTransparencyModifier (kłódka lochów, tylko u siebie);
       :Destroy() poza własnymi obiektami — tylko script.Parent:Destroy() w strażniku serwera.
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
    """Moduł z podanego pliku pod własną nazwą (bez dopisywania cudzych folderów do sys.path — tam jest inny zbuduj.py)."""
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


SL = _modul("sprawdz_luau_las_potwory", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))  # tylko odczyt

WYGENEROWANY = "DaneBazaru.luau"
# dozwolone SetAttribute: (plik, obiekt przed dwukropkiem)
SET_ATTRIBUTE = {
    "SerwerBazaru.server.luau": {"kontener", "gracz"},
    "KlientBazaru.client.luau": {"kontener"},
    "LogikaBazaru.luau": set(),
}
DESTROY = {
    "SerwerBazaru.server.luau": {"script.Parent"},
    "KlientBazaru.client.luau": {"stary.gui", "b"},  # własne dymki (BillboardGui tworzony w tym skrypcie)
    "LogikaBazaru.luau": set(),
}


def luau_mini():
    """Moduł interpretera albo None."""
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
    # 5. składnia, którą parsuje luau_mini
    for m in re.finditer(r"::", bez_kom_nap):
        bledy.append("%s:%d: rzutowanie `::` (zamiast niego adnotacja typu przy local)" % (nazwa, _linia(bez_kom_nap, m.start())))
    if "`" in bez_kom:
        bledy.append("%s:%d: napis z odwrotnym apostrofem" % (nazwa, _linia(bez_kom, bez_kom.find("`"))))
    # 6. parser luau_mini
    if lm is not None:
        try:
            lm.Parser(tekst, nazwa, lm.Interpreter()).program()
        except lm.BladSkladni as e:
            bledy.append("%s: składnia (luau_mini): %s" % (nazwa, e))
    plik = os.path.basename(nazwa)
    if plik == WYGENEROWANY:
        return bledy
    # 7. liczby położeń
    for m in re.finditer(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", bez_kom_nap):
        if float(m.group(1)) >= 100:
            bledy.append("%s:%d: liczba %s w kodzie — położenia tylko w danych (DaneBazaru)" % (nazwa, _linia(bez_kom_nap, m.start()), m.group(1)))
    # 8. cudze instancje
    if plik in SET_ATTRIBUTE:
        for m in re.finditer(r"([\w.]+):SetAttribute\(", bez_kom):
            if m.group(1) not in SET_ATTRIBUTE[plik]:
                bledy.append("%s:%d: SetAttribute na %s — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                         sorted(SET_ATTRIBUTE[plik]) or "nic"))
        for m in re.finditer(r"([\w.]+):Destroy\(\)", bez_kom):
            if m.group(1) not in DESTROY[plik]:
                bledy.append("%s:%d: %s:Destroy() — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                     sorted(DESTROY[plik]) or "nic"))
    if plik == "KlientBazaru.client.luau":
        # jedyne przypisanie właściwości części spoza pakietu: d.LocalTransparencyModifier w pętli po Blokadzie
        for m in re.finditer(r"\bd\.(\w+)\s*=", bez_kom):
            if m.group(1) != "LocalTransparencyModifier":
                bledy.append("%s:%d: zmiana d.%s w cudzej części" % (nazwa, _linia(bez_kom, m.start()), m.group(1)))
    return bledy


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
    print("sprawdz_luau_bazaru: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                   " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
