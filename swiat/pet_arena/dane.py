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
            "promien": _r(min(1.25 * KW["promien_baza"] * K["rozmiar"], max(KW["promien_baza"] * K["rozmiar"], 0.6 * w["szer"]))),
            "rozmiar": K["rozmiar"], "wysokosc": w["wysokosc"],
            "wzorzec": nazwa_wzorca(P["id"]), "czesci": len(w["bryly"]), "umiejetnosc": A,
        })
    return lista


# ------------------------------------------------------------------------------------------------ scena
def _kol(a):
    return math.radians(a)


def _blisko_bramy(U, a):
    """Czy kąt a (radiany) leży w otworze bramy bossa."""
    S = U["scena"]
    b = _kol(S["brama_kat_st"])
    pol = math.atan2(S["brama_szer"] / 2 + 3, S["mur_r"][0])
    d = (a - b + math.pi) % (2 * math.pi) - math.pi
    return abs(d) < pol


def scena(U):
    """Części sceny (v2: jasne koloseum): [kształt (0 blok, 1 kula, 2 walec, 3 klin), grupa, x, y, z, rx, ry, rz (radiany,
    fromOrientation), sx, sy, sz, kolor, materiał, przezroczystość, kolizja (0/1), nazwa]. Walec: oś X (rz = 90° stawia)."""
    S = U["scena"]
    R = S["arena_r"]
    n = S["segmenty"]
    c = []

    def dodaj(ks, grupa, poz, obr, roz, kolor, mat="SmoothPlastic", przez=0.0, koliz=1, nazwa="Klocek"):
        c.append([ks, grupa, _r(poz[0], 3), _r(poz[1], 3), _r(poz[2], 3), _r(obr[0], 5), _r(obr[1], 5), _r(obr[2], 5),
                  _r(roz[0], 3), _r(roz[1], 3), _r(roz[2], 3), kolor, mat, przez, koliz, nazwa])

    def walec(grupa, r, y_gora, grubosc, kolor, mat="SmoothPlastic", przez=0.0, koliz=1, nazwa="Walec"):
        dodaj(2, grupa, (0, y_gora - grubosc / 2, 0), (0, 0, math.pi / 2), (grubosc, 2 * r, 2 * r), kolor, mat, przez, koliz, nazwa)

    def pierscien(grupa, r0, r1, y0, y1, kolory, mat="SmoothPlastic", koliz=1, nazwa="Segment", ile=None, przez=0.0, brama=False):
        m = ile or n
        rs = (r0 + r1) / 2
        szer = 2 * math.pi * r1 / m + 0.2
        for i in range(m):
            a = 2 * math.pi * i / m
            if brama and _blisko_bramy(U, a):
                continue
            dodaj(0, grupa, (math.sin(a) * rs, (y0 + y1) / 2, math.cos(a) * rs), (0, a, 0), (szer, y1 - y0, r1 - r0),
                  kolory[i % len(kolory)], mat, przez, koliz, nazwa)

    # arena: piaskowa podłoga, pasy krawędzi, strefa wybicia za krawędzią
    walec("Arena", R, 0, S["arena_grubosc"], "EBCB8B", "Sand", nazwa="Podloga")
    pierscien("Arena", R - 1.2, R, -0.3, 0.08, ["FF4D4D", "FFF6E0"], nazwa="PasKrawedzi", ile=S["krawedz_pasow"])
    m0, m1 = S["mur_r"]
    yw = S["strefa_wybicia_y"]
    pierscien("Arena", R, m0, yw - 1, yw, ["C79E62", "BD9459"], "Sand", nazwa="StrefaWybicia", brama=False)
    # wzgórze króla: trzy okrągłe stopnie (strefy złota), obwódki, tron i słup światła na szczycie
    st = U["strefy"]
    for s in reversed(st):
        walec("Wzgorze", s["r"] + 0.5, s["wysokosc"] - 0.25, 0.3, "FFF6E0", "SmoothPlastic", nazwa="Obwodka_" + s["id"])
        walec("Wzgorze", s["r"], s["wysokosc"], s["wysokosc"], s["kolor"], s["material"], nazwa="Stopien_" + s["id"])
    h = st[0]["wysokosc"]
    dodaj(0, "Wzgorze", (0, h + 1.2, 1.4), (0, 0, 0), (4.2, 2.4, 1.0), "FFB000", "Foil", nazwa="TronOparcie")
    dodaj(0, "Wzgorze", (0, h + 0.5, 0), (0, 0, 0), (4.2, 1.0, 3.6), "FFB000", "Foil", nazwa="TronSiedzisko")
    # słup światła zaczyna się nad głowami (ciężki pet ma 14,4 st) — widać go z daleka, a nie zasłania bitki na tronie
    dodaj(2, "Wzgorze", (0, h + 38, 0), (0, 0, math.pi / 2), (44, 2.6, 2.6), "FFE68A", "Neon", przez=0.7, koliz=0, nazwa="SlupSwiatla")
    # mur areny (wewnętrzny) z pasem u góry; trybuny w kolorach sektorów; mur zewnętrzny z blankami
    yt = S["mur_y"]
    pierscien("Mur", m0, m1, yw - 1, yt - 1, ["D9A066", "CB9157", "E0AA70"], "Slate", nazwa="Mur", brama=True)
    pierscien("Mur", m0 - 0.2, m1 + 0.2, yt - 1, yt, ["3F6FD8", "FFC83D"], nazwa="PasMuru", brama=True)
    # niewidzialna bariera na krawędzi muru: awatar chodzi po murze i lożach, ale nie spada na arenę
    pierscien("Mur", m0 - 0.6, m0 - 0.2, yt, yt + 10, ["FFFFFF"], przez=1.0, nazwa="BarieraWew", ile=40)
    tr = S["trybuna_r"]
    k = S["trybuna_stopnie"]
    sz = (tr - m1) / k
    sektory = ["E84A4A", "3F8CE8", "F2C230", "4CC46A", "B85CE0", "F2853A", "3FC8C8", "E85CA8"]
    for t in range(k):
        r0 = m1 + t * sz
        y1 = yt + 3 * (t + 1)
        kolory = []
        for i in range(n):
            kolory.append(sektory[(i * 8 // n) % 8] if t % 2 == 0 else "F3E6C8")
        pierscien("Trybuny", r0, r0 + sz, yt - 1, y1, kolory, "SmoothPlastic", nazwa="Stopien%d" % (t + 1), brama=True)
    yz = S["mur_zewn_y"]
    pierscien("MurZewn", tr, tr + 2.5, yt - 1, yz, ["D9A066", "CB9157"], "Slate", nazwa="MurZewn", brama=True)
    for i in range(0, n, 2):
        a = 2 * math.pi * i / n
        if _blisko_bramy(U, a):
            continue
        dodaj(0, "MurZewn", (math.sin(a) * (tr + 1.25), yz + 1.2, math.cos(a) * (tr + 1.25)), (0, a, 0), (3.2, 2.4, 2.5), "E0AA70", "Slate",
              nazwa="Blanka")
    # proporce na murze zewnętrznym
    for i in range(S["proporcow"]):
        a = 2 * math.pi * (i + 0.5) / S["proporcow"]
        if _blisko_bramy(U, a):
            continue
        x, z = math.sin(a) * (tr + 1.25), math.cos(a) * (tr + 1.25)
        dodaj(0, "Proporce", (x, yz + 5, z), (0, a, 0), (0.4, 10, 0.4), "6B4426", "Wood", nazwa="Maszt")
        dodaj(0, "Proporce", (x + math.cos(a) * 2.2, yz + 8.4, z - math.sin(a) * 2.2), (0, a, 0), (4, 2.8, 0.2), sektory[i % 8], "Fabric",
              koliz=0, nazwa="Proporzec")
    # kibice z klocków na trybunach (grupy według sektorów — klient podskakuje nimi)
    for i in range(S["kibicow"]):
        a = 2 * math.pi * ((i * 0.6180339887) % 1.0)
        if _blisko_bramy(U, a):
            continue
        t = (i * 7) % k
        r = m1 + t * sz + sz / 2
        y = yt + 3 * (t + 1)
        x, z = math.sin(a) * r, math.cos(a) * r
        sek = int(((a % (2 * math.pi)) / (2 * math.pi)) * 8) + 1
        kol = sektory[(i * 3) % 8]
        dodaj(0, "Kibice%d" % sek, (x, y + 1.5, z), (0, a, 0), (2.0, 3.0, 1.4), kol, nazwa="Kibic")
        dodaj(1, "Kibice%d" % sek, (x, y + 3.8, z), (0, a, 0), (1.8, 1.8, 1.8), ["F5D0A9", "C98E5E", "8A5A3A", "FFE0BD"][i % 4], nazwa="Glowa")
    # paleniska z kolorowym ogniem na murze (między lożami)
    ognie = ["FF8A1F", "3FA9F5", "B85CE0", "4CD964", "FF4DA6", "FFD23F", "3FE0D0", "FF5A3D"]
    nr = 0
    for i in range(S["palenisk"]):
        a = 2 * math.pi * i / S["palenisk"]
        if _blisko_bramy(U, a) or abs(((a - _kol(S["jajka_kat_st"])) + math.pi) % (2 * math.pi) - math.pi) < 0.2:
            continue
        nr += 1
        x, z = math.sin(a) * (m0 + 1.5), math.cos(a) * (m0 + 1.5)
        dodaj(2, "Paleniska", (x, yt + 1.2, z), (0, 0, math.pi / 2), (2.4, 2.2, 2.2), "6B6B70", "Slate", nazwa="Postument")
        dodaj(2, "Paleniska", (x, yt + 2.8, z), (0, 0, math.pi / 2), (1.0, 4.2, 4.2), "3A3A40", "Metal", nazwa="Misa")
        for j in range(3):
            dodaj(1, "Ogien%d" % nr, (x + (j - 1) * 0.7, yt + 4.0 + (j % 2) * 0.8, z), (0, 0, 0), (1.6, 2.6 - (j % 2) * 0.6, 1.6),
                  ognie[i % len(ognie)], "Neon", przez=0.15, koliz=0, nazwa="Plomien")
    # brama bossa: dwie wieże, łuk, krata
    b = _kol(S["brama_kat_st"])
    bx, bz = math.sin(b), math.cos(b)
    px, pz = math.cos(b), -math.sin(b)
    rb = (m0 + tr) / 2
    W2 = S["brama_szer"] / 2
    for s in (-1, 1):
        dodaj(0, "Brama", (bx * rb + px * s * (W2 + 3), (yw + S["brama_wys"] + 6) / 2, bz * rb + pz * s * (W2 + 3)), (0, b, 0),
              (6, S["brama_wys"] + 6 - yw, tr - m0 + 2), "C98D55", "Slate", nazwa="Wieza")
        dodaj(0, "Brama", (bx * rb + px * s * (W2 + 3), S["brama_wys"] + 7, bz * rb + pz * s * (W2 + 3)), (0, b, 0), (7, 2, tr - m0 + 3),
              "3F6FD8", nazwa="WiezaPas")
    dodaj(0, "Brama", (bx * rb, S["brama_wys"] + 2, bz * rb), (0, b, 0), (S["brama_szer"] + 2, 4, tr - m0 + 2), "C98D55", "Slate", nazwa="Luk")
    dodaj(0, "Brama", (bx * (tr + 1), S["brama_wys"] / 2, bz * (tr + 1)), (0, b, 0), (S["brama_szer"], S["brama_wys"], 1), "2A1E18", "Wood",
          koliz=0, nazwa="Wrota")
    for i in range(5):
        o = (i - 2) * S["brama_szer"] / 5
        dodaj(0, "Brama", (bx * (m0 + 0.5) + px * o, S["brama_wys"] / 2 + 1, bz * (m0 + 0.5) + pz * o), (0, b, 0),
              (0.5, S["brama_wys"] - 2, 0.5), "3A3A40", "Metal", koliz=0, nazwa="Krata")
    # loże graczy na murze: podłoga w kolorze miejsca, poręcz, daszek
    for s in sloty(U):
        a = s["kat"]
        x, z = math.sin(a) * S["slot_r"], math.cos(a) * S["slot_r"]
        dodaj(0, "Loze", (x, yt + 0.2, z), (0, a, 0), (8, 0.4, 5), s["kolor"], nazwa="Loza%d" % s["nr"])
        dodaj(0, "Loze", (x - math.sin(a) * 2.6, yt + 1.3, z - math.cos(a) * 2.6), (0, a, 0), (8, 0.4, 0.4), "9A6234", "Wood", nazwa="Porecz")
        for q in (-1, 1):
            px2, pz2 = math.cos(a) * q * 3.8, -math.sin(a) * q * 3.8
            dodaj(0, "Loze", (x + px2, yt + 3, z + pz2), (0, a, 0), (0.5, 6, 0.5), "9A6234", "Wood", nazwa="Slup")
        px3, pz3 = math.cos(a) * 3.8, -math.sin(a) * 3.8
        dodaj(0, "Loze", (x + px3 + math.cos(a) * 1.6, yt + 5.0, z + pz3 - math.sin(a) * 1.6), (0, a, 0), (3, 2, 0.15), s["kolor"], "Fabric",
              koliz=0, nazwa="Choragiewka")
    # wylęgarnia: cokoły jajek (jajka z wzorców stawia zbuduj.py) i maty treningowe przy lożach
    for kk, (x, z) in enumerate(stanowisko_jajek(U)["cokoly"]):
        dodaj(2, "Jajka", (x, yt + 0.6, z), (0, 0, math.pi / 2), (1.2, 5.2, 5.2), "8C8A84", "Slate", nazwa="Cokol")
        dodaj(2, "Jajka", (x, yt + 1.25, z), (0, 0, math.pi / 2), (0.15, 5.5, 5.5), U["jajka"][kk]["kolor"], "Neon", koliz=0, nazwa="Obrecz")
    for s in sloty(U):
        m = s["mata"]
        dodaj(0, "Maty", (m[0], yt + 0.12, m[2]), (0, s["kat"], 0), (5, 0.24, 5), "3DB36B", "Fabric", nazwa="Mata%d" % s["nr"])
    return c


def stanowisko_jajek(U):
    """Wylęgarnia na murze areny (kąt jajka_kat_st): trzy cokoły w rzędzie i tablica szans za nimi."""
    S = U["scena"]
    a = _kol(S["jajka_kat_st"])
    cokoly = []
    for k in range(len(U["jajka"])):
        da = (k - 1) * 0.11
        cokoly.append((_r(math.sin(a + da) * S["jajka_r"]), _r(math.cos(a + da) * S["jajka_r"])))
    r = S["jajka_r"] + 3.5
    return {"cokoly": cokoly, "tablica": [_r(math.sin(a) * r), S["mur_y"] + 5, _r(math.cos(a) * r)], "patrz": [0, S["mur_y"] + 5, 0]}


def makiety_napisy(U):
    """Tablica szans przy wylęgarni."""
    st = stanowisko_jajek(U)
    linie = []
    for J in U["jajka"]:
        szanse = "  ".join("%s %g%%" % (R["nazwa"][0], s * 100) for R, s in zip(U["rzadkosci"], J["szanse"]) if s > 0)
        linie.append("%s  %d G   %s" % (J["nazwa"], J["cena"], szanse))
    return [{"tekst": "EGGS\n" + "\n".join(linie), "poz": st["tablica"], "patrz": st["patrz"], "szer": 16, "wys": 6}]


def tablice(U):
    T = U["tablice"]
    S = U["scena"]
    w = []
    for i, (tytul, kat) in enumerate(zip(T["tytuly"], T["katy_st"])):
        a = _kol(kat)
        r = S["mur_r"][0] - 0.3
        w.append({"nr": i + 1, "tytul": tytul, "poz": [_r(math.sin(a) * r), T["y"], _r(math.cos(a) * r)], "patrz": [0, T["y"], 0],
                  "szer": T["szer"], "wys": T["wys"], "wierszy": T["wierszy"]})
    return w


def etykiety_stref(U):
    """Małe znaki x1 / x2 / x5 na stopniach wzgórza (po 4 na stopień, na skos)."""
    st = U["strefy"]
    w = []
    for i, s in enumerate(st):
        r_in = st[i - 1]["r"] if i > 0 else 0
        rr = (r_in + s["r"]) / 2 if i > 0 else 3.2
        for k in range(4 if i > 0 else 1):
            a = math.pi / 4 + k * math.pi / 2 + (0 if i == 1 else math.pi / 4)
            w.append({"tekst": "x%d" % s["mnoznik"], "poz": [_r(math.sin(a) * rr) if i > 0 else 0, s["wysokosc"] + 0.07,
                                                            _r(math.cos(a) * rr) if i > 0 else -2.4], "r": _r(a, 4),
                      "wielkosc": 4 if i > 0 else 3})
    return w


def sloty(U):
    """Loże graczy na murze areny: miejsce stania, kąt kamery (obok, by awatar był z boku kadru), kolor, mata."""
    S = U["scena"]
    w = []
    for i in range(S["sloty"]):
        a = _kol(S["slot_kat0_st"] + 360.0 * i / S["sloty"])
        am = a + _kol(S["mata_kat_st"])
        w.append({"nr": i + 1, "poz": [_r(math.sin(a) * S["slot_r"]), S["mur_y"] + 0.4, _r(math.cos(a) * S["slot_r"])],
                  "kat": _r(a, 5), "katKamery": _r(a + _kol(8), 5), "kolor": U["gracz"]["kolory_slotow"][i],
                  "mata": [_r(math.sin(am) * S["mata_r"]), S["mur_y"] + 0.4, _r(math.cos(am) * S["mata_r"])]})
    return w


def brama(U):
    S = U["scena"]
    b = _kol(S["brama_kat_st"])
    r = S["trybuna_r"] + 4
    return {"x": _r(math.sin(b) * r), "z": _r(math.cos(b) * r), "kat": _r(b, 5)}

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
    if [s["r"] for s in st] != sorted(s["r"] for s in st) or st[-1]["r"] >= U["scena"]["arena_r"]:
        raise BladDanych("strefy od środka, wszystkie na arenie")
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
        "zloty": bez_opisu(U["zloty"]), "brama": brama(U), "sterowanie": bez_opisu(U["sterowanie"]),
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
