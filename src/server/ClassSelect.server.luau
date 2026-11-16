-- Wybór klasy po ekranie ładowania: klient wysyła id klasy, serwer sprawdza i ustawia atrybut gracza "Class".
-- HUD (src/client/HUDClient.client.luau) pokazuje się dopiero, gdy "Class" jest ustawione.
-- PLACEHOLDER: bez DataStore — wybór trzeba powtórzyć po każdym wejściu (jak reszta statystyk).
-- Projekt: B&C/UI/Selektor bohatera.md (propozycja). Klasy: D-054.

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local ClassData = require(RS:WaitForChild("Shared"):WaitForChild("ClassData"))

local ev = RS:FindFirstChild("ChooseClass")
if not ev then
	ev = Instance.new("RemoteEvent")
	ev.Name = "ChooseClass"
	ev.Parent = RS
end

local last: { [Player]: number } = {}

ev.OnServerEvent:Connect(function(player: Player, id: unknown)
	if typeof(id) ~= "string" or not ClassData.byId(id) then
		return
	end
	local now = os.clock()
	if last[player] and now - last[player] < 0.5 then
		return
	end
	last[player] = now
	player:SetAttribute("Class", id)
end)

Players.PlayerRemoving:Connect(function(p)
	last[p] = nil
end)
