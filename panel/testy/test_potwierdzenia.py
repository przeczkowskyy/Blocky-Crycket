# -*- coding: utf-8 -*-
"""Potwierdzanie decyzji przez drugą osobę (D-043): parser pól podpisu (bc/sejf.py) i zapis odpowiedzi (bc/zapis.py).

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_potwierdzenia
Wyłącznie na kopii plików sejfu w katalogu tymczasowym (baza z test_zapis.py: LF, CRLF i BOM bajt w bajt).
"""
import os
import sys
import unittest

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from testy import test_zapis as tz  # noqa: E402  (moduł, nie klasy — discover nie uruchomi ich drugi raz)
from bc import sejf, zapis  # noqa: E402

DZIS = tz.DZIS                                                 # 2026-11-13 (podmienione zapis.dzis)

REJESTR = """---
status: kanon
---
# Rejestr decyzji

Statusy: ✅ zatwierdzona · 🕓 do decyzji · 💡 propozycja

---

### D-001 Stara decyzja
✅ zatwierdzona · styl · zdecydował: Karol 2026-11-12
Opis starej.

### D-002 Decyzja Karola
✅ zatwierdzona · game design · 2026-11-13 · zdecydował: Karol Balucki 2026-11-13
Opis drugiej.
Uzasadnienie — Karol Balucki, 2026-11-13: Bo tak ustaliliśmy

### D-003 Odrzucona przez Pawła
❌ odrzucona · technika · zdecydował: Paweł 2026-11-13
Opis trzeciej.

### D-004 Dawny Game Director
✅ zatwierdzona · styl · zdecydował: Game Director (Paweł) 2026-11-13
Opis czwartej.

### D-005 Już potwierdzona
✅ zatwierdzona · narzędzia · zdecydował: Karol 2026-11-13 · potwierdził: Paweł 2026-11-13
Opis piątej.

### D-006 Propozycja
💡 propozycja · narzędzia
Opis szóstej.

---
*Stopka rejestru.*
"""

L2 = "✅ zatwierdzona · game design · 2026-11-13 · zdecydował: Karol Balucki 2026-11-13"
L3 = "❌ odrzucona · technika · zdecydował: Paweł 2026-11-13"


class Baza(tz.Baza):
    def setUp(self):
        super().setUp()
        self.zapisz_pliki(decyzje=REJESTR)
        sejf.uniewaznij()
        self.zdarzenia = []
        zapis.dodaj_sluchacza(self.zdarzenia.append)

    def tearDown(self):
        zapis.usun_sluchacza(self.zdarzenia.append)
        super().tearDown()

    def decyzja(self, ident):
        return next(d for d in sejf.plan()["decyzje"] if d["id"] == ident)

    def tekst(self, klucz):
        return self.bajty(klucz).decode("utf-8-sig").replace("\r\n", "\n")

    def agenda(self):
        with open(os.path.join(self.sejf, "Produkcja", "Sesje główne.md"), encoding="utf-8") as f:
            return f.read()

    def potwierdz(self, ident, odp, kto="Paweł", uz=None, **kw):
        return zapis.potwierdz_decyzje(ident, odp, uz, self.wersja("decyzje"), kto, **kw)


class TestWykrywanie(Baza):
    def test_ktore_czekaja(self):
        czeka = {d["id"]: d["czeka_na"] for d in sejf.plan()["decyzje"]}
        self.assertEqual(czeka, {"D-001": None,                # podpis sprzed 13.11 — nie czeka
                                 "D-002": "Paweł",             # pełne imię „Karol Balucki” = Karol
                                 "D-003": "Karol",             # odrzucenie też czeka
                                 "D-004": None,                # dawny podpis Game Directora
                                 "D-005": None,                # dwa podpisy
                                 "D-006": None})
        d = self.decyzja("D-002")
        self.assertEqual(d["zdecydowal"], {"kto": "Karol Balucki", "data": "2026-11-13"})
        self.assertIsNone(d["potwierdzil"])
        self.assertEqual(self.decyzja("D-005")["potwierdzil"], {"kto": "Paweł", "data": "2026-11-13"})

    def test_kanoniczne_imie(self):
        self.assertEqual(sejf.kanoniczne("Paweł Nowak"), "pawel")
        self.assertEqual(sejf.kanoniczne("  KAROL  "), "karol")
        self.assertEqual(sejf.osoba_zespolu("pawel"), "Paweł")
        self.assertIsNone(sejf.osoba_zespolu("Zenek"))
        self.assertIsNone(sejf.osoba_zespolu(""))

    def test_pola_sprzeciwu(self):
        p = sejf.pola_podpisu("🕓 do decyzji · x · sprzeciw: Paweł 2026-11-14 (wobec: odrzucona przez Karol Balucki 2026-11-13)")
        self.assertEqual(p["sprzeciw"], {"kto": "Paweł", "data": "2026-11-14",
                                         "wobec": {"status": "odrzucona", "kto": "Karol Balucki", "data": "2026-11-13"}})
        self.assertIsNone(p["zdecydowal"])


class TestZapisPotwierdzen(Baza):
    def test_zgoda(self):
        w = self.potwierdz("D-002", "zgoda")
        self.assertPlik("decyzje", tz.zamien_linie(REJESTR, L2, L2 + " · potwierdził: Paweł %s" % DZIS))
        self.assertIsNone(self.decyzja("D-002")["czeka_na"])
        self.assertEqual(w["potwierdzenie"]["odpowiedz"], "zgoda")
        self.assertIn("\n- Paweł: decyzja D-002 potwierdzona: zgoda (zatwierdzona przez Karol Balucki 2026-11-13), "
                      "przez panel ([[Rejestr decyzji]])\n", self.tekst("dziennik"))
        self.assertEqual(self.zdarzenia, [{"typ": "potwierdzenie", "id": "D-002", "odpowiedz": "zgoda", "kto": "Paweł",
                                           "skad": "panel"}])

    def test_zgoda_pelnym_imieniem_i_przez_telegram(self):
        zapis.potwierdz_decyzje("D-003", "zgoda", None, None, "Karol", zapis.ZNACZNIK_TELEGRAMA, skad="telegram")
        self.assertPlik("decyzje", tz.zamien_linie(REJESTR, L3, L3 + " · potwierdził: Karol %s" % DZIS))
        self.assertIn("\n- Karol (Telegram): decyzja D-003 potwierdzona: zgoda (odrzucona przez Paweł 2026-11-13), "
                      "przez Telegram ([[Rejestr decyzji]])\n", self.tekst("dziennik"))

    def test_sprzeciw_z_powodem(self):
        self.potwierdz("D-002", "sprzeciw", uz="Za drogie\nna start")
        nowy = "🕓 do decyzji · game design · 2026-11-13 · sprzeciw: Paweł %s (wobec: zatwierdzona przez Karol Balucki " \
               "2026-11-13)" % DZIS
        oczek = tz.zamien_linie(REJESTR, L2, nowy)
        oczek = tz.wstaw_po(oczek, "Uzasadnienie — Karol Balucki, 2026-11-13: Bo tak ustaliliśmy",
                            ["Uzasadnienie sprzeciwu — Paweł, %s: Za drogie / na start" % DZIS])
        self.assertPlik("decyzje", oczek)
        d = self.decyzja("D-002")
        self.assertEqual((d["status"], d["czeka_na"], d["zdecydowal"]), ("do_decyzji", None, None))
        self.assertEqual(d["sprzeciw"]["wobec"]["kto"], "Karol Balucki")
        self.assertIn("- Paweł: decyzja D-002: brak zgody (zatwierdzona przez Karol Balucki 2026-11-13) — wraca "
                      "„do decyzji”, przez panel", self.tekst("dziennik"))

    def test_sprzeciw_bez_powodu_i_ponowna_decyzja_czysci_slad(self):
        self.potwierdz("D-003", "sprzeciw", kto="Karol")
        nowy = "🕓 do decyzji · technika · sprzeciw: Karol %s (wobec: odrzucona przez Paweł 2026-11-13)" % DZIS
        self.assertPlik("decyzje", tz.zamien_linie(REJESTR, L3, nowy))
        # ponowna decyzja (kogokolwiek) zaczyna od nowa: bez „sprzeciw:”, nowy podpis, znów czeka
        zapis.zmien_status_decyzji("D-003", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")
        self.assertPlik("decyzje", tz.zamien_linie(REJESTR, L3, "✅ zatwierdzona · technika · zdecydował: Paweł %s" % DZIS))
        self.assertEqual(self.decyzja("D-003")["czeka_na"], "Karol")

    def test_ponowna_decyzja_czysci_potwierdzenie_i_rozmowe(self):
        linia = "✅ zatwierdzona · technika · zdecydował: Paweł 2026-11-13"
        for slad in ("potwierdził: Karol 2026-11-13", "do rozmowy: Karol 2026-11-13 (wobec: zatwierdzona przez Paweł 2026-11-13)"):
            stara = "🕓 do decyzji · technika · " + slad
            self.zapisz_pliki(decyzje=tz.zamien_linie(REJESTR, L3, stara))
            sejf.uniewaznij()
            zapis.zmien_status_decyzji("D-003", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")
            self.assertPlik("decyzje", tz.zamien_linie(REJESTR, L3, linia))

    def test_rozmowa_dopisuje_temat_agendy(self):
        w = self.potwierdz("D-002", "rozmowa", uz="Pogadajmy o cenie")
        nowy = "🕓 do decyzji · game design · 2026-11-13 · do rozmowy: Paweł %s (wobec: zatwierdzona przez Karol " \
               "Balucki 2026-11-13)" % DZIS
        self.assertPlik("decyzje", tz.zamien_linie(REJESTR, L2, nowy))
        self.assertTrue(w["agenda"])
        agenda = self.agenda()
        self.assertIn("- [ ] Decyzja Karola (D-002) — Pogadajmy o cenie · dodał: Paweł %s" % DZIS, agenda)
        dz = self.tekst("dziennik")
        self.assertIn("decyzja D-002: do rozmowy na sesji głównej (zatwierdzona przez Karol Balucki 2026-11-13)", dz)
        self.assertIn("temat na sesję główną: Decyzja Karola (D-002)", dz)

    def test_rozmowa_awaria_agendy(self):
        """Rejestr zapisany, agenda nie (błąd HTTP albo nieoczekiwany wyjątek): wynik mówi to wprost, bez wyjątku."""
        from unittest import mock
        from bc import sesje
        from bc.rdzen import BladHTTP
        for awaria in (BladHTTP(500, "Nie udało się zapisać pliku"), OSError("plik zablokowany")):
            self.zapisz_pliki(decyzje=REJESTR)
            sejf.uniewaznij()
            with mock.patch.object(sesje, "dodaj_temat", side_effect=awaria):
                w = self.potwierdz("D-002", "rozmowa")
            self.assertIs(w["agenda"], False)
            self.assertIn("nie trafił na agendę", w["uwaga"])
            self.assertIn("do rozmowy: Paweł %s" % DZIS, self.tekst("decyzje"))
            p = os.path.join(self.sejf, "Produkcja", "Sesje główne.md")
            self.assertFalse(os.path.exists(p) and "(D-002)" in self.agenda())

    def test_rozmowa_gdy_temat_juz_czeka(self):
        from bc import sesje
        sesje.dodaj_temat("Już na agendzie", "", "D-003", None, "Karol")
        w = self.potwierdz("D-003", "rozmowa", kto="Karol")
        self.assertTrue(w["agenda"])
        self.assertNotIn("uwaga", w)
        self.assertEqual(self.agenda().count("(D-003)"), 1)

    def test_wlasna_decyzja(self):
        przed = self.bajty("decyzje")
        for kto in ("Karol", "karol balucki", "KAROL"):
            e = self.assertBlad(403, self.potwierdz, "D-002", "zgoda", kto=kto)
            self.assertEqual(e.dodatkowe.get("kod"), "wlasna_decyzja")
            self.assertIn("To Twoja decyzja", e.komunikat)
        self.assertEqual(self.bajty("decyzje"), przed)
        self.assertEqual(self.zdarzenia, [])

    def test_nic_nie_czeka_i_podwojne_klikniecie(self):
        przed = self.bajty("decyzje")
        for ident in ("D-001", "D-004", "D-005", "D-006"):
            e = self.assertBlad(409, self.potwierdz, ident, "zgoda")
            self.assertEqual(e.dodatkowe.get("kod"), "nic_nie_czeka", ident)
        self.assertEqual(self.bajty("decyzje"), przed)
        self.potwierdz("D-002", "zgoda")
        e = self.assertBlad(409, self.potwierdz, "D-002", "zgoda")       # drugi raz: już dwa podpisy
        self.assertIn("ma już dwa podpisy", e.komunikat)
        e = self.assertBlad(409, self.potwierdz, "D-002", "sprzeciw")
        self.assertEqual(e.dodatkowe.get("kod"), "nic_nie_czeka")

    def test_zle_dane_i_osoba_spoza_zespolu(self):
        self.assertBlad(400, self.potwierdz, "D-002", "moze")
        self.assertBlad(400, self.potwierdz, "X-002", "zgoda")
        self.assertBlad(400, self.potwierdz, "D-002", "zgoda", kto="gość")
        e = self.assertBlad(403, self.potwierdz, "D-002", "zgoda", kto="Zenek")
        self.assertEqual(e.dodatkowe.get("kod"), "spoza_zespolu")
        self.assertBlad(404, self.potwierdz, "D-077", "zgoda")
        e = self.assertBlad(409, zapis.potwierdz_decyzje, "D-002", "zgoda", None, "0" * 16, "Paweł")
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_wersji")

    def test_odcisk_decyzji_zmienionej_w_miedzyczasie(self):
        d = self.decyzja("D-002")
        stary = sejf.odcisk_decyzji("D-002", d["status"], d)
        e = self.assertBlad(409, self.potwierdz, "D-002", "zgoda", odcisk="deadbeef")
        self.assertEqual(e.dodatkowe.get("kod"), "decyzja_zmieniona")
        # ta sama decyzja podjęta na nowo (inna data podpisu) = inny odcisk
        self.zapisz_pliki(decyzje=REJESTR.replace("zdecydował: Karol Balucki 2026-11-13", "zdecydował: Karol 2026-11-14"))
        sejf.uniewaznij()
        e = self.assertBlad(409, self.potwierdz, "D-002", "zgoda", odcisk=stary)
        self.assertEqual(e.dodatkowe.get("kod"), "decyzja_zmieniona")
        d = self.decyzja("D-002")
        self.potwierdz("D-002", "zgoda", odcisk=sejf.odcisk_decyzji("D-002", d["status"], d))
        self.assertIsNone(self.decyzja("D-002")["czeka_na"])

    def test_powod_sprzeciwu_pozniej(self):
        self.potwierdz("D-002", "sprzeciw")
        zapis.dopisz_powod_sprzeciwu("D-002", "Bo za wcześnie", "Paweł", zapis.ZNACZNIK_TELEGRAMA)
        self.assertIn("\nUzasadnienie sprzeciwu — Paweł, %s: Bo za wcześnie\n" % DZIS, self.tekst("decyzje"))
        e = self.assertBlad(409, zapis.dopisz_powod_sprzeciwu, "D-002", "x", "Karol")      # nie jego sprzeciw
        self.assertEqual(e.dodatkowe.get("kod"), "nic_nie_czeka")

    def test_status_z_trasy_powiadamia(self):
        cialo = {"status": "odrzucona", "wersja": self.wersja("decyzje")}
        zapis._t_status(tz._zadanie(cialo, lokalny=True, kto="Karol", params={"id": "D-006"}))
        self.assertEqual(self.zdarzenia, [{"typ": "status", "id": "D-006", "status": "odrzucona", "kto": "Karol",
                                           "skad": "panel"}])
        self.assertEqual(self.decyzja("D-006")["czeka_na"], "Paweł")

    def test_sluchacz_z_bledem_nie_psuje_zapisu(self):
        def zly(_):
            raise RuntimeError("awaria")
        zapis.dodaj_sluchacza(zly)
        try:
            self.potwierdz("D-002", "zgoda")
        finally:
            zapis.usun_sluchacza(zly)
        self.assertIn("potwierdził: Paweł", self.tekst("decyzje"))


class TestZapisPotwierdzenCRLF(TestZapisPotwierdzen):
    nl = "\r\n"


class TestZapisPotwierdzenBOM(TestZapisPotwierdzen):
    bom = True


class TestTrasaPotwierdzenia(Baza):
    def cialo(self, odp="zgoda", **kw):
        return dict({"odpowiedz": odp, "wersja": self.wersja("decyzje")}, **kw)

    def test_uprawnienia(self):
        przed = self.bajty("decyzje")
        e = self.assertBlad(403, zapis._t_potwierdzenie, tz._zadanie(self.cialo(), kto="Paweł", params={"id": "D-002"}))
        self.assertEqual(e.dodatkowe.get("kod"), "brak_klucza_zatwierdzania")              # gość z kodem dostępu
        e = self.assertBlad(400, zapis._t_potwierdzenie, tz._zadanie(self.cialo(), lokalny=True, kto="Karol Balucki",
                                                                   params={"id": "D-002"}, z_naglowka=False))
        self.assertEqual(e.dodatkowe.get("kod"), "brak_imienia")                           # imię z gita nie podpisuje
        e = self.assertBlad(400, zapis._t_potwierdzenie, tz._zadanie(self.cialo(), gd=True, kto="gość",
                                                                   params={"id": "D-002"}))
        self.assertEqual(e.dodatkowe.get("kod"), "brak_imienia")
        e = self.assertBlad(403, zapis._t_potwierdzenie, tz._zadanie(self.cialo(), lokalny=True, kto="Karol",
                                                                   params={"id": "D-002"}))
        self.assertEqual(e.dodatkowe.get("kod"), "wlasna_decyzja")
        self.assertBlad(400, zapis._t_potwierdzenie, tz._zadanie({"odpowiedz": "zgoda", "wersja": self.wersja("decyzje"),
                                                                 "inne": 1}, gd=True, kto="Paweł", params={"id": "D-002"}))
        self.assertBlad(400, zapis._t_potwierdzenie, tz._zadanie({"odpowiedz": "zgoda"}, gd=True, kto="Paweł",
                                                                params={"id": "D-002"}))
        self.assertEqual(self.bajty("decyzje"), przed)
        # klucz zatwierdzania (np. telefon przez tunel): znacznik w Dzienniku
        w = zapis._t_potwierdzenie(tz._zadanie(self.cialo(), gd=True, kto="Paweł", params={"id": "D-002"}))
        self.assertTrue(w["ok"])
        self.assertIn("- Paweł (klucz zatwierdzania): decyzja D-002 potwierdzona: zgoda", self.tekst("dziennik"))
        # osoba przy komputerze
        zapis._t_potwierdzenie(tz._zadanie(self.cialo("sprzeciw", uzasadnienie="Nie"), lokalny=True, kto="Karol",
                                           params={"id": "D-003"}))
        self.assertIn("sprzeciw: Karol %s" % DZIS, self.tekst("decyzje"))


if __name__ == "__main__":
    unittest.main()
