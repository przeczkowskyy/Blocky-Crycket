# -*- coding: utf-8 -*-
"""Testy raportów i komentarzy (katalog tymczasowy — prawdziwe panel/dane zostają nietknięte).

Uruchomienie:  cd panel && python -m unittest testy.test_raporty
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

_TMP = tempfile.mkdtemp(prefix="bc_test_raporty_")
os.environ.setdefault("BC_PANEL_DANE", os.path.join(_TMP, "dane"))
os.environ.setdefault("BC_PANEL_RUNTIME", os.path.join(_TMP, "runtime"))

from bc import rdzen, raporty  # noqa: E402
from bc.http import Odp, Zadanie  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402


def _png(szer=4, wys=3):
    """Poprawny, mały obraz PNG (bez Pillow)."""
    import struct
    import zlib

    def kawalek(typ, dane):
        return struct.pack(">I", len(dane)) + typ + dane + struct.pack(">I", zlib.crc32(typ + dane) & 0xFFFFFFFF)
    wiersze = b"".join(b"\x00" + b"\xf5\xb8\x2e" * szer for _ in range(wys))
    return (b"\x89PNG\r\n\x1a\n" + kawalek(b"IHDR", struct.pack(">IIBBBBB", szer, wys, 8, 2, 0, 0, 0))
            + kawalek(b"IDAT", zlib.compress(wiersze)) + kawalek(b"IEND", b""))


PNG = _png()


def _zadanie(metoda, sciezka, cialo=None, params=None, query=None, kto="Paweł", lokalny=True):
    b = json.dumps(cialo).encode("utf-8") if cialo is not None else b""
    z = Zadanie(metoda, sciezka, query or {}, {}, b, lokalny, kto, "127.0.0.1", "127.0.0.1")
    z.params = params or {}
    return z


class _App:
    def __init__(self):
        self.trasy = {}

    def dodaj(self, metoda, wzorzec, fn):
        self.trasy[(metoda, wzorzec)] = fn


class TestRaporty(unittest.TestCase):
    def setUp(self):
        self.stare_dane = rdzen.DANE
        self.stary_log = rdzen.log
        rdzen.log = lambda *czesci: None                       # cisza w wyniku testów
        self.kat = tempfile.mkdtemp(prefix="dane_", dir=_TMP)
        rdzen.DANE = self.kat
        self.app = _App()
        raporty.zarejestruj(self.app)

    def tearDown(self):
        rdzen.DANE = self.stare_dane
        rdzen.log = self.stary_log
        shutil.rmtree(self.kat, ignore_errors=True)

    def trasa(self, metoda, wzorzec):
        return self.app.trasy[(metoda, wzorzec)]

    # --- tworzenie i walidacja
    def test_dodaj_i_odczytaj(self):
        r = raporty.dodaj_raport("Karczma: drzwi", "**Zrobione**", komponenty=[
            {"typ": "studio", "cel": "Workspace/DemoLesnaBaza/Karczma", "etykieta": "Karczma"},
            {"typ": "notatka", "cel": "B&C/UI/Ekwipunek.md"}], kto="Claude (Karol)")
        self.assertTrue(r["id"].startswith("r-"))
        self.assertEqual(r["status"], "czeka")
        self.assertEqual(r["komentarzy"], 0)
        self.assertEqual(r["komponenty"][1]["etykieta"], "Ekwipunek.md")
        self.assertTrue(os.path.isfile(os.path.join(self.kat, "raporty", r["id"] + ".json")))
        zapisany = rdzen.czytaj_json(os.path.join(self.kat, "raporty", r["id"] + ".json"))
        self.assertNotIn("status", zapisany)                   # status wyliczany przy odczycie
        lista = raporty.lista_raportow()
        self.assertEqual([x["id"] for x in lista], [r["id"]])

    def test_walidacja(self):
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("x" * 141)
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("")
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("ok", "o" * 8001)
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("ok", rodzaj="cos")
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("ok", komponenty=[{"typ": "studio", "cel": "A"}] * 13)
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("ok", komponenty=[{"typ": "zly", "cel": "A"}])
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("ok", komponenty=[{"typ": "studio", "cel": "A", "dziwne": 1}])
        with self.assertRaises(BladHTTP) as e:
            raporty.sprawdz_raport({"tytul": "ok", "hakerskie": True})
        self.assertEqual(e.exception.status, 400)
        self.assertIn("hakerskie", e.exception.komunikat)
        self.assertFalse(os.path.isdir(os.path.join(self.kat, "raporty")) and os.listdir(os.path.join(self.kat, "raporty")))

    def test_statusy_i_decyzja(self):
        info = raporty.dodaj_raport("Info", rodzaj="informacja")
        pyt = raporty.dodaj_raport("Pytanie", rodzaj="pytanie", pytanie="Czerwony czy zielony?")
        self.assertEqual(info["status"], "informacja")
        self.assertEqual(pyt["status"], "czeka")
        self.assertEqual(pyt["pytanie"], "Czerwony czy zielony?")
        r = raporty.zapisz_decyzje(pyt["id"], "do_poprawy", "Karol", "Zielony")
        self.assertEqual(r["status"], "do_poprawy")
        self.assertEqual(r["decyzja"]["komentarz"], "Zielony")
        self.assertTrue(os.path.isfile(os.path.join(self.kat, "raporty", pyt["id"] + ".decyzja.json")))
        r = raporty.zapisz_decyzje(pyt["id"], "zaakceptowane", "Karol")
        self.assertEqual(r["status"], "zaakceptowane")
        statusy = {x["id"]: x["status"] for x in raporty.lista_raportow()}
        self.assertEqual(statusy[pyt["id"]], "zaakceptowane")
        with self.assertRaises(BladHTTP):
            raporty.zapisz_decyzje(pyt["id"], "moze", "Karol")
        with self.assertRaises(BladHTTP) as e:
            raporty.zapisz_decyzje("r-nie-ma", "zaakceptowane", "Karol")
        self.assertEqual(e.exception.status, 404)

    def test_kolejnosc_najnowszy_pierwszy(self):
        a = raporty.dodaj_raport("A")
        b = raporty.dodaj_raport("B")
        # ręcznie postarz A, żeby kolejność nie zależała od tej samej sekundy
        p = os.path.join(self.kat, "raporty", a["id"] + ".json")
        d = rdzen.czytaj_json(p)
        d["czas"] = "2020-01-01T10:00:00+01:00"
        rdzen.zapisz_json(p, d)
        self.assertEqual([x["tytul"] for x in raporty.lista_raportow()], ["B", "A"])
        self.assertIsNotNone(b)

    # --- komentarze
    def test_komentarze(self):
        r = raporty.dodaj_raport("Z komentarzami")
        k1 = raporty.dodaj_komentarz({"typ": "raport", "cel": r["id"]}, "Super!", "Paweł")
        k2 = raporty.dodaj_komentarz({"typ": "studio", "cel": "Workspace/X/Karczma", "etykieta": "Karczma"},
                                     "Za ciemno", "Karol", "glos")
        self.assertTrue(k1["id"].startswith("k-"))
        self.assertEqual(k2["zrodlo"], "glos")
        self.assertEqual(raporty.raport(r["id"])["komentarzy"], 1)
        self.assertEqual(raporty.lista_raportow()[0]["komentarzy"], 1)
        watek = raporty.komentarze("raport", r["id"])
        self.assertEqual([k["tekst"] for k in watek], ["Super!"])
        self.assertEqual(len(raporty.komentarze()), 2)
        self.assertEqual(len(raporty.komentarze("studio")), 1)
        with self.assertRaises(BladHTTP):
            raporty.dodaj_komentarz({"typ": "raport", "cel": r["id"]}, "x" * 4001, "Paweł")
        with self.assertRaises(BladHTTP):
            raporty.dodaj_komentarz({"typ": "raport", "cel": r["id"]}, "   ", "Paweł")
        with self.assertRaises(BladHTTP):
            raporty.dodaj_komentarz({"typ": "zly", "cel": "a"}, "tekst", "Paweł")
        with self.assertRaises(BladHTTP) as e:
            raporty.dodaj_komentarz({"typ": "raport", "cel": "r-20200101-000000-dead"}, "tekst", "Paweł")
        self.assertEqual(e.exception.status, 404)

    # --- trasy HTTP (bez serwera)
    def test_trasy(self):
        post = self.trasy_post = self.trasa("POST", "/api/raporty")
        status, r = post(_zadanie("POST", "/api/raporty", {"tytul": "Z API", "opis_md": "# Hej", "rodzaj": "wdrozenie",
                                                           "komponenty": [{"typ": "migawka", "cel": "p-1", "etykieta": "M"}]}))
        self.assertEqual(status, 201)
        self.assertEqual(r["kto"], "Paweł")
        with self.assertRaises(BladHTTP):
            post(_zadanie("POST", "/api/raporty", {"tytul": "x", "id": "r-podrobione"}))
        with self.assertRaises(BladHTTP):
            post(_zadanie("POST", "/api/raporty", {"tytul": "x", "zrzuty": ["a.png"]}))
        wynik = self.trasa("GET", "/api/raporty")(_zadanie("GET", "/api/raporty"))
        self.assertEqual(wynik["czeka"], 1)
        dec = self.trasa("POST", "/api/raporty/<id>/decyzja")
        with self.assertRaises(BladHTTP):
            dec(_zadanie("POST", "x", {"wartosc": "zaakceptowane", "inne": 1}, params={"id": r["id"]}))
        r2 = dec(_zadanie("POST", "x", {"wartosc": "zaakceptowane", "komentarz": "OK"}, params={"id": r["id"]}, kto="Karol"))
        self.assertEqual(r2["decyzja"]["kto"], "Karol")
        kom = self.trasa("POST", "/api/komentarze")
        status, k = kom(_zadanie("POST", "x", {"cel": {"typ": "raport", "cel": r["id"]}, "tekst": "Dzięki"}))
        self.assertEqual(status, 201)
        with self.assertRaises(BladHTTP):
            kom(_zadanie("POST", "x", {"cel": {"typ": "raport", "cel": r["id"]}, "tekst": "x", "kto": "ktoś"}))
        szczeg = self.trasa("GET", "/api/raporty/<id>")(_zadanie("GET", "x", params={"id": r["id"]}))
        self.assertEqual(szczeg["status"], "zaakceptowane")
        self.assertEqual([x["id"] for x in szczeg["komentarze"]], [k["id"]])
        lista_k = self.trasa("GET", "/api/komentarze")(_zadanie("GET", "x", query={"typ": "raport", "cel": r["id"]}))
        self.assertEqual(len(lista_k["komentarze"]), 1)
        with self.assertRaises(BladHTTP) as e:
            self.trasa("GET", "/api/raporty/<id>")(_zadanie("GET", "x", params={"id": "../../etc"}))
        self.assertEqual(e.exception.status, 400)

    def test_zrzut_i_plik(self):
        png = os.path.join(self.kat, "zrzut.png")
        with open(png, "wb") as f:
            f.write(PNG)
        r = raporty.dodaj_raport("Ze zrzutem", zrzuty=[png])
        self.assertEqual(len(r["zrzuty"]), 1)
        nazwa = r["zrzuty"][0]
        self.assertTrue(os.path.isfile(os.path.join(self.kat, "raporty", r["id"], nazwa)))
        odp = self.trasa("GET", "/api/raporty/<id>/plik/<nazwa>")(_zadanie("GET", "x", params={"id": r["id"], "nazwa": nazwa}))
        self.assertIsInstance(odp, Odp)
        for zla in ("..\\..\\x.png", "../r.json", r["id"] + ".json", "nie_ma.png"):
            with self.assertRaises(BladHTTP):
                self.trasa("GET", "/api/raporty/<id>/plik/<nazwa>")(_zadanie("GET", "x", params={"id": r["id"], "nazwa": zla}))
        tekst = os.path.join(self.kat, "nie_obraz.png")
        with open(tekst, "wb") as f:
            f.write(b"to nie jest obraz" * 10)
        with self.assertRaises(BladHTTP):
            raporty.dodaj_raport("Zły zrzut", zrzuty=[tekst])
        self.assertEqual(len(raporty.lista_raportow()), 1)  # nieudany raport nie zostawił śladu

    def test_wydajnosc_listy(self):
        kat = os.path.join(self.kat, "raporty")
        os.makedirs(kat)
        for i in range(400):
            rid = "r-20261112-%06d-%04x" % (i, i)
            rdzen.zapisz_json(os.path.join(kat, rid + ".json"),
                              {"id": rid, "tytul": "Raport %d" % i, "opis_md": "", "kto": "Claude", "rodzaj": "wdrozenie",
                               "czas": "2026-11-12T10:%02d:%02d+01:00" % (i // 60, i % 60), "komponenty": [], "zrzuty": []})
        t0 = time.perf_counter()
        lista = raporty.lista_raportow()
        pierwszy = time.perf_counter() - t0
        t0 = time.perf_counter()
        for _ in range(20):
            raporty.lista_raportow()
        kolejne = (time.perf_counter() - t0) / 20
        self.assertEqual(len(lista), 400)
        self.assertEqual(lista[0]["tytul"], "Raport 399")
        self.assertLess(kolejne, 0.05, "lista z pamięci podręcznej powinna być natychmiastowa")
        self.assertLess(pierwszy, 5)
        nowy = raporty.dodaj_raport("Świeży")                  # nowy plik unieważnia pamięć
        self.assertEqual(len(raporty.lista_raportow()), 401)
        self.assertIn(nowy["id"], [r["id"] for r in raporty.lista_raportow()])

    # --- CLI (osobny proces, bez serwera)
    def test_cli(self):
        env = dict(os.environ, BC_PANEL_DANE=self.kat, BC_PANEL_RUNTIME=os.path.join(_TMP, "runtime"),
                   PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        cli = os.path.join(PANEL, "narzedzia", "raport.py")
        png = os.path.join(self.kat, "z.png")
        with open(png, "wb") as f:
            f.write(PNG)

        def uruchom(*argv):
            p = subprocess.run([sys.executable, "-B", cli] + list(argv), capture_output=True, env=env, timeout=60)
            return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")

        kod, out, err = uruchom("dodaj", "--tytul", "Z CLI — żółć", "--opis", "Opis", "--komponent",
                                "studio:Workspace/DemoLesnaBaza/Karczma:Karczma", "--zrzut", png, "--kto", "Claude (Karol)",
                                "--json")
        self.assertEqual(kod, 0, err)
        r = json.loads(out)
        self.assertEqual(r["tytul"], "Z CLI — żółć")
        self.assertEqual(r["komponenty"][0], {"typ": "studio", "cel": "Workspace/DemoLesnaBaza/Karczma", "etykieta": "Karczma"})
        self.assertEqual(len(r["zrzuty"]), 1)
        kod, out, _ = uruchom("lista")
        self.assertEqual(kod, 0)
        self.assertIn("Z CLI — żółć", out)
        kod, out, _ = uruchom("odpowiedzi", "--json")
        self.assertEqual(json.loads(out)["odpowiedzi"], [])
        raporty.zapisz_decyzje(r["id"], "do_poprawy", "Paweł", "Popraw kolor")
        raporty.dodaj_komentarz({"typ": "raport", "cel": r["id"]}, "I drzwi", "Karol")
        raporty.dodaj_komentarz({"typ": "raport", "cel": r["id"]}, "Poprawię", "Claude (Karol)")
        kod, out, _ = uruchom("odpowiedzi")
        self.assertEqual(kod, 0)
        self.assertIn("DO POPRAWY", out)
        self.assertIn("Popraw kolor", out)
        self.assertIn("I drzwi", out)
        self.assertNotIn("Poprawię", out)                      # wpisy agenta pomijane
        kod, out, _ = uruchom("odpowiedzi", "--od", "2999-01-01", "--json")
        self.assertEqual(json.loads(out)["odpowiedzi"], [])
        kod, out, err = uruchom("dodaj", "--tytul", "x" * 200)
        self.assertEqual(kod, 1)
        self.assertIn("za długie", err)


def tearDownModule():
    shutil.rmtree(_TMP, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
