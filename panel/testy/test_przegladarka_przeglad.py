# -*- coding: utf-8 -*-
"""Zakładka Podgląd („Do przejrzenia”: podgląd prac w toku, raporty do akceptacji hurtem i po kolei), obraz przy pracy
na Pulpicie, lekkie karty w zakładce Pytania i podpowiedź „Na sesji padło” w zakładce Sesja — w prawdziwej przeglądarce
(Edge/Chrome bez okna). Kroki w testy/przegladarka_przeglad.mjs.

Test jest NA ŻĄDANIE (potrzebuje przeglądarki i Node 22+, ok. 30 s):
    cd panel && set BC_TEST_PRZEGLADARKA=1 && python -B -m unittest testy.test_przegladarka_przeglad
Zrzuty ekranu (telefon 390 px i komputer 1280 px): BC_TEST_ZRZUTY=<katalog>; pełny wynik: BC_TEST_WYPISZ=1.

Serwer testowy jak w test_api.py (katalogi tymczasowe, kopia sejfu z test_zapis.PLIKI i jedno pytanie z punktami,
„Szczegóły:” i wierszem „Rozstrzyga: D-005”). W danych wspólnych serwera: cztery raporty czekające (dwa ze zrzutami,
jeden z migawką 3D, jeden bez obrazu), raport zaakceptowany i informacja; w danych lokalnych trzy prace w toku (ze
zrzutem, z migawką, bez podglądu). Notatki sesji podstawia strona (odpowiedź /api/sesje/transkrypcja) — bez agenta
i bez rozmowy głosowej.
"""
import datetime
import json
import os
import shutil
import struct
import subprocess
import unittest
import zlib

from testy import test_api, test_prace, test_przegladarka  # bez importu klas: discover uruchomiłby je drugi raz
from bc import prace, rdzen

PANEL = test_api.PANEL
R = {"troll": "r-20261117-090000-aaa1", "polana": "r-20261117-091000-aaa2", "ekran": "r-20261117-092000-aaa3",
     "tempo": "r-20261117-093000-aaa4", "stary": "r-20261117-080000-aaa5", "info": "r-20261117-081000-aaa6"}


def obraz_png(szer, wys, gora, dol, ziemia=None, klocek=None):
    """Prosty obraz PNG (niebo z przejściem, ziemia, klocek na środku) — do miniatur i zrzutów ekranu w teście."""
    wiersze = bytearray()
    for y in range(wys):
        t = y / max(1, wys - 1)
        tlo = ziemia if ziemia and y > wys * 0.68 else tuple(int(gora[i] + (dol[i] - gora[i]) * t) for i in range(3))
        w = bytearray(b"\x00")
        for x in range(szer):
            if klocek and abs(x - szer / 2) < szer * 0.13 and wys * 0.32 < y < wys * 0.72:
                w += bytes(klocek)
            else:
                w += bytes(tlo)
        wiersze += w

    def kawalek(typ, dane):
        return struct.pack(">I", len(dane)) + typ + dane + struct.pack(">I", zlib.crc32(typ + dane) & 0xffffffff)
    return (b"\x89PNG\r\n\x1a\n" + kawalek(b"IHDR", struct.pack(">IIBBBBB", szer, wys, 8, 2, 0, 0, 0)) +
            kawalek(b"IDAT", zlib.compress(bytes(wiersze))) + kawalek(b"IEND", b""))


def _zapisz(sciezka, bajty):
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    with open(sciezka, "wb") as f:
        f.write(bajty)
    return sciezka


PYTANIE_Z_PUNKTAMI = """

## 6. Czy las ma mieć mgłę od rana?
- Mgła lekka, tylko w lesie (oświetlenie jest wspólne).
- Albo bez mgły, za to ciemniejsze drzewa.
Szczegóły: dłuższy opis, który ma zostać zwinięty za „Pokaż szczegóły”. Mgła zmienia też widoczność potworów z daleka
i trzeba ją sprawdzić na telefonie, bo tam ekran jest ciemniejszy.
Rozstrzyga: D-005
**Odpowiedź:**
"""


@unittest.skipUnless(os.environ.get("BC_TEST_PRZEGLADARKA") == "1", "test w przeglądarce na żądanie (BC_TEST_PRZEGLADARKA=1)")
@unittest.skipUnless(shutil.which("node") and test_przegladarka._przegladarka(), "brak Node albo przeglądarki Edge/Chrome")
class TestPrzegladWPrzegladarce(test_api.TestZapisSejfuAPI):
    """Dziedziczy rozruch serwera i kopię sejfu z TestZapisSejfuAPI, ale nie jego testy."""

    @classmethod
    def przygotuj(cls, runtime):
        super().przygotuj(runtime)
        with open(os.path.join(cls.sejf, "Produkcja", "Pytania otwarte.md"), "a", encoding="utf-8", newline="\n") as f:
            f.write(PYTANIE_Z_PUNKTAMI)
        dane = os.path.join(cls.tmp, "dane")
        teraz = datetime.datetime.now().astimezone()
        iso = lambda minut: (teraz - datetime.timedelta(minutes=minut)).isoformat(timespec="seconds")  # noqa: E731

        def raport(klucz, tytul, minut, zrzuty=(), **inne):
            rid = R[klucz]
            nazwy = []
            for i, b in enumerate(zrzuty, 1):
                _zapisz(os.path.join(dane, "raporty", rid, "zrzut_%d.png" % i), b)
                nazwy.append("zrzut_%d.png" % i)
            r = {"id": rid, "tytul": tytul, "opis_md": inne.pop("opis", "Opis raportu testowego. Drugie zdanie opisu."),
                 "kto": "Claude (test)", "czas": iso(minut), "rodzaj": inne.pop("rodzaj", "wdrozenie"), "komponenty": [],
                 "zrzuty": nazwy}
            r.update(inne)
            rdzen.zapisz_json(os.path.join(dane, "raporty", rid + ".json"), r)

        raport("troll", "Model: Leśny Troll", 50, [obraz_png(320, 180, (70, 120, 200), (170, 210, 240), (60, 110, 50), (90, 140, 70)),
                                                    obraz_png(320, 180, (40, 40, 60), (90, 90, 120), (50, 50, 50), (200, 120, 60))],
               opis="Model z ośmioma klipami walki. Pokazuję pozę spoczynkową i trafienie.\n\nDalszy opis szczegółów modelu.")
        raport("polana", "Mapa: polana przy bramie", 40, [obraz_png(320, 180, (90, 150, 220), (200, 225, 245), (80, 140, 60), (120, 90, 60))])
        raport("ekran", "Ekran walki — wersja 2", 30, migawka=test_api.MID,
               opis="Nowy układ pasków życia i przycisków. Ocena na telefonie.")
        raport("tempo", "Tempo biegu przez las", 20, rodzaj="pytanie", pytanie="Czy 57 s na bieg od wejścia do bramy to dobre tempo?",
               opis="Bieg od wejścia do bramy trwa 57 s. Bez obrazów — ocena po liczbach.")
        raport("stary", "Stare drzewa", 300, [obraz_png(64, 36, (10, 10, 10), (40, 40, 40))])
        rdzen.zapisz_json(os.path.join(dane, "raporty", R["stary"] + ".decyzja.json"),
                          {"kto": "Karol", "czas": iso(200), "wartosc": "zaakceptowane", "komentarz": ""})
        raport("info", "Informacja o synchronizacji", 10, rodzaj="informacja")
        wej = os.path.join(cls.tmp, "wejscie")
        with test_prace.dane_lokalne_testu(runtime):                     # log do pamięci, nie do logu panelu
            prace.rozpocznij("las-pas", "Las-pas — poprawki faktur", etapy="Plan,Budowa,Kontrola", numer=2, koniec="+40m",
                             kto="Claude (test)", zrzut=_zapisz(os.path.join(wej, "las.png"),
                                                                obraz_png(480, 270, (60, 110, 190), (180, 215, 240), (50, 100, 45), (110, 80, 50))),
                             podpis_zrzutu="Polana od wschodu")
            prace.rozpocznij("render-modeli", "Render modeli lasu", koniec="+20m", kto="Claude (test)")
            prace.rozpocznij("biom-bagno", "Bagno — plan mapy", koniec="+90m", kto="Claude (test)")
            p = prace.czytaj("render-modeli")                             # migawka powstaje dopiero po przygotowaniu
            p["migawka"] = test_api.MID
            rdzen.zapisz_json(os.path.join(runtime, "prace", "render-modeli.json"), p)

    def test_przeglad_w_przegladarce(self):
        # zrzut migawki 3D z test_api to sam nagłówek JPG — podmiana na prawdziwy obraz (serwer czyta plik z dysku)
        _zapisz(os.path.join(self.tmp, "dane", "podglad", test_api.MID, "zrzut_1.jpg"),
                obraz_png(320, 180, (30, 30, 50), (80, 80, 110), (40, 40, 40), (230, 180, 60)))
        runtime = os.path.join(self.tmp, "runtime")
        polecenie = ["node", os.path.join(PANEL, "testy", "przegladarka_przeglad.mjs"), str(self.port), runtime,
                     test_przegladarka._przegladarka(), json.dumps(R)]
        if os.environ.get("BC_TEST_ZRZUTY"):
            polecenie.append(os.environ["BC_TEST_ZRZUTY"])
        r = subprocess.run(polecenie, capture_output=True, timeout=400, cwd=PANEL,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        wyjscie = (r.stdout + r.stderr).decode("utf-8", "replace")
        if os.environ.get("BC_TEST_WYPISZ") == "1":
            print(wyjscie)
        self.assertEqual(r.returncode, 0, wyjscie)
        self.assertNotIn("BŁĄD", wyjscie, wyjscie)
        # decyzje z przeglądarki trafiły do plików decyzji raportów (ta sama droga co karty raportów)
        dec = lambda k: rdzen.czytaj_json(os.path.join(self.tmp, "dane", "raporty", R[k] + ".decyzja.json"))  # noqa: E731
        self.assertEqual((dec("troll") or {}).get("wartosc"), "zaakceptowane")
        self.assertEqual((dec("polana") or {}).get("wartosc"), "zaakceptowane")
        self.assertEqual(((dec("ekran") or {}).get("wartosc"), (dec("ekran") or {}).get("komentarz")), ("do_poprawy", "Ciemniejsze tło"))
        self.assertIsNone(dec("tempo"))                                   # pominięty — dalej czeka
        self.assertEqual((dec("stary") or {}).get("kto"), "Karol")        # cudzej decyzji nikt nie ruszył


for _nazwa in [n for n in dir(test_api.TestZapisSejfuAPI) if n.startswith("test_")]:
    setattr(TestPrzegladWPrzegladarce, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
