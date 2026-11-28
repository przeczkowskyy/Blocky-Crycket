--[[
	KotRasySwiat (serwer) — PODGLĄD u Pawła (26.11), propozycja; klient: src/client/KotRasySwiatClient.client.luau.

	Paweł 26.11: po świecie ma chodzić kot wybranej rasy, widoczny dla wszystkich graczy; bohater klasy jest tylko
	podglądem klasy, nie postacią w świecie. Dlatego, dopóki ten podgląd jest włączony (atrybut Wlaczone folderu
	ReplicatedStorage.KotyRasSwiat), serwer W CZASIE GRY ustawia wyłącznik pakietu Karola „Bohater w świecie”
	(Workspace/BohaterSwiat, atrybut BohaterWSwiecie = false — jego własny, opisany w README wyłącznik). W Edit nic się
	nie zmienia, pliki Karola bez zmian; po wyłączeniu podglądu wraca wartość sprzed zmiany. Do zgody Karola: pytanie 63.

	Broń: klient prosi o wyjęcie / schowanie (RemoteEvent KotRasySwiatBron), serwer zapisuje atrybut gracza BronWyjeta —
	atrybut widzą wszyscy, więc każdy klient pokazuje albo chowa broń na kocie tego gracza.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local folder = RS:WaitForChild("KotyRasSwiat", 30)
if not folder then
	return
end

local ev = RS:FindFirstChild("KotRasySwiatBron")
if not ev then
	ev = Instance.new("RemoteEvent")
	ev.Name = "KotRasySwiatBron"
	ev.Parent = RS
end

local ostatnio: { [Player]: number } = {}
ev.OnServerEvent:Connect(function(gracz: Player, wyjeta: unknown)
	if typeof(wyjeta) ~= "boolean" or not gracz:GetAttribute("Class") then
		return
	end
	local t = os.clock()
	if ostatnio[gracz] and t - ostatnio[gracz] < 0.25 then
		return
	end
	ostatnio[gracz] = t
	gracz:SetAttribute("BronWyjeta", wyjeta)
end)
Players.PlayerRemoving:Connect(function(g)
	ostatnio[g] = nil
end)

-- wyłącznik bohatera klasy z pakietu Karola: tylko w czasie gry i tylko gdy ten podgląd jest włączony
local poprzednio: any = nil
local function ustaw()
	local b = workspace:FindFirstChild("BohaterSwiat")
	if not b then
		return
	end
	if folder:GetAttribute("Wlaczone") ~= false then
		if poprzednio == nil then
			poprzednio = b:GetAttribute("BohaterWSwiecie")
			if poprzednio == nil then
				poprzednio = true
			end
		end
		b:SetAttribute("BohaterWSwiecie", false)
	elseif poprzednio ~= nil then
		b:SetAttribute("BohaterWSwiecie", poprzednio)
		poprzednio = nil
	end
end
folder:GetAttributeChangedSignal("Wlaczone"):Connect(ustaw)
task.defer(ustaw)
task.delay(3, ustaw) -- pakiet Karola mógł wystartować później
