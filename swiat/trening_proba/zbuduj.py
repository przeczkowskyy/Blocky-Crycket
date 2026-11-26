#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/TreningProba — próba Training Center: sześć mini-gier w sceneriach krain
(D-108; pas z prostych części w powietrzu z dala od map: Łąka pod dębem i Polana drwali w Lesie, Grobla i Pomost nad
topielą na Bagnie, Krąg strażnika i Świątynia run w Dżungli), tablica wejścia przy miejscu startu gracza, skrypty
serwera i klienta. Gracz przechodzi z okna wyboru prosto do scenerii wybranej gry (dawnego lobby areny nie ma).

    python -B swiat/trening_proba/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/trening_proba/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/trening_proba/zbuduj.py --skrypty    # tylko moduły i skrypty (arena zostaje)
    python -B swiat/trening_proba/zbuduj.py --usun       # usuwa Workspace/TreningProba
    python -B swiat/trening_proba/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/TreningProba z atrybutem Wygenerowane = true; cudzych kontenerów budowa NIE zmienia —
SpawnLocation i MiasteczkoBazarGra tylko czyta):
  Moduly/DaneTreningu, Moduly/LogikaTreningu      ModuleScript (zrodla/; DaneTreningu wygenerowany przez dane.py)
  Moduly/KameraTreningu, EfektyTreningu, KomiksTreningu   ModuleScript — wygląd jak w walce (kamera, efekty, napisy)
  SerwerTreningu (RunContext = Server), KlientTreningu (RunContext = Client)
  Zdalne/ZdarzeniaTreningu                         RemoteEvent (oba kierunki; opis w SerwerTreningu)
  Sygnaly/PrzyrostStatystyki                       BindableEvent — przyrost statystyki dla przyszłego modułu statystyk
  Sygnaly/SterowanieSerwera, SterowanieKlienta     BindableFunction — haczyki testowe
  Sygnaly/WybierzGre                               BindableFunction (klient) — uchwyt dla docelowego okna 2D Pawła
  Arena (Model, ModelStreamingMode Persistent)     elementy gier (scena.py) i scenerie krain (scenerie.json), ok. 2800 części
  TablicaWejscia (Model, Persistent)               tablica z podpowiedzią E przy pierwszym SpawnLocation (wybór w Studio)
                                                   — od 26.11.2026 NIE powstaje (ustawienia.json → tablica_wejscia.w_grze =
                                                   false): gracz zaczyna w bazarze i wchodzi przez trenera w bazarze
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot, WyborTymczasowy (true; false = okno Pawła zamiast
tymczasowego wyboru), PunktTablicy. Atrybuty ustawione ręcznie w Edit (WyborTymczasowy, RecznyPunktTablicy — Vector3
na gruncie) przechodzą na odbudowany kontener.

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId == 129485428021967 i tryb Edit; ruszany jest tylko własny
kontener (obiekt o tej nazwie bez atrybutu Wygenerowane → STOP); przed budową sprawdzamy, że w pudle areny nie ma
cudzych części (są → STOP); punkty historii przed i po (Ctrl+Z cofa całość); nic nie jest zapisywane ani publikowane,
Lighting nietknięty. --sucho nie importuje studio_mcp ani cel_studio.
"""
import argparse
import os
import sys
import time

sys.dont_write_bytecode = True
TU = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(TU))
if not sys.path or sys.path[0] != TU:
    sys.path.insert(0, TU)
import dane as DANE  # noqa: E402
import scena as SCENA  # noqa: E402
import sprawdz_luau_treningu as SLT  # noqa: E402

SL = SLT.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/trening_proba"
ZRODLA = os.path.join(TU, "zrodla")

SKRYPTY = [
    ("DaneTreningu.luau", "ModuleScript", "Moduly/DaneTreningu", None),
    ("LogikaTreningu.luau", "ModuleScript", "Moduly/LogikaTreningu", None),
    # wygląd jak w walce (18.11.2026): rachunek kamery, efekty 3D trafień i konfetti, komiksowe napisy — tylko klient
    ("KameraTreningu.luau", "ModuleScript", "Moduly/KameraTreningu", None),
    ("EfektyTreningu.luau", "ModuleScript", "Moduly/EfektyTreningu", None),
    ("KomiksTreningu.luau", "ModuleScript", "Moduly/KomiksTreningu", None),
    ("SerwerTreningu.server.luau", "Script", "SerwerTreningu", "Server"),
    ("KlientTreningu.client.luau", "Script", "KlientTreningu", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly"]
INNE = [
    ("RemoteEvent", "Zdalne/ZdarzeniaTreningu"),
    ("BindableEvent", "Sygnaly/PrzyrostStatystyki"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
    ("BindableFunction", "Sygnaly/WybierzGre"),
]
ATRYBUTY_TESTOWE = ["WyborTymczasowy", "RecznyPunktTablicy"]
# 26.11.2026: tryb bez mini-gier (ustawienia.json → mini_gry.w_grze = false) — kontener tylko z sygnałem przyrostu:
# src/server/TreningAFK.server.luau (Paweł) strzela nim przyrostami ze stanowisk AFK, swiat/stan_gracza słucha i zapisuje.
# Bez areny, bez modułów i skryptów (SerwerTreningu i KlientTreningu to tylko mini-gry), bez haczyków (BindableFunction
# bez odbiorcy wstrzymałaby wywołującego na zawsze).
FOLDERY_LOGIKI = ["Sygnaly"]
INNE_LOGIKI = [("BindableEvent", "Sygnaly/PrzyrostStatystyki")]
# podpowiedzi E: (ścieżka części w kontenerze, Akcja, Zrodlo, napis akcji, obiekt)
PODPOWIEDZI = [
    ("TablicaWejscia/E", "wybor", "tablica", "Mini-gry", "Training Center"),
]

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

# ------------------------------------------------------------------------------------------------ kod Luau
# tylko odczyt: czy pudło areny jest wolne (cudze części → STOP), co jest w miejscu
SPRAWDZ = r'''
local f = workspace:FindFirstChild("__KONTENER__")
local op = OverlapParams.new()
op.FilterType = Enum.RaycastFilterType.Exclude
op.FilterDescendantsInstances = if f then { f } else {}
local mn, mx = Vector3.new(__MIN__), Vector3.new(__MAX__)
local obce = workspace:GetPartBoundsInBox(CFrame.new((mn + mx) / 2), (mx - mn) + Vector3.new(8, 8, 8), op)
local uwagi = {}
local spawny = 0
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") then spawny += 1 end
end
table.insert(uwagi, "SpawnLocation: " .. spawny)
local bz = workspace:FindFirstChild("__BAZAR__")
table.insert(uwagi, "__BAZAR__: " .. tostring(bz ~= nil))
local pb = bz
for _, n in string.split("__PODPOWIEDZ_BAZARU__", "/") do pb = pb and pb:FindFirstChild(n) end
table.insert(uwagi, "trener w bazarze (E training_center): " .. tostring(pb ~= nil))
if #obce > 0 then
	local nazwy = {}
	for i = 1, math.min(5, #obce) do table.insert(nazwy, obce[i]:GetFullName()) end
	return "STOP: w pudle areny są cudze części (" .. #obce .. "): " .. table.concat(nazwy, ", ")
end
return "pudło areny wolne | " .. table.concat(uwagi, " | ")
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
f:SetAttribute("WyborTymczasowy", true)
f:SetAttribute("MiniGry", __MINI__)
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

# wspólne: część z danych (scena.py) i podpowiedź E
CZESC = r'''
local function grupa(korzen, sciezka)
	local o = korzen
	for _, n in string.split(sciezka, "/") do
		local d = o:FindFirstChild(n)
		if not d then
			d = Instance.new("Model")
			d.Name = n
			d.Parent = o
		end
		o = d
	end
	return o
end
local function czesc(korzen, c)
	local p = Instance.new(if c.k == "W" then "WedgePart" elseif c.k == "N" then "CornerWedgePart" else "Part")
	p.Name = c.n
	p.Anchored = true
	if c.k ~= "W" and c.k ~= "N" then
		p.Shape = if c.k == "C" then Enum.PartType.Cylinder elseif c.k == "K" then Enum.PartType.Ball else Enum.PartType.Block
	end
	p.Size = Vector3.new(c.s[1], c.s[2], c.s[3])
	local cf = CFrame.new(c.p[1], c.p[2], c.p[3])
	if c.o then cf = cf * CFrame.Angles(math.rad(c.o[1]), math.rad(c.o[2]), math.rad(c.o[3])) end
	p.CFrame = cf
	p.Color = Color3.fromHex(c.c)
	p.Material = Enum.Material[c.m or "SmoothPlastic"]
	p.Transparency = c.t or 0
	p.CanCollide = c.kol ~= false
	p.CanQuery = c.kol ~= false
	p.CanTouch = false
	p.CastShadow = (c.t or 0) < 0.5 and c.bc ~= true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	if c.napis then
		local sg = Instance.new("SurfaceGui")
		sg.Name = "Napis"
		sg.Face = Enum.NormalId[c.napis.strona]
		sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sg.PixelsPerStud = c.napis.px
		sg.LightInfluence = 0
		sg.MaxDistance = 140
		local l = Instance.new("TextLabel")
		l.Size = UDim2.fromScale(0.94, 0.9)
		l.Position = UDim2.fromScale(0.03, 0.05)
		l.BackgroundTransparency = 1
		l.FontFace = Font.new(Font.fromEnum(Enum.Font.__CZCIONKA__).Family, Enum.FontWeight.__WAGA__)
		l.TextScaled = true
		l.TextWrapped = true -- bez zawijania TextScaled w SurfaceGui rysował napis bardzo mały (próba 17.11.2026)
		l.TextColor3 = Color3.fromHex(c.napis.kolor)
		l.Text = c.napis.tekst
		l.Parent = sg
		sg.Parent = p
	end
	p.Parent = grupa(korzen, c.r)
	return p
end
local function podpowiedz(p, akcja, zrodlo, tekst, obiekt, PD)
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "Podpowiedz"
	pp.ActionText = tekst
	pp.ObjectText = obiekt
	pp.KeyboardKeyCode = Enum.KeyCode[PD.klawisz]
	pp.GamepadKeyCode = Enum.KeyCode[PD.pad]
	pp.HoldDuration = 0
	pp.MaxActivationDistance = PD.zasieg
	pp.RequiresLineOfSight = false
	pp.ClickablePrompt = true
	pp.Enabled = false -- włącza SerwerTreningu w trybie Play (tylko w Studio)
	pp:SetAttribute("Akcja", akcja)
	if zrodlo ~= "" then pp:SetAttribute("Zrodlo", zrodlo) end
	pp.Parent = p
	return pp
end
'''

ARENA = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
__CZESC__
local PD = __PODPOWIEDZ__
local stara = f:FindFirstChild("Arena")
local m = stara
if __PIERWSZA__ then
	if stara then stara:Destroy() end
	m = Instance.new("Model")
	m.Name = "Arena"
	m.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	m.Parent = f
end
if not m then return "STOP: brak modelu Arena (paczka części bez pierwszej)" end
local n = 0
for _, c in __CZESCI__ do
	czesc(f, c)
	n += 1
end
if not __OSTATNIA__ then return "OK (paczka: " .. n .. " części)" end
local razem = 0
for _, d in m:GetDescendants() do
	if d:IsA("BasePart") then razem += 1 end
end
if razem ~= __RAZEM__ then return "STOP: w Arenie " .. razem .. " części, a ma być __RAZEM__" end
n = razem
local pp = 0
for _, w in __PODPOWIEDZI_ARENY__ do
	local p = f
	for _, s in string.split(w[1], "/") do p = p and p:FindFirstChild(s) end
	if p then
		podpowiedz(p, w[2], w[3], w[4], w[5], PD)
		pp += 1
	end
end
m.PrimaryPart = m:FindFirstChild("Podloga") and m.Podloga:FindFirstChildWhichIsA("BasePart")
return "OK (części areny: " .. n .. ", podpowiedzi: " .. pp .. ")"
'''

TABLICA = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
__CZESC__
local PD = __PODPOWIEDZ__
local TW = __TABLICA__
local NAPIS = __NAPIS__
local stara = f:FindFirstChild("TablicaWejscia")
if stara then stara:Destroy() end
local pomin = { f }
local function sciezka(t)
	local o = workspace
	for i, n in string.split(t, "/") do
		if not (i == 1 and n == "Workspace") then o = o and o:FindFirstChild(n) end
	end
	return o
end
local function grunt(x, z, y0)
	local par = RaycastParams.new()
	par.FilterType = Enum.RaycastFilterType.Exclude
	par.FilterDescendantsInstances = pomin
	par.RespectCanCollide = true
	local r = workspace:Raycast(Vector3.new(x, y0 + TW.rzut_od, z), Vector3.new(0, -TW.rzut_dlugosc, 0), par)
	return if r then r.Position.Y else nil
end
-- 1. środek szukania: pierwszy SpawnLocation (tylko odczyt), inaczej punkt zapasowy z danych
local sp = nil
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") and not d:IsDescendantOf(f) then sp = d break end
end
local s = if sp then sp.Position + Vector3.new(0, sp.Size.Y / 2, 0) else Vector3.new(TW.zapas_bez_spawnu[1], TW.zapas_bez_spawnu[2], TW.zapas_bez_spawnu[3])
-- 2. miejsca do ominięcia: „Nowe miasteczko (E)” bazaru (atrybut), portal startowy (cudze — tylko odczyt)
local omijaj = {}
for _, o in TW.omijaj do
	local p = nil
	if o.atrybut then
		local k = workspace:FindFirstChild(o.atrybut[1])
		local v = k and k:GetAttribute(o.atrybut[2])
		if typeof(v) == "Vector3" then p = v end
	elseif o.sciezka then
		local obj = sciezka(o.sciezka)
		if obj and obj:IsA("Model") then p = obj:GetPivot().Position elseif obj and obj:IsA("BasePart") then p = obj.Position end
	end
	if p then table.insert(omijaj, { p = p, r = o.promien }) end
end
-- 3. ręczny punkt albo pierwszy wolny kandydat na pierścieniach wokół startu
local wybrany, opis = nil, ""
local reczny = f:GetAttribute("RecznyPunktTablicy")
if typeof(reczny) == "Vector3" then
	wybrany, opis = reczny, "ręczny (atrybut RecznyPunktTablicy)"
else
	local op = OverlapParams.new()
	op.FilterType = Enum.RaycastFilterType.Exclude
	op.FilterDescendantsInstances = pomin
	op.RespectCanCollide = true
	local proby = 0
	for _, r in TW.promienie do
		for i = 0, TW.kierunki - 1 do
			local a = i * 2 * math.pi / TW.kierunki
			local c = s + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
			local wolny = true
			for _, o in omijaj do
				if (Vector3.new(c.X, 0, c.Z) - Vector3.new(o.p.X, 0, o.p.Z)).Magnitude < o.r then wolny = false end
			end
			if wolny then
				proby += 1
				local y = grunt(c.X, c.Z, s.Y)
				if y and math.abs(y - s.Y) <= TW.roznica_wysokosci then
					local w = TW.wolne
					local zajete = workspace:GetPartBoundsInBox(CFrame.new(c.X, y + w[2] / 2 + 0.3, c.Z), Vector3.new(w[1], w[2], w[3]), op)
					if #zajete == 0 then
						wybrany, opis = Vector3.new(c.X, y, c.Z), string.format("pierścień %g st, kierunek %d (próba %d)", r, i, proby)
						break
					end
				end
			end
		end
		if wybrany then break end
	end
	if not wybrany then
		wybrany = s + Vector3.new(TW.promienie[1], 0, 0)
		opis = "BRAK WOLNEGO MIEJSCA — punkt zapasowy, sprawdź na oko i ustaw RecznyPunktTablicy"
	end
end
-- 4. tablica twarzą do startu
local ku = Vector3.new(s.X - wybrany.X, 0, s.Z - wybrany.Z)
local kier = if ku.Magnitude > 0.1 then ku.Unit else Vector3.new(0, 0, 1)
local m = Instance.new("Model")
m.Name = "TablicaWejscia"
m.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
m.Parent = f
local baza = CFrame.lookAt(wybrany, wybrany + kier)
local function dodaj(n, lok, rozmiar, kol, napis, przezr)
	local cf = baza * CFrame.new(lok[1], lok[2], lok[3])
	local c = { n = n, r = "TablicaWejscia", k = "B", p = { cf.X, cf.Y, cf.Z }, s = rozmiar, c = kol, napis = napis, t = przezr, kol = przezr == nil }
	local p = czesc(f, c)
	p.CFrame = cf
	return p
end
dodaj("NogaL", { -3.95, 3, 0 }, { 0.6, 6, 0.6 }, "6B4A2F")
dodaj("NogaP", { 3.95, 3, 0 }, { 0.6, 6, 0.6 }, "6B4A2F")
dodaj("Daszek", { 0, 7.3, 0 }, { 8.4, 0.5, 1.4 }, "E5533D")
dodaj("Deska", { 0, 4.9, 0 }, { 7.2, 3.8, 0.4 }, "FFF6E0", { tekst = NAPIS, strona = "Front", px = 40, kolor = "17121F" })
local tyl = dodaj("DeskaTyl", { 0, 4.9, 0.25 }, { 7.2, 3.8, 0.1 }, "FFF6E0", { tekst = NAPIS, strona = "Back", px = 40, kolor = "17121F" })
local e = dodaj("E", { 0, 3, -0.8 }, { 0.6, 0.6, 0.6 }, "FFF6E0", nil, 1)
podpowiedz(e, "wybor", "tablica", "Mini-gry", "Training Center", PD)
f:SetAttribute("PunktTablicy", wybrany)
return string.format("OK tablica wejścia (%.1f; %.1f; %.1f) — %s | start (%.1f; %.1f; %.1f) z %s | ominięte: %d",
	wybrany.X, wybrany.Y, wybrany.Z, opis, s.X, s.Y, s.Z, if sp then sp:GetFullName() else "danych (brak SpawnLocation)", #omijaj)
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


def _w(v):
    return ", ".join("%g" % x for x in v)


def zrodla_pakietu():
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
    ok, D = DANE.aktualny()
    print("dane.py --sprawdz: %s (skrót %s, statystyk %d, grywalnych %d)"
          % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["statystyki"]), len(D["gry"])))
    if not ok:
        sys.exit("BŁĄD: zrodla/DaneTreningu.luau nieaktualny — uruchom python -B swiat/trening_proba/dane.py")
    bledy, parser = SLT.sprawdz_pliki(SLT.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_treningu.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
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
    mn, mx = SCENA.obrys(D)
    return (SPRAWDZ.replace("__KONTENER__", D["kontener"]).replace("__MIN__", _w(mn)).replace("__MAX__", _w(mx))
            .replace("__BAZAR__", D["bazar"]["kontener"]).replace("__PODPOWIEDZ_BAZARU__", D["bazar"]["podpowiedz"]))


def kod_start(D, usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", D["kontener"]).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__TESTOWE__", ", ".join(DANE._napis(a) for a in ATRYBUTY_TESTOWE))
            .replace("__MINI__", "true" if mini_gry_w_grze(D) else "false")
            .replace("__FOLDERY__", ", ".join(DANE._napis(x) for x in foldery(D)))
            .replace("__INNE__", ", ".join("{%s, %s}" % (DANE._napis(k), DANE._napis(p)) for k, p in inne(D))))


def mini_gry_w_grze(D):
    """Czy budować arenę i skrypty mini-gier (26.11.2026: nie — ustawienia.json → mini_gry.w_grze = false)."""
    return (D.get("mini_gry") or {}).get("w_grze", True) is not False


def foldery(D):
    return FOLDERY if mini_gry_w_grze(D) else FOLDERY_LOGIKI


def inne(D):
    return INNE if mini_gry_w_grze(D) else INNE_LOGIKI


def skrypty_w_grze(D, zrodla):
    """Moduły i skrypty, które budowa wysyła (bez mini-gier: żadnych)."""
    return zrodla if mini_gry_w_grze(D) else []


def _podpowiedzi(z_tablica):
    lista = [p for p in PODPOWIEDZI if p[0].startswith("TablicaWejscia") == z_tablica]
    return "{ " + ", ".join("{ %s }" % ", ".join(DANE._napis(x) for x in p) for p in lista) + " }"


def _czesc(D):
    return CZESC.replace("__CZCIONKA__", D["ui"]["czcionka"]).replace("__WAGA__", D["ui"]["waga_czcionki"])


PACZKA_CZESCI = 300  # części areny w jednym wywołaniu Studio (elementy gier i scenerie to ok. 2800 części)


def kody_areny(D):
    """Kod budowy areny w paczkach po PACZKA_CZESCI części: pierwsza zakłada model, ostatnia sprawdza liczbę części,
    stawia podpowiedzi E i część główną."""
    cz = SCENA.czesci(D)
    paczki = [cz[i:i + PACZKA_CZESCI] for i in range(0, len(cz), PACZKA_CZESCI)]
    kody = []
    for i, paczka in enumerate(paczki):
        kody.append(ARENA.replace("__CZESC__", _czesc(D)).replace("__KONTENER__", D["kontener"])
                    .replace("__PODPOWIEDZ__", DANE._luau(D["podpowiedz"]))
                    .replace("__PODPOWIEDZI_ARENY__", _podpowiedzi(False))
                    .replace("__PIERWSZA__", "true" if i == 0 else "false")
                    .replace("__OSTATNIA__", "true" if i == len(paczki) - 1 else "false")
                    .replace("__RAZEM__", str(len(cz)))
                    .replace("__CZESCI__", DANE._luau(paczka)))
    return kody


def kod_tablicy(D):
    return (TABLICA.replace("__CZESC__", _czesc(D)).replace("__KONTENER__", D["kontener"])
            .replace("__PODPOWIEDZ__", DANE._luau(D["podpowiedz"]))
            .replace("__TABLICA__", DANE._luau(D["tablica_wejscia"]))
            .replace("__NAPIS__", DANE._napis(D["teksty"]["tablica_wejscia"])))


def kod_skryptu(D, sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", D["kontener"]).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def tablica_w_grze(D):
    """Czy budować tablicę wejścia (26.11.2026: nie — ustawienia.json → tablica_wejscia.w_grze = false)."""
    return D["tablica_wejscia"].get("w_grze", True) is not False


def podpowiedzi_w_grze(D):
    """Podpowiedzi E, które budowa naprawdę stawia (bez tablicy wejścia, gdy jest wyłączona)."""
    return [p for p in PODPOWIEDZI if tablica_w_grze(D) or not p[0].startswith("TablicaWejscia")]


def kod_konca(D, punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", D["kontener"]).replace("__OCZEKIWANE__", str(len(podpowiedzi_w_grze(D))))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def wszystkie_kody(D):
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    areny = kody_areny(D) if mini_gry_w_grze(D) else []
    return {"sprawdz": kod_sprawdz(D), "start": kod_start(D, czas="x", skrot="x"), "usun": kod_start(D, True),
            **{"arena%d" % (i + 1): k for i, k in enumerate(areny)}, "tablica": kod_tablicy(D), "koniec": kod_konca(D)}


def plan(D):
    linie = []
    if not mini_gry_w_grze(D):
        linie.append("  %-26s → nie powstaje (mini_gry.w_grze = false, 26.11.2026): bez areny, modułów, skryptów i haczyków"
                     % "Arena, Moduly, skrypty")
        linie.append("  %-26s → BindableEvent dla src/server/TreningAFK.server.luau → swiat/stan_gracza (zapis)"
                     % "Sygnaly/PrzyrostStatystyki")
        linie.append("  %-26s → nie powstaje (tablica_wejscia.w_grze = false i mini_gry.w_grze = false)" % "TablicaWejscia")
        return linie
    mn, mx = SCENA.obrys(D)
    cz = SCENA.czesci(D)
    linie.append("  %-26s → %d części, pudło (%s) – (%s)" % ("Arena (Persistent)", len(cz), _w([round(x, 1) for x in mn]),
                                                             _w([round(x, 1) for x in mx])))
    for st in D["statystyki"]:
        if st["id"] in D["gry"]:
            W = D["swiat"][st["id"]]
            linie.append("  %-26s → stanowisko %s „%s” · podest (%s) · kamera (%s)" % (
                "  " + st["id"], st["nazwa"], st["gra"], _w(W["podest"]), _w(W["oko"])))
        else:
            linie.append("  %-26s → zapowiedź %s „%s” (%s)" % ("  " + st["id"], st["nazwa"], st["gra"], st["stan"]))
    for p in podpowiedzi_w_grze(D):
        linie.append("  %-26s → podpowiedź E: Akcja=%s%s" % (p[0], p[1], (", Zrodlo=" + p[2]) if p[2] else ""))
    TW = D["tablica_wejscia"]
    if tablica_w_grze(D):
        linie.append("  %-26s → przy pierwszym SpawnLocation, pierścienie %s × %d kierunków, omija %d miejsc" % (
            "TablicaWejscia (Persistent)", TW["promienie"], TW["kierunki"], len(TW["omijaj"])))
    else:
        linie.append("  %-26s → nie powstaje (tablica_wejscia.w_grze = false, 26.11.2026): wejście przez trenera w bazarze"
                     % "TablicaWejscia")
    return linie


# ------------------------------------------------------------------------------------------------ główna
def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/TreningProba w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/TreningProba")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        _, D = DANE.dane_z_przypadkami()
        zrodla = []
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · Skrot danych: %s · placeId %d · modułów i skryptów: %d"
              % (D["kontener"], D["skrot"], MIEJSCE, len(skrypty_w_grze(D, zrodla))))
        print("  %-26s → %s" % ("Folder", ", ".join(foldery(D))))
        print("  %-26s → %s" % ("Tryb", "pełna próba mini-gier" if mini_gry_w_grze(D) else
                                "BEZ mini-gier (mini_gry.w_grze = false): tylko sygnał przyrostu dla stanowisk AFK"))
        for klasa, sciezka in inne(D):
            print("  %-26s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in skrypty_w_grze(D, zrodla):
            print("  %-26s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        for linia in plan(D):
            print(linia)
        kody = wszystkie_kody(D)
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
                for sciezka, klasa, kontekst, tekst, plik in skrypty_w_grze(D, zrodla):
                    print("  skrypt:", wykonaj(kod_skryptu(D, sciezka, klasa, kontekst, tekst)))

            t0 = time.time()
            if a.skrypty and not mini_gry_w_grze(D):
                sys.exit("STOP: mini_gry.w_grze = false — bez --skrypty: pełna budowa usuwa arenę i skrypty mini-gier "
                         "i stawia sam sygnał przyrostu")
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
            if mini_gry_w_grze(D):
                for i, k in enumerate(kody_areny(D)):
                    print("  arena %d:" % (i + 1), wykonaj(k))
            else:
                print("  arena: pominięta (mini_gry.w_grze = false — kontener tylko z sygnałem przyrostu)")
            if tablica_w_grze(D):
                print("  tablica:", wykonaj(kod_tablicy(D)))
            else:
                print("  tablica: pominięta (tablica_wejscia.w_grze = false — wejście tylko przez trenera w bazarze)")
            skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
