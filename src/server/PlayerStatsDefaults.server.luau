-- PLACEHOLDER: docelowo wartości z DataStore (osobne zadanie). HUD (src/client/HUDClient.client.luau) czyta atrybuty gracza.
local Players = game:GetService("Players")

local DEFAULTS = {
	Level = 1, XP = 0, XPMax = 100, Gold = 0,
	Gems = 1000, -- TEST (Paweł 15.11): Diamenty na sprawdzenie drzewka umiejętności; przed premierą wrócić do 0
	Fish = 0, -- trzecia waluta HUD (Rybki; propozycja Game Directora 2026-11-14, rola do ustalenia)
	-- statystyki okna ekwipunku (wartości testowe z projektu graficznego; system RPG: B&C/Gra/System RPG.md)
	Strength = 20, Constitution = 16, Intelligence = 18, Dexterity = 12, Luck = 7, Armor = 57,
}

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
