--[[
	SerwerStanu — JEDYNY właściciel stanu gracza między systemami (Script, RunContext = Server, w kontenerze
	Workspace/StanGracza; budowa: swiat/stan_gracza/zbuduj.py; status: propozycja, opis w README pakietu).

	Szyną danych dla HUD i okien Pawła zostają ATRYBUTY GRACZA (Level, XP, XPMax, Gold, Gems, Class, Strength… —
	ich kodu nie ruszamy; HUD i okno ekwipunku same słuchają zmian). Ten skrypt:
		1. łup z walki w lesie (Sygnaly/PrzyznajLup, woła SerwerPotworow obu lasów) → profil od razu, atrybuty po walce:
		   gdy klient zgłosi, że HUD znów widać ("pokaz"), albo najpóźniej po czasie walki + D.publikacja.zapas_s;
		   Gold i Gems czytamy i dopisujemy (odczyt-zapis), bo drzewko Pawła odejmuje Gems z tego samego atrybutu;
		2. awans: XP ≥ XPMax → Level + 1, nowe XPMax z krzywej (D.krzywa = tools/walka/tempo.py), komunikat "awans"
		   do klienta (baner „POZIOM N”);
		3. statystyki: po wyborze klasy i przy każdej zmianie Level sześć atrybutów dostaje rozkład klasy dla puli
		   poziomu (30 + 10 na poziom; rozkłady z ReplicatedStorage.Shared.ClassData Pawła, zapas: D.rozklady).
		   Pierwszy raz wpisuje cel + trening (zastępuje wartości testowe PlayerStatsDefaults), potem tylko różnicę —
		   to, co dopisał ktoś inny (darmowy „+” w oknie ekwipunku), zostaje. Atrybut kontenera StatystykiKlasy = false
		   wyłącza ten punkt (zostają wartości testowe Pawła, trening dalej dopisuje);
		4. trening: Workspace/TreningProba/Sygnaly/PrzyrostStatystyki → przyrost do atrybutu statystyki (i do profilu),
		   z ponownym podłączeniem, gdy kontener treningu zostanie przebudowany w czasie gry;
		5. bohater walki (Sygnaly/Bohater): klasa z Class, poziom z Level, sześć statystyk z atrybutów, broń, pancerz
		   z przedmiotów i sloty ze wzoru dla poziomu (LogikaStanu.opisBohatera = tools/walka/wzorcowe.postac).
	Stan: JEDNA tabela profilu na gracza (pole wersja) — pod przyszły zapis (DataStore / ProfileStore; dziś tylko
	pamięć serwera, profil znika przy wyjściu gracza, jak atrybuty).

	Uchwyty (tylko serwer, BindableFunction w Sygnaly; bez kontenera StanGracza inne pakiety działają jak dawniej):
		Bohater:Invoke(gracz) → opis postaci dla Silnik.symuluj albo nil
		PrzyznajLup:Invoke(gracz, { lup = walka.lup, wynik, czas = walka.czas, zrodlo = nazwa kontenera lasu,
		                            gatunek, poziom }) → { ok = true } | { ok = false, powod }
		SterowanieSerwera:Invoke("stan", gracz?) | ("zgodnosc") | ("publikuj", gracz?) | ("bohater", gracz?)
		                  | ("przyznaj", gracz, lup) — testy (przyznaj pokazuje łup od razu)
	Zdalne/ZdarzeniaStanu (RemoteEvent): serwer → klient "awans", poziom, ile; klient → serwer "pokaz" (bez liczb;
	najwyżej raz na D.publikacja.odstep_pokaz_s — może tylko przyspieszyć pokazanie łupu, nigdy go zmienić).
	Działa tylko w Roblox Studio: poza Studio usuwa cały kontener, jak pozostałe prototypy.
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DaneStanu"))
local L = require(moduly:WaitForChild("LogikaStanu"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaStanu")
local sygnaly = kontener:WaitForChild("Sygnaly")
local bohaterF: BindableFunction = sygnaly:WaitForChild("Bohater")
local lupF: BindableFunction = sygnaly:WaitForChild("PrzyznajLup")
local sterowanie: BindableFunction = sygnaly:WaitForChild("SterowanieSerwera")

local P = D.prefiks
local A = D.atrybuty
local ZRODLA = {}
for _, z in D.zrodla do
	ZRODLA[z] = true
end

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function dolicz(nazwa: string)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

kontener:SetAttribute("SerwerStanuGotowy", false)
for _, n in { "LicznikLupow", "LicznikPokazan", "LicznikAwansow", "LicznikBohaterow", "LicznikTreningu", "LicznikOdmow" } do
	kontener:SetAttribute(n, 0)
end

------------------------------------------------------------------ zgodność logiki (te same przypadki co w Pythonie)
local function zgodnosc(): string
	local ok, n, bledy = L.sprawdzPrzypadki(D)
	local tekst
	if ok then
		tekst = string.format("OK %d/%d", n, n)
	else
		tekst = string.format("BŁĄD %d/%d: %s", n - #bledy, n, tostring(bledy[1]))
		warn(P .. "zgodność logiki: " .. tostring(bledy[1]))
	end
	kontener:SetAttribute("ZgodnoscLogikiStanu", tekst)
	return tekst
end
zgodnosc()

------------------------------------------------------------------ rozkłady klas (ClassData Pawła — tylko odczyt)
local rozklady = {}
for _, k in D.klasy do
	rozklady[k] = D.rozklady[k]
end

local function wczytajRozklady(): string
	local folder = ReplicatedStorage:WaitForChild(D.klasy_pawla.folder, D.klasy_pawla.czekaj_s)
	local m = folder and folder:WaitForChild(D.klasy_pawla.modul, D.klasy_pawla.czekaj_s)
	if not m or not m:IsA("ModuleScript") then
		return "dane (brak ClassData)"
	end
	local ok, CD = pcall(require, m)
	if not ok or type(CD) ~= "table" or type(CD.Classes) ~= "table" then
		return "dane (ClassData nieczytelny: " .. tostring(CD) .. ")"
	end
	local n, rozne = 0, {}
	for _, c in CD.Classes do
		local klasa = type(c) == "table" and D.klasy_gracza[c.id]
		if klasa then
			local r, powod = L.rozkladZClassData(D, c.stats)
			if r then
				rozklady[klasa] = r
				n += 1
				if not L.rowne(r, D.rozklady[klasa]) then
					table.insert(rozne, klasa)
				end
			else
				warn(P .. "ClassData " .. tostring(c.id) .. ": " .. powod .. " — rozkład z danych")
			end
		end
	end
	if #rozne > 0 then
		warn(P .. "rozkłady z ClassData różne od wzorcowych (balans!): " .. table.concat(rozne, ", "))
		return "ClassData (" .. n .. " klas; INNE NIŻ WZORCOWE: " .. table.concat(rozne, ", ") .. ")"
	end
	return "ClassData (" .. n .. " klas)"
end
kontener:SetAttribute("RozkladyZ", wczytajRozklady())

------------------------------------------------------------------ profil i atrybuty
local profile: { [Player]: any } = {}

local function profil(gracz: Player)
	local p = profile[gracz]
	if not p then
		p = L.nowyProfil(D)
		p.oczekujace = {}
		profile[gracz] = p
	end
	return p
end

local function liczba(gracz: Player, nazwa: string, domyslna: number): number
	local v = gracz:GetAttribute(nazwa)
	if type(v) == "number" and v == v and v > -math.huge and v < math.huge then
		return v
	end
	return domyslna
end

local function klasaGracza(gracz: Player): string
	local klasa = L.klasaSilnika(D, gracz:GetAttribute(A.klasa))
	return klasa
end

local function poziomGracza(gracz: Player): number
	return L.poziomZ(D, gracz:GetAttribute(A.poziom))
end

local function statystykiWlaczone(): boolean
	return kontener:GetAttribute("StatystykiKlasy") ~= false
end

-- lustro atrybutów w profilu (pod przyszły zapis); atrybuty są prawdą, bo piszą je też skrypty Pawła
local function zbierz(gracz: Player)
	local p = profil(gracz)
	p.klasa = klasaGracza(gracz)
	p.poziom = poziomGracza(gracz)
	p.xp = liczba(gracz, A.xp, 0)
	p.zloto = liczba(gracz, A.zloto, 0)
	p.gemy = liczba(gracz, A.gemy, 0)
	p.shardy = liczba(gracz, A.shardy, 0)
	return p
end

-- sześć atrybutów: rozkład klasy dla puli poziomu (pierwszy raz cel + trening, potem różnica)
local function zastosujBaze(gracz: Player)
	if not statystykiWlaczone() or not gracz.Parent then
		return
	end
	local p = profil(gracz)
	local klasa = klasaGracza(gracz)
	local poziom = poziomGracza(gracz)
	if p.baza and p.baza.klasa == klasa and p.baza.poziom == poziom then
		return
	end
	local cel = L.rozdziel(D, rozklady[klasa], L.pula(D, poziom))
	local obecne = {}
	for _, s in D.statystyki do
		obecne[s] = gracz:GetAttribute(D.atrybuty_statystyk[s])
	end
	local nowe = L.noweStatystyki(D, obecne, if p.baza then p.baza.st else nil, cel, p.wytrenowane)
	p.baza = { klasa = klasa, poziom = poziom, st = cel }
	for _, s in D.statystyki do
		if gracz:GetAttribute(D.atrybuty_statystyk[s]) ~= nowe[s] then
			gracz:SetAttribute(D.atrybuty_statystyk[s], nowe[s])
		end
	end
end

local function ustawXpMax(gracz: Player)
	local cel = L.xpDoNastepnego(D, poziomGracza(gracz))
	if gracz:GetAttribute(A.xp_max) ~= cel then
		gracz:SetAttribute(A.xp_max, cel)
	end
end

local function dopisz(gracz: Player, nazwa: string, ile: number)
	if ile > 0 then
		gracz:SetAttribute(nazwa, math.min(liczba(gracz, nazwa, 0) + ile, D.limity.waluta_maks))
	end
end

------------------------------------------------------------------ łup: przyjęcie i pokazanie
-- pokazuje (atrybuty) łupy gotowe do pokazania: po czasie albo — wymus — wszystkie starsze niż minWiek
local function publikuj(gracz: Player, wymus: boolean, minWiek: number)
	local p = profile[gracz]
	if not p or not gracz.Parent or #p.oczekujace == 0 then
		return 0
	end
	local t = teraz()
	local gotowe, reszta = {}, {}
	for _, o in p.oczekujace do
		if t >= o.pokazOd or (wymus and t - o.przyjeto >= minWiek) then
			table.insert(gotowe, o.lup)
		else
			table.insert(reszta, o)
		end
	end
	if #gotowe == 0 then
		return 0
	end
	p.oczekujace = reszta
	local suma = L.sumaLupow(D, gotowe)
	dopisz(gracz, A.zloto, suma.zloto)
	dopisz(gracz, A.gemy, suma.gemy)
	dopisz(gracz, A.shardy, suma.shard_ewolucji)
	for kraina, n in suma.tokeny do
		dopisz(gracz, A.tokeny_prefiks .. kraina, n)
		p.tokeny[kraina] = (p.tokeny[kraina] or 0) + n
	end
	local poziom, xp, ile = L.awans(D, poziomGracza(gracz), liczba(gracz, A.xp, 0), suma.doswiadczenie)
	gracz:SetAttribute(A.xp, xp)
	if ile > 0 then
		gracz:SetAttribute(A.poziom, poziom)
	end
	ustawXpMax(gracz)
	zastosujBaze(gracz)
	zbierz(gracz)
	dolicz("LicznikPokazan")
	if ile > 0 then
		p.awanse += ile
		kontener:SetAttribute("LicznikAwansow", (kontener:GetAttribute("LicznikAwansow") or 0) + ile)
		zdarzenia:FireClient(gracz, "awans", poziom, ile)
	end
	kontener:SetAttribute("OstatniePokazanie", string.format("%s:+%dz:+%dxp:poz.%d", gracz.Name, suma.zloto,
		suma.doswiadczenie, poziom))
	return #gotowe
end

local function odmowaLupu(powod: string)
	dolicz("LicznikOdmow")
	kontener:SetAttribute("OstatniaOdmowa", powod)
	return { ok = false, powod = powod }
end

local function przyjmijLup(gracz: any, info: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or gracz.Parent ~= Players then
		return odmowaLupu("zly_gracz")
	end
	if type(info) ~= "table" or type(info.zrodlo) ~= "string" or not ZRODLA[info.zrodlo] then
		return odmowaLupu("zle_zrodlo")
	end
	local lup, powod = L.czystyLup(D, info.lup)
	if not lup then
		return odmowaLupu(powod)
	end
	local czas = info.czas
	if type(czas) ~= "number" or czas ~= czas or czas < 0 or czas > D.limity.czas_walki_maks then
		czas = 0
	end
	local p = profil(gracz)
	if #p.oczekujace >= D.limity.oczekujace_maks then
		publikuj(gracz, true, 0)
	end
	local t = teraz()
	table.insert(p.oczekujace, { lup = lup, przyjeto = t, pokazOd = t + czas + D.publikacja.zapas_s })
	if info.wynik == "wygrana" then
		p.walki.wygrane += 1
	else
		p.walki.przegrane += 1
	end
	dolicz("LicznikLupow")
	kontener:SetAttribute("OstatniLup", string.format("%s:%s:%s:%dz:%dxp", gracz.Name, info.zrodlo, tostring(info.wynik),
		lup.zloto, lup.doswiadczenie))
	task.delay(czas + D.publikacja.zapas_s + 0.1, function()
		publikuj(gracz, false, 0)
	end)
	return { ok = true }
end

lupF.OnInvoke = function(gracz: any, info: any)
	local ok, wynik = pcall(przyjmijLup, gracz, info)
	if ok then
		return wynik
	end
	warn(P .. "PrzyznajLup: " .. tostring(wynik))
	return { ok = false, powod = "blad" }
end

------------------------------------------------------------------ bohater walki
local function bohater(gracz: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or gracz.Parent ~= Players then
		return nil
	end
	-- łup poprzedniej walki przed następną (gracz zaczyna walkę, gdy ekran wyniku już zniknął)
	publikuj(gracz, true, D.publikacja.min_s)
	local p = profil(gracz)
	if not p.baza then
		zastosujBaze(gracz)
	end
	local klasa = klasaGracza(gracz)
	local poziom = poziomGracza(gracz)
	local zapas = L.rozdziel(D, rozklady[klasa], L.pula(D, poziom))
	local st = {}
	for _, s in D.statystyki do
		st[s] = L.statystykaZ(D, gracz:GetAttribute(D.atrybuty_statystyk[s])) or (zapas[s] + p.wytrenowane[s])
	end
	dolicz("LicznikBohaterow")
	kontener:SetAttribute("OstatniBohater", string.format("%s:%s:%d", gracz.Name, klasa, poziom))
	return L.opisBohatera(D, klasa, poziom, st)
end

bohaterF.OnInvoke = function(gracz: any)
	local ok, wynik = pcall(bohater, gracz)
	if ok then
		return wynik
	end
	warn(P .. "Bohater: " .. tostring(wynik))
	return nil
end

------------------------------------------------------------------ trening (Workspace/TreningProba — tylko słuchamy)
local function przyrostTreningu(gracz: any, info: any)
	if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") or gracz.Parent ~= Players then
		return
	end
	local w = L.czystyPrzyrost(D, info)
	if not w then
		return
	end
	local s, n = w[1], w[2]
	local p = profil(gracz)
	p.wytrenowane[s] += n
	local nazwa = D.atrybuty_statystyk[s]
	local obecna = L.statystykaZ(D, gracz:GetAttribute(nazwa))
	if obecna ~= nil then
		gracz:SetAttribute(nazwa, L.statystykaZ(D, obecna + n))
	elseif statystykiWlaczone() then
		p.baza = nil
		zastosujBaze(gracz)
	end
	dolicz("LicznikTreningu")
end

local polaczenieTreningu: RBXScriptConnection? = nil
local function podlaczTrening(k: Instance)
	if k.Name ~= D.trening.kontener then
		return
	end
	task.spawn(function()
		local s = k:WaitForChild("Sygnaly", 15)
		local e = s and s:WaitForChild(D.trening.sygnal, 15)
		if not e or not e:IsA("BindableEvent") or not k.Parent then
			return
		end
		if polaczenieTreningu then
			polaczenieTreningu:Disconnect()
		end
		polaczenieTreningu = e.Event:Connect(function(gracz: any, info: any)
			local ok, blad = pcall(przyrostTreningu, gracz, info)
			if not ok then
				warn(P .. "przyrost treningu: " .. tostring(blad))
			end
		end)
		kontener:SetAttribute("TreningPodlaczony", true)
		k.Destroying:Connect(function()
			kontener:SetAttribute("TreningPodlaczony", false)
		end)
	end)
end
kontener:SetAttribute("TreningPodlaczony", false)
for _, k in workspace:GetChildren() do
	podlaczTrening(k)
end
workspace.ChildAdded:Connect(podlaczTrening)

------------------------------------------------------------------ klient: "pokaz" (HUD znów widać — koniec ekranu walki)
local ostatniePokaz: { [Player]: number } = {}
zdarzenia.OnServerEvent:Connect(function(gracz: Player, polecenie: any)
	if polecenie ~= "pokaz" then
		return
	end
	local t = os.clock()
	if ostatniePokaz[gracz] and t - ostatniePokaz[gracz] < D.publikacja.odstep_pokaz_s then
		return
	end
	ostatniePokaz[gracz] = t
	publikuj(gracz, true, D.publikacja.min_s)
end)

------------------------------------------------------------------ gracze
local function nowyGracz(gracz: Player)
	profil(gracz)
	gracz:GetAttributeChangedSignal(A.poziom):Connect(function()
		ustawXpMax(gracz)
		zastosujBaze(gracz)
	end)
	gracz:GetAttributeChangedSignal(A.klasa):Connect(function()
		zastosujBaze(gracz)
	end)
	ustawXpMax(gracz)
	zastosujBaze(gracz)
	zbierz(gracz)
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	task.spawn(nowyGracz, g)
end
Players.PlayerRemoving:Connect(function(gracz: Player)
	profile[gracz] = nil
	ostatniePokaz[gracz] = nil
end)

-- włączenie StatystykiKlasy w czasie gry: rozkład klasy od razu (wyłączenie zostawia atrybuty, jakie są)
kontener:GetAttributeChangedSignal("StatystykiKlasy"):Connect(function()
	for _, g in Players:GetPlayers() do
		zastosujBaze(g)
	end
end)

------------------------------------------------------------------ haczyk testowy
local function ktory(g: any): Player?
	if typeof(g) == "Instance" and g:IsA("Player") then
		return g
	end
	return Players:GetPlayers()[1]
end

local function kopia(t: any): any
	if type(t) ~= "table" then
		return t
	end
	local w = {}
	for k, v in t do
		w[k] = kopia(v)
	end
	return w
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "zgodnosc" then
		return zgodnosc()
	end
	local g = ktory(a)
	if not g then
		return nil
	end
	if polecenie == "stan" then
		local p = kopia(zbierz(g))
		local atrybuty = {}
		for _, s in D.statystyki do
			atrybuty[D.atrybuty_statystyk[s]] = g:GetAttribute(D.atrybuty_statystyk[s])
		end
		for _, n in { A.klasa, A.poziom, A.xp, A.xp_max, A.zloto, A.gemy, A.shardy } do
			atrybuty[n] = g:GetAttribute(n)
		end
		p.atrybuty = atrybuty
		p.oczekujace = #p.oczekujace
		p.rozklady = kontener:GetAttribute("RozkladyZ")
		p.statystykiKlasy = statystykiWlaczone()
		return p
	elseif polecenie == "publikuj" then
		return publikuj(g, true, 0)
	elseif polecenie == "bohater" then
		return bohater(g)
	elseif polecenie == "przyznaj" then
		local w = przyjmijLup(g, { lup = b, wynik = "wygrana", czas = 0, zrodlo = D.zrodla[1] })
		if w.ok then
			publikuj(g, true, 0)
		end
		return w
	end
	warn(P .. "SterowanieSerwera: nieznane polecenie " .. tostring(polecenie))
	return nil
end

kontener:SetAttribute("SerwerStanuGotowy", true)
print(string.format("%sgotowy: logika %s, rozkłady %s, statystyki klasy %s", P,
	tostring(kontener:GetAttribute("ZgodnoscLogikiStanu")), tostring(kontener:GetAttribute("RozkladyZ")),
	if statystykiWlaczone() then "włączone" else "wyłączone (wartości testowe Pawła)"))
