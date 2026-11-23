--[[
	LogikaZabawek — czyste rachunki obu zabawek (ModuleScript w Workspace/ZabawkiGra/Moduly; też w testach bez Studio).
	Zabawka 1 „EAT & EVOLVE”: byty (gracze i boty) w 2D, masa → promień i prędkość, zjadanie, odbicia, kulki, formy, APEX,
	proste boty. Zabawka 2 „LURE A MONSTER”: potwory w strefach łąki, rzut przynęty z procy, zwabienie albo pudło (płoszy),
	rzadki biegacz. Serwer woła krok1 / krok2 stałym krokiem; zdarzenia wracają listą.
]]
local L = {}

local function dlug(x: number, z: number): number
	return math.sqrt(x * x + z * z)
end
L.dlug = dlug

------------------------------------------------------------------ zabawka 1: EAT & EVOLVE
function L.promien(Z, m: number): number
	return Z.r0 * math.sqrt(m)
end

function L.predkosc(Z, m: number): number
	return Z.v0 / (1 + Z.kv * math.sqrt(m))
end

function L.forma(Z, m: number): number
	local f = 1
	for i, F in Z.formy do
		if m >= F.od then
			f = i
		end
	end
	return f
end

-- następny próg (do paska „do następnej formy”): 0–1
function L.postepFormy(Z, m: number): number
	local f = L.forma(Z, m)
	local nast = Z.formy[f + 1]
	if not nast then
		return 1
	end
	local od = Z.formy[f].od
	return math.clamp((m - od) / (nast.od - od), 0, 1)
end

function L.nowyStan1(D, los)
	local Z = D.zjadacz
	local kulki = {}
	for i = 1, #Z.kulkiPoz do
		kulki[i] = 0
	end
	return { D = D, Z = Z, los = los, czas = 0, byty = {}, nastId = 1, kulki = kulki, apex = 0 }
end

local function wolneMiejsce(S): (number, number)
	local Z = S.Z
	for _ = 1, 20 do
		local a = S.los() * 2 * math.pi
		local r = math.sqrt(S.los()) * (Z.pole_r - 12)
		local x, z = math.sin(a) * r, math.cos(a) * r
		local ok = true
		for _, s in Z.skalyPoz do
			if dlug(x - s.x, z - s.z) < s.r + 4 then
				ok = false
			end
		end
		for _, b in S.byty do
			if not b.martwyDo and dlug(x - b.x, z - b.z) < L.promien(Z, b.m) + 10 then
				ok = false
			end
		end
		if ok then
			return x, z
		end
	end
	return 0, 0
end
L.wolneMiejsce = wolneMiejsce

-- gracz startuje obok żywej kulki (pierwsze zjedzenie w pierwszych sekundach), z dala od większych
local function miejsceGracza(S): (number, number)
	local Z = S.Z
	for _ = 1, 30 do
		local i = 1 + math.floor(S.los() * #Z.kulkiPoz)
		local k = Z.kulkiPoz[i]
		if S.kulki[i] == 0 then
			local x, z = k[1] * 0.97, k[2] * 0.97 - 4
			local ok = true
			for _, b in S.byty do
				if not b.martwyDo and b.m > 1.2 and dlug(x - b.x, z - b.z) < L.promien(Z, b.m) + 16 then
					ok = false
				end
			end
			if ok then
				return x, z
			end
		end
	end
	return wolneMiejsce(S)
end

function L.dodajByt(S, slot: number, m: number, x: number?, z: number?)
	local px, pz = x, z
	if px == nil then
		if slot > 0 then
			px, pz = miejsceGracza(S)
		else
			px, pz = wolneMiejsce(S)
		end
	end
	local b = { id = S.nastId, slot = slot, m = m, x = px, z = pz, vx = 0, vz = 0, wx = 0, wz = 0, dashDo = 0, dashGotowy = 0,
		tarczaDo = S.czas + (if slot > 0 then S.Z.tarcza_s else 0), martwyDo = nil, myslDo = 0, forma = L.forma(S.Z, m), kier = 0,
		zjadl = 0 }
	S.nastId += 1
	table.insert(S.byty, b)
	return b
end

function L.bytPoId(S, id: number)
	for _, b in S.byty do
		if b.id == id then
			return b
		end
	end
	return nil
end

-- wejście gracza: kierunek długości ≤ 1 (nil — stój)
function L.steruj(b, x: any, z: any): boolean
	if x == nil then
		b.wx, b.wz = 0, 0
		return true
	end
	if type(x) ~= "number" or type(z) ~= "number" or x ~= x or z ~= z then
		return false
	end
	local d = dlug(x, z)
	if d > 1 then
		x, z = x / d, z / d
	end
	b.wx, b.wz = x, z
	return true
end

function L.dash(S, b): boolean
	if b.martwyDo or S.czas < b.dashGotowy then
		return false
	end
	b.dashDo = S.czas + S.Z.dash_s
	b.dashGotowy = S.czas + S.Z.dash_odnowa_s
	if b.wx == 0 and b.wz == 0 then
		b.wx, b.wz = math.sin(b.kier), math.cos(b.kier)
	end
	return true
end

-- bot: uciekaj przed większym, goń mniejszego, inaczej kulka albo spacer
function L.mysl(S, b)
	local Z = S.Z
	local r = L.promien(Z, b.m)
	local zagr, dz = nil, math.huge
	local ofiara, dof = nil, math.huge
	for _, q in S.byty do
		if q ~= b and not q.martwyDo then
			local d = dlug(q.x - b.x, q.z - b.z)
			local rq = L.promien(Z, q.m)
			if rq >= r * Z.przewaga and d < Z.bot_widzi + rq and d < dz then
				zagr, dz = q, d
			elseif r >= rq * Z.przewaga and d < Z.bot_widzi + r and d < dof and q.tarczaDo <= S.czas then
				ofiara, dof = q, d
			end
		end
	end
	if zagr then
		local d = math.max(0.1, dz)
		b.wx, b.wz = (b.x - zagr.x) / d, (b.z - zagr.z) / d
		if dz < L.promien(Z, zagr.m) + r + 4 and S.los() < 0.5 then
			L.dash(S, b)
		end
	elseif ofiara then
		local d = math.max(0.1, dof)
		b.wx, b.wz = (ofiara.x - b.x) / d, (ofiara.z - b.z) / d
		if dof < r + 8 and S.los() < 0.35 then
			L.dash(S, b)
		end
	else
		local best, bd = nil, 30
		for i, p in Z.kulkiPoz do
			if S.kulki[i] == 0 then
				local d = dlug(p[1] - b.x, p[2] - b.z)
				if d < bd then
					best, bd = p, d
				end
			end
		end
		if best then
			local d = math.max(0.1, bd)
			b.wx, b.wz = (best[1] - b.x) / d, (best[2] - b.z) / d
		elseif S.los() < 0.3 then
			local a = S.los() * 2 * math.pi
			b.wx, b.wz = math.sin(a) * 0.6, math.cos(a) * 0.6
		end
	end
	b.myslDo = S.czas + Z.bot_myslenie_s * (0.7 + S.los() * 0.6)
end

local function zgin(S, b, zd)
	local Z = S.Z
	b.martwyDo = S.czas + Z.odrodzenie_s
	b.vx, b.vz = 0, 0
	b.wx, b.wz = 0, 0
end

local function odrodz(S, b)
	local Z = S.Z
	if b.slot > 0 then
		-- gracz: forma niżej (część rozmiaru), krótka tarcza
		local f = math.max(1, L.forma(Z, b.m) - 1)
		b.m = math.max(1, Z.formy[f].od)
	else
		b.m = Z.boty_masy[1 + math.floor(S.los() * math.min(#Z.boty_masy, 8))]
	end
	if b.slot > 0 then
		b.x, b.z = miejsceGracza(S)
	else
		b.x, b.z = wolneMiejsce(S)
	end
	b.martwyDo = nil
	b.tarczaDo = S.czas + Z.tarcza_s
	b.forma = L.forma(Z, b.m)
end

-- krok zabawki 1: ruch, ściany i skały, zjadanie i odbicia, kulki, zanik, formy, odrodzenia, APEX → lista zdarzeń
function L.krok1(S, dt: number)
	local Z = S.Z
	S.czas += dt
	local zd = {}
	for _, b in S.byty do
		if b.martwyDo then
			if S.czas >= b.martwyDo then
				odrodz(S, b)
				table.insert(zd, { t = "odrodzenie", id = b.id, x = b.x, z = b.z })
			end
		else
			if b.slot == 0 and S.czas >= b.myslDo then
				L.mysl(S, b)
			end
			local v = L.predkosc(Z, b.m) * (if S.czas < b.dashDo then Z.dash_v else 1)
			local a = math.min(1, Z.przyspieszenie * dt * (if S.czas < b.dashDo then 3 else 1))
			b.vx += (b.wx * v - b.vx) * a
			b.vz += (b.wz * v - b.vz) * a
			b.x += b.vx * dt
			b.z += b.vz * dt
			if b.wx ~= 0 or b.wz ~= 0 then
				b.kier = math.atan2(b.wx, b.wz)
			end
			local r = L.promien(Z, b.m)
			local d = dlug(b.x, b.z)
			local maks = Z.pole_r - r * 0.6
			if d > maks then
				b.x, b.z = b.x / d * maks, b.z / d * maks
			end
			for _, s in Z.skalyPoz do
				local ds = dlug(b.x - s.x, b.z - s.z)
				local min = s.r + r * 0.7
				if ds < min and ds > 0.01 then
					b.x = s.x + (b.x - s.x) / ds * min
					b.z = s.z + (b.z - s.z) / ds * min
				end
			end
		end
	end
	-- zjadanie i odbicia
	local n = #S.byty
	for i = 1, n do
		local a = S.byty[i]
		for j = i + 1, n do
			local b = S.byty[j]
			if not a.martwyDo and not b.martwyDo then
				local ra, rb = L.promien(Z, a.m), L.promien(Z, b.m)
				local dx, dz = b.x - a.x, b.z - a.z
				local d = dlug(dx, dz)
				if d < ra + rb then
					local duzy, maly, rd, rm = a, b, ra, rb
					if rb > ra then
						duzy, maly, rd, rm = b, a, rb, ra
					end
					if rd >= rm * Z.przewaga and d < rd and maly.tarczaDo <= S.czas then
						duzy.m = duzy.m + maly.m * Z.przyrost
						if duzy.slot == 0 then
							duzy.m = math.min(duzy.m, Z.bot_masa_maks)
						end
						duzy.zjadl += 1
						table.insert(zd, { t = "zjedz", a = duzy.id, b = maly.id, x = maly.x, z = maly.z, m = maly.m, sa = duzy.slot, sb = maly.slot })
						zgin(S, maly, zd)
					elseif rd < rm * Z.przewaga then
						-- podobni: odbicie (rozsuń i odbij prędkości)
						local nx, nz = if d > 0.01 then dx / d else 1, if d > 0.01 then dz / d else 0
						local wnik = (ra + rb - d) * 0.5
						a.x -= nx * wnik
						a.z -= nz * wnik
						b.x += nx * wnik
						b.z += nz * wnik
						local va = a.vx * nx + a.vz * nz
						local vb = b.vx * nx + b.vz * nz
						local imp = math.max(0, va - vb) + 6
						a.vx -= nx * imp
						a.vz -= nz * imp
						b.vx += nx * imp
						b.vz += nz * imp
						if not a.odbicieDo or a.odbicieDo < S.czas then
							a.odbicieDo = S.czas + 0.3
							table.insert(zd, { t = "odbicie", a = a.id, b = b.id, x = (a.x + b.x) / 2, z = (a.z + b.z) / 2 })
						end
					end
				end
			end
		end
	end
	-- kulki
	for i, p in Z.kulkiPoz do
		if S.kulki[i] == 0 then
			for _, b in S.byty do
				if not b.martwyDo and dlug(p[1] - b.x, p[2] - b.z) < L.promien(Z, b.m) + Z.kulka_r then
					S.kulki[i] = S.czas + Z.kulka_powrot_s
					b.m += Z.kulka_masa
					table.insert(zd, { t = "kulka", i = i, id = b.id, s = b.slot })
					break
				end
			end
		elseif S.czas >= S.kulki[i] then
			S.kulki[i] = 0
		end
	end
	-- zanik dużych, formy, APEX
	local apex, am = 0, Z.apex_od
	for _, b in S.byty do
		if not b.martwyDo then
			if b.m > Z.zanik_od then
				b.m -= b.m * Z.zanik_na_s * dt
			end
			local f = L.forma(Z, b.m)
			if f > b.forma then
				table.insert(zd, { t = "ewolucja", id = b.id, forma = f, s = b.slot })
			end
			b.forma = f
			if b.m >= am then
				apex, am = b.id, b.m
			end
		end
	end
	if apex ~= S.apex then
		S.apex = apex
		if apex > 0 then
			local b = L.bytPoId(S, apex)
			table.insert(zd, { t = "apex", id = apex, s = b and b.slot or 0 })
		end
	end
	return zd
end

------------------------------------------------------------------ zabawka 2: LURE A MONSTER
local function losujNr(S, stopnie)
	local lista = {}
	for i, P in S.D.pety do
		for _, s in stopnie do
			if P.stopien == s then
				table.insert(lista, i)
			end
		end
	end
	return lista[1 + math.floor(S.los() * #lista)] or 1
end

function L.nowyStan2(D, los)
	local S = { D = D, W = D.wabik, los = los, czas = 0, potwory = {}, nastId = 1, przynety = {}, gracze = {},
		nastRzadki = D.wabik.rzadki_co_s }
	for si, St in S.W.strefy do
		for _ = 1, St.ile do
			L.dodajPotwora(S, si)
		end
	end
	return S
end

local function celWStrefie(S, St)
	local W = S.W
	return (S.los() - 0.5) * (W.laka_szer - 16), St.od + 4 + S.los() * (St.koniec - St.od - 8)
end

function L.promienPotwora(S, p): number
	local P = S.D.pety[p.nr]
	return P.promien * p.skala
end

function L.dodajPotwora(S, si: number, rzadki: boolean?)
	local W = S.W
	local St = W.strefy[si]
	local x, z = celWStrefie(S, St)
	local p = { id = S.nastId, nr = losujNr(S, if rzadki then { 4, 5 } else St.stopnie), strefa = si, x = x, z = z, cx = x, cz = z,
		v = St.v, stan = "laka", wl = 0, odm = nil, skala = W.skala_strefy[si], kier = 0, uciekaDo = 0, rzadki = rzadki == true }
	if rzadki then
		-- rzadki biegacz: przecina daleką strefę z boku na bok
		p.x = -W.laka_szer / 2 - 6
		p.cx, p.cz = W.laka_szer / 2 + 10, p.z
		p.v = W.rzadki_v
	end
	S.nastId += 1
	table.insert(S.potwory, p)
	return p
end

function L.zasieg(W, zwabionych: number): number
	return math.min(W.zasieg_maks, W.zasieg0 + W.zasieg_za * zwabionych)
end

-- lądowanie przynęty: start z przodu zagrody slotu; kąt (rad, 0 = w głąb łąki) i siła 0–1
function L.ladowanie(W, slot: number, kat: number, moc: number, zasieg: number): (number, number, number, number, number)
	local zp = W.zagrodyPoz[slot]
	local x0, z0 = zp[1], zp[2] + W.zagroda_gl / 2
	local km = math.rad(W.kat_maks_st)
	kat = math.clamp(kat, -km, km)
	moc = math.clamp(moc, 0, 1)
	local d = W.zasieg_min + moc * (zasieg - W.zasieg_min)
	return x0 + math.sin(kat) * d, z0 + math.cos(kat) * d, W.lot_s + d * W.lot_na_stud, x0, z0
end

function L.gracz2(S, slot: number)
	local g = S.gracze[slot]
	if not g then
		g = { zwabione = 0, najlepszy = nil, ostRzut = -99, wZagrodzie = {} }
		S.gracze[slot] = g
	end
	return g
end

-- rzut gracza (serwer sprawdza typy); nil, gdy za szybko
function L.rzut2(S, slot: number, kat: number, moc: number)
	local g = L.gracz2(S, slot)
	if S.czas - g.ostRzut < S.W.rzut_przerwa_s then
		return nil
	end
	g.ostRzut = S.czas
	local x, z, t, x0, z0 = L.ladowanie(S.W, slot, kat, moc, L.zasieg(S.W, g.zwabione))
	local pr = { slot = slot, x = x, z = z, x0 = x0, z0 = z0, ladT = S.czas + t, czas = t }
	table.insert(S.przynety, pr)
	return pr
end

function L.losujOdmiane(W, r: number): string?
	local x = r
	for _, o in W.odmiany do
		x -= o.szansa
		if x < 0 then
			return o.id
		end
	end
	return nil
end

local function miejsceWZagrodzie(S, slot: number, k: number): (number, number)
	local W = S.W
	local zp = W.zagrodyPoz[slot]
	local kol = (k - 1) % 4
	local rz = math.floor((k - 1) / 4) % 3
	return zp[1] + (kol - 1.5) * (W.zagroda_szer / 4.4), zp[2] - W.zagroda_gl / 2 + 2 + rz * 3
end

-- krok zabawki 2: ruch potworów, lądowania przynęt (zwabienie albo pudło), rzadki biegacz → lista zdarzeń
function L.krok2(S, dt: number, losOdm: (() -> number)?)
	local W = S.W
	S.czas += dt
	local zd = {}
	-- rzadki biegacz
	if S.czas >= S.nastRzadki then
		S.nastRzadki = S.czas + W.rzadki_co_s
		local p = L.dodajPotwora(S, #W.strefy, true)
		table.insert(zd, { t = "rzadki", id = p.id, nr = p.nr })
	end
	local zostaja = {}
	for _, p in S.potwory do
		local usun = false
		if p.stan == "laka" or p.stan == "ucieka" then
			local v = if p.stan == "ucieka" and S.czas < p.uciekaDo then p.v * 2.6 + 6 else p.v
			if p.stan == "ucieka" and S.czas >= p.uciekaDo then
				p.stan = "laka"
				p.cx, p.cz = celWStrefie(S, W.strefy[p.strefa])
			end
			local dx, dz = p.cx - p.x, p.cz - p.z
			local d = dlug(dx, dz)
			if d < 1 then
				if p.rzadki then
					usun = true
				else
					p.cx, p.cz = celWStrefie(S, W.strefy[p.strefa])
				end
			else
				local k = math.min(d, v * dt)
				p.x += dx / d * k
				p.z += dz / d * k
				p.kier = math.atan2(dx, dz)
			end
			if not p.rzadki and S.los() < dt * 0.25 then
				p.cx, p.cz = celWStrefie(S, W.strefy[p.strefa])
			end
		elseif p.stan == "idzie" then
			local dx, dz = p.cx - p.x, p.cz - p.z
			local d = dlug(dx, dz)
			if d < 0.6 then
				p.stan = "zagroda"
				p.kier = math.pi
			else
				local k = math.min(d, W.idzie_v * dt)
				p.x += dx / d * k
				p.z += dz / d * k
				p.kier = math.atan2(dx, dz)
			end
		end
		if not usun then
			table.insert(zostaja, p)
		end
	end
	S.potwory = zostaja
	-- lądowania przynęt
	local czekaja = {}
	for _, pr in S.przynety do
		if S.czas >= pr.ladT then
			local best, bd = nil, math.huge
			for _, p in S.potwory do
				if p.stan == "laka" or p.stan == "ucieka" then
					local d = dlug(p.x - pr.x, p.z - pr.z)
					if d < W.lap_r + L.promienPotwora(S, p) and d < bd then
						best, bd = p, d
					end
				end
			end
			if best then
				local g = L.gracz2(S, pr.slot)
				g.zwabione += 1
				local odm = L.losujOdmiane(W, if losOdm then losOdm() else S.los())
				best.odm = odm
				best.stan = "idzie"
				best.wl = pr.slot
				local k = #g.wZagrodzie + 1
				if k > W.w_zagrodzie_maks then
					-- pełna zagroda: najstarszy ustępuje miejsca (licznik zostaje)
					local stary = g.wZagrodzie[1]
					stary.usun = true
					for i = 1, #g.wZagrodzie - 1 do
						g.wZagrodzie[i] = g.wZagrodzie[i + 1]
					end
					g.wZagrodzie[#g.wZagrodzie] = nil
					k = #g.wZagrodzie + 1
				end
				g.wZagrodzie[k] = best
				best.cx, best.cz = miejsceWZagrodzie(S, pr.slot, k)
				local rz = S.D.pety[best.nr].stopien
				local wart = rz * 10 + (if odm == "giant" then 30 elseif odm == "golden" then 15 elseif odm == "big" then 5 else 0)
				if not g.najlepszy or wart > g.najlepszy.wart then
					g.najlepszy = { nr = best.nr, odm = odm, wart = wart }
				end
				table.insert(zd, { t = "zwabiony", slot = pr.slot, id = best.id, nr = best.nr, odm = odm, rz = rz, x = pr.x, z = pr.z,
					rzadki = best.rzadki })
				-- łąka się uzupełnia (rzadki biegacz nie)
				if not best.rzadki then
					L.dodajPotwora(S, best.strefa)
				end
			else
				for _, p in S.potwory do
					if (p.stan == "laka" or p.stan == "ucieka") and dlug(p.x - pr.x, p.z - pr.z) < W.ploszy_r then
						local d = math.max(0.1, dlug(p.x - pr.x, p.z - pr.z))
						p.stan = "ucieka"
						p.uciekaDo = S.czas + W.ploszy_s
						p.cx = math.clamp(p.x + (p.x - pr.x) / d * 20, -W.laka_szer / 2 + 4, W.laka_szer / 2 - 4)
						p.cz = math.clamp(p.z + (p.z - pr.z) / d * 20, W.strefy[1].od, W.strefy[#W.strefy].koniec)
					end
				end
				table.insert(zd, { t = "pudlo", slot = pr.slot, x = pr.x, z = pr.z })
			end
		else
			table.insert(czekaja, pr)
		end
	end
	S.przynety = czekaja
	-- usunięci z pełnych zagród
	local zost = {}
	for _, p in S.potwory do
		if not p.usun then
			table.insert(zost, p)
		end
	end
	S.potwory = zost
	return zd
end

-- gracz wychodzi: jego zwabione potwory znikają
function L.usunGracza2(S, slot: number)
	local zost = {}
	for _, p in S.potwory do
		if p.wl ~= slot then
			table.insert(zost, p)
		end
	end
	S.potwory = zost
	S.gracze[slot] = nil
end

return L
