#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy aren walki BEZ Studio (unittest, ok. 20–40 s).

    python -B swiat/areny_walki/testy/test_aren.py

1. Logika (PRAWDZIWY zrodla/LogikaAren.luau w interpreterze tools/walka/luau_mini.py, z prawdziwym DaneAren.luau):
   każde źródło walki z SerwerWalki2 (TestWalki2, LasPotwory, LasPasGra, BagnoPasGra) dostaje swoją arenę, nieznane
   źródło → nil (stara arena), atrybut BiomAreny ma pierwszeństwo, nieznany biom → mapa źródeł; „wczytana” z progiem
   90%; ruchome detale (ogniki, liście, bąbelki, ptaki) zostają w swoich pierścieniach i wysokościach i nie wchodzą na plac.
2. Dane: DaneAren.luau = plan.py = znaczniki.json = czesci.json (liczby części, modele, położenia, nastrój, detale);
   każdy typ detalu z planu ma obsługę w ArenyWalki.luau; kotwice pyłków istnieją.
3. Areny: zero części w wolnej przestrzeni kamer i nad placem (ta sama kontrola co generuj.py i sprawdz.py), budżet,
   wszystkie części bez kolizji, dalekie bez cienia, wszystko w kole gruntu, profil kamer zgodny z danymi aktorów.
4. Odtwarzacz walki: cienkie wywołania są na miejscu (modulAren, wybierzArene przed schowajObcych, cfSceny z areny
   albo U.scena(), pudło i wykluczenie areny) — bez kontenera ArenyWalki zachowanie jak dotąd.
5. Składnia wszystkich zrodla/*.luau pakietu: bilans bloków, strażnik Studio, parser luau_mini; zbuduj.py --sucho.
Pełna kontrola horyzontu i tła za postaciami (ok. 3 min) — swiat/areny_walki/sprawdz.py.
"""
import json
import math
import os
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
for _s in (REPO, PAKIET, os.path.join(REPO, "tools", "walka"), os.path.join(REPO, "swiat", "las_potwory")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import luau_mini as LM  # noqa: E402
import sprawdz_luau as SL  # noqa: E402
import geom  # noqa: E402
import kamery  # noqa: E402
import plan as P  # noqa: E402
from generuj import DALEKO, naruszenia  # noqa: E402

ZRODLA = os.path.join(PAKIET, "zrodla")
ODTWARZACZ = os.path.join(REPO, "swiat", "test_walki2", "zrodla", "OdtwarzaczWalki2.luau")
SERWER = os.path.join(REPO, "swiat", "test_walki2", "zrodla", "SerwerWalki2.server.luau")


def czytaj(p):
    with open(p, encoding="utf-8-sig") as f:
        return f.read()


def bez_rzutowan(tekst):
    wynik, i, n = [], 0, len(tekst)
    while i < n:
        if tekst.startswith("::", i):
            j = i + 2
            while j < n and tekst[j] in " \t":
                j += 1
            g = 0
            while j < n:
                c = tekst[j]
                if c in "({[":
                    g += 1
                elif c in ")}]":
                    if g == 0:
                        break
                    g -= 1
                elif g == 0 and not (c.isalnum() or c in "_.?<>"):
                    break
                j += 1
            i = j
            continue
        wynik.append(tekst[i])
        i += 1
    return "".join(wynik)


def interpreter():
    I = LM.Interpreter()
    g, rs = LM.Tabela(), LM.Tabela()
    rs.set("IsStudio", lambda self: True)
    g.set("GetService", lambda self, nazwa: rs)
    I.globalne.z["game"] = g
    m = I.globalne.z["math"]
    m.set("sin", lambda x: math.sin(x))
    m.set("cos", lambda x: math.cos(x))
    m.set("pi", math.pi)
    for nazwa in ("DaneAren", "LogikaAren"):
        I.laduj(nazwa, bez_rzutowan(czytaj(os.path.join(ZRODLA, nazwa + ".luau"))))
    return I


def wolaj(I, tab, nazwa, *argi):
    return I.wywolaj(tab.get(nazwa), list(argi))


class Logika(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.I = interpreter()
        cls.L = cls.I.wymagaj("LogikaAren")
        cls.D = cls.I.wymagaj("DaneAren")

    def wybierz(self, zrodlo, biom=None):
        r = wolaj(self.I, self.L, "wybierz", self.D, zrodlo, biom)
        return r[0] if r else None

    def test_zrodla_serwera_maja_arene(self):
        serwer = czytaj(SERWER)
        m = re.search(r"local ZRODLA = \{ \[kontener\.Name\] = true, (.*?) \}", serwer)
        self.assertTrue(m, "nie znalazłem listy ZRODLA w SerwerWalki2")
        zrodla = ["TestWalki2"] + re.findall(r"([A-Za-z]+) = true", m.group(1))
        # 18.11: pakiet Dżungli dopisał DzunglaPasGra do SerwerWalki2.ZRODLA
        oczek = {"TestWalki2": "proba", "LasPotwory": "las", "LasPasGra": "las", "BagnoPasGra": "bagno", "DzunglaPasGra": "dzungla"}
        self.assertEqual(set(zrodla), set(oczek))
        for z, k in oczek.items():
            self.assertEqual(self.wybierz(z), k, z)
        self.assertEqual(self.wybierz("CokolwiekInnego", "dzungla"), "dzungla")

    def test_nieznane_zrodlo_to_stara_arena(self):
        self.assertIsNone(self.wybierz("PustyniaPasGra"))
        self.assertIsNone(self.wybierz(None))
        self.assertIsNone(wolaj(self.I, self.L, "wybierz", None, "TestWalki2", None)[0])

    def test_biom_z_atrybutu_ma_pierwszenstwo(self):
        self.assertEqual(self.wybierz("LasPasGra", "bagno"), "bagno")
        self.assertEqual(self.wybierz("PustyniaPasGra", "las"), "las")
        self.assertEqual(self.wybierz("BagnoPasGra", "pustynia"), "bagno")    # nieznany biom → mapa źródeł
        self.assertIsNone(self.wybierz("PustyniaPasGra", "pustynia"))         # nowa arena = nowe dane, nie kod

    def test_wczytana(self):
        w = lambda o, j: LM.prawda(wolaj(self.I, self.L, "wczytana", float(o), float(j))[0])
        self.assertTrue(w(1000, 1000))
        self.assertTrue(w(1000, 900))
        self.assertFalse(w(1000, 899))
        self.assertFalse(w(0, 0))

    def test_detale_w_swoich_pierscieniach(self):
        for i in range(1, 13):
            for t in (0.0, 1.7, 33.3, 250.0, 9999.5):
                x, y, z = wolaj(self.I, self.L, "ognik", float(i), t, 30.0, 84.0, 0.5, 6.0)
                r = math.hypot(x, z)
                self.assertTrue(27.0 <= r <= 87.0 and 0.5 - 1e-9 <= y <= 6.0 + 1e-9, (i, t, r, y))
                x, y, z, _ = wolaj(self.I, self.L, "lisc", float(i), t, 26.0, 60.0, 6.0, 26.0, 1.4)
                self.assertTrue(math.hypot(x, z) >= P.R_PLAC + 1.0 and 6.0 - 1e-9 <= y <= 26.0 + 1e-9, (i, t))
                x, y, z, s = wolaj(self.I, self.L, "babelek", float(i), t, 25.0, 70.0, -1.8)
                self.assertTrue(25.0 - 1e-9 <= math.hypot(x, z) <= 70.0 + 1e-9 and 0 <= s <= 1.0 and y < 0, (i, t))
                x, y, z, _, sk = wolaj(self.I, self.L, "ptak", float(i), t, 70.0, 120.0, 44.0, 60.0)
                self.assertTrue(70.0 - 1e-9 <= math.hypot(x, z) <= 120.0 + 1e-9 and 42.0 <= y <= 62.0 and -1 <= sk <= 1, (i, t))
                f = wolaj(self.I, self.L, "flaga", float(i), t)[0]
                self.assertLessEqual(abs(f), 0.22)
        # deterministycznie: ta sama chwila → to samo miejsce
        self.assertEqual(wolaj(self.I, self.L, "ognik", 3.0, 12.5, 30.0, 84.0, 0.5, 6.0),
                         wolaj(self.I, self.L, "ognik", 3.0, 12.5, 30.0, 84.0, 0.5, 6.0))

    def test_mieszanie_mgly(self):
        self.assertAlmostEqual(wolaj(self.I, self.L, "miesz", 0.3, 0.46, 1.0)[0], 0.46)
        self.assertAlmostEqual(wolaj(self.I, self.L, "krokWagi", 0.0, 1.0, 2.0, 0.1)[0], 0.2)
        self.assertAlmostEqual(wolaj(self.I, self.L, "krokWagi", 0.95, 1.0, 2.0, 0.1)[0], 1.0)


class Dane(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.luau = czytaj(os.path.join(ZRODLA, "DaneAren.luau"))
        cls.modul = czytaj(os.path.join(ZRODLA, "ArenyWalki.luau"))

    def test_dane_zgodne_z_planem_i_plikami(self):
        I = interpreter()
        D = I.wymagaj("DaneAren")
        areny = D.get("areny")
        for klucz, A in P.ARENY.items():
            with open(os.path.join(PAKIET, klucz, "czesci.json"), encoding="utf-8") as f:
                d = json.load(f)
            with open(os.path.join(PAKIET, klucz, "znaczniki.json"), encoding="utf-8") as f:
                z = json.load(f)
            a = areny.get(klucz)
            self.assertIsNotNone(a, klucz)
            self.assertEqual(int(a.get("czesci")), len(d["czesci"]), klucz)
            self.assertEqual(z["czesci"], len(d["czesci"]), klucz)
            self.assertEqual(a.get("model"), A["model"])
            self.assertEqual(a.get("biom"), A["biom"])
            self.assertEqual(z["scena"]["pozycja"], list(A["O"]))
            self.assertEqual([a.get("scena").get(float(i)) for i in (1, 2, 3)], [float(v) for v in A["O"]])
            n = a.get("nastroj")
            for pole in ("Density", "Offset", "Haze", "Glare"):
                self.assertAlmostEqual(n.get(pole), A["nastroj"][pole])
                self.assertTrue(0 <= A["nastroj"][pole] <= (10 if pole == "Haze" else 1), (klucz, pole))
            for pole in ("Color", "Decay"):
                self.assertRegex(A["nastroj"][pole], r"^[0-9A-F]{6}$")
            for w in A.get("detale", []):
                if w["typ"] == "pylki":
                    self.assertTrue(z["kotwice"].get(w["punkty"]), "%s: brak kotwic pyłków %s" % (klucz, w["punkty"]))

    def test_kazdy_detal_ma_obsluge(self):
        typy = {w["typ"] for A in P.ARENY.values() for w in A.get("detale", [])}
        for t in typy:
            self.assertRegex(self.modul, r'typ == "%s"' % t, "ArenyWalki.luau nie obsługuje detalu %s" % t)

    def test_areny_daleko_od_map_i_od_siebie(self):
        mapy = [("demo", (0, 0), 160), ("TestWalki2", (0, 250), 140), ("las_biom", (0, -1960), 1100),
                ("las_bagno_pas", (2000, -700), 1100), ("dzungla_pas", (3450, -700), 600), ("miasteczko", (0, -700), 400),
                ("trening", (3000, 3000), 400),
                ("teleport", (-5000, 5000), 600), ("wybor_klasy", (0, 4000), 200)]
        punkty = [(k, A["O"]) for k, A in P.ARENY.items()]
        for k, O in punkty:
            for nazwa, (x, z), r in mapy:
                self.assertGreater(math.hypot(O[0] - x, O[2] - z), r + P.R_GRUNT + 200, "%s za blisko %s" % (k, nazwa))
            for k2, O2 in punkty:
                if k2 != k:
                    self.assertGreater(math.hypot(O[0] - O2[0], O[2] - O2[2]), 2 * P.R_GRUNT + 100)


class Areny(unittest.TestCase):
    def test_wolna_przestrzen_budzet_i_cechy(self):
        for klucz, A in P.ARENY.items():
            prof = kamery.profil_areny(klucz)
            with open(os.path.join(PAKIET, klucz, "czesci.json"), encoding="utf-8") as f:
                d = json.load(f)
            sc = [geom.do_sceny(c, A["O"]) for c in d["czesci"]]
            nar = naruszenia(sc, prof)
            self.assertEqual(nar, [], "%s: części w wolnej przestrzeni kamer: %s" % (klucz, nar[:5]))
            self.assertLessEqual(len(d["czesci"]), P.BUDZET, klucz)
            for c in sc:
                cechy = c[15] if len(c) > 15 else 0
                self.assertTrue(cechy & 1, "%s: %s ma kolizję" % (klucz, c[14]))
                if math.hypot(c[2], c[4]) > DALEKO:
                    self.assertTrue(cechy & 2, "%s: daleka część %s rzuca cień" % (klucz, c[14]))
                self.assertLessEqual(math.hypot(c[2], c[4]), P.R_GRUNT + 12, "%s: %s poza gruntem" % (klucz, c[14]))
            # plac: nic nad płytą placu poza gruntem (punkty nad r ≤ 22 i y > 0,12)
            for c in sc:
                if geom.gora(c) > 0.12 and c[13] < 0.98:
                    pts = geom.punkty(c, krok=1.0, maks=12)
                    zle = (pts[:, 0] ** 2 + pts[:, 2] ** 2 < P.R_PLAC ** 2) & (pts[:, 1] > 0.12)
                    self.assertFalse(zle.any(), "%s: %s nad placem" % (klucz, c[14]))

    def test_profil_z_danych_aktorow(self):
        for klucz in P.ARENY:
            plik, przeciwnicy = kamery.plik_profilu(klucz)
            akt = kamery.aktorzy_do_profilu(przeciwnicy)
            with open(plik, encoding="utf-8") as f:
                odcisk = json.load(f)["odcisk"]
            self.assertEqual(odcisk, kamery.odcisk(akt), "%s: profil nieaktualny — python -B swiat/areny_walki/kamery.py %s --odswiez"
                             % (klucz, klucz))
            prof = kamery.profil_areny(klucz)
            self.assertGreater(prof.kamer, 50000)
            # wolna przestrzeń sięga dalej niż dzisiejszy podest (r 22) — kamery ogólne i objazd stoją poza nim
            self.assertGreater(prof.r_max_kamery, 40.0)
        # trzy areny z 17.11 dzielą zamrożony zestaw przeciwników (nowi potwory innych biomów ich nie zmieniają)
        for klucz in ("las", "bagno", "proba"):
            self.assertEqual(kamery.plik_profilu(klucz)[0], kamery.PLIK_PROFILU)
        self.assertNotEqual(kamery.plik_profilu("dzungla")[0], kamery.PLIK_PROFILU)


class Odtwarzacz(unittest.TestCase):
    def test_cienkie_wywolania(self):
        t = czytaj(ODTWARZACZ)
        self.assertRegex(t, r"local function modulAren\(\)")
        self.assertRegex(t, r'workspace:FindFirstChild\("ArenyWalki"\)')
        self.assertRegex(t, r"function Sesja:wybierzArene\(\)")
        self.assertRegex(t, r"self:wybierzArene\(\)\n\tself:schowajObcych\(\)", "wybór areny musi być przed chowaniem obcych")
        self.assertRegex(t, r"self\.cfSceny = if self\.arena then self\.arena\.scena else U\.scena\(\)")
        self.assertRegex(t, r"CFrame\.new\(if self\.arena then self\.arena\.pudloSrodek else U\.OBSZAR_SRODEK\)")
        self.assertRegex(t, r"pcall\(A\.przygotuj,")
        self.assertRegex(t, r"pcall\(uchwyt\.zakoncz, uchwyt\)")
        bez_kom, _ = SL.rozbierz(t)
        self.assertEqual(len(re.findall(r"U\.scena\(\)", bez_kom)), 1, "U.scena() w kodzie tylko jako zapas")

    def test_modul_zwraca_powody_i_sprzata(self):
        m = czytaj(os.path.join(ZRODLA, "ArenyWalki.luau"))
        for powod in ("brak_areny_dla_zrodla", "brak_modelu", "brak_znacznika", "arena_niewczytana", "wylaczone"):
            self.assertIn('"%s"' % powod, m)
        self.assertIn('SetAttribute("CelMglyPasa", 1)', m)
        self.assertIn('SetAttribute("CelMglyPasa", nil)', m)
        self.assertIn("function Uchwyt:zakoncz()", m)
        self.assertNotRegex(m, r"Lighting\.\w+\s*=", "moduł nie zmienia właściwości Lighting (tylko lokalnie Atmosphere)")


class Skladnia(unittest.TestCase):
    def test_zrodla_luau(self):
        bledy = []
        pliki = sorted(f for f in os.listdir(ZRODLA) if f.endswith(".luau"))
        self.assertEqual(pliki, ["ArenyWalki.luau", "DaneAren.luau", "LogikaAren.luau"])
        for f in pliki:
            tekst = czytaj(os.path.join(ZRODLA, f))
            bez_kom, bez_kom_nap = SL.rozbierz(tekst)
            bledy += SL.bilans(bez_kom_nap, f) + SL.straznik(tekst, f)
            try:
                LM.Parser(bez_rzutowan(tekst), f, LM.Interpreter()).program()
            except LM.BladSkladni as e:
                bledy.append("%s: %s" % (f, e))
            if f in ("LogikaAren.luau", "DaneAren.luau") and ("::" in bez_kom_nap or "`" in bez_kom):
                bledy.append("%s: rzutowanie albo odwrotny apostrof w czystym module" % f)
        self.assertEqual(bledy, [])

    def test_zbuduj_na_sucho(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True, timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace"))
        self.assertIn("Persistent", r.stdout.decode("utf-8", "replace"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
