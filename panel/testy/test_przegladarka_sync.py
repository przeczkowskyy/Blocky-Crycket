# -*- coding: utf-8 -*-
"""Stan stałej synchronizacji z GitHubem na Pulpicie (Edge/Chrome bez okna) — kroki w testy/przegladarka_sync.mjs.

Test jest NA ŻĄDANIE (potrzebuje przeglądarki i Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_sync

Serwer testowy jak w test_api.py (katalogi tymczasowe, kopia sejfu). Odpowiedzi GET /api/git/stan i GET /api/git/auto
podmienia sama strona (podstawiony `fetch` przed startem aplikacji) — serwer testowy działa w katalogu prawdziwego
repozytorium, więc trasy gita nie są tu wołane wcale. Sprawdza: stary serwer bez pola `auto` (widok jak dotąd),
„Zsynchronizowano …”, „Czeka: …” ze szczegółami, „Konflikt — potrzebny człowiek”, informację po pobraniu (zwykły tekst).
"""
import os
import shutil
import subprocess
import unittest

from testy import test_api, test_przegladarka  # bez importu klas: discover uruchomiłby je drugi raz

PANEL = test_api.PANEL


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestSynchronizacjaWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i kopię sejfu z TestZapisSejfuAPI, ale nie jego testy."""

    def test_synchronizacja_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_sync.mjs"), str(self.port), runtime,
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


for _nazwa in [n for n in dir(test_api.TestZapisSejfuAPI) if n.startswith("test_")]:
    setattr(TestSynchronizacjaWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
