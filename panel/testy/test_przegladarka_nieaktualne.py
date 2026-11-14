# -*- coding: utf-8 -*-
"""„Nieaktualne” w zakładce Pytania w prawdziwej przeglądarce (Edge albo Chrome bez okna): przycisk na pytaniu, na
decyzji i na raporcie zdejmuje kartę i daje etykietę w historii, pytanie z decyzją z wiersza „Rozstrzyga:” zdejmuje też
tę decyzję, karta potwierdzenia nie ma przycisku ani pola wyboru, tryb „Zaznacz kilka” oznacza trzy sprawy naraz (a przy
konflikcie wersji zostawia sprawę zaznaczoną z powodem), wyszukiwarka znajduje po słowie „nieaktualne”, „Przywróć”
wraca decyzję na listę, a przy serwerze bez tej funkcji przycisk mówi, że zadziała po restarcie panelu.

Test jest NA ŻĄDANIE (ok. minuty, potrzebuje przeglądarki oraz Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_nieaktualne
Serwer testowy jak w test_api.py (katalogi tymczasowe, kopia sejfu, tymczasowe klucze). Kroki: testy/przegladarka_nieaktualne.mjs.
"""
import datetime
import os
import shutil
import subprocess
import unittest

from testy import test_api, test_przegladarka  # bez importu klas: discover uruchomiłby je drugi raz

PANEL = test_api.PANEL

PYTANIA = """---
status: do-decyzji
---
# Pytania otwarte

## 1. Pytanie z decyzją
Treść pierwszego.
Rozstrzyga: D-002
**Odpowiedź:**

## 2. Pytanie do zdjęcia z powodem
Treść drugiego.
**Odpowiedź:**

## 3. Pytanie do zaznaczenia
Treść trzeciego.
**Odpowiedź:**

## 4. Pytanie zostaje
Treść czwartego.
**Odpowiedź:**
"""


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestNieaktualneWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i kopię sejfu z TestZapisSejfuAPI, ale nie jego testy."""

    @classmethod
    def przygotuj(cls, runtime):
        super().przygotuj(runtime)
        produkcja = os.path.join(cls.sejf, "Produkcja")
        with open(os.path.join(produkcja, "Pytania otwarte.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(PYTANIA)
        # decyzja Karola z dziś czeka na potwierdzenie Pawła — karta potwierdzenia (bez „Nieaktualne”)
        sciezka = os.path.join(produkcja, "Rejestr decyzji.md")
        with open(sciezka, encoding="utf-8", newline="") as f:
            rejestr = f.read()
        rejestr = rejestr.replace("---\n*Stopka rejestru.*", "### D-009 Decyzja Karola\n✅ zatwierdzona · test · zdecydował: "
                                  "Karol Balucki %s\nOpis decyzji Karola.\n\n---\n*Stopka rejestru.*" % datetime.date.today())
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            f.write(rejestr)

    def test_nieaktualne_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        produkcja = os.path.join(self.sejf, "Produkcja")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_nieaktualne.mjs"), str(self.port), runtime,
                     produkcja, test_przegladarka._przegladarka()]
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
    setattr(TestNieaktualneWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
