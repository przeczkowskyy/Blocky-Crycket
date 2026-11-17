#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola aren walki na gotowych plikach (<arena>/czesci.json + znaczniki.json) — bez Studio.

    python -B swiat/areny_walki/sprawdz.py            # wszystkie areny; kod wyjścia 1 = błąd
    python -B swiat/areny_walki/sprawdz.py --tylko las --szczegoly

Co sprawdza (BŁĄD = kod 1, UWAGA = tylko wypis):
 1. WOLNA PRZESTRZEŃ KAMER — żaden punkt bryły żadnej części (geom.punkty, chmura wypełniająca bryłę) nie leży
    w wolnej przestrzeni kamer (profil_kamer.json, kamery.py: kamery wszystkich par i ujęć + odcinki widoku do postaci)
    z zapasem 1 studa, a nad placem (r ≤ 22,3) nic poza gruntem (wierzch ≤ 0,12). Grunt i części niewidzialne nie łamią.
 2. BUDŻET — części ≤ plan.BUDZET (uwaga) i ≤ plan.BUDZET_TWARDY (błąd).
 3. HORYZONT — z kamer skrajnych (najdalsze w każdej ósemce kierunków, najwyższa, plan ogólny trzech par z obu stron,
    objazd co 30°) promienie co 1° w poziomie i co 0,5° w pionie od krawędzi gruntu do +HORYZONT_MIN° trafiają w bryłę
    albo w grunt — nigdzie nie widać pustego nieba nisko ani „końca świata”. Przecięcie promienia z bryłą dokładne
    (blok, klin, klin narożny i walec jako wielościany wypukłe, kula analitycznie).
 4. TŁO ZA POSTACIAMI — w planie ogólnym trzech par: kadr 160 × 90 promieni, prostokąt postaci +30 %: średni walor L*
    tła, udział bardzo jasnych (L* > 85) i Neonu (uwaga, gdy > 12 % / > 4 %).
 5. ZAKRES — wszystkie części w kole gruntu (+12), żadna > 2048, znaczniki zgodne z planem i z DaneAren.luau.
"""
import argparse
import json
import math
import os
import re
import sys
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import numpy as np  # noqa: E402

import geom  # noqa: E402
import kamery  # noqa: E402
import plan as P  # noqa: E402
from generuj import GRUNT_Y, naruszenia  # noqa: E402

HORYZONT_MIN = 2.0
JASNE_MAKS = 0.12
NEON_MAKS = 0.04


# --------------------------------------------------------------------------- bryły jako wielościany wypukłe
def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lstar(hexa):
    r, g, b = (_lin(int(hexa[i:i + 2], 16) / 255.0) for i in (0, 2, 4))
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    f = y ** (1 / 3) if y > 216 / 24389 else (24389 / 27 * y + 16) / 116
    return 116 * f - 16


def plaszczyzny(c):
    """(normalne (k,3), progi (k,)) — wnętrze: n·x ≤ d, w układzie pliku części; None dla kuli (osobno)."""
    ks = c[0]
    E = geom.polowki(c)
    hx, hy, hz = E
    if ks == geom.KULA:
        return None
    if ks == geom.WALEC:
        L = [((1, 0, 0), hx), ((-1, 0, 0), hx)]
        for i in range(12):
            a = 2 * math.pi * i / 12
            L.append(((0, math.cos(a), math.sin(a)), hy / math.cos(math.pi / 12)))
    elif ks == geom.KLIN:
        n = np.array((0.0, hz, -hy))
        n /= np.linalg.norm(n)
        L = [((1, 0, 0), hx), ((-1, 0, 0), hx), ((0, -1, 0), hy), ((0, 0, 1), hz), (tuple(n), 0.0)]
    elif ks == geom.NAROZNIK:
        n1 = np.array((-hy, hx, 0.0))
        n1 /= np.linalg.norm(n1)
        n2 = np.array((0.0, hz, hy))
        n2 /= np.linalg.norm(n2)
        # skosy przez wierzchołek P(hx, hy, −hz): n1·(x − P) ≤ 0, n2·(x − P) ≤ 0
        Pv = np.array((hx, hy, -hz))
        L = [((1, 0, 0), hx), ((0, 0, -1), hz), ((0, -1, 0), hy), (tuple(n1), float(n1 @ Pv)), (tuple(n2), float(n2 @ Pv))]
    else:
        L = [((1, 0, 0), hx), ((-1, 0, 0), hx), ((0, 1, 0), hy), ((0, -1, 0), hy), ((0, 0, 1), hz), ((0, 0, -1), hz)]
    R = geom.macierz(c[5], c[6], c[7])
    p = np.array((c[2], c[3], c[4]))
    N = np.array([l[0] for l in L], float) @ R.T
    D = np.array([l[1] for l in L], float) + N @ p
    return N, D


class Bryly:
    """Wszystkie widoczne części jako wielościany (tablice wyrównane do najdłuższej listy płaszczyzn) i kule."""

    def __init__(self, czesci, pomin=None):
        self.idx, Ns, Ds, kule = [], [], [], []
        for i, c in enumerate(czesci):
            if c[13] >= 0.98 or (pomin and pomin(c)):
                continue
            pl = plaszczyzny(c)
            if pl is None:
                kule.append((i, np.array((c[2], c[3], c[4])), min(c[8], c[9], c[10]) / 2.0))
                continue
            self.idx.append(i)
            Ns.append(pl[0])
            Ds.append(pl[1])
        k = max(len(n) for n in Ns)
        self.N = np.zeros((len(Ns), k, 3))
        self.D = np.full((len(Ns), k), 1e9)
        for j, (n, d) in enumerate(zip(Ns, Ds)):
            self.N[j, :len(n)] = n
            self.D[j, :len(d)] = d
        self.kule = kule

    def traf(self, o, U, t_maks=1e9, paczka=24):
        """Dla promieni z punktu o w kierunkach U (m,3): (najbliższe t, indeks części albo −1)."""
        m = len(U)
        best_t = np.full(m, np.inf)
        best_i = np.full(m, -1, dtype=np.int64)
        No = self.N @ o                                        # (p, k)
        for a in range(0, len(self.idx), paczka):
            N, D, no = self.N[a:a + paczka], self.D[a:a + paczka], No[a:a + paczka]
            nu = np.einsum("pkj,mj->pmk", N, U)                # (p, m, k)
            licz = (D - no)[:, None, :]                        # (p, 1, k)
            with np.errstate(divide="ignore", invalid="ignore"):
                t = licz / nu
            wej = np.where(nu < -1e-12, t, -np.inf).max(axis=2)
            wyj = np.where(nu > 1e-12, t, np.inf).min(axis=2)
            rown = (np.abs(nu) <= 1e-12) & (licz < 0)          # równoległy i na zewnątrz
            zle = rown.any(axis=2)
            wej = np.maximum(wej, 0.0)
            traf = (wej <= wyj) & ~zle & (wyj > 0) & (wej < t_maks)
            tt = np.where(traf, wej, np.inf)                   # (p, m)
            j = tt.argmin(axis=0)
            tj = tt[j, np.arange(m)]
            lep = tj < best_t
            best_t[lep] = tj[lep]
            best_i[lep] = np.array(self.idx)[a + j[lep]]
        for i, cen, r in self.kule:
            oc = o - cen
            b = U @ oc
            cc = oc @ oc - r * r
            disk = b * b - cc
            ok = disk >= 0
            t = -b - np.sqrt(np.where(ok, disk, 0.0))
            t = np.where(t < 0, -b + np.sqrt(np.where(ok, disk, 0.0)), t)
            lep = ok & (t > 0) & (t < best_t)
            best_t[lep] = t[lep]
            best_i[lep] = i
        return best_t, best_i


# --------------------------------------------------------------------------- dane areny
def wczytaj(klucz):
    with open(os.path.join(TU, klucz, "czesci.json"), encoding="utf-8") as f:
        d = json.load(f)
    with open(os.path.join(TU, klucz, "znaczniki.json"), encoding="utf-8") as f:
        z = json.load(f)
    O = P.ARENY[klucz]["O"]
    sc = [geom.do_sceny(c, O) for c in d["czesci"]]
    return d, z, sc


def kamery_skrajne():
    """Kamery do kontroli horyzontu: najdalsze w każdej ósemce kierunków, najwyższa, plany ogólne, objazd co 30°."""
    akt = kamery.aktorzy()
    wszystkie = []
    for gk, wk in kamery.pary(akt):
        for poz, _ in kamery.kamery_pary(akt[gk], akt[wk]):
            wszystkie.append(poz)
    A = np.array(wszystkie)
    wynik = []
    kat = (np.degrees(np.arctan2(A[:, 2], A[:, 0])) % 360) // 45
    r = np.hypot(A[:, 0], A[:, 2])
    for o in range(8):
        m = kat == o
        if m.any():
            wynik.append(tuple(A[m][r[m].argmax()]))
    wynik.append(tuple(A[A[:, 1].argmax()]))
    for gk, wk in (("wojownik", "lesny_slime"), ("wojownik", "lesny_troll"), ("mag", "straznik_topieli")):
        g = kamery.geometria(akt[gk], akt[wk])
        poz, cel, kat_, _ = kamery.ujecie(g, "ogolny", "gracz", "wrog", 0.0)
        wynik += [poz, (poz[0], poz[1], -poz[2])]
    for a in range(0, 360, 30):
        wynik.append((-6.0 + 14.0 * math.cos(math.radians(a)), 4.7, 14.0 * math.sin(math.radians(a))))
    return wynik


def horyzont(bryly, y_gruntu, kam):
    """Najniższe „domknięcie” horyzontu (°) po wszystkich azymutach z kamery kam i azymut, w którym jest."""
    c = np.array(kam, float)
    el_max = HORYZONT_MIN
    A, E, EG = [], [], []
    for a in np.radians(np.arange(0.0, 360.0, 1.0)):
        u = (math.cos(a), math.sin(a))
        b = c[0] * u[0] + c[2] * u[1]
        t = -b + math.sqrt(max(0.0, b * b - (c[0] ** 2 + c[2] ** 2 - P.R_GRUNT ** 2)))
        e_g = math.degrees(math.atan2(y_gruntu - c[1], t))
        for e in np.arange(math.floor(e_g * 2) / 2.0, el_max + 0.25, 0.5):
            A.append(a)
            E.append(e)
            EG.append(e_g)
    A, E, EG = np.array(A), np.radians(np.array(E)), np.array(EG)
    U = np.stack((np.cos(E) * np.cos(A), np.sin(E), np.cos(E) * np.sin(A)), axis=1)
    tt, _ = bryly.traf(c, U)
    E = np.degrees(E)
    dziury = ~np.isfinite(tt) & (E > EG + 0.01)
    if not dziury.any():
        return el_max, None
    j = np.argmin(np.where(dziury, E, np.inf))
    return float(E[j]) - 0.5, round(float(np.degrees(A[j])), 1)


def tlo(bryly, czesci_sw, materialy, kam, cel, fov, prost):
    """Statystyka tła za postaciami w kadrze (W 160 × H 90): (średni L*, udział jasnych, udział Neonu, trafień)."""
    W, H = 160, 90
    c = np.array(kam, float)
    f = np.array(cel, float) - c
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 1.0, 0.0))
    r /= np.linalg.norm(r)
    up = np.cross(r, f)
    tv = math.tan(math.radians(fov) / 2.0)
    th = tv * 16 / 9
    x0, x1, y0, y1 = prost
    xs = np.linspace(-1, 1, W)
    ys = np.linspace(1, -1, H)
    X, Y = np.meshgrid(xs, ys)
    m = (X >= x0) & (X <= x1) & (Y >= y0) & (Y <= y1)
    D = f[None, :] + (X[m] * th)[:, None] * r[None, :] + (Y[m] * tv)[:, None] * up[None, :]
    D /= np.linalg.norm(D, axis=1)[:, None]
    _, idx = bryly.traf(c, D)
    ls, jasne, neon, n = [], 0, 0, 0
    for i in idx:
        if i < 0:
            continue
        cz = czesci_sw[i]
        L = lstar(cz[11])
        ls.append(L)
        jasne += L > 85
        neon += materialy[cz[12]] == "Neon"
        n += 1
    if not n:
        return 0.0, 0.0, 0.0, 0
    return float(np.mean(ls)), jasne / n, neon / n, n


def prostokat_postaci(g, kam, cel, fov):
    """Prostokąt (−1…1) obu postaci w kadrze + 30 %."""
    c = np.array(kam, float)
    f = np.array(cel, float) - c
    f /= np.linalg.norm(f)
    r = np.cross(f, (0.0, 1.0, 0.0))
    r /= np.linalg.norm(r)
    up = np.cross(r, f)
    tv = math.tan(math.radians(fov) / 2.0)
    th = tv * 16 / 9
    xs, ys = [], []
    for s in ("gracz", "wrog"):
        for dx in (-0.5, 0.5):
            for y in (0.0, g["h"][s]):
                p = np.array((g["x"][s] + dx * g["w"][s], y, 0.0)) - c
                z = p @ f
                xs.append((p @ r) / (z * th))
                ys.append((p @ up) / (z * tv))
    sx, sy = (max(xs) - min(xs)) * 0.15, (max(ys) - min(ys)) * 0.15
    return min(xs) - sx, max(xs) + sx, min(ys) - sy, max(ys) + sy


# --------------------------------------------------------------------------- kontrola jednej areny
def sprawdz(klucz, prof, kam_horyzontu, szczegoly=False):
    t0 = time.time()
    d, z, sc = wczytaj(klucz)
    A = P.ARENY[klucz]
    bledy, uwagi, wyniki = [], [], {}
    # 1. wolna przestrzeń
    nar = naruszenia(sc, prof)
    wyniki["wolna_przestrzen"] = {"naruszen": len(nar), "przyklady": nar[:8]}
    if nar:
        bledy.append("%d części w wolnej przestrzeni kamer albo nad placem, np. %s" % (len(nar), nar[:5]))
    # 2. budżet
    n = len(d["czesci"])
    wyniki["czesci"] = n
    if n > P.BUDZET_TWARDY:
        bledy.append("budżet twardy przekroczony: %d > %d" % (n, P.BUDZET_TWARDY))
    elif n > P.BUDZET:
        uwagi.append("budżet przekroczony: %d > %d" % (n, P.BUDZET))
    # 5. zakres i zgodność
    for c in d["czesci"]:
        if max(c[8], c[9], c[10]) > 2048:
            bledy.append("część > 2048: %s" % c[14])
    O = A["O"]
    rr = max(math.hypot(c[2] - O[0], c[4] - O[2]) for c in d["czesci"])
    if rr > P.R_GRUNT + 12:
        bledy.append("część poza kołem gruntu: r %.0f" % rr)
    if z["scena"]["pozycja"] != list(O) or z["model"] != "Workspace/ArenyWalki/" + A["model"] or z["czesci"] != n:
        bledy.append("znaczniki.json niezgodne z planem albo z czesci.json (wygeneruj ponownie)")
    luau = open(os.path.join(TU, "zrodla", "DaneAren.luau"), encoding="utf-8").read()
    m = re.search(r"\n\t\t%s = \{\n(.*?)\n\t\t\},?\n" % klucz, luau, re.S)
    if not m or ("czesci = %d," % n) not in m.group(1):
        bledy.append("zrodla/DaneAren.luau niezgodne z czesci.json (wygeneruj ponownie)")
    # 3. horyzont
    bryly = Bryly(sc, pomin=lambda c: geom.gora(c) <= A["grunt"]["y"] + 0.15 and max(c[8], c[10]) > 200)
    najg = (99.0, None, None)
    for k in kam_horyzontu:
        e, a = horyzont(bryly, A["grunt"]["y"], k)
        if e < najg[0]:
            najg = (e, a, k)
    wyniki["horyzont"] = {"najnizsze_domkniecie_st": round(najg[0], 2), "azymut": najg[1],
                          "kamera": [round(v, 1) for v in najg[2]] if najg[2] else None, "kamer": len(kam_horyzontu)}
    if najg[0] < HORYZONT_MIN - 1e-6:
        bledy.append("horyzont otwarty: z kamery %s w kierunku %s° domknięcie tylko do %.1f° (wymagane %.1f°)"
                     % ([round(v, 1) for v in najg[2]], najg[1], najg[0], HORYZONT_MIN))
    # 4. tło za postaciami (plan ogólny trzech par)
    akt = kamery.aktorzy()
    tla = []
    for gk, wk in (("wojownik", "lesny_slime"), ("wojownik", "lesny_troll"), ("mag", "straznik_topieli")):
        g = kamery.geometria(akt[gk], akt[wk])
        poz, cel, kat, _ = kamery.ujecie(g, "ogolny", "gracz", "wrog", 0.0)
        for strona in (1, -1):
            p2 = (poz[0], poz[1], strona * poz[2])
            pr = prostokat_postaci(g, p2, cel, kat)
            L, jas, neo, ile = tlo(bryly, sc, d["materialy"], p2, cel, kat, pr)
            tla.append({"para": "%s/%s" % (gk, wk), "strona": "przod" if strona > 0 else "tyl", "L_srednie": round(L, 1),
                        "jasne": round(jas, 3), "neon": round(neo, 3), "promieni": ile})
            if jas > JASNE_MAKS or neo > NEON_MAKS:
                uwagi.append("tło za postaciami (%s, %s): jasne %.0f %%, Neon %.0f %%" % (gk + "/" + wk, tla[-1]["strona"], jas * 100, neo * 100))
    wyniki["tlo"] = tla
    wyniki["czas_s"] = round(time.time() - t0, 1)
    return bledy, uwagi, wyniki


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kontrola aren walki")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--szczegoly", action="store_true")
    ap.add_argument("--json", default=None, help="zapisz wyniki do pliku JSON")
    a = ap.parse_args()
    prof = kamery.profil()
    kam = kamery_skrajne()
    razem_bledow = 0
    wszystkie = {}
    for klucz in P.ARENY:
        if a.tylko and klucz not in a.tylko.split(","):
            continue
        bledy, uwagi, w = sprawdz(klucz, prof, kam, a.szczegoly)
        wszystkie[klucz] = {"bledy": bledy, "uwagi": uwagi, "wyniki": w}
        tl = w["tlo"]
        print("%-6s części %4d/%d · wolna przestrzeń: %d naruszeń · horyzont domknięty do ≥ %.1f° (%d kamer) · tło L* %s · %.0f s"
              % (klucz, w["czesci"], P.BUDZET, w["wolna_przestrzen"]["naruszen"], w["horyzont"]["najnizsze_domkniecie_st"],
                 w["horyzont"]["kamer"], "/".join("%.0f" % t["L_srednie"] for t in tl), w["czas_s"]))
        for b in bledy:
            print("   BŁĄD:", b)
        for u in uwagi:
            print("   UWAGA:", u)
        if a.szczegoly:
            print(json.dumps(w, ensure_ascii=False, indent=1))
        razem_bledow += len(bledy)
    if a.json:
        with open(a.json, "w", encoding="utf-8", newline="\n") as f:
            json.dump(wszystkie, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print("WYNIK:", "OK" if not razem_bledow else "%d błędów" % razem_bledow)
    return 1 if razem_bledow else 0


if __name__ == "__main__":
    sys.exit(main())
