#!/usr/bin/env python3
"""Koty ras w Studio (Paweł 24.11): elf, mroczny elf, ork, goblin, półbóg z swiat/postacie/koty_ras.py — pełny strój
(rząd z = −652; −676 wypadał w zagrodzie petów Karola) i strój podstawowy (rząd z = −660), zbudowane narzędziem Karola swiat/postacie/roblox_postac.py
z klipami Kota-Maga, we WŁASNYM kontenerze Workspace/KotRasyPodglad (atrybut Wygenerowane), na wolnych polach bruku
placu (zmierzone 24.11 promieniem w dół). Do wyboru rasy: tools/studio/koty_ras_wybor.luau.

Użycie: python -B tools/studio/koty_ras_studio.py [--usun]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTACIE = os.path.join(ROOT, "swiat", "postacie")
sys.path.insert(0, ROOT)
sys.path.insert(0, POSTACIE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

RASY = ["elf", "mroczny_elf", "ork", "goblin", "polbog"]
NAZWY = {"elf": "Kot-Elf", "mroczny_elf": "Kot-Mroczny elf", "ork": "Kot-Ork", "goblin": "Kot-Goblin",
         "polbog": "Kot-Półbóg"}
PELNY_X = [955.0, 960.0, 965.0, 970.0, 975.0]
PODST_X = [960.0, 965.0, 970.0, 975.0, 980.0]

R.KONTENER = "KotRasyPodglad"
R.PRZESUNIECIE = (0.0, 0.0)
R.ROZMIESZCZENIE = {}
for r, xp, xs in zip(RASY, PELNY_X, PODST_X):
    R.ROZMIESZCZENIE["kot_" + r] = {"poz": (xp, -652.0), "patrz": (xp, -666.0), "nazwa": NAZWY[r]}
    R.ROZMIESZCZENIE["kot_%s_podstawowy" % r] = {"poz": (xs, -660.0), "patrz": (xs, -674.0),
                                                 "nazwa": NAZWY[r] + " (strój podstawowy)"}

_stare = R.postacie_z_modulu


def postacie_z_modulu(sciezka):
    nazwa = os.path.basename(sciezka)[:-3]
    if nazwa.startswith("kot_") and nazwa[4:].replace("_podstawowy", "") in RASY:
        k = R.wczytaj_modul(os.path.join(POSTACIE, "koty_ras.py"))
        rasa = nazwa[4:].replace("_podstawowy", "")
        return [k.podstawowy(rasa)] if nazwa.endswith("_podstawowy") else [k.zbuduj_rase(rasa)]
    return _stare(sciezka)


R.postacie_z_modulu = postacie_z_modulu

if __name__ == "__main__":
    reszta = [a for a in sys.argv[1:] if a == "--usun"]
    ids = ",".join(["kot_" + r for r in RASY] + ["kot_%s_podstawowy" % r for r in RASY])
    sys.argv = [sys.argv[0], "--tylko", ids, "--wyj", os.path.join(ROOT, "build", "koty_ras")] + reszta
    R.main()
