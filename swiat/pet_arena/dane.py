#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane gry Pet Arena (D-118, etap 1) → zrodla/DanePetArena.luau (wygenerowany), wzorce petów i części sceny do budowy.

    python -B swiat/pet_arena/dane.py              # zapisuje DanePetArena.luau, gdy się zmienił, i wypisuje tabelę
    python -B swiat/pet_arena/dane.py --sprawdz    # kod 1, gdy plik jest nieaktualny (nic nie zapisuje)

Źródła (tylko odczyt): ustawienia.json; modele petów z klocków swiat/postacie/<id>.py (roblox_klocki.rig — te same
dane modeli, do których sięgał BONK); dźwięki: swiat/dzwiek_gra/identyfikatory.json i
assets/audio/arkusz/sfx_arkusz_a.json. Układ: środek areny (0, 0, 0), wierzch areny y = 0. Żadnych liczb w kodzie Luau
poza tymi z ustawień.
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
ZRODLA = os.path.join(TU, "zrodla")
PLIK_DANYCH = "DanePetArena.luau"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
SLOWA_LUAU = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil",
              "not", "or", "repeat", "return", "then", "true", "until", "while", "continue"}
TYPY_UMIEJETNOSCI = {"rykoszet", "szarza", "jezyk", "ogluszenie", "skorupa", "skok", "podpalenie", "zamrozenie", "fala"}


class BladDanych(Exception):
    pass


def czytaj_json(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return json.load(f)


def sciezka_repo(wzgledna):
    return os.path.join(REPO, *wzgledna.split("/"))


def ustawienia():
    return czytaj_json(os.path.join(TU, "ustawienia.json"))


def _r(v, n=2):
    x = round(float(v), n)
    return 0 if x == 0 else x


def bez_opisu(d):
    return {k: v for k, v in d.items() if k != "opis"}


# ------------------------------------------------------------------------------------------------ modele petów
def _postacie():
    if REPO not in sys.path:
        sys.path.insert(0, REPO)
    from swiat.postacie.roblox_postac import postacie_z_modulu
    from swiat.postacie.biblioteka import roblox_klocki as RK
    return postacie_z_modulu, RK


_RIGI = {}


def model_surowy(model_id):
    """Rig z klocków swiat/postacie/<id>.py (układ rigu: ziemia y = 0, przód −Z) → bryły w skali 1 i wymiary."""
    if model_id not in _RIGI:
        postacie_z_modulu, RK = _postacie()
        sciezka = os.path.join(REPO, "swiat", "postacie", model_id + ".py")
        if not os.path.isfile(sciezka):
            raise BladDanych("brak modelu swiat/postacie/%s.py" % model_id)
        p = next((x for x in postacie_z_modulu(sciezka) if x.id == model_id), None)
        if p is None:
            raise BladDanych("brak modelu %s w swiat/postacie/%s.py" % (model_id, model_id))
        d = RK.rig(p, None)
        bryly = []
        for c in d["czesci"]:
            mat = d["materialy"][int(c[13])]
            bryly.append([int(c[1]), c[3], c[4], c[5], c[6], c[7], c[8], c[9], c[10], c[11], c[12].upper(), mat[0], mat[1],
                          c[15] or ""])
        wys = max(b[2] + b[8] / 2 for b in bryly)
        dol = min(b[2] - b[8] / 2 for b in bryly)
        szer = max(max(abs(b[1]) + b[7] / 2, abs(b[3]) + b[9] / 2) for b in bryly)
        _RIGI[model_id] = {"nazwa": p.nazwa, "bryly": bryly, "wys": wys, "dol": dol, "szer": szer}
    return _RIGI[model_id]


def nazwa_wzorca(pid):
    return "Pet_" + pid


def wzorzec_peta(U, P):
    """Wzorzec peta w skali do wysokości klasy wagi; stopy na y = 0 (model z ujemnym dołem podniesiony)."""
    S = model_surowy(P["id"])
    K = U["klasy_wagi"][P["waga"]]
    k = K["wysokosc"] / (S["wys"] - min(0.0, S["dol"]))
    podnies = -min(0.0, S["dol"]) * k
    bryly = []
    for b in S["bryly"]:
        bryly.append([b[0], _r(b[1] * k, 4), _r(b[2] * k + podnies, 4), _r(b[3] * k, 4), _r(b[4], 5), _r(b[5], 5), _r(b[6], 5),
                      _r(b[7] * k, 4), _r(b[8] * k, 4), _r(b[9] * k, 4), b[10], b[11], _r(b[12], 3), b[13]])
    return {"klucz": nazwa_wzorca(P["id"]), "nazwa": P["nazwa"], "bryly": bryly, "skala": _r(k, 4),
            "wysokosc": _r(K["wysokosc"]), "szer": _r(S["szer"] * k)}


def model_potwora(klucz):
    """Model potwora z swiat/test_walki2/dane/<klucz>.json (te same dane, z których brał BONK) — tylko odczyt."""
    s = sciezka_repo("swiat/test_walki2/dane/%s.json" % klucz)
    if not os.path.isfile(s):
        raise BladDanych("brak modelu potwora %s" % klucz)
    return czytaj_json(s)


def wzorzec_bossa(klucz, wysokosc):
    d = model_potwora(klucz)
    k = wysokosc / d["wymiary"]["wysokosc"]
    bryly = []
    for c in d["czesci"]:
        mat = d["materialy"][int(c[13])]
        bryly.append([int(c[1]), _r(c[3] * k, 4), _r(c[4] * k - d["wymiary"]["spod"] * k, 4), _r(c[5] * k, 4), _r(c[6], 5), _r(c[7], 5),
                      _r(c[8], 5), _r(c[9] * k, 4), _r(c[10] * k, 4), _r(c[11] * k, 4), c[12], mat[0], _r(mat[1], 3), c[15] or ""])
    return {"klucz": "Boss_" + klucz, "nazwa": d["nazwa"], "bryly": bryly, "wysokosc": wysokosc}


def wzorzec_jajka(model_id, wysokosc):
    S = model_surowy(model_id)
    k = wysokosc / S["wys"]
    bryly = [[b[0], _r(b[1] * k, 4), _r(b[2] * k, 4), _r(b[3] * k, 4), _r(b[4], 5), _r(b[5], 5), _r(b[6], 5), _r(b[7] * k, 4),
              _r(b[8] * k, 4), _r(b[9] * k, 4), b[10], b[11], _r(b[12], 3), b[13]] for b in S["bryly"]]
    return {"klucz": "Jajko_" + model_id, "nazwa": S["nazwa"], "bryly": bryly, "wysokosc": wysokosc}


WYSOKOSC_JAJKA = 4.5


def wzorce(U):
    w = {nazwa_wzorca(P["id"]): wzorzec_peta(U, P) for P in U["pety"]}
    for J in U["jajka"]:
        x = wzorzec_jajka(J["model"], WYSOKOSC_JAJKA)
        w[x["klucz"]] = x
    for B in U["boss"]["modele"]:
        x = wzorzec_bossa(B["model"], U["boss"]["wysokosc"])
        w[x["klucz"]] = x
    return w


def pety(U, W=None):
    """Liczby petów z klasy wagi i stopnia (jedyne źródło: ustawienia.json)."""
    W = W or wzorce(U)
    KW = U["klasy_wagi"]
    ns = KW["na_stopien"]
    pr = KW["promien"]
    lista = []
    for nr, P in enumerate(U["pety"], 1):
        if P["waga"] not in ("lekki", "sredni", "ciezki"):
            raise BladDanych("%s: nieznana waga %s" % (P["id"], P["waga"]))
        if not 1 <= P["stopien"] <= len(U["rzadkosci"]):
            raise BladDanych("%s: stopień poza rzadkościami" % P["id"])
        A = P["umiejetnosc"]
        if A["typ"] not in TYPY_UMIEJETNOSCI:
            raise BladDanych("%s: nieznana umiejętność %s" % (P["id"], A["typ"]))
        K = KW[P["waga"]]
        s = P["stopien"] - 1
        w = W[nazwa_wzorca(P["id"])]
        lista.append({
            "nr": nr, "id": P["id"], "nazwa": P["nazwa"], "stopien": P["stopien"], "klasa": P["waga"], "waga": K["waga"],
            "zycie": _r(K["zycie"] * (1 + ns["zycie"] * s), 1), "obrazenia": _r(K["obrazenia"] * (1 + ns["obrazenia"] * s), 2),
            "odrzut": _r(K["odrzut"] * (1 + ns["odrzut"] * s), 2), "predkosc": K["predkosc"], "przerwa": K["przerwa_s"],
            "promien": _r(min(pr[1], max(pr[0], w["szer"] * 0.6))), "wysokosc": w["wysokosc"],
            "wzorzec": nazwa_wzorca(P["id"]), "czesci": len(w["bryly"]), "umiejetnosc": A,
        })
    return lista


# ------------------------------------------------------------------------------------------------ scena
def _kol(a):
    return math.radians(a)


def scena(U):
    """Części sceny: [kształt (0 blok, 1 kula, 2 walec), grupa, x, y, z, rx, ry, rz (radiany, fromOrientation),
    sx, sy, sz, kolor, materiał, przezroczystość, kolizja (0/1), nazwa]. Walec: oś X (obrót rz = 90° stawia go)."""
    S = U["scena"]
    R = S["arena_r"]
    n = S["segmenty"]
    c = []

    def dodaj(ks, grupa, poz, obr, roz, kolor, mat="SmoothPlastic", przez=0.0, koliz=1, nazwa="Klocek"):
        c.append([ks, grupa, _r(poz[0], 3), _r(poz[1], 3), _r(poz[2], 3), _r(obr[0], 5), _r(obr[1], 5), _r(obr[2], 5),
                  _r(roz[0], 3), _r(roz[1], 3), _r(roz[2], 3), kolor, mat, przez, koliz, nazwa])

    def walec(grupa, r, y_gora, grubosc, kolor, mat="SmoothPlastic", przez=0.0, koliz=1, nazwa="Walec"):
        dodaj(2, grupa, (0, y_gora - grubosc / 2, 0), (0, 0, math.pi / 2), (grubosc, 2 * r, 2 * r), kolor, mat, przez, koliz, nazwa)

    def pierscien(grupa, r0, r1, y0, y1, kolory, mat="SmoothPlastic", koliz=1, nazwa="Segment", ile=None, przez=0.0):
        m = ile or n
        rs = (r0 + r1) / 2
        szer = 2 * math.pi * r1 / m + 0.15
        for i in range(m):
            a = 2 * math.pi * i / m
            x, z = math.sin(a) * rs, math.cos(a) * rs
            dodaj(0, grupa, (x, (y0 + y1) / 2, z), (0, a, 0), (szer, y1 - y0, r1 - r0), kolory[i % len(kolory)], mat, przez,
                  koliz, nazwa)

    st = U["strefy"]
    # arena: platforma, pierścienie stref (coraz wyżej o 0,03 — bez migotania), środek, pasy krawędzi
    walec("Arena", R, 0, S["arena_grubosc"], "8C7A5E", "Slate", nazwa="Platforma")
    walec("Arena", st[2]["r"] - 0.9, 0.03, 0.2, st[2]["kolor"], "SmoothPlastic", nazwa="Pierscien1")
    walec("Arena", st[1]["r"] + 0.35, 0.06, 0.2, "FFF6E0", "SmoothPlastic", nazwa="ObwodkaPierscien2")
    walec("Arena", st[1]["r"], 0.09, 0.2, st[1]["kolor"], "SmoothPlastic", nazwa="Pierscien2")
    walec("Arena", st[0]["r"] + 0.4, 0.12, 0.2, "FFF6E0", "Neon", nazwa="ObwodkaSrodka")
    walec("Arena", st[0]["r"], 0.15, 0.2, st[0]["kolor"], "SmoothPlastic", nazwa="Srodek")
    pierscien("Arena", R - 0.9, R, -0.2, 0.06, ["FF4D4D", "FFF6E0"], nazwa="PasKrawedzi", ile=S["krawedz_pasow"])
    pierscien("Arena", R - 0.6, R + 0.15, -S["arena_grubosc"], -0.25, ["6E5E48", "5E503C"], "Slate", nazwa="BokAreny", ile=24)
    # fosa: dno, woda, gejzery
    walec("Fosa", S["fosa_r"] + 0.5, S["dno_y"], 1, "2B3A4A", "Slate", nazwa="Dno")
    walec("Fosa", S["fosa_r"] + 0.2, S["woda_y"], 0.6, "3FA9F5", "SmoothPlastic", przez=0.25, koliz=0, nazwa="Woda")
    for i in range(S["gejzery"]):
        a = 2 * math.pi * (i + 0.5) / S["gejzery"]
        x, z = math.sin(a) * S["gejzer_r"], math.cos(a) * S["gejzer_r"]
        dodaj(2, "Fosa", (x, S["woda_y"] + 0.1, z), (0, 0, math.pi / 2), (1.2, 3.4, 3.4), "6B6B70", "Slate", nazwa="Gejzer%d" % (i + 1))
        dodaj(2, "Fosa", (x, S["woda_y"] + 0.75, z), (0, 0, math.pi / 2), (0.2, 2.0, 2.0), "BFF2FF", "Neon", koliz=0,
              nazwa="Wylot%d" % (i + 1))
    # ściana dołu (dwa pasy kamieni), obrzeże, poręcz, niewidzialna ściana
    r0, r1 = S["fosa_r"], S["obrzeze_r"][0]
    pierscien("Sciana", r0, r1, S["dno_y"], S["woda_y"] + 2, ["5C5F66", "50535A", "676A70"], "Slate", nazwa="ScianaDol")
    pierscien("Sciana", r0, r1, S["woda_y"] + 2, S["obrzeze_y"] - 1.2, ["7A7D84", "6E7178", "858890"], "Slate", nazwa="ScianaGora")
    pierscien("Sciana", r0 - 0.3, r1, S["obrzeze_y"] - 1.2, S["obrzeze_y"], ["FFC83D", "FF8A3D"], nazwa="PasObrzeza")
    pierscien("Obrzeze", r1, S["obrzeze_r"][1], S["obrzeze_y"] - 2, S["obrzeze_y"], ["7FB35A", "73A851"], "Grass", nazwa="Trawa")
    for i in range(0, n, 2):
        a = 2 * math.pi * i / n
        rr = r1 + 0.6
        dodaj(0, "Obrzeze", (math.sin(a) * rr, S["obrzeze_y"] + 1.1, math.cos(a) * rr), (0, a, 0), (0.5, 2.2, 0.5), "5E3A1A", "Wood",
              nazwa="Slupek")
    pierscien("Obrzeze", r1 + 0.35, r1 + 0.85, S["obrzeze_y"] + 2.0, S["obrzeze_y"] + 2.45, ["9A6234"], "Wood", nazwa="Porecz")
    pierscien("Obrzeze", r1 - 0.2, r1 + 0.6, S["obrzeze_y"], S["obrzeze_y"] + 12, ["FFFFFF"], przez=1.0, nazwa="Bariera", ile=24)
    pierscien("Obrzeze", S["trybuna"][-1][1], S["trybuna"][-1][1] + 1, S["obrzeze_y"], S["obrzeze_y"] + 14, ["FFFFFF"], przez=1.0,
              nazwa="BarieraZewn", ile=24)
    for nr, (a0, a1, y) in enumerate(S["trybuna"]):
        pierscien("Trybuna", a0, a1, S["obrzeze_y"] - 2, y, ["D98B4A", "E8A660"] if nr == 0 else ["B8653A", "C97548"], "Wood",
                  nazwa="Stopien%d" % (nr + 1))
    # sloty graczy: płytki w kolorach slotów
    for i in range(S["sloty"]):
        a = _kol(360.0 * i / S["sloty"])
        x, z = math.sin(a) * S["slot_r"], math.cos(a) * S["slot_r"]
        dodaj(2, "Sloty", (x, S["obrzeze_y"] + 0.05, z), (0, 0, math.pi / 2), (0.2, 3.6, 3.6), U["gracz"]["kolory_slotow"][i],
              "SmoothPlastic", nazwa="Slot%d" % (i + 1))
    # drzewa z klocków dookoła
    for i in range(S["drzewa"]):
        a = 2 * math.pi * (i + 0.3) / S["drzewa"]
        rr = S["drzewa_r"][0] + (S["drzewa_r"][1] - S["drzewa_r"][0]) * ((i * 7) % 5) / 4
        x, z = math.sin(a) * rr, math.cos(a) * rr
        h = 10 + (i * 3) % 6
        dodaj(0, "Drzewa", (x, S["obrzeze_y"] + h / 2 - 1, z), (0, a, 0), (2.2, h, 2.2), "6B4426", "Wood", nazwa="Pien")
        dodaj(0, "Drzewa", (x, S["obrzeze_y"] + h + 1.5, z), (0, a + 0.4, 0), (9, 6, 9), ["4E9A3A", "5DAA45", "3F8A32"][i % 3], "Grass",
              nazwa="Korona")
        dodaj(0, "Drzewa", (x, S["obrzeze_y"] + h + 5, z), (0, a, 0), (5.5, 3.5, 5.5), ["6DBA52", "4E9A3A", "5DAA45"][i % 3], "Grass",
              nazwa="Czubek")
    # ziemia za trybuną
    pierscien("Teren", S["trybuna"][-1][1], 110, S["obrzeze_y"] - 4, S["obrzeze_y"] - 2, ["6FA34E", "68A048"], "Grass", nazwa="Laka", ile=36)
    # stanowisko jajek (cokoły; jajka z wzorców stawia zbuduj.py) i maty treningowe — po jednej obok każdego miejsca
    for k, (x, z) in enumerate(stanowisko_jajek(U)["cokoly"]):
        dodaj(2, "Jajka", (x, S["obrzeze_y"] + 0.6, z), (0, 0, math.pi / 2), (1.2, 5.2, 5.2), "8C8A84", "Slate", nazwa="Cokol")
        dodaj(2, "Jajka", (x, S["obrzeze_y"] + 1.25, z), (0, 0, math.pi / 2), (0.15, 5.5, 5.5), U["jajka"][k]["kolor"], "Neon", koliz=0,
              nazwa="Obrecz")
    for s in sloty(U):
        m = s["mata"]
        dodaj(0, "Maty", (m[0], S["obrzeze_y"] + 0.12, m[2]), (0, s["kat"], 0), (5, 0.24, 5), "3DB36B", "Fabric", nazwa="Mata%d" % s["nr"])
        dodaj(0, "Maty", (m[0], S["obrzeze_y"] + 0.26, m[2]), (0, s["kat"], 0), (4, 0.06, 4), "62D18A", "Fabric", koliz=0, nazwa="MataSrodek")
    return c


def stanowisko_jajek(U):
    """Stanowisko jajek na obrzeżu (kąt jajka_kat_st): trzy cokoły w rzędzie i tablica szans za nimi."""
    S = U["scena"]
    a = _kol(S["jajka_kat_st"])
    cokoly = []
    for k in range(len(U["jajka"])):
        da = (k - 1) * 0.15
        cokoly.append((_r(math.sin(a + da) * S["jajka_r"]), _r(math.cos(a + da) * S["jajka_r"])))
    r = S["jajka_r"] + 4.5
    return {"cokoly": cokoly, "tablica": [_r(math.sin(a) * r), S["obrzeze_y"] + 5, _r(math.cos(a) * r)], "patrz": [0, S["obrzeze_y"] + 5, 0]}


def makiety_napisy(U):
    """Napisy w świecie (etap 2: tablica szans przy stanowisku jajek)."""
    st = stanowisko_jajek(U)
    linie = []
    for J in U["jajka"]:
        szanse = "  ".join("%s %g%%" % (R["nazwa"][0], s * 100) for R, s in zip(U["rzadkosci"], J["szanse"]) if s > 0)
        linie.append("%s  %d G   %s" % (J["nazwa"], J["cena"], szanse))
    return [{"tekst": "EGGS\n" + "\n".join(linie), "poz": st["tablica"], "patrz": st["patrz"], "szer": 16, "wys": 6}]


def tablice(U):
    T = U["tablice"]
    w = []
    for i, (tytul, kat) in enumerate(zip(T["tytuly"], T["katy_st"])):
        a = _kol(kat)
        w.append({"nr": i + 1, "tytul": tytul, "poz": [_r(math.sin(a) * T["r"]), T["y"], _r(math.cos(a) * T["r"])], "patrz": [0, T["y"], 0],
                  "szer": T["szer"], "wys": T["wys"], "wierszy": T["wierszy"]})
    return w

def etykiety_stref(U):
    """Napisy na podłodze areny: „x5” w środku, „x2” i „x1” w pierścieniach (po 4, na skos)."""
    st = U["strefy"]
    w = [{"tekst": "x%d" % st[0]["mnoznik"], "poz": [0, 0.27, 0], "r": 0, "wielkosc": 5}]
    for i, s in enumerate(st[1:], 1):
        rr = (st[i - 1]["r"] + s["r"]) / 2
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2 + (0 if i == 1 else math.pi / 4)
            w.append({"tekst": "x%d" % s["mnoznik"], "poz": [_r(math.sin(a) * rr), 0.22, _r(math.cos(a) * rr)], "r": _r(a, 4),
                      "wielkosc": 4})
    return w


def sloty(U):
    """Sloty graczy: miejsce stania (na obrzeżu, przy poręczy), kąt kamery (o slot_przesuniecie_st obok, by awatar
    był w lewym dolnym rogu kadru) i kolor."""
    S = U["scena"]
    w = []
    for i in range(S["sloty"]):
        a = _kol(360.0 * i / S["sloty"])
        ak = a + _kol(S["slot_przesuniecie_st"])
        am = a + _kol(S["mata_kat_st"])
        w.append({"nr": i + 1, "poz": [_r(math.sin(a) * S["slot_r"]), S["obrzeze_y"], _r(math.cos(a) * S["slot_r"])],
                  "kat": _r(a, 5), "katKamery": _r(ak, 5), "kolor": U["gracz"]["kolory_slotow"][i],
                  "mata": [_r(math.sin(am) * S["mata_r"]), S["obrzeze_y"], _r(math.cos(am) * S["mata_r"])]})
    return w


def kamera_dla(U, kat):
    """Pozycja i cel kamery dla kąta (radiany): kamera na zewnątrz w kierunku (sin, cos)."""
    K = U["kamera"]
    e = _kol(K["nachylenie_st"])
    dx, dz = math.sin(kat), math.cos(kat)
    poz = [dx * (K["cel_z"] + K["odleglosc"] * math.cos(e)), K["odleglosc"] * math.sin(e), dz * (K["cel_z"] + K["odleglosc"] * math.cos(e))]
    cel = [dx * K["cel_z"], 0, dz * K["cel_z"]]
    return poz, cel


def rzut_punktu(kam, cel, p, fov, aspekt):
    """Rzut punktu na ekran (0–1, 0–1) jak w Roblox (FieldOfView pionowe)."""
    f = [cel[i] - kam[i] for i in range(3)]
    n = math.sqrt(sum(x * x for x in f))
    f = [x / n for x in f]
    r = [-f[2], 0.0, f[0]]
    rn = math.sqrt(r[0] ** 2 + r[2] ** 2)
    r = [r[0] / rn, 0.0, r[2] / rn]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    d = [p[i] - kam[i] for i in range(3)]
    z = sum(d[i] * f[i] for i in range(3))
    x = sum(d[i] * r[i] for i in range(3))
    y = sum(d[i] * u[i] for i in range(3))
    t = math.tan(math.radians(fov / 2))
    return 0.5 + x / (z * t * aspekt) / 2, 0.5 - y / (z * t) / 2


# ------------------------------------------------------------------------------------------------ dźwięki
def dzwieki(U):
    ident = czytaj_json(sciezka_repo("swiat/dzwiek_gra/identyfikatory.json"))
    mapa = czytaj_json(sciezka_repo("assets/audio/arkusz/sfx_arkusz_a.json"))
    efekty = {}
    for rola, nazwa in U["dzwieki"].items():
        if rola in ("glosnosc", "opis"):
            continue
        e = mapa["efekty"].get(nazwa)
        if e is None:
            raise BladDanych("dźwięk %s → %s: brak w mapie arkusza" % (rola, nazwa))
        start = e["poczatek"] + max(0.0, float(e.get("atak", 0)) - 0.04)
        efekty[rola] = {"od": _r(start, 3), "koniec": _r(e["koniec"], 3), "glosnosc": U["dzwieki"]["glosnosc"].get(rola, 0.5)}
    return {"arkusz": int(ident["arkusz"] or 0), "efekty": efekty}


# ------------------------------------------------------------------------------------------------ całość
def dane(U, W=None):
    W = W or wzorce(U)
    P = pety(U, W)
    st = U["strefy"]
    if [s["r"] for s in st] != sorted(s["r"] for s in st) or st[-1]["r"] != U["scena"]["arena_r"]:
        raise BladDanych("strefy od środka, ostatnia do krawędzi areny")
    for pid in U["gracz"]["pety_startowe"]:
        if pid not in {p["id"] for p in P}:
            raise BladDanych("pet startowy %s bez wpisu w pety" % pid)
    if len(U["boty"]["wagi_stopni"]) != len(U["rzadkosci"]):
        raise BladDanych("boty.wagi_stopni: po jednej wadze na rzadkość")
    D = {
        "wersja": 1,
        "kontener": U["kontener"], "prefiks": U["prefiks"], "wylacznik": U["wylacznik"], "folderWzorcow": U["folder_wzorcow_rs"],
        "scena": {k: v for k, v in bez_opisu(U["scena"]).items() if k not in ("swiatlo", "atmosfera")},
        "strefy": st, "kamera": bez_opisu(U["kamera"]), "walka": bez_opisu(U["walka"]), "rzut": bez_opisu(U["rzut"]),
        "zloto": bez_opisu(U["zloto"]), "nagroda": bez_opisu(U["nagroda"]), "umiejetnosc": bez_opisu(U["umiejetnosc"]),
        "odpoczynek": U["odpoczynek_s"], "boty": bez_opisu(U["boty"]), "gracz": bez_opisu(U["gracz"]),
        "rzadkosci": U["rzadkosci"], "pety": P, "sloty": sloty(U), "ui": bez_opisu(U["ui"]), "dzwieki": dzwieki(U),
        "gwiazdki": bez_opisu(U["gwiazdki"]), "tarcza": bez_opisu(U["tarcza"]), "trener": bez_opisu(U["trener"]),
        "wydarzenia": bez_opisu(U["wydarzenia"]), "zapis": bez_opisu(U["zapis"]), "tablice": tablice(U),
        "tabliceCo": U["tablice"]["co_s"], "pokazanie": bez_opisu(U["pokazanie"]),
        "jajka": [{"nr": i + 1, "nazwa": J["nazwa"], "cena": J["cena"], "szanse": J["szanse"], "kolor": J["kolor"],
                   "wzorzec": "Jajko_" + J["model"], "wysokosc": WYSOKOSC_JAJKA} for i, J in enumerate(U["jajka"])],
        "stanowisko": stanowisko_jajek(U),
        "boss": dict(bez_opisu(U["boss"]), modele=[{"wzorzec": "Boss_" + B["model"], "nazwa": B["nazwa"]} for B in U["boss"]["modele"]]),
        "zloty": dict(bez_opisu(U["zloty"]), nr=[p["id"] for p in P].index(U["zloty"]["model"]) + 1),
    }
    for J in U["jajka"]:
        if abs(sum(J["szanse"]) - 1) > 1e-9 or len(J["szanse"]) != len(U["rzadkosci"]):
            raise BladDanych("jajko %s: szanse na każdą rzadkość, suma 1" % J["nazwa"])
    tekst = json.dumps(D, sort_keys=True, ensure_ascii=False)
    D["skrot"] = hashlib.sha1((tekst + json.dumps(U["scena"], sort_keys=True)).encode("utf-8")).hexdigest()[:12]
    return D


def luau(v, wciecie=0):
    """Wartość Pythona jako literał Luau (słowniki z kluczami-identyfikatorami jako pola)."""
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return str(int(v))
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        if all(not isinstance(x, (dict, list, tuple)) for x in v):
            return "{ " + ", ".join(luau(x) for x in v) + " }" if v else "{}"
        w = "\t" * (wciecie + 1)
        return "{\n" + "".join(w + luau(x, wciecie + 1) + ",\n" for x in v) + "\t" * wciecie + "}"
    if isinstance(v, dict):
        if not v:
            return "{}"
        w = "\t" * (wciecie + 1)
        czesci = []
        for k in sorted(v):
            klucz = k if (isinstance(k, str) and k.isidentifier() and k.isascii() and k not in SLOWA_LUAU) else "[%s]" % luau(k)
            czesci.append("%s%s = %s,\n" % (w, klucz, luau(v[k], wciecie + 1)))
        return "{\n" + "".join(czesci) + "\t" * wciecie + "}"
    raise TypeError(type(v))


def tekst_danych(D):
    return ("--[[\n\tDanePetArena — WYGENEROWANE przez swiat/pet_arena/dane.py z swiat/pet_arena/ustawienia.json i modeli\n"
            "\tpetów (swiat/postacie). NIE EDYTUJ RĘCZNIE: zmień ustawienia i uruchom python -B swiat/pet_arena/dane.py.\n]]\n"
            + STRAZNIK + "\n\treturn {}\nend\n\nreturn " + luau(D) + "\n")


def wszystkie_pliki():
    U = ustawienia()
    D = dane(U)
    return U, D, {PLIK_DANYCH: tekst_danych(D)}


def nieaktualne(pliki):
    zle = []
    for nazwa, tekst in pliki.items():
        s = os.path.join(ZRODLA, nazwa)
        try:
            with open(s, encoding="utf-8") as f:
                if f.read().replace("\r\n", "\n") != tekst:
                    zle.append(nazwa)
        except OSError:
            zle.append(nazwa)
    return zle


def tabela(U, D):
    w = ["Pet Arena — dane %s: %d petów, %d stref, %d slotów" % (D["skrot"], len(D["pety"]), len(D["strefy"]), len(D["sloty"]))]
    for p in D["pety"]:
        w.append("  %-15s %-10s %-6s życie %5.1f cios %4.1f odrzut %4.1f prędk. %3.1f r %.1f brył %3d  %s (%s)" % (
            p["nazwa"], U["rzadkosci"][p["stopien"] - 1]["nazwa"], p["klasa"], p["zycie"], p["obrazenia"], p["odrzut"],
            p["predkosc"], p["promien"], p["czesci"], p["umiejetnosc"]["nazwa"], p["umiejetnosc"]["typ"]))
    w.append("  scena: %d części" % len(scena(U)))
    return w


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Dane Pet Arena → zrodla/DanePetArena.luau")
    ap.add_argument("--sprawdz", action="store_true")
    a = ap.parse_args()
    try:
        U, D, pliki = wszystkie_pliki()
    except BladDanych as e:
        print("BŁĄD danych:", e)
        return 2
    for linia in tabela(U, D):
        print(linia)
    zle = nieaktualne(pliki)
    if a.sprawdz:
        print("dane: %s" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle)))
        return 1 if zle else 0
    os.makedirs(ZRODLA, exist_ok=True)
    for nazwa in zle:
        with open(os.path.join(ZRODLA, nazwa), "w", encoding="utf-8", newline="\n") as f:
            f.write(pliki[nazwa])
        print("zapisano zrodla/%s" % nazwa)
    if not zle:
        print("bez zmian")
    return 0


if __name__ == "__main__":
    sys.exit(main())
