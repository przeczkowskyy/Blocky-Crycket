--[[
	Wzorcowe — wzorcowa postać klasy na poziomie (dokładny port tools/walka/wzorcowe.py, funkcja postac()).
	Używa jej WYŁĄCZNIE serwer prototypu: klient wybiera z zamkniętej listy klasę, przeciwnika i poziom, a statystyki
	buduje serwer (klient nie przysyła żadnych liczb — D-016). Zgodność z Pythonem sprawdza testy/test_walki_play.py
	(ten sam wybór i ziarno → ten sam dziennik co port silnika w Pythonie).

	Zasada równości (U10): na danym poziomie każda klasa ma tę samą pulę punktów, tę samą broń, ten sam pancerz z
	przedmiotów i tyle samo slotów umiejętności; różni się tylko rozkładem punktów i cechą klasy (Wojownik nosi tarczę).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local W = {}

W.PUNKTY_START = 30
W.PUNKTY_NA_POZIOM = 10
W.BLOK_TARCZY = 0.2828
W.STATYSTYKI = { "sila", "kondycja", "inteligencja", "zrecznosc", "szczescie", "pancerz" }
W.KLASY = { "wojownik", "zwiadowca", "mag" }
W.ROZKLADY = {
	wojownik = { sila = 0.26, kondycja = 0.30, inteligencja = 0.12, zrecznosc = 0.08, szczescie = 0.10, pancerz = 0.14 },
	zwiadowca = { sila = 0.27, kondycja = 0.27, inteligencja = 0.10, zrecznosc = 0.14, szczescie = 0.13, pancerz = 0.09 },
	mag = { sila = 0.24, kondycja = 0.22, inteligencja = 0.24, zrecznosc = 0.10, szczescie = 0.10, pancerz = 0.10 },
}
W.UMIEJETNOSCI = {
	wojownik = { "ciecie", "miazdzacy_cios", "kamienna_skora" },
	zwiadowca = { "uderzenie_z_gory", "zatruta_strzala", "skupienie" },
	mag = { "kula_ognia", "lodowy_pocisk", "bariera" },
}

function W.pula(poziom: number): number
	return W.PUNKTY_START + W.PUNKTY_NA_POZIOM * (poziom - 1)
end

function W.sloty(poziom: number): number
	if poziom >= 10 then
		return 3
	elseif poziom >= 5 then
		return 2
	end
	return 1
end

-- udziały → całkowite punkty o sumie dokładnie `punkty` (metoda największych reszt, jak w Pythonie)
function W.rozdziel(rozklad, punkty: number)
	local dokladne, st = {}, {}
	local suma = 0
	for _, s in W.STATYSTYKI do
		dokladne[s] = rozklad[s] * punkty
		st[s] = math.floor(dokladne[s] + 1e-9)
		suma += st[s]
	end
	local reszta = punkty - suma
	local kolejnosc = table.clone(W.STATYSTYKI)
	local indeks = {}
	for i, s in W.STATYSTYKI do
		indeks[s] = i
	end
	table.sort(kolejnosc, function(a, b)
		local ua, ub = -(dokladne[a] - st[a]), -(dokladne[b] - st[b])
		if ua ~= ub then
			return ua < ub
		end
		if -rozklad[a] ~= -rozklad[b] then
			return -rozklad[a] < -rozklad[b]
		end
		return indeks[a] < indeks[b]
	end)
	local i = 0
	while reszta > 0 do
		local s = kolejnosc[(i % #kolejnosc) + 1]
		st[s] += 1
		reszta -= 1
		i += 1
	end
	return st
end

function W.postac(klasa: string, poziom: number)
	local st = W.rozdziel(W.ROZKLADY[klasa], W.pula(poziom))
	local um = {}
	for i = 1, W.sloty(poziom) do
		table.insert(um, W.UMIEJETNOSCI[klasa][i])
	end
	local p = {
		nazwa = string.upper(string.sub(klasa, 1, 1)) .. string.sub(klasa, 2),
		klasa = klasa,
		poziom = poziom,
		statystyki = st,
		bron = { obrazenia = 8 + 4 * poziom },
		pancerz_przedmiotow = 3 + 1.5 * poziom,
		umiejetnosci = um,
	}
	if klasa == "wojownik" then
		p.tarcza = { blok = W.BLOK_TARCZY }
	end
	return p
end

return W
