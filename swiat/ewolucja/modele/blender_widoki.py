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
from mathutils import Matrix, Vector  # noqa: E402

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


def kamera_persp(sc, kierunek, pts, szer, wys, ogniskowa=55.0, margines=1.08):
    # Kamera perspektywiczna dla obrazu prostokątnego: kadr dopasowany do punktów.
    d = (bp.C3 @ Vector(kierunek)).normalized()
    przod = -d
    prawo = przod.cross(Vector((0.0, 0.0, 1.0))).normalized()
    gora = prawo.cross(przod).normalized()
    xs, ys, zs = [p.dot(prawo) for p in pts], [p.dot(gora) for p in pts], [p.dot(d) for p in pts]
    sr = prawo * ((min(xs) + max(xs)) / 2) + gora * ((min(ys) + max(ys)) / 2) + d * ((min(zs) + max(zs)) / 2)
    cam = bpy.data.objects.get("_Kamera")
    if cam is None:
        cam = bpy.data.objects.new("_Kamera", bpy.data.cameras.new("_Kamera"))
        sc.collection.objects.link(cam)
    cd = cam.data
    cd.type, cd.lens, cd.sensor_fit = "PERSP", ogniskowa, "HORIZONTAL"
    tx = cd.sensor_width / 2.0 / ogniskowa
    ty = tx * wys / float(szer)
    odl = max((p - sr).dot(d) + max(abs((p - sr).dot(prawo)) / tx, abs((p - sr).dot(gora)) / ty) * margines for p in pts)
    cd.clip_start, cd.clip_end = 0.05, odl + 800.0
    cam.location = sr + d * odl
    cam.rotation_euler = przod.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam


def scena(sc, z, modele, tex, wyj, probki):
    # Kilka modeli w jednej scenie (każdy w swojej pozie, położeniu, obrocie, skali; opcjonalnie czarna sylwetka).
    import math
    czarny = None
    pts = []
    for e in z["modele"]:
        m = bp.zbuduj_postac(modele[e["id"]], tex)
        arm = m["arm"]
        poza(sc, m, e.get("poza"))
        wart = {pb.name: (pb.location.copy(), pb.rotation_euler.copy()) for pb in arm.pose.bones}
        if arm.animation_data:
            arm.animation_data.action = None                    # zamroź pozę: inne modele mają inne klatki
        for pb in arm.pose.bones:
            pb.location, pb.rotation_euler = wart[pb.name]
        arm.location = bp.do_blendera(e.get("poz", (0.0, 0.0, 0.0)))
        arm.rotation_euler = (0.0, 0.0, math.radians(e.get("obrot_y", 0.0)))
        sk = float(e.get("skala", 1.0))
        arm.scale = (sk, sk, sk)
        if e.get("czarny"):
            if czarny is None:
                czarny = bp.nowy_material("_Czarny")
                nt = czarny.node_tree
                for n in list(nt.nodes):
                    nt.nodes.remove(n)
                wy, em = nt.nodes.new("ShaderNodeOutputMaterial"), nt.nodes.new("ShaderNodeEmission")
                em.inputs["Color"].default_value = (0.004, 0.002, 0.008, 1.0)
                nt.links.new(em.outputs["Emission"], wy.inputs["Surface"])
            for ob in m["render"]:
                ob.data.materials.clear()
                ob.data.materials.append(czarny)
        bpy.context.view_layer.update()
        if not z.get("kadr") or e["id"] in z["kadr"]:
            pts += bp.punkty(m["render"])
    for nr, dsk in enumerate(z.get("dyski", [])):               # płaty ziemi: koła w kolorze strefy
        me = bpy.data.meshes.new("_dysk")
        bm = bmesh.new()
        bmesh.ops.create_circle(bm, cap_ends=True, radius=dsk["r"], segments=48)
        bm.to_mesh(me)
        bm.free()
        if dsk.get("swieci"):
            mat = bp.nowy_material("_Dysk%d" % nr)
            nt = mat.node_tree
            for n in list(nt.nodes):
                nt.nodes.remove(n)
            wy, em = nt.nodes.new("ShaderNodeOutputMaterial"), nt.nodes.new("ShaderNodeEmission")
            em.inputs["Color"].default_value = (*bp.lin(dsk["kolor"]), 1.0)
            em.inputs["Strength"].default_value = 2.5
            nt.links.new(em.outputs["Emission"], wy.inputs["Surface"])
        else:
            mat = bp.material_prosty("_Dysk%d" % nr, dsk["kolor"], 0.95)
        me.materials.append(mat)
        ob = bpy.data.objects.new("_Dysk%d" % nr, me)
        bpy.context.scene.collection.objects.link(ob)
        ob.location = bp.do_blendera((dsk["x"], dsk["y"], dsk["z"]))
    for ins in z.get("instancje", []):                         # rekwizyt zbudowany raz, potem kopie z położeniem
        m = bp.zbuduj_postac(modele[ins["id"]], tex)
        for x, zz, rot, sk in ins["m"]:
            for ob in m["render"]:
                c = ob.copy()
                bpy.context.scene.collection.objects.link(c)
                c.parent = None
                for mod in list(c.modifiers):
                    c.modifiers.remove(mod)
                c.matrix_world = (Matrix.Translation(bp.do_blendera((x, 0.0, zz))) @ Matrix.Rotation(math.radians(rot), 4, "Z")
                                  @ Matrix.Scale(sk, 4))
        for ob in m["render"]:
            ob.hide_render = True
    if z.get("kadr_punkty"):
        pts = [bp.do_blendera(q) for q in z["kadr_punkty"]]
    bp.przygotuj_render(sc, probki)
    if z.get("ziemia"):
        ziemia(700.0, z["ziemia"])
    w, h = z["rozmiar"]
    if z.get("orto"):
        kamera_prost(sc, z["kierunek"], pts, w, h, margines=z.get("margines", 1.08))
    else:
        kamera_persp(sc, z["kierunek"], pts, w, h, z.get("ogniskowa", 55.0), z.get("margines", 1.08))
    sc.render.resolution_x, sc.render.resolution_y = int(w), int(h)
    sc.render.film_transparent = not z.get("ziemia")
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.filepath = os.path.join(wyj, z["plik"])
    bpy.ops.render.render(write_still=True)
    bp.log("SCENA", z["plik"])


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
        if z["typ"] == "scena":
            scena(bp.nowa_scena(30), z, modele, tex, wyj, probki)
            continue
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
        elif z["typ"] == "bieg":
            kl = next(k for k in d["klipy"] if k["n"] == z["klip"])
            bp.ustaw_akcje(m["arm"], m["akcje"][kl["n"]])
            n, tempo = kl["dlugosc"], z["v_gry"] / z["v_klipu"]
            krata = ziemia(600.0, "FFFFFF")
            mat = krata.data.materials[0]
            nt = mat.node_tree
            bsdf = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
            tc, sz_ = nt.nodes.new("ShaderNodeTexCoord"), nt.nodes.new("ShaderNodeTexChecker")
            sz_.inputs["Scale"].default_value = 1.0 / z.get("kratka", 4.0)
            sz_.inputs["Color1"].default_value = (*bp.lin("5FB04C"), 1.0)
            sz_.inputs["Color2"].default_value = (*bp.lin("4A953F"), 1.0)
            nt.links.new(tc.outputs["Object"], sz_.inputs["Vector"])
            nt.links.new(sz_.outputs["Color"], bsdf.inputs["Base Color"])
            pts = []
            for i in range(13):
                f = n * i / 12.0
                sc.frame_set(int(f), subframe=f - int(f))
                pts += bp.punkty(m["render"])
            bp.kamera(sc, z["kierunek"], pts, True, margines=1.5)
            for i in range(int(z["klatek"])):                   # klip w tempie gry, ziemia jedzie w tył z prędkością gry
                f = (i * tempo) % n
                sc.frame_set(int(f), subframe=f - int(f))
                krata.location = bp.do_blendera((0.0, 0.02, -z["v_gry"] * i / 30.0))
                render(sc, os.path.join(wyj, "%s_%s_%03d.jpg" % (d["id"], z.get("nazwa", "bieg"), i)), roz, roz)
            bp.log("BIEG", d["id"], kl["n"], "tempo %.2f" % tempo)
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
