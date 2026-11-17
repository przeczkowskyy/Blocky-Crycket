--[[
	SerwerPetow — jajka i pety na próbę (Script, RunContext = Server, w kontenerze Workspace/PetyProba; budowa:
	swiat/pety_proba/zbuduj.py; status: propozycja, opis w swiat/pety_proba/PROJEKT.md).

	Decyduje WYŁĄCZNIE serwer (klient nie losuje i nie podaje ceny):
		1. E przy inkubatorze każdego jajka (D.jajka: las-pas, Bagno; ProximityPrompt Punkty/<jajko.punkt_e>/Podpowiedz)
		   → kup(gracz, jajko): blokada na czas wyklucia (D.wyklucie.blokada_s) USTAWIONA PRZED wywołaniem stanu
		   gracza — drugi E w tym czasie (przy którymkolwiek inkubatorze) dostaje odmowę „trwa wyklucie”;
		   cena = LogikaPetow.cena(…) — od 17.11 stała dla każdego jajka (decyzja Karola; licznik kupionych z profilu
		   liczy się tylko w trybie „rosnaca”, osobny albo wspólny — D.licznik_ceny);
		   pet = LogikaPetow.losuj(Random:NextNumber()) z jawnych szans; Złoto i pet — JEDNYM wywołaniem
		   Workspace/StanGracza/Sygnaly/Pety("kup") (właściciel stanu gracza: wydatek + kopia peta bez przerwy);
		   za mało Złota → odmowa z kwotą, której brakuje; potem "wyklucie" do klienta (animację gra klient).
		2. Zdalne/ZdarzeniaPetow od klienta: "lista" (pety gracza do zagrody), "wybierz", id (aktywny pet — tylko
		   posiadany i tylko przy zagrodzie), "odstaw", "czekaj", tak/nie (pet znika na czas walki, przelotu, chmur
		   i mini-gry — atrybut gracza widzą inni klienci). Każde zdarzenie najwyżej co D.limity.odstep_zdarzen_s.
		3. Zapasowe E przy tablicy zagrody (Zagroda/"E wybor") — włączone tylko, gdy nie ma Workspace/MiasteczkoBazarGra
		   (wtedy E opiekunki nie istnieje); otwiera okno wyboru u klienta.
	Stan petów żyje w profilu StanGracza (jeden właściciel, pod przyszły zapis). Bez StanGracza: inkubator odmawia
	z komunikatem, zagroda pokazuje „brak”, żadnych błędów. Atrybuty gracza tego pakietu: dla każdego jajka
	jajko.atrybuty.cena (cena następnego jajka — napis przy E i wskazówki celu) i jajko.atrybuty.kupione (ile takich
	jajek gracz kupił — wskazówka „stać cię na pierwsze jajko biomu”), oraz D.atrybuty_gracza.czeka.
	Haczyk testowy: Sygnaly/SterowanieSerwera ("kup", gracz?, jajko, r?) | ("zwolnij", gracz?) | ("stan", gracz?)
	| ("wybierz", gracz?, pet, bezZasiegu?) | ("zgodnosc").
	Działa tylko w Roblox Studio: poza Studio usuwa cały kontener, jak pozostałe prototypy.
]]
if not game:GetService("RunService"):IsStudio() then
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local D = require(moduly:WaitForChild("DanePetow"))
local L = require(moduly:WaitForChild("LogikaPetow"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaPetow")
local sterowanie: BindableFunction = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera")

local P = D.prefiks
local S = D.stan_gracza
local AG = D.atrybuty_gracza
local los = Random.new()

local function dolicz(nazwa: string)
	kontener:SetAttribute(nazwa, (kontener:GetAttribute(nazwa) or 0) + 1)
end

kontener:SetAttribute("SerwerPetowGotowy", false)
for _, n in { "LicznikZakupow", "LicznikOdmow", "LicznikWyborow" } do
	kontener:SetAttribute(n, 0)
end

local function zgodnosc(): string
	local ok, n, bledy = L.sprawdzPrzypadki(D)
	local tekst
	if ok then
		tekst = string.format("OK %d/%d", n, n)
	else
		tekst = string.format("BŁĄD %d/%d: %s", n - #bledy, n, tostring(bledy[1]))
		warn(P .. "zgodność logiki: " .. tostring(bledy[1]))
	end
	kontener:SetAttribute("ZgodnoscLogikiPetow", tekst)
	return tekst
end
zgodnosc()

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function graczOk(gracz: any): boolean
	return typeof(gracz) == "Instance" and gracz:IsA("Player") and gracz.Parent == Players
end

------------------------------------------------------------------ stan gracza (Workspace/StanGracza — tylko przez sygnał)
local function sygnalPetow(): BindableFunction?
	local k = workspace:FindFirstChild(S.kontener)
	if not k or k:GetAttribute("Wygenerowane") ~= true or k:GetAttribute(S.gotowy) ~= true then
		return nil
	end
	local s = k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(S.sygnal_petow)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

local function wolajPety(polecenie: string, gracz: Player, info: any)
	local f = sygnalPetow()
	if not f then
		return nil
	end
	local ok, w = pcall(function()
		return f:Invoke(polecenie, gracz, info)
	end)
	if ok and type(w) == "table" then
		return w
	end
	if not ok then
		warn(P .. "StanGracza/Pety " .. polecenie .. ": " .. tostring(w))
	end
	return nil
end

local function wydatki(st)
	return if st and type(st.wydatki) == "table" then st.wydatki else {}
end

-- atrybuty każdego jajka: cena następnego (licznik osobny albo wspólny) i ile takich jajek gracz kupił
local function ustawCeny(gracz: Player, wyd)
	for _, j in D.jajka do
		gracz:SetAttribute(j.atrybuty.cena, L.cena(D, j, L.kupione(D, j, wyd)))
		gracz:SetAttribute(j.atrybuty.kupione, L.kupione(D, j, wyd, "osobny"))
	end
end

local function odswiezCene(gracz: Player)
	if graczOk(gracz) then
		ustawCeny(gracz, wydatki(wolajPety("stan", gracz)))
	end
end

------------------------------------------------------------------ kupno i wyklucie
local zajety: { [Player]: number } = {}

local function odmowa(gracz: Player, powod: string, tekst: string)
	dolicz("LicznikOdmow")
	kontener:SetAttribute("OstatniaOdmowa", powod)
	zdarzenia:FireClient(gracz, "odmowa", tekst, powod)
	return { ok = false, powod = powod, tekst = tekst }
end

local function kup(gracz: any, idJajka: any, wymuszoneR: any)
	if not graczOk(gracz) then
		return { ok = false, powod = "zly_gracz" }
	end
	local t = teraz()
	local d = L.decyzja(D, { stan_gracza = sygnalPetow() ~= nil, jajko = idJajka,
		zajety = zajety[gracz] ~= nil and t < zajety[gracz] })
	if not d.ok then
		return odmowa(gracz, d.powod, d.tekst)
	end
	local j = L.jajko(D, idJajka)
	zajety[gracz] = t + D.wyklucie.blokada_s -- przed wywołaniem: drugi E w tym czasie dostaje „trwa wyklucie”
	local st = wolajPety("stan", gracz)
	if not st or not st.ok then
		zajety[gracz] = nil
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	local wyd = wydatki(st)
	local cena = L.cena(D, j, L.kupione(D, j, wyd))
	local r = if type(wymuszoneR) == "number" and wymuszoneR >= 0 and wymuszoneR < 1 then wymuszoneR else los:NextNumber()
	local pet = L.losuj(D, j, r)
	local w = wolajPety("kup", gracz, { ile = cena, zrodlo = D.kontener, cel = j.id, pet = pet,
		premia = L.premiaPeta(D, pet) })
	if not w or not w.ok then
		zajety[gracz] = nil
		if w and w.powod == "za_malo" then
			return odmowa(gracz, "za_malo", L.tekstBraku(D, w.brakuje, w.zloto, cena))
		end
		return odmowa(gracz, if w then tostring(w.powod) else "brak_stanu", if w then D.teksty.blad else D.teksty.brak_stanu)
	end
	local poZakupie = {}
	for k, v in wyd do
		poZakupie[k] = v
	end
	poZakupie[j.id] = if type(w.licznik) == "number" then w.licznik else L.kupione(D, j, wyd, "osobny") + 1
	ustawCeny(gracz, poZakupie)
	local nastepna = L.cena(D, j, L.kupione(D, j, poZakupie))
	local info = { jajko = j.id, pet = pet, nowy = w.nowy == true, kopie = w.kopie, aktywny = w.aktywny, cena = cena,
		nastepna = nastepna, zloto = w.zloto }
	zdarzenia:FireClient(gracz, "wyklucie", info)
	dolicz("LicznikZakupow")
	kontener:SetAttribute("OstatniZakup", string.format("%s:%s:%s:%dz", gracz.Name, j.id, pet, cena))
	info.ok = true
	return info
end

------------------------------------------------------------------ zagroda: lista, wybór, odstawienie
local function polozenie(gracz: Player): Vector3?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	return if hrp and hrp:IsA("BasePart") then hrp.Position else nil
end

local function przyZagrodzie(gracz: Player): boolean
	local p = polozenie(gracz)
	if not p then
		return false
	end
	local e = D.polozenia.zagroda_e
	local dx, dz = p.X - e[1], p.Z - e[3]
	return dx * dx + dz * dz <= D.zagroda.zasieg_wyboru * D.zagroda.zasieg_wyboru
end

local function wyslijListe(gracz: Player)
	local st = wolajPety("stan", gracz)
	if not st or not st.ok then
		zdarzenia:FireClient(gracz, "lista", { brak = true, tekst = D.teksty.brak_stanu })
		return
	end
	zdarzenia:FireClient(gracz, "lista", { wiersze = L.wierszeZagrody(D, st.kopie, st.aktywny), aktywny = st.aktywny })
end

local function wybierz(gracz: Player, pet: any, bezZasiegu: boolean?)
	if type(pet) ~= "string" or #pet > D.limity.dlugosc_id or L.pet(D, pet) == nil then
		return odmowa(gracz, "nie_masz", D.teksty.nie_masz)
	end
	if not bezZasiegu and not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	local w = wolajPety("aktywny", gracz, { pet = pet, premia = L.premiaPeta(D, pet) })
	if not w then
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	if not w.ok then
		return odmowa(gracz, tostring(w.powod), D.teksty.nie_masz)
	end
	dolicz("LicznikWyborow")
	zdarzenia:FireClient(gracz, "wybrany", pet)
	wyslijListe(gracz)
	return { ok = true, aktywny = pet }
end

local function odstaw(gracz: Player)
	if not przyZagrodzie(gracz) then
		return odmowa(gracz, "za_daleko", D.teksty.za_daleko)
	end
	local w = wolajPety("aktywny", gracz, { odstaw = true })
	if not w or not w.ok then
		return odmowa(gracz, "brak_stanu", D.teksty.brak_stanu)
	end
	zdarzenia:FireClient(gracz, "wybrany", nil)
	wyslijListe(gracz)
	return { ok = true }
end

------------------------------------------------------------------ zdarzenia od klienta (bez liczb, z limitem)
local ostatnie: { [Player]: number } = {}
zdarzenia.OnServerEvent:Connect(function(gracz: Player, polecenie: any, a: any)
	if type(polecenie) ~= "string" then
		return
	end
	local t = os.clock()
	local klucz = gracz
	if ostatnie[klucz] and t - ostatnie[klucz] < D.limity.odstep_zdarzen_s and polecenie ~= "czekaj" then
		return
	end
	ostatnie[klucz] = t
	local ok, blad = pcall(function()
		if polecenie == "lista" then
			wyslijListe(gracz)
		elseif polecenie == "wybierz" then
			wybierz(gracz, a, false)
		elseif polecenie == "odstaw" then
			odstaw(gracz)
		elseif polecenie == "czekaj" then
			local czeka = if a == true then true else nil
			if gracz:GetAttribute(AG.czeka) ~= czeka then
				gracz:SetAttribute(AG.czeka, czeka)
			end
		end
	end)
	if not ok then
		warn(P .. "zdarzenie " .. polecenie .. ": " .. tostring(blad))
	end
end)

------------------------------------------------------------------ podpowiedzi E (części z budowy w Edit)
local function podpowiedz(sciezka: { string }): ProximityPrompt?
	local o: Instance? = kontener
	for _, n in sciezka do
		o = o and o:FindFirstChild(n)
	end
	return if o and o:IsA("ProximityPrompt") then o else nil
end

for _, j in D.jajka do
	local promptJajka = podpowiedz({ "Punkty", j.punkt_e, "Podpowiedz" })
	if promptJajka then
		promptJajka.Enabled = true
		local id = j.id
		promptJajka.Triggered:Connect(function(gracz: Player)
			local ok, blad = pcall(kup, gracz, id)
			if not ok then
				zajety[gracz] = nil
				warn(P .. "kup: " .. tostring(blad))
			end
		end)
	else
		warn(P .. "brak podpowiedzi E inkubatora " .. j.id .. " — przebuduj kontener (zbuduj.py)")
	end
end

local promptZagrody = podpowiedz({ "Zagroda", "E wybor", "Podpowiedz" })
local function zapasoweE()
	if promptZagrody then
		promptZagrody.Enabled = workspace:FindFirstChild(D.zagroda.kontener_bazaru) == nil
		kontener:SetAttribute("ZapasoweEZagrody", promptZagrody.Enabled)
	end
end
if promptZagrody then
	promptZagrody.Triggered:Connect(function(gracz: Player)
		zdarzenia:FireClient(gracz, "okno")
	end)
end
zapasoweE()
workspace.ChildAdded:Connect(function(o)
	if o.Name == D.zagroda.kontener_bazaru then
		zapasoweE()
	end
end)
workspace.ChildRemoved:Connect(function(o)
	if o.Name == D.zagroda.kontener_bazaru then
		zapasoweE()
	end
end)

------------------------------------------------------------------ gracze
local function nowyGracz(gracz: Player)
	ustawCeny(gracz, {})
	-- stan gracza może ruszyć później (kolejność skryptów) — cena z profilu, gdy będzie
	for _ = 1, 20 do
		if not graczOk(gracz) then
			return
		end
		if sygnalPetow() then
			odswiezCene(gracz)
			return
		end
		task.wait(1)
	end
end
Players.PlayerAdded:Connect(nowyGracz)
for _, g in Players:GetPlayers() do
	task.spawn(nowyGracz, g)
end
Players.PlayerRemoving:Connect(function(gracz: Player)
	zajety[gracz] = nil
	ostatnie[gracz] = nil
end)

------------------------------------------------------------------ haczyk testowy
local function ktory(g: any): Player?
	if typeof(g) == "Instance" and g:IsA("Player") then
		return g
	end
	return Players:GetPlayers()[1]
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any, c: any)
	if polecenie == "zgodnosc" then
		return zgodnosc()
	end
	local g = ktory(a)
	if not g then
		return nil
	end
	if polecenie == "kup" then
		return kup(g, b or D.jajka[1].id, c)
	elseif polecenie == "zwolnij" then
		zajety[g] = nil
		return true
	elseif polecenie == "wybierz" then
		return wybierz(g, b, c == true)
	elseif polecenie == "stan" then
		local st = wolajPety("stan", g)
		local ceny, kupioneJ = {}, {}
		for _, j in D.jajka do
			ceny[j.id] = g:GetAttribute(j.atrybuty.cena)
			kupioneJ[j.id] = g:GetAttribute(j.atrybuty.kupione)
		end
		return { stanGracza = sygnalPetow() ~= nil, zajety = zajety[g] ~= nil and teraz() < zajety[g],
			cena = ceny[D.jajka[1].id], ceny = ceny, kupione = kupioneJ, czeka = g:GetAttribute(AG.czeka), pety = st,
			zapasoweE = kontener:GetAttribute("ZapasoweEZagrody") }
	end
	warn(P .. "SterowanieSerwera: nieznane polecenie " .. tostring(polecenie))
	return nil
end

kontener:SetAttribute("SerwerPetowGotowy", true)
local opisJajek = {}
for _, j in D.jajka do
	table.insert(opisJajek, string.format("%s od %d", j.id, L.cena(D, j, 0)))
end
print(string.format("%sgotowy: logika %s, stan gracza %s, jajka: %s (licznik ceny %s)", P,
	tostring(kontener:GetAttribute("ZgodnoscLogikiPetow")), if sygnalPetow() then "jest" else "BRAK (inkubator odmawia)",
	table.concat(opisJajek, ", "), D.licznik_ceny.tryb))
