# -*- coding: utf-8 -*-
"""Zakładka Pytania w prawdziwej przeglądarce (Edge albo Chrome bez okna) — lista „Do odpowiedzi”, zapis do sejfu,
Tak / Nie przy decyzjach, samo-rozstrzyganie pytań, „Na sesję główną”, historia, wyszukiwarka, „Pokaż więcej”,
stare adresy, lista aktywnych osób, ciche odświeżanie.

Test jest NA ŻĄDANIE (trwa ok. dwóch minut i potrzebuje przeglądarki oraz Node 22+):
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

# Pytania do próby: 1 rozstrzyga decyzja D-002 (samo-rozstrzyganie), 2 — odpowiedź tekstem, 3 — szkic przy cichym
# odświeżeniu i „Na sesję główną”, 4 — krótka karta (punkty widoczne, „Szczegóły:” i dopisek zwinięte).
# D-003 i D-005 nie są przypięte do pytań, więc są osobnymi kartami „Czy zatwierdzamy: …?” na liście.
PYTANIA = """---
status: do-decyzji
---
# Pytania otwarte

## 1. Pytanie z decyzją
Treść pierwszego.
Rozstrzyga: D-002
**Odpowiedź:**

## 2. Zwykłe pytanie
Treść drugiego.
**Odpowiedź:**

## 3. Pytanie na sesję
Treść trzeciego.
**Odpowiedź:**

## 4. Pytanie z punktami
- Pierwszy punkt pytania.
- Drugi punkt pytania.
Szczegóły: Długi opis, którego nie widać od razu. Ciąg dalszy opisu.
Dopisek (sesja główna): dopisek zwinięty.
**Odpowiedź:**
"""


def _przegladarka():
    return next((p for p in PRZEGLADARKI if p and os.path.isfile(p)), None)


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and _przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestPytaniaWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i tymczasowy sejf z TestZapisSejfuAPI, ale nie jego testy."""

    @classmethod
    def przygotuj(cls, runtime):
        super().przygotuj(runtime)
        with open(os.path.join(cls.sejf, "Produkcja", "Pytania otwarte.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(PYTANIA)

    def test_pytania_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        produkcja = os.path.join(self.sejf, "Produkcja")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka.mjs"), str(self.port), runtime, produkcja,
                     _przegladarka()]
        if os.environ.get("BC_TEST_ZRZUTY"):
            polecenie.append(os.environ["BC_TEST_ZRZUTY"])
        r = subprocess.run(polecenie, capture_output=True, timeout=300, cwd=PANEL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
        if os.environ.get("BC_TEST_WYPISZ") == "1":
            print(wyjscie)
        self.assertEqual(r.returncode, 0, wyjscie)
        self.assertNotIn("BŁĄD", wyjscie, wyjscie)


# testy odziedziczone z TestZapisSejfuAPI już biegną w test_api.py — tu tylko przeglądarka
for _nazwa in [n for n in dir(test_api.TestZapisSejfuAPI) if n.startswith("test_")]:
    setattr(TestPytaniaWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
