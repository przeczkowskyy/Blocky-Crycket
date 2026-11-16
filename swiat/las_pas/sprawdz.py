#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kontrola offline lasu-pasa (swiat/las_pas/czesci.json + znaczniki.json). Nie dotyka Studio ani sieci.

    python -B swiat/las_pas/sprawdz.py                  # kontrola (kod 1 = błąd)
    python -B swiat/las_pas/sprawdz.py --bez-sucho      # bez próby `tools/studio_buduj.py --sucho`
    python -B swiat/las_pas/sprawdz.py INNY.json        # inny plik części

Sprawdza:
 1. format, którego wymaga tools/studio_buduj.py (jeden kontener Workspace/LasPas, wiersze 15/16 pól, typy, indeksy grup
    i materiałów, nazwy Enum.Material, kolory RRGGBB, cechy w 16. polu) + jego tryb `--sucho` (czyta plik i kończy
    przed połączeniem ze Studio);
 2. rozmiary części > 0 (najmniej 0,05), liczby skończone; limit części (twardy 12 000) i sufity (Neon, kule, walce,
    półprzezroczyste);
 3. granice: każda część w pasie z kulisami i tłem (u −34…966, |v| ≤ 90, X ≥ 1066) i nic nie nachodzi na miasteczko,
    stary las, oba prototypy walki ani Baseplate (te same skrzynki co w swiat/biom_las/pas/sprawdz_plan.py);
 4. zasady na prawdziwych częściach (swiat/las_pas/zasady.py): place walki r 12, ścieżka, otwarcia przejść, pętle
    potworów, przelot kamery;
 5. grunt płaski bez dziur (płyta z kolizją pod całym pasem, wierzch 0), woda bez kolizji, niewidzialne ściany, brama do
    Bagna jako osobna grupa z wrotami zamykającymi otwarcie, punkty E (Kamień Powrotu, stanowisko jajka), obecność
    wszystkich przegród, przejść, punktów orientacyjnych i domów potworów;
 6. znaczniki.json zgodne z planem i z swiat/biom_las/studio_atrybuty.py (streaming grup), faktury: każda część ma rolę.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys

import numpy as np

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.biblioteka.scena import MATERIALY  # noqa: E402
from swiat.biom_las import faktury  # noqa: E402
from swiat.las_pas.generuj import FAKTURY_DODATKOWE, LIMIT, CEL, ODCINKI_RAPORTU, odcinek_raportu  # noqa: E402
from swiat.las_pas.kontekst import KONTENER, Pas, U_MAX, U_MIN  # noqa: E402
from swiat.las_pas.zasady import Zasady, aabb  # noqa: E402

HEX = re.compile(r"^[0-9A-F]{6}$")
V_GRANICA = 90.0
WYMAGANE_GRUPY = [
    "Punkty/BramaPniakow", "Punkty/KamienPowrotu", "Punkty/StanowiskoJajka", "Punkty/Pasnik", "Punkty/WielkiKapelusz",
    "Punkty/WilczaSkala", "Punkty/GlazyLegowiska", "Punkty/BramaMenhirow", "Punkty/FilarKrysztal",
    "Polana/KragPrzybycia", "Przejscia/PlotZFurtka", "Przejscia/Strumyk/Mostek", "Przejscia/Strumyk/Woda",
    "Przejscia/Strumyk/Brod", "Przejscia/JezynoweZwezenie", "Przejscia/KamiennyProg", "Przejscia/BramaMenhirow",
    "Zagroda/Plot", "Zagroda/Przegrodki", "Arena/Krag", "BramaBagna/Palisada", "BramaBagna/Wrota", "Kulisy/Niewidzialne",
    "Kulisy/ScianaZamykajaca", "Sciezka", "Teren/Grunt",
]

bledy, uwagi = [], []


def blad(t):
    bledy.append(t)


def uwaga(t):
    uwagi.append(t)


def l1(x):
    return ("%.1f" % x).replace(".", ",")


def sprawdz_format(d):
    """To, co tools/studio_buduj.py czyta z pliku (main + PACZKA w Luau)."""
    for k in ("grupy", "materialy", "czesci"):
        if k not in d or not isinstance(d[k], list):
            blad("format: brak listy „%s”" % k)
            return None
    grupy, mats, cz = d["grupy"], d["materialy"], d["czesci"]
    korzenie = {g.split("/")[1] for g in grupy if isinstance(g, str) and g.startswith("Workspace/") and g.count("/") >= 1}
    if len(korzenie) != 1 or any(not (isinstance(g, str) and g.startswith(KONTENER + "/")) for g in grupy):
        blad("format: grupy nie leżą w jednym kontenerze %s (korzenie: %s)" % (KONTENER, sorted(korzenie)))
    if d.get("generator") != "biblioteka-v2":
        blad("format: brak generator = biblioteka-v2 (studio_buduj czyta wtedy cechy z 16. pola)")
    for m in mats:
        if m not in MATERIALY:
            blad("format: materiał %r spoza Enum.Material znanych bibliotece" % m)
    zle = 0
    for i, c in enumerate(cz):
        powod = None
        if not isinstance(c, list) or len(c) not in (15, 16):
            powod = "wiersz ma %s pól (ma być 15 albo 16)" % (len(c) if isinstance(c, list) else "?")
        elif not isinstance(c[0], int) or not 0 <= c[0] <= 4:
            powod = "kształt %r spoza 0–4" % (c[0],)
        elif not isinstance(c[1], int) or not 0 <= c[1] < len(grupy):
            powod = "indeks grupy %r" % (c[1],)
        elif not all(isinstance(x, (int, float)) and math.isfinite(x) for x in c[2:11]):
            powod = "pozycja/obrót/rozmiar nie są skończonymi liczbami"
        elif not isinstance(c[11], str) or not HEX.match(c[11]):
            powod = "kolor %r (ma być RRGGBB wielkimi literami)" % (c[11],)
        elif not isinstance(c[12], int) or not 0 <= c[12] < len(mats):
            powod = "indeks materiału %r" % (c[12],)
        elif not isinstance(c[13], (int, float)) or not 0 <= c[13] <= 1:
            powod = "przezroczystość %r" % (c[13],)
        elif not isinstance(c[14], str) or not c[14] or len(c[14]) > 40:
            powod = "nazwa %r (1–40 znaków)" % (c[14],)
        elif len(c) == 16 and (not isinstance(c[15], int) or not 0 <= c[15] <= 3):
            powod = "cechy %r (0–3)" % (c[15],)
        elif min(c[8], c[9], c[10]) <= 0:
            powod = "rozmiar zerowy albo ujemny %s" % (c[8:11],)
        elif min(c[8], c[9], c[10]) < 0.05:
            powod = "rozmiar < 0,05 %s" % (c[8:11],)
        if powod:
            zle += 1
            if zle <= 10:
                blad("część %d „%s”: %s" % (i, c[14] if isinstance(c, list) and len(c) > 14 else "?", powod))
    if zle > 10:
        blad("… i jeszcze %d złych wierszy" % (zle - 10))
    return korzenie.pop() if len(korzenie) == 1 else None


def studio_sucho(plik):
    """tools/studio_buduj.py --sucho: wczytuje plik, wypisuje kontener i liczby, kończy PRZED połączeniem ze Studio."""
    try:
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, "tools", "studio_buduj.py"), plik, "--sucho"],
                           capture_output=True, timeout=120, cwd=REPO, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    except Exception as e:  # noqa: BLE001
        uwaga("studio_buduj.py --sucho nie ruszył: %s" % e)
        return None
    out = (r.stdout + r.stderr).decode("utf-8", "replace").strip()
    if r.returncode != 0 or "Kontener: Workspace/LasPas" not in out:
        blad("studio_buduj.py --sucho: kod %d, wyjście: %s" % (r.returncode, out[-300:]))
    return out


def main():
    ap = argparse.ArgumentParser(description="Kontrola offline lasu-pasa")
    ap.add_argument("plik", nargs="?", default=os.path.join(TU, "czesci.json"))
    ap.add_argument("--znaczniki", default=os.path.join(TU, "znaczniki.json"))
    ap.add_argument("--bez-sucho", action="store_true")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    with open(a.plik, encoding="utf-8") as f:
        d = json.load(f)
    K = Pas()
    Z = Zasady(K)
    P = K.P
    X0, Z0 = K.X0, K.Z0
    grupy, mats, cz = d["grupy"], d["materialy"], d["czesci"]
    print("LAS-PAS — kontrola (%s)" % os.path.relpath(a.plik, REPO).replace(os.sep, "/"))

    # 1. format
    sprawdz_format(d)
    sucho = None if a.bez_sucho else studio_sucho(a.plik)
    if bledy:
        for t in bledy:
            print("BŁĄD:", t)
        print("WYNIK: %d błędów (format) — dalsza kontrola przerwana" % len(bledy))
        return 1

    # 2. liczby i sufity
    n = len(cz)
    if n > LIMIT:
        blad("części %d > twardy limit %d" % (n, LIMIT))
    elif n > CEL * 1.15:
        uwaga("części %d — więcej niż cel ok. %d" % (n, CEL))
    neon = sum(1 for c in cz if mats[c[12]] == "Neon")
    kule = sum(1 for c in cz if c[0] == 1)
    walce = sum(1 for c in cz if c[0] == 2)
    przezr = sum(1 for c in cz if 0 < c[13] < 0.98)
    niewid = sum(1 for c in cz if c[13] >= 0.98)
    for nazwa, ile, mx in (("Neon", neon, 300), ("kule", kule, 300), ("walce", walce, 3000), ("półprzezroczyste", przezr, 20)):
        if ile > mx:
            blad("%s: %d > %d" % (nazwa, ile, mx))

    # 3. granice
    pudla = [("Krzywe Miasteczko", P["swiat"]["miasteczko"]["zajete"])] + [(o["id"], o["xz"]) for o in P["swiat"]["zajete_inne"]]
    poza = 0
    mn_all, mx_all = np.full(3, 1e9), np.full(3, -1e9)
    for i, c in enumerate(cz):
        mn, mx = aabb(c)
        mn_all, mx_all = np.minimum(mn_all, mn), np.maximum(mx_all, mx)
        u1, u2, v1, v2 = mn[0] - X0, mx[0] - X0, mn[2] - Z0, mx[2] - Z0
        if u1 < U_MIN - 0.05 or u2 > U_MAX + 0.05 or v1 < -V_GRANICA or v2 > V_GRANICA or mn[1] < -4.0 or mx[1] > 120:
            poza += 1
            if poza <= 8:
                blad("poza pasem: „%s” (%s) u %s…%s, v %s…%s, y %s…%s" % (c[14], grupy[c[1]][len(KONTENER) + 1:], l1(u1), l1(u2),
                                                                       l1(v1), l1(v2), l1(mn[1]), l1(mx[1])))
        for nazwa, (a1, a2, b1, b2) in pudla:
            if mn[0] < a2 and a1 < mx[0] and mn[2] < b2 and b1 < mx[2]:
                blad("„%s” nachodzi na %s" % (c[14], nazwa))
    if poza > 8:
        blad("… i jeszcze %d części poza pasem" % (poza - 8))

    # 4. zasady na częściach
    licz = {}
    for c in cz:
        for t in Z.naruszenia(c, grupy[c[1]], tylko=("plac", "sciezka", "otwarcie", "petla", "kamera")):
            klucz = t.split(" (")[0] if not t.startswith("plac") else "plac walki"
            licz[klucz] = licz.get(klucz, 0) + 1
            if licz[klucz] <= 6:
                blad("%s: „%s” w %s" % (t, c[14], grupy[c[1]][len(KONTENER) + 1:]))
    for k, v in licz.items():
        if v > 6:
            blad("… %s: razem %d części" % (k, v))

    # 5. grunt, woda, ściany, brama, punkty E, obecność
    def gr(c):
        return grupy[c[1]][len(KONTENER) + 1:]
    plyty = [c for c in cz if c[14] == "Płyta" and not (len(c) > 15 and c[15] & 1)]
    if not plyty:
        blad("brak płyty gruntu z kolizją")
    else:
        mn, mx = aabb(plyty[0])
        if not (mn[0] - X0 <= -24 and mx[0] - X0 >= 964 and mn[2] - Z0 <= -40 and mx[2] - Z0 >= 40 and abs(mx[1]) < 0.01):
            blad("płyta nie przykrywa pasa (u −24…964, |v| ≤ 40) albo jej wierzch nie leży na y = 0")
    # brak dziur: każdy punkt pola gry co 2 st ma pod sobą część z kolizją o wierzchu w −0,05…0,6
    podlogi = [aabb(c) for c in cz if not (len(c) > 15 and c[15] & 1) and c[13] < 0.98 and aabb(c)[1][1] <= 0.6 and aabb(c)[1][1] >= -0.05]
    GU, GV = np.meshgrid(np.arange(-3.0, 963.0, 2.0) + X0, np.arange(-37.0, 37.1, 2.0) + Z0, indexing="ij")
    pokryte = np.zeros(GU.shape, dtype=bool)
    for mn, mx in podlogi:
        pokryte |= (GU >= mn[0]) & (GU <= mx[0]) & (GV >= mn[2]) & (GV <= mx[2])
    dziury = int((~pokryte).sum())
    if dziury:
        blad("dziury w gruncie: %d punktów pola gry bez podłogi z kolizją" % dziury)
    teren_nierowny = [c for c in cz if not (len(c) > 15 and c[15] & 1) and "/Teren/" in grupy[c[1]] and abs(aabb(c)[1][1]) > 0.01]
    if teren_nierowny:
        blad("teren nie jest płaski: %d części gruntu z kolizją ma wierzch ≠ 0" % len(teren_nierowny))
    woda_kol = [c for c in cz if c[14] in ("Woda", "Brzeg wody") and not (len(c) > 15 and c[15] & 1)]
    if woda_kol:
        blad("woda z kolizją: %d części" % len(woda_kol))
    sciany = [c for c in cz if c[14] == "Niewidzialna ściana"]
    for zn in (-1, 1):
        ok = any(not (len(c) > 15 and c[15] & 1) and c[13] >= 0.98 and abs(c[4] - Z0 - zn * 38.0) < 1.01
                 and aabb(c)[0][0] - X0 <= -4.0 and aabb(c)[1][0] - X0 >= 964.0 and aabb(c)[1][1] >= 20 for c in sciany)
        if not ok:
            blad("brak niewidzialnej ściany na v = %d (od u −4 do 964)" % (zn * 38))
    if not any(abs(c[2] - X0 + 5.0) < 1.01 and c[10] >= 76 for c in sciany):
        blad("brak niewidzialnej ściany za bramą Pniaków (u −5)")
    if not any(abs(c[2] - X0 - 965.0) < 1.01 for c in sciany):
        blad("brak niewidzialnej ściany na końcu zapowiedzi Bagna (u 965)")
    obecne = {grupy[c[1]][len(KONTENER) + 1:] for c in cz}
    for g in WYMAGANE_GRUPY:
        if not any(o == g or o.startswith(g + "/") for o in obecne):
            blad("brak grupy %s" % g)
    for st in P["strefy"]:
        if not any(o.startswith("Domy/%s" % st["id"]) for o in obecne):
            blad("brak domu potworów strefy %s" % st["id"])
    wrota = [c for c in cz if gr(c).startswith("BramaBagna/Wrota") and not (len(c) > 15 and c[15] & 1)]
    if not wrota:
        blad("brama do Bagna: brak wrót z kolizją w BramaBagna/Wrota")
    else:
        o1, o2 = K.miejsca["brama_bagna"]["otwarcie"]
        pokryte = sorted((aabb(c)[0][2] - Z0, aabb(c)[1][2] - Z0, aabb(c)[1][1]) for c in wrota)
        v, wys = o1, 99.0
        for a_, b_, h in pokryte:
            if a_ <= v + 0.3:
                v = max(v, b_)
                wys = min(wys, h)
        if v < o2 - 0.3 or wys < 7.0:
            blad("wrota bramy do Bagna nie zamykają otwarcia v %s…%s na wys. ≥ 7 (do v %s, wys. %s)" % (o1, o2, l1(v), l1(wys)))
    for g in ("Punkty/KamienPowrotu/_Interakcja", "Punkty/StanowiskoJajka/_Interakcja"):
        if g not in obecne:
            blad("brak punktu E %s" % g)

    # 6. znaczniki i faktury
    try:
        with open(a.znaczniki, encoding="utf-8") as f:
            zn = json.load(f)
        k = zn.get("kontener")
        if not isinstance(k, dict) or k.get("nazwa") != KONTENER:
            blad("znaczniki: kontener ≠ %s" % KONTENER)
        for klucz in ("grupy_stale_wczytane", "grupy_niski_detal"):
            gg = (zn.get(klucz) or {}).get("grupy")
            if not isinstance(gg, list) or not gg:
                blad("znaczniki: brak %s.grupy (czyta je studio_atrybuty.py)" % klucz)
                continue
            for g in gg:
                if not any(o == g or o.startswith(g + "/") for o in obecne):
                    blad("znaczniki: grupa %s z %s nie istnieje w częściach" % (g, klucz))
        plan_strefy = {st["id"]: st for st in P["strefy"]}
        for st in zn.get("strefy", []):
            ps = plan_strefy.get(st["id"])
            if not ps or len(st["wezly"]) != len(ps["trasa"]) or any(
                    abs(w[0] - p_[0]) > 1e-6 or abs(w[2] - p_[1]) > 1e-6 for w, p_ in zip(st["wezly"], ps["trasa"])):
                blad("znaczniki: węzły strefy %s różnią się od planu" % st["id"])
            for w, ws in zip(st["wezly"], st["wezly_swiat"]):
                if abs(ws[0] - (X0 + w[0])) > 0.01 or abs(ws[2] - (Z0 + w[2])) > 0.01:
                    blad("znaczniki: zły przelicznik na świat w strefie %s" % st["id"])
                    break
        if len(zn.get("strefy", [])) != len(P["strefy"]):
            blad("znaczniki: %d stref, w planie %d" % (len(zn.get("strefy", [])), len(P["strefy"])))
        if len(zn.get("punkty_e", [])) < 2:
            blad("znaczniki: za mało punktów E")
        if zn.get("brama_bagna", {}).get("grupa_wrot") != KONTENER + "/BramaBagna/Wrota":
            blad("znaczniki: brak ścieżki grupy wrót")
    except (OSError, ValueError, KeyError) as e:
        blad("znaczniki.json: %s" % e)
    znane = set(faktury.NAZWY) | {z_[0] for z_ in faktury.ZALEZNE} | set(FAKTURY_DODATKOWE)
    bez_roli = sorted({c[14] for c in cz if c[14] not in znane and mats[c[12]] != "Neon"})
    if bez_roli:
        blad("faktury: części bez roli: %s" % ", ".join(bez_roli))

    # wynik
    od = {}
    for c in cz:
        o = odcinek_raportu(c[2] - X0)
        od[o] = od.get(o, 0) + 1
    bez_kol = sum(1 for c in cz if len(c) > 15 and c[15] & 1)
    print("części: %d (cel ok. %d, limit %d) · grup: %d · materiały: %s" % (n, CEL, LIMIT, len(grupy), ", ".join(mats)))
    print("zakres w świecie: X %s…%s, Y %s…%s, Z %s…%s (u %s…%s, v %s…%s)" % (
        l1(mn_all[0]), l1(mx_all[0]), l1(mn_all[1]), l1(mx_all[1]), l1(mn_all[2]), l1(mx_all[2]),
        l1(mn_all[0] - X0), l1(mx_all[0] - X0), l1(mn_all[2] - Z0), l1(mx_all[2] - Z0)))
    print("Neon %d, kule %d, walce %d, półprzezroczyste %d, niewidzialne %d, z kolizją %d%%" % (
        neon, kule, walce, przezr, niewid, round(100.0 * (n - bez_kol) / n)))
    print("części na odcinek pasa:")
    for _, _, nazwa in ODCINKI_RAPORTU:
        print("  %-34s %5d" % (nazwa, od.get(nazwa, 0)))
    if sucho:
        print("studio_buduj.py --sucho: " + sucho.splitlines()[-1])
    print("sprawdzone: format, rozmiary, limity, granice (miasteczko, stary las, prototypy, Baseplate), place walki r 12 "
          "(%d węzłów), ścieżka, %d otwarć przejść, pętle, przelot kamery (%d próbek), grunt bez dziur, woda bez kolizji, "
          "niewidzialne ściany, wrota, punkty E, grupy, znaczniki, faktury" % (len(Z.wezly), len(Z.otwarcia), len(Z.kamera)))
    print()
    for t in uwagi:
        print("OSTRZEŻENIE:", t)
    for t in bledy:
        print("BŁĄD:", t)
    print("WYNIK: %d błędów, %d ostrzeżeń" % (len(bledy), len(uwagi)))
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
