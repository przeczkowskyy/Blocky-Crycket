--[[
	Logika — czysta matematyka ruchu i odradzania potworów Lasu (PROJEKT.md rozdz. 3.7). Używa jej TYLKO serwer.

	Nie dotyka instancji, zegara ani Random: same liczby, napisy, wartości logiczne i tabele liczb. Wierną kopią jest
	swiat/las_potwory/logika.py (te same funkcje, nazwy snake_case, ta sama kolejność argumentów); testy w Pythonie
	(testy/test_logiki.py) sprawdzają lustro, a ten moduł sprawdza się sam: sprawdzPrzypadki() liczy te same 70
	przypadków wzorcowych z tabeli 3.7a (serwer woła ją przy starcie i zapisuje wynik w atrybucie ZgodnoscLogiki).

	API (L = długość pętli parametru; L ≤ 0 oznacza „stoi w miejscu”, np. Strażnik):
		cel(naraz, maks, gracze) → n                     ile potworów ma strefa (rozdz. 3.5)
		czasOdrodzenia(baza, graczeWStrefie) → s         skracanie 0,15 na gracza, najmniej 10 s
		przod(a, b, L) → d                               odległość do przodu po pętli, [0; L); L ≤ 0 → math.huge
		punktTrasy(trasa, s) → (x, y, z, yaw)            punkt i kierunek na trasie (pętla albo tam i z powrotem)
		krokGrup(s, dlugosc, stoi, L, krok, odstep) → (s2, zbiezne)   jeden krok wszystkich grup z odstępem
		przodDo(sCel, s, dlugosc, L) → d                 do ogona najbliższej grupy przed sCel
		tylDo(sCel, s, L) → d                            od czoła najbliższej grupy za sCel
		minal(sStary, sNowy, sCel, L) → bool             czy ruch przeszedł przez sCel (albo stoi ≤ 0,5 od niego)
		wGrupie(sGrupy, miejsce, odstepWGrupie, L) → s   parametr członka grupy na miejscu `miejsce`
		rozdzialStartowy(cel, grup, miejsc) → {{grupa, miejsce}}
		poczatkowePolozenia(n, L) → {s}
		wolnyDom(domy, gracze, ostatni, blokada) → i?    domy i gracze jako {x, z}; karuzela od ostatni + 1
		krokDo(x, z, cx, cz, krok) → (x2, z2, doszedl)
		swiatZLasu(x, y, z) → (x, y, z)                  (−x, y, −2000 − z); tylko testy i komunikaty
		yaw(dx, dz) → r                                  CFrame.Angles(0, r, 0).LookVector = kierunek (dx; dz)
		sprawdzPrzypadki() → (ok, n, bledy)              n = 70 przy pełnej tabeli 3.7a

	Odczytania kontraktu (te same w logika.py): yaw = atan2(0 − dx, 0 − dz) (zapis −dx dałby −0 i −π zamiast π);
	w minal „bliżej niż 0,5” to ≤ 0,5 (wymaga tego przypadek minal(10, 12.5, 13, 100) = true); reszta z dzielenia po
	pętli zawsze w [0; L). krokGrup zwraca drugą wartość `zbiezne` (false tylko przy złych danych — wtedy nikt się
	nie rusza, a serwer robi warn raz na strefę); lustro w Pythonie zwraca tylko listę.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local HUGE = math.huge

-- reszta z dzielenia w [0; dl) — % w Luau dzieli z podłogą; zaokrąglenie może dać dokładnie dl, wtedy 0
local function mod(a: number, dl: number): number
	local d = a % dl
	if d >= dl then
		d -= dl
	end
	if d < 0 then
		d = 0
	end
	return d
end

------------------------------------------------------------------ odradzanie
function L.cel(naraz: number, maks: number, gracze: number): number
	local g = math.max(1, gracze)
	local pol = math.ceil(naraz / 2)
	local c
	if g <= 8 then
		c = pol + (naraz - pol) * (g - 1) / 7
	else
		c = naraz + (maks - naraz) * math.min(1, (g - 8) / 12)
	end
	return math.floor(c + 0.5)
end

function L.czasOdrodzenia(baza: number, graczeWStrefie: number): number
	local g = math.max(1, graczeWStrefie)
	return math.max(10, baza / (1 + 0.15 * (g - 1)))
end

------------------------------------------------------------------ pętla
function L.przod(a: number, b: number, dl: number): number
	if dl <= 0 then
		return HUGE
	end
	return mod(b - a, dl)
end

function L.yaw(dx: number, dz: number): number
	return math.atan2(0 - dx, 0 - dz)
end

-- punkt na odcinku i → j (numery od 1) w ułamku t; wstecz = kierunek odwrócony
local function naOdcinku(trasa, i: number, j: number, t: number, wstecz: boolean): (number, number, number, number)
	local x = trasa.x[i] + (trasa.x[j] - trasa.x[i]) * t
	local y = trasa.y[i] + (trasa.y[j] - trasa.y[i]) * t
	local z = trasa.z[i] + (trasa.z[j] - trasa.z[i]) * t
	local dx = trasa.x[j] - trasa.x[i]
	local dz = trasa.z[j] - trasa.z[i]
	if wstecz then
		dx, dz = -dx, -dz
	end
	return x, y, z, L.yaw(dx, dz)
end

local function ulamek(dl, i: number, s: number): number
	local dlug = dl[i + 1] - dl[i]
	if dlug > 0 then
		return (s - dl[i]) / dlug
	end
	return 0
end

-- Pętla (zamknieta): n punktów, dl ma n + 1 wpisów, odcinek n wraca z ostatniego punktu do pierwszego.
-- Tam i z powrotem: dl ma n wpisów, Lp = dl[n], L = 2 × Lp; dla s > Lp punkt L − s i kierunek odwrócony.
-- W wierzchołku obowiązuje odcinek, który się w nim KOŃCZY (w s = 0 — pierwszy odcinek).
function L.punktTrasy(trasa, s: number): (number, number, number, number)
	local n = #trasa.x
	local dlPetli = trasa.L
	local dl = trasa.dl
	if dlPetli <= 0 or n < 2 then
		return trasa.x[1], trasa.y[1], trasa.z[1], trasa.yaw or 0
	end
	s = mod(s, dlPetli)
	if trasa.zamknieta then
		for i = 1, n do
			if s <= dl[i + 1] then
				return naOdcinku(trasa, i, (i % n) + 1, ulamek(dl, i, s), false)
			end
		end
		return naOdcinku(trasa, n, 1, 1, false)
	end
	local lp = dl[n]
	if s <= lp then
		for i = 1, n - 1 do
			if s <= dl[i + 1] then
				return naOdcinku(trasa, i, i + 1, ulamek(dl, i, s), false)
			end
		end
		return naOdcinku(trasa, n - 1, n, 1, false)
	end
	local sw = dlPetli - s -- droga powrotna: ten sam punkt co sw na drodze tam
	for i = n - 1, 1, -1 do
		if sw >= dl[i] then
			return naOdcinku(trasa, i, i + 1, ulamek(dl, i, sw), true)
		end
	end
	return naOdcinku(trasa, 1, 2, 0, true)
end

-- Grupa i przesuwa się o kr_i = min(krok, luka do ogona grupy przed nią + krok tamtej − odstęp), liczone
-- jednocześnie (punkt stały, najwyżej 2n + 2 przejść). Stojące mają kr = 0. Brak zbieżności → wszystkie kr = 0.
function L.krokGrup(s: { number }, dlugosc: { number }, stoi: { boolean }, dl: number, krok: number, odstep: number): ({ number }, boolean)
	local n = #s
	if dl <= 0 or n == 0 then
		return table.clone(s), true
	end
	local kr = {}
	for i = 1, n do
		kr[i] = if stoi[i] then 0 else krok
	end
	local zbiezne = false
	for _ = 1, 2 * n + 2 do
		local zmiana = false
		for i = 1, n do
			if not stoi[i] then
				local lim = dl - dlugosc[i] - odstep
				for k = 1, n do
					if k ~= i then
						lim = math.min(lim, L.przod(s[i], s[k], dl) - dlugosc[k] + kr[k] - odstep)
					end
				end
				local nowy = math.min(math.max(lim, 0), krok)
				if nowy < kr[i] then
					kr[i] = nowy
					zmiana = true
				end
			end
		end
		if not zmiana then
			zbiezne = true
			break
		end
	end
	local wynik = {}
	for i = 1, n do
		local k = if zbiezne then kr[i] else 0
		wynik[i] = mod(s[i] + k, dl)
	end
	return wynik, zbiezne
end

function L.przodDo(sCel: number, s: { number }, dlugosc: { number }, dl: number): number
	local wynik = HUGE
	for k = 1, #s do
		wynik = math.min(wynik, L.przod(sCel, s[k], dl) - dlugosc[k])
	end
	return wynik
end

function L.tylDo(sCel: number, s: { number }, dl: number): number
	local wynik = HUGE
	for k = 1, #s do
		wynik = math.min(wynik, L.przod(s[k], sCel, dl))
	end
	return wynik
end

function L.minal(sStary: number, sNowy: number, sCel: number, dl: number): boolean
	if dl <= 0 then
		return true
	end
	if L.przod(sStary, sCel, dl) <= L.przod(sStary, sNowy, dl) + 1e-9 then
		return true
	end
	return math.min(L.przod(sNowy, sCel, dl), L.przod(sCel, sNowy, dl)) <= 0.5
end

function L.wGrupie(sGrupy: number, miejsce: number, odstepWGrupie: number, dl: number): number
	if dl <= 0 then
		return 0
	end
	return mod(sGrupy - (miejsce - 1) * odstepWGrupie, dl)
end

------------------------------------------------------------------ start
function L.rozdzialStartowy(cel: number, grup: number, miejsc: number): { { number } }
	local c = math.min(cel, grup * miejsc)
	local wynik = {}
	for i = 0, c - 1 do
		if miejsc == 1 then
			table.insert(wynik, { math.floor(i * grup / c) + 1, 1 })
		else
			table.insert(wynik, { (i % grup) + 1, math.floor(i / grup) + 1 })
		end
	end
	return wynik
end

function L.poczatkowePolozenia(n: number, dl: number): { number }
	local wynik = {}
	for i = 1, n do
		wynik[i] = (i - 1) * dl / n
	end
	return wynik
end

------------------------------------------------------------------ domy i krok po prostej
function L.wolnyDom(domy: { { number } }, gracze: { { number } }, ostatni: number, blokada: number): number?
	local n = #domy
	for k = 1, n do
		local i = ((ostatni + k - 1) % n) + 1
		local dx, dz = domy[i][1], domy[i][2]
		local wolny = true
		for _, g in gracze do
			local ox, oz = g[1] - dx, g[2] - dz
			if math.sqrt(ox * ox + oz * oz) < blokada then
				wolny = false
				break
			end
		end
		if wolny then
			return i
		end
	end
	return nil
end

function L.krokDo(x: number, z: number, cx: number, cz: number, krok: number): (number, number, boolean)
	local dx, dz = cx - x, cz - z
	local d = math.sqrt(dx * dx + dz * dz)
	if d <= krok or d <= 0 then
		return cx, cz, true
	end
	return x + dx / d * krok, z + dz / d * krok, false
end

function L.swiatZLasu(x: number, y: number, z: number): (number, number, number)
	return 0 - x, y, -2000 - z
end

------------------------------------------------------------------ przypadki wzorcowe (tabela 3.7a)
local TOL = 1e-4

local function zgodne(a: any, b: any): boolean
	if type(b) == "number" then
		if type(a) ~= "number" then
			return false
		end
		if b == HUGE or b == -HUGE then
			return a == b
		end
		return math.abs(a - b) <= TOL
	elseif type(b) == "table" then
		if type(a) ~= "table" or #a ~= #b then
			return false
		end
		for i = 1, #b do
			if not zgodne(a[i], b[i]) then
				return false
			end
		end
		return true
	end
	return a == b
end

local function opisz(v: any): string
	if type(v) == "table" then
		local czesci = {}
		for i = 1, #v do
			czesci[i] = opisz(v[i])
		end
		return "{" .. table.concat(czesci, ", ") .. "}"
	elseif type(v) == "number" then
		return string.format("%.4f", v)
	end
	return tostring(v)
end

local T1 = { x = { 0, 10, 10 }, y = { 0, 0, 0 }, z = { 0, 0, 10 }, dl = { 0, 10, 20, 34.1421356 }, L = 34.1421356, zamknieta = true }
local T2 = { x = { 0, 10, 10 }, y = { 0, 0, 0 }, z = { 0, 0, 10 }, dl = { 0, 10, 20 }, L = 40, zamknieta = false }
local F, P = false, true

-- { opis, f = funkcja bez argumentów (wiele wyników pakujemy w tabelę), w = oczekiwany wynik }
local PRZYPADKI = {
	{ opis = "cel(6,9,0)", f = function() return L.cel(6, 9, 0) end, w = 3 },
	{ opis = "cel(6,9,1)", f = function() return L.cel(6, 9, 1) end, w = 3 },
	{ opis = "cel(6,9,4)", f = function() return L.cel(6, 9, 4) end, w = 4 },
	{ opis = "cel(6,9,8)", f = function() return L.cel(6, 9, 8) end, w = 6 },
	{ opis = "cel(6,9,14)", f = function() return L.cel(6, 9, 14) end, w = 8 },
	{ opis = "cel(6,9,20)", f = function() return L.cel(6, 9, 20) end, w = 9 },
	{ opis = "cel(6,9,50)", f = function() return L.cel(6, 9, 50) end, w = 9 },
	{ opis = "cel(2,3,1)", f = function() return L.cel(2, 3, 1) end, w = 1 },
	{ opis = "cel(2,3,20)", f = function() return L.cel(2, 3, 20) end, w = 3 },
	{ opis = "cel(5,7,4)", f = function() return L.cel(5, 7, 4) end, w = 4 },
	{ opis = "cel(1,1,20)", f = function() return L.cel(1, 1, 20) end, w = 1 },
	{ opis = "cel(3,4,12)", f = function() return L.cel(3, 4, 12) end, w = 3 },
	{ opis = "czasOdrodzenia(15,0)", f = function() return L.czasOdrodzenia(15, 0) end, w = 15 },
	{ opis = "czasOdrodzenia(15,1)", f = function() return L.czasOdrodzenia(15, 1) end, w = 15 },
	{ opis = "czasOdrodzenia(15,4)", f = function() return L.czasOdrodzenia(15, 4) end, w = 10.3448 },
	{ opis = "czasOdrodzenia(25,4)", f = function() return L.czasOdrodzenia(25, 4) end, w = 17.2414 },
	{ opis = "czasOdrodzenia(15,8)", f = function() return L.czasOdrodzenia(15, 8) end, w = 10 },
	{ opis = "czasOdrodzenia(25,8)", f = function() return L.czasOdrodzenia(25, 8) end, w = 12.1951 },
	{ opis = "czasOdrodzenia(20,3)", f = function() return L.czasOdrodzenia(20, 3) end, w = 15.3846 },
	{ opis = "przod(10,5,100)", f = function() return L.przod(10, 5, 100) end, w = 95 },
	{ opis = "przod(90,10,100)", f = function() return L.przod(90, 10, 100) end, w = 20 },
	{ opis = "przod(3,3,100)", f = function() return L.przod(3, 3, 100) end, w = 0 },
	{ opis = "przod(1,2,0)", f = function() return L.przod(1, 2, 0) end, w = HUGE },
	{ opis = "punktTrasy(T1,0)", f = function() return { L.punktTrasy(T1, 0) } end, w = { 0, 0, 0, -1.5708 } },
	{ opis = "punktTrasy(T1,5)", f = function() return { L.punktTrasy(T1, 5) } end, w = { 5, 0, 0, -1.5708 } },
	{ opis = "punktTrasy(T1,10)", f = function() return { L.punktTrasy(T1, 10) } end, w = { 10, 0, 0, -1.5708 } },
	{ opis = "punktTrasy(T1,15)", f = function() return { L.punktTrasy(T1, 15) } end, w = { 10, 0, 5, 3.1416 } },
	{ opis = "punktTrasy(T1,27.0710678)", f = function() return { L.punktTrasy(T1, 27.0710678) } end, w = { 5, 0, 5, 0.7854 } },
	{ opis = "punktTrasy(T1,34.1421356)", f = function() return { L.punktTrasy(T1, 34.1421356) } end, w = { 0, 0, 0, -1.5708 } },
	{ opis = "punktTrasy(T1,-5)", f = function() return { L.punktTrasy(T1, -5) } end, w = { 3.5355, 0, 3.5355, 0.7854 } },
	{ opis = "punktTrasy(T2,0)", f = function() return { L.punktTrasy(T2, 0) } end, w = { 0, 0, 0, -1.5708 } },
	{ opis = "punktTrasy(T2,15)", f = function() return { L.punktTrasy(T2, 15) } end, w = { 10, 0, 5, 3.1416 } },
	{ opis = "punktTrasy(T2,20)", f = function() return { L.punktTrasy(T2, 20) } end, w = { 10, 0, 10, 3.1416 } },
	{ opis = "punktTrasy(T2,25)", f = function() return { L.punktTrasy(T2, 25) } end, w = { 10, 0, 5, 0 } },
	{ opis = "punktTrasy(T2,35)", f = function() return { L.punktTrasy(T2, 35) } end, w = { 5, 0, 0, 1.5708 } },
	{ opis = "punktTrasy(T2,40)", f = function() return { L.punktTrasy(T2, 40) } end, w = { 0, 0, 0, -1.5708 } },
	{
		opis = "krokGrup({0,30})",
		f = function() return (L.krokGrup({ 0, 30 }, { 0, 0 }, { F, F }, 100, 2.5, 25)) end,
		w = { 2.5, 32.5 },
	},
	{
		opis = "krokGrup({0,26})",
		f = function() return (L.krokGrup({ 0, 26 }, { 0, 0 }, { F, F }, 100, 2.5, 25)) end,
		w = { 2.5, 28.5 },
	},
	{
		opis = "krokGrup({0,30} stoi 2)",
		f = function() return (L.krokGrup({ 0, 30 }, { 0, 0 }, { F, P }, 100, 2.5, 25)) end,
		w = { 2.5, 30 },
	},
	{
		opis = "krokGrup(4 grupy)",
		f = function() return (L.krokGrup({ 0, 25.3, 50.6, 75.9 }, { 0, 0, 0, 0 }, { F, F, F, F }, 101.2, 1.5, 25)) end,
		w = { 1.5, 26.8, 52.1, 77.4 },
	},
	{
		opis = "krokGrup(4 grupy, stoi 4)",
		f = function() return (L.krokGrup({ 0, 25.3, 50.6, 75.9 }, { 0, 0, 0, 0 }, { F, F, F, P }, 101.2, 1.5, 25)) end,
		w = { 0.9, 25.9, 50.9, 75.9 },
	},
	{
		opis = "krokGrup({0} dł 38.1)",
		f = function() return (L.krokGrup({ 0 }, { 38.1 }, { F }, 63, 2.5, 25)) end,
		w = { 0 },
	},
	{
		opis = "krokGrup(L=0)",
		f = function() return (L.krokGrup({ 5, 10 }, { 0, 0 }, { F, P }, 0, 1, 25)) end,
		w = { 5, 10 },
	},
	{ opis = "przodDo(10,{30,5})", f = function() return L.przodDo(10, { 30, 5 }, { 0, 0 }, 100) end, w = 20 },
	{ opis = "przodDo(10,{20},{15})", f = function() return L.przodDo(10, { 20 }, { 15 }, 100) end, w = -5 },
	{ opis = "przodDo(10,{})", f = function() return L.przodDo(10, {}, {}, 100) end, w = HUGE },
	{ opis = "tylDo(10,{30,5})", f = function() return L.tylDo(10, { 30, 5 }, 100) end, w = 5 },
	{ opis = "tylDo(10,{})", f = function() return L.tylDo(10, {}, 100) end, w = HUGE },
	{ opis = "minal(98,1,0,100)", f = function() return L.minal(98, 1, 0, 100) end, w = true },
	{ opis = "minal(10,12.5,12,100)", f = function() return L.minal(10, 12.5, 12, 100) end, w = true },
	{ opis = "minal(10,12.5,13,100)", f = function() return L.minal(10, 12.5, 13, 100) end, w = true },
	{ opis = "minal(10,10,10.3,100)", f = function() return L.minal(10, 10, 10.3, 100) end, w = true },
	{ opis = "minal(10,10,11,100)", f = function() return L.minal(10, 10, 11, 100) end, w = false },
	{ opis = "minal(5,5,7,0)", f = function() return L.minal(5, 5, 7, 0) end, w = true },
	{ opis = "wGrupie(5,1,12.7,100)", f = function() return L.wGrupie(5, 1, 12.7, 100) end, w = 5 },
	{ opis = "wGrupie(5,3,12.7,100)", f = function() return L.wGrupie(5, 3, 12.7, 100) end, w = 79.6 },
	{ opis = "wGrupie(5,2,12.7,0)", f = function() return L.wGrupie(5, 2, 12.7, 0) end, w = 0 },
	{ opis = "rozdzialStartowy(3,9,1)", f = function() return L.rozdzialStartowy(3, 9, 1) end, w = { { 1, 1 }, { 4, 1 }, { 7, 1 } } },
	{ opis = "rozdzialStartowy(3,2,5)", f = function() return L.rozdzialStartowy(3, 2, 5) end, w = { { 1, 1 }, { 2, 1 }, { 1, 2 } } },
	{ opis = "rozdzialStartowy(2,1,4)", f = function() return L.rozdzialStartowy(2, 1, 4) end, w = { { 1, 1 }, { 1, 2 } } },
	{ opis = "#rozdzialStartowy(12,2,5)", f = function() return #L.rozdzialStartowy(12, 2, 5) end, w = 10 },
	{
		opis = "poczatkowePolozenia(7,177.3)",
		f = function() return L.poczatkowePolozenia(7, 177.3) end,
		w = { 0, 25.3286, 50.6571, 75.9857, 101.3143, 126.6429, 151.9714 },
	},
	{
		opis = "wolnyDom(3 domy, ostatni 0)",
		f = function() return L.wolnyDom({ { 0, 0 }, { 100, 0 }, { 0, 100 } }, { { 5, 5 } }, 0, 18) end,
		w = 2,
	},
	{
		opis = "wolnyDom(3 domy, ostatni 2)",
		f = function() return L.wolnyDom({ { 0, 0 }, { 100, 0 }, { 0, 100 } }, { { 5, 5 } }, 2, 18) end,
		w = 3,
	},
	{
		opis = "wolnyDom(2 domy zajęte)",
		f = function() return L.wolnyDom({ { 0, 0 }, { 100, 0 } }, { { 5, 5 }, { 95, 0 } }, 1, 18) end,
		w = nil,
	},
	{ opis = "wolnyDom(gracz na 18)", f = function() return L.wolnyDom({ { 0, 0 } }, { { 18, 0 } }, 1, 18) end, w = 1 },
	{ opis = "krokDo(0,0,3,4,2)", f = function() return { L.krokDo(0, 0, 3, 4, 2) } end, w = { 1.2, 1.6, false } },
	{ opis = "krokDo(0,0,3,4,6)", f = function() return { L.krokDo(0, 0, 3, 4, 6) } end, w = { 3, 4, true } },
	{ opis = "swiatZLasu(206.3,0,294.5)", f = function() return { L.swiatZLasu(206.3, 0, 294.5) } end, w = { -206.3, 0, -2294.5 } },
	{ opis = "swiatZLasu(0,32,-373)", f = function() return { L.swiatZLasu(0, 32, -373) } end, w = { 0, 32, -1627 } },
}

-- → (ok, n, bledy): n = liczba przypadków (70), bledy = opisy niezgodnych (pusta lista przy zgodności)
function L.sprawdzPrzypadki(): (boolean, number, { string })
	local bledy = {}
	for _, p in PRZYPADKI do
		local udalo, wynik = pcall(p.f)
		if not udalo then
			table.insert(bledy, p.opis .. ": błąd " .. tostring(wynik))
		elseif not zgodne(wynik, p.w) then
			table.insert(bledy, p.opis .. " = " .. opisz(wynik) .. ", oczekiwano " .. opisz(p.w))
		end
	end
	return #bledy == 0, #PRZYPADKI, bledy
end

return L
