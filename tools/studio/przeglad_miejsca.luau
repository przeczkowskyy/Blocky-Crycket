-- Przegląd otwartego miejsca: usługi, liczniki części, oświetlenie, kto jest w Team Create.
-- Uruchom: python tools/studio_mcp.py luau tools/studio/przeglad_miejsca.luau
local HttpService = game:GetService("HttpService")
local out = { placeId = game.PlaceId, gameId = game.GameId, name = game.Name }
out.services = {}
for _, name in { "Workspace", "Lighting", "ReplicatedFirst", "ReplicatedStorage", "ServerScriptService", "ServerStorage",
	"StarterGui", "StarterPack", "StarterPlayer", "Teams", "SoundService", "MaterialService" } do
	local ok, s = pcall(function()
		return game:GetService(name)
	end)
	if ok and s then
		local kids = {}
		for _, c in s:GetChildren() do
			table.insert(kids, { n = c.Name, c = c.ClassName, d = #c:GetDescendants() })
		end
		out.services[name] = kids
	end
end
local parts, meshes, unions = 0, 0, 0
for _, d in workspace:GetDescendants() do
	if d:IsA("MeshPart") then
		meshes += 1
	elseif d:IsA("UnionOperation") then
		unions += 1
	elseif d:IsA("BasePart") then
		parts += 1
	end
end
out.workspace = { parts = parts, meshParts = meshes, unions = unions, streaming = workspace.StreamingEnabled }
local users = {}
for _, p in game:GetService("Players"):GetPlayers() do
	table.insert(users, { name = p.Name, id = p.UserId })
end
out.collaborators = users
local L = game:GetService("Lighting")
out.lighting = { ClockTime = L.ClockTime, Brightness = L.Brightness } -- Technology nie jest czytelne z tego kontekstu
return HttpService:JSONEncode(out)
