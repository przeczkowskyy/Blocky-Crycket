#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/las_pas_gra (bez Studio, bez Luau w systemie).

    python -B swiat/las_pas_gra/sprawdz_luau_pasa.py             # zrodla/*.luau tego pakietu
    python -B swiat/las_pas_gra/sprawdz_luau_pasa.py plik.luau …  # wybrane pliki

Kod wyjścia 1 przy błędzie. Reguły (1–4 z swiat/las_potwory/sprawdz_luau.py — ten sam rozbiór komentarzy i napisów):
  1. bilans bloków (function / do / repeat / if … end / until) i nawiasów (), {}, [];
  2. pierwsza instrukcja to strażnik Studio;
  3. zakazane: PathfindingService, loadstring, getfenv, setfenv, InvokeClient, globalne wait( spawn( delay(;
  4. Lighting: tylko w MglaPasa i tylko jako game:GetService("Lighting") z jednym wywołaniem
     :FindFirstChildOfClass("Atmosphere") — bez przypisań do Lighting i bez tworzenia obiektów (wspólnego Lighting
     nie wolno zmieniać; mgła zmienia lokalnie Atmosphere jak MglaLasu starego lasu);
  5. bez rzutowań `::` i napisów z odwrotnym apostrofem — wtedy każdy plik da się sparsować interpreterem
     tools/walka/luau_mini.py (podzbiór Luau w Pythonie, nieśledzony jeszcze w git; gdy go nie ma, reguła 6 jest
     pomijana z uwagą);
  6. parsowanie każdego pliku parserem luau_mini (prawdziwa kontrola składni, nie tylko bilans).
"""
import glob
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, os.path.join(REPO, "swiat", "las_potwory"))
import sprawdz_luau as SL  # noqa: E402

ZAKAZANE_NAZWY = ["PathfindingService", "loadstring", "getfenv", "setfenv", "InvokeClient"]
PLIK_MGLY = "MglaPasa.client.luau"


def luau_mini():
    """Moduł interpretera albo None (plik nie jest w git i może zniknąć — wtedy tylko reguły 1–5)."""
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


def sprawdz_tekst(tekst, nazwa, lm=None):
    bez_kom, bez_kom_nap = SL.rozbierz(tekst)
    bledy = SL.bilans(bez_kom_nap, nazwa)
    bledy += SL.straznik(tekst, nazwa)
    for slowo in ZAKAZANE_NAZWY:
        for m in re.finditer(r"\b%s\b" % slowo, bez_kom):
            bledy.append("%s:%d: zakazane `%s`" % (nazwa, bez_kom.count("\n", 0, m.start()) + 1, slowo))
    for slowo in SL.ZAKAZANE_WYWOLANIA:
        for m in re.finditer(r"(?<![.:\w])%s\s*\(" % slowo, bez_kom_nap):
            bledy.append("%s:%d: globalne `%s(` — użyj task.%s" % (nazwa, bez_kom_nap.count("\n", 0, m.start()) + 1, slowo, slowo))
    # 4. Lighting
    trafienia = [m.start() for m in re.finditer(r"\bLighting\b", bez_kom)]
    if os.path.basename(nazwa) == PLIK_MGLY:
        dozwolone = [m.start() + len('game:GetService("') for m in re.finditer(r'game:GetService\("Lighting"\)', bez_kom)]
        if sorted(trafienia) != sorted(dozwolone) or len(dozwolone) != 1:
            bledy.append("%s: Lighting tylko raz, jako game:GetService(\"Lighting\")" % nazwa)
        m = re.search(r'local\s+(\w+)\s*=\s*game:GetService\("Lighting"\)', bez_kom)
        if m:
            zm = m.group(1)
            uzycia = re.findall(r"\b%s\b\s*([.:=\[])\s*([^\n]{0,40})" % zm, bez_kom[m.end():])
            for znak, reszta in uzycia:
                if not (znak == ":" and reszta.startswith('FindFirstChildOfClass("Atmosphere")')):
                    bledy.append("%s: %s%s… — z Lighting wolno tylko FindFirstChildOfClass(\"Atmosphere\")" % (nazwa, zm, znak))
        if re.search(r'Instance\.new\(\s*"(Atmosphere|Sky|BloomEffect|ColorCorrectionEffect)"', bez_kom):
            bledy.append("%s: tworzenie obiektów Lighting jest zakazane" % nazwa)
    else:
        for poz in trafienia:
            bledy.append("%s:%d: Lighting poza MglaPasa" % (nazwa, bez_kom.count("\n", 0, poz) + 1))
    # 5. składnia, którą parsuje luau_mini
    for m in re.finditer(r"::", bez_kom_nap):
        bledy.append("%s:%d: rzutowanie `::` (zamiast niego adnotacja typu przy local)" % (nazwa, bez_kom_nap.count("\n", 0, m.start()) + 1))
    if "`" in bez_kom.replace("``", ""):
        k = bez_kom.find("`")
        bledy.append("%s:%d: napis z odwrotnym apostrofem" % (nazwa, bez_kom.count("\n", 0, k) + 1))
    # 6. parser luau_mini
    if lm is not None:
        try:
            lm.Parser(tekst, nazwa, lm.Interpreter()).program()
        except lm.BladSkladni as e:
            bledy.append("%s: składnia (luau_mini): %s" % (nazwa, e))
    return bledy


def sprawdz_pliki(sciezki, wypisz=None):
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
    pliki = [a for a in argv if not a.startswith("--")] or sorted(glob.glob(os.path.join(TU, "zrodla", "*.luau")))
    if not pliki:
        print("BŁĄD: brak plików do sprawdzenia")
        return 1
    bledy, parser = sprawdz_pliki(pliki)
    for b in bledy:
        print("  " + b)
    print("sprawdz_luau_pasa: %d plików, %s%s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                 " (z parserem luau_mini)" if parser else " (bez parsera)"))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
