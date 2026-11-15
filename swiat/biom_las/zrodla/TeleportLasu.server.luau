--[[
	TeleportLasu — przejście między miasteczkiem a biomem Las (Script, RunContext = Server; prośba Karola z 15.11.2026).

	Trzy miejsca z podpowiedzią E (ProximityPrompt, na telefonie przycisk), zbudowane przez swiat/biom_las/teleport.py:
		Portal przy miejscu startu gracza  → las (Brama Pniaków)        — skrót do testów, żeby nie iść 2400 studów
		Brama Miejska w Krzywym Miasteczku → las (Brama Pniaków)        — jak w planie lasu (uklad.json: „z_miasteczka”)
		Kamień Powrotu przy Bramie Pniaków → Brama Miejska w miasteczku — jak w planie („powrot”)

	Serwer sam przenosi postać (klient niczego nie przysyła poza naciśnięciem podpowiedzi): najpierw prosi o wczytanie
	okolicy celu (streaming), potem ustawia postać w punkcie z atrybutów kontenera. Nie częściej niż raz na 2 s na gracza.
	Punkty docelowe są atrybutami kontenera (PunktLas, PatrzLas, PunktMiasteczka, PatrzMiasteczko) — wylicza je budowa.

	Działa tylko w Roblox Studio: poza Studio (opublikowane miejsce) skrypt usuwa cały kontener, jak pozostałe prototypy.
	Haczyk testowy: BindableFunction „Steruj” w kontenerze, Invoke("las" | "miasteczko") przenosi pierwszego gracza.
]]
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local kontener = script.Parent
if not RunService:IsStudio() then
	kontener:Destroy()
	return
end

local ODSTEP = 2 -- sekundy między przeniesieniami jednego gracza
local ostatnio: { [Player]: number } = {}

local function cel(nazwa: string): (Vector3?, Vector3?)
	if nazwa == "las" then
		return kontener:GetAttribute("PunktLas"), kontener:GetAttribute("PatrzLas")
	elseif nazwa == "miasteczko" then
		return kontener:GetAttribute("PunktMiasteczka"), kontener:GetAttribute("PatrzMiasteczko")
	end
	return nil, nil
end

local function przenies(gracz: Player, nazwa: string): boolean
	local teraz = os.clock()
	local poprzednio = ostatnio[gracz]
	if poprzednio and teraz - poprzednio < ODSTEP then
		return false
	end
	local punkt, patrz = cel(nazwa)
	if typeof(punkt) ~= "Vector3" or typeof(patrz) ~= "Vector3" then
		return false
	end
	local postac = gracz.Character
	local humanoid = postac and postac:FindFirstChildOfClass("Humanoid")
	local korzen = postac and postac:FindFirstChild("HumanoidRootPart")
	if not postac or not humanoid or humanoid.Health <= 0 or not korzen or not korzen:IsA("BasePart") then
		return false
	end
	ostatnio[gracz] = teraz
	-- okolica celu musi być wczytana u gracza, zanim postać tam stanie (miejsce ma włączony streaming)
	pcall(function()
		gracz:RequestStreamAroundAsync(punkt, 5)
	end)
	if postac.Parent == nil or gracz.Character ~= postac then
		return false
	end
	local naWprost = Vector3.new(patrz.X, punkt.Y, patrz.Z)
	if (naWprost - punkt).Magnitude < 0.1 then
		naWprost = punkt + Vector3.new(0, 0, -1)
	end
	postac:PivotTo(CFrame.lookAt(punkt, naWprost))
	korzen.AssemblyLinearVelocity = Vector3.zero
	korzen.AssemblyAngularVelocity = Vector3.zero
	return true
end

for _, obiekt in kontener:GetDescendants() do
	if obiekt:IsA("ProximityPrompt") then
		local nazwa = obiekt:GetAttribute("Cel")
		if type(nazwa) == "string" then
			obiekt.Enabled = true
			obiekt.Triggered:Connect(function(gracz: Player)
				przenies(gracz, nazwa)
			end)
		end
	end
end

Players.PlayerRemoving:Connect(function(gracz: Player)
	ostatnio[gracz] = nil
end)

local steruj = kontener:FindFirstChild("Steruj")
if steruj and steruj:IsA("BindableFunction") then
	steruj.OnInvoke = function(nazwa: any): boolean
		local gracz = Players:GetPlayers()[1]
		if not gracz or type(nazwa) ~= "string" then
			return false
		end
		ostatnio[gracz] = nil
		return przenies(gracz, nazwa)
	end
end
