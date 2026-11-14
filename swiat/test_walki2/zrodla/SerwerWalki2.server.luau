--[[
	SerwerWalki2 — serwerowa połowa prototypu walki v2 (Script, RunContext = Server). Wzór: v1 (SerwerWalki).

	Jedyny punkt styku z klientem to RemoteFunction Zdalne/RozpocznijWalke2:
		klient → wybor = { klasa = "wojownik" | "zwiadowca" | "mag", przeciwnik = id potwora lasu, poziom = "1" | "5" | "10" }
		serwer → sprawdza wybór z ZAMKNIĘTĄ listą (inne wartości, liczby i dodatkowe pola: odmowa „zly_wybor” albo
		         pominięcie), sam buduje postać wzorcową (Moduly/Wzorcowe = tools/walka/wzorcowe.py) i przeciwnika,
		         losuje ziarno, woła Moduly/Walka/Silnik.symuluj i odsyła dziennik { ok, walka, nastepnaOd }.
	Klient nie przysyła liczb (poziom to napis z listy, nie liczba), a resztę argumentów serwer ignoruje (D-016).

	Kiedy wolno zacząć walkę (kolejno, jak w v1):
		1. nie częściej niż jedna prośba na ODSTEP_PROSB s (także odrzucona) — „za_szybko”;
		2. wybór z listy — „zly_wybor”;
		3. postać żyje i stoi najwyżej MAKS_ODLEGLOSC studów od tablicy — „brak_postaci” / „za_daleko”;
		4. poprzednia walka gracza się skończyła: serwer pamięta czas jej końca (teraz + walka.czas, czyli PEŁNY czas
		   dziennika przy tempie ×1) — „walka_trwa”. Tempo ×2 / ×4 i „POMIŃ” skracają tylko odtwarzanie u klienta.
	Łup liczy silnik w tym samym wywołaniu co walkę — bez walki nie ma łupu (w grze tu byłby zapis).

	Do testów (tylko po stronie serwera, klient tego nie zmieni): atrybut kontenera „ZiarnoTestowe” (liczba ≥ 1)
	wymusza ziarno; atrybut „TestBezSesji” = true wyłącza blokadę sesji walki (tylko narzędzie klatek, które ogląda
	dziesiątki walk pod rząd; zmiana atrybutu u klienta się nie replikuje, więc klient go nie ustawi).
]]
if not game:GetService("RunService"):IsStudio() then
	-- Prototyp działa wyłącznie w Studio. Poza Studio (opublikowane miejsce) serwer usuwa CAŁY kontener — arenę,
	-- galerię, szablony aktorów, kopię silnika i podpowiedź — zanim ktokolwiek dołączy.
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local Wzorcowe = require(moduly:WaitForChild("Wzorcowe"))
local folderWalki = moduly:WaitForChild("Walka")
local Silnik = require(folderWalki:WaitForChild("Silnik"))
local Dane = require(folderWalki:WaitForChild("Dane"))
local zdalna = kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke2") :: RemoteFunction
local deska = kontener:WaitForChild("Arena"):WaitForChild("Tablica"):WaitForChild("Deska") :: BasePart

-- podpowiedź jest zbudowana jako wyłączona; włącza ją dopiero serwer w Studio
local podpowiedz = deska:WaitForChild("PodpowiedzWalki2") :: ProximityPrompt
podpowiedz.ActionText = "Wybierz walkę"
podpowiedz.Enabled = true

local ODSTEP_PROSB = 1.0
local MAKS_ODLEGLOSC = 20
local ZAPAS_SESJI = 0.4

-- ZAMKNIĘTE listy wyboru (dane testowe prototypu)
local KLASY = {}
for _, k in Wzorcowe.KLASY do
	KLASY[k] = true
end
local PRZECIWNICY = {}
for _, d in Dane.przeciwnicy do
	PRZECIWNICY[d.id] = true
end
local POZIOMY = { ["1"] = 1, ["5"] = 5, ["10"] = 10 }

local ostatniaProsba: { [Player]: number } = {}
local walkaDo: { [Player]: number } = {}
local generator = Random.new()

local function wybierzZiarno(): number
	local wymuszone = kontener:GetAttribute("ZiarnoTestowe")
	if type(wymuszone) == "number" and wymuszone >= 1 and wymuszone < 2147483647 then
		return math.floor(wymuszone)
	end
	return generator:NextInteger(1, 2147483646)
end

local function odlegloscOdTablicy(gracz: Player): number?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if not hrp or not hrp:IsA("BasePart") or not hum or hum.Health <= 0 then
		return nil
	end
	return (hrp.Position - deska.Position).Magnitude
end

-- wybór od klienta → (klasa, przeciwnik, poziom) albo nil; czytamy tylko trzy pola i tylko jako napisy z listy
local function sprawdzWybor(wybor: any): (string?, string?, number?)
	if type(wybor) ~= "table" then
		return nil
	end
	local klasa, przeciwnik, poziom = rawget(wybor, "klasa"), rawget(wybor, "przeciwnik"), rawget(wybor, "poziom")
	if type(klasa) ~= "string" or type(przeciwnik) ~= "string" or type(poziom) ~= "string" then
		return nil
	end
	if not KLASY[klasa] or not PRZECIWNICY[przeciwnik] or not POZIOMY[poziom] then
		return nil
	end
	return klasa, przeciwnik, POZIOMY[poziom]
end

zdalna.OnServerInvoke = function(gracz: Player, wybor: any)
	local teraz = os.clock()
	local poprzednio = ostatniaProsba[gracz]
	if poprzednio and teraz - poprzednio < ODSTEP_PROSB then
		return { ok = false, powod = "za_szybko", ponowZa = ODSTEP_PROSB - (teraz - poprzednio) }
	end
	ostatniaProsba[gracz] = teraz

	local klasa, przeciwnik, poziom = sprawdzWybor(wybor)
	if not klasa then
		return { ok = false, powod = "zly_wybor" }
	end

	local odleglosc = odlegloscOdTablicy(gracz)
	if not odleglosc then
		return { ok = false, powod = "brak_postaci" }
	elseif odleglosc > MAKS_ODLEGLOSC then
		return { ok = false, powod = "za_daleko", odleglosc = math.floor(odleglosc) }
	end

	local czasSerwera = workspace:GetServerTimeNow()
	local koniec = walkaDo[gracz]
	if koniec and czasSerwera < koniec and kontener:GetAttribute("TestBezSesji") ~= true then
		return { ok = false, powod = "walka_trwa", ponowZa = koniec - czasSerwera }
	end

	local ziarno = wybierzZiarno()
	local postac = Wzorcowe.postac(klasa :: string, poziom :: number)
	local udalo, walka = pcall(Silnik.symuluj, postac, { potwor = przeciwnik, poziom = poziom }, ziarno)
	if not udalo then
		warn("[TestWalki2] Silnik walki zgłosił błąd: " .. tostring(walka))
		return { ok = false, powod = "blad_silnika" }
	end
	walkaDo[gracz] = czasSerwera + walka.czas - ZAPAS_SESJI
	if kontener:GetAttribute("TestBezSesji") == true then
		walkaDo[gracz] = czasSerwera -- tylko narzędzie klatek (patrz nagłówek)
	end

	-- W prawdziwej grze dokładnie tutaj serwer przyznaje i zapisuje łup; klient dostaje tylko zapis do pokazania.
	kontener:SetAttribute("SerwerLicznikWalk", (kontener:GetAttribute("SerwerLicznikWalk") or 0) + 1)
	kontener:SetAttribute("SerwerOstatnieZiarno", ziarno)
	kontener:SetAttribute("SerwerOstatniWybor", string.format("%s/%s/%d", klasa, przeciwnik, poziom))

	pcall(function()
		gracz:RequestStreamAroundAsync(Ustawienia.scena().Position, 3)
	end)

	return { ok = true, walka = walka, nastepnaOd = walkaDo[gracz] }
end

Players.PlayerRemoving:Connect(function(gracz)
	ostatniaProsba[gracz] = nil
	walkaDo[gracz] = nil
end)

kontener:SetAttribute("SerwerGotowy", true)
