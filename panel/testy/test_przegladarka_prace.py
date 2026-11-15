# -*- coding: utf-8 -*-
"""Prace w toku w prawdziwej przeglądarce (Edge/Chrome bez okna) — kroki w testy/przegladarka_prace.mjs.

Test jest NA ŻĄDANIE (potrzebuje przeglądarki i Node 22+, ok. 30 s):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_prace

Serwer testowy jak w test_api.py (katalogi tymczasowe, kopia sejfu). Przed startem w danych lokalnych serwera leżą
trzy prace (w toku, po czasie, gotowa z raportem), a w danych wspólnych trzy raporty. Sprawdza: karta „Prace w toku”
na górze Pulpitu (napisy końca, etap, pasek, zwinięte „Zakończone dziś”, link do raportu), plakietkę w górnym pasku,
znaczek przy raporcie w zakładce Pytania (lista i historia) i w zakładce Sesja, brak karty przy pustej liście i stary
serwer bez prac (podstawiony /api/zdrowie): brak karty, znaczków i żądań /api/prace, bez błędów w konsoli; po „restarcie”
(inny pid w /api/ping, moduł prac w /api/zdrowie) karta i plakietka pojawiają się bez przeładowania strony.
"""
import datetime
import json
import os
import shutil
import subprocess
import unittest

from testy import test_api, test_prace, test_przegladarka  # bez importu klas: discover uruchomiłby je drugi raz
from bc import prace, rdzen

PANEL = test_api.PANEL
R_CZEKA = "r-20261115-090000-aaaa"          # raport czeka na decyzję — praca „walka-v2” w toku
R_POPRAWA = "r-20261115-080000-bbbb"        # raport odesłany do poprawy — praca „biom-las” gotowa
R_WYNIK = "r-20261115-100000-cccc"          # raport z wynikiem poprawki


def _raport(dane, rid, tytul, czas):
    rdzen.zapisz_json(os.path.join(dane, "raporty", rid + ".json"),
                      {"id": rid, "tytul": tytul, "opis_md": "Opis raportu testowego.", "kto": "Claude (test)", "czas": czas,
                       "rodzaj": "wdrozenie", "komponenty": [], "zrzuty": []})


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestPraceWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i kopię sejfu z TestZapisSejfuAPI, ale nie jego testy."""

    @classmethod
    def przygotuj(cls, runtime):
        super().przygotuj(runtime)
        dane = os.path.join(cls.tmp, "dane")
        teraz = datetime.datetime.now().astimezone()
        iso = lambda d: d.isoformat(timespec="seconds")                     # noqa: E731
        _raport(dane, R_POPRAWA, "Mapa lasu", iso(teraz - datetime.timedelta(hours=3)))
        rdzen.zapisz_json(os.path.join(dane, "raporty", R_POPRAWA + ".decyzja.json"),
                          {"kto": "Karol", "czas": iso(teraz - datetime.timedelta(hours=2)), "wartosc": "do_poprawy",
                           "komentarz": "Więcej drzew"})
        _raport(dane, R_CZEKA, "Walka v2: poprawki ataku", iso(teraz - datetime.timedelta(hours=1)))
        _raport(dane, R_WYNIK, "Mapa lasu — poprawki", iso(teraz - datetime.timedelta(minutes=20)))
        with test_prace.dane_lokalne_testu(runtime):                     # log do pamięci, nie do logu panelu
            prace.rozpocznij("walka-v2", "Walka v2 — poprawki", etapy="Plan,Poprawki,Kontrola", numer=2, koniec="+35m",
                             dotyczy="raport:" + R_CZEKA, kto="Claude (test)")
            prace.rozpocznij("modele", "Gołe modele i ekwipunek", koniec=iso(teraz - datetime.timedelta(minutes=10)),
                             kto="Claude (test)", teraz=teraz - datetime.timedelta(hours=1))
            prace.rozpocznij("biom-las", "Biom Las — poprawki mapy", dotyczy="raport:" + R_POPRAWA, kto="Claude (test)",
                             teraz=teraz - datetime.timedelta(hours=1))
            prace.zakoncz("biom-las", raport=R_WYNIK, teraz=teraz - datetime.timedelta(minutes=15))

    def test_prace_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_prace.mjs"), str(self.port), runtime,
                     test_przegladarka._przegladarka(), json.dumps({"czeka": R_CZEKA, "poprawa": R_POPRAWA, "wynik": R_WYNIK})]
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
    setattr(TestPraceWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
