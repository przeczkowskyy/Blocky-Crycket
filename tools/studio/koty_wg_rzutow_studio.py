#!/usr/bin/env python3
"""Koty ras według rzutów Pawła z 26.11 w Studio — PODGLĄD do wyboru rasy (propozycja, nie zastępuje decyzji):
siedem figur w stroju podstawowym (człowiek, półbóg, goblin, mroczny elf, elf, ork z swiat/postacie/koty_wg_rzutow.py
i demon z kot_demon.wg_rzutow) zbudowanych narzędziem Karola swiat/postacie/roblox_postac.py we WŁASNYM kontenerze
Workspace/KotyWgRzutowPodglad (atrybut Wygenerowane). Bez klipów — ekran wyboru rasy pokazuje figury w spoczynku;
pełna budowa z klipami Kota-Maga: uruchomić bez --bez-klipow.
Do wyboru rasy: tools/studio/koty_wg_rzutow_wybor.luau (robi kopię zapasową obecnych figur).

Użycie: python -B tools/studio/koty_wg_rzutow_studio.py [--usun] [--z-klipami]
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POSTACIE = os.path.join(ROOT, "swiat", "postacie")
sys.path.insert(0, ROOT)
sys.path.insert(0, POSTACIE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import roblox_postac as R  # noqa: E402

# wolne pola zmierzone 26.11 (promień w dół + pudełko 4,5 × 8 × 4,5 bez części)
POLA = {"czlowiek": (955.0, -636.0), "polbog": (965.0, -636.0), "goblin": (975.0, -636.0),
        "mroczny_elf": (960.0, -644.0), "elf": (975.0, -644.0), "ork": (1068.0, -705.0), "demon": (1068.0, -697.0)}
NAZWY = {"czlowiek": "Kot-Człowiek", "polbog": "Kot-Półbóg", "goblin": "Kot-Goblin", "mroczny_elf": "Kot-Mroczny elf",
         "elf": "Kot-Elf", "ork": "Kot-Ork", "demon": "Kot-Demon"}


def id_modulu(rasa):
    return "kot_demon_wg_rzutow" if rasa == "demon" else "kot_%s_wg_rzutow" % rasa


R.KONTENER = "KotyWgRzutowPodglad"
R.PRZESUNIECIE = (0.0, 0.0)
R.ROZMIESZCZENIE = {id_modulu(r): {"poz": p, "patrz": (p[0], p[1] - 10.0), "nazwa": NAZWY[r] + " (według rzutów)"}
                    for r, p in POLA.items()}

_stare = R.postacie_z_modulu


def postacie_z_modulu(sciezka):
    nazwa = os.path.basename(sciezka)[:-3]
    if nazwa == "kot_demon_wg_rzutow":                       # demon: te same klipy ruchu co pozostałe koty
        koty = R.wczytaj_modul(os.path.join(POSTACIE, "koty_wg_rzutow.py"))
        return [koty.klipy_ruchu(koty.KD.wg_rzutow())]
    if nazwa.startswith("kot_") and nazwa.endswith("_wg_rzutow"):
        return [R.wczytaj_modul(os.path.join(POSTACIE, "koty_wg_rzutow.py")).zbuduj_kota(nazwa[4:-10])]
    return _stare(sciezka)


R.postacie_z_modulu = postacie_z_modulu

if __name__ == "__main__":
    reszta = [a for a in sys.argv[1:] if a == "--usun"]
    if "--z-klipami" not in sys.argv and not reszta:
        reszta += ["--bez-klipow", "--bez-pokazu"]
    sys.argv = [sys.argv[0], "--tylko", ",".join(id_modulu(r) for r in POLA),
                "--wyj", os.path.join(ROOT, "build", "koty_wg_rzutow")] + reszta
    R.main()
