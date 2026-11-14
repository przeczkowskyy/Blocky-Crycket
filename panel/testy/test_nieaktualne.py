# -*- coding: utf-8 -*-
"""„Nieaktualne” (14.11) — trzecia możliwość obok odpowiedzi, Akceptuję i Do poprawy: zdjęcie sprawy z kolejki.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_nieaktualne

Wszystko na kopiach w katalogach tymczasowych (sejf, panel/dane, dane lokalne); bot Telegram tylko na atrapie API.
- pytanie: zwykły wiersz odpowiedzi zaczynający się od słowa „nieaktualne”; parser podaje pole `nieaktualne`
  (decyduje OSTATNIA odpowiedź);
- decyzja: status „🗃️ nieaktualna” w Rejestrze z podpisem „oznaczył: Imię data”, opcjonalne uzasadnienie, ślad
  w Dzienniku, bez czekania na drugą osobę i bez alertu Telegrama, samo-rozstrzyganie pytań, powrót na „do decyzji”,
  uprawnienia, konflikt wersji, próby wstrzyknięcia struktury w powodzie;
- raport: trzecia wartość decyzji „nieaktualne”, zmiana decyzji, narzędzie panel/narzedzia/raport.py;
- API na prawdziwym serwerze testowym (trasy, pole `funkcje` planu).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from testy import test_zapis as tz  # noqa: E402
from testy import test_telegram as tt  # noqa: E402
from testy import test_api  # noqa: E402  (bez importu klas: discover uruchomiłby je drugi raz)
from bc import rdzen, raporty, sejf, zapis  # noqa: E402

DZIS = tz.DZIS
E = "\U0001F5C3️"                                            # 🗃️ — kartoteka z selektorem wariantu


# =========================================================================== pytania
class TestPytanieNieaktualne(tz.Baza):
    def pytanie(self, nr):
        return {p["nr"]: p for p in sejf.plan()["pytania"]}[nr]

    def test_parser_ostatnia_odpowiedz_decyduje(self):
        przypadki = [
            ("", False),
            ("- Karol (2026-11-14): nieaktualne", True),
            ("- Karol (2026-11-14): Nieaktualne — temat zamknięty na sesji", True),
            ("- Paweł (klucz zatwierdzania, 2026-11-14): NIEAKTUALNE", True),
            ("- Paweł (gość panelu, 2026-11-14): nieaktualna sprawa", True),
            ("- Karol: nieaktualne", True),
            ("nieaktualne, zamknięte", True),                                 # odpowiedź w tym samym wierszu
            ("- Karol (2026-11-14): nie, to wciąż aktualne", False),
            ("- Karol (2026-11-14): nieaktualne\n- Paweł (2026-11-14): A jednak wracamy do tematu.", False),
            ("- Karol (2026-11-13): tak\n- Paweł (2026-11-14): nieaktualne — po sesji", True),
            ("- Karol (2026-11-14): nieaktualne\n  wcięta kontynuacja", True),
            ("- Karol (2026-11-14): Odpowiedź merytoryczna, słowo nieaktualne dalej", False),
        ]
        for odp, oczek in przypadki:
            self.assertEqual(sejf.jest_nieaktualne(odp), oczek, odp)

    def test_wiersz_odpowiedzi_i_pole_parsera(self):
        self.assertFalse(self.pytanie(2)["nieaktualne"])
        self.assertFalse(self.pytanie(1)["nieaktualne"])                    # „Już jest.” = zwykła odpowiedź
        w = zapis.odpowiedz(2, "nieaktualne — omówione na sesji", self.wersja("pytania"), "Karol")
        self.assertEqual(w["opis"], "odpowiedź na pytanie 2")
        oczek = tz.PYTANIA.replace("Treść drugiego.\n**Odpowiedź:**\n",
                                   "Treść drugiego.\n**Odpowiedź:**\n- Karol (%s): nieaktualne — omówione na sesji\n" % DZIS)
        self.assertPlik("pytania", oczek)
        p = self.pytanie(2)
        self.assertEqual((p["otwarte"], p["nieaktualne"]), (False, True))
        p = {x["nr"]: x for x in w["plan"]["pytania"]}[2]                    # odpowiedź trasy ma już nowe pole
        self.assertTrue(p["nieaktualne"])
        self.assertTrue(w["plan"]["funkcje"]["nieaktualne"])
        # sam wyraz, bez powodu
        zapis.odpowiedz(4, "nieaktualne", self.wersja("pytania"), "Paweł", "gość panelu")
        self.assertTrue(self.pytanie(4)["nieaktualne"])
        self.assertIn("\n- Paweł (gość panelu, %s): nieaktualne" % DZIS, self.bajty("pytania").decode("utf-8-sig").replace("\r\n", "\n"))
        # późniejsza zwykła odpowiedź zdejmuje oznaczenie (ostatnia odpowiedź decyduje)
        zapis.odpowiedz(2, "Wracamy do tematu: zielony dach.", self.wersja("pytania"), "Paweł")
        p = self.pytanie(2)
        self.assertEqual((p["otwarte"], p["nieaktualne"]), (False, False))
        dz = self.bajty("dziennik").decode("utf-8-sig").replace("\r\n", "\n")
        self.assertIn("- Karol: odpowiedź na pytanie 2 ([[Pytania otwarte]])", dz)

    def test_ta_sama_dwa_razy(self):
        zapis.odpowiedz(2, "nieaktualne", self.wersja("pytania"), "Karol")
        e = self.assertBlad(409, zapis.odpowiedz, 2, "nieaktualne", self.wersja("pytania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "juz_zapisane")


class TestPytanieNieaktualneCRLF(TestPytanieNieaktualne):
    nl = "\r\n"


# =========================================================================== decyzje
class TestDecyzjaNieaktualna(tz.Baza):
    def tekst(self, klucz):
        return self.bajty(klucz).decode("utf-8-sig").replace("\r\n", "\n")

    def decyzja(self, ident):
        return {d["id"]: d for d in sejf.plan()["decyzje"]}[ident]

    def test_wiersz_statusu_podpis_uzasadnienie_dziennik(self):
        w = zapis.zmien_status_decyzji("D-002", "nieaktualna", "Po sesji 14.11\nnieaktualne", self.wersja("decyzje"), "Karol")
        self.assertEqual(w["opis"], "decyzja D-002 oznaczona jako nieaktualna")
        self.assertEqual(w["rozstrzygniete"], [])
        oczek = tz.zamien_linie(tz.DECYZJE, "💡 propozycja · game design · 2026-11-13 · źródło: [[Notatka]]",
                                E + " nieaktualna · game design · 2026-11-13 · źródło: [[Notatka]] · oznaczył: Karol %s" % DZIS)
        oczek = tz.wstaw_po(oczek, "Powiązane: [[Inna]]", ["Uzasadnienie — Karol, %s: Po sesji 14.11 / nieaktualne" % DZIS])
        self.assertPlik("decyzje", oczek)
        d = self.decyzja("D-002")
        self.assertEqual((d["status"], d["emoji"], d["kategoria"]), ("nieaktualna", E, "game design"))
        self.assertIsNone(d["czeka_na"])                                    # nie czeka na drugą osobę
        self.assertIsNone(d["zdecydowal"])
        self.assertEqual(d["meta"][-1], "oznaczył: Karol %s" % DZIS)
        self.assertIn("\n- Karol: decyzja D-002 oznaczona jako nieaktualna ([[Rejestr decyzji]])\n", self.tekst("dziennik"))
        # z „do decyzji” z dopiskiem i bez uzasadnienia — dopiski zostają bajt w bajt
        zapis.zmien_status_decyzji("D-003", "nieaktualna", "", self.wersja("decyzje"), "Paweł", "klucz zatwierdzania")
        self.assertIn("\n%s nieaktualna · technika · zaproponował: Claude Code · oznaczył: Paweł %s\nOpis trzeciej.\n" % (E, DZIS),
                      self.tekst("decyzje"))
        self.assertIn("- Paweł (klucz zatwierdzania): decyzja D-003 oznaczona jako nieaktualna ([[Rejestr decyzji]])",
                      self.tekst("dziennik"))

    def test_kodowanie_emoji(self):
        zapis.zmien_status_decyzji("D-005", "nieaktualna", None, self.wersja("decyzje"), "Karol")
        surowe = self.bajty("decyzje")
        self.assertIn("\U0001F5C3️ nieaktualna · narzędzia".encode("utf-8"), surowe)
        self.assertIn(b"\xf0\x9f\x97\x83\xef\xb8\x8f nieaktualna", surowe)    # U+1F5C3 U+FE0F w UTF-8

    def test_powrot_do_decyzji_i_zamkniety_status(self):
        zapis.zmien_status_decyzji("D-002", "nieaktualna", None, self.wersja("decyzje"), "Karol")
        przed = self.bajty("decyzje")
        for status in ("zatwierdzona", "odrzucona"):                        # najpierw „Przywróć”
            e = self.assertBlad(409, zapis.zmien_status_decyzji, "D-002", status, None, self.wersja("decyzje"), "Paweł")
            self.assertEqual(e.dodatkowe.get("kod"), "status_zamkniety")
            self.assertIn("Przywróć", e.komunikat)
        e = self.assertBlad(409, zapis.zmien_status_decyzji, "D-002", "nieaktualna", None, self.wersja("decyzje"), "Paweł")
        self.assertNotEqual(e.dodatkowe.get("kod"), "konflikt_wersji")      # ten sam status
        self.assertEqual(self.bajty("decyzje"), przed)
        w = zapis.zmien_status_decyzji("D-002", "do_decyzji", None, self.wersja("decyzje"), "Paweł")
        self.assertEqual(w["opis"], "decyzja D-002 oznaczona „do decyzji”")
        self.assertIn("\n🕓 do decyzji · game design · 2026-11-13 · źródło: [[Notatka]] · oznaczył: Paweł %s\n" % DZIS,
                      self.tekst("decyzje"))                                # podpis zastąpiony, nie zdublowany
        self.assertEqual(self.decyzja("D-002")["status"], "do_decyzji")
        zapis.zmien_status_decyzji("D-002", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")   # dalej zwykła droga
        self.assertEqual(self.decyzja("D-002")["status"], "zatwierdzona")

    def test_zamknietych_nie_oznacza(self):
        przed = self.bajty("decyzje")
        for ident in ("D-001", "D-004"):                                    # zatwierdzona, zastąpiona
            e = self.assertBlad(409, zapis.zmien_status_decyzji, ident, "nieaktualna", None, self.wersja("decyzje"), "Karol")
            self.assertEqual(e.dodatkowe.get("kod"), "status_zamkniety")
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_konflikt_wersji(self):
        stara = self.wersja("decyzje")
        zapis.zmien_status_decyzji("D-003", "nieaktualna", None, stara, "Karol")
        przed = self.bajty("decyzje")
        e = self.assertBlad(409, zapis.zmien_status_decyzji, "D-005", "nieaktualna", None, stara, "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_wersji")
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_wstrzykniecie_przez_powod(self):
        przed = {k: self.bajty(k) for k in tz.PLIKI}
        for zly in ("## Nowa sekcja", "### D-099 Podrobiona", "- [ ] zadanie", "[x] zrobione", "Tekst **Odpowiedź:** x",
                    "a · [ ] b", "x" * 1001):
            self.assertBlad(400, zapis.zmien_status_decyzji, "D-002", "nieaktualna", zly, self.wersja("decyzje"), "Karol")
        for zly in ("nieaktualne **Odpowiedź:** podrobiona", "nieaktualne · [ ] pole", "nieaktualne " + "x" * 2000):
            self.assertBlad(400, zapis.odpowiedz, 2, zly, self.wersja("pytania"), "Karol")
        self.assertEqual({k: self.bajty(k) for k in tz.PLIKI}, przed)
        # wiele linii i znaki sterujące = jedna linia (nowy wiersz statusu ani nagłówek nie powstają)
        zapis.zmien_status_decyzji("D-002", "nieaktualna", "pierwsza\n### D-099 druga‮", self.wersja("decyzje"), "Karol")
        t = self.tekst("decyzje")
        self.assertIn("\nUzasadnienie — Karol, %s: pierwsza / ### D-099 druga\n" % DZIS, t)
        self.assertNotIn("\n### D-099", t)
        self.assertEqual(len(sejf.plan()["decyzje"]), 5)

    def test_potwierdzanie_nie_dotyczy(self):
        zapis.zmien_status_decyzji("D-002", "nieaktualna", None, self.wersja("decyzje"), "Karol")
        e = self.assertBlad(409, zapis.potwierdz_decyzje, "D-002", "zgoda", None, self.wersja("decyzje"), "Paweł")
        self.assertEqual(e.dodatkowe.get("kod"), "nic_nie_czeka")

    # --- uprawnienia (trasa)
    def test_uprawnienia(self):
        przed = {k: self.bajty(k) for k in tz.PLIKI}
        cialo = {"status": "nieaktualna", "uzasadnienie": "stare", "wersja": self.wersja("decyzje")}
        for kto in ("gość", "Paweł"):                                       # gość z kodem dostępu: nie
            e = self.assertBlad(403, zapis._t_status, tz._zadanie(cialo, kto=kto, params={"id": "D-002"}))
            self.assertEqual(e.dodatkowe.get("kod"), "brak_klucza_zatwierdzania")
        for kw in ({"lokalny": True, "kto": ""}, {"gd": True, "kto": "gość"},
                   {"lokalny": True, "kto": "Karol", "z_naglowka": False}):  # decyzja musi mieć podpis z Ustawień
            e = self.assertBlad(400, zapis._t_status, tz._zadanie(cialo, params={"id": "D-002"}, **kw))
            self.assertEqual(e.dodatkowe.get("kod"), "brak_imienia")
        self.assertEqual({k: self.bajty(k) for k in tz.PLIKI}, przed)
        w = zapis._t_status(tz._zadanie(cialo, gd=True, kto="Paweł", params={"id": "D-002"}))   # klucz zatwierdzania
        self.assertTrue(w["ok"])
        self.assertIn("· oznaczył: Paweł %s\n" % DZIS, self.tekst("decyzje"))
        w = zapis._t_status(tz._zadanie({"status": "nieaktualna", "wersja": self.wersja("decyzje")}, lokalny=True,
                                        kto="Karol", params={"id": "D-005"}))   # osoba przy komputerze
        self.assertTrue(w["ok"])
        # gość może oznaczyć jako nieaktualne PYTANIE (tak jak odpowiadać)
        w = zapis._t_odpowiedz(tz._zadanie({"tekst": "nieaktualne", "wersja": self.wersja("pytania")}, kto="Paweł",
                                           params={"nr": "2"}))
        self.assertTrue({p["nr"]: p for p in w["plan"]["pytania"]}[2]["nieaktualne"])


class TestDecyzjaNieaktualnaCRLF(TestDecyzjaNieaktualna):
    nl = "\r\n"


class TestDecyzjaNieaktualnaBOM(TestDecyzjaNieaktualna):
    bom = True


class TestSamoRozstrzyganieNieaktualna(tz.Baza):
    def setUp(self):
        super().setUp()
        self.zapisz_pliki(pytania=tz.PYTANIA_ROZSTRZYGA)
        sejf.uniewaznij()

    def tekst(self, klucz):
        return self.bajty(klucz).decode("utf-8-sig").replace("\r\n", "\n")

    def test_nieaktualna_rozstrzyga_pytanie(self):
        w = zapis.zmien_status_decyzji("D-002", "nieaktualna", "Temat zamknięty", self.wersja("decyzje"), "Karol")
        self.assertEqual([r["nr"] for r in w["rozstrzygniete"]], [1])
        self.assertEqual(w["rozstrzygniete"][0]["decyzje"], [{"id": "D-002", "status": "nieaktualna"}])
        self.assertIn("Rozstrzyga: D-002\n**Odpowiedź:**\n- Karol (%s): rozstrzygnięte decyzjami: D-002 nieaktualna "
                      "(„Temat zamknięty”)\n" % DZIS, self.tekst("pytania"))
        self.assertIn("- Karol: odpowiedź na pytanie 1 (rozstrzygnięte decyzjami: D-002 nieaktualna („Temat zamknięty”)) "
                      "([[Pytania otwarte]])", self.tekst("dziennik"))
        p = {x["nr"]: x for x in w["plan"]["pytania"]}[1]
        self.assertEqual((p["otwarte"], p["nieaktualne"]), (False, False))   # odpowiedź mówi „rozstrzygnięte”

    def test_mieszane(self):
        w = zapis.zmien_status_decyzji("D-003", "nieaktualna", None, self.wersja("decyzje"), "Paweł", "klucz zatwierdzania")
        self.assertEqual(w["rozstrzygniete"], [])                          # D-005 dalej otwarta
        w = zapis.zmien_status_decyzji("D-005", "zatwierdzona", None, self.wersja("decyzje"), "Paweł", "klucz zatwierdzania")
        self.assertEqual([r["nr"] for r in w["rozstrzygniete"]], [2, 4])
        self.assertIn("- Paweł (klucz zatwierdzania, %s): rozstrzygnięte decyzjami: D-003 nieaktualna, D-005 zatwierdzona\n"
                      % DZIS, self.tekst("pytania"))

    def test_przywrocenie_nie_otwiera_pytania(self):
        zapis.zmien_status_decyzji("D-002", "nieaktualna", None, self.wersja("decyzje"), "Karol")
        po = self.bajty("pytania")
        w = zapis.zmien_status_decyzji("D-002", "do_decyzji", None, self.wersja("decyzje"), "Karol")
        self.assertEqual(w["rozstrzygniete"], [])
        self.assertEqual(self.bajty("pytania"), po)


# =========================================================================== zapis panelu na starym kodzie
class TestSprzecznyStatus(tz.Baza):
    """Panel sprzed 14.11 nie zna „🗃️ nieaktualna”: bierze decyzję za propozycję i przy „Tak” wstawia pod nagłówkiem
    DRUGI wiersz statusu. Nowy panel wykrywa taki zapis: decyzja nie czeka na potwierdzenie (brak alertu Telegrama),
    a zmiana statusu i potwierdzenie kończą się 409 „sprzeczny_status” bez zapisu."""
    STARY = "✅ zatwierdzona · zdecydował: Paweł %s" % DZIS

    def setUp(self):
        super().setUp()
        tekst = tz.zamien_linie(tz.DECYZJE, "💡 propozycja · game design · 2026-11-13 · źródło: [[Notatka]]",
                                E + " nieaktualna · game design · 2026-11-13 · źródło: [[Notatka]] · oznaczył: Karol %s" % DZIS)
        self.zapisz_pliki(decyzje=tz.wstaw_po(tekst, "### D-002 Propozycja z linkiem", [self.STARY]))
        sejf.uniewaznij()

    def decyzja(self, ident):
        return {d["id"]: d for d in sejf.plan()["decyzje"]}[ident]

    def test_parser_wykrywa_i_nic_nie_czeka(self):
        d = self.decyzja("D-002")
        self.assertEqual((d["status"], d["sprzeczny_status"]), ("zatwierdzona", "nieaktualna"))
        self.assertEqual(d["zdecydowal"]["kto"], "Paweł")
        self.assertIsNone(d["czeka_na"])                                    # bez tego czekałaby na Karola
        self.assertIsNone(self.decyzja("D-003")["sprzeczny_status"])          # zwykłe decyzje bez zmian

    def test_zapis_odmawia_bez_zmian(self):
        przed = {k: self.bajty(k) for k in tz.PLIKI}
        for status in ("nieaktualna", "do_decyzji", "odrzucona"):
            e = self.assertBlad(409, zapis.zmien_status_decyzji, "D-002", status, None, self.wersja("decyzje"), "Karol")
            self.assertEqual(e.dodatkowe.get("kod"), "sprzeczny_status")
            self.assertIn("dwa wiersze statusu", e.komunikat)
        for odp in ("zgoda", "sprzeciw"):
            e = self.assertBlad(409, zapis.potwierdz_decyzje, "D-002", odp, None, self.wersja("decyzje"), "Karol")
            self.assertEqual(e.dodatkowe.get("kod"), "sprzeczny_status")
        self.assertEqual({k: self.bajty(k) for k in tz.PLIKI}, przed)
        # po ręcznej poprawce w Obsidianie (jeden wiersz) wszystko działa jak zwykle
        tekst = self.bajty("decyzje").decode("utf-8-sig").replace("\r\n", "\n").replace(self.STARY + "\n", "")
        self.zapisz_pliki(decyzje=tekst)
        sejf.uniewaznij()
        self.assertIsNone(self.decyzja("D-002")["sprzeczny_status"])
        zapis.zmien_status_decyzji("D-002", "do_decyzji", None, self.wersja("decyzje"), "Karol")
        self.assertEqual(self.decyzja("D-002")["status"], "do_decyzji")

    def test_zwykly_opis_to_nie_drugi_status(self):
        for linia in ("Propozycja: zielony dach.", "- zatwierdzona wcześniej wersja", "Odrzucona opcja B.", "**Do decyzji** potem"):
            self.assertIsNone(sejf.drugi_status(["", linia]), linia)
        self.assertEqual(sejf.drugi_status(["", "❌ odrzucona · x"]), "odrzucona")
        self.assertIsNone(sejf.drugi_status([]))


class TestSprzecznyStatusCRLF(TestSprzecznyStatus):
    nl = "\r\n"


# =========================================================================== Telegram (atrapa API)
class TestTelegramBezAlertu(tt.Baza):
    def test_nieaktualna_bez_alertu(self):
        w = self.zatwierdz_w_panelu("D-006", status="nieaktualna")
        self.assertTrue(w["ok"])
        self.assertEqual(self.atrapa.zadania("sendMessage"), [])
        d = {x["id"]: x for x in sejf.plan()["decyzje"]}["D-006"]
        self.assertEqual((d["status"], d["czeka_na"]), ("nieaktualna", None))
        self.assertFalse((self.stan().get("alerty") or {}).get("D-006"))
        # dla porównania: zwykłe zatwierdzenie innej decyzji dalej wysyła alert
        self.zapisz_pliki(decyzje=self.bajty("decyzje").decode("utf-8-sig").replace(
            "---\n*Stopka", "### D-007 Inna\n💡 propozycja · test\nOpis.\n\n---\n*Stopka"))
        sejf.uniewaznij()
        self.zatwierdz_w_panelu("D-007")
        self.assertEqual(len(self.atrapa.zadania("sendMessage")), 1)


# =========================================================================== raporty
class TestRaportNieaktualny(unittest.TestCase):
    def setUp(self):
        self.stare_dane = rdzen.DANE
        self.stary_log = rdzen.log
        rdzen.log = lambda *czesci: None
        self.tmp = tempfile.mkdtemp(prefix="bc_test_nieaktualne_")
        rdzen.DANE = os.path.join(self.tmp, "dane")

    def tearDown(self):
        rdzen.DANE = self.stare_dane
        rdzen.log = self.stary_log
        raporty._raporty_kat.uniewaznij()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_trzecia_wartosc_i_zmiana_decyzji(self):
        r = raporty.dodaj_raport("Stary most", "Opis.", kto="Claude (test)")
        inny = raporty.dodaj_raport("Nowy most", "Opis.", kto="Claude (test)")
        self.assertEqual(r["status"], "czeka")
        r2 = raporty.zapisz_decyzje(r["id"], "nieaktualne", "Karol", "Zastąpiony nowym mostem")
        self.assertEqual(r2["status"], "nieaktualne")
        self.assertEqual((r2["decyzja"]["wartosc"], r2["decyzja"]["komentarz"], r2["decyzja"]["kto"]),
                         ("nieaktualne", "Zastąpiony nowym mostem", "Karol"))
        with open(os.path.join(rdzen.DANE, "raporty", r["id"] + ".decyzja.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["wartosc"], "nieaktualne")
        lista = {x["id"]: x["status"] for x in raporty.lista_raportow()}
        self.assertEqual(lista, {r["id"]: "nieaktualne", inny["id"]: "czeka"})
        self.assertEqual(raporty.zdrowie()["czeka"], 1)                   # nie liczy się do czekających
        r3 = raporty.zapisz_decyzje(r["id"], "zaakceptowane", "Paweł")      # „Zmień decyzję”
        self.assertEqual(r3["status"], "zaakceptowane")
        r4 = raporty.zapisz_decyzje(r["id"], "nieaktualne", "Paweł")        # i z powrotem, bez komentarza
        self.assertEqual((r4["status"], r4["decyzja"]["komentarz"]), ("nieaktualne", ""))
        with self.assertRaises(rdzen.BladHTTP):
            raporty.zapisz_decyzje(r["id"], "nieaktualny", "Paweł")         # tylko dokładna wartość

    def test_narzedzie_raport(self):
        r = raporty.dodaj_raport("Raport z CLI", "Opis.", kto="Claude (test)")
        raporty.zapisz_decyzje(r["id"], "nieaktualne", "Karol", "Po sesji")
        env = dict(os.environ, BC_PANEL_DANE=rdzen.DANE, BC_PANEL_RUNTIME=os.path.join(self.tmp, "runtime"),
                   PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        cli = os.path.join(PANEL, "narzedzia", "raport.py")

        def uruchom(*argv):
            p = subprocess.run([sys.executable, "-B", cli] + list(argv), capture_output=True, env=env, timeout=60,
                               creationflags=0x08000000 if os.name == "nt" else 0)
            return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")

        kod, out, err = uruchom("lista")
        self.assertEqual(kod, 0, err)
        self.assertIn("NIEAKTUALNE", out)
        self.assertIn("Raport z CLI", out)
        kod, out, err = uruchom("lista", "--czeka")
        self.assertEqual((kod, out.strip()), (0, "Brak raportów."), err)
        kod, out, err = uruchom("odpowiedzi")
        self.assertEqual(kod, 0, err)
        self.assertIn("Karol: NIEAKTUALNE — raport %s „Raport z CLI”" % r["id"], out)
        self.assertIn("Po sesji", out)
        kod, out, _ = uruchom("odpowiedzi", "--json")
        self.assertEqual(json.loads(out)["odpowiedzi"][0]["wartosc"], "nieaktualne")


# =========================================================================== API (prawdziwy serwer na kopii sejfu)
class TestNieaktualneAPI(test_api.TestZapisSejfuAPI):
    """Serwer testowy z kopią sejfu (rozruch z TestZapisSejfuAPI, bez jego testów — te biegną w test_api.py)."""

    def test_trasy(self):
        plan = self.plan()
        self.assertTrue(plan["funkcje"]["nieaktualne"])
        self.assertIn("nieaktualne", {p["nr"]: p for p in plan["pytania"]}[2])
        # pytanie: zwykła trasa odpowiedzi (gość też może)
        s, o, _ = self.post("/api/sejf/pytania/2/odpowiedz", {"tekst": "nieaktualne — po sesji",
                                                               "wersja": plan["wersje"]["pytania"]}, zdalny=True, kto="Paweł")
        self.assertEqual(s, 200, o)
        self.assertTrue({p["nr"]: p for p in o["plan"]["pytania"]}[2]["nieaktualne"])
        self.assertIn("- Paweł (gość panelu, ", self.plik("Pytania otwarte.md"))
        # decyzja: gość nie, decydent tak
        cialo = {"status": "nieaktualna", "uzasadnienie": "stare", "wersja": o["plan"]["wersje"]["decyzje"]}
        s, o2, _ = self.post("/api/sejf/decyzje/D-005/status", cialo, zdalny=True, kto="Paweł")
        self.assertEqual((s, o2.get("kod")), (403, "brak_klucza_zatwierdzania"), o2)
        s, o2, _ = self.post("/api/sejf/decyzje/D-005/status", cialo, kto="Karol")
        self.assertEqual(s, 200, o2)
        self.assertEqual(o2["rozstrzygniete"], [])
        d = {x["id"]: x for x in o2["plan"]["decyzje"]}["D-005"]
        self.assertEqual((d["status"], d["czeka_na"]), ("nieaktualna", None))
        self.assertIn("\n" + E + " nieaktualna · narzędzia · oznaczył: Karol ", self.plik("Rejestr decyzji.md"))
        # stara wersja = 409, nic nie zapisane
        s, o3, _ = self.post("/api/sejf/decyzje/D-003/status", cialo, kto="Karol")
        self.assertEqual((s, o3.get("kod")), (409, "konflikt_wersji"), o3)
        # „Przywróć”: z powrotem na „do decyzji”
        s, o4, _ = self.post("/api/sejf/decyzje/D-005/status", {"status": "do_decyzji", "wersja": o2["wersja"]}, kto="Karol")
        self.assertEqual(s, 200, o4)
        self.assertEqual({x["id"]: x for x in o4["plan"]["decyzje"]}["D-005"]["status"], "do_decyzji")
        # raport: trzecia wartość decyzji
        s, r, _ = self.post("/api/raporty", {"tytul": "Raport testowy", "opis_md": "x"}, kto="Claude (test)")
        self.assertEqual(s, 201, r)
        s, r2, _ = self.post("/api/raporty/%s/decyzja" % r["id"], {"wartosc": "nieaktualne", "komentarz": "stary"}, zdalny=True)
        self.assertEqual((s, r2["status"]), (200, "nieaktualne"), r2)
        s, lista, _ = self.get("/api/raporty")
        self.assertEqual(lista["czeka"], 0)


for _nazwa in [n for n in dir(test_api.TestZapisSejfuAPI) if n.startswith("test_")]:
    setattr(TestNieaktualneAPI, _nazwa, None)


if __name__ == "__main__":
    unittest.main()
