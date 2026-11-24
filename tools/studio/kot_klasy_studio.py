#!/usr/bin/env python3
"""Koci Rycerz i Koci Zwiadowca w Studio (Paweł 24.11, D-145): stroje klas na Kocie-Magu z swiat/postacie/kot_klasy.py,
zbudowane narzędziem Karola swiat/postacie/roblox_postac.py (części Roblox, bez wgrywania) z klipami Kota-Maga,
we WŁASNYM kontenerze Workspace/KotKlasyPodglad (atrybut Wygenerowane), obok Kota-Demona na placu miasteczka.
Selektor klas bierze z nich kopie (tools/studio/kot_klasy_wybor.luau -> WyborKlasyModele.Warrior / Scout).

Użycie: python -B tools/studio/kot_klasy_studio.py [--usun]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTACIE = os.path.join(ROOT, "swiat", "postacie")
sys.path.insert(0, ROOT)
sys.path.insert(0, POSTACIE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

R.KONTENER = "KotKlasyPodglad"
R.PRZESUNIECIE = (0.0, 0.0)
# ten sam wolny pas placu co KotDemonPodglad (1035–1049), dalej w prawo; twarzą na plac
R.ROZMIESZCZENIE = {
    "kot_rycerz": {"poz": (1056.0, -705.0), "patrz": (1056.0, -715.0), "nazwa": "Koci Rycerz"},
    "kot_zwiadowca": {"poz": (1063.0, -705.0), "patrz": (1063.0, -715.0), "nazwa": "Koci Zwiadowca"},
}

_stare = R.postacie_z_modulu


def postacie_z_modulu(sciezka):
    nazwa = os.path.basename(sciezka)
    if nazwa in ("kot_rycerz.py", "kot_zwiadowca.py"):
        k = R.wczytaj_modul(os.path.join(POSTACIE, "kot_klasy.py"))
        return [k.rycerz()] if nazwa == "kot_rycerz.py" else [k.zwiadowca()]
    return _stare(sciezka)


R.postacie_z_modulu = postacie_z_modulu

if __name__ == "__main__":
    reszta = [a for a in sys.argv[1:] if a == "--usun"]
    sys.argv = [sys.argv[0], "--tylko", "kot_rycerz,kot_zwiadowca",
                "--wyj", os.path.join(ROOT, "build", "kot_klasy")] + reszta
    R.main()
