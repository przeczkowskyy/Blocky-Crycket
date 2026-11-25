--!strict
--[[
	TreningAFK — trening statystyk na stanowiskach AFK (D-141, Paweł 23.11; na main od 24.11 po rozmowie Pawła z Karolem —
	Diamenty za poziom D-140 zostały na gałęzi pawel/diamenty-afk).

	Stanowiska: kontener Workspace/TreningAFK (atrybut Wygenerowane), budowany przy starcie serwera z klocków na wolnym
	pasie placu w miasteczku (TreningAFKDane.start; agent Karola, sesja 25.11: od dziś w sali Training Center —
	TreningAFKDane.miejsca). Trzecia wersja (Paweł 23.11): każde stanowisko ma swoją czynność
	i animację postaci — hantle (Siła), wyciskanie sztangi na ławce (HP), bieżnia (Zręczność), czytanie książki
	(Inteligencja), blok tarczą przed pomidorami od NPC (Pancerz), rzut kośćmi (Szczęście).
	Animacje i ruch rekwizytów liczy klient (src/client/TreningAFKClient.client.luau) — serwer tylko stawia gracza
	na stanowisku (zakotwiczona postać: stoi albo leży na ławce) i liczy pasek.

	Pasek = D.powtorzenNaPasek powtórzeń; pełny → od razu +przyrost do statystyki. Co kilka sekund skill check:
	trafiony = chwilowo ×2.

	Statystyki: NIE piszemy ich sami. Przyrost idzie tym samym sygnałem co mini-gry Training Center:
	Workspace/TreningProba/Sygnaly/PrzyrostStatystyki (BindableEvent pakietu Karola), którego słucha stan gracza
	(swiat/stan_gracza: profil „wytrenowane”, zapis między sesjami, atrybut). Bez tych kontenerów przyrost trafia
	wprost do atrybutu gracza — tylko do prób.

	Zdalne: ReplicatedStorage.TreningAFK (RemoteEvent)
		klient → serwer: "check", numer | "stop"
		serwer → klient: "start", id, postep, przyrost | "postep", postep, tempo | "punkt", atrybut, ile, postep
		                 | "skillcheck", numer, okno | "trafiony", czas | "koniec"
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

------------------------------------------------------------------ klocki
local function czesc(rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3, ksztalt: Enum.PartType?,
	material: Enum.Material?): Part
	local p = Instance.new("Part")
	p.Name = nazwa
	p.Size = rozmiar
	p.CFrame = cf
	p.Color = kolor
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Material = material or Enum.Material.SmoothPlastic
	if ksztalt then
		p.Shape = ksztalt
	end
	p.Parent = rodzic
	return p
end

-- grupa części poruszana przez klienta jako całość (rekwizyt w dłoni, sztanga, kartka…): Model z PrimaryPart „Os”
local function grupa(rodzic: Instance, nazwa: string, cf: CFrame): (Model, Part)
	local m = Instance.new("Model")
	m.Name = nazwa
	local os_ = czesc(m, "Os", Vector3.new(0.2, 0.2, 0.2), cf, Color3.new(1, 1, 1))
	os_.Transparency = 1
	os_.CanCollide = false
	m.PrimaryPart = os_
	m.Parent = rodzic
	return m, os_
end

local function bezKolizji(m: Instance)
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
		end
	end
end

local CIEMNY = Color3.fromRGB(45, 42, 48)
local DREWNO = Color3.fromRGB(150, 98, 60)
local DREWNO_J = Color3.fromRGB(196, 142, 92)
local STAL = Color3.fromRGB(170, 175, 185)
local CZERWONY = Color3.fromRGB(214, 70, 64)

-- hantla wzdłuż osi X, środek w (0,0,0) układu cf
local function hantla(rodzic: Instance, nazwa: string, cf: CFrame, kolor: Color3)
	local m = grupa(rodzic, nazwa, cf)
	czesc(m, "Drążek", Vector3.new(1.3, 0.28, 0.28), cf, STAL)
	for _, x in ipairs({ -0.6, 0.6 }) do
		czesc(m, "Krążek", Vector3.new(0.34, 0.9, 0.9), cf * CFrame.new(x, 0, 0), kolor, Enum.PartType.Cylinder)
	end
	bezKolizji(m)
	return m
end

--[[ Rekwizyty: wszystko względem środka maty `o` (gracz stoi w o, patrzy w −Z układu o). Nazwy grup, które rusza
	klient: Hantla_L / Hantla_P (Siła), Sztanga (HP), Ksiazka + Kartka (Inteligencja), Tasma_* (bieżnia), Tarcza,
	Rzucajacy (+ Rzucajacy_Ramie), Kubek + Kosc_1/2 (Szczęście). ]]
local REKWIZYTY: { [string]: (Model, CFrame, Color3) -> () } = {
	Sila = function(m, o, k)
		-- stojak z zapasowymi hantlami z boku + dwie hantle do rąk (leżą na stojaku, klient przenosi je do dłoni)
		czesc(m, "Stojak", Vector3.new(1.6, 0.3, 4.4), o * CFrame.new(3.4, 2.1, -0.6), DREWNO)
		czesc(m, "Stojak półka", Vector3.new(1.6, 0.3, 4.4), o * CFrame.new(3.4, 1.0, -0.6), DREWNO)
		for _, z in ipairs({ -2.6, 1.4 }) do
			czesc(m, "Stojak noga", Vector3.new(0.3, 2.2, 0.3), o * CFrame.new(3.4, 1.1, z), DREWNO)
		end
		for i, z in ipairs({ -2.2, -1.2, -0.2, 0.8 }) do
			hantla(m, "Zapas", o * CFrame.new(3.4, if i % 2 == 0 then 2.7 else 1.6, z) * CFrame.Angles(0, math.rad(90), 0), CIEMNY)
		end
		hantla(m, "Hantla_L", o * CFrame.new(3.4, 2.7, 1.0) * CFrame.Angles(0, math.rad(90), 0), k)
		hantla(m, "Hantla_P", o * CFrame.new(3.4, 1.6, 1.4) * CFrame.Angles(0, math.rad(90), 0), k)
	end,
	Kondycja = function(m, o, k)
		-- długa ławka wzdłuż Z (gracz leży na plecach, głowa w stronę +Z) + stojak ze sztangą nad głową
		czesc(m, "Ławka", Vector3.new(1.8, 0.5, 6), o * CFrame.new(0, 1.55, 0), k)
		czesc(m, "Ławka obicie", Vector3.new(1.9, 0.2, 6.1), o * CFrame.new(0, 1.25, 0), CIEMNY)
		for _, z in ipairs({ -2.4, 2.4 }) do
			czesc(m, "Ławka noga", Vector3.new(1.4, 1.2, 0.4), o * CFrame.new(0, 0.6, z), CIEMNY)
		end
		for _, x in ipairs({ -1.9, 1.9 }) do
			czesc(m, "Stojak", Vector3.new(0.35, 4.4, 0.35), o * CFrame.new(x, 2.2, 2.3), STAL)
			czesc(m, "Stojak hak", Vector3.new(0.35, 0.35, 0.6), o * CFrame.new(x, 4.3, 2.1), STAL)
		end
		local g = grupa(m, "Sztanga", o * CFrame.new(0, 4.5, 2.1))
		czesc(g, "Drążek", Vector3.new(6, 0.3, 0.3), o * CFrame.new(0, 4.5, 2.1), STAL)
		for _, x in ipairs({ -2.6, 2.6 }) do
			czesc(g, "Krążek", Vector3.new(0.45, 1.8, 1.8), o * CFrame.new(x, 4.5, 2.1), CIEMNY, Enum.PartType.Cylinder)
			czesc(g, "Krążek mały", Vector3.new(0.3, 1.2, 1.2), o * CFrame.new(x + (if x > 0 then -0.38 else 0.38), 4.5, 2.1), k,
				Enum.PartType.Cylinder)
		end
		bezKolizji(g)
	end,
	Zrecznosc = function(m, o, k)
		-- bieżnia: pokład z taśmą (gracz biegnie w miejscu, patrząc w −Z), konsola z poręczami z przodu
		czesc(m, "Bieżnia rama", Vector3.new(3.2, 0.7, 6.4), o * CFrame.new(0, 0.35, 0.2), CIEMNY)
		czesc(m, "Bieżnia taśma", Vector3.new(2.4, 0.12, 5.8), o * CFrame.new(0, 0.76, 0.2), Color3.fromRGB(30, 30, 34))
		for i = 1, 6 do
			local p = czesc(m, "Tasma_" .. i, Vector3.new(2.3, 0.05, 0.22), o * CFrame.new(0, 0.84, -2.6 + (i - 1) * 1.0),
				Color3.fromRGB(80, 80, 90))
			p.CanCollide = false
		end
		czesc(m, "Rolka", Vector3.new(0.7, 0.7, 3.0), o * CFrame.new(0, 0.45, -3.0) * CFrame.Angles(0, math.rad(90), 0), STAL,
			Enum.PartType.Cylinder)
		for _, x in ipairs({ -1.45, 1.45 }) do
			czesc(m, "Słupek", Vector3.new(0.3, 3.6, 0.3), o * CFrame.new(x, 2.4, -2.8), STAL)
			czesc(m, "Poręcz", Vector3.new(0.25, 0.25, 2.6), o * CFrame.new(x, 3.6, -1.6), STAL)
		end
		czesc(m, "Konsola", Vector3.new(3.2, 1.2, 0.6), o * CFrame.new(0, 4.3, -2.9) * CFrame.Angles(math.rad(-25), 0, 0), k)
		local ekran = czesc(m, "Ekran", Vector3.new(1.8, 0.6, 0.1), o * CFrame.new(0, 4.4, -2.58) * CFrame.Angles(math.rad(-25), 0, 0),
			Color3.fromRGB(120, 255, 160), nil, Enum.Material.Neon)
		ekran.CanCollide = false
	end,
	Inteligencja = function(m, o, k)
		-- regał z książkami z boku (nie zasłania czytającego od strony placu) + otwarta książka do rąk
		local r = o * CFrame.new(3.6, 0, -0.4) * CFrame.Angles(0, math.rad(90), 0)
		czesc(m, "Regał", Vector3.new(4.6, 5, 1.2), r * CFrame.new(0, 2.5, 0), DREWNO)
		local kolory = { CZERWONY, Color3.fromRGB(80, 130, 220), Color3.fromRGB(90, 180, 90), Color3.fromRGB(230, 190, 70), k }
		for polka = 0, 2 do
			for i = 0, 7 do
				czesc(m, "Tom", Vector3.new(0.42, 1.1, 0.8), r * CFrame.new(-1.8 + i * 0.52, 0.9 + polka * 1.5, -0.35),
					kolory[(i + polka) % #kolory + 1])
			end
		end
		local g = grupa(m, "Ksiazka", o * CFrame.new(-3.2, 1.2, -1))
		-- układ książki: grzbiet wzdłuż Z, strony otwarte w X, środek w Os
		czesc(g, "Okładka L", Vector3.new(1.05, 0.12, 1.5), o * CFrame.new(-3.2 - 0.55, 1.2, -1), k)
		czesc(g, "Okładka P", Vector3.new(1.05, 0.12, 1.5), o * CFrame.new(-3.2 + 0.55, 1.2, -1), k)
		czesc(g, "Strony L", Vector3.new(0.95, 0.14, 1.36), o * CFrame.new(-3.2 - 0.52, 1.3, -1), Color3.fromRGB(250, 244, 226))
		czesc(g, "Strony P", Vector3.new(0.95, 0.14, 1.36), o * CFrame.new(-3.2 + 0.52, 1.3, -1), Color3.fromRGB(250, 244, 226))
		bezKolizji(g)
		local kart = grupa(m, "Kartka", o * CFrame.new(-3.2, 1.38, -1))
		czesc(kart, "Arkusz", Vector3.new(0.92, 0.03, 1.32), o * CFrame.new(-3.2 + 0.47, 1.38, -1), Color3.fromRGB(255, 250, 236))
		bezKolizji(kart)
		czesc(m, "Stolik", Vector3.new(1.6, 0.3, 1.6), o * CFrame.new(-3.2, 1.0, -1), DREWNO)
		czesc(m, "Stolik noga", Vector3.new(0.4, 1.0, 0.4), o * CFrame.new(-3.2, 0.5, -1), DREWNO)
	end,
	Pancerz = function(m, o, k)
		-- NPC z koszem pomidorów 11 st przed graczem (patrzy na gracza) + tarcza na stojaku obok maty
		local n = o * CFrame.new(0, 0, -11) * CFrame.Angles(0, math.rad(180), 0)
		-- agent Karola, sesja 25.11: NPC stoi poza salą (na placyku) — stopy na ziemi pod nim, nie na wysokości posadzki
		local grunt = workspace:Raycast(n.Position + Vector3.new(0, 6, 0), Vector3.new(0, -12, 0))
		if grunt then
			n += Vector3.new(0, grunt.Position.Y - n.Position.Y, 0)
		end
		local rz = Instance.new("Model")
		rz.Name = "Rzucajacy"
		local skora = Color3.fromRGB(236, 190, 150)
		czesc(rz, "Noga", Vector3.new(0.9, 2, 0.9), n * CFrame.new(-0.5, 1, 0), Color3.fromRGB(70, 80, 120))
		czesc(rz, "Noga", Vector3.new(0.9, 2, 0.9), n * CFrame.new(0.5, 1, 0), Color3.fromRGB(70, 80, 120))
		czesc(rz, "Tułów", Vector3.new(2, 2, 1), n * CFrame.new(0, 3, 0), Color3.fromRGB(220, 150, 60))
		czesc(rz, "Fartuch", Vector3.new(1.6, 1.6, 0.1), n * CFrame.new(0, 2.8, -0.55), Color3.new(1, 1, 1))
		czesc(rz, "Głowa", Vector3.new(1.2, 1.2, 1.2), n * CFrame.new(0, 4.6, 0), skora)
		czesc(rz, "Czapka", Vector3.new(1.3, 0.5, 1.3), n * CFrame.new(0, 5.4, 0), CZERWONY)
		czesc(rz, "Oko", Vector3.new(0.18, 0.18, 0.05), n * CFrame.new(-0.25, 4.7, -0.61), CIEMNY)
		czesc(rz, "Oko", Vector3.new(0.18, 0.18, 0.05), n * CFrame.new(0.25, 4.7, -0.61), CIEMNY)
		czesc(rz, "Ręka L", Vector3.new(0.8, 2, 0.8), n * CFrame.new(-1.4, 3, 0), skora)
		-- prawa ręka obraca się wokół barku (Os = bark)
		local ramie = grupa(rz, "Rzucajacy_Ramie", n * CFrame.new(1.4, 3.9, 0))
		czesc(ramie, "Ręka P", Vector3.new(0.8, 2, 0.8), n * CFrame.new(1.4, 3, 0), skora)
		czesc(ramie, "Pomidor w ręce", Vector3.new(0.6, 0.6, 0.6), n * CFrame.new(1.4, 1.8, 0), CZERWONY, Enum.PartType.Ball)
		czesc(rz, "Kosz", Vector3.new(1.6, 1, 1.6), n * CFrame.new(-2.4, 0.5, 0.4), DREWNO_J, Enum.PartType.Cylinder)
		for i = 1, 4 do
			czesc(rz, "Pomidor", Vector3.new(0.6, 0.6, 0.6), n * CFrame.new(-2.4 + (i % 2) * 0.4 - 0.2, 1.2, 0.4 + (i > 2 and 0.3 or -0.3)),
				CZERWONY, Enum.PartType.Ball)
		end
		bezKolizji(rz)
		rz.Parent = m
		-- tarcza (klient przenosi ją do lewej dłoni)
		local g = grupa(m, "Tarcza", o * CFrame.new(-3.2, 2, 0))
		czesc(g, "Tarcza", Vector3.new(0.3, 2.6, 2.6), o * CFrame.new(-3.2, 2, 0), k, Enum.PartType.Cylinder)
		czesc(g, "Tarcza rant", Vector3.new(0.25, 2.8, 2.8), o * CFrame.new(-3.25, 2, 0), STAL, Enum.PartType.Cylinder)
		czesc(g, "Tarcza guz", Vector3.new(0.4, 0.7, 0.7), o * CFrame.new(-3.05, 2, 0), STAL, Enum.PartType.Ball)
		bezKolizji(g)
		czesc(m, "Stojak tarczy", Vector3.new(0.3, 1.2, 0.3), o * CFrame.new(-3.4, 0.6, 0), DREWNO)
	end,
	Szczescie = function(m, o, k)
		-- stolik przed graczem, kubek do kości w dłoni, dwie kości
		-- agent Karola, sesja 25.11: stolik niżej o 0,5 (blat 2,25) — kot (wzrost ok. 2,8 st) miał blat na wysokości brody
		-- i kubek w dłoni wchodził w krawędź stolika; człowiekowi blat sięga teraz do bioder
		czesc(m, "Stolik", Vector3.new(3.6, 0.3, 2.4), o * CFrame.new(0, 2.1, -2.6), Color3.fromRGB(40, 120, 70))
		czesc(m, "Stolik rant", Vector3.new(3.8, 0.4, 2.6), o * CFrame.new(0, 1.95, -2.6), DREWNO)
		czesc(m, "Stolik noga", Vector3.new(0.6, 1.9, 0.6), o * CFrame.new(0, 0.95, -2.6), DREWNO)
		local kub = grupa(m, "Kubek", o * CFrame.new(1.2, 2.6, -2.4))
		czesc(kub, "Kubek", Vector3.new(0.9, 0.9, 0.9), o * CFrame.new(1.2, 2.6, -2.4), Color3.fromRGB(110, 70, 40), Enum.PartType.Cylinder)
		bezKolizji(kub)
		for i = 1, 2 do
			local g = grupa(m, "Kosc_" .. i, o * CFrame.new(-0.6 + i * 0.6, 2.5, -2.6))
			czesc(g, "Kość", Vector3.new(0.5, 0.5, 0.5), o * CFrame.new(-0.6 + i * 0.6, 2.5, -2.6), if i == 1 then Color3.new(1, 1, 1) else k)
			bezKolizji(g)
		end
	end,
}

------------------------------------------------------------------ budowa
local kontener: Folder
local miejsca: { [string]: CFrame } = {} -- środek maty (wysokość podłogi) i kierunek stanowiska

local function zbuduj()
	local stary = workspace:FindFirstChild("TreningAFK")
	if stary then
		stary:Destroy()
	end
	local f = Instance.new("Folder")
	f.Name = "TreningAFK"
	f:SetAttribute("Wygenerowane", true)
	for i, s in ipairs(D.stanowiska) do
		-- agent Karola, sesja 25.11: miejsce z D.miejsca (sala Training Center), bez wpisu — dawny rząd od D.start
		local miejsce = D.miejsca and D.miejsca[s.id]
		local srodek = if miejsce then miejsce.pozycja else D.start + Vector3.new((i - 1) * D.odstep, 0, 0)
		local o = CFrame.new(srodek) * CFrame.Angles(0, math.rad(if miejsce then miejsce.obrot else D.obrot), 0)
		local m = Instance.new("Model")
		m.Name = s.id
		m:SetAttribute("Atrybut", s.atrybut)
		local mata = czesc(m, "Mata", Vector3.new(4, 0.3, 4), o * CFrame.new(0, 0.15, 0), s.kolor)
		czesc(m, "Mata rant", Vector3.new(4.4, 0.2, 4.4), o * CFrame.new(0, 0.1, 0), CIEMNY)
		-- tabliczka z nazwą statystyki (z przodu stanowiska, czytelna z placu)
		local tab = czesc(m, "Tabliczka", Vector3.new(3.6, 1.2, 0.3), o * CFrame.new(-2.6, 3.6, 3.2), DREWNO)
		czesc(m, "Tabliczka słup", Vector3.new(0.3, 3, 0.3), o * CFrame.new(-2.6, 1.5, 3.2), DREWNO)
		for _, strona in ipairs({ Enum.NormalId.Front, Enum.NormalId.Back }) do
			local sg = Instance.new("SurfaceGui")
			sg.Face = strona
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
		end
		local rek = REKWIZYTY[s.id]
		if rek then
			rek(m, o, s.kolor)
		end
		local pp = Instance.new("ProximityPrompt")
		pp.ActionText = "Train " .. s.nazwa
		pp.ObjectText = s.czynnosc
		pp.KeyboardKeyCode = Enum.KeyCode.E
		pp.HoldDuration = 0
		pp.MaxActivationDistance = 10
		pp.RequiresLineOfSight = false
		pp.Parent = mata
		m.PrimaryPart = mata
		m.Parent = f
		miejsca[s.id] = o
	end
	f.Parent = workspace
	kontener = f
end
zbuduj()

-- gdzie stoi (leży) korzeń postaci na stanowisku: w układzie o, wysokość z HipHeight awatara
local function pozaKorzenia(id: string, hum: Humanoid, hrp: BasePart): CFrame
	local o = miejsca[id]
	local stoi = hum.HipHeight + hrp.Size.Y / 2
	if id == "Kondycja" then
		-- na plecach na ławce (wierzch ławki ~1,8), głowa w stronę +Z układu o, twarz do nieba
		return o * CFrame.new(0, 1.8 + hrp.Size.Z / 2 + 0.25, 0.4) * CFrame.Angles(math.rad(90), 0, 0)
	elseif id == "Zrecznosc" then
		return o * CFrame.new(0, 0.82 + stoi, 0.4)
	end
	return o * CFrame.new(0, 0.3 + stoi, 0)
end

------------------------------------------------------------------ stan treningu graczy (tylko w sesji)
-- postep liczony w powtórzeniach (0 … D.powtorzenNaPasek); skill check: serwer losuje chwilę i numer,
-- klient odsyła numer; trafienie w oknie czasu = przyspieszenie
type Trening = { id: string, postep: number, nastepnyCheck: number, check: number?, checkDo: number, szybkoDo: number }
local trwa: { [Player]: Trening } = {}
local postepy: { [Player]: { [string]: number } } = {} -- niepełny pasek stanowiska zostaje, gdy gracz odejdzie
local licznikCheck = 0

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
		e:Fire(gracz, { atrybut = s.atrybut, przyrost = ile, zrodlo = "TreningAFK", gra = "afk_" .. s.id })
	else
		gracz:SetAttribute(s.atrybut, wartosc(gracz, s.atrybut) + ile)
	end
end

local function losujCheck(): number
	return os.clock() + D.skillCheckCoMin + math.random() * (D.skillCheckCoMaks - D.skillCheckCoMin)
end

local function korzen(gracz: Player): (BasePart?, Humanoid?)
	local char = gracz.Character
	return char and char:FindFirstChild("HumanoidRootPart") :: BasePart?, char and char:FindFirstChildOfClass("Humanoid")
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
	local hrp, hum = korzen(gracz)
	if hrp and hum then
		hrp.Anchored = false
		-- zejście ze stanowiska: przed matę, na stojąco
		local o = miejsca[t.id]
		hrp.CFrame = o * CFrame.new(0, 0.3 + hum.HipHeight + hrp.Size.Y / 2, 3) * CFrame.Angles(0, math.rad(180), 0)
	end
	Z:FireClient(gracz, "koniec")
end

local function zacznij(gracz: Player, id: string)
	local s = D.stanowisko(id)
	local hrp, hum = korzen(gracz)
	if not (s and hrp and hum and miejsca[id]) then
		return
	end
	if trwa[gracz] then
		zakoncz(gracz)
	end
	for g, t in pairs(trwa) do
		if t.id == id and g ~= gracz then
			return -- ktoś już tu trenuje
		end
	end
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.CFrame = pozaKorzenia(id, hum, hrp)
	hrp.Anchored = true
	local p = (postepy[gracz] and postepy[gracz][id]) or 0
	trwa[gracz] = { id = id, postep = p, nastepnyCheck = losujCheck(), check = nil, checkDo = 0, szybkoDo = 0 }
	gracz:SetAttribute("TreningAFK", id)
	Z:FireClient(gracz, "start", id, p, przyrostDla(gracz))
end

for _, m in ipairs(kontener:GetChildren()) do
	local mata = (m :: Model).PrimaryPart
	local pp = mata and mata:FindFirstChildOfClass("ProximityPrompt")
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

Z.OnServerEvent:Connect(function(gracz: Player, akcja: unknown, numer: unknown)
	local t = trwa[gracz]
	if not t then
		return
	end
	if akcja == "check" then
		if t.check ~= nil and numer == t.check and os.clock() <= t.checkDo + 0.25 then
			t.check = nil
			t.szybkoDo = os.clock() + D.czasPrzyspieszenia
			t.nastepnyCheck = losujCheck()
			Z:FireClient(gracz, "trafiony", D.czasPrzyspieszenia)
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
	local teraz = os.clock()
	for gracz, t in pairs(trwa) do
		local s = D.stanowisko(t.id)
		local hrp, hum = korzen(gracz)
		if not (s and hrp and hum and hum.Health > 0 and hrp.Anchored) then
			-- śmierć, odrodzenie albo ktoś odkotwiczył postać
			zakoncz(gracz)
			continue
		end
		local tempo = if teraz < t.szybkoDo then D.mnoznikSkillCheck else 1
		t.postep += krok * tempo / D.czasPowtorzenia
		if t.postep >= D.powtorzenNaPasek then
			t.postep -= D.powtorzenNaPasek
			local ile = przyrostDla(gracz)
			dodajStatystyke(gracz, s, ile)
			Z:FireClient(gracz, "punkt", s.atrybut, ile, t.postep)
		else
			Z:FireClient(gracz, "postep", t.postep, tempo)
		end
		if t.check == nil and teraz >= t.nastepnyCheck then
			licznikCheck += 1
			t.check = licznikCheck
			t.checkDo = teraz + D.skillCheckOkno
			Z:FireClient(gracz, "skillcheck", licznikCheck, D.skillCheckOkno)
		elseif t.check ~= nil and teraz > t.checkDo + 0.25 then
			t.check = nil -- nie trafił: nic się nie dzieje
			t.nastepnyCheck = losujCheck()
		end
	end
end)

Players.PlayerRemoving:Connect(function(gracz)
	trwa[gracz] = nil
	postepy[gracz] = nil
end)
