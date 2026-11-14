--[[
	Dziennik — format dziennika walki v2 i jego niezmienniki (ReplicatedStorage.Shared.Walka.Dziennik).
	Czysty moduł bez zależności: używa go klient (zanim zacznie odtwarzać walkę) i testy silnika.
	Port w Pythonie: tools/walka/dziennik.py (ta sama funkcja sprawdz).

	Walka (z serwera, Silnik.symuluj):
		wersja = 2, ziarno, tury, bezpiecznik, wynik = "wygrana" | "przegrana" (z punktu widzenia gracza),
		strony = { gracz = { nazwa, rodzaj = "postac", id = klasa, ranga = "gracz", poziom, zycie },
		           wrog  = { nazwa, rodzaj = "potwor" | "postac", id, ranga = "zwykly" | "rzadki" | "straznik" | "gracz", poziom, zycie } },
		dziennik = { zdarzenie, ... },
		lup = { zloto, doswiadczenie, tokeny_krainy, gemy, shard_ewolucji, kraina },   -- bez jajek (D-060)
		czas_wstepu, czas_finalu, czas   -- sekundy; czas = czas_wstepu + suma „trwa” wszystkich zdarzeń + czas_finalu

	Zdarzenie (każde ma wszystkie pola):
		typ          — "cios" | "krytyk" | "blok" | "unik" | "umiejetnosc" | "efekt_tick" | "efekt_nalozony"
		               | "efekt_koniec" | "utrata_tury"
		kto          — strona, która działa ("gracz" | "wrog"); przy tyknięciu, końcu efektu i utracie tury: nosiciel
		cel          — strona, która przyjmuje skutek (przy umiejętności na siebie: ta sama co kto)
		obrazenia    — ile życia stracił cel (0 przy uniku); pochloniete — ile przyjęła tarcza pochłaniająca
		rodzaj       — "fizyczne" | "magiczne" przy obrażeniach (do animacji trafienia), inaczej ""
		umiejetnosc  — identyfikator umiejętności: przy typie "umiejetnosc" (trafienie) oraz przy "unik" i "blok",
		               gdy uniknięto albo zablokowano umiejętność; przy zwykłym ciosie ""
		efekt        — identyfikator efektu (typy efekt_*), inaczej ""
		krytyk       — true przy krytyku (także krytyczna umiejętność)
		wartosc, tury — przy nałożeniu efektu: siła (obrażenia tyknięcia, pojemność tarczy albo procent) i czas w turach
		hp_gracz, hp_wrog — życie OBU stron po zdarzeniu
		t, trwa      — początek zdarzenia i jego naturalny czas w sekundach (setne części)
]]

local Dziennik = {}

Dziennik.WERSJA = 2
Dziennik.TYPY = {
	"cios",
	"krytyk",
	"blok",
	"unik",
	"umiejetnosc",
	"efekt_tick",
	"efekt_nalozony",
	"efekt_koniec",
	"utrata_tury",
}
Dziennik.RANGI = { "gracz", "zwykly", "rzadki", "straznik" }
Dziennik.POLA_LUPU = { "zloto", "doswiadczenie", "tokeny_krainy", "gemy", "shard_ewolucji" }

local function calkowita(v: any): boolean
	return type(v) == "number" and v == v and v ~= math.huge and v ~= -math.huge and math.floor(v) == v
end

local function setne(x: number): number
	return math.floor(x * 100 + 0.5)
end

local function jestW(lista, v): boolean
	return table.find(lista, v) ~= nil
end

local function inna(strona: string): string
	return if strona == "gracz" then "wrog" else "gracz"
end

-- sprawdz(walka) → true albo (false, opis błędu)
function Dziennik.sprawdz(walka: any): (boolean, string?)
	if type(walka) ~= "table" or walka.wersja ~= Dziennik.WERSJA then
		return false, "brak walki albo zła wersja"
	end
	if type(walka.strony) ~= "table" or type(walka.dziennik) ~= "table" or type(walka.lup) ~= "table" then
		return false, "brak stron, dziennika albo łupu"
	end
	local hp = {}
	for _, strona in { "gracz", "wrog" } do
		local s = walka.strony[strona]
		if type(s) ~= "table" or not calkowita(s.zycie) or s.zycie < 1 then
			return false, "zła strona " .. strona
		end
		if not jestW(Dziennik.RANGI, s.ranga) or (s.rodzaj ~= "postac" and s.rodzaj ~= "potwor") then
			return false, "zła ranga albo rodzaj strony " .. strona
		end
		hp[strona] = s.zycie
	end
	if walka.strony.gracz.rodzaj ~= "postac" then
		return false, "gracz musi być postacią"
	end
	if type(walka.czas_wstepu) ~= "number" or type(walka.czas_finalu) ~= "number" or type(walka.czas) ~= "number" then
		return false, "brak czasów"
	end
	local n = #walka.dziennik
	if n < 1 then
		return false, "pusty dziennik"
	end
	local aktywne = { gracz = {}, wrog = {} }
	local t = setne(walka.czas_wstepu)
	for i = 1, n do
		local z = walka.dziennik[i]
		local gdzie = "zdarzenie " .. i .. ": "
		if type(z) ~= "table" or not jestW(Dziennik.TYPY, z.typ) then
			return false, gdzie .. "nieznany typ"
		end
		if (z.kto ~= "gracz" and z.kto ~= "wrog") or (z.cel ~= "gracz" and z.cel ~= "wrog") then
			return false, gdzie .. "zła strona"
		end
		if not calkowita(z.obrazenia) or z.obrazenia < 0 or not calkowita(z.pochloniete) or z.pochloniete < 0 then
			return false, gdzie .. "złe obrażenia"
		end
		if type(z.rodzaj) ~= "string" or type(z.umiejetnosc) ~= "string" or type(z.efekt) ~= "string" then
			return false, gdzie .. "brak pól opisu"
		end
		if type(z.krytyk) ~= "boolean" or type(z.wartosc) ~= "number" or z.wartosc < 0 or not calkowita(z.tury) or z.tury < 0 then
			return false, gdzie .. "złe pola krytyk / wartosc / tury"
		end
		local zwykly = z.typ == "cios" or z.typ == "krytyk" or z.typ == "blok" or z.typ == "unik"
		if zwykly and z.cel ~= inna(z.kto) then
			return false, gdzie .. "zwykły cios musi trafiać w drugą stronę"
		end
		if zwykly and z.krytyk ~= (z.typ == "krytyk") then
			return false, gdzie .. "znacznik krytyka niezgodny z typem"
		end
		if z.typ == "unik" and (z.obrazenia ~= 0 or z.pochloniete ~= 0) then
			return false, gdzie .. "unik z obrażeniami"
		end
		if (z.typ == "cios" or z.typ == "krytyk") and z.umiejetnosc ~= "" then
			return false, gdzie .. "cios i krytyk nie niosą umiejętności (krytyczna umiejętność ma typ umiejetnosc)"
		end
		if (z.typ == "cios" or z.typ == "krytyk" or z.typ == "blok") and z.obrazenia + z.pochloniete < 1 then
			return false, gdzie .. "trafienie bez obrażeń (dolna granica to 1)"
		end
		if z.typ == "efekt_nalozony" or z.typ == "efekt_koniec" or z.typ == "utrata_tury" then
			if z.obrazenia ~= 0 or z.pochloniete ~= 0 then
				return false, gdzie .. "zdarzenie bez obrażeń ma obrażenia"
			end
		end
		if (z.typ == "efekt_tick" or z.typ == "efekt_koniec" or z.typ == "utrata_tury") and z.kto ~= z.cel then
			return false, gdzie .. "tyknięcie, koniec efektu i utrata tury dotyczą nosiciela"
		end
		if z.obrazenia + z.pochloniete > 0 and z.rodzaj ~= "fizyczne" and z.rodzaj ~= "magiczne" then
			return false, gdzie .. "obrażenia bez rodzaju"
		end
		if z.typ == "umiejetnosc" and z.umiejetnosc == "" then
			return false, gdzie .. "umiejętność bez identyfikatora"
		end
		if string.sub(z.typ, 1, 6) == "efekt_" then
			if z.efekt == "" then
				return false, gdzie .. "efekt bez identyfikatora"
			end
			if z.typ == "efekt_nalozony" then
				aktywne[z.cel][z.efekt] = true
			elseif not aktywne[z.cel][z.efekt] then
				return false, gdzie .. "tyknięcie albo koniec efektu, którego nie nałożono"
			elseif z.typ == "efekt_koniec" then
				aktywne[z.cel][z.efekt] = nil
			end
		end
		if z.typ == "utrata_tury" and next(aktywne[z.kto]) == nil then
			return false, gdzie .. "utrata tury bez efektu"
		end
		if type(z.t) ~= "number" or setne(z.t) ~= t then
			return false, gdzie .. "zły czas t (oczekiwano " .. (t / 100) .. ")"
		end
		if type(z.trwa) ~= "number" or setne(z.trwa) <= 0 then
			return false, gdzie .. "zły czas trwania"
		end
		t = t + setne(z.trwa)
		hp[z.cel] = math.max(0, hp[z.cel] - z.obrazenia)
		if z.hp_gracz ~= hp.gracz or z.hp_wrog ~= hp.wrog then
			return false, gdzie .. "życie po zdarzeniu niezgodne (oczekiwano " .. hp.gracz .. " / " .. hp.wrog .. ")"
		end
		if (hp.gracz == 0 or hp.wrog == 0) and i ~= n then
			return false, gdzie .. "walka trwa po nokaucie"
		end
	end
	if setne(walka.czas) ~= t + setne(walka.czas_finalu) then
		return false, "czas całości różny od sumy czasów zdarzeń"
	end
	if not calkowita(walka.tury) or walka.tury < 1 then
		return false, "zła liczba tur"
	end
	local G, W = walka.strony.gracz.zycie, walka.strony.wrog.zycie
	if walka.bezpiecznik == true then
		if hp.gracz == 0 or hp.wrog == 0 then
			return false, "bezpiecznik przy walce zakończonej nokautem"
		end
		local oczekiwany = if hp.gracz * W >= hp.wrog * G then "wygrana" else "przegrana"
		if walka.wynik ~= oczekiwany then
			return false, "wynik po bezpieczniku niezgodny z procentem życia"
		end
	elseif walka.bezpiecznik == false then
		if (hp.gracz == 0) == (hp.wrog == 0) then
			return false, "walka bez bezpiecznika musi skończyć się nokautem dokładnie jednej strony"
		end
		local oczekiwany = if hp.wrog == 0 then "wygrana" else "przegrana"
		if walka.wynik ~= oczekiwany then
			return false, "wynik niezgodny z dziennikiem"
		end
	else
		return false, "brak pola bezpiecznik"
	end
	local lup = walka.lup
	for klucz in lup do
		if string.find(string.lower(tostring(klucz)), "jaj", 1, true) then
			return false, "łup z jajkiem — jajka nie wypadają z potworów (D-060)"
		end
	end
	for _, pole in Dziennik.POLA_LUPU do
		if not calkowita(lup[pole]) or lup[pole] < 0 then
			return false, "złe pole łupu " .. pole
		end
	end
	if type(lup.kraina) ~= "string" then
		return false, "łup bez krainy"
	end
	if lup.shard_ewolucji > 0 and (walka.strony.wrog.ranga ~= "straznik" or walka.wynik ~= "wygrana") then
		return false, "Shard Ewolucji spoza wygranej ze strażnikiem biomu"
	end
	if walka.wynik == "przegrana" and (lup.zloto ~= 0 or lup.tokeny_krainy ~= 0 or lup.gemy ~= 0 or lup.shard_ewolucji ~= 0) then
		return false, "łup za przegraną"
	end
	return true, nil
end

return Dziennik
