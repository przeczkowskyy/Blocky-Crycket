#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/MiasteczkoBazarGra — „miasteczko-bazar w grze”: podpowiedzi E przy
sprzedawcach i bramach bazaru, uchwyt dla okien 2D Pawła, portal krain (przejście przez chmury), Brama Leśna (uchwyt
pasa Lasu), działka i lochy (dymki), tablica z rankingiem oraz tymczasowe przejścia stare ↔ nowe miasteczko.

    python -B swiat/miasteczko_bazar_gra/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/miasteczko_bazar_gra/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/miasteczko_bazar_gra/zbuduj.py --skrypty    # tylko moduły i skrypty (części i punkt w starym
                                                                #   miasteczku zostają)
    python -B swiat/miasteczko_bazar_gra/zbuduj.py --usun       # usuwa Workspace/MiasteczkoBazarGra
    python -B swiat/miasteczko_bazar_gra/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/MiasteczkoBazarGra z atrybutem Wygenerowane = true; mapy Workspace/MiasteczkoBazar,
starego miasteczka ani żadnego innego kontenera budowa NIE zmienia — cudze obiekty tylko czyta):
  Moduly/DaneBazaru, Moduly/LogikaBazaru     ModuleScript (zrodla/; DaneBazaru wygenerowany przez dane.py)
  SerwerBazaru (RunContext = Server), KlientBazaru (RunContext = Client)
  Zdalne/ZdarzeniaBazaru                      RemoteEvent (serwer → klient: okno, dymek, chmury, przeniesiono)
  Sygnaly/PrzeniesDoBazaru                    BindableFunction — uchwyt serwera: start bazaru (np. przejście przez chmury)
  Sygnaly/SterowanieSerwera, SterowanieKlienta  BindableFunction — haczyki testowe
  Punkty/E <id>                               niewidzialne części z ProximityPrompt „Podpowiedz” (Enabled = false —
                                              włącza SerwerBazaru w Play) w miejscach ze znaczniki.json; „E nowe_miasteczko”
                                              stoi w STARYM miasteczku przy miejscu startu (wybór w Studio, niżej)
  Tablica/Ekran                               niewidzialna płytka z SurfaceGui „Ranking” na powierzchni tablica_ranking
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot, PunktStartuBazaru / PatrzStartuBazaru (Vector3, środek
HumanoidRootPart — do wpisu „atrybut” w swiat/teleport_chmury/krainy.json), PunktStaregoMiasteczka,
StartStaregoMiasteczka, ZrodloStartuStarego, PunktPowrotuStare / PatrzPowrotuStare. Atrybuty testowe ustawione ręcznie
w Edit (DymkiWylaczone, BezDymku, RecznyPunktStaregoMiasteczka) przechodzą na odbudowany kontener.

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId == 129485428021967 i tryb Edit; ruszany jest tylko własny
kontener (obiekt o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po (Ctrl+Z cofa całość);
nic nie jest zapisywane ani publikowane, Lighting nietknięty. --sucho nie importuje studio_mcp ani cel_studio.

„Nowe miasteczko (E)” w starym miasteczku: budowa szuka (tylko odczyt) SpawnLocation spoza bazaru najbliższego punktowi
startu z swiat/krzywe_miasteczko/uklad.json (bez niego — sam ten punkt) i portalu Workspace/LasTeleport/PortalStart;
kolejność kandydatów liczy LogikaBazaru.kandydaci (ta sama funkcja co w lustrze Pythona), a pierwszy z wolną skrzynką
(bez części z kolizją) i gruntem na wysokości startu wygrywa. Wynik: część „E nowe_miasteczko” i atrybuty kontenera.
"""
import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:  # własny folder pierwszy (w repo jest kilka zbuduj.py i dane*.py)
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402
import sprawdz_luau_bazaru  # noqa: E402

SL = sprawdz_luau_bazaru.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/miasteczko_bazar_gra"
ZRODLA = os.path.join(TU, "zrodla")

# (plik w zrodla/, klasa, ścieżka w kontenerze, RunContext)
SKRYPTY = [
    ("DaneBazaru.luau", "ModuleScript", "Moduly/DaneBazaru", None),
    ("LogikaBazaru.luau", "ModuleScript", "Moduly/LogikaBazaru", None),
    ("SerwerBazaru.server.luau", "Script", "SerwerBazaru", "Server"),
    ("KlientBazaru.client.luau", "Script", "KlientBazaru", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly", "Punkty"]
INNE = [
    ("RemoteEvent", "Zdalne/ZdarzeniaBazaru"),          # serwer → klient (okno, dymek, chmury, przeniesiono)
    ("BindableFunction", "Sygnaly/PrzeniesDoBazaru"),   # uchwyt dla innych skryptów serwera (start bazaru)
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),  # haczyk testowy SerwerBazaru (+ odblokowanie lochów)
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),  # haczyk testowy KlientBazaru
]
# strefy wejścia innych pakietów przy starym miasteczku, z dala od których stoi „Nowe miasteczko (E)”:
# (kontener w Workspace, atrybut Vector3 ze środkiem strefy, promień w st). Brama BONK (swiat/bonk, zasięg 5 st)
# — promień 12 = zasięg bramy + zasięg podpowiedzi E (8) bez 1 st, żeby gracz przy tabliczce nie wszedł w bramę.
STREFY_WEJSCIA = [("BonkGra", "PortalPoz", 12)]
ATRYBUTY_TESTOWE = ["DymkiWylaczone", "BezDymku", "RecznyPunktStaregoMiasteczka", "PrzenikanieKamery"]

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

# ------------------------------------------------------------------------------------------------ kod Luau
# tylko odczyt: co zastajemy w miejscu (ostrzeżenia, nie przerywa)
SPRAWDZ = r'''
local uwagi = {}
local function sciezka(t)
	local o = workspace
	for i, n in string.split(t, "/") do
		if not (i == 1 and n == "Workspace") then o = o and o:FindFirstChild(n) end
	end
	return o
end
local mapa = workspace:FindFirstChild("__MAPA__")
if not mapa then
	table.insert(uwagi, "brak Workspace/__MAPA__ (mapa bazaru) — podpowiedzi E staną w powietrzu, dymki bez sprzedawców")
else
	if mapa:GetAttribute("Wygenerowane") ~= true then table.insert(uwagi, "__MAPA__ bez atrybutu Wygenerowane") end
	local braki = {}
	for _, s in { __CZESCI_MAPY__ } do
		if not sciezka(s) then table.insert(braki, s) end
	end
	if #braki > 0 then table.insert(uwagi, "w mapie brak: " .. table.concat(braki, ", ")) end
	if not sciezka("__BLOKADA__") then table.insert(uwagi, "brak __BLOKADA__ (kłódka lochów)") end
end
if not workspace:FindFirstChild("KrzyweMiasteczko") then table.insert(uwagi, "brak Workspace/KrzyweMiasteczko (stare miasteczko)") end
local lt = workspace:FindFirstChild("LasTeleport")
table.insert(uwagi, "LasTeleport/PortalStart: " .. tostring(lt ~= nil and lt:FindFirstChild("PortalStart") ~= nil))
local tc = workspace:FindFirstChild("__CHMURY__")
table.insert(uwagi, "__CHMURY__/__OTWORZ__: " .. tostring(tc ~= nil and tc:FindFirstChild("__OTWORZ__") ~= nil))
table.insert(uwagi, "__LAS__: " .. tostring(sciezka("__LAS__") ~= nil))
local spawny = {}
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") then
		table.insert(spawny, string.format("%s (%.1f; %.1f; %.1f)", d:GetFullName(), d.Position.X, d.Position.Y, d.Position.Z))
	end
end
table.insert(uwagi, "SpawnLocation: " .. (if #spawny > 0 then table.concat(spawny, "; ") else "brak"))
return table.concat(uwagi, " | ")
'''

START = r'''
local CH = game:GetService("ChangeHistoryService")
local nazwa = "__KONTENER__"
local stare = {}
for _, d in workspace:GetChildren() do
	if d.Name == nazwa then
		if d:GetAttribute("Wygenerowane") ~= true then
			return "STOP: w Workspace jest obiekt '" .. nazwa .. "' bez atrybutu Wygenerowane — nie ruszam cudzej pracy"
		end
		table.insert(stare, d)
	end
end
if __USUN__ then
	if #stare == 0 then
		return "USUNIETO (kontenera nie było)"
	end
	CH:SetWaypoint(nazwa .. ": przed usunięciem")
	for _, d in stare do d:Destroy() end
	CH:SetWaypoint(nazwa .. ": usunięto")
	return "USUNIETO"
end
local testowe = {}
for _, d in stare do
	for _, a in { __TESTOWE__ } do
		local v = d:GetAttribute(a)
		if v ~= nil then testowe[a] = v end
	end
end
CH:SetWaypoint(nazwa .. ": przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
f:SetAttribute("PunktStartuBazaru", Vector3.new(__START_KORZEN__))
f:SetAttribute("PatrzStartuBazaru", Vector3.new(__START_PATRZ__))
for a, v in testowe do f:SetAttribute(a, v) end
for _, n in { __FOLDERY__ } do
	local d = Instance.new("Folder")
	d.Name = n
	d.Parent = f
end
for _, w in { __INNE__ } do
	local czesci = string.split(w[2], "/")
	local o = Instance.new(w[1])
	o.Name = czesci[2]
	o.Parent = f:FindFirstChild(czesci[1])
end
f.Parent = workspace
return "OK"
'''

# wspólna funkcja: niewidzialna część z podpowiedzią E (używa D z DaneBazaru)
PUNKT = r'''
local function punktE(rodzic, id, pozycja, m, tabliczka)
	local p = Instance.new("Part")
	p.Name = "E " .. id
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Transparency = 1
	p.Size = Vector3.new(0.6, 0.6, 0.6)
	p.Position = pozycja
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p:SetAttribute("Miejsce", id)
	p:SetAttribute("Akcja", m.akcja)
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "Podpowiedz"
	pp.ActionText = m.akcja_tekst
	pp.ObjectText = m.obiekt
	pp.KeyboardKeyCode = Enum.KeyCode[D.podpowiedz.klawisz]
	pp.GamepadKeyCode = Enum.KeyCode[D.podpowiedz.pad]
	pp.HoldDuration = 0
	pp.MaxActivationDistance = m.zasieg
	pp.RequiresLineOfSight = D.podpowiedz.linia_wzroku
	pp.ClickablePrompt = true
	pp.Enabled = false -- włącza SerwerBazaru w trybie Play (tylko w Studio)
	pp:SetAttribute("Miejsce", id)
	pp.Parent = p
	if tabliczka then
		local TB = D.tabliczka
		local b = Instance.new("BillboardGui")
		b.Name = "Tabliczka"
		b.Size = UDim2.fromOffset(TB.szer_px, TB.wys_px)
		b.StudsOffset = Vector3.new(0, TB.nad, 0)
		b.MaxDistance = TB.zasieg
		b.AlwaysOnTop = false
		b.LightInfluence = 0
		local t = Instance.new("TextLabel")
		t.Size = UDim2.fromScale(1, 1)
		t.BackgroundColor3 = Color3.fromHex(TB.tlo)
		t.BackgroundTransparency = 0.15
		t.TextColor3 = Color3.fromHex(TB.napis)
		t.Font = Enum.Font.FredokaOne
		t.TextScaled = true
		t.Text = tabliczka
		local r = Instance.new("UICorner")
		r.CornerRadius = UDim.new(0, 10)
		r.Parent = t
		t.Parent = b
		b.Parent = p
	end
	p.Parent = rodzic
	return p
end
'''

CZESCI = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local D = (function()
__DANE__
end)()
__PUNKT__
local punkty = f:FindFirstChild("Punkty")
for _, d in punkty:GetChildren() do
	if d.Name ~= "E nowe_miasteczko" then d:Destroy() end
end
local n = 0
for _, id in D.kolejnosc do
	local m = D.miejsca[id]
	if m.punkt then
		punktE(punkty, id, Vector3.new(m.punkt[1], m.punkt[2], m.punkt[3]), m, m.tabliczka)
		n += 1
	end
end
-- tablica: niewidzialna płytka tuż przed powierzchnią ze znacznika, SurfaceGui na przedniej ścianie (ku graczom)
local stara = f:FindFirstChild("Tablica")
if stara then stara:Destroy() end
local T = D.tablica
local nrm = Vector3.new(T.normalna[1], T.normalna[2], T.normalna[3]).Unit
local poz = Vector3.new(T.srodek[1], T.srodek[2], T.srodek[3]) + nrm * T.odsuniecie
local model = Instance.new("Model")
model.Name = "Tablica"
local e = Instance.new("Part")
e.Name = "Ekran"
e.Anchored = true
e.CanCollide = false
e.CanQuery = false
e.CanTouch = false
e.CastShadow = false
e.Transparency = 1
e.Size = Vector3.new(T.rozmiar[1], T.rozmiar[2], T.grubosc)
e.CFrame = CFrame.lookAt(poz, poz + nrm)
e.Parent = model
local KREM, TUSZ = Color3.fromHex("FFF6E0"), Color3.fromHex("17121F")
local sg = Instance.new("SurfaceGui")
sg.Name = "Ranking"
sg.Face = Enum.NormalId.Front
sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
sg.PixelsPerStud = T.px_na_stud
sg.LightInfluence = 0
sg.MaxDistance = 90
sg.Parent = e
local tlo = Instance.new("Frame")
tlo.Name = "Tlo"
tlo.Size = UDim2.fromScale(1, 1)
tlo.BackgroundColor3 = KREM
tlo.BorderSizePixel = 0
tlo.Parent = sg
local obrys = Instance.new("UIStroke")
obrys.Color = TUSZ
obrys.Thickness = 6
obrys.Parent = tlo
local function napis(nazwa, y, h, tekst, kolor, wyrownaj)
	local l = Instance.new("TextLabel")
	l.Name = nazwa
	l.BackgroundTransparency = 1
	l.Position = UDim2.fromScale(0.05, y)
	l.Size = UDim2.fromScale(0.9, h)
	l.Font = Enum.Font.FredokaOne
	l.TextScaled = true
	l.TextColor3 = kolor
	l.TextXAlignment = wyrownaj
	l.Text = tekst
	l.Parent = tlo
	return l
end
napis("Tytul", 0.03, 0.14, T.tytul, Color3.fromHex("2E8B57"), Enum.TextXAlignment.Center)
napis("Naglowek", 0.17, 0.06, T.naglowek, Color3.fromHex("6B5848"), Enum.TextXAlignment.Center)
local wys = 0.64 / T.wiersze
for i = 1, T.wiersze do
	napis("W" .. i, 0.25 + (i - 1) * wys, wys * 0.92, if i == 1 then T.pusto else "", TUSZ, Enum.TextXAlignment.Left)
end
napis("Stopka", 0.91, 0.06, T.stopka, Color3.fromHex("8A7F72"), Enum.TextXAlignment.Center)
model.PrimaryPart = e
model.Parent = f
return "OK (punktów E w bazarze: " .. n .. ", tablica " .. string.format("%.1f × %.1f", T.rozmiar[1], T.rozmiar[2]) .. ")"
'''

STARE = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local D = (function()
__DANE__
end)()
local L = (function()
__LOGIKA__
end)()
__PUNKT__
local S = D.stare
local m = D.miejsca.nowe_miasteczko
local uwagi = {}
local stary = f.Punkty:FindFirstChild("E nowe_miasteczko")
if stary then stary:Destroy() end
local pomin = { f }
local function grunt(x, z, y0)
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = pomin
	par.RespectCanCollide = true
	local r = workspace:Raycast(Vector3.new(x, y0 + S.rzut_od, z), Vector3.new(0, -S.rzut_dlugosc, 0), par)
	return if r then r.Position.Y else nil
end
-- 1. miejsce startu starego miasteczka: SpawnLocation spoza bazaru najbliższy punktowi z uklad.json, inaczej ten punkt
local zn = Vector3.new(S.znacznik[1], S.znacznik[2], S.znacznik[3])
local sl, zrodlo, najblizej, spawny = nil, "swiat/krzywe_miasteczko/uklad.json (spawn)", math.huge, 0
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") and not d:IsDescendantOf(f) then
		spawny += 1
		local p = d.Position
		if p.X >= D.bazar.czesci_x[1] and p.X <= D.bazar.czesci_x[2] and p.Z >= D.bazar.czesci_z[1] and p.Z <= D.bazar.czesci_z[2] then
			table.insert(uwagi, "SpawnLocation w bazarze pominięty: " .. d:GetFullName())
		else
			local o = Vector3.new(p.X - zn.X, 0, p.Z - zn.Z).Magnitude
			if o < najblizej then
				najblizej, sl, zrodlo = o, d, d:GetFullName()
			end
		end
	end
end
local s
if sl then
	s = sl.Position + Vector3.new(0, sl.Size.Y / 2, 0)
else
	s = Vector3.new(zn.X, grunt(zn.X, zn.Z, zn.Y) or zn.Y, zn.Z)
	table.insert(uwagi, "brak SpawnLocation poza bazarem — start z uklad.json")
end
local o = S.obszar_xz
if s.X < o[1] or s.X > o[2] or s.Z < o[3] or s.Z > o[4] then
	table.insert(uwagi, "start poza obszarem starego miasteczka")
end
-- 2. portal przy starcie (Workspace/LasTeleport/PortalStart, tylko odczyt): nie stawiamy obok i nie na drodze do niego
local lt = workspace:FindFirstChild("LasTeleport")
local ps = lt and lt:FindFirstChild("PortalStart")
local portal = nil
if ps and ps:IsA("Model") then
	portal = ps:GetPivot().Position
elseif ps and ps:IsA("BasePart") then
	portal = ps.Position
end
-- 3. ręczny punkt (atrybut testowy) albo pierwszy wolny kandydat z L.kandydaci
local wybrany, opis = nil, ""
local reczny = f:GetAttribute("RecznyPunktStaregoMiasteczka")
if typeof(reczny) == "Vector3" then
	wybrany, opis = reczny, "ręczny (atrybut RecznyPunktStaregoMiasteczka)"
else
	local op = OverlapParams.new()
	op.FilterType = Enum.RaycastFilterType.Exclude
	op.FilterDescendantsInstances = pomin
	op.RespectCanCollide = true
	local kand = L.kandydaci(D, { x = s.X, z = s.Z }, if portal then { x = portal.X, z = portal.Z } else nil)
	-- strefy wejścia innych pakietów (tylko odczyt atrybutów): brama BONK przy płycie startu przenosi każdego, kto
	-- wejdzie w jej zasięg (5 st). 26.11.2026: tabliczka stała 5,1 st od niej i postać przy tabliczce lądowała w BONK
	-- (B09 próby bazaru). Kandydat bliżej niż promień strefy odpada.
	local strefy = {}
	for _, st in { __STREFY__ } do
		local kk = workspace:FindFirstChild(st[1])
		local v = kk and kk:GetAttribute(st[2])
		if typeof(v) == "Vector3" then
			table.insert(strefy, { p = v, r = st[3], opis = st[1] .. "." .. st[2] })
		end
	end
	local pominiete = 0
	for i = #kand, 1, -1 do
		for _, st in strefy do
			if Vector3.new(kand[i].x - st.p.X, 0, kand[i].z - st.p.Z).Magnitude < st.r then
				table.remove(kand, i)
				pominiete += 1
				break
			end
		end
	end
	if pominiete > 0 then
		table.insert(uwagi, string.format("kandydatów przy strefach wejścia (%d) pominiętych: %d", #strefy, pominiete))
	end
	for i, c in kand do
		local y = grunt(c.x, c.z, s.Y)
		if y and math.abs(y - s.Y) <= S.roznica_wysokosci then
			local w = S.wolne
			local zajete = workspace:GetPartBoundsInBox(CFrame.new(c.x, y + w[2] / 2 + 0.3, c.z), Vector3.new(w[1], w[2], w[3]), op)
			if #zajete == 0 then
				wybrany, opis = Vector3.new(c.x, y, c.z), string.format("kandydat %d z %d", i, #kand)
				break
			end
		end
	end
	if not wybrany then
		local c = kand[1]
		wybrany = if c then Vector3.new(c.x, s.Y, c.z) else s + Vector3.new(S.promienie[1], 0, 0)
		opis = "BRAK WOLNEGO MIEJSCA — pierwszy kandydat"
		table.insert(uwagi, "żaden kandydat nie był wolny — sprawdź punkt na oko")
	end
end
-- 4. punkt E z tabliczką i punkt powrotu (S.powrot st ku startowi, twarzą do startu)
punktE(f.Punkty, "nowe_miasteczko", wybrany + Vector3.new(0, S.wysokosc_podpowiedzi, 0), m, m.tabliczka)
local ku = Vector3.new(s.X - wybrany.X, 0, s.Z - wybrany.Z)
local kier = if ku.Magnitude > 0.1 then ku.Unit else Vector3.new(1, 0, 0)
local powrot = wybrany + kier * S.powrot
f:SetAttribute("PunktStaregoMiasteczka", wybrany)
f:SetAttribute("StartStaregoMiasteczka", s)
f:SetAttribute("ZrodloStartuStarego", zrodlo)
f:SetAttribute("PunktPowrotuStare", Vector3.new(powrot.X, wybrany.Y, powrot.Z))
f:SetAttribute("PatrzPowrotuStare", Vector3.new(s.X, wybrany.Y, s.Z) + kier * 10)
return string.format("OK Nowe miasteczko (E): (%.1f; %.1f; %.1f) — %s | start (%.1f; %.1f; %.1f) z %s | PortalStart %s | SpawnLocation: %d%s",
	wybrany.X, wybrany.Y, wybrany.Z, opis, s.X, s.Y, s.Z, zrodlo,
	if portal then string.format("(%.1f; %.1f; %.1f)", portal.X, portal.Y, portal.Z) else "brak", spawny,
	if #uwagi > 0 then " | UWAGI: " .. table.concat(uwagi, "; ") else "")
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local sciezka = string.split("__SCIEZKA__", "/")
local rodzic = f
for i = 1, #sciezka - 1 do
	rodzic = rodzic:FindFirstChild(sciezka[i])
	if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
end
local stary = rodzic:FindFirstChild(sciezka[#sciezka])
if stary then stary:Destroy() end
local s = Instance.new("__KLASA__")
s.Name = sciezka[#sciezka]
__RUNCONTEXT__
s.Source = __ZRODLO__
s.Parent = rodzic
return "OK " .. s:GetFullName() .. " (" .. #s.Source .. " znaków)"
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local razem, skrypty, czesci, podpowiedzi = 0, 0, 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
	if d:IsA("BasePart") then czesci += 1 end
	if d:IsA("ProximityPrompt") then podpowiedzi += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: __PUNKT_HISTORII__")
local uwaga = if podpowiedzi ~= __OCZEKIWANE__ then " | UWAGA: podpowiedzi " .. podpowiedzi .. " zamiast __OCZEKIWANE__" else ""
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", części: " .. czesci .. ", podpowiedzi E: " .. podpowiedzi
	.. ", Skrot = " .. tostring(f:GetAttribute("Skrot")) .. uwaga
'''


# ------------------------------------------------------------------------------------------------ pomocnicze
def wczytaj(sciezka):
    with open(sciezka, encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n")


def dlugi_napis(tekst):
    poziom = 3
    while ("]" + "=" * poziom + "]") in tekst or ("[" + "=" * poziom + "[") in tekst:
        poziom += 1
    return "[" + "=" * poziom + "[\n" + tekst + "]" + "=" * poziom + "]"


def luau_napis(s):
    return json.dumps(s, ensure_ascii=False)


def _w(v):
    return ", ".join("%g" % x for x in v)


def zrodla_pakietu():
    """Lista (ścieżka w kontenerze, klasa, RunContext, tekst, plik). Brak pliku → kod 2."""
    wynik, braki = [], []
    for plik, klasa, sciezka, kontekst in SKRYPTY:
        pelna = os.path.join(ZRODLA, plik)
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        wynik.append((sciezka, klasa, kontekst, wczytaj(pelna), plik))
    if braki:
        print("BŁĄD: brak plików w zrodla/: " + ", ".join(braki))
        sys.exit(2)
    return wynik


def sprawdz_offline(zrodla):
    """--sucho i każda budowa: dane aktualne, Luau czyste, strażniki, rozmiary. Zwraca D (dane z przypadkami)."""
    ok, D = DANE.aktualny()
    print("dane.py --sprawdz: %s (skrót %s, miejsc %d, przypadków wzorcowych %d)"
          % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["kolejnosc"]), len(D["przypadki"])))
    if not ok:
        sys.exit("BŁĄD: zrodla/DaneBazaru.luau nieaktualny — uruchom python -B swiat/miasteczko_bazar_gra/dane.py")
    bledy, parser = sprawdz_luau_bazaru.sprawdz_pliki(sprawdz_luau_bazaru.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_bazaru.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
                                                      " (z parserem luau_mini)" if parser else " (bez parsera)"))
    if bledy:
        for b in bledy:
            print("  " + b)
        sys.exit("BŁĄD: kontrola Luau")
    for sciezka, klasa, kontekst, tekst, plik in zrodla:
        if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
            sys.exit("BŁĄD: %s (%s) nie zaczyna się od strażnika Studio" % (sciezka, plik))
        if len(tekst) > LIMIT_ZRODLA:
            sys.exit("BŁĄD: %s ma %d znaków (limit Source 200 000)" % (sciezka, len(tekst)))
    return D


# ------------------------------------------------------------------------------------------------ składanie kodu
def kod_sprawdz(D):
    czesci_mapy = [m["czesc_mapy"] for m in (D["miejsca"][i] for i in D["kolejnosc"]) if m.get("czesc_mapy")]
    return (SPRAWDZ.replace("__MAPA__", D["mapa"]).replace("__BLOKADA__", D["lochy"]["blokada"])
            .replace("__CHMURY__", D["chmury"]["kontener"]).replace("__OTWORZ__", D["chmury"]["zdarzenie"])
            .replace("__LAS__", D["las"]["uchwyt"])
            .replace("__CZESCI_MAPY__", ", ".join(luau_napis(s) for s in czesci_mapy)))


def kod_start(D, usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", D["kontener"]).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__START_KORZEN__", _w(D["start"]["korzen"])).replace("__START_PATRZ__", _w(D["start"]["patrz"]))
            .replace("__TESTOWE__", ", ".join(luau_napis(a) for a in ATRYBUTY_TESTOWE))
            .replace("__FOLDERY__", ", ".join(luau_napis(x) for x in FOLDERY))
            .replace("__INNE__", ", ".join("{%s, %s}" % (luau_napis(k), luau_napis(p)) for k, p in INNE)))


def kod_czesci(D):
    dane = wczytaj(os.path.join(ZRODLA, DANE.PLIK_LUAU))
    return (CZESCI.replace("__KONTENER__", D["kontener"]).replace("__PUNKT__", PUNKT)
            .replace("__DANE__", dane))


def kod_stare(D):
    dane = wczytaj(os.path.join(ZRODLA, DANE.PLIK_LUAU))
    logika = wczytaj(os.path.join(ZRODLA, "LogikaBazaru.luau"))
    return (STARE.replace("__KONTENER__", D["kontener"]).replace("__PUNKT__", PUNKT)
            .replace("__STREFY__", ", ".join("{%s, %s, %s}" % (luau_napis(k), luau_napis(a), r) for k, a, r in STREFY_WEJSCIA))
            .replace("__LOGIKA__", logika).replace("__DANE__", dane))


def kod_skryptu(D, sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", D["kontener"]).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def kod_konca(D, punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", D["kontener"]).replace("__OCZEKIWANE__", str(len(D["kolejnosc"])))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def plan(D):
    """Opis budowy do --sucho (bez Studio)."""
    linie = []
    for mid in D["kolejnosc"]:
        m = D["miejsca"][mid]
        gdzie = "(%s)" % _w(m["punkt"]) if m.get("punkt") else "stare miasteczko — wybór w Studio"
        dodatki = []
        if m.get("hud"):
            dodatki.append("HUD „%s”" % m["hud"])
        if m["akcja"] == "okno" or m["akcja"] == "lochy":
            dodatki.append("OknoMiejsca(\"%s\")" % mid)
        if m.get("tabliczka"):
            dodatki.append("tabliczka „%s”" % m["tabliczka"].replace("  ", " "))
        linie.append("  %-24s → %-9s %-36s zasięg %g · „%s / %s”%s" % (
            "Punkty/E " + mid, m["akcja"], gdzie, m["zasieg"], m["obiekt"], m["akcja_tekst"],
            (" · " + ", ".join(dodatki)) if dodatki else ""))
    T = D["tablica"]
    linie.append("  %-24s → SurfaceGui %g × %g st @ (%s), normalna (%s), %d wierszy rankingu" % (
        "Tablica/Ekran", T["rozmiar"][0], T["rozmiar"][1], _w(T["srodek"]), _w(T["normalna"]), T["wiersze"]))
    S = D["stare"]
    linie.append("  %-24s → wokół SpawnLocation spoza bazaru (zapas: (%s) z uklad.json), pierścienie %s, %d kierunków"
                 % ("stare miasteczko", _w(S["znacznik"]), S["promienie"], len(S["kierunki"])))
    return linie


# ------------------------------------------------------------------------------------------------ główna
def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/MiasteczkoBazarGra w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/MiasteczkoBazarGra")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        _, _, D = DANE.wszystko()
        zrodla = []
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · Skrot danych: %s · placeId %d · modułów i skryptów: %d"
              % (D["kontener"], D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-24s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-24s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-24s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                         plik, len(tekst)))
        for linia in plan(D):
            print(linia)
        print("  atrybuty: PunktStartuBazaru (%s), PatrzStartuBazaru (%s); testowe przenoszone przy odbudowie: %s"
              % (_w(D["start"]["korzen"]), _w(D["start"]["patrz"]), ", ".join(ATRYBUTY_TESTOWE)))
        print("  zdarzenie dla okien 2D: ReplicatedStorage.%s (BindableEvent u klienta); sygnał HUD: ReplicatedStorage.%s"
              % (D["zdarzenie_okien"], D["sygnal_hud"]))
        kody = {"sprawdz": kod_sprawdz(D), "start": kod_start(D, czas="x", skrot="x"), "czesci": kod_czesci(D),
                "stare": kod_stare(D), "koniec": kod_konca(D)}
        print("  kod wysyłany do Studio: %s" % ", ".join("%s %d zn." % (k, len(v)) for k, v in kody.items()))
    if a.sucho:
        print("sucho: OK (Studio nieużywane)")
        return

    # --- dopiero tutaj Studio (--sucho niczego z tego nie importuje)
    for _s in (os.path.join(REPO, "tools"), os.path.join(REPO, "swiat", "test_walki_roblox")):
        if _s not in sys.path:
            sys.path.insert(0, _s)
    from cel_studio import MIEJSCE as MIEJSCE_GRY, wybierz_studio  # noqa: E402
    from studio_mcp import StudioMCP, StudioError  # noqa: E402
    if MIEJSCE_GRY != MIEJSCE:
        sys.exit("BŁĄD: placeId w cel_studio.py (%s) ≠ %s — przerywam" % (MIEJSCE_GRY, MIEJSCE))
    try:
        with StudioMCP() as s:
            s.studios(wait=15)
            sid = wybierz_studio(s, a.studio)
            stan = s.call("get_studio_state", {"studio_id": sid})["text"]
            if "Current Studio Mode: Edit" not in stan:
                sys.exit("Studio nie jest w trybie Edit — zatrzymaj Play i spróbuj ponownie.\n" + stan)

            def wykonaj(kod):
                kod = NAGLOWEK_MIEJSCA.replace("__MIEJSCE__", str(MIEJSCE)) + kod
                r = s.call("execute_luau", {"code": kod, "datamodel_type": "Edit", "studio_id": sid}, timeout=240)
                if r["is_error"]:
                    raise StudioError(r["text"][:3000])
                w = r["text"].strip()
                if w.startswith("STOP"):
                    print(w)
                    sys.exit(2)
                return w

            def skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(D, sciezka, klasa, kontekst, tekst)))

            t0 = time.time()
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (D["kontener"], D["kontener"], D["skrot"]))
                skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D, "skrypty wymienione")), time.time() - t0))
                return
            if not a.usun:
                print("w miejscu (tylko odczyt):", wykonaj(kod_sprawdz(D)))
            wynik = wykonaj(kod_start(D, a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or wynik != "OK":
                return
            print("  części:", wykonaj(kod_czesci(D)))
            print("  stare miasteczko:", wykonaj(kod_stare(D)))
            skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
