--[[
	LogikaPetArena — czyste rachunki gry Pet Arena (ModuleScript w Workspace/PetArenaGra/Moduly). Bez usług Roblox:
	wykonywane też w testach bez Studio (tools/walka/luau_mini.py, swiat/pet_arena/testy/test_pet_arena.py).

	Walka w 2D (x, z; środek areny w 0, 0) stałym krokiem: L.nowyStan(D, los) → S; L.dodajPeta(S, …); L.krok(S, dt) →
	lista zdarzeń; L.uzyj(S, pet) — umiejętność; L.zlotoTick(S) — złoto co sekundę. Losowość tylko przez S.los()
	(liczba 0–1), więc testy są powtarzalne. Liczby wyłącznie z D (DanePetArena, z ustawienia.json).

	Pet: { id, nr (indeks w D.pety), P (wpis D.pety), wl (właściciel: numer gracza > 0, dziki 0), dziki, x, z, kx, kz
	(prędkość odrzutu), hp, hpMax, faza ("lot" | "walka"), ladT, cd, osz, ogl, lod, skor, pal, palNaS, palOd, akcja,
	pasek (0–1), ostatni { wl, id, t, dziki }, wSrodku, pozaSrodka, zl (złoto na sekundę), kier }.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

local function clamp(x: number, a: number, b: number): number
	if x < a then
		return a
	elseif x > b then
		return b
	end
	return x
end
L.clamp = clamp

local function dlug(x: number, z: number): number
	return math.sqrt(x * x + z * z)
end
L.dlug = dlug

------------------------------------------------------------------ liczby
function L.format(n: number): string
	local przyrostki = { "K", "M", "B", "T", "Qa" }
	n = math.floor(n + 0.5)
	if n < 1000 then
		return tostring(math.floor(n))
	end
	local i = 0
	local v = n
	while v >= 1000 and i < #przyrostki do
		v = v / 1000
		i += 1
	end
	if v >= 100 then
		return tostring(math.floor(v)) .. przyrostki[i]
	end
	local d = math.floor(v * 10 + 1e-9) / 10
	if d == math.floor(d) then
		return tostring(math.floor(d)) .. przyrostki[i]
	end
	return string.format("%.1f", d) .. przyrostki[i]
end

-- „+5 G/s”: do jednego miejsca po kropce, bez zbędnego zera
function L.naSekunde(n: number): string
	if n == math.floor(n) then
		return L.format(n)
	end
	return string.format("%.1f", n)
end

------------------------------------------------------------------ strefy i odrzut
-- strefa dla odległości od środka: numer (1 środek … ostatnia), mnożnik; poza areną nil, 0
function L.strefa(D, r: number): (number?, number)
	for i, s in D.strefy do
		if r <= s.r then
			return i, s.mnoznik
		end
	end
	return nil, 0
end

-- prędkość odrzutu: siła × (1 + współczynnik × ubytek życia) / waga × mnożnik
function L.odrzut(D, sila: number, hp: number, hpMax: number, waga: number, mnoznik: number?): number
	local ubytek = 1 - clamp(hp / math.max(hpMax, 1), 0, 1)
	return sila * (1 + D.walka.wspolczynnik_odrzutu * ubytek) / waga * (mnoznik or 1)
end

-- droga odrzutu przy tarciu (suma kroków) — do tabel i testów
function L.drogaOdrzutu(D, v0: number, tarcie: number?): number
	local W = D.walka
	local f = math.max(0, 1 - (tarcie or W.tarcie) * W.krok_s)
	local s, v = 0, v0
	local n = 0
	while v > 0.05 and n < 2000 do
		s += v * W.krok_s
		v *= f
		n += 1
	end
	return s
end

function L.czasLotu(D, odleglosc: number): number
	return D.rzut.czas_s + D.rzut.na_stud * odleglosc
end

------------------------------------------------------------------ wiadro tempa (akcje gracza)
function L.wiadro(w, teraz: number, naS: number, zapas: number): boolean
	if w.t == nil then
		w.t = teraz
		w.z = zapas
	end
	w.z = math.min(zapas, w.z + (teraz - w.t) * naS)
	w.t = teraz
	if w.z >= 1 then
		w.z -= 1
		return true
	end
	return false
end

------------------------------------------------------------------ stan areny
function L.nowyStan(D, los)
	return { D = D, pety = {}, nastId = 1, czas = 0, krol = nil, nagroda = 0, los = los, bossUdzial = {} }
end

function L.petPoId(S, id: number)
	for _, p in S.pety do
		if p.id == id then
			return p
		end
	end
	return nil
end

function L.ilePetow(S): number
	return #S.pety
end

function L.ileDzikich(S): number
	local n = 0
	for _, p in S.pety do
		if p.dziki then
			n += 1
		end
	end
	return n
end

function L.petGracza(S, wl: number)
	for _, p in S.pety do
		if p.wl == wl and not p.dziki then
			return p
		end
	end
	return nil
end

-- czy wolno rzucić w (x, z): miejsce na arenie i limit petów (osobne sprawdzenia gracza robi serwer)
function L.mozeRzucic(S, x: any, z: any): (boolean, string?)
	local D = S.D
	if type(x) ~= "number" or type(z) ~= "number" or x ~= x or z ~= z then
		return false, "zle"
	end
	if dlug(x, z) > D.scena.arena_r - D.rzut.margines then
		return false, "poza"
	end
	if #S.pety >= D.rzut.limit_areny then
		return false, "pelna"
	end
	return true, nil
end

-- nowy pet w locie: z (x0, y0, z0) do (x, z) na arenie; ląduje po czasie lotu
function L.dodajPeta(S, nr: number, wl: number, dziki: boolean, x0: number, y0: number, z0: number, x: number, z: number, mn: any?)
	local D = S.D
	local P = D.pety[nr]
	local hpMax = P.zycie * (if dziki then D.boty.zycie_x else 1) * (if mn then mn.zycie else 1)
	local t = L.czasLotu(D, dlug(x - x0, z - z0))
	local p = {
		id = S.nastId, nr = nr, P = P, wl = wl, dziki = dziki, x = x, z = z, kx = 0, kz = 0, hp = hpMax, hpMax = hpMax,
		faza = "lot", ladT = S.czas + t, lotCzas = t, x0 = x0, y0 = y0, z0 = z0, cd = 0.4, osz = 0, ogl = 0, lod = 0,
		skor = 0, pal = 0, palNaS = 0, palOd = nil, akcja = nil, pasek = 0, ostatni = nil, wSrodku = 0, pozaSrodka = 99,
		zl = 0, kier = 0, pelnyOd = nil, mnSila = if mn then mn.sila else 1, gwiazdki = if mn then mn.gwiazdki else 1, y = 0, vy = 0,
	}
	S.nastId += 1
	table.insert(S.pety, p)
	return p
end

------------------------------------------------------------------ ciosy
local function wrog(a, b): boolean
	return a ~= b and b.faza == "walka" and not (b.akcja and b.akcja.typ == "skok") and (b.y or 0) <= 1
end

local function najblizszy(S, p, maks: number?)
	local best, bd = nil, math.huge
	for _, q in S.pety do
		if wrog(p, q) then
			local d = dlug(q.x - p.x, q.z - p.z)
			if d < bd and (maks == nil or d - p.P.promien - q.P.promien <= maks) then
				best, bd = q, d
			end
		end
	end
	return best, bd
end
L.najblizszy = najblizszy

-- obrót wektora o kąt (stopnie) — rozrzut ciosu
local function obroc(dx: number, dz: number, st: number): (number, number)
	local a = math.rad(st)
	local c, s = math.cos(a), math.sin(a)
	return dx * c - dz * s, dx * s + dz * c
end

-- cios a → b: obrażenia, odrzut w kierunku (dx, dz) (jednostkowy), zdarzenie; zwykly = zwykły cios (krytyk, pasek)
function L.cios(S, a, b, obrazenia: number, sila: number, dx: number, dz: number, zwykly: boolean, zdarzenia)
	local D = S.D
	local W = D.walka
	if b.akcja and b.akcja.typ == "skok" then
		return false
	end
	if b.skor > S.czas then
		-- skorupa: bez obrażeń i odrzutu; napastnik odbity
		if a and a.faza == "walka" and not (a.akcja and a.akcja.typ == "skok") then
			local v = L.odrzut(D, b.P.umiejetnosc.sila or 20, a.hp, a.hpMax, a.P.waga, 1)
			a.kx, a.kz = -dx * v, -dz * v
			a.osz = S.czas + math.min(W.oszolomienie_maks_s, v * W.oszolomienie_s_na_odrzut)
			a.ostatni = { wl = b.wl, id = b.id, t = S.czas, dziki = b.dziki }
		end
		table.insert(zdarzenia, { t = "odbicie", a = if a then a.id else 0, b = b.id, x = b.x, z = b.z })
		return false
	end
	if a then
		obrazenia *= (a.mnSila or 1)
		sila *= (a.mnSila or 1)
		if L.tarczaMiedzy(D, a, b) then
			obrazenia *= D.tarcza.mnoznik
			sila *= D.tarcza.mnoznik
		end
	end
	local kryt = false
	local mn = 1
	if zwykly and S.los() < W.krytyk_szansa then
		kryt = true
		obrazenia *= W.krytyk_obrazenia
		mn = W.krytyk_odrzut
	end
	if zwykly then
		dx, dz = obroc(dx, dz, (S.los() * 2 - 1) * W.rozrzut_st)
	end
	b.hp = math.max(0, b.hp - obrazenia)
	local v = L.odrzut(D, sila, b.hp, b.hpMax, b.P.waga, mn)
	b.kx, b.kz = dx * v, dz * v
	b.osz = S.czas + math.min(W.oszolomienie_maks_s, v * W.oszolomienie_s_na_odrzut)
	-- krytyk, cios kończący i mocny odrzut wyrzucają w powietrze (lot liczony w krok)
	local lot = false
	if not b.boss and (kryt or b.hp <= 0 or v >= W.wybicie_v) then
		b.vy = math.min(W.lot_vy_maks, v * W.lot_vy_x)
		b.y = math.max(b.y or 0, 0.05)
		lot = true
	end
	if a then
		b.ostatni = { wl = a.wl, id = a.id, t = S.czas, dziki = a.dziki }
		if zwykly then
			a.pasek = math.min(1, a.pasek + D.umiejetnosc.za_cios)
		end
	end
	b.pasek = math.min(1, b.pasek + D.umiejetnosc.za_trafienie)
	if a and a.wl > 0 and not a.dziki then
		if b.boss then
			S.bossUdzial[a.wl] = (S.bossUdzial[a.wl] or 0) + obrazenia
		end
		if b.zloty then
			table.insert(zdarzenia, { t = "zloto_cios", wl = a.wl, ile = D.zloty.za_cios * a.P.stopien, x = b.x, z = b.z })
		end
	end
	table.insert(zdarzenia, { t = "cios", a = if a then a.id else 0, b = b.id, o = math.floor(obrazenia + 0.5), k = kryt,
		x = b.x, z = b.z, v = v, lot = lot, dx = dx, dz = dz })
	return true
end

------------------------------------------------------------------ umiejętności
local function wKierunku(p, cel): (number, number)
	local dx, dz
	if cel then
		dx, dz = cel.x - p.x, cel.z - p.z
	else
		dx, dz = -p.x, -p.z
	end
	local d = dlug(dx, dz)
	if d < 1e-6 then
		return 1, 0
	end
	return dx / d, dz / d
end

local function wewnatrz(D, x: number, z: number, zapas: number): (number, number)
	local r = dlug(x, z)
	local m = D.scena.arena_r - zapas
	if r > m then
		return x / r * m, z / r * m
	end
	return x, z
end

-- fala odrzutu wokół (x, z): każdy wróg w r (promień + jego promień)
local function fala(S, p, x: number, z: number, r: number, sila: number, obrazenia: number, zdarzenia): number
	local n = 0
	for _, q in S.pety do
		if wrog(p, q) then
			local dx, dz = q.x - x, q.z - z
			local d = dlug(dx, dz)
			if d <= r + q.P.promien then
				if d < 1e-6 then
					dx, dz, d = 1, 0, 1
				end
				if L.cios(S, p, q, obrazenia, sila, dx / d, dz / d, false, zdarzenia) then
					n += 1
				end
			end
		end
	end
	return n
end

-- cel skoku: król (nie siebie) albo najbliższy; „tlum” — wróg z największą liczbą wrogów w r wokół
local function celSkoku(S, p, A)
	if A.cel == "krol" and S.krol and S.krol ~= p.id then
		local k = L.petPoId(S, S.krol)
		if k and wrog(p, k) then
			return k.x, k.z
		end
	end
	if A.cel == "tlum" then
		local best, bn = nil, -1
		for _, q in S.pety do
			if wrog(p, q) then
				local n = 0
				for _, w in S.pety do
					if wrog(p, w) and dlug(w.x - q.x, w.z - q.z) <= A.r then
						n += 1
					end
				end
				if n > bn then
					best, bn = q, n
				end
			end
		end
		if best then
			return best.x, best.z
		end
		return 0, 0
	end
	local q = najblizszy(S, p, nil)
	if q then
		return q.x, q.z
	end
	return 0, 0
end

function L.mozeUzyc(S, p): boolean
	return p ~= nil and p.faza == "walka" and p.pasek >= 1 and p.akcja == nil and p.ogl <= S.czas and p.lod <= S.czas
end

-- użycie umiejętności (gracz albo bot); zwraca true i dopisuje zdarzenie „umiejetnosc”
function L.uzyj(S, p, zdarzenia): boolean
	if not L.mozeUzyc(S, p) then
		return false
	end
	local D = S.D
	local A = p.P.umiejetnosc
	p.pasek = 0
	p.pelnyOd = nil
	local z = { t = "umiejetnosc", id = p.id, typ = A.typ, nazwa = A.nazwa, x = p.x, z = p.z }
	if A.typ == "fala" then
		z.r = A.r
		z.trafione = fala(S, p, p.x, p.z, A.r, A.sila, A.obrazenia, zdarzenia)
	elseif A.typ == "ogluszenie" then
		z.r = A.r
		local n = 0
		for _, q in S.pety do
			if wrog(p, q) and dlug(q.x - p.x, q.z - p.z) <= A.r + q.P.promien then
				q.ogl = S.czas + A.czas
				q.hp = math.max(0, q.hp - A.obrazenia)
				q.ostatni = { wl = p.wl, id = p.id, t = S.czas, dziki = p.dziki }
				n += 1
			end
		end
		z.trafione = n
	elseif A.typ == "zamrozenie" then
		local q = najblizszy(S, p, A.zasieg)
		if q then
			q.lod = S.czas + A.czas
			q.hp = math.max(0, q.hp - A.obrazenia)
			q.ostatni = { wl = p.wl, id = p.id, t = S.czas, dziki = p.dziki }
			z.cel = q.id
			z.trafione = 1
		else
			z.trafione = 0
		end
	elseif A.typ == "skorupa" then
		p.skor = S.czas + A.czas
		z.czas = A.czas
	elseif A.typ == "podpalenie" then
		local q = najblizszy(S, p, nil)
		local fx, fz = wKierunku(p, q)
		local rx, rz = L.kierunekGracza(S, p)
		if rx then
			fx, fz = rx, rz
		end
		local cosKat = math.cos(math.rad(A.kat_st / 2))
		local n = 0
		for _, w in S.pety do
			if wrog(p, w) then
				local dx, dz = w.x - p.x, w.z - p.z
				local d = dlug(dx, dz)
				if d <= A.zasieg + w.P.promien and (d < 1e-6 or (dx * fx + dz * fz) / d >= cosKat) then
					w.pal = S.czas + A.czas
					w.palNaS = A.na_s
					w.palOd = { wl = p.wl, id = p.id, t = S.czas, dziki = p.dziki }
					local ux, uz = if d < 1e-6 then fx else dx / d, if d < 1e-6 then fz else dz / d
					L.cios(S, p, w, 0, A.sila, ux, uz, false, zdarzenia)
					n += 1
				end
			end
		end
		z.kx, z.kz, z.zasieg, z.kat = fx, fz, A.zasieg, A.kat_st
		z.trafione = n
	elseif A.typ == "jezyk" then
		local q = najblizszy(S, p, A.zasieg)
		if q then
			local dx, dz = wKierunku(p, q)
			z.cel = q.id
			z.x1, z.z1 = q.x, q.z
			-- przyciąga i przerzuca za siebie
			local odl = p.P.promien + q.P.promien + 0.6
			q.x, q.z = wewnatrz(D, p.x - dx * odl, p.z - dz * odl, 0.2)
			L.cios(S, p, q, A.obrazenia, A.sila, -dx, -dz, false, zdarzenia)
			z.trafione = 1
		else
			z.trafione = 0
		end
	elseif A.typ == "rykoszet" then
		local cele = {}
		local bylo = {}
		local px, pz = p.x, p.z
		for _ = 1, A.celow do
			local best, bd = nil, math.huge
			for _, q in S.pety do
				if wrog(p, q) and not bylo[q.id] then
					local d = dlug(q.x - px, q.z - pz)
					if d < bd and d <= A.zasieg + q.P.promien then
						best, bd = q, d
					end
				end
			end
			if not best then
				break
			end
			bylo[best.id] = true
			table.insert(cele, best.id)
			px, pz = best.x, best.z
		end
		p.akcja = { typ = "rykoszet", cele = cele, i = 1, nast = S.czas, odX = p.x, odZ = p.z }
		z.cele = cele
		z.trafione = #cele
	elseif A.typ == "szarza" then
		local q = najblizszy(S, p, nil)
		local dx, dz = wKierunku(p, q)
		local rx, rz = L.kierunekGracza(S, p)
		if rx then
			dx, dz = rx, rz
		end
		p.akcja = { typ = "szarza", dx = dx, dz = dz, zostalo = A.dlugosc, trafieni = {} }
		z.kx, z.kz, z.dlugosc = dx, dz, A.dlugosc
	elseif A.typ == "skok" then
		local cx, cz = celSkoku(S, p, A)
		local rx, rz = L.kierunekGracza(S, p)
		if rx then
			cx, cz = p.x + rx * D.sterowanie.skok_dystans, p.z + rz * D.sterowanie.skok_dystans
		end
		cx, cz = wewnatrz(D, cx, cz, p.P.promien + 0.5)
		p.akcja = { typ = "skok", t0 = S.czas, czas = A.czas, odX = p.x, odZ = p.z, doX = cx, doZ = cz }
		z.x1, z.z1, z.czas, z.wysokosc, z.r = cx, cz, A.czas, A.wysokosc, A.r
	end
	table.insert(zdarzenia, z)
	return true
end

-- krok akcji umiejętności (szarża, skok, rykoszet); true = akcja trwa (pet nie chodzi i nie bije)
local function krokAkcji(S, p, dt: number, zdarzenia): boolean
	local a = p.akcja
	if not a then
		return false
	end
	local D = S.D
	local A = p.P.umiejetnosc
	if a.typ == "szarza" then
		local krok = math.min(a.zostalo, A.predkosc * dt)
		p.x += a.dx * krok
		p.z += a.dz * krok
		a.zostalo -= krok
		p.kx, p.kz = 0, 0
		local stop = a.zostalo <= 0
		if dlug(p.x, p.z) > D.scena.arena_r - p.P.promien then
			p.x, p.z = wewnatrz(D, p.x, p.z, p.P.promien)
			stop = true
		end
		for _, q in S.pety do
			if wrog(p, q) and not a.trafieni[q.id] and dlug(q.x - p.x, q.z - p.z) <= p.P.promien + q.P.promien + 0.3 then
				a.trafieni[q.id] = true
				-- odrzut do przodu i trochę w bok od linii szarży
				local bx, bz = q.x - p.x, q.z - p.z
				local bok = bx * -a.dz + bz * a.dx
				local sx = if bok >= 0 then 1 else -1
				local ux, uz = a.dx + -a.dz * sx * 0.45, a.dz + a.dx * sx * 0.45
				local u = dlug(ux, uz)
				L.cios(S, p, q, A.obrazenia, A.sila, ux / u, uz / u, false, zdarzenia)
				if not A.przebija then
					stop = true
					break
				end
			end
		end
		if stop then
			p.akcja = nil
			table.insert(zdarzenia, { t = "koniec_akcji", id = p.id, x = p.x, z = p.z })
		end
		return true
	elseif a.typ == "skok" then
		local f = (S.czas - a.t0) / a.czas
		if f >= 1 then
			p.x, p.z = a.doX, a.doZ
			p.akcja = nil
			p.kx, p.kz = 0, 0
			local n = fala(S, p, p.x, p.z, A.r, A.sila, A.obrazenia, zdarzenia)
			table.insert(zdarzenia, { t = "ladowanie_skoku", id = p.id, x = p.x, z = p.z, r = A.r, trafione = n })
			return true
		end
		p.x = a.odX + (a.doX - a.odX) * f
		p.z = a.odZ + (a.doZ - a.odZ) * f
		return true
	elseif a.typ == "rykoszet" then
		if S.czas >= a.nast then
			local id = a.cele[a.i]
			local q = if id then L.petPoId(S, id) else nil
			if q and wrog(p, q) then
				local dx, dz = q.x - p.x, q.z - p.z
				local d = dlug(dx, dz)
				if d < 1e-6 then
					dx, dz, d = 1, 0, 1
				end
				-- skok do celu (staje obok) i cios
				local odl = p.P.promien + q.P.promien + 0.2
				p.x, p.z = wewnatrz(D, q.x - dx / d * odl, q.z - dz / d * odl, p.P.promien)
				L.cios(S, p, q, A.obrazenia, A.sila, dx / d, dz / d, false, zdarzenia)
				table.insert(zdarzenia, { t = "odbicie_slime", id = p.id, x = p.x, z = p.z, cel = q.id })
			end
			a.i += 1
			a.nast = S.czas + 0.2
			if a.i > #a.cele then
				p.akcja = nil
				table.insert(zdarzenia, { t = "koniec_akcji", id = p.id, x = p.x, z = p.z })
			end
		end
		return true
	end
	p.akcja = nil
	return false
end

------------------------------------------------------------------ sterowanie petem przez gracza
-- wejście: wektor kierunku w świecie (x, z), długość ≤ 1; nil — oddaj autopilotowi
function L.steruj(S, p, x: any, z: any): boolean
	if p == nil then
		return false
	end
	if x == nil then
		p.ster, p.sterT = nil, -1e9
		return true
	end
	if type(x) ~= "number" or type(z) ~= "number" or x ~= x or z ~= z or math.abs(x) > 2 or math.abs(z) > 2 then
		return false
	end
	local d = dlug(x, z)
	if d > 1 then
		x, z = x / d, z / d
	end
	p.ster = { x = x, z = z }
	p.sterT = S.czas
	return true
end

-- czy gracz kieruje (dotknął sterowania w ciągu autopilot_s)
function L.reczny(S, p): boolean
	return p ~= nil and p.ster ~= nil and S.czas - (p.sterT or -1e9) <= S.D.sterowanie.autopilot_s
end

-- kierunek umiejętności w trybie ręcznym: ruch drążka albo patrzenie; nil — autopilot
function L.kierunekGracza(S, p): (number?, number?)
	if not L.reczny(S, p) then
		return nil, nil
	end
	local d = dlug(p.ster.x, p.ster.z)
	if d > S.D.sterowanie.martwa_strefa then
		return p.ster.x / d, p.ster.z / d
	end
	return math.sin(p.kier or 0), math.cos(p.kier or 0)
end

-- krok peta sterowanego: idzie w stronę drążka (sam nie wychodzi za krawędź), bije najbliższego w zasięgu
function L.krokReczny(S, p, dt: number, zd)
	local D = S.D
	local W = D.walka
	local P = p.P
	local q, d = najblizszy(S, p, nil)
	if q and d <= P.promien + q.P.promien + W.zasieg_ciosu * (P.rozmiar or 1) and p.cd <= 0 then
		local dx, dz = (q.x - p.x) / math.max(d, 1e-6), (q.z - p.z) / math.max(d, 1e-6)
		p.kier = math.atan2(dx, dz)
		L.cios(S, p, q, P.obrazenia, P.odrzut, dx, dz, true, zd)
		p.cd = P.przerwa
	end
	local m = dlug(p.ster.x, p.ster.z)
	if m > D.sterowanie.martwa_strefa then
		local krok = P.predkosc * math.min(1, m) * dt
		local nx, nz = p.x + p.ster.x / m * krok, p.z + p.ster.z / m * krok
		local nr = dlug(nx, nz)
		if not (nr > D.scena.arena_r - P.promien * 0.6 and nr > dlug(p.x, p.z)) then
			p.x, p.z = nx, nz
		end
		p.kier = math.atan2(p.ster.x, p.ster.z)
	end
end

-- pet na tronie (złotym szczycie): najbliżej środka spośród stojących na szczycie
function L.naTronie(S)
	local best, br = nil, S.D.strefy[1].r
	for _, p in S.pety do
		if p.faza == "walka" and not p.boss and (p.y or 0) <= 0.5 then
			local r = dlug(p.x, p.z)
			if r <= br then
				best, br = p, r
			end
		end
	end
	return best
end

------------------------------------------------------------------ zderzenia (przekazanie pędu jak kule)
-- a i b stykają się wzdłuż n (od a do b): gdy zbliżają się szybciej niż 2 st/s — odbicie sprężyste według mas
-- (współczynnik odbicie); ślizgający się po ciosie pet przekazuje pęd i zaliczenie wybicia temu, w którego uderzył
function L.zderzenie(S, a, b, nx: number, nz: number, zd)
	local W = S.D.walka
	local vrel = (b.kx - a.kx) * nx + (b.kz - a.kz) * nz
	if vrel >= -2 then
		return false
	end
	local ma = if a.skor > S.czas then 1e6 else a.P.waga
	local mb = if b.skor > S.czas then 1e6 else b.P.waga
	local j = -(1 + W.odbicie) * vrel / (1 / ma + 1 / mb)
	a.kx -= j / ma * nx
	a.kz -= j / ma * nz
	b.kx += j / mb * nx
	b.kz += j / mb * nz
	-- kto pchał (szybszy wzdłuż n) przekazuje drugiemu swojego ostatniego atakującego
	local pchal, pchniety = if a.kx * nx + a.kz * nz > -(b.kx * nx + b.kz * nz) then a else b, nil
	pchniety = if pchal == a then b else a
	local o = pchal.ostatni
	if o and S.czas - o.t <= W.ostatni_cios_s and o.id ~= pchniety.id then
		pchniety.ostatni = { wl = o.wl, id = o.id, t = S.czas, dziki = o.dziki }
	end
	pchniety.osz = math.max(pchniety.osz, S.czas + 0.25)
	if math.abs(j) > 6 then
		table.insert(zd, { t = "zderzenie", a = a.id, b = b.id, x = (a.x + b.x) / 2, z = (a.z + b.z) / 2, j = math.abs(j) })
	end
	return true
end

------------------------------------------------------------------ krok walki
local function wybicie(S, p, rodzaj: string, zdarzenia)
	local D = S.D
	local o = p.ostatni
	if o and S.czas - o.t > D.walka.ostatni_cios_s then
		o = nil
	end
	local byl_krol = S.krol == p.id
	local premia = 0
	local nagrody = nil
	if p.boss then
		nagrody = L.nagrodyBossa(D, S.bossUdzial)
		if p.zloty then
			for wl, ile in nagrody do
				nagrody[wl] = ile + D.zloty.premia
			end
		end
		S.bossUdzial = {}
	elseif o and o.wl and o.wl > 0 and not o.dziki and o.wl ~= p.wl then
		premia = if p.zloty then D.zloty.premia else (if p.dziki then D.zloto.premia_dzikiego else D.zloto.premia_wybicia) * p.P.stopien
	end
	local nagroda = 0
	if byl_krol then
		if o and o.wl and o.wl > 0 and not o.dziki and o.wl ~= p.wl then
			nagroda = math.floor(S.nagroda + 0.5)
		end
		S.krol = nil
		S.nagroda = 0
	end
	table.insert(zdarzenia, {
		t = rodzaj, id = p.id, nr = p.nr, wl = p.wl, dziki = p.dziki, x = p.x, z = p.z, kx = p.kx, kz = p.kz, y = p.y or 0, vy = p.vy or 0,
		przez = if o and not o.dziki then o.wl else 0, przezId = if o then o.id else 0, premia = premia, nagroda = nagroda,
		krol = byl_krol, boss = p.boss == true, zloty = p.zloty == true, nagrody = nagrody,
	})
end

function L.krok(S, dt: number)
	local D = S.D
	local W = D.walka
	local zd = {}
	S.czas += dt
	local t = S.czas
	-- lądowania
	for _, p in S.pety do
		if p.faza == "lot" and t >= p.ladT then
			p.faza = "walka"
			p.cd = 0.3
			for _, q in S.pety do
				if q ~= p and q.faza == "walka" and not (q.akcja and q.akcja.typ == "skok") then
					local dx, dz = q.x - p.x, q.z - p.z
					local d = dlug(dx, dz)
					local lr = if p.boss then D.boss.fala_r else W.ladowanie_r * (p.P.rozmiar or 1)
					if d <= lr + q.P.promien then
						if d < 1e-6 then
							dx, dz, d = 1, 0, 1
						end
						L.cios(S, p, q, 0, if p.boss then D.boss.fala_sila else W.ladowanie_sila, dx / d, dz / d, false, zd)
					end
				end
			end
			table.insert(zd, { t = "ladowanie", id = p.id, x = p.x, z = p.z })
		end
	end
	-- akcje, chodzenie i ciosy
	for _, p in S.pety do
		if p.faza == "walka" then
			p.cd -= dt
			local zajety = krokAkcji(S, p, dt, zd)
			if (p.y or 0) > 0 then
				zajety = true
			elseif p.boss or p.zloty then
				L.krokSpecjalny(S, p, dt, zd)
				zajety = true
			end
			if not zajety and p.akcja == nil and p.ogl <= t and p.lod <= t and p.osz <= t and L.reczny(S, p) then
				L.krokReczny(S, p, dt, zd)
			elseif not zajety and p.akcja == nil and p.ogl <= t and p.lod <= t and p.osz <= t then
				local P = p.P
				local q, d = najblizszy(S, p, nil)
				local cel = nil
				if q and d - P.promien - q.P.promien <= W.zasieg_widzenia then
					cel = q
				end
				if cel and d <= P.promien + cel.P.promien + W.zasieg_ciosu * (P.rozmiar or 1) then
					p.kier = math.atan2(cel.x - p.x, cel.z - p.z)
					if p.cd <= 0 then
						local dx, dz = (cel.x - p.x) / math.max(d, 1e-6), (cel.z - p.z) / math.max(d, 1e-6)
						L.cios(S, p, cel, P.obrazenia, P.odrzut, dx, dz, true, zd)
						p.cd = P.przerwa
					end
				else
					local tx, tz = 0, 0
					if cel then
						tx, tz = cel.x, cel.z
					end
					local dx, dz = tx - p.x, tz - p.z
					local dd = dlug(dx, dz)
					local stoi = (cel == nil and dd < 0.8)
					if not stoi and dd > 1e-6 then
						local krok = math.min(dd, P.predkosc * dt)
						local nx, nz = p.x + dx / dd * krok, p.z + dz / dd * krok
						-- sam nie wychodzi za krawędź, ale też nie jest do środka „przyciągany” (odrzut działa dalej)
						local nr = dlug(nx, nz)
						if not (nr > D.scena.arena_r - P.promien * 0.6 and nr > dlug(p.x, p.z)) then
							p.x, p.z = nx, nz
						end
						p.kier = math.atan2(dx, dz)
					end
				end
			end
		end
	end
	-- odrzut i tarcie
	for _, p in S.pety do
		if p.faza == "walka" and (p.y or 0) > 0 then
			-- lot: bez tarcia (lekki opór powietrza), grawitacja, odbicie przy lądowaniu
			p.x += p.kx * dt
			p.z += p.kz * dt
			local o = math.max(0, 1 - W.opor_powietrza * dt)
			p.kx *= o
			p.kz *= o
			p.vy -= W.grawitacja * dt
			p.y += p.vy * dt
			if p.y <= 0 then
				p.y = 0
				if p.vy < -18 then
					p.vy = -p.vy * 0.3
					p.y = 0.05
					p.kx *= 0.6
					p.kz *= 0.6
				else
					p.vy = 0
				end
				table.insert(zd, { t = "upadek", id = p.id, x = p.x, z = p.z })
			end
		elseif p.faza == "walka" and not (p.akcja and p.akcja.typ ~= "rykoszet") then
			if p.kx ~= 0 or p.kz ~= 0 then
				p.x += p.kx * dt
				p.z += p.kz * dt
				local tr = W.tarcie * (if p.lod > t then W.lod_tarcie else 1)
				local f = math.max(0, 1 - tr * dt)
				p.kx *= f
				p.kz *= f
				if dlug(p.kx, p.kz) < 0.05 then
					p.kx, p.kz = 0, 0
				end
			end
		end
	end
	-- rozpychanie (cięższy ustępuje mniej)
	local n = #S.pety
	for i = 1, n do
		local a = S.pety[i]
		for j = i + 1, n do
			local b = S.pety[j]
			if a.faza == "walka" and b.faza == "walka" and not (a.akcja and a.akcja.typ == "skok")
				and not (b.akcja and b.akcja.typ == "skok") and (a.y or 0) <= 0.5 and (b.y or 0) <= 0.5 then
				local dx, dz = b.x - a.x, b.z - a.z
				local d = dlug(dx, dz)
				local m = a.P.promien + b.P.promien
				if d < m then
					if d < 1e-6 then
						dx, dz, d = 1, 0, 1
					end
					local nak = m - d
					local wa, wb = a.P.waga, b.P.waga
					local ua = if a.skor > t then 0 else wb / (wa + wb)
					local ub = if b.skor > t then 0 else wa / (wa + wb)
					if ua + ub > 0 then
						local s = 1 / (ua + ub)
						a.x -= dx / d * nak * ua * s
						a.z -= dz / d * nak * ua * s
						b.x += dx / d * nak * ub * s
						b.z += dz / d * nak * ub * s
					end
					L.zderzenie(S, a, b, dx / d, dz / d, zd)
				end
			end
		end
	end
	-- podpalenie, pasek, wybicia
	local zostaja = {}
	for _, p in S.pety do
		local out = false
		if p.faza == "walka" then
			if p.pal > t then
				p.hp = math.max(0, p.hp - p.palNaS * dt)
				if p.palOd then
					p.ostatni = { wl = p.palOd.wl, id = p.palOd.id, t = t, dziki = p.palOd.dziki }
				end
			end
			if p.pasek < 1 then
				p.pasek = math.min(1, p.pasek + D.umiejetnosc.na_s * dt)
			end
			if p.pasek >= 1 and p.pelnyOd == nil then
				p.pelnyOd = t
			end
			if (p.boss or p.zloty) and p.koniecT and t >= p.koniecT then
				table.insert(zd, { t = if p.boss then "boss_uciekl" else "zloty_uciekl", id = p.id, x = p.x, z = p.z })
				if p.boss then
					S.bossUdzial = {}
				end
				out = true
			elseif not (p.akcja and p.akcja.typ == "skok") and dlug(p.x, p.z) > D.scena.arena_r then
				wybicie(S, p, "ringout", zd)
				out = true
			elseif p.hp <= 0 then
				wybicie(S, p, "ko", zd)
				out = true
			end
		end
		if not out then
			table.insert(zostaja, p)
		end
	end
	S.pety = zostaja
	-- król środka i nagroda za głowę
	local N = D.nagroda
	local rS = D.strefy[1].r
	for _, p in S.pety do
		if p.faza == "walka" and not p.boss and not p.zloty and not (p.akcja and p.akcja.typ == "skok") and dlug(p.x, p.z) <= rS then
			p.wSrodku += dt
			p.pozaSrodka = 0
		else
			p.pozaSrodka += dt
			if p.pozaSrodka > N.zgubiona_po_s then
				p.wSrodku = 0
			end
		end
	end
	if S.krol then
		local k = L.petPoId(S, S.krol)
		if not k or k.pozaSrodka > N.zgubiona_po_s then
			table.insert(zd, { t = "krol_stracil", id = S.krol })
			S.krol = nil
			S.nagroda = 0
		else
			S.nagroda += N.na_s * dt
		end
	end
	if not S.krol then
		local best, bw = nil, N.korona_po_s
		for _, p in S.pety do
			if p.pozaSrodka == 0 and p.wSrodku >= bw then
				best, bw = p, p.wSrodku
			end
		end
		if best then
			S.krol = best.id
			S.nagroda = N.start
			table.insert(zd, { t = "krol", id = best.id, wl = best.wl, dziki = best.dziki })
		end
	end
	return zd
end

------------------------------------------------------------------ złoto co sekundę
function L.zlotoPeta(D, p): number
	if p.dziki or p.faza ~= "walka" then
		return 0
	end
	local _, m = L.strefa(D, dlug(p.x, p.z))
	return D.zloto.baza * m * p.P.stopien
end

-- { [wl] = złoto }; ustawia p.zl (do napisu „+G/s”)
function L.zlotoTick(S)
	local w = {}
	local tron = L.naTronie(S)
	for _, p in S.pety do
		p.zl = L.zlotoPeta(S.D, p)
		if p.zl > 0 and p ~= tron and dlug(p.x, p.z) <= S.D.strefy[1].r then
			-- na szczycie mieści się jeden: pozostali liczą się jak drugi stopień
			p.zl = S.D.zloto.baza * S.D.strefy[2].mnoznik * p.P.stopien
		end
		if p.zl > 0 then
			w[p.wl] = (w[p.wl] or 0) + p.zl
		end
	end
	return w
end

------------------------------------------------------------------ dzikie pety (boty)
function L.losujStopien(D, r: number): number
	local suma = 0
	for _, w in D.boty.wagi_stopni do
		suma += w
	end
	local x = r * suma
	for i, w in D.boty.wagi_stopni do
		x -= w
		if x < 0 then
			return i
		end
	end
	return #D.boty.wagi_stopni
end

-- numer peta danego stopnia (r1 — los stopnia, r2 — los peta w stopniu)
function L.losujPetaBota(D, r1: number, r2: number): number
	local s = L.losujStopien(D, r1)
	while s >= 1 do
		local lista = {}
		for i, P in D.pety do
			if P.stopien == s then
				table.insert(lista, i)
			end
		end
		if #lista > 0 then
			return lista[math.min(#lista, math.floor(r2 * #lista) + 1)]
		end
		s -= 1
	end
	return 1
end

function L.ileBotowBrakuje(S): number
	local B = S.D.boty
	local brak = (S.botyDo or B.do_ilu) - #S.pety
	local wolne = (S.botyMaks or B.maks) - L.ileDzikich(S)
	return math.max(0, math.min(brak, wolne, S.D.rzut.limit_areny - #S.pety))
end

-- czy bot użyje umiejętności teraz: pełny pasek i wróg w zasięgu umiejętności albo czekał dość
function L.botChce(S, p, czekaj: number): boolean
	if not L.mozeUzyc(S, p) then
		return false
	end
	local A = p.P.umiejetnosc
	local zasieg = A.r or A.zasieg or 6
	if A.typ == "szarza" then
		zasieg = A.dlugosc * 0.6
	elseif A.typ == "skok" then
		zasieg = 99
	elseif A.typ == "skorupa" then
		zasieg = 3
	end
	local q, d = najblizszy(S, p, nil)
	if q and d - p.P.promien - q.P.promien <= zasieg then
		return true
	end
	return p.pelnyOd ~= nil and S.czas - p.pelnyOd >= czekaj
end

------------------------------------------------------------------ tarcza słabszego, boss, złoty pet
-- tarcza: atakujący o co najmniej D.tarcza.roznica stopni silniejszy (bez bossa i złotego peta)
function L.tarczaMiedzy(D, a, b): boolean
	return a ~= nil and b ~= nil and not a.boss and not b.boss and not a.zloty and not b.zloty
		and a.P.stopien - b.P.stopien >= D.tarcza.roznica
end

-- czy pet ma teraz tarczę (na arenie jest ktoś o roznica stopni silniejszy) — ikona przy pecie
function L.chroniony(S, p): boolean
	for _, q in S.pety do
		if q ~= p and L.tarczaMiedzy(S.D, q, p) then
			return true
		end
	end
	return false
end

-- boss: wpis jak pet (P), ląduje w środku z nieba
function L.dodajBossa(S, nrModelu: number, graczy: number, zloty: boolean?)
	local D = S.D
	local B = D.boss
	local P = { id = "boss", nazwa = if zloty then D.zloty.nazwa else B.modele[nrModelu].nazwa, stopien = B.stopien, waga = B.waga,
		zycie = B.zycie + B.na_gracza * graczy, obrazenia = 0, odrzut = 0, predkosc = 2, przerwa = 99, promien = B.promien,
		wysokosc = B.wysokosc, rozmiar = 4, wzorzec = B.modele[nrModelu].wzorzec, umiejetnosc = { typ = "fala", nazwa = "STOMP",
			r = B.fala_r, sila = B.fala_sila, obrazenia = B.fala_obrazenia } }
	-- wejście bramą: lot po ziemi od bramy do środka
	local Bm = D.brama or { x = 0, z = 80 }
	local p = L.dodajPeta(S, 1, 0, true, Bm.x, 0, Bm.z, 0, 0, nil)
	p.P = P
	p.hp, p.hpMax = P.zycie, P.zycie
	p.boss = true
	p.zloty = zloty == true
	p.nrModelu = nrModelu
	p.ladT = S.czas + B.wejscie_s
	p.lotCzas = B.wejscie_s
	p.koniecT = S.czas + B.czas_s
	p.falaT = S.czas + B.wejscie_s + B.fala_co_s
	S.bossUdzial = {}
	return p
end

function L.dodajZlotego(S, x0: number, y0: number, z0: number, x: number, z: number)
	local D = S.D
	local Zl = D.zloty
	local p = L.dodajPeta(S, Zl.nr, 0, true, x0, y0, z0, x, z, nil)
	local P = table.clone(p.P)
	P.zycie, P.predkosc, P.waga, P.nazwa = Zl.zycie, Zl.predkosc, Zl.waga, Zl.nazwa
	p.P = P
	p.hp, p.hpMax = Zl.zycie, Zl.zycie
	p.zloty = true
	p.koniecT = S.czas + Zl.czas_s
	return p
end

-- ruch bossa (stoi w środku, co fala_co_s fala) i złotego peta (ucieka od najbliższego, trzyma się areny)
function L.krokSpecjalny(S, p, dt: number, zd)
	local D = S.D
	if p.boss then
		local r = dlug(p.x, p.z)
		if r > 0.5 and p.osz <= S.czas then
			local k = math.min(r, p.P.predkosc * dt)
			p.x -= p.x / r * k
			p.z -= p.z / r * k
		end
		if S.czas >= p.falaT then
			p.falaT = S.czas + D.boss.fala_co_s
			local n = fala(S, p, p.x, p.z, D.boss.fala_r, D.boss.fala_sila, D.boss.fala_obrazenia, zd)
			table.insert(zd, { t = "boss_fala", id = p.id, x = p.x, z = p.z, r = D.boss.fala_r, trafione = n })
		end
	elseif p.zloty and p.ogl <= S.czas and p.lod <= S.czas and p.osz <= S.czas then
		local q, d = najblizszy(S, p, nil)
		local dx, dz
		if q and d < 12 then
			dx, dz = p.x - q.x, p.z - q.z
		else
			p.cel = p.cel or { x = 0, z = 0 }
			if dlug(p.cel.x - p.x, p.cel.z - p.z) < 1.5 then
				local a = S.los() * math.pi * 2
				local r = S.los() * (D.scena.arena_r - 6)
				p.cel = { x = math.cos(a) * r, z = math.sin(a) * r }
			end
			dx, dz = p.cel.x - p.x, p.cel.z - p.z
		end
		local dd = dlug(dx, dz)
		if dd > 1e-6 then
			-- przy krawędzi skręca w bok (wzdłuż brzegu), żeby nie wypaść sam
			local r = dlug(p.x, p.z)
			if r > D.scena.arena_r - 5 and (dx * p.x + dz * p.z) > 0 then
				dx, dz = -p.z, p.x
				dd = dlug(dx, dz)
			end
			local k = p.P.predkosc * dt
			local nx, nz = wewnatrz(D, p.x + dx / dd * k, p.z + dz / dd * k, p.P.promien + 1)
			p.x, p.z = nx, nz
			p.kier = math.atan2(dx, dz)
		end
	end
end

-- nagrody za bossa: udział w obrażeniach × pula, co najmniej minimum — { [wl] = złoto }
function L.nagrodyBossa(D, udzial)
	local suma = 0
	for _, v in udzial do
		suma += v
	end
	local w = {}
	if suma <= 0 then
		return w
	end
	for wl, v in udzial do
		w[wl] = math.max(D.boss.minimum, math.floor(D.boss.pula * v / suma + 0.5))
	end
	return w
end

function L.typWydarzenia(D, nr: number): string
	local k = D.wydarzenia.kolejnosc
	return k[((nr - 1) % #k) + 1]
end

------------------------------------------------------------------ jajka, kolekcja, gwiazdki, trener
-- pet z jajka: r1 — rzadkość wg jawnych szans, r2 — pet w rzadkości (po równo); zwraca numer peta i rzadkość
function L.losujZJajka(D, nrJajka: number, r1: number, r2: number): (number, number)
	local J = D.jajka[nrJajka]
	local x = r1
	local rz = #J.szanse
	for i, s in J.szanse do
		x -= s
		if x < 0 then
			rz = i
			break
		end
	end
	while rz > 1 and J.szanse[rz] <= 0 do
		rz -= 1
	end
	local lista = {}
	for i, P in D.pety do
		if P.stopien == rz then
			table.insert(lista, i)
		end
	end
	return lista[math.min(#lista, math.floor(r2 * #lista) + 1)], rz
end

-- nowy pet albo kopia (gwiazdka, najwyżej maks; przy maks — zwrot złota): { nowy, gwiazdki, maks, zwrot }
function L.dodajDoKolekcji(D, profil, id: string, cenaJajka: number)
	local g = profil.pety[id]
	profil.ksiega[id] = true
	if g == nil then
		profil.pety[id] = 1
		if #profil.druzyna < D.gracz.druzyna_maks then
			table.insert(profil.druzyna, id)
		end
		return { nowy = true, gwiazdki = 1, maks = false, zwrot = 0 }
	end
	if g >= D.gwiazdki.maks then
		local zwrot = math.floor(cenaJajka * D.gwiazdki.zwrot_przy_maks + 0.5)
		profil.zloto += zwrot
		return { nowy = false, gwiazdki = g, maks = true, zwrot = zwrot }
	end
	profil.pety[id] = g + 1
	return { nowy = false, gwiazdki = g + 1, maks = false, zwrot = 0 }
end

-- doświadczenie potrzebne na przejście z poziomu n na n + 1
function L.potrzeba(D, n: number): number
	return math.floor(D.trener.baza * n ^ D.trener.wykladnik + 0.5)
end

-- poziom z doświadczenia: poziom, doświadczenie w poziomie, potrzeba na następny
function L.poziom(D, xp: number): (number, number, number)
	local n = 1
	local x = xp
	while n < D.trener.maks_poziom and x >= L.potrzeba(D, n) do
		x -= L.potrzeba(D, n)
		n += 1
	end
	return n, x, L.potrzeba(D, n)
end

-- mnożniki peta z gwiazdek i poziomu trenera
function L.mnoznikPeta(D, gwiazdki: number, poziom: number)
	local m = (1 + D.gwiazdki.na_gwiazdke * (gwiazdki - 1)) * (1 + D.trener.na_poziom * (poziom - 1))
	return { zycie = m, sila = m, gwiazdki = gwiazdki }
end

------------------------------------------------------------------ gracz: profil (wersja 2), drużyna, odpoczynek
function L.profilNowy(D)
	local pety, druzyna, ksiega = {}, {}, {}
	for _, id in D.gracz.pety_startowe do
		pety[id] = 1
		ksiega[id] = true
		table.insert(druzyna, id)
	end
	return { v = D.gracz.wersja_profilu, zloto = 0, pety = pety, druzyna = druzyna, ksiega = ksiega, xp = 0,
		samouczek = { rzut = false, jajko = false }, wybicia = 0, rzuty = 0, jajek = 0, krolS = 0,
		-- pod następny etap (jeszcze nieużywane w grze): odmiany złapanych petów { [id] = { [odmiana] = ile } } i jajka
		-- wylęgające się w czasie (także poza grą) { { nr = jajko, koniec = czas os.time() } }
		odmiany = {}, wylegarnia = {} }
end

local function liczba(v, domyslna: number, maks: number): number
	if type(v) ~= "number" or v ~= v or v < 0 or v > maks then
		return domyslna
	end
	return v
end

function L.nrPeta(D, id: string): number?
	for i, P in D.pety do
		if P.id == id then
			return i
		end
	end
	return nil
end

-- rekord z magazynu → profil wersji 2 (zła wartość = domyślna, nieznane pety pominięte). Wersja 1 (etap 1:
-- pety = lista id, bez gwiazdek) → każdy pet z 1 gwiazdką.
function L.profil(D, rekord)
	local p = L.profilNowy(D)
	if type(rekord) ~= "table" then
		return p
	end
	p.zloto = liczba(rekord.zloto, 0, 1e15)
	p.xp = liczba(rekord.xp, 0, 1e12)
	p.wybicia = liczba(rekord.wybicia, 0, 1e9)
	p.rzuty = liczba(rekord.rzuty, 0, 1e9)
	p.jajek = liczba(rekord.jajek, 0, 1e9)
	p.krolS = liczba(rekord.krolS, 0, 1e9)
	if type(rekord.pety) == "table" then
		local pety = {}
		for k, v in rekord.pety do
			local id = if type(k) == "string" then k elseif type(v) == "string" then v else nil
			local g = if type(k) == "string" and type(v) == "number" then math.clamp(math.floor(v), 1, D.gwiazdki.maks) else 1
			if id and L.nrPeta(D, id) then
				pety[id] = g
			end
		end
		if next(pety) ~= nil then
			p.pety = pety
		end
	end
	for id in p.pety do
		p.ksiega[id] = true
	end
	if type(rekord.ksiega) == "table" then
		for id, v in rekord.ksiega do
			if type(id) == "string" and v == true and L.nrPeta(D, id) then
				p.ksiega[id] = true
			end
		end
	end
	if type(rekord.druzyna) == "table" then
		local dr, bylo = {}, {}
		for _, id in rekord.druzyna do
			if type(id) == "string" and p.pety[id] and not bylo[id] and #dr < D.gracz.druzyna_maks then
				table.insert(dr, id)
				bylo[id] = true
			end
		end
		if #dr > 0 then
			p.druzyna = dr
		end
	end
	local zostaw = {}
	for _, id in p.druzyna do
		if p.pety[id] then
			table.insert(zostaw, id)
		end
	end
	if #zostaw == 0 then
		for id in p.pety do
			table.insert(zostaw, id)
			break
		end
	end
	p.druzyna = zostaw
	if type(rekord.samouczek) == "table" then
		p.samouczek = { rzut = rekord.samouczek.rzut == true, jajko = rekord.samouczek.jajko == true }
	end
	if type(rekord.odmiany) == "table" then
		for id, o in rekord.odmiany do
			if type(id) == "string" and L.nrPeta(D, id) and type(o) == "table" then
				local w = {}
				for nazwa, ile in o do
					if type(nazwa) == "string" and #nazwa <= 24 and type(ile) == "number" and ile >= 1 and ile <= 1e6 then
						w[nazwa] = math.floor(ile)
					end
				end
				if next(w) ~= nil then
					p.odmiany[id] = w
				end
			end
		end
	end
	if type(rekord.wylegarnia) == "table" then
		for _, j in rekord.wylegarnia do
			if type(j) == "table" and type(j.nr) == "number" and D.jajka[j.nr] and type(j.koniec) == "number"
				and j.koniec == j.koniec and #p.wylegarnia < 8 then
				table.insert(p.wylegarnia, { nr = j.nr, koniec = j.koniec })
			end
		end
	end
	return p
end

-- profil do magazynu (tylko proste typy, klucze napisowe)
function L.doZapisu(D, p)
	local pety, ksiega, dr = {}, {}, {}
	for id, g in p.pety do
		pety[id] = g
	end
	for id in p.ksiega do
		ksiega[id] = true
	end
	for _, id in p.druzyna do
		table.insert(dr, id)
	end
	return { v = D.gracz.wersja_profilu, zloto = p.zloto, pety = pety, druzyna = dr, ksiega = ksiega, xp = p.xp,
		samouczek = { rzut = p.samouczek.rzut, jajko = p.samouczek.jajko }, wybicia = p.wybicia, rzuty = p.rzuty, jajek = p.jajek,
		krolS = p.krolS, odmiany = table.clone(p.odmiany or {}), wylegarnia = table.clone(p.wylegarnia or {}) }
end

-- nowa drużyna z listy id: tylko posiadane, bez powtórzeń, 1..druzyna_maks
function L.ustawDruzyne(D, profil, lista): boolean
	if type(lista) ~= "table" then
		return false
	end
	local dr, bylo = {}, {}
	for _, id in lista do
		if type(id) ~= "string" or not profil.pety[id] or bylo[id] or #dr >= D.gracz.druzyna_maks then
			return false
		end
		bylo[id] = true
		table.insert(dr, id)
	end
	if #dr == 0 then
		return false
	end
	profil.druzyna = dr
	return true
end

-- drużyna do rzutu: { id, nr, gwiazdki, odpoczynek } (odpoczynek z mapy id → czas)
function L.druzyna(D, profil, odpoczynki)
	local w = {}
	for _, id in profil.druzyna do
		table.insert(w, { id = id, nr = L.nrPeta(D, id), gwiazdki = profil.pety[id] or 1, odpoczynek = (odpoczynki and odpoczynki[id]) or 0 })
	end
	return w
end

function L.gotowy(wpis, teraz: number): boolean
	return wpis ~= nil and (wpis.odpoczynek or 0) <= teraz
end

function L.odpocznij(D, wpis, teraz: number)
	wpis.odpoczynek = teraz + D.odpoczynek
end

-- pozostały odpoczynek w sekundach (zaokrąglony w górę)
function L.zostalo(wpis, teraz: number): number
	return math.max(0, math.ceil((wpis.odpoczynek or 0) - teraz))
end

------------------------------------------------------------------ zapis (magazyn podany z zewnątrz — w testach atrapa)
-- który magazyn: (nazwa albo nil, opis). Znacznik próby (tools/zapis_prob.py) → nil: prawdziwego zapisu nie ruszamy;
-- z ZapisProbaMagazyn = true → osobny magazyn próby
function L.magazyn(Z, studio: boolean, doKiedy, teraz: number, magazynProby: boolean)
	local wProbie = studio and type(doKiedy) == "number" and teraz < doKiedy
	local nazwa = Z.magazyn .. (if studio then Z.przyrostek_studio else "")
	if wProbie and magazynProby then
		return nazwa .. Z.przyrostek_proby, "włączony (magazyn próby)"
	elseif wProbie then
		return nil, "wyłączony (próba gry)"
	end
	return nazwa, "włączony"
end

-- wczytanie: (profil, zapisywalny). Bez magazynu albo po proby nieudanych próbach — nowy profil i zapis WYŁĄCZONY
-- (nie nadpiszemy prawdziwego postępu świeżym profilem). czekaj(n) — pauza między próbami (w teście nic).
function L.wczytajProfil(D, magazyn, klucz: string, czekaj)
	if not magazyn then
		return L.profilNowy(D), false
	end
	for proba = 1, D.zapis.proby do
		local ok, w = pcall(function()
			return magazyn:GetAsync(klucz)
		end)
		if ok then
			return L.profil(D, w), true
		end
		if czekaj then
			czekaj(proba)
		end
	end
	return L.profilNowy(D), false
end

-- zapis: true, gdy się udał; bez zapisywalnego profilu nic nie robi
function L.zapiszProfil(D, magazyn, klucz: string, profil, zapisywalny: boolean): boolean
	if not magazyn or not zapisywalny then
		return false
	end
	local dane = L.doZapisu(D, profil)
	local ok = pcall(function()
		magazyn:UpdateAsync(klucz, function()
			return dane
		end)
	end)
	return ok
end

------------------------------------------------------------------ tablice
-- najlepsze n wpisów { nazwa, w } malejąco po w (bez table.sort — działa też w testach)
function L.top(wpisy, n: number)
	local w = {}
	for _, x in wpisy do
		if x.w > 0 then
			local i = #w + 1
			while i > 1 and w[i - 1].w < x.w do
				w[i] = w[i - 1]
				i -= 1
			end
			w[i] = x
		end
	end
	local out = {}
	for i = 1, math.min(n, #w) do
		out[i] = w[i]
	end
	return out
end

return L