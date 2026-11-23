--!strict
--[[
	TreningAFK — trening statystyk na stanowiskach AFK z paskiem postępu (D-141, Paweł 23.11; gałąź
	pawel/diamenty-afk, wersja do obejrzenia — czeka na Karola).

	Stanowiska: kontener Workspace/TreningAFK (atrybut Wygenerowane), budowany przy starcie serwera z klocków
	(hantle, ławka, worek, skakanka, księgi, kości) na wolnym pasie placu w miasteczku (TreningAFKDane.start).
	Gracz naciska E przy stanowisku → staje na nim, pasek napełnia się sam (AFK), tapnięcie przyspiesza.
	Pełny pasek → +przyrost do statystyki.

	Statystyki: NIE piszemy ich sami. Przyrost idzie tym samym sygnałem co mini-gry Training Center:
	Workspace/TreningProba/Sygnaly/PrzyrostStatystyki (BindableEvent pakietu Karola), którego słucha stan gracza
	(swiat/stan_gracza: dopisuje do profilu „wytrenowane”, zapisuje między sesjami i podnosi atrybut). Bez tego
	kontenera (np. w innym miejscu) przyrost trafia wprost do atrybutu gracza — tylko do prób.

	Zdalne: ReplicatedStorage.TreningAFK (RemoteEvent)
		klient → serwer: "tap" | "stop"
		serwer → klient: "start", id, postep, dlugosc, przyrost | "postep", postep, dlugosc
		                 | "punkt", atrybut, ile, dlugosc | "koniec"
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local D = require(RS:WaitForChild("Shared"):WaitForChild("TreningAFKDane"))

local zdalne = RS:FindFirstChild("TreningAFK") :: RemoteEvent?
if not zdalne then
	local e = Instance.new("RemoteEvent")
	e.Name = "TreningAFK"
	e.Parent = RS
	zdalne = e
end
local Z = zdalne :: RemoteEvent

------------------------------------------------------------------ budowa stanowisk (klocki)
local function czesc(rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3, ksztalt: Enum.PartType?): Part
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Size = rozmiar
	p.CFrame = cf
	p.Color = kolor
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Material = Enum.Material.SmoothPlastic
	if ksztalt then
		p.Shape = ksztalt
	end
	p.Parent = rodzic
	return p
end

local CIEMNY = Color3.fromRGB(45, 42, 48)
local DREWNO = Color3.fromRGB(150, 98, 60)
local STAL = Color3.fromRGB(170, 175, 185)

-- rekwizyt stanowiska; wszystko względem środka maty `o` (gracz stoi w o, rekwizyt przed nim)
local REKWIZYTY: { [string]: (Model, CFrame, Color3) -> () } = {
	Sila = function(m, o, k) -- stojak z hantlami
		czesc(m, "Stojak", Vector3.new(5, 0.4, 1.6), o * CFrame.new(0, 2.2, -3), DREWNO)
		for _, x in ipairs({ -1.6, 0, 1.6 }) do
			czesc(m, "Hantla drążek", Vector3.new(1.2, 0.3, 0.3), o * CFrame.new(x, 2.6, -3), STAL)
			czesc(m, "Hantla krążek", Vector3.new(0.35, 0.8, 0.8), o * CFrame.new(x - 0.6, 2.6, -3), k)
			czesc(m, "Hantla krążek", Vector3.new(0.35, 0.8, 0.8), o * CFrame.new(x + 0.6, 2.6, -3), k)
		end
		czesc(m, "Noga", Vector3.new(0.4, 2, 0.4), o * CFrame.new(-2.2, 1.1, -3), DREWNO)
		czesc(m, "Noga", Vector3.new(0.4, 2, 0.4), o * CFrame.new(2.2, 1.1, -3), DREWNO)
	end,
	Kondycja = function(m, o, k) -- ławka ze sztangą
		czesc(m, "Ławka", Vector3.new(1.6, 0.5, 5), o * CFrame.new(0, 1.4, -2.6), k)
		czesc(m, "Ławka noga", Vector3.new(1.2, 1.2, 0.4), o * CFrame.new(0, 0.7, -0.6), CIEMNY)
		czesc(m, "Ławka noga", Vector3.new(1.2, 1.2, 0.4), o * CFrame.new(0, 0.7, -4.6), CIEMNY)
		czesc(m, "Stojak", Vector3.new(0.4, 3.6, 0.4), o * CFrame.new(-1.6, 1.9, -4.8), CIEMNY)
		czesc(m, "Stojak", Vector3.new(0.4, 3.6, 0.4), o * CFrame.new(1.6, 1.9, -4.8), CIEMNY)
		czesc(m, "Sztanga", Vector3.new(5.4, 0.3, 0.3), o * CFrame.new(0, 3.6, -4.8), STAL)
		czesc(m, "Krążek", Vector3.new(0.4, 1.6, 1.6), o * CFrame.new(-2.4, 3.6, -4.8), CIEMNY, Enum.PartType.Cylinder)
		czesc(m, "Krążek", Vector3.new(0.4, 1.6, 1.6), o * CFrame.new(2.4, 3.6, -4.8), CIEMNY, Enum.PartType.Cylinder)
	end,
	Pancerz = function(m, o, k) -- worek treningowy na szubienicy
		czesc(m, "Słup", Vector3.new(0.6, 8, 0.6), o * CFrame.new(-2.4, 4, -3.4), DREWNO)
		czesc(m, "Wysięgnik", Vector3.new(3, 0.5, 0.5), o * CFrame.new(-1, 7.8, -3.4), DREWNO)
		czesc(m, "Lina", Vector3.new(0.15, 1.2, 0.15), o * CFrame.new(0, 7, -3.4), CIEMNY)
		czesc(m, "Worek", Vector3.new(1.8, 3.4, 1.8), o * CFrame.new(0, 4.6, -3.4), k)
		czesc(m, "Worek pas", Vector3.new(1.9, 0.3, 1.9), o * CFrame.new(0, 5.6, -3.4), CIEMNY)
	end,
	Zrecznosc = function(m, o, k) -- słupki ze skakanką
		czesc(m, "Słupek", Vector3.new(0.5, 3, 0.5), o * CFrame.new(-2.6, 1.5, -2.6), DREWNO)
		czesc(m, "Słupek", Vector3.new(0.5, 3, 0.5), o * CFrame.new(2.6, 1.5, -2.6), DREWNO)
		czesc(m, "Skakanka", Vector3.new(5.2, 0.2, 0.2), o * CFrame.new(0, 2.6, -2.6), k)
		czesc(m, "Uchwyt", Vector3.new(0.3, 0.8, 0.3), o * CFrame.new(-2.6, 3.3, -2.6), k)
		czesc(m, "Uchwyt", Vector3.new(0.3, 0.8, 0.3), o * CFrame.new(2.6, 3.3, -2.6), k)
	end,
	Inteligencja = function(m, o, k) -- pulpit z księgą i stos ksiąg
		czesc(m, "Pulpit", Vector3.new(0.8, 3, 0.8), o * CFrame.new(0, 1.5, -2.8), DREWNO)
		czesc(m, "Blat", Vector3.new(2.6, 0.3, 1.8), o * CFrame.new(0, 3.1, -2.8) * CFrame.Angles(math.rad(20), 0, 0), DREWNO)
		czesc(m, "Księga", Vector3.new(2.2, 0.3, 1.5), o * CFrame.new(0, 3.35, -2.8) * CFrame.Angles(math.rad(20), 0, 0), k)
		for i = 0, 2 do
			czesc(m, "Stos", Vector3.new(1.4, 0.45, 1), o * CFrame.new(2.4, 0.3 + i * 0.45, -2.4) * CFrame.Angles(0, math.rad(i * 15), 0),
				if i % 2 == 0 then k else STAL)
		end
	end,
	Szczescie = function(m, o, k) -- stolik z wielkimi kośćmi
		czesc(m, "Stolik", Vector3.new(3.4, 0.4, 2.4), o * CFrame.new(0, 2.4, -3), DREWNO)
		czesc(m, "Noga", Vector3.new(0.6, 2.2, 0.6), o * CFrame.new(0, 1.1, -3), DREWNO)
		czesc(m, "Kość", Vector3.new(1, 1, 1), o * CFrame.new(-0.7, 3.1, -3) * CFrame.Angles(0, math.rad(25), 0), Color3.new(1, 1, 1))
		czesc(m, "Kość", Vector3.new(1, 1, 1), o * CFrame.new(0.8, 3.1, -2.8) * CFrame.Angles(0, math.rad(-15), 0), k)
	end,
}

local kontener: Folder
local miejsca: { [string]: CFrame } = {}

local function zbuduj()
	local stary = workspace:FindFirstChild("TreningAFK")
	if stary then
		stary:Destroy()
	end
	local f = Instance.new("Folder")
	f.Name = "TreningAFK"
	f:SetAttribute("Wygenerowane", true)
	for i, s in ipairs(D.stanowiska) do
		local srodek = D.start + Vector3.new((i - 1) * D.odstep, 0, 0)
		local o = CFrame.new(srodek) * CFrame.Angles(0, math.rad(D.obrot), 0)
		local m = Instance.new("Model")
		m.Name = s.id
		m:SetAttribute("Atrybut", s.atrybut)
		-- mata: gracz stoi na niej przodem do rekwizytu
		local mata = czesc(m, "Mata", Vector3.new(4, 0.3, 4), o * CFrame.new(0, 0.15, 0), s.kolor)
		czesc(m, "Mata rant", Vector3.new(4.4, 0.2, 4.4), o * CFrame.new(0, 0.1, 0), CIEMNY)
		-- tabliczka z nazwą statystyki
		local tab = czesc(m, "Tabliczka", Vector3.new(3.6, 1.2, 0.3), o * CFrame.new(-3.4, 3.6, -1.4), DREWNO)
		czesc(m, "Tabliczka słup", Vector3.new(0.3, 3, 0.3), o * CFrame.new(-3.4, 1.5, -1.4), DREWNO)
		local sg = Instance.new("SurfaceGui")
		sg.Face = Enum.NormalId.Back
		sg.PixelsPerStud = 60
		sg.LightInfluence = 0
		local t = Instance.new("TextLabel")
		t.Size = UDim2.fromScale(1, 1)
		t.BackgroundTransparency = 1
		t.Text = s.nazwa
		t.TextScaled = true
		t.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
		t.TextColor3 = Color3.new(1, 1, 1)
		local st = Instance.new("UIStroke")
		st.Thickness = 3
		st.Parent = t
		t.Parent = sg
		sg.Parent = tab
		local rek = REKWIZYTY[s.id]
		if rek then
			rek(m, o, s.kolor)
		end
		-- podpowiedź E na macie
		local pp = Instance.new("ProximityPrompt")
		pp.ActionText = "Train " .. s.nazwa
		pp.ObjectText = s.czynnosc
		pp.KeyboardKeyCode = Enum.KeyCode.E
		pp.HoldDuration = 0
		pp.MaxActivationDistance = 9
		pp.RequiresLineOfSight = false
		pp.Parent = mata
		m.PrimaryPart = mata
		m.Parent = f
		miejsca[s.id] = o * CFrame.new(0, 3, 0)
	end
	f.Parent = workspace
	kontener = f
end
zbuduj()

------------------------------------------------------------------ stan treningu graczy (tylko w sesji)
type Trening = { id: string, postep: number, taps: number, oknoTap: number }
local trwa: { [Player]: Trening } = {}
local postepy: { [Player]: { [string]: number } } = {} -- pasek każdego stanowiska zostaje, gdy gracz odejdzie

local function wartosc(gracz: Player, atrybut: string): number
	local v = gracz:GetAttribute(atrybut)
	return if typeof(v) == "number" then v else 0
end

local function przyrostDla(gracz: Player): number
	local lv = gracz:GetAttribute("Level")
	return D.przyrost(if typeof(lv) == "number" then lv else 1)
end

local function dodajStatystyke(gracz: Player, s: any, ile: number)
	local tp = workspace:FindFirstChild("TreningProba")
	local sy = tp and tp:FindFirstChild("Sygnaly")
	local e = sy and sy:FindFirstChild("PrzyrostStatystyki")
	if e and e:IsA("BindableEvent") and workspace:FindFirstChild("StanGracza") then
		-- stan gracza Karola dopisuje do profilu (zapis) i do atrybutu
		e:Fire(gracz, { atrybut = s.atrybut, przyrost = ile, zrodlo = "TreningAFK", gra = "afk_" .. s.id })
	else
		gracz:SetAttribute(s.atrybut, wartosc(gracz, s.atrybut) + ile)
	end
end

local function zakoncz(gracz: Player)
	local t = trwa[gracz]
	if not t then
		return
	end
	postepy[gracz] = postepy[gracz] or {}
	postepy[gracz][t.id] = t.postep
	trwa[gracz] = nil
	gracz:SetAttribute("TreningAFK", nil)
	Z:FireClient(gracz, "koniec")
end

local function zacznij(gracz: Player, id: string)
	local s = D.stanowisko(id)
	local char = gracz.Character
	local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not (s and hrp and miejsca[id]) then
		return
	end
	if trwa[gracz] then
		zakoncz(gracz)
	end
	-- czy ktoś już tu stoi?
	for g, t in pairs(trwa) do
		if t.id == id and g ~= gracz then
			return
		end
	end
	hrp.CFrame = miejsca[id]
	local p = (postepy[gracz] and postepy[gracz][id]) or 0
	trwa[gracz] = { id = id, postep = p, taps = 0, oknoTap = os.clock() }
	gracz:SetAttribute("TreningAFK", id)
	Z:FireClient(gracz, "start", id, p, D.dlugoscPaska(wartosc(gracz, s.atrybut)), przyrostDla(gracz))
end

for _, m in ipairs(kontener:GetChildren()) do
	local pp = m:FindFirstChildWhichIsA("BasePart") and (m :: Model).PrimaryPart and (m :: Model).PrimaryPart:FindFirstChildOfClass("ProximityPrompt")
	if pp then
		local id = m.Name
		pp.Triggered:Connect(function(gracz)
			if trwa[gracz] and trwa[gracz].id == id then
				zakoncz(gracz)
			else
				zacznij(gracz, id)
			end
		end)
	end
end

Z.OnServerEvent:Connect(function(gracz: Player, akcja: unknown)
	local t = trwa[gracz]
	if not t then
		return
	end
	if akcja == "tap" then
		local teraz = os.clock()
		if teraz - t.oknoTap >= 1 then
			t.oknoTap = teraz
			t.taps = 0
		end
		if t.taps < D.tapMaksNaSekunde then
			t.taps += 1
			t.postep += D.tapWartosc
		end
	elseif akcja == "stop" then
		zakoncz(gracz)
	end
end)

------------------------------------------------------------------ licznik
local zebrane = 0
RunService.Heartbeat:Connect(function(dt)
	zebrane += dt
	if zebrane < D.krokSerwera then
		return
	end
	local krok = zebrane
	zebrane = 0
	for gracz, t in pairs(trwa) do
		local s = D.stanowisko(t.id)
		local char = gracz.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
		local hum = char and char:FindFirstChildOfClass("Humanoid")
		-- odległość w poziomie: skok (spacja = tapnięcie) nie przerywa treningu, odejście tak
		local roznica = hrp and (hrp.Position - miejsca[t.id].Position) or Vector3.zero
		if not (s and hrp and hum and hum.Health > 0) or Vector3.new(roznica.X, 0, roznica.Z).Magnitude > D.zasieg then
			zakoncz(gracz)
			continue
		end
		t.postep += D.afkNaSekunde * krok
		local dl = D.dlugoscPaska(wartosc(gracz, s.atrybut))
		if t.postep >= dl then
			t.postep -= dl
			local ile = przyrostDla(gracz)
			dodajStatystyke(gracz, s, ile)
			task.defer(function()
				-- nowa długość paska liczy się od wartości po przyroście
				Z:FireClient(gracz, "punkt", s.atrybut, ile, D.dlugoscPaska(wartosc(gracz, s.atrybut)))
			end)
		else
			Z:FireClient(gracz, "postep", t.postep, dl)
		end
	end
end)

Players.PlayerRemoving:Connect(function(gracz)
	trwa[gracz] = nil
	postepy[gracz] = nil
end)
