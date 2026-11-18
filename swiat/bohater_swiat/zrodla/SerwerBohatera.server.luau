--[[
	SerwerBohatera — serwerowa połowa „bohatera w świecie” (propozycja, swiat/bohater_swiat). Script, RunContext =
	Server, w kontenerze Workspace/BohaterSwiat. Poza Studio usuwa cały kontener (w opublikowanej grze próby nie ma).

	Serwer niczego nie buduje i nie zmienia postaci graczy: bohaterów składa każdy klient u siebie z atrybutów gracza,
	które już piszą inne pakiety (Class — wybór klasy, StrojProba_<klasa> — przymierzalnia i kowal). Tutaj jest tylko:
		• wyłącznik dla wszystkich: atrybut kontenera BohaterWSwiecie (true, gdy go nie ma; false = awatar jak dawniej),
		• haczyk testowy Sygnaly/SterowanieSerwera: Invoke("stan") → { gotowy, wlaczony, skrot, zaleznosci, gracze };
		  Invoke("wlacz", true | false) → przestawia wyłącznik (replikuje się do klientów).
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneBohatera"))
local L = require(moduly:WaitForChild("LogikaBohatera"))
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")

if kontener:GetAttribute(D.atrybut_wlacznika) == nil then
	kontener:SetAttribute(D.atrybut_wlacznika, true)
end

local function jest(nazwa)
	local k = workspace:FindFirstChild(nazwa)
	return k ~= nil and k:GetAttribute("Wygenerowane") == true and k:FindFirstChild("Moduly") ~= nil
end

sterowanie.OnInvoke = function(polecenie, a)
	if polecenie == "stan" then
		local gracze = {}
		for _, p in Players:GetPlayers() do
			local klasa = L.klasa(D, p:GetAttribute(D.atrybut_klasy))
			table.insert(gracze, {
				klasaGry = p:GetAttribute(D.atrybut_klasy),
				klasa = klasa,
				stroj = if klasa then p:GetAttribute(D.atrybut_stroju .. klasa) else nil,
				postac = p.Character ~= nil,
			})
		end
		return {
			gotowy = true,
			wlaczony = kontener:GetAttribute(D.atrybut_wlacznika) ~= false,
			skrot = D.skrot,
			zaleznosci = { walka = jest(D.kontener_walki), stroje = jest(D.kontener_strojow) },
			gracze = gracze,
		}
	elseif polecenie == "wlacz" then
		kontener:SetAttribute(D.atrybut_wlacznika, a == true)
		return true
	end
	return nil
end

kontener:SetAttribute("SkrotSerwera", D.skrot)
kontener:SetAttribute("SerwerGotowy", true)
