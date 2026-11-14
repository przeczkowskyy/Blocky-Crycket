# -*- coding: utf-8 -*-
"""Okna agenta w zakładce Agent (bc/agent.py): karty okien, reguła krótkich odpowiedzi w poleceniu systemowym,
zestawy narzędzi okien, usuwanie rozmów, tytuł z pierwszego pytania, autor przy wiadomości, zgodność starych wątków
i wątków zakładanych przez panel dla sesji głosowych.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_agent_okna

- TestOknaAgenta: trasy wołane w tym procesie; uruchamianie procesu agenta (_bezpiecznie) jest podmienione atrapą,
  która tylko zapamiętuje wiersz poleceń i wejście (jak w test_agent.py).
- TestAgentAPIZAtrapa: prawdziwy serwer panelu (jak test_api.py) z ATRAPĄ programu Claude Code
  (testy/atrapa_agenta.cjs przez `node`): pełna droga przebiegu — zapis wątku, strumień, polecenie systemowe,
  usuwanie w trakcie przebiegu i dostęp zdalny. Pomijany bez Node. Prawdziwy `claude` nie jest nigdy uruchamiany.
"""
import glob
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(PANEL)
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import agent, rdzen  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402
from testy import test_api  # noqa: E402  (bez importu klas testów do tej przestrzeni)

# zakazy z 13–14.11 — okna nie mogą ich osłabić (lista może tylko rosnąć)
ZAKAZY_PRZED_OKNAMI = ["Read(./.env)", "Read(./.env.*)", "Edit(./.env)", "Edit(./.claude/**)", "Edit(./CLAUDE.md)",
                       "Edit(./panel/konfiguracja.json)", "Edit(./B&C/.obsidian/**)", "Edit(./B&C/Źródła/**)"]
# dopisane przy oknach: karty okien (polecenie systemowe rozmów) i pliki, które uruchamiają programy — także dla
# agentów sesji głosowych, którzy czytają treść od gości
ZAKAZY_NOWE = ["Edit(./panel/agenci/**)", "Edit(./.mcp.json)", "Edit(./.git/**)"]


class Z:
    """Udawane żądanie (bc.http.Zadanie)."""

    def __init__(self, kto="Karol", lokalny=True, dane=None, wid=None, z_naglowka=True, query=None):
        self.kto, self.lokalny, self.json, self.params = kto, lokalny, dane, {"id": wid}
        self.kto_z_naglowka = z_naglowka
        self.query = query or {}


def lokalny(kto="Karol", dane=None, wid=None):
    return Z(kto, True, dane, wid)


def zdalny(kto="Paweł", dane=None, wid=None, z_naglowka=True):
    return Z(kto, False, dane, wid, z_naglowka)


def polecenie_systemowe(cmd):
    return cmd[cmd.index("--append-system-prompt") + 1]


def lista_po(cmd, flaga):
    """Wartości flagi o wielu argumentach (do następnej flagi zaczynającej się od --)."""
    i = cmd.index(flaga) + 1
    out = []
    while i < len(cmd) and not cmd[i].startswith("--"):
        out.append(cmd[i])
        i += 1
    return out


# =========================================================================== karty okien
class TestKartyOkien(unittest.TestCase):
    def test_piec_okien_z_kartami(self):
        self.assertEqual(agent.ID_OKIEN, ["ogolny", "balans", "swiat", "modele", "wydanie"])
        for o in agent.OKNA:
            k = agent.karta_okna(o["id"])
            self.assertFalse(k["brak_karty"], o["id"])
            self.assertTrue(k["nazwa"] and k["opis"], o["id"])
            self.assertEqual(k["narzedzia"], o["narzedzia"], o["id"])                    # karta = domyślny zestaw
            for sekcja in ("## Rola", "## Na start przeczytaj", "## Jak odpowiadać", "## Co i gdzie zapisywać",
                           "## Narzędzia"):
                self.assertIn(sekcja, k["tresc"], (o["id"], sekcja))
            self.assertIn("propozycja", k["tresc"])
            self.assertIn("Nigdy nie ustawiaj statusu `kanon`", k["tresc"], o["id"])
            self.assertIn("Rozstrzyga: D-0XX", k["tresc"], o["id"])
            self.assertIn("Pierwsze zdanie to odpowiedź albo wniosek", k["tresc"], o["id"])
            self.assertLess(len(k["tresc"]), agent.MAX_KARTA, o["id"])
            self.assertLessEqual(len(k["opis"].split()), 20, o["id"])                    # jedno krótkie zdanie

    def test_notatki_na_start_istnieja(self):
        """Każda ścieżka `B&C/…` w kartach wskazuje istniejący plik sejfu."""
        for o in agent.OKNA:
            tresc = agent.karta_okna(o["id"])["tresc"]
            start = tresc.split("## Na start przeczytaj", 1)[1].split("\n## ", 1)[0]
            sciezki = re.findall(r"`(B&C/[^`]+)`", tresc)
            self.assertGreaterEqual(len(re.findall(r"`(B&C/[^`]+)`", start)), 5, o["id"])
            for s in sciezki:
                if "0XX" in s:
                    continue
                pelna = os.path.join(REPO, *s.rstrip("/").split("/"))
                ok = os.path.isdir(pelna) if s.endswith("/") else os.path.isfile(pelna)
                self.assertTrue(ok, "%s: brak %s" % (o["id"], s))
            self.assertIn("B&C/Produkcja/Rejestr decyzji.md", start, o["id"])

    def test_modele_bez_kolejki_pracy(self):
        """Modele: na razie tylko rozmowa i propozycje — zlecenie w notatce-propozycji, nie w Zadaniach."""
        zapis = agent.karta_okna("modele")["tresc"].split("## Co i gdzie zapisywać", 1)[1].split("\n## ", 1)[0]
        self.assertNotIn("jako zadanie", zapis)
        self.assertIn("Do `B&C/Produkcja/Zadania.md` nie dopisujesz", zapis)
        self.assertIn("status: propozycja", zapis)

    def test_parsowanie_i_brak_karty(self):
        pola, tresc = agent._parsuj_karte("﻿---\r\nnazwa: X\r\nnarzędzia: sejf\r\n---\r\n\r\n# T\r\nTreść\r\n")
        self.assertEqual(pola, {"nazwa": "X", "narzedzia": "sejf"})
        self.assertEqual(tresc, "# T\nTreść")
        tmp = tempfile.mkdtemp(prefix="bc_test_karty_")
        try:
            with mock.patch.object(agent, "KATALOG_KART", tmp):
                agent._karty.clear()
                k = agent.karta_okna("balans")                                       # brak pliku: wartości domyślne
                self.assertEqual((k["brak_karty"], k["narzedzia"], k["tresc"]), (True, "sejf", ""))
                with open(os.path.join(tmp, "balans.md"), "w", encoding="utf-8") as f:
                    f.write("---\nnazwa: Liczby\nnarzedzia: wszystko\n---\nRola testowa.\n")
                k = agent.karta_okna("balans")                                       # zmiana pliku bez restartu
                self.assertEqual((k["nazwa"], k["narzedzia"], k["tresc"]), ("Liczby", "sejf", "Rola testowa."))
                self.assertIn(agent.REGULA_STYLU, agent.dopisek_okna(k))             # reguła zawsze, także bez karty
                self.assertEqual(agent.karta_okna("nie-ma")["id"], "ogolny")
        finally:
            agent._karty.clear()
            shutil.rmtree(tmp, ignore_errors=True)

    def test_zestawy_narzedzi_okien(self):
        for z in ZAKAZY_PRZED_OKNAMI + ZAKAZY_NOWE:                                 # zakazy tylko rosną
            self.assertIn(z, agent.ZAKAZANE_W_ZESTAWACH, z)
            self.assertIn(z, agent.ZAKAZANE_W_OKNACH, z)
        for zestaw in agent.ZESTAWY_NARZEDZI:                                       # agenci sesji głosowych też
            zakazane = lista_po(agent.zbuduj_polecenie("claude", "praca", zestaw=zestaw), "--disallowedTools")
            for z in ZAKAZY_PRZED_OKNAMI + ZAKAZY_NOWE:
                self.assertIn(z, zakazane, (zestaw, z))
        for oid in agent.ID_OKIEN:
            k = agent.karta_okna(oid)
            for tryb in ("plan", "praca", "auto"):
                cmd = agent.zbuduj_polecenie("claude", tryb, narzedzia_okna=k["narzedzia"], dopisek="x")
                zakazane = lista_po(cmd, "--disallowedTools")
                for z in ZAKAZY_PRZED_OKNAMI + ZAKAZY_NOWE:
                    self.assertIn(z, zakazane, (oid, tryb, z))
                if oid == "ogolny":                                                 # jak dotąd, tylko bez sieci
                    self.assertNotIn("--tools", cmd)
                    self.assertIn("WebSearch", zakazane)
                    self.assertIn("WebFetch", zakazane)
                    continue
                wbudowane = cmd[cmd.index("--tools") + 1].split(",")
                dozwolone = lista_po(cmd, "--allowedTools")
                self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "dontAsk")
                self.assertIn("--strict-mcp-config", cmd)
                self.assertNotIn("--mcp-config", cmd)
                self.assertFalse(any(n.startswith(("Bash", "mcp__")) for n in wbudowane + dozwolone), (oid, dozwolone))
                siec = oid == "wydanie"
                for n in ("WebSearch", "WebFetch"):
                    self.assertEqual(n in wbudowane and n in dozwolone, siec, (oid, tryb, n))
                    self.assertEqual(n in zakazane, not siec, (oid, tryb, n))
                # zapis tylko w sejfie: nigdy gołe Edit / Write (zapis w całym repozytorium)
                self.assertFalse({"Edit", "Write"} & set(dozwolone), (oid, tryb, dozwolone))
                if tryb == "plan":
                    self.assertFalse({"Edit", "Write"} & set(wbudowane), (oid, wbudowane))
                    self.assertFalse(any(n.startswith(("Edit", "Write")) for n in dozwolone), (oid, dozwolone))
                else:
                    self.assertTrue({"Edit", "Write"} <= set(wbudowane), (oid, wbudowane))
                    zapis = [n for n in dozwolone if n.startswith(("Edit", "Write"))]
                    self.assertEqual(zapis, ["Edit(./B&C/**)", "Write(./B&C/**)"], (oid, tryb))
                # bez poleceń w terminalu, więc bez polecenia publikowania raportu
                sp = polecenie_systemowe(cmd)
                self.assertTrue(sp.startswith(agent.INSTRUKCJA_OKNA), oid)
                self.assertNotIn("raport.py dodaj", sp, oid)
        sp = polecenie_systemowe(agent.zbuduj_polecenie("claude", "praca", narzedzia_okna="ogolny", dopisek="x"))
        self.assertTrue(sp.startswith(agent.INSTRUKCJA) and "raport.py dodaj" in sp)    # Ogólny: raport jak dotąd
        bez = agent.zbuduj_polecenie("claude", "praca")                            # wywołania sprzed okien: jak dawniej
        self.assertNotIn("--disallowedTools", bez)
        self.assertEqual(polecenie_systemowe(bez), agent.INSTRUKCJA)

    def test_czytanie_tylko_w_projekcie(self):
        """Żaden zestaw nie ma gołego Read / Glob / Grep — goła nazwa pozwalała czytać dowolny plik na dysku
        (sprawdzone 14.11.2026 na prawdziwym programie claude; reguła ze ścieżką odmawia czytania spoza projektu)."""
        gole = {"Read", "Glob", "Grep"}
        zestawy = dict(agent.ZESTAWY_NARZEDZI)
        zestawy.update({"okno:" + k: v for k, v in agent.ZESTAWY_OKIEN.items() if v is not None})
        zestawy["praca"] = agent.DOZWOLONE_NARZEDZIA
        for nazwa, lista in zestawy.items():
            self.assertFalse(gole & set(lista), "goły odczyt w zestawie " + nazwa)
            for n in ("Read(./**)", "Glob(./**)", "Grep(./**)"):
                self.assertIn(n, lista, nazwa)
        # w wierszu poleceń: nazwy narzędzi w --tools są gołe (to lista wbudowanych), ale zezwolenia mają ścieżkę
        for okno in ("sejf", "sejf_siec"):
            for tryb in ("plan", "praca"):
                cmd = agent.zbuduj_polecenie("claude", tryb, narzedzia_okna=okno, dopisek="x")
                dozwolone = cmd[cmd.index("--allowedTools") + 1:cmd.index("--disallowedTools")]
                self.assertFalse(gole & set(dozwolone), (okno, tryb))
        for zestaw in agent.ZESTAWY_NARZEDZI:
            cmd = agent.zbuduj_polecenie("claude", "praca", zestaw=zestaw)
            dozwolone = cmd[cmd.index("--allowedTools") + 1:cmd.index("--disallowedTools")]
            self.assertFalse(gole & set(dozwolone), zestaw)

    def test_tytul_z_pytania(self):
        self.assertEqual(agent.tytul_z_pytania("## Ile kosztuje miecz?\nszczegóły"), "Ile kosztuje miecz?")
        t = agent.tytul_z_pytania("Ile czasu zajmuje dojście z lasu do biomu kryształowego przy obecnych nagrodach")
        self.assertTrue(t.endswith("…") and len(t) <= 49 and " " in t, t)
        self.assertEqual(agent.tytul_z_pytania("\n\n  "), "Rozmowa")


# =========================================================================== trasy w tym procesie
class TestOknaAgenta(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_okna_")
        self.cfg = {"agent": {"limit_czasu_min": 5, "zdalnie": True}}
        self.przebiegi = []

        def udawany(p, cmd, wejscie, limit_min):
            koniec = threading.Event()
            self.przebiegi.append((p, cmd, wejscie, koniec))
            koniec.wait(10)
            if not p.zakonczony:
                p.zdarzenie("koniec")

        self.latki = [mock.patch.object(rdzen, "RUNTIME", self.tmp),
                      mock.patch.object(rdzen, "konfiguracja", lambda: self.cfg),
                      mock.patch.object(rdzen, "log", lambda *a: None),
                      mock.patch.object(agent, "znajdz_program", lambda: "claude"),
                      mock.patch.object(agent, "_bezpiecznie", udawany)]
        for l in self.latki:
            l.start()
        agent._przebiegi.clear()
        agent._licznik_n.clear()

    def tearDown(self):
        for _, _, _, koniec in self.przebiegi:
            koniec.set()
        for t in [t for t in threading.enumerate() if t.name.startswith("agent-")]:
            t.join(5)
        agent._przebiegi.clear()
        agent._licznik_n.clear()
        for l in reversed(self.latki):
            l.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def czekaj(self, ile):
        for _ in range(300):
            if len(self.przebiegi) >= ile:
                return self.przebiegi[ile - 1]
            time.sleep(0.01)
        self.fail("Przebieg agenta nie wystartował")

    def zakoncz(self, i=-1):
        p, _, _, koniec = self.przebiegi[i]
        koniec.set()
        for t in [t for t in threading.enumerate() if t.name == "agent-" + p.wid]:
            t.join(5)

    def nowy(self, z, okno=None, tytul=None):
        dane = {}
        if okno:
            dane["okno"] = okno
        if tytul:
            dane["tytul"] = tytul
        z.json = dane
        s, w = agent._nowy(z)
        self.assertEqual(s, 201)
        return w

    def napisz(self, z, wid, tekst, **pola):
        z.json = dict({"tekst": tekst}, **pola)
        z.params = {"id": wid}
        s, r = agent._wiadomosc(z)
        self.assertEqual(s, 202, r)
        return r

    def stary_watek(self, wid, **pola):
        w = dict({"id": wid, "tytul": "Stara rozmowa", "utworzono": "2026-11-12T10:00:00+01:00",
                  "ostatnio": "2026-11-12T10:05:00+01:00", "session_id": None,
                  "wiadomosci": [{"nr": 1, "rola": "user", "tekst": "Stare pytanie", "kto": "Karol"}]}, **pola)
        rdzen.zapisz_json(os.path.join(agent._kat_watkow(), wid + ".json"), w)

    def usun(self, z, wid, **dane):
        z.json, z.params = dane, {"id": wid}
        return agent._usun(z)

    # ------------------------------------------------------------------ polecenie systemowe
    def test_regula_stylu_i_karta_w_poleceniu_systemowym(self):
        w = self.nowy(zdalny("Zenobiusz"), "balans", tytul="TYTUL-OD-CZLOWIEKA")
        self.assertEqual(w["okno"], "balans")
        r = self.napisz(zdalny("Zenobiusz"), w["id"], "PYTANIE-XYZ: ile kosztuje miecz?")
        _, cmd, wejscie, _ = self.czekaj(1)
        sp = polecenie_systemowe(cmd)
        self.assertTrue(sp.startswith(agent.INSTRUKCJA_OKNA))
        self.assertNotIn("raport.py dodaj", sp)                                    # Balans nie ma poleceń
        self.assertIn(agent.REGULA_STYLU, sp)
        self.assertIn("Okno agenta w panelu: Balans", sp)
        self.assertIn(agent.karta_okna("balans")["tresc"], sp)
        for obce in ("PYTANIE-XYZ", "TYTUL-OD-CZLOWIEKA", "Zenobiusz"):         # treść od ludzi tylko w wiadomości
            self.assertNotIn(obce, sp)
        self.assertIn("PYTANIE-XYZ", wejscie)
        self.assertIn("[Panel zespołu · pisze: Zenobiusz]", wejscie)
        self.assertNotIn("WebSearch", cmd[cmd.index("--tools") + 1])
        self.assertEqual(r["tryb"], "praca")
        self.zakoncz()
        # okno Wydanie: sieć; okno Ogólny: tryb jak dotąd, sieć zakazana, karta Ogólnego
        w2 = self.nowy(lokalny(), "wydanie")
        self.napisz(lokalny(), w2["id"], "Czy wolno sprzedawać jajka za Robuxy?", tryb="plan")
        _, cmd, _, _ = self.czekaj(2)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "Read,Glob,Grep,WebSearch,WebFetch")
        self.assertIn("Okno agenta w panelu: Wydanie", polecenie_systemowe(cmd))
        self.zakoncz()
        w3 = self.nowy(lokalny())
        self.assertEqual(w3["okno"], "ogolny")
        r3 = self.napisz(lokalny(), w3["id"], "Co dalej?", tryb="auto")
        _, cmd, _, _ = self.czekaj(3)
        self.assertEqual((r3["tryb"], cmd[cmd.index("--permission-mode") + 1]), ("auto", "auto"))
        self.assertIn("WebFetch", lista_po(cmd, "--disallowedTools"))
        self.assertIn(agent.REGULA_STYLU, polecenie_systemowe(cmd))
        self.assertIn("Okno agenta w panelu: Ogólny", polecenie_systemowe(cmd))
        self.zakoncz()

    def test_auto_w_oknie_z_zestawem_to_praca(self):
        w = self.nowy(lokalny(), "swiat")
        r = self.napisz(lokalny(), w["id"], "Jakie potwory w lesie?", tryb="auto")
        _, cmd, _, _ = self.czekaj(1)
        self.assertEqual((r["tryb"], cmd[cmd.index("--permission-mode") + 1]), ("praca", "dontAsk"))
        self.assertEqual(agent._czytaj_watek(w["id"])["wiadomosci"][0]["tryb"], "praca")
        self.zakoncz()
        self.assertEqual(agent.okna(False)[1]["tryby"], ["plan", "praca"])
        self.assertEqual(agent.okna(False)[0]["tryby"], ["plan", "praca"])         # zdalnie bez Auto
        self.assertEqual(agent.okna(True)[0]["tryby"], ["plan", "praca", "auto"])
        self.assertEqual([o["siec"] for o in agent.okna()], [False, False, False, False, True])
        st = agent._stan(lokalny())
        self.assertEqual([o["id"] for o in st["okna"]], agent.ID_OKIEN)
        self.assertIn("usuwanie", st["funkcje"])
        self.assertNotIn("tresc", st["okna"][1])                                   # treść karty tylko dla agenta

    def test_nieznane_okno(self):
        for zle in ({"okno": "kosmos"}, {"okno": 5}, {"okno": "balans", "inne": 1}):
            z = lokalny(dane=zle)
            with self.assertRaises(BladHTTP) as k:
                agent._nowy(z)
            self.assertEqual(k.exception.status, 400)
        with self.assertRaises(BladHTTP) as k:
            agent._lista(Z(query={"okno": "kosmos"}))
        self.assertEqual(k.exception.status, 400)

    # ------------------------------------------------------------------ tytuł, autor, wspólne rozmowy
    def test_tytul_z_pierwszego_pytania_i_zmiana(self):
        w = self.nowy(lokalny(), "balans")
        self.assertEqual((w["tytul"], w["tytul_auto"]), ("Nowa rozmowa", True))
        self.napisz(lokalny(), w["id"], "Ile Złota za pierwszy poziom?\nI jeszcze coś")
        self.czekaj(1)
        self.zakoncz()
        self.assertEqual(agent._czytaj_watek(w["id"])["tytul"], "Ile Złota za pierwszy poziom?")
        self.napisz(zdalny("Paweł"), w["id"], "Drugie pytanie zmienia tytuł?")
        self.czekaj(2)
        self.zakoncz()
        self.assertEqual(agent._czytaj_watek(w["id"])["tytul"], "Ile Złota za pierwszy poziom?")
        z = lokalny(dane={"tytul": "  Koszty   poziomów "}, wid=w["id"])
        self.assertEqual(agent._zmien_tytul(z)["tytul"], "Koszty poziomów")
        for zle in ({"tytul": "  "}, {"tytul": 5}, {}):
            with self.assertRaises(BladHTTP) as k:
                agent._zmien_tytul(lokalny(dane=zle, wid=w["id"]))
            self.assertEqual(k.exception.status, 400)
        with self.assertRaises(BladHTTP) as k:                                      # Paweł nie założył tej rozmowy
            agent._zmien_tytul(zdalny("Paweł", {"tytul": "Moje"}, w["id"]))
        self.assertEqual(k.exception.status, 403)

    def test_autor_przy_wiadomosci_i_osoby(self):
        w = self.nowy(zdalny("Paweł"), "swiat")
        self.napisz(zdalny("Paweł"), w["id"], "Jak wygląda golem?")
        self.czekaj(1)
        self.zakoncz()
        self.napisz(lokalny("Karol"), w["id"], "A kryształowe slimy?")
        self.czekaj(2)
        self.zakoncz()
        widok = agent._watek(lokalny(wid=w["id"]))
        ludzie = [(m["kto"], m["zdalnie"]) for m in widok["wiadomosci"] if m["rola"] == "user"]
        self.assertEqual(ludzie, [("Paweł", True), ("Karol", False)])
        self.assertEqual((widok["utworzyl"], widok["zdalnie"]), ("Paweł", True))
        self.assertEqual(widok["osoby"], [{"kto": "Paweł", "zdalnie": True}, {"kto": "Karol", "zdalnie": False}])
        wpis = next(x for x in agent._lista(lokalny())["watki"] if x["id"] == w["id"])
        self.assertEqual((wpis["okno"], wpis["utworzyl"], len(wpis["osoby"])), ("swiat", "Paweł", 2))

    # ------------------------------------------------------------------ zgodność
    def test_stare_watki_trafiaja_do_ogolnego(self):
        self.stary_watek("w-20261112-100000-aaaa")
        self.stary_watek("w-20261113-200000-bbbb", katalogi=[], tytul="Sesja główna — notatki")   # stare polecenie panelu
        self.stary_watek("w-20261113-200000-cccc", okno="kosmos")
        lista = {x["id"]: x for x in agent._lista(lokalny())["watki"]}
        self.assertEqual(lista["w-20261112-100000-aaaa"]["okno"], "ogolny")
        self.assertFalse(lista["w-20261112-100000-aaaa"]["systemowy"])
        self.assertTrue(lista["w-20261113-200000-bbbb"]["systemowy"])
        self.assertEqual(lista["w-20261113-200000-cccc"]["okno"], "ogolny")
        self.assertEqual(agent._lista(Z(query={"okno": "balans"}))["watki"], [])
        self.assertEqual(len(agent._lista(Z(query={"okno": "ogolny"}))["watki"]), 3)
        self.assertIsNone(lista["w-20261112-100000-aaaa"]["zdalnie"])
        # stary wątek dalej działa: wiadomość idzie z kartą Ogólnego
        self.napisz(lokalny(), "w-20261112-100000-aaaa", "Ciąg dalszy")
        _, cmd, _, _ = self.czekaj(1)
        self.assertIn("Okno agenta w panelu: Ogólny", polecenie_systemowe(cmd))
        self.zakoncz()

    def test_polecenia_panelu_bez_zmian_i_systemowe(self):
        """uruchom_polecenie (bc/sesje.py): wątek systemowy w Ogólnym, polecenie systemowe i narzędzia jak dawniej."""
        r = agent.uruchom_polecenie("Zrób notatki.", "Karol", tytul="Sesja — notatki", zestaw="czytanie")
        _, cmd, _, _ = self.czekaj(1)
        self.assertEqual(polecenie_systemowe(cmd), agent.INSTRUKCJA)              # bez reguły i karty okna
        self.assertEqual(cmd[cmd.index("--tools") + 1], "Read,Glob,Grep")
        self.assertEqual(lista_po(cmd, "--disallowedTools"), agent.ZAKAZANE_W_ZESTAWACH)
        self.assertTrue(set(ZAKAZY_PRZED_OKNAMI + ZAKAZY_NOWE) <= set(agent.ZAKAZANE_W_ZESTAWACH))
        self.zakoncz()
        w = agent._czytaj_watek(r["watek"])
        self.assertEqual((w["okno"], w["systemowy"]), ("ogolny", True))
        self.assertEqual(agent.stan_watku(r["watek"]), {"trwa": False, "ostatnia_odpowiedz": None, "blad": None})
        self.assertTrue(agent.mozna_uruchomic(zdalny()))
        r2 = agent.uruchom_polecenie("Jeszcze raz.", "Karol", watek=r["watek"], zestaw="czytanie")
        self.assertEqual(r2["watek"], r["watek"])
        self.czekaj(2)
        self.zakoncz()

    # ------------------------------------------------------------------ usuwanie
    def test_usuwanie_kto_moze(self):
        pawla = self.nowy(zdalny("Paweł"), "balans")["id"]
        karola = self.nowy(lokalny("Karol"), "balans")["id"]
        goscia = self.nowy(zdalny("gość", z_naglowka=False), "balans")["id"]
        lista = {x["id"]: x for x in agent._lista(zdalny("Paweł"))["watki"]}
        self.assertEqual((lista[pawla]["mozna_usunac"], lista[karola]["mozna_usunac"]), (True, False))
        przypadki = [(zdalny("Karol"), pawla, "cudza_rozmowa"),             # inne imię
                     (zdalny("Karol"), karola, "cudza_rozmowa"),            # to samo imię, ale rozmowa z komputera
                     (zdalny("gość", z_naglowka=False), goscia, "cudza_rozmowa"),   # gość bez imienia
                     (zdalny("Paweł", z_naglowka=False), pawla, "cudza_rozmowa")]   # imię nie z Ustawień
        for z, wid, kod in przypadki:
            with self.assertRaises(BladHTTP) as k:
                self.usun(z, wid)
            self.assertEqual((k.exception.status, k.exception.dodatkowe.get("kod")), (403, kod), (z.kto, wid))
        self.assertTrue(os.path.isfile(agent._sciezka_watku(pawla)))
        self.assertEqual(self.usun(zdalny("Paweł"), pawla), {"ok": True, "usuniety": pawla})   # właściciel
        self.assertFalse(os.path.exists(agent._sciezka_watku(pawla)))
        self.assertEqual(self.usun(lokalny("Ktoś"), goscia)["ok"], True)    # osoba przy komputerze: każdą
        with self.assertRaises(BladHTTP) as k:                                 # brak pliku
            self.usun(lokalny(), pawla)
        self.assertEqual(k.exception.status, 404)
        with self.assertRaises(BladHTTP) as k:                                 # zły identyfikator
            self.usun(lokalny(), "../token")
        self.assertEqual(k.exception.status, 400)
        with self.assertRaises(BladHTTP) as k:
            self.usun(lokalny(), karola, systemowe="tak")
        self.assertEqual(k.exception.status, 400)
        self.cfg["agent"]["zdalnie"] = False                                   # agent z telefonu wyłączony
        with self.assertRaises(BladHTTP) as k:
            self.usun(zdalny("Karol"), karola)
        self.assertEqual(k.exception.dodatkowe.get("kod"), "agent_zdalnie_wylaczony")
        self.assertTrue(os.path.isfile(agent._sciezka_watku(karola)))

    def test_usuwanie_w_trakcie_przebiegu(self):
        w = self.nowy(lokalny(), "modele")
        self.napisz(lokalny(), w["id"], "Opisz rycerza.")
        self.czekaj(1)
        with self.assertRaises(BladHTTP) as k:
            self.usun(lokalny(), w["id"])
        self.assertEqual((k.exception.status, k.exception.dodatkowe.get("kod")), (409, "rozmowa_w_toku"))
        self.zakoncz()
        self.assertTrue(self.usun(lokalny(), w["id"])["ok"])
        self.assertNotIn(w["id"], agent._przebiegi)
        self.assertIsNone(agent.stan_watku(w["id"]))

    def test_usuwanie_rozmowy_systemowej(self):
        r = agent.uruchom_polecenie("Notatki.", "Karol", tytul="Sesja — notatki", zestaw="czytanie")
        self.czekaj(1)
        self.zakoncz()
        wid = r["watek"]
        wpis = next(x for x in agent._lista(lokalny())["watki"] if x["id"] == wid)
        self.assertEqual((wpis["systemowy"], wpis["mozna_usunac"]), (True, True))
        wpis = next(x for x in agent._lista(zdalny("Karol"))["watki"] if x["id"] == wid)
        self.assertFalse(wpis["mozna_usunac"])
        with self.assertRaises(BladHTTP) as k:                                 # zdalnie: nigdy, nawet „założyciel”
            self.usun(zdalny("Karol"), wid, systemowe=True)
        self.assertEqual((k.exception.status, k.exception.dodatkowe.get("kod")), (403, "rozmowa_systemowa"))
        with self.assertRaises(BladHTTP) as k:                                 # przy komputerze: z potwierdzeniem
            self.usun(lokalny(), wid)
        self.assertEqual((k.exception.status, k.exception.dodatkowe.get("kod")), (409, "potwierdz_systemowa"))
        self.assertTrue(self.usun(lokalny(), wid, systemowe=True)["ok"])
        self.assertIsNone(agent.stan_watku(wid))                               # bc/sesje.py: „wątku nie ma”
        with self.assertRaises(BladHTTP) as k:                                 # sesje.py zaczyna wtedy nowy wątek
            agent.uruchom_polecenie("Notatki.", "Karol", watek=wid, zestaw="czytanie")
        self.assertEqual(k.exception.status, 404)

    def test_usuwanie_kilku_naraz(self):
        a = self.nowy(lokalny(), "balans")["id"]
        b = self.nowy(lokalny(), "swiat")["id"]
        c = self.nowy(lokalny(), "wydanie")["id"]
        sysw = agent.uruchom_polecenie("Tematy.", "Karol", tytul="Propozycje tematów", zestaw="sejf")["watek"]
        self.czekaj(1)
        self.zakoncz()
        self.napisz(lokalny(), c, "Trwa.")
        self.czekaj(2)
        z = lokalny(dane={"watki": [a, b, a, c, sysw, "w-20990101-000000-0000", "../zly"]})
        r = agent._usun_wiele(z)
        self.assertEqual(r["usuniete"], [a, b])
        pominiete = {p["id"]: (p["status"], p.get("kod")) for p in r["pominiete"]}
        self.assertEqual(pominiete, {c: (409, "rozmowa_w_toku"), sysw: (409, "potwierdz_systemowa"),
                                     "w-20990101-000000-0000": (404, None), "../zly": (400, None)})
        self.assertFalse(r["ok"])
        self.zakoncz()
        r = agent._usun_wiele(lokalny(dane={"watki": [c, sysw], "systemowe": True}))
        self.assertEqual((r["ok"], sorted(r["usuniete"])), (True, sorted([c, sysw])))
        self.assertEqual(os.listdir(agent._kat_watkow()), [])
        for zle in ({}, {"watki": []}, {"watki": "a"}, {"watki": [1]}, {"watki": ["a"] * 101}, {"watki": ["a"], "x": 1}):
            with self.assertRaises(BladHTTP) as k:
                agent._usun_wiele(lokalny(dane=zle))
            self.assertEqual(k.exception.status, 400, zle)


# =========================================================================== prawdziwy serwer z atrapą agenta
@unittest.skipUnless(shutil.which("node"), "brak Node — atrapa agenta działa przez node")
class TestAgentAPIZAtrapa(test_api.SerwerTestowy):
    """Serwer panelu w osobnym procesie; program agenta = atrapa (testy/atrapa_agenta.cjs)."""

    STARY = "w-20261112-090000-abcd"

    @classmethod
    def srodowisko(cls):
        cls.log_atrapy = os.path.join(cls.tmp, "atrapa_log")
        return {"BC_ATRAPA_AGENTA_LOG": cls.log_atrapy}

    @classmethod
    def przygotuj(cls, runtime):
        kat = os.path.join(runtime, "agent", "watki")
        os.makedirs(kat)
        with open(os.path.join(kat, cls.STARY + ".json"), "w", encoding="utf-8") as f:
            json.dump({"id": cls.STARY, "tytul": "Rozmowa sprzed okien", "utworzono": "2026-11-12T09:00:00+01:00",
                       "ostatnio": "2026-11-12T09:00:00+01:00", "session_id": None, "wiadomosci": []}, f)

    def logi(self):
        out = []
        for p in sorted(glob.glob(os.path.join(self.log_atrapy, "*.json"))):
            with open(p, encoding="utf-8") as f:
                out.append(json.load(f))
        return out

    def przebieg(self, wid, tekst, **kw):
        s, r, _ = self.post("/api/agent/watki/%s/wiadomosc" % wid, {"tekst": tekst}, **kw)
        self.assertEqual(s, 202, r)
        s, _, (nagl, b) = self.get("/api/agent/watki/%s/strumien?od=%d" % (wid, r["od"]), bajty=True, timeout=60, **kw)
        zdarzenia = [json.loads(l[6:]) for l in b.decode("utf-8").splitlines() if l.startswith("data: ")]
        self.assertEqual(zdarzenia[-1]["typ"], "koniec", zdarzenia[-3:])
        return zdarzenia

    def test_przebieg_w_oknie_z_atrapa(self):
        s, o, _ = self.get("/api/agent/okna")
        self.assertEqual([x["id"] for x in o["okna"]], ["ogolny", "balans", "swiat", "modele", "wydanie"])
        s, st, _ = self.get("/api/agent/stan")
        self.assertTrue(st["dostepny"])
        self.assertTrue(st["wersja"].startswith("0.0.0-atrapa"), st)             # atrapa, nie prawdziwy program
        self.assertIn("okna", st)
        s, o, _ = self.get("/api/agent/watki")
        stary = next(x for x in o["watki"] if x["id"] == self.STARY)
        self.assertEqual((stary["okno"], stary["systemowy"]), ("ogolny", False))

        s, w, _ = self.post("/api/agent/watki", {"okno": "balans"}, kto="Karol")
        self.assertEqual((s, w["okno"], w["utworzyl"], w["zdalnie"]), (201, "balans", "Karol", False))
        zd = self.przebieg(w["id"], "Policz krzywą kosztów długo", kto="Karol")
        self.assertEqual([z["nazwa"] for z in zd if z["typ"] == "narzedzie"], ["Read", "Grep", "Read"])
        s, wt, _ = self.get("/api/agent/watki/%s" % w["id"])
        self.assertEqual(wt["tytul"], "Policz krzywą kosztów długo")
        role = [m["rola"] for m in wt["wiadomosci"]]
        self.assertEqual(role, ["user", "narzedzie", "narzedzie", "narzedzie", "assistant"])
        self.assertEqual(wt["wiadomosci"][0]["kto"], "Karol")
        self.assertGreater(wt["wiadomosci"][-1]["tekst"].count("\n"), 12)
        wywolanie = self.logi()[-1]
        sp = polecenie_systemowe(wywolanie["argv"])
        self.assertIn("Styl odpowiedzi (stała reguła panelu", sp)
        self.assertIn("Okno agenta w panelu: Balans", sp)
        self.assertIn("Jesteś projektantem balansu", sp)
        self.assertNotIn("Policz krzywą", sp)
        self.assertIn("Policz krzywą kosztów długo", wywolanie["wejscie"])
        self.assertEqual(wywolanie["argv"][wywolanie["argv"].index("--tools") + 1], "Read,Glob,Grep,Edit,Write")

        s, w2, _ = self.post("/api/agent/watki", {"okno": "wydanie"})
        self.przebieg(w2["id"], "Krótko: czy grupa kosztuje?")
        argv = self.logi()[-1]["argv"]
        self.assertIn("WebSearch", argv[argv.index("--tools") + 1])

        # rozmowa w toku: nie da się usunąć; po końcu — tak, z kilkoma naraz
        s, r, _ = self.post("/api/agent/watki/%s/wiadomosc" % w2["id"], {"tekst": "Odpowiedz powoli"})
        self.assertEqual(s, 202, r)
        s, o, _ = self.post("/api/agent/watki/%s/usun" % w2["id"], {})
        self.assertEqual((s, o.get("kod")), (409, "rozmowa_w_toku"), o)
        self.get("/api/agent/watki/%s/strumien?od=%d" % (w2["id"], r["od"]), timeout=60)
        s, o, _ = self.post("/api/agent/usun", {"watki": [w["id"], w2["id"]]})
        self.assertEqual((s, o["usuniete"], o["pominiete"]), (200, [w["id"], w2["id"]], []), o)
        self.assertEqual(self.get("/api/agent/watki/%s" % w["id"])[0], 404)

    def test_dostep_zdalny_i_usuwanie(self):
        s, o, _ = self.post("/api/agent/watki/%s/usun" % self.STARY, {}, zdalny=True)
        self.assertEqual((s, o.get("kod")), (403, "agent_zdalnie_wylaczony"))
        s, o, _ = self.post("/api/konfiguracja/lokalna", {"agent_zdalnie": True})
        self.assertEqual(s, 200, o)
        try:
            s, w, _ = self.post("/api/agent/watki", {"okno": "swiat"}, zdalny=True, kto="Paweł")
            self.assertEqual((s, w["zdalnie"], w["mozna_usunac"]), (201, True, True), w)
            self.przebieg(w["id"], "Jak wygląda golem?", zdalny=True, kto="Paweł")
            s, wk, _ = self.post("/api/agent/watki", {}, kto="Karol")             # rozmowa z komputera
            for kto, wid in ((None, w["id"]), ("Karol", w["id"]), ("Karol", wk["id"])):
                s, o, _ = self.post("/api/agent/watki/%s/usun" % wid, {}, zdalny=True, kto=kto)
                self.assertEqual((s, o.get("kod")), (403, "cudza_rozmowa"), (kto, wid, o))
            s, o, _ = self.get("/api/agent/watki", zdalny=True, kto="Paweł")
            prawa = {x["id"]: x["mozna_usunac"] for x in o["watki"]}
            self.assertEqual((prawa[w["id"]], prawa[wk["id"]], prawa[self.STARY]), (True, False, False))
            s, o, _ = self.post("/api/agent/watki/%s/tytul" % w["id"], {"tytul": "Golem z jaskini"}, zdalny=True,
                                kto="Paweł")
            self.assertEqual((s, o["tytul"]), (200, "Golem z jaskini"), o)
            s, o, _ = self.post("/api/agent/watki/%s/usun" % w["id"], {}, zdalny=True, kto="Paweł")
            self.assertEqual((s, o), (200, {"ok": True, "usuniety": w["id"]}))
            s, o, _ = self.post("/api/agent/watki/%s/usun" % wk["id"], {})       # przy komputerze: każdą
            self.assertEqual(s, 200, o)
            argv = self.logi()[-1]["argv"]
            self.assertIn("Okno agenta w panelu: Świat", polecenie_systemowe(argv))
            self.assertIn("[Panel zespołu · pisze: Paweł]", self.logi()[-1]["wejscie"])
        finally:
            self.post("/api/konfiguracja/lokalna", {"agent_zdalnie": False})


if __name__ == "__main__":
    unittest.main()
