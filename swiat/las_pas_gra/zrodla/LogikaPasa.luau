--[[
	LogikaPasa — czysta logika pakietu „las-pas w grze” (ModuleScript w Workspace/LasPasGra/Moduly; czytają go
	SerwerPasa, KlientPasa i MglaPasa). Bez instancji, zegara i Random: tylko liczby, napisy, wartości logiczne i
	tabele. Lustro w Pythonie: swiat/las_pas_gra/logika_pasa.py (te same funkcje, nazwy snake_case, te same wzory);
	testy offline: swiat/las_pas_gra/testy/test_pasa.py — porównują oba pliki wywołanie po wywołaniu (ten plik
	wykonuje wtedy interpreter tools/walka/luau_mini.py, jeśli jest w repozytorium), a krzywą przelotu także z
	swiat/biom_las/pas/sprawdz_plan.py (krzywa_kamery). Zmieniasz wzór tutaj — zmień go tam.

	Konwencje:
		prostokąt  { x1, x2, z1, z2 } w poziomie świata (x1 ≤ x2, z1 ≤ z2)
		brama      { x, z1, z2, tolerancja, glebokosc } — linia bramy x; „za bramą” = x + tolerancja < X < x + glebokosc
		ratunek    { x1, x2, z1, z2, yMin }
		punkty     { { t = s, poz = { x, y, z }, patrz = { x, y, z } }, … } (przelot w świecie)
		stan       { faza, id, od, doKiedy, nastepny, wolnyOd } — stan przelotu jednego gracza (krokPrzelotu go zmienia)

	API (wszystko zwraca wartości, nic nie zmienia poza tabelą stanu w krokPrzelotu):
		wProstokacie(x, z, r) → bool          odlegloscOdProstokata(x, z, r) → n
		wagaMgly(x, z, r, pas) → 0…1          krokWagi(waga, cel, tempo, dt) → n
		zaBrama(x, z, b) → bool               decyzjaBramy(x, z, uprawniony, b) → "wolno" | "cofnij"
		potrzebaRatunku(x, y, z, r) → bool    celRatunku(x, z, uprawniony, b) → "przybycie" | "przed_brama" | "za_brama"
		otwieraBrame(info) → bool             (wynik walki z SerwerPotworow: tylko wygrana ze Strażnikiem)
		punktKrzywej(punkty, t) → x, y, z     celKrzywej(punkty, t) → x, y, z     czasKrzywej(punkty) → s
		punktWyprzedzenia(punkty, t, w) → x, y, z
		czyZaczacPrzelot(widzial, faza, wPasie, gotowy, teraz, wolnyOd) → bool
		terminPrzelotu(start, czas, zapas) → s
		nowyStanPrzelotu() → stan             krokPrzelotu(stan, wejscie, teraz, stale) → { akcja, … }
		sprawdzPrzypadki() → (ok, n, bledy)   (te same 39 wywołań co PRZYPADKI w logika_pasa.py)
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

------------------------------------------------------------------ prostokąty i mgła
function L.wProstokacie(x: number, z: number, r): boolean
	return x >= r.x1 and x <= r.x2 and z >= r.z1 and z <= r.z2
end

function L.odlegloscOdProstokata(x: number, z: number, r): number
	local dx = math.max(r.x1 - x, 0, x - r.x2)
	local dz = math.max(r.z1 - z, 0, z - r.z2)
	return math.sqrt(dx * dx + dz * dz)
end

-- 1 w prostokącie pasa, maleje liniowo do 0 w odległości `pas` od brzegu (łagodne wejście i wyjście)
function L.wagaMgly(x: number, z: number, r, pas: number): number
	local d = L.odlegloscOdProstokata(x, z, r)
	if pas <= 0 then
		return if d <= 0 then 1 else 0
	end
	return math.min(1, math.max(0, 1 - d / pas))
end

-- waga idzie do celu najwyżej o tempo · dt
function L.krokWagi(waga: number, cel: number, tempo: number, dt: number): number
	local k = tempo * dt
	if cel > waga then
		return math.min(cel, waga + k)
	end
	return math.max(cel, waga - k)
end

------------------------------------------------------------------ brama i ratunek
function L.zaBrama(x: number, z: number, b): boolean
	return z >= b.z1 and z <= b.z2 and x > b.x + b.tolerancja and x < b.x + b.glebokosc
end

function L.decyzjaBramy(x: number, z: number, uprawniony: boolean, b): string
	if not uprawniony and L.zaBrama(x, z, b) then
		return "cofnij"
	end
	return "wolno"
end

function L.potrzebaRatunku(x: number, y: number, z: number, r): boolean
	return y < r.yMin and L.wProstokacie(x, z, r)
end

function L.celRatunku(x: number, z: number, uprawniony: boolean, b): string
	if z >= b.z1 and z <= b.z2 and x > b.x then
		return if uprawniony then "za_brama" else "przed_brama"
	end
	return "przybycie"
end

-- Sygnaly/WynikWalki z SerwerPotworow niesie { straznik = bool, wynik = "wygrana" | "przegrana", … }
function L.otwieraBrame(info: any): boolean
	return type(info) == "table" and info.straznik == true and info.wynik == "wygrana"
end

------------------------------------------------------------------ krzywa przelotu (Catmull-Rom jak sprawdz_plan.krzywa_kamery)
local function rowne(a, b): boolean
	return a[1] == b[1] and a[2] == b[2] and a[3] == b[3]
end

-- odcinek o tych samych końcach to postój; sąsiad za postojem albo za końcem listy = koniec odcinka
local function krzywa(punkty, t: number, pole: string): (number, number, number)
	local n = #punkty
	if n == 0 then
		return 0, 0, 0
	end
	if n == 1 or t <= punkty[1].t then
		local p = punkty[1][pole]
		return p[1], p[2], p[3]
	end
	for i = 1, n - 1 do
		local a, b = punkty[i], punkty[i + 1]
		local dt = b.t - a.t
		if dt > 0 and (t <= b.t or i == n - 1) then
			local f = math.min(1, math.max(0, (t - a.t) / dt))
			local p1, p2 = a[pole], b[pole]
			if rowne(p1, p2) then
				return p1[1], p1[2], p1[3]
			end
			local p0 = p1
			if i > 1 and not rowne(punkty[i - 1][pole], p1) then
				p0 = punkty[i - 1][pole]
			end
			local p3 = p2
			if i + 2 <= n and not rowne(punkty[i + 2][pole], p2) then
				p3 = punkty[i + 2][pole]
			end
			local w = {}
			for j = 1, 3 do
				w[j] = 0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * f + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * f * f
					+ (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * f * f * f)
			end
			return w[1], w[2], w[3]
		end
	end
	local p = punkty[n][pole]
	return p[1], p[2], p[3]
end

function L.punktKrzywej(punkty, t: number): (number, number, number)
	return krzywa(punkty, t, "poz")
end

function L.celKrzywej(punkty, t: number): (number, number, number)
	return krzywa(punkty, t, "patrz")
end

function L.czasKrzywej(punkty): number
	if #punkty == 0 then
		return 0
	end
	return punkty[#punkty].t
end

function L.punktWyprzedzenia(punkty, t: number, wyprzedzenie: number): (number, number, number)
	return L.punktKrzywej(punkty, math.min(L.czasKrzywej(punkty), t + wyprzedzenie))
end

------------------------------------------------------------------ przelot: flaga pierwszego wejścia i fazy
function L.czyZaczacPrzelot(widzial: boolean, faza: string, wPasie: boolean, gotowy: boolean, teraz: number, wolnyOd: number): boolean
	return (not widzial) and faza == "brak" and wPasie and gotowy and teraz >= wolnyOd
end

function L.terminPrzelotu(start: number, czas: number, zapas: number): number
	return start + czas + zapas
end

function L.nowyStanPrzelotu()
	return { faza = "brak", id = 0, od = 0, doKiedy = 0, nastepny = 0, wolnyOd = 0 }
end

local function zakoncz(s, akcje, teraz: number, przerwij: string?, k)
	table.insert(akcje, "odblokuj")
	if przerwij == "odmowa" then
		table.insert(akcje, "zapomnij")
		s.wolnyOd = teraz + k.ponowPoOdmowie
	elseif przerwij == "reset" then
		table.insert(akcje, "zapomnij")
		s.wolnyOd = teraz
	end
	s.faza = "brak"
end

--[[ Jeden krok automatu przelotu jednego gracza. Serwer woła go w każdym tyknięciu i wykonuje zwrócone akcje
	w podanej kolejności: "widzial" (flaga na tak), "zapomnij" (flaga na nie), "zablokuj" (postać stoi, bez walk),
	"przygotuj" (klient: zasłona, kamera, sterowanie), "laduj" (prośby o wczytanie mapy wzdłuż trasy), "start"
	(klient: lot), "podtrzymaj" (prośba o mapę przed kamerą), "przerwij" (klient: sprzątanie), "odblokuj".
	wejscie: { widzial, wPasie, gotowy, postac (ta sama żywa postać), strumienie (ile próśb jeszcze trwa), koniec
	(klient zgłosił koniec tego przelotu), przerwij = nil | "odmowa" | "reset" | "postac" }.
	Flaga „widział” jest ustawiana NA STARCIE — przelot nie zapętla się po błędzie ani po milczeniu klienta; kasują
	ją tylko odmowa klienta (ponowienie po ponowPoOdmowie s) i uchwyt testowy „odtwórz ponownie” (reset). ]]
function L.krokPrzelotu(s, w, teraz: number, k)
	local akcje = {}
	local f = s.faza
	if f == "brak" then
		if w.postac and L.czyZaczacPrzelot(w.widzial, f, w.wPasie, w.gotowy, teraz, s.wolnyOd) then
			s.id += 1
			s.faza = "uspokaja"
			s.od = teraz
			table.insert(akcje, "widzial")
		end
		return akcje
	end
	local przerwij = w.przerwij
	if przerwij == nil and not w.postac then
		przerwij = "postac"
	end
	if przerwij ~= nil then
		if f == "laduje" or f == "trwa" then
			table.insert(akcje, "przerwij")
		end
		zakoncz(s, akcje, teraz, przerwij, k)
		return akcje
	end
	if f == "uspokaja" then
		if teraz - s.od >= k.uspokojenie then
			s.faza = "laduje"
			s.od = teraz
			table.insert(akcje, "zablokuj")
			table.insert(akcje, "przygotuj")
			table.insert(akcje, "laduj")
		end
	elseif f == "laduje" then
		if w.strumienie <= 0 or teraz - s.od >= k.ladowanie then
			s.faza = "trwa"
			s.od = teraz
			s.doKiedy = L.terminPrzelotu(teraz, k.czas, k.zapas)
			s.nastepny = teraz + k.strumienCo
			table.insert(akcje, "start")
		end
	elseif f == "trwa" then
		if w.koniec then
			zakoncz(s, akcje, teraz, nil, k)
		elseif teraz >= s.doKiedy then
			table.insert(akcje, "przerwij")
			zakoncz(s, akcje, teraz, nil, k)
		elseif teraz >= s.nastepny then
			s.nastepny = teraz + k.strumienCo
			table.insert(akcje, "podtrzymaj")
		end
	end
	return akcje
end

------------------------------------------------------------------ przypadki wzorcowe (te same co PRZYPADKI w logika_pasa.py)
local R = { x1 = 0, x2 = 10, z1 = -5, z2 = 5 }
local B = { x = 100, z1 = -40, z2 = 40, tolerancja = 1.5, glebokosc = 200 }
local RAT = { x1 = -100, x2 = 400, z1 = -60, z2 = 60, yMin = -30 }
local PK = {
	{ t = 0, poz = { 0, 0, 0 }, patrz = { 10, 0, 0 } },
	{ t = 1, poz = { 10, 0, 0 }, patrz = { 20, 0, 0 } },
	{ t = 2, poz = { 20, 10, 0 }, patrz = { 30, 0, 0 } },
	{ t = 3, poz = { 20, 10, 0 }, patrz = { 30, 0, 0 } },
}

local function x_(a, _b, _c)
	return a
end
local function y_(_a, b, _c)
	return b
end

local PRZYPADKI = {
	{ "wProstokacie(5,0)", function() return L.wProstokacie(5, 0, R) end, true },
	{ "wProstokacie(11,0)", function() return L.wProstokacie(11, 0, R) end, false },
	{ "wProstokacie(10,5)", function() return L.wProstokacie(10, 5, R) end, true },
	{ "odleglosc(13,9)", function() return L.odlegloscOdProstokata(13, 9, R) end, 5 },
	{ "wagaMgly(5,0,pas 20)", function() return L.wagaMgly(5, 0, R, 20) end, 1 },
	{ "wagaMgly(20,0,pas 20)", function() return L.wagaMgly(20, 0, R, 20) end, 0.5 },
	{ "wagaMgly(40,0,pas 20)", function() return L.wagaMgly(40, 0, R, 20) end, 0 },
	{ "krokWagi(0,1,0.8,0.5)", function() return L.krokWagi(0, 1, 0.8, 0.5) end, 0.4 },
	{ "krokWagi(0.9,0,0.8,2)", function() return L.krokWagi(0.9, 0, 0.8, 2) end, 0 },
	{ "zaBrama(102,0)", function() return L.zaBrama(102, 0, B) end, true },
	{ "zaBrama(101,0)", function() return L.zaBrama(101, 0, B) end, false },
	{ "zaBrama(102,50)", function() return L.zaBrama(102, 50, B) end, false },
	{ "decyzjaBramy(110,0,nie)", function() return L.decyzjaBramy(110, 0, false, B) end, "cofnij" },
	{ "decyzjaBramy(110,0,tak)", function() return L.decyzjaBramy(110, 0, true, B) end, "wolno" },
	{ "decyzjaBramy(90,0,nie)", function() return L.decyzjaBramy(90, 0, false, B) end, "wolno" },
	{ "potrzebaRatunku(50,-40,0)", function() return L.potrzebaRatunku(50, -40, 0, RAT) end, true },
	{ "potrzebaRatunku(50,0,0)", function() return L.potrzebaRatunku(50, 0, 0, RAT) end, false },
	{ "potrzebaRatunku(900,-40,0)", function() return L.potrzebaRatunku(900, -40, 0, RAT) end, false },
	{ "celRatunku(150,0,nie)", function() return L.celRatunku(150, 0, false, B) end, "przed_brama" },
	{ "celRatunku(150,0,tak)", function() return L.celRatunku(150, 0, true, B) end, "za_brama" },
	{ "celRatunku(50,0,tak)", function() return L.celRatunku(50, 0, true, B) end, "przybycie" },
	{ "otwieraBrame(straznik wygrana)", function() return L.otwieraBrame({ straznik = true, wynik = "wygrana" }) end, true },
	{ "otwieraBrame(straznik przegrana)", function() return L.otwieraBrame({ straznik = true, wynik = "przegrana" }) end, false },
	{ "otwieraBrame(slime wygrana)", function() return L.otwieraBrame({ straznik = false, wynik = "wygrana" }) end, false },
	{ "punktKrzywej(0).x", function() return x_(L.punktKrzywej(PK, 0)) end, 0 },
	{ "punktKrzywej(1).x", function() return x_(L.punktKrzywej(PK, 1)) end, 10 },
	{ "punktKrzywej(0.5).x", function() return x_(L.punktKrzywej(PK, 0.5)) end, 4.375 },
	{ "punktKrzywej(1.5).y", function() return y_(L.punktKrzywej(PK, 1.5)) end, 5 },
	{ "punktKrzywej(2.5).x", function() return x_(L.punktKrzywej(PK, 2.5)) end, 20 },
	{ "punktKrzywej(9).y", function() return y_(L.punktKrzywej(PK, 9)) end, 10 },
	{ "celKrzywej(0.5).x", function() return x_(L.celKrzywej(PK, 0.5)) end, 14.375 },
	{ "punktWyprzedzenia(2.6,2).y", function() return y_(L.punktWyprzedzenia(PK, 2.6, 2)) end, 10 },
	{ "czyZaczac(nie widzial)", function() return L.czyZaczacPrzelot(false, "brak", true, true, 5, 0) end, true },
	{ "czyZaczac(widzial)", function() return L.czyZaczacPrzelot(true, "brak", true, true, 5, 0) end, false },
	{ "czyZaczac(trwa)", function() return L.czyZaczacPrzelot(false, "trwa", true, true, 5, 0) end, false },
	{ "czyZaczac(poza lasem)", function() return L.czyZaczacPrzelot(false, "brak", false, true, 5, 0) end, false },
	{ "czyZaczac(klient niegotowy)", function() return L.czyZaczacPrzelot(false, "brak", true, false, 5, 0) end, false },
	{ "czyZaczac(przed wolnyOd)", function() return L.czyZaczacPrzelot(false, "brak", true, true, 5, 6) end, false },
	{ "terminPrzelotu(10,13.4,6)", function() return L.terminPrzelotu(10, 13.4, 6) end, 29.4 },
}

-- → (ok, liczba przypadków, lista opisów błędów); tolerancja 1e-6 dla liczb
function L.sprawdzPrzypadki(): (boolean, number, { string })
	local bledy = {}
	for _, p in PRZYPADKI do
		local udalo, wynik = pcall(p[2])
		local dobre
		if not udalo then
			dobre = false
		elseif type(p[3]) == "number" then
			dobre = type(wynik) == "number" and math.abs(wynik - p[3]) <= 1e-6
		else
			dobre = wynik == p[3]
		end
		if not dobre then
			table.insert(bledy, p[1] .. ": jest " .. tostring(wynik) .. ", ma być " .. tostring(p[3]))
		end
	end
	return #bledy == 0, #PRZYPADKI, bledy
end

-- opisy przypadków w kolejności (test sprawdza, że są te same co w logika_pasa.py)
function L.opisyPrzypadkow(): { string }
	local wynik = {}
	for _, p in PRZYPADKI do
		table.insert(wynik, p[1])
	end
	return wynik
end

return L
