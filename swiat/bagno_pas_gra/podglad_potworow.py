#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd potworów Bagna BEZ Blendera i bez Studio: rig z klocków (dane walki) narysowany w Pillow.

    python -B swiat/bagno_pas_gra/podglad_potworow.py                       # 5 potworów → swiat/bagno_pas_gra/podglad/
    python -B swiat/bagno_pas_gra/podglad_potworow.py --klucz rechotek --klipy atak,umiejetnosc --wyj <folder>
    python -B swiat/bagno_pas_gra/podglad_potworow.py --modul swiat/postacie/rechotek.py --wyj <folder>

Źródło: --klucz = swiat/test_walki2/dane/<klucz>.json (to, co trafia do Studio: szablon i klipy); --modul = moduł
modelu (rig liczony na nowo, klipy próbkowane liniowo — do pracy nad modelem). Wynik: <klucz>_plansza.jpg (sześć
widoków: 3/4 przód, przód, bok, tył, z góry, z daleka) i <klucz>_<klip>.jpg (8 klatek klipu), a bez --klucz/--modul
także szereg.jpg — pięć potworów w jednej skali obok sylwetki gracza (5,7 st), na tle w kolorze kępy Bagna (czy
sylwetka jest czytelna z daleka). Rzut prostokątny, bufor głębi, proste cieniowanie; Neon jaśniej.
TO NIE JEST WYGLĄD Z ROBLOX (bez materiałów, cieni, poświaty i mgły) — tylko kształt, kolory i proporcje.
"""
import argparse
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki2")):
    if s not in sys.path:
        sys.path.insert(0, s)

from PIL import Image, ImageDraw  # noqa: E402

from geometria import Rig, punkt  # noqa: E402

KLUCZE = ["rechotek", "bulgotnik", "klodoklap", "ropucha_z_chatka", "straznik_topieli"]
TLO = (122, 136, 96)
WZROST_GRACZA = 5.7


def _box(hx, hy, hz):
    v = [(sx * hx, sy * hy, sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    # indeksy: (sx,sy,sz) -> ((sx>0)*4 + (sy>0)*2 + (sz>0))
    f = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    return v, f


def _walec_x(L, ry, rz, n=10):
    v = []
    for s in (-1, 1):
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            v.append((s * L / 2, ry * math.cos(a), rz * math.sin(a)))
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        f.append((i, j, n + j, n + i))
    return v, f


def _kula(rx, ry, rz, nu=10, nv=6):
    v = [(0, ry, 0)]
    for j in range(1, nv):
        b = math.pi * j / nv
        for i in range(nu):
            a = 2 * math.pi * i / nu
            v.append((rx * math.sin(b) * math.cos(a), ry * math.cos(b), rz * math.sin(b) * math.sin(a)))
    v.append((0, -ry, 0))
    f = []
    for i in range(nu):
        f.append((0, 1 + (i + 1) % nu, 1 + i))
    for j in range(nv - 2):
        for i in range(nu):
            a0 = 1 + j * nu + i
            a1 = 1 + j * nu + (i + 1) % nu
            f.append((a0, a1, a1 + nu, a0 + nu))
    last = len(v) - 1
    base = 1 + (nv - 2) * nu
    for i in range(nu):
        f.append((last, base + i, base + (i + 1) % nu))
    return v, f


def _klin(hx, hy, hz):
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, hz), (hx, hy, hz)]
    f = [(0, 1, 2, 3), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2), (0, 4, 5, 1)]
    return v, f


def _naroznik(hx, hy, hz):
    v = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (hx, hy, -hz)]
    f = [(0, 1, 2, 3), (1, 4, 2), (0, 4, 1), (3, 2, 4), (0, 3, 4)]
    return v, f


def siatka(c):
    ks, s, sm = c[1], c[9:12], c[15] if len(c) > 15 else ""
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    if ks == 0 and sm == "Sphere":
        return _kula(hx, hy, hz)
    if ks == 0 and sm == "Cylinder":
        return _walec_x(s[0], hy, hz)
    if ks == 0:
        return _box(hx, hy, hz)
    if ks == 1:
        d = min(s) / 2
        return _kula(d, d, d)
    if ks == 2:
        return _walec_x(s[0], min(s[1], s[2]) / 2, min(s[1], s[2]) / 2)
    if ks == 3:
        return _klin(hx, hy, hz)
    return _naroznik(hx, hy, hz)


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(v):
    n = math.sqrt(_dot(v, v)) or 1.0
    return (v[0] / n, v[1] / n, v[2] / n)


def kamera(yaw, pitch):
    """Kamera: yaw 0 = patrzy na przód postaci (postać patrzy w −Z, kamera stoi po stronie −Z)."""
    y, p = math.radians(yaw), math.radians(pitch)
    # kierunek od kamery do sceny
    fwd = (math.sin(y) * math.cos(p), -math.sin(p), math.cos(y) * math.cos(p))
    right = _norm(_cross(fwd, (0, 1, 0)))
    up = _cross(right, fwd)
    return fwd, right, up


def trojkaty(r, d, pozy):
    out = []
    for c in d["czesci"]:
        if len(c) > 16 and c[16]:
            pass
        cfc = r.czesc_cf(c, pozy)
        v, f = siatka(c)
        w = [punkt(cfc, q) for q in v]
        col = c[12]
        mat = d["materialy"][c[13]][0] if d.get("materialy") else ""
        tr = 0.0
        out.append((w, f, col, mat))
    return out


def rysuj(img, bryly, cam, sr, skala, cx, cy, swiatlo=(-0.4, 0.8, -0.45)):
    import numpy as np
    fwd, right, up = cam
    L = _norm(swiatlo)
    W, H = img.size
    zbuf = np.full((H, W), 1e9)
    kol = np.array(img, dtype=np.float64)
    for w, f, col, mat in bryly:
        rgb = np.array([int(col[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)
        srb = tuple(sum(q[i] for q in w) / len(w) for i in range(3))
        P = [(cx + _dot(_sub(q, sr), right) * skala, cy - _dot(_sub(q, sr), up) * skala, _dot(_sub(q, sr), fwd))
             for q in w]
        for fc in f:
            pts = [w[i] for i in fc]
            n = _norm(_cross(_sub(pts[1], pts[0]), _sub(pts[2], pts[0])))
            if _dot(n, n) < 0.5:
                continue
            sf = tuple(sum(q[i] for q in pts) / len(pts) for i in range(3))
            if _dot(n, _sub(sf, srb)) < 0:
                n = (-n[0], -n[1], -n[2])
            if _dot(n, fwd) >= 0:
                continue
            k = 1.2 if mat == "Neon" else 0.5 + 0.55 * max(0.0, _dot(n, L))
            c = np.clip(rgb * k, 0, 255)
            for j in range(1, len(fc) - 1):
                a, b, d = P[fc[0]], P[fc[j]], P[fc[j + 1]]
                x0, x1 = int(max(0, min(a[0], b[0], d[0]))), int(min(W - 1, max(a[0], b[0], d[0]) + 1))
                y0, y1 = int(max(0, min(a[1], b[1], d[1]))), int(min(H - 1, max(a[1], b[1], d[1]) + 1))
                if x1 < x0 or y1 < y0:
                    continue
                xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                den = (b[1] - d[1]) * (a[0] - d[0]) + (d[0] - b[0]) * (a[1] - d[1])
                if abs(den) < 1e-9:
                    continue
                l1 = ((b[1] - d[1]) * (xs - d[0]) + (d[0] - b[0]) * (ys - d[1])) / den
                l2 = ((d[1] - a[1]) * (xs - d[0]) + (a[0] - d[0]) * (ys - d[1])) / den
                l3 = 1 - l1 - l2
                m = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
                if not m.any():
                    continue
                z = l1 * a[2] + l2 * b[2] + l3 * d[2]
                sub = zbuf[y0:y1 + 1, x0:x1 + 1]
                m = m & (z < sub)
                sub[m] = z[m]
                kol[y0:y1 + 1, x0:x1 + 1][m] = c
    img.paste(Image.fromarray(kol.astype("uint8")))


def ziemia(img, cam, sr, skala, cx, cy, R=6.0):
    fwd, right, up = cam
    dr = ImageDraw.Draw(img)
    for i in range(-int(R), int(R) + 1, 1):
        for a, b in (((i, 0, -R), (i, 0, R)), ((-R, 0, i), (R, 0, i))):
            p = [(cx + _dot(_sub(q, sr), right) * skala, cy - _dot(_sub(q, sr), up) * skala) for q in (a, b)]
            dr.line(p, fill=(150, 160, 140), width=1)


def wymiary(r, d, pozy):
    mn, mx = [1e9] * 3, [-1e9] * 3
    for w, f, col, mat in trojkaty(r, d, pozy):
        for q in w:
            for i in range(3):
                mn[i] = min(mn[i], q[i])
                mx[i] = max(mx[i], q[i])
    return mn, mx


def dane_aktora(klucz=None, modul=None):
    if modul:
        from swiat.postacie.roblox_postac import postacie_z_modulu
        from swiat.postacie.biblioteka.roblox_klocki import rig, probki_liniowe
        p = postacie_z_modulu(modul)[0]
        bledy, _ = p.sprawdz()
        if bledy:
            sys.exit("%s: %s" % (modul, bledy))
        return p.id, rig(p, probki_liniowe(p))
    with open(os.path.join(REPO, "swiat", "test_walki2", "dane", klucz + ".json"), encoding="utf-8") as f:
        return klucz, json.load(f)


def plansza(nazwa, d, wyj, px=400, yaw=35):
    r = Rig(d)
    pozy = r.pozy()
    mn, mx = wymiary(r, d, pozy)
    H = max(mx[1], mx[0] - mn[0], mx[2] - mn[2]) * 1.15 + 1.0
    skala = px / H
    sr = ((mn[0] + mx[0]) / 2, mx[1] / 2, (mn[2] + mx[2]) / 2)
    widoki = [("3/4 przód", yaw, 18), ("przód", 0, 5), ("bok", -90, 5), ("tył 3/4", 180 + 35, 20),
              ("z góry", 20, 70), ("z daleka (1/4)", yaw, 25)]
    img = Image.new("RGB", (px * 3, px * 2), TLO)
    for i, (nm, yw, pitch) in enumerate(widoki):
        cam = kamera(yw, pitch)
        sub = Image.new("RGB", (px, px), TLO if i != 5 else (126, 140, 62))
        sk = skala * (0.25 if i == 5 else 1.0)
        ziemia(sub, cam, sr, sk, px // 2, px // 2, R=12 if i == 5 else 6)
        rysuj(sub, trojkaty(r, d, pozy), cam, sr, sk, px // 2, px // 2)
        ImageDraw.Draw(sub).text((6, 6), nm, fill=(0, 0, 0))
        img.paste(sub, (px * (i % 3), px * (i // 3)))
    img.save(os.path.join(wyj, nazwa + "_plansza.jpg"), quality=86)
    return "%s: %d brył, %d kości, wys. %.2f, szer. %.2f, dł. %.2f" % (
        nazwa, len(d["czesci"]), len(d["kosci"]), mx[1], mx[0] - mn[0], mx[2] - mn[2])


def klip(nazwa, d, kn, wyj, n=8, q=150):
    r = Rig(d)
    kl = r.klipy[kn]
    cam = kamera(-70, 12) if kn in ("umiejetnosc", "skok", "atak", "upadek") else kamera(0 if kn == "unik" else 35, 15)
    bmn, bmx = [1e9] * 3, [-1e9] * 3
    for f in range(0, kl["dl"] + 1, max(1, kl["dl"] // 12)):
        m1, m2 = wymiary(r, d, r.pozy(r.transformy(kn, f)))
        for i in range(3):
            bmn[i], bmx[i] = min(bmn[i], m1[i]), max(bmx[i], m2[i])
    sk = q / (max(bmx[1], bmx[0] - bmn[0], bmx[2] - bmn[2]) * 1.1 + 0.5)
    srk = ((bmn[0] + bmx[0]) / 2, bmx[1] / 2, (bmn[2] + bmx[2]) / 2)
    img = Image.new("RGB", (q * n, q), TLO)
    for j in range(n):
        f = round(j * kl["dl"] / n) if kl["petla"] else round(j * kl["dl"] / (n - 1))
        sub = Image.new("RGB", (q, q), TLO)
        ziemia(sub, cam, srk, sk, q // 2, q // 2, R=8)
        rysuj(sub, trojkaty(r, d, r.pozy(r.transformy(kn, f))), cam, srk, sk, q // 2, q // 2)
        ImageDraw.Draw(sub).text((4, 4), "%s %d" % (kn, f), fill=(0, 0, 0))
        img.paste(sub, (q * j, 0))
    img.save(os.path.join(wyj, "%s_%s.jpg" % (nazwa, kn)), quality=84)


def szereg(dane, wyj, wys=520):
    """Pięć potworów w jednej skali (3/4 z przodu) i gracz jako szary słupek 5,7 st."""
    najwyzszy = max(wymiary(Rig(d), d, Rig(d).pozy())[1][1] for _, d in dane)
    sk = (wys - 60) / max(najwyzszy, WZROST_GRACZA)
    kafle = []
    for nazwa, d in dane:
        r = Rig(d)
        mn, mx = wymiary(r, d, r.pozy())
        szer = int(max(mx[0] - mn[0], mx[2] - mn[2]) * sk * 1.05) + 40
        sub = Image.new("RGB", (szer, wys), (126, 140, 62))
        sr = ((mn[0] + mx[0]) / 2, 0, (mn[2] + mx[2]) / 2)
        rysuj(sub, trojkaty(r, d, r.pozy()), kamera(35, 8), sr, sk, szer // 2, wys - 30)
        ImageDraw.Draw(sub).text((6, 6), nazwa, fill=(0, 0, 0))
        kafle.append(sub)
    g = Image.new("RGB", (70, wys), (126, 140, 62))
    ImageDraw.Draw(g).rectangle((20, wys - 30 - WZROST_GRACZA * sk, 50, wys - 30), fill=(90, 90, 100))
    ImageDraw.Draw(g).text((6, 6), "gracz", fill=(0, 0, 0))
    kafle.insert(0, g)
    img = Image.new("RGB", (sum(k.size[0] for k in kafle), wys), (126, 140, 62))
    x = 0
    for k in kafle:
        img.paste(k, (x, 0))
        x += k.size[0]
    if img.size[0] > 1280:
        img = img.resize((1280, int(wys * 1280 / img.size[0])))
    img.save(os.path.join(wyj, "szereg.jpg"), quality=86)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Podgląd potworów Bagna bez Blendera i Studio")
    ap.add_argument("--klucz", default="", help="aktor z swiat/test_walki2/dane/<klucz>.json")
    ap.add_argument("--modul", default="", help="moduł modelu swiat/postacie/<x>.py")
    ap.add_argument("--klipy", default="", help="klipy do arkuszy klatek (po przecinku); domyślnie bez")
    ap.add_argument("--wyj", default=os.path.join(TU, "podglad"))
    a = ap.parse_args()
    os.makedirs(a.wyj, exist_ok=True)
    if a.klucz or a.modul:
        lista = [dane_aktora(a.klucz or None, a.modul or None)]
    else:
        lista = [dane_aktora(k) for k in KLUCZE]
    for nazwa, d in lista:
        print(plansza(nazwa, d, a.wyj))
        for kn in [k for k in a.klipy.split(",") if k]:
            klip(nazwa, d, kn, a.wyj)
    if not (a.klucz or a.modul):
        szereg(lista, a.wyj)
    print("zapisano do", os.path.relpath(a.wyj, REPO) if a.wyj.startswith(REPO) else a.wyj)


if __name__ == "__main__":
    main()
