# -*- coding: utf-8 -*-
"""Testy poleceń panelu dla agenta (bc/agent.py: uruchom_polecenie, stan_watku, zbuduj_polecenie z zestawem narzędzi).

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_agent

Agent (claude) nigdy nie jest uruchamiany: znajdz_program zwraca udawaną ścieżkę, a _bezpiecznie (wątek, który
uruchomiłby proces) jest podmieniony atrapą, która tylko zapamiętuje wiersz poleceń i kończy przebieg na sygnał testu.
"""
import os
import shutil
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import agent, rdzen  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402


class TestPoleceniaPanelu(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_agent_")
        self.cfg = {"agent": {"limit_czasu_min": 5}}
        self.przebiegi = []                                    # (przebieg, cmd, wejście, zdarzenie „zakończ”)

        def udawany(p, cmd, wejscie, limit_min):
            koniec = threading.Event()
            self.przebiegi.append((p, cmd, wejscie, koniec))
            koniec.wait(10)
            if not p.zakonczony:
                p.zdarzenie("koniec")

        self.latki = [
            mock.patch.object(rdzen, "RUNTIME", self.tmp),
            mock.patch.object(rdzen, "konfiguracja", lambda: self.cfg),
            mock.patch.object(rdzen, "log", lambda *a: None),
            mock.patch.object(agent, "znajdz_program", lambda: "claude"),
            mock.patch.object(agent, "_bezpiecznie", udawany),
        ]
        for l in self.latki:
            l.start()
        agent._przebiegi.clear()
        agent._licznik_n.clear()
        self.kat_sesji = os.path.join(self.tmp, "sesje", "20261113-201500-ab12")
        os.makedirs(self.kat_sesji)

    def tearDown(self):
        for p, _, _, koniec in self.przebiegi:
            koniec.set()
        for t in [t for t in threading.enumerate() if t.name.startswith("agent-")]:
            t.join(5)
        agent._przebiegi.clear()
        agent._licznik_n.clear()
        for l in reversed(self.latki):
            l.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def zakoncz(self, i=-1):
        p, _, _, koniec = self.przebiegi[i]
        koniec.set()
        for t in [t for t in threading.enumerate() if t.name == "agent-" + p.wid]:
            t.join(5)
        self.assertTrue(p.zakonczony)

    def czekaj_na_przebieg(self, ile):
        for _ in range(200):
            if len(self.przebiegi) >= ile:
                return
            threading.Event().wait(0.01)
        self.fail("Przebieg agenta nie wystartował")

    def test_nowy_watek_z_katalogami_i_zestawem(self):
        r = agent.uruchom_polecenie("Zrób notatki.", "Karol", tytul="Sesja — notatki", katalogi=[self.kat_sesji,
                                    self.tmp], zestaw="czytanie")
        self.assertEqual((r["tryb"], r["nr"]), ("praca", 1))
        self.czekaj_na_przebieg(1)
        w = agent._czytaj_watek(r["watek"])
        self.assertEqual(w["tytul"], "Sesja — notatki")
        self.assertEqual(w["katalogi"], [os.path.realpath(self.kat_sesji)])    # tylko katalog sesji
        self.assertEqual(w["wiadomosci"][0]["tekst"], "Zrób notatki.")
        _, cmd, wejscie, _ = self.przebiegi[0]
        self.assertEqual(cmd[cmd.index("--add-dir") + 1], os.path.realpath(self.kat_sesji))
        self.assertIn("Zrób notatki.", wejscie)
        self.assertIn("[Panel zespołu · pisze: Karol]", wejscie)
        self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "dontAsk")
        self.assertEqual(cmd[cmd.index("--tools") + 1], "Read,Glob,Grep")
        self.assertIn("--strict-mcp-config", cmd)
        self.assertNotIn("--mcp-config", cmd)
        self.assertTrue(agent.stan_watku(r["watek"])["trwa"])
        self.zakoncz()
        self.assertFalse(agent.stan_watku(r["watek"])["trwa"])

    def test_kto_zalozyl_watek_i_czy_zdalnie(self):
        """Lista wątków pokazuje, kto założył wątek i czy zdalnie, oraz kto w nim pisał (subskrypcja jest jedna —
        osoby przy komputerze z panelem)."""
        class Z:
            def __init__(self, kto, lokalny, dane=None, wid=None):
                self.kto, self.lokalny, self.json, self.params = kto, lokalny, dane, {"id": wid}
        self.cfg["agent"]["zdalnie"] = True
        s, w = agent._nowy(Z("Paweł", False, {"tytul": "Pytanie o walutę"}))
        self.assertEqual((s, w["utworzyl"], w["zdalnie"]), (201, "Paweł", True))
        r = agent._wiadomosc(Z("Paweł", False, {"tekst": "Jaką walutę premium?"}, w["id"]))
        self.assertEqual(r[0], 202)
        self.czekaj_na_przebieg(1)
        self.zakoncz()
        agent._dopisz(w["id"], {"rola": "user", "tekst": "Dopisuję", "kto": "Karol", "zdalnie": False})
        lista = {x["id"]: x for x in agent._lista(Z("Karol", True))["watki"]}
        x = lista[w["id"]]
        self.assertEqual((x["utworzyl"], x["zdalnie"]), ("Paweł", True))
        self.assertEqual(x["osoby"], [{"kto": "Paweł", "zdalnie": True}, {"kto": "Karol", "zdalnie": False}])
        self.assertTrue(agent._czytaj_watek(w["id"])["wiadomosci"][0]["zdalnie"])
        s, w2 = agent._nowy(Z("Karol", True, {}))                  # przy komputerze
        self.assertEqual((w2["utworzyl"], w2["zdalnie"]), ("Karol", False))
        # polecenie panelu bez informacji o miejscu i stary wątek bez pola: „nie wiadomo” (null), nie „przy komputerze”
        r3 = agent.uruchom_polecenie("Notatki.", "Karol", tytul="Sesja")
        self.czekaj_na_przebieg(2)
        self.zakoncz()
        stary = agent._czytaj_watek(r3["watek"])
        self.assertIsNone(agent._widok_watku(stary)["zdalnie"])
        self.assertEqual(agent._widok_watku(stary)["osoby"], [{"kto": "Karol", "zdalnie": None}])

    def test_wznowienie_istniejacego_watku(self):
        r = agent.uruchom_polecenie("Pierwsze.", "Karol", tytul="T", katalogi=[self.kat_sesji])
        self.czekaj_na_przebieg(1)
        self.zakoncz()
        agent._dopisz(r["watek"], {"rola": "assistant", "tekst": "Zrobione."}, session_id="sesja-claude-1")
        r2 = agent.uruchom_polecenie("Drugie.", "Paweł", watek=r["watek"])
        self.assertEqual((r2["watek"], r2["nr"]), (r["watek"], 3))
        self.czekaj_na_przebieg(2)
        _, cmd, _, _ = self.przebiegi[1]
        self.assertEqual(cmd[cmd.index("--resume") + 1], "sesja-claude-1")
        self.assertEqual(cmd[cmd.index("--add-dir") + 1], os.path.realpath(self.kat_sesji))   # zapamiętane
        self.assertEqual(cmd[cmd.index("--permission-mode") + 1], "acceptEdits")             # bez zestawu
        self.zakoncz()

    def test_409_gdy_watek_pracuje_i_przy_limicie(self):
        r = agent.uruchom_polecenie("Jedno.", "Karol")
        self.czekaj_na_przebieg(1)
        with self.assertRaises(BladHTTP) as k:
            agent.uruchom_polecenie("Drugie w tym samym wątku.", "Karol", watek=r["watek"])
        self.assertEqual(k.exception.status, 409)
        przed = sorted(os.listdir(agent._kat_watkow()))
        with mock.patch.object(agent, "MAX_PRZEBIEGOW", 1):
            with self.assertRaises(BladHTTP) as k:
                agent.uruchom_polecenie("Nowy wątek ponad limit.", "Karol")
            self.assertEqual(k.exception.status, 409)
        self.assertEqual(sorted(os.listdir(agent._kat_watkow())), przed)       # bez pustego wątku-sieroty
        self.zakoncz()

    def test_bledne_argumenty_i_brak_programu(self):
        for kw in ({"tryb": "auto"}, {"zestaw": "wszystko"}):
            with self.assertRaises(BladHTTP) as k:
                agent.uruchom_polecenie("x", "Karol", **kw)
            self.assertEqual(k.exception.status, 400)
        with self.assertRaises(BladHTTP) as k:
            agent.uruchom_polecenie("   ", "Karol")
        self.assertEqual(k.exception.status, 400)
        with self.assertRaises(BladHTTP) as k:
            agent.uruchom_polecenie("x", "Karol", watek="nie-ma-takiego")
        self.assertEqual(k.exception.status, 404)
        with mock.patch.object(agent, "znajdz_program", lambda: None):
            with self.assertRaises(BladHTTP) as k:
                agent.uruchom_polecenie("x", "Karol")
            self.assertEqual(k.exception.status, 503)
        self.assertEqual(self.przebiegi, [])

    def test_stan_watku(self):
        self.assertIsNone(agent.stan_watku("nie-ma-takiego"))
        self.assertIsNone(agent.stan_watku("../zly"))
        r = agent.uruchom_polecenie("Polecenie.", "Karol")
        self.czekaj_na_przebieg(1)
        self.zakoncz()
        wid = r["watek"]
        self.assertEqual(agent.stan_watku(wid), {"trwa": False, "ostatnia_odpowiedz": None, "blad": None})
        agent._dopisz(wid, {"rola": "assistant", "tekst": "## Notatki"})
        self.assertEqual(agent.stan_watku(wid)["ostatnia_odpowiedz"], "## Notatki")
        # błąd systemowy po nowym poleceniu: odpowiedź z poprzedniego polecenia się nie liczy
        agent._dopisz(wid, {"rola": "user", "tekst": "Jeszcze raz."})
        agent._dopisz(wid, {"rola": "system", "tekst": "Wyczerpany limit subskrypcji Claude.\n\nszczegóły"})
        st = agent.stan_watku(wid)
        self.assertIsNone(st["ostatnia_odpowiedz"])
        self.assertTrue(st["blad"].startswith("Wyczerpany limit"))

    def test_zestawy_narzedzi_w_wierszu_polecen(self):
        for zestaw, narzedzia in agent.ZESTAWY_NARZEDZI.items():
            cmd = agent.zbuduj_polecenie("claude", "praca", zestaw=zestaw)
            dozwolone = cmd[cmd.index("--allowedTools") + 1:cmd.index("--disallowedTools")]
            self.assertEqual(dozwolone, narzedzia)
            zakazane = cmd[cmd.index("--disallowedTools") + 1:]
            self.assertIn("Read(./.env)", zakazane)
            wbudowane = cmd[cmd.index("--tools") + 1].split(",")
            for nazwa in ("WebFetch", "WebSearch", "mcp__Roblox_Studio"):
                self.assertNotIn(nazwa, wbudowane)
                self.assertNotIn(nazwa, dozwolone)
            self.assertFalse(any(n.startswith("Bash(python tools/") for n in dozwolone))
        self.assertEqual(agent.zbuduj_polecenie("claude", "praca", zestaw="ustalenia")[
            agent.zbuduj_polecenie("claude", "praca", zestaw="ustalenia").index("--tools") + 1],
            "Read,Glob,Grep,Edit,Write,Bash")
        zwykly = agent.zbuduj_polecenie("claude", "praca")                     # bez zestawu: jak dotąd
        self.assertEqual(zwykly[zwykly.index("--permission-mode") + 1], "acceptEdits")
        self.assertNotIn("--tools", zwykly)
        self.assertNotIn("--disallowedTools", zwykly)


if __name__ == "__main__":
    unittest.main()
