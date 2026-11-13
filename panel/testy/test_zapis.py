# -*- coding: utf-8 -*-
"""Testy pracy na sejfie z panelu (bc/zapis.py) — wyłącznie na plikach w katalogach tymczasowych.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_zapis

Każda operacja jest sprawdzana bajt w bajt: plik po zmianie musi być DOKŁADNIE oryginałem z jedną oczekiwaną zmianą
(końce linii LF i CRLF, BOM, brak końca linii na końcu pliku). Do tego konflikt wersji, złe dane, próby wstrzyknięcia
struktury Markdown, uprawnienia (gość, osoba przy komputerze bez klucza GD, Game Director), przejścia statusów
decyzji, Dziennik zmian i ślad dla przycisku „Wyślij” na tymczasowym repozytorium git.
Prawdziwy sejf B&C/ jest tylko czytany (test, że podział na linie jest bezstratny).
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PANEL not in sys.path:
    sys.path.insert(0, PANEL)
# Katalogi zastępcze ustawia testy/__init__.py (importowany przed tym plikiem — także przy `unittest discover`).

import threading  # noqa: E402
import time  # noqa: E402

from bc import gitsync, rdzen, sejf, zapis  # noqa: E402
from bc.http import Zadanie  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402

DZIS = "2026-11-13"

PYTANIA = """---
status: do-decyzji
---
# Pytania otwarte

Odpowiedź dopisz pod pytaniem.

## 1. Pierwsze
Treść pierwszego.
**Odpowiedź:** Już jest.

## 2. Drugie pytanie
Treść drugiego.
**Odpowiedź:**

## 3. Bez wiersza odpowiedzi
Tylko treść.

## 4. Ostatnie
Treść czwartego.
**Odpowiedź:**"""                                              # celowo bez końca linii na końcu pliku

ZADANIA = """---
status: kanon
---
# Zadania

> Format: `- [ ] Zadanie · #priorytet`.

## 🔥 Teraz (Sprint 1)
- [ ] Pierwsze zadanie · #wysoki
- [ ] Drugie [[Notatka]] · #średni
  - [ ] Podzadanie drugiego

## 📥 Backlog
- [ ] Coś na później · #niski

## 🎨 Assety do stworzenia
- [ ] Rycerz (3D) · [ ] Kot-Mag (3D)
- [x] Ikona Złota · [ ] Ramka

## ✅ Zrobione
- [x] 2026-11-12: Stare zadanie
"""

DECYZJE = """---
status: kanon
---
# Rejestr decyzji

Statusy: ✅ zatwierdzona · 🕓 do decyzji · 💡 propozycja

---

### D-001 Zatwierdzona
✅ zatwierdzona · styl · źródło: dokumentacja
Opis pierwszej.

### D-002 Propozycja z linkiem
💡 propozycja · game design · 2026-11-13 · źródło: [[Notatka]]
Opis drugiej.
Powiązane: [[Inna]]

### D-003 Do decyzji
🕓 do decyzji · technika · zaproponował: Claude Code
Opis trzeciej.

### D-004 Zastąpiona
♻️ zastąpiona · styl
Opis.

### D-005 Ostatnia
💡 propozycja · narzędzia
Opis ostatniej.

---
*Stopka rejestru.*
"""

DZIENNIK = """---
status: kanon
---
# Dziennik zmian

Najnowsze na górze.

## 2026-11-12 · Claude Code (coś)
- Punkt.
"""

PLIKI = {"pytania": ("Pytania otwarte.md", PYTANIA), "zadania": ("Zadania.md", ZADANIA),
         "decyzje": ("Rejestr decyzji.md", DECYZJE), "dziennik": ("Dziennik zmian.md", DZIENNIK)}


def wstaw_po(tekst, kotwica, nowe):
    """Oczekiwany tekst (LF): `nowe` linie wstawione za linią równą `kotwica` (dokładnie jedna taka linia)."""
    linie = tekst.split("\n")
    self_i = [i for i, l in enumerate(linie) if l == kotwica]
    assert len(self_i) == 1, (kotwica, self_i)
    i = self_i[0]
    return "\n".join(linie[:i + 1] + list(nowe) + linie[i + 1:])


def zamien_linie(tekst, stara, nowa):
    assert tekst.count("\n" + stara + "\n") == 1, stara
    return tekst.replace("\n" + stara + "\n", "\n" + nowa + "\n")


def usun_linie(tekst, linia):
    assert tekst.count("\n" + linia + "\n") == 1, linia
    return tekst.replace("\n" + linia + "\n", "\n")


class Baza(unittest.TestCase):
    nl = "\n"
    bom = False

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_zapis_")
        self.sejf = os.path.join(self.tmp, "sejf")
        os.makedirs(os.path.join(self.sejf, "Produkcja"))
        self.zapisz_pliki()
        self.latki = [
            mock.patch.object(sejf, "_sejfy", lambda: [("B&C", "Sejf testowy", self.sejf)]),
            mock.patch.object(zapis, "dzis", lambda: DZIS),
            mock.patch.object(zapis, "_plik_stanu", lambda: os.path.join(self.tmp, "zapis_sejfu.json")),
            mock.patch.object(rdzen, "log", lambda *a: None),
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
        zapis._limity.clear()
        shutil.rmtree(self.tmp, ignore_errors=True)

    # --- pliki
    def kodu(self, tekst):
        return (b"\xef\xbb\xbf" if self.bom else b"") + tekst.replace("\n", self.nl).encode("utf-8")

    def zapisz_pliki(self, **podmiany):
        for klucz, (nazwa, tekst) in PLIKI.items():
            with open(os.path.join(self.sejf, "Produkcja", nazwa), "wb") as f:
                f.write(self.kodu(podmiany.get(klucz, tekst)))

    def bajty(self, klucz):
        with open(os.path.join(self.sejf, "Produkcja", PLIKI[klucz][0]), "rb") as f:
            return f.read()

    def wersja(self, klucz):
        return sejf.wersja_bajtow(self.bajty(klucz))

    def assertPlik(self, klucz, oczekiwany_tekst):
        self.assertEqual(self.bajty(klucz), self.kodu(oczekiwany_tekst))

    def assertBlad(self, status, fn, *a, **kw):
        with self.assertRaises(BladHTTP) as k:
            fn(*a, **kw)
        self.assertEqual(k.exception.status, status, k.exception.komunikat)
        self.assertTrue(k.exception.komunikat)
        return k.exception


# =========================================================================== operacje (LF)
class TestOperacje(Baza):
    def test_odpowiedz_pod_wierszem_odpowiedzi(self):
        w = zapis.odpowiedz(2, "Tak, zgoda.", self.wersja("pytania"), "Paweł")
        self.assertTrue(w["ok"])
        self.assertEqual(w["opis"], "odpowiedź na pytanie 2")
        oczek = PYTANIA.replace("Treść drugiego.\n**Odpowiedź:**\n", "Treść drugiego.\n**Odpowiedź:**\n- Paweł (%s): Tak, zgoda.\n" % DZIS)
        self.assertPlik("pytania", oczek)
        # druga odpowiedź = kolejny wiersz pod pierwszą; nic innego się nie rusza
        zapis.odpowiedz(2, "A ja dopiszę.", self.wersja("pytania"), "Karol")
        oczek = oczek.replace("- Paweł (%s): Tak, zgoda.\n" % DZIS,
                              "- Paweł (%s): Tak, zgoda.\n- Karol (%s): A ja dopiszę.\n" % (DZIS, DZIS))
        self.assertPlik("pytania", oczek)
        # plan od razu widzi zmianę (pamięć unieważniona), pytanie nie jest już otwarte
        p = {x["nr"]: x for x in sejf.plan()["pytania"]}
        self.assertFalse(p[2]["otwarte"])
        self.assertIn("Karol (%s): A ja dopiszę." % DZIS, p[2]["odpowiedz_md"])
        self.assertEqual(w["plan"]["wersje"]["pytania"], sejf.wersja_bajtow(self.kodu(
            PYTANIA.replace("**Odpowiedź:**\n\n## 3", "**Odpowiedź:**\n- Paweł (%s): Tak, zgoda.\n\n## 3" % DZIS))))

    def test_odpowiedz_inne_przypadki(self):
        zapis.odpowiedz(1, "Druga opinia", self.wersja("pytania"), "Karol")       # odpowiedź w tej samej linii
        oczek = wstaw_po(PYTANIA, "**Odpowiedź:** Już jest.", ["- Karol (%s): Druga opinia" % DZIS])
        self.assertPlik("pytania", oczek)
        zapis.odpowiedz(3, "Nowa", self.wersja("pytania"), "Karol")               # brak wiersza „**Odpowiedź:**”
        oczek = wstaw_po(oczek, "Tylko treść.", ["**Odpowiedź:**", "- Karol (%s): Nowa" % DZIS])
        self.assertPlik("pytania", oczek)
        zapis.odpowiedz(4, "Na końcu pliku", self.wersja("pytania"), "Karol")     # ostatnia linia bez końca linii
        oczek = oczek + "\n- Karol (%s): Na końcu pliku\n" % DZIS
        self.assertPlik("pytania", oczek)
        self.assertBlad(404, zapis.odpowiedz, 99, "x", self.wersja("pytania"), "Karol")

    def test_odhacz_z_teraz_do_zrobionych(self):
        poz = next(p for s in sejf.plan()["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Pierwsze zadanie")
        w = zapis.odhacz(poz["id"], None, self.wersja("zadania"), "Karol")
        self.assertEqual(w["opis"], "odhaczone zadanie: Pierwsze zadanie")
        oczek = usun_linie(ZADANIA, "- [ ] Pierwsze zadanie · #wysoki")
        oczek = wstaw_po(oczek, "## ✅ Zrobione", ["- [x] %s: Pierwsze zadanie" % DZIS])
        self.assertPlik("zadania", oczek)
        # zadanie z otwartym podzadaniem nie idzie do „Zrobione” (tam liczyłoby się dalej jako otwarte)
        przed = self.bajty("zadania")
        e = self.assertBlad(409, zapis.odhacz, None, "Drugie [[Notatka]] · #średni", self.wersja("zadania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "otwarte_podzadania")
        self.assertIn("Podzadanie drugiego", e.komunikat)
        self.assertEqual(self.bajty("zadania"), przed)
        zapis.odhacz(None, "Podzadanie drugiego", self.wersja("zadania"), "Karol")
        oczek = zamien_linie(oczek, "  - [ ] Podzadanie drugiego", "  - [x] Podzadanie drugiego")
        # po dokładnym tekście (z priorytetem albo bez); wcięte (odhaczone) podzadanie idzie razem z zadaniem
        zapis.odhacz(None, "Drugie [[Notatka]] · #średni", self.wersja("zadania"), "Karol")
        oczek = usun_linie(oczek, "- [ ] Drugie [[Notatka]] · #średni")
        oczek = usun_linie(oczek, "  - [x] Podzadanie drugiego")
        oczek = wstaw_po(oczek, "## ✅ Zrobione", ["- [x] %s: Drugie [[Notatka]]" % DZIS, "  - [x] Podzadanie drugiego"])
        self.assertPlik("zadania", oczek)
        zapis.odhacz(None, "Coś na później", self.wersja("zadania"), "Karol")      # z Backlogu
        oczek = usun_linie(oczek, "- [ ] Coś na później · #niski")
        oczek = wstaw_po(oczek, "## ✅ Zrobione", ["- [x] %s: Coś na później" % DZIS])
        self.assertPlik("zadania", oczek)
        z = sejf.plan()["zadania"]
        self.assertEqual(z["sekcje"][-1]["pozycje"][0]["tekst_md"], "Coś na później")
        self.assertEqual(z["sekcje"][-1]["pozycje"][0]["data"], DZIS)

    def test_odhacz_w_miejscu(self):
        zapis.odhacz(None, "Kot-Mag (3D)", self.wersja("zadania"), "Karol")        # lista wielopolowa (assety)
        oczek = zamien_linie(ZADANIA, "- [ ] Rycerz (3D) · [ ] Kot-Mag (3D)", "- [ ] Rycerz (3D) · [x] Kot-Mag (3D)")
        self.assertPlik("zadania", oczek)
        poz = next(p for s in sejf.plan()["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Rycerz (3D)")
        zapis.odhacz(poz["id"], None, self.wersja("zadania"), "Karol")
        oczek = zamien_linie(oczek, "- [ ] Rycerz (3D) · [x] Kot-Mag (3D)", "- [x] Rycerz (3D) · [x] Kot-Mag (3D)")
        self.assertPlik("zadania", oczek)
        zapis.odhacz(None, "Podzadanie drugiego", self.wersja("zadania"), "Karol")   # wcięte podzadanie: w miejscu
        oczek = zamien_linie(oczek, "  - [ ] Podzadanie drugiego", "  - [x] Podzadanie drugiego")
        self.assertPlik("zadania", oczek)
        przed = self.bajty("zadania")
        self.assertBlad(409, zapis.odhacz, None, "Ikona Złota", self.wersja("zadania"), "Karol")   # już odhaczone
        self.assertBlad(409, zapis.odhacz, None, "2026-11-12: Stare zadanie", self.wersja("zadania"), "Karol")
        self.assertBlad(404, zapis.odhacz, None, "Nie ma takiego", self.wersja("zadania"), "Karol")
        self.assertBlad(404, zapis.odhacz, "z0123456789", None, self.wersja("zadania"), "Karol")
        self.assertBlad(400, zapis.odhacz, "../zle", None, self.wersja("zadania"), "Karol")
        self.assertBlad(400, zapis.odhacz, None, None, self.wersja("zadania"), "Karol")
        self.assertEqual(self.bajty("zadania"), przed)

    def test_dodaj_zadanie(self):
        w = zapis.dodaj_zadanie("Nowe pilne", "teraz", "wysoki", self.wersja("zadania"), "Karol")
        self.assertEqual(w["opis"], "dodane zadanie: Nowe pilne (Teraz)")
        oczek = wstaw_po(ZADANIA, "  - [ ] Podzadanie drugiego", ["- [ ] Nowe pilne · #wysoki"])
        self.assertPlik("zadania", oczek)
        zapis.dodaj_zadanie("Kiedyś", "backlog", "sredni", self.wersja("zadania"), "Karol")
        oczek = wstaw_po(oczek, "- [ ] Coś na później · #niski", ["- [ ] Kiedyś · #średni"])
        self.assertPlik("zadania", oczek)
        poz = [p for s in sejf.plan()["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Kiedyś"]
        self.assertEqual(poz[0]["priorytet"], "średni")
        przed = self.bajty("zadania")
        for zle in (("x", "zrobione", "wysoki"), ("x", "teraz", "pilny"), ("x", None, "niski"),
                    ("Zadanie · #wysoki", "teraz", "wysoki"), ("Nowe pilne", "backlog", "niski")):
            self.assertBlad(409 if zle[0] == "Nowe pilne" else 400, zapis.dodaj_zadanie, *zle,
                            wersja=self.wersja("zadania"), kto="Karol")
        self.assertEqual(self.bajty("zadania"), przed)

    def test_decyzje_przejscia(self):
        w = zapis.zmien_status_decyzji("D-002", "zatwierdzona", "Prototyp\nnajpierw", self.wersja("decyzje"), "Paweł")
        self.assertEqual(w["opis"], "decyzja D-002 zatwierdzona")
        gd = "Game Director (Paweł)"
        oczek = zamien_linie(DECYZJE, "💡 propozycja · game design · 2026-11-13 · źródło: [[Notatka]]",
                             "✅ zatwierdzona · game design · 2026-11-13 · źródło: [[Notatka]] · zdecydował: %s %s" % (gd, DZIS))
        oczek = wstaw_po(oczek, "Powiązane: [[Inna]]", ["Uzasadnienie — %s, %s: Prototyp / najpierw" % (gd, DZIS)])
        self.assertPlik("decyzje", oczek)
        d = {x["id"]: x for x in sejf.plan()["decyzje"]}
        self.assertEqual((d["D-002"]["status"], d["D-002"]["emoji"], d["D-002"]["kategoria"]), ("zatwierdzona", "✅", "game design"))
        # do decyzji -> odrzucona; propozycja -> do decyzji -> zatwierdzona (podpis nie dubluje się)
        zapis.zmien_status_decyzji("d-3", "odrzucona", None, self.wersja("decyzje"), "Paweł")
        oczek = zamien_linie(oczek, "🕓 do decyzji · technika · zaproponował: Claude Code",
                             "❌ odrzucona · technika · zaproponował: Claude Code · zdecydował: %s %s" % (gd, DZIS))
        self.assertPlik("decyzje", oczek)
        zapis.zmien_status_decyzji("D-005", "do_decyzji", "", self.wersja("decyzje"), "Paweł")
        self.assertIn("🕓 do decyzji · narzędzia · oznaczył: %s %s\n" % (gd, DZIS), self.bajty("decyzje").decode("utf-8-sig").replace("\r\n", "\n"))
        zapis.zmien_status_decyzji("D-005", "zatwierdzona", "Jasne", self.wersja("decyzje"), "Paweł")
        oczek = zamien_linie(oczek, "💡 propozycja · narzędzia", "✅ zatwierdzona · narzędzia · zdecydował: %s %s" % (gd, DZIS))
        oczek = wstaw_po(oczek, "Opis ostatniej.", ["Uzasadnienie — %s, %s: Jasne" % (gd, DZIS)])   # przed „---” i stopką
        self.assertPlik("decyzje", oczek)
        przed = self.bajty("decyzje")
        for ident, status in (("D-001", "odrzucona"), ("D-002", "odrzucona"), ("D-003", "zatwierdzona"),
                              ("D-004", "zatwierdzona"), ("D-005", "zatwierdzona")):
            e = self.assertBlad(409, zapis.zmien_status_decyzji, ident, status, None, self.wersja("decyzje"), "Paweł")
            self.assertEqual(e.dodatkowe.get("kod"), "status_zamkniety")
        self.assertBlad(404, zapis.zmien_status_decyzji, "D-099", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")
        for zle_id, zly_status in (("X-1", "zatwierdzona"), ("D-", "zatwierdzona"), ("D-1/../2", "zatwierdzona"),
                                   ("D-002", "zastapiona"), ("D-002", "propozycja"), ("D-002", None)):
            self.assertBlad(400, zapis.zmien_status_decyzji, zle_id, zly_status, None, self.wersja("decyzje"), "Paweł")
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_ten_sam_status(self):
        przed = self.bajty("decyzje")
        e = self.assertBlad(409, zapis.zmien_status_decyzji, "D-003", "do_decyzji", None, self.wersja("decyzje"), "Paweł")
        self.assertNotEqual(e.dodatkowe.get("kod"), "konflikt_wersji")
        self.assertEqual(self.bajty("decyzje"), przed)

    def test_dziennik(self):
        zapis.odpowiedz(2, "Tak", self.wersja("pytania"), "Paweł")
        pierwszy = "- Paweł: odpowiedź na pytanie 2 ([[Pytania otwarte]])"      # link do notatki, której dotyczy
        oczek = wstaw_po(DZIENNIK, "Najnowsze na górze.", ["", "## %s · Panel (ludzie)" % DZIS, pierwszy])
        self.assertPlik("dziennik", oczek)
        zapis.odhacz(None, "Pierwsze zadanie", self.wersja("zadania"), "Karol", "gość panelu")
        zapis.dodaj_zadanie("Nowe", "backlog", "niski", self.wersja("zadania"), "Karol")
        zapis.zmien_status_decyzji("D-002", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")
        oczek = wstaw_po(oczek, pierwszy, [
            "- Karol (gość panelu): odhaczone zadanie: Pierwsze zadanie ([[Zadania]])",
            "- Karol: dodane zadanie: Nowe (Backlog) ([[Zadania]])",
            "- Paweł (Game Director): decyzja D-002 zatwierdzona ([[Rejestr decyzji]])"])
        self.assertPlik("dziennik", oczek)
        wpis = sejf.plan()["dziennik"][0]
        self.assertEqual((wpis["data"], wpis["kto"], wpis["temat"], len(wpis["punkty_md"])), (DZIS, "Panel", "ludzie", 4))

    def test_dziennik_bez_wpisow_z_data(self):
        self.zapisz_pliki(dziennik="# Dziennik zmian\n\nPusto.")
        zapis.odpowiedz(2, "Tak", self.wersja("pytania"), "Paweł")
        self.assertPlik("dziennik", "# Dziennik zmian\n\nPusto.\n\n## %s · Panel (ludzie)\n"
                                    "- Paweł: odpowiedź na pytanie 2 ([[Pytania otwarte]])\n" % DZIS)

    def test_konflikt_wersji(self):
        stara = self.wersja("pytania")
        zapis.odpowiedz(2, "Pierwszy", stara, "Paweł")
        po_pierwszym = self.bajty("pytania")
        e = self.assertBlad(409, zapis.odpowiedz, 2, "Drugi na starej wersji", stara, "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_wersji")
        self.assertEqual(e.dodatkowe.get("wersja"), sejf.wersja_bajtow(po_pierwszym))
        self.assertEqual(self.bajty("pytania"), po_pierwszym)
        # ręczna edycja w Obsidianie też jest wykrywana
        with open(os.path.join(self.sejf, "Produkcja", "Zadania.md"), "ab") as f:
            f.write(self.kodu("- [ ] dopisane w Obsidianie\n"))
        self.assertBlad(409, zapis.odhacz, None, "Pierwsze zadanie", sejf.wersja_bajtow(self.kodu(ZADANIA)), "Karol")
        for zla in (None, "", 5):
            self.assertBlad(400, zapis.odpowiedz, 2, "x", zla, "Karol")
        dz = self.bajty("dziennik")
        self.assertEqual(dz.count("odpowiedź na pytanie 2".encode("utf-8")), 1)   # nieudane próby bez śladu

    def test_wstrzykniecia_i_zle_dane(self):
        przed = {k: self.bajty(k) for k in PLIKI}
        zle = ["# Nagłówek", "## 5. Nowe pytanie", "###", "- [ ] zadanie", "* [x] zrobione", "[ ] pole", "[x]",
               "**Odpowiedź:** podrobiona", "a ** odpowiedz ** b", "A · [ ] B", "A ·[x] B", "", "   ", "\n\n", "\x00\x1b",
               "x" * (zapis.LIMIT_ODPOWIEDZI + 1), 123, ["lista"]]
        for t in zle:
            self.assertBlad(400, zapis.odpowiedz, 2, t, self.wersja("pytania"), "Karol")
        for t in ("# x", "- [ ] x", "x" * (zapis.LIMIT_ZADANIA + 1), "a · [ ] b"):
            self.assertBlad(400, zapis.dodaj_zadanie, t, "teraz", "wysoki", self.wersja("zadania"), "Karol")
        self.assertBlad(400, zapis.zmien_status_decyzji, "D-002", "zatwierdzona", "## nagłówek", self.wersja("decyzje"), "Paweł")
        self.assertBlad(400, zapis.zmien_status_decyzji, "D-002", "zatwierdzona", "x" * 1001, self.wersja("decyzje"), "Paweł")
        self.assertEqual({k: self.bajty(k) for k in PLIKI}, przed)
        # dozwolone, ale spłaszczone do jednej linii: nowe linie, znaki sterujące, odwracanie kierunku tekstu
        zapis.odpowiedz(2, "  Pierwsza linia\r\n\r\n## Druga\x00\x1b[31m‮odwrócone koniec  ", self.wersja("pytania"), "Karol")
        oczek = PYTANIA.replace("Treść drugiego.\n**Odpowiedź:**\n",
                                "Treść drugiego.\n**Odpowiedź:**\n- Karol (%s): Pierwsza linia / ## Druga[31modwrócone / koniec\n" % DZIS)
        self.assertPlik("pytania", oczek)
        self.assertEqual(len([p for p in sejf.plan()["pytania"] if p["nr"] == 2]), 1)   # żadnego nowego pytania
        # imię nie przemyca formatowania ani struktury
        z = Zadanie("POST", "/", {}, {}, b"", False, "**Odpowiedź:** [[x]] #h\n## y", "1.2.3.4", "h")
        self.assertEqual(zapis.imie(z), "Odpowiedź x h y")
        self.assertEqual(zapis.imie(Zadanie("POST", "/", {}, {}, b"", False, "", "1.2.3.4", "h")), "gość")
        # „·” nie dokleja fałszywego pola do wiersza statusu; nawiasy i przecinki nie podrobią znacznika serwera
        z = Zadanie("POST", "/", {}, {}, b"", False, "Paweł · ♻️ zastąpiona", "1.2.3.4", "h")
        self.assertEqual(zapis.imie(z), "Paweł ♻️ zastąpiona")
        z = Zadanie("POST", "/", {}, {}, b"", False, "Paweł (Game Director, 2026-11-13)", "1.2.3.4", "h")
        self.assertEqual(zapis.imie(z), "Paweł Game Director 2026-11-13")

    def test_skrot_do_dziennika(self):
        self.assertEqual(zapis.skrot("krótki"), "krótki")
        dlugi = "słowo " * 40 + "[[Bardzo długa notatka]]"
        s = zapis.skrot(dlugi, 60)
        self.assertTrue(s.endswith("…") and len(s) <= 60, s)
        s = zapis.skrot("a " * 20 + "[[Długi link do notatki, który się nie zmieści]]", 50)
        self.assertEqual(s.count("[["), s.count("]]"), s)

    def test_wylaczony_zapis_w_konfiguracji(self):
        z = Zadanie("POST", "/api/sejf/zadania/dodaj", {}, {}, json.dumps({"tekst": "x"}).encode(), True, "Karol", "127.0.0.1", "h")
        with mock.patch.object(rdzen, "konfiguracja", lambda: {"zapis_sejfu": False}):
            self.assertBlad(403, zapis._t_dodaj, z)


class TestOperacjeCRLF(TestOperacje):
    nl = "\r\n"


class TestOperacjeBOM(TestOperacje):
    bom = True


class TestPlikMieszany(Baza):
    def test_mieszane_konce_linii(self):
        tekst = PYTANIA.replace("Treść drugiego.\n", "Treść drugiego.\r\n")   # jedna linia CRLF w pliku LF
        self.zapisz_pliki(pytania=tekst)
        zapis.odpowiedz(2, "Tak", self.wersja("pytania"), "Paweł")
        oczek = tekst.replace("**Odpowiedź:**\n\n## 3", "**Odpowiedź:**\n- Paweł (%s): Tak\n\n## 3" % DZIS)
        self.assertPlik("pytania", oczek)

    def test_nie_utf8(self):
        with open(os.path.join(self.sejf, "Produkcja", "Pytania otwarte.md"), "wb") as f:
            f.write("## 2. Pytanie\n**Odpowiedź:**\n".encode("cp1250"))
        przed = self.bajty("pytania")
        self.assertBlad(409, zapis.odpowiedz, 2, "x", self.wersja("pytania"), "Paweł")
        self.assertEqual(self.bajty("pytania"), przed)


# =========================================================================== uprawnienia (trasy)
def _zadanie(cialo, lokalny=False, kto="gość", gd=False, params=None):
    z = Zadanie("POST", "/api/x", {}, {}, json.dumps(cialo).encode("utf-8"), lokalny, kto, "127.0.0.1", "h")
    z.params = params or {}
    z.game_director = gd
    return z


class TestUprawnienia(Baza):
    def test_gosc_odpowiada_i_pracuje_na_zadaniach(self):
        w = zapis._t_odpowiedz(_zadanie({"tekst": "Z tunelu", "wersja": self.wersja("pytania")}, params={"nr": "2"}))
        self.assertTrue(w["ok"])
        self.assertIn("- gość (gość panelu, %s): Z tunelu" % DZIS, self.bajty("pytania").decode("utf-8-sig"))
        w = zapis._t_dodaj(_zadanie({"tekst": "Od gościa", "sekcja": "backlog", "priorytet": "niski",
                                     "wersja": self.wersja("zadania")}, kto="Paweł"))
        self.assertTrue(w["ok"])
        w = zapis._t_odhacz(_zadanie({"tekst": "Od gościa", "wersja": self.wersja("zadania")}, kto="Paweł"))
        self.assertTrue(w["ok"])

    def test_decyzje_tylko_game_director(self):
        przed = self.bajty("decyzje")
        cialo = {"status": "zatwierdzona", "wersja": self.wersja("decyzje")}
        for z in (_zadanie(cialo, params={"id": "D-002"}),                                 # gość z kodem dostępu
                  _zadanie(cialo, lokalny=True, kto="Paweł", params={"id": "D-002"}),       # przy komputerze, bez klucza GD
                  _zadanie(cialo, lokalny=True, kto="Game Director", params={"id": "D-002"})):
            e = self.assertBlad(403, zapis._t_status, z)
            self.assertEqual(e.dodatkowe.get("kod"), "tylko_game_director")
            self.assertIn("--klucz-gd", e.komunikat)
        self.assertEqual(self.bajty("decyzje"), przed)
        w = zapis._t_status(_zadanie(cialo, gd=True, kto="Paweł", params={"id": "D-002"}))   # Game Director (także zdalnie)
        self.assertEqual(w["opis"], "decyzja D-002 zatwierdzona")
        self.assertIn("zdecydował: Game Director (Paweł) %s" % DZIS, self.bajty("decyzje").decode("utf-8"))

    def test_zle_ciala_zadan(self):
        for fn, cialo, params in ((zapis._t_odpowiedz, {"tekst": "x", "wersja": "a", "inne": 1}, {"nr": "2"}),
                                  (zapis._t_odpowiedz, {"tekst": "x", "wersja": "a"}, {"nr": "abc"}),
                                  (zapis._t_odpowiedz, {"tekst": "x", "wersja": "a"}, {"nr": "0"}),
                                  (zapis._t_odpowiedz, {"tekst": "x", "wersja": "a"}, {"nr": "1e3"}),
                                  (zapis._t_odhacz, [1, 2], {}),
                                  (zapis._t_dodaj, "tekst", {})):
            self.assertBlad(400, fn, _zadanie(cialo, params=params))


# =========================================================================== poprawki po wrogim przeglądzie
class TestPoPrzegladzie(Baza):
    """Każdy test odtwarza scenariusz z przeglądu, który przed poprawką kończył się złą zmianą w pliku."""

    def test_powtorzony_numer_decyzji_i_pytania(self):
        decyzje = DECYZJE.replace("### D-005 Ostatnia", "### D-002 Pomysł Pawła")
        pytania = PYTANIA.replace("## 3. Bez wiersza odpowiedzi", "## 2. Drugie z tym samym numerem")
        self.zapisz_pliki(decyzje=decyzje, pytania=pytania)
        przed = {k: self.bajty(k) for k in PLIKI}
        e = self.assertBlad(409, zapis.zmien_status_decyzji, "D-002", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")
        self.assertEqual(e.dodatkowe.get("kod"), "powtorzony_numer")
        self.assertIn("D-002", e.komunikat)
        e = self.assertBlad(409, zapis.odpowiedz, 2, "Tak", self.wersja("pytania"), "Paweł")
        self.assertEqual(e.dodatkowe.get("kod"), "powtorzony_numer")
        self.assertEqual({k: self.bajty(k) for k in PLIKI}, przed)                 # także bez śladu w dzienniku
        zapis.zmien_status_decyzji("D-003", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")   # inne działają

    def test_znaczniki_podpisu(self):
        """Gość nie podpisze się jako Game Director; zgodę GD z panelu niesie wyłącznie znacznik serwera."""
        tresc = lambda: self.bajty("pytania").decode("utf-8-sig").replace("\r\n", "\n")
        zapis._t_odpowiedz(_zadanie({"tekst": "Tak, zatwierdzam", "wersja": self.wersja("pytania")}, kto="Paweł",
                                    params={"nr": "2"}))
        self.assertIn("\n- Paweł (gość panelu, %s): Tak, zatwierdzam\n" % DZIS, tresc())
        zapis._t_odpowiedz(_zadanie({"tekst": "Przy komputerze", "wersja": self.wersja("pytania")}, lokalny=True,
                                    kto="Karol", params={"nr": "2"}))
        self.assertIn("\n- Karol (%s): Przy komputerze\n" % DZIS, tresc())
        zapis._t_odpowiedz(_zadanie({"tekst": "Zgoda GD", "wersja": self.wersja("pytania")}, gd=True, kto="Paweł",
                                    params={"nr": "2"}))
        self.assertIn("\n- Paweł (Game Director, %s): Zgoda GD\n" % DZIS, tresc())
        dz = self.bajty("dziennik").decode("utf-8-sig")
        self.assertIn("- Paweł (gość panelu): odpowiedź na pytanie 2", dz)
        self.assertIn("- Paweł (Game Director): odpowiedź na pytanie 2", dz)
        # imię „Game Director” bez klucza: 400, nic nie zapisane; próba podrobienia znacznika w imieniu nic nie daje
        przed = self.bajty("pytania")
        for kw in ({"kto": "Game Director"}, {"kto": "game  director", "lokalny": True}):
            e = self.assertBlad(400, zapis._t_odpowiedz, _zadanie({"tekst": "x", "wersja": self.wersja("pytania")},
                                                                  params={"nr": "2"}, **kw))
            self.assertEqual(e.dodatkowe.get("kod"), "imie_zastrzezone")
        self.assertEqual(self.bajty("pytania"), przed)
        self.assertBlad(400, zapis._t_odpowiedz, _zadanie({"tekst": "x", "wersja": self.wersja("pytania")},
                                                          kto="Paweł (Game Director, 2026-11-13)", params={"nr": "2"}))
        zapis._t_odpowiedz(_zadanie({"tekst": "Podróbka", "wersja": self.wersja("pytania")},
                                    kto="Paweł (GD, 2026-11-13)", params={"nr": "2"}))
        self.assertIn("\n- Paweł GD 2026-11-13 (gość panelu, %s): Podróbka\n" % DZIS, tresc())

    def test_limit_zapisow_goscia(self):
        for i in range(zapis.LIMIT_ZAPISOW_GOSCIA):
            zapis._t_dodaj(_zadanie({"tekst": "Gość %d" % i, "sekcja": "backlog", "priorytet": "niski",
                                     "wersja": self.wersja("zadania")}))
        przed = self.bajty("zadania")
        e = self.assertBlad(429, zapis._t_dodaj, _zadanie({"tekst": "Za dużo", "sekcja": "backlog", "priorytet": "niski",
                                                            "wersja": self.wersja("zadania")}))
        self.assertEqual(e.dodatkowe.get("kod"), "limit_zapisow")
        self.assertEqual(self.bajty("zadania"), przed)
        # inny klient za tunelem ma własny limit; osoba przy komputerze i Game Director — bez limitu
        z = _zadanie({"tekst": "Inny gość", "sekcja": "backlog", "priorytet": "niski", "wersja": self.wersja("zadania")})
        z.naglowki = {"Cf-Connecting-Ip": "203.0.113.9"}
        self.assertTrue(zapis._t_dodaj(z)["ok"])
        self.assertTrue(zapis._t_dodaj(_zadanie({"tekst": "Karol", "sekcja": "teraz", "priorytet": "niski",
                                                 "wersja": self.wersja("zadania")}, lokalny=True))["ok"])
        self.assertTrue(zapis._t_odpowiedz(_zadanie({"tekst": "GD", "wersja": self.wersja("pytania")}, gd=True,
                                                    params={"nr": "2"}))["ok"])

    def test_powtorzona_odpowiedz(self):
        """Podwójny Ctrl+Enter: druga identyczna odpowiedź tej samej osoby z tego samego dnia to 409, nie duplikat."""
        zapis.odpowiedz(2, "Tak", self.wersja("pytania"), "Paweł")
        po = self.bajty("pytania")
        e = self.assertBlad(409, zapis.odpowiedz, 2, "Tak", self.wersja("pytania"), "Paweł")
        self.assertEqual(e.dodatkowe.get("kod"), "juz_zapisane")
        self.assertEqual(self.bajty("pytania"), po)
        zapis.odpowiedz(2, "Tak", self.wersja("pytania"), "Karol")                 # ktoś inny może napisać to samo

    def test_linia_pozioma_w_tresci_pytania(self):
        self.zapisz_pliki(pytania="# P\n\n## 5. Pytanie\nKontekst.\n---\nWłaściwe pytanie?\n**Odpowiedź:**\n\n## 6. Dalej\nX\n")
        zapis.odpowiedz(5, "Tak", self.wersja("pytania"), "Paweł")
        self.assertPlik("pytania", "# P\n\n## 5. Pytanie\nKontekst.\n---\nWłaściwe pytanie?\n**Odpowiedź:**\n"
                                   "- Paweł (%s): Tak\n\n## 6. Dalej\nX\n" % DZIS)
        p = sejf.plan()["pytania"][0]
        self.assertEqual((p["tresc_md"], p["odpowiedz_md"]), ("Kontekst.\nWłaściwe pytanie?", "- Paweł (%s): Tak" % DZIS))
        # ostatnie pytanie bez wiersza odpowiedzi: --- przed stopką pliku dalej kończy pytanie
        self.zapisz_pliki(pytania="# P\n\n## 7. Ostatnie\nTreść.\n\n---\n*Stopka.*\n")
        zapis.odpowiedz(7, "Ok", self.wersja("pytania"), "Paweł")
        self.assertPlik("pytania", "# P\n\n## 7. Ostatnie\nTreść.\n**Odpowiedź:**\n- Paweł (%s): Ok\n\n---\n*Stopka.*\n" % DZIS)

    def test_blok_kodu_w_odpowiedzi(self):
        self.zapisz_pliki(pytania="# P\n\n## 1. A\nX\n**Odpowiedź:**\n```text\nlinia1\n\nlinia2\n```\n\n## 2. B\nY\n")
        zapis.odpowiedz(1, "Druga odpowiedź", self.wersja("pytania"), "Karol")
        self.assertPlik("pytania", "# P\n\n## 1. A\nX\n**Odpowiedź:**\n```text\nlinia1\n\nlinia2\n```\n"
                                   "- Karol (%s): Druga odpowiedź\n\n## 2. B\nY\n" % DZIS)

    def test_ploty_jak_w_parserze(self):
        """Krótszy płotek wewnątrz dłuższego nie zamyka bloku — tak samo w parserze planu i w zapisie."""
        tekst = "# P\n\n## 1. A\nX\n````md\n```\n## 2. W kodzie\n```\n````\n**Odpowiedź:**\n\n## 3. B\nY\n**Odpowiedź:**\n"
        self.zapisz_pliki(pytania=tekst)
        self.assertEqual([p["nr"] for p in sejf.plan()["pytania"]], [1, 3])
        naglowki = [t for _, poziom, t in zapis.Dokument(self.bajty("pytania")).naglowki() if poziom == 2]
        self.assertEqual(naglowki, ["1. A", "3. B"])
        self.assertBlad(404, zapis.odpowiedz, 2, "x", self.wersja("pytania"), "Karol")
        zapis.odpowiedz(1, "Tak", self.wersja("pytania"), "Karol")
        self.assertIn("````\n**Odpowiedź:**\n- Karol (%s): Tak\n\n## 3. B" % DZIS, self.bajty("pytania").decode("utf-8-sig").replace("\r\n", "\n"))

    def test_samotne_cr_i_znaczniki_konfliktu(self):
        surowe = "# P\r## 1. A\rX\r**Odpowiedź:**\r\n## 2. B\nY\n**Odpowiedź:**\n".encode("utf-8")
        with open(os.path.join(self.sejf, "Produkcja", "Pytania otwarte.md"), "wb") as f:
            f.write(surowe)
        self.assertEqual([p["nr"] for p in sejf.plan()["pytania"]], [1, 2])         # tak widzi to interfejs
        e = self.assertBlad(409, zapis.odpowiedz, 1, "x", self.wersja("pytania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "konce_linii")
        self.assertEqual(self.bajty("pytania"), surowe)
        konflikt = ZADANIA.replace("## 📥 Backlog\n", "## 📥 Backlog\n<<<<<<< Updated upstream\n- [ ] A · #niski\n"
                                                     "=======\n- [ ] B · #niski\n>>>>>>> Stashed changes\n")
        self.zapisz_pliki(zadania=konflikt)
        przed = self.bajty("zadania")
        e = self.assertBlad(409, zapis.dodaj_zadanie, "C", "backlog", "niski", self.wersja("zadania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_gita")
        self.assertEqual(self.bajty("zadania"), przed)

    def test_wiersz_statusu_tylko_status(self):
        dec = DECYZJE.replace("💡 propozycja · narzędzia",
                              "💡 propozycja (wstępna, czeka na test B1) ·  narzędzia  · zaproponował: Karol ")
        self.zapisz_pliki(decyzje=dec)
        zapis.zmien_status_decyzji("D-005", "zatwierdzona", None, self.wersja("decyzje"), "Paweł")
        self.assertPlik("decyzje", dec.replace(
            "💡 propozycja (wstępna, czeka na test B1) ·  narzędzia  · zaproponował: Karol ",
            "✅ zatwierdzona (wstępna, czeka na test B1) ·  narzędzia  · zaproponował: Karol · "
            "zdecydował: Game Director (Paweł) %s " % DZIS))
        d = {x["id"]: x for x in sejf.plan()["decyzje"]}["D-005"]
        self.assertEqual(d["meta"], ["zaproponował: Karol", "zdecydował: Game Director (Paweł) %s" % DZIS])
        # status zapisany samym emoji, pogrubione słowo, GD bez imienia
        dec = DECYZJE.replace("💡 propozycja · narzędzia", "💡 · narzędzia").replace("🕓 do decyzji · technika",
                                                                                     "🕓 **do decyzji** · technika")
        self.zapisz_pliki(decyzje=dec)
        zapis.zmien_status_decyzji("D-005", "do_decyzji", None, self.wersja("decyzje"), "gość")
        zapis.zmien_status_decyzji("D-003", "odrzucona", None, self.wersja("decyzje"), "Paweł")
        tekst = self.bajty("decyzje").decode("utf-8-sig").replace("\r\n", "\n")
        self.assertIn("\n🕓 do decyzji · narzędzia · oznaczył: Game Director %s\n" % DZIS, tekst)
        self.assertIn("\n❌ **odrzucona** · technika · zaproponował: Claude Code · zdecydował: Game Director (Paweł) %s\n"
                      % DZIS, tekst)

    def test_podzadania_i_otwarte_w_zrobionych(self):
        zad = ZADANIA.replace("- [x] 2026-11-12: Stare zadanie\n",
                              "- [x] 2026-11-12: Stare zadanie\n  - [ ] Zostało w Zrobionych\n- [ ] Otwarte w Zrobionych\n")
        self.zapisz_pliki(zadania=zad)
        zapis.odhacz(None, "Zostało w Zrobionych", self.wersja("zadania"), "Karol")
        zapis.odhacz(None, "Otwarte w Zrobionych", self.wersja("zadania"), "Karol")
        oczek = zad.replace("  - [ ] Zostało", "  - [x] Zostało").replace("- [ ] Otwarte w", "- [x] Otwarte w")
        self.assertPlik("zadania", oczek)

    def test_rozpoznawanie_sekcji(self):
        zad = ("# Z\n\n## 🔥 Teraz\n- [ ] A\n\n## ✅ Zrobione (archiwum backlogu)\n- [x] stare\n\n"
               "## 📥 Backlog\n- [ ] B\n")
        self.zapisz_pliki(zadania=zad)
        zapis.dodaj_zadanie("Nowe do backlogu", "backlog", "niski", self.wersja("zadania"), "Karol")
        zapis.odhacz(None, "A", self.wersja("zadania"), "Karol")
        self.assertPlik("zadania", "# Z\n\n## 🔥 Teraz\n\n## ✅ Zrobione (archiwum backlogu)\n- [x] %s: A\n- [x] stare\n\n"
                                   "## 📥 Backlog\n- [ ] B\n- [ ] Nowe do backlogu · #niski\n" % DZIS)
        # dwie sekcje „Zrobione”: 409 zamiast zgadywania
        self.zapisz_pliki(zadania="# Z\n\n## Teraz\n- [ ] A\n\n## Zrobione\n- [x] a\n\n## ✅ Zrobione 2025\n- [x] b\n")
        przed = self.bajty("zadania")
        e = self.assertBlad(409, zapis.odhacz, None, "A", self.wersja("zadania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "powtorzona_sekcja")
        self.assertEqual(self.bajty("zadania"), przed)

    def test_ponowienie_nie_nadpisuje_cudzej_zmiany(self):
        """Plik zablokowany przy pierwszej próbie, bo Obsidian go właśnie zapisuje: 409, a nie nadpisanie wersji B."""
        sciezka = os.path.join(self.sejf, "Produkcja", "Zadania.md")
        prawdziwe = os.replace
        proby = []

        def zablokowany_raz(src, dst):
            if dst == sciezka and not proby:
                proby.append(1)
                with open(sciezka, "ab") as f:                 # „Obsidian” zapisuje wersję B i trzyma uchwyt
                    f.write(self.kodu("- [ ] z Obsidiana\n"))
                raise PermissionError(13, "plik zablokowany")
            return prawdziwe(src, dst)
        with mock.patch.object(zapis.os, "replace", zablokowany_raz), mock.patch.object(zapis.time, "sleep", lambda s: None):
            e = self.assertBlad(409, zapis.dodaj_zadanie, "Z panelu", "teraz", "wysoki", self.wersja("zadania"), "Karol")
        self.assertEqual(e.dodatkowe.get("kod"), "konflikt_wersji")
        tekst = self.bajty("zadania").decode("utf-8-sig")
        self.assertIn("z Obsidiana", tekst)
        self.assertNotIn("Z panelu", tekst)
        self.assertEqual([n for n in os.listdir(os.path.join(self.sejf, "Produkcja")) if n.endswith(".tmp")], [])

    def test_sprzatanie_starych_plikow_tymczasowych(self):
        folder = os.path.join(self.sejf, "Produkcja")
        stary, swiezy, obcy = "Zadania.md.1234.a1b2c3.tmp", "Zadania.md.1234.d4e5f6.tmp", "notatka.tmp"
        for n in (stary, swiezy, obcy):
            with open(os.path.join(folder, n), "wb") as f:
                f.write(b"x")
        godzina_temu = time.time() - 3600
        os.utime(os.path.join(folder, stary), (godzina_temu, godzina_temu))
        os.utime(os.path.join(folder, obcy), (godzina_temu, godzina_temu))
        zapis.odpowiedz(2, "Tak", self.wersja("pytania"), "Karol")
        zostaly = set(os.listdir(folder))
        self.assertNotIn(stary, zostaly)
        self.assertIn(swiezy, zostaly)                         # może to trwający zapis innego procesu
        self.assertIn(obcy, zostaly)                           # nie nasz wzór nazwy

    def test_dane_lokalne_testow_sa_tymczasowe(self):
        """Testy nie mogą czytać ani pisać prawdziwych danych lokalnych komputera (konfiguracja lokalna, ślad)."""
        prawdziwe = os.path.normcase(os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
                                                  "BlockyCrycket"))
        self.assertFalse(os.path.normcase(rdzen.RUNTIME).startswith(prawdziwe), rdzen.RUNTIME)
        self.assertFalse(os.path.normcase(os.path.abspath(rdzen.DANE)).startswith(
            os.path.normcase(os.path.join(rdzen.PANEL, "dane"))), rdzen.DANE)


# =========================================================================== podział na linie: bezstratny na prawdziwym sejfie
class TestDokument(unittest.TestCase):
    def test_bez_strat_na_prawdziwym_sejfie(self):
        katalog = os.path.join(rdzen.REPO, "B&C")
        if not os.path.isdir(katalog):
            self.skipTest("brak sejfu B&C")
        n = 0
        for korzen, katalogi, pliki in os.walk(katalog):
            katalogi[:] = [d for d in katalogi if not d.startswith(".")]
            for p in pliki:
                if p.endswith(".md"):
                    with open(os.path.join(korzen, p), "rb") as f:
                        b = f.read()
                    try:
                        self.assertEqual(zapis.Dokument(b).bajty(), b, p)
                    except BladHTTP:
                        pass                                   # plik nie w UTF-8 — panel go nie zmienia
                    n += 1
        self.assertGreater(n, 10)

    def test_przypadki_brzegowe(self):
        for b in (b"", b"\n", b"a", b"a\r\nb\r\n", b"a\nb", b"\xef\xbb\xbfx\r\n", b"a\r\rb\n", "ł ó\n".encode()):
            self.assertEqual(zapis.Dokument(b).bajty(), b, b)
        d = zapis.Dokument(b"")
        d.wstaw(0, ["## x"])
        self.assertEqual(d.bajty(), b"## x\n")


# =========================================================================== ślad dla „Wyślij” (tymczasowe repozytorium git)
def _git(args, cwd):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                       creationflags=rdzen.CREATE_NO_WINDOW)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr))
    return r.stdout


@unittest.skipUnless(shutil.which("git"), "brak gita")
class TestWyslijSejf(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_test_zapis_git_")
        self.zdalne = os.path.join(self.tmp, "zdalne.git")
        self.repo = os.path.join(self.tmp, "repo")
        _git(["init", "--bare", "-b", "main", self.zdalne], self.tmp)
        _git(["clone", "-q", self.zdalne, self.repo], self.tmp)
        for k, v in (("user.name", "Tester"), ("user.email", "t@example.invalid"), ("core.autocrlf", "false")):
            _git(["config", k, v], self.repo)
        _git(["checkout", "-q", "-B", "main"], self.repo)
        self.sejf = os.path.join(self.repo, "B&C")
        os.makedirs(os.path.join(self.sejf, "Produkcja"))
        for nazwa, tekst in PLIKI.values():
            with open(os.path.join(self.sejf, "Produkcja", nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)
        with open(os.path.join(self.sejf, "Inna notatka.md"), "w", encoding="utf-8") as f:
            f.write("# Inna\n")
        _git(["add", "-A"], self.repo)
        _git(["commit", "-q", "-m", "start"], self.repo)
        _git(["push", "-q", "-u", "origin", "main"], self.repo)
        self.latki = [
            mock.patch.object(sejf, "_sejfy", lambda: [("B&C", "Sejf testowy", self.sejf)]),
            mock.patch.object(zapis, "dzis", lambda: DZIS),
            mock.patch.object(zapis, "_plik_stanu", lambda: os.path.join(self.tmp, "zapis_sejfu.json")),
            mock.patch.object(rdzen, "log", lambda *a: None),
            mock.patch.object(gitsync, "sciezki_panelu", lambda: ["panel/dane"]),
        ]
        for l in self.latki:
            l.start()
        sejf.uniewaznij()

    def tearDown(self):
        for l in reversed(self.latki):
            l.stop()
        sejf.uniewaznij()

        def zdejmij_tylko_do_odczytu(fn, sciezka, _):
            os.chmod(sciezka, 0o700)
            fn(sciezka)
        shutil.rmtree(self.tmp, onerror=zdejmij_tylko_do_odczytu)

    def wersja(self, nazwa):
        with open(os.path.join(self.sejf, "Produkcja", nazwa), "rb") as f:
            return sejf.wersja_bajtow(f.read())

    def do_wyslania(self):
        return zapis.do_wyslania(self.repo, lambda a, r: gitsync.git(a, r, timeout=15))

    def test_wyslij_tylko_zmiany_panelu(self):
        self.assertEqual(self.do_wyslania(), ([], [], []))
        zapis.odpowiedz(2, "Tak", self.wersja("Pytania otwarte.md"), "Paweł")
        sciezki, opisy, uwagi = self.do_wyslania()
        self.assertEqual(sorted(sciezki), ["B&C/Produkcja/Dziennik zmian.md", "B&C/Produkcja/Pytania otwarte.md"])
        self.assertEqual(uwagi, [])
        self.assertIn("odpowiedź na pytanie 2", opisy)
        # cudza, niezatwierdzona zmiana w innym pliku sejfu nie idzie z przyciskiem „Wyślij”
        with open(os.path.join(self.sejf, "Inna notatka.md"), "a", encoding="utf-8") as f:
            f.write("ręcznie\n")
        w = gitsync.wyslij(self.repo)
        self.assertTrue(w["ok"] and w["commit"], w)
        self.assertEqual(sorted(w["pliki_sejfu"]), sorted(sciezki))
        temat = _git(["log", "-1", "--format=%s"], self.repo).strip()
        self.assertTrue(temat.startswith("panel: odpowiedź na pytanie 2"), temat)
        w_commicie = _git(["show", "--name-only", "--format=", "HEAD"], self.repo).split("\n")
        self.assertEqual(sorted(x for x in w_commicie if x), sorted(sciezki))
        self.assertIn("Inna notatka.md", _git(["status", "--porcelain"], self.repo))
        self.assertEqual(self.do_wyslania(), ([], [], []))                               # ślad wyczyszczony

    def test_cudza_zmiana_blokuje_wyslanie_pliku(self):
        sciezka = os.path.join(self.sejf, "Produkcja", "Zadania.md")
        with open(sciezka, "a", encoding="utf-8", newline="\n") as f:                    # agent zmienił plik bez commita
            f.write("- [x] 2026-11-13: ręcznie\n")
        zapis.dodaj_zadanie("Z panelu", "backlog", "niski", self.wersja("Zadania.md"), "Karol")
        sciezki, _, uwagi = self.do_wyslania()
        self.assertNotIn("B&C/Produkcja/Zadania.md", sciezki)
        self.assertTrue(any("Zadania.md" in u for u in uwagi), uwagi)
        # zmiana po zapisie panelu też blokuje (treść nie jest już tą, którą zapisał panel)
        zapis.odpowiedz(2, "Tak", self.wersja("Pytania otwarte.md"), "Paweł")
        with open(os.path.join(self.sejf, "Produkcja", "Pytania otwarte.md"), "a", encoding="utf-8") as f:
            f.write("\nręcznie\n")
        sciezki, _, uwagi = self.do_wyslania()
        self.assertEqual(sciezki, ["B&C/Produkcja/Dziennik zmian.md"])
        self.assertEqual(len(uwagi), 2)

    def test_zapis_w_trakcie_wysylania_czeka_na_commit(self):
        """Paweł odpowiada z telefonu dokładnie wtedy, gdy Karol klika „Wyślij”: zapis czeka na koniec commita
        i zostaje w śladzie jako zmiana panelu (przed poprawką: niezacommitowany i na stałe „spoza panelu”)."""
        zapis.odpowiedz(2, "Pierwsza", self.wersja("Pytania otwarte.md"), "Karol")
        wersja = self.wersja("Pytania otwarte.md")
        prawdziwy_git = gitsync.git
        watek, wynik = [], {}

        def odpowiedz_w_tle():
            try:
                wynik["w"] = zapis.odpowiedz(3, "Z telefonu", wersja, "Paweł", "gość panelu")
            except Exception as e:                             # pragma: no cover — pokaże się w asercji
                wynik["blad"] = e

        def git_z_wtraceniem(argumenty, repo=None, timeout=30):
            wyjscie = prawdziwy_git(argumenty, repo, timeout)
            if argumenty[:1] == ["commit"] and not watek:
                t = threading.Thread(target=odpowiedz_w_tle)
                watek.append(t)
                t.start()
                t.join(0.5)
                wynik["czekal"] = t.is_alive()                 # zapis czeka na blokadę sejfu
            return wyjscie
        with mock.patch.object(gitsync, "git", git_z_wtraceniem):
            w = gitsync.wyslij(self.repo)
        watek[0].join(20)
        self.assertTrue(w["ok"] and w["commit"], w)
        self.assertTrue(wynik.get("czekal"), wynik)
        self.assertNotIn("blad", wynik)
        sciezki, opisy, uwagi = self.do_wyslania()
        self.assertEqual(uwagi, [])
        self.assertEqual(sorted(sciezki), ["B&C/Produkcja/Dziennik zmian.md", "B&C/Produkcja/Pytania otwarte.md"])
        self.assertEqual(opisy.count("odpowiedź na pytanie 3"), 2)                        # pytania + dziennik
        w = gitsync.wyslij(self.repo)                                                    # i da się je wysłać
        self.assertTrue(w["ok"] and w["commit"], w)
        self.assertEqual(_git(["status", "--porcelain", "--", "B&C/Produkcja"], self.repo).strip(), "")

    def test_cudza_zmiana_tuz_przed_commitem(self):
        """Obsidian zapisuje plik między sprawdzeniem a commitem: commit „panel: …” ją zawiera — człowiek dostaje
        uwagę, zamiast dowiedzieć się z historii."""
        zapis.odpowiedz(2, "Tak", self.wersja("Pytania otwarte.md"), "Paweł")
        sciezka = os.path.join(self.sejf, "Produkcja", "Pytania otwarte.md")
        prawdziwy_git = gitsync.git

        def git_z_obsidianem(argumenty, repo=None, timeout=30):
            if argumenty[:1] == ["add"]:
                with open(sciezka, "a", encoding="utf-8", newline="\n") as f:
                    f.write("\ndopisane w Obsidianie\n")
            return prawdziwy_git(argumenty, repo, timeout)
        with mock.patch.object(gitsync, "git", git_z_obsidianem):
            w = gitsync.wyslij(self.repo)
        self.assertTrue(w["ok"] and w["commit"], w)
        self.assertIn("Pytania otwarte.md zmienił się w trakcie wysyłania", w.get("uwaga", ""))
        self.assertNotIn("Dziennik zmian.md zmienił się", w.get("uwaga", ""))

    def test_podglad_tego_co_pojdzie(self):
        zapis.odpowiedz(2, "Treść widoczna przed wysłaniem", self.wersja("Pytania otwarte.md"), "Paweł", "gość panelu")
        sciezki, _, _ = self.do_wyslania()
        podglad = {p["plik"]: p for p in gitsync.podglad_sejfu(sciezki, self.repo)}
        self.assertIn("+ - Paweł (gość panelu, %s): Treść widoczna przed wysłaniem" % DZIS,
                      podglad["B&C/Produkcja/Pytania otwarte.md"]["wiersze"])
        self.assertTrue(any("odpowiedź na pytanie 2" in x for x in podglad["B&C/Produkcja/Dziennik zmian.md"]["wiersze"]))

    def test_zacommitowane_recznie_znika_ze_sladu(self):
        zapis.odpowiedz(2, "Tak", self.wersja("Pytania otwarte.md"), "Paweł")
        _git(["add", "-A"], self.repo)
        _git(["commit", "-q", "-m", "ręcznie"], self.repo)
        self.assertEqual(self.do_wyslania(), ([], [], []))
        stan = rdzen.czytaj_json(os.path.join(self.tmp, "zapis_sejfu.json"), {})
        self.assertEqual(stan.get("pliki"), {})


if __name__ == "__main__":
    unittest.main()
