# -*- coding: utf-8 -*-
"""Tekstury jajek biomów malowane skryptem (bez generatorów): dla każdego biomu
  tekstury/<biom>_jajo_kolor.png  2048 × 1024 — skorupa (płytki z ciemną kreską, cień dwutonowy z rastrem,
                                   świecące pęknięcia; pęknięcia podziału skorupy dokładnie na liniach z ksztalt.py),
  tekstury/<biom>_jajo_blask.png  2048 × 1024 — maska blasku (biel = świeci; kolor daje EmissiveTint w Studio),
  tekstury/<biom>_ozdoby.png      1024 × 1024 — atlas ozdób (pola z atlas.py).
Styl jak tekstura leśnego jaja Pawła (assets/processed/JajoLesne/JajoLesneKolor.png).

    python -B swiat/jajka_biomow/tekstury.py [bagno|dzungla]
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import cKDTree

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import atlas as A  # noqa: E402
import ksztalt as K  # noqa: E402

W, H = 2048, 1024
PX_NA_JEDN = (K.V_MAX * H) / math.pi   # piksele na jednostkę cięciwy kuli (≈ na radian)


def hx(s):
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32) / 255.0


BIOMY = {
    "bagno": dict(
        ziarno=311, siatka="losowa", komorek=62,
        plyty=[("5E7A3A", 3.0), ("4E6A31", 3.0), ("6C8A3A", 1.6), ("5D4A7A", 1.3), ("715C8E", 0.8), ("3F5C3A", 1.5)],
        cien_ton="2A2236", swiatlo_ton="C6E07A", kreska="17141C", blask_rdzen="F4FFD2", blask="9BFF4F",
        swiecace=0.30, cetki=True, zloto=None,
        wnetrze="CDE7A2", podzial=dict(ziarno=7),
    ),
    "dzungla": dict(
        ziarno=523, siatka="luski", komorek=0,
        plyty=[("3DAA47", 3.0), ("2E9140", 2.5), ("56C251", 2.0), ("2AA89A", 1.0), ("E2A92C", 0.55)],
        cien_ton="123A3A", swiatlo_ton="D9F58A", kreska="10231A", blask_rdzen="FFE6F3", blask="FF5FA8",
        swiecace=0.22, cetki=False, zloto="F2B530",
        wnetrze="FFE7B8", podzial=dict(ziarno=19, przod=0.86 * math.pi),
    ),
}


# ----------------------------------------------------------------------------------------------- pomocnicze
def szum(ksztalt, komorki, ziarno, oktawy=3):
    """Gładki szum (okresowy), wartości ok. −1..1."""
    r = np.random.default_rng(ziarno)
    h, w = ksztalt
    wynik = np.zeros(ksztalt, np.float32)
    amp = 1.0
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    for o in range(oktawy):
        ch, cw = komorki[0] * 2 ** o, komorki[1] * 2 ** o
        g = r.standard_normal((ch, cw)).astype(np.float32)
        wynik += amp * ndimage.map_coordinates(g, [yy / h * ch - 0.5, xx / w * cw - 0.5], order=3, mode="grid-wrap")
        amp *= 0.5
    return wynik / 1.6


def gladko(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def mieszaj(baza, kolor, waga):
    w = np.asarray(waga, np.float32)
    if w.ndim == baza.ndim - 1:
        w = w[..., None]
    return baza * (1 - w) + np.asarray(kolor, np.float32) * w


def kierunek(theta, alfa):
    phi = alfa - math.pi / 2
    return np.stack([np.sin(theta) * np.cos(phi), np.cos(theta), np.sin(theta) * np.sin(phi)], -1)


def raster(ksztalt, rozstaw=9.0, kat=0.6):
    """Odległość (px) do najbliższej kropki rastra."""
    h, w = ksztalt
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    c, s = math.cos(kat), math.sin(kat)
    u = (xx * c - yy * s) / rozstaw
    v = (xx * s + yy * c) / rozstaw
    du = u - np.round(u)
    dv = v - np.round(v)
    return np.sqrt(du * du + dv * dv) * rozstaw


# ----------------------------------------------------------------------------------------------- jajo
def ziarna_komorek(b):
    r = random.Random(b["ziarno"])
    pts = []
    if b["siatka"] == "losowa":
        n = b["komorek"]
        zl = math.pi * (3 - math.sqrt(5))
        for i in range(n):
            y = 1 - 2 * (i + 0.5) / n
            rr = math.sqrt(1 - y * y)
            a = zl * i + r.uniform(-0.25, 0.25)
            p = np.array([rr * math.cos(a), y, rr * math.sin(a)]) + np.array([r.gauss(0, 0.07) for _ in range(3)])
            pts.append(p / np.linalg.norm(p))
    else:  # łuski: rzędy po szerokości, przesunięte o pół
        rzedy = 9
        for k in range(rzedy + 1):
            th = math.pi * (k + 0.15) / (rzedy + 0.3)
            m = max(1, int(round(13 * math.sin(th) + 0.5)))
            for j in range(m):
                a = 2 * math.pi * (j + 0.5 * (k % 2)) / m + r.uniform(-0.04, 0.04)
                pts.append(kierunek(np.array(th + r.uniform(-0.03, 0.03)), np.array(a)))
    return np.array(pts, np.float32)


def linie_podzialu_3d(pod, gesto=2500, ktore=(0, 1)):
    """Punkty linii podziału na kuli: 0 = obrzeże dolnej skorupy, 1 = linia przednia, 2 = prosty szew z tyłu."""
    pts = []
    for nr, linia in enumerate(pod.linie_uv(gesto)):
        if nr not in ktore:
            continue
        for u, v in linia:
            pts.append(kierunek(np.array(v / K.V_MAX * math.pi), np.array(u * 2 * math.pi)))
    return np.array(pts, np.float32)


def jajo(biom):
    b = BIOMY[biom]
    hv = int(round(K.V_MAX * H))
    yy, xx = np.mgrid[0:hv, 0:W].astype(np.float32)
    theta = (yy + 0.5) / hv * math.pi
    alfa = (xx + 0.5) / W * 2 * math.pi
    p = kierunek(theta, alfa).astype(np.float32)
    # zakrzywienie krawędzi płytek (szum w pikselach tekstury)
    war = np.stack([szum((hv, W), (6, 12), b["ziarno"] + i, 3) for i in range(3)], -1) * 0.055
    pw = p + war
    pw /= np.linalg.norm(pw, axis=-1, keepdims=True)
    ziarna = ziarna_komorek(b)
    drzewo = cKDTree(ziarna)
    _, idx = drzewo.query(pw.reshape(-1, 3), k=2)
    i1 = idx[:, 0].reshape(hv, W)
    i2 = idx[:, 1].reshape(hv, W)
    s1, s2 = ziarna[i1], ziarna[i2]
    d1 = ((pw - s1) ** 2).sum(-1)
    d2 = ((pw - s2) ** 2).sum(-1)
    e = (d2 - d1) / (2 * np.linalg.norm(s2 - s1, axis=-1) + 1e-6) * PX_NA_JEDN   # px do krawędzi płytki
    r = random.Random(b["ziarno"] * 3 + 1)
    n = len(ziarna)
    kol, wagi = zip(*b["plyty"])
    kolory = np.array([hx(k) for k in kol])
    wyb = np.array(r.choices(range(len(kol)), weights=wagi, k=n))
    jitter = np.array([r.uniform(0.9, 1.08) for _ in range(n)], np.float32)
    baza = kolory[wyb][i1] * jitter[i1][..., None]
    # cień dwutonowy: dolna część każdej płytki
    th_z = np.arccos(np.clip(ziarna[:, 1], -1, 1))
    rozm = math.sqrt(4 * math.pi / n)
    prog = np.array([r.uniform(0.0, 0.3) for _ in range(n)], np.float32)
    faza = np.array([r.uniform(0, 6.28) for _ in range(n)], np.float32)
    dy = (np.arccos(np.clip(pw[..., 1], -1, 1)) - th_z[i1]) / rozm
    fala = 0.07 * np.sin(alfa * 9 + faza[i1]) + 0.05 * np.sin(alfa * 23 + 2 * faza[i1])
    cien = gladko(-0.015, 0.015, dy - prog[i1] - fala)
    cien_kol = baza * 0.5 + hx(b["cien_ton"]) * 0.28
    kolor = baza * (1 - cien[..., None]) + cien_kol * cien[..., None]
    # raster w cieniu
    rd = raster((hv, W), 9.0)
    kropka = (rd < 1.4 + 1.6 * gladko(0.0, 0.5, dy - prog[i1])) & (cien > 0.5)
    kolor[kropka] = kolor[kropka] * 0.72
    # rozświetlenie u góry płytki
    sw = gladko(0.015, -0.015, dy + 0.42 + fala * 0.5) * gladko(9, 16, e)
    kolor = kolor * (1 - 0.55 * sw[..., None]) + hx(b["swiatlo_ton"]) * (0.55 * sw[..., None])
    # cętki (Bagno): ciemnofioletowe plamki z kreską
    if b["cetki"]:
        cz = np.array([kierunek(np.array(r.uniform(0.25, 2.7)), np.array(r.uniform(0, 6.28))) for _ in range(40)], np.float32)
        dc, _ = cKDTree(cz).query(p.reshape(-1, 3))
        dc = dc.reshape(hv, W) * PX_NA_JEDN
        rc = 14 + 10 * (szum((hv, W), (4, 8), 77, 2) * 0.5 + 0.5)
        plamka = dc < rc
        kolor[plamka] = kolor[plamka] * 0.55 + hx("3A2A52") * 0.45
        obw = np.abs(dc - rc) < 1.8
        kolor[obw] = hx(b["kreska"])
    # złote obwódki łusek (Dżungla)
    if b["zloto"] is not None:
        z = gladko(3.0, 3.8, e) * gladko(7.5, 6.3, e)
        kolor = mieszaj(kolor, hx(b["zloto"]), z * 0.9)
    # kreska między płytkami
    kolor = mieszaj(kolor, hx(b["kreska"]), gladko(3.4, 2.4, e))
    # świecące pęknięcia: wybrane krawędzie + linie podziału skorupy
    para = np.minimum(i1, i2) * 1000 + np.maximum(i1, i2)
    pary = np.unique(para)
    rs = random.Random(b["ziarno"] + 5)
    swiec = np.array([p_ for p_ in pary if rs.random() < b["swiecace"]])
    e_sw = np.where(np.isin(para, swiec), e, 999.0)
    pod = K.Podzial(**b["podzial"])
    dl, _ = cKDTree(linie_podzialu_3d(pod)).query(p.reshape(-1, 3))
    e_pod = dl.reshape(hv, W) * PX_NA_JEDN
    # szew z tyłu (prosty, bo tam kończy się UV) — zwykła cienka kreska, bez blasku
    dt, _ = cKDTree(linie_podzialu_3d(pod, ktore=(2,))).query(p.reshape(-1, 3))
    kolor = mieszaj(kolor, hx(b["kreska"]), gladko(2.6, 1.6, dt.reshape(hv, W) * PX_NA_JEDN))
    e_gl = np.minimum(e_sw, e_pod * 0.9)
    kolor = mieszaj(kolor, hx(b["kreska"]), gladko(6.5, 5.0, e_gl))
    rdzen = gladko(2.9, 1.6, e_gl)
    halo = np.exp(-(e_gl / 9.0) ** 2)
    kolor = mieszaj(kolor, hx(b["blask"]), np.clip(halo * 0.55 + gladko(4.6, 2.6, e_gl) * 0.9, 0, 1))
    kolor = mieszaj(kolor, hx(b["blask_rdzen"]), rdzen)
    maska = np.clip(rdzen * 1.0 + gladko(4.6, 2.6, e_gl) * 0.75 + halo * 0.35, 0, 1)
    # drobne rysy wewnątrz płytek
    img = Image.fromarray((np.clip(kolor, 0, 1) * 255).astype(np.uint8))
    dr = ImageDraw.Draw(img)
    rr = random.Random(b["ziarno"] + 9)
    for _ in range(120):
        x, y = rr.uniform(0, W), rr.uniform(hv * 0.05, hv * 0.95)
        a = rr.uniform(0, 6.28)
        pts = [(x, y)]
        for _k in range(rr.randint(2, 4)):
            a += rr.uniform(-0.8, 0.8)
            x += math.cos(a) * rr.uniform(10, 22)
            y += math.sin(a) * rr.uniform(8, 16)
            pts.append((x, y))
        dr.line(pts, fill=tuple(int(c * 255) for c in hx(b["kreska"])), width=2)
    pelny = np.zeros((H, W, 3), np.float32)
    pelny[:hv] = np.asarray(img, np.float32) / 255
    mpel = np.zeros((H, W), np.float32)
    mpel[:hv] = maska
    # pas wnętrza skorupy i krawędzi pęknięcia
    pelny[hv:] = hx(b["kreska"])
    w0, w1 = [int(v * H) for v in K.PAS_WNETRZE]
    k0, k1 = [int(v * H) for v in K.PAS_KRAWEDZ]
    wn = np.ones((w1 - w0, W, 3), np.float32) * hx(b["wnetrze"])
    wn[raster((w1 - w0, W), 7.0) < 1.3] *= 0.85
    pelny[w0:w1] = wn
    pelny[k0:k1] = hx(b["blask"]) * 0.5 + hx(b["blask_rdzen"]) * 0.5
    mpel[w0:w1] = 0.22
    mpel[k0:k1] = 1.0
    return pelny, mpel


# ----------------------------------------------------------------------------------------------- atlas ozdób
def kolor255(s):
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def pole_szum(w, h, ziarno, kom=(4, 4), okt=3):
    return szum((h, w), kom, ziarno, okt)


def wklej(atl, biom, pole, arr):
    x0, y0, x1, y1 = A.POLA[biom][pole]
    atl[y0:y1, x0:x1] = arr[: y1 - y0, : x1 - x0]


def plama_tonowa(w, h, jasny, ciemny, kreska, ziarno, prog=0.15, kom=(3, 3), obw=2.2):
    """Dwutonowe plamy z kreską na granicy (błoto, mech, kamień)."""
    n = pole_szum(w, h, ziarno, kom, 3)
    a = np.ones((h, w, 3), np.float32) * hx(jasny)
    a = mieszaj(a, hx(ciemny), gladko(prog - 0.04, prog + 0.04, n))
    gy, gx = np.gradient(n)
    gm = np.sqrt(gx * gx + gy * gy) + 1e-6
    a = mieszaj(a, hx(kreska), gladko(obw, obw * 0.5, np.abs(n - prog) / gm))
    return a, n


def kamyki(arr, ziarno, ile, kol, kreska, rmin=8, rmax=22):
    img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    r = random.Random(ziarno)
    h, w = arr.shape[:2]
    for _ in range(ile):
        x, y, rr = r.uniform(rmax, w - rmax), r.uniform(rmax, h - rmax), r.uniform(rmin, rmax)
        pts = [(x + rr * math.cos(t) * r.uniform(0.8, 1.1), y + rr * 0.75 * math.sin(t) * r.uniform(0.8, 1.1))
               for t in np.linspace(0, 6.28, 9)[:-1]]
        d.polygon(pts, fill=kolor255(kol), outline=kolor255(kreska), width=3)
        d.line([(x - rr * 0.4, y - rr * 0.35), (x + rr * 0.1, y - rr * 0.5)], fill=(255, 255, 240), width=2)
    return np.asarray(img, np.float32) / 255


def ksztalt_lisc(w, h, pole, tlo, jasny, ciemny, zylka, kreska, zylki_boczne=True):
    """Kształt liścia z atlas.kontur (ten sam co siatka): wypełnienie, ciemniejsza połowa (zagięcie wzdłuż
    nerwu), nerw środkowy, żyłki boczne, ciemna kreska na obrysie."""
    img = Image.new("RGB", (w, h), kolor255(tlo))
    d = ImageDraw.Draw(img)
    m = A.MARGINES

    def P(x, y):
        return (w * (m + (1 - 2 * m) * x), h * (1 - (m + (1 - 2 * m) * y)))
    kont = [P(x, y) for x, y in A.kontur(pole)]
    d.polygon(kont, fill=kolor255(jasny))
    n = A.RZEDY_KSZTALTU[pole]
    f = A.KSZTALTY[pole]
    lewa = [P(0.5, k / n) for k in range(n + 1)] + [P(0.5 - f(k / n) / 2, k / n) for k in reversed(range(n + 1))]
    d.polygon(lewa, fill=kolor255(ciemny))
    if zylki_boczne:
        for k in range(1, 9):
            y = k / 9.5
            for s in (-1, 1):
                x2 = 0.5 + s * f(min(0.99, y + 0.08)) / 2 * 0.85
                d.line([P(0.5, y), P(x2, min(0.99, y + 0.1))], fill=kolor255(zylka), width=max(2, w // 90))
    d.line([P(0.5, 0.0), P(0.5, 0.97)], fill=kolor255(zylka), width=max(3, w // 45))
    d.line(kont + [kont[0]], fill=kolor255(kreska), width=max(4, w // 28), joint="curve")
    return np.asarray(img, np.float32) / 255


def paski(w, h, kol_a, kol_b, kreska, ziarno, ukos=0.0, okres=26.0):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    n = pole_szum(w, h, ziarno, (2, 4), 2)
    t = (xx + yy * ukos) / okres + n * 0.6
    f = t - np.floor(t)
    a = np.ones((h, w, 3), np.float32) * hx(kol_a)
    a = mieszaj(a, hx(kol_b), gladko(0.45, 0.55, f))
    a = mieszaj(a, hx(kreska), gladko(0.07, 0.0, np.abs(f - 0.5)) * 0.85)
    return a


def atlas(biom):
    S = A.ROZMIAR
    atl = np.zeros((S, S, 3), np.float32)
    atl[:] = hx("202020")
    P = A.POLA[biom]

    def wym(p):
        x0, y0, x1, y1 = P[p]
        return x1 - x0, y1 - y0
    if biom == "bagno":
        k = "17141C"
        w, h = wym("bloto")
        a, n = plama_tonowa(w, h, "5B4A2E", "3E3220", k, 3, 0.1, (5, 5))
        a = mieszaj(a, hx("4A5A2A"), gladko(0.3, 0.5, pole_szum(w, h, 11, (3, 3), 2)) * 0.55)   # zieleń mułu
        a[(raster((h, w), 8.0) < 1.4) & (n > 0.1)] *= 0.75
        a = kamyki(a, 5, 9, "6E6A5A", k, 8, 20)
        wklej(atl, biom, "bloto", a)
        w, h = wym("bloto_bok")
        a, _ = plama_tonowa(w, h, "4A3B26", "2F2618", k, 13, 0.0, (3, 6))
        wklej(atl, biom, "bloto_bok", a)
        w, h = wym("kamien")
        a, _ = plama_tonowa(w, h, "7A7C6A", "5A5C4E", k, 21, 0.15, (3, 3))
        a = mieszaj(a, hx("5E7A3A"), gladko(0.35, 0.45, pole_szum(w, h, 22, (3, 3), 2)) * 0.8)
        wklej(atl, biom, "kamien", a)
        w, h = wym("kora")
        wklej(atl, biom, "kora", paski(w, h, "4A3346", "33233A", k, 31, 0.0, 30.0))
        w, h = wym("trzcina")
        wklej(atl, biom, "trzcina", ksztalt_lisc(w, h, "trzcina", "4E6A31", "86A84A", "5E7F34", "B4CF6A", k, False))
        w, h = wym("palka")
        a = paski(w, h, "6A4326", "583720", k, 41, 0.0, 18.0)
        a[raster((h, w), 7.0, 0.3) < 1.6] *= 0.7
        a[:10] = hx(k)
        a[-10:] = hx(k)
        wklej(atl, biom, "palka", a)
        w, h = wym("lodyga")
        wklej(atl, biom, "lodyga", paski(w, h, "6E9440", "557A30", k, 51, 0.0, 22.0))
        w, h = wym("grzybien")
        img = Image.new("RGB", (w, h), kolor255("2E4A2A"))
        d = ImageDraw.Draw(img)
        kont = [(x * w, (1 - y) * h) for x, y in A.grzybien_kontur()]
        d.polygon(kont[1:], fill=kolor255("5FA040"))
        d.polygon([kont[0]] + kont[1:10], fill=kolor255("4E8A36"))
        for x, y in A.grzybien_kontur(12)[1:]:
            d.line([kont[0], (x * w, (1 - y) * h)], fill=kolor255("8CC85E"), width=3)
        d.line(kont[1:], fill=kolor255(k), width=7, joint="curve")
        d.line([kont[1], kont[0], kont[-1]], fill=kolor255(k), width=7)
        wklej(atl, biom, "grzybien", np.asarray(img, np.float32) / 255)
        w, h = wym("platek")
        wklej(atl, biom, "platek", ksztalt_lisc(w, h, "platek", "F3A6C8", "FBD3E6", "EE8DB8", "FFFFFF", "5A1E3A", False))
        w, h = wym("srodek")
        a = np.ones((h, w, 3), np.float32) * hx("FFD84A")
        a[raster((h, w), 10.0) < 2.5] = hx("E79A2A")
        wklej(atl, biom, "srodek", a)
        w, h = wym("woda")
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        a = np.ones((h, w, 3), np.float32) * hx("24443E")
        n = pole_szum(w, h, 61, (3, 3), 2)
        a = mieszaj(a, hx("2E5A50"), gladko(0.0, 0.2, n))
        rr = np.sqrt((xx - w * 0.4) ** 2 + (yy - h * 0.55) ** 2) / 22.0 + n * 0.8
        a = mieszaj(a, hx("8FD8B0"), gladko(0.1, 0.0, np.abs(rr - np.round(rr))) * gladko(9, 4, rr) * 0.8)
        wklej(atl, biom, "woda", a)
    else:
        k = "10231A"
        w, h = wym("plyta")
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        n = pole_szum(w, h, 71, (4, 4), 2)
        bx = (xx + n * 6) / 96.0
        by = (yy + n * 6) / 64.0 + 0.5 * (np.floor((xx + n * 6) / 96.0) % 2)
        fx, fy = bx - np.floor(bx), by - np.floor(by)
        a = np.ones((h, w, 3), np.float32) * hx("8C8A70")
        a = mieszaj(a, hx("6F7058"), gladko(0.55, 0.62, fy))
        kr = np.minimum(np.minimum(fx, 1 - fx) * 96, np.minimum(fy, 1 - fy) * 64)
        a = mieszaj(a, hx(k), gladko(3.0, 1.8, kr))
        a = mieszaj(a, hx("3E9E40"), gladko(0.25, 0.32, pole_szum(w, h, 72, (4, 4), 3)))   # mech na płytach
        wklej(atl, biom, "plyta", a)
        for pole, z in (("fryz", 0), ("fryz2", 1)):
            w, h = wym(pole)
            yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
            a = np.ones((h, w, 3), np.float32) * hx("8A8770")
            a = mieszaj(a, hx("6C6A56"), gladko(0.6, 0.7, yy / h))
            if z == 0:   # schodkowy meander (2 na ścianę) z wpustem złota i różowym „okiem”
                t = (xx % 256) / 256.0
                v = (yy - 14) / (h - 28)
                stopnie = np.floor(t * 4) / 4
                rowek = (np.abs(v - (0.15 + 0.7 * stopnie)) < 0.11) | ((np.abs((t * 4) % 1) < 0.06) & (v > 0.05) & (v < 0.95))
                a[rowek] = hx(k)
                a[(np.abs(v - (0.15 + 0.7 * stopnie)) < 0.055) & ((t * 4) % 1 > 0.06)] = hx("F2B530")
                a[((xx % 256 - 200) ** 2 + (yy - h * 0.3) ** 2) < 150] = hx(k)
                a[((xx % 256 - 200) ** 2 + (yy - h * 0.3) ** 2) < 80] = hx("FF5FA8")
            else:        # trójkąty z turkusem
                t = (xx % 128) / 128.0
                v = yy / h
                gr = 0.2 + 1.2 * np.abs(t - 0.5)
                a[(v > gr) & (v < 0.85)] = hx("2AA89A")
                a[(np.abs(v - gr) < 0.045) & (v < 0.86)] = hx(k)
            a[:7] = hx(k)
            a[-7:] = hx(k)
            a[:, :4] = hx(k)
            a[:, -4:] = hx(k)
            wklej(atl, biom, pole, a)
        w, h = wym("mech")
        a, n = plama_tonowa(w, h, "4FB443", "2F8A3A", k, 81, 0.1, (4, 4))
        a[(raster((h, w), 9.0) < 1.6) & (n > 0.1)] *= 0.8
        wklej(atl, biom, "mech", a)
        w, h = wym("liana")
        wklej(atl, biom, "liana", paski(w, h, "5E8A2E", "4A6E24", k, 91, 1.2, 26.0))
        w, h = wym("kora")
        wklej(atl, biom, "kora", paski(w, h, "6A4A2C", "5C3A22", k, 92, 0.0, 30.0))
        w, h = wym("lisc")
        wklej(atl, biom, "lisc", ksztalt_lisc(w, h, "lisc", "1E5A2A", "3FB24A", "2C8C3C", "9BE26A", k))
        w, h = wym("platek")
        wklej(atl, biom, "platek", ksztalt_lisc(w, h, "platek", "B0204E", "FF4F9A", "E2337E", "FFC0DD", "4A0A24", False))
        w, h = wym("precik")
        a = np.ones((h, w, 3), np.float32) * hx("FFD23F")
        a[raster((h, w), 9.0) < 2.4] = hx("E0901C")
        wklej(atl, biom, "precik", a)
        w, h = wym("listek")
        wklej(atl, biom, "listek", ksztalt_lisc(w, h, "listek", "1E5A2A", "58C24E", "3E9E40", "A6E87A", k))
        w, h = wym("kamien")
        a, _ = plama_tonowa(w, h, "8C8A70", "6C6A56", k, 95, 0.15, (3, 3))
        wklej(atl, biom, "kamien", a)
    return atl


def zapisz(arr, sciezka):
    Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).save(sciezka, optimize=True)


def main():
    biomy = sys.argv[1:] or list(BIOMY)
    wyj = os.path.join(TU, "tekstury")
    os.makedirs(wyj, exist_ok=True)
    for b in biomy:
        kol, maska = jajo(b)
        zapisz(kol, os.path.join(wyj, "%s_jajo_kolor.png" % b))
        zapisz(np.repeat(maska[..., None], 3, -1), os.path.join(wyj, "%s_jajo_blask.png" % b))
        zapisz(atlas(b), os.path.join(wyj, "%s_ozdoby.png" % b))
        print("tekstury:", b)


if __name__ == "__main__":
    main()
