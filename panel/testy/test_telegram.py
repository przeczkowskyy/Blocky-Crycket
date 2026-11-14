# -*- coding: utf-8 -*-
"""Bot Telegram (bc/telegram.py) na ATRAPIE API (testy/atrapa_telegrama.py) i kopii sejfu — bez prawdziwego Telegrama.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_telegram
Bot działa tu synchronicznie (bez wątków), z jawnym adresem atrapy (`Bot(api=…)`); ustawienia bota i stan (offset,
alerty, zaległe) leżą w katalogu tymczasowym. Token jest zmyślony.
"""
import json
import os
import re
import sys
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from testy import test_potwierdzenia as tp  # noqa: E402
from testy import test_zapis as tz  # noqa: E402
from testy.atrapa_telegrama import AtrapaTelegrama, klikniecie, wiadomosc  # noqa: E402
from bc import rdzen, sejf, telegram, zapis  # noqa: E402

TOKEN = "123456:TEST-zmyslony-token-atrapy-xyz"
GRUPA = -1001
KAROL, PAWEL, OBCY = 111, 222, 333
USTAWIENIA = {"token": TOKEN, "bot": "bc_test_bot", "osoby": {str(KAROL): "Karol", str(PAWEL): "Paweł"},
              "grupy": {str(GRUPA): "B&C decyzje"}}
RX_DANE = re.compile(r"^p:D-\d{1,4}:[znr]:[0-9a-f]{8}$")


class Baza(tp.Baza):
    @classmethod
    def setUpClass(cls):
        cls.atrapa = AtrapaTelegrama(TOKEN).start()

    @classmethod
    def tearDownClass(cls):
        cls.atrapa.stop()

    def setUp(self):
        super().setUp()
        self.logi = []
        self.latki_tg = [
            mock.patch.object(telegram, "_plik_ustawien", lambda: os.path.join(self.tmp, "telegram.json")),
            mock.patch.object(telegram, "_plik_stanu", lambda: os.path.join(self.tmp, "telegram_stan.json")),
            mock.patch.object(rdzen, "log", lambda *a: self.logi.append(" ".join(str(x) for x in a))),
        ]
        for l in self.latki_tg:
            l.start()
        self.ustaw(USTAWIENIA)
        self.atrapa.wyczysc()
        self.atrapa.awaria.clear()
        with self.atrapa.cond:
            self.atrapa.aktualizacje.clear()
            self.atrapa.nastepna_wiadomosc = 500               # pierwsza wysłana wiadomość w teście ma numer 501
        self.bot = telegram.Bot(api=self.atrapa.adres, synchronicznie=True)
        zapis.dodaj_sluchacza(self.bot.zdarzenie)

    def tearDown(self):
        zapis.usun_sluchacza(self.bot.zdarzenie)
        for l in reversed(self.latki_tg):
            l.stop()
        telegram._ust_pamiec.update(stan=None, dane=None)
        super().tearDown()
        for linia in self.logi:                                # token nigdy w logu
            self.assertNotIn(TOKEN, linia)
            self.assertNotIn(TOKEN.split(":")[1], linia)

    def ustaw(self, dane):
        p = os.path.join(self.tmp, "telegram.json")
        if dane is None:
            if os.path.exists(p):
                os.remove(p)
        else:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(dane, f, ensure_ascii=False)
        telegram._ust_pamiec.update(stan=None, dane=None)
        sejf.uniewaznij()

    def stan(self):
        return rdzen.czytaj_json(os.path.join(self.tmp, "telegram_stan.json"), {}) or {}

    def zatwierdz_w_panelu(self, ident="D-006", status="zatwierdzona", kto="Karol", uz=None):
        cialo = {"status": status, "wersja": self.wersja("decyzje")}
        if uz:
            cialo["uzasadnienie"] = uz
        return zapis._t_status(tz._zadanie(cialo, lokalny=True, kto=kto, params={"id": ident}))

    def alert(self, ident="D-006"):
        """Zatwierdzenie w panelu (Karol) → ostatni alert: (pola sendMessage, dane przycisków)."""
        self.zatwierdz_w_panelu(ident)
        w = self.atrapa.zadania("sendMessage")[-1]
        dane = [b["callback_data"] for rzad in w["reply_markup"]["inline_keyboard"] for b in rzad]
        return w, dane

    def klik(self, dane, od=PAWEL, czat=GRUPA, nr=77, tekst="Pytanie"):
        self.bot.przetworz(klikniecie(czat, od, dane, wiadomosc_nr=nr, tekst=tekst), telegram.ustawienia())
        odp = self.atrapa.zadania("answerCallbackQuery")
        return odp[-1] if odp else None

    def napisz(self, tekst, od=PAWEL, czat=GRUPA, **kw):
        self.bot.przetworz(wiadomosc(czat, od, tekst, **kw), telegram.ustawienia())

    def wyslane(self):
        return [p["text"] for p in self.atrapa.zadania("sendMessage")]


class TestAlert(Baza):
    def test_tresc_i_przyciski(self):
        self.zapisz_pliki(decyzje=tp.REJESTR.replace("### D-006 Propozycja", "### D-006 Propozycja <b>&</b>"))
        sejf.uniewaznij()
        w, dane = self.alert()
        self.assertEqual(w["chat_id"], GRUPA)
        self.assertEqual(w["parse_mode"], "HTML")
        self.assertIn("Karol zatwierdził decyzję D-006", w["text"])
        self.assertIn("„Propozycja &lt;b&gt;&amp;&lt;/b&gt;”", w["text"])            # treść z sejfu escapowana
        self.assertIn('<a href="tg://user?id=%d">Paweł</a>, zgadzasz się?' % PAWEL, w["text"])
        self.assertIn("robocze ustalenie", w["text"])
        napisy = [b["text"] for rzad in w["reply_markup"]["inline_keyboard"] for b in rzad]
        self.assertEqual(napisy, ["✅ Zgoda", "❌ Brak zgody", "💬 Przedyskutuj"])
        for d in dane:
            self.assertRegex(d, RX_DANE)
            self.assertLessEqual(len(d.encode("utf-8")), 64)
        self.assertEqual([d.split(":")[2] for d in dane], ["z", "n", "r"])
        self.assertEqual(len(self.stan()["alerty"]["D-006"]), 1)

    def test_uzasadnienie_w_alercie_i_odrzucenie(self):
        self.zatwierdz_w_panelu("D-006", status="odrzucona", uz="Za wcześnie")
        t = self.wyslane()[-1]
        self.assertIn("Karol odrzucił decyzję D-006", t)
        self.assertIn("Uzasadnienie: Za wcześnie", t)

    def test_do_decyzji_bez_alertu_i_wylaczony_bot(self):
        self.zatwierdz_w_panelu("D-006", status="do_decyzji")
        self.assertEqual(self.atrapa.zadania("sendMessage"), [])
        self.ustaw(None)                                       # brak pliku = Telegram wyłączony, panel działa
        self.assertFalse(telegram.ustawienia()["wlaczony"])
        self.zatwierdz_w_panelu("D-006")
        self.assertEqual(self.atrapa.zadania(), [])
        self.assertEqual(self.decyzja("D-006")["czeka_na"], "Paweł")

    def test_bez_grupy_prywatnie_do_osoby(self):
        self.ustaw(dict(USTAWIENIA, grupy={}))
        self.alert()
        self.assertEqual(self.atrapa.zadania("sendMessage")[-1]["chat_id"], PAWEL)

    def test_blad_sieci_nie_psuje_zapisu(self):
        for awaria in ("siec", "500"):
            self.atrapa.awaria["sendMessage"] = awaria
            w = self.zatwierdz_w_panelu("D-006")
            self.assertTrue(w["ok"])
            self.assertIn("zdecydował: Karol %s" % tp.DZIS, self.tekst("decyzje"))
            self.assertEqual(self.stan().get("zalegle"), ["D-006"])
            self.assertTrue(self.bot.ostatni_blad and self.bot.ostatni_blad["tekst"])
            self.assertNotIn(TOKEN, json.dumps(self.bot.stan(), ensure_ascii=False))
            # sieć wróciła: zaległy alert idzie (tak samo przy /czeka)
            del self.atrapa.awaria["sendMessage"]
            self.atrapa.wyczysc()
            self.bot.ponow_zalegle()
            self.assertEqual(len(self.atrapa.zadania("sendMessage")), 1)
            self.assertEqual(self.stan().get("zalegle"), [])
            # z powrotem „do decyzji”, żeby druga runda zaczęła od zera
            self.zapisz_pliki(decyzje=tp.REJESTR)
            sejf.uniewaznij()

    def test_zly_czat_bez_ponawiania(self):
        """Telegram odrzuca wiadomość (4xx, np. zły numer grupy): raz próba zwykłym tekstem, potem bez ponawiania."""
        self.atrapa.awaria["sendMessage"] = "400"
        w = self.zatwierdz_w_panelu("D-006")
        self.assertTrue(w["ok"])
        wyslane = self.atrapa.zadania("sendMessage")
        self.assertEqual([p.get("parse_mode") for p in wyslane], ["HTML", None])     # druga próba bez HTML
        self.assertEqual(self.stan().get("zalegle") or [], [])
        self.assertIn("400", self.bot.ostatni_blad["tekst"])

    def test_zly_token_bez_tokenu_w_bledzie(self):
        self.ustaw(dict(USTAWIENIA, token="654321:TEST-inny-zmyslony-token-atrapy"))
        with self.assertRaises(telegram.BladTelegrama) as k:
            self.bot._wyslij(GRUPA, "x")
        self.assertIn("401", k.exception.komunikat)
        self.assertNotIn("654321", k.exception.komunikat)
        self.assertNotIn("TEST-inny", str(k.exception))

    def test_adres_api_tylko_w_trybie_testowym(self):
        with mock.patch.dict(os.environ, {telegram.ZMIENNA_ADRESU_TESTOWEGO: "http://127.0.0.1:1"}):
            os.environ.pop(telegram.ZMIENNA_TRYBU_TESTOWEGO, None)
            self.assertEqual(telegram.adres_api(), telegram.API_TELEGRAMA)
            with mock.patch.dict(os.environ, {telegram.ZMIENNA_TRYBU_TESTOWEGO: "1"}):
                self.assertEqual(telegram.adres_api(), "http://127.0.0.1:1")
        self.assertEqual(telegram.adres_api("http://x:2/"), "http://x:2")
        self.assertEqual(telegram.API_TELEGRAMA, "https://api.telegram.org")

    def test_zle_ustawienia(self):
        self.ustaw({"token": "zly token", "osoby": {"abc": "X", str(PAWEL): "Paweł"}, "grupy": {"5": "dodatnia"}})
        u = telegram.ustawienia()
        self.assertFalse(u["wlaczony"])
        self.assertTrue(u["blad"])
        self.assertEqual((u["osoby"], u["grupy"]), ({PAWEL: "Paweł"}, {}))


class TestKlikniecia(Baza):
    def test_zgoda(self):
        w, dane = self.alert()
        mid = self.stan()["alerty"]["D-006"][0]["wiadomosc"]
        self.assertEqual(mid, 501)                                                   # message_id nadany przez atrapę
        odp = self.klik(dane[0], nr=mid, tekst="Karol zatwierdził decyzję D-006")
        self.assertIn("Zapisano: zgoda", odp["text"])
        self.assertIn("potwierdził: Paweł %s" % tp.DZIS, self.tekst("decyzje"))
        self.assertIn("- Paweł (Telegram): decyzja D-006 potwierdzona: zgoda (zatwierdzona przez Karol %s), przez "
                      "Telegram ([[Rejestr decyzji]])" % tp.DZIS, self.tekst("dziennik"))
        zmiany = self.atrapa.zadania("editMessageText")
        self.assertEqual([(z["chat_id"], z["message_id"]) for z in zmiany], [(GRUPA, mid)])
        self.assertNotIn("reply_markup", zmiany[0])                                  # przyciski znikają
        self.assertIn("Paweł: zgoda (przez Telegram)", zmiany[0]["text"])
        self.assertNotIn("D-006", self.stan().get("alerty") or {})

    def test_podwojne_klikniecie(self):
        _, dane = self.alert()
        self.klik(dane[0])
        odp = self.klik(dane[0])
        self.assertIn("dwa podpisy", odp["text"])
        self.assertEqual(sum(m.startswith("potwierdził") for m in self.decyzja("D-006")["meta"]), 1)
        self.assertEqual(self.tekst("decyzje").count("potwierdził: Paweł"), 2)          # D-005 i raz D-006

    def test_wlasna_decyzja(self):
        _, dane = self.alert()
        przed = self.bajty("decyzje")
        odp = self.klik(dane[0], od=KAROL)
        self.assertIn("To Twoja decyzja", odp["text"])
        self.assertTrue(odp["show_alert"])
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_nieznany_uzytkownik(self):
        _, dane = self.alert()
        przed = self.bajty("decyzje")
        odp = self.klik(dane[0], od=OBCY)
        self.assertIn("Nie znam Cię", odp["text"])
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_czat_spoza_listy(self):
        _, dane = self.alert()
        przed = self.bajty("decyzje")
        self.atrapa.wyczysc()
        self.klik(dane[0], czat=-999)                          # obca grupa
        self.klik(dane[0], od=OBCY, czat=OBCY)                 # rozmowa prywatna kogoś spoza listy
        self.napisz("/start", od=OBCY, czat=OBCY, prywatna=True)
        self.napisz("/czeka", czat=-999)
        self.assertEqual(self.atrapa.zadania(), [])            # bot nic nie odpowiada
        self.assertEqual(self.bajty("decyzje"), przed)
        self.bot.przetworz(klikniecie(PAWEL, PAWEL, dane[0], prywatna=True), telegram.ustawienia())   # prywatnie: tak
        self.assertIn("potwierdził: Paweł", self.tekst("decyzje"))

    def test_zle_dane_przycisku(self):
        self.alert()
        przed = self.bajty("decyzje")
        for dane in ("p:D-006:x:12345678", "p:../../etc:z:12345678", "p:D-006:z:1234", "zz", "", "c:abc"):
            odp = self.klik(dane)
            self.assertIn("Nie znam tego przycisku", odp["text"], dane)
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_decyzja_zmieniona_w_miedzyczasie(self):
        _, dane = self.alert("D-006")
        # ktoś ponownie podjął decyzję innego dnia (np. po sprzeciwie): stary przycisk jest nieaktualny
        tekst = self.tekst("decyzje").replace("zdecydował: Karol %s" % tp.DZIS, "zdecydował: Karol 2026-11-14")
        self.zapisz_pliki(decyzje=tekst)
        sejf.uniewaznij()
        przed = self.bajty("decyzje")
        odp = self.klik(dane[0], nr=self.stan()["alerty"]["D-006"][0]["wiadomosc"])
        self.assertIn("zmieniła się", odp["text"])
        self.assertEqual(self.bajty("decyzje"), przed)
        zmiany = self.atrapa.zadania("editMessageText")
        self.assertTrue(zmiany and "Już nieaktualne" in zmiany[-1]["text"])

    def test_sprzeciw_z_powodem(self):
        _, dane = self.alert()
        odp = self.klik(dane[1])
        self.assertIn("brak zgody", odp["text"])
        self.assertIn("🕓 do decyzji · narzędzia · sprzeciw: Paweł %s (wobec: zatwierdzona przez Karol %s)"
                      % (tp.DZIS, tp.DZIS), self.tekst("decyzje"))
        prosba = self.atrapa.zadania("sendMessage")[-1]
        self.assertIn("dlaczego nie", prosba["text"])
        self.assertEqual(prosba["reply_markup"], {"force_reply": True, "selective": True})
        nr_prosby = 500 + len(self.atrapa.zadania("sendMessage"))
        self.napisz("Za drogie na teraz", odpowiedz_na=nr_prosby)
        self.assertIn("\nUzasadnienie sprzeciwu — Paweł, %s: Za drogie na teraz\n" % tp.DZIS, self.tekst("decyzje"))
        self.assertIn("Zapisałem powód przy D-006", self.wyslane()[-1])
        self.assertIn("decyzja D-006: powód braku zgody, przez Telegram", self.tekst("dziennik"))

    def test_sprzeciw_bez_powodu_i_po_czasie(self):
        _, dane = self.alert()
        self.klik(dane[1])
        nr_prosby = 500 + len(self.atrapa.zadania("sendMessage"))
        self.napisz("Zwykła rozmowa w grupie")                 # nie odpowiedź na prośbę — pomijana
        self.assertNotIn("Uzasadnienie sprzeciwu", self.tekst("decyzje"))
        for v in self.bot._powody.values():                    # po 15 minutach powód nie trafia do Rejestru
            v["do"] = 0
        self.napisz("Spóźniony powód", odpowiedz_na=nr_prosby)
        self.assertNotIn("Uzasadnienie sprzeciwu", self.tekst("decyzje"))
        self.assertIn("sprzeciw: Paweł", self.tekst("decyzje"))

    def test_przedyskutuj(self):
        _, dane = self.alert()
        odp = self.klik(dane[2])
        self.assertIn("agendzie", odp["text"])
        self.assertIn("do rozmowy: Paweł %s" % tp.DZIS, self.tekst("decyzje"))
        self.assertIn("- [ ] Propozycja (D-006) — Paweł prosi o rozmowę", self.agenda())
        self.assertIn("dodał: Paweł (Telegram) %s" % tp.DZIS, self.agenda())

    def test_przedyskutuj_agenda_nie_zapisana(self):
        """Rejestr ma „do rozmowy”, ale agenda się nie zapisała: bot mówi to wprost, a nie „jest na agendzie”."""
        from bc import sesje
        from bc.rdzen import BladHTTP
        for awaria in (BladHTTP(500, "Nie udało się zapisać pliku"), OSError("plik zablokowany")):
            self.zapisz_pliki(decyzje=tp.REJESTR)
            sejf.uniewaznij()
            _, dane = self.alert()
            with mock.patch.object(sesje, "dodaj_temat", side_effect=awaria):
                odp = self.klik(dane[2])
            self.assertIn("tematu nie dopisałem do agendy", odp["text"])
            self.assertIn("Na sesję główną", odp["text"])
            self.assertNotIn("jest na agendzie", odp["text"])
            self.assertTrue(odp["show_alert"])
            self.assertIn("do rozmowy: Paweł %s" % tp.DZIS, self.tekst("decyzje"))
            p = os.path.join(self.sejf, "Produkcja", "Sesje główne.md")
            self.assertFalse(os.path.exists(p) and "(D-006)" in self.agenda())

    def test_potwierdzenie_w_panelu_zamyka_alert(self):
        self.alert()
        mid = self.stan()["alerty"]["D-006"][0]["wiadomosc"]
        zapis._t_potwierdzenie(tz._zadanie({"odpowiedz": "zgoda", "wersja": self.wersja("decyzje")}, gd=True,
                                           kto="Paweł", params={"id": "D-006"}))
        zmiany = self.atrapa.zadania("editMessageText")
        self.assertEqual(zmiany[-1]["message_id"], mid)
        self.assertIn("Paweł: zgoda (w panelu)", zmiany[-1]["text"])


class TestKomendyIOdbior(Baza):
    def dopisz_decyzje(self, ile):
        bloki = "".join("### D-%03d Decyzja numer %d\n✅ zatwierdzona · test · zdecydował: Karol %s\nOpis.\n\n"
                        % (100 + i, i, tp.DZIS) for i in range(ile))
        self.zapisz_pliki(decyzje=tp.REJESTR.replace("---\n*Stopka rejestru.*", bloki + "---\n*Stopka rejestru.*"))
        sejf.uniewaznij()

    def test_czeka_z_paginacja(self):
        self.dopisz_decyzje(6)                                 # + D-002 = 7 czeka na Pawła
        self.napisz("/czeka@bc_test_bot")
        t = self.wyslane()
        self.assertEqual(t[0], "Paweł, na Twoje potwierdzenie czeka: 7.")
        pytania = self.atrapa.zadania("sendMessage")[1:6]
        self.assertTrue(all("inline_keyboard" in p["reply_markup"] for p in pytania))
        self.assertIn("D-002", pytania[0]["text"])
        ostatnia = self.atrapa.zadania("sendMessage")[-1]
        self.assertEqual(len(self.atrapa.zadania("sendMessage")), 7)
        self.assertEqual(ostatnia["text"], "Czeka jeszcze: 2.")
        nastepne = ostatnia["reply_markup"]["inline_keyboard"][0][0]
        self.assertEqual((nastepne["text"], nastepne["callback_data"]), ("Następne ▶", "c:5"))
        self.atrapa.wyczysc()
        self.klik("c:5", nr=507, tekst="Czeka jeszcze: 2.")
        nowe = self.atrapa.zadania("sendMessage")
        self.assertEqual(len(nowe), 2)
        self.assertTrue(all("inline_keyboard" in p["reply_markup"] for p in nowe))
        self.assertNotIn("Następne", json.dumps(nowe, ensure_ascii=False))
        # Karol: czeka tylko decyzja Pawła (D-003)
        self.atrapa.wyczysc()
        self.napisz("/czeka", od=KAROL)
        self.assertEqual(len(self.atrapa.zadania("sendMessage")), 2)
        self.assertIn("D-003", self.wyslane()[1])

    def test_czeka_pusto_i_inne_komendy(self):
        tp.zapis.potwierdz_decyzje("D-003", "zgoda", None, None, "Karol")
        self.napisz("/czeka", od=KAROL)
        self.assertEqual(self.wyslane()[-1], "Nic nie czeka na Twoje potwierdzenie. ✅")
        self.napisz("/start")
        self.assertIn("Cześć, Paweł! Znam Cię", self.wyslane()[-1])
        self.napisz("/start", od=OBCY)
        self.assertIn("Nie znam Cię jeszcze", self.wyslane()[-1])
        self.assertIn(str(OBCY), self.wyslane()[-1])
        self.napisz("/pomoc")
        self.assertIn("/czeka", self.wyslane()[-1])
        n = len(self.wyslane())
        self.napisz("/czeka@inny_bot")                         # komenda do innego bota w grupie
        self.napisz("/nieznana")
        self.assertEqual(len(self.wyslane()), n)
        self.napisz("/start", czat=PAWEL, prywatna=True)       # prywatnie, osoba z listy
        self.assertIn("Znam Cię", self.wyslane()[-1])

    def test_czeka_ponawia_zalegle(self):
        self.atrapa.awaria["sendMessage"] = "siec"
        self.zatwierdz_w_panelu("D-006")
        self.assertEqual(self.stan().get("zalegle"), ["D-006"])
        del self.atrapa.awaria["sendMessage"]
        self.atrapa.wyczysc()
        self.napisz("/czeka")
        self.assertEqual(self.stan().get("zalegle"), [])
        self.assertIn("Karol zatwierdził decyzję D-006", self.wyslane()[0])   # zaległy alert do grupy

    def test_offset_po_restarcie(self):
        self.atrapa.dodaj_aktualizacje(wiadomosc(GRUPA, PAWEL, "/pomoc"))
        ostatni = self.atrapa.dodaj_aktualizacje(wiadomosc(GRUPA, PAWEL, "/start"))
        self.assertEqual(self.bot.odbierz_raz(czas=0), 2)
        self.assertEqual(self.stan()["offset"], ostatni + 1)
        self.assertEqual(len(self.wyslane()), 2)
        nowy = telegram.Bot(api=self.atrapa.adres, synchronicznie=True)                # „restart” panelu
        self.assertEqual(nowy.odbierz_raz(czas=0), 0)
        self.assertEqual(self.atrapa.zadania("getUpdates")[-1]["offset"], ostatni + 1)
        self.assertEqual(len(self.wyslane()), 2)                                      # nic drugi raz
        self.assertEqual(self.atrapa.zadania("getUpdates")[-1]["allowed_updates"], ["message", "callback_query"])

    def test_offset_w_pamieci_gdy_zapis_stanu_pada(self):
        """Zapis pliku stanu się nie udaje (pełny dysk, plik zablokowany): bot nie przetwarza w kółko tych samych
        aktualizacji — offset jest też w pamięci, plik to tylko zapas na restart."""
        self.atrapa.dodaj_aktualizacje(wiadomosc(GRUPA, PAWEL, "/pomoc"))
        with mock.patch.object(rdzen, "zapisz_json", side_effect=OSError("dysk pełny")):
            self.assertEqual(self.bot.odbierz_raz(czas=0), 1)
            self.assertEqual(self.bot.odbierz_raz(czas=0), 0)
            self.assertEqual(self.bot.odbierz_raz(czas=0), 0)
        self.assertEqual(len(self.wyslane()), 1)                                      # /pomoc raz, nie trzy razy
        offsety = [z.get("offset") for z in self.atrapa.zadania("getUpdates")]
        self.assertIsNone(offsety[0])
        self.assertEqual(len(set(offsety[1:])), 1)
        self.assertIsNotNone(offsety[1])
        self.assertNotIn("offset", self.stan())                                       # plik faktycznie nie zapisany
        self.assertTrue(any("nie udało się zapisać stanu" in l for l in self.logi))
        # plik ma wyższy offset niż pamięć (np. zapisał go inny proces) — bierzemy wyższy
        ostatni = self.atrapa.dodaj_aktualizacje(wiadomosc(GRUPA, PAWEL, "/start"))
        rdzen.zapisz_json(os.path.join(self.tmp, "telegram_stan.json"), {"offset": ostatni + 1})
        self.assertEqual(self.bot.odbierz_raz(czas=0), 0)
        self.assertEqual(self.atrapa.zadania("getUpdates")[-1]["offset"], ostatni + 1)
        self.assertEqual(len(self.wyslane()), 1)

    def test_stan_bez_tokenu_i_identyfikatorow(self):
        s = self.bot.stan()
        self.assertEqual((s["wlaczony"], s["bot"], s["osoby"], s["grupy"]), (True, "bc_test_bot", 2, 1))
        tekst = json.dumps(s, ensure_ascii=False)
        for zakazane in (TOKEN, str(KAROL), str(PAWEL), str(GRUPA)):
            self.assertNotIn(zakazane, tekst)
        with self.assertRaises(Exception):
            telegram._t_stan(tz._zadanie({}, lokalny=False))
        self.assertEqual(telegram._t_stan(tz._zadanie({}, lokalny=True))["osoby"], 2)

    def test_zespol_z_ustawien_bota(self):
        self.ustaw(dict(USTAWIENIA, osoby={str(KAROL): "Karol", str(PAWEL): "Paweł", "444": "Ola"}))
        self.assertEqual(sejf.zespol(), ["Karol", "Paweł", "Ola"])
        self.ustaw(None)
        self.assertEqual(sejf.zespol(), ["Karol", "Paweł"])


if __name__ == "__main__":
    unittest.main()
