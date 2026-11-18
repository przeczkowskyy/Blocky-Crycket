# -*- coding: utf-8 -*-
"""Widoki modeli ras do plansz — skrypt uruchamiany W BLENDERZE przez rasy_plansze.py (nie wprost).

    blender -b --factory-startup --python swiat/postacie/rasy_plansze_blender.py -- <zadania.json>

zadania.json: {"pakiet": <pakiet modeli jak dla blender_postac.py>, "wyj": <folder>, "probki": 16,
               "modele": {<id>: {"widoki": [[nazwa, [kx, ky, kz]], …], "wys": [y0, y1], "rozmiar": px,
                                 "poza": {kość: [rx, ry, rz]}, "obrys": true}}}
Każdy widok to kwadratowy render ortogonalny <id>_<nazwa>.png, który obejmuje dokładnie wysokości y0…y1 (studs)
i jest wyśrodkowany na osi postaci — wszystkie widoki i modele z tym samym „wys” i „rozmiar” mają więc tę samą
skalę (piksele na stud) i wspólną linię stóp. Kierunek widoku jak w blender_postac.kamera: od modelu ku kamerze,
w układzie danych (postać patrzy w +Z, jej lewa strona to +X). „poza” ustawia kości tylko na czas renderu
(np. ręce lekko od ciała, jak na rzutach). Budowa siatek, światło, obrys i kamera: biblioteka/blender_postac.py.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(TU, "biblioteka"))
import blender_postac as B  # noqa: E402


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    with open(argv[0], encoding="utf-8") as f:
        zad = json.load(f)
    with open(zad["pakiet"], encoding="utf-8") as f:
        pak = json.load(f)
    wyj = zad["wyj"]
    os.makedirs(wyj, exist_ok=True)
    for d in pak["modele"]:
        z = zad["modele"].get(d["id"])
        if not z or d["rodzaj"] != "postac":
            continue
        sc = B.nowa_scena(30)
        m = B.zbuduj_postac(d, wyj)
        B.przygotuj_render(sc, int(zad.get("probki", 16)))
        arm, model = m["arm"], m["render"]
        B.ustaw_akcje(arm, None)                                  # spoczynek (bez klipu), potem poza z zadania
        for kosc, r in (z.get("poza") or {}).items():
            arm.pose.bones[kosc].rotation_euler = tuple(math.radians(v) for v in r)
        bpy.context.view_layer.update()
        y0, y1 = (float(v) for v in z["wys"])
        a = (y1 - y0) / 2.0
        if z.get("obrys", True):
            B.dodaj_obrys(model, float(z.get("obrys_grubosc", 0.035)))
            # otoczka obrysu nie rzuca cienia na model: bez tego kolory w renderze z obrysem ciemnieją i szarzeją
            # (widać to w kadrze bohaterskim biblioteki), a tu chodzi o porównanie kolorów z rzutem
            for mat in bpy.data.materials:
                if mat.name.startswith("_Obrys") and hasattr(mat, "use_backface_culling_shadow"):
                    mat.use_backface_culling_shadow = True
        B.podloze(max(8.0, (y1 - y0) * 3))
        # stały kadr: sześcian o boku y1 − y0 wokół osi postaci (Blender: dane (x, y, z) -> (x, −z, y))
        pts = [Vector((sx * a, sz * a, y)) for sx in (-1, 1) for sz in (-1, 1) for y in (y0, y1)]
        for nazwa, kier in z["widoki"]:
            cam = B.kamera(sc, tuple(kier), pts, True, margines=1.0)
            cam.data.ortho_scale = y1 - y0
            p = os.path.join(wyj, "%s_%s.png" % (d["id"], nazwa))
            B.renderuj(sc, p, int(z["rozmiar"]), fmt="PNG")
            B.log("RENDER", p)


if __name__ == "__main__":
    main()
