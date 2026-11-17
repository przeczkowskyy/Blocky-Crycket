#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Buduje w Roblox Studio kontener Workspace/PetyProba — jajka i pety na próbę (inkubatory w lesie-pasie i w Bagnie,
wyklucie, pet przy graczu, zagroda w bazarze). Status: propozycja (PROJEKT.md).

    python -B swiat/pety_proba/zbuduj.py --sucho      # bez Studio: dane, kontrola Luau, strażniki, plan budowy
    python -B swiat/pety_proba/zbuduj.py              # buduje / odbudowuje kontener (Studio w trybie Edit)
    python -B swiat/pety_proba/zbuduj.py --skrypty    # tylko moduły i skrypty do istniejącego kontenera
    python -B swiat/pety_proba/zbuduj.py --usun       # usuwa Workspace/PetyProba (gra wraca do stanu sprzed próby)
    python -B swiat/pety_proba/zbuduj.py --studio <studio_id>   # gdy otwartych jest kilka okien Studio

Co powstaje (tylko w Workspace/PetyProba z atrybutem Wygenerowane = true; cudzych obiektów budowa NIE zmienia —
mapę lasu-pasa i bazaru tylko czyta promieniem w dół, żeby postawić jajko na mchu gniazda; w Bagnie jajko leży
w gnieździe na palach z modelu inkubatora, postawionym we własnym kontenerze na stanowisku z mapy):
  Moduly/DanePetow, Moduly/LogikaPetow, Moduly/RigPetow, Moduly/Rigi/*   ModuleScript (zrodla/; dane i rigi
                                                                          wygenerowane przez dane_petow.py)
  SerwerPetow (RunContext = Server), KlientPetow (RunContext = Client)
  Zdalne/ZdarzeniaPetow             RemoteEvent ("wyklucie", "odmowa", "lista", "wybrany", "okno" do klienta;
                                    "lista", "wybierz", "odstaw", "czekaj" do serwera)
  Sygnaly/SterowanieSerwera, Sygnaly/SterowanieKlienta   BindableFunction — haczyki testowe
  <folder jajka>/Jajko (rig z klocków, ×1,8 las / ×1,7 Bagno), <folder jajka>/<kość> <bryła> (stałe bryły z modelu
  inkubatora: tablica z szansami w SurfaceGui, w Bagnie też gniazdo na palach i latarenka), Slup (słup światła
  widoczny z daleka), Swiatlo (światło i iskry), Napis (napis nad jajkiem); foldery: Inkubator (las), InkubatorBagna
  Punkty/<jajko.punkt_e> („E inkubator”, „E inkubator Bagna”: ProximityPrompt „Podpowiedz”, Enabled = false w Edit —
  włącza serwer w Play)
  Zagroda/Tablica (+ słupki, daszek), Zagroda/E wybor (zapasowe E — gdy nie ma MiasteczkoBazarGra)
Atrybuty kontenera: Wygenerowane, Zrodlo, Zbudowano, Skrot; folder jajka: PodstawaJajka (CFrame), SkalaJajka, Jajko.

Zasady (wspólne miejsce Team Create): okno wybiera swiat/test_walki_roblox/cel_studio.py (jedno okno albo --studio,
zawsze placeId gry); KAŻDY wysyłany kod sprawdza game.PlaceId i tryb Edit; ruszany jest tylko własny kontener (obiekt
o tej nazwie bez atrybutu Wygenerowane → STOP); punkty historii przed i po (Ctrl+Z cofa całość); nic nie jest
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
import dane_petow as DANE  # noqa: E402
import sprawdz_luau_petow as SLP  # noqa: E402

SL = SLP.SL
MIEJSCE = 129485428021967  # placeId miejsca gry (to samo co swiat/test_walki_roblox/cel_studio.py)
STRAZNIK = 'if not game:GetService("RunService"):IsStudio() then'
LIMIT_ZRODLA = 199000
ZRODLO = "swiat/pety_proba"
ZRODLA = os.path.join(TU, "zrodla")
KONTENER = "PetyProba"

SKRYPTY_STALE = [
    ("DanePetow.luau", "ModuleScript", "Moduly/DanePetow", None),
    ("LogikaPetow.luau", "ModuleScript", "Moduly/LogikaPetow", None),
    ("RigPetow.luau", "ModuleScript", "Moduly/RigPetow", None),
    ("SerwerPetow.server.luau", "Script", "SerwerPetow", "Server"),
    ("KlientPetow.client.luau", "Script", "KlientPetow", "Client"),
]
FOLDERY_JAJEK = [j["folder"] for j in DANE.ustawienia()["jajka"]]   # Inkubator (las), InkubatorBagna, …
FOLDERY = ["Moduly", "Moduly/Rigi", "Zdalne", "Sygnaly", "Punkty", "Zagroda"] + FOLDERY_JAJEK
TRWALE = ["Punkty", "Zagroda"] + FOLDERY_JAJEK   # Model z ModelStreamingMode = Persistent (streaming nie wypycha)
INNE = [
    ("RemoteEvent", "Zdalne/ZdarzeniaPetow"),
    ("BindableFunction", "Sygnaly/SterowanieSerwera"),
    ("BindableFunction", "Sygnaly/SterowanieKlienta"),
]


def skrypty():
    """Lista (plik względem zrodla/, klasa, ścieżka w kontenerze, RunContext) — stałe + jeden moduł na rig."""
    w = list(SKRYPTY_STALE[:3])
    rigi = sorted(os.listdir(os.path.join(ZRODLA, "rigi"))) if os.path.isdir(os.path.join(ZRODLA, "rigi")) else []
    for plik in rigi:
        if plik.endswith(".luau"):
            w.append(("rigi/" + plik, "ModuleScript", "Moduly/Rigi/" + plik[:-5], None))
    return w + list(SKRYPTY_STALE[3:])


NAGLOWEK_MIEJSCA = ('if game.PlaceId ~= __MIEJSCE__ then return "STOP: inne miejsce (PlaceId " .. tostring(game.PlaceId) .. ")" end\n'
                    'if game:GetService("RunService"):IsRunning() then return "STOP: Studio jest w trybie Play — buduję tylko w trybie Edit" end\n')

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
CH:SetWaypoint(nazwa .. ": przed budową")
for _, d in stare do d:Destroy() end
local f = Instance.new("Folder")
f.Name = nazwa
f:SetAttribute("Wygenerowane", true)
f:SetAttribute("Zrodlo", "__ZRODLO__")
f:SetAttribute("Zbudowano", "__CZAS__")
f:SetAttribute("Skrot", "__SKROT__")
for _, sciezka in { __FOLDERY__ } do
	local czesci = string.split(sciezka, "/")
	local rodzic = f
	for i = 1, #czesci - 1 do
		rodzic = rodzic:FindFirstChild(czesci[i])
	end
	local d
	local trwale = __TRWALE__
	if trwale[czesci[#czesci]] then
		-- części w świecie: Model „Persistent” — klient ma je od wejścia (streaming), jak areny i przymierzalnia
		d = Instance.new("Model")
		d.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	else
		d = Instance.new("Folder")
	end
	d.Name = czesci[#czesci]
	d.Parent = rodzic
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

# części w świecie (po modułach — wymaga Moduly/DanePetow, RigPetow i rigu jajka); tylko we własnym kontenerze
CZESCI = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f or f:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera"
end
local M = f.Moduly
local D = require(M.DanePetow)
local L = require(M.LogikaPetow)
local Rig = require(M.RigPetow)
local I, Z = D.inkubator, D.zagroda
local wyklucz = RaycastParams.new()
wyklucz.FilterType = Enum.RaycastFilterType.Exclude
wyklucz.FilterDescendantsInstances = { f }
local raporty = {}

local function czesc(nazwa, rozmiar, cf, kolor, mat, rodzic, kolizja)
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = cf
	p.Color = Color3.fromHex(kolor)
	p.Material = Enum.Material[mat or "SmoothPlastic"]
	p.CanCollide = kolizja == true
	p.CanQuery = kolizja == true
	p.CanTouch = false
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = rodzic
	return p
end

local function punktE(rodzic, nazwa, poz, akcja, obiekt, zasieg, przytrzymaj)
	local p = czesc(nazwa, Vector3.new(0.6, 0.6, 0.6), CFrame.new(poz), "FFC94A", "SmoothPlastic", rodzic, false)
	p.Transparency = 1
	p.CastShadow = false
	local pp = Instance.new("ProximityPrompt")
	pp.Name = "Podpowiedz"
	pp.ActionText = akcja
	pp.ObjectText = obiekt
	pp.KeyboardKeyCode = Enum.KeyCode.E
	pp.HoldDuration = przytrzymaj or 0
	pp.MaxActivationDistance = zasieg
	pp.RequiresLineOfSight = false
	pp.Enabled = false
	pp.Parent = p
	return p
end

local function tekst(rodzic, t, poz, rozmiar, kolor, czcionka, maks)
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Position = poz
	l.Size = rozmiar
	l.Font = Enum.Font[czcionka or "GothamBold"]
	l.TextScaled = true
	l.TextColor3 = Color3.fromHex(kolor)
	l.TextXAlignment = Enum.TextXAlignment.Left
	l.Text = t
	l.Parent = rodzic
	if maks then -- jednakowa wielkość w wierszach tablicy (dłuższy tekst może się tylko zmniejszyć)
		local o = Instance.new("UITextSizeConstraint")
		o.MaxTextSize = maks
		o.Parent = l
	end
	return l
end

local function grunt(x, z, domyslny)
	local r = workspace:Raycast(Vector3.new(x, 60, z), Vector3.new(0, -120, 0), wyklucz)
	if r then
		return r.Position.Y, r.Instance:GetFullName()
	end
	return domyslny, "dane (promień nic nie trafił)"
end

------------------------------------------------------------------ inkubatory (jeden na jajko z D.jajka: las-pas, Bagno)
local function inkubator(J)
	local ink = f[J.folder]
	local PJ = J.polozenie
	local stan = CFrame.new(PJ.gniazdo[1], PJ.gniazdo[2], PJ.gniazdo[3]) * CFrame.Angles(0, math.rad(PJ.obrot), 0)
	-- jajko na mchu gniazda z mapy (las: promień w dół) albo w gnieździe z modelu inkubatora (wysokość z modelu)
	local y, zrodloY = J.y_jajka, "model inkubatora"
	if J.jajko_na_mchu then
		local r = workspace:Raycast(stan.Position + Vector3.new(0, 12, 0), Vector3.new(0, -24, 0), wyklucz)
		if r and r.Position.Y - PJ.gniazdo[2] > I.mech_od and r.Position.Y - PJ.gniazdo[2] < I.mech_do then
			y, zrodloY = r.Position.Y - PJ.gniazdo[2], r.Instance:GetFullName()
		end
	end
	local podstawa = stan * CFrame.new(0, y, 0)
	ink:SetAttribute("PodstawaJajka", podstawa)
	ink:SetAttribute("SkalaJajka", J.skala_jajka)
	ink:SetAttribute("Jajko", J.id)
	local dj = require(M.Rigi[J.rig])
	local jajko, u = Rig.zbuduj(dj, J.skala_jajka, "Jajko")
	jajko.Parent = ink
	jajko:PivotTo(podstawa * u.korzen.CFrame)
	table.insert(raporty, string.format("%s: jajko na y %.2f (%s)", J.id, y, zrodloY))
	local gora = dj.wysokosc * J.skala_jajka -- wierzch jajka nad podstawą

	-- stałe bryły z modelu inkubatora (tablica z jawnymi szansami; w Bagnie też gniazdo na palach i latarenka);
	-- wiersz: kość, kształt, nazwa, poz, obrót, rozmiar, kolor, materiał, siatka
	local T = J.stale
	local papier
	local kolizja = {}
	for _, n in I.kolizja do
		kolizja[n] = true
	end
	for _, c in T.czesci do
		local p
		if c[2] == 3 then
			p = Instance.new("WedgePart")
		elseif c[2] == 4 then
			p = Instance.new("CornerWedgePart")
		else
			p = Instance.new("Part")
			if c[2] == 1 then
				p.Shape = Enum.PartType.Ball
			elseif c[2] == 2 then
				p.Shape = Enum.PartType.Cylinder
			end
		end
		p.Name = c[1] .. " " .. c[3]
		p.Anchored = true
		p.Size = Vector3.new(c[10], c[11], c[12])
		p.CFrame = stan * CFrame.new(c[4], c[5], c[6]) * CFrame.fromOrientation(c[7], c[8], c[9])
		p.Color = Color3.fromHex(c[13])
		local mat = T.materialy[c[14] + 1]
		p.Material = Enum.Material[mat[1]]
		p.Reflectance = mat[2]
		p.CanCollide = kolizja[c[3]] == true
		p.CanQuery = p.CanCollide
		p.CanTouch = false
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		if c[15] ~= "" then
			local sm = Instance.new("SpecialMesh")
			sm.MeshType = Enum.MeshType[c[15]]
			sm.Parent = p
		end
		if p.Material == Enum.Material.Neon and math.min(p.Size.X, p.Size.Y, p.Size.Z) >= 0.3 then
			local pl = Instance.new("PointLight") -- ognik w latarence świeci naprawdę
			pl.Color = p.Color
			pl.Range = 9
			pl.Brightness = 1.2
			pl.Parent = p
		end
		p.Parent = ink
		if c[3] == D.modele.papier then
			papier = p
		end
	end
	if papier then
		local s = Instance.new("SurfaceGui")
		s.Name = "Szanse"
		s.Face = Enum.NormalId.Back -- przód tablicy w modelu (+Z danych) to po zamianie układu ściana Back części
		s.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		s.PixelsPerStud = 120
		s.LightInfluence = 0
		s.Parent = papier
		local tt = tekst(s, J.tytul, UDim2.fromScale(0.03, 0.02), UDim2.fromScale(0.94, 0.15), "3E2A16", "LuckiestGuy", 40)
		tt.TextXAlignment = Enum.TextXAlignment.Center
		local tc = tekst(s, L.opisCeny(D, J), -- „cena: 300 Złota” (stała) albo „od … · rośnie …” (rosnąca)
			UDim2.fromScale(0.03, 0.17), UDim2.fromScale(0.94, 0.08), "5E3A22", nil, 17)
		tc.TextXAlignment = Enum.TextXAlignment.Center
		tekst(s, D.teksty.szanse_tytul, UDim2.fromScale(0.03, 0.27), UDim2.fromScale(0.94, 0.08), "3E2A16", nil, 17)
		for i, w in L.wierszeSzans(D, J) do
			local yy = 0.36 + (i - 1) * 0.126
			local kw = Instance.new("Frame")
			kw.Position = UDim2.fromScale(0.03, yy + 0.02)
			kw.Size = UDim2.fromScale(0.045, 0.075)
			kw.BackgroundColor3 = Color3.fromHex(w.kolor)
			kw.BorderSizePixel = 0
			kw.Parent = s
			local o = Instance.new("UIStroke")
			o.Color = Color3.fromHex("3E2A16")
			o.Thickness = 1
			o.Parent = kw
			tekst(s, w.szansa, UDim2.fromScale(0.09, yy), UDim2.fromScale(0.12, 0.11), "2B2118", nil, 22)
			tekst(s, w.nazwa, UDim2.fromScale(0.21, yy), UDim2.fromScale(0.36, 0.11), "2B2118", nil, 22)
			tekst(s, w.skill, UDim2.fromScale(0.57, yy + 0.015), UDim2.fromScale(0.41, 0.08), "5E3A22", "Gotham", 14)
		end
		table.insert(raporty, string.format("%s: %d stałych brył, szanse w SurfaceGui", J.id, #T.czesci))
	else
		table.insert(raporty, J.id .. ": UWAGA brak tablicy szans")
	end

	-- słup światła (widać z daleka), światło i iskry, napis nad jajkiem — w kolorze jajka
	local slup = czesc("Slup", Vector3.new(I.wysokosc_slupa, I.promien_slupa * 2, I.promien_slupa * 2),
		CFrame.new(podstawa.Position + Vector3.new(0, gora + 1 + I.wysokosc_slupa / 2, 0)) * CFrame.Angles(0, 0, math.rad(90)),
		J.kolor_swiatla, "Neon", ink, false)
	slup.Shape = Enum.PartType.Cylinder
	slup.Transparency = I.przezroczystosc_slupa
	slup.CastShadow = false
	local swiatlo = czesc("Swiatlo", Vector3.new(0.4, 0.4, 0.4), CFrame.new(podstawa.Position + Vector3.new(0, gora * 0.55, 0)),
		J.kolor_swiatla, "SmoothPlastic", ink, false)
	swiatlo.Transparency = 1
	swiatlo.CastShadow = false
	local pl = Instance.new("PointLight")
	pl.Color = Color3.fromHex(J.kolor_swiatla)
	pl.Range = 16
	pl.Brightness = 1.4
	pl.Parent = swiatlo
	local iskry = Instance.new("ParticleEmitter")
	iskry.Name = "Iskry"
	iskry.Color = ColorSequence.new(Color3.fromHex(J.kolor_swiatla))
	iskry.LightEmission = 1
	iskry.Rate = 5
	iskry.Lifetime = NumberRange.new(1.5, 2.5)
	iskry.Speed = NumberRange.new(1, 2.5)
	iskry.SpreadAngle = Vector2.new(180, 180)
	iskry.Size = NumberSequence.new(0.35, 0)
	iskry.Parent = swiatlo
	local napis = czesc("Napis", Vector3.new(0.4, 0.4, 0.4), CFrame.new(podstawa.Position + Vector3.new(0, gora + 2.4, 0)),
		J.kolor_swiatla, "SmoothPlastic", ink, false)
	napis.Transparency = 1
	napis.CastShadow = false
	local b = Instance.new("BillboardGui")
	b.Name = "Tytul"
	b.Size = UDim2.fromOffset(320, 64)
	b.LightInfluence = 0
	b.MaxDistance = I.widac_z_daleka
	b.StudsOffsetWorldSpace = Vector3.new(0, 0.6, 0)
	b.Parent = napis
	local tt = tekst(b, J.tytul, UDim2.fromScale(0, 0), UDim2.fromScale(1, 0.62), J.kolor_swiatla, "LuckiestGuy")
	tt.TextXAlignment = Enum.TextXAlignment.Center
	tt.TextStrokeTransparency = 0.2
	local tc = tekst(b, L.opisCeny(D, J) .. " · " .. D.teksty.szanse_na_tablicy,
		UDim2.fromScale(0, 0.62), UDim2.fromScale(1, 0.38), "FFF6E0")
	tc.TextXAlignment = Enum.TextXAlignment.Center
	tc.TextStrokeTransparency = 0.2

	local e = PJ.e
	punktE(f.Punkty, J.punkt_e, Vector3.new(e[1], e[2] + I.e_wyzej, e[3]), I.napis_akcja, J.tytul, I.promien_e,
		I.przytrzymaj_s)
	table.insert(raporty, string.format("%s: E (%.1f; %.1f; %.1f)", J.punkt_e, e[1], e[2] + I.e_wyzej, e[3]))
end
for _, J in D.jajka do
	inkubator(J)
end

------------------------------------------------------------------ zagroda w bazarze: tablica i zapasowe E
local G = D.polozenia
local zg = f.Zagroda
local tp = G.zagroda_tablica
local kier = Vector3.new(G.zagroda_kier[1], 0, G.zagroda_kier[3])
local yg, zrodloG = grunt(tp[1], tp[3], tp[2])
local sz, wy = Z.tablica_rozmiar[1], Z.tablica_rozmiar[2]
local baza = CFrame.lookAt(Vector3.new(tp[1], yg, tp[3]), Vector3.new(tp[1], yg, tp[3]) + kier)
czesc("Tablica", Vector3.new(sz, wy, 0.3), baza * CFrame.new(0, 1.2 + wy / 2, 0), "6B4A2E", "WoodPlanks", zg, true)
for _, zn in { -1, 1 } do
	czesc("Tablica slupek", Vector3.new(0.4, 1.4 + wy, 0.4), baza * CFrame.new(zn * (sz / 2 + 0.1), (1.4 + wy) / 2, 0.05),
		"4A3220", "Wood", zg, true)
end
czesc("Tablica daszek", Vector3.new(sz + 0.8, 0.3, 0.9), baza * CFrame.new(0, 1.35 + wy + 0.2, 0.05), "4A3220", "Wood", zg, true)
local pe = (baza * CFrame.new(0, 2.4, -2.4)).Position
punktE(zg, "E wybor", pe, Z.napis_e, Z.napis_tablicy .. " (" .. Z.napis_proby .. ")", 8, 0)
table.insert(raporty, string.format("tablica zagrody: grunt %.2f (%s)", yg, zrodloG))
return "OK " .. table.concat(raporty, " | ")
'''

KONIEC = r'''
local f = workspace:FindFirstChild("__KONTENER__")
if not f then return "STOP: brak kontenera" end
local razem, skrypty, czesci = 0, 0, 0
for _, d in f:GetDescendants() do
	razem += 1
	if d:IsA("LuaSourceContainer") then skrypty += 1 end
	if d:IsA("BasePart") then czesci += 1 end
end
game:GetService("ChangeHistoryService"):SetWaypoint("__KONTENER__: __PUNKT_HISTORII__")
local uwaga = if skrypty ~= __OCZEKIWANE__ then " | UWAGA: skryptów " .. skrypty .. " zamiast __OCZEKIWANE__" else ""
return "instancji: " .. razem .. ", skryptów: " .. skrypty .. ", części: " .. czesci .. ", Skrot = " .. tostring(f:GetAttribute("Skrot")) .. uwaga
'''


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
    for plik, klasa, sciezka, kontekst in skrypty():
        pelna = os.path.join(ZRODLA, *plik.split("/"))
        if not os.path.isfile(pelna):
            braki.append(plik)
            continue
        wynik.append((sciezka, klasa, kontekst, wczytaj(pelna), plik))
    if braki:
        print("BŁĄD: brak plików w zrodla/: " + ", ".join(braki))
        sys.exit(2)
    return wynik


def sprawdz_offline(zrodla):
    zle, D, _pliki = DANE.aktualny()
    print("dane_petow.py --sprawdz: %s (skrót %s, przypadków %d)" % ("aktualne" if not zle else "NIEAKTUALNE: " + ", ".join(zle),
                                                                    D["skrot"], sum(len(v) for v in D["przypadki"].values())))
    if zle:
        sys.exit("BŁĄD: zrodla/ nieaktualne — uruchom python -B swiat/pety_proba/dane_petow.py")
    if D["kontener"] != KONTENER:
        sys.exit("BŁĄD: D.kontener (%s) ≠ %s" % (D["kontener"], KONTENER))
    bledy, parser = SLP.sprawdz_pliki(SLP.pliki_pakietu(), wypisz=print)
    print("sprawdz_luau_petow.py: %d plików, %s%s" % (len(zrodla), "OK" if not bledy else "BŁĘDY: %d" % len(bledy),
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


def _napis(s):
    return DANE._napis(s)


def kod_start(usun=False, czas="", skrot=""):
    return (START.replace("__KONTENER__", KONTENER).replace("__USUN__", "true" if usun else "false")
            .replace("__ZRODLO__", ZRODLO).replace("__CZAS__", czas).replace("__SKROT__", skrot)
            .replace("__FOLDERY__", ", ".join(_napis(x) for x in FOLDERY))
            .replace("__TRWALE__", "{ %s }" % ", ".join("[%s] = true" % _napis(x) for x in TRWALE))
            .replace("__INNE__", ", ".join("{%s, %s}" % (_napis(k), _napis(p)) for k, p in INNE)))


def kod_skryptu(sciezka, klasa, kontekst, tekst):
    kod = (SKRYPT.replace("__KONTENER__", KONTENER).replace("__SCIEZKA__", sciezka).replace("__KLASA__", klasa)
           .replace("__RUNCONTEXT__", "s.RunContext = Enum.RunContext.%s" % kontekst if kontekst else ""))
    return kod.replace("__ZRODLO__", dlugi_napis(tekst))


def kod_czesci():
    return CZESCI.replace("__KONTENER__", KONTENER)


def kod_konca(punkt_historii="zbudowano"):
    return (KONIEC.replace("__KONTENER__", KONTENER).replace("__OCZEKIWANE__", str(len(skrypty())))
            .replace("__PUNKT_HISTORII__", punkt_historii))


def wszystkie_kody():
    """Kod wysyłany do Studio (bez skryptów) — do --sucho i do testu parsowania."""
    return {"start": kod_start(czas="x", skrot="x"), "usun": kod_start(True), "czesci": kod_czesci(),
            "koniec": kod_konca()}


def main():
    for strumien in (sys.stdout, sys.stderr):
        if hasattr(strumien, "reconfigure"):
            strumien.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Buduje kontener Workspace/PetyProba w Roblox Studio")
    ap.add_argument("--sucho", action="store_true", help="bez Studio: sprawdź dane i źródła, pokaż plan")
    ap.add_argument("--skrypty", action="store_true", help="tylko moduły i skrypty do istniejącego kontenera")
    ap.add_argument("--usun", action="store_true", help="usuń Workspace/PetyProba")
    ap.add_argument("--studio", default=None, help="studio_id (gdy otwartych jest kilka okien Studio)")
    a = ap.parse_args()

    if a.usun:
        zrodla, D = [], None
    else:
        zrodla = zrodla_pakietu()
        D = sprawdz_offline(zrodla)
        print("Kontener: Workspace/%s · Skrot danych: %s · placeId %d · modułów i skryptów: %d"
              % (KONTENER, D["skrot"], MIEJSCE, len(zrodla)))
        print("  %-26s → %s" % ("Folder", ", ".join(FOLDERY)))
        for klasa, sciezka in INNE:
            print("  %-26s → %s" % (sciezka, klasa))
        for sciezka, klasa, kontekst, tekst, plik in zrodla:
            print("  %-26s → %s%s, zrodla/%s (%d znaków)" % (sciezka, klasa, " [RunContext=%s]" % kontekst if kontekst else "",
                                                           plik, len(tekst)))
        G = D["polozenia"]
        for j in D["jajka"]:
            print("  %s (%s): gniazdo %s (obrót %s°), E %s „%s”, jajko y %.2f ×%s, stałych brył %d, cena %d (%s; licznik %s)"
                  % (j["id"], j["folder"], j["polozenie"]["gniazdo"], j["polozenie"]["obrot"], j["polozenie"]["e"],
                     j["punkt_e"], j["y_jajka"], j["skala_jajka"], len(j["stale"]["czesci"]),
                     DANE.LP.cena(D, j, 0), j["cena"]["tryb"], D["licznik_ceny"]["tryb"]))
        print("  zagroda: E %s, tablica %s, miejsc na pety %d" % (G["zagroda_e"], G["zagroda_tablica"],
                                                                 len(G["miejsca_petow"])))
        kody = wszystkie_kody()
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

            def wyslij_skrypty():
                for sciezka, klasa, kontekst, tekst, plik in zrodla:
                    print("  skrypt:", wykonaj(kod_skryptu(sciezka, klasa, kontekst, tekst)))

            t0 = time.time()
            if a.skrypty:
                wykonaj('local f = workspace:FindFirstChild("%s") if not f or f:GetAttribute("Wygenerowane") ~= true '
                        'then return "STOP: brak kontenera — zbuduj całość" end '
                        'game:GetService("ChangeHistoryService"):SetWaypoint("%s: przed wymianą skryptów") '
                        'f:SetAttribute("Skrot", "%s") return "OK"' % (KONTENER, KONTENER, D["skrot"]))
                wyslij_skrypty()
                print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca("skrypty wymienione")), time.time() - t0))
                return
            wynik = wykonaj(kod_start(a.usun, time.strftime("%Y-%m-%dT%H:%M:%S"), "" if a.usun else D["skrot"]))
            print("start:", wynik)
            if a.usun or wynik != "OK":
                return
            wyslij_skrypty()
            print("części:", wykonaj(kod_czesci()))
            print("gotowe: %s (%.0f s)" % (wykonaj(kod_konca()), time.time() - t0))
    except StudioError as e:
        sys.exit("BŁĄD Studio: %s" % e)


if __name__ == "__main__":
    main()
