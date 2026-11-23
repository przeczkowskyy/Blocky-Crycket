# -*- coding: utf-8 -*-
"""Rendery mapy v2 — uruchamiane W BLENDERZE (w tle) przez mapa2.py, pod wspólną blokadą biblioteki.

    blender -b --factory-startup --python blender_mapa2.py -- <pakiet.json> <zadania.json> <folder wyników>

Zadanie {"typ": "scena2", "plik", "rozmiar": [w, h], "modele": [{id, poz, obrot_y, poza, skala}],
         "instancje": [{"id", "m": [[x, y, z, obrot, skala], …]}]   (układ biblioteki, y = wysokość podstawy),
         "dyski": [{x, z, r, kolor, y, swieci}], "alfa": {id modelu: krycie},
         "kamera": {"typ": "gra", "cel": [x, y, z], "odl", "nachylenie", "fov"}           — jak kamera gry (z południa, fov pionowy)
                 | {"typ": "panorama", "cel": [x, y, z], "patrz_na": [x, y, z], "odl", "nachylenie", "fov"}
                 | {"typ": "orto", "srodek": [x, z], "szer"}                              — z góry, +Z gry u góry obrazu}
Współrzędne w układzie danych biblioteki: (x, z) biblioteki = (−x, −z) gry.
"""
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)

import bpy  # noqa: E402
import bmesh  # noqa: E402
from mathutils import Matrix, Vector  # noqa: E402

import blender_widoki as bw  # noqa: E402  (dodaje bibliotekę do sys.path)

bp = bw.bp


def _niebo(sc):
    """Niebo późnego popołudnia: ciepły horyzont, błękit u góry (zamiast studyjnego tła)."""
    nt = sc.world.node_tree
    ramp = next(n for n in nt.nodes if n.type == "VALTORGB")
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.45, (*bp.lin("D8C8B8"), 1.0)
    el[-1].position, el[-1].color = 0.85, (*bp.lin("7FA8E0"), 1.0)
    for e in list(el)[1:-1]:
        e.position, e.color = 0.55, (*bp.lin("F2D8B8"), 1.0)
    tlo = nt.nodes.get("Background")
    tlo.inputs[1].default_value = 0.9


def _alfa(obiekty, krycie):
    for ob in obiekty:
        for mat in ob.data.materials:
            bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf:
                bsdf.inputs["Alpha"].default_value = krycie
            for atr, w in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
                try:
                    setattr(mat, atr, w)
                except Exception:
                    pass


def _kamera(sc, k, w, h):
    cam = bpy.data.objects.get("_Kamera")
    if cam is None:
        cam = bpy.data.objects.new("_Kamera", bpy.data.cameras.new("_Kamera"))
        sc.collection.objects.link(cam)
    cd = cam.data
    sc.camera = cam
    if k["typ"] == "orto":
        cd.type, cd.sensor_fit = "ORTHO", "HORIZONTAL"
        cd.ortho_scale = k["szer"]
        cd.clip_start, cd.clip_end = 1.0, 3000.0
        cx, cz = k["srodek"]
        cam.location = bp.do_blendera((cx, 900.0, cz))
        cam.rotation_euler = (0.0, 0.0, 0.0)                  # obraz: +Y Blendera (= +Z gry) u góry, +X Blendera (= −X gry) w prawo
        return
    cel = Vector(k["cel"])
    e = math.radians(k["nachylenie"])
    if k["typ"] == "gra":
        # gra: kamera na południe od celu (−Z gry = +Z biblioteki), patrzy na północ i w dół
        poz = cel + Vector((0.0, k["odl"] * math.sin(e), k["odl"] * math.cos(e)))
    else:
        p = Vector(k["patrz_na"])
        kier = Vector((p.x - cel.x, 0.0, p.z - cel.z)).normalized()
        poz = cel - kier * (k["odl"] * math.cos(e)) + Vector((0.0, k["odl"] * math.sin(e), 0.0))
    pb, cb = bp.do_blendera(poz), bp.do_blendera(cel)
    cd.type, cd.sensor_fit = "PERSP", "VERTICAL"
    cd.sensor_height = 24.0
    cd.lens = 12.0 / math.tan(math.radians(k["fov"]) / 2.0)     # pionowe pole widzenia jak FieldOfView w Roblox
    cd.clip_start, cd.clip_end = 0.5, 2500.0
    cam.location = pb
    cam.rotation_euler = (cb - pb).to_track_quat("-Z", "Y").to_euler()


def scena2(z, modele, tex, wyj, probki):
    sc = bp.nowa_scena(30)
    for e in z["modele"]:
        m = bp.zbuduj_postac(modele[e["id"]], tex)
        arm = m["arm"]
        bw.poza(sc, m, e.get("poza"))
        wart = {pb_.name: (pb_.location.copy(), pb_.rotation_euler.copy()) for pb_ in arm.pose.bones}
        if arm.animation_data:
            arm.animation_data.action = None
        for pb_ in arm.pose.bones:
            pb_.location, pb_.rotation_euler = wart[pb_.name]
        arm.location = bp.do_blendera(e.get("poz", (0.0, 0.0, 0.0)))
        arm.rotation_euler = (0.0, 0.0, math.radians(e.get("obrot_y", 0.0)))
        sk = float(e.get("skala", 1.0))
        arm.scale = (sk, sk, sk)
        if e["id"] in z.get("alfa", {}):
            _alfa(m["render"], z["alfa"][e["id"]])
        bpy.context.view_layer.update()
    for nr, dsk in enumerate(z.get("dyski", [])):
        me = bpy.data.meshes.new("_dysk")
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=True, radius=dsk["r"], segments=max(24, min(96, int(dsk["r"] * 1.2))))
        bm.to_mesh(me)
        bm.free()
        if dsk.get("swieci"):
            mat = bp.nowy_material("_Dysk%d" % nr)
            nt = mat.node_tree
            for n in list(nt.nodes):
                nt.nodes.remove(n)
            wy, em = nt.nodes.new("ShaderNodeOutputMaterial"), nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*bp.lin(dsk["kolor"]), 1.0)
            em.inputs["Strength"].default_value = 2.0
            nt.links.new(em.outputs["Emission"], wy.inputs["Surface"])
        else:
            mat = bp.material_prosty("_Dysk%d" % nr, dsk["kolor"], 0.95)
        me.materials.append(mat)
        ob = bpy.data.objects.new("_Dysk%d" % nr, me)
        sc.collection.objects.link(ob)
        ob.location = bp.do_blendera((dsk["x"], dsk["y"], dsk["z"]))
    for ins in z.get("instancje", []):                         # rekwizyt zbudowany raz, potem kopie z położeniem i wysokością
        m = bp.zbuduj_postac(modele[ins["id"]], tex)
        for x, y, zz, rot, sk in ins["m"]:
            for ob in m["render"]:
                c = ob.copy()
                sc.collection.objects.link(c)
                c.parent = None
                for mod in list(c.modifiers):
                    c.modifiers.remove(mod)
                c.matrix_world = (Matrix.Translation(bp.do_blendera((x, y, zz))) @ Matrix.Rotation(math.radians(rot), 4, "Z")
                                  @ Matrix.Scale(sk, 4))
        for ob in m["render"]:
            ob.hide_render = True
    bp.przygotuj_render(sc, probki)
    _niebo(sc)
    w, h = z["rozmiar"]
    _kamera(sc, z["kamera"], w, h)
    sc.render.resolution_x, sc.render.resolution_y = int(w), int(h)
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.filepath = os.path.join(wyj, z["plik"])
    bpy.ops.render.render(write_still=True)
    bp.log("SCENA", z["plik"])


def main():
    import json
    arg = sys.argv[sys.argv.index("--") + 1:]
    with open(arg[0], encoding="utf-8") as f:
        modele = {d["id"]: d for d in json.load(f)["modele"]}
    with open(arg[1], encoding="utf-8") as f:
        zadania = json.load(f)
    wyj = os.path.abspath(arg[2])
    os.makedirs(wyj, exist_ok=True)
    tex = os.path.join(wyj, "_tekstury")
    for z in zadania:
        scena2(z, modele, tex, wyj, int(z.get("probki", 16)))
    bp.log("GOTOWE mapa v2: %d widoków" % len(zadania))


if __name__ == "__main__":
    main()
