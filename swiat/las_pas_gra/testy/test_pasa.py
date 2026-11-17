# -*- coding: utf-8 -*-
"""Testy offline pakietu swiat/las_pas_gra („las-pas w grze”). Bez Studio, bez sieci.

    python -B swiat/las_pas_gra/testy/test_pasa.py        (unittest; kod 1 przy błędzie)

1. Dane: generator deterministyczny i aktualny; ta sama treść z mapą (swiat/las_pas) i bez niej (sam plan);
   rozjazd planu i mapy wykrywany; liczby potworów 20 / 36 / 46 jak w sprawdz_plan.py.
2. Przydział potworów do przegród: gatunek i poziomy jak w planie, pętla i odcinki dom → przedpole w polu strefy,
   w kojcu i w pasie, poza strefami spokoju; symulacja ruchu (ta sama klasa Symulacja co testy starego lasu, wierna
   kopia SerwerPotworow) — odstęp ≥ 25, nikt nie wychodzi z pola strefy, troll wraca po stałych 150 s.
3. Brama: decyzja serwera (cofnij / wolno), otwarcie tylko po wygranej ze Strażnikiem, ratunek, położenie zapory,
   tabliczki i zabezpieczenia za bramą.
4. Przelot: automat LogikaPasa.krokPrzelotu — pierwsze wejście, brak drugiego, klient niegotowy, odmowa, reset
   (uchwyt „odtwórz ponownie”), utrata postaci, brak odpowiedzi klienta; „odblokuj” w każdej ścieżce wyjścia.
5. Krzywa kamery zgodna z swiat/biom_las/pas/sprawdz_plan.py (krzywa_kamery) i jego kontrolą; postój i ryk.
6. Mgła: prostokąt z planu, łagodne przejście, rozłączna z mgłą starego lasu.
7. Luau: wszystkie pliki parsuje interpreter tools/walka/luau_mini.py (gdy jest); LogikaPasa wykonana w nim daje te
   same wyniki co lustro w Pythonie (przypadki wzorcowe, losowe wywołania, scenariusze automatu); oba wygenerowane
   moduły danych wczytane w Luau są równe danym z generatora.
8. Punkty styku (czytane jak tekst): nazwy instancji, atrybuty, wiadomości zdalne, nadpisania Stale_*, haczyki
   KlientPotworow, strażnik Studio, brak ścieżek lokalnych; zbuduj.py --sucho; przejście przez chmury idzie przez
   uchwyt PrzeniesDoLasu z opóźnieniem przelotu (8k) i próby w Play zamykają ekran wyboru klasy (8l) — oba po
   błędach znalezionych w Studio 17.11.2026.
"""
import importlib.util
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.dont_write_bytecode = True
sys.path.insert(0, PAKIET)


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


import logika_pasa as LP  # noqa: E402
import zrodlo_mapy  # noqa: E402
import sprawdz_luau_pasa  # noqa: E402

GEN = _modul("generuj_dane_pasa_test", os.path.join(PAKIET, "generuj_dane.py"))
ZB = _modul("zbuduj_pasa_test", os.path.join(PAKIET, "zbuduj.py"))
TL = _modul("test_logiki_lasu", os.path.join(REPO, "swiat", "las_potwory", "testy", "test_logiki.py"))
Lg = TL.Lg
PLIK_SPRAWDZ_PLAN = os.path.join(REPO, "swiat", "biom_las", "pas", "sprawdz_plan.py")

M, DP, DPA = GEN.wszystko()
STREFY = {s["id"]: s for s in DP["strefy"]}
PLAN = M["plan"]
TOL = 1e-6


def sprawdz_plan():
    """Świeży moduł sprawdz_plan (ma globalne listy błędów)."""
    return _modul("sprawdz_plan_test_%d" % random.randint(0, 10 ** 9), PLIK_SPRAWDZ_PLAN)


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


ZR = os.path.join(PAKIET, "zrodla")
SERWER = czytaj(ZR, "SerwerPasa.server.luau")
KLIENT = czytaj(ZR, "KlientPasa.client.luau")
MGLA = czytaj(ZR, "MglaPasa.client.luau")
STALE = czytaj(REPO, "swiat", "las_potwory", "zrodla", "Stale.luau")
SERWER_POTWOROW = czytaj(REPO, "swiat", "las_potwory", "zrodla", "SerwerPotworow.server.luau")
KLIENT_POTWOROW = czytaj(REPO, "swiat", "las_potwory", "zrodla", "KlientPotworow.client.luau")


def bez_komentarzy(tekst):
    return sprawdz_luau_pasa.SL.rozbierz(tekst)[0]


def napisy(tekst, metoda):
    return set(re.findall(r'%s\(\s*"([^"]+)"' % metoda, bez_komentarzy(tekst)))


# ============================================================================================== interpreter Luau
LM = sprawdz_luau_pasa.luau_mini()


def luau_modul(plik):
    """Moduł Luau wykonany w luau_mini (game:GetService(...):IsStudio() → true)."""
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    wynik = it.wykonaj(czytaj(ZR, plik), plik)[0]
    return it, wynik


def wolaj(it, modul, nazwa, *argi):
    return it.wywolaj(modul.get(nazwa), [LM.do_luau(a) if isinstance(a, (dict, list)) else
                                           (float(a) if isinstance(a, (int, float)) and not isinstance(a, bool) else a)
                                           for a in argi])


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_generator_deterministyczny_i_aktualny(self):
        skrypt = os.path.join(PAKIET, "generuj_dane.py")
        pliki = []
        with tempfile.TemporaryDirectory() as tmp:
            for nr in (1, 2):
                folder = os.path.join(tmp, str(nr))
                r = subprocess.run([sys.executable, "-B", skrypt, "--wyjscie", folder], capture_output=True)
                self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
                zawartosc = {}
                for n in sorted(os.listdir(folder)):
                    with open(os.path.join(folder, n), "rb") as f:
                        zawartosc[n] = f.read()
                pliki.append(zawartosc)
        self.assertEqual(pliki[0], pliki[1])
        self.assertEqual(sorted(pliki[0]), ["DanePasa.luau", "DanePotworowPasa.luau"])
        r = subprocess.run([sys.executable, "-B", skrypt, "--sprawdz"], capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
        for nazwa, bajty in pliki[0].items():
            with self.subTest(plik=nazwa):
                tekst = bajty.decode("utf-8")
                self.assertFalse(bajty.startswith(b"\xef\xbb\xbf"), "BOM")
                self.assertNotIn("\r", tekst)
                self.assertIsNone(re.search(r"\b20\d\d-\d\d-\d\d\b", tekst), "data w pliku")
                self.assertIsNone(re.search(r"[A-Za-z]:\\|/Users/|/home/", tekst), "ścieżka lokalna")
                self.assertIn('skrot = "%s"' % DP["skrot"], tekst)
                self.assertTrue(tekst.split("]]", 1)[1].lstrip().startswith(sprawdz_luau_pasa.SL.STRAZNIK))

    def test_1b_mapa_i_sam_plan_daja_to_samo(self):
        """Cienka warstwa zrodlo_mapy: bez swiat/las_pas (sam plan) strefy i przelot są identyczne."""
        m2, dp2, dpa2 = GEN.wszystko(bez_mapy=True)
        self.assertEqual(m2["zrodlo"], "plan")
        self.assertEqual(dp2["biom"]["nazwa"], "LasPas")
        self.assertIs(dp2["biom"]["plyta"], False)
        self.assertEqual(dp2["strefy"], DP["strefy"])
        self.assertEqual(dpa2["przelot"], DPA["przelot"])
        self.assertEqual(dpa2["brama"], DPA["brama"])
        if M["zrodlo"] == "znaczniki":
            self.assertEqual(DP["biom"]["plyta"]["sciezka"], "Teren/Grunt/Płyta")
            self.assertEqual(DP["biom"]["obrotY"], 0)

    def test_1c_rozjazd_planu_i_mapy_to_blad(self):
        if M["znaczniki"] is None:
            self.skipTest("brak swiat/las_pas/znaczniki.json")
        zn = json.loads(json.dumps(M["znaczniki"]))
        zn["strefy"][0]["wezly"][0][0] += 3
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "znaczniki.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump(zn, f, ensure_ascii=False)
            with self.assertRaises(zrodlo_mapy.Blad) as k:
                zrodlo_mapy.wczytaj(plik_znacznikow=p)
            self.assertIn("s1", str(k.exception))

    def test_1d_liczby_jak_w_sprawdz_plan(self):
        sp = sprawdz_plan()
        _, sumy = sp.tabela_potworow(PLAN)
        nasze = [sum(1 if s["straznik"] else Lg.cel(s["naraz"], s["max"], G) for s in DP["strefy"]) for G in (1, 8, 20)]
        self.assertEqual(nasze, sumy)
        self.assertEqual(nasze, [20, 36, 46])
        self.assertEqual(len(DP["strefy"]), 11)
        self.assertEqual(DP["strefy"][-1]["id"], "straznik")


# ============================================================================================== 2. potwory w przegrodach
def probki_trasy(st, krok=1.0):
    tr = st["trasa"]
    s, wynik = 0.0, []
    while s < tr["L"]:
        x, _, z, _ = Lg.punkt_trasy(tr, s)
        wynik.append((x, z))
        s += krok
    return wynik + list(zip(tr["x"], tr["z"]))


def w_polu(st, x, z, zapas=1e-6):
    p = st["pole"]
    return p["x1"] - zapas <= x <= p["x2"] + zapas and p["z1"] - zapas <= z <= p["z2"] + zapas


class TestPrzegrod(unittest.TestCase):
    def test_2a_gatunek_poziomy_i_przegroda_jak_w_planie(self):
        sp = sprawdz_plan()
        for st_plan in PLAN["strefy"]:
            st = STREFY[st_plan["id"]]
            with self.subTest(strefa=st["id"]):
                self.assertEqual(st["podbiom"], st_plan["podbiom"])
                self.assertEqual(GEN.GATUNKI[sp.GATUNEK[st["podbiom"]]], st["gatunek"])
                self.assertEqual(st["poziomy"], st_plan["poziomy"])
                self.assertEqual((st["naraz"], st["max"], st["odrodzenieS"]), (st_plan["naraz"], st_plan["max"], st_plan["odrodzenie_s"]))
                self.assertEqual(st["odrodzenieStale"], st["id"] == "t1")
        s = STREFY["straznik"]
        self.assertEqual((s["gatunek"], s["poziomy"], s["odrodzenieS"], s["trasa"]["L"]), ("straznik_lasu", [10, 10], 120, 0))
        self.assertAlmostEqual(s["trasa"]["yaw"], math.pi / 2, delta=0.001)
        self.assertEqual(s["srodek"], [1974, 0, -700])
        self.assertTrue(s["straznik"] and s["odrodzenieStale"])

    def test_2b_trasy_i_domy_w_polu_kojcu_i_pasie(self):
        przeg = {q["id"]: q for q in PLAN["przegrody"]}
        pod = {p["id"]: p for q in PLAN["przegrody"] for p in q.get("pod", [])}
        X0, Z0 = M["X0"], M["Z0"]
        pol = PLAN["pas"]["szerokosc"] / 2
        for st in DP["strefy"]:
            if st["straznik"]:
                continue
            odc = pod.get(st["pod"]) or przeg[st["podbiom"]]
            punkty = probki_trasy(st)
            for d in st["domy"]:
                wx, wz = d["wejscie"]
                k = max(1, int(math.hypot(wx - d["x"], wz - d["z"])))
                punkty += [(d["x"] + (wx - d["x"]) * i / k, d["z"] + (wz - d["z"]) * i / k) for i in range(k + 1)]
                nx, nz = st["trasa"]["x"][d["wezel"] - 1], st["trasa"]["z"][d["wezel"] - 1]
                odl = math.hypot(d["x"] - nx, d["z"] - nz)
                with self.subTest(strefa=st["id"], dom=(d["x"], d["z"])):
                    self.assertTrue(12 - 1e-6 <= odl <= 20 + 1e-6, "dom %.1f od węzła" % odl)
                    self.assertAlmostEqual(math.hypot(wx - nx, wz - nz), 6.0, delta=0.02)
            with self.subTest(strefa=st["id"]):
                for x, z in punkty:
                    self.assertTrue(w_polu(st, x, z), "(%.1f; %.1f) poza polem strefy" % (x, z))
                    self.assertTrue(X0 + odc["u_od"] <= x <= X0 + odc["u_do"], "(%.1f) poza kojcem/przegrodą" % x)
                    self.assertLessEqual(abs(z - Z0), pol, "poza pasem")
                    for sp in DP["spokojProstokaty"]:
                        self.assertFalse(LP.w_prostokacie(x, z, sp), "w strefie spokoju %s" % sp["id"])

    def test_2c_symulacja_odstep_i_pole(self):
        """Ta sama Symulacja co testy starego lasu (lustro tyknięcia SerwerPotworow): 15 min, losowe walki."""
        zasady = DP["zasady"]
        for ziarno in (5, 17):
            for st in DP["strefy"]:
                if st["straznik"]:
                    continue
                v = DP["gatunki"][st["gatunek"]]["predkosc"]
                rnd = random.Random(ziarno)
                sym = TL.Symulacja(st, zasady, v, st["max"], rnd)
                dt, poza = 0.25, []
                kroki = int(15 * 60 / dt)
                nastepna = 1.0
                for i in range(1, kroki + 1):
                    teraz = i * dt
                    if teraz < 15 * 60 - 120 and rnd.random() < dt / 20:
                        wolne = [p for p in sym.potwory if p["zajety"] is None]
                        if wolne:
                            p = rnd.choice(wolne)
                            p["zajety"] = {"do": teraz + rnd.uniform(8, 40), "wynik": "wygrana" if rnd.random() < 0.6 else "przegrana"}
                    sym.tyknij(teraz, dt)
                    if teraz + 1e-9 >= nastepna:
                        sym.odradzaj(teraz)
                        nastepna += 1.0
                    for p in sym.potwory:
                        if p["grupa"] is not None:
                            s = Lg.w_grupie(p["grupa"]["s"], p["miejsce"], st["odstepWGrupie"], sym.L)
                            x, _, z, _ = Lg.punkt_trasy(st["trasa"], s)
                        else:
                            x, z = p["x"], p["z"]
                        if not w_polu(st, x, z, 0.01):
                            poza.append((teraz, p["id"], x, z))
                with self.subTest(strefa=st["id"], ziarno=ziarno):
                    self.assertEqual(sym.bledy[:3], [])
                    self.assertEqual(poza[:3], [])
                    self.assertGreaterEqual(sym.min_luka, zasady["odstep"] - 1e-6)
                    self.assertEqual([p["id"] for p in sym.potwory if p["stan"] != "chodzi"], [],
                                     "po 120 s bez walk ktoś nie jest na pętli")
                    self.assertEqual(len(sym.potwory) + len(sym.kolejka), st["max"])

    def test_2d_troll_stale_150_s_slime_skrocony(self):
        def odrodzenie(sid, gracze):
            st = STREFY[sid]
            sym = TL.Symulacja(st, DP["zasady"], 0, 1, random.Random(1))
            p = sym.potwory[0]
            p["zajety"] = {"do": 1.0, "wynik": "wygrana"}
            sym.tyknij(1.0, 0.25)
            sym.odradzaj(1.0, gracze=gracze)
            return sym.kolejka[0] - 1.0
        tlum = [[1850, -700]] * 5   # 5 graczy w leżu (daleko od domu trolla pod ścianą: 34+ st)
        self.assertAlmostEqual(odrodzenie("t1", tlum), 150.0, delta=1e-9)
        kojec = [[1208, -700]] * 5
        self.assertAlmostEqual(odrodzenie("s1", kojec), max(10, 12 / (1 + 0.15 * 4)), delta=1e-9)

    def test_2e_zasieg_graczy_nie_siega_dalszych_kojcow(self):
        for a in ("s1", "m1", "w1"):
            st = STREFY[a]
            dalszy = STREFY[{"s1": "s3", "m1": "m3", "w1": "w3"}[a]]
            self.assertLess(st["zasiegGraczy"], abs(dalszy["srodek"][0] - st["srodek"][0]) - 32)


# ============================================================================================== 3. brama
B = DPA["brama"]


class TestBramy(unittest.TestCase):
    def test_3a_decyzja_serwera(self):
        z0 = M["Z0"]
        for x, z, upr, wynik in ((B["x"] - 5, z0, False, "wolno"), (B["x"] + 1, z0, False, "wolno"),
                                 (B["x"] + 2, z0, False, "cofnij"), (B["x"] + 20, z0 + 30, False, "cofnij"),
                                 (B["x"] + 20, z0, True, "wolno"), (B["x"] + 20, z0 + 300, False, "wolno"),
                                 (B["x"] + 250, z0, False, "wolno")):
            with self.subTest(x=x, z=z, uprawniony=upr):
                self.assertEqual(LP.decyzja_bramy(x, z, upr, B), wynik)

    def test_3b_tylko_wygrana_ze_straznikiem_otwiera(self):
        przypadki = [({"straznik": True, "wynik": "wygrana", "id": "straznik-1"}, True),
                     ({"straznik": True, "wynik": "przegrana"}, False), ({"straznik": False, "wynik": "wygrana"}, False),
                     ({"straznik": "true", "wynik": "wygrana"}, False), ({}, False), (None, False), ("wygrana", False)]
        for info, wynik in przypadki:
            self.assertEqual(LP.otwiera_brame(info), wynik, info)
        # sekwencja walk jednego gracza: dopiero wygrana ze Strażnikiem ustawia flagę (jak SerwerPasa)
        pokonal = False
        for info in ({"straznik": False, "wynik": "wygrana"}, {"straznik": True, "wynik": "przegrana"},
                     {"straznik": True, "wynik": "wygrana"}, {"straznik": True, "wynik": "przegrana"}):
            pokonal = pokonal or LP.otwiera_brame(info)
        self.assertTrue(pokonal)
        self.assertEqual(LP.decyzja_bramy(B["x"] + 10, M["Z0"], pokonal, B), "wolno")

    def test_3c_ratunek(self):
        R = DPA["ratunek"]
        self.assertTrue(LP.potrzeba_ratunku(1500, -40, -700, R))
        self.assertFalse(LP.potrzeba_ratunku(1500, 3, -700, R))
        self.assertFalse(LP.potrzeba_ratunku(0, -40, -700, R), "miasteczko i Baseplate nie są nasze")
        self.assertEqual(LP.cel_ratunku(B["x"] + 10, M["Z0"], False, B), "przed_brama")
        self.assertEqual(LP.cel_ratunku(B["x"] + 10, M["Z0"], True, B), "za_brama")
        self.assertEqual(LP.cel_ratunku(1500, M["Z0"], True, B), "przybycie")
        # pudło ratunku nie obejmuje starego lasu ani miasteczka (plan: zajete)
        for nazwa, (a1, a2, b1, b2) in [("miasteczko", PLAN["swiat"]["miasteczko"]["zajete"])] + [
                (o["id"], o["xz"]) for o in PLAN["swiat"]["zajete_inne"] if o["id"] != "baseplate"]:
            self.assertFalse(R["x1"] < a2 and a1 < R["x2"] and R["z1"] < b2 and b1 < R["z2"], nazwa)

    def test_3d_polozenie_zapory_tabliczki_i_punktow(self):
        X0, Z0 = M["X0"], M["Z0"]
        sciana = M["pas"]["sciana_v"]
        z = DPA["zapora"]
        self.assertEqual(z["srodek"][0], B["x"])
        self.assertGreaterEqual(z["rozmiar"][2] / 2, sciana, "zapora przez całą szerokość pasa (do niewidzialnych ścian)")
        self.assertGreaterEqual(z["rozmiar"][1], 30, "zapory nie da się przeskoczyć")
        self.assertLess(DPA["przedBrama"]["punkt"][0], B["x"] - 5)
        self.assertEqual(LP.decyzja_bramy(DPA["przedBrama"]["punkt"][0], Z0, False, B), "wolno")
        zb = DPA["zaBrama"]["punkt"][0]
        sc = DPA["zabezpieczenie"]["sciana"]["srodek"][0]
        tab = DPA["tabliczka"]["punkt"][0]
        self.assertTrue(B["x"] + B["tolerancja"] < zb < tab < X0 + 965 < sc, "brama < za bramą < tabliczka < ściana mapy < nasza ściana")
        pod = DPA["zabezpieczenie"]["podloga"]
        self.assertLess(pod["srodek"][1] + pod["rozmiar"][1] / 2, 0, "zapasowa podłoga pod Płytą (wierzch < 0)")
        self.assertLessEqual(pod["srodek"][0] - pod["rozmiar"][0] / 2, B["x"])
        self.assertGreaterEqual(pod["srodek"][0] + pod["rozmiar"][0] / 2, sc - 1)
        # brama zgadza się z planem i mapą
        br = next(m for m in PLAN["miejsca"] if m["id"] == "brama_bagna")
        self.assertEqual(B["x"], X0 + br["u"])
        self.assertEqual(B["otwarcie"], [Z0 + br["otwarcie"][0], Z0 + br["otwarcie"][1]])
        if M["znaczniki"]:
            self.assertEqual(DPA["mapa"]["grupaWrot"], M["znaczniki"]["brama_bagna"]["grupa_wrot"].split("/", 2)[-1])
            kp = next(p for p in M["znaczniki"]["punkty_e"] if p["grupa"] == "Punkty/KamienPowrotu")
            self.assertEqual(DPA["powrot"]["punkt"], kp["punkt_swiat"])
        pr = DPA["przybycie"]
        self.assertTrue(LP.w_prostokacie(pr["punkt"][0], pr["punkt"][2], DPA["wejscie"]))
        self.assertTrue(LP.w_prostokacie(pr["punkt"][0], pr["punkt"][2], DP["spokojProstokaty"][0]), "przybycie w strefie spokoju")


# ============================================================================================== 4. przelot (automat)
K = DPA["przelot"]


def wejscie(**kw):
    w = {"widzial": False, "wPasie": True, "gotowy": True, "postac": True, "strumienie": 0, "koniec": False, "przerwij": None}
    w.update(kw)
    return w


class Gracz:
    """Lustro pętli SerwerPasa dla jednego gracza: flaga w pamięci, automat, wykonanie akcji (bez instancji)."""

    def __init__(self, krok=None):
        self.krok = krok or LP.krok_przelotu
        self.s = LP.nowy_stan_przelotu()
        self.widzial = False
        self.zablokowany = False
        self.log = []

    def tyk(self, teraz, **kw):
        w = wejscie(widzial=self.widzial, **kw)
        akcje = self.krok(self.s, w, teraz, K)
        for a in akcje:
            if a == "widzial":
                self.widzial = True
            elif a == "zapomnij":
                self.widzial = False
            elif a == "zablokuj":
                assert not self.zablokowany, "podwójne zablokowanie"
                self.zablokowany = True
            elif a == "odblokuj":
                self.zablokowany = False
        self.log.append((round(teraz, 2), tuple(akcje)))
        return akcje


def przebieg(g, od, do, dt=0.25, **kw):
    wynik = []
    t = od
    while t <= do + 1e-9:
        a = g.tyk(t, **kw)
        if a:
            wynik.append((round(t, 2), a))
        t += dt
    return wynik


class TestPrzelotu(unittest.TestCase):
    def test_4a_pierwsze_wejscie_i_brak_drugiego(self):
        g = Gracz()
        self.assertEqual(g.tyk(0.0), ["widzial"])
        self.assertEqual(g.tyk(0.25), [])
        self.assertEqual(g.tyk(0.5), ["zablokuj", "przygotuj", "laduj"])
        self.assertEqual(g.tyk(0.75, strumienie=2), [])
        self.assertEqual(g.tyk(1.0, strumienie=0), ["start"])
        self.assertTrue(g.zablokowany)
        podtrzymania = [t for t, a in przebieg(g, 1.25, 10.0) if a == ["podtrzymaj"]]
        self.assertEqual(podtrzymania[:3], [2.0, 3.0, 4.0])
        self.assertEqual(g.tyk(14.5, koniec=True), ["odblokuj"])
        self.assertFalse(g.zablokowany)
        self.assertTrue(g.widzial)
        # wyjście z lasu i ponowne wejście: drugi raz przelot się nie odpala
        self.assertEqual(przebieg(g, 15, 20, wPasie=False), [])
        self.assertEqual(przebieg(g, 20, 60), [])

    def test_4b_klient_niegotowy_czeka(self):
        g = Gracz()
        self.assertEqual(przebieg(g, 0, 10, gotowy=False), [])
        self.assertEqual(g.tyk(10.25), ["widzial"])

    def test_4c_brak_odpowiedzi_klienta_konczy_serwer(self):
        g = Gracz()
        g.tyk(0)
        g.tyk(0.5)
        g.tyk(4.5, strumienie=4)            # mapa się nie wczytała w 4 s → i tak start
        self.assertEqual(g.s["faza"], "trwa")
        termin = g.s["doKiedy"]
        self.assertAlmostEqual(termin, 4.5 + K["czas"] + K["zapas"])
        akcje = [a for t, a in przebieg(g, 4.75, termin + 1) if a != ["podtrzymaj"]]
        self.assertEqual(akcje, [["przerwij", "odblokuj"]])
        self.assertFalse(g.zablokowany)
        self.assertTrue(g.widzial, "po milczeniu klienta nie zapętlamy przelotu")
        self.assertEqual(przebieg(g, termin + 2, termin + 30), [])

    def test_4d_odmowa_klienta_ponawia_po_5_s(self):
        g = Gracz()
        g.tyk(0)
        g.tyk(0.5)
        self.assertEqual(g.tyk(0.75, przerwij="odmowa"), ["przerwij", "odblokuj", "zapomnij"])
        self.assertFalse(g.widzial)
        self.assertEqual(przebieg(g, 1.0, 5.5), [])
        self.assertEqual(g.tyk(5.75), ["widzial"])

    def test_4e_odtworz_ponownie_reset(self):
        g = Gracz()
        g.tyk(0)
        g.tyk(0.5)
        g.tyk(1.0)
        self.assertEqual(g.tyk(3.0, przerwij="reset"), ["przerwij", "odblokuj", "zapomnij"])
        self.assertEqual(g.tyk(3.25), ["widzial"], "uchwyt „odtwórz ponownie” odpala przelot od razu")
        self.assertEqual(g.s["id"], 2)

    def test_4f_utrata_postaci(self):
        for faza_t, oczek in ((0.25, ["odblokuj"]), (0.75, ["przerwij", "odblokuj"]), (2.0, ["przerwij", "odblokuj"])):
            g = Gracz()
            g.tyk(0)
            if faza_t > 0.5:
                g.tyk(0.5, strumienie=1)
            if faza_t > 1.0:
                g.tyk(1.0)
            with self.subTest(t=faza_t, faza=g.s["faza"]):
                self.assertEqual(g.tyk(faza_t, postac=False, strumienie=1), oczek)
                self.assertFalse(g.zablokowany)
                self.assertTrue(g.widzial)

    def test_4g_przelot_po(self):
        g = Gracz()
        g.s["wolnyOd"] = 3.0               # PrzeniesDoLasu(gracz, { przelotPo = 3 })
        self.assertEqual(przebieg(g, 0, 2.75), [])
        self.assertEqual(g.tyk(3.0), ["widzial"])

    def test_4h_losowo_zawsze_odblokowuje(self):
        rnd = random.Random(7)
        for _ in range(300):
            g = Gracz()
            t = 0.0
            for _ in range(rnd.randint(10, 120)):
                kw = {"wPasie": rnd.random() < 0.8, "gotowy": rnd.random() < 0.9, "postac": rnd.random() < 0.95,
                      "strumienie": rnd.choice([0, 0, 1, 3]), "koniec": rnd.random() < 0.1,
                      "przerwij": rnd.choice([None] * 12 + ["odmowa", "reset", "klient"])}
                g.tyk(t, **kw)
                t += rnd.choice([0.1, 0.25, 0.5, 2.0])
                if g.s["faza"] == "brak":
                    self.assertFalse(g.zablokowany, g.log[-5:])
            # bez nowych zdarzeń automat zawsze dochodzi do końca i odblokowuje
            przebieg(g, t, t + K["czas"] + K["zapas"] + K["ladowanie"] + 2, wPasie=False)
            self.assertEqual(g.s["faza"], "brak")
            self.assertFalse(g.zablokowany)


# ============================================================================================== 5. krzywa kamery
class TestKrzywej(unittest.TestCase):
    def test_5a_zgodna_z_sprawdz_plan(self):
        sp = sprawdz_plan()
        X0, Z0 = M["X0"], M["Z0"]
        probki = sp.krzywa_kamery(PLAN["przelot_kamery"]["punkty"], 0.05)
        self.assertGreater(len(probki), 250)
        for t, u, v, y in probki:
            x2, y2, z2 = LP.punkt_krzywej(K["punkty"], t)
            self.assertAlmostEqual(x2, X0 + u, delta=1e-6)
            self.assertAlmostEqual(y2, y, delta=1e-6)
            self.assertAlmostEqual(z2, Z0 + v, delta=1e-6)

    def test_5b_kontrola_planu_przelotu(self):
        sp = sprawdz_plan()
        T, vmax = sp.sprawdz_kamere(PLAN, PLAN["pas"]["szerokosc"] / 2)
        self.assertEqual([b for b in sp.bledy if "przelot" in b], [])
        self.assertAlmostEqual(T, K["czas"])
        self.assertLessEqual(vmax, sp.MAKS_PREDKOSC_KAMERY)
        # gęstsze próbkowanie naszej funkcji: ta sama prędkość najwyższa (± 2 st/s)
        najw, poprz = 0, None
        for i in range(0, int(K["czas"] * 200) + 1):
            p = LP.punkt_krzywej(K["punkty"], i / 200)
            if poprz:
                najw = max(najw, math.dist(p, poprz) * 200)
            poprz = p
        self.assertLessEqual(najw, sp.MAKS_PREDKOSC_KAMERY)
        self.assertAlmostEqual(najw, vmax, delta=2)

    def test_5c_postoj_na_strazniku_i_ryk(self):
        st = DPA["straznik"]["poz"]
        wys = PLAN["rozmiary"]["Strażnik Gaju"]["wys"]
        stop = LP.punkt_krzywej(K["punkty"], K["zatrzymanieOd"])
        for i in range(30):
            t = K["zatrzymanieOd"] + (K["czas"] - K["zatrzymanieOd"]) * i / 29
            self.assertEqual(LP.punkt_krzywej(K["punkty"], t), stop)
            c = LP.cel_krzywej(K["punkty"], t)
            self.assertLessEqual(math.hypot(c[0] - st[0], c[2] - st[2]), 3)
            self.assertTrue(0.5 * wys <= c[1] <= wys)
        self.assertTrue(K["zatrzymanieOd"] <= K["rykOd"] and K["rykOd"] + K["rykDl"] <= K["czas"] + 1e-9)
        self.assertEqual(K["klip"], "ryk")
        dane_straznika = json.loads(czytaj(REPO, "swiat", "test_walki2", "dane", "straznik_lasu.json"))
        ryk = next(k for k in dane_straznika["klipy"] if k["n"] == "ryk")
        self.assertAlmostEqual(ryk["dl"] / ryk["fps"], K["rykDl"], delta=0.05)

    def test_5d_cala_w_lesie_i_strumien_przed_kamera(self):
        for i in range(0, int(K["czas"] * 20) + 1):
            x, y, z = LP.punkt_krzywej(K["punkty"], i / 20)
            self.assertTrue(LP.w_prostokacie(x, z, DPA["wejscie"]), (i / 20, x, z))
            self.assertTrue(8 <= y <= 32, (i / 20, y))
        for p in K["strumien"]:
            self.assertTrue(LP.w_prostokacie(p[0], p[2], DPA["wejscie"]))
        x, _, _ = LP.punkt_wyprzedzenia(K["punkty"], 3.0, K["wyprzedzenie"])
        self.assertGreater(x, LP.punkt_krzywej(K["punkty"], 3.0)[0] + 100, "prośba o mapę wyprzedza kamerę")
        self.assertEqual(LP.punkt_wyprzedzenia(K["punkty"], 13.0, 5), LP.punkt_krzywej(K["punkty"], K["czas"]))


# ============================================================================================== 6. mgła
class TestMgly(unittest.TestCase):
    def test_6a_prostokat_z_planu_i_przejscie(self):
        mg = DPA["mgla"]
        X0, Z0 = M["X0"], M["Z0"]
        self.assertEqual((mg["x1"], mg["x2"], mg["z1"], mg["z2"]), (X0 + PLAN["pas"]["u_od"], X0 + PLAN["pas"]["u_do"], Z0 - 60, Z0 + 60))
        self.assertEqual(LP.waga_mgly(1500, -700, mg, mg["pas"]), 1.0)
        self.assertEqual(LP.waga_mgly(1500, -700 + 60 + mg["pas"] / 2, mg, mg["pas"]), 0.5)
        self.assertEqual(LP.waga_mgly(0, -700, mg, mg["pas"]), 0.0, "miasteczko bez mgły pasa")
        # łagodnie: od 0 do 1 w ok. 1,25 s, bez skoków większych niż tempo · dt
        w, t = 0.0, 0.0
        while w < 1:
            w2 = LP.krok_wagi(w, 1, mg["tempo"], 1 / 60)
            self.assertLessEqual(w2 - w, mg["tempo"] / 60 + 1e-12)
            w, t = w2, t + 1 / 60
        self.assertAlmostEqual(t, 1 / mg["tempo"], delta=0.05)
        self.assertLess(mg["wPrzelocie"], 1)

    def test_6b_rozlaczna_z_mgla_starego_lasu(self):
        stara = czytaj(REPO, "swiat", "biom_las", "zrodla", "MglaLasu.client.luau")
        sx = float(re.search(r"local SRODEK_X, SRODEK_Z = (-?[\d.]+), (-?[\d.]+)", stara).group(1))
        sz = float(re.search(r"local SRODEK_X, SRODEK_Z = (-?[\d.]+), (-?[\d.]+)", stara).group(2))
        pol = float(re.search(r"local POL = ([\d.]+)", stara).group(1))
        pas = float(re.search(r"local PAS = ([\d.]+)", stara).group(1))
        mg = DPA["mgla"]
        stary = {"x1": sx - pol - pas, "x2": sx + pol + pas, "z1": sz - pol - pas, "z2": sz + pol + pas}
        nasz = {"x1": mg["x1"] - mg["pas"], "x2": mg["x2"] + mg["pas"], "z1": mg["z1"] - mg["pas"], "z2": mg["z2"] + mg["pas"]}
        self.assertFalse(stary["x1"] < nasz["x2"] and nasz["x1"] < stary["x2"] and stary["z1"] < nasz["z2"] and nasz["z1"] < stary["z2"])

    def test_6c_mgla_nie_zmienia_wspolnego_lighting(self):
        kod = bez_komentarzy(MGLA)
        self.assertIn('FindFirstChildOfClass("Atmosphere")', kod)
        self.assertNotIn("Instance.new", kod)
        self.assertIsNone(re.search(r"\bSwiatlo\s*\.\s*\w+\s*=", kod))
        for plik in (SERWER, KLIENT):
            self.assertNotIn("Lighting", bez_komentarzy(plik))


# ============================================================================================== 7. Luau w luau_mini
@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py (interpreter nie jest w git) — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.L = luau_modul("LogikaPasa.luau")

    def py(self, v):
        return LM.z_luau(v)

    def test_7a_wszystkie_pliki_parsuja_sie(self):
        pliki = sorted(os.path.join(ZR, n) for n in os.listdir(ZR) if n.endswith(".luau"))
        bledy, parser = sprawdz_luau_pasa.sprawdz_pliki(pliki, wypisz=lambda *_: None)
        self.assertTrue(parser)
        self.assertEqual(bledy, [])
        self.assertEqual(len(pliki), 7)

    def test_7b_przypadki_wzorcowe_te_same(self):
        ok, n, bledy = wolaj(self.it, self.L, "sprawdzPrzypadki")
        self.assertIn(self.py(bledy), ({}, []), "Luau zgłasza błędy przypadków")
        self.assertTrue(ok)
        self.assertEqual(int(n), len(LP.PRZYPADKI))
        opisy = self.py(wolaj(self.it, self.L, "opisyPrzypadkow")[0])
        self.assertEqual(opisy, [o for o, _, _ in LP.PRZYPADKI])

    def test_7c_losowe_wywolania_takie_same(self):
        rnd = random.Random(3)
        R = DPA["mgla"]
        for _ in range(250):
            x, z, y = rnd.uniform(900, 2200), rnd.uniform(-900, -500), rnd.uniform(-60, 40)
            up = rnd.random() < 0.5
            for nazwa, argi, py in (
                    ("wProstokacie", (x, z, R), LP.w_prostokacie(x, z, R)),
                    ("odlegloscOdProstokata", (x, z, R), LP.odleglosc_od_prostokata(x, z, R)),
                    ("wagaMgly", (x, z, R, 120), LP.waga_mgly(x, z, R, 120)),
                    ("krokWagi", (y / 40, up * 1.0, 0.8, 0.016), LP.krok_wagi(y / 40, up * 1.0, 0.8, 0.016)),
                    ("zaBrama", (x, z, B), LP.za_brama(x, z, B)),
                    ("decyzjaBramy", (x, z, up, B), LP.decyzja_bramy(x, z, up, B)),
                    ("potrzebaRatunku", (x, y, z, DPA["ratunek"]), LP.potrzeba_ratunku(x, y, z, DPA["ratunek"])),
                    ("celRatunku", (x, z, up, B), LP.cel_ratunku(x, z, up, B))):
                lu = wolaj(self.it, self.L, nazwa, *argi)[0]
                if isinstance(py, float):
                    self.assertAlmostEqual(lu, py, delta=1e-9, msg=nazwa)
                else:
                    self.assertEqual(lu, py, nazwa)
            t = rnd.uniform(-1, 15)
            for nazwa, py in (("punktKrzywej", LP.punkt_krzywej(K["punkty"], t)), ("celKrzywej", LP.cel_krzywej(K["punkty"], t))):
                lu = wolaj(self.it, self.L, nazwa, K["punkty"], t)
                for a, b in zip(lu, py):
                    self.assertAlmostEqual(a, b, delta=1e-9, msg="%s(%.3f)" % (nazwa, t))

    def test_7d_automat_przelotu_taki_sam(self):
        def krok_luau(s, w, teraz, k):
            ts, tw = LM.do_luau(s), LM.Tabela()
            for kk, vv in w.items():
                if vv is not None:
                    tw.set(kk, float(vv) if isinstance(vv, (int, float)) and not isinstance(vv, bool) else vv)
            akcje = self.py(wolaj(self.it, self.L, "krokPrzelotu", ts, tw, teraz, k)[0])
            for kk, vv in self.py(ts).items():
                s[kk] = vv
            return [] if akcje == {} else akcje
        rnd = random.Random(11)
        for _ in range(60):
            gp, gl = Gracz(), Gracz(krok=krok_luau)
            t = 0.0
            for _ in range(rnd.randint(5, 60)):
                kw = {"wPasie": rnd.random() < 0.85, "gotowy": rnd.random() < 0.9, "postac": rnd.random() < 0.95,
                      "strumienie": rnd.choice([0, 0, 2]), "koniec": rnd.random() < 0.1,
                      "przerwij": rnd.choice([None] * 10 + ["odmowa", "reset", "klient"])}
                self.assertEqual(gl.tyk(t, **kw), gp.tyk(t, **kw))
                t += rnd.choice([0.25, 0.5, 3.0])
            self.assertEqual(gl.s["faza"], gp.s["faza"])
            for kk in ("id", "wolnyOd", "doKiedy"):
                self.assertAlmostEqual(float(gl.s[kk]), float(gp.s[kk]), delta=1e-9, msg=kk)
            self.assertEqual((gl.widzial, gl.zablokowany), (gp.widzial, gp.zablokowany))

    def test_7e_moduly_danych_rowne_generatorowi(self):
        def norm(v):
            if isinstance(v, dict):
                return {k: norm(x) for k, x in v.items()}
            if isinstance(v, list):
                return [norm(x) for x in v]
            if isinstance(v, bool) or v is None or isinstance(v, str):
                return v
            return round(float(v), 6)
        for plik, dane in (("DanePasa.luau", DPA), ("DanePotworowPasa.luau", DP)):
            _, modul = luau_modul(plik)
            lu = norm(LM.z_luau(modul, pusta_jako_lista=True))
            with self.subTest(plik=plik):
                self.assertEqual(lu, norm(dane))


# ============================================================================================== 8. punkty styku
class TestStyku(unittest.TestCase):
    def test_8a_nazwy_instancji_istnieja(self):
        plan = {"Brama", "ZaBrama", "Zapora", "Napis", "Podloga", "Sciana", "Tabliczka", "KamienPowrotu", "Stan"}
        for sciezka in ZB.FOLDERY:
            plan.update(sciezka.split("/"))
        for _, sciezka in ZB.INNE:
            plan.update(sciezka.split("/"))
        for _, _, sciezka, _ in ZB.SKRYPTY:
            plan.update(sciezka.split("/"))
        inne = {"PlayerGui", "PlayerScripts", "PlayerModule", "HumanoidRootPart", "Moduly", "OdtwarzaczWalki2",
                "SterowanieKlienta", "Baner"}   # Baner: element własnego ekranu KlientPasa
        for nazwa, tekst in (("SerwerPasa", SERWER), ("KlientPasa", KLIENT), ("MglaPasa", MGLA)):
            uzyte = napisy(tekst, r":WaitForChild") | napisy(tekst, r":FindFirstChild")
            with self.subTest(plik=nazwa):
                self.assertEqual(sorted(uzyte - plan - inne), [])
        # części, które buduje zbuduj.py, mają te nazwy
        kod = ZB.czesci_kod(DPA)
        for n in ("Brama", "Zapora", "Napis", "ZaBrama", "Podloga", "Sciana", "Tabliczka", "KamienPowrotu", "PodpowiedzPowrotu"):
            self.assertIn('"%s"' % n, kod, n)
        self.assertNotIn("__", kod.replace("__KONTENER__", ""), "nie wszystkie liczby wstawione")

    def test_8b_atrybuty_klienta_ktos_ustawia(self):
        serwer = napisy(SERWER, "SetAttribute")
        klient_sam = napisy(KLIENT, "SetAttribute") | napisy(MGLA, "SetAttribute")
        potwory = napisy(SERWER_POTWOROW, "SetAttribute") | {"KlientGotowy"}
        testowe = set(ZB.ATRYBUTY_TESTOWE)
        for nazwa, tekst in (("KlientPasa", KLIENT), ("MglaPasa", MGLA)):
            brak = napisy(tekst, "GetAttribute") - serwer - klient_sam - potwory - testowe
            with self.subTest(plik=nazwa):
                self.assertEqual(sorted(brak), [])
        self.assertIn('kontener:SetAttribute("KlientGotowy", true)', KLIENT_POTWOROW)
        self.assertIn('c:SetAttribute("Straznik"', SERWER_POTWOROW)
        # serwer czyta tylko swoje atrybuty, testowe i te, które ustawia budowa Workspace/LasTeleport (swiat/biom_las)
        teleport = set(re.findall(r'f:SetAttribute\("(\w+)"', czytaj(REPO, "swiat", "biom_las", "teleport.py")))
        self.assertTrue({"PunktLas", "PatrzLas", "PunktMiasteczka", "PatrzMiasteczko"} <= teleport, teleport)
        self.assertEqual(sorted(napisy(SERWER, "GetAttribute") - serwer - testowe - teleport), [])
        # i odwrotnie: każdy atrybut LasTeleport, który podmieniamy albo czytamy, czyta też TeleportLasu
        tl = napisy(czytaj(REPO, "swiat", "biom_las", "zrodla", "TeleportLasu.server.luau"), "GetAttribute")
        self.assertTrue((napisy(SERWER, "GetAttribute") & teleport) - {"Wygenerowane"} <= tl)

    def test_8c_wiadomosci_zdalne_zgodne(self):
        do_klienta = set(re.findall(r'zdarzenia:FireClient\(gracz, "(\w+)"', bez_komentarzy(SERWER)))
        obslugiwane = set(re.findall(r'polecenie == "(\w+)"', bez_komentarzy(KLIENT).split("zdarzenia.OnClientEvent", 1)[1]))
        self.assertEqual(do_klienta, {"przygotuj", "start", "przerwij", "komunikat"})
        self.assertTrue(do_klienta <= obslugiwane, do_klienta - obslugiwane)
        do_serwera = set(re.findall(r'zdarzenia:FireServer\("(\w+)"', bez_komentarzy(KLIENT)))
        cialo = bez_komentarzy(SERWER).split("zdarzenia.OnServerEvent:Connect", 1)[1].split("\nend)\n", 1)[0]
        self.assertEqual(do_serwera, {"gotowy", "koniec", "odmowa"})
        for p in do_serwera:
            self.assertIn('polecenie == "%s"' % p, cialo)
        # serwer: typy, id bieżącego przelotu, limit wiadomości; klient nie wysyła liczb gry (tylko id przelotu)
        for k in ('type(polecenie) ~= "string"', 'type(id) ~= "number"', "id ~= s.przelot.id", "LIMIT_WIADOMOSCI"):
            self.assertIn(k, cialo)
        self.assertNotIn("InvokeServer", bez_komentarzy(KLIENT))
        self.assertNotIn("RemoteFunction", bez_komentarzy(SERWER) + bez_komentarzy(KLIENT))

    def test_8d_stale_i_nadpisania(self):
        for klucz, wartosc in ZB.STALE.items():
            m = re.search(r"^S\.%s = (.+?)(\s+--.*)?$" % klucz, STALE, re.M)
            self.assertIsNotNone(m, "w Stale.luau nie ma S.%s" % klucz)
            stara = m.group(1).strip()
            if isinstance(wartosc, str) and klucz != "SZABLONY":
                self.assertTrue(stara.startswith('"'), klucz)
            elif klucz == "SZABLONY":
                self.assertTrue(stara.startswith("{"))
            else:
                self.assertRegex(stara, r"^-?\d", klucz)
        walka = json.loads(czytaj(REPO, "tools", "walka", "dane_walki.json"))
        aktorzy = czytaj(REPO, "swiat", "test_walki2", "aktorzy.py")
        for k in ZB.STALE["SZABLONY"].split(","):
            self.assertIn(k, {p["id"] for p in walka["przeciwnicy"]})
            self.assertIn('"klucz": "%s"' % k, aktorzy)
        self.assertEqual(sorted(ZB.STALE["SZABLONY"].split(",")), sorted(DP["gatunki"]))
        self.assertEqual(ZB.STALE["NAZWA_BIOMU"], DP["biom"]["nazwa"])
        self.assertNotEqual(ZB.STALE["NAZWA_SZABLONOW"], re.search(r'S\.NAZWA_SZABLONOW = "(\w+)"', STALE).group(1))
        self.assertNotEqual(ZB.STALE["GUI_BOHATERA"], "LasPotworyBohater")
        # sygnał wyniku i blokada walk: jedna nazwa w Stale, zbudowany BindableEvent, używają obie strony
        sygnal = re.search(r'S\.SYGNAL_WYNIKU = "(\w+)"', STALE).group(1)
        self.assertIn(("BindableEvent", "Sygnaly/" + sygnal), ZB.INNE)
        self.assertIn("Stale.SYGNAL_WYNIKU", SERWER)
        self.assertIn("sygnalWyniku:Fire(gracz, info)", SERWER_POTWOROW)
        self.assertIn("gracz:SetAttribute(Stale.ATRYBUT_BLOKADY, true)", SERWER)
        self.assertIn("gracz:GetAttribute(Stale.ATRYBUT_BLOKADY) == true", SERWER_POTWOROW)
        self.assertIn("st.d.odrodzenieStale == true", SERWER_POTWOROW)
        self.assertIn("if not b.plyta then", SERWER_POTWOROW)
        # pominięcie walki (D-078, opcja A przyjęta na noc 17.11.2026): uchwyt zwolnienia dla serwera prototypu
        self.assertIn(("BindableFunction", "Sygnaly/ZwolnijPoPominieciu"), ZB.INNE)
        self.assertIn('FindFirstChild("ZwolnijPoPominieciu")', SERWER_POTWOROW)
        self.assertIn("zwolnij.OnInvoke = function(gracz: Player)", SERWER_POTWOROW)
        proto = czytaj(REPO, "swiat", "test_walki2", "zrodla", "SerwerWalki2.server.luau")
        self.assertIn('FindFirstChild("ZwolnijPoPominieciu")', proto)
        self.assertIn("LasPasGra = true", proto.split("local ZRODLA_LASU", 1)[1].split("\n", 1)[0])

    def test_8e_haczyki_klienta_potworow_dla_przelotu(self):
        for polecenie in ("wymus", "klip"):
            self.assertIn('elseif polecenie == "%s" then' % polecenie, KLIENT_POTWOROW)
            self.assertIn('sterujPotworami("%s"' % polecenie, KLIENT)
        self.assertIn("w.klipy:maKlip(b)", KLIENT_POTWOROW)
        klipy = czytaj(REPO, "swiat", "test_walki2", "zrodla", "Klipy.luau")
        self.assertIn("function Klipy:maKlip(nazwa: string): boolean", klipy)
        self.assertIn("opcje.potem", klipy)

    def test_8f_przelot_klienta_zawsze_sprzata(self):
        kod = bez_komentarzy(KLIENT)
        for k in ("RunService:UnbindFromRenderStep(KROK_KAMERY)", "ContextActionService:UnbindAction(AKCJA_BLOKADY)",
                  "sterowanie:Enable()", "GuiService.TouchControlsEnabled = dotykBylo", "k.CameraSubject = hum or podmiot",
                  'kontener:SetAttribute("KlientPrzelot", nil)', 'sterujPotworami("wymus", nil)'):
            self.assertIn(k, kod)
        self.assertIn("for i = #s.sprzatanie, 1, -1 do", kod)
        self.assertIn("pcall(s.sprzatanie[i])", kod)
        for zdarzenie in ("gracz.CharacterRemoving:Connect", "kontener.AncestryChanged:Connect"):
            self.assertIn(zdarzenie, kod)
        # nie da się pominąć: brak obsługi klawisza pominięcia
        self.assertNotIn("Enum.KeyCode.Space", kod)

    def test_8g_straznik_studio_i_samousuniecie(self):
        for nazwa in os.listdir(ZR):
            if nazwa.endswith(".luau"):
                self.assertTrue(sprawdz_luau_pasa.SL.pierwsza_instrukcja(czytaj(ZR, nazwa)).startswith(
                    sprawdz_luau_pasa.SL.STRAZNIK), nazwa)
        po = sprawdz_luau_pasa.SL.pierwsza_instrukcja(SERWER).split("\n")
        kod = [x.strip() for x in po[1:6] if x.strip() and not x.strip().startswith("--")]
        self.assertEqual(kod[:2], ["script.Parent:Destroy()", "return"])
        self.assertIn('f:SetAttribute("Wygenerowane", true)', ZB.START)
        self.assertIn("game.PlaceId ~= __MIEJSCE__", ZB.NAGLOWEK_MIEJSCA)
        self.assertIn("IsRunning()", ZB.NAGLOWEK_MIEJSCA)
        self.assertIn("SetWaypoint", ZB.START)

    def test_8h_bez_sciezek_lokalnych(self):
        wzor = re.compile(r"[A-Za-z]:\\\\?Users|/Users/|/home/|AppData|@[a-z0-9-]+\.(?:com|pl)\b", re.I)
        for korzen, _, pliki in os.walk(PAKIET):
            if "__pycache__" in korzen or os.path.basename(korzen) == "testy":
                continue
            for nazwa in pliki:
                if nazwa.endswith((".py", ".luau", ".md", ".json")):
                    with self.subTest(plik=nazwa):
                        self.assertIsNone(wzor.search(czytaj(korzen, nazwa)))

    def test_8i_zbuduj_sucho(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           cwd=REPO)
        wyj = r.stdout.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, wyj[-2000:])
        self.assertIn("sucho: OK", wyj)
        self.assertIn("Workspace/LasPasGra", wyj)

    @unittest.skipIf(LM is None, "brak luau_mini")
    def test_8j_kod_wysylany_do_studio_parsuje_sie(self):
        """Kod, który zbuduj.py składa i wysyła (części, start, zdalne), jest poprawny składniowo."""
        kody = {
            "czesci": ZB.czesci_kod(DPA),
            "start": ZB.START.replace("__KONTENER__", ZB.KONTENER).replace("__USUN__", "false").replace("__ZRODLO__", "x")
                .replace("__SKROT__", "x").replace("__CZAS__", "x").replace("__TESTOWE__", '"a"').replace("__FOLDERY__", '"Moduly"'),
            "inne": ZB.INNE_KOD.replace("__KONTENER__", ZB.KONTENER).replace("__SKROT__", "x").replace("__FOLDERY__", '"Moduly"')
                .replace("__INNE__", '{"RemoteEvent", "Zdalne/ZdarzeniaPasa"}').replace("__STALE__", ZB.stale_luau()),
            "sprawdz": ZB.SPRAWDZ.replace("__MAPA__", "LasPas").replace("__PLYTA__", "x").replace("__WROTA__", "a/b")
                .replace("__ZAPOWIEDZ__", "c").replace("__SZABLONY__", '"lesny_slime"'),
        }
        for nazwa, kod in kody.items():
            with self.subTest(kod=nazwa):
                self.assertNotIn("__", kod)
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()

    @unittest.skipUnless(os.path.isfile(os.path.join(REPO, "swiat", "teleport_chmury", "krainy.json")),
                         "brak swiat/teleport_chmury")
    def test_8k_przejscie_przez_chmury_przez_uchwyt(self):
        """Błąd z próby w Studio 17.11.2026: chmury przenosiły gracza same, a przelot pasa startował 1,2 s po
        przeniesieniu — w połowie opadania kamery chmur (dwa skrypty naraz na kamerze, ucięty początek przelotu).
        Teraz las z chmur idzie przez Sygnaly/PrzeniesDoLasu z przelotPo ≥ czas opadania."""
        tc = os.path.join(REPO, "swiat", "teleport_chmury")
        with open(os.path.join(tc, "krainy.json"), encoding="utf-8") as f:
            kr = json.load(f)
        las = next(k for k in kr["krainy"] if k["id"] == "las")
        pierwszy = las["przybycie"][0]
        self.assertEqual(pierwszy.get("uchwyt"), "PrzeniesDoLasu")
        self.assertEqual(pierwszy.get("gdy_jest"), ZB.KONTENER)
        self.assertIn(pierwszy.get("punkt"), ("las", "przed_brama", "za_brama"))
        cz = kr["czasy"]
        # najgorszy przypadek: serwer przenosi postać na początku zanurzenia (C), potem biel i opadanie (D);
        # przelot przygotowuje kamerę po przelotPo + uspokojenie (DanePasa) — ma to być PO końcu przejścia chmur
        # (pomiar w Studio 17.11: przeniesienie 0,4 s po wyborze, koniec chmur 2,99 s; przy 1,8 s kamery się nakładały)
        koniec_chmur = cz["zanurzenie_s"] + cz["biel_min_s"] + cz["opadanie_s"]
        self.assertGreaterEqual(pierwszy["przelot_po_s"] + DPA["przelot"]["uspokojenie"], koniec_chmur,
                                "przelot pasa ruszyłby w czasie opadania kamery chmur")
        self.assertLessEqual(pierwszy["przelot_po_s"], 10)  # SerwerPasa obcina przelotPo do 0–10 s
        self.assertIn(("BindableFunction", "Sygnaly/PrzeniesDoLasu"), ZB.INNE)
        self.assertIn("przeniesF.OnInvoke = przeniesDoLasu", SERWER)
        self.assertIn("opcje.przelotPo", SERWER)
        st = czytaj(tc, "zrodla", "SerwerTeleportu.server.luau")
        self.assertLess(st.index("przezUchwyt(gracz, kraina)"), st.index("punktPrzybycia(kraina, humanoid, korzen)\n"),
                        "uchwyt musi być pytany przed zwykłymi punktami przybycia")
        self.assertIn("przelotPo = p.przelot_po_s", st)

    def test_8l_proby_w_play_wybieraja_klase(self):
        """Błąd z próby w Studio 17.11.2026: ekran wyboru klasy (src/client/ClassSelectClient) trzyma kamerę w sali
        klas i wyłącza podpowiedzi E — bez Entera przelot, mgła i E w pasie dawały fałszywe wyniki."""
        for nazwa in ("proba_play.py", "proba_dodatkowa.py"):
            with self.subTest(plik=nazwa):
                t = czytaj(TU, nazwa)
                self.assertIn('FindFirstChild("ClassSelect")', t)
                self.assertIn('"Return"', t)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
