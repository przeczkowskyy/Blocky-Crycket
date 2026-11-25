# -*- coding: utf-8 -*-
"""Pulpit per gra (25.11.2026): rejestr gier i klasyfikator (bc/gry.py), znaczniki w parserach, pola `gra` w API,
zapis zadania ze znacznikiem, `raport.py --gra`, lustro i panel bez rejestru.

Uruchomienie (z katalogu panel/):  python -B -m unittest testy.test_gry
- klasyfikator i parsery — w tym procesie, na rejestrze podanym jawnie (bez prawdziwej konfiguracji);
- API — prawdziwy serwer (test_api.SerwerTestowy) z kopią sejfu i rejestrem gier w konfiguracji lokalnej; drugi
  serwer z `"gry": null` sprawdza, że bez rejestru panel działa jak dawniej;
- `narzedzia/raport.py` i eksport lustra — osobne procesy na katalogach tymczasowych.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

PANEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PANEL)

from bc import gry, rdzen, sejf  # noqa: E402
from bc.rdzen import BladHTTP  # noqa: E402
from testy import test_api  # noqa: E402  (bez importu klas: discover uruchomiłby je drugi raz)

REJESTR = {"domyslna": "bc", "aktywna": "bc", "lista": [
    {"id": "bc", "nazwa": "Blocky & Crycket", "stan": "aktywna", "slowa": ["Blocky"]},
    {"id": "smok", "nazwa": "Gra o smoku", "stan": "wstrzymana", "slowa": ["o smok", "Monster Evolution"]},
    {"id": "pet-arena", "nazwa": "Pet Arena", "stan": "wstrzymana", "slowa": ["Pet Aren", "smok"]},
    {"id": "wspolne", "nazwa": "Wspólne", "wspolne": True, "slowa": ["^panel", "sesj glown"]},
]}

PYTANIA = """---
status: do-decyzji
---
# Pytania otwarte

## 1. Zwykłe pytanie
Treść.
**Odpowiedź:**

## 2. Pet Arena: kolor areny?
Treść bez znacznika.
**Odpowiedź:**

## 3. Pytanie ze znacznikiem
- **Gra:** smok
Treść o Pet Arenie (w treści, nie w tytule).
**Odpowiedź:**

## 4. Pytanie bez słowa w tytule
To pytanie jest o smoku, ale tylko w treści.
**Odpowiedź:**

## 5. Znacznik w odpowiedzi się nie liczy
Treść.
**Odpowiedź:**
- Karol (2026-11-25): Gra: smok

## 6. Znacznik w bloku kodu się nie liczy
```
Gra: smok
```
**Odpowiedź:**

## 7. Nieznany znacznik
Gra: nie-ma-takiej
**Odpowiedź:**
"""

DECYZJE = """---
status: kanon
---
# Rejestr decyzji

---

### D-001 Zwykła decyzja
✅ zatwierdzona · styl
Opis.

### D-002 Pet Arena: większa arena
💡 propozycja · game design
Opis.

### D-003 Decyzja ze znacznikiem
💡 propozycja · technika
Gra: Gra o smoku
Opis o Pet Arenie.

### D-004 Panel: nowa zakładka
🕓 do decyzji · panel
Opis.

---
*Stopka rejestru.*
"""

ZADANIA = """---
status: kanon
---
# Zadania

## 🔥 Teraz (Sprint 1)
- [ ] Zwykłe zadanie · #wysoki
- [ ] Pet Arena: testy · #średni
- [ ] Zadanie ze znacznikiem · #gra/smok · agent: Paweł · #niski
- [ ] Pet Arena, ale dla B&C · #gra/bc · #niski

## 📥 Backlog
- [ ] Coś na później · #niski

## ✅ Zrobione
- [x] 2026-11-12: Stare zadanie · #gra/smok
"""

DZIENNIK = """---
status: kanon
---
# Dziennik zmian

## 2026-11-12 · Claude Code (coś)
- Punkt.
"""

RAPORTY = [
    {"id": "r-20261125-100000-aaaa", "tytul": "Gra o smoku: mapa", "rodzaj": "wdrozenie"},
    {"id": "r-20261125-100100-bbbb", "tytul": "Zwykły raport", "rodzaj": "wdrozenie", "gra": "pet-arena"},
    {"id": "r-20261125-100200-cccc", "tytul": "Zwykły raport 2", "rodzaj": "wdrozenie"},
    {"id": "r-20261125-100300-dddd", "tytul": "Gra o smoku 2", "rodzaj": "wdrozenie", "gra": "nieznana"},
    {"id": "r-20261125-100400-eeee", "tytul": "Sesja główna 2026-11-25 — do zatwierdzenia", "rodzaj": "wdrozenie"},
]


def R():
    return gry._zbuduj(REJESTR)


def plan_z(rej):
    """Plan z tekstów testowych (parsery sejf.py + gry.oznacz_plan) — bez plików i konfiguracji."""
    plan = {"pytania": sejf.parsuj_pytania(PYTANIA), "decyzje": sejf.parsuj_decyzje(DECYZJE, osoby=["Karol", "Paweł"]),
            "zadania": sejf.parsuj_zadania(ZADANIA)}
    return gry.oznacz_plan(plan, rej)


# =========================================================================== klasyfikator (w tym procesie)
class TestKlasyfikator(unittest.TestCase):
    def test_znacznik_wygrywa_ze_slowem(self):
        self.assertEqual(gry.klasyfikuj("Pet Arena: test", "smok", R())[:2], ("smok", "znacznik"))
        self.assertEqual(gry.klasyfikuj("Pet Arena: test", "Gra o smoku", R())[:2], ("smok", "znacznik"))   # po nazwie
        self.assertEqual(gry.klasyfikuj("x", "[[Pet Arena]]", R())[:2], ("pet-arena", "znacznik"))
        self.assertEqual(gry.klasyfikuj("x", "smok (wstrzymana)", R())[:2], ("smok", "znacznik"))

    def test_slowo_w_tytule(self):
        self.assertEqual(gry.klasyfikuj("Pet Arenę trzeba poprawić", None, R())[:2], ("pet-arena", "slowo"))   # odmiana
        self.assertEqual(gry.klasyfikuj("Monster-Evolution: etap 2", None, R())[:2], ("smok", "slowo"))
        self.assertEqual(gry.klasyfikuj("PANEL: lustro", None, R())[:2], ("wspolne", "slowo"))

    def test_pierwsza_gra_w_kolejnosci_rejestru(self):
        # „smok” jest słowem gry pet-arena, ale „o smok” gry smok stoi w rejestrze wcześniej
        self.assertEqual(gry.klasyfikuj("Sklep w grze o smoku", None, R())[0], "smok")
        self.assertEqual(gry.klasyfikuj("Czerwony smok (3D)", None, R())[0], "pet-arena")
        self.assertEqual(gry.klasyfikuj("Blocky: Pet Arena w tle", None, R())[0], "bc")

    def test_krotkie_wyrazy_w_calosci_i_poczatek_tytulu(self):
        self.assertEqual(gry.klasyfikuj("Las obok smoka", None, R())[0], "pet-arena")   # „obok” ≠ „o”; „smok” z pet-arena
        r = gry._zbuduj({"lista": [{"id": "a"}, {"id": "b", "slowa": ["o smok"]}]})
        self.assertEqual(gry.klasyfikuj("Las obok smoka", None, r)[0], "a")
        self.assertEqual(gry.klasyfikuj("Zaakceptowane w panelu", None, R())[0], "bc")   # „^panel” tylko na początku
        self.assertEqual(gry.klasyfikuj("Notatka z sesji głównej", None, R())[0], "wspolne")

    def test_domyslna_i_nieznany_znacznik(self):
        self.assertEqual(gry.klasyfikuj("Nic szczególnego", None, R()), ("bc", "domyslna", None))
        gid, skad, szcz = gry.klasyfikuj("Nic", "nie-ma-takiej", R())
        self.assertEqual((gid, skad), ("bc", "domyslna"))
        self.assertIn("nieznany znacznik", szcz)
        self.assertEqual(gry.klasyfikuj("Pet Arena", "nie-ma", R())[0], "pet-arena")    # nieznany znacznik → słowa

    def test_bez_rejestru(self):
        with mock.patch.object(rdzen, "konfiguracja", return_value={}):
            self.assertIsNone(gry.rejestr())
            self.assertEqual(gry.klasyfikuj("Pet Arena", "smok"), (None, None, None))
            self.assertIsNone(gry.publiczny())
            self.assertEqual(gry.podpis(), "")
            with self.assertRaises(BladHTTP) as e:
                gry.sprawdz_gre("smok")
            self.assertEqual(e.exception.dodatkowe.get("kod"), "brak_rejestru_gier")
        with mock.patch.object(rdzen, "konfiguracja", return_value={"gry": {"lista": [{"id": "wspolne", "wspolne": True}]}}):
            self.assertIsNone(gry.rejestr())                   # sama gra wspólna to nie rejestr
        self.assertIsNone(gry._zbuduj({"lista": []}))
        self.assertIsNone(gry._zbuduj("zle"))

    def test_rejestr_poprawia_zle_wpisy(self):
        r = gry._zbuduj({"domyslna": "nie-ma", "aktywna": "wspolne", "lista": [
            {"id": "Zle Id!"}, {"id": "bc", "stan": "dziwny"}, {"id": "bc"}, {"id": "wspolne"}, {"id": "x", "slowa": "nie lista"}]})
        self.assertEqual([g["id"] for g in r["lista"]], ["bc", "wspolne", "x"])
        self.assertEqual((r["domyslna"], r["aktywna"]), ("bc", "bc"))   # „wspólne” nie może być ani domyślną, ani aktywną
        self.assertEqual(r["lista"][0]["stan"], "aktywna")
        self.assertTrue(r["lista"][1]["wspolne"])
        p = gry.publiczny(r)
        self.assertEqual(set(p["lista"][0]), {"id", "nazwa", "stan", "wspolne"})   # bez słów kluczowych dla interfejsu

    def test_sprawdz_gre(self):
        with mock.patch.object(rdzen, "konfiguracja", return_value={"gry": REJESTR}):
            self.assertEqual(gry.sprawdz_gre(" Smok "), "smok")
            self.assertIsNone(gry.sprawdz_gre(""))
            with self.assertRaises(BladHTTP) as e:
                gry.sprawdz_gre("nieznana")
            self.assertEqual((e.exception.status, e.exception.dodatkowe.get("kod")), (400, "nieznana_gra"))
            self.assertEqual(gry.znacznik_nowego_zadania("Zwykłe", "bc"), "")
            self.assertEqual(gry.znacznik_nowego_zadania("Zwykłe", "smok"), " · #gra/smok")
            self.assertEqual(gry.znacznik_nowego_zadania("Pet Arena: x", "bc"), " · #gra/bc")   # słowo innej gry
            self.assertEqual(gry.znacznik_nowego_zadania("Pet Arena: x", "pet-arena"), "")


# =========================================================================== parsery i znaczniki
class TestZnaczniki(unittest.TestCase):
    def test_pytania(self):
        p = {x["nr"]: x for x in plan_z(R())["pytania"]}
        self.assertEqual((p[1]["gra"], p[1]["gra_skad"]), ("bc", "domyslna"))
        self.assertEqual((p[2]["gra"], p[2]["gra_skad"]), ("pet-arena", "slowo"))
        self.assertEqual((p[3]["gra"], p[3]["gra_skad"]), ("smok", "znacznik"))          # znacznik > treść „Pet Arenie”
        self.assertEqual(p[4]["gra"], "bc")                                               # tylko tytuł się liczy
        self.assertEqual(p[5]["gra"], "bc")                                               # odpowiedź się nie liczy
        self.assertEqual(p[6]["gra"], "bc")                                               # blok kodu się nie liczy
        self.assertEqual((p[7]["gra"], p[7]["gra_skad"]), ("bc", "domyslna"))
        self.assertIn("- **Gra:** smok", p[3]["tresc_md"])                                # treść bez zmian

    def test_decyzje_wiersz_statusu_zostaje_pierwszy(self):
        d = {x["id"]: x for x in plan_z(R())["decyzje"]}
        self.assertEqual((d["D-003"]["status"], d["D-003"]["kategoria"]), ("propozycja", "technika"))
        self.assertIsNone(d["D-003"]["sprzeczny_status"])
        self.assertEqual((d["D-003"]["gra"], d["D-003"]["gra_skad"]), ("smok", "znacznik"))
        self.assertEqual(d["D-002"]["gra"], "pet-arena")
        self.assertEqual(d["D-004"]["gra"], "wspolne")
        self.assertEqual(d["D-001"]["gra"], "bc")

    def test_zadania_znacznik_poza_tekstem(self):
        z = [p for s in plan_z(R())["zadania"]["sekcje"] for p in s["pozycje"]]
        po = {p["tekst_md"]: p for p in z}
        t = po["Zadanie ze znacznikiem"]
        self.assertEqual((t["gra"], t["gra_skad"], t["agent"], t["priorytet"]), ("smok", "znacznik", "Paweł", "niski"))
        self.assertEqual(t["id"], sejf.id_zadania("Zadanie ze znacznikiem · #gra/smok · agent: Paweł · #niski"))
        self.assertNotIn("gra_znacznik", t)
        self.assertEqual(po["Pet Arena, ale dla B&C"]["gra"], "bc")                      # znacznik > słowo
        self.assertEqual(po["Pet Arena: testy"]["gra"], "pet-arena")
        self.assertEqual(po["Zwykłe zadanie"]["gra"], "bc")
        self.assertEqual((po["Stare zadanie"]["gra"], po["Stare zadanie"]["data"]), ("smok", "2026-11-12"))

    def test_starszy_kod_czyta_znaczniki_bez_szkody(self):
        """Starszy panel nie zna znaczników: priorytet i „· agent:” zostają na końcu linii, „Gra:” jest tekstem opisu."""
        pole = "Zadanie ze znacznikiem · #gra/smok · agent: Paweł · #niski"
        mp = sejf._RX_PRIORYTET.search(pole)
        self.assertEqual(mp.group(1), "niski")
        bez, agent = sejf.agent_zadania(pole[:mp.start()].rstrip(" ·"))
        self.assertEqual((bez, agent), ("Zadanie ze znacznikiem · #gra/smok", "Paweł"))
        d = sejf.parsuj_decyzje(DECYZJE, osoby=["Karol", "Paweł"])
        self.assertEqual([x["status"] for x in d], ["zatwierdzona", "propozycja", "propozycja", "do_decyzji"])
        with mock.patch.object(rdzen, "konfiguracja", return_value={}):   # panel bez rejestru gier
            bez_rejestru = plan_z(None)
        self.assertNotIn("gra", bez_rejestru["pytania"][0])
        z = [p for s in bez_rejestru["zadania"]["sekcje"] for p in s["pozycje"]]
        self.assertTrue(all("gra" not in p and "gra_znacznik" not in p for p in z))

    def test_pomocnicze(self):
        self.assertEqual(gry.znacznik_zadania("a · #gra/pet-arena · #wysoki"), "pet-arena")
        self.assertIsNone(gry.znacznik_zadania("a#gra/smok"))
        self.assertEqual(gry.bez_znacznika_zadania("#gra/smok tekst"), "tekst")
        self.assertEqual(gry.bez_znacznika_zadania("tekst #gra/smok dalej"), "tekst dalej")
        self.assertEqual(gry.znacznik_tresci("a\n**Gra:** pet-arena\nb"), "pet-arena")
        self.assertIsNone(gry.znacznik_tresci("Gra:\nnic"))
        self.assertTrue(gry.jest_wierszem_gry("- Gra: smok"))
        self.assertEqual(gry.wyrazy("Łódź Pet-Arenę!"), ["lodz", "pet", "arene"])


# =========================================================================== API (prawdziwy serwer)
class _SerwerGier(test_api.SerwerTestowy):
    rejestr = REJESTR

    @classmethod
    def konfiguracja_lokalna(cls):
        cls.sejf = os.path.join(cls.tmp, "sejf")
        return {"gra": {"universeId": None}, "sejfy": [{"id": "B&C", "nazwa": "Sejf testowy", "sciezka": cls.sejf}],
                "gry": cls.rejestr}

    @classmethod
    def przygotuj(cls, runtime):
        produkcja = os.path.join(cls.sejf, "Produkcja")
        os.makedirs(produkcja)
        for nazwa, tekst in (("Pytania otwarte.md", PYTANIA), ("Rejestr decyzji.md", DECYZJE), ("Zadania.md", ZADANIA),
                             ("Dziennik zmian.md", DZIENNIK)):
            with open(os.path.join(produkcja, nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)
        kat = os.path.join(cls.tmp, "dane", "raporty")
        os.makedirs(kat)
        for i, r in enumerate(RAPORTY):
            r = dict(r, opis_md="", kto="Tester", czas="2026-11-25T10:0%d:00+01:00" % i, komponenty=[], zrzuty=[])
            with open(os.path.join(kat, r["id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(r, f, ensure_ascii=False)

    def plik(self, nazwa):
        with open(os.path.join(self.sejf, "Produkcja", nazwa), encoding="utf-8", newline="") as f:
            return f.read()

    def plan(self):
        s, o, _ = self.get("/api/sejf/plan")
        self.assertEqual(s, 200, o)
        return o


class TestGryAPI(_SerwerGier):
    def test_konfiguracja_ma_rejestr(self):
        s, o, _ = self.get("/api/konfiguracja")
        self.assertEqual(s, 200)
        self.assertEqual([g["id"] for g in o["gry"]["lista"]], ["bc", "smok", "pet-arena", "wspolne"])
        self.assertEqual((o["gry"]["domyslna"], o["gry"]["aktywna"]), ("bc", "bc"))
        self.assertEqual(o["gry"]["lista"][1], {"id": "smok", "nazwa": "Gra o smoku", "stan": "wstrzymana", "wspolne": False})
        self.assertTrue(o["gry"]["lista"][3]["wspolne"])
        self.assertIn("gra", o)                                # stary klucz z identyfikatorami Roblox zostaje
        _, o, _ = self.get("/api/konfiguracja", zdalny=True)  # gość z kodem dostępu też widzi rejestr (przełącznik)
        self.assertIn("gry", o)

    def test_plan_ma_gre_przy_kazdej_sprawie(self):
        o = self.plan()
        p = {x["nr"]: x["gra"] for x in o["pytania"]}
        self.assertEqual(p, {1: "bc", 2: "pet-arena", 3: "smok", 4: "bc", 5: "bc", 6: "bc", 7: "bc"})
        self.assertEqual({x["id"]: x["gra"] for x in o["decyzje"]},
                         {"D-001": "bc", "D-002": "pet-arena", "D-003": "smok", "D-004": "wspolne"})
        z = {p["tekst_md"]: (p["gra"], p["gra_skad"]) for s in o["zadania"]["sekcje"] for p in s["pozycje"]}
        self.assertEqual(z["Zadanie ze znacznikiem"], ("smok", "znacznik"))
        self.assertEqual(z["Pet Arena: testy"], ("pet-arena", "slowo"))
        self.assertEqual(z["Coś na później"], ("bc", "domyslna"))

    def test_raporty_maja_gre_a_pliki_zostaja(self):
        kat = os.path.join(self.tmp, "dane", "raporty")

        def bajty(n):
            with open(os.path.join(kat, n), "rb") as f:
                return f.read()
        przed = {n: bajty(n) for n in os.listdir(kat) if n.endswith(".json")}
        s, o, _ = self.get("/api/raporty")
        self.assertEqual(s, 200)
        g = {r["id"]: (r["gra"], r["gra_skad"]) for r in o["raporty"]}
        self.assertEqual(g["r-20261125-100000-aaaa"], ("smok", "slowo"))
        self.assertEqual(g["r-20261125-100100-bbbb"], ("pet-arena", "znacznik"))
        self.assertEqual(g["r-20261125-100200-cccc"], ("bc", "domyslna"))
        self.assertEqual(g["r-20261125-100300-dddd"], ("smok", "slowo"))       # nieznane pole „gra” → tytuł
        self.assertEqual(g["r-20261125-100400-eeee"], ("wspolne", "slowo"))
        s, o, _ = self.get("/api/raporty/r-20261125-100100-bbbb")
        self.assertEqual(o["gra"], "pet-arena")
        self.assertEqual({n: bajty(n) for n in przed}, przed)  # stare pliki w panel/dane/ bez zmian

    def test_nowy_raport_z_gra(self):
        s, o, _ = self.post("/api/raporty", {"tytul": "Nowy raport smoka", "gra": "smok"})
        self.assertEqual(s, 201, o)
        self.assertEqual((o["gra"], o["gra_skad"]), ("smok", "znacznik"))
        with open(os.path.join(self.tmp, "dane", "raporty", o["id"] + ".json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["gra"], "smok")
        self.assertBlad(self.post("/api/raporty", {"tytul": "Zła gra", "gra": "nie-ma"}), 400)

    def test_nowe_zadanie_w_grze_dostaje_znacznik(self):
        def dodaj(tekst, gra=None, sekcja="teraz", priorytet="średni"):
            cialo = {"tekst": tekst, "sekcja": sekcja, "priorytet": priorytet, "wersja": self.plan()["wersje"]["zadania"]}
            if gra is not None:
                cialo["gra"] = gra
            return self.post("/api/sejf/zadania/dodaj", cialo, kto="Karol")

        s, o, _ = dodaj("Nowe zadanie", "smok")
        self.assertEqual(s, 200, o)
        self.assertIn("- [ ] Nowe zadanie · #gra/smok · #średni\n", self.plik("Zadania.md"))
        self.assertIn("dodane zadanie: Nowe zadanie (Teraz, gra: Gra o smoku)", self.plik("Dziennik zmian.md"))
        z = {p["tekst_md"]: p["gra"] for s_ in o["plan"]["zadania"]["sekcje"] for p in s_["pozycje"] if not p["zrobione"]}
        self.assertEqual(z["Nowe zadanie"], "smok")
        s, o, _ = dodaj("Nowe zadanie", "smok")                                  # to samo w tej samej grze = dubel
        self.assertEqual((s, o.get("kod")), (409, "juz_zapisane"))
        s, o, _ = dodaj("Nowe zadanie", "bc")                                    # w innej grze — osobne zadanie
        self.assertEqual(s, 200, o)
        self.assertIn("- [ ] Nowe zadanie · #średni\n", self.plik("Zadania.md"))  # gra domyślna bez znacznika
        s, o, _ = dodaj("Pet Arena dla B&C", "bc")                               # słowo innej gry → jawny znacznik
        self.assertEqual(s, 200, o)
        self.assertIn("- [ ] Pet Arena dla B&C · #gra/bc · #średni\n", self.plik("Zadania.md"))
        s, o, _ = dodaj("Pet Arena: nowe", "pet-arena")                          # słowo tej gry — znacznik zbędny
        self.assertIn("- [ ] Pet Arena: nowe · #średni\n", self.plik("Zadania.md"))
        s, o, _ = dodaj("Bez gry")                                               # bez pola — jak dawniej
        self.assertEqual(s, 200, o)
        self.assertIn("- [ ] Bez gry · #średni\n", self.plik("Zadania.md"))
        przed = self.plik("Zadania.md")
        s, o, _ = dodaj("Zła gra", "nie-ma")
        self.assertEqual((s, o.get("kod")), (400, "nieznana_gra"))
        s, o, _ = dodaj("Tekst #gra/smok z tagiem")
        self.assertEqual(s, 400, o)
        self.assertEqual(self.plik("Zadania.md"), przed)

    def test_agent_i_odhaczenie_zostawiaja_znacznik(self):
        o = self.plan()
        z = next(p for s in o["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Pet Arena, ale dla B&C")
        s, w, _ = self.post("/api/sejf/zadania/agent", {"id": z["id"], "agent": "Karol", "wersja": o["wersje"]["zadania"]},
                            kto="Karol")
        self.assertEqual(s, 200, w)
        self.assertIn("- [ ] Pet Arena, ale dla B&C · #gra/bc · agent: Karol · #niski\n", self.plik("Zadania.md"))
        z = next(p for s in w["plan"]["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Pet Arena, ale dla B&C")
        self.assertEqual((z["gra"], z["agent"]), ("bc", "Karol"))
        s, w, _ = self.post("/api/sejf/zadania/odhacz", {"id": z["id"], "wersja": w["plan"]["wersje"]["zadania"]}, kto="Karol")
        self.assertEqual(s, 200, w)
        self.assertRegex(self.plik("Zadania.md"), r"- \[x\] \d{4}-\d{2}-\d{2}: Pet Arena, ale dla B&C · #gra/bc · agent: Karol\n")
        z = next(p for s in w["plan"]["zadania"]["sekcje"] for p in s["pozycje"] if p["tekst_md"] == "Pet Arena, ale dla B&C")
        self.assertEqual((z["gra"], z["zrobione"]), ("bc", True))

    def test_przekierowanie_z_kluczem_zachowuje_gre(self):
        import http.client
        for gra, adres in (("smok", "/?gra=smok"), ("wszystkie", "/?gra=wszystkie"), ("ZŁE/../x", "/")):
            c = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
            try:
                c.request("GET", "/?k=%s&gra=%s" % (self.token, urllib_quote(gra)), headers={"X-Forwarded-For": "192.168.1.50"})
                r = c.getresponse()
                r.read()
                self.assertIn(r.status, (302, 303))
                self.assertEqual(r.getheader("Location"), adres)
            finally:
                c.close()


def urllib_quote(s):
    import urllib.parse
    return urllib.parse.quote(s, safe="")


class TestBezRejestruAPI(_SerwerGier):
    """`"gry": null` w konfiguracji = bez rejestru: panel jak dawniej (bez pól `gra`, bez przełącznika)."""
    rejestr = None

    def test_bez_rejestru_jak_dawniej(self):
        _, o, _ = self.get("/api/konfiguracja")
        self.assertNotIn("gry", o)
        o = self.plan()
        self.assertTrue(all("gra" not in x for x in o["pytania"] + o["decyzje"]))
        z = [p for s in o["zadania"]["sekcje"] for p in s["pozycje"]]
        self.assertTrue(all("gra" not in p and "gra_znacznik" not in p for p in z))
        _, r, _ = self.get("/api/raporty")
        self.assertNotIn("gra_skad", r["raporty"][0])
        cialo = {"tekst": "Zadanie z grą", "sekcja": "teraz", "priorytet": "niski", "wersja": o["wersje"]["zadania"], "gra": "smok"}
        s, w, _ = self.post("/api/sejf/zadania/dodaj", cialo, kto="Karol")
        self.assertEqual((s, w.get("kod")), (400, "brak_rejestru_gier"))
        cialo.pop("gra")
        s, w, _ = self.post("/api/sejf/zadania/dodaj", cialo, kto="Karol")
        self.assertEqual(s, 200, w)
        self.assertIn("- [ ] Zadanie z grą · #niski\n", self.plik("Zadania.md"))


# =========================================================================== narzędzie raport.py i lustro
class TestNarzedziaGier(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bc_gry_cli_")
        self.dane = os.path.join(self.tmp, "dane")
        os.makedirs(os.path.join(self.dane, "raporty"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def env(self, rejestr):
        runtime = os.path.join(self.tmp, "runtime-%s" % ("z" if rejestr else "bez"))
        os.makedirs(runtime, exist_ok=True)
        with open(os.path.join(runtime, "konfiguracja.lokalna.json"), "w", encoding="utf-8") as f:
            json.dump({"gry": rejestr, "gra": {"universeId": None}}, f)
        return dict(os.environ, BC_PANEL_DANE=self.dane, BC_PANEL_RUNTIME=runtime, PYTHONDONTWRITEBYTECODE="1",
                    PYTHONIOENCODING="utf-8")

    def uruchom(self, env, *argv):
        p = subprocess.run([sys.executable, "-B", os.path.join(PANEL, "narzedzia", "raport.py")] + list(argv),
                           capture_output=True, env=env, timeout=60)
        return p.returncode, p.stdout.decode("utf-8"), p.stderr.decode("utf-8")

    def test_raport_py_gra(self):
        env = self.env(REJESTR)
        kod, out, err = self.uruchom(env, "dodaj", "--tytul", "Raport do smoka", "--gra", "smok", "--json")
        self.assertEqual(kod, 0, err)
        r = json.loads(out)
        self.assertEqual((r["gra"], r["gra_skad"]), ("smok", "znacznik"))
        with open(os.path.join(self.dane, "raporty", r["id"] + ".json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["gra"], "smok")
        kod, out, err = self.uruchom(env, "dodaj", "--tytul", "Zwykły", "--gra", "bc")
        self.assertEqual(kod, 0, err)
        self.assertIn("gra: bc", out)
        przed = sorted(os.listdir(os.path.join(self.dane, "raporty")))
        kod, out, err = self.uruchom(env, "dodaj", "--tytul", "Zła gra", "--gra", "nie-ma")
        self.assertEqual(kod, 1)
        self.assertIn("Nieznana gra", err)
        self.assertEqual(sorted(os.listdir(os.path.join(self.dane, "raporty"))), przed)   # nic nie powstało
        kod, out, err = self.uruchom(env, "lista", "--gra", "smok", "--json")
        self.assertEqual(kod, 0, err)
        self.assertEqual([x["tytul"] for x in json.loads(out)["raporty"]], ["Raport do smoka"])
        kod, out, err = self.uruchom(self.env(None), "dodaj", "--tytul", "Bez rejestru", "--gra", "smok")
        self.assertEqual(kod, 1)
        self.assertIn("rejestru gier", err)

    def test_lustro_ma_rejestr_i_gry(self):
        sejf_kat = os.path.join(self.tmp, "sejf", "Produkcja")
        os.makedirs(sejf_kat)
        for nazwa, tekst in (("Pytania otwarte.md", PYTANIA), ("Rejestr decyzji.md", DECYZJE), ("Zadania.md", ZADANIA)):
            with open(os.path.join(sejf_kat, nazwa), "w", encoding="utf-8", newline="\n") as f:
                f.write(tekst)
        with open(os.path.join(self.dane, "raporty", "r-20261125-100000-aaaa.json"), "w", encoding="utf-8") as f:
            json.dump(dict(RAPORTY[0], opis_md="", kto="t", czas="2026-11-25T10:00:00+01:00", komponenty=[], zrzuty=[]), f)
        env = self.env(REJESTR)
        with open(os.path.join(env["BC_PANEL_RUNTIME"], "konfiguracja.lokalna.json"), "w", encoding="utf-8") as f:
            json.dump({"gry": REJESTR, "gra": {"universeId": None},
                       "sejfy": [{"id": "B&C", "nazwa": "Sejf testowy", "sciezka": os.path.join(self.tmp, "sejf")}]}, f)
        wyj = os.path.join(self.tmp, "lustro")
        r = subprocess.run([sys.executable, "-B", os.path.join(PANEL, "serwer.py"), "--eksport", wyj], capture_output=True,
                           env=env, timeout=180)
        self.assertEqual(r.returncode, 0, (r.stdout + r.stderr).decode("utf-8", "replace")[-800:])
        from bc import statyczny

        def czytaj(sciezka):
            with open(os.path.join(wyj, "dane", statyczny.klucz(sciezka) + ".json"), encoding="utf-8") as f:
                return json.load(f)
        self.assertEqual(czytaj("/api/konfiguracja")["gry"]["aktywna"], "bc")
        plan = czytaj("/api/sejf/plan")
        self.assertEqual({p["nr"]: p["gra"] for p in plan["pytania"]}[3], "smok")
        self.assertEqual(czytaj("/api/raporty")["raporty"][0]["gra"], "smok")
        self.assertTrue(os.path.isfile(os.path.join(wyj, "wspolne", "gry.js")))


if __name__ == "__main__":
    unittest.main()
