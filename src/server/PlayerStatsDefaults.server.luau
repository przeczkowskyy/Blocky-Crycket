-- PLACEHOLDER: docelowo wartości z DataStore (osobne zadanie). HUD (src/client/HUDClient.client.luau) czyta atrybuty gracza.
local Players = game:GetService("Players")

local DEFAULTS = { Level = 1, XP = 0, XPMax = 100, Gold = 0, Gems = 0 }

local function init(player)
	for key, value in pairs(DEFAULTS) do
		if player:GetAttribute(key) == nil then
			player:SetAttribute(key, value)
		end
	end
end

Players.PlayerAdded:Connect(init)
for _, player in ipairs(Players:GetPlayers()) do
	init(player)
end
