#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy aktorów walki v2 BEZ Studio (unittest): tabela aktorów kontra dane silnika, dane klipów, punkty, przenikanie broni.

    python -B swiat/test_walki2/testy/test_aktorow.py            # wszystkie testy
    python -B swiat/test_walki2/testy/test_aktorow.py -v

Pilnuje, żeby:
- każda klasa i każdy przeciwnik z tools/walka/dane_walki.json miał aktora, a każda jego umiejętność wpis w tabeli
  (klip albo jawne None = ruch proceduralny) — nowa umiejętność w danych bez wpisu = błąd, nie cicha dziura;
- każda akcja z AKCJE miała wpis, a blok — klip u klasy z tarczą;
- dane/<klucz>.json były kompletne: klatki 0…dl, szerokość wiersza = 6 × liczba kości, pętle domknięte, punkty;
- broń (miecz, tarcza, łuk, sztylet, kostur, maczuga, laska) nie wchodziła w głowę ani tułów w żadnej klatce
  KLIPÓW ZASTĘPCZYCH (przerobki.py); w klipach modeli z swiat/postacie/ to samo jest liczone i wypisywane
  (tych modeli ten prototyp nie zmienia — wynik idzie do raportu).
"""
import json
import os
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (KATALOG, REPO):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import aktorzy as A  # noqa: E402
from geometria import Rig, punkty_probne, w_pudle  # noqa: E402

with open(os.path.join(REPO, "tools", "walka", "dane_walki.json"), encoding="utf-8") as _f:
    SILNIK = json.load(_f)

# broń: grupy akcesoriów (rig "grupy") albo kości z bryłami broni; ciało: kości, w które broń nie może wchodzić
BRON = {
    "wojownik": {"grupy": ["rycerz_miecz", "rycerz_tarcza"], "cialo": ["Head", "UpperTorso", "LowerTorso"]},
    "zwiadowca": {"grupy": ["zwiadowca_luk", "zwiadowca_sztylet"], "cialo": ["Head", "UpperTorso", "LowerTorso"]},
    "mag": {"grupy": ["kot_mag_kostur"], "cialo": ["Head", "UpperTorso", "LowerTorso"]},
    "lesny_troll": {"kosci": ["Maczuga"], "cialo": ["Glowa", "Tulow"]},
    "straznik_lasu": {"kosci": ["Maczuga"], "cialo": ["Glowa", "Tulow"]},
    "muchomornik": {"kosci": ["Laska"], "cialo": ["Glowa", "Tulow"]},
}
MARGINES = 0.06       # studa: płytkie muśnięcie krawędzi bryły ciała nie liczy się jako przenikanie


def przenikanie(klucz, klip=None, krok=1):
    """Lista (klip, klatka, liczba punktów broni w ciele, kość ciała) dla aktora."""
    d = A.wczytaj(klucz)
    spec = BRON[klucz]
    r = Rig(d)
    indeks = r.indeks
    cialo = [(indeks[n], tuple(r.kosci[indeks[n] - 1][8:11])) for n in spec["cialo"] if n in indeks]
    grupy = [d["grupy"].index(g) for g in spec.get("grupy", []) if g in d["grupy"]]
    kosci_broni = {indeks[n] for n in spec.get("kosci", []) if n in indeks}
    bron = [c for c in d["czesci"] if c[14] in grupy or c[0] in kosci_broni]
    wynik = []
    for kl in d["klipy"]:
        if klip and kl["n"] != klip:
            continue
        for f in range(0, kl["dl"] + 1, krok):
            pozy = r.pozy(r.transformy(kl["n"], f))
            for i, rozmiar in cialo:
                ile = 0
                for c in bron:
                    for p in punkty_probne(r.czesc_cf(c, pozy), c[9:12]):
                        if w_pudle(p, pozy[i], rozmiar, MARGINES):
                            ile += 1
                if ile:
                    wynik.append((kl["n"], f, ile, r.kosci[i - 1][0]))
    return wynik


class TabelaKontraSilnik(unittest.TestCase):
    def test_kazda_klasa_i_przeciwnik_ma_aktora(self):
        for k in SILNIK["klasy"]:
            self.assertIn(k, A.PO_KLUCZU, "klasa %s bez aktora" % k)
            self.assertEqual(A.PO_KLUCZU[k]["rola"], "klasa")
        for p in SILNIK["przeciwnicy"]:
            self.assertIn(p["id"], A.PO_KLUCZU, "przeciwnik %s bez aktora" % p["id"])
            self.assertEqual(A.PO_KLUCZU[p["id"]]["rola"], "przeciwnik")

    def test_kazda_umiejetnosc_ma_wpis(self):
        for k, kl in SILNIK["klasy"].items():
            for u in kl["umiejetnosci"]:
                self.assertIn(u, A.PO_KLUCZU[k]["umiejetnosci"], "%s: umiejętność %s bez wpisu w tabeli aktorów" % (k, u))
        for p in SILNIK["przeciwnicy"]:
            for u in p["umiejetnosci"]:
                self.assertIn(u, A.PO_KLUCZU[p["id"]]["umiejetnosci"], "%s: umiejętność %s bez wpisu" % (p["id"], u))
        # i odwrotnie: tabela nie wymienia umiejętności, których silnik nie zna
        for w in A.AKTORZY:
            for u in w["umiejetnosci"]:
                self.assertIn(u, SILNIK["umiejetnosci"], "%s: nieznana umiejętność %s" % (w["klucz"], u))

    def test_kazda_akcja_ma_wpis_a_blok_klip_u_tarczy(self):
        for w in A.AKTORZY:
            for a in A.AKCJE:
                self.assertIn(a, w["klipy"], "%s: brak wpisu akcji %s" % (w["klucz"], a))
            for a in ("spoczynek", "atak", "trafienie", "upadek", "radosc"):
                self.assertTrue(w["klipy"][a], "%s: akcja %s musi mieć klip" % (w["klucz"], a))
        for k, kl in SILNIK["klasy"].items():
            if kl.get("tarcza"):
                self.assertTrue(A.PO_KLUCZU[k]["klipy"]["blok"], "%s nosi tarczę — blok musi mieć klip" % k)


class Dane(unittest.TestCase):
    def test_dane_kompletne(self):
        for w in A.AKTORZY:
            d = A.wczytaj(w["klucz"])
            nazwy = {k["n"]: k for k in d["klipy"]}
            for kl in list(w["klipy"].values()) + list(w["umiejetnosci"].values()):
                if kl:
                    self.assertIn(kl, nazwy, "%s: brak klipu %s" % (w["klucz"], kl))
            for k in d["klipy"]:
                self.assertEqual(len(k["klatki"]), k["dl"] + 1, "%s/%s: liczba klatek" % (w["klucz"], k["n"]))
                for wiersz in k["klatki"]:
                    self.assertEqual(len(wiersz), 6 * len(k["kosci"]))
                if k["petla"]:
                    a, b = k["klatki"][0], k["klatki"][-1]
                    roz = max(abs(x - y) for x, y in zip(a, b))
                    self.assertLess(roz, 0.02, "%s/%s: pętla nie domknięta (%.3f)" % (w["klucz"], k["n"], roz))
            self.assertEqual(sorted(p[0] for p in d["punkty"]), sorted(w["punkty"]))
            self.assertGreater(d["wymiary"]["wysokosc"], 1.0)
            self.assertLess(abs(d["wymiary"]["spod"]), 0.3, "%s: nie stoi na ziemi" % w["klucz"])

    def test_klipy_zastepcze_istnieja(self):
        for w in A.AKTORZY:
            nazwy = {k["n"] for k in A.wczytaj(w["klucz"])["klipy"]}
            for kl in w.get("zastepcze_klipy", []):
                self.assertIn(kl, nazwy)


class Bron(unittest.TestCase):
    def test_bron_nie_przechodzi_przez_glowe_ani_tulow_w_klipach_zastepczych(self):
        for klucz, spec in BRON.items():
            zast = set(A.PO_KLUCZU[klucz].get("zastepcze_klipy", []))
            for kl in sorted(zast):
                zle = przenikanie(klucz, kl)
                self.assertFalse(zle, "%s/%s: broń w ciele w klatkach %s" % (klucz, kl, zle[:6]))


def raport_przenikania():
    """Wypisuje przenikanie broni we WSZYSTKICH klipach (także modeli z swiat/postacie/)."""
    print("Przenikanie broni w ciało (klatki z punktami broni w głowie/tułowiu):")
    for klucz in BRON:
        zast = set(A.PO_KLUCZU[klucz].get("zastepcze_klipy", []))
        zle = przenikanie(klucz)
        po_klipach = {}
        for kl, f, ile, kosc in zle:
            po_klipach.setdefault(kl, []).append((f, kosc, ile))
        if not po_klipach:
            print("  %-15s brak" % klucz)
        for kl, lista in sorted(po_klipach.items()):
            print("  %-15s %-16s %s %d klatek, np. %s" % (klucz, kl, "(zastępczy)" if kl in zast else "(model)   ",
                                                          len({f for f, _, _ in lista}), lista[:3]))


if __name__ == "__main__":
    if "--raport" in sys.argv:
        raport_przenikania()
        sys.exit(0)
    unittest.main()
