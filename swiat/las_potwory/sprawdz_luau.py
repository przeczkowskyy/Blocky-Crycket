#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tania kontrola statyczna źródeł Luau pakietu „potwory w ruchu” (bez Studio, bez Luau) — PROJEKT.md rozdz. 8.8.

    python -B swiat/las_potwory/sprawdz_luau.py                 # domyślnie swiat/las_potwory/zrodla/*.luau
    python -B swiat/las_potwory/sprawdz_luau.py plik.luau …     # wybrane pliki
    python -B swiat/las_potwory/sprawdz_luau.py --test          # samosprawdzenie na swiat/test_walki2/zrodla

Kod wyjścia 1 przy błędzie. Reguły:
  1. Po usunięciu komentarzy (--[[…]], --[==[…]==], --…) i napisów ("…", '…', [[…]], [==[…]==], `…` razem z {})
     bilans bloków: otwierają `function`, `do`, `repeat` oraz instrukcja `if` (jej `then`); zamykają `end`, `until`.
     `then` po `elseif` niczego nie otwiera. Wyrażenie `if` (local x = if a then b else c) nie otwiera bloku: `if` jest
     wyrażeniem, gdy poprzedni znaczący token to = ( , { [ return and or not .. operator arytmetyczny lub porównania,
     += -= ..= (i pozostałe przypisania złożone). Na końcu pliku stos ma być pusty; błąd podaje linię bloku bez pary.
  2. Bilans (), {}, [].
  3. Pierwsza instrukcja (po komentarzach) to strażnik Studio.
  4. Zakazane: PathfindingService, Lighting, loadstring, getfenv, setfenv, InvokeClient (w kodzie i w napisach, bez
     komentarzy) oraz wywołania globalnych wait( spawn( delay( (bez task.).
  5. Atrybuty stanu potwora (rozdz. 8.3): każdy napis z GetAttribute("…") w KlientPotworow, który należy do listy
     stanu, musi występować w SetAttribute("…") w SerwerPotworow, a serwer musi ustawiać wszystkie 9. Gdy pliku serwera
     nie ma wśród sprawdzanych, reguła jest pomijana z uwagą (serwer pisze druga połowa zespołu).
  6. --test: wszystkie swiat/test_walki2/zrodla/*.luau (znany dobry zbiór, tylko reguły 1–2; oczekiwane 0 błędów)
     oraz dwa zepsute fragmenty z pamięci skryptu (brak `end`, nadmiarowy `end`) — każdy musi dać błąd.

Moduł można też zaimportować (zbuduj.py): sprawdz_pliki(sciezki) → lista błędów (napisy).
"""
import glob
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))

STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
ZAKAZANE_NAZWY = ["PathfindingService", "Lighting", "loadstring", "getfenv", "setfenv", "InvokeClient"]
ZAKAZANE_WYWOLANIA = ["wait", "spawn", "delay"]
ATRYBUTY_STANU = ["Gatunek", "Nazwa", "Wariant", "Strefa", "Poziom", "Straznik", "Pozycja", "Kierunek", "Stan"]
PLIK_KLIENTA = "KlientPotworow.client.luau"
PLIK_SERWERA = "SerwerPotworow.server.luau"

# poprzednie tokeny, po których `if` jest wyrażeniem (nie otwiera bloku)
PRZED_WYRAZENIEM_IF = {"=", "(", ",", "{", "[", "return", "and", "or", "not", "..",
                       "+", "-", "*", "/", "//", "%", "^", "#",
                       "==", "~=", "<", ">", "<=", ">=",
                       "+=", "-=", "*=", "/=", "//=", "%=", "^=", "..="}
OPERATORY = ["..=", "...", "//=", "..", "==", "~=", "<=", ">=", "+=", "-=", "*=", "/=", "%=", "^=", "//", "->", "::"]


# ------------------------------------------------------------------ usuwanie komentarzy i napisów
def _dlugi_nawias(tekst, i):
    """Gdy w tekst[i] zaczyna się nawias długi [[ albo [==[, zwraca (poziom, długość otwarcia); inaczej None."""
    if tekst[i] != "[":
        return None
    j = i + 1
    while j < len(tekst) and tekst[j] == "=":
        j += 1
    if j < len(tekst) and tekst[j] == "[":
        return j - i - 1, j - i + 1
    return None


def _zaslon(fragment, znak=" "):
    """Fragment zastąpiony znakami `znak`, z zachowaniem końców linii (numery linii się nie zmieniają)."""
    return "".join(c if c == "\n" else znak for c in fragment)


def rozbierz(tekst):
    """Zwraca (bez_komentarzy, bez_komentarzy_i_napisow) — dwa teksty tej samej długości co wejście.
    W drugim każdy napis to cyfra 0 i spacje (żeby został znaczącym tokenem-wartością)."""
    bk = []   # bez komentarzy
    bkn = []  # bez komentarzy i napisów
    i, n = 0, len(tekst)
    while i < n:
        c = tekst[i]
        if c == "-" and tekst.startswith("--", i):
            dn = _dlugi_nawias(tekst, i + 2) if i + 2 < n else None
            if dn:
                poziom, dl = dn
                zamk = "]" + "=" * poziom + "]"
                k = tekst.find(zamk, i + 2 + dl)
                k = n if k < 0 else k + len(zamk)
            else:
                k = tekst.find("\n", i)
                k = n if k < 0 else k
            z = _zaslon(tekst[i:k])
            bk.append(z)
            bkn.append(z)
            i = k
        elif c in "\"'":
            k = i + 1
            while k < n and tekst[k] != c and tekst[k] != "\n":
                k += 2 if tekst[k] == "\\" else 1
            k = min(n, k + 1)
            bk.append(tekst[i:k])
            bkn.append("0" + _zaslon(tekst[i + 1:k]))
            i = k
        elif c == "`":
            k, glebokosc = i + 1, 0
            while k < n:
                d = tekst[k]
                if d == "\\":
                    k += 2
                    continue
                if d == "{":
                    glebokosc += 1
                elif d == "}" and glebokosc > 0:
                    glebokosc -= 1
                elif d == "`" and glebokosc == 0:
                    break
                k += 1
            k = min(n, k + 1)
            bk.append(tekst[i:k])
            bkn.append("0" + _zaslon(tekst[i + 1:k]))
            i = k
        elif c == "[" and _dlugi_nawias(tekst, i):
            poziom, dl = _dlugi_nawias(tekst, i)
            zamk = "]" + "=" * poziom + "]"
            k = tekst.find(zamk, i + dl)
            k = n if k < 0 else k + len(zamk)
            bk.append(tekst[i:k])
            bkn.append("0" + _zaslon(tekst[i + 1:k]))
            i = k
        else:
            bk.append(c)
            bkn.append(c)
            i += 1
    return "".join(bk), "".join(bkn)


# ------------------------------------------------------------------ tokeny
_TOKEN = re.compile(
    r"(?P<nazwa>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<liczba>0[xXbB][0-9a-fA-F_]+|(?:\d[\d_]*(?:\.[\d_]*)?|\.\d[\d_]*)(?:[eE][+-]?\d+)?)"
    r"|(?P<op>" + "|".join(re.escape(o) for o in OPERATORY) + r"|[^\sA-Za-z0-9_])"
)


def tokeny(kod):
    """Lista (token, linia) z kodu bez komentarzy i napisów."""
    wynik = []
    linia = 1
    pozycja = 0
    for m in _TOKEN.finditer(kod):
        linia += kod.count("\n", pozycja, m.start())
        pozycja = m.start()
        wynik.append((m.group(0), linia))
    return wynik


# ------------------------------------------------------------------ reguły
def bilans(kod_bez_napisow, nazwa):
    """Reguły 1 i 2. Zwraca listę błędów."""
    bledy = []
    bloki = []    # (słowo, linia)
    nawiasy = []  # (znak, linia)
    para = {")": "(", "}": "{", "]": "["}
    poprzedni = None
    for tok, linia in tokeny(kod_bez_napisow):
        if tok in ("function", "do", "repeat"):
            bloki.append((tok, linia))
        elif tok == "if":
            if poprzedni not in PRZED_WYRAZENIEM_IF:
                bloki.append(("if", linia))
        elif tok == "end":
            if not bloki or bloki[-1][0] == "repeat":
                bledy.append("%s:%d: nadmiarowe `end`%s" % (nazwa, linia, (" (otwarty `repeat` z linii %d czeka na `until`)"
                                                                          % bloki[-1][1]) if bloki else ""))
            else:
                bloki.pop()
        elif tok == "until":
            if not bloki or bloki[-1][0] != "repeat":
                bledy.append("%s:%d: `until` bez `repeat`" % (nazwa, linia))
            else:
                bloki.pop()
        elif tok in ("(", "{", "["):
            nawiasy.append((tok, linia))
        elif tok in (")", "}", "]"):
            if not nawiasy or nawiasy[-1][0] != para[tok]:
                bledy.append("%s:%d: `%s` bez pary%s" % (nazwa, linia, tok, (" (otwarty `%s` z linii %d)" % nawiasy[-1])
                                                          if nawiasy else ""))
            else:
                nawiasy.pop()
        poprzedni = tok
    for slowo, linia in bloki:
        bledy.append("%s:%d: blok `%s` bez `%s`" % (nazwa, linia, slowo, "until" if slowo == "repeat" else "end"))
    for znak, linia in nawiasy:
        bledy.append("%s:%d: `%s` bez pary" % (nazwa, linia, znak))
    return bledy


def pierwsza_instrukcja(tekst):
    """Kod bez wiodących komentarzy i pustych linii (jak zbuduj.py prototypu)."""
    t = tekst.lstrip()
    while True:
        if t.startswith("--"):
            dn = _dlugi_nawias(t, 2) if len(t) > 2 else None
            if dn:
                zamk = "]" + "=" * dn[0] + "]"
                k = t.find(zamk)
                if k < 0:
                    return ""
                t = t[k + len(zamk):].lstrip()
            else:
                t = t.split("\n", 1)[1].lstrip() if "\n" in t else ""
        else:
            return t


def straznik(tekst, nazwa):
    """Reguła 3."""
    if not pierwsza_instrukcja(tekst).startswith(STRAZNIK):
        return ["%s: pierwsza instrukcja to nie strażnik Studio („%s”)" % (nazwa, STRAZNIK)]
    return []


def zakazane(bez_kom, bez_kom_nap, nazwa):
    """Reguła 4."""
    bledy = []
    for slowo in ZAKAZANE_NAZWY:
        for m in re.finditer(r"\b%s\b" % slowo, bez_kom):
            bledy.append("%s:%d: zakazane `%s`" % (nazwa, bez_kom.count("\n", 0, m.start()) + 1, slowo))
    for slowo in ZAKAZANE_WYWOLANIA:
        for m in re.finditer(r"(?<![.:\w])%s\s*\(" % slowo, bez_kom_nap):
            bledy.append("%s:%d: globalne `%s(` — użyj task.%s" % (nazwa, bez_kom_nap.count("\n", 0, m.start()) + 1,
                                                                  slowo, slowo))
    return bledy


def napisy_wywolan(bez_kom, metoda):
    """Zbiór napisów z wywołań metoda("…") / metoda('…') w kodzie bez komentarzy."""
    return set(m.group(2) for m in re.finditer(r"%s\s*\(\s*([\"'])([^\"'\n]*)\1" % metoda, bez_kom))


def atrybuty_stanu(teksty):
    """Reguła 5. teksty: {nazwa pliku: (bez_kom)}. Zwraca (błędy, uwagi)."""
    klient = next((t for n, t in teksty.items() if os.path.basename(n) == PLIK_KLIENTA), None)
    serwer = next((t for n, t in teksty.items() if os.path.basename(n) == PLIK_SERWERA), None)
    if serwer is None:
        return [], ["reguła 5 pominięta: wśród sprawdzanych nie ma %s (pisze go programista S)" % PLIK_SERWERA]
    ustawiane = napisy_wywolan(serwer, "SetAttribute")
    bledy = []
    for a in ATRYBUTY_STANU:
        if a not in ustawiane:
            bledy.append("%s: serwer nie ustawia atrybutu stanu „%s” (SetAttribute(\"%s\", …))" % (PLIK_SERWERA, a, a))
    if klient is not None:
        for a in sorted(napisy_wywolan(klient, "GetAttribute")):
            if a in ATRYBUTY_STANU and a not in ustawiane:
                bledy.append("%s: klient czyta „%s”, którego serwer nie ustawia" % (PLIK_KLIENTA, a))
    return bledy, []


# ------------------------------------------------------------------ API
def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def sprawdz_tekst(tekst, nazwa, pelne=True):
    """Błędy jednego pliku. pelne=False → tylko reguły 1–2 (tryb --test na prototypie)."""
    bez_kom, bez_kom_nap = rozbierz(tekst)
    bledy = bilans(bez_kom_nap, nazwa)
    if pelne:
        bledy += straznik(tekst, nazwa)
        bledy += zakazane(bez_kom, bez_kom_nap, nazwa)
    return bledy


def sprawdz_pliki(sciezki, pelne=True, wypisz=None):
    """Wszystkie reguły dla listy plików. Zwraca listę błędów; uwagi wypisuje funkcją wypisz (domyślnie print)."""
    wypisz = wypisz or print
    bledy = []
    teksty = {}
    for s in sciezki:
        nazwa = os.path.relpath(s, REPO).replace("\\", "/")
        try:
            tekst = wczytaj(s)
        except OSError as e:
            bledy.append("%s: nie mogę przeczytać (%s)" % (nazwa, e))
            continue
        bledy += sprawdz_tekst(tekst, nazwa, pelne)
        teksty[nazwa] = rozbierz(tekst)[0]
    if pelne:
        b, uwagi = atrybuty_stanu(teksty)
        bledy += b
        for u in uwagi:
            wypisz("  uwaga: " + u)
    return bledy


# dwa zepsute fragmenty do samosprawdzenia (każdy musi dać błąd bilansu)
ZEPSUTE = {
    "brak_end": 'local function f(x)\n\tif x then\n\t\treturn 1\n\tend\n-- brak end funkcji\n',
    "nadmiarowy_end": 'local function f(x)\n\tlocal y = if x then 1 else 2\n\treturn y\nend\nend\n',
}
# i jeden poprawny z pułapkami (wyrażenie if, napisy z „end”, długi komentarz) — musi przejść bez błędów
DOBRY = ('local t = { a = if x then "end" else [[do]], b = `{if y then 1 else 2} end` }\n'
         '--[==[ function do repeat ]==]\n'
         'repeat\n\tlocal z = (if t.a then 1 else 2) + #t\nuntil z\n'
         'for i = 1, 2 do\n\tif i > 1 then\n\t\tcontinue\n\telseif i == 0 then\n\t\tbreak\n\tend\nend\n'
         'local function g(): number\n\treturn if t then 1 elseif t.b then 2 else 3\nend\n')


def samosprawdzenie():
    bledy = 0
    pliki = sorted(glob.glob(os.path.join(REPO, "swiat", "test_walki2", "zrodla", "*.luau")))
    if not pliki:
        print("BŁĄD --test: nie znalazłem swiat/test_walki2/zrodla/*.luau")
        return 1
    for s in pliki:
        b = sprawdz_tekst(wczytaj(s), os.path.relpath(s, REPO).replace("\\", "/"), pelne=False)
        print("  %-55s %s" % (os.path.relpath(s, REPO).replace("\\", "/"), "OK" if not b else "%d błędów" % len(b)))
        for x in b[:10]:
            print("      " + x)
        bledy += len(b)
    for nazwa, tekst in ZEPSUTE.items():
        b = sprawdz_tekst(tekst, "(fragment %s)" % nazwa, pelne=False)
        print("  %-55s %s" % ("(fragment zepsuty: %s)" % nazwa, ("wykryty: " + b[0]) if b else "NIE WYKRYTY"))
        if not b:
            bledy += 1
    b = sprawdz_tekst(DOBRY, "(fragment dobry)", pelne=False)
    print("  %-55s %s" % ("(fragment poprawny z pułapkami)", "OK" if not b else "; ".join(b)))
    bledy += len(b)
    print("samosprawdzenie: %s (%d plików prototypu)" % ("OK" if bledy == 0 else "BŁĘDY: %d" % bledy, len(pliki)))
    return 0 if bledy == 0 else 1


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    if "--test" in argv:
        return samosprawdzenie()
    pliki = [a for a in argv if not a.startswith("--")]
    if not pliki:
        pliki = sorted(glob.glob(os.path.join(TU, "zrodla", "*.luau")))
    if not pliki:
        print("BŁĄD: brak plików do sprawdzenia")
        return 1
    bledy = sprawdz_pliki(pliki)
    for b in bledy:
        print("  " + b)
    print("sprawdz_luau: %d plików, %s" % (len(pliki), "OK" if not bledy else "BŁĘDY: %d" % len(bledy)))
    return 0 if not bledy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
