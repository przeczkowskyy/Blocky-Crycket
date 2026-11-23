--[[
	SerwerNpc — serwerowa połowa postaci niezależnych (D-109; swiat/npc_gra). Script, RunContext = Server,
	w kontenerze Workspace/NpcGra. Poza Studio usuwa cały kontener (w opublikowanej grze tej próby nie ma).

	Serwer niczego nie buduje: postacie składa i animuje każdy klient u siebie (KlientNpc). Tutaj jest tylko:
		• wyłącznik dla wszystkich: atrybut kontenera z D.wylacznik (true, gdy go nie ma; false = bez NPC, figury
		  z klocków widoczne jak dawniej),
		• haczyk prób Sygnaly/SterowanieSerwera: Invoke("stan") → { gotowy, wlaczone, skrot, npc, stanowisk, rigow };
		  Invoke("wlacz", true | false) → przestawia wyłącznik (replikuje się do klientów).
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneNpc"))
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")

if kontener:GetAttribute(D.wylacznik) == nil then
	kontener:SetAttribute(D.wylacznik, true)
end

sterowanie.OnInvoke = function(polecenie, a)
	if polecenie == "stan" then
		local rigow = 0
		for _, m in moduly:WaitForChild("Rigi"):GetChildren() do
			if m:IsA("ModuleScript") then
				rigow += 1
			end
		end
		return {
			gotowy = true,
			wlaczone = kontener:GetAttribute(D.wylacznik) ~= false,
			skrot = D.skrot,
			npc = #D.kolejnosc,
			stanowisk = #D.stanowiska,
			rigow = rigow,
		}
	elseif polecenie == "wlacz" then
		kontener:SetAttribute(D.wylacznik, a == true)
		return true
	end
	return nil
end

kontener:SetAttribute("SkrotSerwera", D.skrot)
kontener:SetAttribute("SerwerGotowy", true)
