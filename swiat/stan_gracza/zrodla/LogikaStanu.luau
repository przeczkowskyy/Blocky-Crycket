--[[
	LogikaStanu — czysta logika stanu gracza (ModuleScript w Workspace/StanGracza/Moduly; używa go SerwerStanu).
	Bez Roblox: niczego nie zmienia w świecie, nie używa zegara ani Random. Lustro w Pythonie:
	swiat/stan_gracza/logika_stanu.py (te same nazwy w snake_case); testy uruchamiają ten plik w interpreterze
	tools/walka/luau_mini.py i porównują z lustrem, a lustro — z tools/walka (tempo.py, wzorcowe.py).
	Dlatego tylko podzbiór Luau, który rozumie luau_mini: bez string.match, table.sort, table.clone, ipairs i `::`.

	D = DaneStanu (wygenerowane przez dane.py). Funkcje:
		xpDoNastepnego(D, poziom)                 → doświadczenie z poziomu L na L+1 (krzywa A × L^B)
		awans(D, poziom, xp, dodaj)               → poziom, xp, ile awansów
		pula(D, poziom), sloty(D, poziom)         → punkty statystyk z poziomu, liczba slotów umiejętności
		rozdziel(D, rozklad, punkty)              → { sila = …, … } (metoda największych reszt)
		poziomZ(D, v), statystykaZ(D, v)          → atrybut gracza → liczba całkowita w granicach (statystyka: nil, gdy
		                                            to nie liczba)
		klasaSilnika(D, idKlasy)                  → klasa silnika, czy znana
		rozkladZClassData(D, stats)               → rozkład albo nil, powód
		opisBohatera(D, klasa, poziom, st)        → opis postaci dla Silnik.symuluj
		noweStatystyki(D, obecne, staraBaza, cel, wytrenowane) → wartości sześciu atrybutów po zmianie klasy / poziomu
		czystyLup(D, lup), czystyPrzyrost(D, info) → kopia ze znanymi polami albo nil, powód
		sumaLupow(D, lista), nowyProfil(D), rowne(a, b), sprawdzPrzypadki(D) → ok, n, bledy
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local function liczba(v): boolean
	return type(v) == "number" and v == v and v > -math.huge and v < math.huge
end

function L.xpDoNastepnego(D, poziom: number): number
	return math.max(1, math.floor(D.krzywa.a * poziom ^ D.krzywa.b + 0.5))
end

function L.poziomZ(D, v): number
	if not liczba(v) then
		return 1
	end
	if v >= D.limity.poziom_maks then
		return D.limity.poziom_maks
	end
	if v < 1 then
		return 1
	end
	return math.floor(v)
end

function L.statystykaZ(D, v): number?
	if not liczba(v) then
		return nil
	end
	if v <= 0 then
		return 0
	end
	if v >= D.limity.statystyka_maks then
		return D.limity.statystyka_maks
	end
	return math.floor(v)
end

function L.awans(D, poziom, xp, dodaj)
	local maks = D.limity.poziom_maks
	poziom = L.poziomZ(D, poziom)
	xp = math.max(0, if liczba(xp) then xp else 0) + math.max(0, if liczba(dodaj) then dodaj else 0)
	local ile = 0
	while poziom < maks do
		local potrzeba = L.xpDoNastepnego(D, poziom)
		if xp < potrzeba then
			break
		end
		xp -= potrzeba
		poziom += 1
		ile += 1
	end
	if poziom >= maks then
		xp = math.min(xp, L.xpDoNastepnego(D, poziom))
	end
	return poziom, xp, ile
end

function L.pula(D, poziom: number): number
	return D.pula.baza + D.pula.na_poziom * (poziom - 1)
end

function L.sloty(D, poziom: number): number
	for _, prog in D.sloty do
		if poziom >= prog.od then
			return prog.n
		end
	end
	return 0
end

-- czy statystyka a idzie przed b przy rozdawaniu reszty: większa część ułamkowa, potem większy udział, potem kolejność
local function przed(a, b, ulamek, rozklad, indeks): boolean
	if ulamek[a] ~= ulamek[b] then
		return ulamek[a] > ulamek[b]
	end
	if rozklad[a] ~= rozklad[b] then
		return rozklad[a] > rozklad[b]
	end
	return indeks[a] < indeks[b]
end

function L.rozdziel(D, rozklad, punkty: number)
	local S = D.statystyki
	local st, ulamek, indeks = {}, {}, {}
	local suma = 0
	for i, s in S do
		local dokladne = rozklad[s] * punkty
		st[s] = math.floor(dokladne + 1e-9)
		ulamek[s] = dokladne - st[s]
		indeks[s] = i
		suma += st[s]
	end
	-- kolejność rozdawania reszty: sortowanie przez wybieranie (sześć pozycji; luau_mini nie ma table.sort)
	local kolejnosc = {}
	local wolne = {}
	for _, s in S do
		table.insert(wolne, s)
	end
	while #wolne > 0 do
		local najlepsza = 1
		for j = 2, #wolne do
			if przed(wolne[j], wolne[najlepsza], ulamek, rozklad, indeks) then
				najlepsza = j
			end
		end
		table.insert(kolejnosc, wolne[najlepsza])
		local reszta = {}
		for j = 1, #wolne do
			if j ~= najlepsza then
				table.insert(reszta, wolne[j])
			end
		end
		wolne = reszta
	end
	local reszta = punkty - suma
	local i = 0
	while reszta > 0 do
		local s = kolejnosc[(i % #kolejnosc) + 1]
		st[s] += 1
		reszta -= 1
		i += 1
	end
	return st
end

function L.klasaSilnika(D, idKlasy): (string, boolean)
	if type(idKlasy) == "string" and D.klasy_gracza[idKlasy] ~= nil then
		return D.klasy_gracza[idKlasy], true
	end
	return D.klasa_domyslna, false
end

function L.rozkladZClassData(D, stats)
	local S = D.statystyki
	if type(stats) ~= "table" or #stats ~= #S then
		return nil, "zla_lista"
	end
	local suma = 0
	for i = 1, #S do
		local v = stats[i]
		if not liczba(v) or v < 0 or v > 100 then
			return nil, "zla_liczba"
		end
		suma += v
	end
	if math.abs(suma - 100) > 1e-9 then
		return nil, "suma_nie_100"
	end
	local r = {}
	for i, s in S do
		r[s] = stats[i] / 100
	end
	return r, "ok"
end

function L.opisBohatera(D, klasa: string, poziom: number, st)
	local W = D.wzor
	local statystyki = {}
	for _, s in D.statystyki do
		statystyki[s] = st[s]
	end
	local umiejetnosci = {}
	local n = L.sloty(D, poziom)
	for i = 1, math.min(n, #D.umiejetnosci[klasa]) do
		table.insert(umiejetnosci, D.umiejetnosci[klasa][i])
	end
	local p = {
		nazwa = D.nazwy_klas[klasa],
		klasa = klasa,
		poziom = poziom,
		statystyki = statystyki,
		bron = { obrazenia = W.bron_baza + W.bron_na_poziom * poziom },
		pancerz_przedmiotow = W.pancerz_baza + W.pancerz_na_poziom * poziom,
		umiejetnosci = umiejetnosci,
	}
	if D.tarcza[klasa] == true then
		p.tarcza = { blok = W.blok_tarczy }
	end
	return p
end

function L.noweStatystyki(D, obecne, staraBaza, cel, wytrenowane)
	local w = {}
	for _, s in D.statystyki do
		local teraz = L.statystykaZ(D, obecne[s])
		local v
		if staraBaza == nil or teraz == nil then
			v = cel[s] + (wytrenowane[s] or 0)
		else
			v = teraz + cel[s] - staraBaza[s]
		end
		w[s] = L.statystykaZ(D, v)
	end
	return w
end

local function calkowita(v, maks: number): boolean
	return liczba(v) and v >= 0 and v <= maks and math.floor(v) == v
end

function L.nazwaOk(D, t): boolean
	if type(t) ~= "string" or #t == 0 or #t > D.limity.dlugosc_nazwy then
		return false
	end
	for i = 1, #t do
		local b = string.byte(t, i)
		if not ((b >= 48 and b <= 57) or (b >= 65 and b <= 90) or (b >= 97 and b <= 122) or b == 95) then
			return false
		end
	end
	return true
end

function L.czystyLup(D, lup)
	if type(lup) ~= "table" then
		return nil, "zly_lup"
	end
	local w = {}
	for _, pole in D.pola_lupu do
		local v = lup[pole]
		if v == nil then
			v = 0
		end
		if not calkowita(v, D.limity.lup[pole]) then
			return nil, "zle_" .. pole
		end
		w[pole] = v
	end
	local kraina = lup.kraina
	if kraina == nil or kraina == "" then
		kraina = ""
	elseif not L.nazwaOk(D, kraina) then
		return nil, "zla_kraina"
	end
	w.kraina = kraina
	return w, "ok"
end

function L.czystyPrzyrost(D, info)
	if type(info) ~= "table" then
		return nil, "zly_przyrost"
	end
	local s = nil
	for nazwa, a in D.atrybuty_statystyk do
		if a == info.atrybut then
			s = nazwa
		end
	end
	if s == nil and type(info.statystyka) == "string" and D.atrybuty_statystyk[info.statystyka] ~= nil then
		s = info.statystyka
	end
	if s == nil then
		return nil, "zla_statystyka"
	end
	local n = info.przyrost
	if not calkowita(n, D.limity.przyrost_maks) or n < 1 then
		return nil, "zly_przyrost"
	end
	return { s, n }, "ok"
end

function L.sumaLupow(D, lista)
	local w = {}
	for _, p in D.pola_lupu do
		w[p] = 0
	end
	local tokeny = {}
	for _, lup in lista do
		for _, p in D.pola_lupu do
			w[p] += lup[p]
		end
		if lup.tokeny_krainy > 0 and lup.kraina ~= "" then
			tokeny[lup.kraina] = (tokeny[lup.kraina] or 0) + lup.tokeny_krainy
		end
	end
	w.tokeny = tokeny
	return w
end

function L.nowyProfil(D)
	local wytrenowane = {}
	for _, s in D.statystyki do
		wytrenowane[s] = 0
	end
	return {
		wersja = D.wersja_profilu,
		klasa = D.klasa_domyslna,
		poziom = 1,
		xp = 0,
		zloto = 0,
		gemy = 0,
		tokeny = {},
		shardy = 0,
		wytrenowane = wytrenowane,
		baza = nil,
		walki = { wygrane = 0, przegrane = 0 },
		awanse = 0,
	}
end

-- równość głęboka (tabele: te same klucze i wartości; liczby z tolerancją 1e-9)
function L.rowne(a, b): boolean
	if type(a) ~= type(b) then
		return false
	end
	if type(a) == "number" then
		return math.abs(a - b) <= 1e-9
	end
	if type(a) ~= "table" then
		return a == b
	end
	for k, v in a do
		if not L.rowne(v, b[k]) then
			return false
		end
	end
	for k in b do
		if a[k] == nil then
			return false
		end
	end
	return true
end

------------------------------------------------------------------ przypadki wzorcowe (lustro w Pythonie je liczy)
local function falsz(v)
	if v == nil then
		return false
	end
	return v
end

function L.sprawdzPrzypadki(D)
	local P = D.przypadki
	local bledy, n = {}, 0
	local function sprawdz(nazwa: string, i: number, ok: boolean)
		n += 1
		if not ok then
			table.insert(bledy, nazwa .. " #" .. tostring(i))
		end
	end
	for i, c in P.xp do
		sprawdz("xp", i, L.xpDoNastepnego(D, c.poziom) == c.wynik)
	end
	for i, c in P.awans do
		local p, x, ile = L.awans(D, c.poziom, c.xp, c.dodaj)
		sprawdz("awans", i, L.rowne({ p, x, ile }, c.wynik))
	end
	for i, c in P.rozdziel do
		sprawdz("rozdziel", i, L.rowne(L.rozdziel(D, D.rozklady[c.klasa], c.punkty), c.wynik))
	end
	for i, c in P.opis do
		sprawdz("opis", i, L.rowne(L.opisBohatera(D, c.klasa, c.poziom, c.st), c.wynik))
	end
	for i, c in P.nowe do
		local baza = if c.baza == false then nil else c.baza
		sprawdz("nowe", i, L.rowne(L.noweStatystyki(D, c.obecne, baza, c.cel, c.wytrenowane), c.wynik))
	end
	for i, c in P.lup do
		local w, powod = L.czystyLup(D, c.lup)
		sprawdz("lup", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.przyrost do
		local w, powod = L.czystyPrzyrost(D, c.info)
		sprawdz("przyrost", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.poziom_z do
		sprawdz("poziom_z", i, L.poziomZ(D, c.v) == c.wynik)
	end
	for i, c in P.statystyka_z do
		sprawdz("statystyka_z", i, L.rowne(falsz(L.statystykaZ(D, c.v)), c.wynik))
	end
	for i, c in P.rozklad do
		local w, powod = L.rozkladZClassData(D, c.stats)
		sprawdz("rozklad", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	return #bledy == 0, n, bledy
end

return L
