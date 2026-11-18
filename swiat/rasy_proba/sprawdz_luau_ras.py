#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/rasy_proba (bez Studio, bez Luau w systemie).

    python -B swiat/rasy_proba/sprawdz_luau_ras.py

Reguły 1–4 z swiat/las_potwory/sprawdz_luau.py (tylko odczyt tamtego modułu): bilans bloków i nawiasów, pierwsza
instrukcja = strażnik Studio, bez PathfindingService / Lighting / loadstring / getfenv / setfenv / InvokeClient
i bez globalnych wait( spawn( delay(. Sprawdzany jest plik źródłowy i ten sam plik po wpisaniu ustawień
(tak trafia do Studio). Kod wyjścia 1 przy błędzie.
"""
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    SL = ZB.kontrola_luau()
    bledy = SL.sprawdz_pliki([ZB.SKRYPT_PLIK], wypisz=lambda t: None)
    bledy += SL.sprawdz_tekst(ZB.zrodlo_skryptu(DN.ustawienia()), "SpoczynekRas (po wpisaniu ustawień)")
    for b in bledy:
        print("BŁĄD:", b)
    print("źródła Luau wystawy ras: %s" % ("bez błędów" if not bledy else "%d błędów" % len(bledy)))
    sys.exit(1 if bledy else 0)
