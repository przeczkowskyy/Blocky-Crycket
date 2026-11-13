#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test silnika walki w Roblox Studio (tryb Edit, tylko odczyt — nic nie zmienia w miejscu).

    python -B swiat/test_walki_roblox/testy/test_silnika.py [--studio <studio_id>] [--ile 1500]

Wymaga zbudowanego kontenera (zbuduj.py). Sprawdza moduł Workspace/TestWalki/Moduly/SilnikWalki:
  1. powtarzalność — to samo ziarno dwa razy daje identyczny dziennik;
  2. niezmienniki — 4–6 wymian, 8–10 s, rosnące czasy, zgodne hp_po, nokaut w ostatniej wymianie (SilnikWalki.sprawdz);
  3. zgodność z kontrolnym portem w Pythonie (testy/symulacja.py) dla każdego ziarna — ten sam dziennik co do liczby;
  4. błędne dane wejściowe są odrzucane.
"""
import argparse
import json
import os
import sys

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, TU)
from studio_mcp import StudioMCP, StudioError  # noqa: E402
sys.path.insert(0, os.path.dirname(TU))
from cel_studio import wybierz_studio  # noqa: E402
import symulacja  # noqa: E402

LUAU = r'''
local HttpService = game:GetService("HttpService")
local kontener = workspace:FindFirstChild("TestWalki")
if not kontener then return HttpService:JSONEncode({ blad = "brak kontenera Workspace/TestWalki — uruchom zbuduj.py" }) end
local Silnik = require(kontener.Moduly.SilnikWalki)
local G = HttpService:JSONDecode([==[__GRACZ__]==])
local W = HttpService:JSONDecode([==[__WROG__]==])
local ILE = __ILE__
local function podpis(w)
	local t = {}
	for _, z in w.dziennik do
		table.insert(t, string.format("%s:%s-%d>%d@%.2f", string.sub(z.kto, 1, 1), z.akcja, z.obrazenia, z.hp_po, z.t))
	end
	return table.concat(t, ",") .. "|" .. w.wynik .. "|" .. w.lup.zloto .. "/" .. w.lup.doswiadczenie .. "/" .. w.lup.jajko .. "|" .. string.format("%.2f", w.czas)
end
-- odpowiedź narzędzia jest przycinana do ok. 100 tys. znaków, więc odsyłamy skróty podpisów, a nie całe podpisy
local function skrot(napis)
	local h = 7
	for i = 1, #napis do
		h = (h * 131 + string.byte(napis, i)) % 2147483647
	end
	return h
end
local wynik = { skroty = {}, przyklady = {}, zle = {}, powtarzalne = true }
for ziarno = 1, ILE do
	local a = Silnik.symuluj(G, W, ziarno)
	local dobre, opis = Silnik.sprawdz(a)
	if not dobre then table.insert(wynik.zle, ziarno .. ": " .. tostring(opis)) end
	local pa = podpis(a)
	if ziarno % 50 == 0 then
		local b = Silnik.symuluj(G, W, ziarno)
		if podpis(b) ~= pa or HttpService:JSONEncode(a) ~= HttpService:JSONEncode(b) then wynik.powtarzalne = false end
	end
	wynik.skroty[ziarno] = skrot(pa)
	if ziarno == 1 or ziarno == 6 or ziarno == 153 or ziarno == 770 then wynik.przyklady[tostring(ziarno)] = pa end
	if ziarno % 400 == 0 then task.wait() end
end
-- błędne dane muszą zostać odrzucone
local odrzucone = 0
for _, proba in { function() Silnik.symuluj(nil, W, 1) end, function() Silnik.symuluj(G, { hp = -5 }, 1) end,
	function() Silnik.symuluj(G, W, "abc") end, function() Silnik.symuluj(G, W, 0 / 0) end } do
	if not pcall(proba) then odrzucone += 1 end
end
wynik.odrzucone = odrzucone
return HttpService:JSONEncode(wynik)
'''


def podpis(w):
    t = ",".join("%s:%s-%d>%d@%.2f" % (z["kto"][0], z["akcja"], z["obrazenia"], z["hp_po"], z["t"]) for z in w["dziennik"])
    return "%s|%s|%d/%d/%d|%.2f" % (t, w["wynik"], w["lup"]["zloto"], w["lup"]["doswiadczenie"], w["lup"]["jajko"], w["czas"])


def skrot(napis):
    h = 7
    for b in napis.encode("utf-8"):
        h = (h * 131 + b) % 2147483647
    return h


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", default=None)
    ap.add_argument("--ile", type=int, default=1500)
    a = ap.parse_args()
    kod = (LUAU.replace("__GRACZ__", json.dumps(symulacja.GRACZ)).replace("__WROG__", json.dumps(symulacja.WROG))
           .replace("__ILE__", str(a.ile)))
    try:
        with StudioMCP() as s:
            sid = wybierz_studio(s, a.studio)
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
            if r["is_error"]:
                sys.exit("BŁĄD Studio: " + r["text"][:2000])
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)
    d = json.loads(r["text"])
    if d.get("blad"):
        sys.exit(d["blad"])
    roznice = []
    for ziarno in range(1, a.ile + 1):
        oczekiwany = podpis(symulacja.symuluj(symulacja.GRACZ, symulacja.WROG, ziarno))
        if d["skroty"][ziarno - 1] != skrot(oczekiwany):
            roznice.append((ziarno, d["przyklady"].get(str(ziarno), "?"), oczekiwany))
    ok = True
    print("1. powtarzalność:            %s" % ("OK" if d["powtarzalne"] else "BŁĄD"))
    ok &= bool(d["powtarzalne"])
    print("2. niezmienniki (%d ziaren): %s" % (a.ile, "OK" if not d["zle"] else "BŁĄD %s" % d["zle"][:5]))
    ok &= not d["zle"]
    print("3. zgodność z portem:        %s" % ("OK (%d/%d identycznych dzienników)" % (a.ile, a.ile) if not roznice
                                             else "BŁĄD: %d różnic, np. %s" % (len(roznice), roznice[:2])))
    ok &= not roznice
    print("4. odrzucanie złych danych:  %s" % ("OK (4/4)" if d["odrzucone"] == 4 else "BŁĄD (%s/4)" % d["odrzucone"]))
    ok &= d["odrzucone"] == 4
    for ziarno, tekst in sorted(d["przyklady"].items(), key=lambda kv: int(kv[0])):
        print("   ziarno %4s: %s" % (ziarno, tekst))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
