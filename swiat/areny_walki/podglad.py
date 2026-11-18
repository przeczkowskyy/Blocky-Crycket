#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Podglądy aren walki z kamer walki: plan ogólny z obu stron, cztery kierunki z miejsca zwycięzcy (jak objazd),
widok z góry i „pocztówka”. Dwa silniki:

    python -B swiat/areny_walki/podglad.py                          # rysownik Pillow (szybki, bez Blendera) → <arena>/podglad/
    python -B swiat/areny_walki/podglad.py --blender --szer 960     # Blender (EEVEE, cienie, mgła z przebiegu Mist)
    python -B swiat/areny_walki/podglad.py --tylko las --kadry szeroki_przod,gora

Kamery liczone wzorami odtwarzacza (kamery.py) dla pary przykładowej areny (Wojownik i potwór biomu): `szeroki_przod`
= plan ogólny (kąt 40°), `szeroki_tyl` = to samo ujęcie z drugiej strony (jak lot strzały od strony tła),
`objazd_1…4` = kamera objazdu wokół zwycięzcy co 90° (widać tło w czterech ćwiartkach), `gora` = rzut z góry całej
areny, `pocztowka` = ukos z wysoka. Na placu stoją dwie bryły zastępcze postaci (wzrost i szerokość z danych aktorów),
tylko w podglądzie — w czesci.json ich nie ma.
Rysownik Pillow to NIE jest wygląd z Roblox (bez faktur, cieni i świateł); Blender pokazuje cienie i mgłę odległości,
ale też bez faktur Roblox. Blender: jeden naraz (wspólna blokada swiat/biblioteka/podglad.py), proces o niskim priorytecie.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import time

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import kamery  # noqa: E402
import plan as P  # noqa: E402

PARA = {"las": ("wojownik", "lesny_troll"), "bagno": ("wojownik", "ropucha_z_chatka"), "proba": ("zwiadowca", "lesny_slime"),
        "dzungla": ("mag", "kokosowy_silacz")}
NIEBO = {"las": ((0.52, 0.72, 0.93), (0.81, 0.89, 0.80), 430.0),
         "bagno": ((0.55, 0.64, 0.62), (0.64, 0.68, 0.59), 290.0),
         "proba": ((0.50, 0.70, 0.95), (0.92, 0.86, 0.76), 540.0),
         "dzungla": ((0.50, 0.72, 0.86), (0.66, 0.82, 0.68), 460.0)}
NISKI_PRIORYTET = False
KADRY = ["szeroki_przod", "szeroki_tyl", "objazd_1", "objazd_2", "objazd_3", "objazd_4", "gora", "pocztowka"]
OPISY = {"szeroki_przod": "plan ogólny walki (kąt 40°) od strony widowni",
         "szeroki_tyl": "plan ogólny z drugiej strony (tło za widownią)",
         "objazd_1": "objazd zwycięzcy: kamera z przodu-prawej, tło za plecami", "objazd_2": "objazd zwycięzcy: z przodu-lewej",
         "objazd_3": "objazd zwycięzcy: zza pleców-lewej (tło widowni)", "objazd_4": "objazd zwycięzcy: zza pleców-prawej",
         "gora": "rzut z góry całej areny (u góry tło za walczącymi)", "pocztowka": "ukos z wysoka — arena jako miejsce"}


def kamery_kadrow(klucz):
    """{kadr: (kamera, cel, kąt pionowy°)} w układzie SCENY."""
    akt = kamery.aktorzy_do_profilu(P.ARENY[klucz].get("przeciwnicy"))     # z szacunkowymi potworami nowego biomu
    gk, wk = PARA[klucz]
    g = kamery.geometria(akt[gk], akt[wk])
    wynik = {}
    poz, cel, kat, _ = kamery.ujecie(g, "ogolny", "gracz", "wrog", 0.0)
    wynik["szeroki_przod"] = (poz, cel, kat)
    wynik["szeroki_tyl"] = ((poz[0], poz[1], -poz[2]), cel, kat)
    hz = g["h"]["gracz"]
    R = 1.25 * hz + 6.5
    W = (g["x"]["gracz"], 0.0, 0.0)
    for i, a in enumerate((50.0, 130.0, 230.0, 310.0)):
        ar = math.radians(a)
        wynik["objazd_%d" % (i + 1)] = ((W[0] + R * math.cos(ar), hz * 0.55 + 1.6, R * math.sin(ar)), (W[0], hz * 0.5, 0.0), 44.0)
    wynik["gora"] = ((0.0, 900.0, 0.02), (0.0, 0.0, 0.0), 2 * math.degrees(math.atan(255.0 / 900.0)))
    wynik["pocztowka"] = ((24.0, 22.0, 50.0), (0.0, 3.0, -18.0), 54.0)   # w wolnej przestrzeni kamer: nic nie zasłania
    return wynik, g


def zastepcy(g):
    """Bryły zastępcze postaci na placu (gracz niebieski, potwór zielony) w układzie sceny — wiersze czesci.json."""
    wiersze = []
    for s, kol, kol2 in (("gracz", "2F6FE0", "F2C79B"), ("wrog", "52A04A", "2E6B2A")):
        x, h, w = g["x"][s], g["h"][s], g["w"][s]
        wiersze.append([0, 0, x, h * 0.42, 0.0, 0.0, 0.0, 0.0, w * 0.7, h * 0.84, w * 0.6, kol, 0, 0.0, "Aktor"])
        wiersze.append([0, 0, x, h * 0.9, 0.0, 0.0, 0.0, 0.0, w * 0.42, h * 0.2, w * 0.42, kol2, 0, 0.0, "Aktor głowa"])
    return wiersze


def json_z_aktorami(klucz, g):
    import geom
    with open(os.path.join(TU, klucz, "czesci.json"), encoding="utf-8") as f:
        d = json.load(f)
    O = P.ARENY[klucz]["O"]
    d["grupy"] = d["grupy"] + ["Workspace/ArenyWalki/_Aktorzy"]
    gi = len(d["grupy"]) - 1
    if "SmoothPlastic" not in d["materialy"]:
        d["materialy"].append("SmoothPlastic")
    mi = d["materialy"].index("SmoothPlastic")
    for w in zastepcy(g):
        w[1], w[12] = gi, mi
        d["czesci"].append(geom.do_swiata(w, O))
    fd, plik = tempfile.mkstemp(suffix=".json", prefix="arena_%s_" % klucz)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(d, f)
    return plik


def swiat(O, p):
    return (O[0] - p[0], O[1] + p[1], O[2] - p[2])


def pillow(klucz, kadry, szer, wyj):
    from PIL import ImageDraw
    from swiat.las_pas import podglad as rys
    kam, g = kamery_kadrow(klucz)
    plik = json_z_aktorami(klucz, g)
    try:
        _, sciany = rys.wczytaj(plik)
    finally:
        os.remove(plik)
    gora, dol, mgla = NIEBO[klucz]
    import numpy as np
    rys.NIEBO_GORA, rys.NIEBO_DOL = np.array(gora), np.array(dol)
    O = P.ARENY[klucz]["O"]
    H = int(szer * 9 / 16)
    pliki = []
    for nazwa in kadry:
        t0 = time.time()
        poz, cel, kat = kam[nazwa]
        img = rys.kadr_perspektywa(sciany, swiat(O, poz), swiat(O, cel), kat, szer, H if nazwa != "gora" else szer, mgla=mgla)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, img.width, 26), fill=(250, 246, 236))
        d.text((8, 6), "%s · %s · rysunek Pillow (bez faktur, cieni i świateł Roblox)" % (P.ARENY[klucz]["nazwa"], OPISY[nazwa]),
               fill=(40, 34, 30))
        p = os.path.join(wyj, "%s.jpg" % nazwa)
        img.save(p, quality=86)
        pliki.append(p)
        print("  %s/%s (%.1f s)" % (klucz, nazwa, time.time() - t0), flush=True)
    return pliki


def blender(klucz, kadry, szer, wyj, probki):
    sys.path.insert(0, os.path.join(REPO, "swiat", "biblioteka"))
    from swiat.biblioteka.podglad import blender_exe, zajmij_blender, zwolnij_blender
    kam, g = kamery_kadrow(klucz)
    plik = json_z_aktorami(klucz, g)
    O = P.ARENY[klucz]["O"]
    uj = []
    for nazwa in kadry:
        poz, cel, kat = kam[nazwa]
        if nazwa == "gora":
            uj.append([nazwa, list(swiat(O, poz)), list(swiat(O, cel)), 35.0, 2 * P.R_GRUNT + 10])
        else:
            # ogniskowa dla kąta PIONOWEGO `kat` w kadrze 16:9 (Blender: matryca 36 mm w poziomie)
            ogn = 18.0 / (math.tan(math.radians(kat / 2.0)) * 16.0 / 9.0)
            uj.append([nazwa, list(swiat(O, poz)), list(swiat(O, cel)), round(ogn, 2), None])
    fd, plik_uj = tempfile.mkstemp(suffix=".json", prefix="ujecia_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(uj, f)
    gora, dol, mgla = NIEBO[klucz]
    polecenie = [blender_exe(), "-b", "--factory-startup", "-t", "2", "--python-exit-code", "1", "--python",
                 os.path.join(TU, "render_blender.py"), "--", "--z-json", plik, "--render", wyj, "--szer", str(szer),
                 "--probki", str(probki), "--ujecia", plik_uj, "--mgla", "%g" % mgla,
                 "--niebo", ",".join("%g" % v for v in gora), "--kolor-mgly", ",".join("%g" % v for v in dol)]
    blok = zajmij_blender()
    t0 = time.time()
    try:
        flagi = 0x08000000 | (0x00000040 if NISKI_PRIORYTET else 0)            # bez okna (+ IDLE_PRIORITY_CLASS)
        r = subprocess.Popen(polecenie, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=flagi if os.name == "nt" else 0)
        out, _ = r.communicate(timeout=30 * 60)
    finally:
        zwolnij_blender(blok)
        os.remove(plik)
        os.remove(plik_uj)
    tekst = out.decode("utf-8", "replace")
    for linia in tekst.splitlines():
        if linia.startswith("KLOCKI |") or linia.startswith("ARENA |"):
            print("  " + linia)
    if r.returncode != 0:
        print("\n".join(tekst.splitlines()[-30:]))
        raise SystemExit("Blender: błąd %d" % r.returncode)
    print("  %s: Blender %.0f s" % (klucz, time.time() - t0))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Podglądy aren walki")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--kadry", default="")
    ap.add_argument("--szer", type=int, default=1280)
    ap.add_argument("--wyj", default=None, help="folder (domyślnie swiat/areny_walki/<arena>/podglad)")
    ap.add_argument("--blender", action="store_true")
    ap.add_argument("--probki", type=int, default=16)
    ap.add_argument("--niski-priorytet", action="store_true", help="Blender z najniższym priorytetem (gdy w Studio trwają próby)")
    a = ap.parse_args()
    global NISKI_PRIORYTET
    NISKI_PRIORYTET = a.niski_priorytet
    kadry = [k for k in a.kadry.split(",") if k] or KADRY
    for klucz in P.ARENY:
        if a.tylko and klucz not in a.tylko.split(","):
            continue
        wyj = os.path.join(a.wyj, klucz) if a.wyj else os.path.join(TU, klucz, "podglad")
        os.makedirs(wyj, exist_ok=True)
        if a.blender:
            blender(klucz, kadry, a.szer, wyj, a.probki)
        else:
            pillow(klucz, kadry, a.szer, wyj)


if __name__ == "__main__":
    main()
