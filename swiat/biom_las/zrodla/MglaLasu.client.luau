--[[
	MglaLasu — lekka mgła w biomie Las (Script, RunContext = Client; zgoda Karola z 15.11.2026).

	Działa tylko u gracza i tylko wtedy, gdy jego kamera jest w lesie: skrypt zmienia u siebie właściwości obiektu
	Lighting.Atmosphere (zmiany klienta nie idą do serwera ani do innych graczy), a przy wyjściu z lasu płynnie
	przywraca wartości, które zastał przy starcie. Wspólne ustawienia miejsca zostają więc nietknięte — w Edit
	i w miasteczku wszystko wygląda jak dotąd.

	Wartości miejsca z 15.11.2026 (dla porządku; skrypt i tak czyta je przy starcie):
		Density 0.30, Offset 0.25, Haze 0, Glare 0, Color C7C7C7, Decay 6A707D.

	Wyłączenie bez usuwania: atrybut kontenera „Wylaczona” = true (mgła wraca do wartości miejsca).
	Usunięcie: python -B swiat/biom_las/mgla.py --usun (skrypt przy usuwaniu sam przywraca wartości).
	Gdy w Lighting nie ma obiektu Atmosphere, skrypt nic nie robi (nie tworzy wspólnych obiektów).
	Ograniczenie: jeśli kiedyś inny skrypt zacznie zmieniać Atmosphere (np. pora dnia), trzeba je uzgodnić — ten
	skrypt wraca do wartości zapamiętanych przy starcie.
]]
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")

local kontener = script.Parent

-- las: środek (0, 0, -2000), grywalny kwadrat 1000 × 1000 (swiat/biom_las/PROJEKT.md, rozdz. 2)
local SRODEK_X, SRODEK_Z = 0, -2000
local POL = 500 -- połowa boku: w środku mgła jest pełna
local PAS = 180 -- pas przejścia na zewnątrz kwadratu (mgła narasta przy dojściu do lasu)
local TEMPO = 0.8 -- ile „wagi” na sekundę (pełne przejście trwa ok. 1,25 s po zmianie strefy, np. po teleporcie)

local CEL = {
	Density = 0.36,
	Offset = 0.15,
	Haze = 1.4,
	Glare = 0,
	Color = Color3.fromHex("D6E4DA"),
	Decay = Color3.fromHex("8FAF9A"),
}

local atmosfera = Lighting:FindFirstChildOfClass("Atmosphere")
if not atmosfera then
	return
end

local BAZA = {
	Density = atmosfera.Density,
	Offset = atmosfera.Offset,
	Haze = atmosfera.Haze,
	Glare = atmosfera.Glare,
	Color = atmosfera.Color,
	Decay = atmosfera.Decay,
}

local waga = 0 -- 0 = wartości miejsca, 1 = pełna mgła lasu
local ustawiona = -1

local function zastosuj(w: number)
	if math.abs(w - ustawiona) < 0.002 then
		return
	end
	ustawiona = w
	atmosfera.Density = BAZA.Density + (CEL.Density - BAZA.Density) * w
	atmosfera.Offset = BAZA.Offset + (CEL.Offset - BAZA.Offset) * w
	atmosfera.Haze = BAZA.Haze + (CEL.Haze - BAZA.Haze) * w
	atmosfera.Glare = BAZA.Glare + (CEL.Glare - BAZA.Glare) * w
	atmosfera.Color = BAZA.Color:Lerp(CEL.Color, w)
	atmosfera.Decay = BAZA.Decay:Lerp(CEL.Decay, w)
end

local function wagaDocelowa(): number
	if kontener:GetAttribute("Wylaczona") == true then
		return 0
	end
	local kamera = workspace.CurrentCamera
	if not kamera then
		return 0
	end
	local p = kamera.CFrame.Position
	-- odległość kamery od kwadratu lasu w poziomie (0 w środku)
	local dx = math.max(math.abs(p.X - SRODEK_X) - POL, 0)
	local dz = math.max(math.abs(p.Z - SRODEK_Z) - POL, 0)
	local poza = math.sqrt(dx * dx + dz * dz)
	return math.clamp(1 - poza / PAS, 0, 1)
end

local polaczenie = RunService.RenderStepped:Connect(function(dt: number)
	local cel = wagaDocelowa()
	local krok = TEMPO * dt
	if cel > waga then
		waga = math.min(cel, waga + krok)
	else
		waga = math.max(cel, waga - krok)
	end
	zastosuj(waga)
	kontener:SetAttribute("WagaMgly", math.floor(waga * 100 + 0.5) / 100) -- tylko u klienta, do podglądu i testów
end)

script.Destroying:Connect(function()
	polaczenie:Disconnect()
	ustawiona = -1
	zastosuj(0)
end)
