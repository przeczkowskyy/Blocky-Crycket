--[[
	LogikaSklepu — czysta strona sklepu zbrojmistrza na próbę (D-106; swiat/sklep_proba). Bez instancji i usług Roblox,
	więc ten sam plik wykonuje bez Studio interpreter tools/walka/luau_mini.py (lustro: logika_sklepu.py).

	Sklep NIE decyduje o kupnie — robi to kowal (KowalProba/Sygnaly/Sklep). Tutaj: układ okna z rozmiaru ekranu,
	teksty stanów i odmów, grupowanie oferty po stopniach. D = require(DaneSklepu); „oferta” = wiersze od kowala:
		{ id, nazwa, slot, slotNazwa, stopien, nrStopnia, cena, poziom, stan, brakuje, ulepszenie, staty }

	L.uklad(D, W, H) → rozmiary okna · L.grupy(D, oferta) → { { id, nazwa, kolor, wiersze, doKupienia } }
	L.pierwszaZakladka(D, oferta) → id stopnia · L.wiersz(D, o) → teksty wiersza i przycisk
	L.naglowek(D, zloto, poziom) · L.komunikat(D, akcja, odpowiedz) → zdanie dla gracza
	L.sprawdzPrzypadki(D) → ok, n, zle
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local function zakres(v, lo, hi)
	return math.max(lo, math.min(hi, v))
end

function L.uklad(D, W, H)
	local U = D.ui
	local szer = math.floor(math.min(W * (U.okno_x[2] - U.okno_x[1]), U.okno_maks_px[1]))
	local wys = math.floor(math.min(H * (U.okno_y[2] - U.okno_y[1]), U.okno_maks_px[2]))
	local naglowek = zakres(math.floor(wys * 0.1), U.naglowek_px[1], U.naglowek_px[2])
	local zakladka = zakres(math.floor(wys * 0.1), U.zakladka_px[1], U.zakladka_px[2])
	local wiersz = zakres(math.floor(wys * 0.115), U.wiersz_px[1], U.wiersz_px[2])
	local komunikat = zakres(math.floor(wys * 0.06), U.komunikat_px[1], U.komunikat_px[2])
	local lista = wys - naglowek - zakladka - komunikat
	local tekst = zakres(math.floor(wiersz * 0.3), U.tekst_min, U.tekst_maks)
	return { x = math.floor((W - szer) / 2), y = math.floor(H * U.okno_y[1]), szer = szer, wys = wys,
		naglowek = naglowek, zakladka = zakladka, wiersz = wiersz, komunikat = komunikat, lista = lista,
		przycisk = wiersz - 4, przyciskSzer = math.floor(szer * U.przycisk_szer), zamknij = naglowek, tekst = tekst,
		widoczne = math.floor(lista / wiersz * 10) / 10 }
end

function L.grupy(D, oferta)
	local w = {}
	for _, s in D.stopnie do
		local wiersze = {}
		local doKupienia = 0
		for _, o in oferta do
			if o.stopien == s.id then
				table.insert(wiersze, o)
				if o.stan == "kup" then
					doKupienia += 1
				end
			end
		end
		table.insert(w, { id = s.id, nazwa = s.nazwa, kolor = s.kolor, wiersze = wiersze, doKupienia = doKupienia })
	end
	return w
end

function L.pierwszaZakladka(D, oferta)
	local g = L.grupy(D, oferta)
	for _, s in g do
		if s.doKupienia > 0 then
			return s.id
		end
	end
	local wynik = if g[1] then g[1].id else ""
	for _, s in g do
		for _, o in s.wiersze do
			if o.stan == "masz" or o.stan == "zalozone" then
				wynik = s.id
			end
		end
	end
	return wynik
end

function L.wiersz(D, o)
	local T = D.teksty
	local posiadany = o.stan == "masz" or o.stan == "zalozone"
	local nazwa = o.nazwa
	if posiadany and o.ulepszenie > 0 then
		nazwa = string.format("%s %s", nazwa, string.format(T.ulepszenie, o.ulepszenie))
	end
	local staty = if o.staty ~= "" then o.staty else T.bez_dodatkow
	local cena = if o.cena > 0 then string.format(T.cena, o.cena) else T.cena_zero
	local w = { id = o.id, nazwa = nazwa, opis = string.format("%s · %s", o.slotNazwa, staty),
		wymaga = string.format("%s · %s", string.format(T.wymaga, o.poziom), cena), stan = T["stan_" .. o.stan],
		akcja = "", przycisk = "", aktywny = false, powod = "" }
	if o.stan == "kup" then
		w.akcja, w.przycisk, w.aktywny = "kup", T.kup, true
	elseif o.stan == "masz" then
		w.akcja, w.przycisk, w.aktywny = "zaloz", T.zaloz, true
	elseif o.stan == "za_drogie" then
		w.przycisk, w.powod = T.kup, string.format(T.za_malo_zlota, o.brakuje)
	elseif o.stan == "za_niski_poziom" then
		w.przycisk, w.powod = T.kup, string.format(T.za_niski_poziom, o.poziom)
	end
	return w
end

function L.naglowek(D, zloto, poziom)
	local T = D.teksty
	return { tytul = T.tytul, zloto = string.format(T.zloto, zloto), poziom = string.format(T.poziom, poziom) }
end

local MAPA = { masz = "masz", inna_klasa = "inna_klasa", czesc_zbroi = "czesc_zbroi",
	nieznany_przedmiot = "nieznany_przedmiot", nie_masz = "nie_masz", nie_zalozono = "nie_zalozono",
	brak_przymierzalni = "nie_zalozono", daleko = "podejdz", za_szybko = "za_szybko", brak_stanu = "nieczynny",
	nieczynny = "nieczynny" }

function L.komunikat(D, akcja, r)
	local T = D.teksty
	if type(r) ~= "table" then
		return T.nieczynny
	end
	if r.ok == true then
		local nazwa = if type(r.nazwa) == "string" then r.nazwa else ""
		if akcja == "kup" then
			return string.format(if r.zalozony == true then T.ok_kup_zalozony else T.ok_kup_schowany, nazwa)
		elseif akcja == "zaloz" then
			return string.format(T.ok_zaloz, nazwa)
		end
		return ""
	end
	local ile = if type(r.brakuje) == "number" then r.brakuje else 0
	if r.powod == "za_malo_zlota" then
		return string.format(T.za_malo_zlota, ile)
	elseif r.powod == "za_niski_poziom" then
		return string.format(T.za_niski_poziom, if type(r.wymagany) == "number" then r.wymagany else ile)
	end
	return T[MAPA[r.powod] or "blad"]
end

------------------------------------------------------------------ zgodność z lustrem (przypadki z dane.py)
local function rowne(a, b)
	if type(a) ~= type(b) then
		return false
	end
	if type(a) == "number" then
		return math.abs(a - b) < 1e-9
	end
	if type(a) ~= "table" then
		return a == b
	end
	for k, v in a do
		if not rowne(v, b[k]) then
			return false
		end
	end
	for k, v in b do
		if a[k] == nil and v ~= nil then
			return false
		end
	end
	return true
end
L.rowne = rowne

function L.sprawdzPrzypadki(D)
	local P = D.przypadki
	local n, zle = 0, {}
	local function sprawdz(nazwa, i, oczekiwane, wynik)
		n += 1
		if not rowne(oczekiwane, wynik) then
			table.insert(zle, nazwa .. " " .. tostring(i))
		end
	end
	for i, p in P.uklad do
		sprawdz("uklad", i, p.wynik, L.uklad(D, p.W, p.H))
	end
	for i, p in P.oferta do
		sprawdz("grupy", i, p.grupy, L.grupy(D, p.oferta))
		sprawdz("zakladka", i, p.zakladka, L.pierwszaZakladka(D, p.oferta))
		local wiersze = {}
		for _, o in p.oferta do
			table.insert(wiersze, L.wiersz(D, o))
		end
		sprawdz("wiersze", i, p.wiersze, wiersze)
	end
	for i, p in P.komunikat do
		sprawdz("komunikat", i, p.wynik, L.komunikat(D, p.akcja, p.r))
	end
	for i, p in P.naglowek do
		sprawdz("naglowek", i, p.wynik, L.naglowek(D, p.zloto, p.poziom))
	end
	return #zle == 0, n, zle
end

return L
