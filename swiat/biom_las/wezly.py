# -*- coding: utf-8 -*-
"""Wylicza węzły tras (miejsca walki) i domy potworów z maski terenu i zapisuje je w potwory.json.

    python -B swiat/biom_las/wezly.py            # pokaż wynik
    python -B swiat/biom_las/wezly.py --zapisz   # zapisz trasy i domy do potwory.json

Węzeł walki (PROJEKT.md rozdz. 6): grunt ±0,5 w promieniu 12 i na wysokości strefy, woda ≥ 12 (Oczko: ≥ 10), rdzeń
lokacji (wysokie rekwizyty, „rdzen” w uklad.json) ≥ 12, poza strefami spokoju i Sercem Boru ze smyczą 10, ≥ 12 od
ścieżek-ramp, w obrysie strefy. Węzły leżą na pętli wokół środka strefy; skrypt szuka promienia i obrotu pętli, a węzeł,
który nie pasuje, przesuwa najkrócej, jak się da. Dom (2–3 na strefę): 35–50 od najbliższego węzła i ≥ 35 od każdego,
poza ścieżkami, wodą i rdzeniami lokacji. Pojemność strefy = obwód pętli / odstęp 25; „max” nie może jej przekroczyć.
Jedna strefa ma węzły ustalone ręcznie: z09 (labirynt: plac wejścia, polanka środka, plac wyjścia).
"""
import argparse
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import geo  # noqa: E402

R_WALKI = 12.0
R_GRUNT = 15.5                  # płasko w r 14: skały urwisk wystają ok. 2 poza krawędź poziomu
WODA_MIN = 12.0
RECZNE = {"z09": [[-226, -197], [-200, -262], [-240, -313]]}
DOM_W_WODZIE = {"z01": [[250, 300], [247, 304], [253, 296]]}     # slime'y wyskakują z Oczka


class Maska:
    def __init__(self, U, P):
        self.U, self.P = U, P
        self.T = geo.Teren(U)
        self.pod = {b["id"]: b for b in U["podbiomy"]}
        self.spokoj = [s for s in U["strefy_spokoju"] if "srodek" in s]
        self.rdzenie = [(l["x"], l["z"], l.get("rdzen", 0), l["id"]) for l in U["lokacje"] if l.get("rdzen", 0) > 0]
        self.sciezki = U["sciezki"]

    def woda(self, x, z):
        return geo.woda_odl(self.U, x, z)

    def powod(self, x, z, y, strefa, woda_min=WODA_MIN):
        """Pusty napis = węzeł dobry; inaczej powód odrzucenia."""
        if max(abs(x), abs(z)) > 418:
            return "mur"
        lo, hi = self.T.plaskosc(x, z, R_GRUNT)
        if hi - lo > 0.5 or abs(lo - y) > 0.5:
            return "grunt %.1f–%.1f" % (lo, hi)
        if self.woda(x, z) < woda_min:
            return "woda"
        for lx, lz, r, lid in self.rdzenie:
            if lid in strefa.get("pomin_rdzen", ()):
                continue
            if math.hypot(x - lx, z - lz) < r + R_WALKI:
                return "rdzeń lokacji"
        for s in self.spokoj:
            if math.hypot(x - s["srodek"][0], z - s["srodek"][1]) < s["r"] + 10:
                return "strefa spokoju"
        if geo.odl_wielokat((x, z), self.pod["serce"]["wielokat"]) < 10:
            return "Serce Boru"
        if math.hypot(x - strefa["srodek"][0], z - strefa["srodek"][1]) > strefa["r"] - 2:
            return "poza strefą"
        return ""

    def powod_domu(self, x, z, y, wezly, strefa):
        if max(abs(x), abs(z)) > 420:
            return "mur"
        d = [math.hypot(x - a, z - b) for a, b, _ in wezly]
        if min(d) < 35 or min(d) > 50:
            return "odległość od węzłów"
        lo, hi = self.T.plaskosc(x, z, 4)
        if hi - lo > 0.5 or abs(lo - y) > 0.5:
            return "grunt"
        if self.woda(x, z) < 4:
            return "woda"
        if not geo.w_wielokacie((x, z), self.pod[strefa["podbiom"]]["wielokat"]):
            return "poza podbiomem"
        for s in self.sciezki:
            if geo.odl_lamana((x, z), s["pts"]) < s["szer"] / 2.0 + 4:
                return "ścieżka"
        for lx, lz, r, _ in self.rdzenie:
            if math.hypot(x - lx, z - lz) < r + 6:
                return "rdzeń lokacji"
        for s in self.spokoj:
            if math.hypot(x - s["srodek"][0], z - s["srodek"][1]) < s["r"] + 4:
                return "strefa spokoju"
        if geo.odl_wielokat((x, z), self.pod["serce"]["wielokat"]) < 4:
            return "Serce Boru"
        return ""


def popraw(maska, x, z, y, st, zajete, woda_min):
    """Najbliższy dobry punkt (spirala do 24 st), z dala ≥ 18 od zajętych węzłów."""
    for r in [0.0] + [2.0 * k for k in range(1, 13)]:
        n = 1 if r == 0 else int(6 + r)
        for k in range(n):
            a = 2 * math.pi * k / n
            px, pz = x + r * math.cos(a), z + r * math.sin(a)
            if any(math.hypot(px - qx, pz - qz) < 18 for qx, qz in zajete):
                continue
            if not maska.powod(px, pz, y, st, woda_min):
                return px, pz
    return None


def obwod(pts):
    return sum(math.dist(pts[i][:2], pts[(i + 1) % len(pts)][:2]) for i in range(len(pts))) if len(pts) > 1 else 0.0


def jednostki(st):
    g = st.get("grupa") or {}
    if "watahy" in g:
        return g.get("watahy", 0) + g.get("samotniki", 0)
    return st["max"]


def licz_strefe(maska, st):
    y = float(st["y"])
    cx, cz = st["srodek"]
    woda_min = 10.0 if st["id"] == "z01" else WODA_MIN
    if st["id"] in RECZNE:
        wezly = [(x, z, y) for x, z in RECZNE[st["id"]]]
    else:
        n = st.get("liczba_wezlow", 5)
        best = None
        for frac in (0.82, 0.75, 0.68, 0.6, 0.88, 0.52):
            for obrot in range(0, 360, 10):
                pts, zle = [], 0
                for k in range(n):
                    a = math.radians(obrot + 360.0 * k / n)
                    x, z = cx + st["r"] * frac * math.cos(a), cz + st["r"] * frac * math.sin(a)
                    if maska.powod(x, z, y, st, woda_min):
                        zle += 1
                    pts.append((x, z))
                wynik = (zle, -frac)
                if best is None or wynik < best[0]:
                    best = (wynik, pts)
            if best[0][0] == 0:
                break
        wezly = []
        for x, z in best[1]:
            if not maska.powod(x, z, y, st, woda_min) and all(math.hypot(x - a, z - b) >= 18 for a, b, _ in wezly):
                wezly.append((x, z, y))
                continue
            p = popraw(maska, x, z, y, st, [(a, b) for a, b, _ in wezly], woda_min)
            if p:
                wezly.append((p[0], p[1], y))
        # pętla w kolejności kąta wokół środka
        wezly.sort(key=lambda w: math.atan2(w[1] - cz, w[0] - cx))
    # domy
    domy = []
    if st["id"] in DOM_W_WODZIE:
        domy = [(x, z, y) for x, z in DOM_W_WODZIE[st["id"]]]
    else:
        kand = []
        for r in range(int(st["r"]) + 6, int(st["r"]) + 60, 3):
            for k in range(72):
                a = 2 * math.pi * k / 72
                x, z = cx + r * math.cos(a), cz + r * math.sin(a)
                if not maska.powod_domu(x, z, y, wezly, st):
                    kand.append((x, z))
        # 2–3 domy rozrzucone: najpierw najbliższy środkowi, potem najdalsze od wybranych
        if kand:
            kand.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cz))
            domy.append((kand[0][0], kand[0][1], y))
            while len(domy) < 3:
                q = max(kand, key=lambda p: min(math.hypot(p[0] - d[0], p[1] - d[1]) for d in domy))
                if min(math.hypot(q[0] - d[0], q[1] - d[1]) for d in domy) < 25:
                    break
                domy.append((q[0], q[1], y))
    return wezly, domy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zapisz", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    U, P = geo.wczytaj("uklad.json"), geo.wczytaj("potwory.json")
    maska = Maska(U, P)
    problemy = 0
    for st in P["strefy"]:
        wezly, domy = licz_strefe(maska, st)
        ob = obwod(wezly)
        poj = max(1, int(ob // P["zasady"]["odstep_min"])) if len(wezly) > 2 else len(wezly)
        brak = st.get("liczba_wezlow", len(wezly)) - len(wezly) if st["id"] not in RECZNE else 0
        uw = []
        if brak > 0:
            uw.append("brakuje %d węzłów" % brak)
        if jednostki(st) > poj:
            uw.append("max %d > pojemność %d" % (jednostki(st), poj))
        if len(domy) < 2:
            uw.append("tylko %d dom(y)" % len(domy))
        problemy += bool(uw)
        print("%s %-14s węzłów %d, obwód %4.0f → pojemność %2d (jednostek %2d), domów %d %s" % (
            st["id"], st["potwor"], len(wezly), ob, poj, jednostki(st), len(domy), ("  UWAGA: " + "; ".join(uw)) if uw else ""))
        st["trasa"] = [[round(x, 1), round(z, 1)] for x, z, _ in wezly]
        st["dom"]["pts"] = [[round(x, 1), round(z, 1)] for x, z, _ in domy]
        st["obwod"] = round(ob)
        st["pojemnosc"] = poj
    if a.zapisz:
        with open(os.path.join(TU, "potwory.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(P, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("zapisano potwory.json")
    return 1 if problemy else 0


if __name__ == "__main__":
    sys.exit(main())
