# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaTreningu.luau w Pythonie — ta sama logika mini-gier Training Center (próba), działanie po
działaniu w tej samej kolejności (liczby double, jak w Luau), żeby testy offline i przypadki wzorcowe w
DaneTreningu.luau dawały to samo co serwer w Studio.

Sześć rodzajów mini-gier (gry.<id>.typ w ustawienia.json):
    kierunki  (Siła „Rozbijanie”)     — właściwy kierunek w oknie czasu wokół dolotu skrzynki
    blok      (Pancerz „Blok”)        — blok w oknie czasu przy ciosie; zmyłkę trzeba przeczekać
    rytm      (Kondycja „Bieżnia”)    — lewa i prawa stopa na zmianę, równo z rytmem (bez rozrzutu, podbiegi)
    unik      (Zręczność „Kłody”)     — niska kłoda: skok, wysoka: padnij (odpowiedz: wartość → akcja)
    sekwencja (Inteligencja „Runy”)   — runy świecą po kolei, gracz powtarza; bez okna czasu na runę
    lapanie   (Szczęście „Koniczyny”) — koszyk na jednym z trzech torów; werdykt w chwili upadku

    plan(D, gra, ziarno)            → zdarzenia rundy (czasowe: {nr, t, poziom, okno, wartosc, …}; sekwencja: runy)
    nowa_runda(D, gra, id, t0, plan) → stan rundy (serwer i kopia u klienta)
    zgloszenie(D, R, wartosc, tk, teraz) → werdykt jednego naciśnięcia (ochrona przed spamem, okno czasu)
    przeterminowane(D, R, teraz, zapas) → werdykty zdarzeń, których nikt nie odbił (pudło), zmyłek przeczekanych,
                                       upadków koniczyn i kamieni; w sekwencji: ponowny pokaz po bezczynności
    przyrost(D, seria, G)           → jednostki paska za trafienie przy tej serii (waga mini-gry G)
    wejscie / start / w_arenie / skala_ui / podsumowanie — reszta reguł serwera i UI
    kod_wyniku(w)                   → krótki zapis werdyktu do przypadków wzorcowych ("T3", "p7", "-", "S", "X", "K",
                                       "D", "W" — naciśnięcie w czasie pokazu run, "R" — ruch koszyka)
"""
import math

M = 2147483647.0
NIGDY = -1e9
CZASOWE = ("kierunki", "blok", "rytm", "unik", "lapanie")


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


def odpowiedz(G, wartosc):
    """Akcja, która odbija zdarzenie o tej wartości (Kłody: nisko → skok); bez mapy — ta sama nazwa."""
    o = G.get("odpowiedz")
    if o is not None:
        return o.get(wartosc)
    return wartosc


def _plan_sekwencji(G, s):
    """Runy całej rundy (zapas na długie granie): bez tej samej runy dwa razy z rzędu (podwójnego mignięcia nie widać)."""
    lista = []
    n = len(G["runy"])
    poprzednia = 0
    for nr in range(1, int(G["baza"]) + 1):
        s, u = losuj(s)
        k = 1 + _floor(u * n)
        if k > n:
            k = n
        if k == poprzednia:
            k = _mod(k, n) + 1
        poprzednia = k
        lista.append({"nr": nr, "wartosc": G["runy"][int(k) - 1]})
    return lista


def plan(D, gra, z):
    G = D["gry"][gra]
    Rd = D["runda"]
    s = ziarno(z)
    typ = G["typ"]
    if typ == "sekwencja":
        return _plan_sekwencji(G, s)
    t = float(G.get("pierwsze_s", Rd["pierwsze_s"]))
    koniec = Rd["dlugosc_s"] - Rd["koniec_zapas_s"]
    lista = []
    nr = 0
    podbieg = 0
    while t <= koniec:
        i = poziom(G, t)
        p = G["poziomy"][i - 1]
        nr += 1
        s, u = losuj(s)
        e = {"nr": nr, "t": zaokr(t), "poziom": i, "okno": p.get("okno_s", 0)}
        if typ == "kierunki":
            k = 1 + _floor(u * p["kierunki"])
            if k > p["kierunki"]:
                k = p["kierunki"]
            e["wartosc"] = G["kierunki"][int(k) - 1]
        elif typ == "blok":
            e["wartosc"] = "zmylka" if u < p["zmylki"] else "cios"
        elif typ == "rytm":
            e["wartosc"] = G["kierunki"][0] if _mod(nr, 2) == 1 else G["kierunki"][1]
            if podbieg > 0:
                e["podbieg"] = True
                podbieg -= 1
            elif u < p["podbiegi"]:
                e["podbieg"] = True
                podbieg = G["podbieg"]["kroki"] - 1
        elif typ == "unik":
            k = 1 + _floor(u * p["wartosci"])
            if k > p["wartosci"]:
                k = p["wartosci"]
            e["wartosc"] = G["wartosci"][int(k) - 1]
            s, u = losuj(s)
            if u < p["zmiany"]:
                e["zmiana"] = True
        else:  # lapanie
            if u < p["kamienie"]:
                e["wartosc"] = "kamien"
            else:
                s, u = losuj(s)
                e["wartosc"] = "zlota" if u < p["zlote"] else "koniczyna"
            s, u = losuj(s)
            e["los"] = u
            s, u = losuj(s)
            if e["wartosc"] != "kamien" and u < p["wiatr"]:
                e["wiatr"] = -1 if u < p["wiatr"] / 2 else 1
        lista.append(e)
        s, u = losuj(s)
        baza = p["odstep_s"]
        if typ == "rytm" and podbieg > 0:
            baza = baza * G["podbieg"]["mnoznik"]
        odstep = baza * (1 - G["rozrzut"] + 2 * G["rozrzut"] * u)
        t = t + odstep
    return lista


def przyrost(D, seria, G=None):
    """Jednostki paska za jedno trafienie przy tej serii (× waga mini-gry, gdy podana)."""
    P = D["przyrost"]
    k = 1
    for i in range(1, len(P["progi_serii"]) + 1):
        if seria >= P["progi_serii"][i - 1]:
            k = i + 1
    j = P["za_trafienie"][k - 1] * P["mnoznik_centrum"]
    if G is not None and G.get("waga") is not None:
        j = j * G["waga"]
    return j


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


def punkty_za_serie(D, n, S0=None, G=None, mnozniki=None):
    """n trafień bez pudła od zera serii → (punkty, pasek, W, trafień z punktem) — do testów i próby w Studio."""
    s0 = S0 or {}
    pasek, W, pl = float(s0.get("pasek", 0)), s0.get("W", 0), s0.get("pula", pula(D, 1))
    punkty, z_punktem = 0, 0
    for seria in range(1, n + 1):
        j = przyrost(D, seria, G)
        if mnozniki is not None:
            j = j * mnozniki[seria - 1]
        pasek += j
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


def _kubelek_gry(D, G):
    O = D["ochrona"]
    k = G.get("kubelek")
    if k is not None:
        return k["pojemnosc"], k["uzupelnianie_na_s"]
    return O["pojemnosc"], O["uzupelnianie_na_s"]


def tempo_pokazu(D, R):
    """Tempo pokazu run z poziomu w chwili jego początku: R.swieci i R.krok (świecenie + przerwa)."""
    G = D["gry"][R["gra"]]
    p = G["poziomy"][poziom(G, R["pokazOd"]) - 1]
    R["swieci"] = p["pokaz_s"]
    R["krok"] = p["pokaz_s"] + p["przerwa_s"]
    return p


def _koniec_pokazu(D, R):
    """Koniec pokazu run (od niego wolno wpisywać): dł × świecenie + (dł − 1) × przerwa, tempo z poziomu w chwili pokazu."""
    p = tempo_pokazu(D, R)
    R["pokazDo"] = R["pokazOd"] + R["dl"] * p["pokaz_s"] + (R["dl"] - 1) * p["przerwa_s"]
    R["ostatnia"] = R["pokazDo"]


def nowa_runda(D, gra, id_, t0, plan_, S0=None):
    s0 = S0 or {}
    G = D["gry"][gra]
    poj, _ = _kubelek_gry(D, G)
    R = {"id": id_, "gra": gra, "t0": t0, "plan": plan_, "rozstrzygniete": {}, "nastepny": 1,
         "seria": 0, "najdluzsza": 0, "trafienia": 0, "pudla": 0, "puste": 0, "spam": 0, "odrzucone": 0,
         "suma": 0, "jednostki": 0, "pasek": s0.get("pasek", 0), "W": s0.get("W", 0),
         "pula": s0.get("pula", pula(D, 1)), "tokeny": poj, "ostatnio": t0, "koniec": False}
    if G["typ"] == "sekwencja":
        R.update({"dl": G["start_dlugosc"], "poz": 0, "offset": 0, "licznik": 0, "zaklecia": 0, "najdluzszaSekwencja": 0,
                  "pokazy": 1, "ostatniaRuna": None, "ostatniaRunaT": NIGDY,
                  "pokazOd": float(G.get("pierwsze_s", D["runda"]["pierwsze_s"]))})
        _koniec_pokazu(D, R)
    elif G["typ"] == "lapanie":
        R.update({"ruchy": [], "tory": {}, "zlapane": 0, "kamienie": 0})
    return R


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


def _ocen(D, R, trafienie, mnoznik):
    """Seria, jednostki paska i punkty statystyki za jedno rozstrzygnięcie → (punkty, jednostki, próg po)."""
    G = D["gry"][R["gra"]]
    p, j = 0, 0
    pr = prog(D, R["W"], R["pula"])
    if trafienie:
        R["seria"] += 1
        if R["seria"] > R["najdluzsza"]:
            R["najdluzsza"] = R["seria"]
        R["trafienia"] += 1
        j = przyrost(D, R["seria"], G) * mnoznik
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
    return p, j, pr


def _rozstrzygnij(D, R, e, trafienie, powod, akcja, d, mnoznik=1):
    R["rozstrzygniete"][e["nr"]] = "T" if trafienie else "P"
    p, j, pr = _ocen(D, R, trafienie, mnoznik)
    _przesun(R)
    return {"przyjete": True, "nr": e["nr"], "wartosc": e["wartosc"], "akcja": akcja, "trafienie": trafienie,
            "powod": powod, "seria": R["seria"], "przyrost": p, "jednostki": j, "suma": R["suma"],
            "pasek": R["pasek"], "prog": pr, "d": zaokr(d) if d is not None else None}


def _liczba(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# ------------------------------------------------------------------------------------------------ sekwencja (Runy)
def aktualizuj_sekwencje(D, R, r):
    """Bezczynność w czasie wpisywania (bezczynnosc_s bez naciśnięcia) → ten sam pokaz jeszcze raz, od pierwszej runy,
    bez kary. Chwila nowego pokazu nie zależy od tego, kiedy to zauważono (serwer co tik, klient co klatkę)."""
    G = D["gry"][R["gra"]]
    if R["koniec"] or r < R["pokazDo"]:
        return False
    od = R["ostatnia"] + G["bezczynnosc_s"]
    if r > od and od < D["runda"]["dlugosc_s"]:
        R["pokazOd"] = od
        R["poz"] = 0
        R["pokazy"] += 1
        _koniec_pokazu(D, R)
        return True
    return False


def _zgloszenie_sekwencji(D, R, wartosc, r):
    G = D["gry"][R["gra"]]
    O = D["ochrona"]
    aktualizuj_sekwencje(D, R, r)
    if r < R["pokazDo"]:
        return {"przyjete": False, "powod": "pokaz"}
    if wartosc == R["ostatniaRuna"] and r - R["ostatniaRunaT"] <= O["dubel_s"]:
        return {"przyjete": False, "powod": "dubel"}
    i = R["offset"] + R["poz"] + 1
    oczekiwana = R["plan"][i - 1]["wartosc"] if i <= len(R["plan"]) else None
    R["licznik"] += 1
    nr = R["licznik"]
    R["ostatniaRuna"] = wartosc
    R["ostatniaRunaT"] = r
    trafienie = wartosc == oczekiwana
    p, j, pr = _ocen(D, R, trafienie, 1)
    zaklecie = False
    if trafienie:
        R["poz"] += 1
        if R["poz"] >= R["dl"]:
            zaklecie = True
            R["zaklecia"] += 1
            if R["dl"] > R["najdluzszaSekwencja"]:
                R["najdluzszaSekwencja"] = R["dl"]
            if R["dl"] >= G["maks_dlugosc"]:
                R["offset"] += R["dl"]
                R["dl"] = G["start_dlugosc"]
            else:
                R["dl"] += 1
            R["poz"] = 0
            R["pokazOd"] = r + G["przerwa_s"]
            R["pokazy"] += 1
            _koniec_pokazu(D, R)
        else:
            R["ostatnia"] = r
    else:
        R["dl"] = max(G["min_dlugosc"], R["dl"] - G["kara"])
        R["poz"] = 0
        R["pokazOd"] = r + G["przerwa_bledu_s"]
        R["pokazy"] += 1
        _koniec_pokazu(D, R)
    return {"przyjete": True, "nr": nr, "wartosc": oczekiwana, "akcja": wartosc, "trafienie": trafienie,
            "powod": "trafienie" if trafienie else "zla_runa", "seria": R["seria"], "przyrost": p, "jednostki": j,
            "suma": R["suma"], "pasek": R["pasek"], "prog": pr, "d": None, "zaklecie": zaklecie, "dl": R["dl"],
            "poz": R["poz"], "offset": R["offset"], "pokazOd": R["pokazOd"], "pokazDo": R["pokazDo"],
            "pokazy": R["pokazy"], "ostatnia": R["ostatnia"]}


# ------------------------------------------------------------------------------------------------ łapanie (Koniczyny)
def tor_w(D, R, T):
    """Tor koszyka (1..3) w chwili T (s od t0): ostatni ruch o czasie ≤ T; przed pierwszym ruchem tor startowy."""
    G = D["gry"][R["gra"]]
    b = G["tory"].index(G["start_tor"]) + 1
    najp = NIGDY
    for m in R["ruchy"]:
        if m["t"] <= T and m["t"] >= najp:
            b = m["tor"]
            najp = m["t"]
    return b


def tory_zdarzenia(D, R, e):
    """(tor upadku, tor startu) koniczyny lub kamienia — z toru koszyka w chwili, gdy zaczyna spadać (t − lot):
    kamień celuje w koszyk, koniczyna spada na jeden z DWÓCH pozostałych torów (stanie w miejscu nic nie daje), a gdy
    się da — nie na tor kamienia, który jeszcze leci; przy wietrze zaczyna o tor obok i dryfuje na swój. Liczone raz
    i zapamiętane (te same ruchy → ten sam wynik u klienta i na serwerze)."""
    G = D["gry"][R["gra"]]
    w = R["tory"].get(e["nr"])
    if w is not None:
        return w[0], w[1]
    start = e["t"] - G["lot_s"]
    b = tor_w(D, R, start)
    n = len(G["tory"])
    if e["wartosc"] == "kamien":
        k = b
    else:
        zajete = {}
        for e2 in R["plan"]:
            if e2["nr"] >= e["nr"]:
                break
            if e2["wartosc"] == "kamien" and e2["t"] > start:
                zajete[tory_zdarzenia(D, R, e2)[0]] = True
        wolne = [i for i in range(1, n + 1) if i != b and not zajete.get(i)]
        if not wolne:
            wolne = [i for i in range(1, n + 1) if i != b]
        j = 1 + _floor(e["los"] * len(wolne))
        if j > len(wolne):
            j = len(wolne)
        k = wolne[int(j) - 1]
    z = k
    if e.get("wiatr") is not None:
        z = k + e["wiatr"]
        if z < 1 or z > n:
            z = k - e["wiatr"]
    R["tory"][e["nr"]] = [k, z]
    return k, z


def _zgloszenie_lapania(D, R, wartosc, r):
    G = D["gry"][R["gra"]]
    k = G["tory"].index(wartosc) + 1
    R["ruchy"].append({"t": r, "tor": k})
    return {"przyjete": True, "nr": None, "wartosc": None, "akcja": wartosc, "trafienie": False, "powod": "ruch",
            "ruch": True, "tor": k, "seria": R["seria"], "przyrost": 0, "jednostki": 0, "suma": R["suma"],
            "pasek": R["pasek"], "prog": prog(D, R["W"], R["pula"]), "d": None}


def stal_na_torze(D, R, k, od, do):
    """Czy koszyk był na torze k przez cały odcinek (od, do] — bez ruchu na inny tor (ruch „na ten sam” nie psuje)."""
    if tor_w(D, R, od) != k:
        return False
    for m in R["ruchy"]:
        if od < m["t"] <= do and m["tor"] != k:
            return False
    return True


def _upadek(D, R, e):
    G = D["gry"][R["gra"]]
    k, _ = tory_zdarzenia(D, R, e)
    b = tor_w(D, R, e["t"])
    if e["wartosc"] == "kamien":
        if b == k:
            R["kamienie"] += 1
            w = _rozstrzygnij(D, R, e, False, "kamien", None, None)
        else:
            R["rozstrzygniete"][e["nr"]] = "N"  # kamień obok koszyka — bez werdyktu, seria zostaje
            _przesun(R)
            return None
    elif stal_na_torze(D, R, k, e["t"] - G["zlapanie_s"], e["t"]):
        # koszyk pod koniczyną już chwilę przed upadkiem (wsunięcie w ostatniej chwili się nie liczy — inaczej
        # bezmyślne miotanie koszykiem łapałoby co trzecią koniczynę)
        R["zlapane"] += 1
        w = _rozstrzygnij(D, R, e, True, "zlota" if e["wartosc"] == "zlota" else "zlapana", None, None,
                          G["zlota_mnoznik"] if e["wartosc"] == "zlota" else 1)
    else:
        w = _rozstrzygnij(D, R, e, False, "za_pozno" if b == k else "spadla", None, None)
    w["tor"] = k
    return w


# ------------------------------------------------------------------------------------------------ zgłoszenie
def zgloszenie(D, R, wartosc, tk, teraz):
    O = D["ochrona"]
    G = D["gry"][R["gra"]]
    if R["koniec"]:
        return {"przyjete": False, "powod": "koniec"}
    poj, uzup = _kubelek_gry(D, G)
    if not kubelek(R, teraz, poj, uzup):
        R["spam"] += 1
        return {"przyjete": False, "powod": "spam"}
    if not jest_akcja(G, wartosc):
        R["odrzucone"] += 1
        return {"przyjete": False, "powod": "zla_wartosc"}
    t = teraz
    if _liczba(tk) and tk >= teraz - O["max_opoznienie_s"] and tk <= teraz + O["max_wyprzedzenie_s"]:
        t = float(tk)
    r = t - R["t0"]
    if G["typ"] == "sekwencja":
        return _zgloszenie_sekwencji(D, R, wartosc, r)
    if G["typ"] == "lapanie":
        return _zgloszenie_lapania(D, R, wartosc, r)
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
    if G["typ"] == "blok":
        pasuje = e["wartosc"] == "cios"
    else:
        pasuje = wartosc == odpowiedz(G, e["wartosc"])
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


def przeterminowane(D, R, teraz, zapas=None):
    """Zdarzenia po czasie: pudła (przepuszczone), przeczekane zmyłki, upadki (Koniczyny) i koniec rundy.
    zapas = ile czekać po oknie na spóźnione wiadomości (domyślnie max_opoznienie_s; klient w Koniczynach: 0)."""
    O = D["ochrona"]
    G = D["gry"][R["gra"]]
    if zapas is None:
        zapas = O["max_opoznienie_s"]
    r = teraz - R["t0"]
    lista = []
    if G["typ"] == "sekwencja":
        aktualizuj_sekwencje(D, R, r)
        if not R["koniec"] and r > D["runda"]["dlugosc_s"] + O["max_opoznienie_s"]:
            R["koniec"] = True
        return lista
    n = len(R["plan"])
    i = R["nastepny"]
    while i <= n:
        e = R["plan"][i - 1]
        if e["nr"] not in R["rozstrzygniete"]:
            if r > e["t"] + e["okno"] + zapas:
                if G["typ"] == "lapanie":
                    w = _upadek(D, R, e)
                    if w is not None:
                        lista.append(w)
                elif e["wartosc"] == "zmylka":
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
    G = D["gry"][R["gra"]]
    n = len(R["plan"])
    if G["typ"] == "sekwencja":
        n = R["trafienia"] + R["pudla"]
    p = {"gra": R["gra"], "n": n, "trafienia": R["trafienia"], "pudla": R["pudla"],
         "puste": R["puste"], "spam": R["spam"], "najdluzsza": R["najdluzsza"], "suma": R["suma"],
         "jednostki": R["jednostki"], "pasek": R["pasek"], "W": R["W"], "pula": R["pula"],
         "prog": prog(D, R["W"], R["pula"]), "celnosc": _floor(100 * R["trafienia"] / max(1, proby) + 0.5)}
    if G["typ"] == "sekwencja":
        p["zaklecia"] = R["zaklecia"]
        p["najdluzszaSekwencja"] = R["najdluzszaSekwencja"]
    elif G["typ"] == "lapanie":
        p["zlapane"] = R["zlapane"]
        p["kamienie"] = R["kamienie"]
    return p


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
        return {"spam": "S", "zla_wartosc": "X", "koniec": "K", "dubel": "D", "pokaz": "W"}.get(w["powod"], "?")
    if w.get("ruch"):
        return "R"
    if w["nr"] is None:
        return "-"
    litera = "T" if w["trafienie"] else "P"
    if wygasly:
        litera = litera.lower()
    return "%s%d" % (litera, w["nr"])


def wykonaj_kroki(D, gra, z, t0, kroki, S0=None):
    """Przebieg sekwencji kroków (jak L.sprawdzPrzypadki w Luau) → (zapis, stan rundy).
    Krok: {"typ": "z", "w", "tk", "teraz"} zgłoszenie; {"typ": "p", "teraz", "zapas"?} przeterminowane."""
    R = nowa_runda(D, gra, 1, t0, plan(D, gra, z), S0)
    kody = []
    for k in kroki:
        if k["typ"] == "z":
            kody.append(kod_wyniku(zgloszenie(D, R, k.get("w"), k.get("tk"), k["teraz"])))
        else:
            for w in przeterminowane(D, R, k["teraz"], k.get("zapas")):
                kody.append(kod_wyniku(w, True))
    return ",".join(kody), R
