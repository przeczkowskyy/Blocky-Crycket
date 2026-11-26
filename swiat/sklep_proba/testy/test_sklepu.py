#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy sklepu zbrojmistrza na próbę bez Studio (swiat/sklep_proba). Uruchom:
    python -B swiat/sklep_proba/testy/test_sklepu.py

1. Dane: plik aktualny; spójność z katalogiem sklepu (72 sprzedawane przedmioty: ceny, poziomy, stopnie, sloty i klasy
   u kowala = katalog; 8 części zbroi bez własnej pozycji); teksty dla gracza bez języka twórców.
2. Logika sklepu: LogikaSklepu.luau w luau_mini = logika_sklepu.py (przypadki wzorcowe, zepsuta wersja wykryta);
   układ okna na telefonie 667 × 375 i na dużym ekranie.
3. Kupno na atrapie stanu gracza (sama logika kowala + portfel w Pythonie): wszystkie 54 nowe przedmioty, odmowy,
   reguła zakładania, łup tylko ze stopnia startowego.
4. PRAWDZIWE SerwerSklepu + SerwerKowala + SerwerStanu + SerwerStrojow w luau_mini (atrapa Roblox z testów kowala):
   udane kupno (Złoto w dół o cenę, przedmiot w posiadanych, część zbroi ze zbroją, założenie według reguły, wpis
   Modyfikatory rośnie o statystyki), wszystkie odmowy (zła klasa, za niski poziom, posiadany, brak Złota, nieznany,
   część zbroi, za daleko, za szybko), kupno dwa razy pod rząd nie zabiera Złota dwa razy, atrybut SklepStacNa,
   sklep bez kowala i bez stanu gracza („Sklep nieczynny (próba)”, bez ostrzeżeń).
5. Narzędzia: kontrola Luau, zbuduj.py --sucho, kod budowy parsuje się, brak ścieżek lokalnych, proba_play --sprawdz.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
TESTY = os.path.dirname(os.path.abspath(__file__))
PAKIET = os.path.dirname(TESTY)
REPO = os.path.dirname(os.path.dirname(PAKIET))
KOWAL = os.path.join(REPO, "swiat", "kowal_proba")
STROJE = os.path.join(REPO, "swiat", "stroje_proba")


def _modul(nazwa, sciezka):
    if nazwa in sys.modules:
        return sys.modules[nazwa]
    spec = importlib.util.spec_from_file_location(nazwa, sciezka)
    m = importlib.util.module_from_spec(spec)
    sys.modules[nazwa] = m
    spec.loader.exec_module(m)
    return m


if PAKIET not in sys.path:
    sys.path.insert(0, PAKIET)
import logika_sklepu as LS  # noqa: E402
DANE = _modul("dane_sklepu", os.path.join(PAKIET, "dane.py"))
SLS = _modul("sprawdz_luau_sklepu", os.path.join(PAKIET, "sprawdz_luau_sklepu.py"))
TK = _modul("test_kowala_baza", os.path.join(KOWAL, "testy", "test_kowala.py"))   # atrapa serwerów i dane kowala
LK = TK.LK
DK = TK.D
LM = TK.LM


def czytaj(*czesci):
    with open(os.path.join(*czesci), encoding="utf-8") as f:
        return f.read()


D = DANE.dane_z_przypadkami()
ZRODLA = os.path.join(PAKIET, "zrodla")
DANE_LUAU = czytaj(ZRODLA, "DaneSklepu.luau")
LOGIKA = czytaj(ZRODLA, "LogikaSklepu.luau")
SERWER = czytaj(ZRODLA, "SerwerSklepu.server.luau")
KATALOG = json.loads(czytaj(REPO, "swiat", "postacie", "sklep_przedmioty.json"))
_STOPIEN_LAS = os.path.join(STROJE, "zrodla", "DaneStrojowLas.luau")
NOWE_W_PRZYMIERZALNI = os.path.isfile(_STOPIEN_LAS) and '"rycerz_las_zbroja"' in czytaj(_STOPIEN_LAS)


def nowe(klasa, slot=None, nr=None):
    return [i for i in DK["klasy"][klasa]["wszystkie"] if DK["przedmioty"][i]["nrStopnia"] > 0
            and (slot is None or DK["przedmioty"][i]["slot"] == slot)
            and (nr is None or DK["przedmioty"][i]["nrStopnia"] == nr)]


# ------------------------------------------------------------------------------------------------ 1. dane
class TestDanych(unittest.TestCase):
    def test_1a_aktualne(self):
        zle, _D, _t = DANE.aktualny()
        self.assertEqual(zle, [], "uruchom python -B swiat/sklep_proba/dane.py")

    def test_1b_spojnosc_z_katalogiem(self):
        sprzedawane = [p for p in KATALOG["przedmioty"] if p["sprzedawany"]]
        czesci = [p for p in KATALOG["przedmioty"] if not p["sprzedawany"]]
        self.assertEqual((len(sprzedawane), len(czesci)), (72, 8))
        self.assertEqual(set(DK["przedmioty"]), {p["id"] for p in sprzedawane})
        for p in sprzedawane:
            P = DK["przedmioty"][p["id"]]
            for pole_k, pole_d in (("cena", "cena"), ("poziom", "poziom"), ("stopien", "stopien"),
                                   ("nr_stopnia", "nrStopnia"), ("slot", "slot"), ("klasa", "klasa"),
                                   ("nazwa", "nazwa"), ("baza", "baza"), ("krok", "krok"), ("waga", "waga"),
                                   ("podstawowy", "podstawowy")):
                self.assertEqual(P[pole_d], p[pole_k], "%s.%s" % (p["id"], pole_k))
        self.assertEqual(DK["czesci"], {p["id"]: p["czesc_od"] for p in czesci})
        self.assertEqual([(s["id"], s["nr"], s["nazwa"]) for s in D["stopnie"]],
                         [(s["id"], s["nr"], s["nazwa"]) for s in KATALOG["stopnie"]])
        self.assertEqual([s["id"] for s in DK["stopnie"]], [s["id"] for s in D["stopnie"]])
        for k, Kl in DK["klasy"].items():
            self.assertEqual(len(Kl["wszystkie"]), 4 * len(Kl["przedmioty"]), k)

    def test_1c_teksty_dla_gracza(self):
        zle = re.compile(r"(swiat/|D-\d|atrybut|Studio|pakiet|SklepProba|KowalProba|_|\bid\b)")
        for k, t in D["teksty"].items():
            for x in (t if isinstance(t, list) else [t]):
                self.assertFalse(zle.search(x), "tekst %s: %r" % (k, x))
        self.assertIn("PRÓBA", D["teksty"]["tytul"])
        self.assertEqual(LS.komunikat(D, "kup", {"ok": False, "powod": "za_malo_zlota", "brakuje": 150}),
                         "Brakuje ci 150 Rybek.")
        # waluta to Rybki (D-146, atrybut Gold): odmiana przy liczbie, dopełniacz po „Brakuje ci”, bez „Złota”
        self.assertEqual(LS.komunikat(D, "kup", {"ok": False, "powod": "za_malo_zlota", "brakuje": 1}),
                         "Brakuje ci 1 Rybki.")
        self.assertEqual(LS.komunikat(D, "kup", {"ok": False, "powod": "za_malo_zlota", "brakuje": 22}),
                         "Brakuje ci 22 Rybek.")
        oczek = {0: ("Rybek", "Rybek"), 1: ("Rybka", "Rybki"), 2: ("Rybki", "Rybek"), 4: ("Rybki", "Rybek"),
                 5: ("Rybek", "Rybek"), 11: ("Rybek", "Rybek"), 12: ("Rybek", "Rybek"), 14: ("Rybek", "Rybek"),
                 21: ("Rybek", "Rybek"), 22: ("Rybki", "Rybek"), 25: ("Rybek", "Rybek"), 100: ("Rybek", "Rybek"),
                 101: ("Rybek", "Rybek"), 102: ("Rybki", "Rybek"), 112: ("Rybek", "Rybek")}
        for n, (m, d) in oczek.items():
            self.assertEqual(LS.ile_rybek(D, n), "%d %s" % (n, m))
            self.assertEqual(LS.ile_rybek_dop(D, n), "%d %s" % (n, d))
        self.assertEqual(LS.naglowek(D, 1234, 17)["zloto"], "Rybki: 1234")
        teksty = [x for t in D["teksty"].values() for x in (t if isinstance(t, list) else [t])]
        self.assertFalse([t for t in teksty if re.search(r"złot|Złot|ZŁOT", t)], "waluta to Rybki, nie Złoto")
        self.assertFalse(any(re.search(r"%d Ryb", t) for t in teksty), "liczba przy Rybkach bez odmiany")
        self.assertEqual(LS.komunikat(D, "kup", {"ok": False, "powod": "za_niski_poziom", "brakuje": 3, "wymagany": 13}),
                         "Potrzebujesz poziomu 13.")
        self.assertEqual(LS.komunikat(D, "oferta", None), "Sklep nieczynny (próba).")
        for powod in ("masz", "inna_klasa", "czesc_zbroi", "nieznany_przedmiot", "daleko", "za_szybko", "cos_nowego"):
            t = LS.komunikat(D, "kup", {"ok": False, "powod": powod})
            self.assertTrue(len(t) > 8 and t[0].isupper() and t[-1] in ".…", (powod, t))

    def test_1d_miejsce(self):
        m = D["miejsce"]
        self.assertEqual(m["id"], "zbrojownia")
        self.assertEqual(len(m["punkt"]), 3)
        self.assertGreater(m["zasiegOkna"], m["zasieg"])


# ------------------------------------------------------------------------------------------------ 2. logika i układ
def luau_logika(logika=LOGIKA):
    import atrapa_roblox as AR
    sw = AR.Swiat()
    Dl = sw.it.wykonaj(DANE_LUAU, "DaneSklepu.luau")[0]
    Ll = sw.it.wykonaj(logika, "LogikaSklepu.luau")[0]
    return sw, Dl, Ll


@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestLogiki(unittest.TestCase):
    def test_2a_przypadki_wzorcowe(self):
        sw, Dl, Ll = luau_logika()
        w = [LM.z_luau(x) for x in sw.wolaj(Ll.get("sprawdzPrzypadki"), Dl)]
        self.assertTrue(w[0], w[2])
        self.assertGreater(w[1], 40)

    def test_2b_zepsute_wersje_wykryte(self):
        zepsute = [("przycisk = wiersz - 4", "przycisk = wiersz - 5"),
                   ('if o.stan == "kup" then\n\t\t\t\t\tdoKupienia += 1', 'if o.stan == "masz" then\n\t\t\t\t\tdoKupienia += 1'),
                   ("string.format(T.za_malo_zlota, L.ileRybekDop(D, ile))",
                    "string.format(T.za_malo_zlota, L.ileRybekDop(D, ile + 1))"),
                   ("if j >= 2 and j <= 4 and not (d >= 12 and d <= 14) then", "if j >= 2 and j <= 4 then")]
        for stare, nowe_ in zepsute:
            self.assertEqual(LOGIKA.count(stare), 1, stare)
            sw, Dl, Ll = luau_logika(LOGIKA.replace(stare, nowe_))
            try:
                ok = sw.wolaj(Ll.get("sprawdzPrzypadki"), Dl)[0]
            except Exception:  # noqa: BLE001 — błąd wykonania też jest wykryciem
                ok = False
            self.assertFalse(ok, "zepsuta logika przeszła: %s" % nowe_)


class TestUkladu(unittest.TestCase):
    def sprawdz(self, W, H):
        u = LS.uklad(D, W, H)
        self.assertGreaterEqual(u["tekst"], 12, "tekst co najmniej 12 pt")
        self.assertGreaterEqual(u["przycisk"], 44, "przycisk w wierszu co najmniej 44 px")
        self.assertGreaterEqual(u["zamknij"], 44, "przycisk zamknięcia co najmniej 44 px")
        self.assertGreaterEqual(u["zakladka"], 44)
        self.assertGreaterEqual(u["przyciskSzer"], 88)
        self.assertGreaterEqual(u["x"], 0)
        self.assertGreaterEqual(u["y"], 0)
        self.assertLessEqual(u["x"] + u["szer"], W)
        self.assertLessEqual(u["y"] + u["wys"], H)
        self.assertLess(u["szer"], W * 0.9, "okno nie zasłania całego ekranu")
        self.assertEqual(u["naglowek"] + u["zakladka"] + u["lista"] + u["komunikat"], u["wys"])
        self.assertGreaterEqual(u["widoczne"], 4, "co najmniej cztery wiersze bez przewijania")
        self.assertLessEqual(u["tekst"] * 2 + 4, u["wiersz"], "dwie linie tekstu mieszczą się w wierszu")
        # wiersz: pole stopnia + teksty + przycisk mieszczą się w szerokości listy
        szer_wiersza = u["szer"] - 24
        self.assertGreater(szer_wiersza - (u["wiersz"] - 10) - 10 - u["przyciskSzer"] - 8, 180, "miejsce na nazwę i opis")
        return u

    def test_2c_telefon_667x375(self):
        u = self.sprawdz(667, 375)
        self.assertEqual((u["wiersz"], u["tekst"]), (48, 14))

    def test_2d_duzy_ekran(self):
        for W, H in ((1366, 768), (1920, 1080), (2560, 1440)):
            u = self.sprawdz(W, H)
            self.assertLessEqual(u["szer"], D["ui"]["okno_maks_px"][0])
            self.assertLessEqual(u["wys"], D["ui"]["okno_maks_px"][1])

    def test_2e_inne_telefony(self):
        for W, H in ((812, 375), (896, 414), (1024, 768)):
            self.sprawdz(W, H)

    def test_2f_wiersze_i_zakladki(self):
        for k in DK["klasy"]:
            dane = LK.podstawowe(DK, LK.nowe(DK), k)[0]
            zal = LK.zalozone(DK, k, dane, None)
            of = LK.oferta(DK, dane, k, 6, 400, zal)
            g = LS.grupy(D, of)
            self.assertEqual([x["id"] for x in g], ["start", "las", "bagno", "dzungla"])
            self.assertEqual(sum(len(x["wiersze"]) for x in g), len(DK["klasy"][k]["wszystkie"]))
            for o in of:
                w = LS.wiersz(D, o)
                self.assertEqual(w["aktywny"], o["stan"] in ("kup", "masz"), o)
                self.assertEqual(w["akcja"], {"kup": "kup", "masz": "zaloz"}.get(o["stan"], ""), o)
                self.assertIn(str(o["poziom"]), w["wymaga"])
                if o["stan"] == "za_drogie":
                    self.assertNotEqual(o["cena"] - 400, 1)
                    self.assertEqual(w["powod"], "Brakuje ci %d Rybek." % (o["cena"] - 400))
                if o["stan"] == "za_niski_poziom":
                    self.assertEqual(w["powod"], "Potrzebujesz poziomu %d." % o["poziom"])
            self.assertIn(LS.pierwsza_zakladka(D, of), ("start", "las"))


# ------------------------------------------------------------------------------------------------ 3. kupno na atrapie
class Portfel:
    """Atrapa stanu gracza: Złoto nigdy poniżej zera, odmowa „za_malo” z brakującą kwotą (jak WydajZloto)."""

    def __init__(self, zloto):
        self.zloto = zloto
        self.wydatki = []

    def wydaj(self, ile, zrodlo, cel):
        if ile > self.zloto:
            return {"ok": False, "powod": "za_malo", "brakuje": ile - self.zloto}
        self.zloto -= ile
        self.wydatki.append((ile, zrodlo, cel))
        return {"ok": True, "zloto": self.zloto}


def kup_na_atrapie(dane, klasa, poziom, portfel, pid, napis):
    """Ta sama kolejność co w SerwerKowala: logika → portfel → posiadanie → założenie według reguły."""
    ok, w, info = LK.kup(DK, dane, klasa, poziom, portfel.zloto, pid)
    if not ok:
        return dane, napis, {"ok": False, "powod": w, "brakuje": info}
    r = portfel.wydaj(info["cena"], "KowalProba", DK["sklep"]["celWydatku"])
    if not r["ok"]:
        return dane, napis, {"ok": False, "powod": "za_malo_zlota", "brakuje": r["brakuje"]}
    zal = LK.zalozone(DK, klasa, w, napis)
    if LK.czy_zalozyc(DK, zal, pid):
        napis = LK.stroj_z_przedmiotem(DK, napis, pid)
    return w, napis, {"ok": True, "zalozony": pid in LK.zalozone(DK, klasa, w, napis)}


class TestKupnaNaAtrapie(unittest.TestCase):
    def start(self, klasa):
        dane = LK.podstawowe(DK, LK.nowe(DK), klasa)[0]
        return dane, LK.na_napis(LK.zalozone(DK, klasa, dane, None))

    def test_3a_wszystkie_nowe_przedmioty(self):
        for k in DK["klasy"]:
            dane, napis = self.start(k)
            portfel = Portfel(10 ** 6)
            suma = 0
            for pid in nowe(k):
                przed = LK.mod(DK, k, dane, LK.zalozone(DK, k, dane, napis))
                dane, napis, r = kup_na_atrapie(dane, k, 30, portfel, pid, napis)
                self.assertTrue(r["ok"], (pid, r))
                self.assertTrue(r["zalozony"], "%s: wyższy stopień zakłada się sam (kupowane po kolei)" % pid)
                self.assertEqual(dane["przedmioty"][pid], {"poziom": 0, "zapas": 0})
                suma += DK["przedmioty"][pid]["cena"]
                po = LK.mod(DK, k, dane, LK.zalozone(DK, k, dane, napis))
                self.assertNotEqual(przed, po, "%s zmienia wpis Modyfikatory" % pid)
            self.assertEqual(portfel.zloto, 10 ** 6 - suma)
            self.assertTrue(all(w[1:] == ("KowalProba", "zakup_przedmiotu") for w in portfel.wydatki))
            zal = LK.zalozone(DK, k, dane, napis)
            self.assertEqual({DK["przedmioty"][i]["nrStopnia"] for i in zal}, {3}, "na końcu cały komplet Dżungli")
            self.assertEqual(len(zal), len({DK["przedmioty"][i]["slot"] for i in zal}), "jeden przedmiot na slot")
            self.assertEqual(LK.stac_na(DK, dane, k, 30, 10 ** 6),
                             len([i for i in DK["klasy"][k]["przedmioty"] if i not in dane["przedmioty"]]))

    def test_3b_odmowy(self):
        dane, napis = self.start("wojownik")
        pid = nowe("wojownik", "Helmet", 1)[0]
        P = DK["przedmioty"][pid]
        przypadki = [
            ("nie_ma", 30, 10 ** 5, "nieznany_przedmiot", 0),
            (17, 30, 10 ** 5, "nieznany_przedmiot", 0),
            (DK["czescCalosci"][nowe("wojownik", "Chest", 1)[0]], 30, 10 ** 5, "czesc_zbroi", 0),
            (nowe("mag")[0], 30, 10 ** 5, "inna_klasa", 0),
            (DK["klasy"]["wojownik"]["podstawowe"][0], 30, 10 ** 5, "masz", 0),
            (pid, P["poziom"] - 2, 10 ** 5, "za_niski_poziom", 2),
            (pid, 30, P["cena"] - 150, "za_malo_zlota", 150),
        ]
        for x, poziom, zloto, powod, brakuje in przypadki:
            portfel = Portfel(zloto)
            d2, n2, r = kup_na_atrapie(dane, "wojownik", poziom, portfel, x, napis)
            self.assertEqual((r["ok"], r["powod"], r["brakuje"]), (False, powod, brakuje), x)
            self.assertIs(d2, dane, "odmowa niczego nie zmienia")
            self.assertEqual((n2, portfel.zloto, portfel.wydatki), (napis, zloto, []))

    def test_3c_dwa_razy_i_regula_zakladania(self):
        dane, napis = self.start("wojownik")
        portfel = Portfel(10 ** 5)
        bagno, las = nowe("wojownik", "Helmet", 2)[0], nowe("wojownik", "Helmet", 1)[0]
        dane, napis, r = kup_na_atrapie(dane, "wojownik", 30, portfel, bagno, napis)
        self.assertTrue(r["ok"] and r["zalozony"], "pusty slot: zakłada się sam")
        po = portfel.zloto
        dane, napis, r = kup_na_atrapie(dane, "wojownik", 30, portfel, bagno, napis)
        self.assertEqual((r["ok"], r["powod"], portfel.zloto), (False, "masz", po), "drugie kupno nie zabiera Złota")
        dane, napis, r = kup_na_atrapie(dane, "wojownik", 30, portfel, las, napis)
        self.assertTrue(r["ok"])
        self.assertFalse(r["zalozony"], "niższy stopień nie zdejmuje wyższego")
        self.assertIn(bagno, napis.split(","))
        napis = LK.stroj_z_przedmiotem(DK, napis, las)        # ręczne „Załóż”
        self.assertEqual([i for i in LK.zalozone(DK, "wojownik", dane, napis)
                          if DK["przedmioty"][i]["slot"] == "Helmet"], [las])
        # ten sam stopień zostaje dotychczasowy: startowy hełm z łupu nie zdejmuje kupionego leśnego
        start_helm = next(i for i in DK["klasy"]["wojownik"]["przedmioty"] if DK["przedmioty"][i]["slot"] == "Helmet")
        self.assertFalse(LK.czy_zalozyc(DK, LK.zalozone(DK, "wojownik", dane, napis), start_helm))
        # zbroja: nowa wypiera starą razem z jej częścią
        zbroja = nowe("wojownik", "Chest", 1)[0]
        n2 = LK.stroj_z_przedmiotem(DK, "rycerz_miecz,rycerz_zbroja,rycerz_nogawice,rycerz_tarcza", zbroja)
        self.assertEqual(n2, "rycerz_miecz,rycerz_tarcza," + zbroja)

    def test_3d_lup_tylko_ze_stopnia_startowego(self):
        for k in DK["klasy"]:
            dane, _n = self.start(k)
            ids = set()
            for i in range(200):
                _w, lup = LK.lup(DK, dane, k, "straznik", 0.0, i / 200.0)
                ids.add(lup["id"])
            self.assertEqual(ids, set(DK["klasy"][k]["przedmioty"]), "łup = dzisiejsza lista klasy")
            self.assertTrue(all(DK["przedmioty"][i]["nrStopnia"] == 0 for i in ids))
            # okno kowala gracza, który nic nie kupił: tylko dzisiejsze przedmioty
            w = LK.widok(DK, dane, k, LK.zalozone(DK, k, dane, None), 0, "")
            self.assertEqual([x["id"] for x in w["wiersze"]],
                             [i for i in DK["klasy"][k]["przedmioty"] if i in dane["przedmioty"]]
                             + [i for i in DK["klasy"][k]["przedmioty"] if i not in dane["przedmioty"]])


# ------------------------------------------------------------------------------------------------ 4. prawdziwe serwery
@unittest.skipIf(LM is None, "brak tools/walka/luau_mini.py — Luau nie wykonany")
class TestSerwerow(TK.SerweryOffline, unittest.TestCase):
    """SerwerSklepu + SerwerKowala + SerwerStanu + SerwerStrojow w jednym interpreterze z atrapą Roblox."""

    def start(self, klasa="Warrior", poziom=30, zloto=5000, **kw):
        self.uruchom(klasa=klasa, **kw)
        self.kontener_sklepu()
        self.gracz.ustaw("Level", float(poziom))
        self.gracz.ustaw("Gold", float(zloto))
        self.przy_zbrojmistrzu()

    def kontener_sklepu(self):
        AR = self.AR
        ks = AR.Inst(self.sw, "SklepProba", "Folder", self.sw.workspace)
        ks.ustaw("Wygenerowane", True)
        f = {n: AR.Inst(self.sw, n, "Folder", ks) for n in ("Moduly", "Zdalne", "Sygnaly")}
        self.sw.modul(f["Moduly"], "DaneSklepu", DANE_LUAU)
        self.sw.modul(f["Moduly"], "LogikaSklepu", LOGIKA)
        self.zdalny = AR.Inst(self.sw, "Sklep", "RemoteFunction", f["Zdalne"])
        self.ster_sklepu = AR.Inst(self.sw, "SterowanieSerwera", "BindableFunction", f["Sygnaly"])
        self.ks = ks
        self._skrypt(ks, SERWER, "SerwerSklepu.server.luau")

    def przy_zbrojmistrzu(self, dx=1.0, dz=1.0):
        p = D["miejsce"]["punkt"]
        self.postaw(p[0] + dx, p[2] + dz)

    def prosba(self, akcja, pid=None, czas=1.0):
        if czas:
            self.sw.krok(czas)
        w = self.sw.wolaj(self.zdalny.t.get("OnServerInvoke"), self.gracz.t, akcja, pid)
        return LM.z_luau(w[0]) if w else None

    def posiadane(self):
        return self.hak("stan", self.gracz.t)["dane"]["przedmioty"]

    def stroj_teraz(self):
        return (self.atr("StrojProba_wojownik") or "").split(",")

    def test_4a_gotowosc_i_oferta(self):
        self.start()
        self.assertEqual(self.ks.atrybuty.get("SerwerSklepuGotowy"), True)
        self.assertTrue(str(self.ks.atrybuty.get("ZgodnoscLogikiSklepu")).startswith("OK"))
        self.assertEqual(self.ks.atrybuty.get("KowalPodlaczony"), True)
        self.assertEqual(self.kp.atrybuty.get("WejscieSklepu"), True)
        r = self.prosba("oferta")
        self.assertTrue(r["ok"], r)
        w = r["widok"]
        self.assertEqual((w["zloto"], w["poziom"], w["klasa"]), (5000, 30, "wojownik"))
        self.assertEqual([o["id"] for o in w["oferta"]], DK["klasy"]["wojownik"]["wszystkie"])
        stany = {o["id"]: o["stan"] for o in w["oferta"]}
        for pid in DK["klasy"]["wojownik"]["podstawowe"]:
            self.assertEqual(stany[pid], "zalozone", pid)
        for pid in nowe("wojownik"):
            self.assertEqual(stany[pid], "kup", pid)
        for o in w["oferta"]:
            P = DK["przedmioty"][o["id"]]
            self.assertEqual((o["cena"], o["poziom"], o["stopien"], o["slot"]),
                             (P["cena"], P["poziom"], P["stopien"], P["slot"]))
        self.assertEqual(self.atr("SklepStacNa"), LK.stac_na(DK, self.posiadane_dane(), "wojownik", 30, 5000))
        self.assertEqual(self.sw.ostrzezenia, [])

    def posiadane_dane(self):
        return self.hak("stan", self.gracz.t)["dane"]

    def test_4b_udane_kupno(self):
        self.start()
        pid = nowe("wojownik", "Helmet", 1)[0]
        P = DK["przedmioty"][pid]
        m0 = self.mody()
        b0 = self.bohater_stanu()
        r = self.prosba("kup", pid)
        self.assertTrue(r["ok"], r)
        self.assertEqual(self.atr("Gold"), 5000 - P["cena"], "Złoto w dół o cenę")
        self.assertEqual(self.posiadane()[pid], {"poziom": 0, "zapas": 0})
        self.assertIn(pid, self.atr("KowalDostepne").split(","))
        self.assertEqual(r["widok"]["zloto"], 5000 - P["cena"])
        self.assertEqual(self.ks.atrybuty.get("LicznikKupna"), 1)
        if not NOWE_W_PRZYMIERZALNI:
            self.skipTest("przymierzalnia nie zna jeszcze nowych przedmiotów — założenie niesprawdzone")
        self.assertTrue(r["zalozony"], "pusty slot: kupiony przedmiot zakłada się sam")
        self.assertIn(pid, self.stroj_teraz())
        self.assertEqual(r["tekst"], D["teksty"]["ok_kup_zalozony"] % P["nazwa"])
        stan = {o["id"]: o["stan"] for o in r["widok"]["oferta"]}
        self.assertEqual(stan[pid], "zalozone")
        m1 = self.mody()
        self.assertEqual(m1["pancerz"] - m0["pancerz"], P["baza"].get("pancerz", 0), "wpis Modyfikatory rośnie o statystyki")
        st = self.hak("stan", self.gracz.t)
        self.assertEqual(st["mod"], json.loads(json.dumps(LK.mod(DK, "wojownik", st["dane"], st["zalozone"]))))
        self.assertIn(pid, st["zalozone"])
        self.assertNotEqual(b0, self.bohater_stanu(), "kupiony przedmiot zmienia bohatera walki")
        self.assertEqual([o for o in self.sw.ostrzezenia if "Proba" in o], [])

    def test_4c_zbroja_z_czescia_i_regula_zakladania(self):
        if not NOWE_W_PRZYMIERZALNI:
            self.skipTest("przymierzalnia nie zna jeszcze nowych przedmiotów")
        self.start(zloto=20000)
        zbroja = nowe("wojownik", "Chest", 1)[0]
        czesc = DK["czescCalosci"][zbroja]
        r = self.prosba("kup", zbroja)
        self.assertTrue(r["ok"] and r["zalozony"], r)
        stroj = self.stroj_teraz()
        self.assertIn(zbroja, stroj)
        self.assertIn(czesc, stroj, "część zbroi idzie razem ze zbroją")
        self.assertNotIn("rycerz_zbroja", stroj, "wyższy stopień zastępuje startową zbroję")
        self.assertNotIn("rycerz_nogawice", stroj)
        # wyższy stopień najpierw, potem niższy: dotychczasowy zostaje, „Załóż” zmienia ręcznie
        bagno, las = nowe("wojownik", "Helmet", 2)[0], nowe("wojownik", "Helmet", 1)[0]
        self.assertTrue(self.prosba("kup", bagno)["zalozony"])
        r = self.prosba("kup", las)
        self.assertTrue(r["ok"], r)
        self.assertFalse(r["zalozony"], "przy wyższym stopniu w slocie zostaje dotychczasowy")
        self.assertEqual(r["tekst"], D["teksty"]["ok_kup_schowany"] % DK["przedmioty"][las]["nazwa"])
        self.assertIn(bagno, self.stroj_teraz())
        self.assertNotIn(las, self.stroj_teraz())
        stan = {o["id"]: o["stan"] for o in r["widok"]["oferta"]}
        self.assertEqual((stan[bagno], stan[las]), ("zalozone", "masz"))
        m_bagno = self.mody()["pancerz"]
        r = self.prosba("zaloz", las)
        self.assertTrue(r["ok"] and r["zalozony"], r)
        self.assertIn(las, self.stroj_teraz())
        self.assertNotIn(bagno, self.stroj_teraz())
        self.assertEqual(self.mody()["pancerz"] - m_bagno, DK["przedmioty"][las]["baza"].get("pancerz", 0)
                         - DK["przedmioty"][bagno]["baza"].get("pancerz", 0), "liczy się założony, nie każdy posiadany")
        self.assertEqual([o for o in self.sw.ostrzezenia if "Proba" in o], [])

    def test_4d_odmowy(self):
        self.start()
        pid = nowe("wojownik", "Helmet", 1)[0]
        P = DK["przedmioty"][pid]
        zloto0, dane0 = self.atr("Gold"), self.posiadane()
        for x, powod in (("nie_ma", "nieznany_przedmiot"), (DK["czescCalosci"][nowe("wojownik", "Chest", 1)[0]], "czesc_zbroi"),
                         (nowe("mag")[0], "inna_klasa"), (DK["klasy"]["wojownik"]["podstawowe"][0], "masz")):
            r = self.prosba("kup", x)
            self.assertEqual((r["ok"], r["powod"]), (False, powod), x)
            self.assertEqual(r["tekst"], LS.komunikat(D, "kup", {"ok": False, "powod": powod}))
        self.gracz.ustaw("Level", float(P["poziom"] - 1))
        r = self.prosba("kup", pid)
        self.assertEqual((r["powod"], r["brakuje"]), ("za_niski_poziom", 1))
        self.assertEqual(r["tekst"], "Potrzebujesz poziomu %d." % P["poziom"])
        self.gracz.ustaw("Level", 30.0)
        self.gracz.ustaw("Gold", float(P["cena"] - 150))
        r = self.prosba("kup", pid)
        self.assertEqual((r["powod"], r["brakuje"], r["tekst"]), ("za_malo_zlota", 150, "Brakuje ci 150 Rybek."))
        self.assertEqual(self.atr("Gold"), P["cena"] - 150)
        self.gracz.ustaw("Gold", float(zloto0))
        self.przy_zbrojmistrzu(40.0, 0.0)
        r = self.prosba("kup", pid)
        self.assertEqual((r["powod"], r["tekst"]), ("daleko", D["teksty"]["podejdz"]))
        self.przy_zbrojmistrzu()
        self.assertTrue(self.prosba("oferta")["ok"])
        r = self.prosba("kup", pid, czas=0)
        self.assertEqual((r["powod"], r["tekst"]), ("za_szybko", D["teksty"]["za_szybko"]))
        for zly in (("kradnij", pid), ("kup", "x" * 80)):
            self.assertFalse(self.prosba(*zly)["ok"])
        self.assertEqual(self.prosba("zaloz", pid)["powod"], "nie_masz")
        self.assertEqual((self.atr("Gold"), self.posiadane()), (zloto0, dane0), "odmowy niczego nie zmieniają")
        self.assertEqual(self.ks.atrybuty.get("LicznikKupna"), None)

    def test_4e_dwa_razy_pod_rzad(self):
        self.start()
        pid = nowe("wojownik", "Belt", 1)[0]
        cena = DK["przedmioty"][pid]["cena"]
        r1 = self.prosba("kup", pid)
        r2 = self.prosba("kup", pid, czas=0)
        r3 = self.prosba("kup", pid)
        self.assertTrue(r1["ok"], r1)
        self.assertEqual((r2["powod"], r3["powod"]), ("za_szybko", "masz"))
        self.assertEqual(self.atr("Gold"), 5000 - cena, "Złoto zabrane tylko raz")
        self.assertEqual(self.ks.atrybuty.get("LicznikKupna"), 1)

    def test_4f_stac_na_i_lup(self):
        self.start(poziom=1, zloto=0)
        self.assertEqual(self.atr("SklepStacNa"), 0)
        self.gracz.ustaw("Gold", 100000.0)
        n1 = self.atr("SklepStacNa")
        self.assertEqual(n1, LK.stac_na(DK, self.posiadane_dane(), "wojownik", 1, 100000))
        self.gracz.ustaw("Level", 30.0)
        n30 = self.atr("SklepStacNa")
        self.assertEqual(n30, LK.stac_na(DK, self.posiadane_dane(), "wojownik", 30, 100000))
        self.assertGreater(n30, n1)
        pid = nowe("wojownik", "Belt", 1)[0]
        self.assertTrue(self.prosba("kup", pid)["ok"])
        self.assertEqual(self.atr("SklepStacNa"), n30 - 1)
        # łup dalej tylko z dzisiejszej listy klasy
        ids = set()
        for i in range(40):
            ids.add(self.hak("lup", self.gracz.t, "straznik", i / 40.0)["lup"]["id"])
        self.assertTrue(ids <= set(DK["klasy"]["wojownik"]["przedmioty"]), ids)

    def test_4g_bez_kowala_i_bez_stanu(self):
        self.start()
        self.kp.usun()
        r = self.prosba("oferta")
        self.assertEqual((r["ok"], r["powod"], r["tekst"]), (False, "nieczynny", "Sklep nieczynny (próba)."))
        r = self.prosba("kup", nowe("wojownik")[0])
        self.assertEqual((r["ok"], r["powod"]), (False, "nieczynny"))
        self.sw.krok(D["kowal"]["coIleS"] + 0.1)
        self.assertEqual(self.ks.atrybuty.get("KowalPodlaczony"), False)
        self.assertEqual([o for o in self.sw.ostrzezenia if "SklepProba" in o], [])
        self.start(stan_gracza=False)
        r = self.prosba("oferta")
        self.assertEqual((r["ok"], r["tekst"]), (False, "Sklep nieczynny (próba)."))
        r = self.prosba("kup", nowe("wojownik")[0])
        self.assertEqual((r["ok"], r["tekst"]), (False, "Sklep nieczynny (próba)."))
        self.assertEqual([o for o in self.sw.ostrzezenia if "SklepProba" in o], [])

    def test_4h_bez_przymierzalni(self):
        self.start(stroje=False)
        bagno, las = nowe("wojownik", "Helmet", 2)[0], nowe("wojownik", "Helmet", 1)[0]
        self.assertTrue(self.prosba("kup", bagno)["zalozony"], "bez przymierzalni liczy się najwyższy stopień w slocie")
        m = self.mody()["pancerz"]
        r = self.prosba("kup", las)
        self.assertTrue(r["ok"])
        self.assertFalse(r["zalozony"])
        self.assertEqual(self.mody()["pancerz"], m)
        self.assertEqual(self.prosba("zaloz", las)["ok"], False)


# ------------------------------------------------------------------------------------------------ 5. narzędzia
class TestNarzedzi(unittest.TestCase):
    def test_5a_kontrola_luau(self):
        bledy, _p = SLS.sprawdz_pliki(SLS.pliki_pakietu(), wypisz=lambda *_: None)
        self.assertEqual(bledy, [])

    def test_5b_zbuduj_sucho_i_kod_budowy(self):
        r = subprocess.run([sys.executable, "-B", os.path.join(PAKIET, "zbuduj.py"), "--sucho"], capture_output=True,
                           timeout=300, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace")[-2000:])
        if LM is not None:
            ZB = _modul("zbuduj_sklepu_test", os.path.join(PAKIET, "zbuduj.py"))
            for nazwa, kod in ZB.wszystkie_kody().items():
                LM.Parser(ZB.NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", "1") + kod, nazwa, LM.Interpreter()).program()

    def test_5c_bez_sciezek_lokalnych(self):
        # wzorce składane z kawałków, żeby ten plik sam ich nie zawierał
        zakazane = [re.compile(r"[A-Za-z]:\\" + "Users" + r"\\"), re.compile("App" + "Data"), re.compile("/" + "Users/")]
        for root, _d, pliki in os.walk(PAKIET):
            if "__pycache__" in root:
                continue
            for p in pliki:
                if p.endswith((".py", ".luau", ".json", ".md")):
                    t = czytaj(root, p)
                    for z in zakazane:
                        self.assertIsNone(z.search(t), "%s: %s" % (p, z.pattern))

    def test_5d_proba_play_sprawdz(self):
        sciezka = os.path.join(TESTY, "proba_play.py")
        if not os.path.isfile(sciezka):
            self.skipTest("brak proba_play.py")
        r = subprocess.run([sys.executable, "-B", sciezka, "--sprawdz"], capture_output=True, timeout=300,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"))
        self.assertEqual(r.returncode, 0, r.stdout.decode("utf-8", "replace")[-2000:])


if __name__ == "__main__":
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    unittest.main(verbosity=1)
