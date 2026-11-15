#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import sześciu modeli lasu do Roblox Studio po kolei — nakładka na roblox_import.py (jego logiki tu nie ma).

UWAGA: z opcją --tak-wgraj skrypt WGRYWA ZASOBY NA KONTO ROBLOX osoby zalogowanej w Studio (po jednym zasobie Model na
model, zasoby są trwałe i usuwa się je tylko w Creator Dashboard). Bez tej opcji skrypt tylko pokazuje plan: z niczym
się nie łączy (ani ze Studio, ani z siecią), niczego nie wysyła i niczego nie zapisuje.

    python -B swiat/postacie/roblox_import_lasu.py                              # plan dla sześciu modeli (domyślnie)
    python -B swiat/postacie/roblox_import_lasu.py --tylko zwiadowca            # plan jednego modelu
    python -B swiat/postacie/roblox_import_lasu.py --tylko zwiadowca --tak-wgraj   # wgraj, wstaw, sprawdź jeden model
    python -B swiat/postacie/roblox_import_lasu.py --sonda-skory                # po imporcie slime'a: wagi skóry w Studio

Kolejność (KOLEJNOSC) idzie od najbezpieczniejszego do najbardziej ryzykownego: Zwiadowca (R15, ta sama droga co
Rycerz 13.11.2026), Leśny Troll, Cierniowy Wilk, Muchomornik, Strażnik Gaju, Leśny Slime (siatka skórowana na dwóch
kościach). Powody i cały plan: swiat/postacie/IMPORT_LASU.md.

Bezpieczniki przed wgraniem (15.11.2026, po niezależnej kontroli):
- --tak-wgraj działa tylko razem z --tylko, więc wszystkich sześciu modeli nie da się wgrać jednym poleceniem;
- opcji nie da się skracać (np. --tak), bo skrót też by wgrywał;
- model wgrywa się dopiero wtedy, gdy wszystkie wcześniejsze z KOLEJNOSC mają w tabeli werdykt „zgodny” albo idą
  wcześniej w tym samym poleceniu (świadome odstępstwo: --mimo-kolejnosci);
- plik FBX musi mieć sha256 z PRZYJETE_SHA256 (pliki z 15.11.2026). Inny plik znaczy, że model przebudowano po
  przyjęciu: plan pokazuje BRAK, a wgranie odmawia, dopóki właściciel nie przyjmie nowej wersji i ktoś nie wpisze
  nowej wartości do PRZYJETE_SHA256;
- model, który jest w roblox_postac.ROZMIESZCZENIE, to BRAK, bo roblox_import postawiłby go tam, a ocena liczy
  kierunek z PROFILE.

Co robi z --tak-wgraj, model po modelu: wywołuje roblox_import.main(["--modul", id, "--tak-wgraj"], profil=…) — ta
sama ochrona przed podwójnym wgraniem (plik stanu wynik/_roblox/wgranie_<id>_fbx.json), wstawienie do
Workspace/TestPostaci, kontrola, naprawa skali i obrotu, dwa zrzuty — a potem ocenia wynik
(wynik/_roblox/import_<id>_fbx.json) liczbami z raport.json i z pliku GLB tego samego modelu. Po każdym modelu
zapisuje tabelę wynik/_roblox/import_lasu.json i import_lasu.txt. Pierwsza niezgodność albo przerwanie zatrzymuje
całość (kod 1): dalej idzie się dopiero po decyzji człowieka.
Wznowienie po przerwaniu: to samo polecenie. Model z tabeli z werdyktem „zgodny” jest pomijany. Model, który ma już
plik wyniku z tym samym numerem zasobu co plik stanu, jest oceniany z pliku — NIE jest wstawiany drugi raz (każde
wstawienie dokłada kopię w kontenerze). Resztę wznawia sam roblox_import.py z pliku stanu (bez drugiego wgrania).
Wyjątek: przerwanie PO wstawieniu, a PRZED zapisem pliku wyniku (np. błąd przeniesienia albo kontroli) zostawia
model w kontenerze bez pliku wyniku. Wznowienie wstawi wtedy ten sam zasób drugi raz, pod nazwą „… #2”. To nie jest
drugie wgranie, tylko druga kopia do ręcznego usunięcia.

Fakty o modelach skrypt czyta bez Blendera: raport.json (siatki, kości, zaczepy, klipy, wymiary), plik GLB tego
samego eksportu (drzewo kości, wagi skóry, które kości klipy przesuwają, czy jest kanał skali) i moduł postaci
(które bryły świecą — tylko odczyt danych, moduł niczego nie buduje).
Sprawdzian logiki planu i oceny bez Studio: python -B swiat/postacie/biblioteka/test_roblox_import_lasu.py
"""
import argparse
import importlib.util
import json
import math
import os
import re
import struct
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from swiat.postacie import roblox_import as ri  # noqa: E402  (sam import niczego nie łączy: Studio dopiero w ri.main)

FORMAT = "fbx"
# od najbezpieczniejszego do najbardziej ryzykownego (uzasadnienie w IMPORT_LASU.md, rozdz. 2)
KOLEJNOSC = ["zwiadowca", "lesny_troll", "cierniowy_wilk", "muchomornik", "straznik_gaju", "lesny_slime"]
POWODY = {
    "zwiadowca": "R15 jak Rycerz (sprawdzona droga), bez świecenia; łuk i sztylet są poza plikiem",
    "lesny_troll": "pierwszy własny szkielet: 18 kości, przesuwa tylko Biodra, bez świecenia",
    "cierniowy_wilk": "czworonóg, 22 kości, świecące oczy wewnątrz siatki głowy",
    "muchomornik": "29 kości, 13 siatek w całości świecących, zarodniki odlatują o 3,6 studa",
    "straznik_gaju": "największy: 37 kości, 11 168 trójkątów, 1,67 MB, 14,5 studa wzrostu, korzenie do 13,5 studa",
    "lesny_slime": "jedyna siatka skórowana na dwóch kościach; kości Cialo i Gora bez własnej siatki",
}
SPAWN = (21.4, 18.0)                                    # punkt wejścia w układzie miasta (krzywe_miasteczko/uklad.json)
WZROST_GRACZA = 5.71                                    # skala kamery zrzutów: wzrost / wzrost Rycerza, nie mniej niż 1
# Miejsce modelu (środek po imporcie) w układzie miasta: pas rynku między studnią (r = 9) a straganami 2, 3 i 5
# (z ≈ −24 … −37), wyliczony z uklad.json 15.11.2026. W Studio nie oglądany — pierwszy zrzut to sprawdza.
# Po kontroli 15.11.2026 przesunięte o 1–3 studa: obrys każdego modelu (szerokość × głębokość z raport.json, obrócony
# w stronę punktu wejścia) ma co najmniej 3 studa do obrysu straganów i studni z uklad.json i do sąsiednich modeli.
# Wcześniej Troll miał 1,3 studa do straganu 3, a Zwiadowca i Troll 0,4 studa między sobą.
# Przód: para nazw (przód, tył), której środki siatek i stawy kości leżą w danych wzdłuż +Z (przód modelu), oraz
# para (lewa, prawa) wzdłuż +X; liczby z raport.json i GLB pokazuje plan (wiersz „przód”).
PROFILE = {
    "zwiadowca": {"miejsce": (3.0, -18.0), "przod": None},          # None = punkty R15 z roblox_import.PRZOD_R15
    "lesny_troll": {"miejsce": (13.0, -14.0), "przod": ("Szczeka", "Tulow", "RamieL", "RamieP")},
    "cierniowy_wilk": {"miejsce": (-14.0, -15.0), "przod": ("Glowa", "Zad", "LapaPrzodL_Gora", "LapaPrzodP_Gora")},
    "muchomornik": {"miejsce": (-5.0, -22.0), "przod": ("Broda", "Glowa", "RamieL", "RamieP")},
    "straznik_gaju": {"miejsce": (27.0, -15.0), "przod": ("Krysztal", "Tulow", "RamieL", "RamieP")},
    "lesny_slime": {"miejsce": (42.0, -2.0), "przod": ("Przod", "Tyl", "BokL", "BokP")},
}
# Przesunięte 15.11.2026 po imporcie Muchomornika: w (−5; −17) stoi ławka (rekwizyty miasta nie są w uklad.json),
# a w (36; −8) latarnia. Nowe miejsca wybrał przegląd w Studio (tylko odczyt): w obrysie modelu z zapasem 2 studiów
# (Strażnik 1 stud) i w całej jego wysokości nie ma żadnej części, a bruk pod środkiem i czterema brzegami leży na
# wysokości −0,4 … 0,8; slime stoi co najmniej 8,6 studa od Strażnika.
ODSUNIECIE = 6.5                    # roblox_import stawia import 6,5 studa w lewo od „poz” (obok postaci z klocków)
TOL_WZROST = 0.02                   # ułamek: wzrost przed naprawą kontra raport.json (skala 1:1)
TOL_STOPY = 0.05                    # studa: spód siatek po naprawie kontra podłoże w miejscu modelu
TOL_POZIOM = (0.05, 0.25)           # szerokość i głębokość: ułamek albo studa (większe z dwóch; HumanoidRootPart R15)
TOL_PRZOD = 10.0                    # stopnie: przód po naprawie kontra kierunek na punkt wejścia
PODLOZE = (-0.4, 0.8)               # y spodu po naprawie (bruk rynku ma wierzch 0,2)
SKORA_UDZIAL = 0.9                  # sonda skóry: udział wierzchołków na dwóch kościach ≥ 0,9 × udziału z GLB
TABELA = "import_lasu"
# sha256 plików FBX przyjętych 15.11.2026 (te same liczby są w IMPORT_LASU.md, rozdz. 8). Inna wartość = model
# przebudowany po przyjęciu: wgranie odmawia, dopóki właściciel nie przyjmie nowej wersji i ktoś nie zmieni wpisu.
PRZYJETE_SHA256 = {
    "zwiadowca": "2e46f26f2af037aaecb16fadbc28e159a5780712dbd76eadf483754802a27624",
    "lesny_troll": "9a7d7c3d894e5da8742e24da501b530384f52cb8f08f86178297ff47652c67f1",
    "cierniowy_wilk": "b3b8845eb2d7c664cb9fb1ef11143fb273d04fa94cce935c480797f30b7dd72c",
    "muchomornik": "e8d7dd6c8d673b14ce9a52a00e781d1b05e62e0125f566055503ace69a80db18",
    "straznik_gaju": "f7dc8f428fb3b8dd57157f85a561fe563aef6f57431f26d1ed4d14c23a1947c2",
    "lesny_slime": "e57cb1df744dd1908e573f71145e684e76304596d08dfc5d2ce077305e72e1a4",
}


# ---------------------------------------------------------------- GLB bez Blendera (glTF 2.0, plik binarny)

_SKLADOWE = {5126: ("f", 4), 5125: ("I", 4), 5123: ("H", 2), 5121: ("B", 1)}
_ILE = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}


def wczytaj_glb(sciezka):
    """Plik .glb -> (słownik JSON, bajty bloku BIN)."""
    with open(sciezka, "rb") as f:
        b = f.read()
    magia, _wersja, dlugosc = struct.unpack_from("<4sII", b, 0)
    if magia != b"glTF":
        raise ValueError("%s to nie jest plik GLB" % sciezka)
    off, js, dane = 12, None, b""
    while off < min(dlugosc, len(b)):
        n, typ = struct.unpack_from("<I4s", b, off)
        blok = b[off + 8:off + 8 + n]
        if typ == b"JSON":
            js = json.loads(blok.decode("utf-8"))
        elif typ == b"BIN\x00":
            dane = blok
        off += 8 + n
    if js is None:
        raise ValueError("%s: brak bloku JSON" % sciezka)
    return js, dane


def akcesor(js, dane, i):
    """Wartości akcesora glTF jako lista krotek (z normalizacją liczb całkowitych)."""
    a = js["accessors"][i]
    bv = js["bufferViews"][a["bufferView"]]
    fmt, rozm = _SKLADOWE[a["componentType"]]
    n = _ILE[a["type"]]
    krok = bv.get("byteStride") or rozm * n
    baza = bv.get("byteOffset", 0) + a.get("byteOffset", 0)
    wynik = []
    for k in range(a["count"]):
        v = struct.unpack_from("<%d%s" % (n, fmt), dane, baza + k * krok)
        if a.get("normalized") and fmt != "f":
            v = tuple(x / float((1 << (8 * rozm)) - 1) for x in v)
        wynik.append(v)
    return wynik


def _qmul(a, b):
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)


def _qobroc(q, v):
    r = _qmul(_qmul(q, (v[0], v[1], v[2], 0.0)), (-q[0], -q[1], -q[2], q[3]))
    return r[:3]


def fakty_glb(sciezka):
    """Szkielet, skóra i klipy z GLB: {kosci, rodzice, glebokosc, stawy_swiat, skora, klipy}.

    glTF ma tę samą konwencję co dane biblioteki (Y w górę, przód +Z, lewa strona +X), więc położenia stawów
    porównuje się wprost z raport.json. Klip „przesuwa” kość, gdy jej przesunięcie odchodzi od spoczynku o > 1e-4 studa;
    „skala” — gdy kanał skali odchodzi od 1 o > 1e-4."""
    js, dane = wczytaj_glb(sciezka)
    wezly = js["nodes"]
    rodzic = {}
    for i, w in enumerate(wezly):
        for c in w.get("children", []):
            rodzic[c] = i
    stawy = js["skins"][0]["joints"] if js.get("skins") else []
    nazwy = {j: wezly[j]["name"] for j in stawy}
    rodzice, glebokosc = {}, {}
    for j in stawy:
        r = rodzic.get(j)
        rodzice[nazwy[j]] = nazwy[r] if r in nazwy else ""
        g, x = 0, j
        while rodzic.get(x) in nazwy:
            x = rodzic[x]
            g += 1
        glebokosc[nazwy[j]] = g
    pamiec = {}

    def swiat(i):
        if i in pamiec:
            return pamiec[i]
        w = wezly[i]
        t, q, s = w.get("translation", [0, 0, 0]), w.get("rotation", [0, 0, 0, 1]), w.get("scale", [1, 1, 1])
        if i in rodzic:
            pt, pq, ps = swiat(rodzic[i])
            t2 = _qobroc(pq, [t[k] * ps[k] for k in range(3)])
            wynik = ([pt[k] + t2[k] for k in range(3)], _qmul(pq, q), [ps[k] * s[k] for k in range(3)])
        else:
            wynik = (list(t), tuple(q), list(s))
        pamiec[i] = wynik
        return wynik

    stawy_swiat = {nazwy[j]: [round(x, 4) for x in swiat(j)[0]] for j in stawy}
    skora = []
    for w in wezly:
        if "mesh" not in w:
            continue
        for pr in js["meshes"][w["mesh"]]["primitives"]:
            at = pr.get("attributes", {})
            if "WEIGHTS_0" not in at or "JOINTS_0" not in at:
                continue
            wagi, kosci = akcesor(js, dane, at["WEIGHTS_0"]), akcesor(js, dane, at["JOINTS_0"])
            dwa = sum(1 for x in wagi if sorted(x, reverse=True)[1] > 0.01)
            if dwa:
                uzyte = sorted({nazwy[stawy[j]] for jj, ww in zip(kosci, wagi) for j, x in zip(jj, ww) if x > 0.01})
                skora.append({"siatka": w["name"], "wierzcholki": len(wagi), "dwa_wplywy": dwa, "kosci": uzyte})
    klipy = {}
    for an in js.get("animations", []):
        przesuwa, skala = {}, []
        for ch in an["channels"]:
            cel = ch["target"]
            if cel.get("node") is None:
                continue
            nazwa, sciezka_k = wezly[cel["node"]]["name"], cel["path"]
            if sciezka_k not in ("translation", "scale"):
                continue
            wartosci = akcesor(js, dane, an["samplers"][ch["sampler"]]["output"])
            if sciezka_k == "translation":
                spocz = wezly[cel["node"]].get("translation", [0, 0, 0])
                d = max((max(abs(a - b) for a, b in zip(x, spocz)) for x in wartosci), default=0.0)
                if d > 1e-4:
                    przesuwa[nazwa] = round(d, 3)
            elif max((max(abs(a - 1.0) for a in x) for x in wartosci), default=0.0) > 1e-4:
                skala.append(nazwa)
        probek = max(js["accessors"][s["input"]]["count"] for s in an["samplers"])
        sekundy = max(js["accessors"][s["input"]].get("max", [0])[0] for s in an["samplers"])
        klipy[an["name"]] = {"probek": probek, "sekundy": round(sekundy, 3), "przesuwa": przesuwa, "skala": skala}
    return {"kosci": [nazwy[j] for j in stawy], "rodzice": rodzice, "glebokosc": max(glebokosc.values() or [0]),
            "stawy_swiat": stawy_swiat, "skora": skora, "klipy": klipy}


# ---------------------------------------------------------------- oczekiwania z raport.json, GLB i modułu

def swiecenie_z_modulu(mid):
    """Kości, których bryły świecą (materiał „swiecacy” albo „poswiata”), z danych modułu postaci.

    -> {"cale": [kości w całości świecące], "mieszane": {kość: "świecące/wszystkie"}} albo None, gdy moduł się nie
    wczytał. Moduł jest tylko czytany (zbuduj() zwraca opis postaci w czystym Pythonie, bez Blendera)."""
    try:
        from swiat.postacie.biblioteka.postac import Postac
        spec = importlib.util.spec_from_file_location("lasu_" + mid, os.path.join(TU, mid + ".py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        w = mod.zbuduj()
        w = list(w) if isinstance(w, (list, tuple)) else [w]
        p = next(o for o in w if isinstance(o, Postac))
        per = {}
        for c in p.json()["czesci"]:
            t = per.setdefault(c["kosc"], [0, 0])
            t[0] += 1
            t[1] += 1 if c.get("m") in ("swiecacy", "poswiata") else 0
    except Exception as e:                                   # noqa: BLE001 — opis jest dodatkiem, nie warunkiem planu
        return {"blad": "%s: %s" % (type(e).__name__, e)}
    return {"cale": sorted(k for k, (n, s) in per.items() if n and s == n),
            "mieszane": {k: "%d/%d" % (s, n) for k, (n, s) in sorted(per.items()) if 0 < s < n}}


def _srodki(model):
    return {s["kosc"]: [(s["min"][k] + s["max"][k]) / 2.0 for k in range(3)]
            for s in model["siatki"] if s.get("kosc") and s.get("min") and s.get("max")}


def miejsce_dla_importu(cel, patrz=SPAWN):
    """Środek, w którym ma stanąć import -> „poz” dla roblox_import (który odsuwa import o ODSUNIECIE w lewo od poz,
    patrząc z poz na patrz). Wynik: (poz, kierunek przodu (fx, fz)) w układzie miasta."""
    # roblox_import liczy kierunek z poz (nie z celu), więc poz szukamy kolejnymi przybliżeniami:
    # poz = cel − ODSUNIECIE · lewo(kierunek z poz na patrz); przy odległości ≫ 6,5 studa zbiega w kilku krokach
    poz = cel
    for _ in range(50):
        fx, fz = patrz[0] - poz[0], patrz[1] - poz[1]
        d = math.hypot(fx, fz)
        fx, fz = fx / d, fz / d
        nowa = (cel[0] - fz * ODSUNIECIE, cel[1] + fx * ODSUNIECIE)          # lewo = (fz, −fx)
        if math.hypot(nowa[0] - poz[0], nowa[1] - poz[1]) < 1e-9:
            poz = nowa
            break
        poz = nowa
    fx, fz = patrz[0] - poz[0], patrz[1] - poz[1]
    d = math.hypot(fx, fz)
    return (round(poz[0], 4), round(poz[1], 4)), (fx / d, fz / d)


def warianty_nazwy(zaczep):
    """Nazwy, pod którymi zaczep może wyjść z importera: „GlowaAttachment”, znacznik „Glowa_Att”, samo „Glowa”."""
    rdzen = zaczep[:-len("Attachment")] if zaczep.endswith("Attachment") else zaczep
    return [zaczep, rdzen + "_Att", rdzen]


def oczekiwania(mid, wynik_dir=None):
    """Wszystko, co wiadomo o modelu przed importem -> słownik (bez kontaktu z czymkolwiek poza dyskiem)."""
    wynik_dir = wynik_dir or ri.WYNIK
    katalog = os.path.join(wynik_dir, mid)
    plik = os.path.join(katalog, "%s.%s" % (mid, FORMAT))
    glb = os.path.join(katalog, "%s.glb" % mid)
    e = {"modul": mid, "plik": plik, "braki": []}
    if not os.path.isfile(plik):
        e["braki"].append("brak pliku %s (eksporty są poza gitem: python -B swiat/postacie/przebuduj.py %s)"
                          % (os.path.relpath(plik, REPO).replace("\\", "/"), mid))
    else:
        e["rozmiar"] = os.path.getsize(plik)
        e["sha256"] = ri.sha256_pliku(plik)
        if e["rozmiar"] > ri.LIMIT_MB * 1e6:
            e["braki"].append("plik większy niż %d MB" % ri.LIMIT_MB)
        przyjety = PRZYJETE_SHA256.get(mid)
        e["sha_przyjety"] = przyjety == e["sha256"]
        if not e["sha_przyjety"]:
            e["braki"].append("sha256 pliku %s nie jest wersją przyjętą 15.11.2026 (%s) — model przebudowano? Stop i "
                              "pytanie do właściciela; po jego zgodzie nowa wartość do PRZYJETE_SHA256"
                              % (e["sha256"][:12], (przyjety or "brak wpisu")[:12]))
    from swiat.postacie.roblox_postac import ROZMIESZCZENIE        # czyste stałe (ten sam import robi roblox_import)
    if mid in ROZMIESZCZENIE:
        e["braki"].append("%s jest w roblox_postac.ROZMIESZCZENIE — roblox_import postawi go tam, a ocena liczy kierunek "
                          "z PROFILE; usuń jedno z dwóch" % mid)
    try:
        with open(os.path.join(katalog, "raport.json"), encoding="utf-8") as f:
            rap = json.load(f)
        m = next(x for x in rap["modele"] if x.get("rodzaj") == "postac")
    except (OSError, ValueError, StopIteration) as ex:
        e["braki"].append("brak raport.json z modelem postaci (%s)" % ex)
        return e
    poza = {"%s_Akc" % a["id"] for a in m.get("akcesoria", []) if not a.get("eksport", True)}
    siatki = [s["nazwa"] for s in m["siatki"] if s["nazwa"] not in poza]
    kosci_z_siatka = {s["kosc"] for s in m["siatki"] if s["nazwa"] in siatki and s.get("kosc")}
    # trójkąty siatek, które są w pliku (trojkaty_razem z raportu liczy też przedmioty spoza pliku: łuk i sztylet
    # Zwiadowcy, miecz Rycerza); znaczniki _Att dokładają po 12 trójkątów i są tylko w kontroli eksportu
    trojkaty = sum(s.get("trojkaty", 0) for s in m["siatki"] if s["nazwa"] in siatki)
    e.update(nazwa=m["nazwa"], typ=m["typ"], siatki=siatki, poza_plikiem=sorted(poza), kosci=list(m["kosci"]),
             kosci_bez_siatki=[k for k in m["kosci"] if k not in kosci_z_siatka], zaczepy=list(m["zaczepy"]),
             znaczniki_att=list(m.get("znaczniki_att", [])), wymiary=list(m["wymiary_ciala"]),
             trojkaty=trojkaty, trojkaty_razem=m["trojkaty_razem"],
             klipy_raportu=[[k["n"], k["dlugosc"], k["sekundy"], k["petla"]] for k in m["klipy"]],
             tekstura=m.get("tekstury", {}))
    e["kontrola_eksportu"] = [k for k in rap.get("kontrola", []) if k.startswith("%s.%s:" % (mid, FORMAT))]
    if os.path.isfile(glb):
        try:
            e["glb"] = fakty_glb(glb)
        except (OSError, ValueError, KeyError, struct.error) as ex:
            e["braki"].append("GLB nieczytelny: %s" % ex)
    else:
        e["braki"].append("brak %s (potrzebny do faktów o szkielecie i skórze)" % os.path.basename(glb))
    prof = PROFILE[mid]
    poz, f = miejsce_dla_importu(prof["miejsce"])
    e["profil"] = {"rozmieszczenie": {"poz": poz, "patrz": SPAWN},
                   "zrzut_skala": round(max(1.0, e["wymiary"][1] / WZROST_GRACZA), 3)}
    e["kierunek_celu"] = [round(f[0], 5), round(f[1], 5)]
    if prof["przod"]:
        p, t, lw, pr = prof["przod"]
        e["profil"]["przod"] = {"przod": [p + "_Geo", p], "tyl": [t + "_Geo", t], "lewa": [lw + "_Geo", lw],
                                "prawa": [pr + "_Geo", pr]}
        pary = [(p, t), (lw, pr)]
    else:
        pary = [("LeftFoot", "LeftLowerLeg"), ("LeftUpperArm", "RightUpperArm")]
    sr = _srodki(m)
    st = (e.get("glb") or {}).get("stawy_swiat", {})
    e["przod_dane"] = []
    for (a, b), os_ in zip(pary, (2, 0)):                      # przód wzdłuż +Z, lewa strona wzdłuż +X
        e["przod_dane"].append({"para": [a, b], "os": "Z" if os_ == 2 else "X",
                                "siatki": round(sr[a][os_] - sr[b][os_], 3) if a in sr and b in sr else None,
                                "kosci": round(st[a][os_] - st[b][os_], 3) if a in st and b in st else None})
    e["swiecenie"] = swiecenie_z_modulu(mid)
    return e


# ---------------------------------------------------------------- ocena wyniku roblox_import (bez Studio)

def _kat(a, b):
    """Kąt w stopniach między dwoma kierunkami w płaszczyźnie XZ."""
    d = math.degrees(math.atan2(a[0], a[1]) - math.atan2(b[0], b[1]))
    return abs((d + 180.0) % 360.0 - 180.0)


def _liczba(wzor, kroki):
    for k in kroki or []:
        m = re.search(wzor, k)
        if m:
            return [float(x) for x in m.groups()]
    return None


def ocen(e, wynik):
    """Wynik roblox_import (słownik z import_<id>_fbx.json) kontra oczekiwania -> (werdykt, lista sprawdzeń).

    Sprawdzenie: {n, oczekiwane, jest, wynik} z wynikiem „tak”, „nie” albo „obejrzyj” (człowiek patrzy na zrzut;
    nie blokuje). Werdykt „zgodny”, gdy żadne sprawdzenie nie ma „nie”."""
    s = []

    def dodaj(n, oczek, jest, ok):
        s.append({"n": n, "oczekiwane": oczek, "jest": jest, "wynik": ok if isinstance(ok, str) else ("tak" if ok else "nie")})

    wynik = wynik or {}
    przed = wynik.get("kontrola_przed") or {}
    po = wynik.get("kontrola_po") or przed
    kl = po.get("klasy") or {}
    if wynik.get("bledy"):
        dodaj("błędy kroków", "brak", "; ".join(wynik["bledy"])[:300], False)
    # siatki i kolor. Znaczniki zaczepów (sześciany <Nazwa>_Att) u Rycerza zamieniły się w Attachment; przy własnym
    # szkielecie mogą wyjść jako zwykłe MeshPart. Wtedy nie liczą się do siatek ciała ani do koloru, a brak zaczepów
    # pokaże osobny punkt niżej.
    znaczniki = [x["n"] for x in po.get("siatki", []) if x.get("n", "").endswith("_Att")]
    n_siatek = kl.get("MeshPart", 0) - len(znaczniki)
    dodaj("siatki MeshPart (bez znaczników _Att)", len(e["siatki"]), n_siatek, n_siatek == len(e["siatki"]))
    if znaczniki:
        dodaj("znaczniki _Att jako MeshPart (informacja)", "0 (u Rycerza były Attachment)",
              "%d: %s" % (len(znaczniki), ", ".join(znaczniki[:6])), "obejrzyj")
    bez = [x["n"] for x in po.get("siatki", []) if not x.get("tekstura") and not x.get("colormap")
           and not x.get("n", "").endswith("_Att")]
    dodaj("kolor (tekstura albo SurfaceAppearance)", "0 siatek bez koloru", "%d: %s" % (len(bez), ", ".join(bez[:6])), not bez)
    # skala 1:1 przed naprawą (naprawa i tak wyrównuje wzrost, więc liczy się wynik PRZED nią). Od 15.11.2026 wymiary
    # pochodzą z pomiaru samych siatek w układzie modelu (ri.pomiar): niewidoczny RootPart rigu z kości stoi środkiem
    # na wysokości stóp i zawyżał wzrost, a skrzynka w osiach świata obróconego modelu zawyżała głębokość. Stare wyniki
    # bez danych części (Rycerz z 13.11) ocenia się jak dawniej, ze skrzynki z KONTROLA.
    pm_przed = przed.get("pomiar") or ri.pomiar(przed)
    pm_po = po.get("pomiar") or ri.pomiar(po)
    wym = pm_przed["wymiary"] if pm_przed else przed.get("wymiary")
    if wym:
        wz = e["wymiary"][1]
        dodaj("wzrost przed naprawą (skala 1:1)", "%.2f ±%d%%" % (wz, TOL_WZROST * 100), round(wym[1], 3),
              abs(wym[1] - wz) <= TOL_WZROST * wz)
        ocz, jest = sorted([e["wymiary"][0], e["wymiary"][2]]), sorted([wym[0], wym[2]])
        ok = all(abs(a - b) <= max(TOL_POZIOM[0] * a, TOL_POZIOM[1]) for a, b in zip(ocz, jest))
        dodaj("szerokość i głębokość", "%.2f × %.2f" % tuple(ocz), "%.2f × %.2f" % tuple(jest), ok)
    else:
        dodaj("wzrost przed naprawą (skala 1:1)", "%.2f" % e["wymiary"][1], "brak pomiaru", False)
    # szkielet
    stawy = kl.get("Motor6D", 0) + kl.get("AnimationConstraint", 0)
    drzewo = {k["n"]: k for k in przed.get("kosci_drzewo") or po.get("kosci_drzewo") or []}
    nazwy_czesci = {x["n"] for x in po.get("siatki", [])}
    if e["typ"] == "r15":
        dodaj("Humanoid", 1, kl.get("Humanoid", 0), kl.get("Humanoid", 0) == 1)
        dodaj("stawy R15 (Motor6D + AnimationConstraint)", 15, stawy, stawy == 15)
        rodzaj = "R15"
    elif drzewo:
        rodzaj = "kości (Bone)"
        wymagane = [k for k in e["kosci"] if k != "Root"]
        brak = [k for k in wymagane if k not in drzewo]
        dodaj("kości Bone (bez Root)", len(wymagane), "%d, brak: %s" % (len(wymagane) - len(brak), ", ".join(brak[:8]) or "-"),
              not brak)
        rodz = (e.get("glb") or {}).get("rodzice", {})
        zle = [k for k in wymagane if k in drzewo and rodz.get(k) not in ("", "Root", None)
               and drzewo[k].get("r") != rodz.get(k)]
        dodaj("rodzice kości jak w GLB", "0 różnic", "%d: %s" % (len(zle), ", ".join(zle[:6])), not zle)
        g = max((k.get("g", 0) for k in drzewo.values()), default=0)
        gl = (e.get("glb") or {}).get("glebokosc")
        if gl is not None:
            # gl liczy przodków-kości od Root. Importer może Root zostawić (gl), zamienić na część, jak u Rycerza, gdzie
            # z Root powstał HumanoidRootPart (gl − 1), albo dołożyć własną kość nad nim (gl + 1). Wszystkie trzy są
            # w porządku, bo rodziców sprawdza osobny punkt.
            dodaj("głębokość drzewa kości", "%d … %d" % (gl - 1, gl + 1), g, gl - 1 <= g <= gl + 1)
    elif stawy:
        rodzaj = "sztywne części ze stawami"
        bez_siatki = [k for k in e["kosci_bez_siatki"] if k != "Root"]
        # znaczniki _Att wyjęte jako MeshPart mogą mieć własne stawy, więc dochodzą do tolerancji
        dodaj("stawy części (bez kości Bone)", "%d ±%d" % (len(e["siatki"]), 1 + len(znaczniki)), stawy,
              abs(stawy - len(e["siatki"])) <= 1 + len(znaczniki))
        dodaj("kości bez siatki zachowane", "brak takich kości" if not bez_siatki else "nie da się (giną: %s)" % ", ".join(bez_siatki),
              "-", not bez_siatki)
    else:
        rodzaj = "brak"
        dodaj("szkielet", "kości Bone albo stawy", "ani kości, ani stawów", False)
    # zaczepy
    nazwy_zaczepow = {z.split("@")[0] for z in po.get("zaczepy", [])}
    brak_z, warianty = [], set()
    for z in e["zaczepy"]:
        traf = [v for v in warianty_nazwy(z) if v in nazwy_zaczepow]
        if traf:
            warianty.add("nazwa" if traf[0] == z else ("_Att" if traf[0].endswith("_Att") else "rdzeń"))
        elif z != "RootAttachment":                         # u Rycerza znacznik Root_Att nie przeszedł (13.11.2026)
            brak_z.append(z)
    dodaj("zaczepy (RootAttachment może zniknąć)", len([z for z in e["zaczepy"] if z != "RootAttachment"]),
          "brak: %s; nazwy: %s" % (", ".join(brak_z) or "-", ", ".join(sorted(warianty)) or "-"), not brak_z)
    # kierunek, lustro, podłoże, obrót
    # Uwaga: naprawa obraca model o różnicę między zmierzonym a zadanym przodem, więc po naprawie ten punkt przechodzi
    # zawsze, gdy pomiar się udał. Sprawdza tylko, że pomiar i obrót zadziałały; o samym imporcie mówią „lustro”
    # i kąt obrotu niżej (ok. ±180° = FBX patrzył tyłem). Czy zmierzony przód jest prawdziwym przodem, widać na zrzucie.
    if po.get("przod"):
        k = _kat(po["przod"], e["kierunek_celu"])
        dodaj("przód po naprawie (pomiar i obrót zadziałały)", "≤ %.0f° od kierunku na punkt wejścia" % TOL_PRZOD, "%.1f°" % k,
              k <= TOL_PRZOD)
    else:
        dodaj("przód po naprawie", "zmierzony", "nie dało się zmierzyć — obejrzyj zrzut", "obejrzyj")
    lewa = po.get("lewa_po_lewej")
    dodaj("lewa strona po lewej (brak lustra)", True, lewa, lewa is True if lewa is not None else "obejrzyj")
    kroki = (wynik.get("naprawa") or {}).get("kroki") or []
    pos = _liczba(r"postawiono w \(([-\d.]+); ([-\d.]+); ([-\d.]+)\)", kroki)
    if pos:
        dodaj("podłoże pod modelem (y)", "%.1f … %.1f" % PODLOZE, pos[1], PODLOZE[0] <= pos[1] <= PODLOZE[1])
        if pm_po:
            # spód siatek po naprawie ma leżeć na podłożu (a nie spód niewidocznego RootPart)
            dodaj("stopy na podłożu (spód siatek po naprawie)", "y %.2f ±%.2f" % (pos[1], TOL_STOPY), round(pm_po["min_y"], 3),
                  abs(pm_po["min_y"] - pos[1]) <= TOL_STOPY)
    else:
        dodaj("podłoże pod modelem (y)", "naprawa ustawiła model", "brak kroku naprawy", False)
    kol = (wynik.get("naprawa") or {}).get("kolizje")
    if kol is not None:
        # od 15.11.2026: Muchomornik stanął na oparciu ławki (podłoże y 3,8). Części miasta w skrzynce modelu pokazują,
        # że miejsce jest zajęte; skrzynka jest w osiach świata, więc to sygnał do obejrzenia, nie werdykt.
        dodaj("części miasta w obrysie modelu", "brak", "%d: %s" % (len(kol), "; ".join(kol[:4])) if kol else "brak",
              "obejrzyj" if kol else "tak")
    if wynik.get("przywrocenie_skali"):
        ps = wynik["przywrocenie_skali"]
        dodaj("skala przywrócona do 1:1 przed kontrolą (informacja)", "1", "%.4f → %.4f" % (ps.get("przed", 0), ps.get("po", 0)),
              abs(float(ps.get("po") or 0) - 1) <= 1e-3)
    obrot = _liczba(r"obrót wokół pionu o ([-\d.]+)°", kroki)
    dodaj("obrót przy naprawie (informacja)", "dowolny; ok. ±180° = FBX patrzył tyłem", "%.1f°" % obrot[0] if obrot else "0°", "tak")
    skala = _liczba(r"skala ×([\d.]+)", kroki)
    if skala:
        dodaj("skala przy naprawie", "bez zmian", "×%.4f" % skala[0], False)
    # świecenie: siatki kości w całości świecących (Neon dokłada się później, decyzją)
    sw = e.get("swiecenie") or {}
    if sw.get("cale") and rodzaj != "R15":
        znalezione = [k for k in sw["cale"] if k in nazwy_czesci or (k + "_Geo") in nazwy_czesci]
        dodaj("siatki do świecenia odnalezione", len(sw["cale"]), len(znalezione), len(znalezione) == len(sw["cale"]))
    # skóra i zrzuty: ogląda człowiek (sonda skóry: --sonda-skory)
    if (e.get("glb") or {}).get("skora"):
        dodaj("skóra na dwóch kościach", "sonda --sonda-skory i zrzut pozy (IMPORT_LASU.md, krok S8)", "-", "obejrzyj")
    dodaj("zrzuty", "2 pliki do obejrzenia", "-", "obejrzyj")
    werdykt = "zgodny" if all(x["wynik"] != "nie" for x in s) else "niezgodny"
    return werdykt, s, rodzaj


# ---------------------------------------------------------------- wypisywanie

def _mb(n):
    return ("%.2f MB" % (n / 1e6)).replace(".", ",")


def stan_wgrania(mid):
    """(plik stanu, stan albo None, akcja, komunikat) — decyzja z roblox_import.decyzja_wgrania, bez Studio."""
    p = ri.sciezka_stanu(mid, FORMAT)
    st = ri.wczytaj_stan(p)
    akcja, kom = ri.decyzja_wgrania(st)
    return p, st, akcja, kom


def wiersz_planu(nr, e):
    """Linie planu jednego modelu (lista napisów)."""
    mid = e["modul"]
    L = ["[%d/%d] %s — %s (%s): %s" % (nr, len(KOLEJNOSC), mid, e.get("nazwa", "?"),
                                       "R15" if e.get("typ") == "r15" else "własny szkielet", POWODY[mid])]
    rel = os.path.relpath(e["plik"], REPO).replace("\\", "/")
    if "rozmiar" in e:
        L.append("  plik:        %s, %s (%d B; limit %d MB), sha256 %s (%s)"
                 % (rel, _mb(e["rozmiar"]), e["rozmiar"], ri.LIMIT_MB, e["sha256"],
                    "wersja przyjęta 15.11" if e.get("sha_przyjety") else "INNY NIŻ PRZYJĘTY"))
    else:
        L.append("  plik:        %s — BRAK" % rel)
    p, st, akcja, kom = stan_wgrania(mid)
    prel = os.path.relpath(p, REPO).replace("\\", "/")
    if st:
        L.append("  stan:        %s: etap „%s”, zasób %s, moderacja %s (%s) → z --tak-wgraj: %s"
                 % (prel, st.get("etap"), st.get("asset") or "-", st.get("moderacja") or "-", st.get("czas") or "?", akcja))
        if st.get("sha256") and e.get("sha256") and st["sha256"] != e["sha256"]:
            L.append("  UWAGA:       plik zmienił się od tamtego wgrania — wznowienie wstawi STARĄ wersję")
    else:
        L.append("  stan:        brak pliku %s → z --tak-wgraj: pierwsze wgranie (jeden trwały zasób Model)" % prel)
    if kom:
        L.append("               %s" % kom)
    wyn = os.path.join(ri.STAN_DIR, "import_%s_%s.json" % (mid, FORMAT))
    L.append("  wynik:       %s" % ("jest %s (ocena z pliku, bez ponownego wstawiania)" % os.path.basename(wyn)
                                    if os.path.isfile(wyn) else "jeszcze nie ma import_%s_%s.json" % (mid, FORMAT)))
    if "siatki" not in e:
        for b in e["braki"]:
            L.append("  BRAK:        %s" % b)
        return L
    g = e.get("glb") or {}
    L.append("  szkielet:    %d kości, głębokość drzewa %s, korzeń Root; kości bez siatki: %s"
             % (len(e["kosci"]), g.get("glebokosc", "?"), ", ".join(e["kosci_bez_siatki"]) or "-"))
    L.append("  siatki:      %d w pliku (MeshPart po imporcie)%s; trójkąty w pliku %d%s; tekstura-paleta %s px, %s kolorów"
             % (len(e["siatki"]), "; poza plikiem: %s" % ", ".join(e["poza_plikiem"]) if e["poza_plikiem"] else "",
                e["trojkaty"], " (z przedmiotami %d)" % e["trojkaty_razem"] if e["trojkaty_razem"] != e["trojkaty"] else "",
                e["tekstura"].get("rozmiar_px", "?"), e["tekstura"].get("kolory_materialy", "?")))
    if e.get("kontrola_eksportu"):
        L.append("  eksport:     %s" % e["kontrola_eksportu"][0].split(":", 1)[1].strip())
    kl = g.get("klipy") or {}
    opis = []
    for n, dl, sek, petla in e["klipy_raportu"]:
        opis.append("%s %d kl. %.2f s%s" % (n, dl + 1, sek, " pętla" if petla else ""))
    L.append("  klipy (%d):   %s" % (len(opis), ", ".join(opis)))
    ruch = {}
    for n, k in kl.items():
        for kosc, d in k.get("przesuwa", {}).items():
            ruch[kosc] = max(ruch.get(kosc, 0), d)
    top = sorted(ruch.items(), key=lambda x: -x[1])
    L.append("  przesunięcia: %d kości; największe: %s; kanał skali: %s"
             % (len(ruch), ", ".join("%s %.2f" % x for x in top[:5]) or "-",
                ", ".join(sorted({s for k in kl.values() for s in k.get("skala", [])})) or "brak"))
    if g.get("skora"):
        for sk in g["skora"]:
            L.append("  skóra:       %s: %d z %d wierzchołków na dwóch kościach (%s), udział %.3f"
                     % (sk["siatka"], sk["dwa_wplywy"], sk["wierzcholki"], ", ".join(sk["kosci"]),
                        sk["dwa_wplywy"] / float(sk["wierzcholki"])))
    else:
        L.append("  skóra:       brak (każda siatka na jednej kości, waga 1)")
    sw = e.get("swiecenie") or {}
    if sw.get("blad"):
        L.append("  świecenie:   nieznane (moduł się nie wczytał: %s)" % sw["blad"])
    else:
        L.append("  świecenie:   całe siatki: %s; w części siatki: %s"
                 % (", ".join(sw.get("cale", [])) or "-", ", ".join("%s %s" % kv for kv in sw.get("mieszane", {}).items()) or "-"))
    pd = []
    for x in e["przod_dane"]:
        pd.append("%s→%s d%s %s (siatki) / %s (kości)" % (x["para"][0], x["para"][1], x["os"],
                                                          "?" if x["siatki"] is None else "%.2f" % x["siatki"],
                                                          "?" if x["kosci"] is None else "%.2f" % x["kosci"]))
    L.append("  przód:       %s" % "; ".join(pd))
    prof = e["profil"]
    L.append("  miejsce:     środek (%.1f; %.1f) w układzie miasta, patrzy na punkt wejścia (%.1f; %.1f); kamera zrzutów ×%.2f"
             % (PROFILE[mid]["miejsce"][0], PROFILE[mid]["miejsce"][1], SPAWN[0], SPAWN[1], prof["zrzut_skala"]))
    zacz = [z for z in e["zaczepy"] if z != "RootAttachment"]
    if e["typ"] == "r15":
        szk = "Humanoid 1, stawy 15"
    else:
        szk = ("kości Bone %d (bez Root) z rodzicami jak w GLB, głębokość %s albo o 1 więcej — albo sztywne części: stawy %d ±1"
               % (len(e["kosci"]) - 1, g.get("glebokosc", "?"), len(e["siatki"])))
        if [k for k in e["kosci_bez_siatki"] if k != "Root"]:
            szk += " (tylko kości: %s nie mają siatki)" % ", ".join(k for k in e["kosci_bez_siatki"] if k != "Root")
    L.append("  oczekiwane:  MeshPart %d; %s; wzrost %.2f ±%d%% przed naprawą; zaczepy %d (%s); przód ≤ %.0f°; lewa po lewej; "
             "podłoże y %.1f…%.1f" % (len(e["siatki"]), szk, e["wymiary"][1], TOL_WZROST * 100, len(zacz),
                                      ", ".join(zacz), TOL_PRZOD, PODLOZE[0], PODLOZE[1]))
    for b in e["braki"]:
        L.append("  BRAK:        %s" % b)
    for x in e["przod_dane"]:
        if x["siatki"] is not None and x["siatki"] <= 0.02:
            L.append("  UWAGA:       para %s→%s nie wyznacza kierunku na siatkach (d%s = %.2f)" % (x["para"][0], x["para"][1], x["os"], x["siatki"]))
    return L


def wczytaj_tabele():
    p = os.path.join(ri.STAN_DIR, TABELA + ".json")
    try:
        with open(p, encoding="utf-8") as f:
            t = json.load(f)
        return t if isinstance(t, dict) else {}
    except (OSError, ValueError):
        return {}


def zapisz_tabele(tabela):
    """Tabela wyników do wynik/_roblox/import_lasu.json i .txt (bez numeru konta)."""
    ri.zapisz_stan(os.path.join(ri.STAN_DIR, TABELA + ".json"), tabela)
    linie = ["Import modeli lasu do Roblox Studio (roblox_import_lasu.py), stan na %s." % ri.teraz(), ""]
    for mid in KOLEJNOSC:
        w = tabela.get(mid)
        if not w:
            linie.append("%-15s nie zaczęty" % mid)
            continue
        linie.append("%-15s %s — zasób %s, model „%s”, szkielet: %s (%s)" % (
            mid, w.get("werdykt", "?").upper(), w.get("asset") or "-", w.get("model") or "-", w.get("rodzaj") or "-", w.get("czas", "?")))
        if w.get("powod"):
            linie.append("    powód: %s" % w["powod"])
        for x in w.get("sprawdzenia", []):
            linie.append("    [%-7s] %s: oczekiwane %s, jest %s" % (x["wynik"], x["n"], x["oczekiwane"], x["jest"]))
    tmp = os.path.join(ri.STAN_DIR, TABELA + ".txt")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(linie) + "\n")


# ---------------------------------------------------------------- sonda skóry (Studio, tylko odczyt)

SONDA_SKORY = r'''
-- roblox_import_lasu: SONDA SKORY
local HS = game:GetService("HttpService")
local AS = game:GetService("AssetService")
if game.PlaceId ~= __PLACE__ then
	return HS:JSONEncode({ blad = "to nie jest miejsce gry (PlaceId " .. tostring(game.PlaceId) .. ")" })
end
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ blad = "brak kontenera __KONTENER__ z atrybutem Wygenerowane" })
end
local model = kont:FindFirstChild(__MODEL__)
if not model then
	return HS:JSONEncode({ blad = "brak modelu w kontenerze" })
end
local SIATKA = __SIATKA__
local w = { siatka = "", kosci = {}, wierzcholki = 0, dwa = 0, nazwy = {}, bledy = {} }
local mp = nil
for _, d in model:GetDescendants() do
	if d:IsA("MeshPart") and (d.Name == SIATKA or d.Name == SIATKA .. "_Geo") then
		mp = d
	elseif d:IsA("Bone") then
		table.insert(w.kosci, d.Name)
	end
end
if not mp then
	w.blad = "brak MeshPart " .. SIATKA
	return HS:JSONEncode(w)
end
w.siatka = mp.Name
local ok, em = pcall(function()
	return AS:CreateEditableMeshAsync(Content.fromUri(mp.MeshId))
end)
if not ok or not em then
	table.insert(w.bledy, "CreateEditableMeshAsync: " .. tostring(em))
	return HS:JSONEncode(w)
end
local okB, nazwy = pcall(function()
	local t = {}
	for _, b in em:GetBones() do
		t[b] = em:GetBoneName(b)
	end
	return t
end)
if not okB then
	table.insert(w.bledy, "GetBones/GetBoneName: " .. tostring(nazwy))
	nazwy = {}
end
local okV, bladV = pcall(function()
	local uzyte = {}
	for _, v in em:GetVertices() do
		w.wierzcholki += 1
		local kosci = em:GetVertexBones(v)
		local wagi = em:GetVertexBoneWeights(v)
		local ile = 0
		for i, x in wagi do
			if x > 0.01 then
				ile += 1
				uzyte[nazwy[kosci[i]] or tostring(kosci[i])] = true
			end
		end
		if ile >= 2 then
			w.dwa += 1
		end
	end
	for n in uzyte do
		table.insert(w.nazwy, n)
	end
end)
if not okV then
	table.insert(w.bledy, "GetVertexBones/GetVertexBoneWeights: " .. tostring(bladV))
end
pcall(function()
	em:Destroy()
end)
return HS:JSONEncode(w)
'''


def kod_sondy(model, siatka):
    return (SONDA_SKORY.replace("__PLACE__", str(ri.PLACE_ID)).replace("__KONTENER__", ri.KONTENER)
            .replace("__SIATKA__", json.dumps(siatka, ensure_ascii=False))
            .replace("__MODEL__", json.dumps(model, ensure_ascii=False)))


def ocen_sonde(e, w):
    """Wynik sondy skóry -> (werdykt „tak” / „nie” / „nieznany” / „błąd”, opis).

    „błąd” znaczy, że sonda nie doszła do siatki (inne miejsce, brak kontenera, modelu albo siatki Dol): o skórze
    nic jeszcze nie wiadomo, trzeba usunąć przyczynę i uruchomić sondę jeszcze raz."""
    sk = ((e.get("glb") or {}).get("skora") or [None])[0]
    if not sk:
        return "nieznany", "model nie ma skóry na dwóch kościach"
    if w.get("blad"):
        return "błąd", w["blad"]
    if not w.get("wierzcholki"):
        return "nieznany", "API siatki nie odpowiedziało: %s" % "; ".join(w.get("bledy") or ["?"])
    udzial = w["dwa"] / float(w["wierzcholki"])
    wzor = sk["dwa_wplywy"] / float(sk["wierzcholki"])
    kosci_ok = set(sk["kosci"]) <= set(w.get("nazwy") or [])
    ok = udzial >= SKORA_UDZIAL * wzor and kosci_ok
    return ("tak" if ok else "nie"), ("udział wierzchołków na dwóch kościach %.3f (GLB %.3f, próg %.3f); kości wag: %s (oczekiwane %s)"
                                      % (udzial, wzor, SKORA_UDZIAL * wzor, ", ".join(sorted(w.get("nazwy") or [])) or "-",
                                         ", ".join(sk["kosci"])))


# ---------------------------------------------------------------- przebieg

def sprawdz_ponownie(wybrane):
    """Nowa ocena modeli, które już stoją w kontenerze, bez drugiego wgrania i bez drugiego wstawienia -> kod wyjścia.

    Dla każdego modelu: numer zasobu z pliku stanu wgrania, nazwa modelu z pliku wyniku importu, potem roblox_import
    --sprawdz <nazwa> --napraw (skala 1:1, kontrola, naprawa, zrzuty; plik wyniku zachowuje numer zasobu), nowy werdykt
    w tabeli import_lasu. Powód (15.11.2026): stara kontrola liczyła RootPart do wzrostu i zmniejszyła Trolla ×0,909."""
    tabela = wczytaj_tabele()
    kod = 0
    for mid in wybrane:
        e = oczekiwania(mid)
        _p, st, _akcja, _kom = stan_wgrania(mid)
        asset = str((st or {}).get("asset") or "")
        wyn_p = os.path.join(ri.STAN_DIR, "import_%s_%s.json" % (mid, FORMAT))
        try:
            with open(wyn_p, encoding="utf-8") as f:
                poprzedni = json.load(f)
        except (OSError, ValueError):
            poprzedni = {}
        nazwa = (poprzedni.get("model") or {}).get("nazwa")
        if not asset or not nazwa or str(poprzedni.get("asset")) != asset:
            sys.exit("STOP (%s): brak wstawionego modelu do ponownej kontroli (zasób %s, model %s w %s). Nic nie zmieniono."
                     % (mid, asset or "-", nazwa or "-", os.path.basename(wyn_p)))
        print("ponownie:    %s — zasób %s, model „%s” (bez wgrywania i wstawiania)" % (mid, asset, nazwa))
        try:
            wynik = ri.main(["--modul", mid, "--format", FORMAT, "--sprawdz", nazwa, "--napraw"], profil=e["profil"])
        except SystemExit as ex:
            sys.exit("STOP na %s: %s" % (mid, ex.code))
        werdykt, spr, rodzaj = ocen(e, wynik)
        tabela[mid] = {"werdykt": werdykt, "asset": str(wynik.get("asset") or asset), "model": nazwa, "rodzaj": rodzaj,
                       "sprawdzenia": spr, "czas": ri.teraz(), "sha256": e.get("sha256"), "ponowna_kontrola": True}
        zapisz_tabele(tabela)
        for x in spr:
            print("  [%-7s] %s: oczekiwane %s, jest %s" % (x["wynik"], x["n"], x["oczekiwane"], x["jest"]))
        print("WERDYKT %s: %s (szkielet: %s)" % (mid, werdykt.upper(), rodzaj))
        if werdykt != "zgodny":
            kod = 1
    return kod


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    # allow_abbrev=False: skrót w rodzaju --tak albo --s nie może po cichu znaczyć --tak-wgraj albo --sonda-skory
    ap = argparse.ArgumentParser(description="Import sześciu modeli lasu do Roblox Studio (plan albo wgranie po kolei)",
                                 allow_abbrev=False)
    ap.add_argument("--tylko", default="", help="id modułów po przecinku (kolejność i tak z KOLEJNOSC); z --tak-wgraj wymagane")
    ap.add_argument("--tak-wgraj", action="store_true",
                    help="NAPRAWDĘ wgraj pliki na konto Roblox zalogowane w Studio (po jednym trwałym zasobie na model)")
    ap.add_argument("--mimo-kolejnosci", action="store_true",
                    help="z --tak-wgraj: wgraj, choć wcześniejszy model z KOLEJNOSC nie ma werdyktu „zgodny” (decyzja właściciela)")
    ap.add_argument("--sonda-skory", action="store_true",
                    help="po imporcie Leśnego Slime'a: odczytaj w Studio wagi skóry siatki Dol (nic nie wgrywa i nie zmienia)")
    ap.add_argument("--sprawdz-ponownie", action="store_true",
                    help="model już wstawiony (z --tylko): skala 1:1, kontrola i naprawa jeszcze raz, nowy werdykt — "
                         "NIC nie wgrywa i nie wstawia (roblox_import.py --sprawdz --napraw)")
    a = ap.parse_args(argv)
    if a.sprawdz_ponownie and (a.tak_wgraj or a.sonda_skory or not a.tylko.strip()):
        ap.error("--sprawdz-ponownie działa osobno (bez --tak-wgraj i --sonda-skory) i wymaga --tylko <id>")
    if a.tak_wgraj and a.sonda_skory:
        ap.error("--sonda-skory uruchamia się osobno, bez --tak-wgraj")
    if a.mimo_kolejnosci and not a.tak_wgraj:
        ap.error("--mimo-kolejnosci działa tylko z --tak-wgraj")
    wybrane = [x.strip() for x in a.tylko.split(",") if x.strip()]
    for x in wybrane:
        if x not in KOLEJNOSC:
            ap.error("nieznany model %r (są: %s)" % (x, ", ".join(KOLEJNOSC)))
    if a.tak_wgraj and not wybrane:
        ap.error("--tak-wgraj wymaga --tylko <id>[,<id>…] (wgrywa się świadomie, model po modelu; IMPORT_LASU.md, rozdz. 5)")
    wybrane = [m for m in KOLEJNOSC if not wybrane or m in wybrane]

    if a.sonda_skory:
        return sonda_skory()
    if a.sprawdz_ponownie:
        return sprawdz_ponownie(wybrane)

    if a.tak_wgraj:
        # kolejność: każdy wcześniejszy model musi być już „zgodny” albo iść wcześniej w tym samym poleceniu
        tabela = wczytaj_tabele()
        for mid in wybrane:
            wczesniej = KOLEJNOSC[:KOLEJNOSC.index(mid)]
            braki_k = [m for m in wczesniej if m not in wybrane and (tabela.get(m) or {}).get("werdykt") != "zgodny"]
            if braki_k and not a.mimo_kolejnosci:
                sys.exit("STOP przed wgraniem: %s idzie w kolejności po %s, a te nie mają jeszcze werdyktu „zgodny” w %s. "
                         "Nic nie wysłano. Najpierw je, albo świadomie --mimo-kolejnosci (decyzja właściciela)."
                         % (mid, ", ".join(braki_k), os.path.join(ri.STAN_DIR, TABELA + ".json")))

    oczek = {mid: oczekiwania(mid) for mid in wybrane}
    if not a.tak_wgraj:
        print("PLAN importu modeli lasu (%s) — z niczym się nie łączę, niczego nie wysyłam i niczego nie zapisuję." % ri.teraz())
        braki = 0
        for mid in wybrane:
            print()
            print("\n".join(wiersz_planu(KOLEJNOSC.index(mid) + 1, oczek[mid])))
            braki += len(oczek[mid]["braki"])
        print()
        print("PODSUMOWANIE PLANU: modeli %d, pliki razem %s, braków %d. Nic nie wysłano. Żeby naprawdę wgrać: --tylko <id> "
              "--tak-wgraj, zaczynając od --tylko zwiadowca." % (len(wybrane), _mb(sum(e.get("rozmiar", 0) for e in oczek.values())),
                                                                 braki))
        return 0 if braki == 0 else 1

    # --- naprawdę: model po modelu, stop na pierwszej niezgodności
    tabela = wczytaj_tabele()
    print("WGRYWANIE modeli lasu: %s. Każdy nowy model to jeden TRWAŁY zasób Model na koncie zalogowanym w Studio."
          % ", ".join(wybrane))
    for mid in wybrane:
        e = oczek[mid]
        print()
        print("=" * 100)
        print("\n".join(wiersz_planu(KOLEJNOSC.index(mid) + 1, e)))
        if e["braki"]:
            tabela[mid] = {"werdykt": "przerwany", "powod": "; ".join(e["braki"]), "czas": ri.teraz()}
            zapisz_tabele(tabela)
            sys.exit("STOP (%s): %s" % (mid, "; ".join(e["braki"])))
        _p, st, _akcja, _kom = stan_wgrania(mid)
        wyn_p = os.path.join(ri.STAN_DIR, "import_%s_%s.json" % (mid, FORMAT))
        stary = tabela.get(mid) or {}
        asset = str((st or {}).get("asset") or "")
        if stary.get("werdykt") == "zgodny" and asset and str(stary.get("asset")) == asset and os.path.isfile(wyn_p):
            print("zrobione:    %s ma werdykt „zgodny” dla zasobu %s — pomijam." % (mid, asset))
            continue
        wynik = None
        if asset and os.path.isfile(wyn_p):
            try:
                with open(wyn_p, encoding="utf-8") as f:
                    poprzedni = json.load(f)
            except (OSError, ValueError):
                poprzedni = None
            if poprzedni and str(poprzedni.get("asset")) == asset and poprzedni.get("model"):
                print("wznowienie:  zasób %s jest już wstawiony („%s”) — oceniam z %s, NIE wstawiam drugi raz."
                      % (asset, poprzedni["model"].get("nazwa"), os.path.basename(wyn_p)))
                wynik = poprzedni
        if wynik is None:
            t0 = time.time()
            try:
                wynik = ri.main(["--modul", mid, "--format", FORMAT, "--tak-wgraj"], profil=e["profil"])
            except SystemExit as ex:
                powod = ex.code if isinstance(ex.code, str) else "kod wyjścia %s" % ex.code
                st2 = ri.wczytaj_stan(ri.sciezka_stanu(mid, FORMAT)) or {}
                tabela[mid] = {"werdykt": "przerwany", "powod": powod, "etap": st2.get("etap"), "asset": st2.get("asset") or "",
                               "czas": ri.teraz()}
                zapisz_tabele(tabela)
                print(powod)
                etap = st2.get("etap") or "?"
                if etap == "zasob" and ri.klasa_moderacji(st2.get("moderacja")) == "odrzucony":
                    dalej = "Moderacja ODRZUCIŁA zasób %s: nie wgrywaj tego pliku drugi raz." % (st2.get("asset") or "?")
                elif etap in ("operacja", "zasob"):
                    dalej = ("Zasób albo operacja są zapisane w pliku stanu: to samo polecenie później wznowi czekanie albo "
                             "wstawienie bez drugiego wgrania.")
                elif etap in ri.ETAPY_BEZ_ZASOBU:
                    dalej = "Zasób nie powstał (etap „%s”); po usunięciu przyczyny to samo polecenie wgra plik." % etap
                else:
                    dalej = ("NIE WIADOMO, czy zasób powstał: to samo polecenie znowu się zatrzyma. Sprawdź Creator "
                             "Dashboard (IMPORT_LASU.md, rozdz. 6) i nic nie wgrywaj na ślepo.")
                sys.exit("STOP na %s (etap „%s”). %s Zanim pójdziesz dalej, zapytaj właściciela (IMPORT_LASU.md, rozdz. 6)."
                         % (mid, etap, dalej))
            print("czas:        %.0f s" % (time.time() - t0))
        werdykt, spr, rodzaj = ocen(e, wynik)
        tabela[mid] = {"werdykt": werdykt, "asset": str(wynik.get("asset") or asset), "model": (wynik.get("model") or {}).get("nazwa"),
                       "rodzaj": rodzaj, "sprawdzenia": spr, "czas": ri.teraz(), "sha256": e.get("sha256")}
        zapisz_tabele(tabela)
        for x in spr:
            print("  [%-7s] %s: oczekiwane %s, jest %s" % (x["wynik"], x["n"], x["oczekiwane"], x["jest"]))
        print("WERDYKT %s: %s (szkielet: %s)" % (mid, werdykt.upper(), rodzaj))
        if werdykt != "zgodny":
            sys.exit("STOP: %s niezgodny — dalsze modele czekają na decyzję właściciela (IMPORT_LASU.md, rozdz. 6)." % mid)
    print()
    print("PODSUMOWANIE: %s" % ", ".join("%s %s" % (m, (tabela.get(m) or {}).get("werdykt", "nie zaczęty")) for m in KOLEJNOSC))
    print("Tabela: %s (.txt obok). Zrzuty do obejrzenia: wynik/_roblox/import_<id>_fbx_0.png i _1.png."
          % os.path.join(ri.STAN_DIR, TABELA + ".json"))
    return 0


def sonda_skory(mid="lesny_slime"):
    """Wagi skóry siatki Dol zaimportowanego slime'a (Studio, tylko odczyt).

    Kod wyjścia: 0 = TAK (skóra zachowana), 1 = NIE (skóra przepadła), 2 = BŁĄD (sonda nie doszła do siatki),
    3 = NIEZNANY (API siatki nie odpowiedziało; decyduje próba pozy)."""
    e = oczekiwania(mid)
    wyn_p = os.path.join(ri.STAN_DIR, "import_%s_%s.json" % (mid, FORMAT))
    try:
        with open(wyn_p, encoding="utf-8") as f:
            model = json.load(f)["model"]["nazwa"]
    except (OSError, ValueError, KeyError, TypeError):
        sys.exit("Nie ma wyniku importu %s — najpierw --tylko %s --tak-wgraj." % (os.path.basename(wyn_p), mid))
    sk = ((e.get("glb") or {}).get("skora") or [None])[0]
    if not sk:
        sys.exit("GLB modelu %s nie ma skóry na dwóch kościach — nie ma czego sprawdzać." % mid)
    sys.path.insert(0, os.path.join(REPO, "tools"))
    from studio_mcp import StudioMCP, StudioError, first_studio_id
    try:
        with StudioMCP() as s:
            sid = first_studio_id(s)
            if not sid:
                sys.exit("Roblox Studio nie jest podłączone.")
            r = s.call("execute_luau", {"code": kod_sondy(model, sk["siatka"].replace("_Geo", "")), "datamodel_type": "Edit",
                                        "studio_id": sid}, timeout=240)
            if r["is_error"]:
                raise StudioError(r["text"])
            w = json.loads(r["text"])
    except StudioError as ex:
        sys.exit("BŁĄD Studio: %s" % ex)
    werdykt, opis = ocen_sonde(e, w)
    print("Sonda skóry %s, siatka %s: %s — %s" % (model, w.get("siatka") or sk["siatka"], werdykt.upper(), opis))
    if w.get("bledy"):
        print("Błędy API: %s" % "; ".join(w["bledy"]))
    print("Kości w modelu: %s" % (", ".join(w.get("kosci") or []) or "brak"))
    return {"tak": 0, "nie": 1, "nieznany": 3}.get(werdykt, 2)


if __name__ == "__main__":
    sys.exit(main())
