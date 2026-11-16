--[[
	Statystyki — sprawdzanie opisu postaci i przeliczenie statystyk na wartości bojowe (silnik walki v3).
	Czysty moduł. TEN SAM WZÓR (Statystyki.bojowe) przechodzą gracz, postać-przeciwnik (Arena) i potwór.
	Port w Pythonie: tools/walka/silnik.py, sekcja Statystyki.luau (te same nazwy funkcji).

	Opis postaci (wejście):
		{
			nazwa = "Karol"?,                       -- opcjonalnie; domyślnie nazwa klasy
			klasa = "wojownik" | "zwiadowca" | "mag",
			poziom = 1..,                           -- liczba całkowita
			statystyki = { sila, kondycja, inteligencja, zrecznosc, szczescie, pancerz },  -- punkty, >= 0
			bron = { obrazenia = > 0, zaklecie = "trucizna" | "podpalenie" | nil, pasywka = id z Dane.pasywki_broni | nil },
			pancerz_przedmiotow = >= 0 | nil,       -- Pancerz z założonych przedmiotów (punkty)
			tarcza = { blok = 0..blok_maks } | nil, -- tylko Wojownik; szansa bloku z przedmiotu (D-062), dochodzi do bloku klasy
			umiejetnosci = { "ciecie", "kolos", ... } | nil,  -- 0–3 sloty w kolejności: aktywne (Dane.umiejetnosci)
			                                        -- i pasywne (Dane.pasywne) klasy, dowolna mieszanka
			premie = { zysk_many = 0.2, ... } | nil, -- modyfikatory z przedmiotów i węzłów drzewka (lista: Dane.modyfikatory)
			pasywki = { sila = 0.05, ... } | nil,   -- premie procentowe z drzewka do statystyk (ułamki)
			pet = { kondycja = 0.03, ... } | nil,   -- pet tylko mnoży statystyki, nie walczy (D-059)
		}
		Innych pól (także w bron i tarcza) nie ma — nieznane pole to błąd „Walka: nieznane pole …” (literówka nie
		przechodzi po cichu).

	Wzory (liczby w Dane.stale i Dane.klasy, do strojenia; m = suma modyfikatorów):
		statystyka efektywna = zaokrąglij(punkty × (1 + pasywka) × (1 + premia peta))
		polowa      = polowa_baza + polowa_na_poziom × poziom      -- ile punktów daje połowę drogi do limitu
		życie       = mnożnik życia klasy × (zycie_baza + zycie_na_poziom × poziom + zycie_za_kondycje × Kondycja) × (1 + m.zycie)
		cios        = mnożnik ciosu klasy × (obrażenia broni + sila_za_punkt × Siła) × (1 + m.cios)
		Pancerz     = mnożnik Pancerza klasy × (pancerz_za_punkt × Pancerz + Pancerz z przedmiotów) × (1 + m.pancerz)
		odporność   = mnożnik odporności klasy × odpornosc_za_inteligencje × Inteligencja × (1 + m.odpornosc)
		unik        = unik_baza + (unik_limit − unik_baza) × Zr / (Zr + polowa) + m.unik      (całość ≤ unik_maks)
		krytyk      = krytyk_baza + (krytyk_limit − krytyk_baza) × Sz / (Sz + polowa) + m.krytyk   (≤ krytyk_maks)
		mn. krytyka = mnożnik krytyka klasy + kryt_za_zrecznosc klasy × Zr / (Zr + polowa) + m.mnoznik_krytyka
		blok        = blok klasy + blok tarczy + m.blok                                   (całość ≤ blok_maks)
		moc umiej.  = 1 + moc_maks × Int / (Int + polowa) + m.moc
		mana        = pasek 0..mana_maks; zysk × (1 + m.zysk_many), koszt × (1 − m.koszt_many), start m.mana_startowa
	Mana NIE jest statystyką: to wartość pochodna z przedmiotów, drzewka i pasywek.
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

-- słownik id → opis modyfikatora, zbudowany z LISTY (lista niesie kolejność dodawania, słownik służy do szukania)
local MODYFIKATORY_PO_ID = {}
for _, spec in Dane.modyfikatory do
	MODYFIKATORY_PO_ID[spec.id] = spec
end

-- zamknięte listy pól wejścia (te same w tools/walka/silnik.py)
Statystyki.POLA_POSTACI = {
	"nazwa",
	"klasa",
	"poziom",
	"statystyki",
	"bron",
	"pancerz_przedmiotow",
	"tarcza",
	"umiejetnosci",
	"pasywki",
	"pet",
	"premie",
}
local POLA_BRONI = { "obrazenia", "zaklecie", "pasywka" }
local POLA_TARCZY = { "blok" }
Statystyki.POLA_PRZECIWNIKA = { "potwor", "poziom", "postac" }

-- zamknięta lista pól: literówka (np. "premia" zamiast "premie", "pasywki" w broni) nie może przejść po cichu —
-- bez tego postać walczyłaby bez przedmiotów albo slotów i nikt by tego nie zauważył (kontrola 16/17.11);
-- kolejność tej pętli zmienia najwyżej to, które z kilku złych pól trafi do komunikatu
function Statystyki.sprawdzKlucze(t: any, dozwolone, co: string, strona: string)
	for klucz in t do
		if not table.find(dozwolone, klucz) then
			Los.blad("nieznane pole " .. tostring(klucz) .. " w " .. co .. " strony " .. strona)
		end
	end
end

-- pasywki z drzewka i pet: procentowe premie do SZEŚCIU statystyk (D-055, D-059)
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

-- premie z przedmiotów i węzłów drzewka (sumuje je serwer): zamknięta lista kluczy z granicami z danych
local function sprawdzModyfikatory(mod: any, strona: string)
	if mod == nil then
		return
	end
	if type(mod) ~= "table" then
		Los.blad("premie strony " .. strona .. " muszą być tabelą")
	end
	for klucz, wartosc in mod do
		local spec = if type(klucz) == "string" then MODYFIKATORY_PO_ID[klucz] else nil
		if spec == nil then
			Los.blad("premie strony " .. strona .. ": nieznany modyfikator " .. tostring(klucz))
		end
		if not Los.liczba(wartosc) or wartosc < spec.min or wartosc > spec.max then
			Los.blad("premie strony " .. strona .. ": zła wartość dla " .. tostring(klucz))
		end
	end
end

function Statystyki.sprawdzPostac(p: any, strona: string)
	if type(p) ~= "table" then
		Los.blad("brak opisu postaci strony " .. strona)
	end
	Statystyki.sprawdzKlucze(p, Statystyki.POLA_POSTACI, "opisie postaci", strona)
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
	Statystyki.sprawdzKlucze(bron, POLA_BRONI, "broni", strona)
	local zaklecie = bron.zaklecie
	if zaklecie ~= nil and (type(zaklecie) ~= "string" or Dane.zaklecia[zaklecie] == nil) then
		Los.blad("nieznane zaklęcie broni strony " .. strona)
	end
	local pb = bron.pasywka
	if pb ~= nil then
		local d = if type(pb) == "string" then Dane.pasywki_broni[pb] else nil
		if d == nil then
			Los.blad("nieznana pasywka broni strony " .. strona)
		end
		if d.klasa ~= "" and d.klasa ~= p.klasa then
			Los.blad("pasywka broni " .. pb .. " nie pasuje do klasy strony " .. strona)
		end
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
		Statystyki.sprawdzKlucze(tarcza, POLA_TARCZY, "tarczy", strona)
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
			-- slot = umiejętność aktywna ALBO pasywna klasy (3 aktywne, 3 pasywne albo dowolna mieszanka)
			local u = nil
			if type(um[i]) == "string" then
				u = Dane.umiejetnosci[um[i]]
				if u == nil then
					u = Dane.pasywne[um[i]]
				end
			end
			if u == nil then
				Los.blad("nieznana umiejętność strony " .. strona)
			end
			if u.klasa ~= "" and u.klasa ~= p.klasa then
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
	sprawdzModyfikatory(p.premie, strona)
	if p.nazwa ~= nil and type(p.nazwa) ~= "string" then
		Los.blad("nazwa strony " .. strona .. " musi być napisem")
	end
end

-- Suma modyfikatorów z kolejnych źródeł (premie, pasywka broni, pasywki w slotach — w tej kolejności), liczona po
-- LIŚCIE kluczy z danych (ta sama kolejność dodawania w obu portach), przycięta do granic z danych.
function Statystyki.zbierzModyfikatory(zrodla)
	local m = {}
	for _, spec in Dane.modyfikatory do
		local s = 0
		for _, z in zrodla do
			local v = z[spec.id]
			if v ~= nil then
				s = s + v
			end
		end
		m[spec.id] = Los.miedzy(s, spec.min, spec.max)
	end
	return m
end

-- sloty w kolejności: aktywne idą do rotacji many, pasywne dają stałe modyfikatory
function Statystyki.podzielUmiejetnosci(um)
	local lista, aktywne, pasywne = {}, {}, {}
	for i = 1, #um do
		table.insert(lista, um[i])
		if Dane.pasywne[um[i]] ~= nil then
			table.insert(pasywne, um[i])
		else
			table.insert(aktywne, um[i])
		end
	end
	return lista, aktywne, pasywne
end

-- Wspólny wzór dla gracza, postaci-przeciwnika i potwora: efektywne statystyki + przedmioty + modyfikatory →
-- wartości bojowe. `zrodla` to lista tabel modyfikatorów (bez pasywek ze slotów — te dokładamy tu).
function Statystyki.bojowe(
	klasa,
	poziom: number,
	e,
	obrazeniaBroni: number,
	zaklecie: string,
	pancerzPrzedmiotow: number,
	blokTarczy: number,
	zrodla,
	um
)
	local lista, aktywne, pasywne = Statystyki.podzielUmiejetnosci(um)
	local wszystkie = {}
	for _, z in zrodla do
		table.insert(wszystkie, z)
	end
	for _, u in pasywne do
		table.insert(wszystkie, Dane.pasywne[u].modyfikatory)
	end
	local m = Statystyki.zbierzModyfikatory(wszystkie)
	-- wskrzeszenie (legendarna pasywka, propozycja D-094) — TYLKO ze slotu: nie ma go wśród modyfikatorów,
	-- więc nie da go ani pasywka broni, ani premia z przedmiotów czy drzewka
	local wsk = 0
	for _, u in pasywne do
		wsk = math.max(wsk, Dane.pasywne[u].wskrzeszenie)
	end
	local polowa = STALE.polowa_baza + STALE.polowa_na_poziom * poziom
	local zycie = Los.zaokraglij(
		klasa.mnoznik_zycia
			* (STALE.zycie_baza + STALE.zycie_na_poziom * poziom + STALE.zycie_za_kondycje * e.kondycja)
			* (1 + m.zycie)
	)
	local pZr = Los.premia(e.zrecznosc, polowa)
	local zysk = 1 + m.zysk_many + STALE.mana_premia_za_aktywna * math.max(0, #aktywne - 1)
	return {
		zycie = math.max(1, zycie),
		cios = klasa.mnoznik_ciosu * (obrazeniaBroni + STALE.sila_za_punkt * e.sila) * (1 + m.cios),
		cios_zwykly = math.max(0, 1 + m.cios_zwykly),
		rodzaj_ciosu = klasa.rodzaj_ciosu,
		pancerz = klasa.mnoznik_pancerza
			* (STALE.pancerz_za_punkt * e.pancerz + pancerzPrzedmiotow)
			* (1 + m.pancerz),
		odpornosc = klasa.mnoznik_odpornosci * STALE.odpornosc_za_inteligencje * e.inteligencja * (1 + m.odpornosc),
		unik = Los.miedzy(klasa.unik_baza + (klasa.unik_limit - klasa.unik_baza) * pZr + m.unik, 0, STALE.unik_maks),
		krytyk = Los.miedzy(
			STALE.krytyk_baza + (STALE.krytyk_limit - STALE.krytyk_baza) * Los.premia(e.szczescie, polowa) + m.krytyk,
			0,
			STALE.krytyk_maks
		),
		mnoznik_krytyka = math.max(1, klasa.mnoznik_krytyka + klasa.kryt_za_zrecznosc * pZr + m.mnoznik_krytyka),
		blok = Los.miedzy(klasa.blok + blokTarczy + m.blok, 0, STALE.blok_maks),
		moc = math.max(0, 1 + STALE.moc_maks * Los.premia(e.inteligencja, polowa) + m.moc),
		umiejetnosci = lista,
		aktywne = aktywne,
		pasywne = pasywne,
		zaklecie = zaklecie,
		zysk_many = math.max(0, zysk),
		koszt_many = m.koszt_many,
		mana_start = Los.miedzy(Los.zaokraglij(m.mana_startowa), 0, STALE.mana_maks),
		wskrzeszenie = wsk,
		mod = m,
		efektywne = e,
	}
end

-- Sześć statystyk + przedmioty + pasywki + pet + premie → wartości bojowe (gracz i postać-przeciwnik).
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
	local bron = p.bron
	local tarcza = p.tarcza
	local zrodla = {}
	if p.premie ~= nil then
		table.insert(zrodla, p.premie)
	end
	if bron.pasywka ~= nil then
		table.insert(zrodla, Dane.pasywki_broni[bron.pasywka].modyfikatory)
	end
	local um = {}
	local wejscie = p.umiejetnosci or {}
	for i = 1, #wejscie do -- po indeksach, w kolejności slotów (sprawdzPostac pilnuje, że to lista)
		table.insert(um, wejscie[i])
	end
	local w = Statystyki.bojowe(
		klasa,
		poziom,
		e,
		bron.obrazenia,
		if type(bron.zaklecie) == "string" then bron.zaklecie else "",
		p.pancerz_przedmiotow or 0,
		if tarcza ~= nil then tarcza.blok else 0,
		zrodla,
		um
	)
	w.nazwa = if type(p.nazwa) == "string" and p.nazwa ~= "" then p.nazwa else klasa.nazwa
	w.rodzaj = "postac"
	w.id = p.klasa
	w.ranga = "gracz"
	w.poziom = poziom
	return w
end

return Statystyki
