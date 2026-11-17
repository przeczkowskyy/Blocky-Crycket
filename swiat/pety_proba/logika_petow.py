# -*- coding: utf-8 -*-
"""Lustro w Pythonie modułu zrodla/LogikaPetow.luau (te same nazwy w snake_case, te same zaokrąglenia i teksty).

Czysta logika petów — bez Roblox: cena jajka (rosnąca z liczbą kupionych), losowanie peta z jawnymi szansami
(r ∈ [0, 1) podaje serwer z Random), teksty szans, skilli i braku Złota, premia peta, wiersze tablicy zagrody,
decyzja serwera przed zakupem. testy/test_petow.py porównuje to lustro z LogikaPetow.luau w interpreterze
tools/walka/luau_mini.py; przypadki wzorcowe (D["przypadki"]) liczy ten plik, a LogikaPetow.sprawdzPrzypadki sprawdza
je w Studio (atrybut kontenera ZgodnoscLogikiPetow).
"""
import math


def pet(D, pid):
    for p in D["pety"]:
        if p["id"] == pid:
            return p
    return None


def jajko(D, jid):
    for j in D["jajka"]:
        if j["id"] == jid:
            return j
    return None


def rzadkosc(D, rid):
    for r in D["rzadkosci"]:
        if r["id"] == rid:
            return r
    return None


def _calkowita_nieujemna(v):
    return (not isinstance(v, bool)) and isinstance(v, (int, float)) and v == v and v >= 0 and math.floor(v) == v


def cena(D, j, kupione):
    """Cena NASTĘPNEGO jajka, gdy gracz kupił już `kupione` takich jajek (licznik wydatków w profilu StanGracza)."""
    c = j["cena"]
    n = kupione if _calkowita_nieujemna(kupione) else 0
    if c["tryb"] == "kalkulator":
        return c["kalkulator"]
    return min(c["maks"], c["start"] + c["krok"] * int(n))


def losuj(D, j, r):
    """r ∈ [0, 1) (Random:NextNumber na serwerze) → id peta z puli jajka; szanse po kolei (pospolity … legendarny)."""
    if isinstance(r, bool) or not isinstance(r, (int, float)) or r != r or r < 0:
        r = 0.0
    suma = 0.0
    for s in j["szanse"]:
        suma += s["szansa"]
        if r < suma:
            return s["pet"]
    return j["szanse"][-1]["pet"]


def procent(szansa):
    """0.5 → „50%”, 0.02 → „2%”, 0.005 → „0,5%”."""
    p = szansa * 100.0
    calk = math.floor(p + 0.5)
    if abs(p - calk) < 1e-9:
        return "%d%%" % calk
    dz = math.floor(p * 10 + 0.5)
    return "%d,%d%%" % (dz // 10, dz % 10)


def opis_skilla(D, p):
    s = p["skill"]
    T = D["teksty"]
    z = int(math.floor(s["zloto"] * 100 + 0.5))
    x = int(math.floor(s["doswiadczenie"] * 100 + 0.5))
    if z > 0 and x > 0 and z == x:
        return T["skill_oba"] % z
    if z > 0 and x > 0:
        return (T["skill_zloto"] % z) + ", " + (T["skill_xp"] % x)
    if z > 0:
        return T["skill_zloto"] % z
    return T["skill_xp"] % x


def premia_peta(D, pid):
    p = pet(D, pid)
    if not p:
        return {"zloto": 0, "doswiadczenie": 0}
    return {"zloto": p["skill"]["zloto"], "doswiadczenie": p["skill"]["doswiadczenie"]}


def tekst_braku(D, brakuje, zloto, c):
    return D["teksty"]["za_malo"] % (brakuje, zloto, c)


def wiersze_szans(D, j):
    """Tablica przy inkubatorze: pet, rzadkość, kolor, szansa tekstem, skill — w kolejności puli."""
    w = []
    for s in j["szanse"]:
        p = pet(D, s["pet"])
        r = rzadkosc(D, p["rzadkosc"])
        w.append({"pet": p["id"], "nazwa": p["nazwa"], "rzadkosc": r["nazwa"], "kolor": r["kolor"],
                  "szansa": procent(s["szansa"]), "skill": opis_skilla(D, p)})
    return w


def wiersze_zagrody(D, kopie, aktywny):
    """Tablica i okno zagrody: posiadane pety w kolejności katalogu, z liczbą kopii (= shardy peta, D-058)."""
    w = []
    for p in D["pety"]:
        n = (kopie or {}).get(p["id"])
        if _calkowita_nieujemna(n) and n > 0:
            r = rzadkosc(D, p["rzadkosc"])
            w.append({"pet": p["id"], "nazwa": p["nazwa"], "rzadkosc": r["nazwa"], "kolor": r["kolor"],
                      "kopie": int(n), "skill": opis_skilla(D, p), "aktywny": p["id"] == aktywny})
    return w


def decyzja(D, stan):
    """Serwer przed zakupem: stan = {stan_gracza (bool), zajety (bool), jajko (id)} → {ok, powod, tekst}."""
    T = D["teksty"]
    if not stan.get("stan_gracza"):
        return {"ok": False, "powod": "brak_stanu", "tekst": T["brak_stanu"]}
    if jajko(D, stan.get("jajko")) is None:
        return {"ok": False, "powod": "nieznane_jajko", "tekst": T["nieznane"]}
    if stan.get("zajety"):
        return {"ok": False, "powod": "trwa_wyklucie", "tekst": T["trwa"]}
    return {"ok": True, "powod": "ok", "tekst": ""}


def czas_wyklucia(D):
    W = D["wyklucie"]
    return W["trzesienie_s"] + W["pekniecie_s"] + W["wyskok_s"] + W["radosc_s"]


# ------------------------------------------------------------------------------------------------ przypadki
def przypadki(D):
    j = D["jajka"][0]
    P = {"cena": [], "losuj": [], "procent": [], "skill": [], "zagroda": [], "decyzja": [], "szanse": []}
    for n in (0, 1, 2, 3, 4, 5, 10, -1, 2.5, None):
        P["cena"].append({"jajko": j["id"], "kupione": n, "wynik": cena(D, j, n)})
    granice = []
    suma = 0.0
    for s in j["szanse"]:
        suma += s["szansa"]
        granice.append(suma)
    for r in [0.0, 0.25, 0.4999, 0.5, 0.74, 0.75, 0.899, 0.9, 0.979, 0.98, 0.999999, -1, None] + granice:
        P["losuj"].append({"jajko": j["id"], "r": r, "wynik": losuj(D, j, r)})
    for s in (0.5, 0.25, 0.15, 0.08, 0.02, 0.005, 0.125, 1.0):
        P["procent"].append({"szansa": s, "wynik": procent(s)})
    for p in D["pety"]:
        P["skill"].append({"pet": p["id"], "wynik": opis_skilla(D, p), "premia": premia_peta(D, p["id"])})
    for kopie, akt in (({}, None), ({"zoledziak": 3, "jelonek_gaju": 1}, "jelonek_gaju"),
                       ({"lisciolis": 2, "zoledziak": 1, "obcy": 5}, "zoledziak"), ({"zoledziak": 0, "lisciolis": -1}, None)):
        P["zagroda"].append({"kopie": kopie, "aktywny": akt, "wynik": wiersze_zagrody(D, kopie, akt)})
    for st in ({"stan_gracza": True, "jajko": j["id"]}, {"stan_gracza": False, "jajko": j["id"]},
               {"stan_gracza": True, "jajko": "jajko_smoka"}, {"stan_gracza": True, "jajko": j["id"], "zajety": True},
               {"stan_gracza": True}):
        P["decyzja"].append({"stan": st, "wynik": decyzja(D, st)})
    P["szanse"].append({"jajko": j["id"], "wynik": wiersze_szans(D, j)})
    return P
