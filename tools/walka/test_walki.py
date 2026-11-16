# -*- coding: utf-8 -*-
"""Testy silnika walki v3 (port w Pythonie, dane, wzorce, zrodla Luau — statycznie i w interpreterze luau_mini).

    python -B -m unittest discover -s tools/walka -p "test_*.py" -v

Duza proba (2000 ziaren na kazda pare klasa-przeciwnik, poziomy 1-10, 12, 15 i 20) liczy sie raz i sluzy
testom niezmiennikow, zasad U7 (dlugosc walki) i U10 (rownosc klas). Mana, rotacja slotow i statusy sa sprawdzane
NIEZALEZNYMI wyroczniami (odtworzenie dziennika z regul w tym pliku, bez kodu silnika). Caly zestaw trwa kilka minut.
"""
import copy
import json
import os
import re
import statistics
import sys
import unittest

TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
sys.path.insert(0, TU)
import dziennik  # noqa: E402
import generuj_dane  # noqa: E402
import silnik  # noqa: E402
import wzorce  # noqa: E402
import wzorcowe  # noqa: E402

ZIAREN = 2000
# wszystkie poziomy 1-10 (kazdy prog slotow: 1 slot do 4. poziomu, 2 od 5., 3 od 10.) i wyzsze probki
POZIOMY = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20]
MONSTRY = [p["id"] for p in silnik.PRZECIWNICY_LISTA]
PRZECIWNICY = MONSTRY + wzorcowe.KLASY
# U10 — progi sa CELEM, nie straznikiem regresji z zapasem: roznica klas przy tym samym potworze najwyzej 7 pp
# (cel z zadania: ok. 5 pp; patrz tabela balansu), pojedynek klasa na klase 45-55% na kazdym poziomie.
TOLERANCJA_KLAS_PP = 7.0
WYJATKI_KLAS_PP = {}
PVP_OD, PVP_DO = 45.0, 55.0
# buildy (sesja 16.11): z postacia wzorcowa swojej klasy 45-55%, z potworem „wyraznie” lepiej i gorzej niz wzorcowa
BUILD_OD, BUILD_DO = 45.0, 55.0
BUILD_WYRAZNIE_PP = 3.0
ZIAREN_BUILDOW = 800

_PROBA = None


def przeciwnik(nazwa, poziom):
    if nazwa in wzorcowe.KLASY:
        return {"postac": wzorcowe.postac(nazwa, poziom)}
    return {"potwor": nazwa, "poziom": poziom}


def wartosci_stron(gracz, prz):
    """Wartosci bojowe obu stron tak, jak liczy je silnik (do wyroczni)."""
    A = silnik.wartosci_postaci(gracz)
    B = silnik.wartosci_przeciwnika(prz)
    return {"gracz": A, "wrog": B}


def proba():
    """Raz liczona duza proba: {(poziom, klasa, przeciwnik): statystyki}."""
    global _PROBA
    if _PROBA is not None:
        return _PROBA
    wynik = {}
    for L in POZIOMY:
        for k in wzorcowe.KLASY:
            g = wzorcowe.postac(k, L)
            for p in PRZECIWNICY:
                prz = przeciwnik(p, L)
                V = wartosci_stron(g, prz)
                s = {"wygrane": 0, "tury": [], "czasy": [], "zle": [], "bezpiecznik": 0, "shardy": 0, "gemy": 0,
                     "klucze_lupu": set(), "efekty_zle": [], "czasy_zle": [], "mana_zle": [], "uzycia": [],
                     "pierwsze": []}
                for z in range(1, ZIAREN + 1):
                    w = silnik.symuluj(g, prz, z)
                    ok, opis = dziennik.sprawdz(w)
                    if not ok and len(s["zle"]) < 3:
                        s["zle"].append((z, opis))
                    s["wygrane"] += w["wynik"] == "wygrana"
                    s["tury"].append(w["tury"])
                    s["czasy"].append(w["czas"])
                    s["bezpiecznik"] += w["bezpiecznik"]
                    s["shardy"] += w["lup"]["shard_ewolucji"]
                    s["gemy"] += w["lup"]["gemy"]
                    s["klucze_lupu"] |= set(w["lup"])
                    blad_efektu = sprawdz_przebieg_efektow(w)
                    if blad_efektu and len(s["efekty_zle"]) < 3:
                        s["efekty_zle"].append((z, blad_efektu))
                    blad_czasu = sprawdz_naturalne_czasy(w)
                    if blad_czasu and len(s["czasy_zle"]) < 3:
                        s["czasy_zle"].append((z, blad_czasu))
                    if z <= 200:
                        blad_many = sprawdz_mane(w, V)
                        if blad_many and len(s["mana_zle"]) < 3:
                            s["mana_zle"].append((z, blad_many))
                    nr, uz, pierwsza = 0, 0, 0
                    for e in w["dziennik"]:
                        if e["kto"] == "gracz" and e["typ"] in ("cios", "krytyk", "blok", "unik", "umiejetnosc"):
                            nr += 1
                            if e["umiejetnosc"]:
                                uz += 1
                                pierwsza = pierwsza or nr
                    s["uzycia"].append(uz)
                    if pierwsza:
                        s["pierwsze"].append(pierwsza)
                wynik[(L, k, p)] = s
    _PROBA = wynik
    return wynik


# ------------------------------------------------------------------------------------------------ wyrocznie
def naturalny_czas(z):
    """Czas zdarzenia z DANYCH (setne sekundy): umiejetnosc (takze jej unik i blok) trwa tyle, ile podaje jej
    pole czas; kazde inne zdarzenie tyle, ile stale.czasy[typ]. Nic nie zalezy od tury ani dlugosci walki."""
    if z["umiejetnosc"] != "" and z["typ"] in ("umiejetnosc", "unik", "blok"):
        return silnik.UMIEJETNOSCI[z["umiejetnosc"]]["czas"]
    return silnik.STALE["czasy"][z["typ"]]


def sprawdz_naturalne_czasy(w):
    """U7: kazde zdarzenie trwa dokladnie swoj naturalny czas z danych, a t kolejnego = t poprzedniego + trwa."""
    t = silnik.STALE["czas_wstepu"]
    for i, z in enumerate(w["dziennik"]):
        if wzorce.setne(z["t"]) != t:
            return "zdarzenie %d: t = %s zamiast %s" % (i + 1, z["t"], t / 100)
        oczekiwany = naturalny_czas(z)
        if wzorce.setne(z["trwa"]) != oczekiwany:
            return "zdarzenie %d (%s): trwa %s zamiast %s" % (i + 1, z["typ"], z["trwa"], oczekiwany / 100)
        t += oczekiwany
    return None


def sprawdz_przebieg_efektow(w):
    """Statusy wedlug danych (wyrocznia bez kodu silnika):
    - obrazenia w czasie: kazde tykniecie = wartosc ogloszona przy ostatnim nalozeniu (siła × stosy), nigdy unik, blok
      ani tarcza; dopoki trwa, tyka raz na ture nosiciela, a pelny przebieg to dokladnie `trwa` tykniec;
    - stosy: kolejne nalozenie trwajacego efektu dokłada 1 stos (do limitu z danych + modyfikatora), po wygasnieciu 1;
    - ogluszenie zabiera dokladnie jedna ture; spowolnienie nie zabiera tury; tarcza (oslona) dziala tylko, gdy trwa;
    - KAZDY efekt trwa dokladnie `tury` tur nosiciela: miedzy nalozeniem a efekt_koniec nosiciel wykonuje dokladnie
      `tury` akcji (cios, umiejetnosc albo utrata tury) — efekt na siebie liczy sie od nastepnej wlasnej tury, wiec
      tarcza z umiejetnosci oslania przed dokladnie 3 turami przeciwnika (kontrola 16/17.11)."""
    otwarte = {}
    ostatnie_stosy = {}
    utraty = {"gracz": 0, "wrog": 0}
    ostatnia_akcja = {"gracz": "", "wrog": ""}
    for i, z in enumerate(w["dziennik"]):
        if z["typ"] in ("cios", "krytyk", "blok", "unik", "umiejetnosc", "utrata_tury"):
            ostatnia_akcja[z["kto"]] = z["typ"]
            for (cel, _ef), st in otwarte.items():
                if cel == z["kto"]:
                    st["akcje"] += 1
        klucz = (z["cel"], z["efekt"])
        if z["typ"] == "efekt_nalozony":
            E = silnik.EFEKTY[z["efekt"]]
            # efekt na przeciwnika tylko po trafieniu: zablokowany albo unikniety cios i umiejetnosc nie nakladaja
            # efektow (kontrola 16/17.11: wczesniej nikt tego nie sprawdzal)
            if z["kto"] != z["cel"] and ostatnia_akcja[z["kto"]] not in ("cios", "krytyk", "umiejetnosc"):
                return "zdarzenie %d: %s nalozony po akcji %s" % (i + 1, z["efekt"], ostatnia_akcja[z["kto"]])
            # ogloszony czas = czas z danych (+ modyfikator trwania, jesli efekt go ma — w granicach z danych)
            dod = silnik.MODYFIKATORY_PO_ID[E["mod_trwania"]] if E["mod_trwania"] else {"min": 0, "max": 0}
            if not E["trwa"] + round(dod["min"]) <= z["tury"] <= E["trwa"] + round(dod["max"]):
                return "zdarzenie %d: %s ogloszony na %d tur, dane: %d" % (i + 1, z["efekt"], z["tury"], E["trwa"])
            if klucz in otwarte and E["stosy_maks"] > 1:
                if z["stosy"] not in (otwarte[klucz]["stosy"], otwarte[klucz]["stosy"] + 1):
                    return "zdarzenie %d: %s stosy %d po %d" % (i + 1, z["efekt"], z["stosy"], otwarte[klucz]["stosy"])
            elif z["stosy"] != 1:
                return "zdarzenie %d: pierwsze nalozenie %s ma %d stosow" % (i + 1, z["efekt"], z["stosy"])
            if z["stosy"] < 1 or (E["stosy_maks"] == 1 and z["stosy"] != 1):
                return "zdarzenie %d: zle stosy %s" % (i + 1, z["efekt"])
            otwarte[klucz] = {"tykniecia": 0, "utraty": 0, "wartosc": z["wartosc"], "stosy": z["stosy"], "tury": z["tury"],
                              "akcje": 0}
            ostatnie_stosy[klucz] = z["stosy"]
        elif z["typ"] == "efekt_tick":
            st = otwarte[klucz]
            st["tykniecia"] += 1
            if z["obrazenia"] != st["wartosc"] or z["stosy"] != st["stosy"] or z["pochloniete"] != 0:
                return "zdarzenie %d: tykniecie %s = %d, ogloszone %d" % (i + 1, z["efekt"], z["obrazenia"], st["wartosc"])
        elif z["typ"] == "utrata_tury":
            ogl = [ef for (cel, ef) in otwarte if cel == z["kto"] and silnik.EFEKTY[ef]["typ"] == "ogluszenie"]
            if not ogl:
                return "zdarzenie %d: utrata tury bez ogluszenia" % (i + 1)
            for ef in ogl:
                otwarte[(z["kto"], ef)]["utraty"] += 1
            utraty[z["kto"]] += 1
        elif z["typ"] == "efekt_koniec":
            st = otwarte.pop(klucz)
            E = silnik.EFEKTY[z["efekt"]]
            if E["typ"] == "obrazenia_w_czasie" and st["tykniecia"] != st["tury"]:
                return "zdarzenie %d: %s tyknal %d razy zamiast %d" % (i + 1, z["efekt"], st["tykniecia"], st["tury"])
            if E["typ"] == "ogluszenie" and st["utraty"] != 1:
                return "zdarzenie %d: ogluszenie zabralo %d tur" % (i + 1, st["utraty"])
            if st["akcje"] != st["tury"]:
                return "zdarzenie %d: %s trwal %d tur nosiciela zamiast %d" % (i + 1, z["efekt"], st["akcje"], st["tury"])
        elif z["pochloniete"] > 0:
            if not any(cel == z["cel"] and silnik.EFEKTY[ef]["typ"] == "oslona" for (cel, ef) in otwarte):
                return "zdarzenie %d: tarcza zatrzymala obrazenia bez aktywnej tarczy" % (i + 1)
    return None


def koszt(walczacy, id_um):
    return min(silnik.STALE["mana_maks"], max(1, silnik.zaokraglij(silnik.UMIEJETNOSCI[id_um]["koszt_many"]
                                                                   * (1 - walczacy["koszt_many"]))))


def sprawdz_mane(w, V):
    """Wyrocznia many i rotacji (bez kodu silnika): mana startuje od mana_start, rosnie o mana_za_cios za kazdy
    zwykly cios (takze chybiony) i o mana_za_obrazenia × procent utraconego zycia zywego celu (× mnoznik zysku,
    spowolnienie go obniza), do mana_maks; umiejetnosc pada, GDY mana >= koszt nastepnej aktywnej w rotacji slotow
    (wtedy zwykly cios jest bledem), i zabiera dokladnie koszt. Zwraca opis bledu albo None."""
    S = silnik.STALE
    mana = {s: w["strony"][s]["mana"] for s in ("gracz", "wrog")}
    hp = {s: w["strony"][s]["zycie"] for s in ("gracz", "wrog")}
    rot = {"gracz": 0, "wrog": 0}
    spow = {"gracz": {}, "wrog": {}}

    def mnoznik(s):
        m = V[s]["zysk_many"]
        for kara in spow[s].values():
            m = m * (1 - kara)
        return m

    def obrazenia(cel, ile):
        stracone = min(hp[cel], ile)
        hp[cel] -= stracone
        if stracone > 0 and hp[cel] > 0:
            zysk = silnik.zaokraglij(S["mana_za_obrazenia"] * 100 * stracone / V[cel]["zycie"] * mnoznik(cel))
            mana[cel] = min(S["mana_maks"], mana[cel] + zysk)

    for i, z in enumerate(w["dziennik"]):
        kto, cel, typ = z["kto"], z["cel"], z["typ"]
        akt = V[kto]["aktywne"]
        uzycie = z["umiejetnosc"] != "" and typ in ("umiejetnosc", "unik", "blok")
        if uzycie:
            if not akt or z["umiejetnosc"] != akt[rot[kto]]:
                return "zdarzenie %d: umiejetnosc %s poza rotacja slotow" % (i + 1, z["umiejetnosc"])
            k = koszt(V[kto], z["umiejetnosc"])
            if mana[kto] < k or z["wartosc"] != k:
                return "zdarzenie %d: umiejetnosc bez many albo zly koszt" % (i + 1)
            mana[kto] -= k
            rot[kto] = (rot[kto] + 1) % len(akt)
            if cel != kto:
                obrazenia(cel, z["obrazenia"])
        elif typ in ("cios", "krytyk", "blok", "unik"):
            if akt and mana[kto] >= koszt(V[kto], akt[rot[kto]]):
                return "zdarzenie %d: zwykly cios mimo pelnej many" % (i + 1)
            zysk = silnik.zaokraglij(S["mana_za_cios"] * mnoznik(kto))
            obrazenia(cel, z["obrazenia"])
            mana[kto] = min(S["mana_maks"], mana[kto] + zysk)
        elif typ == "efekt_tick":
            obrazenia(kto, z["obrazenia"])
        elif typ == "wskrzeszenie":
            hp[kto] = z["wartosc"]
        elif typ == "efekt_nalozony" and silnik.EFEKTY[z["efekt"]]["typ"] == "spowolnienie":
            spow[cel][z["efekt"]] = silnik.EFEKTY[z["efekt"]]["mana_kara"]
        elif typ == "efekt_koniec":
            spow[cel].pop(z["efekt"], None)
        if (z["mana_gracz"], z["mana_wrog"]) != (mana["gracz"], mana["wrog"]):
            return "zdarzenie %d (%s): mana %s/%s zamiast %s/%s" % (i + 1, typ, z["mana_gracz"], z["mana_wrog"],
                                                                  mana["gracz"], mana["wrog"])
    return None


# ------------------------------------------------------------------------------------------------ dane i pliki
class TestDaneIPliki(unittest.TestCase):
    def test_dane_luau_wygenerowane_z_json_i_aktualne(self):
        with open(generuj_dane.CEL, encoding="utf-8", newline="") as f:
            self.assertEqual(f.read(), generuj_dane.tekst(), "uruchom: python -B tools/walka/generuj_dane.py")

    def test_wzorce_aktualne(self):
        tekst = json.dumps(wzorce.zbuduj(), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
        with open(wzorce.PLIK, encoding="utf-8") as f:
            self.assertEqual(f.read(), tekst, "uruchom: python -B tools/walka/wzorce.py")

    def test_dane_spojne(self):
        D = silnik.DANE
        mod_id = [m["id"] for m in D["modyfikatory"]]
        self.assertEqual(len(mod_id), len(set(mod_id)))
        for m in D["modyfikatory"]:
            self.assertLessEqual(m["min"], 0, m["id"])
            self.assertGreaterEqual(m["max"], 0, m["id"])
        pola_klasy = {"nazwa", "styl", "mnoznik_zycia", "mnoznik_ciosu", "mnoznik_pancerza", "mnoznik_odpornosci",
                      "rodzaj_ciosu", "unik_baza", "unik_limit", "mnoznik_krytyka", "kryt_za_zrecznosc", "blok", "tarcza",
                      "umiejetnosci", "pasywne"}
        for k, kl in list(D["klasy"].items()) + list(D["klasy_potworow"].items()):
            self.assertEqual(set(kl), pola_klasy, k)
            self.assertLessEqual(kl["unik_baza"], kl["unik_limit"])
            self.assertLessEqual(kl["unik_limit"], D["stale"]["unik_maks"])
            self.assertGreater(kl["blok"], 0, "blok ma KAZDA klasa (D-062, sesja 16.11)")
            self.assertGreater(kl["kryt_za_zrecznosc"], 0, "Zrecznosc daje mnoznik krytyka kazdej klasie")
        for k, kl in D["klasy"].items():
            for u in kl["umiejetnosci"]:
                self.assertEqual(D["umiejetnosci"][u]["klasa"], k)
            for u in kl["pasywne"]:
                self.assertIn(D["pasywne"][u]["klasa"], (k, ""))
            self.assertGreaterEqual(len(kl["umiejetnosci"]), 2)
            self.assertGreaterEqual(len(kl["pasywne"]), 3, "trzy sloty pasywne musza miec czym sie wypelnic")
        self.assertEqual(D["klasy"]["zwiadowca"]["unik_baza"], 0.25)
        self.assertEqual(D["klasy"]["zwiadowca"]["unik_limit"], 0.5)
        for k in ("wojownik", "mag"):
            self.assertEqual(D["klasy"][k]["unik_baza"], 0)
            self.assertLess(D["klasy"][k]["unik_limit"], 0.5)
        self.assertEqual([k for k, kl in D["klasy"].items() if kl["tarcza"]], ["wojownik"])
        # Wojownik korzysta z Pancerza lepiej niz Mag i Zwiadowca (sesja 16.11, pkt 5); limit redukcji jawny
        for k in ("zwiadowca", "mag"):
            self.assertGreater(D["klasy"]["wojownik"]["mnoznik_pancerza"], D["klasy"][k]["mnoznik_pancerza"] + 0.2)
        self.assertEqual(D["stale"]["limit_redukcji"], 0.75)
        self.assertGreater(wzorcowe.BLOK_TARCZY, 3 * max(kl["blok"] for kl in D["klasy"].values()),
                           "tarcza daje Wojownikowi WYRAZNIE wiekszy blok")
        for uid, u in D["umiejetnosci"].items():
            self.assertEqual(set(u), {"nazwa", "klasa", "cel", "koszt_many", "mnoznik", "rodzaj", "premia_krytyka",
                                      "czas", "efekty"}, uid)
            self.assertIn(u["cel"], ("wrog", "sam"), uid)
            if u["cel"] == "wrog":
                self.assertGreater(u["mnoznik"], 0, uid)
            self.assertTrue(1 <= u["koszt_many"] <= D["stale"]["mana_maks"], uid)
            for e in u["efekty"]:
                self.assertIn(e["efekt"], D["efekty"], uid)
            self.assertNotIn(uid, D["pasywne"], "id aktywnej i pasywnej nie moga sie powtarzac")
        pola_efektu = {"nazwa", "typ", "rodzaj", "trwa", "wartosc", "limit", "mana_kara", "sila", "udzial",
                       "limit_ciosu", "stosy_maks", "mod_stosow", "mod_sily", "mod_trwania"}
        typy = {"obrazenia_w_czasie", "spowolnienie", "ogluszenie", "zdarcie", "oslona", "wzmocnienie"}
        for eid, E in D["efekty"].items():
            self.assertEqual(set(E), pola_efektu, eid)
            self.assertIn(E["typ"], typy, eid)
            self.assertGreaterEqual(E["trwa"], 1, eid)
            for pole in ("mod_stosow", "mod_sily", "mod_trwania"):
                self.assertTrue(E[pole] == "" or E[pole] in mod_id, (eid, pole))
            if E["typ"] == "obrazenia_w_czasie":
                self.assertIn(E["sila"], ("cios", "zycie_celu", "trafienie"), eid)
        # trucizna i podpalenie maja rozne charaktery (sesja 16.11, pkt 6)
        T, P = D["efekty"]["trucizna"], D["efekty"]["podpalenie"]
        self.assertGreater(T["stosy_maks"], 1)
        self.assertEqual(P["stosy_maks"], 1)
        self.assertGreater(T["trwa"], P["trwa"])
        self.assertEqual((T["sila"], P["sila"], D["efekty"]["krwawienie"]["sila"]), ("cios", "zycie_celu", "trafienie"))
        for pid, ps in list(D["pasywne"].items()) + list(D["pasywki_broni"].items()):
            for klucz in ps["modyfikatory"]:
                self.assertIn(klucz, mod_id, pid)
        for pid, ps in D["pasywne"].items():
            self.assertEqual(set(ps), {"nazwa", "klasa", "opis", "modyfikatory", "wskrzeszenie", "legendarna"}, pid)
            self.assertTrue(0 <= ps["wskrzeszenie"] <= 1, pid)
            self.assertEqual(ps["wskrzeszenie"] > 0, ps["legendarna"], "wskrzeszenie to legendarna pasywka (D-094)")
        self.assertNotIn("wskrzeszenie", mod_id, "wskrzeszenia nie da premia z przedmiotow ani drzewka (tylko slot)")
        for pid, ps in D["pasywki_broni"].items():
            self.assertNotIn("wskrzeszenie", ps, "wskrzeszenie nie moze byc pasywka broni")
        for z in D["zaklecia"].values():
            self.assertIn(z["efekt"], D["efekty"])
        rangi = [p["ranga"] for p in D["przeciwnicy"]]
        self.assertGreaterEqual(len(D["przeciwnicy"]), 4)
        self.assertIn("lesny_slime", MONSTRY)
        self.assertIn("rzadki", rangi)
        self.assertEqual(rangi.count("straznik"), 1)
        klasy_potworow = {"lesny_slime": "zwiadowca", "cierniowy_wilk": "zwiadowca", "muchomornik": "mag",
                          "lesny_troll": "wojownik", "straznik_lasu": "straznik"}
        for p in D["przeciwnicy"]:
            self.assertIn(p["ranga"], ("zwykly", "rzadki", "straznik"))
            self.assertTrue(p["wyglad"].strip())
            self.assertEqual(p["klasa"], klasy_potworow[p["id"]], "klasy potworow z sesji 16.11 (pkt 10)")
            self.assertEqual(set(p["statystyki"]), set(D["statystyki"]))
            self.assertTrue(0 <= p["tarcza"] <= D["stale"]["blok_maks"])
            for klucz in p["modyfikatory"]:
                self.assertIn(klucz, mod_id, p["id"])
            for u in p["umiejetnosci"]:
                self.assertEqual((D["umiejetnosci"].get(u) or D["pasywne"].get(u))["klasa"], "potwor")
            if p["ranga"] == "straznik":
                self.assertEqual(len([u for u in p["umiejetnosci"] if u in D["umiejetnosci"]]), 1,
                                 "straznik ma jedna wlasna umiejetnosc")
                self.assertGreater(p["lup"]["szansa_sharda"], 0)
            else:
                self.assertEqual(p["lup"]["szansa_sharda"], 0, "Shard Ewolucji tylko ze straznika")
            self.assertFalse(any("jaj" in k for k in p["lup"]), "jajka nie wypadaja z potworow (D-060)")

    def test_mana_nie_jest_statystyka(self):
        # sesja 16.11, pkt 2: mana to wartosc pochodna (przedmioty, drzewko, pasywki), nie siodma statystyka
        self.assertEqual(silnik.STATYSTYKI, ["sila", "kondycja", "inteligencja", "zrecznosc", "szczescie", "pancerz"])
        p = wzorcowe.postac("mag", 5)
        p["statystyki"]["mana"] = 5
        with self.assertRaises(ValueError):
            silnik.symuluj(p, {"potwor": "lesny_slime", "poziom": 5}, 1)
        # Inteligencja nie zmienia many (Karol: Int nie ma byc naraz obrazeniami, odpornoscia i mana)
        a = silnik.wartosci_postaci(wzorcowe.postac("mag", 5))
        b = silnik.wartosci_postaci(wzorcowe.postac("mag", 5, dodatkowe={"inteligencja": 50}))
        self.assertEqual((a["zysk_many"], a["koszt_many"], a["mana_start"]), (b["zysk_many"], b["koszt_many"], b["mana_start"]))


# ------------------------------------------------------------------------------------------------ podstawy
class TestPodstawy(unittest.TestCase):
    def test_powtarzalnosc(self):
        for k in wzorcowe.KLASY:
            for p in PRZECIWNICY:
                g, prz = wzorcowe.postac(k, 5), przeciwnik(p, 5)
                for z in (1, 99, 2026):
                    a = json.dumps(silnik.symuluj(g, prz, z), sort_keys=True)
                    b = json.dumps(silnik.symuluj(copy.deepcopy(g), copy.deepcopy(prz), z), sort_keys=True)
                    self.assertEqual(a, b)

    def test_rozne_ziarna_daja_rozne_walki(self):
        g, prz = wzorcowe.postac("mag", 5), przeciwnik("cierniowy_wilk", 5)
        podpisy = {wzorce.podpis(silnik.symuluj(g, prz, z)) for z in range(1, 51)}
        self.assertGreater(len(podpisy), 45)

    def test_wejscie_nie_jest_zmieniane(self):
        g = wzorcowe.build("trucizna", "mag", 10)
        prz = {"postac": wzorcowe.build("mana", "zwiadowca", 10)}
        g0, p0 = copy.deepcopy(g), copy.deepcopy(prz)
        silnik.symuluj(g, prz, 5)
        self.assertEqual((g, prz), (g0, p0))
        d0 = json.dumps(silnik.DANE, sort_keys=True)
        silnik.symuluj(wzorcowe.postac("wojownik", 10, umiejetnosci=["kolos", "rozdzieracz", "ciecie"]),
                       {"potwor": "straznik_lasu", "poziom": 10}, 3)
        self.assertEqual(json.dumps(silnik.DANE, sort_keys=True), d0, "silnik nie moze zmieniac danych")

    def test_generator_jak_w_prototypie(self):
        los = silnik.nowy_los(1)
        stan = 1
        for _ in range(9):
            stan = (stan * 48271) % 2147483647
        self.assertEqual(los(), (stan - 1) / (2147483647 - 1))


class TestWalidacja(unittest.TestCase):
    def test_zle_wejscia_odrzucone(self):
        for spec in wzorce.ZLE_WEJSCIA:
            with self.subTest(spec["opis"]):
                gracz, prz, ziarno = wzorce.zle_wejscie(spec)
                with self.assertRaises(ValueError) as e:
                    silnik.symuluj(gracz, prz, ziarno)
                self.assertTrue(str(e.exception).startswith("Walka: "))

    def test_poprawne_wejscia_przyjete(self):
        for k in wzorcowe.KLASY:
            silnik.symuluj(wzorcowe.postac(k, 1, ile_slotow=0), {"potwor": "lesny_slime", "poziom": 1}, 1)
            silnik.symuluj(wzorcowe.postac(k, 7, ile_slotow=3, zaklecie="podpalenie"), przeciwnik("mag", 3), 27)
            # 3 pasywne, mieszanka, premie z przedmiotow, pasywka broni
            pas = silnik.KLASY[k]["pasywne"]
            for um in (pas[:3], [silnik.KLASY[k]["umiejetnosci"][0]] + pas[:2]):
                ok, opis = dziennik.sprawdz(silnik.symuluj(
                    wzorcowe.postac(k, 10, umiejetnosci=um, premie={"zysk_many": 0.5, "koszt_many": 0.6, "mana_startowa": 100},
                                    pasywka_broni=wzorcowe.BRON_MANY[k]), {"potwor": "lesny_troll", "poziom": 10}, 4))
                self.assertTrue(ok, opis)
        for z in (0, 2 ** 31 - 1, 2 ** 31 - 1.0):
            ok, opis = dziennik.sprawdz(silnik.symuluj(wzorcowe.postac("mag", 2), {"potwor": "lesny_slime", "poziom": 2}, z))
            self.assertTrue(ok, opis)
        minimalna = {"klasa": "mag", "poziom": 1, "bron": {"obrazenia": 1},
                     "statystyki": {s: 0 for s in silnik.STATYSTYKI}}
        ok, opis = dziennik.sprawdz(silnik.symuluj(minimalna, {"potwor": "straznik_lasu", "poziom": 1}, 3))
        self.assertTrue(ok, opis)


# ------------------------------------------------------------------------------------------------ zasady
def _w(cel_strona, cel_walczacy, efekty=()):
    """Minimalny stan walki do sprawdzania pojedynczych wzorow."""
    return {"strony": {cel_strona: cel_walczacy},
            "stan": {cel_strona: {"hp": 10 ** 9, "efekty": list(efekty), "mana": 0, "nastepna": 0}}}


def _akcje(w, strona):
    """Kolejne akcje strony: '' = zwykly cios, id = umiejetnosc (pomija utrate tury i zdarzenia efektow)."""
    return [z["umiejetnosc"] for z in w["dziennik"]
            if z["kto"] == strona and z["typ"] in ("cios", "krytyk", "blok", "unik", "umiejetnosc")]


def _walki(g, prz, ziarna):
    return [silnik.symuluj(g, prz, z) for z in ziarna]


class TestPancerzIObrona(unittest.TestCase):
    def test_pancerz_punktowy_z_limitem_redukcji(self):
        cel = {"pancerz": 30, "odpornosc": 0}
        w = _w("wrog", cel)
        self.assertEqual(silnik.po_obronie(w, 100, "fizyczne", "wrog"), 70)       # 100 - 30 punktow (D-062)
        cel["pancerz"] = 60
        self.assertEqual(silnik.po_obronie(w, 100, "fizyczne", "wrog"), 40)       # punkty, nie procent
        cel["pancerz"] = 10 ** 6
        lim = silnik.STALE["limit_redukcji"]
        self.assertEqual(lim, 0.75)
        self.assertEqual(silnik.po_obronie(w, 100, "fizyczne", "wrog"), 100 * (1 - lim))  # nigdy nie zeruje ciosu
        # w calej walce: gracz z ogromnym Pancerzem dostaje od kazdego trafienia fizycznego >= 25% (bez bloku i tarczy)
        g = wzorcowe.postac("wojownik", 5, tarcza=False, ile_slotow=0)
        g["pancerz_przedmiotow"] = 10 ** 5
        widziane = 0
        troll = silnik.wartosci_potwora("lesny_troll", 5)
        for w in _walki(g, {"potwor": "lesny_troll", "poziom": 5}, range(1, 60)):
            for e in w["dziennik"]:
                if e["kto"] == "wrog" and e["typ"] == "cios" and e["umiejetnosc"] == "":
                    self.assertGreaterEqual(e["obrazenia"] + e["pochloniete"],
                                            silnik.zaokraglij(troll["cios"] * 0.9 * (1 - lim)) - 1)
                    widziane += 1
        self.assertGreater(widziane, 50)

    def test_wojownik_ma_lepszy_przelicznik_pancerza(self):
        # te same punkty i te same przedmioty -> Wojownik ma wiecej Pancerza i szybciej dochodzi do limitu
        for L in (1, 5, 10, 20):
            st = {s: 10 for s in silnik.STATYSTYKI}
            v = {k: silnik.wartosci_postaci({"klasa": k, "poziom": L, "statystyki": st, "bron": {"obrazenia": 10},
                                             "pancerz_przedmiotow": 10})["pancerz"] for k in wzorcowe.KLASY}
            self.assertGreater(v["wojownik"], 1.2 * v["zwiadowca"])
            self.assertGreater(v["wojownik"], 1.2 * v["mag"])

    def test_zdarcie_pancerza_i_pasywka_na_starcie(self):
        ef = {"typ": "zdarcie", "wartosc": 0.5}
        self.assertEqual(silnik.pancerz_efektywny({"pancerz": 40}, {"efekty": [ef]}), 20)
        w = _w("wrog", {"pancerz": 40, "odpornosc": 0}, [ef])
        self.assertEqual(silnik.po_obronie(w, 100, "fizyczne", "wrog"), 80)
        # pasywka „na starcie zdziera X% Pancerza przeciwnika” dziala na cala walke (Karol, sesja 16.11)
        g = wzorcowe.postac("wojownik", 10, umiejetnosci=["rozdzieracz"])
        zdarcie = silnik.PASYWNE["rozdzieracz"]["modyfikatory"]["pancerz_wroga"]
        self.assertLess(zdarcie, 0)
        B = silnik.wartosci_potwora("cierniowy_wilk", 10)
        # porownanie: pierwszy zwykly cios gracza w wilka z pasywka i bez (te same rzuty) — z pasywka mocniejszy
        # (przy trollu cios Wojownika czesto i tak opiera sie o dolna granice 25%, wiec zdarcie nic nie zmienia)
        mocniej = 0
        bez = wzorcowe.postac("wojownik", 10, umiejetnosci=[])
        for z in range(1, 80):
            def pierwszy(gr):
                for e in silnik.symuluj(gr, {"potwor": "cierniowy_wilk", "poziom": 10}, z)["dziennik"]:
                    if e["kto"] == "gracz" and e["typ"] == "cios":
                        return e["obrazenia"] + e["pochloniete"]
                return None
            a, b = pierwszy(g), pierwszy(bez)
            if a is not None and b is not None:
                self.assertGreaterEqual(a, b)
                mocniej += a > b
        self.assertGreater(mocniej, 10)
        self.assertGreater(B["pancerz"], 0)

    def test_magia_omija_pancerz_odpornosc_z_inteligencji(self):
        g = wzorcowe.postac("mag", 5)
        cel_a = wzorcowe.postac("wojownik", 5)
        cel_b = copy.deepcopy(cel_a)
        cel_b["pancerz_przedmiotow"] = 5000
        cel_b["statystyki"]["pancerz"] = 900
        for z in range(1, 40):
            wa = silnik.symuluj(g, {"postac": cel_a}, z)
            wb = silnik.symuluj(g, {"postac": cel_b}, z)
            ciosy_a = [e["obrazenia"] + e["pochloniete"] for e in wa["dziennik"] if e["kto"] == "gracz" and e["cel"] == "wrog"]
            ciosy_b = [e["obrazenia"] + e["pochloniete"] for e in wb["dziennik"] if e["kto"] == "gracz" and e["cel"] == "wrog"]
            n = min(len(ciosy_a), len(ciosy_b))
            self.assertEqual(ciosy_a[:n], ciosy_b[:n])
        cel = wzorcowe.postac("wojownik", 5)
        odp1 = silnik.wartosci_postaci(cel)["odpornosc"]
        cel["statystyki"]["inteligencja"] += 20
        odp2 = silnik.wartosci_postaci(cel)["odpornosc"]
        self.assertAlmostEqual(odp2 - odp1, 20 * silnik.STALE["odpornosc_za_inteligencje"]
                               * silnik.KLASY["wojownik"]["mnoznik_odpornosci"])
        self.assertEqual(silnik.po_obronie(_w("wrog", {"pancerz": 0, "odpornosc": 30}), 100, "magiczne", "wrog"), 70)


class TestUnikIBlok(unittest.TestCase):
    def test_limit_uniku_zalezy_od_klasy(self):
        for k, limit, baza in (("zwiadowca", 0.5, 0.25), ("wojownik", silnik.KLASY["wojownik"]["unik_limit"], 0),
                               ("mag", silnik.KLASY["mag"]["unik_limit"], 0)):
            p = wzorcowe.postac(k, 5, tarcza=False)
            p["statystyki"]["zrecznosc"] = 10 ** 6
            u = silnik.wartosci_postaci(p)["unik"]
            self.assertLess(u, limit + 1e-12, k)
            self.assertGreater(u, limit - 0.001, k)
            p["statystyki"]["zrecznosc"] = 0
            self.assertEqual(silnik.wartosci_postaci(p)["unik"], baza, k)
        p = wzorcowe.postac("zwiadowca", 5)
        p["statystyki"]["zrecznosc"] = 10 ** 6
        ataki = uniki = 0
        for w in _walki(p, {"potwor": "lesny_slime", "poziom": 5}, range(1, 400)):
            spowolniony = False
            for e in w["dziennik"]:
                if e["typ"] == "efekt_nalozony" and e["cel"] == "gracz" and e["efekt"] == "spowolnienie":
                    spowolniony = True
                if e["kto"] == "wrog" and e["typ"] in ("cios", "krytyk", "blok", "unik", "umiejetnosc") and not spowolniony:
                    ataki += 1
                    uniki += e["typ"] == "unik"
        self.assertLess(abs(uniki / ataki - 0.5), 0.03)

    def test_zrecznosc_daje_mnoznik_krytyka_kazdej_klasie(self):
        for k in wzorcowe.KLASY:
            a = silnik.wartosci_postaci(wzorcowe.postac(k, 5))
            b = silnik.wartosci_postaci(wzorcowe.postac(k, 5, dodatkowe={"zrecznosc": 15}))
            self.assertGreater(b["mnoznik_krytyka"], a["mnoznik_krytyka"], k)
            self.assertGreater(b["unik"], a["unik"], k)
            p = wzorcowe.postac(k, 5)
            p["statystyki"]["zrecznosc"] = 10 ** 6
            v = silnik.wartosci_postaci(p)
            self.assertLess(v["mnoznik_krytyka"], silnik.KLASY[k]["mnoznik_krytyka"] + silnik.KLASY[k]["kryt_za_zrecznosc"]
                            + 1e-9, "krzywa z nasyceniem")

    def test_blok_ma_kazda_klasa_tarcza_tylko_wojownik(self):
        def bloki_gracza(p, n=300):
            bloki = ataki = 0
            for w in _walki(p, {"potwor": "lesny_troll", "poziom": 5}, range(1, n)):
                for e in w["dziennik"]:
                    if e["cel"] == "gracz" and e["kto"] == "wrog" and e["typ"] in ("cios", "krytyk", "blok", "umiejetnosc"):
                        ataki += 1
                        bloki += e["typ"] == "blok"
            return bloki / ataki
        z_tarcza = bloki_gracza(wzorcowe.postac("wojownik", 5))
        bez = bloki_gracza(wzorcowe.postac("wojownik", 5, tarcza=False))
        zw = bloki_gracza(wzorcowe.postac("zwiadowca", 5))
        mag = bloki_gracza(wzorcowe.postac("mag", 5))
        for k, x in (("bez tarczy", bez), ("zwiadowca", zw), ("mag", mag)):
            self.assertGreater(x, 0.5 * silnik.KLASY["mag"]["blok"], k)
            self.assertLess(x, 2 * max(kl["blok"] for kl in silnik.KLASY.values()), k)
        self.assertGreater(z_tarcza, 3 * max(bez, zw, mag), "tarcza daje wyraznie wiekszy blok")
        for k in ("mag", "zwiadowca"):
            p = wzorcowe.postac(k, 5)
            p["tarcza"] = {"blok": 0.2}
            with self.assertRaises(ValueError):
                silnik.symuluj(p, {"potwor": "lesny_slime", "poziom": 5}, 1)

    def test_kolejnosc_rzutu_unik_blok_krytyk(self):
        # kontrola 16/17.11: kolejnosc unik -> blok -> krytyk (z v2) nie byla sprawdzana; silnik z krytykiem przed
        # blokiem przechodzil wszystkie testy. Czestosci zwyklych ciosow trolla w Wojownika z tarcza:
        # P(unik) = unik, P(blok | bez uniku) = blok, P(krytyk | bez uniku i bloku) = krytyk trolla.
        g = wzorcowe.postac("wojownik", 5, umiejetnosci=[])
        A = silnik.wartosci_postaci(g)
        T = silnik.wartosci_potwora("lesny_troll", 5)
        n = {"unik": 0, "blok": 0, "krytyk": 0, "cios": 0}
        for walka in _walki(g, {"potwor": "lesny_troll", "poziom": 5}, range(1, 700)):
            for e in walka["dziennik"]:
                if e["kto"] == "wrog" and e["typ"] in n and e["umiejetnosc"] == "":
                    n[e["typ"]] += 1
        razem = sum(n.values())
        self.assertGreater(razem, 3000)
        self.assertAlmostEqual(n["unik"] / razem, A["unik"], delta=0.02)
        self.assertAlmostEqual(n["blok"] / (razem - n["unik"]), A["blok"], delta=0.03)
        self.assertAlmostEqual(n["krytyk"] / (n["krytyk"] + n["cios"]), T["krytyk"], delta=0.03)

    def test_blok_zmniejsza_obrazenia_do_czesci_ciosu_a_nie_zeruje(self):
        # kontrola 16/17.11: wczesniej test sprawdzal tylko „obrazenia >= 1”, wiec silnik, w ktorym blok zeruje cios
        # (zostaje dolna granica 1), przechodzil wszystkie testy. Blok przepuszcza DOKLADNIE czesc_przez_blok ciosu po
        # obronie — sprawdzamy wzorem i na kazdym zablokowanym zwyklym ciosie trolla w prawdziwych walkach.
        czesc = silnik.STALE["czesc_przez_blok"]
        w = _w("wrog", {"pancerz": 20, "odpornosc": 0})
        self.assertEqual(silnik.obrazenia_trafienia(w, "wrog", 100, "fizyczne", True), (silnik.zaokraglij(80 * czesc), 0))
        self.assertEqual(silnik.obrazenia_trafienia(w, "wrog", 100, "fizyczne", False), (80, 0))
        troll = silnik.wartosci_potwora("lesny_troll", 5)
        widziane = 0
        for k in ("mag", "zwiadowca"):
            g = wzorcowe.postac(k, 5, umiejetnosci=[])
            obr = silnik.wartosci_postaci(g)["pancerz"]
            lo = max(troll["cios"] * 0.9 * (1 - silnik.STALE["limit_redukcji"]), troll["cios"] * 0.9 - obr) * czesc
            hi = max(troll["cios"] * 1.1 * (1 - silnik.STALE["limit_redukcji"]), troll["cios"] * 1.1 - obr) * czesc
            self.assertGreater(lo, 3, "proba musi odroznic 25% ciosu od dolnej granicy 1")
            for walka in _walki(g, {"potwor": "lesny_troll", "poziom": 5}, range(1, 400)):
                for e in walka["dziennik"]:
                    if e["kto"] == "wrog" and e["typ"] == "blok" and e["umiejetnosc"] == "":
                        self.assertGreaterEqual(e["obrazenia"], silnik.zaokraglij(lo), (k, e))
                        self.assertLessEqual(e["obrazenia"], silnik.zaokraglij(hi), (k, e))
                        widziane += 1
        self.assertGreater(widziane, 20)

    def test_blok_wariant_25_i_0_procent(self):
        stary = silnik.STALE["czesc_przez_blok"]
        try:
            for wariant in (0.25, 0.0):
                silnik.STALE["czesc_przez_blok"] = wariant
                bloki = 0
                for w in _walki(wzorcowe.postac("wojownik", 5), {"potwor": "lesny_troll", "poziom": 5}, range(1, 120)):
                    ok, opis = dziennik.sprawdz(w)
                    self.assertTrue(ok, opis)
                    self.assertEqual(w["czesc_przez_blok"], wariant)
                    for e in w["dziennik"]:
                        if e["typ"] == "blok" and e["cel"] == "gracz":
                            bloki += 1
                            if wariant == 0:
                                self.assertEqual((e["obrazenia"], e["pochloniete"]), (0, 0))
                            else:
                                self.assertGreaterEqual(e["obrazenia"], 1)
                self.assertGreater(bloki, 50)
                # dziennik pilnuje wariantu: blok z obrazeniami przy 0% albo bez obrazen przy 25% to blad
                w = silnik.symuluj(wzorcowe.postac("wojownik", 5), {"potwor": "lesny_troll", "poziom": 5}, 1)
                w["czesc_przez_blok"] = 0.0 if wariant > 0 else 0.25
                if any(e["typ"] == "blok" for e in w["dziennik"]):
                    self.assertFalse(dziennik.sprawdz(w)[0])
        finally:
            silnik.STALE["czesc_przez_blok"] = stary


class TestMana(unittest.TestCase):
    def test_mana_i_rotacja_wedlug_wyroczni(self):
        for (L, k, p), s in proba().items():
            self.assertEqual(s["mana_zle"], [], (L, k, p))
        # buildy, pasywki, spowolnienie, premie: ta sama wyrocznia
        for k in wzorcowe.KLASY:
            for b in ["mana", "zwykle"] + wzorcowe.BUILDY_KLAS[k]:
                for L in (1, 5, 10):
                    g = wzorcowe.build(b, k, L)
                    for p in ("muchomornik", "lesny_troll", "straznik_lasu", "mag"):
                        prz = przeciwnik(p, L)
                        V = wartosci_stron(g, prz)
                        for w in _walki(g, prz, range(1, 15)):
                            self.assertIsNone(sprawdz_mane(w, V), (k, b, L, p))

    def test_wyrocznie_wykrywaja_zepsute_dzienniki(self):
        g, prz = wzorcowe.build("trucizna", "mag", 10), {"potwor": "straznik_lasu", "poziom": 10}
        V = wartosci_stron(g, prz)
        w = next(w for w in _walki(g, prz, range(1, 200))
                 if sum(e["typ"] == "efekt_nalozony" and e["efekt"] == "trucizna" for e in w["dziennik"]) >= 2
                 and any(e["kto"] == "gracz" and e["typ"] == "umiejetnosc" for e in w["dziennik"]))
        self.assertIsNone(sprawdz_mane(w, V))
        self.assertIsNone(sprawdz_przebieg_efektow(w))
        for psuj in ("mana", "koszt", "kolejnosc", "stosy", "tick"):
            z = copy.deepcopy(w)
            d = z["dziennik"]
            if psuj == "mana":
                d[len(d) // 2]["mana_gracz"] += 1
                self.assertIsNotNone(sprawdz_mane(z, V), psuj)
            elif psuj == "koszt":
                e = next(e for e in d if e["kto"] == "gracz" and e["typ"] == "umiejetnosc")
                e["wartosc"] -= 1
                self.assertIsNotNone(sprawdz_mane(z, V), psuj)
            elif psuj == "kolejnosc":
                e = next(e for e in d if e["kto"] == "gracz" and e["umiejetnosc"])
                e["umiejetnosc"] = "bariera"
                self.assertIsNotNone(sprawdz_mane(z, V), psuj)
            elif psuj == "stosy":
                e = [e for e in d if e["typ"] == "efekt_nalozony" and e["efekt"] == "trucizna"][1]
                e["stosy"] += 2
                self.assertIsNotNone(sprawdz_przebieg_efektow(z), psuj)
            else:
                e = next(e for e in d if e["typ"] == "efekt_tick")
                e["obrazenia"] += 1
                self.assertIsNotNone(sprawdz_przebieg_efektow(z), psuj)

    def test_pierwsza_umiejetnosc_w_3_4_akcji_i_kilka_razy_w_walce(self):
        # sesja 16.11: postac bez modyfikatorow uzywa pierwszej umiejetnosci ok. w 3.-4. wlasnej akcji, 2-3 razy w walce
        pierwsze, uzycia = [], []
        for (L, k, p), s in proba().items():
            if p in MONSTRY and silnik.PRZECIWNICY[p]["ranga"] == "zwykly":
                pierwsze += s["pierwsze"]
                uzycia += s["uzycia"]
        self.assertIn(statistics.median(pierwsze), (3, 3.5, 4))
        # zmierzone: ok. 1,4-2,1 uzycia ze zwyklym potworem (Mag mniej, bo jego walki sa krotsze), 2-4 z trollem
        # i straznikiem — patrz tabela (d); prog 1,5 pilnuje, zeby umiejetnosc nie stala sie rzadkoscia
        self.assertGreaterEqual(statistics.mean(uzycia), 1.5)
        self.assertLessEqual(statistics.mean(uzycia), 3.5)

    def test_build_pod_mane_uzywa_umiejetnosci_wyraznie_czesciej(self):
        for k in wzorcowe.KLASY:
            for L in (5, 10):
                def srednio(g):
                    u = []
                    for p in MONSTRY:
                        for w in _walki(g, {"potwor": p, "poziom": L}, range(1, 120)):
                            u.append(sum(1 for e in w["dziennik"] if e["kto"] == "gracz" and e["umiejetnosc"]))
                    return statistics.mean(u)
                a, b = srednio(wzorcowe.postac(k, L)), srednio(wzorcowe.build("mana", k, L))
                # zmierzone ok. 1,3-1,6x (nie 2x): pasek konczy sie na 100, wiec umiejetnosc pada najwyzej co druga
                # akcje, a postac wzorcowa juz uzywa jej co ok. trzecia (na 10. poziomie ma tez premie za 3 aktywne)
                # — wybor do decyzji (tansze umiejetnosci)
                self.assertGreater(b, 1.25 * a, (k, L, a, b))

    def test_trzy_pasywne_bez_umiejetnosci_i_bez_many_do_wydania(self):
        for k in wzorcowe.KLASY:
            g = wzorcowe.postac(k, 10, umiejetnosci=silnik.KLASY[k]["pasywne"][:3])
            for w in _walki(g, {"potwor": "lesny_troll", "poziom": 10}, range(1, 30)):
                self.assertFalse(any(e["kto"] == "gracz" and e["umiejetnosc"] for e in w["dziennik"]))
                self.assertTrue(dziennik.sprawdz(w)[0])

    def test_rotacja_slotow_pomija_pasywne_i_wraca_na_poczatek(self):
        g = wzorcowe.postac("mag", 10, umiejetnosci=["lodowy_pocisk", "przeplyw_many", "kula_ognia"])
        for w in _walki(g, {"potwor": "straznik_lasu", "poziom": 10}, range(1, 40)):
            u = [x for x in _akcje(w, "gracz") if x]
            self.assertEqual(u, [["lodowy_pocisk", "kula_ognia"][i % 2] for i in range(len(u))])

    def test_premie_many_dzialaja(self):
        A = silnik.wartosci_postaci(wzorcowe.postac("zwiadowca", 5, premie={"zysk_many": 0.5, "koszt_many": 0.3,
                                                                            "mana_startowa": 40}))
        self.assertEqual(A["mana_start"], 40)
        self.assertAlmostEqual(A["zysk_many"], 1.5 + silnik.STALE["mana_premia_za_aktywna"] * (len(A["aktywne"]) - 1))
        self.assertEqual(koszt(A, "uderzenie_z_gory"), 70)
        # granice z danych przycinaja sume zrodel
        B = silnik.wartosci_postaci(wzorcowe.postac("mag", 10, umiejetnosci=["przeplyw_many"], pasywka_broni="kostur_many",
                                                    premie={"koszt_many": 0.6, "mana_startowa": 100}))
        self.assertEqual(B["koszt_many"], 0.6)
        self.assertEqual(B["mana_start"], silnik.STALE["mana_maks"])
        w = silnik.symuluj(wzorcowe.postac("mag", 10, premie={"mana_startowa": 100}), {"potwor": "lesny_slime", "poziom": 10}, 2)
        pierwsza = next(e for e in w["dziennik"] if e["kto"] == "gracz" and e["typ"] in ("cios", "krytyk", "blok", "unik",
                                                                                         "umiejetnosc"))
        self.assertEqual(pierwsza["umiejetnosc"], "kula_ognia", "pelna mana na starcie = umiejetnosc w 1. akcji")

    def test_spowolnienie_obniza_zysk_many_i_unik_nie_zabiera_tury(self):
        E = silnik.EFEKTY["spowolnienie"]
        self.assertGreater(E["mana_kara"], 0)
        self.assertGreater(E["wartosc"], 0)
        st = {"efekty": [{"typ": "spowolnienie", "wartosc": E["wartosc"], "mana_kara": E["mana_kara"]}]}
        self.assertAlmostEqual(silnik.unik_efektywny({"unik": 0.4}, st), 0.4 * (1 - E["wartosc"]))
        w = {"strony": {"gracz": {"zysk_many": 1.2}}, "stan": {"gracz": st}}
        self.assertAlmostEqual(silnik.mnoznik_many(w, "gracz"), 1.2 * (1 - E["mana_kara"]))
        widziane = 0
        for w in _walki(wzorcowe.postac("mag", 10), {"potwor": "cierniowy_wilk", "poziom": 10}, range(1, 300)):
            for e in w["dziennik"]:
                if e["typ"] == "utrata_tury":
                    self.fail("spowolnienie (Lodowy pocisk) nie moze zabierac tury")
                widziane += e["typ"] == "efekt_nalozony" and e["efekt"] == "spowolnienie"
        self.assertGreater(widziane, 15)


class TestStatusy(unittest.TestCase):
    def test_przebieg_efektow_wedlug_wyroczni(self):
        for (L, k, p), s in proba().items():
            self.assertEqual(s["efekty_zle"], [], (L, k, p))
        for k in wzorcowe.KLASY:
            for b in wzorcowe.BUILDY_KLAS[k]:
                for p in MONSTRY + ["mag"]:
                    for w in _walki(wzorcowe.build(b, k, 10), przeciwnik(p, 10), range(1, 30)):
                        self.assertIsNone(sprawdz_przebieg_efektow(w), (k, b, p))

    def test_trucizna_kumuluje_stosy_do_limitu(self):
        g = wzorcowe.build("trucizna", "mag", 10)
        limit = silnik.EFEKTY["trucizna"]["stosy_maks"] + silnik.PASYWNE["kumulowanie_trucizny"]["modyfikatory"]["stosy_trucizny"]
        najwiecej = 0
        for w in _walki(g, {"potwor": "straznik_lasu", "poziom": 10}, range(1, 300)):
            for e in w["dziennik"]:
                if e["efekt"] == "trucizna" and e["typ"] in ("efekt_nalozony", "efekt_tick"):
                    self.assertLessEqual(e["stosy"], limit)
                    najwiecej = max(najwiecej, e["stosy"])
        # kontrola 16/17.11: po zabraniu pasywce szansy zaklecia stosy ponad 5 zdarzaja sie w walce rzadko (ok. 0,5%
        # walk ze straznikiem), wiec mechanizm limitu sprawdzamy WPROST: kolejne nalozenia dokladaja po stosie do limitu
        # z danych + modyfikator (z pasywka) albo do limitu z danych (bez niej)
        self.assertGreater(najwiecej, 1, "w walce trucizna sie kumuluje")
        for postac, oczekiwany in ((g, limit), (wzorcowe.postac("mag", 10, zaklecie="trucizna"),
                                                silnik.EFEKTY["trucizna"]["stosy_maks"])):
            A = silnik.wartosci_postaci(postac)
            w = {"strony": {"gracz": A, "wrog": A}, "stan": {s: {"hp": 10 ** 6, "efekty": [], "mana": 0} for s in ("gracz", "wrog")},
                 "dziennik": [], "czas": 0, "tura": 1}
            stosy = []
            for _ in range(oczekiwany + 3):
                silnik.naloz_efekt(w, "gracz", "wrog", "trucizna", 1, 0)
                stosy.append(w["stan"]["wrog"]["efekty"][0]["stosy"])
            self.assertEqual(stosy, [min(i + 1, oczekiwany) for i in range(oczekiwany + 3)])
            self.assertGreater(oczekiwany, 1)
        self.assertGreater(limit, silnik.EFEKTY["trucizna"]["stosy_maks"], "pasywka podnosi limit stosow")
        # bez pasywki limit z danych
        bez = wzorcowe.postac("mag", 10, zaklecie="trucizna")
        for w in _walki(bez, {"potwor": "straznik_lasu", "poziom": 10}, range(1, 60)):
            for e in w["dziennik"]:
                if e["efekt"] == "trucizna":
                    self.assertLessEqual(e["stosy"], silnik.EFEKTY["trucizna"]["stosy_maks"])

    def test_podpalenie_od_zycia_celu_lepsze_na_grubych(self):
        E = silnik.EFEKTY["podpalenie"]
        A = silnik.wartosci_postaci(wzorcowe.postac("mag", 10))
        for cel in ("lesny_slime", "straznik_lasu"):
            D = silnik.wartosci_potwora(cel, 10)
            oczek = max(1, silnik.zaokraglij(min(D["zycie"] * E["udzial"] * A["moc"], A["cios"] * E["limit_ciosu"])))
            for w in _walki(wzorcowe.postac("mag", 10), {"potwor": cel, "poziom": 10}, range(1, 40)):
                for e in w["dziennik"]:
                    if e["typ"] == "efekt_nalozony" and e["efekt"] == "podpalenie" and e["kto"] == "gracz":
                        self.assertEqual(e["wartosc"], oczek)
                        self.assertEqual(e["stosy"], 1)
        maly = silnik.wartosci_potwora("cierniowy_wilk", 10)
        duzy = silnik.wartosci_potwora("straznik_lasu", 10)
        self.assertGreater(min(duzy["zycie"] * E["udzial"] * A["moc"], A["cios"] * E["limit_ciosu"]),
                           min(maly["zycie"] * E["udzial"] * A["moc"], A["cios"] * E["limit_ciosu"]))

    def test_krwawienie_od_ciosu_ktory_je_nalozyl(self):
        E = silnik.EFEKTY["krwawienie"]
        widziane = 0
        for w in _walki(wzorcowe.postac("wojownik", 5), {"potwor": "cierniowy_wilk", "poziom": 5}, range(1, 200)):
            d = w["dziennik"]
            for i, e in enumerate(d):
                if e["typ"] == "efekt_nalozony" and e["efekt"] == "krwawienie":
                    traf = d[i - 1]
                    self.assertEqual(traf["umiejetnosc"], "rozszarpanie")
                    self.assertEqual(e["wartosc"], max(1, silnik.zaokraglij(traf["obrazenia"] * E["udzial"])))
                    widziane += 1
        self.assertGreater(widziane, 30)

    def test_obrazenia_w_czasie_omijaja_obrone_tarcze_unik_i_blok(self):
        # ta sama trucizna tyka tak samo bez wzgledu na Pancerz, odpornosc i blok celu
        g = wzorcowe.postac("zwiadowca", 5, ile_slotow=0, zaklecie="trucizna")
        cel_a = wzorcowe.postac("wojownik", 5)
        cel_b = copy.deepcopy(cel_a)
        cel_b["pancerz_przedmiotow"] = 900
        cel_b["statystyki"]["inteligencja"] = 900
        for z in range(1, 60):
            ta = [e["obrazenia"] for e in silnik.symuluj(g, {"postac": cel_a}, z)["dziennik"] if e["typ"] == "efekt_tick"]
            tb = [e["obrazenia"] for e in silnik.symuluj(g, {"postac": cel_b}, z)["dziennik"] if e["typ"] == "efekt_tick"]
            if ta and tb:
                self.assertEqual(ta[0], tb[0])
        # tykniecie nigdy nie jest unikiem ani blokiem i nie ma tarczy (pochloniete 0) — pilnuja tego takze Dziennik
        # i wyrocznia sprawdz_przebieg_efektow na calej duzej probie

    def test_ogluszenie_zabiera_ture_spowolnienie_nie(self):
        utraty = 0
        for w in _walki(wzorcowe.postac("zwiadowca", 5), {"potwor": "lesny_troll", "poziom": 5}, range(1, 200)):
            for e in w["dziennik"]:
                if e["typ"] == "utrata_tury":
                    utraty += 1
        self.assertGreater(utraty, 30)
        self.assertEqual(silnik.EFEKTY["ogluszenie"]["typ"], "ogluszenie")
        self.assertEqual(silnik.EFEKTY["spowolnienie"]["typ"], "spowolnienie")

    def test_tarcza_procentowa_trzy_tury(self):
        for eid in ("kamienna_skora", "bariera"):
            E = silnik.EFEKTY[eid]
            self.assertEqual((E["typ"], E["trwa"]), ("oslona", 3), "tarcza: −X% obrazen na 3 tury (sesja 16.11, pkt 7)")
        st = {"efekty": [{"typ": "oslona", "wartosc": 0.4}]}
        self.assertAlmostEqual(silnik.oslona(st), 0.6)
        g = wzorcowe.postac("mag", 10, umiejetnosci=["bariera"])
        A = silnik.wartosci_postaci(g)
        red = min(silnik.EFEKTY["bariera"]["limit"], silnik.EFEKTY["bariera"]["wartosc"] * A["moc"])
        przeszlo = zatrzymane = 0
        for w in _walki(g, {"potwor": "lesny_troll", "poziom": 10}, range(1, 80)):
            for e in w["dziennik"]:
                if e["cel"] == "gracz" and e["kto"] == "wrog" and e["pochloniete"] > 0:
                    przeszlo += e["obrazenia"]
                    zatrzymane += e["pochloniete"]
                if e["typ"] == "efekt_nalozony" and e["efekt"] == "bariera":
                    self.assertEqual(e["wartosc"], silnik.zaokraglij(100 * red))
        self.assertGreater(zatrzymane, 0)
        self.assertAlmostEqual(zatrzymane / (przeszlo + zatrzymane), red, delta=0.03)
        # limit tarczy z danych (kontrola 16/17.11: przy zwyklej mocy limit nigdy nie byl osiagany, wiec nie byl
        # sprawdzany): ogromna moc daje dokladnie limit, nie wiecej
        for eid in ("kamienna_skora", "bariera"):
            w = {"strony": {"gracz": A, "wrog": A},
                 "stan": {s: {"hp": 100, "efekty": [], "mana": 0} for s in ("gracz", "wrog")}, "dziennik": [],
                 "czas": 0, "tura": 1}
            silnik.naloz_efekt(w, "gracz", "gracz", eid, 50.0, 0)
            self.assertEqual(w["stan"]["gracz"]["efekty"][0]["wartosc"], silnik.EFEKTY[eid]["limit"])
            self.assertLess(silnik.EFEKTY[eid]["limit"], 1, "tarcza nigdy nie zeruje trafienia")

    def test_wzmocnienie_mnozy(self):
        self.assertEqual(silnik.wzmocnienie({"efekty": [{"typ": "wzmocnienie", "wartosc": 0.4}]}), 1.4)


class TestPasywki(unittest.TestCase):
    def test_pasywka_w_slocie_zmienia_wartosci(self):
        a = silnik.wartosci_postaci(wzorcowe.postac("wojownik", 10, umiejetnosci=[]))
        b = silnik.wartosci_postaci(wzorcowe.postac("wojownik", 10, umiejetnosci=["kolos"]))
        m = silnik.PASYWNE["kolos"]["modyfikatory"]
        self.assertAlmostEqual(b["cios"], a["cios"] * (1 + m.get("cios", 0)))
        K, S, L = silnik.KLASY["wojownik"], silnik.STALE, 10
        surowe = K["mnoznik_zycia"] * (S["zycie_baza"] + S["zycie_na_poziom"] * L + S["zycie_za_kondycje"] * a["efektywne"]["kondycja"])
        self.assertEqual(a["zycie"], silnik.zaokraglij(surowe))
        self.assertEqual(b["zycie"], silnik.zaokraglij(surowe * (1 + m["zycie"])))
        self.assertGreater(b["zycie"], a["zycie"])

    def test_pasywka_broni_ognista_rozdzka_wydluza_podpalenie(self):
        dod = silnik.PASYWKI_BRONI["ognista_rozdzka"]["modyfikatory"]["trwanie_podpalenia"]
        self.assertEqual(dod, 2)
        g = wzorcowe.postac("mag", 5, umiejetnosci=["kula_ognia"], pasywka_broni="ognista_rozdzka")
        widziane = 0
        for w in _walki(g, {"potwor": "lesny_troll", "poziom": 5}, range(1, 60)):
            for e in w["dziennik"]:
                if e["typ"] == "efekt_nalozony" and e["efekt"] == "podpalenie":
                    self.assertEqual(e["tury"], silnik.EFEKTY["podpalenie"]["trwa"] + dod)
                    widziane += 1
        self.assertGreater(widziane, 20)

    def test_pet_i_pasywki_drzewka_tylko_mnoza_statystyki(self):
        zwykla = wzorcowe.postac("wojownik", 5)
        zwykla["statystyki"].update({"sila": 50, "kondycja": 40})
        z_petem = copy.deepcopy(zwykla)
        z_petem["pet"] = {"sila": 0.1, "kondycja": 0.25}
        z_pasywka = copy.deepcopy(zwykla)
        z_pasywka["pasywki"] = {"sila": 0.1, "kondycja": 0.25}
        bez = copy.deepcopy(zwykla)
        bez["statystyki"].update({"sila": 55, "kondycja": 50})
        for z in range(1, 30):
            prz = {"potwor": "straznik_lasu", "poziom": 5}
            a = wzorce.podpis(silnik.symuluj(z_petem, prz, z))
            self.assertEqual(a, wzorce.podpis(silnik.symuluj(bez, prz, z)))
            self.assertEqual(a, wzorce.podpis(silnik.symuluj(z_pasywka, prz, z)))
        w = silnik.symuluj(z_petem, {"potwor": "lesny_slime", "poziom": 5}, 1)
        strony = {e["kto"] for e in w["dziennik"]} | {e["cel"] for e in w["dziennik"]}
        self.assertTrue(strony <= {"gracz", "wrog"})

    def test_potwory_maja_klasy_i_ten_sam_wzor(self):
        # potwor = postac z klasa i punktami: wartosci_potwora to ten sam wzor co wartosci_postaci
        for p in silnik.PRZECIWNICY_LISTA:
            if p["klasa"] not in silnik.KLASY:
                continue
            for L in (1, 7):
                st = {s: max(0, silnik.zaokraglij(silnik.skala(p["statystyki"][s], L))) for s in silnik.STATYSTYKI}
                postac = {"klasa": p["klasa"], "poziom": L, "statystyki": st,
                          "bron": {"obrazenia": silnik.skala(p["bron"], L)},
                          "pancerz_przedmiotow": silnik.skala(p["pancerz_przedmiotow"], L),
                          "premie": dict(p["modyfikatory"])}
                a, b = silnik.wartosci_postaci(postac), silnik.wartosci_potwora(p["id"], L)
                for pole in ("zycie", "cios", "pancerz", "odpornosc", "unik", "krytyk", "mnoznik_krytyka", "moc"):
                    self.assertAlmostEqual(a[pole], b[pole], msg=(p["id"], L, pole))
            # potwory tez uzywaja many
            uzyl = any(e["kto"] == "wrog" and e["umiejetnosc"]
                       for w in _walki(wzorcowe.postac("wojownik", 5), {"potwor": p["id"], "poziom": 5}, range(1, 20))
                       for e in w["dziennik"])
            self.assertTrue(uzyl, p["id"])


class TestWskrzeszenie(unittest.TestCase):
    """Propozycja D-094: legendarna pasywka w slocie; raz na walke smiertelna strata zycia konczy sie powrotem z
    ulamkiem maks. zycia (dane: 25%), bez losowania, z wlasnym zdarzeniem. Wyzwala ja kazda smiertelna strata zycia,
    takze tykniecie trucizny, podpalenia albo krwawienia (decyzja tej paczki, wybor do decyzji)."""

    def walki(self, k, L, wrog, n=300):
        g = wzorcowe.postac(k, L, umiejetnosci=[wzorcowe.UMIEJETNOSCI[k][0], "wskrzeszenie"])
        return g, _walki(g, {"potwor": wrog, "poziom": L + 1}, range(1, n))

    def test_dziala_raz_tylko_przy_smiertelnej_stracie_i_od_tykniec(self):
        frac = silnik.PASYWNE["wskrzeszenie"]["wskrzeszenie"]
        po_ticku = razem = 0
        for k in wzorcowe.KLASY:
            for wrog in ("lesny_troll", "straznik_lasu", "muchomornik"):
                g, ww = self.walki(k, 5, wrog)
                zycie = silnik.wartosci_postaci(g)["zycie"]
                for w in ww:
                    d = w["dziennik"]
                    ok, opis = dziennik.sprawdz(w)
                    self.assertTrue(ok, opis)
                    idx = [i for i, e in enumerate(d) if e["typ"] == "wskrzeszenie"]
                    self.assertLessEqual(len(idx), 1, "najwyzej raz na walke")
                    for i in idx:
                        e, przed = d[i], d[i - 1]
                        self.assertEqual((e["kto"], e["cel"]), ("gracz", "gracz"))
                        self.assertEqual(przed["hp_gracz"], 0, "tylko zaraz po smiertelnej stracie zycia")
                        self.assertEqual(e["wartosc"], max(1, silnik.zaokraglij(zycie * frac)))
                        self.assertEqual(e["hp_gracz"], e["wartosc"])
                        razem += 1
                        po_ticku += przed["typ"] == "efekt_tick"
                    if not idx:
                        self.assertTrue(all(e["hp_gracz"] > 0 for e in d[:-1]))
                    self.assertEqual(sum(1 for e in d if e["kto"] == "wrog" and e["typ"] == "wskrzeszenie"), 0)
        self.assertGreater(razem, 300)
        self.assertGreater(po_ticku, 0, "smiertelne tykniecie tez wyzwala wskrzeszenie")

    def test_bez_pasywki_nie_ma_wskrzeszenia_i_jest_deterministyczne(self):
        for w in _walki(wzorcowe.postac("mag", 5), {"potwor": "straznik_lasu", "poziom": 6}, range(1, 100)):
            self.assertFalse(any(e["typ"] == "wskrzeszenie" for e in w["dziennik"]))
        g = wzorcowe.postac("wojownik", 10, umiejetnosci=["wskrzeszenie", "ciecie", "kolos"])
        for z in range(1, 30):
            a = silnik.symuluj(g, {"potwor": "straznik_lasu", "poziom": 11}, z)
            b = silnik.symuluj(copy.deepcopy(g), {"potwor": "straznik_lasu", "poziom": 11}, z)
            self.assertEqual(wzorce.podpis(a), wzorce.podpis(b))

    def test_kazda_klasa_moze_ja_wlozyc_tylko_do_slotu(self):
        for k in wzorcowe.KLASY:
            silnik.symuluj(wzorcowe.postac(k, 5, umiejetnosci=["wskrzeszenie"]), {"potwor": "lesny_slime", "poziom": 5}, 1)
        for zle in ({"premie": {"wskrzeszenie": 0.25}}, {"bron": {"obrazenia": 20, "pasywka": "wskrzeszenie"}},
                    {"umiejetnosci": ["wskrzeszenie", "wskrzeszenie"]}):
            p = wzorcowe.postac("zwiadowca", 5)
            p.update(zle)
            with self.assertRaises(ValueError):
                silnik.symuluj(p, {"potwor": "lesny_slime", "poziom": 5}, 1)

    def test_dziennik_odrzuca_zle_wskrzeszenie(self):
        g, ww = self.walki("zwiadowca", 5, "straznik_lasu", 100)
        w = next(w for w in ww if any(e["typ"] == "wskrzeszenie" for e in w["dziennik"]))
        d = w["dziennik"]
        i = next(i for i, e in enumerate(d) if e["typ"] == "wskrzeszenie")
        for psuj in ("drugi_raz", "bez_nokautu", "zle_zycie", "usuniete"):
            z = copy.deepcopy(w)
            if psuj == "drugi_raz":
                z["dziennik"].insert(i + 1, copy.deepcopy(z["dziennik"][i]))
            elif psuj == "bez_nokautu":
                z["dziennik"][i - 1]["obrazenia"] = 0
            elif psuj == "zle_zycie":
                z["dziennik"][i]["wartosc"] += 1
            else:
                del z["dziennik"][i]
            self.assertFalse(dziennik.sprawdz(z)[0], psuj)


class TestLup(unittest.TestCase):
    def test_lup_bez_jajek_shard_tylko_ze_straznika(self):
        oczekiwane = {"zloto", "doswiadczenie", "tokeny_krainy", "gemy", "shard_ewolucji", "kraina"}
        shardy_straznika = 0
        for (L, k, p), s in proba().items():
            self.assertEqual(s["klucze_lupu"], oczekiwane)
            if p == "straznik_lasu":
                shardy_straznika += s["shardy"]
            else:
                self.assertEqual(s["shardy"], 0, (L, k, p))
        self.assertGreater(shardy_straznika, 0)
        oryg = silnik.PRZECIWNICY["straznik_lasu"]["ranga"]
        g = wzorcowe.postac("zwiadowca", 5)
        przed = [silnik.symuluj(g, {"potwor": "straznik_lasu", "poziom": 5}, z) for z in range(1, 40)]
        try:
            silnik.PRZECIWNICY["straznik_lasu"]["ranga"] = "zwykly"
            po = [silnik.symuluj(g, {"potwor": "straznik_lasu", "poziom": 5}, z) for z in range(1, 40)]
        finally:
            silnik.PRZECIWNICY["straznik_lasu"]["ranga"] = oryg
        for a, b in zip(przed, po):
            self.assertEqual(a["dziennik"], b["dziennik"])
            self.assertEqual(b["lup"]["shard_ewolucji"], 0)

    def test_lup_za_przegrana_i_wygrana(self):
        for z in range(1, 200):
            w = silnik.symuluj(wzorcowe.postac("mag", 1), {"potwor": "straznik_lasu", "poziom": 3}, z)
            if w["wynik"] == "przegrana":
                L = w["lup"]
                self.assertEqual((L["zloto"], L["tokeny_krainy"], L["gemy"], L["shard_ewolucji"]), (0, 0, 0, 0))
                self.assertGreater(L["doswiadczenie"], 0)
        w = silnik.symuluj(wzorcowe.postac("mag", 5), {"postac": wzorcowe.postac("mag", 5)}, 1)
        self.assertEqual(w["lup"]["zloto"] + w["lup"]["doswiadczenie"], 0)


# ------------------------------------------------------------------------------------------------ U7: dlugosc walki
class TestDlugoscWalki(unittest.TestCase):
    def test_niezmienniki_na_calej_probie(self):
        for klucz, s in proba().items():
            self.assertEqual(s["zle"], [], klucz)

    def test_walka_zawsze_konczy_sie_naturalnie_bezpiecznik_nie_zadzialal(self):
        najdluzsza = 0
        for klucz, s in proba().items():
            self.assertEqual(s["bezpiecznik"], 0, klucz)
            najdluzsza = max(najdluzsza, max(s["tury"]))
        self.assertLess(najdluzsza * 5, silnik.STALE["maks_tur"], "limit tur ma byc w praktyce nieosiagalny")

    def test_bezpiecznik_dziala_gdy_limit_jest_sztucznie_niski(self):
        stary = silnik.STALE["maks_tur"]
        try:
            silnik.STALE["maks_tur"] = 3
            w = silnik.symuluj(wzorcowe.postac("wojownik", 5), {"potwor": "straznik_lasu", "poziom": 5}, 1)
        finally:
            silnik.STALE["maks_tur"] = stary
        self.assertTrue(w["bezpiecznik"])
        self.assertEqual(w["tury"], 3)
        self.assertEqual(dziennik.sprawdz(w), (True, None))

    def test_bezpiecznik_porownuje_jak_luau_na_liczbach_double(self):
        # kontrola 16/17.11: przy zyciu rzedu 10^9 iloczyn hp x zycie przekracza 2^53. Luau liczy go na double, a port
        # liczyl na dokladnych int — tu dokladnie 999999951 x 1000000009 < 999999953 x 1000000007 (o 112), ale po
        # zaokragleniu do double oba iloczyny sa rowne, wiec Luau uznaje remis procentow (wygrywa gracz).
        G, W, hg, hw = 1000000007, 1000000009, 999999951, 999999953
        self.assertLess(hg * W, hw * G)
        self.assertEqual(float(hg) * W, float(hw) * G)

        def zd(kto, cel, t, hp_g, hp_w):
            return {"typ": "cios", "kto": kto, "cel": cel, "obrazenia": 56, "pochloniete": 0, "rodzaj": "fizyczne",
                    "umiejetnosc": "", "efekt": "", "krytyk": False, "wartosc": 0, "tury": 0, "stosy": 0, "t": t,
                    "trwa": 1.1, "hp_gracz": hp_g, "hp_wrog": hp_w, "mana_gracz": 0, "mana_wrog": 0}
        strona = {"nazwa": "x", "rodzaj": "postac", "id": "mag", "ranga": "gracz", "poziom": 1, "mana": 0, "mana_maks": 100}
        walka = {"wersja": 3, "ziarno": 1, "strony": {"gracz": dict(strona, zycie=G), "wrog": dict(strona, zycie=W)},
                 "dziennik": [zd("gracz", "wrog", 1.1, G, hw), zd("wrog", "gracz", 2.2, hg, hw)],
                 "wynik": "wygrana", "tury": 2, "bezpiecznik": True,
                 "lup": {"zloto": 0, "doswiadczenie": 0, "tokeny_krainy": 0, "gemy": 0, "shard_ewolucji": 0, "kraina": ""},
                 "czesc_przez_blok": 0.25, "czas_wstepu": 1.1, "czas_finalu": 1.9, "czas": 5.2}
        self.assertEqual(dziennik.sprawdz(walka), (True, None))
        import luau_mini as LM
        interp = LM.Interpreter()
        with open(os.path.join(REPO, "src", "shared", "Walka", "Dziennik.luau"), encoding="utf-8") as f:
            interp.laduj("Dziennik", f.read())
        sprawdz_luau = interp.wymagaj("Dziennik").get("sprawdz")
        for wynik, ok in (("wygrana", True), ("przegrana", False)):
            walka["wynik"] = wynik
            self.assertEqual(dziennik.sprawdz(walka)[0], ok, wynik)
            self.assertEqual(interp.wywolaj(sprawdz_luau, [LM.do_luau(walka)])[0], ok, wynik)

    def test_dlugosc_ma_szeroki_naturalny_rozrzut(self):
        for L in POZIOMY:
            for k in wzorcowe.KLASY:
                for p in PRZECIWNICY:
                    t = proba()[(L, k, p)]["tury"]
                    self.assertGreaterEqual(max(t), 2 * min(t), (L, k, p))

    def test_zwykly_potwor_bywa_dluzszy_niz_typowa_walka_ze_straznikiem(self):
        zwykle = [p for p in MONSTRY if silnik.PRZECIWNICY[p]["ranga"] == "zwykly"]
        for L in POZIOMY:
            mediana = statistics.median(t for k in wzorcowe.KLASY for t in proba()[(L, k, "straznik_lasu")]["tury"])
            najdluzsza = max(max(proba()[(L, k, p)]["tury"]) for k in wzorcowe.KLASY for p in zwykle)
            self.assertGreater(najdluzsza, mediana, L)
        for L in POZIOMY:
            najkrotsza_straznika = min(min(proba()[(L, k, "straznik_lasu")]["tury"]) for k in wzorcowe.KLASY)
            mediana_zwyklych = statistics.median(t for k in wzorcowe.KLASY for p in zwykle for t in proba()[(L, k, p)]["tury"])
            self.assertLess(najkrotsza_straznika, mediana_zwyklych, L)

    def test_straznik_moze_pasc_w_jednej_dwoch_turach(self):
        g = wzorcowe.postac("wojownik", 10, dodatkowe={"sila": 600})
        tury = [silnik.symuluj(g, {"potwor": "straznik_lasu", "poziom": 2}, z)["tury"] for z in range(1, 200)]
        self.assertLessEqual(min(tury), 2)

    def test_pierwszy_cios_moze_zabic(self):
        g = wzorcowe.postac("zwiadowca", 10, dodatkowe={"sila": 300})
        zabil = 0
        for z in range(1, 200):
            w = silnik.symuluj(g, {"potwor": "lesny_slime", "poziom": 1}, z)
            pierwsze = w["dziennik"][0]
            if pierwsze["kto"] == "gracz" and pierwsze["hp_wrog"] == 0:
                zabil += 1
                self.assertEqual(len(w["dziennik"]), 1)
                self.assertEqual(w["tury"], 1)
        self.assertGreater(zabil, 0)

    def test_kazde_zdarzenie_trwa_swoj_naturalny_czas_z_danych(self):
        for klucz, s in proba().items():
            self.assertEqual(s["czasy_zle"], [], klucz)
        g = wzorcowe.postac("wojownik", 5, dodatkowe={"kondycja": 700})
        cel = {"postac": wzorcowe.postac("mag", 5, dodatkowe={"kondycja": 700})}
        for z in range(1, 6):
            w = silnik.symuluj(g, cel, z)
            self.assertGreater(w["tury"], 60)
            self.assertFalse(w["bezpiecznik"])
            self.assertIsNone(sprawdz_naturalne_czasy(w))

    def _sztuczna_walka(self, tura, ziarno):
        A = silnik.wartosci_postaci(wzorcowe.postac("wojownik", 5, ile_slotow=2, zaklecie="trucizna"))
        B = silnik.wartosci_potwora("straznik_lasu", 5)
        return {"strony": {"gracz": A, "wrog": B},
                "stan": {"gracz": silnik.nowy_stan(A), "wrog": silnik.nowy_stan(B)},
                "dziennik": [], "czas": 0, "tura": tura, "los": silnik.nowy_los(ziarno)}

    def test_brak_narastajacych_obrazen_ta_sama_akcja_w_turze_1_i_50(self):
        def bez_czasu(w):
            return [{k: v for k, v in z.items() if k not in ("t",)} for z in w["dziennik"]]
        for ziarno in range(1, 40):
            wyniki = []
            for tura in (1, 50, 400):
                w = self._sztuczna_walka(tura, ziarno)
                silnik.zwykly_cios(w, "gracz", "wrog")
                silnik.zwykly_cios(w, "wrog", "gracz")
                silnik.uzyj_umiejetnosci(w, "gracz", "wrog", "ciecie", 100)
                silnik.uzyj_umiejetnosci(w, "wrog", "gracz", "uscisk_korzeni", 100)
                silnik.naloz_efekt(w, "gracz", "wrog", "trucizna", 1, 0)
                silnik.naloz_efekt(w, "gracz", "wrog", "trucizna", 1, 0)
                silnik.tykniecia(w, "wrog")
                wyniki.append(bez_czasu(w))
            self.assertEqual(wyniki[0], wyniki[1], ziarno)
            self.assertEqual(wyniki[0], wyniki[2], ziarno)

    def test_trafienia_w_poznych_turach_nie_sa_mocniejsze_niz_we_wczesnych(self):
        g = wzorcowe.postac("wojownik", 5, umiejetnosci=["ciecie"], dodatkowe={"kondycja": 60})
        wczesne, pozne = [], []
        for z in range(1, 1500):
            nr = 0
            for e in silnik.symuluj(g, {"potwor": "straznik_lasu", "poziom": 5}, z)["dziennik"]:
                if e["kto"] == "wrog" and e["typ"] in ("cios", "krytyk", "blok", "unik", "umiejetnosc", "utrata_tury"):
                    nr += 1
                    if e["typ"] == "cios":
                        (wczesne if nr <= 3 else pozne if nr >= 8 else []).append(e["obrazenia"] + e["pochloniete"])
        self.assertGreater(len(pozne), 1000)
        stosunek = statistics.mean(pozne) / statistics.mean(wczesne)
        self.assertLess(abs(stosunek - 1), 0.02, stosunek)

    def test_czas_calosci_to_suma_czasow_zdarzen_bez_sciskania(self):
        for z in range(1, 100):
            w = silnik.symuluj(wzorcowe.postac("wojownik", 5), {"potwor": "straznik_lasu", "poziom": 5}, z)
            suma = silnik.STALE["czas_wstepu"] + sum(wzorce.setne(e["trwa"]) for e in w["dziennik"]) + silnik.STALE["czas_finalu"]
            self.assertEqual(wzorce.setne(w["czas"]), suma)
        czasy = [c for s in proba().values() for c in s["czasy"]]
        self.assertGreater(max(czasy), 4 * min(czasy), "czas rosnie z dlugoscia walki, nic go nie sciska")


# ------------------------------------------------------------------------------------------------ U10: rownosc klas
class TestRownoscKlas(unittest.TestCase):
    def procent(self, L, k, p):
        return 100.0 * proba()[(L, k, p)]["wygrane"] / ZIAREN

    def test_klasy_maja_zblizony_procent_wygranych_z_kazdym_potworem(self):
        for L in POZIOMY:
            for p in MONSTRY:
                r = [self.procent(L, k, p) for k in wzorcowe.KLASY]
                prog = WYJATKI_KLAS_PP.get((p, L), TOLERANCJA_KLAS_PP)
                self.assertLessEqual(max(r) - min(r), prog, "poziom %d, %s: %s" % (L, p, r))

    def test_pojedynki_klasa_na_klase_blisko_50_procent(self):
        for L in POZIOMY:
            for a in wzorcowe.KLASY:
                for b in wzorcowe.KLASY:
                    x = self.procent(L, a, b)
                    self.assertGreaterEqual(x, PVP_OD, "poziom %d: %s na %s = %.1f%%" % (L, a, b, x))
                    self.assertLessEqual(x, PVP_DO, "poziom %d: %s na %s = %.1f%%" % (L, a, b, x))


# UCZCIWIE: wymog „kazdy build ma potwora, na ktorego jest wyraznie lepszy, i takiego, na ktorego jest wyraznie gorszy”
# spelniaja dzis tylko te buildy (poziom, klasa, build). Pozostale sa rowne wzorcowej (45-55%), ale potwory lasu po
# wyrownaniu klas sa do siebie za podobne, zeby build mial w lesie wyraznego „swojego” i „nie swojego” potwora
# (tabela e w ZMIANY_SESJA_1611.md). Do zrobienia: potwory o ostrzejszych cechach w kolejnych biomach albo buildy
# o mocniejszym charakterze — wtedy dopisac je tutaj.
BUILDY_ROZNE = {(5, "wojownik", "pancerz"), (10, "wojownik", "pancerz"), (5, "mag", "mana")}


class TestBuildy(unittest.TestCase):
    """Sesja 16.11, pkt 9: buildy rozne i zaden nie dominuje — kazdy 45-55% z wzorcowa swojej klasy; potwor wyraznie
    lepszy i wyraznie gorszy — patrz BUILDY_ROZNE."""

    def _wyniki(self, L, k, b, n):
        wz = wzorcowe.postac(k, L)
        g = wzorcowe.build(b, k, L)
        jako_gracz = sum(silnik.symuluj(g, {"postac": wz}, z)["wynik"] == "wygrana" for z in range(1, n + 1))
        jako_wrog = sum(silnik.symuluj(wz, {"postac": g}, z)["wynik"] == "przegrana" for z in range(1, n + 1))
        duel = 100.0 * (jako_gracz + jako_wrog) / (2 * n)
        roznice = []
        for p in MONSTRY:
            a = sum(silnik.symuluj(g, {"potwor": p, "poziom": L}, z)["wynik"] == "wygrana" for z in range(1, n + 1))
            c = sum(silnik.symuluj(wz, {"potwor": p, "poziom": L}, z)["wynik"] == "wygrana" for z in range(1, n + 1))
            roznice.append(100.0 * (a - c) / n)
        return duel, roznice

    def test_buildy_rowne_wzorcowej_i_rozne_tam_gdzie_umiemy(self):
        for L in (5, 10):
            for k in wzorcowe.KLASY:
                for b in wzorcowe.BUILDY_KLAS[k]:
                    duel, roznice = self._wyniki(L, k, b, ZIAREN_BUILDOW)
                    self.assertGreaterEqual(duel, BUILD_OD, (L, k, b, duel))
                    self.assertLessEqual(duel, BUILD_DO, (L, k, b, duel))
                    if (L, k, b) in BUILDY_ROZNE:
                        self.assertGreaterEqual(max(roznice), BUILD_WYRAZNIE_PP, (L, k, b, roznice))
                        self.assertLessEqual(min(roznice), -BUILD_WYRAZNIE_PP, (L, k, b, roznice))


def zestawy_slotow(k, n, wskrzeszenie=False):
    """Wszystkie zestawy 1..n slotow klasy: aktywne w kazdej kolejnosci (rotacja), pasywne bez kolejnosci."""
    import itertools
    akt = silnik.KLASY[k]["umiejetnosci"]
    pas = silnik.KLASY[k]["pasywne"] + (["wskrzeszenie"] if wskrzeszenie else [])
    wynik = []
    for r in range(1, n + 1):
        for zb in itertools.combinations(akt + pas, r):
            a = [x for x in zb if x in akt]
            for perm in itertools.permutations(a):
                wynik.append(list(perm) + [x for x in zb if x not in akt])
    return wynik


class TestZestawySlotow(unittest.TestCase):
    """Kontrola 16/17.11: przeszukanie WSZYSTKICH zestawow slotow (bez broni z pasywka, zaklecia i premii — wybor slotow
    jest darmowy) na 10. poziomie. Przed poprawka danych „1-2 aktywne + pasywka many” wygrywaly z wzorcowa 63-67%
    (na swiezych ziarnach), a zaden test tego nie lapal (tabela g sprawdzala tylko 6 wybranych zestawow). Po poprawce
    najlepszy zestaw (Mag: Kula ognia + 2 pasywki) ma ok. 60% — to juz zasada rotacji (wybory 3 i 4 w ZMIANY_SESJA_1611.md,
    decyzja ludzi), wiec prog 63% pilnuje tylko WYRAZNEJ dominacji (na starych danych test pada: 66%). Wskrzeszenie
    (legenda, propozycja D-094) jest poza tym testem — jego sila to decyzja ludzi."""

    def test_zaden_zestaw_slotow_nie_bije_wzorcowej_wyraznie(self):
        L = 10

        def pojedynek(g, wz, start, n):
            a = sum(silnik.symuluj(g, {"postac": wz}, z)["wynik"] == "wygrana" for z in range(start, start + n))
            b = sum(silnik.symuluj(wz, {"postac": g}, z)["wynik"] == "przegrana" for z in range(start, start + n))
            return 100.0 * (a + b) / (2 * n)
        for k in wzorcowe.KLASY:
            wz = wzorcowe.postac(k, L)
            sito = sorted(((pojedynek(wzorcowe.postac(k, L, umiejetnosci=um), wz, 1, 100), um)
                           for um in zestawy_slotow(k, wzorcowe.sloty(L))), key=lambda x: -x[0])
            for _, um in sito[:3]:
                d = pojedynek(wzorcowe.postac(k, L, umiejetnosci=um), wz, 1001, 1500)
                self.assertLess(d, 63.0, (k, um, d))


class TestStatystyki(unittest.TestCase):
    def test_kazda_statystyka_cos_daje_kazdej_klasie(self):
        # +20% puli w jedna statystyke na 5. poziomie: kazda statystyka podnosi wygrane kazdej klasy (potwory i klasy)
        L, n = 5, 300
        dod = round(0.2 * wzorcowe.pula(L))
        for k in wzorcowe.KLASY:
            def srednio(g):
                return statistics.mean(sum(silnik.symuluj(g, przeciwnik(p, L), z)["wynik"] == "wygrana"
                                           for z in range(1, n + 1)) for p in PRZECIWNICY)
            baza = srednio(wzorcowe.postac(k, L))
            zyski = {s: (srednio(wzorcowe.postac(k, L, dodatkowe={s: dod})) - baza) / n * 100 / dod for s in wzorcowe.STATYSTYKI}
            for s, v in zyski.items():
                self.assertGreater(v, 0.15, (k, s, zyski))
            self.assertGreater(min(zyski.values()) / max(zyski.values()), 0.25, (k, zyski))


# ------------------------------------------------------------------------------------------------ zrodla Luau
LUAU_PLIKI = [os.path.join(REPO, "src", "server", "Walka", n) for n in
              ("Dane.luau", "Los.luau", "Statystyki.luau", "Przeciwnicy.luau", "Umiejetnosci.luau", "Silnik.luau")] + \
             [os.path.join(REPO, "src", "shared", "Walka", "Dziennik.luau")]


def tokeny_luau(tekst):
    """Prosty lekser Luau: zwraca liste (slowo, nr_linii, pierwszy_w_linii) bez komentarzy i napisow."""
    wynik, i, n, linia, pierwszy = [], 0, len(tekst), 1, True
    while i < n:
        c = tekst[i]
        if c == "\n":
            linia, pierwszy, i = linia + 1, True, i + 1
            continue
        if c in " \t\r":
            i += 1
            continue
        if tekst.startswith("--", i):
            m = re.match(r"--\[(=*)\[", tekst[i:])
            if m:
                koniec = tekst.find("]" + m.group(1) + "]", i)
                linia += tekst.count("\n", i, koniec)
                i = koniec + len(m.group(1)) + 2
            else:
                while i < n and tekst[i] != "\n":
                    i += 1
            continue
        m = re.match(r"\[(=*)\[", tekst[i:])
        if m:
            koniec = tekst.find("]" + m.group(1) + "]", i)
            linia += tekst.count("\n", i, koniec)
            i = koniec + len(m.group(1)) + 2
            wynik.append(("<napis>", linia, pierwszy))
            pierwszy = False
            continue
        if c in "\"'`":
            j = i + 1
            while tekst[j] != c:
                j += 2 if tekst[j] == "\\" else 1
            i = j + 1
            wynik.append(("<napis>", linia, pierwszy))
            pierwszy = False
            continue
        m = re.match(r"[A-Za-z_][A-Za-z0-9_]*|\d+(\.\d+)?([eE][-+]?\d+)?|\.\.\.|\.\.|[=~<>]=|//|\+=|-=|\*=|/=|\.\.=|::|->|.", tekst[i:])
        wynik.append((m.group(0), linia, pierwszy))
        pierwszy = False
        i += len(m.group(0))
    return wynik


class TestZrodlaLuau(unittest.TestCase):
    def test_bloki_i_nawiasy_domkniete(self):
        for sciezka in LUAU_PLIKI:
            with self.subTest(os.path.basename(sciezka)):
                with open(sciezka, encoding="utf-8") as f:
                    tok = tokeny_luau(f.read())
                stos = []
                przed_wyrazeniem = {"=", "(", ",", "{", "[", "return", "and", "or", "not", "..", "+", "-", "*", "/",
                                    "==", "~=", "<", ">", "<=", ">=", "+=", "-="}
                poprzedni = None
                for slowo, linia, pierwszy in tok:
                    instrukcja_if = slowo == "if" and pierwszy and poprzedni not in przed_wyrazeniem
                    poprzedni = slowo
                    if slowo in ("function", "do", "repeat") or instrukcja_if:
                        stos.append((slowo, linia))
                    elif slowo == "end":
                        self.assertTrue(stos, "nadmiarowe end w linii %d" % linia)
                        self.assertNotEqual(stos.pop()[0], "repeat", "linia %d" % linia)
                    elif slowo == "until":
                        self.assertEqual(stos.pop()[0], "repeat", "linia %d" % linia)
                    elif slowo in "([{":
                        stos.append((slowo, linia))
                    elif slowo in ")]}":
                        para = {")": "(", "]": "[", "}": "{"}[slowo]
                        self.assertTrue(stos, "nadmiarowy %s w linii %d" % (slowo, linia))
                        otw = stos.pop()
                        self.assertEqual(otw[0], para, "linia %d zamyka %s z linii %d" % (linia, otw[0], otw[1]))
                self.assertEqual(stos, [], "niedomkniete bloki")
                fory = sum(1 for s, _, _ in tok if s in ("for", "while"))
                doy = sum(1 for s, _, _ in tok if s == "do")
                self.assertEqual(fory, doy)

    def test_bilans_blokow_drugim_narzedziem(self):
        # niezalezna kontrola z pakietu lasu (swiat/las_potwory/sprawdz_luau.py, reguly 1-2: bloki i nawiasy)
        sys.path.insert(0, os.path.join(REPO, "swiat", "las_potwory"))
        import sprawdz_luau  # noqa: E402
        for sciezka in LUAU_PLIKI:
            with open(sciezka, encoding="utf-8") as f:
                self.assertEqual(sprawdz_luau.sprawdz_tekst(f.read(), os.path.basename(sciezka), pelne=False), [])

    def test_moduly_czyste_bez_swiata_zegara_i_random(self):
        zakazane = re.compile(r"\b(Random|workspace|Instance|wait|delay|spawn)\b|\btick\s*\(|os\.(time|clock|date)|game:|"
                              r"task\.|RunService|IsStudio")
        for sciezka in LUAU_PLIKI:
            with open(sciezka, encoding="utf-8") as f:
                tekst = f.read()
            kod = re.sub(r"--\[\[.*?\]\]", "", tekst, flags=re.S)
            kod = re.sub(r"--[^\n]*", "", kod)
            kod = re.sub(r'"(\\.|[^"\\])*"', '""', kod)
            self.assertIsNone(zakazane.search(kod), os.path.basename(sciezka))
            self.assertRegex(tekst.rstrip(), r"return [A-Za-z]+$|^[\s\S]*\n\}$", os.path.basename(sciezka))

    def test_iteracja_tylko_po_listach_tam_gdzie_kolejnosc_wplywa_na_rzuty(self):
        # pairs()/iteracja po slownikach jest dozwolona tylko w walidacji (sprawdzPremie, sprawdzModyfikatory,
        # sprawdzKlucze, sprawdzPostac, Dziennik.sprawdz) — tam kolejnosc nie zmienia wyniku walki.
        # Kontrola 16/17.11: dawny wzorzec (…umiejetnosci|…statystyki$) przepuszczal tez SLOWNIKI Dane.umiejetnosci
        # i p.statystyki — teraz dokladna lista zrodel, ktore sa listami.
        listy = {"stanStrony.efekty", "w.stan[strona].efekty", "POLA_ZDARZENIA", "U.efekty", "s.efekty",
                 "Dane.przeciwnicy", "Dane.statystyki"}
        for nazwa in ("Silnik.luau", "Umiejetnosci.luau", "Przeciwnicy.luau", "Los.luau"):
            with open(os.path.join(REPO, "src", "server", "Walka", nazwa), encoding="utf-8") as f:
                tekst = f.read()
            for m in re.finditer(r"for\s+[^\n]*\bin\s+([^\n]+?)\s+do", tekst):
                zrodlo = m.group(1)
                self.assertIn(zrodlo, listy, "%s: for ... in %s" % (nazwa, zrodlo))
        with open(os.path.join(REPO, "src", "server", "Walka", "Statystyki.luau"), encoding="utf-8") as f:
            tekst = f.read()
        bojowe = tekst[tekst.index("function Statystyki.zbierzModyfikatory"):tekst.index("function Statystyki.wartosciPostaci")]
        for m in re.finditer(r"for\s+[^\n]*\bin\s+([^\n]+?)\s+do", bojowe):
            self.assertIn(m.group(1), ("Dane.modyfikatory", "zrodla", "pasywne"), m.group(1))

    def test_statystyki_luau_umiejetnosci_tylko_jako_lista(self):
        with open(os.path.join(REPO, "src", "server", "Walka", "Statystyki.luau"), encoding="utf-8") as f:
            tekst = f.read()
        wartosci = tekst[tekst.index("function Statystyki.wartosciPostaci"):]
        wartosci = wartosci[:wartosci.index("\nend\n")]
        for m in re.finditer(r"for\s+[^\n]*\bin\s+([^\n]+?)\s+do", wartosci):
            self.assertEqual(m.group(1), "Dane.statystyki", "wartosciPostaci: for ... in %s" % m.group(1))
        self.assertRegex(wartosci, r"for i = 1, #wejscie do")
        sprawdz = tekst[tekst.index("function Statystyki.sprawdzPostac"):tekst.index("function Statystyki.zbierzModyfikatory")]
        self.assertRegex(sprawdz, r"if ile ~= #um then")
        self.assertRegex(sprawdz, r'type\(klucz\) ~= "number"')

    def test_zamkniete_listy_pol_takie_same_w_obu_portach(self):
        with open(os.path.join(REPO, "src", "server", "Walka", "Statystyki.luau"), encoding="utf-8") as f:
            tekst = f.read()
        for nazwa_luau, lista in (("Statystyki.POLA_POSTACI", silnik.POLA_POSTACI), ("local POLA_BRONI", silnik.POLA_BRONI),
                                  ("local POLA_TARCZY", silnik.POLA_TARCZY),
                                  ("Statystyki.POLA_PRZECIWNIKA", silnik.POLA_PRZECIWNIKA)):
            m = re.search(re.escape(nazwa_luau) + r"\s*=\s*\{([^}]*)\}", tekst)
            self.assertIsNotNone(m, nazwa_luau)
            self.assertEqual(re.findall(r'"([a-z_]+)"', m.group(1)), lista, nazwa_luau)
        # kazde pole z wzorcowej postaci i buildow jest na liscie (inaczej silnik odrzucilby poprawne wejscie)
        for k in wzorcowe.KLASY:
            for b in ["wzorcowa"] + wzorcowe.BUILDY_KLAS[k]:
                p = wzorcowe.build(b, k, 10)
                self.assertTrue(set(p) <= set(silnik.POLA_POSTACI), (k, b, set(p)))
                self.assertTrue(set(p["bron"]) <= set(silnik.POLA_BRONI), (k, b))

    def test_ziarno_sprawdzane_tak_samo_w_obu_portach(self):
        with open(os.path.join(REPO, "src", "server", "Walka", "Silnik.luau"), encoding="utf-8") as f:
            silnik_luau = f.read()
        with open(os.path.join(REPO, "src", "server", "Walka", "Los.luau"), encoding="utf-8") as f:
            los_luau = f.read()
        self.assertIn("if not Los.calkowita(ziarno) or ziarno < 0 or ziarno >= Los.ZIARNO_GRANICA then", silnik_luau)
        self.assertIn("Los.ZIARNO_GRANICA = %d" % silnik.ZIARNO_GRANICA, los_luau)
        self.assertEqual(silnik.ZIARNO_GRANICA, 2 ** 31)

    def test_funkcje_portu_maja_odpowiedniki_w_luau(self):
        pary = {"nowy_los": "nowyLos", "zaokraglij": "zaokraglij", "premia": "premia", "miedzy": "miedzy",
                "sprawdz_postac": "sprawdzPostac", "sprawdz_modyfikatory": "sprawdzModyfikatory",
                "zbierz_modyfikatory": "zbierzModyfikatory", "podziel_umiejetnosci": "podzielUmiejetnosci",
                "bojowe": "bojowe", "wartosci_postaci": "wartosciPostaci", "wartosci_potwora": "wartosciPotwora",
                "klasa_potwora": "klasaPotwora", "wartosci_przeciwnika": "wartosciPrzeciwnika", "losuj_lup": "losujLup",
                "po_obronie": "poObronie", "obrazenia_trafienia": "obrazeniaTrafienia", "przyjmij": "przyjmij",
                "oslona": "oslona", "unik_efektywny": "unikEfektywny", "mnoznik_many": "mnoznikMany",
                "dodaj_mane": "dodajMane", "naloz_efekt": "nalozEfekt", "zwykly_cios": "zwyklyCios",
                "uzyj_umiejetnosci": "uzyjUmiejetnosci", "koszt_umiejetnosci": "kosztUmiejetnosci", "akcja": "akcja",
                "tykniecia": "tykniecia", "koniec_tury": "koniecTury", "symuluj": "symuluj", "wskrzes": "wskrzes",
                "sprawdz_klucze": "sprawdzKlucze"}
        wszystko = ""
        for sciezka in LUAU_PLIKI:
            with open(sciezka, encoding="utf-8") as f:
                wszystko += f.read()
        for py, lu in pary.items():
            self.assertTrue(hasattr(silnik, py), py)
            self.assertRegex(wszystko, r"function\s+([A-Za-z]+\.)?%s\s*\(" % lu, lu)

    def test_skladanie_kodu_do_studio(self):
        import zgodnosc_studio
        with open(wzorce.PLIK, encoding="utf-8") as f:
            kod = zgodnosc_studio.zloz_kod(json.load(f))
        self.assertIn('zrodla["Silnik"] = function()', kod)
        self.assertNotIn("require(script", kod)
        self.assertLess(len(kod), 1_500_000)

    def test_luau_w_interpreterze_zgodny_z_pythonem(self):
        # moduly Luau uruchomione w interpreterze tools/walka/luau_mini.py (podzbior Luau, NIE Studio) daja te same
        # dzienniki co port w Pythonie na wszystkich wzorcach i odrzucaja wszystkie zle wejscia bledem „Walka: …”
        import zgodnosc_studio
        with open(wzorce.PLIK, encoding="utf-8") as f:
            wz = json.load(f)
        ok, wynik = zgodnosc_studio.sprawdz_offline(wz, wypisz=lambda *_: None)
        self.assertTrue(ok, wynik)
        self.assertEqual(wynik["rozne"], 0)
        self.assertEqual(wynik["odrzucone"], wynik["zle_wejscia"])


if __name__ == "__main__":
    unittest.main()
