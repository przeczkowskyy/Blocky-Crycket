# -*- coding: utf-8 -*-
"""Wolna przestrzeń kamer walki — liczona z DANYCH UJĘĆ odtwarzacza, nie zgadywana.

Port wzorów kamery z swiat/test_walki2/zrodla/OdtwarzaczWalki2.luau (Sesja:ujecieSurowe, Sesja:twarzPotwora,
Sesja:parametryObjazdu, Sesja:ujecie „pokonany”, Sesja:ustawAktorow) na wymiarach aktorów z swiat/test_walki2/dane
(aktorzy.py). Układ SCENY jak w odtwarzaczu: X wzdłuż walki (gracz −S/2, przeciwnik +S/2), Y w górę od płyty placu,
Z ku kamerze planu ogólnego (strona „widowni”); −Z to tło większości ujęć.

Dla każdej pary (klasa × każdy przeciwnik i lustro) i każdego rodzaju ujęcia (ogólny, z boku, zza atakującego,
zza broniącego, zbliżenie, krytyk ze skokiem, lot pocisku z obu stron, umiejętność na siebie, efekt, pokonany,
objazd 20°–142°) liczymy położenia kamery na początku, w połowie i na końcu ujęcia, a dla ujęć z poprawką „twarz
potwora” — wszystkie 36 kandydatów (obrót 100…0% × odjazd 1,0…1,8). Wolna przestrzeń = kamery (kula ZAPAS_KAMERY)
+ odcinki widoku od kamery do celu i do punktów obu postaci (0,25 / 0,6 / 1,0 wysokości).

Zapis: profil biegunowy wokół środka placu — dla przedziału kąta (KROK_KATA°) i pasma wysokości (KROK_Y) największy
promień, do którego sięga wolna przestrzeń. Bryła areny łamie zasadę, gdy któryś jej punkt leży bliżej środka niż
ten promień (z sąsiednimi przedziałami i zapasem) — sprawdz.py.

Uwaga: odtwarzacz nie omija brył otoczenia (nie ma promieni do sceny), więc tę zasadę trzyma sama arena.
"""
import json
import math
import os
import sys

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
WALKA2 = os.path.join(REPO, "swiat", "test_walki2")
for _s in (REPO, WALKA2):
    if _s not in sys.path:
        sys.path.insert(0, _s)

KROK_KATA = 3.0            # stopnie na przedział profilu
KROK_Y = 0.5               # studs na pasmo wysokości
Y_MAKS = 40.0              # profil do tej wysokości nad placem
ZAPAS_KAMERY = 1.6         # kula wokół kamery (płaszczyzna bliska, wstrząs, wygładzanie)
TWARZ_R = (1, 0.85, 0.7, 0.5, 0.25, 0)
TWARZ_F = (1, 1.12, 1.25, 1.4, 1.6, 1.8)
MAKS_KAT_TWARZY = 56.0
DUZY = 8.0
ODKRYTE_U_GORY = 0.56
SKOK = 4.5                 # Choreografie: uderzenie_z_gory.wysokosc
ZAMACH = 3.5               # Choreografie: miazdzacy_cios.zamach


def rad(x):
    return math.radians(x)


def wyjscie(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) * (1 - x)


# --------------------------------------------------------------------------- aktorzy (z danych prototypu walki)
def aktorzy():
    """{klucz: {rola, h, szer, gleb, przod, lezy}} z swiat/test_walki2/dane (te same liczby, które dostaje odtwarzacz)."""
    import aktorzy as A
    wynik = {}
    for w in A.AKTORZY:
        d = A.wczytaj(w["klucz"])
        wym = d["wymiary"]
        wynik[w["klucz"]] = {"rola": w["rola"], "h": wym["wysokosc"], "szer": wym["szerokosc"], "gleb": wym["glebokosc"],
                             "przod": wym["przod"], "lezy": _lezy(d)}
    return wynik


# Aktorzy SZACUNKOWI (zapas), dopóki prawdziwych danych nie ma w swiat/test_walki2/dane: wysokość z PLAN_BIOMOW
# (swiat/biomy/PLAN_BIOMOW.md), szerokość, głębokość i przód z proporcji podobnych potworów (z zapasem w górę).
# Gdy w tabeli aktorów pojawi się wpis o tym kluczu, profil liczy się z prawdziwych wymiarów (inny odcisk → od nowa).
ZAPASOWI = {
    # Dżungla (18.11): ostateczne klucze; od 18.11 wszystkie mają prawdziwe dane, te liczby są tylko zapasem
    "zwijogon": {"rola": "przeciwnik", "h": 3.6, "szer": 3.0, "gleb": 5.8, "przod": 3.0, "lezy": None},
    "gebokwiat": {"rola": "przeciwnik", "h": 5.2, "szer": 3.8, "gleb": 2.0, "przod": 1.0, "lezy": None},
    "kokosowy_silacz": {"rola": "przeciwnik", "h": 7.2, "szer": 6.6, "gleb": 3.2, "przod": 2.0, "lezy": None},
    "pancernik_ruin": {"rola": "przeciwnik", "h": 4.5, "szer": 4.0, "gleb": 7.8, "przod": 4.1, "lezy": None},
    "waz_stu_lian": {"rola": "przeciwnik", "h": 17.5, "szer": 11.2, "gleb": 12.5, "przod": 6.0, "lezy": None},
}


def aktorzy_do_profilu(przeciwnicy=None, akt=None):
    """Klasy + wskazani przeciwnicy (prawdziwi z tabeli aktorów, a gdy ich jeszcze nie ma — szacunkowi z ZAPASOWI).
    przeciwnicy = None → wszyscy prawdziwi aktorzy (jak dotąd)."""
    akt = akt or aktorzy()
    if przeciwnicy is None:
        return akt
    wynik = {k: a for k, a in akt.items() if a["rola"] == "klasa"}
    for k in przeciwnicy:
        if k in akt:
            wynik[k] = akt[k]
        elif k in ZAPASOWI:
            wynik[k] = dict(ZAPASOWI[k], zapas=True)
        else:
            raise KeyError("nieznany przeciwnik %r (ani w tabeli aktorów, ani w ZAPASOWI)" % k)
    return wynik


def _lezy(d):
    """Obwiednia ostatniej klatki klipu „upadek” (jak zbuduj.obwiednia_lezenia) — kadr ujęcia pokonanego."""
    try:
        from geometria import Rig, obwiednia
        r = Rig(d)
        klip = next((k for k in d["klipy"] if k["n"] == "upadek"), None)
        if not klip:
            return None
        mn, mx = obwiednia(r, r.pozy(r.transformy("upadek", klip["dl"])))
        return {"mn": list(mn), "mx": list(mx)}
    except Exception:
        return None


# --------------------------------------------------------------------------- geometria walki (Sesja:ustawAktorow)
def geometria(G, W):
    S = max(9.5, G["przod"] + W["przod"] + 3.2)
    geo = {"S": S, "x": {"gracz": -S / 2, "wrog": S / 2}, "kier": {"gracz": 1, "wrog": -1},
           "h": {"gracz": G["h"], "wrog": W["h"]},
           "w": {"gracz": max(G["szer"], G["gleb"] * 0.6), "wrog": max(W["szer"], W["gleb"] * 0.6)},
           "akt": {"gracz": G, "wrog": W}}
    geo["H"] = max(G["h"], W["h"])
    pol = S / 2 + max(G["przod"], W["przod"]) * 0.8 + 2.2
    geo["dist"] = max(pol / (math.tan(rad(20)) * 16 / 9), (geo["H"] * 0.72 + 1.8) / math.tan(rad(20)), 12)
    return geo


def odl_dla_wys(h, kat, szer=None):
    t = math.tan(rad(kat / 2))
    s = szer or 0
    return max((h * 0.62 + 1.1) / t, (s * 0.62 + 1.4) / (t * 16 / 9) + s * 0.35)


def odl_dla_pary(lo, hi, gora, kat, zapas=1.0):
    t = math.tan(rad(kat / 2))
    pw = (hi - lo) * 0.5 + 1.0 * zapas
    ph = gora * 0.5 * (1 + 0.32 * zapas) + 0.8 * zapas
    return max(ph / t, pw / (t * 16 / 9))


def odl_dla_gory(gora, srodek_y, kat):
    return (gora + 0.4 - srodek_y) / (ODKRYTE_U_GORY * math.tan(rad(kat / 2)))


def inna(s):
    return "wrog" if s == "gracz" else "gracz"


def obrys_pary(g, A, D, dodatek=0.0):
    lo, hi, gora = 1e9, -1e9, 0.0
    for s in (A, D):
        pol = g["w"][s] * 0.5 + 0.3
        lo = min(lo, g["x"][s] - pol)
        hi = max(hi, g["x"][s] + pol)
        gora = max(gora, g["h"][s] + (dodatek if s == A else 0.0))
    return lo, hi, gora


# --------------------------------------------------------------------------- ujęcia (Sesja:ujecieSurowe)
def ujecie(g, typ, A, D, k, strona=1, gora_plus=0.0, skok=False):
    """(pozycja, cel, kąt) w układzie sceny albo None. k = postęp ujęcia (0…1, po wygładzeniu)."""
    xA, xD = g["x"][A], g["x"][D]
    hA, hD = g["h"][A], g["h"][D]
    wA, wD = g["w"][A], g["w"][D]
    S = g["S"]
    d_ = 1 if xD > xA else -1
    if typ == "zaAtakujacym" and A == "wrog":
        typ = "zaBroniacym"
    elif typ == "zaBroniacym" and D == "wrog":
        typ = "zaAtakujacym"
    roznica = max(hA, hD) / max(min(hA, hD), 0.5)
    if (typ == "zaAtakujacym" and hA > 1.3 * hD + 0.5) or (typ == "zaBroniacym" and hD > 1.3 * hA + 0.5) \
            or (typ in ("zaAtakujacym", "zaBroniacym") and roznica > 1.8):
        typ = "boczny"
    olbrzym = hA > 1.8 * hD + 0.5
    if typ == "zblizenie" and olbrzym:
        typ = "boczny"
    if typ == "ogolny":
        dryf = strona * S * 0.06
        return (dryf, g["H"] * 0.42 + 1.6, g["dist"] * (1.06 - 0.06 * k)), (dryf * 0.5, g["H"] * 0.46, 0.0), 40.0, typ
    if typ == "boczny":
        lo, hi, gora = obrys_pary(g, A, D, gora_plus)
        d = max(odl_dla_wys(g["H"], 42) * 1.02, S * 1.05, odl_dla_pary(lo, hi, gora, 42) + 0.4 * max(wA, wD))
        if gora > DUZY:
            d = max(d, odl_dla_gory(gora, gora * 0.5, 42))
        sr = (lo + hi) / 2
        st = -1 if (olbrzym or A == "wrog") else 1
        xk, xc = sr - d_ * st * (S * 0.32 + 0.6 * k), sr + d_ * st * S * 0.08
        tan_pol = math.tan(rad(21)) * 16 / 9 * 0.86
        for _ in range(10):
            z = d - 0.8 * k
            skret = math.atan2(xc - xk, z)
            if all(abs(math.tan(math.atan2(x - xk, z) - skret)) <= tan_pol for x in (lo, hi)):
                break
            d *= 1.07
        return (xk, gora * 0.4 + 1.2, d - 0.8 * k), (xc, gora * 0.5, 0.0), 42.0, typ
    if typ == "zaAtakujacym":
        return ((xA - d_ * (2.4 + 0.4 * hA) + d_ * 0.6 * k, 0.5 * hA + 0.25 * hD + 1.0, 3.0 + 0.65 * hA + 0.3 * hD + 0.4 * wA - 0.3 * k),
                (xD - d_ * 0.5, 0.5 * hD, 0.0), 50.0, typ)
    if typ == "zaBroniacym":
        return ((xD + d_ * (2.4 + 0.4 * hD) - d_ * 0.5 * k, 0.5 * hD + 0.25 * hA + 1.0, 3.0 + 0.65 * hD + 0.3 * hA + 0.4 * wD - 0.3 * k),
                (xA + d_ * 0.6, 0.5 * hA, 0.0), 50.0, typ)
    if typ == "zblizenie":
        d = odl_dla_wys(hD, 44, wD) * 0.95
        if hD > DUZY:
            d = max(d, odl_dla_gory(hD, 0.5 * hD, 44) / 0.94)
        return (xD - d_ * d * 0.35, 0.55 * hD + 0.6, d * 0.94 - 0.5 * k), (xD - d_ * 0.6, 0.5 * hD, 0.0), 44.0, typ
    if typ == "krytyk":
        lo, hi, gora = obrys_pary(g, A, D, gora_plus)
        gora = max(gora, max(hA, hD))
        d = odl_dla_pary(lo, hi, gora, 52) + 0.4 * max(wA, wD)
        sr = (lo + hi) / 2
        ycel = 0.46 * gora
        if gora > DUZY:
            ycel = 0.5 * gora
            d = max(d, odl_dla_gory(gora, ycel, 52))
        ykam = 0.28 * gora + 0.8
        if skok:
            ykam = max(ykam, max(hA, hD) + 1.6)
        return (sr - d_ * 0.4 * k, ykam, d), (sr + d_ * 0.04 * (hi - lo) * k, ycel, 0.0), 46.0, typ
    if typ == "pocisk":
        s = strona
        pos0 = [xA - d_ * (4.5 + 0.6 * hA + 0.3 * wA), 0.72 * hA + 1.4, s * (3.2 + 0.55 * hA + 0.5 * wA)]
        cel0 = (xD - d_ * 0.3, 0.42 * hD + 0.3, 0.0)
        dcel, datak = abs(cel0[0] - pos0[0]), abs(xA - pos0[0])
        if dcel > datak + 0.5:
            r = wA * 0.5 + wD * 0.3 + 0.7
            potrzeba = r * dcel / (dcel - datak)
            if abs(pos0[2]) < potrzeba:
                pos0[2] = s * potrzeba
        lo, hi, gora = obrys_pary(g, A, D, gora_plus)
        d1 = odl_dla_pary(lo, hi, gora, 48) + 0.4 * max(wA, wD)
        c1 = (lo + hi) / 2
        pos1 = (c1 - d_ * S * 0.3, gora * 0.42 + 1.0, s * d1)
        cel1 = (c1 + d_ * S * 0.06, gora * 0.45, 0.0)
        p = tuple(pos0[i] + (pos1[i] - pos0[i]) * k for i in range(3))
        c = tuple(cel0[i] + (cel1[i] - cel0[i]) * k for i in range(3))
        return p, c, 48.0, typ
    if typ == "naSiebie":
        f = g["kier"][A]
        d = odl_dla_wys(hA, 42, wA) * 1.05
        if hA > DUZY:
            d = max(d, odl_dla_gory(hA, 0.5 * hA, 42) / 0.88)
        return (xA + f * d * 0.45, 0.55 * hA + 0.5, d * 0.88 - 0.6 * k), (xA + f * 0.3, 0.5 * hA, 0.0), 42.0, typ
    if typ == "efekt":
        f = g["kier"][A]
        d = odl_dla_wys(hA, 44, wA) * 1.15
        if hA > DUZY:
            d = max(d, odl_dla_gory(hA, 0.48 * hA, 44) / 0.9)
        return (xA + f * d * 0.4, 0.6 * hA + 0.8, d * 0.9 - 0.5 * k), (xA + f * 0.4, 0.48 * hA, 0.0), 44.0, typ
    raise ValueError(typ)


def lezacy(g, P):
    """Prostokąt leżącego pokonanego (Sesja:lezacy) w układzie sceny: (x0, x1, z0, z1, wys)."""
    k = g["kier"][P]
    x = g["x"][P]
    lz = g["akt"][P]["lezy"]
    if lz:
        xa, xb = x - k * lz["mn"][2], x - k * lz["mx"][2]
        za, zb = k * lz["mn"][0], k * lz["mx"][0]
        return min(xa, xb), max(xa, xb), min(za, zb), max(za, zb), max(lz["mx"][1], 0.8)
    r = max(g["w"][P], g["h"][P] * 0.5)
    return x - r, x + r, -r, r, g["h"][P] * 0.5


def ujecie_pokonanego(g, P, k, u0):
    kP = g["kier"][P]
    x0, x1, z0, z1, hl = lezacy(g, P)
    c = ((x0 + x1) / 2, g["h"][P] * 0.42 * (1 - u0) + hl * 0.3 * u0, (z0 + z1) / 2)
    rozp = max(x1 - x0, z1 - z0) * 0.5
    wys = max(hl, g["h"][P] * 0.8 * (1 - u0))
    t = math.tan(rad(22))
    d = max(7, ((rozp * 1.2 + 1.0) / (t * 16 / 9) + rozp * 0.5) * 1.3, (wys * 0.9 + 1.2) / t)
    d *= 1.08 - 0.08 * k
    a, e = rad(62), rad(30)
    u = (kP * math.cos(a), 0.0, math.sin(a))
    poz = (c[0] + u[0] * d * math.cos(e), c[1] + d * math.sin(e), c[2] + u[2] * d * math.cos(e))
    return poz, c


def objazd(g, zw):
    """Kamery objazdu zwycięzcy dla kątów 20°…142° (zakres, w którym może się znaleźć przy każdym leżącym)."""
    hZ = g["h"][zw]
    R = 1.25 * hZ + 6.5
    prz = 0.32
    if hZ > DUZY:
        R = max(R, odl_dla_gory(hZ, 0.5 * hZ, 44)) * 1.15
        prz = 0.2
    znak = g["kier"][zw]
    W = (g["x"][zw], 0.0, 0.0)
    cel = (W[0] + znak * R * prz, hZ * 0.5, 0.0)
    wynik = []
    for kat in range(20, 144, 4):
        a = rad(kat)
        wynik.append(((W[0] + znak * R * math.cos(a), hZ * 0.55 + 1.6, R * math.sin(a)), cel))
    return wynik


# --------------------------------------------------------------------------- twarz potwora (Sesja:twarzPotwora)
def kat_twarzy(g, poz):
    pM = (g["x"]["wrog"], 0.0)
    f = (-1.0, 0.0)                                    # potwór patrzy na gracza (kier wrog = −1)
    vx, vz = poz[0] - pM[0], poz[2] - pM[1]
    n = math.hypot(vx, vz)
    if n < 1e-3:
        return 0.0
    return math.degrees(math.acos(max(-1.0, min(1.0, (vx * f[0] + vz * f[1]) / n))))


def twarz(g, poz, cel):
    """Wszyscy kandydaci kamery po poprawce „twarz potwora” (36 położeń)."""
    rx, rz = poz[0] - cel[0], poz[2] - cel[2]

    def obroc(a):
        c, s = math.cos(a), math.sin(a)
        return (cel[0] + rx * c - rz * s, poz[1], cel[2] + rx * s + rz * c)
    krok = rad(2)
    znak = 1 if kat_twarzy(g, obroc(krok)) < kat_twarzy(g, obroc(-krok)) else -1
    phi = 0.0
    if kat_twarzy(g, poz) > MAKS_KAT_TWARZY:
        for i in range(1, 61):
            phi = znak * krok * i
            if kat_twarzy(g, obroc(phi)) <= MAKS_KAT_TWARZY:
                break
    wynik = []
    for r in TWARZ_R:
        p = obroc(phi * r)
        for f in TWARZ_F:
            wynik.append(tuple(cel[i] + (p[i] - cel[i]) * f for i in range(3)))
    return wynik


# --------------------------------------------------------------------------- wszystkie kamery jednej pary
def kamery_pary(G, W):
    """Lista (pozycja kamery, [punkty, na które kamera patrzy]) dla jednej pary aktorów."""
    g = geometria(G, W)
    cele_postaci = []
    for s in ("gracz", "wrog"):
        for u in (0.25, 0.6, 1.0):
            cele_postaci.append((g["x"][s], g["h"][s] * u, 0.0))
    wynik = []
    proste = []
    for typ in ("ogolny", "boczny", "zaAtakujacym", "zaBroniacym", "zblizenie", "krytyk", "pocisk", "naSiebie", "efekt"):
        for A in ("gracz", "wrog"):
            D = inna(A)
            for k in (0.0, 0.5, 1.0):
                warianty = [(1, 0.0, False)]
                if typ in ("ogolny", "pocisk"):
                    warianty = [(1, 0.0, False), (-1, 0.0, False)]
                if typ in ("boczny", "krytyk"):
                    warianty += [(1, SKOK, True), (1, ZAMACH, False)]
                for strona, plus, skok in warianty:
                    poz, cel, kat, typ2 = ujecie(g, typ, A, D, k, strona, plus, skok)
                    tylko_gracz = typ2 in ("naSiebie", "efekt") and A == "gracz"
                    proste.append((typ2, poz, cel, tylko_gracz))
    for typ2, poz, cel, tylko_gracz in proste:
        if tylko_gracz:
            wynik.append((poz, [cel] + cele_postaci[:3]))
        else:
            for q in twarz(g, poz, cel):
                wynik.append((q, [cel] + cele_postaci))
    for P in ("gracz", "wrog"):
        for k in (0.0, 1.0):
            for u0 in (0.0, 1.0):
                poz, cel = ujecie_pokonanego(g, P, k, u0)
                wynik.append((poz, [cel]))
        for poz, cel in objazd(g, inna(P)):
            wynik.append((poz, [cel] + cele_postaci))
    return wynik


def pary(akt):
    klasy = [k for k, a in akt.items() if a["rola"] == "klasa"]
    wrogowie = [k for k, a in akt.items() if a["rola"] == "przeciwnik"] + klasy     # lustro: ta sama klasa
    return [(g, w) for g in klasy for w in wrogowie]


# --------------------------------------------------------------------------- profil biegunowy (numpy)
class Profil:
    """r[i_kata, i_y] = największy promień wolnej przestrzeni w przedziale kąta (od osi +X ku +Z) i paśmie wysokości."""

    def __init__(self, krok_kata=KROK_KATA, krok_y=KROK_Y, y_maks=Y_MAKS):
        import numpy as np
        self.kk, self.ky, self.ym = float(krok_kata), float(krok_y), float(y_maks)
        self.nk = int(round(360.0 / self.kk))
        self.ny = int(math.ceil(self.ym / self.ky)) + 1
        self.r = np.zeros((self.nk, self.ny))
        self.y_max_kamery = 0.0
        self.r_max_kamery = 0.0
        self.kamer = 0

    def indeksy(self, x, z, y):
        import numpy as np
        a = np.degrees(np.arctan2(z, x)) % 360.0
        ik = (a / self.kk).astype(int) % self.nk
        iy = np.clip(np.floor(np.maximum(y, 0.0) / self.ky).astype(int), 0, self.ny - 1)
        return ik, iy

    def dodaj_punkty(self, P):
        """P: tablica (n, 3) punktów sceny, które muszą być wolne."""
        import numpy as np
        P = np.asarray(P, float)
        P = P[P[:, 1] <= self.ym]
        if not len(P):
            return
        ik, iy = self.indeksy(P[:, 0], P[:, 2], P[:, 1])
        np.maximum.at(self.r, (ik, iy), np.hypot(P[:, 0], P[:, 2]))

    def dodaj_kamery(self, kamery, krok=0.35):
        """kamery: lista (pozycja, [cele]). Kula ZAPAS_KAMERY wokół kamery + odcinki do celów (próbki co `krok`)."""
        import numpy as np
        kule = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    v = np.array((dx, dy, dz), float)
                    n = np.linalg.norm(v)
                    kule.append(v / n * ZAPAS_KAMERY if n else v)
        kule = np.array(kule)
        A, B = [], []
        for poz, cele in kamery:
            self.kamer += 1
            self.y_max_kamery = max(self.y_max_kamery, poz[1])
            self.r_max_kamery = max(self.r_max_kamery, math.hypot(poz[0], poz[2]))
            for c in cele:
                A.append(poz)
                B.append(c)
        A, B = np.array(A, float), np.array(B, float)
        self.dodaj_punkty((np.array([k[0] for k in kamery], float)[:, None, :] + kule[None, :, :]).reshape(-1, 3))
        dl = np.linalg.norm(B - A, axis=1)
        nmax = int(np.ceil(dl.max() / krok)) + 1
        for i in range(0, len(A), 4000):                       # paczkami (pamięć)
            a, b, d = A[i:i + 4000], B[i:i + 4000], dl[i:i + 4000]
            t = np.linspace(0.0, 1.0, nmax)[None, :, None]
            P = a[:, None, :] + (b - a)[:, None, :] * t
            m = (t[0, :, 0][None, :] * d[:, None]) <= d[:, None] + krok   # wszystkie próbki ważne (odcinek do końca)
            self.dodaj_punkty(P[m].reshape(-1, 3))

    def rozszerz(self, sasiedzi_kata=1):
        """Maksimum z sąsiednich przedziałów kąta (odcinek między próbkami nie wypada z profilu)."""
        import numpy as np
        r = self.r.copy()
        for d in range(1, sasiedzi_kata + 1):
            r = np.maximum(r, np.maximum(np.roll(self.r, d, axis=0), np.roll(self.r, -d, axis=0)))
        self.r = r

    def promien(self, x, z, y):
        """Promień wolnej przestrzeni w kierunku (x, z) na wysokości y (tablice albo liczby); 0 nad profilem."""
        import numpy as np
        x, z, y = np.asarray(x, float), np.asarray(z, float), np.asarray(y, float)
        ik, iy = self.indeksy(x, z, y)
        wynik = self.r[ik, iy]
        return np.where(y > self.ym, 0.0, wynik)

    def json(self):
        return {"krok_kata": self.kk, "krok_y": self.ky, "y_maks": self.ym, "kamer": self.kamer,
                "y_max_kamery": round(self.y_max_kamery, 2), "r_max_kamery": round(self.r_max_kamery, 2),
                "r": [[round(float(v), 2) for v in wiersz] for wiersz in self.r]}

    @classmethod
    def z_json(cls, d):
        import numpy as np
        p = cls(d["krok_kata"], d["krok_y"], d["y_maks"])
        p.r = np.array(d["r"], float)
        p.kamer = d["kamer"]
        p.y_max_kamery = d["y_max_kamery"]
        p.r_max_kamery = d["r_max_kamery"]
        return p


def odcisk(akt):
    """Odcisk danych wejściowych profilu (wymiary aktorów + źródło tego pliku) — profil liczy się od nowa, gdy się zmieni."""
    import hashlib
    h = hashlib.sha1()
    with open(os.path.abspath(__file__), "rb") as f:
        h.update(f.read())
    h.update(json.dumps({k: [a["h"], a["szer"], a["gleb"], a["przod"], a["lezy"]] for k, a in sorted(akt.items())},
                        sort_keys=True, default=str).encode("utf-8"))
    return h.hexdigest()[:16]


def policz_profil(akt=None):
    """Profil wolnej przestrzeni dla wszystkich par (klasy × przeciwnicy i lustro) i statystyka par."""
    akt = akt or aktorzy()
    p = Profil()
    statystyka = {}
    for gk, wk in pary(akt):
        kam = kamery_pary(akt[gk], akt[wk])
        p.dodaj_kamery(kam)
        statystyka["%s/%s" % (gk, wk)] = round(max(math.hypot(q[0], q[2]) for q, _ in kam), 1)
    p.rozszerz()
    return p, statystyka


PLIK_PROFILU = os.path.join(TU, "profil_kamer.json")


def plik_profilu(klucz_areny=None):
    """Profil areny: wspólny `profil_kamer.json` dla aren z przeciwnikami z 17.11 (las, Bagno, plac — ten sam zestaw),
    własny `<arena>/profil_kamer.json` dla areny z innym zestawem (np. Dżungla)."""
    import plan as P
    if klucz_areny is None:
        return PLIK_PROFILU, None
    przeciwnicy = P.ARENY[klucz_areny].get("przeciwnicy")
    if przeciwnicy is None or sorted(przeciwnicy) == sorted(P.PRZECIWNICY_17_11):
        return PLIK_PROFILU, P.PRZECIWNICY_17_11
    return os.path.join(TU, klucz_areny, "profil_kamer.json"), przeciwnicy


def profil_areny(klucz_areny, odswiez=False):
    plik, przeciwnicy = plik_profilu(klucz_areny)
    return profil(odswiez, przeciwnicy, plik)


def profil(odswiez=False, przeciwnicy=None, plik=None):
    """Profil z pliku (gdy odcisk danych się zgadza) albo policzony od nowa i zapisany."""
    plik = plik or PLIK_PROFILU
    if przeciwnicy is None and plik == PLIK_PROFILU:
        import plan as P
        przeciwnicy = P.PRZECIWNICY_17_11
    akt = aktorzy_do_profilu(przeciwnicy)
    o = odcisk(akt)
    if not odswiez and os.path.isfile(plik):
        with open(plik, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("odcisk") == o:
            return Profil.z_json(d)
    p, st = policz_profil(akt)
    import numpy as np
    p.r = np.round(p.r, 2)                                   # jak w pliku — świeży profil = wczytany (te same areny)
    d = p.json()
    d["odcisk"] = o
    d["opis"] = ("Wolna przestrzeń kamer walki (swiat/areny_walki/kamery.py): r[kąt][wysokość] = największy promień od "
                 "środka placu, kąt od osi +X sceny ku +Z co krok_kata°, wysokość od płyty placu co krok_y.")
    d["pary"] = st
    d["przeciwnicy"] = sorted(k for k, a in akt.items() if a["rola"] == "przeciwnik")
    d["szacunkowi"] = sorted(k for k, a in akt.items() if a.get("zapas"))
    os.makedirs(os.path.dirname(plik), exist_ok=True)
    with open(plik, "w", encoding="utf-8", newline="\n") as f:
        json.dump(d, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    return p


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    import time
    t0 = time.time()
    arena = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
    p = profil_areny(arena, odswiez="--odswiez" in sys.argv) if arena else profil(odswiez="--odswiez" in sys.argv)
    print("kamer: %d, r_max %.1f, y_max %.1f (%.1f s)" % (p.kamer, p.r_max_kamery, p.y_max_kamery, time.time() - t0))
    for ka in range(0, 360, 15):
        ik = int(ka / p.kk)
        print("kąt %3d°: " % ka + " ".join("%5.1f" % p.r[ik][iy] for iy in range(0, p.ny, 4)))