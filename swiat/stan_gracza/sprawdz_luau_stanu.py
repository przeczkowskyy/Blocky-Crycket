#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/stan_gracza (bez Studio, bez Luau w systemie).

    python -B swiat/stan_gracza/sprawdz_luau_stanu.py              # zrodla/*.luau tego pakietu
    python -B swiat/stan_gracza/sprawdz_luau_stanu.py plik.luau …   # wybrane pliki

Kod wyjścia 1 przy błędzie. Reguły:
  1–4. jak swiat/las_potwory/sprawdz_luau.py (tylko odczyt modułu): bilans bloków i nawiasów, pierwsza instrukcja =
       strażnik Studio, zakazane PathfindingService / Lighting / loadstring / getfenv / setfenv / InvokeClient
       i globalne wait( spawn( delay(;
  5.   bez rzutowań `::` i napisów z odwrotnym apostrofem; każdy plik parsuje interpreter tools/walka/luau_mini.py;
  6.   cudze instancje: SetAttribute tylko na kontenerze pakietu, graczu (serwer) i własnym GUI (klient);
       :Destroy() tylko na własnych obiektach (kontener poza Studio, własne dźwięki i baner);
  7.   LogikaStanu.luau jest czysta: bez game, workspace, Instance, task, os, wait, require, print;
  8.   bez ścieżek lokalnych (dysk, katalog użytkownika) i adresów sieci (http, https).
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

SET_ATTRIBUTE = {
    "SerwerStanu.server.luau": {"kontener", "gracz"},
    "KlientStanu.client.luau": {"kontener", "gui"},
    "LogikaStanu.luau": set(),
    "DaneStanu.luau": set(),
}
DESTROY = {
    "SerwerStanu.server.luau": {"script.Parent"},
    "KlientStanu.client.luau": {"s", "gui"},
    "LogikaStanu.luau": set(),
    "DaneStanu.luau": set(),
}
CZYSTA = "LogikaStanu.luau"
ZAKAZANE_W_CZYSTEJ = ["workspace", "Instance", "task.", "os.", "require", "print(", "warn("]
# ścieżki składane z kawałków, żeby ten plik sam nie zawierał tego, czego zabrania
ZAKAZANE_ZASOBY = ["http" + "://", "https" + "://", "C:" + "\\", "/" + "Users/", "InsertService", "MarketplaceService",
                   "GetAsync", "PostAsync"]


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
    for z in ZAKAZANE_ZASOBY:
        if z in tekst:
            bledy.append("%s: zakazany zasób / ścieżka „%s”" % (nazwa, z))
    plik = os.path.basename(nazwa)
    if plik == CZYSTA:
        # strażnik Studio (pierwsza instrukcja) używa game — reszta modułu już nie
        reszta = bez_kom_nap.split("local L = {}", 1)[-1]
        for z in ZAKAZANE_W_CZYSTEJ + ["game"]:
            if re.search(r"(?<![\w.])%s" % re.escape(z), reszta):
                bledy.append("%s: czysta logika używa „%s”" % (nazwa, z))
    if plik in SET_ATTRIBUTE:
        for m in re.finditer(r"([\w.]+):SetAttribute\(", bez_kom):
            if m.group(1) not in SET_ATTRIBUTE[plik]:
                bledy.append("%s:%d: SetAttribute na %s — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                         sorted(SET_ATTRIBUTE[plik]) or "nic"))
        for m in re.finditer(r"([\w.]+):Destroy\(\)", bez_kom):
            if m.group(1) not in DESTROY[plik]:
                bledy.append("%s:%d: %s:Destroy() — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                     sorted(DESTROY[plik]) or "nic"))
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
    print("sprawdz_luau_stanu: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                  " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
