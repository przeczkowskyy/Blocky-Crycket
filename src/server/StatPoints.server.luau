--[[
	StatPoints — przycisk „+” w oknie ekwipunku (TEST).
	Klient: ReplicatedStorage.AddStatPoint:FireServer("Strength") → serwer podnosi atrybut gracza o 1.
	Okno (EquipmentPanelClient) odświeża się samo, bo słucha zmian atrybutów.

	TYMCZASOWO bez kosztu (punkty statystyk / złoto) i bez zapisu w DataStore — do ustalenia w B&C/Gra/System RPG.md.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local ALLOWED = { Strength = true, Constitution = true, Intelligence = true, Dexterity = true, Luck = true, Armor = true }
local MAX_VALUE = 9999
local COOLDOWN = 0.08 -- s, ochrona przed spamem z klienta

local remote = RS:FindFirstChild("AddStatPoint")
if not remote then
	remote = Instance.new("RemoteEvent")
	remote.Name = "AddStatPoint"
	remote.Parent = RS
end

local last = {}

remote.OnServerEvent:Connect(function(player, stat)
	if typeof(stat) ~= "string" or not ALLOWED[stat] then
		return
	end
	local now = os.clock()
	if last[player] and now - last[player] < COOLDOWN then
		return
	end
	last[player] = now
	local v = player:GetAttribute(stat)
	if typeof(v) ~= "number" then
		return
	end
	player:SetAttribute(stat, math.min(v + 1, MAX_VALUE))
end)

Players.PlayerRemoving:Connect(function(player)
	last[player] = nil
end)
