# -*- coding: utf-8 -*-
"""Potwierdzanie decyzji i bot Telegram na prawdziwym serwerze panelu (osobny proces) i ATRAPIE API Telegrama.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_telegram_api
Serwer testowy jak w test_api.py (katalogi tymczasowe, tymczasowy sejf, tymczasowe klucze), z plikiem telegram.json
w tymczasowych danych lokalnych (zmyślony token) i zmiennymi trybu testowego, które kierują bota na atrapę
(testy/atrapa_telegrama.py). Sprawdza: trasę POST /api/sejf/decyzje/<id>/potwierdzenie (gość, osoba przy
komputerze, klucz zatwierdzania, brak imienia, własna decyzja), alert po decyzji w panelu, kliknięcie odebrane przez
wątek odbioru (offset w danych lokalnych), błąd sieci przy wysyłce, GET /api/telegram/stan i brak tokenu w logach
i odpowiedziach.
"""
import datetime
import json
import os
import time
import unittest

from testy import test_api, test_zapis, test_potwierdzenia
from testy.atrapa_telegrama import AtrapaTelegrama, klikniecie, wiadomosc

TOKEN = "123456:TEST-zmyslony-token-atrapy-xyz"
GRUPA, KAROL, PAWEL = -1001, 111, 222
DODATKOWE = ("### D-007 Decyzja do próby sieci\n💡 propozycja · test\nOpis.\n\n"
             "### D-008 Decyzja do kliknięcia\n💡 propozycja · test\nOpis.\n\n")


def dzis():
    return datetime.date.today().isoformat()


class TestTelegramAPI(test_api.SerwerTestowy):
    klucz_gd = "klucz-zatwierdzania-testowy-telegram-0123456789"

    @classmethod
    def setUpClass(cls):
        cls.atrapa = AtrapaTelegrama(TOKEN).start()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.atrapa.stop()

    @classmethod
    def konfiguracja_lokalna(cls):
        cls.sejf = os.path.join(cls.tmp, "sejf")
        return {"gra": {"universeId": None}, "sejfy": [{"id": "B&C", "nazwa": "Sejf testowy", "sciezka": cls.sejf}]}

    @classmethod
    def przygotuj(cls, runtime):
        os.makedirs(os.path.join(cls.sejf, "Produkcja"))
        pliki = dict(test_zapis.PLIKI)
        pliki["decyzje"] = ("Rejestr decyzji.md", test_potwierdzenia.REJESTR.replace(
            "---\n*Stopka rejestru.*", DODATKOWE + "---\n*Stopka rejestru.*"))
        for nazwa, tekst in pliki.values():
            with open(os.path.join(cls.sejf, "Produkcja", nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)
        with open(os.path.join(runtime, "klucz_gd.txt"), "w", encoding="utf-8") as f:
            f.write(cls.klucz_gd + "\n")
        with open(os.path.join(runtime, "telegram.json"), "w", encoding="utf-8") as f:
            json.dump({"token": TOKEN, "bot": "bc_test_bot", "osoby": {str(KAROL): "Karol", str(PAWEL): "Paweł"},
                       "grupy": {str(GRUPA): "B&C decyzje"}}, f, ensure_ascii=False)

    @classmethod
    def srodowisko(cls):
        return {"BC_TELEGRAM_TRYB_TESTOWY": "1", "BC_TELEGRAM_API_TESTOWE": cls.atrapa.adres}

    # ------------------------------------------------------------------ pomocnicze
    def rejestr(self):
        with open(os.path.join(self.sejf, "Produkcja", "Rejestr decyzji.md"), encoding="utf-8") as f:
            return f.read()

    def wersja(self):
        s, o, _ = self.get("/api/sejf/plan")
        self.assertEqual(s, 200, o)
        return o["wersje"]["decyzje"]

    def czekaj(self, warunek, czas=15.0):
        koniec = time.time() + czas
        while time.time() < koniec:
            if warunek():
                return True
            time.sleep(0.2)
        return False

    def potwierdz(self, ident, odp, wersja=None, **kw):
        cialo = {"odpowiedz": odp, "wersja": wersja or self.wersja()}
        if "uzasadnienie" in kw:
            cialo["uzasadnienie"] = kw.pop("uzasadnienie")
        return self.post("/api/sejf/decyzje/%s/potwierdzenie" % ident, cialo, **kw)

    def stan_bota(self):
        with open(os.path.join(self.tmp, "runtime", "telegram_stan.json"), encoding="utf-8") as f:
            return json.load(f)

    # ------------------------------------------------------------------ testy (kolejność alfabetyczna)
    def test_a_stan_bota_bez_tokenu(self):
        s, o, _ = self.get("/api/telegram/stan")
        self.assertEqual(s, 200, o)
        self.assertEqual((o["wlaczony"], o["bot"], o["osoby"], o["grupy"]), (True, "bc_test_bot", 2, 1))
        self.assertTrue(self.czekaj(lambda: self.get("/api/telegram/stan")[1]["odbior"]), "wątek odbioru nie wstał")
        self.assertTrue(self.atrapa.czekaj_na("getUpdates"), "bot nie odpytuje atrapy")
        self.assertBlad(self.get("/api/telegram/stan", zdalny=True), 403)
        for sciezka in ("/api/telegram/stan", "/api/ja", "/api/zdrowie", "/api/sejf/plan"):
            for kw in ({}, {"zdalny": True}):
                s, o, (n, b) = self.zadanie("GET", sciezka, bajty=True, **kw)
                tekst = b.decode("utf-8")
                self.assertNotIn(TOKEN, tekst, sciezka)
                self.assertNotIn(TOKEN.split(":")[1], tekst, sciezka)
                self.assertNotIn(str(GRUPA), tekst, sciezka)
        # zapytania do atrapy idą na ścieżkę /bot<token>/<metoda> (tak jak do prawdziwego API)
        self.assertTrue(all(p.startswith("/bot%s/" % TOKEN) for p in self.atrapa.sciezki()))

    def test_b_alert_i_klikniecie_przez_watek_odbioru(self):
        s, w, _ = self.post("/api/sejf/decyzje/D-008/status", {"status": "zatwierdzona", "uzasadnienie": "Bierzemy",
                                                               "wersja": self.wersja()}, kto="Karol")
        self.assertEqual(s, 200, w)
        alerty = self.atrapa.czekaj_na("sendMessage", warunek=lambda p: "D-008" in p.get("text", ""))
        self.assertTrue(alerty, "brak alertu na Telegramie")
        a = alerty[-1]
        self.assertEqual(a["chat_id"], GRUPA)
        self.assertIn("Karol zatwierdził decyzję D-008", a["text"])
        self.assertIn("Uzasadnienie: Bierzemy", a["text"])
        dane = a["reply_markup"]["inline_keyboard"][0][0]["callback_data"]
        self.assertRegex(dane, r"^p:D-008:z:[0-9a-f]{8}$")
        nr = self.atrapa.dodaj_aktualizacje(klikniecie(GRUPA, PAWEL, dane, wiadomosc_nr=901, tekst=a["text"]))
        self.assertTrue(self.czekaj(lambda: "potwierdził: Paweł %s" % dzis() in self.rejestr()), self.rejestr()[-600:])
        odp = self.atrapa.czekaj_na("answerCallbackQuery", warunek=lambda p: "zgoda" in p.get("text", ""))
        self.assertTrue(odp)
        self.assertTrue(self.atrapa.czekaj_na("editMessageText", warunek=lambda p: p.get("message_id") == 901))
        self.assertTrue(self.czekaj(lambda: self.stan_bota().get("offset", 0) >= nr + 1))
        with open(os.path.join(self.sejf, "Produkcja", "Dziennik zmian.md"), encoding="utf-8") as f:
            self.assertIn("- Paweł (Telegram): decyzja D-008 potwierdzona: zgoda", f.read())
        # te same dane jeszcze raz (np. drugie kliknięcie): nic nie czeka, w Rejestrze jeden podpis
        self.atrapa.dodaj_aktualizacje(klikniecie(GRUPA, PAWEL, dane, wiadomosc_nr=901, tekst=a["text"]))
        self.assertTrue(self.atrapa.czekaj_na("answerCallbackQuery", warunek=lambda p: "dwa podpisy" in p.get("text", "")))
        self.assertEqual(self.rejestr().count("· potwierdził: Paweł %s" % dzis()), 1)

    def test_c_trasa_potwierdzenia(self):
        przed = self.rejestr()
        s, e, _ = self.potwierdz("D-002", "zgoda", zdalny=True, kto="Paweł")                       # gość
        self.assertEqual((s, e.get("kod")), (403, "brak_klucza_zatwierdzania"), e)
        s, e, _ = self.potwierdz("D-002", "zgoda")                                                # bez imienia
        self.assertEqual((s, e.get("kod")), (400, "brak_imienia"), e)
        s, e, _ = self.potwierdz("D-002", "zgoda", zdalny=True, gd=self.klucz_gd, kto="Gość")
        self.assertEqual((s, e.get("kod")), (400, "brak_imienia"), e)
        s, e, _ = self.potwierdz("D-002", "zgoda", kto="Karol Balucki")                           # własna
        self.assertEqual((s, e.get("kod")), (403, "wlasna_decyzja"), e)
        self.assertIn("To Twoja decyzja", e["blad"])
        s, e, _ = self.potwierdz("D-002", "zgoda", kto="Zenek")
        self.assertEqual((s, e.get("kod")), (403, "spoza_zespolu"), e)
        self.assertBlad(self.potwierdz("D-002", "moze", kto="Paweł"), 400)
        s, e, _ = self.potwierdz("D-002", "zgoda", wersja="0" * 16, kto="Paweł")
        self.assertEqual((s, e.get("kod")), (409, "konflikt_wersji"), e)
        s, e, _ = self.potwierdz("D-001", "zgoda", kto="Paweł")                                    # stara decyzja
        self.assertEqual((s, e.get("kod")), (409, "nic_nie_czeka"), e)
        self.assertEqual(self.rejestr(), przed)
        # klucz zatwierdzania przez tunel: zgoda
        s, w, _ = self.potwierdz("D-002", "zgoda", zdalny=True, gd=self.klucz_gd, kto="Paweł")
        self.assertEqual(s, 200, w)
        self.assertPola(w, ["ok", "opis", "plik", "wersja", "plan", "potwierdzenie"])
        d = next(x for x in w["plan"]["decyzje"] if x["id"] == "D-002")
        self.assertEqual((d["czeka_na"], d["potwierdzil"]), (None, {"kto": "Paweł", "data": dzis()}))
        self.assertEqual(d["zdecydowal"], {"kto": "Karol Balucki", "data": "2026-11-13"})
        s, e, _ = self.potwierdz("D-002", "zgoda", zdalny=True, gd=self.klucz_gd, kto="Paweł")
        self.assertEqual((s, e.get("kod")), (409, "nic_nie_czeka"), e)
        # osoba przy komputerze: brak zgody z powodem
        s, w, _ = self.potwierdz("D-003", "sprzeciw", kto="Karol", uzasadnienie="Za wcześnie")
        self.assertEqual(s, 200, w)
        self.assertIn("🕓 do decyzji · technika · sprzeciw: Karol %s (wobec: odrzucona przez Paweł 2026-11-13)" % dzis(),
                      self.rejestr())
        self.assertIn("\nUzasadnienie sprzeciwu — Karol, %s: Za wcześnie\n" % dzis(), self.rejestr())
        d = next(x for x in w["plan"]["decyzje"] if x["id"] == "D-003")
        self.assertEqual((d["status"], d["sprzeciw"]["kto"], d["czeka_na"]), ("do_decyzji", "Karol", None))
        self.assertBlad(self.get("/api/sejf/decyzje/D-002/potwierdzenie"), 405)

    def test_d_blad_sieci_przy_wysylce(self):
        self.atrapa.awaria["sendMessage"] = "500"
        try:
            s, w, _ = self.post("/api/sejf/decyzje/D-007/status", {"status": "zatwierdzona", "wersja": self.wersja()},
                                kto="Karol")
            self.assertEqual(s, 200, w)                                                  # zapis nie czeka na Telegram
            self.assertIn("zdecydował: Karol %s" % dzis(), self.rejestr())
            self.assertTrue(self.atrapa.czekaj_na("sendMessage", warunek=lambda p: "D-007" in p.get("text", "")))
            self.assertTrue(self.czekaj(lambda: self.get("/api/telegram/stan")[1]["zalegle"] == 1))
            o = self.get("/api/telegram/stan")[1]
            self.assertTrue(o["ostatni_blad"] and "500" in o["ostatni_blad"]["tekst"], o)
            self.assertNotIn(TOKEN, json.dumps(o))
        finally:
            del self.atrapa.awaria["sendMessage"]
        # /czeka (Paweł w grupie) ponawia zaległy alert
        self.atrapa.wyczysc()
        self.atrapa.dodaj_aktualizacje(wiadomosc(GRUPA, PAWEL, "/czeka", nr=950))
        self.assertTrue(self.czekaj(lambda: self.get("/api/telegram/stan")[1]["zalegle"] == 0))
        teksty = [p["text"] for p in self.atrapa.zadania("sendMessage")]
        self.assertTrue(any("Karol zatwierdził decyzję D-007" in t for t in teksty), teksty)

    def test_z_logi_bez_tokenu(self):
        time.sleep(0.5)
        for p in (os.path.join(self.tmp, "runtime", "panel.log"), os.path.join(self.tmp, "serwer.log")):
            if os.path.exists(p):
                with open(p, "rb") as f:
                    tekst = f.read().decode("utf-8", "replace")
                self.assertNotIn(TOKEN, tekst, p)
                self.assertNotIn(TOKEN.split(":")[1], tekst, p)
        with open(os.path.join(self.tmp, "runtime", "panel.log"), encoding="utf-8") as f:
            self.assertIn("telegram:", f.read())                                        # błąd z próby sieci jest w logu


if __name__ == "__main__":
    unittest.main()
