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
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smok as SMOK  # noqa: E402

sys.dont_write_bytecode = True
PAKIET = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(PAKIET))
ZR = os.path.join(PAKIET, "zrodla")
PLIK = os.path.join(ZR, "DaneEwolucji.luau")
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'


MODELE = os.path.join(PAKIET, "modele", "dane")


def modele_wczytaj(plik):
    """Plik z danych modeli Blendera (swiat/ewolucja/modele/dane, format /2) — tylko do odczytu."""
    with open(os.path.join(MODELE, plik), encoding="utf-8") as f:
        return json.load(f)


def stadia_smoka(I):
    """Stadia 1–8 z indeksu (wersja 2 miała w „stadia” także jajo `smok_jajo`; wersja 3 trzyma je pod kluczem `jajo`)."""
    w = [S for S in I["stadia"] if S["id"] != "smok_jajo" and isinstance(S.get("nr"), int)]
    if [S["nr"] for S in w] != list(range(1, 9)):
        raise SystemExit("modele/dane/indeks.json: oczekiwane stadia 1–8, są %s" % [S.get("nr") for S in w])
    return w


def czasy_klipow(K):
    """Chwile z klipów (sekundy od startu) dla serwera: zamach zdolności = zdarzenie w klipie (efekt w tej klatce)."""
    fps = K["fps"]

    def zd(klip, nazwa, zapas):
        c = K["klipy"].get(klip)
        return round(c["zdarzenia"][nazwa] / fps, 3) if c and nazwa in c.get("zdarzenia", {}) else zapas
    o = zd("ogien_start", "ogien_start", 0.35)
    return {"zar": zd("splun", "strzal", 0.3), "oddech": o, "inferno": o, "ogon": zd("ogon_zamach", "uderzenie_start", 0.3),
            "lot": zd("szybowanie_start", "odbicie", 0.2), "ryk": zd("ryk", "ryk_start", 0.45), "meteor": zd("nurkowanie_skok", "odbicie", 0.45)}


def blender(U):
    """Zestaw „blender”: osiem stadiów z modele/dane (rig pełny i uproszczony, klipy), jajo, rekwizyty, owca, golem."""
    I = modele_wczytaj("indeks.json")
    if I.get("wersja") not in (2, 3):
        raise SystemExit("modele/dane/indeks.json: oczekiwana wersja 2 albo 3, jest %s" % I.get("wersja"))
    st = []
    for S in stadia_smoka(I):
        K = modele_wczytaj(S["pliki"][1])
        st.append({"nr": S["nr"], "rig": S["id"], "nazwa": S["nazwa"], "promien": S["promien_gry"], "wys": S["wymiary"]["wys"],
                   "czasy": czasy_klipow(K), "chod": K["klipy"]["chod"].get("predkosc"), "bieg": K["klipy"]["bieg"].get("predkosc")})
    G = U.get("blender", {})
    return {"stadia": st, "stawy": I["stawy"], "zaczepy": I["zaczepy"], "regiony": I["regiony"],
            "rekwizyty": [r["id"] for r in I.get("rekwizyty", [])], "stwory": [s["id"] for s in I.get("stwory", [])],
            "lod": G.get("lod", {}), "warianty": G.get("warianty", {}), "golem": G.get("golem")}


def modele_do_budowy(U):
    """Dla zbuduj.py: [(wzorzec, plik rigu)] i [(id klipów, plik klipów)] zestawu „blender”."""
    I = modele_wczytaj("indeks.json")
    rigi, klipy = [], []
    U = ustawienia()
    # pisklę: „obecne” (smok_1_rig) albo „lagodne” (wariant modelu z indeksu 3: te same stawy, zaczepy i klipy)
    piskle = U.get("blender", {}).get("piskle", "obecne")
    zamiana = {}
    for W in I.get("warianty_modeli", []):
        if piskle == "lagodne" and W["id"] == "smok_1_lagodny":
            zamiana[W["zamiast"]] = W["plik"]
    for S in stadia_smoka(I):
        rigi.append(("SmokB_%d" % S["nr"], zamiana.get(S["id"], S["pliki"][0])))
        rigi.append(("SmokB_%d_lod" % S["nr"], S["plik_lod"]))
        klipy.append((S["id"], S["pliki"][1]))
    rigi.append(("SmokB_jajo", "smok_jajo_rig.json"))
    klipy.append(("smok_jajo", "smok_jajo_klipy.json"))
    for r in I.get("rekwizyty", []):
        rigi.append(("Rekwizyt_" + r["id"], r["plik"]))
    # efekty (indeks 3): stożek ognia (rig + klip „migotanie”) i przypalona ziemia INFERNO
    for E in I.get("efekty", []):
        if "pliki" in E:
            rigi.append(("Efekt_" + E["id"], E["pliki"][0]))
            klipy.append((E["id"], E["pliki"][1]))
        elif "plik" in E:
            rigi.append(("Rekwizyt_" + E["id"], E["plik"]))
    # świat (swiat1): kule trzech rozmiarów i kopce złota legowiska jako wzorce dla klienta
    for rid in ("kula_mala", "kula_duza", "kula_wielka", "stos_zlota_1", "stos_zlota_2", "stos_zlota_3"):
        if os.path.exists(os.path.join(MODELE, "rekwizyt_%s_rig.json" % rid)):
            rigi.append(("Rekwizyt_" + rid, "rekwizyt_%s_rig.json" % rid))
    for s in I.get("stwory", []):
        rigi.append(("Stwor_" + s["id"], s["pliki"][0]))
        klipy.append((s["id"], s["pliki"][1]))
    return rigi, klipy


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


def przeszkody(P, LS=None):
    """Skały, drzewa i stawy w polu i w lesie (koła dla logiki), powtarzalne."""
    los = random.Random(11)
    R = P["r"]
    w = [{"typ": "staw", "x": -78.0, "z": 58.0, "r": 11.0}]
    while len([s for s in w if s["typ"] == "skala"]) < P["skal"]:
        a, r = los.random() * 2 * math.pi, 34 + los.random() * (R - 60)
        s = {"typ": "skala", "x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "r": round(5 + los.random() * 4.5, 2)}
        if all(math.hypot(s["x"] - q["x"], s["z"] - q["z"]) > s["r"] + q["r"] + 22 for q in w):
            w.append(s)
    while len([s for s in w if s["typ"] == "drzewo"]) < P["drzew_w_polu"]:
        a, r = los.random() * 2 * math.pi, 40 + los.random() * (R - 58)
        s = {"typ": "drzewo", "x": round(math.sin(a) * r, 2), "z": round(math.cos(a) * r, 2), "r": 2.4, "h": round(16 + los.random() * 8, 1)}
        if not (s["z"] > 100 and abs(s["x"]) < 85) and all(math.hypot(s["x"] - q["x"], s["z"] - q["z"]) > s["r"] + q["r"] + 20 for q in w):
            w.append(s)
    if LS:
        lx, lz, LR = LS["srodek"][0], LS["srodek"][1], LS["r"]
        w.append({"typ": "staw", "x": lx + 42.0, "z": lz + 30.0, "r": 12.0})
        n = 0
        while n < LS["drzew_w_lesie"]:
            a, r = los.random() * 2 * math.pi, 25 + los.random() * (LR - 40)
            s = {"typ": "drzewo", "x": round(lx + math.sin(a) * r, 2), "z": round(lz + math.cos(a) * r, 2), "r": 3.0, "h": round(24 + los.random() * 10, 1),
                 "las": True}
            if s["z"] > 160 and all(math.hypot(s["x"] - q["x"], s["z"] - q["z"]) > s["r"] + q["r"] + 18 for q in w):
                w.append(s)
                n += 1
    return w


SIATKA = 24


def siatka_przeszkod(prz, zapas=12.0):
    """Siatka komórek SIATKA st.: klucz (cx + 100) * 1000 + (cz + 100) → indeksy przeszkód (od 1) w zasięgu r + zapas."""
    w = {}
    for i, s in enumerate(prz, 1):
        R = s["r"] + zapas
        for cx in range(int(math.floor((s["x"] - R) / SIATKA)), int(math.floor((s["x"] + R) / SIATKA)) + 1):
            for cz in range(int(math.floor((s["z"] - R) / SIATKA)), int(math.floor((s["z"] + R) / SIATKA)) + 1):
                w.setdefault(str((cx + 100) * 1000 + (cz + 100)), []).append(i)
    return {"krok": SIATKA, "komorki": w}


def kulki(P, J, prz, LS=None):
    """Stałe miejsca kulek: [x, z, typ] (1 mała, 2 duża, 3 wielka — tylko w lesie), z dala od przeszkód."""
    los = random.Random(7)
    w = []
    G = ustawienia()["legowisko"]
    for (dx, dz) in legowiska(G):
        d = math.hypot(dx, dz)
        ux, uz = -dx / d, -dz / d
        for j in range(G.get("kulki_startowe", 0)):
            odl = G["r"] + 2.5 + j * 2.2
            bok = (j % 3 - 1) * 2.2
            w.append([round(dx + ux * odl - uz * bok, 2), round(dz + uz * odl + ux * bok, 2), 1])
    if LS:
        lx, lz = LS["srodek"]
        for typ, ile in ((3, LS["wielkie"]), (2, LS["duze"])):
            n = 0
            while n < ile:
                a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (LS["r"] - 6)
                x, z = round(lx + math.sin(a) * r, 2), round(lz + math.cos(a) * r, 2)
                if math.hypot(x, z) > P["r"] + 4 and all(math.hypot(x - s["x"], z - s["z"]) > s["r"] + 2.5 for s in prz):
                    w.append([x, z, typ])
                    n += 1
    WY = ustawienia().get("wyspa")
    for typ, ile in ((2, J["duze"]), (1, J["male"])):
        n = 0
        while n < ile:
            a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (P["r"] - 5)
            x, z = round(math.sin(a) * r, 2), round(math.cos(a) * r, 2)
            if all(math.hypot(x - s["x"], z - s["z"]) > s["r"] + 2.5 for s in prz) and not (WY and math.hypot(x - WY["x"], z - WY["z"]) < WY["r_zew"] + 2):
                w.append([x, z, typ])
                n += 1
    if WY:
        # SKY NEST: wielkie kulki na wyspie (tylko szybowaniem albo skokiem meteoru)
        for i in range(WY["kulek"]):
            a = 2 * math.pi * i / WY["kulek"]
            w.append([round(WY["x"] + math.sin(a) * WY["r_wew"] * 0.55, 2), round(WY["z"] + math.cos(a) * WY["r_wew"] * 0.55, 2), 3])
    return w


def kulki_v2(P, J, W2, LS):
    """mapa2a: kule startowe przy legowiskach, las jak dotąd, kule łąki rozsiane po wszystkich strefach maski 1 (łąka, polana,
    jezioro, wąwóz bramy, szlak) z dala od przeszkód, wody i głębi; wielkie kule na SKY NEST."""
    import swiat_mapa2 as M2
    los = random.Random(7)
    w = []
    G = ustawienia()["legowisko"]
    for (dx, dz) in legowiska(G):
        d = math.hypot(dx, dz)
        ux, uz = -dx / d, -dz / d
        for j in range(G.get("kulki_startowe", 0)):
            odl = G["r"] + 2.5 + j * 2.2
            bok = (j % 3 - 1) * 2.2
            w.append([round(dx + ux * odl - uz * bok, 2), round(dz + uz * odl + ux * bok, 2), 1])
    lx, lz = LS["srodek"]
    for typ, ile in ((3, LS["wielkie"]), (2, LS["duze"])):
        n = 0
        while n < ile:
            a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (LS["r"] - 6)
            x, z = round(lx + math.sin(a) * r, 2), round(lz + math.cos(a) * r, 2)
            if math.hypot(x, z) > P["r"] + 4 and M2.wolny_punkt(W2, x, z, 2.5, 2):
                w.append([x, z, typ])
                n += 1
    WY = W2["wyspa"]
    # łąka: tyle kul co dotąd (gęstość startu bez zmian), potem nowe strefy: + ok. 30% (polana, jezioro, wąwóz, szlak)
    for typ, ile in ((2, J["duze"]), (1, J["male"])):
        n = 0
        while n < ile:
            a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (P["r"] - 5)
            x, z = round(math.sin(a) * r, 2), round(math.cos(a) * r, 2)
            if M2.wolny_punkt(W2, x, z, 2.5, 1) and not M2.w_wodzie(W2, x, z) and math.hypot(x - WY["x"], z - WY["z"]) > WY["r_zew"] + 2:
                w.append([x, z, typ])
                n += 1
    for typ, ile in ((2, round(J["duze"] * 0.3)), (1, round(J["male"] * 0.3))):
        n = 0
        while n < ile:
            x, z = round(-200 + los.random() * 440, 2), round(-265 + los.random() * 420, 2)
            if math.hypot(x, z) < P["r"] + 2 or (math.hypot(x - lx, z - lz) < LS["r"] + 2):
                continue
            if M2.wolny_punkt(W2, x, z, 2.5, 1) and not M2.w_wodzie(W2, x, z):
                w.append([x, z, typ])
                n += 1
    for i in range(WY["kulek"]):
        a = 2 * math.pi * i / WY["kulek"]
        w.append([round(WY["x"] + math.sin(a) * WY["r_wew"] * 0.55, 2), round(WY["z"] + math.cos(a) * WY["r_wew"] * 0.55, 2), 3])
    return w


def punkty_botow(W2, formy):
    """mapa2a: miejsca odrodzenia botów maski 1 rozsiane po strefach (łąka i nowe kieszenie, waga nowych × 2), z największym
    promieniem, który się tam mieści (polana i tunel tylko dla małych)."""
    import swiat_mapa2 as M2
    los = random.Random(17)
    rr = sorted({f["r"] for f in formy})
    w = []
    proby = 0
    while len(w) < 160 and proby < 20000:
        proby += 1
        x, z = -200 + los.random() * 440, -265 + los.random() * 420
        st = M2.strefa_punktu(W2["M"], x, z)
        if st not in ("laka", "polana", "jezioro", "brama", "szlak_popiolu"):
            continue
        if st == "laka" and los.random() < 0.5:
            continue  # nowe strefy gęściej niż łąka (waga × 2)
        rm = 0
        for r in rr:
            if M2.wolny_punkt(W2, x, z, r, 1) and not M2.w_wodzie(W2, x, z):
                rm = r
        if rm > 0:
            w.append([round(x, 1), round(z, 1), rm])
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
    kepki = []
    for i in range(P["kepek"]):
        a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (R - 4)
        kepki.append([round(math.sin(a) * r, 2), round(math.cos(a) * r, 2), round(los.random() * 6.28, 2)])
    grzyby = []
    for i in range(P["grzybow"]):
        a, r = los.random() * 2 * math.pi, 30 + los.random() * (R - 40)
        grzyby.append([round(math.sin(a) * r, 2), round(math.cos(a) * r, 2), round(0.8 + los.random() * 0.8, 2)])
    krzaki = []
    for i in range(P["krzakow"]):
        a = 2 * math.pi * (i + los.random() * 0.5) / P["krzakow"]
        r = R + 5 + los.random() * 5
        krzaki.append([round(math.sin(a) * r, 2), round(math.cos(a) * r, 2), round(3 + los.random() * 3, 1)])
    return {"plamy": plamy, "drzewa": drzewa, "kwiaty": kwiaty, "kepki": kepki, "grzyby": grzyby, "krzaki": krzaki}


def smoki(U):
    """Modele stadiów smoka do budowy w Studio (zbuduj.py): {wzorzec: {czesci, pivoty}}."""
    w = {}
    if U.get("zestaw", "smok") != "smok":
        return w
    for i, F in enumerate(U["formy_smok"]):
        w["Smok_%d" % (i + 1)] = SMOK.stadium(F["smok"])
    return w


def wystroj_lasu(LS):
    """Tylko scena lasu: drzewa za murem lasu, grzyby, plamy ciemnej ściółki."""
    los = random.Random(13)
    lx, lz, R = LS["srodek"][0], LS["srodek"][1], LS["r"]
    drzewa, grzyby, plamy = [], [], []
    for i in range(LS["drzew_za_murem"]):
        a = 2 * math.pi * (i + los.random() * 0.6) / LS["drzew_za_murem"]
        x, z = lx + math.sin(a) * (R + 10 + los.random() * 22), lz + math.cos(a) * (R + 10 + los.random() * 22)
        if math.hypot(x, z) > 170:
            drzewa.append({"x": round(x, 2), "z": round(z, 2), "h": round(26 + los.random() * 16, 1)})
    for i in range(LS["grzybow"]):
        a, r = los.random() * 2 * math.pi, 10 + los.random() * (R - 16)
        x, z = lx + math.sin(a) * r, lz + math.cos(a) * r
        if math.hypot(x, z) > 158:
            grzyby.append([round(x, 2), round(z, 2), round(1.0 + los.random() * 1.2, 2)])
    for i in range(10):
        a, r = los.random() * 2 * math.pi, math.sqrt(los.random()) * (R - 20)
        x, z = lx + math.sin(a) * r, lz + math.cos(a) * r
        if math.hypot(x, z) > 160:
            plamy.append({"x": round(x, 2), "z": round(z, 2), "r": round(10 + los.random() * 14, 1), "c": ["3E7A33", "4A6B2E", "5C4A32"][i % 3],
                          "m": ["LeafyGrass", "Grass", "Ground"][i % 3]})
    return {"drzewa": drzewa, "grzyby": grzyby, "plamy": plamy}


def legowiska(G):
    """Środki legowisk na skraju łąki (kąt 0 = północ, tam brama lasu — pomijamy)."""
    w = []
    for i in range(G["miejsc"]):
        a = math.radians(G["kat_od"] + (G["kat_do"] - G["kat_od"]) * i / max(1, G["miejsc"] - 1))
        w.append([round(math.sin(a) * G["odleglosc"], 2), round(math.cos(a) * G["odleglosc"], 2)])
    return w


def dane():
    U = ustawienia()
    PA = _pa()
    UP, DP, _ = PA.wszystkie_pliki()
    pety = {p["id"]: p for p in DP["pety"]}
    formy = []
    zestaw = U.get("zestaw", "smok")
    BL = blender(U) if zestaw == "blender" else None
    for i, F in enumerate(U["formy_" + ("smok" if zestaw == "blender" else zestaw)]):
        f = {k: v for k, v in F.items() if k not in ("pet", "boss", "smok")}
        if BL:
            S = BL["stadia"][i]
            f["wzorzec"], f["wzorzecLod"], f["rig"] = "SmokB_%d" % (i + 1), "SmokB_%d_lod" % (i + 1), S["rig"]
            f["model_r"], f["model_h"], f["czasy"] = S["promien"], S["wys"], S["czasy"]
        elif "smok" in F:
            S = SMOK.stadium(F["smok"])
            f["wzorzec"], f["model_r"], f["model_h"] = "Smok_%d" % (i + 1), S["promien"], S["wysokosc"]
        elif "pet" in F:
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
    CHODY = {"skok": {"podskok": 0.32, "pochyl": 0.12, "krok": 1.0}, "klus": {"podskok": 0.1, "pochyl": 0.14, "krok": 1.3},
             "dwunozny": {"podskok": 0.14, "pochyl": 0.1, "krok": 1.1}, "pelzanie": {"podskok": 0.02, "pochyl": 0.04, "krok": 0.8}}
    for f in formy:
        for k, v in CHODY[f.get("chod", "skok")].items():
            f.setdefault(k, v)
        f.setdefault("anim", None)  # opcjonalnie: {"chod": id, "gryz": id} dla modelu ze szkieletem (Animator)
    for a, b in zip(formy, formy[1:]):
        if b["r"] <= a["r"]:
            raise SystemExit("formy: promienie muszą rosnąć")
    P = dict(U["pole"])
    P.pop("opis", None)
    LS = {k: v for k, v in U["las"].items() if k != "opis"}
    prz = przeszkody(P, LS)
    SW = None
    W2 = None
    if zestaw == "blender" and U.get("swiat", {}).get("mapa") == 2:
        # mapa2a: mapa v2 na płaskiej ziemi (swiat_mapa2.py) — obszar ze stref, przeszkody (koła i prostokąty), woda, bramy, kryjówki
        import swiat_mapa2 as M2
        W2 = M2.mapa({k: v for k, v in U["wyspa"].items() if k != "opis"}, legowiska(U["legowisko"]), U["swiat"].get("gestosc", 1.0),
                     U["swiat"].get("teren_v2", False))
        prz = W2["przeszkody"]
        SW = {"stawy": []}
    elif zestaw == "blender" and U.get("swiat", {}).get("mapa"):
        # świat z propozycji mapy: przeszkody = koła blokujących rekwizytów + stawy (swiat_mapa.py)
        import swiat_mapa as SM
        WY0 = {k: v for k, v in U["wyspa"].items() if k != "opis"}
        SW = SM.mapa(WY0, legowiska(U["legowisko"]), P["r"], {"x": LS["srodek"][0], "z": LS["srodek"][1], "r": LS["r"]},
                     U["swiat"].get("gestosc", 1.0))
        prz = SW["przeszkody"]
    J = {k: v for k, v in U["jedzenie"].items() if k != "opis"}
    B = {k: v for k, v in U["boss"].items() if k != "opis"}
    if B["model"] not in [b["model"] for b in UP["boss"]["modele"]]:
        raise SystemExit("boss: nieznany model %s" % B["model"])
    B["wzorzec"], B["model_r"], B["model_h"] = "Boss_" + B["model"], UP["boss"]["promien"], UP["boss"]["wysokosc"]
    B["chod"] = "pelzanie"
    if zestaw == "blender" and U.get("blender", {}).get("golem"):
        # KNIGHT GOLEM zamiast węża: zamach do chwili ciosu w klipie „zamach” (serwer czeka tyle przed raną)
        K = modele_wczytaj("golem_1_klipy.json")
        B["zamach_s"] = round(K["klipy"]["zamach"]["zdarzenia"]["uderzenie"] / K["fps"], 3)
        B["golem"] = True
        B["nazwa"] = "KNIGHT GOLEM"
    B.update({"podskok": 0.02, "pochyl": 0.04, "krok": 0.8, "anim": None})
    D = {
        "kontener": U["kontener"], "prefiks": U["prefiks"], "wylacznik": U["wylacznik"], "wzorceRS": U["wzorce_rs"], "ui": U["ui"],
        # interfejs1: numery obrazów ikon (0 = brak, zastępstwo w grze) — tabela w ustawienia.json, klucz „ikony.id”
        "ikony": {k: v for k, v in U.get("ikony", {}).get("id", {}).items()},
        # odrodzenie1: odrodzenie i linie smoków, wydarzenia zegarowe, jajo dnia
        "odrodzenie": {k: v for k, v in U["odrodzenie"].items() if k != "opis"},
        "wydarzenia": {k: v for k, v in U["wydarzenia"].items() if k != "opis"},
        "jajo_dnia": {k: v for k, v in U["jajo_dnia"].items() if k != "opis"},
        # retencja1: seria logowań, zadania dnia, ranking odrodzeń
        "seria": {k: v for k, v in U["seria"].items() if k != "opis"},
        "zadania": {k: v for k, v in U["zadania"].items() if k != "opis"},
        "ranking": {k: v for k, v in U["ranking"].items() if k != "opis"},
        # odczucie1: tabela dźwięków gry (0 = cisza), sklep (flaga i numery produktów)
        "dzwiekiGry": dict(U["dzwieki_gry"]["id"]),
        "sklep": {k: v for k, v in U["sklep"].items() if k != "opis"},
        "pole": P, "przeszkody": prz, "przSiatka": siatka_przeszkod(prz), "kulkiPoz": kulki_v2(P, J, W2, LS) if W2 else kulki(P, J, prz, LS),
        "jedzenie": J, "formy": formy,
        "las": {"nazwa": LS["nazwa"], "x": LS["srodek"][0], "z": LS["srodek"][1], "r": LS["r"], "od_formy": LS["od_formy"]}, "boss": B,
        "legowisko": {k: v for k, v in U["legowisko"].items() if k != "opis"}, "legowiska": legowiska(U["legowisko"]),
        "warianty": U["warianty"], "zapis": {k: v for k, v in U["zapis"].items() if k != "opis"},
        "olbrzym": {k: v for k, v in U["olbrzym"].items() if k != "opis"},
        "ruch": {k: v for k, v in U["ruch"].items() if k != "opis"},
        "gryzienie": {k: v for k, v in U["gryzienie"].items() if k != "opis"},
        "walka": {k: v for k, v in U["walka"].items() if k != "opis"},
        "zdolnosci": {k: v for k, v in U["zdolnosci"].items() if k != "opis"},
        "wyspa": W2["wyspa"] if W2 else {k: v for k, v in U["wyspa"].items() if k != "opis"},
        "ulepszenia": U["ulepszenia"],
        "smierc": {k: v for k, v in U["smierc"].items() if k != "opis"},
        "ewolucja": {k: v for k, v in U["ewolucja"].items() if k != "opis"},
        "boty": {k: v for k, v in U["boty"].items() if k != "opis"},
        "siec": {k: v for k, v in U["siec"].items() if k != "opis"},
        "kamera": U["kamera"],
        "dzwieki": {"arkusz": DP["dzwieki"]["arkusz"], "efekty": {r: DP["dzwieki"]["efekty"][r] for r in U["dzwieki"] if r in DP["dzwieki"]["efekty"]}},
        "miejsceBC": U["miejsce_bc"],
        "zestaw": zestaw,
        "blender": BL,
        "swiat": ({k: v for k, v in U["swiat"].items() if k not in ("opis", "mapa", "gestosc", "mapa_opis", "owce_v2_dodatkowe")} | {"stawy": SW["stawy"]})
        if SW else None,
    }
    if W2:
        D["swiat"]["owce"] = dict(D["swiat"]["owce"], stada=[list(p) for p in W2["owce"]] + U["swiat"].get("owce_v2_dodatkowe", []))
        D["ranking"] = dict(D["ranking"], x=W2["ranking"][0], z=W2["ranking"][1])
        nastroj = {sid: W2["strefy"][sid]["nastroj"] for sid in ("polana", "jezioro", "brama", "szlak_popiolu") if W2["strefy"][sid]["nastroj"]}
        D["mapa2"] = {"obszar": W2["obszar"], "woda": W2["woda"], "suche": W2["suche"], "woda_x": W2["woda_x"], "glebia": W2["glebia"],
                      "podesty": W2["podesty"], "bramy": W2["bramy"], "kryjowki": W2["kryjowki"], "sekrety": W2["sekrety"],
                      "lamliwe": [{k: v for k, v in q.items() if k not in ("rid", "sk", "o")} for q in W2["lamliwe"]],
                      "przenikalne": W2["przenikalne"], "nastroj": nastroj, "punktyBotow": punkty_botow(W2, formy),
                      "sekret_r": 2.5, "ukrycie_bot_st": 8, "odkrycie_s": 1.5, "lamliwa_x": {"ogon": 2, "meteor": 2}, "rozbite": {}}
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
