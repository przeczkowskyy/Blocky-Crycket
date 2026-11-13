# -*- coding: utf-8 -*-
"""Blender 5.0 (w tle): z pakietu JSON biblioteki postac.py buduje postacie i akcesoria, robi raport z limitami
Roblox, eksport FBX/GLB/.blend, rendery prezentacyjne, ikony, film MP4 i arkusz klatek.

    blender -b --factory-startup --python-exit-code 1 --python blender_postac.py -- --json <pakiet.json> --wyj <folder>
        [--render] [--ikona] [--film KLIP] [--klatki KLIP] [--fbx] [--glb] [--zapisz-blend]
        [--bez-obrysu] [--szer 900] [--probki 16] [--ffmpeg <ffmpeg.exe>]
    blender -b --factory-startup --python-exit-code 1 --python blender_postac.py -- --kontrola <eksport_oczekiwane.json>

Zwykle wołany przez podglad_postaci.py (pod wspólną blokadą Blendera). Model w pakiecie może mieć własne
"zadania": {"render", "ikona", "film", "klatki", "fbx", "glb", "blend"} — wtedy one rozstrzygają, nie flagi.
Raport (<id>_raport.json + linie „POSTAC |”) powstaje zawsze.

Co powstaje (dla modelu o id X, w folderze --wyj):
  X_plansza.jpg  — 2×2: kadr bohaterski 3/4 (z komiksowym OBRYSEM jako efektem renderu) | przód (z szarym manekinem
                   R15 dla skali) / bok (prawa strona) | tył; trzy rzuty bez obrysu (uczciwa geometria)
  X_bohater.jpg  — kadr bohaterski w pełnej rozdzielczości;  X_ikona.png — 512 px, przezroczyste tło, obrys
  X_<klip>.mp4   — film H.264 yuv420p (pętla ×3);  X_<klip>_klatki.jpg — 8 klatek klipu (4×2, czytaj wierszami)
  X.fbx, X__<klip>.fbx (jeden klip na plik, jak każe Roblox), X.glb (wszystkie klipy), X.blend, X_tekstury/*.png

Układ: dane (x, y, z) w studach, Y w górę, przód +Z → Blender (x, −z, y): postać patrzy w −Y (widok Front), lewa
strona postaci to +X. Każda kość ma w spoczynku osie równoległe do osi modelu (kość skierowana w górę, roll 0), więc
obroty z klipów wchodzą do Blendera 1:1 w trybie Euler ZXY (= Ry·Rx·Rz Roblox).
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import time

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

C3 = Matrix(((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)))   # dane (x, y, z) -> Blender (x, -z, y)
C3T = C3.transposed()
SCIEZKI = {"obrot": "rotation_euler", "przes": "location", "skala": "scale"}
INTERP = {"gladko": "BEZIER", "liniowo": "LINEAR", "stale": "CONSTANT"}
TLO = "D9D2E8"            # tło renderów prezentacyjnych (jasny lawendowy) — horyzont
TLO_GORA = "F4F0FA"       # góra gradientu świata
TLO_DOL = "6E6488"        # dół gradientu świata
PODLOZE = "A69CBB"        # podłoże pod postacią
MANEKIN = "9AA0AC"        # manekin skali
BOHATER = (0.5, 0.16, 1.0)  # kierunek kadru bohaterskiego (dane: od postaci ku kamerze) — 3/4 od lewej strony postaci
OGNISKOWA = 70.0          # mm; dłuższa ogniskowa = mniej zniekształceń perspektywy


def log(*a):
    print("POSTAC |", *a, flush=True)


def argumenty():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(description="Postacie z brył: budowa, raport, eksport, rendery")
    ap.add_argument("--json")
    ap.add_argument("--wyj")
    ap.add_argument("--render", action="store_true")
    ap.add_argument("--ikona", action="store_true")
    ap.add_argument("--film", default=None)
    ap.add_argument("--klatki", default=None)
    ap.add_argument("--fbx", action="store_true")
    ap.add_argument("--glb", action="store_true")
    ap.add_argument("--zapisz-blend", action="store_true")
    ap.add_argument("--bez-obrysu", action="store_true")
    ap.add_argument("--szer", type=int, default=900)
    ap.add_argument("--probki", type=int, default=16)
    ap.add_argument("--ffmpeg", default=None)
    ap.add_argument("--kontrola", default=None, help="plik eksport_oczekiwane.json: wczytaj eksporty i porównaj")
    return ap.parse_args(argv)


# --------------------------------------------------------------------------- drobiazgi
def lin(h):
    """RRGGBB -> liniowe RGB (dla wejść shaderów)."""
    def k(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(k(int(h[i:i + 2], 16) / 255.0) for i in (0, 2, 4))


def srgb(h):
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def obrot_dane(r):
    """(rx, ry, rz) w stopniach, kolejność Roblox Ry·Rx·Rz -> macierz 3×3 w układzie danych."""
    rx, ry, rz = (math.radians(v) for v in r)
    return Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X") @ Matrix.Rotation(rz, 3, "Z")


def do_blendera(p):
    return C3 @ Vector(p)


def macierz_b(p, r):
    """4×4 w Blenderze dla położenia p i obrotu r (dane)."""
    return Matrix.Translation(do_blendera(p)) @ (C3 @ obrot_dane(r) @ C3T).to_4x4()


def nazwa_att(zaczep):
    return (zaczep[:-len("Attachment")] if zaczep.endswith("Attachment") else zaczep) + "_Att"


def nowa_scena(fps=30):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "NONE"                        # 1 jednostka Blendera = 1 stud (create.roblox.com/docs/art/blender)
    sc.unit_settings.scale_length = 1.0
    sc.unit_settings.system_rotation = "DEGREES"
    sc.render.fps, sc.render.fps_base = int(fps), 1.0
    return sc


def nowy_material(nazwa):
    m = bpy.data.materials.new(nazwa)
    if m.node_tree is None:
        m.use_nodes = True
    return m


def zaznacz(obiekty):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in obiekty:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obiekty[0]


# --------------------------------------------------------------------------- geometria brył
def _pierscien(n, hx, hz, y, s=1.0):
    rk = s / math.cos(math.pi / n)                           # ściany (a nie rogi) dotykają skrzynki: dokładny rozmiar
    return [(hx * rk * math.cos(2 * math.pi * (i + 0.5) / n), y, hz * rk * math.sin(2 * math.pi * (i + 0.5) / n))
            for i in range(n)]


def bryla(c):
    """bmesh bryły w jej układzie lokalnym (dane: X lewo, Y góra, Z przód): zamknięta, fazowana, bez n-gonów."""
    k = c["k"]
    sx, sy, sz = c["s"]
    hx, hy, hz = sx / 2.0, sy / 2.0, sz / 2.0
    if k == "blok":
        v = [(x * hx, y * hy, z * hz) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    elif k == "klin":                                        # jak WedgePart: pionowa ściana +Z, skos ku −Z
        v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, hz), (hx, hy, hz)]
        f = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 4, 5, 1), (0, 3, 4), (1, 5, 2)]
    elif k == "naroznik":                                    # jak CornerWedgePart: wierzchołek (+X, +Y, −Z)
        v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (hx, hy, -hz)]
        f = [(0, 1, 2, 3), (0, 1, 4), (1, 2, 4), (0, 4, 3), (4, 2, 3)]
    elif k in ("walec", "stozek"):
        n = max(3, int(c.get("seg", 8)))
        g = float(c.get("gora", 1.0))
        v = _pierscien(n, hx, hz, -hy)
        if g <= 1e-4:
            v.append((0.0, hy, 0.0))
            f = [tuple(range(n))[::-1]] + [(i, (i + 1) % n, n) for i in range(n)]
        else:
            v += _pierscien(n, hx, hz, hy, g)
            f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + \
                [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    elif k == "kula":
        n = max(4, int(c.get("seg", 8)))
        m = max(2, n // 2)
        rk = 1.0 / math.cos(math.pi / n)                       # jak w walcu: ściany na równiku dotykają skrzynki
        v = [(0.0, hy, 0.0)]
        for j in range(1, m):
            fi = math.pi * j / m
            for i in range(n):
                th = 2 * math.pi * (i + 0.5) / n
                v.append((hx * rk * math.sin(fi) * math.cos(th), hy * math.cos(fi), hz * rk * math.sin(fi) * math.sin(th)))
        v.append((0.0, -hy, 0.0))
        dol = len(v) - 1
        f = [(0, 1 + (i + 1) % n, 1 + i) for i in range(n)]
        for j in range(m - 2):
            for i in range(n):
                a0, a1 = 1 + j * n + i, 1 + j * n + (i + 1) % n
                f.append((a0, a1, a1 + n, a0 + n))
        b = 1 + (m - 2) * n
        f += [(dol, b + i, b + (i + 1) % n) for i in range(n)]
    elif k == "ostroslup":
        tx, tz = c.get("gora", [0.0, 0.0])
        dx, dz = c.get("pg", [0.0, 0.0])
        v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz),
             (dx - tx / 2, hy, dz - tz / 2), (dx + tx / 2, hy, dz - tz / 2), (dx + tx / 2, hy, dz + tz / 2),
             (dx - tx / 2, hy, dz + tz / 2)]
        f = [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    else:
        raise ValueError("nieznany kształt %r" % k)
    bm = bmesh.new()
    vs = [bm.verts.new(p) for p in v]
    for ff in f:
        bm.faces.new([vs[i] for i in ff])
    if k == "ostroslup":                                      # szpic / grzbiet: zlej wierzchołki góry
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5)
        zdegenerowane = [ff for ff in bm.faces if ff.calc_area() < 1e-9]
        if zdegenerowane:
            bmesh.ops.delete(bm, geom=zdegenerowane, context="FACES_ONLY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    faza = min(float(c.get("f", 0.0)), 0.22 * min(sx, sy, sz))
    if faza > 1e-4 and k != "kula":
        bm.normal_update()
        # fazujemy tylko twarde krawędzie (> ~57°): boki walców zostają kanciaste, a krawędzie schodzące do szpica
        # (wierzchołek z ≥ 4 krawędziami) zostają ostre — inaczej faza zjada czubek stożka / ostrosłupa
        kr = [e for e in bm.edges if e.is_manifold and e.calc_face_angle(0.0) > 1.0
              and all(len(v.link_edges) <= 3 for v in e.verts)]
        if kr:
            bmesh.ops.bevel(bm, geom=kr, offset=faza, offset_type="OFFSET", segments=1, profile=0.5,
                            affect="EDGES", clamp_overlap=True)
    ngony = [ff for ff in bm.faces if len(ff.verts) > 4]
    if ngony:
        bmesh.ops.triangulate(bm, faces=ngony, quad_method="BEAUTY", ngon_method="BEAUTY")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


# --------------------------------------------------------------------------- paleta (tekstury) i materiał
def paleta(czesci):
    """{(kolor, materiał): numer komórki}, liczba komórek w rzędzie."""
    komb = sorted({(c["c"], c["m"]) for c in czesci})
    G = 4
    while G * G < len(komb):
        G *= 2
    return {k: i for i, k in enumerate(komb)}, G


def obrazy_palety(id_, komorki, G, materialy, folder, cs=8):
    """Cztery małe tekstury-palety (kolor, metal, szorstkość, emisja) o wspólnym układzie komórek 8×8 px."""
    W = G * cs
    kol = np.zeros((W, W, 4), np.float32)
    kol[..., :3], kol[..., 3] = 0.5, 1.0
    met = np.zeros((W, W, 4), np.float32)
    met[..., 3] = 1.0
    sz = np.zeros((W, W, 4), np.float32)
    sz[..., :3], sz[..., 3] = 0.5, 1.0
    emi = np.zeros((W, W, 4), np.float32)
    emi[..., 3] = 1.0
    for (h, m), i in komorki.items():
        cx, cy = i % G, i // G
        ys, xs = slice(cy * cs, (cy + 1) * cs), slice(cx * cs, (cx + 1) * cs)
        rgb = srgb(h)
        mm = materialy[m]
        kol[ys, xs, :3] = rgb
        met[ys, xs, :3] = mm["metal"]
        sz[ys, xs, :3] = mm["szorstkosc"]
        emi[ys, xs, :3] = [x * mm["emisja"] for x in rgb]
    os.makedirs(folder, exist_ok=True)
    obrazy = {}
    for nazwa, arr, przestrzen in (("kolor", kol, "sRGB"), ("metal", met, "Non-Color"),
                                   ("szorstkosc", sz, "Non-Color"), ("emisja", emi, "sRGB")):
        img = bpy.data.images.new("%s_%s" % (id_, nazwa), W, W, alpha=False)
        img.pixels.foreach_set(arr.ravel())
        sciezka = os.path.join(folder, "%s_%s.png" % (id_, nazwa))
        img.filepath_raw = sciezka
        img.file_format = "PNG"
        img.save()
        img.colorspace_settings.name = przestrzen
        obrazy[nazwa] = img
    return obrazy


def material_modelu(id_, obrazy, sila_emisji=3.0):
    """Jeden materiał na siatkę (wymóg Roblox): wszystkie kolory i cechy materiałów siedzą w teksturach palety."""
    m = nowy_material(id_ + "_Mat")
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")

    def tekstura(nazwa, y):
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image, t.interpolation, t.location = obrazy[nazwa], "Closest", (-520, y)
        return t

    nt.links.new(tekstura("kolor", 300).outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tekstura("metal", 20).outputs["Color"], bsdf.inputs["Metallic"])
    nt.links.new(tekstura("szorstkosc", -260).outputs["Color"], bsdf.inputs["Roughness"])
    nt.links.new(tekstura("emisja", -540).outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = sila_emisji
    return m


def material_prosty(nazwa, kolor, szorstkosc=0.6):
    m = nowy_material(nazwa)
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*lin(kolor), 1.0)
    bsdf.inputs["Roughness"].default_value = szorstkosc
    m.diffuse_color = (*lin(kolor), 1.0)
    return m


def siatka(nazwa, czesci, komorki, G, material):
    """Jedna scalona siatka z listy części (współrzędne modelu), płaskie cieniowanie, UV na komórki palety,
    kolory wierzchołków (atrybut Col) dla narzędzi, które ich używają."""
    wsp, sciany, kom = [], [], []
    for c in czesci:
        bm = bryla(c)
        R, p = obrot_dane(c["r"]), Vector(c["p"])
        bm.verts.index_update()
        baza = len(wsp)
        wsp.extend(tuple(C3 @ (R @ v.co + p)) for v in bm.verts)
        kk = komorki[(c["c"], c["m"])]
        for ff in bm.faces:
            sciany.append(tuple(baza + v.index for v in ff.verts))
            kom.append(kk)
        bm.free()
    me = bpy.data.meshes.new(nazwa)
    me.from_pydata(wsp, [], sciany)
    at = me.attributes.new("komorka", "INT", "FACE")
    at.data.foreach_set("value", kom)
    me.validate(clean_customdata=False)
    me.update()
    n = len(me.polygons)
    kom = [0] * n
    me.attributes["komorka"].data.foreach_get("value", kom)
    try:
        me.shade_flat()
    except AttributeError:
        me.polygons.foreach_set("use_smooth", [False] * n)
    odw = {i: k for k, i in komorki.items()}
    uvs = [0.0] * (2 * len(me.loops))
    cols = [1.0] * (4 * len(me.loops))
    for poly in me.polygons:
        ki = kom[poly.index]
        cx, cy = ki % G, ki // G
        u0, u1, v0, v1 = (cx + 0.25) / G, (cx + 0.75) / G, (cy + 0.25) / G, (cy + 0.75) / G
        rogi = ((u0, v0), (u1, v0), (u1, v1), (u0, v1))
        rgb = lin(odw[ki][0])
        for j, li in enumerate(poly.loop_indices):
            uvs[2 * li], uvs[2 * li + 1] = rogi[j % 4]
            cols[4 * li], cols[4 * li + 1], cols[4 * li + 2] = rgb
    # UWAGA: każdy nowy atrybut może przenieść w pamięci pozostałe warstwy — stare odwołania (np. wynik
    # uv_layers.new) przestają być ważne i zapis przez nie psuje stertę (crash 0xC0000374). Dlatego każdą warstwę
    # wypełniamy od razu po utworzeniu i zawsze pobieramy ją świeżo po nazwie.
    me.attributes.remove(me.attributes["komorka"])
    me.uv_layers.new(name="UVMap")
    me.uv_layers["UVMap"].data.foreach_set("uv", uvs)
    me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
    me.color_attributes["Col"].data.foreach_set("color", cols)
    me.materials.append(material)
    ob = bpy.data.objects.new(nazwa, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# --------------------------------------------------------------------------- szkielet, zaczepy, klipy
def szkielet(d):
    arm_d = bpy.data.armatures.new(d["id"] + "_kosci")
    arm = bpy.data.objects.new(d["id"], arm_d)
    bpy.context.scene.collection.objects.link(arm)
    zaznacz([arm])
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for k in d["kosci"]:
        b = arm_d.edit_bones.new(k["n"])
        h = do_blendera(k["staw"])
        b.head, b.tail, b.roll = h, h + Vector((0.0, 0.0, max(0.05, k["dl"]))), 0.0
        eb[k["n"]] = b
    for k in d["kosci"]:
        if k["rodzic"]:
            eb[k["n"]].parent = eb[k["rodzic"]]
            eb[k["n"]].use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in arm.pose.bones:
        pb.rotation_mode = "ZXY"                              # = Ry·Rx·Rz (CFrame.fromOrientation)
    zle = [b.name for b in arm_d.bones
           if max(abs(b.matrix_local[i][j] - C3[i][j]) for i in range(3) for j in range(3)) > 1e-4]
    if zle:
        log("UWAGA: osie kości nie pokrywają się z osiami modelu:", ", ".join(zle))
    arm.show_in_front = True
    return arm


def przypnij(ob, arm, kosc):
    """Sztywne przypięcie: cała siatka w grupie wierzchołków kości z wagą 1 + modyfikator Armature."""
    ob.parent = arm
    vg = ob.vertex_groups.new(name=kosc)
    vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
    mod = ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm


def znaczniki_att(d, arm):
    """Siatki-znaczniki „<Nazwa>_Att” (importer Roblox zamienia je na Attachment) przypięte do kości."""
    me = bpy.data.meshes.new("_znacznik_att")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=0.1)
    bm.to_mesh(me)
    bm.free()
    lista = list(d["zaczepy"])
    if d["typ"] == "r15":
        lt = next(k for k in d["kosci"] if k["n"] == "LowerTorso")
        lista.append({"n": "Root", "kosc": "LowerTorso", "p": lt["staw"], "r": [0, 0, 0]})
    obs = []
    for z in lista:
        ob = bpy.data.objects.new(nazwa_att(z["n"]), me)
        bpy.context.scene.collection.objects.link(ob)
        ob.parent, ob.parent_type, ob.parent_bone = arm, "BONE", z["kosc"]
        bpy.context.view_layer.update()
        ob.matrix_world = macierz_b(z["p"], z["r"])
        ob.hide_render, ob.display_type = True, "WIRE"
        ob["roblox_attachment"] = z["n"] if z["n"] != "Root" else "RootAttachment"
        obs.append(ob)
    bpy.context.view_layer.update()
    return obs


def kanaly_akcji(akcja):
    try:
        return list(akcja.fcurves)                            # Blender < 5.0
    except AttributeError:
        pass
    wynik = []
    for warstwa in getattr(akcja, "layers", []):              # akcje warstwowe (4.4+ / 5.0)
        for pas in warstwa.strips:
            for cb in getattr(pas, "channelbags", []):
                wynik.extend(cb.fcurves)
    return wynik


def zeruj_poze(arm):
    for pb in arm.pose.bones:
        pb.location, pb.rotation_euler, pb.scale = (0, 0, 0), (0, 0, 0), (1, 1, 1)


def ustaw_akcje(arm, akcja):
    """Przełącz klip. Poza jest zawsze najpierw zerowana: kanały, których nowy klip nie animuje (np. RightHand
    z klipu ataku), inaczej zostałyby w wartości z poprzedniego klipu (tak było w pokazie: miecz Rycerza poziomo)."""
    ad = arm.animation_data_create()
    ad.action = None
    zeruj_poze(arm)
    ad.action = akcja
    if akcja is not None and hasattr(ad, "action_slot") and len(getattr(akcja, "slots", [])) and ad.action_slot is None:
        ad.action_slot = akcja.slots[0]


def klipy(arm, lista):
    """Jedna akcja Blendera na klip. Klucze z wygładzaniem; klip zapętlony dostaje modyfikator Cycles na krzywych
    (gładkie przejście przez szew pętli)."""
    akcje = {}
    if not lista:
        return akcje
    ad = arm.animation_data_create()
    for kl in lista:
        akt = bpy.data.actions.new(kl["n"])
        akt.use_fake_user = True
        ad.action = akt
        zeruj_poze(arm)
        wyg = {}
        for kan in kl["kanaly"]:
            pb = arm.pose.bones[kan["kosc"]]
            sciezka = SCIEZKI[kan["typ"]]
            for f, x, y, z, w in kan["klucze"]:
                setattr(pb, sciezka, (math.radians(x), math.radians(y), math.radians(z)) if kan["typ"] == "obrot" else (x, y, z))
                pb.keyframe_insert(sciezka, frame=float(f), group=kan["kosc"])
                wyg[(kan["kosc"], sciezka, round(float(f), 2))] = w
        for fc in kanaly_akcji(akt):
            kosc, sciezka = fc.data_path.split('"')[1], fc.data_path.rsplit(".", 1)[1]
            for kp in fc.keyframe_points:
                w = wyg.get((kosc, sciezka, round(kp.co.x, 2)), "gladko")
                kp.interpolation = INTERP[w]
                if w == "gladko":
                    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
            if kl["petla"]:
                fc.modifiers.new("CYCLES")
            fc.update()
        akcje[kl["n"]] = akt
    ustaw_akcje(arm, None)
    return akcje


# --------------------------------------------------------------------------- budowa modeli
def zbuduj_postac(d, wyj):
    wszystkie = list(d["czesci"]) + [c for a in d["akcesoria"] for c in a["czesci"]]
    komorki, G = paleta(wszystkie)
    obrazy = obrazy_palety(d["id"], komorki, G, d["materialy"], os.path.join(wyj, d["id"] + "_tekstury"))
    mat = material_modelu(d["id"], obrazy)
    arm = szkielet(d)
    cialo, akc, eksport_akc = [], [], []
    for kosc in [k["n"] for k in d["kosci"]]:
        cz = [c for c in d["czesci"] if c["kosc"] == kosc]
        if cz:
            ob = siatka(kosc + "_Geo", cz, komorki, G, mat)
            przypnij(ob, arm, kosc)
            sk = (d.get("skora") or {}).get(kosc)
            if sk:                                              # siatka skórowana na dwóch kościach (wagi z wysokości)
                gora, y0, y1 = sk
                vg_d, vg_g = ob.vertex_groups[kosc], ob.vertex_groups.new(name=gora)
                for v in ob.data.vertices:
                    w = min(1.0, max(0.0, (v.co.z - y0) / max(1e-6, y1 - y0)))
                    vg_d.add([v.index], 1.0 - w, "REPLACE")
                    vg_g.add([v.index], w, "REPLACE")
            ob["roblox_czesc"] = kosc
            cialo.append(ob)
    for a in d["akcesoria"]:
        if not a["czesci"]:
            continue
        ob = siatka(a["id"] + "_Akc", a["czesci"], komorki, G, mat)
        przypnij(ob, arm, a["kosc"])
        ob["roblox_zaczep"] = a["zaczep"]
        akc.append(ob)
        if a.get("eksport", True):
            eksport_akc.append(ob)
    att = znaczniki_att(d, arm)
    akcje = klipy(arm, d["klipy"])
    return {"arm": arm, "cialo": cialo, "akc": akc, "att": att, "akcje": akcje, "G": G, "kolory": len(komorki),
            "rozmiar_tekstury": G * 8, "eksport": [arm] + cialo + eksport_akc + att, "render": cialo + akc}


def zbuduj_akcesorium(d, wyj):
    komorki, G = paleta(d["czesci"])
    obrazy = obrazy_palety(d["id"], komorki, G, d["materialy"], os.path.join(wyj, d["id"] + "_tekstury"))
    ob = siatka(d["id"], d["czesci"], komorki, G, material_modelu(d["id"], obrazy))
    ob["roblox_zaczep"] = d["zaczep"]
    return {"arm": None, "cialo": [], "akc": [ob], "att": [], "akcje": {}, "G": G, "kolory": len(komorki),
            "rozmiar_tekstury": G * 8, "eksport": [ob], "render": [ob]}


def manekin_skali(d):
    """Szary manekin R15 obok postaci (tylko w kadrze „przód”), żeby było widać skalę."""
    cz = d.get("manekin_skali")
    if not cz:
        return None
    komorki, G = paleta(cz)
    ob = siatka("_ManekinSkali", cz, komorki, G, material_prosty("_Manekin", MANEKIN, 0.7))
    return ob


# --------------------------------------------------------------------------- raport
def trojkaty(ob):
    ob.data.calc_loop_triangles()
    return len(ob.data.loop_triangles)


def skrzynka(obiekty):
    """Skrzynka w układzie DANYCH (szer X, wys Y, głęb Z) z wierzchołków w spoczynku."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for ob in obiekty:
        mw = ob.matrix_world
        for v in ob.data.vertices:
            p = C3T @ (mw @ v.co)
            for i in range(3):
                mn[i], mx[i] = min(mn[i], p[i]), max(mx[i], p[i])
    if mn[0] > mx[0]:
        return None
    return [round(x, 3) for x in mn], [round(x, 3) for x in mx]


def wymiary(sk):
    return [round(sk[1][i] - sk[0][i], 3) for i in range(3)] if sk else [0, 0, 0]


def raport(d, m, wyj):
    L = d["limity"]
    ost = []
    siatki = []
    for ob in m["cialo"] + m["akc"]:
        sk = skrzynka([ob])
        t = trojkaty(ob)
        siatki.append({"nazwa": ob.name, "kosc": ob.vertex_groups[0].name if ob.vertex_groups else None,
                       "trojkaty": t, "wierzcholki": len(ob.data.vertices), "wymiary": wymiary(sk),
                       "min": sk[0] if sk else None, "max": sk[1] if sk else None})
        if t > L["trojkaty_siatka"]:
            ost.append("%s: %d trójkątów > %d (limit siatki Roblox)" % (ob.name, t, L["trojkaty_siatka"]))
        if ob in m["akc"] and t > L["trojkaty_akcesorium"]:
            ost.append("%s: %d trójkątów > %d (limit sztywnego akcesorium)" % (ob.name, t, L["trojkaty_akcesorium"]))
    r = {"id": d["id"], "nazwa": d["nazwa"], "rodzaj": d["rodzaj"], "siatki": siatki,
         "trojkaty_razem": sum(s["trojkaty"] for s in siatki), "tekstury": {"rozmiar_px": m["rozmiar_tekstury"],
                                                                          "kolory_materialy": m["kolory"]}}
    if d["rodzaj"] == "postac":
        sk_cialo = skrzynka(m["cialo"])
        sk_calosc = skrzynka(m["cialo"] + m["akc"])
        r.update({"typ": d["typ"], "skala": d["skala"], "wymiary_ciala": wymiary(sk_cialo),
                  "wymiary_z_akcesoriami": wymiary(sk_calosc), "zakres_z_akcesoriami": sk_calosc,
                  "kosci": [k["n"] for k in d["kosci"]], "zaczepy": [z["n"] for z in d["zaczepy"]],
                  "znaczniki_att": [o.name for o in m["att"]],
                  "klipy": [{"n": k["n"], "dlugosc": k["dlugosc"], "fps": k["fps"],
                             "sekundy": round(k["dlugosc"] / float(k["fps"]), 2), "petla": k["petla"]} for k in d["klipy"]],
                  "akcesoria": [{"id": a["id"], "zaczep": a["zaczep"], "eksport": a.get("eksport", True)}
                                for a in d["akcesoria"]]})
        if d["typ"] == "r15":
            po_nazwie = {ob.vertex_groups[0].name: ob for ob in m["cialo"]}
            grupy = {}
            for g, kosci in L["grupy_ciala"].items():
                obs = [po_nazwie[k] for k in kosci if k in po_nazwie]
                t = sum(trojkaty(o) for o in obs)
                w = wymiary(skrzynka(obs)) if obs else [0, 0, 0]
                grupy[g] = {"trojkaty": t, "limit": L["trojkaty_cialo"][g], "wymiary": w}
                if t > L["trojkaty_cialo"][g]:
                    ost.append("ciało %s: %d trójkątów > %d (budżet części ciała awatara)" % (g, t, L["trojkaty_cialo"][g]))
                rodz = "Arm" if "Arm" in g else "Leg" if "Leg" in g else g
                mn, mx = L["wymiary_ciala"][rodz]
                for i, os_ in enumerate(("szer", "wys", "głęb")):
                    if obs and not (mn[i] - 1e-6 <= w[i] <= mx[i] + 1e-6):
                        ost.append("ciało %s: %s %.2f poza %.2f…%.2f studa (limit części ciała awatara)"
                                   % (g, os_, w[i], mn[i], mx[i]))
            r["grupy_ciala"] = grupy
            t_cialo = sum(trojkaty(o) for o in m["cialo"])
            if t_cialo > L["trojkaty_cialo_razem"]:
                ost.append("ciało razem: %d trójkątów > %d" % (t_cialo, L["trojkaty_cialo_razem"]))
            mn, mx = L["wymiary_ciala"]["Razem"]
            wc = wymiary(sk_cialo)
            for i, os_ in enumerate(("szer", "wys", "głęb")):
                if not (mn[i] - 1e-6 <= wc[i] <= mx[i] + 1e-6):
                    ost.append("ciało razem: %s %.2f poza %.2f…%.2f studa (dotyczy ciała awatara; NPC to nie blokuje)"
                               % (os_, wc[i], mn[i], mx[i]))
    else:
        sk = skrzynka(m["akc"])
        r.update({"zaczep": d["zaczep"], "typ_roblox": d["typ"], "zakres_od_zaczepu": sk,
                  "srodek_skrzynki_od_zaczepu": [round((sk[0][i] + sk[1][i]) / 2, 3) for i in range(3)] if sk else None})
        if d.get("pudlo") and sk:
            for i, os_ in enumerate("XYZ"):
                if sk[0][i] < d["pudlo"][0][i] - 1e-6 or sk[1][i] > d["pudlo"][1][i] + 1e-6:
                    ost.append("%s: oś %s %.2f…%.2f poza pudełkiem typu %s (%.2f…%.2f, skala Classic)"
                               % (d["id"], os_, sk[0][i], sk[1][i], d["typ"], d["pudlo"][0][i], d["pudlo"][1][i]))
    if m["rozmiar_tekstury"] > L["tekstura_bezpieczna"]:
        ost.append("tekstura %d px > %d" % (m["rozmiar_tekstury"], L["tekstura_bezpieczna"]))
    for kl in d.get("klipy", []):                               # Roblox przenosi pozycję i obrót kości, skali raczej nie
        skala_k = sorted({k["kosc"] for k in kl["kanaly"] if k["typ"] == "skala"})
        if skala_k:
            ost.append("klip %s ma kanał skali (%s) — animacja Roblox najpewniej go nie przeniesie"
                       % (kl["n"], ", ".join(skala_k)))
    r["ostrzezenia"] = ost
    with open(os.path.join(wyj, d["id"] + "_raport.json"), "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    log("RAPORT %s (%s): %d siatek, %d trójkątów razem, tekstura palety %d px (%d kolorów)"
        % (d["id"], d["rodzaj"], len(siatki), r["trojkaty_razem"], m["rozmiar_tekstury"], m["kolory"]))
    for s in siatki:
        log("   %-22s %6d tr.  %5.2f × %5.2f × %5.2f st." % (s["nazwa"][:22], s["trojkaty"], *s["wymiary"]))
    if d["rodzaj"] == "postac":
        log("   ciało %.2f × %.2f × %.2f st. (szer × wys × głęb), z akcesoriami %.2f × %.2f × %.2f"
            % (*r["wymiary_ciala"], *r["wymiary_z_akcesoriami"]))
        log("   kości (%d): %s" % (len(r["kosci"]), ", ".join(r["kosci"])))
        log("   klipy: %s" % (", ".join("%s %d kl. %.2f s%s" % (k["n"], k["dlugosc"], k["sekundy"], " pętla" if k["petla"] else "")
                                         for k in r["klipy"]) or "brak"))
        if "grupy_ciala" in r:
            log("   budżety R15: " + ", ".join("%s %d/%d" % (g, v["trojkaty"], v["limit"]) for g, v in r["grupy_ciala"].items()))
    else:
        log("   zaczep %s, typ %s, zakres od zaczepu %s … %s" % (d["zaczep"], d["typ"], r["zakres_od_zaczepu"][0],
                                                               r["zakres_od_zaczepu"][1]))
    for o in ost:
        log("   OSTRZEŻENIE:", o)
    return r


# --------------------------------------------------------------------------- eksport
def eksport_fbx(sciezka, obiekty, anim=False, typy=("ARMATURE", "MESH")):
    """Ustawienia z create.roblox.com/docs/art/blender i /art/characters/export-settings (13.11.2026)."""
    zaznacz(obiekty)
    bpy.ops.export_scene.fbx(
        filepath=sciezka, use_selection=True, object_types=set(typy), use_mesh_modifiers=True,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="Z", axis_up="Y",
        use_custom_props=True, add_leaf_bones=False, bake_anim=anim, bake_anim_use_all_bones=True,
        bake_anim_use_nla_strips=False, bake_anim_use_all_actions=False, bake_anim_force_startend_keying=False,
        bake_anim_simplify_factor=0.0, path_mode="COPY", embed_textures=True)


def eksport_glb(sciezka, obiekty, anim=True):
    zaznacz(obiekty)
    kw = dict(filepath=sciezka, export_format="GLB", use_selection=True, export_yup=True, export_apply=False,
              export_animations=anim, export_animation_mode="ACTIONS", export_skins=True, export_materials="EXPORT")
    try:
        bpy.ops.export_scene.gltf(**kw)
    except TypeError as e:
        log("UWAGA: eksporter glTF odrzucił opcję (%s) — ponawiam z minimalnymi" % e)
        bpy.ops.export_scene.gltf(filepath=sciezka, export_format="GLB", use_selection=True, export_yup=True)


def eksportuj(d, m, wyj, z):
    oczek = []
    sc = bpy.context.scene
    siatki = [o for o in m["eksport"] if o.type == "MESH"]
    tri = sum(trojkaty(o) for o in siatki)
    kosci = len(m["arm"].data.bones) if m["arm"] else 0
    sk = skrzynka([o for o in siatki if not o.name.endswith("_Att")])
    wys = round(sk[1][1] - sk[0][1], 3) if sk else 0
    if m["arm"]:
        ustaw_akcje(m["arm"], None)
    if z.get("fbx"):
        p = os.path.join(wyj, d["id"] + ".fbx")
        eksport_fbx(p, m["eksport"], anim=False, typy=("ARMATURE", "MESH") if m["arm"] else ("MESH",))
        oczek.append({"plik": p, "siatki": len(siatki), "kosci": kosci, "trojkaty": tri, "wysokosc": wys, "klipy": []})
        log("EKSPORT", p)
        for kl in d.get("klipy", []):
            ustaw_akcje(m["arm"], m["akcje"][kl["n"]])
            sc.frame_start, sc.frame_end = 0, int(kl["dlugosc"])
            sc.render.fps = int(kl["fps"])
            p = os.path.join(wyj, "%s__%s.fbx" % (d["id"], kl["n"]))
            eksport_fbx(p, m["eksport"], anim=True)
            oczek.append({"plik": p, "siatki": len(siatki), "kosci": kosci, "trojkaty": tri, "wysokosc": wys,
                          "klipy": [[kl["n"], int(kl["dlugosc"])]], "fps": int(kl["fps"])})
            log("EKSPORT", p)
        if m["arm"]:
            ustaw_akcje(m["arm"], None)
    if z.get("glb"):
        p = os.path.join(wyj, d["id"] + ".glb")
        eksport_glb(p, m["eksport"], anim=bool(m["akcje"]))
        oczek.append({"plik": p, "siatki": len(siatki), "kosci": kosci, "trojkaty": tri, "wysokosc": wys,
                      "klipy": [[k["n"], int(k["dlugosc"])] for k in d.get("klipy", [])],
                      "fps": int(d["klipy"][0]["fps"]) if d.get("klipy") else 30})
        log("EKSPORT", p)
    return oczek


def zapisz_blend(d, wyj):
    t = bpy.data.texts.new("README_POSTAC")
    t.write("Model %s (%s) z biblioteki swiat/postacie/biblioteka (blender_postac.py).\n"
            "1 jednostka = 1 stud. Postać patrzy w -Y (widok Front), lewa strona postaci = +X.\n"
            "Każda siatka <Kosc>_Geo jest sztywno przypięta do jednej kości (grupa wierzchołków, waga 1).\n"
            "Klipy = akcje (fake user); obrót kości: Euler ZXY = kolejność Roblox Ry*Rx*Rz.\n"
            "Siatki <Nazwa>_Att to znaczniki punktów zaczepienia dla importera Roblox.\n"
            "Kolory: tekstury-palety (kolor/metal/szorstkosc/emisja) + atrybut Col. Źródłem prawdy jest moduł .py,\n"
            "nie ten plik — zmiany rób w kodzie i generuj od nowa.\n" % (d["id"], d["nazwa"]))
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        log("UWAGA: nie spakowano tekstur do .blend (%s)" % e)
    for img in bpy.data.images:                                 # bez ścieżek z dysku autora: względne do .blend
        if img.filepath and img.packed_file:
            try:
                rel = os.path.relpath(bpy.path.abspath(img.filepath), wyj).replace(os.sep, "/")
            except ValueError:
                rel = os.path.basename(img.filepath)
            img.filepath_raw = "//" + rel
    p = os.path.join(wyj, d["id"] + ".blend")
    bpy.ops.wm.save_as_mainfile(filepath=p, copy=True, compress=True)
    log("EKSPORT", p)


# --------------------------------------------------------------------------- rendery
def przygotuj_render(sc, probki):
    sc.render.engine = "BLENDER_EEVEE"
    ee = sc.eevee
    for atr, wart in (("taa_render_samples", int(probki)), ("use_shadows", True), ("use_gtao", True),
                      ("use_raytracing", False), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
        if hasattr(ee, atr):
            try:
                setattr(ee, atr, wart)
            except Exception:
                pass
    sc.view_settings.view_transform = "Standard"
    try:
        sc.view_settings.look = "None"
    except Exception:
        pass
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    swiat = bpy.data.worlds.new("Swiat")
    if swiat.node_tree is None:
        swiat.use_nodes = True
    nt = swiat.node_tree
    tlo = nt.nodes.get("Background")
    # pionowy gradient (jasna góra, ciemny dół): metal ma co odbijać, tło nie jest płaskie
    tc, sep = nt.nodes.new("ShaderNodeTexCoord"), nt.nodes.new("ShaderNodeSeparateXYZ")
    mr, ramp = nt.nodes.new("ShaderNodeMapRange"), nt.nodes.new("ShaderNodeValToRGB")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -1.0, 1.0
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.38, (*lin(TLO_DOL), 1.0)
    el[1].position, el[1].color = 0.78, (*lin(TLO_GORA), 1.0)
    srodek = el.new(0.52)
    srodek.color = (*lin(TLO), 1.0)
    nt.links.new(ramp.outputs["Color"], tlo.inputs["Color"])
    tlo.inputs[1].default_value = 0.75
    sc.world = swiat
    for nazwa, kier, energia, kolor in (("Klucz", (0.85, 1.35, 1.1), 3.0, (1.0, 0.95, 0.88)),
                                        ("Wypelnienie", (-1.2, 0.45, 0.8), 0.9, (0.80, 0.86, 1.0)),
                                        ("Kontra", (-0.5, 0.9, -1.3), 2.4, (1.0, 0.9, 1.0))):
        sw = bpy.data.lights.new(nazwa, "SUN")
        sw.energy, sw.color, sw.angle = energia, kolor, math.radians(10)
        ob = bpy.data.objects.new(nazwa, sw)
        sc.collection.objects.link(ob)
        ob.rotation_euler = (-(C3 @ Vector(kier))).to_track_quat("-Z", "Y").to_euler()


def podloze(promien):
    me = bpy.data.meshes.new("_podloze")
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=promien, segments=64)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material_prosty("_Podloze", PODLOZE, 0.9))
    ob = bpy.data.objects.new("_Podloze", me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def dodaj_obrys(obiekty, grub):
    """Komiksowy obrys = efekt RENDERU (odwrócona otoczka: Solidify + materiał z backface culling). Nie trafia do
    eksportów (te powstają wcześniej)."""
    m = nowy_material("_Obrys")
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    wyj = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin("120E18"), 1.0)
    nt.links.new(em.outputs["Emission"], wyj.inputs["Surface"])
    m.use_backface_culling = True
    m.diffuse_color = (0.02, 0.02, 0.03, 1.0)
    mody = []
    for ob in obiekty:
        ob.data.materials.append(m)
        mod = ob.modifiers.new("_Obrys", "SOLIDIFY")
        mod.thickness, mod.offset, mod.use_even_offset = grub, 1.0, True
        mod.use_flip_normals, mod.use_rim = True, False
        mod.material_offset = len(ob.data.materials) - 1
        mody.append(mod)
    return mody


def punkty(obiekty):
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for ob in obiekty:
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        mw = ev.matrix_world.copy()
        pts.extend(mw @ v.co for v in me.vertices)
        ev.to_mesh_clear()
    return pts


def kamera(sc, kierunek, pts, orto, margines=1.1, ogniskowa=50.0):
    """Kamera z kierunku `kierunek` (dane: od modelu ku kamerze), kadr dopasowany do punktów (kwadratowy obraz)."""
    d = (C3 @ Vector(kierunek)).normalized()
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
    cd.sensor_fit = "AUTO"
    if orto:
        cd.type = "ORTHO"
        cd.ortho_scale = max(max(xs) - min(xs), max(ys) - min(ys)) * margines
        odl = (max(zs) - min(zs)) + 40.0
    else:
        cd.type, cd.lens = "PERSP", ogniskowa
        tg = math.tan(math.atan(cd.sensor_width / 2.0 / ogniskowa))
        odl = max((p - sr).dot(d) + max(abs((p - sr).dot(prawo)), abs((p - sr).dot(gora))) * margines / tg for p in pts)
    cd.clip_start, cd.clip_end = 0.05, odl + 400.0
    cam.location = sr + d * odl
    cam.rotation_euler = przod.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam


def renderuj(sc, sciezka, rozmiar, przezroczyste=False, fmt="JPEG"):
    sc.render.resolution_x = sc.render.resolution_y = int(rozmiar)
    sc.render.film_transparent = przezroczyste
    sc.render.image_settings.file_format = fmt
    sc.render.image_settings.color_mode = "RGBA" if fmt == "PNG" else "RGB"
    sc.render.filepath = sciezka
    bpy.ops.render.render(write_still=True)


def piksele(sciezka):
    img = bpy.data.images.load(sciezka, check_existing=False)
    w, h = img.size
    a = np.empty(w * h * 4, np.float32)
    img.pixels.foreach_get(a)
    bpy.data.images.remove(img)
    return a.reshape(h, w, 4)


def zapisz_piksele(arr, sciezka):
    h, w = arr.shape[:2]
    img = bpy.data.images.new("_kompozycja", w, h, alpha=False)
    img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).ravel())
    img.filepath_raw = sciezka
    img.file_format = "JPEG"
    try:
        img.save(quality=90)
    except TypeError:
        img.save()
    bpy.data.images.remove(img)


def zmniejsz(arr, k):
    h, w = arr.shape[0] // k * k, arr.shape[1] // k * k
    return arr[:h, :w].reshape(h // k, k, w // k, k, 4).mean(axis=(1, 3))


def poza_renderu(d, m):
    """Ustaw pozę do renderów (klip + klatka z modelu albo spoczynek)."""
    sc = bpy.context.scene
    pr = d.get("poza_renderu")
    if m["arm"] and pr and pr[0] in m["akcje"]:
        ustaw_akcje(m["arm"], m["akcje"][pr[0]])
        f = float(pr[1])
        sc.frame_set(int(f), subframe=f - int(f))
    elif m["arm"]:
        ustaw_akcje(m["arm"], None)
        sc.frame_set(0)
    bpy.context.view_layer.update()


def rendery(d, m, wyj, z, a, ffmpeg):
    sc = bpy.context.scene
    przygotuj_render(sc, a.probki)
    model = m["render"]
    sk = skrzynka(model)
    rozmiar_modelu = max(wymiary(sk)) if sk else 5.0
    grub = max(0.02, 0.0085 * rozmiar_modelu)
    obrys = [] if a.bez_obrysu and not z.get("ikona") else dodaj_obrys(model, grub)
    ziemia = podloze(max(8.0, rozmiar_modelu * 3)) if d["rodzaj"] == "postac" else None
    man = manekin_skali(d) if d["rodzaj"] == "postac" else None
    if man is not None:                                         # manekin skali po lewej stronie obrazu (−X danych)
        skm = skrzynka([man])
        dx = (sk[0][0] - 0.9) - skm[1][0]
        man.location = do_blendera((dx, 0.0, (sk[0][2] + sk[1][2]) / 2 - (skm[0][2] + skm[1][2]) / 2))
        man.hide_render = True
    pliki = []

    def obrys_wl(wl):
        for mod in obrys:
            mod.show_render = mod.show_viewport = wl

    if z.get("render"):
        poza_renderu(d, m)
        szer = int(a.szer)
        widoki = (("bohater", BOHATER, False, szer), ("przod", (0.0, 0.0, 1.0), True, szer // 2),
                  ("bok", (-1.0, 0.0, 0.0), True, szer // 2), ("tyl", (0.0, 0.0, -1.0), True, szer // 2))
        kadry = {}
        for nazwa, kier, orto, roz in widoki:
            obrys_wl(nazwa == "bohater" and not a.bez_obrysu)
            obiekty = list(model)
            if man is not None:
                man.hide_render = nazwa != "przod"
                if nazwa == "przod":
                    obiekty.append(man)
            if ziemia is not None:
                ziemia.hide_render = False
            kamera(sc, kier, punkty(obiekty), orto, margines=1.12, ogniskowa=OGNISKOWA)
            p = os.path.join(wyj, "%s_%s.jpg" % (d["id"], nazwa))
            renderuj(sc, p, roz)
            kadry[nazwa] = p
        if man is not None:
            man.hide_render = True
        h = piksele(kadry["bohater"])
        pol = szer // 2
        if h.shape[0] != pol:
            h = zmniejsz(h, max(1, h.shape[0] // pol))[:pol, :pol]
        plansza = np.ones((2 * pol, 2 * pol, 4), np.float32) * 0.12
        plansza[pol:, :pol] = h[:pol, :pol]
        plansza[pol:, pol:] = piksele(kadry["przod"])[:pol, :pol]
        plansza[:pol, :pol] = piksele(kadry["bok"])[:pol, :pol]
        plansza[:pol, pol:] = piksele(kadry["tyl"])[:pol, :pol]
        plansza[pol - 1:pol + 1, :, :3] = 0.12
        plansza[:, pol - 1:pol + 1, :3] = 0.12
        p = os.path.join(wyj, d["id"] + "_plansza.jpg")
        zapisz_piksele(plansza, p)
        for nazwa in ("przod", "bok", "tyl"):
            os.remove(kadry[nazwa])
        pliki += [p, kadry["bohater"]]
        log("RENDER", p)

    if z.get("ikona"):
        poza_renderu(d, m)
        obrys_wl(True)
        if ziemia is not None:
            ziemia.hide_render = True
        stare = {}
        io = d.get("ikona_obrot") or [0, 0, 0]
        if d["rodzaj"] == "akcesorium" and any(abs(x) > 1e-6 for x in io):
            for ob in model:                                    # ikona_obrot: np. miecz po skosie
                stare[ob] = ob.matrix_world.copy()
                ob.matrix_world = (C3 @ obrot_dane(io) @ C3T).to_4x4() @ ob.matrix_world
            bpy.context.view_layer.update()
        pts = punkty(model)
        if d["rodzaj"] == "postac" and d.get("typ") == "r15":
            # postać R15: popiersie (głowa + górne 40% tułowia), żeby w 64 px było widać twarz
            st = {k["n"]: k["staw"] for k in d["kosci"]}
            szyja = st["Head"][1]
            ut = szyja - st["UpperTorso"][1]
            prog = szyja - 0.4 * ut
            pts = [p for p in pts if p.z >= prog] or pts
        cam = kamera(sc, (0.65, 0.45, 1.0), pts, True, margines=1.12)
        for mod in obrys:                                       # obrys ikony: ok. 3 px przy 512 px
            mod.thickness = 3.0 / 512.0 * cam.data.ortho_scale
        p = os.path.join(wyj, d["id"] + "_ikona.png")
        renderuj(sc, p, 512, przezroczyste=True, fmt="PNG")
        for mod in obrys:
            mod.thickness = grub
        for ob, mw in stare.items():
            ob.matrix_world = mw
        if ziemia is not None:
            ziemia.hide_render = False
        pliki.append(p)
        log("RENDER", p)

    for rodzaj in ("film", "klatki"):
        nazwa_klipu = z.get(rodzaj)
        if not nazwa_klipu:
            continue
        kl = next((k for k in d.get("klipy", []) if k["n"] == nazwa_klipu), None)
        if kl is None or not m["arm"]:
            log("UWAGA: %s nie ma klipu %r — pomijam %s" % (d["id"], nazwa_klipu, rodzaj))
            continue
        obrys_wl(not a.bez_obrysu)
        if ziemia is not None:
            ziemia.hide_render = False
        # jeden kadr dla wszystkich klipów modelu (obwiednia wszystkich klipów, stała ogniskowa) — filmy i arkusze
        # różnych klipów mają tę samą skalę
        pts = []
        for k2 in d.get("klipy", []):
            ustaw_akcje(m["arm"], m["akcje"][k2["n"]])
            n2 = int(k2["dlugosc"])
            for i in range(9):
                f = n2 * i / 8.0
                sc.frame_set(int(f), subframe=f - int(f))
                pts += punkty(model)
        ustaw_akcje(m["arm"], m["akcje"][kl["n"]])
        kamera(sc, BOHATER, pts, False, margines=1.1, ogniskowa=OGNISKOWA)
        if rodzaj == "film":
            pliki += film(sc, d, kl, wyj, ffmpeg)
        else:
            pliki += arkusz_klatek(sc, d, kl, wyj)
    return pliki


def film(sc, d, kl, wyj, ffmpeg, rozmiar=480):
    n, fps = int(kl["dlugosc"]), int(kl["fps"])
    sc.render.fps = fps
    tmp = os.path.join(wyj, "_klatki_%s_%s" % (d["id"], kl["n"]))
    os.makedirs(tmp, exist_ok=True)
    klatki = list(range(n * 3)) if kl["petla"] else list(range(n + 1))
    for i, f in enumerate(klatki):
        sc.frame_set(f)
        renderuj(sc, os.path.join(tmp, "%04d.png" % i), rozmiar, fmt="PNG")
    if not kl["petla"]:                                        # klip jednorazowy: przytrzymaj ostatnią klatkę 0,5 s
        for j in range(fps // 2):
            shutil.copy(os.path.join(tmp, "%04d.png" % (len(klatki) - 1)), os.path.join(tmp, "%04d.png" % (len(klatki) + j)))
    mp4 = os.path.join(wyj, "%s_%s.mp4" % (d["id"], kl["n"]))
    if ffmpeg:
        r = subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(tmp, "%04d.png"),
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23", "-movflags", "+faststart", mp4],
                           capture_output=True)
        if r.returncode != 0:
            log("UWAGA: ffmpeg:", r.stderr.decode("utf-8", "replace")[-400:])
    else:                                                       # bez ffmpeg: wbudowany zapis wideo Blendera
        im = sc.render.image_settings
        try:
            im.media_type = "VIDEO"
        except Exception:
            pass
        im.file_format = "FFMPEG"
        sc.render.ffmpeg.format, sc.render.ffmpeg.codec = "MPEG4", "H264"
        sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
        sc.frame_start, sc.frame_end = 0, len(klatki) - 1
        sc.render.filepath = mp4
        bpy.ops.render.render(animation=True)
        try:
            im.media_type = "IMAGE"
        except Exception:
            pass
    shutil.rmtree(tmp, ignore_errors=True)
    log("FILM", mp4, "(%d klatek, %d kl./s)" % (len(klatki), fps))
    return [mp4]


def arkusz_klatek(sc, d, kl, wyj, kolumny=4, wiersze=2, rozmiar=240):
    n = int(kl["dlugosc"])
    ile = kolumny * wiersze
    klatki = [n * i / ile for i in range(ile)] if kl["petla"] else [n * i / (ile - 1) for i in range(ile)]
    tmp = os.path.join(wyj, "_tmp_klatka.png")
    ark = np.ones((wiersze * rozmiar, kolumny * rozmiar, 4), np.float32) * 0.12
    for i, f in enumerate(klatki):
        sc.frame_set(int(f), subframe=f - int(f))
        renderuj(sc, tmp, rozmiar, fmt="PNG")
        px = piksele(tmp)
        r, c = i // kolumny, i % kolumny
        y0 = (wiersze - 1 - r) * rozmiar
        ark[y0:y0 + rozmiar, c * rozmiar:(c + 1) * rozmiar] = px[:rozmiar, :rozmiar]
    os.remove(tmp)
    ark[:, ::rozmiar, :3] = 0.12
    ark[::rozmiar, :, :3] = 0.12
    p = os.path.join(wyj, "%s_%s_klatki.jpg" % (d["id"], kl["n"]))
    zapisz_piksele(ark, p)
    log("KLATKI", p, "(klatki %s)" % ", ".join("%g" % round(f, 1) for f in klatki))
    return [p]


# --------------------------------------------------------------------------- kontrola eksportów
def kontrola(sciezka):
    """Wczytuje każdy wyeksportowany plik do pustej sceny i porównuje siatki, kości, klatki, trójkąty i wzrost."""
    with open(sciezka, encoding="utf-8") as f:
        oczek = json.load(f)
    bledy = 0
    for e in oczek["pliki"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        sc.render.fps = int(e.get("fps", 30))
        if e["plik"].lower().endswith(".fbx"):
            bpy.ops.import_scene.fbx(filepath=e["plik"])
        else:
            bpy.ops.import_scene.gltf(filepath=e["plik"])
        # importer glTF dokłada pomocniczy kształt kości (Icosphere w kolekcji glTF_not_exported) — to nie nasz model
        siatki = [o for o in sc.objects if o.type == "MESH"
                  and not any(c.name.startswith("glTF_not_exported") for c in o.users_collection)]
        szk = [o for o in sc.objects if o.type == "ARMATURE"]
        kosci = sum(len(a.data.bones) for a in szk)
        tri = 0
        mn, mx = 1e9, -1e9
        for o in siatki:
            o.data.calc_loop_triangles()
            tri += len(o.data.loop_triangles)
            if o.name.split(".")[0].endswith("_Att"):
                continue
            for v in o.data.vertices:
                z = (o.matrix_world @ v.co).z
                mn, mx = min(mn, z), max(mx, z)
        wys = round(mx - mn, 3) if mx > mn else 0
        akcje = [(a.name, int(round(a.frame_range[0])), int(round(a.frame_range[1]))) for a in bpy.data.actions]
        dl_ocz = sorted(k[1] for k in e["klipy"])
        dl_jest = sorted(b - a for _, a, b in akcje)
        problemy = []
        if len(siatki) != e["siatki"]:
            problemy.append("siatki %d ≠ %d" % (len(siatki), e["siatki"]))
        if kosci != e["kosci"]:
            problemy.append("kości %d ≠ %d" % (kosci, e["kosci"]))
        if tri != e["trojkaty"]:
            problemy.append("trójkąty %d ≠ %d" % (tri, e["trojkaty"]))
        if abs(wys - e["wysokosc"]) > 0.02:
            problemy.append("wzrost %.3f ≠ %.3f (skala!)" % (wys, e["wysokosc"]))
        if dl_ocz and dl_jest != dl_ocz:
            problemy.append("długości klipów %s ≠ %s" % (dl_jest, dl_ocz))
        if not dl_ocz and akcje:
            problemy.append("niespodziewane akcje %s" % akcje)
        bledy += bool(problemy)
        log("KONTROLA %s: siatki %d, kości %d, trójkąty %d, wzrost %.2f st., akcje %s -> %s"
            % (os.path.basename(e["plik"]), len(siatki), kosci, tri, wys,
               ", ".join("%s %d-%d" % a for a in akcje) or "brak", "; ".join(problemy) or "ZGODNE"))
    return bledy


# --------------------------------------------------------------------------- główna pętla
def zadania_modelu(d, a):
    z = {"render": a.render, "ikona": a.ikona, "film": a.film, "klatki": a.klatki, "fbx": a.fbx, "glb": a.glb,
         "blend": a.zapisz_blend}
    z.update(d.get("zadania") or {})
    return z


def main():
    a = argumenty()
    if a.kontrola:
        bledy = kontrola(a.kontrola)
        if bledy:
            raise SystemExit("KONTROLA: %d plików niezgodnych" % bledy)
        return
    with open(a.json, encoding="utf-8") as f:
        pak = json.load(f)
    wyj = os.path.abspath(a.wyj)
    os.makedirs(wyj, exist_ok=True)
    ffmpeg = a.ffmpeg or shutil.which("ffmpeg")
    oczekiwane = []
    for d in pak["modele"]:
        t0 = time.time()
        z = zadania_modelu(d, a)
        fps = d["klipy"][0]["fps"] if d.get("klipy") else 30
        nowa_scena(fps)
        m = zbuduj_postac(d, wyj) if d["rodzaj"] == "postac" else zbuduj_akcesorium(d, wyj)
        raport(d, m, wyj)
        if z.get("blend"):
            zapisz_blend(d, wyj)
        oczekiwane += eksportuj(d, m, wyj, z)
        if any(z.get(k) for k in ("render", "ikona", "film", "klatki")):
            rendery(d, m, wyj, z, a, ffmpeg)
        log("GOTOWE %s w %.1f s" % (d["id"], time.time() - t0))
    if oczekiwane:
        p = os.path.join(wyj, "eksport_oczekiwane.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"pliki": oczekiwane}, f, ensure_ascii=False, indent=1)
        log("OCZEKIWANE", p)


if __name__ == "__main__":
    main()
