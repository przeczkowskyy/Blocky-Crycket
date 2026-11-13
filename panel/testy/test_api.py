# -*- coding: utf-8 -*-
"""Test dymny całego API panelu: prawdziwy serwer w osobnym procesie, prawdziwe żądania HTTP.

Uruchomienie (z katalogu panel/):  python -m unittest testy.test_api
Wszystkie testy:                   python -m unittest discover -s testy -t .

- Serwer startuje na wolnym porcie z katalogami tymczasowymi (BC_PANEL_DANE, BC_PANEL_RUNTIME) — prawdziwe
  panel/dane i dane lokalne komputera zostają nietknięte; katalog tymczasowy jest usuwany na końcu.
- Bez Roblox Studio (STUDIO_MCP_CMD = mostek, który od razu się kończy), bez sieci (universeId wyłączone
  w konfiguracji lokalnej), bez przebiegu agenta i bez robotnika głosówek (atrapa pliku pid).
- Git tylko czyta (zdrowie, obecność). GET /api/git/stan nie jest wołany, bo uruchamia `git fetch` w tle;
  POST /api/git/pobierz i /api/git/wyslij są sprawdzane wyłącznie jako odmowy (403).
- Sejf B&C jest czytany naprawdę (tylko odczyt) — testy sprawdzają kształt odpowiedzi, nie treść notatek.
- Zapis do sejfu (TestZapisSejfuAPI) idzie WYŁĄCZNIE do tymczasowego sejfu wskazanego w konfiguracji lokalnej
  serwera testowego; klucz zatwierdzania (plik klucz_gd.txt) też jest tymczasowy.
"""
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request

PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(PANEL)
MID = "20261112-100000-test"                                   # migawka przygotowana w katalogu tymczasowym
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 64 + b"\xff\xd9"         # wystarczy nagłówek JPG — serwer tylko serwuje bajty


def _wolny_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class SerwerTestowy(unittest.TestCase):
    """Prawdziwy serwer panelu w osobnym procesie na katalogach tymczasowych (bez testów — tylko rozruch i klient)."""
    port = None
    proc = None
    tmp = None
    token = None

    @classmethod
    def konfiguracja_lokalna(cls):
        """Konfiguracja lokalna serwera testowego (podklasy mogą np. wskazać tymczasowy sejf)."""
        return {"gra": {"universeId": None}}                            # analityka bez sieci

    @classmethod
    def przygotuj(cls, runtime):
        """Miejsce na dodatkowe pliki w danych lokalnych przed startem serwera."""

    # ------------------------------------------------------------------ serwer
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="bc_test_api_")
        dane, runtime = os.path.join(cls.tmp, "dane"), os.path.join(cls.tmp, "runtime")
        os.makedirs(runtime)
        with open(os.path.join(runtime, "konfiguracja.lokalna.json"), "w", encoding="utf-8") as f:
            json.dump(cls.konfiguracja_lokalna(), f, ensure_ascii=False)
        cls.przygotuj(runtime)
        cls.klucz = "klucz-lokalny-testowy-0123456789"                  # serwer bierze istniejący plik (min. 20 znaków)
        with open(os.path.join(runtime, "klucz_lokalny.txt"), "w", encoding="utf-8") as f:
            f.write(cls.klucz + "\n")
        cls._migawka(os.path.join(dane, "podglad", MID))
        cls.port = _wolny_port()
        env = dict(os.environ, BC_PANEL_DANE=dane, BC_PANEL_RUNTIME=runtime, PYTHONDONTWRITEBYTECODE="1",
                   PYTHONIOENCODING="utf-8", STUDIO_MCP_CMD="exit 1")
        cls.log = open(os.path.join(cls.tmp, "serwer.log"), "wb")
        cls.proc = subprocess.Popen([sys.executable, "-B", os.path.join(PANEL, "serwer.py"), "--bez-przegladarki",
                                     "--port", str(cls.port)], cwd=REPO, env=env, stdin=subprocess.DEVNULL,
                                    stdout=cls.log, stderr=subprocess.STDOUT,
                                    creationflags=0x08000000 if os.name == "nt" else 0)
        koniec = time.time() + 30
        while True:
            try:
                s, o, _ = cls.zadanie("GET", "/api/ping", timeout=2)
                if s == 200 and o.get("pid") == cls.proc.pid:
                    break
            except OSError:
                pass
            if cls.proc.poll() is not None or time.time() > koniec:
                cls.tearDownClass()
                raise RuntimeError("Serwer panelu nie wystartował (log: %s)" % os.path.join(cls.tmp, "serwer.log"))
            time.sleep(0.2)
        with open(os.path.join(runtime, "token.txt"), encoding="utf-8") as f:
            cls.token = f.read().strip()

    @classmethod
    def tearDownClass(cls):
        if cls.proc is not None and cls.proc.poll() is None:
            cls.proc.terminate()
            try:
                cls.proc.wait(10)
            except subprocess.TimeoutExpired:
                cls.proc.kill()
        try:
            cls.log.close()
        except Exception:
            pass
        for _ in range(20):                                    # Windows: pliki potrafią być chwilę zablokowane
            shutil.rmtree(cls.tmp, ignore_errors=True)
            if not os.path.exists(cls.tmp):
                break
            time.sleep(0.25)

    @staticmethod
    def _migawka(folder):
        os.makedirs(folder)
        czesci = {"wersja": 1, "grupy": ["Workspace", "Workspace/Baza/Karczma"], "materialy": ["Plastic", "Wood"],
                  "czesci": [[0, 0, 0, -0.5, 0, 0, 0, 0, 512, 1, 512, "A3A2A5", 0, 0, "Baseplate"],
                             [3, 1, 4, 3, 2, 0, 1.5708, 0, 4, 2, 6, "8B5A2B", 1, 0, "Dach ąę"]]}
        meta = {"id": MID, "tytul": "Migawka testowa", "opis": "", "kto": "Tester", "czas": "2026-11-12T10:00:00+01:00",
                "zrodlo": "studio", "czesci": 2, "grupy": [{"sciezka": "Workspace", "czesci": 1},
                                                           {"sciezka": "Workspace/Baza/Karczma", "czesci": 1}],
                "zrzuty": ["zrzut_1.jpg"], "zakres": {"min": [-256, -0.5, -256], "max": [256, 4, 256]},
                "miejsce": {"placeId": 1, "nazwa": "Test"}}
        with open(os.path.join(folder, "czesci.json"), "w", encoding="utf-8") as f:
            json.dump(czesci, f, ensure_ascii=False, separators=(",", ":"))
        with open(os.path.join(folder, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False)
        with open(os.path.join(folder, "zrzut_1.jpg"), "wb") as f:
            f.write(JPG)

    # ------------------------------------------------------------------ klient
    @classmethod
    def zadanie(cls, metoda, sciezka, cialo=None, zdalny=False, xbc=True, ct="application/json", surowe=None,
                kto=None, naglowki=None, timeout=30, bajty=False, klucz=True, gd=None):
        """Zwraca (status, obiekt JSON albo None, nagłówki); z bajty=True trzecim elementem są (nagłówki, bajty).

        Domyślnie żądanie idzie jak z przeglądarki przy komputerze (z kluczem lokalnym); `zdalny=True` udaje telefon
        przez pośrednika z poprawnym kodem dostępu, `klucz=False` — obcy program na tym samym komputerze."""
        h = {}
        if metoda == "POST":
            if xbc:
                h["X-BC"] = "1"
            h["Content-Type"] = ct
        if zdalny:                                             # jak telefon przez pośrednika, z poprawnym kodem
            h["X-Forwarded-For"] = "192.168.1.50"
            h["X-BC-Token"] = cls.token
        elif klucz:
            h["X-BC-Lokalny"] = cls.klucz
        if kto:
            h["X-BC-Kto"] = urllib.parse.quote(kto)
        if gd:
            h["X-BC-GD"] = gd
        h.update(naglowki or {})
        dane = surowe if surowe is not None else (json.dumps(cialo).encode("utf-8") if cialo is not None else None)
        if metoda == "POST" and dane is None:
            dane = b""
        req = urllib.request.Request("http://127.0.0.1:%d%s" % (cls.port, sciezka), data=dane, method=metoda,
                                     headers=h)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                status, nagl, b = r.status, r.headers, r.read()
        except urllib.error.HTTPError as e:
            status, nagl, b = e.code, e.headers, e.read()
        obj = None
        if "json" in (nagl.get("Content-Type") or ""):
            obj = json.loads(b.decode("utf-8"))
        return (status, obj, (nagl, b)) if bajty else (status, obj, nagl)

    def get(self, sciezka, **kw):
        return self.zadanie("GET", sciezka, **kw)

    def post(self, sciezka, cialo=None, **kw):
        return self.zadanie("POST", sciezka, cialo, **kw)

    def assertPola(self, obj, pola):
        self.assertIsInstance(obj, dict)
        brak = [p for p in pola if p not in obj]
        self.assertFalse(brak, "brak pól %s w %s" % (brak, json.dumps(obj, ensure_ascii=False)[:300]))

    def assertBlad(self, wynik, status):
        s, o, _ = wynik
        self.assertEqual(s, status, o)
        self.assertTrue(o and isinstance(o.get("blad"), str) and o["blad"], o)


class TestAPI(SerwerTestowy):

    # ------------------------------------------------------------------ rdzeń i zabezpieczenia
    def test_rdzen(self):
        s, o, _ = self.get("/api/ping")
        self.assertEqual(s, 200)
        self.assertPola(o, ["ok", "app", "wersja", "start", "pid", "port", "lan"])
        self.assertEqual((o["app"], o["port"], o["lan"]), ("bc-panel", self.port, False))
        s, o, _ = self.get("/api/ja", kto="Paweł Ż")
        self.assertPola(o, ["kto", "lokalny", "gospodarz", "tryb_statyczny", "wersja", "game_director", "decydent",
                            "zapis_sejfu"])
        self.assertEqual((o["kto"], o["lokalny"], o["tryb_statyczny"]), ("Paweł Ż", True, False))
        self.assertFalse(o["game_director"])                                         # bez klucza zatwierdzania
        self.assertTrue(o["decydent"])                                               # ale przy komputerze z panelem
        s, o, _ = self.get("/api/ja", zdalny=True)
        self.assertEqual((s, o["lokalny"], o["kto"], o["decydent"]), (200, False, "gość", False))
        s, o, _ = self.get("/api/konfiguracja")
        self.assertPola(o, ["port", "gra", "sejfy", "agent", "glos"])
        self.assertPola(o["gra"], ["nazwa", "universeId", "placeId"])
        self.assertTrue(all(set(x) == {"id", "nazwa"} for x in o["sejfy"]), o["sejfy"])
        s, o, _ = self.get("/api/dostep")
        self.assertEqual(s, 200)
        self.assertPola(o, ["lan", "token", "adresy", "podpowiedz", "link_lokalny"])
        self.assertTrue(o["link_lokalny"].endswith("/?l=" + self.klucz))
        self.assertBlad(self.get("/api/dostep", zdalny=True), 403)

    def test_klucz_lokalny(self):
        """Samo połączenie z 127.0.0.1 nie daje praw osoby przy komputerze — potrzebny jest klucz lokalny."""
        self.assertBlad(self.get("/api/ja", klucz=False), 401)                       # obcy program na tym komputerze
        self.assertBlad(self.get("/api/ja", klucz=False, naglowki={"X-BC-Lokalny": "zly-klucz-0123456789012345"}), 401)
        s, o, _ = self.get("/api/ja", klucz=False, naglowki={"X-BC-Token": self.token})
        self.assertEqual((s, o["lokalny"], o["kto"]), (200, False, "gość"))          # sam kod dostępu = prawa gościa
        self.assertBlad(self.get("/api/dostep", klucz=False, naglowki={"X-BC-Token": self.token}), 403)
        s, o, _ = self.get("/api/ja", naglowki={"Cookie": "bc_l=" + self.klucz}, klucz=False)
        self.assertEqual((s, o["lokalny"]), (200, True))                             # ciasteczko przeglądarki
        # klucz przyniesiony przez pośrednika (tunel, przekierowanie portu) nie działa
        s, o, _ = self.get("/api/ja", zdalny=True, naglowki={"X-BC-Lokalny": self.klucz})
        self.assertEqual((s, o["lokalny"]), (200, False))
        self.assertBlad(self.get("/api/ja", klucz=False, naglowki={"X-BC-Lokalny": self.klucz,
                                                                   "Cf-Connecting-Ip": "203.0.113.7"}), 401)
        # wejście z adresu startowego: ciasteczko i przekierowanie na adres bez klucza
        import http.client
        c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        try:
            c.request("GET", "/?l=" + self.klucz)
            r = c.getresponse()
            r.read()
            self.assertIn(r.status, (302, 303))
            self.assertEqual(r.getheader("Location"), "/")
            ciastko = r.getheader("Set-Cookie") or ""
            self.assertTrue(ciastko.startswith("bc_l=" + self.klucz + ";"), ciastko)
            self.assertIn("HttpOnly", ciastko)
            self.assertIn("SameSite=Strict", ciastko)
            c.request("GET", "/")                                                    # bez klucza: strona kodu dostępu
            r = c.getresponse()
            tresc = r.read().decode("utf-8")
            self.assertEqual(r.status, 401)
            self.assertIn("kod dostępu", tresc)
        finally:
            c.close()
        # zdrowie dla gościa: bez lokalnych ścieżek
        s, o, _ = self.get("/api/zdrowie", zdalny=True, timeout=60)
        self.assertEqual(s, 200)
        self.assertNotIn("repo", o["rdzen"])
        self.assertNotIn("runtime", o["rdzen"])

    def test_zabezpieczenia(self):
        self.assertBlad(self.get("/api/ping", naglowki={"X-Forwarded-For": "1.2.3.4"}), 401)    # bez kodu dostępu
        self.assertBlad(self.get("/api/ping", naglowki={"Host": "zly.example:%d" % self.port}), 403)
        self.assertBlad(self.post("/api/obecnosc/puls", {"klient": "x"}, xbc=False), 403)
        self.assertBlad(self.post("/api/obecnosc/puls", {"klient": "x"}, naglowki={"Origin": "http://zly.pl"}), 403)
        self.assertBlad(self.post("/api/obecnosc/puls", {"klient": "x"}, ct="text/plain"), 415)
        self.assertBlad(self.get("/api/nie-ma-takiej-trasy"), 404)
        self.assertBlad(self.post("/api/ping", {}), 405)
        s, _, (nagl, b) = self.get("/", bajty=True)
        self.assertEqual(s, 200)
        self.assertTrue(nagl["Content-Type"].startswith("text/html"))
        for zla in ("/../serwer.py", "/%2e%2e/serwer.py", "/..%5Cserwer.py", "/wspolne/../../serwer.py",
                    "/../bc/rdzen.py"):
            self.assertEqual(self.get(zla)[0], 404, zla)

    def test_zdrowie(self):
        s, o, _ = self.get("/api/zdrowie", timeout=60)
        self.assertEqual(s, 200)
        self.assertPola(o, ["rdzen", "moduly", "szczegoly"])
        zle = {k: v for k, v in o["moduly"].items() if k != "statyczny" and not v.get("ok")}
        self.assertFalse(zle, "moduły z błędem: %s" % zle)
        for nazwa in ("sejf", "zapis", "gitsync", "obecnosc", "studio", "podglad", "analityka", "raporty", "agent",
                      "glos"):
            self.assertIn(nazwa, o["moduly"])

    # ------------------------------------------------------------------ sejf
    def test_sejf(self):
        s, o, _ = self.get("/api/sejf/plan")
        self.assertEqual(s, 200)
        self.assertPola(o, ["roadmapa", "zadania", "decyzje", "pytania", "dziennik", "zrodla"])
        self.assertPola(o["roadmapa"], ["fazy", "propozycje"])
        self.assertPola(o["zadania"], ["sekcje", "otwarte", "zrobione"])
        for f in o["roadmapa"]["fazy"]:
            self.assertPola(f, ["nazwa", "opis", "status_tekst", "aktywna", "pozycje", "postep"])
            self.assertTrue(0 <= f["postep"] <= 100)
        for d in o["decyzje"]:
            self.assertPola(d, ["id", "tytul", "status", "emoji", "kategoria", "meta", "opis_md"])
            self.assertIn(d["status"], ("zatwierdzona", "do_decyzji", "propozycja", "odrzucona", "zastapiona"))
        for p in o["pytania"]:
            self.assertPola(p, ["nr", "tytul", "tresc_md", "odpowiedz_md", "otwarte"])
        self.assertLessEqual(len(o["dziennik"]), 30)

        s, o, _ = self.get("/api/sejf/siec")
        self.assertEqual(s, 200)
        self.assertPola(o, ["wezly", "krawedzie", "kategorie", "nierozwiazane", "statystyki"])
        n = len(o["wezly"])
        self.assertGreater(n, 0)
        for i, w in enumerate(o["wezly"]):
            self.assertPola(w, ["id", "tytul", "sejf", "folder", "kategoria", "status", "tagi", "slowa", "zmieniono",
                                "stopien", "sciezka"])
            self.assertEqual(w["id"], i)
        self.assertTrue(all(len(k) == 2 and 0 <= k[0] < n and 0 <= k[1] < n for k in o["krawedzie"]))
        self.assertEqual(o["statystyki"]["notatki"], n)

        sciezka = o["wezly"][0]["sciezka"]
        s, o, _ = self.get("/api/sejf/notatka?sciezka=" + urllib.parse.quote(sciezka))
        self.assertEqual(s, 200, o)
        self.assertPola(o, ["sciezka", "tytul", "sejf", "frontmatter", "tresc_md", "linki_wy", "linki_we", "zmieniono"])
        for zla in ("panel/serwer.py", "B&C/../panel/serwer.py", "../B&C/x.md", "C:/Windows/win.ini", "/etc/passwd"):
            self.assertBlad(self.get("/api/sejf/notatka?sciezka=" + urllib.parse.quote(zla)), 403)
        self.assertBlad(self.get("/api/sejf/notatka?sciezka=" + urllib.parse.quote("B&C/Nie ma takiej notatki.md")), 404)
        self.assertBlad(self.get("/api/sejf/notatka"), 400)
        s, o, _ = self.get("/api/sejf/szukaj?q=a")
        self.assertEqual(s, 200)
        self.assertLessEqual(len(o["wyniki"]), 40)
        for w in o["wyniki"][:3]:
            self.assertPola(w, ["sciezka", "tytul", "sejf", "fragment"])
        self.assertEqual(self.get("/api/sejf/szukaj")[1], {"wyniki": []})

    # ------------------------------------------------------------------ git (tylko odmowy)
    def test_git_tylko_lokalnie(self):
        for trasa in ("/api/git/pobierz", "/api/git/wyslij"):
            self.assertBlad(self.post(trasa, {}, zdalny=True), 403)
            self.assertBlad(self.post(trasa, {}, xbc=False), 403)

    # ------------------------------------------------------------------ obecność, Studio, analityka (bez Studio)
    def test_obecnosc(self):
        s, o, _ = self.post("/api/obecnosc/puls", {"klient": "karta-test", "widok": "pulpit"}, kto="Paweł")
        self.assertEqual(s, 200, o)
        self.assertPola(o, ["panel", "studio", "git"])
        wpis = next(p for p in o["panel"] if p["kto"] == "Paweł")
        self.assertPola(wpis, ["kto", "widok", "od", "ostatnio", "lokalny"])
        self.assertEqual((wpis["widok"], wpis["lokalny"]), ("pulpit", True))
        self.assertEqual(o["studio"]["dostepne"], False)
        self.assertEqual(o["studio"]["osoby"], [])
        for g in o["git"][:1]:
            self.assertPola(g, ["autor", "ostatnio", "temat"])
        self.assertBlad(self.post("/api/obecnosc/puls", {"widok": "x"}), 400)
        s, o, _ = self.post("/api/obecnosc/puls", {"klient": "telefon", "widok": "plan"}, zdalny=True)
        self.assertTrue(any(p["lokalny"] is False for p in o["panel"]))
        self.assertEqual(self.get("/api/obecnosc")[0], 200)

    def test_studio_bez_studia(self):
        t = time.time()
        s, o, _ = self.get("/api/studio/stan")
        self.assertEqual(s, 200)
        self.assertLess(time.time() - t, 10)
        self.assertPola(o, ["mostek", "polaczone", "osoby"])
        self.assertFalse(o["polaczone"])
        self.assertTrue(o.get("blad"))
        s, o, _ = self.get("/api/studio/konsola")
        self.assertEqual(s, 200)
        self.assertPola(o, ["linie", "bledy", "ostrzezenia"])
        self.assertEqual((o["linie"], o["bledy"]), ([], 0))

    def test_analityka_bez_sieci(self):
        s, o, _ = self.get("/api/analityka")
        self.assertEqual(s, 200)
        self.assertPola(o, ["gra", "historia", "studio", "telemetria", "robuxy"])
        self.assertPola(o["gra"], ["universeId", "placeId", "gracze", "wizyty", "ulubione", "zaktualizowano", "publiczna"])
        self.assertFalse(o["gra"]["publiczna"])
        self.assertTrue(o["gra"].get("opis"))
        self.assertPola(o["studio"], ["polaczone", "bledy", "ostrzezenia", "konsola"])
        self.assertPola(o["telemetria"], ["podlaczona", "opis"])
        self.assertPola(o["robuxy"], ["dostepne", "opis"])

    def test_telemetria(self):
        """Telemetria gry bez klucza i bez sieci: „wyłączona” z powodem; dane przykładowe tylko przy komputerze."""
        s, o, _ = self.get("/api/telemetria?godzin=24")
        self.assertEqual(s, 200)
        self.assertPola(o, ["wlaczona", "zrodlo", "kod", "powod", "kroki", "plik_konfiguracji"])
        self.assertEqual((o["wlaczona"], o["zrodlo"], o["kod"]), (False, None, "brak_universe"))
        s, o, _ = self.get("/api/telemetria", zdalny=True)
        self.assertEqual((s, o["wlaczona"]), (200, False))
        self.assertNotIn("plik_konfiguracji", o)                                     # lokalna ścieżka nie dla gościa
        self.assertBlad(self.get("/api/telemetria?probka=1", zdalny=True), 403)
        self.assertBlad(self.get("/api/telemetria?probka=1", klucz=False, naglowki={"X-BC-Token": self.token}), 403)
        s, o, _ = self.get("/api/telemetria?godzin=6&probka=1")
        self.assertEqual((s, o["wlaczona"], o["zrodlo"], o["przykladowe"]), (200, False, "probka", True))
        self.assertPola(o, ["powod", "okres", "suma", "godziny", "zakupy", "bledy", "serwery"])
        self.assertPola(o["suma"], ["sesje", "sredni_czas_sesji_s", "ccu_max", "robuxy", "zakupy", "bledy"])
        self.assertEqual(len(o["godziny"]), 6)
        self.assertIn("telemetria", self.get("/api/zdrowie", timeout=60)[1]["moduly"])

    # ------------------------------------------------------------------ podgląd
    def test_podglad(self):
        s, o, _ = self.get("/api/podglad")
        self.assertEqual(s, 200)
        self.assertPola(o, ["migawki", "najnowsza"])
        self.assertEqual(o["najnowsza"]["id"], MID)
        self.assertPola(o["najnowsza"], ["id", "tytul", "opis", "kto", "czas", "zrodlo", "czesci", "grupy", "zrzuty",
                                         "zakres", "miejsce"])
        s, o, _ = self.get("/api/podglad/%s/czesci" % MID)
        self.assertEqual(s, 200)
        self.assertPola(o, ["wersja", "grupy", "materialy", "czesci"])
        self.assertEqual(o["czesci"][1][14], "Dach ąę")
        s, _, (nagl, b) = self.get("/api/podglad/%s/plik/zrzut_1.jpg" % MID, bajty=True)
        self.assertEqual((s, nagl["Content-Type"], b), (200, "image/jpeg", JPG))
        for zla in ("meta.json", "czesci.json", "..%2Fmeta.json", "..%5Cmeta.json", "zrzut_9.jpg"):
            self.assertEqual(self.get("/api/podglad/%s/plik/%s" % (MID, zla))[0], 404, zla)
        for zle_id in ("nie-ma", "..", "..%2F..%2Fpanel"):
            self.assertEqual(self.get("/api/podglad/%s/czesci" % zle_id)[0], 404, zle_id)
        self.assertBlad(self.post("/api/podglad/migawka", {"tytul": "x"}, zdalny=True), 403)
        self.assertBlad(self.post("/api/podglad/migawka", {"tytul": "x"}), 503)                 # Studio niedostępne
        self.assertBlad(self.post("/api/podglad/migawka", [1]), 400)

    # ------------------------------------------------------------------ assety (rejestr grafik — tylko odczyt)
    def test_assety(self):
        """Prawdziwy assets/manifest.json jest tylko czytany — sprawdzamy kształt odpowiedzi, nie treść rejestru."""
        s, o, _ = self.get("/api/assety")
        self.assertEqual(s, 200, o)
        self.assertPola(o, ["zrodlo", "assety", "liczniki", "etapy", "statusy", "czeka"])
        self.assertEqual(o["zrodlo"], "assets/manifest.json")
        self.assertEqual([e["id"] for e in o["etapy"]], ["generowanie", "obrobka", "figma", "zgoda", "roblox"])
        self.assertEqual(sum(o["liczniki"].values()), len(o["assety"]))
        for a in o["assety"]:
            self.assertPola(a, ["nazwa", "kategoria", "status", "status_opis", "etap", "uzycie", "notatki", "obraz",
                                "historia", "czeka_na_zgode", "cel_komentarzy"])
        s, gosc, _ = self.get("/api/assety", zdalny=True)                           # gość widzi ten sam rejestr
        self.assertEqual((s, [a["nazwa"] for a in gosc["assety"]]), (200, [a["nazwa"] for a in o["assety"]]))
        z_obrazem = next((a for a in o["assety"] if a["obraz"]), None)
        if z_obrazem:                                                                # adresy z rejestru prowadzą do obrazów
            s, _, (nagl, b) = self.get(z_obrazem["obraz"], bajty=True, zdalny=True)
            self.assertEqual((s, len(b)), (200, z_obrazem["rozmiar"]))
            self.assertTrue(nagl["Content-Type"].startswith("image/"), nagl["Content-Type"])
            self.assertIn("max-age", nagl["Cache-Control"])
            s, _, (nagl, b) = self.get(z_obrazem["miniatura"], bajty=True)
            self.assertEqual(s, 200)
            self.assertTrue(nagl["Content-Type"].startswith("image/") and b, nagl["Content-Type"])
        for zla in ("..", "%2e%2e", "..%2Fmanifest.json", "..%2F..%2F.env", "..%5C..%5C.env", "manifest.json",
                    "nie-ma-takiego-assetu.png"):
            for rodzaj in ("plik", "miniatura"):
                self.assertEqual(self.get("/api/assety/%s/%s" % (rodzaj, zla))[0], 404, zla)
        for trasa in ("/api/assety", "/api/assety/plik/x", "/api/assety/miniatura/x"):
            self.assertBlad(self.post(trasa, {}), 405)                               # zakładka niczego nie zapisuje
        # komentarz do assetu = cel typu „plik” (ścieżka obrazu w repo); trafia do katalogu tymczasowego testu
        cel = "assets/processed/TestowyAsset.png"
        s, k, _ = self.post("/api/komentarze", {"cel": {"typ": "plik", "cel": cel, "etykieta": "TestowyAsset"},
                                                "tekst": "Za ciemny obrys"}, kto="Paweł")
        self.assertEqual((s, k["cel"]["typ"]), (201, "plik"), k)
        s, w, _ = self.get("/api/komentarze?typ=plik&cel=" + urllib.parse.quote(cel))
        self.assertEqual([x["id"] for x in w["komentarze"]], [k["id"]])
        s, z, _ = self.get("/api/zdrowie", timeout=60)
        self.assertTrue(z["moduly"]["assety"]["ok"], z["moduly"]["assety"])
        self.assertPola(z["szczegoly"]["assety"], ["manifest", "assety", "bez_obrazu"])
        self.assertEqual(z["szczegoly"]["assety"]["assety"], len(o["assety"]))

    # ------------------------------------------------------------------ raporty i komentarze
    def test_raporty_i_komentarze(self):
        s, r, _ = self.post("/api/raporty", {
            "tytul": "Karczma: nowe drzwi ąę", "opis_md": "**Zrobione**", "migawka": MID,
            "komponenty": [{"typ": "studio", "cel": "Workspace/Baza/Karczma", "etykieta": "Karczma"},
                           {"typ": "notatka", "cel": "B&C/00 Start.md"}]}, kto="Claude (Test)")
        self.assertEqual(s, 201, r)
        self.assertPola(r, ["id", "tytul", "opis_md", "kto", "czas", "rodzaj", "status", "komponenty", "zrzuty",
                            "komentarzy", "migawka"])
        self.assertEqual((r["status"], r["rodzaj"], r["kto"], r["komentarzy"]), ("czeka", "wdrozenie", "Claude (Test)", 0))
        self.assertEqual(r["komponenty"][1]["etykieta"], "00 Start.md")
        rid = r["id"]
        s, info, _ = self.post("/api/raporty", {"tytul": "Informacja", "rodzaj": "informacja"})
        self.assertEqual((s, info["status"]), (201, "informacja"))
        s, pyt, _ = self.post("/api/raporty", {"tytul": "Kolor dachu?", "rodzaj": "pytanie", "pytanie": "Czerwony?"})
        self.assertEqual((s, pyt["status"], pyt["pytanie"]), (201, "czeka", "Czerwony?"))

        for zle in ({}, {"tytul": "x", "nieznane": 1}, {"tytul": "x", "rodzaj": "zly"}, {"tytul": 5},
                    {"tytul": "x" * 141}, {"tytul": "x", "komponenty": [{"typ": "zly", "cel": "a"}]},
                    {"tytul": "x", "migawka": "../x"}, {"tytul": "x", "migawka": "20991231-000000-brak"},
                    {"tytul": "x", "zrzuty": ["a.png"]}):
            self.assertBlad(self.post("/api/raporty", zle), 400)
        self.assertBlad(self.post("/api/raporty", surowe=b"to nie json"), 400)

        s, o, _ = self.get("/api/raporty/%s" % rid)
        self.assertEqual((s, o["id"], o["komentarze"]), (200, rid, []))
        self.assertBlad(self.get("/api/raporty/r-20990101-000000-0000"), 404)

        s, k, _ = self.post("/api/komentarze", {"cel": {"typ": "raport", "cel": rid}, "tekst": "Wygląda dobrze"}, kto="Paweł")
        self.assertEqual(s, 201, k)
        self.assertPola(k, ["id", "cel", "kto", "czas", "tekst", "zrodlo"])
        self.assertEqual((k["kto"], k["zrodlo"]), ("Paweł", "tekst"))
        s, k2, _ = self.post("/api/komentarze", {"cel": {"typ": "studio", "cel": "Workspace/Baza/Karczma",
                                                         "etykieta": "Karczma"}, "tekst": "Drzwi za małe", "zrodlo": "glos"})
        self.assertEqual((s, k2["zrodlo"], k2["cel"]["etykieta"]), (201, "glos", "Karczma"))
        self.assertEqual(self.post("/api/komentarze", {"cel": {"typ": "migawka", "cel": MID}, "tekst": "ok"})[0], 201)
        self.assertBlad(self.post("/api/komentarze", {"tekst": "x"}), 400)
        self.assertBlad(self.post("/api/komentarze", {"cel": {"typ": "zly", "cel": "a"}, "tekst": "x"}), 400)
        self.assertBlad(self.post("/api/komentarze", {"cel": {"typ": "raport", "cel": rid}, "tekst": ""}), 400)
        self.assertBlad(self.post("/api/komentarze", {"cel": {"typ": "raport", "cel": "r-20990101-000000-0000"},
                                                      "tekst": "x"}), 404)
        s, o, _ = self.get("/api/komentarze?typ=raport&cel=" + urllib.parse.quote(rid))
        self.assertEqual([x["id"] for x in o["komentarze"]], [k["id"]])
        self.assertGreaterEqual(len(self.get("/api/komentarze")[1]["komentarze"]), 3)
        self.assertBlad(self.get("/api/komentarze?typ=zly"), 400)

        czeka = self.get("/api/raporty")[1]["czeka"]
        s, o, _ = self.post("/api/raporty/%s/decyzja" % rid, {"wartosc": "do_poprawy", "komentarz": "Większe drzwi"},
                            kto="Paweł")
        self.assertEqual((s, o["status"]), (200, "do_poprawy"), o)
        self.assertPola(o["decyzja"], ["kto", "czas", "wartosc", "komentarz"])
        self.assertEqual(o["decyzja"]["kto"], "Paweł")
        s, o, _ = self.post("/api/raporty/%s/decyzja" % rid, {"wartosc": "zaakceptowane"})
        self.assertEqual((s, o["status"], o["komentarzy"]), (200, "zaakceptowane", 1))
        self.assertBlad(self.post("/api/raporty/%s/decyzja" % rid, {"wartosc": "tak"}), 400)
        self.assertBlad(self.post("/api/raporty/%s/decyzja" % rid, {}), 400)
        self.assertBlad(self.post("/api/raporty/r-20990101-000000-0000/decyzja", {"wartosc": "zaakceptowane"}), 404)

        s, o, _ = self.get("/api/raporty")
        self.assertPola(o, ["raporty", "czeka"])
        self.assertEqual(o["czeka"], czeka - 1)
        ids = [x["id"] for x in o["raporty"]]
        self.assertLess(ids.index(pyt["id"]), ids.index(info["id"]))     # najnowszy pierwszy (także w tej samej sekundzie)
        self.assertLess(ids.index(info["id"]), ids.index(rid))
        for zla in ("zrzut_1.jpg", "..%2F..%2Fkomentarze", "..%5C" + rid + ".json"):
            self.assertEqual(self.get("/api/raporty/%s/plik/%s" % (rid, zla))[0], 404, zla)

    # ------------------------------------------------------------------ agent (bez przebiegu)
    def test_agent_watki(self):
        s, o, _ = self.get("/api/agent/stan", timeout=60)
        self.assertEqual(s, 200)
        self.assertPola(o, ["dostepny", "zdalnie", "tryby", "tryb_domyslny", "model"])
        self.assertEqual([t["id"] for t in o["tryby"]], ["plan", "praca", "auto"])
        s, o, _ = self.get("/api/agent/stan", zdalny=True, timeout=60)
        self.assertEqual((s, o["dostepny"]), (200, False))
        self.assertNotIn("sciezka", o)
        self.assertNotIn("auto", [t["id"] for t in o["tryby"]])

        s, w, _ = self.post("/api/agent/watki", {"tytul": "Test"})
        self.assertEqual(s, 201, w)
        self.assertPola(w, ["id", "tytul", "trwa", "wiadomosci"])
        wid = w["id"]
        s, o, _ = self.get("/api/agent/watki")
        wpis = next(x for x in o["watki"] if x["id"] == wid)
        self.assertPola(wpis, ["id", "tytul", "utworzono", "ostatnio", "wiadomosci", "trwa"])
        s, o, _ = self.get("/api/agent/watki/%s" % wid)
        self.assertEqual((s, o["wiadomosci"], o["trwa"]), (200, [], False))
        self.assertBlad(self.get("/api/agent/watki/w-20990101-000000-0000"), 404)
        for zle in ({"tekst": ""}, {"tekst": "x", "tryb": "zly"}, {"tekst": "x", "model": "a b;c"},
                    {"tekst": "x", "nieznane": 1}, {"tekst": "x", "kontekst": "zly"}):
            self.assertBlad(self.post("/api/agent/watki/%s/wiadomosc" % wid, zle), 400)
        self.assertBlad(self.post("/api/agent/watki/w-20990101-000000-0000/wiadomosc", {"tekst": "x"}), 404)
        s, _, (nagl, b) = self.get("/api/agent/watki/%s/strumien?od=7" % wid, bajty=True, timeout=10)
        self.assertTrue(nagl["Content-Type"].startswith("text/event-stream"))
        zdarzenie = json.loads(b.decode("utf-8").strip()[len("data: "):])
        self.assertEqual((zdarzenie["typ"], zdarzenie["n"]), ("koniec", 7))         # koniec zawsze z n >= od
        self.assertEqual(self.get("/api/agent/watki/w-20990101-000000-0000/strumien")[0], 404)
        s, o, _ = self.post("/api/agent/watki/%s/stop" % wid, {})
        self.assertEqual((s, o["ok"]), (200, True))
        self.assertBlad(self.post("/api/agent/watki/w-20990101-000000-0000/stop", {}), 404)
        for metoda, trasa, cialo in (("GET", "/api/agent/watki", None), ("POST", "/api/agent/watki", {}),
                                     ("GET", "/api/agent/watki/%s" % wid, None),
                                     ("POST", "/api/agent/watki/%s/wiadomosc" % wid, {"tekst": "x"}),
                                     ("GET", "/api/agent/watki/%s/strumien" % wid, None),
                                     ("POST", "/api/agent/watki/%s/stop" % wid, {})):
            s, o, _ = self.zadanie(metoda, trasa, cialo, zdalny=True, timeout=10)
            self.assertEqual((s, o.get("kod")), (403, "agent_zdalnie_wylaczony"), trasa)

    def test_przelacznik_agenta_z_telefonu(self):
        """Agenta z telefonu włącza tylko osoba przy komputerze; gość nie może sam sobie nadać dostępu."""
        self.assertBlad(self.post("/api/konfiguracja/lokalna", {"agent_zdalnie": True}, zdalny=True), 403)
        self.assertBlad(self.post("/api/konfiguracja/lokalna", {"agent_zdalnie": "tak"}), 400)
        self.assertBlad(self.post("/api/konfiguracja/lokalna", {}), 400)
        self.assertFalse(self.get("/api/konfiguracja")[1]["agent"]["zdalnie"])
        try:
            s, o, _ = self.post("/api/konfiguracja/lokalna", {"agent_zdalnie": True})
            self.assertEqual((s, o), (200, {"agent": {"zdalnie": True}}))
            self.assertTrue(self.get("/api/konfiguracja")[1]["agent"]["zdalnie"])
            s, o, _ = self.get("/api/agent/stan", zdalny=True)
            self.assertEqual((s, o["zdalnie"]), (200, True))
            self.assertNotIn("auto", [t["id"] for t in o["tryby"]])                  # z telefonu najwyżej tryb Praca
        finally:
            s, o, _ = self.post("/api/konfiguracja/lokalna", {"agent_zdalnie": False})
        self.assertEqual((s, o), (200, {"agent": {"zdalnie": False}}))
        self.assertFalse(self.get("/api/konfiguracja")[1]["agent"]["zdalnie"])

    # ------------------------------------------------------------------ głosówki (bez robotnika)
    def test_glos(self):
        s, o, _ = self.get("/api/glos/stan", timeout=60)
        self.assertEqual(s, 200)
        self.assertPola(o, ["whisper", "model"])
        # atrapa żywego robotnika (pid serwera) — POST nie uruchomi transkrypcji ani nie załaduje modelu
        kat = os.path.join(self.tmp, "runtime", "nagrania")
        os.makedirs(kat, exist_ok=True)
        with open(os.path.join(kat, "robotnik.pid"), "w", encoding="utf-8") as f:
            json.dump({"pid": self.proc.pid, "start": "atrapa"}, f)
        n = 8000
        wav = (b"RIFF" + struct.pack("<I", 36 + 2 * n) + b"WAVEfmt " + struct.pack("<IHHIIHH", 16, 1, 1, 16000, 32000, 2, 16)
               + b"data" + struct.pack("<I", 2 * n) + b"\x00\x00" * n)
        s, o, _ = self.post("/api/glos", surowe=wav, ct="audio/wav")
        self.assertEqual(s, 201, o)
        self.assertIn(o["stan"], ("czeka", "brak_whispera"))
        self.assertEqual(set(o), {"id", "stan"})
        s, o2, _ = self.get("/api/glos/%s" % o["id"])
        self.assertEqual((s, o2["id"], o2["stan"]), (200, o["id"], o["stan"]))
        self.assertBlad(self.post("/api/glos", surowe=b"\x00" * 100, ct="audio/wav"), 400)
        self.assertBlad(self.post("/api/glos", surowe=b"\x00" * 4000, ct="audio/webm"), 415)
        self.assertBlad(self.post("/api/glos", surowe=b'{"a": 1}', ct="application/json"), 415)
        self.assertBlad(self.get("/api/glos/g-20990101-000000-0000"), 404)


class TestZapisSejfuAPI(SerwerTestowy):
    """Trasy zapisu do sejfu na tymczasowym sejfie (konfiguracja lokalna serwera testowego wskazuje kopię plików)."""
    klucz_gd = "klucz-game-directora-testowy-0123456789"

    @classmethod
    def konfiguracja_lokalna(cls):
        cls.sejf = os.path.join(cls.tmp, "sejf")
        return {"gra": {"universeId": None}, "sejfy": [{"id": "B&C", "nazwa": "Sejf testowy", "sciezka": cls.sejf}]}

    @classmethod
    def przygotuj(cls, runtime):
        from testy.test_zapis import PLIKI
        os.makedirs(os.path.join(cls.sejf, "Produkcja"))
        for nazwa, tekst in PLIKI.values():
            with open(os.path.join(cls.sejf, "Produkcja", nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)
        with open(os.path.join(runtime, "klucz_gd.txt"), "w", encoding="utf-8") as f:
            f.write(cls.klucz_gd + "\n")

    def plik(self, nazwa):
        with open(os.path.join(self.sejf, "Produkcja", nazwa), encoding="utf-8", newline="") as f:
            return f.read()

    def plan(self, **kw):
        s, o, _ = self.get("/api/sejf/plan", **kw)
        self.assertEqual(s, 200, o)
        return o

    def test_plan_ma_wersje_i_identyfikatory(self):
        o = self.plan()
        self.assertEqual(set(o["wersje"]), {"roadmapa", "zadania", "decyzje", "pytania", "dziennik"})
        self.assertIsNone(o["wersje"]["roadmapa"])                                   # brak pliku = brak wersji
        self.assertRegex(o["wersje"]["zadania"], r"^[0-9a-f]{16}$")
        self.assertTrue(o["pliki"]["zadania"].endswith("Produkcja/Zadania.md"))
        for s in o["zadania"]["sekcje"]:
            for p in s["pozycje"]:
                self.assertRegex(p["id"], r"^z[0-9a-f]{10}$")

    def test_klucz_zatwierdzania(self):
        """Klucz zatwierdzania (dawny klucz Game Directora: plik klucz_gd.txt, ciasteczko bc_gd, parametr gd)."""
        self.assertFalse(self.get("/api/ja")[1]["game_director"])
        self.assertTrue(self.get("/api/ja", gd=self.klucz_gd)[1]["game_director"])
        o = self.get("/api/ja", gd=self.klucz_gd, zdalny=True)[1]                         # także przez tunel
        self.assertEqual((o["game_director"], o["decydent"], o["lokalny"]), (True, True, False))
        o = self.get("/api/ja", zdalny=True)[1]
        self.assertEqual((o["game_director"], o["decydent"]), (False, False))           # gość: nie decyduje
        self.assertFalse(self.get("/api/ja", naglowki={"Cookie": "bc_gd=zly"})[1]["game_director"])
        self.assertTrue(self.get("/api/ja", naglowki={"Cookie": "bc_gd=" + self.klucz_gd})[1]["game_director"])
        # klucz zatwierdzania nie zastępuje dostępu do panelu: bez kodu dostępu i bez klucza lokalnego nadal 401
        self.assertBlad(self.get("/api/ja", klucz=False, gd=self.klucz_gd), 401)
        # zły klucz: 200 bez uprawnień (próba liczy się do limitu)
        s, o, _ = self.get("/api/ja", gd="zly-klucz-0123456789-0123456789")
        self.assertEqual((s, o["game_director"], o["decydent"]), (200, False, True))   # decydent tylko z lokalnego
        # link z kluczem: ciasteczko HttpOnly i przekierowanie na adres bez klucza (lokalnie i z kodem dostępu)
        import http.client
        for zapytanie, naglowki in (("/?gd=" + self.klucz_gd, {"X-BC-Lokalny": self.klucz}),
                                    ("/?k=%s&gd=%s" % (self.token, self.klucz_gd), {"X-Forwarded-For": "192.168.1.50"})):
            c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
            try:
                c.request("GET", zapytanie, headers=naglowki)
                r = c.getresponse()
                r.read()
                self.assertEqual((r.status, r.getheader("Location")), (302, "/"))
                ciastka = r.msg.get_all("Set-Cookie") or []
                gd = [x for x in ciastka if x.startswith("bc_gd=")]
                self.assertEqual(len(gd), 1, ciastka)
                self.assertTrue(gd[0].startswith("bc_gd=" + self.klucz_gd + ";"))
                self.assertIn("HttpOnly", gd[0])
                if "k=" in zapytanie:
                    self.assertTrue(any(x.startswith("bc_t=") for x in ciastka), ciastka)
            finally:
                c.close()

    def test_przekierowanie_tylko_w_panelu(self):
        """Po zamianie klucza z adresu na ciasteczko przekierowanie nigdy nie wyprowadza na obcą stronę."""
        import http.client
        przypadki = [("/%5Cevil.example/?gd=" + self.klucz_gd, {"X-BC-Lokalny": self.klucz}, "/"),
                     ("/%5C%5Cevil.example?k=" + self.token, {"X-Forwarded-For": "192.168.1.50"}, "/"),
                     ("/%2F%2Fevil.example?l=" + self.klucz, {}, "/"),
                     ("/\\evil.example?l=" + self.klucz, {}, "/"),
                     ("//evil.example/?l=" + self.klucz, {}, None),    # nowszy Python sam skraca „//” do „/”
                     ("/podglad?k=" + self.token, {"X-Forwarded-For": "192.168.1.50"}, "/podglad")]
        for zapytanie, naglowki, dokad in przypadki:
            c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
            try:
                c.request("GET", zapytanie, headers=naglowki)
                r = c.getresponse()
                r.read()
                gdzie = r.getheader("Location") or ""
                self.assertEqual(r.status, 302, zapytanie)
                self.assertRegex(gdzie, r"^/(?![/\\])[^\\]*$", zapytanie)               # zawsze ścieżka tego panelu
                self.assertNotRegex(urllib.parse.unquote(gdzie), r"^/[/\\]|\\", zapytanie)
                if dokad is not None:
                    self.assertEqual(gdzie, dokad, zapytanie)
            finally:
                c.close()

    def test_odpowiedz_z_kluczem_zatwierdzania_ma_znacznik(self):
        o = self.plan(zdalny=True, gd=self.klucz_gd)
        s, w, _ = self.post("/api/sejf/pytania/4/odpowiedz", {"tekst": "Zatwierdzam", "wersja": o["wersje"]["pytania"]},
                            zdalny=True, gd=self.klucz_gd, kto="Paweł")
        self.assertEqual(s, 200, w)
        self.assertIn("\n- Paweł (klucz zatwierdzania, ", self.plik("Pytania otwarte.md"))
        self.assertIn("\n- Paweł (klucz zatwierdzania): odpowiedź na pytanie 4", self.plik("Dziennik zmian.md"))
        for kto in ("Game Director", "Klucz Zatwierdzania", "gość panelu"):              # imiona = znaczniki serwera
            s, e, _ = self.post("/api/sejf/pytania/4/odpowiedz", {"tekst": "x", "wersja": w["wersja"]}, zdalny=True,
                                kto=kto)
            self.assertEqual((s, e.get("kod")), (400, "imie_zastrzezone"), (kto, e))

    def test_odpowiedz_jako_gosc(self):
        o = self.plan(zdalny=True)
        s, w, _ = self.post("/api/sejf/pytania/2/odpowiedz", {"tekst": "Z telefonu", "wersja": o["wersje"]["pytania"]},
                            zdalny=True, kto="Paweł")
        self.assertEqual(s, 200, w)
        self.assertPola(w, ["ok", "opis", "plik", "wersja", "plan"])
        self.assertIn("- Paweł (", self.plik("Pytania otwarte.md"))
        self.assertIn("): Z telefonu\n", self.plik("Pytania otwarte.md"))
        self.assertIn("· Panel (ludzie)\n", self.plik("Dziennik zmian.md"))
        self.assertIn("\n- Paweł (gość panelu): odpowiedź na pytanie 2 ([[Pytania otwarte]])\n", self.plik("Dziennik zmian.md"))
        self.assertIn("- Paweł (gość panelu, ", self.plik("Pytania otwarte.md"))     # imię gościa niczego nie dowodzi
        self.assertEqual(w["plan"]["wersje"]["pytania"], self.plan()["wersje"]["pytania"])
        # stara wersja = konflikt, z kodem do rozpoznania w interfejsie
        s, e, _ = self.post("/api/sejf/pytania/2/odpowiedz", {"tekst": "x", "wersja": o["wersje"]["pytania"]})
        self.assertEqual((s, e.get("kod")), (409, "konflikt_wersji"), e)
        self.assertBlad(self.post("/api/sejf/pytania/2/odpowiedz", {"tekst": "# wstrzyknięcie", "wersja": w["wersja"]}), 400)
        self.assertBlad(self.post("/api/sejf/pytania/abc/odpowiedz", {"tekst": "x", "wersja": w["wersja"]}), 400)
        self.assertBlad(self.post("/api/sejf/pytania/77/odpowiedz", {"tekst": "x", "wersja": w["wersja"]}), 404)
        self.assertBlad(self.post("/api/sejf/pytania/2/odpowiedz", {"tekst": "x", "wersja": w["wersja"]}, xbc=False), 403)
        self.assertBlad(self.post("/api/sejf/pytania/2/odpowiedz", {"tekst": "x", "wersja": w["wersja"]}, klucz=False), 401)

    def test_zadania_jako_gosc(self):
        o = self.plan(zdalny=True)
        poz = next(p for s in o["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Coś na później")
        s, w, _ = self.post("/api/sejf/zadania/odhacz", {"id": poz["id"], "wersja": o["wersje"]["zadania"]}, zdalny=True)
        self.assertEqual(s, 200, w)
        self.assertNotIn("- [ ] Coś na później", self.plik("Zadania.md"))
        self.assertIn("## ✅ Zrobione\n- [x] ", self.plik("Zadania.md"))
        s, w, _ = self.post("/api/sejf/zadania/dodaj", {"tekst": "Z panelu", "sekcja": "teraz", "priorytet": "niski",
                                                         "wersja": w["wersja"]}, zdalny=True)
        self.assertEqual(s, 200, w)
        self.assertIn("- [ ] Z panelu · #niski\n", self.plik("Zadania.md"))
        self.assertBlad(self.post("/api/sejf/zadania/dodaj", {"tekst": "x", "sekcja": "teraz", "priorytet": "x",
                                                               "wersja": w["wersja"]}), 400)
        self.assertBlad(self.post("/api/sejf/zadania/odhacz", {"id": "z0000000000", "wersja": w["wersja"]}), 404)
        self.assertBlad(self.post("/api/sejf/zadania/odhacz", {"wersja": w["wersja"], "nieznane": 1}), 400)
        self.assertBlad(self.get("/api/sejf/zadania/odhacz"), 405)

    def test_decyzje_karol_albo_pawel(self):
        """Status decyzji: klucz zatwierdzania albo osoba przy komputerze; gość 403; bez imienia 400; podpis imię i data."""
        o = self.plan()
        przed = self.plik("Rejestr decyzji.md")
        cialo = {"status": "zatwierdzona", "uzasadnienie": "Tak", "wersja": o["wersje"]["decyzje"]}
        for kw in ({"zdalny": True}, {"zdalny": True, "kto": "Paweł"}, {"zdalny": True, "kto": "Game Director"},
                   {"zdalny": True, "gd": "zly-klucz-0123456789-0123456789", "kto": "Paweł"}):
            s, e, _ = self.post("/api/sejf/decyzje/D-002/status", cialo, **kw)
            self.assertEqual((s, e.get("kod")), (403, "brak_klucza_zatwierdzania"), (kw, e))
            self.assertIn("--klucz-zatwierdzania", e["blad"])
        # decydent bez prawdziwego imienia: 400 brak_imienia (lokalnie i z kluczem przez tunel). Także przy komputerze
        # BEZ nagłówka X-BC-Kto — serwer nie podpisuje decyzji domyślnym imieniem z `git config user.name`.
        for kw in ({"kto": "gość"}, {"zdalny": True, "gd": self.klucz_gd, "kto": "Gość"}, {}, {"gd": self.klucz_gd}):
            s, e, _ = self.post("/api/sejf/decyzje/D-002/status", cialo, **kw)
            self.assertEqual((s, e.get("kod")), (400, "brak_imienia"), (kw, e))
            self.assertIn("Ustawieniach", e["blad"])
        self.assertEqual(self.plik("Rejestr decyzji.md"), przed)
        # osoba przy komputerze z panelem, BEZ klucza zatwierdzania
        s, w, _ = self.post("/api/sejf/decyzje/D-002/status", cialo, kto="Karol")
        self.assertEqual(s, 200, w)
        rejestr = self.plik("Rejestr decyzji.md")
        self.assertIn("✅ zatwierdzona · game design · 2026-11-13 · źródło: [[Notatka]] · zdecydował: Karol ", rejestr)
        self.assertIn("\nUzasadnienie — Karol, ", rejestr)
        self.assertNotIn("Game Director", rejestr)
        self.assertIn("\n- Karol: decyzja D-002 zatwierdzona ([[Rejestr decyzji]])\n", self.plik("Dziennik zmian.md"))
        # klucz zatwierdzania przez tunel
        s, w, _ = self.post("/api/sejf/decyzje/D-003/status", {"status": "odrzucona", "wersja": w["wersja"]},
                            gd=self.klucz_gd, zdalny=True, kto="Paweł")
        self.assertEqual(s, 200, w)
        self.assertIn("· zaproponował: Claude Code · zdecydował: Paweł ", self.plik("Rejestr decyzji.md"))
        self.assertIn("\n- Paweł (klucz zatwierdzania): decyzja D-003 odrzucona ([[Rejestr decyzji]])\n",
                      self.plik("Dziennik zmian.md"))
        s, e, _ = self.post("/api/sejf/decyzje/D-001/status", {"status": "odrzucona", "wersja": w["wersja"]},
                            gd=self.klucz_gd, kto="Paweł")
        self.assertEqual((s, e.get("kod")), (409, "status_zamkniety"), e)

    def test_z_polecenie_klucz_zatwierdzania(self):
        """`--klucz-zatwierdzania` (i dawne `--klucz-gd`) wypisuje link z istniejącym kluczem; `--nowy-klucz-zatwierdzania`
        (i dawne `--nowy-klucz-gd`) unieważnia stary bez restartu panelu. Plik klucza dalej nazywa się klucz_gd.txt.
        (Nazwa z „z_”, żeby test szedł ostatni — zmienia klucz.)"""
        env = dict(os.environ, BC_PANEL_RUNTIME=os.path.join(self.tmp, "runtime"), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONIOENCODING="utf-8")
        bez_okna = 0x08000000 if os.name == "nt" else 0

        def polecenie(nazwa):
            r = subprocess.run([sys.executable, "-B", os.path.join(PANEL, "serwer.py"), nazwa], env=env, cwd=REPO,
                               capture_output=True, timeout=60, creationflags=bez_okna)
            self.assertEqual(r.returncode, 0, (nazwa, r.stderr.decode("utf-8", "replace")))
            return r.stdout.decode("utf-8")

        def plik_klucza():
            with open(os.path.join(self.tmp, "runtime", "klucz_gd.txt"), encoding="utf-8") as f:
                return f.read().strip()

        for nazwa in ("--klucz-zatwierdzania", "--klucz-gd"):
            wyjscie = polecenie(nazwa)
            self.assertIn("/?gd=" + self.klucz_gd, wyjscie)
            self.assertIn("Klucz zatwierdzania", wyjscie)
            self.assertIn("--nowy-klucz-zatwierdzania", wyjscie)
            self.assertNotIn("Game Director", wyjscie)
        for nazwa in ("--nowy-klucz-zatwierdzania", "--nowy-klucz-gd"):
            stary = self.klucz_gd
            wyjscie = polecenie(nazwa)
            nowy = plik_klucza()
            self.assertNotEqual(nowy, stary)
            self.assertIn("/?gd=" + nowy, wyjscie)
            self.assertFalse(self.get("/api/ja", gd=stary)[1]["game_director"])
            self.assertTrue(self.get("/api/ja", gd=nowy)[1]["game_director"])
            type(self).klucz_gd = nowy


if __name__ == "__main__":
    unittest.main()
