#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Szybkie sprawdzenie w trybie EDIT (tylko odczyt, nic nie zmienia w miejscu):
  1. każdy moduł kontenera da się wczytać (require) — błąd składni albo wczytania wychodzi od razu;
  2. Moduly/Wzorcowe (serwer) + kopia silnika dają dla wyborów z listy i ziaren TEN SAM dziennik co port w Pythonie
     (tools/walka/wzorcowe.py + tools/walka/silnik.py) — podpis: wynik, tury, liczba zdarzeń, czas, życie stron, łup;
  3. funkcje pomocnicze z poprawek po przeglądzie: liczba obrażeń przy trafieniu w całości w tarczę (bez „−0”),
     odmiana liczebników w panelu wyniku (1 tura / 3 tury / 5 tur, w 1 turze), wygląd spowolnienia zależny od umiejętności.

    python -B swiat/test_walki2/testy/sprawdz_edit.py [--studio <id>]
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
KATALOG = os.path.dirname(TU)
REPO = os.path.dirname(os.path.dirname(KATALOG))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "tools", "walka"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.insert(0, _s)
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
import silnik as S  # noqa: E402
import wzorcowe as WZ  # noqa: E402

MODULY = ["Ustawienia", "Klipy", "Aktorzy", "Wzorcowe", "Choreografie", "Efekty3D", "InterfejsWalki2", "WyborWalki2",
          "OdtwarzaczWalki2", "Dziennik", "PlanWalki", "PamiecWalk"]  # v3: dwa czyste moduły

KOD = r'''
if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce" end
if game:GetService("RunService"):IsRunning() then return "STOP: tryb Play" end
local HS = game:GetService("HttpService")
local k = workspace:FindFirstChild("TestWalki2")
if not k or k:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local M = k.Moduly
local w = { moduly = {}, walki = {} }
for _, n in { __MODULY__ } do
	local ok, b = pcall(require, M[n])
	w.moduly[n] = if ok then "OK" else tostring(b)
end
local W = require(M.Wzorcowe)
local Silnik = require(M.Walka.Silnik)
local Dziennik = require(M.Dziennik)
for _, p in { __PROBY__ } do
	local ok, walka = pcall(Silnik.symuluj, W.postac(p[1], p[3]), { potwor = p[2], poziom = p[3] }, p[4])
	if not ok then
		table.insert(w.walki, { blad = tostring(walka) })
	else
		local dobre, opis = Dziennik.sprawdz(walka)
		local hp = walka.dziennik[#walka.dziennik]
		table.insert(w.walki, { wynik = walka.wynik, tury = walka.tury, zdarzen = #walka.dziennik, czas = walka.czas,
			hp = { hp.hp_gracz, hp.hp_wrog }, zycie = { walka.strony.gracz.zycie, walka.strony.wrog.zycie },
			zloto = walka.lup.zloto, dosw = walka.lup.doswiadczenie, sprawdz = dobre, opis = opis })
	end
end
-- funkcje pomocnicze odtwarzacza i interfejsu (poprawki po przeglądzie etapu 3)
local O = require(M.OdtwarzaczWalki2)
local I = require(M.InterfejsWalki2)
w.liczba = {
	O.pokazLiczbe({ obrazenia = 0, pochloniete = 26 }),   -- całość na tarczy → bez „−0”
	O.pokazLiczbe({ obrazenia = 5, pochloniete = 20 }),
	O.pokazLiczbe({ obrazenia = 0, pochloniete = 0 }),     -- (nie występuje, ale bez tarczy liczba zostaje)
	O.pokazLiczbe({ obrazenia = 12, pochloniete = 0 }),
}
w.odmiana = {}
for _, n in { 1, 2, 3, 4, 5, 11, 12, 14, 21, 22, 25, 33, 104, 112 } do
	table.insert(w.odmiana, I.liczebnik(n, "tura", "tury", "tur"))
end
table.insert(w.odmiana, I.wTurach(1))
table.insert(w.odmiana, I.wTurach(3))
table.insert(w.odmiana, I.liczebnik(1, "zdarzenie", "zdarzenia", "zdarzeń"))
table.insert(w.odmiana, I.liczebnik(23, "zdarzenie", "zdarzenia", "zdarzeń"))
w.wyglad = {
	-- v3: spowolnienie (lód) i ogłuszenie (gwiazdki / pnącza) to różne statusy
	O.wygladEfektu("spowolnienie", "lodowy_pocisk"), O.wygladEfektu("ogluszenie", "uscisk_korzeni"),
	O.wygladEfektu("ogluszenie", "ogluszajace_uderzenie"), O.wygladEfektu("ogluszenie", ""),
	O.wygladEfektu("trucizna", "lodowy_pocisk"), O.wygladEfektu("spowolnienie", ""),
}
-- v3: zestawy postaci tablicy (W.zestaw) przechodzą ścisłą walidację wejścia silnika w Studio (gracz i lustro)
w.zestawy = {}
for _, zestaw in W.ZESTAWY do
	for _, klasa in W.KLASY do
		for _, poziom in { 1, 5, 10 } do
			local ok, walka = pcall(Silnik.symuluj, W.zestaw(zestaw, klasa, poziom), { postac = W.lustro(zestaw, klasa, poziom) }, 7)
			local dobre = ok and (Dziennik.sprawdz(walka))
			if not dobre then
				table.insert(w.zestawy, zestaw .. "/" .. klasa .. "/" .. poziom .. ": " .. tostring(if ok then "dziennik" else walka))
			end
		end
	end
end
-- v3: czysta logika odtwarzacza i pamięć pomijania wczytują się w Studio
local PW = require(M.PlanWalki)
local PM = require(M.PamiecWalk)
local pam = PM.nowa()
w.pamiec = { PM.przyjmij(pam, 1, "TestWalki2", "lesny_slime", 0, 10), (PM.pomin(pam, 1, "TestWalki2", 5)),
	PM.przyjmij(pam, 1, "TestWalki2", "lesny_slime", 11, 20), (PM.pomin(pam, 1, "TestWalki2", 12)) }
w.plan = #PW.TYPY
return HS:JSONEncode(w)
'''

OCZEKIWANE = {
    "liczba": [False, True, True, True],
    "odmiana": ["1 tura", "2 tury", "3 tury", "4 tury", "5 tur", "11 tur", "12 tur", "14 tur", "21 tur", "22 tury",
                "25 tur", "33 tury", "104 tury", "112 tur", "w 1 turze", "w 3 turach", "1 zdarzenie", "23 zdarzenia"],
    "wyglad": ["lod", "pnacza", "gwiazdki", "gwiazdki", "babelki", "lod"],
    "zestawy": [],
    "pamiec": [False, False, True, True],
    "plan": 10,
}


def podpis_py(klasa, wrog, poziom, ziarno):
    w = S.symuluj(WZ.postac(klasa, poziom), {"potwor": wrog, "poziom": poziom}, ziarno)
    hp = w["dziennik"][-1]
    return {"wynik": w["wynik"], "tury": w["tury"], "zdarzen": len(w["dziennik"]), "czas": round(w["czas"], 2),
            "hp": [hp["hp_gracz"], hp["hp_wrog"]], "zycie": [w["strony"]["gracz"]["zycie"], w["strony"]["wrog"]["zycie"]],
            "zloto": w["lup"]["zloto"], "dosw": w["lup"]["doswiadczenie"]}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    proby = []
    for klasa in WZ.KLASY:
        for wrog in [p["id"] for p in S.PRZECIWNICY_LISTA]:
            for poziom in (1, 5, 10):
                proby.append((klasa, wrog, poziom, 1000 + len(proby) * 7919))
    kod = (KOD.replace("__MIEJSCE__", str(MIEJSCE)).replace("__MODULY__", ", ".join('"%s"' % m for m in MODULY))
           .replace("__PROBY__", ", ".join('{"%s", "%s", %d, %d}' % p for p in proby)))
    with StudioMCP(timeout=120) as s:
        sid = wybierz_studio(s, a.studio)
        r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=110)
        if r["is_error"] or r["text"].startswith("STOP"):
            sys.exit("BŁĄD: " + r["text"][:2000])
        w = json.loads(r["text"])
    zle = 0
    for n, stan in w["moduly"].items():
        print("moduł %-18s %s" % (n, stan))
        zle += stan != "OK"
    zgodne = 0
    for p, wl in zip(proby, w["walki"]):
        wp = podpis_py(*p)
        if "blad" in wl:
            print("BŁĄD walki", p, wl["blad"])
            zle += 1
            continue
        wl2 = dict(wl)
        wl2["czas"] = round(wl2["czas"], 2)
        ok = all(wl2[k] == wp[k] for k in wp) and wl["sprawdz"]
        zgodne += ok
        if not ok:
            zle += 1
            print("RÓŻNICA", p, "\n  Luau:", wl2, "\n  Py:  ", wp)
    print("walki: %d/%d zgodnych z Pythonem (Wzorcowe.luau + kopia silnika vs wzorcowe.py + silnik.py)" % (zgodne, len(proby)))
    for klucz, oczek in OCZEKIWANE.items():
        ok = w.get(klucz) == oczek
        zle += not ok
        print("%-8s %s%s" % (klucz, "OK" if ok else "BŁĄD", "" if ok else "\n  jest:     %s\n  oczekuję: %s" % (w.get(klucz), oczek)))
    print("WYNIK:", "OK" if zle == 0 else "BŁĘDY: %d" % zle)
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
