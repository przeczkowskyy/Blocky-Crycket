#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy logiki Monster Evolution bez Studio (zrodla/LogikaEwolucji.luau w interpreterze tools/walka/luau_mini.py).

    python -B swiat/ewolucja/testy/test_ewolucji.py
"""
import functools
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


def interpreter():
    it = LM.Interpreter()
    m = it.globalne.z["math"]
    for n, f in (("rad", math.radians), ("cos", math.cos), ("sin", math.sin), ("sqrt", math.sqrt), ("exp", math.exp)):
        m.set(n, f)
    m.set("atan2", lambda y, x: math.atan2(y, x))
    m.set("pi", math.pi)
    m.set("clamp", lambda x, a, b: min(max(x, a), b))
    t = it.globalne.z["table"]

    def tsort(tab, cmp=None):
        n = int(tab.dlugosc())
        el = [tab.d[float(i)] for i in range(1, n + 1)]

        def k(a, b):
            if cmp is None:
                return -1 if a < b else (1 if b < a else 0)
            if it.wywolaj(cmp, [a, b])[0]:
                return -1
            return 1 if it.wywolaj(cmp, [b, a])[0] else 0
        el.sort(key=functools.cmp_to_key(k))
        for i, v in enumerate(el):
            tab.d[float(i + 1)] = v
    t.set("sort", tsort)
    return it


IT = interpreter()
L = IT.wykonaj(open(os.path.join(PAKIET, "zrodla", "LogikaEwolucji.luau"), encoding="utf-8").read(), "LogikaEwolucji")[0]
DL = IT.wykonaj(open(os.path.join(PAKIET, "zrodla", "DaneEwolucji.luau"), encoding="utf-8").read(), "DaneEwolucji")[0]


class Los:
    def __init__(self, s=1):
        self.s = s

    def __call__(self, *_a):
        self.s = (self.s * 1103515245 + 12345) % 2147483648
        return self.s / 2147483648.0


def lu(x):
    if isinstance(x, (dict, list)):
        return LM.do_luau(x)
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return float(x)
    return x


def wolaj(n, *a):
    return IT.wywolaj(L.get(n), [lu(x) for x in a])


def jeden(n, *a):
    r = wolaj(n, *a)
    return r[0] if r else None


def stan(dane=None, ziarno=3):
    return jeden("nowyStan", dane or DL, Los(ziarno))


def byt(S, slot, forma, x=None, z=None):
    if x is None:
        return jeden("dodajByt", S, slot, forma)
    return jeden("dodajByt", S, slot, forma, x, z)


def krok(S, n=1, dt=0.05):
    zd = []
    for _ in range(n):
        zd += LM.z_luau(jeden("krok", S, dt), True)
    return zd


def ustaw(b, **kw):
    for k, v in kw.items():
        b.set(k, lu(v))


def g(b, k):
    return LM.z_luau(b.get(k))


def bez_kulek(S):
    """Wszystkie kulki „zjedzone” na długo (testy bez przypadkowego zbierania)."""
    k = S.get("kulki")
    for i in range(1, int(k.dlugosc()) + 1):
        k.set(float(i), 1e9)


def daleko(S, b, x=0, z=0):
    ustaw(b, x=x, z=z, tarczaDo=0)


class TestLiczby(unittest.TestCase):
    def test_01_formy_stawka_ceny(self):
        self.assertEqual(jeden("promien", DL, 1), D["formy"][0]["r"])
        self.assertEqual(jeden("potrzeba", DL, 2), D["formy"][1]["potrzeba"])
        tro = [f["trofeum"] for f in D["formy"]]
        self.assertEqual(tro, [1, 2, 4, 7, 12, 20, 35, 60], "trofea z projektu")
        self.assertEqual(jeden("stawka", DL, 1), 1)
        self.assertEqual(jeden("stawka", DL, 3), 7)
        self.assertEqual(jeden("stawka", DL, 8), sum(tro))
        self.assertEqual([f["r"] for f in D["formy"]], sorted(f["r"] for f in D["formy"]), "drabina rośnie")
        self.assertGreater(D["formy"][-1]["r"], 1.5 * D["formy"][-2]["r"], "Olbrzym wyraźnie ogromny")
        U = {u["id"]: u for u in D["ulepszenia"]}
        self.assertEqual(U["szybkosc"]["wartosci"][:3], [16, 19, 22])
        self.assertEqual(U["apetyt"]["wartosci"][:3], [1, 1.25, 1.5])
        self.assertTrue(all(len(u["ceny"]) == 4 for u in D["ulepszenia"]), "po pięć poziomów (start + 4 zakupy)")
        self.assertTrue(all(u["ceny"][3] > 2 * u["ceny"][1] for u in D["ulepszenia"]), "poziomy 4 i 5 wyraźnie drożej")

    def test_02_zasady_jedzenia(self):
        S = stan()
        g1, g2, g3 = byt(S, 1, 1, 0, 0), byt(S, 2, 2, 10, 0), byt(S, 3, 3, 20, 0)
        b2, b4 = byt(S, 0, 2, 30, 0), byt(S, 0, 4, 40, 0)
        mz = lambda a, b: jeden("mozeZjesc", DL, a, b)  # noqa: E731
        self.assertTrue(mz(b2, g1), "bot formy 2 zjada gracza formy 1 (zagrażają mu boty)")
        self.assertFalse(mz(g3, g2), "gracz formy 2 chroniony przed graczami")
        self.assertFalse(mz(g3, g1), "gracz formy 1 chroniony przed graczami")
        self.assertTrue(mz(b4, g3), "bot o formę większy zjada gracza formy 3")
        self.assertFalse(mz(g2, b2), "ta sama forma się nie zjada")
        self.assertTrue(mz(g3, b2), "o jedną formę większy zjada")
        ustaw(g2, forma=4)
        self.assertTrue(mz(g2, g3), "gracz formy 4 zjada gracza formy 3")


class TestPetla(unittest.TestCase):
    def test_03_kulka_i_wzrost(self):
        S = stan()
        k0 = len(D["kulkiPoz"])
        p = D["kulkiPoz"][-1]
        gr = byt(S, 1, 1, p[0] + 1.0, p[1])
        zd = krok(S)
        kul = [z for z in zd if z["t"] == "kulka" and z["id"] == g(gr, "id")]
        self.assertTrue(kul, "kulka zjedzona dotykiem")
        self.assertGreaterEqual(g(gr, "wzrost"), D["jedzenie"]["duza"] if p[2] == 2 else D["jedzenie"]["mala"])
        self.assertGreater(g(S.get("kulki"), k0), 0, "kulka czeka na powrót")
        krok(S, int(D["jedzenie"]["powrot_duza_s"] / 0.5) + 2, 0.5)
        ustaw(gr, x=0, z=0)

    def test_04_gryz_i_przerwa(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, tarczaDo=0)
        ofiara = byt(S, 0, 2, D["formy"][2]["r"] + 2.5, 0)
        ustaw(ofiara, myslDo=99)
        zd = LM.z_luau(LM.Tabela(), True)
        lista = LM.Tabela()
        self.assertTrue(jeden("gryz", S, gr, lista))
        zd = LM.z_luau(lista, True)
        zj = [z for z in zd if z["t"] == "zjedz"]
        self.assertTrue(zj and zj[0]["b"] == g(ofiara, "id"), "BITE zjada mniejszego w zasięgu Szczęki")
        self.assertIsNotNone(g(ofiara, "martwyDo"))
        self.assertEqual(g(gr, "wzrost"), D["jedzenie"]["za_forme"][1])
        self.assertFalse(jeden("gryz", S, gr, LM.Tabela()), "przerwa między ugryzieniami")
        # bot wraca po odrodzenie_s w tej samej formie
        krok(S, int(D["boty"]["odrodzenie_s"] / 0.1) + 2, 0.1)
        self.assertIsNone(g(ofiara, "martwyDo"))
        self.assertEqual(g(ofiara, "forma"), 2)

    def test_05_ewolucja_kokon_trofeum(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 1, 0, 0)
        lista = LM.Tabela()
        self.assertFalse(jeden("ewoluuj", S, gr, lista), "pasek niepełny")
        ustaw(gr, wzrost=D["formy"][0]["potrzeba"] + 5)
        self.assertTrue(jeden("ewoluuj", S, gr, lista))
        self.assertIsNotNone(g(gr, "kokonDo"))
        self.assertFalse(jeden("pozycjaKlienta", S, gr, 1, 1), "w kokonie serwer prowadzi")
        zd = krok(S, int(D["ewolucja"]["kokon_s"] / 0.1) + 1, 0.1)
        ew = [z for z in zd if z["t"] == "ewolucja"]
        self.assertTrue(ew and ew[0]["nowa"] and ew[0]["forma"] == 2)
        self.assertEqual((g(gr, "forma"), g(gr, "maxForma")), (2, 2))
        self.assertAlmostEqual(g(gr, "wzrost"), 5, places=6, msg="nadmiar przechodzi")
        self.assertEqual(jeden("stawka", DL, g(gr, "maxForma")), 3)

    def test_06_smierc_forma_nizej_legowisko_zostaje(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, maxForma=4, zloto=123.0, tarczaDo=0, laskaDo=0)
        gr.get("poziomy").set("szybkosc", 2.0)
        bot = byt(S, 0, 5, D["formy"][2]["r"] + 2, 0)
        ustaw(bot, myslDo=99, tarczaDo=0)
        zd = krok(S)
        self.assertTrue([z for z in zd if z["t"] == "smierc" and z["id"] == g(gr, "id")], "bot zjada gracza")
        krok(S, int(D["smierc"]["odrodzenie_s"] / 0.1) + 1, 0.1)
        self.assertIsNone(g(gr, "martwyDo"))
        self.assertEqual(g(gr, "forma"), 2, "o jedną formę niżej")
        self.assertEqual(g(gr, "maxForma"), 4, "legowisko zostaje")
        self.assertGreaterEqual(g(gr, "zloto"), 123, "złoto zostaje")
        self.assertEqual(g(gr.get("poziomy"), "szybkosc"), 2, "ulepszenia zostają")
        self.assertGreater(g(gr, "tarczaDo"), g(S, "czas") + D["smierc"]["tarcza_s"] - 1, "tarcza ok. 5 s")
        self.assertAlmostEqual(g(gr, "wzrost"), D["formy"][1]["potrzeba"] * D["smierc"]["pasek_po"])
        # forma 1 nigdy niżej
        ustaw(gr, forma=1, tarczaDo=0, x=50, z=50)
        ustaw(bot, x=50 + D["formy"][0]["r"] + 2, z=50)
        krok(S, 1)
        krok(S, int(D["smierc"]["odrodzenie_s"] / 0.1) + 1, 0.1)
        self.assertEqual(g(gr, "forma"), 1)

    def test_07_kup(self):
        S = stan()
        gr = byt(S, 1, 1, 0, 0)
        ok, powod = wolaj("kup", S, gr, "szybkosc")
        self.assertEqual((ok, powod), (False, "zloto"))
        self.assertEqual(wolaj("kup", S, gr, 5)[0], False, "zły typ")
        self.assertEqual(wolaj("kup", S, gr, "nie_ma")[0], False)
        ustaw(gr, zloto=10000.0)
        v1 = jeden("predkosc", DL, gr)
        self.assertTrue(wolaj("kup", S, gr, "szybkosc")[0])
        self.assertEqual(g(gr, "zloto"), 10000 - D["ulepszenia"][1]["ceny"][0])
        self.assertAlmostEqual(jeden("predkosc", DL, gr) / v1, 19 / 16)
        self.assertTrue(wolaj("kup", S, gr, "szybkosc")[0])
        self.assertEqual(wolaj("kup", S, gr, "szybkosc"), [False, "zloto"], "poziom 4 za drogi przy reszcie złota")
        ustaw(gr, zloto=1e6)
        self.assertTrue(wolaj("kup", S, gr, "szybkosc")[0])
        self.assertTrue(wolaj("kup", S, gr, "szybkosc")[0])
        self.assertEqual(g(gr.get("poziomy"), "szybkosc"), 5)
        self.assertEqual(wolaj("kup", S, gr, "szybkosc"), [False, "maks"])
        self.assertTrue(wolaj("kup", S, gr, "apetyt")[0])
        self.assertEqual(jeden("apetyt", DL, gr), 1.25)
        self.assertTrue(wolaj("kup", S, gr, "szczeka")[0])
        self.assertEqual(jeden("zasiegGryzu", DL, gr), D["ulepszenia"][0]["zasieg"][1])

    def test_08_pozycja_od_klienta(self):
        S = stan()
        gr = byt(S, 1, 1, 0, 0)
        krok(S, 2, 0.05)
        self.assertTrue(jeden("pozycjaKlienta", S, gr, 1.0, 0.5), "krok w zasięgu prędkości")
        self.assertFalse(jeden("pozycjaKlienta", S, gr, 80.0, 0.0), "teleport odrzucony")
        self.assertFalse(jeden("pozycjaKlienta", S, gr, float("nan"), 0.0), "NaN odrzucony")
        self.assertFalse(jeden("pozycjaKlienta", S, gr, "x", 0.0), "zły typ odrzucony")
        self.assertFalse(jeden("steruj", gr, float("nan"), 0.0))
        jeden("steruj", gr, 5.0, 0.0)
        self.assertAlmostEqual(g(gr, "wx"), 1.0, msg="kierunek przycięty do 1")
        x, z = wolaj("ogranicz", DL, 500.0, 0.0, 1.6)
        self.assertLessEqual(math.hypot(x, z), D["pole"]["r"], "pole ograniczone")

    def test_09_umiejetnosci(self):
        S = stan()
        # SLURP (forma 1): kulki w promieniu
        p = D["kulkiPoz"][-6]
        gr = byt(S, 1, 1, p[0] + 4, p[1])
        lista = LM.Tabela()
        self.assertTrue(jeden("umiejetnosc", S, gr, lista))
        self.assertTrue([z for z in LM.z_luau(lista, True) if z["t"] == "kulka"], "SLURP zjada kulki w pobliżu")
        self.assertFalse(jeden("umiejetnosc", S, gr, LM.Tabela()), "odnowa")
        # SPORE CLOUD (forma 4): ogłusza bota obok
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 4, 0, 0)
        bot = byt(S, 0, 6, 12, 0)
        ustaw(bot, tarczaDo=0)
        self.assertTrue(jeden("umiejetnosc", S, gr, LM.Tabela()))
        self.assertGreater(g(bot, "ogluszonyDo"), g(S, "czas"), "ogłuszony większy")
        # POUNCE (forma 6): skok i lądowanie z połknięciem mniejszego
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 6, 0, 0)
        ustaw(gr, tarczaDo=0, kier=0.0)
        ofiara = byt(S, 0, 3, 0, D["formy"][5]["um"]["d"])
        ustaw(ofiara, tarczaDo=0, myslDo=99)
        self.assertTrue(jeden("umiejetnosc", S, gr, LM.Tabela()))
        self.assertIsNotNone(gr.get("skok"))
        zd = krok(S, 14, 0.05)
        self.assertTrue([z for z in zd if z["t"] == "ladowanie"], "lądowanie")
        self.assertIsNotNone(g(ofiara, "martwyDo"), "połknięty przy lądowaniu")

    def test_10_odbicie_chronionych(self):
        S = stan()
        bez_kulek(S)
        a = byt(S, 1, 4, 0, 0)
        b = byt(S, 2, 2, 1.0, 0)
        ustaw(a, tarczaDo=0)
        ustaw(b, tarczaDo=0)
        zd = krok(S)
        self.assertFalse([z for z in zd if z["t"] == "zjedz"], "gracz formy 2 nie do zjedzenia przez gracza")
        self.assertIsNone(g(b, "martwyDo"))
        self.assertTrue([z for z in zd if z["t"] == "odbicie"], "odbicie")

    def test_12_bot_nie_zjada_mlodego_przypadkiem(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 1, 0, 0)
        bot = byt(S, 0, 3, D["formy"][0]["r"] + 1.5, 0)
        ustaw(gr, tarczaDo=0, laskaDo=0)
        ustaw(bot, myslDo=99, tarczaDo=0)
        krok(S, 2)
        self.assertIsNone(g(gr, "martwyDo"), "bot idący do kulek nie zjada gracza formy 1 przypadkiem")
        ustaw(bot, cel=g(gr, "id"), x=D["formy"][0]["r"] + 1.5, z=0)
        ustaw(gr, x=0, z=0, laskaDo=g(S, "czas") + 30)
        krok(S, 1)
        self.assertIsNone(g(gr, "martwyDo"), "łaska nowicjusza: w pierwszej minucie boty nie zjadają")
        ustaw(bot, cel=g(gr, "id"), x=D["formy"][0]["r"] + 1.5, z=0)
        ustaw(gr, x=0, z=0, laskaDo=0)
        krok(S, 1)
        self.assertIsNotNone(g(gr, "martwyDo"), "bot, który poluje na gracza formy 1, zjada go")

    def test_11_boty_zyja_i_nie_stoja_przy_starcie(self):
        S = stan(ziarno=9)
        for f, ile in enumerate([3, 3, 2, 2, 1, 1], 1):
            for _ in range(ile):
                byt(S, 0, f)
        gr = byt(S, 1, 3)
        x0, z0 = g(gr, "x"), g(gr, "z")
        # większe boty nie zaczynają przy miejscu startu gracza
        wieksze = [b for b in LM.z_luau(S.get("byty"), True) if b["slot"] == 0 and b["forma"] > 3]
        self.assertTrue(all(math.hypot(b["x"] - x0, b["z"] - z0) > 20 for b in wieksze), "start z dala od większych")
        # 8 s świata: boty się ruszają, ten sam skład form
        poz0 = {b["id"]: (b["x"], b["z"]) for b in wieksze}
        krok(S, 40, 0.2)
        byty = LM.z_luau(S.get("byty"), True)
        boty = [b for b in byty if b["slot"] == 0]
        self.assertEqual(len(boty), 12)
        ruszone = sum(1 for b in boty if b["id"] in poz0 and math.hypot(b["x"] - poz0[b["id"]][0], b["z"] - poz0[b["id"]][1]) > 3)
        self.assertGreaterEqual(ruszone, len(poz0) - 1, "boty chodzą")
        self.assertEqual(sorted(b["forma"] for b in boty), [1, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5, 6], "formy botów stałe")


class TestLas(unittest.TestCase):
    def test_13_brama_lasu(self):
        S = stan()
        gr = byt(S, 1, 3, 0, 0)
        LS = D["las"]
        cel = (LS["x"], LS["z"])
        ustaw(gr, maxForma=3)
        x, z = wolaj("ogranicz", DL, cel[0], cel[1], 3.0, jeden("maska", DL, gr))
        self.assertLessEqual(math.hypot(x, z), D["pole"]["r"], "forma 3: las zamknięty (zostaje na łące)")
        ustaw(gr, maxForma=4, forma=4)
        x, z = wolaj("ogranicz", DL, cel[0], cel[1], 4.0, jeden("maska", DL, gr))
        self.assertAlmostEqual(x, cel[0])
        self.assertAlmostEqual(z, cel[1], msg="forma 4 zdobyta: las otwarty")
        self.assertTrue(jeden("wLesie", DL, cel[0], cel[1]))
        # bot łąki nie wchodzi do lasu, bot lasu nie wychodzi
        b1, b2 = byt(S, 0, 2, 0, 0), byt(S, 0, 5, None, None, 2) if False else jeden("dodajByt", S, 0.0, 5.0, None, None, 2.0)
        x, z = wolaj("ogranicz", DL, cel[0], cel[1], 2.2, jeden("maska", DL, b1))
        self.assertLessEqual(math.hypot(x, z), D["pole"]["r"])
        x, z = wolaj("ogranicz", DL, 0.0, 0.0, 5.2, jeden("maska", DL, b2))
        self.assertLessEqual(math.hypot(x - cel[0], z - cel[1]), LS["r"])
        self.assertTrue(jeden("wLesie", DL, g(b2, "x"), g(b2, "z")), "bot lasu rodzi się w lesie")

    def test_14_las_otwiera_sie_przy_formie_4(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, maxForma=3, wzrost=D["formy"][2]["potrzeba"])
        jeden("ewoluuj", S, gr, LM.Tabela())
        zd = krok(S, int(D["ewolucja"]["kokon_s"] / 0.1) + 1, 0.1)
        self.assertTrue([z for z in zd if z["t"] == "las_otwarty"], "zdarzenie: DEEP WOODS otwarte")
        self.assertEqual(jeden("maska", DL, gr), 3)

    def test_15_mini_boss(self):
        S = stan()
        bez_kulek(S)
        boss = jeden("dodajBossa", S)
        gr = byt(S, 1, 5, g(boss, "x") + D["formy"][4]["r"] + D["formy"][6]["r"] + 1, g(boss, "z"))
        ustaw(gr, maxForma=5, tarczaDo=0, laskaDo=0, zloto=0.0)
        self.assertFalse(jeden("mozeZjesc", DL, gr, boss), "bossa nie da się zjeść")
        self.assertFalse(jeden("mozeZjesc", DL, boss, gr), "boss nie zjada")
        hp0 = g(boss, "hp")
        lista = LM.Tabela()
        self.assertTrue(jeden("gryz", S, gr, lista))
        rany = [z for z in LM.z_luau(lista, True) if z["t"] == "boss_rana"]
        self.assertTrue(rany, "BITE rani bossa")
        self.assertEqual(hp0 - g(boss, "hp"), jeden("obrazenia", DL, gr))
        # boss gryzie: odrzut, ogłuszenie, kara z paska — bez zjedzenia
        ustaw(gr, wzrost=100.0, x=g(boss, "x") + D["formy"][4]["r"] + D["formy"][6]["r"] - 0.5, z=g(boss, "z"))
        ustaw(boss, gryzGotowy=0, myslDo=0)
        zd = krok(S, 3, 0.05)
        bg = [z for z in zd if z["t"] == "boss_gryz"]
        self.assertTrue(bg, "boss gryzie gracza w zasięgu")
        self.assertIsNone(g(gr, "martwyDo"), "gracz nie zjedzony")
        self.assertLess(g(gr, "wzrost"), 100, "kara z paska")
        # pokonany: skrzynia dla gracza, powrót po czasie z pełnym życiem
        ustaw(boss, hp=3.0)
        ustaw(gr, ogluszonyDo=0, x=g(boss, "x") + D["formy"][4]["r"] + D["formy"][6]["r"] + 1, z=g(boss, "z"), gryzGotowy=0)
        lista = LM.Tabela()
        jeden("gryz", S, gr, lista)
        pok = [z for z in LM.z_luau(lista, True) if z["t"] == "boss_pokonany"]
        self.assertTrue(pok and pok[0]["s"] == g(gr, "slot"), "pokonany przez gracza")
        self.assertGreaterEqual(g(gr, "zloto"), D["boss"]["skrzynia"], "skrzynia złota")
        self.assertIsNotNone(g(boss, "martwyDo"))
        krok(S, int(D["boss"]["odrodzenie_s"] / 1.0) + 2, 1.0)
        self.assertIsNone(g(boss, "martwyDo"))
        self.assertEqual(g(boss, "hp"), D["boss"]["stopnie_hp"][1], "wraca jako stopień 2 z pełnym życiem")


class TestEtap3(unittest.TestCase):
    def test_16_zapis_i_wczytanie(self):
        S = stan()
        gr = byt(S, 1, 5, 0, 0)
        ustaw(gr, maxForma=6, zloto=1234.0, zlotoLeg=56.0, bossTrofea=2)
        gr.get("poziomy").set("apetyt", 3.0)
        gr.get("warianty").set(3.0, "rubin")
        gr.get("trofea").set(2.0, 4.0)
        mag = jeden("pamiec")
        p = jeden("doProfilu", DL, gr, 1000)
        ok, powod = wolaj("zapisz", DL, mag, "player_1", "job_a", p, 1000, True)
        self.assertTrue(ok)
        prof, zapisywalny, powod = wolaj("wczytaj", DL, mag, "player_1", "job_b", 1000)
        self.assertTrue(zapisywalny, "zwolniona blokada: inny serwer wczytuje")
        nowy = byt(S, 2, 1, 10, 10)
        zarobek, sek = wolaj("zProfilu", DL, nowy, prof, 1000)
        self.assertEqual((g(nowy, "forma"), g(nowy, "maxForma"), g(nowy, "zloto")), (1, 6, 1234), "forma od nowa, reszta zostaje")
        self.assertEqual(g(nowy.get("poziomy"), "apetyt"), 3)
        self.assertEqual(g(nowy.get("warianty"), 3), "rubin")
        self.assertEqual(g(nowy.get("trofea"), 2), 4)
        self.assertEqual(g(nowy, "bossTrofea"), 2)
        self.assertEqual(zarobek, 0, "bez nieobecności")
        # blokada: job_b trzyma sesję, job_c nie wczyta zapisywalnie i nie nadpisze
        prof2, zapisywalny2, powod2 = wolaj("wczytaj", DL, mag, "player_1", "job_c", 1010)
        self.assertEqual((zapisywalny2, powod2), (False, "zajety"))
        ok3, powod3 = wolaj("zapisz", DL, mag, "player_1", "job_c", jeden("profilNowy", DL), 1011, False)
        self.assertEqual((ok3, powod3), (False, "cudza_sesja"), "cudza sesja nie nadpisuje prawdziwego postępu")
        # dane zepsute → szablon
        zly = jeden("profilZ", DL, LM.do_luau({"zloto": "x", "maxForma": 99, "warianty": ["oszust"]}))
        self.assertEqual((g(zly, "zloto"), g(zly, "maxForma"), g(zly.get("warianty"), 1)), (0, len(D["formy"]), ""))

    def test_17_nieobecnosc_do_2_godzin(self):
        S = stan()
        gr = byt(S, 1, 1, 0, 0)
        p = jeden("profilNowy", DL)
        p.set("maxForma", 3.0)
        p.set("ostatnio", 1000.0)
        stawka = sum(f["trofeum"] for f in D["formy"][:3])
        zar, sek = wolaj("zProfilu", DL, gr, p, 1000 + 600)
        self.assertEqual((sek, zar), (600, stawka * 600))
        gr2 = byt(S, 2, 1, 5, 5)
        zar2, sek2 = wolaj("zProfilu", DL, gr2, p, 1000 + 99999)
        self.assertEqual(sek2, D["zapis"]["nieobecnosc_maks_s"], "najwyżej 2 godziny")
        self.assertEqual(zar2, stawka * 7200)

    def test_18_szanse_wariantow(self):
        import random
        r = random.Random(5)
        n = 20000
        ile = {}
        for _ in range(n):
            w = jeden("losujWariant", DL, r.random())
            ile[w] = ile.get(w, 0) + 1
        for W in D["warianty"]:
            p = ile.get(W["id"], 0) / n
            self.assertAlmostEqual(p, W["szansa"], delta=max(0.004, W["szansa"] * 0.35), msg=W["id"])
        self.assertEqual(jeden("losujWariant", DL, 0.0), "tecza", "najrzadszy na początku przedziału")
        self.assertIsNone(jeden("losujWariant", DL, 0.5))
        # najlepszy wariant zostaje, mnożnik w stawce
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 1, 0, 0)
        ustaw(gr, wzrost=D["formy"][0]["potrzeba"])
        S.set("wymusWariant", "krysztal")
        jeden("ewoluuj", S, gr, LM.Tabela())
        krok(S, int(D["ewolucja"]["kokon_s"] / 0.1) + 1, 0.1)
        self.assertEqual(g(gr.get("warianty"), 2), "krysztal")
        self.assertEqual(jeden("stawkaB", DL, gr), D["formy"][0]["trofeum"] + D["formy"][1]["trofeum"] * 4)

    def test_19_poziomy_trofeow_i_legowisko(self):
        S = stan()
        bez_kulek(S)
        lx, lz = D["legowiska"][0]
        gr = byt(S, 1, 3, lx + 40, lz)
        ustaw(gr, maxForma=3, zloto=1e6, laskaDo=0, tarczaDo=0)
        self.assertEqual(wolaj("kupTrofeum", S, gr, 2), [False, "legowisko"], "poziom trofeum tylko w legowisku")
        ustaw(gr, x=lx, z=lz)
        for _ in range(4):
            self.assertTrue(wolaj("kupTrofeum", S, gr, 2)[0])
        self.assertEqual(wolaj("kupTrofeum", S, gr, 2), [False, "maks"], "pięć poziomów")
        self.assertEqual(wolaj("kupTrofeum", S, gr, 5), [False, "brak"], "forma niezdobyta")
        self.assertAlmostEqual(jeden("stawkaB", DL, gr), 1 + 2 * D["legowisko"]["poziomy_x"][4] + 4)
        # złoto legowiska zbiera się w legowisku; legowisko to strefa bezpieczna; boty nie wchodzą
        ustaw(gr, zloto=0.0, zlotoLeg=0.0)
        bot = byt(S, 0, 6, lx + 3, lz)
        ustaw(bot, myslDo=99, tarczaDo=0, cel=g(gr, "id"))
        krok(S, 20, 0.05)
        self.assertIsNone(g(gr, "martwyDo"), "nikt cię nie zje we własnym legowisku")
        self.assertGreater(math.hypot(g(bot, "x") - lx, g(bot, "z") - lz), D["legowisko"]["r"], "bot wypchnięty z legowiska")
        self.assertGreater(g(gr, "zloto"), 0, "złoto zebrane w legowisku")
        ustaw(gr, x=lx + 60, z=lz, zloto=0.0)
        krok(S, 20, 0.05)
        self.assertEqual(g(gr, "zloto"), 0, "poza legowiskiem złoto czeka w legowisku")
        self.assertGreater(g(gr, "zlotoLeg"), 0)

    def test_20_stopnie_bossa(self):
        S = stan()
        bez_kulek(S)
        boss = jeden("dodajBossa", S)
        gr = byt(S, 1, 6, g(boss, "x") + D["formy"][5]["r"] + D["formy"][6]["r"] + 1, g(boss, "z"))
        ustaw(gr, maxForma=6, tarczaDo=0, laskaDo=0, zloto=0.0)
        hp = []
        for st in range(1, 4):
            hp.append(g(boss, "hpMaks"))
            ustaw(boss, hp=1.0)
            lista = LM.Tabela()
            wolaj("ranBossa", S, boss, gr, 5, lista)
            pok = [z for z in LM.z_luau(lista, True) if z["t"] == "boss_pokonany"]
            self.assertTrue(pok and pok[0]["stopien"] == st and pok[0]["trofeum"])
            krok(S, int(D["boss"]["odrodzenie_s"]) + 2, 1.0)
        self.assertEqual(hp, D["boss"]["stopnie_hp"][:3], "coraz silniejszy")
        self.assertEqual(g(gr, "bossTrofea"), 3, "trofea bossa za pierwsze wygrane stopnie")
        self.assertGreaterEqual(g(gr, "zloto"), sum(D["boss"]["stopnie_skrzynia"][:3]))

    def test_21_olbrzym_boss_serwera(self):
        S = stan()
        bez_kulek(S)
        nf = len(D["formy"])
        olb = byt(S, 1, nf, 0, 0)
        ustaw(olb, maxForma=nf, tarczaDo=0, laskaDo=0, olbrzymHp=float(D["olbrzym"]["hp"]))
        at = byt(S, 2, 5, D["formy"][nf - 1]["r"] + D["formy"][4]["r"] + 1, 0)
        ustaw(at, maxForma=5, tarczaDo=0, laskaDo=0, zloto=0.0)
        krok(S, 1)
        lista = LM.Tabela()
        self.assertTrue(jeden("gryz", S, at, lista))
        zd = LM.z_luau(lista, True)
        self.assertTrue([z for z in zd if z["t"] == "olbrzym_rana"], "inny gracz rani Olbrzyma")
        self.assertEqual(g(at, "zloto"), D["olbrzym"]["za_trafienie"])
        ustaw(olb, olbrzymHp=1.0)
        ustaw(at, gryzGotowy=0)
        lista = LM.Tabela()
        jeden("gryz", S, at, lista)
        self.assertTrue([z for z in LM.z_luau(lista, True) if z["t"] == "olbrzym_obalony"])
        self.assertEqual(g(olb, "forma"), nf - 1, "Olbrzym spada o formę")
        self.assertIsNone(g(olb, "martwyDo"), "nie ginie")
        self.assertGreaterEqual(g(at, "zloto"), D["olbrzym"]["skrzynia"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
