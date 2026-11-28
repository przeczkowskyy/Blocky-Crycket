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
		czystyWydatek(D, info), czystaPremia(D, premia) → kopia albo nil, powód   (17.11.2026, swiat/pety_proba)
		czystyPrzychod(D, info)                   → kopia albo nil, powód   (25.11.2026, Pety "przychod" — zagroda)
		czystaSprzedaz(D, info)                   → kopia albo nil, powód   (26.11.2026, Pety "sprzedaj" — sprzedaż petów)
		wydaj(D, zloto, ile)                      → Złoto po, brakuje (nigdy poniżej zera)
		premiaLupu(D, lup, premia)                → { zloto, doswiadczenie } — dodatek od aktywnego peta
	lupZwyklego(D, poziom)                    → Złoto za wygraną ze zwykłym potworem na tym poziomie (17.11.2026)
	karaPrzegranej(D, zloto, poziomPotwora, procent) → Złoto zabrane za przegraną (propozycja D-098)
	czystyModyfikator(D, mod), czysteDanePakietu(D, v) → kopia albo nil, powód   (18.11.2026, Sygnaly/Modyfikatory
	                                            i Sygnaly/DanePakietu)
	zlozModyfikatory(D, mody)                 → złożenie wpisów wszystkich źródeł
	opisZModyfikatorami(D, opis, z)           → opis bohatera dla silnika z modyfikatorami (bez nich — ten sam)
	pulaSama(D, poziom, punktyWlaczone)       → punkty rozdzielane samo rozkładem klasy (18.11.2026, D-097)
	czyStraznik(D, gatunek)                   → strażnik biomu (Gemy za pierwsze pokonanie, D-099)
	zapisywalne(D, v, G), migrujProfil(D, dane), czystyProfil(D, p) → kopia albo nil, powód   (zapis postępu)
	profilDoZapisu(D, p)                      → kopia samych zapisywanych pól profilu
	zmianaStatystyki(D, znana, nowa, pula)    → wartość, pula po, "ok" | "brak_punktow" | "cofnieta"
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

local function wytrenowaneZero(D)
	local w = {}
	for _, s in D.statystyki do
		w[s] = 0
	end
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
		-- wersja 2: pety (kopie = shardy peta, D-058) i licznik wydatków Złota na cel (np. kupione jajka)
		pety = { kopie = {}, aktywny = nil, premia = { zloto = 0, doswiadczenie = 0 } },
		wydatki = {},
		-- wersja 3 (18.11.2026): dane pakietów (Sygnaly/DanePakietu) — pakiety[pakiet] = tabela pakietu
		pakiety = {},
		-- punkty statystyk do rozdania (18.11.2026, D-097)
		punkty = { pula = 0, rozdane = wytrenowaneZero(D), poziom = 1 },
		-- strażnicy pokonani choć raz (gatunek → true) — Gemy za pierwsze pokonanie (D-099, 18.11.2026)
		straznicy = {},
		-- wersja 4 (18.11.2026, zapis postępu): wybrana klasa (atrybut Class) i zapisywane atrybuty innych pakietów
		idKlasy = nil,
		-- 27.11.2026 (Karol: „Tak, zapisuj rasę”): wybrana rasa (atrybut Race, D.rasy_gracza); brak = jak dotąd
		idRasy = nil,
		atrybuty = {},
	}
end

------------------------------------------------------------------ wydatki Złota i pety (17.11.2026, swiat/pety_proba)
function L.czystyWydatek(D, info)
	if type(info) ~= "table" then
		return nil, "zly_wydatek"
	end
	local ile = info.ile
	if not calkowita(ile, D.wydatki.kwota_maks) or ile < 1 then
		return nil, "zla_kwota"
	end
	local znane = false
	for _, z in D.wydatki.zrodla do
		if info.zrodlo == z then
			znane = true
		end
	end
	if type(info.zrodlo) ~= "string" or not znane then
		return nil, "zle_zrodlo"
	end
	if not L.nazwaOk(D, info.cel) then
		return nil, "zly_cel"
	end
	return { ile = ile, zrodlo = info.zrodlo, cel = info.cel }, "ok"
end

function L.czystaSprzedaz(D, info)
	if type(info) ~= "table" then
		return nil, "zla_sprzedaz"
	end
	local pety = info.pety
	if type(pety) ~= "table" or #pety > 0 then
		return nil, "zle_pety"
	end
	local n, kopia = 0, {}
	for k, v in pety do
		n += 1
		if not L.nazwaOk(D, k) or not calkowita(v, D.pety.kopii_maks) or v < 1 then
			return nil, "zle_pety"
		end
		kopia[k] = v
	end
	if n < 1 or n > D.pety.rodzajow_maks then
		return nil, "zle_pety"
	end
	local ile = info.ile
	if not calkowita(ile, D.przychody.kwota_maks) or ile < 1 then
		return nil, "zla_kwota"
	end
	local znane = false
	for _, z in D.przychody.zrodla do
		if info.zrodlo == z then
			znane = true
		end
	end
	if type(info.zrodlo) ~= "string" or not znane then
		return nil, "zle_zrodlo"
	end
	if not L.nazwaOk(D, info.cel) then
		return nil, "zly_cel"
	end
	return { pety = kopia, ile = ile, zrodlo = info.zrodlo, cel = info.cel }, "ok"
end

function L.czystyPrzychod(D, info)
	if type(info) ~= "table" then
		return nil, "zly_przychod"
	end
	local ile = info.ile
	if not calkowita(ile, D.przychody.kwota_maks) or ile < 1 then
		return nil, "zla_kwota"
	end
	local znane = false
	for _, z in D.przychody.zrodla do
		if info.zrodlo == z then
			znane = true
		end
	end
	if type(info.zrodlo) ~= "string" or not znane then
		return nil, "zle_zrodlo"
	end
	if not L.nazwaOk(D, info.cel) then
		return nil, "zly_cel"
	end
	return { ile = ile, zrodlo = info.zrodlo, cel = info.cel }, "ok"
end

function L.wydaj(D, zloto, ile: number): (number, number)
	local z = 0
	if liczba(zloto) and zloto >= 0 then
		z = math.floor(math.min(zloto, D.limity.waluta_maks))
	end
	if z < ile then
		return z, ile - z
	end
	return z - ile, 0
end

function L.czystaPremia(D, premia)
	if premia == nil then
		return { zloto = 0, doswiadczenie = 0 }, "ok"
	end
	if type(premia) ~= "table" then
		return nil, "zla_premia"
	end
	local w = {}
	for _, pole in { "zloto", "doswiadczenie" } do
		local v = premia[pole]
		if v == nil then
			v = 0
		end
		if not liczba(v) or v < 0 or v > D.pety.premia_maks then
			return nil, "zla_premia"
		end
		w[pole] = v
	end
	return w, "ok"
end

function L.premiaLupu(D, lup, premia)
	return {
		zloto = math.floor(lup.zloto * premia.zloto + 0.5),
		doswiadczenie = math.floor(lup.doswiadczenie * premia.doswiadczenie + 0.5),
	}
end

------------------------------------------------------------------ kara za przegraną (17.11.2026, propozycja D-098)
function L.lupZwyklego(D, poziom): number
	local g = D.kara.limit_lupu
	return g.baza + g.na_poziom * (L.poziomZ(D, poziom) - 1)
end

-- ułamek `procent` posiadanego Złota (w dół), najwyżej łup zwykłego potwora na poziomie przeciwnika, nigdy więcej,
-- niż gracz ma; procent ≤ 0 albo nie liczba = kara wyłączona
function L.karaPrzegranej(D, zloto, poziomPotwora, procent): number
	local z = L.wydaj(D, zloto, 0)
	if not liczba(procent) or procent <= 0 then
		return 0
	end
	local k = math.floor(z * math.min(procent, 1))
	return math.min(k, L.lupZwyklego(D, poziomPotwora), z)
end

------------------------------------------------------------------ modyfikatory bohatera (18.11.2026, pety D-101, Kowal D-102)
local POLA_MODU = { statystyki = true, procent = true, lup = true, bron = true, pancerz = true, tarcza = true, pasywki = true,
	zaklecie = true }

local function jestAtrybutem(D, a): boolean
	for _, n in D.atrybuty_statystyk do
		if n == a then
			return true
		end
	end
	return false
end

local function zawiera(lista, x): boolean
	for _, y in lista do
		if y == x then
			return true
		end
	end
	return false
end

-- czysta lista (klucze 1..n): liczba elementów albo nil
local function dlugoscListy(t): number?
	if type(t) ~= "table" then
		return nil
	end
	local n = 0
	for _ in t do
		n += 1
	end
	if n ~= #t then
		return nil
	end
	return n
end

function L.czystyModyfikator(D, mod)
	local G = D.modyfikatory
	if type(mod) ~= "table" then
		return nil, "zly_mod"
	end
	for k in mod do
		if not POLA_MODU[k] then
			return nil, "nieznane_pole"
		end
	end
	local w = {}
	for _, spec in { { "statystyki", -G.statystyka_maks, G.statystyka_maks, true }, { "procent", 0, G.procent_maks, false } } do
		local pole, lo, hi, calk = spec[1], spec[2], spec[3], spec[4]
		local t = mod[pole]
		if t ~= nil then
			if type(t) ~= "table" then
				return nil, "zle_" .. pole
			end
			local kopia = {}
			for a, v in t do
				if not jestAtrybutem(D, a) then
					return nil, "zla_statystyka"
				end
				if not liczba(v) or v < lo or v > hi or (calk and math.floor(v) ~= v) then
					return nil, "zle_" .. pole
				end
				if v ~= 0 then
					kopia[a] = v
				end
			end
			w[pole] = kopia
		end
	end
	local t = mod.lup
	if t ~= nil then
		if type(t) ~= "table" then
			return nil, "zly_lup"
		end
		local kopia = {}
		for k, v in t do
			if k ~= "zloto" and k ~= "doswiadczenie" then
				return nil, "zly_lup"
			end
			if not liczba(v) or v < 0 or v > G.lup_maks_zrodla then
				return nil, "zly_lup"
			end
			kopia[k] = v
		end
		w.lup = kopia
	end
	for _, pole in { "bron", "pancerz", "tarcza" } do
		local v = mod[pole]
		if v ~= nil then
			local maks = G[pole .. "_maks"]
			if not liczba(v) or v < -maks or v > maks then
				return nil, "zle_" .. pole
			end
			w[pole] = v
		end
	end
	t = mod.pasywki
	if t ~= nil then
		local n = dlugoscListy(t)
		if n == nil or n > G.pasywek_maks then
			return nil, "zle_pasywki"
		end
		local lista = {}
		for i = 1, n do
			local nazwa = t[i]
			if type(nazwa) ~= "string" or D.pasywki_silnika[nazwa] == nil then
				return nil, "nieznana_pasywka"
			end
			if not zawiera(lista, nazwa) then
				table.insert(lista, nazwa)
			end
		end
		w.pasywki = lista
	end
	local z = mod.zaklecie
	if z ~= nil then
		if type(z) ~= "string" or not zawiera(D.zaklecia_silnika, z) then
			return nil, "nieznane_zaklecie"
		end
		w.zaklecie = z
	end
	return w, "ok"
end

function L.zlozModyfikatory(D, mody)
	local G = D.modyfikatory
	local w = { statystyki = {}, procent = {}, lup = { zloto = 0, doswiadczenie = 0 }, bron = 0, pancerz = 0, tarcza = 0,
		pasywki = {} }
	for _, m in mody do
		for _, pole in { "statystyki", "procent" } do
			for a, v in m[pole] or {} do
				w[pole][a] = (w[pole][a] or 0) + v
			end
		end
		for k, v in m.lup or {} do
			w.lup[k] += v
		end
		for _, pole in { "bron", "pancerz", "tarcza" } do
			w[pole] += m[pole] or 0
		end
		for _, n in m.pasywki or {} do
			if not zawiera(w.pasywki, n) then
				table.insert(w.pasywki, n)
			end
		end
		-- zaklęcie broni: pierwsze z listy (serwer podaje wpisy posortowane według nazwy źródła)
		if w.zaklecie == nil and m.zaklecie ~= nil then
			w.zaklecie = m.zaklecie
		end
	end
	for a, v in w.procent do
		w.procent[a] = math.min(v, G.procent_suma_maks)
	end
	for _, k in { "zloto", "doswiadczenie" } do
		w.lup[k] = math.min(w.lup[k], G.lup_suma_maks)
	end
	return w
end

local function kopiaPlytka(v)
	if type(v) ~= "table" then
		return v
	end
	local w = {}
	for k, x in v do
		w[k] = x
	end
	return w
end

function L.opisZModyfikatorami(D, opis, z)
	local G = D.modyfikatory
	local w = {}
	for k, v in opis do
		w[k] = kopiaPlytka(v)
	end
	for _, s in D.statystyki do
		local d = z.statystyki[D.atrybuty_statystyk[s]] or 0
		if d ~= 0 then
			w.statystyki[s] = math.min(math.max(w.statystyki[s] + d, 0), D.limity.statystyka_maks)
		end
	end
	local pet, jest = {}, false
	for _, s in D.statystyki do
		local p = z.procent[D.atrybuty_statystyk[s]] or 0
		if p > 0 then
			pet[s] = p
			jest = true
		end
	end
	if jest then
		w.pet = pet
	end
	if z.bron ~= 0 then
		w.bron.obrazenia = math.max(1, w.bron.obrazenia + z.bron)
	end
	if z.pancerz ~= 0 then
		w.pancerz_przedmiotow = math.max(0, w.pancerz_przedmiotow + z.pancerz)
	end
	if z.zaklecie ~= nil and w.bron.zaklecie == nil then
		w.bron.zaklecie = z.zaklecie -- zaklęcie broni silnika (podpalenie 25%, trucizna 30% przy ciosie)
	end
	if z.tarcza ~= 0 and w.tarcza ~= nil then
		w.tarcza.blok = math.min(math.max(w.tarcza.blok + z.tarcza, 0), G.blok_maks)
	end
	local premie, sa = {}, false
	for _, n in z.pasywki do
		local p = D.pasywki_silnika[n]
		if p.klasa == "" or p.klasa == opis.klasa then
			for k, v in p.modyfikatory do
				premie[k] = (premie[k] or 0) + v
				sa = true
			end
		end
	end
	if sa then
		local przyciete = {}
		for k, v in premie do
			local g = D.granice_modyfikatorow[k]
			przyciete[k] = math.min(math.max(v, g[1]), g[2])
		end
		w.premie = przyciete
	end
	return w
end

------------------------------------------------------------------ dane pakietów w profilu (18.11.2026)
function L.czysteDanePakietu(D, v)
	return L.zapisywalne(D, v, D.pakiety)
end

-- tabela → kopia z samych zapisywalnych wartości w granicach G (wartosci_maks, glebokosc_maks, napis_maks i — gdy
-- jest — bajty_maks: bajty napisów i kluczy + 8 na wartość) albo nil, powód; dane pakietów i cały profil
function L.zapisywalne(D, v, G)
	local licznik, bajty = 0, 0
	local blad: string? = nil
	local function dolicz(n: number)
		bajty += n
		if G.bajty_maks ~= nil and bajty > G.bajty_maks then
			blad = "za_duzy"
		end
	end
	local function kopia(x, glebokosc: number)
		if blad then
			return nil
		end
		licznik += 1
		if licznik > G.wartosci_maks then
			blad = "za_duzo"
			return nil
		end
		dolicz(8)
		if blad then
			return nil
		end
		local t = type(x)
		if t == "boolean" then
			return x
		elseif t == "number" then
			if not liczba(x) then
				blad = "zla_liczba"
				return nil
			end
			return x
		elseif t == "string" then
			if #x > G.napis_maks then
				blad = "za_dlugi_napis"
				return nil
			end
			dolicz(#x)
			if blad then
				return nil
			end
			return x
		elseif t == "table" then
			if glebokosc >= G.glebokosc_maks then
				blad = "za_gleboko"
				return nil
			end
			local w = {}
			for k, y in x do
				if not (type(k) == "string" or (liczba(k) and math.floor(k) == k)) then
					blad = "zly_klucz"
					return nil
				end
				if type(k) == "string" and #k > G.napis_maks then
					blad = "za_dlugi_napis"
					return nil
				end
				if type(k) == "string" then
					dolicz(#k)
					if blad then
						return nil
					end
				end
				w[k] = kopia(y, glebokosc + 1)
				if blad then
					return nil
				end
			end
			return w
		end
		blad = "zly_typ"
		return nil
	end
	if type(v) ~= "table" then
		return nil, "zly_typ"
	end
	local w = kopia(v, 0)
	if blad then
		return nil, blad
	end
	return w, "ok"
end

------------------------------------------------------------------ zapis postępu (18.11.2026, propozycja; domyślnie wyłączony)
local function glebokaKopia(v)
	if type(v) ~= "table" then
		return v
	end
	local w = {}
	for k, x in v do
		w[k] = glebokaKopia(x)
	end
	return w
end

function L.profilDoZapisu(D, p)
	local w = {}
	for _, pole in D.zapis.pola do
		if p[pole] ~= nil then
			w[pole] = glebokaKopia(p[pole])
		end
	end
	w.wersja = D.wersja_profilu
	return w
end

local function uzupelnij(w, wzor)
	for k, d in wzor do
		if w[k] == nil then
			w[k] = glebokaKopia(d)
		elseif type(d) == "table" and type(w[k]) == "table" then
			uzupelnij(w[k], d)
		end
	end
end

function L.migrujProfil(D, dane)
	if dane == nil then
		return nil, "brak"
	end
	if type(dane) ~= "table" then
		return nil, "zly_profil"
	end
	local w = glebokaKopia(dane)
	local v = w.wersja
	if not liczba(v) then
		v = 1
	end
	if v > D.wersja_profilu then
		return nil, "przyszla_wersja"
	end
	if v < 4 and type(w.punkty) ~= "table" then
		local rozdane = {}
		for _, s in D.statystyki do
			rozdane[s] = 0
		end
		w.punkty = { pula = 0, rozdane = rozdane, poziom = L.poziomZ(D, w.poziom) }
	end
	w.baza = nil
	w.oczekujace = nil
	uzupelnij(w, L.nowyProfil(D))
	w.wersja = D.wersja_profilu
	return w, "ok"
end

local function zaczynaSie(n: string, przedrostki): boolean
	for _, pre in przedrostki do
		if string.sub(n, 1, #pre) == pre then
			return true
		end
	end
	return false
end

function L.czystyProfil(D, p)
	local k, powod = L.zapisywalne(D, p, D.zapis.limity)
	if k == nil then
		return nil, powod
	end
	local G = D.limity
	if k.wersja ~= D.wersja_profilu then
		return nil, "zla_wersja"
	end
	local znanaKlasa = false
	for _, kl in D.klasy do
		if kl == k.klasa then
			znanaKlasa = true
		end
	end
	if not znanaKlasa then
		return nil, "zla_klasa"
	end
	if k.idKlasy ~= nil and (type(k.idKlasy) ~= "string" or D.klasy_gracza[k.idKlasy] == nil) then
		return nil, "zla_klasa"
	end
	-- 27.11.2026: rasa w zapisie (pole nieobowiązkowe)
	if k.idRasy ~= nil and (type(k.idRasy) ~= "string" or not table.find(D.rasy_gracza, k.idRasy)) then
		return nil, "zla_rasa"
	end
	if not calkowita(k.poziom, G.poziom_maks) or k.poziom < 1 then
		return nil, "zly_poziom"
	end
	if not liczba(k.xp) or k.xp < 0 then
		return nil, "zle_xp"
	end
	for _, pole in { "zloto", "gemy", "shardy", "awanse" } do
		if not calkowita(k[pole], G.waluta_maks) then
			return nil, "zle_" .. pole
		end
	end
	for _, pole in { "tokeny", "wydatki", "straznicy", "pakiety", "atrybuty" } do
		if type(k[pole]) ~= "table" then
			return nil, "zle_" .. pole
		end
	end
	for n, v in k.tokeny do
		if type(n) ~= "string" or not calkowita(v, G.waluta_maks) then
			return nil, "zle_tokeny"
		end
	end
	for n, v in k.wydatki do
		if type(n) ~= "string" or not calkowita(v, G.waluta_maks) then
			return nil, "zle_wydatki"
		end
	end
	for n, v in k.straznicy do
		if type(n) ~= "string" or v ~= true then
			return nil, "zle_straznicy"
		end
	end
	for n, v in k.atrybuty do
		if type(n) ~= "string" or not zaczynaSie(n, D.zapis.atrybuty_prefiksy) then
			return nil, "zle_atrybuty"
		end
		if not (type(v) == "boolean" or type(v) == "string" or liczba(v)) then
			return nil, "zle_atrybuty"
		end
	end
	if type(k.wytrenowane) ~= "table" then
		return nil, "zle_wytrenowane"
	end
	for _, s in D.statystyki do
		if not calkowita(k.wytrenowane[s], G.statystyka_maks) then
			return nil, "zle_wytrenowane"
		end
	end
	local w = k.walki
	if type(w) ~= "table" or not calkowita(w.wygrane, G.waluta_maks) or not calkowita(w.przegrane, G.waluta_maks) then
		return nil, "zle_walki"
	end
	local pt = k.punkty
	if type(pt) ~= "table" or not calkowita(pt.pula, G.waluta_maks) or not calkowita(pt.poziom, G.poziom_maks)
		or type(pt.rozdane) ~= "table" then
		return nil, "zle_punkty"
	end
	for _, s in D.statystyki do
		if not calkowita(pt.rozdane[s], G.statystyka_maks) then
			return nil, "zle_punkty"
		end
	end
	local pe = k.pety
	if type(pe) ~= "table" or type(pe.kopie) ~= "table" then
		return nil, "zle_pety"
	end
	for n, v in pe.kopie do
		if type(n) ~= "string" or not calkowita(v, D.pety.kopii_maks) then
			return nil, "zle_pety"
		end
	end
	if pe.aktywny ~= nil and type(pe.aktywny) ~= "string" then
		return nil, "zle_pety"
	end
	if L.czystaPremia(D, pe.premia) == nil then
		return nil, "zle_pety"
	end
	return k, "ok"
end

------------------------------------------------------------------ Gemy bez płacenia (18.11.2026, D-099)
function L.czyStraznik(D, gatunek): boolean
	local p = D.gemy.prefiks_straznika
	return type(gatunek) == "string" and string.sub(gatunek, 1, #p) == p
end

------------------------------------------------------------------ punkty statystyk do rozdania (18.11.2026, D-097)
function L.pulaSama(D, poziom, punktyWlaczone: boolean?): number
	local na = if punktyWlaczone == false then D.pula.na_poziom else D.punkty.auto_na_poziom
	return D.pula.baza + na * (L.poziomZ(D, poziom) - 1)
end

function L.zmianaStatystyki(D, znana, nowa, pula): (number, number, string)
	local z = L.statystykaZ(D, znana) or 0
	local p = if liczba(pula) and pula >= 0 then pula else 0
	local n = L.statystykaZ(D, nowa)
	if n == nil then
		return z, p, "cofnieta"
	end
	local d = n - z
	if d == 0 then
		return z, p, "ok"
	elseif d < 0 then
		return z, p, "cofnieta"
	elseif d > p then
		return z, p, "brak_punktow"
	end
	return n, p - d, "ok"
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
	for i, c in P.wydatek do
		local w, powod = L.czystyWydatek(D, c.info)
		sprawdz("wydatek", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.przychod do
		local w, powod = L.czystyPrzychod(D, c.info)
		sprawdz("przychod", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.sprzedaz or {} do
		local w, powod = L.czystaSprzedaz(D, c.info)
		sprawdz("sprzedaz", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.wydaj do
		local z, brak = L.wydaj(D, c.zloto, c.ile)
		sprawdz("wydaj", i, L.rowne({ z, brak }, c.wynik))
	end
	for i, c in P.premia do
		local premia = if c.premia == false then nil else c.premia
		local w, powod = L.czystaPremia(D, premia)
		sprawdz("premia", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.premia_lupu do
		sprawdz("premia_lupu", i, L.rowne(L.premiaLupu(D, c.lup, c.premia), c.wynik))
	end
	for i, c in P.mod do
		local w, powod = L.czystyModyfikator(D, c.mod)
		sprawdz("mod", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.zloz do
		sprawdz("zloz", i, L.rowne(L.zlozModyfikatory(D, c.mody), c.wynik))
	end
	for i, c in P.opis_mod do
		sprawdz("opis_mod", i, L.rowne(L.opisZModyfikatorami(D, c.opis, c.z), c.wynik))
	end
	for i, c in P.dane_pakietu do
		local w, powod = L.czysteDanePakietu(D, c.v)
		sprawdz("dane_pakietu", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.pula_sama do
		sprawdz("pula_sama", i, L.pulaSama(D, c.poziom, c.wl) == c.wynik)
	end
	for i, c in P.zmiana do
		local w, pula, wynik = L.zmianaStatystyki(D, c.znana, c.nowa, c.pula)
		sprawdz("zmiana", i, L.rowne({ w, pula, wynik }, c.wynik))
	end
	for i, c in P.migruj do
		local dane = if c.dane == false then nil else c.dane
		local w, powod = L.migrujProfil(D, dane)
		sprawdz("migruj", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.czysty_profil do
		local w, powod = L.czystyProfil(D, c.p)
		sprawdz("czysty_profil", i, L.rowne(falsz(w), c.wynik) and powod == c.powod)
	end
	for i, c in P.do_zapisu do
		sprawdz("do_zapisu", i, L.rowne(L.profilDoZapisu(D, c.p), c.wynik))
	end
	for i, c in P.straznik do
		sprawdz("straznik", i, L.czyStraznik(D, c.gatunek) == c.wynik)
	end
	for i, c in P.kara do
		local zloto = if c.zloto == false then nil else c.zloto
		local procent = if c.procent == false then nil else c.procent
		sprawdz("kara", i, L.karaPrzegranej(D, zloto, c.poziom, procent) == c.wynik)
	end
	return #bledy == 0, n, bledy
end

return L
