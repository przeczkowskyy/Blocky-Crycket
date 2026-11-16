# -*- coding: utf-8 -*-
"""Zadania przypisane do agenta osoby (16.11.2026): pole „· agent: Imię” w Zadaniach, przypisanie z panelu
(bc/zapis.py) i uruchamianie wyłącznie na komputerze przypisanej osoby (bc/zadania_agenta.py).

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_zadania_agenta

Pliki sejfu są tymczasowe (klasa Baza z test_zapis), agent i prace są podmienione — żaden test nie uruchamia Claude.
"""
import os
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import agent, prace, rdzen, sejf, sesje, zadania_agenta, zapis  # noqa: E402
from testy.test_zapis import DZIS, ZADANIA, Baza, _zadanie, zamien_linie, wstaw_po  # noqa: E402


def pozycje():
    return [p for s in sejf.plan()["zadania"]["sekcje"] for p in s["pozycje"]]


def id_po_tekscie(tekst):
    return next(p["id"] for p in pozycje() if p["tekst_md"] == tekst and not p["zrobione"])


class TestPrzypisanie(Baza):
    def test_przypisz_zmien_zdejmij(self):
        zid = id_po_tekscie("Pierwsze zadanie")
        w = zapis.przypisz_agenta(zid, "paweł", self.wersja("zadania"), "Karol")
        self.assertEqual(w["opis"], "zadanie dla agenta Paweł: Pierwsze zadanie")
        oczek = zamien_linie(ZADANIA, "- [ ] Pierwsze zadanie · #wysoki", "- [ ] Pierwsze zadanie · agent: Paweł · #wysoki")
        self.assertPlik("zadania", oczek)
        p = next(p for p in pozycje() if p["tekst_md"] == "Pierwsze zadanie")
        self.assertEqual((p["agent"], p["priorytet"]), ("Paweł", "wysoki"))
        self.assertIn("zadanie dla agenta Paweł", self.bajty("dziennik").decode("utf-8-sig"))

        zid = id_po_tekscie("Pierwsze zadanie")                # id zmienia się razem z tekstem pola
        zapis.przypisz_agenta(zid, "Karol", self.wersja("zadania"), "Karol")
        oczek = zamien_linie(oczek, "- [ ] Pierwsze zadanie · agent: Paweł · #wysoki",
                             "- [ ] Pierwsze zadanie · agent: Karol · #wysoki")
        self.assertPlik("zadania", oczek)

        zid = id_po_tekscie("Pierwsze zadanie")
        e = self.assertBlad(409, zapis.przypisz_agenta, zid, "Karol", self.wersja("zadania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "bez_zmian")
        w = zapis.przypisz_agenta(zid, "", self.wersja("zadania"), "Karol")
        self.assertIn("bez przypisanego agenta (było: Karol)", w["opis"])
        self.assertPlik("zadania", ZADANIA)

    def test_zadanie_bez_priorytetu_z_linkiem(self):
        zid = id_po_tekscie("Drugie [[Notatka]]")
        zapis.przypisz_agenta(zid, "Paweł", self.wersja("zadania"), "Karol")
        self.assertPlik("zadania", zamien_linie(ZADANIA, "- [ ] Drugie [[Notatka]] · #średni",
                                                "- [ ] Drugie [[Notatka]] · agent: Paweł · #średni"))
        zid = id_po_tekscie("Podzadanie drugiego")             # wcięte podzadanie, bez priorytetu
        zapis.przypisz_agenta(zid, "Karol", self.wersja("zadania"), "Karol")
        self.assertIn("  - [ ] Podzadanie drugiego · agent: Karol\n", self.bajty("zadania").decode("utf-8-sig")
                      .replace("\r\n", "\n"))

    def test_zle(self):
        przed = self.bajty("zadania")
        zid = id_po_tekscie("Pierwsze zadanie")
        self.assertBlad(400, zapis.przypisz_agenta, zid, "Zenek", self.wersja("zadania"), "Karol")
        self.assertBlad(400, zapis.przypisz_agenta, "../x", "Karol", self.wersja("zadania"), "Karol")
        self.assertBlad(404, zapis.przypisz_agenta, "z0123456789", "Karol", self.wersja("zadania"), "Karol")
        zrob = next(p["id"] for p in pozycje() if p["tekst_md"] == "Stare zadanie")
        self.assertBlad(409, zapis.przypisz_agenta, zrob, "Karol", self.wersja("zadania"), "Karol")
        rycerz = next(p["id"] for p in pozycje() if p["tekst_md"] == "Rycerz (3D)")
        self.assertBlad(409, zapis.przypisz_agenta, rycerz, "Karol", self.wersja("zadania"), "Karol")
        self.assertBlad(409, zapis.przypisz_agenta, zid, "Karol", "stara-wersja", "Karol")
        self.assertEqual(self.bajty("zadania"), przed)

    def test_dodaj_z_agentem_i_odhacz(self):
        w = zapis.dodaj_zadanie("Nowe dla Pawła", "teraz", "wysoki", self.wersja("zadania"), "Karol", agent="Paweł")
        self.assertEqual(w["opis"], "dodane zadanie: Nowe dla Pawła (Teraz, agent: Paweł)")
        oczek = wstaw_po(ZADANIA, "  - [ ] Podzadanie drugiego", ["- [ ] Nowe dla Pawła · agent: Paweł · #wysoki"])
        self.assertPlik("zadania", oczek)
        # bez dubli także wtedy, gdy istniejące zadanie ma agenta
        self.assertBlad(409, zapis.dodaj_zadanie, "Nowe dla Pawła", "backlog", "niski", self.wersja("zadania"), "Karol")
        # przypisanie tylko polem — nie w treści
        self.assertBlad(400, zapis.dodaj_zadanie, "Coś · agent: Paweł", "teraz", "niski", self.wersja("zadania"), "Karol")
        self.assertBlad(400, zapis.dodaj_zadanie, "Coś", "teraz", "niski", self.wersja("zadania"), "Karol", agent="Ktoś")
        zapis.odhacz(id_po_tekscie("Nowe dla Pawła"), None, self.wersja("zadania"), "Paweł")
        tekst = self.bajty("zadania").decode("utf-8-sig").replace("\r\n", "\n")
        self.assertIn("- [x] %s: Nowe dla Pawła · agent: Paweł\n" % DZIS, tekst)
        p = next(p for p in pozycje() if p["tekst_md"] == "Nowe dla Pawła")
        self.assertEqual((p["zrobione"], p["agent"]), (True, "Paweł"))


class TestPrzypisanieCRLF(TestPrzypisanie):
    nl = "\r\n"
    bom = True


class TestUprawnieniaPrzypisania(Baza):
    def test_gosc_nie_przypisuje(self):
        przed = self.bajty("zadania")
        zid = id_po_tekscie("Pierwsze zadanie")
        e = self.assertBlad(403, zapis._t_agent, _zadanie({"id": zid, "agent": "Paweł", "wersja": self.wersja("zadania")},
                                                         kto="Paweł"))
        self.assertEqual(e.dodatkowe.get("kod"), "brak_klucza_zatwierdzania")
        self.assertBlad(403, zapis._t_dodaj, _zadanie({"tekst": "X", "sekcja": "teraz", "priorytet": "niski",
                                                       "agent": "Paweł", "wersja": self.wersja("zadania")}, kto="Paweł"))
        self.assertEqual(self.bajty("zadania"), przed)
        # gość dodaje zwykłe zadanie jak dotąd (puste pole agenta)
        w = zapis._t_dodaj(_zadanie({"tekst": "Od gościa", "sekcja": "backlog", "priorytet": "niski", "agent": "",
                                     "wersja": self.wersja("zadania")}, kto="Paweł"))
        self.assertTrue(w["ok"])

    def test_lokalny_i_klucz_zatwierdzania(self):
        zid = id_po_tekscie("Pierwsze zadanie")
        w = zapis._t_agent(_zadanie({"id": zid, "agent": "Paweł", "wersja": self.wersja("zadania")}, lokalny=True,
                                    kto="Karol"))
        self.assertTrue(w["ok"])
        self.assertIn("- Karol: zadanie dla agenta Paweł", self.bajty("dziennik").decode("utf-8-sig"))
        zid = id_po_tekscie("Pierwsze zadanie")
        w = zapis._t_agent(_zadanie({"id": zid, "agent": "", "wersja": self.wersja("zadania")}, gd=True, kto="Paweł"))
        self.assertTrue(w["ok"])
        self.assertIn("- Paweł (klucz zatwierdzania): zadanie bez przypisanego agenta",
                      self.bajty("dziennik").decode("utf-8-sig"))


# =========================================================================== uruchamianie na właściwym komputerze
ZADANIA_AGENTA = ZADANIA.replace("- [ ] Pierwsze zadanie · #wysoki", "- [ ] Pierwsze zadanie · agent: Paweł · #wysoki") \
    .replace("- [ ] Coś na później · #niski", "- [ ] Coś na później · agent: Karol · #niski\n"
             "- [ ] Drugie dla Karola · agent: Karol")


class TestUruchamianie(Baza):
    def setUp(self):
        super().setUp()
        self.zapisz_pliki(zadania=ZADANIA_AGENTA)
        sejf.uniewaznij()
        self.watki = {}                                        # id wątku -> trwa
        self.polecenia = []
        self.prace = []
        self.osoba = ("Karol", "Karol")
        self.cfg = {}

        def uruchom_polecenie(tekst, kto, tytul=None, **kw):
            wid = "w-%d" % (len(self.polecenia) + 1)
            self.polecenia.append({"tekst": tekst, "kto": kto, "tytul": tytul, **kw})
            self.watki[wid] = True
            return {"watek": wid, "nr": 1, "od": 1, "tryb": kw.get("tryb")}

        def stan_watku(wid):
            if wid not in self.watki:
                return None
            return {"trwa": self.watki[wid], "ostatnia_odpowiedz": None if self.watki[wid] else "Zrobione.",
                    "blad": None}

        stary_cfg = rdzen.konfiguracja
        self.latki2 = [
            mock.patch.object(zadania_agenta, "_plik", lambda: os.path.join(self.tmp, "zadania_agenta.json")),
            mock.patch.object(zadania_agenta, "ja", lambda: self.osoba),
            mock.patch.object(agent, "uruchom_polecenie", uruchom_polecenie),
            mock.patch.object(agent, "stan_watku", stan_watku),
            mock.patch.object(prace, "rozpocznij", lambda pid, tytul, **kw: self.prace.append(("start", pid, tytul))),
            mock.patch.object(prace, "zakoncz", lambda pid, **kw: self.prace.append(("koniec", pid))),
            mock.patch.object(prace, "oznacz_blad", lambda pid, k: self.prace.append(("blad", pid, k))),
            mock.patch.object(rdzen, "konfiguracja", lambda: dict(stary_cfg(), **self.cfg)),
        ]
        for l in self.latki2:
            l.start()
        zadania_agenta._tlo["ostatnie_auto"] = 0.0

    def tearDown(self):
        for l in reversed(self.latki2):
            l.stop()
        super().tearDown()

    def test_tylko_wlasne_zadanie(self):
        cudze = id_po_tekscie("Pierwsze zadanie")
        e = self.assertBlad(409, zadania_agenta.uruchom, cudze, "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "cudze_zadanie")
        self.assertIn("Paweł", e.komunikat)
        bez_agenta = id_po_tekscie("Drugie [[Notatka]]")
        self.assertBlad(404, zadania_agenta.uruchom, bez_agenta, "Karol")
        self.assertEqual(self.polecenia, [])

        moje = id_po_tekscie("Coś na później")
        w = zadania_agenta.uruchom(moje, "Karol")
        self.assertEqual((w["stan"], w["agent"], w["praca"]), ("w_toku", "Karol", "zadanie-" + moje))
        self.assertEqual(self.polecenia[0]["tryb"], "praca")
        self.assertIn("<<<ZADANIE\nCoś na później\nZADANIE>>>", self.polecenia[0]["tekst"])
        self.assertIn("agenta osoby: Karol", self.polecenia[0]["tekst"])
        self.assertEqual(self.prace, [("start", "zadanie-" + moje, "Zadanie: Coś na później")])
        e = self.assertBlad(409, zadania_agenta.uruchom, moje, "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "trwa")

        # wątek skończył → obieg zamyka wpis i pracę; ponowne uruchomienie przyciskiem jest możliwe
        self.watki["w-1"] = False
        zadania_agenta.obieg()
        self.assertEqual(zadania_agenta._stan()[moje]["stan"], "gotowe")
        self.assertIn(("koniec", "zadanie-" + moje), self.prace)
        zadania_agenta.uruchom(moje, "Karol")
        self.assertEqual(len(self.polecenia), 2)

    def test_nieznana_osoba(self):
        self.osoba = (None, "przeczkowskyy")
        e = self.assertBlad(409, zadania_agenta.uruchom, id_po_tekscie("Coś na później"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "nieznana_osoba")
        self.assertIn("git config bc.osoba", e.komunikat)

    def test_u_pawla_uruchamia_sie_zadanie_pawla(self):
        self.osoba = ("Paweł", "Paweł")
        self.assertBlad(409, zadania_agenta.uruchom, id_po_tekscie("Coś na później"), "Paweł")
        w = zadania_agenta.uruchom(id_po_tekscie("Pierwsze zadanie"), "Paweł")
        self.assertEqual(w["agent"], "Paweł")

    def test_samo_uruchamianie(self):
        zadania_agenta.obieg(teraz_s=1000)                     # wyłączone: nic
        self.assertEqual(self.polecenia, [])
        self.cfg = {"zadania_agenta": {"auto": True}}
        zadania_agenta.obieg(teraz_s=2000)
        self.assertEqual(len(self.polecenia), 1)
        self.assertEqual(self.polecenia[0]["tytul"], "Zadanie: Coś na później")
        zadania_agenta.obieg(teraz_s=2000 + zadania_agenta.AUTO_CO_S + 1)   # po jednym naraz
        self.assertEqual(len(self.polecenia), 1)
        self.watki["w-1"] = False
        zadania_agenta.obieg(teraz_s=2000 + 2 * zadania_agenta.AUTO_CO_S + 2)
        self.assertEqual(len(self.polecenia), 2)
        self.assertEqual(self.polecenia[1]["tytul"], "Zadanie: Drugie dla Karola")
        self.watki["w-2"] = False
        for i in range(3, 6):                                  # zadania Pawła nigdy, raz uruchomione nie wracają same
            zadania_agenta.obieg(teraz_s=2000 + i * (zadania_agenta.AUTO_CO_S + 1))
        self.assertEqual(len(self.polecenia), 2)

    def test_watek_zniknal(self):
        moje = id_po_tekscie("Coś na później")
        zadania_agenta.uruchom(moje, "Karol")
        del self.watki["w-1"]
        zadania_agenta.obieg()
        self.assertEqual(zadania_agenta._stan()[moje]["stan"], "blad")
        self.assertEqual(self.prace[-1][0], "blad")

    def test_trasy(self):
        moje = id_po_tekscie("Coś na później")
        e = self.assertBlad(403, zadania_agenta._post_uruchom, _zadanie({"id": moje}, kto="Karol"))
        self.assertEqual(e.dodatkowe.get("kod"), "brak_uprawnien")
        self.assertBlad(403, zadania_agenta._post_auto, _zadanie({"auto": True}, gd=True, kto="Paweł"))
        w = zadania_agenta._post_uruchom(_zadanie({"id": moje}, lokalny=True, kto="Karol"))
        self.assertEqual(w["stan"], "w_toku")
        g = zadania_agenta._get(_zadanie({}, kto="gość"))
        self.assertEqual((g["ja"], g["auto"], g["mozna_uruchomic"]), ("Karol", False, False))
        self.assertNotIn("watek", g["stany"][moje])           # numer wątku tylko dla osoby przy komputerze
        g = zadania_agenta._get(_zadanie({}, lokalny=True, kto="Karol"))
        self.assertEqual(g["stany"][moje]["watek"], "w-1")


class TestParser(unittest.TestCase):
    def test_tylko_imie_na_koncu(self):
        self.assertEqual(sejf.agent_zadania("Opis · agent: Paweł"), ("Opis", "Paweł"))
        self.assertEqual(sejf.agent_zadania("Opis · agent: pawel"), ("Opis", "Paweł"))
        self.assertEqual(sejf.agent_zadania("Opis · Agent: Karol Balucki"), ("Opis", "Karol"))
        for t in ("pole „· agent: Imię” w Zadaniach, wybór (Karol)", "Opis · agent: Paweł, potem Karol",
                  "Opis agent: Paweł", "Opis · agent: "):
            self.assertEqual(sejf.agent_zadania(t), (t, None), t)


class TestKonfiguracjaISesja(unittest.TestCase):
    def test_wspolna_konfiguracja_nie_wlacza_samo_uruchamiania(self):
        cfg = rdzen._bezpieczna_wspolna({"zadania_agenta": {"auto": True}})
        self.assertNotIn("auto", cfg.get("zadania_agenta") or {})

    def test_polecenie_konca_sesji_zna_pole_agenta(self):
        self.assertIn("· agent: Imię", sesje.POLECENIE_AGENTA_ZADANIA)


if __name__ == "__main__":
    unittest.main()
