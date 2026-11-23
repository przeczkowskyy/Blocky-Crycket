#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapa v2 w grze (mapa2a): modele/dane/mapa_v2.json (format smok-ewolucji-mapa/2, tylko do odczytu) → instancje rekwizytów,
bryły terenu, przeszkody serwera (koła i prostokąty), obszar gry (suma kształtów stref), woda, głębia, bramy rozmiaru, kryjówki,
rzeczy do rozbicia, sekrety dnia i tablice COMING SOON.

Tryb A (flaga `teren_v2` wyłączona, ziemia płaska — ruch, boty, kamera i kule bez wysokości):
- pagóry łąki (Kwietny Pagór, Bazaltowy Stół) spłaszczone: ich bryły nie powstają, rekwizyty z nich stoją na y = 0;
- chodzi się po łące, Ukrytej Polanie, DEEP WOODS, Lily Lake, wąwozie Sealed Gate i Szlaku Popiołu;
- strefy rzeźby (wyżyna, kanion, kotlina wodospadu, kaldera) stoją jako sceneria za granicą obszaru gry; w przejściach głazy
  i tablica COMING SOON; runy, prądy, gniazdo i skrzynie w tych strefach wyłączone (etap B);
- SKY NEST zostaje na łące; rzeka v2 płynie przez jej dawne miejsce (−36, −42), więc wyspa przesuwa się na najbliższe wolne
  miejsce łąki (`WYSPA_A`), a rekwizyty z wyspy kaldery (bazalt, ołtarz kul) stoją na niej jak w v1.
Wzory brył: kontrakt w modele/README.md („Mapa v2”): CFrame = CFrame.new(p) * CFrame.Angles(0, rad(o), 0); lokalne
z = dx·sin o + dz·cos o, lokalne x = dx·cos o − dz·sin o.
"""
import json
import math
import os

import swiat_mapa as SM

PAKIET = os.path.dirname(os.path.abspath(__file__))
MODELE = os.path.join(PAKIET, "modele", "dane")

CHODZONE = ("laka", "polana", "las", "jezioro", "brama", "szlak_popiolu")
SCENERIA = ("wodospad", "kanion", "kaldera", "wyzyna", "punkt_widokowy", "przyszla_kraina")
PRIORYTET = ("polana", "jezioro", "brama", "szlak_popiolu", "wodospad", "kanion", "kaldera", "wyzyna", "punkt_widokowy", "przyszla_kraina",
             "las", "laka")
WYLACZONE_A = {"kamien_runiczny", "wiatr_kolumna", "gniazdo_orle"}  # runy i prądy wznoszące — etap B
SEKRETY_A = ("S01", "S02", "S03", "S04", "S07", "S08", "S11", "S13")
LAMLIWE_A = ("L03", "L04", "L06")
BRAMY_A = ("B01", "B02", "B03", "B05")
SPLASZCZ = ("pagor_kwietny", "stol_zachodni")
ZNAKI = {"czaszka_wielka", "posag_prastarego", "brama_zapieczetowana", "krag_kamienny", "punkt_widokowy"}
KROK = 2.0
# przejścia do stref rzeźby (A): środek przejścia, kierunek osi (o), szerokość, nazwa strefy na tablicy
PRZEJSCIA_A = [
    {"strefa": "kanion", "nazwa": "WIND CANYON", "x": -151.0, "z": 27.2, "o": 280.4, "szer": 30.0},
    {"strefa": "wodospad", "nazwa": "WATERFALL BASIN", "x": -122.5, "z": 90.0, "o": 306.3, "szer": 18.0},
    {"strefa": "kaldera", "nazwa": "LAVA CALDERA", "x": -249.0, "z": -102.0, "o": 270.0, "szer": 22.0},
]
# SKY NEST w A: dawne miejsce (−36, −42) leży w nurcie rzeki v2 — najbliższe wolne miejsce łąki (szukaj_wyspy)
WYSPA_A = (-66.0, -54.0)


def wczytaj():
    with open(os.path.join(MODELE, "mapa_v2.json"), encoding="utf-8") as f:
        return json.load(f)


def lok(dx, dz, o):
    a = math.radians(o)
    return dx * math.cos(a) - dz * math.sin(a), dx * math.sin(a) + dz * math.cos(a)


def swiat_xz(lx, lz, o):
    a = math.radians(o)
    return lx * math.cos(a) + lz * math.sin(a), -lx * math.sin(a) + lz * math.cos(a)


def w_ksztalcie(k, x, z, m=0.0):
    if "kolo" in k:
        cx, cz, r = k["kolo"]
        return math.hypot(x - cx, z - cz) <= r + m
    if "prostokat" in k:
        x0, x1, z0, z1 = k["prostokat"]
        return x0 - m <= x <= x1 + m and z0 - m <= z <= z1 + m
    cx, cz, sz, dl, o = k["pas"]
    lx, lz = lok(x - cx, z - cz, o)
    return abs(lx) <= sz / 2 + m and abs(lz) <= dl / 2 + m


def strefa_punktu(M, x, z):
    S = {s["id"]: s for s in M["strefy"]["lista"]}
    for sid in PRIORYTET:
        if any(w_ksztalcie(k, x, z) for k in S[sid]["obszar"]):
            return sid
    return "obramowanie"


def bryla_prost(t):
    """Obrys bryły terenu jako prostokąt (blok, klin) albo koło (walec): {k, x, z, o, hx, hz} / {k, x, z, r}."""
    if t["k"] == "walec":
        return {"k": "k", "x": t["p"][0], "z": t["p"][2], "r": t["s"][0] / 2}
    return {"k": "p", "x": t["p"][0], "z": t["p"][2], "o": t["o"], "hx": t["s"][0] / 2, "hz": t["s"][2] / 2}


def w_obrysie(f, x, z, m=0.0):
    if f["k"] == "k":
        return math.hypot(x - f["x"], z - f["z"]) <= f["r"] + m
    lx, lz = lok(x - f["x"], z - f["z"], f["o"])
    return abs(lx) <= f["hx"] + m and abs(lz) <= f["hz"] + m


def _r(v, n=2):
    return round(v, n)


def mapa(WY, legowiska, gestosc=1.0, teren=False):
    """WY: wyspa gry {x, z, r_wew, r_zew}. Zwraca wszystko dla dane.py (logika) i zbuduj.py (scena). teren=True — etap B (nie teraz)."""
    if teren:
        raise SystemExit("mapa v2: etap B (teren_v2) jeszcze nie zrobiony")
    M = wczytaj()
    Z = {s["id"]: s for s in M["strefy"]["lista"]}
    bez_kol = set(M["bez_kolizji"])
    kol_nowe = M["kolizje_rekwizytow"]
    # --- teren
    splaszczone, teren_bud, przeszkody, woda, suche, glebie, podesty = [], [], [], [], [], [], []
    for t in M["teren"]:
        s = t["strefa"]
        chodzona = s in CHODZONE or s == "rzeka"
        if t["id"].startswith(SPLASZCZ):
            splaszczone.append(bryla_prost(t))
            continue
        top, dol = t["p"][1] + t["s"][1] / 2, t["p"][1] - t["s"][1] / 2
        if t.get("widoczny") is False:
            if chodzona and t["chodzi"]:
                suche.append(bryla_prost(t))
                podesty.append(dict(bryla_prost(t), y=_r(top)))
            continue
        teren_bud.append(t)
        if not chodzona:
            continue
        f = bryla_prost(t)
        if t.get("woda"):
            woda.append(f)
        elif t.get("glebia"):
            glebie.append(f)
        elif t["chodzi"] and 0.3 < top <= KROK:
            podesty.append(dict(f, y=_r(top)))
        elif not t["chodzi"] and not t.get("ozdoba") and not t.get("przenikalny") and dol <= KROK and top > 0.6:
            przeszkody.append(dict(f, typ="skala", rid=t["id"]))
    # głębia jeziora: wolne miejsca = wysepka (podest) i bród (woda) wewnątrz
    glebia = []
    for g in glebie:
        wolne = [f for f in podesty + woda if w_obrysie(g, f["x"], f["z"])]
        glebia.append({"obrys": g, "wolne": [{k: v for k, v in f.items() if k != "y"} for f in wolne]})
    # --- wyspa gry (A: na łące, poza rzeką)
    WYG = dict(WY)
    if WYSPA_A:
        WYG["x"], WYG["z"] = WYSPA_A
    wx0, wz0 = M["wyspa"]["x"], M["wyspa"]["z"]
    sk_w = WYG["r_wew"] / M["wyspa"]["r_wew"]
    # --- rzeczy do rozbicia (A: L03, L04, L06); instancje na ich miejscach budowane osobno (model z nazwą id)
    lamliwe = []
    for e in M["lamliwe"]:
        if e["id"] not in LAMLIWE_A:
            continue
        kola = [[_r(c[0]), _r(c[1]), _r(c[2])] for c in e["kola"]]
        q = {"id": e["id"], "rid": e["rekwizyt"], "x": e["x"], "z": e["z"], "o": e["o"], "sk": e["skala"], "hp": e["hp"], "odrost_s": e["odrost_s"],
             "zloto": e["zloto"], "od": e["od_stadium"], "kola": kola, "prost": [],
             "r": _r(max(math.hypot(c[0] - e["x"], c[1] - e["z"]) + c[2] for c in kola))}
        if e["id"] == "L06":
            # wyłom w murze: skała zamyka całą szerokość Szlaku Popiołu (koło 7,5 zostawiało szpary przy ścianach korytarza)
            q["prost"].append({"k": "p", "x": e["x"], "z": e["z"], "o": 90.0, "hx": 12.5, "hz": 3.2})
        lamliwe.append(q)
    lam_poz = [(q["x"], q["z"], q["rid"]) for q in lamliwe]
    # --- instancje
    inst = []
    for rid, lista in M["instancje"].items():
        for i, e in enumerate(lista):
            x, z, kat, sk = e[0], e[1], e[2], e[3]
            y = e[4] if len(e) > 4 else 0.0
            if rid in SM.DEKORACJA and gestosc < 1 and (i * 0.618) % 1 > gestosc:
                continue
            if any(abs(x - lx) < 1.0 and abs(z - lz) < 1.0 and rid == lr for lx, lz, lr in lam_poz):
                continue  # rzecz do rozbicia: osobny model
            st = strefa_punktu(M, x, z)
            if rid in SM.LAWA and math.hypot(x - wx0, z - wz0) < M["wyspa"]["r_wew"] + 2:
                # rekwizyty z wyspy kaldery → wyspa gry (A)
                x, z, sk, y, st = WYG["x"] + (x - wx0) * sk_w, WYG["z"] + (z - wz0) * sk_w, sk * sk_w, 0.0, "lawa"
            elif st in SCENERIA and (rid in WYLACZONE_A or rid == "skrzynia_ukryta"):
                continue
            elif rid in WYLACZONE_A:
                continue
            if st != "lawa" and math.hypot(x - WYG["x"], z - WYG["z"]) < WYG["r_zew"] + 3:
                continue  # wyspa gry i fosa wolne
            if st in CHODZONE and y > 0.3 and any(w_obrysie(f, x, z, 0.5) for f in splaszczone):
                y = 0.0  # pagór spłaszczony
            strefa = st
            if st in SCENERIA:
                strefa = "sceneria"
            if rid in ("lilia", "trzcina"):
                strefa = "woda"
            slot = 0
            if rid in ("legowisko_krag", "legowisko_brama", "sztandar"):
                strefa = "legowisko"
                slot = min(range(len(legowiska)), key=lambda k: math.hypot(x - legowiska[k][0], z - legowiska[k][1])) + 1
            elif rid in ZNAKI:
                strefa = "znak"
            elif rid.startswith("latarnia_"):
                strefa = "latarnie"
            inst.append([rid, _r(x), _r(z), kat, _r(sk, 3), strefa, slot, _r(y), st])
    # głazy w przejściach do stref rzeźby (A)
    tablice = []
    for P in PRZEJSCIA_A:
        ux, uz = math.sin(math.radians(P["o"])), math.cos(math.radians(P["o"]))
        n = max(3, int(P["szer"] // 6))
        for k in range(n):
            f = (k + 0.5) / n - 0.5
            gx, gz = P["x"] + ux * 4 + (-uz) * f * P["szer"] * 1.05, P["z"] + uz * 4 + ux * f * P["szer"] * 1.05
            inst.append(["glaz_1" if k % 2 else "glaz_2", _r(gx), _r(gz), (k * 47) % 360, 1.25, "sceneria", 0, 0.0, P["strefa"]])
        tablice.append({"x": _r(P["x"] - ux * 3), "z": _r(P["z"] - uz * 3), "tekst": "COMING SOON", "pod": P["nazwa"]})
    # --- przeszkody z rekwizytów (koła) w strefach chodzonych
    for rid, x, z, kat, sk, strefa, slot, y, st in inst:
        if st not in CHODZONE and strefa not in ("legowisko", "znak", "lawa"):
            continue
        if rid in bez_kol or y > KROK:
            continue
        kola = SM.KOLA.get(rid) or [tuple(c) for c in kol_nowe.get(rid, [])]
        for (lx, lz, r) in kola:
            ox, oz = SM.obroc(lx * sk, lz * sk, kat)
            przeszkody.append({"k": "k", "typ": "lawa" if rid == "oltarz_kul" else ("legowisko" if strefa == "legowisko" else "skala"),
                               "x": _r(x + ox), "z": _r(z + oz), "r": _r(r * sk), "rid": rid})
    # przeszkody: wszystkie mają x, z, r (koło opisane) — stare miejsca w logice traktują je jak koła
    for p in przeszkody:
        if p["k"] == "p":
            p["r"] = _r(math.hypot(p["hx"], p["hz"]))
            p["x"], p["z"], p["hx"], p["hz"] = _r(p["x"]), _r(p["z"]), _r(p["hx"]), _r(p["hz"])
    # --- obszar gry: kształty stref chodzonych (maska 1 — łąka i kieszenie, 2 — las); pas bez kurczenia wzdłuż osi
    obszar = []
    for sid in CHODZONE:
        for k in Z[sid]["obszar"]:
            m = 2 if sid == "las" else 1
            if "kolo" in k:
                obszar.append({"k": "k", "x": k["kolo"][0], "z": k["kolo"][1], "r": k["kolo"][2], "maska": m, "s": sid})
            elif "pas" in k:
                cx, cz, sz, dl, o = k["pas"]
                obszar.append({"k": "pas", "x": cx, "z": cz, "o": o, "hx": sz / 2, "hz": dl / 2, "maska": m, "s": sid})
            else:
                x0, x1, z0, z1 = k["prostokat"]
                obszar.append({"k": "p", "x": (x0 + x1) / 2, "z": (z0 + z1) / 2, "o": 0.0, "hx": (x1 - x0) / 2, "hz": (z1 - z0) / 2, "maska": m, "s": sid})
    # --- bramy rozmiaru, kryjówki, sekrety
    bramy = []
    for b in M["bramy_rozmiaru"]:
        if b["id"] in BRAMY_A:
            bramy.append({"id": b["id"], "x": b["x"], "z": b["z"], "o": b["o"], "hx": b["szer"] / 2, "hz": b["dl"] / 2, "r_maks": b["r_maks"]})
    kryjowki = [{"id": k["id"], "x": k["x"], "z": k["z"], "r": k["r"], "r_maks": k["r_maks_smoka"]} for k in M["kryjowki"] if k["strefa"] in CHODZONE
                and math.hypot(k["x"] - WYG["x"], k["z"] - WYG["z"]) > WYG["r_zew"] + k["r"]]
    sekrety = [{"id": s["id"], "x": s["x"], "z": s["z"], "zloto": s["zloto"], "nazwa": s["nazwa"], "typ": s["typ"]}
               for s in M["sekrety"] if s["id"] in SEKRETY_A]
    # brody rzeki (kamienie brodu) — szybkie jak most
    brody = []
    for (x, z, *_r2) in M["instancje"].get("kamien_brodu", []):
        if not any(math.hypot(x - b["x"], z - b["z"]) < 10 for b in brody):
            grupa = [(a, c) for (a, c, *_q) in M["instancje"]["kamien_brodu"] if math.hypot(a - x, c - z) < 12]
            gx, gz = sum(a for a, _ in grupa) / len(grupa), sum(c for _, c in grupa) / len(grupa)
            if any(w_obrysie(w, gx, gz, 1.0) for w in woda) and strefa_punktu(M, gx, gz) == "laka":
                brody.append({"k": "k", "x": _r(gx), "z": _r(gz), "r": 6.5})
    # --- płaty ziemi (bez wyspy gry), teren do budowy (bryły; A: pagóry spłaszczone)
    platy = [p for p in M["platy_ziemi"] if not (math.hypot(p[0] - WYG["x"], p[1] - WYG["z"]) < WYG["r_zew"] + p[2] - 1 and p[2] < 40)]
    teren_out = []
    for t in teren_bud:
        s = t["strefa"]
        if math.hypot(t["p"][0] - WYG["x"], t["p"][2] - WYG["z"]) < WYG["r_zew"] + 2 and s in ("laka", "rzeka") and not t.get("woda") \
                and not t.get("ozdoba"):
            continue
        teren_out.append([{"blok": 0, "klin": 3, "walec": 2}[t["k"]], _r(t["p"][0]), _r(t["p"][1], 3), _r(t["p"][2]), _r(t["s"][0], 3), _r(t["s"][1], 3),
                          _r(t["s"][2], 3), _r(t["o"]), t["kolor"], t.get("material", "SmoothPlastic"),
                          0.25 if t.get("woda") or t.get("glebia") else 0.0, "sceneria" if s in SCENERIA else s,
                          (1 if t.get("przenikalny") else 0) + (2 if t.get("woda") or t.get("glebia") else 0) + (4 if t.get("lawa") else 0)])
    przen = [bryla_prost(t) for t in teren_bud if t.get("przenikalny") and t["strefa"] in CHODZONE]
    PG = M["punkty_gry"]
    return {"M": M, "instancje": inst, "teren": teren_out, "platy": platy, "przeszkody": przeszkody, "obszar": obszar, "woda": woda,
            "suche": suche + brody, "glebia": glebia, "podesty": podesty, "bramy": bramy, "kryjowki": kryjowki, "sekrety": sekrety,
            "lamliwe": lamliwe, "tablice": tablice, "splaszczone": splaszczone, "przenikalne": przen, "wyspa": WYG, "ranking": PG["ranking"], "owce": PG["owce_stada"],
            "rampage": PG["rampage_start"], "czesci_rek": M["czesci_rekwizytu"], "liczba": len(inst), "strefy": Z,
            "woda_x": M["parametry"]["woda_v_x"]}


# ------------------------------------------------------------------ geometria wspólna z logiką (sprawdziany w Pythonie)
def wolny_punkt(W, x, z, r, maska=1):
    """Czy smok o promieniu r stoi tu bez kolizji (obszar, przeszkody, bramy, głębia, wyspa) — do kul, owiec, wyspy, prób."""
    if not any((o["maska"] == maska or maska == 3) and _w_obszarze(o, x, z, r) for o in W["obszar"]):
        return False
    for p in W["przeszkody"]:
        if (p["k"] == "k" and math.hypot(x - p["x"], z - p["z"]) < p["r"] + r * 0.7) or (p["k"] == "p" and w_obrysie(p, x, z, r * 0.7)):
            return False
    for q in W["lamliwe"]:
        if any(math.hypot(x - c[0], z - c[1]) < c[2] + r * 0.7 for c in q["kola"]) or any(w_obrysie(f, x, z, r * 0.7) for f in q["prost"]):
            return False
    for b in W["bramy"]:
        if r > b["r_maks"] and w_obrysie(dict(b, k="p"), x, z, r * 0.7):
            return False
    for g in W["glebia"]:
        if w_obrysie(g["obrys"], x, z) and not any(w_obrysie(f, x, z) for f in g["wolne"]):
            return False
    WY = W["wyspa"]
    if WY["r_wew"] - r * 0.6 < math.hypot(x - WY["x"], z - WY["z"]) < WY["r_zew"] + r * 0.6:
        return False
    return True


def _w_obszarze(o, x, z, r):
    if o["k"] == "k":
        return math.hypot(x - o["x"], z - o["z"]) <= o["r"] - r * 0.6
    lx, lz = lok(x - o["x"], z - o["z"], o["o"])
    if o["k"] == "pas":
        return abs(lx) <= o["hx"] - r * 0.6 and abs(lz) <= o["hz"]
    return abs(lx) <= o["hx"] - r * 0.6 and abs(lz) <= o["hz"] - r * 0.6


def w_wodzie(W, x, z):
    if any(w_obrysie(f, x, z) for f in W["suche"]):
        return False
    return any(w_obrysie(f, x, z) for f in W["woda"])


def szukaj_wyspy(W, x0=-36.0, z0=-42.0):
    """Najbliższe miejsce łąki dla SKY NEST (r_zew + zapas wolne od rzeki, przeszkód, legowisk, placu, latarni i sekretów)."""
    WY = W["wyspa"]
    M = W["M"]
    zap = WY["r_zew"] + 4
    lat = [p for L in M["linie_latarni"] for p in L["punkty"]]
    best = None
    for rr in range(0, 120, 2):
        for k in range(max(1, rr * 2)):
            a = 2 * math.pi * k / max(1, rr * 2)
            x, z = x0 + math.sin(a) * rr, z0 + math.cos(a) * rr
            if math.hypot(x, z) > 150 - zap - 8 or math.hypot(x, z) < 17 + zap:
                continue
            if any(w_obrysie(f, x, z, zap) for f in W["woda"] + W["suche"]):
                continue
            if any(math.hypot(x - p["x"], z - p["z"]) < p["r"] + zap for p in W["przeszkody"] if p["k"] == "k" and p.get("typ") != "legowisko"):
                continue
            if any(w_obrysie(p, x, z, zap) for p in W["przeszkody"] if p["k"] == "p"):
                continue
            if any(math.hypot(x - lx, z - lz) < zap + 16 for lx, lz, _k in M["legowiska"]):
                continue
            if any(math.hypot(x - px, z - pz) < zap + 2 for px, pz in lat):
                continue
            if any(math.hypot(x - s["x"], z - s["z"]) < zap + 3 for s in W["sekrety"] + W["kryjowki"]):
                continue
            if any(w_obrysie(dict(b, k="p"), x, z, zap) for b in W["bramy"]) or any(w_obrysie(f, x, z, zap) for f in W["splaszczone"]):
                continue
            if any(math.hypot(x - px, z - pz) < zap + 8 for px, pz in W["owce"] + [W["ranking"], W["rampage"]]):
                continue
            best = (round(x, 1), round(z, 1))
            return best
    return best


def definicje(ids):
    """Bryły rekwizytów (stare i nowe rigi z jedną kością `Podstawa`) dla budowy w Studio."""
    return SM.definicje(ids)
