--!strict
--[[
	OknoPetow (serwer) — dane i polecenia dla okna petów w HUD (Paweł 25.11, src/client/OknoPetowClient.client.luau).

	Pety i ich premie liczy serwer petów Karola (Workspace/PetyProba). Tutaj tylko wołamy jego haczyk
	Sygnaly/SterowanieSerwera ("stan", "wybierz" z pominięciem zasięgu zagrody) i czytamy jego dane (Moduly/DanePetow,
	Moduly/LogikaPetow) — bez zmian w jego plikach.

	Czego jego stan dziś nie umie (pytanie do Karola w sejfie):
	  - ma JEDNEGO aktywnego peta: slot 1 okna = jego aktywny pet (premia działa); slot 2 trzymamy tylko tutaj,
	    w pamięci serwera (pokazuje się w oknie, premii nie daje i znika po wyjściu z gry);
	  - nie ma „odstaw” poza zagrodą ani usuwania petów: zdjęcie peta ze slotu 1 działa tylko wtedy, gdy w slocie 2
	    jest inny (zamiana), a DELETE odpowiada „jeszcze nie”.

	Zdalne: ReplicatedStorage.OknoPetow (RemoteFunction)
	  "stan"                → { ok, pety = { { pet, nazwa, rzadkosc, rzadkoscNazwa, kolor, kopie, skill, krotko } },
	                           zalozone = { pet1?, pet2? }, sloty = 2, wszystkich = 4, razem = liczba kopii }
	  "zaloz", pet          → jak "stan" (+ tekst przy odmowie)
	  "zdejmij", slot       → jak "stan"
	  "najlepsze"           → jak "stan"
	  "zdejmij_wszystkie"   → jak "stan"
	  "usun", pet           → odmowa z tekstem
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local SLOTY, WSZYSTKICH = 2, 4
local LIMIT = 0.25 -- najmniejszy odstęp poleceń jednego gracza (s)
local KOLEJNOSC = { pospolity = 1, zwykly = 2, rzadki = 3, epicki = 4, legendarny = 5 }

local F = RS:FindFirstChild("OknoPetow") :: RemoteFunction?
if not F then
	local f = Instance.new("RemoteFunction")
	f.Name = "OknoPetow"
	f.Parent = RS
	F = f
end

local drugi: { [Player]: string } = {} -- slot 2 (tylko tutaj)
local ostatnie: { [Player]: number } = {}

local function karol(): (any, any, BindableFunction?)
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local d = mod and mod:FindFirstChild("DanePetow")
	local l = mod and mod:FindFirstChild("LogikaPetow")
	local s = k and k:FindFirstChild("Sygnaly")
	local h = s and s:FindFirstChild("SterowanieSerwera")
	if not (d and d:IsA("ModuleScript") and l and l:IsA("ModuleScript") and h and h:IsA("BindableFunction")) then
		return nil, nil, nil
	end
	local ok, D, L = pcall(function()
		return require(d), require(l)
	end)
	if not ok or type(D) ~= "table" or type(L) ~= "table" or D.pety == nil then
		return nil, nil, nil
	end
	return D, L, h
end

local function stan(gracz: Player, tekst: string?): any
	local D, L, h = karol()
	if not (D and L and h) then
		return { ok = false, tekst = "Pets are not available (pet server missing)" }
	end
	local okS, w = pcall(function()
		return h:Invoke("stan", gracz)
	end)
	local st = if okS and type(w) == "table" then w.pety else nil
	if type(st) ~= "table" or not st.ok then
		return { ok = false, tekst = "Pets are not available (player state missing)" }
	end
	local wiersze = L.wierszeZagrody(D, st.kopie, st.aktywny)
	local pety, razem, mam = {}, 0, {}
	for _, r in ipairs(wiersze) do
		local p = L.pet(D, r.pet)
		table.insert(pety, { pet = r.pet, nazwa = r.nazwa, rzadkosc = p and p.rzadkosc or "", rzadkoscNazwa = r.rzadkosc,
			kolor = r.kolor, kopie = r.kopie, skill = r.skill, krotko = r.krotko })
		razem += r.kopie
		mam[r.pet] = true
	end
	table.sort(pety, function(a, b)
		local ka, kb = KOLEJNOSC[a.rzadkosc] or 0, KOLEJNOSC[b.rzadkosc] or 0
		if ka ~= kb then
			return ka > kb
		end
		return a.nazwa < b.nazwa
	end)
	local pierwszy = if type(st.aktywny) == "string" and mam[st.aktywny] then st.aktywny else nil
	local d2 = drugi[gracz]
	if d2 and (not mam[d2] or d2 == pierwszy or not pierwszy) then
		drugi[gracz] = nil
		d2 = nil
	end
	return { ok = true, pety = pety, zalozone = { pierwszy :: any, d2 :: any }, pierwszy = pierwszy, drugi = d2, sloty = SLOTY,
		wszystkich = WSZYSTKICH, razem = razem, tekst = tekst }
end

local function wybierz(gracz: Player, pet: string): (boolean, string?)
	local _, _, h = karol()
	if not h then
		return false, "Pets are not available"
	end
	local ok, w = pcall(function()
		return h:Invoke("wybierz", gracz, pet, true)
	end)
	if ok and type(w) == "table" and w.ok then
		return true, nil
	end
	return false, "You don't have this pet"
end

local function zaloz(gracz: Player, pet: any): any
	if type(pet) ~= "string" or #pet > 40 then
		return stan(gracz, "Unknown pet")
	end
	local s = stan(gracz)
	if not s.ok then
		return s
	end
	local mam = false
	for _, p in ipairs(s.pety) do
		mam = mam or p.pet == pet
	end
	if not mam then
		return stan(gracz, "You don't have this pet")
	end
	if s.pierwszy == pet or s.drugi == pet then
		return s
	end
	if not s.pierwszy then
		local ok, t = wybierz(gracz, pet)
		return stan(gracz, if ok then nil else t)
	end
	-- slot 1 zajęty: nowy pet idzie do slotu 2 (gdy i on zajęty — zastępuje go)
	drugi[gracz] = pet
	return stan(gracz)
end

local function zdejmij(gracz: Player, slot: any): any
	local s = stan(gracz)
	if not s.ok then
		return s
	end
	if slot == 2 then
		drugi[gracz] = nil
		return stan(gracz)
	end
	if slot == 1 and s.pierwszy then
		if s.drugi then
			local d2 = s.drugi
			drugi[gracz] = nil
			local ok, t = wybierz(gracz, d2)
			return stan(gracz, if ok then nil else t)
		end
		return stan(gracz, "Put the pet away at the Pet Pen")
	end
	return s
end

local function najlepsze(gracz: Player): any
	local s = stan(gracz)
	if not s.ok or #s.pety == 0 then
		return s
	end
	-- lista jest już ułożona od najrzadszych
	local a, b = s.pety[1], s.pety[2]
	if s.pierwszy ~= a.pet then
		local ok, t = wybierz(gracz, a.pet)
		if not ok then
			return stan(gracz, t)
		end
	end
	drugi[gracz] = if b then b.pet else nil
	return stan(gracz)
end

(F :: RemoteFunction).OnServerInvoke = function(gracz: Player, polecenie: any, a: any): any
	if type(polecenie) ~= "string" then
		return { ok = false }
	end
	local t = os.clock()
	if polecenie ~= "stan" and ostatnie[gracz] and t - ostatnie[gracz] < LIMIT then
		return stan(gracz)
	end
	ostatnie[gracz] = t
	if polecenie == "stan" then
		return stan(gracz)
	elseif polecenie == "zaloz" then
		return zaloz(gracz, a)
	elseif polecenie == "zdejmij" then
		return zdejmij(gracz, a)
	elseif polecenie == "najlepsze" then
		return najlepsze(gracz)
	elseif polecenie == "zdejmij_wszystkie" then
		drugi[gracz] = nil
		local s = stan(gracz)
		if s.ok and s.pierwszy then
			s.tekst = "Slot 1 pet stays until you visit the Pet Pen"
		end
		return s
	elseif polecenie == "usun" then
		return stan(gracz, "Deleting pets is coming soon")
	end
	return { ok = false }
end

Players.PlayerRemoving:Connect(function(gracz)
	drugi[gracz] = nil
	ostatnie[gracz] = nil
end)
