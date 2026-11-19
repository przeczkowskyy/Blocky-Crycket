#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BONK w Roblox Studio (D-112, propozycja): cała gra we własnym kontenerze Workspace/BonkGra.

    python -B swiat/bonk/zbuduj.py --sucho        # bez Studio: dane, kontrola Luau, plan budowy
    python -B swiat/bonk/zbuduj.py --teren        # odczyt: czy obszar mapy BONK jest pusty (niczego nie zmienia)
    python -B swiat/bonk/zbuduj.py                # buduje / odbudowuje (mapa tylko, gdy jej nie ma)
    python -B swiat/bonk/zbuduj.py --mapa         # jak wyżej, ale mapę też buduje od nowa (ok. 15 tys. części)
    python -B swiat/bonk/zbuduj.py --skrypty      # tylko moduły i skrypty (mapa, wzorce, bramy i portale zostają)
    python -B swiat/bonk/zbuduj.py --stan         # odczyt: co stoi w kontenerze
    python -B swiat/bonk/zbuduj.py --autostart on|off   # atrybut AutoStart (on: gracz po wejściu do gry od razu w BONK)
    python -B swiat/bonk/zbuduj.py --wlacz on|off       # wyłącznik BonkWlaczony (off: serwer i klient BONK nic nie robią)
    python -B swiat/bonk/zbuduj.py --usun         # usuwa własny kontener (cudzy obiekt o tej nazwie zostaje)
    python -B swiat/bonk/zbuduj.py --publikacja --studio <id>   # do PUSTEGO miejsca: bez strażnika IsStudio, bez
                                                  # bramy przy starcie obecnej gry, AutoStart = true (nie miejsce gry!)

Zasady (wspólne miejsce Team Create): tylko miejsce gry (swiat/test_walki_roblox/cel_studio.py), tylko tryb Edit,
tylko własny kontener z atrybutem Wygenerowane; punkty historii przed i po; niczego nie zapisuje ani nie publikuje;
Lighting nietknięty. Brama BONK przy płycie startu stoi WE WŁASNYM kontenerze (Portal), w pierwszym wolnym miejscu
obok płyty (odczyt części w pudle). W grze BONK nie czyta innych kontenerów: mapa (z czesci.json pasów), wzorce
potworów (z swiat/test_walki2/dane), dane i identyfikatory dźwięków są kopiowane tu przy budowie.
"""
import argparse
import json
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
MODULY = ("LogikaBonk", "EfektyBonk", "InterfejsBonk", "OknaBonk")      # obok wygenerowanego DaneBonk
SKRYPTY = (("SerwerBonk", "SerwerBonk.server.luau", "Server"), ("KlientBonk", "KlientBonk.client.luau", "Client"))
ZDALNE = ("Bonk", "Zdarzenia", "Akcja")                      # RemoteEvent
LOKALNE = ("SterowanieSerwera", "SterowanieKlienta")         # BindableFunction (haczyki prób)
PACZKA_MAPY = 400
GALERIA_Y = -90                                              # wzorce w Edit: pod mapą (w grze serwer przenosi je do RS)

WSTEP = r'''
if __WARUNEK_MIEJSCA__ then
	return "STOP: __OPIS_MIEJSCA__ — nic nie zmieniono"
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
local function czesc(rodzic, nazwa, rozmiar, cf, kolor, material)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = cf
	p.Color = kolor
	p.Material = material or Enum.Material.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanTouch = false
	p.Parent = rodzic
	return p
end
'''

START = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local CH = game:GetService("ChangeHistoryService")
CH:SetWaypoint("BonkGra: przed budową")
if not kont then
	kont = Instance.new("Folder")
	kont.Name = KONTENER
	kont:SetAttribute("Wygenerowane", true)
	kont.Parent = workspace
end
local zostaw = { Mapa = not __MAPA_OD_NOWA__ }
if __TYLKO_SKRYPTY__ then
	zostaw = { Mapa = true, Wzorce = true, Bramy = true, Portal = true, Powrot = true, Stanowiska = true }
end
for _, d in kont:GetChildren() do
	if not zostaw[d.Name] then
		d:Destroy()
	end
end
kont:SetAttribute("Zrodlo", "swiat/bonk")
kont:SetAttribute("Zbudowano", "__CZAS__")
kont:SetAttribute("Skrot", "__SKROT__")
kont:SetAttribute("Publikacja", __PUBLIKACJA__)
if kont:GetAttribute("__WYLACZNIK__") == nil then
	kont:SetAttribute("__WYLACZNIK__", true)
end
if __PUBLIKACJA__ then
	kont:SetAttribute("__AUTOSTART__", true)
elseif kont:GetAttribute("__AUTOSTART__") == nil then
	kont:SetAttribute("__AUTOSTART__", false)
end
for _, a in { "SerwerGotowy", "KlientGotowy", "WzorceGotowe", "ZapisStan", "ZapisMagazyn", "ZapisAktywny" } do
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
for _, n in { __LOKALNE__ } do
	local b = Instance.new("BindableFunction")
	b.Name = n
	b.Parent = s
end
return "kontener gotowy; mapa " .. (if kont:FindFirstChild("Mapa") then "zostaje" else "do budowy")
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

# wzorzec potwora: zakotwiczony korzeń „Korzen” (punkt obrotu = ziemia pod potworem), bryły przyspawane do korzenia
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

# bramy krain (niewidzialna ściana z napisem; klient otwiera ją u gracza z Mocą) i portal powrotu na starcie lasu
BRAMY = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local mapa = kont:FindFirstChild("Mapa")
local pr = RaycastParams.new()
pr.FilterType = Enum.RaycastFilterType.Include
pr.FilterDescendantsInstances = if mapa then { mapa } else {}
pr.RespectCanCollide = true
local function ziemia(x, y, z)
	local t = mapa and workspace:Raycast(Vector3.new(x, y + 30, z), Vector3.new(0, -60, 0), pr)
	return if t then t.Position.Y else y
end
local stare = kont:FindFirstChild("Bramy")
if stare then
	stare:Destroy()
end
local bramy = Instance.new("Folder")
bramy.Name = "Bramy"
for _, b in D.bramy do
	local y = ziemia(b.x - 6, b.y, b.z)
	local s = czesc(bramy, "Brama" .. b.nr, Vector3.new(2, b.wys, b.szer), CFrame.new(b.x, y + b.wys / 2, b.z), Color3.new(1, 1, 1))
	s.Transparency = 1
	s.CanQuery = false
	s.CastShadow = false
	local g = Instance.new("BillboardGui")
	g.Name = "Tablica"
	g.Size = UDim2.fromScale(30, 6)
	g.StudsOffsetWorldSpace = Vector3.new(0, 18 - b.wys / 2, 0)
	g.LightInfluence = 0
	g.MaxDistance = 220
	g.Parent = s
	local t = Instance.new("TextLabel")
	t.Name = "Napis"
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 1)
	t.Text = b.napis
	t.TextScaled = true
	t.Font = Enum.Font.LuckiestGuy
	t.TextColor3 = Color3.fromHex("FFF6E0")
	t.Parent = g
	local o = Instance.new("UIStroke")
	o.Thickness = 4
	o.Color = Color3.fromHex("1B1424")
	o.Parent = t
end
bramy.Parent = kont
-- portal powrotu (EXIT) na starcie lasu
local stary = kont:FindFirstChild("Powrot")
if stary then
	stary:Destroy()
end
local n = 0
if D.powrot then
	local p = D.powrot
	local y = ziemia(p.x, p.y, p.z)
	local m = Instance.new("Model")
	m.Name = "Powrot"
	local cf = CFrame.lookAt(Vector3.new(p.x, y, p.z), Vector3.new(p.x, y, p.z + 10))
	local kol, ciemny = Color3.fromHex(p.kolor), Color3.fromHex("3A2A1E")
	czesc(m, "SlupL", Vector3.new(1.2, 11, 1.2), cf * CFrame.new(-4, 5.5, 0), ciemny, Enum.Material.Wood)
	czesc(m, "SlupP", Vector3.new(1.2, 11, 1.2), cf * CFrame.new(4, 5.5, 0), ciemny, Enum.Material.Wood)
	local belka = czesc(m, "Belka", Vector3.new(10, 1.8, 1.6), cf * CFrame.new(0, 11.4, 0), ciemny, Enum.Material.Wood)
	local tafla = czesc(m, "Tafla", Vector3.new(6.8, 9.8, 0.3), cf * CFrame.new(0, 5.4, 0), kol, Enum.Material.Neon)
	tafla.Transparency = 0.45
	tafla.CanCollide = false
	tafla.CanQuery = false
	for _, strona in { Enum.NormalId.Front, Enum.NormalId.Back } do
		local sg = Instance.new("SurfaceGui")
		sg.Face = strona
		sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sg.PixelsPerStud = 40
		sg.LightInfluence = 0
		sg.Parent = belka
		local t = Instance.new("TextLabel")
		t.BackgroundTransparency = 1
		t.Size = UDim2.fromScale(1, 1)
		t.Text = p.napis
		t.TextScaled = true
		t.Font = Enum.Font.LuckiestGuy
		t.TextColor3 = Color3.fromHex("FFF6E0")
		t.Parent = sg
	end
	m.Parent = kont
	kont:SetAttribute("PowrotPoz", Vector3.new(p.x, y, p.z))
	n = 1
end
return string.format("bramy: %d, portal powrotu: %d", #D.bramy, n)
'''

# brama BONK przy płycie startu obecnej gry — pierwsze wolne miejsce (odczyt części w pudle), we własnym kontenerze
PORTAL = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local stary = kont:FindFirstChild("Portal")
if stary then
	stary:Destroy()
end
kont:SetAttribute("PortalPoz", nil)
kont:SetAttribute("PortalWyjscie", nil)
local spawny = {}
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") and d.Enabled and not d:IsDescendantOf(kont) then
		table.insert(spawny, d)
	end
end
if #spawny == 0 then
	return "UWAGA: brak SpawnLocation w Workspace — brama BONK nie postawiona"
end
table.sort(spawny, function(a, b)
	if a.Neutral ~= b.Neutral then
		return a.Neutral
	end
	return a.Position.Magnitude < b.Position.Magnitude
end)
local sp = spawny[1]
local gora = sp.Position + Vector3.new(0, sp.Size.Y / 2, 0)
local pr = RaycastParams.new()
pr.FilterType = Enum.RaycastFilterType.Exclude
pr.FilterDescendantsInstances = { kont }
pr.RespectCanCollide = true
local op = OverlapParams.new()
op.FilterType = Enum.RaycastFilterType.Exclude
op.FilterDescendantsInstances = { kont }
local roz = Vector3.new(D.rozmiar[1], D.rozmiar[2], D.rozmiar[3])
local wybrane = nil
local odrzucone = 0
for _, odl in D.odleglosci do
	for k = 0, 15 do
		local a = k * math.pi / 8
		local c = gora + Vector3.new(math.cos(a) * odl, 0, math.sin(a) * odl)
		local t = workspace:Raycast(c + Vector3.new(0, 12, 0), Vector3.new(0, -30, 0), pr)
		if t and math.abs(t.Position.Y - gora.Y) < 2.5 then
			local g = t.Position
			local cf = CFrame.lookAt(g, Vector3.new(gora.X, g.Y, gora.Z))
			local przeszkody = 0
			for _, p in workspace:GetPartBoundsInBox(cf * CFrame.new(0, roz.Y / 2 + 0.4, 0), roz + Vector3.new(3, 0, 3), op) do
				if p.Transparency < 1 or p.CanCollide then
					przeszkody += 1
				end
			end
			if przeszkody == 0 then
				wybrane = cf
				break
			end
			odrzucone += 1
		end
	end
	if wybrane then
		break
	end
end
if not wybrane then
	return string.format("UWAGA: przy płycie %s nie ma wolnego miejsca na bramę (sprawdzono %d) — nie postawiona", sp:GetFullName(), odrzucone)
end
local cf = wybrane
local m = Instance.new("Model")
m.Name = "Portal"
local kol, ciemny = Color3.fromHex(D.kolor), Color3.fromHex("3A2A1E")
local w = roz.X
czesc(m, "SlupL", Vector3.new(1.2, roz.Y, 1.2), cf * CFrame.new(-w / 2, roz.Y / 2, 0), ciemny, Enum.Material.Wood)
czesc(m, "SlupP", Vector3.new(1.2, roz.Y, 1.2), cf * CFrame.new(w / 2, roz.Y / 2, 0), ciemny, Enum.Material.Wood)
local belka = czesc(m, "Belka", Vector3.new(w + 2, 1.8, 1.6), cf * CFrame.new(0, roz.Y + 0.4, 0), ciemny, Enum.Material.Wood)
local tafla = czesc(m, "Tafla", Vector3.new(w - 1.2, roz.Y - 1.2, 0.3), cf * CFrame.new(0, roz.Y / 2 - 0.1, 0), kol, Enum.Material.Neon)
tafla.Transparency = 0.4
tafla.CanCollide = false
tafla.CanQuery = false
for _, strona in { Enum.NormalId.Front, Enum.NormalId.Back } do
	local sg = Instance.new("SurfaceGui")
	sg.Face = strona
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40
	sg.LightInfluence = 0
	sg.Parent = belka
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 1)
	t.Text = D.napis
	t.TextScaled = true
	t.Font = Enum.Font.LuckiestGuy
	t.TextColor3 = Color3.fromHex("FFF6E0")
	t.Parent = sg
end
m.Parent = kont
local poz = cf.Position
kont:SetAttribute("PortalPoz", poz)
kont:SetAttribute("PortalWyjscie", poz + cf.LookVector * 7)
return string.format("brama BONK przy płycie %s: (%.1f; %.1f; %.1f), %.0f st od płyty", sp:GetFullName(), poz.X, poz.Y, poz.Z,
	(Vector3.new(poz.X, gora.Y, poz.Z) - gora).Magnitude)
'''

# etap 2: inkubatory (jajko z brył na cokole + tablica jawnych szans), stoiska pałek, trzy tablice wyników (wiersze
# Rzad1…N wypełnia serwer). Wszystko zakotwiczone, we własnym kontenerze (Stanowiska).
STANOWISKA = WSTEP + r'''
local D = __DANE__
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local mapa = kont:FindFirstChild("Mapa")
local pr = RaycastParams.new()
pr.FilterType = Enum.RaycastFilterType.Include
pr.FilterDescendantsInstances = if mapa then { mapa } else {}
pr.RespectCanCollide = true
local function ziemia(x, y, z)
	local t = mapa and workspace:Raycast(Vector3.new(x, y + 30, z), Vector3.new(0, -60, 0), pr)
	return if t then t.Position.Y else y
end
local stare = kont:FindFirstChild("Stanowiska")
if stare then
	stare:Destroy()
end
local st = Instance.new("Folder")
st.Name = "Stanowiska"
local KSZ = { [0] = Enum.PartType.Block, [1] = Enum.PartType.Ball, [2] = Enum.PartType.Cylinder }
local function bryly(rodzic, lista, baza)
	for _, c in lista do
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
		p.Anchored = true
		p.CanCollide = false
		p.CanTouch = false
		p.CastShadow = true
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		if c[14] ~= "" then
			local sm = Instance.new("SpecialMesh")
			sm.MeshType = Enum.MeshType[c[14]]
			sm.Parent = p
		end
		p.Parent = rodzic
	end
end
local function napisy(czesc, linie, tlo)
	local sg = Instance.new("SurfaceGui")
	sg.Name = "Ekran"
	sg.Face = Enum.NormalId.Front
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 50
	sg.LightInfluence = 0
	sg.Parent = czesc
	local f = Instance.new("Frame")
	f.Size = UDim2.fromScale(1, 1)
	f.BackgroundColor3 = Color3.fromHex(tlo)
	f.BorderSizePixel = 0
	f.Parent = sg
	local lista = Instance.new("UIListLayout")
	lista.SortOrder = Enum.SortOrder.LayoutOrder
	lista.HorizontalAlignment = Enum.HorizontalAlignment.Center
	lista.Padding = UDim.new(0.01, 0)
	lista.Parent = f
	local pad = Instance.new("UIPadding")
	pad.PaddingTop = UDim.new(0.04, 0)
	pad.PaddingLeft = UDim.new(0.04, 0)
	pad.PaddingRight = UDim.new(0.04, 0)
	pad.Parent = f
	for i, l in linie do
		local t = Instance.new("TextLabel")
		t.Name = l.nazwa or ("Linia" .. i)
		t.LayoutOrder = i
		t.BackgroundTransparency = 1
		t.Size = UDim2.fromScale(1, l.wys)
		t.Text = l.tekst
		t.TextScaled = true
		t.Font = if l.cyfry then Enum.Font.FredokaOne else Enum.Font.LuckiestGuy
		t.TextColor3 = Color3.fromHex(l.kolor)
		t.TextXAlignment = if l.lewo then Enum.TextXAlignment.Left else Enum.TextXAlignment.Center
		local o = Instance.new("UIStroke")
		o.Thickness = 2
		o.Color = Color3.fromHex("1B1424")
		o.Parent = t
		t.Parent = f
	end
	return sg
end
local function plaszczyzna(x, y, z, patrz)
	return CFrame.lookAt(Vector3.new(x, y, z), Vector3.new(patrz[1], y, patrz[3]))
end
local drewno, ciemne, kamien = Color3.fromHex("9A6234"), Color3.fromHex("5E3A1A"), Color3.fromHex("8C8A84")
for _, I in D.inkubatory do
	local m = Instance.new("Model")
	m.Name = "Inkubator" .. I.nr
	local y = ziemia(I.miejsce[1], I.miejsce[2], I.miejsce[3])
	local cf = plaszczyzna(I.miejsce[1], y, I.miejsce[3], I.patrz)
	local cokol = czesc(m, "Cokol", Vector3.new(1.2, 7, 7), cf * CFrame.new(0, 0.6, 0) * CFrame.Angles(0, 0, math.pi / 2), kamien, Enum.Material.Slate)
	cokol.Shape = Enum.PartType.Cylinder
	local obr = czesc(m, "Obrecz", Vector3.new(0.25, 7.3, 7.3), cf * CFrame.new(0, 0.95, 0) * CFrame.Angles(0, 0, math.pi / 2), Color3.fromHex(I.kolor), Enum.Material.Neon)
	obr.Shape = Enum.PartType.Cylinder
	obr.CanCollide = false
	local jajko = Instance.new("Model")
	jajko.Name = "Jajko"
	bryly(jajko, I.bryly, cf * CFrame.new(0, 1.2, 0))
	jajko.Parent = m
	local tab = czesc(m, "Tablica", Vector3.new(6.4, 5.2, 0.4), cf * CFrame.new(-6.4, 3.4, 0.6) * CFrame.Angles(0, math.rad(-18), 0), Color3.fromHex("FFF6E0"))
	for _, s in { -1, 1 } do
		czesc(m, "Noga", Vector3.new(0.4, 3.2, 0.4), cf * CFrame.new(-6.4, 0, 0.6) * CFrame.Angles(0, math.rad(-18), 0) * CFrame.new(s * 2.6, 1.6, 0.3), ciemne, Enum.Material.Wood)
	end
	napisy(tab, I.linie, "FFF6E0")
	m.Parent = st
end
for _, S in D.sklepy do
	local m = Instance.new("Model")
	m.Name = "Sklep" .. S.nr
	local y = ziemia(S.miejsce[1], S.miejsce[2], S.miejsce[3])
	local cf = plaszczyzna(S.miejsce[1], y, S.miejsce[3], S.patrz)
	czesc(m, "Lada", Vector3.new(9, 3, 2.6), cf * CFrame.new(0, 1.5, 0), drewno, Enum.Material.Wood)
	czesc(m, "Blat", Vector3.new(9.6, 0.4, 3.2), cf * CFrame.new(0, 3.2, 0), ciemne, Enum.Material.Wood)
	for _, sx in { -4.3, 4.3 } do
		czesc(m, "Slup", Vector3.new(0.6, 8, 0.6), cf * CFrame.new(sx, 4, 1.4), ciemne, Enum.Material.Wood)
	end
	for i = 0, 5 do
		czesc(m, "Daszek" .. i, Vector3.new(1.6, 0.35, 4.4), cf * CFrame.new(-4 + i * 1.6, 8.1, 0.2) * CFrame.Angles(math.rad(-12), 0, 0),
			if i % 2 == 0 then Color3.fromHex("FF4D4D") else Color3.fromHex("FFF6E0"))
	end
	local szyld = czesc(m, "Szyld", Vector3.new(7.4, 1.8, 0.3), cf * CFrame.new(0, 6.6, -0.6), Color3.fromHex("FFC83D"))
	napisy(szyld, { { tekst = S.tytul, kolor = "FFF6E0", wys = 0.9 } }, "FF8A3D")
	local wystawa = Instance.new("Model")
	wystawa.Name = "Wystawa"
	bryly(wystawa, S.bryly, cf * CFrame.new(0, 3.4, 0) * CFrame.Angles(0, math.pi, 0))
	wystawa.Parent = m
	m.Parent = st
end
for _, T in D.tablice do
	local m = Instance.new("Model")
	m.Name = "Tablica" .. T.nr
	local y = ziemia(T.miejsce[1], T.miejsce[2], T.miejsce[3])
	local cf = plaszczyzna(T.miejsce[1], y, T.miejsce[3], T.patrz)
	for _, sx in { -1, 1 } do
		czesc(m, "Slup", Vector3.new(0.6, T.wys + 1.6, 0.6), cf * CFrame.new(sx * (T.szer / 2 + 0.2), (T.wys + 1.6) / 2, 0.3), ciemne, Enum.Material.Wood)
	end
	local tab = czesc(m, "Tablica", Vector3.new(T.szer, T.wys, 0.4), cf * CFrame.new(0, 1.6 + T.wys / 2, 0), Color3.fromHex("1B1424"))
	local linie = { { tekst = T.tytul, kolor = T.kolor, wys = 0.12 } }
	for i = 1, T.wierszy do
		table.insert(linie, { tekst = "", kolor = "FFF6E0", wys = 0.095, nazwa = "Rzad" .. i, cyfry = true, lewo = true })
	end
	napisy(tab, linie, "2A2236")
	m.Parent = st
end
st.Parent = kont
return string.format("stanowiska: %d inkubatory, %d stoiska, %d tablice", #D.inkubatory, #D.sklepy, #D.tablice)
'''

MAPA_START = WSTEP + r'''
local kont, odmowa = kontener()
if odmowa then
	return odmowa
end
local stara = kont:FindFirstChild("Mapa")
if stara then
	stara:Destroy()
end
local m = Instance.new("Folder")
m.Name = "Mapa"
m.Parent = kont
return "OK"
'''

MAPA_PACZKA = WSTEP + r'''
local G = __GRUPY__
local M = __MATERIALY__
local Dn = __DANE__
local kont = kontener()
local mapa = kont and kont:FindFirstChild("Mapa")
if not mapa then
	return "STOP: brak Mapa w kontenerze"
end
local cache = {}
local function grupa(i)
	local g = cache[i]
	if g then
		return g
	end
	local cur = mapa
	local czlony = string.split(G[i], "/")
	for k = 1, #czlony do
		local nxt = cur:FindFirstChild(czlony[k])
		if not nxt then
			nxt = Instance.new(if k == #czlony then "Model" else "Folder")
			nxt.Name = czlony[k]
			nxt.Parent = cur
		end
		cur = nxt
	end
	cache[i] = cur
	return cur
end
local n = 0
for _, c in Dn do
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
	p.CanTouch = false
	p.CanCollide = c[16] == 1
	p.CastShadow = c[17] == 1
	p.Parent = grupa(c[2] + 1)
	n += 1
end
return n
'''

KONIEC = WSTEP + r'''
local kont = kontener()
if kont then
	game:GetService("ChangeHistoryService"):SetWaypoint("BonkGra: zbudowano")
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
CH:SetWaypoint("BonkGra: przed usunięciem")
for _, k in nasze do
	k:Destroy()
end
CH:SetWaypoint("BonkGra: usunięto")
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
CH:SetWaypoint("BonkGra: przed __ATR__")
kont:SetAttribute("__ATR__", __WARTOSC__)
CH:SetWaypoint("BonkGra: __ATR__")
return "__ATR__ = " .. tostring(kont:GetAttribute("__ATR__"))
'''

# odczyt: czy obszar mapy jest pusty (promienie w siatce + części w pudle); niczego nie zmienia
TEREN = r'''
local HS = game:GetService("HttpService")
local D = __DANE__
local kont = workspace:FindFirstChild("__KONTENER__")
local pomin = {}
if kont and kont:GetAttribute("Wygenerowane") == true then
	table.insert(pomin, kont)
end
local pr = RaycastParams.new()
pr.FilterType = Enum.RaycastFilterType.Exclude
pr.FilterDescendantsInstances = pomin
local trafienia, promieni, przyklady = 0, 0, {}
local x = D.x[1]
while x <= D.x[2] do
	local z = D.z[1]
	while z <= D.z[2] do
		promieni += 1
		local t = workspace:Raycast(Vector3.new(x, D.y[2] + 200, z), Vector3.new(0, -(D.y[2] - D.y[1] + 400), 0), pr)
		if t then
			trafienia += 1
			if #przyklady < 8 then
				table.insert(przyklady, string.format("%s (%.0f; %.0f; %.0f)", t.Instance:GetFullName(), t.Position.X, t.Position.Y, t.Position.Z))
			end
		end
		z += D.krok
	end
	x += D.krok
end
local op = OverlapParams.new()
op.FilterType = Enum.RaycastFilterType.Exclude
op.FilterDescendantsInstances = pomin
op.MaxParts = 40
local srodek = Vector3.new((D.x[1] + D.x[2]) / 2, (D.y[1] + D.y[2]) / 2, (D.z[1] + D.z[2]) / 2)
local roz = Vector3.new(D.x[2] - D.x[1], D.y[2] - D.y[1], D.z[2] - D.z[1])
local czesci = workspace:GetPartBoundsInBox(CFrame.new(srodek), roz, op)
local wlasciciele = {}
for _, p in czesci do
	local o = p
	while o.Parent and o.Parent ~= workspace do
		o = o.Parent
	end
	wlasciciele[o.Name] = (wlasciciele[o.Name] or 0) + 1
end
local spawny = {}
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") then
		table.insert(spawny, string.format("%s (%.1f; %.1f; %.1f) Enabled=%s Neutral=%s", d:GetFullName(), d.Position.X, d.Position.Y,
			d.Position.Z, tostring(d.Enabled), tostring(d.Neutral)))
	end
end
return HS:JSONEncode({ promieni = promieni, trafienia = trafienia, przyklady = przyklady, czesciWPudle = #czesci,
	wlasciciele = wlasciciele, streaming = workspace.StreamingEnabled, spawny = spawny })
'''

STAN = r'''
local HS = game:GetService("HttpService")
local kont = workspace:FindFirstChild("__KONTENER__")
if not kont or kont:GetAttribute("Wygenerowane") ~= true then
	return HS:JSONEncode({ jest = false })
end
local w = { jest = true, atrybuty = {}, zrodla = {}, sygnaly = {}, wzorce = {}, czesciMapy = 0, bramy = 0 }
for n, v in kont:GetAttributes() do
	w.atrybuty[n] = if typeof(v) == "Vector3" then { v.X, v.Y, v.Z } else v
end
for _, d in kont:GetDescendants() do
	if d:IsA("LuaSourceContainer") then
		w.zrodla[d.Name] = { klasa = d.ClassName, bajtow = #d.Source, kontekst = if d:IsA("Script") then d.RunContext.Name else nil }
	end
end
for _, d in (kont:FindFirstChild("Sygnaly") or kont):GetChildren() do
	if d:IsA("RemoteEvent") or d:IsA("BindableFunction") then
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
local mapa = kont:FindFirstChild("Mapa")
if mapa then
	for _, d in mapa:GetDescendants() do
		if d:IsA("BasePart") then
			w.czesciMapy += 1
		end
	end
end
local b = kont:FindFirstChild("Bramy")
w.bramy = if b then #b:GetChildren() else 0
local st = kont:FindFirstChild("Stanowiska")
w.stanowiska = if st then #st:GetChildren() else 0
w.portal = kont:FindFirstChild("Portal") ~= nil
w.powrot = kont:FindFirstChild("Powrot") ~= nil
return HS:JSONEncode(w)
'''


def log(*a):
    print("BONK |", *a, flush=True)


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
    w = [("Moduly", "DaneBonk", "ModuleScript", "", pliki[DN.PLIK_DANYCH])]
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


def dane_wzorca(klucz, i):
    w = DN.wzorzec(klucz)
    return {"klucz": klucz, "nazwa": w["nazwa"], "bryly": w["bryly"], "poz": [0, 0, 0], "_i": i}


def wzorce_wszystkie(U, D):
    """[(nazwa wzorca, dane do WZORZEC)] — potwory i Strażnicy (D.gatunki) oraz pety, jajka i pałki (etap 2)."""
    w = [(k, dane_wzorca(k, i)) for i, k in enumerate(sorted(D["gatunki"]))]
    for nazwa, x in sorted(DN.wzorce_etapu2(U).items()):
        w.append((nazwa, {"klucz": nazwa, "nazwa": x["nazwa"], "bryly": x["bryly"], "poz": [0, 0, 0]}))
    return w


def oczekiwane_wzorce(U, D):
    """{nazwa: liczba części (bryły + korzeń)} — do kontroli po budowie."""
    return {n: len(d["bryly"]) + 1 for n, d in wzorce_wszystkie(U, D)}


def dane_stanowisk(U, D):
    W = DN.wzorce_etapu2(U)
    ui = U["ui"]
    ink = []
    for J in D["jajka"]:
        K = D["krainy"][J["nr"] - 1]
        linie = [{"tekst": J["nazwa"], "kolor": "1B1424", "wys": 0.17},
                 {"tekst": "%s %s" % (format_liczby(J["cena"]), ui["monety"]), "kolor": "C98A00", "wys": 0.12, "cyfry": True},
                 {"tekst": ui["szanse"], "kolor": "1B1424", "wys": 0.1}]
        for i, pid in enumerate(J["pety"]):
            R = D["rzadkosci"][i]
            linie.append({"tekst": "%s  %g%%" % (D["pety"][pid]["nazwa"], R["szansa"] * 100), "kolor": R["kolor"], "wys": 0.1,
                          "cyfry": True})
        ink.append({"nr": J["nr"], "miejsce": J["miejsce"], "patrz": [J["miejsce"][0], 0, K["start"][2]],
                    "bryly": W[J["wzorzec"]]["bryly"], "linie": linie, "kolor": D["rzadkosci"][2]["kolor"]})
    skl = []
    for i, S in enumerate(D["sklepy"], 1):
        K = D["krainy"][S["kraina"] - 1]
        skl.append({"nr": i, "miejsce": S["miejsce"], "patrz": [S["miejsce"][0], 0, K["start"][2]], "tytul": ui["sklep"],
                    "bryly": W[DN.nazwa_wzorca_palki(3)]["bryly"]})
    kolory = [ui["kolory"]["moc"], ui["kolory"]["monety"], "C27BFF"]
    tab = [dict(T, wierszy=D["pokazanie"]["wierszy"], kolor=kolory[i]) for i, T in enumerate(D["pokazanie"]["tablice"])]
    return {"inkubatory": ink, "sklepy": skl, "tablice": tab}


def dane_bram(U, D, publikacja):
    bramy = []
    for K in D["krainy"]:
        b = K["brama"]
        bramy.append({"nr": K["nr"], "x": b["x"], "y": K["start"][1], "z": b["z"], "wys": b["wysokosc"], "szer": b["szerokosc"],
                      "napis": (U["ui"]["brama_dalej"] if K["nr"] >= len(D["krainy"])
                                else U["ui"]["brama_zamknieta"] % format_liczby(b["wymagana"]))})
    p = D["powrot"]
    powrot = None if publikacja else {"x": p[0], "y": p[1], "z": p[2], "napis": U["ui"]["powrot"], "kolor": "4DA6FF"}
    return {"bramy": bramy, "powrot": powrot}


def format_liczby(n):
    """Lustro L.format (LogikaBonk) — do napisów budowanych w Edit."""
    przyrostki = ["K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp"]
    if n < 1000:
        return str(int(n))
    i = 0
    n = float(n)
    while n >= 1000 and i < len(przyrostki):
        n /= 1000
        i += 1
    if n >= 100:
        t = str(int(n))
    else:
        d = int(n * 10 + 1e-9) / 10
        t = str(int(d)) if d == int(d) else "%.1f" % d
    return t + przyrostki[i - 1]


def dane_mapy(U):
    """[(nazwa krainy, grupy (ścieżki w Mapa), materiały, części z przesunięciem)] — z czesci.json map pasów."""
    p = U["przesuniecie"]
    w = []
    for K in U["krainy"]:
        d = DN.czytaj_json(DN.sciezka_repo(K["mapa"] + "/czesci.json"))
        prefiks = K["grupa"] + "/"
        grupy = []
        for g in d["grupy"]:
            if not (g == K["grupa"] or g.startswith(prefiks)):
                raise DN.BladDanych("%s: grupa %s poza %s" % (K["id"], g, K["grupa"]))
            reszta = g[len(prefiks):] if g.startswith(prefiks) else ""
            grupy.append(K["folder"] + ("/" + reszta if reszta else ""))
        czesci = []
        for c in d["czesci"]:
            cechy = int(c[15]) if len(c) > 15 else 0
            czesci.append([int(c[0]), int(c[1]), round(c[2] + p[0], 3), round(c[3] + p[1], 3), round(c[4] + p[2], 3),
                           c[5], c[6], c[7], c[8], c[9], c[10], c[11], int(c[12]), c[13], c[14],
                           0 if cechy & 1 else 1, 0 if cechy & 2 else 1])
        w.append((K["id"], grupy, d["materialy"], czesci))
    return w


def obszar(U):
    p = U["przesuniecie"]
    O = U["obszar_sprawdzenia"]
    return {"x": [DN.X0 + O["u"][0] + p[0], DN.X0 + O["u"][1] + p[0]], "z": [DN.Z0 + O["v"][0] + p[2], DN.Z0 + O["v"][1] + p[2]],
            "y": [O["y"][0] + p[1], O["y"][1] + p[1]], "krok": O["krok"]}


def plan(U, D, Z, mapa):
    w = ["do Studio: %d modułów i skryptów (%d kB), sygnały: %s" % (
        len(Z), sum(len(t.encode("utf-8")) for *_, t in Z) // 1000, ", ".join(ZDALNE + LOKALNE))]
    W = wzorce_wszystkie(U, D)
    w.append("wzorce: %d (potwory i Strażnicy %d, pety, jajka, pałki), %d brył" % (len(W), len(D["gatunki"]),
                                                                                  sum(len(d["bryly"]) for _, d in W)))
    w.append("mapa: %s — razem %d części, przesunięcie %s" % (
        ", ".join("%s %d" % (k, len(c)) for k, _, _, c in mapa), sum(len(c) for *_, c in mapa), U["przesuniecie"]))
    O = obszar(U)
    w.append("obszar BONK: x %.0f…%.0f, z %.0f…%.0f" % (O["x"][0], O["x"][1], O["z"][0], O["z"][1]))
    return w


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="BONK w Studio: Workspace/BonkGra")
    ap.add_argument("--sucho", action="store_true")
    ap.add_argument("--teren", action="store_true")
    ap.add_argument("--mapa", action="store_true")
    ap.add_argument("--skrypty", action="store_true")
    ap.add_argument("--stan", action="store_true")
    ap.add_argument("--usun", action="store_true")
    ap.add_argument("--autostart", choices=["on", "off"])
    ap.add_argument("--wlacz", choices=["on", "off"])
    ap.add_argument("--publikacja", action="store_true")
    ap.add_argument("--studio", default=None)
    a = ap.parse_args()
    try:
        U, D, pliki = DN.wszystkie_pliki()
        mapa = dane_mapy(U)
    except DN.BladDanych as e:
        log("BŁĄD danych:", e)
        return 2
    zle = DN.nieaktualne(pliki)
    if zle:
        log("BŁĄD: nieaktualne dane (%s) — uruchom python -B swiat/bonk/dane.py" % ", ".join(zle))
        return 1
    Z = zrodla(pliki, a.publikacja)
    bledy = sprawdz_zrodla()
    bledy += ["%s: %d znaków ponad limit %d" % (n, len(t), U["limit_zrodla"]) for _, n, _, _, t in Z if len(t) > U["limit_zrodla"]]
    for b in bledy:
        log("BŁĄD źródeł:", b)
    for linia in DN.tabela(U, D) + plan(U, D, Z, mapa):
        log(linia)
    log("źródła Luau: %s%s" % ("bez błędów" if not bledy else "%d błędów" % len(bledy),
                              "; PUBLIKACJA: bez strażnika Studio" if a.publikacja else ""))
    if bledy:
        return 1
    if a.sucho:
        return 0
    if a.publikacja and not a.studio:
        log("--publikacja wymaga --studio <id> (puste miejsce, nie miejsce gry)")
        return 2
    from studio_mcp import StudioMCP  # noqa: E402
    from cel_studio import MIEJSCE, wybierz_studio  # noqa: E402
    if a.publikacja:
        wspolne = dict(WARUNEK_MIEJSCA="game.PlaceId == %d" % MIEJSCE,
                       OPIS_MIEJSCA="to miejsce obecnej gry, a --publikacja jest dla pustego miejsca", KONTENER=U["kontener"])
    else:
        wspolne = dict(WARUNEK_MIEJSCA="game.PlaceId ~= %d" % MIEJSCE, OPIS_MIEJSCA="to nie jest miejsce gry",
                       KONTENER=U["kontener"])
    with StudioMCP(timeout=240) as s:
        if a.publikacja:
            sid = a.studio
        else:
            sid = wybierz_studio(s, a.studio)
        if "Current Studio Mode: Edit" not in s.call("get_studio_state", {"studio_id": sid})["text"]:
            log("PRZERWANO — Studio nie jest w trybie Edit (ktoś może grać); nic nie zmieniono")
            return 1

        def wykonaj(kod, opis, timeout=240):
            r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=timeout)
            tekst = (r["text"] or "").strip()
            if r["is_error"] or tekst.startswith("STOP"):
                log("PRZERWANO — Studio odmówiło (%s): %s" % (opis, tekst[:600]))
                raise SystemExit(1)
            return tekst

        if a.teren:
            w = json.loads(wykonaj(wstaw(TEREN, DANE=DN.luau(obszar(U)), KONTENER=U["kontener"]), "teren"))
            print(json.dumps(w, ensure_ascii=False, indent=1))
            pusty = w["trafienia"] == 0 and w["czesciWPudle"] == 0
            log("obszar BONK %s" % ("PUSTY — można budować" if pusty else "ZAJĘTY — zmień przesuniecie w ustawieniach"))
            return 0 if pusty else 1
        if a.stan:
            print(json.dumps(json.loads(wykonaj(wstaw(STAN, KONTENER=U["kontener"]), "stan")), ensure_ascii=False, indent=1))
            return 0
        if a.usun:
            log(wykonaj(wstaw(USUN, **wspolne), "usuwanie"))
            return 0
        if a.autostart or a.wlacz:
            atr, wart = (U["autostart"], a.autostart) if a.autostart else (U["wylacznik"], a.wlacz)
            log(wykonaj(wstaw(ATRYBUT, ATR=atr, WARTOSC="true" if wart == "on" else "false", **wspolne), atr))
            return 0
        t0 = time.time()
        wynik = wykonaj(wstaw(START, CZAS=time.strftime("%Y-%m-%d %H:%M"), SKROT=D["skrot"], WYLACZNIK=U["wylacznik"],
                              AUTOSTART=U["autostart"], MAPA_OD_NOWA="true" if a.mapa else "false",
                              TYLKO_SKRYPTY="true" if a.skrypty else "false",
                              PUBLIKACJA="true" if a.publikacja else "false",
                              ZDALNE=", ".join(json.dumps(n) for n in ZDALNE),
                              LOKALNE=", ".join(json.dumps(n) for n in LOKALNE), **wspolne), "start")
        log(wynik)
        for rodzic, nazwa, klasa, kontekst, tekst in Z:
            log(wykonaj(wstaw(ZRODLO, RODZIC=rodzic, NAZWA=nazwa, KLASA=klasa, KONTEKST=kontekst or "Legacy",
                              TEKST=DN.luau(tekst), **wspolne), nazwa))
        if not a.skrypty:
            if "do budowy" in wynik:
                log(wykonaj(wstaw(MAPA_START, **wspolne), "mapa"))
                for nazwa, grupy, materialy, czesci in mapa:
                    razem = 0
                    for i in range(0, len(czesci), PACZKA_MAPY):
                        n = wykonaj(wstaw(MAPA_PACZKA, GRUPY=DN.luau(grupy), MATERIALY=DN.luau(materialy),
                                          DANE=DN.luau(czesci[i:i + PACZKA_MAPY]), **wspolne), "mapa " + nazwa)
                        razem += int(float(n))
                    log("mapa %s: %d części" % (nazwa, razem))
            for i, (klucz, d) in enumerate(wzorce_wszystkie(U, D)):
                p = U["przesuniecie"]
                d["poz"] = [DN.X0 + p[0] + 20 * i, GALERIA_Y + p[1], DN.Z0 + p[2]]
                log(wykonaj(wstaw(WZORZEC, DANE=DN.luau(d), **wspolne), "wzorzec " + klucz))
            log(wykonaj(wstaw(BRAMY, DANE=DN.luau(dane_bram(U, D, a.publikacja)), **wspolne), "bramy"))
            log(wykonaj(wstaw(STANOWISKA, DANE=DN.luau(dane_stanowisk(U, D)), **wspolne), "stanowiska"))
            if not a.publikacja:
                P = U["portal"]
                dp = {"rozmiar": P["rozmiar"], "odleglosci": list(range(P["odleglosc"][0], P["odleglosc"][1] + 1, 4)),
                      "napis": U["ui"]["portal"], "kolor": U["ui"]["kolory"]["moc"]}
                log(wykonaj(wstaw(PORTAL, DANE=DN.luau(dp), **wspolne), "portal"))
        wykonaj(wstaw(KONIEC, **wspolne), "koniec")
        stan = json.loads(wykonaj(wstaw(STAN, KONTENER=U["kontener"]), "stan"))
        niezgodne = []
        for _, nazwa, klasa, kontekst, tekst in Z:
            m = stan["zrodla"].get(nazwa)
            if not m or m["klasa"] != klasa or m["bajtow"] != len(tekst.encode("utf-8")) or (kontekst and m.get("kontekst") != kontekst):
                niezgodne.append(nazwa)
        if sorted(stan["sygnaly"]) != sorted(ZDALNE + LOKALNE) or stan["atrybuty"].get("Skrot") != D["skrot"]:
            niezgodne.append("sygnały albo skrót")
        oczek_mapy = sum(len(c) for *_, c in mapa)
        if stan["czesciMapy"] != oczek_mapy:
            niezgodne.append("mapa %d / %d części" % (stan["czesciMapy"], oczek_mapy))
        oczek_wz = oczekiwane_wzorce(U, D)
        if stan["wzorce"] != oczek_wz:
            niezgodne.append("wzorce (%d / %d)" % (len(stan["wzorce"]), len(oczek_wz)))
        if stan.get("stanowiska") != len(D["jajka"]) + len(D["sklepy"]) + len(D["pokazanie"]["tablice"]):
            niezgodne.append("stanowiska")
        if stan["bramy"] != len(D["krainy"]):
            niezgodne.append("bramy")
        log("kontrola po budowie (%.0f s): %s" % (time.time() - t0, "zgodne — %d źródeł, skrót %s, mapa %d części, wzorce %d, "
                                                 "bramy %d, stanowiska %s, portal %s, powrót %s, AutoStart %s" % (
                                                     len(stan["zrodla"]), stan["atrybuty"].get("Skrot"), stan["czesciMapy"],
                                                     len(stan["wzorce"]), stan["bramy"], stan.get("stanowiska"), stan["portal"], stan["powrot"],
                                                     stan["atrybuty"].get(U["autostart"]))
                                                 if not niezgodne else "NIEZGODNE: " + ", ".join(niezgodne)))
        return 1 if niezgodne else 0


if __name__ == "__main__":
    sys.exit(main())
