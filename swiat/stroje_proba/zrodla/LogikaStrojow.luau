--[[
	LogikaStrojow — czysta logika stroju bohatera (próba D-071, swiat/stroje_proba). Bez instancji i usług Roblox,
	więc ten sam plik wykonuje bez Studio interpreter tools/walka/luau_mini.py (testy: lustro logika_strojow.py).

	Strój = lista id przedmiotów z katalogu (swiat/postacie/przedmioty.json) założonych na bohatera klasy `klasa`.
	D = require(DaneStrojow). Funkcje zwracają (ok, wynik) — wynik albo powód odmowy:
		zla_klasa, zly_stroj, nieznany_przedmiot, przedmiot_innej_klasy, czesc_bez_calosci, czesc_zbroi,
		dwa_w_slocie, dwie_powloki, zly_slot, nieznany_zestaw.

	L.dostepny(D, klasa, id) → bool        przedmiot pasuje do klasy (D.dobor: "klasa" — pole klasy, "cialo" — typ ciała)
	L.slotOkna(D, id) → slot               slot w oknie przymierzalni ("Legs" dla spodni przy D.spodnie = "osobny_slot")
	L.wybieralny(D, klasa, id) → bool      ma własny wybór w oknie (część zbroi przy D.spodnie = "czesc_zbroi" — nie)
	L.oferta(D, klasa) → { { slot, nazwa, przedmioty = { id… } } }   sloty okna z przedmiotami
	L.normalizuj(D, klasa, ids) → ok, ids  bez powtórzeń, z częściami zbroi, w kolejności K.przedmioty
	L.zaloz(D, klasa, stroj, id) / L.zdejmij(D, klasa, stroj, slot) / L.zestaw(D, klasa, nazwa) → ok, ids
	L.plan(D, klasa, ids) → ok, { przedmioty = { id… }, zakryte = { [kość] = true }, ukryte = { [znacznik] = true } }
	L.naNapis(ids) → "a,b"                 L.zNapisu(napis) → { id… } | nil (nil = brak stroju: dawny szablon walki)
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}
local MAKS_PRZEDMIOTOW = 24

local function czescZbroi(D, P)
	return P.czescOd ~= nil and D.spodnie == "czesc_zbroi"
end

function L.dostepny(D, klasa, id)
	local K = D.klasy[klasa]
	local P = if type(id) == "string" then D.przedmioty[id] else nil
	if K == nil or P == nil then
		return false
	end
	if D.dobor == "cialo" then
		return P.cialo == K.cialo or P.cialo == "dowolne"
	end
	return table.find(P.klasy, klasa) ~= nil
end

function L.slotOkna(D, id)
	local P = D.przedmioty[id]
	if P.czescOd ~= nil and D.spodnie == "osobny_slot" then
		return "Legs"
	end
	return P.slot
end

function L.wybieralny(D, klasa, id)
	if not L.dostepny(D, klasa, id) then
		return false
	end
	return not czescZbroi(D, D.przedmioty[id])
end

-- kolejność przedmiotów klasy (przy doborze po ciele dochodzą przedmioty innych klas, w kolejności danych)
local function kolejnosc(D, klasa)
	local K = D.klasy[klasa]
	local lista = {}
	for _, id in K.przedmioty do
		table.insert(lista, id)
	end
	if D.dobor == "cialo" then
		for _, k in D.kolejnoscKlas do
			if k ~= klasa then
				for _, id in D.klasy[k].przedmioty do
					table.insert(lista, id)
				end
			end
		end
	end
	return lista
end

function L.oferta(D, klasa)
	local wynik = {}
	if D.klasy[klasa] == nil then
		return wynik
	end
	local lista = kolejnosc(D, klasa)
	for _, s in D.sloty do
		local ids = {}
		for _, id in lista do
			if L.wybieralny(D, klasa, id) and L.slotOkna(D, id) == s.id then
				table.insert(ids, id)
			end
		end
		if #ids > 0 then
			table.insert(wynik, { slot = s.id, nazwa = s.nazwa, przedmioty = ids })
		end
	end
	return wynik
end

function L.normalizuj(D, klasa, ids)
	if type(klasa) ~= "string" or D.klasy[klasa] == nil then
		return false, "zla_klasa"
	end
	if type(ids) ~= "table" or #ids > MAKS_PRZEDMIOTOW then
		return false, "zly_stroj"
	end
	local n = 0
	for _ in ids do
		n += 1
	end
	if n ~= #ids then
		return false, "zly_stroj"
	end
	local zbior = {}
	for _, id in ids do
		if type(id) ~= "string" then
			return false, "zly_stroj"
		end
		if D.przedmioty[id] == nil then
			return false, "nieznany_przedmiot"
		end
		if not L.dostepny(D, klasa, id) then
			return false, "przedmiot_innej_klasy"
		end
		zbior[id] = true
	end
	local lista = kolejnosc(D, klasa)
	if D.spodnie == "czesc_zbroi" then
		for _, id in lista do
			local c = D.przedmioty[id].czescOd
			if zbior[id] and c ~= nil and not zbior[c] then
				return false, "czesc_bez_calosci"
			end
		end
		for _, id in lista do
			local c = D.przedmioty[id].czescOd
			if c ~= nil and zbior[c] and L.dostepny(D, klasa, id) then
				zbior[id] = true
			end
		end
	end
	local sloty, kosci = {}, {}
	for _, id in lista do
		if zbior[id] then
			local P = D.przedmioty[id]
			if not czescZbroi(D, P) then
				local s = L.slotOkna(D, id)
				if sloty[s] then
					return false, "dwa_w_slocie"
				end
				sloty[s] = id
			end
			for _, seg in P.segmenty do
				if seg.zakrywa then
					if kosci[seg.kosc] then
						return false, "dwie_powloki"
					end
					kosci[seg.kosc] = id
				end
			end
		end
	end
	local wynik = {}
	for _, id in lista do
		if zbior[id] then
			table.insert(wynik, id)
			zbior[id] = nil
		end
	end
	return true, wynik
end

-- strój bez przedmiotów slotu okna (przy „czesc_zbroi” razem z ich częściami zbroi)
local function bezSlotu(D, stroj, slot)
	local zdjete = {}
	for _, id in stroj do
		if not czescZbroi(D, D.przedmioty[id]) and L.slotOkna(D, id) == slot then
			zdjete[id] = true
		end
	end
	local wynik = {}
	for _, id in stroj do
		local c = D.przedmioty[id].czescOd
		if not zdjete[id] and not (D.spodnie == "czesc_zbroi" and c ~= nil and zdjete[c]) then
			table.insert(wynik, id)
		end
	end
	return wynik
end

function L.zaloz(D, klasa, stroj, id)
	local ok, st = L.normalizuj(D, klasa, stroj)
	if not ok then
		return ok, st
	end
	if type(id) ~= "string" or D.przedmioty[id] == nil then
		return false, "nieznany_przedmiot"
	end
	if not L.dostepny(D, klasa, id) then
		return false, "przedmiot_innej_klasy"
	end
	if not L.wybieralny(D, klasa, id) then
		return false, "czesc_zbroi"
	end
	local nowy = bezSlotu(D, st, L.slotOkna(D, id))
	table.insert(nowy, id)
	return L.normalizuj(D, klasa, nowy)
end

function L.zdejmij(D, klasa, stroj, slot)
	local ok, st = L.normalizuj(D, klasa, stroj)
	if not ok then
		return ok, st
	end
	local znany = false
	for _, s in D.sloty do
		if s.id == slot then
			znany = true
		end
	end
	if type(slot) ~= "string" or not znany then
		return false, "zly_slot"
	end
	return L.normalizuj(D, klasa, bezSlotu(D, st, slot))
end

function L.zestaw(D, klasa, nazwa)
	local K = if type(klasa) == "string" then D.klasy[klasa] else nil
	if K == nil then
		return false, "zla_klasa"
	end
	for _, z in K.zestawy do
		if z.id == nazwa then
			local ids = {}
			for _, id in z.przedmioty do
				table.insert(ids, id)
			end
			return L.normalizuj(D, klasa, ids)
		end
	end
	return false, "nieznany_zestaw"
end

function L.plan(D, klasa, ids)
	local ok, st = L.normalizuj(D, klasa, ids)
	if not ok then
		return ok, st
	end
	local zakryte, ukryte = {}, {}
	for _, id in st do
		local P = D.przedmioty[id]
		for _, seg in P.segmenty do
			if seg.zakrywa then
				zakryte[seg.kosc] = true
			end
		end
		for _, z in P.ukrywa do
			ukryte[z] = true
		end
	end
	return true, { przedmioty = st, zakryte = zakryte, ukryte = ukryte }
end

function L.naNapis(ids)
	return table.concat(ids, ",")
end

function L.zNapisu(napis)
	if type(napis) ~= "string" then
		return nil
	end
	local wynik = {}
	local start = 1
	while start <= #napis + 1 do
		local a = string.find(napis, ",", start, true)
		local kawalek = string.sub(napis, start, if a then a - 1 else #napis)
		if kawalek ~= "" then
			table.insert(wynik, kawalek)
		end
		if not a then
			break
		end
		start = a + 1
	end
	return wynik
end

return L
