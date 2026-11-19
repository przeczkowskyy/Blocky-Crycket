#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test bez Studio pakietu swiat/cutscenka_biomu (D-077).

    python -B swiat/cutscenka_biomu/testy/test_cutscenki.py

1. dane = mapy i pakiety gry: nazwy biomów i strażników, atrybuty pamięci, prostokąty, moduł DaneCutscenki aktualny;
2. trasa każdego biomu (krzywa, którą gra klient): czas, ciągłość, prędkość, przyspieszenie, obrót, odstęp od brył
   mapy, kolejność i zwolnienia przy przegrodach, inkubator i strażnik w kadrze; trasa wynika z mapy;
3. automat i pamięć „widziane”: pierwsze wejście, drugie wejście, odmowa, cisza klienta, pominięcie, śmierć postaci,
   odtworzenie na życzenie, odblokowanie w każdej ścieżce; zapis postępu zostaje wyłączony;
4. Luau: kontrola statyczna, LogikaCutscenki wykonana w luau_mini = lustro w Pythonie;
5. telefon: układ napisów i przycisku na 667 × 375 i 844 × 390;
6. budowniczy --sucho, haczyk w SerwerPasa, nazwy zależności w cudzych źródłach, brak ścieżek i numerów w plikach.
"""
import json
import os
import random
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import logika_cutscenki as LP  # noqa: E402
import sprawdz_luau_cutscenki as SLC  # noqa: E402
import zbuduj as ZB  # noqa: E402

LM = SLC.luau_mini()
ZR = os.path.join(PAKIET, "zrodla")
U = DN.ustawienia()
D = DN.wszystko(U)
PR = U["progi"]
MIARY = {b["id"]: DN.miary_trasy(b["trasa"], b["_mapa"], U) for b in D["biomy"]}
STALE = {"uspokojenie": 0.5, "odpowiedz": 3.0, "ponowPoOdmowie": 1.0, "ponowPoCiszy": 5.0, "probMaks": 3, "ladowanie": 4.0,
         "zapas": 6.0, "strumienCo": 1.0}


def czytaj(*czesci):
    with open(os.path.join(REPO, *czesci), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


# ============================================================================================== 1. dane
class TestDane(unittest.TestCase):
    def test_1a_trzy_biomy_w_kolejnosci_pasa(self):
        self.assertEqual([b["id"] for b in D["biomy"]], ["las", "bagno", "dzungla"])
        x = [b["prostokat"]["x1"] for b in D["biomy"]]
        self.assertEqual(x, sorted(x))
        for a, b in zip(D["biomy"], D["biomy"][1:]):
            self.assertLessEqual(a["prostokat"]["x2"], b["prostokat"]["x1"], "prostokąty biomów nie mogą się nakładać")

    def test_1b_nazwy_z_pakietow_nie_wymyslone(self):
        for wpis, b in zip(U["biomy"], D["biomy"]):
            G = DN.dane_gry(wpis)
            self.assertEqual(b["nazwa"], G["biom"]["nazwa"])
            self.assertEqual(b["atrybut"], G["biom"]["atrybutPrzelot"])
            self.assertEqual(b["mapa"], G["mapa"]["nazwa"])
            self.assertEqual(b["straznik"]["gatunek"], G["straznik"]["gatunek"])
            z = b["_mapa"].z
            self.assertEqual(b["straznik"]["nazwa"], z["straznik"]["potwor"])
            self.assertEqual(b["mapa"], z["kontener"]["nazwa"].split("/")[-1])
            nazwy = [p["nazwa"] for p in z["przegrody"]]
            for p in b["trasa"]["przystanki"]:
                self.assertIn(p["nazwa"], nazwy)
            self.assertEqual(b["wymaganie"], (G["biom"].get("wymaganie") or {}).get("atrybut"))

    def test_1c_straznik_tam_gdzie_w_pakiecie_gry(self):
        for wpis, b in zip(U["biomy"], D["biomy"]):
            G = DN.dane_gry(wpis)
            for k in (0, 2):
                self.assertAlmostEqual(b["straznik"]["poz"][k], G["straznik"]["poz"][k], delta=0.01)

    def test_1d_modul_luau_aktualny_i_czytelny(self):
        ok, _ = DN.aktualny()
        self.assertTrue(ok, "zrodla/DaneCutscenki.luau nieaktualny — uruchom dane.py")
        T = DN.tabela_luau(czytaj("swiat", "cutscenka_biomu", "zrodla", "DaneCutscenki.luau"))
        self.assertEqual(T["skrot"], D["skrot"])
        self.assertEqual(len(T["biomy"]), 3)
        for t, b in zip(T["biomy"], D["biomy"]):
            self.assertEqual(len(t["trasa"]["poz"]), 3 * b["trasa"]["n"])
            self.assertEqual(len(t["trasa"]["patrz"]), 3 * b["trasa"]["n"])
            self.assertEqual(t["trasa"]["poz"], [float(x) for x in b["trasa"]["poz"]])

    def test_1e_parser_tabel_luau(self):
        t = DN.tabela_luau('if x then return {} end\nreturn { a = 1, b = { 1, 2.5, -3 }, c = "ż\\"x", d = true, -- k\n e = { f = { } } }')
        self.assertEqual(t, {"a": 1.0, "b": [1.0, 2.5, -3.0], "c": 'ż"x', "d": True, "e": {"f": []}})


# ============================================================================================== 2. trasa
class TestTrasa(unittest.TestCase):
    def test_2a_czas_w_granicach(self):
        for b in D["biomy"]:
            m = MIARY[b["id"]]
            self.assertGreaterEqual(m["czas"], PR["czas_od_s"])
            self.assertLessEqual(m["czas"], PR["czas_do_s"])
            self.assertAlmostEqual(b["trasa"]["n"], round(m["czas"] / b["trasa"]["krok"]) + 1)

    def test_2b_ciaglosc_predkosc_przyspieszenie_obrot(self):
        for b in D["biomy"]:
            m = MIARY[b["id"]]
            self.assertLessEqual(m["skok_maks"], PR["ciaglosc_skok_maks_st"], b["id"])
            self.assertLessEqual(m["predkosc_maks"], PR["predkosc_maks_st_s"], b["id"])
            self.assertLessEqual(m["przyspieszenie_maks"], PR["przyspieszenie_maks_st_s2"], b["id"])
            self.assertLessEqual(m["przyspieszenie_wektorowe_maks"], PR["przyspieszenie_maks_st_s2"], b["id"])
            self.assertLessEqual(m["obrot_maks"], PR["obrot_maks_st_s"], b["id"])
            self.assertLess(m["predkosc_koncowa"], 0.5, "kamera stoi na strażniku")

    def test_2c_odstep_od_bryl_mapy(self):
        for b in D["biomy"]:
            m = MIARY[b["id"]]
            self.assertGreaterEqual(m["odstep_min"], U["trasa"]["odstep_min_st"], "%s: %s" % (b["id"], m["odstep_gdzie"]))
            self.assertLessEqual(m["bok_maks"], PR["bok_maks_st"], "kamera trzyma się środka pasa, z dala od kulis")
            self.assertGreaterEqual(m["wysokosc_min"], PR["nad_ziemia_min_st"])
            self.assertLess(b["_mapa"].pominiete, len(b["_mapa"].czesci) * 0.2, "za dużo brył pominiętych jako przezroczyste")

    def test_2d_kolejnosc_i_zwolnienia(self):
        for b in D["biomy"]:
            m = MIARY[b["id"]]
            self.assertLessEqual(m["cofniecie"], PR["cofniecie_maks_st"], "kamera nie cofa się wzdłuż pasa")
            p = m["przystanki"]
            uk = b["trasa"]["uklad"]
            self.assertEqual([x["nazwa"] for x in p], [x["nazwa"] for x in uk["przegrody"]])
            self.assertEqual([x["rola"] for x in p][-1], "leze", "ostatni przystanek przed areną to leże rzadkiego potwora")
            self.assertEqual([x["t"] for x in p], sorted(x["t"] for x in p))
            for x, pg in zip(p, uk["przegrody"]):
                u = x["x"] - b["_mapa"].X0
                self.assertTrue(pg["u"][0] - 2 <= u <= pg["u"][1], "%s: przystanek %s poza przegrodą" % (b["id"], x["nazwa"]))
                self.assertLessEqual(x["predkosc"], PR["zwolnienie_najwyzej_udzial"] * m["przelotowa"], x["nazwa"])
                self.assertLess(x["t"], m["lot"])

    def test_2e_start_inkubator_straznik(self):
        for b in D["biomy"]:
            m, tr, M = MIARY[b["id"]], b["trasa"], b["_mapa"]
            uk = tr["uklad"]
            self.assertLess(tr["poz"][0], M.X0 + uk["przybycie"][0], "kamera startuje za plecami gracza")
            self.assertGreaterEqual(m["inkubator_w_kadrze_s"], 0.4, "inkubator widać na początku")
            koniec = tr["poz"][-3:]
            self.assertLess(koniec[0], b["straznik"]["poz"][0], "kamera kończy przed strażnikiem, od strony wejścia")
            for nazwa, k in m["kadry"].items():
                self.assertLessEqual(k["y"], 1 - 2 * U["oprawa"]["pasy_udzial"], "%s %s: strażnik wychodzi pod pasy" % (b["id"], nazwa))
                self.assertLessEqual(k["x"], 0.95)
                self.assertGreaterEqual(k["udzial"], PR["straznik_w_kadrze_min_udzial"])
            ryk = tr["lot"] + U["oprawa"]["straznik"]["ryk_po_s"]
            self.assertLess(ryk + 2.0, tr["czas"] - U["oprawa"]["koniec"]["zaciemnienie_s"] + 0.35, "ryk mieści się w postoju")

    def test_2f_trasa_wynika_z_mapy(self):
        wpis = U["biomy"][0]
        M = DN.Mapa(wpis["mapa"], U["trasa"]["przezroczystosc_przeszkody_do"])
        w0, _, _ = DN.wezly_biomu(M, U)
        M.z["straznik"]["miejsce"][0] -= 6
        M.z["przegrody"][2]["u"] = [M.z["przegrody"][2]["u"][0] + 5, M.z["przegrody"][2]["u"][1]]
        w1, _, _ = DN.wezly_biomu(M, U)
        self.assertAlmostEqual(w1[-1]["patrz"][0], w0[-1]["patrz"][0] - 6, delta=1e-6)
        self.assertAlmostEqual(w1[3]["poz"][0], w0[3]["poz"][0] + 5, delta=1e-6)

    def test_2g_kolizja_podnosi_wezly_albo_zatrzymuje(self):
        wpis = U["biomy"][1]
        M = DN.Mapa(wpis["mapa"], U["trasa"]["przezroczystosc_przeszkody_do"])
        tr0 = DN.trasa_biomu(M, U)
        x = tr0["poz"][3 * 40]
        # ściana w poprzek pasa do wysokości 24 — trasa musi ją ominąć górą
        M.male.append((x, 12.0, M.Z0, None, 1.0, 12.0, 40.0, 42.0, 0))
        M.male.sort(key=lambda b: b[0])
        M.xs = [b[0] for b in M.male]
        tr1 = DN.trasa_biomu(M, U)
        self.assertGreater(tr1["podniesienia"], tr0["podniesienia"])
        self.assertGreaterEqual(DN.miary_trasy(tr1, M, U)["odstep_min"], U["trasa"]["odstep_min_st"])
        M.duze.append((x + 60, 30.0, M.Z0, None, 2.0, 60.0, 60.0, 90.0, 0))   # ściana nie do ominięcia
        with self.assertRaises(DN.BladDanych):
            DN.trasa_biomu(M, U)


# ============================================================================================== 3. automat i pamięć
class Gracz:
    """Serwer w miniaturze: pamięć „widział”, blokady, akcje automatu (jak SerwerCutscenki.wykonaj)."""

    def __init__(self, krok=LP.krok):
        self.s = LP.nowy_stan()
        self.widzial = set()
        self.kotwica = self.blokada = False
        self.zdarzenia = []
        self.krok = krok

    def tyk(self, teraz, biom=None, **w):
        w.setdefault("postac", True)
        w.setdefault("strumienie", 0)
        w.setdefault("czas", 11.2)
        w["cel"] = biom if biom is not None and biom not in self.widzial else None
        akcje = self.krok(self.s, w, teraz, STALE)
        for a in akcje:
            self.zdarzenia.append(a)
            if a in ("widzial", "poddaj"):
                self.widzial.add(self.s["biom"])
            elif a == "blokuj_walke":
                self.blokada = True
            elif a == "zakotwicz":
                self.kotwica = True
            elif a == "odblokuj":
                self.kotwica = self.blokada = False
        return akcje

    def przebieg(self, biom, t=0.0, odpowiedz="gotowe", koniec_po=11.2, pominieta=False):
        """Wejście do biomu i cała cutscenka; → (czas końca, lista akcji)."""
        od = len(self.zdarzenia)
        start = None
        for _ in range(400):
            w = {}
            if self.s["faza"] == "pyta":
                w["odpowiedz"] = odpowiedz
            if self.s["faza"] == "trwa":
                start = start if start is not None else t
                if t - start >= koniec_po:
                    w["koniec"], w["pominieta"] = True, pominieta
            self.tyk(t, biom, **w)
            t += 0.25
            if self.s["faza"] == "brak" and len(self.zdarzenia) > od and self.zdarzenia[-1] == "odblokuj":
                break
        return t, self.zdarzenia[od:]


class TestAutomat(unittest.TestCase):
    def test_3a_pierwsze_wejscie_gra_drugie_nie(self):
        g = Gracz()
        t, akcje = g.przebieg("las")
        self.assertEqual([a for a in akcje if a != "podtrzymaj"],
                         ["blokuj_walke", "pytaj", "widzial", "zakotwicz", "laduj", "start", "odblokuj"])
        self.assertEqual(g.s["wynik"], "koniec")
        self.assertIn("las", g.widzial)
        self.assertFalse(g.kotwica or g.blokada)
        for i in range(40):
            self.assertEqual(g.tyk(t + i * 0.25, "las"), [])
        self.assertEqual(g.s["id"], 1)

    def test_3b_kazdy_biom_osobno(self):
        g = Gracz()
        t, _ = g.przebieg("las")
        t, akcje = g.przebieg("bagno", t)
        self.assertIn("start", akcje)
        self.assertEqual(g.widzial, {"las", "bagno"})

    def test_3c_odmowa_niczego_nie_zapisuje_i_pyta_ponownie(self):
        g = Gracz()
        t, akcje = g.przebieg("las", odpowiedz="odmowa")
        self.assertEqual(akcje, ["blokuj_walke", "pytaj", "odblokuj"])
        self.assertEqual(g.widzial, set())
        self.assertEqual(g.tyk(t, "las"), [], "przed upływem ponowPoOdmowie serwer nie pyta")
        t2, akcje = g.przebieg("las", t + STALE["ponowPoOdmowie"])
        self.assertIn("start", akcje)
        self.assertIn("las", g.widzial)

    def test_3d_cisza_klienta_konczy_sie_poddaniem(self):
        g = Gracz()
        t = 0.0
        for _ in range(STALE["probMaks"]):
            t, akcje = g.przebieg("las", t + STALE["ponowPoCiszy"], odpowiedz=None)
            self.assertIn("przerwij", akcje)
            self.assertNotIn("zakotwicz", akcje)
        self.assertIn("poddaj", g.zdarzenia)
        self.assertIn("las", g.widzial, "po probMaks próbach bez odpowiedzi serwer przestaje pytać")
        self.assertFalse(g.blokada)

    def test_3e_pominiecie(self):
        g = Gracz()
        t, akcje = g.przebieg("las", koniec_po=2.0, pominieta=True)
        self.assertEqual(g.s["wynik"], "pominieta")
        self.assertEqual(akcje[-1], "odblokuj")
        self.assertIn("las", g.widzial)
        self.assertEqual(g.tyk(t + 1, "las"), [])

    def test_3f_smierc_postaci_i_brak_klienta(self):
        for faza_celu in ("pyta", "laduje", "trwa"):
            g = Gracz()
            t = 0.0
            while g.s["faza"] != faza_celu:
                w = {"odpowiedz": "gotowe"} if g.s["faza"] == "pyta" and faza_celu != "pyta" else {}
                if faza_celu == "laduje":
                    w["strumienie"] = 3
                g.tyk(t, "las", **w)
                t += 0.25
            akcje = g.tyk(t, "las", postac=False)
            self.assertEqual(akcje, ["przerwij", "odblokuj"], faza_celu)
            self.assertFalse(g.kotwica or g.blokada)
        g = Gracz()
        t, akcje = g.przebieg("las", koniec_po=999)
        self.assertEqual(g.s["wynik"], "czas", "klient milczy w locie → serwer kończy sam po czasie + zapas")
        self.assertEqual(akcje[-2:], ["przerwij", "odblokuj"])

    def test_3g_odtworzenie_na_zyczenie(self):
        g = Gracz()
        t, _ = g.przebieg("las")
        g.tyk(t, None, wymus="las")
        self.assertEqual(g.s["faza"], "uspokaja")
        self.assertTrue(g.s["wymuszony"])
        zd = len(g.zdarzenia)
        for i in range(1, 80):
            w = {"odpowiedz": "gotowe"} if g.s["faza"] == "pyta" else {}
            if g.s["faza"] == "trwa" and i > 20:
                w["koniec"] = True
            g.tyk(t + i * 0.25, None, **w)
        self.assertIn("start", g.zdarzenia[zd:])
        self.assertEqual(g.s["id"], 2)

    def test_3h_wyjscie_z_biomu_przed_pytaniem(self):
        g = Gracz()
        g.tyk(0.0, "las")
        self.assertEqual(g.tyk(0.6, None), [])
        self.assertEqual((g.s["faza"], g.s["wynik"]), ("brak", "wyszedl"))
        self.assertEqual(g.widzial, set())

    def test_3i_losowe_przebiegi_zawsze_odblokowuja(self):
        rnd = random.Random(77)
        for _ in range(300):
            g = Gracz()
            t = 0.0
            for _ in range(rnd.randint(5, 80)):
                w = {"postac": rnd.random() < 0.95, "strumienie": rnd.choice([0, 0, 2]), "koniec": rnd.random() < 0.08,
                     "pominieta": rnd.random() < 0.5, "odpowiedz": rnd.choice([None, None, "gotowe", "odmowa"]),
                     "przerwij": rnd.choice([None] * 12 + ["reset", "klient"]),
                     "wymus": rnd.choice([None] * 15 + ["bagno"])}
                g.tyk(t, rnd.choice(["las", "las", None, "bagno"]), **w)
                t += 0.25
                if g.s["faza"] == "brak":
                    self.assertFalse(g.kotwica or g.blokada, "po wyjściu z automatu nic nie zostaje zablokowane")
                if g.kotwica:
                    self.assertIn(g.s["faza"], ("laduje", "trwa"))

    def test_3j_pamiec_gotowa_na_zapis_i_zapis_wlaczony(self):
        zrodlo = czytaj("swiat", "stan_gracza", "dane.py")
        self.assertRegex(zrodlo, r"(?m)^ZAPIS_WLACZONY = True", "zapis postępu włączony decyzją D-110 (19.11.2026)")
        m = re.search(r'"atrybuty_prefiksy":\s*\[([^\]]*)\]', zrodlo)
        prefiksy = re.findall(r'"([^"]+)"', m.group(1))
        for b in D["biomy"]:
            self.assertTrue(any(b["atrybut"].startswith(p) for p in prefiksy),
                            "%s: zapis postępu nie objąłby atrybutu %s" % (b["id"], b["atrybut"]))
        serwer = czytaj("swiat", "cutscenka_biomu", "zrodla", "SerwerCutscenki.server.luau")
        self.assertIn("gracz:SetAttribute(b.atrybut, wartosc)", serwer)
        self.assertIn("gracz:GetAttribute(b.atrybut) == true", serwer)


# ============================================================================================== 4. Luau
def luau_modul(plik):
    it = LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    return it, it.wykonaj(czytaj("swiat", "cutscenka_biomu", "zrodla", plik), plik)[0]


def wolaj(it, modul, nazwa, *argi):
    return it.wywolaj(modul.get(nazwa), [LM.do_luau(a) if isinstance(a, (dict, list)) else
                                           (float(a) if isinstance(a, (int, float)) and not isinstance(a, bool) else a)
                                           for a in argi])


class TestLuauStatycznie(unittest.TestCase):
    def test_4a_kontrola_statyczna(self):
        bledy, _parser = SLC.sprawdz_pliki(SLC.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertEqual(bledy, [])

    def test_4b_straznik_studio_na_poczatku(self):
        for plik in os.listdir(ZR):
            self.assertTrue(SLC.SL.pierwsza_instrukcja(czytaj("swiat", "cutscenka_biomu", "zrodla", plik)).startswith(ZB.STRAZNIK), plik)

    def test_4c_przypadki_w_pythonie(self):
        ok, n, bledy = LP.sprawdz_przypadki()
        self.assertTrue(ok, bledy)
        self.assertGreaterEqual(n, 20)

    def test_4d_sprzatanie_w_kazdej_sciezce(self):
        k = czytaj("swiat", "cutscenka_biomu", "zrodla", "KlientCutscenki.client.luau")
        for powod in ("przerwane przez serwer", "postać usunięta", "kontener usunięty", "błąd w locie", "błąd przygotowania",
                      "brak startu od serwera", "nowa cutscenka"):
            self.assertIn(powod, k)
        self.assertIn('Enum.CameraType.Custom', k)
        self.assertIn("ProximityPromptService.Enabled = podpowiedzi", k)
        self.assertIn("ster:Enable()", k)
        self.assertEqual(k.count("FireClient"), 0)
        s = czytaj("swiat", "cutscenka_biomu", "zrodla", "SerwerCutscenki.server.luau")
        self.assertNotIn("FireAllClients", s, "cutscenkę dostaje tylko gracz, który wszedł")
        self.assertIn("kontener.Destroying:Connect", s)
        self.assertIn("Players.PlayerRemoving:Connect", s)


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuauWykonany(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.L = luau_modul("LogikaCutscenki.luau")

    def test_4e_przypadki_w_luau(self):
        ok, n, bledy = wolaj(self.it, self.L, "sprawdzPrzypadki")
        self.assertTrue(ok, LM.z_luau(bledy))
        self.assertEqual(int(n), len(LP.PRZYPADKI))
        self.assertEqual(LM.z_luau(wolaj(self.it, self.L, "opisyPrzypadkow")[0]), [p[0] for p in LP.PRZYPADKI])

    def test_4f_krzywa_na_prawdziwych_trasach(self):
        rnd = random.Random(5)
        for b in D["biomy"]:
            tr = b["trasa"]
            tab = LM.do_luau(tr["poz"])
            for _ in range(60):
                t = rnd.uniform(-0.5, tr["czas"] + 0.5)
                lu = self.it.wywolaj(self.L.get("krzywa"), [tab, float(tr["n"]), float(tr["krok"]), t])
                py = LP.krzywa(tr["poz"], tr["n"], tr["krok"], t)
                dn = DN.krzywa_probek(tr["poz"], tr["n"], tr["krok"], t)
                for a, c, d in zip(lu, py, dn):
                    self.assertAlmostEqual(a, c, delta=1e-9)
                    self.assertAlmostEqual(c, d, delta=1e-9)

    def test_4g_automat_taki_sam(self):
        def krok_luau(s, w, teraz, k):
            ts, tw = LM.do_luau(s), LM.Tabela()
            for kk, vv in w.items():
                if vv is not None:
                    tw.set(kk, float(vv) if isinstance(vv, (int, float)) and not isinstance(vv, bool) else vv)
            akcje = LM.z_luau(wolaj(self.it, self.L, "krok", ts, tw, teraz, k)[0])
            for kk, vv in LM.z_luau(ts).items():
                s[kk] = vv
            return [] if akcje == {} else akcje
        rnd = random.Random(11)
        for _ in range(80):
            gp, gl = Gracz(), Gracz(krok=krok_luau)
            t = 0.0
            for _ in range(rnd.randint(5, 70)):
                w = {"postac": rnd.random() < 0.95, "strumienie": rnd.choice([0, 0, 2]), "koniec": rnd.random() < 0.1,
                     "pominieta": rnd.random() < 0.5, "odpowiedz": rnd.choice([None, None, "gotowe", "odmowa"]),
                     "przerwij": rnd.choice([None] * 10 + ["reset", "klient"]), "wymus": rnd.choice([None] * 12 + ["bagno"])}
                biom = rnd.choice(["las", "las", None, "bagno"])
                a, b = gp.tyk(t, biom, **dict(w)), gl.tyk(t, biom, **dict(w))
                self.assertEqual(a, b)
                for kk in ("faza", "id", "biom", "wymuszony", "wynik", "proby"):
                    self.assertEqual(gp.s[kk], gl.s[kk], kk)
                for kk in ("od", "doKiedy", "nastepny", "wolnyOd"):
                    self.assertAlmostEqual(gp.s[kk], gl.s[kk], delta=1e-9)
                t += 0.25

    def test_4h_uklad_i_oprawa_takie_same(self):
        k = DN.uklad_stale(U)
        for w, h, lewo, prawo in [(667, 375, 0, 0), (844, 390, 47, 47), (1920, 1080, 0, 0), (1280, 720, 0, 0)]:
            lu = LM.z_luau(wolaj(self.it, self.L, "uklad", w, h, lewo, 0, prawo, 0, k)[0])
            py = LP.uklad(w, h, lewo, 0, prawo, 0, k)
            self.assertEqual(json.dumps(lu, sort_keys=True), json.dumps(json.loads(json.dumps(py)), sort_keys=True).replace(".0,", ",").replace(".0}", "}"))
        for t in (0, 0.2, 0.4, 1.0, 1.6, 1.9, 3):
            self.assertAlmostEqual(wolaj(self.it, self.L, "widocznosc", t, 0.1, 0.4, 1.5, 1.9)[0], LP.widocznosc(t, 0.1, 0.4, 1.5, 1.9))
            self.assertAlmostEqual(wolaj(self.it, self.L, "wstrzas", t, 0.2, 1.3, 0.38)[0], LP.wstrzas(t, 0.2, 1.3, 0.38))


# ============================================================================================== 5. telefon
class TestTelefon(unittest.TestCase):
    EKRANY = [tuple(e) + (0, 0) for e in U["telefon"]] + [(844, 390, 47, 47), (667, 375, 0, 20)]

    @staticmethod
    def szerokosc_napisu(tekst, rozmiar):
        return 0.52 * rozmiar * len(tekst)      # Bangers: wersaliki ok. połowy wysokości

    def test_5a_napisy_i_przycisk_czytelne(self):
        k = DN.uklad_stale(U)
        for w, h, bok, dol in self.EKRANY:
            u = LP.uklad(w, h, bok, 0, bok, dol, k)
            for nazwa in ("nazwa", "nadtytul", "podpis", "straznik"):
                r = u[nazwa]
                self.assertGreaterEqual(r["tekst"], PR["napis_min_px"], "%dx%d %s" % (w, h, nazwa))
                self.assertGreaterEqual(r["x"], bok)
                self.assertLessEqual(r["x"] + r["w"], w - bok)
                self.assertGreaterEqual(r["y"], 0)
                self.assertLessEqual(r["y"] + r["h"], h)
            p = u["pomin"]
            self.assertGreaterEqual(p["w"], PR["przycisk_min_px"])
            self.assertGreaterEqual(p["h"], PR["przycisk_min_px"])
            self.assertGreaterEqual(p["tekst"], PR["napis_min_px"])
            self.assertLessEqual(p["x"] + p["w"], w - bok - k["margines"] + 0.01)
            self.assertLessEqual(p["y"] + p["h"], h - dol - k["margines"] + 0.01)
            self.assertLessEqual(self.szerokosc_napisu(U["oprawa"]["pomijanie"]["napis"], p["tekst"]), p["w"] - 8)
            for nazwa in ("podpis", "straznik"):
                r = u[nazwa]
                self.assertLessEqual(r["x"] + r["w"], p["x"], "%dx%d: %s nie może wejść pod przycisk" % (w, h, nazwa))
            self.assertGreater(u["nazwa"]["y"], u["pas"], "nazwa biomu pod górnym pasem")
            self.assertGreater(u["nadtytul"]["y"], u["pas"] - 1)
            self.assertLess(u["nazwa"]["y"] + u["nazwa"]["h"], u["straznik"]["y"])

    def test_5b_nazwy_mieszcza_sie_na_ekranie(self):
        k = DN.uklad_stale(U)
        for w, h, bok, dol in self.EKRANY:
            u = LP.uklad(w, h, bok, 0, bok, dol, k)
            for b in D["biomy"]:
                self.assertLessEqual(self.szerokosc_napisu(b["nazwa"], u["nazwa"]["tekst"]), u["nazwa"]["w"])
                self.assertLessEqual(self.szerokosc_napisu(b["straznik"]["nazwa"], u["straznik"]["tekst"]), u["straznik"]["w"],
                                     "%dx%d %s" % (w, h, b["straznik"]["nazwa"]))
                for p in b["trasa"]["przystanki"]:
                    self.assertLessEqual(self.szerokosc_napisu(p["nazwa"], u["podpis"]["tekst"]), u["podpis"]["w"], p["nazwa"])
            self.assertLessEqual(self.szerokosc_napisu(U["oprawa"]["plansza"]["nadtytul"], u["nadtytul"]["tekst"]), u["nadtytul"]["w"])

    def test_5c_oprawa_w_czasie(self):
        O = U["oprawa"]
        for b in D["biomy"]:
            tr = b["trasa"]
            self.assertLess(O["plansza"]["do_s"], tr["przystanki"][1]["t"], "plansza znika przed drugą przegrodą")
            self.assertLess(O["pomijanie"]["od_s"], 2.0)
            self.assertGreater(tr["czas"] - tr["lot"], O["straznik"]["ryk_po_s"] + O["straznik"]["wstrzas_s"])


# ============================================================================================== 6. budowniczy i sąsiedzi
class TestBudowniczy(unittest.TestCase):
    def test_6a_sucho(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True, text=True,
                           encoding="utf-8", cwd=REPO)
        self.assertEqual(r.returncode, 0, r.stdout[-800:] + r.stderr[-800:])
        self.assertIn("sucho: OK", r.stdout)

    @unittest.skipIf(LM is None, "brak luau_mini")
    def test_6b_kod_dla_studia_parsuje_sie(self):
        for nazwa, kod in ZB.wszystkie_kody(D).items():
            LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()
            self.assertNotIn("Lighting", kod)
            self.assertNotIn("SavePlace", kod)

    def test_6c_haczyk_w_serwerze_pasa(self):
        sp = czytaj(*U["zaleznosci"]["haczyk_pasa"]["plik"].split("/"))
        H = U["zaleznosci"]["haczyk_pasa"]
        self.assertIn('"%s" .. (B.id or "las")' % H["atrybut_przejecia"], sp)
        self.assertIn('local KONTENER_CUTSCENKI = "%s"' % U["kontener"], sp)
        self.assertIn("workspace:FindFirstChild(KONTENER_CUTSCENKI)", sp)
        self.assertIn('kontener:SetAttribute("%s", true)' % H["atrybut_ustepuje"], sp)
        self.assertIn('if s.przelot.faza == "brak" and cutscenkaPrzejela() then', sp)
        self.assertIn("w.wPasie = false", sp)
        serwer = czytaj("swiat", "cutscenka_biomu", "zrodla", "SerwerCutscenki.server.luau")
        self.assertIn("kontener:SetAttribute(D.przejecie .. b.id, true)", serwer)
        for wpis, b in zip(U["biomy"], D["biomy"]):
            self.assertEqual(DN.dane_gry(wpis)["biom"]["id"], b["id"], "id biomu = to, z którego haczyk składa nazwę atrybutu")

    def test_6d_nazwy_zaleznosci_sa_w_cudzych_zrodlach(self):
        Z = U["zaleznosci"]
        self.assertIn('SetAttribute("%s", true)' % Z["chmury"]["atrybut"], czytaj(*Z["chmury"]["zrodlo"].split("/")))
        self.assertIn('"%s"' % Z["mgla"]["atrybut_przelotu"], czytaj(*Z["mgla"]["zrodlo"].split("/")))
        self.assertIn('"%s"' % Z["trening"]["atrybut_gracza"], czytaj(*Z["trening"]["zrodlo"].split("/")))
        kat = DN.tabela_luau(czytaj(*Z["dzwiek"]["zrodlo"].split("/")))
        efekt = kat["zdarzenia"][Z["dzwiek"]["zdarzenie_ryku"]]["efekt"]
        self.assertIn(efekt, kat["efekty"])
        for b in D["biomy"]:
            self.assertEqual(kat["potwory"][b["straznik"]["gatunek"]] if "potwory" in kat else Z["dzwiek"]["zdarzenie_ryku"],
                             Z["dzwiek"]["zdarzenie_ryku"])
        kp = czytaj("swiat", "las_potwory", "zrodla", "KlientPotworow.client.luau")
        for s in ('polecenie == "wymus"', 'polecenie == "klip"', 'SetAttribute("%s", true)' % Z["potwory"]["atrybut_gotowosci"]):
            self.assertIn(s, kp)
        self.assertEqual(D["blokada"], "BlokadaWalki")
        self.assertIn(D["blokada"], czytaj("swiat", "las_potwory", "zrodla", "Stale.luau"))
        self.assertIn('SetAttribute("%s"' % Z["stan_gracza"]["atrybut_zapisu"],
                      czytaj("swiat", "stan_gracza", "zrodla", "SerwerStanu.server.luau"))

    def test_6e_bez_sciezek_i_numerow(self):
        for katalog, _dirs, pliki in os.walk(PAKIET):
            if "__pycache__" in katalog:
                continue
            for plik in pliki:
                if not plik.endswith((".py", ".luau", ".json", ".md")):
                    continue
                tekst = czytaj(os.path.relpath(os.path.join(katalog, plik), REPO))
                wzor = "[A-Za-z]:.{1,2}Us" + "ers|/Us" + "ers/|App" + "Data|One" + "Drive"   # sklejone: test nie trafia w siebie
                self.assertIsNone(re.search(wzor, tekst), plik)
                self.assertIsNone(re.search(r"(?<![\d.])\d{9,}(?![\d.])", tekst), "%s: długi numer (identyfikator?)" % plik)

    def test_6g_pomoc_prob_stary_i_nowy_przelot(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pomoc_prob_test", os.path.join(PAKIET, "pomoc_prob.py"))
        PP = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(PP)

        def gra(przejety):
            def luau(kod, dm):
                if "Przejmuje_" in kod:
                    return "true" if przejety else "false"
                if 'Invoke("gracz")' in kod:
                    return json.dumps({"faza": "trwa", "zakotwiczony": True, "blokadaWalki": True, "widziane": {"bagno": True},
                                       "licznik": 3})
                if "SterowanieCutscenkiKlienta" in kod:
                    return json.dumps({"kamera": "Scriptable", "zaslona": 1, "trwa": {"lot": True, "t": 4.0},
                                       "ostatnia": {"biom": "bagno", "ok": True, "ryk": True, "czas": 11.2}})
                if "SterowaniePasaKlienta" in kod:
                    return json.dumps({"lot": True, "t": 4.0, "zaslona": True})
                return "ok"
            return luau
        stary = {"faza": "brak", "pamiec": {"widzialPrzelotBagna": False}}
        G = {"przelot": 10.17, "zatrzymanie": 7.27}
        self.assertIs(PP.scal_gracza(gra(False), "bagno", stary), stary)
        self.assertFalse(PP.dopasuj(gra(False), "bagno", G))
        self.assertEqual(PP.licznik(gra(False), "bagno", 7), 7)
        self.assertFalse(PP.odtworz(gra(False), "bagno"))
        self.assertFalse(PP.pora_na_zrzut(gra(False), "bagno", [(3.5, "a")], 0.0, 9.0), "stary przelot: zasłona zasłania — bez zrzutu")
        g = PP.scal_gracza(gra(True), "bagno", stary)
        self.assertEqual((g["faza"], g["zablokowany"], g["blokadaWalki"], g["pamiec"]["widzialPrzelotBagna"]), ("trwa", True, True, True))
        k = PP.scal_klienta(gra(True), "bagno", {"kamera": "Custom"})
        self.assertEqual((k["kamera"], k["ostatniPrzelot"]["ok"], k["ostatniPrzelot"]["ryk"]), ("Scriptable", True, True))
        self.assertTrue(PP.dopasuj(gra(True), "bagno", G))
        b = next(x for x in D["biomy"] if x["id"] == "bagno")
        self.assertEqual((G["przelot"], G["zatrzymanie"]), (b["trasa"]["czas"] - 0.5, b["trasa"]["lot"]))
        self.assertEqual(PP.licznik(gra(True), "bagno", 7), 3)
        plan = [(0.8, "za_pozno"), (3.5, "w_pore"), (5.0, "za_wczesnie")]     # lot u klienta: t = 4,0 s
        self.assertTrue(PP.pora_na_zrzut(gra(True), "bagno", plan, None, 0.0))
        self.assertEqual([n for _, n in plan], ["w_pore", "za_wczesnie"], "kadr spóźniony o ponad okno wypada z planu")
        plan.pop(0)
        self.assertFalse(PP.pora_na_zrzut(gra(True), "bagno", plan, None, 0.0))
        self.assertFalse(PP.pora_na_zrzut(gra(True), "bagno", [], None, 0.0))

    def test_6f_podglady_tras(self):
        for b in D["biomy"]:
            sciezka = os.path.join(PAKIET, "podglady", "trasa_%s.jpg" % b["id"])
            self.assertTrue(os.path.isfile(sciezka), "brak podglądu — uruchom podglad.py")
            self.assertGreater(os.path.getsize(sciezka), 20000)


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
