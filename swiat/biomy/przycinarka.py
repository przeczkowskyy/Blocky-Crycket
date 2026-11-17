#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Przycinarka pasa (D-096): z DŁUGICH map-projektów (swiat/las_pas, swiat/bagno_pas — generatory bez zmian) robi
KRÓTKIE i węższe mapy gry o wymiarach z swiat/biomy/wymiary_pasa.json. Bez Studio, bez Blendera.

    python -B swiat/biomy/przycinarka.py               # → swiat/las_pas/krotki/, swiat/bagno_pas/krotki/ + tabela
    python -B swiat/biomy/przycinarka.py --sprawdz     # tylko sprawdza, czy pliki w krotki/ są aktualne (kod 1, gdy nie)
    python -B swiat/biomy/przycinarka.py --podglad DIR # dodatkowo rzut z góry „przed / po” (las + Bagno) do DIR

Jak (ta sama mapa, tylko krótsza i węższa — bez nowych rzeczy):
  1. Z każdego biomu zostają wybrane odcinki wzdłuż pasa („zostaw” w wymiarach: przybycie, pierwszy kojec każdej
     przegrody z przejściem, leże, arena, brama) i są sklejane jeden za drugim; reszta odpada (2 z 3 kojców przegród).
  2. Sklejony pas jest ściskany wzdłuż (położenia, nie rozmiary brył) tak, żeby bieg od przybycia do bramy trwał
     dlugosc_s przy bieg_st_s; to, co leży przed punktem przybycia, zostaje bez ściskania. Las zostaje przy swoim
     punkcie przybycia (u 14 — teleport bez zmian, las dalej zaczyna się w u 0), Bagno zaczyna się za nową bramą
     lasu, a dalsze rezerwacje (Dżungla…) przesuwają się o tyle, o ile skrócił się pas.
  3. W poprzek: środek |v| ≤ rdzen_v_st bez zmian (przejścia), pole od rdzenia do 36 ściskane do
     szerokosc_s · bieg / 2 (położenia), kulisy dalej przesuwane o różnicę — niewidzialna ściana z 38 na 34 przy 4 s.
  4. Długie bryły osiowe (płyta, ścieżka, ściany, płoty w poprzek) dostają nowe końce; reszta tylko się przesuwa,
     bryły z wyciętych odcinków (i grupy z „pomin_grupy”) odpadają.
  5. Plan i znaczniki: te same przekształcenia na każdym polu z położeniem (u, v, punkty, węzły, domy, pola stref,
     przelot kamery, prostokąty w świecie). Strefy scalone: z każdej przegrody zostaje strefa pierwszego kojca z
     poziomami wszystkich trzech; max potworów ≤ obwód pętli / odstęp (wataha jak w generatorze gry). Przelot kamery:
     odcinki lotu skrócone jednym współczynnikiem, najkrótszy lot z kamerą ≤ VMAX_PRZELOTU; postój i ryk bez zmian.
Wynik deterministyczny; plik planu krótkiego ma pole „wymiary” (skąd, jakie liczby, współczynniki).
"""
import argparse
import copy
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

import numpy as np  # noqa: E402

from swiat.las_pas.zasady import aabb, macierz  # noqa: E402

PLIK_WYMIAROW = os.path.join(TU, "wymiary_pasa.json")
X0, Z0 = 1100.0, -700.0
KROK = 0.01


def _json(sciezka):
    with open(os.path.join(REPO, sciezka) if not os.path.isabs(sciezka) else sciezka, encoding="utf-8") as f:
        return json.load(f)


def r2(x):
    return round(float(x) / KROK) * KROK if abs(round(float(x) / KROK) * KROK - round(float(x), 2)) > 1e-9 else round(float(x), 2)


# ======================================================================================== przekształcenie wzdłuż
class Odcinki:
    """Odcinki zostawione z długiego pasa → sklejone → ściśnięte współczynnikiem f wokół kotwicy."""

    def __init__(self, zostaw, kotwica, brama, dl_cel, kotwica_nowa=None, wejscie=None, wejscie_nowe=None):
        self.seg = [tuple(map(float, s)) for s in sorted(zostaw)]
        for (a, b), (c, _) in zip(self.seg, self.seg[1:]):
            if b > c:
                raise ValueError("odcinki zachodzą na siebie: %s, %s" % ((a, b), (c, _)))
        self.start, s = [], 0.0
        for a, b in self.seg:
            self.start.append(s)
            s += b - a
        self.dl_sklejona = s
        self.kotwica, self.brama = float(kotwica), float(brama)
        self.f = dl_cel / (self.s(brama) - self.s(kotwica))
        if wejscie is not None:
            # biom za bramą poprzedniego: punkt wejścia (brama poprzedniego) ma stanąć w wejscie_nowe; przed punktem
            # przybycia nic nie jest ściskane (to nie należy do biegu przybycie → brama)
            self.kotwica_nowa = wejscie_nowe + (self.s(kotwica) - self.s(wejscie))
        else:
            self.kotwica_nowa = float(kotwica if kotwica_nowa is None else kotwica_nowa)

    def s(self, u):
        """Położenie w sklejonym pasie (punkt z wyciętego odcinka → początek następnego zostawionego)."""
        a0 = self.seg[0][0]
        if u <= a0:
            return u - a0
        for (a, b), st in zip(self.seg, self.start):
            if u < a:
                return st
            if u <= b:
                return st + (u - a)
        return self.dl_sklejona + (u - self.seg[-1][1])

    def zostaje(self, u):
        return any(a <= u < b for a, b in self.seg)

    def T(self, u):
        """Ściśnięty jest tylko bieg przybycie → brama; przed przybyciem i za bramą odległości bez zmian."""
        s, sk, sb = self.s(u), self.s(self.kotwica), self.s(self.brama)
        if s <= sk:
            return self.kotwica_nowa + (s - sk)
        if s <= sb:
            return self.kotwica_nowa + self.f * (s - sk)
        return self.kotwica_nowa + self.f * (sb - sk) + (s - sb)


class Przeksztalcenie:
    """Całość pasa: las (u ≤ brama lasu), Bagno (do końca jego części), dalej przesunięcie; w poprzek g(v)."""

    def __init__(self, W):
        self.W = W
        dl = W["dlugosc_s"] * W["bieg_st_s"]
        self.h_nowe = W["szerokosc_s"] * W["bieg_st_s"] / 2.0
        self.h_dawne = float(W["dawna_polowa_pola_st"])
        self.rdzen = float(W.get("rdzen_v_st", 0))     # środek pasa bez ściskania (przejścia ±8 zostają szerokie na 16)
        self.biomy = {}
        self.kolejnosc = []
        for b in W["biomy"]:
            if b.get("po_biomie"):
                pop = self.biomy[b["po_biomie"]]
                o = Odcinki(b["zostaw"], b["kotwica_u"], b["brama_u"], dl, wejscie=b["wejscie_u"],
                            wejscie_nowe=pop.T(pop.brama))
            else:
                o = Odcinki(b["zostaw"], b["kotwica_u"], b["brama_u"], dl, kotwica_nowa=b.get("kotwica_nowa_u"))
            self.biomy[b["id"]] = o
            self.kolejnosc.append((b, o))
        # granice biomów w długim pasie (las do bramy lasu, Bagno do końca jego zostawionych odcinków)
        self.granice = []
        dol = -1e9
        for i, (b, o) in enumerate(self.kolejnosc):
            gora = self.kolejnosc[i + 1][0]["wejscie_u"] if i + 1 < len(self.kolejnosc) else o.seg[-1][1]
            self.granice.append((dol, gora, o))
            dol = gora
        ost = self.kolejnosc[-1][1]
        self.koniec_dl = ost.seg[-1][1]
        self.przesuniecie_dalej = ost.T(self.koniec_dl) - self.koniec_dl
        self.u_min = self.kolejnosc[0][1].seg[0][0]

    def T(self, u):
        if u < self.u_min - 200:
            return u                                   # miasteczko i wszystko przed pasem — bez zmian
        if u > self.koniec_dl:
            return u + self.przesuniecie_dalej         # rezerwacje dalszych biomów
        for dol, gora, o in self.granice:
            if dol < u <= gora:
                return o.T(u)
        return self.granice[0][2].T(u)

    def zostaje(self, u):
        return any(o.zostaje(u) for _, o in self.kolejnosc)

    def w_pasie_x(self, x):
        """Punkt świata leży w pasie biomów (miasteczko i to, co przed pasem, zostaje bez zmian — też w poprzek)."""
        return (x - X0) >= self.u_min - 200

    def g(self, v):
        a, r = abs(v), self.rdzen
        if a <= r:
            return v
        if a <= self.h_dawne:
            return math.copysign(r + (a - r) * (self.h_nowe - r) / (self.h_dawne - r), v)
        return v - math.copysign(self.h_dawne - self.h_nowe, v)

    # świat
    def x(self, x):
        return X0 + self.T(x - X0)

    def z(self, z):
        return Z0 + self.g(z - Z0)


# ======================================================================================== części mapy
def osiowa(c):
    R = macierz(c[5], c[6], c[7])
    A = np.abs(R)
    return bool(np.all((A < 1e-3) | (A > 1 - 1e-3)))


def czesci_krotkie(d, P, pomin_grupy):
    """Nowa lista części: przesunięte, przycięte albo odrzucone. → (dane, liczniki)."""
    wyn = copy.deepcopy(d)
    grupy = d["grupy"]
    pomin = set()
    for i, gname in enumerate(grupy):
        for pg in pomin_grupy:
            if gname.split("/", 2)[-1] == pg or gname.split("/", 2)[-1].startswith(pg + "/"):
                pomin.add(i)
    nowe, odrzucone, przyciete = [], 0, 0
    for c in d["czesci"]:
        if c[1] in pomin:
            odrzucone += 1
            continue
        lo, hi = aabb(c)
        u, v = c[2] - X0, c[4] - Z0
        hu, hv = (hi[0] - lo[0]) / 2.0, (hi[2] - lo[2]) / 2.0
        n = list(c)
        ax = osiowa(c)
        R = macierz(c[5], c[6], c[7]) if ax else None
        if hu > 10 and ax:
            u1, u2 = u - hu, u + hu
            # odrzuć tylko, gdy żaden kawałek nie leży w zostawionych odcinkach
            probki = np.linspace(u1, u2, 41)
            if not any(P.zostaje(x) for x in probki):
                odrzucone += 1
                continue
            n1, n2 = P.T(u1), P.T(u2)
            n[2] = X0 + (n1 + n2) / 2.0
            os_x = int(np.argmax(np.abs(R[0, :])))     # która oś części leży wzdłuż świata X
            rozm = list(n[8:11])
            rozm[os_x] = max(0.05, (n2 - n1))
            n[8], n[9], n[10] = rozm
            przyciete += 1
        else:
            if not P.zostaje(u):
                odrzucone += 1
                continue
            n[2] = X0 + P.T(u)
        if hv > 12 and ax:
            v1, v2 = v - hv, v + hv
            m1, m2 = P.g(v1), P.g(v2)
            n[4] = Z0 + (m1 + m2) / 2.0
            os_z = int(np.argmax(np.abs(R[2, :])))
            rozm = list(n[8:11])
            rozm[os_z] = max(0.05, (m2 - m1))
            n[8], n[9], n[10] = rozm
        elif abs(v) - hv > P.rdzen and "/Punkty/" not in grupy[c[1]]:   # punkty E: środek = znacznik
            # cała bryła po jednej stronie, poza rdzeniem: brzeg bliższy środka pasa trafia tam, gdzie jego punkt — to,
            # co stało obok przejścia albo pętli, nie wjeżdża w nie przez to, że bryła ma dawny rozmiar
            n[4] = Z0 + math.copysign(abs(P.g(abs(v) - hv)) + hv, v)
        else:
            n[4] = Z0 + P.g(v)
        n[2], n[4] = round(n[2], 3), round(n[4], 3)
        n[8], n[9], n[10] = round(n[8], 3), round(n[9], 3), round(n[10], 3)
        nowe.append(n)
    wyn["czesci"] = nowe
    return wyn, {"przed": len(d["czesci"]), "po": len(nowe), "odrzucone": odrzucone, "przyciete": przyciete}


ZASADY_RZECZY = ("plac", "otwarcie", "petla")
PRZESUNIECIA = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
                for r in (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0) for a in range(0, 360, 45)]


def zasady_planu(plan):
    """Zasady lasu-pasa (swiat/las_pas/zasady.py) z liczbami planu krótkiego."""
    import types
    from swiat.las_pas import zasady as ZA
    K = types.SimpleNamespace(
        X0=float(plan["swiat"]["X0"]), Z0=float(plan["swiat"]["Z0"]), P=plan, strefy=plan["strefy"],
        straznik=plan["straznik"],
        wezly=[tuple(w) for st in plan["strefy"] for w in st["trasa"]] + [tuple(plan["straznik"]["miejsce"])])
    return ZA, ZA.Zasady(K), float(plan["zasady"].get("plac_walki_r", ZA.PLAC_R))


def popraw_rzeczy(cz, plan, P, b):
    """Bryły zostają w dawnym rozmiarze, a pas się ściska — część drobiazgów wchodzi w plac walki, otwarcie przejścia
    albo pętlę potworów. Taka rzecz (stykające się bryły tej samej grupy) jest odsuwana o najmniej (0,5…6 st), a gdy
    się nie da — odpada. → (odsunięte, usunięte, bryły usunięte)."""
    ZA, Z, r = zasady_planu(plan)
    stary_r, ZA.PLAC_R = ZA.PLAC_R, r
    try:
        grupy, czesci = cz["grupy"], cz["czesci"]
        o = P.biomy[b["id"]]
        u_lo, u_hi = X0 + o.T(o.seg[0][0]) - 40, X0 + o.T(o.seg[-1][1]) + 40
        zle = [i for i, c in enumerate(czesci) if Z.naruszenia(c, grupy[c[1]], tylko=ZASADY_RZECZY)]
        if not zle:
            return 0, 0, 0
        bb = [aabb(c) for c in czesci]
        maly = [max(mx[0] - mn[0], mx[2] - mn[2]) <= 16 for mn, mx in bb]   # duże bryły (płoty, płyty) nie jeżdżą
        po_grupie = {}
        for i, c in enumerate(czesci):
            if maly[i]:
                po_grupie.setdefault(c[1], []).append(i)
        zrobione, usun, odsuniete, usuniete = set(), set(), 0, 0
        for i in zle:
            if i in zrobione or not maly[i]:
                continue
            # rzecz = spójne (stykające się) bryły tej samej grupy wokół złej bryły
            rzecz, stos = {i}, [i]
            while stos:
                j = stos.pop()
                mn, mx = bb[j]
                for k in po_grupie[czesci[j][1]]:
                    if k in rzecz:
                        continue
                    a, c_ = bb[k]
                    if np.all(a <= mx + 0.05) and np.all(mn <= c_ + 0.05) and len(rzecz) < 40:
                        rzecz.add(k)
                        stos.append(k)
            zrobione |= rzecz
            dobre = None
            for du, dv in PRZESUNIECIA:
                proba = []
                for k in rzecz:
                    n = list(czesci[k])
                    n[2], n[4] = n[2] + du, n[4] + dv
                    proba.append(n)
                if any(not (u_lo <= n[2] <= u_hi) for n in proba):
                    continue
                if all(not Z.naruszenia(n, grupy[n[1]], tylko=ZASADY_RZECZY) for n in proba):
                    dobre = (du, dv)
                    break
            if dobre:
                for k in rzecz:
                    czesci[k][2] = round(czesci[k][2] + dobre[0], 3)
                    czesci[k][4] = round(czesci[k][4] + dobre[1], 3)
                odsuniete += 1
            else:
                usun |= rzecz
                usuniete += 1
        if usun:
            cz["czesci"] = [c for k, c in enumerate(czesci) if k not in usun]
        return odsuniete, usuniete, len(usun)
    finally:
        ZA.PLAC_R = stary_r


# ======================================================================================== plan i znaczniki
POLA_U = {"u", "u_od", "u_do", "przybycie_u", "woda"}
POLA_V = {"v", "otwarcie", "otwarcie_v", "mostek", "kamienie"}
POLA_UYV = {"punkt", "patrz_na", "srodek", "start"}
POLA_UV = {"patrz", "miejsce"}
POLA_SWIAT = {"punkt_swiat", "patrz_na_swiat", "miejsce_swiat", "arena_srodek_swiat", "wezly_swiat", "domy_swiat",
              "punkty_swiat", "srodek_swiat"}


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _r(x):
    return round(float(x), 2)


def _swiat(P, p):
    """Punkt świata [x, y, z] / [x, z], lista takich punktów albo słowniki z nimi (np. {t, poz, patrz})."""
    if isinstance(p, dict):
        return {k: (_swiat(P, v) if isinstance(v, (list, dict)) else v) for k, v in p.items()}
    if not isinstance(p, list):
        return p
    if len(p) in (2, 3) and all(_num(a) for a in p) and not P.w_pasie_x(p[0]):
        return p
    if len(p) == 3 and all(_num(a) for a in p):
        return [_r(P.x(p[0])), p[1], _r(P.z(p[2]))]
    if len(p) == 2 and all(_num(a) for a in p):
        return [_r(P.x(p[0])), _r(P.z(p[1]))]
    return [_swiat(P, q) for q in p]


def przeksztalc(obj, P, klucz=None, w_przelocie=False):
    if isinstance(obj, dict):
        wynik = {}
        for k, v in obj.items():
            wynik[k] = _pole(k, v, P, w_przelocie or k == "przelot_kamery")
        return wynik
    if isinstance(obj, list):
        return [przeksztalc(x, P, klucz, w_przelocie) for x in obj]
    return obj


def _pole(k, v, P, w_przelocie):
    if k in POLA_U:
        if _num(v):
            return _r(P.T(v))
        if isinstance(v, list) and all(_num(a) for a in v):
            return [_r(P.T(a)) for a in v]
    if k in POLA_V:
        if _num(v):
            return _r(P.g(v))
        if isinstance(v, list) and all(_num(a) for a in v):
            return [_r(P.g(a)) for a in v]
    if k == "zakres_czesci_u" and isinstance(v, list):
        return [_r(P.T(a)) for a in v]
    if k == "zakres_czesci_v" and isinstance(v, list):
        return [_r(P.g(a)) for a in v]
    if k == "niewidzialna_sciana_v" and _num(v):
        return _r(P.g(v))
    if k in POLA_SWIAT and isinstance(v, list):
        return _swiat(P, v)
    if k == "swiat_xz" and isinstance(v, list):
        return _swiat(P, v)
    if k == "swiat_x" and isinstance(v, list):
        return [_r(P.x(a)) for a in v]
    if k == "prostokat_swiat" and isinstance(v, dict):
        if not P.w_pasie_x(max(v["x"])):
            return v
        return {"x": [_r(P.x(a)) for a in v["x"]], "z": [_r(P.z(a)) for a in v["z"]]}
    if k in ("poz", "patrz") and w_przelocie and isinstance(v, list) and len(v) == 3:
        return [_r(P.T(v[0])), _r(P.g(v[1])), v[2]]          # przelot: [u, v, wysokość]
    if k in POLA_UYV and isinstance(v, list) and len(v) == 3 and all(_num(a) for a in v):
        return [_r(P.T(v[0])), v[1], _r(P.g(v[2]))]
    if k in POLA_UYV | POLA_UV and isinstance(v, list) and len(v) == 2 and all(_num(a) for a in v):
        return [_r(P.T(v[0])), _r(P.g(v[1]))]
    if k in ("wezly", "domy") and isinstance(v, list):
        return [[_r(P.T(p[0])), p[1], _r(P.g(p[2]))] for p in v]
    if k in ("trasa", "pts", "menhiry") and isinstance(v, list) and all(isinstance(p, list) and len(p) == 2 for p in v):
        return [[_r(P.T(p[0])), _r(P.g(p[1]))] for p in v]
    if k == "pole" and isinstance(v, list) and len(v) == 4:
        return [_r(P.T(v[0])), _r(P.T(v[1])), _r(P.g(v[2])), _r(P.g(v[3]))]
    return przeksztalc(v, P, k, w_przelocie)


def obwod(pts):
    return sum(math.hypot(pts[i][0] - pts[i - 1][0], pts[i][-1] - pts[i - 1][-1]) for i in range(len(pts)))


def _pojemnosc(st, rozmiary, odstep):
    """Ile potworów mieści pętla (te same zasady co generator gry: wataha = (miejsca − 1) × odstęp w grupie + odstęp)."""
    pts = st.get("trasa") or [[w[0], w[2]] for w in st.get("wezly", [])]
    L = obwod(pts)
    r = rozmiary.get(st["potwor"], {})
    wymiar = max(r.get("szer", r.get("dl", 3)), r.get("dl", r.get("szer", 3)))
    grupa = st.get("grupa") or {}
    watahy = grupa.get("watahy", 0) or 0
    if watahy > 0:
        miejsc = math.ceil(st["max"] / watahy)
        return L, watahy * ((miejsc - 1) * (wymiar + 5) + odstep) <= L + 1e-9
    return L, st["max"] * odstep <= L + 1e-9


def scal_strefy(dane, b, uwagi):
    """Zostają strefy z klucza „strefy” (pierwsza z każdej grupy) z poziomami całej grupy; max ≤ pojemność pętli."""
    if "strefy" not in dane:
        return
    po_id = {s["id"]: s for s in dane["strefy"]}
    rozm = dane.get("rozmiary", {})
    odstep = (dane.get("zasady") or {}).get("odstep_min", 25)
    nowe = []
    for sid, grupa in b["strefy"].items():
        st = copy.deepcopy(po_id[sid])
        for pole in ("poziomy", "poziomy_rowny"):
            if pole in st:
                lo = min(po_id[g][pole][0] for g in grupa)
                hi = max(po_id[g][pole][1] for g in grupa)
                st[pole] = [lo, hi]
        if len(grupa) > 1:
            st["scalone_z"] = grupa
        while True:
            L, ok = _pojemnosc(st, rozm, odstep)
            if ok or st["max"] <= 1:
                break
            st["max"] -= 1
            st["naraz"] = min(st["naraz"], max(1, st["max"] - 1))
            if (st.get("grupa") or {}).get("w_watasze"):
                st["grupa"]["w_watasze"] = math.ceil(st["max"] / st["grupa"]["watahy"])
        if "obwod" in st:
            st["obwod"] = round(L, 1)
        if "pojemnosc" in st:
            st["pojemnosc"] = int(L // odstep)
        if st["max"] != po_id[sid]["max"]:
            uwagi.append("%s: max %d → %d (pętla %.1f st)" % (sid, po_id[sid]["max"], st["max"], L))
        nowe.append(st)
    dane["strefy"] = nowe
    zostaja = set(b["strefy"])
    for q in dane.get("przegrody", []):
        if "strefy" in q:
            q["strefy"] = [s for s in q["strefy"] if s in zostaja]
        if q.get("pod"):
            pody = {s.get("pod") for s in nowe}
            q["pod"] = [p for p in q["pod"] if (p.get("id") if isinstance(p, dict) else p) in pody]


def _odl3(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


VMAX_PRZELOTU = 104.0     # st/s, gęsto próbkowana krzywa; kontrola planu i test gry dopuszczają 110


def _vmax_krzywej(punkty, krok=0.005):
    from swiat.biom_las.pas.sprawdz_plan import krzywa_kamery
    pr = krzywa_kamery(punkty, krok)
    return max((math.dist(a[1:], b[1:]) / (b[0] - a[0]) for a, b in zip(pr, pr[1:]) if b[0] > a[0]), default=0.0)


def przelot(dane, dawny):
    """Lot krótszy: wszystkie odcinki lotu skrócone JEDNYM współczynnikiem (proporcje czasu jak w projekcie, więc krzywa
    Catmull-Rom bez szarpnięć na punktach), najmniejszym, przy którym kamera nie przekracza VMAX_PRZELOTU;
    postój na Strażniku (od zatrzymanie_od_s) i ryk bez zmian."""
    k = dane.get("przelot_kamery")
    if not k:
        return
    z_od = k["zatrzymanie_od_s"]
    stare, nowe = dawny["punkty"], k["punkty"]

    def ustaw(F):
        t = [stare[0]["t"]]
        for i in range(1, len(stare)):
            dt = stare[i]["t"] - stare[i - 1]["t"]
            t.append(t[-1] + (dt * F if stare[i]["t"] <= z_od + 1e-9 else dt))
        for p, ti in zip(nowe, t):
            p["t"] = round(ti, 2)

    lo, hi = 0.05, 1.0
    ustaw(hi)
    if _vmax_krzywej(nowe) <= VMAX_PRZELOTU:
        for _ in range(30):
            sr = (lo + hi) / 2
            ustaw(sr)
            if _vmax_krzywej(nowe) <= VMAX_PRZELOTU:
                hi = sr
            else:
                lo = sr
    ustaw(hi)
    nowe_z = next((p["t"] for p, s in zip(nowe, stare) if abs(s["t"] - z_od) < 1e-9), round(z_od, 2))
    k["ryk_od_s"] = round(nowe_z + (dawny["ryk_od_s"] - z_od), 2)
    k["czas_s"] = round(nowe[-1]["t"], 2)
    k["zatrzymanie_od_s"] = nowe_z


def strumien(dane_dl, dane, P):
    """Punkty wczytywania mapy przed przelotem: z tekstu „u = a, b, c, d” planu → nowe u (też pole streaming_u)."""
    k = dane.get("przelot_kamery")
    if not k or "streaming" not in k:
        return
    import re
    m = re.search(r"u = ([\d, ]+)", dane_dl["przelot_kamery"]["streaming"])
    if not m:
        return
    stare = [int(x) for x in m.group(1).replace(" ", "").split(",") if x]
    nowe = [int(round(P.T(u))) for u in stare]
    k["streaming_u"] = nowe
    k["streaming"] = dane_dl["przelot_kamery"]["streaming"].replace(m.group(1).rstrip(", "), ", ".join(str(u) for u in nowe))


def zasady(dane, P, b, uwagi):
    z = dane.get("zasady")
    if not z:
        return
    o = P.biomy[b["id"]]
    s = min(o.f, P.h_nowe / P.h_dawne)
    if "plac_walki_r" in z:
        z["plac_walki_r"] = round(12 * s, 1)
    if "dom_od_wezlow" in z:
        z["dom_od_wezlow"] = [round(z["dom_od_wezlow"][0] * s, 1), z["dom_od_wezlow"][1]]
    uwagi.append("zasady: plac walki r %.1f, domy %.1f–%s st od węzłów (ściśnięcie %.3f)"
                 % (z.get("plac_walki_r", 0), z["dom_od_wezlow"][0], z["dom_od_wezlow"][1], s))


def rezerwacje(nowy, plan, W, uwagi):
    """Dalsze biomy (jeszcze bez map): każdy tej samej długości co krótki biom (bieg dlugosc_s + zapas przed przybyciem
    i za bramą, jak w projekcie: 940 − 920 = 20 st), jeden za drugim od końca ostatniego biomu z mapą."""
    kb = nowy.get("kolejne_biomy")
    if not kb:
        return
    L = W["dlugosc_s"] * W["bieg_st_s"] + W.get("zapas_rezerwacji_st", 20)
    z_mapa = {x["id"] for x in W["biomy"]}
    pop = None
    for n, s in zip(kb, plan["kolejne_biomy"]):
        if s["id"] in z_mapa:
            pop = n["u_do"]
            continue
        u_od = n["u_od"] if pop is None else pop
        n["u_od"], n["u_do"] = _r(u_od), _r(u_od + L)
        n["przybycie_u"] = _r(u_od + s["przybycie_u"] - s["u_od"])
        n["swiat_x"] = [_r(X0 + n["u_od"]), _r(X0 + n["u_do"])]
        pop = n["u_do"]
    dalsze = [n for n in kb if n["id"] not in z_mapa]
    if dalsze:
        uwagi.append("dalsze biomy bez map: po %d st każdy, pierwszy (%s) od u %s" % (L, dalsze[0]["id"], dalsze[0]["u_od"]))


def plan_krotki(plan, P, b, W):
    uwagi = []
    o = P.biomy[b["id"]]
    dl = copy.deepcopy(plan)
    nowy = przeksztalc(dl, P)
    rezerwacje(nowy, plan, W, uwagi)
    scal_strefy(nowy, b, uwagi)
    nowy["punkty_orientacyjne"] = [x for x, s in zip(nowy.get("punkty_orientacyjne", []), plan.get("punkty_orientacyjne", []))
                                   if P.zostaje(s["u"])] if "punkty_orientacyjne" in nowy else []
    # przelot: tor w długim pasie od pierwszego do ostatniego punktu lotu → w krótkim
    k0 = plan.get("przelot_kamery")
    if k0:
        lot = [p for p in k0["punkty"] if p["t"] <= k0["zatrzymanie_od_s"] + 1e-9]
        dl_dawna = sum(math.hypot(b2["poz"][0] - a2["poz"][0], b2["poz"][1] - a2["poz"][1]) for a2, b2 in zip(lot, lot[1:]))
        lotn = [p for p in nowy["przelot_kamery"]["punkty"] if p["t"] <= k0["zatrzymanie_od_s"] + 1e-9]
        dl_nowa = sum(math.hypot(b2["poz"][0] - a2["poz"][0], b2["poz"][1] - a2["poz"][1]) for a2, b2 in zip(lotn, lotn[1:]))
        przelot(nowy, k0)
        strumien(plan, nowy, P)
        uwagi.append("przelot: tor %.0f → %.0f st, lot %.1f → %.1f s, całość %.1f s" % (
            dl_dawna, dl_nowa, k0["zatrzymanie_od_s"], nowy["przelot_kamery"]["zatrzymanie_od_s"],
            nowy["przelot_kamery"]["czas_s"]))
    zasady(nowy, P, b, uwagi)
    if "pas" in nowy:
        if "szerokosc" in nowy["pas"]:
            nowy["pas"]["szerokosc"] = int(round(2 * P.h_nowe))
        if "szerokosc_s" in nowy["pas"]:
            nowy["pas"]["szerokosc_s"] = W["szerokosc_s"]
    nowy["wymiary"] = {
        "decyzja": "D-096 (Karol, 17.11.2026)", "zrodlo": "swiat/biomy/wymiary_pasa.json",
        "projekt": b["plan"], "dlugosc_s": W["dlugosc_s"], "szerokosc_s": W["szerokosc_s"], "bieg_st_s": W["bieg_st_s"],
        "wspolczynnik_wzdluz": round(o.f, 4),
        "wspolczynnik_w_poprzek": round((P.h_nowe - P.rdzen) / (P.h_dawne - P.rdzen), 4), "rdzen_v_st": P.rdzen,
        "zostawione_odcinki_u": [list(s) for s in o.seg], "uwagi": uwagi,
        "przybycie_do_bramy_st": round(o.T(o.brama) - o.T(o.kotwica), 2),
    }
    return nowy, uwagi


def znaczniki_krotkie(zn, P, b, W, plan_nowy, czesci_nowe):
    nowy = przeksztalc(copy.deepcopy(zn), P)
    uw = []
    scal_strefy(nowy, b, uw)
    if "punkty_orientacyjne" in nowy:
        nowy["punkty_orientacyjne"] = [x for x, s in zip(nowy["punkty_orientacyjne"], zn["punkty_orientacyjne"])
                                       if P.zostaje(s["u"])]
    if "przelot_kamery" in nowy:
        nowy["przelot_kamery"] = copy.deepcopy(plan_nowy["przelot_kamery"])
        if "punkty_swiat" in zn.get("przelot_kamery", {}):
            nowy["przelot_kamery"]["punkty_swiat"] = [
                {"t": p["t"], "poz": [_r(X0 + p["poz"][0]), p["poz"][2], _r(Z0 + p["poz"][1])],
                 "patrz": [_r(X0 + p["patrz"][0]), p["patrz"][2], _r(Z0 + p["patrz"][1])]}
                for p in plan_nowy["przelot_kamery"]["punkty"]]
    if "pas" in nowy:
        nowy["pas"]["szerokosc"] = int(round(2 * P.h_nowe))
    for k in ("grupy_stale_wczytane", "grupy_niski_detal"):
        if k in nowy:
            grupy = {g.split("/", 2)[-1] for g in czesci_nowe["grupy"]}
            uzywane = {czesci_nowe["grupy"][c[1]].split("/", 2)[-1] for c in czesci_nowe["czesci"]}
            nowy[k]["grupy"] = [g for g in nowy[k]["grupy"] if g in grupy and any(
                u == g or u.startswith(g + "/") for u in uzywane)]
    if "statystyka" in nowy:
        nowy["statystyka"] = {"czesci": len(czesci_nowe["czesci"]),
                              "uwaga": "mapa przycięta przez swiat/biomy/przycinarka.py (D-096) — liczby na odcinek: projekt"}
    if "sasiad_las" in nowy:
        nowy["sasiad_las"]["usun_przed_budowa"] = "(nie dotyczy: krótki las nie ma zapowiedzi Bagna)"
    nowy["wymiary"] = plan_nowy["wymiary"]
    nowy["plan"] = "%s/%s" % (b["wyj"], b["plik_planu"])
    return nowy


# ======================================================================================== całość
def tekst(d, zwarty=False):
    if zwarty:
        return json.dumps(d, ensure_ascii=False, separators=(",", ":")) + "\n"
    return json.dumps(d, ensure_ascii=False, indent=1) + "\n"


def wszystko(W=None):
    W = W or _json(PLIK_WYMIAROW)
    P = Przeksztalcenie(W)
    pliki, raport = {}, []
    for b, o in P.kolejnosc:
        plan = _json(b["plan"])
        d = _json(b["czesci"])
        zn = _json(b["znaczniki"])
        pl, uw = plan_krotki(plan, P, b, W)
        cz, licz = czesci_krotkie(d, P, b.get("pomin_grupy", []))
        licz["odsuniete"], licz["usuniete_rzeczy"], licz["usuniete_bryly"] = popraw_rzeczy(cz, pl, P, b)
        licz["po"] = len(cz["czesci"])
        uw.append("drobiazgi przy placach walki, otwarciach i pętlach: odsunięte %d, usunięte %d (%d brył)"
                  % (licz["odsuniete"], licz["usuniete_rzeczy"], licz["usuniete_bryly"]))
        pl["wymiary"]["uwagi"] = uw
        z = znaczniki_krotkie(zn, P, b, W, pl, cz)
        wyj = b["wyj"]
        pliki[os.path.join(REPO, wyj, "czesci.json")] = tekst(cz, zwarty=True)
        pliki[os.path.join(REPO, wyj, "znaczniki.json")] = tekst(z)
        pliki[os.path.join(REPO, wyj, b["plik_planu"])] = tekst(pl)
        raport.append({"biom": b["id"], "czesci": licz, "f": o.f, "kotwica": o.T(o.kotwica), "brama": o.T(o.brama),
                       "pas": (o.T(o.seg[0][0]), o.T(o.seg[-1][1])), "uwagi": uw,
                       "przed": (b["kotwica_u"], b["brama_u"]), "strefy": [(s["id"], s["poziomy"], s["naraz"], s["max"])
                                                                          for s in pl["strefy"]]})
    return P, pliki, raport


def drukuj(P, raport, W):
    bieg = W["bieg_st_s"]
    print("Wymiary (swiat/biomy/wymiary_pasa.json): %s s długości, %s s szerokości przy %s st/s → %d st i %d st"
          % (W["dlugosc_s"], W["szerokosc_s"], bieg, W["dlugosc_s"] * bieg, W["szerokosc_s"] * bieg))
    for r in raport:
        kp, bp = r["przed"]
        print("%-6s przybycie→brama: %.0f st (%.1f s) → %.0f st (%.1f s); świat X %.0f…%.0f (było %.0f…%.0f); "
              "ściśnięcie %.3f; części %d → %d (odrzucone %d, przycięte %d)" % (
                  r["biom"], bp - kp, (bp - kp) / bieg, r["brama"] - r["kotwica"], (r["brama"] - r["kotwica"]) / bieg,
                  X0 + r["pas"][0], X0 + r["pas"][1], X0 + P.biomy[r["biom"]].seg[0][0], X0 + P.biomy[r["biom"]].seg[-1][1],
                  r["f"], r["czesci"]["przed"], r["czesci"]["po"], r["czesci"]["odrzucone"], r["czesci"]["przyciete"]))
        print("       strefy: " + "; ".join("%s poz. %d–%d naraz %d max %d" % (s[0], s[1][0], s[1][1], s[2], s[3])
                                           for s in r["strefy"]))
        for u in r["uwagi"]:
            print("       " + u)
    print("dalsze biomy przesunięte o %.0f st (brama do Dżungli X %.0f)" % (P.przesuniecie_dalej, X0 + P.T(1874)))


def podglad(wyj, P):
    """Rzut z góry „przed / po” w jednej skali: las + Bagno (projekt) obok krótkich map."""
    from PIL import Image, ImageDraw
    from swiat.las_pas import podglad as RYS
    os.makedirs(wyj, exist_ok=True)
    skala, v0, v1 = 0.9, -90.0, 90.0
    u0, u1 = -40.0, 1910.0
    obrazy = []
    for etykieta, pliki in (("PRZED (projekt)", ("swiat/las_pas/czesci.json", "swiat/bagno_pas/czesci.json")),
                            ("PO (D-096)", ("swiat/las_pas/krotki/czesci.json", "swiat/bagno_pas/krotki/czesci.json"))):
        sciany = []
        for p in pliki:
            sciany += RYS.wczytaj(os.path.join(REPO, p))[1]
        img, _ = RYS.kadr_gora(sciany, skala=skala, u0=u0, u1=u1, v0=v0, v1=v1)
        img = img.rotate(-90, expand=True)              # pas poziomo: przybycie lasu z lewej, Bagno z prawej
        ImageDraw.Draw(img).text((6, 4), etykieta, fill=(255, 255, 255))
        obrazy.append(img)
    W = max(i.size[0] for i in obrazy)
    H = sum(i.size[1] for i in obrazy) + 12
    calosc = Image.new("RGB", (W, H), (255, 255, 255))
    y = 0
    for i in obrazy:
        calosc.paste(i, (0, y))
        y += i.size[1] + 12
    sciezka = os.path.join(wyj, "pas_przed_po.jpg")
    calosc.save(sciezka, quality=85)
    return sciezka


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Krótkie mapy biomów z długich projektów (D-096)")
    ap.add_argument("--sprawdz", action="store_true")
    ap.add_argument("--podglad", default="")
    a = ap.parse_args()
    W = _json(PLIK_WYMIAROW)
    P, pliki, raport = wszystko(W)
    if a.sprawdz:
        zle = []
        for sciezka, t in pliki.items():
            try:
                with open(sciezka, encoding="utf-8", newline="") as f:
                    if f.read() != t:
                        zle.append(os.path.relpath(sciezka, REPO))
            except OSError:
                zle.append(os.path.relpath(sciezka, REPO))
        if zle:
            print("NIEAKTUALNE: %s — uruchom python -B swiat/biomy/przycinarka.py" % ", ".join(zle))
            sys.exit(1)
        print("krótkie mapy aktualne (%d plików)" % len(pliki))
        return
    for sciezka, t in pliki.items():
        os.makedirs(os.path.dirname(sciezka), exist_ok=True)
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            f.write(t)
    drukuj(P, raport, W)
    if a.podglad:
        print("podgląd:", podglad(a.podglad, P))


if __name__ == "__main__":
    main()
