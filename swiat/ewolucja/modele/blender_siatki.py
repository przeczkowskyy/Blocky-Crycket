# -*- coding: utf-8 -*-
"""Ścieżka siatek (na później, BEZ wgrywania) — uruchamiane W BLENDERZE przez generuj.py pod wspólną blokadą.

    blender -b --factory-startup --python blender_siatki.py -- <pakiet.json> <folder wyników> <manifest.json>

Dla każdego modelu: jedna siatka na STAW i REGION KOLORU (osobno bryły świecące i każdy stały kolor), każda w jednym
kolorze i jednym materiale, z punktem obrotu w stawie. Nazwa: <Staw>__<region>[_neon | _RRGGBB]. Bez szkieletu —
siatki są sztywne, stawy opisuje rig z danych gry. Pliki: <id>_czesci.fbx (ustawienia biblioteki: Forward Z, Up Y,
jednostka = stud) i <id>_czesci.glb. Siatki budują funkcje biblioteki (te same bryły i fazy co w pozostałych eksportach).
"""
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(os.path.dirname(os.path.dirname(TU)), "postacie", "biblioteka")
if BIB not in sys.path:
    sys.path.insert(0, BIB)

import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402

import blender_postac as bp  # noqa: E402


def main():
    arg = sys.argv[sys.argv.index("--") + 1:]
    with open(arg[0], encoding="utf-8") as f:
        pak = json.load(f)
    wyj = os.path.abspath(arg[1])
    os.makedirs(wyj, exist_ok=True)
    manifest = {}
    for d in pak["modele"]:
        bp.nowa_scena(30)
        komorki, G = bp.paleta(d["czesci"])
        obrazy = bp.obrazy_palety(d["id"], komorki, G, d["materialy"], os.path.join(wyj, d["id"] + "_tekstury"))
        mat = bp.material_modelu(d["id"], obrazy)
        stawy = {k["n"]: k["staw"] for k in d["kosci"]}
        grupy = {}
        for c, reg in zip(d["czesci"], d["regiony_czesci"]):
            neon = c["m"] == "swiecacy"
            klucz = reg + ("_" + c["c"] if reg == "stale" else "") + ("_neon" if neon else "")
            grupy.setdefault((c["kosc"], klucz), {"cz": [], "reg": reg, "neon": neon, "kolor": c["c"]})["cz"].append(c)
        obs, wiersze = [], []
        for k in d["kosci"]:
            for (kosc, klucz), g in grupy.items():
                if kosc != k["n"]:
                    continue
                ob = bp.siatka("%s__%s" % (kosc, klucz), g["cz"], komorki, G, mat)
                j = bp.do_blendera(stawy[kosc])
                ob.data.transform(Matrix.Translation(-j))          # punkt obrotu siatki = staw
                ob.location = j
                ob["staw"], ob["region"], ob["neon"], ob["kolor"] = kosc, g["reg"], int(g["neon"]), g["kolor"]
                obs.append(ob)
                wiersze.append([ob.name, kosc, g["reg"], int(g["neon"]), g["kolor"], bp.trojkaty(ob)])
        bpy.context.view_layer.update()
        bp.eksport_fbx(os.path.join(wyj, d["id"] + "_czesci.fbx"), obs, anim=False, typy=("MESH",))
        bp.eksport_glb(os.path.join(wyj, d["id"] + "_czesci.glb"), obs, anim=False)
        manifest[d["id"]] = {"siatki": wiersze, "trojkaty": sum(w[5] for w in wiersze), "liczba_siatek": len(wiersze)}
        bp.log("SIATKI %s: %d siatek, %d trójkątów" % (d["id"], len(wiersze), manifest[d["id"]]["trojkaty"]))
    with open(arg[2], "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, separators=(",", ":"))
    bp.log("GOTOWE siatki: %d modeli" % len(manifest))


if __name__ == "__main__":
    main()
