# -*- coding: utf-8 -*-
"""Pulpit per gra w prawdziwej przeglądarce (Edge albo Chrome bez okna): przełącznik gier w nagłówku (telefon i komputer),
okno „Która gra?” z liczbami i wstrzymanymi grami, filtr listy „Do odpowiedzi”, Zadań, Pulpitu i Podglądu, „Wszystkie gry”
z etykietami, wybór zapamiętany w przeglądarce i ustawiany adresem ?gra=, zadanie dodane w grze ze znacznikiem.

Test jest NA ŻĄDANIE (ok. pół minuty, potrzebuje przeglądarki oraz Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_gry
Serwer testowy jak w test_gry.py (kopia sejfu i raporty z testy/test_gry.py, rejestr gier w konfiguracji lokalnej).
Kroki: testy/przegladarka_gry.mjs; zrzuty ekranu: BC_TEST_ZRZUTY=<katalog>; pełny wynik: BC_TEST_WYPISZ=1.
"""
import os
import shutil
import subprocess
import unittest

from testy import test_gry, test_przegladarka  # bez importu klas: discover uruchomiłby je drugi raz

PANEL = test_gry.PANEL


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestGryWPrzegladarce(test_gry._SerwerGier):
    def test_gry_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_gry.mjs"), str(self.port), runtime,
                     os.path.join(self.sejf, "Produkcja"), test_przegladarka._przegladarka()]
        if os.environ.get("BC_TEST_ZRZUTY"):
            polecenie.append(os.environ["BC_TEST_ZRZUTY"])
        r = subprocess.run(polecenie, capture_output=True, timeout=300, cwd=PANEL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
        if os.environ.get("BC_TEST_WYPISZ") == "1":
            print(wyjscie)
        self.assertEqual(r.returncode, 0, wyjscie)
        self.assertNotIn("BŁĄD", wyjscie, wyjscie)


if __name__ == "__main__":
    unittest.main()
