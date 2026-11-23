#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Budowa Monster Evolution w Studio: Workspace/EwolucjaGra (moduły, skrypty, sygnały, wzorce 8 form, pole).

    python -B swiat/ewolucja/zbuduj.py --sucho                 # bez Studio: dane, kontrola Luau, plan
    python -B swiat/ewolucja/zbuduj.py --studio <id>           # pełna budowa (strażnik „tylko Studio” w skryptach)
    python -B swiat/ewolucja/zbuduj.py --skrypty --studio <id> # tylko moduły i skrypty (scena i wzorce zostają)
    python -B swiat/ewolucja/zbuduj.py --publikacja ...        # skrypty BEZ strażnika Studio (prywatna wersja testowa)
    python -B swiat/ewolucja/zbuduj.py --wlacz on|off ...      # wyłącznik EwolucjaWlaczona (atrybut kontenera)
    python -B swiat/ewolucja/zbuduj.py --stan | --usun ...     # odczyt / usunięcie własnego kontenera

Zasady: odmowa w miejscu gry B&C, poza trybem Edit i przy obcym obiekcie EwolucjaGra (bez atrybutu Wygenerowane);
punkt historii przed i po każdej zmianie; niczego nie zapisuje ani nie publikuje; Lighting bez zmian. Wzorce potworów
kopiuje z Workspace/PetArenaGra/Wzorce (tylko 8 modeli drabiny) do własnego kontenera; serwer w czasie gry przenosi je
do ReplicatedStorage/EwolucjaWzorce.
"""
import argparse
import importlib.util
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
PAKIET = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
sys.path.append(os.path.join(REPO, "tools"))
import dane as DN  # noqa: E402

ZR = os.path.join(PAKIET, "zrodla")
MODULY = ["DaneEwolucji", "LogikaEwolucji", "EfektyEwolucji", "KlipyEwolucji", "RigiEwolucji", "SmokiKlienta", "LegowiskaKlienta", "SwiatKlienta", "IkonyEwolucji", "InterfejsKlienta"]
SKRYPTY = [("SerwerEwolucji", "SerwerEwolucji.server.luau", "Server"), ("KlientEwolucji", "KlientEwolucji.client.luau", "Client")]


def log(*a):
    print("Ewolucja |", *a, flush=True)


def bez_straznika(tekst):
    """--publikacja: usuwa blok strażnika Studio (`if not …IsStudio() then` … `end` w kolumnie 0)."""
    i = tekst.find(DN.STRAZNIK)
    if i < 0:
        raise ValueError("brak strażnika Studio")
    k = tekst.find("\nend\n", i)
    if k < 0:
        raise ValueError("strażnik bez `end` w kolumnie 0")
    return tekst[:i] + "-- (publikacja: bez strażnika Studio)\n" + tekst[k + 5:]


def zrodla(publikacja=False):
    w = {}
    for n in MODULY:
        w[n] = open(os.path.join(ZR, n + ".luau"), encoding="utf-8").read().replace("\r\n", "\n")
    for n, plik, _ in SKRYPTY:
        t = open(os.path.join(ZR, plik), encoding="utf-8").read().replace("\r\n", "\n")
        if DN.STRAZNIK not in t:
            raise SystemExit("BŁĄD: %s bez strażnika Studio" % plik)
        w[n] = bez_straznika(t) if publikacja else t
    return w


def kontrola_luau():
    spec = importlib.util.spec_from_file_location("kontrola_luau_potworow", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # skrypty: wszystkie reguły (bilans, strażnik Studio, zakazane konstrukcje); moduły: bez strażnika (czyste rachunki
    # uruchamiane też w testach bez Studio; działają tylko, gdy wymaga ich skrypt ze strażnikiem)
    bledy = mod.sprawdz_pliki([os.path.join(ZR, p) for _, p, _ in SKRYPTY], wypisz=lambda t: None)
    for n in MODULY:
        s = os.path.join(ZR, n + ".luau")
        t = mod.wczytaj(s)
        nazwa = os.path.relpath(s, REPO).replace("\\", "/")
        bez_kom, bez_kom_nap = mod.rozbierz(t)
        zak = mod.zakazane(bez_kom, bez_kom_nap, nazwa)
        if n == "SwiatKlienta":
            # wyjątek jawny (swiat1): światło i niebo ustawia w czasie gry tylko ten moduł klienta (lokalnie u gracza, nigdy w trybie
            # Edit ani na serwerze) — zlecone w zadaniu „świat”; pozostałe zakazy (loadstring, getfenv, …) obowiązują
            zak = [b for b in zak if not b.endswith("zakazane `Lighting`")]
        bledy += mod.sprawdz_tekst(t, nazwa, pelne=False) + zak
    return bledy


def czesc(lista, grupa, nazwa, poz, roz, kolor, mat="SmoothPlastic", ksztalt="Block", obrot=(0, 0, 0), przez=0, kol=False):
    lista.append({"g": grupa, "n": nazwa, "p": [round(x, 3) for x in poz], "s": [round(x, 3) for x in roz], "c": kolor, "m": mat,
                  "k": ksztalt, "r": [round(x, 4) for x in obrot], "t": przez, "kol": kol})


def drzewo(L, cx, cy, cz, x, z, h, nazwa):
    # drzewa w polu i w lesie: korona półprzezroczysta, żeby z kamery z góry było widać potwora pod nią
    przez = 0.45 if nazwa in ("DrzewoPole", "DrzewoLas") else 0
    pien = max(1.6, h * 0.11)
    czesc(L, "Drzewa", nazwa, (cx + x, cy + h * 0.4, cz + z), (h * 0.8, pien, pien), "7A5232", "Wood", "Cylinder", (0, 0, math.pi / 2))
    for i, (dx, dy, dz, s, k) in enumerate([(0, 0.82, 0, 0.62, "4E9A3C"), (0.18, 0.7, 0.12, 0.45, "5DB047"), (-0.16, 0.68, -0.1, 0.42, "3F8A33")]):
        czesc(L, "Drzewa", nazwa + "Korona", (cx + x + dx * h, cy + dy * h, cz + z + dz * h), (s * h, s * h * 0.85, s * h), k, "LeafyGrass", "Ball",
              (0, 0, 0), przez)


def brama_lasu(D):
    """Cięciwa przecięcia koła łąki i lasu: końce, środek, kierunek do lasu."""
    LS = D["las"]
    r1, r2 = D["pole"]["r"], LS["r"]
    d = math.hypot(LS["x"], LS["z"])
    ux, uz = LS["x"] / d, LS["z"] / d
    a = (d * d + r1 * r1 - r2 * r2) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    return {"a": (ux * a - uz * h, uz * a + ux * h), "b": (ux * a + uz * h, uz * a - ux * h), "srodek": (ux * a, uz * a), "u": (ux, uz), "h": h}


def scena(D):
    if D.get("swiat"):
        return scena_swiata(D)
    P = D["pole"]
    LS = D["las"]
    cx, cy, cz = P["srodek"]
    R = P["r"]
    W = DN.wystroj(P)
    WL = DN.wystroj_lasu(dict(DN.ustawienia()["las"]))
    L = []
    rot = (0, 0, math.pi / 2)
    czesc(L, "Teren", "Pole", (cx, cy - 2, cz), (4, 2 * R + 20, 2 * R + 20), "8FD46B", "Grass", "Cylinder", rot)
    czesc(L, "Teren", "Okolica", (cx, cy - 2.2, cz), (4, 2 * R + 140, 2 * R + 140), "6FB04F", "Grass", "Cylinder", rot)
    lx, lz = cx + LS["x"], cz + LS["z"]
    czesc(L, "Las", "Sciolka", (lx, cy - 2.05, lz), (4, 2 * LS["r"] + 14, 2 * LS["r"] + 14), "4A7A3A", "LeafyGrass", "Cylinder", rot)
    czesc(L, "Las", "OkolicaLasu", (lx, cy - 2.25, lz), (4, 2 * LS["r"] + 120, 2 * LS["r"] + 120), "3F6B33", "Grass", "Cylinder", rot)
    for i, p in enumerate(W["plamy"]):
        czesc(L, "Teren", "Plama", (cx + p["x"], cy + 0.02 + i * 0.002, cz + p["z"]), (0.12, p["r"] * 2, p["r"] * 2), p["c"], p["m"], "Cylinder", rot)
    for i, p in enumerate(WL["plamy"]):
        czesc(L, "Las", "Plama", (cx + p["x"], cy + 0.03 + i * 0.002, cz + p["z"]), (0.12, p["r"] * 2, p["r"] * 2), p["c"], p["m"], "Cylinder", rot)
    for i in range(9):
        a = -0.9 + i * 0.22
        czesc(L, "Teren", "Sciezka", (cx + math.sin(a) * 60 * (i - 4) / 4, cy + 0.06, cz + (i - 4) * 30), (0.1, 9, 9), "E6D3A0", "Sand", "Cylinder", rot)
    # mury: łąka bez odcinka przy lesie, las bez odcinka w łące
    n = 56
    for i in range(n):
        a = 2 * math.pi * i / n
        r = R + 1.5
        x, z = math.sin(a) * r, math.cos(a) * r
        if math.hypot(x - LS["x"], z - LS["z"]) < LS["r"] + 1:
            continue
        czesc(L, "Mur", "Mur", (cx + x, cy + P["mur_y"] / 2, cz + z), (2 * math.pi * r / n + 0.6, P["mur_y"], 2.6), ["F2C36B", "E8A85A"][i % 2], "Slate",
              "Block", (0, a, 0), 0, True)
    n = 44
    for i in range(n):
        a = 2 * math.pi * i / n
        r = LS["r"] + 1.5
        x, z = LS["x"] + math.sin(a) * r, LS["z"] + math.cos(a) * r
        if math.hypot(x, z) < R + 1:
            continue
        czesc(L, "Las", "MurLasu", (cx + x, cy + 2, cz + z), (2 * math.pi * r / n + 0.6, 4, 3), ["6B5A44", "5C4D3A"][i % 2], "Wood", "Block", (0, a, 0), 0, True)
    # brama: niski płot z wikliny na cięciwie (klient chowa go, gdy las otwarty), słupki ze światłem, tablica
    B = brama_lasu(D)
    (ax, az), (bx, bz) = B["a"], B["b"]
    dl = math.hypot(bx - ax, bz - az)
    kat = math.atan2(bx - ax, bz - az)
    k = int(dl // 6)
    for i in range(k):
        f = (i + 0.5) / k
        czesc(L, "Brama", "Plot", (cx + ax + (bx - ax) * f, cy + 1.2, cz + az + (bz - az) * f), (0.8, 2.4, dl / k - 0.4), "8A6A3A", "Wood", "Block",
              (0, kat, 0))
        czesc(L, "Brama", "Plot", (cx + ax + (bx - ax) * f, cy + 1.9, cz + az + (bz - az) * f), (0.5, 0.35, dl / k + 0.1), "7CFF9A", "Neon", "Block",
              (0, kat, 0), 0.2)
    for (px, pz) in (B["a"], B["b"]):
        czesc(L, "Brama", "Slup", (cx + px, cy + 4, cz + pz), (2.2, 8, 2.2), "6B5A44", "Wood", "Block")
        czesc(L, "Brama", "SlupSwiatlo", (cx + px, cy + 8.6, cz + pz), (2.2, 2.2, 2.2), "7CFF9A", "Neon", "Ball")
    # kępki trawy, grzyby, krzaki, stawy
    for x, z, a in W["kepki"]:
        if math.hypot(x - LS["x"], z - LS["z"]) > LS["r"]:
            czesc(L, "Kepki", "Kepka", (cx + x, cy + 0.45, cz + z), (0.5, 0.9, 1.1), ["6FBF4A", "7ACC55", "5EAA3E"][int(a * 10) % 3], "Grass", "Wedge", (0, a, 0))
    for x, z, s in W["grzyby"] + WL["grzyby"]:
        czesc(L, "Grzyby", "Trzon", (cx + x, cy + s * 0.6, cz + z), (s * 1.2, s * 0.45, s * 0.45), "F2EBDD", "SmoothPlastic", "Cylinder", rot)
        czesc(L, "Grzyby", "Kapelusz", (cx + x, cy + s * 1.25, cz + z), (s * 1.3, s * 0.7, s * 1.3), ["E0483C", "C9783A", "D64A8A"][int(s * 10) % 3],
              "SmoothPlastic", "Ball")
    for x, z, s in W["krzaki"]:
        if math.hypot(x - LS["x"], z - LS["z"]) > LS["r"] + 6:
            czesc(L, "Krzaki", "Krzak", (cx + x, cy + s * 0.45, cz + z), (s * 1.6, s, s * 1.6), ["4E9A3C", "5DB047", "3F8A33"][int(s * 10) % 3], "LeafyGrass", "Ball")
    for s in D["przeszkody"]:
        if s["typ"] == "skala":
            i = int(abs(s["x"])) % 3
            czesc(L, "Skaly", "Skala", (cx + s["x"], cy + 2.5, cz + s["z"]), (6, s["r"] * 2, s["r"] * 2), ["9C8C7A", "8A7C6C", "A89A86"][i],
                  "Slate", "Cylinder", rot, 0, True)
            czesc(L, "Skaly", "SkalaCzubek", (cx + s["x"], cy + 5.6, cz + s["z"]), (s["r"] * 1.5, 4, s["r"] * 1.5), "B5A792", "Rock", "Ball")
            czesc(L, "Skaly", "SkalaMala", (cx + s["x"] + s["r"] * 0.9, cy + 1.2, cz + s["z"] - s["r"] * 0.5), (s["r"] * 0.7, s["r"] * 0.5, s["r"] * 0.7),
                  "8A7C6C", "Rock", "Ball")
        elif s["typ"] == "staw":
            czesc(L, "Stawy", "Brzeg", (cx + s["x"], cy + 0.05, cz + s["z"]), (0.14, s["r"] * 2 + 4, s["r"] * 2 + 4), "D9C58E", "Sand", "Cylinder", rot)
            czesc(L, "Stawy", "Woda", (cx + s["x"], cy + 0.12, cz + s["z"]), (0.16, s["r"] * 2, s["r"] * 2), "4FA8E0", "Glass", "Cylinder", rot, 0.15)
            for j in range(5):
                a = j * 1.3
                czesc(L, "Stawy", "Lilia", (cx + s["x"] + math.sin(a) * s["r"] * 0.55, cy + 0.2, cz + s["z"] + math.cos(a) * s["r"] * 0.5),
                      (0.1, 2.2, 2.2), "6FBF4A", "SmoothPlastic", "Cylinder", rot)
        else:
            drzewo(L, cx, cy, cz, s["x"], s["z"], s["h"], "DrzewoLas" if s.get("las") else "DrzewoPole")
    for d in W["drzewa"]:
        if math.hypot(d["x"] - LS["x"], d["z"] - LS["z"]) > LS["r"] + 8:
            drzewo(L, cx, cy, cz, d["x"], d["z"], d["h"], "DrzewoZa")
    for d in WL["drzewa"]:
        drzewo(L, cx, cy, cz, d["x"], d["z"], d["h"], "DrzewoZaLasem")
    for i in range(3):
        a = 2 * math.pi * i / 3 + 2.6
        r = R + 10
        czesc(L, "Znaki", "Menhir", (cx + math.sin(a) * r, cy + 7, cz + math.cos(a) * r), (4, 14, 3), "7C7486", "Slate", "Block", (0, a, 0.08))
    # znak w środku łąki: kamienny krąg (punkt orientacyjny przy starcie)
    for i in range(8):
        a = 2 * math.pi * i / 8
        czesc(L, "Znaki", "Krag", (cx + 12 + math.sin(a) * 9, cy + 1.6, cz - 20 + math.cos(a) * 9), (1.6, 3.2, 1.6), "A8A0B4", "Slate", "Block", (0, a, 0))
    # SKY NEST (walka1): wyspa w fosie lawy — tylko szybowanie albo skok meteoru
    WY = D.get("wyspa")
    if WY:
        wx, wz, rw, rz = WY["x"], WY["z"], WY["r_wew"], WY["r_zew"]
        czesc(L, "Wyspa", "Brzeg", (cx + wx, cy + 0.06, cz + wz), (0.14, rz * 2 + 2.4, rz * 2 + 2.4), "3A2A2A", "Basalt", "Cylinder", rot)
        czesc(L, "Wyspa", "Lawa", (cx + wx, cy + 0.1, cz + wz), (0.16, rz * 2, rz * 2), "FF6A1A", "Neon", "Cylinder", rot)
        czesc(L, "Wyspa", "Skorupa", (cx + wx, cy + 0.14, cz + wz), (0.12, rw * 2 + 3, rw * 2 + 3), "4A2E26", "CrackedLava", "Cylinder", rot)
        czesc(L, "Wyspa", "Trawa", (cx + wx, cy + 0.2, cz + wz), (0.16, rw * 2, rw * 2), "8FD86B", "Grass", "Cylinder", rot)
        for i in range(10):
            a = i * 2 * math.pi / 10 + 0.3
            czesc(L, "Wyspa", "Kamien", (cx + wx + math.sin(a) * (rw + 0.6), cy + 0.6, cz + wz + math.cos(a) * (rw + 0.6)), (2.2, 1.2, 1.8), "5A4A48",
                  "Slate", "Ball")
        for i in range(3):
            a = i * 2 * math.pi / 3
            czesc(L, "Wyspa", "Krysztal", (cx + wx + math.sin(a) * rw * 0.82, cy + 3, cz + wz + math.cos(a) * rw * 0.82), (1.4, 6, 1.4), "7FE9FF", "Neon",
                  "Block", (0.15, a, 0.1), 0.15)
        for i in range(14):
            a = i * 2 * math.pi / 14
            r = (rw + rz) / 2 + (0.8 if i % 2 else -0.8)
            czesc(L, "Wyspa", "Iskra", (cx + wx + math.sin(a) * r, cy + 0.35, cz + wz + math.cos(a) * r), (0.6, 0.5, 0.6), "FFC83D", "Neon", "Ball")
    # legowiska graczy na skraju łąki: podłoga, obrzeże, 8 cokołów (trofea stawia klient)
    kol = ["FFD9D9", "D9ECFF", "DDF7DD", "FFEBCF", "EBDDFF", "FFDDF0", "D6FAF6", "F7F7D2"]
    for i, (x, z) in enumerate(D["legowiska"]):
        R2 = D["legowisko"]["r"]
        czesc(L, "Legowiska", "Obrzeze", (cx + x, cy + 0.1, cz + z), (0.2, 2 * R2 + 1.6, 2 * R2 + 1.6), "8A6A3A", "WoodPlanks", "Cylinder", rot)
        czesc(L, "Legowiska", "Podloga", (cx + x, cy + 0.16, cz + z), (0.22, 2 * R2, 2 * R2), kol[i % len(kol)], "WoodPlanks", "Cylinder", rot)
        for f in range(8 if not D.get("blender") else 0):  # zestaw blender: cokoły z danych stawia klient
            a = f * 2 * math.pi / 8
            czesc(L, "Legowiska", "Cokol", (cx + x + math.sin(a) * 8.5, cy + 0.65, cz + z + math.cos(a) * 8.5), (1.2, 3.2, 3.2), "B8B0C8", "Slate",
                  "Cylinder", rot)
    for i, (x, z) in enumerate(W["kwiaty"]):
        czesc(L, "Kwiaty", "Kwiat", (cx + x, cy + 0.08, cz + z), (0.1, 1.6, 1.6), ["FFF07A", "FF9AD8", "FFFFFF", "C8A8FF"][i % 4], "SmoothPlastic",
              "Cylinder", rot)
    return L


def scena_swiata(D):
    """Świat z mapy: w scenie zostają brama lasu (płot chowany przez klienta) i wyspa gry w fosie lawy (SKY NEST)."""
    P = D["pole"]
    cx, cy, cz = P["srodek"]
    L = []
    rot = (0, 0, math.pi / 2)
    B = brama_lasu(D)
    (ax, az), (bx, bz) = B["a"], B["b"]
    dl = math.hypot(bx - ax, bz - az)
    kat = math.atan2(bx - ax, bz - az)
    k = int(dl // 6)
    for i in range(k):
        f = (i + 0.5) / k
        czesc(L, "Brama", "Plot", (cx + ax + (bx - ax) * f, cy + 1.2, cz + az + (bz - az) * f), (0.8, 2.4, dl / k - 0.4), "8A6A3A", "Wood", "Block",
              (0, kat, 0))
        czesc(L, "Brama", "Plot", (cx + ax + (bx - ax) * f, cy + 1.9, cz + az + (bz - az) * f), (0.5, 0.35, dl / k + 0.1), "7CFF9A", "Neon", "Block",
              (0, kat, 0), 0.2)
    for (px, pz) in (B["a"], B["b"]):
        czesc(L, "Brama", "Slup", (cx + px, cy + 4, cz + pz), (2.2, 8, 2.2), "6B5A44", "Wood", "Block")
        czesc(L, "Brama", "SlupSwiatlo", (cx + px, cy + 8.6, cz + pz), (2.2, 2.2, 2.2), "7CFF9A", "Neon", "Ball")
    WY = D["wyspa"]
    wx, wz, rw, rz = WY["x"], WY["z"], WY["r_wew"], WY["r_zew"]
    czesc(L, "Wyspa", "Brzeg", (cx + wx, cy + 0.06, cz + wz), (0.14, rz * 2 + 2.4, rz * 2 + 2.4), "37323F", "Basalt", "Cylinder", rot)
    czesc(L, "Wyspa", "Lawa", (cx + wx, cy + 0.1, cz + wz), (0.16, rz * 2, rz * 2), "C2410F", "Neon", "Cylinder", rot)
    czesc(L, "Wyspa", "Skorupa", (cx + wx, cy + 0.14, cz + wz), (0.12, rw * 2 + 3, rw * 2 + 3), "4A2E26", "CrackedLava", "Cylinder", rot)
    czesc(L, "Wyspa", "Wyspa", (cx + wx, cy + 0.2, cz + wz), (0.16, rw * 2, rw * 2), "37323F", "Basalt", "Cylinder", rot)
    return L


def tablica_lasu(D):
    """Tablica przy bramie (po stronie łąki), przodem do łąki; sylwetki mieszkańców lasu nad nią."""
    B = brama_lasu(D)
    cx, cy, cz = D["pole"]["srodek"]
    sx, sz = B["srodek"]
    ux, uz = B["u"]
    px, pz = cx + sx - ux * 10 + uz * 22, cz + sz - uz * 10 - ux * 22
    return {"poz": [round(px, 2), cy + 5, round(pz, 2)], "patrz": [round(px - ux * 10, 2), cy + 5, round(pz - uz * 10, 2)],
            "sylwetki": [D["formy"][3]["wzorzec"], D["formy"][5]["wzorzec"], D["boss"]["wzorzec"]]}


WSTEP = r'''
local HS = game:GetService("HttpService")
if game.PlaceId == __BC__ then
	return "STOP: to miejsce gry B&C — Monster Evolution buduje się tylko w innym miejscu"
end
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio jest w trybie Play"
end
local K = "__KONTENER__"
local CH = game:GetService("ChangeHistoryService")
local stary = workspace:FindFirstChild(K)
if stary and stary:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest obcy obiekt " .. K .. " (bez atrybutu Wygenerowane) — nie ruszam"
end
'''

BUDOWA = WSTEP + r'''
local zr = HS:JSONDecode(__ZRODLA__)
local tylkoSkrypty = __TYLKO__
CH:SetWaypoint(K .. ": przed budową")
local wlaczona = if stary then stary:GetAttribute("__WYLACZNIK__") else nil
if tylkoSkrypty then
	if not stary then
		return "STOP: brak kontenera — najpierw pełna budowa"
	end
	for n, t in zr do
		local s = stary:FindFirstChild(n, true)
		if s then
			s.Source = t
		end
	end
	stary:SetAttribute("Zbudowano", "__CZAS__")
	stary:SetAttribute("Publikacja", __PUBLIKACJA__)
	stary:SetAttribute("Wydanie", "__WYDANIE__")
	CH:SetWaypoint(K .. ": skrypty")
	return "skrypty zaktualizowane"
end
local zrodloWz = workspace:FindFirstChild("PetArenaGra") and workspace.PetArenaGra:FindFirstChild("Wzorce")
if not zrodloWz then
	return "STOP: brak wzorców potworów (Workspace/PetArenaGra/Wzorce)"
end
local potrzebne = HS:JSONDecode(__WZORCE__)
local smoki = HS:JSONDecode(__SMOKI__)
for _, n in potrzebne do
	if not smoki[n] and not zrodloWz:FindFirstChild(n) then
		return "STOP: brak wzorca " .. n
	end
end
if stary then
	stary:Destroy()
end
local k = Instance.new("Folder")
k.Name = K
k:SetAttribute("Wygenerowane", true)
k:SetAttribute("Zrodlo", "swiat/ewolucja")
k:SetAttribute("Zbudowano", "__CZAS__")
k:SetAttribute("Publikacja", __PUBLIKACJA__)
k:SetAttribute("Wydanie", "__WYDANIE__")
k:SetAttribute("__WYLACZNIK__", if wlaczona == nil then true else wlaczona)
local mod = Instance.new("Folder")
mod.Name = "Moduly"
mod.Parent = k
for _, n in HS:JSONDecode(__MODULY__) do
	local m = Instance.new("ModuleScript")
	m.Name = n
	m.Source = zr[n]
	m.Parent = mod
end
local syg = Instance.new("Folder")
syg.Name = "Sygnaly"
syg.Parent = k
for _, n in { "Akcja", "Zdarzenia" } do
	local e = Instance.new("RemoteEvent")
	e.Name = n
	e.Parent = syg
end
local st = Instance.new("UnreliableRemoteEvent")
st.Name = "Stan"
st.Parent = syg
local bf = Instance.new("BindableFunction")
bf.Name = "SterowanieSerwera"
bf.Parent = syg
local wz = Instance.new("Folder")
wz.Name = "Wzorce"
wz.Parent = k
for _, n in potrzebne do
	if not smoki[n] then
		local m = zrodloWz:FindFirstChild(n):Clone()
		m:PivotTo(CFrame.new(0, -200, 0))
		m.Parent = wz
	end
end
-- stadia smoka z generatora (smok.py): części z atrybutem Grupa, punkty obrotu jako atrybuty modelu Pivot<k>
for nazwa, S in smoki do
	local m = Instance.new("Model")
	m.Name = nazwa
	for _, c in S.czesci do
		local p = Instance.new("Part")
		p.Name = c.n
		p.Anchored = true
		p.CanCollide = false
		p.CanTouch = false
		p.Shape = Enum.PartType[c.k] or Enum.PartType.Block
		if c.k == "Wedge" then
			p:Destroy()
			p = Instance.new("WedgePart")
			p.Name = c.n
			p.Anchored = true
			p.CanCollide = false
			p.CanTouch = false
		end
		p.Size = Vector3.new(c.s[1], c.s[2], c.s[3])
		p.CFrame = CFrame.new(c.p[1], c.p[2], c.p[3]) * CFrame.Angles(c.r[1], c.r[2], c.r[3])
		p.Color = Color3.fromHex(c.c)
		p.Material = Enum.Material[c.m]
		p.Transparency = c.t
		p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
		if c.g and c.g > 0 then
			p:SetAttribute("Grupa", c.g)
		end
		p.Parent = m
		if c.n == "Korzen" then
			m.PrimaryPart = p
		end
	end
	for k, v in S.pivoty do
		m:SetAttribute("Pivot" .. k, Vector3.new(v[1], v[2], v[3]))
	end
	-- kotwice zdolności (walka1): Kotwica_<Nazwa> w skali 1 (Pysk, Brzuch, Ogon, SkrzydloL, SkrzydloP)
	for n, v in S.kotwice or {} do
		m:SetAttribute("Kotwica_" .. n, Vector3.new(v[1], v[2], v[3]))
	end
	m:PivotTo(CFrame.new(0, -200, 0))
	m.Parent = wz
end
-- napis tytułu gry na łące (czytelny z kamery z góry)
do
	local p = Instance.new("Part")
	p.Name = "TytulGry"
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.Size = Vector3.new(44, 0.2, 7)
	p.CFrame = CFrame.new(__TX__, __TY__ + 0.3, __TZ__)
	p.Color = Color3.fromHex("2A2236")
	p.Material = Enum.Material.SmoothPlastic
	p.Transparency = 0.15
	p.Parent = sc
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 20
	sg.LightInfluence = 0
	sg.Parent = p
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Rotation = 180
	l.Text = "__TYTUL__"
	l.TextScaled = true
	l.Font = Enum.Font.LuckiestGuy
	l.TextColor3 = Color3.fromHex("FFC83D")
	l.Parent = sg
end
local sc = Instance.new("Folder")
sc.Name = "Scena"
sc.Parent = k
local grupy = {}
for _, c in HS:JSONDecode(__SCENA__) do
	local g = grupy[c.g]
	if not g then
		g = Instance.new("Model")
		g.Name = c.g
		g.Parent = sc
		grupy[c.g] = g
	end
	local p = Instance.new("Part")
	p.Name = c.n
	p.Anchored = true
	p.CanCollide = c.kol
	p.CanTouch = false
	p.CanQuery = c.kol
	p.Shape = Enum.PartType[c.k]
	p.Size = Vector3.new(c.s[1], c.s[2], c.s[3])
	p.CFrame = CFrame.new(c.p[1], c.p[2], c.p[3]) * CFrame.Angles(c.r[1], c.r[2], c.r[3])
	p.Color = Color3.fromHex(c.c)
	p.Material = Enum.Material[c.m]
	p.Transparency = c.t
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = g
end
-- tablica DEEP WOODS z sylwetkami mieszkańców lasu (czarne kopie wzorców)
do
	local T = HS:JSONDecode(__TABLICA__)
	local g = grupy.Brama or sc
	local cf = CFrame.lookAt(Vector3.new(T.poz[1], T.poz[2], T.poz[3]), Vector3.new(T.patrz[1], T.patrz[2], T.patrz[3]))
	local p = Instance.new("Part")
	p.Name = "Tablica"
	p.Anchored = true
	p.Size = Vector3.new(16, 7, 0.6)
	p.CFrame = cf
	p.Color = Color3.fromHex("5C4632")
	p.Material = Enum.Material.Wood
	p.Parent = g
	for _, dx in { -6.5, 6.5 } do
		local n = Instance.new("Part")
		n.Name = "Noga"
		n.Anchored = true
		n.Size = Vector3.new(0.8, 6, 0.8)
		n.CFrame = cf * CFrame.new(dx, -5, 0)
		n.Color = Color3.fromHex("4A3826")
		n.Material = Enum.Material.Wood
		n.Parent = g
	end
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Front
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 24
	sg.LightInfluence = 0
	sg.Parent = p
	for i, tx in { "__NAPIS1__", "__NAPIS2__" } do
		local l = Instance.new("TextLabel")
		l.BackgroundTransparency = 1
		l.Position = UDim2.fromScale(0.05, if i == 1 then 0.06 else 0.58)
		l.Size = UDim2.fromScale(0.9, if i == 1 then 0.5 else 0.34)
		l.Text = tx
		l.TextScaled = true
		l.Font = Enum.Font.LuckiestGuy
		l.TextColor3 = if i == 1 then Color3.fromHex("9BFFB8") else Color3.fromHex("FFC83D")
		l.Parent = sg
	end
	p:SetAttribute("Sylwetki", HS:JSONEncode(T.sylwetki))
end
for _, s in { { "SerwerEwolucji", Enum.RunContext.Server }, { "KlientEwolucji", Enum.RunContext.Client } } do
	local sk = Instance.new("Script")
	sk.Name = s[1]
	sk.RunContext = s[2]
	sk.Source = zr[s[1]]
	sk.Parent = k
end
k.Parent = workspace
CH:SetWaypoint(K .. ": zbudowano")
local czesci = 0
for _, d in sc:GetDescendants() do
	if d:IsA("BasePart") then
		czesci += 1
	end
end
return string.format("zbudowano: %d części sceny, %d wzorców, %d modułów", czesci, #wz:GetChildren(), #mod:GetChildren())
'''

WLACZ = WSTEP + r'''
if not stary then
	return "STOP: brak kontenera — najpierw zbuduj"
end
CH:SetWaypoint(K .. ": przed __WYLACZNIK__")
stary:SetAttribute("__WYLACZNIK__", __WARTOSC__)
CH:SetWaypoint(K .. ": __WYLACZNIK__ = " .. tostring(__WARTOSC__))
return "__WYLACZNIK__ = " .. tostring(stary:GetAttribute("__WYLACZNIK__"))
'''

USUN = WSTEP + r'''
if not stary then
	return "nie ma czego usuwać"
end
CH:SetWaypoint(K .. ": przed usunięciem")
stary:Destroy()
CH:SetWaypoint(K .. ": usunięto")
return "USUNIĘTO Workspace/" .. K
'''

# świat z mapy (swiat1): rekwizyty jako zakotwiczone bryły (bez stawów — statyczne), płaty ziemi, stawy; foldery według stref
SWIAT = WSTEP + r'''
if not stary then
	return "STOP: brak kontenera"
end
local P = HS:JSONDecode(__PACZKA__)
local sc = stary:FindFirstChild("Scena")
if not sc then
	return "STOP: brak sceny"
end
CH:SetWaypoint(K .. ": przed światem")
local stare = sc:FindFirstChild("Swiat")
if stare then
	stare:Destroy()
end
local sw = Instance.new("Folder")
sw.Name = "Swiat"
local C = Vector3.new(P.C[1], P.C[2], P.C[3])
local foldery = {}
local function folder(n)
	local f = foldery[n]
	if not f then
		f = Instance.new("Folder")
		f.Name = n
		f.Parent = sw
		foldery[n] = f
	end
	return f
end
local dekor = {}
for _, n in P.dekoracja do
	dekor[n] = true
end
local n = 0
for _, e in P.inst do
	local d = P.defs[e[1]]
	local cf = CFrame.new(C + Vector3.new(e[2], e[8] or 0, e[3])) * CFrame.Angles(0, math.rad(e[4]), 0)
	local sk = e[5]
	local rodzic = folder(e[6])
	if e[6] == "legowisko" or e[6] == "znak" or e[6] == "lawa" then
		local m = Instance.new("Model")
		m.Name = if e[7] > 0 then e[1] .. "_" .. e[7] else e[1]
		m.Parent = rodzic
		rodzic = m
	end
	local cien = not dekor[e[1]]
	for _, c in d.czesci do
		local ks = c[1]
		local p
		if ks == 3 then
			p = Instance.new("WedgePart")
		elseif ks == 4 then
			p = Instance.new("CornerWedgePart")
		else
			p = Instance.new("Part")
			p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
		end
		p.Name = e[1]
		p.Anchored = true
		p.CanCollide = false
		p.CanTouch = false
		p.CanQuery = false
		p.CastShadow = cien
		p.Size = Vector3.new(c[8] * sk, c[9] * sk, c[10] * sk)
		p.CFrame = cf * CFrame.new(c[2] * sk, c[3] * sk, c[4] * sk) * CFrame.fromOrientation(c[5], c[6], c[7])
		p.Color = Color3.fromHex(c[11])
		local mat = d.materialy[c[12] + 1]
		p.Material = Enum.Material[mat[1]]
		p.Reflectance = mat[2]
		p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
		if e[1] == "sztandar" and c[13] == 0 then
			p:SetAttribute("Region", 0)
		end
		p.Parent = rodzic
		n += 1
	end
end
-- mapa2a: bryły terenu [k (0 blok, 3 klin, 2 walec), px, py, pz, sx, sy, sz, o, kolor, materiał, przezr., strefa, flagi
-- (1 przenikalny — dach, 2 woda, 4 lawa)]; walec: Size = (s.y, s.x, s.x), obrót 90° wokół Z
local nt = 0
for _, t in P.teren or {} do
	local p
	if t[1] == 3 then
		p = Instance.new("WedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if t[1] == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	p.Name = if t[13] % 2 == 1 then "Dach" elseif t[13] >= 4 then "Lawa" elseif t[13] >= 2 then "Woda" else "Teren"
	p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery = true, false, false, false
	if t[1] == 2 then
		p.Size = Vector3.new(t[6], t[5], t[5])
		p.CFrame = CFrame.new(C + Vector3.new(t[2], t[3], t[4])) * CFrame.Angles(0, 0, math.rad(90))
	else
		p.Size = Vector3.new(t[5], t[6], t[7])
		p.CFrame = CFrame.new(C + Vector3.new(t[2], t[3], t[4])) * CFrame.Angles(0, math.rad(t[8]), 0)
	end
	p.Color = Color3.fromHex(t[9])
	local ok = pcall(function()
		p.Material = Enum.Material[t[10]]
	end)
	if not ok then
		p.Material = Enum.Material.SmoothPlastic
	end
	p.Transparency = t[11]
	if t[13] >= 2 then
		p.Reflectance = 0.15
	end
	p.CastShadow = t[13] < 2 and t[6] > 1
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	if t[13] % 2 == 1 then
		p:SetAttribute("Przenikalny", true)
	end
	p.Parent = folder(if t[12] == "sceneria" then "sceneria_teren" else "teren")
	nt += 1
end
-- rzeczy do rozbicia: osobne modele z nazwą id (serwer chowa je po rozbiciu)
for _, q in P.lamliwe or {} do
	local d = P.defs[q.rid]
	local m = Instance.new("Model")
	m.Name = q.id
	m:SetAttribute("Lamliwa", true)
	m.Parent = folder("lamliwe")
	local cf = CFrame.new(C + Vector3.new(q.x, 0, q.z)) * CFrame.Angles(0, math.rad(q.o), 0)
	for _, c in d.czesci do
		local ks = c[1]
		local p
		if ks == 3 then
			p = Instance.new("WedgePart")
		elseif ks == 4 then
			p = Instance.new("CornerWedgePart")
		else
			p = Instance.new("Part")
			p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
		end
		p.Name = q.rid
		p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery = true, false, false, false
		p.Size = Vector3.new(c[8] * q.sk, c[9] * q.sk, c[10] * q.sk)
		p.CFrame = cf * CFrame.new(c[2] * q.sk, c[3] * q.sk, c[4] * q.sk) * CFrame.fromOrientation(c[5], c[6], c[7])
		p.Color = Color3.fromHex(c[11])
		local mat = d.materialy[c[12] + 1]
		p.Material = Enum.Material[mat[1]]
		p.Reflectance = mat[2]
		p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
		p.Parent = m
		n += 1
	end
end
-- tablice COMING SOON w przejściach do stref rzeźby (lico na południe — w stronę kamery)
for _, tb in P.tablice or {} do
	local slup = Instance.new("Part")
	slup.Name = "TablicaSlup"
	slup.Size = Vector3.new(0.9, 6.4, 0.9)
	slup.CFrame = CFrame.new(C + Vector3.new(tb.x, 3.2, tb.z))
	slup.Color = Color3.fromHex("6B4A2E")
	slup.Material = Enum.Material.Wood
	slup.Anchored, slup.CanCollide, slup.CanTouch, slup.CanQuery = true, false, false, false
	slup.Parent = folder("tablice")
	local deska = Instance.new("Part")
	deska.Name = "Tablica"
	deska.Size = Vector3.new(11, 4.2, 0.5)
	deska.CFrame = CFrame.new(C + Vector3.new(tb.x, 6.2, tb.z - 0.6))
	deska.Color = Color3.fromHex("8A5A32")
	deska.Material = Enum.Material.WoodPlanks
	deska.Anchored, deska.CanCollide, deska.CanTouch, deska.CanQuery = true, false, false, false
	deska.Parent = folder("tablice")
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Front
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40
	sg.LightInfluence = 0.2
	sg.Parent = deska
	local function linia(tekst, y0, h, kolor)
		local l = Instance.new("TextLabel")
		l.BackgroundTransparency = 1
		l.Size = UDim2.new(0.92, 0, h, 0)
		l.Position = UDim2.new(0.04, 0, y0, 0)
		l.Text = tekst
		l.TextScaled = true
		l.Font = Enum.Font.FredokaOne
		l.TextColor3 = kolor
		local st = Instance.new("UIStroke")
		st.Thickness = 3
		st.Color = Color3.fromHex("2A1A10")
		st.Parent = l
		l.Parent = sg
	end
	linia(tb.tekst, 0.08, 0.5, Color3.fromHex("FFD24A"))
	linia(tb.pod, 0.6, 0.3, Color3.fromHex("FFF4E0"))
	nt += 2
end
-- płaty ziemi: [x, z, promień, kolor, wysokość, świeci]
local ziemia = folder("ziemia")
local np = 0
for i, pl in P.platy do
	local p = Instance.new("Part")
	p.Name = "Plat"
	p.Shape = Enum.PartType.Cylinder
	p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery, p.CastShadow = true, false, false, false, false
	local gr = if pl[3] > 200 then 2 else 0.2
	p.Size = Vector3.new(gr, pl[3] * 2, pl[3] * 2)
	p.CFrame = CFrame.new(C + Vector3.new(pl[1], pl[5] - gr / 2 + i * 0.0005, pl[2])) * CFrame.Angles(0, 0, math.pi / 2)
	p.Color = Color3.fromHex(pl[4])
	local kol = string.upper(pl[4])
	p.Material = if pl[6] then Enum.Material.Neon elseif kol == "C7B285" or kol == "B9A47C" then Enum.Material.Sand
		else Enum.Material.Grass
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	p.Parent = ziemia
	np += 1
end
-- stawy: woda (Glass 3E8FD8, przezroczystość 0,25, połysk 0,15) z piaszczystym brzegiem
local woda = folder("woda")
for _, st in P.stawy do
	for k, w in { { st[3] + 2.2, "D9C58E", Enum.Material.Sand, 0.08, 0, 0 }, { st[3], "3E8FD8", Enum.Material.Glass, 0.14, 0.25, 0.15 } } do
		local p = Instance.new("Part")
		p.Name = if k == 1 then "Brzeg" else "Woda"
		p.Shape = Enum.PartType.Cylinder
		p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery, p.CastShadow = true, false, false, false, false
		p.Size = Vector3.new(0.16, w[1] * 2, w[1] * 2)
		p.CFrame = CFrame.new(C + Vector3.new(st[1], w[4], st[2])) * CFrame.Angles(0, 0, math.pi / 2)
		p.Color = Color3.fromHex(w[2])
		p.Material = w[3]
		p.Transparency = w[5]
		p.Reflectance = w[6]
		p.Parent = woda
		np += 1
	end
end
sw.Parent = sc
CH:SetWaypoint(K .. ": świat")
local liczby = {}
for nazwa, f in foldery do
	local c = 0
	for _, d in f:GetDescendants() do
		if d:IsA("BasePart") then
			c += 1
		end
	end
	table.insert(liczby, nazwa .. " " .. c)
end
return string.format("rekwizyty: %d części, płaty i woda: %d, teren: %d; %s", n, np, nt, table.concat(liczby, ", "))
'''

# sylwetki mieszkańców lasu na tablicy (po budowie rigów: czarne, nieruchome kopie wzorców)
SYLWETKI = WSTEP + r'''
if not stary then
	return "STOP: brak kontenera"
end
local wz = stary:FindFirstChild("Wzorce")
local tab = stary:FindFirstChild("Tablica", true)
if not (wz and tab) then
	return "bez tablicy"
end
for _, s in tab.Parent:GetChildren() do
	if s.Name == "Sylwetka" then
		s:Destroy()
	end
end
local cf = tab.CFrame
local n = 0
for i, nazwa in HS:JSONDecode(tab:GetAttribute("Sylwetki") or "[]") do
	local m = wz:FindFirstChild(nazwa)
	if m then
		m = m:Clone()
		m.Name = "Sylwetka"
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				d.Color = Color3.fromHex("141018")
				d.Material = Enum.Material.SmoothPlastic
				d.CastShadow = false
				d.CanCollide = false
				d.Anchored = true
			end
		end
		for _, d in m:GetDescendants() do
			if d:IsA("JointInstance") or d:IsA("WeldConstraint") or d:IsA("Attachment") then
				d:Destroy()
			end
		end
		local _, roz = m:GetBoundingBox()
		pcall(function()
			m:ScaleTo(m:GetScale() * 5 / math.max(roz.Y, 0.1))
		end)
		m:PivotTo(cf * CFrame.new((i - 2) * 5.2, 3.6, 0) * CFrame.Angles(0, math.pi, 0))
		m.Parent = tab.Parent
		n += 1
	end
end
return "sylwetki: " .. n
'''

# rigi z danych Blendera (modele/dane, format /2): kość = niewidzialna część, Motor6D w dziecku (C0 = staw − środek rodzica,
# C1 = staw − środek), bryły na WeldConstraint (atrybut Region), zaczepy na kościach; klipy jako StringValue (JSON) w Wzorce/Klipy
RIGI = WSTEP + r'''
if not stary then
	return "STOP: brak kontenera — najpierw pełna budowa"
end
local wz = stary:FindFirstChild("Wzorce")
local P = HS:JSONDecode(__PACZKA__)
CH:SetWaypoint(K .. ": przed rigami")
local function bezFizyki(p)
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
end
local zbudowane = {}
for _, e in P.rigi do
	local D = HS:JSONDecode(e.json)
	local poprz = wz:FindFirstChild(e.nazwa)
	if poprz then
		poprz:Destroy()
	end
	local m = Instance.new("Model")
	m.Name = e.nazwa
	local hrp = Vector3.new(D.hrp[1], D.hrp[2], D.hrp[3])
	local korzen = Instance.new("Part")
	korzen.Name = "Korzen"
	korzen.Size = Vector3.new(0.4, 0.4, 0.4)
	korzen.Transparency = 1
	korzen.Anchored = true
	korzen.CastShadow = false
	bezFizyki(korzen)
	korzen.CFrame = CFrame.new(hrp)
	korzen.Parent = m
	m.PrimaryPart = korzen
	local kosci = {}
	for i, k in D.kosci do
		local p = Instance.new("Part")
		p.Name = k[1]
		p.Size = Vector3.new(math.max(0.05, k[9]), math.max(0.05, k[10]), math.max(0.05, k[11]))
		p.Transparency = 1
		p.CastShadow = false
		p.Anchored = false
		bezFizyki(p)
		p.CFrame = CFrame.new(k[6], k[7], k[8])
		p.Parent = m
		kosci[i] = p
	end
	for i, k in D.kosci do
		local rodzic, srodekRodzica
		if k[2] == 0 then
			rodzic, srodekRodzica = korzen, hrp
		else
			local kr = D.kosci[k[2]]
			rodzic, srodekRodzica = kosci[k[2]], Vector3.new(kr[6], kr[7], kr[8])
		end
		local staw = Vector3.new(k[3], k[4], k[5])
		local mo = Instance.new("Motor6D")
		mo.Name = k[12]
		mo.C0 = CFrame.new(staw - srodekRodzica)
		mo.C1 = CFrame.new(staw - Vector3.new(k[6], k[7], k[8]))
		mo.Part0 = rodzic
		mo.Part1 = kosci[i]
		mo.Parent = kosci[i]
	end
	local n = 0
	for _, c in D.czesci do
		local ks = c[2]
		local p
		if ks == 3 then
			p = Instance.new("WedgePart")
		elseif ks == 4 then
			p = Instance.new("CornerWedgePart")
		else
			p = Instance.new("Part")
			p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
		end
		p.Name = c[3]
		p.Size = Vector3.new(c[10], c[11], c[12])
		p.CFrame = CFrame.new(c[4], c[5], c[6]) * CFrame.fromOrientation(c[7], c[8], c[9])
		p.Color = Color3.fromHex(c[13])
		local mat = D.materialy[c[14] + 1]
		p.Material = Enum.Material[mat[1]]
		p.Reflectance = mat[2]
		p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
		p.Anchored = false
		bezFizyki(p)
		p:SetAttribute("Region", c[17])
		local w = Instance.new("WeldConstraint")
		w.Part0 = kosci[c[1]]
		w.Part1 = p
		w.Parent = p
		p.Parent = m
		n += 1
	end
	for _, zc in D.zaczepy do
		local a = Instance.new("Attachment")
		a.Name = zc[1]
		a.CFrame = CFrame.new(zc[3], zc[4], zc[5]) * CFrame.fromOrientation(zc[6], zc[7], zc[8])
		a.Parent = kosci[zc[2]]
	end
	korzen.PivotOffset = CFrame.new(-hrp)
	m:SetAttribute("KorzenPoz", hrp)
	m:SetAttribute("Rig", D.id)
	m:SetAttribute("Czesci", n)
	m:SetAttribute("Kosci", #D.kosci)
	m:PivotTo(CFrame.new(0, -200, 0))
	m.Parent = wz
	table.insert(zbudowane, e.nazwa .. ":" .. n)
end
local fk = wz:FindFirstChild("Klipy")
if not fk then
	fk = Instance.new("Folder")
	fk.Name = "Klipy"
	fk.Parent = wz
end
for _, e in P.klipy do
	local v = fk:FindFirstChild(e.id) or Instance.new("StringValue")
	v.Name = e.id
	v.Value = e.json
	v.Parent = fk
	table.insert(zbudowane, "klipy " .. e.id .. ":" .. #e.json)
end
CH:SetWaypoint(K .. ": rigi")
return table.concat(zbudowane, ", ")
'''

STAN = r'''
local HS = game:GetService("HttpService")
local k = workspace:FindFirstChild("__KONTENER__")
if not k or k:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, atrybuty = k:GetAttributes(), zrodla = {}, wzorce = {}, czesci = 0 }
for _, d in k:GetDescendants() do
	if d:IsA("LuaSourceContainer") then
		w.zrodla[d.Name] = { bajtow = #d.Source, straznik = string.find(d.Source, "IsStudio()", 1, true) ~= nil }
	elseif d:IsA("BasePart") and d:IsDescendantOf(k.Scena) then
		w.czesci += 1
	end
end
for _, m in k.Wzorce:GetChildren() do
	table.insert(w.wzorce, m.Name)
end
return HS:JSONEncode(w)
'''


def paczka_swiata(D):
    """Instancje rekwizytów, płaty ziemi i stawy z mapy (swiat_mapa.py) + bryły rekwizytów dla kroku SWIAT."""
    import swiat_mapa as SM
    U = DN.ustawienia()
    if U["swiat"].get("mapa") == 2:
        # mapa2a: mapa v2 (swiat_mapa2.py) — rekwizyty z y, bryły terenu, rzeczy do rozbicia (modele z id), tablice COMING SOON
        import swiat_mapa2 as M2
        W2 = M2.mapa({k: v for k, v in U["wyspa"].items() if k != "opis"}, D["legowiska"], U["swiat"].get("gestosc", 1.0),
                     U["swiat"].get("teren_v2", False))
        lam = [{"id": q["id"], "rid": q["rid"], "x": q["x"], "z": q["z"], "o": q["o"], "sk": q["sk"]} for q in W2["lamliwe"]]
        ids = sorted({i[0] for i in W2["instancje"]} | {q["rid"] for q in lam})
        return {"C": D["pole"]["srodek"], "defs": M2.definicje(ids), "inst": W2["instancje"], "platy": W2["platy"], "stawy": [],
                "dekoracja": sorted(SM.DEKORACJA), "teren": W2["teren"], "lamliwe": lam, "tablice": W2["tablice"]}
    W = {k: v for k, v in U["wyspa"].items() if k != "opis"}
    M = SM.mapa(W, D["legowiska"], D["pole"]["r"], {"x": D["las"]["x"], "z": D["las"]["z"], "r": D["las"]["r"]}, U["swiat"].get("gestosc", 1.0))
    ids = sorted({i[0] for i in M["instancje"]})
    return {"C": D["pole"]["srodek"], "defs": SM.definicje(ids), "inst": M["instancje"], "platy": M["platy"], "stawy": M["stawy"],
            "dekoracja": sorted(SM.DEKORACJA)}


def paczki_rigow():
    """Rigi i klipy zestawu blender w paczkach (jedno stadium na wywołanie: pełny rig, uproszczony, klipy; potem reszta)."""
    rigi, klipy = DN.modele_do_budowy(DN.ustawienia())

    def czyt(f):
        return open(os.path.join(DN.MODELE, f), encoding="utf-8").read()
    w = []
    for nr in range(1, 9):
        w.append({"rigi": [{"nazwa": n, "json": czyt(f)} for n, f in rigi if n in ("SmokB_%d" % nr, "SmokB_%d_lod" % nr)],
                  "klipy": [{"id": i, "json": czyt(f)} for i, f in klipy if i == "smok_%d" % nr]})
    w.append({"rigi": [{"nazwa": n, "json": czyt(f)} for n, f in rigi if not n.startswith("SmokB_") or n == "SmokB_jajo"],
              "klipy": [{"id": i, "json": czyt(f)} for i, f in klipy if not i.startswith("smok_") or i == "smok_jajo"]})
    return w


def luau_str(t):
    n = 1
    while ("]" + "=" * n + "]") in t:
        n += 1
    return "[" + "=" * n + "[" + t + "]" + "=" * n + "]"


def wstaw(szablon, **w):
    for k, v in w.items():
        szablon = szablon.replace("__%s__" % k, v)
    return szablon


def main():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--skrypty", action="store_true")
    ap.add_argument("--stan", action="store_true")
    ap.add_argument("--usun", action="store_true")
    ap.add_argument("--wlacz", choices=["on", "off"])
    ap.add_argument("--publikacja", action="store_true")
    ap.add_argument("--studio", default=None)
    ap.add_argument("--wydanie", default="studio", help="etykieta wydania (atrybut Wydanie kontenera), np. etap2")
    a = ap.parse_args()
    DN.main()
    D = DN.dane()
    zr = zrodla(a.publikacja)
    bledy = kontrola_luau()
    for b in bledy:
        log("BŁĄD Luau:", b)
    sc = scena(D)
    # wzorce z Pet Areny / generatora części (rigi zestawu blender powstają osobno, krokiem RIGI)
    wzorce = sorted({f["wzorzec"] for f in D["formy"] if not f.get("rig")} | {D["boss"]["wzorzec"]})
    log("źródła: %s (%d kB); scena: %d części; wzorce: %d; %s" % (
        ", ".join(zr), sum(len(t.encode("utf-8")) for t in zr.values()) // 1000, len(sc), len(wzorce),
        "PUBLIKACJA: bez strażnika Studio" if a.publikacja else "ze strażnikiem Studio (tylko w Studio)"))
    if bledy:
        return 1
    if a.sucho:
        return 0
    if not a.studio:
        raise SystemExit("podaj --studio <id>")
    from studio_mcp import StudioMCP
    wsp = dict(BC=str(D["miejsceBC"]), KONTENER=D["kontener"], WYLACZNIK=D["wylacznik"])
    with StudioMCP(timeout=240) as s:
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": a.studio})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit; nic nie zmieniono")
            return 1

        def wykonaj(kod, opis):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": a.studio}, timeout=240)
            t = (r["text"] or "").strip()
            if r["is_error"] or t.startswith("STOP"):
                log("PRZERWANO (%s): %s" % (opis, t[:600]))
                raise SystemExit(1)
            return t

        if a.stan:
            print(json.dumps(json.loads(wykonaj(wstaw(STAN, KONTENER=D["kontener"]), "stan")), ensure_ascii=False, indent=1))
            return 0
        if a.usun:
            log(wykonaj(wstaw(USUN, **wsp), "usuwanie"))
            return 0
        if a.wlacz:
            log(wykonaj(wstaw(WLACZ, WARTOSC="true" if a.wlacz == "on" else "false", **wsp), "wyłącznik"))
            return 0
        kod = wstaw(BUDOWA, CZAS=time.strftime("%Y-%m-%d %H:%M"), TYLKO="true" if a.skrypty else "false",
                    PUBLIKACJA="true" if a.publikacja else "false", WZORCE=luau_str(json.dumps(wzorce)), MODULY=luau_str(json.dumps(MODULY)),
                    ZRODLA=luau_str(json.dumps(zr, ensure_ascii=False)), SCENA=luau_str(json.dumps(sc)), TABLICA=luau_str(json.dumps(tablica_lasu(D))),
                    SMOKI=luau_str(json.dumps(DN.smoki(DN.ustawienia()) or {"_": None}).replace('"_": null', "")),
                    TX=str(D["pole"]["srodek"][0] + 12), TY=str(D["pole"]["srodek"][1]), TZ=str(D["pole"]["srodek"][2] - 52), TYTUL=D["ui"]["tytul_gry"],
                    NAPIS1=D["ui"]["las_tablica"], NAPIS2=D["ui"]["las_warunek"] % D["las"]["od_formy"], WYDANIE=a.wydanie.replace('"', ""), **wsp)
        log(wykonaj(kod, "budowa"))
        if not a.skrypty and D.get("blender"):
            for P in paczki_rigow():
                log("rigi:", wykonaj(wstaw(RIGI, PACZKA=luau_str(json.dumps(P, ensure_ascii=False)), **wsp), "rigi")[:300])
        if not a.skrypty and D.get("swiat"):
            log("świat:", wykonaj(wstaw(SWIAT, PACZKA=luau_str(json.dumps(paczka_swiata(D), ensure_ascii=False)), **wsp), "świat")[:300])
        if not a.skrypty:
            log(wykonaj(wstaw(SYLWETKI, **wsp), "sylwetki"))
        st = json.loads(wykonaj(wstaw(STAN, KONTENER=D["kontener"]), "stan"))
        zle = [n for n, t in zr.items() if (st["zrodla"].get(n) or {}).get("bajtow") != len(t.encode("utf-8"))]
        log("sprawdzenie: %s; wyłącznik %s = %s; publikacja %s; wydanie %s; części sceny %d" % (
            "źródła zgodne" if not zle else "NIEZGODNE: " + ", ".join(zle), D["wylacznik"], st["atrybuty"].get(D["wylacznik"]),
            st["atrybuty"].get("Publikacja"), st["atrybuty"].get("Wydanie"), st["czesci"]))
        return 1 if zle else 0


if __name__ == "__main__":
    sys.exit(main())
