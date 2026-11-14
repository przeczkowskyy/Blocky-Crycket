#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test modułów Klipy i Aktorzy w trybie PLAY (lokalne klony u klienta). Na końcu ZAWSZE wraca do trybu Edit.

    python -B swiat/test_walki2/testy/test_klipow_play.py [--studio <id>]

Sprawdza: klon każdego aktora powstaje i ma klip spoczynku; graj() z naTrafieniu / naKoniec / potem (zdarzenia
w dobrych chwilach, po końcu gra „potem”); tempo ×2 skraca klip o połowę; dlugosc= dopasowuje prędkość; płynne
przejście (staw w połowie przejścia jest między pozami); zatrzymaj() wraca do pozy zerowej; nakładka; brak klipu
→ nil; punkty aktora; obrys highlight / skorupa / brak; zniszcz() sprząta; pomiar kosztu (krok + zastosuj) na klatkę
dla dwóch aktorów i czas klatki w trakcie odtwarzania. Zmienia wyłącznie stan sesji Play.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TU)))
for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"), TU):
    sys.path.insert(0, _s)
from studio_mcp import StudioMCP, StudioError  # noqa: E402
from cel_studio import wybierz_studio  # noqa: E402
from czuwanie import nie_usypiaj  # noqa: E402

TEST = r'''
local HS = game:GetService("HttpService")
local RS = game:GetService("RunService")
local k = workspace.TestWalki2
local U = require(k.Moduly.Ustawienia)
local Aktorzy = require(k.Moduly.Aktorzy)
local f = Instance.new("Folder")
f.Name = "TestKlipowLokalny"
f.Parent = k
local w = {}
local ok, blad = pcall(function()
	-- 1. każdy aktor: klon, spoczynek, liczby
	w.aktorzy = {}
	for _, klucz in Aktorzy.kolejnosc do
		local a = Aktorzy.nowy(klucz, U.miejsce("wrog"), { rodzic = f })
		task.wait(0.15)
		local tor = a.klipy:biezacy()
		w.aktorzy[klucz] = { spoczynek = tor and tor.nazwa or "BRAK", czesci = a.liczbaCzesci, instancje = a.liczbaInstancji,
			pasek = a:punkt("Pasek") ~= nil, bron = a:punkt("Bron") ~= nil, piers = a:punkt("Piers") ~= nil,
			pocisk = a:punkt("Pocisk") ~= nil }
		a:zniszcz()
	end
	-- 2. zdarzenia, potem, tempo
	local a = Aktorzy.nowy("wojownik", U.miejsce("gracz"), { rodzic = f })
	task.wait(0.3)
	local t0 = os.clock()
	local trafienie, koniec
	local tor = a:graj("atak", { naTrafieniu = function() trafienie = os.clock() - t0 end, potem = "idle" })
	tor:naKoniec(function() koniec = os.clock() - t0 end)
	local dl = tor.dlugosc
	while not koniec and os.clock() - t0 < 4 do task.wait() end
	task.wait(0.3)
	w.atak = { dlugosc = dl, trafienie = trafienie, koniec = koniec, chwila = a:chwila("atak"),
		potem = a.klipy:biezacy() and a.klipy:biezacy().nazwa }
	a.klipy.tempo = 2
	t0 = os.clock()
	koniec = nil
	tor = a:graj("atak", { potem = "idle" })
	tor:naKoniec(function() koniec = os.clock() - t0 end)
	while not koniec and os.clock() - t0 < 4 do task.wait() end
	w.tempo2 = koniec
	a.klipy.tempo = 1
	t0 = os.clock()
	koniec = nil
	tor = a:graj("ciecie", { dlugosc = 0.7 })
	tor:naKoniec(function() koniec = os.clock() - t0 end)
	while not koniec and os.clock() - t0 < 4 do task.wait() end
	w.dopasowanie07 = koniec
	-- 3. przejście: staw ramienia w połowie przejścia leży między pozą końca cięcia a pozą spoczynku
	local staw = a.model.RightUpperArm:FindFirstChildOfClass("Motor6D")
	a.klipy:poza("ciecie", 0.5) -- ręka z mieczem wyciągnięta w bok: daleko od pozy spoczynku
	task.wait(0.05)
	local przed = staw.Transform
	a.klipy:graj("idle", { przejscie = 0.6, petla = true })
	task.wait(0.3)
	local srodek = staw.Transform
	task.wait(0.6)
	local po = staw.Transform
	local function kat(x, y) local _, k2 = (x:Inverse() * y):ToAxisAngle() return math.deg(math.abs(k2)) end
	w.przejscie = { przed_po = kat(przed, po), przed_srodek = kat(przed, srodek), srodek_po = kat(srodek, po) }
	-- 4. zatrzymaj → poza zerowa, nakładka, brak klipu
	a.klipy:zatrzymaj(0.1)
	task.wait(0.4)
	local maks = 0
	for _, m in a.model:GetDescendants() do
		if m:IsA("Motor6D") then
			local _, k2 = m.Transform:ToAxisAngle()
			maks = math.max(maks, math.deg(math.abs(k2)) + m.Transform.Position.Magnitude * 100)
		end
	end
	w.zero = maks
	a.klipy:ustawNakladke("Head", CFrame.Angles(0, math.rad(40), 0))
	task.wait(0.1)
	local _, kg = a.model.Head:FindFirstChildOfClass("Motor6D").Transform:ToAxisAngle()
	w.nakladka = math.deg(kg)
	a.klipy:ustawNakladke("Head", nil)
	w.brakKlipu = a:graj("blok_ktorego_nie_ma") == nil and a:graj("blok") ~= nil
	w.zwiadowcaBlok = Aktorzy.klip("zwiadowca", "blok") == nil
	w.umiejetnosc = Aktorzy.klip("mag", "kula_ognia")
	-- 5. obrys
	w.obrys = { highlight = a:obrys("highlight"), skorupa = a:obrys("skorupa"), brak = a:obrys("brak") }
	w.poBraku = a.model:FindFirstChild("ObrysSkorupa") == nil and a.model:FindFirstChild("ObrysHighlight") == nil
	a:zniszcz()
	-- 6. koszt: dwa aktory, krok + zastosuj ręcznie, 300 razy
	local g = Aktorzy.nowy("wojownik", U.miejsce("gracz"), { rodzic = f, reczny = true })
	local p = Aktorzy.nowy("lesny_troll", U.miejsce("wrog", 16), { rodzic = f, reczny = true })
	g:graj("ciecie", { petla = true })
	p:graj("atak", { petla = true })
	local czasy = {}
	for i = 1, 300 do
		local t = os.clock()
		g.klipy:krok(1 / 60); g.klipy:zastosuj()
		p.klipy:krok(1 / 60); p.klipy:zastosuj()
		table.insert(czasy, (os.clock() - t) * 1000)
		if i % 10 == 0 then RS.Heartbeat:Wait() end
	end
	table.sort(czasy)
	local s = 0
	for _, c in czasy do s += c end
	w.koszt = { srednio = s / #czasy, p95 = czasy[math.floor(#czasy * 0.95)], maks = czasy[#czasy] }
	g:zniszcz(); p:zniszcz()
	-- 7. czas klatki przy dwóch aktorach w pętli automatycznej (3 s)
	g = Aktorzy.nowy("wojownik", U.miejsce("gracz"), { rodzic = f })
	p = Aktorzy.nowy("lesny_troll", U.miejsce("wrog", 16), { rodzic = f })
	g:graj("ciecie", { petla = true })
	p:graj("atak", { petla = true })
	local dts = {}
	local c = RS.Heartbeat:Connect(function(dt) table.insert(dts, dt * 1000) end)
	task.wait(3)
	c:Disconnect()
	table.sort(dts)
	s = 0
	for _, d in dts do s += d end
	w.klatka = { srednio = s / #dts, p95 = dts[math.floor(#dts * 0.95)], maks = dts[#dts], klatek = #dts }
	g:zniszcz(); p:zniszcz()
	-- 8. haczyk klienta Sygnaly/PokazAktora (skrypt KlientWalki2)
	k.Sygnaly.PokazAktora:Fire("lesny_troll", "atak")
	task.wait(0.5)
	local pokaz = k:FindFirstChild("PokazLokalny")
	w.pokaz = pokaz ~= nil and pokaz:FindFirstChild("lesny_troll_lokalny") ~= nil
	k.Sygnaly.PokazAktora:Fire()
	task.wait(0.3)
	w.pokazSprzatniety = k:FindFirstChild("PokazLokalny") == nil
end)
f:Destroy()
w.ok = ok
w.blad = if ok then nil else tostring(blad)
w.posprzatane = k:FindFirstChild("TestKlipowLokalny") == nil
return HS:JSONEncode(w)
'''


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    wyniki = []

    def sprawdz(nazwa, warunek, opis=""):
        wyniki.append((nazwa, bool(warunek)))
        print("%-62s %s %s" % (nazwa, "OK" if warunek else "BŁĄD", opis), flush=True)

    with StudioMCP(timeout=180) as s:
        sid = wybierz_studio(s, a.studio)

        def call(n, x=None, timeout=None):
            x = dict(x or {})
            x["studio_id"] = sid
            return s.call(n, x, timeout=timeout)

        def tryb_edit():
            return "Current Studio Mode: Edit" in call("get_studio_state")["text"]

        if not tryb_edit():
            sys.exit("Studio nie jest w trybie Edit — nie zaczynam.")
        nie_usypiaj()
        try:
            call("start_stop_play", {"is_start": True})
            for _ in range(120):
                if "Client" in call("get_studio_state")["text"]:
                    r = call("execute_luau", {"code": 'local k = workspace:FindFirstChild("TestWalki2") return tostring(k and k:GetAttribute("KlientGotowy"))',
                                              "datamodel_type": "Client"})
                    if r["text"].strip() == "true":
                        break
                time.sleep(0.5)
            time.sleep(1.0)
            r = call("execute_luau", {"code": TEST, "datamodel_type": "Client"}, timeout=170)
            if r["is_error"]:
                raise StudioError(r["text"][:2000])
            w = json.loads(r["text"])
            print(json.dumps(w, ensure_ascii=False, indent=1))
            sprawdz("0. test bez błędu Luau", w.get("ok"), w.get("blad") or "")
            for klucz, x in (w.get("aktorzy") or {}).items():
                sprawdz("1. %s: klon gra spoczynek, ma punkty" % klucz,
                        x["spoczynek"] != "BRAK" and x["pasek"] and x["bron"] and x["piers"] and x["pocisk"],
                        "(%s, %d brył, %d instancji)" % (x["spoczynek"], x["czesci"], x["instancje"]))
            at = w.get("atak") or {}
            sprawdz("2a. naTrafieniu w chwili z tabeli (±0,1 s)",
                    at.get("trafienie") is not None and abs(at["trafienie"] - at["chwila"]) < 0.1,
                    "(%.2f s, tabela %.2f s)" % (at.get("trafienie") or -1, at.get("chwila") or -1))
            sprawdz("2b. naKoniec po długości klipu (±0,1 s)", at.get("koniec") is not None and abs(at["koniec"] - at["dlugosc"]) < 0.1,
                    "(%.2f s, klip %.2f s)" % (at.get("koniec") or -1, at.get("dlugosc") or -1))
            sprawdz("2c. po końcu gra klip „potem” (idle)", at.get("potem") == "idle", "(%s)" % at.get("potem"))
            sprawdz("2d. tempo ×2 skraca klip o połowę (±0,08 s)", w.get("tempo2") is not None and abs(w["tempo2"] - at["dlugosc"] / 2) < 0.08,
                    "(%.2f s)" % (w.get("tempo2") or -1))
            sprawdz("2e. dlugosc = 0,7 s dopasowuje prędkość (±0,08 s)", w.get("dopasowanie07") is not None and abs(w["dopasowanie07"] - 0.7) < 0.08,
                    "(%.2f s)" % (w.get("dopasowanie07") or -1))
            pr = w.get("przejscie") or {}
            sprawdz("3. płynne przejście: w połowie staw jest między pozami",
                    pr and pr["przed_srodek"] > 0.15 * pr["przed_po"] and pr["srodek_po"] > 0.15 * pr["przed_po"] and pr["przed_po"] > 5,
                    str(pr))
            sprawdz("4a. zatrzymaj() wraca do pozy zerowej", (w.get("zero") if w.get("zero") is not None else 99) < 0.5, "(%.3f)" % (w.get("zero") if w.get("zero") is not None else -1))
            sprawdz("4b. nakładka obraca staw (40°)", abs((w.get("nakladka") or 0) - 40) < 1.0, "(%.1f°)" % (w.get("nakladka") or -1))
            sprawdz("4c. brak klipu → nil; Wojownik ma blok; Zwiadowca bez bloku", w.get("brakKlipu") and w.get("zwiadowcaBlok"))
            sprawdz("4d. umiejętność → klip (kula_ognia)", w.get("umiejetnosc") == "kula_ognia", "(%s)" % w.get("umiejetnosc"))
            ob = w.get("obrys") or {}
            sprawdz("5. obrys: highlight 1, skorupa > 0, brak sprząta", ob.get("highlight") == 1 and (ob.get("skorupa") or 0) > 0 and w.get("poBraku"),
                    str(ob))
            sprawdz("6. sprzątanie lokalnych klonów", w.get("posprzatane"))
            sprawdz("8. Sygnaly/PokazAktora: klon na podeście i sprzątanie", w.get("pokaz") and w.get("pokazSprzatniety"))
            ko, kl = w.get("koszt") or {}, w.get("klatka") or {}
            print("koszt Klipy (2 aktorów, krok+zastosuj): średnio %.3f ms, p95 %.3f ms, maks %.3f ms"
                  % (ko.get("srednio", -1), ko.get("p95", -1), ko.get("maks", -1)))
            print("czas klatki (Heartbeat, 2 aktorów w pętli, 3 s): średnio %.2f ms, p95 %.2f ms, maks %.2f ms, klatek %s"
                  % (kl.get("srednio", -1), kl.get("p95", -1), kl.get("maks", -1), kl.get("klatek")))
            kons = call("get_console_output")["text"]
            zle = [x for x in kons.splitlines() if "TestWalki2" in x and ("rror" in x or "warn" in x.lower() or "[TestWalki2]" in x)]
            sprawdz("7. konsola bez komunikatów z TestWalki2", not zle, "\n".join(zle[:5]))
        finally:
            call("start_stop_play", {"is_start": False})
            for _ in range(40):
                time.sleep(0.5)
                if tryb_edit():
                    break
            sprawdz("Studio wróciło do trybu Edit", tryb_edit())
    zle = [n for n, ok in wyniki if not ok]
    print("WYNIK: %d/%d zaliczonych%s" % (len(wyniki) - len(zle), len(wyniki), "" if not zle else " — nie: " + "; ".join(zle)))
    sys.exit(1 if zle else 0)


if __name__ == "__main__":
    main()
