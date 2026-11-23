#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pet Arena w Roblox Studio (D-118, etap 1): cała gra we własnym kontenerze Workspace/PetArenaGra, we własnym (pustym)
miejscu — plik lokalny PetArena.rbxlx. Wzór: swiat/bonk/zbuduj.py (skopiowany i przerobiony).

    python -B swiat/pet_arena/zbuduj.py --sucho          # bez Studio: dane, kontrola Luau, plan budowy
    python -B swiat/pet_arena/zbuduj.py                  # buduje / odbudowuje wszystko (scena ok. 600 części, wzorce, skrypty)
    python -B swiat/pet_arena/zbuduj.py --skrypty        # tylko moduły i skrypty (scena i wzorce zostają)
    python -B swiat/pet_arena/zbuduj.py --stan           # odczyt: co stoi w kontenerze
    python -B swiat/pet_arena/zbuduj.py --wlacz on|off   # wyłącznik PetArenaWlaczony
    python -B swiat/pet_arena/zbuduj.py --usun           # usuwa własny kontener (cudzy obiekt o tej nazwie zostaje)
    python -B swiat/pet_arena/zbuduj.py --publikacja     # skrypty bez strażnika IsStudio (prywatna wersja testowa — decyzja ludzi)
    --studio <id>   okno Studio (domyślnie jedyne okno z „PetArena” w nazwie)

Zasady: nigdy w miejscu obecnej gry (placeId B&C — odmowa), tylko tryb Edit, tylko własny kontener z atrybutem
Wygenerowane; punkty historii przed i po; niczego nie zapisuje ani nie publikuje (zapis pliku: narzędzie save_place
po udanej budowie, osobno). Miejsce jest nasze i puste, więc budowa ustawia też SpawnLocation (w kontenerze) i
Lighting (pora dnia, jasność, Atmosphere, Sky) — wartości z ustawienia.json → scena.swiatlo / atmosfera.
"""
import argparse
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
for _s in (REPO, os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
    if _s not in sys.path:
        sys.path.append(_s)
if TU in sys.path:
    sys.path.remove(TU)
sys.path.insert(0, TU)
import dane as DN  # noqa: E402

ZRODLA = os.path.join(TU, "zrodla")
MODULY = ("LogikaPetArena", "EfektyPetArena", "InterfejsPetArena", "OknaPetArena")      # obok wygenerowanego DanePetArena
SKRYPTY = (("SerwerPetArena", "SerwerPetArena.server.luau", "Server"), ("KlientPetArena", "KlientPetArena.client.luau", "Client"))
ZDALNE = ("Akcja", "Zdarzenia")                               # RemoteEvent
NIEPEWNE = ("Stan",)                                          # UnreliableRemoteEvent (migawki petów)
LOKALNE = ("SterowanieSerwera", "SterowanieKlienta")          # BindableFunction (haczyki prób)
PACZKA = 300
GALERIA_Y = -60                                               # wzorce w Edit: pod sceną (w grze serwer przenosi je do RS)
MIEJSCE_GRY = 129485428021967                                 # placeId obecnej gry B&C (swiat/test_walki_roblox/cel_studio.py)

WSTEP = r'''
if game.PlaceId == __MIEJSCE_GRY__ then
	return "STOP: to miejsce obecnej gry B&C — Pet Arena buduje się tylko we własnym miejscu"
end
if game:GetService("RunService"):IsRunning() then
	return "STOP: Studio nie jest w trybie Edit — nic nie zmieniono"
end
local KONTENER = "__KONTENER__"
local function kontenery()
	local nasze, obce = {}, {}
	for _, d in workspace:GetChildren() do
		if d.Name == KONTENER then
			table.insert(if d:GetAttribute("Wygenerowane") == true then nasze else obce, d)
		end
	end
	return nasze, obce
end
local function kontener()
	local nasze, obce = kontenery()
	if #obce > 0 then
		return nil, string.format("STOP: w Workspace jest %d obiekt(ów) '%s' bez atrybutu Wygenerowane — nie ruszam cudzej pracy", #obce, KONTENER)
	end
	if #nasze > 1 then
		return nil, string.format("STOP: w Workspace są %d kontenery '%s' — usuń je (--usun) i zbuduj od nowa", #nasze, KONTENER)
	end
	return nasze[1], nil
end
local function folder(rodzic, nazwa, klasa)
	local f = rodzic:FindFirstChild(nazwa)
	if not f then
		f = Instance.new(klasa or "Folder")
		f.Name = nazwa
		f.Parent = rodzic
	end
	return f
end
'''

START = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("PetArenaGra: przed budową")
if not kont then
	kont = Instance.new("Folder")
	kont.Name = KONTENER
	kont:SetAttribute("Wygenerowane", true)
	kont.Parent = workspace
end
local zostaw = {}
if __TYLKO_SKRYPTY__ then
	zostaw = { Scena = true, Wzorce = true, Start = true, Stanowisko = true, Tablice = true }
end
for _, d in kont:GetChildren() do
	if not zostaw[d.Name] then
		d:Destroy()
	end
end
kont:SetAttribute("Zrodlo", "swiat/pet_arena")
kont:SetAttribute("Zbudowano", "__CZAS__")
kont:SetAttribute("Skrot", "__SKROT__")
kont:SetAttribute("Publikacja", __PUBLIKACJA__)
if kont:GetAttribute("__WYLACZNIK__") == nil then
	kont:SetAttribute("__WYLACZNIK__", true)
end
for _, a in { "SerwerGotowy", "KlientGotowy", "WzorceGotowe", "ZapisStan", "EmulacjaEkranu" } do
	kont:SetAttribute(a, nil)
end
folder(kont, "Moduly")
local s = folder(kont, "Sygnaly")
for _, d in s:GetChildren() do
	d:Destroy()
end
for _, n in { __ZDALNE__ } do
	local r = Instance.new("RemoteEvent")
	r.Name = n
	r.Parent = s
end
for _, n in { __NIEPEWNE__ } do
	local r = Instance.new("UnreliableRemoteEvent")
	r.Name = n
	r.Parent = s
end
for _, n in { __LOKALNE__ } do
	local b = Instance.new("BindableFunction")
	b.Name = n
	b.Parent = s
end
-- pusty Baseplate / domyślny SpawnLocation miejsca (gdyby był) wyłączony — start jest w kontenerze
for _, d in workspace:GetChildren() do
	if d:IsA("SpawnLocation") and d.Enabled then
		d.Enabled = false
	end
end
return "kontener gotowy"
'''

ZRODLO = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
if not kont then
	return "STOP: brak kontenera Workspace/" .. KONTENER
end
local rodzic = if "__RODZIC__" == "" then kont else kont:FindFirstChild("__RODZIC__")
if not rodzic then
	return "STOP: brak folderu __RODZIC__"
end
local stary = rodzic:FindFirstChild("__NAZWA__")
if stary then
	stary:Destroy()
end
local s = Instance.new("__KLASA__")
s.Name = "__NAZWA__"
if s:IsA("Script") then
	s.RunContext = Enum.RunContext.__KONTEKST__
end
s.Source = __TEKST__
s.Parent = rodzic
return string.format("__NAZWA__: %d bajtów", #s.Source)
'''

# wzorzec peta: zakotwiczony korzeń „Korzen” (punkt obrotu = ziemia pod petem), bryły przyspawane do korzenia
WZORZEC = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local wz = folder(kont, "Wzorce")
local stary = wz:FindFirstChild(D.klucz)
if stary then
	stary:Destroy()
end
local baza = CFrame.new(D.poz[1], D.poz[2], D.poz[3])
local m = Instance.new("Model")
m.Name = D.klucz
m:SetAttribute("Nazwa", D.nazwa)
local korzen = Instance.new("Part")
korzen.Name = "Korzen"
korzen.Size = Vector3.new(1, 1, 1)
korzen.Transparency = 1
korzen.Anchored = true
korzen.CanCollide = false
korzen.CanTouch = false
korzen.CanQuery = false
korzen.CastShadow = false
korzen.CFrame = baza
korzen.Parent = m
m.PrimaryPart = korzen
local KSZ = { [0] = Enum.PartType.Block, [1] = Enum.PartType.Ball, [2] = Enum.PartType.Cylinder }
for _, c in D.bryly do
	local p
	if c[1] == 3 then
		p = Instance.new("WedgePart")
	elseif c[1] == 4 then
		p = Instance.new("CornerWedgePart")
	else
		p = Instance.new("Part")
		p.Shape = KSZ[c[1]] or Enum.PartType.Block
	end
	p.Size = Vector3.new(c[8], c[9], c[10])
	p.CFrame = baza * CFrame.new(c[2], c[3], c[4]) * CFrame.fromOrientation(c[5], c[6], c[7])
	p.Color = Color3.fromHex(c[11])
	p.Material = Enum.Material[c[12]]
	p.Reflectance = c[13]
	p.Anchored = false
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Massless = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	if c[14] ~= "" then
		local sm = Instance.new("SpecialMesh")
		sm.MeshType = Enum.MeshType[c[14]]
		sm.Parent = p
	end
	local w = Instance.new("WeldConstraint")
	w.Part0 = korzen
	w.Part1 = p
	w.Parent = p
	p.Parent = m
end
m.Parent = wz
return string.format("wzorzec %s: %d brył", D.klucz, #D.bryly)
'''

SCENA_START = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local stara = kont:FindFirstChild("Scena")
if stara then
	stara:Destroy()
end
local m = Instance.new("Folder")
m.Name = "Scena"
m.Parent = kont
return "OK"
'''

SCENA_PACZKA = WSTEP + r'''
local Dn = __DANE__
local kont = kontener()
local sc = kont and kont:FindFirstChild("Scena")
if not sc then
	return "STOP: brak Scena w kontenerze"
end
local n = 0
for _, c in Dn do
	local g = sc:FindFirstChild(c[2])
	if not g then
		g = Instance.new("Model")
		g.Name = c[2]
		g.Parent = sc
	end
	local p = Instance.new("Part")
	p.Shape = if c[1] == 1 then Enum.PartType.Ball elseif c[1] == 2 then Enum.PartType.Cylinder else Enum.PartType.Block
	p.Name = c[16]
	p.Anchored = true
	p.Size = Vector3.new(c[9], c[10], c[11])
	p.CFrame = CFrame.new(c[3], c[4], c[5]) * CFrame.fromOrientation(c[6], c[7], c[8])
	p.Color = Color3.fromHex(c[12])
	p.Material = Enum.Material[c[13]]
	p.Transparency = c[14]
	p.CanCollide = c[15] == 1
	p.CanTouch = false
	p.CanQuery = c[14] < 1
	p.CastShadow = c[14] < 0.5
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = g
	n += 1
end
return n
'''

# napisy makiet (jajka, mata), SpawnLocation na pierwszym slocie, światło i niebo (puste miejsce — tylko nasze)
OTOCZENIE = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local sc = kont:FindFirstChild("Scena")
for _, n in { "Start", "Stanowisko", "Tablice" } do
	local stare = kont:FindFirstChild(n)
	if stare then
		stare:Destroy()
	end
end
local stan = Instance.new("Folder")
stan.Name = "Stanowisko"
stan.Parent = kont
-- jajka z wzorców na cokołach stanowiska (zakotwiczone kopie)
local wz = kont:FindFirstChild("Wzorce")
for i, J in D.jajka do
	local w = wz and wz:FindFirstChild(J.wzorzec)
	if w then
		local m = w:Clone()
		m.Name = "Jajko" .. i
		m:PivotTo(CFrame.new(J.poz[1], J.poz[2], J.poz[3]) * CFrame.Angles(0, math.rad(J.obrot), 0))
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				d.Anchored = true
			end
		end
		m.Parent = stan
	end
end
-- tablice wyników na ścianie dołu (wiersze uzupełnia serwer)
local tab = Instance.new("Folder")
tab.Name = "Tablice"
tab.Parent = kont
for _, T in D.tablice do
	local cf = CFrame.lookAt(Vector3.new(T.poz[1], T.poz[2], T.poz[3]), Vector3.new(T.patrz[1], T.patrz[2], T.patrz[3]))
	local m = Instance.new("Model")
	m.Name = "Tablica" .. T.nr
	local p = Instance.new("Part")
	p.Name = "Tablica"
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.Size = Vector3.new(T.szer, T.wys, 0.4)
	p.CFrame = cf
	p.Color = Color3.fromHex("1B1424")
	p.Parent = m
	local sg = Instance.new("SurfaceGui")
	sg.Name = "Ekran"
	sg.Face = Enum.NormalId.Front
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 30
	sg.LightInfluence = 0
	sg.Parent = p
	local lista = Instance.new("UIListLayout")
	lista.SortOrder = Enum.SortOrder.LayoutOrder
	lista.Padding = UDim.new(0.01, 0)
	lista.Parent = sg
	local function linia(nazwa, tekst, wys, kolor, nr)
		local l = Instance.new("TextLabel")
		l.Name = nazwa
		l.LayoutOrder = nr
		l.BackgroundTransparency = 1
		l.Size = UDim2.fromScale(1, wys)
		l.Text = tekst
		l.TextScaled = true
		l.Font = if nr == 0 then Enum.Font.LuckiestGuy else Enum.Font.FredokaOne
		l.TextColor3 = Color3.fromHex(kolor)
		l.Parent = sg
	end
	linia("Tytul", T.tytul, 0.2, "FFC83D", 0)
	for r = 1, T.wierszy do
		linia("Rzad" .. r, "", 0.78 / T.wierszy, "FFF6E0", r)
	end
	m.Parent = tab
end
-- v3: tytuł gry nad bramą (atrapa)
if D.tytul then
	local T = D.tytul
	local p = Instance.new("Part")
	p.Name = "TytulGry"
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.Size = Vector3.new(T.szer, T.wys, 0.6)
	p.CFrame = CFrame.lookAt(Vector3.new(T.poz[1], T.poz[2], T.poz[3]), Vector3.new(T.patrz[1], T.patrz[2], T.patrz[3]))
	p.Color = Color3.fromHex("2A1A3A")
	p.Material = Enum.Material.SmoothPlastic
	p.Parent = tab
	local sg = Instance.new("SurfaceGui")
	sg.Name = "Ekran"
	sg.Face = Enum.NormalId.Front
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 30
	sg.LightInfluence = 0
	sg.Parent = p
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Text = T.tekst
	l.TextScaled = true
	l.Font = Enum.Font.LuckiestGuy
	l.TextColor3 = Color3.fromHex("FFC83D")
	l.TextStrokeTransparency = 0
	l.TextStrokeColor3 = Color3.fromHex("1B1424")
	l.Parent = sg
end
for _, N in D.napisy do
	local cf = CFrame.lookAt(Vector3.new(N.poz[1], N.poz[2], N.poz[3]), Vector3.new(N.patrz[1], N.patrz[2], N.patrz[3]))
	local t = Instance.new("Part")
	t.Name = "Tablica"
	t.Anchored = true
	t.CanCollide = false
	t.CanTouch = false
	t.Size = Vector3.new(N.szer or 11, N.wys or 3, 0.4)
	t.CFrame = cf
	t.Color = Color3.fromHex("1B1424")
	t.Material = Enum.Material.SmoothPlastic
	t.Parent = sc and sc:FindFirstChild("Makiety") or kont
	for _, sx in { -5, 5 } do
		local s = Instance.new("Part")
		s.Name = "Noga"
		s.Anchored = true
		s.CanCollide = false
		s.CanTouch = false
		s.Size = Vector3.new(0.5, 4.4, 0.5)
		s.CFrame = cf * CFrame.new(sx * (N.szer or 11) / 11, -(N.wys or 3) / 2 - 1.1, 0)
		s.Color = Color3.fromHex("5E3A1A")
		s.Material = Enum.Material.Wood
		s.Parent = t.Parent
	end
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Back
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40
	sg.LightInfluence = 0
	sg.Parent = t
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Text = N.tekst
	l.TextScaled = true
	l.Font = Enum.Font.LuckiestGuy
	l.TextColor3 = Color3.fromHex("FFC83D")
	l.Parent = sg
end
for _, N in D.strefy do
	local t = Instance.new("Part")
	t.Name = "NapisStrefy"
	t.Anchored = true
	t.CanCollide = false
	t.CanTouch = false
	t.CanQuery = false
	t.CastShadow = false
	t.Transparency = 1
	t.Size = Vector3.new(N.wielkosc, 0.1, N.wielkosc * 0.6)
	t.CFrame = CFrame.new(N.poz[1], N.poz[2], N.poz[3]) * CFrame.Angles(0, N.r + math.pi, 0)
	t.Parent = sc and sc:FindFirstChild("Arena") or kont
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40
	sg.LightInfluence = 0.3
	sg.Parent = t
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Text = N.tekst
	l.TextScaled = true
	l.Font = Enum.Font.LuckiestGuy
	l.TextColor3 = Color3.fromHex("FFF6E0")
	l.TextTransparency = 0.15
	l.Parent = sg
	local o = Instance.new("UIStroke")
	o.Thickness = 3
	o.Color = Color3.fromHex("1B1424")
	o.Transparency = 0.3
	o.Parent = l
end
local st = Instance.new("SpawnLocation")
st.Name = "Start"
st.Anchored = true
st.Neutral = true
st.Duration = 0
st.Size = Vector3.new(4, 0.4, 4)
st.CFrame = CFrame.new(D.start[1], D.start[2] + 0.2, D.start[3])
st.Transparency = 1
st.CanCollide = true
st.CanTouch = true
st.Parent = kont
local L = game:GetService("Lighting")
for k, v in D.swiatlo do
	if type(v) == "string" then
		L[k] = Color3.fromHex(v)
	else
		L[k] = v
	end
end
local at = L:FindFirstChildOfClass("Atmosphere") or Instance.new("Atmosphere")
for k, v in D.atmosfera do
	if type(v) == "string" then
		at[k] = Color3.fromHex(v)
	else
		at[k] = v
	end
end
at.Parent = L
if not L:FindFirstChildOfClass("Sky") then
	local sky = Instance.new("Sky")
	sky.Parent = L
end
return string.format("otoczenie: %d tablice, start, światło (ClockTime %.1f)", #D.napisy, L.ClockTime)
'''

KONIEC = WSTEP + r'''
local kont = kontener()
if kont then
	game:GetService("ChangeHistoryService"):SetWaypoint("PetArenaGra: zbudowano")
end
return "punkt historii"
'''

USUN = WSTEP + r'''
local nasze, obce = kontenery()
local zostawione = ""
if #obce > 0 then
	zostawione = string.format("; zostawiono %d obiekt(ów) '%s' bez atrybutu Wygenerowane (cudza praca, nie ruszam)", #obce, KONTENER)
end
if #nasze == 0 then
	return (if #obce > 0 then "STOP: nic nie usunięto" else "nie ma czego usuwać") .. zostawione
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("PetArenaGra: przed usunięciem")
for _, k in nasze do
	k:Destroy()
end
CH:SetWaypoint("PetArenaGra: usunięto")
return string.format("USUNIĘTO %d × Workspace/%s%s", #nasze, KONTENER, zostawione)
'''

ATRYBUT = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
if not kont then
	return "STOP: brak kontenera — najpierw zbuduj.py"
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("PetArenaGra: przed __ATR__")
kont:SetAttribute("__ATR__", __WARTOSC__)
CH:SetWaypoint("PetArenaGra: __ATR__")
return "__ATR__ = " .. tostring(kont:GetAttribute("__ATR__"))
'''

STAN = r'''
local HS = game:GetService("HttpService")
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, atrybuty = {}, zrodla = {}, sygnaly = {}, wzorce = {}, czesciSceny = 0 }
for n, v in kont:GetAttributes() do
	w.atrybuty[n] = if typeof(v) == "Vector3" then { v.X, v.Y, v.Z } elseif typeof(v) == "Vector2" then { v.X, v.Y } else v
end
for _, d in kont:GetDescendants() do
	if d:IsA("LuaSourceContainer") then
		w.zrodla[d.Name] = { klasa = d.ClassName, bajtow = #d.Source, kontekst = if d:IsA("Script") then d.RunContext.Name else nil }
	end
end
for _, d in (kont:FindFirstChild("Sygnaly") or kont):GetChildren() do
	if d:IsA("RemoteEvent") or d:IsA("UnreliableRemoteEvent") or d:IsA("BindableFunction") then
		table.insert(w.sygnaly, d.Name)
	end
end
local wz = kont:FindFirstChild("Wzorce")
if wz then
	for _, m in wz:GetChildren() do
		local n = 0
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				n += 1
			end
		end
		w.wzorce[m.Name] = n
	end
end
local sc = kont:FindFirstChild("Scena")
if sc then
	for _, d in sc:GetDescendants() do
		if d:IsA("BasePart") and d.Name ~= "Tablica" and d.Name ~= "Noga" and d.Name ~= "NapisStrefy" then
			w.czesciSceny += 1
		end
	end
end
local st = kont:FindFirstChild("Start")
w.start = st ~= nil and st:IsA("SpawnLocation")
w.zegar = game:GetService("Lighting").ClockTime
return HS:JSONEncode(w)
'''


def log(*a):
    print("PetArena |", *a, flush=True)


def wstaw(szablon, **w):
    for k, v in w.items():
        szablon = szablon.replace("__%s__" % k, v)
    return szablon


def czytaj(nazwa):
    with open(os.path.join(ZRODLA, nazwa), encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")


def bez_straznika(tekst):
    """--publikacja: usuwa blok strażnika Studio (pierwsza instrukcja `if not …IsStudio() then` … `end` w kolumnie 0)."""
    i = tekst.find(DN.STRAZNIK)
    if i < 0:
        raise ValueError("brak strażnika Studio")
    k = tekst.find("\nend\n", i)
    if k < 0:
        raise ValueError("strażnik bez `end` w kolumnie 0")
    return tekst[:i] + "-- (publikacja: bez strażnika Studio)\n" + tekst[k + 5:]


def zrodla(pliki, publikacja=False):
    """Wszystko, co trafia do Studio: [(folder w kontenerze, nazwa, klasa, kontekst, tekst)]."""
    w = [("Moduly", "DanePetArena", "ModuleScript", "", pliki[DN.PLIK_DANYCH])]
    w += [("Moduly", n, "ModuleScript", "", czytaj(n + ".luau")) for n in MODULY]
    w += [("", nazwa, "Script", kontekst, czytaj(plik)) for nazwa, plik, kontekst in SKRYPTY]
    if publikacja:
        w = [(r, n, k, c, bez_straznika(t)) for r, n, k, c, t in w]
    return w


def pliki_luau():
    return ([os.path.join(ZRODLA, n + ".luau") for n in MODULY] + [os.path.join(ZRODLA, p) for _, p, _ in SKRYPTY]
            + [os.path.join(ZRODLA, DN.PLIK_DANYCH)])


def kontrola_luau():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "kontrola_luau_potworow", os.path.join(REPO, "swiat", "las_potwory", "sprawdz_luau.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sprawdz_zrodla():
    return kontrola_luau().sprawdz_pliki(pliki_luau(), wypisz=lambda t: None)


def wzorce_wszystkie(U):
    return sorted(DN.wzorce(U).items())


def oczekiwane_wzorce(U):
    return {n: len(d["bryly"]) + 1 for n, d in wzorce_wszystkie(U)}


def dane_otoczenia(U, D):
    S = U["scena"]
    st = DN.stanowisko_jajek(U)
    jajka = [{"wzorzec": J["wzorzec"], "poz": [x, U["scena"]["mur_y"] + 1.3, z], "obrot": 180 + U["scena"]["jajka_kat_st"]}
             for J, (x, z) in zip(D["jajka"], st["cokoly"])]
    # v3: tytuł gry (atrapa) nad kratą bramy, przodem do areny
    a = math.radians(S["brama_kat_st"])
    r = S["mur_r"][0] - 1.2
    tytul = {"tekst": U["ui"]["tytul_gry"], "poz": [round(math.sin(a) * r, 3), S["brama_wys"] - 2.5, round(math.cos(a) * r, 3)],
             "patrz": [0, S["brama_wys"] - 2.5, 0], "szer": 26, "wys": 4.6}
    return {"napisy": DN.makiety_napisy(U), "strefy": DN.etykiety_stref(U), "jajka": jajka, "tablice": D["tablice"], "start": D["sloty"][0]["poz"],
            "swiatlo": S["swiatlo"], "atmosfera": S["atmosfera"], "tytul": tytul}


def plan(U, D, Z, scena):
    W = wzorce_wszystkie(U)
    return ["do Studio: %d modułów i skryptów (%d kB), sygnały: %s" % (
        len(Z), sum(len(t.encode("utf-8")) for *_, t in Z) // 1000, ", ".join(ZDALNE + NIEPEWNE + LOKALNE)),
        "wzorce petów: %d, %d brył" % (len(W), sum(len(d["bryly"]) for _, d in W)),
        "scena: %d części (koloseum: arena r %s, mur %s, trybuny do r %s)" % (len(scena), U["scena"]["arena_r"], U["scena"]["mur_r"],
                                                                            U["scena"]["trybuna_r"])]


def wybierz_okno(s, studio):
    okna = json.loads(s.call("list_roblox_studios", {})["text"] or "[]")
    if isinstance(okna, dict):
        okna = okna.get("studios") or okna.get("instances") or []
    if studio:
        if not any(o.get("id") == studio for o in okna):
            raise SystemExit("brak okna Studio o id %s" % studio)
        return studio
    nasze = [o for o in okna if "PetArena" in (o.get("name") or "") + (o.get("file") or "")]
    if len(nasze) != 1:
        raise SystemExit("podaj --studio <id>: okien z „PetArena” w nazwie jest %d" % len(nasze))
    return nasze[0]["id"]


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Pet Arena w Studio: Workspace/PetArenaGra")
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--skrypty", action="store_true")
    ap.add_argument("--stan", action="store_true")
    ap.add_argument("--usun", action="store_true")
    ap.add_argument("--wlacz", choices=["on", "off"])
    ap.add_argument("--publikacja", action="store_true")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    try:
        U, D, pliki = DN.wszystkie_pliki()
        scena = DN.scena(U)
    except DN.BladDanych as e:
        log("BŁĄD danych:", e)
        return 2
    zle = DN.nieaktualne(pliki)
    if zle:
        log("BŁĄD: nieaktualne dane (%s) — uruchom python -B swiat/pet_arena/dane.py" % ", ".join(zle))
        return 1
    Z = zrodla(pliki, a.publikacja)
    bledy = sprawdz_zrodla()
    bledy += ["%s: %d znaków ponad limit %d" % (n, len(t), U["limit_zrodla"]) for _, n, _, _, t in Z if len(t) > U["limit_zrodla"]]
    for b in bledy:
        log("BŁĄD źródeł:", b)
    for linia in DN.tabela(U, D) + plan(U, D, Z, scena):
        log(linia)
    log("źródła Luau: %s%s" % ("bez błędów" if not bledy else "%d błędów" % len(bledy),
                              "; PUBLIKACJA: bez strażnika Studio" if a.publikacja else ""))
    if bledy:
        return 1
    if a.sucho:
        return 0
    from studio_mcp import StudioMCP  # noqa: E402
    wspolne = dict(MIEJSCE_GRY=str(MIEJSCE_GRY), KONTENER=U["kontener"])
    with StudioMCP(timeout=240) as s:
        sid = wybierz_okno(s, a.studio)
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit; nic nie zmieniono")
            return 1

        def wykonaj(kod, opis, timeout=240):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=timeout)
            tekst = (r["text"] or "").strip()
            if r["is_error"] or tekst.startswith("STOP"):
                log("PRZERWANO — Studio odmówiło (%s): %s" % (opis, tekst[:600]))
                raise SystemExit(1)
            return tekst

        if a.stan:
            print(json.dumps(json.loads(wykonaj(wstaw(STAN, KONTENER=U["kontener"]), "stan")), ensure_ascii=False, indent=1))
            return 0
        if a.usun:
            log(wykonaj(wstaw(USUN, **wspolne), "usuwanie"))
            return 0
        if a.wlacz:
            log(wykonaj(wstaw(ATRYBUT, ATR=U["wylacznik"], WARTOSC="true" if a.wlacz == "on" else "false", **wspolne), "wyłącznik"))
            return 0
        t0 = time.time()
        log(wykonaj(wstaw(START, CZAS=time.strftime("%Y-%m-%d %H:%M"), SKROT=D["skrot"], WYLACZNIK=U["wylacznik"],
                          TYLKO_SKRYPTY="true" if a.skrypty else "false", PUBLIKACJA="true" if a.publikacja else "false",
                          ZDALNE=", ".join(json.dumps(n) for n in ZDALNE), NIEPEWNE=", ".join(json.dumps(n) for n in NIEPEWNE),
                          LOKALNE=", ".join(json.dumps(n) for n in LOKALNE), **wspolne), "start"))
        for rodzic, nazwa, klasa, kontekst, tekst in Z:
            log(wykonaj(wstaw(ZRODLO, RODZIC=rodzic, NAZWA=nazwa, KLASA=klasa, KONTEKST=kontekst or "Legacy",
                              TEKST=DN.luau(tekst), **wspolne), nazwa))
        if not a.skrypty:
            log(wykonaj(wstaw(SCENA_START, **wspolne), "scena"))
            razem = 0
            for i in range(0, len(scena), PACZKA):
                razem += int(float(wykonaj(wstaw(SCENA_PACZKA, DANE=DN.luau(scena[i:i + PACZKA]), **wspolne), "scena")))
            log("scena: %d części" % razem)
            for i, (klucz, d) in enumerate(wzorce_wszystkie(U)):
                dd = {"klucz": klucz, "nazwa": d["nazwa"], "bryly": d["bryly"], "poz": [-60 + 11 * i, GALERIA_Y, 0]}
                log(wykonaj(wstaw(WZORZEC, DANE=DN.luau(dd), **wspolne), "wzorzec " + klucz))
            log(wykonaj(wstaw(OTOCZENIE, DANE=DN.luau(dane_otoczenia(U, D)), **wspolne), "otoczenie"))
        wykonaj(wstaw(KONIEC, **wspolne), "koniec")
        stan = json.loads(wykonaj(wstaw(STAN, KONTENER=U["kontener"]), "stan"))
        niezgodne = []
        for _, nazwa, klasa, kontekst, tekst in Z:
            m = stan["zrodla"].get(nazwa)
            if not m or m["klasa"] != klasa or m["bajtow"] != len(tekst.encode("utf-8")) or (kontekst and m.get("kontekst") != kontekst):
                niezgodne.append(nazwa)
        if sorted(stan["sygnaly"]) != sorted(ZDALNE + NIEPEWNE + LOKALNE) or stan["atrybuty"].get("Skrot") != D["skrot"]:
            niezgodne.append("sygnały albo skrót")
        if stan["czesciSceny"] != len(scena):
            niezgodne.append("scena %d / %d części" % (stan["czesciSceny"], len(scena)))
        if stan["wzorce"] != oczekiwane_wzorce(U):
            niezgodne.append("wzorce (%d / %d)" % (len(stan["wzorce"]), len(oczekiwane_wzorce(U))))
        if not stan.get("start"):
            niezgodne.append("start")
        log("kontrola po budowie (%.0f s): %s" % (time.time() - t0, "zgodne — %d źródeł, skrót %s, scena %d części, wzorce %d, "
                                                 "start %s, ClockTime %s" % (len(stan["zrodla"]), stan["atrybuty"].get("Skrot"),
                                                                             stan["czesciSceny"], len(stan["wzorce"]), stan["start"],
                                                                             stan["zegar"])
                                                 if not niezgodne else "NIEZGODNE: " + ", ".join(niezgodne)))
        return 1 if niezgodne else 0


if __name__ == "__main__":
    sys.exit(main())
