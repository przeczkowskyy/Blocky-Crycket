# -*- coding: utf-8 -*-
"""Zakładka Wytwórnia w prawdziwej przeglądarce (Edge/Chrome bez okna) — kroki w testy/przegladarka_wytwornia.mjs.

Test jest NA ŻĄDANIE (potrzebuje przeglądarki i Node 22+, ok. 30 s):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_wytwornia

Serwer testowy jak w test_wytwornia.TestWytworniaAPI: katalogi tymczasowe i tymczasowy sejf z notatkami Wytwórni
(BONK, Ring Potworów, Stary pomysł, Radar trendów, Karta oceny pomysłu, szablon). Zrzuty: BC_TEST_ZRZUTY=<katalog>.
"""
import os
import shutil
import subprocess
import unittest

from testy import test_api, test_przegladarka, test_wytwornia  # bez importu klas: discover uruchomiłby je drugi raz

PANEL = test_api.PANEL


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestWytworniaWPrzegladarce(test_wytwornia.TestWytworniaAPI):
    """Dziedziczy rozruch serwera i tymczasowy sejf z TestWytworniaAPI, ale nie jego testy."""

    def test_wytwornia_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_wytwornia.mjs"), str(self.port), runtime, self.sejf,
                     test_przegladarka._przegladarka()]
        if os.environ.get("BC_TEST_ZRZUTY"):
            polecenie.append(os.environ["BC_TEST_ZRZUTY"])
        r = subprocess.run(polecenie, capture_output=True, timeout=300, cwd=PANEL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
        if os.environ.get("BC_TEST_WYPISZ") == "1":
            print(wyjscie)
        self.assertEqual(r.returncode, 0, wyjscie)
        self.assertNotIn("BŁĄD", wyjscie, wyjscie)


def load_tests(loader, standard, wzorzec):
    """Tylko próba w przeglądarce — bez odziedziczonych testów API (te są w test_wytwornia)."""
    return unittest.TestSuite([TestWytworniaWPrzegladarce("test_wytwornia_w_przegladarce")])
