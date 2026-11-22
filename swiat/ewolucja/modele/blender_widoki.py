# -*- coding: utf-8 -*-
"""Własne kadry smoków — uruchamiane W BLENDERZE (w tle) przez generuj.py, pod wspólną blokadą biblioteki.

    blender -b --factory-startup --python blender_widoki.py -- <pakiet.json> <zadania.json> <folder wyników>

Buduje modele tymi samymi funkcjami co biblioteka (swiat/postacie/biblioteka/blender_postac.py), a kadruje po swojemu:
kamera gry (z tyłu, z góry), bok, rząd stadiów w prawdziwej skali, paski klatek klipów. Zadania (lista słowników):
  {"typ": "widoki", "model": id, "widoki": {nazwa: [kierunek x, y, z]}, "rozmiar": 480, "poza": [klip, klatka] | null,
   "orto": false, "trawa": true, "obrys": false}                     -> <id>_<nazwa>.jpg
  {"typ": "rzad", "modele": [id…], "kierunek": [x, y, z], "rozmiar": [szer, wys], "plik": "rzad.jpg", "odstep": 0.25,
   "poza": [klip, klatka] | null}
  {"typ": "pasek", "model": id, "klip": nazwa, "klatki": [..], "kierunek": [x, y, z], "rozmiar": 300}
                                                                      -> <id>_<klip>_<nr>.jpg (wspólny kadr klipu)
Kierunek = od modelu ku kamerze, w układzie danych (Y w górę, przód +Z).
"""
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
BIB = os.path.join(os.path.dirname(os.path.dirname(TU)), "postacie", "biblioteka")
if BIB not in sys.path:
    sys.path.insert(0, BIB)

import bmesh  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

import blender_postac as bp  # noqa: E402

TRAWA = "4F9440"


def ziemia(promien, kolor):
    me = bpy.data.meshes.new("_ziemia")
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=promien, segments=48)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(bp.material_prosty("_Ziemia", kolor, 0.95))
    ob = bpy.data.objects.new("_Ziemia", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def kamera_prost(sc, kierunek, pts, szer, wys, margines=1.08):
    """Kamera ortograficzna dla obrazu prostokątnego szer × wys."""
    d = (bp.C3 @ Vector(kierunek)).normalized()
    przod = -d
    prawo = przod.cross(Vector((0.0, 0.0, 1.0)))
    if prawo.length < 1e-6:
        prawo = Vector((1.0, 0.0, 0.0))
    prawo.normalize()
    gora = prawo.cross(przod).normalized()
    xs, ys, zs = [p.dot(prawo) for p in pts], [p.dot(gora) for p in pts], [p.dot(d) for p in pts]
    sr = prawo * ((min(xs) + max(xs)) / 2) + gora * ((min(ys) + max(ys)) / 2) + d * ((min(zs) + max(zs)) / 2)
    cam = bpy.data.objects.get("_Kamera")
    if cam is None:
        cam = bpy.data.objects.new("_Kamera", bpy.data.cameras.new("_Kamera"))
        sc.collection.objects.link(cam)
    cd = cam.data
    cd.type, cd.sensor_fit = "ORTHO", "HORIZONTAL"
    cd.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * szer / float(wys)) * margines
    odl = (max(zs) - min(zs)) + 60.0
    cd.clip_start, cd.clip_end = 0.05, odl + 600.0
    cam.location = sr + d * odl
    cam.rotation_euler = przod.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam


def render(sc, sciezka, szer, wys):
    sc.render.resolution_x, sc.render.resolution_y = int(szer), int(wys)
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.quality = 92
    sc.render.filepath = sciezka
    bpy.ops.render.render(write_still=True)


def poza(sc, m, pz):
    if pz and pz[0] in m["akcje"]:
        bp.ustaw_akcje(m["arm"], m["akcje"][pz[0]])
        f = float(pz[1])
        sc.frame_set(int(f), subframe=f - int(f))
    else:
        bp.ustaw_akcje(m["arm"], None)
        sc.frame_set(0)
    bpy.context.view_layer.update()


def main():
    arg = sys.argv[sys.argv.index("--") + 1:]
    with open(arg[0], encoding="utf-8") as f:
        modele = {d["id"]: d for d in json.load(f)["modele"]}
    with open(arg[1], encoding="utf-8") as f:
        zadania = json.load(f)
    wyj = os.path.abspath(arg[2])
    os.makedirs(wyj, exist_ok=True)
    tex = os.path.join(wyj, "_tekstury")
    for z in zadania:
        probki = int(z.get("probki", 16))
        if z["typ"] == "rzad":
            sc = bp.nowa_scena(30)
            x, pts_all, ms = 0.0, [], []
            for id_ in z["modele"]:
                m = bp.zbuduj_postac(modele[id_], tex)
                poza(sc, m, z.get("poza"))
                sk = bp.skrzynka(m["render"])
                szer = sk[1][0] - sk[0][0]
                if z.get("os") == "z":                              # rząd wzdłuż osi przód–tył (widok z boku)
                    szer = sk[1][2] - sk[0][2]
                    m["arm"].location = bp.do_blendera((0.0, 0.0, -(x + sk[1][2])))
                else:
                    m["arm"].location = Vector((x - sk[0][0], 0.0, 0.0))
                x += szer + z.get("odstep", 0.25) * szer + 0.6
                ms.append(m)
            bpy.context.view_layer.update()
            bp.przygotuj_render(sc, probki)
            ziemia(x * 3 + 40, z.get("ziemia", TRAWA))
            pts = [p for m in ms for p in bp.punkty(m["render"])]
            w, h = z["rozmiar"]
            kamera_prost(sc, z["kierunek"], pts, w, h)
            render(sc, os.path.join(wyj, z["plik"]), w, h)
            bp.log("RZAD", z["plik"])
            continue
        d = modele[z["model"]]
        sc = bp.nowa_scena(d["klipy"][0]["fps"] if d.get("klipy") else 30)
        m = bp.zbuduj_postac(d, tex)
        inne = [bp.zbuduj_postac(modele[i], tex) for i in z.get("dodatkowe", [])]   # np. jajo obok pisklęcia
        bp.przygotuj_render(sc, probki)
        sk = bp.skrzynka(m["render"])
        rozmiar_modelu = max(bp.wymiary(sk))
        ziemia(max(10.0, rozmiar_modelu * 4), z.get("ziemia", TRAWA if z.get("trawa", True) else bp.PODLOZE))
        if z.get("obrys"):
            bp.dodaj_obrys(m["render"], max(0.02, 0.0085 * rozmiar_modelu))
        roz = int(z.get("rozmiar", 480))
        if z["typ"] == "widoki":
            poza(sc, m, z.get("poza"))
            for nazwa, kier in z["widoki"].items():
                bp.kamera(sc, kier, bp.punkty(m["render"]), bool(z.get("orto")), margines=z.get("margines", 1.1),
                          ogniskowa=z.get("ogniskowa", 60.0))
                render(sc, os.path.join(wyj, "%s_%s%s.jpg" % (d["id"], nazwa, z.get("przyrostek", ""))), roz, roz)
            bp.log("WIDOKI", d["id"], ", ".join(z["widoki"]))
        elif z["typ"] == "pasek":
            kl = next(k for k in d["klipy"] if k["n"] == z["klip"])
            bp.ustaw_akcje(m["arm"], m["akcje"][kl["n"]])
            for x in inne:
                bp.ustaw_akcje(x["arm"], x["akcje"].get(kl["n"]))
            pts = []
            for i in range(13):
                f = kl["dlugosc"] * i / 12.0
                sc.frame_set(int(f), subframe=f - int(f))
                pts += bp.punkty(m["render"] + [o for x in inne for o in x["render"]])
            bp.kamera(sc, z["kierunek"], pts, True, margines=1.06)
            for i, f in enumerate(z["klatki"]):
                sc.frame_set(int(f), subframe=f - int(f))
                render(sc, os.path.join(wyj, "%s_%s_%02d.jpg" % (d["id"], kl["n"], i)), roz, roz)
            bp.log("PASEK", d["id"], kl["n"], len(z["klatki"]))
    bp.log("GOTOWE widoki: %d zadań" % len(zadania))


if __name__ == "__main__":
    main()
