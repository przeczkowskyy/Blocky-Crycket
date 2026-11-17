--[[
	LogikaAren — czysta logika aren walki zależnych od biomu (D-095), bez instancji. Używa jej moduł ArenyWalki
	(Workspace/ArenyWalki/Moduly); testy bez Studio (swiat/areny_walki/testy/test_aren.py) wykonują DOKŁADNIE ten plik
	interpreterem tools/walka/luau_mini.py.

	• wybierz(dane, zrodlo, biom) → klucz areny albo nil (nil = odtwarzacz zostaje na starej arenie prototypu):
	  najpierw atrybut BiomAreny kontenera źródła (nowy biom bez zmiany kodu: kontener Dżungli ustawia BiomAreny =
	  "dzungla", a DaneAren ma arenę o biomie "dzungla"), potem mapa źródeł (nazwa kontenera → arena);
	• wczytana(oczekiwane, jest) — model areny przyszedł do klienta (Persistent) w ≥ 90% części;
	• miesz, krokWagi — mgła lokalna (Atmosphere) od wartości zastanych do nastroju areny i z powrotem;
	• ognik, lisc, babelek, ptak, flaga — położenia drobnych ruchomych detali w UKŁADZIE SCENY (x w prawo na ekranie,
	  y w górę od płyty placu, z ku kamerze planu ogólnego) w chwili t — deterministyczne, bez losowania w klatce.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local PI = 3.141592653589793
local ZLOTY = 2.399963229728653 -- kąt złoty (rad): ogniki i liście rozłożone równo wokół placu

function L.wybierz(dane: any, zrodlo: any, biom: any): string?
	if type(dane) ~= "table" or type(dane.areny) ~= "table" then
		return nil
	end
	if type(biom) == "string" and biom ~= "" then
		if type(dane.areny[biom]) == "table" then
			return biom
		end
		for klucz, a in dane.areny do
			if type(a) == "table" and a.biom == biom then
				return klucz
			end
		end
	end
	if type(zrodlo) == "string" and type(dane.zrodla) == "table" then
		local k = dane.zrodla[zrodlo]
		if type(k) == "string" and type(dane.areny[k]) == "table" then
			return k
		end
	end
	return nil
end

function L.wczytana(oczekiwane: any, jest: any, prog: number?): boolean
	if type(oczekiwane) ~= "number" or type(jest) ~= "number" or oczekiwane <= 0 then
		return false
	end
	return jest >= oczekiwane * (prog or 0.9)
end

function L.miesz(a: number, b: number, w: number): number
	return a + (b - a) * w
end

function L.krokWagi(w: number, cel: number, tempo: number, dt: number): number
	local k = tempo * dt
	if cel > w then
		return math.min(cel, w + k)
	end
	return math.max(cel, w - k)
end

local function ulamek(x: number): number
	return x - math.floor(x)
end

-- pseudolosowa liczba 0…1 z dwóch liczb (bez stanu): ten sam bąbelek w tym samym cyklu zawsze w tym samym miejscu
function L.hasz(a: number, b: number): number
	return ulamek(math.sin(a * 12.9898 + b * 78.233) * 43758.5453)
end

-- błędny ognik i: krąży powoli po pierścieniu r0…r1, unosi się między y0 a y1
function L.ognik(i: number, t: number, r0: number, r1: number, y0: number, y1: number): (number, number, number)
	local a = i * ZLOTY + 0.06 * math.sin(t * 0.23 + i * 1.3) + t * 0.012
	local r = r0 + (r1 - r0) * ulamek(i * 0.618034) + 2.2 * math.sin(t * 0.41 + i * 1.7)
	local y = y0 + (y1 - y0) * (0.5 + 0.5 * math.sin(t * 0.7 + i * 2.1))
	return r * math.cos(a), y, r * math.sin(a)
end

-- spadający liść i: cykl opadania z y1 do y0 (prędkość v), kołysanie w bok; zwraca też obrót (rad) do wirowania
function L.lisc(i: number, t: number, r0: number, r1: number, y0: number, y1: number, v: number): (number, number, number, number)
	local okres = (y1 - y0) / math.max(v, 0.1)
	local faza = ulamek(t / okres + i * 0.37)
	local cykl = math.floor(t / okres + i * 0.37)
	local a = i * ZLOTY + L.hasz(i, cykl) * 0.8
	local r = r0 + (r1 - r0) * L.hasz(cykl, i + 0.5)
	local kolys = 1.3 * math.sin(t * 1.7 + i)
	local y = y1 - (y1 - y0) * faza
	return r * math.cos(a) - math.sin(a) * kolys, y, r * math.sin(a) + math.cos(a) * kolys, t * 2.3 + i
end

-- bąbelek i na wodzie: rośnie ze skali 0 do s, potem pęka (widoczny w pierwszych 70% cyklu); położenie z cyklu
function L.babelek(i: number, t: number, r0: number, r1: number, y_wody: number): (number, number, number, number)
	local okres = 2.6 + (i % 3) * 0.7
	local faza = ulamek(t / okres + i * 0.29)
	local cykl = math.floor(t / okres + i * 0.29)
	local a = 2 * PI * L.hasz(i, cykl)
	local r = r0 + (r1 - r0) * L.hasz(cykl + 0.3, i)
	local skala = 0
	if faza < 0.7 then
		skala = 0.25 + 0.75 * (faza / 0.7)
	end
	return r * math.cos(a), y_wody + 0.1 + 0.25 * faza, r * math.sin(a), skala
end

-- ptak i: krąży wysoko po okręgu; zwraca też kąt lotu (rad, styczny) i wychylenie skrzydeł (−1…1)
function L.ptak(i: number, t: number, r0: number, r1: number, y0: number, y1: number): (number, number, number, number, number)
	local w = 0.09 + 0.02 * (i % 3)
	local a = t * w + i * 2.1
	local r = r0 + (r1 - r0) * ulamek(i * 0.618034)
	local y = y0 + (y1 - y0) * ulamek(i * 0.381966) + 1.5 * math.sin(t * 0.5 + i)
	return r * math.cos(a), y, r * math.sin(a), a + PI / 2, math.sin(t * 6.0 + i * 1.9)
end

-- chorągiewka / pas chorągwi: kąt łopotania (rad) wokół pionu
function L.flaga(i: number, t: number, amplituda: number?): number
	return (amplituda or 0.16) * math.sin(t * 2.2 + i * 0.9) + 0.05 * math.sin(t * 5.3 + i * 2.7)
end

return L
