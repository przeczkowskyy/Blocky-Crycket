--[[
	Źródła telemetrii — podpina agregator pod zdarzenia serwera:
	- Players.PlayerAdded / PlayerRemoving → liczba sesji i ich długość;
	- ScriptContext.Error → błędy skryptów (komunikat czyszczony z nazw graczy);
	- RunService.Heartbeat → liczba klatek serwera na sekundę;
	- probka() wołana co minutę → liczba graczy, pamięć i klatki serwera.

	PRYWATNOŚĆ: czas wejścia i nazwy graczy są tylko w pamięci serwera (do policzenia długości sesji i do
	wycięcia nazw z komunikatów błędów). Nic z tego nie jest zapisywane ani wysyłane.

	Usługi są wstrzykiwane (opcje.uslugi), żeby dało się je podmienić w teście.
]]

local Zrodla = {}
Zrodla.__index = Zrodla

local BLEDOW_Z_TRESCIA_NA_MINUTE = 60 -- powyżej tego błędy są tylko liczone (ochrona przed lawiną)
local PAMIETAJ_NAZWE_S = 600 -- tyle sekund po wyjściu gracza wycinamy jeszcze jego nazwę z błędów

--[[
	opcje:
		agregator (wymagany) obiekt z Agregator.nowy()
		uslugi    { Players, ScriptContext, RunService, Stats } — domyślnie prawdziwe usługi gry
		zegar     funkcja → sekundy Unix (domyślnie os.time)
		stoper    funkcja → dokładny czas w sekundach do pomiaru klatek (domyślnie os.clock)
]]
function Zrodla.nowe(opcje)
	if type(opcje) ~= "table" or opcje.agregator == nil then
		error("Zrodla.nowe: podaj opcje.agregator")
	end
	local uslugi = opcje.uslugi or {}
	local self = setmetatable({}, Zrodla)
	self.agregator = opcje.agregator
	self.zegar = opcje.zegar or os.time
	self.stoper = opcje.stoper or os.clock
	self.uslugi = {
		Players = uslugi.Players or game:GetService("Players"),
		ScriptContext = uslugi.ScriptContext or game:GetService("ScriptContext"),
		RunService = uslugi.RunService or game:GetService("RunService"),
		Stats = uslugi.Stats or game:GetService("Stats"),
	}
	self.bledy_razem = 0
	self._wejscia = {} -- gracz (obiekt Player) → czas wejścia; tylko w pamięci
	self._niedawni = {} -- lista { nazwy = {…}, do_kiedy = czas } graczy, którzy właśnie wyszli
	self._polaczenia = {}
	self._klatki = 0
	self._ostatni_pomiar = self.stoper()
	self._minuta_bledow = -1
	self._bledy_w_minucie = 0
	self._dziala = false
	return self
end

local function nazwy_gracza(gracz)
	local nazwy = {}
	local ok = pcall(function()
		nazwy[#nazwy + 1] = gracz.Name
		if gracz.DisplayName ~= gracz.Name then
			nazwy[#nazwy + 1] = gracz.DisplayName
		end
	end)
	if not ok then
		return {}
	end
	return nazwy
end

function Zrodla:_wejscie(gracz)
	if self._wejscia[gracz] ~= nil then
		return
	end
	self._wejscia[gracz] = self.zegar()
	self.agregator:sesja_start()
end

function Zrodla:_wyjscie(gracz)
	local od = self._wejscia[gracz]
	if od == nil then
		return
	end
	self._wejscia[gracz] = nil
	local teraz = self.zegar()
	self.agregator:sesja_koniec(teraz - od)
	self._niedawni[#self._niedawni + 1] = { nazwy = nazwy_gracza(gracz), do_kiedy = teraz + PAMIETAJ_NAZWE_S }
end

-- Nazwy do wycięcia z komunikatów błędów: gracze na serwerze i ci, którzy wyszli w ostatnich minutach.
function Zrodla:_nazwy()
	local wynik = {}
	for _, gracz in ipairs(self.uslugi.Players:GetPlayers()) do
		for _, nazwa in ipairs(nazwy_gracza(gracz)) do
			wynik[#wynik + 1] = nazwa
		end
	end
	local teraz = self.zegar()
	local aktualni = {}
	for _, wpis in ipairs(self._niedawni) do
		if wpis.do_kiedy > teraz then
			aktualni[#aktualni + 1] = wpis
			for _, nazwa in ipairs(wpis.nazwy) do
				wynik[#wynik + 1] = nazwa
			end
		end
	end
	self._niedawni = aktualni
	return wynik
end

-- Błąd skryptu (z ScriptContext.Error albo zgłoszony ręcznie przez Telemetria.blad).
function Zrodla:blad(komunikat)
	self.bledy_razem += 1
	local minuta = math.floor(self.zegar() / 60)
	if minuta ~= self._minuta_bledow then
		self._minuta_bledow = minuta
		self._bledy_w_minucie = 0
	end
	self._bledy_w_minucie += 1
	if self._bledy_w_minucie > BLEDOW_Z_TRESCIA_NA_MINUTE then
		self.agregator:blad_bez_tresci()
	else
		self.agregator:blad(komunikat, self:_nazwy())
	end
end

-- Podpina zdarzenia. Gracze, którzy są już na serwerze, liczą się jako sesje rozpoczęte teraz.
function Zrodla:start()
	if self._dziala then
		return
	end
	self._dziala = true
	local Players = self.uslugi.Players
	local polaczenia = self._polaczenia
	polaczenia[#polaczenia + 1] = Players.PlayerAdded:Connect(function(gracz)
		self:_wejscie(gracz)
	end)
	polaczenia[#polaczenia + 1] = Players.PlayerRemoving:Connect(function(gracz)
		self:_wyjscie(gracz)
	end)
	for _, gracz in ipairs(Players:GetPlayers()) do
		self:_wejscie(gracz)
	end
	polaczenia[#polaczenia + 1] = self.uslugi.ScriptContext.Error:Connect(function(komunikat)
		-- pcall: błąd w samej telemetrii nie może wywołać kolejnego zdarzenia Error (pętla)
		pcall(function()
			self:blad(komunikat)
		end)
	end)
	polaczenia[#polaczenia + 1] = self.uslugi.RunService.Heartbeat:Connect(function()
		self._klatki += 1
	end)
end

-- Próbka co minutę. Zwraca stan serwera dla wpisu „na żywo”: { gracze, fps, pamiec_mb, bledy }.
function Zrodla:probka()
	local Players = self.uslugi.Players
	-- sesje graczy, których już nie ma, a zdarzenie wyjścia nie dotarło
	for gracz in pairs(self._wejscia) do
		if gracz.Parent == nil then
			self:_wyjscie(gracz)
		end
	end
	local gracze = #Players:GetPlayers()
	self.agregator:probka_ccu(gracze)

	local teraz = self.stoper()
	local uplynelo = teraz - self._ostatni_pomiar
	local fps = nil
	if uplynelo >= 1 then -- przy krótszym pomiarze wynik byłby przypadkowy
		fps = math.floor(self._klatki / uplynelo * 10 + 0.5) / 10
	end
	self._klatki = 0
	self._ostatni_pomiar = teraz

	local pamiec_mb = nil
	local ok, mb = pcall(function()
		return self.uslugi.Stats:GetTotalMemoryUsageMb()
	end)
	if ok and type(mb) == "number" then
		pamiec_mb = math.floor(mb + 0.5)
	end
	return { gracze = gracze, fps = fps, pamiec_mb = pamiec_mb, bledy = self.bledy_razem }
end

-- Zamyka wszystkie otwarte sesje (serwer się wyłącza, a PlayerRemoving mogło nie zdążyć).
function Zrodla:zamknij_sesje()
	local otwarte = {}
	for gracz in pairs(self._wejscia) do
		otwarte[#otwarte + 1] = gracz
	end
	for _, gracz in ipairs(otwarte) do
		self:_wyjscie(gracz)
	end
end

function Zrodla:stop()
	for _, polaczenie in ipairs(self._polaczenia) do
		polaczenie:Disconnect()
	end
	self._polaczenia = {}
	self._dziala = false
end

return Zrodla
