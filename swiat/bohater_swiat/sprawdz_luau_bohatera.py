#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/bohater_swiat (bez Studio, bez Luau w systemie).

    python -B swiat/bohater_swiat/sprawdz_luau_bohatera.py             # zrodla/*.luau tego pakietu
    python -B swiat/bohater_swiat/sprawdz_luau_bohatera.py plik.luau …  # wybrane pliki

Kod wyjścia 1 przy błędzie. Reguły:
  1–4. jak swiat/las_potwory/sprawdz_luau.py (tylko odczyt modułu): bilans bloków i nawiasów, pierwsza instrukcja =
       strażnik Studio, zakazane PathfindingService / Lighting / loadstring / getfenv / setfenv / InvokeClient
       i globalne wait( spawn( delay(;
  5.   bez rzutowań `::` i napisów z odwrotnym apostrofem (każdy plik parsuje interpreter luau_mini);
  6.   parsowanie parserem tools/walka/luau_mini.py;
  7.   bez położeń w kodzie: w Vector3.new / CFrame.new żadnej liczby ≥ 10 (liczby tylko w danych);
  8.   cudze instancje: SetAttribute tylko na własnym kontenerze i własnym modelu; :Destroy() tylko na własnych
       obiektach (lista dozwolonych nazw na plik);
  9.   bez zasobów spoza pakietu: żadnego rbxassetid://, InsertService, MarketplaceService, HttpService, adresów http,
       DataStore, TeleportService; bez zasobów Animation (LoadAnimation, AnimationTrack, KeyframeSequence) — ruch
       to własne klipy z danych;
 10.   bohater nie łączy się z postacią: klient nie tworzy Weld / WeldConstraint / Motor6D / żadnego Constraint
       (Instance.new) i nie zmienia właściwości ruchu postaci (WalkSpeed, JumpPower, JumpHeight, HipHeight,
       AutoRotate, PlatformStand, Anchored postaci).
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

WYGENEROWANY = "DaneBohatera.luau"
SET_ATTRIBUTE = {
    "SerwerBohatera.server.luau": {"kontener"},
    "KlientBohatera.client.luau": {"kontener", "model"},
    "LogikaBohatera.luau": set(),
}
DESTROY = {
    "SerwerBohatera.server.luau": {"script.Parent"},
    "KlientBohatera.client.luau": {"model", "b.model"},
    "LogikaBohatera.luau": set(),
}
ZAKAZANE_ZASOBY = ["rbxassetid://", "InsertService", "MarketplaceService", "HttpService", "GetAsync", "PostAsync",
                   "http://", "https://", "DataStoreService", "TeleportService"]
ZAKAZANE_ANIMACJE = ["LoadAnimation", "AnimationTrack", "KeyframeSequence", "AnimationController"]
ZAKAZANE_TWORZENIE = re.compile(r'Instance\.new\(\s*"(Weld|WeldConstraint|Motor6D|\w*Constraint|Humanoid|Animator)"')
RUCH_POSTACI = re.compile(r"\.(WalkSpeed|JumpPower|JumpHeight|HipHeight|AutoRotate|PlatformStand|Sit)\s*=[^=]")
KOTWICA = re.compile(r"([\w.]+)\.Anchored\s*=[^=]")
KOTWICA_DOZWOLONA = {"korzen"}


def luau_mini():
    sciezka = os.path.join(REPO, "tools", "walka")
    if not os.path.isfile(os.path.join(sciezka, "luau_mini.py")):
        return None
    if sciezka not in sys.path:
        sys.path.append(sciezka)
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
        if z in bez_kom:
            bledy.append("%s: zakazany zasób / usługa „%s”" % (nazwa, z))
    for z in ZAKAZANE_ANIMACJE:
        if re.search(r"\b%s\b" % z, bez_kom_nap):
            bledy.append("%s: zasób Animation „%s” — ruch tylko z własnych klipów" % (nazwa, z))
    plik = os.path.basename(nazwa)
    if plik == WYGENEROWANY:
        return bledy
    for m in re.finditer(r"(?:Vector3|CFrame)\.new\(([^()]*)\)", bez_kom_nap):
        for x in re.findall(r"(?<![\w.\[])(\d+(?:\.\d+)?)(?![\w.\]])", m.group(1)):  # bez indeksów w[10]
            if float(x) >= 10:
                bledy.append("%s:%d: liczba %s w Vector3/CFrame — liczby tylko w danych" % (nazwa, _linia(bez_kom_nap, m.start()), x))
    for m in ZAKAZANE_TWORZENIE.finditer(bez_kom):
        bledy.append("%s:%d: Instance.new(\"%s\") — bohater nie łączy się z postacią i nie ma Humanoida"
                     % (nazwa, _linia(bez_kom, m.start()), m.group(1)))
    for m in RUCH_POSTACI.finditer(bez_kom_nap):
        bledy.append("%s:%d: zmiana %s — pakiet nie zmienia ruchu postaci" % (nazwa, _linia(bez_kom_nap, m.start()), m.group(1)))
    for m in KOTWICA.finditer(bez_kom_nap):
        if m.group(1) not in KOTWICA_DOZWOLONA:
            bledy.append("%s:%d: %s.Anchored — kotwiczyć wolno tylko korzeń własnego modelu"
                         % (nazwa, _linia(bez_kom_nap, m.start()), m.group(1)))
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
    print("sprawdz_luau_bohatera: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                     " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
