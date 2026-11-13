--[[
	Agregator telemetrii — CZYSTA logika: żadnych globali Roblox (game, task, os, Instance…), tylko biblioteki
	języka (string, table, math, utf8) i zegar przekazany z zewnątrz. Dzięki temu da się ją sprawdzić testem
	(tools/studio/test_telemetrii.py) bez uruchamiania gry.

	Co robi:
	- zbiera zdarzenia serwera w KUBEŁKI GODZINOWE (czas UTC), po jednym na godzinę zegarową;
	- oddaje je do zapisu (zdejmij) i przyjmuje z powrotem, gdy zapis się nie udał (oddaj);
	- scala kubełek zapisany w Data Store z przyrostem tego serwera (scal) — to funkcja dla UpdateAsync;
	- pilnuje rozmiaru wpisu: najwyżej LIMITY.* kluczy w słownikach, reszta trafia pod klucz "_inne";
	- czyści komunikaty błędów z danych graczy i liczy dla nich krótką sygnaturę.

	PRYWATNOŚĆ: w kubełku nie ma nazw graczy, UserId ani niczego, co wskazuje konkretną osobę. Są same liczby
	oraz nazwy produktów, kroków i zdarzeń, które podaje kod gry.

	Kubełek (wartość wpisu "g_RRRRMMDD_GG" w Data Store; panel czyta go przez Open Cloud — panel/bc/telemetria.py):
	{
		wersja = 1,
		t = <początek godziny, sekundy Unix UTC>, zaktualizowano = <czas ostatniego zdarzenia>,
		serwery = <ile serwerów pisało do tej godziny>, zapisy = <ile zapisów>, starty = <ile serwerów wystartowało>,
		sesje = <wejścia graczy>, sesje_zakonczone = <wyjścia>, sekundy_gry = <suma długości zakończonych sesji>,
		dlugosci = { do_1 = n, do_5 = n, do_15 = n, do_30 = n, do_60 = n, ponad_60 = n },   -- minuty
		ccu_max = <najwięcej graczy naraz na jednym serwerze>, ccu_suma, ccu_probki,          -- próbka co minutę
		ccu_minuty = { 60 liczb },   -- gracze w każdej minucie godziny, zsumowani ze wszystkich serwerów
		robuxy = <suma>, zakupy = { ["<id produktu>"] = { n, robuxy, nazwa } },
		bledy_n = <wszystkie błędy>, bledy = { ["<sygnatura>"] = { n, komunikat } },
		zdarzenia = { ["<nazwa>"] = <licznik albo suma wartości> },
		lejek = { ["<krok>"] = { n, nazwa } },
		zamkniecia = { ["<powód zamknięcia serwera>"] = n },
	}
]]

local Agregator = {}
Agregator.__index = Agregator

Agregator.WERSJA = 1
Agregator.INNE = "_inne"

Agregator.LIMITY = {
	zakupy = 60, -- różnych produktów w jednym kubełku
	bledy = 40, -- różnych sygnatur błędów
	zdarzenia = 60, -- różnych nazw własnych zdarzeń
	lejek = 100, -- kroków lejka (AnalyticsService przyjmuje kroki 1–100)
	komunikat = 160, -- bajtów skróconego komunikatu błędu
	nazwa = 60, -- bajtów nazwy produktu, zdarzenia albo kroku
	klucz = 50, -- bajtów klucza w słowniku
	godziny_w_pamieci = 48, -- tyle niezapisanych godzin trzymamy, gdy Data Store nie działa
}

-- Przedziały długości sesji: { górna granica w sekundach, nazwa przedziału }.
local PRZEDZIALY_SESJI = {
	{ 60, "do_1" },
	{ 300, "do_5" },
	{ 900, "do_15" },
	{ 1800, "do_30" },
	{ 3600, "do_60" },
}

local POLA_SUMOWANE = {
	"serwery",
	"zapisy",
	"starty",
	"sesje",
	"sesje_zakonczone",
	"sekundy_gry",
	"ccu_suma",
	"ccu_probki",
	"robuxy",
	"bledy_n",
}
local SLOWNIKI = { "dlugosci", "zakupy", "bledy", "zdarzenia", "lejek", "zamkniecia" }

-- Znaki, które we wzorcach Lua mają znaczenie specjalne (trzeba je poprzedzić %, żeby szukać dosłownie).
local ZNAKI_WZORCA = "[%^%$%(%)%%%.%[%]%*%+%-%?]"
local WZOR_GUID = "%x%x%x%x%x%x%x%x%-%x%x%x%x%-%x%x%x%x%-%x%x%x%x%-%x%x%x%x%x%x%x%x%x%x%x%x"
local NAJWIEKSZA_CALKOWITA = 9007199254740992 -- 2^53: do tej wartości liczby całkowite są dokładne

-- --------------------------------------------------------------------------- drobne narzędzia
local function liczba(wartosc, domyslnie)
	if type(wartosc) == "number" and wartosc == wartosc and wartosc ~= math.huge and wartosc ~= -math.huge then
		return wartosc
	end
	return domyslnie
end

local function nieujemna(wartosc)
	local n = liczba(wartosc, 0)
	if n < 0 then
		return 0
	end
	return n
end

-- Ucina tekst do `limit` bajtów, ale nigdy w środku znaku UTF-8 (Data Store odrzuca niepoprawny UTF-8).
local function utnij(tekst, limit)
	if #tekst <= limit then
		return tekst
	end
	local koniec = limit
	while koniec > 0 do
		local nastepny = string.byte(tekst, koniec + 1)
		if nastepny ~= nil and nastepny >= 128 and nastepny < 192 then
			koniec = koniec - 1 -- następny bajt to dalszy ciąg znaku: cofamy cięcie
		else
			break
		end
	end
	return string.sub(tekst, 1, koniec)
end

local function waga(wpis)
	if type(wpis) == "table" then
		return liczba(wpis.n, 0)
	end
	return liczba(wpis, 0)
end

-- Dolicza `wpis` do slownik[klucz]: liczby sumuje, z tekstów zostawia najnowszy niepusty.
local function dolicz_wpis(slownik, klucz, wpis)
	local obecny = slownik[klucz]
	if type(wpis) == "table" then
		if type(obecny) ~= "table" then
			obecny = {}
			slownik[klucz] = obecny
		end
		for pole, wartosc in pairs(wpis) do
			if type(wartosc) == "number" then
				obecny[pole] = nieujemna(obecny[pole]) + nieujemna(wartosc)
			elseif type(wartosc) == "string" then
				if wartosc ~= "" or obecny[pole] == nil then
					obecny[pole] = wartosc
				end
			end
		end
	elseif type(wpis) == "number" then
		slownik[klucz] = waga(obecny) + nieujemna(wpis)
	end
end

local function puste_minuty()
	local minuty = {}
	for i = 1, 60 do
		minuty[i] = 0
	end
	return minuty
end

-- --------------------------------------------------------------------------- czas i klucze
-- Początek godziny zegarowej (UTC), w której leży chwila `t` (sekundy Unix).
function Agregator.godzina(t)
	return math.floor(t / 3600) * 3600
end

-- Data UTC z sekund Unix, bez os.date (algorytm „civil from days”): rok, miesiąc, dzień, godzina.
function Agregator.data_utc(t)
	local dni = math.floor(t / 86400)
	local sekundy = t - dni * 86400
	local z = dni + 719468
	local era = math.floor(z / 146097)
	local dzien_ery = z - era * 146097
	local rok_ery = math.floor(
		(dzien_ery - math.floor(dzien_ery / 1460) + math.floor(dzien_ery / 36524) - math.floor(dzien_ery / 146096)) / 365
	)
	local rok = rok_ery + era * 400
	local dzien_roku = dzien_ery - (365 * rok_ery + math.floor(rok_ery / 4) - math.floor(rok_ery / 100))
	local mp = math.floor((5 * dzien_roku + 2) / 153)
	local dzien = dzien_roku - math.floor((153 * mp + 2) / 5) + 1
	local miesiac = mp + 3
	if mp >= 10 then
		miesiac = mp - 9
	end
	if miesiac <= 2 then
		rok = rok + 1
	end
	return rok, miesiac, dzien, math.floor(sekundy / 3600)
end

-- Klucz wpisu w Data Store dla godziny zawierającej `t`: "g_RRRRMMDD_GG" (UTC). Sortuje się jak czas.
function Agregator.klucz_godziny(t)
	local rok, miesiac, dzien, godzina = Agregator.data_utc(Agregator.godzina(t))
	return string.format("g_%04d%02d%02d_%02d", rok, miesiac, dzien, godzina)
end

-- --------------------------------------------------------------------------- teksty i sygnatury
-- Tekst bezpieczny do zapisu: bez znaków sterujących, poprawny UTF-8, najwyżej `limit` bajtów.
function Agregator.oczysc_tekst(tekst, limit)
	local wynik = tostring(tekst)
	wynik = string.gsub(wynik, "%c+", " ")
	if utf8.len(wynik) == nil then
		wynik = string.gsub(wynik, "[\128-\255]", "?")
	end
	return utnij(wynik, limit)
end

-- Klucz słownika jako tekst (Data Store nie przyjmuje słowników z kluczami liczbowymi).
function Agregator.klucz_tekstowy(wartosc)
	local tekst
	if
		type(wartosc) == "number"
		and wartosc == math.floor(wartosc)
		and wartosc > -NAJWIEKSZA_CALKOWITA
		and wartosc < NAJWIEKSZA_CALKOWITA
	then
		tekst = string.format("%d", wartosc)
	else
		tekst = tostring(wartosc)
	end
	tekst = Agregator.oczysc_tekst(tekst, Agregator.LIMITY.klucz)
	if tekst == "" then
		tekst = "?"
	end
	return tekst
end

-- Usuwa z komunikatu błędu dane graczy: nazwy z listy `nazwy` (gracze obecni na serwerze), identyfikatory
-- GUID i długie liczby (UserId, numery assetów). Krótkie liczby — numery linii — zostają.
function Agregator.bez_danych_gracza(komunikat, nazwy)
	local tekst = tostring(komunikat)
	if #tekst > 600 then
		tekst = string.sub(tekst, 1, 600)
	end
	tekst = string.gsub(tekst, "%c+", " ")
	if type(nazwy) == "table" then
		for _, nazwa in ipairs(nazwy) do
			if type(nazwa) == "string" and #nazwa >= 3 then
				-- granice słowa, żeby gracz „Server” nie zamazał „ServerScriptService”
				local przed, po = "", ""
				if string.find(nazwa, "^[%w_]") then
					przed = "%f[%w_]"
				end
				if string.find(nazwa, "[%w_]$") then
					po = "%f[^%w_]"
				end
				local wzor = przed .. string.gsub(nazwa, ZNAKI_WZORCA, "%%%0") .. po
				tekst = string.gsub(tekst, wzor, "<gracz>")
			end
		end
	end
	tekst = string.gsub(tekst, WZOR_GUID, "<id>")
	tekst = string.gsub(tekst, "%d%d%d%d%d+", "<n>")
	return tekst
end

-- Sygnatura błędu: 8 znaków szesnastkowych. Ten sam błąd w tej samej linii daje tę samą sygnaturę, nawet gdy
-- w komunikacie zmieniają się liczby (np. „indeks 7” i „indeks 9”). Podaj tekst po bez_danych_gracza().
function Agregator.sygnatura(tekst)
	local czysty = tostring(tekst)
	if #czysty > 300 then
		czysty = string.sub(czysty, 1, 300)
	end
	local linia = string.match(czysty, ":(%d+)") or ""
	local wzorzec = string.gsub(czysty, "%d+", "#") .. "|" .. linia
	local skrot = 5381
	for i = 1, #wzorzec do
		skrot = (skrot * 33 + string.byte(wzorzec, i)) % 4294967296
	end
	return string.format("%08x", skrot)
end

-- Nazwa przedziału długości sesji (w minutach): do_1, do_5, do_15, do_30, do_60, ponad_60.
function Agregator.przedzial_sesji(sekundy)
	local s = nieujemna(sekundy)
	for _, przedzial in ipairs(PRZEDZIALY_SESJI) do
		if s < przedzial[1] then
			return przedzial[2]
		end
	end
	return "ponad_60"
end

-- --------------------------------------------------------------------------- kubełki
function Agregator.pusty_kubelek(t)
	return {
		wersja = Agregator.WERSJA,
		t = t,
		zaktualizowano = 0,
		serwery = 0,
		zapisy = 0,
		starty = 0,
		sesje = 0,
		sesje_zakonczone = 0,
		sekundy_gry = 0,
		ccu_max = 0,
		ccu_suma = 0,
		ccu_probki = 0,
		ccu_minuty = puste_minuty(),
		robuxy = 0,
		bledy_n = 0,
		dlugosci = {},
		zakupy = {},
		bledy = {},
		zdarzenia = {},
		lejek = {},
		zamkniecia = {},
	}
end

-- Zostawia w słowniku `limit` wpisów o największej wadze (pole n albo sama liczba); resztę sumuje pod kluczem
-- "_inne", żeby sumy się zgadzały. Zwraca, ile wpisów przeniesiono.
function Agregator.przytnij(slownik, limit)
	local klucze = {}
	for klucz in pairs(slownik) do
		if klucz ~= Agregator.INNE then
			klucze[#klucze + 1] = klucz
		end
	end
	if #klucze <= limit then
		return 0
	end
	table.sort(klucze, function(a, b)
		local wa, wb = waga(slownik[a]), waga(slownik[b])
		if wa ~= wb then
			return wa > wb
		end
		return tostring(a) < tostring(b)
	end)
	local inne = slownik[Agregator.INNE]
	for i = limit + 1, #klucze do
		local wpis = slownik[klucze[i]]
		if type(wpis) == "table" then
			if type(inne) ~= "table" then
				inne = {}
			end
			for pole, wartosc in pairs(wpis) do
				if type(wartosc) == "number" then
					inne[pole] = nieujemna(inne[pole]) + nieujemna(wartosc)
				end
			end
		else
			inne = waga(inne) + nieujemna(wpis)
		end
		slownik[klucze[i]] = nil
	end
	slownik[Agregator.INNE] = inne
	return #klucze - limit
end

function Agregator.przytnij_kubelek(kubelek)
	Agregator.przytnij(kubelek.zakupy, Agregator.LIMITY.zakupy)
	Agregator.przytnij(kubelek.bledy, Agregator.LIMITY.bledy)
	Agregator.przytnij(kubelek.zdarzenia, Agregator.LIMITY.zdarzenia)
	Agregator.przytnij(kubelek.lejek, Agregator.LIMITY.lejek)
end

local function dolicz_kubelek(wynik, kubelek)
	if type(kubelek) ~= "table" then
		return
	end
	for _, pole in ipairs(POLA_SUMOWANE) do
		wynik[pole] = wynik[pole] + nieujemna(kubelek[pole])
	end
	wynik.ccu_max = math.max(wynik.ccu_max, nieujemna(kubelek.ccu_max))
	wynik.zaktualizowano = math.max(wynik.zaktualizowano, nieujemna(kubelek.zaktualizowano))
	wynik.wersja = math.max(wynik.wersja, nieujemna(kubelek.wersja))
	if wynik.t == 0 then
		wynik.t = nieujemna(kubelek.t)
	end
	if type(kubelek.ccu_minuty) == "table" then
		for i = 1, 60 do
			wynik.ccu_minuty[i] = wynik.ccu_minuty[i] + nieujemna(kubelek.ccu_minuty[i])
		end
	end
	for _, nazwa in ipairs(SLOWNIKI) do
		local zrodlo = kubelek[nazwa]
		if type(zrodlo) == "table" then
			for klucz, wpis in pairs(zrodlo) do
				if type(klucz) == "string" then
					dolicz_wpis(wynik[nazwa], klucz, wpis)
				end
			end
		end
	end
	-- pola, których ta wersja nie zna (zapisane przez nowszą wersję modułu), przechodzą bez zmian
	for pole, wartosc in pairs(kubelek) do
		if wynik[pole] == nil then
			wynik[pole] = wartosc
		end
	end
end

-- Scala kubełek zapisany w Data Store (`stary`, może być nil albo uszkodzony) z przyrostem (`delta`).
-- Niczego nie zmienia w argumentach — UpdateAsync może wywołać tę funkcję kilka razy dla tego samego przyrostu.
function Agregator.scal(stary, delta)
	local wynik = Agregator.pusty_kubelek(0)
	dolicz_kubelek(wynik, stary)
	dolicz_kubelek(wynik, delta)
	Agregator.przytnij_kubelek(wynik)
	return wynik
end

-- Wpis "stan" w Data Store: znak dla panelu, że moduł był włączony (i kiedy ostatnio wystartował serwer).
function Agregator.scal_stan(stary, teraz)
	local wynik = { wersja = Agregator.WERSJA, pierwszy_start = teraz, ostatni_start = teraz, starty = 1 }
	if type(stary) == "table" then
		local pierwszy = nieujemna(stary.pierwszy_start)
		if pierwszy > 0 and pierwszy < teraz then
			wynik.pierwszy_start = pierwszy
		end
		wynik.ostatni_start = math.max(teraz, nieujemna(stary.ostatni_start))
		wynik.starty = nieujemna(stary.starty) + 1
		wynik.wersja = math.max(wynik.wersja, nieujemna(stary.wersja))
	end
	return wynik
end

-- --------------------------------------------------------------------------- agregator jednego serwera
-- zegar: funkcja zwracająca sekundy Unix (UTC), np. os.time.
function Agregator.nowy(zegar)
	if type(zegar) ~= "function" then
		error("Agregator.nowy: podaj zegar — funkcję zwracającą sekundy Unix (np. os.time)")
	end
	local self = setmetatable({}, Agregator)
	self._zegar = zegar
	self._oczekujace = {} -- klucz godziny → kubełek z przyrostami, których jeszcze nie zapisano
	self._zgloszone = {} -- klucz godziny → true, gdy ten serwer policzył się już w polu „serwery”
	self._ostatnia_minuta = -1 -- minuta (licząc od 1970 r.) ostatniej próbki graczy
	self.utracone_godziny = 0 -- ile godzin danych porzucono, bo zapis nie działał dłużej niż 48 h
	return self
end

function Agregator:_przytnij_oczekujace()
	local klucze = {}
	for klucz in pairs(self._oczekujace) do
		klucze[#klucze + 1] = klucz
	end
	local limit = Agregator.LIMITY.godziny_w_pamieci
	if #klucze <= limit then
		return
	end
	table.sort(klucze)
	for i = 1, #klucze - limit do
		self._oczekujace[klucze[i]] = nil -- najstarsze godziny
		self.utracone_godziny = self.utracone_godziny + 1
	end
end

-- Kubełek przyrostów dla godziny, w której leży chwila `t` (tworzony przy pierwszym zdarzeniu).
function Agregator:_kubelek(t)
	local poczatek = Agregator.godzina(t)
	local klucz = Agregator.klucz_godziny(poczatek)
	local kubelek = self._oczekujace[klucz]
	if kubelek == nil then
		kubelek = Agregator.pusty_kubelek(poczatek)
		if not self._zgloszone[klucz] then
			self._zgloszone[klucz] = true
			kubelek.serwery = 1
		end
		self._oczekujace[klucz] = kubelek
		self:_przytnij_oczekujace()
	end
	if t > kubelek.zaktualizowano then
		kubelek.zaktualizowano = t
	end
	return kubelek
end

-- Start serwera (raz na życie serwera).
function Agregator:start_serwera()
	local kubelek = self:_kubelek(self._zegar())
	kubelek.starty += 1
end

-- Gracz wszedł na serwer.
function Agregator:sesja_start()
	local kubelek = self:_kubelek(self._zegar())
	kubelek.sesje += 1
end

-- Gracz wyszedł po `sekundy` sekundach gry.
function Agregator:sesja_koniec(sekundy)
	local kubelek = self:_kubelek(self._zegar())
	local dlugosc = nieujemna(sekundy)
	kubelek.sesje_zakonczone += 1
	kubelek.sekundy_gry += dlugosc
	local przedzial = Agregator.przedzial_sesji(dlugosc)
	kubelek.dlugosci[przedzial] = nieujemna(kubelek.dlugosci[przedzial]) + 1
end

-- Próbka liczby graczy na serwerze. Do średniej i do minut liczy się jedna próbka na minutę zegarową.
function Agregator:probka_ccu(gracze)
	local t = self._zegar()
	local kubelek = self:_kubelek(t)
	local n = math.floor(nieujemna(gracze))
	if n > kubelek.ccu_max then
		kubelek.ccu_max = n
	end
	local minuta = math.floor(t / 60)
	if minuta > self._ostatnia_minuta then
		self._ostatnia_minuta = minuta
		kubelek.ccu_suma += n
		kubelek.ccu_probki += 1
		local indeks = minuta % 60 + 1
		kubelek.ccu_minuty[indeks] += n
	end
end

-- Zakup za Robuxy. Nie zapisujemy, kto kupił — tylko co i za ile.
function Agregator:zakup(idProduktu, robuxy, nazwa)
	local kubelek = self:_kubelek(self._zegar())
	local kwota = nieujemna(robuxy)
	local klucz = Agregator.klucz_tekstowy(idProduktu)
	kubelek.robuxy += kwota
	local wpis = kubelek.zakupy[klucz]
	if wpis == nil then
		wpis = { n = 0, robuxy = 0, nazwa = "" }
		kubelek.zakupy[klucz] = wpis
	end
	wpis.n += 1
	wpis.robuxy += kwota
	if nazwa ~= nil and wpis.nazwa == "" then
		wpis.nazwa = Agregator.oczysc_tekst(nazwa, Agregator.LIMITY.nazwa)
	end
end

-- Błąd skryptu. `nazwy` to lista nazw graczy do usunięcia z komunikatu. Zwraca sygnaturę błędu.
function Agregator:blad(komunikat, nazwy)
	local kubelek = self:_kubelek(self._zegar())
	local tekst = Agregator.bez_danych_gracza(komunikat, nazwy)
	local sygnatura = Agregator.sygnatura(tekst)
	kubelek.bledy_n += 1
	local wpis = kubelek.bledy[sygnatura]
	if wpis ~= nil then
		wpis.n += 1
	else
		kubelek.bledy[sygnatura] = { n = 1, komunikat = Agregator.oczysc_tekst(tekst, Agregator.LIMITY.komunikat) }
		-- lawina różnych błędów nie może rozdąć pamięci serwera między zapisami
		Agregator.przytnij(kubelek.bledy, Agregator.LIMITY.bledy * 2)
	end
	return sygnatura
end

-- Błąd liczony bez treści (gdy w tej minucie było ich już za dużo, żeby każdy analizować).
function Agregator:blad_bez_tresci()
	local kubelek = self:_kubelek(self._zegar())
	kubelek.bledy_n += 1
	local wpis = kubelek.bledy[Agregator.INNE]
	if type(wpis) ~= "table" then
		wpis = { n = 0 }
		kubelek.bledy[Agregator.INNE] = wpis
	end
	wpis.n = nieujemna(wpis.n) + 1
end

-- Własne zdarzenie gry: licznik (wartosc pominięta = 1) albo suma wartości.
function Agregator:zdarzenie(nazwa, wartosc)
	local kubelek = self:_kubelek(self._zegar())
	local klucz = Agregator.klucz_tekstowy(nazwa)
	local przyrost = 1
	if wartosc ~= nil then
		przyrost = nieujemna(wartosc)
	end
	local nowy = kubelek.zdarzenia[klucz] == nil
	kubelek.zdarzenia[klucz] = waga(kubelek.zdarzenia[klucz]) + przyrost
	if nowy then
		Agregator.przytnij(kubelek.zdarzenia, Agregator.LIMITY.zdarzenia * 2)
	end
end

-- Krok lejka (1–100). Zwraca false, gdy numer kroku jest spoza zakresu.
function Agregator:lejek(krok, nazwa)
	local numer = liczba(krok, 0)
	if numer ~= math.floor(numer) or numer < 1 or numer > Agregator.LIMITY.lejek then
		return false
	end
	local kubelek = self:_kubelek(self._zegar())
	local klucz = string.format("%d", numer)
	local wpis = kubelek.lejek[klucz]
	if wpis == nil then
		wpis = { n = 0, nazwa = "" }
		kubelek.lejek[klucz] = wpis
	end
	wpis.n += 1
	if nazwa ~= nil and wpis.nazwa == "" then
		wpis.nazwa = Agregator.oczysc_tekst(nazwa, Agregator.LIMITY.nazwa)
	end
	return true
end

-- Serwer się zamyka; `powod` to nazwa z Enum.CloseReason (np. "ServerEmpty", "OutOfMemory").
function Agregator:zamkniecie(powod)
	local kubelek = self:_kubelek(self._zegar())
	local klucz = Agregator.klucz_tekstowy(powod or "Unknown")
	kubelek.zamkniecia[klucz] = nieujemna(kubelek.zamkniecia[klucz]) + 1
end

-- Czy jest coś do zapisania.
function Agregator:ma_dane()
	return next(self._oczekujace) ~= nil
end

-- Zdejmuje wszystkie oczekujące przyrosty do zapisu: lista { klucz = "g_…", kubelek = {…} } od najstarszej godziny.
-- Po udanym zapisie nic więcej nie trzeba robić; po nieudanym oddaj je przez oddaj().
function Agregator:zdejmij()
	local partie = {}
	for klucz, kubelek in pairs(self._oczekujace) do
		Agregator.przytnij_kubelek(kubelek)
		kubelek.zapisy = 1
		partie[#partie + 1] = { klucz = klucz, kubelek = kubelek }
	end
	table.sort(partie, function(a, b)
		return a.klucz < b.klucz
	end)
	self._oczekujace = {}
	return partie
end

-- Przyjmuje z powrotem przyrost, którego nie udało się zapisać (trafi do następnego zapisu).
function Agregator:oddaj(klucz, kubelek)
	local obecny = self._oczekujace[klucz]
	if obecny == nil then
		self._oczekujace[klucz] = kubelek
	else
		self._oczekujace[klucz] = Agregator.scal(kubelek, obecny)
	end
	self:_przytnij_oczekujace()
end

return Agregator
