# -*- coding: utf-8 -*-
"""Stała synchronizacja z GitHubem (bc/gitsync.py, decyzja D-070) — wyłącznie na repozytoriach próbnych.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_gitsync_auto

Każdy test buduje w katalogu tymczasowym: repozytorium bare (jak GitHub) + klon „karol” (komputer z panelem) + klon
„pawel” (druga osoba). Funkcje dostają jawnie repo= z katalogu tymczasowego; prawdziwe repozytorium chroni bezpiecznik
`gitsync._pilnuj` (sprawdzany tu też osobno), a GitHub i prawdziwy Telegram nie są nigdy używane (Telegram = atrapa).
Globalna konfiguracja gita użytkownika jest odcięta (GIT_CONFIG_GLOBAL = pusty plik), żeby np. autocrlf czy
pull.rebase z tego komputera nie zmieniały wyniku.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import gitsync, rdzen, telegram  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402
from testy.atrapa_telegrama import AtrapaTelegrama  # noqa: E402

SC = ["panel/dane"]
TOKEN = "123456:TEST-zmyslony-token-atrapy-sync"
GRUPA = -1009
USTAW = {"co_s": 90.0, "wyslij_po_s": 60.0, "telegram": False, "auto": True}


def _srodowisko_gita(tmp):
    pusty = os.path.join(tmp, "pusty.gitconfig")
    if not os.path.exists(pusty):
        open(pusty, "w").close()
    return {"GIT_CONFIG_GLOBAL": pusty, "GIT_CONFIG_NOSYSTEM": "1"}


class Baza(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_gitauto_")
        self.env = mock.patch.dict(os.environ, _srodowisko_gita(self.tmp))
        self.env.start()
        self.logi = []
        self.log = mock.patch.object(rdzen, "log", lambda *a: self.logi.append(" ".join(str(x) for x in a)))
        self.log.start()
        self.zdalne = os.path.join(self.tmp, "zdalne.git")
        self.g(["init", "-q", "--bare", "-b", "main", self.zdalne], self.tmp)
        self.karol = self.klon("karol", "Karol")
        self.pisz(self.karol, "README.md", "repo próbne\n")
        self.pisz(self.karol, "a.txt", "wiersz 1\nwiersz 2\nwiersz 3\n")
        self.pisz(self.karol, ".gitignore", "*.log\n")
        self.pisz(self.karol, "panel/dane/.keep", "")
        self.g(["add", "-A"], self.karol)
        self.g(["commit", "-q", "-m", "start"], self.karol)
        self.g(["push", "-q", "-u", "origin", "main"], self.karol)
        self.pawel = self.klon("pawel", "Paweł")
        gitsync._auto.clear()

    def tearDown(self):
        gitsync._auto.clear()
        self.log.stop()
        self.env.stop()

        def zdejmij(fn, sciezka, _):
            os.chmod(sciezka, 0o700)
            fn(sciezka)
        for _ in range(10):
            try:
                shutil.rmtree(self.tmp, onerror=zdejmij)
                break
            except OSError:
                time.sleep(0.3)

    # ------------------------------------------------------------------ narzędzia
    def g(self, args, cwd):
        r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           env=dict(os.environ, GIT_TERMINAL_PROMPT="0"), creationflags=rdzen.CREATE_NO_WINDOW)
        if r.returncode != 0:
            raise RuntimeError("git %s: %s %s" % (" ".join(args), r.stdout, r.stderr))
        return r.stdout

    def klon(self, nazwa, osoba):
        cel = os.path.join(self.tmp, nazwa)
        self.g(["clone", "-q", "-c", "core.autocrlf=false", self.zdalne, cel], self.tmp)
        self.g(["config", "user.name", osoba], cel)
        self.g(["config", "user.email", "%s@example.invalid" % nazwa], cel)
        self.g(["config", "core.autocrlf", "false"], cel)
        try:
            self.g(["checkout", "-q", "-B", "main", "--track", "origin/main"], cel)
        except RuntimeError:                                   # pusty bare: pierwszy klon zakłada gałąź
            self.g(["checkout", "-q", "-B", "main"], cel)
        return cel

    def pisz(self, repo, rel, tekst, tryb="w"):
        p = os.path.join(repo, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, tryb, encoding=None if "b" in tryb else "utf-8", newline=None if "b" in tryb else "") as f:
            f.write(tekst)
        return p

    def czytaj(self, repo, rel):
        with open(os.path.join(repo, *rel.split("/")), "rb") as f:
            return f.read()

    def commit_pawla(self, rel, tekst, temat):
        self.g(["pull", "-q", "--no-rebase"], self.pawel)
        self.pisz(self.pawel, rel, tekst)
        self.g(["add", "-A"], self.pawel)
        self.g(["commit", "-q", "-m", temat], self.pawel)
        self.g(["push", "-q"], self.pawel)

    def head(self, repo, ref="HEAD"):
        return self.g(["rev-parse", ref], repo).strip()

    def odcisk(self, repo, pliki):
        """Bajty i czas zmiany plików — do sprawdzenia „nietknięte co do bajta”."""
        wynik = {}
        for rel in pliki:
            p = os.path.join(repo, *rel.split("/"))
            s = os.stat(p)
            wynik[rel] = (self.czytaj(repo, rel), s.st_mtime_ns, s.st_size)
        return wynik

    def obieg(self, repo=None, teraz=None, **ustaw):
        return gitsync.obieg(repo or self.karol, SC, dict(USTAW, **ustaw), teraz)

    def git_z_zapisem(self, zmien=None):
        """Łatka na gitsync.git: zapisuje polecenia; `zmien(argumenty)` może podać własny wynik (kod, out, err)."""
        prawdziwy = gitsync.git
        polecenia = []

        def git(argumenty, repo=None, timeout=30):
            polecenia.append(list(argumenty))
            if zmien:
                w = zmien(list(argumenty), repo)
                if w is not None:
                    return w
            return prawdziwy(argumenty, repo, timeout)
        return mock.patch.object(gitsync, "git", git), polecenia


# =========================================================================== S2: samo pobieranie
class TestSamoPobieranie(Baza):
    def test_przewiniecie_i_praca_w_toku_nietknieta(self):
        # na komputerze z panelem: zmieniony śledzony plik, nowy plik, plik ignorowany, plik binarny — inne niż u Pawła
        self.pisz(self.karol, "README.md", "repo próbne — lokalna praca w toku\r\n")
        self.pisz(self.karol, "notatki/szkic.md", "szkic agenta\n")
        self.pisz(self.karol, "blender.log", "log ignorowany\n")
        self.pisz(self.karol, "modele/troll.blend", bytes(range(256)) * 50, "wb")
        przed = self.odcisk(self.karol, ["README.md", "notatki/szkic.md", "blender.log", "modele/troll.blend"])
        status_przed = self.g(["status", "--porcelain", "-uall"], self.karol)
        self.commit_pawla("a.txt", "wiersz 1 od Pawła\nwiersz 2\nwiersz 3\n", "Paweł: poprawka a.txt")

        a = self.obieg()
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(self.head(self.karol), self.head(self.pawel))             # przewinięcie, bez scalenia
        self.assertEqual(self.czytaj(self.karol, "a.txt"), "wiersz 1 od Pawła\nwiersz 2\nwiersz 3\n".encode("utf-8"))
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)               # co do bajta i czasu zmiany
        self.assertEqual(self.g(["status", "--porcelain", "-uall"], self.karol), status_przed)
        self.assertEqual(self.g(["stash", "list"], self.karol), "")                # żadnego autostash
        p = a["pobranie"]
        self.assertEqual((p["ile"], p["autorzy"]), (1, ["Paweł"]))
        self.assertEqual(p["commity"][0]["temat"], "Paweł: poprawka a.txt")
        self.assertTrue(a["zgodne"])

    def test_scalenie_przy_wlasnych_commitach(self):
        self.pisz(self.karol, "c.txt", "commit Karola\n")
        self.g(["add", "c.txt"], self.karol)
        self.g(["commit", "-q", "-m", "Karol: c.txt"], self.karol)
        self.pisz(self.karol, "szkic.txt", "nieśledzony szkic\n")
        przed = self.odcisk(self.karol, ["szkic.txt"])
        self.commit_pawla("b.txt", "plik Pawła\n", "Paweł: b.txt")

        a = self.obieg()                                       # commit Karola świeży — scalenie tak, wysłanie jeszcze nie
        rodzice = self.g(["log", "-1", "--format=%P"], self.karol).split()
        self.assertEqual(len(rodzice), 2, "oczekiwano commita scalającego")
        self.assertEqual(self.g(["log", "-1", "--format=%s"], self.karol).strip(), "panel: scalenie zmian z GitHuba")
        self.assertTrue(os.path.isfile(os.path.join(self.karol, "b.txt")))
        self.assertEqual(self.odcisk(self.karol, ["szkic.txt"]), przed)
        self.assertEqual(a["stan"], "ok")
        self.assertNotEqual(self.head(self.karol), self.g(["rev-parse", "main"], self.zdalne).strip())

        a = self.obieg(teraz=time.time() + 120)                # po minucie spokoju lokalne commity idą na GitHuba
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(self.head(self.karol), self.g(["rev-parse", "main"], self.zdalne).strip())
        self.assertTrue(a["wyslanie"])

    def test_lokalna_zmiana_w_pliku_drugiej_osoby_czeka(self):
        self.pisz(self.karol, "a.txt", "wiersz 1\nwiersz 2 — Karol pisze\nwiersz 3\n")
        przed = self.odcisk(self.karol, ["a.txt"])
        head = self.head(self.karol)
        self.commit_pawla("a.txt", "wiersz 1\nwiersz 2\nwiersz 3\nwiersz 4 Pawła\n", "Paweł: a.txt")

        a = self.obieg()
        self.assertEqual(a["stan"], "czeka", a)
        self.assertEqual(a["pliki"], ["a.txt"])
        self.assertEqual(a["krotko"], "lokalne zmiany w 1 pliku")
        self.assertTrue(a["co_zrobic"])
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.odcisk(self.karol, ["a.txt"]), przed)
        self.assertFalse(os.path.exists(os.path.join(self.karol, ".git", "MERGE_HEAD")))
        self.assertEqual(self.obieg()["stan"], "czeka")         # następny obieg: dalej czeka, nic nie ruszone
        self.assertEqual(self.odcisk(self.karol, ["a.txt"]), przed)

        self.pisz(self.karol, "a.txt", "wiersz 1\nwiersz 2\nwiersz 3\n")    # człowiek skończył (wrócił do wersji z HEAD)
        a = self.obieg()
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(self.head(self.karol), self.head(self.pawel))

    def test_nowy_plik_drugiej_osoby_a_lokalny_nieśledzony_i_ignorowany(self):
        self.pisz(self.karol, "nowy.txt", "mój nieśledzony\n")
        self.pisz(self.karol, "wynik.log", "mój ignorowany\n")
        przed = self.odcisk(self.karol, ["nowy.txt", "wynik.log"])
        self.g(["pull", "-q", "--no-rebase"], self.pawel)
        self.pisz(self.pawel, "nowy.txt", "Pawła\n")
        self.pisz(self.pawel, "wynik.log", "Pawła log\n")
        self.g(["add", "-f", "nowy.txt", "wynik.log"], self.pawel)
        self.g(["commit", "-q", "-m", "Paweł: nowe pliki"], self.pawel)
        self.g(["push", "-q"], self.pawel)

        a = self.obieg()
        self.assertEqual(a["stan"], "czeka", a)
        self.assertEqual(sorted(a["pliki"]), ["nowy.txt", "wynik.log"])          # także plik ignorowany
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)

    def test_prawdziwy_konflikt_bez_ponawiania(self):
        self.pisz(self.karol, "a.txt", "wiersz 1\nwiersz 2 KAROL\nwiersz 3\n")
        self.g(["commit", "-q", "-am", "Karol: a.txt"], self.karol)
        self.pisz(self.karol, "szkic.txt", "praca w toku\n")
        przed = self.odcisk(self.karol, ["szkic.txt", "a.txt"])
        status_przed = self.g(["status", "--porcelain", "-uall"], self.karol)
        head = self.head(self.karol)
        self.commit_pawla("a.txt", "wiersz 1\nwiersz 2 PAWEŁ\nwiersz 3\n", "Paweł: a.txt")

        a = self.obieg()
        self.assertEqual(a["stan"], "konflikt", a)
        self.assertIn("a.txt", a["pliki"])
        self.assertEqual(a["krotko"], "potrzebny człowiek")
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)
        self.assertEqual(self.g(["status", "--porcelain", "-uall"], self.karol), status_przed)
        self.assertFalse(os.path.exists(os.path.join(self.karol, ".git", "MERGE_HEAD")))

        latka, polecenia = self.git_z_zapisem()
        with latka:
            a = self.obieg()                                    # ten sam konflikt — bez nowej próby scalenia
        self.assertEqual(a["stan"], "konflikt")
        self.assertFalse([p for p in polecenia if p[0] in ("merge", "merge-tree")], polecenia)

        self.commit_pawla("d.txt", "jeszcze coś\n", "Paweł: d.txt")              # zmienił się commit na GitHubie
        latka, polecenia = self.git_z_zapisem()
        with latka:
            a = self.obieg()
        self.assertTrue([p for p in polecenia if p[0] == "merge-tree"], polecenia)
        self.assertEqual(a["stan"], "konflikt")

    def test_dziwny_wynik_proby_na_sucho_blad_bez_ruszania(self):
        """Gdy `git merge-tree` da nieoczekiwany wynik, panel nie scala niczego (stan „błąd”, katalog nietknięty)."""
        self.pisz(self.karol, "c.txt", "Karol\n")
        self.g(["add", "c.txt"], self.karol)
        self.g(["commit", "-q", "-m", "Karol: c.txt"], self.karol)
        self.pisz(self.karol, "szkic.txt", "praca w toku\n")
        przed = self.odcisk(self.karol, ["szkic.txt", "c.txt"])
        status_przed = self.g(["status", "--porcelain", "-uall"], self.karol)
        head = self.head(self.karol)
        self.commit_pawla("b.txt", "Paweł\n", "Paweł: b.txt")

        def na_sucho_dziwnie(argumenty, repo):
            if argumenty[0] == "merge-tree":
                return 0, "to nie jest drzewo\n", ""
            return None
        latka, polecenia = self.git_z_zapisem(na_sucho_dziwnie)
        with latka:
            a = self.obieg()
        self.assertEqual(a["stan"], "blad", a)
        self.assertFalse([p for p in polecenia if p[0] in ("merge", "commit-tree")], polecenia)
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)
        self.assertEqual(self.g(["status", "--porcelain", "-uall"], self.karol), status_przed)

    def test_index_lock_pomija_obieg(self):
        self.commit_pawla("b.txt", "Pawła\n", "Paweł: b.txt")
        head = self.head(self.karol)
        blokada = os.path.join(self.karol, ".git", "index.lock")
        open(blokada, "w").close()
        latka, polecenia = self.git_z_zapisem()
        with latka:
            a = self.obieg()
        self.assertFalse([p for p in polecenia if p[0] in ("fetch", "merge", "commit", "push", "add")], polecenia)
        self.assertEqual(self.head(self.karol), head)
        self.assertNotEqual(a["stan"], "konflikt")
        os.remove(blokada)
        self.assertEqual(self.obieg()["stan"], "ok")
        self.assertEqual(self.head(self.karol), self.head(self.pawel))

    def test_cudze_scalanie_w_toku_czeka(self):
        self.pisz(self.karol, "a.txt", "wiersz 1\nKAROL\nwiersz 3\n")
        self.g(["commit", "-q", "-am", "Karol"], self.karol)
        self.commit_pawla("a.txt", "wiersz 1\nPAWEŁ\nwiersz 3\n", "Paweł")
        self.g(["fetch", "-q"], self.karol)
        subprocess.run(["git", "merge", "origin/main"], cwd=self.karol, capture_output=True)   # człowiek w terminalu
        self.assertTrue(os.path.exists(os.path.join(self.karol, ".git", "MERGE_HEAD")))
        przed = self.czytaj(self.karol, "a.txt")
        latka, polecenia = self.git_z_zapisem()
        with latka:
            a = self.obieg()
        self.assertEqual(a["stan"], "czeka")
        self.assertEqual(a["krotko"], "trwa scalanie w repozytorium")
        self.assertFalse([p for p in polecenia if p[0] in ("fetch", "merge", "commit", "push", "add")], polecenia)
        self.assertEqual(self.czytaj(self.karol, "a.txt"), przed)                 # znaczniki konfliktu człowieka zostają
        self.assertTrue(os.path.exists(os.path.join(self.karol, ".git", "MERGE_HEAD")))

    def test_reczne_pobierz_ta_sama_bezpieczna_droga(self):
        self.pisz(self.karol, "a.txt", "lokalnie\n")
        self.commit_pawla("a.txt", "Paweł\n", "Paweł: a.txt")
        with self.assertRaises(BladHTTP) as ctx:
            gitsync.pobierz(self.karol, bezpiecznie=True)
        self.assertEqual(ctx.exception.status, 409)
        self.assertIn("Nie pobrano", ctx.exception.komunikat)
        self.assertEqual(self.czytaj(self.karol, "a.txt"), b"lokalnie\n")
        self.assertEqual(self.g(["stash", "list"], self.karol), "")
        self.pisz(self.karol, "a.txt", "wiersz 1\nwiersz 2\nwiersz 3\n")
        w = gitsync.pobierz(self.karol, bezpiecznie=True)
        self.assertTrue(w["ok"], w)
        self.assertEqual(self.head(self.karol), self.head(self.pawel))


# =========================================================================== praca w toku pod scaleniem (po przeglądzie)
class TestPracaWToku(Baza):
    """Przegląd 14.11: zwykły `git merge` przy odmowie robił w środku reset --hard + stash apply i gubił pliki dodane
    `git add` i niezacommitowane zmiany. Teraz katalog roboczy rusza tylko `merge --ff-only`."""

    N = 300

    def przygotuj_wiele(self):
        """300 śledzonych plików we własnym (niewysłanym) commicie, potem wszystkie zmienione bez commita."""
        pliki = ["praca/p%03d.txt" % i for i in range(self.N)]
        for p in pliki:
            self.pisz(self.karol, p, "wersja z commita %s\n" % p)
        self.g(["add", "praca"], self.karol)
        self.g(["commit", "-q", "-m", "Karol: 300 plików"], self.karol)
        for p in pliki:
            self.pisz(self.karol, p, "praca w toku %s\r\n" % p)
        return pliki

    def piszacy_watek(self, rel):
        """Wątek, który co ~2 ms zapisuje `rel` (jak agent albo Blender w tle). Zwraca (stop, ostatnia_tresc)."""
        import threading
        stop = threading.Event()
        ostatnia = {"t": None}

        def pisz():
            n = 0
            while not stop.is_set():
                n += 1
                t = "zapis w tle %d\n" % n
                try:
                    self.pisz(self.karol, rel, t)
                    ostatnia["t"] = t.encode("utf-8")
                except OSError:                                # Windows: plik chwilowo zajęty przez gita
                    pass
                time.sleep(0.002)
        w = threading.Thread(target=pisz, daemon=True)
        w.start()
        return stop, w, ostatnia

    def indeks(self, repo):
        return self.g(["ls-files", "-s"], repo)

    def test_plik_po_add_czeka_i_nic_nie_ruszone(self):
        pliki = self.przygotuj_wiele()
        self.pisz(self.karol, "agent.lua", "print('agent')\n")
        self.g(["add", "agent.lua"], self.karol)
        self.commit_pawla("b.txt", "Paweł\n", "Paweł: b.txt")
        przed = self.odcisk(self.karol, pliki + ["agent.lua"])
        indeks_przed = self.indeks(self.karol)
        head = self.head(self.karol)
        stop, w, ostatnia = self.piszacy_watek("README.md")
        try:
            latka, polecenia = self.git_z_zapisem()
            with latka:
                a = self.obieg()
        finally:
            stop.set()
            w.join(5)
        self.assertEqual(a["stan"], "czeka", a)
        self.assertTrue(a["krotko"].startswith("pliki dodane do commita"), a)
        self.assertEqual(a["pliki"], ["agent.lua"])
        self.assertIn("dokończ", a["krotko"])
        self.assertFalse([p for p in polecenia if p[0] in ("merge", "commit-tree", "stash", "reset", "checkout")],
                         polecenia)
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)              # bajty i czas zmiany
        self.assertEqual(self.indeks(self.karol), indeks_przed)
        self.assertEqual(self.czytaj(self.karol, "README.md"), ostatnia["t"])
        self.assertEqual(self.g(["stash", "list"], self.karol), "")

        self.g(["commit", "-q", "-m", "agent: agent.lua"], self.karol)           # agent dokończył commit
        a = self.obieg()
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(len(self.g(["log", "-1", "--format=%P"], self.karol).split()), 2)

    def test_scalenie_bez_zwyklego_merge_i_praca_w_toku_co_do_bajta(self):
        pliki = self.przygotuj_wiele()
        self.pisz(self.karol, "notatki/nowy.md", "nieśledzony\n")
        self.pisz(self.karol, "README.md", "zapis w tle 0\n")                    # README zmieniony już przed obiegiem
        self.commit_pawla("b.txt", "Paweł\n", "Paweł: b.txt")
        przed = self.odcisk(self.karol, pliki + ["notatki/nowy.md"])
        status_przed = self.g(["status", "--porcelain", "-uall"], self.karol)
        head = self.head(self.karol)
        stop, w, ostatnia = self.piszacy_watek("README.md")
        try:
            latka, polecenia = self.git_z_zapisem()
            with latka:
                a = self.obieg()
        finally:
            stop.set()
            w.join(5)
        self.assertEqual(a["stan"], "ok", a)
        merge = [p for p in polecenia if p[0] == "merge"]
        self.assertTrue(merge)
        for p in merge:                                        # nigdy zwykłe scalenie w katalogu roboczym
            self.assertIn("--ff-only", p)
            self.assertIn("--no-autostash", p)
            self.assertIn("--no-overwrite-ignore", p)
        self.assertTrue([p for p in polecenia if p[0] == "commit-tree"])
        rodzice = self.g(["log", "-1", "--format=%P"], self.karol).split()
        self.assertEqual(rodzice, [head, self.g(["rev-parse", "main"], self.zdalne).strip()])
        self.assertEqual(self.g(["log", "-1", "--format=%s"], self.karol).strip(), gitsync.OPIS_SCALENIA)
        self.assertEqual(self.czytaj(self.karol, "b.txt"), b"Pawe\xc5\x82\n")
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)
        self.assertEqual(self.czytaj(self.karol, "README.md"), ostatnia["t"])
        self.assertEqual(self.g(["status", "--porcelain", "-uall"], self.karol), status_przed)
        self.assertEqual(self.g(["stash", "list"], self.karol), "")

    def test_przewiniecie_zachowuje_indeks(self):
        """Nawet gdyby sprawdzenie indeksu nie zadziałało: przewinięcie zostawia plik po `git add` w indeksie
        i na dysku (scalenie przy własnych commitach idzie tą samą drogą)."""
        pliki = self.przygotuj_wiele()
        self.pisz(self.karol, "agent.lua", "print('agent')\n")
        self.g(["add", "agent.lua"], self.karol)
        self.commit_pawla("b.txt", "Paweł\n", "Paweł: b.txt")
        przed = self.odcisk(self.karol, pliki + ["agent.lua"])
        stop, w, _ = self.piszacy_watek("README.md")
        try:
            with mock.patch.object(gitsync, "_dodane_do_indeksu", lambda repo: []):
                a = self.obieg()
        finally:
            stop.set()
            w.join(5)
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(self.odcisk(self.karol, list(przed)), przed)
        self.assertEqual(self.g(["diff", "--cached", "--name-only"], self.karol).split(), ["agent.lua"])
        self.assertEqual(len(self.g(["log", "-1", "--format=%P"], self.karol).split()), 2)

    def test_zmiana_w_oknie_miedzy_proba_a_scaleniem(self):
        """Ktoś zapisuje nadchodzący plik między próbą na sucho a przewinięciem: git odmawia czysto → „czeka”,
        z listą plików (komunikat gita z wcięciem), lokalny plik nietknięty."""
        self.pisz(self.karol, "c.txt", "Karol\n")
        self.g(["add", "c.txt"], self.karol)
        self.g(["commit", "-q", "-m", "Karol: c.txt"], self.karol)
        self.g(["pull", "-q", "--no-rebase"], self.pawel)
        self.pisz(self.pawel, "a.txt", "Paweł zmienia a.txt\n")
        self.pisz(self.pawel, "nowy.txt", "Paweł dodaje\n")
        self.g(["add", "-A"], self.pawel)
        self.g(["commit", "-q", "-m", "Paweł: a i nowy"], self.pawel)
        self.g(["push", "-q"], self.pawel)
        head = self.head(self.karol)
        test = self

        def wtrac_sie(argumenty, repo):
            if argumenty[0] == "merge" and "--ff-only" in argumenty and not getattr(test, "_wtracono", False):
                test._wtracono = True
                test.pisz(test.karol, "a.txt", "agent pisze a.txt\n")
                test.pisz(test.karol, "nowy.txt", "agent tworzy nowy.txt\n")
            return None
        latka, _ = self.git_z_zapisem(wtrac_sie)
        with latka:
            a = self.obieg()
        self.assertEqual(a["stan"], "czeka", a)
        self.assertTrue(set(a["pliki"]) & {"a.txt", "nowy.txt"}, a)
        self.assertNotIn("(lista plików w logu panelu)", a["pliki"])
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.czytaj(self.karol, "a.txt"), b"agent pisze a.txt\n")
        self.assertEqual(self.czytaj(self.karol, "nowy.txt"), b"agent tworzy nowy.txt\n")
        self.assertFalse(os.path.exists(os.path.join(self.karol, ".git", "MERGE_HEAD")))
        self.assertEqual(self.g(["stash", "list"], self.karol), "")

    def test_ignorowany_plik_tam_gdzie_nadchodzi_katalog(self):
        self.pisz(self.karol, "wynik.log", "mój ignorowany plik\n")              # .gitignore: *.log
        przed = self.odcisk(self.karol, ["wynik.log"])
        head = self.head(self.karol)
        self.g(["pull", "-q", "--no-rebase"], self.pawel)
        self.pisz(self.pawel, "wynik.log/x.txt", "katalog Pawła\n")
        self.g(["add", "-f", "wynik.log/x.txt"], self.pawel)
        self.g(["commit", "-q", "-m", "Paweł: katalog wynik.log"], self.pawel)
        self.g(["push", "-q"], self.pawel)

        a = self.obieg()
        self.assertEqual(a["stan"], "czeka", a)
        self.assertIn("wynik.log", a["pliki"])
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.odcisk(self.karol, ["wynik.log"]), przed)

        # druga zapora: nawet bez sprawdzenia przedrostków git (--no-overwrite-ignore) odmawia i pliku nie kasuje
        with mock.patch.object(gitsync, "_ignorowane_na_drodze", lambda repo, pliki: []):
            a = self.obieg()
        self.assertEqual(a["stan"], "czeka", a)
        self.assertEqual(self.head(self.karol), head)
        self.assertEqual(self.odcisk(self.karol, ["wynik.log"]), przed)

    def test_sledzony_plik_zastapiony_katalogiem_to_zwykla_zmiana(self):
        self.g(["pull", "-q", "--no-rebase"], self.pawel)
        self.g(["rm", "-q", "a.txt"], self.pawel)
        self.pisz(self.pawel, "a.txt/w.txt", "teraz katalog\n")
        self.g(["add", "-A"], self.pawel)
        self.g(["commit", "-q", "-m", "Paweł: a.txt to katalog"], self.pawel)
        self.g(["push", "-q"], self.pawel)
        a = self.obieg()
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(self.head(self.karol), self.head(self.pawel))
        self.assertTrue(os.path.isfile(os.path.join(self.karol, "a.txt", "w.txt")))

    def test_rebase_w_toku_czeka_i_nie_jest_przerywany(self):
        self.pisz(self.karol, "a.txt", "wiersz 1\nKAROL\nwiersz 3\n")
        self.g(["commit", "-q", "-am", "Karol: a.txt"], self.karol)
        self.commit_pawla("a.txt", "wiersz 1\nPAWEŁ\nwiersz 3\n", "Paweł: a.txt")
        self.g(["fetch", "-q"], self.karol)
        r = subprocess.run(["git", "rebase", "origin/main"], cwd=self.karol, capture_output=True,
                           creationflags=rdzen.CREATE_NO_WINDOW)        # człowiek w terminalu: rebase z konfliktem
        self.assertNotEqual(r.returncode, 0)
        rebase = os.path.join(self.karol, ".git", "rebase-merge")
        self.assertTrue(os.path.isdir(rebase))
        przed = self.czytaj(self.karol, "a.txt")
        latka, polecenia = self.git_z_zapisem()
        with latka:
            a = self.obieg()
            with self.assertRaises(BladHTTP) as ctx:
                gitsync.pobierz(self.karol, bezpiecznie=True)
            self.assertEqual(ctx.exception.status, 409)
            with self.assertRaises(BladHTTP) as ctx:
                gitsync.pobierz(self.karol, bezpiecznie=False)              # stara droga też nie przerywa rebase
            self.assertEqual(ctx.exception.status, 409)
        self.assertEqual(a["stan"], "czeka", a)
        self.assertEqual(a["krotko"], "trwa scalanie w repozytorium")
        self.assertFalse([p for p in polecenia if p[0] in ("fetch", "merge", "rebase", "pull", "commit", "push")],
                         polecenia)
        self.assertTrue(os.path.isdir(rebase))
        self.assertEqual(self.czytaj(self.karol, "a.txt"), przed)

        # panel startuje w trakcie rebase: pętla rusza mimo odłączonego HEAD i czeka (nie „wyłączona”)
        gitsync._auto.clear()
        with mock.patch.object(rdzen, "REPO", self.karol), mock.patch.dict(os.environ, {"BC_GIT_AUTO": "1"}), \
                mock.patch.object(gitsync, "START_PO_S", 0), mock.patch.object(gitsync, "sciezki_panelu", lambda: SC):
            try:
                gitsync.uruchom_w_tle()
                self.assertTrue(gitsync.petla_dziala())
                koniec = time.time() + 30
                while time.time() < koniec and not gitsync.stan_auto().get("ostatni_obieg"):
                    time.sleep(0.2)
                a = gitsync.stan_auto()
            finally:
                gitsync.zatrzymaj_w_tle(czekaj_s=30)
                gitsync._petla.update(watek=None, stop=None, repo=None)
        self.assertEqual((a["stan"], a["krotko"]), ("czeka", "trwa scalanie w repozytorium"), a)
        self.assertTrue(os.path.isdir(rebase))

    def test_lista_plikow_z_odmowy_oba_wciecia(self):
        tab = ("error: Your local changes to the following files would be overwritten by merge:\n\ta.txt\n\tb/c.txt\n"
               "Please commit your changes or stash them before you merge.\nAborting\n")
        spacje = ("error: The following untracked working tree files would be overwritten by merge:\n  nowy.txt\n"
                  "  x y.txt\nPlease move or remove them before you merge.\nAborting\n")
        self.assertEqual(gitsync._pliki_z_odmowy(tab), ["a.txt", "b/c.txt"])
        self.assertEqual(gitsync._pliki_z_odmowy(spacje), ["nowy.txt", "x y.txt"])
        self.assertEqual(gitsync._pliki_z_odmowy("fatal: coś innego\n  nie plik\n"), [])


# =========================================================================== S3: samo wysyłanie
class TestSamoWysylanie(Baza):
    def test_z_opoznieniem_i_zbieraniem_zmian(self):
        t0 = time.time()
        self.pisz(self.karol, "panel/dane/raporty/r1.json", "{}\n")
        self.pisz(self.karol, "inny.txt", "nie panel\n")
        a = self.obieg(teraz=t0)
        self.assertEqual(a["stan"], "ok")
        self.assertEqual(a["czeka_na_wyslanie"], 1)
        self.assertEqual(a["krotko"], "zmiany pójdą za chwilę")
        self.pisz(self.karol, "panel/dane/komentarze/k1.json", "{}\n")
        self.obieg(teraz=t0 + 30)                               # dalej czeka (ostatnia zmiana przed chwilą)
        self.assertEqual(self.g(["rev-list", "--count", "HEAD"], self.karol).strip(), "1")
        a = self.obieg(teraz=time.time() + 61)
        self.assertEqual(a["stan"], "ok", a)
        self.assertEqual(self.g(["rev-list", "--count", "HEAD"], self.karol).strip(), "2")   # JEDEN commit na wszystko
        pliki = sorted(self.g(["show", "--name-only", "--format=", "HEAD"], self.karol).split())
        self.assertEqual(pliki, ["panel/dane/komentarze/k1.json", "panel/dane/raporty/r1.json"])
        temat = self.g(["log", "-1", "--format=%s"], self.karol).strip()
        self.assertTrue(temat.startswith("panel: dane panelu"), temat)
        self.assertIn("inny.txt", self.g(["status", "--porcelain"], self.karol))            # spoza panelu: nie poszło
        self.assertEqual(self.head(self.karol), self.g(["rev-parse", "main"], self.zdalne).strip())
        self.assertEqual(a["wyslanie"]["temat"], temat)

    def test_najdluzej_piec_minut(self):
        t0 = time.time()
        p = self.pisz(self.karol, "panel/dane/raporty/r1.json", "{}\n")
        self.obieg(teraz=t0)
        os.utime(p, (t0 + 290, t0 + 290))                      # ktoś ciągle pisze — ostatnia zmiana 11 s temu
        self.obieg(teraz=t0 + 200)
        self.assertEqual(self.g(["rev-list", "--count", "HEAD"], self.karol).strip(), "1")
        self.obieg(teraz=t0 + 301)
        self.assertEqual(self.g(["rev-list", "--count", "HEAD"], self.karol).strip(), "2")

    def test_odrzucony_push_pobranie_i_ponowny_push(self):
        self.pisz(self.karol, "panel/dane/raporty/r1.json", "{}\n")
        pawel = self

        def wyprzedz_push(argumenty, repo):
            if argumenty == ["push"] and not getattr(pawel, "_wyprzedzono", False):
                pawel._wyprzedzono = True
                pawel.commit_pawla("b.txt", "Paweł był pierwszy\n", "Paweł: b.txt")
            return None
        latka, polecenia = self.git_z_zapisem(wyprzedz_push)
        with latka:
            a = self.obieg(teraz=time.time() + 120)
        self.assertEqual([p for p in polecenia if p[0] == "push"], [["push"], ["push"]])   # dwa razy, bez --force
        self.assertEqual(a["stan"], "ok", a)
        zdalny = self.g(["rev-parse", "main"], self.zdalne).strip()
        self.assertEqual(self.head(self.karol), zdalny)
        drzewo = self.g(["ls-tree", "-r", "--name-only", zdalny], self.karol).split()
        self.assertIn("b.txt", drzewo)
        self.assertIn("panel/dane/raporty/r1.json", drzewo)

    def test_nie_commituje_spoza_panelu(self):
        self.pisz(self.karol, "src/kod.lua", "print(1)\n")
        self.pisz(self.karol, "README.md", "zmiana\n")
        a = self.obieg(teraz=time.time() + 600)
        self.assertEqual(self.g(["rev-list", "--count", "HEAD"], self.karol).strip(), "1")
        self.assertEqual(a["stan"], "ok")
        self.assertTrue(a["zgodne"])


# =========================================================================== błędy, odstępy, brak zdalnego
class TestBledy(Baza):
    def test_brak_zdalnego(self):
        samotne = os.path.join(self.tmp, "samotne")
        self.g(["init", "-q", "-b", "main", samotne], self.tmp)
        latka, polecenia = self.git_z_zapisem()
        with latka:
            a = gitsync.obieg(samotne, SC, USTAW)
        self.assertEqual(a["stan"], "wylaczona")
        self.assertFalse(a["wlaczona"])
        self.assertFalse([p for p in polecenia if p[0] in ("fetch", "push", "merge")], polecenia)

    def test_zdalne_z_bledem_rosnacy_odstep(self):
        self.g(["remote", "set-url", "origin", os.path.join(self.tmp, "nie-ma-takiego.git")], self.karol)
        t0 = time.time()
        a = self.obieg(teraz=t0)
        self.assertEqual(a["stan"], "blad", a)
        st = gitsync._st(self.karol)
        self.assertEqual(st["nastepna_proba"], t0 + 180)
        latka, polecenia = self.git_z_zapisem()
        with latka:
            self.obieg(teraz=t0 + 60)                          # w trakcie odstępu: nic
        self.assertEqual(polecenia, [])
        self.obieg(teraz=t0 + 181)
        self.assertEqual(st["nastepna_proba"], t0 + 181 + 360)
        self.obieg(teraz=t0 + 600)
        self.obieg(teraz=t0 + 2000)
        self.obieg(teraz=t0 + 4000)
        self.assertEqual(st["nastepna_proba"], t0 + 4000 + 900)                   # najwyżej co 15 minut

    def test_brak_logowania(self):
        def bez_logowania(argumenty, repo):
            if argumenty[0] == "fetch":
                return 128, "", ("fatal: could not read Username for 'https://login:tajne@github.com': "
                                 "terminal prompts disabled")
            return None
        latka, _ = self.git_z_zapisem(bez_logowania)
        t0 = time.time()
        with latka:
            a = self.obieg(teraz=t0)
        self.assertEqual(a["stan"], "brak_logowania")
        self.assertIn("zaloguj", a["co_zrobic"].lower())
        self.assertEqual(gitsync._st(self.karol)["nastepna_proba"], t0 + 900)
        self.assertNotIn("tajne", json.dumps(a, ensure_ascii=False))

    def test_dlugi_opis_bledu_przyciety_bez_hasla(self):
        def dziwny(argumenty, repo):
            if argumenty[0] == "fetch":
                return 1, "", "fatal: https://ktos:tajny-token@example.invalid/x " + "x" * 2000
            return None
        latka, _ = self.git_z_zapisem(dziwny)
        with latka:
            a = self.obieg()
        self.assertEqual(a["stan"], "blad")
        self.assertLess(len(a["opis"]), 420)
        self.assertNotIn("tajny-token", a["opis"])

    def test_opis_bledu_bez_sciezek_z_nazwa_uzytkownika(self):
        """Opis błędu widzi gość przez link i grupa na Telegramie — bez ścieżki repozytorium i katalogu domowego."""
        dom = os.path.expanduser("~")
        for sciezka in (gitsync.rdzen.REPO, gitsync.rdzen.REPO.replace("\\", "/"), dom, dom.replace("\\", "/")):
            t = gitsync._czysty("fatal: Unable to create '%s/.git/index.lock': File exists." % sciezka, 400)
            self.assertNotIn(os.path.basename(dom), t, sciezka)
            self.assertIn("index.lock", t)
        self.assertIn("<repo>", gitsync._czysty("blad w %s/.git" % gitsync.rdzen.REPO, 400))


# =========================================================================== powiadomienia (atrapa Telegrama)
class TestPowiadomienia(Baza):
    @classmethod
    def setUpClass(cls):
        cls.atrapa = AtrapaTelegrama(TOKEN).start()

    @classmethod
    def tearDownClass(cls):
        cls.atrapa.stop()

    def setUp(self):
        super().setUp()
        plik = os.path.join(self.tmp, "telegram.json")
        with open(plik, "w", encoding="utf-8") as f:
            json.dump({"token": TOKEN, "bot": "bc_test_bot", "osoby": {"111": "Karol", "222": "Paweł"},
                       "grupy": {str(GRUPA): "B&C"}}, f)
        self.latki_tg = [mock.patch.object(telegram, "_plik_ustawien", lambda: plik),
                         mock.patch.object(telegram, "_plik_stanu", lambda: os.path.join(self.tmp, "tg_stan.json")),
                         mock.patch.object(telegram, "BOT", telegram.Bot(api=self.atrapa.adres, synchronicznie=True))]
        for l in self.latki_tg:
            l.start()
        telegram._ust_pamiec.update(stan=None, dane=None)
        self.atrapa.wyczysc()

    def tearDown(self):
        for l in reversed(self.latki_tg):
            l.stop()
        telegram._ust_pamiec.update(stan=None, dane=None)
        super().tearDown()

    def wiadomosci(self):
        return self.atrapa.zadania("sendMessage")

    def test_cudze_commity_jedna_wiadomosc_zwyklym_tekstem(self):
        self.commit_pawla("b.txt", "1\n", "<b>Nowy HUD</b> & rybki")
        self.commit_pawla("c.txt", "2\n", "Paweł: drugi")
        self.obieg(telegram=True)
        w = self.wiadomosci()
        self.assertEqual(len(w), 1, w)
        self.assertEqual(w[0]["chat_id"], GRUPA)
        self.assertNotIn("parse_mode", w[0])                   # zwykły tekst: treść od ludzi nie jest HTML-em
        self.assertIn("Paweł", w[0]["text"])
        self.assertIn("2 zmiany", w[0]["text"])
        self.assertIn("<b>Nowy HUD</b> & rybki", w[0]["text"])

    def test_wlasne_commity_bez_wiadomosci_i_wylacznik(self):
        drugi = self.klon("karol2", "Karol")                   # ta sama osoba z innego klonu
        self.pisz(drugi, "x.txt", "x\n")
        self.g(["add", "x.txt"], drugi)
        self.g(["commit", "-q", "-m", "Karol z laptopa"], drugi)
        self.g(["push", "-q"], drugi)
        self.obieg(telegram=True)
        self.assertEqual(self.wiadomosci(), [])
        self.commit_pawla("b.txt", "1\n", "Paweł: b")
        self.obieg(telegram=False)                             # git.auto_telegram = false
        self.assertEqual(self.wiadomosci(), [])

    def test_incydent_raz_i_powrot_do_normy(self):
        url = self.g(["remote", "get-url", "origin"], self.karol).strip()
        self.g(["remote", "set-url", "origin", os.path.join(self.tmp, "nie-ma.git")], self.karol)
        t = time.time()
        for i in range(5):                                     # pięć prób (każda po odstępie)
            self.obieg(teraz=t + i * 1000, telegram=True)
        w = self.wiadomosci()
        self.assertEqual(len(w), 1, w)
        self.assertIn("Co zrobić", w[0]["text"])
        self.g(["remote", "set-url", "origin", url], self.karol)
        self.obieg(teraz=t + 9000, telegram=True)
        self.obieg(teraz=t + 9100, telegram=True)
        w = self.wiadomosci()
        self.assertEqual(len(w), 2, w)
        self.assertIn("znów działa", w[1]["text"])

    def test_bez_ustawien_telegrama_nic(self):
        os.remove(os.path.join(self.tmp, "telegram.json"))
        telegram._ust_pamiec.update(stan=None, dane=None)
        self.commit_pawla("b.txt", "1\n", "Paweł: b")
        a = self.obieg(telegram=True)
        self.assertEqual(a["stan"], "ok")
        self.assertEqual(self.atrapa.zadania(), [])


# =========================================================================== stan w API, pętla i bezpieczniki
class TestStanIPetla(Baza):
    def test_pole_auto_w_stanie(self):
        self.obieg()
        a = gitsync.stan_auto(self.karol)
        for k in ("wlaczona", "stan", "opis", "zgodne", "pobranie", "wyslanie", "pliki", "co_s", "wyslij_po_s"):
            self.assertIn(k, a)
        self.assertIn(a["stan"], gitsync.STANY_AUTO)
        with mock.patch.object(gitsync, "stan", lambda *a, **k: {"galaz": "main", "zdalne": None}), \
                mock.patch.object(gitsync, "sejf_do_wyslania", lambda *a: ([], [], [])):
            w = gitsync._t_stan(None)
        self.assertIn("auto", w)
        self.assertFalse(w["auto"]["wlaczona"])                # w testach pętla nie działa → „wyłączona”
        self.assertEqual(w["auto"]["stan"], "wylaczona")
        self.assertEqual(gitsync._t_auto(None)["stan"], "wylaczona")          # GET /api/git/auto: sam stan, bez gita

    def test_petla_nie_startuje_w_testach(self):
        latka, polecenia = self.git_z_zapisem()
        with latka:
            gitsync.uruchom_w_tle()
        self.assertFalse(gitsync.petla_dziala())
        self.assertIsNone(gitsync._petla["watek"])
        self.assertEqual(polecenia, [])
        self.assertIn("BC_GIT_AUTO", gitsync.powod_wylaczenia())
        with mock.patch.dict(os.environ, {"BC_GIT_AUTO": ""}):
            self.assertIn("zastępczych", gitsync.powod_wylaczenia())   # testy mają BC_PANEL_DANE / BC_PANEL_RUNTIME

    def test_bezpiecznik_prawdziwego_repozytorium(self):
        latka, polecenia = self.git_z_zapisem()
        with latka:
            with self.assertRaises(RuntimeError):
                gitsync.obieg(rdzen.REPO, SC, USTAW)
            with self.assertRaises(RuntimeError):
                gitsync.obieg(None, SC, USTAW)
            with self.assertRaises(RuntimeError):
                gitsync.pobierz(rdzen.REPO, bezpiecznie=True)
            with mock.patch.dict(os.environ, {"BC_GIT_AUTO": "1"}), \
                    mock.patch.object(gitsync, "_upstream", lambda r: "origin/main"):
                with self.assertRaises(RuntimeError):
                    gitsync.uruchom_w_tle()
        self.assertEqual(polecenia, [])
        self.assertIsNone(gitsync._petla["watek"])

    def test_petla_start_i_czyste_zamkniecie(self):
        """Pętla na repozytorium próbnym (podmienione rdzen.REPO): pierwszy obieg pobiera, zamknięcie kończy wątek."""
        self.commit_pawla("b.txt", "1\n", "Paweł: b")
        with mock.patch.object(rdzen, "REPO", self.karol), mock.patch.dict(os.environ, {"BC_GIT_AUTO": "1"}), \
                mock.patch.object(gitsync, "START_PO_S", 0), mock.patch.object(gitsync, "sciezki_panelu", lambda: SC):
            try:
                gitsync.uruchom_w_tle()
                self.assertTrue(gitsync.petla_dziala())
                koniec = time.time() + 30
                while time.time() < koniec and self.head(self.karol) != self.head(self.pawel):
                    time.sleep(0.2)
                self.assertEqual(self.head(self.karol), self.head(self.pawel))
                self.assertTrue(gitsync.stan_auto()["wlaczona"])
            finally:
                gitsync.zatrzymaj_w_tle(czekaj_s=30)
                w = gitsync._petla["watek"]
                gitsync._petla.update(watek=None, stop=None, repo=None)
        self.assertFalse(w.is_alive())


if __name__ == "__main__":
    unittest.main()
