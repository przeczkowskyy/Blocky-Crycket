#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Świat gry z propozycji mapy (modele/dane/mapa_propozycja.json, tylko do odczytu) → instancje do budowy w Studio,
płaty ziemi, stawy i proste kształty przeszkód dla serwera (koła w układzie pola).

Zmiany względem propozycji (reguły gry mają pierwszeństwo):
- wyspa lawy z propozycji leży za łąką w jeziorze (−250, 70) — WING GLIDE (34 st.) nie przeleci 68 st. wody, więc
  jej rekwizyty (bazalt, skały lawy, ołtarz kul) stoją na wyspie gry SKY NEST w fosie lawy (przesunięte i × 0,55);
  jezioro i jego lilie / trzciny pomijamy;
- mały staw przesunięty o (−4, −4), żeby nie stykał się z fosą wyspy;
- nic nie stoi na wyspie gry ani w fosie poza jej rekwizytami.
"""
import json
import math
import os

PAKIET = os.path.dirname(os.path.abspath(__file__))
MODELE = os.path.join(PAKIET, "modele", "dane")

# blokujące rekwizyty: koła w układzie rekwizytu (x, z, r; przód −Z); reszta to dekoracja bez kolizji
KOLA = {
    "glaz_1": [(0, 0, 2.9)], "glaz_2": [(0, 0, 2.9)],
    "drzewo_1": [(0, 0, 1.1)], "drzewo_2": [(0, 0, 1.1)], "drzewo_3": [(0, 0, 1.1)],
    "sosna_1": [(0, 0, 1.2)], "sosna_2": [(0, 0, 1.2)], "grzyb_wielki": [(0, 0, 1.5)], "filar_ruin": [(0, 0, 1.7)],
    "kloda": [(-2.2, 0, 1.0), (0, 0, 1.0), (2.2, 0, 1.0)],
    "luk_korzeni": [(-6.9, -0.3, 1.3), (6.9, -0.3, 1.3)],
    "krag_kamienny": [(-1.98, -9.29, 1.1), (-8.5, -4.25, 1.1), (-8.62, 3.99, 1.1), (-2.25, 9.23, 1.1), (5.81, 7.52, 1.1), (9.5, 0.14, 1.1),
                      (6.03, -7.34, 1.1)],
    "czaszka_smoka": [(0, 2.0, 4.6), (0, -6.6, 4.2), (0, 9.0, 2.2), (0, 13.4, 1.8), (0, 17.2, 1.4)],
    "posag_prastarego": [(0, 2.1, 11.5), (15.96, -4.2, 3.0)],
    "legowisko_krag": [(11.06, -7.74, 2.3), (13.29, -2.34, 2.3), (13.04, 3.49, 2.3), (10.34, 8.68, 2.3), (5.71, 12.24, 2.3), (0, 13.5, 2.3),
                       (-5.71, 12.24, 2.3), (-10.34, 8.68, 2.3), (-13.04, 3.49, 2.3), (-13.29, -2.34, 2.3), (-11.06, -7.74, 2.3)],
    "legowisko_brama": [(-4.6, 0, 1.2), (4.6, 0, 1.2)],
    "oltarz_kul": [(0, 0, 6.8)],
}
# strefy rekwizytów (do folderów i progów kosztu); dekoracja = można pominąć przy przerzedzaniu
DEKORACJA = {"trawa_1", "trawa_2", "kwiat_czerwony", "kwiat_zolty", "kwiat_niebieski", "kwiat_bialy", "kamyk", "krzak", "grzyb", "lilia",
             "trzcina", "grzyby_swiecace"}
LAWA = {"bazalt_1", "bazalt_2", "skala_lawy", "oltarz_kul"}


def wczytaj(plik):
    with open(os.path.join(MODELE, plik), encoding="utf-8") as f:
        return json.load(f)


def obroc(x, z, kat_st):
    """Obrót o kąt wokół pionu jak CFrame.Angles(0, rad(kąt), 0): przód (0, −1) → (−sin, −cos)."""
    a = math.radians(kat_st)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def mapa(WY, legowiska, pole_r, las, gestosc=1.0):
    """WY: wyspa gry {x, z, r_wew, r_zew}; legowiska: [[x, z]] gry; las: {x, z, r}. Zwraca instancje, płaty, stawy, przeszkody."""
    M = wczytaj("mapa_propozycja.json")
    S = M["strefy"]
    wx0, wz0, wr0 = S["wyspa_lawy"]
    sk_w = (WY["r_zew"] + 2) / wr0
    stawy = [list(s) for s in S["stawy"]]
    przes_staw = (-4.0, -4.0)
    st2 = stawy[1][:]
    stawy[1] = [st2[0] + przes_staw[0], st2[1] + przes_staw[1], st2[2]]
    inst = []
    licz = 0
    for rid, lista in M["instancje"].items():
        for i, (x, z, kat, sk) in enumerate(lista):
            if rid in DEKORACJA and gestosc < 1 and (i * 0.618) % 1 > gestosc:
                continue  # przerzedzanie dekoracji (nigdy znaków i legowisk)
            strefa = "laka"
            if rid in LAWA:
                # wyspa lawy z propozycji → wyspa gry (przesunięcie i skala)
                x, z, sk = WY["x"] + (x - wx0) * sk_w, WY["z"] + (z - wz0) * sk_w, sk * (0.5 if rid == "oltarz_kul" else sk_w * 1.1)
                strefa = "lawa"
            elif math.hypot(x - wx0, z - wz0) < S["jezioro_r"] + 8:
                continue  # jezioro wyspy z propozycji — nie ma go w grze
            elif math.hypot(x - st2[0], z - st2[1]) < st2[2] + 6:
                x, z = x + przes_staw[0], z + przes_staw[1]
                strefa = "woda"
            if strefa != "lawa" and math.hypot(x - WY["x"], z - WY["z"]) < WY["r_zew"] + 3:
                continue  # wyspa gry i fosa wolne
            if rid in ("lilia", "trzcina"):
                strefa = "woda"
            elif math.hypot(x - las["x"], z - las["z"]) < las["r"] + 30 and math.hypot(x, z) > pole_r - 5:
                strefa = "las"
            slot = 0
            if rid in ("legowisko_krag", "legowisko_brama", "sztandar"):
                strefa = "legowisko"
                slot = min(range(len(legowiska)), key=lambda k: math.hypot(x - legowiska[k][0], z - legowiska[k][1])) + 1
            elif rid in ("czaszka_smoka", "posag_prastarego", "brama_zapieczetowana", "krag_kamienny"):
                strefa = "znak"
            inst.append([rid, round(x, 2), round(z, 2), kat, round(sk, 3), strefa, slot])
            licz += 1
    platy = []
    for p in M["platy_ziemi"]:
        x, z, r = p[0], p[1], p[2]
        if math.hypot(x - wx0, z - wz0) < S["jezioro_r"] + 2:
            continue
        if math.hypot(x - WY["x"], z - WY["z"]) < WY["r_zew"] + r - 1 and r < 40:
            continue
        platy.append(p)
    # przeszkody serwera: koła blokujących rekwizytów w polu gry (łąka albo las), stawy
    prz = []
    for rid, x, z, kat, sk, strefa, slot in inst:
        for (lx, lz, r) in KOLA.get(rid, []):
            ox, oz = obroc(lx * sk, lz * sk, kat)
            px, pz, pr = x + ox, z + oz, r * sk
            w_polu = math.hypot(px, pz) < pole_r + pr or math.hypot(px - las["x"], pz - las["z"]) < las["r"] + pr
            if w_polu:
                prz.append({"typ": "lawa" if rid == "oltarz_kul" else ("legowisko" if strefa == "legowisko" else "skala"), "x": round(px, 2),
                            "z": round(pz, 2), "r": round(pr, 2), "rid": rid})
    for (x, z, r) in stawy:
        prz.append({"typ": "staw", "x": x, "z": z, "r": r})
    return {"instancje": inst, "platy": platy, "stawy": stawy, "przeszkody": prz, "liczba": licz, "czesci_rek": M["czesci_rekwizytu"]}


def definicje(ids):
    """Bryły rekwizytów (z rigów z jedną kością `Podstawa`) dla budowy w Studio."""
    w = {}
    for rid in ids:
        R = wczytaj("rekwizyt_%s_rig.json" % rid)
        w[rid] = {"czesci": [[c[1], c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12], c[13], c[16]] for c in R["czesci"]],
                  "materialy": R["materialy"]}
    return w
