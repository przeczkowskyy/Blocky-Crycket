# -*- coding: utf-8 -*-
"""Testy Wytwórni pomysłów (bc/wytwornia.py) — wyłącznie na tymczasowej kopii sejfu.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_wytwornia

Sprawdza: czytanie notatek Wytwórni (frontmatter, karta oceny z tabeli, sumy, werdykt, metryki), lejek i portfel gier,
radar trendów, opisy kryteriów, dodanie pomysłu z szablonu (i bez szablonu) z wpisem w Dzienniku zmian i śladem dla
„Wyślij”, ocenę ludzi (kolumna w tabeli bajt w bajt + suma we frontmatterze), zmianę etapu, odmowę dla gościa
i osoby spoza zespołu, pulpit gry (raporty po tytule, zadania i decyzje po wzmiance) — także na prawdziwym serwerze.
"""
import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)

from bc import raporty, rdzen, sejf, wytwornia, zapis  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402
from testy import test_api  # noqa: E402
from testy.test_zapis import PLIKI  # noqa: E402

DZIS = "2026-11-20"

BONK = """---
status: propozycja
typ: pomysł-gry
gra: BONK
etap: prototyp
zdanie: "Bonk monsters into the sky and race your friends."
ocena_agenta: 17
werdykt_agenta: buduj
ocena_karol:
ocena_pawel:
d1: 12
d7:
sesja_min: 6.5
ccu:
miejsce: 92789057272917
aliases: [Bonk Game]
tags: [wytwórnia, pomysł]
---
# BONK

## W jednym zdaniu
Bonk monsters into the sky.

## Hak ciekawości
Jak wysoko poleci potwór?

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
| Jedno zdanie | 3 |  |  |
| Pierwsze 10 sekund | 2 |  |  |
| Hak ciekawości | 2 |  |  |
| Głębia | 1 |  |  |
| Inni gracze | 2 |  |  |
| Pokazanie się | 1 |  |  |
| Moment do nagrania | 3 |  |  |
| Powód powrotu | 1 |  |  |
| Trend | 1 |  |  |
| Koszt dla nas | 1 |  |  |

## Krytyka agenta
Za mało powodu do powrotu.

## Powiązane
- [[Radar trendów]]
"""

RING = """---
typ: pomysł-gry
gra: Ring Potworów
etap: ocena
werdykt_agenta: popraw
---
# Ring Potworów

## W jednym zdaniu
Potwory walczą na ringu, a gracze obstawiają.

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
| Jedno zdanie | 2 | 1 |  |
| Pierwsze 10 sekund | 1 |  |  |
"""

STARY = """---
typ: pomysł-gry
etap: porzucony
---
# Stary pomysł
"""

RADAR = """---
status: propozycja
aktualizacja: 2026-11-20
---
# Radar trendów

| Trend | Przykłady | Siła | Kierunek | Źródło |
|---|---|---|---|---|
| Brainrot | [[BONK]], Steal a Brainrot | 5/5 | rośnie | Roblox Charts |
| Tower defense | Toilet TD | 3/5 | spada | — |
"""

KARTA = """---
status: propozycja
---
# Karta oceny pomysłu

## 1. Jedno zdanie
Czy da się opowiedzieć grę jednym zdaniem.

## 2. Pierwsze 10 sekund
Co gracz robi od razu.

- **Trend** — czy gra trafia w to, co teraz rośnie.
"""

SZABLON = """---
status: propozycja
typ: pomysł-gry
gra: {{title}}
etap: pomysł
zdanie: "…"
ocena_agenta: 17
werdykt_agenta: buduj
ocena_karol:
ocena_pawel:
tags: [wytwórnia, pomysł]
---
# {{title}}

## W jednym zdaniu
> Jedno zdanie: kto, co robi, dlaczego to fajne.

## Pierwsze 10 sekund

## Hak ciekawości
_Co sprawia, że gracz chce zobaczyć więcej?_

## Karta oceny
| Kryterium | Agent | Karol | Paweł |
|---|---|---|---|
| Jedno zdanie |  |  |  |
| Pierwsze 10 sekund |  |  |  |
| Hak ciekawości |  |  |  |
| Głębia |  |  |  |
| Inni gracze |  |  |  |
| Pokazanie się |  |  |  |
| Moment do nagrania |  |  |  |
| Powód powrotu |  |  |  |
| Trend |  |  |  |
| Koszt dla nas |  |  |  |

## Krytyka agenta

## Najtańszy test
"""

ZADANIA_GRY = """---
status: kanon
---
# Zadania

## 🔥 Teraz
- [ ] BONK: poprawić zamach pałką · #wysoki
- [ ] Coś innego · #niski

## ✅ Zrobione
- [x] 2026-11-19: Ikona BONK gotowa
"""

DECYZJE_GRY = """---
status: kanon
---
# Rejestr decyzji

### D-112 BONK jako prototyp
✅ zatwierdzona · produkcja · zdecydował: Karol 2026-11-19
Robimy BONK.

### D-113 Inna sprawa
💡 propozycja · styl
Nie o grze (bonkers to nie BONK? — słowo „bonkers” nie pasuje).

---
"""


# Kopie prawdziwych notatek sejfu (20.11.2026): pomysł wygenerowany skryptem z badania, notatka B&C pisana ręcznie
# (z aliases), prawdziwy Radar trendów (Markdown w komórkach) i Karta oceny pomysłu — dane testowe, nie źródło prawdy.
DANE_PRAWDZIWE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dane_wytwornia")


def zbuduj_sejf(korzen, szablon=True, prawdziwe=False):
    """Tymczasowy sejf: Produkcja (pliki z test_zapis + zadania i decyzje o grze), Wytwórnia, szablon; z prawdziwe=True
    także kopie prawdziwych notatek (Monster Evolution, Blocky & Crycket, Radar trendów, Karta oceny pomysłu)."""
    os.makedirs(os.path.join(korzen, "Produkcja"))
    pliki = dict(PLIKI)
    pliki["zadania"] = ("Zadania.md", ZADANIA_GRY)
    pliki["decyzje"] = ("Rejestr decyzji.md", DECYZJE_GRY)
    for nazwa, tekst in pliki.values():
        with open(os.path.join(korzen, "Produkcja", nazwa), "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
    pom = os.path.join(korzen, "Wytwórnia", "Pomysły")
    os.makedirs(pom)
    for nazwa, tekst in (("BONK.md", BONK), ("Ring Potworów.md", RING), ("Stary pomysł.md", STARY)):
        with open(os.path.join(pom, nazwa), "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
    for nazwa, tekst in (("Radar trendów.md", RADAR), ("Karta oceny pomysłu.md", KARTA)):
        with open(os.path.join(korzen, "Wytwórnia", nazwa), "w", encoding="utf-8", newline="\n") as f:
            f.write(tekst)
    if prawdziwe:
        for nazwa in ("Monster Evolution.md", "Blocky & Crycket.md"):
            shutil.copyfile(os.path.join(DANE_PRAWDZIWE, nazwa), os.path.join(pom, nazwa))
        for nazwa in ("Radar trendów.md", "Karta oceny pomysłu.md"):
            shutil.copyfile(os.path.join(DANE_PRAWDZIWE, nazwa), os.path.join(korzen, "Wytwórnia", nazwa))
    if szablon:
        os.makedirs(os.path.join(korzen, "Szablony"))
        with open(os.path.join(korzen, "Szablony", "Pomysł gry.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(SZABLON)


class Baza(unittest.TestCase):
    szablon = True
    prawdziwe = False

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_wytwornia_")
        self.sejf = os.path.join(self.tmp, "sejf")
        zbuduj_sejf(self.sejf, self.szablon, self.prawdziwe)
        self.latki = [
            mock.patch.object(sejf, "_sejfy", lambda: [("B&C", "Sejf testowy", self.sejf)]),
            mock.patch.object(zapis, "dzis", lambda: DZIS),
            mock.patch.object(zapis, "_plik_stanu", lambda: os.path.join(self.tmp, "zapis_sejfu.json")),
            mock.patch.object(rdzen, "log", lambda *a: None),
            mock.patch.object(raporty, "lista_raportow", lambda: [
                {"id": "r1", "tytul": "BONK etap 3: zamach", "kto": "Claude", "czas": "2026-11-19T10:00:00+01:00",
                 "status": "czeka", "rodzaj": "wdrozenie", "zrzuty": []},
                {"id": "r2", "tytul": "BONKERS — inna gra", "status": "czeka"},
                {"id": "r3", "tytul": "Sejf: BONK w tytule, ale nie na początku", "status": "czeka"},
                {"id": "r4", "tytul": "🎮 bonk game: miniatury", "status": "zaakceptowane"}]),
        ]
        for l in self.latki:
            l.start()
        sejf.uniewaznij()
        zapis._limity.clear()
        zapis._posprzatane.clear()

    def tearDown(self):
        for l in reversed(self.latki):
            l.stop()
        sejf.uniewaznij()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def plik(self, *czesci):
        with open(os.path.join(self.sejf, *czesci), encoding="utf-8", newline="") as f:
            return f.read()

    def wersja(self, nazwa):
        with open(os.path.join(self.sejf, "Wytwórnia", "Pomysły", nazwa + ".md"), "rb") as f:
            return sejf.wersja_bajtow(f.read())

    def assertBlad(self, status, fn, *a, **kw):
        with self.assertRaises(BladHTTP) as k:
            fn(*a, **kw)
        self.assertEqual(k.exception.status, status, k.exception.komunikat)
        return k.exception


class TestCzytanie(Baza):
    def test_lista_i_lejek(self):
        d = wytwornia.lista()
        self.assertTrue(d["jest"])
        po_id = {p["id"]: p for p in d["pomysly"]}
        self.assertEqual(set(po_id), {"BONK", "Ring Potworów", "Stary pomysł"})
        b = po_id["BONK"]
        self.assertEqual((b["nazwa"], b["etap"], b["werdykt_agenta"], b["ocena_agenta"]), ("BONK", "prototyp", "buduj", 17))
        self.assertEqual(b["zdanie"], "Bonk monsters into the sky and race your friends.")
        self.assertEqual(b["metryki"], {"d1": 12, "d7": None, "sesja_min": "6.5", "ccu": None})
        self.assertEqual(b["miejsce"], "92789057272917")
        self.assertIsNone(b["ocena_karol"])
        r = po_id["Ring Potworów"]
        self.assertEqual((r["etap"], r["werdykt_agenta"]), ("ocena", "popraw"))
        self.assertEqual((r["ocena_agenta"], r["ocena_karol"]), (3, 1))           # bez pól we frontmatterze: z tabeli
        self.assertEqual(r["zdanie"], "Potwory walczą na ringu, a gracze obstawiają.")
        self.assertEqual(po_id["Stary pomysł"]["etap"], "porzucona")               # „porzucony” też pasuje
        self.assertEqual(d["lejek"]["prototyp"], ["BONK"])
        self.assertEqual(d["lejek"]["ocena"], ["Ring Potworów"])
        self.assertEqual(d["lejek"]["porzucona"], ["Stary pomysł"])
        self.assertEqual(d["gry"], ["BONK"])
        self.assertEqual(d["etapy_lejka"], ["pomysł", "ocena", "prototyp", "test", "publiczna"])
        self.assertTrue(d["pliki"]["szablon_jest"])

    def test_szczegol_karta_oceny(self):
        p = wytwornia.szczegol("BONK")
        self.assertEqual([w["kryterium"] for w in p["karta"]], list(wytwornia.KRYTERIA))
        self.assertEqual([w["agent"] for w in p["karta"]], [3, 2, 2, 1, 2, 1, 3, 1, 1, 1])
        self.assertEqual(p["sumy"], {"agent": 17, "karol": None, "pawel": None})
        self.assertEqual(p["krytyka_md"], "Za mało powodu do powrotu.")
        self.assertRegex(p["wersja"], r"^[0-9a-f]{16}$")
        self.assertIn("Hak ciekawości", [s["tytul"] for s in p["sekcje"]])
        self.assertTrue(p["sciezka"].endswith("Wytwórnia/Pomysły/BONK.md"))
        self.assertEqual(wytwornia.szczegol("bonk")["id"], "BONK")                 # bez wielkości liter
        self.assertBlad(404, wytwornia.szczegol, "Nie ma")
        for zle in ("../Produkcja/Zadania", "a/b", "..", ".ukryty", ""):
            self.assertBlad(400, wytwornia.szczegol, zle)

    def test_radar_i_kryteria(self):
        r = wytwornia.radar()
        self.assertEqual(r["aktualizacja"], "2026-11-20")
        self.assertEqual([p["trend"] for p in r["pozycje"]], ["Brainrot", "Tower defense"])
        self.assertEqual(r["pozycje"][0]["sila"], "5/5")
        self.assertEqual(r["pozycje"][1]["kierunek"], "spada")
        self.assertIn("[[BONK]]", r["pozycje"][0]["przyklady"])
        k = {x["nazwa"]: x["opis"] for x in wytwornia.kryteria()}
        self.assertEqual(len(k), 10)
        self.assertEqual(k["Jedno zdanie"], "Czy da się opowiedzieć grę jednym zdaniem.")
        self.assertEqual(k["Trend"], "czy gra trafia w to, co teraz rośnie.")
        self.assertEqual(k["Koszt dla nas"], "")

    def test_etapy(self):
        for surowy, oczekiwany in (("Pomysł", "pomysł"), ("pomysl", "pomysł"), ("PUBLICZNY", "publiczna"),
                                   ("wstrzymany", "wstrzymana"), ("", "pomysł"), (None, "pomysł"), ("xyz", "pomysł")):
            self.assertEqual(wytwornia.etap(surowy), oczekiwany, surowy)

    def test_pulpit_gry(self):
        g = wytwornia.pulpit_gry("BONK")
        self.assertEqual(g["nazwy"], ["BONK", "Bonk Game"])
        self.assertEqual([r["id"] for r in g["raporty"]], ["r1", "r4"])            # tytuł ZACZYNA SIĘ od nazwy
        self.assertEqual([z["tekst_md"] for z in g["zadania"]], ["BONK: poprawić zamach pałką", "Ikona BONK gotowa"])
        self.assertEqual(g["zadania"][0]["sekcja"], "🔥 Teraz")
        self.assertEqual([d["id"] for d in g["decyzje"]], ["D-112", "D-113"])      # D-113 wspomina „BONK”
        self.assertTrue(g["regula"])


class TestDodaj(Baza):
    def test_nowy_pomysl_z_szablonu_i_dziennik(self):
        w = wytwornia.dodaj_pomysl("Kosmiczny Kurier", "Dostarczasz paczki: między planetami?", "Co jest w paczce?",
                                   "Paweł", zapis.ZNACZNIK_GOSCIA)
        self.assertTrue(w["ok"])
        self.assertEqual(w["id"], "Kosmiczny Kurier")
        t = self.plik("Wytwórnia", "Pomysły", "Kosmiczny Kurier.md")
        fm, tresc, _ = sejf.parsuj_frontmatter(t)
        self.assertEqual((fm["gra"], fm["etap"], fm["status"], fm["typ"]), ("Kosmiczny Kurier", "pomysł", "propozycja", "pomysł-gry"))
        self.assertEqual(fm["zdanie"], "Dostarczasz paczki: między planetami?")
        self.assertIsNone(fm["ocena_agenta"])                                       # przykład z szablonu wyczyszczony
        self.assertIsNone(fm["werdykt_agenta"])
        self.assertIn("# Kosmiczny Kurier\n", tresc)
        self.assertIn("## W jednym zdaniu\nDostarczasz paczki: między planetami?\n\n## Pierwsze 10 sekund", tresc)
        self.assertNotIn("> Jedno zdanie: kto", tresc)                              # podpowiedź zastąpiona
        self.assertIn("## Hak ciekawości\nCo jest w paczce?\n\n## Karta oceny", tresc)
        self.assertIn("| Koszt dla nas |  |  |  |", tresc)
        dz = self.plik("Produkcja", "Dziennik zmian.md")
        self.assertIn("## %s · Panel (ludzie)\n- Paweł (gość panelu): nowy pomysł w Wytwórni: Kosmiczny Kurier "
                      "([[Kosmiczny Kurier]])\n" % DZIS, dz)
        # nowy pomysł od razu w lejku
        self.assertEqual(wytwornia.lista()["lejek"]["pomysł"], ["Kosmiczny Kurier"])
        # ślad dla „Wyślij”: plik nowy (baza None), w HEAD go nie ma → idzie do commita
        repo = self.tmp
        sciezki, opisy, uwagi = zapis.do_wyslania(repo, lambda argumenty, r: (128, "", "brak"))
        self.assertIn("sejf/Wytwórnia/Pomysły/Kosmiczny Kurier.md", sciezki)
        self.assertIn("nowy pomysł w Wytwórni: Kosmiczny Kurier", opisy)
        self.assertFalse([u for u in uwagi if "Wytwórnia" in u], uwagi)   # (Dziennik: atrapa gita nie zna HEAD)

    def test_powtorka_i_zle_nazwy(self):
        e = self.assertBlad(409, wytwornia.dodaj_pomysl, "bonk", "Zdanie.", "", "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "juz_istnieje")
        for zla in ("a/b", "..", "CON", "Nazwa?", "[[Link]]", "", "x" * 61, "# Nagłówek"):
            self.assertBlad(400, wytwornia.dodaj_pomysl, zla, "Zdanie.", "", "Karol")
        self.assertBlad(400, wytwornia.dodaj_pomysl, "Dobra nazwa", "", "", "Karol")      # zdanie wymagane
        self.assertFalse(os.path.exists(os.path.join(self.sejf, "Wytwórnia", "Pomysły", "Dobra nazwa.md")))


class TestDodajBezSzablonu(Baza):
    szablon = False

    def test_wbudowany_szablon(self):
        wytwornia.dodaj_pomysl("Ring 2", "Krótko.", "", "Karol")
        t = self.plik("Wytwórnia", "Pomysły", "Ring 2.md")
        fm, tresc, _ = sejf.parsuj_frontmatter(t)
        self.assertEqual((fm["gra"], fm["etap"], fm["zdanie"]), ("Ring 2", "pomysł", "Krótko."))
        self.assertIn("## W jednym zdaniu\nKrótko.\n", tresc)
        self.assertEqual(len(wytwornia.szczegol("Ring 2")["karta"]), 10)
        self.assertIn("- Karol: nowy pomysł w Wytwórni: Ring 2 ([[Ring 2]])", self.plik("Produkcja", "Dziennik zmian.md"))


class TestOcenaIEtap(Baza):
    def test_ocena_karola_bajt_w_bajt(self):
        przed = self.plik("Wytwórnia", "Pomysły", "BONK.md")
        oceny = [3, 2, 2, 2, 1, 1, 3, 2, 1, 0]
        w = wytwornia.ocen("BONK", oceny, self.wersja("BONK"), "Karol")
        self.assertEqual(w["pomysl"]["ocena_karol"], 17)
        po = self.plik("Wytwórnia", "Pomysły", "BONK.md")
        oczekiwany = przed.replace("ocena_karol:\n", "ocena_karol: 17\n")
        for k, v in zip(wytwornia.KRYTERIA, oceny):
            stary = [l for l in przed.split("\n") if l.startswith("| %s |" % k)][0]
            agent = stary.split("|")[2]
            oczekiwany = oczekiwany.replace(stary, "| %s |%s| %d |  |" % (k, agent, v))
        self.assertEqual(po, oczekiwany)
        self.assertEqual([x["karol"] for x in w["pomysl"]["karta"]], oceny)
        self.assertEqual([x["agent"] for x in w["pomysl"]["karta"]], [3, 2, 2, 1, 2, 1, 3, 1, 1, 1])   # agent bez zmian
        self.assertIn("- Karol: ocena pomysłu BONK (Karol): 17/30 ([[BONK]])", self.plik("Produkcja", "Dziennik zmian.md"))
        # druga ocena Pawła z kluczem zatwierdzania, z pustym kryterium
        w = wytwornia.ocen("BONK", [1] * 9 + [None], self.wersja("BONK"), "Paweł", zapis.ZNACZNIK_ZATWIERDZANIA)
        self.assertEqual((w["pomysl"]["ocena_pawel"], w["pomysl"]["ocena_karol"]), (9, 17))
        self.assertIn("- Paweł (klucz zatwierdzania): ocena pomysłu BONK (Paweł): 9/30, 9 z 10 kryteriów ([[BONK]])",
                      self.plik("Produkcja", "Dziennik zmian.md"))

    def test_ocena_dopisuje_brakujace_wiersze(self):
        w = wytwornia.ocen("Ring Potworów", [2] * 10, self.wersja("Ring Potworów"), "Paweł")
        karta = w["pomysl"]["karta"]
        self.assertEqual([x["pawel"] for x in karta], [2] * 10)
        self.assertEqual(karta[0]["karol"], 1)                                      # cudza kolumna bez zmian
        self.assertEqual(w["pomysl"]["ocena_pawel"], 20)

    def test_ocena_zle_dane_i_konflikt(self):
        v = self.wersja("BONK")
        self.assertBlad(400, wytwornia.ocen, "BONK", [1] * 9, v, "Karol")
        self.assertBlad(400, wytwornia.ocen, "BONK", [4] + [1] * 9, v, "Karol")
        self.assertBlad(400, wytwornia.ocen, "BONK", [True] + [1] * 9, v, "Karol")
        e = self.assertBlad(403, wytwornia.ocen, "BONK", [1] * 10, v, "Zenek")
        self.assertEqual(e.dodatkowe.get("kod"), "spoza_zespolu")
        e = self.assertBlad(409, wytwornia.ocen, "BONK", [1] * 10, "0" * 16, "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_wersji")
        self.assertEqual(self.plik("Wytwórnia", "Pomysły", "BONK.md"), BONK)

    def test_etap(self):
        w = wytwornia.zmien_etap("BONK", "test", self.wersja("BONK"), "Karol")
        self.assertEqual(w["pomysl"]["etap"], "test")
        self.assertEqual(self.plik("Wytwórnia", "Pomysły", "BONK.md"), BONK.replace("etap: prototyp\n", "etap: test\n"))
        self.assertIn("- Karol: etap pomysłu BONK: prototyp → test ([[BONK]])", self.plik("Produkcja", "Dziennik zmian.md"))
        self.assertBlad(409, wytwornia.zmien_etap, "BONK", "test", self.wersja("BONK"), "Karol")
        self.assertBlad(400, wytwornia.zmien_etap, "BONK", "gotowe", self.wersja("BONK"), "Karol")
        self.assertEqual(wytwornia.lista()["gry"], ["BONK"])

    def test_zapis_tylko_w_wytworni(self):
        cel = os.path.join(self.sejf, "Produkcja", "Zadania.md")
        self.assertBlad(403, zapis.wykonaj_plik, cel, "x", "Zadania", "0" * 16, lambda d: "x", "Karol")
        self.assertBlad(403, zapis.utworz_plik, os.path.join(self.sejf, "Inne.md"), "x", "Inne", b"x", "x", "Karol")


class TestPrawdziweNotatki(Baza):
    """Kopie prawdziwych notatek z sejfu (testy/dane_wytwornia/) — format pisany przez agenta i ręcznie."""
    prawdziwe = True

    def test_pomysl_z_badania(self):
        p = wytwornia.szczegol("Monster Evolution")
        self.assertEqual((p["etap"], p["ocena_agenta"], p["werdykt_agenta"]), ("ocena", 26, "popraw"))
        self.assertEqual(p["zdanie"], "Start as a tiny slime, eat smaller monsters, evolve into a giant beast.")
        self.assertEqual([w["kryterium"] for w in p["karta"]], list(wytwornia.KRYTERIA))
        self.assertTrue(all(w["agent"] is not None for w in p["karta"]), p["karta"])
        self.assertEqual(p["sumy"]["agent"], 26)
        self.assertIsNone(p["sumy"]["karol"])
        tytuly = [s["tytul"] for s in p["sekcje"]]
        for t in ("W jednym zdaniu", "Hak ciekawości", "Monetyzacja", "Karta oceny", "Krytyka agenta", "Najtańszy test"):
            self.assertIn(t, tytuly)
        self.assertTrue(p["krytyka_md"])
        self.assertTrue(all(v is None for v in p["metryki"].values()))           # puste pola „d1:” = brak danych

    def test_lejek_i_gra_bc(self):
        d = wytwornia.lista()
        self.assertIn("Monster Evolution", d["lejek"]["ocena"])
        po = {p["id"]: p for p in d["pomysly"]}
        bc = po["Blocky & Crycket"]
        self.assertEqual((bc["etap"], bc["miejsce"], bc["aliasy"]), ("prototyp", "129485428021967", ["B&C", "Blocky&Crycket"]))
        self.assertIn("Blocky & Crycket", d["gry"])
        self.assertEqual(wytwornia.nazwy_gry(bc), ["Blocky & Crycket", "B&C", "Blocky&Crycket"])

    def test_radar_i_kryteria(self):
        r = wytwornia.radar()
        self.assertEqual(r["aktualizacja"], "2026-11-20")
        self.assertGreaterEqual(len(r["pozycje"]), 10)
        self.assertIn("Kradzież", r["pozycje"][0]["trend"])
        self.assertTrue(all(p["trend"] and p["sila"] for p in r["pozycje"]), r["pozycje"])
        k = wytwornia.kryteria()
        self.assertEqual(len(k), 10)
        self.assertTrue(all(x["opis"] for x in k), k)
        self.assertEqual(k[0]["opis"], "Czy z tytułu i miniatury wiadomo, o co chodzi?")
        self.assertEqual(k[0]["skala"], {"0": "trzeba tłumaczyć", "3": "„aha” w sekundę"})
        self.assertIn("Radar trendów", k[8]["opis"])                              # wikilink jako zwykły tekst

    def test_ocena_prawdziwej_tabeli(self):
        przed = self.plik("Wytwórnia", "Pomysły", "Monster Evolution.md")
        w = wytwornia.ocen("Monster Evolution", [2] * 10, self.wersja("Monster Evolution"), "Paweł")
        po = self.plik("Wytwórnia", "Pomysły", "Monster Evolution.md")
        self.assertEqual(w["pomysl"]["ocena_pawel"], 20)
        self.assertEqual([x["pawel"] for x in w["pomysl"]["karta"]], [2] * 10)
        self.assertIn("| Jedno zdanie | 3 | | 2 |", po)
        self.assertEqual(po.count("\n"), przed.count("\n"))                       # żadnych nowych wierszy
        self.assertEqual(po.replace("ocena_pawel: 20\n", "ocena_pawel:\n").replace(" | 2 |\n", " | |\n"), przed)


class TestWytworniaAPI(test_api.SerwerTestowy):
    """Trasy Wytwórni na prawdziwym serwerze z tymczasowym sejfem."""

    @classmethod
    def konfiguracja_lokalna(cls):
        cls.sejf = os.path.join(cls.tmp, "sejf")
        return {"gra": {"universeId": None}, "sejfy": [{"id": "B&C", "nazwa": "Sejf testowy", "sciezka": cls.sejf}]}

    @classmethod
    def przygotuj(cls, runtime):
        zbuduj_sejf(cls.sejf, prawdziwe=True)

    def wersja(self, ident):
        s, o, _ = self.get("/api/wytwornia/pomysly/" + urllib_quote(ident))
        self.assertEqual(s, 200, o)
        return o["wersja"]

    def test_odczyt(self):
        s, o, _ = self.get("/api/wytwornia")
        self.assertEqual(s, 200, o)
        self.assertIn("BONK", o["gry"])                                           # (inny test przenosi Ring do prototypu)
        self.assertEqual(len(o["kryteria"]), 10)
        self.assertEqual(o["radar"]["aktualizacja"], "2026-11-20")
        s, o, _ = self.get("/api/wytwornia/pomysly/" + urllib_quote("Ring Potworów"))
        self.assertEqual(s, 200, o)
        self.assertIn(o["etap"], ("ocena", "prototyp"))
        s, o, _ = self.get("/api/wytwornia/gry/BONK")
        self.assertEqual(s, 200, o)
        self.assertEqual([d["id"] for d in o["decyzje"]], ["D-112", "D-113"])
        self.assertBlad(self.get("/api/wytwornia/pomysly/" + urllib_quote("Nie ma")), 404)
        s, o, _ = self.get("/api/wytwornia", zdalny=True)                         # gość czyta
        self.assertEqual(s, 200)
        s, o, _ = self.get("/api/zdrowie")
        self.assertTrue(o["moduly"]["wytwornia"]["ok"], o["moduly"].get("wytwornia"))

    def test_gosc_dodaje_ale_nie_ocenia(self):
        s, o, _ = self.post("/api/wytwornia/pomysly", {"nazwa": "Pomysł z telefonu", "zdanie": "Gramy w berka."},
                            zdalny=True, kto="Paweł")
        self.assertEqual(s, 201, o)
        with open(os.path.join(self.sejf, "Produkcja", "Dziennik zmian.md"), encoding="utf-8") as f:
            self.assertIn("- Paweł (gość panelu): nowy pomysł w Wytwórni: Pomysł z telefonu ([[Pomysł z telefonu]])", f.read())
        v = self.wersja("BONK")
        s, o, _ = self.post("/api/wytwornia/pomysly/BONK/ocena", {"oceny": [1] * 10, "wersja": v}, zdalny=True, kto="Paweł")
        self.assertEqual((s, o.get("kod")), (403, "brak_klucza_zatwierdzania"), o)
        s, o, _ = self.post("/api/wytwornia/pomysly/BONK/etap", {"etap": "test", "wersja": v}, zdalny=True, kto="Paweł")
        self.assertEqual((s, o.get("kod")), (403, "brak_klucza_zatwierdzania"), o)
        self.assertEqual(self.wersja("BONK"), v)                                    # nic się nie zmieniło
        self.assertBlad(self.post("/api/wytwornia/pomysly", {"nazwa": "X", "zdanie": "Y", "inne": 1}, zdalny=True), 400)

    def test_ocena_i_etap_przy_komputerze(self):
        # bez imienia z Ustawień: 400 (kolumna oceny to imię osoby)
        v = self.wersja("Ring Potworów")
        s, o, _ = self.post("/api/wytwornia/pomysly/" + urllib_quote("Ring Potworów") + "/ocena", {"oceny": [1] * 10, "wersja": v})
        self.assertEqual((s, o.get("kod")), (400, "brak_imienia"), o)
        s, o, _ = self.post("/api/wytwornia/pomysly/" + urllib_quote("Ring Potworów") + "/ocena",
                            {"oceny": [2] * 10, "wersja": v}, kto="Karol")
        self.assertEqual(s, 200, o)
        self.assertEqual(o["pomysl"]["ocena_karol"], 20)
        s, o, _ = self.post("/api/wytwornia/pomysly/" + urllib_quote("Ring Potworów") + "/etap",
                            {"etap": "prototyp", "wersja": o["wersja"]}, kto="Karol")
        self.assertEqual((s, o["pomysl"]["etap"]), (200, "prototyp"), o)
        s, o, _ = self.get("/api/wytwornia")
        self.assertIn("Ring Potworów", o["gry"])


def urllib_quote(s):
    import urllib.parse
    return urllib.parse.quote(s, safe="")


if __name__ == "__main__":
    unittest.main()
