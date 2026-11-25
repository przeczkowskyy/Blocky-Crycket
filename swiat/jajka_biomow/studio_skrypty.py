# -*- coding: utf-8 -*-
"""Skrypty ustawiające jajka biomów w Studio (na wzór tools/studio/jajo_lesne_ustaw.luau Pawła) — generowane
z jednego szablonu, żeby oba jajka miały te same kroki: studio/jajko_bagno_ustaw.luau, studio/jajko_dzungla_ustaw.luau.

    python -B swiat/jajka_biomow/studio_skrypty.py

Skryptów NIE uruchamiam (25.11 Studio ma inny agent). Uruchamia je etap „Studio” po wgraniu modelu — kroki
w swiat/jajka_biomow/PROJEKT.md.
"""
import os

TU = os.path.dirname(os.path.abspath(__file__))

SZABLON = r'''-- %(NAZWA)s z pakietu swiat/jajka_biomow (Karol 25.11, na wzór leśnego jaja Pawła: tools/studio/jajo_lesne_ustaw.luau)
-- -> gotowy model Workspace/%(KONTENER)s/"%(NAZWA)s". Wygenerowane przez swiat/jajka_biomow/studio_skrypty.py — zmiany
-- rób w generatorze. Uruchom RAZ w trybie Edit (MCP execute_luau), po wstawieniu modelu z GLB
-- (swiat/jajka_biomow/modele/jajko_%(BIOM)s.glb) jako Workspace/%(KONTENER)s/%(IMPORT)s.
-- Co robi (to samo co u Pawła): skala ×1,5 (1 m pliku = 1 stud), zakotwiczenie, kolory siatek bez tekstury
-- (Neon jak kryształy leśnego), na Egg i kawałkach skorupy SurfaceAppearance: kolor z obrazu, który utworzył importer
-- (czytany z Egg.TextureID), świecące pęknięcia z maski %(MASKA)s; kawałki skorupy w spoczynku niewidoczne;
-- niewidzialny korzeń (PrimaryPart) w najniższym punkcie z przodem = +Z pliku. Nie rusza żadnego istniejącego
-- jajka (stare gniazda z klocków w PetyProba zostają) — model staje obok stanowiska, do obejrzenia.
local CHS = game:GetService("ChangeHistoryService")
local KONTENER = "%(KONTENER)s"
local IMPORT = "%(IMPORT)s"
local NAZWA = "%(NAZWA)s"
local SKALA = 1.5
-- maska blasku pęknięć: wgrać swiat/jajka_biomow/tekstury/%(MASKA)s (manifest: %(MANIFEST)s) i wpisać ID
local BLASK = "rbxassetid://%(BLASK_ID)s"
local KOLOR_ZYL = %(KOLOR_ZYL)s -- EmissiveTint pęknięć (u Pawła 83, 232, 154)
local KOLOR_BLASKU = %(KOLOR_BLASKU)s -- jasny środek rdzenia i słupa
-- miejsce: obok stanowiska jajka z mapy (%(STANOWISKO)s), przesunięte o PRZESUNIECIE, żeby nie wejść
-- w stare gniazdo; bez mapy — punkt ze znaczników (%(ZNACZNIKI)s). Przód (LookVector) w stronę PRZOD.
local STANOWISKO = "%(STANOWISKO)s"
local ZAPAS = Vector3.new(%(ZAPAS)s)
local PRZESUNIECIE = Vector3.new(%(PRZESUNIECIE)s)
local PRZOD = Vector3.new(%(PRZOD)s)

local KOLORY = { -- nazwa siatki -> kolor, materiał, przezroczystość (nil = siatka z teksturą atlasu: kolor biały)
%(KOLORY)s
}
local CIEN = { Egg = true, %(CIEN)s = true }

local function sciezka(s: string): Instance?
	local w: Instance? = workspace
	for czesc in string.gmatch(s, "[^/]+") do
		if czesc ~= "Workspace" then
			w = w and w:FindFirstChild(czesc)
		end
	end
	return w
end

local k = workspace:FindFirstChild(KONTENER)
assert(k, "brak Workspace/" .. KONTENER .. " (wstaw tam model z GLB jako " .. IMPORT .. ")")
local imp = k:FindFirstChild(IMPORT)
assert(imp, "brak " .. KONTENER .. "/" .. IMPORT)
assert(BLASK ~= "rbxassetid://0", "wpisz ID maski blasku (BLASK) przed uruchomieniem")
local egg = imp:FindFirstChild("Egg", true)
assert(egg and egg:IsA("MeshPart"), "brak siatki Egg w imporcie")
local kolorTekstury = (egg :: MeshPart).TextureID
if kolorTekstury == "" then -- nowszy importer może dać SurfaceAppearance zamiast TextureID
	local saImp = egg:FindFirstChildWhichIsA("SurfaceAppearance")
	if saImp then
		kolorTekstury = saImp.ColorMap
	end
end
assert(kolorTekstury ~= "", "Egg bez tekstury koloru — importer nie utworzył obrazu (sprawdź import GLB)")

local rec = CHS:TryBeginRecording(NAZWA .. ": ustawienie modelu")
local m = Instance.new("Model")
m.Name = NAZWA .. " nowe"
local dol, sx, sz = math.huge, 0, 0
local czesci = {}
for _, d in ipairs(imp:GetDescendants()) do
	if d:IsA("MeshPart") then
		table.insert(czesci, d)
	end
end
for _, d in ipairs(czesci) do
	d.Anchored = true
	d.CanCollide = false
	d.CanTouch = false
	d.CanQuery = false
	d.CastShadow = CIEN[d.Name] == true
	pcall(function()
		d.CollisionFidelity = Enum.CollisionFidelity.Box -- i tak bez kolizji; mniej pamięci na telefonie
	end)
	local kol = KOLORY[d.Name]
	if d.Name == "Egg" or string.sub(d.Name, 1, 5) == "Shell" or kol then
		for _, stara in ipairs(d:GetChildren()) do
			if stara:IsA("SurfaceAppearance") then
				stara:Destroy() -- z importu; własną dokładamy niżej (jajo) albo kolor bez tekstury (Neon)
			end
		end
	end
	if d.Name == "Egg" or string.sub(d.Name, 1, 5) == "Shell" then
		-- jajo i kawałki skorupy: tekstura + świecące pęknięcia (jak u Pawła)
		d.Color = Color3.new(1, 1, 1)
		d.Material = Enum.Material.SmoothPlastic
		d.TextureID = ""
		local sa = Instance.new("SurfaceAppearance")
		sa.ColorMap = kolorTekstury
		local sx2: any = sa
		pcall(function()
			sx2.EmissiveMaskContent = Content.fromUri(BLASK)
			sx2.EmissiveStrength = 1
			sx2.EmissiveTint = KOLOR_ZYL
		end)
		sa.Parent = d
		if d.Name ~= "Egg" then
			d.Transparency = 1
		end
	elseif kol then
		d.Color, d.Material = kol[1], kol[2]
		d.Transparency = kol[3] or 0
		d.TextureID = ""
	else
		-- siatki z atlasem ozdób: tekstura z importu, kolor biały
		d.Color = Color3.new(1, 1, 1)
		d.Material = Enum.Material.SmoothPlastic
	end
	dol = math.min(dol, d.Position.Y - d.Size.Y / 2)
	if d.Name == "Egg" then
		sx, sz = d.Position.X, d.Position.Z
	end
	d.Parent = m
end
local woda = m:FindFirstChild("Water")
if woda and woda:IsA("BasePart") then
	woda.Reflectance = 0.2
	woda.Transparency = 0.1
end
local korzen = Instance.new("Part")
korzen.Name = "Korzen"
korzen.Size = Vector3.new(0.4, 0.4, 0.4)
korzen.Transparency = 1
korzen.Anchored, korzen.CanCollide, korzen.CanTouch, korzen.CanQuery = true, false, false, false
-- przód modelu = +Z pliku (po imporcie GLB +Z pliku = +Z świata, sprawdzone przez Pawła na leśnym jaju)
korzen.CFrame = CFrame.lookAt(Vector3.new(sx, dol, sz), Vector3.new(sx, dol, sz + 1))
korzen.Parent = m
m.PrimaryPart = korzen
m.Parent = k
m:ScaleTo(SKALA)

-- miejsce: stanowisko z mapy (albo zapas), przesunięcie, wysokość gruntu promieniem w dół
local st = sciezka(STANOWISKO)
local baza = ZAPAS
if st and st:IsA("BasePart") then
	baza = st.Position
elseif st and st:IsA("Model") then
	baza = st:GetPivot().Position
elseif st then -- folder punktów: środek jego części
	local suma, ile = Vector3.zero, 0
	for _, d in ipairs(st:GetDescendants()) do
		if d:IsA("BasePart") then
			suma += d.Position
			ile += 1
		end
	end
	if ile > 0 then
		baza = suma / ile
	end
end
local miejsce = baza + PRZESUNIECIE
local rp = RaycastParams.new()
rp.FilterType = Enum.RaycastFilterType.Exclude
rp.FilterDescendantsInstances = { k }
local traf = workspace:Raycast(miejsce + Vector3.new(0, 150, 0), Vector3.new(0, -400, 0), rp)
if traf then
	miejsce = Vector3.new(miejsce.X, traf.Position.Y, miejsce.Z)
end
m:PivotTo(CFrame.lookAt(miejsce, miejsce + Vector3.new(PRZOD.X, 0, PRZOD.Z)))
m:SetAttribute("Wygenerowane", true)
m:SetAttribute("Zrodlo", "swiat/jajka_biomow (Karol 25.11), wzór: leśne jajo Pawła")
m:SetAttribute("JajkoId", "%(JAJKO_ID)s")
m:SetAttribute("Biom", "%(BIOM)s")
m:SetAttribute("KolorZyl", KOLOR_ZYL)
m:SetAttribute("KolorBlasku", KOLOR_BLASKU)
m:SetAttribute("RdzenY", 1.59) -- nad korzeniem, przed skalą (stała z klienta Pawła)
m:SetAttribute("Zajety", true)
imp:Destroy()
local stary = k:FindFirstChild(NAZWA)
if stary then
	stary:Destroy() -- poprzednia wersja TEGO modelu (ponowne uruchomienie)
end
m.Name = NAZWA
-- punkt podpowiedzi nad jajem (bez ProximityPrompt — podpina go etap scenki)
local punkt = k:FindFirstChild("Punkt " .. NAZWA)
if not punkt then
	local p = Instance.new("Part")
	p.Name = "Punkt " .. NAZWA
	p.Anchored, p.CanCollide, p.CanTouch, p.CanQuery = true, false, false, false
	p.Transparency = 1
	p.Size = Vector3.new(1, 1, 1)
	p.Parent = k
	punkt = p
end
(punkt :: BasePart).CFrame = CFrame.new(miejsce + Vector3.new(0, 3, 0))
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
local _, rozmiar = m:GetBoundingBox()
local sa: any = (m:FindFirstChild("Egg") :: Instance):FindFirstChildWhichIsA("SurfaceAppearance")
local okE, blask = pcall(function()
	return tostring(sa.EmissiveMaskContent)
end)
return string.format("ok: %%d części, rozmiar %%.1f × %%.1f × %%.1f, pivot %%s, stanowisko %%s, blask: %%s", #czesci, rozmiar.X,
	rozmiar.Y, rozmiar.Z, tostring(m:GetPivot().Position), st and "z mapy" or "zapas", okE and blask or "brak")
'''

KONFIG = {
    "bagno": dict(
        BLASK_ID="0",  # ID obrazu tekstury/bagno_jajo_blask.png po wgraniu (etap Studio)
        NAZWA="Jajko Bagna", IMPORT="JajkoBagnaImport", JAJKO_ID="jajko_bagienne", MASKA="bagno_jajo_blask.png",
        MANIFEST="JajkoBagnaBlask", KOLOR_ZYL="Color3.fromRGB(155, 255, 79)", KOLOR_BLASKU='Color3.fromHex("F4FFD2")',
        STANOWISKO="Workspace/BagnoPas/Punkty/StanowiskoJajka", ZNACZNIKI="swiat/bagno_pas/krotki/znaczniki.json",
        ZAPAS="1548.88, 0, -680", PRZESUNIECIE="0, 0, 9", PRZOD="-1, 0, 0", CIEN="MudBed",
        KOLORY="\n".join([
            '\tCrystals = { Color3.fromRGB(155, 255, 79), Enum.Material.Neon },',
            '\tShards = { Color3.fromRGB(155, 255, 79), Enum.Material.Neon },',
            '\tBubbles = { Color3.fromRGB(180, 255, 110), Enum.Material.Neon, 0.15 },',
            '\tMushroomStems = { Color3.fromRGB(215, 210, 184), Enum.Material.SmoothPlastic },',
            '\tMushroomCaps = { Color3.fromRGB(122, 62, 158), Enum.Material.SmoothPlastic },',
            '\tMushroomSpots = { Color3.fromRGB(190, 255, 120), Enum.Material.Neon },',
        ])),
    "dzungla": dict(
        BLASK_ID="0",  # ID obrazu tekstury/dzungla_jajo_blask.png po wgraniu (etap Studio)
        NAZWA="Jajko Dżungli", IMPORT="JajkoDzungliImport", JAJKO_ID="jajko_dzungli", MASKA="dzungla_jajo_blask.png",
        MANIFEST="JajkoDzungliBlask", KOLOR_ZYL="Color3.fromRGB(255, 95, 168)", KOLOR_BLASKU='Color3.fromHex("FFE6F3")',
        STANOWISKO="Workspace/DzunglaPas/Punkty/StanowiskoJajka", ZNACZNIKI="swiat/dzungla_pas/krotki/znaczniki.json",
        ZAPAS="1968.88, 0, -680", PRZESUNIECIE="0, 0, 9", PRZOD="-1, 0, 0", CIEN="StoneBase",
        KOLORY="\n".join([
            '\tCrystals = { Color3.fromRGB(255, 140, 26), Enum.Material.Neon },',
            '\tShards = { Color3.fromRGB(255, 170, 60), Enum.Material.Neon },',
        ])),
}


def main():
    wyj = os.path.join(TU, "studio")
    os.makedirs(wyj, exist_ok=True)
    for biom, k in KONFIG.items():
        d = dict(k, BIOM=biom, KONTENER="JajkaBiomowPodglad")
        sc = os.path.join(wyj, "jajko_%s_ustaw.luau" % biom)
        with open(sc, "w", encoding="utf-8", newline="\n") as f:
            f.write(SZABLON % d)
        print("skrypt:", os.path.relpath(sc, os.path.dirname(os.path.dirname(TU))))


if __name__ == "__main__":
    main()
