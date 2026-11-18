#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testy odtwarzacza walki (dziennik v3) BEZ Studio (unittest) + wyszukiwanie ziaren pokazowych.

    python -B swiat/test_walki2/testy/test_odtwarzacza.py            # testy (ok. 1–2 min, jeden proces)
    python -B swiat/test_walki2/testy/test_odtwarzacza.py --ziarna   # policz ziarna pokazowe → testy/ziarna.json

Co sprawdza:
  1. POKRYCIE (nowa umiejętność, efekt, typ zdarzenia, POLE dziennika albo modyfikator silnika nie zostanie po cichu
     bez obsługi — test się nie uda):
     • typy zdarzeń: Dziennik.TYPY (src/shared/Walka/Dziennik.luau) = PlanWalki.TYPY = klucze Choreografie.ZDARZENIA,
       każda obsługa (i obsługa zdarzenia nieznanego) jest funkcją Obsluga.<nazwa> w OdtwarzaczWalki2.luau;
     • POLA: zbiór pól każdego zdarzenia, walki, strony i łupu w dziennikach z portu silnika = listy znane odtwarzaczowi
       (PlanWalki.POLA_ZDARZENIA / POLA_WALKI / POLA_STRONY / POLA_LUPU);
     • umiejętności (styl, pocisk, wybuch, klip aktora), efekty (wygląd, ikona, napis = nazwa z danych, znaczek stosów
       dla efektów w stosach i procentu dla tarcz procentowych), wygląd ogłuszenia i spowolnienia zależny od
       umiejętności (każda, która je nakłada, ma wpis), utrata tury tylko przy efektach typu „ogluszenie”;
     • etykiety premii (Choreografie.MODYFIKATORY) dla każdego modyfikatora z danych; zapowiedź każdej pasywki ze slotu
       i z broni (PlanWalki.opisPasywki wykonany interpreterem) bez braków;
     • aktorzy i portrety; ikony v3; funkcje efektów v3 (parada, wskrzeszenie); melodia wskrzeszenia.
  2. DZIENNIKI z portu Pythona (tools/walka/silnik.py — ten sam silnik co serwer): postacie wzorcowe (3 klasy × 5
     przeciwników × poziomy 1/5/10 × 60 ziaren) i zestawy z tablicy prototypu (pod manę, pasywki, wskrzeszenie;
     przeciwnicy lasu i lustro). Każdy dziennik: Dziennik.sprawdz; PRAWDZIWY kod zrodla/PlanWalki.luau wykonany
     interpreterem tools/walka/luau_mini.py: normalizacja bez ostrzeżeń, tury = walka.tury, mana na paskach = dziennik
     (użycie = spadek dokładnie o koszt), próg = koszt następnego użycia z dziennika, powalenie tylko przed
     wskrzeszeniem, cios kończący, LICZNIKI TUR I STOSY ikon na początku każdej tury = stan efektów silnika; ten sam
     wynik z niezależnego portu w Pythonie (odtworz); wystąpiło 10/10 typów i każda umiejętność.
  3. Odporność: dziennik z nieznanym typem zdarzenia, nieznanym polem i brakującym polem — PlanWalki ostrzega
     i daje dziennik do odtworzenia (nie wywraca się).
  4. Pamięć pomijania (D-078): PRAWDZIWY kod zrodla/PamiecWalk.luau w interpreterze — pierwsza walka bez zgody, druga
     ze zgodą, pominięcie bez zgody odrzucone, gatunek poznany po końcu walki albo po następnej walce, źródła wspólne.
  5. Wzorcowe.luau (serwer) = tools/walka/wzorcowe.py; zestawy W.zestaw / W.lustro = swiat/test_walki2/zestawy.py
     (wykonane interpreterem) i każdy przechodzi ścisłą walidację wejścia silnika (S.symuluj).
  6. Składnia wszystkich zrodla/*.luau: bilans bloków i nawiasów, strażnik Studio, parser luau_mini (bez rzutowań `::`).
"""
import json
import os
import re
import sys
import unittest
from functools import cmp_to_key

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (os.path.join(REPO, "tools", "walka"), os.path.join(REPO, "swiat", "las_potwory"), KATALOG):
    if _s not in sys.path:
        sys.path.insert(0, _s)
import silnik as S  # noqa: E402
import dziennik as DZ  # noqa: E402
import wzorcowe as WZ  # noqa: E402
import aktorzy as A  # noqa: E402
import zestawy as ZE  # noqa: E402
import luau_mini as LM  # noqa: E402
import sprawdz_luau as SL  # noqa: E402

ZRODLA = os.path.join(KATALOG, "zrodla")
POZIOMY = (1, 5, 10)
ZIARNA_NA_PARE = 60
ZIARNA_ZESTAWOW = 12


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


# --------------------------------------------------------------------------- interpreter Luau (prawdziwy kod modułów)
def bez_rzutowan(tekst):
    """Usuwa rzutowania `:: typ` (luau_mini ich nie zna) — typ z nawiasami (), {} i ? też; reszta kodu bez zmian."""
    wynik, i, n = [], 0, len(tekst)
    while i < n:
        if tekst.startswith("::", i):
            j = i + 2
            while j < n and tekst[j] in " \t":
                j += 1
            glebokosc = 0
            while j < n:
                c = tekst[j]
                if c in "({[":
                    glebokosc += 1
                elif c in ")}]":
                    if glebokosc == 0:
                        break
                    glebokosc -= 1
                elif glebokosc == 0 and not (c.isalnum() or c in "_.?<>"):
                    if c == "-" and tekst.startswith("->", j):
                        j += 2
                        continue
                    break
                j += 1
            i = j
            continue
        wynik.append(tekst[i])
        i += 1
    return "".join(wynik)


def interpreter():
    """luau_mini z atrapą `game` (strażnik Studio przepuszcza) i kilkoma funkcjami biblioteki, których moduły serwera
    używają, a podzbiór nie ma (table.clone, table.sort, string.upper) — zachowanie jak w Luau."""
    I = LM.Interpreter()
    g, rs = LM.Tabela(), LM.Tabela()
    rs.set("IsStudio", lambda self: True)
    g.set("GetService", lambda self, nazwa: rs)
    I.globalne.z["game"] = g
    t = I.globalne.z["table"]

    def tclone(tab):
        k = LM.Tabela()
        k.d = dict(tab.d)
        return k

    def tsort(tab, cmp=None):
        n = int(tab.dlugosc())
        el = [tab.d[float(i)] for i in range(1, n + 1)]
        if cmp is None:
            el.sort()
        else:
            el.sort(key=cmp_to_key(lambda a, b: -1 if LM.prawda(I.wywolaj(cmp, [a, b])[0]) else
                                   (1 if LM.prawda(I.wywolaj(cmp, [b, a])[0]) else 0)))
        for i, v in enumerate(el):
            tab.d[float(i + 1)] = v

    t.set("clone", tclone)
    t.set("sort", tsort)
    I.globalne.z["string"].set("upper", lambda s: s.upper())
    return I


def modul(I, nazwa):
    I.laduj(nazwa, bez_rzutowan(czytaj(os.path.join(ZRODLA, nazwa + ".luau"))))
    return I.wymagaj(nazwa)


def wolaj(I, tabela, nazwa, *argi):
    return I.wywolaj(tabela.get(nazwa), list(argi))


class Zrodla:
    ch = czytaj(os.path.join(ZRODLA, "Choreografie.luau"))
    odtw = czytaj(os.path.join(ZRODLA, "OdtwarzaczWalki2.luau"))
    efekty = czytaj(os.path.join(ZRODLA, "Efekty3D.luau"))
    ui = czytaj(os.path.join(ZRODLA, "InterfejsWalki2.luau"))
    ustawienia = czytaj(os.path.join(ZRODLA, "Ustawienia.luau"))
    dziennik = czytaj(os.path.join(REPO, "src", "shared", "Walka", "Dziennik.luau"))
    wzorcowe_luau = czytaj(os.path.join(ZRODLA, "Wzorcowe.luau"))
    ZDARZENIA = wpisy(blok_tabeli(ch, "ZDARZENIA"))
    UMIEJETNOSCI = wpisy(blok_tabeli(ch, "UMIEJETNOSCI"))
    EFEKTY = wpisy(blok_tabeli(ch, "EFEKTY"))
    ATAK = wpisy(blok_tabeli(ch, "ATAK"))
    STYLE = re.findall(r'"([a-z_]+)"', blok_tabeli(ch, "STYLE"))
    NIEZNANE = re.search(r'Ch\.NIEZNANE\s*=\s*"([a-z_]+)"', ch).group(1)
    OBSLUGA = funkcje(odtw, "Obsluga")
    CHOREO = funkcje(odtw, "Choreo")
    POCISKI = funkcje(efekty, "Pocisk")
    WYBUCHY = funkcje(efekty, "Wybuch")
    WYGLADY = funkcje(efekty, "Wyglad")
    IKONY = set(re.findall(r"^\t([a-z_]+) = \{\n\t\tpaleta", ui, re.M))
    TYPY = re.findall(r'"([a-z_]+)"', re.search(r"Dziennik\.TYPY\s*=\s*\{(.*?)\}", dziennik, re.S).group(1))


# dane odtwarzacza wykonane interpreterem (Choreografie: tabele wyglądu, etykiety premii)
_I = interpreter()
CH = LM.z_luau(modul(_I, "Choreografie"))
PLAN = modul(_I, "PlanWalki")
PLAN_PY = LM.z_luau(PLAN)

# sterownik: ta sama księgowość co Sesja w OdtwarzaczWalki2 (nowa tura → koniecTury poprzedniej strony, potem
# nałożenie / tyknięcie / koniec), z migawką stanu efektów (surowe tury i stosy) na początku każdej tury
STEROWNIK = r'''
local P = wymagaj("PlanWalki")
return function(walka, efekty)
	local w, ostrz = P.normalizuj(walka)
	if not w then
		return { blad = ostrz }
	end
	local plan = P.plan(w)
	local stan = P.nowyStan()
	local migawki = {}
	local bledy = {}
	local turaStrona, turaNr = nil, 0
	local function kopia(strona)
		local l = {}
		for _, e in stan[strona] do
			table.insert(l, { id = e.id, tury = e.tury, stosy = e.stosy, procent = e.procent or -1 })
		end
		return l
	end
	for i = 1, #w.dziennik do
		local z = w.dziennik[i]
		local e = plan.zdarzenia[i]
		if e.nowaTura then
			if turaStrona then
				P.koniecTury(stan, turaStrona, turaNr)
			end
			turaStrona, turaNr = e.stronaTury, e.tura
			table.insert(migawki, { nr = i, gracz = kopia("gracz"), wrog = kopia("wrog") })
		end
		if z.typ == "efekt_nalozony" then
			P.nalozony(stan, z, e.tura, efekty)
		elseif z.typ == "efekt_tick" then
			P.tykniecie(stan, z)
		elseif z.typ == "efekt_koniec" then
			if not P.koniec(stan, z) then
				table.insert(bledy, "zd. " .. i .. ": koniec efektu, którego odtwarzacz nie zna")
			end
		end
	end
	return { ostrzezenia = ostrz, plan = plan, migawki = migawki, bledy = bledy, ikony = { gracz = P.lista(stan, "gracz"), wrog = P.lista(stan, "wrog") } }
end
'''
_I.laduj("Sterownik", STEROWNIK)
STER = _I.wymagaj("Sterownik")
EFEKTY_LUAU = LM.do_luau({k: {"typ": v["typ"]} for k, v in S.EFEKTY.items()})


def plan_luau(walka):
    return LM.z_luau(_I.wywolaj(STER, [LM.do_luau(walka), EFEKTY_LUAU])[0], pusta_jako_lista=True)


# --------------------------------------------------------------------------- niezależny port księgowości (Python)
AKCJE_TURY = {"cios", "krytyk", "blok", "unik", "umiejetnosc", "utrata_tury", "efekt_tick"}


def odtworz(walka):
    """Port księgowości odtwarzacza w Pythonie (niezależny od PlanWalki): tury, efekty z licznikami i stosami, paski
    życia (z wskrzeszeniem — pasek wraca z 0) i many. Zwraca (tury, błędy)."""
    bledy = []
    tura, strona_tury = 0, None
    efekty = {"gracz": [], "wrog": []}
    paski = {"gracz": walka["strony"]["gracz"]["zycie"], "wrog": walka["strony"]["wrog"]["zycie"]}
    mana = {"gracz": walka["strony"]["gracz"]["mana"], "wrog": walka["strony"]["wrog"]["mana"]}
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
            efekty[z["cel"]].append({"id": z["efekt"], "tury": z["tury"], "od": tura, "stosy": max(1, z["stosy"])})
        elif z["typ"] == "efekt_tick":
            for e in efekty[z["cel"]]:
                if e["id"] == z["efekt"]:
                    e["stosy"] = z["stosy"]
        elif z["typ"] == "efekt_koniec":
            e = next((e for e in efekty[z["cel"]] if e["id"] == z["efekt"]), None)
            if e is None:
                bledy.append("zd. %d: koniec efektu, którego odtwarzacz nie zna (%s)" % (i, z["efekt"]))
            else:
                po = e["tury"] - (0 if e["od"] == tura else 1)
                if z["cel"] == strona_tury and po > 0:
                    bledy.append("zd. %d: efekt %s kończy się, a licznik pokazuje jeszcze %d" % (i, z["efekt"], po))
                efekty[z["cel"]].remove(e)
        if z["pochloniete"] > 0 and not any(S.EFEKTY.get(e["id"], {}).get("typ") == "oslona" for e in efekty[z["cel"]]):
            bledy.append("zd. %d: „TARCZA −n” bez tarczy procentowej na celu" % i)
        if z["typ"] == "wskrzeszenie":
            if paski[z["kto"]] != 0:
                bledy.append("zd. %d: wskrzeszenie, a pasek nie stoi na 0" % i)
            paski[z["kto"]] = z["wartosc"]           # pasek życia wraca z 0 do życia po powrocie
        else:
            paski[z["cel"]] = max(0, paski[z["cel"]] - z["obrazenia"])
        if paski["gracz"] != z["hp_gracz"] or paski["wrog"] != z["hp_wrog"]:
            bledy.append("zd. %d: paski %s ≠ dziennik %s" % (i, paski, (z["hp_gracz"], z["hp_wrog"])))
        uzycie = z["umiejetnosc"] != "" and z["typ"] in ("umiejetnosc", "unik", "blok")
        if uzycie and z["mana_" + z["kto"]] != mana[z["kto"]] - z["wartosc"]:
            bledy.append("zd. %d: użycie umiejętności, a mana nie spadła o koszt" % i)
        mana = {"gracz": z["mana_gracz"], "wrog": z["mana_wrog"]}
    if tura != walka["tury"]:
        bledy.append("tury odtwarzacza %d ≠ silnik %d" % (tura, walka["tury"]))
    return tura, bledy


# --------------------------------------------------------------------------- dzienniki z silnika (+ stan efektów)
def walka_ze_stanem(gracz, wrog, ziarno):
    """Walka z portu + migawka stanu efektów silnika przy tworzeniu każdego zdarzenia (przed jego skutkiem)."""
    migawki = []
    oryginal = S.zdarzenie

    def zdarzenie(w, typ, kto, cel, trwa, pola):
        migawki.append({s: [(e["id"], e["trwa"], e["stosy"]) for e in w["stan"][s]["efekty"]] for s in ("gracz", "wrog")})
        return oryginal(w, typ, kto, cel, trwa, pola)
    S.zdarzenie = zdarzenie
    try:
        w = S.symuluj(gracz, wrog, ziarno)
    finally:
        S.zdarzenie = oryginal
    return w, migawki


def wszystkie_walki(ziaren=ZIARNA_NA_PARE, start=1, ze_stanem=False):
    """(opis, walka[, migawki]) — postacie wzorcowe z każdym potworem, potem zestawy tablicy prototypu."""
    def jedna(opis, gracz, wrog, ziarno):
        if ze_stanem:
            w, m = walka_ze_stanem(gracz, wrog, ziarno)
            return opis, w, m
        return opis, S.symuluj(gracz, wrog, ziarno), None
    for klasa in WZ.KLASY:
        for wrog in [p["id"] for p in S.PRZECIWNICY_LISTA]:
            for poziom in POZIOMY:
                for z in range(start, start + ziaren):
                    ziarno = z * 7919 + poziom * 31 + len(wrog)
                    yield jedna({"klasa": klasa, "przeciwnik": wrog, "poziom": poziom, "ziarno": ziarno, "zestaw": "wzorcowa"},
                                WZ.postac(klasa, poziom), {"potwor": wrog, "poziom": poziom}, ziarno)
    for zestaw in ZE.ZESTAWY[1:]:
        for klasa in WZ.KLASY:
            for wrog in [p["id"] for p in S.PRZECIWNICY_LISTA] + [ZE.LUSTRO]:
                for poziom in POZIOMY:
                    for z in range(start, start + max(1, ziaren // 5)):
                        ziarno = z * 104729 + poziom * 17 + len(wrog) + len(zestaw)
                        yield jedna({"klasa": klasa, "przeciwnik": wrog, "poziom": poziom, "ziarno": ziarno, "zestaw": zestaw},
                                    ZE.postac(zestaw, klasa, poziom), ZE.przeciwnik(zestaw, klasa, wrog, poziom), ziarno)


def opis_walki(o):
    return "%s/%s/%d/%s ziarno %d" % (o["klasa"], o["przeciwnik"], o["poziom"], o["zestaw"], o["ziarno"])


# --------------------------------------------------------------------------- testy: pokrycie
class Pokrycie(unittest.TestCase):
    def test_typy_zdarzen_maja_obsluge(self):
        self.assertTrue(Zrodla.TYPY, "nie wczytałem Dziennik.TYPY")
        self.assertEqual(list(PLAN_PY["TYPY"]), list(Zrodla.TYPY), "PlanWalki.TYPY ≠ Dziennik.TYPY")
        for typ in Zrodla.TYPY:
            self.assertIn(typ, Zrodla.ZDARZENIA, "typ zdarzenia %s bez wpisu w Choreografie.ZDARZENIA" % typ)
            self.assertIn(Zrodla.ZDARZENIA[typ], Zrodla.OBSLUGA, "brak funkcji Obsluga.%s w odtwarzaczu" % Zrodla.ZDARZENIA[typ])
        for typ in Zrodla.ZDARZENIA:
            self.assertIn(typ, Zrodla.TYPY, "Choreografie.ZDARZENIA ma typ spoza dziennika: %s" % typ)
        self.assertIn(Zrodla.NIEZNANE, Zrodla.OBSLUGA, "brak Obsluga.%s (zdarzenie nieznane)" % Zrodla.NIEZNANE)
        self.assertIn("wskrzeszenie", Zrodla.TYPY)

    def test_pola_dziennika_znane_odtwarzaczowi(self):
        # nowe pole silnika (w zdarzeniu, walce, stronie albo łupie) = błąd testu, dopóki odtwarzacz go nie zna
        pola_z, pola_w, pola_s, pola_l = set(), set(), set(), set()
        for _, w, _ in wszystkie_walki(ziaren=3):
            pola_w |= set(w)
            pola_l |= set(w["lup"])
            for s in w["strony"].values():
                pola_s |= set(s)
            for z in w["dziennik"]:
                pola_z |= set(z)
                self.assertEqual(set(z), set(PLAN_PY["POLA_ZDARZENIA"]), "zdarzenie z innym zbiorem pól: %s" % sorted(set(z) ^ set(PLAN_PY["POLA_ZDARZENIA"])))
        self.assertEqual(pola_z, set(PLAN_PY["POLA_ZDARZENIA"]), "pola zdarzeń: %s" % sorted(pola_z ^ set(PLAN_PY["POLA_ZDARZENIA"])))
        self.assertEqual(pola_w, set(PLAN_PY["POLA_WALKI"]), "pola walki: %s" % sorted(pola_w ^ set(PLAN_PY["POLA_WALKI"])))
        self.assertEqual(pola_s, set(PLAN_PY["POLA_STRONY"]), "pola strony: %s" % sorted(pola_s ^ set(PLAN_PY["POLA_STRONY"])))
        self.assertEqual(pola_l, set(PLAN_PY["POLA_LUPU"]), "pola łupu: %s" % sorted(pola_l ^ set(PLAN_PY["POLA_LUPU"])))
        # Dziennik.luau opisuje te same pola zdarzenia, które zna odtwarzacz
        for pole in PLAN_PY["POLA_ZDARZENIA"]:
            self.assertRegex(Zrodla.dziennik, r"\b%s\b" % re.escape(pole), "pole %s nie występuje w Dziennik.luau" % pole)

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

    def test_efekty_maja_wyglad_ikone_i_znaczek(self):
        self.assertEqual(set(S.EFEKTY), set(Zrodla.EFEKTY), "efekty w danych i w Choreografie.EFEKTY różnią się: %s"
                         % sorted(set(S.EFEKTY) ^ set(Zrodla.EFEKTY)))
        for eid, w in Zrodla.EFEKTY.items():
            self.assertIn(w.get("wyglad"), Zrodla.WYGLADY, "%s: brak Wyglad.%s" % (eid, w.get("wyglad")))
            self.assertIn(w.get("ikona"), Zrodla.IKONY, "%s: brak ikony %s w InterfejsWalki2" % (eid, w.get("ikona")))
            d = S.EFEKTY[eid]
            # efekt w stosach (trucizna: limit > 1 albo modyfikator stosów) pokazuje „×N”; tarcza procentowa — „−N%”
            w_stosach = d["stosy_maks"] > 1 or d["mod_stosow"] != ""
            self.assertEqual(w.get("znaczek") == "stosy", w_stosach, "%s: znaczek stosów" % eid)
            self.assertEqual(w.get("znaczek") == "procent", d["typ"] == "oslona", "%s: znaczek procentu tarczy" % eid)
        # ogłuszenie i spowolnienie to różne statusy: inny wygląd i inna ikona
        self.assertNotEqual(Zrodla.EFEKTY["ogluszenie"]["ikona"], Zrodla.EFEKTY["spowolnienie"]["ikona"])
        self.assertNotEqual(Zrodla.EFEKTY["ogluszenie"]["wyglad"], Zrodla.EFEKTY["spowolnienie"]["wyglad"])

    def test_napis_efektu_jak_w_dzienniku(self):
        for eid, w in Zrodla.EFEKTY.items():
            self.assertEqual(w.get("napis"), S.EFEKTY[eid]["nazwa"].upper() + "!", "%s: napis niezgodny z nazwą w danych" % eid)

    def test_wyglad_statusow_od_umiejetnosci(self):
        # każda umiejętność, która nakłada ogłuszenie albo spowolnienie, ma własny wygląd — i tylko takie
        wg = CH["WYGLAD_OD_UMIEJETNOSCI"]
        for efekt in ("ogluszenie", "spowolnienie"):
            nakladaja = {uid for uid, u in S.UMIEJETNOSCI.items() if any(e["efekt"] == efekt for e in u["efekty"])}
            self.assertTrue(nakladaja, efekt)
            self.assertEqual(set(wg.get(efekt, {})), nakladaja, "WYGLAD_OD_UMIEJETNOSCI.%s ≠ umiejętności z tym efektem" % efekt)
            for uid, wyglad in wg[efekt].items():
                self.assertIn(wyglad, Zrodla.WYGLADY, "%s/%s: brak Wyglad.%s" % (efekt, uid, wyglad))
        self.assertEqual(set(wg), {"ogluszenie", "spowolnienie"})
        self.assertEqual(wg["spowolnienie"]["lodowy_pocisk"], "lod")
        self.assertEqual(wg["ogluszenie"]["uscisk_korzeni"], "pnacza")
        self.assertEqual(wg["ogluszenie"]["ogluszajace_uderzenie"], "gwiazdki")
        # utrata tury: puls ozdoby tylko przy efektach, które zabierają turę (typ „ogluszenie” w danych)
        self.assertEqual(set(CH["TRACI_TURE"]), {k for k, v in S.EFEKTY.items() if v["typ"] == "ogluszenie"})

    # ----------------------------------------------------------------- własny wygląd umiejętności u aktora (Dżungla)
    def test_wlasny_wyglad_umiejetnosci_aktora_dane(self):
        """Choreografie.UMIEJETNOSCI_AKTORA: tylko aktorzy Dżungli, tylko ich umiejętności z klipem; styl, czas i kamera
        jak we wpisie ogólnym (POLA_CZASU); pocisk, wybuch, aura i ozdoby statusów istnieją w Efekty3D; dźwięki
        wskazują istniejące zdarzenia katalogu (uderzenie = takie, które ma szczyt na trafieniu)."""
        wa = CH["UMIEJETNOSCI_AKTORA"]
        ogolne = CH["UMIEJETNOSCI"]
        pola_czasu = list(CH["POLA_CZASU"])
        self.assertIn("styl", pola_czasu)
        self.assertIn("predkosc", pola_czasu)
        self.assertIn("kamera", pola_czasu)
        dzungla = {w["klucz"] for w in A.AKTORZY_DZUNGLI}
        self.assertEqual(set(wa), dzungla, "własny wygląd mają dokładnie aktorzy Dżungli (las, Bagno, bohaterowie — nie)")
        with open(os.path.join(REPO, "swiat", "dzwiek_gra", "ustawienia.json"), encoding="utf-8") as f:
            zdarzenia_dzwieku = json.load(f)["zdarzenia"]
        wbudowane = set(re.findall(r"^\t([a-z_]+) = \{ id = S \.\.", Zrodla.ustawienia, re.M))
        self.assertIn("plusk", wbudowane)
        znane_pola = set(pola_czasu) | {"pocisk", "wybuch", "aura", "smuga", "fala", "pazury", "pazuryKrzyz", "kly", "wstrzas",
                                        "grot", "nazwa", "wyglady", "dzwiekUderzenia", "dzwiekWypuszczenia", "dzwiekWbudowany",
                                        "kolor", "skalaWybuchu"}
        for klucz, wpisy_aktora in wa.items():
            aktor = A.PO_KLUCZU[klucz]
            for uid, w in wpisy_aktora.items():
                gdzie = "%s/%s" % (klucz, uid)
                self.assertIn(uid, S.UMIEJETNOSCI, gdzie)
                self.assertTrue(aktor["umiejetnosci"].get(uid), "%s: aktor nie ma klipu tej umiejętności" % gdzie)
                self.assertTrue(set(w) <= znane_pola, "%s: nieznane pola %s" % (gdzie, sorted(set(w) - znane_pola)))
                baza = ogolne[uid]
                for pole in pola_czasu:
                    self.assertEqual(w.get(pole), baza.get(pole), "%s: pole czasu / kamery „%s” inne niż we wpisie ogólnym"
                                     % (gdzie, pole))
                styl = w["styl"]
                self.assertIn(styl, Zrodla.CHOREO, gdzie)
                self.assertEqual(styl == "na_siebie", S.UMIEJETNOSCI[uid]["cel"] == "sam", gdzie)
                if styl == "pocisk":
                    self.assertIn(w.get("pocisk"), Zrodla.POCISKI, "%s: brak Pocisk.%s" % (gdzie, w.get("pocisk")))
                    self.assertGreater(w.get("grot", 0), 0, "%s: pocisk bez pola grot" % gdzie)
                for pole in ("wybuch", "aura"):
                    if w.get(pole):
                        self.assertIn(w[pole], Zrodla.WYBUCHY, "%s: brak Wybuch.%s" % (gdzie, w[pole]))
                # wygląd naprawdę własny: inny pocisk / wybuch / aura / ślad niż we wpisie ogólnym
                wyglad = {p: w.get(p) for p in ("pocisk", "wybuch", "aura", "smuga", "pazury", "kly", "pazuryKrzyz", "fala")}
                self.assertNotEqual(wyglad, {p: baza.get(p) for p in wyglad}, "%s: wygląd taki sam jak pożyczony" % gdzie)
                naklada = {e["efekt"] for e in S.UMIEJETNOSCI[uid]["efekty"]}
                for efekt, wygl in (w.get("wyglady") or {}).items():
                    self.assertIn(efekt, naklada, "%s: ozdoba efektu %s, którego ta umiejętność nie nakłada" % (gdzie, efekt))
                    self.assertIn(wygl, Zrodla.WYGLADY, "%s: brak Wyglad.%s" % (gdzie, wygl))
                    self.assertNotEqual(wygl, CH["EFEKTY"][efekt]["wyglad"], gdzie)
                if "nazwa" in w:
                    self.assertTrue(isinstance(w["nazwa"], str) and 3 <= len(w["nazwa"]) <= 24, gdzie)
                du = w.get("dzwiekUderzenia")
                if du is not None and du is not False:
                    self.assertTrue(zdarzenia_dzwieku.get(du, {}).get("uderzenie"), "%s: zdarzenie „%s” nie jest uderzeniem "
                                    "w swiat/dzwiek_gra/ustawienia.json" % (gdzie, du))
                if w.get("dzwiekWypuszczenia"):
                    self.assertIn(w["dzwiekWypuszczenia"], zdarzenia_dzwieku, gdzie)
                if w.get("dzwiekWbudowany"):
                    self.assertIn(w["dzwiekWbudowany"], wbudowane, gdzie)
        # nowe funkcje efektów i miejsca podpięcia w odtwarzaczu
        for f in ("ukaszenie", "pyl", "licznik", "opisKosztu", "zmierz"):
            self.assertRegex(Zrodla.efekty, r"function Efekty:%s\(" % f, "brak fx:%s w Efekty3D" % f)
        for kawalek in ("Ch.UMIEJETNOSCI_AKTORA[klucz]", "Ch.UMIEJETNOSCI_AKTORA[aktor]", "c.pazuryKrzyz == true",
                        "self.fx:ukaszenie(", "c.grot or (", "ev.choreo.dzwiekUderzenia ~= nil", "c.dzwiekWypuszczenia",
                        "c.dzwiekWbudowany", "ev.choreo.nazwa", '"OstatniKosztEfektow"', "efekty3D = s.fx and s.fx:licznik()"):
            self.assertIn(kawalek, Zrodla.odtw, "odtwarzacz nie używa: %s" % kawalek)
        # nowe efekty nie świecą światłem i nie zostawiają niczego poza folderem sceny (sprzątanie przez fx:wyczysc)
        nowe = Zrodla.efekty.split("-- Dżungla (18.11.2026) — rozbłyski", 1)[1].split("function Efekty:wybuch(", 1)[0] \
            + Zrodla.efekty.split("-- Dżungla — usypiający pyłek", 1)[1].split("function Efekty:pocisk(", 1)[0] \
            + Zrodla.efekty.split("Dżungla (18.11.2026): ozdoby własnych efektów", 1)[1].split("function Efekty:wyglad(", 1)[0] \
            + Zrodla.efekty.split("--[[ Ukąszenie (Dżungla", 1)[1].split("-- wybuchy (rozbłysk przy trafieniu)", 1)[0]
        for zakazane in ("PointLight", "Instance.new", "Debris", "task.delay", "task.spawn", "workspace:", "rbxassetid", "SoundId",
                         "Texture ="):
            self.assertNotIn(zakazane, nowe, "nowe efekty Dżungli: %s" % zakazane)

    @staticmethod
    def _funkcja_odtwarzacza(naglowek):
        """Tekst funkcji najwyższego poziomu z OdtwarzaczWalki2.luau (od nagłówka do `end` w pierwszej kolumnie)."""
        tekst = Zrodla.odtw.replace("\r\n", "\n")
        i = tekst.index(naglowek)
        return tekst[i:tekst.index("\nend\n", i) + 5]

    def test_wlasny_wyglad_umiejetnosci_aktora_kod(self):
        """PRAWDZIWY kod Sesja:wpisChoreo i Sesja.wygladEfektu z odtwarzacza wykonany interpreterem: aktor Dżungli dostaje
        własny wpis, a KAŻDY inny aktor (bohaterowie, las, Bagno) dokładnie wpis ogólny i dawną ozdobę statusu."""
        kod = ('local Ch = wymagaj("Choreografie")\nlocal Dane = { umiejetnosci = {} }\nlocal Sesja = {}\n'
               + bez_rzutowan(self._funkcja_odtwarzacza("function Sesja:wpisChoreo(")) + "\n"
               + bez_rzutowan(self._funkcja_odtwarzacza("function Sesja.wygladEfektu(")) + "\nreturn Sesja\n")
        _I.laduj("WycinekOdtwarzacza", kod)
        sesja = _I.wymagaj("WycinekOdtwarzacza")

        def wpis(uid, klucz):
            ja = LM.do_luau({"brakiChoreo": 0})
            w = _I.wywolaj(sesja.get("wpisChoreo"), [ja, LM.do_luau({"umiejetnosc": uid, "rodzaj": "fizyczne"}), klucz])
            self.assertTrue(LM.prawda(w[1]), "%s/%s: wpis zastępczy" % (klucz, uid))
            return LM.z_luau(w[0])

        def wyglad(efekt, uid, klucz):
            return _I.wywolaj(sesja.get("wygladEfektu"), [efekt, uid, klucz])[0]

        wa, ogolne = CH["UMIEJETNOSCI_AKTORA"], CH["UMIEJETNOSCI"]
        sprawdzone = 0
        for aktor in A.AKTORZY:
            klucz = aktor["klucz"]
            for uid in aktor["umiejetnosci"]:
                if uid not in S.UMIEJETNOSCI:
                    continue
                w = wpis(uid, klucz)
                if klucz in wa and uid in wa[klucz]:
                    self.assertEqual(w, wa[klucz][uid], "%s/%s" % (klucz, uid))
                else:
                    self.assertEqual(w, ogolne[uid], "%s/%s: wpis inny niż ogólny" % (klucz, uid))
                for e in S.UMIEJETNOSCI[uid]["efekty"]:
                    efekt = e["efekt"]
                    dawny = CH["WYGLAD_OD_UMIEJETNOSCI"].get(efekt, {}).get(uid) or CH["EFEKTY"][efekt]["wyglad"]
                    wlasny = (wa.get(klucz, {}).get(uid, {}).get("wyglady") or {}).get(efekt)
                    self.assertEqual(wyglad(efekt, uid, klucz), wlasny or dawny, "%s/%s/%s" % (klucz, uid, efekt))
                    self.assertEqual(wyglad(efekt, uid, None), dawny, "bez aktora: dawna ozdoba (%s/%s)" % (uid, efekt))
                sprawdzone += 1
        self.assertGreaterEqual(sprawdzone, 20)
        # przykłady wprost
        self.assertEqual(wpis("lodowy_pocisk", "gebokwiat")["pocisk"], "pylek")
        self.assertEqual(wpis("lodowy_pocisk", "mag")["pocisk"], "lod")
        self.assertEqual(wpis("zatruta_strzala", "waz_stu_lian")["pocisk"], "jad")
        self.assertEqual(wpis("zatruta_strzala", "zwiadowca")["pocisk"], "strzala")
        self.assertEqual(wyglad("spowolnienie", "lodowy_pocisk", "gebokwiat"), "sen")
        self.assertEqual(wyglad("spowolnienie", "lodowy_pocisk", "mag"), "lod")
        self.assertEqual(wyglad("skupienie", "skupienie", "zwijogon"), "kamuflaz")
        self.assertEqual(wyglad("skupienie", "skupienie", "zwiadowca"), "blask")
        self.assertEqual(wyglad("kamienna_skora", "kamienna_skora", "pancernik_ruin"), "ruiny")
        self.assertEqual(wyglad("kamienna_skora", "kamienna_skora", "wojownik"), "kamienie")
        self.assertEqual(wyglad("trucizna", "zatruta_strzala", "waz_stu_lian"), "babelki")
        self.assertEqual(wyglad("krwawienie", "", "waz_stu_lian"), "krople")

    def test_etykiety_premii_i_zapowiedzi_pasywek(self):
        et = CH["MODYFIKATORY"]
        ids = [m["id"] for m in S.MODYFIKATORY]
        self.assertEqual(list(et["kolejnosc"]), ids, "Choreografie.MODYFIKATORY.kolejnosc ≠ modyfikatory z danych")
        for k in ids:
            self.assertIn(k, et, "brak etykiety modyfikatora %s" % k)
            self.assertIn(et[k]["jednostka"], ("%", "pp", "pkt", "tury", "stosy", "x"), k)
        et_l = LM.do_luau(et)
        dane_l = LM.do_luau({"pasywne": S.PASYWNE, "pasywki_broni": S.PASYWKI_BRONI})
        widziane = 0
        for zrodlo, tabela in (("slot", S.PASYWNE), ("bron", S.PASYWKI_BRONI)):
            for pid, p in tabela.items():
                o = LM.z_luau(wolaj(_I, PLAN, "opisPasywki", dane_l, pid, zrodlo, et_l)[0], pusta_jako_lista=True)
                self.assertEqual(o["braki"], [], "%s: modyfikatory bez etykiety %s" % (pid, o["braki"]))
                self.assertEqual(o["nazwa"], p["nazwa"])
                self.assertTrue(o["linia"], "%s: pusta zapowiedź" % pid)
                if p.get("wskrzeszenie", 0) > 0:
                    self.assertTrue(o["legendarna"])
                    self.assertIn("%d%% życia" % round(p["wskrzeszenie"] * 100), o["linia"])
                widziane += 1
        self.assertEqual(widziane, len(S.PASYWNE) + len(S.PASYWKI_BRONI))
        # przykłady z danych (bez liczb na sztywno w kliencie — tu sprawdzamy tylko format)
        o = LM.z_luau(wolaj(_I, PLAN, "opisPasywki", dane_l, "kolos", "slot", et_l)[0])
        self.assertEqual(o["linia"], "+%d%% życia · +%d%% obrażeń" % (round(S.PASYWNE["kolos"]["modyfikatory"]["zycie"] * 100),
                                                                    round(S.PASYWNE["kolos"]["modyfikatory"]["cios"] * 100)))
        o = LM.z_luau(wolaj(_I, PLAN, "opisPasywki", dane_l, "ognista_rozdzka", "bron", et_l)[0])
        self.assertEqual(o["linia"], "+2 tury podpalenia")

    def test_aktorzy_portrety_ikony_i_efekty_v3(self):
        klucze = {w["klucz"] for w in A.AKTORZY}
        for k in list(S.KLASY) + [p["id"] for p in S.PRZECIWNICY_LISTA]:
            self.assertIn(k, klucze, "brak aktora %s" % k)
            self.assertIn(k, Zrodla.IKONY, "brak portretu %s w InterfejsWalki2" % k)
        for ik in ("sniezynka", "feniks", "mana", "bron", "gwiazda"):
            self.assertIn(ik, Zrodla.IKONY, "brak ikony v3 %s" % ik)
        for m in re.finditer(r"^\t([a-z_]+) = \{\n\t\tpaleta = \{([^}]*)\},\n\t\tmapa = \{([^}]*)\}", Zrodla.ui, re.M):
            paleta = set(re.findall(r"([A-Za-z]) = \"#", m.group(2)))
            wiersze = re.findall(r'"([^"]*)"', m.group(3))
            self.assertEqual(len(wiersze), 8, "ikona %s: 8 wierszy" % m.group(1))
            for w in wiersze:
                self.assertEqual(len(w), 8, "ikona %s: wiersz %r" % (m.group(1), w))
                self.assertTrue(set(w) - {"."} <= paleta, "ikona %s: znak spoza palety w %r" % (m.group(1), w))
        for f in ("parada", "wskrzeszenie"):
            self.assertRegex(Zrodla.efekty, r"function Efekty:%s\(" % f, "brak fx:%s w Efekty3D" % f)
        self.assertRegex(Zrodla.ustawienia, r"wskrzeszenie = \{ nuty = ", "brak melodii wskrzeszenia")
        self.assertIn("powalenie", CH["ZWOLNIENIE"])

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

    def test_zestawy_serwera_jak_python_i_przechodza_walidacje(self):
        I = interpreter()
        W = modul(I, "Wzorcowe")
        for nazwa_py, nazwa_lu in (("KOSZT_MANY", "KOSZT_MANY"), ("BRON_MANY", "BRON_MANY"), ("PASYWKA_MANY", "PASYWKA_MANY"),
                                   ("PREMIE_MANY", "PREMIE_MANY")):
            self.assertEqual(LM.z_luau(W.get(nazwa_lu)), getattr(WZ, nazwa_py), nazwa_lu)
        self.assertEqual(LM.z_luau(W.get("ZESTAWY")), ZE.ZESTAWY)
        self.assertEqual(LM.z_luau(W.get("PASYWKI_ZESTAWU")), ZE.PASYWKI_ZESTAWU)
        self.assertEqual(LM.z_luau(W.get("BRON_ZESTAWU")), ZE.BRON_ZESTAWU)
        self.assertEqual(LM.z_luau(W.get("NAZWY_LUSTRA")), ZE.NAZWY_LUSTRA)
        for zestaw in ZE.ZESTAWY:
            for klasa in WZ.KLASY:
                for poziom in POZIOMY:
                    lu = LM.z_luau(wolaj(I, W, "zestaw", zestaw, klasa, float(poziom))[0], pusta_jako_lista=True)
                    py = json.loads(json.dumps(ZE.postac(zestaw, klasa, poziom)))
                    self.assertEqual(lu, py, "%s/%s/%d: W.zestaw ≠ zestawy.postac" % (zestaw, klasa, poziom))
                    lustro = LM.z_luau(wolaj(I, W, "lustro", zestaw, klasa, float(poziom))[0], pusta_jako_lista=True)
                    self.assertEqual({"postac": lustro}, json.loads(json.dumps(ZE.przeciwnik(zestaw, klasa, ZE.LUSTRO, poziom))))
                    # ścisła walidacja wejścia silnika (nieznane pole = błąd „Walka: …”) — gracz i lustro
                    w = S.symuluj(lu, {"postac": lustro}, 7)
                    self.assertTrue(DZ.sprawdz(w)[0])
                    w = S.symuluj(lu, {"potwor": "lesny_troll", "poziom": poziom}, 7)
                    self.assertTrue(DZ.sprawdz(w)[0])
        self.assertIsNone(LM.z_luau(wolaj(I, W, "zestaw", "nieznany", "mag", 5.0)[0]) or None)
        # zestaw pod manę = build z tools/walka/wzorcowe.py; ze wskrzeszeniem = tabela (k) balansu
        self.assertEqual(ZE.postac("mana", "mag", 10), WZ.build("mana", "mag", 10))
        self.assertEqual(ZE.postac("wskrzeszenie", "zwiadowca", 1)["umiejetnosci"], ["wskrzeszenie"])
        self.assertEqual(ZE.postac("wskrzeszenie", "wojownik", 10)["umiejetnosci"], ["ciecie", "miazdzacy_cios", "wskrzeszenie"])
        # pasywki do zapowiedzi: to, co wysyła serwer (pasywkiOpisu w SerwerWalki2)
        self.assertEqual(ZE.pasywki_strony(ZE.postac("pasywki", "mag", 10)), {"sloty": ["skupiona_magia", "magiczny_pocisk"],
                                                                          "bron": "ognista_rozdzka"})


# --------------------------------------------------------------------------- testy: dzienniki
class Dzienniki(unittest.TestCase):
    def test_dzienniki_i_odtwarzanie(self):
        widziane_typy, widziane_um, widziane_ef = set(), set(), set()
        n, maks_tur, min_tur, wskrz = 0, 0, 10 ** 9, {"gracz": 0, "wrog": 0, "obie": 0}
        porownane_tury, stosy_maks, uzycia = 0, 1, 0
        for opis, w, mig in wszystkie_walki(ze_stanem=True):
            n += 1
            gdzie = opis_walki(opis)
            ok, blad = DZ.sprawdz(w)
            self.assertTrue(ok, "%s: %s" % (gdzie, blad))
            for z in w["dziennik"]:
                widziane_typy.add(z["typ"])
                self.assertIn(z["typ"], Zrodla.ZDARZENIA)
                if z["umiejetnosc"]:
                    widziane_um.add(z["umiejetnosc"])
                    self.assertIn(z["umiejetnosc"], Zrodla.UMIEJETNOSCI)
                if z["efekt"]:
                    widziane_ef.add(z["efekt"])
                    self.assertIn(z["efekt"], Zrodla.EFEKTY)
                stosy_maks = max(stosy_maks, z["stosy"])
            # niezależny port w Pythonie
            tury, bledy = odtworz(w)
            self.assertFalse(bledy, "%s: %s" % (gdzie, bledy[:3]))
            # prawdziwy PlanWalki.luau (interpreter)
            r = plan_luau(w)
            self.assertNotIn("blad", r, gdzie)
            self.assertEqual(r["ostrzezenia"], [], "%s: ostrzeżenia normalizacji %s" % (gdzie, r["ostrzezenia"]))
            self.assertEqual(r["bledy"], [], gdzie)
            pl = r["plan"]
            self.assertEqual(pl["tury"], w["tury"], "%s: tury planu" % gdzie)
            d = w["dziennik"]
            mana = {"gracz": w["strony"]["gracz"]["mana"], "wrog": w["strony"]["wrog"]["mana"]}
            nastepne = {}
            for i in range(len(d) - 1, -1, -1):
                z, e = d[i], pl["zdarzenia"][i]
                for s in ("gracz", "wrog"):
                    self.assertEqual(e["prog"][s], nastepne.get(s, w["strony"][s]["mana_maks"]), "%s zd. %d: próg many %s" % (gdzie, i + 1, s))
                    self.assertEqual(e["gotowa"][s], z["mana_" + s] >= e["prog"][s])
                if z["umiejetnosc"] and z["typ"] in ("umiejetnosc", "unik", "blok"):
                    nastepne[z["kto"]] = z["wartosc"]
            for i, z in enumerate(d):
                e = pl["zdarzenia"][i]
                self.assertEqual(e["manaPrzed"], mana, "%s zd. %d: mana przed" % (gdzie, i + 1))
                self.assertEqual(e["manaPo"], {"gracz": z["mana_gracz"], "wrog": z["mana_wrog"]})
                if e["uzycie"]:
                    uzycia += 1
                    self.assertEqual(e["koszt"], z["wartosc"])
                    self.assertEqual(z["mana_" + z["kto"]], mana[z["kto"]] - e["koszt"], "%s zd. %d: koszt" % (gdzie, i + 1))
                mana = e["manaPo"]
                # powalenie: tylko tuż przed wskrzeszeniem tej strony; wskrzeszenie: pasek z 0
                if e.get("powala"):
                    self.assertEqual(d[i + 1]["typ"], "wskrzeszenie")
                    self.assertEqual(z["hp_" + e["powala"]], 0)
                if z["typ"] == "wskrzeszenie":
                    self.assertEqual(e.get("wstaje"), z["kto"])
                    self.assertEqual(d[i - 1]["hp_" + z["kto"]], 0)
                    self.assertEqual(z["hp_" + z["kto"]], z["wartosc"])
            # cios kończący = ostatnie zdarzenie przy nokaucie (żadne powalenie przed wskrzeszeniem)
            if not w["bezpiecznik"]:
                self.assertEqual(pl["nrKonczacego"], len(d), gdzie)
            ws = {s: any(z["typ"] == "wskrzeszenie" and z["kto"] == s for z in d) for s in ("gracz", "wrog")}
            for s in ("gracz", "wrog"):
                wskrz[s] += ws[s]
            wskrz["obie"] += ws["gracz"] and ws["wrog"]
            # liczniki tur i stosy na ikonach na początku każdej tury = stan efektów silnika
            for m in r["migawki"]:
                silnik_stan = mig[m["nr"] - 1]
                for s in ("gracz", "wrog"):
                    nasze = [(e["id"], e["tury"], e["stosy"]) for e in m[s]]
                    self.assertEqual(nasze, silnik_stan[s], "%s zd. %d (%s): ikony %s ≠ silnik %s" % (gdzie, m["nr"], s, nasze, silnik_stan[s]))
                    for e in m[s]:
                        if S.EFEKTY[e["id"]]["typ"] == "oslona":
                            self.assertGreater(e["procent"], 0)
                porownane_tury += 1
            maks_tur, min_tur = max(maks_tur, w["tury"]), min(min_tur, w["tury"])
        print("\n  dzienników: %d, tury %d–%d, typy zdarzeń: %d/%d, umiejętności: %d/%d, efekty: %d/%d, użyć many: %d,"
              " tur porównanych ze stanem silnika: %d, stosy do %d, wskrzeszenia: gracz %d, przeciwnik %d, obie %d"
              % (n, min_tur, maks_tur, len(widziane_typy), len(Zrodla.TYPY), len(widziane_um), len(S.UMIEJETNOSCI),
                 len(widziane_ef), len(S.EFEKTY), uzycia, porownane_tury, stosy_maks, wskrz["gracz"], wskrz["wrog"], wskrz["obie"]))
        self.assertEqual(widziane_typy, set(Zrodla.TYPY), "nie każdy typ zdarzenia wystąpił w próbie")
        self.assertEqual(widziane_um, set(S.UMIEJETNOSCI), "nie każda umiejętność wystąpiła w próbie")
        self.assertEqual(widziane_ef, set(S.EFEKTY), "nie każdy efekt wystąpił w próbie")
        self.assertGreater(stosy_maks, 1, "w próbie nie było trucizny w stosach")
        self.assertTrue(wskrz["gracz"] and wskrz["wrog"] and wskrz["obie"], "w próbie brak wskrzeszenia gracza, przeciwnika albo obu")

    def test_zrodlo_efektu_po_wskrzeszeniu(self):
        # cios „zabił”, cel wstał, efekt z tego ataku nałożony PO wskrzeszeniu — źródło = umiejętność ataku
        znalezione = 0
        for opis, w, _ in wszystkie_walki(ziaren=12):
            d = w["dziennik"]
            for i in range(2, len(d)):
                if d[i]["typ"] == "efekt_nalozony" and d[i - 1]["typ"] == "wskrzeszenie":
                    pl = plan_luau(w)["plan"]
                    atak = d[i - 2]
                    oczek = atak["umiejetnosc"] if atak["kto"] == d[i]["kto"] else ""
                    self.assertEqual(pl["zdarzenia"][i].get("zrodlo", ""), oczek, opis_walki(opis))
                    znalezione += 1
        print("\n  efektów nałożonych po wskrzeszeniu: %d" % znalezione)


class Odpornosc(unittest.TestCase):
    def test_nieznane_typy_i_pola_nie_wywracaja_odtwarzania(self):
        w = S.symuluj(WZ.postac("mag", 5), {"potwor": "lesny_troll", "poziom": 5}, 4242)
        w = json.loads(json.dumps(w))
        w["nowe_pole_walki"] = 1
        w["strony"]["gracz"]["nowe_pole_strony"] = "x"
        d = w["dziennik"]
        d[1]["nowe_pole"] = 5                                  # nieznane pole zdarzenia
        del d[2]["stosy"]                                      # brakujące pole
        obcy = dict(d[3], typ="teleport")                      # nieznany typ zdarzenia (nowszy silnik)
        d.insert(4, obcy)
        bez_strony = dict(d[5], kto="obserwator")              # zdarzenie bez strony — do pominięcia
        d.insert(6, bez_strony)
        r = plan_luau(w)
        self.assertNotIn("blad", r)
        ostrz = " | ".join(r["ostrzezenia"])
        for fraza in ("nieznane pole walki: nowe_pole_walki", "nieznane pole strony: nowe_pole_strony",
                      "nieznane pole zdarzenia: nowe_pole", "brak pola zdarzenia: stosy", "nieznany typ zdarzenia: teleport",
                      "zdarzenie bez strony"):
            self.assertIn(fraza, ostrz)
        # ostrzeżenia raz na nazwę; dziennik po normalizacji ma wszystkie pola i jedno zdarzenie mniej
        self.assertEqual(len(r["ostrzezenia"]), len(set(r["ostrzezenia"])))
        wn = LM.z_luau(wolaj(_I, PLAN, "normalizuj", LM.do_luau(w))[0], pusta_jako_lista=True)
        self.assertEqual(len(wn["dziennik"]), len(d) - 1)
        self.assertTrue(wn["dziennik"][4]["nieznany"])
        for z in wn["dziennik"]:
            self.assertTrue(set(PLAN_PY["POLA_ZDARZENIA"]) <= set(z))
        # zepsute zdarzenie bez życia i many dostaje wartości z poprzedniego (paski nie skaczą do 0)
        w2 = json.loads(json.dumps(S.symuluj(WZ.postac("wojownik", 1), {"potwor": "lesny_slime", "poziom": 1}, 5)))
        for k in ("hp_gracz", "hp_wrog", "mana_gracz", "mana_wrog", "t"):
            del w2["dziennik"][2][k]
        wn2 = LM.z_luau(wolaj(_I, PLAN, "normalizuj", LM.do_luau(w2))[0], pusta_jako_lista=True)
        self.assertEqual(wn2["dziennik"][2]["hp_gracz"], w2["dziennik"][1]["hp_gracz"])
        self.assertEqual(wn2["dziennik"][2]["mana_wrog"], w2["dziennik"][1]["mana_wrog"])
        self.assertAlmostEqual(wn2["dziennik"][2]["t"], w2["dziennik"][1]["t"] + w2["dziennik"][1]["trwa"])
        # to, czego nie da się odtworzyć, daje czytelny błąd (odtwarzacz kończy walkę komunikatem, bez wywrotki)
        for zly in ({}, {"strony": {}, "dziennik": []}, {"strony": w["strony"], "dziennik": []}):
            r = _I.wywolaj(PLAN.get("normalizuj"), [LM.do_luau(zly)])
            self.assertIsNone(r[0])
            self.assertIsInstance(r[1], str)


class Pomijanie(unittest.TestCase):
    def setUp(self):
        self.I = interpreter()
        self.M = modul(self.I, "PamiecWalk")
        self.p = wolaj(self.I, self.M, "nowa")[0]

    def przyjmij(self, gracz, zrodlo, gatunek, teraz, koniec):
        return wolaj(self.I, self.M, "przyjmij", self.p, float(gracz), zrodlo, gatunek, float(teraz), float(koniec))[0]

    def pomin(self, gracz, zrodlo, teraz):
        return tuple(wolaj(self.I, self.M, "pomin", self.p, float(gracz), zrodlo, float(teraz)))

    def czy(self, gracz, zrodlo, teraz):
        return tuple(wolaj(self.I, self.M, "czyMozna", self.p, float(gracz), zrodlo, float(teraz)))

    def poznane(self, gracz, teraz):
        return LM.z_luau(wolaj(self.I, self.M, "poznane", self.p, float(gracz), float(teraz))[0], pusta_jako_lista=True)

    def test_pierwsza_walka_bez_pomijania_druga_z(self):
        self.assertFalse(self.przyjmij(1, "TestWalki2", "lesny_slime", 0, 20))
        self.assertEqual(self.czy(1, "TestWalki2", 5), (False, "pierwsza_walka"))
        self.assertEqual(self.pomin(1, "TestWalki2", 5), (False, "pierwsza_walka"))   # próba oszukania z klienta
        self.assertEqual(self.poznane(1, 10), [])                                   # walka jeszcze trwa
        self.assertEqual(self.poznane(1, 20), ["lesny_slime"])                      # skończyła się (pełny czas ×1)
        self.assertTrue(self.przyjmij(1, "TestWalki2", "lesny_slime", 21, 40))
        self.assertEqual(self.czy(1, "TestWalki2", 22), (True, "ok"))
        self.assertEqual(self.pomin(1, "TestWalki2", 22), (True, "ok"))
        self.assertEqual(self.pomin(1, "TestWalki2", 22), (False, "brak_walki"))     # drugi raz tej samej walki
        self.assertFalse(self.przyjmij(1, "TestWalki2", "cierniowy_wilk", 23, 40))  # inny gatunek — znów pierwsza

    def test_nastepna_walka_zamyka_poprzednia_i_zrodla_sa_wspolne(self):
        self.assertFalse(self.przyjmij(7, "LasPasGra", "lesny_troll", 0, 30))
        # rewanż po przegranej przed końcem zajętości (serwer lasu wpuszcza po końcu sesji) — gatunek już poznany
        self.assertTrue(self.przyjmij(7, "LasPasGra", "lesny_troll", 29, 60))
        # ten sam gatunek na tablicy prototypu: pamięć wspólna dla źródeł
        self.assertTrue(self.przyjmij(7, "TestWalki2", "lesny_troll", 61, 80))
        # ta sama walka zgłoszona drugi raz (np. mostek i serwer lasu) — ta sama odpowiedź, bez zmiany stanu
        self.assertTrue(self.przyjmij(7, "TestWalki2", "lesny_troll", 61.5, 80))
        self.assertEqual(self.czy(7, "LasPotwory", 62), (False, "brak_walki"))      # stary las bez mostka: brak walki
        self.assertEqual(self.czy(8, "TestWalki2", 62), (False, "brak_walki"))      # inny gracz

    def test_przerwana_walka_liczy_sie_po_czasie(self):
        self.assertFalse(self.przyjmij(3, "TestWalki2", "postac:mag", 0, 15))
        self.assertEqual(self.poznane(3, 14.9), [])
        self.assertEqual(self.poznane(3, 15), ["postac:mag"])
        self.assertTrue(self.przyjmij(3, "TestWalki2", "postac:mag", 30, 45))
        self.assertEqual(self.poznane(3, 31), ["postac:mag"])
        wolaj(self.I, self.M, "zapomnij", self.p, 3.0)
        self.assertEqual(self.poznane(3, 31), [])


class Skladnia(unittest.TestCase):
    def test_wszystkie_zrodla_luau(self):
        pliki = sorted(f for f in os.listdir(ZRODLA) if f.endswith(".luau"))
        self.assertIn("PlanWalki.luau", pliki)
        self.assertIn("PamiecWalk.luau", pliki)
        bledy = []
        for f in pliki:
            tekst = czytaj(os.path.join(ZRODLA, f))
            bez_kom, bez_kom_nap = SL.rozbierz(tekst)
            bledy += SL.bilans(bez_kom_nap, f) + SL.straznik(tekst, f)
            try:
                LM.Parser(bez_rzutowan(tekst), f, LM.Interpreter()).program()
            except LM.BladSkladni as e:
                bledy.append("%s: składnia (luau_mini): %s" % (f, e))
            # czyste moduły (wykonywane w testach interpreterem) — bez rzutowań i odwrotnych apostrofów
            if f in ("PlanWalki.luau", "PamiecWalk.luau"):
                if "::" in bez_kom_nap or "`" in bez_kom:
                    bledy.append("%s: rzutowanie `::` albo napis z odwrotnym apostrofem w czystym module" % f)
        print("\n  plików Luau: %d (bilans, strażnik, parser luau_mini)" % len(pliki))
        self.assertEqual(bledy, [])


# --------------------------------------------------------------------------- ziarna pokazowe
def podpis(o, w):
    d = w["dziennik"]
    typy = sorted({z["typ"] for z in d})
    um = sorted({z["umiejetnosc"] for z in d if z["umiejetnosc"]})
    trafione = sorted({z["umiejetnosc"] for z in d if z["umiejetnosc"] and z["typ"] == "umiejetnosc"})
    efekty = sorted({z["efekt"] for z in d if z["efekt"]})
    bloki = sorted({z["cel"] for z in d if z["typ"] == "blok"})
    return dict(o, wynik=w["wynik"], tury=w["tury"], zdarzen=len(d), czas=w["czas"], typy=typy, umiejetnosci=um,
                trafione=trafione, efekty=efekty, krytyk=any(z["krytyk"] for z in d), lup=w["lup"],
                stosy=max([z["stosy"] for z in d] + [0]), blok_cel=bloki,
                wskrzeszenia=sorted({z["kto"] for z in d if z["typ"] == "wskrzeszenie"}),
                blok_umiejetnosci=any(z["typ"] == "blok" and z["umiejetnosc"] for z in d),
                pierwsza_umiejetnosc=next((i + 1 for i, z in enumerate(d) if z["umiejetnosc"] and z["kto"] == "gracz"), 0))


def szukaj_ziaren():
    wszystkie = [podpis(o, w) for o, w, _ in wszystkie_walki(ziaren=120)]
    wzorcowe = [p for p in wszystkie if p["zestaw"] == "wzorcowa"]
    wynik = {}
    dlugie = sorted([p for p in wzorcowe if p["tury"] > 20], key=lambda p: -p["tury"])
    wynik["najdluzsza"] = dlugie[0]
    wynik["dluga"] = next(p for p in sorted(dlugie, key=lambda p: p["tury"]) if p["tury"] >= 24 and p["wynik"] == "wygrana")
    wynik["krotka"] = sorted(wzorcowe, key=lambda p: (p["tury"], -len(p["typy"])))[0]
    wynik["wszystkie_typy"] = {}
    for klasa in WZ.KLASY:
        mozliwe = set(Zrodla.TYPY) - {"wskrzeszenie"}
        kand = [p for p in wzorcowe if p["klasa"] == klasa]
        kand.sort(key=lambda p: (-len(set(p["typy"]) & mozliwe), p["tury"] < 8, p["tury"]))
        wynik["wszystkie_typy"][klasa] = dict(kand[0], brakuje=sorted(mozliwe - set(kand[0]["typy"])))
    wynik["umiejetnosci"] = {}
    for uid in S.UMIEJETNOSCI:
        kand = [p for p in wzorcowe if uid in p["trafione"] and 6 <= p["tury"] <= 16]
        kand.sort(key=lambda p: (p["wynik"] != "wygrana", p["tury"]))
        wynik["umiejetnosci"][uid] = kand[0] if kand else None
    wynik["play"] = []
    for i, klasa in enumerate(WZ.KLASY):
        wrogowie = [p["id"] for p in S.PRZECIWNICY_LISTA]
        for j in range(3):
            wrog = wrogowie[(i + j * 2) % len(wrogowie)]
            poziom = POZIOMY[(i + j) % 3]
            kand = [p for p in wzorcowe if p["klasa"] == klasa and p["przeciwnik"] == wrog and p["poziom"] == poziom
                    and 6 <= p["tury"] <= 14]
            kand.sort(key=lambda p: (-len(p["typy"]), p["tury"]))
            wynik["play"].append(kand[0])
    shard = [p for p in wzorcowe if p["lup"]["shard_ewolucji"] > 0]
    wynik["shard"] = sorted(shard, key=lambda p: p["tury"])[0] if shard else None
    gem = [p for p in wzorcowe if p["lup"]["gemy"] > 0 and p["lup"]["shard_ewolucji"] == 0]
    wynik["gem"] = sorted(gem, key=lambda p: p["tury"])[0] if gem else None

    # v3 — pokazy nowości dla testy/test_v3_play.py (krótkie walki, 6–18 tur, gdy się da)
    def najlepsza(warunek, klucz=lambda p: (p["tury"] < 6, p["tury"] > 18, p["tury"])):
        kand = [p for p in wszystkie if warunek(p)]
        return sorted(kand, key=klucz)[0] if kand else None
    v3 = {
        "wskrzeszenie_gracza": najlepsza(lambda p: p["wskrzeszenia"] == ["gracz"] and p["przeciwnik"] != ZE.LUSTRO),
        "wskrzeszenie_przeciwnika": najlepsza(lambda p: p["wskrzeszenia"] == ["wrog"]),
        "wskrzeszenie_obu": najlepsza(lambda p: p["wskrzeszenia"] == ["gracz", "wrog"]),
        "trucizna_stosy": najlepsza(lambda p: p["stosy"] >= 3),
        "ogluszenie_gwiazdki": najlepsza(lambda p: "ogluszajace_uderzenie" in p["trafione"] and "utrata_tury" in p["typy"]
                                         and "ogluszenie" in p["efekty"]),
        "ogluszenie_pnacza": najlepsza(lambda p: "uscisk_korzeni" in p["trafione"] and "utrata_tury" in p["typy"]),
        "ogluszenie_miazdzacy": najlepsza(lambda p: "miazdzacy_cios" in p["trafione"] and "ogluszenie" in p["efekty"]),
        "spowolnienie": najlepsza(lambda p: "lodowy_pocisk" in p["trafione"] and "spowolnienie" in p["efekty"]),
        "podpalenie_dluzsze": najlepsza(lambda p: p["zestaw"] == "pasywki" and p["klasa"] == "mag" and "podpalenie" in p["efekty"]),
        "tarcza_kamienna": najlepsza(lambda p: "kamienna_skora" in p["efekty"] and p["klasa"] == "wojownik"),
        "tarcza_bariera": najlepsza(lambda p: "bariera" in p["efekty"] and p["klasa"] == "mag"),
        "krwawienie": najlepsza(lambda p: "krwawienie" in p["efekty"]),
        "zdarcie": najlepsza(lambda p: "zdarcie_pancerza" in p["efekty"]),
        "skupienie": najlepsza(lambda p: "skupienie" in p["efekty"]),
        "mana_pierwsza_akcja": najlepsza(lambda p: p["zestaw"] == "mana" and p["pierwsza_umiejetnosc"] == 1),
        "pasywki": {k: najlepsza(lambda p, k=k: p["zestaw"] == "pasywki" and p["klasa"] == k and p["poziom"] == 10)
                    for k in WZ.KLASY},
        "blok_umiejetnosci": najlepsza(lambda p: p["blok_umiejetnosci"]),
        "blok": {},
    }
    # blok każdej klasy i potwora (broniący = cel zdarzenia blok)
    for kto in list(WZ.KLASY) + [p["id"] for p in S.PRZECIWNICY_LISTA]:
        if kto in WZ.KLASY:
            v3["blok"][kto] = najlepsza(lambda p, kto=kto: p["klasa"] == kto and "gracz" in p["blok_cel"] and p["przeciwnik"] != ZE.LUSTRO)
        else:
            v3["blok"][kto] = najlepsza(lambda p, kto=kto: p["przeciwnik"] == kto and "wrog" in p["blok_cel"])
    # pomijanie (D-078): dwie walki z tym samym gatunkiem (pierwsza bez przycisku, druga z przyciskiem)
    v3["pomijanie"] = najlepsza(lambda p: p["zestaw"] == "wzorcowa" and p["przeciwnik"] == "lesny_slime" and 6 <= p["tury"] <= 10)
    wynik["v3"] = v3
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
        for k, p in w["v3"].items():
            for nazwa, q in (p.items() if isinstance(p, dict) and "klasa" not in p else [(k, p)]):
                if q:
                    print("v3 %-26s %s (%d tur)" % (nazwa if nazwa == k else "%s.%s" % (k, nazwa), opis_walki(q), q["tury"]))
                else:
                    print("v3 %-26s BRAK" % nazwa)
        print("zapisane: swiat/test_walki2/testy/ziarna.json")
    else:
        unittest.main(verbosity=2)
