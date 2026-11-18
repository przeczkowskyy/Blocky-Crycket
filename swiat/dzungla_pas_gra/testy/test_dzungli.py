# -*- coding: utf-8 -*-
"""Testy offline pakietu swiat/dzungla_pas_gra („Dżungla w grze”, trzeci biom). Bez Studio, bez sieci.

    python -B swiat/dzungla_pas_gra/testy/test_dzungli.py        (unittest; kod 1 przy błędzie)

Ten sam zestaw co test_bagna.py, przesunięty o jeden biom (poprzedni = Bagno, następny = Pustynia „wkrótce”):
1. Dane: generator deterministyczny i aktualny; mapa i sam plan dają te same strefy; 8 / 11 / 14 potworów; poziomy
   stref z konfiguracji (kalkulator 17 → 23, Dżungla zaczyna się poziom po Bagnie), Wąż Stu Lian na końcu.
2. Przegrody: gatunek każdej przegrody jak w planie (D-069: trzy klasy), trasy i domy w polu strefy i w pasie, poza
   strefami spokoju; symulacja ruchu — odstęp ≥ 25, nikt nie wychodzi z pola; scalone strefy rozdają poziomy po miejscach.
3. Styk z Bagnem: wejście do Dżungli zaczyna się ZA bramą Bagna, ratunek tylko od bramy Bagna, prawo wejścia = atrybut
   ustawiany przez serwer Bagna, punkt cofnięcia = punkt przed bramą Bagna, Bagno wie, że za nim jest mapa DzunglaPas;
   brama do Pustyni i tabliczka „wkrótce” na końcu Dżungli; nazwy inne niż w lesie i Bagnie.
4. Przelot: koniec na Wężu Stu Lian, ryk w postoju, klip „ryk” modelu ma 2,0 s.
5. Mgła: prostokąt Dżungli od bramy Bagna; przejście Bagno → Dżungla bez przebłysku (lustro MglaPasa).
6. Walka: przeciwnicy Dżungli = dane lasu bez zmian + 5 wpisów; umiejętności mają choreografię i klipy; moduł danych
   silnika w Luau = dane z generatora; wygrane klas wzorcowych w przyjętych widełkach.
7. Styki: szablony = gatunki = aktorzy Dżungli (dane, ikony), mostek pomijania w SerwerWalki2, dźwięki potworów,
   teleport (kraina otwarta atrybutem bramy Bagna, uchwyt PrzeniesDoDzungli), wskazówki znają biom, Stale_*,
   zbuduj.py --sucho, kod dla Studio parsuje się, brak ścieżek lokalnych.
"""
import importlib.util
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import tempfile
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
PAS = os.path.join(REPO, "swiat", "las_pas_gra")
sys.dont_write_bytecode = True
for _s in (PAKIET, PAS, os.path.join(REPO, "tools", "walka"), os.path.join(REPO, "swiat", "test_walki2")):
    if _s not in sys.path:
        sys.path.insert(0, _s)


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


import logika_pasa as LP  # noqa: E402
import sprawdz_luau_pasa  # noqa: E402
import przeciwnicy as PRZ  # noqa: E402

GEN = _modul("generuj_dane_dzungli_test", os.path.join(PAKIET, "generuj_dane.py"))
ZB = _modul("zbuduj_dzungli_test", os.path.join(PAKIET, "zbuduj.py")).ZB
GEN_LASU = GEN.BAG   # poprzedni biom (nazwa jak w test_bagna.py): Bagno
TL = _modul("test_logiki_lasu_dla_dzungli", os.path.join(REPO, "swiat", "las_potwory", "testy", "test_logiki.py"))
Lg = TL.Lg

M, DP, DPA = GEN.wszystko()
_, DP_LASU, DPA_LASU = GEN_LASU.wszystko()
PLAN = M["plan"]
STREFY = {s["id"]: s for s in DP["strefy"]}
LM = sprawdz_luau_pasa.luau_mini()


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def luau_plik(sciezka):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    return LM.z_luau(it.wykonaj(czytaj(sciezka), os.path.basename(sciezka))[0], pusta_jako_lista=True)


def norm(v):
    if isinstance(v, dict) and not v:
        return []                                            # pusta tabela Luau = pusta lista (z_luau)
    if isinstance(v, dict):
        return {k: norm(x) for k, x in v.items() if not str(k).startswith("_")}
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return v
    return round(float(v), 6)


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_deterministyczny_i_aktualny(self):
        skrypt = os.path.join(PAKIET, "generuj_dane.py")
        r = subprocess.run([sys.executable, "-B", skrypt, "--sprawdz"], cwd=REPO, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            for d in (a, b):
                subprocess.run([sys.executable, "-B", skrypt, "--wyjscie", d], cwd=REPO, capture_output=True, check=True)
            for n in ("DanePotworowDzungli.luau", "DaneDzungli.luau", "DaneWalkiDzungli.luau"):
                with open(os.path.join(a, n), encoding="utf-8") as f1, open(os.path.join(b, n), encoding="utf-8") as f2:
                    t = f1.read()
                    self.assertEqual(t, f2.read(), n)
                self.assertNotIn("\r", t)

    def test_1b_mapa_i_sam_plan_daja_to_samo(self):
        _, dp2, dpa2 = GEN.wszystko(bez_mapy=True)
        for a, b in zip(DP["strefy"], dp2["strefy"]):
            self.assertEqual(norm(a["trasa"]), norm(b["trasa"]), a["id"])
            self.assertEqual(norm(a["domy"]), norm(b["domy"]), a["id"])
        self.assertEqual(norm(DPA["przelot"]["punkty"]), norm(dpa2["przelot"]["punkty"]))
        self.assertEqual(M["zrodlo"], "znaczniki")

    def test_1c_liczby_i_poziomy(self):
        cele = [0, 0, 0]
        for st in DP["strefy"]:
            c = [1, 1, 1] if st["straznik"] else [Lg.cel(st["naraz"], st["max"], G) for G in (1, 8, 20)]
            cele = [x + y for x, y in zip(cele, c)]
        self.assertEqual(cele, [8, 11, 14])                        # krótki pas (D-096), jedna scalona strefa na przegrodę
        for sid, (p1, p2) in GEN.POZIOMY_STREF.items():
            self.assertEqual(STREFY[sid]["poziomy"], [p1, p2])
        self.assertEqual(STREFY["straznik"]["poziomy"], [GEN.POZIOM_STRAZNIKA] * 2)
        self.assertEqual(STREFY["straznik"]["gatunek"], "waz_stu_lian")
        # poziomy rosną przegroda po przegrodzie; Bagno kończy się na 16, gracz wychodzi z niego na ok. 17. — Dżungla od 17
        kolejno = [STREFY[s["id"]]["poziomy"] for s in PLAN["strefy"]]     # z1, g1, o1, t1 (po scaleniu, D-096)
        self.assertEqual([s["id"] for s in PLAN["strefy"]], ["z1", "g1", "o1", "t1"])
        self.assertEqual(kolejno, sorted(kolejno))
        self.assertEqual(kolejno[0][0], max(s["poziomy"][1] for s in DP_LASU["strefy"]) + 1)
        # scalone strefy: poziomy rozdawane po miejscach (SerwerPotworow, poziomNaMiejsce)
        self.assertEqual({s["id"] for s in DP["strefy"] if s.get("poziomyPoMiejscach")}, {"z1", "g1", "o1"})
        self.assertEqual(STREFY["t1"]["odrodzenieS"], 150)
        self.assertTrue(STREFY["t1"]["odrodzenieStale"])


# ============================================================================================== 2. przegrody
def w_polu(st, x, z, zapas=1e-6):
    p = st["pole"]
    return p["x1"] - zapas <= x <= p["x2"] + zapas and p["z1"] - zapas <= z <= p["z2"] + zapas


class TestPrzegrod(unittest.TestCase):
    def test_2a_gatunki_i_klasy(self):
        klasy = {d["id"]: d["klasa"] for d in PRZ.przeciwnicy()}
        przegrody = {}
        for st in PLAN["strefy"]:
            przegrody.setdefault(st["podbiom"], set()).add(GEN.GATUNKI[st["potwor"]])
        trzy = [GEN.GATUNKI[st["potwor"]] for st in PLAN["strefy"] if st.get("scalone_z")]
        self.assertEqual(sorted(klasy[g] for g in trzy), ["mag", "wojownik", "zwiadowca"])   # D-069
        self.assertEqual(klasy["waz_stu_lian"], "straznik")

    def test_2b_trasy_i_domy(self):
        X0, Z0 = M["X0"], M["Z0"]
        pol = PLAN["pas"]["szerokosc"] / 2
        for st in DP["strefy"]:
            if st["straznik"]:
                continue
            with self.subTest(strefa=st["id"]):
                t = st["trasa"]
                for x, z in zip(t["x"], t["z"]):
                    self.assertTrue(w_polu(st, x, z))
                    self.assertLessEqual(abs(z - Z0), pol)
                    for sp in DP["spokojProstokaty"]:
                        self.assertFalse(LP.w_prostokacie(x, z, sp), sp["id"])
                for d in st["domy"]:
                    self.assertTrue(w_polu(st, d["x"], d["z"]))
                    self.assertTrue(w_polu(st, d["wejscie"][0], d["wejscie"][1]))
                self.assertGreaterEqual(st["pole"]["x1"], X0 + PLAN["pas"]["u_od"])

    def test_2c_symulacja_odstep_i_pole(self):
        zasady = DP["zasady"]
        for st in DP["strefy"]:
            if st["straznik"]:
                continue
            v = DP["gatunki"][st["gatunek"]]["predkosc"]
            rnd = random.Random(7)
            sym = TL.Symulacja(st, zasady, v, st["max"], rnd)
            dt, poza, nastepna = 0.25, [], 1.0
            for i in range(1, int(8 * 60 / dt) + 1):
                teraz = i * dt
                if teraz < 8 * 60 - 120 and rnd.random() < dt / 20:
                    wolne = [p for p in sym.potwory if p["zajety"] is None]
                    if wolne:
                        rnd.choice(wolne)["zajety"] = {"do": teraz + rnd.uniform(8, 40),
                                                       "wynik": "wygrana" if rnd.random() < 0.6 else "przegrana"}
                sym.tyknij(teraz, dt)
                if teraz + 1e-9 >= nastepna:
                    sym.odradzaj(teraz)
                    nastepna += 1.0
                for p in sym.potwory:
                    if not w_polu(st, p["x"], p["z"], 0.01):
                        poza.append((teraz, p["id"]))
            with self.subTest(strefa=st["id"]):
                self.assertEqual(sym.bledy[:3], [])
                self.assertEqual(poza[:3], [])
                self.assertGreaterEqual(sym.min_luka, zasady["odstep"] - 1e-6)
                self.assertEqual(len(sym.potwory) + len(sym.kolejka), st["max"])


# ============================================================================================== 3. styk z lasem
class TestStykuZLasem(unittest.TestCase):
    def test_3a_wejscie_za_brama_lasu(self):
        brama_lasu = DPA_LASU["brama"]
        x_bramy = brama_lasu["x"] + brama_lasu["tolerancja"]
        self.assertGreater(DPA["wejscie"]["x1"], x_bramy, "gracz przed bramą Bagna nie może dostać przelotu Dżungli")
        self.assertGreaterEqual(DPA["ratunek"]["x1"], brama_lasu["x"], "ratunek Dżungli nie może zabierać graczy z Bagna")
        self.assertFalse(LP.w_prostokacie(DPA_LASU["przedBrama"]["punkt"][0], DPA_LASU["przedBrama"]["punkt"][2],
                                          DPA["wejscie"]))
        self.assertTrue(LP.w_prostokacie(DPA["przybycie"]["punkt"][0], DPA["przybycie"]["punkt"][2], DPA["wejscie"]))

    def test_3b_prawo_wejscia_z_bramy_lasu(self):
        w = DPA["biom"]["wymaganie"]
        self.assertEqual(w["atrybut"], DPA_LASU["biom"]["atrybutStraznik"])
        self.assertEqual(w["punkt"][0], DPA_LASU["przedBrama"]["punkt"][0])
        self.assertEqual(w["punkt"][2], DPA_LASU["przedBrama"]["punkt"][2])
        serwer = czytaj(PAS, "zrodla", "SerwerPasa.server.luau")
        for k in ("brakWejscia(gracz)", 'powod = "zamkniete"', 'cel = "wymaganie"', "WYMAGANIE.komunikat"):
            self.assertIn(k, serwer)
        # Bagno: następny biom = mapa Dżungli; ZaBrama znika, gdy stoi
        self.assertEqual(DPA_LASU["biom"]["nastepny"]["mapa"], M["kontener"])
        self.assertIn('kontener:FindFirstChild("ZaBrama")', serwer)
        self.assertIn('kontener:SetAttribute("NastepnyBiomJest", true)', serwer)
        self.assertFalse(DPA["biom"]["przekieruj"])
        self.assertFalse(DPA_LASU["biom"]["przekieruj"])   # bramę miasteczka przekierowuje tylko las

    def test_3c_brama_do_dzungli_i_tabliczka(self):
        b = DPA["brama"]
        self.assertAlmostEqual(b["x"], M["X0"] + PLAN["miejsca"][[m["id"] for m in PLAN["miejsca"]].index("brama_pustyni")]["u"])
        self.assertEqual(DPA["tabliczka"]["tekst"], "PUSTYNIA — WKRÓTCE")
        self.assertGreater(DPA["tabliczka"]["punkt"][0], b["x"])
        self.assertEqual(DPA["napisBramy"]["podpis"], "Pokonaj Węża Stu Lian")
        self.assertEqual(DPA["mapa"]["grupaWrot"], "BramaPustyni/Wrota")
        x, z = DPA["straznik"]["poz"][0], DPA["straznik"]["poz"][2]
        self.assertLess(x, b["x"])
        self.assertEqual(LP.decyzja_bramy(b["x"] + 5, z, False, b), "cofnij")
        self.assertEqual(LP.decyzja_bramy(b["x"] + 5, z, True, b), "wolno")

    def test_3d_nazwy_inne_niz_w_lesie(self):
        bl, bb = DPA_LASU["biom"], DPA["biom"]
        for k in ("uchwyt", "pamiecPrzelot", "pamiecStraznik", "atrybutPrzelot", "atrybutStraznik", "atrybutPunktu"):
            self.assertNotEqual(bl[k], bb[k], k)
        self.assertIn(("BindableFunction", "Sygnaly/" + bb["uchwyt"]), ZB.INNE)
        self.assertNotIn(("BindableFunction", "Sygnaly/PrzeniesDoLasu"), ZB.INNE)
        self.assertNotIn(("BindableFunction", "Sygnaly/PrzeniesDoBagna"), ZB.INNE)
        zb_bagna = _modul("zb_bagna_test_dz", os.path.join(REPO, "swiat", "bagno_pas_gra", "zbuduj.py"))
        for k in ("NAZWA_SZABLONOW", "GUI_BOHATERA", "GUI_BANERA", "PREFIKS", "NAZWA_KONTENERA", "NAZWA_BIOMU"):
            self.assertNotEqual(ZB.STALE[k], zb_bagna.STALE[k], k)
        for k in ("NAZWA_SZABLONOW", "GUI_BOHATERA", "GUI_BANERA", "PREFIKS", "NAZWA_KONTENERA", "NAZWA_BIOMU"):
            self.assertNotEqual(ZB.STALE[k], GEN_LASU.KONFIG and _modul("zb_lasu_test", os.path.join(PAS, "zbuduj.py")).STALE[k], k)
        klient = czytaj(PAS, "zrodla", "KlientPasa.client.luau")
        self.assertIn('local KROK_KAMERY = kontener.Name .. "Przelot"', klient)
        self.assertIn('local NAZWA_GUI = kontener.Name .. "Ekran"', klient)


    def test_3e_jedno_pilnowanie_przy_bramie(self):
        """Lustro reguły SerwerPasa: gdy stoi Dżungla, Bagno pilnuje przelotu i ratunku tylko przed linią swojej bramy
        (x < granica), Dżungla od niej; cofanie nieuprawnionych: Bagno do bramy + głębokość, Dżungla od odX dalej.
        W każdym miejscu najwyżej jeden serwer przenosi gracza (wcześniej przy bramie mogły dwa)."""
        bl = DPA_LASU["brama"]
        granica = bl["x"]
        odX = DPA["biom"]["wymaganie"]["odX"]
        self.assertAlmostEqual(odX, bl["x"] + bl["glebokosc"])
        z = M["Z0"]
        x = granica - 84.0
        while x <= granica + 366.0:
            ratuje = [LP.potrzeba_ratunku(x, -40, z, DPA_LASU["ratunek"]) and x < granica,
                      LP.potrzeba_ratunku(x, -40, z, DPA["ratunek"])]
            self.assertEqual(sum(ratuje), 1, "ratunek x=%.2f: %s" % (x, ratuje))
            przelot = [LP.w_prostokacie(x, z, DPA_LASU["wejscie"]) and x < granica, LP.w_prostokacie(x, z, DPA["wejscie"])]
            self.assertLessEqual(sum(przelot), 1, "przelot x=%.2f" % x)
            cofa = [LP.decyzja_bramy(x, z, False, bl) == "cofnij", LP.w_prostokacie(x, z, DPA["wejscie"]) and x >= odX]
            self.assertLessEqual(sum(cofa), 1, "cofanie x=%.2f" % x)
            if x > bl["x"] + bl["tolerancja"]:
                self.assertEqual(sum(cofa), 1, "nieuprawniony bez cofania x=%.2f" % x)
            x += 0.25
        serwer = czytaj(PAS, "zrodla", "SerwerPasa.server.luau")
        for k in ("D.ratunek) and not zaGranica(poz.X) then", "and not zaGranica(poz.X),", "granicaNastepnego = D.brama.x",
                  "poz.X >= (WYMAGANIE.odX or -math.huge)", "x >= granicaNastepnego"):
            self.assertIn(k, serwer)


# ============================================================================================== 4. przelot
class TestPrzelotu(unittest.TestCase):
    def test_4a_koniec_na_strazniku_i_ryk(self):
        p = DPA["przelot"]
        ost = p["punkty"][-1]
        s = DPA["straznik"]["poz"]
        self.assertLess(math.hypot(ost["patrz"][0] - s[0], ost["patrz"][2] - s[2]), 3.0)
        self.assertLessEqual(p["zatrzymanieOd"], p["rykOd"])
        self.assertLessEqual(p["rykOd"] + p["rykDl"], p["czas"] + 1e-9)
        d = json.loads(czytaj(REPO, "swiat", "test_walki2", "dane", "waz_stu_lian.json"))
        ryk = next(k for k in d["klipy"] if k["n"] == p["klip"])
        self.assertAlmostEqual(ryk["dl"] / ryk["fps"], p["rykDl"], places=3)
        for q in p["punkty"]:
            self.assertTrue(DPA["wejscie"]["x1"] - 40 <= q["poz"][0] <= DPA["wejscie"]["x2"], q)


# ============================================================================================== 5. mgła
def symuluj_mgly(mgly, droga, dt=1 / 60.0):
    """Lustro pętli MglaPasa.client.luau dla kilku mgieł naraz (ten sam porządek co w skrypcie: cel, publikacja,
    ustąpienie, przejęcie od wartości zastanych, krok wagi, zapis). Atmosphere = jedna liczba (Density).
    mgly: [{nazwa, prostokat, pas, tempo, cel}]; droga: lista pozycji kamery (x, z) co klatkę. → [Density co klatkę]"""
    baza = 0.30
    atm = {"d": baza}
    stan = [{"waga": 0.0, "ustawiona": -1.0, "od": baza, "cel_pub": None, "ostatnia": -1.0} for _ in mgly]
    wynik = []
    for x, z in droga:
        for i, m in enumerate(mgly):
            s = stan[i]
            cel = round(LP.waga_mgly(x, z, m["prostokat"], m["pas"]) * 100 + 1e-9) / 100.0
            s["cel_pub"] = cel
            ustep = any(stan[j]["cel_pub"] is not None and (stan[j]["cel_pub"] > cel or (
                stan[j]["cel_pub"] == cel and cel > 0 and mgly[j]["nazwa"] < m["nazwa"])) for j in range(len(mgly)) if j != i)
            if ustep:
                s["waga"], s["ustawiona"], s["od"] = 0.0, 0.0, baza
                continue
            if s["waga"] <= 0 and cel > 0:
                s["od"] = atm["d"]
            elif s["od"] != baza and (s["waga"] >= 1 or cel < s["waga"]):
                s["od"] = baza
            s["waga"] = LP.krok_wagi(s["waga"], cel, m["tempo"], dt)
            obca = s["waga"] > 0 and s["ustawiona"] >= 0 and abs(atm["d"] - s["ostatnia"]) > 1e-4
            if obca or abs(s["waga"] - s["ustawiona"]) >= 0.002:
                s["ustawiona"] = s["waga"]
                atm["d"] = s["od"] + (m["cel"] - s["od"]) * s["waga"]
                s["ostatnia"] = atm["d"]
        wynik.append(atm["d"])
    return wynik


class TestMgly(unittest.TestCase):
    def test_5a_prostokat_dzungli_od_bramy_bagna(self):
        m, ml = DPA["mgla"], DPA_LASU["mgla"]
        self.assertAlmostEqual(m["x1"], M["X0"] + PLAN["pas"]["u_od"])
        self.assertAlmostEqual(m["x2"], M["X0"] + PLAN["pas"]["u_do"])
        self.assertLessEqual(ml["x2"] - m["x1"], 10, "prostokąty mgieł Bagna i Dżungli zachodzą na siebie najwyżej 10 st")
        self.assertEqual(m["cel"]["Color"], "8FC79A")
        mgla = czytaj(PAS, "zrodla", "MglaPasa.client.luau")
        for k in ('kontener:SetAttribute("CelMglyPasa", celOkr)', "ustepujeInnej(celOkr)", "d.Name < kontener.Name"):
            self.assertIn(k, mgla)

    def test_5b_przejscie_bagno_dzungla_bez_przeblysku(self):
        mgly = [{"nazwa": "BagnoPasGra", "prostokat": DPA_LASU["mgla"], "pas": DPA_LASU["mgla"]["pas"],
                 "tempo": DPA_LASU["mgla"]["tempo"], "cel": DPA_LASU["mgla"]["cel"]["Density"]},
                {"nazwa": "DzunglaPasGra", "prostokat": DPA["mgla"], "pas": DPA["mgla"]["pas"],
                 "tempo": DPA["mgla"]["tempo"], "cel": DPA["mgla"]["cel"]["Density"]}]
        z = M["Z0"]
        # bieg 16 st/s z Bagna (134 st przed bramą Bagna) przez bramę do Dżungli (170 st za nią), postój, z powrotem
        xa = DPA_LASU["brama"]["x"] - 134.0
        xb = xa + 16 * 19
        droga = [(xa + 16 * t / 60.0, z) for t in range(0, 60 * 19)] + [(xb, z)] * 180
        droga += [(xb - 16 * t / 60.0, z) for t in range(0, 60 * 19)] + [(xa, z)] * 180
        d = symuluj_mgly(mgly, droga)
        las, bagno = mgly[0]["cel"], mgly[1]["cel"]
        self.assertGreater(min(d[60:]), min(las, bagno) - 0.02, "na granicy mgła nie może zgasnąć do bazy")
        self.assertAlmostEqual(d[60 * 19 + 170], bagno, places=3)
        self.assertAlmostEqual(d[-1], las, places=3)
        skoki = max(abs(a - b) for a, b in zip(d, d[1:]))
        self.assertLess(skoki, 0.01, "skok gęstości między klatkami")


# ============================================================================================== 6. walka
class TestWalki(unittest.TestCase):
    def test_6a_dane_lasu_bez_zmian_plus_dzungla(self):
        lasu = PRZ.dane_lasu()
        bagna = PRZ.dane_walki_dzungli()
        for k in lasu:
            if k != "przeciwnicy":
                self.assertEqual(lasu[k], bagna[k], k)
        n = len(lasu["przeciwnicy"])
        self.assertEqual(bagna["przeciwnicy"][:n], lasu["przeciwnicy"])
        self.assertEqual([p["id"] for p in bagna["przeciwnicy"][n:]], list(GEN.GATUNKI.values()))
        self.assertEqual([p["ranga"] for p in bagna["przeciwnicy"][n:]].count("straznik"), 1)

    def test_6b_umiejetnosci_maja_choreografie_i_klipy(self):
        import aktorzy as A
        choreo = czytaj(REPO, "swiat", "test_walki2", "zrodla", "Choreografie.luau")
        for d in PRZ.przeciwnicy():
            w = A.PO_KLUCZU[d["id"]]
            dane = A.wczytaj(d["id"])
            klipy = {k["n"] for k in dane["klipy"]}
            for u in d["umiejetnosci"]:
                with self.subTest(gatunek=d["id"], umiejetnosc=u):
                    self.assertRegex(choreo, r"\n\t%s = \{" % u)
                    self.assertIn(w["umiejetnosci"].get(u), klipy)
            for akcja, klip in w["klipy"].items():
                if klip:
                    self.assertIn(klip, klipy, (d["id"], akcja))

    @unittest.skipIf(LM is None, "brak luau_mini")
    def test_6c_moduly_luau_rowne_generatorowi(self):
        for plik, dane in ((os.path.join(PAKIET, "zrodla", "DaneDzungli.luau"), DPA),
                           (os.path.join(PAKIET, "zrodla", "DanePotworowDzungli.luau"), DP),
                           (os.path.join(PAKIET, "silnik", "DaneWalkiDzungli.luau"), PRZ.dane_walki_dzungli())):
            with self.subTest(plik=os.path.basename(plik)):
                self.assertEqual(norm(luau_plik(plik)), norm(dane))

    @unittest.skipIf(LM is None, "brak luau_mini")
    def test_6e_wlasne_efekty_umiejetnosci(self):
        """Każda umiejętność każdego potwora Dżungli ma własny wygląd (Choreografie.UMIEJETNOSCI_AKTORA) — nic nie jest
        pożyczone; silnik dalej zna te same id umiejętności (logika walki bez zmian); README ma tabelę, a próba w grze
        (J15) sprawdza każdą z nich."""
        ch = luau_plik(os.path.join(REPO, "swiat", "test_walki2", "zrodla", "Choreografie.luau"))
        wa, ogolne = ch["UMIEJETNOSCI_AKTORA"], ch["UMIEJETNOSCI"]
        # id silnika — te same co przed własnymi efektami (zmiana wyglądu nie może ruszyć danych walki)
        silnik = {"zwijogon": ["skupienie", "rozszarpanie"], "gebokwiat": ["lodowy_pocisk"], "kokosowy_silacz": ["ciecie"],
                  "pancernik_ruin": ["kamienna_skora"], "waz_stu_lian": ["zatruta_strzala", "rozszarpanie"]}
        self.assertEqual({d["id"]: d["umiejetnosci"] for d in PRZ.przeciwnicy()}, silnik)
        self.assertEqual(set(wa), set(silnik))
        readme = czytaj(PAKIET, "README.md")
        proba = _modul("proba_play_dzungli_test", os.path.join(TU, "proba_play.py"))
        for gatunek, umiejetnosci in silnik.items():
            self.assertEqual(set(wa[gatunek]), set(umiejetnosci), gatunek)
            self.assertEqual(set(proba.EFEKTY[gatunek][2]), set(umiejetnosci), "próba J15: %s" % gatunek)
            for u in umiejetnosci:
                with self.subTest(gatunek=gatunek, umiejetnosc=u):
                    w = wa[gatunek][u]
                    for pole in ch["POLA_CZASU"]:
                        self.assertEqual(w.get(pole), ogolne[u].get(pole), "pole czasu / kamery %s" % pole)
                    self.assertIn("`%s`" % u, readme, "README: brak wiersza umiejętności")
                    if "nazwa" in w:
                        self.assertIn(w["nazwa"], readme, "README: brak napisu umiejętności")
                    oczek_wyglad, _ = proba.EFEKTY[gatunek][2][u]
                    for pole, wartosc in oczek_wyglad.items():
                        if pole in ("kly",):
                            self.assertEqual("kly" in w, wartosc)
                        else:
                            self.assertEqual(w.get(pole), wartosc, "próba J15 oczekuje innego %s" % pole)
        # nazwy instancji efektów, których próba szuka po walce = nazwy w kodzie własnych efektów
        ef = czytaj(REPO, "swiat", "test_walki2", "zrodla", "Efekty3D.luau")
        nowe = (ef.split("--[[ Ukąszenie (Dżungla", 1)[1].split("-- wybuchy (rozbłysk przy trafieniu)", 1)[0]
                + ef.split("-- Dżungla — usypiający pyłek", 1)[1].split("function Efekty:pocisk(", 1)[0]
                + ef.split("Dżungla (18.11.2026): ozdoby własnych efektów", 1)[1].split("function Efekty:wyglad(", 1)[0])
        self.assertEqual(set(re.findall(r'Name = "([A-Za-z]+)"', nowe)), set(proba.NAZWY_EFEKTOW))
        # …i żadna z nich nie jest nazwą części modelu aktora (próba liczyłaby wtedy modele: „Kiel” Węża, 18.11.2026)
        dane = os.path.join(REPO, "swiat", "test_walki2", "dane")
        for plik in sorted(os.listdir(dane)):
            if plik.endswith(".json"):
                tekst = czytaj(dane, plik)
                for nazwa in proba.NAZWY_EFEKTOW:
                    self.assertNotIn('"%s"' % nazwa, tekst, "%s: część modelu nazywa się jak część efektu" % plik)

    def test_6d_wygrane_klas_w_widelkach(self):
        """Postacie wzorcowe (bez treningu) na poziomie wejścia do przegrody; rzadki i strażnik: gracz o poziom wyżej.
        Widełki przyjęte (do zmiany): zwykłe 65–90%, rzadki 40–70%, strażnik 15–45%, rozstęp klas ≤ 20 pp."""
        widelki = {"zwykly": (65, 90), "rzadki": (40, 70), "straznik": (15, 45)}
        ranga = {d["id"]: d["ranga"] for d in PRZ.przeciwnicy()}
        poziomy = {"zwijogon": [(17, 17)], "gebokwiat": [(19, 19)], "kokosowy_silacz": [(21, 21)],
                   "pancernik_ruin": [(23, 24)], "waz_stu_lian": [(23, 24)]}
        for pid, Lp, Lgr, w in PRZ.tabela(200, poziomy):
            lo, hi = widelki[ranga[pid]]
            with self.subTest(gatunek=pid):
                self.assertTrue(lo <= statistics.mean(w.values()) <= hi, w)
                self.assertLessEqual(max(w.values()) - min(w.values()), 20, w)


# ============================================================================================== 7. styki
class TestStykow(unittest.TestCase):
    def test_7a_szablony_aktorzy_ikony(self):
        import aktorzy as A
        interfejs = czytaj(REPO, "swiat", "test_walki2", "zrodla", "InterfejsWalki2.luau")
        self.assertEqual(sorted(ZB.STALE["SZABLONY"].split(",")), sorted(DP["gatunki"]))
        self.assertEqual(ZB.SZABLONY, ZB.STALE["SZABLONY"].split(","))
        klucze = [a["klucz"] for a in A.AKTORZY]
        for g in DP["gatunki"]:
            with self.subTest(gatunek=g):
                self.assertIn(g, klucze)
                self.assertTrue(os.path.isfile(os.path.join(REPO, "swiat", "test_walki2", "dane", g + ".json")))
                self.assertTrue(os.path.isfile(os.path.join(REPO, "swiat", "postacie", A.PO_KLUCZU[g]["model"] + ".py")))
                self.assertRegex(interfejs, r"\n\t%s = \{" % g)
        # aktorzy Dżungli na końcu tabeli (za Bagnem): galeria lasu, bohaterów i Bagna bez zmian
        self.assertEqual(klucze[-5:], [a["klucz"] for a in A.AKTORZY_DZUNGLI])

    def test_7b_mostek_pomijania_zna_dzungle(self):
        proto = czytaj(REPO, "swiat", "test_walki2", "zrodla", "SerwerWalki2.server.luau")
        for lista in ("local ZRODLA =", "local ZRODLA_LASU ="):
            linia = proto.split(lista, 1)[1].split("\n", 1)[0]
            self.assertIn(ZB.KONTENER + " = true", linia)
        self.assertIn("znanyGatunek(k, gatunek)", proto)
        self.assertIn(("BindableFunction", "Sygnaly/ZwolnijPoPominieciu"), ZB.INNE)
        self.assertIn(("BindableEvent", "Sygnaly/WynikWalki"), ZB.INNE)

    def test_7c_dzwieki_potworow(self):
        ust = json.loads(czytaj(REPO, "swiat", "dzwiek_gra", "ustawienia.json"))
        for g in DP["gatunki"]:
            self.assertIn(ust["glosy_potworow"].get(g), ust["zdarzenia"], g)

    def test_7d_teleport_przez_chmury(self):
        tc = os.path.join(REPO, "swiat", "teleport_chmury")
        kr = json.loads(czytaj(tc, "krainy.json"))
        b = next(k for k in kr["krainy"] if k["id"] == "dzungla")
        self.assertFalse(b["od_poczatku"])
        self.assertEqual(b["odblokowanie"]["atrybut_gracza"], DPA_LASU["biom"]["atrybutStraznik"])
        p = b["przybycie"][0]
        self.assertEqual((p["gdy_jest"], p["uchwyt"]), (ZB.KONTENER, DPA["biom"]["uchwyt"]))
        self.assertIn(p["punkt"], ("przybycie", "las"))
        cz = kr["czasy"]
        self.assertGreaterEqual(p["przelot_po_s"] + DPA["przelot"]["uspokojenie"],
                                cz["zanurzenie_s"] + cz["biel_min_s"] + cz["opadanie_s"])
        st = czytaj(tc, "zrodla", "SerwerTeleportu.server.luau")
        self.assertIn("if not otwarta(gracz, w, kraina) then", st)
        self.assertIn("gracz:GetAttribute(o.atrybut_gracza) == true", st)
        dane = czytaj(tc, "zrodla", "Dane.luau")
        self.assertIn("PrzeniesDoDzungli", dane, "zrodla/Dane.luau teleportu nieaktualny (zbuduj.py --sucho)")

    def test_7d2_wskazowki_znaja_dzungle(self):
        u = json.loads(czytaj(REPO, "swiat", "wskazowki_gry", "ustawienia.json"))
        b = next(x for x in u["zrodla"]["biomy"] if x["id"] == "dzungla")
        self.assertEqual((b["kontener"], b["atrybut_straznika"]), (ZB.KONTENER, DPA["biom"]["atrybutStraznik"]))
        self.assertEqual(u["zrodla"]["walki"].get(ZB.KONTENER), "dzungla")
        for kid in ("c_poziomy_dzungla", "c_straznik_dzungla", "e_brama_pustynia", "e_koniec_dzungla"):
            self.assertIn(kid, u["kroki"])

    def test_7e_stale_i_sucho(self):
        stale = czytaj(REPO, "swiat", "las_potwory", "zrodla", "Stale.luau")
        for k in ZB.STALE:
            self.assertRegex(stale, r"\nS\.%s = " % k, k)
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           cwd=REPO)
        wyj = r.stdout.decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, wyj[-2000:])
        self.assertIn("sucho: OK", wyj)
        self.assertIn("Workspace/DzunglaPasGra", wyj)
        self.assertIn("DaneWalkiDzungli.luau", wyj)

    @unittest.skipIf(LM is None, "brak luau_mini")
    def test_7f_kod_dla_studio_parsuje_sie(self):
        kody = {"czesci": ZB.czesci_kod(DPA),
                "start": ZB.START.replace("__KONTENER__", ZB.KONTENER).replace("__USUN__", "false")
                    .replace("__ZRODLO__", "x").replace("__SKROT__", "x").replace("__CZAS__", "x")
                    .replace("__TESTOWE__", '"a"').replace("__FOLDERY__", '"Moduly"')}
        for nazwa, kod in kody.items():
            with self.subTest(kod=nazwa):
                self.assertNotIn("__", kod)
                self.assertIn(ZB.KONTENER, kod)
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()

    def test_7h_proba_play_kod_luau_parsuje_sie(self):
        """Próba w Play (część B) — przynajmniej każdy jej kawałek Luau się parsuje,
        a wybór klasy zamyka Enter (jak w próbach lasu: ekran ClassSelect trzyma kamerę i wyłącza podpowiedzi)."""
        sciezka = os.path.join(TU, "proba_play.py")
        r = subprocess.run([sys.executable, "-B", sciezka, "--sprawdz"], cwd=REPO, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace"))
        tekst = czytaj(sciezka)
        self.assertIn('FindFirstChild("ClassSelect")', tekst)
        self.assertIn('nacisnij("Return")', tekst)
        for kod in ("J%02d" % i for i in range(18)):   # J15–J17: własne efekty umiejętności (18.11.2026)
            self.assertIn('punkt("%s"' % kod, tekst)
        self.assertIn('S:Invoke("wstrzymaj", true)', tekst)

    def test_7g_bez_sciezek_lokalnych(self):
        wzor = re.compile(r"[A-Za-z]:\\\\?Users|/Users/|/home/|AppData|@[a-z0-9-]+\.(?:com|pl)\b", re.I)
        for korzen, _, pliki in os.walk(PAKIET):
            if "__pycache__" in korzen or os.path.basename(korzen) == "testy":
                continue
            for nazwa in pliki:
                if nazwa.endswith((".py", ".luau", ".md", ".json")):
                    with self.subTest(plik=nazwa):
                        self.assertIsNone(wzor.search(czytaj(korzen, nazwa)))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
