# -*- coding: utf-8 -*-
"""Testy kalkulatora balansu 17.11 (tools/walka/progresja.py) — szybkie, bez duzych symulacji.

    python -B -m unittest tools/walka/test_progresja.py -v

Pilnuja: odczytu drzewek z src/shared/SkillTreeData.luau (wzor ceny), zgodnosci krzywej tempa z tempo.py, wlasnosci
proponowanego wzoru treningu (malejacy zysk, jedna mini-gra nigdy nie daje wiecej punktow niz szesc), wariantow zasad
z pytania 40 (jedna szansa unik/blok, nizszy limit uniku — i ze po wyjsciu silnik jest jak przedtem), potworow
biomu (mnoznik ciosu i zycia) i rachunkow geometrycznych (Shard Ewolucji).
"""
import os
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TU)
import progresja as P  # noqa: E402
import silnik  # noqa: E402
import tempo  # noqa: E402
import wzorcowe  # noqa: E402

_T = None


def T():
    global _T
    if _T is None:
        _T = P.Tempo()
    return _T


class TestDrzewka(unittest.TestCase):
    def test_trzy_zakladki_i_wzor_ceny(self):
        wezly = P.wezly_drzewka()
        zakl = {w["zakladka"] for w in wezly}
        self.assertEqual(zakl, {"Player", "Fortress", "Pets"})
        for w in wezly:
            if w["nazwa"] == "ROOT":
                self.assertEqual(w["glebokosc"], 0)
                continue
            self.assertGreaterEqual(w["glebokosc"], 1)
            self.assertLessEqual(w["glebokosc"], 5)
            # SkillTreeData.cost: (10 + 5 * glebokosc) * kolejny poziom
            self.assertEqual(w["koszt"], [(10 + 5 * w["glebokosc"]) * n for n in range(1, w["max"] + 1)])
        kz = P.koszty_zakladek(wezly)
        self.assertEqual(sum(kz.values()), sum(sum(w["koszt"]) for w in wezly))
        # jeden korzen na zakladke
        self.assertEqual(sum(1 for w in wezly if w["nazwa"] == "ROOT"), 3)

    def test_koszt_slotow(self):
        # trzy sloty umiejetnosci w galezi Skills; koszt rosnie, pierwszy = korzen + SKILL SLOT I na 1. poziomie
        wezly = P.wezly_drzewka()
        ks = P.koszt_slotow(wezly)
        self.assertEqual(len(ks), 3)
        self.assertTrue(ks[0] < ks[1] < ks[2])
        root = next(w["koszt"][0] for w in wezly if w["zakladka"] == "Player" and w["nazwa"] == "ROOT")
        slot1 = next(w for w in wezly if w["zakladka"] == "Player" and w["stat"] == "SkillSlots")
        self.assertEqual(ks[0], root + slot1["koszt"][0])

    def test_kupione_za(self):
        wezly = P.wezly_drzewka()
        self.assertEqual(P.kupione_za(wezly, "Player", 0), 0.0)
        self.assertAlmostEqual(P.kupione_za(wezly, "Player", 10 ** 9), 100.0)
        a, b = P.kupione_za(wezly, "Player", 500), P.kupione_za(wezly, "Player", 2000)
        self.assertLess(a, b)


class TestTempo(unittest.TestCase):
    def test_zgodne_z_modelem_biomow(self):
        # ta sama krzywa co tempo.model_biomow: na koncu planu rosnacego 600 min ten sam poziom
        import argparse
        a = argparse.Namespace(xp_a=tempo.DOMYSLNE_A, xp_b=1.6, tempo_odtwarzania=1.0, odrodzenie_s=15.0)
        _, L8 = tempo.model_biomow(a, tempo.PLAN_ROSNACY)
        self.assertEqual(int(T().poziom(600)), L8)
        gr = P.granice(T(), "rosnący")
        self.assertEqual(len(gr), 8)
        self.assertEqual(gr[0]["L_od"], 1)
        self.assertEqual(gr[6]["L_do"], L8)

    def test_trening_obniza_poziom(self):
        g0 = P.granice(T(), "rosnący")
        g2 = P.granice(T(), "rosnący", 0.2)
        self.assertTrue(all(b["L_do"] <= a["L_do"] for a, b in zip(g0, g2)))


class TestTrening(unittest.TestCase):
    def test_malejacy_zysk(self):
        tr = P.Trening()
        L = 30
        H = tr.h * wzorcowe.pula(L)
        self.assertAlmostEqual(tr.mnoznik(0, L), 1.0)
        self.assertAlmostEqual(tr.mnoznik(H, L), 0.25)  # (1 + 1)^-2
        self.assertGreater(tr.mnoznik(5, L), tr.mnoznik(50, L))
        self.assertEqual(P.Trening(wykladnik=0).mnoznik(10 ** 6, L), 1.0)
        # awans przywraca tempo: te same punkty w statystyce przy wyzszym poziomie licza sie mniej
        self.assertGreater(tr.mnoznik(40, 50), tr.mnoznik(40, 20))

    def test_jedna_mini_gra_nie_wygrywa_punktami(self):
        tr = P.Trening()
        t = [600.0]
        for k in wzorcowe.KLASY:
            rowno = sum(P.przebieg_treningu(T(), tr, k, "rosnący", 0.2, "rowno", t)[600.0][1].values())
            for s in wzorcowe.STATYSTYKI:
                jedna = sum(P.przebieg_treningu(T(), tr, k, "rosnący", 0.2, "jedna:" + s, t)[600.0][1].values())
                self.assertLess(jedna, 0.6 * rowno, (k, s))

    def test_bez_malejacego_wszystko_jedno(self):
        tr0 = P.Trening(wykladnik=0)
        t = [345.0]
        sumy = {sum(P.przebieg_treningu(T(), tr0, "mag", "rosnący", 0.2, pol, t)[345.0][1].values())
                for pol in ("rowno", "klasa", "jedna:kondycja")}
        self.assertEqual(len({round(x, 6) for x in sumy}), 1)

    def test_gracz_oczekiwany_w_przedziale(self):
        # zalozenie strojenia: gracz trenujacy 20% czasu ma pod koniec 7. biomu 30-60% puli z treningu
        tr = P.Trening()
        L, W = P.przebieg_treningu(T(), tr, "wojownik", "rosnący", 0.2, "klasa", [600.0])[600.0]
        udzial = sum(W.values()) / wzorcowe.pula(int(L))
        self.assertGreater(udzial, 0.30)
        self.assertLess(udzial, 0.60)


class TestWarianty(unittest.TestCase):
    def test_jedna_szansa_max_unik_blok(self):
        # Wojownik z tarcza: w wariancie (c) ciosy potwora omija (unik) albo blokuje najwyzej max(unik, blok) razy
        g = wzorcowe.postac("wojownik", 10, dodatkowe={"zrecznosc": 60})
        v = silnik.wartosci_postaci(g)
        u, b = v["unik"], v["blok"]
        licz = {"unik": 0, "blok": 0, "inne": 0}
        with P.wariant_silnika("jedna_szansa"):
            for z in range(1, 401):
                w = silnik.symuluj(g, {"potwor": "lesny_troll", "poziom": 10}, z)
                for e in w["dziennik"]:
                    if e["kto"] == "wrog" and e["cel"] == "gracz" and e["typ"] in ("cios", "krytyk", "blok", "unik") \
                            and not e["umiejetnosc"]:
                        licz[e["typ"] if e["typ"] in ("unik", "blok") else "inne"] += 1
        n = sum(licz.values())
        self.assertAlmostEqual(licz["unik"] / n, u, delta=0.03)
        self.assertAlmostEqual(licz["blok"] / n, max(0, b - u), delta=0.03)
        # po wyjsciu silnik jest jak przedtem
        self.assertEqual(silnik.zwykly_cios.__name__, "zwykly_cios")
        self.assertEqual(silnik.uzyj_umiejetnosci.__name__, "uzyj_umiejetnosci")

    def test_wariant_powtarzalny_i_bez_wycieku(self):
        g = wzorcowe.postac("wojownik", 5)
        przed = silnik.symuluj(g, {"potwor": "cierniowy_wilk", "poziom": 5}, 7)
        with P.wariant_silnika("jedna_szansa"):
            a = silnik.symuluj(g, {"potwor": "cierniowy_wilk", "poziom": 5}, 7)
            b = silnik.symuluj(g, {"potwor": "cierniowy_wilk", "poziom": 5}, 7)
        self.assertEqual(a["dziennik"], b["dziennik"])
        with P.wariant_silnika("limit_uniku_15"):
            self.assertEqual(silnik.KLASY["wojownik"]["unik_limit"], 0.15)
        self.assertNotEqual(silnik.KLASY["wojownik"]["unik_limit"], 0.15)
        po = silnik.symuluj(g, {"potwor": "cierniowy_wilk", "poziom": 5}, 7)
        self.assertEqual(przed["dziennik"], po["dziennik"])


class TestPotworBiomu(unittest.TestCase):
    def test_mnoznik_ciosu_i_zycia(self):
        for p in ("lesny_slime", "lesny_troll", "straznik_lasu"):
            for L in (5, 40):
                baza = silnik.wartosci_potwora(p, L)
                jeden = silnik.wartosci_potwora(P.potwor_biomu(p, 1.0)[0], L)
                self.assertAlmostEqual(jeden["cios"], baza["cios"], delta=1e-9)
                self.assertEqual(jeden["zycie"], baza["zycie"])
                pol = silnik.wartosci_potwora(P.potwor_biomu(p, 1.5)[0], L)
                self.assertAlmostEqual(pol["cios"] / baza["cios"], 1.5, delta=0.03)
                self.assertAlmostEqual(pol["zycie"] / baza["zycie"], 1.5, delta=0.01)
                self.assertEqual(pol["pancerz"], baza["pancerz"])

    def test_granica_modyfikatora(self):
        with self.assertRaises(ValueError):
            P.potwor_biomu("straznik_lasu", 3.0)


class TestRachunki(unittest.TestCase):
    def test_geometryczny(self):
        sr, med, p90 = P.geometryczny(0.1)
        self.assertAlmostEqual(sr, 10.0)
        self.assertEqual(med, 7)
        self.assertEqual(p90, 22)

    def test_gemy_dzis_prawie_zero(self):
        # dzisiejsze szanse z dane_walki.json: w 10 godzin gry mniej niz koszt korzenia jednej zakladki z zapasem
        out = P.gemy_w_czasie(T(), "rosnący", P.zrodla_gemow("dzis"))
        self.assertLess(out[6]["gemy"], 20)
        milowe = P.gemy_w_czasie(T(), "rosnący", P.zrodla_gemow("łup ×5 + kamienie milowe"))
        self.assertGreater(milowe[6]["gemy"], 1000)
        self.assertTrue(all(a["gemy"] <= b["gemy"] for a, b in zip(milowe, milowe[1:])))


if __name__ == "__main__":
    unittest.main()
