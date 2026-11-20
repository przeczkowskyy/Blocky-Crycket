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
	return { D = D, pety = {}, nastId = 1, czas = 0, krol = nil, nagroda = 0, los = los }
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
function L.dodajPeta(S, nr: number, wl: number, dziki: boolean, x0: number, y0: number, z0: number, x: number, z: number)
	local D = S.D
	local P = D.pety[nr]
	local hpMax = P.zycie * (if dziki then D.boty.zycie_x else 1)
	local t = L.czasLotu(D, dlug(x - x0, z - z0))
	local p = {
		id = S.nastId, nr = nr, P = P, wl = wl, dziki = dziki, x = x, z = z, kx = 0, kz = 0, hp = hpMax, hpMax = hpMax,
		faza = "lot", ladT = S.czas + t, lotCzas = t, x0 = x0, y0 = y0, z0 = z0, cd = 0.4, osz = 0, ogl = 0, lod = 0,
		skor = 0, pal = 0, palNaS = 0, palOd = nil, akcja = nil, pasek = 0, ostatni = nil, wSrodku = 0, pozaSrodka = 99,
		zl = 0, kier = 0, pelnyOd = nil,
	}
	S.nastId += 1
	table.insert(S.pety, p)
	return p
end

------------------------------------------------------------------ ciosy
local function wrog(a, b): boolean
	return a ~= b and b.faza == "walka" and not (b.akcja and b.akcja.typ == "skok")
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
	if a then
		b.ostatni = { wl = a.wl, id = a.id, t = S.czas, dziki = a.dziki }
		if zwykly then
			a.pasek = math.min(1, a.pasek + D.umiejetnosc.za_cios)
		end
	end
	b.pasek = math.min(1, b.pasek + D.umiejetnosc.za_trafienie)
	table.insert(zdarzenia, { t = "cios", a = if a then a.id else 0, b = b.id, o = math.floor(obrazenia + 0.5), k = kryt,
		x = b.x, z = b.z, v = v })
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
		p.akcja = { typ = "szarza", dx = dx, dz = dz, zostalo = A.dlugosc, trafieni = {} }
		z.kx, z.kz, z.dlugosc = dx, dz, A.dlugosc
	elseif A.typ == "skok" then
		local cx, cz = celSkoku(S, p, A)
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

------------------------------------------------------------------ krok walki
local function wybicie(S, p, rodzaj: string, zdarzenia)
	local D = S.D
	local o = p.ostatni
	if o and S.czas - o.t > D.walka.ostatni_cios_s then
		o = nil
	end
	local byl_krol = S.krol == p.id
	local premia = 0
	if o and o.wl and o.wl > 0 and not o.dziki and o.wl ~= p.wl then
		premia = (if p.dziki then D.zloto.premia_dzikiego else D.zloto.premia_wybicia) * p.P.stopien
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
		t = rodzaj, id = p.id, nr = p.nr, wl = p.wl, dziki = p.dziki, x = p.x, z = p.z, kx = p.kx, kz = p.kz,
		przez = if o and not o.dziki then o.wl else 0, przezId = if o then o.id else 0, premia = premia, nagroda = nagroda,
		krol = byl_krol,
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
					if d <= W.ladowanie_r + q.P.promien then
						if d < 1e-6 then
							dx, dz, d = 1, 0, 1
						end
						L.cios(S, p, q, 0, W.ladowanie_sila, dx / d, dz / d, false, zd)
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
			if not zajety and p.akcja == nil and p.ogl <= t and p.lod <= t and p.osz <= t then
				local P = p.P
				local q, d = najblizszy(S, p, nil)
				local cel = nil
				if q and d - P.promien - q.P.promien <= W.zasieg_widzenia then
					cel = q
				end
				if cel and d <= P.promien + cel.P.promien + W.zasieg_ciosu then
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
						nx, nz = wewnatrz(D, nx, nz, P.promien * 0.6)
						p.x, p.z = nx, nz
						p.kier = math.atan2(dx, dz)
					end
				end
			end
		end
	end
	-- odrzut i tarcie
	for _, p in S.pety do
		if p.faza == "walka" and not (p.akcja and p.akcja.typ ~= "rykoszet") then
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
				and not (b.akcja and b.akcja.typ == "skok") then
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
			if not (p.akcja and p.akcja.typ == "skok") and dlug(p.x, p.z) > D.scena.arena_r then
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
		if p.faza == "walka" and not (p.akcja and p.akcja.typ == "skok") and dlug(p.x, p.z) <= rS then
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
	for _, p in S.pety do
		p.zl = L.zlotoPeta(S.D, p)
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

------------------------------------------------------------------ gracz: profil, drużyna, odpoczynek
function L.profilNowy(D)
	local pety = {}
	for _, id in D.gracz.pety_startowe do
		table.insert(pety, id)
	end
	return { v = D.gracz.wersja_profilu, zloto = 0, pety = pety, wybicia = 0, rzuty = 0 }
end

-- rekord z magazynu (etap 2) → profil; braki uzupełnione, nieznane pety pominięte
function L.profil(D, rekord)
	local p = L.profilNowy(D)
	if type(rekord) ~= "table" then
		return p
	end
	if type(rekord.zloto) == "number" and rekord.zloto >= 0 then
		p.zloto = rekord.zloto
	end
	if type(rekord.pety) == "table" then
		local znane = {}
		for _, P in D.pety do
			znane[P.id] = true
		end
		local lista = {}
		for _, id in rekord.pety do
			if znane[id] then
				table.insert(lista, id)
			end
		end
		if #lista > 0 then
			p.pety = lista
		end
	end
	if type(rekord.wybicia) == "number" then
		p.wybicia = rekord.wybicia
	end
	return p
end

function L.nrPeta(D, id: string): number?
	for i, P in D.pety do
		if P.id == id then
			return i
		end
	end
	return nil
end

-- drużyna: pierwsze pety profilu (do druzyna_maks); w etapie 1 trzeci to pet próbny (losowy od stopnia 2)
function L.druzyna(D, profil, r: number)
	local w = {}
	for _, id in profil.pety do
		if #w < D.gracz.druzyna_maks then
			table.insert(w, { id = id, nr = L.nrPeta(D, id), probny = false, odpoczynek = 0 })
		end
	end
	if D.gracz.pet_probny and #w < D.gracz.druzyna_maks then
		local lista = {}
		for i, P in D.pety do
			if P.stopien >= 2 then
				table.insert(lista, i)
			end
		end
		local nr = lista[math.min(#lista, math.floor(r * #lista) + 1)]
		table.insert(w, { id = D.pety[nr].id, nr = nr, probny = true, odpoczynek = 0 })
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

return L
