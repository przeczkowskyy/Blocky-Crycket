#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy offline pakietu swiat/wskazowki_gry (bez Studio).

    python -B swiat/wskazowki_gry/testy/test_wskazowek.py

1. Dane: generator deterministyczny i aktualny; złe ustawienia wykryte; żadnych napisów dla twórców na ekranie gracza.
2. Logika (Python): kroki zgodne z zamówieniem (a–e), bez StanGracza nie ma kroków o poziomach i treningu.
3. Luau w luau_mini: pliki parsują się; przypadki wzorcowe OK (zepsuty wykryty); losowe stany = lustro Pythona.
4. Klient: każde pole danych, którego używa, istnieje; nic nie wysyła do serwera; kod do Studio parsuje się.
5. Styki z innymi pakietami (tylko odczyt): nazwy atrybutów, modułów i instancji, które klient czyta, istnieją u nich.
6. Bez ścieżek lokalnych i danych prywatnych w plikach pakietu.
"""
import copy
import io
import json
import os
import random
import re
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
ZR = os.path.join(PAKIET, "zrodla")
sys.path.insert(0, PAKIET)
import dane as DANE  # noqa: E402
import logika_wskazowek as LW  # noqa: E402
import sprawdz_luau_wskazowek as SLW  # noqa: E402
import zbuduj as ZB  # noqa: E402

LM = SLW.luau_mini()
_, D = DANE.dane_z_przypadkami()


def czytaj(*czesci):
    with io.open(os.path.join(*czesci), encoding="utf-8") as f:
        return f.read()


KLIENT = czytaj(ZR, "KlientWskazowek.client.luau")
LOGIKA = czytaj(ZR, "LogikaWskazowek.luau")


def bez_komentarzy(t):
    return SLW.SL.rozbierz(t)[0]


# ============================================================================================== 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_generator_deterministyczny_i_aktualny(self):
        ok, D1 = DANE.aktualny()
        self.assertTrue(ok, "zrodla/DaneWskazowek.luau nieaktualny — uruchom dane.py")
        _, D2 = DANE.dane_z_przypadkami()
        self.assertEqual(D1["skrot"], D2["skrot"])
        with tempfile.TemporaryDirectory() as tmp:
            DANE.zapisz(tmp)
            self.assertEqual(czytaj(tmp, DANE.PLIK_LUAU), czytaj(ZR, DANE.PLIK_LUAU))

    def test_1b_zle_ustawienia(self):
        _, D0 = DANE.wczytaj()
        for psuj, opis in [
            (lambda d: d["kroki"]["a_teleport"].update(tekst=""), "pusty tekst"),
            (lambda d: d["kroki"]["b_potwor"].update(cel="gdzies"), "nieznany cel"),
            (lambda d: d["kroki"]["c_straznik"].update(tekst="Docelowe okno robi Paweł (D-093)"), "napis dla twórców"),
            (lambda d: d["kroki"]["e_koniec"].update(tekst="x" * 80), "za długi"),
            (lambda d: d["kroki"].pop("d_trening"), "brak kroku"),
            (lambda d: d["ui"].update(zamknij_px=20), "za mały krzyżyk"),
        ]:
            d = copy.deepcopy(D0)
            psuj(d)
            with self.subTest(opis=opis):
                with self.assertRaises(DANE.BladDanych):
                    DANE.sprawdz(d)

    def test_1c_teksty_dla_gracza(self):
        for kid, k in D["kroki"].items():
            self.assertIsNone(DANE.TWORCY.search(k["tekst"]), (kid, k["tekst"]))
            self.assertLessEqual(len(k["tekst"]), 64, kid)
        napisy = re.findall(r'"([^"\n]*)"', bez_komentarzy(KLIENT))
        for t in napisy:
            if " " in t:  # zdania (nazwy instancji i atrybutów nie mają spacji)
                self.assertIsNone(re.search(r"D-0\d\d|Paweł|próba|bez zapisu", t), t)


# ============================================================================================== 2. logika
def s(**k):
    baza = {"klasa": True, "miejsce": "miasto", "wygrane": 0, "przegrane": 0}
    baza.update(k)
    return baza


class TestLogiki(unittest.TestCase):
    def kid(self, **k):
        w = LW.krok(D, s(**k))
        return w and w["id"]

    def test_2a_kroki_z_zamowienia(self):
        self.assertEqual(self.kid(), "a_teleport")                                   # (a) po wyborze klasy
        self.assertEqual(LW.krok(D, s())["cel"], "teleport")
        self.assertEqual(self.kid(miejsce="las"), "b_potwor")                         # (b) w lesie
        self.assertEqual(self.kid(miejsce="las", wygrane=1, ostatni="wygrana", stan_gracza=True, poziom=2), "c_poziomy")
        self.assertEqual(self.kid(miejsce="las", przegrane=1, ostatni="przegrana", stan_gracza=True,
                                  trening_wzmacnia=True), "d_trening")               # (d) po przegranej
        self.assertEqual(self.kid(miejsce="las", straznik=True), "e_brama")           # (e) po Strażniku

    def test_2b_bez_stanu_gracza_bez_poziomow_i_treningu(self):
        for st in [s(miejsce=m, wygrane=w, przegrane=p, ostatni=o, poziom=7, trenowal=t)
                   for m in ("las", "miasto") for w in (0, 1, 3) for p in (0, 1) for o in (None, "wygrana", "przegrana")
                   for t in (False, True)]:
            w = LW.krok(D, st)
            self.assertNotIn(w["id"], {"c_poziomy", "c_poziomy_miasto", "d_trening", "d_trening_miasto"}, st)
            self.assertNotIn("poziomy", w["tekst"].lower(), st)
            self.assertNotIn("trener", w["tekst"].lower(), st)

    def test_2c_nic_gdy_ukryte_wylaczone_bez_klasy(self):
        for k in ({"ukryte": True}, {"wylaczone": True}, {"klasa": False}):
            for m in ("las", "miasto", "za_brama"):
                self.assertIsNone(LW.krok(D, s(miejsce=m, straznik=True, **k)))

    def test_2d_cele_maja_sens(self):
        for st in [s(miejsce=m, wygrane=w, ostatni=o, straznik=z, stan_gracza=g, trening_wzmacnia=g, poziom=3)
                   for m in ("las", "miasto", "za_brama") for w in (0, 2) for o in (None, "przegrana")
                   for z in (False, True) for g in (False, True)]:
            w = LW.krok(D, st)
            if st["miejsce"] == "miasto":
                self.assertIn(w["cel"], {"teleport", "trener"}, (st, w))
            elif w["cel"] is not None:
                self.assertIn(w["cel"], {"potwor", "straznik", "kamien", "brama"}, (st, w))

    def test_2f_bagno(self):
        bag = dict(kraina="bagno", miejsce="las", straznik=True, bagno=True)
        self.assertEqual(self.kid(miejsce="las", kraina="las", straznik=True, bagno=True), "e_brama_bagno")
        self.assertEqual(LW.krok(D, s(miejsce="las", kraina="las", straznik=True, bagno=True))["cel"], "brama")
        self.assertEqual(self.kid(straznik=True, bagno=True), "e_bagno_miasto")
        self.assertEqual(self.kid(**bag), "b_potwor")
        self.assertEqual(self.kid(wygrane=1, ostatni="wygrana", stan_gracza=True, poziom=12, **bag), "c_poziomy_bagno")
        self.assertIn("Topieli", LW.krok(D, s(wygrane=1, ostatni="wygrana", **bag))["tekst"])
        self.assertEqual(self.kid(straznik_bagna=True, **bag), "e_brama_dzungla")
        self.assertEqual(self.kid(kraina="bagno", miejsce="za_brama", straznik=True, straznik_bagna=True, bagno=True),
                         "e_koniec_bagno")

    def test_2g_jajko(self):
        # 17.11.2026 (swiat/pety_proba): Złoto na pierwsze jajko — znacznik nad inkubatorem w lesie, TELEPORT w mieście
        las = LW.krok(D, s(miejsce="las", kraina="las", wygrane=2, ostatni="wygrana", jajko=True))
        self.assertEqual((las["id"], las["cel"]), ("f_jajko", "jajko"))
        self.assertIn("jajko", las["tekst"])
        miasto = LW.krok(D, s(wygrane=2, ostatni="wygrana", jajko=True, pety=0))
        self.assertEqual((miasto["id"], miasto["cel"]), ("f_jajko_miasto", "teleport"))
        for st in (s(miejsce="las", jajko=True, pety=1), s(miejsce="las", jajko=False), s(miejsce="las"),
                   s(kraina="bagno", miejsce="las", straznik=True, bagno=True, jajko=True),
                   s(miejsce="za_brama", straznik=True, jajko=True)):
            self.assertNotIn(LW.krok(D, st)["id"], {"f_jajko", "f_jajko_miasto"}, st)
        self.assertIsNone(LW.krok(D, s(miejsce="las", jajko=True, ukryte=True)))

    def test_2e_miejsce(self):
        pr = {"x1": 0, "x2": 10, "z1": -5, "z2": 5}
        self.assertEqual(LW.miejsce(5, 0, pr, 8), "las")
        self.assertEqual(LW.miejsce(9, 0, pr, 8), "za_brama")
        self.assertEqual(LW.miejsce(11, 0, pr, 8), "miasto")
        self.assertEqual(LW.miejsce(5, 0, None, 8), "miasto")
        self.assertEqual(LW.miejsce(9, 0, pr, None), "las")
        self.assertEqual(LW.wynik_walki("wygrana"), "wygrana")
        self.assertIsNone(LW.wynik_walki("przerwano"))


# ============================================================================================== 3. Luau
def luau_modul(tekst, nazwa, it=None):
    it = it or LM.Interpreter()
    rs = LM.Tabela()
    rs.set("IsStudio", lambda _self: True)
    game = LM.Tabela()
    game.set("GetService", lambda _self, _n: rs)
    it.globalne.z["game"] = game
    return it, it.wykonaj(tekst, nazwa)[0]


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLuau(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.it, cls.Dl = luau_modul(czytaj(ZR, DANE.PLIK_LUAU), DANE.PLIK_LUAU)
        cls.L = luau_modul(LOGIKA, "LogikaWskazowek.luau", cls.it)[1]

    def wolaj(self, nazwa, *argi):
        return self.it.wywolaj(self.L.get(nazwa), list(argi))

    def test_3a_pliki_parsuja_sie(self):
        bledy, parser = SLW.sprawdz_pliki(SLW.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertTrue(parser)
        self.assertEqual(bledy, [])
        self.assertEqual(len(SLW.pliki_pakietu()), 3)

    def test_3b_przypadki_wzorcowe(self):
        ok, n, bledy = self.wolaj("sprawdzPrzypadki", self.Dl)
        self.assertTrue(ok, LM.z_luau(bledy))
        self.assertEqual(n, len(D["przypadki"]["kroki"]) + len(D["przypadki"]["miejsca"]))
        zepsute = copy.deepcopy(D)
        zepsute["przypadki"]["kroki"][1]["id"] = "b_potwor"
        zepsute["przypadki"]["miejsca"][0]["wynik"] = "miasto"
        ok, _, bledy = self.wolaj("sprawdzPrzypadki", LM.do_luau(zepsute))
        self.assertFalse(ok)
        self.assertEqual(len(LM.z_luau(bledy)), 2)

    def test_3c_losowe_stany_jak_lustro(self):
        rnd = random.Random(1711)
        for _ in range(400):
            st = {"klasa": rnd.random() < 0.9, "ukryte": rnd.random() < 0.1, "wylaczone": rnd.random() < 0.05,
                  "miejsce": rnd.choice(["las", "miasto", "za_brama"]), "wygrane": rnd.choice([0, 0, 1, 4]),
                  "przegrane": rnd.choice([0, 1, 2]), "ostatni": rnd.choice([None, "wygrana", "przegrana"]),
                  "trenowal": rnd.random() < 0.3, "straznik": rnd.random() < 0.2, "stan_gracza": rnd.random() < 0.5,
                  "trening_wzmacnia": rnd.random() < 0.5, "poziom": rnd.choice([None, 1, 3, 9.0, 12.7]),
                  "bagno": rnd.random() < 0.3, "kraina": rnd.choice([None, "las", "bagno"]),
                  "straznik_bagna": rnd.random() < 0.2}
            st = {k: v for k, v in st.items() if v is not None}
            wl = LM.z_luau(self.wolaj("krok", self.Dl, LM.do_luau(st))[0])
            wp = LW.krok(D, st)
            wp = {k: v for k, v in wp.items() if v is not None} if wp else None  # nil nie wraca z Luau
            self.assertEqual(wl or None, wp, st)
        pr = {"x1": 1056, "x2": 2076, "z1": -760, "z2": -640}
        for _ in range(300):
            x, z = rnd.uniform(900, 2200), rnd.uniform(-800, -600)
            br = rnd.choice([None, 2034.0])
            self.assertEqual(self.wolaj("miejsce", x, z, LM.do_luau(pr), br)[0], LW.miejsce(x, z, pr, br))

    def test_3d_kod_do_studio_parsuje_sie(self):
        kody = dict(ZB.wszystkie_kody(D))
        for sciezka, klasa, kontekst, tekst, plik in ZB.zrodla_pakietu():
            kody["skrypt " + plik] = ZB.kod_skryptu(D, sciezka, klasa, kontekst, tekst)
        for nazwa, kod in kody.items():
            pelny = ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(ZB.MIEJSCE)) + kod
            LM.Parser(pelny, nazwa, LM.Interpreter()).program()
            self.assertIsNone(re.search(r"__[A-Z_]+__", kod), nazwa)


# ============================================================================================== 4. klient
class TestKlienta(unittest.TestCase):
    def test_4a_pola_danych_istnieja(self):
        k = bez_komentarzy(KLIENT)
        for pole in set(re.findall(r"\bZ\.(\w+)", k)):
            self.assertIn(pole, D["zrodla"], "Z.%s" % pole)
        for pole in set(re.findall(r"\bU\.(\w+)", k)):
            self.assertIn(pole, D["ui"], "U.%s" % pole)
        for pole in set(re.findall(r"\bD\.czasy\.(\w+)", k)):
            self.assertIn(pole, D["czasy"], "D.czasy.%s" % pole)

    def test_4b_niczego_nie_wysyla_i_nie_zmienia_cudzych(self):
        k = bez_komentarzy(KLIENT)
        for zakaz in ("FireServer", "InvokeServer", "PivotTo", ".Enabled = true", "HUD.Enabled"):
            self.assertNotIn(zakaz, k)
        self.assertEqual(set(re.findall(r"(\w+):SetAttribute\(", k)), {"kontener"})
        self.assertIn('gui.Name = "WskazowkiGry"', k)
        self.assertIn("zamknij.Activated:Connect", k)          # wyłączenie jednym kliknięciem
        self.assertGreaterEqual(D["ui"]["zamknij_px"], 40)

    def test_4c_schowane_w_walce_przelocie_chmurach_minigrze(self):
        k = bez_komentarzy(KLIENT)
        cialo = k.split("local function ukryte()", 1)[1].split("\nend\n", 1)[0]
        for wymog in ("Z.hud", "Z.ekran_walki", "Z.ekran_klasy", "CameraType.Custom", "Z.atrybut_treningu", "Z.chmury_trwa"):
            self.assertIn(wymog, cialo)

    def test_4d_haczyk_testowy(self):
        k = bez_komentarzy(KLIENT)
        for p in ("stan", "wylacz", "wlacz", "zeruj", "ustaw"):
            self.assertIn('polecenie == "%s"' % p, k)


# ============================================================================================== 5. styki
class TestStykow(unittest.TestCase):
    def test_5a_odtwarzacz_walki_ustawia_czytane_atrybuty(self):
        odtw = czytaj(REPO, "swiat", "test_walki2", "zrodla", "OdtwarzaczWalki2.luau")
        Z = D["zrodla"]
        for a in (Z["atrybut_wyniku"], Z["atrybut_stanu_walki"], Z["atrybut_ziarna"]):
            self.assertIn('self:atrybut("%s"' % a, odtw)
        self.assertIn('self:atrybut("%s", "%s")' % (Z["atrybut_stanu_walki"], Z["stan_wyniku"]), odtw)

    def test_5b_biomy_dane_i_punkty(self):
        Z = D["zrodla"]
        pliki = {"las": ("las_pas_gra", "DanePasa.luau"), "bagno": ("bagno_pas_gra", "DaneBagna.luau")}
        for b in Z["biomy"]:
            with self.subTest(biom=b["id"]):
                pakiet, dane = pliki[b["id"]]
                dp = czytaj(REPO, "swiat", pakiet, "zrodla", dane)
                for klucz in ("wejscie =", "brama =", "zaBrama =", "powrot =", "straznik =", "atrybutStraznik = \"%s\""
                              % b["atrybut_straznika"]):
                    self.assertIn(klucz, dp)
                self.assertIn('KONTENER = "%s"' % b["kontener"], czytaj(REPO, "swiat", pakiet, "zbuduj.py"))
                self.assertTrue(b["dane"].startswith(b["kontener"] + "/Moduly/"))
                self.assertTrue(b["kamien"].startswith(b["kontener"] + "/Punkty/"))
        self.assertIn('"Punkty/KamienPowrotu"', czytaj(REPO, "swiat", "las_pas_gra", "zbuduj.py"))
        self.assertEqual(set(Z["walki"].values()), {b["id"] for b in Z["biomy"]})
        self.assertEqual({b["pole_straznika"] for b in Z["biomy"]}, {"straznik", "straznik_bagna"})

    def test_5c_trening_bazar_chmury_hud(self):
        Z = D["zrodla"]
        self.assertIn('gracz:SetAttribute("%s"' % Z["atrybut_treningu"],
                      czytaj(REPO, "swiat", "trening_proba", "zrodla", "SerwerTreningu.server.luau"))
        self.assertIn('("TablicaWejscia/E"', czytaj(REPO, "swiat", "trening_proba", "zbuduj.py"))
        self.assertIn('"training_center"', czytaj(REPO, "swiat", "miasteczko_bazar_gra", "miejsca.json"))
        self.assertIn('SetAttribute("%s"' % Z["chmury_trwa"],
                      czytaj(REPO, "swiat", "teleport_chmury", "zrodla", "KlientTeleportu.client.luau"))
        hud = json.loads(czytaj(REPO, "src", "gui", "HUD.model.json"))
        nazwy = set()

        def zbierz(o):
            nazwy.add(o.get("Name"))
            for c in o.get("Children", []):
                zbierz(c)
        zbierz(hud)
        for n in Z["przycisk_teleportu"].split("/")[1:]:
            self.assertIn(n, nazwy, n)
        self.assertIn('Name = "%s"' % Z["ekran_walki"], czytaj(REPO, "swiat", "test_walki2", "zrodla", "InterfejsWalki2.luau"))

    def test_5e_pety_proba_gdy_jest(self):
        Z = D["zrodla"]
        ust = os.path.join(REPO, "swiat", "pety_proba", "ustawienia.json")
        if not os.path.isfile(ust):
            self.skipTest("brak pakietu swiat/pety_proba — krok o jajku się nie pokaże")
        P = json.loads(czytaj(ust))
        self.assertEqual(Z["pety"], P["kontener"])
        self.assertEqual(Z["atrybut_ceny_jajka"], P["atrybuty_gracza"]["cena"])
        self.assertEqual(Z["atrybut_petow"], P["stan_gracza"]["atrybut_liczby"])
        self.assertEqual(Z["atrybut_zlota"], P["stan_gracza"]["atrybut_zlota"])
        zb = czytaj(REPO, "swiat", "pety_proba", "zbuduj.py")
        kontener, punkty, e = Z["inkubator"].split("/")
        self.assertEqual(kontener, P["kontener"])
        self.assertIn('"%s"' % punkty, zb)
        self.assertIn('punktE(f.%s, "%s"' % (punkty, e), zb)

    def test_5d_stan_gracza_gdy_jest(self):
        Z = D["zrodla"]
        readme = os.path.join(REPO, "swiat", "stan_gracza", "README.md")
        if not os.path.isfile(readme):
            self.skipTest("brak pakietu swiat/stan_gracza — wskazówki działają bez niego")
        t = czytaj(readme)
        for a in (Z["stan_gracza"], Z["stan_gracza_gotowy"], Z["stan_gracza_trening"]):
            self.assertIn(a, t)


# ============================================================================================== 6. prywatność
class TestPrywatnosci(unittest.TestCase):
    def test_6a_bez_sciezek_i_danych_prywatnych(self):
        for korzen, _, pliki in os.walk(PAKIET):
            for p in pliki:
                if not p.endswith((".py", ".luau", ".json", ".md")):
                    continue
                t = czytaj(korzen, p)
                with self.subTest(plik=p):
                    # wzorzec składany z kawałków, żeby nie znalazł sam siebie w tym pliku
                    self.assertIsNone(re.search("[A-Za-z]:[\\\\/]" + "Users|" + "App" + "Data|" + "/ho" + "me/", t))


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
