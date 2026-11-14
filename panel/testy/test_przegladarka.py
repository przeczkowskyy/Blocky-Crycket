# -*- coding: utf-8 -*-
"""Interfejs Planu w prawdziwej przeglądarce (Edge albo Chrome bez okna) — scenariusze z przeglądu zapisu do sejfu.

Test jest NA ŻĄDANIE (trwa ok. minuty i potrzebuje przeglądarki oraz Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka
Bez zmiennej BC_TEST_PRZEGLADARKA=1 jest pomijany, więc zwykłe `unittest discover` go nie uruchamia.

Serwer testowy jak w test_api.py: katalogi tymczasowe, tymczasowy sejf z konfiguracji lokalnej, tymczasowe klucze
(lokalny i zatwierdzania). Właściwe kroki są w testy/przegladarka.mjs. Zrzuty ekranu: BC_TEST_ZRZUTY=<katalog>.
"""
import os
import shutil
import subprocess
import unittest

from testy import test_api  # bez importu klas do tej przestrzeni: discover uruchomiłby je drugi raz

PANEL = test_api.PANEL

PRZEGLADARKI = [os.environ.get("BC_PRZEGLADARKA") or "",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                shutil.which("msedge") or "", shutil.which("google-chrome") or "", shutil.which("chromium") or ""]


def _przegladarka():
    return next((p for p in PRZEGLADARKI if p and os.path.isfile(p)), None)


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and _przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestPlanWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i tymczasowy sejf z TestZapisSejfuAPI, ale nie jego testy."""

    def test_plan_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        produkcja = os.path.join(self.sejf, "Produkcja")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka.mjs"), str(self.port), runtime, produkcja,
                     _przegladarka()]
        if os.environ.get("BC_TEST_ZRZUTY"):
            polecenie.append(os.environ["BC_TEST_ZRZUTY"])
        r = subprocess.run(polecenie, capture_output=True, timeout=240, cwd=PANEL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
        self.assertEqual(r.returncode, 0, wyjscie)
        self.assertNotIn("BŁĄD", wyjscie, wyjscie)


# testy odziedziczone z TestZapisSejfuAPI już biegną w test_api.py — tu tylko przeglądarka
for _nazwa in [n for n in dir(test_api.TestZapisSejfuAPI) if n.startswith("test_")]:
    setattr(TestPlanWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
