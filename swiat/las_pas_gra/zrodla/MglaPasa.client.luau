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

	Kilka mgieł pasa naraz (17.11.2026: las-pas i Bagno stykają się w bramie): każda mgła wystawia na swoim
	kontenerze lokalny atrybut CelMglyPasa (cel 0–1 z położenia kamery). Mgła, której cel jest niższy niż cel innej
	(remis: ustępuje kontener o nazwie dalej w alfabecie), USTĘPUJE — cel 0 i żadnego zapisu do Atmosphere. Mgła,
	która zaczyna narastać, startuje od wartości ZASTANYCH w Atmosphere (nie od zapamiętanej bazy), więc na granicy
	biomów jedna mgła płynnie przechodzi w drugą, bez przebłysku czystego nieba. Gasnąc, wraca do bazy jak dotąd.
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
local OD = BAZA -- skąd narasta mgła: baza albo wartości zastane przy przejęciu po innej mgle pasa

local function zastosuj(w: number, wymus: boolean)
	if not wymus and math.abs(w - ustawiona) < 0.002 then
		return
	end
	ustawiona = w
	atmosfera.Density = OD.Density + (CEL.Density - OD.Density) * w
	atmosfera.Offset = OD.Offset + (CEL.Offset - OD.Offset) * w
	atmosfera.Haze = OD.Haze + (CEL.Haze - OD.Haze) * w
	atmosfera.Glare = OD.Glare + (CEL.Glare - OD.Glare) * w
	atmosfera.Color = OD.Color:Lerp(CEL.Color, w)
	atmosfera.Decay = OD.Decay:Lerp(CEL.Decay, w)
	ostatniaGestosc = atmosfera.Density
end

-- inne mgły pasa (kontenery z lokalnym atrybutem CelMglyPasa), lista odświeżana co 0,5 s
local inne: { Instance } = {}
local odswiezonoInne = -math.huge
local function ustepujeInnej(cel: number): boolean
	local teraz = os.clock()
	if teraz - odswiezonoInne > 0.5 then
		odswiezonoInne = teraz
		table.clear(inne)
		for _, d in workspace:GetChildren() do
			if d ~= kontener and d:GetAttribute("CelMglyPasa") ~= nil then
				table.insert(inne, d)
			end
		end
	end
	for _, d in inne do
		local c = d:GetAttribute("CelMglyPasa")
		if type(c) == "number" and d.Parent and (c > cel or (c == cel and c > 0 and d.Name < kontener.Name)) then
			return true
		end
	end
	return false
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

local opublikowanyCel = -1
local polaczenie = RunService.RenderStepped:Connect(function(dt: number)
	local cel = wagaDocelowa()
	local celOkr = math.floor(cel * 100 + 0.5) / 100
	if celOkr ~= opublikowanyCel then
		opublikowanyCel = celOkr
		kontener:SetAttribute("CelMglyPasa", celOkr)
	end
	if ustepujeInnej(celOkr) then
		-- inna mgła pasa jest „bliżej”: oddajemy jej Atmosphere bez zapisu (ona przejmie od wartości zastanych)
		waga = 0
		ustawiona = 0
		OD = BAZA
		kontener:SetAttribute("WagaMglyPasa", 0)
		return
	end
	if waga <= 0 and cel > 0 then
		-- początek narastania: od wartości zastanych (inna mgła pasa albo baza)
		OD = { Density = atmosfera.Density, Offset = atmosfera.Offset, Haze = atmosfera.Haze, Glare = atmosfera.Glare,
			Color = atmosfera.Color, Decay = atmosfera.Decay }
	elseif OD ~= BAZA and (waga >= 1 or cel < waga) then
		OD = BAZA -- pełna mgła albo gaśnięcie: dalej względem bazy (wyjście z pasa wraca do wartości zastanych przy starcie)
	end
	waga = L.krokWagi(waga, cel, M.tempo, dt)
	-- ktoś nadpisał Atmosphere, gdy nasza mgła jest włączona → ustawiamy ponownie
	local obca = waga > 0 and ustawiona >= 0 and math.abs(atmosfera.Density - ostatniaGestosc) > 1e-4
	zastosuj(waga, obca)
	kontener:SetAttribute("WagaMglyPasa", math.floor(waga * 100 + 0.5) / 100)
end)

script.Destroying:Connect(function()
	polaczenie:Disconnect()
	ustawiona = -1
	OD = BAZA
	pcall(function()
		kontener:SetAttribute("CelMglyPasa", nil)
	end)
	zastosuj(0, true)
end)
