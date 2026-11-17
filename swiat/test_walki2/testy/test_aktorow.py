#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy aktorów próby walki BEZ Studio (unittest): tabela aktorów kontra dane silnika, dane klipów, punkty, przenikanie broni.

    python -B swiat/test_walki2/testy/test_aktorow.py            # wszystkie testy
    python -B swiat/test_walki2/testy/test_aktorow.py -v

Pilnuje, żeby:
- każda klasa i każdy przeciwnik z tools/walka/dane_walki.json miał aktora, a każda jego umiejętność wpis w tabeli
  (klip albo jawne None = ruch proceduralny) — nowa umiejętność w danych bez wpisu = błąd, nie cicha dziura;
- każda akcja z AKCJE miała wpis, a blok — klip u klasy z tarczą;
- dane/<klucz>.json były kompletne: klatki 0…dl, szerokość wiersza = 6 × liczba kości, pętle domknięte, punkty;
- broń (miecz, tarcza, łuk, sztylet, kostur, maczuga, laska) nie wchodziła w głowę ani tułów w żadnej klatce
  KLIPÓW ZASTĘPCZYCH (przerobki.py); w klipach modeli z swiat/postacie/ to samo jest liczone i wypisywane
  (tych modeli ten prototyp nie zmienia — wynik idzie do raportu);
- (etap 8) Wojownik i Mag grali WŁASNE klipy modułów (bez klipów zastępczych), z chwilami z CHWILE modułów, każda
  chwila leżała ściśle wewnątrz swojego klipu; Wojownik miał dokładnie jedną tarczę (przedmiot modułu na lewej dłoni,
  D-071), a punkt Tarcza leżał na jej godle; punkt Bron/Pocisk Maga szedł za kryształem kostura w każdej klatce (także
  w upadku), a kapelusz i kostur siedziały na kościach HatPivot / StaffPivot i po upadku leżały na ziemi z dala od głowy
  i łapy; ręczna chwila uniku była klatką największego odskoku; klipy z „ruch_w_klipie” naprawdę przesuwały postać;
- (etap 9) cios wręcz Wojownika z bronią daleko z boku osi (miażdżący cios) był w „celowanie” z kątem 10–35°.
"""
import json
import math
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
from geometria import Rig, punkt, punkty_probne, w_pudle  # noqa: E402

with open(os.path.join(REPO, "tools", "walka", "dane_walki.json"), encoding="utf-8") as _f:
    SILNIK = json.load(_f)

# broń: grupy akcesoriów (rig "grupy") albo kości z bryłami broni; ciało: kości, w które broń nie może wchodzić
BRON = {
    "wojownik": {"grupy": ["rycerz_miecz", "rycerz_tarcza"], "cialo": ["Head", "UpperTorso", "LowerTorso"]},
    "zwiadowca": {"grupy": ["zwiadowca_luk", "zwiadowca_sztylet"], "cialo": ["Head", "UpperTorso", "LowerTorso"]},
    "mag": {"grupy": ["kot_mag_kostur"], "cialo": ["Head", "UpperTorso", "LowerTorso"]},
    "lesny_troll": {"kosci": ["Maczuga"], "cialo": ["Glowa", "Tulow"]},
    "straznik_lasu": {"kosci": ["DlonL", "DlonP"], "cialo": ["Glowa"]},
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


def _punkt(r, d, nazwa, pozy):
    p = next(p for p in d["punkty"] if p[0] == nazwa)
    return punkt(pozy[p[1]], tuple(p[2:5]))


def _bryla(r, d, grupa, nazwa, pozy):
    gi = d["grupy"].index(grupa)
    c = next(c for c in d["czesci"] if c[14] == gi and c[2] == nazwa)
    return r.czesc_cf(c, pozy)[1]


class Bohaterowie(unittest.TestCase):
    """Etap 8: Wojownik i Mag na własnych klipach modułów rycerz.py / kot_mag.py."""

    def test_bez_klipow_zastepczych(self):
        for k in ("wojownik", "mag"):
            w = A.PO_KLUCZU[k]
            self.assertIsNone(w["przerobka"], "%s: szkice z przerobki.py nie są już potrzebne" % k)
            self.assertEqual(w["zastepcze_klipy"], [])

    def test_chwile_z_modulu_i_w_klipie(self):
        from swiat.postacie.roblox_postac import wczytaj_modul
        for k in ("wojownik", "mag"):
            w = A.PO_KLUCZU[k]
            d = A.wczytaj(k)
            dl = {c["n"]: c["dl"] / float(c["fps"]) for c in d["klipy"]}
            modul = wczytaj_modul(os.path.join(REPO, "swiat", "postacie", w["model"] + ".py"))
            for klip, klatka in modul.CHWILE.items():
                self.assertAlmostEqual(d["chwile"][klip], klatka / 30.0, places=3, msg="%s/%s: chwila ≠ CHWILE modułu" % (k, klip))
            # każdy klip ataku i umiejętności ma chwilę z modułu, a każda chwila leży w swoim klipie
            for klip in [w["klipy"]["atak"], w["klipy"]["krytyk"]] + list(w["umiejetnosci"].values()):
                self.assertIn(klip, modul.CHWILE, "%s/%s: brak chwili w CHWILE modułu" % (k, klip))
            for klip, s in d["chwile"].items():
                self.assertTrue(0 < s < dl[klip], "%s/%s: chwila %.3f nie leży wewnątrz klipu (%.3f s)" % (k, klip, s, dl[klip]))

    def test_chwila_uniku_w_najwiekszym_odskoku(self):
        # ręczna chwila „unik” (aktorzy.py) = klatka największego odskoku bioder w poziomie — odtwarzacz kładzie ją
        # w chwili trafienia; gdy moduł zmieni klip uniku, ta liczba ma się zmienić razem z nim
        for k in ("wojownik", "mag"):
            d = A.wczytaj(k)
            r = Rig(d)
            lt = r.indeks["LowerTorso"]
            spocz = r.pozy()[lt][1]
            kl = r.klipy["unik"]
            odl = [math.hypot(r.pozy(r.transformy("unik", f))[lt][1][0] - spocz[0],
                              r.pozy(r.transformy("unik", f))[lt][1][2] - spocz[2]) for f in range(kl["dl"] + 1)]
            szczyt = max(range(len(odl)), key=lambda f: odl[f])
            f = d["chwile"]["unik"] * kl["fps"]
            self.assertLessEqual(abs(f - szczyt), 1.01, "%s: chwila uniku kl. %.1f, największy odskok kl. %d" % (k, f, szczyt))
            self.assertGreater(odl[szczyt], 1.0, "%s: unik bez odskoku (%.2f studa)" % (k, odl[szczyt]))

    def test_kapelusz_i_kostur_maga_leza_na_ziemi_po_upadku(self):
        # ostatnia klatka upadku (odtwarzacz ją trzyma): kapelusz i kostur leżą na ziemi, z dala od łapy i głowy
        from geometria import narozniki
        d = A.wczytaj("mag")
        r = Rig(d)
        pozy = r.pozy(r.transformy("upadek", r.klipy["upadek"]["dl"]))
        for grupa, kosc, odstep in (("kot_mag_kapelusz", "Head", 1.0), ("kot_mag_kostur", "RightHand", 1.5)):
            gi = d["grupy"].index(grupa)
            rogi = [q for c in d["czesci"] if c[14] == gi for q in narozniki(r.czesc_cf(c, pozy), c[9:12])]
            spod = min(q[1] for q in rogi)
            sr = [sum(q[i] for q in rogi) / len(rogi) for i in range(3)]
            self.assertLess(abs(spod), 0.05, "%s po upadku nie leży na ziemi (spód %.2f)" % (grupa, spod))
            od_kosci = math.dist(sr, pozy[r.indeks[kosc]][1])
            self.assertGreater(od_kosci, odstep, "%s po upadku %.2f studa od %s — nie spadł" % (grupa, od_kosci, kosc))

    def test_jedna_tarcza_wojownika_i_punkt_na_godle(self):
        d = A.wczytaj("wojownik")
        r = Rig(d)
        self.assertEqual(d["grupy"].count("rycerz_tarcza"), 1, "D-071: dokładnie jedna tarcza")
        gi = d["grupy"].index("rycerz_tarcza")
        kosci = {d["kosci"][c[0] - 1][0] for c in d["czesci"] if c[14] == gi}
        self.assertEqual(kosci, {"LeftHand"}, "tarcza modułu siedzi na LeftGripAttachment (kość LeftHand)")
        self.assertNotIn("TarczaAttachment", [z[0] for z in d["zaczepy"]], "dawna tarcza prototypu wróciła")
        kl = next(c for c in d["klipy"] if c["n"] == "blok")
        for f in range(kl["dl"] + 1):
            pozy = r.pozy(r.transformy("blok", f))
            odl = math.dist(_punkt(r, d, "Tarcza", pozy), _bryla(r, d, "rycerz_tarcza", "Godlo", pozy))
            self.assertLess(odl, 0.1, "blok kl. %d: punkt Tarcza %.2f studa od godła tarczy" % (f, odl))
        # w chwili ciosu w tarczę godło jest przed Rycerzem (przód rigu = −Z), na wysokości tułowia
        pozy = r.pozy(r.transformy("blok", int(round(d["chwile"]["blok"] * 30))))
        q = _punkt(r, d, "Tarcza", pozy)
        self.assertGreater(-q[2], 1.0)
        self.assertTrue(1.5 < q[1] < 4.5, "tarcza na wysokości %.2f" % q[1])
        self.assertNotIn("rycerz_tarcza", A.wczytaj("mag")["grupy"])

    def test_krysztal_maga_idzie_za_kosturem_i_kosci_nosne(self):
        d = A.wczytaj("mag")
        r = Rig(d)
        kosci = [k[0] for k in d["kosci"]]
        for grupa, kosc in (("kot_mag_kapelusz", "HatPivot"), ("kot_mag_kostur", "StaffPivot")):
            gi = d["grupy"].index(grupa)
            self.assertEqual({kosci[c[0] - 1] for c in d["czesci"] if c[14] == gi}, {kosc},
                             "%s ma siedzieć na kości %s (spada w upadku)" % (grupa, kosc))
        for nazwa in ("Bron", "Pocisk"):
            p = next(p for p in d["punkty"] if p[0] == nazwa)
            self.assertEqual(kosci[p[1] - 1], "StaffPivot", "punkt %s Maga ma iść za kosturem" % nazwa)
        for kl in d["klipy"]:
            for f in range(0, kl["dl"] + 1, 2):
                pozy = r.pozy(r.transformy(kl["n"], f))
                odl = math.dist(_punkt(r, d, "Pocisk", pozy), _bryla(r, d, "kot_mag_kostur", "Krysztal gora", pozy))
                self.assertLess(odl, 0.35, "%s kl. %d: punkt Pocisk %.2f studa od kryształu" % (kl["n"], f, odl))

    def test_punkt_w_chwili_trafienia_przed_aktorem(self):
        # punkt broni (Wojownik) i wylot pocisku (Mag) w chwili trafienia / wypuszczenia: przed aktorem, nad ziemią
        for k, nazwa in (("wojownik", "Bron"), ("mag", "Pocisk")):
            w = A.PO_KLUCZU[k]
            d = A.wczytaj(k)
            r = Rig(d)
            for akcja, klip in list(w["umiejetnosci"].items()) + [("atak", w["klipy"]["atak"])]:
                if akcja in ("kamienna_skora", "bariera"):
                    continue                                     # na siebie: bez trafienia
                f = int(round(d["chwile"][klip] * 30))
                q = _punkt(r, d, nazwa, r.pozy(r.transformy(klip, f)))
                self.assertGreater(-q[2], 2.0, "%s/%s: punkt %s %.2f studa przed aktorem" % (k, klip, nazwa, -q[2]))
                self.assertTrue(1.0 < q[1] < 4.0, "%s/%s: punkt %s na wysokości %.2f" % (k, klip, nazwa, q[1]))

    def test_celowanie_ciosu_z_boku(self):
        # etap 9 (Studio): klinga miażdżącego ciosu spadała 1,4–3,3 studa w prawo od osi i mijała wąskie cele — klip
        # ciosu wręcz Wojownika z punktem Bron ponad 1,5 studa z boku w chwili trafienia musi być w „celowanie”, a kąt
        # obrotu (atan(bok / przód), liczy zbuduj.py) ma być rozsądny: 10–35°
        w = A.PO_KLUCZU["wojownik"]
        d = A.wczytaj("wojownik")
        r = Rig(d)
        for klip in [w["klipy"]["atak"], "ciecie", "miazdzacy_cios"]:
            f = int(round(d["chwile"][klip] * 30))
            q = _punkt(r, d, "Bron", r.pozy(r.transformy(klip, f)))
            kat = math.degrees(math.atan2(q[0], -q[2]))
            if klip in w.get("celowanie", []):
                self.assertTrue(10 < abs(kat) < 35, "%s: kąt celowania %.1f°" % (klip, kat))
            else:
                self.assertLess(abs(q[0]), 1.5, "%s: broń %.2f studa z boku osi, a klipu nie ma w „celowanie”" % (klip, q[0]))
        self.assertIn("miazdzacy_cios", w.get("celowanie", []))

    def test_ruch_w_klipie_naprawde_rusza_postac(self):
        # flaga „ruch_w_klipie” wyłącza ruch proceduralny odtwarzacza — klip musi więc sam przesuwać biodra
        for w in A.AKTORZY:
            if not w.get("ruch_w_klipie"):
                continue
            d = A.wczytaj(w["klucz"])
            r = Rig(d)
            lt = r.indeks["LowerTorso"]
            for klip in w["ruch_w_klipie"]:
                kl = r.klipy[klip]
                j = kl["kosci"].index(lt)
                maks = max(max(math.hypot(x[j * 6], x[j * 6 + 2]), abs(x[j * 6 + 1])) for x in kl["klatki"])
                self.assertGreater(maks, 0.1, "%s/%s: klip nie przesuwa postaci (%.2f studa)" % (w["klucz"], klip, maks))


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
