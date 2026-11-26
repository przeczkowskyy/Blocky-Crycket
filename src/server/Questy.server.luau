--!strict
--[[
	Questy — tablica questów (Paweł 25.11: tablica w miasteczku zamiast rankingu; gracz wybiera questy, wybrane
	trafiają do wysuwanej szuflady po prawej). Wersja bazowa u Pawła; okno: src/client/OknoQuestowClient.client.luau,
	szuflada: src/client/QuestyClient.client.luau. Status: propozycja (B&C/UI/Tablica questów (propozycja).md).

	Dwa rodzaje: DZIENNE (zerują się o północy UTC) i OSIĄGNIĘCIA (jednorazowe). Postęp liczy się zawsze, także
	bez wybrania; „śledzenie” (do MAKS_SLEDZONYCH) tylko przypina quest do szuflady. Nagrodę gracz odbiera na tablicy.

	Skąd postęp (bez zmian w plikach Karola — serwer patrzy na atrybuty gracza i jedno własne zdarzenie):
	  kostka    — zmiana atrybutu MistrzPole (src/server/MistrzGier.server.luau: każdy rzut przesuwa pionek)
	  plansza   — wzrost atrybutu MistrzPlansza
	  walki     — wzrost atrybutu XP albo Level (XP daje dziś tylko wygrana walka)
	  rybki     — przyrost atrybutu Gold (Rybki, D-146), sumowane same przyrosty
	  drzewko   — zmiana atrybutu SkillTree (zakup węzła)
	  poziom    — atrybut Level (wartość, nie licznik)
	  jajka     — ServerStorage.QuestPostep:Fire(gracz, "jajka", n) z src/server/JajkoKorowe.server.luau
	Inne skrypty serwera mogą zgłaszać postęp tak samo: ServerStorage.QuestPostep:Fire(gracz, licznik, ile).

	Stan jest na czas sesji (pamięć serwera) — zapis profilu dojdzie ze stanem gracza Karola (pytanie w sejfie).
	Nagrody wypłaca stan gracza Karola: Workspace/StanGracza/Sygnaly/SterowanieSerwera("przyznaj", gracz, lup);
	bez niego quest zostaje „do odebrania”, a okno mówi dlaczego.

	Zdalne: ReplicatedStorage.Questy (RemoteFunction)
	    "stan"        → { ok, dzienne = { wiersz… }, osiagniecia = { wiersz… }, sledzone = { id… }, maks, doPolnocy }
	    "sledz", id   → przypina / odpina quest (ten sam kształt odpowiedzi + tekst przy odmowie)
	    "odbierz", id → wypłaca nagrodę
	  wiersz = { id, nazwa, opis, postep, cel, nagroda, waluta = "fish" | "gems", gotowe, odebrane, sledzone }
	ReplicatedStorage.QuestyZdarzenia (RemoteEvent, serwer → klient): "stan", ta sama tabela — po zmianie postępu.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local MAKS_SLEDZONYCH = 3
local LIMIT = 0.25 -- s między zapytaniami gracza
local WYSYLKA_CO = 1 -- s: najczęściej tyle razy serwer wysyła klientowi nowy stan
local ROZBIEG = 10 -- s po wejściu gracza: stan gracza wczytuje wtedy profil (Rybki, XP) — to nie jest postęp

type Def = { id: string, nazwa: string, opis: string, licznik: string, cel: number, nagroda: number, waluta: string }

-- liczby robocze — do kalkulatora balansu
local DZIENNE: { Def } = {
	{ id = "d_walki", nazwa = "FOREST PATROL", opis = "Win fights", licznik = "walki", cel = 5, nagroda = 200, waluta = "fish" },
	{ id = "d_jajka", nazwa = "EGG HUNTER", opis = "Hatch eggs", licznik = "jajka", cel = 3, nagroda = 300, waluta = "fish" },
	{ id = "d_kostka", nazwa = "LUCKY ROLL", opis = "Roll the dice", licznik = "kostka", cel = 5, nagroda = 150, waluta = "fish" },
	{ id = "d_rybki", nazwa = "FISH MARKET", opis = "Earn fish", licznik = "rybki", cel = 500, nagroda = 3, waluta = "gems" },
	{ id = "d_drzewko", nazwa = "STUDENT", opis = "Buy skill tree upgrades", licznik = "drzewko", cel = 1, nagroda = 2, waluta = "gems" },
}
local OSIAGNIECIA: { Def } = {
	{ id = "o_poziom5", nazwa = "RISING STAR", opis = "Reach level", licznik = "poziom", cel = 5, nagroda = 10, waluta = "gems" },
	{ id = "o_poziom10", nazwa = "LOCAL HERO", opis = "Reach level", licznik = "poziom", cel = 10, nagroda = 25, waluta = "gems" },
	{ id = "o_walki25", nazwa = "MONSTER SLAYER", opis = "Win fights", licznik = "walki", cel = 25, nagroda = 500, waluta = "fish" },
	{ id = "o_jajka10", nazwa = "PET COLLECTOR", opis = "Hatch eggs", licznik = "jajka", cel = 10, nagroda = 15, waluta = "gems" },
	{ id = "o_plansza", nazwa = "BOARD MASTER", opis = "Finish a game master board", licznik = "plansza", cel = 1, nagroda = 10, waluta = "gems" },
	{ id = "o_rybki5000", nazwa = "FISH TYCOON", opis = "Earn fish", licznik = "rybki", cel = 5000, nagroda = 20, waluta = "gems" },
}
local DEF: { [string]: Def } = {}
local CZY_DZIENNY: { [string]: boolean } = {}
for _, d in ipairs(DZIENNE) do
	DEF[d.id] = d
	CZY_DZIENNY[d.id] = true
end
for _, d in ipairs(OSIAGNIECIA) do
	DEF[d.id] = d
end

local function zdalny(klasa: string, nazwa: string): Instance
	local i = RS:FindFirstChild(nazwa)
	if not i then
		i = Instance.new(klasa)
		i.Name = nazwa
		i.Parent = RS
	end
	return i :: Instance
end
local F = zdalny("RemoteFunction", "Questy") :: RemoteFunction
local Z = zdalny("RemoteEvent", "QuestyZdarzenia") :: RemoteEvent
local postepZdarzenie = ServerStorage:FindFirstChild("QuestPostep") :: BindableEvent?
if not postepZdarzenie then
	local e = Instance.new("BindableEvent")
	e.Name = "QuestPostep"
	e.Parent = ServerStorage
	postepZdarzenie = e
end

type Stan = {
	dzien: string,
	dzienne: { [string]: number }, -- liczniki od północy
	stale: { [string]: number }, -- liczniki od początku sesji
	odebrane: { [string]: boolean },
	sledzone: { string },
	ostatnie: number,
	brudny: boolean,
	poprzednie: { [string]: any }, -- ostatnie wartości atrybutów (do liczenia przyrostów)
}
local stany: { [Player]: Stan } = {}

local function dzis(): string
	return os.date("!%Y%m%d") :: string
end

local function stan(gracz: Player): Stan
	local s = stany[gracz]
	if not s then
		s = { dzien = dzis(), dzienne = {}, stale = {}, odebrane = {}, sledzone = {}, ostatnie = 0, brudny = false, poprzednie = {} }
		stany[gracz] = s
	end
	if s.dzien ~= dzis() then
		-- nowy dzień: liczniki dzienne od zera, odebrane dzienne wracają, śledzone dzienne zostają przypięte
		s.dzien = dzis()
		s.dzienne = {}
		for id in pairs(s.odebrane) do
			if CZY_DZIENNY[id] then
				s.odebrane[id] = nil
			end
		end
		s.brudny = true
	end
	return s
end

local function licznik(gracz: Player, s: Stan, d: Def): number
	if d.licznik == "poziom" then
		local lv = gracz:GetAttribute("Level")
		return if typeof(lv) == "number" then lv else 1
	end
	local t = if CZY_DZIENNY[d.id] then s.dzienne else s.stale
	return t[d.licznik] or 0
end

local function wiersz(gracz: Player, s: Stan, d: Def)
	local p = math.min(licznik(gracz, s, d), d.cel)
	return {
		id = d.id, nazwa = d.nazwa, opis = d.opis, postep = p, cel = d.cel, nagroda = d.nagroda, waluta = d.waluta,
		gotowe = p >= d.cel, odebrane = s.odebrane[d.id] == true, sledzone = table.find(s.sledzone, d.id) ~= nil,
	}
end

local function widok(gracz: Player, s: Stan)
	local w = { ok = true, dzienne = {}, osiagniecia = {}, sledzone = table.clone(s.sledzone), maks = MAKS_SLEDZONYCH,
		doPolnocy = 86400 - (os.time() % 86400) }
	for _, d in ipairs(DZIENNE) do
		table.insert(w.dzienne, wiersz(gracz, s, d))
	end
	for _, d in ipairs(OSIAGNIECIA) do
		table.insert(w.osiagniecia, wiersz(gracz, s, d))
	end
	return w
end

local function dodaj(gracz: Player, nazwa: string, ile: number)
	if ile <= 0 or not gracz.Parent then
		return
	end
	local s = stan(gracz)
	s.dzienne[nazwa] = (s.dzienne[nazwa] or 0) + ile
	s.stale[nazwa] = (s.stale[nazwa] or 0) + ile
	s.brudny = true
end

(postepZdarzenie :: BindableEvent).Event:Connect(function(gracz: any, nazwa: any, ile: any)
	if typeof(gracz) == "Instance" and gracz:IsA("Player") and type(nazwa) == "string" then
		dodaj(gracz, nazwa, if type(ile) == "number" then ile else 1)
	end
end)

-- atrybuty gracza → liczniki
local function obserwuj(gracz: Player)
	local s = stan(gracz)
	local od = os.clock() + ROZBIEG
	local function atrybut(nazwa: string, zmiana: (stara: any, nowa: any) -> ())
		s.poprzednie[nazwa] = gracz:GetAttribute(nazwa)
		gracz:GetAttributeChangedSignal(nazwa):Connect(function()
			local nowa = gracz:GetAttribute(nazwa)
			local stara = s.poprzednie[nazwa]
			s.poprzednie[nazwa] = nowa
			if stara ~= nil and nowa ~= nil and nowa ~= stara and os.clock() >= od then -- wczytanie profilu to nie postęp
				zmiana(stara, nowa)
			end
		end)
	end
	atrybut("MistrzPole", function()
		dodaj(gracz, "kostka", 1)
	end)
	atrybut("MistrzPlansza", function(stara, nowa)
		if typeof(stara) == "number" and typeof(nowa) == "number" and nowa > stara then
			dodaj(gracz, "plansza", nowa - stara)
		end
	end)
	atrybut("Gold", function(stara, nowa)
		if typeof(stara) == "number" and typeof(nowa) == "number" and nowa > stara then
			dodaj(gracz, "rybki", nowa - stara)
		end
	end)
	atrybut("SkillTree", function()
		dodaj(gracz, "drzewko", 1)
	end)
	local function walka(stara: any, nowa: any)
		if typeof(stara) == "number" and typeof(nowa) == "number" and nowa > stara then
			dodaj(gracz, "walki", 1)
		end
	end
	atrybut("XP", walka)
	atrybut("Level", function(stara, nowa)
		-- awans zeruje XP (spadek), więc wygraną z awansem łapiemy po poziomie; brudny = odświeżenie osiągnięć „poziom”
		walka(stara, nowa)
		s.brudny = true
	end)
end

local function wyplac(gracz: Player, d: Def): boolean
	local k = workspace:FindFirstChild("StanGracza")
	local sy = k and k:FindFirstChild("Sygnaly")
	local f = sy and sy:FindFirstChild("SterowanieSerwera")
	if not (f and f:IsA("BindableFunction")) then
		return false
	end
	local lup = { zloto = 0, gemy = 0, doswiadczenie = 0, tokeny_krainy = 0, kraina = "" }
	if d.waluta == "gems" then
		lup.gemy = d.nagroda
	else
		lup.zloto = d.nagroda
	end
	local ok, w = pcall(function()
		return (f :: BindableFunction):Invoke("przyznaj", gracz, lup)
	end)
	return ok and type(w) == "table" and w.ok == true
end

F.OnServerInvoke = function(gracz: Player, akcja: any, id: any)
	local s = stan(gracz)
	local t = os.clock()
	if t - s.ostatnie < LIMIT then
		return { ok = false, tekst = "Too fast" }
	end
	s.ostatnie = t
	if akcja == "stan" then
		return widok(gracz, s)
	end
	local d = if type(id) == "string" and #id <= 32 then DEF[id] else nil
	if not d then
		return { ok = false, tekst = "?" }
	end
	local tekst: string? = nil
	if akcja == "sledz" then
		local i = table.find(s.sledzone, d.id)
		if i then
			table.remove(s.sledzone, i)
		elseif s.odebrane[d.id] then
			tekst = "Already claimed"
		elseif #s.sledzone >= MAKS_SLEDZONYCH then
			tekst = string.format("You can track %d quests", MAKS_SLEDZONYCH)
		else
			table.insert(s.sledzone, d.id)
		end
	elseif akcja == "odbierz" then
		if s.odebrane[d.id] then
			tekst = "Already claimed"
		elseif licznik(gracz, s, d) < d.cel then
			tekst = "Not finished yet"
		else
			-- rezerwacja przed wypłatą: drugie kliknięcie w trakcie nie wypłaci drugi raz
			s.odebrane[d.id] = true
			if wyplac(gracz, d) then
				local i = table.find(s.sledzone, d.id)
				if i then
					table.remove(s.sledzone, i)
				end
				tekst = string.format("+%d %s", d.nagroda, if d.waluta == "gems" then "GEMS" else "FISH")
			else
				s.odebrane[d.id] = nil
				tekst = "Rewards need the player state (Karol) - try later"
			end
		end
	else
		return { ok = false, tekst = "?" }
	end
	local w = widok(gracz, s) :: any
	w.tekst = tekst
	s.brudny = false
	return w
end

Players.PlayerAdded:Connect(obserwuj)
for _, g in ipairs(Players:GetPlayers()) do
	obserwuj(g)
end
Players.PlayerRemoving:Connect(function(g)
	stany[g] = nil
end)

-- po zmianie postępu klient dostaje nowy stan (najwyżej raz na WYSYLKA_CO s)
task.spawn(function()
	while true do
		task.wait(WYSYLKA_CO)
		for gracz, s in pairs(stany) do
			stan(gracz) -- zmiana dnia
			if s.brudny then
				s.brudny = false
				Z:FireClient(gracz, "stan", widok(gracz, s))
			end
		end
	end
end)
