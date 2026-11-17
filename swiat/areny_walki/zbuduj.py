#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener aren walki Workspace/ArenyWalki z plików tego pakietu (część B pracy D-095).

    python -B swiat/areny_walki/zbuduj.py --sucho            # tylko sprawdza pliki i pokazuje plan (bez Studio)
    python -B swiat/areny_walki/zbuduj.py                    # buduje / odbudowuje cały kontener (idempotentnie)
    python -B swiat/areny_walki/zbuduj.py --tylko bagno      # odbudowuje jedną arenę (moduły też)
    python -B swiat/areny_walki/zbuduj.py --moduly           # tylko moduły (ArenyWalki, LogikaAren, DaneAren)
    python -B swiat/areny_walki/zbuduj.py --usun             # usuwa kontener (walki wracają na starą arenę)
    python -B swiat/areny_walki/zbuduj.py --studio <id>      # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/ArenyWalki z atrybutem Wygenerowane = true):
  Moduly/ArenyWalki, Moduly/LogikaAren, Moduly/DaneAren (ModuleScript; zaczynają się od strażnika Studio)
  Las, Bagno, Proba — Model, ModelStreamingMode = Persistent (przychodzi do klienta po dołączeniu i nie jest wypychany),
       części z <arena>/czesci.json (Anchored, bez CanCollide, CanQuery i CanTouch; cień wg pliku), grupy jako Modele,
       znacznik „Scena” (niewidzialny klocek 1 × 1 × 1 w CFrame.lookAt(O, O + (0, 0, 1)) = cfSceny odtwarzacza),
       atrybuty Biom, Nazwa, LiczbaCzesci, Zbudowano.
Zasady bezpieczeństwa (wspólne Team Create) jak swiat/test_walki2/zbuduj.py: tylko tryb Edit, tylko placeId gry
(cel_studio.py), tylko kontener z atrybutem Wygenerowane, przed budową kontrola, czy w pudłach aren nie stoi nic obcego,
punkty historii przed i po (całość cofa Ctrl+Z), niczego nie publikuje, nie zapisuje miejsca, nie zmienia Lighting.
Moduły odtwarzacza walki (Workspace/TestWalki2) wysyła osobno: python -B swiat/test_walki2/zbuduj.py --skrypty.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox"), TU):
    if _s not in sys.path:
        sys.path.insert(0, _s)

import plan as P  # noqa: E402

KONTENER = "ArenyWalki"
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
MODULY = [("zrodla/DaneAren.luau", "DaneAren"), ("zrodla/LogikaAren.luau", "LogikaAren"), ("zrodla/ArenyWalki.luau", "ArenyWalki")]
PACZKA = 200

START = r'''
local CH = game:GetService("ChangeHistoryService")
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit"
end
local nazwa = "__KONTENER__"
local stary = workspace:FindFirstChild(nazwa)
if stary and stary:GetAttribute("Wygenerowane") ~= true then
	return "STOP: w Workspace jest obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
end
if __USUN__ then
	if not stary then return "USUNIETO (kontenera nie było)" end
	CH:SetWaypoint("ArenyWalki: przed usunięciem")
	stary:Destroy()
	CH:SetWaypoint("ArenyWalki: usunięto")
	return "USUNIETO"
end
-- pudła aren muszą być wolne od cudzych części (poza starym własnym kontenerem)
local filtr = OverlapParams.new()
filtr.FilterType = Enum.RaycastFilterType.Exclude
local wyklucz = { workspace.Terrain }
if stary then table.insert(wyklucz, stary) end
local plyta = workspace:FindFirstChild("Baseplate")
if plyta then table.insert(wyklucz, plyta) end
filtr.FilterDescendantsInstances = wyklucz
for _, p in __PUDLA__ do
	local obce = workspace:GetPartBoundsInBox(CFrame.new(p[1], p[2], p[3]), Vector3.new(p[4], p[5], p[6]), filtr)
	if #obce > 0 then
		return "STOP: w miejscu areny stoi coś obcego (" .. #obce .. " części), np. " .. obce[1]:GetFullName()
	end
end
CH:SetWaypoint("ArenyWalki: przed budową")
local f = stary
if not f then
	f = Instance.new("Folder")
	f.Name = nazwa
	f:SetAttribute("Wygenerowane", true)
	f.Parent = workspace
end
f:SetAttribute("Zrodlo", "swiat/areny_walki")
f:SetAttribute("Zbudowano", "__CZAS__")
local m = f:FindFirstChild("Moduly")
if not m then
	m = Instance.new("Folder")
	m.Name = "Moduly"
	m.Parent = f
end
for _, n in __ODBUDUJ__ do
	local a = f:FindFirstChild(n)
	if a then a:Destroy() end
end
return "OK"
'''

MODUL = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local m = f:FindFirstChild("Moduly")
local stary = m:FindFirstChild("__NAZWA__")
if stary then stary:Destroy() end
local s = Instance.new("ModuleScript")
s.Name = "__NAZWA__"
s.Source = __ZRODLO__
s.Parent = m
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''

ARENA = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local a = Instance.new("Model")
a.Name = "__MODEL__"
a.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
a:SetAttribute("Biom", "__BIOM__")
a:SetAttribute("Nazwa", "__NAZWA__")
a:SetAttribute("Zbudowano", "__CZAS__")
local z = Instance.new("Part")
z.Name = "Scena"
z.Size = Vector3.one
z.Anchored = true
z.CanCollide = false
z.CanQuery = false
z.CanTouch = false
z.CastShadow = false
z.Transparency = 1
local O = Vector3.new(__O__)
z.CFrame = CFrame.lookAt(O, O + Vector3.new(0, 0, 1))
z.Parent = a
a.WorldPivot = z.CFrame
a.Parent = f
return "OK"
'''

CZESCI = r'''
local G = __GRUPY__
local M = __MATERIALY__
local D = __DANE__
local f = workspace:FindFirstChild("__KONTENER__")
local cache = {}
local function grupa(i)
	local m = cache[i]
	if m then return m end
	local path = string.split(G[i], "/")
	local cur = workspace
	for k = 2, #path do
		local nxt = cur:FindFirstChild(path[k])
		if not nxt then
			nxt = Instance.new("Model")
			nxt.Name = path[k]
			nxt.Parent = cur
		end
		cur = nxt
	end
	cache[i] = cur
	return cur
end
local n = 0
for _, c in D do
	local ks = c[1]
	local p
	if ks == 3 then
		p = Instance.new("WedgePart")
	elseif ks == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = if ks == 1 then Enum.PartType.Ball elseif ks == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	end
	p.Name = c[15]
	p.Anchored = true
	p.Size = Vector3.new(c[9], c[10], c[11])
	p.CFrame = CFrame.new(c[3], c[4], c[5]) * CFrame.fromOrientation(c[6], c[7], c[8])
	p.Color = Color3.fromHex(c[12])
	p.Material = Enum.Material[M[c[13] + 1]]
	p.Transparency = c[14]
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = c[16] == 1
	p.Parent = grupa(c[2] + 1)
	n += 1
end
return n
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local wynik = {}
for _, a in f:GetChildren() do
	if a:IsA("Model") then
		local n = 0
		for _, d in a:GetDescendants() do
			if d:IsA("BasePart") then n += 1 end
		end
		a:SetAttribute("LiczbaCzesci", n - 1)
		table.insert(wynik, a.Name .. " " .. (n - 1))
	end
end
game:GetService("ChangeHistoryService"):SetWaypoint("ArenyWalki: zbudowano")
return table.concat(wynik, ", ")
'''


def luau(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(luau(x) for x in v) + "}"
    raise TypeError(type(v))


def dlugi_napis(tekst):
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def bez_komentarzy_na_poczatku(t):
    t = t.lstrip()
    while True:
        if t.startswith("--[["):
            k = t.find("]]")
            t = t[k + 2:].lstrip() if k >= 0 else ""
        elif t.startswith("--"):
            t = t.split("\n", 1)[1].lstrip() if "\n" in t else ""
        else:
            return t


def wczytaj_areny(tylko):
    areny = []
    for klucz, A in P.ARENY.items():
        if tylko and klucz not in tylko:
            continue
        with open(os.path.join(TU, klucz, "czesci.json"), encoding="utf-8") as f:
            d = json.load(f)
        with open(os.path.join(TU, klucz, "znaczniki.json"), encoding="utf-8") as f:
            z = json.load(f)
        if z["czesci"] != len(d["czesci"]) or z["scena"]["pozycja"] != list(A["O"]):
            sys.exit("%s: znaczniki.json niezgodne z czesci.json albo z planem — uruchom generuj.py" % klucz)
        korzenie = {g.split("/")[2] for g in d["grupy"]}
        if korzenie != {A["model"]} or any(not g.startswith("Workspace/%s/" % KONTENER) for g in d["grupy"]):
            sys.exit("%s: grupy czesci.json poza Workspace/%s/%s" % (klucz, KONTENER, A["model"]))
        areny.append((klucz, A, d, z))
    return areny


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje Workspace/ArenyWalki w Roblox Studio")
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--usun", action="store_true")
    ap.add_argument("--moduly", action="store_true")
    ap.add_argument("--tylko", default="")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    tylko = [k for k in a.tylko.split(",") if k]
    for k in tylko:
        if k not in P.ARENY:
            sys.exit("nie ma areny %r (są: %s)" % (k, ", ".join(P.ARENY)))
    moduly = []
    for plik, nazwa in MODULY:
        with open(os.path.join(TU, plik), encoding="utf-8-sig") as f:
            tekst = f.read().replace("\r\n", "\n")
        if not bez_komentarzy_na_poczatku(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s nie zaczyna się od strażnika Studio" % plik)
        moduly.append((nazwa, tekst, plik))
    areny = [] if a.moduly else wczytaj_areny(tylko)
    pudla = []
    for klucz, A, d, z in (wczytaj_areny([]) if not a.moduly else []):
        s, r = z["pudlo"]["srodek"], z["pudlo"]["rozmiar"]
        pudla.append([s[0], s[1], s[2], r[0], r[1], r[2]])
    print("Kontener: Workspace/%s · moduły: %s" % (KONTENER, ", ".join("%s (%d znaków)" % (n, len(t)) for n, t, _ in moduly)))
    for klucz, A, d, z in areny:
        print("  %-6s → Workspace/%s/%s (Persistent): %d części + znacznik Scena w %s · pudło %s × %s"
              % (klucz, KONTENER, A["model"], len(d["czesci"]), A["O"], z["pudlo"]["srodek"], z["pudlo"]["rozmiar"]))
    if a.sucho:
        return
    from studio_mcp import StudioMCP, StudioError
    from cel_studio import MIEJSCE, wybierz_studio
    try:
        with StudioMCP() as s:
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — przerywam.\n" + stan)

            def wykonaj(kod):
                kod = ('if game.PlaceId ~= %d then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                       % MIEJSCE) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            t0 = time.time()
            odbuduj = [A["model"] for _, A, _, _ in areny]
            print("start:", wykonaj(START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if a.usun else "false")
                                     .replace("__PUDLA__", luau(pudla)).replace("__ODBUDUJ__", luau(odbuduj))
                                     .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S"))))
            if a.usun:
                return
            for nazwa, tekst, plik in moduly:
                print("  moduł:", wykonaj(MODUL.replace("__KONTENER__", KONTENER).replace("__NAZWA__", nazwa)
                                           .replace("__ZRODLO__", dlugi_napis(tekst))))
            for klucz, A, d, z in areny:
                print("  arena %s:" % klucz, wykonaj(ARENA.replace("__KONTENER__", KONTENER).replace("__MODEL__", A["model"])
                                                     .replace("__BIOM__", A["biom"]).replace("__NAZWA__", A["nazwa"])
                                                     .replace("__CZAS__", time.strftime("%Y-%m-%dT%H:%M:%S"))
                                                     .replace("__O__", ", ".join(repr(float(v)) for v in A["O"]))))
                razem = 0
                for i in range(0, len(d["czesci"]), PACZKA):
                    paczka = []
                    for c in d["czesci"][i:i + PACZKA]:
                        cechy = int(c[15]) if len(c) > 15 else 0
                        paczka.append(list(c[:15]) + [0 if cechy & 2 else 1])
                    n = wykonaj(CZESCI.replace("__KONTENER__", KONTENER).replace("__GRUPY__", luau(d["grupy"]))
                                .replace("__MATERIALY__", luau(d["materialy"])).replace("__DANE__", luau(paczka)))
                    razem += int(float(n))
                print("    %d / %d części" % (razem, len(d["czesci"])), flush=True)
            print("gotowe: %s (%.0f s)" % (wykonaj(KONIEC.replace("__KONTENER__", KONTENER)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
