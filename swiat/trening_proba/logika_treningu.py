# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaTreningu.luau w Pythonie — ta sama logika mini-gier Training Center (próba), działanie po
działaniu w tej samej kolejności (liczby double, jak w Luau), żeby testy offline i przypadki wzorcowe w
DaneTreningu.luau dawały to samo co serwer w Studio.

    plan(D, gra, ziarno)            → lista zdarzeń rundy {nr, t, poziom, okno, wartosc} (t od startu rundy, s)
    nowa_runda(D, gra, id, t0, plan) → stan rundy (serwer i kopia u klienta)
    zgloszenie(D, R, wartosc, tk, teraz) → werdykt jednego naciśnięcia (ochrona przed spamem, okno czasu)
    przeterminowane(D, R, teraz)    → werdykty zdarzeń, których nikt nie odbił (pudło) i zmyłek przeczekanych
    przyrost(D, seria)              → ile punktów statystyki daje trafienie przy tej serii
    wejscie / start / w_arenie / skala_ui / podsumowanie — reszta reguł serwera i UI
    kod_wyniku(w)                   → krótki zapis werdyktu do przypadków wzorcowych ("T3", "p7", "-", "S", "X", "K")
"""
import math

M = 2147483647.0
NIGDY = -1e9


def _floor(x):
    return float(math.floor(x))


def _mod(a, b):
    return a - _floor(a / b) * b


def ziarno(z):
    s = _mod(_floor(abs(float(z))), M - 1)
    return s + 1


def ziarno_z_czasu(t, licznik):
    return ziarno(t * 1000 + licznik)


def losuj(s):
    s = _mod(48271.0 * s, M)
    return s, (s - 1) / (M - 1)


def zaokr(x):
    return _floor(x * 1000 + 0.5) / 1000


def poziom(G, t):
    n = len(G["poziomy"])
    for i in range(n, 0, -1):
        if t >= G["poziomy"][i - 1]["od_s"]:
            return i
    return 1


def plan(D, gra, z):
    G = D["gry"][gra]
    Rd = D["runda"]
    s = ziarno(z)
    t = float(Rd["pierwsze_s"])
    koniec = Rd["dlugosc_s"] - Rd["koniec_zapas_s"]
    lista = []
    nr = 0
    while t <= koniec:
        i = poziom(G, t)
        p = G["poziomy"][i - 1]
        nr += 1
        s, u = losuj(s)
        e = {"nr": nr, "t": zaokr(t), "poziom": i, "okno": p["okno_s"]}
        if G["typ"] == "kierunki":
            k = 1 + _floor(u * p["kierunki"])
            if k > p["kierunki"]:
                k = p["kierunki"]
            e["wartosc"] = G["kierunki"][int(k) - 1]
        else:
            e["wartosc"] = "zmylka" if u < p["zmylki"] else "cios"
        lista.append(e)
        s, u = losuj(s)
        odstep = p["odstep_s"] * (1 - G["rozrzut"] + 2 * G["rozrzut"] * u)
        t = t + odstep
    return lista


def przyrost(D, seria):
    """Jednostki paska za jedno trafienie przy tej serii."""
    P = D["przyrost"]
    k = 1
    for i in range(1, len(P["progi_serii"]) + 1):
        if seria >= P["progi_serii"][i - 1]:
            k = i + 1
    return P["za_trafienie"][k - 1] * P["mnoznik_centrum"]


def pula(D, poziom):
    P = D["przyrost"]
    lv = _floor(poziom) if _liczba(poziom) and poziom >= 1 else 1
    return P["pula_baza"] + P["pula_na_poziom"] * (lv - 1)


def prog(D, W, pula_):
    P = D["przyrost"]
    if not P["malejacy_zysk"]:
        return P["prog_paska"]
    q = 1 + W / (P["polowa_udzialu"] * pula_)
    return P["prog_paska"] * q * q


def punkty_za_serie(D, n, S0=None):
    """n trafień bez pudła od zera serii → (punkty, pasek, W, trafień z punktem) — do testów i próby w Studio."""
    s0 = S0 or {}
    pasek, W, pl = float(s0.get("pasek", 0)), s0.get("W", 0), s0.get("pula", pula(D, 1))
    punkty, z_punktem = 0, 0
    for seria in range(1, n + 1):
        pasek += przyrost(D, seria)
        p = 0
        pr = prog(D, W, pl)
        while pasek >= pr:
            pasek -= pr
            W += 1
            p += 1
            pr = prog(D, W, pl)
        punkty += p
        z_punktem += p > 0
    return punkty, pasek, W, z_punktem


def kubelek(K, teraz, poj, uzup):
    K["tokeny"] = min(poj, K["tokeny"] + max(0.0, teraz - K["ostatnio"]) * uzup)
    K["ostatnio"] = max(K["ostatnio"], teraz)
    if K["tokeny"] < 1:
        return False
    K["tokeny"] = K["tokeny"] - 1
    return True


def nowy_kubelek(poj, teraz):
    return {"tokeny": poj, "ostatnio": teraz}


def nowa_runda(D, gra, id_, t0, plan_, S0=None):
    O = D["ochrona"]
    s0 = S0 or {}
    return {"id": id_, "gra": gra, "t0": t0, "plan": plan_, "rozstrzygniete": {}, "nastepny": 1,
            "seria": 0, "najdluzsza": 0, "trafienia": 0, "pudla": 0, "puste": 0, "spam": 0, "odrzucone": 0,
            "suma": 0, "jednostki": 0, "pasek": s0.get("pasek", 0), "W": s0.get("W", 0),
            "pula": s0.get("pula", pula(D, 1)), "tokeny": O["pojemnosc"], "ostatnio": t0, "koniec": False}


def jest_akcja(G, wartosc):
    return isinstance(wartosc, str) and wartosc in G["akcje"]


def _przesun(R):
    n = len(R["plan"])
    while R["nastepny"] <= n and R["plan"][R["nastepny"] - 1]["nr"] in R["rozstrzygniete"]:
        R["nastepny"] += 1


def _najblizsze(R, r, zasieg):
    najlepsze, odl = None, None
    for i in range(R["nastepny"], len(R["plan"]) + 1):
        e = R["plan"][i - 1]
        if e["t"] - r > zasieg:
            break
        if e["nr"] not in R["rozstrzygniete"]:
            dd = abs(r - e["t"])
            if dd <= zasieg and (odl is None or dd < odl):
                najlepsze, odl = e, dd
    return najlepsze


def _dubel(R, r, zasieg):
    """Drugie naciśnięcie tuż po rozstrzygniętym zdarzeniu (np. podwójne kliknięcie) — pomijane, bez kary."""
    for e in R["plan"]:
        if e["t"] - r > zasieg:
            break
        if e["nr"] in R["rozstrzygniete"] and abs(r - e["t"]) <= zasieg:
            return True
    return False


def _rozstrzygnij(D, R, e, trafienie, powod, akcja, d):
    R["rozstrzygniete"][e["nr"]] = "T" if trafienie else "P"
    p, j = 0, 0
    pr = prog(D, R["W"], R["pula"])
    if trafienie:
        R["seria"] += 1
        if R["seria"] > R["najdluzsza"]:
            R["najdluzsza"] = R["seria"]
        R["trafienia"] += 1
        j = przyrost(D, R["seria"])
        R["jednostki"] += j
        R["pasek"] += j
        while R["pasek"] >= pr:
            R["pasek"] -= pr
            R["W"] += 1
            p += 1
            pr = prog(D, R["W"], R["pula"])
        R["suma"] += p
    else:
        R["seria"] = 0
        R["pudla"] += 1
    _przesun(R)
    return {"przyjete": True, "nr": e["nr"], "wartosc": e["wartosc"], "akcja": akcja, "trafienie": trafienie,
            "powod": powod, "seria": R["seria"], "przyrost": p, "jednostki": j, "suma": R["suma"],
            "pasek": R["pasek"], "prog": pr, "d": zaokr(d) if d is not None else None}


def _liczba(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def zgloszenie(D, R, wartosc, tk, teraz):
    O = D["ochrona"]
    G = D["gry"][R["gra"]]
    if R["koniec"]:
        return {"przyjete": False, "powod": "koniec"}
    if not kubelek(R, teraz, O["pojemnosc"], O["uzupelnianie_na_s"]):
        R["spam"] += 1
        return {"przyjete": False, "powod": "spam"}
    if not jest_akcja(G, wartosc):
        R["odrzucone"] += 1
        return {"przyjete": False, "powod": "zla_wartosc"}
    t = teraz
    if _liczba(tk) and tk >= teraz - O["max_opoznienie_s"] and tk <= teraz + O["max_wyprzedzenie_s"]:
        t = float(tk)
    r = t - R["t0"]
    e = _najblizsze(R, r, O["przypisanie_s"])
    if e is None and _dubel(R, r, O["dubel_s"]):
        return {"przyjete": False, "powod": "dubel"}
    if e is None:
        R["seria"] = 0
        R["puste"] += 1
        return {"przyjete": True, "nr": None, "wartosc": None, "akcja": wartosc, "trafienie": False, "powod": "pusty",
                "seria": 0, "przyrost": 0, "jednostki": 0, "suma": R["suma"], "pasek": R["pasek"],
                "prog": prog(D, R["W"], R["pula"]), "d": None}
    d = r - e["t"]
    if G["typ"] == "kierunki":
        pasuje = wartosc == e["wartosc"]
    else:
        pasuje = e["wartosc"] == "cios"
    if abs(d) <= e["okno"] and pasuje:
        return _rozstrzygnij(D, R, e, True, "trafienie", wartosc, d)
    if G["typ"] == "blok" and e["wartosc"] == "zmylka":
        powod = "zmylka"
    elif d < -e["okno"]:
        powod = "za_wczesnie"
    elif d > e["okno"]:
        powod = "za_pozno"
    else:
        powod = "zly_kierunek"
    return _rozstrzygnij(D, R, e, False, powod, wartosc, d)


def przeterminowane(D, R, teraz):
    O = D["ochrona"]
    r = teraz - R["t0"]
    lista = []
    n = len(R["plan"])
    i = R["nastepny"]
    while i <= n:
        e = R["plan"][i - 1]
        if e["nr"] not in R["rozstrzygniete"]:
            if r > e["t"] + e["okno"] + O["max_opoznienie_s"]:
                if e["wartosc"] == "zmylka":
                    lista.append(_rozstrzygnij(D, R, e, True, "przetrwana_zmylka", None, None))
                else:
                    lista.append(_rozstrzygnij(D, R, e, False, "przepuszczone", None, None))
            else:
                break
        i += 1
    _przesun(R)
    if not R["koniec"] and R["nastepny"] > n and r > D["runda"]["dlugosc_s"] + O["max_opoznienie_s"]:
        R["koniec"] = True
    return lista


def podsumowanie(D, R):
    proby = R["trafienia"] + R["pudla"] + R["puste"]
    return {"gra": R["gra"], "n": len(R["plan"]), "trafienia": R["trafienia"], "pudla": R["pudla"],
            "puste": R["puste"], "spam": R["spam"], "najdluzsza": R["najdluzsza"], "suma": R["suma"],
            "jednostki": R["jednostki"], "pasek": R["pasek"], "W": R["W"], "pula": R["pula"],
            "prog": prog(D, R["W"], R["pula"]), "celnosc": _floor(100 * R["trafienia"] / max(1, proby) + 0.5)}


def statystyka(D, id_):
    for s in D["statystyki"]:
        if s["id"] == id_:
            return s
    return None


def nowy_gracz():
    return {"gra": None, "ostatnieWejscie": NIGDY, "ostatniStart": NIGDY, "runda": None}


def wejscie(D, gra, S, teraz, odleglosc, w_arenie):
    O = D["ochrona"]
    if teraz - S["ostatnieWejscie"] < O["odstep_wejsc_s"]:
        return {"ok": False, "powod": "za_szybko"}
    st = statystyka(D, gra) if isinstance(gra, str) else None
    if st is None:
        return {"ok": False, "powod": "nieznana"}
    if st["stan"] != "grywalna" or gra not in D["gry"]:
        return {"ok": False, "powod": "w_projekcie"}
    if S["runda"] is not None and not S["runda"]["koniec"]:
        return {"ok": False, "powod": "trwa_runda"}
    if not w_arenie and (odleglosc is None or odleglosc > O["zasieg_wejscia"]):
        return {"ok": False, "powod": "za_daleko"}
    S["ostatnieWejscie"] = teraz
    return {"ok": True, "powod": "ok"}


def start(D, S, teraz):
    O = D["ochrona"]
    if S["gra"] is None:
        return {"ok": False, "powod": "brak_gry"}
    if S["runda"] is not None and not S["runda"]["koniec"]:
        return {"ok": False, "powod": "trwa_runda"}
    if teraz - S["ostatniStart"] < O["odstep_startu_s"]:
        return {"ok": False, "powod": "za_szybko"}
    S["ostatniStart"] = teraz
    return {"ok": True, "powod": "ok"}


def w_arenie(D, x, y, z):
    A = D["arena"]
    c = A["srodek"]
    if abs(x - c[0]) > A["rozmiar"][0] / 2 + A["zapas_wArenie"]:
        return False
    if abs(z - c[2]) > A["rozmiar"][1] / 2 + A["zapas_wArenie"]:
        return False
    dy = y - c[1]
    return dy >= A["wysokosc_wArenie"][0] and dy <= A["wysokosc_wArenie"][1]


def skala_ui(D, w, h):
    U = D["ui"]
    s = min(w / U["baza"][0], h / U["baza"][1])
    if s < U["skala_min"]:
        s = U["skala_min"]
    if s > U["skala_max"]:
        s = U["skala_max"]
    return s


def kod_wyniku(w, wygasly=False):
    if not w["przyjete"]:
        return {"spam": "S", "zla_wartosc": "X", "koniec": "K", "dubel": "D"}.get(w["powod"], "?")
    if w["nr"] is None:
        return "-"
    litera = "T" if w["trafienie"] else "P"
    if wygasly:
        litera = litera.lower()
    return "%s%d" % (litera, w["nr"])


def wykonaj_kroki(D, gra, z, t0, kroki, S0=None):
    """Przebieg sekwencji kroków (jak L.sprawdzPrzypadki w Luau) → (zapis, stan rundy)."""
    R = nowa_runda(D, gra, 1, t0, plan(D, gra, z), S0)
    kody = []
    for k in kroki:
        if k["typ"] == "z":
            kody.append(kod_wyniku(zgloszenie(D, R, k.get("w"), k.get("tk"), k["teraz"])))
        else:
            for w in przeterminowane(D, R, k["teraz"]):
                kody.append(kod_wyniku(w, True))
    return ",".join(kody), R
