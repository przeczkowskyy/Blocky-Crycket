#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Lista przedmiotów w formacie kodu gry — PROPOZYCJA do rozmowy, nie kanon i nie część gry.

    python -B swiat/postacie/przedmioty_luau.py

Czyta `przedmioty.json` i zapisuje `roblox/PrzedmiotyPropozycja.luau`: tabelę w tym samym układzie co moduł
`ReplicatedStorage.Shared.Items` Game Directora (pola name, slot, category, icon) z dodatkowymi polami iconFile
(plik ikony w repozytorium — ikon nie ma jeszcze na koncie Roblox, więc icon jest puste) i set (zestaw).
Przedmioty bohaterów (D-071, swiat/postacie/EKWIPUNEK.md pkt 5) dostają jeszcze: body (typ ciała: czlowiek, kot,
dowolne), classes (klasy), hides (znaczniki chowanych akcesoriów ciała, np. Wlosy), parent (przedmiot nadrzędny —
spodnie są częścią zbroi) i meshes (segmenty: id, bone, covers = powłoka, attachment, pliki fbx/glb, a przy
korekcie ciała kota onBody = { kot = { attachment, bone, pos, rot } }). Wpisy zestawów i broni zostają jednolinijkowe
jak dotąd.
Niczego nie wysyła do Studio i nie zmienia kodu gry. Wypisuje też, które sloty, kategorie, typy ciała, klasy i pola
nie występują w kodzie gry.
"""
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))

# sloty i zakładki plecaka z komentarza w ReplicatedStorage.Shared.Items (stan z 13.11.2026)
SLOTY_GRY = ("Helmet", "Chest", "Gloves", "Boots", "Amulet", "Belt", "Ring", "Trinket", "Weapon")
KATEGORIE_GRY = ("Weapons", "Armor", "Amulets", "Others")
POLA_GRY = ("name", "slot", "category", "icon")
# pola propozycji, których moduł Items nie zna (iconFile i set — każdy wpis; reszta — przedmioty bohaterów)
POLA_SPOZA = ("iconFile", "set", "body", "classes", "hides", "parent", "meshes", "onBody")


def napis(s):
    return json.dumps(s, ensure_ascii=False)


def lista_luau(w):
    return "{ " + ", ".join(napis(x) if isinstance(x, str) else "%g" % x for x in w) + " }" if w else "{}"


def pola_bohatera(p):
    """Wiersze pól D-071 przedmiotu bohatera (body, classes, hides, parent, meshes) — wcięte pod wpisem."""
    linie = ["\t\tbody = %s, classes = %s, hides = %s, parent = %s," % (
        napis(p["cialo"]), lista_luau(p["klasy"]), lista_luau(p["ukrywa"]),
        napis(p["czesc_od"]) if p.get("czesc_od") else "nil"), "\t\tmeshes = {"]
    for c in p["czesci"]:
        w = "{ id = %s, bone = %s, covers = %s, attachment = %s, fbx = %s, glb = %s" % (
            napis(c["id"]), napis(c["kosc"]), "true" if c["zakrywa"] else "false", napis(c["zaczep"]),
            napis("swiat/postacie/" + c["fbx"]), napis("swiat/postacie/" + c["glb"]))
        k = c.get("korekta")
        if k:
            w += ", onBody = { %s = { attachment = %s, bone = %s, pos = %s, rot = %s } }" % (
                k["cialo"], napis(k["zaczep"]), napis(k["kosc"]), lista_luau(k["pos"]), lista_luau(k["rot"]))
        linie.append("\t\t\t" + w + " },")
    linie.append("\t\t},")
    return linie


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
    bohaterowie = [p for p in przedmioty if "cialo" in p]
    if bohaterowie:
        linie.append("-- Przedmioty bohaterów (D-071, swiat/postacie/EKWIPUNEK.md pkt 5) mają pola spoza Items: body, classes,")
        linie.append("-- hides, parent, meshes (segmenty na kościach; attachment Ekw<Kosc>Attachment = środek klocka kości")
        linie.append("-- w gołym ciele bohatera) i onBody (korekta zaczepu na ciele kota). Spodnie: parent = zbroja (brak slotu Legs).")
    linie.append("return {")
    zestaw = None
    for p in przedmioty:
        if p.get("zestaw") != zestaw:
            zestaw = p.get("zestaw")
            linie.append("\t-- %s" % (zestaw or "bez zestawu"))
        ikona = p.get("plik_ikony") or ""
        wpis = ("\t%s = { name = %s, slot = %s, category = %s, icon = \"\", iconFile = %s, set = %s"
                % (p["id"], napis(p["nazwa"]), napis(p["slot"]), napis(p["kategoria"]),
                   napis("swiat/postacie/" + ikona if ikona else ""), napis(zestaw or "")))
        if "cialo" in p:                                  # przedmiot bohatera: pola D-071 w kolejnych wierszach
            linie.append(wpis + ",")
            linie.extend(pola_bohatera(p))
            linie.append("\t},")
        else:
            linie.append(wpis + " },")
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
    print("pola spoza modułu Items (zna tylko %s): %s" % (", ".join(POLA_GRY), ", ".join(
        x for x in POLA_SPOZA if x in ("iconFile", "set") or bohaterowie)))
    if bohaterowie:
        ciala, klasy = {}, {}
        for p in bohaterowie:
            ciala.setdefault(p["cialo"], []).append(p["id"])
            for k in p["klasy"]:
                klasy.setdefault(k, []).append(p["id"])
        print("przedmioty bohaterów: %d (zestawy: %s)" % (len(bohaterowie),
                                                         ", ".join(sorted({p["zestaw"] for p in bohaterowie}))))
        print("typy ciała (body; kod gry ich nie zna): %s" % "; ".join(
            "%s %d" % (c, len(v)) for c, v in sorted(ciala.items())))
        print("klasy (classes; kod gry ich nie zna): %s" % "; ".join(
            "%s %d" % (k, len(v)) for k, v in sorted(klasy.items())))
        print("części innego przedmiotu (parent; okno ekwipunku nie ma slotu Legs): %s" % (", ".join(
            "%s -> %s" % (p["id"], p["czesc_od"]) for p in bohaterowie if p.get("czesc_od")) or "brak"))
        print("ukrywa (hides): %s" % (", ".join("%s %s" % (p["id"], "/".join(p["ukrywa"])) for p in bohaterowie
                                                 if p["ukrywa"]) or "brak"))
        zacz = sorted({c["zaczep"] for p in bohaterowie for c in p["czesci"]})
        print("części bohaterów: %d segmentów; zaczepy Ekw<Kosc>Attachment (są tylko w gołym ciele bohatera, nie w rigu "
              "R15 gry): %d rodzajów; standardowe: %s" % (
                  sum(len(p["czesci"]) for p in bohaterowie), len([z for z in zacz if z.startswith("Ekw")]),
                  ", ".join(z for z in zacz if not z.startswith("Ekw"))))
        print("korekty ciała kota (onBody): %s" % (", ".join(
            "%s -> %s" % (c["id"], c["korekta"]["zaczep"]) for p in bohaterowie for c in p["czesci"]
            if c.get("korekta")) or "brak"))
    brak_ikon = [p["id"] for p in przedmioty if not p.get("plik_ikony") or not os.path.isfile(os.path.join(TU, p["plik_ikony"]))]
    print("przedmioty bez pliku ikony: %s" % (", ".join(brak_ikon) or "brak"))


if __name__ == "__main__":
    main()
