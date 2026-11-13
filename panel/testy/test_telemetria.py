# -*- coding: utf-8 -*-
"""Testy telemetrii gry (panel/bc/telemetria.py): kubełki godzinowe, odczyt z Open Cloud, sekrety, dane przykładowe.

Uruchomienie (z katalogu panel/):  python -m unittest testy.test_telemetria
Bez sieci: jedyne wyjście do Roblox (`telemetria._otworz`) jest podmieniane atrapą. Konfiguracja i log są
podstawiane w pamięci — prawdziwe dane lokalne komputera zostają nietknięte.
"""
import io
import json
import os
import re
import shutil
import socket
import sys
import tempfile
import unittest
import urllib.error
import urllib.parse

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(PANEL)
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import rdzen, statyczny, telemetria  # noqa: E402
from bc.http import Zadanie  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

KLUCZ = "tajny-klucz-open-cloud-DoTestow-0123456789"
UID = 4242
TERAZ = 1794549000                                             # 2026-11-13 05:50:00 UTC
H5 = 1794546000                                                # początek godziny 05:00 UTC
H4 = H5 - 3600


def kubelek(**pola):
    """Surowy kubełek w formacie zapisywanym przez grę (Agregator.luau)."""
    k = {"wersja": 1, "t": H5, "zaktualizowano": H5 + 60, "serwery": 1, "zapisy": 1, "starty": 0, "sesje": 0,
         "sesje_zakonczone": 0, "sekundy_gry": 0, "ccu_max": 0, "ccu_suma": 0, "ccu_probki": 0, "ccu_minuty": [0] * 60,
         "robuxy": 0, "bledy_n": 0, "dlugosci": [], "zakupy": [], "bledy": [], "zdarzenia": [], "lejek": [],
         "zamkniecia": []}                                     # puste tabele Luau przychodzą jako []
    k.update(pola)
    return k


class Odpowiedz:
    """Atrapa odpowiedzi HTTP (to, co zwraca urlopen)."""

    def __init__(self, obj, surowe=None):
        self._bajty = surowe if surowe is not None else json.dumps(obj).encode("utf-8")
        self.status = 200

    def read(self, n=-1):
        return self._bajty if n is None or n < 0 else self._bajty[:n]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def blad_http(url, kod, cialo=b"{}"):
    return urllib.error.HTTPError(url, kod, "blad", {}, io.BytesIO(cialo))


class OpenCloud:
    """Atrapa Open Cloud: wpisy Data Store i serwery Memory Store ze słowników; pamięta każde żądanie."""

    def __init__(self, wpisy=None, serwery=None):
        self.wpisy = dict(wpisy or {})
        self.serwery = serwery
        self.zadania = []
        self.awaria = None                                     # funkcja(url) -> wyjątek albo None
        self.awaria_serwerow = None

    def __call__(self, zadanie, limit_czasu):
        self.zadania.append(zadanie)
        url = zadanie.full_url
        sciezka = urllib.parse.urlsplit(url).path
        if self.awaria:
            wyjatek = self.awaria(url)
            if wyjatek:
                raise wyjatek
        m = re.search(r"/data-stores/([^/]+)/entries/([^/]+)$", sciezka)
        if m:
            nazwa = urllib.parse.unquote(m.group(2))
            if nazwa not in self.wpisy:
                raise blad_http(url, 404, b'{"code":"NOT_FOUND","message":"Entry not found."}')
            return Odpowiedz({"path": sciezka, "id": nazwa, "state": "ACTIVE", "value": self.wpisy[nazwa]})
        if "/memory-store/sorted-maps/" in sciezka:
            if self.awaria_serwerow:
                raise self.awaria_serwerow(url)
            if self.serwery is None:
                raise blad_http(url, 404)
            return Odpowiedz({"items": self.serwery})
        raise blad_http(url, 400)

    def sciezki(self):
        return [urllib.parse.urlsplit(z.full_url).path for z in self.zadania]


class Baza(unittest.TestCase):
    def setUp(self):
        self.cfg = {"gra": {"universeId": UID}, "analityka": {}}
        self.log = []
        self._stare = (rdzen.konfiguracja, rdzen.log, telemetria._otworz, os.environ.get(telemetria.ZMIENNA_KLUCZA))
        rdzen.konfiguracja = lambda: self.cfg
        rdzen.log = lambda *czesci: self.log.append(" ".join(str(c) for c in czesci))
        os.environ.pop(telemetria.ZMIENNA_KLUCZA, None)
        self.oc = OpenCloud()
        telemetria._otworz = self.oc
        telemetria._pamiec.clear()
        telemetria._godziny.clear()
        telemetria._zapytania.clear()                          # ogranicznik żądań liczy od zera w każdym teście

    def tearDown(self):
        rdzen.konfiguracja, rdzen.log, telemetria._otworz, klucz = self._stare
        if klucz is None:
            os.environ.pop(telemetria.ZMIENNA_KLUCZA, None)
        else:
            os.environ[telemetria.ZMIENNA_KLUCZA] = klucz
        telemetria._pamiec.clear()
        telemetria._godziny.clear()

    def z_kluczem(self):
        self.cfg["analityka"]["klucz_open_cloud"] = KLUCZ

    def dzialajaca_gra(self):
        """Gra z włączonym modułem: ślad „stan”, dwie godziny danych, dwa serwery na żywo."""
        self.z_kluczem()
        self.oc.wpisy = {
            "stan": {"wersja": 1, "pierwszy_start": H4 - 86400, "ostatni_start": H5 + 300, "starty": 7},
            telemetria.klucz_godziny(H4): kubelek(
                t=H4, sesje=10, sesje_zakonczone=8, sekundy_gry=4800, ccu_max=6, ccu_minuty=[4] * 30 + [9] * 30,
                robuxy=500, starty=2, bledy_n=3,
                zakupy={"111": {"n": 2, "robuxy": 400, "nazwa": "Skrzynia"}, "222": {"n": 1, "robuxy": 100, "nazwa": "Worek"}},
                bledy={"aaaa1111": {"n": 3, "komunikat": "Server.Walka:42: attempt to index nil"}},
                dlugosci={"do_1": 2, "do_15": 6}, zamkniecia={"ServerEmpty": 1}),
            telemetria.klucz_godziny(H5): kubelek(
                t=H5, sesje=4, sesje_zakonczone=2, sekundy_gry=1200, ccu_max=5, ccu_minuty=[5] * 50 + [0] * 10,
                robuxy=100, bledy_n=1, zakupy={"222": {"n": 1, "robuxy": 100, "nazwa": "Worek złota"}},
                bledy={"bbbb2222": {"n": 1, "komunikat": "Server.Pety:7: błąd"}}),
        }
        self.oc.serwery = [
            {"id": "7c1e5a90-3b1f-4c0e-9a51-0d6f2b8e1a11", "value": {"gracze": 3, "od": H4 + 100, "pamiec_mb": 900.4, "fps": 59.94}},
            {"id": "e04b77d2-91aa-4f6d-8c3e-5a2d90c4b7f3", "value": {"gracze": 5, "od": H5 + 300, "bledy": 2}},
        ]


# --------------------------------------------------------------------------- czas i klucze wpisów
class TestCzas(unittest.TestCase):
    def test_klucz_godziny_jest_w_utc(self):
        self.assertEqual(telemetria.klucz_godziny(0), "g_19700101_00")
        self.assertEqual(telemetria.klucz_godziny(TERAZ), "g_20261113_05")
        self.assertEqual(telemetria.klucz_godziny(H5), "g_20261113_05")
        self.assertEqual(telemetria.klucz_godziny(H5 - 1), "g_20261113_04")
        self.assertEqual(telemetria.klucz_godziny(1835395200), "g_20280229_00")     # rok przestępny
        self.assertEqual(telemetria.klucz_godziny(1798761599), "g_20261231_23")     # ostatnia godzina roku
        self.assertEqual(telemetria.klucz_godziny(1798761600), "g_20270101_00")

    def test_poczatki_godzin(self):
        p = telemetria.poczatki_godzin(3, TERAZ)
        self.assertEqual(p, [H5 - 7200, H4, H5])
        self.assertEqual(len(telemetria.poczatki_godzin(24, TERAZ)), 24)
        self.assertEqual(telemetria.poczatki_godzin(1, H5), [H5])


# --------------------------------------------------------------------------- parsowanie i sumowanie kubełków
class TestKubelki(unittest.TestCase):
    def test_normalizacja_nie_ufa_danym(self):
        for smiec in (None, [], "tekst", 5, {"sesje": "dużo", "zakupy": "x", "ccu_minuty": {"a": 1}}):
            k = telemetria.normalizuj_kubelek(smiec, H5)
            self.assertEqual((k["t"], k["sesje"], k["zakupy"], k["bledy"], k["ccu_minuty"]), (H5, 0, {}, {}, []))
        k = telemetria.normalizuj_kubelek({
            "sesje": 7.0, "robuxy": -50, "sekundy_gry": float("nan"), "ccu_max": {"t": "numeric", "v": "inf"},
            "bledy_n": True, "ccu_minuty": [1, "x", -3, 4.9] + [2] * 100,
            "zakupy": {"111": {"n": 2, "robuxy": 98, "nazwa": "Worek\nzłota " + "x" * 200}, "zle": 5, "": {"n": 1}},
            "bledy": {"abcd": {"n": "3", "komunikat": 17}},
            "zdarzenia": {"quest": 12, "zly": "x"}, "dlugosci": [], "lejek": {"1": {"n": 4, "nazwa": "Wejście"}},
        })
        self.assertEqual((k["sesje"], k["robuxy"], k["sekundy_gry"], k["ccu_max"], k["bledy_n"]), (7, 0, 0, 0, 0))
        self.assertEqual(len(k["ccu_minuty"]), 60)
        self.assertEqual(k["ccu_minuty"][:4], [1, 0, 0, 4])
        self.assertEqual(set(k["zakupy"]), {"111"})
        self.assertEqual(k["zakupy"]["111"]["robuxy"], 98)
        self.assertEqual(len(k["zakupy"]["111"]["nazwa"]), 80)
        self.assertNotIn("\n", k["zakupy"]["111"]["nazwa"])
        self.assertEqual(k["bledy"], {"abcd": {"n": 0, "komunikat": ""}})
        self.assertEqual(k["zdarzenia"], {"quest": 12.0, "zly": 0.0})
        self.assertEqual((k["dlugosci"], k["lejek"]), ({}, {"1": {"n": 4, "nazwa": "Wejście"}}))

    def test_limit_kluczy(self):
        duzo = {"p%04d" % i: {"n": 1, "robuxy": 1, "nazwa": "x"} for i in range(5000)}
        self.assertEqual(len(telemetria.normalizuj_kubelek({"zakupy": duzo})["zakupy"]), telemetria.LIMIT_KLUCZY)

    def test_sumowanie(self):
        a = telemetria.normalizuj_kubelek(kubelek(
            t=H4, sesje=10, sesje_zakonczone=8, sekundy_gry=4800, ccu_max=6, ccu_minuty=[4] * 30 + [9] * 30, robuxy=500,
            starty=2, bledy_n=5,
            zakupy={"111": {"n": 2, "robuxy": 400, "nazwa": "Skrzynia"}, "222": {"n": 1, "robuxy": 100, "nazwa": "Worek"},
                    "_inne": {"n": 4, "robuxy": 999}},
            bledy={"aaaa1111": {"n": 3, "komunikat": "Walka:42: nil"}, "_inne": {"n": 2}},
            dlugosci={"do_1": 2, "do_15": 6}, zamkniecia={"ServerEmpty": 1, "OutOfMemory": 1},
            lejek={"2": {"n": 6, "nazwa": "Bohater"}, "1": {"n": 10, "nazwa": "Wejście"}}, zdarzenia={"quest": 7}), H4)
        b = telemetria.normalizuj_kubelek(kubelek(
            t=H5, sesje=4, sesje_zakonczone=2, sekundy_gry=1200, ccu_max=5, ccu_minuty=[5] * 60, robuxy=100, bledy_n=1,
            zakupy={"222": {"n": 1, "robuxy": 100, "nazwa": "Worek złota"}},
            bledy={"aaaa1111": {"n": 1, "komunikat": ""}}, dlugosci={"do_1": 1}, zdarzenia={"quest": 2.5}), H5)
        poczatki = [H4 - 3600, H4, H5]                              # pierwsza godzina bez danych
        w = telemetria.zloz({H4: a, H5: b}, poczatki, serwery=[{"id": "s1", "gracze": 3, "od": None}])
        self.assertEqual(w["suma"]["sesje"], 14)
        self.assertEqual(w["suma"]["sredni_czas_sesji_s"], 600)     # 6000 s / 10 zakończonych sesji
        self.assertEqual(w["suma"]["ccu_max"], 9)                   # największa minuta, nie szczyt jednego serwera
        self.assertEqual(w["suma"]["robuxy"], 600)
        self.assertEqual(w["suma"]["zakupy"], 8)                    # 2 + 1 + 4 (pozostałe) + 1
        self.assertEqual(w["suma"]["bledy"], 6)
        self.assertEqual(w["suma"]["sesje_ponizej_minuty"], 3)
        self.assertEqual((w["suma"]["serwery_start"], w["suma"]["serwery_koniec"], w["suma"]["brak_pamieci"]), (2, 2, 1))
        self.assertEqual(w["suma"]["niedomkniete"], 0)              # 2 starty − 2 zamknięcia − 1 żywy, nie mniej niż 0
        self.assertEqual((w["suma"]["serwery_teraz"], w["suma"]["gracze_teraz"]), (1, 3))
        self.assertEqual([g["sesje"] for g in w["godziny"]], [0, 10, 4])
        self.assertEqual([g["ccu_max"] for g in w["godziny"]], [0, 9, 5])
        self.assertEqual([g["robuxy"] for g in w["godziny"]], [0, 500, 100])
        self.assertEqual([g["bledy"] for g in w["godziny"]], [0, 5, 1])
        self.assertTrue(all(set(g) == {"t", "sesje", "ccu_max", "robuxy", "bledy"} for g in w["godziny"]))
        self.assertEqual([z["id"] for z in w["zakupy"]], ["111", "222", "_inne"])       # wg Robuxów, „pozostałe” na końcu
        self.assertEqual(w["zakupy"][1], {"id": "222", "nazwa": "Worek złota", "n": 2, "robuxy": 200})   # nowsza nazwa
        self.assertEqual(w["zakupy"][2]["nazwa"], "Pozostałe produkty")
        self.assertEqual(w["bledy"][0], {"sygnatura": "aaaa1111", "n": 4, "komunikat": "Walka:42: nil"})
        self.assertEqual(w["bledy"][-1]["sygnatura"], "_inne")
        self.assertEqual([k["krok"] for k in w["lejek"]], [1, 2])
        self.assertEqual(w["zdarzenia"], [{"nazwa": "quest", "n": 9.5}])
        self.assertEqual(w["dlugosci_sesji"], {"do_1": 3, "do_15": 6})

    def test_puste_okno(self):
        w = telemetria.zloz({}, [H4, H5], serwery=None)
        self.assertEqual(w["suma"]["sesje"], 0)
        self.assertIsNone(w["suma"]["sredni_czas_sesji_s"])
        self.assertIsNone(w["suma"]["niedomkniete"])               # bez listy serwerów nie zgadujemy awarii
        self.assertIsNone(w["suma"]["gracze_teraz"])
        self.assertEqual((w["zakupy"], w["bledy"], w["serwery"]), ([], [], []))
        self.assertEqual(len(w["godziny"]), 2)

    def test_serwer_na_zywo(self):
        s = telemetria.normalizuj_serwer({"id": "7c1e5a90-3b1f-4c0e-9a51-0d6f2b8e1a11",
                                          "value": {"gracze": 4, "od": H5, "pamiec_mb": 1024.6, "fps": 59.96, "bledy": 0}})
        self.assertEqual((s["id"], s["gracze"], s["pamiec_mb"], s["fps"], s["bledy"]), ("7c1e5a90", 4, 1024, 60.0, 0))
        self.assertTrue(s["od"].startswith("2026-11-13T"))
        self.assertIsNone(telemetria.normalizuj_serwer({"id": "x", "value": "to nie jest JSON"}))
        self.assertIsNone(telemetria.normalizuj_serwer("śmieć"))
        s = telemetria.normalizuj_serwer({"id": "", "value": '{"gracze": -2}'})      # wartość jako tekst JSON
        self.assertEqual((s["id"], s["gracze"], s["od"]), ("?", 0, None))

    def test_czas_spoza_kalendarza_nie_wywraca_odpowiedzi(self):
        # błąd z przeglądu: „od” = 1e20 (albo rok > 3000 — na Windows już OSError) rzucało z datetime.fromtimestamp
        for zly in (1e20, 2 ** 63, 99999999999, float("1e300")):
            s = telemetria.normalizuj_serwer({"id": "abc", "value": {"gracze": 2, "od": zly}})
            self.assertEqual((s["gracze"], s["od"]), (2, None), zly)
            self.assertIsNone(telemetria._iso_z_gry(zly))
        self.assertTrue(telemetria._iso_z_gry(H5).startswith("2026-11-13T"))
        self.assertIsNone(telemetria._iso_z_gry("1794546000"))

    def test_dziwny_numer_kroku_lejka(self):
        # błąd z przeglądu: "²".isdigit() == True, a int("²") rzuca ValueError — cały odczyt kończył się „blad_panelu”
        k = telemetria.normalizuj_kubelek({"lejek": {"²": {"n": 3, "nazwa": "x"}, "١": {"n": 1}, "2": {"n": 5, "nazwa": "B"},
                                                     "-1": {"n": 1}, "1.5": {"n": 1}}}, H5)
        w = telemetria.zloz({H5: k}, [H5])
        self.assertEqual(w["lejek"], [{"krok": 2, "nazwa": "B", "n": 5}])


# --------------------------------------------------------------------------- stan: brak klucza, odczyt, błędy
class TestStan(Baza):
    def test_brak_universe_i_brak_klucza_bez_wychodzenia_do_sieci(self):
        self.cfg["gra"]["universeId"] = None
        w = telemetria.stan_telemetrii(24)
        self.assertEqual((w["wlaczona"], w["zrodlo"], w["kod"]), (False, None, "brak_universe"))
        self.cfg["gra"]["universeId"] = UID
        w = telemetria.stan_telemetrii(24)
        self.assertEqual((w["wlaczona"], w["zrodlo"], w["kod"]), (False, None, "brak_klucza"))
        self.assertIn("klucz", w["powod"].lower())
        self.assertEqual(w["kroki"], {"modul": None, "klucz": False})
        self.assertEqual(self.oc.zadania, [])

    def test_klucz_ze_zmiennej_srodowiskowej_ma_pierwszenstwo(self):
        self.cfg["analityka"]["klucz_open_cloud"] = "klucz-z-konfiguracji-lokalnej-000"
        os.environ[telemetria.ZMIENNA_KLUCZA] = "  " + KLUCZ + "\n"
        self.assertEqual(telemetria.klucz_open_cloud(), (KLUCZ, "zmienna środowiskowa BC_OPEN_CLOUD_KEY"))
        os.environ.pop(telemetria.ZMIENNA_KLUCZA)
        self.assertEqual(telemetria.klucz_open_cloud()[1], "konfiguracja lokalna")
        self.cfg["analityka"] = "zepsute"
        self.assertEqual(telemetria.klucz_open_cloud(), (None, None))

    def test_klucz_o_zlym_ksztalcie_nie_idzie_do_sieci(self):
        self.cfg["analityka"]["klucz_open_cloud"] = "klucz ze spacją i ogonkami ąę"
        w = telemetria.stan_telemetrii(24)
        self.assertEqual((w["wlaczona"], w["kod"]), (False, "klucz_odrzucony"))
        self.assertEqual(self.oc.zadania, [])

    def test_odczyt_z_open_cloud(self):
        self.dzialajaca_gra()
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["zrodlo"]), (True, "open_cloud"))
        self.assertNotIn("powod", w)
        self.assertEqual(w["okres"]["godzin"], 24)
        self.assertEqual(len(w["godziny"]), 24)
        self.assertEqual(w["suma"]["sesje"], 14)
        self.assertEqual(w["suma"]["sredni_czas_sesji_s"], 600)
        self.assertEqual(w["suma"]["ccu_max"], 9)
        self.assertEqual(w["suma"]["robuxy"], 600)
        self.assertEqual(w["suma"]["zakupy"], 4)
        self.assertEqual(w["suma"]["bledy"], 4)
        self.assertEqual([g["sesje"] for g in w["godziny"][-2:]], [10, 4])
        self.assertEqual(w["zakupy"][0], {"id": "111", "nazwa": "Skrzynia", "n": 2, "robuxy": 400})
        self.assertEqual([s["id"] for s in w["serwery"]], ["e04b77d2", "7c1e5a90"])          # najpełniejszy pierwszy
        self.assertEqual((w["suma"]["serwery_teraz"], w["suma"]["gracze_teraz"]), (2, 8))
        self.assertEqual(w["modul"]["starty"], 7)
        self.assertNotIn("uwagi", w)
        # żądania: ślad modułu, 24 godziny, lista serwerów — wszystkie z kluczem w nagłówku, pod właściwy adres
        sciezki = self.oc.sciezki()
        self.assertEqual(len(sciezki), 26)
        baza = "/cloud/v2/universes/%d/data-stores/BC_Telemetria_v1/entries/" % UID
        self.assertEqual(sciezki[0], baza + "stan")
        self.assertIn(baza + "g_20261113_05", sciezki)
        self.assertIn(baza + "g_20261112_06", sciezki)                                       # najstarsza z 24 godzin
        self.assertEqual(sciezki[-1], "/cloud/v2/universes/%d/memory-store/sorted-maps/BC_Telemetria_Serwery/items" % UID)
        for z in self.oc.zadania:
            self.assertTrue(z.full_url.startswith("https://apis.roblox.com/"), z.full_url)
            self.assertEqual(z.get_header("X-api-key"), KLUCZ)
            self.assertNotIn(KLUCZ, z.full_url)
            self.assertEqual(z.get_method(), "GET")
        self.assertIn("maxPageSize=200", self.oc.zadania[-1].full_url)

    def test_pamiec_podreczna_5_minut(self):
        self.dzialajaca_gra()
        a = telemetria.stan_telemetrii(24, teraz=TERAZ)
        ile = len(self.oc.zadania)
        b = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual(len(self.oc.zadania), ile, "drugie pytanie w ciągu 5 minut nie może iść do Roblox")
        self.assertEqual(a["suma"], b["suma"])
        b["suma"]["sesje"] = -1                                    # odpowiedź to kopia: zmiana nie psuje pamięci
        b["dopisane"] = True
        self.assertNotIn("dopisane", telemetria.stan_telemetrii(24, teraz=TERAZ))
        telemetria.stan_telemetrii(48, teraz=TERAZ)                # inne okno = osobny odczyt
        self.assertGreater(len(self.oc.zadania), ile)

    def test_zamkniete_godziny_nie_sa_pobierane_drugi_raz(self):
        self.dzialajaca_gra()
        telemetria.stan_telemetrii(24, teraz=TERAZ)
        telemetria._pamiec.clear()                                 # minęło 5 minut
        self.oc.zadania.clear()
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        godziny = [s for s in self.oc.sciezki() if "/entries/g_" in s]
        self.assertEqual(len(godziny), 3, "ponownie pobieramy tylko 3 ostatnie godziny (mogą się jeszcze zmienić)")
        self.assertEqual(w["suma"]["sesje"], 14)

    def test_modul_w_grze_nie_wlaczony(self):
        self.z_kluczem()                                           # klucz działa, ale nie ma wpisu „stan”
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["zrodlo"], w["kod"]), (False, None, "modul_wylaczony"))
        self.assertEqual(w["kroki"], {"modul": False, "klucz": True})
        self.assertIn("moduł", w["powod"])
        self.assertEqual(len(self.oc.zadania), 1, "bez śladu modułu nie pytamy o 24 godziny")

    def test_bledy_roblox_po_polsku(self):
        self.z_kluczem()
        przypadki = [
            (lambda u: blad_http(u, 401), "klucz_odrzucony", False, "odrzucił klucz"),
            (lambda u: blad_http(u, 403, b'{"code":"PERMISSION_DENIED","message":"Insufficient scope."}'),
             "brak_uprawnien", False, "universe-datastores.objects:read"),
            (lambda u: blad_http(u, 429), "limit", True, "429"),
            (lambda u: blad_http(u, 503), "blad_roblox", True, "503"),
            (lambda u: blad_http(u, 302), "blad_roblox", True, "przekierować"),
            (lambda u: urllib.error.URLError("getaddrinfo failed"), "siec", True, "Nie udało się połączyć"),
            (lambda u: socket.timeout("timed out"), "siec", True, "Nie udało się połączyć"),
            (lambda u: ConnectionResetError("reset"), "siec", True, "Nie udało się połączyć"),
        ]
        for awaria, kod, chwilowe, fragment in przypadki:
            telemetria._pamiec.clear()
            self.oc.awaria = awaria
            w = telemetria.stan_telemetrii(24, teraz=TERAZ)
            self.assertEqual((w["wlaczona"], w["zrodlo"], w["kod"]), (False, None, kod), kod)
            self.assertEqual(bool(w.get("chwilowe")), chwilowe, kod)
            self.assertIn(fragment, w["powod"], kod)
            self.assertTrue(w["kroki"]["klucz"])
        self.assertEqual(w["kod"], "siec")
        # błąd też jest pamiętany (minutę), żeby nie odpytywać Roblox przy każdym odświeżeniu widoku
        ile = len(self.oc.zadania)
        telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual(len(self.oc.zadania), ile)

    def test_szczegoly_z_roblox_tylko_do_wgladu_lokalnego(self):
        self.z_kluczem()
        self.oc.awaria = lambda u: blad_http(u, 403, b'{"code":"PERMISSION_DENIED","message":"Insufficient  scope\\nfor key."}')
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual(w["szczegoly"], "Insufficient scope for key.")
        self.assertEqual(self.trasa(lokalny=False).get("szczegoly"), None)
        self.assertEqual(self.trasa(lokalny=True)["szczegoly"], "Insufficient scope for key.")

    def trasa(self, lokalny=True, **query):
        app = _App()
        telemetria.zarejestruj(app)
        z = Zadanie("GET", "/api/telemetria", {k: str(v) for k, v in query.items()}, {}, b"", lokalny, "Tester",
                    "127.0.0.1", "127.0.0.1:8787")
        return app.trasy[("GET", "/api/telemetria")](z)

    def test_zla_odpowiedz_roblox(self):
        self.z_kluczem()
        self.oc.awaria = None
        telemetria._otworz = lambda zadanie, limit: Odpowiedz(None, surowe=b"<html>to nie JSON</html>")
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["kod"]), (False, "blad_roblox"))

    def test_brak_uprawnien_do_listy_serwerow_nie_psuje_reszty(self):
        self.dzialajaca_gra()
        self.oc.awaria_serwerow = lambda u: blad_http(u, 403)
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertTrue(w["wlaczona"])
        self.assertEqual(w["suma"]["sesje"], 14)
        self.assertEqual(w["serwery"], [])
        self.assertIsNone(w["suma"]["serwery_teraz"])
        self.assertTrue(any("memory-store.sorted-map:read" in u for u in w["uwagi"]), w["uwagi"])

    def test_mapy_serwerow_jeszcze_nie_ma(self):
        self.dzialajaca_gra()
        self.oc.serwery = None                                     # 404: żaden serwer nie zapisał wpisu „na żywo”
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["serwery"], w["suma"]["serwery_teraz"]), (True, [], 0))

    def test_czesc_godzin_niedostepna(self):
        self.dzialajaca_gra()
        zepsuta = telemetria.klucz_godziny(H4)
        self.oc.awaria = lambda u: blad_http(u, 500) if u.endswith(zepsuta) else None
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertTrue(w["wlaczona"])
        self.assertEqual(w["suma"]["sesje"], 4)                    # jest tylko godzina 05
        self.assertTrue(any("1 z 24 godzin" in u for u in w["uwagi"]), w["uwagi"])

    def test_po_awarii_sieci_pokazuje_ostatnie_dobre_dane(self):
        self.dzialajaca_gra()
        dobre = telemetria.stan_telemetrii(24, teraz=TERAZ)
        for wpis in telemetria._pamiec.values():
            wpis["t"] -= telemetria.PAMIEC_S + 1                   # pamięć się przeterminowała
        self.oc.awaria = lambda u: urllib.error.URLError("brak sieci")
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["zrodlo"], w["nieaktualne"]), (True, "open_cloud", True))
        self.assertIn("poprzedniego odczytu", w["blad"])
        self.assertEqual(w["suma"], dobre["suma"])
        self.assertEqual(telemetria.stan_telemetrii(24, teraz=TERAZ)["nieaktualne"], True)   # i tak przez minutę
        self.oc.awaria = None                                      # sieć wróciła
        for wpis in telemetria._pamiec.values():
            wpis["t"] -= telemetria.PAMIEC_S + 1
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertNotIn("nieaktualne", w)
        self.assertNotIn("blad", w)

    def test_smieci_z_gry_w_stanie_i_serwerach_nie_wylaczaja_telemetrii(self):
        self.dzialajaca_gra()
        self.oc.wpisy["stan"] = {"wersja": 1, "pierwszy_start": 1e20, "ostatni_start": 2 ** 70, "starty": 3}
        self.oc.serwery.append({"id": "zly", "value": {"gracze": 1, "od": 1e300}})
        self.oc.wpisy[telemetria.klucz_godziny(H5)]["lejek"] = {"²": {"n": 2}, "1": {"n": 4, "nazwa": "Wejście"}}
        w = telemetria.stan_telemetrii(24, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["kod"] if "kod" in w else None), (True, None), w.get("powod"))
        self.assertEqual((w["modul"]["pierwszy_start"], w["modul"]["ostatni_start"]), (None, None))
        self.assertEqual(w["suma"]["serwery_teraz"], 3)
        self.assertEqual(w["lejek"], [{"krok": 1, "nazwa": "Wejście", "n": 4}])

    def test_ogranicznik_zapytan_chroni_wspolny_budzet_data_store(self):
        # budżet odczytów Data Store gra dzieli z Open Cloud: panel nie może go wyczerpać nawet przy wielu oknach czasu
        self.dzialajaca_gra()
        telemetria.stan_telemetrii(24, teraz=TERAZ)
        for godzin in range(25, 200):                          # każde okno to osobny wpis pamięci podręcznej
            telemetria.stan_telemetrii(godzin, teraz=TERAZ)
        self.assertLessEqual(len(self.oc.zadania), telemetria.ZAPYTAN_NA_MINUTE)
        w = telemetria.stan_telemetrii(7, teraz=TERAZ)
        self.assertEqual((w["wlaczona"], w["kod"], w.get("chwilowe")), (False, "limit", True))
        self.assertIn("Panel wstrzymał", w["powod"])
        telemetria._zapytania[:] = [t - 61 for t in telemetria._zapytania]   # minęła minuta
        telemetria._pamiec.clear()
        self.assertTrue(telemetria.stan_telemetrii(7, teraz=TERAZ)["wlaczona"])

    def test_lista_serwerow_nie_czeka_ponad_limit(self):
        self.dzialajaca_gra()
        strony, oc = [], self.oc

        def z_tokenem(zadanie, limit_czasu):                   # Roblox zawsze mówi „jest kolejna strona”
            if "/memory-store/" in zadanie.full_url:
                strony.append(zadanie.full_url)
                return Odpowiedz({"items": oc.serwery, "nextPageToken": "dalej"})
            return oc(zadanie, limit_czasu)
        telemetria._otworz = z_tokenem
        serwery, wiecej = telemetria._czytaj_serwery(telemetria.ustawienia(), KLUCZ, koniec=0)   # czas już minął
        self.assertEqual((len(strony), len(serwery), wiecej), (1, 2, True))
        strony.clear()
        serwery, wiecej = telemetria._czytaj_serwery(telemetria.ustawienia(), KLUCZ)
        self.assertEqual((len(strony), wiecej), (telemetria.STRON_SERWEROW, True))
        self.assertIn("pageToken=dalej", strony[-1])

    def test_nazwy_zasobow_z_konfiguracji(self):
        self.dzialajaca_gra()
        self.oc.wpisy = {"stan": {"wersja": 1}}
        self.cfg["analityka"].update(magazyn="Inny_Magazyn", mapa_serwerow="Inna.Mapa-2")
        telemetria.stan_telemetrii(1, teraz=TERAZ)
        self.assertIn("/data-stores/Inny_Magazyn/entries/stan", self.oc.sciezki()[0])
        self.assertIn("/sorted-maps/Inna.Mapa-2/items", self.oc.sciezki()[-1])
        telemetria._pamiec.clear()
        self.oc.zadania.clear()
        self.cfg["analityka"].update(magazyn="../../inna/sciezka?x=1", mapa_serwerow="a b")   # niedozwolone znaki
        telemetria.stan_telemetrii(1, teraz=TERAZ)
        self.assertIn("/data-stores/BC_Telemetria_v1/entries/stan", self.oc.sciezki()[0])
        self.assertIn("/sorted-maps/BC_Telemetria_Serwery/items", self.oc.sciezki()[-1])


# --------------------------------------------------------------------------- sekrety
class TestSekrety(Baza):
    def test_klucz_nie_wycieka_do_odpowiedzi_ani_logu(self):
        teksty = []

        def zbierz(obj):
            teksty.append(json.dumps(obj, ensure_ascii=False))

        self.dzialajaca_gra()
        app = _App()
        telemetria.zarejestruj(app)
        trasa = app.trasy[("GET", "/api/telemetria")]

        def pytaj(lokalny, **query):
            z = Zadanie("GET", "/api/telemetria", {k: str(v) for k, v in query.items()}, {}, b"", lokalny, "Tester",
                        "127.0.0.1", "127.0.0.1:8787")
            return trasa(z)

        zbierz(pytaj(True))                                        # dane z gry
        zbierz(pytaj(False))
        zbierz(pytaj(True, probka=1))                              # dane przykładowe
        zbierz(telemetria.zdrowie())
        # Roblox (albo pośrednik) odsyła klucz w treści błędu i w opisie awarii sieci
        echo = json.dumps({"code": "PERMISSION_DENIED", "message": "Key %s lacks scope" % KLUCZ}).encode("utf-8")
        for awaria in (lambda u: blad_http(u, 403, echo), lambda u: blad_http(u, 401, echo),
                       lambda u: blad_http(u, 500, echo), lambda u: urllib.error.URLError("proxy odrzucił " + KLUCZ),
                       lambda u: OSError("nagłówek x-api-key: " + KLUCZ)):
            telemetria._pamiec.clear()
            telemetria._godziny.clear()
            self.oc.awaria = awaria
            zbierz(pytaj(True))
            zbierz(pytaj(False))
            zbierz(telemetria.stan_telemetrii(24, teraz=TERAZ))
        # nieoczekiwany wyjątek w środku odczytu
        telemetria._pamiec.clear()
        telemetria._otworz = lambda zadanie, limit: (_ for _ in ()).throw(RuntimeError("awaria z kluczem " + KLUCZ))
        zbierz(pytaj(True))
        self.assertGreaterEqual(len(self.log), 5, "błędy odczytu mają trafić do logu")
        for tekst in teksty + self.log:
            self.assertNotIn(KLUCZ, tekst)
            self.assertNotIn(KLUCZ[:20], tekst)
        self.assertTrue(any("***" in t for t in teksty), "wycięty klucz ma zostawić ślad ***")

    def test_zdrowie_mowi_tylko_czy_klucz_jest(self):
        self.z_kluczem()
        z = telemetria.zdrowie()
        self.assertEqual((z["klucz_open_cloud"], z["skad_klucz"], z["universeId"]), (True, "konfiguracja lokalna", UID))

    def test_wspolna_konfiguracja_nie_ustawi_klucza_ani_adresu(self):
        wspolna = {"analityka": {"klucz_open_cloud": "podrzucony-klucz-z-repozytorium", "adres_open_cloud": "https://zly.example",
                                 "magazyn": "Inny"}, "gra": {"universeId": 1}}
        bezpieczna = rdzen._bezpieczna_wspolna(wspolna)
        self.assertEqual(bezpieczna["analityka"], {"magazyn": "Inny"})
        self.assertEqual(wspolna["analityka"]["klucz_open_cloud"], "podrzucony-klucz-z-repozytorium")   # wejście nietknięte
        # cała ścieżka: plik wspólny + plik lokalny
        tmp = tempfile.mkdtemp(prefix="bc_test_telemetria_")
        stare = (rdzen.PLIK_KONFIGURACJI, rdzen.PLIK_KONFIGURACJI_LOKALNEJ)
        rdzen.konfiguracja = self._stare[0]                        # prawdziwa funkcja zamiast atrapy z setUp
        try:
            rdzen.PLIK_KONFIGURACJI = os.path.join(tmp, "konfiguracja.json")
            rdzen.PLIK_KONFIGURACJI_LOKALNEJ = os.path.join(tmp, "konfiguracja.lokalna.json")
            with open(rdzen.PLIK_KONFIGURACJI, "w", encoding="utf-8") as f:
                json.dump(wspolna, f)
            rdzen._cfg_cache.update(mtime=None, dane=None)
            self.assertEqual(telemetria.klucz_open_cloud(), (None, None))
            self.assertEqual(telemetria.ustawienia()["adres"], "https://apis.roblox.com")
            self.assertEqual(telemetria.ustawienia()["magazyn"], "Inny")
            with open(rdzen.PLIK_KONFIGURACJI_LOKALNEJ, "w", encoding="utf-8") as f:
                json.dump({"analityka": {"klucz_open_cloud": KLUCZ}}, f)
            rdzen._cfg_cache.update(mtime=None, dane=None)
            self.assertEqual(telemetria.klucz_open_cloud(), (KLUCZ, "konfiguracja lokalna"))
        finally:
            rdzen.PLIK_KONFIGURACJI, rdzen.PLIK_KONFIGURACJI_LOKALNEJ = stare
            rdzen._cfg_cache.update(mtime=None, dane=None)
            shutil.rmtree(tmp, ignore_errors=True)

    def test_adres_tylko_https_albo_ten_komputer(self):
        self.assertEqual(telemetria._adres({}), "https://apis.roblox.com")
        self.assertEqual(telemetria._adres({"adres_open_cloud": "https://apis.roblox.com/"}), "https://apis.roblox.com")
        self.assertEqual(telemetria._adres({"adres_open_cloud": "http://127.0.0.1:8899"}), "http://127.0.0.1:8899")
        for zly in ("http://apis.roblox.com", "http://192.168.1.5:80", "ftp://x", "apis.roblox.com", "https://", 5):
            self.assertEqual(telemetria._adres({"adres_open_cloud": zly}), "https://apis.roblox.com", zly)

    def test_bez_przekierowan(self):
        # przekierowanie pod inny adres zabrałoby ze sobą nagłówek z kluczem
        self.assertIsNone(telemetria._BezPrzekierowan().redirect_request(None, None, 302, "Found", {}, "https://zly.example/"))


# --------------------------------------------------------------------------- dane przykładowe i trasa
class _App:
    def __init__(self):
        self.trasy = {}

    def dodaj(self, metoda, wzorzec, fn):
        self.trasy[(metoda, wzorzec)] = fn

    def znajdz(self, metoda, sciezka):                             # lustro: żadna trasa nie istnieje
        return None, None


class TestTrasa(Baza):
    def pytaj(self, lokalny=True, **query):
        app = _App()
        telemetria.zarejestruj(app)
        z = Zadanie("GET", "/api/telemetria", {k: str(v) for k, v in query.items()}, {}, b"", lokalny, "Tester",
                    "127.0.0.1", "127.0.0.1:8787")
        return app.trasy[("GET", "/api/telemetria")](z)

    def test_dane_przykladowe_tylko_lokalnie(self):
        with self.assertRaises(BladHTTP) as ctx:
            self.pytaj(lokalny=False, probka=1)
        self.assertEqual(ctx.exception.status, 403)
        self.assertIn("przykładowe", ctx.exception.komunikat)
        w = self.pytaj(lokalny=True, probka=1)
        self.assertEqual((w["wlaczona"], w["zrodlo"], w["przykladowe"]), (False, "probka", True))
        self.assertIn("przykładowe", w["powod"])
        self.assertEqual(self.oc.zadania, [], "dane przykładowe nie mogą wychodzić do sieci")
        # bez parametru nikt nie dostaje danych przykładowych
        for lokalny in (True, False):
            w = self.pytaj(lokalny=lokalny)
            self.assertEqual((w["wlaczona"], w["zrodlo"], w.get("przykladowe")), (False, None, None))
            self.assertNotIn("suma", w)

    def test_ksztalt_danych_przykladowych(self):
        w = self.pytaj(probka=1, godzin=24)
        for pole in ("wlaczona", "zrodlo", "powod", "okres", "suma", "godziny", "zakupy", "bledy", "serwery"):
            self.assertIn(pole, w)
        for pole in ("sesje", "sredni_czas_sesji_s", "ccu_max", "robuxy", "zakupy", "bledy"):
            self.assertIn(pole, w["suma"])
        self.assertEqual(len(w["godziny"]), 24)
        self.assertEqual(w["suma"]["sesje"], sum(g["sesje"] for g in w["godziny"]))
        self.assertEqual(w["suma"]["robuxy"], sum(g["robuxy"] for g in w["godziny"]))
        self.assertEqual(w["suma"]["robuxy"], sum(z["robuxy"] for z in w["zakupy"]))
        self.assertEqual(w["suma"]["bledy"], sum(b["n"] for b in w["bledy"]))
        self.assertGreater(w["suma"]["sesje"], 0)
        self.assertTrue(all(set(z) == {"id", "nazwa", "n", "robuxy"} for z in w["zakupy"]))
        self.assertTrue(all(set(b) == {"sygnatura", "komunikat", "n"} for b in w["bledy"]))
        self.assertTrue(all({"id", "gracze", "od"} <= set(s) for s in w["serwery"]))
        # spójność: „gracze teraz” na serwerach nie przekracza szczytu bieżącej godziny na wykresie
        for t in (TERAZ, TERAZ - 6 * 3600, TERAZ + 9 * 3600):
            p = telemetria.probka(24, t)
            self.assertLessEqual(p["suma"]["gracze_teraz"], p["godziny"][-1]["ccu_max"], t)
            self.assertGreaterEqual(p["suma"]["serwery_teraz"], 1)
            self.assertTrue(all(0 < s["gracze"] <= 12 for s in p["serwery"]), p["serwery"])
            # przykład awarii: jedno zamknięcie z braku pamięci na dobę, bez wymyślonych „niedomkniętych” serwerów
            self.assertEqual((p["suma"]["brak_pamieci"], p["suma"]["niedomkniete"]), (1, 0), t)
        self.assertEqual(len(self.pytaj(probka=1, godzin=3)["godziny"]), 3)
        a, b = telemetria.probka(24, TERAZ), telemetria.probka(24, TERAZ + 240)
        self.assertEqual(a["godziny"][:23], b["godziny"][:23], "zamknięte godziny mają być powtarzalne")
        self.assertEqual(a["okres"]["od"], b["okres"]["od"])

    def test_zakres_godzin(self):
        self.assertEqual(len(self.pytaj(probka=1, godzin=0)["godziny"]), 1)
        self.assertEqual(len(self.pytaj(probka=1, godzin=99999)["godziny"]), telemetria.GODZIN_MAX)
        self.assertEqual(len(self.pytaj(probka=1, godzin="x")["godziny"]), telemetria.GODZIN_DOMYSLNIE)

    def test_plik_konfiguracji_tylko_dla_osoby_przy_komputerze(self):
        self.assertEqual(self.pytaj(lokalny=True)["plik_konfiguracji"], rdzen.PLIK_KONFIGURACJI_LOKALNEJ)
        self.assertNotIn("plik_konfiguracji", self.pytaj(lokalny=False))

    def test_odswiez_tylko_lokalnie_i_nie_czesciej_niz_co_pol_minuty(self):
        self.dzialajaca_gra()
        self.pytaj(lokalny=True)
        ile = len(self.oc.zadania)
        self.pytaj(lokalny=True, odswiez=1)                        # za wcześnie
        self.assertEqual(len(self.oc.zadania), ile)
        for wpis in telemetria._pamiec.values():
            wpis["t"] -= 31
        self.pytaj(lokalny=False, odswiez=1)                       # gość nie wymusza odczytu
        self.assertEqual(len(self.oc.zadania), ile)
        self.pytaj(lokalny=True, odswiez=1)
        self.assertGreater(len(self.oc.zadania), ile)


# --------------------------------------------------------------------------- lustro statyczne i zgodność z grą
class TestLustroIZgodnosc(unittest.TestCase):
    def test_lustro_nie_dostaje_danych_telemetrii(self):
        tmp = tempfile.mkdtemp(prefix="bc_test_telemetria_lustro_")
        try:
            wyj = os.path.join(tmp, "lustro")
            statyczny.eksportuj(_App(), wyj, czas="2026-11-13T00:00:00+01:00")
            with open(os.path.join(PANEL, "static", "widoki", "analityka.js"), encoding="utf-8") as f:
                sciezki = set(re.findall(r'"(/api/telemetria[^"]*)"', f.read()))
            sciezki = {s for s in sciezki if "probka" not in s}
            self.assertTrue(sciezki, "widok Analityka ma pytać o /api/telemetria")
            for sciezka in sciezki | {"/api/telemetria"}:
                plik = os.path.join(wyj, "dane", statyczny.klucz(sciezka) + ".json")
                self.assertTrue(os.path.isfile(plik), "lustro nie ma pliku dla %s" % sciezka)
                with open(plik, encoding="utf-8") as f:
                    self.assertEqual(json.load(f), {"wlaczona": False, "powod": "niedostępne w podglądzie"})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_nazwy_zgodne_z_modulem_w_grze(self):
        """Panel i gra muszą mówić o tych samych wpisach: nazwy magazynu, mapy, klucza stanu i pól kubełka."""
        katalog = os.path.join(REPO, "src", "server", "Telemetria")
        with open(os.path.join(katalog, "init.luau"), encoding="utf-8") as f:
            init = f.read()
        with open(os.path.join(katalog, "Magazyn.luau"), encoding="utf-8") as f:
            magazyn = f.read()
        with open(os.path.join(katalog, "Agregator.luau"), encoding="utf-8") as f:
            agregator = f.read()
        self.assertIn('magazyn = "%s"' % telemetria.MAGAZYN, init)
        self.assertIn('mapa_serwerow = "%s"' % telemetria.MAPA_SERWEROW, init)
        self.assertIn('Magazyn.KLUCZ_STANU = "%s"' % telemetria.WPIS_STANU, magazyn)
        self.assertIn('Agregator.INNE = "%s"' % telemetria.INNE, agregator)
        self.assertIn('"g_%04d%02d%02d_%02d"', agregator)
        for pole in telemetria.POLA_LICZBOWE + ("ccu_minuty", "zakupy", "bledy", "zdarzenia", "lejek", "dlugosci",
                                                "zamkniecia"):
            self.assertRegex(agregator, r"\b%s\b" % pole, "pole %s zniknęło z Agregator.luau" % pole)
        for pole in ("gracze", "od", "pamiec_mb", "fps", "bledy"):         # wpis serwera na żywo
            self.assertRegex(magazyn, r"\b%s = " % pole, "pole %s zniknęło z wpisu serwera" % pole)
        self.assertIn('"OutOfMemory"', agregator)
        # moduł w grze ma pozostać bezwładny: żadnego skryptu, który sam go uruchamia
        for nazwa in os.listdir(katalog):
            self.assertFalse(nazwa.endswith((".server.luau", ".client.luau")), nazwa)


if __name__ == "__main__":
    unittest.main()
