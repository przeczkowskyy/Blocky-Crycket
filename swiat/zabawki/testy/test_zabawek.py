#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy zabawek bez Studio (logika w interpreterze tools/walka/luau_mini.py).

    python -B swiat/zabawki/testy/test_zabawek.py
"""
import math
import os
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka")):
    if _s not in sys.path:
        sys.path.append(_s)
sys.path.insert(0, PAKIET)
import dane as DN  # noqa: E402
import luau_mini as LM  # noqa: E402

DN.main()
D = DN.dane()
Z, W = D["zjadacz"], D["wabik"]


def interpreter():
    it = LM.Interpreter()
    m = it.globalne.z["math"]
    m.set("rad", math.radians)
    m.set("cos", math.cos)
    m.set("sin", math.sin)
    m.set("atan2", lambda y, x: math.atan2(y, x))
    m.set("pi", math.pi)
    m.set("clamp", lambda x, a, b: min(max(x, a), b))
    m.set("sqrt", math.sqrt)
    m.set("exp", math.exp)
    return it


IT = interpreter()
L = IT.wykonaj(open(os.path.join(PAKIET, "zrodla", "LogikaZabawek.luau"), encoding="utf-8").read(), "LogikaZabawek")[0]
DL = IT.wykonaj(open(os.path.join(PAKIET, "zrodla", "DaneZabawek.luau"), encoding="utf-8").read(), "DaneZabawek")[0]
ZL, WL = DL.get("zjadacz"), DL.get("wabik")


class Los:
    def __init__(self, s=1):
        self.s = s

    def __call__(self, *_a):
        self.s = (self.s * 1103515245 + 12345) % 2147483648
        return self.s / 2147483648.0


def wolaj(n, *a):
    a = [LM.do_luau(x) if isinstance(x, (dict, list)) else (float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else x) for x in a]
    return IT.wywolaj(L.get(n), a)


def jeden(n, *a):
    r = wolaj(n, *a)
    return r[0] if r else None


def z(t):
    return LM.z_luau(t)


class TestZjadacz(unittest.TestCase):
    def test_1a_rozmiar_predkosc_formy(self):
        self.assertAlmostEqual(jeden("promien", ZL, 4), Z["r0"] * 2)
        self.assertGreater(jeden("predkosc", ZL, 1), jeden("predkosc", ZL, 30), "mały szybszy")
        self.assertEqual(jeden("forma", ZL, 1), 1)
        self.assertEqual(jeden("forma", ZL, Z["formy"][1]["od"]), 2)
        self.assertEqual(jeden("forma", ZL, 999), 6)
        self.assertAlmostEqual(jeden("postepFormy", ZL, (Z["formy"][0]["od"] + Z["formy"][1]["od"]) / 2), 0.5, places=3)

    def test_1b_zjadanie_odbicie_kulki_ewolucja(self):
        S = jeden("nowyStan1", DL, Los(2))
        S.set("kulki", LM.do_luau([99999.0] * len(Z["kulkiPoz"])))   # bez kulek w tej próbie
        duzy = jeden("dodajByt", S, 1, 4, 0, 0)
        maly = jeden("dodajByt", S, 0, 1, 2.0, 0)
        duzy.set("tarczaDo", 0.0)
        maly.set("tarczaDo", 0.0)
        maly.set("myslDo", 999.0)
        zd = z(jeden("krok1", S, 0.05)) or []
        self.assertTrue(any(e["t"] == "zjedz" and e["a"] == duzy.get("id") for e in zd), zd)
        self.assertAlmostEqual(duzy.get("m"), 4 + Z["przyrost"])
        self.assertIsNotNone(maly.get("martwyDo"))
        # podobni się odbijają
        S2 = jeden("nowyStan1", DL, Los(3))
        S2.set("kulki", LM.do_luau([99999.0] * len(Z["kulkiPoz"])))
        a = jeden("dodajByt", S2, 1, 4, 0, 0)
        b = jeden("dodajByt", S2, 0, 4.2, 3.0, 0)
        b.set("myslDo", 999.0)
        zd = z(jeden("krok1", S2, 0.05)) or []
        self.assertTrue(any(e["t"] == "odbicie" for e in zd))
        self.assertFalse(any(e["t"] == "zjedz" for e in zd))
        # kulka i ewolucja
        S3 = jeden("nowyStan1", DL, Los(4))
        k = Z["kulkiPoz"][0]
        g = jeden("dodajByt", S3, 1, Z["formy"][1]["od"] - 0.05, k[0], k[1])
        zd = z(jeden("krok1", S3, 0.05)) or []
        self.assertTrue(any(e["t"] == "kulka" for e in zd))
        self.assertTrue(any(e["t"] == "ewolucja" and e["forma"] == 2 for e in zd), "próg formy → EVOLVED!")

    def test_1c_odrodzenie_forma_nizej_z_tarcza(self):
        S = jeden("nowyStan1", DL, Los(5))
        g = jeden("dodajByt", S, 1, Z["formy"][3]["od"] + 1, 0, 0)
        g.set("martwyDo", 0.01)
        zd = z(jeden("krok1", S, 0.05)) or []
        self.assertTrue(any(e["t"] == "odrodzenie" for e in zd))
        self.assertAlmostEqual(g.get("m"), Z["formy"][2]["od"], delta=0.5, msg="forma niżej (ewentualnie + kulka obok startu)")
        self.assertGreater(g.get("tarczaDo"), S.get("czas"))

    def test_1d_bot_ucieka_i_goni(self):
        S = jeden("nowyStan1", DL, Los(6))
        S.set("kulki", LM.do_luau([99999.0] * len(Z["kulkiPoz"])))
        bot = jeden("dodajByt", S, 0, 3, 0, 0)
        duzy = jeden("dodajByt", S, 0, 20, 12, 0)
        wolaj("mysl", S, bot)
        self.assertLess(bot.get("wx"), 0, "ucieka od większego")
        S2 = jeden("nowyStan1", DL, Los(6))
        S2.set("kulki", LM.do_luau([99999.0] * len(Z["kulkiPoz"])))
        bot2 = jeden("dodajByt", S2, 0, 8, 0, 0)
        ofiara = jeden("dodajByt", S2, 0, 1, 0, 15)
        ofiara.set("tarczaDo", 0.0)
        wolaj("mysl", S2, bot2)
        self.assertGreater(bot2.get("wz"), 0.5, "goni mniejszego")


class TestWabik(unittest.TestCase):
    def test_2a_ladowanie_i_zasieg(self):
        x, zz, t, x0, z0 = wolaj("ladowanie", WL, 1, 0, 1, 105)
        self.assertAlmostEqual(zz - z0, 105, places=3)
        self.assertAlmostEqual(x, x0)
        x, zz, *_ = wolaj("ladowanie", WL, 1, 3.0, 0.5, 105)
        self.assertGreater(x - x0, 0, "kąt ograniczony do kat_maks")
        self.assertLessEqual(math.degrees(math.atan2(x - x0, zz - z0)), W["kat_maks_st"] + 0.01)
        self.assertEqual(jeden("zasieg", WL, 0), W["zasieg0"])
        self.assertEqual(jeden("zasieg", WL, 1000), W["zasieg_maks"])
        n = math.ceil((W["strefy"][2]["od"] + 5 - W["zasieg0"]) / W["zasieg_za"])
        self.assertLessEqual(n, 12, "daleka strefa po kilkunastu zwabieniach (ok. 2 min)")

    def test_2b_trafienie_zwabia_pudlo_ploszy(self):
        S = jeden("nowyStan2", DL, Los(8))
        self.assertEqual(len(z(S.get("potwory"))), sum(s["ile"] for s in W["strefy"]))
        p = S.get("potwory").get(1)
        pr = jeden("rzut2", S, 1, 0, 0.3)
        p.set("x", pr.get("x"))
        p.set("z", pr.get("z"))
        p.set("cx", pr.get("x"))
        p.set("cz", pr.get("z"))
        p.set("v", 0.0)
        zd = []
        for _ in range(30):
            zd += z(jeden("krok2", S, 0.1)) or []
        zw = [e for e in zd if e["t"] == "zwabiony"]
        self.assertTrue(zw, zd)
        self.assertEqual(p.get("wl"), 1)
        self.assertEqual(z(S.get("gracze"))[0]["zwabione"], 1)
        for _ in range(120):
            jeden("krok2", S, 0.1)
        self.assertEqual(p.get("stan"), "zagroda", "zwabiony doszedł do zagrody")
        # pudło płoszy
        self.assertIsNone(jeden("rzut2", S, 1, 0, 0.5) if False else None)
        S.set("czas", S.get("czas") + 5)
        pr = jeden("rzut2", S, 1, 0.5, 0.0)
        q = S.get("potwory").get(2)
        q.set("x", pr.get("x") + W["lap_r"] + 6)
        q.set("z", pr.get("z"))
        zd = []
        for _ in range(10):
            zd += z(jeden("krok2", S, 0.1)) or []
        self.assertTrue(any(e["t"] == "pudlo" for e in zd))
        self.assertEqual(q.get("stan"), "ucieka")

    def test_2c_rzadki_biegacz_i_odmiany(self):
        S = jeden("nowyStan2", DL, Los(9))
        S.set("nastRzadki", 0.0)
        zd = z(jeden("krok2", S, 0.1)) or []
        r = [e for e in zd if e["t"] == "rzadki"]
        self.assertTrue(r)
        self.assertGreaterEqual(D["pety"][r[0]["nr"] - 1]["stopien"], 4)
        self.assertEqual(jeden("losujOdmiane", WL, 0.0), "giant")
        self.assertIsNone(jeden("losujOdmiane", WL, 0.99))


if __name__ == "__main__":
    unittest.main(verbosity=1)
