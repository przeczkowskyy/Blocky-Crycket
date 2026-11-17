#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator zrodla/DaneWskazowek.luau — wskazówki celu dla nowego gracza (pakiet swiat/wskazowki_gry).

    python -B swiat/wskazowki_gry/dane.py               # zapisuje zrodla/DaneWskazowek.luau
    python -B swiat/wskazowki_gry/dane.py --sprawdz     # kod 1, gdy plik jest nieaktualny (nic nie zapisuje)
    python -B swiat/wskazowki_gry/dane.py --wyjscie DIR # zapis gdzie indziej (testy)

Źródło: ustawienia.json (teksty kroków, nazwy instancji innych pakietów — tylko do odczytu, wygląd). Położeń nie ma:
punkty celów klient czyta w grze (dane lasu, punkty bazaru, potwory). Do danych dochodzą przypadki wzorcowe logiki
(logika_wskazowek.py), które sprawdza też Luau.
"""
import copy
import hashlib
import json
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
ZRODLA = os.path.join(TU, "zrodla")
USTAWIENIA = os.path.join(TU, "ustawienia.json")
PLIK_LUAU = "DaneWskazowek.luau"
if TU not in sys.path:
    sys.path.insert(0, TU)
import logika_wskazowek as LW  # noqa: E402

CELE = {"teleport", "potwor", "straznik", "kamien", "trener", "brama", None}
# napisy dla twórców nie mogą trafić na ekran gracza (raport przejścia gry 17.11.2026)
TWORCY = re.compile(r"D-0\d\d|Paweł|Karol|próba|\btest|TYMCZASOW|bez zapisu|atrybut|placeholder|w budowie", re.I)


class BladDanych(Exception):
    pass


def wczytaj():
    with open(USTAWIENIA, encoding="utf-8") as f:
        K = json.load(f)
    D = {k: v for k, v in K.items() if k not in ("opis", "status")}
    sprawdz(D)
    return K, D


def sprawdz(D):
    kroki = D.get("kroki") or {}
    if not kroki:
        raise BladDanych("brak kroków")
    for kid, k in kroki.items():
        if not isinstance(k.get("tekst"), str) or not k["tekst"].strip():
            raise BladDanych("krok %s bez tekstu" % kid)
        if k.get("cel") not in CELE:
            raise BladDanych("krok %s: nieznany cel %r" % (kid, k.get("cel")))
        if TWORCY.search(k["tekst"]):
            raise BladDanych("krok %s: napis dla twórców na ekranie gracza: %r" % (kid, k["tekst"]))
        if len(k["tekst"]) > 64:
            raise BladDanych("krok %s: tekst dłuższy niż 64 znaki (nie zmieści się na telefonie)" % kid)
        if k["tekst"].count("%d") > 1 or ("%" in k["tekst"].replace("%d", "")):
            raise BladDanych("krok %s: w tekście wolno tylko jedno %%d" % kid)
    potrzebne = {"a_teleport", "b_potwor", "c_poziomy", "c_poziomy_miasto", "c_straznik", "c_straznik_miasto",
                 "d_trening", "d_trening_miasto", "d_slabszy", "e_brama", "e_brama_miasto", "e_dalej", "e_koniec"}
    brak = potrzebne - set(kroki)
    if brak:
        raise BladDanych("brak kroków: %s" % sorted(brak))
    for k in ("y_px", "wys_px", "tekst_px", "zamknij_px"):
        if not isinstance(D["ui"].get(k), (int, float)) or D["ui"][k] <= 0:
            raise BladDanych("ui.%s musi być liczbą > 0" % k)
    if D["ui"]["zamknij_px"] < 40:
        raise BladDanych("ui.zamknij_px < 40 — za mały cel dotyku na telefonie")


def dane_z_przypadkami():
    K, D = wczytaj()
    D = copy.deepcopy(D)
    D["przypadki"] = LW.przypadki(D)
    D["skrot"] = hashlib.sha1(json.dumps(D, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    return K, D


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
          "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}


def _napis(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    r = repr(float(x))
    return r[:-2] if r.endswith(".0") else r


def _klucz(k):
    return k if (_IDENT.match(k) and k not in _SLOWA) else "[%s]" % _napis(k)


def _luau(v, wciecie=1):
    if v is None:
        return "nil"
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, list):
        czesci = [_luau(x, wciecie + 1) for x in v]
    elif isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
    else:
        raise TypeError(repr(v))
    jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
    if len(jedna) <= 110 and "\n" not in jedna:
        return jedna
    return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"


def luau_tekst(D):
    naglowek = ("--[[\n\tDaneWskazowek — WYGENEROWANE przez swiat/wskazowki_gry/dane.py z ustawienia.json. Nie edytuj\n"
                "\tręcznie: zmień ustawienia i uruchom dane.py.\n\tSkrót danych: %s\n]]\n" % D["skrot"])
    return (naglowek + 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn '
            + _luau(D) + "\n")


def zapisz(folder):
    _, D = dane_z_przypadkami()
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, PLIK_LUAU), "w", encoding="utf-8", newline="\n") as f:
        f.write(luau_tekst(D))
    return D


def aktualny():
    _, D = dane_z_przypadkami()
    sciezka = os.path.join(ZRODLA, PLIK_LUAU)
    if not os.path.isfile(sciezka):
        return False, D
    with open(sciezka, encoding="utf-8") as f:
        return f.read() == luau_tekst(D), D


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("DaneWskazowek.luau: %s (skrót %s, kroków %d, przypadków %d + %d)" % (
                "aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["kroki"]), len(D["przypadki"]["kroki"]),
                len(D["przypadki"]["miejsca"])))
            return 0 if ok else 1
        folder = argv[argv.index("--wyjscie") + 1] if "--wyjscie" in argv else ZRODLA
        D = zapisz(folder)
        print("zapisano %s (skrót %s)" % (os.path.join(os.path.relpath(folder, REPO) if folder == ZRODLA else folder,
                                                       PLIK_LUAU), D["skrot"]))
        for p in D["przypadki"]["kroki"]:
            print("  %-52s → %s" % (p["opis"], p["tekst"] or "—"))
        return 0
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
