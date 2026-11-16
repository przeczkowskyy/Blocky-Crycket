--[[
	MglaPasa — lekka mgła w lesie-pasie (Script, RunContext = Client, w kontenerze Workspace/LasPasGra). Wariant
	MglaLasu ze starego lasu (swiat/biom_las/zrodla/MglaLasu.client.luau, zgoda Karola z 15.11.2026) dla PROSTOKĄTA
	pasa z DanePasa.mgla zamiast kwadratu starego lasu.

	Działa tylko u gracza i tylko wtedy, gdy jego kamera jest w pasie albo przy nim: zmienia u siebie właściwości
	obiektu Atmosphere (zmiany klienta nie idą do serwera ani do innych graczy) i przy wyjściu płynnie wraca do
	wartości zastanych przy starcie. Wspólne ustawienia miejsca zostają nietknięte; skrypt nie tworzy obiektów i nie
	zmienia niczego poza Atmosphere. Brak Atmosphere → nic nie robi.

	Waga mgły = LogikaPasa.wagaMgly(kamera, prostokąt, pas przejścia) — 1 w pasie, 0 dalej niż `pas` od brzegu; idzie
	do celu z tempem `tempo` na sekundę (łagodne wejście i wyjście, np. po teleporcie). W czasie przelotu kamery
	(lokalny atrybut kontenera KlientPrzelot, ustawia KlientPasa) cel jest mnożony przez `wPrzelocie` (rzadsza mgła,
	żeby było widać przegrody). Gdy ktoś inny nadpisze Atmosphere w czasie, gdy nasza waga > 0 (np. MglaLasu starego
	lasu kończy wygaszanie po teleporcie), wartości są ustawiane ponownie.

	Wyłączenie bez usuwania: atrybut kontenera MglaWylaczona = true. Do testów: lokalny atrybut WagaMglyPasa (0–1).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local RunService = game:GetService("RunService")
local Swiatlo = game:GetService("Lighting")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DanePasa"))
local L = require(moduly:WaitForChild("LogikaPasa"))
local M = D.mgla

local atmosfera = Swiatlo:FindFirstChildOfClass("Atmosphere")
if not atmosfera then
	return
end

local CEL = {
	Density = M.cel.Density,
	Offset = M.cel.Offset,
	Haze = M.cel.Haze,
	Glare = M.cel.Glare,
	Color = Color3.fromHex(M.cel.Color),
	Decay = Color3.fromHex(M.cel.Decay),
}
local BAZA = {
	Density = atmosfera.Density,
	Offset = atmosfera.Offset,
	Haze = atmosfera.Haze,
	Glare = atmosfera.Glare,
	Color = atmosfera.Color,
	Decay = atmosfera.Decay,
}

local waga = 0
local ustawiona = -1
local ostatniaGestosc = -1

local function zastosuj(w: number, wymus: boolean)
	if not wymus and math.abs(w - ustawiona) < 0.002 then
		return
	end
	ustawiona = w
	atmosfera.Density = BAZA.Density + (CEL.Density - BAZA.Density) * w
	atmosfera.Offset = BAZA.Offset + (CEL.Offset - BAZA.Offset) * w
	atmosfera.Haze = BAZA.Haze + (CEL.Haze - BAZA.Haze) * w
	atmosfera.Glare = BAZA.Glare + (CEL.Glare - BAZA.Glare) * w
	atmosfera.Color = BAZA.Color:Lerp(CEL.Color, w)
	atmosfera.Decay = BAZA.Decay:Lerp(CEL.Decay, w)
	ostatniaGestosc = atmosfera.Density
end

local function wagaDocelowa(): number
	if kontener:GetAttribute("MglaWylaczona") == true then
		return 0
	end
	local kamera = workspace.CurrentCamera
	if not kamera then
		return 0
	end
	local p = kamera.CFrame.Position
	local w = L.wagaMgly(p.X, p.Z, M, M.pas)
	if kontener:GetAttribute("KlientPrzelot") == true then
		w *= M.wPrzelocie
	end
	return w
end

local polaczenie = RunService.RenderStepped:Connect(function(dt: number)
	waga = L.krokWagi(waga, wagaDocelowa(), M.tempo, dt)
	-- ktoś nadpisał Atmosphere, gdy nasza mgła jest włączona → ustawiamy ponownie
	local obca = waga > 0 and ustawiona >= 0 and math.abs(atmosfera.Density - ostatniaGestosc) > 1e-4
	zastosuj(waga, obca)
	kontener:SetAttribute("WagaMglyPasa", math.floor(waga * 100 + 0.5) / 100)
end)

script.Destroying:Connect(function()
	polaczenie:Disconnect()
	ustawiona = -1
	zastosuj(0, true)
end)
