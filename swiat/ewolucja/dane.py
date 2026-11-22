#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane Monster Evolution (swiat/ewolucja): ustawienia.json + modele, promienie i dźwięki z danych Pet Areny
→ zrodla/DaneEwolucji.luau.

    python -B swiat/ewolucja/dane.py

W grze nic nie jest importowane z Pet Areny: wygenerowany moduł ma własną kopię liczb, a wzorce potworów zbuduj.py
kopiuje do własnego kontenera (Workspace/PetArenaGra/Wzorce → EwolucjaGra/Wzorce).
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
PLIK = os.path.join(ZR, "DaneEwolucji.luau")
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'


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


def przeszkody(P):
    """Skały i drzewa w polu (koła dla logiki), powtarzalne."""
    los = random.Random(11)
    R = P["r"]
    w = []
    while len([s for s in w if s["typ"] == "skala"]) < P["skal"]:
        a, r = los.random() * 2 * math.pi, 34 + los.random() * (R - 60)
        s = {"typ": "skala", "x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "r": round(5 + los.random() * 4.5, 2)}
        if all(math.hypot(s["x"] - q["x"], s["z"] - q["z"]) > s["r"] + q["r"] + 22 for q in w):
            w.append(s)
    while len([s for s in w if s["typ"] == "drzewo"]) < P["drzew_w_polu"]:
        a, r = los.random() * 2 * math.pi, 40 + los.random() * (R - 58)
        s = {"typ": "drzewo", "x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "r": 2.4, "h": round(16 + los.random() * 8, 1)}
        if all(math.hypot(s["x"] - q["x"], s["z"] - q["z"]) > s["r"] + q["r"] + 20 for q in w):
            w.append(s)
    return w


def kulki(P, J, prz):
    """Stałe miejsca kulek: [x, z, typ] (1 mała, 2 duża), z dala od przeszkód."""
    los = random.Random(7)
    w = []
    for typ, ile in ((2, J["duze"]), (1, J["male"])):
        n = 0
        while n < ile:
            a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (P["r"] - 5)
            x, z = round(math.sin(a) * r, 2), round(math.cos(a) * r, 2)
            if all(math.hypot(x - s["x"], z - s["z"]) > s["r"] + 2.5 for s in prz):
                w.append([x, z, typ])
                n += 1
    return w


def wystroj(P):
    """Tylko scena: plamy trawy, drzewa za murem, kwiaty."""
    los = random.Random(5)
    R = P["r"]
    plamy = []
    kolory = [("7CC85A", "Grass"), ("9AD86E", "Grass"), ("6DB851", "LeafyGrass"), ("C9B27A", "Ground"), ("A8D27A", "Grass"),
              ("D9C58E", "Sand"), ("86C062", "LeafyGrass")]
    for i in range(P["plam"]):
        a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (R - 20)
        k = kolory[i % len(kolory)]
        plamy.append({"x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "r": round(10 + los.random() * 16, 1), "c": k[0], "m": k[1]})
    drzewa = []
    for i in range(P["drzew_za_murem"]):
        a = 2 * math.pi * (i + los.random() * 0.6) / P["drzew_za_murem"]
        r = R + 12 + los.random() * 26
        drzewa.append({"x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "h": round(18 + los.random() * 14, 1)})
    kwiaty = []
    for i in range(P["kwiatow"]):
        a = i * 2.39996
        r = math.sqrt((i + 0.5) / P["kwiatow"]) * (R - 6)
        kwiaty.append([round(math.sin(a) * r, 2), round(math.cos(a) * r, 2)])
    return {"plamy": plamy, "drzewa": drzewa, "kwiaty": kwiaty}


def dane():
    U = ustawienia()
    PA = _pa()
    UP, DP, _ = PA.wszystkie_pliki()
    pety = {p["id"]: p for p in DP["pety"]}
    formy = []
    for i, F in enumerate(U["formy"]):
        f = {k: v for k, v in F.items() if k not in ("pet", "boss")}
        if "pet" in F:
            P = pety.get(F["pet"])
            if not P:
                raise SystemExit("forma %d: nieznany pet %s" % (i + 1, F["pet"]))
            f["wzorzec"], f["model_r"], f["model_h"] = P["wzorzec"], P["promien"], P["wysokosc"]
        else:
            B = UP["boss"]
            if F["boss"] not in [b["model"] for b in B["modele"]]:
                raise SystemExit("forma %d: nieznany boss %s" % (i + 1, F["boss"]))
            f["wzorzec"], f["model_r"], f["model_h"] = "Boss_" + F["boss"], B["promien"], B["wysokosc"]
        formy.append(f)
    for a, b in zip(formy, formy[1:]):
        if b["r"] <= a["r"]:
            raise SystemExit("formy: promienie muszą rosnąć")
    P = dict(U["pole"])
    P.pop("opis", None)
    prz = przeszkody(P)
    J = {k: v for k, v in U["jedzenie"].items() if k != "opis"}
    D = {
        "kontener": U["kontener"], "prefiks": U["prefiks"], "wylacznik": U["wylacznik"], "wzorceRS": U["wzorce_rs"], "ui": U["ui"],
        "pole": P, "przeszkody": prz, "kulkiPoz": kulki(P, J, prz), "jedzenie": J, "formy": formy,
        "ruch": {k: v for k, v in U["ruch"].items() if k != "opis"},
        "gryzienie": {k: v for k, v in U["gryzienie"].items() if k != "opis"},
        "ulepszenia": U["ulepszenia"],
        "smierc": {k: v for k, v in U["smierc"].items() if k != "opis"},
        "ewolucja": {k: v for k, v in U["ewolucja"].items() if k != "opis"},
        "boty": {k: v for k, v in U["boty"].items() if k != "opis"},
        "siec": {k: v for k, v in U["siec"].items() if k != "opis"},
        "kamera": U["kamera"],
        "dzwieki": {"arkusz": DP["dzwieki"]["arkusz"], "efekty": {r: DP["dzwieki"]["efekty"][r] for r in U["dzwieki"] if r in DP["dzwieki"]["efekty"]}},
        "miejsceBC": U["miejsce_bc"],
    }
    return D


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
        if all(isinstance(x, list) and all(not isinstance(y, (dict, list)) for y in x) for x in v):
            return "{\n" + "".join(p + luau(x) + ",\n" for x in v) + "\t" * w + "}"
        return "{\n" + "".join(p + luau(x, w + 1) + ",\n" for x in v) + "\t" * w + "}"
    return "{\n" + "".join(p + (k if k.isidentifier() else "[%s]" % json.dumps(k)) + " = " + luau(x, w + 1) + ",\n"
                           for k, x in v.items()) + "\t" * w + "}"


def tekst():
    return ("-- WYGENEROWANE przez swiat/ewolucja/dane.py z ustawienia.json (+ modele i dźwięki Pet Areny) — nie edytuj\nreturn "
            + luau(dane()) + "\n")


def main():
    t = tekst()
    stary = open(PLIK, encoding="utf-8").read() if os.path.exists(PLIK) else ""
    if t != stary:
        os.makedirs(ZR, exist_ok=True)
        open(PLIK, "w", encoding="utf-8", newline="\n").write(t)
        print("zapisano zrodla/DaneEwolucji.luau")
    else:
        print("bez zmian")


if __name__ == "__main__":
    main()
