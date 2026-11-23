#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy symulatora przejścia gry (swiat/przejscie_gry/symulacja_przejscia.py). Bez Roblox Studio, ok. pół minuty.

    python -B -m unittest discover -s swiat/przejscie_gry -p "test_symulacji.py"
"""
import copy
import json
import os
import random
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
if TU not in sys.path:
    sys.path.insert(0, TU)
import symulacja_przejscia as SP  # noqa: E402

LS, silnik = SP.LS, SP.silnik
WARIANT = "po_zmianie"


class Powtarzalnosc(unittest.TestCase):
    def test_to_samo_ziarno_ten_sam_wynik(self):
        G = SP.gra()
        for tryb in ("walki", "wszystko", "niecierpliwy"):
            a = SP.przejscie(G, "mag", tryb, WARIANT, 5)
            b = SP.przejscie(SP.gra(), "mag", tryb, WARIANT, 5)
            self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True), tryb)

    def test_inne_ziarno_inny_przebieg(self):
        G = SP.gra()
        a = SP.przejscie(G, "wojownik", "walki", WARIANT, 1)
        b = SP.przejscie(G, "wojownik", "walki", WARIANT, 2)
        self.assertNotEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_kolejnosc_przebiegow_bez_znaczenia(self):
        G = SP.gra()
        a1 = SP.przejscie(G, "zwiadowca", "wszystko", WARIANT, 3)
        SP.przejscie(G, "mag", "ostrozny", "przed_zmiana", 9)
        a2 = SP.przejscie(G, "zwiadowca", "wszystko", WARIANT, 3)
        self.assertEqual(json.dumps(a1, sort_keys=True), json.dumps(a2, sort_keys=True))


class ZgodnoscZDanymiGry(unittest.TestCase):
    def test_lup_i_awans_jak_w_silniku_i_stanie_gracza(self):
        """Każda walka z zapisu daje ten sam wynik i łup co silnik dla tego samego wejścia; poziom, doświadczenie
        i Złoto po każdej walce wynikają z prawdziwej logiki stanu gracza."""
        G = SP.gra()
        Ds = G["Ds"]
        for klasa in Ds["klasy"]:
            zapis = []
            w = SP.przejscie(G, klasa, "walki", WARIANT, 11, sledz=zapis)
            self.assertTrue(w["ukonczone"])
            self.assertEqual(len(zapis), w["walki"])
            L, xp, zloto, zarobione = 1, 0, 0, 0
            for z in zapis:
                r = silnik.symuluj(z["opis"], {"potwor": z["potwor"], "poziom": z["poziom"]}, z["ziarno"])
                self.assertEqual(r["wynik"], z["wynik"])
                self.assertEqual(r["lup"], z["lup"])
                self.assertEqual(z["xp"], r["lup"]["doswiadczenie"])          # bez peta — bez premii do łupu
                self.assertEqual(z["opis"]["poziom"], L)
                kara = LS.kara_przegranej(Ds, zloto, z["poziom"], Ds["kara"]["procent"]) if z["wynik"] != "wygrana" else 0
                L, xp, _ = LS.awans(Ds, L, xp, r["lup"]["doswiadczenie"])
                zloto += r["lup"]["zloto"] - kara
                zarobione += r["lup"]["zloto"]
                self.assertEqual((z["poziom_po"], z["xp_po"], z["zloto_po"]), (L, xp, zloto))
            self.assertEqual((w["poziom"], w["zarobione"], w["zloto"]), (L, zarobione, zloto))
            self.assertEqual(w["zloto"], w["zarobione"] - w["wydane"] - w["stracone"])

    def test_lup_z_plikow_gry(self):
        """Łup potworów w symulacji = dane silnika; potwory Bagna i Dżungli mają łup według swojej rangi."""
        G = SP.gra()
        with open(os.path.join(SP.WALKA, "dane_walki.json"), encoding="utf-8") as f:
            las = {p["id"]: p for p in json.load(f)["przeciwnicy"]}
        for pid, p in las.items():
            self.assertEqual(G["przeciwnicy"][pid]["lup"], p["lup"])
        for b in G["biomy"]:
            for s in b["strefy"]:
                p = G["przeciwnicy"][s["gatunek"]]
                self.assertEqual(p["kraina"], b["id"])
                self.assertEqual(s["ranga"], p["ranga"])
            self.assertEqual(b["strefy"][-1]["ranga"], "straznik")
            self.assertEqual([s["straznik"] for s in b["strefy"]].count(True), 1)

    def test_bohater_jak_wzorcowy(self):
        """Bohater bez dodatków = opis z logiki stanu gracza (ten sam, którego używa gra)."""
        G = SP.gra()
        Ds = G["Ds"]
        for klasa in Ds["klasy"]:
            for L in (1, 7, 16, 23):
                wzor = LS.opis_bohatera(Ds, klasa, L, LS.rozdziel(Ds, Ds["rozklady"][klasa], LS.pula(Ds, L)))
                self.assertEqual(SP.opis_bohatera(G, klasa, L)[0], wzor)

    def test_bramy_w_kolejnosci(self):
        G = SP.gra()
        zapis = []
        w = SP.przejscie(G, "wojownik", "wszystko", WARIANT, 4, sledz=zapis)
        k = w["kamienie"]
        kolejnosc = ["pierwsza_wygrana"]
        for b in G["biomy"]:
            kolejnosc += ["straznik_" + b["id"], "brama_" + b["id"]]
        czasy = [k[n]["min"] for n in kolejnosc]
        self.assertEqual(czasy, sorted(czasy))
        # do następnej krainy gracz wchodzi dopiero po wygranej ze Strażnikiem poprzedniej (wymaganie bramy)
        for z in zapis:
            nr = [b["id"] for b in G["biomy"]].index(z["biom"])
            if nr > 0:
                self.assertGreaterEqual(z["czas"] / 60.0, k["straznik_" + G["biomy"][nr - 1]["id"]]["min"])


class PrzypadkiBrzegowe(unittest.TestCase):
    def test_pierwsza_walka_prawie_pewna(self):
        """Szczęście początkującego z danych stanu gracza: pierwsza walka wygrana u prawie wszystkich."""
        G = SP.gra()
        for klasa in G["Ds"]["klasy"]:
            wyg = 0
            for z in range(40):
                zapis = []
                SP.przejscie(G, klasa, "walki", WARIANT, 100 + z, limit_min=1.0, sledz=zapis)
                wyg += zapis[0]["wynik"] == "wygrana"
            self.assertGreaterEqual(wyg, 36, klasa)

    def test_limit_czasu(self):
        G = SP.gra()
        w = SP.przejscie(G, "mag", "walki", WARIANT, 1, limit_min=5.0)
        self.assertFalse(w["ukonczone"])
        self.assertTrue(w["utknal_w"].startswith("las/"))
        self.assertLess(w["czas_min"], 8.0)
        P = SP.podsumuj([w])
        self.assertEqual(P["ukonczylo_proc"], 0.0)
        self.assertIsNone(P["czas_min"])

    def test_zmiany_tylko_na_kopii(self):
        przed = copy.deepcopy(SP.baza()["przeciwnicy"])
        a_przed = SP.baza()["Ds"]["krzywa"]["a"]
        G = SP.gra({"krzywa_a": 0.5, "potwor": {"waz_stu_lian": {"zycie": -0.2, "bron": 0.5}},
                    "poziomy": {"dzungla/straznik": -3, "bagno/t1": [14, 14]},
                    "lup": {"dzungla": {"doswiadczenie": 2.0}}, "cena_jajka": {"jajko_lesne": 1}, "kara_procent": 0.0})
        self.assertAlmostEqual(G["Ds"]["krzywa"]["a"], a_przed * 0.5)
        self.assertEqual(G["biomy"][2]["strefy"][-1]["od"], SP.baza()["biomy"][2]["strefy"][-1]["od"] - 3)
        self.assertEqual(G["biomy"][1]["strefy"][-2]["do"], 14)
        self.assertNotEqual(silnik.PRZECIWNICY["waz_stu_lian"]["bron"], przed["waz_stu_lian"]["bron"])
        szybciej = SP.przejscie(G, "mag", "walki", WARIANT, 1)
        G0 = SP.gra()
        self.assertEqual(SP.baza()["przeciwnicy"], przed)
        self.assertEqual(silnik.PRZECIWNICY, przed)
        self.assertEqual(SP.baza()["Ds"]["krzywa"]["a"], a_przed)
        zwykle = SP.przejscie(G0, "mag", "walki", WARIANT, 1)
        self.assertLess(szybciej["czas_min"], zwykle["czas_min"])
        with self.assertRaises(ValueError):
            SP.gra({"nie_ma_takiej": 1})

    def test_mini_gra(self):
        G = SP.gra()
        los = random.Random(1)
        for stat in G["Ds"]["statystyki"]:
            W, pasek, traf, n = SP.runda_minigry(G, stat, 5, 0, 0.0, 0.0, los)
            self.assertEqual((W, pasek, traf), (0, 0.0, 0), stat)
            self.assertGreater(n, 10)
            W1, _p, traf1, n1 = SP.runda_minigry(G, stat, 5, 0, 0.0, 1.0, los)
            self.assertEqual(traf1, n1)
            self.assertGreater(W1, 0, stat)
            W2, _p, _t, _n = SP.runda_minigry(G, stat, 5, 30, 0.0, 1.0, los)   # malejący zysk: dalej trudniej
            self.assertLess(W2 - 30, W1, stat)

    def test_mini_gry_wzmacniaja(self):
        G = SP.gra()
        w = SP.przejscie(G, "wojownik", "walki_minigry", WARIANT, 2)
        self.assertGreater(w["wytrenowane"], 0)
        self.assertGreater(w["min_trening"], 0)
        self.assertEqual(SP.przejscie(G, "wojownik", "walki", WARIANT, 2)["wytrenowane"], 0)

    def test_po_zmianie_bez_czekania_na_blokade(self):
        """D-107: po walce nie ma czekania (blokada trwa najwyżej najkrótszy pokaz) — także u niecierpliwego."""
        G = SP.gra()
        if G["tempo_blokady"] < 4:
            self.skipTest("pliki gry bez D-107 (S.TEMPO_POKAZU_MAKS)")
        po = SP.przejscie(G, "mag", "niecierpliwy", "po_zmianie", 3)
        przed = SP.przejscie(G, "mag", "niecierpliwy", "przed_zmiana", 3)
        self.assertEqual(po["min_blokady"], 0.0)
        self.assertGreater(przed["min_blokady"], 0.0)

    def test_katalog_sklepu(self):
        self.assertIsNone(SP.wczytaj_katalog([os.path.join(TU, "nie_ma_takiego_pliku.json")]))
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "katalog.json")
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"przedmioty": {
                    "rycerz_miecz": {"klasa": "wojownik", "stopien": "start", "slot": "Weapon", "cena": 0, "baza": {}},
                    "rycerz_las_miecz": {"klasa": "wojownik", "stopien": "las", "slot": "Weapon", "cena": 200, "poziom": 2,
                                         "baza": {"bron": 6, "Strength": 3}},
                    "rycerz_bagno_miecz": {"klasa": "wojownik", "stopien": "bagno", "slot": "Weapon", "cena": 900,
                                           "poziom": 10, "baza": {"bron": 12, "Strength": 6}},
                    "kot_mag_las_kostur": {"klasa": "mag", "stopien": "las", "slot": "Weapon", "cena": 200,
                                           "baza": {"bron": 6}}}}, f)
            K = SP.wczytaj_katalog([p])
            self.assertEqual(sorted(it["id"] for it in K["przedmioty"]),
                             ["kot_mag_las_kostur", "rycerz_bagno_miecz", "rycerz_las_miecz"])
            self.assertEqual(K["przedmioty"][0]["mod"], {"bron": 6, "statystyki": {"Strength": 3}})
            G = SP.gra()
            G["katalog"] = K
            zapis = []
            w = SP.przejscie(G, "wojownik", "ze_sklepem", WARIANT, 1, sledz=zapis)
            self.assertEqual(w["sklep"], 1)                       # jeden slot (broń), kupiony co najmniej raz
            self.assertGreaterEqual(w["wydane"], 200)
            bez = SP.przejscie(G, "wojownik", "wszystko", WARIANT, 1)
            self.assertEqual(bez["sklep"], 0)                     # „wszystko” nie kupuje w sklepie
            # broń ze sklepu nie zabiera Wojownikowi tarczy (blok ze wzoru zostaje do końca)
            self.assertGreaterEqual(zapis[-1]["opis"]["tarcza"]["blok"], G["Ds"]["wzor"]["blok_tarczy"] - 1e-9)
            with open(p, "w", encoding="utf-8") as f:
                json.dump({"przedmioty": [{"id": "x", "slot": "Helmet", "stopien": 1}]}, f)
            with self.assertRaises(ValueError):
                SP.wczytaj_katalog([p])

    def test_kwantyl_i_rozklad(self):
        self.assertEqual(SP.kwantyl([1, 2, 3, 4, 5], 0.5), 3)
        self.assertAlmostEqual(SP.kwantyl([10, 20], 0.1), 11)
        self.assertIsNone(SP.kwantyl([], 0.5))
        self.assertIsNone(SP.rozklad([None]))
        self.assertEqual(SP.rozklad([4, 2, 9])["med"], 4)

    def test_tabele_i_wstawianie(self):
        G = SP.gra()
        wyn = SP.podsumuj([SP.przejscie(G, "mag", "walki", WARIANT, z) for z in range(3)])
        R = {"meta": {"klasy": ["mag"], "tryby": ["walki"], "warianty": [WARIANT], "przebiegow": 3, "ziarno": 0,
                      "katalog_sklepu": None, "data": "test", "propozycje_tryby": ["walki"],
                      "propozycje_wariant": WARIANT},
             "wyniki": {WARIANT: {"walki": {"mag": wyn}}}, "propozycje": {}}
        tekst = SP.tabele(R)
        self.assertIn("Strażnik", tekst)
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "raport.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# Raport\n\nWnioski ręczne.\n\n%s\nstare\n%s\n\nStopka.\n" % (SP.ZNACZNIK_OD, SP.ZNACZNIK_DO))
            SP.wstaw_tabele(p, tekst)
            with open(p, encoding="utf-8") as f:
                nowy = f.read()
            self.assertIn("Wnioski ręczne.", nowy)
            self.assertIn("Stopka.", nowy)
            self.assertNotIn("\nstare\n", nowy)
            self.assertEqual(nowy.count(SP.ZNACZNIK_OD), 1)


if __name__ == "__main__":
    unittest.main()
