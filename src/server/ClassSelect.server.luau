-- Wybór klasy po ekranie ładowania: klient wysyła id klasy, serwer sprawdza i ustawia atrybut gracza "Class".
-- Potem rasa: RemoteEvent ChooseRace → atrybut "Race" (D-079). HUD pokazuje się dopiero po wyborze rasy.
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

-- wybór rasy (D-079): po klasie; rasa premium (Półbóg, D-080) zablokowana, dopóki nie ma zakupów
local RaceData = require(RS:WaitForChild("Shared"):WaitForChild("RaceData"))
local raceEv = RS:FindFirstChild("ChooseRace")
if not raceEv then
	raceEv = Instance.new("RemoteEvent")
	raceEv.Name = "ChooseRace"
	raceEv.Parent = RS
end
local lastRace: { [Player]: number } = {}
raceEv.OnServerEvent:Connect(function(player: Player, id: unknown)
	if typeof(id) ~= "string" or not player:GetAttribute("Class") then
		return
	end
	local race = RaceData.byId(id)
	if not race or race.premium then
		return
	end
	local now = os.clock()
	if lastRace[player] and now - lastRace[player] < 0.5 then
		return
	end
	lastRace[player] = now
	player:SetAttribute("Race", id)
end)

Players.PlayerRemoving:Connect(function(p)
	lastRace[p] = nil
	last[p] = nil
end)
