# -*- coding: utf-8 -*-
"""Blender: scena wyboru klasy z bohaterami na podeście (koło postaci) — render z kamery gracza.

Uruchamiane przez swiat/wybor_klasy/render.py (Blender w tle, plik sali .blend z tools/blender/klocki.py):
    blender -b <sala.blend> --python swiat/wybor_klasy/blender_scena.py -- --bohaterowie <folder> --wyj <plik.jpg>
        [--zapisz <scena.blend>] [--szer 1600] [--probki 64] [--przod rycerz]

<folder>/<id>/<id>.glb = model bohatera (eksport swiat/postacie/biblioteka/podglad_postaci.py --eksport),
<folder>/<id>/<id>_<przedmiot>.glb = przedmioty; każdy przypinany do pustaka/kości o nazwie zaczepu z raportu.
Układ Roblox (x, y, z) -> Blender (x, −z, y). Środek podestu = PRZESUNIECIE z generuj.py.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(nazwa, dom=None):
    return A[A.index(nazwa) + 1] if nazwa in A else dom


TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(TU)))
from swiat.wybor_klasy.generuj import PRZESUNIECIE, GORA_PODESTU  # noqa: E402

FOLDER = arg("--bohaterowie")
WYJ = arg("--wyj")
SZER = int(arg("--szer", "1600"))
PROBKI = int(arg("--probki", "64"))
KOLO_R = 5.3                                   # promień koła postaci na podeście (studs)
KOLEJNOSC = ["rycerz", "zwiadowca", "kot_mag"]  # przód, lewo-tył, prawo-tył (jak na makiecie)
PRZOD = arg("--przod", "rycerz")
KLIP = arg("--klip", "idle")
KLATKA = int(arg("--klatka", "12"))


def rbx(x, y, z):
    """punkt w układzie sceny (względem środka podestu) -> Blender"""
    px, py, pz = PRZESUNIECIE
    return Vector((px + x, -(pz + z), py + y))


def importuj(sciezka):
    przed = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=sciezka)
    return [o for o in bpy.data.objects if o not in przed]


def korzenie(obiekty):
    return [o for o in obiekty if o.parent is None]


def ustaw_bohatera(id_, kat_deg):
    folder = os.path.join(FOLDER, id_)
    nowe = importuj(os.path.join(folder, id_ + ".glb"))
    # przedmioty: zaczep z raportu (np. RightGripAttachment) -> pustak/kość o tej nazwie w modelu
    zaczepy = {o.name.split(".")[0]: o for o in nowe}
    for o in nowe:  # znaczniki zaczepów (_Att) to małe siatki — w renderze niewidoczne
        if o.name.split(".")[0].endswith("_Att"):
            o.hide_render = True
            o.hide_viewport = True
    # poza z klipu „idle” (zamiast pozy spoczynkowej z rozłożonymi rękami)
    for o in nowe:
        if o.type == "ARMATURE":
            akcja = bpy.data.actions.get(KLIP) or next((a for a in bpy.data.actions if a.name.startswith(KLIP)), None)
            if akcja:
                o.animation_data_create()
                o.animation_data.action = akcja
                if getattr(akcja, "slots", None) and len(akcja.slots):
                    o.animation_data.action_slot = akcja.slots[0]
    bpy.context.scene.frame_set(KLATKA)
    for plik in sorted(os.listdir(folder)):
        if not (plik.startswith(id_ + "_") and plik.endswith(".glb")):
            continue
        rap = os.path.join(folder, plik[:-4] + "_raport.json")
        if not os.path.exists(rap):
            continue
        zaczep = json.load(open(rap, encoding="utf-8")).get("zaczep")
        przedm = importuj(os.path.join(folder, plik))
        cel = zaczepy.get(zaczep.replace("Attachment", "_Att")) if zaczep else None
        if cel is None:
            print("SCENA | brak zaczepu", zaczep, "dla", plik)
        for o in korzenie(przedm):
            if cel is not None:
                mw = cel.matrix_world.copy()
                o.parent = cel
                o.matrix_world = mw @ o.matrix_world
            nowe.append(o)
        nowe += [o for o in przedm if o.parent is not None]
    # cały bohater pod jednym pustakiem: obrót wokół pionu i miejsce na kole
    piwot = bpy.data.objects.new("Bohater_" + id_, None)
    bpy.context.scene.collection.objects.link(piwot)
    for o in korzenie(nowe):
        o.parent = piwot
    a = math.radians(kat_deg)
    x, z = KOLO_R * math.sin(a), KOLO_R * math.cos(a)
    piwot.location = rbx(x, GORA_PODESTU, z)
    # model patrzy na −Y Blendera (= +Z Roblox, w stronę kamery); boczni lekko obróceni ku środkowi sceny
    piwot.rotation_euler = (0, 0, a * 0.3)
    bpy.context.view_layer.update()
    return piwot


def swiatla():
    swiat = bpy.context.scene.world or bpy.data.worlds.new("Swiat")
    bpy.context.scene.world = swiat
    swiat.use_nodes = True
    bg = swiat.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.05, 0.04, 0.06, 1)
        bg.inputs[1].default_value = 0.6
    for o in list(bpy.data.objects):
        if o.type == "LIGHT":
            bpy.data.objects.remove(o)

    def lampa(nazwa, typ, pos, moc, kolor, rozmiar=0.5, cel=None, kat=None):
        d = bpy.data.lights.new(nazwa, typ)
        d.energy, d.color = moc, kolor
        if hasattr(d, "shadow_soft_size"):
            d.shadow_soft_size = rozmiar
        if typ == "SPOT":
            d.spot_size, d.spot_blend = math.radians(kat or 40), 0.5
        o = bpy.data.objects.new(nazwa, d)
        bpy.context.scene.collection.objects.link(o)
        o.location = pos
        if cel is not None:
            o.rotation_euler = (pos - cel).to_track_quat("Z", "Y").to_euler()
        return o

    cieply = (1.0, 0.62, 0.3)
    # światło przy każdym „Ogniu” sali (pochodnie, kominek, świece)
    for o in bpy.data.objects:
        if "Ogień" in o.name and "rdzeń" not in o.name and o.type == "MESH":
            moc = 2600 if "kominka" in o.name else (180 if "Świecznik" in o.name else 900)
            lampa("L_" + o.name, "POINT", o.matrix_world.translation.copy(), moc, cieply, 0.6)
    lampa("Reflektor podestu", "SPOT", rbx(0, 20, 2), 9000, (1.0, 0.86, 0.6), 2.0, cel=rbx(0, 2, 0), kat=38)
    lampa("Wypełnienie", "AREA", rbx(0, 12, 18), 1600, (0.85, 0.85, 1.0), 10.0, cel=rbx(0, 4, 0))


def kamera():
    with open(os.path.join(TU, "ujecia.json"), encoding="utf-8") as f:
        uj = json.load(f)[0]
    (cx, cy, cz), (tx, ty, tz), mm = uj[1], uj[2], uj[3]
    c = bpy.data.cameras.new("Gracz")
    c.lens = mm
    o = bpy.data.objects.new("Gracz", c)
    bpy.context.scene.collection.objects.link(o)
    pos, cel = Vector((cx, -cz, cy)), Vector((tx, -tz, ty))
    o.location = pos
    o.rotation_euler = (pos - cel).to_track_quat("Z", "Y").to_euler()
    bpy.context.scene.camera = o


def main():
    kol = KOLEJNOSC[:]
    i = kol.index(PRZOD)
    kol = kol[i:] + kol[:i]
    for id_, kat in zip(kol, (0, -120, 120)):
        ustaw_bohatera(id_, kat)
    swiatla()
    kamera()
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = PROBKI
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = SZER, int(SZER * 9 / 16)
    sc.view_settings.view_transform = "AgX" if "AgX" in [v.identifier for v in sc.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    sc.render.image_settings.file_format = "JPEG"
    sc.render.filepath = WYJ
    bpy.ops.render.render(write_still=True)
    if arg("--zapisz"):
        bpy.ops.wm.save_as_mainfile(filepath=arg("--zapisz"))
    print("SCENA | render", WYJ)


main()
