#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/pety_proba (bez Studio, bez Luau w systemie).

    python -B swiat/pety_proba/sprawdz_luau_petow.py              # zrodla/*.luau i zrodla/rigi/*.luau
    python -B swiat/pety_proba/sprawdz_luau_petow.py plik.luau …   # wybrane pliki

Kod wyjścia 1 przy błędzie. Reguły:
  1–4. jak swiat/las_potwory/sprawdz_luau.py (tylko odczyt modułu): bilans bloków i nawiasów, pierwsza instrukcja =
       strażnik Studio, zakazane PathfindingService / Lighting / loadstring / getfenv / setfenv / InvokeClient
       i globalne wait( spawn( delay(;
  5.   bez rzutowań `::` i napisów z odwrotnym apostrofem; każdy plik parsuje interpreter tools/walka/luau_mini.py;
  6.   cudze instancje: SetAttribute tylko na kontenerze, graczu (serwer) i zdarzeniu okien bazaru (klient — wyłącza
       dymek „w budowie” dla zagrody); :Destroy() tylko na własnych obiektach;
  7.   LogikaPetow.luau jest czysta: bez game, workspace, Instance, task, os, require, print, warn;
  8.   bez ścieżek lokalnych, adresów sieci, zapisu (DataStore) i zakupów za Robuxy (MarketplaceService,
       PromptProductPurchase, ProcessReceipt — jajka tylko za Złoto, D-086);
  9.   klient nie wysyła liczb ani cen: FireServer tylko z poleceniem i id peta / tak-nie; Złota nie pisze nikt
       z pakietu (Gold zmienia wyłącznie StanGracza).
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
    "SerwerPetow.server.luau": {"kontener", "gracz"},
    "KlientPetow.client.luau": {"kontener", "okna"},
}
DESTROY = {
    "SerwerPetow.server.luau": {"script.Parent"},
    "KlientPetow.client.luau": {"s", "kula", "slup", "t.model", "z.model", "em", "pm", "napis", "m", "d"},
}
CZYSTA = "LogikaPetow.luau"
ZAKAZANE_W_CZYSTEJ = ["workspace", "Instance", "task.", "os.", "require", "print(", "warn("]
# ścieżki i nazwy składane z kawałków, żeby ten plik sam nie zawierał tego, czego zabrania
ZAKAZANE_ZASOBY = ["http" + "://", "https" + "://", "C:" + "\\", "/" + "Users/", "Insert" + "Service",
                   "Marketplace" + "Service", "Prompt" + "ProductPurchase", "Process" + "Receipt", "Data" + "Store",
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
        reszta = bez_kom_nap.split("local L = {}", 1)[-1]
        for z in ZAKAZANE_W_CZYSTEJ + ["game"]:
            if re.search(r"(?<![\w.])%s" % re.escape(z), reszta):
                bledy.append("%s: czysta logika używa „%s”" % (nazwa, z))
    dozw_set = SET_ATTRIBUTE.get(plik, set())
    dozw_destroy = DESTROY.get(plik, set())
    for m in re.finditer(r"([\w.]+):SetAttribute\(", bez_kom):
        if m.group(1) not in dozw_set:
            bledy.append("%s:%d: SetAttribute na %s — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                     sorted(dozw_set) or "nic"))
    for m in re.finditer(r"([\w.]+):Destroy\(\)", bez_kom):
        if m.group(1) not in dozw_destroy:
            bledy.append("%s:%d: %s:Destroy() — wolno tylko %s" % (nazwa, _linia(bez_kom, m.start()), m.group(1),
                                                                 sorted(dozw_destroy) or "nic"))
    # Złoto zmienia wyłącznie StanGracza
    if re.search(r'SetAttribute\(\s*"Gold"', bez_kom) or re.search(r"SetAttribute\(\s*S\.atrybut_zlota", bez_kom):
        bledy.append("%s: pakiet petów nie pisze Złota (robi to StanGracza)" % nazwa)
    if plik.endswith(".client.luau"):
        for m in re.finditer(r"FireServer\(([^)]*)\)", bez_kom):
            argi = [a.strip() for a in m.group(1).split(",")]
            if not argi or not re.match(r'^"\w+"$', argi[0]):
                bledy.append("%s:%d: FireServer bez stałego polecenia" % (nazwa, _linia(bez_kom, m.start())))
            elif len(argi) > 2:
                bledy.append("%s:%d: FireServer z więcej niż jednym argumentem" % (nazwa, _linia(bez_kom, m.start())))
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
    return sorted(glob.glob(os.path.join(TU, "zrodla", "*.luau")) + glob.glob(os.path.join(TU, "zrodla", "rigi", "*.luau")))


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
    print("sprawdz_luau_petow: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                  " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
