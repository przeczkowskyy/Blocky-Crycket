--[[
	Statystyki — sprawdzanie opisu postaci i przeliczenie sześciu statystyk na wartości bojowe (silnik walki v2).
	Czysty moduł. Te same wzory przechodzą gracz i postać-przeciwnik (Arena, test lustrzany klasa na klasę).
	Port w Pythonie: tools/walka/silnik.py, sekcja Statystyki.luau (te same nazwy funkcji).

	Opis postaci (wejście):
		{
			nazwa = "Karol"?,                       -- opcjonalnie; domyślnie nazwa klasy
			klasa = "wojownik" | "zwiadowca" | "mag",
			poziom = 1..,                           -- liczba całkowita
			statystyki = { sila, kondycja, inteligencja, zrecznosc, szczescie, pancerz },  -- punkty, >= 0
			bron = { obrazenia = > 0, zaklecie = "trucizna" | "podpalenie" | nil },
			pancerz_przedmiotow = >= 0 | nil,       -- Pancerz z założonych przedmiotów (punkty)
			tarcza = { blok = 0..blok_maks } | nil, -- tylko Wojownik; stała szansa bloku z przedmiotu (D-062)
			umiejetnosci = { "ciecie", ... } | nil, -- 0–3 sloty, w kolejności slotów, tylko umiejętności klasy (D-055)
			pasywki = { sila = 0.05, ... } | nil,   -- premie procentowe z drzewka (ułamki)
			pet = { kondycja = 0.03, ... } | nil,   -- pet tylko mnoży statystyki, nie walczy (D-059)
		}

	Wzory (liczby w Dane.stale, do strojenia):
		statystyka efektywna = zaokrąglij(punkty × (1 + pasywka) × (1 + premia peta))
		polowa      = polowa_baza + polowa_na_poziom × poziom      -- ile punktów daje połowę drogi do limitu
		życie       = mnożnik życia klasy × (zycie_baza + zycie_na_poziom × poziom + zycie_za_kondycje × Kondycja)
		cios        = mnożnik ciosu klasy × (obrażenia broni + sila_za_punkt × Siła)   -- także zwykły atak Maga (magiczny)
		Pancerz     = pancerz_za_punkt × Pancerz + Pancerz z przedmiotów             -- punkty odejmowane od ciosu fizycznego
		odporność   = odpornosc_za_inteligencje × Inteligencja                     -- punkty odejmowane od ciosu magicznego
		unik        = unik_baza + (unik_limit − unik_baza) × Zręczność / (Zręczność + polowa)   -- limit zależy od klasy
		krytyk      = krytyk_baza + (krytyk_limit − krytyk_baza) × Szczęście / (Szczęście + polowa)
		moc umiej.  = 1 + moc_maks × Inteligencja / (Inteligencja + polowa)
		blok        = szansa bloku tarczy (0 bez tarczy)
]]

local Dane = require(script.Parent.Dane)
local Los = require(script.Parent.Los)

local Statystyki = {}

-- nazwy atrybutów gracza w dzisiejszym kodzie (src/server/StatPoints.server.luau) → nazwy w silniku walki
Statystyki.ATRYBUTY_GRACZA = {
	Strength = "sila",
	Constitution = "kondycja",
	Intelligence = "inteligencja",
	Dexterity = "zrecznosc",
	Luck = "szczescie",
	Armor = "pancerz",
}

local STALE = Dane.stale

local function sprawdzPremie(premie: any, co: string, strona: string)
	if premie == nil then
		return
	end
	if type(premie) ~= "table" then
		Los.blad(co .. " strony " .. strona .. " muszą być tabelą")
	end
	for klucz, wartosc in premie do
		if not table.find(Dane.statystyki, klucz) then
			Los.blad(co .. " strony " .. strona .. ": nieznana statystyka " .. tostring(klucz))
		end
		if not Los.liczba(wartosc) or wartosc < 0 or wartosc > STALE.premia_maks then
			Los.blad(co .. " strony " .. strona .. ": zła wartość dla " .. tostring(klucz))
		end
	end
end

function Statystyki.sprawdzPostac(p: any, strona: string)
	if type(p) ~= "table" then
		Los.blad("brak opisu postaci strony " .. strona)
	end
	local klasa = if type(p.klasa) == "string" then Dane.klasy[p.klasa] else nil
	if klasa == nil then
		Los.blad("nieznana klasa strony " .. strona)
	end
	local poziom = p.poziom
	if not Los.calkowita(poziom) or poziom < 1 or poziom > STALE.poziom_maks then
		Los.blad("zły poziom strony " .. strona)
	end
	local st = p.statystyki
	if type(st) ~= "table" then
		Los.blad("brak statystyk strony " .. strona)
	end
	for _, nazwa in Dane.statystyki do
		local v = st[nazwa]
		if not Los.liczba(v) or v < 0 or v > STALE.statystyka_maks then
			Los.blad("zła statystyka " .. nazwa .. " strony " .. strona)
		end
	end
	for klucz in st do
		if not table.find(Dane.statystyki, klucz) then
			Los.blad("nieznana statystyka " .. tostring(klucz) .. " strony " .. strona)
		end
	end
	local bron = p.bron
	if type(bron) ~= "table" or not Los.liczba(bron.obrazenia) or bron.obrazenia <= 0 or bron.obrazenia > STALE.statystyka_maks then
		Los.blad("broń strony " .. strona .. " musi mieć dodatnie obrażenia")
	end
	local zaklecie = bron.zaklecie
	if zaklecie ~= nil and (type(zaklecie) ~= "string" or Dane.zaklecia[zaklecie] == nil) then
		Los.blad("nieznane zaklęcie broni strony " .. strona)
	end
	local pp = p.pancerz_przedmiotow
	if pp ~= nil and (not Los.liczba(pp) or pp < 0 or pp > STALE.statystyka_maks) then
		Los.blad("zły pancerz z przedmiotów strony " .. strona)
	end
	local tarcza = p.tarcza
	if tarcza ~= nil then
		if not klasa.tarcza then
			Los.blad("klasa " .. klasa.nazwa .. " nie nosi tarczy (strona " .. strona .. ")")
		end
		if type(tarcza) ~= "table" or not Los.liczba(tarcza.blok) or tarcza.blok < 0 or tarcza.blok > STALE.blok_maks then
			Los.blad("zła szansa bloku tarczy strony " .. strona)
		end
	end
	local um = p.umiejetnosci
	if um ~= nil then
		if type(um) ~= "table" then
			Los.blad("umiejętności strony " .. strona .. " muszą być listą")
		end
		-- lista = same klucze całkowite 1..n bez dziur (tabela { x = "kula_ognia" } ma #um == 0 i przeszłaby dalej);
		-- kolejność tej pętli nie ma znaczenia, bo tylko sprawdza klucze
		local ile = 0
		for klucz in um do
			ile += 1
			if type(klucz) ~= "number" or klucz < 1 or klucz > #um or math.floor(klucz) ~= klucz then
				Los.blad("umiejętności strony " .. strona .. " muszą być listą")
			end
		end
		if ile ~= #um then
			Los.blad("umiejętności strony " .. strona .. " muszą być listą")
		end
		if #um > STALE.maks_slotow then
			Los.blad("strona " .. strona .. " ma " .. #um .. " umiejętności, a slotów jest najwyżej " .. STALE.maks_slotow)
		end
		for i = 1, #um do
			local u = if type(um[i]) == "string" then Dane.umiejetnosci[um[i]] else nil
			if u == nil then
				Los.blad("nieznana umiejętność strony " .. strona)
			end
			if u.klasa ~= p.klasa then
				Los.blad("umiejętność " .. um[i] .. " nie należy do klasy strony " .. strona)
			end
			for j = 1, i - 1 do
				if um[j] == um[i] then
					Los.blad("umiejętność " .. um[i] .. " dwa razy u strony " .. strona)
				end
			end
		end
	end
	sprawdzPremie(p.pasywki, "pasywki", strona)
	sprawdzPremie(p.pet, "premie peta", strona)
	if p.nazwa ~= nil and type(p.nazwa) ~= "string" then
		Los.blad("nazwa strony " .. strona .. " musi być napisem")
	end
end

-- Sześć statystyk + przedmioty + pasywki + pet → wartości bojowe (te same wzory dla gracza i postaci-przeciwnika).
function Statystyki.wartosciPostaci(p: any)
	local klasa = Dane.klasy[p.klasa]
	local poziom = p.poziom
	local st = p.statystyki
	local pasywki = p.pasywki or {}
	local pet = p.pet or {}
	local e = {}
	for _, nazwa in Dane.statystyki do
		-- pasywki z drzewka i pet tylko mnożą statystyki (D-055, D-059)
		e[nazwa] = Los.zaokraglij(st[nazwa] * (1 + (pasywki[nazwa] or 0)) * (1 + (pet[nazwa] or 0)))
	end
	local polowa = STALE.polowa_baza + STALE.polowa_na_poziom * poziom
	local bron = p.bron
	local tarcza = p.tarcza
	local umiejetnosci = {}
	local um = p.umiejetnosci or {}
	for i = 1, #um do -- po indeksach, w kolejności slotów (sprawdzPostac pilnuje, że to lista)
		table.insert(umiejetnosci, um[i])
	end
	local zycie = Los.zaokraglij(
		klasa.mnoznik_zycia
			* (STALE.zycie_baza + STALE.zycie_na_poziom * poziom + STALE.zycie_za_kondycje * e.kondycja)
	)
	return {
		nazwa = if type(p.nazwa) == "string" and p.nazwa ~= "" then p.nazwa else klasa.nazwa,
		rodzaj = "postac",
		id = p.klasa,
		ranga = "gracz",
		poziom = poziom,
		zycie = math.max(1, zycie),
		cios = klasa.mnoznik_ciosu * (bron.obrazenia + STALE.sila_za_punkt * e.sila),
		rodzaj_ciosu = klasa.rodzaj_ciosu,
		pancerz = STALE.pancerz_za_punkt * e.pancerz + (p.pancerz_przedmiotow or 0),
		odpornosc = STALE.odpornosc_za_inteligencje * e.inteligencja,
		unik = klasa.unik_baza + (klasa.unik_limit - klasa.unik_baza) * Los.premia(e.zrecznosc, polowa),
		krytyk = STALE.krytyk_baza + (STALE.krytyk_limit - STALE.krytyk_baza) * Los.premia(e.szczescie, polowa),
		mnoznik_krytyka = klasa.mnoznik_krytyka,
		blok = if tarcza ~= nil then tarcza.blok else 0,
		moc = 1 + STALE.moc_maks * Los.premia(e.inteligencja, polowa),
		umiejetnosci = umiejetnosci,
		zaklecie = if type(bron.zaklecie) == "string" then bron.zaklecie else "",
		efektywne = e,
	}
end

return Statystyki
