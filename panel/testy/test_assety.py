# -*- coding: utf-8 -*-
"""Testy zakładki Assety (rejestr grafik gry — tylko do odczytu) na tymczasowym „repozytorium”.

Uruchomienie (z katalogu panel/):  python -m unittest testy.test_assety
Prawdziwe assets/ i panel/dane zostają nietknięte: na czas testu rdzen.REPO i rdzen.DANE wskazują katalog
tymczasowy z własnym manifestem i obrazami (w tym ze ścieżkami złośliwymi). Pillow jest opcjonalny.
"""
import hashlib
import io
import json
import os
import random
import re
import shutil
import struct
import sys
import tempfile
import unittest
import urllib.parse
import zlib
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import assety, raporty, rdzen, statyczny  # noqa: E402
from bc.http import Aplikacja, Odp, Strumien, Zadanie  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

try:
    from PIL import Image
except Exception:                                              # Pillow jest opcjonalny
    Image = None


def _png(szer=4, wys=3, alfa=False, szum=False):
    """Poprawny obraz PNG bez Pillow. `szum` = losowe piksele (plik duży, bo niekompresowalny)."""
    def kawalek(typ, dane):
        return struct.pack(">I", len(dane)) + typ + dane + struct.pack(">I", zlib.crc32(typ + dane) & 0xFFFFFFFF)
    kanaly = 4 if alfa else 3
    los = random.Random(7)
    piksel = b"\xf5\xb8\x2e\x80" if alfa else b"\xf5\xb8\x2e"
    wiersze = b"".join(b"\x00" + (los.randbytes(szer * kanaly) if szum else piksel * szer) for _ in range(wys))
    return (b"\x89PNG\r\n\x1a\n" + kawalek(b"IHDR", struct.pack(">IIBBBBB", szer, wys, 8, 6 if alfa else 2, 0, 0, 0))
            + kawalek(b"IDAT", zlib.compress(wiersze)) + kawalek(b"IEND", b""))


PNG = _png()


def zadanie(nazwa=None, sciezka="/api/assety", lokalny=False):
    """Żądanie gościa (bez praw osoby przy komputerze) — zakładka ma działać tak samo dla każdego."""
    z = Zadanie("GET", sciezka, {}, {}, b"", lokalny, "gość", "192.168.1.50", "127.0.0.1:8787")
    z.params = {"nazwa": nazwa} if nazwa is not None else {}
    return z


class Baza(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_assety_")
        self.repo = os.path.join(self.tmp, "repo")
        os.makedirs(os.path.join(self.repo, "assets", "processed"))
        os.makedirs(os.path.join(self.repo, "assets", "raw"))
        self._stare = (rdzen.REPO, rdzen.DANE, rdzen.log, dict(assety._pil))
        rdzen.REPO = self.repo
        rdzen.DANE = os.path.join(self.tmp, "dane")
        rdzen.log = lambda *czesci: None                       # cisza w wyniku testów, nic do prawdziwego logu
        self.czysc_pamiec()

    def tearDown(self):
        rdzen.REPO, rdzen.DANE, rdzen.log = self._stare[:3]
        assety._pil.clear()
        assety._pil.update(self._stare[3])
        self.czysc_pamiec()
        shutil.rmtree(self.tmp, ignore_errors=True)

    @staticmethod
    def czysc_pamiec():
        assety._pamiec.update(klucz=None, dane=None, blad=None, indeks=None, indeks_dla=None)
        assety._obrazy.clear()
        assety._miniatury.clear()
        assety._sygnatura.update(wartosc=None, kiedy=0.0)

    def plik(self, wzgledna, dane=PNG):
        pelna = os.path.join(self.repo, *wzgledna.split("/"))
        os.makedirs(os.path.dirname(pelna), exist_ok=True)
        with open(pelna, "wb") as f:
            f.write(dane)
        return pelna

    def manifest(self, assets, surowy=None, **pola):
        sciezka = os.path.join(self.repo, "assets", "manifest.json")
        with open(sciezka, "w", encoding="utf-8", newline="\n") as f:
            if surowy is not None:
                f.write(surowy)
            else:
                json.dump(dict({"figma_file": "BbLd4jDnvxAmOWZN1hAZQJ", "assets": assets}, **pola), f, ensure_ascii=False)
        return sciezka

    def asset(self, nazwa):
        return next(a for a in assety.rejestr()["assety"] if a["nazwa"] == nazwa)

    def stan_dysku(self):
        """Wszystkie pliki katalogu tymczasowego z rozmiarem i czasem zmiany — do sprawdzenia „zero zapisu”."""
        wynik = {}
        for katalog, _, pliki in os.walk(self.tmp):
            for p in pliki:
                st = os.stat(os.path.join(katalog, p))
                wynik[os.path.relpath(os.path.join(katalog, p), self.tmp)] = (st.st_size, st.st_mtime_ns)
        return wynik


# --------------------------------------------------------------------------- rejestr
class TestRejestr(Baza):
    def test_brak_manifestu_to_stan_pusty_a_nie_blad(self):
        r = assety.rejestr()
        self.assertEqual(r["zrodlo"], "assets/manifest.json")
        self.assertIs(r["brak_manifestu"], True)
        self.assertNotIn("blad", r)
        self.assertEqual((r["assety"], r["liczniki"], r["czeka"]), ([], {}, 0))
        self.assertEqual([e["id"] for e in r["etapy"]], ["generowanie", "obrobka", "figma", "zgoda", "roblox"])
        self.assertTrue(all(e["liczba"] == 0 and e["nazwa"] and e["opis"] for e in r["etapy"]))
        self.assertEqual(assety.zdrowie(), {"manifest": False, "assety": 0, "bez_obrazu": 0, "czeka_na_zgode": 0})
        for nazwa in ("Teleport", "Teleport.png", ".."):
            with self.assertRaises(BladHTTP) as e:
                assety._get_plik(zadanie(nazwa))
            self.assertEqual(e.exception.status, 404)

    def test_uszkodzony_manifest_ma_komunikat_po_polsku(self):
        self.manifest(None, surowy='{"assets": {"Teleport": {"status": "done",}')
        r = assety.rejestr()
        self.assertNotIn("brak_manifestu", r)
        self.assertIn("wierszu 1", r["blad"])
        self.assertEqual(r["assety"], [])
        z = assety.zdrowie()
        self.assertEqual((z["manifest"], z["assety"]), (True, 0))
        self.assertTrue(z["blad"])
        for surowy, fragment in (("[1, 2]", "nieoczekiwany kształt"), ('"tekst"', "nieoczekiwany kształt"),
                                 ("", "wierszu 1")):
            self.manifest(None, surowy=surowy)
            self.assertIn(fragment, assety.rejestr()["blad"], surowy)
        with open(self.manifest(None, surowy="x"), "wb") as f:
            f.write(b'{"assets": {"\xff\xfe": {}}}')
        self.assertIn("UTF-8", assety.rejestr()["blad"])

    def test_blad_odczytu_bez_lokalnej_sciezki(self):
        """Komunikat systemu („Permission denied: 'C:\\Users\\…\\manifest.json'”) niesie ścieżkę tego komputera —
        a `blad` widzi gość z telefonu i trafia do lustra. Odczytu nie da się zrobić: manifest jest katalogiem."""
        os.makedirs(os.path.join(self.repo, "assets", "manifest.json"))
        r = assety.rejestr()
        self.assertIn("Nie mogę odczytać assets/manifest.json", r["blad"])
        tresc = json.dumps(r, ensure_ascii=False) + json.dumps(assety.zdrowie(), ensure_ascii=False)
        for fragment in (self.tmp, self.repo, os.path.basename(self.tmp), "\\\\", "Users"):
            self.assertNotIn(fragment, tresc)

    def test_dziwny_ksztalt_assets_nie_wywraca(self):
        for assets in (None, 5, "tekst", [], [1, "a", None], {}):
            self.manifest(assets)
            r = assety.rejestr()
            self.assertEqual(r["assety"], [], assets)
            self.assertNotIn("blad", r)
        self.manifest(None, surowy='{"inne": 1}')                    # brak pola assets
        self.assertEqual(assety.rejestr()["assety"], [])

    def test_pelny_wpis(self):
        self.plik("assets/processed/Teleport.png", _png(40, 30, alfa=True))
        self.manifest({"Teleport": {
            "created_at": "2026-11-11T22:26:12+00:00", "updated_at": "2026-11-12T19:37:52+00:00",
            "history": [{"roblox_image": "111", "replaced_at": "2026-11-12T10:00:00+00:00"}],
            "category": "button", "status": "in_roblox", "processed": "assets/processed/Teleport.png",
            "figma_node": "10:1563", "usage": "HUD button", "notes": "Oryginał od zespołu",
            "roblox_image": "133130837278176", "roblox_decal": 999, "moderation": "Approved",
            "roblox_target": "StarterGui.HUD.LeftColumn.TeleportSlot.Teleport.Image",
            "prompt": "cartoon portal", "raw": "assets/raw/Teleport"}}, updated_at="2026-11-12T19:37:53+00:00")
        r = assety.rejestr()
        self.assertEqual((r["figma_plik"], r["zaktualizowano"]), ("BbLd4jDnvxAmOWZN1hAZQJ", "2026-11-12T19:37:53+00:00"))
        self.assertEqual((r["liczniki"], r["czeka"]), ({"in_roblox": 1}, 0))
        self.assertEqual([e["liczba"] for e in r["etapy"]], [0, 0, 0, 0, 1])
        a = r["assety"][0]
        for pole in ("nazwa", "kategoria", "status", "status_opis", "etap", "uzycie", "notatki", "obraz", "historia",
                     "czeka_na_zgode"):
            self.assertIn(pole, a)
        self.assertEqual((a["nazwa"], a["kategoria"], a["kategoria_opis"]), ("Teleport", "button", "przycisk"))
        self.assertEqual((a["status"], a["status_opis"], a["etap"]), ("in_roblox", "w Roblox", 4))
        self.assertEqual((a["uzycie"], a["notatki"]), ("HUD button", "Oryginał od zespołu"))
        self.assertRegex(a["obraz"], r"^/api/assety/plik/Teleport\.png\?v=\d+$")
        self.assertEqual((a["plik"], a["wymiary"], a["rozmiar"]), ("assets/processed/Teleport.png", [40, 30],
                                                                   len(_png(40, 30, alfa=True))))
        self.assertEqual((a["roblox_id"], a["roblox_decal"], a["moderacja"]), ("133130837278176", "999", "Approved"))
        self.assertEqual(a["roblox_cel"], "StarterGui.HUD.LeftColumn.TeleportSlot.Teleport.Image")
        self.assertEqual(a["figma_wezel"], "10:1563")
        self.assertEqual(a["figma_adres"], "https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ/Teleport?node-id=10-1563")
        self.assertEqual((a["utworzono"], a["zmieniono"]), ("2026-11-11T22:26:12+00:00", "2026-11-12T19:37:52+00:00"))
        self.assertEqual(a["historia"], [{"opis": "Poprzedni numer obrazu Roblox", "pole": "roblox_image",
                                          "wartosc": "111", "kiedy": "2026-11-12T10:00:00+00:00"}])
        self.assertEqual((a["prompt"], a["surowe"]), ("cartoon portal", "assets/raw/Teleport"))
        self.assertEqual((a["czeka_na_zgode"], a["cel_komentarzy"]), (False, "assets/processed/Teleport.png"))
        self.assertNotIn("uwagi", a)
        self.assertNotIn("zgoda", a)
        self.assertEqual(assety.zdrowie(), {"manifest": True, "assety": 1, "bez_obrazu": 0, "czeka_na_zgode": 0})
        json.dumps(r)                                                # cała odpowiedź daje się zapisać jako JSON

    def test_brakujace_i_dodatkowe_klucze(self):
        self.manifest({
            "Pusty": {},
            "NieSlownik": "tekst zamiast wpisu",
            "Lista": [1, 2],
            "Dodatki": {"status": "Generated", "wariant": 2, "autor": "Karol", "flaga": True, "pusty": "",
                        "zagniezdzone": {"a": 1}, "lista": [1], "api_key": "sekret-1", "ROBLOX_TOKEN": "sekret-2",
                        "haslo": "sekret-3", "history": "nie lista", "usage": 5, "notes": None, "category": 7,
                        "roblox_image": 1.33130837278176e14, "created_at": "wczoraj", "updated_at": 5},
            "  Spacje  ": {"status": "done"},
            "": {"status": "done"},
        })
        r = assety.rejestr()
        self.assertEqual([a["nazwa"] for a in r["assety"]], ["Pusty", "NieSlownik", "Lista", "Dodatki", "Spacje"])
        for nazwa in ("Pusty", "NieSlownik", "Lista"):
            a = self.asset(nazwa)
            self.assertEqual((a["status"], a["status_opis"], a["etap"], a["status_nieznany"]),
                             ("brak", "bez statusu", None, True))
            self.assertEqual((a["kategoria"], a["kategoria_opis"], a["uzycie"], a["notatki"], a["obraz"], a["historia"]),
                             ("", "bez kategorii", "", "", None, []))
            self.assertFalse(a["czeka_na_zgode"])
            self.assertEqual(a["cel_komentarzy"], "assets/processed/%s.png" % nazwa)
        d = self.asset("Dodatki")
        self.assertEqual((d["status"], d["status_opis"], d["etap"]), ("generated", "wygenerowany", 0))
        self.assertEqual(d["inne"], {"wariant": "2", "autor": "Karol", "flaga": "tak"})
        self.assertNotIn("sekret", json.dumps(r))                    # nic, co wygląda na sekret, nie wychodzi przez API
        self.assertEqual((d["uzycie"], d["notatki"], d["kategoria"], d["historia"]), ("5", "", "7", []))
        self.assertEqual(d["roblox_id"], "133130837278176")           # liczba z manifestu bez notacji wykładniczej
        self.assertNotIn("utworzono", d)
        self.assertNotIn("zmieniono", d)
        self.assertEqual(r["liczniki"], {"brak": 3, "generated": 1, "done": 1})
        nieznane = [s for s in r["statusy"] if s.get("nieznany")]
        self.assertEqual([(s["id"], s["liczba"]) for s in nieznane], [("brak", 3)])

    def test_lista_wpisow_zamiast_slownika(self):
        self.manifest([{"name": "IconArena", "status": "planned"}, {"nazwa": "IconDungeon", "status": "wip"},
                       {"status": "done"}, "śmieć", {"name": "IconArena", "status": "done"}])
        r = assety.rejestr()
        self.assertEqual([(a["nazwa"], a["status"]) for a in r["assety"]], [("IconArena", "planned"), ("IconDungeon", "wip")])
        wip = self.asset("IconDungeon")
        self.assertEqual((wip["status_opis"], wip["etap"], wip["status_nieznany"]), ("wip", None, True))

    def test_statusy_pokrywaja_pipeline(self):
        for status, (nazwa, etap, opis) in assety.STATUSY.items():
            self.assertTrue(nazwa and opis, status)
            self.assertTrue(etap is None or 0 <= etap < len(assety.ETAPY), status)
        self.assertIsNone(assety.STATUSY["rejected"][1])
        self.assertEqual(sum(1 for e in assety.ETAPY if e.get("bramka")), 1)
        self.assertEqual(assety.ETAPY[assety.STATUSY["awaiting_approval"][1]]["id"], "zgoda")
        self.assertLess(assety.STATUSY["in_figma"][1], assety.STATUSY["awaiting_approval"][1])     # Figma przed zgodą
        self.assertLess(assety.STATUSY["approved"][1], assety.STATUSY["in_roblox"][1])             # zgoda przed Roblox
        # lista statusów z prawdziwego narzędzia pipeline'u — gdy dojdzie nowy, ten test przypomni o panelu
        narzedzie = os.path.join(os.path.dirname(PANEL), "tools", "manifest.py")
        if os.path.isfile(narzedzie):
            with open(narzedzie, encoding="utf-8") as f:
                linia = next((l for l in f if l.startswith("Statusy:")), "")
            for status in [s.strip() for s in linia.replace("Statusy:", "").split(",") if s.strip()]:
                self.assertIn(status, assety.STATUSY)
        self.manifest({s: {"status": s} for s in assety.STATUSY})
        r = assety.rejestr()
        self.assertEqual(sum(e["liczba"] for e in r["etapy"]), len(assety.STATUSY) - 1)            # bez odrzuconego
        self.assertEqual(r["liczniki"], {s: 1 for s in assety.STATUSY})
        self.assertEqual([s["id"] for s in r["statusy"]], list(assety.STATUSY))

    def test_czeka_na_zgode(self):
        dobry = self.plik("assets/processed/Dobry.png", _png(8, 8))
        self.plik("assets/processed/Zmieniony.png", _png(9, 9))
        with open(dobry, "rb") as f:
            suma = hashlib.sha256(f.read()).hexdigest()
        self.manifest({
            "Czeka": {"status": "awaiting_approval"},
            "Dobry": {"status": "approved", "processed": "assets/processed/Dobry.png", "approved_by_user": True,
                      "approved_sha256": suma, "approved_at": "2026-11-12T20:00:00+00:00"},
            "Zmieniony": {"status": "approved", "processed": "assets/processed/Zmieniony.png", "approved_by_user": True,
                          "approved_sha256": "0" * 64},
            "Cofniety": {"status": "approved", "approved_by_user": False},
            "WFigmie": {"status": "in_figma"},
            "Stary": {"status": "in_roblox", "roblox_image": "1"},
        })
        r = assety.rejestr()
        self.assertEqual({a["nazwa"]: a["czeka_na_zgode"] for a in r["assety"]},
                         {"Czeka": True, "Dobry": False, "Zmieniony": True, "Cofniety": True, "WFigmie": False,
                          "Stary": False})
        self.assertEqual((r["czeka"], assety.zdrowie()["czeka_na_zgode"]), (3, 3))
        self.assertEqual(self.asset("Dobry")["zgoda"], {"jest": True, "kiedy": "2026-11-12T20:00:00+00:00", "aktualna": True})
        self.assertEqual(self.asset("Zmieniony")["zgoda"], {"jest": True, "aktualna": False})
        self.assertIn("zgoda wygasła", self.asset("Zmieniony")["uwagi"][0])
        self.assertEqual(self.asset("Cofniety")["zgoda"], {"jest": False})
        self.assertEqual(self.asset("Czeka")["zgoda"], {"jest": False})
        self.assertNotIn("zgoda", self.asset("Stary"))
        self.assertNotIn(suma, json.dumps(r))                         # sumy kontrolnej nie ma po co wysyłać
        self.assertEqual([e["liczba"] for e in r["etapy"]], [0, 0, 1, 4, 1])

    def test_uwagi_o_niespojnosciach(self):
        self.manifest({"BezNumeru": {"status": "in_roblox"}, "Odrzucony": {"status": "pending_studio",
                                                                         "moderation": "Rejected"},
                       "BezPliku": {"status": "processed", "processed": "assets/processed/NieMa.png"}})
        self.assertIn("nie ma numeru obrazu", self.asset("BezNumeru")["uwagi"][0])
        self.assertIn("Moderacja", self.asset("Odrzucony")["uwagi"][0])
        b = self.asset("BezPliku")
        self.assertEqual((b["obraz"], b["miniatura"], b["plik"]), (None, None, "assets/processed/NieMa.png"))
        self.assertIn("nie ma go na dysku", b["uwagi"][0])
        self.assertEqual(assety.zdrowie()["bez_obrazu"], 3)

    def test_adres_figmy(self):
        f = assety.adres_figmy
        self.assertEqual(f("BbLd4jDnvxAmOWZN1hAZQJ", "2:76", "KeyArt"),
                         "https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ/KeyArt?node-id=2-76")
        self.assertEqual(f("BbLd4jDnvxAmOWZN1hAZQJ", "I5666:180910;1:10515", "Ikona areny!"),
                         "https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ/Ikona-areny?node-id=I5666-180910%3B1-10515")
        for plik, wezel in ((None, "1:2"), ("", "1:2"), ("krotki", "1:2"), ("zly/klucz/pliku", "1:2"),
                            ("BbLd4jDnvxAmOWZN1hAZQJ", None), ("BbLd4jDnvxAmOWZN1hAZQJ", ""),
                            ("BbLd4jDnvxAmOWZN1hAZQJ", "Assets Library"), ("BbLd4jDnvxAmOWZN1hAZQJ", "1:2&x=1"),
                            ("BbLd4jDnvxAmOWZN1hAZQJ", "javascript:alert"), ("BbLd4jDnvxAmOWZN1hAZQJ", 12)):
            self.assertIsNone(f(plik, wezel, "X"), (plik, wezel))
        self.manifest({"A": {"figma_node": "1:2"}}, figma_file="../../zly")
        r = assety.rejestr()
        self.assertNotIn("figma_plik", r)
        self.assertNotIn("figma_adres", r["assety"][0])
        self.assertEqual(r["assety"][0]["figma_wezel"], "1:2")

    def test_pamiec_podreczna_po_czasie_modyfikacji(self):
        sciezka = self.manifest({"A": {"status": "planned"}})
        d1, _ = assety.manifest()
        d2, _ = assety.manifest()
        self.assertIs(d1, d2)                                        # bez zmiany pliku nic nie jest czytane ponownie
        self.assertIs(assety._indeks(), assety._indeks())
        self.manifest({"A": {"status": "planned"}, "B": {"status": "done"}})
        self.assertEqual([a["nazwa"] for a in assety.rejestr()["assety"]], ["A", "B"])
        # ta sama długość pliku, inny czas modyfikacji — też nowy odczyt
        st = os.stat(self.manifest({"A": {"status": "planned"}, "C": {"status": "done"}}))
        os.utime(sciezka, ns=(st.st_atime_ns, st.st_mtime_ns + 5_000_000_000))
        self.assertEqual([a["nazwa"] for a in assety.rejestr()["assety"]], ["A", "C"])
        os.remove(sciezka)
        self.assertTrue(assety.rejestr()["brak_manifestu"])
        # obraz podmieniony bez zmiany manifestu: nowy adres (wersja pliku), nowe wymiary
        self.plik("assets/processed/A.png", _png(10, 10))
        self.manifest({"A": {"processed": "assets/processed/A.png"}})
        pierwszy = self.asset("A")
        pelna = self.plik("assets/processed/A.png", _png(20, 12))
        st = os.stat(pelna)
        os.utime(pelna, ns=(st.st_atime_ns, st.st_mtime_ns + 3_000_000_000))
        drugi = self.asset("A")
        self.assertEqual((pierwszy["wymiary"], drugi["wymiary"]), ([10, 10], [20, 12]))
        self.assertNotEqual(pierwszy["obraz"], drugi["obraz"])


# --------------------------------------------------------------------------- pliki obrazów i bezpieczeństwo ścieżek
class TestPliki(Baza):
    def setUp(self):
        super().setUp()
        self.app = Aplikacja()
        assety.zarejestruj(self.app)

    def trasa(self, sciezka, metoda="GET"):
        """Jak serwer: dopasowanie trasy z dekodowaniem %XX, potem wywołanie."""
        fn, params = self.app.znajdz(metoda, sciezka)
        if fn is None:
            return None
        z = zadanie(sciezka=sciezka)
        z.params = params
        return fn(z)

    def kod_bledu(self, sciezka):
        try:
            wynik = self.trasa(sciezka)
        except BladHTTP as e:
            return e.status
        return 404 if wynik is None else 200

    def test_obraz_pod_nazwa_i_z_rozszerzeniem(self):
        self.plik("assets/processed/Teleport.png", PNG)
        self.plik("assets/processed/pety/Smok Maly.JPG", b"\xff\xd8\xff\xe0" + b"\x00" * 30)
        self.manifest({"Teleport": {"processed": "assets/processed/Teleport.png"},
                       "Smok Mały": {"processed": "assets\\processed\\pety\\Smok Maly.JPG"},
                       "Ikona.v2": {"processed": "./assets/processed/Teleport.png"}})
        for sciezka in ("/api/assety/plik/Teleport", "/api/assety/plik/Teleport.png", "/api/assety/plik/Teleport.webp",
                        "/api/assety/plik/Ikona.v2", "/api/assety/plik/Ikona.v2.png"):
            odp = self.trasa(sciezka)
            self.assertIsInstance(odp, Odp, sciezka)
            self.assertEqual(os.path.realpath(odp.plik_sciezka),
                             os.path.realpath(os.path.join(self.repo, "assets", "processed", "Teleport.png")))
            self.assertEqual((odp.mime, odp.status), ("image/png", 200))
            self.assertIn("max-age", odp.naglowki["Cache-Control"])
        smok = self.asset("Smok Mały")
        self.assertRegex(smok["obraz"], r"^/api/assety/plik/Smok%20Ma%C5%82y\.jpg\?v=\d+$")
        self.assertEqual(smok["plik"], "assets/processed/pety/Smok Maly.JPG")
        odp = self.trasa(smok["obraz"].split("?")[0])                # adres z rejestru prowadzi do pliku
        self.assertEqual(odp.mime, "image/jpeg")
        self.assertTrue(odp.plik_sciezka.endswith("Smok Maly.JPG"))
        self.assertEqual(self.asset("Ikona.v2")["plik"], "assets/processed/Teleport.png")

    def test_tylko_odczyt(self):
        self.assertTrue(self.app.lista_tras())
        self.assertEqual({t["metoda"] for t in self.app.lista_tras()}, {"GET"})
        for sciezka in ("/api/assety", "/api/assety/plik/Teleport", "/api/assety/miniatura/Teleport"):
            self.assertEqual(self.app.znajdz("POST", sciezka), (None, "metoda"), sciezka)
        self.plik("assets/processed/Teleport.png", _png(500, 400, szum=True))
        self.plik("assets/raw/Teleport/v1_1.png", PNG)
        self.manifest({"Teleport": {"status": "approved", "processed": "assets/processed/Teleport.png",
                                    "approved_by_user": True, "approved_sha256": "a" * 64},
                       "Plan": {"status": "planned"}})
        przed = self.stan_dysku()
        self.trasa("/api/assety")
        self.trasa("/api/assety/plik/Teleport.png")
        self.trasa("/api/assety/miniatura/Teleport.webp")
        assety.zdrowie()
        self.assertEqual(self.stan_dysku(), przed)                   # nic nie powstało, nic się nie zmieniło
        self.assertFalse(os.path.exists(rdzen.DANE))

    def test_zlosliwe_sciezki_w_manifescie(self):
        poza = os.path.join(self.tmp, "poza.png")
        with open(poza, "wb") as f:
            f.write(PNG)
        self.plik("assets/raw/Tajny/v1_1.png")
        self.plik("assets/luzem.png")
        self.plik("assets/processed/tajne.txt", b"sekret")
        self.plik("assets/processed/ok.png")
        self.plik(".env", b"ROBLOX_API_KEY=x")
        zle = {
            "WGore": "../poza.png", "DwaRazy": "../../poza.png", "WGoreIWDol": "../repo/assets/processed/ok.png",
            "PrzezProcessed": "assets/processed/../raw/Tajny/v1_1.png",
            "Glebiej": "assets/processed/a/../../raw/Tajny/v1_1.png",
            "Raw": "assets/raw/Tajny/v1_1.png", "RawWindows": "assets\\raw\\Tajny\\v1_1.png",
            "ObokProcessed": "assets/luzem.png",
            "Bezwzgledna": poza, "BezwzglednaWRepo": os.path.join(self.repo, "assets", "processed", "ok.png"),
            "Dysk": "C:/Windows/win.ini", "Unix": "/etc/passwd", "Siec": "\\\\serwer\\udzial\\a.png",
            "Strumien": "assets/processed/ok.png:tajne", "Zero": "assets/processed/ok.png\x00.txt",
            "NieObraz": "assets/processed/tajne.txt", "Env": ".env", "Manifest": "assets/manifest.json",
            "SamKatalog": "assets/processed", "Kropka": "assets/processed/ok.png.",
            "Procenty": "assets/processed/%2e%2e/%2e%2e/.env",
            "ProcentyObraz": "assets/processed/%2e%2e/%2e%2e/luzem.png/..",
        }
        self.manifest({n: {"status": "processed", "processed": p} for n, p in zle.items()})
        r = assety.rejestr()
        self.assertEqual(len(r["assety"]), len(zle))
        for a in r["assety"]:
            self.assertIsNone(a["obraz"], a["nazwa"])
            self.assertIsNone(a["miniatura"], a["nazwa"])
            self.assertTrue(a.get("uwagi"), a["nazwa"])
        self.assertEqual(assety.zdrowie()["bez_obrazu"], len(zle))
        tresc = json.dumps(r)
        self.assertNotIn("ROBLOX_API_KEY", tresc)
        for nazwa in zle:
            for rodzaj in ("plik", "miniatura"):
                self.assertEqual(self.kod_bledu("/api/assety/%s/%s" % (rodzaj, nazwa)), 403, (nazwa, rodzaj))
        # wartości, które nie są tekstem: brak obrazu, bez wywracania się
        self.manifest({"Liczba": {"processed": 5}, "Lista": {"processed": ["assets/processed/ok.png"]},
                       "Slownik": {"processed": {"a": 1}}, "Pusty": {"processed": "  "}})
        for a in assety.rejestr()["assety"]:
            self.assertIsNone(a["obraz"])
            self.assertEqual(self.kod_bledu("/api/assety/plik/" + a["nazwa"]), 404)
        # zapis niechlujny, ale uczciwy (spacje na końcach, „./”, ukośniki Windows) prowadzi do właściwego pliku
        self.manifest({"Spacje": {"processed": "  ./assets\\processed/ok.png  "}})
        self.assertEqual(self.asset("Spacje")["plik"], "assets/processed/ok.png")
        odp = self.trasa("/api/assety/plik/Spacje")
        self.assertEqual(os.path.realpath(odp.plik_sciezka),
                         os.path.realpath(os.path.join(self.repo, "assets", "processed", "ok.png")))

    def test_dowiazania_poza_katalog_obrazow(self):
        poza = os.path.join(self.tmp, "poza.png")
        with open(poza, "wb") as f:
            f.write(PNG)
        self.plik("assets/raw/Tajny.png")
        try:
            os.symlink(poza, os.path.join(self.repo, "assets", "processed", "NaZewnatrz.png"))
            os.symlink(os.path.join(self.repo, "assets", "raw", "Tajny.png"),
                       os.path.join(self.repo, "assets", "processed", "DoRaw.png"))
        except (OSError, NotImplementedError):
            self.skipTest("ten system nie pozwala tworzyć dowiązań bez uprawnień administratora")
        self.manifest({"NaZewnatrz": {"processed": "assets/processed/NaZewnatrz.png"},
                       "DoRaw": {"processed": "assets/processed/DoRaw.png"}})
        for a in assety.rejestr()["assety"]:
            self.assertIsNone(a["obraz"], a["nazwa"])
            self.assertEqual(self.kod_bledu("/api/assety/plik/" + a["nazwa"]), 403)

    def test_zlosliwe_nazwy_w_adresie(self):
        self.plik("assets/processed/Teleport.png")
        self.plik("assets/raw/Teleport.png")
        self.manifest({"Teleport": {"processed": "assets/processed/Teleport.png"}, "BezObrazu": {"status": "planned"},
                       "..": {"processed": "assets/processed/Teleport.png"},
                       "a/b": {"processed": "assets/processed/Teleport.png"},
                       "100%": {"processed": "assets/processed/Teleport.png"}})
        for nazwa in ("..", "%2e%2e", "..%2Fmanifest.json", "..%5C..%5Cmanifest.json",
                      "Teleport%2F..%2F..%2Fraw%2FTeleport.png", "..%2Fraw%2FTeleport.png", "manifest.json", "Nieznany", "Nieznany.png", "Teleport.txt",
                      "Teleport.png.png", "teleport", "Teleport%00.png", "BezObrazu", "BezObrazu.png", "a%2Fb", "raw"):
            for rodzaj in ("plik", "miniatura"):
                self.assertEqual(self.kod_bledu("/api/assety/%s/%s" % (rodzaj, nazwa)), 404, (rodzaj, nazwa))
        self.assertEqual(self.kod_bledu("/api/assety/plik/"), 404)
        self.assertEqual(self.kod_bledu("/api/assety/plik/Teleport/x"), 404)
        # nazwy, których nie da się bezpiecznie włożyć do adresu, nie dostają adresu obrazu
        for nazwa in ("..", "a/b", "100%"):
            a = self.asset(nazwa)
            self.assertIsNone(a["obraz"], nazwa)
            self.assertIn("znaki", a["uwagi"][0])
            self.assertTrue(a["cel_komentarzy"].startswith("assets/"))
        self.assertEqual(self.kod_bledu("/api/assety/plik/Teleport"), 200)

    def test_nazwa_z_rozszerzeniem_nie_przejmuje_cudzego_obrazu(self):
        """Asset „Coin” ma adres …/plik/Coin.png. Gdy w manifeście jest też asset o nazwie „Coin.png” (z innym plikiem),
        ten adres nadal musi prowadzić do obrazu „Coin”, a „Coin.png” dostaje własny adres …/Coin.png.png."""
        self.plik("assets/processed/Coin.png", _png(5, 5))
        self.plik("assets/processed/Inny.png", _png(9, 9))
        self.manifest({"Coin": {"processed": "assets/processed/Coin.png"},
                       "Coin.png": {"processed": "assets/processed/Inny.png"}})
        for nazwa, plik in (("Coin", "Coin.png"), ("Coin.png", "Inny.png")):
            a = self.asset(nazwa)
            for pole in ("obraz", "miniatura"):
                odp = self.trasa(a[pole].split("?")[0])
                if odp.plik_sciezka:
                    self.assertEqual(os.path.basename(odp.plik_sciezka), plik, (nazwa, pole, a[pole]))
        self.assertTrue(self.trasa("/api/assety/plik/Coin").plik_sciezka.endswith("Coin.png"))

    def test_nazwy_niedozwolone_w_pliku_na_windows(self):
        """Lustro zapisuje obraz pod nazwą z adresu: „Ikona:2.png” na NTFS to strumień pliku „Ikona”, a „*” i „|”
        to błąd zapisu. Takie nazwy nie dostają adresu obrazu (uwaga zamiast niego), reszta działa."""
        self.plik("assets/processed/ok.png")
        zle = ("Ikona:2", "a*b", "a|b", 'a"b', "a<b", "a>b", "Kropka.")
        self.manifest(dict({n: {"processed": "assets/processed/ok.png"} for n in zle},
                           Dobra={"processed": "assets/processed/ok.png"}))
        for nazwa in zle:
            a = self.asset(nazwa)
            self.assertEqual((a["obraz"], a["miniatura"]), (None, None), nazwa)
            self.assertIn("znaki", a["uwagi"][0])
            self.assertEqual(self.kod_bledu("/api/assety/plik/" + urllib.parse.quote(nazwa)), 404, nazwa)
        self.assertTrue(self.asset("Dobra")["obraz"])
        wyj = os.path.join(self.tmp, "lustro")
        app = Aplikacja()
        assety.zarejestruj(app)
        stat = statyczny.eksportuj(app, wyj)
        self.assertEqual([b for b in stat["bledy"] if "assety" in b], [])
        self.assertEqual(os.listdir(os.path.join(wyj, "api", "assety", "plik")), ["Dobra.png"])

    def test_wymiary_z_naglowkow(self):
        w = assety.wymiary_obrazu
        self.assertEqual(w(self.plik("a.png", _png(7, 5))), (7, 5))
        self.assertEqual(w(self.plik("a.gif", b"GIF89a" + struct.pack("<HH", 12, 9) + b"\x00" * 20)), (12, 9))
        jpg = (b"\xff\xd8" + b"\xff\xe0" + struct.pack(">H", 16) + b"JFIF\x00" + b"\x00" * 9
               + b"\xff\xdb" + struct.pack(">H", 4) + b"\x00\x00" + b"\xff\xff"
               + b"\xff\xc2" + struct.pack(">HBHHB", 11, 8, 33, 44, 1) + b"\x00" * 3 + b"\xff\xd9")
        self.assertEqual(w(self.plik("a.jpg", jpg)), (44, 33))

        def riff(rodzaj, dane):
            return (b"RIFF" + struct.pack("<I", 4 + 8 + len(dane)) + b"WEBP" + rodzaj
                    + struct.pack("<I", len(dane)) + dane)

        vp8x = riff(b"VP8X", b"\x10\x00\x00\x00" + (299).to_bytes(3, "little") + (199).to_bytes(3, "little"))
        self.assertEqual(w(self.plik("a.webp", vp8x)), (300, 200))
        vp8l = riff(b"VP8L", b"\x2f" + ((64 - 1) | ((48 - 1) << 14)).to_bytes(4, "little") + b"\x00" * 6)
        self.assertEqual(w(self.plik("b.webp", vp8l)), (64, 48))
        vp8 = riff(b"VP8 ", b"\x00\x00\x00\x9d\x01\x2a" + struct.pack("<HH", 320, 240) + b"\x00" * 4)
        self.assertEqual(w(self.plik("c.webp", vp8)), (320, 240))
        for nazwa, dane in (("pusty.png", b""), ("smiec.png", b"to nie obraz" * 5), ("uciety.png", PNG[:12]),
                            ("zero.png", _png(1, 1)[:16] + struct.pack(">II", 0, 0) + b"\x00" * 20),
                            ("bez_ramki.jpg", b"\xff\xd8\xff\xd9")):
            self.assertIsNone(w(self.plik(nazwa, dane)), nazwa)
        self.assertIsNone(w(os.path.join(self.repo, "nie-ma.png")))

    def test_bez_pillow_miniatura_to_pelny_plik(self):
        assety._pil.update(sprawdzono=True, format=None)             # udajemy komputer bez Pillow
        self.plik("assets/processed/Tlo.png", _png(600, 400, szum=True))
        self.manifest({"Tlo": {"processed": "assets/processed/Tlo.png"}})
        a = self.asset("Tlo")
        self.assertEqual(a["miniatura"], a["obraz"])
        odp = self.trasa("/api/assety/miniatura/Tlo.png")
        self.assertTrue(odp.plik_sciezka.endswith("Tlo.png"))
        self.assertEqual(odp.mime, "image/png")

    @unittest.skipIf(Image is None, "Pillow nie jest zainstalowany (opcjonalny)")
    def test_miniatura_z_pillow(self):
        assety._pil.update(sprawdzono=False, format=None)
        duzy = _png(800, 500, szum=True)
        self.plik("assets/processed/Tlo.png", duzy)
        self.plik("assets/processed/Ikona.png", _png(200, 200, alfa=True, szum=True))
        self.plik("assets/processed/Zepsuty.png", PNG[:20] + b"\x00" * 3000)
        self.manifest({"Tlo": {"processed": "assets/processed/Tlo.png"}, "Ikona": {"processed": "assets/processed/Ikona.png"},
                       "Zepsuty": {"processed": "assets/processed/Zepsuty.png"}})
        fmt = assety.format_miniatur()
        self.assertIn(fmt, ("webp", "png"))
        a = self.asset("Tlo")
        self.assertRegex(a["miniatura"], r"^/api/assety/miniatura/Tlo\.%s\?v=\d+$" % fmt)
        self.assertNotEqual(a["miniatura"], a["obraz"])
        odp = self.trasa(a["miniatura"].split("?")[0])
        self.assertIsNone(odp.plik_sciezka)
        self.assertEqual(odp.mime, "image/" + fmt)
        self.assertLess(len(odp.cialo), len(duzy))
        with Image.open(io.BytesIO(odp.cialo)) as obraz:
            self.assertEqual(max(obraz.size), assety.BOK_MINIATURY)
            self.assertEqual(obraz.size, (384, 240))
        self.assertIs(self.trasa(a["miniatura"].split("?")[0]).cialo, odp.cialo)      # druga prośba z pamięci
        if fmt == "webp":                                             # mała ikona: bez zmiany rozmiaru, z przezroczystością
            odp = self.trasa("/api/assety/miniatura/Ikona.webp")
            with Image.open(io.BytesIO(odp.cialo)) as obraz:
                self.assertEqual(obraz.size, (200, 200))
                self.assertEqual(obraz.mode, "RGBA")
        zepsuty = self.trasa("/api/assety/miniatura/Zepsuty.webp")   # nieczytelny obraz: oddajemy plik bez zmian
        self.assertTrue(zepsuty.plik_sciezka.endswith("Zepsuty.png"))

    @unittest.skipIf(Image is None, "Pillow nie jest zainstalowany (opcjonalny)")
    def test_miniatura_nie_rozpakowuje_olbrzymow(self):
        """Mały plik z nagłówkiem „20000 × 20000 px” rozpakowałby się do ok. 1,6 GB w pamięci serwera. Wymiary
        sprawdzamy przed odczytem pikseli (tu z obniżonym limitem): bez miniatury, oddajemy plik bez zmian."""
        stary = assety.LIMIT_PIKSELI_MINIATURY
        assety.LIMIT_PIKSELI_MINIATURY = 30 * 30
        try:
            assety._pil.update(sprawdzono=False, format=None)
            self.plik("assets/processed/Wielki.png", _png(40, 40, szum=True))
            self.plik("assets/processed/Maly.png", _png(20, 20, szum=True))
            self.manifest({"Wielki": {"processed": "assets/processed/Wielki.png"},
                           "Maly": {"processed": "assets/processed/Maly.png"}})
            fmt = assety.format_miniatur()
            wielki = self.trasa("/api/assety/miniatura/Wielki." + fmt)
            self.assertTrue(wielki.plik_sciezka and wielki.plik_sciezka.endswith("Wielki.png"))
            if fmt == "webp":                                         # mały obraz nadal dostaje miniaturę
                self.assertIsNone(self.trasa("/api/assety/miniatura/Maly.webp").plik_sciezka)
        finally:
            assety.LIMIT_PIKSELI_MINIATURY = stary


# --------------------------------------------------------------------------- na żywo: znacznik wersji i strumień zdarzeń
class TestNaZywo(Baza):
    def przesun(self, pelna, s=5):
        st = os.stat(pelna)
        os.utime(pelna, ns=(st.st_atime_ns, st.st_mtime_ns + s * 1_000_000_000))

    def test_sygnatura_z_samych_metadanych(self):
        self.manifest({"A": {"status": "planned"}})
        s1 = assety.sygnatura(swieza=True)
        self.assertRegex(s1, r"^[0-9a-f]{16}$")
        self.assertEqual(assety.sygnatura(swieza=True), s1)                     # bez zmian — ten sam znacznik
        obraz = self.plik("assets/processed/ClassSelect/CsBg1.png")               # nowa grafika w podkatalogu
        s2 = assety.sygnatura(swieza=True)
        self.assertNotEqual(s2, s1)
        self.plik("assets/processed/ClassSelect/CsBg1.png", _png(4, 3))          # podmiana: ten sam rozmiar…
        self.przesun(obraz)                                                       # …inny czas zmiany
        s3 = assety.sygnatura(swieza=True)
        self.assertNotEqual(s3, s2)
        self.przesun(self.manifest({"A": {"status": "planned"}, "B": {"status": "done"}}))
        s4 = assety.sygnatura(swieza=True)
        self.assertNotEqual(s4, s3)
        self.plik("assets/raw/CsBg1/v1.png")                                     # surowe warianty się nie liczą
        self.assertEqual(assety.sygnatura(swieza=True), s4)
        with mock.patch("builtins.open", side_effect=AssertionError("znacznik nie może czytać plików")):
            self.assertEqual(assety.sygnatura(swieza=True), s4)
        self.przesun(self.manifest({"C": {"status": "planned"}}), 9)
        self.assertEqual(assety.sygnatura(), s4)                                   # wspólna pamięć 1,5 s
        self.assertNotEqual(assety.sygnatura(swieza=True), s4)
        os.remove(os.path.join(self.repo, "assets", "manifest.json"))
        shutil.rmtree(os.path.join(self.repo, "assets", "processed"))
        self.assertRegex(assety.sygnatura(swieza=True), r"^[0-9a-f]{16}$")      # brak plików to nie błąd

    def test_wersja_rejestru_i_wersje_assetow(self):
        obraz = self.plik("assets/processed/A.png")
        self.manifest({"A": {"status": "processed", "processed": "assets/processed/A.png"}, "B": {"status": "planned"}},
                      updated_at="2026-11-16T19:23:14+00:00")
        r1 = assety.rejestr()
        self.assertEqual(r1["wersja"], assety.sygnatura(swieza=True))
        self.assertEqual(r1["zaktualizowano"], "2026-11-16T19:23:14+00:00")        # czas z rejestru, nie z dysku
        self.assertTrue(r1["na_dysku"])
        w1 = {a["nazwa"]: a["wersja"] for a in r1["assety"]}
        self.assertTrue(all(re.fullmatch(r"[0-9a-f]{12}", w) for w in w1.values()), w1)
        self.przesun(self.manifest({"A": {"status": "processed", "processed": "assets/processed/A.png"},
                                    "B": {"status": "generated"}}))
        r2 = assety.rejestr()
        w2 = {a["nazwa"]: a["wersja"] for a in r2["assety"]}
        self.assertNotEqual(r2["wersja"], r1["wersja"])
        self.assertEqual(w2["A"], w1["A"])                                        # wpis A bez zmian
        self.assertNotEqual(w2["B"], w1["B"])
        self.plik("assets/processed/A.png", _png(6, 6))                          # obraz podmieniony bez zmiany wpisu
        self.przesun(obraz)
        w3 = {a["nazwa"]: a["wersja"] for a in assety.rejestr()["assety"]}
        self.assertNotEqual(w3["A"], w2["A"])
        self.assertEqual(w3["B"], w2["B"])

    def test_strumien_zmiana_puls_i_stan_gita(self):
        self.manifest({"A": {"status": "planned"}})
        gen = assety.zdarzenia(co_ile_s=0.01, puls_s=0.05, czas_s=30)
        try:
            z1 = next(gen)
            self.assertEqual((z1["typ"], z1["git"]), ("assety", None))
            self.assertEqual(z1["wersja"], assety.sygnatura(swieza=True))
            self.assertEqual(assety._strumienie["n"], 1)
            self.przesun(self.manifest({"A": {"status": "planned"}, "B": {"status": "planned"}}))
            assety._sygnatura.update(wartosc=None)                               # bez czekania 1,5 s na pamięć
            z2 = next(gen)
            self.assertEqual(z2["typ"], "assety")
            self.assertNotEqual(z2["wersja"], z1["wersja"])
            self.assertEqual(next(gen), {"typ": "puls"})                          # cisza — znak, że łącze żyje
            g = {"ile": 2, "od": "2026-11-16T21:25:40+01:00", "assety": True, "stan": "czeka", "krotko": "lokalne zmiany w 1 pliku"}
            with mock.patch.object(assety, "_stan_gita", lambda: dict(g)):
                z3 = next(gen)
            self.assertEqual((z3["typ"], z3["git"], z3["wersja"]), ("assety", g, z2["wersja"]))
            self.assertEqual(next(gen)["git"], None)                             # pobrane — pasek znika
        finally:
            gen.close()
        self.assertEqual(assety._strumienie["n"], 0)

    def test_strumien_konczy_sie_po_czasie_i_przy_limicie(self):
        self.manifest({"A": {"status": "planned"}})
        zdarzenia = list(assety.zdarzenia(co_ile_s=0.01, puls_s=60, czas_s=0.05))
        self.assertEqual(zdarzenia[0]["typ"], "assety")
        self.assertEqual(zdarzenia[-1], {"typ": "koniec", "powod": "czas"})
        self.assertEqual(assety._strumienie["n"], 0)
        with mock.patch.object(assety, "MAKS_STRUMIENI", 1):
            g1 = assety.zdarzenia(co_ile_s=0.01)
            self.assertEqual(next(g1)["typ"], "assety")
            self.assertEqual(list(assety.zdarzenia(co_ile_s=0.01)), [{"typ": "koniec", "powod": "limit"}])
            g1.close()
            g3 = assety.zdarzenia(co_ile_s=0.01)
            self.assertEqual(next(g3)["typ"], "assety")                           # miejsce się zwolniło
            g3.close()
        self.assertEqual(assety._strumienie["n"], 0)

    def test_trasa_zdarzen_i_stan_gita_z_synchronizacji(self):
        app = Aplikacja()
        assety.zarejestruj(app)
        fn, _ = app.znajdz("GET", "/api/assety/zdarzenia")
        wynik = fn(zadanie(sciezka="/api/assety/zdarzenia"))
        self.assertIsInstance(wynik, Strumien)
        wynik.generator.close()                                                  # nieuruchomiony — nic nie zajmuje
        self.assertEqual(assety._strumienie["n"], 0)
        from bc import gitsync
        klucz = os.path.normpath(self.repo)
        gitsync._auto[klucz] = dict(gitsync._nowy_stan(), stan="czeka", krotko="lokalne zmiany w 1 pliku",
                                    do_pobrania=3, do_pobrania_od="2026-11-16T21:25:40+01:00", do_pobrania_assety=True)
        try:
            self.assertEqual(assety._stan_gita(), {"ile": 3, "od": "2026-11-16T21:25:40+01:00", "assety": True,
                                                   "stan": "czeka", "krotko": "lokalne zmiany w 1 pliku"})
            gitsync._auto[klucz]["do_pobrania"] = 0
            self.assertIsNone(assety._stan_gita())
        finally:
            gitsync._auto.pop(klucz, None)


# --------------------------------------------------------------------------- lustro tylko do odczytu i komentarze
class TestLustro(Baza):
    def test_eksport_rejestru_obrazow_i_komentarzy(self):
        self.plik("assets/processed/Teleport.png", _png(30, 30, alfa=True))
        self.plik("assets/processed/Tlo.png", _png(700, 420, szum=True))
        self.plik("assets/raw/Teleport/v1_1.png")
        self.manifest({"Teleport": {"status": "awaiting_approval", "processed": "assets/processed/Teleport.png"},
                       "Tlo": {"status": "done", "processed": "assets/processed/Tlo.png", "roblox_image": "5"},
                       "Plan": {"status": "planned"},
                       "Zly": {"status": "processed", "processed": "assets/raw/Teleport/v1_1.png"}})
        app = Aplikacja()
        assety.zarejestruj(app)
        raporty.zarejestruj(app)
        k = raporty.dodaj_komentarz({"typ": "plik", "cel": "assets/processed/Teleport.png", "etykieta": "Teleport"},
                                    "Za ciemny obrys", "Paweł")
        self.assertEqual(k["cel"]["typ"], "plik")
        wyj = os.path.join(self.tmp, "lustro")
        stat = statyczny.eksportuj(app, wyj)
        self.assertEqual([b for b in stat["bledy"] if "assety" in b], [])

        def dane(sciezka):
            with open(os.path.join(wyj, "dane", statyczny.klucz(sciezka) + ".json"), encoding="utf-8") as f:
                return json.load(f)

        r = dane("/api/assety")
        self.assertEqual([a["nazwa"] for a in r["assety"]], ["Teleport", "Tlo", "Plan", "Zly"])
        self.assertEqual(r["czeka"], 1)
        for a in r["assety"]:
            for pole in ("obraz", "miniatura"):
                if a[pole]:                                           # plik leży pod tą samą ścieżką co w API
                    self.assertTrue(os.path.isfile(os.path.join(wyj, *a[pole].split("?")[0].strip("/").split("/"))), a[pole])
        with open(os.path.join(wyj, "api", "assety", "plik", "Teleport.png"), "rb") as f:
            self.assertEqual(f.read(), _png(30, 30, alfa=True))
        self.assertIsNone(r["assety"][3]["obraz"])
        self.assertFalse(os.path.exists(os.path.join(wyj, "api", "assety", "plik", "Zly.png")))
        wszystkie = [os.path.join(k2, p) for k2, _, pliki in os.walk(os.path.join(wyj, "api")) for p in pliki]
        self.assertFalse([p for p in wszystkie if "raw" in p or "v1_1" in p], "do lustra nie trafia nic z assets/raw")
        watek = dane("/api/komentarze?typ=plik&cel=" + statyczny.enc("assets/processed/Teleport.png"))
        self.assertEqual([x["tekst"] for x in watek["komentarze"]], ["Za ciemny obrys"])
        self.assertEqual(dane("/api/komentarze?typ=plik&cel=" + statyczny.enc("assets/processed/Plan.png")),
                         {"komentarze": []})
        self.assertEqual(len(dane("/api/komentarze?typ=plik")["komentarze"]), 1)


if __name__ == "__main__":
    unittest.main()
