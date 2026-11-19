#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy kowala na próbę bez Studio (swiat/kowal_proba). Uruchom: python -B swiat/kowal_proba/testy/test_kowala.py

1. Dane: pliki aktualne, katalog przedmiotów (stopień startowy: 18 całych + 2 części zbroi = 20 przedmiotów bohaterów;
   z przedmiotami do kupienia D-106 razem 72 całe + 8 części — kupno sprawdza swiat/sklep_proba/testy), podstawowe
   zestawy, koszty, miejsce kuźni w bazarze, teksty dla gracza bez języka twórców.
2. Balans: podstawowy zestaw = dzisiejszy bohater ze wzoru (co do pola opisu) na poziomach 1–30; każdy wpis kowala
   przechodzi walidację Sygnaly/Modyfikatory (prawdziwa logika stanu gracza); bez tarczy Wojownik traci blok tarczy;
   pełny zestaw każdej klasy kosztuje tyle samo.
3. Lustro: LogikaKowala.luau w luau_mini = logika_kowala.py (przypadki wzorcowe, 600 losowych wywołań, 3 zepsute
   wersje logiki wykryte).
4. Rig kowala: klipy, nic pod ziemią w żadnej klatce, młot trafia w blat kowadła kuźni w klatce uderzenia.
5. PRAWDZIWE SerwerKowala + SerwerStanu (swiat/stan_gracza) + SerwerStrojow (swiat/stroje_proba) w luau_mini
   (atrapa Roblox): podstawowy zestaw na starcie, łup z przyrostu tokenów, nowy przedmiot założony, rozbiórka,
   ulepszenie (Złoto przez WydajZloto, za mało Złota / materiałów = odmowa bez zmian), zasięg, limit zapytań,
   zmiana klasy, zdjęta tarcza, przymierzalnia tylko z posiadanymi (i jak dawniej bez kowala), brak StanGracza,
   przebudowa StanGracza.
6. Narzędzia: kontrola Luau (też zmienionych plików przymierzalni), zbuduj.py --sucho, kod budowy parsuje się,
   brak ścieżek lokalnych, proba_play.py --sprawdz.
"""
import copy
import glob
import importlib.util
import json
import math
import os
import random
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TESTY = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TESTY)
REPO = os.path.dirname(os.path.dirname(PAKIET))
STAN = os.path.join(REPO, "swiat", "stan_gracza")
STROJE = os.path.join(REPO, "swiat", "stroje_proba")
WALKA = os.path.join(REPO, "tools", "walka")
for _s in (os.path.join(STAN, "testy"), WALKA, REPO, PAKIET):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import dane as DANE  # noqa: E402  (swiat/kowal_proba/dane.py — PAKIET jest pierwszy w sys.path)
import logika_kowala as LK  # noqa: E402
import sprawdz_luau_kowala as SLK  # noqa: E402

LM = SLK.luau_mini()


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8") as f:
        return f.read()


D, SCENA = DANE.dane_z_przypadkami()
ZRODLA = os.path.join(PAKIET, "zrodla")
DANE_LUAU = czytaj(ZRODLA, "DaneKowala.luau")
LOGIKA = czytaj(ZRODLA, "LogikaKowala.luau")
SERWER = czytaj(ZRODLA, "SerwerKowala.server.luau")


def _stan():
    DS = _modul("dane_stanu_test_kowala", os.path.join(STAN, "dane.py"))
    LS = _modul("logika_stanu", os.path.join(STAN, "logika_stanu.py"))
    return DS.dane_z_przypadkami()[1], LS


# ------------------------------------------------------------------------------------------------ 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_aktualne(self):
        zle, _D, _p = DANE.aktualny()
        self.assertEqual(zle, [], "uruchom python -B swiat/kowal_proba/dane.py")

    def test_1b_katalog_i_podstawowe(self):
        K = DANE.katalog()
        bohaterow = [p for p in K["przedmioty"] if p["zestaw"] in DANE.ZESTAWY_BOHATEROW]
        self.assertEqual(len(bohaterow), 20)
        # D-106: do dzisiejszych 18 całych + 2 części doszły 54 przedmioty do kupienia + 6 części (katalog sklepu)
        startowe = [i for i, P in D["przedmioty"].items() if P["nrStopnia"] == 0]
        czesci_start = {c for c, cal in D["czesci"].items() if D["przedmioty"][cal]["nrStopnia"] == 0}
        self.assertEqual(len(startowe) + len(czesci_start), 20)
        self.assertEqual(czesci_start, {"rycerz_nogawice", "zwiadowca_spodnie"})
        self.assertEqual((len(D["przedmioty"]), len(D["czesci"])), (72, 8))
        self.assertEqual(sorted(startowe), sorted(DANE.ustawienia()["przedmioty"]), "stopień startowy = ustawienia kowala")
        for k, Kl in D["klasy"].items():
            self.assertEqual(Kl["przedmioty"], [i for i in Kl["wszystkie"] if D["przedmioty"][i]["nrStopnia"] == 0], k)
            self.assertFalse(any(D["przedmioty"][i]["podstawowy"] for i in Kl["wszystkie"] if i not in Kl["przedmioty"]))
        for k, Kl in D["klasy"].items():
            sloty = [D["przedmioty"][i]["slot"] for i in Kl["przedmioty"]]
            self.assertEqual(len(sloty), len(set(sloty)), k)
            podst = {D["przedmioty"][i]["slot"] for i in Kl["podstawowe"]}
            self.assertTrue({"Weapon", "Chest"} <= podst, k)
            self.assertEqual("OffHand" in podst, Kl["tarcza"], k)
            for i in Kl["podstawowe"]:
                self.assertEqual(D["przedmioty"][i]["baza"], {}, "podstawowy %s ma liczyć się jak dziś" % i)

    def test_1c_koszty(self):
        for pid, P in D["przedmioty"].items():
            for pole in ("zloto", "materialy"):
                t = P["koszt"][pole]
                self.assertEqual(len(t), D["ulepszenie"]["maks"], pid)
                self.assertTrue(all(t[i] <= t[i + 1] for i in range(len(t) - 1)), pid)
                self.assertTrue(all(isinstance(x, int) and x >= 1 for x in t), pid)
            self.assertIsNone(LK.koszt(D, pid, D["ulepszenie"]["maks"]))

    def test_1d_miejsce_kuzni(self):
        kz = D["kuznia"]
        uk = DANE._json(os.path.join(DANE.BAZAR, "uklad.json"))
        X0, Z0 = uk["swiat"]["X0"], uk["swiat"]["Z0"]
        g = uk["granice"]
        mn, mx = kz["zakres"]["min"], kz["zakres"]["max"]
        self.assertGreaterEqual(mn[0] - X0, g["pole_gry_x"][0])
        self.assertLessEqual(mx[0] - X0, g["pole_gry_x"][1])
        self.assertGreaterEqual(mn[2] - Z0, 4.0, "kuźnia poza środkowym pasem uliczki (południowa strona)")
        self.assertLessEqual(mx[2] - Z0, g["pole_gry_z"][1])
        for s, odl in kz["odstepyE"].items():
            self.assertGreaterEqual(odl, DANE.ustawienia()["kuznia"]["odstep_e"], s)
        self.assertLess(math.hypot(kz["e"][0] - kz["kowal"][0], kz["e"][2] - kz["kowal"][2]), kz["zasieg"] + 1,
                        "punkt E blisko kowala")
        nazwy = {c[14] for c in SCENA.czesci}
        for n in ("Palenisko", "Żar", "Kowadło", "Sztaba", "Miech skóra", "Stojak słup", "Szyld", "Komin", "Kadź"):
            self.assertIn(n, nazwy)
        self.assertEqual(SCENA.sprawdz(), [], "kontrola jakości sceny kuźni")

    def test_1e_teksty_dla_gracza(self):
        zle = re.compile(r"(swiat/|D-\d|atrybut|Studio|pakiet|KowalProba|_|\bid\b)")
        for k, t in D["teksty"].items():
            for x in (t if isinstance(t, list) else [t]):
                self.assertFalse(zle.search(x), "tekst %s: %r" % (k, x))
        self.assertIn("PRÓBA", D["teksty"]["tytul"])

    def test_1f_odmiana_przy_liczbie(self):
        oczek = {0: ("materiałów", "materiałów"), 1: ("materiał", "materiału"), 2: ("materiały", "materiałów"),
                 3: ("materiały", "materiałów"), 4: ("materiały", "materiałów"), 5: ("materiałów", "materiałów"),
                 11: ("materiałów", "materiałów"), 12: ("materiałów", "materiałów"), 14: ("materiałów", "materiałów"),
                 21: ("materiałów", "materiałów"), 22: ("materiały", "materiałów"), 24: ("materiały", "materiałów"),
                 25: ("materiałów", "materiałów"), 104: ("materiały", "materiałów"), 112: ("materiałów", "materiałów")}
        for n, (m, d) in oczek.items():
            self.assertEqual(LK.ile_materialow(D, n), "%d %s" % (n, m))
            self.assertEqual(LK.ile_materialow_dop(D, n), "%d %s" % (n, d))
        self.assertEqual(LK.komunikat(D, "za_malo_materialow", 1),
                         "Brakuje ci 1 materiału — rozbierz zapasowe przedmioty z walk.")
        # w oknie: koszt i rozbiórka z odmianą, bez skrótu „mat.”
        s = _zestaw("wojownik", 0)
        s["przedmioty"][D["klasy"]["wojownik"]["przedmioty"][0]]["zapas"] = 1
        for w in LK.widok(D, s, "wojownik", LK.zalozone(D, "wojownik", s, None), 0, "")["wiersze"]:
            for pole in ("koszt", "powod", "rozbiorka"):
                self.assertNotIn("mat.", w[pole])
                self.assertIsNone(re.search(r"\b1 materiałów|\b[2-4] materiałów\b(?! —)|\b1 materiały", w[pole]), w[pole])
        teksty = [t for t in D["teksty"].values() if isinstance(t, str)]
        self.assertFalse(any(re.search(r"%d (materia|mat\.)", t) for t in teksty), "liczba przy rzeczowniku bez odmiany")


# ------------------------------------------------------------------------------------------------ 2. balans
def _zestaw(klasa, poziom=0, tylko_podstawowy=False, bez=()):
    s = LK.nowe(D)
    for pid in D["klasy"][klasa]["przedmioty"]:
        if (tylko_podstawowy and not D["przedmioty"][pid]["podstawowy"]) or pid in bez:
            continue
        s["przedmioty"][pid] = {"poziom": poziom, "zapas": 0}
    return s


class TestBalansu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.Ds, cls.LS = _stan()

    def bohater(self, k, L, stan):
        st = self.LS.rozdziel(self.Ds, self.Ds["rozklady"][k], self.LS.pula(self.Ds, L))
        o = self.LS.opis_bohatera(self.Ds, k, L, st)
        if stan is None:
            return o
        m = LK.mod(D, k, stan, LK.zalozone(D, k, stan, None))
        czysty, powod = self.LS.czysty_modyfikator(self.Ds, m)
        self.assertIsNotNone(czysty, "%s %s" % (powod, m))
        return self.LS.opis_z_modyfikatorami(self.Ds, o, self.LS.zloz_modyfikatory(self.Ds, [czysty]))

    def test_2a_podstawowy_zestaw_jak_dzis(self):
        for k in D["klasy"]:
            s = LK.podstawowe(D, LK.nowe(D), k)[0]
            self.assertEqual(LK.mod(D, k, s, LK.zalozone(D, k, s, None)), {}, k)
            for L in range(1, 31):
                self.assertEqual(self.bohater(k, L, s), self.bohater(k, L, None), "%s L%d" % (k, L))

    def test_2b_wpisy_przechodza_walidacje_stanu(self):
        los = random.Random(3)
        for _ in range(400):
            k = los.choice(list(D["klasy"]))
            s = LK.nowe(D)
            for pid in D["klasy"][k]["przedmioty"]:
                if los.random() < 0.7:
                    s["przedmioty"][pid] = {"poziom": los.randint(0, D["ulepszenie"]["maks"]), "zapas": los.randint(0, 3)}
            napis = None if los.random() < 0.3 else ",".join(p for p in D["klasy"][k]["przedmioty"] if los.random() < 0.6)
            m = LK.mod(D, k, s, LK.zalozone(D, k, s, napis))
            czysty, powod = self.LS.czysty_modyfikator(self.Ds, m)
            self.assertIsNotNone(czysty, "%s %s" % (powod, m))
            self.assertEqual(czysty, m)

    def test_2c_bez_tarczy_bez_bloku(self):
        tarcza = next(p for p in D["klasy"]["wojownik"]["podstawowe"] if D["przedmioty"][p]["slot"] == "OffHand")
        s = _zestaw("wojownik", 0, True, bez=(tarcza,))
        self.assertAlmostEqual(LK.mod(D, "wojownik", s, LK.zalozone(D, "wojownik", s, None))["tarcza"], -D["blokTarczy"])
        self.assertEqual(self.bohater("wojownik", 5, s)["tarcza"]["blok"], 0)
        s2 = _zestaw("wojownik", 3)
        self.assertAlmostEqual(self.bohater("wojownik", 5, s2)["tarcza"]["blok"], D["blokTarczy"] + 0.03)

    def test_2d_pelny_zestaw_klas_kosztuje_tyle_samo(self):
        sumy = {}
        for k, Kl in D["klasy"].items():
            sumy[k] = (sum(sum(D["przedmioty"][i]["koszt"]["zloto"]) for i in Kl["przedmioty"]),
                       sum(sum(D["przedmioty"][i]["koszt"]["materialy"]) for i in Kl["przedmioty"]))
        for k in sumy:
            self.assertLess(abs(sumy[k][0] - sumy["wojownik"][0]) / sumy["wojownik"][0], 0.03, sumy)
            self.assertLess(abs(sumy[k][1] - sumy["wojownik"][1]) / sumy["wojownik"][1], 0.06, sumy)

    def test_2e_pelny_zestaw_silniejszy_i_rowny(self):
        """Mała próba silnikiem: pełny zestaw +0 i najwyższy poziom dają więcej niż dziś, a klasy zostają blisko."""
        silnik = _modul("silnik", os.path.join(WALKA, "silnik.py"))
        wyniki = {}
        for k in D["klasy"]:
            for nazwa, s in (("dzis", None), ("pelny0", _zestaw(k, 0)), ("maks", _zestaw(k, D["ulepszenie"]["maks"]))):
                los = random.Random("2e-%s" % k)
                w = 0
                for i in range(240):
                    L = 8 + i % 3
                    o = self.bohater(k, L, s)
                    r = silnik.symuluj(o, {"potwor": ("lesny_troll", "straznik_lasu")[i % 2], "poziom": L + 1},
                                       los.randrange(1, 2 ** 31 - 1))
                    w += r["wynik"] == "wygrana"
                wyniki[(k, nazwa)] = w / 240.0
        for k in D["klasy"]:
            self.assertGreater(wyniki[(k, "pelny0")], wyniki[(k, "dzis")], k)
            self.assertGreater(wyniki[(k, "maks")], wyniki[(k, "pelny0")] + 0.1, k)
        maks = [wyniki[(k, "maks")] for k in D["klasy"]]
        self.assertLess(max(maks) - min(maks), 0.12, wyniki)


# ------------------------------------------------------------------------------------------------ 3. lustro
def luau_logika(logika=LOGIKA):
    import atrapa_roblox as AR
    sw = AR.Swiat()
    Dl = sw.it.wykonaj(DANE_LUAU, "DaneKowala.luau")[0]
    Ll = sw.it.wykonaj(logika, "LogikaKowala.luau")[0]
    return sw, Dl, Ll


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLustra(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sw, cls.Dl, cls.Ll = luau_logika()

    def wolaj(self, nazwa, *argi):
        w = self.sw.wolaj(self.Ll.get(nazwa), *[a if isinstance(a, LM.Tabela) else LM.do_luau(a) for a in argi])
        return [LM.z_luau(x) for x in w]

    def test_3a_przypadki_wzorcowe(self):
        ok, n, zle = self.wolaj("sprawdzPrzypadki", self.Dl)
        self.assertTrue(ok, zle)
        self.assertGreater(n, 150)

    def test_3b_losowe_wywolania(self):
        los = random.Random(11)

        def norm(v):
            return json.loads(json.dumps(v)) if v is not None else None

        def rowne(a, b):
            if isinstance(a, dict) and isinstance(b, list) and not b:
                return not a
            if isinstance(b, dict) and isinstance(a, list) and not a:
                return not b
            if isinstance(a, dict) and isinstance(b, dict):
                return set(a) == set(b) and all(rowne(a[k], b[k]) for k in a)
            if isinstance(a, list) and isinstance(b, list):
                return len(a) == len(b) and all(rowne(x, y) for x, y in zip(a, b))
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
                return abs(a - b) < 1e-9
            return a == b
        for _ in range(600):
            k = los.choice(list(D["klasy"]))
            ids = D["klasy"][k]["przedmioty"]
            s = LK.nowe(D)
            for pid in ids:
                if los.random() < 0.65:
                    s["przedmioty"][pid] = {"poziom": los.randint(0, D["ulepszenie"]["maks"]), "zapas": los.randint(0, 2)}
            s["materialy"] = los.randint(0, 12)
            s["bezLupu"] = los.randint(0, D["lup"]["ochrona"])
            napis = None if los.random() < 0.3 else ",".join(p for p in ids + list(D["czesci"]) if los.random() < 0.5)
            pid = los.choice(ids + ["nieznany"])
            zal = LK.zalozone(D, k, s, napis)
            self.assertTrue(rowne(norm(zal), self.wolaj("zalozone", self.Dl, k, s, napis)[0]))
            self.assertTrue(rowne(norm(LK.mod(D, k, s, zal)), self.wolaj("mod", self.Dl, k, s, zal)[0]))
            self.assertEqual(LK.stroj_do_ustawienia(D, k, s, napis), self.wolaj("strojDoUstawienia", self.Dl, k, s, napis)[0])
            self.assertEqual(LK.dostepne(D, s), self.wolaj("dostepne", self.Dl, s)[0])
            ok, w, z = LK.rozbierz(D, s, k, pid)
            wl = self.wolaj("rozbierz", self.Dl, s, k, pid)
            self.assertTrue(rowne([ok, norm(w), z], wl), (ok, w, z, wl))
            ok, w, z = LK.plan_ulepszenia(D, s, k, pid)
            wl = self.wolaj("planUlepszenia", self.Dl, s, k, pid)
            self.assertTrue(rowne([ok, norm(w), z], wl), (ok, w, z, wl))
            rg = los.choice(["zwykly", "rzadki", "straznik"])
            l1, l2 = los.random(), los.random()
            w, lup = LK.lup(D, s, k, rg, l1, l2)
            wl = self.wolaj("lup", self.Dl, s, k, rg, l1, l2)
            self.assertTrue(rowne(norm(w), wl[0]) and rowne(norm(lup), wl[1] if len(wl) > 1 else None), (w, lup, wl))
            zl = los.randint(0, 2000)
            self.assertTrue(rowne(norm(LK.widok(D, s, k, zal, zl, "Broń 30")),
                                  self.wolaj("widok", self.Dl, s, k, zal, zl, "Broń 30")[0]))
            r = los.choice([0, 1, 2, 3, 4, 5, 6, 7, 9, -1])
            self.assertEqual(LK.ranga(D, r), self.wolaj("ranga", self.Dl, r)[0])

    def test_3d_losowe_wywolania_z_kupionymi(self):
        """D-106: te same funkcje na danych gracza z przedmiotami wszystkich stopni + kupno, oferta, reguła zakładania."""
        los = random.Random(23)

        def norm(v):
            return json.loads(json.dumps(v)) if v is not None else None
        for _ in range(250):
            k = los.choice(list(D["klasy"]))
            ids = D["klasy"][k]["wszystkie"]
            s = LK.nowe(D)
            for pid in ids:
                if los.random() < 0.4:
                    s["przedmioty"][pid] = {"poziom": los.randint(0, D["ulepszenie"]["maks"]), "zapas": los.randint(0, 1)}
            s["materialy"] = los.randint(0, 12)
            czesci = [c for c, cal in D["czesci"].items() if D["przedmioty"][cal]["klasa"] == k]
            napis = None if los.random() < 0.3 else ",".join(p for p in ids + czesci if los.random() < 0.35)
            zal = LK.zalozone(D, k, s, napis)
            self.assertEqual(len(zal), len({D["przedmioty"][i]["slot"] for i in zal}), "jeden przedmiot na slot")
            self.assertEqual(norm(zal) or {}, self.wolaj("zalozone", self.Dl, k, s, napis)[0] or {})
            ml = self.wolaj("mod", self.Dl, k, s, zal)[0]
            self.assertEqual(json.dumps(norm(LK.mod(D, k, s, zal)) or {}, sort_keys=True), json.dumps(ml or {}, sort_keys=True))
            self.assertEqual(LK.stroj_do_ustawienia(D, k, s, napis), self.wolaj("strojDoUstawienia", self.Dl, k, s, napis)[0])
            self.assertEqual(LK.dostepne(D, s), self.wolaj("dostepne", self.Dl, s)[0])
            zl, poziom = los.randint(0, 3000), los.randint(1, 30)
            self.assertEqual(LK.mozna_ulepszyc(D, k, s, zl), self.wolaj("moznaUlepszyc", self.Dl, k, s, zl)[0])
            self.assertEqual(norm(LK.widok(D, s, k, zal, zl, "")), self.wolaj("widok", self.Dl, s, k, zal, zl, "")[0])
            self.assertEqual(norm(LK.oferta(D, s, k, poziom, zl, zal)), self.wolaj("oferta", self.Dl, s, k, poziom, zl, zal)[0])
            self.assertEqual(LK.stac_na(D, s, k, poziom, zl), self.wolaj("stacNa", self.Dl, s, k, poziom, zl)[0])
            pid = los.choice(ids + czesci + ["nieznany", los.choice(D["kolejnosc"])])
            ok, w, info = LK.kup(D, s, k, poziom, zl, pid)
            wl = self.wolaj("kup", self.Dl, s, k, poziom, zl, pid)
            self.assertEqual([ok, norm(w), norm(info)], wl, pid)
            if ok:
                self.assertEqual(w["przedmioty"][pid], {"poziom": 0, "zapas": 0})
                self.assertEqual(len(w["przedmioty"]), len(s["przedmioty"]) + 1)
            x = los.choice(ids)
            self.assertEqual(LK.czy_zalozyc(D, zal, x), self.wolaj("czyZalozyc", self.Dl, zal, x)[0])
            self.assertEqual(LK.stroj_z_przedmiotem(D, napis, x), self.wolaj("strojZPrzedmiotem", self.Dl, napis, x)[0])
            po = LK.zalozone(D, k, dict(s, przedmioty=dict(s["przedmioty"], **{x: {"poziom": 0, "zapas": 0}})),
                             LK.stroj_z_przedmiotem(D, napis, x))
            self.assertIn(x, po, "założony ręcznie przedmiot liczy się w swoim slocie")

    def test_3c_zepsute_wersje_wykryte(self):
        zepsute = [
            ("w.materialy += zysk", "w.materialy += zysk + 1"),                       # rozbiórka daje za dużo
            ("K.zloto[poziom + 1]", "K.zloto[poziom]"),                                # koszt o poziom za tani
            ("suma.tarcza = (suma.tarcza or 0) - D.blokTarczy", "suma.tarcza = (suma.tarcza or 0)"),  # tarcza za darmo
            ('return false, "za_malo_zlota", P.cena - zloto', 'return false, "za_malo_zlota", P.cena'),  # zła brakująca kwota
            ("return Z.nrStopnia < P.nrStopnia", "return Z.nrStopnia > P.nrStopnia"),       # reguła zakładania na odwrót
        ]
        for stare, nowe in zepsute:
            self.assertEqual(LOGIKA.count(stare), 1, stare)
            sw, Dl, Ll = luau_logika(LOGIKA.replace(stare, nowe))
            try:
                w = sw.wolaj(Ll.get("sprawdzPrzypadki"), Dl)
                ok = w[0]
            except Exception:  # noqa: BLE001 — błąd wykonania też jest wykryciem
                ok = False
            self.assertFalse(ok, "zepsuta logika przeszła: %s" % nowe)


# ------------------------------------------------------------------------------------------------ 4. rig kowala
def rig_kowala():
    import atrapa_roblox as AR
    sw = AR.Swiat()
    return LM.z_luau(sw.it.wykonaj(czytaj(ZRODLA, "RigKowal.luau"), "RigKowal.luau")[0])


def _obr(rx, ry, rz):
    from swiat.biblioteka.scena import macierz_obrotu
    return macierz_obrotu(math.degrees(rx), math.degrees(ry), math.degrees(rz))


def _mul(a, b):
    from swiat.biblioteka.scena import mnoz, razy_wektor
    v = razy_wektor(a[0], b[1])
    return (mnoz(a[0], b[0]), tuple(a[1][i] + v[i] for i in range(3)))


def _inv(a):
    from swiat.biblioteka.scena import razy_wektor
    Rt = tuple(tuple(a[0][j][i] for j in range(3)) for i in range(3))
    t = razy_wektor(Rt, a[1])
    return (Rt, (-t[0], -t[1], -t[2]))


I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def poza_rigu(R, klip, f):
    """Ramki kości rigu w klatce f klipu (jak RigKowala: C0 · Transform · C1⁻¹, korzeń w hrp)."""
    kl = R["klipy"][klip]
    wiersz = kl["klatki"][f]
    tr = {}
    for j, ki in enumerate(kl["kosci"]):
        o = j * 6
        tr[ki] = (_obr(wiersz[o + 3], wiersz[o + 4], wiersz[o + 5]), (wiersz[o], wiersz[o + 1], wiersz[o + 2]))
    hrp = tuple(R["hrp"])
    kosci = {0: (I3, hrp)}
    for i, k in enumerate(R["kosci"], 1):
        rodzic, staw, srodek = k[1], k[2:5], k[5:8]
        srp = hrp if rodzic == 0 else tuple(R["kosci"][rodzic - 1][5:8])
        C0 = (I3, tuple(staw[a] - srp[a] for a in range(3)))
        C1 = (I3, tuple(staw[a] - srodek[a] for a in range(3)))
        kosci[i] = _mul(_mul(_mul(kosci[rodzic], C0), tr.get(i, (I3, (0, 0, 0)))), _inv(C1))
    return kosci


def czesci_w_pozie(R, kosci):
    w = []
    for c in R["czesci"]:
        ib = c[0]
        spoczynek = (I3, tuple(R["kosci"][ib - 1][5:8]))
        pr = (_obr(c[6], c[7], c[8]), tuple(c[3:6]))
        w.append((c[2], _mul(kosci[ib], _mul(_inv(spoczynek), pr)), c[9:12]))
    return w


class TestRigu(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.R = rig_kowala()

    def test_4a_klipy_i_nic_pod_ziemia(self):
        for klip in ("spoczynek", "kucie", "radosc"):
            self.assertIn(klip, self.R["klipy"])
            for f in range(len(self.R["klipy"][klip]["klatki"])):
                for nazwa, (Rm, t), s in czesci_w_pozie(self.R, poza_rigu(self.R, klip, f)):
                    pol = sum(abs(Rm[1][i]) * s[i] for i in range(3)) / 2
                    self.assertGreater(t[1] - pol, -0.06, "%s %s kl.%d" % (klip, nazwa, f))

    def test_4b_mlot_trafia_w_kowadlo(self):
        kl = self.R["klipy"]["kucie"]
        f = round(14 / (30 / (len(kl["klatki"]) - 1)))       # klatka 14 modelu (uderzenie) w próbkach co 2.
        twarz = next(t for n, (_r, t), _s in czesci_w_pozie(self.R, poza_rigu(self.R, "kucie", f)) if n == "Obuch twarz")
        kz = D["kuznia"]
        a = math.radians(kz["kowalRy"])
        x = kz["kowal"][0] + math.cos(a) * twarz[0] + math.sin(a) * twarz[2]
        z = kz["kowal"][2] - math.sin(a) * twarz[0] + math.cos(a) * twarz[2]
        y = kz["kowal"][1] + twarz[1]
        blat = next(c for c in SCENA.czesci if c[14] == "Kowadło blat")
        R = _obr(blat[5], blat[6], blat[7])
        lok = [sum(R[j][i] * ((x, y, z)[j] - blat[2 + j]) for j in range(3)) for i in range(3)]
        self.assertLess(abs(lok[0]), blat[8] / 2 + 0.1, "młot obok kowadła (wzdłuż): %s" % lok)
        self.assertLess(abs(lok[2]), blat[10] / 2 + 0.15, "młot obok kowadła (w poprzek): %s" % lok)
        self.assertLess(abs(lok[1]), 0.5, "młot nad / pod blatem: %s" % lok)


# ------------------------------------------------------------------------------------------------ 5. serwery w atrapie
class _Wywolanie:
    def __init__(self, sw, inst):
        self.sw, self.inst = sw, inst

    def __call__(self, _s, *argi):
        fn = self.inst.t.get("OnInvoke")
        if fn is None:
            return None
        w = self.sw.wolaj(fn, *argi)
        return w[0] if w else None


class SerweryOffline:
    """Prawdziwe SerwerKowala, SerwerStanu i SerwerStrojow w jednym interpreterze z atrapą Roblox (sama atrapa, bez
    testów — używają jej też testy sklepu swiat/sklep_proba)."""

    def uruchom(self, stan_gracza=True, stroje=True, zloto=0, klasa="Warrior"):
        import atrapa_roblox as AR
        self.AR = AR
        sw = AR.Swiat()
        g = sw.it.globalne.z
        g["task"].set("wait", lambda *a: None)
        self.losy = []
        losy = LM.Tabela()

        def nowy(*_):
            t = LM.Tabela()
            t.set("NextNumber", lambda _s: self.losy.pop(0) if self.losy else 0.99)
            return t
        losy.set("new", nowy)
        g["Random"] = losy
        bit = LM.Tabela()
        bit.set("band", lambda a, b: float(int(a) & int(b)))
        g["bit32"] = bit
        self.sw = sw
        self.gracz = self.nowy_gracz({"Level": 1, "XP": 0, "Gold": zloto, "Gems": 0, "Class": klasa})
        if stan_gracza:
            self.stan_gracza()
        if stroje:
            self.przymierzalnia()
        self.kontener_kowala()
        return sw

    def nowy_gracz(self, atrybuty):
        AR = self.AR
        gr = AR.Inst(self.sw, "Gracz1", "Player")
        zmiana = AR.Zdarzenie(self.sw)
        gr.t.set("AttributeChanged", zmiana.t)
        stara = gr.ustaw

        def ustaw(n, v):
            przed = gr.atrybuty.get(n)
            stara(n, v)
            if przed != gr.atrybuty.get(n):
                zmiana.odpal(n)
        gr.ustaw = ustaw
        gr.t.set("GetAttributes", lambda _s: LM.do_luau(dict(gr.atrybuty)))
        for k, v in atrybuty.items():
            gr.ustaw(k, v)
        self.sw.players.dodaj(gr)
        return gr

    def _potomkowie(self, inst):
        w = []
        for d in inst.dzieci:
            w.append(d.t)
            w += self._potomkowie(d)
        return w

    def _skrypt(self, kontener, tekst, nazwa):
        s = LM.Tabela()
        s.set("Parent", kontener.t)
        self.sw.it.globalne.z["script"] = s
        self.sw.it.wykonaj(tekst, nazwa)

    def stan_gracza(self):
        AR = self.AR
        ZBS = _modul("zbuduj_stanu_test_kowala", os.path.join(STAN, "zbuduj.py"))
        k, inne = AR.kontener_stanu(self.sw, {"DaneStanu": czytaj(STAN, "zrodla", "DaneStanu.luau"),
                                              "LogikaStanu": czytaj(STAN, "zrodla", "LogikaStanu.luau")}, ZBS.INNE)
        for o in inne.values():
            if o.klasa == "BindableFunction":
                o.t.set("Invoke", _Wywolanie(self.sw, o))
        if not self.sw.replicated.dziecko("Shared"):
            shared = AR.Inst(self.sw, "Shared", "Folder", self.sw.replicated)
            self.sw.modul(shared, "ClassData", wartosc=LM.do_luau({"Classes": []}))
        self.kstan, self.inne = k, inne
        self.sw.it.wykonaj(czytaj(STAN, "zrodla", "SerwerStanu.server.luau"), "SerwerStanu.server.luau")

    def przymierzalnia(self):
        AR = self.AR
        k = AR.Inst(self.sw, "StrojeProba", "Folder", self.sw.workspace)
        k.ustaw("Wygenerowane", True)
        f = {n: AR.Inst(self.sw, n, "Folder", k) for n in ("Moduly", "Zdalne", "Sygnaly")}
        self.sw.modul(f["Moduly"], "DaneStrojow", czytaj(STROJE, "zrodla", "DaneStrojow.luau"))
        self.sw.modul(f["Moduly"], "LogikaStrojow", czytaj(STROJE, "zrodla", "LogikaStrojow.luau"))
        # moduły stopni przymierzalni (D-106: DaneStrojowLas / Bagno / Dzungla) — scala je sam DaneStrojow
        for plik in sorted(glob.glob(os.path.join(STROJE, "zrodla", "DaneStrojow?*.luau"))):
            self.sw.modul(f["Moduly"], os.path.basename(plik)[:-len(".luau")], czytaj(plik))
        self.zmien = AR.Inst(self.sw, "ZmienStroj", "RemoteFunction", f["Zdalne"])
        st = AR.Inst(self.sw, "SterowanieSerwera", "BindableFunction", f["Sygnaly"])
        st.t.set("Invoke", _Wywolanie(self.sw, st))
        k.t.set("GetDescendants", lambda _s: AR.lista(self._potomkowie(k)))
        self.kstroje = k
        self._skrypt(k, czytaj(STROJE, "zrodla", "SerwerStrojow.server.luau"), "SerwerStrojow.server.luau")

    def kontener_kowala(self):
        AR = self.AR
        kp = AR.Inst(self.sw, "KowalProba", "Folder", self.sw.workspace)
        kp.ustaw("Wygenerowane", True)
        f = {n: AR.Inst(self.sw, n, "Folder", kp) for n in ("Moduly", "Zdalne", "Sygnaly", "Kuznia")}
        self.sw.modul(f["Moduly"], "DaneKowala", DANE_LUAU)
        self.sw.modul(f["Moduly"], "LogikaKowala", LOGIKA)
        self.kuznia = AR.Inst(self.sw, "Kuznia", "RemoteFunction", f["Zdalne"])
        self.ev = AR.Inst(self.sw, "ZdarzeniaKowala", "RemoteEvent", f["Zdalne"])
        self.ev.t.set("FireClient", lambda _s, gracz, *a: self.sw.do_klienta.append((gracz, [AR.py(x) for x in a])))
        self.ster = AR.Inst(self.sw, "SterowanieSerwera", "BindableFunction", f["Sygnaly"])
        AR.Inst(self.sw, "SterowanieKlienta", "BindableFunction", f["Sygnaly"])
        self.sklep_f = AR.Inst(self.sw, "Sklep", "BindableFunction", f["Sygnaly"])
        self.sklep_f.t.set("Invoke", _Wywolanie(self.sw, self.sklep_f))
        e = AR.Inst(self.sw, "E", "BasePart", f["Kuznia"])
        self.pp = AR.Inst(self.sw, "Podpowiedz", "ProximityPrompt", e)
        self.pp.t.set("Enabled", False)
        self.pp.ustaw("Akcja", "kowal")
        kp.t.set("GetDescendants", lambda _s: AR.lista(self._potomkowie(kp)))
        self.kp = kp
        self._skrypt(kp, SERWER, "SerwerKowala.server.luau")

    # --- pomocnicze
    def atr(self, n, gr=None):
        v = (gr or self.gracz).atrybuty.get(n)
        return int(v) if isinstance(v, float) and v == int(v) else v

    def hak(self, *argi):
        w = self.sw.wolaj(self.ster.t.get("OnInvoke"), *[a if isinstance(a, LM.Tabela) else LM.do_luau(a) for a in argi])
        return LM.z_luau(w[0]) if w else None

    def kuznia_(self, akcja, pid=None, czas=1.0):
        self.sw.krok(czas)
        w = self.sw.wolaj(self.kuznia.t.get("OnServerInvoke"), self.gracz.t, akcja, pid)
        return LM.z_luau(w[0]) if w else None

    def stroj(self, akcja, klasa, arg=None):
        self.sw.krok(1.0)
        w = self.sw.wolaj(self.zmien.t.get("OnServerInvoke"), self.gracz.t, akcja, klasa, arg)
        return LM.z_luau(w[0]) if w else None

    def mody(self):
        f = self.inne["Modyfikatory"]
        w = self.sw.wolaj(f.t.get("OnInvoke"), "czytaj", self.gracz.t)
        return LM.z_luau(w[0])

    def bohater_stanu(self):
        f = self.inne["Bohater"]
        w = self.sw.wolaj(f.t.get("OnInvoke"), self.gracz.t)
        return LM.z_luau(w[0])

    def postaw(self, x=None, z=None):
        AR = self.AR
        e = D["kuznia"]["e"]
        postac = AR.Inst(self.sw, "Postac", "Model")
        hrp = AR.Inst(self.sw, "HumanoidRootPart", "BasePart", postac)
        hrp.t.set("Position", LM.do_luau({"X": e[0] + 1 if x is None else x, "Y": 3, "Z": e[2] + 1 if z is None else z}))
        self.gracz.t.set("Character", postac.t)

    def od_serwera(self, polecenie):
        return [a for _g, a in self.sw.do_klienta if a and a[0] == polecenie]

    def wygrana(self, tokeny=1, kraina="las"):
        n = (self.atr("TokenyKrainy_" + kraina) or 0) + tokeny
        self.gracz.ustaw("TokenyKrainy_" + kraina, float(n))

    def sklep(self, polecenie, pid=None):
        w = self.sw.wolaj(self.sklep_f.t.get("OnInvoke"), polecenie, self.gracz.t, pid)
        return LM.z_luau(w[0]) if w else None


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestSerweraOffline(SerweryOffline, unittest.TestCase):
    # --- testy
    def test_5a_start_podstawowy_zestaw_jak_dzis(self):
        self.uruchom()
        self.assertEqual(self.kp.atrybuty.get("SerwerKowalaGotowy"), True)
        n = sum(len(v) for v in D["przypadki"].values())
        self.assertTrue(str(self.kp.atrybuty.get("ZgodnoscLogikiKowala")).startswith("OK"))
        self.assertTrue(self.pp.t.get("Enabled"))
        self.assertEqual(self.kp.atrybuty.get("StanGraczaPodlaczony"), True)
        podst = D["klasy"]["wojownik"]["podstawowe"]
        self.assertEqual(self.atr("KowalDostepne"), ",".join(p for p in D["kolejnosc"] if p in podst))
        self.assertEqual(self.atr("KowalMaterialy"), 0)
        stroj = self.atr("StrojProba_wojownik")
        self.assertIsNotNone(stroj)
        for p in podst:
            self.assertIn(p, stroj.split(","))
        m = self.mody()
        self.assertIn("kowal", m["zrodla"])
        self.assertEqual(m["bron"], 0)
        self.assertEqual(m["tarcza"], 0)
        self.assertEqual(self.bohater_stanu()["tarcza"]["blok"], D["blokTarczy"])
        self.assertEqual(self.sw.ostrzezenia, [])
        self.assertGreater(n, 100)

    def test_5b_lup_z_tokenow_nowy_przedmiot_zalozony(self):
        self.uruchom()
        przed = self.bohater_stanu()
        self.losy = [0.0, 0.5]                       # szansa trafiona, przedmiot ze środka listy klasy
        self.wygrana(1)
        lista = D["klasy"]["wojownik"]["przedmioty"]
        pid = lista[int(0.5 * len(lista))]
        self.assertFalse(D["przedmioty"][pid]["podstawowy"], pid)
        st = self.hak("stan", self.gracz.t)
        self.assertIn(pid, st["dane"]["przedmioty"])
        self.assertIn(pid, self.atr("StrojProba_wojownik").split(","), "nowy przedmiot od razu założony")
        self.assertIn(pid, self.atr("KowalDostepne").split(","))
        lup = self.od_serwera("lup")
        self.assertEqual(lup[-1], ["lup", D["przedmioty"][pid]["nazwa"], True])
        po = self.bohater_stanu()
        self.assertNotEqual(przed, po, "przedmiot z łupu zmienia bohatera walki")
        # wygrana bez trafienia: licznik ochrony rośnie, nic nie wypada
        self.losy = [0.99, 0.0]
        self.wygrana(2)
        self.assertEqual(self.hak("stan", self.gracz.t)["dane"]["bezLupu"], 1)
        # przyrost spoza zakresu (wczytanie / zbiór walk) — bez losowania
        self.losy = [0.0, 0.0]
        self.wygrana(40)
        self.assertEqual(self.hak("stan", self.gracz.t)["dane"]["bezLupu"], 1)
        self.assertEqual(len(self.od_serwera("lup")), 1)

    def test_5c_rozbiorka_i_zasieg(self):
        self.uruchom()
        miecz = D["klasy"]["wojownik"]["przedmioty"][0]
        self.losy = [0.0, 0.0]                       # pierwszy przedmiot listy = miecz (już posiadany) → zapas
        self.wygrana(1)
        self.assertEqual(self.od_serwera("lup")[-1][2], False)
        self.assertEqual(self.atr("KowalZapasy"), 1)
        r = self.kuznia_("rozbierz", miecz)
        self.assertEqual(r["powod"], "daleko", "bez postaci przy kowalu")
        self.postaw(D["kuznia"]["e"][0] + 30, D["kuznia"]["e"][2])
        self.assertEqual(self.kuznia_("rozbierz", miecz)["powod"], "daleko")
        self.postaw()
        r = self.kuznia_("rozbierz", miecz)
        self.assertTrue(r["ok"], r)
        self.assertEqual(self.atr("KowalMaterialy"), D["rozbiorka"]["materialy"])
        self.assertEqual(self.atr("KowalZapasy"), 0)
        self.assertEqual(self.kuznia_("rozbierz", miecz)["powod"], "brak_zapasu")
        self.assertEqual(self.kuznia_("rozbierz", "kot_mag_kostur")["powod"], "nieznany_przedmiot", "przedmiot innej klasy")
        self.assertEqual(self.kuznia_("cos")["powod"], "zla_akcja")
        self.assertEqual(self.kuznia_("rozbierz", "x" * 80)["powod"], "zly_argument")

    def test_5d_ulepszenie_zloto_i_materialy(self):
        self.uruchom(zloto=0)
        miecz = D["klasy"]["wojownik"]["przedmioty"][0]
        self.postaw()
        k = LK.koszt(D, miecz, 0)
        r = self.kuznia_("ulepsz", miecz)
        self.assertEqual(r["powod"], "za_malo_materialow")
        self.assertEqual(self.atr("Gold"), 0)
        self.assertEqual(self.hak("materialy", self.gracz.t, 5)["ok"], True)
        r = self.kuznia_("ulepsz", miecz)
        self.assertEqual(r["powod"], "za_malo_zlota", r)
        self.assertIn(str(k["zloto"]), r["tekst"])
        self.assertEqual(self.atr("Gold"), 0, "Złoto nigdy poniżej zera")
        self.assertEqual(self.atr("KowalMaterialy"), 5, "odmowa niczego nie zabiera")
        self.assertEqual(self.atr("KowalMoznaUlepszyc"), False, "bez Złota — wskazówka nie kusi ulepszeniem")
        self.assertEqual(self.atr("KowalUlepszen"), 0)
        self.gracz.ustaw("Gold", float(k["zloto"] + 7))
        self.assertEqual(self.atr("KowalMoznaUlepszyc"), True, "Złoto przyszło — atrybut od razu")
        przed = self.bohater_stanu()["bron"]["obrazenia"]
        r = self.kuznia_("ulepsz", miecz)
        self.assertTrue(r["ok"], r)
        self.assertEqual(self.atr("Gold"), 7)
        self.assertEqual(self.atr("KowalMaterialy"), 5 - k["materialy"])
        self.assertEqual(self.hak("stan", self.gracz.t)["dane"]["przedmioty"][miecz]["poziom"], 1)
        self.assertEqual(self.atr("KowalUlepszen"), 1, "po pierwszym ulepszeniu wskazówka „kowal” znika")
        self.assertEqual(self.bohater_stanu()["bron"]["obrazenia"], przed + D["przedmioty"][miecz]["krok"]["bron"])
        self.assertEqual(self.od_serwera("ulepszono")[-1], ["ulepszono", miecz, 1])
        w = r["widok"]
        wiersz = next(x for x in w["wiersze"] if x["id"] == miecz)
        self.assertEqual(wiersz["poziom"], 1)
        self.assertTrue(w["bohater"].startswith(D["teksty"]["bohater"].split("%")[0]))

    def test_5e_limit_zapytan(self):
        self.uruchom()
        self.postaw()
        self.sw.krok(1)
        a = LM.z_luau(self.sw.wolaj(self.kuznia.t.get("OnServerInvoke"), self.gracz.t, "widok", None)[0])
        b = LM.z_luau(self.sw.wolaj(self.kuznia.t.get("OnServerInvoke"), self.gracz.t, "widok", None)[0])
        self.assertTrue(a["ok"])
        self.assertEqual(b["powod"], "za_szybko")

    def test_5f_zmiana_klasy(self):
        self.uruchom()
        self.gracz.ustaw("Class", "Mage")
        st = self.hak("stan", self.gracz.t)
        self.assertEqual(st["klasa"], "mag")
        for p in D["klasy"]["mag"]["podstawowe"]:
            self.assertIn(p, st["dane"]["przedmioty"])
        self.assertIsNotNone(self.atr("StrojProba_mag"))
        self.assertNotIn("tarcza", self.mody() if self.mody()["tarcza"] else {}, "Mag bez tarczy")

    def test_5g_zdjeta_tarcza_i_przymierzalnia_tylko_posiadane(self):
        self.uruchom()
        r = self.stroj("zdejmij", "wojownik", "OffHand")
        self.assertTrue(r["ok"], r)
        self.assertAlmostEqual(self.mody()["tarcza"], -D["blokTarczy"])
        self.assertEqual(self.bohater_stanu()["tarcza"]["blok"], 0)
        helm = next(p for p in D["klasy"]["wojownik"]["przedmioty"] if D["przedmioty"][p]["slot"] == "Helmet")
        r = self.stroj("zaloz", "wojownik", helm)
        self.assertEqual(r["powod"], "nie_masz", "przymierzalnia nie zakłada nieposiadanego")
        # przy kowalu inne odmowy zostają jak dawniej (próba strojów S04): cudza klasa, część zbroi, nieznany przedmiot
        self.assertEqual(self.stroj("zaloz", "wojownik", "kot_mag_kapelusz")["powod"], "przedmiot_innej_klasy")
        self.assertEqual(self.stroj("zaloz", "wojownik", "rycerz_nogawice")["powod"], "czesc_zbroi")
        self.assertEqual(self.stroj("zaloz", "wojownik", "nie_ma")["powod"], "nieznany_przedmiot")
        self.assertEqual(self.stroj("dawny", "wojownik")["powod"], "dawny_niedostepny")
        r = self.stroj("zestaw", "wojownik", "komplet")
        self.assertTrue(r["ok"], r)
        self.assertNotIn(helm, r["stroj"].split(","))
        self.assertIn("rycerz_nogawice", r["stroj"].split(","), "część zbroi idzie z całością")
        self.assertEqual(self.mody()["tarcza"], 0, "tarcza znowu założona")

    def test_5h_przymierzalnia_bez_kowala_jak_dawniej(self):
        self.uruchom(stan_gracza=False)
        self.assertIsNone(self.atr("KowalDostepne"))
        helm = next(p for p in D["klasy"]["wojownik"]["przedmioty"] if D["przedmioty"][p]["slot"] == "Helmet")
        r = self.stroj("zaloz", "wojownik", helm)
        self.assertTrue(r["ok"], r)
        self.assertTrue(self.stroj("dawny", "wojownik")["ok"])

    def test_5i_bez_stanu_gracza(self):
        self.uruchom(stan_gracza=False)
        self.postaw()
        r = self.kuznia_("widok")
        self.assertEqual(r["powod"], "brak_stanu")
        self.assertEqual(r["tekst"], D["teksty"]["nieczynna"])
        self.assertEqual(self.kp.atrybuty.get("StanGraczaPodlaczony"), False)
        self.wygrana(1)
        self.assertEqual(self.od_serwera("lup"), [])
        self.assertEqual([o for o in self.sw.ostrzezenia if "KowalProba" in o], [])

    def test_5j_stan_gracza_pozniej_i_przebudowa(self):
        self.uruchom(stan_gracza=False)
        self.stan_gracza()
        self.sw.krok(D["stan"]["coIleS"] + 0.1)
        self.assertEqual(self.kp.atrybuty.get("StanGraczaPodlaczony"), True)
        self.assertIsNotNone(self.atr("KowalDostepne"))
        self.assertIn("kowal", self.mody()["zrodla"])
        # przebudowa StanGracza: nowy kontener — wpis kowala wraca bez działania gracza
        self.kstan.usun()
        self.stan_gracza()
        self.sw.krok(D["stan"]["coIleS"] + 0.1)
        self.assertIn("kowal", self.mody()["zrodla"])

    def test_5l_wejscie_sklepu(self):
        """D-106: Sygnaly/Sklep — oferta, kupno (Złoto przez WydajZloto), odmowa bez zmian, atrybut SklepStacNa."""
        self.uruchom()
        self.assertEqual(self.kp.atrybuty.get("WejscieSklepu"), True)
        self.gracz.ustaw("Level", 30.0)
        pas = next(i for i in D["klasy"]["wojownik"]["wszystkie"]
                   if D["przedmioty"][i]["nrStopnia"] == 1 and D["przedmioty"][i]["slot"] == "Belt")
        cena = D["przedmioty"][pas]["cena"]
        r = self.sklep("kup", pas)
        self.assertEqual((r["ok"], r["powod"], r["brakuje"]), (False, "za_malo_zlota", cena))
        self.assertNotIn(pas, self.hak("stan", self.gracz.t)["dane"]["przedmioty"])
        self.assertEqual(self.atr("SklepStacNa"), 0)
        self.gracz.ustaw("Gold", float(cena + 5))
        self.assertGreaterEqual(self.atr("SklepStacNa"), 1)
        of = self.sklep("oferta")
        self.assertEqual((of["ok"], of["zloto"], of["poziom"], of["klasa"]), (True, cena + 5, 30, "wojownik"))
        self.assertEqual(len(of["oferta"]), len(D["klasy"]["wojownik"]["wszystkie"]))
        r = self.sklep("kup", pas)
        self.assertTrue(r["ok"], r)
        self.assertEqual((self.atr("Gold"), r["zloto"], r["cena"]), (5, 5, cena))
        self.assertEqual(self.hak("stan", self.gracz.t)["dane"]["przedmioty"][pas], {"poziom": 0, "zapas": 0})
        self.assertEqual(self.sklep("kup", pas)["powod"], "masz")
        self.assertEqual(self.atr("Gold"), 5)
        self.assertEqual(self.kp.atrybuty.get("LicznikKupna"), 1)
        # kupiony przedmiot ulepsza się jak dzisiejsze: jest w oknie kowala gracza
        self.assertIn(pas, [w["id"] for w in self.hak("widok", self.gracz.t)["widok"]["wiersze"]])
        self.assertEqual([o for o in self.sw.ostrzezenia if "KowalProba" in o], [])

    def test_5k_bez_przymierzalni_licza_sie_wszystkie_posiadane(self):
        self.uruchom(stroje=False)
        helm = next(p for p in D["klasy"]["wojownik"]["przedmioty"] if D["przedmioty"][p]["slot"] == "Helmet")
        self.assertTrue(self.hak("daj", self.gracz.t, helm)["ok"])
        st = self.hak("stan", self.gracz.t)
        self.assertIn(helm, st["zalozone"])
        self.assertEqual(self.mody()["pancerz"], D["przedmioty"][helm]["baza"]["pancerz"])


# ------------------------------------------------------------------------------------------------ 6. narzędzia
class TestNarzedzi(unittest.TestCase):
    def test_6a_kontrola_luau(self):
        bledy, _p = SLK.sprawdz_pliki(SLK.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertEqual(bledy, [])
        SLS = _modul("sprawdz_luau_strojow_test_kowala", os.path.join(STROJE, "sprawdz_luau_strojow.py"))
        pliki = [os.path.join(STROJE, "zrodla", p) for p in ("SerwerStrojow.server.luau", "KlientStrojow.client.luau",
                                                             "OknoStrojow.luau")]
        bledy, _p = SLS.sprawdz_pliki(pliki, wypisz=lambda *_: None)
        self.assertEqual(bledy, [], "zmienione pliki przymierzalni")

    def test_6b_zbuduj_sucho_i_kod_budowy(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           timeout=300, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace")[-2000:])
        if LM is not None:
            ZB = _modul("zbuduj_kowala_test", os.path.join(PAKIET, "zbuduj.py"))
            for nazwa, kod in ZB.wszystkie_kody().items():
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()

    def test_6c_bez_sciezek_lokalnych(self):
        # wzorce składane z kawałków, żeby ten plik sam ich nie zawierał
        zakazane = [re.compile(r"[A-Za-z]:\\" + "Users" + r"\\"), re.compile("App" + "Data"), re.compile("/" + "Users/")]
        for root, _d, pliki in os.walk(PAKIET):
            if "__pycache__" in root or os.sep + "klatki" in root:
                continue
            for p in pliki:
                if p.endswith((".py", ".luau", ".json", ".md")):
                    t = czytaj(root, p)
                    for z in zakazane:
                        self.assertIsNone(z.search(t), "%s: %s" % (p, z.pattern))

    def test_6d_proba_play_sprawdz(self):
        sciezka = os.path.join(TESTY, "proba_play.py")
        if not os.path.isfile(sciezka):
            self.skipTest("brak proba_play.py")
        r = subprocess.run([sys.executable, "-B", sciezka, "--sprawdz"], capture_output=True, timeout=300,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace")[-2000:])


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
