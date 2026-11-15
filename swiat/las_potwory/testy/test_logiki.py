# -*- coding: utf-8 -*-
"""Testy offline pakietu „potwory w ruchu” (PROJEKT.md rozdz. 9.1, punkty 1–7). Bez Studio, bez sieci.

    python -B swiat/las_potwory/testy/test_logiki.py        (unittest; kod 1 przy błędzie)

1. Przypadki wzorcowe z tabeli 3.7a (te same 70 wywołań co Logika.sprawdzPrzypadki() w Luau).
2. Odstęp: symulacja każdej strefy przez 30 min (dt 0,25 s) przy cel = max z losowymi walkami — luka czoło → ogon
   ≥ 25, żadna grupa się nie cofa ani nie robi kroku > v·dt, po wyłączeniu walk na 120 s każdy czekający wchodzi.
   Klasa Symulacja to WIERNA KOPIA tyknięcia SerwerPotworow.server.luau (te same kroki i ta sama kolejność: koniec
   zajętości → krokGrup → członkowie → wychodzący → czekający; odradzanie raz na sekundę, od recenzji także z
   karuzelą domów, blokadą 18 i wyjątkiem Strażnika jak w serwerze). Zmieniasz serwer — zmień ją.
3. Pojemność, 4. liczby celu (35 / 64 / 86), 5. geometria danych, 6. przeliczenie las → świat, 7. generator.
8. Brzegi (dopisane przy recenzji): 0 i 1 gracz, minimum odrodzenia 10 s, Strażnik (strefa z jednym punktem, L = 0),
   wszystkie domy zablokowane, nadmiar potworów po odejściu graczy, potrójne uruchomienie generatora, kolejność
   kroków serwera (prosty wykrywacz rozjazdu lustra z Luau).
"""
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
sys.path.insert(0, PAKIET)
import logika as Lg  # noqa: E402
import generuj_dane  # noqa: E402

INF = math.inf
TOL = 1e-4

T1 = {"x": [0, 10, 10], "y": [0, 0, 0], "z": [0, 0, 10], "dl": [0, 10, 20, 34.1421356], "L": 34.1421356,
      "zamknieta": True}
T2 = {"x": [0, 10, 10], "y": [0, 0, 0], "z": [0, 0, 10], "dl": [0, 10, 20], "L": 40, "zamknieta": False}
F = False
P = True

# (opis, funkcja bez argumentów, oczekiwany wynik) — dokładnie tabela 3.7a, w tej samej kolejności co w Logika.luau
PRZYPADKI = [
    ("cel(6,9,0)", lambda: Lg.cel(6, 9, 0), 3),
    ("cel(6,9,1)", lambda: Lg.cel(6, 9, 1), 3),
    ("cel(6,9,4)", lambda: Lg.cel(6, 9, 4), 4),
    ("cel(6,9,8)", lambda: Lg.cel(6, 9, 8), 6),
    ("cel(6,9,14)", lambda: Lg.cel(6, 9, 14), 8),
    ("cel(6,9,20)", lambda: Lg.cel(6, 9, 20), 9),
    ("cel(6,9,50)", lambda: Lg.cel(6, 9, 50), 9),
    ("cel(2,3,1)", lambda: Lg.cel(2, 3, 1), 1),
    ("cel(2,3,20)", lambda: Lg.cel(2, 3, 20), 3),
    ("cel(5,7,4)", lambda: Lg.cel(5, 7, 4), 4),
    ("cel(1,1,20)", lambda: Lg.cel(1, 1, 20), 1),
    ("cel(3,4,12)", lambda: Lg.cel(3, 4, 12), 3),
    ("czasOdrodzenia(15,0)", lambda: Lg.czas_odrodzenia(15, 0), 15),
    ("czasOdrodzenia(15,1)", lambda: Lg.czas_odrodzenia(15, 1), 15),
    ("czasOdrodzenia(15,4)", lambda: Lg.czas_odrodzenia(15, 4), 10.3448),
    ("czasOdrodzenia(25,4)", lambda: Lg.czas_odrodzenia(25, 4), 17.2414),
    ("czasOdrodzenia(15,8)", lambda: Lg.czas_odrodzenia(15, 8), 10),
    ("czasOdrodzenia(25,8)", lambda: Lg.czas_odrodzenia(25, 8), 12.1951),
    ("czasOdrodzenia(20,3)", lambda: Lg.czas_odrodzenia(20, 3), 15.3846),
    ("przod(10,5,100)", lambda: Lg.przod(10, 5, 100), 95),
    ("przod(90,10,100)", lambda: Lg.przod(90, 10, 100), 20),
    ("przod(3,3,100)", lambda: Lg.przod(3, 3, 100), 0),
    ("przod(1,2,0)", lambda: Lg.przod(1, 2, 0), INF),
    ("punktTrasy(T1,0)", lambda: Lg.punkt_trasy(T1, 0), (0, 0, 0, -1.5708)),
    ("punktTrasy(T1,5)", lambda: Lg.punkt_trasy(T1, 5), (5, 0, 0, -1.5708)),
    ("punktTrasy(T1,10)", lambda: Lg.punkt_trasy(T1, 10), (10, 0, 0, -1.5708)),
    ("punktTrasy(T1,15)", lambda: Lg.punkt_trasy(T1, 15), (10, 0, 5, 3.1416)),
    ("punktTrasy(T1,27.0710678)", lambda: Lg.punkt_trasy(T1, 27.0710678), (5, 0, 5, 0.7854)),
    ("punktTrasy(T1,34.1421356)", lambda: Lg.punkt_trasy(T1, 34.1421356), (0, 0, 0, -1.5708)),
    ("punktTrasy(T1,-5)", lambda: Lg.punkt_trasy(T1, -5), (3.5355, 0, 3.5355, 0.7854)),
    ("punktTrasy(T2,0)", lambda: Lg.punkt_trasy(T2, 0), (0, 0, 0, -1.5708)),
    ("punktTrasy(T2,15)", lambda: Lg.punkt_trasy(T2, 15), (10, 0, 5, 3.1416)),
    ("punktTrasy(T2,20)", lambda: Lg.punkt_trasy(T2, 20), (10, 0, 10, 3.1416)),
    ("punktTrasy(T2,25)", lambda: Lg.punkt_trasy(T2, 25), (10, 0, 5, 0)),
    ("punktTrasy(T2,35)", lambda: Lg.punkt_trasy(T2, 35), (5, 0, 0, 1.5708)),
    ("punktTrasy(T2,40)", lambda: Lg.punkt_trasy(T2, 40), (0, 0, 0, -1.5708)),
    ("krokGrup({0,30})", lambda: Lg.krok_grup([0, 30], [0, 0], [F, F], 100, 2.5, 25), [2.5, 32.5]),
    ("krokGrup({0,26})", lambda: Lg.krok_grup([0, 26], [0, 0], [F, F], 100, 2.5, 25), [2.5, 28.5]),
    ("krokGrup({0,30} stoi 2)", lambda: Lg.krok_grup([0, 30], [0, 0], [F, P], 100, 2.5, 25), [2.5, 30]),
    ("krokGrup(4 grupy)", lambda: Lg.krok_grup([0, 25.3, 50.6, 75.9], [0, 0, 0, 0], [F, F, F, F], 101.2, 1.5, 25),
     [1.5, 26.8, 52.1, 77.4]),
    ("krokGrup(4 grupy, stoi 4)", lambda: Lg.krok_grup([0, 25.3, 50.6, 75.9], [0, 0, 0, 0], [F, F, F, P], 101.2, 1.5,
                                                         25), [0.9, 25.9, 50.9, 75.9]),
    ("krokGrup({0} dł 38.1)", lambda: Lg.krok_grup([0], [38.1], [F], 63, 2.5, 25), [0]),
    ("krokGrup(L=0)", lambda: Lg.krok_grup([5, 10], [0, 0], [F, P], 0, 1, 25), [5, 10]),
    ("przodDo(10,{30,5})", lambda: Lg.przod_do(10, [30, 5], [0, 0], 100), 20),
    ("przodDo(10,{20},{15})", lambda: Lg.przod_do(10, [20], [15], 100), -5),
    ("przodDo(10,{})", lambda: Lg.przod_do(10, [], [], 100), INF),
    ("tylDo(10,{30,5})", lambda: Lg.tyl_do(10, [30, 5], 100), 5),
    ("tylDo(10,{})", lambda: Lg.tyl_do(10, [], 100), INF),
    ("minal(98,1,0,100)", lambda: Lg.minal(98, 1, 0, 100), True),
    ("minal(10,12.5,12,100)", lambda: Lg.minal(10, 12.5, 12, 100), True),
    ("minal(10,12.5,13,100)", lambda: Lg.minal(10, 12.5, 13, 100), True),
    ("minal(10,10,10.3,100)", lambda: Lg.minal(10, 10, 10.3, 100), True),
    ("minal(10,10,11,100)", lambda: Lg.minal(10, 10, 11, 100), False),
    ("minal(5,5,7,0)", lambda: Lg.minal(5, 5, 7, 0), True),
    ("wGrupie(5,1,12.7,100)", lambda: Lg.w_grupie(5, 1, 12.7, 100), 5),
    ("wGrupie(5,3,12.7,100)", lambda: Lg.w_grupie(5, 3, 12.7, 100), 79.6),
    ("wGrupie(5,2,12.7,0)", lambda: Lg.w_grupie(5, 2, 12.7, 0), 0),
    ("rozdzialStartowy(3,9,1)", lambda: Lg.rozdzial_startowy(3, 9, 1), [[1, 1], [4, 1], [7, 1]]),
    ("rozdzialStartowy(3,2,5)", lambda: Lg.rozdzial_startowy(3, 2, 5), [[1, 1], [2, 1], [1, 2]]),
    ("rozdzialStartowy(2,1,4)", lambda: Lg.rozdzial_startowy(2, 1, 4), [[1, 1], [1, 2]]),
    ("#rozdzialStartowy(12,2,5)", lambda: len(Lg.rozdzial_startowy(12, 2, 5)), 10),
    ("poczatkowePolozenia(7,177.3)", lambda: Lg.poczatkowe_polozenia(7, 177.3),
     [0, 25.3286, 50.6571, 75.9857, 101.3143, 126.6429, 151.9714]),
    ("wolnyDom(3 domy, ostatni 0)", lambda: Lg.wolny_dom([[0, 0], [100, 0], [0, 100]], [[5, 5]], 0, 18), 2),
    ("wolnyDom(3 domy, ostatni 2)", lambda: Lg.wolny_dom([[0, 0], [100, 0], [0, 100]], [[5, 5]], 2, 18), 3),
    ("wolnyDom(2 domy zajęte)", lambda: Lg.wolny_dom([[0, 0], [100, 0]], [[5, 5], [95, 0]], 1, 18), None),
    ("wolnyDom(gracz na 18)", lambda: Lg.wolny_dom([[0, 0]], [[18, 0]], 1, 18), 1),
    ("krokDo(0,0,3,4,2)", lambda: Lg.krok_do(0, 0, 3, 4, 2), (1.2, 1.6, False)),
    ("krokDo(0,0,3,4,6)", lambda: Lg.krok_do(0, 0, 3, 4, 6), (3, 4, True)),
    ("swiatZLasu(206.3,0,294.5)", lambda: Lg.swiat_z_lasu(206.3, 0, 294.5), (-206.3, 0, -2294.5)),
    ("swiatZLasu(0,32,-373)", lambda: Lg.swiat_z_lasu(0, 32, -373), (0, 32, -1627)),
]


def zgodne(a, b):
    """Porównanie wyniku z oczekiwanym: liczby z tolerancją 1e-4, nieskończoność dokładnie, listy element po elemencie."""
    if isinstance(b, bool) or b is None:
        return a is b or a == b and type(a) is type(b)
    if isinstance(b, (int, float)):
        if isinstance(a, bool) or not isinstance(a, (int, float)):
            return False
        if math.isinf(b):
            return math.isinf(a) and (a > 0) == (b > 0)
        return abs(a - b) <= TOL
    if isinstance(b, (list, tuple)):
        if not isinstance(a, (list, tuple)) or len(a) != len(b):
            return False
        return all(zgodne(x, y) for x, y in zip(a, b))
    return a == b


def w_wielokacie(x, z, wielokat):
    wewnatrz = False
    n = len(wielokat)
    for i in range(n):
        x1, z1 = wielokat[i]
        x2, z2 = wielokat[(i + 1) % n]
        if (z1 > z) != (z2 > z):
            xc = x1 + (z - z1) * (x2 - x1) / (z2 - z1)
            if x < xc:
                wewnatrz = not wewnatrz
    return wewnatrz


# =========================================================================== symulacja (kopia tyknięcia serwera)
class Symulacja:
    """Jedna strefa, tak jak liczy ją SerwerPotworow: grupy (czoło `s`, `dlugosc`, rezerwacja, członkowie po miejscach),
    potwory w stanach wychodzi / czeka / chodzi, zajętość jako osobne pole (stan wewnętrzny się nie zmienia)."""

    def __init__(self, st, zasady, predkosc, cel, rnd):
        self.st, self.cel, self.rnd = st, cel, rnd
        self.odstep = zasady["odstep"]
        self.blokada_domu = zasady["blokadaDomu"]
        self.ostatni_dom = 0
        self.v = predkosc
        self.L = st["trasa"]["L"]
        self.grupy = []
        self.potwory = []
        self.kolejka = []
        self.licznik = 0
        self.min_luka = INF
        self.bledy = []
        # start (rozdz. 3.4): od razu na pętli
        if st["watahy"]:
            for s in Lg.poczatkowe_polozenia(st["grupy"], self.L):
                self.grupy.append(self.nowa_grupa(s, (st["miejsc"] - 1) * st["odstepWGrupie"], False))
            for g, m in Lg.rozdzial_startowy(cel, st["grupy"], st["miejsc"]):
                p = self.nowy_potwor("chodzi", 1)
                self.grupy[g - 1]["czlonkowie"][m] = p
                p["grupa"], p["miejsce"] = self.grupy[g - 1], m
        else:
            for s in Lg.poczatkowe_polozenia(cel, self.L):
                g = self.nowa_grupa(s, 0, False)
                self.grupy.append(g)
                p = self.nowy_potwor("chodzi", 1)
                g["czlonkowie"][1] = p
                p["grupa"], p["miejsce"] = g, 1

    def nowa_grupa(self, s, dlugosc, rezerwacja):
        return {"s": s, "s_stare": s, "dlugosc": dlugosc, "rezerwacja": rezerwacja, "czlonkowie": {}}

    def nowy_potwor(self, stan, dom):
        self.licznik += 1
        d = self.st["domy"][dom - 1]
        p = {"id": "%s-%d" % (self.st["id"], self.licznik), "stan": stan, "dom": dom, "x": d["x"], "z": d["z"],
             "grupa": None, "miejsce": 0, "rezerwacja": None, "zajety": None}
        self.potwory.append(p)
        return p

    def zajety_w(self, g):
        return any(p["zajety"] is not None for p in g["czlonkowie"].values())

    def usun(self, p):
        g = p["grupa"]
        if g is not None:
            if self.st["watahy"]:
                del g["czlonkowie"][p["miejsce"]]
            else:
                self.grupy.remove(g)
        if p["rezerwacja"] is not None:
            self.grupy.remove(p["rezerwacja"])
        self.potwory.remove(p)

    def sprobuj_wejsc(self, p):
        dom = self.st["domy"][p["dom"] - 1]
        if self.st["watahy"]:
            for g in self.grupy:
                for j in range(1, self.st["miejsc"] + 1):
                    if j in g["czlonkowie"]:
                        continue
                    s_s = Lg.w_grupie(g["s_stare"], j, self.st["odstepWGrupie"], self.L)
                    s_n = Lg.w_grupie(g["s"], j, self.st["odstepWGrupie"], self.L)
                    for s_w in dom["s"]:
                        if Lg.minal(s_s, s_n, s_w, self.L):
                            g["czlonkowie"][j] = p
                            p["grupa"], p["miejsce"], p["stan"] = g, j, "chodzi"
                            return
            return
        s_w = dom["s"][0]
        if p["rezerwacja"] is None:
            if len(self.grupy) < self.st["grupy"] and Lg.tyl_do(s_w, [g["s"] for g in self.grupy], self.L) >= self.odstep:
                g = self.nowa_grupa(s_w, 0, True)
                self.grupy.append(g)
                p["rezerwacja"] = g
        if p["rezerwacja"] is not None:
            inne = [g for g in self.grupy if g is not p["rezerwacja"]]
            if Lg.przod_do(s_w, [g["s"] for g in inne], [g["dlugosc"] for g in inne], self.L) >= self.odstep:
                g = p["rezerwacja"]
                g["rezerwacja"] = False
                g["czlonkowie"][1] = p
                p["grupa"], p["miejsce"], p["stan"], p["rezerwacja"] = g, 1, "chodzi", None

    def tyknij(self, teraz, dt):
        # 1. koniec zajętości
        for p in list(self.potwory):
            z = p["zajety"]
            if z is not None and teraz >= z["do"]:
                if z["wynik"] == "wygrana":
                    self.usun(p)
                else:
                    p["zajety"] = None
        krok = self.v * dt
        # 2. grupy
        if self.grupy:
            s = [g["s"] for g in self.grupy]
            dl = [g["dlugosc"] for g in self.grupy]
            stoi = [g["rezerwacja"] or self.zajety_w(g) for g in self.grupy]
            nowe = Lg.krok_grup(s, dl, stoi, self.L, krok, self.odstep)
            for g, n in zip(self.grupy, nowe):
                g["s_stare"], g["s"] = g["s"], n
                if self.L > 0:
                    przes = Lg.przod(g["s_stare"], n, self.L)
                    if przes > krok + 1e-6:
                        self.bledy.append("%.2f: grupa przesunęła się o %.4f > %.4f" % (teraz, przes, krok))
        # 3. wychodzący
        for p in self.potwory:
            if p["stan"] == "wychodzi" and p["zajety"] is None:
                wej = self.st["domy"][p["dom"] - 1]["wejscie"]
                p["x"], p["z"], doszedl = Lg.krok_do(p["x"], p["z"], wej[0], wej[1], krok)
                if doszedl:
                    p["stan"] = "czeka"
        # 4. czekający
        for p in self.potwory:
            if p["stan"] == "czeka" and p["zajety"] is None:
                self.sprobuj_wejsc(p)
        self.sprawdz_luki(teraz)

    def sprawdz_luki(self, teraz):
        prawdziwe = [g for g in self.grupy if not g["rezerwacja"]]
        if self.L <= 0:
            return
        for g in prawdziwe:
            luka = self.L - g["dlugosc"]
            for k in prawdziwe:
                if k is not g:
                    luka = min(luka, Lg.przod(g["s"], k["s"], self.L) - k["dlugosc"])
            if len(prawdziwe) > 1 or g["dlugosc"] > 0:
                self.min_luka = min(self.min_luka, luka)
            if luka < self.odstep - 1e-6:
                self.bledy.append("%.2f: luka %.4f < %s" % (teraz, luka, self.odstep))

    def gracze_w_strefie(self, gracze):
        """Kopia graczeWStrefie: gracze w poziomie ≤ zasiegGraczy od środka strefy."""
        cx, cz = self.st["srodek"][0], self.st["srodek"][2]
        return sum(1 for g in gracze if math.hypot(g[0] - cx, g[1] - cz) <= self.st["zasiegGraczy"])

    def odradzaj(self, teraz, gracze=(), G=None):
        """Kopia odradzaj() z SerwerPotworow dla jednej strefy (rozdz. 3.5): cel z liczby graczy G (None = stały
        self.cel), kolejka, karuzela wolnych domów (blokada 18; Strażnik bez blokady — poprawka recenzji).
        gracze = lista [x, z] położeń HumanoidRootPart wszystkich graczy serwera."""
        st = self.st
        if G is not None:
            self.cel = 1 if st["straznik"] else Lg.cel(st["naraz"], st["max"], G)
        brak = self.cel - len(self.potwory) - len(self.kolejka)
        if brak > 0:
            za_ile = (st["odrodzenieS"] if st["straznik"]
                      else Lg.czas_odrodzenia(st["odrodzenieS"], self.gracze_w_strefie(gracze)))
            for _ in range(brak):
                self.kolejka.append(teraz + za_ile)
            self.kolejka.sort()
        while self.kolejka and self.kolejka[0] <= teraz:
            if len(self.potwory) >= self.cel:
                self.kolejka.pop(0)  # graczy ubyło: wpis przepada
                continue
            blokada = 0 if st["straznik"] else self.blokada_domu
            i = Lg.wolny_dom([[d["x"], d["z"]] for d in st["domy"]], list(gracze), self.ostatni_dom, blokada)
            if i is None:
                break  # każdy dom ma gracza bliżej niż 18: wpis czeka do następnej sekundy
            self.kolejka.pop(0)
            self.ostatni_dom = i
            self.nowy_potwor("wychodzi", i)


def symuluj(st, zasady, predkosc, ziarno, minuty=30, dt=0.25):
    rnd = random.Random(ziarno)
    sym = Symulacja(st, zasady, predkosc, st["max"], rnd)
    kroki = int(minuty * 60 / dt)
    koniec_walk = minuty * 60 - 120
    nastepna_sekunda = 1.0
    for i in range(1, kroki + 1):
        teraz = i * dt
        if teraz < koniec_walk and rnd.random() < dt / 25:
            wolne = [p for p in sym.potwory if p["zajety"] is None]
            if wolne:
                p = rnd.choice(wolne)
                p["zajety"] = {"do": teraz + rnd.uniform(8, 40), "wynik": "wygrana" if rnd.random() < 0.6 else "przegrana"}
        sym.tyknij(teraz, dt)
        if teraz + 1e-9 >= nastepna_sekunda:
            sym.odradzaj(teraz)
            nastepna_sekunda += 1.0
    return sym


# =========================================================================== testy
class TestLogiki(unittest.TestCase):
    def test_1_przypadki_wzorcowe(self):
        self.assertEqual(len(PRZYPADKI), 70)
        zle = []
        for opis, f, oczekiwane in PRZYPADKI:
            wynik = f()
            if not zgodne(wynik, oczekiwane):
                zle.append("%s = %r, oczekiwano %r" % (opis, wynik, oczekiwane))
        self.assertEqual(zle, [], "\n".join(zle))

    def test_1b_luau_ma_ta_sama_tabele(self):
        """Logika.luau: te same 15 funkcji i te same 70 przypadków (opisy i oczekiwane wyniki) co ten plik."""
        with open(os.path.join(PAKIET, "zrodla", "Logika.luau"), encoding="utf-8") as f:
            zrodlo = f.read()
        funkcje = re.findall(r"^function L\.(\w+)\(", zrodlo, re.M)
        oczekiwane_funkcje = ["cel", "czasOdrodzenia", "przod", "yaw", "punktTrasy", "krokGrup", "przodDo", "tylDo",
                              "minal", "wGrupie", "rozdzialStartowy", "poczatkowePolozenia", "wolnyDom", "krokDo",
                              "swiatZLasu", "sprawdzPrzypadki"]
        self.assertEqual(sorted(funkcje), sorted(oczekiwane_funkcje))
        for nazwa in oczekiwane_funkcje[:-1]:
            mirror = re.sub(r"([A-Z])", lambda m: "_" + m.group(1).lower(), nazwa)
            self.assertTrue(callable(getattr(Lg, mirror, None)), "brak %s w logika.py" % mirror)
        tabela = zrodlo.split("local PRZYPADKI = {", 1)[1].split("\nfunction L.sprawdzPrzypadki", 1)[0]
        opisy = re.findall(r'opis = "([^"]*)"', tabela)
        self.assertEqual(opisy, [p[0] for p in PRZYPADKI])
        wyniki = []
        for m in re.finditer(r"\bw = ", tabela):
            i = m.end()
            if tabela[i] == "{":
                glebokosc, j = 0, i
                while True:
                    glebokosc += {"{": 1, "}": -1}.get(tabela[j], 0)
                    j += 1
                    if glebokosc == 0:
                        break
                tekst = tabela[i:j]
            else:
                tekst = re.match(r"[^,}\n]+", tabela[i:]).group(0).strip()
            tekst = tekst.replace("{", "[").replace("}", "]")
            tekst = re.sub(r"\bHUGE\b", "inf", tekst)
            tekst = re.sub(r"\bnil\b", "None", tekst)
            tekst = re.sub(r"\btrue\b", "True", tekst)
            tekst = re.sub(r"\bfalse\b", "False", tekst)
            wyniki.append(eval(tekst, {"inf": INF, "None": None, "True": True, "False": False}))
        self.assertEqual(len(wyniki), 70)
        for (opis, _, oczekiwane), w in zip(PRZYPADKI, wyniki):
            self.assertTrue(zgodne(w, oczekiwane) and zgodne(oczekiwane, w), "%s: Luau %r, Python %r" % (opis, w, oczekiwane))

    def test_krok_grup_bez_zbieznosci_nie_rusza(self):
        # dane bez sensu (grupy nachodzą) — wynik nie może wyjść poza kopię wejścia ani cofnąć grup
        wynik = Lg.krok_grup([0, 1, 2], [0, 0, 0], [F, F, F], 100, 2.5, 25)
        for a, b in zip([0, 1, 2], wynik):
            self.assertLessEqual(Lg.przod(a, b, 100), 2.5 + 1e-9)


class TestDanych(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.D = generuj_dane.dane(generuj_dane.wczytaj())
        cls.strefy = {s["id"]: s for s in cls.D["strefy"]}

    def test_2_odstep_symulacja(self):
        D = self.D
        for ziarno in (3, 11):
            for st in D["strefy"]:
                if st["straznik"]:
                    continue
                v = D["gatunki"][st["gatunek"]]["predkosc"]
                sym = symuluj(st, D["zasady"], v, ziarno)
                with self.subTest(strefa=st["id"], ziarno=ziarno):
                    self.assertEqual(sym.bledy[:5], [])
                    czekajacy = [p["id"] for p in sym.potwory if p["stan"] != "chodzi"]
                    self.assertEqual(czekajacy, [], "po 120 s bez walk ktoś wciąż nie jest na pętli")
                    self.assertEqual(len(sym.potwory) + len(sym.kolejka), st["max"])
                    self.assertGreaterEqual(sym.min_luka, D["zasady"]["odstep"] - 1e-6)

    def test_2b_straznik_wchodzi_od_razu(self):
        st = self.strefy["straznik"]
        sym = Symulacja(st, self.D["zasady"], 0, 1, random.Random(1))
        p = sym.potwory[0]
        p["zajety"] = {"do": 1.0, "wynik": "wygrana"}
        sym.tyknij(1.0, 0.25)
        self.assertEqual(sym.potwory, [])
        sym.odradzaj(1.0)
        self.assertEqual(len(sym.kolejka), 1)
        self.assertAlmostEqual(sym.kolejka[0], 121.0)
        sym.odradzaj(121.0)
        self.assertEqual(len(sym.potwory), 1)
        sym.tyknij(121.25, 0.25)
        self.assertEqual(sym.potwory[0]["stan"], "chodzi")

    def test_3_pojemnosc(self):
        for st in self.D["strefy"]:
            if st["straznik"]:
                continue
            potrzeba = st["grupy"] * ((st["miejsc"] - 1) * st["odstepWGrupie"] + self.D["zasady"]["odstep"])
            with self.subTest(strefa=st["id"]):
                self.assertLessEqual(potrzeba, st["trasa"]["L"])
        self.assertAlmostEqual(self.strefy["z02"]["trasa"]["L"] - 7 * 25, 2.3, delta=0.05)
        self.assertAlmostEqual(self.strefy["z12"]["trasa"]["L"] - 5 * 25, 3.4, delta=0.05)

    def test_4_liczby(self):
        for G, oczekiwane in ((1, 35), (8, 64), (20, 86)):
            suma = sum(Lg.cel(s["naraz"], s["max"], G) for s in self.D["strefy"] if not s["straznik"])
            self.assertEqual(suma, oczekiwane, "G = %d" % G)
        self.assertEqual(sum(1 for s in self.D["strefy"] if not s["straznik"]), 16)
        self.assertEqual(self.D["strefy"][-1]["id"], "straznik")
        watahy = sorted(s["id"] for s in self.D["strefy"] if s["watahy"])
        self.assertEqual(watahy, ["z07", "z08", "z09", "z11", "z13", "z15"])
        self.assertEqual((self.strefy["z08"]["grupy"], self.strefy["z08"]["miejsc"]), (2, 5))

    def test_5_geometria(self):
        D = self.D
        for st in D["strefy"]:
            if st["straznik"]:
                continue
            tr = st["trasa"]
            cx, cz = st["srodek"][0], st["srodek"][2]
            granica = st["r"] + D["zasady"]["smycz"]
            probki = []
            n = 0
            s = 0.0
            while s < tr["L"]:
                x, _, z, _ = Lg.punkt_trasy(tr, s)
                probki.append((x, z))
                s += 2.0
                n += 1
            probki += list(zip(tr["x"], tr["z"]))
            for d in st["domy"]:
                wx, wz = d["wejscie"]
                dlug = math.hypot(wx - d["x"], wz - d["z"])
                k = max(1, int(dlug / 2))
                odcinek = [(d["x"] + (wx - d["x"]) * i / k, d["z"] + (wz - d["z"]) * i / k) for i in range(k + 1)]
                nx, nz = tr["x"][d["wezel"] - 1], tr["z"][d["wezel"] - 1]
                with self.subTest(strefa=st["id"], dom=(d["x"], d["z"])):
                    self.assertAlmostEqual(math.hypot(wx - nx, wz - nz), 6.0, delta=0.02)
                    odl = math.hypot(d["x"] - nx, d["z"] - nz)
                    self.assertTrue(35 <= odl <= 50, "dom %.1f od węzła" % odl)
                    for x, z in odcinek:
                        self.sprawdz_punkt(st, x, z, "odcinek dom → przedpole")
            with self.subTest(strefa=st["id"]):
                for x, z in probki:
                    self.assertLessEqual(math.hypot(x - cx, z - cz), granica + 1e-6, "punkt pętli poza smyczą")
                    self.sprawdz_punkt(st, x, z, "pętla")
        z09 = self.strefy["z09"]["trasa"]
        self.assertEqual(len(z09["x"]), 9)
        self.assertFalse(z09["zamknieta"])
        self.assertAlmostEqual(z09["L"], 475.1, delta=0.2)

    def sprawdz_punkt(self, st, x, z, co):
        for s in self.D["spokoj"]:
            self.assertGreaterEqual(math.hypot(x - s["x"], z - s["z"]), s["r"],
                                    "%s %s w strefie spokoju %s (%.1f; %.1f)" % (st["id"], co, s["id"], x, z))
        self.assertFalse(w_wielokacie(x, z, self.D["serce"]), "%s %s w Sercu Boru (%.1f; %.1f)" % (st["id"], co, x, z))

    def test_6_przeliczenie(self):
        z01 = self.strefy["z01"]["trasa"]
        self.assertEqual((z01["x"][0], z01["y"][0], z01["z"][0]), (-206.3, 0, -2294.5))
        s = self.strefy["straznik"]
        self.assertEqual(s["srodek"], [0, 32, -1627])
        self.assertEqual((s["trasa"]["x"][0], s["trasa"]["y"][0], s["trasa"]["z"][0]), (0, 32, -1627))
        self.assertEqual(s["trasa"]["L"], 0)
        self.assertEqual(s["poziomy"], [10, 10])
        potwory = generuj_dane._json(generuj_dane.PLIK_POTWOROW)
        for zr in potwory["strefy"]:
            self.assertTrue(all(y == zr["y"] for y in self.strefy[zr["id"]]["trasa"]["y"]), zr["id"])
        # przykład z rozdz. 2.3: z02, dom 1 → węzeł 2, przedpole (−10,61; −2327,91)
        d = self.strefy["z02"]["domy"][0]
        self.assertEqual(d["wezel"], 2)
        self.assertEqual(d["wejscie"], [-10.61, -2327.91])
        self.assertEqual(self.D["biom"]["plyta"]["pozycja"], [0, -1, -2000])
        self.assertEqual(self.D["biom"]["plyta"]["rozmiar"], [1400, 2, 1400])

    def test_7_generator(self):
        skrypt = os.path.join(PAKIET, "generuj_dane.py")
        with tempfile.TemporaryDirectory() as tmp:
            pliki = []
            for nr in (1, 2):
                cel = os.path.join(tmp, "dane%d.luau" % nr)
                wynik = subprocess.run([sys.executable, "-B", skrypt, "--wyjscie", cel], capture_output=True)
                self.assertEqual(wynik.returncode, 0, wynik.stdout.decode("utf-8", "replace"))
                with open(cel, "rb") as f:
                    pliki.append(f.read())
            self.assertEqual(pliki[0], pliki[1])
        wynik = subprocess.run([sys.executable, "-B", skrypt, "--sprawdz"], capture_output=True)
        self.assertEqual(wynik.returncode, 0, wynik.stdout.decode("utf-8", "replace"))
        tekst = pliki[0].decode("utf-8")
        self.assertFalse(pliki[0].startswith(b"\xef\xbb\xbf"), "BOM")
        self.assertNotIn("\r", tekst)
        self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\d\b|\d{1,2}\.\d{1,2}\.20\d\d", tekst), "data w pliku")
        self.assertIsNone(re.search(r"[A-Za-z]:\\|/Users/|/home/|\\Users\\", tekst), "ścieżka lokalna w pliku")
        self.assertIn('skrot = "%s"' % self.D["skrot"], tekst)
        self.assertTrue(tekst.split("]]", 1)[1].lstrip().startswith('if not game:GetService("RunService"):IsStudio() then'))


class TestBrzegi(unittest.TestCase):
    """Przypadki brzegowe dopisane przy recenzji (zadanie: 0 graczy, 1 gracz, strefa z jednym punktem, minimum 10 s)."""

    @classmethod
    def setUpClass(cls):
        cls.D = generuj_dane.dane(generuj_dane.wczytaj())
        cls.strefy = {s["id"]: s for s in cls.D["strefy"]}

    def sym(self, sid, cel=None):
        st = self.strefy[sid]
        v = self.D["gatunki"][st["gatunek"]]["predkosc"]
        if cel is None:
            cel = 1 if st["straznik"] else Lg.cel(st["naraz"], st["max"], 1)
        return Symulacja(st, self.D["zasady"], v, cel, random.Random(1))

    @staticmethod
    def biegnij(sym, od, do, gracze=(), G=None, dt=0.25):
        """Tyknięcia ruchu co dt i odradzanie w każdej pełnej sekundzie, od czasu `od` do `do` (jak pętle serwera)."""
        kroki = int(round((do - od) / dt))
        for i in range(1, kroki + 1):
            t = od + i * dt
            sym.tyknij(t, dt)
            if abs(t - round(t)) < 1e-9:
                sym.odradzaj(t, gracze, G)
        return od + kroki * dt

    @staticmethod
    def zabij(sym, p, teraz):
        """Walka wygrana przez gracza, która kończy się w chwili `teraz` (potwór znika w tyknięciu `teraz`)."""
        p["zajety"] = {"do": teraz, "wynik": "wygrana"}

    def test_8a_zero_i_jeden_gracz(self):
        zwykle = [s for s in self.D["strefy"] if not s["straznik"]]
        for G in (-3, 0, 1):
            self.assertEqual(sum(Lg.cel(s["naraz"], s["max"], G) for s in zwykle), 35, "G = %d" % G)
        self.assertEqual(sum(Lg.cel(s["naraz"], s["max"], 4) for s in zwykle), 45)
        self.assertEqual(sum(Lg.cel(s["naraz"], s["max"], 100) for s in zwykle), 86)
        for s in zwykle:
            with self.subTest(strefa=s["id"]):
                c0 = Lg.cel(s["naraz"], s["max"], 0)
                self.assertEqual(c0, Lg.cel(s["naraz"], s["max"], 1))
                self.assertEqual(c0, math.ceil(s["naraz"] / 2))
                self.assertGreaterEqual(c0, 1)
                # cel nigdy nie przekracza tego, co strefa mieści (grupy × miejsca)
                for G in range(0, 41):
                    self.assertLessEqual(Lg.cel(s["naraz"], s["max"], G), s["grupy"] * s["miejsc"])
        # 0 graczy w strefie (pusty serwer albo wszyscy w mieście): czas odrodzenia = baza, nie dłużej
        sym = self.sym("z01")
        self.zabij(sym, sym.potwory[0], 0.5)
        self.biegnij(sym, 0.0, 15.75, gracze=(), G=0)
        self.assertEqual(len(sym.potwory), 2, "przed upływem 15 s nikt nie powinien się odrodzić")
        self.biegnij(sym, 15.75, 16.0, gracze=(), G=0)
        self.assertEqual(len(sym.potwory), 3, "odrodzenie dokładnie po 15 s (wpis z t = 1 s → t = 16 s)")
        self.assertEqual(sym.potwory[-1]["id"], "z01-4")
        self.assertEqual(sym.potwory[-1]["dom"], 1, "karuzela zaczyna od domu 1")

    def test_8b_minimum_odrodzenia_10_s(self):
        for s in self.D["strefy"]:
            if s["straznik"]:
                continue
            for n in range(0, 41):
                self.assertGreaterEqual(Lg.czas_odrodzenia(s["odrodzenieS"], n), 10 - 1e-9, (s["id"], n))
        self.assertEqual(Lg.czas_odrodzenia(15, 5), 10)   # 15 / 1,6 = 9,375 → podłoga 10
        self.assertEqual(Lg.czas_odrodzenia(25, 40), 10)
        # 20 graczy w zasięgu strefy z01 (60 od środka, czyli daleko od domów w stawie): odrodzenie po 10 s, nie 2,4 s
        sym = self.sym("z01")
        cx, cz = sym.st["srodek"][0], sym.st["srodek"][2]
        gracze = [[cx + 60, cz]] * 20
        self.assertEqual(sym.gracze_w_strefie(gracze), 20)
        self.zabij(sym, sym.potwory[0], 0.5)
        self.biegnij(sym, 0.0, 10.75, gracze=gracze)
        self.assertEqual(len(sym.potwory), 2)
        self.biegnij(sym, 10.75, 11.0, gracze=gracze)
        self.assertEqual(len(sym.potwory), 3, "wpis z t = 1 s dojrzewa w t = 11 s (minimum 10 s)")

    def test_8c_straznik_strefa_z_jednym_punktem(self):
        st = self.strefy["straznik"]
        tr = st["trasa"]
        self.assertEqual((len(tr["x"]), tr["L"]), (1, 0))
        self.assertEqual(Lg.punkt_trasy(tr, Lg.w_grupie(123.4, 1, 0, 0)), (0, 32, -1627, 0))
        self.assertEqual(Lg.krok_grup([0], [0], [False], 0, 2.5, 25), [0])
        self.assertTrue(Lg.minal(0, 0, 0, 0))
        self.assertEqual(Lg.przod_do(0, [], [], 0), INF)
        sym = self.sym("straznik")
        self.assertEqual([p["stan"] for p in sym.potwory], ["chodzi"])
        # zwycięzca stoi 2 studa od Strażnika: Strażnik i tak wraca dokładnie po 120 s (bez blokady domu)
        gracz = [[0, -1625]]
        self.zabij(sym, sym.potwory[0], 1.0)
        self.biegnij(sym, 0.0, 1.0, gracze=gracz)
        self.assertEqual(sym.potwory, [])
        self.assertEqual(sym.kolejka, [121.0])
        self.biegnij(sym, 1.0, 120.75, gracze=gracz)
        self.assertEqual(sym.potwory, [])
        self.biegnij(sym, 120.75, 121.0, gracze=gracz)
        self.assertEqual(len(sym.potwory), 1, "Strażnik wraca po 120 s także przy graczu obok")
        self.biegnij(sym, 121.0, 121.25, gracze=gracz)
        self.assertEqual(sym.potwory[0]["stan"], "chodzi", "Strażnik wchodzi na swoje miejsce w jednym tyknięciu")
        self.assertEqual(sym.potwory[0]["id"], "straznik-2")

    def test_8d_wszystkie_domy_zablokowane(self):
        sym = self.sym("z02")
        domy = sym.st["domy"]
        przy_domach = [[d["x"] + 3, d["z"]] for d in domy]
        self.zabij(sym, sym.potwory[0], 0.5)
        self.biegnij(sym, 0.0, 40.0, gracze=przy_domach)
        self.assertEqual(len(sym.potwory), 2, "każdy dom ma gracza bliżej niż 18: nikt nie wychodzi")
        self.assertEqual(len(sym.kolejka), 1, "wpis czeka w kolejce (nie przepada)")
        # gracz spod domu 1 odchodzi: następna sekunda → nowy potwór w domu 1 (karuzela od ostatni = 0)
        reszta = przy_domach[1:]
        self.biegnij(sym, 40.0, 41.0, gracze=reszta)
        self.assertEqual(len(sym.potwory), 3)
        self.assertEqual(sym.potwory[-1]["dom"], 1)
        self.assertEqual(sym.kolejka, [])
        # gracz na granicy 18 nie blokuje (wolny, gdy odległość ≥ 18)
        d1 = domy[0]
        self.assertEqual(Lg.wolny_dom([[d1["x"], d1["z"]]], [[d1["x"] + 18, d1["z"]]], 0, 18), 1)

    def test_8e_nadmiar_po_odejsciu_graczy(self):
        # 20 graczy: strefa dochodzi do 9; potem zostaje 1 gracz — nikt nie znika sam
        sym = self.sym("z01")
        self.biegnij(sym, 0.0, 60.0, G=20)
        self.assertEqual(len(sym.potwory), 9)
        self.biegnij(sym, 60.0, 120.0, G=1)
        self.assertEqual(len(sym.potwory), 9, "nadmiaru nie usuwamy")
        self.assertEqual(sym.kolejka, [])
        # wpisy dodane przy 20 graczach, które dojrzały przy 1 graczu, przepadają
        sym = self.sym("z01")
        self.biegnij(sym, 0.0, 1.0, G=20)
        self.assertEqual(len(sym.kolejka), 6)
        self.biegnij(sym, 1.0, 30.0, G=1)
        self.assertEqual((len(sym.potwory), sym.kolejka), (3, []))

    def test_8f_generator_trzy_razy_i_plik_z_repozytorium(self):
        skrypt = os.path.join(PAKIET, "generuj_dane.py")
        with tempfile.TemporaryDirectory() as tmp:
            pliki = []
            for nr in (1, 2, 3):
                cel = os.path.join(tmp, "dane%d.luau" % nr)
                wynik = subprocess.run([sys.executable, "-B", skrypt, "--wyjscie", cel], capture_output=True)
                self.assertEqual(wynik.returncode, 0)
                with open(cel, "rb") as f:
                    pliki.append(f.read())
        with open(generuj_dane.CEL, "rb") as f:
            z_repo = f.read()
        self.assertEqual(len(set(pliki + [z_repo])), 1, "generator nie jest deterministyczny albo plik jest nieaktualny")

    def test_8g_kolejnosc_krokow_serwera(self):
        """Wykrywacz rozjazdu lustra: kolejność kroków tyknięcia i reguła Strażnika w Luau jak w klasie Symulacja."""
        with open(os.path.join(PAKIET, "zrodla", "SerwerPotworow.server.luau"), encoding="utf-8") as f:
            serwer = f.read()
        tyk = serwer.split("local function tyknijStrefe", 1)[1].split("\nend\n", 1)[0]
        kroki = ["zakonczZajetosc(", "Logika.krokGrup(", "ustawNaPetli(", "Logika.krokDo(", "sprobujWejsc(",
                 "zapiszAtrybuty("]
        miejsca = [tyk.find(k) for k in kroki]
        self.assertNotIn(-1, miejsca, dict(zip(kroki, miejsca)))
        self.assertEqual(miejsca, sorted(miejsca), "kolejność kroków tyknięcia w serwerze się zmieniła")
        odr = serwer.split("local function odradzaj", 1)[1].split("\nend\n", 1)[0]
        self.assertIn("if st.d.straznik then 0 else BLOKADA_DOMU", odr)
        self.assertIn("if #st.potwory >= st.cel then", odr)
        self.assertIn("Logika.czasOdrodzenia(st.d.odrodzenieS, graczeWStrefie(st, gracze))", odr)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
