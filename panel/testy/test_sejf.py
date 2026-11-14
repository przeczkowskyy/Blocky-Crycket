# -*- coding: utf-8 -*-
"""Testy modułów sejfu, gita i obecności (sama biblioteka standardowa).

Uruchomienie (z katalogu panel/):
    PYTHONDONTWRITEBYTECODE=1 python -m unittest testy.test_sejf

Parsery planu i graf sprawdzane są na PRAWDZIWYM sejfie `B&C/` (tylko odczyt). Git sprawdzany jest wyłącznie na
tymczasowej parze repozytoriów (bare + dwa klony) w katalogu tymczasowym — prawdziwe repo jest tylko czytane.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)
# stan lokalny testów nie może trafić do prawdziwego katalogu panelu ani do %LOCALAPPDATA%
os.environ.setdefault("BC_PANEL_RUNTIME", os.path.join(tempfile.gettempdir(), "bc_panel_testy_runtime"))
os.environ.setdefault("BC_PANEL_DANE", os.path.join(tempfile.gettempdir(), "bc_panel_testy_dane"))

from bc import gitsync, obecnosc, rdzen, sejf  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

SEJF_BC = os.path.join(rdzen.REPO, "B&C")


@unittest.skipUnless(os.path.isdir(os.path.join(SEJF_BC, "Produkcja")), "brak sejfu B&C w repozytorium")
class TestPlanNaPrawdziwymSejfie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = sejf.plan()

    def test_decyzje_d001_d011(self):
        decyzje = {d["id"]: d for d in self.plan["decyzje"]}
        for nr in range(1, 12):
            self.assertIn("D-%03d" % nr, decyzje)
        dozwolone = {"zatwierdzona", "do_decyzji", "propozycja", "odrzucona", "zastapiona", "nieaktualna"}
        for d in decyzje.values():
            self.assertIn(d["status"], dozwolone)
            self.assertTrue(d["tytul"])
            self.assertNotIn("---", d["opis_md"])              # stopka rejestru nie wchodzi do opisu
        self.assertEqual(decyzje["D-008"]["status"], "zatwierdzona")
        self.assertEqual(decyzje["D-008"]["emoji"], "✅")
        self.assertEqual(decyzje["D-008"]["kategoria"], "narzędzia")
        # (statusów D-006 / D-009 nie sprawdzamy — zmieniają się, gdy zespół podejmuje decyzje; zatwierdzoną decyzję
        # może też zastąpić nowsza — tak D-027 zastąpiła D-001 13.11.2026)
        for nr in range(1, 6):
            self.assertIn(decyzje["D-%03d" % nr]["status"], ("zatwierdzona", "zastapiona"), "D-%03d" % nr)
        # tytuł z odwrotnymi apostrofami
        self.assertIn("$ignoreUnknownInstances", decyzje["D-006"]["tytul"])
        self.assertNotIn("`", decyzje["D-006"]["tytul"])

    def test_roadmapa_aktywna_faza_1(self):
        fazy = self.plan["roadmapa"]["fazy"]
        aktywne = [f for f in fazy if f["aktywna"]]
        self.assertEqual(len(aktywne), 1)
        self.assertTrue(aktywne[0]["nazwa"].startswith("Faza 1"))
        self.assertNotIn("▶", aktywne[0]["nazwa"])
        self.assertTrue(aktywne[0]["pozycje"])
        self.assertTrue(0 <= aktywne[0]["postep"] <= 100)
        self.assertIn("w trakcie", aktywne[0]["status_tekst"])
        propozycje = self.plan["roadmapa"]["propozycje"]
        self.assertEqual([p["nr"] for p in propozycje], [2, 3, 4, 5, 6])
        self.assertTrue(all(p["nazwa"] and not p["nazwa"].endswith(":") for p in propozycje))

    def test_zadania_priorytety_i_sekcje(self):
        z = self.plan["zadania"]
        self.assertGreater(len(z["sekcje"]), 2)
        pozycje = [p for s in z["sekcje"] for p in s["pozycje"]]
        self.assertTrue(any(p.get("priorytet") == "wysoki" for p in pozycje))
        for p in pozycje:
            if "priorytet" in p:
                self.assertIn(p["priorytet"], ("wysoki", "średni", "niski"))
                self.assertNotIn("#" + p["priorytet"], p["tekst_md"])
        self.assertEqual(z["otwarte"], sum(1 for p in pozycje if not p["zrobione"]))
        self.assertEqual(z["zrobione"], sum(1 for p in pozycje if p["zrobione"]))
        # sekcja assetów: kilka pól wyboru w jednej linii daje osobne pozycje
        assety = [s for s in z["sekcje"] if "Assety" in s["nazwa"]]
        self.assertTrue(assety)
        teksty = [p["tekst_md"] for p in assety[0]["pozycje"]]
        self.assertTrue(all("[x]" not in t and "[ ]" not in t for t in teksty))
        self.assertGreater(len(teksty), 6)
        # zrobione z datą
        z_data = [p for p in pozycje if p.get("data")]
        self.assertTrue(z_data)
        self.assertRegex(z_data[0]["data"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertFalse(z_data[0]["tekst_md"].startswith(z_data[0]["data"]))

    def test_pytania_otwarte(self):
        # liczba pytań rośnie z każdą rozmową zespołu — sprawdzamy niezmienniki, nie bieżącą liczbę
        pytania = self.plan["pytania"]
        self.assertGreaterEqual(len(pytania), 6)
        nry = [p["nr"] for p in pytania]
        self.assertEqual(nry[:6], [1, 2, 3, 4, 5, 6])
        self.assertEqual(len(set(nry)), len(nry))
        for p in pytania:
            self.assertTrue(p["tresc_md"] and p["tytul"])
            self.assertEqual(p["otwarte"], not p["odpowiedz_md"])
            for ident in p["rozstrzyga"] + p["powiazane"]:
                self.assertRegex(ident, r"^D-\d{3,4}$")
            self.assertFalse(set(p["rozstrzyga"]) & set(p["powiazane"]))
        # wiersze „Rozstrzyga: D-0XX” są w prawdziwych pytaniach (np. 16: D-019, D-020)
        self.assertTrue(any(p["rozstrzyga"] for p in pytania))

    def test_dziennik_ma_daty(self):
        d = self.plan["dziennik"]
        self.assertTrue(d)
        self.assertLessEqual(len(d), 30)
        for w in d:
            self.assertRegex(w["data"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(w["kto"])
            self.assertIsInstance(w["punkty_md"], list)
        self.assertEqual([w["data"] for w in d], sorted([w["data"] for w in d], reverse=True))

    def test_zrodla(self):
        self.assertIn("B&C/Produkcja/Zadania.md", self.plan["zrodla"])


@unittest.skipUnless(os.path.isdir(SEJF_BC), "brak sejfu B&C w repozytorium")
class TestSiecNaPrawdziwymSejfie(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.siec = sejf.siec()

    def test_wezly_i_krawedzie(self):
        wezly, krawedzie = self.siec["wezly"], self.siec["krawedzie"]
        self.assertGreater(len(wezly), 20)
        self.assertEqual([w["id"] for w in wezly], list(range(len(wezly))))
        pary = set()
        for a, b in krawedzie:
            self.assertTrue(0 <= a < len(wezly) and 0 <= b < len(wezly))
            self.assertNotEqual(a, b)
            pary.add((min(a, b), max(a, b)))
        self.assertEqual(len(pary), len(krawedzie))              # każda para raz
        stopnie = [0] * len(wezly)
        for a, b in krawedzie:
            stopnie[a] += 1
            stopnie[b] += 1
        self.assertEqual(stopnie, [w["stopien"] for w in wezly])
        self.assertEqual(self.siec["statystyki"]["notatki"], len(wezly))
        self.assertEqual(self.siec["statystyki"]["powiazania"], len(krawedzie))

    def test_kategorie_i_kolory(self):
        kat = {(k["sejf"], k["nazwa"]): k for k in self.siec["kategorie"]}
        self.assertEqual(kat[("B&C", "Gra")]["kolor"], "#f5b82e")
        self.assertEqual(kat[("B&C", "(korzeń)")]["kolor"], "#ffffff")
        for w in self.siec["wezly"]:
            self.assertIn((w["sejf"], w["kategoria"]), kat)
        self.assertEqual(sum(k["liczba"] for k in kat.values()), len(self.siec["wezly"]))

    def test_notatka_i_ochrona_sciezek(self):
        w = next(w for w in self.siec["wezly"] if w["tytul"] == "Zadania")
        n = sejf.notatka(w["sciezka"])
        self.assertEqual(n["tytul"], "Zadania")
        self.assertFalse(n["tresc_md"].startswith("---"))
        self.assertIn("tags", n["frontmatter"])
        self.assertTrue(n["linki_wy"])
        self.assertTrue(n["linki_we"])
        for zla, status in (("panel/serwer.py", 403), ("../B&C/00 Start.md", 403), ("C:/Windows/win.ini", 403),
                            ("B&C/../panel/serwer.py", 403), ("B&C/Nie ma takiej.md", 404)):
            with self.assertRaises(BladHTTP) as ctx:
                sejf.notatka(zla)
            self.assertEqual(ctx.exception.status, status, zla)

    def test_szukaj(self):
        wyniki = sejf.szukaj("karczm")["wyniki"]
        self.assertTrue(wyniki)
        self.assertLessEqual(len(wyniki), 40)
        self.assertTrue(all(len(w["fragment"]) <= 170 for w in wyniki))
        self.assertEqual(sejf.szukaj("")["wyniki"], [])


class TestParserowNaSztucznychDanych(unittest.TestCase):
    def test_frontmatter(self):
        fm, tresc, _ = sejf.parsuj_frontmatter(
            '---\nstatus: kanon\ntags: [a, "b, c", d]\nlista:\n  - x\n  - "y: z"\nźródło: "[[Notatka]] §3"\n'
            'liczba: 12\ntak: true\nzepsute: [a, b\n: bez klucza\nblok: |\n  linia 1\n  linia 2\n---\n# Treść\n')
        self.assertEqual(fm["status"], "kanon")
        self.assertEqual(fm["tags"], ["a", "b, c", "d"])
        self.assertEqual(fm["lista"], ["x", "y: z"])
        self.assertEqual(fm["źródło"], "[[Notatka]] §3")
        self.assertEqual(fm["liczba"], 12)
        self.assertIs(fm["tak"], True)
        self.assertEqual(fm["zepsute"], ["a", "b"])
        self.assertEqual(fm["blok"], "linia 1\nlinia 2")
        self.assertEqual(tresc, "# Treść\n")
        # bez zamknięcia i śmieci — bez wyjątku
        self.assertEqual(sejf.parsuj_frontmatter("---\na: [\n")[0], {})
        self.assertEqual(sejf.parsuj_frontmatter("bez frontmattera")[0], {})
        sejf.parsuj_frontmatter("---\n\t: : :\n- - -\n'x: \"\n---\n")

    def test_linki_pomijaja_kod(self):
        tekst = ("[[A]] i [[B|alias]] i [[C#Nagłówek]] i ![[obraz.png]] i ![[D]]\n"
                 "`[[Nie1]]` oraz [[E#D-008 Tytuł `z kodem`|D-008]]\n```\n[[Nie2]]\n```\n~~~\n[[Nie3]]\n~~~\n[[#tylko nagłówek]]")
        cele = [c for c, _ in sejf.wyciagnij_linki(tekst)]
        self.assertEqual(cele, ["A", "B", "C", "obraz.png", "D", "E"])

    def test_graf_na_sztucznym_sejfie(self):
        tmp = tempfile.mkdtemp(prefix="bc_sejf_")
        try:
            def zapisz(rel, tekst):
                p = os.path.join(tmp, *rel.split("/"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(tekst)
            zapisz("A.md", "[[B]] [[B]] [[Gra/C|cc]] [[Brak]] ![[obraz.png]] ![[Brak2]]\n```\n[[Kod]]\n```")
            zapisz("Gra/B.md", "---\nstatus: kanon\ntags: [x]\n---\n[[A]] [[c]]")
            zapisz("Gra/C.md", "nic")
            zapisz(".obsidian/X.md", "[[A]]")
            ix = sejf.zbuduj_indeks([("T", "Test", tmp)])
            nazwy = [n["tytul"] for n in ix["notatki"]]
            self.assertEqual(nazwy, ["A", "B", "C"])
            self.assertEqual(ix["krawedzie"], [(0, 1), (0, 2), (1, 2)])
            self.assertEqual(ix["stopnie"], [2, 2, 2])
            self.assertEqual([x["link"] for x in ix["nierozwiazane"]], ["Brak"])
            kolory = {k["nazwa"]: k["kolor"] for k in ix["kategorie"]}
            self.assertIn(kolory["Gra"], sejf.PALETA_CHLODNA)    # inny sejf niż B&C: chłodna paleta
            self.assertEqual(ix["notatki"][1]["status"], "kanon")
            self.assertEqual(ix["notatki"][1]["tagi"], ["x"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_brak_pliku_planu_to_pusta_lista(self):
        self.assertEqual(sejf.parsuj_decyzje(""), [])
        self.assertEqual(sejf.parsuj_zadania("")["sekcje"], [])
        self.assertEqual(sejf.parsuj_roadmape("")["fazy"], [])
        p = sejf.parsuj_pytania("## 1. Pyt\nTreść\n**Odpowiedź:** Tak, zgoda.\n\n## 2. Drugie\n**Odpowiedź:**\n")
        self.assertEqual([x["otwarte"] for x in p], [False, True])
        self.assertEqual(p[0]["odpowiedz_md"], "Tak, zgoda.")
        self.assertEqual((p[0]["rozstrzyga"], p[0]["powiazane"]), ([], []))

    def test_pytania_rozstrzyga_i_wzmianki(self):
        p = sejf.parsuj_pytania("## 4. Czy D-006 i D-7?\nZob. D-009.\n- **Rozstrzyga:** D-6, D-007\n"
                                "rozstrzyga: D-010\n**Odpowiedź:**\nRozstrzyga: D-011 (w odpowiedzi — pomijane)\n")
        self.assertEqual(p[0]["rozstrzyga"], ["D-006", "D-007", "D-010"])
        self.assertEqual(p[0]["powiazane"], ["D-009"])                   # D-011 jest w odpowiedzi, nie w treści


def _git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       creationflags=rdzen.CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr))
    return r.stdout


@unittest.skipUnless(shutil.which("git"), "brak gita")
class TestGitNaRepozytoriumTestowym(unittest.TestCase):
    """Wyłącznie tymczasowe repozytoria: bare (jak GitHub) + klon Karola + klon Pawła."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_git_")
        self.zdalne = os.path.join(self.tmp, "zdalne.git")
        _git(["init", "--bare", "-b", "main", self.zdalne], self.tmp)
        self.karol = self._klon("karol", "Karol")
        os.makedirs(os.path.join(self.karol, "panel", "dane"))
        with open(os.path.join(self.karol, "README.md"), "w", encoding="utf-8") as f:
            f.write("repo testowe\n")
        _git(["add", "-A"], self.karol)
        _git(["commit", "-m", "start"], self.karol)
        _git(["push", "-u", "origin", "main"], self.karol)
        self.pawel = self._klon("pawel", "Paweł")

    def tearDown(self):
        def zdejmij_tylko_do_odczytu(fn, sciezka, _):
            os.chmod(sciezka, 0o700)
            fn(sciezka)
        shutil.rmtree(self.tmp, onerror=zdejmij_tylko_do_odczytu)

    def _klon(self, nazwa, osoba):
        cel = os.path.join(self.tmp, nazwa)
        _git(["clone", "-q", self.zdalne, cel], self.tmp)
        _git(["config", "user.name", osoba], cel)
        _git(["config", "user.email", "%s@example.invalid" % nazwa], cel)
        _git(["checkout", "-q", "-B", "main"], cel)
        return cel

    def _plik(self, repo, rel, tekst):
        p = os.path.join(repo, *rel.split("/"))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(tekst)

    def test_stan_wyslij_pobierz_i_odrzucenie(self):
        sc = ["panel/dane"]
        self._plik(self.karol, "panel/dane/komentarze/k1.json", "{}\n")
        self._plik(self.karol, "inny.txt", "nie panel\n")
        s = gitsync.stan(self.karol, sc, wymus=True)
        self.assertEqual(s["galaz"], "main")
        self.assertFalse(s["czyste"])
        self.assertEqual(s["zmiany_panelu"], 1)
        self.assertEqual(s["zdalne"]["nazwa"], "origin")

        w = gitsync.wyslij(self.karol, "komentarz ąę", sc)
        self.assertTrue(w["ok"])
        self.assertTrue(w["commit"])
        self.assertEqual(_git(["log", "-1", "--format=%s"], self.karol).strip(), "panel: komentarz ąę")
        zmienione = _git(["show", "--name-only", "--format=", "HEAD"], self.karol).split()
        self.assertEqual(zmienione, ["panel/dane/komentarze/k1.json"])  # inny.txt NIE trafił do commita
        self.assertIn("inny.txt", _git(["status", "--porcelain"], self.karol))

        w2 = gitsync.wyslij(self.karol, None, sc)                 # nic nowego
        self.assertTrue(w2["ok"])
        self.assertIsNone(w2["commit"])

        # Paweł pobiera, potem obaj piszą — drugi dostaje „Najpierw kliknij Pobierz”
        p = gitsync.pobierz(self.pawel)
        self.assertTrue(p["ok"])
        self.assertTrue(os.path.isfile(os.path.join(self.pawel, "panel", "dane", "komentarze", "k1.json")))
        self._plik(self.pawel, "panel/dane/komentarze/k2.json", "{}\n")
        self.assertTrue(gitsync.wyslij(self.pawel, "", sc)["ok"])
        self.assertEqual(_git(["log", "-1", "--format=%s"], self.pawel).strip(), "panel: dane panelu")
        self._plik(self.karol, "panel/dane/komentarze/k3.json", "{}\n")
        with self.assertRaises(BladHTTP) as ctx:
            gitsync.wyslij(self.karol, "drugi", sc)
        self.assertEqual(ctx.exception.status, 409)
        self.assertIn("Najpierw kliknij Pobierz", ctx.exception.komunikat)
        # Pobierz (z autostash niezacommitowanego inny.txt) i ponowne wysłanie
        self.assertTrue(gitsync.pobierz(self.karol)["ok"])
        self.assertTrue(gitsync.wyslij(self.karol, "drugi", sc)["ok"])
        s = gitsync.stan(self.karol, sc, wymus=True)
        self.assertEqual(s["do_wyslania"], 0)
        self.assertEqual(s["zmiany_panelu"], 0)
        self.assertEqual(len(s["ostatnie_commity"]), 4)

    def test_autorzy_w_obecnosci(self):
        self._plik(self.pawel, "panel/dane/a.json", "{}\n")
        _git(["add", "-A"], self.pawel)
        _git(["commit", "-m", "od Pawła"], self.pawel)
        obecnosc._git["wynik"] = None
        autorzy = obecnosc.git_autorzy(self.pawel)
        obecnosc._git["wynik"] = None
        self.assertEqual({a["autor"] for a in autorzy}, {"Karol", "Paweł"})
        self.assertEqual(autorzy[0]["autor"], "Paweł")


class TestObecnosci(unittest.TestCase):
    def test_pulsy(self):
        obecnosc.zapisz_puls("klient-1", "Karol", "plan", True)
        obecnosc.zapisz_puls("klient-1", "Karol", "siec", True)
        lista = [p for p in obecnosc.panel() if p["kto"] == "Karol"]
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0]["widok"], "siec")
        obecnosc._pulsy["klient-1"]["ostatnio"] -= 60            # puls starszy niż 45 s znika
        self.assertFalse([p for p in obecnosc.panel() if p["kto"] == "Karol"])

    def _z_modulem_studio(self, modul):
        """Podmienia bc.studio na atrapę (prawdziwy moduł łączy się z Roblox Studio — w testach go nie ruszamy)."""
        import bc
        stary_mod, stary_attr = sys.modules.get("bc.studio"), getattr(bc, "studio", None)
        if modul is None:                                         # brak modułu
            sys.modules["bc.studio"] = None                       # import rzuci ImportError
            if hasattr(bc, "studio"):
                delattr(bc, "studio")
        else:
            sys.modules["bc.studio"] = modul
            bc.studio = modul
        try:
            obecnosc._studio.update(wynik=None, watek=None)
            return obecnosc.studio_stan()
        finally:
            obecnosc._studio.update(wynik=None, watek=None)
            if stary_mod is not None:
                sys.modules["bc.studio"] = stary_mod
            else:
                sys.modules.pop("bc.studio", None)
            if stary_attr is not None:
                bc.studio = stary_attr
            elif hasattr(bc, "studio"):
                delattr(bc, "studio")

    def test_studio_zabezpieczenia(self):
        import types
        niedostepne = {"dostepne": False, "osoby": []}
        self.assertEqual(self._z_modulem_studio(None), niedostepne)                      # brak modułu
        self.assertEqual(self._z_modulem_studio(types.ModuleType("bc.studio")), niedostepne)  # brak funkcji
        zly = types.ModuleType("bc.studio")
        zly.stan = lambda: 1 / 0
        self.assertEqual(self._z_modulem_studio(zly), niedostepne)                       # wyjątek
        dobry = types.ModuleType("bc.studio")
        dobry.stan = lambda: {"mostek": True, "polaczone": True, "studio": {"tryb": "edit", "id": "x"},
                              "osoby": [{"nazwa": "Karol", "id": 1}, {"nazwa": "Paweł", "id": 2}]}
        self.assertEqual(self._z_modulem_studio(dobry),
                         {"dostepne": True, "tryb": "edit", "osoby": [{"nazwa": "Karol", "id": 1},
                                                                      {"nazwa": "Paweł", "id": 2}]})


if __name__ == "__main__":
    unittest.main()
