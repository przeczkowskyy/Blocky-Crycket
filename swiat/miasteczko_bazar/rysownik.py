# -*- coding: utf-8 -*-
"""Lekki rysownik brył z `czesci.json` (Pillow + numpy) — podglądy BEZ Blendera i BEZ Roblox Studio.

Każda część to bryła z panel/luau/KSZTALTY.md (blok, kula, walec o osi X, klin z wysoką ścianą po +Z, klin narożny
z wierzchołkiem w rogu (+X, +Y, −Z)) obrócona jak CFrame.fromOrientation (macierz z swiat/biblioteka/scena.py).
Ściany cieniowane prosto (słońce z pn.-zach., światło nieba), bufor głębi, komiksowy kontur tam, gdzie styka się bryła
z bryłą, lekka mgła w dali.

TO NIE JEST WYGLĄD Z ROBLOX: brak faktur materiałów, cieni rzucanych, poświaty Neonu i oświetlenia miejsca. Podgląd
pokazuje kształty, kolory i układ. Części niewidzialne (przezroczystość ≥ 0,98) są pomijane.
"""
import math
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

_TU = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_TU))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from swiat.biblioteka.scena import macierz_obrotu  # noqa: E402

BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4
SLONCE = np.array((-0.558, 0.728, -0.399))                # wektor ku słońcu (krzywe_miasteczko/PROJEKT.md 4.1)
SLONCE = SLONCE / np.linalg.norm(SLONCE)
NIEBO_GORA = np.array((0.52, 0.72, 0.95))
NIEBO_DOL = np.array((0.84, 0.91, 0.98))


def _bryla(ks, hx, hy, hz):
    """Wierzchołki lokalne i ściany (listy indeksów) kształtu o połówkach (hx, hy, hz)."""
    if ks == KLIN:
        V = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, hz), (hx, hy, hz)]
        F = [[0, 1, 2, 3], [3, 2, 5, 4], [0, 4, 5, 1], [0, 3, 4], [1, 5, 2]]
    elif ks == NAROZNIK:
        V = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (hx, hy, -hz)]
        F = [[0, 1, 2, 3], [0, 4, 1], [1, 4, 2], [0, 3, 4], [3, 2, 4]]
    elif ks == WALEC:
        n = 14
        a = np.linspace(0, 2 * math.pi, n, endpoint=False)
        V = [(-hx, math.cos(t) * hy, math.sin(t) * hz) for t in a] + [(hx, math.cos(t) * hy, math.sin(t) * hz) for t in a]
        F = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)] + [list(range(n)), list(range(n, 2 * n))]
    elif ks == KULA:
        r = hx
        nl, nt = 12, 7
        V = [(0.0, r, 0.0)]
        for i in range(1, nt):
            t = math.pi * i / nt
            for j in range(nl):
                p = 2 * math.pi * j / nl
                V.append((r * math.sin(t) * math.cos(p), r * math.cos(t), r * math.sin(t) * math.sin(p)))
        V.append((0.0, -r, 0.0))
        F = [[0, 1 + j, 1 + (j + 1) % nl] for j in range(nl)]
        for i in range(nt - 2):
            for j in range(nl):
                a0, a1 = 1 + i * nl + j, 1 + i * nl + (j + 1) % nl
                F.append([a0, a1, a1 + nl, a0 + nl])
        last = len(V) - 1
        F += [[last, 1 + (nt - 2) * nl + (j + 1) % nl, 1 + (nt - 2) * nl + j] for j in range(nl)]
    else:
        V = [(sx * hx, sy * hy, sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        F = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
    return np.array(V, dtype=float), F


class Model:
    """Trójkąty całej sceny w świecie: T (n,3,3), normalna N (n,3), kolor K (n,3), id części P, neon, grunt, alfa,
    spód części (y min) i nazwa części (do filtrów kadru)."""

    def __init__(self, dane, pomin=None):
        T, N, K, P, NE, G, A, SP = [], [], [], [], [], [], [], []
        self.nazwy = []
        self.grupy = dane["grupy"]
        mats = dane["materialy"]
        for pid, c in enumerate(dane["czesci"]):
            self.nazwy.append(c[14])
            if c[13] >= 0.98 or (pomin and pomin(c, self.grupy[c[1]])):
                continue
            ks = c[0]
            hx, hy, hz = c[8] / 2.0, c[9] / 2.0, c[10] / 2.0
            R = np.array(macierz_obrotu(math.degrees(c[5]), math.degrees(c[6]), math.degrees(c[7])))
            V, F = _bryla(ks, hx, hy, hz)
            W = V @ R.T + np.array((c[2], c[3], c[4]))
            srodek = W.mean(axis=0)
            kol = np.array([int(c[11][i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
            neon = mats[c[12]] == "Neon"
            spod = float(W[:, 1].min())
            grunt = float(W[:, 1].max()) <= 0.65 and max(c[8], c[10]) > 3.0
            for f in F:
                Pf = W[f]
                n = np.cross(Pf[1] - Pf[0], Pf[2] - Pf[0])
                ln = np.linalg.norm(n)
                if ln < 1e-12 and len(f) > 3:
                    n = np.cross(Pf[2] - Pf[0], Pf[3] - Pf[0])
                    ln = np.linalg.norm(n)
                if ln < 1e-12:
                    continue
                n = n / ln
                if np.dot(n, Pf.mean(axis=0) - srodek) < 0:
                    n = -n
                for i in range(1, len(f) - 1):
                    T.append((Pf[0], Pf[i], Pf[i + 1]))
                    N.append(n)
                    K.append(kol)
                    P.append(pid)
                    NE.append(neon)
                    G.append(grunt)
                    A.append(c[13])
                    SP.append(spod)
        self.T = np.array(T, dtype=float).reshape(-1, 3, 3)
        self.N = np.array(N, dtype=float).reshape(-1, 3)
        self.K = np.array(K, dtype=float).reshape(-1, 3)
        self.P = np.array(P, dtype=np.int64)
        self.neon = np.array(NE, dtype=bool)
        self.grunt = np.array(G, dtype=bool)
        self.alfa = np.array(A, dtype=float)
        self.spod = np.array(SP, dtype=float)


def cieniuj(N, K, neon):
    """Kolor ścian: światło nieba (zależne od pochylenia) + słońce; Neon świeci sam."""
    dif = np.clip(N @ SLONCE, 0, None)[:, None]
    amb = (0.58 + 0.15 * N[:, 1])[:, None]
    k = np.clip(K * (amb + 0.48 * dif), 0, 1)
    k[neon] = np.clip(K[neon] * 1.08 + 0.10, 0, 1)
    return k


class Plotno:
    def __init__(self, W, H, tlo):
        self.W, self.H = W, H
        self.z = np.full((H, W), -1e30)
        self.c = np.array(tlo, dtype=float).copy() if np.ndim(tlo) == 3 else np.broadcast_to(tlo, (H, W, 3)).copy()
        self.id = np.full((H, W), -1, dtype=np.int64)
        self.grunt = np.ones((H, W), dtype=bool)

    def trojkat(self, xy, w, kol, pid, grunt, alfa=0.0):
        xs, ys = xy[:, 0], xy[:, 1]
        x0, x1 = max(int(math.floor(xs.min())), 0), min(int(math.ceil(xs.max())), self.W - 1)
        y0, y1 = max(int(math.floor(ys.min())), 0), min(int(math.ceil(ys.max())), self.H - 1)
        if x0 > x1 or y0 > y1:
            return
        (ax, ay), (bx, by), (cx, cy) = xy
        pole = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
        if abs(pole) < 1e-9:
            return
        PX, PY = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        w0 = ((bx - PX) * (cy - PY) - (by - PY) * (cx - PX)) / pole
        w1 = ((cx - PX) * (ay - PY) - (cy - PY) * (ax - PX)) / pole
        w2 = 1.0 - w0 - w1
        m = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not m.any():
            return
        z = w0 * w[0] + w1 * w[1] + w2 * w[2]
        zs = self.z[y0:y1 + 1, x0:x1 + 1]
        upd = m & (z > zs)
        if not upd.any():
            return
        cs = self.c[y0:y1 + 1, x0:x1 + 1]
        if alfa > 0:
            cs[upd] = cs[upd] * alfa + kol * (1 - alfa)
            return
        zs[upd] = z[upd]
        cs[upd] = kol
        self.id[y0:y1 + 1, x0:x1 + 1][upd] = pid
        self.grunt[y0:y1 + 1, x0:x1 + 1][upd] = grunt

    def kontury(self, sila=0.5):
        """Ciemna kreska na styku dwóch różnych części (poza stykiem dwóch płyt gruntu) — komiksowy tusz."""
        idb, g = self.id, self.grunt
        e = np.zeros(idb.shape, dtype=bool)
        for di, dj in ((0, 1), (1, 0)):
            a = idb[:idb.shape[0] - di, :idb.shape[1] - dj]
            b = idb[di:, dj:]
            ga, gb = g[:g.shape[0] - di, :g.shape[1] - dj], g[di:, dj:]
            r = (a != b) & ~(ga & gb) & (a >= 0) & (b >= 0)
            e[:e.shape[0] - di, :e.shape[1] - dj] |= r
        self.c[e] *= (1.0 - sila)

    def obraz(self):
        return Image.fromarray((np.clip(self.c, 0, 1) * 255).astype(np.uint8), "RGB")


def niebo(H, W):
    t = np.linspace(0, 1, H)[:, None, None]
    return np.broadcast_to(NIEBO_GORA * (1 - t) + NIEBO_DOL * t, (H, W, 3)).copy()


def kadr(model, kam, cel, fov=60.0, W=1600, H=1000, mgla=650.0, kontur=0.42):
    """Ujęcie perspektywiczne z kamery `kam` na `cel` (świat), kąt widzenia w pionie fov°."""
    kam, cel = np.array(kam, float), np.array(cel, float)
    f = cel - kam
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 1.0, 0.0))
    r /= np.linalg.norm(r)
    up = np.cross(r, f)
    ogn = (H / 2.0) / math.tan(math.radians(fov) / 2.0)
    pl = Plotno(W, H, niebo(H, W))
    T = model.T
    srodki = T.mean(axis=1)
    widoczne = np.einsum("ij,ij->i", model.N, srodki - kam) < 0
    Q = T - kam
    zc = Q @ f
    widoczne &= zc.max(axis=1) > 0.35
    kol = cieniuj(model.N, model.K, model.neon)
    d = np.linalg.norm(srodki - kam, axis=1)
    mg = (1.0 - np.exp(-d / mgla))[:, None]
    kol = kol * (1 - 0.5 * mg) + NIEBO_DOL * 0.5 * mg
    xc, yc = Q @ r, Q @ up
    blizej = 0.35
    przezr = []
    for i in np.nonzero(widoczne)[0]:
        pts = np.stack((xc[i], yc[i], zc[i]), axis=1)
        if pts[:, 2].min() < blizej:                          # przycięcie płaszczyzną bliską
            wyn = []
            for j in range(3):
                a, b = pts[j], pts[(j + 1) % 3]
                ina, inb = a[2] >= blizej, b[2] >= blizej
                if ina:
                    wyn.append(a)
                if ina != inb:
                    t = (blizej - a[2]) / (b[2] - a[2])
                    wyn.append(a + (b - a) * t)
            if len(wyn) < 3:
                continue
            pts = np.array(wyn)
        sx = W / 2.0 + ogn * pts[:, 0] / pts[:, 2]
        sy = H / 2.0 - ogn * pts[:, 1] / pts[:, 2]
        if sx.max() < 0 or sx.min() > W or sy.max() < 0 or sy.min() > H:
            continue
        w = 1.0 / pts[:, 2]
        xy = np.stack((sx, sy), axis=1)
        if model.alfa[i] > 0:
            przezr.append((xy, w, kol[i], model.alfa[i]))
            continue
        for j in range(1, len(xy) - 1):
            pl.trojkat(xy[[0, j, j + 1]], w[[0, j, j + 1]], kol[i], model.P[i], model.grunt[i])
    pl.kontury(kontur)
    for xy, w, k, a in przezr:
        for j in range(1, len(xy) - 1):
            pl.trojkat(xy[[0, j, j + 1]], w[[0, j, j + 1]], k, -2, False, alfa=a)
    return pl.obraz()


def kadr_gora(model, x0, x1, z0, z1, skala, tlo=(0.20, 0.24, 0.20), kontur=0.35):
    """Rzut prostokątny z góry (świat): x w prawo, z w dół (północ = −Z na górze). Zwraca (obraz, (x, z) → piksel)."""
    W, H = int(round((x1 - x0) * skala)), int(round((z1 - z0) * skala))
    pl = Plotno(W, H, np.array(tlo))
    kol = cieniuj(model.N, model.K, model.neon)
    for i in np.nonzero(model.N[:, 1] > 1e-6)[0]:
        P = model.T[i]
        xy = np.stack(((P[:, 0] - x0) * skala, (P[:, 2] - z0) * skala), axis=1)
        if xy[:, 0].max() < 0 or xy[:, 0].min() > W or xy[:, 1].max() < 0 or xy[:, 1].min() > H:
            continue
        pl.trojkat(xy, P[:, 1], kol[i], model.P[i], model.grunt[i], alfa=model.alfa[i] if model.alfa[i] > 0 else 0.0)
    pl.kontury(kontur)
    return pl.obraz(), (lambda x, z: ((x - x0) * skala, (z - z0) * skala))


def czcionka(rozmiar, gruba=False):
    for nazwa in (("arialbd.ttf", "segoeuib.ttf") if gruba else ("arial.ttf", "segoeui.ttf")):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def naglowek(img, tytul, opis, wys=96):
    """Pasek z tytułem i opisem nad kadrem (napisy ≥ 24 px — czytelne na telefonie)."""
    nowy = Image.new("RGB", (img.width, img.height + wys), (250, 246, 236))
    nowy.paste(img, (0, wys))
    d = ImageDraw.Draw(nowy)
    d.text((20, 10), tytul, fill=(40, 34, 30), font=czcionka(36, True))
    d.text((20, 56), opis, fill=(105, 80, 58), font=czcionka(24))
    return nowy


def ramka_napisu(d, xy, tekst, font, tlo=(255, 250, 238), kolor=(30, 26, 22), obrys=(30, 26, 22), kotwica="mm", pad=6):
    """Napis w jasnej ramce z ciemnym obrysem (czytelny na każdym tle). Zwraca prostokąt ramki."""
    x, y = xy
    l, t, r, b = d.textbbox((0, 0), tekst, font=font)
    w, h = r - l, b - t
    if kotwica == "mm":
        x0, y0 = x - w / 2 - pad, y - h / 2 - pad
    elif kotwica == "lm":
        x0, y0 = x - pad, y - h / 2 - pad
    else:
        x0, y0 = x - w - pad, y - h / 2 - pad
    box = (x0, y0, x0 + w + 2 * pad, y0 + h + 2 * pad)
    d.rounded_rectangle(box, radius=7, fill=tlo, outline=obrys, width=3)
    d.text((x0 + pad - l, y0 + pad - t), tekst, fill=kolor, font=font)
    return box
