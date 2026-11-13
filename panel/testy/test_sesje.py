# -*- coding: utf-8 -*-
"""Testy zakładki Sesja (bc/sesje.py): agenda sesji głównych, pokój rozmowy, sygnały WebRTC, odcinki nagrań
z transkrypcją (ATRAPA — bez modelu Whisper), uprawnienia i prywatność.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_sesje

- Testy jednostkowe działają w tym procesie na katalogach tymczasowych (sejf, dane lokalne z testy/__init__.py).
- TestSesjeAPI stawia prawdziwy serwer na losowym porcie (jak test_api.py) i sprawdza całą drogę odcinka: przeglądarka
  -> serwer -> robotnik bc.glos w osobnym procesie (BC_GLOS_ATRAPA=1, bez ładowania modelu) -> zapis rozmowy.
- Agent (claude) nigdy nie jest uruchamiany: bc.agent.uruchom_polecenie jest podmieniany, a w serwerze testowym
  notatki automatyczne są wyłączone (sesje.notatki_co_min = 0) i trasy agenta są sprawdzane tylko jako odmowy.
"""
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import agent, glos, rdzen, sejf, sesje, zapis  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402
from testy.test_zapis import DZIS, PLIKI  # noqa: E402
from testy import test_api  # noqa: E402  (bez importu klas: discover uruchomiłby je drugi raz)

AGENDA = """---
status: do-decyzji
tags: [produkcja, sesje]
---
# Sesje główne

Sesja główna to długa rozmowa głosowa. Format wiersza: `- [ ] Temat — kontekst · dodał: imię data`.

## Do omówienia
- [ ] Karczma: poziomy trudności zadań i Energia (D-009) — Karol 13.11: „zostawiamy na sesję długą” · dodał: Karol 2026-11-13
- [ ] Zakres pierwszego wydania — po odrzuceniu D-014 · propozycja agenta 2026-11-13

## Omówione
"""
WEBM = b"\x1a\x45\xdf\xa3" + b"\x42\x86\x81\x01" + b"\x00" * 3000        # wystarczy nagłówek EBML — atrapa nie dekoduje


class Z:
    """Udawane żądanie (bc.http.Zadanie) do wołania tras w tym procesie."""

    def __init__(self, dane=None, lokalny=False, gd=False, kto="Karol", naglowki=None, cialo=b"", query=None,
                 ip="127.0.0.1"):
        self.json = dane
        self.lokalny = lokalny
        self.game_director = gd
        self.kto = kto
        self.kto_z_naglowka = True
        self.naglowki = naglowki or {}
        self.cialo = cialo
        self.query = query or {}
        self.ip = ip
        self.params = {}

    def q(self, k, d=None):
        return self.query.get(k, d)


def lokalny(dane=None, **kw):
    return Z(dane, lokalny=True, **kw)


def gosc(dane=None, **kw):
    kw.setdefault("kto", "Paweł")
    kw.setdefault("ip", "192.168.1.50")
    return Z(dane, **kw)


class Baza(unittest.TestCase):
    konfiguracja_sesji = {"stun": ["stun:stun.example.org:3478"], "notatki_co_min": 0}

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_sesje_")
        self.sejf = os.path.join(self.tmp, "sejf")
        self.runtime = os.path.join(self.tmp, "runtime")
        os.makedirs(os.path.join(self.sejf, "Produkcja"))
        os.makedirs(self.runtime)
        for nazwa, tekst in PLIKI.values():
            with open(os.path.join(self.sejf, "Produkcja", nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)
        self.pisz_agende(AGENDA)
        self.cfg = {"zapis_sejfu": True, "sesje": dict(self.konfiguracja_sesji), "agent": {"zdalnie": False}}
        self.latki = [
            mock.patch.object(sejf, "_sejfy", lambda: [("B&C", "Sejf testowy", self.sejf)]),
            mock.patch.object(zapis, "dzis", lambda: DZIS),
            mock.patch.object(zapis, "_plik_stanu", lambda: os.path.join(self.tmp, "zapis_sejfu.json")),
            mock.patch.object(rdzen, "log", lambda *a: None),
            mock.patch.object(rdzen, "konfiguracja", lambda: self.cfg),
            mock.patch.object(rdzen, "RUNTIME", self.runtime),
            mock.patch.object(glos, "uruchom_robotnika", lambda: False),     # robotnika woła test, nie trasa
        ]
        for l in self.latki:
            l.start()
        sejf.uniewaznij()
        zapis._limity.clear()
        zapis._posprzatane.clear()
        sesje._reset_do_testow()

    def tearDown(self):
        sesje._reset_do_testow()
        for w in list(sesje._watki_konca.values()):
            w.join(10)
        for l in reversed(self.latki):
            l.stop()
        sejf.uniewaznij()
        zapis._limity.clear()
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- pliki
    def sciezka(self, nazwa):
        return os.path.join(self.sejf, "Produkcja", nazwa)

    def pisz_agende(self, tekst):
        with open(self.sciezka("Sesje główne.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)

    def agenda(self):
        with open(self.sciezka("Sesje główne.md"), encoding="utf-8", newline="") as f:
            return f.read()

    def dziennik(self):
        with open(self.sciezka("Dziennik zmian.md"), encoding="utf-8", newline="") as f:
            return f.read()

    def assertBlad(self, status, fn, *a, **kw):
        with self.assertRaises(BladHTTP) as k:
            fn(*a, **kw)
        self.assertEqual(k.exception.status, status, k.exception.komunikat)
        self.assertTrue(k.exception.komunikat)
        return k.exception

    # --- pokój
    def dolacz(self, z):
        s, o = sesje._t_dolacz(z)
        self.assertEqual(s, 201)
        return o["u"], o["k"], o


# =========================================================================== agenda
class TestAgenda(Baza):
    def test_odczyt(self):
        a = sesje._t_agenda(gosc())
        self.assertTrue(a["istnieje"])
        self.assertTrue(a["plik"].endswith("Produkcja/Sesje główne.md"))
        self.assertRegex(a["wersja"], r"^[0-9a-f]{16}$")
        self.assertEqual(len(a["do_omowienia"]), 2)
        self.assertEqual(a["omowione"], [])
        t1, t2 = a["do_omowienia"]
        self.assertEqual(t1["temat"], "Karczma: poziomy trudności zadań i Energia (D-009)")
        self.assertEqual(t1["dodal"], "Karol")
        self.assertEqual(t1["data"], "2026-11-13")
        self.assertEqual(t1["zrodla"], ["D-009"])
        self.assertRegex(t1["id"], r"^t[0-9a-f]{10}$")
        self.assertTrue(t2["propozycja_agenta"])
        self.assertIsNone(t2["dodal"])

    def test_dodanie_jedna_linia_i_dziennik(self):
        przed = self.agenda()
        w = sesje._t_agenda_dodaj(lokalny({"temat": "Ile kosztuje pet", "kontekst": "ceny w Robuxach",
                                             "zrodlo": "pytanie 19", "wersja": sesje.czytaj_agende()["wersja"]}))
        self.assertTrue(w["ok"])
        wiersz = "- [ ] Ile kosztuje pet (pytanie 19) — ceny w Robuxach · dodał: Karol %s" % DZIS
        kotwica = "- [ ] Zakres pierwszego wydania — po odrzuceniu D-014 · propozycja agenta 2026-11-13\n"
        self.assertEqual(self.agenda(), przed.replace(kotwica, kotwica + wiersz + "\n"))
        self.assertIn("- Karol: temat na sesję główną: Ile kosztuje pet (pytanie 19) ([[Sesje główne]])", self.dziennik())
        self.assertEqual(len(w["agenda"]["do_omowienia"]), 3)
        self.assertNotIn("plan", w)

    def test_gosc_ma_znacznik_i_limit(self):
        sesje._t_agenda_dodaj(gosc({"temat": "Temat od gościa"}))
        self.assertIn("· dodał: Paweł (gość panelu) %s" % DZIS, self.agenda())
        self.assertIn("- Paweł (gość panelu): temat na sesję główną", self.dziennik())
        with mock.patch.object(zapis, "LIMIT_ZAPISOW_GOSCIA", 1):
            self.assertBlad(429, sesje._t_agenda_dodaj, gosc({"temat": "Drugi temat"}))
        sesje._t_agenda_dodaj(lokalny({"temat": "Osoba przy komputerze bez limitu"}))

    def test_na_sesje_glowna_kontrakt(self):
        w = sesje._t_na_sesje(gosc({"zrodlo": "D-024", "tytul": "Walka 3D: cutscenka",
                                    "dopisek": "Paweł: do rozmowy na głos"}))
        self.assertTrue(w["ok"])
        self.assertIn("- [ ] Walka 3D: cutscenka (D-024) — Paweł: do rozmowy na głos · dodał: Paweł (gość panelu) %s"
                      % DZIS, self.agenda())
        e = self.assertBlad(409, sesje._t_na_sesje, lokalny({"zrodlo": "D-024", "tytul": "Inny tytuł"}))
        self.assertEqual(e.dodatkowe.get("kod"), "juz_zapisane")
        e = self.assertBlad(409, sesje._t_na_sesje, lokalny({"zrodlo": "D-009", "tytul": "Karczma"}))
        self.assertEqual(e.dodatkowe.get("kod"), "juz_zapisane")
        self.assertBlad(400, sesje._t_na_sesje, lokalny({"tytul": "Bez źródła"}))
        self.assertBlad(400, sesje._t_na_sesje, lokalny({"zrodlo": "D-1", "tytul": "x", "inne": 1}))
        self.assertBlad(400, sesje._t_na_sesje, lokalny({"zrodlo": "D-1 (x)", "tytul": "Nawiasy w źródle"}))

    def test_omowione(self):
        a = sesje.czytaj_agende()
        t1 = a["do_omowienia"][0]
        w = sesje._t_agenda_omowione(lokalny({"id": t1["id"], "wynik": "trzy poziomy", "wersja": a["wersja"]}))
        tekst = self.agenda()
        self.assertNotIn("- [ ] Karczma", tekst)
        oczekiwany = "- [x] %s · omówione: %s, Karol — trzy poziomy" % (t1["tekst_md"], DZIS)
        self.assertTrue(tekst.endswith("## Omówione\n" + oczekiwany + "\n"), tekst)
        om = w["agenda"]["omowione"][0]
        self.assertEqual(om["omowione"], {"data": DZIS, "kto": "Karol", "wynik": "trzy poziomy"})
        self.assertEqual(om["dodal"], "Karol")
        self.assertIn("omówiony temat sesji: Karczma", self.dziennik())
        self.assertBlad(409, sesje._t_agenda_omowione, lokalny({"id": t1["id"], "wersja": a["wersja"]}))  # wersja
        self.assertBlad(404, sesje._t_agenda_omowione, lokalny({"id": t1["id"], "wersja": w["wersja"]}))
        self.assertBlad(400, sesje._t_agenda_omowione, lokalny({"id": "../x", "wersja": w["wersja"]}))
        self.assertBlad(400, sesje._t_agenda_omowione, lokalny({"id": t1["id"]}))

    def test_wstrzykniecia(self):
        for temat in ("# Nagłówek", "## Omówione", "- [ ] fałszywe pole", "[x] zrobione", "**Odpowiedź:** tak",
                      "a · [ ] b"):
            self.assertBlad(400, sesje._t_agenda_dodaj, lokalny({"temat": temat}))
        self.assertBlad(400, sesje._t_agenda_dodaj, lokalny({"temat": "x" * 201}))
        self.assertBlad(400, sesje._t_agenda_dodaj, lokalny({"temat": "   "}))
        self.assertBlad(400, sesje._t_agenda_dodaj, lokalny({"temat": 5}))
        # nowe linie i udawane pola podpisu nie rozbijają wiersza
        sesje._t_agenda_dodaj(lokalny({"temat": "Linia 1\n## Omówione\nLinia 3 · dodał: Paweł 2020-01-01"}))
        dodane = [l for l in self.agenda().split("\n") if l.startswith("- [ ] Linia 1")]
        self.assertEqual(len(dodane), 1, self.agenda())
        self.assertEqual([l for l in self.agenda().split("\n") if l.startswith("#")],
                         ["# Sesje główne", "## Do omówienia", "## Omówione"])
        r = sesje.rozbierz_temat(dodane[0][6:])
        self.assertEqual(r["dodal"], "Karol")
        self.assertNotIn(" · ", r["temat"])

    def test_kontrola_wersji_i_wylaczony_zapis(self):
        stara = sesje.czytaj_agende()["wersja"]
        with open(self.sciezka("Sesje główne.md"), "a", encoding="utf-8", newline="\n") as f:
            f.write("- [x] ktoś dopisał w Obsidianie\n")
        e = self.assertBlad(409, sesje._t_agenda_dodaj, lokalny({"temat": "Nowy", "wersja": stara}))
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_wersji")
        sesje._t_agenda_dodaj(lokalny({"temat": "Bez wersji — bierze bieżącą"}))
        self.cfg["zapis_sejfu"] = False
        self.assertBlad(403, sesje._t_agenda_dodaj, lokalny({"temat": "Wyłączone"}))
        self.assertBlad(403, sesje._t_na_sesje, lokalny({"zrodlo": "D-030", "tytul": "Wyłączone"}))

    def test_brak_pliku_i_dubel_tematu(self):
        os.remove(self.sciezka("Sesje główne.md"))
        self.assertFalse(sesje.czytaj_agende()["istnieje"])
        sesje._t_agenda_dodaj(lokalny({"temat": "Pierwszy temat"}))
        tekst = self.agenda()
        self.assertTrue(tekst.startswith("---\nstatus: propozycja\n"))
        self.assertIn("## Do omówienia\n- [ ] Pierwszy temat · dodał: Karol", tekst)
        e = self.assertBlad(409, sesje._t_agenda_dodaj, lokalny({"temat": "pierwszy TEMAT"}))
        self.assertEqual(e.dodatkowe.get("kod"), "juz_zapisane")

    def test_wyslij_widzi_agende(self):
        sesje._t_agenda_dodaj(lokalny({"temat": "Do wysłania"}))
        stan = rdzen.czytaj_json(os.path.join(self.tmp, "zapis_sejfu.json"))
        sciezki = [w["sciezka"] for w in stan["pliki"].values()]
        self.assertTrue(any(s.endswith("Sesje główne.md") for s in sciezki), sciezki)


# =========================================================================== pokój
class TestPokoj(Baza):
    def test_dolaczenie_stan_i_wyjscie(self):
        u, k, o = self.dolacz(lokalny())
        self.assertRegex(u, r"^[0-9a-f]{16}$")
        self.assertEqual(o["ja"]["id"], u)
        self.assertEqual(o["ice"], [{"urls": ["stun:stun.example.org:3478"]}])
        u2, k2, _ = self.dolacz(gosc())
        st = sesje._t_stan(gosc())
        self.assertEqual([x["kto"] for x in st["pokoj"]["uczestnicy"]], ["Karol", "Paweł"])
        self.assertEqual(st["pokoj"]["uczestnicy"][1]["rola"], "gość")
        self.assertNotIn("id", st["pokoj"]["uczestnicy"][0])            # adresy tylko dla uczestników
        self.assertNotIn("ice", st)
        p = sesje._t_puls(gosc({"u": u2, "k": k2, "wyciszony": True, "polaczenia": {u: "polaczony", "obcy": "x"}}))
        ja = [x for x in p["pokoj"]["uczestnicy"] if x["id"] == u2][0]
        self.assertEqual(ja["stan"], "wyciszony")
        self.assertEqual(ja["polaczenia"], {u: "polaczony"})
        self.assertEqual(sesje._t_opusc(gosc({"u": u2, "k": k2})), {"ok": True})
        self.assertEqual(len(sesje._t_stan(gosc())["pokoj"]["uczestnicy"]), 1)
        self.assertEqual(sesje._t_opusc(gosc({"u": u2, "k": k2})), {"ok": True})   # drugi raz — bez błędu

    def test_zly_klucz_i_brak_uczestnika(self):
        u, k, _ = self.dolacz(lokalny())
        self.assertBlad(403, sesje._t_puls, lokalny({"u": u, "k": "zly-klucz"}))
        self.assertBlad(410, sesje._t_puls, lokalny({"u": "0123456789abcdef", "k": "x"}))
        self.assertBlad(400, sesje._t_puls, lokalny({"u": "../../etc", "k": "x"}))
        self.assertBlad(400, sesje._t_puls, lokalny({}))

    def test_wygasniecie_pulsu(self):
        u, k, _ = self.dolacz(lokalny())
        u2, k2, _ = self.dolacz(gosc())
        sesje._t_sygnal(gosc({"u": u2, "k": k2, "do": u, "typ": "oferta", "dane": {"sdp": "x"}}))
        sesje._uczestnicy[u2]["ostatnio"] -= sesje.ZYCIE_UCZESTNIKA_S + 1
        st = sesje._t_puls(lokalny({"u": u, "k": k}))
        self.assertEqual([x["id"] for x in st["pokoj"]["uczestnicy"]], [u])
        self.assertEqual(sesje._t_odbierz(lokalny({"u": u, "k": k, "czekaj": 0}))["sygnaly"], [])  # sygnał zniknął
        self.assertBlad(410, sesje._t_puls, gosc({"u": u2, "k": k2}))
        self.assertEqual(sesje.obecni()["osoby"], [{"kto": "Karol", "stan": "polaczony",
                                                    "od": sesje._t_stan(lokalny())["pokoj"]["uczestnicy"][0]["od"]}])

    def test_limit_osob(self):
        self.cfg["sesje"]["max_osob"] = 3
        for i in range(3):
            self.dolacz(gosc(kto="Osoba %d" % i))
        e = self.assertBlad(409, sesje._t_dolacz, lokalny())
        self.assertEqual(e.dodatkowe.get("kod"), "pelny")
        self.cfg["sesje"]["max_osob"] = 99                                 # górna granica 12
        self.assertEqual(sesje.cfg()["max_osob"], 12)


# =========================================================================== sygnały
class TestSygnaly(Baza):
    def test_tylko_adresat_kolejnosc_potwierdzenie(self):
        a, ka, _ = self.dolacz(lokalny())
        b, kb, _ = self.dolacz(gosc())
        c, kc, _ = self.dolacz(gosc(kto="Ola"))
        for i in range(3):
            sesje._t_sygnal(lokalny({"u": a, "k": ka, "do": b, "typ": "ice", "dane": {"i": i}}))
        self.assertEqual(sesje._t_odbierz(gosc({"u": c, "k": kc, "czekaj": 0}))["sygnaly"], [])
        sy = sesje._t_odbierz(gosc({"u": b, "k": kb, "czekaj": 0}))["sygnaly"]
        self.assertEqual([s["dane"]["i"] for s in sy], [0, 1, 2])
        self.assertTrue(all(s["od"] == a and s["typ"] == "ice" for s in sy))
        self.assertEqual(sorted(s["n"] for s in sy), [s["n"] for s in sy])
        sy2 = sesje._t_odbierz(gosc({"u": b, "k": kb, "od": sy[1]["n"] + 1, "czekaj": 0}))["sygnaly"]
        self.assertEqual([s["dane"]["i"] for s in sy2], [2])

    def test_zle_sygnaly(self):
        a, ka, _ = self.dolacz(lokalny())
        b, kb, _ = self.dolacz(gosc())
        self.assertBlad(400, sesje._t_sygnal, lokalny({"u": a, "k": ka, "do": b, "typ": "skrypt", "dane": {}}))
        self.assertBlad(404, sesje._t_sygnal, lokalny({"u": a, "k": ka, "do": a, "typ": "ice", "dane": {}}))
        self.assertBlad(404, sesje._t_sygnal, lokalny({"u": a, "k": ka, "do": "0123456789abcdef", "typ": "ice"}))
        self.assertBlad(413, sesje._t_sygnal, lokalny({"u": a, "k": ka, "do": b, "typ": "oferta",
                                                      "dane": {"sdp": "x" * (sesje.MAX_SYGNAL_BAJTY + 1)}}))
        self.assertBlad(403, sesje._t_sygnal, lokalny({"u": a, "k": kb, "do": b, "typ": "ice", "dane": {}}))
        with mock.patch.object(sesje, "LIMIT_SYGNALOW", 5):
            for _ in range(5):
                sesje._t_sygnal(lokalny({"u": a, "k": ka, "do": b, "typ": "ice", "dane": {}}))
            e = self.assertBlad(429, sesje._t_sygnal, lokalny({"u": a, "k": ka, "do": b, "typ": "ice", "dane": {}}))
            self.assertEqual(e.dodatkowe.get("kod"), "limit_sygnalow")

    def test_dlugie_odpytywanie(self):
        a, ka, _ = self.dolacz(lokalny())
        b, kb, _ = self.dolacz(gosc())
        threading.Timer(0.3, lambda: sesje._t_sygnal(
            lokalny({"u": a, "k": ka, "do": b, "typ": "oferta", "dane": {"sdp": "v=0"}}))).start()
        t0 = time.time()
        sy = sesje._t_odbierz(gosc({"u": b, "k": kb, "czekaj": 5}))["sygnaly"]
        self.assertLess(time.time() - t0, 3)
        self.assertEqual(sy[0]["dane"], {"sdp": "v=0"})
        t0 = time.time()
        self.assertEqual(sesje._t_odbierz(gosc({"u": b, "k": kb, "od": sy[0]["n"] + 1, "czekaj": 0.5}))["sygnaly"], [])
        self.assertGreaterEqual(time.time() - t0, 0.4)


# =========================================================================== słuchanie, odcinki, transkrypcja
class TestOdcinki(Baza):
    def wyslij(self, u, k, dane=WEBM, ct="audio/webm;codecs=opus", nr=1, sesja=None):
        query = {"nr": str(nr), "t": str(int(time.time() * 1000))}
        if sesja:
            query["sesja"] = sesja
        return sesje._t_odcinek(Z(naglowki={"X-BC-Sesja": "%s:%s" % (u, k), "Content-Type": ct}, cialo=dane,
                                  query=query))

    def test_ostatni_odcinek_po_wylaczeniu_sluchania(self):
        """Przeglądarka dowiaduje się o wyłączeniu z pulsu i dopiero wtedy wysyła ostatni kawałek — serwer ma na
        niego okno łaski (odcinek_s + LASKA_S), tylko dla tej sesji i tylko od uczestnika pokoju."""
        u, k, _ = self.dolacz(gosc())
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        sid = sesje._biezaca()["id"]
        sesje._t_sluchanie(lokalny({"wlacz": False}))
        s, o = self.wyslij(u, k, sesja=sid)
        self.assertEqual((s, o["sesja"]), (201, sid))
        s, o = self.wyslij(u, k, nr=2)                                            # bez identyfikatora też
        self.assertEqual((s, o["sesja"]), (201, sid))
        e = self.assertBlad(409, self.wyslij, u, k, nr=3, sesja="20200101-000000-abcd")   # inna sesja
        self.assertEqual(e.dodatkowe.get("kod"), "nie_slucha")
        self.assertBlad(403, self.wyslij, u, "zly-klucz", nr=4, sesja=sid)        # tylko uczestnik
        sesje._zmien_sesje(sid, slucha_do_ts=time.time() - sesje._okno_laski() - 1)
        e = self.assertBlad(409, self.wyslij, u, k, nr=5, sesja=sid)               # po oknie łaski
        self.assertEqual(e.dodatkowe.get("kod"), "nie_slucha")

    def test_ostatni_odcinek_po_zakonczeniu_sesji(self):
        u, k, _ = self.dolacz(gosc())
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        sid = sesje._biezaca()["id"]
        sesje._t_zakoncz(lokalny({"spisz": False}))
        self.assertIsNone(sesje._biezaca())
        s, o = self.wyslij(u, k, sesja=sid)
        self.assertEqual((s, o["sesja"]), (201, sid))                            # trafia do zakończonej sesji
        self.assertEqual(sesje._czytaj_sesje(sid)["odcinki"], 1)
        # nowa sesja ze słuchaniem: odcinek z jej identyfikatorem idzie do niej, nie do starej
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        nowa = sesje._biezaca()["id"]
        self.assertNotEqual(nowa, sid)
        self.assertEqual(self.wyslij(u, k, nr=2, sesja=nowa)[1]["sesja"], nowa)
        self.assertEqual(self.wyslij(u, k, nr=3)[1]["sesja"], nowa)

    def transkrybuj_wszystko(self):
        with mock.patch.dict(os.environ, {"BC_GLOS_ATRAPA": "1"}):
            tr = glos._Transkryptor()
            for nid in glos._do_zrobienia():
                glos._przetworz(nid, tr)

    def test_sluchanie_tylko_decydent(self):
        e = self.assertBlad(403, sesje._t_sluchanie, gosc({"wlacz": True}))
        self.assertEqual(e.dodatkowe.get("kod"), "tylko_decydent")
        st = sesje._t_sluchanie(gosc({"wlacz": True}, gd=True))                 # klucz zatwierdzania przez tunel
        self.assertTrue(st["sluchanie"]["wlaczone"])
        self.assertEqual(st["sluchanie"]["kto"], "Paweł")
        st = sesje._t_sluchanie(lokalny({"wlacz": False}))
        self.assertFalse(st["sluchanie"]["wlaczone"])
        self.assertBlad(400, sesje._t_sluchanie, lokalny({"wlacz": "tak"}))

    def test_cala_droga_odcinka_z_atrapa(self):
        u, k, _ = self.dolacz(gosc())
        e = self.assertBlad(409, self.wyslij, u, k)                              # agent nie słucha
        self.assertEqual(e.dodatkowe.get("kod"), "nie_slucha")
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        s, o = self.wyslij(u, k)
        self.assertEqual(s, 201)
        sid = sesje._biezaca()["id"]
        kat = os.path.join(self.runtime, "sesje", sid, "odcinki", o["id"])
        self.assertTrue(os.path.isfile(os.path.join(kat, "nagranie.webm")))
        self.assertFalse(os.path.realpath(kat).startswith(os.path.realpath(rdzen.REPO) + os.sep))   # poza repo
        self.assertEqual(glos._do_zrobienia(), [o["id"]])
        zapytanie = Z()
        zapytanie.params = {"id": o["id"]}
        self.assertBlad(404, glos._odczytaj, zapytanie)                        # trasa głosówek go nie pokaże
        self.transkrybuj_wszystko()
        self.assertFalse(os.path.exists(os.path.join(kat, "nagranie.webm")))   # dźwięk usunięty po transkrypcji
        sesje.zbierz()
        self.assertFalse(os.path.exists(kat))
        t = sesje._t_transkrypcja(gosc({"u": u, "k": k}))
        self.assertEqual([(w["n"], w["kto"], w["tekst"]) for w in t["wpisy"]], [(1, "Paweł", glos.TEKST_ATRAPY)])
        self.assertEqual(sesje._t_transkrypcja(gosc({"u": u, "k": k, "od": 1}))["wpisy"], [])
        md = sesje.tekst_transkrypcji(sid)
        self.assertIn("Paweł: " + glos.TEKST_ATRAPY, md)
        with open(os.path.join(self.runtime, "sesje", sid, "transkrypcja.md"), encoding="utf-8") as f:
            self.assertIn(glos.TEKST_ATRAPY, f.read())

    def test_zostaw_dzwiek_z_konfiguracji_lokalnej(self):
        self.cfg["sesje"]["zostaw_dzwiek"] = True
        u, k, _ = self.dolacz(lokalny())
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        _, o = self.wyslij(u, k)
        self.transkrybuj_wszystko()
        sesje.zbierz()
        kat = os.path.join(self.runtime, "sesje", sesje._biezaca()["id"], "odcinki", o["id"])
        self.assertTrue(os.path.isfile(os.path.join(kat, "nagranie.webm")))
        sesje.zbierz()                                                           # drugi raz nie dubluje wpisu
        self.assertEqual(sesje._biezaca()["wpisy"], 1)

    def test_limity_i_formaty(self):
        u, k, _ = self.dolacz(lokalny())
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        self.assertBlad(403, self.wyslij, u, "zly")
        self.assertBlad(400, sesje._t_odcinek, Z(naglowki={"Content-Type": "audio/webm"}, cialo=WEBM))
        self.assertBlad(415, self.wyslij, u, k, ct="application/json")
        self.assertBlad(415, self.wyslij, u, k, dane=b"RIFF" + b"\x00" * 4 + b"WAVE" + b"\x00" * 3000)
        self.assertBlad(400, self.wyslij, u, k, dane=WEBM[:100])
        self.cfg["sesje"]["odcinek_max_kb"] = 64
        self.assertBlad(413, self.wyslij, u, k, dane=WEBM + b"\x00" * 70 * 1024)
        self.cfg["sesje"]["odcinek_max_kb"] = 2048
        self.cfg["sesje"]["sesja_max_mb"] = 10
        sesje._zmien_sesje(sesje._biezaca()["id"], bajty=10 * 1024 * 1024 - 100)
        e = self.assertBlad(507, self.wyslij, u, k)
        self.assertEqual(e.dodatkowe.get("kod"), "limit_sesji")
        sesje._zmien_sesje(sesje._biezaca()["id"], bajty=0)
        self.cfg["sesje"]["odcinki_na_minute"] = 2
        sesje._uczestnicy[u]["odcinki_t"].clear()
        self.wyslij(u, k)
        self.wyslij(u, k)
        e = self.assertBlad(429, self.wyslij, u, k)
        self.assertEqual(e.dodatkowe.get("kod"), "limit_odcinkow")


# =========================================================================== uprawnienia i agent
class TestUprawnieniaIAgent(Baza):
    def setUp(self):
        super().setUp()
        self.wywolania = []

        def udawany(tekst, kto, tytul=None, watek=None, tryb="praca", katalogi=None, zestaw=None):
            self.wywolania.append({"tekst": tekst, "kto": kto, "tytul": tytul, "watek": watek, "tryb": tryb,
                                   "katalogi": katalogi, "zestaw": zestaw})
            return {"watek": watek or "w-test-%d" % len(self.wywolania), "nr": 1, "od": 1, "tryb": tryb}
        self.latki_agenta = [mock.patch.object(agent, "uruchom_polecenie", udawany),
                             mock.patch.object(sesje, "CZEKANIE_NA_TRANSKRYPCJE_S", 1),
                             mock.patch.object(sesje, "ODSTEP_CZEKANIA_S", 0.05),
                             mock.patch.object(sesje, "_okno_laski", lambda: 0.3)]
        for l in self.latki_agenta:
            l.start()

    def tearDown(self):
        for w in list(sesje._watki_konca.values()):
            w.join(10)
        for l in reversed(self.latki_agenta):
            l.stop()
        super().tearDown()

    def czekaj_na_koniec(self, sid, limit=10):
        koniec = time.time() + limit
        while time.time() < koniec and sesje._czytaj_sesje(sid)["zakonczenie"]["stan"] == "czeka_na_transkrypcje":
            time.sleep(0.05)
        return sesje._czytaj_sesje(sid)["zakonczenie"]

    def z_zapisem(self):
        """Sesja ze słuchaniem i jednym wpisem w zapisie rozmowy."""
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        sid = sesje._biezaca()["id"]
        sesje._dopisz_wpisy(sid, [{"t": rdzen.teraz(), "kto": "Karol", "tekst": "Ustalamy trzy poziomy karczmy."}])
        return sid

    def test_gosc_nie_wlacza_agenta(self):
        self.z_zapisem()
        for fn in (sesje._t_notatki, sesje._t_zakoncz, sesje._t_zaproponuj):
            e = self.assertBlad(403, fn, gosc({}))
            self.assertEqual(e.dodatkowe.get("kod"), "tylko_decydent")
        # klucz zatwierdzania przez tunel: decydent, ale agent z telefonu wyłączony
        for fn in (sesje._t_notatki, sesje._t_zaproponuj):
            e = self.assertBlad(403, fn, gosc({}, gd=True))
            self.assertEqual(e.dodatkowe.get("kod"), "agent_zdalnie_wylaczony")
        e = self.assertBlad(403, sesje._t_zakoncz, gosc({}, gd=True))
        self.assertEqual(self.wywolania, [])
        st = sesje._t_stan(gosc({}, gd=True))
        self.assertEqual((st["ja"]["decydent"], st["ja"]["agent"]), (True, False))
        self.cfg["agent"]["zdalnie"] = True
        self.assertTrue(sesje._t_stan(gosc({}, gd=True))["ja"]["agent"])
        self.assertFalse(sesje._t_stan(gosc({}))["ja"]["agent"])

    def test_notatki_teraz(self):
        sid = self.z_zapisem()
        s, o = sesje._t_notatki(lokalny({}))
        self.assertEqual(s, 202)
        w = self.wywolania[0]
        kat = os.path.join(self.runtime, "sesje", sid)
        self.assertEqual(w["katalogi"], [kat])
        self.assertIn(os.path.join(kat, "transkrypcja.md").replace("\\", "/"), w["tekst"])
        self.assertNotIn("Ustalamy trzy poziomy", w["tekst"])                  # transkrypcja nie idzie w poleceniu
        self.assertIn("Sesje główne.md", w["tekst"])
        with mock.patch.object(agent, "stan_watku", lambda wid: {"trwa": True, "ostatnia_odpowiedz": None,
                                                                  "blad": None}):
            e = self.assertBlad(409, sesje._t_notatki, lokalny({}))            # przebieg „trwa”
        self.assertEqual(e.dodatkowe.get("kod"), "trwa")
        # koniec przebiegu: agent zapisał plik notatek
        with mock.patch.object(agent, "stan_watku", lambda wid: {"trwa": False, "ostatnia_odpowiedz": "Gotowe.",
                                                                  "blad": None}):
            time.sleep(0.05)
            with open(os.path.join(kat, "notatki.md"), "w", encoding="utf-8") as f:
                f.write("## Ustalenia\n- trzy poziomy\n")
            s2 = sesje._dokoncz_notatki(sesje._biezaca())
        self.assertFalse(s2["notatki"]["trwa"])
        self.assertTrue(s2["notatki"]["czas"])
        t = sesje._t_transkrypcja(lokalny({}))
        self.assertIn("trzy poziomy", t["notatki"]["tekst_md"])

    def test_notatki_automatyczne(self):
        self.cfg["sesje"]["notatki_co_min"] = 1
        sid = self.z_zapisem()
        sesje._zmien_sesje(sid, slucha_od="2020-01-01T00:00:00+00:00")
        sesje._tik["t"] = 0
        sesje._okresowo()
        self.assertEqual(len(self.wywolania), 1)
        self.assertEqual(self.wywolania[0]["kto"], "Karol")
        sesje._tik["t"] = 0
        sesje._okresowo()                                                        # trwa — drugi raz nie startuje
        self.assertEqual(len(self.wywolania), 1)

    def test_zakoncz_i_ustalenia(self):
        sid = self.z_zapisem()
        s, o = sesje._t_zakoncz(lokalny({}))
        self.assertEqual((s, o["sesja"]), (202, sid))
        self.assertIsNone(sesje._biezaca())
        koniec = time.time() + 10
        while time.time() < koniec and sesje._czytaj_sesje(sid)["zakonczenie"]["stan"] == "czeka_na_transkrypcje":
            time.sleep(0.05)
        w = self.wywolania[-1]
        self.assertIn("propozycj", w["tekst"])
        self.assertIn("Nigdy nie ustawiaj statusu zatwierdzona ani kanon", w["tekst"])
        self.assertIn("raport.py", w["tekst"])
        self.assertEqual(w["katalogi"], [os.path.join(self.runtime, "sesje", sid)])
        zak = sesje._czytaj_sesje(sid)["zakonczenie"]
        self.assertEqual((zak["stan"], zak["watek"]), ("agent", "w-test-1"))
        self.assertEqual(sesje._t_stan(lokalny())["zakonczenie"]["stan"], "agent")
        self.assertNotIn("watek", sesje._t_stan(gosc())["zakonczenie"])
        self.assertBlad(409, sesje._t_zakoncz, lokalny({}))                     # nie ma już trwającej sesji

    def test_zakoncz_bez_spisywania_zdalnie(self):
        self.z_zapisem()
        s, o = sesje._t_zakoncz(gosc({"spisz": False}, gd=True))
        self.assertEqual((s, o["spisz"]), (202, False))
        self.assertEqual(self.wywolania, [])

    def test_zaproponuj_tematy(self):
        s, o = sesje._t_zaproponuj(lokalny({}))
        self.assertEqual(s, 202)
        w = self.wywolania[0]
        self.assertIn("Pytania otwarte.md", w["tekst"])
        self.assertIn("Rejestr decyzji.md", w["tekst"])
        self.assertIn("propozycja agenta", w["tekst"])
        self.assertIsNone(w["katalogi"])

    def test_zawezone_narzedzia_i_dane_nie_polecenia(self):
        """Każde polecenie mówi, że treść od ludzi to dane; każde idzie z zawężonym zestawem narzędzi."""
        sid = self.z_zapisem()
        sesje._t_notatki(lokalny({}))
        sesje._t_zaproponuj(lokalny({}))
        sesje._t_zakoncz(lokalny({}))
        self.czekaj_na_koniec(sid)
        zestawy = [w["zestaw"] for w in self.wywolania]
        self.assertEqual(zestawy, ["czytanie", "sejf", "ustalenia"])
        for w in self.wywolania:
            self.assertIn(sesje.DANE_NIE_POLECENIA, w["tekst"])
        self.assertIn("Odpowiedz WYŁĄCZNIE pełną, nową wersją notatek", self.wywolania[0]["tekst"])
        self.assertNotIn("Write", self.wywolania[0]["tekst"])
        self.assertNotIn("NIEPEŁNY", self.wywolania[2]["tekst"])

    def test_notatki_z_odpowiedzi_agenta(self):
        """Agent notatek ma tylko narzędzia do czytania — plik notatek zapisuje panel z jego odpowiedzi."""
        sid = self.z_zapisem()
        sesje._t_notatki(lokalny({}))
        odp = "Oto notatki:\n\n## O czym mowa\n- karczma\n\n## Ustalenia\n- trzy poziomy trudności\n"
        with mock.patch.object(agent, "stan_watku", lambda wid: {"trwa": False, "ostatnia_odpowiedz": odp,
                                                                  "blad": None}):
            s = sesje._dokoncz_notatki(sesje._biezaca())
        self.assertFalse(s["notatki"]["trwa"])
        self.assertIsNone(s["notatki"]["blad"])
        with open(os.path.join(self.runtime, "sesje", sid, "notatki.md"), encoding="utf-8") as f:
            tekst = f.read()
        self.assertTrue(tekst.startswith("## O czym mowa"), tekst)                # bez wstępu agenta
        self.assertIn("trzy poziomy trudności", tekst)
        # odpowiedź, która nie jest notatkami: błąd zamiast nadpisania pliku
        sesje._t_notatki(lokalny({}))
        with mock.patch.object(agent, "stan_watku", lambda wid: {"trwa": False, "ostatnia_odpowiedz": "Nie mogę.",
                                                                  "blad": None}):
            s = sesje._dokoncz_notatki(sesje._biezaca())
        self.assertTrue(s["notatki"]["blad"])
        with open(os.path.join(self.runtime, "sesje", sid, "notatki.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), tekst)

    def odcinek_w_kolejce(self, sid, nr):
        """Odcinek czekający na transkrypcję (robotnik w testach się nie uruchamia)."""
        with mock.patch.dict(os.environ, {"BC_GLOS_ATRAPA": "1"}):
            return glos.nowy_odcinek(sid, nr, WEBM, "webm", {"kto": "Paweł", "t0": rdzen.teraz()})

    def test_zakoncz_z_niepelnym_zapisem(self):
        sid = self.z_zapisem()
        self.odcinek_w_kolejce(sid, 1)                                            # nigdy nie zostanie spisany
        sesje._t_zakoncz(lokalny({}))
        zak = self.czekaj_na_koniec(sid)
        self.assertEqual((zak["stan"], zak["brakujace"]), ("agent", 1))
        self.assertIn("NIEPEŁNY", self.wywolania[-1]["tekst"])
        self.assertIn("1 odcinek nagrania", self.wywolania[-1]["tekst"])
        self.assertEqual(sesje._t_stan(gosc())["zakonczenie"]["brakujace"], 1)

    def test_zakoncz_czeka_dopoki_kolejka_maleje(self):
        """Limit bez postępu to 1 s, ale kolejka maleje co 0,7 s — panel czeka do końca i zapis jest pełny."""
        sid = self.z_zapisem()
        nid1 = self.odcinek_w_kolejce(sid, 1)
        nid2 = self.odcinek_w_kolejce(sid, 2)

        def robotnik():
            with mock.patch.dict(os.environ, {"BC_GLOS_ATRAPA": "1"}):
                tr = glos._Transkryptor()
                for nid in (nid1, nid2):
                    time.sleep(0.7)
                    glos._przetworz(nid, tr)
        w = threading.Thread(target=robotnik)
        w.start()
        t0 = time.time()
        sesje._t_zakoncz(lokalny({}))
        zak = self.czekaj_na_koniec(sid)
        w.join(10)
        self.assertGreater(time.time() - t0, 1.2)
        self.assertEqual(zak["stan"], "agent")
        self.assertNotIn("brakujace", zak)
        self.assertEqual(sesje._czytaj_sesje(sid)["wpisy"], 3)
        self.assertNotIn("NIEPEŁNY", self.wywolania[-1]["tekst"])


# =========================================================================== prywatność
class TestPrywatnosc(Baza):
    def test_zapis_rozmowy_tylko_dla_pokoju_i_komputera(self):
        u, k, _ = self.dolacz(lokalny())
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        sesje._dopisz_wpisy(sesje._biezaca()["id"], [{"t": rdzen.teraz(), "kto": "Karol", "tekst": "tajne"}])
        self.assertBlad(400, sesje._t_transkrypcja, gosc({}))                     # spoza pokoju
        u2, k2, _ = self.dolacz(gosc())
        self.assertEqual(sesje._t_transkrypcja(gosc({"u": u2, "k": k2}))["wpisy"][0]["tekst"], "tajne")
        self.assertEqual(sesje._t_transkrypcja(lokalny({}))["wpisy"][0]["tekst"], "tajne")  # przy komputerze
        self.assertBlad(403, sesje._t_pobierz, gosc())
        self.assertBlad(403, sesje._t_lista, gosc())
        odp = sesje._t_pobierz(lokalny())
        self.assertIn(b"tajne", odp.cialo)
        self.assertIn("attachment", odp.naglowki["Content-Disposition"])
        self.assertBlad(404, sesje._t_pobierz, lokalny(query={"sesja": "../../sejf"}))
        self.assertBlad(404, sesje._t_transkrypcja, lokalny({"sesja": "../../sejf"}))
        self.assertBlad(400, sesje._t_transkrypcja, gosc({"u": "x", "k": k2}))
        # nic z rozmowy w stanie, w obecności ani w zdrowiu
        for obj in (sesje._t_stan(gosc()), sesje.obecni(), sesje.zdrowie()):
            self.assertNotIn("tajne", json.dumps(obj, ensure_ascii=False))
            self.assertNotIn(k, json.dumps(obj, ensure_ascii=False))

    def test_gosc_w_pokoju_nie_czyta_zakonczonej_sesji(self):
        """Pole `sesja` (dawne sesje) tylko przy komputerze; identyfikatora zakończonej sesji gość nie dostaje."""
        sesje._t_sluchanie(lokalny({"wlacz": True}))
        stara = sesje._biezaca()["id"]
        sesje._dopisz_wpisy(stara, [{"t": rdzen.teraz(), "kto": "Karol", "tekst": "stara tajemnica"}])
        sesje._t_zakoncz(lokalny({"spisz": False}))
        st_gosc = sesje._t_stan(gosc())
        self.assertNotIn("sesja", st_gosc["zakonczenie"])
        self.assertNotIn(stara, json.dumps(st_gosc))
        self.assertEqual(sesje._t_stan(lokalny())["zakonczenie"]["sesja"], stara)
        u, k, o = self.dolacz(gosc())                                            # pusty pokój, gość wchodzi
        self.assertNotIn(stara, json.dumps(o))
        e = self.assertBlad(403, sesje._t_transkrypcja, gosc({"u": u, "k": k, "sesja": stara}))
        self.assertNotIn("tajemnica", e.komunikat)
        self.assertBlad(403, sesje._t_transkrypcja, gosc({"u": u, "k": k, "sesja": stara}, gd=True))
        t = sesje._t_transkrypcja(gosc({"u": u, "k": k}))                        # bieżącej sesji nie ma
        self.assertEqual((t["sesja"], t["wpisy"]), (None, []))
        t = sesje._t_transkrypcja(lokalny({"sesja": stara}))                     # przy komputerze — tak
        self.assertEqual([w["tekst"] for w in t["wpisy"]], ["stara tajemnica"])

    def test_turn_tylko_z_konfiguracji_lokalnej_i_tylko_uczestnikom(self):
        wspolna = rdzen._bezpieczna_wspolna({"sesje": {"turn": {"adres": "turn:zly.example:3478", "uzytkownik": "a",
                                                                "haslo": "b"}, "zostaw_dzwiek": True,
                                                       "max_osob": 4}})
        self.assertEqual(wspolna["sesje"], {"max_osob": 4})
        self.cfg["sesje"]["turn"] = {"adres": "turn:turn.example.org:3478", "uzytkownik": "u", "haslo": "tajne-haslo"}
        self.cfg["sesje"]["stun"] = ["stun:ok.example:3478", "http://zly", "stun:zły znak"]
        u, k, o = self.dolacz(gosc())
        self.assertEqual(o["ice"][0], {"urls": ["stun:ok.example:3478"]})
        self.assertEqual(o["ice"][1]["credential"], "tajne-haslo")
        self.assertNotIn("tajne-haslo", json.dumps(sesje._t_stan(gosc()), ensure_ascii=False))
        self.assertNotIn("tajne-haslo", json.dumps(sesje.zdrowie(), ensure_ascii=False))

    def test_sciezki_nie_z_danych_klienta(self):
        self.assertBlad(400, sesje._kat, "../../etc")
        self.assertBlad(400, sesje._kat, "20261113-201500-ab12/../../x")
        self.assertIsNone(glos.RX_ODCINEK.match("s-../x-000001"))
        self.assertIn(os.path.join("sesje", "20261113-201500-ab12", "odcinki"),
                      glos._kat("s-20261113-201500-ab12-000001"))

    def test_agent_add_dir_tylko_katalogi_sesji(self):
        kat = os.path.join(self.runtime, "sesje", "20261113-201500-ab12")
        os.makedirs(kat)
        self.assertEqual(agent._katalogi_sesji([kat, self.runtime, rdzen.REPO, "C:\\Windows", None]),
                         [os.path.realpath(kat)])
        cmd = agent.zbuduj_polecenie("claude", "praca", katalogi=[kat])
        self.assertEqual(cmd[cmd.index("--add-dir") + 1], os.path.realpath(kat))
        self.assertNotIn("--add-dir", agent.zbuduj_polecenie("claude", "praca"))


# =========================================================================== prawdziwy serwer
class TestSesjeAPI(test_api.SerwerTestowy):
    """Trasy na prawdziwym serwerze; odcinek przechodzi przez robotnika bc.glos w osobnym procesie (atrapa)."""

    @classmethod
    def konfiguracja_lokalna(cls):
        cls.sejf = os.path.join(cls.tmp, "sejf")
        return {"gra": {"universeId": None}, "sejfy": [{"id": "B&C", "nazwa": "Sejf testowy", "sciezka": cls.sejf}],
                "sesje": {"stun": [], "notatki_co_min": 0, "odcinek_s": 4}}

    @classmethod
    def przygotuj(cls, runtime):
        os.makedirs(os.path.join(cls.sejf, "Produkcja"))
        for nazwa, tekst in list(PLIKI.values()) + [("Sesje główne.md", AGENDA)]:
            with open(os.path.join(cls.sejf, "Produkcja", nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)

    @classmethod
    def setUpClass(cls):
        stare = {k: os.environ.get(k) for k in ("BC_GLOS_ATRAPA", "BC_GLOS_CZEKAJ_S")}
        os.environ.update(BC_GLOS_ATRAPA="1", BC_GLOS_CZEKAJ_S="2")         # serwer i jego robotnik: atrapa
        try:
            super().setUpClass()
        finally:
            for k, v in stare.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_droga_przez_serwer(self):
        s, o, _ = self.get("/api/sesje/agenda", zdalny=True)
        self.assertEqual((s, len(o["do_omowienia"])), (200, 2))
        s, a, _ = self.post("/api/sesje/dolacz", {}, kto="Karol")
        self.assertEqual(s, 201, a)
        s, b, _ = self.post("/api/sesje/dolacz", {}, kto="Paweł", zdalny=True)
        self.assertEqual(s, 201, b)
        self.assertEqual(self.post("/api/sesje/sygnal", {"u": a["u"], "k": a["k"], "do": b["u"], "typ": "oferta",
                                                         "dane": {"sdp": "v=0"}})[0], 200)
        s, o, _ = self.post("/api/sesje/odbierz", {"u": b["u"], "k": b["k"], "czekaj": 1}, zdalny=True)
        self.assertEqual([x["dane"] for x in o["sygnaly"]], [{"sdp": "v=0"}])
        self.assertBlad(self.post("/api/sesje/sluchanie", {"wlacz": True}, zdalny=True, kto="Paweł"), 403)
        self.assertBlad(self.post("/api/sesje/sluchanie", {"wlacz": True}, xbc=False), 403)
        self.assertEqual(self.post("/api/sesje/sluchanie", {"wlacz": True}, kto="Karol")[0], 200)
        s, o, _ = self.zadanie("POST", "/api/sesje/odcinek?nr=1&t=%d" % int(time.time() * 1000), surowe=WEBM,
                               ct="audio/webm;codecs=opus", zdalny=True, kto="Paweł",
                               naglowki={"X-BC-Sesja": "%s:%s" % (b["u"], b["k"])})
        self.assertEqual(s, 201, o)
        self.assertBlad(self.get("/api/glos/" + o["id"]), 404)                  # nie przez trasę głosówek
        wpisy = []
        koniec = time.time() + 40
        while time.time() < koniec and not wpisy:
            self.post("/api/sesje/puls", {"u": a["u"], "k": a["k"]})
            wpisy = self.post("/api/sesje/transkrypcja", {"u": b["u"], "k": b["k"]}, zdalny=True)[1]["wpisy"]
            time.sleep(0.5)
        self.assertEqual([(w["kto"], w["tekst"]) for w in wpisy], [("Paweł", glos.TEKST_ATRAPY)])
        self.assertBlad(self.post("/api/sesje/transkrypcja", {}, zdalny=True), 400)    # gość spoza pokoju
        self.assertBlad(self.get("/api/sesje/pobierz", zdalny=True), 403)
        s, _, (nagl, tresc) = self.zadanie("GET", "/api/sesje/pobierz", bajty=True)
        self.assertEqual(s, 200)
        self.assertIn(glos.TEKST_ATRAPY.encode("utf-8"), tresc)
        ob = self.get("/api/obecnosc", zdalny=True)[1]["rozmowa"]
        self.assertEqual(([o["kto"] for o in ob["osoby"]], ob["slucha"]), (["Karol", "Paweł"], True))
        self.assertBlad(self.post("/api/sesje/zakoncz", {}, zdalny=True, kto="Paweł"), 403)
        self.assertBlad(self.post("/api/sesje/agenda/zaproponuj", {}, zdalny=True), 403)
        for sid in os.listdir(os.path.join(self.tmp, "runtime", "sesje")):
            kat = os.path.join(self.tmp, "runtime", "sesje", sid, "odcinki")
            if os.path.isdir(kat):
                self.assertEqual(os.listdir(kat), [], kat)                      # dźwięk i odcinek sprzątnięte
        self.assertEqual(self.post("/api/sesje/opusc", {"u": b["u"], "k": b["k"]}, zdalny=True)[0], 200)
        # robotnik czeka 2 s na kolejne odcinki i kończy się sam
        time.sleep(3)


if __name__ == "__main__":
    unittest.main()
