# -*- coding: utf-8 -*-
"""Lustro zrodla/LogikaBazaru.luau w Pythonie — te same funkcje, ta sama kolejność działań (testy bez Studio).

Funkcje (nazwy Luau w nawiasie):
  nowy_stan (nowyStan)                 — stan gracza na serwerze: ostatnie E, ostatnie przejście, w trakcie, lochy
  decyzja (decyzja)                    — co zrobić po E w miejscu: okno / dymek / chmury / las / przenies / nic
  lochy_otwarte (lochyOtwarte)         — D-042: osobno dla gracza (flaga albo wymagany poziom, gdy ustalony)
  tekst_odmowy (tekstOdmowy)           — czytelna odmowa (za_szybko z liczbą sekund, powody uchwytu Lasu)
  poczatek_przejscia / koniec_przejscia (poczatekPrzejscia / koniecPrzejscia) — blokada czasu przejść
  ranking (ranking), wiersz (wiersz), liczba (liczba) — tablica z rankingiem serwera
  kandydaci (kandydaci), odl_od_odcinka (odlegloscOdOdcinka) — kolejność miejsc na „Nowe miasteczko (E)”
  rowne (rowne)                        — porównanie wyników (liczby z tolerancją 1e-6)
  przypadki(D)                         — przypadki wzorcowe (wejście + wynik z tego lustra) → DaneBazaru.przypadki;
                                         Luau sprawdza je w L.sprawdzPrzypadki (serwer przy starcie, test w luau_mini)

Słowniki odpowiadają tabelom Luau: brak klucza = nil (wyniki nie mają wartości None).
"""
import copy
import math

NIGDY = -1e9  # „dawno temu” (nie -inf: przypadki przechodzą przez JSON)


def nowy_stan():
    return {"ostatnieE": NIGDY, "ostatniePrzejscie": NIGDY, "wTrakcie": False, "lochy": False}


def _liczba_luau(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def lochy_otwarte(D, s, poziom):
    if s.get("lochy") is True:
        return True
    wym = D["lochy"].get("wymagany_poziom")
    return wym is not None and _liczba_luau(poziom) and poziom >= wym


def tekst_odmowy(D, powod, zostalo=None):
    t = D["teksty"].get(powod) or D["teksty"]["blad"]
    if powod == "za_szybko":
        return t % max(1, math.ceil(zostalo or 0))
    return t


def decyzja(D, mid, s, teraz, swiat):
    """Mutuje s["ostatnieE"] (tak jak Luau). Zwraca słownik akcji."""
    m = D["miejsca"].get(mid)
    if m is None:
        return {"akcja": "nic", "powod": "nieznane_miejsce"}
    odl = swiat.get("odleglosc")
    if odl is not None and odl > m["zasieg"] + D["podpowiedz"]["zapas"]:
        return {"akcja": "nic", "powod": "za_daleko"}
    if teraz - s["ostatnieE"] < D["czasy"]["odstep_e_s"]:
        return {"akcja": "nic", "powod": "spam"}
    s["ostatnieE"] = teraz
    a = m["akcja"]
    if a == "okno":
        return {"akcja": "okno", "id": mid}
    if a == "lochy":
        if lochy_otwarte(D, s, swiat.get("poziom")):
            return {"akcja": "okno", "id": mid}
        return {"akcja": "dymek", "id": mid, "tekst": m["dymek"], "powod": "zamkniete"}
    if a == "chmury":
        if not swiat.get("chmury"):
            return {"akcja": "dymek", "id": mid, "tekst": m["dymek"], "powod": "brak_chmur"}
        return {"akcja": "chmury", "id": mid}
    if a in ("las", "przenies"):
        if s["wTrakcie"]:
            return {"akcja": "dymek", "id": mid, "tekst": tekst_odmowy(D, "trwa"), "powod": "trwa"}
        zostalo = s["ostatniePrzejscie"] + D["czasy"]["odstep_przejsc_s"] - teraz
        if zostalo > 0:
            return {"akcja": "dymek", "id": mid, "tekst": tekst_odmowy(D, "za_szybko", zostalo), "powod": "za_szybko"}
        if a == "las" and not swiat.get("las"):
            return {"akcja": "dymek", "id": mid, "tekst": tekst_odmowy(D, "brak_lasu"), "powod": "brak_lasu"}
        if a == "przenies" and not swiat.get("cel"):
            return {"akcja": "dymek", "id": mid, "tekst": tekst_odmowy(D, "brak_celu"), "powod": "brak_celu"}
        w = {"akcja": a, "id": mid}
        if a == "przenies":
            w["cel"] = m["cel"]
        return w
    return {"akcja": "nic", "powod": "nieznana_akcja"}


def poczatek_przejscia(s):
    s["wTrakcie"] = True


def koniec_przejscia(s, ok, teraz):
    s["wTrakcie"] = False
    if ok:
        s["ostatniePrzejscie"] = teraz


# ------------------------------------------------------------------------------------------------ dymek okna
def przytnij(t):
    return t.strip(" ")


def na_liscie(lista, mid):
    if not isinstance(lista, str) or not isinstance(mid, str):
        return False
    return any(przytnij(x) == mid for x in lista.split(","))


def dymek_okna(mid, otwarto, zgloszone, wylaczone, bez):
    if otwarto or zgloszone is True or wylaczone is True:
        return False
    return not na_liscie(bez, mid)


# ------------------------------------------------------------------------------------------------ ranking
def _przed(a, b):
    pa = a["poziom"] if a.get("poziom") is not None else -1
    pb = b["poziom"] if b.get("poziom") is not None else -1
    if pa != pb:
        return pa > pb
    xa = a["xp"] if a.get("xp") is not None else 0
    xb = b["xp"] if b.get("xp") is not None else 0
    if xa != xb:
        return xa > xb
    ma = a["moc"] if a.get("moc") is not None else 0
    mb = b["moc"] if b.get("moc") is not None else 0
    if ma != mb:
        return ma > mb
    return a["nazwa"] < b["nazwa"]


def ranking(gracze, n):
    t = list(gracze)
    for i in range(1, len(t)):
        v = t[i]
        j = i - 1
        while j >= 0 and _przed(v, t[j]):
            t[j + 1] = t[j]
            j -= 1
        t[j + 1] = v
    wynik = []
    for i, g in enumerate(t[:int(n)]):
        w = {"miejsce": i + 1, "nazwa": g["nazwa"]}
        for k in ("poziom", "xp", "moc"):
            if g.get(k) is not None:
                w[k] = g[k]
        wynik.append(w)
    return wynik


def liczba(x):
    if x is None:
        return "—"
    if float(x) == math.floor(x):
        return "%d" % x
    return "%.1f" % x


def wiersz(w):
    return "%d. %s — poz. %s · moc %s" % (w["miejsce"], w["nazwa"], liczba(w.get("poziom")), liczba(w.get("moc")))


# ------------------------------------------------------------------------------------------------ stare miasteczko
def odl_od_odcinka(px, pz, ax, az, bx, bz):
    dx, dz = bx - ax, bz - az
    l2 = dx * dx + dz * dz
    if l2 <= 1e-12:
        return math.sqrt((px - ax) * (px - ax) + (pz - az) * (pz - az))
    t = ((px - ax) * dx + (pz - az) * dz) / l2
    t = max(0.0, min(1.0, t))
    qx, qz = ax + t * dx, az + t * dz
    return math.sqrt((px - qx) * (px - qx) + (pz - qz) * (pz - qz))


def kandydaci(D, spawn, portal):
    """Kolejne miejsca na „Nowe miasteczko (E)” wokół startu starego miasteczka (pierwsze wolne wybiera Studio)."""
    S = D["stare"]
    wynik = []
    for r in S["promienie"]:
        for k in S["kierunki"]:
            x = spawn["x"] + k[0] * r
            z = spawn["z"] + k[1] * r
            if portal is not None:
                dx, dz = x - portal["x"], z - portal["z"]
                if math.sqrt(dx * dx + dz * dz) < S["min_od_portalu"]:
                    continue
                if odl_od_odcinka(x, z, spawn["x"], spawn["z"], portal["x"], portal["z"]) < S["min_od_odcinka"]:
                    continue
            wynik.append({"x": x, "z": z})
    return wynik


# ------------------------------------------------------------------------------------------------ porównanie
def rowne(a, b):
    if _liczba_luau(a) and _liczba_luau(b):
        return abs(a - b) <= 1e-6
    if type(a) is not type(b):
        if isinstance(a, (list, dict)) and isinstance(b, (list, dict)) and not a and not b:
            return True
        return False
    if isinstance(a, dict):
        return set(a) == set(b) and all(rowne(a[k], b[k]) for k in a)
    if isinstance(a, list):
        return len(a) == len(b) and all(rowne(x, y) for x, y in zip(a, b))
    return a == b


# ------------------------------------------------------------------------------------------------ przypadki wzorcowe
def _swiat(**kw):
    w = {"odleglosc": 5, "chmury": True, "las": True, "poziom": 1, "cel": True}
    for k, v in kw.items():
        if v is None:
            w.pop(k, None)
        else:
            w[k] = v
    return w


def _przypadek_decyzji(D, opis, mid, stan, teraz, swiat):
    s = copy.deepcopy(stan)
    w = decyzja(D, mid, s, teraz, swiat)
    return {"f": "decyzja", "opis": opis, "id": mid, "stan": copy.deepcopy(stan), "teraz": teraz, "swiat": swiat,
            "wynik": w, "stan_po": s}


def _sekwencja(D, opis, kroki):
    s = nowy_stan()
    wyniki = []
    for k in kroki:
        if k["typ"] == "e":
            wyniki.append(decyzja(D, k["id"], s, k["teraz"], k["swiat"]))
        elif k["typ"] == "poczatek":
            poczatek_przejscia(s)
            wyniki.append({"krok": "poczatek"})
        else:
            koniec_przejscia(s, k["ok"], k["teraz"])
            wyniki.append({"krok": "koniec"})
    return {"f": "sekwencja", "opis": opis, "kroki": kroki, "wynik": wyniki, "stan_po": s}


def przypadki(D):
    P = []
    n = nowy_stan()
    zasieg = D["podpowiedz"]["zapas"]
    # 1. każde miejsce z pełnym światem
    for mid in D["kolejnosc"]:
        P.append(_przypadek_decyzji(D, "E: %s" % mid, mid, n, 10.0, _swiat()))
    # 2. odległość, spam, nieznane
    for mid in ("zbrojownia", "brama_lesna"):
        z = D["miejsca"][mid]["zasieg"] + zasieg
        P.append(_przypadek_decyzji(D, "%s: za daleko" % mid, mid, n, 10.0, _swiat(odleglosc=z + 0.5)))
        P.append(_przypadek_decyzji(D, "%s: na granicy zasięgu" % mid, mid, n, 10.0, _swiat(odleglosc=z)))
    s = nowy_stan()
    s["ostatnieE"] = 9.8
    P.append(_przypadek_decyzji(D, "spam E", "karczma", s, 10.0, _swiat()))
    s = nowy_stan()
    s["ostatnieE"] = 9.6
    P.append(_przypadek_decyzji(D, "E po odstępie", "karczma", s, 10.0, _swiat()))
    P.append(_przypadek_decyzji(D, "nieznane miejsce", "nie_ma_takiego", n, 10.0, _swiat()))
    P.append(_przypadek_decyzji(D, "bez odległości (haczyk)", "sklep_magiczny", n, 10.0, _swiat(odleglosc=None)))
    # 3. lochy
    s = nowy_stan()
    s["lochy"] = True
    P.append(_przypadek_decyzji(D, "lochy otwarte (flaga)", "lochy", s, 10.0, _swiat()))
    P.append(_przypadek_decyzji(D, "lochy zamknięte (poziom 99, brak progu)", "lochy", n, 10.0, _swiat(poziom=99)))
    # 4. chmury, las, przejścia
    P.append(_przypadek_decyzji(D, "portal bez chmur", "portal_krain", n, 10.0, _swiat(chmury=False)))
    P.append(_przypadek_decyzji(D, "Brama Leśna bez Lasu", "brama_lesna", n, 10.0, _swiat(las=False)))
    s = nowy_stan()
    s["wTrakcie"] = True
    P.append(_przypadek_decyzji(D, "Brama Leśna w trakcie", "brama_lesna", s, 10.0, _swiat()))
    for teraz, zostalo in ((10.0, 1.5), (11.4, 0.1), (8.6, 2.9), (10.0, 0.0)):
        s = nowy_stan()
        s["ostatniePrzejscie"] = teraz - D["czasy"]["odstep_przejsc_s"] + zostalo
        P.append(_przypadek_decyzji(D, "stare miasteczko: blokada, zostało %.1f s" % zostalo, "stare_miasteczko", s,
                                    teraz, _swiat()))
    P.append(_przypadek_decyzji(D, "nowe miasteczko bez celu", "nowe_miasteczko", n, 10.0, _swiat(cel=False)))
    # 5. sekwencja: E → w trakcie → koniec → za szybko → znowu wolno
    sw = _swiat()
    P.append(_sekwencja(D, "sekwencja Brama Leśna", [
        {"typ": "e", "id": "brama_lesna", "teraz": 0.0, "swiat": sw},
        {"typ": "poczatek"},
        {"typ": "e", "id": "brama_lesna", "teraz": 0.5, "swiat": sw},
        {"typ": "koniec", "ok": True, "teraz": 1.0},
        {"typ": "e", "id": "stare_miasteczko", "teraz": 1.5, "swiat": sw},
        {"typ": "e", "id": "zbrojownia", "teraz": 2.0, "swiat": sw},
        {"typ": "e", "id": "nowe_miasteczko", "teraz": 4.1, "swiat": sw},
        {"typ": "poczatek"},
        {"typ": "koniec", "ok": False, "teraz": 4.5},
        {"typ": "e", "id": "nowe_miasteczko", "teraz": 5.0, "swiat": sw},
    ]))
    # 6. teksty odmów
    for powod in sorted(D["teksty"]) + ["nieznany_powod"]:
        P.append({"f": "tekst", "opis": "tekst %s" % powod, "powod": powod, "zostalo": 2.2,
                  "wynik": tekst_odmowy(D, powod, 2.2)})
    # 7. ranking i wiersze
    gracze = [
        {"nazwa": "Bartek", "poziom": 3, "xp": 40, "moc": 130},
        {"nazwa": "Ala", "poziom": 3, "xp": 40, "moc": 130},
        {"nazwa": "Zenek", "poziom": 7, "xp": 0, "moc": 90},
        {"nazwa": "Cyryl", "poziom": 3, "xp": 55, "moc": 10},
        {"nazwa": "Duch"},
        {"nazwa": "Ewa", "poziom": 3, "xp": 40, "moc": 131.5},
        {"nazwa": "Franek", "poziom": 0, "xp": 0},
    ]
    for liczba_wierszy in (8, 3, 0):
        P.append({"f": "ranking", "opis": "ranking n=%d" % liczba_wierszy, "gracze": gracze, "n": liczba_wierszy,
                  "wynik": ranking(gracze, liczba_wierszy)})
    P.append({"f": "ranking", "opis": "ranking pusty", "gracze": [], "n": 8, "wynik": []})
    for w in ranking(gracze, 8):
        P.append({"f": "wiersz", "opis": "wiersz %d" % w["miejsce"], "w": w, "wynik": wiersz(w)})
    # 8. kandydaci na „Nowe miasteczko (E)”
    sp = {"x": D["stare"]["znacznik"][0], "z": D["stare"]["znacznik"][2]}
    for opis, portal in (("bez portalu", None), ("portal na +z 16", {"x": sp["x"], "z": sp["z"] + 16}),
                         ("portal na −x 20", {"x": sp["x"] - 20, "z": sp["z"] + 2})):
        P.append({"f": "kandydaci", "opis": "kandydaci %s" % opis, "spawn": sp, "portal": portal,
                  "wynik": kandydaci(D, sp, portal)})
    for c in ((0, 0, 0, 0, 10, 0), (5, 3, 0, 0, 10, 0), (-4, 3, 0, 0, 10, 0), (14, -3, 0, 0, 10, 0), (2, 2, 1, 1, 1, 1)):
        P.append({"f": "odcinek", "opis": "odcinek %s" % (c,), "argi": list(c), "wynik": odl_od_odcinka(*c)})
    # 9. dymek „okno w budowie” (klient)
    for opis, otwarto, zgloszone, wylaczone, bez in (
            ("nic się nie otworzyło", False, None, None, None),
            ("okno się otworzyło", "EquipmentPanel", None, None, None),
            ("okno zgłoszone atrybutem", False, True, None, None),
            ("dymki wyłączone", False, None, True, None),
            ("na liście BezDymku", False, None, None, "karczma, zbrojownia"),
            ("nie na liście BezDymku", False, None, None, "karczma,mistrz_gier"),
            ("pusta lista BezDymku", False, None, None, ""),
            ("lista z przecinkiem na końcu", False, None, None, "zbrojownia,")):
        p = {"f": "dymek", "opis": "dymek: %s" % opis, "id": "zbrojownia", "otwarto": otwarto, "zgloszone": zgloszone,
             "wylaczone": wylaczone, "bez": bez, "wynik": dymek_okna("zbrojownia", otwarto, zgloszone, wylaczone, bez)}
        P.append(p)
    # bez None w przypadkach (nil w Luau = brak klucza)
    for p in P:
        for k in [k for k, v in p.items() if v is None]:
            p.pop(k)
    return P
