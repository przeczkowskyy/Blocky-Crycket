--!strict
--[[
	Indeks (serwer) — dane okna Index (Paweł 26.11, src/client/OknoIndeksuClient.client.luau).

	Pety: wszystkie gatunki z danych Karola (Workspace/PetyProba/Moduly/DanePetow) pogrupowane według krain — kraina
	peta to kraina jego jajka (DanePetow.jajka[].kraina). Czy gracz ma danego peta, mówi stan serwera petów Karola
	(Sygnaly/SterowanieSerwera "stan"). Bez zmian w plikach Karola. Moduły Karola działają tylko w Studio — poza nim
	zakładka petów mówi, że pety nie są dostępne.
	Przedmioty: lista jest w ReplicatedStorage.Shared.IndeksPrzedmioty (klient filtruje według klasy gracza).

	Zdalne: ReplicatedStorage.OknoIndeksu (RemoteFunction)
	  "pety" → { ok, krainy = { { id, nazwa, pety = { { id, nazwa, rzadkosc, rzadkoscNazwa, kolor, skill, mam } } } },
	             mam = liczba gatunków gracza, wszystkich = liczba gatunków } | { ok = false, tekst }
]]
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")

local KRAINY = { { id = "las", nazwa = "FOREST" }, { id = "bagno", nazwa = "SWAMP" }, { id = "dzungla", nazwa = "JUNGLE" } }
local KOLEJNOSC = { pospolity = 1, zwykly = 2, rzadki = 3, epicki = 4, legendarny = 5 }
local NAZWY_RZADKOSCI = { pospolity = "Common", zwykly = "Uncommon", rzadki = "Rare", epicki = "Epic", legendarny = "Legendary" }
local LIMIT = 0.5

local F = RS:FindFirstChild("OknoIndeksu") :: RemoteFunction?
if not F then
	local f = Instance.new("RemoteFunction")
	f.Name = "OknoIndeksu"
	f.Parent = RS
	F = f
end

local ostatnie: { [Player]: number } = {}

local function karol(): (any, any, BindableFunction?)
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local d = mod and mod:FindFirstChild("DanePetow")
	local l = mod and mod:FindFirstChild("LogikaPetow")
	local s = k and k:FindFirstChild("Sygnaly")
	local h = s and s:FindFirstChild("SterowanieSerwera")
	if not (d and d:IsA("ModuleScript") and l and l:IsA("ModuleScript")) then
		return nil, nil, nil
	end
	local ok, D, L = pcall(function()
		return require(d), require(l)
	end)
	if not ok or type(D) ~= "table" or type(L) ~= "table" or D.pety == nil then
		return nil, nil, nil
	end
	return D, L, if h and h:IsA("BindableFunction") then h else nil
end

local function pety(gracz: Player): any
	local D, L, h = karol()
	if not (D and L) then
		return { ok = false, tekst = "Pets are not available yet" }
	end
	local mam: { [string]: boolean } = {}
	if h then
		local okS, w = pcall(function()
			return h:Invoke("stan", gracz)
		end)
		local st = if okS and type(w) == "table" then w.pety else nil
		if type(st) == "table" and type(st.kopie) == "table" then
			for pet, n in pairs(st.kopie) do
				if type(n) == "number" and n > 0 then
					mam[pet] = true
				end
			end
		end
	end
	local krainaJajka: { [string]: string } = {}
	for _, j in ipairs(D.jajka or {}) do
		krainaJajka[j.id] = j.kraina
	end
	local kolory: { [string]: string } = {}
	for _, r in ipairs(D.rzadkosci or {}) do
		kolory[r.id] = r.kolor
	end
	local wynik, ile, moje = {}, 0, 0
	for _, k in ipairs(KRAINY) do
		local lista = {}
		for _, p in ipairs(D.pety) do
			if krainaJajka[p.jajko] == k.id then
				local okO, opis = pcall(function()
					return L.opisSkillaKrotki(D, p)
				end)
				table.insert(lista, { id = p.id, nazwa = p.nazwa, rzadkosc = p.rzadkosc,
					rzadkoscNazwa = NAZWY_RZADKOSCI[p.rzadkosc] or p.rzadkosc, kolor = kolory[p.rzadkosc] or "B8C2CC",
					skill = if okO and type(opis) == "string" then opis else (p.skill and p.skill.nazwa or ""),
					mam = mam[p.id] == true })
				ile += 1
				if mam[p.id] then
					moje += 1
				end
			end
		end
		table.sort(lista, function(a, b)
			local ka, kb = KOLEJNOSC[a.rzadkosc] or 0, KOLEJNOSC[b.rzadkosc] or 0
			if ka ~= kb then
				return ka < kb
			end
			return a.nazwa < b.nazwa
		end)
		if #lista > 0 then
			table.insert(wynik, { id = k.id, nazwa = k.nazwa, pety = lista })
		end
	end
	return { ok = true, krainy = wynik, mam = moje, wszystkich = ile }
end

(F :: RemoteFunction).OnServerInvoke = function(gracz: Player, polecenie: any): any
	local t = os.clock()
	if t - (ostatnie[gracz] or 0) < LIMIT then
		return { ok = false, tekst = "Slow down" }
	end
	ostatnie[gracz] = t
	if polecenie == "pety" then
		return pety(gracz)
	end
	return { ok = false, tekst = "Unknown command" }
end

Players.PlayerRemoving:Connect(function(g)
	ostatnie[g] = nil
end)
