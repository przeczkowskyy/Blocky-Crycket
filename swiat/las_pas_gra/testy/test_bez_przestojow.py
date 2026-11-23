#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""D-107 — walka bez przestojów: testy bez Studio dla lasu, Bagna i Dżungli (jeden kod potworów, trzy zestawy danych).

    python -B swiat/las_pas_gra/testy/test_bez_przestojow.py            # testy
    python -B swiat/las_pas_gra/testy/test_bez_przestojow.py --tabela   # rachunek „było / jest” (do README)

Co sprawdza:
  1. serwer potworów: blokada sesji gracza i zajętość potwora trwają walka.czas / TEMPO_POKAZU_MAKS (najkrótszy pokaz),
     a nie pełny czas ×1 — po obejrzanej walce (także przegranej) nie ma czekania; ochrona przed podwójnym startem
     zostaje (odstęp próśb, blokada na czas najkrótszego pokazu); sygnał WynikWalki niesie dalej koniec pokazu ×1;
  2. dane trzech biomów: liczby gry z GESTOSC_D107 (4 / 7 / 8 potworów na zwykłą strefę przy 1 / 8 / 20 graczach,
     wilki lasu 3 / 6 / 7, odrodzenie stałe 2 s, rzadki 20 s, strażnik 30 s), plan mapy nietknięty, potwory mieszczą
     się na pętli;
  3. rachunek „gracz nigdy nie czeka” — symulacja tą samą klasą Symulacja co testy potworów (lustro tyknięcia
     SerwerPotworow): gracze walczą bez przerwy (walka pominięta 1 s + dojście 1,5 s — z pomiaru w Play), a test liczy, ile sekund
     gracz stał bez wolnego potwora. Samotny gracz: 0 s w każdej strefie; 3 graczy w strefie (8 na serwerze): 0 s;
     6 graczy w strefie (20 na serwerze): liczba w teście 3b. Dla porównania te same przebiegi na liczbach sprzed
     D-107 (z planu) — samotny gracz stał wtedy 61–73% czasu;
  4. rzadki potwór i strażnik wracają po czasie z danych (bez skracania i bez dolnej granicy 10 s).

Czego nie da się sprawdzić bez Studio: prawdziwy czas pominiętej walki i koszt klatki przy większej liczbie potworów —
to punkty prób w Play (testy/pomoc_d107.py: D3 i D5; pomiar 19.11.2026: pominięta walka 0,45 s od E do powrotu na pas).
"""
import importlib.util
import os
import random
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
POTWORY = os.path.join(REPO, "swiat", "las_potwory")


def _modul(nazwa, sciezka):
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(sciezka))
    sys.modules.pop("przeciwnicy", None)   # Bagno i Dżungla mają moduł o tej samej nazwie — każdy generator bierze swój
    try:
        spec.loader.exec_module(m)
    finally:
        sys.path.remove(os.path.dirname(sciezka))
    return m


GEN = _modul("generuj_dane_d107", os.path.join(PAKIET, "generuj_dane.py"))
GEN_B = _modul("generuj_dane_bagna_d107", os.path.join(REPO, "swiat", "bagno_pas_gra", "generuj_dane.py"))
GEN_D = _modul("generuj_dane_dzungli_d107", os.path.join(REPO, "swiat", "dzungla_pas_gra", "generuj_dane.py"))
TL = _modul("test_logiki_d107", os.path.join(POTWORY, "testy", "test_logiki.py"))
Lg = GEN.Lg
G107 = GEN.GESTOSC_D107

BIOMY = {"las": GEN.KONFIG, "bagno": GEN_B.KONFIG, "dzungla": GEN_D.KONFIG}


def dane(konfig, gestosc=True):
    k = dict(konfig)
    if not gestosc:
        k["gestosc"] = None
    return GEN.wszystko(k=k)[1]


DANE = {b: dane(k) for b, k in BIOMY.items()}
DANE_PRZED = {b: dane(k, gestosc=False) for b, k in BIOMY.items()}

with open(os.path.join(POTWORY, "zrodla", "SerwerPotworow.server.luau"), encoding="utf-8") as _f:
    SERWER = _f.read()
with open(os.path.join(POTWORY, "zrodla", "Stale.luau"), encoding="utf-8") as _f:
    STALE = _f.read()

# model gracza do rachunku. Próba w Play 19.11.2026 (punkt PD5): pominięta walka trwa u klienta 0,45 s od E do powrotu
# na pas (E → przycisk POMIŃ 0,21 s, spacja → wynik 0,01 s, zamknięcie → pas 0,00 s; reszta to chwila między nimi) —
# do tego dwa naciśnięcia człowieka (POMIŃ, ZAMKNIJ), razem przyjęte 1 s; serwer i tak przyjmuje jedną prośbę na 1 s
WALKA_POMINIETA_S = 1.0     # E → POMIŃ → ZAMKNIJ (najszybszy gracz; przed pomiarem zakładałem 3 s)
DOJSCIE_S = 1.5             # do następnego potwora: 4 potwory na pętli 121 st to ok. 30 st, bieg 16 st/s, potwór też idzie
GRACZE_W_STREFIE = {1: 1, 8: 3, 20: 6}   # graczy na serwerze → w jednej strefie (trzy strefy zwykłe + rzadki + strażnik)
CZAS_PROBY_S = 600


def przebieg(st, zasady, G, ziarno=1, cykl=WALKA_POMINIETA_S + DOJSCIE_S, czas=CZAS_PROBY_S):
    """Gracze walczą bez przerwy w jednej strefie (każda walka wygrana i pominięta — najgorszy przypadek dla podaży
    potworów). → (walk, sekundy czekania wszystkich graczy, najdłuższe czekanie, najmniej wolnych potworów)."""
    rnd = random.Random(ziarno)
    v = 0 if st["straznik"] else DANE_V[id(st)]
    sym = TL.Symulacja(st, zasady, v, 1 if st["straznik"] else Lg.cel(st["naraz"], st["max"], G), rnd)
    n = GRACZE_W_STREFIE[G]
    gotowy = [0.5 + i * cykl / n for i in range(n)]      # gracze nie zaczynają w tej samej chwili
    czeka_od = [None] * n
    pozycje = [[st["srodek"][0], st["srodek"][2]] for _ in range(n)]
    walk, czekanie, najdluzej, min_wolnych = 0, 0.0, 0.0, 10 ** 9
    dt, nastepna = 0.25, 1.0
    for i in range(1, int(czas / dt) + 1):
        teraz = i * dt
        sym.tyknij(teraz, dt)
        if teraz + 1e-9 >= nastepna:
            sym.odradzaj(teraz, gracze=pozycje, G=G)
            nastepna += 1.0
        wolne = [p for p in sym.potwory if p["zajety"] is None]
        min_wolnych = min(min_wolnych, len(wolne))
        for g in range(n):
            if teraz + 1e-9 < gotowy[g]:
                continue
            if not wolne:
                if czeka_od[g] is None:
                    czeka_od[g] = teraz
                continue
            p = wolne.pop(rnd.randrange(len(wolne)))
            # pominięcie: serwer zamyka zajętość w najbliższym tyknięciu pętli ruchu (ZwolnijPoPominieciu)
            p["zajety"] = {"do": teraz + dt, "wynik": "wygrana"}
            if czeka_od[g] is not None:
                czekanie += teraz - czeka_od[g]
                najdluzej = max(najdluzej, teraz - czeka_od[g])
                czeka_od[g] = None
            if p["grupa"] is not None:
                s = Lg.w_grupie(p["grupa"]["s"], p["miejsce"], st["odstepWGrupie"], sym.L)
                x, _, z, _ = Lg.punkt_trasy(st["trasa"], s)
            else:
                x, z = p["x"], p["z"]
            pozycje[g] = [x, z]
            gotowy[g] = teraz + cykl
            walk += 1
    for g in range(n):
        if czeka_od[g] is not None:
            czekanie += czas - czeka_od[g]
            najdluzej = max(najdluzej, czas - czeka_od[g])
    return walk, czekanie, najdluzej, min_wolnych


DANE_V = {}
for _zestaw in (DANE, DANE_PRZED):
    for _dp in _zestaw.values():
        for _st in _dp["strefy"]:
            DANE_V[id(_st)] = _dp["gatunki"][_st["gatunek"]]["predkosc"]


def zwykle(dp):
    return [s for s in dp["strefy"] if not s["straznik"] and not s.get("rzadki", s.get("odrodzenieStale") and s["max"] == 1)]


def suma_celow(dp):
    return [sum(1 if s["straznik"] else Lg.cel(s["naraz"], s["max"], G) for s in dp["strefy"]) for G in (1, 8, 20)]


class TestSerwera(unittest.TestCase):
    def test_1a_sesja_i_zajetosc_na_czas_najkrotszego_pokazu(self):
        self.assertIn("S.TEMPO_POKAZU_MAKS = 4", STALE)
        self.assertIn("local pokaz = walka.czas / math.max(1, Stale.TEMPO_POKAZU_MAKS)", SERWER)
        self.assertIn("walkaDo[gracz] = czas + pokaz - Stale.ZAPAS_SESJI", SERWER)
        self.assertIn("koniec = czas + pokaz + Stale.ZAPAS_ZAJETOSCI }", SERWER)
        # nic już nie blokuje na pełny czas walki ×1
        self.assertNotIn("walkaDo[gracz] = czas + walka.czas", SERWER)
        self.assertNotIn("koniec = czas + walka.czas + Stale.ZAPAS_ZAJETOSCI }\n\tp.ruszyl", SERWER)

    def test_1b_ochrona_przed_podwojnym_startem_zostaje(self):
        self.assertIn('return odmowa("za_szybko", Stale.ODSTEP_PROSB - (zegar - poprzednio))', SERWER)
        self.assertIn('return odmowa("walka_trwa", koniec - czas)', SERWER)
        self.assertIn("S.ODSTEP_PROSB = 1.0", STALE)
        # zajęty potwór: inny gracz albo ten sam po wygranej — odmowa; ten sam po przegranej — rewanż
        self.assertIn('if p.zajety and (p.zajety.gracz ~= gracz or p.zajety.wynik == "wygrana") then', SERWER)

    def test_1c_pamiec_pomijania_dostaje_koniec_pokazu_x1(self):
        self.assertIn("koniec = czas + walka.czas + Stale.ZAPAS_ZAJETOSCI } -- koniec pokazu ×1", SERWER)
        # pominięcie dalej zwalnia gracza i potwora od razu
        self.assertIn("walkaDo[gracz] = czas\n\t\tfor _, p in potwory do", SERWER)

    def test_1d_komunikaty_bez_odpoczynku(self):
        self.assertNotIn('= "Odpoczywasz', STALE)
        self.assertNotIn("Wróci za 2 min", STALE)

    def test_1e_najkrotszy_pokaz_krotszy_niz_walka(self):
        # przykład: walka 24 s (slime, średnio) — dawniej blokada 23,6 s, teraz 5,6 s; pokaz ×4 trwa 6 s + wejście i wynik
        czas, tempo, zapas = 24.0, 4, 0.4
        self.assertLess(czas / tempo - zapas, czas / tempo)
        self.assertAlmostEqual(czas / tempo - zapas, 5.6)


class TestDanych(unittest.TestCase):
    def test_2a_liczby_gry_w_trzech_biomach(self):
        for biom, dp in DANE.items():
            with self.subTest(biom=biom):
                self.assertEqual(suma_celow(dp), [13, 22, 25] if biom == "las" else [14, 23, 26])
                self.assertEqual(dp["zasady"]["odstep"], G107["odstep"])
                self.assertEqual(dp["zasady"]["blokadaDomu"], G107["blokada_domu"])
                for st in dp["strefy"]:
                    self.assertTrue(st["odrodzenieStale"], st["id"])
                    if st["straznik"]:
                        self.assertEqual(st["odrodzenieS"], G107["straznik"]["odrodzenie_s"])
                    elif st["rzadki"]:
                        self.assertEqual((st["naraz"], st["max"], st["odrodzenieS"]), (1, 1, G107["rzadki"]["odrodzenie_s"]))
                    else:
                        # wilki lasu: 3 / 6 / 7 (544 bryły każdy przy budżecie 4000 brył widoków klienta)
                        self.assertEqual([Lg.cel(st["naraz"], st["max"], G) for G in (1, 8, 20)],
                                         [3, 6, 7] if st["id"] == "w1" else [4, 7, 8])
                        self.assertEqual(st["odrodzenieS"], G107["zwykla"]["odrodzenie_s"])

    def test_2b_plan_mapy_i_trasy_bez_zmian(self):
        for biom in DANE:
            przed, po = DANE_PRZED[biom], DANE[biom]
            with self.subTest(biom=biom):
                self.assertEqual([s["id"] for s in przed["strefy"]], [s["id"] for s in po["strefy"]])
                for a, b in zip(przed["strefy"], po["strefy"]):
                    for pole in ("trasa", "domy", "pole", "srodek", "poziomy", "gatunek", "zasiegGraczy", "r"):
                        self.assertEqual(a[pole], b[pole], "%s.%s" % (a["id"], pole))
                self.assertEqual(przed["biom"], po["biom"])
                self.assertEqual(przed["gatunki"], po["gatunki"])
        self.assertEqual([suma_celow(DANE_PRZED[b]) for b in ("las", "bagno", "dzungla")],
                         [[8, 12, 16], [8, 11, 14], [8, 11, 14]])

    def test_2c_potwory_mieszcza_sie_na_petli_z_luzem(self):
        for biom, dp in DANE.items():
            for st in zwykle(dp):
                with self.subTest(biom=biom, strefa=st["id"]):
                    potrzeba = st["grupy"] * ((st["miejsc"] - 1) * st["odstepWGrupie"] + dp["zasady"]["odstep"])
                    self.assertLessEqual(potrzeba + dp["zasady"]["odstep"], st["trasa"]["L"] + 1e-9)
                    # odstęp nie mniejszy niż sam potwór (nie nachodzą na siebie)
                    self.assertGreater(dp["zasady"]["odstep"], max(dp["gatunki"][st["gatunek"]]["wymiary"][0],
                                                                 dp["gatunki"][st["gatunek"]]["wymiary"][2]))


class TestBezCzekania(unittest.TestCase):
    def test_3a_samotny_gracz_nigdy_nie_czeka(self):
        for biom, dp in DANE.items():
            for st in zwykle(dp):
                for ziarno in (1, 7):
                    with self.subTest(biom=biom, strefa=st["id"], ziarno=ziarno):
                        walk, czekanie, _, min_wolnych = przebieg(st, dp["zasady"], 1, ziarno)
                        self.assertEqual(czekanie, 0.0)
                        self.assertGreaterEqual(min_wolnych, 1)      # po każdej walce zostaje co najmniej 1 wolny
                        self.assertGreaterEqual(walk, CZAS_PROBY_S / (WALKA_POMINIETA_S + DOJSCIE_S) - 2)

    def test_3b_kilku_graczy_ma_z_kim_walczyc(self):
        for biom, dp in DANE.items():
            for st in zwykle(dp):
                with self.subTest(biom=biom, strefa=st["id"]):
                    _, czekanie8, _, _ = przebieg(st, dp["zasady"], 8)
                    self.assertEqual(czekanie8, 0.0)                 # 3 graczy w strefie, 7 potworów
                    _, czekanie20, najdluzej, _ = przebieg(st, dp["zasady"], 20)
                    udzial = czekanie20 / (CZAS_PROBY_S * GRACZE_W_STREFIE[20])
                    self.assertLessEqual(udzial, 0.05)               # 6 graczy w strefie, 8 potworów
                    self.assertLessEqual(najdluzej, 4.0)

    def test_3c_przed_d107_samotny_gracz_stal(self):
        """Te same przebiegi na liczbach sprzed D-107 (z planu): samotny gracz stał bez potwora 61–73% czasu."""
        for biom, dp in DANE_PRZED.items():
            st = zwykle(dp)[0]
            with self.subTest(biom=biom, strefa=st["id"]):
                walk, czekanie, _, _ = przebieg(st, dp["zasady"], 1)
                self.assertGreater(czekanie / CZAS_PROBY_S, 0.3)
                self.assertLess(walk, przebieg(zwykle(DANE[biom])[0], DANE[biom]["zasady"], 1)[0] * 0.7)

    def test_4_rzadki_i_straznik_wracaja_po_czasie_z_danych(self):
        for biom, dp in DANE.items():
            for st in dp["strefy"]:
                if not (st["straznik"] or st["rzadki"]):
                    continue
                with self.subTest(biom=biom, strefa=st["id"]):
                    sym = TL.Symulacja(st, dp["zasady"], 0, 1, random.Random(1))
                    sym.potwory[0]["zajety"] = {"do": 1.0, "wynik": "wygrana"}
                    sym.tyknij(1.0, 0.25)
                    sym.odradzaj(1.0, gracze=[[st["srodek"][0], st["srodek"][2]]] * 5)
                    self.assertAlmostEqual(sym.kolejka[0] - 1.0, st["odrodzenieS"], delta=1e-9)
                    self.assertLessEqual(st["odrodzenieS"], 30)


class TestLupu(unittest.TestCase):
    """Doświadczenie zawsze dostępne: łup liczy silnik przy przyjęciu walki i zależy od poziomu POTWORA, nie bohatera."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.join(REPO, "tools", "walka"))
        import silnik
        import wzorcowe
        cls.silnik, cls.wzorcowe = silnik, wzorcowe

    def lupy(self, potwor, poziom_potwora, poziom_bohatera, n=25):
        w = []
        for klasa in self.wzorcowe.KLASY:
            for ziarno in range(1, n + 1):
                r = self.silnik.symuluj(self.wzorcowe.postac(klasa, poziom_bohatera), {"potwor": potwor, "poziom": poziom_potwora}, ziarno)
                w.append((r["wynik"], r["lup"]["doswiadczenie"], r["lup"]["zloto"]))
        return w

    def test_5a_slabszy_potwor_dalej_daje_doswiadczenie_i_zloto(self):
        # bohater poz. 10 przeciw slime'owi poz. 1 (dziewięć poziomów niżej): każda wygrana daje doświadczenie i Złoto,
        # w tym samym przedziale co u bohatera poz. 1 (łup nie zależy od poziomu bohatera)
        wysoki = [x for x in self.lupy("lesny_slime", 1, 10) if x[0] == "wygrana"]
        niski = [x for x in self.lupy("lesny_slime", 1, 1) if x[0] == "wygrana"]
        self.assertGreater(len(wysoki), 60)
        self.assertGreater(len(niski), 20)
        for zestaw in (wysoki, niski):
            self.assertTrue(all(10 <= xp <= 14 and 16 <= zl <= 24 for _, xp, zl in zestaw), zestaw[:5])

    def test_5b_przegrana_daje_doswiadczenie_a_pominiecie_nie_zmienia_lupu(self):
        przegrane = [x for x in self.lupy("straznik_lasu", 10, 5) if x[0] == "przegrana"]
        self.assertGreater(len(przegrane), 60)
        self.assertTrue(all(xp >= 1 and zl == 0 for _, xp, zl in przegrane), przegrane[:5])
        # łup idzie do gracza przy PRZYJĘCIU walki (przed pokazem) — pominięcie i tempo nic w nim nie zmieniają
        i_lup = SERWER.index("nagrodaZaWalke(gracz, p, walka)" + chr(10) + chr(9) + "end")
        i_odp = SERWER.index("return { ok = true, walka = walka, nastepnaOd = walkaDo[gracz] }")
        self.assertLess(i_lup, i_odp)
        zwolnij = SERWER[SERWER.index("zwolnij.OnInvoke = function"):]
        self.assertNotIn("lup", zwolnij[:zwolnij.index("return true")])


def tabela():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print("cykl gracza: walka pominięta %.1f s + dojście %.1f s; próba %d s; graczy w strefie przy 1 / 8 / 20: %s" % (
        WALKA_POMINIETA_S, DOJSCIE_S, CZAS_PROBY_S, " / ".join(str(GRACZE_W_STREFIE[g]) for g in (1, 8, 20))))
    print("biom     strefa  stan     potworów 1/8/20  odrodz.  czekanie gracza (udział czasu) przy 1 / 8 / 20   walk solo")
    for biom in DANE:
        for nazwa, zestaw in (("przed", DANE_PRZED), ("D-107", DANE)):
            dp = zestaw[biom]
            for st in zwykle(dp):
                cele = [Lg.cel(st["naraz"], st["max"], G) for G in (1, 8, 20)]
                w = [przebieg(st, dp["zasady"], G) for G in (1, 8, 20)]
                udzialy = ["%4.0f%%" % (100 * w[i][1] / (CZAS_PROBY_S * GRACZE_W_STREFIE[G])) for i, G in enumerate((1, 8, 20))]
                print("%-8s %-7s %-8s %-16s %-8s %-48s %d" % (biom, st["id"], nazwa, " / ".join(map(str, cele)),
                      "%d s" % st["odrodzenieS"], " / ".join(udzialy), w[0][0]))
    for biom in DANE:
        print("%-8s razem ze strażnikiem: przed %s, D-107 %s" % (biom, suma_celow(DANE_PRZED[biom]), suma_celow(DANE[biom])))


if __name__ == "__main__":
    if "--tabela" in sys.argv:
        tabela()
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        unittest.main(verbosity=1)
