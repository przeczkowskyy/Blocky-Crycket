--[[
	Telemetria gry (ServerScriptService.Server.Telemetria) — liczy, co dzieje się na serwerach, i zapisuje zbiorcze
	liczby godzina po godzinie, żeby panel zespołu pokazał je w zakładce Analityka: sesje i ich długość, graczy
	naraz, wydane Robuxy, błędy skryptów i serwery na żywo.

	MODUŁ JEST BEZWŁADNY. Samo require() niczego nie uruchamia: nie podpina zdarzeń, nie woła usług, nie zapisuje
	danych. Zaczyna działać dopiero po Telemetria.start(). O włączeniu decyduje Game Director — instrukcja
	krok po kroku: B&C/Technika/Telemetria gry.md.

	Użycie (w skrypcie serwera):
		local Telemetria = require(game.ServerScriptService.Server.Telemetria)
		Telemetria.start()                                    -- raz, przy starcie serwera
		Telemetria.lejek(gracz, 1, "Wejście do gry")          -- krok lejka (AnalyticsService + licznik w kubełku)
		Telemetria.zdarzenie("quest_ukonczony")               -- własny licznik
		Telemetria.zdarzenie("zloto_zdobyte", { wartosc = 250, gracz = gracz })
		Telemetria.zakup(gracz, info.ProductId, info.CurrencySpent, "Worek złota")   -- z ProcessReceipt, po przyznaniu
		Telemetria.blad("Nie udało się wczytać profilu")      -- błąd złapany przez pcall

	Czego NIE robi:
	- nie ustawia MarketplaceService.ProcessReceipt — zakup zgłasza kod, który obsługuje paragony;
	- nie zapisuje nazw graczy ani UserId — w danych zbiorczych są same liczby;
	- w Studio nie dotyka prawdziwego Data Store ani Memory Store (magazyn w pamięci), chyba że
	  start({ zapis_w_studio = true }) i w ustawieniach gry włączono dostęp Studio do usług API.

	Części: Agregator (czysta logika kubełków), Magazyn (zapis co 5 min i przy zamykaniu), Zrodla (zdarzenia serwera).
]]

local Telemetria = {}

local DOMYSLNA_KONFIGURACJA = {
	magazyn = "BC_Telemetria_v1", -- nazwa Data Store z kubełkami godzinowymi (panel: analityka.magazyn)
	mapa_serwerow = "BC_Telemetria_Serwery", -- sorted mapa Memory Store z serwerami na żywo
	co_ile_zapis_s = 300, -- zapis kubełków co 5 minut
	wygasanie_serwera_s = 180, -- wpis „na żywo” znika po 3 minutach bez odnowienia
	zapis_w_studio = false, -- w Studio domyślnie magazyn w pamięci
	analityka_roblox = true, -- przekazuj lejek i zdarzenia z graczem do AnalyticsService (poza Studio)
	-- do testów: zegar (funkcja → sekundy Unix), magazyn_obiekt, mapa_obiekt (atrapy zamiast usług Roblox)
}

local stan = nil -- nil, dopóki nikt nie wywołał start()

-- Wykonuje funkcję tak, żeby błąd telemetrii nigdy nie zatrzymał gry. Ostrzeżenie najwyżej raz na minutę.
local function bezpiecznie(co, funkcja)
	local ok, wynik = pcall(funkcja)
	if ok then
		return wynik
	end
	local teraz = os.time()
	if stan ~= nil and teraz - stan.ostatnie_ostrzezenie >= 60 then
		stan.ostatnie_ostrzezenie = teraz
		warn(string.format("[Telemetria] %s: %s", co, tostring(wynik)))
	end
	return nil
end

-- Ile zapisów UpdateAsync serwer może teraz wykonać (UpdateAsync zużywa budżet odczytu i zapisu).
local function budzet_zapisu()
	local ok, wynik = pcall(function()
		local DataStoreService = game:GetService("DataStoreService")
		local zapis = DataStoreService:GetRequestBudgetForRequestType(Enum.DataStoreRequestType.StandardWrite)
		local odczyt = DataStoreService:GetRequestBudgetForRequestType(Enum.DataStoreRequestType.StandardRead)
		return math.min(zapis, odczyt)
	end)
	if ok and type(wynik) == "number" then
		return wynik
	end
	return nil
end

-- Przekazuje zdarzenie do AnalyticsService (funkcja dostaje usługę). Limit Roblox to 120 + 20 × gracze żądań
-- na minutę dla całej gry — serwer bierze swoją część (20 × gracze na tym serwerze), nadmiar pomija.
local function do_analityki(funkcja)
	if stan.analityka == nil then
		return
	end
	local minuta = math.floor(stan.zegar() / 60)
	if minuta ~= stan.minuta_analityki then
		stan.minuta_analityki = minuta
		stan.analityka_w_minucie = 0
	end
	local limit = 20 * math.max(1, #stan.Players:GetPlayers())
	if stan.analityka_w_minucie >= limit then
		stan.analityka_pominiete += 1
		return
	end
	stan.analityka_w_minucie += 1
	bezpiecznie("AnalyticsService", function()
		funkcja(stan.analityka)
	end)
end

local function zamknij(powod)
	if stan == nil or not stan.dziala then
		return
	end
	stan.dziala = false
	bezpiecznie("zamykanie", function()
		local nazwa = "Unknown"
		if typeof(powod) == "EnumItem" then
			nazwa = powod.Name
		end
		stan.zrodla:zamknij_sesje()
		stan.agregator:zamkniecie(nazwa)
		stan.zrodla:stop()
		if stan.polaczenie_wyjscia ~= nil then
			stan.polaczenie_wyjscia:Disconnect()
		end
		stan.magazyn:zamknij()
	end)
end

--[[
	Włącza telemetrię. Wywołaj raz na serwerze. konfiguracja (wszystko opcjonalne) — pola jak w
	DOMYSLNA_KONFIGURACJA. Zwraca true, gdy moduł wystartował, false przy drugim wywołaniu.
]]
function Telemetria.start(konfiguracja)
	if stan ~= nil then
		warn("[Telemetria] start() wywołano drugi raz — moduł już działa")
		return false
	end
	local konf = {}
	for klucz, wartosc in pairs(DOMYSLNA_KONFIGURACJA) do
		konf[klucz] = wartosc
	end
	if type(konfiguracja) == "table" then
		for klucz, wartosc in pairs(konfiguracja) do
			konf[klucz] = wartosc
		end
	end
	konf.co_ile_zapis_s = math.max(30, tonumber(konf.co_ile_zapis_s) or 300)

	local Agregator = require(script.Agregator)
	local Magazyn = require(script.Magazyn)
	local Zrodla = require(script.Zrodla)

	local RunService = game:GetService("RunService")
	local Players = game:GetService("Players")
	local wStudio = RunService:IsStudio()
	local zegar = konf.zegar or os.time
	local prawdziwyZapis = (not wStudio) or konf.zapis_w_studio == true

	-- Data Store z kubełkami: prawdziwy tylko poza Studio (albo na wyraźne życzenie), inaczej atrapa w pamięci
	local magazynDanych = konf.magazyn_obiekt
	local budzet = nil
	if magazynDanych == nil and prawdziwyZapis then
		local ok, wynik = pcall(function()
			return game:GetService("DataStoreService"):GetDataStore(konf.magazyn)
		end)
		if ok then
			magazynDanych = wynik
			budzet = budzet_zapisu
		else
			warn("[Telemetria] Data Store niedostępny, liczę tylko w pamięci: " .. tostring(wynik))
		end
	end
	if magazynDanych == nil then
		magazynDanych = Magazyn.w_pamieci()
		prawdziwyZapis = false
	end

	-- sorted mapa Memory Store z serwerami na żywo
	local mapaSerwerow = konf.mapa_obiekt
	if mapaSerwerow == nil and prawdziwyZapis then
		local ok, wynik = pcall(function()
			return game:GetService("MemoryStoreService"):GetSortedMap(konf.mapa_serwerow)
		end)
		if ok then
			mapaSerwerow = wynik
		end
	end
	if mapaSerwerow == nil then
		mapaSerwerow = Magazyn.mapa_w_pamieci()
	end

	local idSerwera = game.JobId
	if idSerwera == "" then
		idSerwera = "studio" -- w Studio JobId jest pusty
	end

	local analityka = nil
	if konf.analityka_roblox and not wStudio then -- zdarzeń AnalyticsService nie da się wysyłać ze Studio
		analityka = game:GetService("AnalyticsService")
	end

	local agregator = Agregator.nowy(zegar)
	local magazyn = Magazyn.nowy({
		agregator = agregator,
		magazyn = magazynDanych,
		mapa = mapaSerwerow,
		budzet = budzet,
		zegar = zegar,
		id_serwera = idSerwera,
		wygasanie_s = konf.wygasanie_serwera_s,
	})
	local zrodla = Zrodla.nowe({ agregator = agregator, zegar = zegar })

	stan = {
		dziala = true,
		konfiguracja = konf,
		w_studio = wStudio,
		prawdziwy_zapis = prawdziwyZapis,
		zegar = zegar,
		Players = Players,
		agregator = agregator,
		magazyn = magazyn,
		zrodla = zrodla,
		analityka = analityka,
		minuta_analityki = -1,
		analityka_w_minucie = 0,
		analityka_pominiete = 0,
		ostatnie_ostrzezenie = 0,
		lejek_graczy = setmetatable({}, { __mode = "k" }), -- Player → { [krok] = true }; tylko w pamięci
	}

	agregator:start_serwera()
	zrodla:start()
	-- gracz wyszedł: zapominamy jego kroki lejka (nie czekamy, aż słabą tabelę wyczyści odśmiecacz)
	stan.polaczenie_wyjscia = Players.PlayerRemoving:Connect(function(gracz)
		stan.lejek_graczy[gracz] = nil
	end)

	local function probka_i_puls()
		local serwer = zrodla:probka()
		serwer.miejsce = game.PlaceId
		serwer.wersja_miejsca = game.PlaceVersion
		magazyn:puls(serwer)
	end

	-- od razu: ślad „moduł włączony” i pierwszy wpis serwera na żywo
	task.spawn(function()
		bezpiecznie("wpis stanu", function()
			magazyn:zapisz_stan()
		end)
		bezpiecznie("pierwsza próbka", probka_i_puls)
	end)

	-- co minutę, tuż po pełnej minucie zegarowej: liczba graczy i odnowienie wpisu „na żywo”
	task.spawn(function()
		while stan.dziala do
			task.wait(60 - (zegar() % 60) + 1)
			if not stan.dziala then
				break
			end
			bezpiecznie("próbka", probka_i_puls)
		end
	end)

	-- co 5 minut: zapis kubełków. Pierwszy zapis po 20–60 s (losowo), żeby serwery uruchomione razem
	-- nie pisały w tej samej sekundzie.
	task.spawn(function()
		task.wait(20 + 40 * math.random())
		while stan.dziala do
			bezpiecznie("zapis", function()
				magazyn:zapisz()
			end)
			task.wait(konf.co_ile_zapis_s)
		end
	end)

	-- zamknięcie serwera: Roblox czeka na tę funkcję najwyżej 30 sekund
	game:BindToClose(zamknij)

	return true
end

--[[
	Własne zdarzenie gry. nazwa: krótka, stała nazwa (np. "quest_ukonczony"). pola (opcjonalne):
		wartosc — liczba do zsumowania (bez niej zdarzenie liczy się jako 1),
		gracz   — obiekt Player; wtedy zdarzenie idzie też do AnalyticsService:LogCustomEvent.
	Gracz służy tylko do wywołania AnalyticsService — w kubełku go nie ma.
]]
function Telemetria.zdarzenie(nazwa, pola)
	if stan == nil then
		return false
	end
	return bezpiecznie("zdarzenie", function()
		local wartosc, gracz = nil, nil
		if type(pola) == "table" then
			wartosc = pola.wartosc
			gracz = pola.gracz
		end
		stan.agregator:zdarzenie(nazwa, wartosc)
		if gracz ~= nil then
			-- AnalyticsService przyjmuje najwyżej 100 różnych nazw zdarzeń na grę — nazwy mają być stałe
			local liczbowa = tonumber(wartosc) or 1
			do_analityki(function(analityka)
				analityka:LogCustomEvent(gracz, tostring(nazwa), liczbowa)
			end)
		end
		return true
	end) == true
end

--[[
	Krok lejka wejścia do gry (1–100): AnalyticsService:LogOnboardingFunnelStepEvent i licznik w kubełku.
	Ten sam krok tego samego gracza liczy się raz na sesję (jak w AnalyticsService) — licznik w kubełku mówi więc,
	ilu graczy doszło do kroku, a nie ile razy kod go zgłosił. Kto przeszedł który krok, wie tylko pamięć serwera
	(słaba tabela: znika razem z obiektem Player); w zapisie jest sama liczba.
]]
function Telemetria.lejek(gracz, krok, nazwa)
	if stan == nil then
		return false
	end
	return bezpiecznie("lejek", function()
		local kroki = nil
		if gracz ~= nil then
			kroki = stan.lejek_graczy[gracz]
			if kroki ~= nil and kroki[krok] then
				return false -- ten gracz już zgłosił ten krok w tej sesji
			end
		end
		if not stan.agregator:lejek(krok, nazwa) then
			return false
		end
		if gracz ~= nil then
			if kroki == nil then
				kroki = {}
				stan.lejek_graczy[gracz] = kroki
			end
			kroki[krok] = true
			-- stepName jest wymagany: bez nazwy wysyłamy „Krok N”
			local nazwaKroku = if type(nazwa) == "string" and nazwa ~= "" then nazwa else "Krok " .. tostring(krok)
			do_analityki(function(analityka)
				analityka:LogOnboardingFunnelStepEvent(gracz, krok, nazwaKroku)
			end)
		end
		return true
	end) == true
end

--[[
	Zakup za Robuxy — wywołaj z obsługi paragonów (MarketplaceService.ProcessReceipt albo handler z
	BindReceiptHandler(Enum.ReceiptType.DeveloperProduct, …)) PO przyznaniu produktu i tuż przed zwróceniem
	„Processed”, żeby paragon dostarczony ponownie nie liczył się dwa razy:
		Telemetria.zakup(gracz, receiptInfo.ProductId, receiptInfo.CurrencySpent, "Worek złota")
	Paragonów przelewów Robux (RobuxTransferSender / RobuxTransferReceiver) tu nie zgłaszaj — to nie zakupy.
	gracz jest w podpisie dla wygody wywołania; nie zapisujemy, kto kupił.
]]
function Telemetria.zakup(gracz, idProduktu, robuxy, nazwa)
	if stan == nil then
		return false
	end
	return bezpiecznie("zakup", function()
		stan.agregator:zakup(idProduktu, robuxy, nazwa)
		return true
	end) == true
end

-- Błąd zgłoszony ręcznie (np. złapany przez pcall). Błędy niezłapane moduł zbiera sam z ScriptContext.Error.
function Telemetria.blad(komunikat)
	if stan == nil then
		return false
	end
	return bezpiecznie("błąd", function()
		stan.zrodla:blad(komunikat)
		return true
	end) == true
end

-- Zapisuje oczekujące dane od razu (diagnostyka, testy). Czeka na zapis; zwraca true, gdy wszystko zapisano.
function Telemetria.zapisz_teraz()
	if stan == nil then
		return false
	end
	return bezpiecznie("zapis na żądanie", function()
		return stan.magazyn:zapisz()
	end) == true
end

-- Stan modułu do podglądu w konsoli: print(Telemetria.stan())
function Telemetria.stan()
	if stan == nil then
		return { dziala = false }
	end
	return {
		dziala = stan.dziala,
		w_studio = stan.w_studio,
		prawdziwy_zapis = stan.prawdziwy_zapis,
		magazyn = stan.konfiguracja.magazyn,
		ostatni_udany_zapis = stan.magazyn.ostatni_udany_zapis,
		zapisane_kubelki = stan.magazyn.zapisane_kubelki,
		nieudane_zapisy = stan.magazyn.nieudane_zapisy,
		ostatni_blad_zapisu = stan.magazyn.ostatni_blad,
		bledy_skryptow = stan.zrodla.bledy_razem,
		pominiete_zdarzenia_analityki = stan.analityka_pominiete,
		utracone_godziny = stan.agregator.utracone_godziny,
	}
end

return Telemetria
