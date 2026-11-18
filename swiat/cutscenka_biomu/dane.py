#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dane cutscenki biomu (D-077; propozycja wykonania): trasy przelotu liczone z map i moduł DaneCutscenki.luau.

    python -B swiat/cutscenka_biomu/dane.py            # policz trasy i zapisz zrodla/DaneCutscenki.luau
    python -B swiat/cutscenka_biomu/dane.py --sprawdz  # czy zapisany moduł jest aktualny (kod 1, gdy nie)
    python -B swiat/cutscenka_biomu/dane.py --opis     # tabela tras (długość, czas, przystanki, odstępy)

Skąd biorą się liczby (nic nie jest wpisane ręcznie):
  * mapa biomu  — <biom>/krotki/znaczniki.json (przegrody, strefy potworów, inkubator, przybycie, strażnik, rozmiary)
                  i <biom>/krotki/czesci.json (bryły mapy: odstęp kamery od ścian, drzew i bram);
  * pakiet gry  — wygenerowany moduł danych biomu (DanePasa / DaneBagna / DaneDzungli): nazwa biomu, prostokąt
                  wejścia, linia bramy, atrybut „widział przelot”, wymaganie wejścia, kontener mapy;
  * ustawienia.json — kształt trasy (wysokości do wyboru, zwolnienia, czasy), oprawa, liczby serwera, progi testów.

Trasa: węzły (start za plecami gracza → inkubator → wejście każdej przegrody z potworami → leże rzadkiego potwora →
wejście areny → zbliżenie na strażnika) łączy krzywa Catmull-Rom; prędkość wzdłuż drogi ma rozbieg, zwolnienie przy
każdej przegrodzie i hamowanie do zera przed strażnikiem. Wysokość węzła = najniższa z listy, przy której kamera ma
odstęp od brył mapy; gdy próbka krzywej wchodzi za blisko bryły, sąsiednie węzły idą w górę i trasa liczy się od nowa.
Gotowa trasa to próbki co `krok_s` (położenie i cel kamery); klient i testy liczą z nich TĘ SAMĄ krzywą
(jednostajny Catmull-Rom po próbkach — ciągła prędkość, bez szarpnięć na łączeniach).
"""
import bisect
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
PLIK_USTAWIEN = os.path.join(TU, "ustawienia.json")
PLIK_LUAU = os.path.join(TU, "zrodla", "DaneCutscenki.luau")


class BladDanych(Exception):
    pass


def ustawienia():
    with open(PLIK_USTAWIEN, encoding="utf-8") as f:
        return json.load(f)


def _repo(sciezka):
    return os.path.join(REPO, *sciezka.split("/"))


# ================================================================================================ tabele Luau
_LICZBA = re.compile(r"-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")
_NAZWA = re.compile(r"[A-Za-z_]\w*")


def _tokeny(t):
    i, n, wynik = 0, len(t), []
    while i < n:
        c = t[i]
        if c.isspace():
            i += 1
        elif t.startswith("--[[", i):
            j = t.find("]]", i)
            i = n if j < 0 else j + 2
        elif t.startswith("--", i):
            j = t.find("\n", i)
            i = n if j < 0 else j
        elif c == '"':
            j, buf = i + 1, []
            while t[j] != '"':
                if t[j] == "\\":
                    j += 1
                    buf.append({"n": "\n", "t": "\t"}.get(t[j], t[j]))
                else:
                    buf.append(t[j])
                j += 1
            wynik.append(("s", "".join(buf)))
            i = j + 1
        elif c.isdigit() or (c == "-" and i + 1 < n and t[i + 1].isdigit()):
            m = _LICZBA.match(t, i)
            wynik.append(("n", float(m.group())))
            i = m.end()
        elif c.isalpha() or c == "_":
            m = _NAZWA.match(t, i)
            wynik.append(("i", m.group()))
            i = m.end()
        else:
            wynik.append((c, c))
            i += 1
    return wynik


def _wartosc(tok, i):
    rodzaj, w = tok[i]
    if rodzaj in ("s", "n"):
        return w, i + 1
    if rodzaj == "i":
        if w in ("true", "false"):
            return w == "true", i + 1
        if w == "nil":
            return None, i + 1
        raise BladDanych("nieznana wartość Luau: %s" % w)
    if rodzaj != "{":
        raise BladDanych("nieoczekiwany znak w tabeli Luau: %s" % w)
    i += 1
    slownik, lista = {}, []
    while tok[i][0] != "}":
        if tok[i][0] == "i" and tok[i + 1][0] == "=":
            klucz = tok[i][1]
            v, i = _wartosc(tok, i + 2)
            slownik[klucz] = v
        elif tok[i][0] == "[":
            klucz, i = _wartosc(tok, i + 1)
            if tok[i][0] != "]" or tok[i + 1][0] != "=":
                raise BladDanych("zły klucz w tabeli Luau")
            v, i = _wartosc(tok, i + 2)
            slownik[klucz] = v
        else:
            v, i = _wartosc(tok, i)
            lista.append(v)
        if tok[i][0] in (",", ";"):
            i += 1
    if slownik and lista:
        for nr, v in enumerate(lista, 1):
            slownik[nr] = v
    return (slownik if slownik else lista), i + 1


def tabela_luau(tekst):
    """Ostatnia tabela `return { … }` modułu danych (pierwsza to pusty zwrot strażnika Studio)."""
    tok = _tokeny(tekst)
    wynik = None
    for i in range(len(tok) - 1):
        if tok[i] == ("i", "return") and tok[i + 1][0] == "{":
            w, _ = _wartosc(tok, i + 1)
            if w:
                wynik = w
    if not isinstance(wynik, dict):
        raise BladDanych("brak tabeli danych w module Luau")
    return wynik


def stala_luau(tekst, nazwa):
    """Wartość napisowa stałej `S.NAZWA = "…"` z modułu stałych potworów."""
    m = re.search(r"\b%s\s*=\s*\"([^\"]+)\"" % re.escape(nazwa), tekst)
    if not m:
        raise BladDanych("brak stałej %s" % nazwa)
    return m.group(1)


# ================================================================================================ mapa
def _macierz(rx, ry, rz):
    """Obrót jak CFrame.fromOrientation(rx, ry, rz): R = Ry · Rx · Rz (kolumny = osie bryły w świecie)."""
    if abs(rx) < 1e-6 and abs(ry) < 1e-6 and abs(rz) < 1e-6:
        return None
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    return ((cy * cz + sy * sx * sz, -cy * sz + sy * sx * cz, sy * cx),
            (cx * sz, cx * cz, -sx),
            (-sy * cz + cy * sx * sz, sy * sz + cy * sx * cz, cy * cx))


class Mapa:
    """Znaczniki i bryły jednej mapy biomu (krótka mapa gry)."""
    R_MALE = 30.0

    def __init__(self, folder, przezroczystosc_do):
        self.folder = folder
        with open(os.path.join(_repo(folder), "znaczniki.json"), encoding="utf-8") as f:
            self.z = json.load(f)
        with open(os.path.join(_repo(folder), "czesci.json"), encoding="utf-8") as f:
            c = json.load(f)
        self.X0 = float(self.z["kontener"]["X0"])
        self.Z0 = float(self.z["kontener"]["Z0"])
        self.kontener = self.z["kontener"]["nazwa"].split("/")[-1]
        self.grupy = c["grupy"]
        self.czesci = c["czesci"]
        self.pominiete = 0
        male, self.duze = [], []
        for nr, p in enumerate(self.czesci):
            if float(p[13]) >= przezroczystosc_do:
                self.pominiete += 1
                continue
            hx, hy, hz = p[8] / 2.0, p[9] / 2.0, p[10] / 2.0
            rb = math.sqrt(hx * hx + hy * hy + hz * hz)
            bryla = (float(p[2]), float(p[3]), float(p[4]), _macierz(p[5], p[6], p[7]), hx, hy, hz, rb, nr)
            (self.duze if rb > self.R_MALE else male).append(bryla)
        male.sort(key=lambda b: b[0])
        self.male = male
        self.xs = [b[0] for b in male]

    def swiat(self, u, y, v):
        return [self.X0 + u, y, self.Z0 + v]

    def odstep(self, p, limit=40.0):
        """Najmniejsza odległość punktu świata p od bryły mapy (pudełka zorientowane) → (odległość, nr bryły)."""
        najlepsza, ktora = limit, None
        px, py, pz = p
        lo = bisect.bisect_left(self.xs, px - self.R_MALE - limit)
        hi = bisect.bisect_right(self.xs, px + self.R_MALE + limit)
        for zbior in (self.duze, self.male[lo:hi]):
            for cx, cy, cz, R, hx, hy, hz, rb, nr in zbior:
                dx, dy, dz = px - cx, py - cy, pz - cz
                zasieg = rb + najlepsza
                if dx * dx + dy * dy + dz * dz > zasieg * zasieg:
                    continue
                if R is not None:
                    dx, dy, dz = (R[0][0] * dx + R[1][0] * dy + R[2][0] * dz,
                                  R[0][1] * dx + R[1][1] * dy + R[2][1] * dz,
                                  R[0][2] * dx + R[1][2] * dy + R[2][2] * dz)
                ex, ey, ez = abs(dx) - hx, abs(dy) - hy, abs(dz) - hz
                d = math.sqrt(max(ex, 0.0) ** 2 + max(ey, 0.0) ** 2 + max(ez, 0.0) ** 2)
                if d < najlepsza:
                    najlepsza, ktora = d, nr
        return najlepsza, ktora

    def nazwa_bryly(self, nr):
        if nr is None:
            return "—"
        p = self.czesci[nr]
        return "%s (%s)" % (p[14], self.grupy[p[1]].split("/", 2)[-1])


# ================================================================================================ krzywe
def catmull(p0, p1, p2, p3, f):
    return 0.5 * (2 * p1 + (-p0 + p2) * f + (2 * p0 - 5 * p1 + 4 * p2 - p3) * f * f
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * f * f * f)


def _dosrodkowy(p0, p1, p2, p3, f):
    """Dośrodkowy Catmull-Rom (Barry–Goldman, wykładnik 0,5) na odcinku p1 → p2: bez pętli i ostrych zwrotów przy
    nierównych odstępach węzłów."""
    def odstep(a, b):
        return max(math.sqrt(math.dist(a, b)), 1e-4)
    t1 = odstep(p0, p1)
    t2 = t1 + odstep(p1, p2)
    t3 = t2 + odstep(p2, p3)
    t = t1 + f * (t2 - t1)

    def mieszaj(a, b, ta, tb):
        w = (t - ta) / (tb - ta)
        return [a[k] + (b[k] - a[k]) * w for k in range(3)]
    a1, a2, a3 = mieszaj(p0, p1, 0.0, t1), mieszaj(p1, p2, t1, t2), mieszaj(p2, p3, t2, t3)
    b1, b2 = mieszaj(a1, a2, 0.0, t2), mieszaj(a2, a3, t1, t3)
    return mieszaj(b1, b2, t1, t2)


def krzywa_wezlow(wezly, q):
    """Krzywa przez węzły [x, y, z] (dośrodkowy Catmull-Rom); q od 0 do len − 1; za końcami punkt odbity."""
    n = len(wezly)
    q = min(max(q, 0.0), n - 1.0)
    i = min(int(math.floor(q)), n - 2)
    f = q - i
    b, c = wezly[i], wezly[i + 1]
    a = wezly[i - 1] if i > 0 else [2 * b[k] - c[k] for k in range(3)]
    d = wezly[i + 2] if i + 2 < n else [2 * c[k] - b[k] for k in range(3)]
    return _dosrodkowy(a, b, c, d, f)


def krzywa_probek(tab, n, krok, t):
    """Krzywa, którą gra klient: jednostajny Catmull-Rom po płaskiej tablicy próbek co `krok` s.
    Ten sam wzór co LogikaCutscenki.krzywa (Luau)."""
    q = t / krok
    if q <= 0:
        return [tab[0], tab[1], tab[2]]
    if q >= n - 1:
        return [tab[3 * n - 3], tab[3 * n - 2], tab[3 * n - 1]]
    i = int(math.floor(q))
    f = q - i
    a, c, d = max(i - 1, 0), i + 1, min(i + 2, n - 1)
    return [catmull(tab[3 * a + k], tab[3 * i + k], tab[3 * c + k], tab[3 * d + k], f) for k in range(3)]


def _garb(x):
    if abs(x) >= 1:
        return 0.0
    k = math.cos(math.pi * x / 2)
    return k * k


# ================================================================================================ trasa
def _strefa(z, przegroda_id):
    for s in z["strefy"]:
        if s["podbiom"] == przegroda_id:
            return s
    return None


def uklad_biomu(M):
    """Z mapy: wejście, przegrody z potworami, leże, arena, inkubator, przybycie, strażnik (układ pasa u, y, v)."""
    z = M.z
    przeg = z["przegrody"]
    if len(przeg) < 3:
        raise BladDanych("%s: za mało przegród" % M.folder)
    srodkowe = []
    for p in przeg[1:-1]:
        s = _strefa(z, p["id"])
        if s is None:
            raise BladDanych("%s: przegroda %s bez strefy potworów" % (M.folder, p["id"]))
        rozmiar = z["rozmiary"].get(s["potwor"], {})
        srodkowe.append({"id": p["id"], "nazwa": p["nazwa"], "u": p["u"], "srodek": s["srodek"], "potwor": s["potwor"],
                         "leze": bool(s.get("odrodzenie_stale")), "wys": float(rozmiar.get("wys", 4.0))})
    jajko = next((m for m in z["miejsca"] if m["id"] == "jajko"), None)
    if jajko is None:
        raise BladDanych("%s: brak stanowiska jajka (inkubatora)" % M.folder)
    st = z["straznik"]
    rozm = z["rozmiary"].get(st["potwor"])
    if not rozm:
        raise BladDanych("%s: brak rozmiaru strażnika %s" % (M.folder, st["potwor"]))
    return {
        "wejscie": {"nazwa": przeg[0]["nazwa"], "u": przeg[0]["u"]},
        "przegrody": srodkowe,
        "arena": {"nazwa": przeg[-1]["nazwa"], "u": przeg[-1]["u"]},
        "inkubator": {"u": float(jajko["u"]), "v": float(jajko["v"])},
        "przybycie": [float(x) for x in z["przybycie"]["punkt"]],
        "straznik": {"nazwa": st["potwor"], "u": float(st["miejsce"][0]), "v": float(st["miejsce"][1]),
                     "y": float(st.get("y", 0)), "wys": float(rozm["wys"]),
                     "szer": float(rozm.get("szer", rozm.get("dl", rozm["wys"] * 0.6))),
                     "klip": (st.get("ryk") or {}).get("klip", "ryk")},
    }


def _kadr(oko, cel, st, T, proporcje):
    """Rzut pudła strażnika na ekran przy końcowym ujęciu → (największe |x|, największe |y|, udział wysokości).
    Współrzędne znormalizowane: ±1 to brzeg ekranu; pasy zabierają z góry i dołu po pasy_udzial wysokości."""
    f = [cel[k] - oko[k] for k in range(3)]
    dl = math.sqrt(sum(x * x for x in f))
    f = [x / dl for x in f]
    r = [-f[2], 0.0, f[0]]
    dr = math.sqrt(r[0] * r[0] + r[2] * r[2])
    r = [x / dr for x in r]
    g = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    tg = math.tan(math.radians(T["kat"]) / 2)
    xs, ys = [], []
    pol = st["szer"] / 2.0
    for dx in (-pol, pol):
        for dz in (-pol, pol):
            for y in (st["y"], st["y"] + st["wys"]):
                rel = [st["x"] + dx - oko[0], y - oko[1], st["z"] + dz - oko[2]]
                gl = sum(rel[k] * f[k] for k in range(3))
                if gl <= 0.5:
                    return 9.0, 9.0, 0.0
                xs.append(sum(rel[k] * r[k] for k in range(3)) / gl / (tg * proporcje))
                ys.append(sum(rel[k] * g[k] for k in range(3)) / gl / tg)
    widoczne = 1 - 2 * T["pasy"]
    return max(abs(x) for x in xs), max(abs(y) for y in ys), (max(ys) - min(ys)) / (2 * widoczne)


def _wysokosc(M, u, v, lista, odstep):
    """Najniższa wysokość z listy, przy której punkt (u, y, v) ma odstęp od brył mapy."""
    for y in lista:
        if M.odstep(M.swiat(u, y, v), odstep + 1)[0] >= odstep:
            return float(y)
    return float(lista[-1])


def wezly_biomu(M, U):
    """Węzły trasy w świecie: [{poz, patrz, rola, nazwa, zwolnienie, szer, dalej}]."""
    T = U["trasa"]
    uk = uklad_biomu(M)
    strona = 1.0 if uk["inkubator"]["v"] >= 0 else -1.0
    odstep = T["odstep_wezla_st"]
    wezly = []

    def dodaj(rola, nazwa, u, y, v, pu, py, pv, zwolnienie=0.0, szer=0.0, dalej=0.0, staly=False):
        wezly.append({"rola": rola, "nazwa": nazwa, "poz": M.swiat(u, y, v), "patrz": M.swiat(pu, py, pv),
                      "zwolnienie": zwolnienie, "szer": szer, "dalej": dalej, "staly": staly})

    PP, PI = T["przegroda"], T["inkubator"]
    u0 = uk["przybycie"][0] - T["start_za_plecami_st"]
    dodaj("start", uk["wejscie"]["nazwa"], u0, _wysokosc(M, u0, 0.0, T["start_wysokosci"], odstep), 0.0,
          uk["inkubator"]["u"] + 4, PP["patrz_y"], strona * PI["patrz_bok_st"])
    ui = uk["inkubator"]["u"] - PI["przed_st"]
    if ui > u0 + 6:
        dodaj("inkubator", "inkubator", ui, _wysokosc(M, ui, -strona * PI["bok_st"], PI["wysokosci"], odstep),
              -strona * PI["bok_st"], uk["wejscie"]["u"][1] + PI["patrz_dalej_st"], PP["patrz_y"],
              strona * PI["patrz_bok_st"] * 0.45, PI["zwolnienie"], PI["szerokosc_st"], 0.0)
    for nr, p in enumerate(uk["przegrody"]):
        bok = -strona * PP["bok_st"] * (1 if nr % 2 == 0 else -1)
        u = p["u"][0] + PP["za_wejsciem_st"]
        patrz_y = max(PP["patrz_y"], 0.4 * p["wys"]) if p["leze"] else PP["patrz_y"]
        dodaj("leze" if p["leze"] else "przegroda", p["nazwa"], u, _wysokosc(M, u, bok, PP["wysokosci"], odstep), bok,
              p["srodek"][0] + PP["patrz_za_srodek_st"], patrz_y, -bok / PP["bok_st"] * PP["patrz_bok_st"],
              PP["zwolnienie_leza"] if p["leze"] else PP["zwolnienie"], PP["szerokosc_st"], PP["srodek_dalej_st"])
    st = uk["straznik"]
    cel = (st["u"], st["y"] + T["straznik"]["patrz_x_wys"] * st["wys"], st["v"])
    ua = uk["arena"]["u"][0] - T["arena"]["przed_st"]
    dodaj("arena", uk["arena"]["nazwa"], ua, _wysokosc(M, ua, 0.0, T["arena"]["wysokosci"], odstep), 0.0, *cel)
    # zbliżenie: najbliższe ujęcie, w którym cały strażnik mieści się między pasami (także na telefonie) i kamera
    # ma odstęp od brył areny
    TS = T["straznik"]
    kadr = {"kat": U["oprawa"]["kat_widzenia"] - U["oprawa"]["straznik"]["najazd_kat"], "pasy": U["oprawa"]["pasy_udzial"]}
    pudlo = {"x": M.X0 + st["u"], "y": st["y"], "z": M.Z0 + st["v"], "wys": st["wys"], "szer": st["szer"]}
    proporcje = [16 / 9.0] + [a / float(b) for a, b in U["telefon"]]
    wybor = None
    for wsp in TS["odleglosci_x_wys"]:
        for bok in TS["boki_st"]:
            oko = M.swiat(st["u"] - wsp * st["wys"], st["y"] + TS["oko_x_wys"] * st["wys"], st["v"] + bok)
            if M.odstep(oko, odstep + 1)[0] < odstep:
                continue
            miary = [_kadr(oko, M.swiat(*cel), pudlo, kadr, pr) for pr in proporcje]
            if all(x <= TS["kadr_ndc_x"] and y <= TS["kadr_ndc_y"] for x, y, _ in miary):
                wybor = (wsp, bok, oko)
                break
        if wybor:
            break
    if wybor is None:
        raise BladDanych("%s: nie ma ujęcia strażnika z odstępem od brył i całym strażnikiem w kadrze" % M.folder)
    wsp, bok, oko = wybor
    wezly.append({"rola": "straznik", "nazwa": st["nazwa"], "poz": oko, "patrz": M.swiat(*cel), "zwolnienie": 0.0,
                  "szer": 0.0, "dalej": 0.0, "staly": True})
    return wezly, uk, pudlo


def _probkuj(wezly, U):
    """Z węzłów: próbki co krok_s (położenie, cel), czasy przystanków, długość drogi."""
    T = U["trasa"]
    poz = [w["poz"] for w in wezly]
    patrz = [w["patrz"] for w in wezly]
    n = len(wezly)
    NA_ODCINEK = 80
    qs, ss = [0.0], [0.0]
    poprzedni = poz[0]
    for i in range(1, (n - 1) * NA_ODCINEK + 1):
        q = i / float(NA_ODCINEK)
        p = krzywa_wezlow(poz, q)
        ss.append(ss[-1] + math.dist(p, poprzedni))
        qs.append(q)
        poprzedni = p
    S = ss[-1]
    garby = []
    for i, w in enumerate(wezly):
        if w["zwolnienie"] > 0:
            garby.append((ss[i * NA_ODCINEK] + w["dalej"], w["szer"], w["zwolnienie"], w))

    def mnoznik(s):
        m0 = T["rozbieg"]["udzial"]
        m = math.sqrt(m0 * m0 + (1 - m0 * m0) * min(1.0, s / T["rozbieg"]["droga_st"]))
        m = min(m, math.sqrt(max(0.0, min(1.0, (S - s) / T["hamowanie_st"]))))
        for srodek, szer, glebia, _w in garby:
            m *= 1 - glebia * _garb((s - srodek) / szer)
        return m

    # czas wzdłuż drogi przy prędkości jednostkowej: t(s) = ∫ ds / mnoznik(s); koniec (hamowanie do zera) analitycznie
    DS = 0.2
    kroki = int(math.floor((S - 0.02) / DS))
    s_tab, t_tab = [0.0], [0.0]
    for i in range(kroki):
        s_tab.append((i + 1) * DS)
        if i == 0 and T["rozbieg"]["udzial"] <= 0:
            t_tab.append(2 * math.sqrt(T["rozbieg"]["droga_st"] * DS))   # start z miejsca: ∫ ds / √(s / droga)
        else:
            t_tab.append(t_tab[-1] + DS / mnoznik((i + 0.5) * DS))
    reszta = S - s_tab[-1]
    s_tab.append(S)
    t_tab.append(t_tab[-1] + 2 * math.sqrt(T["hamowanie_st"] * reszta))
    predkosc = t_tab[-1] / T["lot_s"]                      # prędkość przelotowa (st/s), przy której lot trwa lot_s
    t_tab = [t / predkosc for t in t_tab]

    def droga(t):
        if t >= t_tab[-1]:
            return S
        i = bisect.bisect_right(t_tab, t) - 1
        f = (t - t_tab[i]) / (t_tab[i + 1] - t_tab[i])
        return s_tab[i] + f * (s_tab[i + 1] - s_tab[i])

    def parametr(s):
        i = min(bisect.bisect_right(ss, s) - 1, len(ss) - 2)
        d = ss[i + 1] - ss[i]
        return qs[i] + (qs[i + 1] - qs[i]) * ((s - ss[i]) / d if d > 0 else 0.0)

    def czas(s):
        i = min(bisect.bisect_right(s_tab, s) - 1, len(s_tab) - 2)
        return t_tab[i] + (t_tab[i + 1] - t_tab[i]) * (s - s_tab[i]) / (s_tab[i + 1] - s_tab[i])

    krok = T["krok_s"]
    razem = T["lot_s"] + T["postoj_s"]
    ile = int(round(razem / krok)) + 1
    tab_poz, tab_patrz = [], []
    for j in range(ile):
        q = parametr(droga(j * krok))
        tab_poz += [round(x, 3) for x in krzywa_wezlow(poz, q)]
        tab_patrz += [round(x, 3) for x in krzywa_wezlow(patrz, q)]
    przystanki = [{"t": round(czas(min(srodek, S)), 2), "nazwa": w["nazwa"], "rola": w["rola"]}
                  for srodek, _szer, _g, w in garby]
    return {"krok": krok, "czas": round(razem, 2), "lot": T["lot_s"], "n": ile, "poz": tab_poz, "patrz": tab_patrz,
            "dlugosc": round(S, 1), "przelotowa": round(predkosc, 1), "przystanki": przystanki}


def trasa_biomu(M, U):
    """Trasa biomu z kontrolą odstępu: gdy krzywa wchodzi za blisko bryły, sąsiednie węzły idą w górę."""
    T = U["trasa"]
    wezly, uk, pudlo = wezly_biomu(M, U)
    podniesienia = 0
    for _ in range(40):
        tr = _probkuj(wezly, U)
        zle = None
        t = 0.0
        while t <= tr["lot"] + 0.2:
            p = krzywa_probek(tr["poz"], tr["n"], tr["krok"], t)
            d, nr = M.odstep(p, T["odstep_min_st"] + 2)
            if d < T["odstep_min_st"] + T.get("odstep_zapas_st", 0):
                zle = (t, p, d, nr)
                break
            t += 0.05
        if zle is None:
            tr.update({"wezly": wezly, "uklad": uk, "pudlo": pudlo, "podniesienia": podniesienia})
            return tr
        # węzły najbliższe miejscu kolizji (wzdłuż pasa) idą w górę; ujęcie strażnika jest stałe
        px = zle[1][0]
        ruchome = [w for w in wezly if not w["staly"]]
        ruchome.sort(key=lambda w: abs(w["poz"][0] - px))
        zmieniono = False
        for w in ruchome[:2]:
            if w["poz"][1] + T["podnies_o_st"] <= T["wysokosc_maks_st"]:
                w["poz"][1] += T["podnies_o_st"]
                zmieniono = True
        podniesienia += 1
        if not zmieniono:
            break
    raise BladDanych("%s: nie udało się ułożyć trasy z odstępem %.1f st (ostatnia kolizja: t = %.2f s, %s, %.2f st)"
                     % (M.folder, T["odstep_min_st"], zle[0], M.nazwa_bryly(zle[3]), zle[2]))


def miary_trasy(tr, M, U, dt=1 / 60.0):
    """Liczby do testów i README: prędkość, przyspieszenie, obrót, odstęp od brył, cofnięcia, kadr strażnika."""
    n, krok = tr["n"], tr["krok"]
    czas = tr["czas"]
    ile = int(round(czas / dt))
    P = [krzywa_probek(tr["poz"], n, krok, i * dt) for i in range(ile + 1)]
    C = [krzywa_probek(tr["patrz"], n, krok, i * dt) for i in range(ile + 1)]
    V = [math.dist(P[i + 1], P[i]) / dt for i in range(ile)]
    A = [abs(V[i + 1] - V[i]) / dt for i in range(ile - 1)]
    wektor = [[(P[i + 1][k] - P[i][k]) / dt for k in range(3)] for i in range(ile)]
    A3 = [math.dist(wektor[i + 1], wektor[i]) / dt for i in range(ile - 1)]

    def kierunek(i):
        d = [C[i][k] - P[i][k] for k in range(3)]
        dl = math.sqrt(sum(x * x for x in d))
        return [x / dl for x in d]

    K = [kierunek(i) for i in range(ile + 1)]
    obrot = [math.degrees(math.acos(max(-1.0, min(1.0, sum(K[i][k] * K[i + 1][k] for k in range(3)))))) / dt
             for i in range(ile)]
    odstep, gdzie = 1e9, None
    for i in range(0, ile + 1, 2):
        d, nr = M.odstep(P[i], 12.0)
        if d < odstep:
            odstep, gdzie = d, (round(i * dt, 2), M.nazwa_bryly(nr))
    cofniecie = max([0.0] + [P[i][0] - P[i + 1][0] for i in range(ile)])
    # wstecz liczone narastająco: najdalsze cofnięcie od dotychczasowego maksimum
    szczyt, wstecz = P[0][0], 0.0
    for p in P:
        szczyt = max(szczyt, p[0])
        wstecz = max(wstecz, szczyt - p[0])
    kadr = {"kat": U["oprawa"]["kat_widzenia"] - U["oprawa"]["straznik"]["najazd_kat"], "pasy": U["oprawa"]["pasy_udzial"]}
    kadry = {}
    for nazwa, pr in [("16x9", 16 / 9.0)] + [("%dx%d" % (a, b), a / float(b)) for a, b in U["telefon"]]:
        x, y, udzial = _kadr(P[-1], C[-1], tr["pudlo"], kadr, pr)
        kadry[nazwa] = {"x": round(x, 3), "y": round(y, 3), "udzial": round(udzial, 3)}
    ink = tr["uklad"]["inkubator"]
    punkt = {"x": M.X0 + ink["u"], "y": 0.0, "z": M.Z0 + ink["v"], "wys": 4.0, "szer": 4.0}
    w_kadrze = 0
    for i in range(0, ile + 1):
        x, y, _ = _kadr(P[i], C[i], punkt, kadr, min(a / float(b) for a, b in U["telefon"]))
        if x <= 0.95 and y <= 1 - 2 * kadr["pasy"]:
            w_kadrze += 1
    przystanki = []
    for p in tr["przystanki"]:
        i = min(int(round(p["t"] / dt)), ile - 1)
        okno = V[max(0, i - 6):i + 7]
        przystanki.append({"nazwa": p["nazwa"], "rola": p["rola"], "t": p["t"], "predkosc": round(min(okno), 1),
                           "x": round(P[i][0], 1)})
    return {
        "czas": czas, "lot": tr["lot"], "dlugosc": tr["dlugosc"], "przelotowa": tr["przelotowa"],
        "predkosc_maks": round(max(V), 1), "przyspieszenie_maks": round(max(A), 1),
        "przyspieszenie_wektorowe_maks": round(max(A3), 1), "obrot_maks": round(max(obrot), 1),
        "odstep_min": round(odstep, 2), "odstep_gdzie": gdzie, "cofniecie_krok": round(cofniecie, 3),
        "cofniecie": round(wstecz, 3), "bok_maks": round(max(abs(p[2] - M.Z0) for p in P), 1),
        "wysokosc_min": round(min(p[1] for p in P), 1), "wysokosc_maks": round(max(p[1] for p in P), 1),
        "predkosc_koncowa": round(V[-1], 3), "kadry": kadry, "przystanki": przystanki,
        "przyspieszenie_kiedy": round(A.index(max(A)) * dt, 2), "obrot_kiedy": round(obrot.index(max(obrot)) * dt, 2),
        "skok_maks": round(max(math.dist(P[i + 1], P[i]) for i in range(ile)), 2),
        "inkubator_w_kadrze_s": round(w_kadrze * dt, 2),
    }


# ================================================================================================ dane biomów
def dane_gry(wpis):
    with open(_repo(wpis["dane_gry"]), encoding="utf-8") as f:
        return tabela_luau(f.read())


def biom(wpis, U, mapa=None):
    """Wszystko o jednym biomie: nazwy z pakietu gry, trasa z mapy."""
    G = dane_gry(wpis)
    M = mapa or Mapa(wpis["mapa"], U["trasa"]["przezroczystosc_przeszkody_do"])
    B = G["biom"]
    if G["mapa"]["nazwa"] != M.kontener:
        raise BladDanych("%s: pakiet gry czyta mapę %s, a mapa to %s" % (wpis["mapa"], G["mapa"]["nazwa"], M.kontener))
    tr = trasa_biomu(M, U)
    uk = tr["uklad"]
    st = uk["straznik"]
    wej = G["wejscie"]
    # jedno miejsce pasa = jeden biom: prostokąt wejścia kończy się na linii bramy do następnego biomu
    prostokat = {"x1": wej["x1"], "x2": min(wej["x2"], G["brama"]["x"]), "z1": wej["z1"], "z2": wej["z2"]}
    strumien, ostatni = [], None
    for i in range(tr["n"]):
        p = tr["poz"][3 * i:3 * i + 3]
        if ostatni is None or abs(p[0] - ostatni) >= U["trasa"]["strumien_co_st"]:
            strumien.append([round(p[0], 1), 0, round(M.Z0, 1)])
            ostatni = p[0]
    strumien.append([round(M.X0 + st["u"], 1), 0, round(M.Z0 + st["v"], 1)])
    wym = B.get("wymaganie")
    return {
        "id": B["id"], "nazwa": B["nazwa"], "kontenerGry": wpis["kontener_gry"], "mapa": G["mapa"]["nazwa"],
        "atrybut": B["atrybutPrzelot"], "wymaganie": wym["atrybut"] if wym else None,
        "prostokat": prostokat, "yMin": G["ratunek"]["yMin"],
        "straznik": {"nazwa": st["nazwa"], "klip": st["klip"], "gatunek": G["straznik"]["gatunek"],
                     "poz": [tr["pudlo"]["x"], tr["pudlo"]["y"], tr["pudlo"]["z"]], "wys": st["wys"], "szer": st["szer"]},
        "trasa": tr, "strumien": strumien, "_mapa": M,
    }


def wszystko(U=None):
    U = U or ustawienia()
    Z = U["zaleznosci"]
    with open(_repo(Z["stale_potworow"]), encoding="utf-8") as f:
        blokada = stala_luau(f.read(), Z["blokada_walki"])
    biomy = [biom(w, U) for w in U["biomy"]]
    D = {"U": U, "kontener": U["kontener"], "blokada": blokada, "biomy": biomy}
    D["skrot"] = hashlib.sha256(tekst_luau(D, "").encode("utf-8")).hexdigest()[:12]
    return D


# ================================================================================================ Luau
def _napis(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def _liczba(x):
    if isinstance(x, bool):
        return "true" if x else "false"
    if isinstance(x, int) or float(x).is_integer():
        return str(int(x))
    return repr(round(float(x), 4))


def luau(v, wciecie=1):
    t = "\t" * wciecie
    if v is None:
        return "nil"
    if isinstance(v, bool) or isinstance(v, (int, float)):
        return _liczba(v)
    if isinstance(v, str):
        return _napis(v)
    if isinstance(v, (list, tuple)):
        if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
            wiersze, wiersz = [], []
            for x in v:
                wiersz.append(_liczba(x))
                if len(wiersz) == 15:
                    wiersze.append(", ".join(wiersz))
                    wiersz = []
            if wiersz:
                wiersze.append(", ".join(wiersz))
            if len(wiersze) <= 1:
                return "{ " + "".join(wiersze) + " }" if wiersze else "{}"
            return "{\n" + "".join(t + "\t" + w + ",\n" for w in wiersze) + t + "}"
        if not v:
            return "{}"
        return "{\n" + "".join(t + "\t" + luau(x, wciecie + 1) + ",\n" for x in v) + t + "}"
    if isinstance(v, dict):
        return "{\n" + "".join("%s\t%s = %s,\n" % (t, k, luau(x, wciecie + 1)) for k, x in v.items() if x is not None) + t + "}"
    raise BladDanych("nie umiem zapisać w Luau: %r" % (v,))


def uklad_stale(U):
    """Stałe układu napisów i przycisku (te same liczby dostaje LogikaCutscenki.uklad u klienta)."""
    K = U["oprawa"]["uklad"]
    return {"margines": K["margines_px"], "pasy": U["oprawa"]["pasy_udzial"], "nazwa": K["nazwa"], "nadtytul": K["nadtytul"],
            "podpis": K["podpis"], "straznik": K["straznik"],
            "pomin": {"szer": K["pomin"]["szer"], "wys": K["pomin"]["wys"], "minSzer": K["pomin"]["min_szer"],
                      "minWys": K["pomin"]["min_wys"], "maksSzer": K["pomin"]["maks_szer"], "maksWys": K["pomin"]["maks_wys"],
                      "tekst": K["pomin"]["tekst"], "tekstMin": K["pomin"]["tekst_min"]}}


def tabela_danych(D):
    U = D["U"]
    S, O, Z = U["serwer"], U["oprawa"], U["zaleznosci"]
    biomy = []
    for b in D["biomy"]:
        tr = b["trasa"]
        biomy.append({
            "id": b["id"], "nazwa": b["nazwa"], "kontenerGry": b["kontenerGry"], "mapa": b["mapa"], "atrybut": b["atrybut"],
            "wymaganie": b["wymaganie"], "prostokat": b["prostokat"], "yMin": b["yMin"],
            "straznik": {k: b["straznik"][k] for k in ("nazwa", "klip", "gatunek", "poz", "wys")},
            "przystanki": [{"t": p["t"], "nazwa": p["nazwa"]} for p in tr["przystanki"] if p["rola"] != "inkubator"],
            "strumien": b["strumien"],
            "trasa": {"krok": tr["krok"], "czas": tr["czas"], "lot": tr["lot"], "n": tr["n"], "poz": tr["poz"],
                      "patrz": tr["patrz"]},
        })
    return {
        "wersja": 1,
        "skrot": D.get("skrot", ""),
        "kontener": D["kontener"],
        "blokada": D["blokada"],
        "serwer": {"okres": S["okres_s"], "uspokojenie": S["uspokojenie_s"], "odpowiedz": S["odpowiedz_s"],
                   "ponowPoOdmowie": S["ponow_po_odmowie_s"], "ponowPoCiszy": S["ponow_po_ciszy_s"], "probMaks": S["prob_maks"],
                   "ladowanie": S["ladowanie_s"], "zapas": S["zapas_s"], "strumienCo": S["strumien_co_s"],
                   "wyprzedzenie": S["wyprzedzenie_s"], "limitWiadomosci": S["limit_wiadomosci"],
                   "czekanieNaBiom": S["czekanie_na_biom_s"]},
        "oprawa": {
            "kat": O["kat_widzenia"], "pasy": O["pasy_udzial"], "pasyWjazd": O["pasy_wjazd_s"], "zaslona": O["zaslona_s"],
            "plansza": {"od": O["plansza"]["od_s"], "pelnaOd": O["plansza"]["pelna_od_s"], "pelnaDo": O["plansza"]["pelna_do_s"],
                        "doKiedy": O["plansza"]["do_s"], "nadtytul": O["plansza"]["nadtytul"]},
            "podpisy": {"wlaczone": O["podpisy_przegrod"]["wlaczone"], "przed": O["podpisy_przegrod"]["przed_s"],
                        "trwa": O["podpisy_przegrod"]["trwa_s"]},
            "pomijanie": {"wlaczone": O["pomijanie"]["wlaczone"], "od": O["pomijanie"]["od_s"], "napis": O["pomijanie"]["napis"],
                          "klawisze": O["pomijanie"]["klawisze"], "podpowiedz": O["pomijanie"]["podpowiedz_klawisza"],
                          "atrybut": O["pomijanie"]["atrybut_wylacznika"]},
            "straznik": {"rykPo": O["straznik"]["ryk_po_s"], "napisPrzed": O["straznik"]["napis_przed_s"],
                         "napisDoKonca": O["straznik"]["napis_do_konca_s"], "wstrzasCzas": O["straznik"]["wstrzas_s"],
                         "wstrzas": O["straznik"]["wstrzas_st"], "wstrzasHz": O["straznik"]["wstrzas_hz"],
                         "najazd": O["straznik"]["najazd_kat"]},
            "uklad": uklad_stale(U),
            "koniec": {"zaciemnienie": O["koniec"]["zaciemnienie_s"], "rozjasnienie": O["koniec"]["rozjasnienie_s"],
                       "zaPlecami": O["koniec"]["kamera_za_plecami_st"], "nad": O["koniec"]["kamera_nad_st"]},
        },
        "zajetosc": {
            "walka": {"kontener": Z["prototyp_walki"]["kontener"], "modul": Z["prototyp_walki"]["modul"]},
            "chmury": {"kontener": Z["chmury"]["kontener"], "atrybut": Z["chmury"]["atrybut"]},
            "trening": Z["trening"]["atrybut_gracza"],
        },
        "dzwiek": {"kontener": Z["dzwiek"]["kontener"], "modul": Z["dzwiek"]["modul"], "ryk": Z["dzwiek"]["zdarzenie_ryku"]},
        "potwory": {"uchwyt": Z["potwory"]["uchwyt_klienta"], "gotowy": Z["potwory"]["atrybut_gotowosci"],
                    "stan": Z["potwory"]["folder_stanu"], "straznik": Z["potwory"]["atrybut_straznika"]},
        "mgla": Z["mgla"]["atrybut_przelotu"],
        "zapis": {"kontener": Z["stan_gracza"]["kontener"], "atrybut": Z["stan_gracza"]["atrybut_zapisu"]},
        "przejecie": Z["haczyk_pasa"]["atrybut_przejecia"],
        "ustepuje": Z["haczyk_pasa"]["atrybut_ustepuje"],
        "biomy": biomy,
    }


NAGLOWEK = """--[[
	DaneCutscenki — WYGENEROWANE przez swiat/cutscenka_biomu/dane.py z map biomów (krotki/znaczniki.json, czesci.json),
	modułów danych pakietów gry i ustawienia.json. NIE EDYTUJ RĘCZNIE: zmień źródła i uruchom
	python -B swiat/cutscenka_biomu/dane.py. Trasa biomu to próbki co `krok` s: poz i patrz = płaskie tablice
	{ x1, y1, z1, x2, … } w ŚWIECIE; krzywą liczy LogikaCutscenki.krzywa (jednostajny Catmull-Rom po próbkach).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

return """


def tekst_luau(D, skrot=None):
    d = dict(D)
    if skrot is not None:
        d["skrot"] = skrot
    return NAGLOWEK + luau(tabela_danych(d), 0) + "\n"


def aktualny():
    D = wszystko()
    try:
        with open(PLIK_LUAU, encoding="utf-8") as f:
            zapisany = f.read().replace("\r\n", "\n")
    except OSError:
        zapisany = ""
    return zapisany == tekst_luau(D), D


def opis(D):
    linie = []
    for b in D["biomy"]:
        m = miary_trasy(b["trasa"], b["_mapa"], D["U"])
        linie.append("%-8s %-8s droga %.0f st, czas %.1f s (lot %.1f s), przelotowa %.0f st/s, najw. %.0f st/s, "
                     "przysp. %.0f st/s², obrót %.0f°/s, odstęp min %.2f st (%s, t = %.2f s), wysokość %.1f–%.1f, "
                     "podniesień węzłów %d; największe przyspieszenie w t = %.2f s, obrót w t = %.2f s"
                     % (b["id"], b["nazwa"], m["dlugosc"], m["czas"], m["lot"], m["przelotowa"], m["predkosc_maks"],
                        m["przyspieszenie_maks"], m["obrot_maks"], m["odstep_min"], m["odstep_gdzie"][1],
                        m["odstep_gdzie"][0], m["wysokosc_min"], m["wysokosc_maks"], b["trasa"]["podniesienia"],
                        m["przyspieszenie_kiedy"], m["obrot_kiedy"]))
        for p in m["przystanki"]:
            linie.append("           %5.2f s  %-26s %5.1f st/s (x = %.0f)" % (p["t"], p["nazwa"], p["predkosc"], p["x"]))
        linie.append("           strażnik %s: kadr %s" % (b["straznik"]["nazwa"], ", ".join(
            "%s wys. %.0f%% (|y| %.2f, |x| %.2f)" % (k, v["udzial"] * 100, v["y"], v["x"]) for k, v in m["kadry"].items())))
    return linie


def main(argv):
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    try:
        if "--sprawdz" in argv:
            ok, D = aktualny()
            print("DaneCutscenki.luau: %s (skrót %s)" % ("aktualny" if ok else "NIEAKTUALNY — uruchom dane.py", D["skrot"]))
            return 0 if ok else 1
        D = wszystko()
        if "--opis" not in argv:
            os.makedirs(os.path.dirname(PLIK_LUAU), exist_ok=True)
            with open(PLIK_LUAU, "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst_luau(D))
            print("zapisano zrodla/DaneCutscenki.luau (skrót %s, %d biomy)" % (D["skrot"], len(D["biomy"])))
        for linia in opis(D):
            print(linia)
    except BladDanych as e:
        print("BŁĄD DANYCH: %s" % e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
