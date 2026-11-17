# -*- coding: utf-8 -*-
"""Render podglądów areny w Blenderze (woła go podglad.py --blender; ścieżki bezwzględne, bez okna):

    blender -b --factory-startup -t 2 --python-exit-code 1 --python swiat/areny_walki/render_blender.py -- \
        --z-json <czesci.json> --render <folder> --ujecia <ujecia.json> --szer 960 --probki 16 \
        --mgla 300 --niebo r,g,b --kolor-mgly r,g,b

Scenę buduje tools/blender/klocki.py (ten sam import części co mapy — wczytany jako moduł, bez zmian w nim). Własne
tu: niebo w kolorze nastroju areny, słońce za plecami kamery planu ogólnego, MGŁA ODLEGŁOŚCI w materiałach (węzeł
Camera Data → odległość → 0,85·(1 − e^(−d/mgla)) → mieszanie z emisją koloru mgły) — przybliżenie lokalnej mgły
Atmosphere z gry; działa tak samo w Blenderze 4.x i 5.x (bez kompozytora).
"""
import importlib.util
import json
import math
import os
import sys

import bpy
from mathutils import Vector

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(k, d=None):
    return A[A.index(k) + 1] if k in A else d


TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
_spec = importlib.util.spec_from_file_location("klocki_aren", os.path.join(REPO, "tools", "blender", "klocki.py"))
K = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(K)


def wektor(s):
    return tuple(float(v) for v in s.split(","))


def z_json_z_cieniami(sciezka):
    """Jak klocki.z_json, ale z 16. polem części: bit 2 = bez cienia (CastShadow = false w Roblox) → visible_shadow."""
    with open(sciezka, encoding="utf-8") as f:
        d = json.load(f)
    siatki = K.siatki_jednostkowe()
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    korzen = bpy.data.collections.new("Arena")
    bpy.context.scene.collection.children.link(korzen)
    kolekcje = [K.kolekcja(g, korzen) for g in d["grupy"]]
    from mathutils import Matrix
    for c in d["czesci"]:
        ks, gi, x, y, z, rx, ry, rz, sx, sy, sz, kolor, mi, alfa, nazwa = c[:15]
        cechy = int(c[15]) if len(c) > 15 else 0
        mat = d["materialy"][mi]
        ob = bpy.data.objects.new(nazwa, siatki.get(ks, siatki[0]))
        if ks == 1:
            sred = min(sx, sy, sz)
            skala = (sred, sred, sred)
        elif ks == 2:
            sred = min(sy, sz)
            skala = (sx, sred, sred)
        else:
            skala = (sx, sz, sy)
        R = K.C @ K.obrot_rbx(rx, ry, rz) @ K.CT
        ob.matrix_world = Matrix.Translation(K.C @ Vector((x, y, z))) @ R.to_4x4() @ Matrix.Diagonal((skala[0], skala[1], skala[2], 1.0))
        kolekcje[gi].objects.link(ob)
        ob.material_slots[0].link = "OBJECT"
        ob.material_slots[0].material = K.material(kolor, mat, alfa)
        if cechy & 2 and hasattr(ob, "visible_shadow"):
            ob.visible_shadow = False
    import re
    for m in bpy.data.materials:                               # półprzezroczysty Neon świeci słabiej (jak w Roblox)
        if m.use_nodes and re.search(r"_a\d\d$", m.name):
            b = m.node_tree.nodes.get("Principled BSDF")
            if b and "Emission Strength" in b.inputs and b.inputs["Emission Strength"].default_value > 1.0:
                b.inputs["Emission Strength"].default_value = 0.8
    print("ARENA | zbudowano %d części" % len(d["czesci"]), flush=True)


WEZLY_MGLY = []


def ustaw_mgle(odl):
    for w in WEZLY_MGLY:
        w.inputs[1].default_value = odl


def mgla_w_materialach(odl, kolor):
    """Każdy materiał: Principled → Mix Shader z Emission (kolor mgły), czynnik z odległości od kamery."""
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        nt = m.node_tree
        wyj = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if not wyj or not bsdf:
            continue
        kam = nt.nodes.new("ShaderNodeCameraData")
        dz = nt.nodes.new("ShaderNodeMath")
        dz.operation = "DIVIDE"
        dz.inputs[1].default_value = odl
        WEZLY_MGLY.append(dz)
        mn = nt.nodes.new("ShaderNodeMath")
        mn.operation = "MULTIPLY"
        mn.inputs[1].default_value = -1.0
        ex = nt.nodes.new("ShaderNodeMath")
        ex.operation = "EXPONENT"
        od = nt.nodes.new("ShaderNodeMath")
        od.operation = "SUBTRACT"
        od.inputs[0].default_value = 1.0
        sk = nt.nodes.new("ShaderNodeMath")
        sk.operation = "MULTIPLY"
        sk.inputs[1].default_value = 0.85
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (K.srgb_lin(kolor[0]), K.srgb_lin(kolor[1]), K.srgb_lin(kolor[2]), 1.0)
        em.inputs["Strength"].default_value = 1.0
        mix = nt.nodes.new("ShaderNodeMixShader")
        wyjscie_kam = kam.outputs.get("View Distance") or kam.outputs[1]
        nt.links.new(wyjscie_kam, dz.inputs[0])
        nt.links.new(dz.outputs[0], mn.inputs[0])
        nt.links.new(mn.outputs[0], ex.inputs[0])
        nt.links.new(ex.outputs[0], od.inputs[1])
        nt.links.new(od.outputs[0], sk.inputs[0])
        nt.links.new(sk.outputs[0], mix.inputs[0])
        nt.links.new(bsdf.outputs[0], mix.inputs[1])
        nt.links.new(em.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], wyj.inputs["Surface"])


def swiat_i_slonce(niebo):
    sc = bpy.context.scene
    w = bpy.data.worlds.new("NieboAreny")
    w.use_nodes = True
    nt = w.node_tree
    tlo = nt.nodes.get("Background")
    kol = (K.srgb_lin(niebo[0]), K.srgb_lin(niebo[1]), K.srgb_lin(niebo[2]), 1.0)
    tlo.inputs[0].default_value = kol
    tlo.inputs[1].default_value = 0.5                          # światło otoczenia słabsze niż widok nieba
    widok = nt.nodes.new("ShaderNodeBackground")
    widok.inputs[0].default_value = kol
    widok.inputs[1].default_value = 1.0
    sciezka = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(sciezka.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(tlo.outputs[0], mix.inputs[1])
    nt.links.new(widok.outputs[0], mix.inputs[2])
    wyj = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    nt.links.new(mix.outputs[0], wyj.inputs["Surface"])
    sc.world = w
    sl = bpy.data.lights.new("Slonce", "SUN")
    sl.energy = 3.2
    sl.color = (1.0, 0.95, 0.85)
    sl.angle = math.radians(5)
    ob = bpy.data.objects.new("Slonce", sl)
    sc.collection.objects.link(ob)
    # światło biegnie w świecie Roblox ku +Z i w dół (słońce za plecami kamery planu ogólnego); Blender: (x, −z, y)
    kier = Vector((0.32, -0.62, -0.72)).normalized()
    ob.rotation_euler = kier.to_track_quat("-Z", "Y").to_euler()
    ee = sc.eevee
    for atr, wart in (("taa_render_samples", int(arg("--probki", "16"))), ("use_shadows", True), ("use_gtao", True),
                      ("use_raytracing", False), ("shadow_ray_count", 1), ("shadow_step_count", 6)):
        if hasattr(ee, atr):
            try:
                setattr(ee, atr, wart)
            except Exception:
                pass
    sc.view_settings.view_transform = "Standard"


def main():
    z_json_z_cieniami(arg("--z-json"))
    swiat_i_slonce(wektor(arg("--niebo", "0.5,0.7,0.95")))
    mgla_w_materialach(float(arg("--mgla", "300")), wektor(arg("--kolor-mgly", "0.8,0.85,0.8")))
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in
                                                                       bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    szer = int(arg("--szer", "960"))
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 86
    folder = arg("--render")
    os.makedirs(folder, exist_ok=True)
    with open(arg("--ujecia"), encoding="utf-8") as f:
        ujecia = json.load(f)
    for nazwa, pos, cel, ogn, orto in ujecia:
        cam = K.kamera("KAMERA_" + nazwa, pos, cel, float(ogn), orto)
        cam.data.clip_end = 3000.0
        if orto:
            # rzut z góry: u góry kadru tło za walczącymi (−Z sceny = +Z świata Roblox = −Y Blendera), bez mgły
            cam.rotation_euler = (0.0, 0.0, math.pi)
            sc.render.resolution_x = sc.render.resolution_y = min(szer, 1100)
            ustaw_mgle(1e9)
        else:
            sc.render.resolution_x, sc.render.resolution_y = szer, int(szer * 9 / 16)
            ustaw_mgle(float(arg("--mgla", "300")))
        sc.render.resolution_percentage = 100
        sc.camera = cam
        sc.render.filepath = os.path.join(folder, nazwa + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("ARENA | render %s" % sc.render.filepath, flush=True)


main()
