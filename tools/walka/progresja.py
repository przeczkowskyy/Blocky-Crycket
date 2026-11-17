#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kalkulator balansu 17.11 (propozycja liczb, NIE kanon): szesc zaleglych rachunkow z sesji 14.11 i 16.11.

    python -B tools/walka/progresja.py                         # wszystko (kilka minut), Markdown na ekran
    python -B tools/walka/progresja.py --czesci 2,3,4          # same rachunki bez ciezkich symulacji
    python -B tools/walka/progresja.py --md wynik.md --procesy 1 --ziaren 400

Czesci (numery jak w zleceniu z Zadania.md):
  1 Pancerz punktowy a obrazenia potworow w osmiu biomach (D-061, D-062, D-091, D-076);
  2 drzewko Twierdzy: mnoznik procentowy razy ulepszenie budynku (D-049, D-056, D-087);
  3 ewolucja petow: shardy, tokeny krainy, szansa na Shard Ewolucji (D-058);
  4 Gemy na drzewka wzgledem czasu gry: 10 godzin do ostatniego biomu, plan rosnacy i rowny (D-056, D-057, D-076);
  5 pytanie 40: Wojownik z tarcza i unikiem — limit uniku, slabszy trening Zrecznosci, jedna szansa (D-062, D-073);
  6 trening: przyrost za trafienie i za serie bez nadużywania jednej mini-gry (D-050, D-063, D-074).

Zalozenia, ktorych nie ma w sejfie, sa w slowniku ZALOZENIA (kazde „przyjete, do zmiany”) i w BALANS_1711.md.
Potwory dalszych biomow nie istnieja — liczymy na potworach lasu przeskalowanych do poziomu gracza i mnoznikiem
biomu (zastepczo). Tempo (minuty walki do poziomu) to ta sama krzywa co w tempo.py (11,71 x L^1,6).
"""
import argparse
import contextlib
import copy
import math
import os
import re
import statistics
import sys
import time
from multiprocessing import Pool

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, TU)
import balans  # noqa: E402
import silnik  # noqa: E402
import tempo  # noqa: E402
import wzorcowe  # noqa: E402

KLASY = wzorcowe.KLASY
STAT = wzorcowe.STATYSTYKI
NAZWY = balans.NAZWY
NAZWY_STAT = balans.NAZWY_STAT
NAZWY_BIOMOW = tempo.NAZWY_BIOMOW + ["Kryształowy"]
ZWYKLE = ["lesny_slime", "cierniowy_wilk", "muchomornik"]
FIZYCZNE = ["lesny_slime", "cierniowy_wilk"]          # zwykle potwory bijace fizycznie (Pancerz dziala)
MIEDZY = {p: m for p, _, _, m, _ in tempo.PRZEGRODY}  # sekundy miedzy walkami (dojscie + odrodzenie potwora)
ODRODZENIE_GRACZA = 15.0
SKILL_TREE = os.path.join(REPO, "src", "shared", "SkillTreeData.luau")

pp, proc, liczba = balans.pp, balans.proc, balans.liczba

# ------------------------------------------------------------------------------------------------ zalozenia
# Wszystko ponizej to zalozenia „przyjete, do zmiany” — w sejfie tych liczb nie ma. Opis: BALANS_1711.md.
ZALOZENIA = {
    "plan_rosnacy": list(tempo.PLAN_ROSNACY),        # D-076 (korekta Karola): roboczo 30/45/.../170 min = 600
    "plan_rowny": [600 / 7.0] * 7,                   # D-076: wariant rowny ok. 85 min
    "osmy_biom_min": {"rosnący": 230.0, "równy": 600 / 7.0},  # ile trwa 8. biom (tylko do „wyjscia” z niego)
    "udzial_treningu": 0.20,                         # gracz oczekiwany: 20% czasu w Training Center
    "udzial_treningu_duzo": 0.40,                    # gracz, ktory duzo trenuje
    "cel_zwykle_wejscie": (85.0, 75.0),              # wygrane gracza oczekiwanego ze zwyklymi na wejsciu: biom 1 -> 8
    # trening (propozycja wzoru, czesc 6)
    "trafienia_na_min": 30.0,                        # tempo mini-gry (zmierzy prototyp)
    "combo_srednie": 1.3,                            # sredni mnoznik serii gracza (seria 0-4: x1; 5-9: x1,25; 10-19: x1,5; 20+: x2)
    "trafien_na_punkt": 10.0,                        # N0: tyle trafien bez serii daje +1 punkt swiezej statystyki
    "polowa_udzialu": 0.10,                          # h: malejacy zysk liczony od h x pula punktow poziomu (na statystyke)
    "wykladnik": 2,                                  # M = 1 / (1 + W/(h*pula))^wykladnik
    "centrum": [1.0, 1.15, 1.3, 1.45, 1.6, 1.75, 1.9, 2.0],  # mnoznik ulepszonego centrum, poziom centrum <= nr biomu
    # Twierdza (czesc 2)
    "kopalnie_od_poziomu": 25,                       # Karol, odpowiedz na pytanie 9
    "poziom_budynku_co": 5,                          # kolejny poziom budynku dostepny co 5 poziomow gracza
    "baza_kopalni": 0.15,                            # 1. poziom kopalni zlota = 15% zlota z walk na godzine na 25. poziomie
    "godzin_gry_dziennie": 2.0,                      # do rachunku dochodu offline
    # pety (czesc 3)
    "ewolucje": 3,                                   # trzy ewolucje na peta (poziomy peta 10 / 20 / 30)
    "szanse_jajka": [0.50, 0.25, 0.15, 0.08, 0.02],  # jajko z pieciu petow: pospolity ... legendarny
    "ceny_jajek": (1000, 10000),                     # tanie i najdrozsze jajko lasu (D-052: najdrozsze ok. 10 tys.)
    "kopie_na_ewolucje": [2, 3, 5],                  # shardy peta (kopie) na 1., 2. i 3. ewolucje (D-058: kopia = shard)
    "kopie_wg_rzadkosci": [10, 8, 6, 4, 3],          # wariant: kopii na komplet ewolucji wg rzadkosci peta
    "tokeny_na_ewolucje": [60, 180, 450],            # tokeny krainy na 1., 2. i 3. ewolucje
}


def plan(nazwa):
    p = ZALOZENIA["plan_rosnacy"] if nazwa == "rosnący" else ZALOZENIA["plan_rowny"]
    return list(p) + [ZALOZENIA["osmy_biom_min"][nazwa]]


# ------------------------------------------------------------------------------------------------ silnik: zadania
@contextlib.contextmanager
def wariant_silnika(nazwa):
    """Wariant zasad tylko na czas serii (pytanie 40). None = silnik jak w danych."""
    if not nazwa:
        yield
        return
    if nazwa == "limit_uniku_15":
        # (a') nizszy limit uniku klasy Wojownik (takze Lesny Troll, ktory ma te klase)
        stary = silnik.KLASY["wojownik"]["unik_limit"]
        silnik.KLASY["wojownik"]["unik_limit"] = 0.15
        try:
            yield
        finally:
            silnik.KLASY["wojownik"]["unik_limit"] = stary
        return
    if nazwa == "jedna_szansa":
        # (c) blok i unik sie nie sumuja: jedna szansa uniknięcia ciosu = max(unik, blok); unik ma pierwszenstwo,
        # blok tylko w nadwyzce. Rzuty silnika sa niezalezne (najpierw unik, potem blok), wiec wystarczy podmienic
        # na czas ataku szanse bloku celu na (blok - unik) / (1 - unik) — kolejnosc i liczba rzutow bez zmian.
        zc, uu = silnik.zwykly_cios, silnik.uzyj_umiejetnosci

        def owin(f):
            def g(w, kto, cel, *reszta):
                D = w["strony"][cel]
                b = D["blok"]
                u = silnik.unik_efektywny(D, w["stan"][cel])
                D["blok"] = max(0.0, b - u) / (1 - u) if u < 1 else 0.0
                try:
                    return f(w, kto, cel, *reszta)
                finally:
                    D["blok"] = b
            return g
        silnik.zwykly_cios, silnik.uzyj_umiejetnosci = owin(zc), owin(uu)
        try:
            yield
        finally:
            silnik.zwykly_cios, silnik.uzyj_umiejetnosci = zc, uu
        return
    raise ValueError("nieznany wariant %s" % nazwa)


def potwor_biomu(baza, k):
    """Potwor lasu jako zastepczy potwor biomu: cios x k (bron i Sila) i zycie x k (modyfikator zycia).
    Zwraca (id, opis); opis trzeba przekazac do procesu liczacego (dopisuje go do silnik.PRZECIWNICY)."""
    ident = "%s@%.4f" % (baza, k)
    if ident not in silnik.PRZECIWNICY:
        d = copy.deepcopy(silnik.PRZECIWNICY[baza])
        d["id"] = ident
        d["bron"] = [d["bron"][0] * k, d["bron"][1] * k]
        d["statystyki"]["sila"] = [x * k for x in d["statystyki"]["sila"]]
        m = d["modyfikatory"]
        m["zycie"] = (1 + m.get("zycie", 0)) * k - 1
        if m["zycie"] > silnik.MODYFIKATORY_PO_ID["zycie"]["max"]:
            raise ValueError("mnoznik %.2f za duzy dla %s (granica modyfikatora zycia)" % (k, baza))
        silnik.PRZECIWNICY[ident] = d
    return ident, silnik.PRZECIWNICY[ident]


def _zadanie(arg):
    klucz, gracz, prz, start, n, wariant, nowe = arg
    for d in nowe:
        silnik.PRZECIWNICY.setdefault(d["id"], d)
    with wariant_silnika(wariant):
        r = balans.seria(gracz, prz, start, n)
    r["tury_med"] = statistics.median(r["tury"])
    del r["tury"]
    return klucz, r


class Liczydlo:
    """Serie walk w kilku procesach. Zadanie: (klucz, gracz, przeciwnik, start, n, wariant, [opisy potworow])."""

    def __init__(self, procesy):
        self.pula = Pool(procesy) if procesy > 1 else None

    def licz(self, zadania):
        unik = {}
        for z in zadania:
            unik.setdefault(z[0], z)
        lista = list(unik.values())
        if self.pula is None:
            return dict(_zadanie(z) for z in lista)
        return dict(self.pula.map(_zadanie, lista, chunksize=4))


# ------------------------------------------------------------------------------------------------ tempo i ekonomia walk
_CYKLE = {}


def cykl(L, ziaren=20):
    """Sredni cykl walki gracza wzorcowego (srednia klas) z trzema zwyklymi potworami lasu jego poziomu (zastepczo
    za potwory biomu): sekundy (walka + dojscie + odrodzenie po przegranej), doswiadczenie, zloto, gemy, tokeny
    krainy i udzial wygranych na cykl. Te same ziarna i ten sam cykl co tempo.cykl_na_poziomie (model biomow)."""
    klucz = (min(L, 200), ziaren)
    if klucz in _CYKLE:
        return _CYKLE[klucz]
    s = {"t": 0.0, "xp": 0.0, "zloto": 0.0, "gemy": 0.0, "tokeny": 0.0, "wygrane": 0.0}
    n = 0
    for k in KLASY:
        g = wzorcowe.postac(k, klucz[0])
        for p in ZWYKLE:
            for z in range(1, ziaren + 1):
                w = silnik.symuluj(g, {"potwor": p, "poziom": klucz[0]}, z)
                wyg = w["wynik"] == "wygrana"
                lup = w["lup"]
                s["t"] += w["czas"] + MIEDZY[p] + (0.0 if wyg else ODRODZENIE_GRACZA)
                s["xp"] += lup["doswiadczenie"]
                s["zloto"] += lup["zloto"]
                s["gemy"] += lup["gemy"]
                s["tokeny"] += lup["tokeny_krainy"]
                s["wygrane"] += 1 if wyg else 0
                n += 1
    out = {k: v / n for k, v in s.items()}
    _CYKLE[klucz] = out
    return out


class Tempo:
    """Krzywa: minuty WALKI potrzebne, by z 1. poziomu dojsc do poziomu L (ta sama co w tempo.model_biomow)."""

    def __init__(self, maks=130, ziaren=20):
        self.minuty = [0.0, 0.0]
        for L in range(1, maks):
            c = cykl(L, ziaren)
            n = tempo.xp_do_nastepnego(L, tempo.DOMYSLNE_A, 1.6) / c["xp"]
            self.minuty.append(self.minuty[-1] + n * c["t"] / 60.0)

    def poziom(self, m):
        """Ulamkowy poziom po m minutach walki."""
        L = 1
        while L + 1 < len(self.minuty) and self.minuty[L + 1] <= m:
            L += 1
        if L + 1 >= len(self.minuty):
            return float(L)
        a, b = self.minuty[L], self.minuty[L + 1]
        return L + (m - a) / (b - a)

    def na_minute(self, L, co):
        """Zloto / doswiadczenie / gemy / tokeny na minute walki na poziomie L."""
        c = cykl(int(L))
        return c[co] / (c["t"] / 60.0)


def granice(T, nazwa_planu, udzial=0.0):
    """Biomy planu: minuty gry na wejsciu i wyjsciu, poziom gracza (walczy (1 - udzial) czasu, reszta to trening)."""
    out, t = [], 0.0
    for i, m in enumerate(plan(nazwa_planu)):
        out.append({"i": i, "biom": NAZWY_BIOMOW[i], "od": t, "do": t + m,
                    "L_od": int(T.poziom((1 - udzial) * t)), "L_do": int(T.poziom((1 - udzial) * (t + m)))})
        t += m
    return out


# ------------------------------------------------------------------------------------------------ trening (czesc 6)
class Trening:
    """Propozycja wzoru przyrostu z mini-gry (czesc 6; liczby w ZALOZENIA, wszystkie do zmiany):

        punkty za trafienie w mini-grze statystyki s = C x K x M_s / N0
        C   — mnoznik ulepszonego centrum (poziom centrum <= numer biomu),
        K   — seria trafien bez pudla: 0-4 x1, 5-9 x1,25, 10-19 x1,5, od 20 x2 (srednio przyjete x1,3),
        N0  — trafien na +1 punkt swiezej statystyki (pasek treningu; ekran pokazuje „+1” przy zapelnieniu),
        M_s — malejacy zysk TEJ statystyki: 1 / (1 + W_s / (h x pula(L)))^p, W_s = punkty juz wytrenowane w s,
              pula(L) = punkty statystyk z poziomu gracza. Inna mini-gra ma pelne tempo, a awans je przywraca.
    wykladnik p = 0 -> bez malejacego zysku (dzisiejsze D-050: „+1 za trafienie”, bez limitu)."""

    def __init__(self, **zm):
        z = dict(ZALOZENIA)
        z.update(zm)
        self.r = z["trafienia_na_min"] * z["combo_srednie"] / z["trafien_na_punkt"]  # punkty/min, swieza stat.
        self.h = z["polowa_udzialu"]
        self.p = z["wykladnik"]
        self.centrum = z["centrum"]

    def mnoznik(self, W_s, L):
        if self.p == 0:
            return 1.0
        return 1.0 / (1.0 + W_s / (self.h * wzorcowe.pula(L))) ** self.p

    def tempo(self, W_s, L, biom):
        return self.r * self.centrum[min(biom, len(self.centrum) - 1)] * self.mnoznik(W_s, L)


def wybierz(polityka, W, klasa):
    if polityka == "rowno":            # zawsze mini-gra statystyki z najmniejszym treningiem (= po kolei wszystkie)
        return min(STAT, key=lambda s: (W[s], STAT.index(s)))
    if polityka == "klasa":            # trening w proporcjach rozkladu klasy (statystyka najbardziej „ponizej”)
        roz = wzorcowe.ROZKLADY[klasa]
        razem = sum(W.values())
        return max(STAT, key=lambda s: (roz[s] * (razem + 1) - W[s], -STAT.index(s)))
    if polityka.startswith("jedna:"):  # caly trening w jednej mini-grze
        return polityka.split(":", 1)[1]
    raise ValueError(polityka)


def przebieg_treningu(T, tr, klasa, nazwa_planu, udzial, polityka, punkty, krok=0.25):
    """Calkowanie po czasie gry: co `krok` minut gry gracz walczy (1 - udzial) i trenuje udzial minut. Poziom wynika
    z minut walki (Tempo), mini-gre wybiera polityka. Zwraca {minuta gry z `punkty`: (poziom, {stat: punkty})}."""
    W = {s: 0.0 for s in STAT}
    gr = granice(T, nazwa_planu, udzial)
    out = {}
    cele = sorted(punkty)
    t = 0.0
    while cele:
        while cele and cele[0] <= t + 1e-9:
            out[cele.pop(0)] = (T.poziom((1 - udzial) * t), dict(W))
        if not cele:
            break
        L = max(1, int(T.poziom((1 - udzial) * t)))
        biom = next((b["i"] for b in gr if b["od"] <= t < b["do"]), len(gr) - 1)
        if udzial > 0:
            s = wybierz(polityka, W, klasa)
            W[s] += tr.tempo(W[s], L, biom) * udzial * krok
        t += krok
    return out


def trenowany(klasa, L, W, tarcza=True, mnoznik_zr=1.0):
    """Postac wzorcowa poziomu L z punktami z treningu ponad pule (zaokraglone)."""
    dod = {s: int(round(W[s] * (mnoznik_zr if s == "zrecznosc" else 1.0))) for s in STAT if W.get(s)}
    return wzorcowe.postac(klasa, L, dodatkowe=dod or None, tarcza=tarcza)


# ------------------------------------------------------------------------------------------------ drzewka (czesc 2, 4)
def wezly_drzewka(sciezka=SKILL_TREE):
    """Wezly drzewek z src/shared/SkillTreeData.luau (tylko odczyt): lista {zakladka, galaz, nazwa, stat, per, max,
    glebokosc, koszt}. Koszt i glebokosc jak w SkillTreeData.cost: (10 + 5 x glebokosc) x kolejny poziom."""
    with open(sciezka, encoding="utf-8") as f:
        tekst = f.read()
    if "return (10 + 5 * node.depth) * nextLevel" not in tekst:
        raise ValueError("SkillTreeData.cost ma inny wzor niz (10 + 5 * depth) * nextLevel — zaktualizuj kalkulator")
    root = int(re.search(r"ROOT_COST = (\d+)", tekst).group(1))
    blok = re.search(r"local SLOTS = \{(.*?)\n\}", tekst, re.S).group(1)
    sloty = [(float(m.group(1)), int(m.group(2))) for m in re.finditer(r"\{ ([\d.]+), -?[\d.]+, (\d+) \}", blok)]
    wezly, zakladka, galaz, i = [], None, None, 0
    for linia in tekst.splitlines():
        mz = re.match(r'\s*id = "(\w+)",\s*$', linia)
        mg = re.match(r'\s*id = "(\w+)", title = ', linia)
        mw = re.match(r'\s*\{ "\w+", "([^"]+)", "(\w+)", (\d+), (\d+)', linia)
        if mz:
            zakladka = mz.group(1)
            wezly.append({"zakladka": zakladka, "galaz": "", "nazwa": "ROOT", "stat": "", "per": 0, "max": 1,
                          "glebokosc": 0, "koszt": [root]})
        elif mg:
            galaz, i = mg.group(1), 0
        elif mw and zakladka:
            d = int(math.floor(sloty[i][0]))
            mx = int(mw.group(4))
            wezly.append({"zakladka": zakladka, "galaz": galaz, "nazwa": mw.group(1), "stat": mw.group(2),
                          "per": int(mw.group(3)), "max": mx, "glebokosc": d, "nr": i + 1, "rodzic": sloty[i][1],
                          "koszt": [(10 + 5 * d) * n for n in range(1, mx + 1)]})
            i += 1
    return wezly


def koszt_slotow(wezly):
    """Ile Gemow trzeba na 1., 2. i 3. slot umiejetnosci z drzewka Player (wezly SkillSlots razem z rodzicami po
    drodze, kazdy rodzic na 1. poziomie, i korzeniem zakladki) — narastajaco."""
    gal = {w["nr"]: w for w in wezly if w["zakladka"] == "Player" and w["galaz"] == "Skills"}
    root = next(w["koszt"][0] for w in wezly if w["zakladka"] == "Player" and w["nazwa"] == "ROOT")
    kupione, suma, out = set(), root, []
    for nr in sorted(n for n, w in gal.items() if w["stat"] == "SkillSlots"):
        x = nr
        while x and x not in kupione:
            kupione.add(x)
            suma += gal[x]["koszt"][0]
            x = gal[x]["rodzic"]
        out.append(suma)
    return out


def koszty_zakladek(wezly):
    out = {}
    for w in wezly:
        out[w["zakladka"]] = out.get(w["zakladka"], 0) + sum(w["koszt"])
    return out


def kupione_za(wezly, zakladka, gemy):
    """Ile procent kosztu zakladki da sie kupic za `gemy`, kupujac zawsze najtanszy dostepny poziom wezla
    (rodzic przed dzieckiem upraszczamy: korzen pierwszy, potem najtansze — wszystkie wezly 1. glebokosci sa tanie)."""
    ceny = sorted(c for w in wezly if w["zakladka"] == zakladka for c in w["koszt"])
    suma = sum(ceny)
    wydane = 0
    for c in ceny:
        if wydane + c > gemy:
            break
        wydane += c
    return 100.0 * wydane / suma


# ------------------------------------------------------------------------------------------------ czesc 1: Pancerz
def czesc_1(T, liczydlo, N, S, w):
    w.append("## 1. Pancerz punktowy a obrażenia potworów w ośmiu biomach")
    w.append("")
    tr = Trening()
    s_ocz, s_duzo = ZALOZENIA["udzial_treningu"], ZALOZENIA["udzial_treningu_duzo"]
    cel0, cel8 = ZALOZENIA["cel_zwykle_wejscie"]
    dane = {}
    for nazwa_planu in ("rosnący", "równy"):
        gr = granice(T, nazwa_planu, s_ocz)
        punkty = sorted({b["od"] for b in gr} | {b["do"] for b in gr})
        prof = {}
        for k in KLASY:
            for nazwa, s in (("gołe", 0.0), ("oczekiwany", s_ocz), ("dużo", s_duzo)):
                prof[(k, nazwa)] = przebieg_treningu(T, tr, k, nazwa_planu, s, "klasa", punkty) if s > 0 else None

        def postac(k, nazwa, t, L):
            p = prof[(k, nazwa)]
            return trenowany(k, L, p[t][1]) if p else wzorcowe.postac(k, L)
        # mnoznik biomu k_b: bisekcja tak, zeby gracz oczekiwany na wejsciu wygrywal ze zwyklymi cel_b procent
        lo = {b["i"]: 0.6 for b in gr}
        hi = {b["i"]: 2.6 for b in gr}
        cel = {b["i"]: cel0 + (cel8 - cel0) * b["i"] / 7.0 for b in gr}
        for _ in range(9):
            zad = []
            for b in gr:
                kb = (lo[b["i"]] + hi[b["i"]]) / 2
                for k in KLASY:
                    g = postac(k, "oczekiwany", b["od"], b["L_od"])
                    for p in ZWYKLE:
                        ident, opis = potwor_biomu(p, kb)
                        zad.append(((b["i"], k, ident), g, {"potwor": ident, "poziom": b["L_od"]}, S + 70000,
                                    max(200, N // 2), None, [opis]))
            r = liczydlo.licz(zad)
            for b in gr:
                kb = (lo[b["i"]] + hi[b["i"]]) / 2
                sr = statistics.mean(r[(b["i"], k, "%s@%.4f" % (p, kb))]["proc"] for k in KLASY for p in ZWYKLE)
                if sr > cel[b["i"]]:
                    lo[b["i"]] = kb
                else:
                    hi[b["i"]] = kb
        kb = {i: round((lo[i] + hi[i]) / 2, 2) for i in lo}
        # sprawdzenie: trzy profile, wejscie (zwykle) i wyjscie (zwykle, troll i straznik o poziom nizej niz gracz)
        zad = []
        for b in gr:
            for k in KLASY:
                for nazwa in ("gołe", "oczekiwany", "dużo"):
                    g_od = postac(k, nazwa, b["od"], b["L_od"])
                    g_do = postac(k, nazwa, b["do"], b["L_do"])
                    for p in ZWYKLE:
                        ident, opis = potwor_biomu(p, kb[b["i"]])
                        zad.append(((nazwa_planu, b["i"], k, nazwa, "od", p), g_od, {"potwor": ident, "poziom": b["L_od"]},
                                    S, N, None, [opis]))
                        zad.append(((nazwa_planu, b["i"], k, nazwa, "do", p), g_do, {"potwor": ident, "poziom": b["L_do"]},
                                    S, N, None, [opis]))
                    for p in ("lesny_troll", "straznik_lasu"):
                        ident, opis = potwor_biomu(p, kb[b["i"]])
                        zad.append(((nazwa_planu, b["i"], k, nazwa, "do", p), g_do,
                                    {"potwor": ident, "poziom": max(1, b["L_do"] - 1)}, S, N, None, [opis]))
        r = liczydlo.licz(zad)
        dane[nazwa_planu] = {"granice": gr, "kb": kb, "wyniki": r, "prof": prof}

        w.append("### Plan %s (%s min do ostatniego biomu; gracz oczekiwany trenuje %s czasu)" % (
            nazwa_planu, liczba(sum(plan(nazwa_planu)[:7]), 0), proc(100 * s_ocz)))
        w.append("")
        w.append("Mnożnik biomu k = o ile ciosy i życie potworów biomu są większe od potwora lasu tego samego poziomu "
                 "(dobrany symulacją tak, żeby gracz oczekiwany na wejściu wygrywał ze zwykłymi potworami tyle, ile "
                 "w kolumnie „Cel”). Wygrane: średnio trzy klasy; „gołe poziomy” = ta sama postać bez treningu, "
                 "„dużo treningu” = %s czasu w Training Center. Wyjście: zwykłe potwory poziomu gracza, troll i "
                 "strażnik o poziom niżej." % proc(100 * s_duzo))
        w.append("")
        w.append("| Biom | Poziom wejście → wyjście | k | Cel | Zwykłe na wejściu: gołe / oczekiwany / dużo | "
                 "Zwykłe na wyjściu (oczekiwany) | Troll / strażnik na wyjściu: gołe | oczekiwany | dużo |")
        w.append("|---|---|---:|---:|---|---:|---|---|---|")

        def sr(b, nazwa, gdzie, potwory):
            return statistics.mean(r[(nazwa_planu, b["i"], k, nazwa, gdzie, p)]["proc"] for k in KLASY for p in potwory)
        for b in gr:
            w.append("| %s | %d → %d | %s | %s | %s / %s / %s | %s | %s / %s | %s / %s | %s / %s |" % (
                b["biom"], b["L_od"], b["L_do"], liczba(kb[b["i"]], 2), proc(cel[b["i"]]),
                proc(sr(b, "gołe", "od", ZWYKLE)), proc(sr(b, "oczekiwany", "od", ZWYKLE)), proc(sr(b, "dużo", "od", ZWYKLE)),
                proc(sr(b, "oczekiwany", "do", ZWYKLE)),
                proc(sr(b, "gołe", "do", ["lesny_troll"])), proc(sr(b, "gołe", "do", ["straznik_lasu"])),
                proc(sr(b, "oczekiwany", "do", ["lesny_troll"])), proc(sr(b, "oczekiwany", "do", ["straznik_lasu"])),
                proc(sr(b, "dużo", "do", ["lesny_troll"])), proc(sr(b, "dużo", "do", ["straznik_lasu"]))))
        w.append("")
        # Pancerz kazdej klasy na wejsciu i wyjsciu, cios zwyklego potwora fizycznego biomu, co przechodzi
        lim = silnik.STALE["limit_redukcji"]
        w.append("Pancerz gracza (punkty po przeliczniku klasy) i cios zwykłego potwora fizycznego biomu (średnio Slime "
                 "i Wilk × k, bez krytyka, rozrzut 100%%). „Przechodzi” = część ciosu po Pancerzu (najmniej %s — limit "
                 "D-091). „Do limitu” = ile punktów Pancerza z treningu brakuje graczowi oczekiwanemu, żeby zwykły cios "
                 "tego biomu dochodził tylko w %s." % (proc(100 - 100 * lim), proc(100 - 100 * lim)))
        w.append("")
        w.append("| Biom | Gdzie | Poziom | Cios potwora | " + " | ".join(
            "%s: Pancerz gołe / oczek. → przechodzi gołe / oczek. | do limitu" % NAZWY[k] for k in KLASY) + " |")
        w.append("|---|---|---:|---:|" + "---|---:|" * len(KLASY))
        pancerz = []
        for b in gr:
            for gdzie, t, L in (("wejście", b["od"], b["L_od"]), ("wyjście", b["do"], b["L_do"])):
                cios = statistics.mean(silnik.wartosci_potwora(potwor_biomu(p, kb[b["i"]])[0], L)["cios"] for p in FIZYCZNE)
                kom = []
                for k in KLASY:
                    v0 = silnik.wartosci_postaci(wzorcowe.postac(k, L))["pancerz"]
                    v1 = silnik.wartosci_postaci(postac(k, "oczekiwany", t, L))["pancerz"]
                    po0 = max(cios * (1 - lim), cios - v0) / cios
                    po1 = max(cios * (1 - lim), cios - v1) / cios
                    brak = max(0.0, lim * cios - v1) / (silnik.KLASY[k]["mnoznik_pancerza"] * silnik.STALE["pancerz_za_punkt"])
                    kom.append("%s / %s → %s / %s | %s" % (liczba(v0, 0), liczba(v1, 0), proc(100 * po0), proc(100 * po1),
                                                          liczba(brak, 0)))
                    pancerz.append({"plan": nazwa_planu, "biom": b["i"], "gdzie": gdzie, "klasa": k, "L": L,
                                    "cios": cios, "pancerz": v1, "przechodzi": po1, "brak": brak})
                w.append("| %s | %s | %d | %s | %s |" % (b["biom"], gdzie, L, liczba(cios, 0), " | ".join(kom)))
        w.append("")
        dane[nazwa_planu]["pancerz"] = pancerz
    return dane


# ------------------------------------------------------------------------------------------------ czesc 2: Twierdza
KRZYWE_BUDYNKU = {
    "liniowa (n)": lambda n: float(n),
    "potęgowa (n^1,5)": lambda n: n ** 1.5,
    "wykładnicza ×1,25": lambda n: 1.25 ** (n - 1),
    "wykładnicza ×1,6": lambda n: 1.6 ** (n - 1),
}


def mnozniki_drzewka(wezly):
    """Pelne premie z drzewka (procent x maks. poziom) dla zrodel dochodu Twierdzy i gracza."""
    def suma(zakladka, galaz, staty):
        return sum(w["per"] * w["max"] for w in wezly if w["zakladka"] == zakladka and w["galaz"] == galaz
                   and w["stat"] in staty) / 100.0
    return {
        "kopalnia": suma("Fortress", "Income", ("FortOre",)),
        "wszystkie_surowce": suma("Fortress", "Income", ("FortAllRes",)),
        "na_czas": suma("Fortress", "Income", ("FortTimed",)),
        "zloto_gracza": suma("Player", "Income", ("Gold",)),
        "offline": suma("Player", "Income", ("Offline",)),
        "gemy_gracza": suma("Player", "Income", ("Gems",)),
        "trening_ogolny": suma("Fortress", "Training", ("FortTraining",)),
        "trening_staty": {w["stat"]: w["per"] * w["max"] / 100.0 for w in wezly
                          if w["zakladka"] == "Fortress" and w["galaz"] == "Training" and w["stat"] != "FortTraining"},
    }


def czesc_2(T, w):
    w.append("## 2. Drzewko Twierdzy: mnożnik procentowy razy ulepszenie budynku")
    w.append("")
    wezly = wezly_drzewka()
    m = mnozniki_drzewka(wezly)
    L0 = ZALOZENIA["kopalnie_od_poziomu"]
    co = ZALOZENIA["poziom_budynku_co"]
    zl_h = {L: 60 * T.na_minute(L, "zloto") for L in range(1, 121)}
    baza = ZALOZENIA["baza_kopalni"] * zl_h[L0]
    w.append("Premie z drzewka w dzisiejszych danych (`src/shared/SkillTreeData.luau`, pełne poziomy): Twierdza → "
             "Income: kopalnia (MINING) +%s, wszystkie surowce (BIG CARTS) +%s, premia czasowa (RUSH HOUR) +%s; "
             "gracz → Income: Złoto (GOLD I i II) +%s, Złoto offline +%s." % (
                 proc(100 * m["kopalnia"]), proc(100 * m["wszystkie_surowce"]), proc(100 * m["na_czas"]),
                 proc(100 * m["zloto_gracza"]), proc(100 * m["offline"])))
    w.append("")
    # sposoby skladania premii
    zloz = {
        "tylko Twierdza, dodawane": 1 + m["kopalnia"] + m["wszystkie_surowce"],
        "Twierdza + gracz, dodawane": 1 + m["kopalnia"] + m["wszystkie_surowce"] + m["zloto_gracza"],
        "Twierdza + gracz, mnożone": (1 + m["kopalnia"]) * (1 + m["wszystkie_surowce"]) * (1 + m["zloto_gracza"]),
        "wszystko mnożone (z RUSH HOUR i offline)": (1 + m["kopalnia"]) * (1 + m["wszystkie_surowce"])
        * (1 + m["zloto_gracza"]) * (1 + m["na_czas"]) * (1 + m["offline"]),
    }
    w.append("| Jak składać premie z drzewka | Mnożnik dochodu kopalni przy pełnym drzewku |")
    w.append("|---|---:|")
    for k, v in zloz.items():
        w.append("| %s | ×%s |" % (k, liczba(v, 2)))
    w.append("")
    w.append("Kopalnia Złota od %d. poziomu gracza, kolejny poziom budynku co %d poziomów gracza. 1. poziom kopalni = "
             "%s Złota z walk na godzinę na %d. poziomie (%s zł/h z %s zł/h). Złoto z walk: gracz wzorcowy, zwykłe "
             "potwory jego poziomu, cykl jak w modelu tempa." % (L0, co, proc(100 * ZALOZENIA["baza_kopalni"]), L0,
                                                                 liczba(baza, 0), liczba(zl_h[L0], 0)))
    w.append("")
    w.append("Komórka: dochód kopalni na godzinę jako procent Złota z walk na godzinę na tym poziomie gracza — bez drzewka / "
             "z pełnym drzewkiem Twierdzy (dodawane) / z drzewkiem Twierdzy i gracza mnożonym. Powyżej 100% kopalnia "
             "daje więcej niż walka.")
    w.append("")
    Ls = [L0 + co * i for i in range(0, 9)]
    w.append("| Krzywa budynku | " + " | ".join("poz. %d (bud. %d)" % (L, (L - L0) // co + 1) for L in Ls) + " |")
    w.append("|---|" + "---|" * len(Ls))
    wynik = {}
    for nazwa, f in KRZYWE_BUDYNKU.items():
        kom = []
        for L in Ls:
            n = (L - L0) // co + 1
            d = baza * f(n)
            r0, r1, r2 = (100 * d * x / zl_h[L] for x in (1.0, zloz["tylko Twierdza, dodawane"],
                                                           zloz["Twierdza + gracz, mnożone"]))
            kom.append("%s / %s / %s" % (liczba(r0, 0), liczba(r1, 0), liczba(r2, 0)))
            wynik[(nazwa, L)] = (r0, r1, r2)
        w.append("| %s | %s |" % (nazwa, " | ".join(kom)))
    w.append("")
    # dochod offline: kopalnia pracuje takze, gdy gracza nie ma (D-049: Twierdza „chodzi sama”; wezel OFFLINE GOLD)
    gra_h = ZALOZENIA["godzin_gry_dziennie"]
    w.append("Jeżeli kopalnia pracuje także wtedy, gdy gracza nie ma w grze (Twierdza „chodzi sama”, D-049; węzeł "
             "OFFLINE GOLD), liczy się doba, nie godzina gry. Gracz gra %s h dziennie (przyjęte). Komórka: Złoto "
             "kopalni na dobę jako procent Złota z walk z tej doby — krzywa wykładnicza ×1,25, bez drzewka / z pełnym "
             "drzewkiem Twierdzy i gracza (mnożone):" % liczba(gra_h, 0))
    w.append("")
    w.append("| Kopalnia pracuje | " + " | ".join("poz. %d (bud. %d)" % (L, (L - L0) // co + 1) for L in Ls[::2]) + " |")
    w.append("|---|" + "---|" * len(Ls[::2]))
    offline = {}
    for nazwa, godz in (("tylko w czasie gry", gra_h), ("offline do 8 h, 50% tempa", gra_h + 0.5 * 8),
                        ("cała doba, pełne tempo", 24.0)):
        kom = []
        for L in Ls[::2]:
            n = (L - L0) // co + 1
            d = baza * KRZYWE_BUDYNKU["wykładnicza ×1,25"](n) * godz
            akt = zl_h[L] * gra_h
            kom.append("%s / %s" % (proc(100 * d / akt), proc(100 * d * zloz["Twierdza + gracz, mnożone"] / akt)))
            offline[(nazwa, L)] = d / akt
        w.append("| %s | %s |" % (nazwa, " | ".join(kom)))
    w.append("")
    # wartosc wezla drzewka w zlocie na godzine a jego cena w Gemach
    w.append("Ile Złota na godzinę daje jeden poziom węzła MINING (+%d%% kopalni, cena 15–75 Gemów niezależnie od "
             "budynku) przy kopalni 1. i 9. poziomu:" % next(x["per"] for x in wezly if x["stat"] == "FortOre"))
    w.append("")
    w.append("| Krzywa budynku | Kopalnia 1. poz. | Kopalnia 9. poz. | Ile razy więcej |")
    w.append("|---|---:|---:|---:|")
    per = next(x["per"] for x in wezly if x["stat"] == "FortOre") / 100.0
    for nazwa, f in KRZYWE_BUDYNKU.items():
        w.append("| %s | %s zł/h | %s zł/h | ×%s |" % (nazwa, liczba(baza * f(1) * per, 0), liczba(baza * f(9) * per, 0),
                                                       liczba(f(9) / f(1), 1)))
    w.append("")
    # Training Center w drzewku Twierdzy
    ts = m["trening_staty"]
    staty_tc = {"FortTrainStr": "Siła", "FortTrainDex": "Zręczność", "FortTrainLuck": "Szczęście", "FortTrainArmor": "Pancerz"}
    w.append("Gałąź Training Center w drzewku Twierdzy: wszystkie mini-gry +%s (TRAINING I i II), do tego osobne węzły "
             "%s (po +%s). **Kondycja i Inteligencja nie mają własnego węzła**, więc przy pełnym drzewku cztery mini-gry "
             "dają ×%s, a dwie ×%s — patrz część 6." % (
                 proc(100 * m["trening_ogolny"]), ", ".join(staty_tc[s] for s in ts), proc(100 * max(ts.values())),
                 liczba(1 + m["trening_ogolny"] + max(ts.values()), 2), liczba(1 + m["trening_ogolny"], 2)))
    w.append("")
    return {"mnozniki": m, "zloz": zloz, "wynik": wynik, "zloto_h": zl_h, "baza": baza, "offline": offline}


# ------------------------------------------------------------------------------------------------ czesc 3: pety
def geometryczny(q):
    """Liczba prob do pierwszego sukcesu przy szansie q: srednia, mediana, 90% graczy."""
    return 1 / q, math.ceil(math.log(0.5) / math.log(1 - q)), math.ceil(math.log(0.1) / math.log(1 - q))


def czesc_3(T, liczydlo, N, S, w):
    w.append("## 3. Ewolucja petów: shardy, tokeny krainy, Shard Ewolucji")
    w.append("")
    G = 10  # Straznik Gaju stoi na 10. poziomie (przegroda lasu)
    zad = []
    for d in (0, 2, 5):
        for k in KLASY:
            zad.append(((d, k), wzorcowe.postac(k, G + d), {"potwor": "straznik_lasu", "poziom": G}, S, N, None, []))
    r = liczydlo.licz(zad)
    lup = silnik.PRZECIWNICY["straznik_lasu"]["lup"]
    szansa_dzis = lup["szansa_sharda"]
    farm = {}
    for d in (0, 2, 5):
        pw = statistics.mean(r[(d, k)]["proc"] for k in KLASY) / 100
        cz = statistics.mean(r[(d, k)]["czas"] for k in KLASY)
        t = cz + MIEDZY["straznik_lasu"] + (1 - pw) * ODRODZENIE_GRACZA
        farm[d] = (pw, t)
    w.append("Strażnik Gaju (10. poziom) farmiony przez gracza wzorcowego (średnio klasy): wygrane i czas jednej próby "
             "(walka + %d s dojścia i odrodzenia + %d s po przegranej):" % (MIEDZY["straznik_lasu"], ODRODZENIE_GRACZA))
    w.append("")
    w.append("| Gracz | Wygrane | Czas próby |")
    w.append("|---|---:|---:|")
    for d in (0, 2, 5):
        w.append("| poziom %d (+%d) | %s | %s s |" % (G + d, d, proc(100 * farm[d][0]), liczba(farm[d][1], 0)))
    w.append("")
    szanse = [0.05, 0.10, 0.15, 0.20, 0.25, 0.33]
    w.append("**Shard Ewolucji** (wypada tylko z wygranej ze strażnikiem, D-058; dziś szansa %s): ile prób na JEDEN "
             "Shard — średnio / połowa graczy / 90%% graczy — i ile to minut. Gracz farmi strażnika 2 poziomy wyżej. "
             "Ostatnia kolumna: ochrona przed pechem — Shard gwarantowany po 2/szansa wygranych bez Sharda "
             "(średnio prób)." % proc(100 * szansa_dzis))
    w.append("")
    w.append("| Szansa | Prób: średnio / 50%% / 90%% | Minut: średnio / 50%% / 90%% | Komplet %d ewolucji jednego peta (śr. minut) | "
             "10 petów biomu × %d (śr. godzin) | Z ochroną po N wygranych: N, śr. prób |" % (
                 ZALOZENIA["ewolucje"], ZALOZENIA["ewolucje"]))
    w.append("|---:|---|---|---:|---:|---|")
    pw, t = farm[2]
    tabela_sh = {}
    for p in szanse:
        sr_, med, p90 = geometryczny(pw * p)
        nmax = round(2 / p)
        e_wygr = (1 - (1 - p) ** nmax) / p
        e_prob = e_wygr / pw
        tabela_sh[p] = (sr_, med, p90, sr_ * t / 60)
        w.append("| %s | %s / %d / %d | %s / %s / %s | %s | %s | %d, %s |" % (
            proc(100 * p), liczba(sr_, 0), med, p90, liczba(sr_ * t / 60, 0), liczba(med * t / 60, 0),
            liczba(p90 * t / 60, 0), liczba(ZALOZENIA["ewolucje"] * sr_ * t / 60, 0),
            liczba(10 * ZALOZENIA["ewolucje"] * sr_ * t / 3600, 1), nmax, liczba(e_prob, 0)))
    w.append("")
    # tokeny krainy
    Lz = 10
    tok_min = T.na_minute(Lz, "tokeny")
    tok_str = lup["tokeny"] + lup["szansa_tokenu"]
    w.append("**Tokeny krainy** (dziś: zwykły potwór 1 + 30%% szansy na drugi, troll 3 + 50%%, strażnik 5 + 50%%, tylko "
             "za wygraną): gracz %d. poziomu na zwykłych potworach lasu zbiera **%s tokenu na minutę** (%s na godzinę); "
             "z farmienia strażnika %s na minutę." % (Lz, liczba(tok_min, 2), liczba(60 * tok_min, 0),
                                                    liczba(farm[2][0] * tok_str / (farm[2][1] / 60), 2)))
    w.append("")
    w.append("| Ewolucja | Tokeny (propozycja) | Minut zwykłych walk | Shardy peta = kopie (propozycja) |")
    w.append("|---|---:|---:|---:|")
    for i in range(ZALOZENIA["ewolucje"]):
        w.append("| %d. | %d | %s | %d |" % (i + 1, ZALOZENIA["tokeny_na_ewolucje"][i],
                                            liczba(ZALOZENIA["tokeny_na_ewolucje"][i] / tok_min, 0),
                                            ZALOZENIA["kopie_na_ewolucje"][i]))
    w.append("")
    # kopie z jajek
    zl_min = T.na_minute(Lz, "zloto")
    kop = sum(ZALOZENIA["kopie_na_ewolucje"])
    w.append("**Kopie peta z jajek** (jedna kopia = jeden shard, D-058). Jajko z pięciu petów, szanse %s (przyjęte); "
             "komplet ewolucji = %d kopii + sam pet. Złoto gracza %d. poziomu z walk: %s na minutę." % (
                 " / ".join(proc(100 * x) for x in ZALOZENIA["szanse_jajka"]), kop, Lz, liczba(zl_min, 0)))
    w.append("")
    w.append("| Pet w jajku | Szansa | Jajek na komplet (śr.) | Godzin walki na Złoto: jajko %s / jajko %s | "
             "Wariant: kopii wg rzadkości | jajek | godzin: jajko %s / %s |" % (
                 liczba(ZALOZENIA["ceny_jajek"][0], 0), liczba(ZALOZENIA["ceny_jajek"][1], 0),
                 liczba(ZALOZENIA["ceny_jajek"][0], 0), liczba(ZALOZENIA["ceny_jajek"][1], 0)))
    w.append("|---|---:|---:|---|---:|---:|---|")
    jajka = {}
    c0, c1 = ZALOZENIA["ceny_jajek"]
    for i, p in enumerate(ZALOZENIA["szanse_jajka"]):
        n = (kop + 1) / p
        kr = ZALOZENIA["kopie_wg_rzadkosci"][i]
        n2 = (kr + 1) / p
        jajka[i] = (n, n2)
        w.append("| %d. (%s) | %s | %s | %s / %s | %d | %s | %s / %s |" % (
            i + 1, ["pospolity", "zwykły", "rzadki", "epicki", "legendarny"][i], proc(100 * p), liczba(n, 0),
            liczba(n * c0 / zl_min / 60, 1), liczba(n * c1 / zl_min / 60, 1), kr, liczba(n2, 0),
            liczba(n2 * c0 / zl_min / 60, 1), liczba(n2 * c1 / zl_min / 60, 1)))
    w.append("")
    return {"farm": farm, "shard": tabela_sh, "tokeny_min": tok_min, "zloto_min": zl_min, "jajka": jajka}


# ------------------------------------------------------------------------------------------------ czesc 4: Gemy
def zrodla_gemow(nazwa):
    """Zestawy zrodel Gemow (propozycje do porownania; dzis = dane_walki.json)."""
    z = {"dzis": dict(mnoznik_lupu=1.0, za_poziom=0, za_straznika=0, kopalnia_h=0.0),
         "łup ×5": dict(mnoznik_lupu=5.0, za_poziom=0, za_straznika=0, kopalnia_h=0.0),
         "łup ×5 + kamienie milowe": dict(mnoznik_lupu=5.0, za_poziom=10, za_straznika=100, kopalnia_h=0.0),
         "łup ×5 + milowe + kopalnia": dict(mnoznik_lupu=5.0, za_poziom=10, za_straznika=100, kopalnia_h=30.0)}
    return z[nazwa]


ZESTAWY_GEMOW = ["dzis", "łup ×5", "łup ×5 + kamienie milowe", "łup ×5 + milowe + kopalnia"]


def gemy_w_czasie(T, nazwa_planu, zrodla, udzial=0.0, krok=1.0):
    """Gemy zebrane do konca kazdego biomu: lup zwyklych walk (szansa z danych x mnoznik), pierwsze pokonanie strazn-
    ika biomu (szansa z danych x mnoznik, z jednej proby, + premia za_straznika), kamien milowy za kazdy poziom,
    kopalnia diamentow od ZALOZENIA['kopalnie_od_poziomu'] (Gemow/h na 1. poziomie budynku, kolejny poziom budynku
    co 5 poziomow gracza x1,25)."""
    gr = granice(T, nazwa_planu, udzial)
    st = silnik.PRZECIWNICY["straznik_lasu"]["lup"]["szansa_gemow"]
    gemy, t, L_pop, out = 0.0, 0.0, 1, []
    for b in gr:
        while t < b["do"] - 1e-9:
            L = max(1, int(T.poziom((1 - udzial) * t)))
            gemy += T.na_minute(L, "gemy") * zrodla["mnoznik_lupu"] * (1 - udzial) * krok
            if L >= ZALOZENIA["kopalnie_od_poziomu"] and zrodla["kopalnia_h"] > 0:
                n = (L - ZALOZENIA["kopalnie_od_poziomu"]) // ZALOZENIA["poziom_budynku_co"]
                gemy += zrodla["kopalnia_h"] * 1.25 ** n * krok / 60
            if L > L_pop:
                gemy += zrodla["za_poziom"] * (L - L_pop)
                L_pop = L
            t += krok
        gemy += min(1.0, st * zrodla["mnoznik_lupu"]) + zrodla["za_straznika"]
        out.append({"biom": b["biom"], "do": b["do"], "L": b["L_do"], "gemy": gemy})
    return out


def czesc_4(T, w):
    w.append("## 4. Gemy na drzewka a czas gry (10 godzin do ostatniego biomu)")
    w.append("")
    wezly = wezly_drzewka()
    kz = koszty_zakladek(wezly)
    w.append("Koszt drzewek w dzisiejszych danych (`src/shared/SkillTreeData.luau`: korzeń %d, poziom węzła = "
             "(10 + 5 × głębokość) × numer poziomu): **Player %s, Fortress %s, Pets %s, razem %s Gemów**." % (
                 wezly[0]["koszt"][0], liczba(kz["Player"], 0), liczba(kz["Fortress"], 0), liczba(kz["Pets"], 0),
                 liczba(sum(kz.values()), 0)))
    w.append("")
    g_dzis = silnik.PRZECIWNICY
    w.append("Dziś Gemy wypadają tylko z łupu (`dane_walki.json`): zwykły potwór %s–%s, troll %s, strażnik %s szansy na "
             "1 Gem za wygraną. Zestawy do porównania (propozycje): „łup ×5” — pięć razy większe szanse; „kamienie "
             "milowe” — +10 Gemów za każdy poziom i +100 za pierwsze pokonanie strażnika biomu; „kopalnia” — kopalnia "
             "diamentów od %d. poziomu, 30 Gemów/h na 1. poziomie budynku i ×1,25 co poziom budynku (co 5 poziomów "
             "gracza). Kopalnia liczy tylko czas gry (bez dochodu offline)." % (
                 proc(100 * g_dzis["lesny_slime"]["lup"]["szansa_gemow"]),
                 proc(100 * g_dzis["muchomornik"]["lup"]["szansa_gemow"]),
                 proc(100 * g_dzis["lesny_troll"]["lup"]["szansa_gemow"]),
                 proc(100 * g_dzis["straznik_lasu"]["lup"]["szansa_gemow"]), ZALOZENIA["kopalnie_od_poziomu"]))
    w.append("")
    dane = {}
    for nazwa_planu in ("rosnący", "równy"):
        w.append("### Plan %s — Gemy zebrane do końca biomu (w nawiasie: procent kosztu drzewka Player, które da się kupić)"
                 % nazwa_planu)
        w.append("")
        w.append("| Biom | Koniec (min) | Poziom | " + " | ".join(ZESTAWY_GEMOW) + " |")
        w.append("|---|---:|---:|" + "---:|" * len(ZESTAWY_GEMOW))
        kol = {z: gemy_w_czasie(T, nazwa_planu, zrodla_gemow(z)) for z in ZESTAWY_GEMOW}
        dane[nazwa_planu] = kol
        for i in range(8):
            b = kol["dzis"][i]
            w.append("| %s | %s | %d | %s |" % (b["biom"], liczba(b["do"], 0), b["L"], " | ".join(
                "%s (%s)" % (liczba(kol[z][i]["gemy"], 0), proc(kupione_za(wezly, "Player", kol[z][i]["gemy"])))
                for z in ZESTAWY_GEMOW)))
        w.append("")
    # sloty umiejetnosci sa w drzewku (D-055, D-088): kiedy gracza na nie stac
    ks = koszt_slotow(wezly)
    w.append("**Sloty umiejętności są w drzewku** (D-055, D-088; gałąź Skills): 1. slot kosztuje z korzeniem %d Gemów, "
             "2. — razem %d, 3. — razem %d (z węzłami po drodze na 1. poziomie). Model balansu walki zakłada sloty od "
             "1., 5. i 10. poziomu. Komórka: biom, na którego końcu gracz ma już Gemy na kolejne sloty (1. / 2. / 3.; "
             "„—” = nie w 8 biomach):" % tuple(ks))
    w.append("")
    w.append("| Plan | " + " | ".join(ZESTAWY_GEMOW) + " |")
    w.append("|---|" + "---|" * len(ZESTAWY_GEMOW))
    sloty_kiedy = {}
    for nazwa_planu in ("rosnący", "równy"):
        kom = []
        for z in ZESTAWY_GEMOW:
            kiedy = []
            for c in ks:
                b = next((x for x in dane[nazwa_planu][z] if x["gemy"] >= c), None)
                kiedy.append("%s (poz. %d)" % (b["biom"], b["L"]) if b else "—")
            sloty_kiedy[(nazwa_planu, z)] = kiedy
            kom.append(" / ".join(kiedy))
        w.append("| %s | %s |" % (nazwa_planu, " | ".join(kom)))
    w.append("")
    potrzeba = {f: f * kz["Player"] / 10.0 for f in (0.25, 0.5, 1.0)}
    w.append("Ile Gemów na godzinę gry trzeba, żeby gracz bez płacenia kupił w 10 godzin 25%% / 50%% / 100%% drzewka "
             "Player: **%s / %s / %s Gemów/h** (dziś łup daje ok. %s Gemu/h)." % (
                 liczba(potrzeba[0.25], 0), liczba(potrzeba[0.5], 0), liczba(potrzeba[1.0], 0),
                 liczba(60 * T.na_minute(10, "gemy"), 1)))
    w.append("")
    return {"koszty": kz, "kolumny": dane, "potrzeba": potrzeba, "sloty": ks, "sloty_kiedy": sloty_kiedy}


# ------------------------------------------------------------------------------------------------ czesc 5: pytanie 40
PODEJSCIA_40 = [("dziś (limit uniku klasy już jest: Wojownik 24,2%)", None, 1.0),
                ("(a') niższy limit uniku Wojownika: 15%", "limit_uniku_15", 1.0),
                ("(b) połowa przyrostu Zręczności z treningu u Wojownika", None, 0.5),
                ("(c) blok i unik się nie sumują (jedna szansa)", "jedna_szansa", 1.0)]


def czesc_5(liczydlo, N, S, w):
    w.append("## 5. Pytanie 40: Wojownik z tarczą i unikiem")
    w.append("")
    Ls = [10, 30]
    ulamki = [0.0, 0.25, 0.5, 1.0]
    MON = [p["id"] for p in silnik.PRZECIWNICY_LISTA]
    zad = []
    for ia, (_, war, mz) in enumerate(PODEJSCIA_40):
        for L in Ls:
            for f in ulamki:
                T_ = int(round(f * wzorcowe.pula(L)))
                wd = wzorcowe.postac("wojownik", L, dodatkowe={"zrecznosc": int(round(T_ * mz))} if T_ else None)
                wr = trenowany("wojownik", L, wzorcowe.rozdziel(wzorcowe.ROZKLADY["wojownik"], T_) if T_ else {})
                zd = wzorcowe.postac("zwiadowca", L, dodatkowe={"zrecznosc": T_} if T_ else None)
                for nazwa, g in (("W_zr", wd), ("W_roz", wr), ("Z_zr", zd)):
                    for p in MON:
                        zad.append(((ia, L, f, nazwa, p), g, {"potwor": p, "poziom": L}, S, N, war, []))
                for b in KLASY:
                    op = trenowany(b, L, wzorcowe.rozdziel(wzorcowe.ROZKLADY[b], T_) if T_ else {})
                    for nazwa, g in (("W_zr", wd), ("W_roz", wr)):
                        zad.append(((ia, L, f, nazwa, "pvp_g", b), g, {"postac": op}, S, N, war, []))
                        zad.append(((ia, L, f, nazwa, "pvp_w", b), op, {"postac": g}, S, N, war, []))
            # rownosc klas przy danym podejsciu (postacie wzorcowe)
            for k in KLASY:
                for p in MON:
                    zad.append(((ia, L, "rown", k, p), wzorcowe.postac(k, L), {"potwor": p, "poziom": L}, S, N, war, []))
                for b in KLASY:
                    if b != k:
                        zad.append(((ia, L, "rown", k, b), wzorcowe.postac(k, L), {"postac": wzorcowe.postac(b, L)},
                                    S, N, war, []))
    r = liczydlo.licz(zad)

    def duel(ia, L, f, nazwa, b):
        return (r[(ia, L, f, nazwa, "pvp_g", b)]["proc"] + 100 - r[(ia, L, f, nazwa, "pvp_w", b)]["proc"]) / 2

    def mon(ia, L, f, nazwa):
        return statistics.mean(r[(ia, L, f, nazwa, p)]["proc"] for p in MON)
    w.append("Wojownik z tarczą (blok 5%% + 28,3%%) trenuje Zręczność: T dodatkowych punktów (ułamek puli poziomu) idzie w "
             "Zręczność; przeciwnicy w pojedynkach mają te same T punktów rozdane rozkładem swojej klasy (równy wkład). "
             "Dla porównania ten sam Wojownik z T rozdanym rozkładem klasy i Zwiadowca z T w Zręczności. %d walk na "
             "parę, pojedynki średnio z obu miejsc." % N)
    w.append("")
    w.append("| Podejście | Poziom | T (ułamek puli) | Wojownik T w Zręczność: z potworami / z Wojownikiem / Zwiadowcą / Magiem | "
             "Wojownik T rozkładem: z potworami / z Wojownikiem / Zwiadowcą / Magiem | Zwiadowca T w Zręczność: z potworami | "
             "Unik + blok Wojownika (T w Zr.) | Długość: tury (mediana) / czas z potworami |")
    w.append("|---|---:|---:|---|---|---:|---|---|")
    dane = {}
    for ia, (opis, war, mz) in enumerate(PODEJSCIA_40):
        for L in Ls:
            for f in ulamki:
                T_ = int(round(f * wzorcowe.pula(L)))
                wd = wzorcowe.postac("wojownik", L, dodatkowe={"zrecznosc": int(round(T_ * mz))} if T_ else None)
                with wariant_silnika(war):
                    v = silnik.wartosci_postaci(wd)
                u = v["unik"]
                b_ = (max(0, v["blok"] - u) if war == "jedna_szansa" else (1 - u) * v["blok"])
                tury = statistics.mean(r[(ia, L, f, "W_zr", p)]["tury_med"] for p in MON)
                czas = statistics.mean(r[(ia, L, f, "W_zr", p)]["czas"] for p in MON)
                d = {"mon_zr": mon(ia, L, f, "W_zr"), "mon_roz": mon(ia, L, f, "W_roz"), "mon_z": mon(ia, L, f, "Z_zr"),
                     "duel_zr": {b: duel(ia, L, f, "W_zr", b) for b in KLASY},
                     "duel_roz": {b: duel(ia, L, f, "W_roz", b) for b in KLASY}, "unik": u, "blok": b_,
                     "tury": tury, "czas": czas}
                dane[(ia, L, f)] = d
                w.append("| %s | %d | %s | %s / %s / %s / %s | %s / %s / %s / %s | %s | %s + %s | %s / %s s |" % (
                    opis, L, liczba(f, 2), proc(d["mon_zr"]), proc(d["duel_zr"]["wojownik"]), proc(d["duel_zr"]["zwiadowca"]),
                    proc(d["duel_zr"]["mag"]), proc(d["mon_roz"]), proc(d["duel_roz"]["wojownik"]),
                    proc(d["duel_roz"]["zwiadowca"]), proc(d["duel_roz"]["mag"]), proc(d["mon_z"]), proc(100 * u),
                    proc(100 * b_), liczba(tury, 0), liczba(czas, 1)))
    w.append("")
    w.append("Skutek uboczny podejścia dla wszystkich klas (postacie wzorcowe bez treningu): największa różnica klas przy "
             "tym samym potworze i zakres pojedynków klas.")
    w.append("")
    w.append("| Podejście | Poziom | Różnica klas (potwory) | Pojedynki klas | Wygrane z potworami: Wojownik / Zwiadowca / Mag |")
    w.append("|---|---:|---:|---|---|")
    rown = {}
    for ia, (opis, war, mz) in enumerate(PODEJSCIA_40):
        if ia == 2:
            continue  # (b) nie zmienia postaci wzorcowych
        for L in Ls:
            roz = max(max(r[(ia, L, "rown", k, p)]["proc"] for k in KLASY) - min(r[(ia, L, "rown", k, p)]["proc"] for k in KLASY)
                      for p in MON)
            pv = [(r[(ia, L, "rown", a_, b_)]["proc"] + 100 - r[(ia, L, "rown", b_, a_)]["proc"]) / 2
                  for a_ in KLASY for b_ in KLASY if a_ != b_]
            sr = [statistics.mean(r[(ia, L, "rown", k, p)]["proc"] for p in MON) for k in KLASY]
            rown[(ia, L)] = (roz, min(pv), max(pv), sr)
            w.append("| %s | %d | %s pp | %s–%s | %s |" % (opis, L, liczba(roz), proc(min(pv)), proc(max(pv)),
                                                          " / ".join(proc(x) for x in sr)))
    w.append("")
    return {"tabela": dane, "rownosc": rown}


# ------------------------------------------------------------------------------------------------ czesc 6: trening
POLITYKI = ["rowno", "klasa"] + ["jedna:" + s for s in STAT]
NAZWY_POLITYK = {"rowno": "sześć po równo", "klasa": "rozkładem klasy"}
NAZWY_POLITYK.update({"jedna:" + s: "tylko " + NAZWY_STAT[s] for s in STAT})


def czesc_6(T, liczydlo, N, S, w):
    w.append("## 6. Trening: przyrost za trafienie i za serię, bez nadużywania jednej mini-gry")
    w.append("")
    tr = Trening()
    tr0 = Trening(wykladnik=0)
    z = ZALOZENIA
    w.append("**Wzór (propozycja):** punkty statystyki za trafienie = C × K × M / N0, gdzie N0 = %s trafień na punkt "
             "(pasek treningu), K = seria (0–4: ×1, 5–9: ×1,25, 10–19: ×1,5, od 20: ×2; średnio przyjęte ×%s), "
             "C = poziom centrum (%s; poziom centrum najwyżej numer biomu), M = 1 / (1 + W / (%s × pula))², "
             "W = punkty już wytrenowane w TEJ statystyce, pula = punkty statystyk z poziomu gracza (30 + 10 za "
             "poziom). Przy %s trafieniach na minutę świeża statystyka rośnie %s punktu na minutę (centrum 1)." % (
                 liczba(z["trafien_na_punkt"], 0), liczba(z["combo_srednie"], 1),
                 " / ".join(liczba(x, 1) for x in z["centrum"]), liczba(z["polowa_udzialu"], 2),
                 liczba(z["trafienia_na_min"], 0), liczba(tr.r, 1)))
    w.append("")
    # punkty na minute: walka a trening
    gr = granice(T, "rosnący", z["udzial_treningu"])
    w.append("| Biom (plan rosnący) | Poziomy | Punkty z poziomów na minutę walki | Trening: świeża statystyka / "
             "po %s puli w niej / po %s puli | Minut jednej mini-gry do połowy tempa |" % (
                 proc(100 * z["polowa_udzialu"]), proc(200 * z["polowa_udzialu"])))
    w.append("|---|---|---:|---|---:|")
    for b in gr:
        Lm = max(1, (b["L_od"] + b["L_do"]) // 2)
        walka = 10 * (b["L_do"] - b["L_od"]) / ((1 - z["udzial_treningu"]) * (b["do"] - b["od"]))
        H = z["polowa_udzialu"] * wzorcowe.pula(Lm)
        r0 = tr.tempo(0, Lm, b["i"])
        t_pol = H / (3 * r0) * ((2 ** 0.5) ** 3 - 1)  # (1 + W/H)^2 = 2
        w.append("| %s | %d → %d | %s | %s / %s / %s | %s |" % (
            b["biom"], b["L_od"], b["L_do"], liczba(walka, 2), liczba(r0, 1), liczba(tr.tempo(H, Lm, b["i"]), 1),
            liczba(tr.tempo(2 * H, Lm, b["i"]), 1), liczba(t_pol, 1)))
    w.append("")
    # przebiegi: punkty z treningu na koncu biomow 1, 4 i 7 dla polityk i dwoch wzorow
    kontrola = [gr[0]["do"], gr[3]["do"], gr[6]["do"]]
    przeb = {}
    for k in KLASY:
        for wz, t_ in (("propozycja", tr), ("bez malejącego", tr0)):
            for pol in POLITYKI:
                przeb[(k, wz, pol)] = przebieg_treningu(T, t_, k, "rosnący", z["udzial_treningu"], pol, kontrola)
    w.append("Punkty z treningu (gracz trenuje %s czasu gry, plan rosnący) na końcu Lasu, Pustyni i Wulkanicznego — "
             "razem i jako procent puli z poziomów (Wojownik; inne klasy tak samo przy „po równo” i „tylko jednej”):" %
             proc(100 * z["udzial_treningu"]))
    w.append("")
    w.append("| Wzór | Polityka | " + " | ".join("%s (poz. %d)" % (b["biom"], b["L_do"]) for b in (gr[0], gr[3], gr[6])) + " |")
    w.append("|---|---|---:|---:|---:|")
    for wz in ("propozycja", "bez malejącego"):
        for pol in ["rowno", "klasa", "jedna:kondycja"]:
            kom = []
            for t in kontrola:
                L, W = przeb[("wojownik", wz, pol)][t]
                kom.append("%s (%s)" % (liczba(sum(W.values()), 0), proc(100 * sum(W.values()) / wzorcowe.pula(int(L)))))
            w.append("| %s | %s | %s |" % (wz, NAZWY_POLITYK[pol], " | ".join(kom)))
    w.append("")
    # symulacje: postac z treningiem kontra potwory i kontra „rozkladem klasy” (ten sam czas treningu)
    MON = [p["id"] for p in silnik.PRZECIWNICY_LISTA]
    zad = []
    for k in KLASY:
        for t in kontrola:
            L = int(przeb[(k, "propozycja", "rowno")][t][0])
            g0 = wzorcowe.postac(k, L)
            for p in MON:
                zad.append(((k, t, "gołe", "", p), g0, {"potwor": p, "poziom": L}, S, N, None, []))
            for wz in ("propozycja", "bez malejącego"):
                ref = trenowany(k, L, przeb[(k, wz, "klasa")][t][1])
                for pol in POLITYKI:
                    g = trenowany(k, L, przeb[(k, wz, pol)][t][1])
                    for p in MON:
                        zad.append(((k, t, wz, pol, p), g, {"potwor": p, "poziom": L}, S, N, None, []))
                    zad.append(((k, t, wz, pol, "pvp_g"), g, {"postac": ref}, S, N, None, []))
                    zad.append(((k, t, wz, pol, "pvp_w"), ref, {"postac": g}, S, N, None, []))
    r = liczydlo.licz(zad)
    dane = {}
    for wz in ("propozycja", "bez malejącego"):
        w.append("### Wzór: %s" % wz)
        w.append("")
        w.append("Komórka: średnie wygrane z pięcioma potworami lasu poziomu gracza (zmiana względem tej samej postaci bez "
                 "treningu, pp) / pojedynek z tą samą klasą, która trenowała tyle samo czasu rozkładem klasy (oba "
                 "miejsca). %d walk na parę." % N)
        w.append("")
        w.append("| Klasa | Koniec biomu | " + " | ".join(NAZWY_POLITYK[p] for p in POLITYKI) + " |")
        w.append("|---|---|" + "---|" * len(POLITYKI))
        for k in KLASY:
            for t in kontrola:
                L = int(przeb[(k, wz, "rowno")][t][0])
                baza = statistics.mean(r[(k, t, "gołe", "", p)]["proc"] for p in MON)
                kom = []
                for pol in POLITYKI:
                    mon = statistics.mean(r[(k, t, wz, pol, p)]["proc"] for p in MON)
                    du = (r[(k, t, wz, pol, "pvp_g")]["proc"] + 100 - r[(k, t, wz, pol, "pvp_w")]["proc"]) / 2
                    dane[(wz, k, t, pol)] = {"mon": mon, "delta": mon - baza, "duel": du,
                                             "punkty": sum(przeb[(k, wz, pol)][t][1].values())}
                    kom.append("%s / %s" % (pp(mon - baza), proc(du)))
                nazwa_b = next(b["biom"] for b in gr if abs(b["do"] - t) < 1e-6)
                w.append("| %s | %s (poz. %d) | %s |" % (NAZWY[k], nazwa_b, L, " | ".join(kom)))
        w.append("")
    return {"przebiegi": przeb, "wyniki": dane, "kontrola": kontrola, "granice": gr}


# ------------------------------------------------------------------------------------------------ main
def tabela_tempa(T, w):
    w.append("## Tempo: poziom gracza na granicach biomów")
    w.append("")
    w.append("Ta sama krzywa co w `tempo.py` (11,71 × L^1,6, cykl walki gracza wzorcowego). Plan rosnący i równy z D-076; "
             "8. biom: %s min (rosnący) i %s min (równy) — przyjęte, tylko do „wyjścia” z ostatniego biomu. Gracz, który "
             "trenuje 20%% czasu, walczy 80%% czasu, więc jest niżej." % (
                 liczba(ZALOZENIA["osmy_biom_min"]["rosnący"], 0), liczba(ZALOZENIA["osmy_biom_min"]["równy"], 0)))
    w.append("")
    w.append("| Biom | Rosnący: minuty | poziom bez treningu | z 20% treningu | Równy: minuty | poziom bez treningu | z 20% treningu |")
    w.append("|---|---|---|---|---|---|---|")
    a0, a2 = granice(T, "rosnący"), granice(T, "rosnący", ZALOZENIA["udzial_treningu"])
    b0, b2 = granice(T, "równy"), granice(T, "równy", ZALOZENIA["udzial_treningu"])
    for i in range(8):
        w.append("| %s | %s–%s | %d → %d | %d → %d | %s–%s | %d → %d | %d → %d |" % (
            a0[i]["biom"], liczba(a0[i]["od"], 0), liczba(a0[i]["do"], 0), a0[i]["L_od"], a0[i]["L_do"], a2[i]["L_od"],
            a2[i]["L_do"], liczba(b0[i]["od"], 0), liczba(b0[i]["do"], 0), b0[i]["L_od"], b0[i]["L_do"], b2[i]["L_od"],
            b2[i]["L_do"]))
    w.append("")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kalkulator balansu 17.11 (propozycja liczb)")
    ap.add_argument("--czesci", default="1,2,3,4,5,6")
    ap.add_argument("--ziaren", type=int, default=800, help="walk na pare w symulacjach")
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--procesy", type=int, default=3)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    czesci = set(a.czesci.split(","))
    t0 = time.time()
    T = Tempo()
    liczydlo = Liczydlo(a.procesy) if czesci & {"1", "3", "5", "6"} else None
    w = ["# Kalkulator balansu 17.11 — wynik (propozycja liczb, nie kanon)", ""]
    tabela_tempa(T, w)
    if "1" in czesci:
        czesc_1(T, liczydlo, a.ziaren, a.start, w)
    if "2" in czesci:
        czesc_2(T, w)
    if "3" in czesci:
        czesc_3(T, liczydlo, max(a.ziaren, 1000), a.start, w)
    if "4" in czesci:
        czesc_4(T, w)
    if "5" in czesci:
        czesc_5(liczydlo, a.ziaren, a.start, w)
    if "6" in czesci:
        czesc_6(T, liczydlo, a.ziaren, a.start, w)
    w.append("_Policzone w %.0f s (python -B tools/walka/progresja.py --ziaren %d --start %d --czesci %s)._" % (
        time.time() - t0, a.ziaren, a.start, a.czesci))
    tekst = "\n".join(w) + "\n"
    print(tekst)
    if a.md:
        with open(a.md, "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)


if __name__ == "__main__":
    main()
