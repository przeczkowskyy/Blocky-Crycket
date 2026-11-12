# -*- coding: utf-8 -*-
"""Test cutscenki auto-walki 3D (prośba z rozmowy 12.11 [17:08]): Rycerz kontra Leśny Slime, 9 sekund, 24 kl./s.

Cel: pokazać, jak mogłaby wyglądać walka „jak w Shakes & Fidget, ale w 3D”: gracz nie klika, postacie atakują na zmianę,
nad głowami wyskakują liczby obrażeń, na końcu łup. To previz w Blenderze (klocki, animacja z kodu) — nie assety do gry.

    blender -b --factory-startup --python-exit-code 1 --python swiat/test_cutscenki/cutscenka.py -- \
        --wyj <folder na klatki> [--klatki 1,47,92,144,165,200] [--szer 1280] [--probki 16] [--zapisz plik.blend]

Bez --klatki renderuje całość (216 klatek JPG). Film składa ffmpeg:
    ffmpeg -nostdin -framerate 24 -i klatka_%04d.jpg -c:v libx264 -crf 20 -pix_fmt yuv420p -movflags +faststart cutscenka.mp4
Układ Blendera: Z w górę; postacie stoją na osi X (rycerz po lewej, slime po prawej), kamera patrzy wzdłuż +Y.
"""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

A = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(k, d=None):
    return A[A.index(k) + 1] if k in A else d


FPS, KONIEC = 24, 216
K0, S0 = -5.0, 5.0                                             # pozycje wyjściowe rycerza i slime'a na osi X
_mat = {}


def srgb(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def mat(hexs, emisja=0.0, alfa=1.0, szorstkosc=0.6):
    klucz = (hexs, emisja, alfa)
    if klucz in _mat:
        return _mat[klucz]
    m = bpy.data.materials.new("M_%s_%s_%s" % (hexs, emisja, alfa))
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    rgb = [srgb(int(hexs[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Roughness"].default_value = szorstkosc
    if emisja:
        for n in ("Emission Color", "Emission"):
            if n in b.inputs:
                b.inputs[n].default_value = (*rgb, 1.0)
                break
        b.inputs["Emission Strength"].default_value = emisja
    if alfa < 1.0:
        b.inputs["Alpha"].default_value = alfa
        for atr, w in (("blend_method", "BLEND"), ("surface_render_method", "BLENDED")):
            if hasattr(m, atr):
                try:
                    setattr(m, atr, w)
                except Exception:
                    pass
    _mat[klucz] = m
    return m


def pusty(nazwa, poz=(0, 0, 0), rodzic=None):
    o = bpy.data.objects.new(nazwa, None)
    o.location = poz
    o.empty_display_size = 0.3
    bpy.context.scene.collection.objects.link(o)
    if rodzic:
        o.parent = rodzic
    return o


def kostka(nazwa, rozmiar, poz, kolor, rodzic=None, srodek=(0, 0, 0), **m):
    """Prostopadłościan; `srodek` przesuwa siatkę względem punktu obrotu (np. (0,0,-1) = pivot na górze kończyny)."""
    sx, sy, sz = (r / 2 for r in rozmiar)
    ox, oy, oz = srodek
    w = [(x * sx + ox, y * sy + oy, z * sz + oz) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    s = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    me = bpy.data.meshes.new(nazwa)
    me.from_pydata(w, [], s)
    me.update()
    me.materials.append(mat(kolor, **m))
    o = bpy.data.objects.new(nazwa, me)
    o.location = poz
    bpy.context.scene.collection.objects.link(o)
    if rodzic:
        o.parent = rodzic
    return o


def bryla(nazwa, typ, poz, kolor, rodzic=None, **kw):
    """Walec, stożek albo kula z operatorów Blendera."""
    m = kw.pop("m", {})
    if typ == "walec":
        bpy.ops.mesh.primitive_cylinder_add(vertices=kw.get("boki", 20), radius=kw["r"], depth=kw["h"], location=poz)
    elif typ == "stozek":
        bpy.ops.mesh.primitive_cone_add(vertices=kw.get("boki", 4), radius1=kw["r"], radius2=0, depth=kw["h"], location=poz)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, radius=kw["r"], location=poz)
    o = bpy.context.active_object
    o.name = nazwa
    o.data.materials.append(mat(kolor, **m))
    if typ == "kula":
        for p in o.data.polygons:
            p.use_smooth = True
    if rodzic:
        o.parent = rodzic
    return o


def klucz(o, f, loc=None, rot=None, skala=None):
    if loc is not None:
        o.location = loc
        o.keyframe_insert("location", frame=f)
    if rot is not None:
        o.rotation_euler = [math.radians(a) for a in rot]
        o.keyframe_insert("rotation_euler", frame=f)
    if skala is not None:
        o.scale = skala if isinstance(skala, (tuple, list)) else (skala, skala, skala)
        o.keyframe_insert("scale", frame=f)


def widoczny(o, od, do):
    """Obiekt (i dzieci) widoczny w renderze tylko w klatkach od..do."""
    for ob in [o] + list(o.children_recursive):
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=1)
        ob.hide_render = False
        ob.keyframe_insert("hide_render", frame=od)
        ob.hide_render = True
        ob.keyframe_insert("hide_render", frame=do)


FONT = None


def napis(tekst, poz, rozmiar, kolor, rodzic=None, cien="1A1420", emisja=1.6):
    """Napis zwrócony do kamery (ograniczenie Copy Rotation dodawane później), z ciemnym cieniem pod spodem."""
    global FONT
    if FONT is None:
        for sciezka in (r"C:\Windows\Fonts\ariblk.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
            if os.path.isfile(sciezka):
                FONT = bpy.data.fonts.load(sciezka)
                break
    korzen = pusty("NAPIS_" + tekst[:12], poz, rodzic)

    def jeden(nazwa, kol, przes, em):
        k = bpy.data.curves.new(nazwa, "FONT")
        k.body = tekst
        k.size = rozmiar
        k.align_x = "CENTER"
        k.align_y = "CENTER"
        k.extrude = 0.02
        if FONT:
            k.font = FONT
        k.materials.append(mat(kol, emisja=em))
        o = bpy.data.objects.new(nazwa, k)
        o.location = przes
        o.parent = korzen
        bpy.context.scene.collection.objects.link(o)
        return o

    for o in (jeden("cien", cien, (rozmiar * 0.05, -rozmiar * 0.06, -0.06), 0.0), jeden("tekst", kolor, (0, 0, 0), emisja)):
        o.visible_shadow = False
    return korzen


def nakladka(o, kamera, x, y, d=10.0):
    """Przypina obiekt do kamery jak element interfejsu: (x, y) w jednostkach na odległości d przed obiektywem."""
    o.parent = kamera
    o.location = (x, y, -d)
    o.rotation_euler = (0, 0, 0)
    for ob in [o] + list(o.children_recursive):
        ob.visible_shadow = False


# =========================================================================== scena
def zbuduj():
    sc = bpy.context.scene
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    sc.frame_start, sc.frame_end = 1, KONIEC
    sc.render.fps = FPS
    rnd = random.Random(7)

    # --- polana
    bryla("Polana", "walec", (0, 4, -0.25), "5FB548", r=34, h=0.5, boki=48)
    kostka("Ścieżka", (26, 5, 0.06), (0, 0, 0.03), "B58A5A")
    for i in range(9):
        kostka("Łata", (rnd.uniform(3, 7), rnd.uniform(2, 5), 0.04), (rnd.uniform(-16, 16), rnd.uniform(4, 16), 0.02),
               rnd.choice(["4E9E3C", "79C95A"]))
    for i in range(15):                                        # las w tle
        x = -24 + i * 3.4 + rnd.uniform(-0.8, 0.8)
        y = rnd.uniform(9, 17)
        h = rnd.uniform(5.5, 8)
        bryla("Pień", "walec", (x, y, h * 0.2), "5A3A22", r=0.55, h=h * 0.4, boki=10)
        kol = rnd.choice(["2C7A3D", "236533", "37904A"])
        for k in range(3):
            st = bryla("Igły", "stozek", (x, y, h * 0.4 + k * h * 0.26 + h * 0.2), kol, r=2.7 - k * 0.6, h=h * 0.42)
            st.rotation_euler = (0, 0, math.radians(45 * k + rnd.uniform(0, 30)))
    for x, y, a in ((-11, 5, 1.6), (12, 6.5, 2.2), (9, 3.5, 1.0), (-14, 8, 1.2)):
        g = kostka("Głaz", (a * 1.4, a, a * 0.8), (x, y, a * 0.3), rnd.choice(["8D949C", "6C727A"]))
        g.rotation_euler = (rnd.uniform(-0.2, 0.2), rnd.uniform(-0.2, 0.2), rnd.uniform(0, 1.5))
    for x, y in ((-8, 3.5), (7.5, 2.6), (14, 4), (-3, 5.5), (3.4, 6.2)):
        bryla("Grzyb trzon", "walec", (x, y, 0.35), "F3EAD7", r=0.14, h=0.7, boki=8)
        bryla("Grzyb kapelusz", "walec", (x, y, 0.8), "E23B3B", r=0.45, h=0.25, boki=10)

    # --- rycerz (patrzy w +X)
    R = pusty("RYCERZ", (K0, 0, 0))
    cialo = pusty("R_cialo", (0, 0, 2.0), R)                   # punkt obrotu w biodrach (pochylenie)
    for znak, n in ((-1, "L"), (1, "P")):
        noga = kostka("R_noga_" + n, (0.9, 0.9, 2.0), (0, znak * 0.5, 2.0), "3A4658", R, srodek=(0, 0, -1.0))
        kostka("R_but_" + n, (1.2, 1.0, 0.5), (0.15, 0, -1.75), "2A2420", noga)
    kostka("R_tors", (1.3, 2.0, 2.0), (0, 0, 1.0), "AEB6C2", cialo, szorstkosc=0.35)
    kostka("R_tabard", (1.36, 1.1, 1.7), (0.02, 0, 0.9), "2F5FB5", cialo)
    kostka("R_herb", (0.12, 0.6, 0.6), (0.7, 0, 1.2), "F5B82E", cialo).rotation_euler = (math.radians(45), 0, 0)
    kostka("R_pas", (1.4, 2.06, 0.3), (0, 0, 0.15), "5A3A22", cialo)
    kostka("R_peleryna", (0.2, 1.8, 2.6), (-0.75, 0, 0.9), "C4302B", cialo).rotation_euler = (0, math.radians(-8), 0)
    glowa = kostka("R_glowa", (1.3, 1.3, 1.3), (0, 0, 2.65), "F2C9A0", cialo)
    kostka("R_helm", (1.46, 1.46, 0.8), (0, 0, 0.42), "8D949C", glowa, szorstkosc=0.3)
    kostka("R_przylbica", (0.2, 1.46, 0.35), (0.68, 0, -0.05), "5B6470", glowa)
    kostka("R_pioropusz", (0.9, 0.25, 0.7), (-0.2, 0, 1.05), "E23B3B", glowa)
    for znak in (-1, 1):
        kostka("R_oko", (0.08, 0.2, 0.2), (0.66, znak * 0.3, -0.3), "1A1420", glowa)
    rp = kostka("R_ramie_P", (0.8, 0.8, 2.0), (0, -1.4, 2.0), "AEB6C2", cialo, srodek=(0, 0, -1.0), szorstkosc=0.35)
    rl = kostka("R_ramie_L", (0.8, 0.8, 2.0), (0, 1.4, 2.0), "AEB6C2", cialo, srodek=(0, 0, -1.0), szorstkosc=0.35)
    miecz = pusty("R_miecz", (0.1, 0, -1.9), rp)
    miecz.rotation_euler = (0, math.radians(135), 0)           # ostrze w przód i lekko w dół przy opuszczonej ręce
    kostka("M_rekojesc", (0.25, 0.25, 0.9), (0, 0, -0.1), "5A3A22", miecz)
    kostka("M_jelec", (0.3, 1.3, 0.25), (0, 0, 0.45), "F5B82E", miecz, szorstkosc=0.3)
    kostka("M_ostrze", (0.14, 0.5, 3.2), (0, 0, 2.15), "DDE3EA", miecz, szorstkosc=0.2)
    poswiata = kostka("M_poswiata", (0.5, 0.9, 3.6), (0, 0, 2.15), "FFD23F", miecz, emisja=3.0, alfa=0.5)
    poswiata.visible_shadow = False
    tarcza = kostka("R_tarcza", (0.25, 2.0, 2.3), (0.55, 0.1, -1.2), "2F5FB5", rl)
    kostka("T_okucie", (0.3, 0.5, 0.5), (0.03, 0, 0), "F5B82E", tarcza).rotation_euler = (math.radians(45), 0, 0)
    kostka("T_rant", (0.2, 2.2, 2.5), (-0.05, 0, 0), "AEB6C2", tarcza, szorstkosc=0.3)

    # --- slime (patrzy w −X)
    S = pusty("SLIME", (S0, 0, 0))
    kostka("S_cialo", (4.0, 4.0, 3.2), (0, 0, 1.6), "56C94A", S, alfa=0.86, szorstkosc=0.25)
    kostka("S_jadro", (2.4, 2.4, 1.8), (0.1, 0, 1.2), "2F8232", S)
    kostka("S_polysk", (0.9, 1.4, 0.5), (-1.3, -0.9, 2.95), "C8F7B8", S, emisja=0.6)
    for znak in (-1, 1):
        oko = kostka("S_oko", (0.2, 0.9, 1.0), (-2.02, znak * 0.85, 2.0), "FFFFFF", S, emisja=0.8)
        kostka("S_zrenica", (0.12, 0.42, 0.5), (-0.1, -znak * 0.1, -0.12), "1A1420", oko)
    kostka("S_usta", (0.14, 1.3, 0.22), (-2.02, 0, 1.05), "1A4D1A", S)
    blysk = kostka("S_blysk", (4.3, 4.3, 3.5), (0, 0, 1.6), "FFFFFF", S, alfa=0.5)
    blysk.visible_shadow = False

    # --- paski życia i podpisy: tworzone tutaj, przypinane do kamery niżej (jak HUD walki)
    def pasek(nazwa, podpis, kolor, kotwica_z_lewej):
        k = pusty("HP_" + nazwa)
        kostka("HP_tlo", (3.7, 0.38, 0.02), (0, 0, -0.02), "1A1420", k)
        kx = -1.7 if kotwica_z_lewej else 1.7
        w = kostka("HP_wypelnienie", (3.4, 0.24, 0.02), (kx, 0, 0), kolor, k, srodek=(-kx, 0, 0), emisja=1.4)
        napis(podpis, (0, 0.42, 0), 0.3, "FFFFFF", k, emisja=1.3)
        return k, w

    hp_r, hp_r_w = pasek("rycerz", "Rycerz  ·  poz. 3", "3ECF8E", True)
    hp_s, hp_s_w = pasek("slime", "Leśny Slime  ·  poz. 2", "EF5A5A", False)

    # --- łup: monety i jajko
    monety = []
    for i in range(14):
        m = bryla("Moneta", "walec", (S0, 0, 1.2), "F5B82E", r=0.32, h=0.1, boki=12, m={"emisja": 0.8, "szorstkosc": 0.3})
        m.rotation_euler = (math.radians(90), 0, 0)
        monety.append(m)
    jajo = pusty("JAJO", (S0, 0, 1.0))
    bryla("Jajo dół", "kula", (0, 0, 0.0), "F7F2E6", jajo, r=0.75)
    bryla("Jajo góra", "kula", (0, 0, 0.45), "F7F2E6", jajo, r=0.58)
    for kx, kz in ((-0.55, 0.1), (0.2, 0.55), (0.45, -0.2)):
        bryla("Jajo kropka", "kula", (kx, -0.55, kz), "6FD3FF", jajo, r=0.14)

    # --- kamera, światło, świat
    kam = bpy.data.cameras.new("Kamera")
    kam.lens = 30
    K = bpy.data.objects.new("KAMERA", kam)
    sc.collection.objects.link(K)
    sc.camera = K
    cel = pusty("CEL_KAMERY", (0, 0, 3.9))
    tt = K.constraints.new("TRACK_TO")
    tt.target = cel
    tt.track_axis, tt.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
    sl = bpy.data.lights.new("Slonce", "SUN")
    sl.energy, sl.color, sl.angle = 3.6, (1.0, 0.95, 0.84), math.radians(5)
    so = bpy.data.objects.new("Slonce", sl)
    so.rotation_euler = (math.radians(52), math.radians(6), math.radians(-35))
    sc.collection.objects.link(so)
    sw = bpy.data.worlds.new("Niebo")
    sw.use_nodes = True
    sw.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.62, 0.95, 1.0)
    sw.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    sc.world = sw

    # --- napisy: liczby obrażeń w świecie (zwrócone do kamery), banery i paski jako nakładka ekranowa
    n_d1 = napis("-128", (S0 - 0.5, -2.2, 4.6), 2.0, "FFFFFF")
    n_d2 = napis("-23", (K0 + 0.5, -2.2, 6.6), 1.7, "EF5A5A")
    n_blok = napis("BLOK!", (K0 + 0.4, -2.2, 8.4), 1.3, "4EA8FF")
    n_d3 = pusty("NAPIS_krytyk", (S0 - 1.0, -2.4, 5.4))
    napis("KRYTYK!", (0, 2.5, 0), 1.6, "FFD23F", n_d3, emisja=2.4)      # oś Y nadrzędnego = „góra ekranu”
    napis("-512", (0, 0, 0), 2.9, "FFD23F", n_d3, emisja=2.4)
    for n in (n_d1, n_d2, n_blok, n_d3):
        c = n.constraints.new("COPY_ROTATION")
        c.target = K
    n_start = napis("RYCERZ   VS   LEŚNY SLIME", (0, 0, 0), 0.62, "FFFFFF")
    n_wygrana = napis("ZWYCIĘSTWO!", (0, 0, 0), 1.15, "FFD23F", emisja=2.2)
    n_lup = napis("+120 złota     +45 EXP     +1 jajko", (0, 0, 0), 0.46, "FFFFFF")
    nakladka(n_start, K, 0, 1.55)
    nakladka(n_wygrana, K, 0, 1.75)
    nakladka(n_lup, K, 0, 0.55)
    nakladka(hp_r, K, -3.55, 2.72)
    nakladka(hp_s, K, 3.55, 2.72)

    # =========================================================================== animacja
    # kamera: powolny najazd + wstrząsy przy trafieniach
    for f, poz in ((1, (-1.5, -22.5, 5.4)), (120, (0.0, -21.5, 5.2)), (176, (0.6, -21.0, 5.0)), (216, (0.2, -19.4, 4.8))):
        klucz(K, f, loc=poz)
    for f, sila in ((47, 0.25), (92, 0.14), (144, 0.45)):
        for i, (dx, dz) in enumerate(((1, 0.6), (-0.8, -0.5), (0.5, 0.3), (-0.3, -0.2), (0, 0))):
            klucz(cel, f + i * 2, loc=(dx * sila, 0, 3.9 + dz * sila))
    klucz(cel, 1, loc=(0, 0, 3.9))
    klucz(cel, 44, loc=(0, 0, 3.9))
    klucz(cel, 176, loc=(-0.4, 0, 4.0))
    klucz(cel, 216, loc=(-1.0, 0, 4.2))

    def bezczynnosc(od, do):
        for f in range(od, do + 1, 12):
            gora = ((f - od) // 12) % 2 == 1
            klucz(cialo, f, loc=(0, 0, 2.0 + (0.12 if gora else 0.0)))
            klucz(S, f, skala=(1.04, 1.04, 0.93) if gora else (1.0, 1.0, 1.0))

    # --- 0–1 s: przedstawienie
    klucz(R, 1, loc=(K0, 0, 0), rot=(0, 0, 0), skala=1.0)
    klucz(S, 1, loc=(S0, 0, 0), skala=1.0)
    klucz(cialo, 1, rot=(0, 0, 0))
    klucz(rp, 1, rot=(0, -20, 0))
    klucz(rl, 1, rot=(0, -35, 0))
    bezczynnosc(1, 24)
    widoczny(n_start, 3, 26)
    klucz(n_start, 3, skala=0.3)
    klucz(n_start, 8, skala=1.12)
    klucz(n_start, 11, skala=1.0)
    klucz(n_start, 22, skala=1.0)
    klucz(n_start, 26, skala=0.2)

    # --- 1,0–2,7 s: atak rycerza
    klucz(R, 24, loc=(K0, 0, 0))
    klucz(cialo, 24, rot=(0, 0, 0))
    klucz(rp, 24, rot=(0, -20, 0))
    klucz(R, 36, loc=(K0 - 0.8, 0, 0), skala=(0.94, 1.0, 1.05))            # zamach: odchylenie
    klucz(cialo, 36, rot=(0, -16, 0))
    klucz(rp, 36, rot=(0, 160, 0))
    klucz(R, 41, loc=(-1.0, 0, 0.25), skala=(1.22, 1.0, 0.88))             # doskok
    klucz(cialo, 41, rot=(0, 24, 0))
    klucz(rp, 42, rot=(0, 172, 0))
    klucz(R, 46, loc=(1.9, 0, 0), skala=1.0)
    klucz(rp, 47, rot=(0, 300, 0))                                         # cięcie górą w przód
    klucz(cialo, 50, rot=(0, 10, 0))
    klucz(R, 54, loc=(1.9, 0, 0))
    klucz(R, 60, loc=(-1.6, 0, 1.5))                                       # odskok łukiem
    klucz(R, 66, loc=(K0, 0, 0), skala=(1.08, 1.0, 0.92))
    klucz(R, 70, skala=1.0)
    klucz(cialo, 66, rot=(0, 0, 0))
    klucz(rp, 66, rot=(0, 340, 0))
    # slime: trafienie 1
    klucz(S, 46, loc=(S0, 0, 0), skala=1.0)
    klucz(S, 48, loc=(S0 + 0.5, 0, 0), skala=(0.72, 1.12, 1.24))
    klucz(S, 53, loc=(S0 + 1.3, 0, 0), skala=(1.14, 1.0, 0.86))
    klucz(S, 60, loc=(S0, 0, 0), skala=(0.96, 1.0, 1.06))
    klucz(S, 66, skala=1.0)
    widoczny(blysk, 47, 49)
    widoczny(n_d1, 47, 70)
    klucz(n_d1, 47, loc=(S0 - 0.5, -2.2, 4.6), skala=0.2)
    klucz(n_d1, 51, skala=1.25)
    klucz(n_d1, 54, skala=1.0)
    klucz(n_d1, 70, loc=(S0 - 0.2, -2.2, 7.0), skala=0.9)
    klucz(hp_s_w, 46, skala=(1.0, 1, 1))
    klucz(hp_s_w, 52, skala=(0.74, 1, 1))

    # --- 3,0–4,7 s: kontra slime'a, blok tarczą
    bezczynnosc(66, 72)
    klucz(S, 72, loc=(S0, 0, 0), skala=1.0)
    klucz(S, 79, loc=(S0 + 0.3, 0, 0), skala=(1.28, 1.28, 0.58))           # przysiad
    klucz(S, 84, loc=(1.5, 0, 3.4), skala=(0.84, 0.84, 1.3))               # lot
    klucz(S, 91, loc=(-2.1, 0, 0.4), skala=(1.0, 1.0, 1.0))
    klucz(S, 93, loc=(-2.3, 0, 0.2), skala=(0.72, 1.15, 1.2))              # uderzenie w tarczę
    klucz(S, 100, loc=(1.8, 0, 2.6), skala=(1.0, 1.0, 1.0))
    klucz(S, 108, loc=(S0, 0, 0), skala=(1.22, 1.22, 0.72))
    klucz(S, 114, skala=1.0)
    klucz(rl, 84, rot=(0, -35, 0))
    klucz(rl, 90, rot=(0, -95, 0))                                         # tarcza w górę
    klucz(cialo, 84, rot=(0, 0, 0))
    klucz(cialo, 92, rot=(0, -12, 0))
    klucz(R, 90, loc=(K0, 0, 0))
    klucz(R, 97, loc=(K0 - 1.1, 0, 0))                                     # odepchnięcie
    klucz(R, 108, loc=(K0, 0, 0))
    klucz(cialo, 108, rot=(0, 0, 0))
    klucz(rl, 108, rot=(0, -35, 0))
    widoczny(n_d2, 92, 114)
    klucz(n_d2, 92, loc=(K0 + 0.5, -2.2, 6.6), skala=0.2)
    klucz(n_d2, 96, skala=1.2)
    klucz(n_d2, 99, skala=1.0)
    klucz(n_d2, 114, loc=(K0 + 0.3, -2.2, 7.6), skala=0.9)
    widoczny(n_blok, 92, 110)
    klucz(n_blok, 92, skala=0.2)
    klucz(n_blok, 96, skala=1.15)
    klucz(n_blok, 110, skala=1.0)
    klucz(hp_r_w, 91, skala=(1.0, 1, 1))
    klucz(hp_r_w, 97, skala=(0.9, 1, 1))

    # --- 5,0–6,7 s: cios krytyczny z obrotem
    bezczynnosc(114, 120)
    widoczny(poswiata, 122, 152)
    klucz(R, 120, loc=(K0, 0, 0), rot=(0, 0, 0), skala=1.0)
    klucz(cialo, 120, rot=(0, 0, 0))
    klucz(rp, 120, rot=(0, 340, 0))
    klucz(R, 131, loc=(K0 - 0.6, 0, 0), skala=(1.1, 1.1, 0.84))            # przykucnięcie i ładowanie
    klucz(rp, 131, rot=(0, 265, 0))                                        # ręka z mieczem wyciągnięta w przód
    klucz(cialo, 131, rot=(0, -10, 0))
    klucz(R, 132, rot=(0, 0, 0))
    klucz(R, 138, loc=(-1.5, 0, 0.6), skala=1.0)
    klucz(R, 144, loc=(1.7, 0, 0.3))
    klucz(R, 150, loc=(2.3, 0, 0), rot=(0, 0, -720))                       # dwa pełne obroty
    klucz(cialo, 150, rot=(0, 14, 0))
    klucz(rp, 150, rot=(0, 300, 0))
    klucz(S, 143, loc=(S0, 0, 0), skala=1.0)
    klucz(S, 146, loc=(S0 + 0.9, 0, 0.2), skala=(0.56, 1.2, 1.46))
    klucz(S, 152, loc=(S0 + 2.2, 0, 0), skala=(1.3, 1.1, 0.7))
    klucz(S, 158, loc=(S0 + 1.6, 0, 0), skala=(1.34, 1.34, 1.3))           # pęcznieje
    klucz(S, 162, skala=(0.02, 0.02, 0.02))                                # pyk
    widoczny(blysk, 144, 147)
    widoczny(n_d3, 144, 172)
    klucz(n_d3, 144, loc=(S0 - 1.0, -2.4, 5.0), skala=0.2)
    klucz(n_d3, 149, skala=1.3)
    klucz(n_d3, 153, skala=1.0)
    klucz(n_d3, 172, loc=(S0 - 0.8, -2.4, 6.2), skala=0.92)
    klucz(hp_s_w, 143, skala=(0.74, 1, 1))
    klucz(hp_s_w, 150, skala=(0.001, 1, 1))

    # --- 6,7–7,7 s: łup
    for i, m in enumerate(monety):
        kat = math.tau * i / len(monety) + rnd.uniform(-0.2, 0.2)
        r = rnd.uniform(2.2, 5.0)
        cx, cy = S0 + 1.6 + math.cos(kat) * r, math.sin(kat) * r * 0.55 - 0.6
        widoczny(m, 160, KONIEC + 1)
        klucz(m, 160, loc=(S0 + 1.6, 0, 1.4), rot=(90, 0, 0))
        klucz(m, 170, loc=((S0 + 1.6 + cx) / 2, cy / 2, rnd.uniform(3.6, 5.6)), rot=(90, 0, 200))
        klucz(m, 180, loc=(cx, cy, 0.32), rot=(90, 0, 400))
        klucz(m, 184, loc=(cx + math.cos(kat) * 0.3, cy, 0.7))
        klucz(m, 188, loc=(cx + math.cos(kat) * 0.5, cy, 0.32), rot=(90, 0, 520))
    widoczny(jajo, 162, KONIEC + 1)
    klucz(jajo, 162, loc=(S0 + 1.6, 0, 1.4), skala=0.2, rot=(0, 0, 0))
    klucz(jajo, 172, loc=(S0 + 0.6, -1.2, 4.6), skala=1.0, rot=(0, 40, 0))
    klucz(jajo, 182, loc=(S0 - 0.4, -2.0, 0.75), rot=(0, -12, 0))
    klucz(jajo, 187, loc=(S0 - 0.7, -2.1, 1.5), rot=(0, 8, 0))
    klucz(jajo, 192, loc=(S0 - 0.9, -2.2, 0.75), rot=(0, 0, 0))
    klucz(jajo, 204, rot=(0, 7, 0))
    klucz(jajo, 216, rot=(0, -7, 0))

    # --- 7,3–9 s: zwycięstwo
    klucz(R, 158, loc=(2.3, 0, 0), rot=(0, 0, -720))
    klucz(R, 166, loc=(-1.2, 0, 1.4))
    klucz(R, 174, loc=(-4.6, 0, 0), skala=(1.08, 1.0, 0.92))
    klucz(R, 178, skala=1.0)
    klucz(cialo, 174, rot=(0, 0, 0))
    klucz(rp, 174, rot=(0, 300, 0))
    klucz(rp, 182, rot=(0, 192, 0))                                        # miecz w górę
    for f, z in ((180, 0.0), (186, 1.5), (192, 0.0), (198, 1.2), (204, 0.0)):
        klucz(R, f, loc=(-4.6, 0, z))
    widoczny(n_wygrana, 178, KONIEC + 1)
    klucz(n_wygrana, 178, skala=0.15)
    klucz(n_wygrana, 185, skala=1.2)
    klucz(n_wygrana, 189, skala=1.0)
    klucz(n_wygrana, 216, skala=1.05)
    widoczny(n_lup, 188, KONIEC + 1)
    klucz(n_lup, 188, skala=0.2)
    klucz(n_lup, 194, skala=1.1)
    klucz(n_lup, 197, skala=1.0)
    return sc


def render(sc, folder):
    os.makedirs(folder, exist_ok=True)
    sc.render.engine = "BLENDER_EEVEE"
    szer = int(arg("--szer", "1280"))
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = szer, int(szer * 9 / 16), 100
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92
    for atr, w in (("taa_render_samples", int(arg("--probki", "16"))), ("use_shadows", True), ("use_gtao", True)):
        if hasattr(sc.eevee, atr):
            try:
                setattr(sc.eevee, atr, w)
            except Exception:
                pass
    sc.view_settings.view_transform = "Standard"
    klatki = [int(k) for k in arg("--klatki").split(",")] if arg("--klatki") else range(1, KONIEC + 1)
    for f in klatki:
        sc.frame_set(f)
        sc.render.filepath = os.path.join(folder, "klatka_%04d.jpg" % f)
        bpy.ops.render.render(write_still=True)
        if f % 24 == 0 or arg("--klatki"):
            print("CUTSCENKA | klatka %d" % f, flush=True)


if __name__ == "__main__":
    scena = zbuduj()
    if arg("--zapisz"):
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=arg("--zapisz"), compress=True)
    if arg("--wyj"):
        render(scena, arg("--wyj"))
