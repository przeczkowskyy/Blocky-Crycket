#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generuje modul Luau src/server/Walka/Dane.luau z jednego zrodla danych tools/walka/dane_walki.json.

    python -B tools/walka/generuj_dane.py            # zapisuje Dane.luau
    python -B tools/walka/generuj_dane.py --sprawdz  # tylko sprawdza, czy Dane.luau jest aktualny (kod 1, gdy nie)

Dane sa w jednym miejscu, wiec Luau i Python nie moga sie rozjechac: Python czyta JSON wprost, a Luau dostaje
wierna kopie jako tabele. Liczby zapisujemy w najkrotszej postaci, ktora po wczytaniu daje DOKLADNIE ta sama
liczbe zmiennoprzecinkowa (repr w Pythonie), wiec obie strony licza na identycznych wartosciach.
Klucze slownikow sa sortowane (stala postac pliku); silnik nigdy nie iteruje po slownikach tam, gdzie kolejnosc
wplywa na rzuty — kolejnosc niosa tylko listy.
"""
import json
import math
import os
import re
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
ZRODLO = os.path.join(TU, "dane_walki.json")
CEL = os.path.join(REPO, "src", "server", "Walka", "Dane.luau")
IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
         "not", "or", "repeat", "return", "then", "true", "until", "while", "continue", "type", "export"}

NAGLOWEK = """--[[
\tDane — WYGENEROWANE z tools/walka/dane_walki.json przez tools/walka/generuj_dane.py. NIE EDYTUJ RECZNIE:
\tzmien plik JSON i uruchom: python -B tools/walka/generuj_dane.py (test sprawdza, czy ten plik jest aktualny).

\tKlasy, umiejetnosci, efekty, zaklecia broni, przeciwnicy lasu z lupem i stale wzorow silnika walki v2.
\tTe same dane czyta port w Pythonie (tools/walka/silnik.py), wiec obie strony licza na identycznych liczbach.
]]
"""


def liczba(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if not math.isfinite(v):
        raise ValueError("liczba nieskonczona w danych")
    if v == math.floor(v) and abs(v) < 2 ** 53:
        return str(int(v))
    return repr(v)


def napis(s):
    wynik = ['"']
    for ch in s:
        if ch == "\\":
            wynik.append("\\\\")
        elif ch == '"':
            wynik.append('\\"')
        elif ch == "\n":
            wynik.append("\\n")
        elif ord(ch) < 32:
            wynik.append("\\%03d" % ord(ch))
        else:
            wynik.append(ch)
    wynik.append('"')
    return "".join(wynik)


def luau(v, wciecie):
    pad = "\t" * wciecie
    if isinstance(v, dict):
        if not v:
            return "{}"
        czesci = []
        for k in sorted(v):
            if k.startswith("_"):
                continue  # pola-komentarze z JSON (np. _opis) nie trafiaja do gry
            klucz = k if IDENT.match(k) and k not in SLOWA else "[%s]" % napis(k)
            czesci.append("%s\t%s = %s," % (pad, klucz, luau(v[k], wciecie + 1)))
        return "{\n" + "\n".join(czesci) + "\n" + pad + "}"
    if isinstance(v, list):
        if not v:
            return "{}"
        if all(not isinstance(x, (dict, list)) for x in v):
            return "{ " + ", ".join(luau(x, wciecie + 1) for x in v) + " }"
        return "{\n" + "\n".join("%s\t%s," % (pad, luau(x, wciecie + 1)) for x in v) + "\n" + pad + "}"
    if isinstance(v, str):
        return napis(v)
    if v is None:
        raise ValueError("null w danych — Luau nie ma odpowiednika w tabeli; usun pole albo daj wartosc")
    return liczba(v)


def tekst():
    with open(ZRODLO, encoding="utf-8") as f:
        dane = json.load(f)
    return NAGLOWEK + "\nreturn " + luau(dane, 0) + "\n"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    nowy = tekst()
    if "--sprawdz" in sys.argv:
        try:
            with open(CEL, encoding="utf-8", newline="") as f:
                stary = f.read()
        except OSError:
            stary = None
        if stary != nowy:
            print("Dane.luau jest NIEAKTUALNY — uruchom: python -B tools/walka/generuj_dane.py")
            sys.exit(1)
        print("Dane.luau aktualny")
        return
    os.makedirs(os.path.dirname(CEL), exist_ok=True)
    with open(CEL, "w", encoding="utf-8", newline="\n") as f:
        f.write(nowy)
    print("zapisano", os.path.relpath(CEL, REPO))


if __name__ == "__main__":
    main()
