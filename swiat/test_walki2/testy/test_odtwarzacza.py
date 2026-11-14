#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy odtwarzacza walki v2 BEZ Studio (unittest) + wyszukiwanie ziaren pokazowych.

    python -B swiat/test_walki2/testy/test_odtwarzacza.py            # testy
    python -B swiat/test_walki2/testy/test_odtwarzacza.py --ziarna   # policz ziarna pokazowe → testy/ziarna.json

Co sprawdza:
  1. POKRYCIE (żeby nowa umiejętność albo nowy typ zdarzenia nie zostały po cichu bez animacji):
     • każdy typ zdarzenia z Dziennik.TYPY (src/shared/Walka/Dziennik.luau) ma wpis w Choreografie.ZDARZENIA,
       a każda wskazana obsługa jest funkcją Obsluga.<nazwa> w OdtwarzaczWalki2.luau;
     • każda umiejętność z tools/walka/dane_walki.json ma wpis w Choreografie.UMIEJETNOSCI (i odwrotnie), jej styl
       ma choreografię Choreo.<styl>, a pocisk / wybuch / aura istnieją w Efekty3D (Pocisk.<x>, Wybuch.<x>);
     • każdy efekt z danych ma wpis w Choreografie.EFEKTY z wyglądem Wyglad.<x> i ikoną w interfejsie;
     • każda klasa i każdy przeciwnik ma aktora w tabeli (swiat/test_walki2/aktorzy.py) i portret w interfejsie.
  2. DZIENNIKI z portu Pythona (tools/walka/silnik.py + wzorcowe.py — to samo, co liczy serwer prototypu) dla każdej
     klasy, każdego przeciwnika, poziomów 1 / 5 / 10 i wielu ziaren: dziennik przechodzi Dziennik.sprawdz; każdy typ
     zdarzenia i każda umiejętność, które się pojawiają, mają obsługę; odtwarzacz liczy tury tak samo jak silnik
     (walka.tury); liczniki efektów w interfejsie (ta sama logika co Sesja:koniecTury w odtwarzaczu) nigdy nie gubią
     efektu i dochodzą do zera przy efekt_koniec; paski życia po każdym zdarzeniu = życie z dziennika.
  3. Wzorcowe.luau (serwer) ma te same liczby co tools/walka/wzorcowe.py (rozkłady, broń, pancerz, sloty, tarcza).
"""
import json
import os
import re
import sys
import unittest

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (os.path.join(REPO, "tools", "walka"), KATALOG):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import dziennik as DZ  # noqa: E402
import wzorcowe as WZ  # noqa: E402
import aktorzy as A  # noqa: E402

ZRODLA = os.path.join(KATALOG, "zrodla")
POZIOMY = (1, 5, 10)
ZIARNA_NA_PARE = 60


def czytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read()


def blok_tabeli(tekst, nazwa):
    """Treść tabeli `Ch.<nazwa> = { ... }` (dopasowanie nawiasów klamrowych)."""
    m = re.search(r"\bCh\.%s\s*=\s*\{" % nazwa, tekst)
    if not m:
        raise AssertionError("brak tabeli Ch.%s w Choreografie.luau" % nazwa)
    i, glebokosc = m.end(), 1
    while glebokosc:
        c = tekst[i]
        glebokosc += (c == "{") - (c == "}")
        i += 1
    return tekst[m.end():i - 1]


def wpisy(blok):
    """Wpisy pierwszego poziomu `klucz = { pola }` → {klucz: {pole: wartość-napis}}; i `klucz = "x"`."""
    wynik = {}
    for m in re.finditer(r"^\s*([a-z_]+)\s*=\s*(\{[^\n]*\}|\"[^\"]*\")\s*,", blok, re.M):
        klucz, wartosc = m.group(1), m.group(2)
        if wartosc.startswith("{"):
            pola = dict(re.findall(r"([a-zA-Z_]+)\s*=\s*\"([^\"]*)\"", wartosc))
            for k, v in re.findall(r"([a-zA-Z_]+)\s*=\s*(-?[0-9.]+|true|false)", wartosc):
                pola.setdefault(k, v)
            wynik[klucz] = pola
        else:
            wynik[klucz] = wartosc.strip('"')
    return wynik


def funkcje(tekst, rejestr):
    return set(re.findall(r"\b%s\.([a-z_]+)\s*=\s*function" % rejestr, tekst))


class Zrodla:
    ch = czytaj(os.path.join(ZRODLA, "Choreografie.luau"))
    odtw = czytaj(os.path.join(ZRODLA, "OdtwarzaczWalki2.luau"))
    efekty = czytaj(os.path.join(ZRODLA, "Efekty3D.luau"))
    ui = czytaj(os.path.join(ZRODLA, "InterfejsWalki2.luau"))
    dziennik = czytaj(os.path.join(REPO, "src", "shared", "Walka", "Dziennik.luau"))
    wzorcowe_luau = czytaj(os.path.join(ZRODLA, "Wzorcowe.luau"))
    ZDARZENIA = wpisy(blok_tabeli(ch, "ZDARZENIA"))
    UMIEJETNOSCI = wpisy(blok_tabeli(ch, "UMIEJETNOSCI"))
    EFEKTY = wpisy(blok_tabeli(ch, "EFEKTY"))
    ATAK = wpisy(blok_tabeli(ch, "ATAK"))
    WYGLAD_SPOWOLNIENIA = wpisy(blok_tabeli(ch, "WYGLAD_SPOWOLNIENIA"))
    STYLE = re.findall(r'"([a-z_]+)"', blok_tabeli(ch, "STYLE"))
    OBSLUGA = funkcje(odtw, "Obsluga")
    CHOREO = funkcje(odtw, "Choreo")
    POCISKI = funkcje(efekty, "Pocisk")
    WYBUCHY = funkcje(efekty, "Wybuch")
    WYGLADY = funkcje(efekty, "Wyglad")
    IKONY = set(re.findall(r"^\t([a-z_]+) = \{\n\t\tpaleta", ui, re.M))
    TYPY = re.findall(r'"([a-z_]+)"', re.search(r"Dziennik\.TYPY\s*=\s*\{(.*?)\}", dziennik, re.S).group(1))


# --------------------------------------------------------------------------- logika odtwarzacza (port do testu)
AKCJE_TURY = {"cios", "krytyk", "blok", "unik", "umiejetnosc", "utrata_tury", "efekt_tick"}


def odtworz(walka):
    """Ta sama księgowość co Sesja (OdtwarzaczWalki2): tury, efekty z licznikami, paski. Zwraca (tury, błędy)."""
    bledy = []
    tura, strona_tury = 0, None
    efekty = {"gracz": [], "wrog": []}
    paski = {"gracz": walka["strony"]["gracz"]["zycie"], "wrog": walka["strony"]["wrog"]["zycie"]}
    for i, z in enumerate(walka["dziennik"], 1):
        if z["typ"] in AKCJE_TURY and z["kto"] != strona_tury:
            if strona_tury is not None:
                for e in efekty[strona_tury]:          # Sesja:koniecTury
                    if e["od"] != tura:
                        e["tury"] -= 1
            tura += 1
            strona_tury = z["kto"]
            for s in efekty:
                for e in efekty[s]:
                    if e["tury"] < 1:
                        bledy.append("zd. %d: aktywny efekt %s z licznikiem %d" % (i, e["id"], e["tury"]))
        if z["typ"] == "efekt_nalozony":
            efekty[z["cel"]] = [e for e in efekty[z["cel"]] if e["id"] != z["efekt"]]
            zapas = z["wartosc"] if S.EFEKTY[z["efekt"]]["typ"] == "tarcza" else None
            efekty[z["cel"]].append({"id": z["efekt"], "tury": z["tury"], "od": tura, "zapas": zapas})
        elif z["typ"] == "efekt_koniec":
            e = next((e for e in efekty[z["cel"]] if e["id"] == z["efekt"]), None)
            if e is None:
                bledy.append("zd. %d: koniec efektu, którego odtwarzacz nie zna (%s)" % (i, z["efekt"]))
            else:
                pekla = e["zapas"] is not None and e["zapas"] <= 0
                po = e["tury"] - (0 if e["od"] == tura else 1)
                if not pekla and z["cel"] == strona_tury and po > 0:
                    bledy.append("zd. %d: efekt %s kończy się, a licznik pokazuje jeszcze %d" % (i, z["efekt"], po))
                efekty[z["cel"]].remove(e)
        if z["pochloniete"] > 0:
            ile = z["pochloniete"]
            for e in efekty[z["cel"]]:
                if e["zapas"] and ile > 0:
                    m = min(e["zapas"], ile)
                    e["zapas"] -= m
                    ile -= m
            if ile > 0:
                bledy.append("zd. %d: tarcza pochłonęła więcej, niż odtwarzacz miał w zapasie" % i)
        paski[z["cel"]] = max(0, paski[z["cel"]] - z["obrazenia"])
        if paski["gracz"] != z["hp_gracz"] or paski["wrog"] != z["hp_wrog"]:
            bledy.append("zd. %d: paski %s ≠ dziennik %s" % (i, paski, (z["hp_gracz"], z["hp_wrog"])))
    if tura != walka["tury"]:
        bledy.append("tury odtwarzacza %d ≠ silnik %d" % (tura, walka["tury"]))
    return tura, bledy


def walka(klasa, wrog, poziom, ziarno):
    return S.symuluj(WZ.postac(klasa, poziom), {"potwor": wrog, "poziom": poziom}, ziarno)


def wszystkie_walki(ziaren=ZIARNA_NA_PARE, start=1):
    for klasa in WZ.KLASY:
        for wrog in [p["id"] for p in S.PRZECIWNICY_LISTA]:
            for poziom in POZIOMY:
                for z in range(start, start + ziaren):
                    ziarno = z * 7919 + poziom * 31 + len(wrog)
                    yield klasa, wrog, poziom, ziarno, walka(klasa, wrog, poziom, ziarno)


# --------------------------------------------------------------------------- testy
class Pokrycie(unittest.TestCase):
    def test_typy_zdarzen_maja_obsluge(self):
        self.assertTrue(Zrodla.TYPY, "nie wczytałem Dziennik.TYPY")
        for typ in Zrodla.TYPY:
            self.assertIn(typ, Zrodla.ZDARZENIA, "typ zdarzenia %s bez wpisu w Choreografie.ZDARZENIA" % typ)
            self.assertIn(Zrodla.ZDARZENIA[typ], Zrodla.OBSLUGA, "brak funkcji Obsluga.%s w odtwarzaczu" % Zrodla.ZDARZENIA[typ])
        for typ in Zrodla.ZDARZENIA:
            self.assertIn(typ, Zrodla.TYPY, "Choreografie.ZDARZENIA ma typ spoza dziennika: %s" % typ)

    def test_umiejetnosci_maja_choreografie(self):
        dane = set(S.UMIEJETNOSCI)
        self.assertEqual(dane, set(Zrodla.UMIEJETNOSCI),
                         "umiejętności w danych i w Choreografie.UMIEJETNOSCI różnią się: %s"
                         % sorted(dane ^ set(Zrodla.UMIEJETNOSCI)))
        for uid, w in Zrodla.UMIEJETNOSCI.items():
            styl = w.get("styl")
            self.assertIn(styl, Zrodla.STYLE, "%s: nieznany styl %s" % (uid, styl))
            self.assertIn(styl, Zrodla.CHOREO, "%s: styl %s nie ma funkcji Choreo.%s" % (uid, styl, styl))
            sam = S.UMIEJETNOSCI[uid]["cel"] == "sam"
            self.assertEqual(styl == "na_siebie", sam, "%s: cel %s, a styl %s" % (uid, S.UMIEJETNOSCI[uid]["cel"], styl))
            if styl == "pocisk":
                self.assertIn(w.get("pocisk"), Zrodla.POCISKI, "%s: brak Pocisk.%s" % (uid, w.get("pocisk")))
            for pole in ("wybuch", "aura"):
                if w.get(pole):
                    self.assertIn(w[pole], Zrodla.WYBUCHY, "%s: brak Wybuch.%s" % (uid, w[pole]))
            # każda umiejętność ma też klip u aktora (tabela etapu 1) albo jawny ruch proceduralny
            for wpis in A.AKTORZY:
                if uid in wpis["umiejetnosci"]:
                    self.assertTrue(wpis["umiejetnosci"][uid], "%s: aktor %s bez klipu" % (uid, wpis["klucz"]))

    def test_style_maja_choreografie(self):
        for styl in Zrodla.STYLE:
            self.assertIn(styl, Zrodla.CHOREO, "styl %s bez Choreo.%s" % (styl, styl))
        for klucz, w in Zrodla.ATAK.items():
            self.assertIn(w.get("styl"), Zrodla.CHOREO)
            if w.get("pocisk"):
                self.assertIn(w["pocisk"], Zrodla.POCISKI)

    def test_efekty_maja_wyglad_i_ikone(self):
        self.assertEqual(set(S.EFEKTY), set(Zrodla.EFEKTY), "efekty w danych i w Choreografie.EFEKTY różnią się")
        for eid, w in Zrodla.EFEKTY.items():
            self.assertIn(w.get("wyglad"), Zrodla.WYGLADY, "%s: brak Wyglad.%s" % (eid, w.get("wyglad")))
            self.assertIn(w.get("ikona"), Zrodla.IKONY, "%s: brak ikony %s w InterfejsWalki2" % (eid, w.get("ikona")))

    def test_napis_efektu_jak_w_dzienniku(self):
        # napis przy nałożeniu = nazwa efektu z danych silnika (np. „SPOWOLNIENIE!”, a nie „OGŁUSZENIE!” przy lodowym pocisku)
        for eid, w in Zrodla.EFEKTY.items():
            self.assertEqual(w.get("napis"), S.EFEKTY[eid]["nazwa"].upper() + "!", "%s: napis niezgodny z nazwą w danych" % eid)

    def test_wyglad_spowolnienia_od_umiejetnosci(self):
        # każda umiejętność, która nakłada spowolnienie, ma własny wygląd (lód, pnącza, gwiazdki) — i tylko takie
        nakladaja = {uid for uid, u in S.UMIEJETNOSCI.items() if any(e["efekt"] == "spowolnienie" for e in u["efekty"])}
        self.assertTrue(nakladaja)
        self.assertEqual(set(Zrodla.WYGLAD_SPOWOLNIENIA), nakladaja, "Choreografie.WYGLAD_SPOWOLNIENIA ≠ umiejętności ze spowolnieniem")
        for uid, wyglad in Zrodla.WYGLAD_SPOWOLNIENIA.items():
            self.assertIn(wyglad, Zrodla.WYGLADY, "%s: brak Wyglad.%s" % (uid, wyglad))
        self.assertEqual(Zrodla.WYGLAD_SPOWOLNIENIA["lodowy_pocisk"], "lod")
        self.assertEqual(Zrodla.WYGLAD_SPOWOLNIENIA["uscisk_korzeni"], "pnacza")

    def test_aktorzy_i_portrety(self):
        klucze = {w["klucz"] for w in A.AKTORZY}
        for k in list(S.KLASY) + [p["id"] for p in S.PRZECIWNICY_LISTA]:
            self.assertIn(k, klucze, "brak aktora %s" % k)
            self.assertIn(k, Zrodla.IKONY, "brak portretu %s w InterfejsWalki2" % k)

    def test_wzorcowe_luau_jak_python(self):
        t = Zrodla.wzorcowe_luau
        for nazwa, wart in (("PUNKTY_START", WZ.PUNKTY_START), ("PUNKTY_NA_POZIOM", WZ.PUNKTY_NA_POZIOM),
                            ("BLOK_TARCZY", WZ.BLOK_TARCZY)):
            m = re.search(r"W\.%s\s*=\s*([0-9.]+)" % nazwa, t)
            self.assertIsNotNone(m, nazwa)
            self.assertAlmostEqual(float(m.group(1)), float(wart), msg=nazwa)
        for klasa, rozklad in WZ.ROZKLADY.items():
            m = re.search(r"%s = \{ (sila = .*?) \}" % klasa, t)
            self.assertIsNotNone(m, klasa)
            luau = {k: float(v) for k, v in re.findall(r"([a-z]+) = ([0-9.]+)", m.group(1))}
            self.assertEqual(luau, rozklad, klasa)
        for klasa, um in WZ.UMIEJETNOSCI.items():
            self.assertIn("%s = { %s }" % (klasa, ", ".join('"%s"' % u for u in um)), t)
        self.assertIn("8 + 4 * poziom", t)
        self.assertIn("3 + 1.5 * poziom", t)


class Dzienniki(unittest.TestCase):
    def test_dzienniki_i_odtwarzanie(self):
        widziane_typy, widziane_um = set(), set()
        n, maks_tur, min_tur = 0, 0, 10 ** 9
        for klasa, wrog, poziom, ziarno, w in wszystkie_walki():
            n += 1
            ok, opis = DZ.sprawdz(w)
            self.assertTrue(ok, "%s/%s/%d ziarno %d: %s" % (klasa, wrog, poziom, ziarno, opis))
            for z in w["dziennik"]:
                widziane_typy.add(z["typ"])
                self.assertIn(z["typ"], Zrodla.ZDARZENIA)
                if z["umiejetnosc"]:
                    widziane_um.add(z["umiejetnosc"])
                    self.assertIn(z["umiejetnosc"], Zrodla.UMIEJETNOSCI)
                if z["efekt"]:
                    self.assertIn(z["efekt"], Zrodla.EFEKTY)
            tury, bledy = odtworz(w)
            self.assertFalse(bledy, "%s/%s/%d ziarno %d: %s" % (klasa, wrog, poziom, ziarno, bledy[:3]))
            maks_tur, min_tur = max(maks_tur, w["tury"]), min(min_tur, w["tury"])
        print("\n  dzienników: %d, tury %d–%d, typy zdarzeń: %d/%d, umiejętności: %d/%d"
              % (n, min_tur, maks_tur, len(widziane_typy), len(Zrodla.TYPY), len(widziane_um), len(S.UMIEJETNOSCI)))
        self.assertEqual(widziane_typy, set(Zrodla.TYPY), "nie każdy typ zdarzenia wystąpił w próbie")
        self.assertEqual(widziane_um, set(S.UMIEJETNOSCI), "nie każda umiejętność wystąpiła w próbie")


# --------------------------------------------------------------------------- ziarna pokazowe
def podpis(klasa, wrog, poziom, ziarno, w):
    typy = sorted({z["typ"] for z in w["dziennik"]})
    um = sorted({z["umiejetnosc"] for z in w["dziennik"] if z["umiejetnosc"]})
    trafione = sorted({z["umiejetnosc"] for z in w["dziennik"] if z["umiejetnosc"] and z["typ"] == "umiejetnosc"})
    return {"klasa": klasa, "przeciwnik": wrog, "poziom": poziom, "ziarno": ziarno, "wynik": w["wynik"], "tury": w["tury"],
            "zdarzen": len(w["dziennik"]), "czas": w["czas"], "typy": typy, "umiejetnosci": um, "trafione": trafione,
            "krytyk": any(z["krytyk"] for z in w["dziennik"]), "lup": w["lup"]}


def szukaj_ziaren():
    wszystkie = [podpis(*x[:4], x[4]) for x in wszystkie_walki(ziaren=120)]
    wynik = {}
    # długa (> 20 tur) i najdłuższa; krótka
    dlugie = sorted([p for p in wszystkie if p["tury"] > 20], key=lambda p: -p["tury"])
    wynik["najdluzsza"] = dlugie[0]
    wynik["dluga"] = next(p for p in sorted(dlugie, key=lambda p: p["tury"]) if p["tury"] >= 24 and p["wynik"] == "wygrana")
    wynik["krotka"] = sorted(wszystkie, key=lambda p: (p["tury"], -len(p["typy"])))[0]
    # dla każdej klasy: walka ze wszystkimi możliwymi rodzajami zdarzeń, możliwie krótka
    wynik["wszystkie_typy"] = {}
    for klasa in WZ.KLASY:
        mozliwe = set(Zrodla.TYPY) - (set() if klasa == "wojownik" else {"blok"})
        kand = [p for p in wszystkie if p["klasa"] == klasa]
        # najwięcej możliwych typów, potem możliwie krótko (ale nie krócej niż 8 tur)
        kand.sort(key=lambda p: (-len(set(p["typy"]) & mozliwe), p["tury"] < 8, p["tury"]))
        wynik["wszystkie_typy"][klasa] = dict(kand[0], brakuje=sorted(mozliwe - set(kand[0]["typy"])))
    # dla każdej umiejętności: walka, w której jest (krótka, wygrana gracza jeśli się da) — do klatek
    wynik["umiejetnosci"] = {}
    for uid in S.UMIEJETNOSCI:
        kand = [p for p in wszystkie if uid in p["trafione"] and 6 <= p["tury"] <= 16]
        kand.sort(key=lambda p: (p["wynik"] != "wygrana", p["tury"]))
        wynik["umiejetnosci"][uid] = kand[0] if kand else None
    # do testu Play: każda klasa z trzema różnymi przeciwnikami, walki średniej długości (6–14 tur), różne poziomy
    wynik["play"] = []
    for i, klasa in enumerate(WZ.KLASY):
        wrogowie = [p["id"] for p in S.PRZECIWNICY_LISTA]
        for j in range(3):
            wrog = wrogowie[(i + j * 2) % len(wrogowie)]
            poziom = POZIOMY[(i + j) % 3]
            kand = [p for p in wszystkie if p["klasa"] == klasa and p["przeciwnik"] == wrog and p["poziom"] == poziom
                    and 6 <= p["tury"] <= 14]
            kand.sort(key=lambda p: (-len(p["typy"]), p["tury"]))
            wynik["play"].append(kand[0])
    # wygrana ze strażnikiem z Shardem Ewolucji (panel łupu)
    shard = [p for p in wszystkie if p["lup"]["shard_ewolucji"] > 0]
    wynik["shard"] = sorted(shard, key=lambda p: p["tury"])[0] if shard else None
    gem = [p for p in wszystkie if p["lup"]["gemy"] > 0 and p["lup"]["shard_ewolucji"] == 0]
    wynik["gem"] = sorted(gem, key=lambda p: p["tury"])[0] if gem else None
    return wynik


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--ziarna" in sys.argv:
        w = szukaj_ziaren()
        with open(os.path.join(TU, "ziarna.json"), "w", encoding="utf-8") as f:
            json.dump(w, f, ensure_ascii=False, indent=1)
        for k in ("najdluzsza", "dluga", "krotka", "shard", "gem"):
            p = w[k]
            print("%-11s %s/%s/%d ziarno %d: %s, %d tur, %d zdarzeń, %.1f s" % (k, p["klasa"], p["przeciwnik"], p["poziom"],
                                                                            p["ziarno"], p["wynik"], p["tury"], p["zdarzen"], p["czas"]))
        for k, p in w["wszystkie_typy"].items():
            print("wszystkie typy %-9s %s/%d ziarno %d: %d tur, typów %d, brakuje: %s"
                  % (k, p["przeciwnik"], p["poziom"], p["ziarno"], p["tury"], len(p["typy"]), p["brakuje"] or "—"))
        for k, p in w["umiejetnosci"].items():
            print("umiejętność %-22s %s/%s/%d ziarno %d (%d tur)" % (k, p["klasa"], p["przeciwnik"], p["poziom"], p["ziarno"], p["tury"]))
        print("zapisane: swiat/test_walki2/testy/ziarna.json")
    else:
        unittest.main(verbosity=2)
