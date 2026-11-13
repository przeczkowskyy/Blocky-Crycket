# -*- coding: utf-8 -*-
"""Blender 5.0 (w tle): rendery zbiorcze dla prezentacji (wołane przez swiat/postacie/zestawienie.py).

    blender -b --factory-startup --python-exit-code 1 --python blender_zestawienie.py -- --json <plik> --wyj <folder>

Plik JSON = pakiet z postac.pakiet() plus pole "zestawienie":
  {"tryb": "rzad", "nazwa": "postacie_w_skali", "szer": 1800, "wys": 760, "probki": 16,
   "obrot": -26.57, "odstep": 1.0, "obrys": [false, true], "manekin": [...czesci manekina... albo null]}
      -> wszystkie modele w jednym rzędzie, w jednej skali (kamera ortogonalna), każdy obrócony przodem 3/4;
         <nazwa>.jpg (bez obrysu) i <nazwa>_obrys.jpg (z komiksowym obrysem renderu)
  {"tryb": "film", "rozmiar": 540, "probki": 8, "start": 0, "segmenty": [["idle", 30], ["atak", 31, 8], ...]}
      -> klatki PNG <wyj>/klatki/NNNNN.png (od numeru "start") dla jednego modelu; segment = [klip, ile klatek,
         (przytrzymanie)]; pętla zawija się sama, klip jednorazowy stoi na ostatniej klatce
Kod korzysta z funkcji blender_postac.py (budowa modeli, światło, obrys, kamera), więc wygląd = wygląd plansz.
"""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

sys.dont_write_bytecode = True                                  # bez __pycache__ w repozytorium
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blender_postac as bp  # noqa: E402


def argumenty():
    import argparse
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", required=True)
    ap.add_argument("--wyj", required=True)
    return ap.parse_args(argv)


def zamroz_poze(d, m):
    """Ustaw pozę renderu modelu i odłącz akcję — poza zostaje, a zmiana klatki nie rusza tego modelu."""
    sc = bpy.context.scene
    pr = d.get("poza_renderu")
    if not m["arm"]:
        return
    if pr and pr[0] in m["akcje"]:
        bp.ustaw_akcje(m["arm"], m["akcje"][pr[0]])
        f = float(pr[1])
        sc.frame_set(int(f), subframe=f - int(f))
        m["arm"].animation_data.action = None
    else:
        bp.ustaw_akcje(m["arm"], None)
    bpy.context.view_layer.update()


def skrzynka_pkt(pts):
    xs, ys, zs = [p.x for p in pts], [p.y for p in pts], [p.z for p in pts]
    return Vector((min(xs), min(ys), min(zs))), Vector((max(xs), max(ys), max(zs)))


def kamera_orto(sc, pts, szer, wys, elewacja_deg=8.0, margines=1.06):
    """Kamera ortogonalna z przodu (od −Y Blendera), lekko z góry; kadr dopasowany do punktów i proporcji obrazu."""
    el = math.radians(elewacja_deg)
    d = Vector((0.0, -math.cos(el), math.sin(el)))             # od sceny ku kamerze
    przod = -d
    prawo = Vector((1.0, 0.0, 0.0))
    gora = prawo.cross(przod).normalized()
    xs, ys, zs = [p.dot(prawo) for p in pts], [p.dot(gora) for p in pts], [p.dot(d) for p in pts]
    sr = prawo * ((min(xs) + max(xs)) / 2) + gora * ((min(ys) + max(ys)) / 2) + d * ((min(zs) + max(zs)) / 2)
    cam = bpy.data.objects.new("_KameraRzad", bpy.data.cameras.new("_KameraRzad"))
    sc.collection.objects.link(cam)
    cd = cam.data
    cd.type, cd.sensor_fit = "ORTHO", "AUTO"
    aspekt = szer / float(wys)
    cd.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * aspekt) * margines
    odl = (max(zs) - min(zs)) + 60.0
    cd.clip_start, cd.clip_end = 0.05, odl + 200.0
    cam.location = sr + d * odl
    cam.rotation_euler = przod.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    return cam


def renderuj(sc, sciezka, szer, wys, fmt="JPEG"):
    sc.render.resolution_x, sc.render.resolution_y = int(szer), int(wys)
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = fmt
    sc.render.image_settings.color_mode = "RGB"
    if fmt == "JPEG":
        sc.render.image_settings.quality = 90
    sc.render.filepath = sciezka
    bpy.ops.render.render(write_still=True)


def tryb_rzad(pak, z, wyj):
    sc = bp.nowa_scena(30)
    tekstury = os.path.join(wyj, "_tekstury")
    obrot = math.radians(float(z.get("obrot", -26.57)))
    modele = []
    for d in pak["modele"]:
        m = bp.zbuduj_postac(d, tekstury)
        zamroz_poze(d, m)
        modele.append((d, m))
    man = None
    if z.get("manekin"):
        komorki, G = bp.paleta(z["manekin"])
        man = bp.siatka("_ManekinSkali", z["manekin"], komorki, G, bp.material_prosty("_Manekin", bp.MANEKIN, 0.7))
    # kolejność w rzędzie: manekin (jeśli jest), potem modele w kolejności pakietu
    rzad = ([("manekin", man, [man])] if man else []) + [(d["id"], m["arm"], m["render"]) for d, m in modele]
    x = 0.0
    wszystkie = []
    for i, (nazwa, korzen, obiekty) in enumerate(rzad):
        korzen.rotation_euler = (0.0, 0.0, obrot)
        korzen.location = (0.0, 0.0, 0.0)
        bpy.context.view_layer.update()
        mn, mx = skrzynka_pkt(bp.punkty(obiekty))
        if i:
            x += float(z.get("odstep", 1.0))
        korzen.location = (x - mn.x, -(mn.y + mx.y) / 2.0, 0.0)
        x += mx.x - mn.x
        bpy.context.view_layer.update()
        wszystkie += obiekty
        bp.log("RZAD %s: szer %.2f, wys %.2f" % (nazwa, mx.x - mn.x, mx.z - mn.z))
    bp.przygotuj_render(sc, int(z.get("probki", 16)))
    pts = bp.punkty(wszystkie)
    mn, mx = skrzynka_pkt(pts)
    ziemia = bp.podloze(max(300.0, (mx.x - mn.x) * 10.0))   # horyzont daleko poza kadrem
    ziemia.location = ((mn.x + mx.x) / 2.0, 0.0, 0.0)
    szer, wys = int(z.get("szer", 1800)), int(z.get("wys", 760))
    cam = kamera_orto(sc, pts, szer, wys, float(z.get("elewacja", 8.0)), float(z.get("margines", 1.06)))
    pozycje = []                                                # środek każdego modelu w poziomie (0..1 szerokości)
    for nazwa, korzen, obiekty in rzad:
        a, b = skrzynka_pkt(bp.punkty(obiekty))
        pozycje.append({"id": nazwa, "x": round(((a.x + b.x) / 2 - cam.location.x) / cam.data.ortho_scale + 0.5, 4)})
    with open(os.path.join(wyj, z["nazwa"] + "_pozycje.json"), "w", encoding="utf-8") as f:
        json.dump(pozycje, f)
    grub = float(z.get("grubosc_obrysu", 0.04))
    model_obj = [o for o in wszystkie if o is not man]
    mody = bp.dodaj_obrys(model_obj + ([man] if man and z.get("obrys_manekina") else []), grub)
    for obrys in z.get("obrys", [False, True]):
        for mod in mody:
            mod.show_render = mod.show_viewport = bool(obrys)
        p = os.path.join(wyj, z["nazwa"] + ("_obrys" if obrys else "") + ".jpg")
        renderuj(sc, p, szer, wys)
        bp.log("RENDER", p)


def tryb_film(pak, z, wyj):
    sc = bp.nowa_scena(30)
    d = pak["modele"][0]
    m = bp.zbuduj_postac(d, os.path.join(wyj, "_tekstury"))
    bp.przygotuj_render(sc, int(z.get("probki", 8)))
    klipy = {k["n"]: k for k in d["klipy"]}
    model = m["render"]
    if z.get("obrys", True):
        sk = bp.skrzynka(model)
        bp.dodaj_obrys(model, max(0.02, 0.0085 * max(bp.wymiary(sk))))
    # kadr: punkty z całej sekwencji (żeby nic nie wyszło poza kadr)
    pts = []
    for seg in z["segmenty"]:
        kl = klipy[seg[0]]
        bp.ustaw_akcje(m["arm"], m["akcje"][kl["n"]])
        for i in range(9):
            f = min(seg[1], kl["dlugosc"]) * i / 8.0
            sc.frame_set(int(f), subframe=f - int(f))
            pts += bp.punkty(model)
    sk = skrzynka_pkt(pts)
    ziemia = bp.podloze(300.0)                                  # horyzont daleko poza kadrem
    kier = z.get("kierunek", list(bp.BOHATER))
    bp.kamera(sc, kier, pts, False, margines=float(z.get("margines", 1.22)), ogniskowa=bp.OGNISKOWA)
    folder = os.path.join(wyj, "klatki")
    os.makedirs(folder, exist_ok=True)
    nr = int(z.get("start", 0))
    roz = int(z.get("rozmiar", 540))
    for seg in z["segmenty"]:
        kl = klipy[seg[0]]
        bp.ustaw_akcje(m["arm"], m["akcje"][kl["n"]])
        ile, stop = int(seg[1]), int(seg[2]) if len(seg) > 2 else 0
        for i in range(ile + stop):
            f = i if kl["petla"] else min(i, int(kl["dlugosc"]))
            sc.frame_set(f)
            bp.renderuj(sc, os.path.join(folder, "%05d.png" % nr), roz, fmt="PNG")
            nr += 1
        bp.log("FILM %s/%s: %d klatek" % (d["id"], kl["n"], ile + stop))
    with open(os.path.join(wyj, "film_%s.json" % d["id"]), "w", encoding="utf-8") as f:
        json.dump({"id": d["id"], "start": int(z.get("start", 0)), "koniec": nr}, f)


def main():
    a = argumenty()
    with open(a.json, encoding="utf-8") as f:
        pak = json.load(f)
    wyj = os.path.abspath(a.wyj)
    os.makedirs(wyj, exist_ok=True)
    z = pak["zestawienie"]
    if z["tryb"] == "rzad":
        tryb_rzad(pak, z, wyj)
    elif z["tryb"] == "film":
        tryb_film(pak, z, wyj)
    else:
        raise SystemExit("Nieznany tryb %r" % z["tryb"])


if __name__ == "__main__":
    main()
