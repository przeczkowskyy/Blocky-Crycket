--[[
	Budowa aktorów (uruchamiane w Roblox Studio, tryb Edit, przez zbuduj.py → execute_luau).
	Tworzy WYŁĄCZNIE Workspace/TestWalki/Aktorzy: dwa rigi R15 jako szablony — „Rycerz” i „Zbir”.

	Rig powstaje udokumentowaną drogą: Players:CreateHumanoidModelFromDescription (domyślny, klockowy R15).
	Wyposażenie to zwykłe części przyspawane (WeldConstraint) do części ciała — żadnych cudzych modeli ani uploadów.
	HumanoidRootPart jest zakotwiczony, wszystkie części mają wyłączone kolizje (gracz przez nie przechodzi).
	Klient nie animuje szablonów: na czas walki chowa je lokalnie i odtwarza walkę na własnych klonach.
]]
local kontener = workspace:FindFirstChild("TestWalki")
if not kontener or kontener:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera Workspace/TestWalki z atrybutem Wygenerowane"
end
local U = require(kontener.Moduly.Ustawienia)
local Players = game:GetService("Players")

local stare = kontener:FindFirstChild("Aktorzy")
if stare then
	stare:Destroy()
end
local aktorzy = Instance.new("Folder")
aktorzy.Name = "Aktorzy"

local M = Enum.Material
local rad = math.rad
local licznik = 0

local function nowyRig(nazwa: string, strona: string, kolory: { [string]: string }): Model
	local model = Players:CreateHumanoidModelFromDescription(Instance.new("HumanoidDescription"), Enum.HumanoidRigType.R15)
	model.Name = nazwa
	model:SetAttribute("Strona", strona)
	-- porządki: domyślny skrypt Animate (nie jest potrzebny — animacje puszcza Odtwarzacz), BodyColors i opis,
	-- które przy klonowaniu nadpisałyby nasze kolory
	for _, d in model:GetChildren() do
		if d:IsA("LuaSourceContainer") or d:IsA("BodyColors") then
			d:Destroy()
		end
	end
	local hum = model:FindFirstChildOfClass("Humanoid") :: Humanoid
	local opis = hum:FindFirstChildOfClass("HumanoidDescription")
	if opis then
		opis:Destroy()
	end
	hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None
	hum.HealthDisplayType = Enum.HumanoidHealthDisplayType.AlwaysOff
	hum.RequiresNeck = false
	hum.BreakJointsOnDeath = false
	hum.AutomaticScalingEnabled = false
	hum.EvaluateStateMachine = false -- statysta: bez maszyny stanów i fizyki humanoida
	for _, p in model:GetDescendants() do
		if p:IsA("BasePart") then
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
			p.Anchored = p.Name == "HumanoidRootPart"
			p.Material = M.SmoothPlastic
			local kolor = kolory[p.Name]
			if kolor then
				p.Color = Color3.fromHex(kolor)
			end
			if p:IsA("MeshPart") and p.Name == "Head" then
				p.TextureID = "" -- twarz rysujemy klockami
			end
		end
	end
	model:PivotTo(U.miejsce(strona))
	local wyposazenie = Instance.new("Model")
	wyposazenie.Name = "Wyposazenie"
	wyposazenie.Parent = model
	return model
end

-- część wyposażenia: pozycja w układzie lokalnym części ciała (przód postaci to −Z, jej prawa strona to +X)
local function dodaj(model: Model, czescCiala: string, nazwa: string, rozmiar: Vector3, offset: CFrame, kolor: string, material: Enum.Material?)
	local baza = model:FindFirstChild(czescCiala) :: BasePart
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Size = rozmiar
	p.CFrame = baza.CFrame * offset
	p.Color = Color3.fromHex(kolor)
	p.Material = material or M.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Anchored = false
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Massless = true
	local spaw = Instance.new("WeldConstraint")
	spaw.Name = "Spaw"
	spaw.Part0 = baza
	spaw.Part1 = p
	spaw.Parent = p
	p.Parent = model:FindFirstChild("Wyposazenie")
	licznik += 2
	return p
end
local function V(x, y, z)
	return Vector3.new(x, y, z)
end
local function C(x, y, z)
	return CFrame.new(x, y, z)
end

local function wykoncz(model: Model)
	local obrys = Instance.new("Highlight")
	obrys.Name = "ObrysKomiksowy"
	obrys.FillTransparency = 1
	obrys.FillColor = Color3.new(1, 1, 1)
	obrys.OutlineColor = Color3.fromHex("#17121F")
	obrys.OutlineTransparency = 0
	obrys.DepthMode = Enum.HighlightDepthMode.Occluded
	obrys.Adornee = model
	obrys.Parent = model
	-- mapa jest strumieniowana: szablon ma być u klienta zawsze w całości (klonujemy go lokalnie)
	model.ModelStreamingMode = Enum.ModelStreamingMode.Persistent
	model.Parent = aktorzy
	licznik += #model:GetDescendants() + 1
end

------------------------------------------------------------------ RYCERZ
local STAL, STAL_J, STAL_C = "#9AA5B5", "#C9D2DE", "#5B6470"
local NIEBIESKI, ZLOTO, CZERWONY = "#2F6FE0", "#FFC83D", "#E0413A"
local rycerz = nowyRig("Rycerz", "gracz", {
	Head = "#20242B", UpperTorso = STAL, LowerTorso = STAL_C,
	LeftUpperArm = STAL, RightUpperArm = STAL, LeftLowerArm = "#7C8798", RightLowerArm = "#7C8798",
	LeftHand = "#3F4654", RightHand = "#3F4654",
	LeftUpperLeg = STAL_C, RightUpperLeg = STAL_C, LeftLowerLeg = STAL, RightLowerLeg = STAL,
	LeftFoot = "#3A3F4A", RightFoot = "#3A3F4A",
})
-- hełm z wizjerem
dodaj(rycerz, "Head", "HelmGora", V(1.5, 0.36, 1.5), C(0, 0.66, 0), STAL_J)
dodaj(rycerz, "Head", "HelmTyl", V(1.5, 1.2, 0.3), C(0, 0, 0.62), STAL)
dodaj(rycerz, "Head", "HelmLewy", V(0.3, 1.2, 1.26), C(-0.62, 0, -0.1), STAL)
dodaj(rycerz, "Head", "HelmPrawy", V(0.3, 1.2, 1.26), C(0.62, 0, -0.1), STAL)
dodaj(rycerz, "Head", "HelmCzolo", V(1.5, 0.44, 0.3), C(0, 0.42, -0.62), STAL_J)
dodaj(rycerz, "Head", "HelmPodbrodek", V(1.5, 0.52, 0.3), C(0, -0.36, -0.62), STAL)
dodaj(rycerz, "Head", "HelmNosal", V(0.22, 0.4, 0.36), C(0, 0.06, -0.64), STAL_J)
dodaj(rycerz, "Head", "HelmRant", V(1.64, 0.2, 1.64), C(0, -0.62, 0), STAL_C)
dodaj(rycerz, "Head", "OkoLewe", V(0.3, 0.17, 0.08), C(-0.33, 0.06, -0.59), "#8FF6FF", M.Neon)
dodaj(rycerz, "Head", "OkoPrawe", V(0.3, 0.17, 0.08), C(0.33, 0.06, -0.59), "#8FF6FF", M.Neon)
dodaj(rycerz, "Head", "Pioropusz", V(0.36, 0.52, 1.5), C(0, 1.1, 0.05), CZERWONY)
dodaj(rycerz, "Head", "PioropuszTyl", V(0.36, 1.0, 0.42), C(0, 0.72, 0.98), CZERWONY)
-- tułów: tabard, kołnierz, peleryna
dodaj(rycerz, "UpperTorso", "TabardPrzod", V(1.5, 1.72, 0.12), C(0, -0.02, -0.56), NIEBIESKI)
dodaj(rycerz, "UpperTorso", "TabardTyl", V(1.5, 1.72, 0.12), C(0, -0.02, 0.56), NIEBIESKI)
dodaj(rycerz, "UpperTorso", "Herb", V(0.72, 0.72, 0.08), C(0, 0.12, -0.64) * CFrame.Angles(0, 0, rad(45)), ZLOTO)
dodaj(rycerz, "UpperTorso", "Kolnierz", V(2.12, 0.3, 1.16), C(0, 0.8, 0), STAL_C)
dodaj(rycerz, "UpperTorso", "Peleryna", V(1.8, 3.0, 0.14), C(0, -0.8, 0.8) * CFrame.Angles(rad(-9), 0, 0), CZERWONY, M.Fabric)
dodaj(rycerz, "LowerTorso", "Pas", V(2.1, 0.36, 1.14), C(0, 0.06, 0), "#6B3F1D")
dodaj(rycerz, "LowerTorso", "Klamra", V(0.46, 0.36, 0.1), C(0, 0.06, -0.6), ZLOTO)
dodaj(rycerz, "LowerTorso", "TabardDol", V(1.1, 1.3, 0.12), C(0, -0.82, -0.57), NIEBIESKI)
dodaj(rycerz, "LowerTorso", "TabardDolTyl", V(1.1, 1.3, 0.12), C(0, -0.82, 0.57), NIEBIESKI)
-- naramienniki i nakolanniki
for _, strona in { "Left", "Right" } do
	local z = if strona == "Left" then -1 else 1
	dodaj(rycerz, strona .. "UpperArm", "Naramiennik", V(1.34, 0.62, 1.34), C(0.06 * z, 0.44, 0), STAL_J)
	dodaj(rycerz, strona .. "UpperArm", "NaramiennikRant", V(1.4, 0.16, 1.4), C(0.06 * z, 0.08, 0), STAL_C)
	dodaj(rycerz, strona .. "LowerLeg", "Nakolannik", V(1.1, 0.42, 1.1), C(0, 0.52, 0), STAL_J)
end
-- wielki miecz w prawej dłoni: klinga wzdłuż −Z dłoni (po uniesieniu ręki animacją toolnone sterczy w górę)
local yd = -0.16 -- wysokość chwytu w dłoni (RightGripAttachment)
dodaj(rycerz, "RightHand", "MieczRekojesc", V(0.3, 0.3, 1.5), C(0, yd, -0.1), "#6B3F1D")
dodaj(rycerz, "RightHand", "MieczGlowica", V(0.48, 0.48, 0.38), C(0, yd, 0.82), ZLOTO)
dodaj(rycerz, "RightHand", "MieczJelec", V(0.38, 1.8, 0.36), C(0, yd, -1.0), ZLOTO)
dodaj(rycerz, "RightHand", "MieczKlinga", V(0.2, 0.9, 4.6), C(0, yd, -3.48), "#E6EEF8", M.Metal)
dodaj(rycerz, "RightHand", "MieczZbrocze", V(0.26, 0.26, 3.9), C(0, yd, -3.2), "#AEB7C4", M.Metal)
dodaj(rycerz, "RightHand", "MieczSztych", V(0.2, 0.52, 0.5), C(0, yd, -6.02), "#E6EEF8", M.Metal)
-- tarcza na lewym przedramieniu (zewnętrzna strona lewej ręki to −X)
dodaj(rycerz, "LeftLowerArm", "TarczaObrys", V(0.16, 2.3, 2.8), C(-0.62, -0.15, -0.05), "#2B2238")
dodaj(rycerz, "LeftLowerArm", "Tarcza", V(0.22, 2.0, 2.5), C(-0.72, -0.15, -0.05), NIEBIESKI)
dodaj(rycerz, "LeftLowerArm", "TarczaPasPion", V(0.26, 2.0, 0.5), C(-0.76, -0.15, -0.05), ZLOTO)
dodaj(rycerz, "LeftLowerArm", "TarczaPasPoziom", V(0.26, 0.5, 2.5), C(-0.76, -0.15, -0.05), ZLOTO)
dodaj(rycerz, "LeftLowerArm", "TarczaGuz", V(0.36, 0.72, 0.72), C(-0.8, -0.15, -0.05) * CFrame.Angles(rad(45), 0, 0), STAL_J, M.Metal)
wykoncz(rycerz)

------------------------------------------------------------------ ZBIR
local KAPTUR, KAPTUR_J, SKORA, SKORA_C = "#1F5A36", "#2A7A48", "#D29A6A", "#3B2616"
local zbir = nowyRig("Zbir", "wrog", {
	Head = SKORA, UpperTorso = "#6B4A2B", LowerTorso = "#4A3526",
	LeftUpperArm = KAPTUR_J, RightUpperArm = KAPTUR_J, LeftLowerArm = SKORA, RightLowerArm = SKORA,
	LeftHand = SKORA, RightHand = SKORA,
	LeftUpperLeg = "#4A3526", RightUpperLeg = "#4A3526", LeftLowerLeg = "#4A3526", RightLowerLeg = "#4A3526",
	LeftFoot = "#221A14", RightFoot = "#221A14",
})
-- ciemnozielony kaptur z części
dodaj(zbir, "Head", "KapturGora", V(1.5, 0.4, 1.5), C(0, 0.68, 0.04), KAPTUR)
dodaj(zbir, "Head", "KapturTyl", V(1.5, 1.45, 0.34), C(0, -0.05, 0.64), KAPTUR)
dodaj(zbir, "Head", "KapturLewy", V(0.34, 1.3, 1.3), C(-0.64, 0, 0.02), KAPTUR)
dodaj(zbir, "Head", "KapturPrawy", V(0.34, 1.3, 1.3), C(0.64, 0, 0.02), KAPTUR)
dodaj(zbir, "Head", "KapturDaszek", V(1.56, 0.24, 0.5), C(0, 0.56, -0.62), KAPTUR_J)
dodaj(zbir, "Head", "KapturCzubek", V(0.84, 0.52, 0.84), C(0, 1.06, 0.3), KAPTUR)
dodaj(zbir, "Head", "KapturKoniec", V(0.46, 0.46, 0.46), C(0, 1.36, 0.66), KAPTUR_J)
-- twarz: gniewne oczy i chusta
dodaj(zbir, "Head", "OkoLewe", V(0.32, 0.2, 0.08), C(-0.28, 0.14, -0.58), "#FFFFFF")
dodaj(zbir, "Head", "OkoPrawe", V(0.32, 0.2, 0.08), C(0.28, 0.14, -0.58), "#FFFFFF")
dodaj(zbir, "Head", "ZrenicaLewa", V(0.13, 0.15, 0.1), C(-0.23, 0.12, -0.6), "#17121F")
dodaj(zbir, "Head", "ZrenicaPrawa", V(0.13, 0.15, 0.1), C(0.23, 0.12, -0.6), "#17121F")
dodaj(zbir, "Head", "BrewLewa", V(0.46, 0.11, 0.12), C(-0.28, 0.32, -0.61) * CFrame.Angles(0, 0, rad(-20)), "#17121F")
dodaj(zbir, "Head", "BrewPrawa", V(0.46, 0.11, 0.12), C(0.28, 0.32, -0.61) * CFrame.Angles(0, 0, rad(20)), "#17121F")
dodaj(zbir, "Head", "Chusta", V(1.22, 0.5, 0.14), C(0, -0.3, -0.57), "#8E2F2F", M.Fabric)
-- tułów: pelerynka kaptura, pas na ukos, pas biodrowy
dodaj(zbir, "UpperTorso", "Pelerynka", V(2.5, 0.5, 1.5), C(0, 0.72, 0.02), KAPTUR_J, M.Fabric)
dodaj(zbir, "UpperTorso", "PelerynkaTyl", V(1.9, 1.6, 0.14), C(0, -0.1, 0.6), KAPTUR, M.Fabric)
dodaj(zbir, "UpperTorso", "PasNaUkos", V(0.32, 2.3, 0.1), C(0, 0, -0.56) * CFrame.Angles(0, 0, rad(38)), SKORA_C)
dodaj(zbir, "LowerTorso", "Pas", V(2.1, 0.36, 1.14), C(0, 0.06, 0), "#2E1F14")
dodaj(zbir, "LowerTorso", "Klamra", V(0.44, 0.36, 0.1), C(0, 0.06, -0.6), "#B4B9BF", M.Metal)
for _, strona in { "Left", "Right" } do
	dodaj(zbir, strona .. "LowerArm", "Karwasz", V(1.1, 0.56, 1.1), C(0, -0.1, 0), SKORA_C)
	dodaj(zbir, strona .. "LowerLeg", "Cholewka", V(1.1, 0.34, 1.1), C(0, -0.4, 0), "#221A14")
end
-- maczuga w prawej dłoni
dodaj(zbir, "RightHand", "MaczugaTrzonek", V(0.34, 0.34, 1.8), C(0, yd, -0.25), "#5A3A22", M.Wood)
dodaj(zbir, "RightHand", "MaczugaGlowica", V(0.92, 0.92, 2.7), C(0, yd, -2.45), "#8A5A34", M.Wood)
dodaj(zbir, "RightHand", "MaczugaOkucie1", V(1.04, 1.04, 0.3), C(0, yd, -1.4), "#6C727A", M.Metal)
dodaj(zbir, "RightHand", "MaczugaOkucie2", V(1.04, 1.04, 0.3), C(0, yd, -3.4), "#6C727A", M.Metal)
dodaj(zbir, "RightHand", "MaczugaKoniec", V(0.7, 0.7, 0.3), C(0, yd, -3.95), "#5A3A22", M.Wood)
for i, k in { { 0.56, 0, -2.0 }, { -0.56, 0, -2.0 }, { 0, 0.56, -2.4 }, { 0, -0.56, -2.4 }, { 0.56, 0, -2.9 }, { -0.56, 0, -2.9 } } do
	dodaj(zbir, "RightHand", "MaczugaKolec" .. i, V(0.36, 0.36, 0.36), C(k[1], yd + k[2], k[3]) * CFrame.Angles(rad(45), rad(45), 0), "#C9D2DE", M.Metal)
end
wykoncz(zbir)

aktorzy.Parent = kontener
return "OK aktorzy: " .. licznik .. " instancji (Rycerz " .. #rycerz:GetDescendants() .. ", Zbir " .. #zbir:GetDescendants() .. ")"
