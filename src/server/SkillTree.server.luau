-- Drzewko umiejętności: zakup węzłów za Diamenty (atrybut gracza "Gems"), wyłącznie na serwerze.
-- Dane: ReplicatedStorage.Shared.SkillTreeData. Projekt: B&C/UI/Okno drzewka umiejętności.md (propozycja).
--
-- Stan gracza: atrybut "SkillTree" (JSON {idWęzła = poziom}). Premie: atrybuty "ST_<stat>" (suma w %),
-- które czytają inne systemy (walka, karczma, Twierdza, pety) — dziś jeszcze nikt ich nie czyta.
-- PLACEHOLDER: bez zapisu w DataStore (jak reszta statystyk gracza), stan znika po wyjściu z gry.

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Data = require(RS:WaitForChild("Shared"):WaitForChild("SkillTreeData"))

local buy = RS:FindFirstChild("SkillTreeBuy")
if not buy then
	buy = Instance.new("RemoteEvent")
	buy.Name = "SkillTreeBuy"
	buy.Parent = RS
end

local COOLDOWN = 0.12
local last: { [Player]: number } = {}

local function levelsOf(player: Player): { [string]: number }
	local ok, t = pcall(HttpService.JSONDecode, HttpService, player:GetAttribute("SkillTree") or "{}")
	return (ok and type(t) == "table") and t or {}
end

local function applyBonuses(player: Player, levels: { [string]: number })
	local sums: { [string]: number } = {}
	for id, lvl in pairs(levels) do
		local node = Data.Nodes[id]
		if node and node.stat then
			sums[node.stat] = (sums[node.stat] or 0) + node.per * lvl
		end
	end
	for stat, v in pairs(sums) do
		player:SetAttribute("ST_" .. stat, v)
	end
end

buy.OnServerEvent:Connect(function(player: Player, id: unknown)
	if typeof(id) ~= "string" or #id > 64 then
		return
	end
	local now = os.clock()
	if last[player] and now - last[player] < COOLDOWN then
		return
	end
	last[player] = now

	local node = Data.Nodes[id]
	if not node then
		return
	end
	local levels = levelsOf(player)
	local lvl = levels[id] or 0
	if lvl >= node.max or not Data.isAvailable(node, levels) then
		return
	end
	local cost = Data.cost(node, lvl + 1)
	local gems = player:GetAttribute("Gems")
	if typeof(gems) ~= "number" or gems < cost then
		return
	end
	player:SetAttribute("Gems", gems - cost)
	levels[id] = lvl + 1
	player:SetAttribute("SkillTree", HttpService:JSONEncode(levels))
	applyBonuses(player, levels)
end)

local function init(player: Player)
	if player:GetAttribute("SkillTree") == nil then
		player:SetAttribute("SkillTree", "{}")
	end
	applyBonuses(player, levelsOf(player))
end

Players.PlayerAdded:Connect(init)
for _, p in ipairs(Players:GetPlayers()) do
	init(p)
end
Players.PlayerRemoving:Connect(function(p)
	last[p] = nil
end)
