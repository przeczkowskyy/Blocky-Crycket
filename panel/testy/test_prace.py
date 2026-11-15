# -*- coding: utf-8 -*-
"""Prace w toku (bc/prace.py, narzedzia/praca.py, GET /api/prace).

Wszystko na katalogach tymczasowych: moduł pisze do rdzen.RUNTIME podmienionego na katalog testu, narzędzie dostaje
BC_PANEL_RUNTIME z katalogu testu, a serwer testowy (test_api.SerwerTestowy) ma własne dane lokalne. Prawdziwe dane
lokalne panelu nie są czytane ani pisane.
"""
import contextlib
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

from testy import test_api  # noqa: F401  (bez importu klas: discover uruchomiłby je drugi raz)
from bc import prace, rdzen  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

PANEL = test_api.PANEL
STREFA = datetime.timezone(datetime.timedelta(hours=1))


def T(g, m=0, dzien=15):
    return datetime.datetime(2026, 11, dzien, g, m, tzinfo=STREFA)


@contextlib.contextmanager
def dane_lokalne_testu(runtime):
    """Na czas bloku moduł prac pisze do `runtime` (katalog testu), a log panelu idzie do listy w pamięci i — gdyby
    ktoś wołał prawdziwy rdzen.log — do <runtime>/panel.log, nigdy do logu działającego panelu. → lista wpisów logu."""
    stare = rdzen.RUNTIME, rdzen.PLIK_LOGU, rdzen.log
    logi = []
    rdzen.RUNTIME = runtime
    rdzen.PLIK_LOGU = os.path.join(runtime, "panel.log")
    rdzen.log = lambda *c: logi.append(" ".join(str(x) for x in c))
    try:
        yield logi
    finally:
        rdzen.RUNTIME, rdzen.PLIK_LOGU, rdzen.log = stare


class _KatalogTymczasowy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_prace_")
        self._dane = dane_lokalne_testu(os.path.join(self.tmp, "runtime"))
        self.logi = self._dane.__enter__()
        prace._sprzatanie["t"] = 0.0

    def tearDown(self):
        self._dane.__exit__(None, None, None)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def plik(self, nazwa, dane):
        kat = rdzen.upewnij_katalog(os.path.join(rdzen.RUNTIME, "prace"))
        with open(os.path.join(kat, nazwa), "w", encoding="utf-8") as f:
            json.dump(dane, f, ensure_ascii=False)


class TestCzas(unittest.TestCase):
    def test_godzina_dzis_albo_jutro(self):
        teraz = T(10, 15)
        self.assertEqual(prace.parsuj_koniec("12:40", teraz)[:16], "2026-11-15T12:40")
        self.assertEqual(prace.parsuj_koniec("9:05", teraz)[:16], "2026-11-16T09:05")     # już była — jutro
        self.assertEqual(prace.parsuj_koniec("10:15", teraz)[:16], "2026-11-16T10:15")    # ta sama minuta = jutro
        self.assertEqual(prace.parsuj_koniec("00:30", T(23, 50))[:16], "2026-11-16T00:30")

    def test_za_ile(self):
        teraz = T(10, 0)
        self.assertEqual(prace.parsuj_koniec("+90m", teraz)[:16], "2026-11-15T11:30")
        self.assertEqual(prace.parsuj_koniec("+2h", teraz)[:16], "2026-11-15T12:00")
        self.assertEqual(prace.parsuj_koniec("+1h30m", teraz)[:16], "2026-11-15T11:30")
        self.assertEqual(prace.parsuj_koniec("+45", teraz)[:16], "2026-11-15T10:45")
        self.assertEqual(prace.parsuj_koniec("+20min", teraz)[:16], "2026-11-15T10:20")

    def test_iso(self):
        d = datetime.datetime.fromisoformat(prace.parsuj_koniec("2026-11-15T14:30+01:00", T(10)))
        self.assertEqual(d, T(14, 30))
        d = datetime.datetime.fromisoformat(prace.parsuj_koniec("2026-11-15T14:30", T(10)))
        self.assertIsNotNone(d.tzinfo)                                       # bez strefy = czas lokalny

    def test_zle_dane(self):
        for zle in ("25:00", "12:61", "+0m", "+", "+abc", "jutro", "", "  ", "12"):
            with self.assertRaises(BladHTTP, msg=zle):
                prace.parsuj_koniec(zle, T(10))

    def test_bezpieczne_id(self):
        self.assertEqual(prace.sprawdz_id("Biom-Las"), "biom-las")
        self.assertEqual(prace.sprawdz_id(" walka_v2 "), "walka_v2")
        for zle in ("../x", "a b", "", "-x", "x" * 65, "a/b", "a\\b", "C:x", "żaba", None, 5):
            with self.assertRaises(BladHTTP, msg=repr(zle)):
                prace.sprawdz_id(zle)

    def test_dotyczy(self):
        self.assertEqual(prace.parsuj_dotyczy("raport:r-20261115-101500-ab12"), {"typ": "raport", "id": "r-20261115-101500-ab12"})
        self.assertEqual(prace.parsuj_dotyczy("pytanie:019"), {"typ": "pytanie", "id": "19"})
        self.assertEqual(prace.parsuj_dotyczy("decyzja:d-71"), {"typ": "decyzja", "id": "D-071"})
        for zle in ("raport", "raport:../x", "zadanie:1", "pytanie:abc", "decyzja:71x"):
            with self.assertRaises(BladHTTP, msg=zle):
                prace.parsuj_dotyczy(zle)

    def test_koniec_poza_zakresem(self):
        # rok 1 i 9999 dawały OSError z astimezone() na Windows (traceback w narzędziu) — teraz czytelny błąd 400
        for zle in ("9999-12-31T23:59", "9999-12-31T23:59:59", "0001-01-01T00:00", "2030-01-01T00:00",
                    "2026-11-13T10:00+01:00", "2026-11-30T10:00+01:00"):
            with self.assertRaises(BladHTTP, msg=zle) as b:
                prace.parsuj_koniec(zle, T(10))
            self.assertEqual(b.exception.status, 400)
            self.assertIn("zakresem", b.exception.komunikat)
        self.assertTrue(prace.parsuj_koniec("2026-11-15T09:00+01:00", T(10)))     # chwilę temu — można (po czasie)
        self.assertTrue(prace.parsuj_koniec("2026-11-28T10:00+01:00", T(10)))     # za 13 dni — można

    def test_czas_z_dziwnych_wartosci(self):
        for zle in ("0001-01-01T00:00", "9999-12-31T23:59:59", "abc", 12345, None, ["2026-11-15"], "1970-01-01T00:00"):
            self.assertIsNone(prace._czas(zle), repr(zle))
        self.assertIsNotNone(prace._czas("2026-11-15T10:00"))

    def test_godzina_przez_zmiane_czasu(self):
        # godzina HH:MM to zawsze godzina na zegarze lokalnym, także gdy w nocy zmienia się czas (letni ↔ zimowy);
        # wynik oceniany w czasie lokalnym (w strefie bez zmiany czasu test przechodzi trywialnie)
        for teraz, wpis, oczekiwane in (
                (datetime.datetime(2026, 10, 24, 22, 0), "20:00", datetime.datetime(2026, 10, 25, 20, 0)),
                (datetime.datetime(2026, 10, 25, 1, 0), "05:00", datetime.datetime(2026, 10, 25, 5, 0)),
                (datetime.datetime(2027, 3, 27, 22, 0), "20:00", datetime.datetime(2027, 3, 28, 20, 0)),
                (datetime.datetime(2027, 3, 28, 1, 0), "12:00", datetime.datetime(2027, 3, 28, 12, 0))):
            wynik = datetime.datetime.fromisoformat(prace.parsuj_koniec(wpis, teraz.astimezone())).astimezone()
            self.assertEqual(wynik.replace(tzinfo=None), oczekiwane, "%s, %s" % (teraz, wpis))


class TestPrace(_KatalogTymczasowy):
    def test_plik_w_danych_lokalnych(self):
        p = prace.rozpocznij("biom-las", "Biom Las — mapa z klocków", etapy="Plan,Budowa,Kontrola", koniec="+90m",
                             kto="Claude (test)")
        sciezka = os.path.join(rdzen.RUNTIME, "prace", "biom-las.json")
        self.assertTrue(os.path.isfile(sciezka))
        self.assertEqual(rdzen.czytaj_json(sciezka)["tytul"], "Biom Las — mapa z klocków")
        self.assertEqual((p["stan"], p["etap"], p["numer"], p["etapy"]), ("w_toku", "Plan", 1, ["Plan", "Budowa", "Kontrola"]))
        self.assertEqual([x for x in os.listdir(os.path.dirname(sciezka)) if x.endswith(".tmp")], [])

    def test_sortowanie_i_48h(self):
        t0 = T(9)
        prace.rozpocznij("pozniej", "B", koniec="13:00", teraz=t0)
        prace.rozpocznij("wczesniej", "A", koniec="11:00", teraz=t0)
        prace.rozpocznij("bez-konca", "C", teraz=t0)
        prace.rozpocznij("pauza", "D", koniec="12:00", teraz=t0)
        prace.wstrzymaj("pauza", "czeka na decyzję", teraz=T(9, 30))
        prace.rozpocznij("zepsuta", "E", teraz=t0)
        prace.oznacz_blad("zepsuta", "Studio się zamknęło", teraz=T(9, 40))
        prace.rozpocznij("gotowa", "F", teraz=t0)
        prace.zakoncz("gotowa", raport="r-1", teraz=T(9, 50))
        prace.rozpocznij("stara", "G", teraz=T(8, dzien=12))
        prace.zakoncz("stara", teraz=T(9, dzien=12))
        prace.rozpocznij("stary-blad", "H", teraz=T(8, dzien=12))
        prace.oznacz_blad("stary-blad", "x", teraz=T(9, dzien=12))
        lista = prace.lista(T(10))
        self.assertEqual([p["id"] for p in lista], ["wczesniej", "pozniej", "bez-konca", "zepsuta", "pauza", "gotowa"])
        self.assertTrue(os.path.isfile(os.path.join(rdzen.RUNTIME, "prace", "stara.json")) is False)   # sprzątnięta
        self.assertFalse(os.path.isfile(os.path.join(rdzen.RUNTIME, "prace", "stary-blad.json")))
        self.assertEqual(lista[-1]["raport"], "r-1")
        # gotowa znika z listy po 48 h
        self.assertNotIn("gotowa", [p["id"] for p in prace.lista(T(10, 0, dzien=17))])

    def test_przeterminowanie_i_postep(self):
        prace.rozpocznij("a", "A", koniec="11:40", teraz=T(10))
        p = prace.lista(T(11, 5))[0]
        self.assertEqual((p["zostalo_min"], p["po_czasie_min"], p["przeterminowana"]), (35, None, False))
        self.assertAlmostEqual(p["postep"], 65 / 100.0, places=2)
        p = prace.lista(T(11, 50))[0]
        self.assertEqual((p["zostalo_min"], p["po_czasie_min"], p["przeterminowana"]), (None, 10, True))
        self.assertEqual(p["postep"], 0.99)                                   # w toku nigdy 100 %
        prace.wstrzymaj("a", teraz=T(11, 50))
        self.assertFalse(prace.lista(T(11, 55))[0]["przeterminowana"])       # wstrzymana nie jest „po czasie”
        prace.zakoncz("a", teraz=T(12))
        p = prace.lista(T(12, 5))[0]
        self.assertEqual((p["postep"], p["zostalo_min"], p["po_czasie_min"], p["przeterminowana"]), (1.0, None, None, False))

    def test_postep_z_etapow(self):
        prace.rozpocznij("e", "E", etapy="Plan,Budowa,Kontrola,Raport", teraz=T(10))
        self.assertEqual(prace.lista(T(10, 5))[0]["postep"], 0.0)
        p = prace.ustaw_etap("e", etap="Kontrola", teraz=T(10, 30))
        self.assertEqual((p["numer"], p["etap"]), (3, "Kontrola"))
        self.assertEqual(prace.lista(T(10, 31))[0]["postep"], 0.5)
        p = prace.ustaw_etap("e", numer=4, teraz=T(10, 40))
        self.assertEqual((p["numer"], p["etap"]), (4, "Raport"))
        p = prace.ustaw_etap("e", etap="Poprawki po kontroli", teraz=T(10, 45))      # etap spoza listy: numer zostaje
        self.assertEqual((p["numer"], p["etap"]), (4, "Poprawki po kontroli"))
        with self.assertRaises(BladHTTP):
            prace.ustaw_etap("e", numer=5)
        with self.assertRaises(BladHTTP):
            prace.ustaw_etap("e")                                             # nic do zmiany
        with self.assertRaises(BladHTTP) as b:
            prace.ustaw_etap("nie-ma", etap="x")
        self.assertEqual(b.exception.status, 404)

    def test_etap_po_bledzie_wraca_do_pracy(self):
        prace.rozpocznij("x", "X", teraz=T(10))
        prace.oznacz_blad("x", "padło", teraz=T(10, 10))
        p = prace.ustaw_etap("x", etap="Druga próba", koniec="+30m", teraz=T(10, 20))
        self.assertEqual(p["stan"], "w_toku")
        self.assertNotIn("komunikat", p)
        self.assertNotIn("zakonczono", p)
        self.assertEqual(p["koniec_szacowany"][:16], "2026-11-15T10:50")

    def test_zepsuty_plik(self):
        prace.rozpocznij("dobra", "Dobra", teraz=T(10))
        kat = os.path.join(rdzen.RUNTIME, "prace")
        with open(os.path.join(kat, "zepsuta.json"), "w", encoding="utf-8") as f:
            f.write("{ to nie jest json")
        with open(os.path.join(kat, "obca.json"), "w", encoding="utf-8") as f:
            json.dump({"id": "inna", "tytul": "x", "stan": "w_toku"}, f)                # id nie zgadza się z nazwą
        with open(os.path.join(kat, "zly-stan.json"), "w", encoding="utf-8") as f:
            json.dump({"id": "zly-stan", "tytul": "x", "stan": "cos"}, f)
        with open(os.path.join(kat, "ZLA NAZWA.json"), "w", encoding="utf-8") as f:
            f.write("{}")
        self.assertEqual([p["id"] for p in prace.lista(T(10, 5))], ["dobra"])
        self.assertTrue(any("zepsuta.json" in l for l in self.logi), self.logi)
        self.assertTrue(any("obca.json" in l for l in self.logi), self.logi)

    def test_bez_sciezek_i_walidacja(self):
        p = prace.rozpocznij("s", "Tytuł", opis="Plik C:\\Users\\jan\\Desktop\\x.rbxl i /home/jan/y", teraz=T(10))
        self.assertNotIn("jan", p["opis"])
        self.assertIn("x.rbxl", p["opis"])
        for kw in ({"tytul": ""}, {"tytul": "x" * 121}, {"tytul": "x", "etapy": ",".join("e%d" % i for i in range(13))},
                   {"tytul": "x", "etapy": "A,B", "numer": 3}, {"tytul": "x", "dotyczy": "raport:../../x"},
                   {"tytul": "x", "koniec": "jutro"}):
            with self.assertRaises(BladHTTP, msg=kw):
                prace.rozpocznij("s2", teraz=T(10), **kw)
        self.assertFalse(os.path.exists(os.path.join(rdzen.RUNTIME, "prace", "s2.json")))
        with self.assertRaises(BladHTTP):
            prace.zakoncz("s", raport="../r")
        with self.assertRaises(BladHTTP):
            prace.oznacz_blad("s", "")

    def test_usun(self):
        prace.rozpocznij("u", "U")
        prace.usun("u")
        self.assertEqual(prace.lista(), [])
        with self.assertRaises(BladHTTP) as b:
            prace.usun("u")
        self.assertEqual(b.exception.status, 404)


class TestOdpornosc(_KatalogTymczasowy):
    """Pliki, które da się odczytać jako JSON, ale mają dziwne wartości pól; równoległe zmiany jednej pracy."""

    def test_dziwne_wartosci_nie_wywracaja_listy(self):
        prace.rozpocznij("dobra", "Dobra", koniec="11:00", teraz=T(10))
        self.plik("numer.json", {"id": "numer", "tytul": "N", "stan": "w_toku", "numer": "abc", "etapy": ["a", "b"]})
        self.plik("rok1.json", {"id": "rok1", "tytul": "R", "stan": "w_toku", "start": "0001-01-01T00:00"})
        self.plik("rok9999.json", {"id": "rok9999", "tytul": "R", "stan": "w_toku", "start": "2026-11-15T09:00",
                                   "koniec_szacowany": "9999-12-31T23:59:59"})
        self.plik("typy.json", {"id": "typy", "tytul": 5, "stan": "gotowe", "etapy": "nie lista", "numer": True,
                                "dotyczy": "raport:x", "raport": ["x"], "zakonczono": 12345, "opis": {"a": 1},
                                "kto": 7, "komunikat": None})
        self.plik("zly-dotyczy.json", {"id": "zly-dotyczy", "tytul": "D", "stan": "w_toku",
                                       "dotyczy": {"typ": "raport", "id": "../x"}, "numer": 99, "etapy": ["a"]})
        lista = prace.lista(T(10, 5))
        ids = [p["id"] for p in lista]
        self.assertEqual(sorted(ids), ["dobra", "numer", "rok1", "rok9999", "zly-dotyczy"])     # „typy”: gotowa bez daty końca = dawno
        p = {x["id"]: x for x in lista}
        self.assertEqual((p["numer"]["numer"], p["numer"]["postep"]), (1, 0.0))
        self.assertNotIn("start", p["rok1"])
        self.assertNotIn("koniec_szacowany", p["rok9999"])
        self.assertEqual((p["zly-dotyczy"]["numer"], p["zly-dotyczy"].get("dotyczy")), (1, None))
        self.assertEqual(ids[0], "dobra")                                     # w toku z szacowanym końcem — pierwsza
        self.assertTrue(prace.zdrowie()["ok"])
        d = prace._get_prace(None)
        self.assertEqual(d["najblizszy_koniec"], p["dobra"]["koniec_szacowany"])
        json.dumps(d)                                                          # da się wysłać jako JSON

    def test_typy_z_pliku(self):
        self.plik("typy.json", {"id": "typy", "tytul": 5, "stan": "w_toku", "etapy": ["A", 3, None, "B"], "numer": 2,
                                "opis": {"a": 1}, "kto": 7, "start": "2026-11-15T09:00+01:00"})
        p = prace.lista(T(10))[0]
        self.assertEqual((p["tytul"], p["etapy"], p["numer"]), ("typy", ["A", "B"], 2))
        self.assertNotIn("opis", p)
        self.assertNotIn("kto", p)

    def test_zla_praca_pominieta_z_wpisem_w_logu(self):
        prace.rozpocznij("a", "A", teraz=T(10))
        prace.rozpocznij("b", "B", teraz=T(10))
        oryginal = prace._wylicz

        def psuj(p, t):
            if p["id"] == "a":
                raise ValueError("test")
            return oryginal(p, t)
        prace._wylicz = psuj
        try:
            self.assertEqual([p["id"] for p in prace.lista(T(10, 5))], ["b"])
        finally:
            prace._wylicz = oryginal
        self.assertTrue(any("pomijam pracę a" in l for l in self.logi), self.logi)

    def test_biala_lista_pol(self):
        self.plik("obce-pola.json", {"id": "obce-pola", "tytul": "Obce", "stan": "w_toku", "sciezka": "C:\\Users\\jan\\tajne",
                                     "token": "abc123", "etapy": ["C:\\Users\\jan\\etap", "Kontrola"],
                                     "kto": "C:\\Users\\jan", "start": "2026-11-15T09:00+01:00"})
        p = prace.lista(T(10))[0]
        self.assertEqual(set(p) - set(prace.POLA) - {"zostalo_min", "po_czasie_min", "przeterminowana", "postep"}, set())
        tekst = json.dumps(p, ensure_ascii=False)
        for zakazane in ("jan", "token", "abc123", "sciezka", "tajne"):
            self.assertNotIn(zakazane, tekst)
        # kolejny zapis (zmiana etapu) nie przenosi obcych pól dalej
        prace.ustaw_etap("obce-pola", etap="Kontrola", teraz=T(10, 5))
        zapis = rdzen.czytaj_json(os.path.join(rdzen.RUNTIME, "prace", "obce-pola.json"))
        self.assertNotIn("token", zapis)
        self.assertNotIn("sciezka", zapis)
        self.assertEqual(zapis["numer"], 2)
        # kto ze ścieżką — czyszczone także przy zapisie
        q = prace.rozpocznij("kto", "K", kto="C:\\Users\\jan", teraz=T(10))
        self.assertNotIn("jan", q.get("kto", ""))
        self.assertNotIn("jan", json.dumps(rdzen.czytaj_json(os.path.join(rdzen.RUNTIME, "prace", "kto.json"))))

    def test_odczyt_w_trakcie_podmiany_jest_ponawiany(self):
        prace.rozpocznij("p", "P", teraz=T(10))
        sciezka = os.path.join(rdzen.RUNTIME, "prace", "p.json")
        prawdziwy_open = open
        licznik = {"n": 0}

        def zajety_open(plik, *a, **kw):                                      # dwa pierwsze odczyty: plik zajęty
            if os.path.abspath(str(plik)) == os.path.abspath(sciezka) and licznik["n"] < 2:
                licznik["n"] += 1
                raise PermissionError(13, "Permission denied")
            return prawdziwy_open(plik, *a, **kw)
        import builtins
        builtins.open = zajety_open
        try:
            self.assertEqual([x["id"] for x in prace.lista(T(10, 5))], ["p"])
        finally:
            builtins.open = prawdziwy_open
        self.assertEqual(licznik["n"], 2)
        self.assertFalse(any("zepsuty" in l for l in self.logi), self.logi)       # chwilowa blokada to nie zepsuty plik

    def test_blokada(self):
        with prace._blokada("x"):
            with self.assertRaises(BladHTTP) as b:
                with prace._blokada("x", czekaj_s=0.2):
                    pass
            self.assertEqual(b.exception.status, 409)
        with prace._blokada("x", czekaj_s=0.2):                               # zwolniona — można znowu
            pass
        stara = os.path.join(rdzen.RUNTIME, "prace", "y.lock")                # po procesie, który padł
        open(stara, "w").close()
        os.utime(stara, (os.path.getmtime(stara) - 60,) * 2)
        prace.rozpocznij("y", "Y", teraz=T(10))
        self.assertFalse(os.path.exists(stara))

    def test_rownolegle_zmiany_z_kilku_procesow(self):
        # trzy procesy po 25 razy zmieniają etap tej samej pracy, a „serwer” (ten proces) w tym czasie czyta listę:
        # żadne wywołanie nie kończy się „Nie ma pracy”, praca nie znika z listy, w logu nie ma „zepsuty plik”
        prace.rozpocznij("rownolegle", "Równolegle", etapy="A,B,C", teraz=T(10))
        skrypt = os.path.join(self.tmp, "zmieniaj.py")
        with open(skrypt, "w", encoding="utf-8") as f:
            f.write("import sys\nsys.path.insert(0, %r)\nfrom bc import prace\nbledy = 0\n"
                    "for i in range(25):\n"
                    "    try:\n"
                    "        prace.ustaw_etap('rownolegle', numer=1 + i %% 3)\n"
                    "    except Exception as e:\n"
                    "        bledy += 1\n"
                    "        print('BLAD', type(e).__name__, getattr(e, 'komunikat', e))\n"
                    "sys.exit(1 if bledy else 0)\n" % PANEL)
        env = dict(os.environ, BC_PANEL_RUNTIME=rdzen.RUNTIME, BC_PANEL_DANE=os.path.join(self.tmp, "dane"),
                   PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
        procesy = [subprocess.Popen([sys.executable, "-B", skrypt], env=env, cwd=self.tmp, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, creationflags=0x08000000 if os.name == "nt" else 0)
                   for _ in range(3)]
        braki = 0
        while any(p.poll() is None for p in procesy):
            if "rownolegle" not in [x["id"] for x in prace.lista()]:
                braki += 1
            time.sleep(0.005)
        wyniki = [(p.wait(60), p.stdout.read().decode("utf-8", "replace")) for p in procesy]
        for p in procesy:
            p.stdout.close()
        self.assertEqual([k for k, _ in wyniki], [0, 0, 0], [w for _, w in wyniki])
        self.assertEqual(braki, 0)
        self.assertFalse(any("zepsuty" in l for l in self.logi), self.logi)
        log_procesow = os.path.join(rdzen.RUNTIME, "panel.log")
        if os.path.exists(log_procesow):
            with open(log_procesow, encoding="utf-8") as f:
                self.assertNotIn("zepsuty", f.read())
        self.assertEqual([x for x in os.listdir(os.path.join(rdzen.RUNTIME, "prace")) if x.endswith((".lock", ".tmp"))], [])


class TestLogWTestach(unittest.TestCase):
    def test_przygotowanie_serwera_nie_pisze_do_logu_panelu(self):
        # przygotowanie prac dla serwera testowego (TestPraceAPI.przygotuj) nie może pisać do pliku logu z danych
        # lokalnych procesu testów — „prawdziwy” log udaje tu plik w katalogu tymczasowym
        tmp = tempfile.mkdtemp(prefix="bc_test_prace_log_")
        stary_log = rdzen.PLIK_LOGU
        udawany = os.path.join(tmp, "udawany_prawdziwy_panel.log")
        rdzen.PLIK_LOGU = udawany
        try:
            runtime = os.path.join(tmp, "runtime")
            TestPraceAPI.przygotuj(runtime)
            self.assertTrue(os.path.isfile(os.path.join(runtime, "prace", "walka-v2.json")))
            self.assertFalse(os.path.exists(udawany))
            self.assertEqual(rdzen.PLIK_LOGU, udawany)                        # przywrócone po przygotowaniu
        finally:
            rdzen.PLIK_LOGU = stary_log
            shutil.rmtree(tmp, ignore_errors=True)


class TestNarzedzie(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_praca_cli_")
        self.env = dict(os.environ, BC_PANEL_RUNTIME=os.path.join(self.tmp, "runtime"),
                        BC_PANEL_DANE=os.path.join(self.tmp, "dane"), PYTHONDONTWRITEBYTECODE="1",
                        PYTHONIOENCODING="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def uruchom(self, *argv):
        p = subprocess.run([sys.executable, "-B", os.path.join(PANEL, "narzedzia", "praca.py")] + list(argv),
                           capture_output=True, env=self.env, timeout=60, cwd=self.tmp,
                           creationflags=0x08000000 if os.name == "nt" else 0)
        return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")

    def test_cykl_pracy(self):
        kod, out, err = self.uruchom("start", "--id", "biom-las", "--tytul", "Biom Las — mapa z klocków",
                                     "--etapy", "Plan,Budowa,Kontrola", "--koniec", "+90m", "--kto", "Claude (test)",
                                     "--dotyczy", "raport:r-20261115-101500-ab12")
        self.assertEqual(kod, 0, err)
        self.assertIn("Start pracy: biom-las", out)
        self.assertIn("etap: Plan (1 z 3)", out)
        self.assertRegex(out, r"koniec ok\. \S+ \(za (1 h 30 min|1 h 29 min)\)")
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "runtime", "prace", "biom-las.json")))
        kod, out, err = self.uruchom("etap", "--id", "biom-las", "--etap", "Kontrola", "--koniec", "+20m")
        self.assertEqual(kod, 0, err)
        self.assertIn("Kontrola (3 z 3)", out)
        kod, out, err = self.uruchom("lista")
        self.assertEqual(kod, 0, err)
        self.assertIn("biom-las", out)
        self.assertRegex(out, r"za (20|19) min")
        kod, out, err = self.uruchom("koniec", "--id", "biom-las", "--raport", "r-20261115-121500-cd34")
        self.assertEqual(kod, 0, err)
        self.assertIn("gotowe", out)
        self.assertIn("r-20261115-121500-cd34", out)
        kod, out, _ = self.uruchom("lista", "--json")
        d = json.loads(out)["prace"][0]
        self.assertEqual((d["stan"], d["raport"], d["postep"]), ("gotowe", "r-20261115-121500-cd34", 1.0))
        kod, out, err = self.uruchom("usun", "--id", "biom-las")
        self.assertEqual(kod, 0, err)
        self.assertEqual(self.uruchom("lista")[1].strip(), "Brak prac w toku.")

    def test_bledy(self):
        kod, out, err = self.uruchom("start", "--id", "x", "--tytul", "X", "--koniec", "25:99", "--kto", "t")
        self.assertNotEqual(kod, 0)
        self.assertIn("Błąd:", err)
        self.assertIn("godziny", err)
        kod, _, err = self.uruchom("start", "--id", "../zle", "--tytul", "X", "--kto", "t")
        self.assertNotEqual(kod, 0)
        self.assertIn("identyfikator", err)
        kod, _, err = self.uruchom("etap", "--id", "nie-ma", "--etap", "A")
        self.assertNotEqual(kod, 0)
        self.assertIn("Nie ma pracy", err)
        kod, out, _ = self.uruchom("blad", "--id", "nie-ma", "--komunikat", "x", "--json")
        self.assertNotEqual(kod, 0)
        self.assertIn("blad", json.loads(out))
        for koniec in ("9999-12-31T23:59", "0001-01-01T00:00"):              # dawniej traceback ze ścieżką (OSError)
            kod, out, err = self.uruchom("start", "--id", "x", "--tytul", "X", "--koniec", koniec, "--kto", "t")
            self.assertEqual(kod, 1, out + err)
            self.assertIn("Błąd:", err)
            self.assertIn("zakresem", err)
            self.assertNotIn("Traceback", err)
            self.assertNotIn(os.path.expanduser("~"), err)
        self.assertNotEqual(self.uruchom()[0], 0)                             # bez polecenia: pomoc i kod 2
        self.assertNotEqual(self.uruchom("start", "--id", "x")[0], 0)        # brak --tytul (argparse)

    def test_wstrzymaj_wznow_i_po_czasie(self):
        self.assertEqual(self.uruchom("start", "--id", "w", "--tytul", "W", "--kto", "t",
                                      "--koniec", (datetime.datetime.now().astimezone() - datetime.timedelta(minutes=5)).isoformat())[0], 0)
        kod, out, _ = self.uruchom("lista")
        self.assertIn("po czasie o", out)
        kod, out, err = self.uruchom("wstrzymaj", "--id", "w", "--komunikat", "czeka na decyzję")
        self.assertEqual(kod, 0, err)
        self.assertIn("wstrzymane", out)
        kod, out, err = self.uruchom("wznow", "--id", "w", "--koniec", "+1h")
        self.assertEqual(kod, 0, err)
        self.assertIn("w toku", out)
        self.assertRegex(out, r"za (1 h|59 min)")


class TestPraceAPI(test_api.SerwerTestowy):
    @classmethod
    def przygotuj(cls, runtime):
        with dane_lokalne_testu(runtime):
            teraz = datetime.datetime.now().astimezone()
            prace.rozpocznij("walka-v2", "Walka v2 — poprawki", etapy="Plan,Poprawki,Kontrola", numer=2,
                             koniec="+35m", dotyczy="raport:r-20261115-090000-ab12", kto="Claude (test)",
                             opis="Pliki w C:\\Users\\tester\\Desktop")
            prace.rozpocznij("biom-las", "Biom Las", koniec=(teraz - datetime.timedelta(minutes=10)).isoformat(),
                             kto="Claude (test)", teraz=teraz - datetime.timedelta(hours=1))
            prace.rozpocznij("modele", "Gołe modele", kto="Claude (test)", teraz=teraz - datetime.timedelta(hours=1))
            prace.zakoncz("modele", raport="r-20261115-110000-cd34")
            rdzen.zapisz_json(os.path.join(runtime, "prace", "dziwna.json"),          # ręcznie zapisany, dziwny plik
                              {"id": "dziwna", "tytul": "Dziwna", "stan": "wstrzymane", "numer": "abc", "etapy": ["a", "b"],
                               "start": "0001-01-01T00:00", "koniec_szacowany": "9999-12-31T23:59:59",
                               "sciezka": "C:\\Users\\tester\\tajne", "token": "abc123", "kto": "C:\\Users\\tester"})

    def test_lista_dla_goscia(self):
        s, o, _ = self.get("/api/prace", zdalny=True)
        self.assertEqual(s, 200, o)
        self.assertPola(o, ["prace", "teraz", "w_toku", "najblizszy_koniec"])
        self.assertEqual([p["id"] for p in o["prace"]], ["biom-las", "walka-v2", "dziwna", "modele"])
        self.assertEqual(o["w_toku"], 2)
        biom, walka, dziwna, modele = o["prace"]
        # dziwny plik nie wywraca listy (wcześniej 500), a z jego pól idą dalej tylko znane, z właściwymi typami
        self.assertEqual(set(dziwna) - set(prace.POLA) - {"zostalo_min", "po_czasie_min", "przeterminowana", "postep"}, set())
        self.assertEqual((dziwna["numer"], dziwna["etapy"]), (1, ["a", "b"]))
        self.assertNotIn("start", dziwna)
        self.assertNotIn("koniec_szacowany", dziwna)
        self.assertTrue(biom["przeterminowana"])
        self.assertGreaterEqual(biom["po_czasie_min"], 9)
        self.assertIn(walka["zostalo_min"], (34, 35))
        self.assertEqual(walka["dotyczy"], {"typ": "raport", "id": "r-20261115-090000-ab12"})
        self.assertEqual((modele["stan"], modele["postep"], modele["raport"]), ("gotowe", 1.0, "r-20261115-110000-cd34"))
        tekst = json.dumps(o, ensure_ascii=False)
        self.assertNotIn("tester", tekst)
        for zakazane in ("token", "abc123", "sciezka", "tajne"):
            self.assertNotIn(zakazane, tekst)
        self.assertNotIn(self.tmp.replace("\\", "\\\\"), tekst)
        self.assertNotIn("runtime", tekst)
        self.assertNotIn(":\\\\", tekst)                                      # żadnej ścieżki z dyskiem

    def test_bez_kodu_dostepu(self):
        s, o, _ = self.get("/api/prace", klucz=False, naglowki={"X-Forwarded-For": "192.168.1.50"})
        self.assertEqual(s, 401, o)

    def test_zdrowie(self):
        s, o, _ = self.get("/api/zdrowie", timeout=60)
        self.assertTrue(o["moduly"]["prace"]["ok"], o["moduly"].get("prace"))
        self.assertEqual(o["szczegoly"]["prace"]["w_toku"], 2)
        self.assertTrue(o["szczegoly"]["prace"]["ok"], o["szczegoly"]["prace"])        # dziwny plik nie psuje zdrowia
        s, o, _ = self.get("/api/zdrowie", zdalny=True, timeout=60)
        self.assertEqual(o["szczegoly"]["prace"], {"ok": True})


if __name__ == "__main__":
    unittest.main()
