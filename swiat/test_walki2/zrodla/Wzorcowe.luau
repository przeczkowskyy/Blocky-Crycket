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

-- postać wzorcowa (umowa z swiat/las_potwory: ta sygnatura i ten wynik się nie zmieniają)
function W.postac(klasa: string, poziom: number)
	return W.postacZPula(klasa, poziom, W.pula(poziom))
end

-- to samo z własną pulą punktów (v3: zestaw „pod manę” — pula pomniejszona o koszt przedmiotów many)
function W.postacZPula(klasa: string, poziom: number, punkty: number)
	local st = W.rozdziel(W.ROZKLADY[klasa], punkty)
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

--[[ Zestawy postaci na tablicy prototypu (v3) — dokładny port swiat/test_walki2/zestawy.py (opis zestawów tam;
	test bez Studio porównuje W.zestaw z Pythonem dla każdej klasy, poziomu i zestawu). Liczby buildu „pod manę”
	są z tools/walka/wzorcowe.py (KOSZT_MANY, BRON_MANY, PASYWKA_MANY, PREMIE_MANY). ]]
W.ZESTAWY = { "wzorcowa", "mana", "pasywki", "wskrzeszenie" }
W.KOSZT_MANY = { wojownik = 0.225, zwiadowca = 0.20, mag = 0.26 }
W.BRON_MANY = { wojownik = "miecz_runiczny", zwiadowca = "luk_runiczny", mag = "kostur_many" }
W.PASYWKA_MANY = { wojownik = "bitewny_rytm", zwiadowca = "przyplyw_adrenaliny", mag = "przeplyw_many" }
W.PREMIE_MANY = { zysk_many = 0.6, koszt_many = 0.15, mana_startowa = 70 }
W.PASYWKI_ZESTAWU = { wojownik = { "kolos", "rozdzieracz" }, zwiadowca = { "oko_lowcy", "zwinnosc" }, mag = { "skupiona_magia", "magiczny_pocisk" } }
W.BRON_ZESTAWU = { wojownik = "topor_rzeznika", zwiadowca = "luk_wiatru", mag = "ognista_rozdzka" }
W.LUSTRO = "lustro"
W.NAZWY_LUSTRA = { wojownik = "Lustrzany Wojownik", zwiadowca = "Lustrzany Zwiadowca", mag = "Lustrzany Mag" }

-- round() Pythona (przy równym .5 do parzystej) — build „pod manę” w wzorcowe.py liczy pulę tak
local function zaokraglijJakPython(x: number): number
	local f = math.floor(x)
	local r = x - f
	if r > 0.5 then
		return f + 1
	elseif r < 0.5 then
		return f
	end
	return if f % 2 == 0 then f else f + 1
end

local function pierwsze(lista, n: number)
	local wynik = {}
	for i = 1, math.min(n, #lista) do
		wynik[i] = lista[i]
	end
	return wynik
end

-- zestaw → opis postaci (wejście silnika) albo nil (nieznany zestaw)
function W.zestaw(nazwa: string, klasa: string, poziom: number)
	local akt = W.UMIEJETNOSCI[klasa]
	local n = W.sloty(poziom)
	if nazwa == "wzorcowa" then
		return W.postac(klasa, poziom)
	elseif nazwa == "mana" then
		local p = W.postacZPula(klasa, poziom, zaokraglijJakPython(W.pula(poziom) * (1 - W.KOSZT_MANY[klasa])))
		p.umiejetnosci = pierwsze({ akt[1], W.PASYWKA_MANY[klasa], akt[2] }, n)
		p.premie = table.clone(W.PREMIE_MANY)
		p.bron.pasywka = W.BRON_MANY[klasa]
		return p
	elseif nazwa == "pasywki" then
		local p = W.postac(klasa, poziom)
		p.umiejetnosci = pierwsze({ akt[1], W.PASYWKI_ZESTAWU[klasa][1], W.PASYWKI_ZESTAWU[klasa][2] }, n)
		p.bron.pasywka = W.BRON_ZESTAWU[klasa]
		return p
	elseif nazwa == "wskrzeszenie" then
		local p = W.postac(klasa, poziom)
		local um = pierwsze(akt, n - 1)
		table.insert(um, "wskrzeszenie")
		p.umiejetnosci = um
		return p
	end
	return nil
end

-- przeciwnik „lustro”: postać tej samej klasy i zestawu (pojedynek — wskrzeszenie przeciwnika na tablicy)
function W.lustro(nazwa: string, klasa: string, poziom: number)
	local p = W.zestaw(nazwa, klasa, poziom)
	if p then
		p.nazwa = W.NAZWY_LUSTRA[klasa]
	end
	return p
end

return W
