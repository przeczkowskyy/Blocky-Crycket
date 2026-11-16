--[[
	Przeciwnicy — potwory biomów (na razie las) skalowane poziomem i łup po walce (silnik walki v3). Czysty moduł.
	Port w Pythonie: tools/walka/silnik.py, sekcja Przeciwnicy.luau. Dane potworów: Dane.przeciwnicy.

	Potwór jest opisany jak postać: ma KLASĘ (klasę gracza — zwiadowca, mag, wojownik — albo klasę tylko dla potworów
	z Dane.klasy_potworow, np. strażnik biomu), punkty sześciu statystyk, broń i Pancerz z przedmiotów (pary
	[baza, na_poziom]: wartość na poziomie L = baza + na_poziom × (L − 1)), szansę bloku tarczy, modyfikatory
	(np. więcej życia, słabsze ciosy) i umiejętności w slotach. Przechodzi przez TEN SAM wzór (Statystyki.bojowe),
	ataki, obronę i manę co postać gracza.
	Ranga ("zwykly", "rzadki", "straznik") to WYŁĄCZNIE informacja dla interfejsu i łupu: nie zmienia zasad walki.

	Łup (D-058, D-060, D-057): Złoto, doświadczenie, tokeny krainy, rzadko Gemy; Shard Ewolucji WYŁĄCZNIE ze strażnika
	biomu i z szansą. JAJEK Z POTWORÓW NIE MA (D-060) — łup nie ma nawet takiego pola.
]]

local Dane = require(script.Parent.Dane)
local Los = require(script.Parent.Los)
local Statystyki = require(script.Parent.Statystyki)

local Przeciwnicy = {}

local STALE = Dane.stale

-- słownik id → opis, zbudowany z listy (lista niesie kolejność dla interfejsu, słownik służy tylko do szukania)
local PO_ID = {}
for _, d in Dane.przeciwnicy do
	PO_ID[d.id] = d
end
Przeciwnicy.PO_ID = PO_ID

local function skala(para, poziom: number): number
	return para[1] + para[2] * (poziom - 1)
end
Przeciwnicy.skala = skala

-- potwór ma klasę gracza (zwiadowca, mag, wojownik) albo klasę tylko dla potworów (np. strażnik biomu)
local function klasaPotwora(d)
	local k = Dane.klasy[d.klasa]
	if k == nil then
		k = Dane.klasy_potworow[d.klasa]
	end
	return k
end

function Przeciwnicy.wartosciPotwora(identyfikator: string, poziom: number)
	local d = PO_ID[identyfikator]
	local e = {}
	for _, nazwa in Dane.statystyki do
		e[nazwa] = math.max(0, Los.zaokraglij(skala(d.statystyki[nazwa], poziom)))
	end
	local w = Statystyki.bojowe(
		klasaPotwora(d),
		poziom,
		e,
		skala(d.bron, poziom),
		"",
		skala(d.pancerz_przedmiotow, poziom),
		d.tarcza,
		{ d.modyfikatory },
		d.umiejetnosci
	)
	w.nazwa = d.nazwa
	w.rodzaj = "potwor"
	w.id = d.id
	w.ranga = d.ranga
	w.poziom = poziom
	return w
end

-- przeciwnik = { potwor = id, poziom = n } ALBO { postac = opis postaci } (Arena PvP, test lustrzany)
function Przeciwnicy.wartosciPrzeciwnika(przeciwnik: any)
	if type(przeciwnik) ~= "table" then
		Los.blad("brak opisu przeciwnika")
	end
	Statystyki.sprawdzKlucze(przeciwnik, Statystyki.POLA_PRZECIWNIKA, "opisie przeciwnika", "wrog")
	local potwor = przeciwnik.potwor
	local postac = przeciwnik.postac
	if potwor ~= nil and postac ~= nil then
		Los.blad("przeciwnik to potwór ALBO postać, nie oba")
	end
	if potwor ~= nil then
		if type(potwor) ~= "string" or PO_ID[potwor] == nil then
			Los.blad("nieznany przeciwnik")
		end
		local poziom = przeciwnik.poziom
		if not Los.calkowita(poziom) or poziom < 1 or poziom > STALE.poziom_maks then
			Los.blad("zły poziom przeciwnika")
		end
		return Przeciwnicy.wartosciPotwora(potwor, poziom)
	end
	if postac ~= nil then
		Statystyki.sprawdzPostac(postac, "wrog")
		return Statystyki.wartosciPostaci(postac)
	end
	Los.blad("przeciwnik musi mieć pole potwor albo postac")
	return nil
end

function Przeciwnicy.losujLup(strona, wygrana: boolean, los: () -> number)
	-- zawsze pięć rzutów w tej samej kolejności, niezależnie od wyniku (powtarzalność i zgodność portów)
	local rZloto = los()
	local rDosw = los()
	local rToken = los()
	local rGemy = los()
	local rShard = los()
	local lup = { zloto = 0, doswiadczenie = 0, tokeny_krainy = 0, gemy = 0, shard_ewolucji = 0, kraina = "" }
	if strona.rodzaj ~= "potwor" then
		return lup -- Arena (PvP): nagrody poza zakresem silnika
	end
	local d = PO_ID[strona.id]
	local L = d.lup
	local poziom = strona.poziom
	lup.kraina = d.kraina
	local dosw = skala(L.doswiadczenie, poziom)
	if wygrana then
		lup.zloto = Los.zaokraglij(skala(L.zloto, poziom) * (0.8 + 0.4 * rZloto))
		lup.doswiadczenie = Los.zaokraglij(dosw * (0.9 + 0.2 * rDosw))
		lup.tokeny_krainy = L.tokeny + (if rToken < L.szansa_tokenu then 1 else 0)
		lup.gemy = if rGemy < L.szansa_gemow then 1 else 0
		-- Shard Ewolucji wypada wyłącznie ze strażnika biomu (D-058); jajek z potworów nie ma wcale (D-060)
		if d.ranga == "straznik" and rShard < L.szansa_sharda then
			lup.shard_ewolucji = 1
		end
	else
		lup.doswiadczenie = Los.zaokraglij(dosw * STALE.udzial_doswiadczenia_przy_przegranej)
	end
	return lup
end

return Przeciwnicy
