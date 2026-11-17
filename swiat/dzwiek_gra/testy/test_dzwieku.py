#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy pakietu „dźwięk gry” BEZ Studio:  python -B swiat/dzwiek_gra/testy/test_dzwieku.py

Pilnują: katalog w repozytorium = to, co budowniczy wygeneruje dziś (mapa arkusza + ustawienia + identyfikatory),
odcinki = mapa arkusza co do sekundy, zdarzenia używane przez odtwarzacz walki są w katalogu (i odwrotnie),
wpisywanie identyfikatorów (dwie postaci pliku, odmowa złych), strefy muzyki z gruntu map, strażniki i kontrola Luau.
"""
import json
import os
import re
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(PAKIET))
sys.path.insert(0, PAKIET)
import zbuduj as ZB  # noqa: E402


def czytaj(*c):
    with open(os.path.join(REPO, *c), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


UST = ZB.wczytaj_json(ZB.USTAWIENIA)
IDENT = ZB.wczytaj_json(ZB.IDENTYFIKATORY)
MAPA = json.loads(czytaj("assets", "audio", "arkusz", "sfx_arkusz_a.json"))
ODTW = czytaj("swiat", "test_walki2", "zrodla", "OdtwarzaczWalki2.luau")


class TestKatalogu(unittest.TestCase):
    def test_katalog_aktualny(self):
        tekst, _ = ZB.zrodlo_katalogu(ZB.katalog(UST, IDENT))
        self.assertEqual(tekst, czytaj("swiat", "dzwiek_gra", "zrodla", "KatalogDzwiekow.luau"),
                         "zrodla/KatalogDzwiekow.luau nieaktualny — python -B swiat/dzwiek_gra/zbuduj.py --sucho")

    def test_odcinki_z_mapy(self):
        k = ZB.katalog(UST, IDENT)
        self.assertEqual(sorted(k["efekty"]), sorted(MAPA["efekty"]))
        for n, e in MAPA["efekty"].items():
            for pole in ("poczatek", "koniec", "atak", "szczyt"):
                self.assertEqual(k["efekty"][n][pole], e[pole], (n, pole))

    def test_identyfikatory_w_repo_zerowe(self):
        # pliki nie są wgrane — w repozytorium wszystkie identyfikatory 0 (wpisuje je człowiek po wgraniu)
        self.assertEqual(IDENT["arkusz"], 0)
        self.assertTrue(all(v == 0 for v in IDENT["muzyka"].values()))

    def test_strefy_z_gruntu_map(self):
        k = ZB.katalog(UST, IDENT)
        self.assertEqual(k["muzyka"]["strefy"]["bazar"]["prostokaty"], [[882.0, 1066.0, -790.0, -610.0]])
        self.assertEqual(k["muzyka"]["strefy"]["las"]["prostokaty"], [[1066.0, 2066.0, -788.0, -612.0]])
        self.assertEqual(len(k["muzyka"]["strefy"]["bazar"]["utwory"]), 3)
        self.assertEqual(len(k["muzyka"]["strefy"]["las"]["utwory"]), 2)
        self.assertFalse(k["muzyka"]["strefy"]["menu"]["podpiete"])

    def test_zdarzenia_odtwarzacza_w_katalogu(self):
        # zdarzenia, które odtwarzacz gra (lista jawna; każde musi wystąpić w kodzie jako napis w wywołaniu)
        gra = {"cios", "krytyk", "blok", "unik", "kula_ognia", "lodowy_pocisk", "galareta", "rzut", "tarcza",
               "tik_trucizna", "tik_podpalenie", "ogluszenie", "zwyciestwo", "porazka", "awans", "monety", "przycisk",
               "zarodniki"}
        for zd in gra - {"kula_ognia", "lodowy_pocisk"}:
            self.assertRegex(ODTW, r'(dzwiekZdarzenia\(|odcinekZdarzenia\(|then |else |kand = )"%s"' % zd, zd)
        uzyte = gra | set(UST["glosy_potworow"].values())
        self.assertEqual(sorted(uzyte - set(UST["zdarzenia"])), [], "zdarzenia odtwarzacza bez wpisu w ustawieniach")
        # „chmury” to przejście przez chmury (inny pakiet) — w katalogu na później
        self.assertEqual(sorted(set(UST["zdarzenia"]) - uzyte - {"chmury"}), [], "wpisy, których odtwarzacz nie gra")
        self.assertIn('workspace:FindFirstChild("DzwiekGra")', ODTW)
        self.assertIn("PlaybackRegion = NumberRange.new(p0, p1)", ODTW)

    def test_uderzenia_maja_szczyt_w_odcinku(self):
        for z, w in UST["zdarzenia"].items():
            e = MAPA["efekty"][w["efekt"]]
            self.assertLessEqual(e["atak"], e["szczyt"], z)
            self.assertLess(e["szczyt"], e["koniec"] - e["poczatek"], z)


class TestIdentyfikatorow(unittest.TestCase):
    def _plik(self, dane):
        f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
        json.dump(dane, f)
        f.close()
        self.addCleanup(os.unlink, f.name)
        return f.name

    def test_postac_prosta(self):
        ident = json.loads(json.dumps(IDENT))
        zm = ZB.wpisz_identyfikatory(self._plik({"arkusz": 123, "muzyka": {"muzyka_05_las_a_petla": "456"}}), ident)
        self.assertEqual(ident["arkusz"], 123)
        self.assertEqual(ident["muzyka"]["muzyka_05_las_a_petla"], 456)
        self.assertEqual(len(zm), 2)
        k = ZB.katalog(UST, ident)
        tekst, _ = ZB.zrodlo_katalogu(k)
        self.assertIn("id = 123,", tekst)

    def test_postac_rejestru_wgranych(self):
        ident = json.loads(json.dumps(IDENT))
        ZB.wpisz_identyfikatory(self._plik({"wgrane": [
            {"plik": "assets/audio/arkusz/sfx_arkusz_a.ogg", "assetId": "777"},
            {"plik": "assets/audio/muzyka/muzyka_02_bazar_targ_petla.ogg", "assetId": "888"},
            {"plik": "assets/audio/dzwieki/sfx_unik.wav", "assetId": "999"}]}), ident)
        self.assertEqual(ident["arkusz"], 777)
        self.assertEqual(ident["muzyka"]["muzyka_02_bazar_targ_petla"], 888)

    def test_odmowa_zlych(self):
        for zle in ({"arkusz": 0}, {"arkusz": -5}, {"muzyka": {"nie_ma_takiego": 5}}, {"arkusz": "abc"}, {}):
            with self.assertRaises(SystemExit, msg=str(zle)):
                ZB.wpisz_identyfikatory(self._plik(zle), json.loads(json.dumps(IDENT)))


class TestZrodel(unittest.TestCase):
    def test_straznik_i_luau(self):
        tekst, _ = ZB.zrodlo_katalogu(ZB.katalog(UST, IDENT))
        zrodla = ZB.zrodla_pakietu(tekst)
        self.assertEqual([z[0] for z in zrodla], ["Moduly/KatalogDzwiekow", "MuzykaStref"])
        self.assertEqual(ZB.SL.sprawdz_pliki([ZB.KATALOG, ZB.MUZYKA]), [])

    def test_muzyka_tylko_czyta_cudze(self):
        m = czytaj("swiat", "dzwiek_gra", "zrodla", "MuzykaStref.client.luau")
        self.assertNotIn("Lighting", m)
        for cudzy in ("MiasteczkoBazar", "LasPas", "TestWalki2"):
            # cudze kontenery tylko przez FindFirstChild / WaitForChild (bez zmian)
            self.assertNotRegex(m, r'%s"\)\s*[:.]\s*(Destroy|SetAttribute|ClearAllChildren)' % cudzy)
        self.assertIn('folder.Parent = kontener', m)  # dźwięki muzyki tylko we własnym kontenerze (u klienta)
        self.assertNotIn("menu", re.sub(r"--.*", "", m).lower().replace("menu główne", ""))


if __name__ == "__main__":
    unittest.main(verbosity=1)
