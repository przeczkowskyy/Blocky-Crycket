# -*- coding: utf-8 -*-
"""Blender (bez okna): jajko biomu na wzór leśnego jaja Pawła — siatki Egg, ShellBottom, ShellTopLeft,
ShellTopRight (kawałki skorupy dokładnie z linii podziału ksztalt.py), podstawa i ozdoby biomu jako osobne siatki
o czytelnych nazwach; eksport GLB + FBX (bez animacji: ruch gra klient w Roblox) i rendery podglądu.

    blender -b --factory-startup --python-exit-code 1 --python swiat/jajka_biomow/blender_jajko.py -- \
        --biom bagno --wyj swiat/jajka_biomow/modele --klatki <folder renderów>
    ... -- --zestawienie --klatki <folder>          (oba jajka + przybliżenie leśnego w jednej skali)

Układ: liczę w osiach pliku Roblox (x w prawo, y w górę, z = przód) i przeliczam na Blender (x, −z, y).
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import atlas as A  # noqa: E402
import ksztalt as K  # noqa: E402

REPO = os.path.dirname(os.path.dirname(TU))


def log(*a):
    print("JAJKA |", *a, flush=True)


def B(p):
    return (p[0], -p[2], p[1])


def lin(h):
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def v3(*a):
    return Vector(a)


# ----------------------------------------------------------------------------------------------- budowa siatek
class Siatka:
    """Siatka składana ręcznie: wierzchołki wspólne (po położeniu), UV na rogach ścian, kierunek ścian
    sprawdzany punktem odniesienia (normalna od punktu `od` albo do góry)."""

    def __init__(self):
        self.v, self.klucze, self.f, self.uv, self.mat, self.gl = [], {}, [], [], [], []

    def w(self, p):
        if p[2] < 0.0:   # nic poniżej ziemi: najniższy punkt modelu = 0 (tam stoi korzeń w Studio)
            p = (p[0], p[1], 0.0)
        k = (round(p[0], 5), round(p[1], 5), round(p[2], 5))
        i = self.klucze.get(k)
        if i is None:
            i = len(self.v)
            self.v.append(Vector(p))
            self.klucze[k] = i
        return i

    def sciana(self, pts, uvs, od=None, gora=None, mat=0, gladka=False, odwrotnie=False):
        idx = [self.w(p) for p in pts]
        par = list(zip(idx, uvs))
        czyste = []
        for i, (a, u) in enumerate(par):
            if a != par[i - 1][0] or len(par) == 1:
                czyste.append((a, u))
        while len(czyste) > 1 and czyste[0][0] == czyste[-1][0]:
            czyste.pop()
        if len(set(a for a, _ in czyste)) < 3:
            return
        idx = [a for a, _ in czyste]
        uvs = [u for _, u in czyste]
        if od is not None or gora is not None:
            n = Vector((0, 0, 0))
            for i in range(len(idx)):
                a, b = self.v[idx[i]], self.v[idx[(i + 1) % len(idx)]]
                n += Vector(((a.y - b.y) * (a.z + b.z), (a.z - b.z) * (a.x + b.x), (a.x - b.x) * (a.y + b.y)))
            c = sum((self.v[i] for i in idx), Vector()) / len(idx)
            kier = Vector(gora) if gora is not None else (c - Vector(od))
            if n.dot(kier) < 0:
                idx.reverse()
                uvs.reverse()
        if odwrotnie:
            idx.reverse()
            uvs.reverse()
        self.f.append(idx)
        self.uv.append(uvs)
        self.mat.append(mat)
        self.gl.append(gladka)

    def obiekt(self, nazwa, materialy, przelicz=False):
        me = bpy.data.meshes.new(nazwa)
        me.from_pydata([tuple(p) for p in self.v], [], self.f)
        uvl = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            uvs = self.uv[poly.index]
            for k, li in enumerate(poly.loop_indices):
                uvl.data[li].uv = uvs[k]
            poly.material_index = self.mat[poly.index]
            poly.use_smooth = self.gl[poly.index]
        for m in materialy:
            me.materials.append(m)
        if przelicz:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            bm.to_mesh(me)
            bm.free()
        me.validate()
        me.update()
        ob = bpy.data.objects.new(nazwa, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


def ramka(t):
    t = Vector(t).normalized()
    pom = Vector((0, 1, 0)) if abs(t.y) < 0.9 else Vector((1, 0, 0))
    n = t.cross(pom).normalized()
    return n, t.cross(n).normalized()


def rura(s, punkty, promienie, boki, biom, pole, mat=0, zamknij=(True, True), gladka=True, skret=0.0):
    """Rura wzdłuż łamanej (punkty w osiach Roblox -> zamieniam na Blender). UV: każdy odcinek = całe pole atlasu."""
    P = [Vector(B(p)) for p in punkty]
    n_prev = None
    pierscienie = []
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        if n_prev is None:
            n, b = ramka(t)
        else:
            n = (n_prev - t * n_prev.dot(t)).normalized()
            b = t.cross(n).normalized()
        n_prev = n
        r = promienie[i]
        rz = []
        for j in range(boki):
            a = 2 * math.pi * j / boki + skret * i
            rz.append(p + (n * math.cos(a) + b * math.sin(a)) * r)
        pierscienie.append((p, rz))
    for i in range(len(P) - 1):
        c0, r0 = pierscienie[i]
        c1, r1 = pierscienie[i + 1]
        cs = (c0 + c1) / 2
        for j in range(boki):
            j2 = (j + 1) % boki
            u0, u1 = j / boki, (j + 1) / boki
            uv = [A.uv(biom, pole, u0, 0), A.uv(biom, pole, u1, 0), A.uv(biom, pole, u1, 1), A.uv(biom, pole, u0, 1)]
            s.sciana([r0[j], r0[j2], r1[j2], r1[j]], uv, od=cs, mat=mat, gladka=gladka)
    for koniec, (c, rz) in ((0, pierscienie[0]), (1, pierscienie[-1])):
        if not zamknij[koniec]:
            continue
        sasiad = pierscienie[1][0] if koniec == 0 else pierscienie[-2][0]
        for j in range(boki):
            j2 = (j + 1) % boki
            uvc = A.uv(biom, pole, 0.5, 0.5)
            s.sciana([c, rz[j], rz[j2]], [uvc, A.uv(biom, pole, 0.3, 0.3), A.uv(biom, pole, 0.7, 0.3)],
                     od=sasiad, mat=mat, gladka=False)


def lisc(s, nasada, kier, bok, dlug, szer, biom, pole, opad=0.5, zgiecie=0.18, mat=0, rzedy=None):
    """Liść wstęgą wzdłuż nerwu (3 wierzchołki w rzędzie: brzeg, nerw, brzeg — zagięcie „V”), dwustronny.
    Kształt i UV z atlas.kontur, więc ciemna kreska tekstury leży dokładnie na brzegu siatki."""
    f = A.KSZTALTY[pole]
    n = rzedy or A.RZEDY_KSZTALTU[pole]
    kier = Vector(kier).normalized()   # wszystko w osiach Roblox (y w górę)
    bok = (Vector(bok) - kier * Vector(bok).dot(kier)).normalized()
    norm = kier.cross(bok).normalized()
    if norm.y < 0:
        norm = -norm
    rz = []
    p = Vector(nasada)
    d = kier.copy()
    krok = dlug / n
    for k in range(n + 1):
        y = k / n
        hw = f(y) / 2
        sr = p.copy()
        zg = norm * (zgiecie * szer * hw)
        rz.append([sr + bok * (-hw * szer) - zg, sr, sr + bok * (hw * szer) - zg, y])
        # opadanie: kierunek skręca w dół
        d = (d - Vector((0, opad * krok * 0.9, 0))).normalized()
        p = p + d * krok
    for strona in (0, 1):
        przes = norm * (-0.004 if strona else 0.0)
        for k in range(n):
            a, b_ = rz[k], rz[k + 1]
            for (i0, i1) in ((0, 1), (1, 2)):
                x0 = 0.5 + (i0 - 1) * f(a[3]) / 2
                x1 = 0.5 + (i1 - 1) * f(a[3]) / 2
                x2 = 0.5 + (i1 - 1) * f(b_[3]) / 2
                x3 = 0.5 + (i0 - 1) * f(b_[3]) / 2
                pts = [B(a[i0] + przes), B(a[i1] + przes), B(b_[i1] + przes), B(b_[i0] + przes)]
                uv = [A.uv(biom, pole, x0, a[3]), A.uv(biom, pole, x1, a[3]), A.uv(biom, pole, x2, b_[3]),
                      A.uv(biom, pole, x3, b_[3])]
                s.sciana(pts, uv, mat=mat, gladka=False, odwrotnie=bool(strona))


def bryla(s, srodek, r, wys, boki=6, rzedy=3, ziarno=0, biom=None, pole=None, mat=0, splaszcz=1.0, losowo=0.18):
    """Niska kanciasta bryła (kamień, bąbel, cętka): sfera boki × rzedy z rozrzutem."""
    rr = random.Random(ziarno)
    c = Vector(srodek)
    pier = []
    for k in range(1, rzedy):
        th = math.pi * k / rzedy
        rz = []
        for j in range(boki):
            a = 2 * math.pi * (j + 0.5 * (k % 2)) / boki
            q = 1 + rr.uniform(-losowo, losowo)
            rz.append(c + Vector((math.sin(th) * math.cos(a) * r * q, math.cos(th) * wys * q * splaszcz,
                                  math.sin(th) * math.sin(a) * r * q)))
        pier.append(rz)
    gora = c + Vector((0, wys * splaszcz, 0))
    dol = c - Vector((0, wys * splaszcz, 0))
    cb = Vector(B(c))

    def uvp(p):
        if pole is None:
            return (0.5, 0.5)
        return A.uv(biom, pole, 0.5 + (p.x - c.x) / (2.4 * r), 0.5 + (p.z - c.z) / (2.4 * r))
    for j in range(boki):
        j2 = (j + 1) % boki
        s.sciana([B(gora), B(pier[0][j]), B(pier[0][j2])], [uvp(gora), uvp(pier[0][j]), uvp(pier[0][j2])], od=cb, mat=mat)
        s.sciana([B(dol), B(pier[-1][j]), B(pier[-1][j2])], [uvp(dol), uvp(pier[-1][j]), uvp(pier[-1][j2])], od=cb, mat=mat)
        for k in range(len(pier) - 1):
            q = [pier[k][j], pier[k][j2], pier[k + 1][j2], pier[k + 1][j]]
            s.sciana([B(x) for x in q], [uvp(x) for x in q], od=cb, mat=mat)


def krysztal(s, podstawa, kier, r, h, boki=6, mat=0, obrot=0.0):
    kier = Vector(kier).normalized()
    n, b = ramka(kier)
    c0 = Vector(podstawa)
    dol = [c0 + (n * math.cos(obrot + 2 * math.pi * j / boki) + b * math.sin(obrot + 2 * math.pi * j / boki)) * r
           for j in range(boki)]
    gora = [p + kier * h for p in dol]
    gora = [c0 + kier * h + (p - c0) * 0.88 for p in dol]
    szpic = c0 + kier * (h + r * 1.6)
    cb = Vector(B(c0 + kier * h * 0.5))
    uv = (0.5, 0.5)
    for j in range(boki):
        j2 = (j + 1) % boki
        s.sciana([B(dol[j]), B(dol[j2]), B(gora[j2]), B(gora[j])], [uv] * 4, od=cb, mat=mat)
        s.sciana([B(gora[j]), B(gora[j2]), B(szpic)], [uv] * 3, od=cb, mat=mat)
        s.sciana([B(dol[j]), B(dol[j2]), B(c0 - kier * 0.02)], [uv] * 3, od=cb, mat=mat)


def kopczyk(s, profil, segmenty, rmax, biom, pole, ziarno, szum=0.04, kraj_los=0.12, mat=0, dziury=(), potega=2):
    """Kopiec / gniazdo: siatka biegunowa, wysokość z profilu [(r_ułamek, y)], brzeg nieregularny, najniższy
    pierścień na y = 0. UV rzutem z góry na pole atlasu."""
    rr = random.Random(ziarno)
    kraj = [1.0 + rr.uniform(-kraj_los, kraj_los * 0.5) for _ in range(segmenty)]
    pier = []
    for k, (fr, y) in enumerate(profil):
        rz = []
        for j in range(segmenty):
            a = 2 * math.pi * j / segmenty
            r = fr * rmax * (kraj[j] if fr > 0.5 else 1.0)
            yy = y if (k == len(profil) - 1 or fr == 0) else y + rr.uniform(-szum, szum)
            x, z = r * math.cos(a), r * math.sin(a)
            for (dx, dz, dr, dy) in dziury:
                d = math.hypot(x - dx, z - dz)
                if d < dr and k < len(profil) - 1:
                    yy = min(yy, dy + (yy - dy) * (d / dr) ** potega)
            rz.append(Vector((x, yy, z)))
        pier.append(rz)

    def uvp(p):
        return A.uv(biom, pole, 0.5 + p.x / (2.2 * rmax), 0.5 + p.z / (2.2 * rmax))
    for k in range(len(pier) - 1):
        for j in range(segmenty):
            j2 = (j + 1) % segmenty
            q = [pier[k][j], pier[k][j2], pier[k + 1][j2], pier[k + 1][j]]
            s.sciana([B(x) for x in q], [uvp(x) for x in q], gora=(0, 0, 1), mat=mat, gladka=True)
    return pier


# ----------------------------------------------------------------------------------------------- materiały
def mat_obraz(nazwa, sciezka, szorstkosc=0.75):
    m = bpy.data.materials.new(nazwa)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(sciezka)
    tex.interpolation = "Linear"
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = szorstkosc
    for nazwa_we in ("Specular IOR Level", "Specular"):
        if nazwa_we in bsdf.inputs:
            bsdf.inputs[nazwa_we].default_value = 0.2
    return m


def mat_kolor(nazwa, hexk, szorstkosc=0.6):
    m = bpy.data.materials.new(nazwa)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*lin(hexk), 1.0)
    bsdf.inputs["Roughness"].default_value = szorstkosc
    m.diffuse_color = (*lin(hexk), 1.0)
    m["kolor"] = hexk
    return m


def dodaj_blask(m, kolor_hex, sila, maska=None):
    """Tylko do renderu podglądu (po eksporcie): świecenie jak Neon / EmissiveMask w Roblox."""
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    kol = (*lin(kolor_hex), 1.0)
    if maska:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = bpy.data.images.load(maska)
        tex.image.colorspace_settings.name = "Non-Color"
        mix = nt.nodes.new("ShaderNodeMixRGB")
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 1.0
        nt.links.new(tex.outputs["Color"], mix.inputs[1])
        mix.inputs[2].default_value = kol
        nt.links.new(mix.outputs[0], bsdf.inputs["Emission Color"])
    else:
        bsdf.inputs["Emission Color"].default_value = kol
    bsdf.inputs["Emission Strength"].default_value = sila


# ----------------------------------------------------------------------------------------------- jajo i skorupa
def uv_jajo(th, U):
    return (U, 1.0 - th / math.pi * K.V_MAX)


def uv_pas(pas, th, U):
    v = pas[0] + (pas[1] - pas[0]) * (th / math.pi)
    return (U, 1.0 - v)


def powierzchnia(s, rzedy, mat=0):
    """Zewnętrzna powierzchnia kawałka z rzędów (theta, alfa, U)."""
    c = Vector(B(K.srodek()))
    for k in range(len(rzedy) - 1):
        a, b_ = rzedy[k], rzedy[k + 1]
        for j in range(len(a) - 1):
            q = [a[j], a[j + 1], b_[j + 1], b_[j]]
            s.sciana([B(K.punkt(t, al)) for t, al, _ in q], [uv_jajo(t, U) for t, _, U in q], od=c, mat=mat, gladka=True)


def skorupa(s, rzedy, mat=0):
    """Kawałek skorupy z grubością: zewnątrz (tekstura jaja), wewnątrz (pas wnętrza), krawędź (pas krawędzi)."""
    powierzchnia(s, rzedy, mat)
    c = Vector(K.srodek())

    def wew(t, al):
        p = Vector(K.punkt(t, al))
        d = p - c
        return p - d.normalized() * K.GRUBOSC
    for k in range(len(rzedy) - 1):
        a, b_ = rzedy[k], rzedy[k + 1]
        for j in range(len(a) - 1):
            q = [a[j], a[j + 1], b_[j + 1], b_[j]]
            s.sciana([B(wew(t, al)) for t, al, _ in q], [uv_pas(K.PAS_WNETRZE, t, U) for t, _, U in q],
                     od=B(K.srodek()), mat=mat, gladka=True, odwrotnie=False)
            # wnętrze: normalna do środka jaja
            s.f[-1].reverse()
            s.uv[-1].reverse()
    # krawędzie: obrzeże (rząd 0) i dla kawałków górnych także obie linie boczne (kolumna 0 i ostatnia)
    brzegi = [list(zip(rzedy[0][:-1], rzedy[0][1:]))]
    if rzedy[-1][0][0] < 1e-6:   # kawałek górny (kończy się na czubku): boki
        brzegi.append([(rzedy[k][0], rzedy[k + 1][0]) for k in range(len(rzedy) - 1)])
        brzegi.append([(rzedy[k][-1], rzedy[k + 1][-1]) for k in range(len(rzedy) - 1)])
    for brzeg in brzegi:
        for (t0, a0, U0), (t1, a1, U1) in brzeg:
            q = [K.punkt(t0, a0), K.punkt(t1, a1), wew(t1, a1), wew(t0, a0)]
            v = 1.0 - (K.PAS_KRAWEDZ[0] + K.PAS_KRAWEDZ[1]) / 2
            s.sciana([B(x) for x in q], [(U0, v), (U1, v), (U1, v - 0.01), (U0, v - 0.01)], mat=mat, gladka=False)


def jajo_i_skorupy(pod, m_jajo):
    rz_dol, rz_p, rz_l = pod.rzedy_dol(), pod.rzedy_gora(True), pod.rzedy_gora(False)
    s = Siatka()
    for rz in (rz_dol, rz_p, rz_l):
        powierzchnia(s, rz)
    ob = {"Egg": s.obiekt("Egg", [m_jajo], przelicz=True)}
    for nazwa, rz in (("ShellBottom", rz_dol), ("ShellTopRight", rz_p), ("ShellTopLeft", rz_l)):
        s = Siatka()
        skorupa(s, rz)
        ob[nazwa] = s.obiekt(nazwa, [m_jajo], przelicz=True)
    return ob


# ----------------------------------------------------------------------------------------------- Bagno
def bagno(m):
    biom = "bagno"
    r = random.Random(41)
    ob = {}
    # --- błotne gniazdo + kamienie (MudBed)
    s = Siatka()
    kaluza = (-0.95, 0.85, 0.55, 0.06)   # x, z (przód +), promień, poziom wody
    RMAX = 1.85
    profil = [(0.0, 0.48), (0.17, 0.5), (0.30, 0.52), (0.36, 0.58), (0.40, 0.6), (0.45, 0.57), (0.50, 0.5),
              (0.57, 0.41), (0.64, 0.33), (0.72, 0.24), (0.80, 0.16), (0.87, 0.1), (0.93, 0.05), (1.0, 0.0)]

    def hb(x, z):
        fr = math.hypot(x, z) / RMAX
        y = profil[-1][1]
        for (f0, y0), (f1, y1) in zip(profil, profil[1:]):
            if f0 <= fr <= f1:
                y = y0 + (y1 - y0) * (fr - f0) / (f1 - f0)
                break
        d = math.hypot(x - kaluza[0], z - kaluza[1])
        if d < kaluza[2] + 0.25:
            y = min(y, 0.02 + (y - 0.02) * (d / (kaluza[2] + 0.25)) ** 4)
        return y
    kopczyk(s, profil, 32, RMAX, biom, "bloto", 5, 0.035, 0.12, dziury=[(kaluza[0], kaluza[1], kaluza[2] + 0.25, 0.02)],
            potega=4)
    for i, (a, rad, sk) in enumerate([(0.3, 1.15, 0.16), (1.2, 1.3, 0.12), (2.3, 1.05, 0.18), (3.4, 1.35, 0.14),
                                      (4.3, 1.2, 0.2), (5.4, 1.1, 0.13), (2.9, 0.9, 0.1)]):
        x, z = rad * math.cos(a), rad * math.sin(a)
        if math.hypot(x - kaluza[0], z - kaluza[1]) < kaluza[2] + 0.15:
            continue
        bryla(s, (x, hb(x, z) + sk * 0.15, z), sk, sk * 0.7, 6, 3, 100 + i, biom, "kamien")
    ob["MudBed"] = s.obiekt("MudBed", [m["ozdoby"]])
    # --- kałuża (Water)
    s = Siatka()
    cx, cz, kr, ky = kaluza
    n = 14
    kraj = [kr * r.uniform(0.85, 1.08) for _ in range(n)]
    for j in range(n):
        a0, a1 = 2 * math.pi * j / n, 2 * math.pi * (j + 1) / n
        p0 = (cx + kraj[j] * math.cos(a0), ky, cz + kraj[j] * math.sin(a0))
        p1 = (cx + kraj[(j + 1) % n] * math.cos(a1), ky, cz + kraj[(j + 1) % n] * math.sin(a1))
        pc = (cx, ky, cz)

        def uvw(p):
            return A.uv(biom, "woda", 0.5 + (p[0] - cx) / (2.2 * kr), 0.5 + (p[2] - cz) / (2.2 * kr))
        s.sciana([B(pc), B(p0), B(p1)], [uvw(pc), uvw(p0), uvw(p1)], gora=(0, 0, 1))
    ob["Water"] = s.obiekt("Water", [m["ozdoby"]])
    # --- lilie wodne (Lilies): liście grzybienia na wodzie i na błocie, dwa kwiaty
    s = Siatka()
    for (x, z, rad, obr) in [(cx - 0.18, cz + 0.12, 0.2, 0.4), (cx + 0.22, cz - 0.1, 0.16, 2.1), (cx + 0.05, cz + 0.33, 0.13, 4.0),
                             (1.25, 0.95, 0.17, 5.2)]:
        y = ky + 0.012 if math.hypot(x - cx, z - cz) < kr else hb(x, z) + 0.015
        kont = A.grzybien_kontur(14)
        c = kont[0]
        pts = kont[1:]
        for j in range(len(pts) - 1):
            def P(q):
                ax, az = (q[0] - 0.5) * 2 * rad / 0.94, (q[1] - 0.5) * 2 * rad / 0.94
                return (x + ax * math.cos(obr) - az * math.sin(obr), y, z + ax * math.sin(obr) + az * math.cos(obr))
            s.sciana([B(P(c)), B(P(pts[j])), B(P(pts[j + 1]))],
                     [A.uv(biom, "grzybien", *c), A.uv(biom, "grzybien", *pts[j]), A.uv(biom, "grzybien", *pts[j + 1])],
                     gora=(0, 0, 1))
    for (x, z, rad, y0) in [(cx - 0.18, cz + 0.12, 0.13, ky + 0.02), (1.25, 0.95, 0.11, hb(1.25, 0.95) + 0.02)]:
        for i in range(8):
            a = 2 * math.pi * i / 8 + (0.2 if i % 2 else 0)
            dl = rad * (1.0 if i % 2 == 0 else 0.8)
            kier = (math.cos(a) * 0.75, 0.66, math.sin(a) * 0.75)
            lisc(s, Vector((x, y0, z)), Vector(kier), Vector((-math.sin(a), 0, math.cos(a))), dl, dl * 0.75, biom, "platek", opad=-0.4, zgiecie=0.3)
        rura(s, [(x, y0, z), (x, y0 + 0.07, z)], [0.035, 0.03], 6, biom, "srodek")
    ob["Lilies"] = s.obiekt("Lilies", [m["ozdoby"]])
    # --- korzenie (Roots): spod jaja na błoto i w ziemię
    s = Siatka()
    for i, a in enumerate([0.5, 1.6, 2.6, 3.8, 4.9, 5.7]):
        if abs(a - math.atan2(cz, cx) % (2 * math.pi)) < 0.35:
            continue
        rr0 = 0.45
        dl = r.uniform(1.05, 1.25)
        pts, prom = [], []
        for k in range(8):
            t = k / 7
            rad = rr0 + t * dl
            aa = a + math.sin(t * 3 + i) * 0.18
            x, z = rad * math.cos(aa), rad * math.sin(aa)
            y = hb(x, z) + 0.03 + 0.07 * math.sin(t * math.pi) - (0.09 if t > 0.95 else 0.0)
            pts.append((x, y, z))
            prom.append(0.11 * (1 - t * 0.65))
        rura(s, pts, prom, 6, biom, "kora", skret=0.15)
    ob["Roots"] = s.obiekt("Roots", [m["ozdoby"]])
    # --- trzciny z pałkami (Reeds): kępy z tyłu i po bokach
    s = Siatka()
    kepy = [(-1.15, -0.75, 6), (1.05, -0.95, 5), (-1.45, 0.15, 3), (0.25, -1.35, 4)]
    for (kx, kz, ile) in kepy:
        for i in range(ile):
            x, z = kx + r.uniform(-0.18, 0.18), kz + r.uniform(-0.18, 0.18)
            h = r.uniform(1.3, 2.3)
            y0 = hb(x, z) - 0.02
            lean = Vector((r.uniform(-0.12, 0.12), 1, r.uniform(-0.12, 0.12))).normalized()
            if i % 2 == 0:   # łodyga z pałką
                pts = [Vector((x, y0, z)) + lean * h * t + Vector((0.06 * t * t, 0, 0)) for t in (0, 0.35, 0.7, 1.0)]
                rura(s, [tuple(p) for p in pts], [0.028, 0.024, 0.02, 0.017], 5, biom, "lodyga")
                g = pts[-1]
                pk = [g - lean * 0.38, g - lean * 0.34, g - lean * 0.04, g]
                rura(s, [tuple(p) for p in pk], [0.03, 0.068, 0.068, 0.035], 6, biom, "palka", gladka=True)
                rura(s, [tuple(g), tuple(g + lean * 0.22)], [0.012, 0.004], 4, biom, "lodyga")
            # liście trzciny
            for kk in range(1 if i % 2 == 0 else 2):
                a = r.uniform(0, 6.28)
                kier = Vector((math.cos(a) * 0.35, 1, math.sin(a) * 0.35)).normalized()
                bok = Vector((-math.sin(a), 0, math.cos(a)))
                lisc(s, Vector((x, y0, z)), kier, bok, r.uniform(0.9, 1.6), 0.12, biom,
                     "trzcina", opad=r.uniform(0.25, 0.55), zgiecie=0.25)
    ob["Reeds"] = s.obiekt("Reeds", [m["ozdoby"]])
    # --- muchomory bagienne (MushroomStems / MushroomCaps / MushroomSpots)
    st, cp, sp = Siatka(), Siatka(), Siatka()
    for i, (x, z, sk) in enumerate([(0.78, 0.55, 1.0), (0.95, 0.3, 0.7), (0.6, 0.82, 0.6), (-0.62, -0.78, 0.85),
                                    (-0.25, 1.05, 0.55)]):
        y0 = hb(x, z)
        h = 0.26 * sk
        rura(st, [(x, y0 - 0.05, z), (x + 0.02, y0 + h * 0.6, z), (x, y0 + h, z)], [0.05 * sk, 0.045 * sk, 0.04 * sk], 6, biom, "bloto")
        rc = 0.2 * sk
        top = Vector((x, y0 + h, z))
        prof = [(1.0, -0.02), (0.95, 0.06), (0.75, 0.15), (0.42, 0.21), (0.0, 0.23)]
        pier = []
        for fr, dy in prof:
            pier.append([top + Vector((fr * rc * math.cos(2 * math.pi * j / 8), dy * sk, fr * rc * math.sin(2 * math.pi * j / 8)))
                         for j in range(8)])
        for k in range(len(pier) - 1):
            for j in range(8):
                j2 = (j + 1) % 8
                q = [pier[k][j], pier[k][j2], pier[k + 1][j2], pier[k + 1][j]]
                cp.sciana([B(p) for p in q], [(0.5, 0.5)] * 4, od=B(top - Vector((0, 0.1, 0))))
        for j in range(8):
            j2 = (j + 1) % 8
            cp.sciana([B(top + Vector((0, -0.01, 0))), B(pier[0][j]), B(pier[0][j2])], [(0.5, 0.5)] * 3, gora=(0, 0, -1))
        for kk in range(5):
            a = 2 * math.pi * kk / 5 + i
            fr = 0.55 if kk % 2 else 0.8
            p = top + Vector((fr * rc * math.cos(a), (0.17 if fr < 0.7 else 0.1) * sk, fr * rc * math.sin(a)))
            bryla(sp, tuple(p), 0.035 * sk, 0.018 * sk, 5, 2, 300 + i * 10 + kk)
    ob["MushroomStems"] = st.obiekt("MushroomStems", [m["trzon"]])
    ob["MushroomCaps"] = cp.obiekt("MushroomCaps", [m["kapelusz"]])
    ob["MushroomSpots"] = sp.obiekt("MushroomSpots", [m["neon"]])
    # --- świecące bąble (Bubbles): na błocie, na wodzie i kilka w powietrzu
    s = Siatka()
    for i, (x, y, z, rad) in enumerate([(cx + 0.3, ky, cz + 0.25, 0.07), (cx - 0.3, ky, cz - 0.15, 0.05), (0.62, None, -0.55, 0.06),
                                        (-0.78, None, 0.4, 0.08), (1.05, None, -0.2, 0.05), (cx, 0.5, cz, 0.045),
                                        (cx + 0.15, 0.85, cz - 0.05, 0.035), (-0.4, None, -1.0, 0.06), (0.9, 0.95, 0.2, 0.03)]):
        bryla(s, (x, hb(x, z) if y is None else y, z), rad, rad, 6, 3, 500 + i, losowo=0.05)
    ob["Bubbles"] = s.obiekt("Bubbles", [m["neon"]])
    # --- kryształy (Crystals) i odłamki (Shards)
    s = Siatka()
    for (x, z, ile) in [(0.9, -0.55, 4), (-0.85, -0.1, 3), (0.35, 0.95, 2)]:
        y0 = hb(x, z) - 0.03
        for i in range(ile):
            a = r.uniform(0, 6.28)
            kier = Vector((math.cos(a) * 0.45 + x * 0.25, 1, math.sin(a) * 0.45 + z * 0.25)).normalized()
            krysztal(s, Vector((x + r.uniform(-0.08, 0.08), y0, z + r.uniform(-0.08, 0.08))), kier,
                     r.uniform(0.05, 0.09), r.uniform(0.18, 0.42) * (1.3 if i == 0 else 1.0), 6, obrot=r.uniform(0, 1))
    ob["Crystals"] = s.obiekt("Crystals", [m["neon"]])
    s = Siatka()
    for i in range(7):
        a = r.uniform(0, 6.28)
        rad = r.uniform(1.05, 1.5)
        x, z = rad * math.cos(a), rad * math.sin(a)
        krysztal(s, Vector((x, hb(x, z) - 0.01, z)), Vector((r.uniform(-0.6, 0.6), 1, r.uniform(-0.6, 0.6))), 0.03,
                 r.uniform(0.05, 0.1), 4, obrot=a)
    ob["Shards"] = s.obiekt("Shards", [m["neon"]])
    return ob


# ----------------------------------------------------------------------------------------------- Dżungla
def dzungla(m):
    biom = "dzungla"
    r = random.Random(77)
    ob = {}
    s = Siatka()
    # --- kamienny cokół (StoneBase): dwa ośmiokątne stopnie z fryzami, luźne bloki
    def osmiokat(R, y0, y1, pole_bok, gorna=True, r_wew=None):
        rogi = [(R * math.cos(math.pi / 8 + 2 * math.pi * j / 8), R * math.sin(math.pi / 8 + 2 * math.pi * j / 8)) for j in range(8)]
        for j in range(8):
            (x0, z0), (x1, z1) = rogi[j], rogi[(j + 1) % 8]
            q = [(x0, y0, z0), (x1, y0, z1), (x1, y1, z1), (x0, y1, z0)]
            s.sciana([B(p) for p in q], [A.uv(biom, pole_bok, 0, 0), A.uv(biom, pole_bok, 1, 0), A.uv(biom, pole_bok, 1, 1),
                                         A.uv(biom, pole_bok, 0, 1)], od=(0, 0, (y0 + y1) / 2))
        if gorna:
            def uvp(x, z):
                return A.uv(biom, "plyta", 0.5 + x / 3.4, 0.5 + z / 3.4)
            for j in range(8):
                (x0, z0), (x1, z1) = rogi[j], rogi[(j + 1) % 8]
                if r_wew:
                    f = r_wew / R
                    q = [(x0, z0), (x1, z1), (x1 * f, z1 * f), (x0 * f, z0 * f)]
                else:
                    q = [(x0, z0), (x1, z1), (0, 0)]
                s.sciana([B((x, y1, z)) for x, z in q], [uvp(x, z) for x, z in q], gora=(0, 0, 1))
    osmiokat(1.6, 0.0, 0.26, "fryz2", True, 1.24)
    osmiokat(1.24, 0.26, 0.52, "fryz", True)
    for i, (a, rad, sk) in enumerate([(0.9, 1.75, 0.2), (2.5, 1.85, 0.16), (4.0, 1.8, 0.22), (5.6, 1.7, 0.14)]):
        x, z = rad * math.cos(a), rad * math.sin(a)
        bryla(s, (x, sk * 0.55, z), sk, sk * 0.65, 4, 2, 200 + i, biom, "kamien", losowo=0.12)
    # dwa kamienne „strażniki” ze złotym czubkiem po bokach przodu (ramują jajo w kadrze scenki)
    for a in (math.radians(45), math.radians(135)):
        c = Vector((1.08 * math.cos(a), 0.52, 1.08 * math.sin(a)))
        pr = Vector((math.cos(a), 0, math.sin(a)))
        bk = Vector((-math.sin(a), 0, math.cos(a)))
        hw, hh = 0.15, 0.34
        rogi = [c + pr * sx_ * hw + bk * sz_ * hw for sx_, sz_ in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        gorne = [p + Vector((0, hh, 0)) for p in rogi]
        sr = c + Vector((0, hh / 2, 0))
        for j in range(4):
            q = [rogi[j], rogi[(j + 1) % 4], gorne[(j + 1) % 4], gorne[j]]
            s.sciana([B(p) for p in q], [A.uv(biom, "fryz2", 0, 0), A.uv(biom, "fryz2", 0.25, 0), A.uv(biom, "fryz2", 0.25, 1),
                                         A.uv(biom, "fryz2", 0, 1)], od=B(sr))
        szpic = c + Vector((0, hh + 0.2, 0))
        for j in range(4):
            q = [gorne[j], gorne[(j + 1) % 4], szpic]
            s.sciana([B(p) for p in q], [A.uv(biom, "precik", 0.1, 0.1), A.uv(biom, "precik", 0.9, 0.1),
                                         A.uv(biom, "precik", 0.5, 0.9)], od=B(sr))
    ob["StoneBase"] = s.obiekt("StoneBase", [m["ozdoby"]])
    # --- mchowe gniazdo (MossNest)
    s = Siatka()
    profil = [(0.0, 0.5), (0.4, 0.52), (0.55, 0.62), (0.66, 0.70), (0.8, 0.62), (0.92, 0.55), (1.0, 0.515)]
    kopczyk(s, profil, 20, 1.08, biom, "mech", 9, 0.035, 0.05)
    ob["MossNest"] = s.obiekt("MossNest", [m["ozdoby"]])
    # --- wielkie liście (BigLeaves): wachlarz z tyłu i z boków
    s = Siatka()
    for i, (a, dl, szer, nach) in enumerate([(-2.2, 2.1, 0.95, 0.55), (-1.55, 2.4, 1.0, 0.35), (-0.95, 2.15, 0.95, 0.5),
                                              (-2.85, 1.7, 0.8, 0.75), (-0.3, 1.6, 0.8, 0.8), (2.6, 1.3, 0.7, 1.0),
                                              (0.55, 1.25, 0.65, 1.05)]):
        # a: kąt w płaszczyźnie (0 = +X, −π/2 = tył −Z), nach: odchylenie od pionu
        kier = Vector((math.cos(a) * math.sin(nach), math.cos(nach), math.sin(a) * math.sin(nach))).normalized()
        nas = Vector((math.cos(a) * 0.95, 0.5, math.sin(a) * 0.95))
        bok = Vector((-math.sin(a), 0, math.cos(a)))
        # ogonek
        rura(s, [tuple(nas - kier * 0.05), tuple(nas + kier * 0.3)], [0.035, 0.03], 5, biom, "liana", zamknij=(True, False))
        lisc(s, nas + kier * 0.28, kier, bok, dl, szer, biom, "lisc",
             opad=0.32 + 0.05 * i % 3, zgiecie=0.22)
    ob["BigLeaves"] = s.obiekt("BigLeaves", [m["ozdoby"]])
    # --- liany (Vines) z listkami: oplatają cokół i wspinają się z tyłu
    s = Siatka()
    for i, (a0, obr, h0, h1, rad) in enumerate([(-0.4, 1.4, 0.05, 0.55, 1.3), (2.2, 1.2, 0.05, 0.5, 1.33), (3.6, -1.1, 0.28, 0.3, 1.4)]):
        pts, prom = [], []
        for k in range(10):
            t = k / 9
            a = a0 + obr * t
            rr_ = rad + 0.05 * math.sin(t * 9)
            y = h0 + (h1 - h0) * t + 0.05 * math.sin(t * 13 + i)
            if y < 0.26:
                rr_ = max(rr_, 1.62)
            elif y < 0.52:
                rr_ = max(rr_, 1.27) if rad > 1.1 else rr_
            pts.append((rr_ * math.cos(a), y, rr_ * math.sin(a)))
            prom.append(0.04)
        rura(s, pts, prom, 5, biom, "liana", skret=0.3)
        for k in range(1, 9, 2):
            p = Vector(pts[k])
            na_zew = Vector((p.x, 0, p.z)).normalized()
            kier = (na_zew + Vector((0, 0.8, 0))).normalized()
            bok = Vector((0, 1, 0)).cross(na_zew).normalized()
            lisc(s, p, kier, bok, 0.22, 0.13, biom, "listek", opad=0.6, zgiecie=0.2)
    # liana wspinająca się po tylnym liściu
    pts = [(math.cos(-1.55) * 0.95 + 0.05 * math.sin(k), 0.5 + k * 0.17, math.sin(-1.55) * 0.95 - 0.05 * k) for k in range(8)]
    rura(s, pts, [0.03] * 8, 5, biom, "liana", skret=0.4)
    ob["Vines"] = s.obiekt("Vines", [m["ozdoby"]])
    # --- kwiaty (Flowers): hibiskusy z precikiem
    s = Siatka()
    for (x, y, z, rad, nach) in [(1.05, 0.58, 0.7, 0.3, (0.4, 1, 0.5)), (-1.2, 0.62, 0.45, 0.27, (-0.5, 1, 0.4)),
                                 (-0.55, 0.62, -0.75, 0.26, (0, 1, -0.3)), (1.55, 0.3, -0.35, 0.22, (0.8, 0.6, 0))]:
        os_ = Vector(nach).normalized()
        n1, n2 = ramka(os_)
        c = Vector((x, y, z))
        for i in range(5):
            a = 2 * math.pi * i / 5
            rad_k = (n1 * math.cos(a) + n2 * math.sin(a))
            kier = (rad_k * 0.85 + os_ * 0.5).normalized()
            bok = os_.cross(rad_k).normalized()
            lisc(s, c, kier, bok, rad, rad * 0.9, biom, "platek", opad=-0.25, zgiecie=0.25)
        rura(s, [tuple(c), tuple(c + os_ * rad * 0.9)], [0.022, 0.012], 5, biom, "precik")
        bryla(s, tuple(c + os_ * rad * 0.95), 0.03, 0.03, 5, 3, 7, biom, "precik")
    ob["Flowers"] = s.obiekt("Flowers", [m["ozdoby"]])
    # --- bursztynowe kryształy (Crystals) i odłamki (Shards)
    s = Siatka()
    for (x, y0, z, ile) in [(1.25, 0.26, -0.6, 4), (-1.3, 0.26, 0.85, 3), (-0.3, 0.5, -1.0, 2)]:
        for i in range(ile):
            a = r.uniform(0, 6.28)
            kier = Vector((math.cos(a) * 0.45 + x * 0.2, 1, math.sin(a) * 0.45 + z * 0.2)).normalized()
            krysztal(s, Vector((x + r.uniform(-0.07, 0.07), y0, z + r.uniform(-0.07, 0.07))), kier,
                     r.uniform(0.07, 0.12), r.uniform(0.25, 0.5) * (1.3 if i == 0 else 1.0), 6, obrot=r.uniform(0, 1))
    ob["Crystals"] = s.obiekt("Crystals", [m["neon"]])
    s = Siatka()
    for i in range(6):
        a = r.uniform(0, 6.28)
        rad = r.uniform(1.3, 1.5)
        krysztal(s, Vector((rad * math.cos(a), 0.26, rad * math.sin(a))), Vector((r.uniform(-0.6, 0.6), 1, r.uniform(-0.6, 0.6))),
                 0.03, r.uniform(0.05, 0.1), 4, obrot=a)
    ob["Shards"] = s.obiekt("Shards", [m["neon"]])
    return ob


# ----------------------------------------------------------------------------------------------- dane biomów
BIOMY = {
    "bagno": dict(budowa=bagno, podzial=dict(ziarno=7), neon="9BFF4F", trzon="D7D2B8", kapelusz="7A3E9E",
                  blask="9BFF4F", tlo="DCE8D2"),
    "dzungla": dict(budowa=dzungla, podzial=dict(ziarno=19, przod=0.86 * math.pi), neon="FF8C1A", trzon="D7D2B8",
                    kapelusz="7A3E9E", blask="FF5FA8", tlo="E8F0D8"),
}


def zbuduj(biom):
    d = BIOMY[biom]
    tx = os.path.join(TU, "tekstury")
    m = {
        "jajo": mat_obraz("Jajo_" + biom, os.path.join(tx, biom + "_jajo_kolor.png"), 0.6),
        "ozdoby": mat_obraz("Ozdoby_" + biom, os.path.join(tx, biom + "_ozdoby.png"), 0.85),
        "neon": mat_kolor("Neon_" + biom, d["neon"]),
        "trzon": mat_kolor("Trzon_" + biom, d["trzon"]),
        "kapelusz": mat_kolor("Kapelusz_" + biom, d["kapelusz"]),
    }
    ob = jajo_i_skorupy(K.Podzial(**d["podzial"]), m["jajo"])
    ob.update(d["budowa"](m))
    for o in ob.values():
        o.data.name = o.name
    return ob, m


def trojkaty(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def wyczysc():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)


def zaznacz(obs):
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]


def eksport(ob, wyj, biom):
    os.makedirs(wyj, exist_ok=True)
    obs = list(ob.values())
    for o in obs:   # początek obiektu w środku jego bryły (Roblox i tak liczy środek ramki)
        zaznacz([o])
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    zaznacz(obs)
    glb = os.path.join(wyj, "jajko_%s.glb" % biom)
    bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=True, export_animations=False, export_materials="EXPORT",
                              export_image_format="AUTO")
    fbx = os.path.join(wyj, "jajko_%s.fbx" % biom)
    bpy.ops.export_scene.fbx(filepath=fbx, use_selection=True, object_types={"MESH"}, use_mesh_modifiers=True,
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", axis_forward="-Z",
                             axis_up="Y", add_leaf_bones=False, bake_anim=False, path_mode="COPY", embed_textures=True)
    stat = {}
    for o in obs:
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        mn = [min(p[i] for p in bb) for i in range(3)]
        mx = [max(p[i] for p in bb) for i in range(3)]
        # Blender (x, y, z) -> Roblox (x, z, -y): rozmiar (x, z, y)
        stat[o.name] = {"trojkaty": trojkaty(o), "rozmiar_m": [round(mx[0] - mn[0], 3), round(mx[2] - mn[2], 3), round(mx[1] - mn[1], 3)],
                        "srodek_m": [round((mx[0] + mn[0]) / 2, 3), round((mx[2] + mn[2]) / 2, 3), round(-(mx[1] + mn[1]) / 2, 3)],
                        "material": o.data.materials[0].name if o.data.materials else ""}
    wsz = [o.matrix_world @ Vector(c) for o in obs for c in o.bound_box]
    calosc = {"trojkaty_razem": sum(v["trojkaty"] for v in stat.values()),
              "trojkaty_w_spoczynku": sum(v["trojkaty"] for k, v in stat.items() if not k.startswith("Shell")),
              "rozmiar_m": [round(max(p.x for p in wsz) - min(p.x for p in wsz), 3), round(max(p.z for p in wsz) - min(p.z for p in wsz), 3),
                            round(max(p.y for p in wsz) - min(p.y for p in wsz), 3)],
              "najnizszy_y_m": round(min(p.z for p in wsz), 4)}
    with open(os.path.join(wyj, "jajko_%s_statystyki.json" % biom), "w", encoding="utf-8") as f:
        json.dump({"biom": biom, "calosc": calosc, "czesci": stat}, f, ensure_ascii=False, indent=1)
    log("eksport", biom, calosc)
    return calosc


# ----------------------------------------------------------------------------------------------- render
def scena_renderu(tlo_hex):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    ee = sc.eevee
    for atr, wart in (("taa_render_samples", 24), ("use_shadows", True), ("use_gtao", True), ("use_raytracing", False),
                      ("use_bloom", True)):
        if hasattr(ee, atr):
            try:
                setattr(ee, atr, wart)
            except Exception:
                pass
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 92
    sw = bpy.data.worlds.new("Swiat")
    sw.use_nodes = True
    sw.node_tree.nodes["Background"].inputs[0].default_value = (*lin(tlo_hex), 1.0)
    sw.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    sc.world = sw
    for nazwa, kier, energia in (("Klucz", (0.7, -1.0, 1.25), 3.2), ("Wypelnienie", (-1.0, -0.4, 0.6), 1.0),
                                 ("Kontra", (-0.3, 1.0, 0.9), 2.0)):
        l_ = bpy.data.lights.new(nazwa, "SUN")
        l_.energy = energia
        l_.angle = math.radians(8)
        o = bpy.data.objects.new(nazwa, l_)
        sc.collection.objects.link(o)
        o.rotation_euler = (-Vector(kier)).to_track_quat("-Z", "Y").to_euler()
    me = bpy.data.meshes.new("_Podloze")
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=40, segments=48)
    bm.to_mesh(me)
    bm.free()
    pod = bpy.data.objects.new("_Podloze", me)
    me.materials.append(mat_kolor("_Podloze", "6F7C5E", 0.95))
    pod.location.z = -0.004
    sc.collection.objects.link(pod)
    return sc


def obrys(obs, grub=0.014):
    m = bpy.data.materials.new("_Obrys")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    wy = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin("0F1A14"), 1.0)
    nt.links.new(em.outputs[0], wy.inputs["Surface"])
    m.use_backface_culling = True
    for o in obs:
        o.data.materials.append(m)
        md = o.modifiers.new("_Obrys", "SOLIDIFY")
        md.thickness, md.offset, md.use_even_offset = grub, 1.0, True
        md.use_flip_normals, md.use_rim = True, False
        md.material_offset = len(o.data.materials) - 1


def kamera(sc, kat_deg, cel, odl, wys_deg=14.0, orto=None, lens=50):
    cam = bpy.data.objects.get("_Kamera")
    if cam is None:
        cam = bpy.data.objects.new("_Kamera", bpy.data.cameras.new("_Kamera"))
        sc.collection.objects.link(cam)
    a, e = math.radians(kat_deg), math.radians(wys_deg)
    # kat 0 = z przodu (Roblox +Z = Blender −Y)
    d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
    cam.location = Vector(cel) + d * odl
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    if orto:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = orto
    else:
        cam.data.type = "PERSP"
        cam.data.lens = lens
    cam.data.clip_end = 500
    sc.camera = cam


def render(sc, plik, w=720, h=800):
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = plik
    bpy.ops.render.render(write_still=True)
    log("render", os.path.basename(plik))


def blaski_podgladu(m, d, biom):
    tx = os.path.join(TU, "tekstury")
    dodaj_blask(m["jajo"], d["blask"], 1.6, os.path.join(tx, biom + "_jajo_blask.png"))
    dodaj_blask(m["neon"], d["neon"], 0.7)


def rdzen_i_slup(kolor_hex, przes=(0, 0, 0)):
    """Do ujęcia „wyklucie”: świecący rdzeń i słup światła jak w kliencie Pawła (rdzeń 1,59, słup od 1,66)."""
    m = bpy.data.materials.new("_Rdzen")
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    wy = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*lin(kolor_hex), 1.0)
    em.inputs["Strength"].default_value = 1.6
    nt.links.new(em.outputs[0], wy.inputs["Surface"])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.675, location=(przes[0], przes[1], K.RDZEN_Y))
    r = bpy.context.active_object
    r.scale.z = 0.5
    r.data.materials.append(m)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.4, depth=7.0, location=(przes[0], przes[1], 1.66 + 3.5))
    s = bpy.context.active_object
    s.data.materials.append(m)
    return [r, s]


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    biom = argv[argv.index("--biom") + 1] if "--biom" in argv else None
    wyj = argv[argv.index("--wyj") + 1] if "--wyj" in argv else os.path.join(TU, "modele")
    klatki = argv[argv.index("--klatki") + 1] if "--klatki" in argv else None
    wyczysc()
    if "--zestawienie" in argv:
        zestawienie(klatki)
        return
    ob, m = zbuduj(biom)
    calosc = eksport(ob, wyj, biom)
    if not klatki:
        return
    os.makedirs(klatki, exist_ok=True)
    d = BIOMY[biom]
    sc = scena_renderu(d["tlo"])
    blaski_podgladu(m, d, biom)
    widoczne = [o for n, o in ob.items() if not n.startswith("Shell")]
    for n, o in ob.items():
        if n.startswith("Shell"):
            o.hide_render = True
    obrys(list(ob.values()))
    cel = (0, 0, 1.4)
    for i, kat in enumerate((0, 90, 180, 270)):
        kamera(sc, kat, cel, 8.3, 12)
        render(sc, os.path.join(klatki, "%s_%d.jpg" % (biom, i)))
    # zbliżenie skorupy z przodu
    kamera(sc, 20, (0, 0, 1.7), 5.8, 8)
    render(sc, os.path.join(klatki, "%s_zblizenie.jpg" % biom))
    # wyklucie: jajo znika, kawałki skorupy odsunięte, rdzeń i słup
    ob["Egg"].hide_render = True
    for n, (dx, dz, rot) in {"ShellBottom": (0, 0, 0), "ShellTopRight": (0.9, 0.9, -0.6), "ShellTopLeft": (-0.7, 0.5, 0.45)}.items():
        o = ob[n]
        o.hide_render = False
        o.location.x += dx
        o.location.z += dz
        o.rotation_euler.y += rot
    rdzen_i_slup(d["blask"])
    kamera(sc, 15, (0, 0, 1.9), 9.0, 10)
    render(sc, os.path.join(klatki, "%s_wyklucie.jpg" % biom))
    with open(os.path.join(klatki, "%s_render.json" % biom), "w", encoding="utf-8") as f:
        json.dump(calosc, f)


def zestawienie(klatki):
    """Bagno, Dżungla i przybliżenie leśnego (tekstura Pawła na naszej bryle jaja) w jednej skali, z przodu,
    rzut prostokątny; obok sylwetka gracza (5,3 studa = 3,53 m pliku przy skali ×1,5)."""
    sc = scena_renderu("E4E8DC")
    wszystkie = []
    for biom, dx in (("bagno", -4.2), ("dzungla", 4.2)):
        ob, m = zbuduj(biom)
        blaski_podgladu(m, BIOMY[biom], biom)
        for n, o in ob.items():
            if n.startswith("Shell"):
                o.hide_render = True
            o.location.x += dx
        wszystkie += list(ob.values())
    # leśne: sama bryła jaja z teksturą Pawła (modelu GLB nie ma w repo)
    las = os.path.join(REPO, "assets", "processed", "JajoLesne")
    mj = mat_obraz("Jajo_las", os.path.join(las, "JajoLesneKolor.png"), 0.6)
    dodaj_blask(mj, "53E89A", 2.2, os.path.join(las, "JajoLesneBlask.png"))
    pod = K.Podzial(ziarno=3)
    s = Siatka()
    for rz in (pod.rzedy_dol(), pod.rzedy_gora(True), pod.rzedy_gora(False)):
        powierzchnia(s, rz)
    e = s.obiekt("Egg_las", [mj], przelicz=True)
    wszystkie.append(e)
    # sylwetka gracza
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.33, depth=3.53 - 0.66, location=(7.6, 0, (3.53 - 0.66) / 2 + 0.0))
    g = bpy.context.active_object
    g.data.materials.append(mat_kolor("_Gracz", "8A93A6"))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.33, location=(7.6, 0, 3.53 - 0.33))
    g2 = bpy.context.active_object
    g2.data.materials.append(mat_kolor("_Gracz2", "8A93A6"))
    obrys(wszystkie)
    kamera(sc, 0, (1.7, 0, 1.75), 30, 4, orto=17.5)
    render(sc, os.path.join(klatki, "zestawienie.jpg"), 1600, 820)


main()
