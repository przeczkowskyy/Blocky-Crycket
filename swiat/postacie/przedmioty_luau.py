#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista przedmiotów w formacie kodu gry — PROPOZYCJA do rozmowy, nie kanon i nie część gry.

    python -B swiat/postacie/przedmioty_luau.py

Czyta `przedmioty.json` i zapisuje `roblox/PrzedmiotyPropozycja.luau`: tabelę w tym samym układzie co moduł
`ReplicatedStorage.Shared.Items` Game Directora (pola name, slot, category, icon) z dodatkowymi polami iconFile
(plik ikony w repozytorium — ikon nie ma jeszcze na koncie Roblox, więc icon jest puste) i set (zestaw).
Niczego nie wysyła do Studio i nie zmienia kodu gry. Wypisuje też, które sloty i kategorie nie występują w kodzie gry.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))

# sloty i zakładki plecaka z komentarza w ReplicatedStorage.Shared.Items (stan z 13.11.2026)
SLOTY_GRY = ("Helmet", "Chest", "Gloves", "Boots", "Amulet", "Belt", "Ring", "Trinket", "Weapon")
KATEGORIE_GRY = ("Weapons", "Armor", "Amulets", "Others")


def napis(s):
    return json.dumps(s, ensure_ascii=False)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with open(os.path.join(TU, "przedmioty.json"), encoding="utf-8") as f:
        dane = json.load(f)
    przedmioty = dane["przedmioty"]
    kolejnosc = {s: i for i, s in enumerate(SLOTY_GRY)}
    przedmioty = sorted(przedmioty, key=lambda p: (p.get("zestaw") or "", kolejnosc.get(p["slot"], 99), p["id"]))
    obce_sloty = sorted({p["slot"] for p in przedmioty if p["slot"] not in SLOTY_GRY})
    obce_kat = sorted({p["kategoria"] for p in przedmioty if p["kategoria"] not in KATEGORIE_GRY})
    linie = [
        "-- WYGENEROWANE z swiat/postacie/przedmioty.json przez swiat/postacie/przedmioty_luau.py — nie edytuj ręcznie.",
        "-- PROPOZYCJA do rozmowy, nie kanon i nie część gry: ten plik nie jest nigdzie wczytywany.",
        "-- Układ jak w ReplicatedStorage.Shared.Items (name, slot, category, icon). Ikon nie ma jeszcze na koncie Roblox,",
        "-- więc icon jest puste; iconFile wskazuje plik ikony w repozytorium, set — zestaw, z którego pochodzi przedmiot.",
    ]
    if obce_sloty:
        linie.append("-- Sloty spoza kodu gry (do decyzji, pytanie 24 w sejfie): %s." % ", ".join(obce_sloty))
    linie.append("return {")
    zestaw = None
    for p in przedmioty:
        if p.get("zestaw") != zestaw:
            zestaw = p.get("zestaw")
            linie.append("\t-- %s" % (zestaw or "bez zestawu"))
        ikona = p.get("plik_ikony") or ""
        linie.append("\t%s = { name = %s, slot = %s, category = %s, icon = \"\", iconFile = %s, set = %s },"
                     % (p["id"], napis(p["nazwa"]), napis(p["slot"]), napis(p["kategoria"]),
                        napis("swiat/postacie/" + ikona if ikona else ""), napis(zestaw or "")))
    linie.append("}")
    cel = os.path.join(TU, "roblox", "PrzedmiotyPropozycja.luau")
    with open(cel, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linie) + "\n")
    licz = {}
    for p in przedmioty:
        licz[p["slot"]] = licz.get(p["slot"], 0) + 1
    print("zapisano %s: %d przedmiotów" % (os.path.relpath(cel, os.path.dirname(os.path.dirname(TU))).replace("\\", "/"), len(przedmioty)))
    print("sloty: " + ", ".join("%s %d" % (s, licz[s]) for s in sorted(licz, key=lambda s: kolejnosc.get(s, 99))))
    print("sloty spoza kodu gry: %s" % (", ".join("%s (%s)" % (s, ", ".join(p["id"] for p in przedmioty if p["slot"] == s)) for s in obce_sloty) or "brak"))
    print("kategorie spoza kodu gry: %s" % (", ".join(obce_kat) or "brak"))
    brak_ikon = [p["id"] for p in przedmioty if not p.get("plik_ikony") or not os.path.isfile(os.path.join(TU, p["plik_ikony"]))]
    print("przedmioty bez pliku ikony: %s" % (", ".join(brak_ikon) or "brak"))


if __name__ == "__main__":
    main()
