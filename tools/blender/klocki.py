# -*- coding: utf-8 -*-
"""Klocki Roblox <-> Blender: ta sama scena z prymitywów w Blenderze, w Roblox Studio i w podglądzie 3D panelu.

Format wejścia/wyjścia: `czesci.json` (panel/README.md), geometria kształtów: panel/luau/KSZTALTY.md.
Układ Roblox: Y w górę, przód −Z. Blender: Z w górę. Przeliczenie: (x, y, z)_roblox -> (x, −z, y)_blender.
Każda część to obiekt ze wspólną siatką jednostkową (5 siatek na całą scenę) i skalą = rozmiar, więc scena jest lekka,
a przesunięcie/obrót/skalowanie klocka w Blenderze wraca do Robloxa przez --do-json.

    blender -b --factory-startup --python-exit-code 1 --python tools/blender/klocki.py -- \
        --z-json <czesci.json> [--zapisz <plik.blend>] [--render <folder>] [--szer 1600] [--probki 48]
    blender -b --factory-startup <plik.blend> --python-exit-code 1 --python tools/blender/klocki.py -- --do-json <czesci.json>

Kadry renderu: domyślnie ujęcia dema „Leśna baza”; `--auto` = kadry wyliczone z rozmiaru sceny (przód 3/4, tył 3/4, bok,
oczy gracza, rzut z góry); `--ujecia <plik.json>` = własna lista [[nazwa, [x,y,z] kamery, [x,y,z] celu, ogniskowa mm,
skala rzutu prostokątnego albo null], …] w układzie Roblox; `--tylko a,b` = tylko ujęcia zawierające te słowa.
`--swiatlo studio` = płaskie, szare światło jak w domyślnym miejscu Roblox (uczciwy test kontrastu); domyślnie słońce.

Ścieżki ZAWSZE bezwzględne (katalog roboczy Blendera to C:\\). Render uruchamiaj pod blokadą GPU (gpu_lock.py).
Własności obiektu: rbx_ksztalt (0 blok, 1 kula, 2 walec, 3 klin, 4 klin narożny), rbx_kolor, rbx_material, rbx_alfa,
rbx_grupa. Obiekty bez rbx_ksztalt (np. importowane siatki) są przy eksporcie pomijane — idą osobną drogą (FBX/GLB).
"""
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(k, d=None):
    return A[A.index(k) + 1] if k in A else d


C = Matrix(((1, 0, 0), (0, 0, -1), (0, 1, 0)))                 # roblox -> blender
CT = C.transposed()
SZORSTKOSC = {"SmoothPlastic": 0.55, "Plastic": 0.6, "Wood": 0.8, "WoodPlanks": 0.8, "Slate": 0.9, "Cobblestone": 0.9,
              "Grass": 0.95, "Ground": 0.95, "Sand": 0.95, "Fabric": 0.9, "Metal": 0.35, "Glass": 0.08, "Neon": 0.5}
NAZWY_KSZTALTOW = {0: "blok", 1: "kula", 2: "walec", 3: "klin", 4: "naroznik"}


def b(v):
    """Wierzchołek z lokalnego układu Roblox do lokalnego układu Blendera."""
    return (v[0], -v[2], v[1])


def _siatka(nazwa, wierzcholki, sciany, gladkie=None):
    me = bpy.data.meshes.new(nazwa)
    me.from_pydata([b(v) for v in wierzcholki], [], sciany)
    me.update()
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    if gladkie is not None:
        for i, p in enumerate(me.polygons):
            p.use_smooth = gladkie(i)
    me.materials.append(None)                                  # jedno gniazdo; materiał podpinany na obiekcie
    return me


def siatki_jednostkowe():
    h = 0.5
    blok = _siatka("RBX_blok", [(-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h), (-h, h, -h), (h, h, -h), (h, h, h), (-h, h, h)],
                   [(0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)])
    # klin: podstawa (±h, −h, ±h), górna krawędź (±h, +h, +h) — wysoka ściana po +Z
    klin = _siatka("RBX_klin", [(-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h), (-h, h, h), (h, h, h)],
                   [(0, 1, 2, 3), (3, 2, 5, 4), (0, 4, 5, 1), (0, 3, 4), (1, 5, 2)])
    # klin narożny: A B C D + wierzchołek P(+h, +h, −h)
    nar = _siatka("RBX_naroznik", [(-h, -h, -h), (h, -h, -h), (h, -h, h), (-h, -h, h), (h, h, -h)],
                  [(0, 1, 2, 3), (0, 4, 1), (1, 4, 2), (0, 3, 4), (4, 3, 2)])
    n = 24                                                     # walec: oś X; boki gładkie, denka osobne
    w, s = [], []
    for i in range(n):
        k = math.tau * i / n
        w.append((-h, math.cos(k) * h, math.sin(k) * h))
        w.append((h, math.cos(k) * h, math.sin(k) * h))
    for i in range(n):
        j = (i + 1) % n
        s.append((2 * i, 2 * j, 2 * j + 1, 2 * i + 1))
    baza = len(w)
    for i in range(n):
        k = math.tau * i / n
        w.append((-h, math.cos(k) * h, math.sin(k) * h))
    for i in range(n):
        k = math.tau * i / n
        w.append((h, math.cos(k) * h, math.sin(k) * h))
    s.append(tuple(baza + i for i in range(n)))
    s.append(tuple(baza + n + i for i in range(n)))
    walec = _siatka("RBX_walec", w, s, gladkie=lambda i: i < n)
    w, s = [(0, h, 0)], []                                     # kula UV
    pier, seg = 9, 18
    for r in range(1, pier):
        fi = math.pi * r / pier
        for q in range(seg):
            k = math.tau * q / seg
            w.append((math.sin(fi) * math.cos(k) * h, math.cos(fi) * h, math.sin(fi) * math.sin(k) * h))
    w.append((0, -h, 0))
    for q in range(seg):
        s.append((0, 1 + q, 1 + (q + 1) % seg))
    for r in range(pier - 2):
        for q in range(seg):
            a0 = 1 + r * seg + q
            a1 = 1 + r * seg + (q + 1) % seg
            s.append((a0, a0 + seg, a1 + seg, a1))
    ost = len(w) - 1
    for q in range(seg):
        s.append((ost, 1 + (pier - 2) * seg + (q + 1) % seg, 1 + (pier - 2) * seg + q))
    kula = _siatka("RBX_kula", w, s, gladkie=lambda i: True)
    return {0: blok, 1: kula, 2: walec, 3: klin, 4: nar}


def srgb_lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


_materialy = {}


def material(kolor, mat, alfa):
    klucz = (kolor, mat, alfa)
    if klucz in _materialy:
        return _materialy[klucz]
    m = bpy.data.materials.new("RBX_%s_%s%s" % (kolor, mat, ("_a%02d" % int(alfa * 100)) if alfa else ""))
    m.use_nodes = True
    rgb = [srgb_lin(int(kolor[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
    bsdf.inputs["Roughness"].default_value = SZORSTKOSC.get(mat, 0.6)
    if mat == "Metal":
        bsdf.inputs["Metallic"].default_value = 0.6
    if mat == "Neon":
        for nazwa in ("Emission Color", "Emission"):
            if nazwa in bsdf.inputs:
                bsdf.inputs[nazwa].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
                break
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = 3.0
    if alfa > 0:
        bsdf.inputs["Alpha"].default_value = 1.0 - alfa
        for atr, wart in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
            if hasattr(m, atr):
                try:
                    setattr(m, atr, wart)
                except Exception:
                    pass
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0 - alfa)
    _materialy[klucz] = m
    return m


def obrot_rbx(rx, ry, rz):
    """Macierz obrotu Roblox: CFrame.fromOrientation(rx, ry, rz) = Ry · Rx · Rz."""
    return Matrix.Rotation(ry, 3, "Y") @ Matrix.Rotation(rx, 3, "X") @ Matrix.Rotation(rz, 3, "Z")


def kolekcja(sciezka, rodzic):
    nazwa = sciezka.split("/")[-1]
    kol = bpy.data.collections.get(nazwa)
    if kol is None:
        kol = bpy.data.collections.new(nazwa)
        rodzic.children.link(kol)
    return kol


def z_json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        d = json.load(f)
    siatki = siatki_jednostkowe()
    for o in list(bpy.data.objects):                           # pusta scena fabryczna: usuń sześcian, lampę, kamerę
        bpy.data.objects.remove(o, do_unlink=True)
    korzen_nazwa = (d["grupy"][0].split("/")[1] if d["grupy"] and "/" in d["grupy"][0] else "Scena")
    korzen = bpy.data.collections.new(korzen_nazwa)
    bpy.context.scene.collection.children.link(korzen)
    kolekcje = [kolekcja(g, korzen) for g in d["grupy"]]
    for c in d["czesci"]:
        ks, gi, x, y, z, rx, ry, rz, sx, sy, sz, kolor, mi, alfa, nazwa = c[:15]   # 16. pole (cechy) dotyczy tylko Studio
        mat = d["materialy"][mi]
        ob = bpy.data.objects.new(nazwa, siatki.get(ks, siatki[0]))
        if ks == 1:
            sred = min(sx, sy, sz)
            skala = (sred, sred, sred)
        elif ks == 2:
            sred = min(sy, sz)
            skala = (sx, sred, sred)
        else:
            skala = (sx, sz, sy)                               # lokalne osie Blendera: x=X, y=−Z, z=Y Robloxa
        R = C @ obrot_rbx(rx, ry, rz) @ CT
        ob.matrix_world = Matrix.Translation(C @ Vector((x, y, z))) @ R.to_4x4() @ Matrix.Diagonal((skala[0], skala[1], skala[2], 1.0))
        ob["rbx_ksztalt"], ob["rbx_kolor"], ob["rbx_material"], ob["rbx_alfa"], ob["rbx_grupa"] = ks, kolor, mat, alfa, d["grupy"][gi]
        kolekcje[gi].objects.link(ob)
        ob.material_slots[0].link = "OBJECT"                   # siatka wspólna, materiał na obiekcie
        ob.material_slots[0].material = material(kolor, mat, alfa)
        ob.color = ob.material_slots[0].material.diffuse_color
    txt = bpy.data.texts.new("CLAUDE_README")
    txt.write("Scena z klocków Roblox (tools/blender/klocki.py).\n"
              "Każdy obiekt = jedna część Roblox: rbx_ksztalt 0 blok / 1 kula / 2 walec (oś X) / 3 klin / 4 klin narożny.\n"
              "Skala obiektu = rozmiar części w studs (1 jednostka = 1 stud). Kolekcje = grupy (Modele) w Studio.\n"
              "Po zmianach: blender -b --factory-startup <ten plik> --python tools/blender/klocki.py -- --do-json <czesci.json>\n"
              "Kolor zmieniaj we własności rbx_kolor (RRGGBB), nie w materiale.\n")
    print("KLOCKI | zbudowano %d części w %d kolekcjach" % (len(d["czesci"]), len(kolekcje)), flush=True)


def do_json(sciezka):
    grupy, materialy, czesci = [], [], []

    def idx(lista, v):
        if v not in lista:
            lista.append(v)
        return lista.index(v)

    bpy.context.view_layer.update()
    for ob in bpy.context.scene.objects:
        if "rbx_ksztalt" not in ob:
            continue
        ks = int(ob["rbx_ksztalt"])
        loc, rot, skala = ob.matrix_world.decompose()
        p = CT @ loc
        R = CT @ rot.to_matrix() @ C
        rx = math.asin(max(-1.0, min(1.0, -R[1][2])))
        ry = math.atan2(R[0][2], R[2][2])
        rz = math.atan2(R[1][0], R[1][1])
        if ks == 1:
            sred = min(abs(skala.x), abs(skala.y), abs(skala.z))
            sx = sy = sz = sred
        elif ks == 2:
            sx = abs(skala.x)
            sy = sz = min(abs(skala.y), abs(skala.z))
        else:
            sx, sy, sz = abs(skala.x), abs(skala.z), abs(skala.y)
        nazwa = ob.name.rsplit(".", 1)[0] if ob.name[-4:-3] == "." and ob.name[-3:].isdigit() else ob.name
        czesci.append([ks, idx(grupy, ob.get("rbx_grupa") or "Workspace/Scena"), round(p.x, 3), round(p.y, 3), round(p.z, 3),
                       round(rx, 4), round(ry, 4), round(rz, 4), round(sx, 3), round(sy, 3), round(sz, 3),
                       str(ob.get("rbx_kolor") or "A3A2A5"), idx(materialy, str(ob.get("rbx_material") or "SmoothPlastic")),
                       round(float(ob.get("rbx_alfa") or 0.0), 2), nazwa[:40]])
    with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"wersja": 1, "grupy": grupy, "materialy": materialy, "czesci": czesci}, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print("KLOCKI | wyeksportowano %d części -> %s" % (len(czesci), sciezka), flush=True)


def kamera(nazwa, pos, cel, ogniskowa=35.0, orto=None):
    cam = bpy.data.cameras.new(nazwa)
    cam.clip_start, cam.clip_end = 0.5, 2000.0
    if orto:
        cam.type = "ORTHO"
        cam.ortho_scale = orto
    else:
        cam.lens = ogniskowa
    ob = bpy.data.objects.new(nazwa, cam)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = C @ Vector(pos)
    kier = (C @ Vector(cel)) - ob.location
    ob.rotation_euler = kier.to_track_quat("-Z", "Y").to_euler()
    return ob


def swiatlo_i_swiat():
    sc = bpy.context.scene
    swiat = bpy.data.worlds.new("Niebo")
    swiat.use_nodes = True
    tlo = swiat.node_tree.nodes.get("Background")
    studio = arg("--swiatlo", "slonce") == "studio"            # „studio” = płaskie, szare światło domyślnego miejsca Roblox
    tlo.inputs[0].default_value = (0.60, 0.64, 0.72, 1.0) if studio else (0.42, 0.62, 0.95, 1.0)
    tlo.inputs[1].default_value = 1.15 if studio else 0.9
    sc.world = swiat
    slonce = bpy.data.lights.new("Slonce", "SUN")
    slonce.energy = 1.9 if studio else 3.4
    slonce.color = (1.0, 1.0, 1.0) if studio else (1.0, 0.94, 0.82)
    slonce.angle = math.radians(6)
    ob = bpy.data.objects.new("Slonce", slonce)
    sc.collection.objects.link(ob)
    ob.rotation_euler = (math.radians(48), math.radians(8), math.radians(-128))
    ee = sc.eevee
    for atr, wart in (("taa_render_samples", int(arg("--probki", "48"))), ("use_shadows", True), ("use_gtao", True),
                      ("use_raytracing", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
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


def ujecia_auto():
    """Kadry dopasowane do sceny: przód 3/4, tył 3/4, bok, oczy gracza przed frontem (+Z), rzut z góry.
    Zakres liczony z obiektów „klocków” (własność rbx_ksztalt), z pominięciem grup, których nazwa zaczyna się od „_”
    (np. „_Podloze”) — podłoże nie rozdmuchuje kadru. Współrzędne w układzie Roblox."""
    mn, mx = [1e9] * 3, [-1e9] * 3
    for ob in bpy.data.objects:
        if "rbx_ksztalt" not in ob.keys() or str(ob.get("rbx_grupa", "")).split("/")[-1].startswith("_"):
            continue
        for naroznik in ob.bound_box:
            w = CT @ (ob.matrix_world @ Vector(naroznik))
            for i in range(3):
                mn[i] = min(mn[i], w[i])
                mx[i] = max(mx[i], w[i])
    if mn[0] > mx[0]:
        mn, mx = [-10, 0, -10], [10, 10, 10]
    c = [(mn[i] + mx[i]) / 2.0 for i in range(3)]
    sx, sy, sz = (mx[i] - mn[i] for i in range(3))
    r = math.sqrt(sx * sx + sy * sy + sz * sz) / 2.0
    d = r / math.sin(math.radians(15.5)) * 0.76                # ogniskowa 35 mm, kadr 16:9: pionowy kąt widzenia ok. 32°
    cel = (c[0], mn[1] + sy * 0.45, c[2])

    def z_kierunku(kx, ky, kz):
        n = math.sqrt(kx * kx + ky * ky + kz * kz)
        return (cel[0] + kx / n * d, cel[1] + ky / n * d, cel[2] + kz / n * d)

    oczy_d = max(sx * 0.9, sy * 1.35) + sz / 2.0
    return [
        ("a_przod34", z_kierunku(0.62, 0.45, 1.0), cel, 35.0, None),
        ("b_tyl34", z_kierunku(-0.7, 0.5, -1.0), cel, 35.0, None),
        ("c_bok", z_kierunku(1.0, 0.22, 0.12), cel, 35.0, None),
        ("d_oczy", (c[0] + sx * 0.12, mn[1] + 5.5, c[2] + oczy_d), (c[0], mn[1] + sy * 0.42, c[2]), 24.0, None),
        ("e_gora", (c[0], mx[1] + 300, c[2] + 0.01), (c[0], mn[1], c[2]), 35.0, max(sx, sz) * 1.18),
    ]


def render(folder):
    sc = bpy.context.scene
    os.makedirs(folder, exist_ok=True)
    sc.render.engine = "BLENDER_EEVEE"
    szer = int(arg("--szer", "1600"))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = szer, int(szer * 9 / 16), 100
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 90
    swiatlo_i_swiat()
    if arg("--ujecia"):                                        # własna lista: [[nazwa, [x,y,z], [x,y,z], ogniskowa, orto|null], …]
        px, py, pz = (float(v) for v in arg("--przesun", "0,0,0").split(","))   # przesunięcie mapy w świecie (ujęcia są lokalne)
        with open(arg("--ujecia"), encoding="utf-8") as f:
            ujecia = [(u[0], (u[1][0] + px, u[1][1] + py, u[1][2] + pz), (u[2][0] + px, u[2][1] + py, u[2][2] + pz),
                       float(u[3] if len(u) > 3 and u[3] else 35.0),
                       (float(u[4]) if len(u) > 4 and u[4] else None)) for u in json.load(f)]
    elif "--auto" in A:                                        # kadry wyliczone z rozmiaru sceny (pojedynczy budynek, dowolna mapa)
        ujecia = ujecia_auto()
    else:                                                      # demo „Leśna baza startowa”
        ujecia = [
            ("1_panorama", (78, 62, 104), (-2, 6, -18), 32.0, None),
            ("2_karczma", (7, 7.5, 25), (-2, 16, -42), 24.0, None),
            ("3_mapa", (0, 400, 0.01), (0, 0, 0), 35.0, 236.0),
            ("4_od_bramy", (0.5, 7.0, 101), (0, 13, 0), 22.0, None),
            ("5_portal", (42, 9, -1), (78, 7.5, -6), 28.0, None),
            ("6_arena_stajnia_wylegarnia", (-14, 17, 14), (-62, 5, -4), 26.0, None),
            ("7_wylegarnia_i_kolo", (-24, 8, -4), (-25, 6, -26), 26.0, None),
        ]
    tylko = [t for t in (arg("--tylko") or "").split(",") if t]
    for nazwa, pos, cel, ogn, orto in ujecia:
        if tylko and not any(t in nazwa for t in tylko):
            continue
        cam = kamera("KAMERA_" + nazwa, pos, cel, ogn, orto)
        if orto:                                               # mapa: kwadrat, północ (−Z Robloxa) u góry
            cam.rotation_euler = (0.0, 0.0, 0.0)
            sc.render.resolution_x = sc.render.resolution_y = min(szer, 1400)
        else:
            sc.render.resolution_x, sc.render.resolution_y = szer, int(szer * 9 / 16)
        sc.camera = cam
        sc.render.filepath = os.path.join(folder, nazwa + ".jpg")
        bpy.ops.render.render(write_still=True)
        print("KLOCKI | render %s" % sc.render.filepath, flush=True)


def main():
    if arg("--z-json"):
        z_json(arg("--z-json"))
    if arg("--render"):
        render(arg("--render"))
    if arg("--do-json"):
        do_json(arg("--do-json"))
    if arg("--zapisz"):
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=arg("--zapisz"), compress=True)
        print("KLOCKI | zapisano %s" % arg("--zapisz"), flush=True)


if __name__ == "__main__":
    main()
