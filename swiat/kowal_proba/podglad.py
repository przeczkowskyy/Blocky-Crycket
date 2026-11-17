#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podglądy kuźni kowala w Blenderze (bez okna) — do pokazania Karolowi przed budową w Studio.

    python -B swiat/kowal_proba/podglad.py                  # wszystkie kadry → swiat/kowal_proba/podglad/*.jpg
    python -B swiat/kowal_proba/podglad.py --tylko przod     # wybrane kadry
    python -B swiat/kowal_proba/podglad.py --bez-renderu     # tylko scena (JSON w folderze roboczym) i liczby

Scena = kuźnia z kuznia/czesci.json (dane.py) + kowal z klocków (rig zrodla/RigKowal.luau w klatce uderzenia klipu
„kucie”, ustawiony jak w Studio: D.kuznia.kowal, D.kuznia.kowalRy) + otoczenie z mapy bazaru (części
swiat/miasteczko_bazar/czesci.json w pudełku wokół kuźni, tylko odczyt) — widać, gdzie kuźnia stoi wobec zbrojowni,
Wrót lochów i Bramy Leśnej. Render: tools/blender/klocki.py (ta sama geometria co Studio i panel), pod wspólną blokadą
Blendera; Blender bierze zmienną BLENDER_EXE, jak reszta repozytorium. To nie jest wygląd z Roblox (bez świecenia Neonu,
ognia i iskier — te dokłada Studio).
"""
import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (TU, REPO, os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402
from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender  # noqa: E402
from swiat.biblioteka.scena import katy_z_macierzy, macierz_obrotu, mnoz, razy_wektor  # noqa: E402

PODGLAD = os.path.join(TU, "podglad")
KLOCKI = os.path.join(REPO, "tools", "blender", "klocki.py")
I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
KLATKA_UDERZENIA = 14      # klatka modelu (30 kl./s) w klipie „kucie”


def _obr(rx, ry, rz):
    return macierz_obrotu(math.degrees(rx), math.degrees(ry), math.degrees(rz))


def _mul(a, b):
    v = razy_wektor(a[0], b[1])
    return (mnoz(a[0], b[0]), tuple(a[1][i] + v[i] for i in range(3)))


def _inv(a):
    Rt = tuple(tuple(a[0][j][i] for j in range(3)) for i in range(3))
    t = razy_wektor(Rt, a[1])
    return (Rt, (-t[0], -t[1], -t[2]))


def rig():
    import luau_mini as LM
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _s: True)
    game = LM.Tabela()
    game.set("GetService", lambda _s, _n: rs)
    it.globalne.z["game"] = game
    with open(os.path.join(TU, "zrodla", "RigKowal.luau"), encoding="utf-8") as f:
        return LM.z_luau(it.wykonaj(f.read(), "RigKowal.luau")[0])


def czesci_kowala(D, R, klip="kucie", klatka=KLATKA_UDERZENIA):
    """Bryły kowala w świecie w danej klatce klipu (jak RigKowala: C0 · Transform · C1⁻¹; model jak w zbuduj.py)."""
    kl = R["klipy"][klip]
    f = round(klatka / (30.0 / kl["fps"]))
    wiersz = kl["klatki"][min(f, len(kl["klatki"]) - 1)]
    tr = {}
    for j, ki in enumerate(kl["kosci"]):
        o = j * 6
        tr[ki] = (_obr(wiersz[o + 3], wiersz[o + 4], wiersz[o + 5]), (wiersz[o], wiersz[o + 1], wiersz[o + 2]))
    hrp = tuple(R["hrp"])
    kosci = {0: (I3, hrp)}
    for i, k in enumerate(R["kosci"], 1):
        rodzic, staw, srodek = k[1], k[2:5], k[5:8]
        srp = hrp if rodzic == 0 else tuple(R["kosci"][rodzic - 1][5:8])
        C0 = (I3, tuple(staw[a] - srp[a] for a in range(3)))
        C1 = (I3, tuple(staw[a] - srodek[a] for a in range(3)))
        kosci[i] = _mul(_mul(_mul(kosci[rodzic], C0), tr.get(i, (I3, (0, 0, 0)))), _inv(C1))
    kz = D["kuznia"]
    baza = (macierz_obrotu(0, kz["kowalRy"], 0), tuple(kz["kowal"]))
    w = []
    for c in R["czesci"]:
        ib = c[0]
        spoczynek = (I3, tuple(R["kosci"][ib - 1][5:8]))
        cf = _mul(baza, _mul(kosci[ib], _mul(_inv(spoczynek), (_obr(c[6], c[7], c[8]), tuple(c[3:6])))))
        w.append({"ks": c[1], "nazwa": "Kowal " + c[2], "cf": cf, "rozmiar": c[9:12], "kolor": c[12],
                  "material": R["materialy"][c[13]][0]})
    return w


def scena(D):
    """czesci.json do renderu: kuźnia + kowal + otoczenie z bazaru."""
    with open(DANE.PLIK_KUZNI, encoding="utf-8") as f:
        kuz = json.load(f)
    grupy, materialy, czesci = list(kuz["grupy"]), list(kuz["materialy"]), [list(c) for c in kuz["czesci"]]

    def idx(lista, v):
        if v not in lista:
            lista.append(v)
        return lista.index(v)
    g_kowal = idx(grupy, "Workspace/KowalProba/Kuznia/Kowal")
    for c in czesci_kowala(D, rig()):
        rx, ry, rz = katy_z_macierzy(c["cf"][0])
        p = c["cf"][1]
        czesci.append([c["ks"], g_kowal, round(p[0], 3), round(p[1], 3), round(p[2], 3), round(math.radians(rx), 4),
                       round(math.radians(ry), 4), round(math.radians(rz), 4)] + [round(v, 3) for v in c["rozmiar"]]
                      + [c["kolor"], idx(materialy, c["material"]), 0.0, c["nazwa"][:40]])
    baz = DANE._json(os.path.join(DANE.BAZAR, "czesci.json"))
    sx, _y, sz = D["kuznia"]["srodek"]
    mapa_g, mapa_m = {}, {}
    n = 0
    for c in baz["czesci"]:
        if abs(c[2] - sx) > 46 or abs(c[4] - sz) > 44 or "Niewidzialna" in c[14]:
            continue
        g, m = c[1], c[12]
        if g not in mapa_g:
            mapa_g[g] = idx(grupy, baz["grupy"][g])
        if m not in mapa_m:
            mapa_m[m] = idx(materialy, baz["materialy"][m])
        w = list(c)
        w[1], w[12] = mapa_g[g], mapa_m[m]
        czesci.append(w)
        n += 1
    return {"wersja": 1, "generator": "biblioteka-v2", "grupy": grupy, "materialy": materialy, "czesci": czesci}, n


def _lok(D, p):
    kz = D["kuznia"]
    a = math.radians(kz["ry"])
    s = kz["srodek"]
    return [round(s[0] + math.cos(a) * p[0] + math.sin(a) * p[2], 2), round(s[1] + p[1], 2),
            round(s[2] - math.sin(a) * p[0] + math.cos(a) * p[2], 2)]


def ujecia(D):
    """[nazwa, kamera, cel, ogniskowa mm, skala rzutu albo None] w układzie Roblox (świat)."""
    cel = _lok(D, (0, 3.2, 0))
    kw = D["kuznia"]["kowal"]
    uk = DANE._json(os.path.join(DANE.BAZAR, "uklad.json"))["swiat"]
    return [
        ["kuznia_przod", _lok(D, (0, 6.5, 18)), cel, 32, None],
        ["kuznia_34_lewo", _lok(D, (-5, 7, 14)), cel, 30, None],
        ["kuznia_34_prawo", _lok(D, (13, 8, 13)), cel, 32, None],
        ["kuznia_z_gory", _lok(D, (1, 26, 14)), _lok(D, (0, 1, 0)), 30, None],
        ["kowal_przy_kowadle", _lok(D, (-3.2, 5.0, 8.5)), [kw[0], kw[1] + 2.4, kw[2]], 40, None],
        ["kuznia_od_zbrojowni", [uk["X0"] + 50.5, 6.0, uk["Z0"] - 12.5], cel, 28, None],
        ["kuznia_w_bazarze", [uk["X0"] + 18.0, 16.0, uk["Z0"] - 6.0], _lok(D, (0, 3, 0)), 30, None],
    ]


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Podglądy kuźni kowala (Blender w tle)")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--szer", type=int, default=1280)
    ap.add_argument("--probki", type=int, default=32)
    ap.add_argument("--bez-renderu", action="store_true")
    a = ap.parse_args()
    D = DANE.dane_z_przypadkami()[0]
    sc, n_baz = scena(D)
    U = ujecia(D)
    if a.tylko:
        U = [u for u in U if any(t in u[0] for t in a.tylko.split(","))]
    rob = tempfile.mkdtemp(prefix="kowal_podglad_")
    plik = os.path.join(rob, "czesci.json")
    with open(plik, "w", encoding="utf-8") as f:
        json.dump(sc, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(rob, "ujecia.json"), "w", encoding="utf-8") as f:
        json.dump(U, f)
    print("scena: %d części (kuźnia i kowal %d, bazar %d), kadrów %d" % (len(sc["czesci"]), len(sc["czesci"]) - n_baz,
                                                                         n_baz, len(U)))
    if a.bez_renderu:
        shutil.rmtree(rob, ignore_errors=True)
        return 0
    wyj = os.path.join(rob, "render")
    os.makedirs(wyj, exist_ok=True)
    blokada = zajmij_blender()
    try:
        t0 = time.time()
        r = subprocess.run([blender_exe(), "-b", "--factory-startup", "--python-exit-code", "1", "--python", KLOCKI, "--",
                            "--z-json", plik, "--render", wyj, "--ujecia", os.path.join(rob, "ujecia.json"),
                            "--szer", str(a.szer), "--probki", str(a.probki)],
                           capture_output=True, timeout=30 * 60, creationflags=0x08000000 if os.name == "nt" else 0)
        if r.returncode != 0:
            print((r.stdout + r.stderr).decode("utf-8", "replace")[-3000:])
            return 1
        print("Blender: %.0f s" % (time.time() - t0))
    finally:
        zwolnij_blender(blokada)
    os.makedirs(PODGLAD, exist_ok=True)
    for nazwa in sorted(os.listdir(wyj)):
        if nazwa.endswith(".jpg"):
            shutil.copy(os.path.join(wyj, nazwa), os.path.join(PODGLAD, nazwa))
            print("  podglad/%s" % nazwa)
    shutil.rmtree(rob, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
