--[[
	SerwerWalki — serwerowa połowa testu walki 3D (Script, RunContext = Server).

	Jedyny punkt styku z klientem to RemoteFunction „RozpocznijWalke”:
		klient prosi (bez żadnych danych) → serwer sprawdza, czy wolno → liczy całą walkę → odsyła dziennik zdarzeń.
	Klient nie przysyła liczb, a to, co przyśle, jest ignorowane. Statystyki zna tylko serwer.

	Kiedy wolno zacząć walkę (sprawdza wyłącznie serwer, kolejno):
		1. nie częściej niż jedna prośba na ODSTEP_PROSB s (także odrzucona) — „za_szybko”;
		2. postać żyje i stoi najwyżej MAKS_ODLEGLOSC studów od tablicy — „brak_postaci” / „za_daleko”;
		3. poprzednia walka tego gracza się skończyła: serwer pamięta czas jej końca (teraz + walka.czas) — „walka_trwa”.
		   „POMIŃ” skraca tylko odtwarzanie u klienta, nie ten limit. Tempo zdobywania łupu wyznacza więc długość walki.

	Do testów: atrybut kontenera „ZiarnoTestowe” (liczba > 0, ustawiany po stronie serwera) wymusza ziarno.
]]
if not game:GetService("RunService"):IsStudio() then
	-- Prototyp działa wyłącznie w Studio. Poza Studio (opublikowane miejsce) serwer usuwa cały kontener — arenę, słup,
	-- szablony aktorów i podpowiedź — zanim ktokolwiek dołączy, więc w świecie gry nie zostaje nic widocznego ani klikalnego.
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local SilnikWalki = require(moduly:WaitForChild("SilnikWalki"))
local zdalna = kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke") :: RemoteFunction
local deska = kontener:WaitForChild("Arena"):WaitForChild("Tablica"):WaitForChild("Deska") :: BasePart

-- Podpowiedź jest zbudowana jako wyłączona (zabezpieczenie na wypadek, gdyby ten skrypt nie ruszył); włącza ją dopiero serwer w Studio.
local podpowiedz = deska:WaitForChild("PodpowiedzWalki") :: ProximityPrompt
podpowiedz.Enabled = true

-- Statystyki testowe (w prawdziwej grze: z zapisu gracza i tabeli przeciwników — też tylko na serwerze).
local STATYSTYKI = {
	gracz = { nazwa = "Rycerz", poziom = 3, hp = 480, atak = 150, obrona = 30, szybkosc = 12,
		krytyk = 0.22, mnoznikKrytyka = 3.0, blok = 0.30, unik = 0.06 },
	wrog = { nazwa = "Zbir", poziom = 2, hp = 450, atak = 125, obrona = 15, szybkosc = 9,
		krytyk = 0.12, mnoznikKrytyka = 2.5, blok = 0.10, unik = 0.12 },
}

local ODSTEP_PROSB = 1.0 -- s: najkrótsza przerwa między prośbami jednego gracza (także odrzuconymi)
local MAKS_ODLEGLOSC = 20 -- studów od tablicy (podpowiedź działa z 14)
local ZAPAS_SESJI = 0.4 -- s: serwer uznaje walkę za skończoną odrobinę przed końcem odtwarzania u klienta (sieć, zasłona)

local ostatniaProsba: { [Player]: number } = {}
local walkaDo: { [Player]: number } = {} -- czas serwera (workspace:GetServerTimeNow()), do którego trwa walka gracza
local generator = Random.new()

local function wybierzZiarno(): number
	local wymuszone = kontener:GetAttribute("ZiarnoTestowe")
	if type(wymuszone) == "number" and wymuszone >= 1 then
		return math.floor(wymuszone)
	end
	return generator:NextInteger(1, 2147483646)
end

-- odległość żywej postaci od tablicy albo nil (brak postaci / martwa)
local function odlegloscOdTablicy(gracz: Player): number?
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if not hrp or not hrp:IsA("BasePart") or not hum or hum.Health <= 0 then
		return nil
	end
	return (hrp.Position - deska.Position).Magnitude
end

zdalna.OnServerInvoke = function(gracz: Player)
	-- żadnych argumentów od klienta nie czytamy
	local teraz = os.clock()
	local poprzednio = ostatniaProsba[gracz]
	if poprzednio and teraz - poprzednio < ODSTEP_PROSB then
		return { ok = false, powod = "za_szybko", ponowZa = ODSTEP_PROSB - (teraz - poprzednio) }
	end
	ostatniaProsba[gracz] = teraz

	local odleglosc = odlegloscOdTablicy(gracz)
	if not odleglosc then
		return { ok = false, powod = "brak_postaci" }
	elseif odleglosc > MAKS_ODLEGLOSC then
		return { ok = false, powod = "za_daleko", odleglosc = math.floor(odleglosc) }
	end

	local czasSerwera = workspace:GetServerTimeNow()
	local koniec = walkaDo[gracz]
	if koniec and czasSerwera < koniec then
		return { ok = false, powod = "walka_trwa", ponowZa = koniec - czasSerwera }
	end

	local ziarno = wybierzZiarno()
	local udalo, walka = pcall(SilnikWalki.symuluj, STATYSTYKI.gracz, STATYSTYKI.wrog, ziarno)
	if not udalo then
		warn("[TestWalki] Silnik walki zgłosił błąd: " .. tostring(walka))
		return { ok = false, powod = "blad_silnika" }
	end
	walkaDo[gracz] = czasSerwera + walka.czas - ZAPAS_SESJI

	-- W prawdziwej grze dokładnie tutaj serwer przyznaje i zapisuje łup; klient dostaje tylko zapis do pokazania.
	kontener:SetAttribute("SerwerLicznikWalk", (kontener:GetAttribute("SerwerLicznikWalk") or 0) + 1)
	kontener:SetAttribute("SerwerOstatnieZiarno", ziarno)

	-- Mapa jest strumieniowana: poproś o doczytanie areny, zanim klient przeniesie tam kamerę.
	pcall(function()
		gracz:RequestStreamAroundAsync(Ustawienia.podloga().Position, 3)
	end)

	return { ok = true, walka = walka, nastepnaOd = walkaDo[gracz] }
end

Players.PlayerRemoving:Connect(function(gracz)
	ostatniaProsba[gracz] = nil
	walkaDo[gracz] = nil
end)
