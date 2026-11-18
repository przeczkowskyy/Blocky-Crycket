--[[
	LogikaTreningu — czysta logika mini-gier Training Center (próba). ModuleScript Moduly/LogikaTreningu w kontenerze
	Workspace/TreningProba (budowa: swiat/trening_proba/zbuduj.py). Bez instancji Roblox: te same funkcje ma lustro
	w Pythonie (swiat/trening_proba/logika_treningu.py), a przypadki wzorcowe z lustra są w DaneTreningu.przypadki —
	SerwerTreningu sprawdza je przy starcie (atrybut ZgodnoscLogikiTreningu), test offline wykonuje ten plik
	interpreterem tools/walka/luau_mini.py.

	Tylko podzbiór biblioteki, który ma luau_mini: math.floor/abs/min/max, string.format, table.insert/find, type;
	iteracja `for k, v in t do`; bez typeof, ipairs, table.sort, math.random (własny generator Parka–Millera).

	Kto decyduje: SERWER. Klient liczy to samo na swojej kopii rundy tylko po to, żeby efekt trafienia był od razu;
	licznik serii i przyrost w HUD poprawia werdykt serwera.
	Sześć rodzajów mini-gier (D.gry[gra].typ):
		kierunki  (Siła „Rozbijanie”)     — właściwy kierunek w oknie czasu wokół dolotu skrzynki
		blok      (Pancerz „Blok”)        — blok w oknie przy ciosie; zmyłkę trzeba przeczekać
		rytm      (Kondycja „Bieżnia”)    — lewa i prawa stopa na zmianę, równo z rytmem (bez rozrzutu, podbiegi)
		unik      (Zręczność „Kłody”)     — niska kłoda: skok, wysoka: padnij (G.odpowiedz: wartość → akcja)
		sekwencja (Inteligencja „Runy”)   — runy świecą po kolei, gracz powtarza; bez okna czasu na pojedynczą runę
		lapanie   (Szczęście „Koniczyny”) — koszyk na jednym z trzech torów; werdykt w chwili upadku
		L.plan(D, gra, ziarno)                 → zdarzenia rundy { nr, t, poziom, okno, wartosc, … } (sekwencja: runy)
		L.nowaRunda(D, gra, id, t0, plan)      → stan rundy R
		L.zgloszenie(D, R, wartosc, tk, teraz) → werdykt naciśnięcia: kubełek żetonów (spam), okno czasu, kierunek
		L.przeterminowane(D, R, teraz, zapas)  → werdykty zdarzeń, których nikt nie odbił / zmyłek przeczekanych /
		                                         upadków; w sekwencji ponowny pokaz po bezczynności
		L.wejscie / L.start / L.wArenie / L.skalaUI / L.podsumowanie / L.przyrost / L.torW / L.toryZdarzenia
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

-- akcja, która odbija zdarzenie o tej wartości (Kłody: nisko → skok); bez mapy — ta sama nazwa
function L.odpowiedz(G, wartosc)
	local o = G.odpowiedz
	if o ~= nil then
		return o[wartosc]
	end
	return wartosc
end

-- runy całej rundy (zapas na długie granie): bez tej samej runy dwa razy z rzędu (podwójnego mignięcia nie widać)
local function planSekwencji(G, s)
	local lista = {}
	local n = #G.runy
	local poprzednia = 0
	local u
	for nr = 1, G.baza do
		s, u = L.losuj(s)
		local k = 1 + math.floor(u * n)
		if k > n then
			k = n
		end
		if k == poprzednia then
			k = k % n + 1
		end
		poprzednia = k
		table.insert(lista, { nr = nr, wartosc = G.runy[k] })
	end
	return lista
end

function L.plan(D, gra, z)
	local G = D.gry[gra]
	local Rd = D.runda
	local s = L.ziarno(z)
	local typ = G.typ
	if typ == "sekwencja" then
		return planSekwencji(G, s)
	end
	local t = G.pierwsze_s or Rd.pierwsze_s
	local koniec = Rd.dlugosc_s - Rd.koniec_zapas_s
	local lista = {}
	local nr = 0
	local podbieg = 0
	local u
	while t <= koniec do
		local i = L.poziom(G, t)
		local p = G.poziomy[i]
		nr += 1
		s, u = L.losuj(s)
		local e = { nr = nr, t = L.zaokr(t), poziom = i, okno = p.okno_s or 0 }
		if typ == "kierunki" then
			local k = 1 + math.floor(u * p.kierunki)
			if k > p.kierunki then
				k = p.kierunki
			end
			e.wartosc = G.kierunki[k]
		elseif typ == "blok" then
			e.wartosc = if u < p.zmylki then "zmylka" else "cios"
		elseif typ == "rytm" then
			e.wartosc = if nr % 2 == 1 then G.kierunki[1] else G.kierunki[2]
			if podbieg > 0 then
				e.podbieg = true
				podbieg -= 1
			elseif u < p.podbiegi then
				e.podbieg = true
				podbieg = G.podbieg.kroki - 1
			end
		elseif typ == "unik" then
			local k = 1 + math.floor(u * p.wartosci)
			if k > p.wartosci then
				k = p.wartosci
			end
			e.wartosc = G.wartosci[k]
			s, u = L.losuj(s)
			if u < p.zmiany then
				e.zmiana = true
			end
		else -- lapanie
			if u < p.kamienie then
				e.wartosc = "kamien"
			else
				s, u = L.losuj(s)
				e.wartosc = if u < p.zlote then "zlota" else "koniczyna"
			end
			s, u = L.losuj(s)
			e.los = u
			s, u = L.losuj(s)
			if e.wartosc ~= "kamien" and u < p.wiatr then
				e.wiatr = if u < p.wiatr / 2 then -1 else 1
			end
		end
		table.insert(lista, e)
		s, u = L.losuj(s)
		local baza = p.odstep_s
		if typ == "rytm" and podbieg > 0 then
			baza = baza * G.podbieg.mnoznik
		end
		local odstep = baza * (1 - G.rozrzut + 2 * G.rozrzut * u)
		t = t + odstep
	end
	return lista
end

-- jednostki paska za jedno trafienie przy tej serii (mnożnik serii × poziom centrum × waga mini-gry G, gdy podana)
function L.przyrost(D, seria, G)
	local P = D.przyrost
	local k = 1
	for i = 1, #P.progi_serii do
		if seria >= P.progi_serii[i] then
			k = i + 1
		end
	end
	local j = P.za_trafienie[k] * P.mnoznik_centrum
	if G ~= nil and G.waga ~= nil then
		j = j * G.waga
	end
	return j
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

-- kubełek zgłoszeń w rundzie: własny mini-gry (Runy, Koniczyny: szybsze wpisywanie) albo wspólny z D.ochrona
local function kubelekGry(D, G)
	local k = G.kubelek
	if k ~= nil then
		return k.pojemnosc, k.uzupelnianie_na_s
	end
	return D.ochrona.pojemnosc, D.ochrona.uzupelnianie_na_s
end

-- tempo pokazu run z poziomu w chwili jego początku: R.swieci (s świecenia runy) i R.krok (świecenie + przerwa)
function L.tempoPokazu(D, R)
	local G = D.gry[R.gra]
	local p = G.poziomy[L.poziom(G, R.pokazOd)]
	R.swieci = p.pokaz_s
	R.krok = p.pokaz_s + p.przerwa_s
	return p
end

-- koniec pokazu run (od niego wolno wpisywać): dł × świecenie + (dł − 1) × przerwa, tempo z poziomu w chwili pokazu
local function koniecPokazu(D, R)
	local p = L.tempoPokazu(D, R)
	R.pokazDo = R.pokazOd + R.dl * p.pokaz_s + (R.dl - 1) * p.przerwa_s
	R.ostatnia = R.pokazDo
end

-- S0 = { pasek, W, pula } — stan paska statystyki gracza na starcie rundy (serwer); bez niego pasek od zera, poziom 1
function L.nowaRunda(D, gra, id, t0, plan, S0)
	local s0 = S0 or {}
	local G = D.gry[gra]
	local poj = kubelekGry(D, G)
	local R = {
		id = id, gra = gra, t0 = t0, plan = plan, rozstrzygniete = {}, nastepny = 1,
		seria = 0, najdluzsza = 0, trafienia = 0, pudla = 0, puste = 0, spam = 0, odrzucone = 0,
		suma = 0, jednostki = 0, pasek = s0.pasek or 0, W = s0.W or 0, pula = s0.pula or L.pula(D, 1),
		tokeny = poj, ostatnio = t0, koniec = false,
	}
	if G.typ == "sekwencja" then
		R.dl = G.start_dlugosc
		R.poz = 0
		R.offset = 0
		R.licznik = 0
		R.zaklecia = 0
		R.najdluzszaSekwencja = 0
		R.pokazy = 1
		R.ostatniaRuna = nil
		R.ostatniaRunaT = L.NIGDY
		R.pokazOd = G.pierwsze_s or D.runda.pierwsze_s
		koniecPokazu(D, R)
	elseif G.typ == "lapanie" then
		R.ruchy = {}
		R.tory = {}
		R.zlapane = 0
		R.kamienie = 0
	end
	return R
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

-- seria, jednostki paska i punkty statystyki za jedno rozstrzygnięcie → punkty, jednostki, próg po
local function ocen(D, R, trafienie, mnoznik)
	local G = D.gry[R.gra]
	local p, j = 0, 0
	local prog = L.prog(D, R.W, R.pula)
	if trafienie then
		R.seria += 1
		if R.seria > R.najdluzsza then
			R.najdluzsza = R.seria
		end
		R.trafienia += 1
		j = L.przyrost(D, R.seria, G) * mnoznik
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
	return p, j, prog
end

local function rozstrzygnij(D, R, e, trafienie, powod, akcja, d, mnoznik)
	R.rozstrzygniete[e.nr] = if trafienie then "T" else "P"
	local p, j, prog = ocen(D, R, trafienie, mnoznik or 1)
	przesun(R)
	return {
		przyjete = true, nr = e.nr, wartosc = e.wartosc, akcja = akcja, trafienie = trafienie, powod = powod,
		seria = R.seria, przyrost = p, jednostki = j, suma = R.suma, pasek = R.pasek, prog = prog,
		d = if d ~= nil then L.zaokr(d) else nil,
	}
end

------------------------------------------------------------------ sekwencja (Runy)
-- bezczynność w czasie wpisywania (bezczynnosc_s bez naciśnięcia) → ten sam pokaz jeszcze raz, od pierwszej runy, bez
-- kary; chwila nowego pokazu nie zależy od tego, kiedy to zauważono (serwer co tik, klient co klatkę)
function L.aktualizujSekwencje(D, R, r)
	local G = D.gry[R.gra]
	if R.koniec or r < R.pokazDo then
		return false
	end
	local od = R.ostatnia + G.bezczynnosc_s
	if r > od and od < D.runda.dlugosc_s then
		R.pokazOd = od
		R.poz = 0
		R.pokazy += 1
		koniecPokazu(D, R)
		return true
	end
	return false
end

local function zgloszenieSekwencji(D, R, wartosc, r)
	local G = D.gry[R.gra]
	local O = D.ochrona
	L.aktualizujSekwencje(D, R, r)
	if r < R.pokazDo then
		return { przyjete = false, powod = "pokaz" }
	end
	if wartosc == R.ostatniaRuna and r - R.ostatniaRunaT <= O.dubel_s then
		return { przyjete = false, powod = "dubel" }
	end
	local i = R.offset + R.poz + 1
	local oczekiwana = if i <= #R.plan then R.plan[i].wartosc else nil
	R.licznik += 1
	local nr = R.licznik
	R.ostatniaRuna = wartosc
	R.ostatniaRunaT = r
	local trafienie = wartosc == oczekiwana
	local p, j, prog = ocen(D, R, trafienie, 1)
	local zaklecie = false
	if trafienie then
		R.poz += 1
		if R.poz >= R.dl then
			zaklecie = true
			R.zaklecia += 1
			if R.dl > R.najdluzszaSekwencja then
				R.najdluzszaSekwencja = R.dl
			end
			if R.dl >= G.maks_dlugosc then
				R.offset += R.dl
				R.dl = G.start_dlugosc
			else
				R.dl += 1
			end
			R.poz = 0
			R.pokazOd = r + G.przerwa_s
			R.pokazy += 1
			koniecPokazu(D, R)
		else
			R.ostatnia = r
		end
	else
		R.dl = math.max(G.min_dlugosc, R.dl - G.kara)
		R.poz = 0
		R.pokazOd = r + G.przerwa_bledu_s
		R.pokazy += 1
		koniecPokazu(D, R)
	end
	return {
		przyjete = true, nr = nr, wartosc = oczekiwana, akcja = wartosc, trafienie = trafienie,
		powod = if trafienie then "trafienie" else "zla_runa", seria = R.seria, przyrost = p, jednostki = j,
		suma = R.suma, pasek = R.pasek, prog = prog, d = nil, zaklecie = zaklecie, dl = R.dl, poz = R.poz,
		offset = R.offset, pokazOd = R.pokazOd, pokazDo = R.pokazDo, pokazy = R.pokazy, ostatnia = R.ostatnia,
	}
end

------------------------------------------------------------------ łapanie (Koniczyny)
-- tor koszyka (1..3) w chwili T (s od t0): ostatni ruch o czasie ≤ T; przed pierwszym ruchem tor startowy
function L.torW(D, R, T)
	local G = D.gry[R.gra]
	local b = table.find(G.tory, G.start_tor)
	local najp = L.NIGDY
	for i = 1, #R.ruchy do
		local m = R.ruchy[i]
		if m.t <= T and m.t >= najp then
			b = m.tor
			najp = m.t
		end
	end
	return b
end

-- tor upadku i tor startu koniczyny albo kamienia — z toru koszyka w chwili, gdy zaczyna spadać (t − lot): kamień
-- celuje w koszyk, koniczyna spada na jeden z DWÓCH pozostałych torów (stanie w miejscu nic nie daje), a gdy się da —
-- nie na tor kamienia, który jeszcze leci; przy wietrze zaczyna o tor obok i dryfuje na swój; liczone raz i
-- zapamiętane (te same ruchy → ten sam wynik u klienta i na serwerze)
function L.toryZdarzenia(D, R, e)
	local G = D.gry[R.gra]
	local w = R.tory[e.nr]
	if w ~= nil then
		return w[1], w[2]
	end
	local start = e.t - G.lot_s
	local b = L.torW(D, R, start)
	local n = #G.tory
	local k
	if e.wartosc == "kamien" then
		k = b
	else
		local zajete = {}
		for j = 1, #R.plan do
			local e2 = R.plan[j]
			if e2.nr >= e.nr then
				break
			end
			if e2.wartosc == "kamien" and e2.t > start then
				local k2 = L.toryZdarzenia(D, R, e2)
				zajete[k2] = true
			end
		end
		local wolne = {}
		for i = 1, n do
			if i ~= b and not zajete[i] then
				table.insert(wolne, i)
			end
		end
		if #wolne == 0 then
			for i = 1, n do
				if i ~= b then
					table.insert(wolne, i)
				end
			end
		end
		local j = 1 + math.floor(e.los * #wolne)
		if j > #wolne then
			j = #wolne
		end
		k = wolne[j]
	end
	local z = k
	if e.wiatr ~= nil then
		z = k + e.wiatr
		if z < 1 or z > n then
			z = k - e.wiatr
		end
	end
	R.tory[e.nr] = { k, z }
	return k, z
end

local function zgloszenieLapania(D, R, wartosc, r)
	local G = D.gry[R.gra]
	local k = table.find(G.tory, wartosc)
	table.insert(R.ruchy, { t = r, tor = k })
	return {
		przyjete = true, nr = nil, wartosc = nil, akcja = wartosc, trafienie = false, powod = "ruch", ruch = true,
		tor = k, seria = R.seria, przyrost = 0, jednostki = 0, suma = R.suma, pasek = R.pasek,
		prog = L.prog(D, R.W, R.pula), d = nil,
	}
end

-- czy koszyk był na torze k przez cały odcinek (od, do] — bez ruchu na inny tor (ruch „na ten sam” nie psuje)
function L.stalNaTorze(D, R, k, od, koniec)
	if L.torW(D, R, od) ~= k then
		return false
	end
	for i = 1, #R.ruchy do
		local m = R.ruchy[i]
		if m.t > od and m.t <= koniec and m.tor ~= k then
			return false
		end
	end
	return true
end

local function upadek(D, R, e)
	local G = D.gry[R.gra]
	local k = L.toryZdarzenia(D, R, e)
	local b = L.torW(D, R, e.t)
	local w
	if e.wartosc == "kamien" then
		if b == k then
			R.kamienie += 1
			w = rozstrzygnij(D, R, e, false, "kamien", nil, nil, 1)
		else
			R.rozstrzygniete[e.nr] = "N" -- kamień obok koszyka — bez werdyktu, seria zostaje
			przesun(R)
			return nil
		end
	elseif L.stalNaTorze(D, R, k, e.t - G.zlapanie_s, e.t) then
		-- koszyk pod koniczyną już chwilę przed upadkiem (wsunięcie w ostatniej chwili się nie liczy — inaczej
		-- bezmyślne miotanie koszykiem łapałoby co trzecią koniczynę)
		R.zlapane += 1
		local zlota = e.wartosc == "zlota"
		w = rozstrzygnij(D, R, e, true, if zlota then "zlota" else "zlapana", nil, nil, if zlota then G.zlota_mnoznik else 1)
	else
		w = rozstrzygnij(D, R, e, false, if b == k then "za_pozno" else "spadla", nil, nil, 1)
	end
	w.tor = k
	return w
end

------------------------------------------------------------------ zgłoszenie i przeterminowane
function L.zgloszenie(D, R, wartosc, tk, teraz)
	local O = D.ochrona
	local G = D.gry[R.gra]
	if R.koniec then
		return { przyjete = false, powod = "koniec" }
	end
	local poj, uzup = kubelekGry(D, G)
	if not L.kubelek(R, teraz, poj, uzup) then
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
	if G.typ == "sekwencja" then
		return zgloszenieSekwencji(D, R, wartosc, r)
	elseif G.typ == "lapanie" then
		return zgloszenieLapania(D, R, wartosc, r)
	end
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
	if G.typ == "blok" then
		pasuje = e.wartosc == "cios"
	else
		pasuje = wartosc == L.odpowiedz(G, e.wartosc)
	end
	if math.abs(d) <= e.okno and pasuje then
		return rozstrzygnij(D, R, e, true, "trafienie", wartosc, d, 1)
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
	return rozstrzygnij(D, R, e, false, powod, wartosc, d, 1)
end

-- zapas = ile czekać po oknie na spóźnione wiadomości (domyślnie max_opoznienie_s; klient w Koniczynach: 0 — efekt
-- złapania w chwili upadku, serwer i tak rozstrzyga po zapasie)
function L.przeterminowane(D, R, teraz, zapas)
	local O = D.ochrona
	local G = D.gry[R.gra]
	local z = if zapas == nil then O.max_opoznienie_s else zapas
	local r = teraz - R.t0
	local lista = {}
	if G.typ == "sekwencja" then
		L.aktualizujSekwencje(D, R, r)
		if not R.koniec and r > D.runda.dlugosc_s + O.max_opoznienie_s then
			R.koniec = true
		end
		return lista
	end
	local n = #R.plan
	local i = R.nastepny
	while i <= n do
		local e = R.plan[i]
		if R.rozstrzygniete[e.nr] == nil then
			if r > e.t + e.okno + z then
				if G.typ == "lapanie" then
					local w = upadek(D, R, e)
					if w ~= nil then
						table.insert(lista, w)
					end
				elseif e.wartosc == "zmylka" then
					table.insert(lista, rozstrzygnij(D, R, e, true, "przetrwana_zmylka", nil, nil, 1))
				else
					table.insert(lista, rozstrzygnij(D, R, e, false, "przepuszczone", nil, nil, 1))
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
	local G = D.gry[R.gra]
	local n = #R.plan
	if G.typ == "sekwencja" then
		n = R.trafienia + R.pudla
	end
	local p = {
		gra = R.gra, n = n, trafienia = R.trafienia, pudla = R.pudla, puste = R.puste, spam = R.spam,
		najdluzsza = R.najdluzsza, suma = R.suma, jednostki = R.jednostki, pasek = R.pasek, W = R.W, pula = R.pula,
		prog = L.prog(D, R.W, R.pula), celnosc = math.floor(100 * R.trafienia / math.max(1, proby) + 0.5),
	}
	if G.typ == "sekwencja" then
		p.zaklecia = R.zaklecia
		p.najdluzszaSekwencja = R.najdluzszaSekwencja
	elseif G.typ == "lapanie" then
		p.zlapane = R.zlapane
		p.kamienie = R.kamienie
	end
	return p
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

-- prostokąty interfejsu rundy { x0, y0, x1, y1 } w pikselach obszaru GUI gw × gh przy skali s: zwarty panel rundy
-- i przycisk przerwania w prawym górnym rogu, przyciski gry przy krawędziach na dole (prawa kolumna HUD-u jest na
-- stanowisku schowana), kropki Run w lewym górnym rogu; ten sam układ sprawdza test telefonu (lustro: uklad_ui)
function L.ukladUI(D, gra, gw, gh, s)
	local U = D.ui
	local m = U.margines_px
	local g = U.odstep_px
	local R = {}
	local sw, sh = U.status_px[1] * s, U.status_px[2] * s
	R.status = { gw - m - sw, m, gw - m, m + sh }
	local b = U.przycisk_maly_px * s
	R.przerwij = { R.status[1] - g * s - b, m, R.status[1] - g * s, m + b }
	local function prawy(sz, wy)
		return { gw - m - sz * s, gh - m - wy * s, gw - m, gh - m }
	end
	local function lewy(sz, wy)
		return { m, gh - m - wy * s, m + sz * s, gh - m }
	end
	if gra == "sila" then
		local k = 3 * U.przycisk_px + 2 * g
		R.krzyz = prawy(k, k)
	elseif gra == "pancerz" then
		R.blok = prawy(U.blok_px, U.blok_px)
	elseif gra == "kondycja" then
		R.stopaL = lewy(U.stopa_px, U.stopa_px)
		R.stopaP = prawy(U.stopa_px, U.stopa_px)
	elseif gra == "zrecznosc" then
		R.unik = prawy(U.unik_px, 2 * U.unik_px + 2 * g)
	elseif gra == "inteligencja" then
		local k = 3 * U.runa_px + 2 * g
		R.runy = prawy(k, k)
		R.postep = { m, m, m + U.postep_px[1] * s, m + U.postep_px[2] * s }
	elseif gra == "szczescie" then
		R.torL = lewy(U.tor_px, U.tor_px)
		R.torP = prawy(U.tor_px, U.tor_px)
	end
	return R
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
		elseif w.powod == "pokaz" then
			return "W"
		end
		return "?"
	end
	if w.ruch then
		return "R"
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
			for _, w in L.przeterminowane(D, R, k.teraz, k.zapas) do
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
			suma += e.t or 0
		end
		local ok = #pl == c.n and blisko(suma, c.suma_t)
		for j, p in c.pierwsze do
			local e = pl[j]
			if e == nil or not blisko(e.t or 0, p[1]) or e.wartosc ~= p[2] then
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
			or not blisko(R.jednostki, w.jednostki) or R.W ~= w.W or not blisko(R.pasek, w.pasek) then
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
