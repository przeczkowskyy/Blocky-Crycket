# -*- coding: utf-8 -*-
"""Zakładka Sesja w prawdziwej przeglądarce: dwie osobne sesje przeglądarki z atrapami mikrofonu łączą się przez
WebRTC, a odcinek nagrania przechodzi przez serwer i robotnika (atrapa transkrypcji) aż do widoku.

Test jest NA ŻĄDANIE (trwa 1–2 minuty, potrzebuje Edge albo Chrome i Node 22+):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_sesja
Bez zmiennej BC_TEST_PRZEGLADARKA=1 jest pomijany. Zrzuty ekranu: BC_TEST_ZRZUTY=<katalog>.

Serwer testowy jak w test_sesje.TestSesjeAPI: katalogi tymczasowe, tymczasowy sejf, BC_GLOS_ATRAPA=1 (robotnik nie
ładuje modelu Whisper), bez serwerów STUN (połączenie na pętli zwrotnej), odcinki po 4 s. Kroki: testy/przegladarka_sesja.mjs.
"""
import os
import shutil
import subprocess
import unittest

from testy import test_sesje  # bez importu klas do tej przestrzeni: discover uruchomiłby je drugi raz
from testy.test_przegladarka import _przegladarka

PANEL = test_sesje.PANEL


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and _przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestSesjaWPrzegladarce(test_sesje.TestSesjeAPI):
    """Dziedziczy rozruch serwera z TestSesjeAPI, ale nie jego testy."""

    def test_sesja_w_dwoch_przegladarkach(self):
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_sesja.mjs"), str(self.port), runtime,
                     _przegladarka()]
        if os.environ.get("BC_TEST_ZRZUTY"):
            polecenie.append(os.environ["BC_TEST_ZRZUTY"])
        r = subprocess.run(polecenie, capture_output=True, timeout=300, cwd=PANEL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
        print(wyjscie)
        self.assertEqual(r.returncode, 0, wyjscie)
        self.assertNotIn("BŁĄD", wyjscie, wyjscie)
        # po transkrypcji nie zostaje żaden plik dźwięku
        sesje = os.path.join(runtime, "sesje")
        for sid in os.listdir(sesje) if os.path.isdir(sesje) else []:
            kat = os.path.join(sesje, sid, "odcinki")
            for katalog, _, pliki in os.walk(kat):
                self.assertFalse([p for p in pliki if p.startswith("nagranie.")], katalog)


for _nazwa in [n for n in dir(test_sesje.TestSesjeAPI) if n.startswith("test_")]:
    setattr(TestSesjaWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
