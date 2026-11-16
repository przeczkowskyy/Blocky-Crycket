#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podgląd lasu-pasa BEZ Blendera i bez Studio: własny lekki rysownik brył z czesci.json (Pillow + numpy).

    python -B swiat/las_pas/podglad.py                     # wszystkie kadry → swiat/las_pas/podglad/*.jpg
    python -B swiat/las_pas/podglad.py --tylko gora,lasek  # wybrane kadry
    python -B swiat/las_pas/podglad.py --wyj <folder>      # kadry gdzie indziej (np. robocze)

Kadry: `gora` (rzut z góry całego pasa — u w górę, v w prawo, jak plansza planu), `gora_strefy` (to samo z placami walki
r 12, pętlami, ścieżką i otwarciami przejść), cztery ujęcia z ukosa (`polana_zagroda`, `lasek`, `zarosla_leze`,
`arena_brama`), Polana od furtki (`polana_wejscie`) i dwa z oczu gracza (`oczy_przybycie`, `oczy_zarosla`). Te same
kamery zapisuje w świecie Studio do `ujecia_swiat.json` (dla tools/studio_zrzuty.py w następnym etapie).

Jak to działa: każda część to bryła z panel/luau/KSZTALTY.md (blok, kula, walec o osi X, klin, klin narożny) obrócona
jak CFrame.fromOrientation; ściany cieniowane prosto (słońce z pn.-zach. świata, światło nieba), rysowane z buforem
głębi (rzut perspektywiczny albo prostokątny z góry), kontury tam, gdzie styka się bryła z bryłą, lekka mgła w dali.
TO NIE JEST WYGLĄD Z ROBLOX: brak faktur materiałów, cieni rzucanych, poświaty Neonu i oświetlenia miejsca — tylko
kształty, kolory (po korekcie faktury.py) i układ. Części niewidzialne (przezroczystość ≥ 0,98) są pomijane.
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFont

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.las_pas.kontekst import ODCINKI_SCIEZKI, PLAC_R, v_sciezki  # noqa: E402
from swiat.las_pas.zasady import macierz, polowki  # noqa: E402

BLOK, KULA, WALEC, KLIN, NAROZNIK = 0, 1, 2, 3, 4
SLONCE = np.array((-0.42, 0.78, -0.46))
SLONCE = SLONCE / np.linalg.norm(SLONCE)
NIEBO_GORA = np.array((0.55, 0.74, 0.95))
NIEBO_DOL = np.array((0.80, 0.89, 0.98))
X0, Z0 = 1100.0, -700.0

# kadry z ukosa i z oczu gracza: (kamera [u, wys, v], cel [u, wys, v], kąt widzenia w pionie °, opis)
KADRY = {
    "polana_wejscie": ((62.0, 22.0, 20.0), (4.0, 6.0, -6.0), 58.0, "Polana Przybycia widziana od furtki: Brama Pniaków, "
                       "Kamień Powrotu, stanowisko jajka"),
    "polana_zagroda": ((-20.0, 44.0, -2.0), (122.0, 0.0, 6.0), 50.0, "Polana Przybycia i Zagroda Slime'ów"),
    "lasek": ((234.0, 30.0, 10.0), (362.0, 0.0, -2.0), 52.0, "strumyk z mostkiem i Lasek Muchomorowy"),
    "zarosla_leze": ((548.0, 36.0, -12.0), (736.0, 0.0, 4.0), 50.0, "Wilcze Zarośla, kamienny próg i Leże Trolla"),
    "arena_brama": ((790.0, 28.0, 14.0), (900.0, 5.0, -2.0), 54.0, "brama menhirów, Arena Strażnika i Brama do Bagna"),
    "oczy_przybycie": ((14.0, 5.6, 0.0), (80.0, 4.0, 0.0), 60.0, "z oczu gracza w miejscu przybycia"),
    "oczy_zarosla": ((468.0, 5.6, 1.0), (560.0, 3.5, 0.0), 60.0, "z oczu gracza przed jeżynowym zwężeniem (Lasek → Zarośla)"),
}


# =========================================================================== bryły → wielokąty
def _bryla(ks, E):
    """(wierzchołki lokalne (n,3), ściany = listy indeksów) dla kształtu i połówek E."""
    hx, hy, hz = E
    if ks == KLIN:
        V = np.array([(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (-hx, hy, hz), (hx, hy, hz)])
        F = [[0, 1, 2, 3], [3, 2, 5, 4], [0, 1, 5, 4], [0, 3, 4], [1, 2, 5]]
    elif ks == NAROZNIK:
        V = np.array([(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz), (hx, hy, -hz)])
        F = [[0, 1, 2, 3], [0, 1, 4], [1, 2, 4], [0, 4, 3], [4, 2, 3]]
    elif ks == WALEC:
        n = 12
        a = np.linspace(0, 2 * math.pi, n, endpoint=False)
        ring = np.stack((np.cos(a) * hy, np.sin(a) * hy), axis=1)
        V = np.concatenate((np.column_stack((np.full(n, -hx), ring)), np.column_stack((np.full(n, hx), ring))))
        F = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)] + [list(range(n)), list(range(n, 2 * n))]
    elif ks == KULA:
        r = hx
        nl, nt = 10, 6
        pts = [(0.0, r, 0.0)]
        for i in range(1, nt):
            t = math.pi * i / nt
            for j in range(nl):
                p = 2 * math.pi * j / nl
                pts.append((r * math.sin(t) * math.cos(p), r * math.cos(t), r * math.sin(t) * math.sin(p)))
        pts.append((0.0, -r, 0.0))
        V = np.array(pts)
        F = []
        for j in range(nl):
            F.append([0, 1 + j, 1 + (j + 1) % nl])
        for i in range(nt - 2):
            for j in range(nl):
                a0 = 1 + i * nl + j
                a1 = 1 + i * nl + (j + 1) % nl
                F.append([a0, a1, a1 + nl, a0 + nl])
        last = len(pts) - 1
        for j in range(nl):
            F.append([last, 1 + (nt - 2) * nl + (j + 1) % nl, 1 + (nt - 2) * nl + j])
    else:
        V = np.array([(sx * hx, sy * hy, sz * hz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])
        F = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    return V, F


def wczytaj(plik):
    with open(plik, encoding="utf-8") as f:
        d = json.load(f)
    sciany = []                                              # (wierzchołki świata (n,3), normalna, kolor rgb 0–1, id, neon, grunt)
    for pid, c in enumerate(d["czesci"]):
        if c[13] >= 0.98:
            continue
        ks = c[0]
        E = polowki(c)
        R = macierz(c[5], c[6], c[7])
        V, F = _bryla(ks, E)
        W = V @ R.T + np.array((c[2], c[3], c[4]))
        srodek = W.mean(axis=0)
        kol = np.array([int(c[11][i:i + 2], 16) / 255.0 for i in (0, 2, 4)])
        neon = d["materialy"][c[12]] == "Neon"
        top = float(W[:, 1].max())
        grunt = top <= 0.45
        for f in F:
            P = W[f]
            n = np.cross(P[1] - P[0], P[2] - P[0])
            if np.linalg.norm(n) < 1e-9 and len(f) > 3:
                n = np.cross(P[2] - P[0], P[3] - P[0])
            ln = np.linalg.norm(n)
            if ln < 1e-12:
                continue
            n = n / ln
            if np.dot(n, P.mean(axis=0) - srodek) < 0:
                n = -n
            sciany.append((P, n, kol, pid, neon, grunt, c[13]))
    return d, sciany


def cieniuj(n, kol, neon):
    if neon:
        return np.clip(kol * 1.08 + 0.08, 0, 1)
    dif = max(0.0, float(np.dot(n, SLONCE)))
    amb = 0.56 + 0.16 * float(n[1])
    return np.clip(kol * (amb + 0.5 * dif), 0, 1)


# =========================================================================== rasteryzacja z buforem głębi
class Plotno:
    def __init__(self, W, H, tlo):
        self.W, self.H = W, H
        self.z = np.full((H, W), -1e30)
        self.c = np.zeros((H, W, 3))
        self.c[:] = tlo
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
        m = (w0 >= -1e-7) & (w1 >= -1e-7) & (w2 >= -1e-7)
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
        """Ciemna kreska tam, gdzie styka się bryła z bryłą (poza stykami dwóch warstw gruntu) — komiksowy tusz."""
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


def kadr_perspektywa(sciany, kam, cel, fov, W=1600, H=1000, mgla=520.0):
    """Ujęcie z kamery (świat) na cel (świat), kąt widzenia w pionie fov°."""
    kam, cel = np.array(kam, float), np.array(cel, float)
    f = cel - kam
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 1.0, 0.0))
    r /= np.linalg.norm(r)
    up = np.cross(r, f)
    ogn = (H / 2.0) / math.tan(math.radians(fov) / 2.0)
    pl = Plotno(W, H, 0)
    pl.c = niebo(H, W)
    blizej = 0.4
    przezr = []
    for P, n, kol, pid, neon, grunt, alfa in sciany:
        sr = P.mean(axis=0)
        if np.dot(n, sr - kam) >= 0:
            continue
        Q = P - kam
        zc = Q @ f
        if zc.max() < blizej:
            continue
        xc, yc = Q @ r, Q @ up
        pts = np.stack((xc, yc, zc), axis=1)
        if zc.min() < blizej:                                   # przycięcie płaszczyzną bliską
            wyn = []
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
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
        w = 1.0 / pts[:, 2]
        k = cieniuj(n, kol, neon)
        d = float(np.linalg.norm(sr - kam))
        mg = 1.0 - math.exp(-d / mgla)
        k = k * (1 - 0.55 * mg) + NIEBO_DOL * 0.55 * mg
        xy = np.stack((sx, sy), axis=1)
        if alfa > 0:
            przezr.append((xy, w, k, pid, alfa))
            continue
        for i in range(1, len(xy) - 1):
            pl.trojkat(xy[[0, i, i + 1]], w[[0, i, i + 1]], k, pid, grunt)
    pl.kontury(0.42)
    for xy, w, k, pid, alfa in przezr:
        for i in range(1, len(xy) - 1):
            pl.trojkat(xy[[0, i, i + 1]], w[[0, i, i + 1]], k, pid, False, alfa=alfa)
    return pl.obraz()


def kadr_gora(sciany, skala=3.0, u0=-36.0, u1=968.0, v0=-90.0, v1=90.0):
    """Rzut prostokątny z góry: u w górę, v w prawo (jak plansza planu). Zwraca (obraz, funkcja (u, v) → piksel)."""
    W = int((v1 - v0) * skala)
    H = int((u1 - u0) * skala)
    pl = Plotno(W, H, np.array((0.16, 0.2, 0.17)))
    for P, n, kol, pid, neon, grunt, alfa in sciany:
        if n[1] <= 1e-6:
            continue
        u = P[:, 0] - X0
        v = P[:, 2] - Z0
        sx = (v - v0) * skala
        sy = (u1 - u) * skala
        w = P[:, 1]
        k = cieniuj(n, kol, neon)
        xy = np.stack((sx, sy), axis=1)
        for i in range(1, len(xy) - 1):
            pl.trojkat(xy[[0, i, i + 1]], w[[0, i, i + 1]], k, pid, grunt, alfa=alfa if alfa > 0 else 0.0)
    pl.kontury(0.35)
    return pl.obraz(), (lambda u, v: ((v - v0) * skala, (u1 - u) * skala))


def czcionka(rozmiar, gruba=False):
    for nazwa in (("arialbd.ttf", "segoeuib.ttf") if gruba else ("arial.ttf", "segoeui.ttf")):
        try:
            return ImageFont.truetype(nazwa, rozmiar)
        except OSError:
            continue
    return ImageFont.load_default()


def podpis(img, tytul, opis):
    d = ImageDraw.Draw(img)
    f1, f2 = czcionka(30, True), czcionka(19)
    d.rectangle((0, 0, img.width, 74), fill=(250, 246, 236))
    d.text((18, 8), tytul, fill=(40, 34, 30), font=f1)
    d.text((18, 46), opis, fill=(110, 84, 60), font=f2)
    return img


def plansza_gory(img, rzut, plan, strefy=False):
    """Rzut z góry na planszy: po lewej przegrody (nazwa, u), po prawej przejścia, punkty orientacyjne i strefy potworów
    (jak na planszy planu); z `strefy` na rzucie także place walki r 12, pętle, domy, otwarcia przejść i oś ścieżki."""
    ml, mt, mr, mb = 300, 104, 420, 70
    W, H = img.width + ml + mr, img.height + mt + mb
    out = Image.new("RGB", (W, H), (247, 243, 233))
    out.paste(img, (ml, mt))
    d = ImageDraw.Draw(out, "RGBA")
    f1, f2, f3, f4 = czcionka(30, True), czcionka(18), czcionka(17, True), czcionka(15)
    xr = ml + img.width + 16

    def px(u, v):
        x, y = rzut(u, v)
        return x + ml, y + mt
    d.text((18, 12), "Las jako wąski pas — rzut z góry z prawdziwych części" + (" · strefy potworów" if strefy else ""),
           fill=(40, 34, 30), font=f1)
    d.text((18, 54), "swiat/las_pas/czesci.json · u w górę (u góry brama do Bagna), v w prawo (prawa ręka idącego) · "
                     "skala 1 st = %g px" % (img.width / 180.0), fill=(110, 84, 60), font=f2)
    d.text((18, 78), "rysunek własny w Pillow z brył części — to NIE jest wygląd z Roblox (bez faktur, cieni i świateł)",
           fill=(150, 60, 40), font=f2)
    for q in plan["przegrody"]:
        _, y1 = px(q["u_od"], -90)
        _, y2 = px(q["u_do"], -90)
        d.line((ml - 10, y1, ml, y1), fill=(60, 50, 40, 255), width=2)
        d.line((ml - 10, y2, ml, y2), fill=(60, 50, 40, 255), width=2)
        d.text((14, (y1 + y2) / 2 - 22), q["nazwa"], fill=(40, 34, 30), font=f3)
        d.text((14, (y1 + y2) / 2), "u %d–%d" % (q["u_od"], q["u_do"]), fill=(110, 84, 60), font=f4)
    etykiety = []
    for t_ in plan["przejscia"]:
        etykiety.append(((t_["u_od"] + t_["u_do"]) / 2.0, t_["nazwa"], "otwarcie %d st" % (t_["otwarcie"][1] - t_["otwarcie"][0]),
                         (40, 90, 170)))
    for z_ in plan["punkty_orientacyjne"]:
        if z_["id"].endswith("_prawy"):
            continue
        etykiety.append((z_["u"], z_["nazwa"].replace(" (lewy)", "").replace(" (pień lewy)", ""), "wys. %d" % z_["wys"], (90, 70, 40)))
    if strefy:
        for st in plan["strefy"]:
            p = st["poziomy"]
            etykiety.append((st["srodek"][0], "%s · %s" % (st["id"], st["potwor"]),
                             "poz. %s · %d/%d naraz" % ("%d" % p[0] if p[0] == p[1] else "%d–%d" % tuple(p), st["naraz"], st["max"]),
                             (170, 40, 40)))
        etykiety.append((plan["straznik"]["miejsce"][0], "Strażnik Gaju", "poz. %d" % plan["straznik"]["poziom"], (170, 40, 40)))
    etykiety.sort(key=lambda e: -e[0])
    ostatni = -1e9
    for u, n1, n2, kol in etykiety:
        _, y = px(u, 0)
        y = max(y - 18, ostatni + 40)
        ostatni = y
        _, yu = px(u, 0)
        d.line((ml + img.width, yu, xr - 4, y + 12), fill=kol + (160,), width=1)
        d.text((xr, y), n1, fill=kol, font=f3)
        d.text((xr, y + 19), n2, fill=(110, 84, 60), font=f4)
    if strefy:
        rr = PLAC_R * (img.width / 180.0)
        for st in plan["strefy"]:
            tr = st["trasa"] + [st["trasa"][0]]
            d.line([px(u, v) for u, v in tr], fill=(255, 210, 40, 230), width=2)
            for u, v in st["trasa"]:
                x, y = px(u, v)
                d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(230, 40, 40, 200), width=2)
            for u, v in st["dom"]["pts"]:
                x, y = px(u, v)
                d.rectangle((x - 4, y - 4, x + 4, y + 4), fill=(170, 60, 230, 255))
        su, sv = plan["straznik"]["miejsce"]
        x, y = px(su, sv)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(230, 40, 40, 220), width=3)
        for t_ in plan["przejscia"]:
            a_ = px(t_["u_do"], t_["otwarcie"][0])
            b_ = px(t_["u_od"], t_["otwarcie"][1])
            d.rectangle((a_[0], a_[1], b_[0], b_[1]), outline=(40, 140, 255, 230), width=2)
        for a_, b_ in ODCINKI_SCIEZKI:
            pts = [px(u, v_sciezki(u)) for u in np.arange(a_, b_ + 0.1, 4.0)]
            d.line(pts, fill=(255, 255, 255, 160), width=1)
        for m in plan["miejsca"]:
            x, y = px(m["u"], m["v"])
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 60, 60, 255) if m["id"] == "przybycie" else (60, 200, 255, 255))
        d.text((ml, H - mb + 8), "czerwone koła: place walki r 12 · żółte: pętle potworów · fiolet: domy potworów",
               fill=(60, 50, 40), font=f4)
        d.text((ml, H - mb + 30), "niebieskie ramki: otwarcia przejść · biała kreska: oś ścieżki · kropki: miejsca z planu "
                                  "(czerwona = przybycie)", fill=(60, 50, 40), font=f4)
    return out


def zapisz_ujecia(plik):
    """Te same kadry w świecie Studio dla tools/studio_zrzuty.py (format: [nazwa, kamera, cel, ogniskowa, null]) —
    następny etap może porównać ten podgląd z prawdziwym zrzutem ze Studio z tego samego miejsca."""
    wyn = []
    for nazwa, (kam, cel, fov, _) in KADRY.items():
        ogn = round(12.0 / math.tan(math.radians(fov) / 2.0), 1)        # ogniskowa „35 mm” dla kąta w pionie
        wyn.append([nazwa, [X0 + kam[0], kam[1], Z0 + kam[2]], [X0 + cel[0], cel[1], Z0 + cel[2]], ogn, None])
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        f.write("[\n" + ",\n".join(" " + json.dumps(u, ensure_ascii=False) for u in wyn) + "\n]\n")


def main():
    ap = argparse.ArgumentParser(description="Podgląd lasu-pasa w Pillow (bez Blendera)")
    ap.add_argument("--json", default=os.path.join(TU, "czesci.json"))
    ap.add_argument("--wyj", default=os.path.join(TU, "podglad"))
    ap.add_argument("--tylko", default="")
    ap.add_argument("--skala-gory", type=float, default=3.0)
    ap.add_argument("--szer", type=int, default=1600)
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    os.makedirs(a.wyj, exist_ok=True)
    t0 = time.time()
    d, sciany = wczytaj(a.json)
    with open(os.path.join(REPO, "swiat", "biom_las", "pas", "plan_pasa.json"), encoding="utf-8") as f:
        plan = json.load(f)
    tylko = set(x for x in a.tylko.split(",") if x)
    print("PODGLĄD: %d części, %d ścian (%.1f s)" % (len(d["czesci"]), len(sciany), time.time() - t0))
    if not tylko or tylko & {"gora", "gora_strefy"}:
        t1 = time.time()
        img, rzut = kadr_gora(sciany, a.skala_gory)
        if not tylko or "gora" in tylko:
            plansza_gory(img, rzut, plan).save(os.path.join(a.wyj, "gora.jpg"), quality=88)
        if not tylko or "gora_strefy" in tylko:
            plansza_gory(img, rzut, plan, strefy=True).save(os.path.join(a.wyj, "gora_strefy.jpg"), quality=88)
        print("  gora (%.1f s)" % (time.time() - t1))
    H = int(a.szer * 0.625)
    for nazwa, (kam, cel, fov, opis) in KADRY.items():
        if tylko and nazwa not in tylko:
            continue
        t1 = time.time()
        img = kadr_perspektywa(sciany, (X0 + kam[0], kam[1], Z0 + kam[2]), (X0 + cel[0], cel[1], Z0 + cel[2]), fov, a.szer, H)
        podpis(img, opis, "kamera u %g, wys. %g, v %g → u %g · rysunek własny w Pillow, to NIE jest wygląd z Roblox"
               % (kam[0], kam[1], kam[2], cel[0])).save(os.path.join(a.wyj, nazwa + ".jpg"), quality=88)
        print("  %s (%.1f s)" % (nazwa, time.time() - t1))
    zapisz_ujecia(os.path.join(TU, "ujecia_swiat.json"))
    print("GOTOWE w %.0f s → %s (+ swiat/las_pas/ujecia_swiat.json dla tools/studio_zrzuty.py)"
          % (time.time() - t0, os.path.relpath(a.wyj, REPO).replace(os.sep, "/")))


if __name__ == "__main__":
    main()
