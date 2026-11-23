#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane zabawek (swiat/zabawki): ustawienia.json + pety, rzadkości i dźwięki z danych Pet Areny → zrodla/DaneZabawek.luau.

    python -B swiat/zabawki/dane.py

W grze nic nie jest importowane z Pet Areny: wygenerowany moduł ma własną kopię danych, a wzorce potworów zbuduj.py kopiuje
do własnego kontenera.
"""
import importlib.util
import json
import math
import os
import random
import sys

sys.dont_write_bytecode = True
PAKIET = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(PAKIET))
ZR = os.path.join(PAKIET, "zrodla")
PLIK = os.path.join(ZR, "DaneZabawek.luau")


def _pa():
    spec = importlib.util.spec_from_file_location("dane_pet_arena", os.path.join(REPO, "swiat", "pet_arena", "dane.py"))
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.join(REPO, "swiat", "pet_arena"))
    try:
        spec.loader.exec_module(m)
    finally:
        sys.path.pop(0)
    return m


def ustawienia():
    with open(os.path.join(PAKIET, "ustawienia.json"), encoding="utf-8") as f:
        return json.load(f)


def kulki(Z):
    """Stałe miejsca kulek na polu (bez skał), powtarzalne."""
    los = random.Random(7)
    sk = skaly(Z)
    w = []
    while len(w) < Z["kulek"]:
        a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (Z["pole_r"] - 4)
        x, z = round(math.sin(a) * r, 2), round(math.cos(a) * r, 2)
        if all(math.hypot(x - s["x"], z - s["z"]) > s["r"] + 2 for s in sk):
            w.append([x, z])
    return w


def skaly(Z):
    los = random.Random(3)
    w = []
    while len(w) < Z["skal"]:
        a, r = los.random() * 2 * math.pi, 30 + los.random() * (Z["pole_r"] - 45)
        s = {"x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "r": round(5 + los.random() * 5, 2)}
        if all(math.hypot(s["x"] - q["x"], s["z"] - q["z"]) > s["r"] + q["r"] + 12 for q in w):
            w.append(s)
    return w


def dane():
    U = ustawienia()
    PA = _pa()
    _, DP, _ = PA.wszystkie_pliki()
    pety = [{"id": p["id"], "nazwa": p["nazwa"], "wzorzec": p["wzorzec"], "wysokosc": p["wysokosc"], "promien": p["promien"],
             "stopien": p["stopien"]} for p in DP["pety"]]
    nr = {p["id"]: i + 1 for i, p in enumerate(pety)}
    Z = dict(U["zjadacz"])
    Z.pop("opis", None)
    for f in Z["formy"]:
        if f["pet"] not in nr:
            raise SystemExit("forma: nieznany pet %s" % f["pet"])
        f["nr"] = nr[f["pet"]]
    Z["kulkiPoz"] = kulki(Z)
    Z["skalyPoz"] = skaly(Z)
    W = dict(U["wabik"])
    W.pop("opis", None)
    W["zagrodyPoz"] = [[round((i - (W["zagrod"] - 1) / 2) * W["zagroda_szer"], 2), -W["zagroda_gl"] / 2] for i in range(W["zagrod"])]
    dz = {r: DP["dzwieki"]["efekty"][r] for r in U["dzwieki"] if r in DP["dzwieki"]["efekty"]}
    return {"kontener": U["kontener"], "prefiks": U["prefiks"], "ui": U["ui"], "zjadacz": Z, "wabik": W, "pety": pety,
            "rzadkosci": DP["rzadkosci"], "dzwieki": {"arkusz": DP["dzwieki"]["arkusz"], "efekty": dz}, "miejsceBC": U["miejsce_bc"]}


def luau(v, w=0):
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(v, 6)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    p = "\t" * (w + 1)
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            return "{ " + ", ".join(luau(x) for x in v) + " }"
        return "{\n" + "".join(p + luau(x, w + 1) + ",\n" for x in v) + "\t" * w + "}"
    return "{\n" + "".join(p + (k if k.isidentifier() else "[%s]" % json.dumps(k)) + " = " + luau(x, w + 1) + ",\n"
                           for k, x in v.items()) + "\t" * w + "}"


def tekst():
    return "-- WYGENEROWANE przez swiat/zabawki/dane.py z ustawienia.json (+ pety, rzadkości, dźwięki Pet Areny) — nie edytuj\nreturn " + luau(dane()) + "\n"


def main():
    t = tekst()
    stary = open(PLIK, encoding="utf-8").read() if os.path.exists(PLIK) else ""
    if t != stary:
        os.makedirs(ZR, exist_ok=True)
        open(PLIK, "w", encoding="utf-8", newline="\n").write(t)
        print("zapisano zrodla/DaneZabawek.luau")
    else:
        print("bez zmian")


if __name__ == "__main__":
    main()
