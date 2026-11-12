# -*- coding: utf-8 -*-
"""Testy lustra tylko-do-odczytu: zgodność klucza plików z przeglądarką i dymny eksport na danych tymczasowych.

Uruchomienie: cd panel && python -m unittest testy.test_statyczny
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PANEL)

from bc import statyczny  # noqa: E402


class Klucz(unittest.TestCase):
    def test_zgodnosc_z_przegladarka(self):
        # wartość odczytana z żądania prawdziwej przeglądarki (wspolne/api.js) dla tej samej ścieżki
        self.assertEqual(statyczny.klucz("/api/podglad/20261112-222856-ca2c/czesci"), "013f4f0824ed9352")

    def test_polskie_znaki_i_zapytanie(self):
        a = statyczny.klucz("/api/sejf/notatka?sciezka=" + statyczny.enc("B&C/Gra/Pętla gry.md"))
        self.assertEqual(len(a), 16)
        self.assertNotEqual(a, statyczny.klucz("/api/sejf/notatka?sciezka=" + statyczny.enc("B&C/Gra/Petla gry.md")))

    def test_enc_jak_encodeuricomponent(self):
        self.assertEqual(statyczny.enc("B&C/Gra/Karczma (Questy).md"), "B%26C%2FGra%2FKarczma%20(Questy).md")
        self.assertEqual(statyczny.enc("Źródła"), "%C5%B9r%C3%B3d%C5%82a")


class Eksport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_lustro_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_eksport_dymny(self):
        dane = os.path.join(self.tmp, "dane")
        os.makedirs(os.path.join(dane, "raporty"))
        with open(os.path.join(dane, "raporty", "r-20260101-000000-abcd.json"), "w", encoding="utf-8") as f:
            json.dump({"id": "r-20260101-000000-abcd", "tytul": "Test lustra", "opis_md": "opis", "kto": "test",
                       "czas": "2026-01-01T00:00:00+01:00", "rodzaj": "informacja", "komponenty": [], "zrzuty": []}, f)
        wyj = os.path.join(self.tmp, "lustro")
        env = dict(os.environ, BC_PANEL_DANE=dane, BC_PANEL_RUNTIME=os.path.join(self.tmp, "runtime"), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONIOENCODING="utf-8")
        r = subprocess.run([sys.executable, os.path.join(PANEL, "serwer.py"), "--eksport", wyj], capture_output=True, env=env,
                           timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr).decode("utf-8", "replace")[-800:])
        for nazwa in ("index.html", "app.js", "tryb.js", ".nojekyll"):
            self.assertTrue(os.path.isfile(os.path.join(wyj, nazwa)), nazwa)
        with open(os.path.join(wyj, "tryb.js"), encoding="utf-8") as f:
            self.assertIn("window.BC_STATYCZNY = true", f.read())
        for sciezka in ("/api/ja", "/api/sejf/plan", "/api/sejf/siec", "/api/raporty", "/api/podglad", "/api/agent/stan"):
            plik = os.path.join(wyj, "dane", statyczny.klucz(sciezka) + ".json")
            self.assertTrue(os.path.isfile(plik), sciezka)
        with open(os.path.join(wyj, "dane", statyczny.klucz("/api/ja") + ".json"), encoding="utf-8") as f:
            ja = json.load(f)
        self.assertTrue(ja["tryb_statyczny"])
        self.assertFalse(ja["lokalny"])
        with open(os.path.join(wyj, "dane", statyczny.klucz("/api/raporty") + ".json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["raporty"][0]["tytul"], "Test lustra")
        # w lustrze nie ma danych lokalnych ani sejfów spoza repozytorium
        with open(os.path.join(wyj, "dane", statyczny.klucz("/api/sejf/siec") + ".json"), encoding="utf-8") as f:
            siec = json.load(f)
        self.assertTrue(all(not str(w.get("sciezka", "")).startswith("sejf:") for w in siec["wezly"]))
        self.assertFalse(os.path.exists(os.path.join(wyj, "_dev3d.html")))


if __name__ == "__main__":
    unittest.main()
