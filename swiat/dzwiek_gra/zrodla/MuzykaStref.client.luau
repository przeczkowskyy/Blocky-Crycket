--[[
	MuzykaStref — muzyka stref gry (Script, RunContext = Client, w kontenerze Workspace/DzwiekGra; pakiet swiat/dzwiek_gra).

	Co robi (tylko u tego klienta, nic nie wysyła do serwera):
		• co 0,5 s sprawdza, w której strefie stoi postać: prostokąty stref z Moduly/KatalogDzwiekow (policzone przy
		  budowie z gruntu map: bazar = Workspace/MiasteczkoBazar, las = Workspace/LasPas); strefa liczy się tylko wtedy,
		  gdy jej mapa stoi w Workspace (cudzych kontenerów nie zmieniamy — tylko FindFirstChild);
		• gra utwory strefy na zmianę (bazar: trzy, las: dwa), każdy raz do końca, potem płynne przejście w następny;
		  zmiana strefy albo wyjście ze stref = płynne przejście (katalog: muzyka.przejscie s);
		• na czas walki (odtwarzacz prototypu TestWalki2: czyTrwa) przycisza muzykę do muzyka.przyciszenieWalki;
		• utwór bez identyfikatora (0 = jeszcze nie wgrany) jest pomijany; strefa bez żadnego utworu z identyfikatorem
		  = cisza, bez komunikatów w konsoli. Menu główne (ekran Pawła) NIE jest tu podpięte — tylko pozycja w katalogu.
	Uchwyt testowy: Sygnaly/SterowanieMuzyki (BindableFunction):
		Invoke("stan") → { strefa, utwor, id, glosnosc, walka, gotowy, bledy, zmiany }
		Invoke("wymus", strefa | nil) → wymuszona strefa (nil = wg pozycji); Invoke("probny", strefa, id | contentId)
		→ na czas sesji Play podstawia identyfikator pierwszego utworu strefy (próba bez wgranych plików).
	Lokalne atrybuty kontenera: MuzykaStrefa, MuzykaUtwor, MuzykaGotowa, MuzykaBledy.
]]
if not game:GetService("RunService"):IsStudio() then
	return -- pakiet działa wyłącznie w Studio (jak reszta prototypu)
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local kontener = script.Parent
local gracz = Players.LocalPlayer
local P = "[DzwiekGra] "

local K = nil
do
	local m = kontener:WaitForChild("Moduly"):WaitForChild("KatalogDzwiekow", 10)
	local ok, w = false, nil
	if m then
		ok, w = pcall(require, m)
	end
	if ok and type(w) == "table" and type(w.muzyka) == "table" then
		K = w
	else
		warn(P .. "brak modułu KatalogDzwiekow — muzyka stref wyłączona (" .. tostring(w) .. ")")
		return
	end
end
local M = K.muzyka

local bledy = 0
local function zglosBlad(gdzie: string, blad: any)
	bledy += 1
	pcall(function()
		kontener:SetAttribute("MuzykaBledy", bledy)
	end)
	warn(P .. "błąd muzyki (" .. gdzie .. "): " .. tostring(blad))
end

------------------------------------------------------------------ czy trwa walka (odtwarzacz prototypu, tylko odczyt)
local Odtwarzacz: any = nil
task.spawn(function()
	local proto = workspace:WaitForChild("TestWalki2", 30)
	local m = proto and proto:WaitForChild("Moduly", 10)
	local o = m and m:WaitForChild("OdtwarzaczWalki2", 10)
	if o then
		local ok, w = pcall(require, o)
		if ok and type(w) == "table" and type(w.czyTrwa) == "function" then
			Odtwarzacz = w
		end
	end
end)
local function walkaTrwa(): boolean
	return Odtwarzacz ~= nil and Odtwarzacz.czyTrwa() == true
end

------------------------------------------------------------------ strefy
local probne: { [string]: any } = {} -- strefa → identyfikator próbny (haczyk "probny"), tylko na czas sesji
local wymuszona: string? = nil

local function contentId(id: any): string?
	if type(id) == "number" and id > 0 then
		return "rbxassetid://" .. tostring(math.floor(id))
	elseif type(id) == "string" and id ~= "" then
		return id -- tylko próby: pełny adres, np. rbxasset://sounds/… (dźwięk wbudowany w klienta)
	end
	return nil
end

-- lista grywalnych utworów strefy: { { nazwa, adres } } (pusta = cisza)
local function utworyStrefy(nazwa: string): { { any } }
	local s = M.strefy[nazwa]
	local lista = {}
	if not s or s.podpiete == false then
		return lista
	end
	for i, u in s.utwory do
		local adres = contentId(if i == 1 and probne[nazwa] ~= nil then probne[nazwa] else u.id)
		if adres then
			table.insert(lista, { u.nazwa, adres })
		end
	end
	return lista
end

local function strefaTeraz(): string?
	if wymuszona then
		return wymuszona
	end
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	if not hrp or not hrp:IsA("BasePart") then
		return nil
	end
	local p = hrp.Position
	for nazwa, s in M.strefy do
		if s.podpiete ~= false and type(s.prostokaty) == "table" and #s.prostokaty > 0
			and (not s.kontener or workspace:FindFirstChild(s.kontener) ~= nil) then
			for _, r in s.prostokaty do
				if p.X >= r[1] and p.X <= r[2] and p.Z >= r[3] and p.Z <= r[4] then
					return nazwa
				end
			end
		end
	end
	return nil
end

------------------------------------------------------------------ odtwarzanie (dwa tory na zmianę, przenikanie)
local folder = Instance.new("Folder")
folder.Name = "MuzykaLokalna" -- tylko u tego klienta; Sound w folderze (nie w części) gra bez położenia
folder.Parent = kontener

local tory = {}
for i = 1, 2 do
	local s = Instance.new("Sound")
	s.Name = "Tor" .. i
	s.Volume = 0
	s.Looped = false
	s.Parent = folder
	tory[i] = { dzwiek = s, waga = 0, cel = 0, glosnosc = 0, nazwa = nil, strefa = nil }
end
local biezacy = 0 -- indeks toru, który gra „na głos” (0 = żaden)
local nrUtworu: { [string]: number } = {}
local zmiany = 0
local przyciszenie = 1

local function graj(strefa: string)
	local lista = utworyStrefy(strefa)
	if #lista == 0 then
		return false
	end
	local n = ((nrUtworu[strefa] or 0) % #lista) + 1
	nrUtworu[strefa] = n
	local nastepny = if biezacy == 1 then 2 else 1
	local t = tory[nastepny]
	local u = lista[n]
	t.dzwiek:Stop()
	t.dzwiek.SoundId = u[2]
	t.dzwiek.TimePosition = 0
	t.nazwa, t.strefa = u[1], strefa
	t.glosnosc = M.strefy[strefa].glosnosc or 0.35
	t.waga, t.cel = 0, 1
	t.dzwiek.Volume = 0
	t.dzwiek:Play()
	if biezacy ~= 0 then
		tory[biezacy].cel = 0
	end
	biezacy = nastepny
	zmiany += 1
	kontener:SetAttribute("MuzykaUtwor", u[1])
	return true
end

local function wycisz()
	if biezacy ~= 0 then
		tory[biezacy].cel = 0
		biezacy = 0
		kontener:SetAttribute("MuzykaUtwor", nil)
	end
end

local strefa: string? = nil
local przelicz = false -- haczyk „probny” / „wymus”: przelicz strefę i utwór od nowa (także gdy strefa się nie zmienia)
local function sprawdzStrefe()
	local nowa = strefaTeraz()
	if nowa ~= strefa or przelicz then
		przelicz = false
		strefa = nowa
		kontener:SetAttribute("MuzykaStrefa", nowa)
		if not nowa or not graj(nowa) then
			wycisz()
		end
		return
	end
	-- utwór dobiega końca: następny utwór strefy (na zmianę); jedyny utwór — od początku
	if nowa and biezacy ~= 0 then
		local t = tory[biezacy]
		local dl = t.dzwiek.TimeLength
		if t.dzwiek.IsLoaded and dl > 0 and t.dzwiek.TimePosition >= dl - (M.przejscie or 2.5) then
			graj(nowa)
		end
	elseif nowa and biezacy == 0 then
		graj(nowa) -- np. identyfikator próbny podany po wejściu do strefy
	end
end

RunService.Heartbeat:Connect(function(dt: number)
	local ok, blad = pcall(function()
		local celP = if walkaTrwa() then (M.przyciszenieWalki or 0.25) else 1
		local szybkoP = dt / math.max(M.przyciszenieCzas or 0.8, 0.05)
		przyciszenie += math.clamp(celP - przyciszenie, -szybkoP, szybkoP)
		local szybko = dt / math.max(M.przejscie or 2.5, 0.05)
		for _, t in tory do
			if t.waga ~= t.cel then
				t.waga += math.clamp(t.cel - t.waga, -szybko, szybko)
			end
			local v = t.glosnosc * t.waga * przyciszenie
			if math.abs(t.dzwiek.Volume - v) > 1e-3 then
				t.dzwiek.Volume = v
			end
			if t.cel == 0 and t.waga <= 0 and t.dzwiek.IsPlaying then
				t.dzwiek:Stop()
			end
		end
	end)
	if not ok then
		zglosBlad("klatka", blad)
	end
end)

task.spawn(function()
	while kontener.Parent do
		local ok, blad = pcall(sprawdzStrefe)
		if not ok then
			zglosBlad("strefa", blad)
		end
		task.wait(0.5)
	end
end)

------------------------------------------------------------------ haczyk testowy
local h = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieMuzyki", 5)
if h and h:IsA("BindableFunction") then
	h.OnInvoke = function(polecenie: string, a: any, b: any)
		if polecenie == "stan" then
			local t = if biezacy ~= 0 then tory[biezacy] else nil
			return {
				strefa = strefa, utwor = t and t.nazwa, id = t and t.dzwiek.SoundId, glosnosc = t and t.dzwiek.Volume,
				gra = t ~= nil and t.dzwiek.IsPlaying, przyciszenie = przyciszenie, walka = walkaTrwa(), gotowy = true,
				bledy = bledy, zmiany = zmiany,
			}
		elseif polecenie == "wymus" then
			wymuszona = if type(a) == "string" and M.strefy[a] then a else nil
			przelicz = true
			return wymuszona
		elseif polecenie == "probny" then
			if type(a) ~= "string" or not M.strefy[a] then
				return false
			end
			probne[a] = b
			przelicz = true
			return true
		end
		return nil
	end
end
kontener:SetAttribute("MuzykaGotowa", true)
