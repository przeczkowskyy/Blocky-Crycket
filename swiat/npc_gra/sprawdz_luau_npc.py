#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola statyczna źródeł Luau pakietu swiat/npc_gra (bez Studio, bez Luau w systemie).

    python -B swiat/npc_gra/sprawdz_luau_npc.py

Reguły 1–4 z swiat/las_potwory/sprawdz_luau.py (tylko odczyt tamtego modułu): bilans bloków i nawiasów, pierwsza
instrukcja = strażnik Studio, bez PathfindingService / Lighting / loadstring / getfenv / setfenv / InvokeClient
i bez globalnych wait( spawn( delay(. Sprawdzane są pliki pakietu (logika, rig, klient, serwer, dane i rigi) oraz
kod, który budowniczy wysyła do Studio (szablony zbuduj.py po wstawieniu wartości — tylko bilans). Kod 1 przy błędzie.
"""
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)
import dane as DN  # noqa: E402
import zbuduj as ZB  # noqa: E402


def kody_budowniczego(U):
    """Kod wysyłany do Studio z przykładowymi wartościami (nazwa, tekst) — do kontroli bilansu."""
    w = dict(MIEJSCE="1", KONTENER=U["kontener"])
    kotwica = ZB.kotwica_luau(U, "golem", "proba", (1, 2, 3), (4, 5), "workspace", skala=1.5, rola="Rola")
    return [
        ("START", ZB.wstaw(ZB.START, KOTWICE=ZB.FOLDER_KOTWIC, ZRODLO="x", CZAS="x", SKROT="x", WYLACZNIK=U["wylacznik"],
                           SYGNALY='"A", "B"', **w)),
        ("ZRODLO", ZB.wstaw(ZB.ZRODLO, RODZIC="Moduly/Rigi", NAZWA="X", KLASA="ModuleScript", KONTEKST="Legacy",
                            TEKST=DN.luau("return 1\n"), **w)),
        ("KONIEC", ZB.wstaw(ZB.KONIEC, **w)), ("USUN", ZB.wstaw(ZB.USUN, **w)),
        ("BEZ_KOTWICY", ZB.wstaw(ZB.BEZ_KOTWICY, KOTWICE=ZB.FOLDER_KOTWIC, NAZWA="Kotwica_x", **w)),
        ("KOTWICA", kotwica), ("STAN", ZB.kod_stanu(U)), ("TRENERZY", ZB.kod_trenerow(U, w)[1]),
        ("BEZ_TRENEROW", ZB.wstaw(ZB.BEZ_TRENEROW, KOTWICE=ZB.FOLDER_KOTWIC, NAZWY='"Kotwica_x"', **w)),
    ]


def sprawdz():
    SL = ZB.kontrola_luau()
    bledy = SL.sprawdz_pliki(ZB.pliki_luau(), wypisz=lambda t: None)
    for nazwa, kod in kody_budowniczego(DN.ustawienia()):
        if "__" in kod.replace("__index", ""):
            bledy.append("%s: niewstawione pole szablonu" % nazwa)
        bledy += SL.sprawdz_tekst(kod, "zbuduj.py:" + nazwa, pelne=False)
    return bledy


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    bledy = sprawdz()
    for b in bledy:
        print("BŁĄD:", b)
    print("źródła Luau NPC (%d plików i kod budowniczego): %s" % (len(ZB.pliki_luau()), "bez błędów" if not bledy else "%d błędów" % len(bledy)))
    sys.exit(1 if bledy else 0)
