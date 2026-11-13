# -*- coding: utf-8 -*-
"""Próbki klipów co klatkę — uruchamiane W BLENDERZE (w tle) przez roblox_postac.py.

    blender -b --factory-startup --python blender_probki.py -- <pakiet.json> <wynik.json>

Buduje szkielet i akcje dokładnie tak, jak blender_postac.py (te same funkcje), a potem odczytuje wartość każdej
krzywej w każdej klatce 0…dlugosc. Dzięki temu animacja w Roblox ma te same wygładzenia co filmy z Blendera
(Bezier z automatycznymi uchwytami, pętla domknięta modyfikatorem Cycles), bez przepisywania tej matematyki.
Wynik: {id postaci: {klip: {kość: {"obrot": [[rx, ry, rz] w stopniach, …], "przes": [[x, y, z], …]}}}} w układzie danych.
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True                              # bez __pycache__ w repozytorium
TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)

import blender_postac as bp  # noqa: E402

TYPY = {"rotation_euler": "obrot", "location": "przes", "scale": "skala"}


def main():
    arg = sys.argv[sys.argv.index("--") + 1:]
    with open(arg[0], encoding="utf-8") as f:
        pak = json.load(f)
    wynik = {}
    for d in pak["modele"]:
        if d.get("rodzaj") != "postac" or not d.get("klipy"):
            continue
        bp.nowa_scena(d["klipy"][0]["fps"])
        arm = bp.szkielet(d)
        akcje = bp.klipy(arm, d["klipy"])
        klipy = {}
        for kl in d["klipy"]:
            n = int(kl["dlugosc"])
            kosci = {}
            for fc in bp.kanaly_akcji(akcje[kl["n"]]):
                kosc = fc.data_path.split('"')[1]
                typ = TYPY.get(fc.data_path.rsplit(".", 1)[1])
                if typ is None:
                    continue
                domyslna = 1.0 if typ == "skala" else 0.0
                tab = kosci.setdefault(kosc, {}).setdefault(typ, [[domyslna] * 3 for _ in range(n + 1)])
                for f in range(n + 1):
                    v = fc.evaluate(float(f))
                    tab[f][fc.array_index] = round(math.degrees(v) if typ == "obrot" else v, 4)
            klipy[kl["n"]] = kosci
        wynik[d["id"]] = klipy
        bp.log("PROBKI %s: %s" % (d["id"], ", ".join("%s %d kl." % (k["n"], k["dlugosc"] + 1) for k in d["klipy"])))
    with open(arg[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(wynik, f, ensure_ascii=False, separators=(",", ":"))


if __name__ == "__main__":
    main()
