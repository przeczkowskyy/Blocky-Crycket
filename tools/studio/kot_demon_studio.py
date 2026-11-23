#!/usr/bin/env python3
"""Kot-Demon w Studio do obejrzenia (Paweł 23.11): obie wersje z swiat/postacie/kot_demon.py — pełny strój i strój
podstawowy — zbudowane narzędziem Karola swiat/postacie/roblox_postac.py (części Roblox, bez wgrywania), z klipami
Kota-Maga (próbki z Blendera), we WŁASNYM kontenerze Workspace/KotDemonPodglad (atrybut Wygenerowane) na placu
miasteczka obok siłowni AFK. W Play figury grają animacje (skrypt PokazAnimacji z narzędzia Karola).
Kontener Karola Workspace/TestPostaci zostaje nietknięty.

Użycie: python -B tools/studio/kot_demon_studio.py [--usun]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTACIE = os.path.join(ROOT, "swiat", "postacie")
sys.path.insert(0, ROOT)
sys.path.insert(0, POSTACIE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

R.KONTENER = "KotDemonPodglad"
R.PRZESUNIECIE = (0.0, 0.0)
# wolny pas placu w Workspace/MiasteczkoBazar (zmierzony 23.11), za ostatnim stanowiskiem siłowni AFK; twarzą na plac
R.ROZMIESZCZENIE = {
    "kot_demon": {"poz": (1042.0, -705.0), "patrz": (1042.0, -715.0), "nazwa": "Kot-Demon (pełny strój)"},
    "kot_demon_podstawowy": {"poz": (1049.0, -705.0), "patrz": (1049.0, -715.0), "nazwa": "Kot-Demon (strój podstawowy)"},
    "kot_czlowiek_podstawowy": {"poz": (1035.0, -705.0), "patrz": (1035.0, -715.0),
                                "nazwa": "Kot-Człowiek (strój podstawowy)"},
}

_stare = R.postacie_z_modulu


def postacie_z_modulu(sciezka):
    if os.path.basename(sciezka) == "kot_demon_podstawowy.py":
        demon = R.wczytaj_modul(os.path.join(POSTACIE, "kot_demon.py"))
        return [demon.podstawowy()]
    if os.path.basename(sciezka) == "kot_czlowiek_podstawowy.py":
        demon = R.wczytaj_modul(os.path.join(POSTACIE, "kot_demon.py"))
        return [demon.czlowiek_podstawowy()]
    return _stare(sciezka)


R.postacie_z_modulu = postacie_z_modulu

if __name__ == "__main__":
    reszta = [a for a in sys.argv[1:] if a == "--usun"]
    sys.argv = [sys.argv[0], "--tylko", "kot_demon,kot_demon_podstawowy,kot_czlowiek_podstawowy",
                "--wyj", os.path.join(ROOT, "build", "kot_demon")] + reszta
    R.main()
