# -*- coding: utf-8 -*-
"""Zakładka Assety „na żywo” (Edge/Chrome bez okna) — kroki w testy/przegladarka_assety.mjs.

Test jest NA ŻĄDANIE (potrzebuje przeglądarki i Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_assety

Serwer testowy jak w test_api.py (katalogi tymczasowe, kopia sejfu). Serwer działa w katalogu prawdziwego
repozytorium, więc rejestr grafik, strumień zdarzeń i stan gita podstawia sama strona (fetch podmieniony przed
startem aplikacji) — prawdziwy assets/manifest.json nie jest tu ani czytany przez widok, ani zmieniany. Sprawdza:
pierwsze otwarcie bez znaczków „nowe”, „Zaktualizowano HH:MM.”, odświeżenie po zdarzeniu (przewinięcie, fokus,
szukanie zostają), znaczki „nowe”, pasek „Na GitHubie są nowsze zmiany”, obejrzenie, ponowne połączenie.
"""
import os
import shutil
import subprocess
import unittest

from testy import test_api, test_przegladarka  # bez importu klas: discover uruchomiłby je drugi raz

PANEL = test_api.PANEL


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestAssetyWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i kopię sejfu z TestZapisSejfuAPI, ale nie jego testy."""

    def test_assety_na_zywo_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_assety.mjs"), str(self.port), runtime,
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
    """Tylko próba w przeglądarce — bez odziedziczonych testów zapisu sejfu (te są w test_api)."""
    return unittest.TestSuite([TestAssetyWPrzegladarce("test_assety_na_zywo_w_przegladarce")])
