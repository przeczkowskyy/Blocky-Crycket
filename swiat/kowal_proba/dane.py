#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator danych kowala na próbę (swiat/kowal_proba) — z ustawienia.json, katalogu przedmiotów
(swiat/postacie/przedmioty.json), wzoru postaci (tools/walka/wzorcowe.py, dane_walki.json), mapy bazaru
(swiat/miasteczko_bazar: uklad.json, czesci.json, znaczniki.json) i modelu kowala (swiat/postacie/kowal.py).

    python -B swiat/kowal_proba/dane.py            # zapisuje zrodla/DaneKowala.luau, zrodla/RigKowal.luau, kuznia/czesci.json
    python -B swiat/kowal_proba/dane.py --sprawdz  # tylko sprawdza, czy pliki są aktualne (kod 1, gdy nie)

Co sprawdza (błąd = BladDanych, nic nie jest zapisywane): każdy CAŁY przedmiot bohatera z katalogu (zestawy rycerz,
kot_mag, zwiadowca; bez części zbroi „czesc_od”) ma wpis w ustawieniach i odwrotnie; slot i klasa z katalogu; każda klasa
ma podstawowy zestaw z bronią i zbroją (Wojownik — także z tarczą, bo blok tarczy ze wzoru należy do tarczy); znane
statystyki i liczby; koszty ulepszeń rosną; kuźnia stoi w wolnym miejscu bazaru (obrys bez cudzych części od bruku do
wysokości dachu, poza środkowym pasem uliczki, punkt E dalej niż `odstep_e` od cudzych punktów E).
"""
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA = os.path.join(REPO, "tools", "walka")
for _s in (TU, REPO, WALKA):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import logika_kowala as LK  # noqa: E402
import wzorcowe  # noqa: E402

ZRODLA = os.path.join(TU, "zrodla")
PLIK_DANYCH = "DaneKowala.luau"
PLIK_RIGU = "RigKowal.luau"
PLIK_KUZNI = os.path.join(TU, "kuznia", "czesci.json")
KATALOG = os.path.join(REPO, "swiat", "postacie", "przedmioty.json")
BAZAR = os.path.join(REPO, "swiat", "miasteczko_bazar")
ZESTAWY_BOHATEROW = ("rycerz", "zwiadowca", "kot_mag")
KOLEJNOSC_SLOTOW = ["Weapon", "OffHand", "Chest", "Helmet", "Gloves", "Boots", "Belt"]


class BladDanych(Exception):
    pass


def ustawienia():
    with open(os.path.join(TU, "ustawienia.json"), encoding="utf-8") as f:
        return json.load(f)


def katalog():
    with open(KATALOG, encoding="utf-8") as f:
        return json.load(f)


def _json(sciezka):
    with open(sciezka, encoding="utf-8") as f:
        return json.load(f)


def klasy_z_tarcza():
    d = _json(os.path.join(WALKA, "dane_walki.json"))
    return {k: bool(v.get("tarcza")) for k, v in d["klasy"].items()}


# ------------------------------------------------------------------------------------------------ przedmioty
def przedmioty(U, K):
    """Całe przedmioty bohaterów z katalogu + liczby z ustawień → (przedmioty, części zbroi, klasy)."""
    sloty = U["sloty"]
    staty = [s[0] for s in U["statystyki"]]
    tarcze = klasy_z_tarcza()
    klasy = list(U["nazwy_klas"])
    kat = [p for p in K["przedmioty"] if p["zestaw"] in ZESTAWY_BOHATEROW]
    calosci = [p for p in kat if not p.get("czesc_od")]
    czesci = {p["id"]: p["czesc_od"] for p in kat if p.get("czesc_od")}
    ids_kat = {p["id"] for p in calosci}
    ids_ust = set(U["przedmioty"])
    if ids_kat != ids_ust:
        raise BladDanych("ustawienia.przedmioty ≠ katalog: brak %s, nadmiar %s" % (sorted(ids_kat - ids_ust),
                                                                                 sorted(ids_ust - ids_kat)))
    for c, cal in czesci.items():
        if cal not in ids_kat:
            raise BladDanych("część %s: całość %s spoza katalogu" % (c, cal))
    G = U["ulepszenie"]
    maks = G["maks"]
    if len(G["zloto"]) != maks or len(G["materialy"]) != maks:
        raise BladDanych("ulepszenie: %d kosztów Złota i materiałów (maks)" % maks)
    for nazwa in ("zloto", "materialy"):
        t = G[nazwa]
        if any((not isinstance(x, int)) or x < 1 for x in t) or any(t[i] > t[i + 1] for i in range(maks - 1)):
            raise BladDanych("ulepszenie.%s: liczby całkowite ≥ 1, nie malejące" % nazwa)
    wynik = {}
    for p in calosci:
        u = U["przedmioty"][p["id"]]
        klasa = (p.get("klasy") or [None])[0]
        if klasa not in klasy or len(p.get("klasy") or []) != 1:
            raise BladDanych("przedmiot %s: jedna klasa z %s" % (p["id"], klasy))
        if p["slot"] not in sloty:
            raise BladDanych("przedmiot %s: slot %s spoza ustawienia.sloty" % (p["id"], p["slot"]))
        for pole in ("baza", "krok"):
            for k, v in u[pole].items():
                if k not in staty:
                    raise BladDanych("przedmiot %s: nieznana statystyka %s" % (p["id"], k))
                if k == "tarcza":
                    if not tarcze.get(klasa) or p["slot"] != "OffHand":
                        raise BladDanych("przedmiot %s: tarcza tylko w drugiej ręce klasy z tarczą" % p["id"])
                    if not (0 <= v <= 0.1):
                        raise BladDanych("przedmiot %s: tarcza 0..0,1" % p["id"])
                elif not isinstance(v, int) or v < 0:
                    raise BladDanych("przedmiot %s: %s.%s liczba całkowita ≥ 0" % (p["id"], pole, k))
        if not u["krok"]:
            raise BladDanych("przedmiot %s: ulepszenie bez przyrostu" % p["id"])
        waga = u["waga"]
        if not (isinstance(waga, (int, float)) and 0.5 <= waga <= 3):
            raise BladDanych("przedmiot %s: waga 0,5..3" % p["id"])
        zl = [int(G["zaokraglenie_zlota"] * math.floor(x * waga / G["zaokraglenie_zlota"] + 0.5)) for x in G["zloto"]]
        mat = [int(math.floor(x * waga + 0.5)) for x in G["materialy"]]
        wynik[p["id"]] = {"id": p["id"], "nazwa": p["nazwa"], "slot": p["slot"], "klasa": klasa,
                          "podstawowy": bool(u["podstawowy"]), "waga": waga,
                          "baza": {k: u["baza"][k] for k in staty if k in u["baza"]},
                          "krok": {k: u["krok"][k] for k in staty if k in u["krok"]},
                          "koszt": {"zloto": zl, "materialy": mat}}
    kl = {}
    for k in klasy:
        ids = sorted((i for i, P in wynik.items() if P["klasa"] == k),
                     key=lambda i: (KOLEJNOSC_SLOTOW.index(wynik[i]["slot"]), i))
        sloty_kl = [wynik[i]["slot"] for i in ids]
        if len(set(sloty_kl)) != len(sloty_kl):
            raise BladDanych("klasa %s: dwa przedmioty w jednym slocie — logika zakłada jeden na slot" % k)
        podst = [i for i in ids if wynik[i]["podstawowy"]]
        sl = {wynik[i]["slot"] for i in podst}
        if not {"Weapon", "Chest"} <= sl:
            raise BladDanych("klasa %s: podstawowy zestaw bez broni albo zbroi" % k)
        if tarcze.get(k) and "OffHand" not in sl:
            raise BladDanych("klasa %s: podstawowy zestaw bez tarczy (blok tarczy ze wzoru należy do tarczy)" % k)
        kl[k] = {"przedmioty": ids, "podstawowe": podst, "tarcza": bool(tarcze.get(k))}
    return wynik, czesci, kl


# ------------------------------------------------------------------------------------------------ kuźnia w bazarze
def _obrot_y(ry, v):
    r = math.radians(ry)
    return (math.cos(r) * v[0] + math.sin(r) * v[2], v[1], -math.sin(r) * v[0] + math.cos(r) * v[2])


def _swiat(kz, lokalny):
    p = _obrot_y(kz["ry"], lokalny)
    return [round(kz["srodek_swiat"][i] + p[i], 3) for i in range(3)]


def polozenie_kuzni(U):
    """Środek kuźni w świecie, punkt E, miejsce kowala; sprawdzenie miejsca w bazarze."""
    kz = dict(U["kuznia"])
    uk = _json(os.path.join(BAZAR, "uklad.json"))
    X0, Z0 = uk["swiat"]["X0"], uk["swiat"]["Z0"]
    bx, bz = kz["srodek_bazar"]
    kz["srodek_swiat"] = [X0 + bx, kz["y_podlogi"], Z0 + bz]
    from kuznia import PODLOGA
    e = _swiat(kz, (kz["punkt_e"][0], 1.2, kz["punkt_e"][1]))
    kowal = _swiat(kz, (kz["kowal"][0], PODLOGA, kz["kowal"][1]))
    return kz, e, kowal, (X0, Z0)


def sprawdz_miejsce(U, kz, e, X0Z0, scena):
    """Obrys kuźni (z częściami obróconymi) bez cudzych części bazaru, poza pasem uliczki, punkt E z odstępem."""
    from swiat.biblioteka.scena import macierz_obrotu
    X0, Z0 = X0Z0
    st = scena.statystyki()["zakres"]
    mn, mx = st["min"], st["max"]
    uw = []
    if mx[1] > kz["y_podlogi"] + kz["wysokosc_maks"]:
        uw.append("kuźnia za wysoka (%.1f > %.1f — girlandy bazaru)" % (mx[1], kz["y_podlogi"] + kz["wysokosc_maks"]))
    if min(abs(mn[2] - Z0), abs(mx[2] - Z0)) < kz["pas_uliczki"] or (mn[2] - Z0) * (mx[2] - Z0) < 0:
        uw.append("kuźnia w środkowym pasie uliczki (|z| < %.0f)" % kz["pas_uliczki"])
    d = _json(os.path.join(BAZAR, "czesci.json"))
    kolizje = []
    for c in d["czesci"]:
        ks, g, x, y, z, rx, ry, rz, sx, sy, sz = c[:11]
        R = macierz_obrotu(math.degrees(rx), math.degrees(ry), math.degrees(rz))
        pol = [(abs(R[i][0]) * sx + abs(R[i][1]) * sy + abs(R[i][2]) * sz) / 2.0 for i in range(3)]
        if y + pol[1] <= kz["y_podlogi"] + 0.4 or y - pol[1] >= mx[1]:
            continue                                  # bruk, kody na bruku i to, co wyżej niż dach kuźni
        if "Niewidzialna" in c[14]:
            continue
        if x + pol[0] > mn[0] and x - pol[0] < mx[0] and z + pol[2] > mn[2] and z - pol[2] < mx[2]:
            kolizje.append("%s (%s)" % (c[14], d["grupy"][g].split("/")[-1]))
    if kolizje:
        uw.append("w obrysie kuźni stoją części bazaru: " + ", ".join(sorted(set(kolizje))[:8]))
    zn = _json(os.path.join(BAZAR, "znaczniki.json"))
    for sciezka in kz["inne_e"]:
        a, b = sciezka.split("/")
        w = zn[a]
        w = next(x for x in w if x.get("id") == b) if isinstance(w, list) else w[b]
        p = w.get("podpowiedz") or w["swiat"]
        odl = math.hypot(p[0] - e[0], p[2] - e[2])
        if odl < kz["odstep_e"]:
            uw.append("punkt E kowala %.1f st od %s (< %.0f)" % (odl, sciezka, kz["odstep_e"]))
    if uw:
        raise BladDanych("miejsce kuźni: " + "; ".join(uw))
    return {"zakres": st, "odstepy": {s: round(math.hypot(_e(zn, s)[0] - e[0], _e(zn, s)[2] - e[2]), 1)
                                      for s in kz["inne_e"]}}


def _e(zn, sciezka):
    a, b = sciezka.split("/")
    w = zn[a]
    w = next(x for x in w if x.get("id") == b) if isinstance(w, list) else w[b]
    return w.get("podpowiedz") or w["swiat"]


def scena_kuzni(U):
    import kuznia
    kz, e, kowal, x0z0 = polozenie_kuzni(U)
    s = kuznia.scena(kz["srodek_swiat"], kz["ry"], "Workspace/" + U["kontener"])
    return s, kz, e, kowal, x0z0


# ------------------------------------------------------------------------------------------------ rig kowala
def _r(v, n=3):
    x = round(float(v), n)
    return 0 if x == 0 else x


def rig_kowala(U):
    """Model swiat/postacie/kowal.py → zwięzły rig dla Studio (ten sam układ co rigi petów: RigKowala.luau)."""
    from swiat.postacie.biblioteka.roblox_klocki import probki_liniowe, rig
    from swiat.postacie.roblox_postac import postacie_z_modulu
    M = U["kowal"]
    p = next((x for x in postacie_z_modulu(os.path.join(REPO, "swiat", "postacie", M["modul"] + ".py"))
              if x.id == M["id"]), None)
    if p is None:
        raise BladDanych("brak modelu %s w swiat/postacie/%s.py" % (M["id"], M["modul"]))
    bledy, _uwagi = p.sprawdz()
    if bledy:
        raise BladDanych("model kowala: " + "; ".join(bledy))
    p.skala = float(M["skala"])
    d = rig(p, probki_liniowe(p))
    kosci = [[k[0], k[1]] + [_r(v) for v in k[2:11]] for k in d["kosci"]]
    czesci = [[c[0], c[1], c[2]] + [_r(v) for v in c[3:6]] + [_r(v, 4) for v in c[6:9]] + [_r(v) for v in c[9:12]]
              + [c[12].upper(), c[13], c[15]] for c in d["czesci"]]
    klipy = {}
    for kl in d["klipy"]:
        krok = 2 if kl["dl"] % 2 == 0 else 1
        klatki = [[_r(v) for v in kl["klatki"][f]] for f in range(0, kl["dl"] + 1, krok)]
        klipy[kl["n"]] = {"fps": kl["fps"] / krok, "petla": kl["petla"], "kosci": kl["kosci"], "klatki": klatki}
    for nazwa in (M["klip"], M["klip_radosci"]):
        if nazwa not in klipy:
            raise BladDanych("model kowala bez klipu %s" % nazwa)
    wys = max(c[4] + c[10] / 2 for c in d["czesci"])
    return {"id": p.id, "nazwa": p.nazwa, "skala": M["skala"], "hrp": [_r(v) for v in d["hrp"]], "kosci": kosci,
            "czesci": czesci, "materialy": d["materialy"], "klipy": klipy, "wysokosc": _r(wys)}


# ------------------------------------------------------------------------------------------------ dane całe
def podstawa():
    U = ustawienia()
    K = katalog()
    P, czesci, klasy = przedmioty(U, K)
    s, kz, e, kowal, x0z0 = scena_kuzni(U)
    miejsce = sprawdz_miejsce(U, kz, e, x0z0, s)
    from kuznia import PODLOGA
    D = {
        "wersja": 1, "status": U["status"], "kontener": U["kontener"], "prefiks": U["prefiks"],
        "klasyGracza": U["klasy_gracza"], "klasaDomyslna": U["klasa_domyslna"], "nazwyKlas": U["nazwy_klas"],
        "stan": {"kontener": U["stan"]["kontener"], "modyfikatory": U["stan"]["modyfikatory"],
                 "danePakietu": U["stan"]["dane_pakietu"], "wydaj": U["stan"]["wydaj"], "bohater": U["stan"]["bohater"],
                 "zrodloModyfikatorow": U["stan"]["zrodlo_modyfikatorow"], "pakiet": U["stan"]["pakiet"],
                 "zrodloWydatku": U["stan"]["zrodlo_wydatku"], "celWydatku": U["stan"]["cel_wydatku"],
                 "atrybutZlota": U["stan"]["atrybut_zlota"], "atrybutKlasy": U["stan"]["atrybut_klasy"],
                 "coIleS": U["stan"]["co_ile_s"]},
        "przymierzalnia": dict(U["przymierzalnia"]),
        "atrybuty": dict(U["atrybuty_gracza"]),
        "wersjaDanych": U["wersja_danych"],
        "ulepszenie": {"maks": U["ulepszenie"]["maks"]},
        "rozbiorka": dict(U["rozbiorka"]),
        "lup": {"atrybut": U["lup"]["atrybut_tokenow"], "progi": dict(U["lup"]["progi"]),
                "szansa": dict(U["lup"]["szansa"]), "ochrona": U["lup"]["ochrona"]},
        "statystyki": [{"id": a, "nazwa": b} for a, b in U["statystyki"]],
        "nazwyStatystyk": {a: b for a, b in U["statystyki"]},
        "sloty": dict(U["sloty"]),
        "klasy": klasy,
        "kolejnosc": [i for k in U["nazwy_klas"] for i in klasy[k]["przedmioty"]],
        "przedmioty": P,
        "czesci": czesci,
        "blokTarczy": wzorcowe.BLOK_TARCZY,
        "kuznia": {"srodek": kz["srodek_swiat"], "ry": kz["ry"], "e": e, "kowal": kowal,
                   "kowalRy": (kz["ry"] + 180) % 360, "podloga": PODLOGA, "zasieg": kz["zasieg"],
                   "zapasSerwera": kz["zapas_serwera"], "zasiegOkna": kz["zasieg_okna"],
                   "zakres": miejsce["zakres"], "odstepyE": miejsce["odstepy"]},
        "kowal": {"rig": "RigKowal", "klip": U["kowal"]["klip"], "klipRadosci": U["kowal"]["klip_radosci"]},
        "limit": U["limit_zapytan_s"],
        "ui": U["ui"],
        "teksty": U["teksty"],
    }
    return D, s


# ------------------------------------------------------------------------------------------------ przypadki wzorcowe
NIL = "<nil>"


def _nil(v):
    return NIL if v is None else v


def przypadki(D):
    """Wejścia i wyniki liczone lustrem (logika_kowala.py) — Luau sprawdza je w Studio (LogikaKowala.sprawdzPrzypadki)."""
    P = {"czyste": [], "mod": [], "koszt": [], "rozbierz": [], "plan": [], "lup": [], "stroj": [], "ranga": [],
         "widok": [], "opis": [], "odmiana": [], "mozna": []}
    for v in (None, "zle", {"przedmioty": {"rycerz_miecz": {"poziom": 3, "zapas": 1}, "nieznany": {"poziom": 1}},
                            "materialy": 7.5, "bezLupu": 2, "klasy": {"wojownik": True, "obcy": True}},
              {"przedmioty": {"kot_mag_kostur": {"poziom": 99, "zapas": -1}}, "materialy": -3}):
        P["czyste"].append({"v": _nil(v), "wynik": LK.czyste(D, v)})
    for k in D["klasy"]:
        pusta = LK.nowe(D)
        dane, _ = LK.podstawowe(D, pusta, k)
        pelna = LK.nowe(D)
        for i, pid in enumerate(D["klasy"][k]["przedmioty"]):
            pelna["przedmioty"][pid] = {"poziom": (i * 3) % (D["ulepszenie"]["maks"] + 1), "zapas": i % 2}
        pelna["materialy"] = 5
        for dn, napis in ((dane, None), (pelna, None), (pelna, ""), (pelna, D["klasy"][k]["przedmioty"][0])):
            zal = LK.zalozone(D, k, dn, napis)
            P["mod"].append({"klasa": k, "dane": dn, "napis": _nil(napis), "zalozone": zal,
                             "wynik": LK.mod(D, k, dn, zal)})
        for pid in D["klasy"][k]["przedmioty"]:
            for poz in (0, 4, D["ulepszenie"]["maks"]):
                P["koszt"].append({"id": pid, "poziom": poz, "wynik": _nil(LK.koszt(D, pid, poz))})
        for pid in (D["klasy"][k]["przedmioty"][0], D["klasy"][k]["przedmioty"][-1], "nieznany"):
            ok, w, zysk = LK.rozbierz(D, pelna, k, pid)
            P["rozbierz"].append({"klasa": k, "dane": pelna, "id": pid, "ok": ok, "wynik": w, "zysk": zysk})
            ok, w, ile = LK.plan_ulepszenia(D, pelna, k, pid)
            P["plan"].append({"klasa": k, "dane": pelna, "id": pid, "ok": ok, "wynik": w, "ile": ile})
        for rg, l1, l2 in (("zwykly", 0.05, 0.0), ("zwykly", 0.5, 0.7), ("straznik", 0.4, 0.99), ("rzadki", 0.9, 0.3)):
            w, wyn = LK.lup(D, dane, k, rg, l1, l2)
            P["lup"].append({"klasa": k, "dane": dane, "ranga": rg, "l1": l1, "l2": l2, "wynik": w, "lup": _nil(wyn)})
        ochr = dict(dane, bezLupu=D["lup"]["ochrona"] - 1)
        w, wyn = LK.lup(D, ochr, k, "zwykly", 0.99, 0.5)
        P["lup"].append({"klasa": k, "dane": ochr, "ranga": "zwykly", "l1": 0.99, "l2": 0.5, "wynik": w, "lup": _nil(wyn)})
        ids = D["klasy"][k]["przedmioty"]
        czesc = next((c for c, cal in D["czesci"].items() if D["przedmioty"][cal]["klasa"] == k), None)
        for napis in (None, "", ",".join(ids), ids[0] + "," + ids[-1], ",".join(ids + ([czesc] if czesc else []))):
            P["stroj"].append({"klasa": k, "dane": dane, "napis": _nil(napis),
                               "wynik": _nil(LK.stroj_do_ustawienia(D, k, dane, napis))})
        for zl in (0, 149, 150, 10000):
            for dn in (dane, pelna):
                P["mozna"].append({"klasa": k, "dane": dn, "zloto": zl, "wynik": LK.mozna_ulepszyc(D, k, dn, zl),
                                   "suma": LK.suma_poziomow(dn)})
        P["widok"].append({"klasa": k, "dane": pelna, "zalozone": LK.zalozone(D, k, pelna, None), "zloto": 150,
                           "bohater": "Broń 12", "wynik": LK.widok(D, pelna, k, LK.zalozone(D, k, pelna, None), 150,
                                                                  "Broń 12")})
    for r in (0, 1, 2, 3, 4, 5, 6, 7, -1, 1.5):
        P["ranga"].append({"r": r, "wynik": _nil(LK.ranga(D, r))})
    for o in ({"bron": {"obrazenia": 30.4}, "pancerz_przedmiotow": 13.5, "tarcza": {"blok": 0.2828}},
              {"bron": {"obrazenia": 12}}, "zle"):
        P["opis"].append({"opis": o, "wynik": LK.opis_bohatera(D, o)})
    for n in (0, 1, 2, 4, 5, 11, 12, 14, 21, 22, 25, 104, 112):
        P["odmiana"].append({"n": n, "mianownik": LK.ile_materialow(D, n), "dopelniacz": LK.ile_materialow_dop(D, n)})
    return P


def dane_z_przypadkami():
    D, s = podstawa()
    D["przypadki"] = przypadki(D)
    bez = {k: v for k, v in D.items() if k != "skrot"}
    D["skrot"] = hashlib.sha1(json.dumps(bez, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:12]
    return D, s


# ------------------------------------------------------------------------------------------------ zapis Luau
_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_SLOWA = {"and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in", "local", "nil", "not",
          "or", "repeat", "return", "then", "true", "until", "while", "continue", "export", "type"}


def _napis(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int):
        return str(x)
    r = repr(float(x))
    return r[:-2] if r.endswith(".0") else r


def _klucz(k):
    if isinstance(k, int):
        return "[%d]" % k
    return k if (_IDENT.match(k) and k not in _SLOWA) else "[%s]" % _napis(k)


def _luau(v, wciecie=1):
    if v is None:
        return "nil"
    if isinstance(v, (bool, int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    tab = "\t" * wciecie
    if isinstance(v, (list, tuple)):
        czesci = [_luau(x, wciecie + 1) for x in v]
    elif isinstance(v, dict):
        czesci = ["%s = %s" % (_klucz(k), _luau(x, wciecie + 1)) for k, x in v.items() if x is not None]
    else:
        raise TypeError(repr(v))
    jedna = "{ " + ", ".join(czesci) + " }" if czesci else "{}"
    if len(jedna) <= 110 and "\n" not in jedna:
        return jedna
    return "{\n" + "".join(tab + c + ",\n" for c in czesci) + "\t" * (wciecie - 1) + "}"


STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then\n\treturn {}\nend\n\nreturn '


def luau_danych(D):
    naglowek = ("--[[\n\tDaneKowala — WYGENEROWANE przez swiat/kowal_proba/dane.py z ustawienia.json, katalogu przedmiotów\n"
                "\t(swiat/postacie/przedmioty.json), wzoru postaci (tools/walka) i mapy bazaru. NIE EDYTUJ RĘCZNIE: zmień źródło\n"
                "\ti uruchom python -B swiat/kowal_proba/dane.py (testy i zbuduj.py --sucho pilnują aktualności). Status: propozycja.\n]]\n")
    return naglowek + STRAZNIK + _luau(D) + "\n"


def luau_rigu(R):
    naglowek = ("--[[\n\tRigKowal — rig z klocków modelu swiat/postacie/%s.py (skala %s), WYGENEROWANY przez swiat/kowal_proba/dane.py.\n"
                "\tUkład rigu Roblox (przód −Z, początek = ziemia pod postacią). kosci: {nazwa, rodzic, staw xyz, środek xyz,\n"
                "\trozmiar xyz}; czesci: {kość, kształt, nazwa, poz xyz, obrót xyz (rad), rozmiar xyz, kolor, materiał, siatka};\n"
                "\tklipy: klatki co 1/fps s, w wierszu po 6 liczb na kość z listy kosci (przes xyz, obrót xyz). NIE EDYTUJ RĘCZNIE.\n]]\n"
                % (R["id"], _liczba(R["skala"])))
    return naglowek + STRAZNIK + _luau(R) + "\n"


def tekst_kuzni(s):
    return json.dumps(s.json(), ensure_ascii=False, separators=(",", ":")) + "\n"


def wszystkie_pliki():
    D, s = dane_z_przypadkami()
    U = ustawienia()
    return D, {os.path.join(ZRODLA, PLIK_DANYCH): luau_danych(D), os.path.join(ZRODLA, PLIK_RIGU): luau_rigu(rig_kowala(U)),
               PLIK_KUZNI: tekst_kuzni(s)}


def zapisz():
    D, pliki = wszystkie_pliki()
    for sciezka, tekst in pliki.items():
        os.makedirs(os.path.dirname(sciezka), exist_ok=True)
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
    return D, pliki


def aktualny():
    D, pliki = wszystkie_pliki()
    zle = []
    for sciezka, tekst in pliki.items():
        if not os.path.isfile(sciezka):
            zle.append(os.path.relpath(sciezka, TU))
            continue
        with open(sciezka, encoding="utf-8") as f:
            if f.read() != tekst:
                zle.append(os.path.relpath(sciezka, TU).replace("\\", "/"))
    return zle, D, pliki


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            zle, D, _p = aktualny()
            print("dane kowala: %s (skrót %s)" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle), D["skrot"]))
            return 1 if zle else 0
        D, pliki = zapisz()
    except BladDanych as e:
        print("BŁĄD DANYCH:", e)
        return 2
    kz = D["kuznia"]
    print("zapisano: %s (skrót %s)" % (", ".join(os.path.relpath(p, REPO).replace("\\", "/") for p in pliki), D["skrot"]))
    print("  przedmiotów %d (%s), części zbroi %d, blok tarczy ze wzoru %.4f"
          % (len(D["przedmioty"]), ", ".join("%s %d" % (k, len(v["przedmioty"])) for k, v in D["klasy"].items()),
             len(D["czesci"]), D["blokTarczy"]))
    print("  kuźnia: środek %s, E %s, kowal %s (ry %d°), zakres %s; odstępy E: %s"
          % (kz["srodek"], kz["e"], kz["kowal"], kz["kowalRy"], kz["zakres"], kz["odstepyE"]))
    print("  przypadków wzorcowych: %d" % sum(len(v) for v in D["przypadki"].values()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
