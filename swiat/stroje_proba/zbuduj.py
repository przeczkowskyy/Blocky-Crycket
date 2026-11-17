#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/StrojeProba — próba ubierania postaci (D-071): stojak „Przymierzalnia”
z lustrem i podestem przy miejscu startu, moduły danych / logiki / ubierania i okna, skrypty serwera i klienta.

    python -B swiat/stroje_proba/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/stroje_proba/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/stroje_proba/zbuduj.py --skrypty    # tylko moduły i skrypty (stojak zostaje)
    python -B swiat/stroje_proba/zbuduj.py --walka      # TYLKO moduł Workspace/TestWalki2/Moduly/Aktorzy z
                                                        # swiat/test_walki2/zrodla/Aktorzy.luau (haczyk stroju);
                                                        # reszty próby walki nie rusza (inne zmiany w jej źródłach
                                                        # wysyła jej własny zbuduj.py)
    python -B swiat/stroje_proba/zbuduj.py --usun       # usuwa Workspace/StrojeProba (przed publikacją miejsca)
    python -B swiat/stroje_proba/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/StrojeProba z atrybutem Wygenerowane = true; cudzych kontenerów budowa NIE zmienia —
SpawnLocation, TreningProba, MiasteczkoBazarGra i LasTeleport tylko czyta; wyjątek: --walka, opisany wyżej):
  Moduly/DaneStrojow (wygenerowany przez dane.py), Moduly/LogikaStrojow, Moduly/Ubieranie, Moduly/OknoStrojow
  SerwerStrojow (RunContext = Server), KlientStrojow (RunContext = Client)
  Zdalne/ZmienStroj (RemoteFunction), Sygnaly/SterowanieSerwera i Sygnaly/SterowanieKlienta (BindableFunction, testy)
  Przymierzalnia (Model, ModelStreamingMode Persistent): podłoga, rama lustra z taflą, podest podglądu, tablica,
  wieszak, część „E” z podpowiedzią (włącza ją serwer w Play). Miejsce: atrybut RecznyPunktStojaka (Vector3 na
  gruncie, ustawiony ręcznie w Edit, przechodzi na odbudowany kontener), inaczej stojak.punkt z ustawienia.json,
  a bez niego pierścienie wokół pierwszego SpawnLocation (wolny grunt z dala od tablicy Training Center, bazaru
  i portalu; szukanie nie widzi ścieżek).
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot, PunktStojaka, KierunekStojaka.

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener
(obiekt o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po (Ctrl+Z cofa całość); nic nie jest
zapisywane ani publikowane, Lighting nietknięty. --sucho nie importuje studio_mcp ani cel_studio.
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
import sprawdz_luau_strojow as SLS  # noqa: E402

SL = SLS.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/stroje_proba"
ZRODLA = os.path.join(TU, "zrodla")
AKTORZY_WALKI = os.path.join(REPO, "swiat", "test_walki2", "zrodla", "Aktorzy.luau")
HACZYK_WALKI = "StrojeProba"          # napis, po którym --walka poznaje, że Aktorzy.luau ma haczyk stroju

SKRYPTY = [
    ("DaneStrojow.luau", "ModuleScript", "Moduly/DaneStrojow", None),
    ("LogikaStrojow.luau", "ModuleScript", "Moduly/LogikaStrojow", None),
    ("Ubieranie.luau", "ModuleScript", "Moduly/Ubieranie", None),
    ("OknoStrojow.luau", "ModuleScript", "Moduly/OknoStrojow", None),
    ("SerwerStrojow.server.luau", "Script", "SerwerStrojow", "Server"),
    ("KlientStrojow.client.luau", "Script", "KlientStrojow", "Client"),
]
FOLDERY = ["Moduly", "Zdalne", "Sygnaly"]
INNE = [
    ("RemoteFunction", "Zdalne/ZmienStroj"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
]
ATRYBUTY_TESTOWE = ["RecznyPunktStojaka", "EmulacjaEkranu"]

# części stojaka w układzie podstawy: początek = grunt w punkcie stojaka, −Z = przód (ku startowi, gdzie staje gracz)
# (nazwa, rozmiar, położenie, kolor, materiał, kształt B/C, przezroczystość, odbicie, kolizja)
CZESCI_STOJAKA = [
    ("Podloga", (11, 0.4, 8), (0, 0.2, 0.6), "8A5A3B", "WoodPlanks", "B", 0, 0, True),
    ("Podest", (3.6, 0.6, 3.6), (0, 0.7, 1.0), "E5D3B3", "SmoothPlastic", "B", 0, 0, True),
    ("RamaL", (0.5, 8, 0.5), (-3.0, 4.4, 3.4), "F2C14E", "SmoothPlastic", "B", 0, 0, True),
    ("RamaP", (0.5, 8, 0.5), (3.0, 4.4, 3.4), "F2C14E", "SmoothPlastic", "B", 0, 0, True),
    ("RamaGora", (6.5, 0.5, 0.5), (0, 8.4, 3.4), "F2C14E", "SmoothPlastic", "B", 0, 0, True),
    ("RamaDol", (6.5, 0.4, 0.5), (0, 0.6, 3.4), "F2C14E", "SmoothPlastic", "B", 0, 0, True),
    ("Tafla", (5.5, 7.6, 0.15), (0, 4.4, 3.55), "BFE3FF", "Glass", "B", 0.25, 0.3, True),
    ("Tablica", (5.2, 1.5, 0.25), (0, 9.5, 3.4), "FFF6E0", "SmoothPlastic", "B", 0, 0, True),
    ("WieszakNoga", (0.3, 5.2, 0.3), (-4.6, 3.0, 1.6), "6B4A2F", "Wood", "B", 0, 0, True),
    ("WieszakDrazek", (0.2, 0.2, 3.4), (-4.6, 5.5, 1.6), "6B4A2F", "Wood", "B", 0, 0, True),
    ("UbranieA", (0.3, 1.6, 0.9), (-4.6, 4.6, 0.6), "2C6BE0", "Fabric", "B", 0, 0, False),
    ("UbranieB", (0.3, 1.9, 0.9), (-4.6, 4.45, 1.6), "26633A", "Fabric", "B", 0, 0, False),
    ("UbranieC", (0.3, 1.4, 0.9), (-4.6, 4.7, 2.6), "7A3FB8", "Fabric", "B", 0, 0, False),
]
PUNKT_E = (0, 2.5, -2.6)
ROZMIAR_E = (0.8, 0.8, 0.8)

NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

# ------------------------------------------------------------------------------------------------ kod Luau
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

STOJAK = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then return "STOP: brak kontenera" end
local S = __STOJAK__
local CZESCI = __CZESCI__
local stary = f:FindFirstChild("Przymierzalnia")
if stary then stary:Destroy() end
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
	local r = workspace:Raycast(Vector3.new(x, y0 + S.rzut_od, z), Vector3.new(0, -S.rzut_dlugosc, 0), par)
	return if r then r.Position.Y else nil
end
-- 1. środek szukania: pierwszy SpawnLocation (tylko odczyt), inaczej punkt zapasowy z danych
local sp = nil
for _, d in workspace:GetDescendants() do
	if d:IsA("SpawnLocation") and not d:IsDescendantOf(f) then sp = d break end
end
local s = if sp then sp.Position + Vector3.new(0, sp.Size.Y / 2, 0) else Vector3.new(S.zapas_bez_spawnu[1], S.zapas_bez_spawnu[2], S.zapas_bez_spawnu[3])
-- 2. miejsca do ominięcia (cudze — tylko odczyt): tablica Training Center, bazar, portal startowy
local omijaj = {}
for _, o in S.omijaj do
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
-- 3. ręczny punkt albo pierwszy wolny kandydat na pierścieniach wokół startu (przodem do startu)
local op = OverlapParams.new()
op.FilterType = Enum.RaycastFilterType.Exclude
op.FilterDescendantsInstances = pomin
op.RespectCanCollide = false
local function wolne(c, y)
	local ku = Vector3.new(s.X - c.X, 0, s.Z - c.Z)
	local kier = if ku.Magnitude > 0.1 then ku.Unit else Vector3.new(0, 0, -1)
	local baza = CFrame.lookAt(Vector3.new(c.X, y, c.Z), Vector3.new(c.X, y, c.Z) + kier)
	local w = S.wolne
	local zajete = workspace:GetPartBoundsInBox(baza * CFrame.new(0, w[2] / 2 + 0.3, 0.6), Vector3.new(w[1], w[2], w[3]), op)
	return #zajete == 0, baza
end
local wybrany, baza, opis = nil, nil, ""
local reczny = f:GetAttribute("RecznyPunktStojaka")
if typeof(reczny) == "Vector3" then
	local _, b = wolne(reczny, reczny.Y)
	wybrany, baza, opis = reczny, b, "ręczny (atrybut RecznyPunktStojaka)"
elseif S.punkt then
	local p = Vector3.new(S.punkt[1], S.punkt[2], S.punkt[3])
	local ok, b = wolne(p, p.Y)
	wybrany, baza, opis = p, b, "z ustawień (stojak.punkt)" .. (if ok then "" else " — UWAGA: coś stoi w miejscu stojaka")
else
	local proby = 0
	for _, r in S.promienie do
		for i = 0, S.kierunki - 1 do
			local a = i * 2 * math.pi / S.kierunki
			local c = s + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
			local daleko = true
			for _, o in omijaj do
				if (Vector3.new(c.X, 0, c.Z) - Vector3.new(o.p.X, 0, o.p.Z)).Magnitude < o.r then daleko = false end
			end
			if daleko then
				proby += 1
				local y = grunt(c.X, c.Z, s.Y)
				if y and math.abs(y - s.Y) <= S.roznica_wysokosci then
					local ok, b = wolne(c, y)
					if ok then
						wybrany, baza, opis = Vector3.new(c.X, y, c.Z), b, string.format("pierścień %g st, kierunek %d (próba %d)", r, i, proby)
						break
					end
				end
			end
		end
		if wybrany then break end
	end
	if not wybrany then
		local c = s + Vector3.new(S.promienie[#S.promienie], 0, 0)
		local _, b = wolne(c, s.Y)
		wybrany, baza = Vector3.new(c.X, s.Y, c.Z), b
		opis = "BRAK WOLNEGO MIEJSCA — punkt zapasowy, sprawdź na oko i ustaw RecznyPunktStojaka"
	end
end
-- 4. części stojaka
local m = Instance.new("Model")
m.Name = "Przymierzalnia"
m.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
m.Parent = f
for _, c in CZESCI do
	local p = Instance.new("Part")
	p.Name = c[1]
	p.Anchored = true
	p.Shape = if c[6] == "C" then Enum.PartType.Cylinder else Enum.PartType.Block
	p.Size = Vector3.new(c[2][1], c[2][2], c[2][3])
	p.CFrame = baza * CFrame.new(c[3][1], c[3][2], c[3][3])
	p.Color = Color3.fromHex(c[4])
	p.Material = Enum.Material[c[5]]
	p.Transparency = c[7]
	p.Reflectance = c[8]
	p.CanCollide = c[9]
	p.CanQuery = c[9]
	p.CanTouch = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = m
end
local tab = m:FindFirstChild("Tablica")
local sg = Instance.new("SurfaceGui")
sg.Name = "Napis"
sg.Face = Enum.NormalId.Front
sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
sg.PixelsPerStud = 50
sg.LightInfluence = 0
sg.MaxDistance = 140
local t = Instance.new("TextLabel")
t.BackgroundTransparency = 1
t.Size = UDim2.fromScale(0.94, 0.9)
t.Position = UDim2.fromScale(0.03, 0.05)
t.Text = S.napis
t.TextScaled = true
t.TextWrapped = true
t.Font = Enum.Font.FredokaOne
t.TextColor3 = Color3.fromHex("17121F")
t.Parent = sg
sg.Parent = tab
local e = Instance.new("Part")
e.Name = "E"
e.Anchored = true
e.Size = Vector3.new(S.rozmiar_e[1], S.rozmiar_e[2], S.rozmiar_e[3])
e.CFrame = baza * CFrame.new(S.punkt_e[1], S.punkt_e[2], S.punkt_e[3])
e.Transparency = 1
e.CanCollide = false
e.CanQuery = false
e.CanTouch = false
e.Parent = m
local pp = Instance.new("ProximityPrompt")
pp.Name = "PodpowiedzPrzymierzalni"
pp.ActionText = S.akcja
pp.ObjectText = S.obiekt
pp.KeyboardKeyCode = Enum.KeyCode.E
pp.HoldDuration = 0
pp.MaxActivationDistance = S.zasieg_podpowiedzi
pp.RequiresLineOfSight = false
pp.ClickablePrompt = true
pp.Enabled = false -- włącza SerwerStrojow w trybie Play (tylko w Studio)
pp:SetAttribute("Akcja", "przymierzalnia")
pp.Parent = e
m.PrimaryPart = m:FindFirstChild("Podloga")
f:SetAttribute("PunktStojaka", wybrany)
f:SetAttribute("KierunekStojaka", baza.LookVector)
local pd = m:FindFirstChild("Podest")
return string.format("OK stojak (%.1f; %.1f; %.1f) przodem (%.2f; %.2f) — %s | podest (%.1f; %.1f; %.1f) | start (%.1f; %.1f; %.1f) z %s | ominięte: %d",
	wybrany.X, wybrany.Y, wybrany.Z, baza.LookVector.X, baza.LookVector.Z, opis, pd.Position.X, pd.Position.Y, pd.Position.Z,
	s.X, s.Y, s.Z, if sp then sp:GetFullName() else "danych (brak SpawnLocation)", #omijaj)
'''

SKRYPT = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera __KONTENER__"
end
local sciezka = string.split("__SCIEZKA__", "/")
local rodzic = f
for i = 1, #sciezka - 1 do
	rodzic = rodzic:FindFirstChild(sciezka[i])
	if not rodzic then return "STOP: brak folderu " .. sciezka[i] end
end
local stary = rodzic:FindFirstChild(sciezka[#sciezka])
__TYLKO_ISTNIEJACY__
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
local uwaga = if podpowiedzi ~= 1 then " | UWAGA: podpowiedzi " .. podpowiedzi .. " zamiast 1" else ""
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


def zrodlo_walki():
    """Aktorzy.luau próby walki z haczykiem stroju (do --walka)."""
    tekst = wczytaj(AKTORZY_WALKI)
    if HACZYK_WALKI not in tekst:
        sys.exit("BŁĄD: swiat/test_walki2/zrodla/Aktorzy.luau nie ma haczyka stroju (%s) — nic nie wysyłam" % HACZYK_WALKI)
    if not SL.pierwsza_instrukcja(tekst).startswith(STRAZNIK):
        sys.exit("BŁĄD: Aktorzy.luau próby walki nie zaczyna się od strażnika Studio")
    return tekst


def sprawdz_offline(zrodla):
    ok, D = DANE.aktualny()
    print("dane.py --sprawdz: %s (skrót %s, %d klas, %d przedmiotów)"
          % ("aktualny" if ok else "NIEAKTUALNY", D["skrot"], len(D["klasy"]), len(D["przedmioty"])))
    if not ok:
        sys.exit("BŁĄD: zrodla/DaneStrojow.luau nieaktualny — uruchom python -B swiat/stroje_proba/dane.py")
    bledy, parser = SLS.sprawdz_pliki(SLS.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_strojow.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
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
def _stojak(D):
    S = dict(D["stojak"])
    S.update({"napis": D["teksty"]["tablica"], "akcja": D["teksty"]["podpowiedz_akcja"],
              "obiekt": D["teksty"]["podpowiedz_obiekt"], "punkt_e": list(PUNKT_E), "rozmiar_e": list(ROZMIAR_E)})
    return S


def kod_start(D, usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", D["kontener"]).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__TESTOWE__", ", ".join(DANE._napis(a) for a in ATRYBUTY_TESTOWE))
            .replace("__FOLDERY__", ", ".join(DANE._napis(x) for x in FOLDERY))
            .replace("__INNE__", ", ".join("{%s, %s}" % (DANE._napis(k), DANE._napis(p)) for k, p in INNE)))


def kod_stojaka(D):
    czesci = [[n, list(r), list(p), k, m, ks, t, o, kol] for n, r, p, k, m, ks, t, o, kol in CZESCI_STOJAKA]
    return (STOJAK.replace("__KONTENER__", D["kontener"]).replace("__STOJAK__", DANE._luau(_stojak(D)))
            .replace("__CZESCI__", DANE._luau(czesci)))


def kod_skryptu(kontener, sciezka, klasa, kontekst, tekst, tylko_istniejacy=False):
    kod = (SKRYPT.replace("__KONTENER__", kontener).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else "")
           .replace("__TYLKO_ISTNIEJACY__", 'if not stary or not stary:IsA("ModuleScript") then return "STOP: brak '
                    'modułu " .. sciezka[#sciezka] .. " — zbuduj próbę walki jej zbuduj.py" end' if tylko_istniejacy else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def kod_konca(D, punkt_historii="zbudowano"):
    return KONIEC.replace("__KONTENER__", D["kontener"]).replace("__PUNKT_HISTORII__", punkt_historii)


def wszystkie_kody(D):
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(D, czas="x", skrot="x"), "usun": kod_start(D, True), "stojak": kod_stojaka(D),
            "koniec": kod_konca(D), "skrypt": kod_skryptu("X", "Moduly/Y", "ModuleScript", None, "return 1"),
            "walka": kod_skryptu("TestWalki2", "Moduly/Aktorzy", "ModuleScript", None, "return 1", True)}


def plan(D):
    linie = ["  %-26s → %d części + E, przodem do startu, pierścienie %s × %d kierunków, omija %d miejsc"
             % ("Przymierzalnia (Persistent)", len(CZESCI_STOJAKA), D["stojak"]["promienie"], D["stojak"]["kierunki"],
                len(D["stojak"]["omijaj"]))]
    for linia in DANE.podsumowanie(D):
        linie.append(linia)
    return linie


# ------------------------------------------------------------------------------------------------ główna
def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/StrojeProba w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--walka", action="store_true", help="tylko moduł TestWalki2/Moduly/Aktorzy (haczyk stroju)")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/StrojeProba")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        D = {"kontener": DANE.ustawienia()["kontener"]}
        zrodla = []
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        walka = zrodlo_walki()
        print("Kontener: Workspace/%s · skrót danych %s · placeId %d · modułów i skryptów: %d"
              % (D["kontener"], D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-26s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-26s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-26s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        for linia in plan(D):
            print(linia)
        print("  %-26s → tylko z --walka: swiat/test_walki2/zrodla/Aktorzy.luau (%d znaków, haczyk stroju jest)"
              % ("TestWalki2/Moduly/Aktorzy", len(walka)))
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

            t0 = time.time()
            if a.walka:
                wykonaj('local f = workspace:FindFirstChild("TestWalki2") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera TestWalki2 z atrybutem Wygenerowane" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("TestWalki2: przed haczykiem stroju") return "OK"')
                print("  moduł walki:", wykonaj(kod_skryptu("TestWalki2", "Moduly/Aktorzy", "ModuleScript", None, walka, True)))
                wykonaj('game:GetService("ChangeHistoryService"):SetWaypoint("TestWalki2: haczyk stroju") return "OK"')
                print("gotowe (%.0f s)" % (time.time() - t0))
                return

            def skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(D["kontener"], sciezka, klasa, kontekst, tekst)))

            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (D["kontener"], D["kontener"], D["skrot"]))
                skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D, "skrypty wymienione")), time.time() - t0))
                return
            wynik = wykonaj(kod_start(D, a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or wynik != "OK":
                return
            print("  stojak:", wykonaj(kod_stojaka(D)))
            skrypty()
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca(D)), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
