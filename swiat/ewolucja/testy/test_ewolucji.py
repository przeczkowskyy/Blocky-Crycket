#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy logiki Monster Evolution bez Studio (zrodla/LogikaEwolucji.luau w interpreterze tools/walka/luau_mini.py).

    python -B swiat/ewolucja/testy/test_ewolucji.py
"""
import functools
import json
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
import dane as DN
import swiat_mapa2 as M2  # noqa: E402
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
        W = D["walka"]
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, tarczaDo=0, laskaDo=0, kier=math.pi / 2)
        ofiara = byt(S, 0, 3, D["formy"][2]["r"] * 2 + 1.5, 0)
        ustaw(ofiara, myslDo=99, tarczaDo=0)
        hp0 = g(ofiara, "hp")
        self.assertAlmostEqual(hp0, W["hp_baza"] * W["hp_wzrost"] ** 2, msg="życie według stadium")
        rany, k = [], []
        for i in range(3):
            lista = LM.Tabela()
            ustaw(ofiara, x=D["formy"][2]["r"] * 2 + 1.5, z=0, ogluszonyDo=0)
            self.assertTrue(jeden("gryz", S, gr, lista))
            zd = LM.z_luau(lista, True)
            k += [z["k"] for z in zd if z["t"] == "gryz"]
            rany += [z for z in zd if z["t"] == "rana"]
            self.assertFalse(jeden("gryz", S, gr, LM.Tabela()), "przerwa między ciosami")
            ustaw(gr, gryzGotowy=0)
        self.assertEqual(k, [1, 2, 3], "łańcuch trzech ciosów")
        sila = W["gryz_baza"] * W["gryz_wzrost"] ** 2
        oczek = [max(1, math.floor(sila * x + 0.5)) for x in W["lancuch_x"]]
        for z, o in zip(rany, oczek):
            self.assertIn(z["ile"], (o, max(1, math.floor(sila * W["lancuch_x"][rany.index(z)] * W["kryt_x"] + 0.5))), "rana z łańcucha (albo kryt)")
        self.assertTrue(rany[2].get("pw") and not rany[0].get("pw"), "trzeci cios przewraca")
        self.assertGreater(g(ofiara, "ogluszonyDo"), g(S, "czas"), "przewrócony")
        self.assertGreater(abs(g(ofiara, "vx")), W["odrzut"] * 0.9, "trzeci cios odrzuca")
        # przerwa dłuższa niż lancuch_reset_s → łańcuch od nowa
        krok(S, int((W["lancuch_s"][2] + W["lancuch_reset_s"]) / 0.1) + 2, 0.1)
        lista = LM.Tabela()
        ustaw(ofiara, x=D["formy"][2]["r"] * 2 + 1.5, z=0, ogluszonyDo=0, hp=1.0)
        ustaw(gr, x=0, z=0, gryzGotowy=0)
        jeden("gryz", S, gr, lista)
        zd = LM.z_luau(lista, True)
        self.assertEqual([z["k"] for z in zd if z["t"] == "gryz"], [1], "łańcuch od nowa po przerwie")
        # zero życia → zjedzony, wzrost dla zjadającego
        zj = [z for z in zd if z["t"] == "zjedz"]
        self.assertTrue(zj and zj[0]["b"] == g(ofiara, "id"), "zero życia = zjedzony")
        self.assertIsNotNone(g(ofiara, "martwyDo"))
        self.assertEqual(g(gr, "wzrost"), D["jedzenie"]["za_forme"][2])
        # bot wraca po odrodzenie_s w tej samej formie z pełnym życiem
        krok(S, int(D["boty"]["odrodzenie_s"] / 0.1) + 2, 0.1)
        self.assertIsNone(g(ofiara, "martwyDo"))
        self.assertEqual(g(ofiara, "forma"), 3)
        self.assertAlmostEqual(g(ofiara, "hp"), hp0)
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
        ustaw(gr, maxForma=4, zloto=123.0, tarczaDo=0, laskaDo=0, hp=1.0)
        gr.get("poziomy").set("szybkosc", 2.0)
        bot = byt(S, 0, 5, D["formy"][2]["r"] + D["formy"][4]["r"] + 1, 0)
        ustaw(bot, myslDo=99, tarczaDo=0, cel=g(gr, "id"))
        zd = krok(S, 2)
        self.assertTrue([z for z in zd if z["t"] == "smierc" and z["id"] == g(gr, "id")], "bot gryzie gracza do zera")
        krok(S, int(D["smierc"]["odrodzenie_s"] / 0.1) + 1, 0.1)
        self.assertIsNone(g(gr, "martwyDo"))
        self.assertEqual(g(gr, "forma"), 2, "o jedną formę niżej")
        self.assertAlmostEqual(g(gr, "hp"), g(gr, "hpMaks"), msg="pełne życie po odrodzeniu")
        self.assertEqual(g(gr, "maxForma"), 4, "legowisko zostaje")
        self.assertGreaterEqual(g(gr, "zloto"), 123, "złoto zostaje")
        self.assertEqual(g(gr.get("poziomy"), "szybkosc"), 2, "ulepszenia zostają")
        self.assertGreater(g(gr, "tarczaDo"), g(S, "czas") + D["smierc"]["tarcza_s"] - 1, "tarcza ok. 5 s")
        self.assertAlmostEqual(g(gr, "wzrost"), D["formy"][1]["potrzeba"] * D["smierc"]["pasek_po"])
        # forma 1 nigdy niżej
        ustaw(gr, forma=1, tarczaDo=0, x=50, z=50, hp=1.0)
        ustaw(bot, x=50 + D["formy"][0]["r"] + D["formy"][4]["r"] + 1, z=50, gryzGotowy=0, cel=g(gr, "id"))
        krok(S, 2)
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
        if D.get("mapa2"):
            # mapa v2: obszar = suma stref (najdalej wąwóz bramy ok. 236 st.); punkt z ograniczenia już nie przesuwa się dalej
            x2, z2 = wolaj("ogranicz", DL, x, z, 1.6)
            self.assertLess(math.hypot(x2 - x, z2 - z), 0.01, "pole ograniczone (stały punkt)")
            self.assertLessEqual(math.hypot(x, z), 240, "pole ograniczone")
        else:
            self.assertLessEqual(math.hypot(x, z), D["pole"]["r"], "pole ograniczone")

    def test_09_umiejetnosci(self):
        Z = D["zdolnosci"]
        # linie ewoluują: stadium 1 bez zdolności, potem wersje z danych; następna wersja do pokazania w HUD
        self.assertIsNone(jeden("zdolnoscFormy", DL, "ogien", 1))
        self.assertIsNone(jeden("zdolnoscFormy", DL, "moc", 2))
        for linia in ("ogien", "moc"):
            for f in range(1, len(D["formy"]) + 1):
                A = jeden("zdolnoscFormy", DL, linia, f)
                oczek = [x for x in Z[linia] if x["od"] <= f]
                self.assertEqual(LM.z_luau(A)["id"] if A else None, oczek[-1]["id"] if oczek else None)
        self.assertEqual(LM.z_luau(jeden("nastepnaZdolnosc", DL, "ogien", 2))["id"], "oddech")
        self.assertEqual([x["od"] for x in Z["ogien"]], [2, 4, 7])
        self.assertEqual([x["od"] for x in Z["moc"]], [3, 5, 6, 8])
        # EMBER SPIT: zamach widoczny, potem pocisk trafia bota przed pyskiem
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 2, 0, 0)
        ustaw(gr, tarczaDo=0, laskaDo=0, kier=0.0)
        bot = byt(S, 0, 2, 0, 15)
        ustaw(bot, tarczaDo=0, myslDo=99)
        lista = LM.Tabela()
        self.assertFalse(jeden("zdolnosc", S, gr, "moc", lista), "POWER zamknięte na stadium 2")
        self.assertFalse(jeden("zdolnosc", S, gr, "zle", lista), "zła linia odrzucona")
        self.assertTrue(jeden("zdolnosc", S, gr, "ogien", lista))
        self.assertTrue([z for z in LM.z_luau(lista, True) if z["t"] == "zamach" and z["ab"] == "zar"], "zamach widoczny dla innych")
        self.assertFalse(jeden("zdolnosc", S, gr, "ogien", LM.Tabela()), "odnowa")
        zd = krok(S, 20, 0.05)
        self.assertTrue([z for z in zd if z["t"] == "pocisk"], "pocisk po zamachu")
        tr = [z for z in zd if z["t"] == "rana" and z["id"] == g(bot, "id") and z["jak"] == "zar"]
        self.assertTrue(tr, "EMBER SPIT trafia")
        # ogłuszenie w zamachu przerywa zdolność
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, tarczaDo=0, laskaDo=0)
        self.assertTrue(jeden("zdolnosc", S, gr, "moc", LM.Tabela()))
        ustaw(gr, ogluszonyDo=g(S, "czas") + 1)
        jeden("ran", S, byt(S, 0, 3, 40, 40), gr, 1, LM.Tabela(), "test", 1.0, 0.0, 5.0, 1.0)
        zd = krok(S, 30, 0.05)
        self.assertFalse([z for z in zd if z["t"] == "ogon"], "przewrót w zamachu przerywa TAIL SWEEP")
        # TAIL SWEEP: krąg wokół, odrzut i przewrót (także większego), bez ran dla chronionego gracza
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, tarczaDo=0, laskaDo=0)
        za = byt(S, 0, 4, 0, -(D["formy"][2]["r"] + D["formy"][3]["r"] + 1))
        mlody = byt(S, 2, 2, D["formy"][2]["r"] + D["formy"][1]["r"] + 1, 0)
        ustaw(za, tarczaDo=0, myslDo=99)
        ustaw(mlody, tarczaDo=0, laskaDo=0)
        self.assertTrue(jeden("zdolnosc", S, gr, "moc", LM.Tabela()))
        zd = krok(S, 8, 0.05)
        self.assertTrue([z for z in zd if z["t"] == "ogon"])
        self.assertTrue([z for z in zd if z["t"] == "rana" and z["id"] == g(za, "id") and z.get("pw")], "za plecami też (360°)")
        self.assertFalse([z for z in zd if z["t"] == "rana" and z["id"] == g(mlody, "id")], "gracz stadium 2 chroniony")
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
        odl = D["formy"][0]["r"] + D["formy"][2]["r"] + 1
        bot = byt(S, 0, 3, odl, 0)
        ustaw(gr, tarczaDo=0, laskaDo=0, hp=1.0)
        ustaw(bot, myslDo=99, tarczaDo=0)
        krok(S, 2)
        self.assertIsNone(g(gr, "martwyDo"), "bot idący do kulek nie gryzie gracza formy 1 przypadkiem")
        ustaw(bot, cel=g(gr, "id"), x=odl, z=0, gryzGotowy=0)
        ustaw(gr, x=0, z=0, laskaDo=g(S, "czas") + 30)
        krok(S, 1)
        self.assertIsNone(g(gr, "martwyDo"), "łaska nowicjusza: w pierwszych minutach boty nie gryzą")
        ustaw(bot, cel=g(gr, "id"), x=odl, z=0, gryzGotowy=0)
        ustaw(gr, x=0, z=0, laskaDo=0)
        krok(S, 1)
        self.assertIsNotNone(g(gr, "martwyDo"), "bot, który poluje na gracza formy 1, gryzie go do zera")
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
        rB, r5 = D["formy"][D["boss"]["forma"] - 1]["r"], D["formy"][4]["r"]
        gr = byt(S, 1, 5, g(boss, "x") + r5 + rB + 1, g(boss, "z"))
        ustaw(gr, maxForma=5, tarczaDo=0, laskaDo=0, zloto=0.0)
        self.assertFalse(jeden("mozeZjesc", DL, gr, boss), "bossa nie da się zjeść")
        self.assertFalse(jeden("mozeRanic", S, byt(S, 0, 6, 300, 300), boss), "boty nie ranią bossa")
        hp0 = g(boss, "hp")
        self.assertEqual(hp0, D["boss"]["stopnie_hp"][0])
        lista = LM.Tabela()
        self.assertTrue(jeden("gryz", S, gr, lista))
        rany = [z for z in LM.z_luau(lista, True) if z["t"] == "boss_rana"]
        self.assertTrue(rany, "BITE rani bossa")
        sila = jeden("obrazenia", DL, gr)
        self.assertIn(hp0 - g(boss, "hp"), (math.floor(sila + 0.5), math.floor(sila * D["walka"]["kryt_x"] + 0.5)), "rana jak każdemu (bez rozmiaru)")
        # boss gryzie: rana z życia gracza, odrzut i ogłuszenie
        ustaw(gr, x=g(boss, "x") + r5 + rB, z=g(boss, "z"), hp=100.0, ostRana=1e9)
        ustaw(boss, gryzGotowy=0, myslDo=0)
        zd = krok(S, 3 + int((D["boss"].get("zamach_s") or 0) / 0.05) + 1, 0.05)
        if D["boss"].get("zamach_s"):
            self.assertTrue([z for z in zd if z["t"] == "boss_zamach"], "golem: zamach przed ciosem")
        self.assertTrue([z for z in zd if z["t"] == "boss_gryz"], "boss gryzie gracza w zasięgu")
        self.assertIsNone(g(gr, "martwyDo"))
        self.assertAlmostEqual(g(gr, "hp"), 100 - D["boss"]["stopnie_gryz"][0], delta=1)
        self.assertGreater(g(gr, "ogluszonyDo"), g(S, "czas") - 0.2)
        # boss zjada gracza z zerem życia (spada o stadium jak zawsze)
        ustaw(gr, x=g(boss, "x") + r5 + rB, z=g(boss, "z"), hp=1.0, ogluszonyDo=0, tarczaDo=0)
        ustaw(boss, gryzGotowy=0, myslDo=0)
        zd = krok(S, 3 + int((D["boss"].get("zamach_s") or 0) / 0.05) + 1, 0.05)
        self.assertTrue([z for z in zd if z["t"] == "zjedz" and z["b"] == g(gr, "id")], "boss zjada przy zerze")
        krok(S, int(D["smierc"]["odrodzenie_s"] / 0.1) + 2, 0.1)
        self.assertEqual(g(gr, "forma"), 4)
        # pokonany: skrzynia dla gracza, powrót po czasie z pełnym życiem
        ustaw(boss, hp=3.0)
        ustaw(gr, forma=5, ogluszonyDo=0, x=g(boss, "x") + r5 + rB + 1, z=g(boss, "z"), gryzGotowy=0, tarczaDo=0)
        lista = LM.Tabela()
        jeden("gryz", S, gr, lista)
        pok = [z for z in LM.z_luau(lista, True) if z["t"] == "boss_pokonany"]
        self.assertTrue(pok and pok[0]["s"] == g(gr, "slot"), "pokonany przez gracza")
        self.assertGreaterEqual(g(gr, "zloto"), D["boss"]["skrzynia"], "skrzynia złota")
        self.assertIsNotNone(g(boss, "martwyDo"))
        krok(S, int(D["boss"]["odrodzenie_s"] / 1.0) + 2, 1.0)
        self.assertIsNone(g(boss, "martwyDo"))
        self.assertEqual(g(boss, "hp"), D["boss"]["stopnie_hp"][1], "wraca jako stopień 2 z pełnym życiem")

class TestSmok(unittest.TestCase):
    def test_22_oddech_i_podmuch(self):
        # FIRE BREATH: kanał, stożek przed pyskiem (nie za plecami), kulki w stożku zjedzone
        S = stan()
        bez_kulek(S)
        fo = 4
        r = D["formy"][fo - 1]["r"]
        gr = byt(S, 1, fo, 0, 0)
        ustaw(gr, tarczaDo=0, kier=0.0, laskaDo=0)
        przod = byt(S, 0, fo, 0, r * 2 + 4)
        tyl = byt(S, 0, fo, 0, -(r * 2 + 4))
        ustaw(przod, tarczaDo=0, myslDo=99)
        ustaw(tyl, tarczaDo=0, myslDo=99)
        self.assertTrue(jeden("zdolnosc", S, gr, "ogien", LM.Tabela()))
        zd = krok(S, 60, 0.05)
        self.assertTrue([z for z in zd if z["t"] == "oddech"])
        rp = [z for z in zd if z["t"] == "rana" and z["id"] == g(przod, "id")]
        self.assertGreaterEqual(len(rp), 5, "FIRE BREATH rani przed pyskiem co tik")
        self.assertFalse([z for z in zd if z["t"] == "rana" and z["id"] == g(tyl, "id")], "a nie za plecami")
        self.assertIsNone(gr.get("kanal"), "kanał się kończy")
        # INFERNO BREATH: płonąca ziemia rani stojącego w niej
        S = stan()
        bez_kulek(S)
        fi = 7
        r = D["formy"][fi - 1]["r"]
        gr = byt(S, 1, fi, 0, 0)
        ustaw(gr, tarczaDo=0, kier=0.0, laskaDo=0)
        self.assertTrue(jeden("zdolnosc", S, gr, "ogien", LM.Tabela()))
        zd = krok(S, 20, 0.05)
        pl = [z for z in zd if z["t"] == "plama"]
        self.assertTrue(pl, "INFERNO zostawia płonącą ziemię")
        ofiara = byt(S, 0, 5, pl[0]["x"], pl[0]["z"])
        ustaw(ofiara, tarczaDo=0, myslDo=99)
        ustaw(gr, x=-60.0, z=0.0)
        zd = krok(S, 25, 0.05)
        self.assertTrue([z for z in zd if z["t"] == "rana" and z["id"] == g(ofiara, "id") and z["jak"] == "plama"], "płonąca ziemia rani")
    def test_23_smok_generator(self):
        import smok as SM
        U = DN.ustawienia()
        if U.get("zestaw") != "smok":
            self.skipTest("zestaw potworów")
        czesci = []
        for i, F in enumerate(U["formy_smok"]):
            St = SM.stadium(F["smok"])
            czesci.append(len(St["czesci"]))
            grupy = {c["g"] for c in St["czesci"]}
            self.assertTrue({1, 2, 3, 4, 6, 7, 8, 9}.issubset(grupy), F["nazwa"] + ": nogi, głowa, szczęka, skrzydła")
            self.assertTrue(any(k >= 11 for k in grupy), "segmenty ogona")
            self.assertTrue(all(str(k) in St["pivoty"] for k in grupy if k), "każda grupa ma punkt obrotu")
            self.assertEqual(D["formy"][i]["wzorzec"], "Smok_%d" % (i + 1))
        self.assertTrue(all(n <= 80 for n in czesci), "tanio na telefonie: %s" % czesci)
        self.assertEqual(czesci, sorted(czesci), "późniejsze stadia bogatsze")


class TestPomiar(unittest.TestCase):
    def test_24_podsumowanie_sesji(self):
        M = LM.do_luau({"formy": {"1": 0, "2": 21.4, "3": 70.2}, "smierci": 2, "po_smierci": [{"t": 100, "forma": 3, "dalej": True}, {"t": 150}],
                        "ulepszenia": [{"id": "szybkosc"}], "sesja_s": 400.4, "leg": 3, "zb": 2, "tr": 1, "bs": 2, "war": {"zloty": 1, "oszust": 5}})
        r = LM.z_luau(jeden("podsumowanie", DL, M, "2026-11-23T10:00", False, 3))
        self.assertEqual(r["t"], [0, 21, 70, -1, -1, -1, -1, -1])
        self.assertEqual((r["maks"], r["sm"], r["dalej"], r["po"], r["dl"], r["ul"], r["bs"], r["nowy"], r["dni"], r["d"]),
                         (3, 2, True, 300, 400, 1, 2, False, 3, "2026-11-23"))
        self.assertEqual(set(r["war"]), {W["id"] for W in D["warianty"]}, "tylko znane warianty")
        self.assertFalse({"UserId", "userId", "nazwa", "name", "id", "slot"} & set(r), "bez identyfikatora i nazwy gracza")
        self.assertLess(len(json.dumps(r)), D["zapis"]["prob_maks_znakow"], "krótki rekord")
        pusty = LM.z_luau(jeden("podsumowanie", DL, LM.do_luau({}), "2026-11-23", True, 0))
        self.assertEqual((pusty["maks"], pusty["sm"], pusty["dalej"], pusty["nowy"]), (1, 0, False, True))

    def test_25_tabela_d128(self):
        sys.path.insert(0, TU)
        import odczyt_prob as OP
        Z = OP.zestawienie(json.load(open(os.path.join(TU, "fixtury_prob.json"), encoding="utf-8")))
        self.assertEqual(Z["sesje"], 4)
        self.assertEqual(Z["mediana_sesji_s"], 600)
        self.assertEqual((Z["udzial_stadium_3"], Z["udzial_stadium_5"]), (0.75, 0.5))
        self.assertEqual((Z["zginelo_sesji"], Z["gralo_dalej_po_1_smierci"]), (2, 0.5))
        self.assertEqual(Z["udzial_powrotow_innego_dnia"], 0.25)
        self.assertEqual(OP.zestawienie([])["sesje"], 0)


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


class TestWalka(unittest.TestCase):
    def test_26_zasady_ran(self):
        S = stan()
        bez_kulek(S)
        mr = lambda a, b: jeden("mozeRanic", S, a, b)  # noqa: E731
        g1, g3, g4 = byt(S, 1, 2, 0, 0), byt(S, 2, 3, 20, 0), byt(S, 3, 4, 40, 0)
        b1 = byt(S, 0, 1, 60, 0)
        for b in (g1, g3, g4, b1):
            ustaw(b, tarczaDo=0, laskaDo=0)
        self.assertFalse(mr(g4, g1), "gracz stadium 2 chroniony przed graczami")
        self.assertFalse(mr(g1, g4), "… i sam nie rani graczy")
        self.assertTrue(mr(g3, g4), "mniejszy też może ranić (o stadium większego)")
        self.assertTrue(mr(g1, b1), "chroniony gracz gryzie boty")
        ustaw(g4, tarczaDo=g(S, "czas") + 3)
        self.assertFalse(mr(g3, g4), "tarcza chroni")
        ustaw(g4, tarczaDo=0)
        lx, lz = wolaj("legowiskoPoz", DL, 3)
        ustaw(g4, x=lx, z=lz)
        self.assertFalse(mr(g3, g4), "we własnym legowisku nikt nie rani")
        self.assertFalse(mr(g4, g3), "… ani z legowiska")
        # rozmiar: o dwa stadia większy zabija w 1–2 ugryzieniach, mniejszy o dwa ledwo drapie
        import walka_sim as WS
        for f in range(3, len(D["formy"]) + 1):
            self.assertLessEqual(WS.ugryzien_na_zabicie(f, f - 2), 2, "o dwa stadia większy: 1–2 ugryzienia")
            self.assertGreaterEqual(WS.ugryzien_na_zabicie(f - 2, f), 20, "o dwa mniejszy: ponad 20")
        # kulki leczą, bez ran regeneracja
        S = stan()
        p = D["kulkiPoz"][-1]
        gr = byt(S, 1, 3, p[0] + 1.0, p[1])
        ustaw(gr, hp=10.0, ostRana=g(S, "czas"))
        krok(S, 1)
        self.assertGreater(g(gr, "hp"), 10.0 + g(gr, "hpMaks") * 0.01, "kulka leczy")
        h = g(gr, "hp")
        ustaw(gr, x=0, z=0)
        bez_kulek(S)
        krok(S, int(D["walka"]["regen_po_s"] / 0.1) + 10, 0.1)
        self.assertGreater(g(gr, "hp"), h, "regeneracja bez ran")

    def test_27_pojedynki(self):
        import walka_sim as WS
        czasy = [WS.pojedynek(4, 4, 100 + i)[1] for i in range(8)]
        import statistics
        m = statistics.median(czasy)
        self.assertTrue(4.0 <= m <= 6.0, "równe stadia: 4–6 s (mediana %.2f)" % m)
        wyg = sum(WS.pojedynek(5, 4, 500 + i)[0] == "a" for i in range(16))
        self.assertTrue(10 <= wyg <= 15, "o stadium większy wygrywa ok. 3 z 4 (%d/16)" % wyg)
        for linia in ("ogien", "moc"):
            for A in D["zdolnosci"][linia]:
                x = WS.manekin(A["od"], linia, 15.0) / WS.manekin(A["od"], None, 15.0)
                self.assertTrue(0.45 <= x <= 2.0, "%s: x%.2f BITE (0,5–2)" % (A["id"], x))

    def test_28_wyspa_tylko_lotem(self):
        WY = D["wyspa"]
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 5, WY["x"], WY["z"] - WY["r_zew"] - 4)
        ustaw(gr, tarczaDo=0, laskaDo=0, maxForma=5, kier=0.0)
        # pieszo: fosa nie do przejścia
        x, z = wolaj("ogranicz", DL, float(WY["x"]), float(WY["z"] - (WY["r_wew"] + WY["r_zew"]) / 2), D["formy"][4]["r"], 1.0)
        self.assertGreaterEqual(math.hypot(x - WY["x"], z - WY["z"]), WY["r_zew"], "pieszo nie wejdzie do fosy")
        self.assertFalse(jeden("naWyspie", DL, x, z))
        # WING GLIDE nad fosą: ląduje na wyspie, kulki wyspy osiągalne
        self.assertTrue(jeden("zdolnosc", S, gr, "moc", LM.Tabela()))
        krok(S, 30, 0.05)
        self.assertTrue(jeden("naWyspie", DL, g(gr, "x"), g(gr, "z")), "szybowanie przenosi przez fosę")
        wysp = [p for p in D["kulkiPoz"] if math.hypot(p[0] - WY["x"], p[1] - WY["z"]) < WY["r_wew"]]
        self.assertEqual(len(wysp), WY["kulek"], "wielkie kulki na wyspie")
        self.assertFalse([p for p in D["kulkiPoz"] if WY["r_wew"] <= math.hypot(p[0] - WY["x"], p[1] - WY["z"]) < WY["r_zew"]], "nic w fosie")
        # boty nie rodzą się na wyspie
        S = stan(ziarno=4)
        for _ in range(40):
            b = byt(S, 0, 2)
            self.assertGreater(math.hypot(g(b, "x") - WY["x"], g(b, "z") - WY["z"]), WY["r_zew"])


class TestModele(unittest.TestCase):
    """Dane modeli Blendera (modele/dane, format /2) i próbkowanie klipów (zrodla/KlipyEwolucji.luau)."""

    @classmethod
    def setUpClass(cls):
        cls.I = DN.modele_wczytaj("indeks.json")
        cls.KL = IT.wykonaj(open(os.path.join(PAKIET, "zrodla", "KlipyEwolucji.luau"), encoding="utf-8").read(), "KlipyEwolucji")[0]

    def test_29_wczytanie_danych(self):
        I = self.I
        self.assertEqual(I["wersja"], 3)
        # indeks 3: w „stadia” tylko osiem stadiów (jajo pod kluczem „jajo”), nowe klucze efektów, wariantów i prędkości stworów
        self.assertEqual([S["nr"] for S in I["stadia"]], list(range(1, 9)))
        self.assertEqual(I["jajo"]["id"], "smok_jajo")
        self.assertEqual({E["id"] for E in I["efekty"]}, {"ogien_stozek", "przypalenie"})
        self.assertEqual(I["warianty_modeli"][0]["zamiast"], "smok_1")
        self.assertEqual(I["predkosc_stworow"]["owca"], {"chod": 1.76, "ucieczka": 5.0})
        self.assertEqual(len(I["stawy"]), 26)
        self.assertEqual(len(I["zaczepy"]), 13)
        self.assertEqual(len(I["regiony"]), 9)
        st = DN.stadia_smoka(I)
        self.assertEqual([S["promien_gry"] for S in st], [f["r"] for f in D["formy"]], "promienie stadiów = promienie gry")
        for S in st:
            R = DN.modele_wczytaj(S["pliki"][0])
            Lr = DN.modele_wczytaj(S["plik_lod"])
            K = DN.modele_wczytaj(S["pliki"][1])
            self.assertEqual([k[0] for k in R["kosci"]], I["stawy"], S["id"])
            self.assertEqual([k[0] for k in Lr["kosci"]], I["stawy"], "LOD: te same stawy")
            self.assertEqual(sorted(z[0] for z in R["zaczepy"]), sorted(I["zaczepy"]))
            self.assertEqual(sorted(z[0] for z in Lr["zaczepy"]), sorted(I["zaczepy"]), "LOD: te same zaczepy")
            self.assertEqual(len(R["czesci"]), S["czesci"])
            self.assertEqual(len(Lr["czesci"]), S["czesci_lod"])
            self.assertTrue(all(0 <= c[16] < 9 for c in R["czesci"] + Lr["czesci"]), "region 0–8")
            self.assertTrue(all(0 <= c[13] < len(R["materialy"]) for c in R["czesci"]), "materiał w tablicy")
            self.assertTrue(all(1 <= c[0] <= 26 for c in R["czesci"]), "kość części")
            self.assertEqual(K["stawy"], I["stawy"])
            nazwy = set(K["klipy"])
            self.assertTrue(set(I["klipy_podstawowe"]) | set(I["klipy_dodatkowe"]) <= nazwy, S["id"])
            for n, c in K["klipy"].items():
                self.assertEqual(len(c["probki"]), c["dl"] // c.get("krok", K["krok"]) + 1, n)
                self.assertTrue(all(len(w) == 3 * (len(c["stawy"]) + len(c["przes"])) for w in c["probki"]), n)
                self.assertTrue(set(c["zdarzenia"]) <= set(I["zdarzenia"]), n)
                self.assertTrue(all(0 <= k <= c["dl"] for k in c["zdarzenia"].values()), n)
            self.assertGreater(K["klipy"]["chod"]["predkosc"], 0)
            self.assertGreater(K["klipy"]["bieg"]["predkosc"], K["klipy"]["chod"]["predkosc"])
        # rigi do budowy: 8 × (pełny, uproszczony) + jajo + rekwizyty + stwory; klipy 8 + jajo + stwory
        U = DN.ustawienia()
        rigi, klipy = DN.modele_do_budowy(U)
        self.assertEqual(len([n for n, _ in rigi if n.startswith("SmokB_") and n != "SmokB_jajo"]), 16)
        self.assertIn("SmokB_jajo", [n for n, _ in rigi])
        self.assertIn("smok_jajo", [i for i, _ in klipy])
        # efekty z indeksu 3 i wybór pisklęcia (ustawienia: blender.piskle „obecne” | „lagodne”)
        R = dict(rigi)
        self.assertEqual(R["Efekt_ogien_stozek"], "ogien_stozek_rig.json")
        self.assertEqual(R["Rekwizyt_przypalenie"], "rekwizyt_przypalenie_rig.json")
        self.assertIn("ogien_stozek", [i for i, _ in klipy])
        self.assertEqual(R["SmokB_1"], "smok_1_rig.json" if U["blender"].get("piskle", "obecne") == "obecne" else "smok_1_lagodny_rig.json")
        U2 = json.loads(json.dumps(U))
        U2["blender"]["piskle"] = "lagodne"
        stary = DN.ustawienia
        DN.ustawienia = lambda: U2
        try:
            self.assertEqual(dict(DN.modele_do_budowy(U2)[0])["SmokB_1"], "smok_1_lagodny_rig.json")
        finally:
            DN.ustawienia = stary
        Rl = DN.modele_wczytaj("smok_1_lagodny_rig.json")
        self.assertEqual([k[0] for k in Rl["kosci"]], I["stawy"], "łagodne pisklę: te same stawy")
        # krótki koziołek i poza portretu w każdym stadium; chód 7 i bieg 18 studs/s
        for S in st:
            K = DN.modele_wczytaj(S["pliki"][1])["klipy"]
            self.assertEqual(K["koziolek"]["dl"], 14)
            self.assertIn("koziolek_dlugi", K)
            self.assertIn("portret", K)
            self.assertEqual((K["chod"]["predkosc"], K["bieg"]["predkosc"]), (7.0, 18.0), S["id"])
            # runda 6: chód i bieg co klatkę z oknami podporu (stopy NogaPL3, NogaPP3, NogaTL3, NogaTP3)
            for x in ("chod", "bieg"):
                self.assertEqual(K[x].get("krok"), 1, (S["id"], x))
                self.assertEqual(len(K[x]["podpor"]["start"]), 4)
                self.assertTrue(1 <= K[x]["podpor"]["klatki"] < K[x]["dl"])
        # serwer: zamach zdolności = zdarzenie w klipie stadium
        for i, F in enumerate(D["formy"]):
            K = DN.modele_wczytaj("smok_%d_klipy.json" % (i + 1))
            self.assertAlmostEqual(F["czasy"]["zar"], K["klipy"]["splun"]["zdarzenia"]["strzal"] / 30, places=2)
            self.assertAlmostEqual(F["czasy"]["ryk"], K["klipy"]["ryk"]["zdarzenia"]["ryk_start"] / 30, places=2)

    def test_30_probkowanie_klipow(self):
        J = DN.modele_wczytaj("smok_3_klipy.json")
        W = T_KL(self.KL, "przygotuj", J)
        k = W.get("klipy").get("chod")
        n = int(W.get("n"))
        poza = T_KL(self.KL, "nowaPoza", n)
        # Python: ta sama interpolacja liczb co w README (próbka co 2 klatki)
        c = J["klipy"]["chod"]
        for t in (0.0, 0.1, 0.37, c["dl"] / 30 + 0.05):
            T_KL(self.KL, "probka", W, k, t, poza)
            p = LM.z_luau(poza, True)
            tt = t % (c["dl"] / 30)
            f = tt * 30 / c.get("krok", J["krok"])
            a, u = int(math.floor(f)), f % 1
            A, B = c["probki"][min(a, len(c["probki"]) - 1)], c["probki"][min(a + 1, len(c["probki"]) - 1)]
            o = 0
            for i in c["stawy"]:
                b = (i - 1) * 6
                if i in c["przes"]:
                    for q in range(3):
                        self.assertAlmostEqual(p[b + q], (A[o + q] + (B[o + q] - A[o + q]) * u) / 1000, places=6)
                    o += 3
                for q in range(3):
                    self.assertAlmostEqual(p[b + 3 + q], A[o + q] + (B[o + q] - A[o + q]) * u, places=6)
                o += 3
        # mieszanie: kąty najkrótszą drogą (3590 → 10 przez 3600, nie wstecz)
        a, b = T_KL(self.KL, "nowaPoza", 1), T_KL(self.KL, "nowaPoza", 1)
        a.set(4.0, 3590.0)
        b.set(4.0, 10.0)
        T_KL(self.KL, "mieszaj", a, b, 0.5, 1)
        self.assertAlmostEqual(LM.z_luau(a.get(4.0)), 3600.0, places=6)
        # zdarzenia: gryz3 „ugryzienie” w swojej klatce; tempo chodu z prędkości
        g3 = W.get("klipy").get("gryz3")
        tz = J["klipy"]["gryz3"]["zdarzenia"]["ugryzienie"] / 30
        wyn = LM.z_luau(T_KL(self.KL, "zdarzenia", g3, tz - 0.05, tz + 0.01, LM.Tabela()), True)
        self.assertEqual(wyn, ["ugryzienie"])
        self.assertEqual(LM.z_luau(T_KL(self.KL, "zdarzenia", g3, tz + 0.01, tz + 0.2, LM.Tabela()), True), [])
        bieg = W.get("klipy").get("bieg")
        self.assertAlmostEqual(T_KL(self.KL, "tempo", bieg, J["klipy"]["bieg"]["predkosc"], 1.0, 0.5, 3.0), 1.0, places=6)
        self.assertEqual(T_KL(self.KL, "tempo", bieg, 100.0, 1.0, 0.5, 2.4), 2.4, "granica tempa")
        # ogon_zamach przechodzi przez 360° — liczby, nie CFrame
        oz = J["klipy"]["ogon_zamach"]
        maks = max(abs(v) for w in oz["probki"] for v in w)
        self.assertGreater(maks, 1800, "obrót ciała w ogon_zamach (dziesiąte stopnia)")


class TestRuchIIkony(unittest.TestCase):
    """Dane 3 i interfejs1: tempo chodu i biegu z prędkości po ziemi (bez poślizgu stóp), zastępstwa ikon."""

    @classmethod
    def setUpClass(cls):
        cls.KL = IT.wykonaj(open(os.path.join(PAKIET, "zrodla", "KlipyEwolucji.luau"), encoding="utf-8").read(), "KlipyEwolucji")[0]

    def test_33_chod_bieg_z_predkosci(self):
        KL = self.KL
        LOD = D["blender"]["lod"]
        for nr in range(1, 9):
            J = DN.modele_wczytaj("smok_%d_klipy.json" % nr)
            W = T_KL(KL, "przygotuj", J)
            vc, vb = J["klipy"]["chod"]["predkosc"], J["klipy"]["bieg"]["predkosc"]
            prog = math.sqrt(vc * vb)

            def wybor(v, pop=None):
                o = lu({"skala": 1, "mn": LOD["tempo_min"], "mx": LOD["tempo_maks"], "hist": LOD["bieg_hist"]})
                r = IT.wywolaj(KL.get("chodBieg"), [W, float(v), pop, o])
                return r[0], r[1]
            self.assertEqual(wybor(0.5)[0], "spoczynek")
            # szybkości gry: chód przy wolnym ruchu, bieg przy 16–26 studs/s; stopa w podporze stoi: v = tempo × predkosc
            for v, nazwa in ((3, "chod"), (7, "chod"), (11, "chod"), (14, "bieg"), (16, "bieg"), (22, "bieg"), (26, "bieg")):
                n, t = wybor(v)
                self.assertEqual(n, nazwa, (nr, v))
                pk = vc if n == "chod" else vb
                self.assertAlmostEqual(t * pk, v, places=6, msg="poślizg stopy przy %s studs/s (stadium %d)" % (v, nr))
            # histereza wokół środka geometrycznego (≈11,2): bez migotania chód ↔ bieg
            h = LOD["bieg_hist"]
            self.assertEqual(wybor(prog + h * 0.5, "chod")[0], "chod")
            self.assertEqual(wybor(prog + h * 1.2, "chod")[0], "bieg")
            self.assertEqual(wybor(prog - h * 0.5, "bieg")[0], "bieg")
            self.assertEqual(wybor(prog - h * 1.2, "bieg")[0], "chod")
            # granice tempa nie obcinają zakresu prędkości gry (16–26 studs/s, ulepszenie SPEED)
            for v in D["ulepszenia"][1]["wartosci"]:
                self.assertTrue(LOD["tempo_min"] <= v / vb <= LOD["tempo_maks"], v)
        # owca i golem: własne predkosc (owca: ucieczka przy 13 studs/s → tempo 2,6)
        Jo = DN.modele_wczytaj("owca_klipy.json")
        Wo = T_KL(KL, "przygotuj", Jo)
        self.assertAlmostEqual(T_KL(KL, "tempo", Wo.get("klipy").get("ucieczka"), 13.0, 1.0, 0.3, 3.0) * 5.0, 13.0, places=6)
        self.assertAlmostEqual(T_KL(KL, "tempo", Wo.get("klipy").get("chod"), 5.0, 1.0, 0.3, 3.0) * 1.76, 5.0, places=6)
        Jg = DN.modele_wczytaj("golem_3_klipy.json")
        Wg = T_KL(KL, "przygotuj", Jg)
        n, t = IT.wywolaj(KL.get("chodBieg"), [Wg, 9.0, None, lu({"skala": 1, "mn": 0.1, "mx": 3})])[:2]
        self.assertEqual(n, "chod", "golem nie ma biegu")
        self.assertAlmostEqual(t * Jg["klipy"]["chod"]["predkosc"], 9.0, places=6)

    def test_34_ikony_i_zastepstwa(self):
        U = DN.ustawienia()
        ids = U["ikony"]["id"]
        # 24 ikony z modele/README.md (runda 4), wszystkie na razie bez numeru
        oczek = ["bite", "dash", "ember_spit", "fire_breath", "inferno_breath", "tail_sweep", "wing_glide", "roar", "meteor_dive", "zablokowane",
                 "moneta", "skarb", "kula_mala", "kula_duza", "kula_wielka", "wariant_gold", "wariant_crystal", "wariant_ruby", "wariant_rainbow",
                 "korona", "ulepszenie_jaw", "ulepszenie_speed", "ulepszenie_appetite", "czaszka"]
        self.assertEqual(sorted(ids), sorted(oczek))
        self.assertEqual(D["ikony"], ids)
        for linia in ("ogien", "moc"):
            for A in D["zdolnosci"][linia]:
                self.assertIn(A["ikona"], ids, A["id"])
                self.assertTrue(A.get("opis"), A["id"])
        for W in D["warianty"]:
            self.assertIn(W["ikona"], ids)
        for Up in D["ulepszenia"]:
            self.assertIn(Up["ikona"], ids)
        src = open(os.path.join(PAKIET, "zrodla", "IkonyEwolucji.luau"), encoding="utf-8").read()
        I = IT.wykonaj(src, "IkonyEwolucji")[0]
        opak = IT.wykonaj("return function(I, ids, n, ma, napis) return I.wybierz(ids, n, function(x) return ma end, napis) end", "opak")[0]

        def wybierz(tab, n, ma=True, napis=None):
            return LM.z_luau(IT.wywolaj(opak, [I, lu(tab), n, ma, napis])[0])
        typy = {}
        for n in oczek:
            w = wybierz(ids, n)
            self.assertNotEqual(w["typ"], "obraz", n)
            typy[n] = w["typ"]
        # zastępstwa: modele 3D z wzorców (kule, kopiec złota), moneta i korona z części, kłódka i romby rysowane, reszta napis
        self.assertEqual({n for n, t in typy.items() if t == "wzorzec"}, {"skarb", "kula_mala", "kula_duza", "kula_wielka"})
        self.assertEqual({n for n, t in typy.items() if t == "model"}, {"moneta", "korona"})
        self.assertEqual({n for n, t in typy.items() if t == "rysunek"}, {"zablokowane", "wariant_gold", "wariant_crystal", "wariant_ruby", "wariant_rainbow"})
        self.assertEqual(wybierz(ids, "roar", True, "ROAR")["napis"], "ROAR")
        # bez wzorca w grze → napis zapasowy na płytce
        self.assertEqual(wybierz(ids, "kula_mala", False), {"typ": "napis", "napis": "ORB"})
        # po wpisaniu numeru: obraz bez zmiany kodu (liczba albo napis rbxassetid)
        ids2 = dict(ids, bite=123456, roar="rbxassetid://987")
        self.assertEqual(wybierz(ids2, "bite"), {"typ": "obraz", "wartosc": "rbxassetid://123456"})
        self.assertEqual(wybierz(ids2, "roar")["wartosc"], "rbxassetid://987")
        self.assertEqual(IT.wywolaj(I.get("ileObrazow"), [lu(ids2)])[0], 2)
        self.assertEqual(IT.wywolaj(I.get("ileObrazow"), [lu(ids)])[0], 0)
        # nieznana nazwa → napis z nazwy
        self.assertEqual(wybierz(ids, "cos_nowego")["typ"], "napis")


class TestOdrodzenie(unittest.TestCase):
    """odrodzenie1: REBIRTH (mnożnik, linie, trofea), migawka linii, wydarzenia zegarowe, jajo dnia, zapis nowych pól."""

    def test_35_odrodzenie_i_mnoznik(self):
        S = stan()
        bez_kulek(S)
        NF = len(D["formy"])
        O = D["odrodzenie"]
        gr = byt(S, 1, 3, 0, 0)
        lista = LM.Tabela()
        self.assertFalse(jeden("odrodzenie", S, gr, lista), "tylko na ANCIENT")
        ustaw(gr, forma=NF, maxForma=NF, zloto=777)
        gr.set("warianty", LM.do_luau({}))
        gr.get("warianty").set(3.0, "zloty")
        przed = jeden("stawkaB", DL, gr)
        self.assertTrue(jeden("odrodzenie", S, gr, lista))
        ev = [z for z in LM.z_luau(lista, True) if z["t"] == "odr_start"]
        self.assertEqual((ev[0]["linia"], ev[0]["n"]), (2, 1))
        self.assertTrue(jeden("sterowanyPrzezSerwer", S, gr), "ceremonia: serwer prowadzi")
        zd = krok(S, int(O["ceremonia_s"] / 0.1) + 2, 0.1)
        self.assertTrue([z for z in zd if z["t"] == "odr_koniec" and z["linia"] == 2])
        self.assertEqual((g(gr, "forma"), g(gr, "maxForma"), g(gr, "linia"), g(gr, "odrodzenia"), g(gr, "zloto") >= 777), (1, 1, 2, 1, True))
        # trofea linii 1 zostają (8 stadiów, wariant) i zarabiają × 1,25
        self.assertEqual(g(gr, "linie")[0]["maxForma"] if isinstance(g(gr, "linie"), list) else g(gr, "linie")["1"]["maxForma"], NF)
        self.assertAlmostEqual(jeden("mnoznikOdr", DL, gr), O["x"], places=6)
        self.assertAlmostEqual(jeden("stawkaB", DL, gr), (przed + D["formy"][0]["trofeum"]) * O["x"], places=4)
        # wzrost × mnożnik
        ustaw(gr, wzrost=0)
        wolaj("dodajWzrost", S, gr, 10)
        self.assertAlmostEqual(g(gr, "wzrost"), 10 * O["x"], places=6)
        # mnożnik z sufitem; linie po kolei, po ostatniej znów pierwsza
        ustaw(gr, odrodzenia=50)
        self.assertAlmostEqual(jeden("mnoznikOdr", DL, gr), O["maks_x"], places=6)
        self.assertEqual([jeden("liniaPo", DL, l) for l in (1, 2, 3, 4)], [2, 3, 4, 1])

    def test_36_linie_kolory_i_migawka(self):
        L4 = D["odrodzenie"]["linie"]
        self.assertEqual([x["id"] for x in L4], ["ember", "frost", "storm", "shadow"])
        regiony = {"cialo", "luski", "brzuch", "blona", "kolce", "zar", "zar_rdzen"}
        self.assertIsNone(L4[0].get("paleta"), "EMBER = dzisiejsze kolory")
        for x in L4[1:]:
            self.assertEqual(set(x["paleta"]), regiony, x["id"])
            self.assertTrue(all(len(v) == 6 and int(v, 16) >= 0 for v in x["paleta"].values()))
        # bajt migawki: wariant 0–4 i linia 1–4 w jednym bajcie, tam i z powrotem
        for nr in range(0, 5):
            for linia in range(1, 5):
                bajt = jeden("kodWariantu", nr, linia)
                self.assertTrue(0 <= bajt <= 255)
                self.assertEqual(wolaj("dekodWariantu", bajt)[:2], [nr, linia])

    def test_37_wydarzenia_zegarowe(self):
        S = stan()
        W = D["wydarzenia"]
        gr = byt(S, 1, 3, 0, 0)
        bez_kulek(S)
        # zegar UTC tuż przed oknem deszczu: start dokładnie raz, w tym samym miejscu rozkładu na każdym serwerze
        Wd = W["deszcz"]
        t0 = 20000 * 86400 + Wd["przesun_s"] + 5 * Wd["co_s"] - 30
        S.set("zegar", float(t0))
        self.assertEqual(wolaj("oknoWydarzenia", lu(Wd), t0)[:3], [False, 0, 30])
        self.assertEqual(wolaj("oknoWydarzenia", lu(Wd), t0 + 40)[:2], [True, Wd["trwa_s"] - 10])
        zd = []
        for _ in range(25):
            S.set("zegar", S.get("zegar") + 2.0)
            zd += krok(S, 1, 2.0)
        start = [z for z in zd if z["t"] == "wydarzenie" and z["co"] == "deszcz" and z.get("start")]
        self.assertEqual(len(start), 1, "deszcz z zegara UTC")
        E = LM.z_luau(S.get("wyd"))
        self.assertIsNotNone(E.get("deszczDo"))
        k = LM.z_luau(S.get("kulki"), True)
        zywe = [i for i, v in enumerate(k) if v == 0]
        self.assertGreater(len(zywe), 20, "kule łąki od razu żywe")
        # kula w deszczu: wzrost × wzrost_x i złoto
        ustaw(gr, wzrost=0, zloto=0)
        i = zywe[0] + 1
        pk = D["kulkiPoz"][i - 1]
        ustaw(gr, x=pk[0], z=pk[1])
        krok(S, 1)
        self.assertGreaterEqual(g(gr, "zloto"), W["deszcz"]["zloto"])
        self.assertGreater(g(gr, "wzrost"), 0)
        zd = []
        for _ in range(int(W["deszcz"]["trwa_s"] / 2) + 2):
            S.set("zegar", S.get("zegar") + 2.0)
            zd += krok(S, 1, 2.0)
        self.assertTrue([z for z in zd if z["t"] == "wydarzenie" and z["co"] == "deszcz" and z.get("koniec")])
        E2 = LM.z_luau(S.get("wyd"))
        self.assertAlmostEqual(E2["deszczNast"] - LM.z_luau(S.get("czas")), Wd["co_s"] - (S.get("zegar") - Wd["przesun_s"]) % Wd["co_s"], delta=0.01)
        # rampage wymuszony z jednym graczem: golem wychodzi z lasu, trafienie → dzielona skrzynia
        wolaj("dodajBossa", S)
        wolaj("wymusWydarzenie", S, "rampage")
        zd = krok(S, 1)
        st = [z for z in zd if z["t"] == "wydarzenie" and z["co"] == "rampage" and z.get("start")]
        self.assertTrue(st)
        boss = jeden("bytPoId", S, S.get("boss"))
        self.assertFalse(jeden("wLesie", DL, g(boss, "x"), g(boss, "z")), "golem na łące")
        self.assertEqual(g(boss, "strefa"), 3)
        zl = g(gr, "zloto")
        lista = LM.Tabela()
        wolaj("ranBossa", S, boss, gr, g(boss, "hp") + 1, lista)
        sk = [z for z in LM.z_luau(lista, True) if z["t"] == "rampage_skrzynia"]
        self.assertTrue(sk and sk[0]["ile"] == 1)
        dzial = int(D["boss"]["stopnie_skrzynia"][st[0]["stopien"] - 1] * W["rampage"]["pula_x"])
        self.assertEqual(g(gr, "zloto") - zl, dzial)
        zd = krok(S, 2)
        self.assertTrue([z for z in zd if z["t"] == "wydarzenie" and z["co"] == "rampage" and z.get("koniec")])
        self.assertEqual(g(boss, "strefa"), 2)
        zd = krok(S, 20)
        self.assertFalse([z for z in zd if z["t"] == "wydarzenie" and z["co"] == "rampage" and z.get("start")], "po pokonaniu bez wznowienia")

    def test_38_jajo_dnia(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 4, 0, 0)
        ustaw(gr, maxForma=4)
        dzien = 20000 * 86400 + 3600
        self.assertEqual(jeden("dzienUTC", dzien), 20000)
        self.assertEqual(jeden("dzienUTC", dzien + 86400 - 3601 - 1), 20000)
        r = wolaj("jajoDnia", S, gr, dzien, 0.1)
        self.assertEqual(r[:2], [False, "legowisko"], "tylko w legowisku")
        lx, lz = wolaj("legowiskoPoz", DL, 1)[:2]
        ustaw(gr, x=lx, z=lz)
        r = wolaj("jajoDnia", S, gr, dzien, 0.1)
        self.assertTrue(r[0])
        self.assertEqual((r[1], r[2], r[3]), ("zloty", True, 4))
        self.assertEqual(LM.z_luau(gr.get("warianty").get(4.0)), "zloty")
        self.assertEqual(wolaj("jajoDnia", S, gr, dzien + 3000, 0.99)[:2], [False, "jutro"], "raz na dzień UTC")
        self.assertTrue(jeden("jajoDostepne", DL, gr, dzien + 86400))
        r = wolaj("jajoDnia", S, gr, dzien + 86400, 0.99)
        self.assertEqual((r[0], r[1], r[2]), (True, "tecza", True))
        r = wolaj("jajoDnia", S, gr, dzien + 2 * 86400, 0.0)
        self.assertEqual((r[1], r[2]), ("zloty", False), "gorszy wariant nie zastępuje")

    def test_39_zapis_odrodzen(self):
        S = stan()
        bez_kulek(S)
        NF = len(D["formy"])
        gr = byt(S, 1, NF, 0, 0)
        ustaw(gr, maxForma=NF, dzienJaja=20001)
        lista = LM.Tabela()
        self.assertTrue(jeden("odrodzenie", S, gr, lista))
        krok(S, int(D["odrodzenie"]["ceremonia_s"] / 0.1) + 2, 0.1)
        ustaw(gr, maxForma=3)
        P = jeden("doProfilu", DL, gr, 1000)
        surowe = json.loads(json.dumps(LM.z_luau(P)))
        self.assertEqual((surowe["odrodzenia"], surowe["linia"], surowe["dzienJaja"]), (1, 2, 20001))
        self.assertEqual(surowe["linie"]["1"]["maxForma"], NF)
        p2 = jeden("profilZ", DL, lu(surowe))
        b2 = byt(S, 2, 1, 50, 50)
        wolaj("zProfilu", DL, b2, p2, 1000)
        self.assertEqual((g(b2, "odrodzenia"), g(b2, "linia"), g(b2, "maxForma"), g(b2, "dzienJaja")), (1, 2, 3, 20001))
        self.assertAlmostEqual(jeden("stawkaB", DL, b2), jeden("stawkaB", DL, gr), places=4)
        # złe dane: liczby przycięte, obecna linia nie wraca jako zarchiwizowana, nieznany wariant → pusty
        zle = dict(surowe, odrodzenia=-5, linia=99, dzienJaja="x")
        zle["linie"] = {"2": {"maxForma": 99, "warianty": ["hack"], "trofea": [9]}}
        p3 = LM.z_luau(jeden("profilZ", DL, lu(zle)))
        self.assertEqual((p3["odrodzenia"], p3["linia"], p3["dzienJaja"]), (0, 4, -1))
        self.assertEqual(p3["linie"]["2"]["maxForma"], NF)
        self.assertEqual(p3["linie"]["2"]["warianty"][0], "")
        self.assertEqual(p3["linie"]["2"]["trofea"][0], len(D["legowisko"]["poziomy_x"]))


class TestRetencja(unittest.TestCase):
    """retencja1: seria logowań (7 dni), zadania dnia (pula, postęp ze zdarzeń, reset UTC), zapis w wersji 2."""

    def test_40_seria_logowan(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 2, 0, 0)
        ustaw(gr, maxForma=5, zloto=0)
        N = D["seria"]["nagrody"]
        d0 = 20000 * 86400 + 5000
        r = LM.z_luau(jeden("logowanie", DL, gr, d0, 0.1))
        self.assertEqual((r["dni"], g(gr, "zloto")), (1, N[0]["zloto"]))
        r = LM.z_luau(jeden("logowanie", DL, gr, d0 + 3600, 0.1))
        self.assertEqual(r["dni"], 1)
        self.assertIsNone(r.get("nagroda"), "ten sam dzień: bez drugiej nagrody")
        zl = g(gr, "zloto")
        for k in range(2, 8):
            r = LM.z_luau(jeden("logowanie", DL, gr, d0 + (k - 1) * 86400, 0.01))
            self.assertEqual(r["dni"], k)
        self.assertEqual(g(gr, "zloto") - zl, sum(x.get("zloto", 0) for x in N[1:]))
        self.assertEqual(g(gr, "boostS"), sum(x.get("boost_s", 0) for x in N))
        self.assertEqual((r["wariant"], r["f"], r["lepszy"]), ("zloty", 5, True), "dzień 7: wariant najwyższego trofeum")
        r = LM.z_luau(jeden("logowanie", DL, gr, d0 + 7 * 86400, 0.5))
        self.assertEqual(r["dni"], 1, "po 7. dniu znów 1.")
        r = LM.z_luau(jeden("logowanie", DL, gr, d0 + 9 * 86400, 0.5))
        self.assertEqual(r["dni"], 1, "przerwa: od 1")
        # przyspieszenie: wzrost × boost_x, maleje z czasem gry
        ustaw(gr, wzrost=0, boostS=10)
        wolaj("dodajWzrost", S, gr, 4)
        self.assertAlmostEqual(g(gr, "wzrost"), 4 * D["seria"]["boost_x"], places=6)
        krok(S, 5, 0.1)
        self.assertAlmostEqual(g(gr, "boostS"), 9.5, places=6)

    def test_41_zadania_dnia(self):
        Z = D["zadania"]
        a = LM.z_luau(jeden("losujZadania", DL, 20001, 77, 8))
        b = LM.z_luau(jeden("losujZadania", DL, 20001, 77, 8))
        c = LM.z_luau(jeden("losujZadania", DL, 20002, 77, 8))
        self.assertEqual(a, b, "ten sam dzień i gracz: te same zadania")
        self.assertEqual(len(a["lista"]), Z["ile"])
        self.assertEqual(len({q["id"] for q in a["lista"]}), Z["ile"], "bez powtórzeń")
        self.assertNotEqual([q["id"] for q in a["lista"]], [q["id"] for q in c["lista"]])
        for d in range(20000, 20040):
            l1 = LM.z_luau(jeden("losujZadania", DL, d, 5, 1))
            self.assertFalse({q["id"] for q in l1["lista"]} & {"wyspa", "boss", "zdolnosci"}, "zadania od formy")
        # postęp ze zdarzeń kroku: kulki i owce gracza, nagroda złoto + wzrost, zdarzenie „zadanie”
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 2, 0, 0)
        ustaw(gr, maxForma=2, zloto=0, wzrost=0)
        gr.set("zadania", lu({"dzien": 20001, "lista": [{"id": "kulki", "cel": 3, "postep": 0, "gotowe": False},
                                                         {"id": "owce", "cel": 4, "postep": 0, "gotowe": False}]}))
        zd = []
        for i in range(3):
            lista = LM.Tabela()
            lista.set(1.0, lu({"t": "kulka", "i": i + 1, "id": g(gr, "id"), "s": 1}))
            wolaj("krokZadan", S, 0.05, lista)
            zd += LM.z_luau(lista, True)
        gotowe = [z for z in zd if z["t"] == "zadanie"]
        Q = next(q for q in Z["pula"] if q["id"] == "kulki")
        self.assertEqual(len(gotowe), 1)
        self.assertEqual((gotowe[0]["zad"], g(gr, "zloto")), ("kulki", Q["zloto"]))
        self.assertAlmostEqual(g(gr, "wzrost"), Q["wzrost"] * D["formy"][1]["potrzeba"], places=6)
        # nowy dzień UTC: nowe zadania, zdarzenie „zadania_nowe”
        S.set("zegar", float(20002 * 86400 + 10))
        lista = LM.Tabela()
        wolaj("krokZadan", S, 0.05, lista)
        self.assertTrue([z for z in LM.z_luau(lista, True) if z["t"] == "zadania_nowe"])
        self.assertEqual(LM.z_luau(gr.get("zadania"))["dzien"], 20002)

    def test_42_zapis_v2_i_migracja(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 3, 0, 0)
        ustaw(gr, maxForma=3, pierwszy=1700000000)
        jeden("logowanie", DL, gr, 20003 * 86400 + 7, 0.3)
        zad = gr.get("zadania").get("lista").get(1.0)
        zad.set("postep", 1.0)
        ustaw(gr, boostS=123.4)
        P = LM.z_luau(jeden("doProfilu", DL, gr, 1000))
        self.assertEqual((P["wersja"], P["seria"], P["boostS"]), (D["zapis"]["wersja"], {"dzien": 20003, "dni": 1}, 123))
        self.assertEqual(len(P["zadania"]["lista"]), D["zadania"]["ile"])
        surowe = json.loads(json.dumps(P))
        b2 = byt(S, 2, 1, 50, 50)
        wolaj("zProfilu", DL, b2, jeden("profilZ", DL, lu(surowe)), 1000)
        self.assertEqual(LM.z_luau(b2.get("seria")), {"dzien": 20003, "dni": 1})
        self.assertEqual(LM.z_luau(b2.get("zadania"))["lista"][0]["postep"], 1)
        self.assertEqual(g(b2, "ziarno"), 1700000000 % 100003)
        # migracja: zapis w wersji 1 (bez nowych pól) → domyślne; zły wpis zadania odrzucony
        v1 = {"wersja": 1, "zloto": 50, "maxForma": 4, "poziomy": {"szczeka": 2}}
        p1 = LM.z_luau(jeden("profilZ", DL, lu(v1)))
        self.assertEqual((p1["wersja"], p1["seria"], p1["boostS"], p1["zadania"]["dzien"], p1["zloto"]), (D["zapis"]["wersja"], {"dzien": -1, "dni": 0}, 0, -1, 50))
        zle = dict(surowe, seria={"dzien": "x", "dni": 99}, boostS=-5)
        zle["zadania"] = {"dzien": 20003, "lista": [{"id": "hack", "postep": 5}, {"id": "kulki", "postep": 999, "gotowe": True}]}
        p3 = LM.z_luau(jeden("profilZ", DL, lu(zle)))
        self.assertEqual((p3["seria"]["dzien"], p3["seria"]["dni"], p3["boostS"]), (-1, len(D["seria"]["nagrody"]), 0))
        self.assertEqual([q["id"] for q in p3["zadania"]["lista"]], ["kulki"])
        self.assertEqual(p3["zadania"]["lista"][0]["postep"], next(q for q in D["zadania"]["pula"] if q["id"] == "kulki")["cel"])


class TestSklep(unittest.TestCase):
    """odczucie1: sklep (flaga wyłączona) — produkty po numerze, nagroda i cofnięcie, paragony (idempotencja), przepustki,
    zapis paragonów; bez płatnych losowań."""

    def test_43_sklep_logika(self):
        SK = D["sklep"]
        self.assertFalse(SK["wlaczony"], "flaga sklepu wyłączona")
        self.assertFalse(jeden("sklepWidoczny", DL), "bez przycisku SHOP")
        self.assertTrue(all(x["product_id"] == 0 for x in SK["produkty"]) and all(x["pass_id"] == 0 for x in SK["przepustki"]), "nic nie utworzono")
        ids = {x["id"] for x in SK["produkty"]} | {x["id"] for x in SK["przepustki"]}
        self.assertFalse({i for i in ids if "jaj" in i or "wariant" in i or "los" in i}, "bez płatnych losowań")
        self.assertIsNone(jeden("produktPoId", DL, 0), "numer 0 = ukryty")
        # numery tylko w kopii danych testu (ustawienia.json zostają z zerami)
        D2 = json.loads(json.dumps(D))
        D2["sklep"]["produkty"][0]["product_id"] = 111
        D2["sklep"]["produkty"][3]["product_id"] = 444
        D2["sklep"]["wlaczony"] = True
        DL2 = lu(D2)
        self.assertTrue(jeden("sklepWidoczny", DL2))
        P1 = jeden("produktPoId", DL2, 111)
        self.assertEqual(LM.z_luau(P1)["zloto"], 1000)
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 2, 0, 0)
        ustaw(gr, zloto=50, boostS=0)
        cof = jeden("przyznajProdukt", DL2, gr, P1)
        self.assertEqual(g(gr, "zloto"), 1050)
        wolaj("zapamietajParagon", DL2, gr, "abc-1")
        self.assertTrue(jeden("paragonZnany", gr, "abc-1"))
        self.assertFalse(jeden("paragonZnany", gr, "abc-2"))
        wolaj("cofnijProdukt", gr, cof)
        wolaj("zapomnijParagon", gr, "abc-1")
        self.assertEqual((g(gr, "zloto"), jeden("paragonZnany", gr, "abc-1")), (50, False), "cofnięcie po błędzie zapisu")
        jeden("przyznajProdukt", DL2, gr, jeden("produktPoId", DL2, 444))
        self.assertEqual(g(gr, "boostS"), 900)
        # lista paragonów przycięta do paragony_max
        D2["sklep"]["paragony_max"] = 3
        DL3 = lu(D2)
        for i in range(6):
            wolaj("zapamietajParagon", DL3, gr, "p%d" % i)
        self.assertEqual(LM.z_luau(gr.get("paragony"), True), ["p3", "p4", "p5"])
        # przepustki: 2x GROWTH na wzrost, VIP ×1,5 na złoto legowiska
        ustaw(gr, wzrost=0, boostS=0, maxForma=2)
        przed = jeden("stawkaB", DL, gr)
        gr.set("przepustki", lu({"wzrost2x": True, "vip": True}))
        wolaj("dodajWzrost", S, gr, 3)
        self.assertAlmostEqual(g(gr, "wzrost"), 6, places=6)
        self.assertAlmostEqual(jeden("stawkaB", DL, gr), przed * 1.5, places=6)
        # zapis: paragony w profilu (napisy, przycięte), złe wpisy odrzucone
        P = LM.z_luau(jeden("doProfilu", DL, gr, 1000))
        self.assertEqual(P["paragony"], ["p3", "p4", "p5"])
        zle = dict(P, paragony=["ok", 5, "x" * 99])
        self.assertEqual(LM.z_luau(jeden("profilZ", DL, lu(zle)))["paragony"], ["ok"])


class TestMapa2(unittest.TestCase):
    """mapa2a: mapa v2 na płaskiej ziemi — obszar ze stref, bramy rozmiaru, głębia, woda, kryjówki, rzeczy do rozbicia, sekrety dnia."""

    def setUp(self):
        if not D.get("mapa2"):
            self.skipTest("bez mapy v2")
        self.roz = DL.get("mapa2").get("rozbite")
        for q in D["mapa2"]["lamliwe"]:
            self.roz.set(q["id"], None)

    def tearDown(self):
        for q in D["mapa2"]["lamliwe"]:
            self.roz.set(q["id"], None)

    def og(self, x, z, r, m=1):
        return wolaj("ogranicz", DL, float(x), float(z), float(r), float(m))

    def test_44_bramy_glebia_woda(self):
        # tunel Grzbietu Nory (B02): pisklę przechodzi, DRAGON (r 5,2) nie
        x, z = self.og(58, 24, 1.6)
        self.assertLess(math.hypot(x - 58, z - 24), 0.5, "pisklę w tunelu")
        x, z = self.og(58, 24, 5.2)
        self.assertGreater(math.hypot(x - 58, z - 24), 6, "duży smok wypchnięty z bramy")
        # każda brama zamknięta dla większych niż r_maks
        for b in D["mapa2"]["bramy"]:
            x, z = self.og(b["x"], b["z"], b["r_maks"] + 1.5)
            self.assertGreater(math.hypot(x - b["x"], z - b["z"]), 2, "brama %s zamknięta dla większych" % b["id"])
        # głębia jeziora: środek wypchnięty, bród i wysepka dozwolone
        x, z = self.og(-15, -214, 1.6)
        self.assertGreater(math.hypot(x - 8, z + 214), 28, "głęboka woda → brzeg")
        x, z = self.og(3, -219, 1.6)
        self.assertLess(math.hypot(x - 10, z + 224), 7.1, "głęboka woda obok wysepki → wysepka")
        for (px, pz) in ((10, -224), (22.5, -204.5)):
            x, z = self.og(px, pz, 1.6)
            self.assertLess(math.hypot(x - px, z - pz), 0.5, "wysepka / bród")
        # woda × 0,7, most szybki
        self.assertAlmostEqual(jeden("wodaX", DL, -13.0, -97.0), D["mapa2"]["woda_x"])
        self.assertEqual(jeden("wodaX", DL, -37.0, -2.0), 1, "most")
        self.assertEqual(jeden("wodaX", DL, 50.0, 50.0), 1, "łąka")
        self.assertGreater(jeden("podestY", DL, -37.0, -2.0), 1.0, "most wyżej (obraz)")
        # nowe strefy chodzone (pisklę): polana za łukiem, jezioro, wąwóz bramy
        for (px, pz) in ((148, 106), (30, -200), (190, -52)):
            x, z = self.og(px, pz, 1.6)
            self.assertLess(math.hypot(x - px, z - pz), 3, "strefa chodzona (%s, %s)" % (px, pz))
        # strefy rzeźby niedostępne (A): kanion, kotlina wodospadu, kaldera
        for (px, pz) in ((-200, 30), (-164, 126), (-318, -96)):
            x, z = self.og(px, pz, 1.6)
            self.assertGreater(math.hypot(x - px, z - pz), 10, "strefa rzeźby zamknięta (%s, %s)" % (px, pz))

    def test_45_kryjowki_lamliwe_sekrety(self):
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 1, 46, 8)
        ustaw(gr, x=46, z=8, tarczaDo=0)
        self.assertTrue(jeden("ukryty", S, gr), "pisklę w wysokiej trawie")
        bot = byt(S, 0, 3, 46, 20)
        ustaw(bot, x=46, z=20)
        wolaj("mysl", S, bot, lu([]))
        self.assertNotEqual(g(bot, "cel"), g(gr, "id"), "bot dalej niż 8 st. gubi ukrytego")
        ustaw(gr, gryzGotowy=0)
        jeden("gryz", S, gr, lu([]))
        self.assertFalse(jeden("ukryty", S, gr), "atak odkrywa")
        duzy = byt(S, 2, 6, 46, 8)
        ustaw(duzy, x=46, z=8)
        self.assertFalse(jeden("ukryty", S, duzy), "WAR DRAGON się nie mieści")
        # L06 (wyłom do Szlaku Popiołu): stadium 5 — podpowiedź, stadium 6 — rozbija, złoto, przejście, odrost
        S = stan()
        bez_kulek(S)
        gr = byt(S, 1, 5, -113.0, -102.4)
        ustaw(gr, x=-113.0, z=-102.4, tarczaDo=0, gryzGotowy=0)
        zd = lu([])
        jeden("gryz", S, gr, zd)
        self.assertIn("lamliwa_mala", [e["t"] for e in LM.z_luau(zd, True)])
        x, z = self.og(-122.9, -102.4, 1.6)
        self.assertGreater(math.hypot(x + 122.9, z + 102.4), 3, "skała blokuje szlak")
        x, z = self.og(-122.9, -92.5, 1.6)
        self.assertGreater(math.hypot(x + 122.9, z + 92.5), 1, "bez szpary przy ścianie korytarza")
        ustaw(gr, forma=6, zloto=0)
        zdarz = []
        for _ in range(80):
            ustaw(gr, gryzGotowy=0, x=-113.0, z=-102.4)
            zd = lu([])
            jeden("gryz", S, gr, zd)
            zdarz += LM.z_luau(zd, True)
            if any(e["t"] == "lamliwa_rozbita" for e in zdarz):
                break
        self.assertTrue(any(e["t"] == "lamliwa_rozbita" for e in zdarz), "L06 rozbita")
        self.assertEqual(g(gr, "zloto"), 60)
        x, z = self.og(-122.9, -102.4, 1.6)
        self.assertLess(math.hypot(x + 122.9, z + 102.4), 0.5, "szlak otwarty")
        ustaw(S, czas=g(S, "czas") + 200)
        zd = lu([])
        wolaj("krokLamliwych", S, zd)
        self.assertIn("lamliwa_odrost", [e["t"] for e in LM.z_luau(zd, True)])
        # sekret dnia: paszcza czaszki (S02) raz na dzień UTC, zapis v3
        S = stan()
        bez_kulek(S)
        ustaw(S, zegar=20003 * 86400 + 100)
        s02 = [s for s in D["mapa2"]["sekrety"] if s["id"] == "S02"][0]
        gr = byt(S, 1, 1, s02["x"], s02["z"])
        ustaw(gr, zloto=0, x=s02["x"], z=s02["z"], tarczaDo=0)
        zd = lu([])
        wolaj("krokSekretow", S, gr, zd)
        wolaj("krokSekretow", S, gr, zd)
        self.assertEqual(g(gr, "zloto"), s02["zloto"], "raz na dzień")
        ustaw(S, zegar=20004 * 86400 + 100)
        wolaj("krokSekretow", S, gr, zd)
        self.assertEqual(g(gr, "zloto"), 2 * s02["zloto"], "następny dzień UTC")
        P = LM.z_luau(jeden("doProfilu", DL, gr, 1000))
        self.assertEqual((P["wersja"], P["sekrety"]), (3, {"dzien": 20004, "lista": ["S02"]}))
        p2 = LM.z_luau(jeden("profilZ", DL, lu(dict(P, sekrety={"dzien": 20004, "lista": ["S02", "S99", 5]}))))
        self.assertEqual(p2["sekrety"]["lista"], ["S02"], "tylko znane sekrety")
        p3 = LM.z_luau(jeden("profilZ", DL, lu({"wersja": 2, "zloto": 5})))
        self.assertEqual((p3["wersja"], p3["sekrety"]["dzien"], len(p3["sekrety"]["lista"])), (3, -1, 0), "migracja v2 → v3")


def T_KL(KL, n, *a):
    r = IT.wywolaj(KL.get(n), [lu(x) for x in a])
    return r[0] if r else None


class TestSwiat(unittest.TestCase):
    """Świat z mapy (swiat1): przeszkody serwera z rekwizytów, wyjście z legowiska, owce."""

    def test_31_przeszkody_i_wyjscie_z_legowiska(self):
        if not D.get("swiat"):
            self.skipTest("bez świata z mapy")
        prz = D["przeszkody"]
        leg = [p for p in prz if p["typ"] == "legowisko"]
        self.assertEqual(len(leg), 12 * 13, "krąg (11 skał) i brama (2 filary) w każdym z 12 legowisk")
        self.assertTrue(any(p.get("rid") in ("glaz_1", "glaz_2") for p in prz), "głazy blokują")
        self.assertTrue(any(p.get("rid") in ("czaszka_smoka", "czaszka_wielka") for p in prz), "czaszka smoka blokuje")
        self.assertFalse(any(p.get("rid") in ("trawa_1", "kwiat_zolty", "krzak", "kamyk") for p in prz), "dekoracja bez kolizji")
        # nic nie blokuje wyspy gry ani jej fosy (poza ołtarzem pośrodku wyspy)
        WY = D["wyspa"]
        self.assertFalse([p for p in prz if p["typ"] != "lawa" and math.hypot(p["x"] - WY["x"], p["z"] - WY["z"]) < WY["r_zew"] + p["r"]])
        for i, (lx, lz) in enumerate(D["legowiska"]):
            # miejsce wyklucia (start gracza) i wejście do legowiska wolne
            for (x, z) in ((lx * 0.97, lz * 0.97), (lx - lx / 126 * 15, lz - lz / 126 * 15)):
                for f in (1, 3):
                    r = D["formy"][f - 1]["r"]
                    x2, z2 = wolaj("ogranicz", DL, float(x), float(z), r, 1.0)
                    self.assertLess(math.hypot(x2 - x, z2 - z), 0.01, "legowisko %d: punkt (%.0f, %.0f) wolny dla stadium %d" % (i + 1, x, z, f))
        # pisklę idzie z każdego legowiska prosto na środek łąki i nie utyka
        S = stan()
        bez_kulek(S)
        for slot in range(1, 13):
            b = byt(S, slot, 1)
            ustaw(b, tarczaDo=0, laskaDo=1e9)
        krok(S, 1)
        for _ in range(60):
            for b in LM.z_luau(S.get("byty"), True):
                pass
            for bt in [S.get("byty").get(float(k)) for k in range(1, 13)]:
                x, z = g(bt, "x"), g(bt, "z")
                d = max(0.1, math.hypot(x, z))
                ustaw(bt, wx=-x / d, wz=-z / d)
            krok(S, 5, 0.05)
        for k in range(1, 13):
            bt = S.get("byty").get(float(k))
            self.assertLess(math.hypot(g(bt, "x"), g(bt, "z")), 70, "pisklę z legowiska %d doszło na łąkę" % k)
        # boty nie rodzą się w przeszkodach
        S = stan(ziarno=5)
        for f in (1, 3, 6):
            for _ in range(15):
                b = byt(S, 0, f)
                r = D["formy"][f - 1]["r"]
                for p in prz:
                    if p.get("k") == "p":
                        lx, lz = M2.lok(g(b, "x") - p["x"], g(b, "z") - p["z"], p["o"])
                        self.assertTrue(abs(lx) > p["hx"] + r * 0.7 - 0.15 or abs(lz) > p["hz"] + r * 0.7 - 0.15, "bot poza skałą")
                    else:
                        self.assertGreater(math.hypot(g(b, "x") - p["x"], g(b, "z") - p["z"]), p["r"] + r * 0.7 - 0.15)

    def test_32_owce(self):
        if not (D.get("swiat") and D["swiat"].get("owce")):
            self.skipTest("bez owiec")
        O = D["swiat"]["owce"]
        S = stan()
        bez_kulek(S)
        owce = LM.z_luau(jeden("dodajOwce", S), True)
        self.assertEqual(len(owce), len(O["stada"]) * O["na_stado"])
        o = S.get("owce").get(1.0)
        ox, oz = g(o, "x"), g(o, "z")
        gr = byt(S, 1, 2, ox + 8.0, oz)
        ustaw(gr, tarczaDo=0, laskaDo=0)
        krok(S, 20, 0.05)
        self.assertGreater(math.hypot(g(o, "x") - g(gr, "x"), g(o, "z") - g(gr, "z")), 8.5, "owca ucieka przed smokiem")
        # dotyk: zjedzona — wzrost jak duża kulka, potem wraca
        w0 = g(gr, "wzrost")
        ustaw(gr, x=g(o, "x") + 1.0, z=g(o, "z"))
        zd = krok(S, 1, 0.05)
        zj = [z for z in zd if z["t"] == "owca"]
        self.assertTrue(zj and zj[0]["id"] == g(gr, "id"), "owca zjedzona dotykiem")
        self.assertAlmostEqual(g(gr, "wzrost") - w0, O["wzrost"] * len([z for z in zd if z["t"] == "owca" and z["id"] == g(gr, "id")]), places=6)
        self.assertIsNotNone(g(o, "martwyDo"))
        zd = krok(S, int(O["powrot_s"] / 0.5) + 2, 0.5)
        self.assertIsNone(g(o, "martwyDo"), "owca wraca po czasie")
        self.assertTrue([z for z in zd if z["t"] == "owca_wraca"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
