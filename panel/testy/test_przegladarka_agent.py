# -*- coding: utf-8 -*-
"""Zakładka Agent w prawdziwej przeglądarce (Edge albo Chrome bez okna) z ATRAPĄ agenta: pięć okien, nowa rozmowa
w oknie Balans, odpowiedź zwinięta i rozwijana, kroki narzędzi w jednym wierszu, usunięcie z potwierdzeniem (także
kilku naraz i rozmowy systemowej), widok telefonu (okna → rozmowy → rozmowa).

Test jest NA ŻĄDANIE (ok. minuty, potrzebuje Edge albo Chrome i Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_agent
Bez zmiennej BC_TEST_PRZEGLADARKA=1 jest pomijany. Zrzuty ekranu: BC_TEST_ZRZUTY=<katalog>; pełny wynik:
BC_TEST_WYPISZ=1.

Serwer testowy jak w test_api.py (katalogi tymczasowe); program agenta to atrapa (testy/atrapa_agenta.cjs), więc
prawdziwy Claude Code nie jest uruchamiany. W danych lokalnych czekają stara rozmowa (bez pola okna) i rozmowa
założona przez panel dla sesji (z polem `katalogi`). Kroki: testy/przegladarka_agent.mjs.
"""
import glob
import json
import os
import shutil
import subprocess
import unittest

from testy import test_api  # bez importu klas testów do tej przestrzeni
from testy.test_przegladarka import _przegladarka

PANEL = test_api.PANEL


def _watek(kat, wid, **pola):
    w = dict({"id": wid, "utworzono": "2026-11-12T09:00:00+01:00", "ostatnio": "2026-11-12T09:00:00+01:00",
              "session_id": None, "wiadomosci": [{"nr": 1, "rola": "user", "tekst": "Stare pytanie", "kto": "Karol",
                                                  "czas": "2026-11-12T09:00:00+01:00"}]}, **pola)
    with open(os.path.join(kat, wid + ".json"), "w", encoding="utf-8") as f:
        json.dump(w, f, ensure_ascii=False)


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and _przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestAgentWPrzegladarce(test_api.SerwerTestowy):

    @classmethod
    def srodowisko(cls):
        cls.log_atrapy = os.path.join(cls.tmp, "atrapa_log")
        return {"BC_ATRAPA_AGENTA_LOG": cls.log_atrapy}

    @classmethod
    def przygotuj(cls, runtime):
        kat = os.path.join(runtime, "agent", "watki")
        os.makedirs(kat)
        _watek(kat, "w-20261112-090000-aaaa", tytul="Rozmowa sprzed okien", utworzyl="Karol")
        _watek(kat, "w-20261113-200000-bbbb", tytul="Sesja główna — notatki", utworzyl="Karol", tytul_auto=False,
               katalogi=[])

    def test_agent_w_przegladarce(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_agent.mjs"), str(self.port), runtime,
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
        # atrapa dostała polecenie systemowe okna Balans z regułą krótkich odpowiedzi
        wywolania = []
        for p in sorted(glob.glob(os.path.join(self.log_atrapy, "*.json"))):
            with open(p, encoding="utf-8") as f:
                wywolania.append(json.load(f))
        balans = [w for w in wywolania if "Policz krzywą" in w["wejscie"]]
        self.assertEqual(len(balans), 1, wywolania)
        argv = balans[0]["argv"]
        sp = argv[argv.index("--append-system-prompt") + 1]
        self.assertIn("Okno agenta w panelu: Balans", sp)
        self.assertIn("Styl odpowiedzi (stała reguła panelu", sp)
        self.assertNotIn("Policz krzywą", sp)


if __name__ == "__main__":
    unittest.main()
