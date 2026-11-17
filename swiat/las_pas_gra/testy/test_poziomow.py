# -*- coding: utf-8 -*-
"""Poziomy w scalonych zagrodach krótkiego pasa (D-096). Bez Studio, ok. 2 s.

    python -B swiat/las_pas_gra/testy/test_poziomow.py        (unittest; kod 1 przy błędzie)
    python -B swiat/las_pas_gra/testy/test_poziomow.py --rozklad   # tylko tabela: poziomy w zagrodach przy 1/8/20 graczach

Po scaleniu trzech kojców w jeden w zagrodzie chodzą potwory kilku poziomów (las s1: 1–3). Losowy poziom dawał nowemu
graczowi pierwszą walkę jak rzut monetą. Teraz (SerwerPotworow, poziomNaMiejsce) poziomy są rozdane po miejscach:
lo, lo+1, …, hi, lo, … — najniższy zawsze pierwszy, odrodzenie uzupełnia brakujący najniższy; wskazówka „Podejdź do
potwora” (swiat/wskazowki_gry, KlientWskazowek) wskazuje potwora o poziomie najbliższym poziomowi gracza.
Funkcja serwera jest wykonywana w luau_mini (ten sam kod, który idzie do Studio).
"""
import importlib.util
import os
import random
import re
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.dont_write_bytecode = True
for _s in (PAKIET, os.path.join(REPO, "swiat", "bagno_pas_gra")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import sprawdz_luau_pasa  # noqa: E402


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


GEN = _modul("generuj_dane_pasa_poziomy", os.path.join(PAKIET, "generuj_dane.py"))
GEN_B = _modul("generuj_dane_bagna_poziomy", os.path.join(REPO, "swiat", "bagno_pas_gra", "generuj_dane.py"))
LG = _modul("logika_potworow_poziomy", os.path.join(REPO, "swiat", "las_potwory", "logika.py"))
_, DP, _ = GEN.wszystko()
_, DP_B, _ = GEN_B.wszystko()
SERWER = czytaj(REPO, "swiat", "las_potwory", "zrodla", "SerwerPotworow.server.luau")
KLIENT_WSK = czytaj(REPO, "swiat", "wskazowki_gry", "zrodla", "KlientWskazowek.client.luau")
LM = sprawdz_luau_pasa.luau_mini()
FUNKCJA = re.search(r"local function poziomNaMiejsce\(.*?\nend\n", SERWER, re.S).group(0)


def poziom_serwera(lo, hi, maks, zywe):
    """poziomNaMiejsce z SerwerPotworow wykonane w luau_mini."""
    kod = FUNKCJA + "return poziomNaMiejsce(%d, %d, %d, { %s })" % (lo, hi, maks, ", ".join(str(z) for z in zywe))
    return LM.z_luau(LM.Interpreter().wykonaj(kod, "poziomNaMiejsce")[0])


def napelnij(st, G):
    """Strefa po starcie przy G graczach: tyle potworów, ile cel, każdy z poziomem od serwera."""
    lo, hi = st["poziomy"]
    zywe = []
    for _ in range(LG.cel(st["naraz"], st["max"], G)):
        zywe.append(poziom_serwera(lo, hi, st["max"], zywe))
    return zywe


def scalone():
    return [s for s in DP["strefy"] + DP_B["strefy"] if s.get("poziomyPoMiejscach")]


class TestPoziomowPoMiejscach(unittest.TestCase):
    def test_1_flaga_w_danych(self):
        las = {s["id"]: s.get("poziomyPoMiejscach") for s in DP["strefy"]}
        bagno = {s["id"]: s.get("poziomyPoMiejscach") for s in DP_B["strefy"]}
        self.assertEqual({k for k, v in las.items() if v}, {"s1", "m1", "w1"})
        self.assertEqual({k for k, v in bagno.items() if v}, {"r1", "b1", "k1"})
        self.assertIn("poziomNowego(st)", SERWER)
        self.assertIn("if not st.d.poziomyPoMiejscach or hi <= lo then", SERWER)   # stary las i t1: jak dotąd

    def test_2_pierwsza_zagroda_lasu(self):
        s1 = next(s for s in DP["strefy"] if s["id"] == "s1")
        self.assertEqual(s1["poziomy"], [1, 3])
        self.assertEqual(napelnij(s1, 1), [1, 2])
        self.assertEqual(napelnij(s1, 8), [1, 2, 3])
        self.assertEqual(sorted(napelnij(s1, 20)), [1, 1, 2, 3])

    def test_3_zawsze_najnizszy_po_odrodzeniu(self):
        """Losowe wygrane gracza (z przewagą najsłabszych): po każdym odrodzeniu w strefie chodzi najniższy poziom,
        a liczba potworów każdego poziomu nie przekracza miejsc."""
        rnd = random.Random(96)
        for st in scalone():
            lo, hi = st["poziomy"]
            for G in (1, 8, 20):
                zywe = napelnij(st, G)
                cel = len(zywe)
                for _ in range(25):
                    i = min(range(len(zywe)), key=lambda k: (zywe[k], rnd.random())) if rnd.random() < 0.7 \
                        else rnd.randrange(len(zywe))
                    zywe.pop(i)
                    zywe.append(poziom_serwera(lo, hi, st["max"], zywe))
                    with self.subTest(strefa=st["id"], G=G):
                        self.assertEqual(len(zywe), cel)
                        self.assertIn(lo, zywe)
                        miejsca = [lo + k % (hi - lo + 1) for k in range(st["max"])]
                        for poz in set(zywe):
                            self.assertLessEqual(zywe.count(poz), miejsca.count(poz))

    def test_4_wskazowka_wybiera_poziom_gracza(self):
        f = re.search(r"local function najblizszyPotwor\(od\).*?\nend\n", KLIENT_WSK, re.S).group(0)
        self.assertIn('gracz:GetAttribute("Level")', f)
        self.assertIn('c:GetAttribute("Poziom")', f)
        self.assertIn("(r < roznica or (r == roznica and d < odl))", f)
        self.assertIn("d < D.czasy.potwor_promien", f)


def rozklad():
    print("Poziomy w scalonych zagrodach (poziomNaMiejsce z SerwerPotworow, luau_mini): przy 1 / 8 / 20 graczach")
    for st in scalone():
        print("  %-3s %-16s poz. %d–%d, max %d:  %s" % (
            st["id"], st["gatunek"], st["poziomy"][0], st["poziomy"][1], st["max"],
            "   ".join("G%d %s" % (G, sorted(napelnij(st, G))) for G in (1, 8, 20))))


if __name__ == "__main__":
    if "--rozklad" in sys.argv:
        rozklad()
        sys.exit(0)
    unittest.main(verbosity=2)
