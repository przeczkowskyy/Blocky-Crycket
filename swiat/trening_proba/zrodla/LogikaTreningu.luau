--[[
	LogikaTreningu — czysta logika mini-gier Training Center (próba). ModuleScript Moduly/LogikaTreningu w kontenerze
	Workspace/TreningProba (budowa: swiat/trening_proba/zbuduj.py). Bez instancji Roblox: te same funkcje ma lustro
	w Pythonie (swiat/trening_proba/logika_treningu.py), a przypadki wzorcowe z lustra są w DaneTreningu.przypadki —
	SerwerTreningu sprawdza je przy starcie (atrybut ZgodnoscLogikiTreningu), test offline wykonuje ten plik
	interpreterem tools/walka/luau_mini.py.

	Tylko podzbiór biblioteki, który ma luau_mini: math.floor/abs/min/max, string.format, table.insert, type;
	iteracja `for k, v in t do`; bez typeof, ipairs, table.sort, math.random (własny generator Parka–Millera).

	Kto decyduje: SERWER. Klient liczy to samo na swojej kopii rundy tylko po to, żeby efekt trafienia był od razu;
	licznik serii i przyrost w HUD poprawia werdykt serwera.
		L.plan(D, gra, ziarno)                 → zdarzenia rundy { nr, t, poziom, okno, wartosc } (t od t0, s)
		L.nowaRunda(D, gra, id, t0, plan)      → stan rundy R
		L.zgloszenie(D, R, wartosc, tk, teraz) → werdykt naciśnięcia: kubełek żetonów (spam), okno czasu, kierunek
		L.przeterminowane(D, R, teraz)         → werdykty zdarzeń, których nikt nie odbił / zmyłek przeczekanych
		L.wejscie / L.start / L.wArenie / L.skalaUI / L.podsumowanie / L.przyrost
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local M = 2 ^ 31 - 1
L.NIGDY = -1e9

function L.ziarno(z)
	return math.floor(math.abs(z)) % (M - 1) + 1
end

-- ziarno rundy z czasu serwera i licznika rund (serwer); ten sam wynik daje lustro w Pythonie
function L.ziarnoZCzasu(t, licznik)
	return L.ziarno(t * 1000 + licznik)
end

function L.losuj(s)
	s = (48271 * s) % M
	return s, (s - 1) / (M - 1)
end

function L.zaokr(x)
	return math.floor(x * 1000 + 0.5) / 1000
end

function L.poziom(G, t)
	local n = #G.poziomy
	for i = n, 1, -1 do
		if t >= G.poziomy[i].od_s then
			return i
		end
	end
	return 1
end

function L.plan(D, gra, z)
	local G = D.gry[gra]
	local Rd = D.runda
	local s = L.ziarno(z)
	local t = Rd.pierwsze_s
	local koniec = Rd.dlugosc_s - Rd.koniec_zapas_s
	local lista = {}
	local nr = 0
	local u
	while t <= koniec do
		local i = L.poziom(G, t)
		local p = G.poziomy[i]
		nr += 1
		s, u = L.losuj(s)
		local e = { nr = nr, t = L.zaokr(t), poziom = i, okno = p.okno_s }
		if G.typ == "kierunki" then
			local k = 1 + math.floor(u * p.kierunki)
			if k > p.kierunki then
				k = p.kierunki
			end
			e.wartosc = G.kierunki[k]
		else
			e.wartosc = if u < p.zmylki then "zmylka" else "cios"
		end
		table.insert(lista, e)
		s, u = L.losuj(s)
		local odstep = p.odstep_s * (1 - G.rozrzut + 2 * G.rozrzut * u)
		t = t + odstep
	end
	return lista
end

-- jednostki paska za jedno trafienie przy tej serii (mnożnik serii × poziom centrum)
function L.przyrost(D, seria)
	local P = D.przyrost
	local k = 1
	for i = 1, #P.progi_serii do
		if seria >= P.progi_serii[i] then
			k = i + 1
		end
	end
	return P.za_trafienie[k] * P.mnoznik_centrum
end

-- pula punktów statystyk z poziomu gracza (do malejącego zysku)
function L.pula(D, poziom)
	local P = D.przyrost
	local lv = if type(poziom) == "number" and poziom >= 1 then math.floor(poziom) else 1
	return P.pula_baza + P.pula_na_poziom * (lv - 1)
end

-- ile jednostek paska trzeba na +1 punkt statystyki, gdy w tej statystyce wytrenowano już W punktów
function L.prog(D, W, pula)
	local P = D.przyrost
	if not P.malejacy_zysk then
		return P.prog_paska
	end
	local q = 1 + W / (P.polowa_udzialu * pula)
	return P.prog_paska * q * q
end

-- kubełek żetonów: pojemność poj, uzupełnianie uzup na sekundę; false = zgłoszenie odrzucone jako spam
function L.kubelek(K, teraz, poj, uzup)
	K.tokeny = math.min(poj, K.tokeny + math.max(0, teraz - K.ostatnio) * uzup)
	K.ostatnio = math.max(K.ostatnio, teraz)
	if K.tokeny < 1 then
		return false
	end
	K.tokeny = K.tokeny - 1
	return true
end

function L.nowyKubelek(poj, teraz)
	return { tokeny = poj, ostatnio = teraz }
end

-- S0 = { pasek, W, pula } — stan paska statystyki gracza na starcie rundy (serwer); bez niego pasek od zera, poziom 1
function L.nowaRunda(D, gra, id, t0, plan, S0)
	local O = D.ochrona
	local s0 = S0 or {}
	return {
		id = id, gra = gra, t0 = t0, plan = plan, rozstrzygniete = {}, nastepny = 1,
		seria = 0, najdluzsza = 0, trafienia = 0, pudla = 0, puste = 0, spam = 0, odrzucone = 0,
		suma = 0, jednostki = 0, pasek = s0.pasek or 0, W = s0.W or 0, pula = s0.pula or L.pula(D, 1),
		tokeny = O.pojemnosc, ostatnio = t0, koniec = false,
	}
end

function L.jestAkcja(G, wartosc)
	if type(wartosc) ~= "string" then
		return false
	end
	for _, a in G.akcje do
		if a == wartosc then
			return true
		end
	end
	return false
end

local function przesun(R)
	local n = #R.plan
	while R.nastepny <= n and R.rozstrzygniete[R.plan[R.nastepny].nr] ~= nil do
		R.nastepny += 1
	end
end

local function najblizsze(R, r, zasieg)
	local najlepsze, odl = nil, nil
	for i = R.nastepny, #R.plan do
		local e = R.plan[i]
		if e.t - r > zasieg then
			break
		end
		if R.rozstrzygniete[e.nr] == nil then
			local dd = math.abs(r - e.t)
			if dd <= zasieg and (odl == nil or dd < odl) then
				najlepsze, odl = e, dd
			end
		end
	end
	return najlepsze
end

-- drugie naciśnięcie tuż po rozstrzygniętym zdarzeniu (np. podwójne kliknięcie) — pomijane, bez kary
local function dubel(R, r, zasieg)
	for _, e in R.plan do
		if e.t - r > zasieg then
			break
		end
		if R.rozstrzygniete[e.nr] ~= nil and math.abs(r - e.t) <= zasieg then
			return true
		end
	end
	return false
end

local function rozstrzygnij(D, R, e, trafienie, powod, akcja, d)
	R.rozstrzygniete[e.nr] = if trafienie then "T" else "P"
	local p, j = 0, 0
	local prog = L.prog(D, R.W, R.pula)
	if trafienie then
		R.seria += 1
		if R.seria > R.najdluzsza then
			R.najdluzsza = R.seria
		end
		R.trafienia += 1
		j = L.przyrost(D, R.seria)
		R.jednostki += j
		R.pasek += j
		while R.pasek >= prog do
			R.pasek -= prog
			R.W += 1
			p += 1
			prog = L.prog(D, R.W, R.pula)
		end
		R.suma += p
	else
		R.seria = 0
		R.pudla += 1
	end
	przesun(R)
	return {
		przyjete = true, nr = e.nr, wartosc = e.wartosc, akcja = akcja, trafienie = trafienie, powod = powod,
		seria = R.seria, przyrost = p, jednostki = j, suma = R.suma, pasek = R.pasek, prog = prog,
		d = if d ~= nil then L.zaokr(d) else nil,
	}
end

function L.zgloszenie(D, R, wartosc, tk, teraz)
	local O = D.ochrona
	local G = D.gry[R.gra]
	if R.koniec then
		return { przyjete = false, powod = "koniec" }
	end
	if not L.kubelek(R, teraz, O.pojemnosc, O.uzupelnianie_na_s) then
		R.spam += 1
		return { przyjete = false, powod = "spam" }
	end
	if not L.jestAkcja(G, wartosc) then
		R.odrzucone += 1
		return { przyjete = false, powod = "zla_wartosc" }
	end
	local t = teraz
	if type(tk) == "number" and tk >= teraz - O.max_opoznienie_s and tk <= teraz + O.max_wyprzedzenie_s then
		t = tk
	end
	local r = t - R.t0
	local e = najblizsze(R, r, O.przypisanie_s)
	if e == nil and dubel(R, r, O.dubel_s) then
		return { przyjete = false, powod = "dubel" }
	end
	if e == nil then
		R.seria = 0
		R.puste += 1
		return {
			przyjete = true, nr = nil, wartosc = nil, akcja = wartosc, trafienie = false, powod = "pusty",
			seria = 0, przyrost = 0, jednostki = 0, suma = R.suma, pasek = R.pasek, prog = L.prog(D, R.W, R.pula), d = nil,
		}
	end
	local d = r - e.t
	local pasuje
	if G.typ == "kierunki" then
		pasuje = wartosc == e.wartosc
	else
		pasuje = e.wartosc == "cios"
	end
	if math.abs(d) <= e.okno and pasuje then
		return rozstrzygnij(D, R, e, true, "trafienie", wartosc, d)
	end
	local powod
	if G.typ == "blok" and e.wartosc == "zmylka" then
		powod = "zmylka"
	elseif d < -e.okno then
		powod = "za_wczesnie"
	elseif d > e.okno then
		powod = "za_pozno"
	else
		powod = "zly_kierunek"
	end
	return rozstrzygnij(D, R, e, false, powod, wartosc, d)
end

function L.przeterminowane(D, R, teraz)
	local O = D.ochrona
	local r = teraz - R.t0
	local lista = {}
	local n = #R.plan
	local i = R.nastepny
	while i <= n do
		local e = R.plan[i]
		if R.rozstrzygniete[e.nr] == nil then
			if r > e.t + e.okno + O.max_opoznienie_s then
				if e.wartosc == "zmylka" then
					table.insert(lista, rozstrzygnij(D, R, e, true, "przetrwana_zmylka", nil, nil))
				else
					table.insert(lista, rozstrzygnij(D, R, e, false, "przepuszczone", nil, nil))
				end
			else
				break
			end
		end
		i += 1
	end
	przesun(R)
	if not R.koniec and R.nastepny > n and r > D.runda.dlugosc_s + O.max_opoznienie_s then
		R.koniec = true
	end
	return lista
end

function L.podsumowanie(D, R)
	local proby = R.trafienia + R.pudla + R.puste
	return {
		gra = R.gra, n = #R.plan, trafienia = R.trafienia, pudla = R.pudla, puste = R.puste, spam = R.spam,
		najdluzsza = R.najdluzsza, suma = R.suma, jednostki = R.jednostki, pasek = R.pasek, W = R.W, pula = R.pula,
		prog = L.prog(D, R.W, R.pula), celnosc = math.floor(100 * R.trafienia / math.max(1, proby) + 0.5),
	}
end

function L.statystyka(D, id)
	for _, s in D.statystyki do
		if s.id == id then
			return s
		end
	end
	return nil
end

function L.nowyGracz()
	return { gra = nil, ostatnieWejscie = L.NIGDY, ostatniStart = L.NIGDY, runda = nil }
end

function L.wejscie(D, gra, S, teraz, odleglosc, wArenie)
	local O = D.ochrona
	if teraz - S.ostatnieWejscie < O.odstep_wejsc_s then
		return { ok = false, powod = "za_szybko" }
	end
	local st = if type(gra) == "string" then L.statystyka(D, gra) else nil
	if st == nil then
		return { ok = false, powod = "nieznana" }
	end
	if st.stan ~= "grywalna" or D.gry[gra] == nil then
		return { ok = false, powod = "w_projekcie" }
	end
	if S.runda ~= nil and not S.runda.koniec then
		return { ok = false, powod = "trwa_runda" }
	end
	if not wArenie and (odleglosc == nil or odleglosc > O.zasieg_wejscia) then
		return { ok = false, powod = "za_daleko" }
	end
	S.ostatnieWejscie = teraz
	return { ok = true, powod = "ok" }
end

function L.start(D, S, teraz)
	local O = D.ochrona
	if S.gra == nil then
		return { ok = false, powod = "brak_gry" }
	end
	if S.runda ~= nil and not S.runda.koniec then
		return { ok = false, powod = "trwa_runda" }
	end
	if teraz - S.ostatniStart < O.odstep_startu_s then
		return { ok = false, powod = "za_szybko" }
	end
	S.ostatniStart = teraz
	return { ok = true, powod = "ok" }
end

function L.wArenie(D, x, y, z)
	local A = D.arena
	local c = A.srodek
	if math.abs(x - c[1]) > A.rozmiar[1] / 2 + A.zapas_wArenie then
		return false
	end
	if math.abs(z - c[3]) > A.rozmiar[2] / 2 + A.zapas_wArenie then
		return false
	end
	local dy = y - c[2]
	return dy >= A.wysokosc_wArenie[1] and dy <= A.wysokosc_wArenie[2]
end

function L.skalaUI(D, w, h)
	local U = D.ui
	local s = math.min(w / U.baza[1], h / U.baza[2])
	if s < U.skala_min then
		s = U.skala_min
	end
	if s > U.skala_max then
		s = U.skala_max
	end
	return s
end

function L.kodWyniku(w, wygasly)
	if not w.przyjete then
		if w.powod == "spam" then
			return "S"
		elseif w.powod == "zla_wartosc" then
			return "X"
		elseif w.powod == "koniec" then
			return "K"
		elseif w.powod == "dubel" then
			return "D"
		end
		return "?"
	end
	if w.nr == nil then
		return "-"
	end
	local litera = if w.trafienie then "T" else "P"
	if wygasly then
		litera = if w.trafienie then "t" else "p"
	end
	return string.format("%s%d", litera, w.nr)
end

function L.wykonajKroki(D, gra, z, t0, kroki, S0)
	local R = L.nowaRunda(D, gra, 1, t0, L.plan(D, gra, z), S0)
	local kody = {}
	for _, k in kroki do
		if k.typ == "z" then
			table.insert(kody, L.kodWyniku(L.zgloszenie(D, R, k.w, k.tk, k.teraz), false))
		else
			for _, w in L.przeterminowane(D, R, k.teraz) do
				table.insert(kody, L.kodWyniku(w, true))
			end
		end
	end
	return table.concat(kody, ","), R
end

local function blisko(a, b)
	return type(a) == "number" and type(b) == "number" and math.abs(a - b) <= 1e-6
end

-- przypadki wzorcowe z lustra w Pythonie (DaneTreningu.przypadki) → ok, liczba, lista błędów
function L.sprawdzPrzypadki(D)
	local P = D.przypadki
	local bledy = {}
	local n = 0
	for _, c in P.plany do
		n += 1
		local pl = L.plan(D, c.gra, c.ziarno)
		local suma = 0
		for _, e in pl do
			suma += e.t
		end
		local ok = #pl == c.n and blisko(suma, c.suma_t)
		for j, p in c.pierwsze do
			local e = pl[j]
			if e == nil or not blisko(e.t, p[1]) or e.wartosc ~= p[2] then
				ok = false
			end
		end
		if not ok then
			table.insert(bledy, string.format("plan %s/%d", c.gra, c.ziarno))
		end
	end
	for _, c in P.sekwencje do
		n += 1
		local kod, R = L.wykonajKroki(D, c.gra, c.ziarno, c.t0, c.kroki, c.s0)
		local w = c.wynik
		if kod ~= w.kod or R.trafienia ~= w.trafienia or R.pudla ~= w.pudla or R.puste ~= w.puste
			or R.spam ~= w.spam or R.najdluzsza ~= w.najdluzsza or R.suma ~= w.suma or R.koniec ~= w.koniec
			or R.jednostki ~= w.jednostki or R.W ~= w.W or not blisko(R.pasek, w.pasek) then
			table.insert(bledy, string.format("sekwencja %s/%d", c.gra, c.ziarno))
		end
	end
	for _, c in P.przyrosty do
		n += 1
		if L.przyrost(D, c[1]) ~= c[2] then
			table.insert(bledy, string.format("przyrost %d", c[1]))
		end
	end
	for _, c in P.wejscia do
		n += 1
		local S = L.nowyGracz()
		S.ostatnieWejscie = c.ostatnie
		if c.runda then
			S.runda = { koniec = false }
		end
		local w = L.wejscie(D, c.gra, S, c.teraz, c.odl, c.wArenie)
		if w.ok ~= c.ok or w.powod ~= c.powod then
			table.insert(bledy, "wejscie " .. tostring(c.gra) .. " " .. c.powod)
		end
	end
	for _, c in P.skale do
		n += 1
		if not blisko(L.skalaUI(D, c[1], c[2]), c[3]) then
			table.insert(bledy, string.format("skala %d", c[1]))
		end
	end
	return #bledy == 0, n, bledy
end

return L
