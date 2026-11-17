#!/usr/bin/env python3
"""Goły model dla ekranu wyboru rasy (D-079, D-071): ciało bazowe Rycerza z kodu Karola (`rycerz.cialo()`),
zbudowane narzędziem Karola `swiat/postacie/roblox_postac.py`, ale we WŁASNYM kontenerze Workspace/WyborKlasyBaza
(z atrybutem Wygenerowane, daleko od mapy) — kontener Karola Workspace/TestPostaci zostaje nietknięty.
Potem `python tools/studio/deploy_classselect.py` kopiuje go do ReplicatedStorage.WyborKlasyModele.Base.

Użycie: python -B tools/studio/baza_rasy.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTACIE = os.path.join(ROOT, "swiat", "postacie")
sys.path.insert(0, ROOT)
sys.path.insert(0, POSTACIE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

ID = "baza_rasy"
R.KONTENER = "WyborKlasyBaza"
R.PRZESUNIECIE = (0.0, 5000.0)          # z dala od mapy i od sali (sala: y 400, z 4000)
R.ROZMIESZCZENIE = {ID: {"poz": (0.0, 0.0), "patrz": (0.0, 10.0), "nazwa": "Ciało bazowe (rasy)"}}

_stare = R.postacie_z_modulu


def postacie_z_modulu(sciezka):
    if os.path.basename(sciezka) == ID + ".py":
        rycerz = R.wczytaj_modul(os.path.join(POSTACIE, "rycerz.py"))
        return [rycerz.cialo()]
    return _stare(sciezka)


R.postacie_z_modulu = postacie_z_modulu

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--tylko", ID, "--bez-klipow", "--bez-pokazu", "--wyj",
                os.path.join(ROOT, "build", "baza_rasy")]
    R.main()
