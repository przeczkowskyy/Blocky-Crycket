#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola offline KRÓTKICH map gry (D-096): swiat/las_pas/krotki i swiat/bagno_pas/krotki. Bez Studio i sieci.

    python -B swiat/biomy/kontrola_krotkich.py               # kod 1 = błąd
    python -B swiat/biomy/kontrola_krotkich.py --bez-sucho   # bez próby tools/studio_buduj.py --sucho

Długie mapy-projekty mają własne kontrole (swiat/las_pas/sprawdz.py, swiat/bagno_pas/sprawdz.py) z liczbami długiego
pasa. Tu te same zasady z liczbami krótkiego planu:
 1. pliki krotki/ aktualne (przycinarka); plan krótki: kontrola planu lasu (swiat/biom_las/pas/sprawdz_plan.py) albo
    część „plan” kontroli Bagna (swiat/bagno_pas/sprawdz.py);
 2. format tools/studio_buduj.py (jeden kontener biomu, wiersze, materiały) i jego tryb --sucho;
 3. granice: części biomu w jego odcinku pasa (|v| ≤ 90), nic na miasteczku i prototypach;
 4. zasady na prawdziwych częściach (swiat/las_pas/zasady.py): plac walki (promień z planu), otwarcia przejść, pętle
    potworów, przelot kamery;
 5. grunt bez dziur w polu gry, niewidzialne ściany boczne wzdłuż całego biomu, wrota bram, punkty E, domy stref;
 6. znaczniki zgodne z planem krótkim (strefy, węzły w świecie, przelot);
 7. styk lasu i Bagna: płyty gruntu i ściany boczne bez przerwy.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import types

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biomy import przycinarka as PR  # noqa: E402
from swiat.las_pas import sprawdz as SL  # noqa: E402
from swiat.las_pas import zasady as ZA  # noqa: E402
from swiat.las_pas.zasady import Zasady, aabb  # noqa: E402

V_GRANICA = 90.0
BIOMY = {
    "las": {"kontener": "Workspace/LasPas", "brama": "BramaBagna/Wrota", "miejsce_bramy": "brama_bagna",
            "klucz_bramy": "brama_bagna"},
    "bagno": {"kontener": "Workspace/BagnoPas", "brama": "BramaDzungli/Wrota", "miejsce_bramy": "brama_dzungli",
              "klucz_bramy": "brama_dzungli"},
}
PUNKTY_E = ("Punkty/KamienPowrotu/_Interakcja", "Punkty/StanowiskoJajka/_Interakcja")

bledy, uwagi = [], []


def blad(t):
    bledy.append(t)


def uwaga(t):
    uwagi.append(t)


def l1(x):
    return ("%.1f" % x).replace(".", ",")


def bez_kolizji(c):
    return len(c) > 15 and c[15] & 1


def _json(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------------------------------------------- 1. plan
def plan_lasu(sciezka):
    r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "swiat", "biom_las", "pas", "sprawdz_plan.py"),
                        os.path.join(REPO, sciezka), "--krotko"], capture_output=True, timeout=300, cwd=REPO,
                       env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    m = re.search(r"WYNIK: (\d+) błęd", out)
    if not m:
        blad("las: kontrola planu nie skończyła się (%s)" % out.strip()[-300:])
        return "?"
    for linia in out.splitlines():
        if linia.startswith("BŁĄD:"):
            blad("las, plan: " + linia[5:].strip())
    k = re.search(r"przelot kamery: ([^\n]+)", out)
    return k.group(1).strip() if k else "?"


def plan_bagna(P):
    from swiat.bagno_pas import sprawdz as SB
    SB.bledy.clear()
    SB.uwagi.clear()
    T, vmax, n = SB.sprawdz_plan(P)
    for t in SB.bledy:
        if not t.startswith("D-069"):          # liczy przegrody z trzema strefami — po scaleniu jest jedna (klasy_d069)
            blad("bagno, plan: " + t)
    klasy_d069("bagno", P)
    return "%s s, najszybciej %s st/s (%d próbek)" % (l1(T), l1(vmax), n)


# ------------------------------------------------------------------------------------------------------- 2–6. mapa
def mapa(b, P_przek, sucho=True):
    bid = b["id"]
    kont = BIOMY[bid]["kontener"]
    plan = _json(os.path.join(b["wyj"], b["plik_planu"]))
    zn = _json(os.path.join(b["wyj"], "znaczniki.json"))
    plik = os.path.join(REPO, b["wyj"], "czesci.json")
    with open(plik, encoding="utf-8") as f:
        d = json.load(f)
    grupy, mats, cz = d["grupy"], d["materialy"], d["czesci"]
    X0, Z0 = float(plan["swiat"]["X0"]), float(plan["swiat"]["Z0"])
    o = P_przek.biomy[bid]
    u_od, u_do = o.T(o.seg[0][0]), o.T(o.seg[-1][1])
    pol = plan["pas"]["szerokosc"] / 2.0
    sciana_v = P_przek.g(38.0)

    # 2. format + --sucho (te same funkcje co kontrola długiego lasu, z kontenerem biomu)
    SL.bledy.clear()
    SL.uwagi.clear()
    SL.KONTENER = kont
    SL.sprawdz_format(d)
    for t in SL.bledy:
        blad("%s, format: %s" % (bid, t))
    wynik_sucho = None
    if sucho:
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_buduj.py"), plik, "--sucho"],
                           capture_output=True, timeout=180, cwd=REPO, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        out = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
        if r.returncode != 0 or ("Kontener: " + kont) not in out:
            blad("%s: studio_buduj.py --sucho: kod %d, %s" % (bid, r.returncode, out[-300:]))
        wynik_sucho = out.splitlines()[-1] if out else ""

    # 3. granice i sufity
    if len(cz) > 12000:
        blad("%s: części %d > 12 000" % (bid, len(cz)))
    przezr = sum(1 for c in cz if 0 < c[13] < 0.98)
    if przezr > 20:
        uwaga("%s: półprzezroczystych %d > 20" % (bid, przezr))
    pudla = [("Krzywe Miasteczko", plan["swiat"]["miasteczko"]["zajete"])] if "miasteczko" in plan.get("swiat", {}) else []
    pudla += [(x["id"], x["xz"]) for x in plan.get("swiat", {}).get("zajete_inne", [])]
    poza = 0
    bb = [aabb(c) for c in cz]
    for c, (mn, mx) in zip(cz, bb):
        u1, u2, v1, v2 = mn[0] - X0, mx[0] - X0, mn[2] - Z0, mx[2] - Z0
        if u1 < u_od - 40 or u2 > u_do + 40 or v1 < -V_GRANICA or v2 > V_GRANICA or mn[1] < -4 or mx[1] > 120:
            poza += 1
            if poza <= 5:
                blad("%s: poza pasem „%s” u %s…%s, v %s…%s" % (bid, c[14], l1(u1), l1(u2), l1(v1), l1(v2)))
        for nazwa, (a1, a2, b1, b2) in pudla:
            if mn[0] < a2 and a1 < mx[0] and mn[2] < b2 and b1 < mx[2]:
                blad("%s: „%s” nachodzi na %s" % (bid, c[14], nazwa))

    # 4. zasady na częściach: plac walki (promień z planu krótkiego), otwarcia, pętle, przelot kamery
    K = types.SimpleNamespace(X0=X0, Z0=Z0, P=plan, strefy=plan["strefy"], straznik=plan["straznik"],
                              wezly=[tuple(w) for st in plan["strefy"] for w in st["trasa"]] + [tuple(plan["straznik"]["miejsce"])])
    Z = Zasady(K)
    plac_dawny = ZA.PLAC_R
    ZA.PLAC_R = float(plan["zasady"].get("plac_walki_r", plac_dawny))
    licz = {}
    try:
        for c in cz:
            g = grupy[c[1]]
            for t in Z.naruszenia(c, g, tylko=("plac", "otwarcie", "petla", "kamera")):
                if "/BramaDzungli/" in g and t.startswith("kamera"):
                    continue
                k = t.split(" (")[0] if not t.startswith("plac") else "plac walki"
                licz[k] = licz.get(k, 0) + 1
                if licz[k] <= 4:
                    blad("%s: %s: „%s” w %s" % (bid, t, c[14], g[len(kont) + 1:]))
    finally:
        ZA.PLAC_R = plac_dawny
    for k, v in licz.items():
        if v > 4:
            blad("%s: … %s: razem %d części" % (bid, k, v))

    # 5. grunt i ściany boczne — w main(), razem dla wszystkich biomów (płyta i ściany lasu sięgają w pas Bagna);
    #    tu: ściany w poprzek pola, wrota, punkty E, domy
    podlogi = [b_ for c, b_ in zip(cz, bb) if not bez_kolizji(c) and c[13] < 0.98 and -0.05 <= b_[1][1] <= 0.6]
    sciany = [(c, b_) for c, b_ in zip(cz, bb) if c[14] == "Niewidzialna ściana" and not bez_kolizji(c)]
    boczne = {zn_: [(b_[0][0] - X0, b_[1][0] - X0) for c, b_ in sciany
                    if abs(c[4] - Z0 - zn_ * sciana_v) < 1.01 and b_[1][1] >= 20] for zn_ in (-1, 1)}
    poprzeczne = [(b_[0][0] - X0, b_[1][0] - X0) for c, b_ in sciany if b_[0][2] - Z0 < -10 and b_[1][2] - Z0 > 10]
    for a_, b2 in poprzeczne:
        if not (b2 < o.T(o.kotwica) - 8 or a_ > o.T(o.brama) + 8):
            blad("%s: niewidzialna ściana w poprzek pola gry u %s…%s (między przybyciem a bramą)" % (bid, l1(a_), l1(b2)))
    obecne = {g[len(kont) + 1:] for g in (grupy[c[1]] for c in cz)}
    for g in PUNKTY_E:
        if g not in obecne:
            blad("%s: brak punktu E %s" % (bid, g))
    for e in zn.get("punkty_e", []):
        cz_e = [c for c in cz if grupy[c[1]] == "%s/%s/_Interakcja" % (kont, e["grupa"])]
        if cz_e and math.hypot(cz_e[0][2] - e["punkt_swiat"][0], cz_e[0][4] - e["punkt_swiat"][2]) > 0.05:
            blad("%s: punkt E %s: część (%s; %s), znacznik (%s; %s)" % (bid, e["grupa"], cz_e[0][2], cz_e[0][4],
                                                                     e["punkt_swiat"][0], e["punkt_swiat"][2]))
    for st in plan["strefy"]:
        if not any(x.startswith("Domy/%s" % st["id"]) for x in obecne):
            blad("%s: brak domu potworów strefy %s" % (bid, st["id"]))
    wrota = [(c, b_) for c, b_ in zip(cz, bb) if grupy[c[1]][len(kont) + 1:].startswith(BIOMY[bid]["brama"])
             and not bez_kolizji(c)]
    miejsca = {m["id"]: m for m in plan.get("miejsca", [])}
    mb = miejsca.get(BIOMY[bid]["miejsce_bramy"])
    if not wrota:
        blad("%s: brak wrót z kolizją w %s" % (bid, BIOMY[bid]["brama"]))
    elif mb and "otwarcie" in mb:
        o1, o2 = mb["otwarcie"]
        v, wys = o1, 99.0
        for a_, b2, h in sorted((b_[0][2] - Z0, b_[1][2] - Z0, b_[1][1]) for _, b_ in wrota):
            if a_ <= v + 0.3:
                v, wys = max(v, b2), min(wys, h)
        if v < o2 - 0.3 or wys < 7.0:
            blad("%s: wrota nie zamykają otwarcia v %s…%s (do v %s, wys. %s)" % (bid, o1, o2, l1(v), l1(wys)))

    # 6. znaczniki zgodne z planem
    if zn.get("kontener", {}).get("nazwa") != kont:
        blad("%s: znaczniki: kontener ≠ %s" % (bid, kont))
    ps = {st["id"]: st for st in plan["strefy"]}
    if sorted(s["id"] for s in zn.get("strefy", [])) != sorted(ps):
        blad("%s: znaczniki: strefy %s, w planie %s" % (bid, [s["id"] for s in zn.get("strefy", [])], sorted(ps)))
    for st in zn.get("strefy", []):
        p_ = ps.get(st["id"])
        if p_ and (len(st["wezly"]) != len(p_["trasa"]) or any(abs(w[0] - t[0]) > 1e-6 or abs(w[2] - t[1]) > 1e-6
                                                                 for w, t in zip(st["wezly"], p_["trasa"]))):
            blad("%s: znaczniki: węzły strefy %s różnią się od planu" % (bid, st["id"]))
        for w, ws in zip(st.get("wezly", []), st.get("wezly_swiat", [])):
            if abs(ws[0] - (X0 + w[0])) > 0.01 or abs(ws[2] - (Z0 + w[2])) > 0.01:
                blad("%s: znaczniki: zły przelicznik na świat w strefie %s" % (bid, st["id"]))
                break
    if zn.get("przelot_kamery", {}).get("punkty") != plan["przelot_kamery"]["punkty"]:
        blad("%s: znaczniki: przelot różni się od planu" % bid)
    for klucz in ("grupy_stale_wczytane", "grupy_niski_detal"):
        for g in (zn.get(klucz) or {}).get("grupy", []):
            if not any(x == g or x.startswith(g + "/") for x in obecne):
                blad("%s: znaczniki: grupa %s z %s nie istnieje w częściach" % (bid, g, klucz))
    return {"czesci": len(cz), "u": (u_od, u_do), "x": (min(b_[0][0] for b_ in bb), max(b_[1][0] for b_ in bb)),
            "sucho": wynik_sucho, "podlogi": [(mn - (X0, 0, Z0), mx - (X0, 0, Z0)) for mn, mx in podlogi],
            "boczne": boczne, "pol": pol, "przybycie": o.T(o.kotwica), "brama": o.T(o.brama)}


def klasy_d069(bid, plan):
    """D-069 na krótkim planie: w przegrodach ze scalonymi strefami każda klasa gracza ma swojego przeciwnika."""
    klasy = {st.get("klasa") for st in plan["strefy"] if st.get("scalone_z")}
    if klasy != {"Wojownik", "Zwiadowca", "Mag"}:
        blad("%s: D-069: przegrody mają mieć po jednym potworze każdej klasy (Wojownik, Zwiadowca, Mag) — są %s"
             % (bid, sorted(k for k in klasy if k)))


def ciaglosc(kaw, od, do):
    """Pierwsza przerwa w sumie odcinków [a, b] na przedziale od…do albo None."""
    v = od
    for a, b in sorted(kaw):
        if a > v + 0.05:
            return v, a
        v = max(v, b)
        if v >= do:
            return None
    return (v, do) if v < do else None


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kontrola offline krótkich map (D-096)")
    ap.add_argument("--bez-sucho", action="store_true")
    a = ap.parse_args()
    W = PR._json(PR.PLIK_WYMIAROW)
    P, pliki, _ = PR.wszystko(W)
    for sciezka, t in pliki.items():
        try:
            with open(sciezka, encoding="utf-8", newline="") as f:
                if f.read() != t:
                    blad("%s nieaktualny — uruchom python -B swiat/biomy/przycinarka.py" % os.path.relpath(sciezka, REPO))
        except OSError:
            blad("brak %s" % os.path.relpath(sciezka, REPO))
    wyn = {}
    for b in W["biomy"]:
        sciezka_planu = os.path.join(b["wyj"], b["plik_planu"])
        przelot = plan_lasu(sciezka_planu) if b["id"] == "las" else plan_bagna(_json(sciezka_planu))
        wyn[b["id"]] = mapa(b, P, sucho=not a.bez_sucho)
        wyn[b["id"]]["przelot"] = przelot
    # 5 i 7. grunt bez dziur i ściany boczne — razem dla wszystkich biomów (też styk lasu i Bagna)
    ids = [b["id"] for b in W["biomy"]]
    u_od = min(-3.0, wyn[ids[0]]["przybycie"] - 10)
    u_do = wyn[ids[-1]]["brama"] + 2
    pol = min(r["pol"] for r in wyn.values())
    podlogi = [p for r in wyn.values() for p in r["podlogi"]]
    GU, GV = np.meshgrid(np.arange(u_od, u_do, 2.0), np.arange(-(pol - 1.0), pol - 0.9, 2.0), indexing="ij")
    pokryte = np.zeros(GU.shape, dtype=bool)
    for mn, mx in podlogi:
        pokryte |= (GU >= mn[0]) & (GU <= mx[0]) & (GV >= mn[2]) & (GV <= mx[2])
    if (~pokryte).sum():
        i, j = np.argwhere(~pokryte)[0]
        blad("dziury w gruncie: %d punktów pola gry bez podłogi z kolizją (np. u %s, v %s)"
             % (int((~pokryte).sum()), l1(GU[i, j]), l1(GV[i, j])))
    for zn_ in (-1, 1):
        kaw = [k for r in wyn.values() for k in r["boczne"][zn_]]
        dz = ciaglosc(kaw, u_od, u_do)
        if dz:
            blad("niewidzialna ściana boczna (strona %+d): przerwa u %s…%s" % (zn_, l1(dz[0]), l1(dz[1])))
    print("KRÓTKIE MAPY (D-096) — kontrola")
    for bid, r in wyn.items():
        print("%-6s części %d · pas u %s…%s · świat X %s…%s · przelot: %s" % (
            bid, r["czesci"], l1(r["u"][0]), l1(r["u"][1]), l1(r["x"][0]), l1(r["x"][1]), r["przelot"]))
        if r["sucho"]:
            print("       studio_buduj.py --sucho: " + r["sucho"])
    print("sprawdzone: pliki aktualne, plan (las: sprawdz_plan.py; Bagno: kontrola planu Bagna), format, --sucho, granice, "
          "place walki (r z planu), otwarcia, pętle, przelot przez części, grunt bez dziur, ściany boczne, wrota, punkty E, "
          "domy stref, znaczniki, styk lasu i Bagna")
    for t in uwagi:
        print("OSTRZEŻENIE:", t)
    for t in bledy:
        print("BŁĄD:", t)
    print("WYNIK: %d błędów, %d ostrzeżeń" % (len(bledy), len(uwagi)))
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
