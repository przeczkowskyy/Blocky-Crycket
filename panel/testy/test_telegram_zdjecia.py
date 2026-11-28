# -*- coding: utf-8 -*-
"""Narzędzie narzedzia/telegram_zdjecia.py (raport ze zdjęciami na grupę zespołu) — bez sieci i bez prawdziwego bota.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_telegram_zdjecia
Wywołania API są podmienione; ustawienia bota są zmyślone i podawane jawnie.
"""
import email
import email.policy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
import urllib.error
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _s in (PANEL, os.path.join(PANEL, "narzedzia")):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import testy  # noqa: F401,E402  (katalogi zastępcze panelu)
import telegram_zdjecia as tz  # noqa: E402

TOKEN = "123456:TEST-zmyslony-token-atrapy-xyz"
GRUPA = -1001
USTAW = {"wlaczony": True, "token": TOKEN, "bot": "bc_test_bot", "osoby": {}, "grupy": {GRUPA: "B&C"}, "blad": None}
JPG = b"\xff\xd8\xff\xe0" + bytes(range(256)) * 4 + b"\r\n--granica\r\n\xff\xd9"


class Baza(unittest.TestCase):
    def setUp(self):
        self.kat = tempfile.mkdtemp(prefix="bc_tg_zdjecia_")
        self.addCleanup(shutil.rmtree, self.kat, True)
        for n in ("a.jpg", "b.jpg", "c.png"):
            with open(os.path.join(self.kat, n), "wb") as f:
                f.write(JPG)

    def plan(self, d):
        p = os.path.join(self.kat, "plan.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        return p


class TestPlanu(Baza):
    def test_1_poprawny_plan_i_sciezki_wzgledem_planu(self):
        plan = tz.wczytaj_plan(self.plan({"tekst": " Wstęp ", "koniec": "Koniec",
                                          "grupy": [{"podpis": "1. Miasto", "zdjecia": ["a.jpg", "b.jpg"]},
                                                    {"zdjecia": [os.path.join(self.kat, "c.png")]}]}))
        self.assertEqual((plan["tekst"], plan["koniec"]), ("Wstęp", "Koniec"))
        self.assertEqual([len(g["zdjecia"]) for g in plan["grupy"]], [2, 1])
        self.assertTrue(all(os.path.isabs(p) and os.path.isfile(p) for g in plan["grupy"] for p in g["zdjecia"]))
        self.assertEqual(plan["grupy"][1]["podpis"], "")

    def test_2_zle_plany(self):
        zle = [
            ({}, "pusty"),
            ({"tekst": "x" * (tz.MAKS_TEKST + 1)}, "znaków"),
            ({"grupy": [{"podpis": "p" * (tz.MAKS_PODPIS + 1), "zdjecia": ["a.jpg"]}]}, "Podpis"),
            ({"grupy": [{"zdjecia": []}]}, "od 1 do"),
            ({"grupy": [{"zdjecia": ["a.jpg"] * (tz.MAKS_ZDJEC_W_GRUPIE + 1)}]}, "od 1 do"),
            ({"grupy": [{"zdjecia": ["nie_ma.jpg"]}]}, "brak pliku"),
            ({"grupy": [{"zdjecia": ["plan.json"]}]}, "JPG albo PNG"),
            ({"grupy": "a.jpg"}, "listą"),
        ]
        for d, slowo in zle:
            with self.assertRaises(tz.Blad, msg=str(d)[:60]) as k:
                tz.wczytaj_plan(self.plan(d))
            self.assertIn(slowo, str(k.exception))
        with self.assertRaises(tz.Blad):
            tz.wczytaj_plan(os.path.join(self.kat, "brak_planu.json"))

    def test_3_komunikat_bez_sciezki_z_komputera(self):
        with self.assertRaises(tz.Blad) as k:
            tz.wczytaj_plan(self.plan({"grupy": [{"zdjecia": ["nie_ma.jpg"]}]}))
        self.assertNotIn(self.kat, str(k.exception))


class TestTresci(unittest.TestCase):
    def test_1_wieloczesciowe_wraca_te_same_bajty_i_polskie_znaki(self):
        media = json.dumps([{"type": "photo", "media": "attach://f0", "caption": "zażółć gęślą jaźń — „test”"}],
                           ensure_ascii=False)
        tresc, typ = tz.wieloczesciowe({"chat_id": GRUPA, "media": media}, {"f0": ("zdjecie_1.jpg", JPG, "image/jpeg")})
        msg = email.message_from_bytes(b"Content-Type: " + typ.encode("ascii") + b"\r\n\r\n" + tresc,
                                       policy=email.policy.HTTP)
        czesci = {p.get_param("name", header="content-disposition"): p for p in msg.iter_parts()}
        self.assertEqual(set(czesci), {"chat_id", "media", "f0"})
        self.assertEqual(czesci["chat_id"].get_payload(decode=True), str(GRUPA).encode("ascii"))
        self.assertEqual(json.loads(czesci["media"].get_payload(decode=True).decode("utf-8"))[0]["caption"],
                         "zażółć gęślą jaźń — „test”")
        self.assertEqual(czesci["f0"].get_payload(decode=True), JPG)
        self.assertEqual((czesci["f0"].get_filename(), czesci["f0"].get_content_type()), ("zdjecie_1.jpg", "image/jpeg"))


class TestWysylki(Baza):
    def setUp(self):
        super().setUp()
        self.wywolania = []
        self.latki = [mock.patch.object(tz, "_wywolaj", side_effect=self._wywolaj), mock.patch.object(tz.time, "sleep")]
        for l in self.latki:
            l.start()
            self.addCleanup(l.stop)

    def _wywolaj(self, token, metoda, pola, pliki=None, czas=90, ponow=True):
        self.wywolania.append((token, metoda, pola, pliki or {}))
        return {"ok": True}

    def test_1_kolejnosc_metody_i_podpisy(self):
        plan = tz.wczytaj_plan(self.plan({"tekst": "Wstęp", "koniec": "Koniec",
                                          "grupy": [{"podpis": "1. Album", "zdjecia": ["a.jpg", "b.jpg", "c.png"]},
                                                    {"podpis": "2. Jedno", "zdjecia": ["a.jpg"]}]}))
        linie = []
        wynik = tz.wyslij(plan, ustaw=USTAW, pisz=linie.append)
        self.assertEqual(wynik, {"grupy": 1, "wiadomosci": 4, "zdjecia": 4})
        self.assertEqual([w[1] for w in self.wywolania], ["sendMessage", "sendMediaGroup", "sendPhoto", "sendMessage"])
        self.assertTrue(all(w[0] == TOKEN and w[2]["chat_id"] == GRUPA for w in self.wywolania))
        self.assertEqual((self.wywolania[0][2]["text"], self.wywolania[3][2]["text"]), ("Wstęp", "Koniec"))
        self.assertNotIn("parse_mode", self.wywolania[0][2])                     # zwykły tekst, bez HTML
        media = json.loads(self.wywolania[1][2]["media"])
        self.assertEqual([m["media"] for m in media], ["attach://f0", "attach://f1", "attach://f2"])
        self.assertEqual([m.get("caption") for m in media], ["1. Album", None, None])
        pliki = self.wywolania[1][3]
        self.assertEqual(sorted(pliki), ["f0", "f1", "f2"])
        self.assertEqual([pliki[k][0] for k in sorted(pliki)], ["zdjecie_1.jpg", "zdjecie_2.jpg", "zdjecie_3.png"])
        self.assertEqual(pliki["f2"][2], "image/png")
        self.assertEqual(self.wywolania[2][2]["caption"], "2. Jedno")
        self.assertEqual(self.wywolania[2][3]["photo"][1], JPG)
        self.assertEqual(len(linie), 2)

    def test_2_bot_wylaczony_albo_bez_grupy_nic_nie_wysyla(self):
        plan = tz.wczytaj_plan(self.plan({"tekst": "Wstęp"}))
        for ustaw in (dict(USTAW, wlaczony=False, token=None), dict(USTAW, grupy={})):
            with self.assertRaises(tz.Blad):
                tz.wyslij(plan, ustaw=ustaw)
        self.assertEqual(self.wywolania, [])

    def test_3_na_sucho_nic_nie_wysyla(self):
        p = self.plan({"tekst": "Wstęp", "grupy": [{"zdjecia": ["a.jpg"]}]})
        with mock.patch.object(tz.telegram, "ustawienia", return_value=USTAW), mock.patch("sys.stdout", io.StringIO()) as wy:
            kod = tz.main(["--plan", p, "--sucho"])
        self.assertEqual((kod, self.wywolania), (0, []))
        self.assertIn("nic nie wysłano", wy.getvalue())
        self.assertNotIn(TOKEN, wy.getvalue())
        self.assertNotIn(str(GRUPA), wy.getvalue())

    def test_4_zly_plan_daje_kod_1_i_komunikat(self):
        with mock.patch("sys.stdout", io.StringIO()) as wy:
            kod = tz.main(["--plan", self.plan({})])
        self.assertEqual(kod, 1)
        self.assertIn("BŁĄD", wy.getvalue())


class TestBledowApi(unittest.TestCase):
    def test_1_blad_telegrama_bez_tokenu_i_bez_adresu(self):
        cialo = json.dumps({"ok": False, "description": "Bad Request: zły token %s w adresie" % TOKEN}).encode("utf-8")
        blad = urllib.error.HTTPError("https://api.telegram.org/bot%s/sendPhoto" % TOKEN, 400, "Bad Request", {}, io.BytesIO(cialo))
        with mock.patch.object(tz.urllib.request, "urlopen", side_effect=blad):
            with self.assertRaises(tz.Blad) as k:
                tz._wywolaj(TOKEN, "sendPhoto", {"chat_id": GRUPA}, {"photo": ("zdjecie_1.jpg", JPG, "image/jpeg")})
        tekst = str(k.exception)
        self.assertIn("kod 400", tekst)
        self.assertNotIn(TOKEN, tekst)
        self.assertNotIn("api.telegram.org", tekst)
        self.assertIsNone(k.exception.__cause__)                                 # bez łańcucha z adresem żądania
        self.assertTrue(k.exception.__suppress_context__)

    def test_2_brak_sieci(self):
        with mock.patch.object(tz.urllib.request, "urlopen", side_effect=urllib.error.URLError("brak")):
            with self.assertRaises(tz.Blad) as k:
                tz._wywolaj(TOKEN, "sendMessage", {"chat_id": GRUPA, "text": "x"})
        self.assertNotIn(TOKEN, str(k.exception))

    def test_3_limit_429_ponawia_raz(self):
        cialo = json.dumps({"ok": False, "description": "Too Many Requests", "parameters": {"retry_after": 2}}).encode("utf-8")

        class Odp:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return json.dumps({"ok": True, "result": {"message_id": 7}}).encode("utf-8")

        kolejka = [urllib.error.HTTPError("x", 429, "Too Many Requests", {}, io.BytesIO(cialo)), Odp()]

        def urlopen(req, timeout=None):
            x = kolejka.pop(0)
            if isinstance(x, Exception):
                raise x
            return x

        with mock.patch.object(tz.urllib.request, "urlopen", side_effect=urlopen), mock.patch.object(tz.time, "sleep") as spij:
            wynik = tz._wywolaj(TOKEN, "sendMessage", {"chat_id": GRUPA, "text": "x"})
        self.assertEqual(wynik, {"message_id": 7})
        spij.assert_called_once_with(3)
        self.assertEqual(kolejka, [])


if __name__ == "__main__":
    unittest.main()
