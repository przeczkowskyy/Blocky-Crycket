--[[
	LogikaEwolucji — czyste rachunki Monster Evolution (ModuleScript w Workspace/EwolucjaGra/Moduly; też w testach bez Studio).
	Byty (gracze i boty) w 2D na polu-kole: formy 1–8 (stała drabina), jedzenie kulek i mniejszych (co najmniej o jedną
	formę), BITE, DASH, umiejętność formy, pasek wzrostu i EVOLVE z kokonem, legowisko (złoto na sekundę za każdą
	zdobytą formę), ulepszenia (Szczęka, Szybkość, Apetyt), śmierć o formę niżej z tarczą, proste boty.
	Serwer woła krok stałym krokiem; zdarzenia wracają listą. Wszystko liczy serwer — klient tylko przewiduje ruch.
]]
local L = {}

local function dlug(x: number, z: number): number
	return math.sqrt(x * x + z * z)
end
L.dlug = dlug

------------------------------------------------------------------ liczby
function L.promien(D, f: number): number
	return D.formy[f].r
end

function L.potrzeba(D, f: number): number
	return D.formy[f].potrzeba
end

-- złoto na sekundę z legowiska: suma trofeów zdobytych form (1..maxForma)
function L.stawka(D, maxForma: number): number
	local s = 0
	for i = 1, maxForma do
		s += D.formy[i].trofeum
	end
	return s
end

function L.ulepszenie(D, id: string)
	for _, U in D.ulepszenia do
		if U.id == id then
			return U
		end
	end
	return nil
end

function L.poziom(b, id: string): number
	return (b.poziomy and b.poziomy[id]) or 1
end

function L.cena(D, b, id: string): number?
	local U = L.ulepszenie(D, id)
	if not U then
		return nil
	end
	return U.ceny[L.poziom(b, id)]
end

function L.predkosc(D, b): number
	local baza
	if b.slot > 0 then
		baza = L.ulepszenie(D, "szybkosc").wartosci[L.poziom(b, "szybkosc")]
	else
		baza = D.ruch.bot_v
	end
	return baza * D.formy[b.forma].v
end

function L.apetyt(D, b): number
	if b.slot == 0 then
		return 1
	end
	return L.ulepszenie(D, "apetyt").wartosci[L.poziom(b, "apetyt")]
end

function L.zasiegGryzu(D, b): number
	if b.slot == 0 then
		return D.gryzienie.bot_zasieg
	end
	return L.ulepszenie(D, "szczeka").zasieg[L.poziom(b, "szczeka")]
end

function L.przerwaGryzu(D, b): number
	if b.slot == 0 then
		return D.gryzienie.bot_przerwa_s
	end
	return L.ulepszenie(D, "szczeka").przerwa_s[L.poziom(b, "szczeka")]
end

-- wartość zjedzonego stworka (przed Apetytem)
function L.wartosc(D, b): number
	local w = D.jedzenie.za_forme[b.forma]
	if b.slot > 0 then
		w *= D.jedzenie.gracz_x
	end
	return w
end

-- czy a może zjeść b (same zasady: forma co najmniej o jedną większa; formy chronione nie dla graczy)
function L.mozeZjesc(D, a, b): boolean
	if a.forma < b.forma + 1 then
		return false
	end
	if a.slot > 0 and b.slot > 0 and b.forma <= D.smierc.chronione_formy then
		return false
	end
	return true
end

-- czy b da się teraz zjeść / dotknąć (żywy, bez tarczy, nie w kokonie, nie w skoku)
local function wolny(S, b): boolean
	return b.martwyDo == nil and b.kokonDo == nil and b.skok == nil
end

local function bezbronny(S, b): boolean
	return wolny(S, b) and b.tarczaDo <= S.czas
end
L.bezbronny = bezbronny

------------------------------------------------------------------ stan
function L.nowyStan(D, los)
	local kulki = {}
	for i = 1, #D.kulkiPoz do
		kulki[i] = 0
	end
	return { D = D, los = los, czas = 0, byty = {}, nastId = 1, kulki = kulki, strefy = {}, olbrzym = 0 }
end

-- ograniczenia ruchu: pole-koło i przeszkody (wspólne dla serwera i przewidywania u klienta)
function L.ogranicz(D, x: number, z: number, r: number): (number, number)
	local d = dlug(x, z)
	local maks = D.pole.r - r * 0.6
	if d > maks then
		x, z = x / d * maks, z / d * maks
	end
	for _, s in D.przeszkody do
		local ds = dlug(x - s.x, z - s.z)
		local min = s.r + r * 0.7
		if ds < min and ds > 0.01 then
			x = s.x + (x - s.x) / ds * min
			z = s.z + (z - s.z) / ds * min
		end
	end
	return x, z
end

-- miejsce z dala od większych (dla gracza: obok kulki; dla bota: z dala od graczy)
function L.bezpieczneMiejsce(S, forma: number, gracz: boolean): (number, number)
	local D = S.D
	local najlepsze, wynik = -1, nil
	for proba = 1, 24 do
		local x, z
		if gracz then
			local i = 1 + math.floor(S.los() * #D.kulkiPoz)
			local k = D.kulkiPoz[i]
			x, z = k[1] * 0.97 + 3, k[2] * 0.97 - 3
		else
			local a = S.los() * 2 * math.pi
			local r = math.sqrt(S.los()) * (D.pole.r - 14)
			x, z = math.sin(a) * r, math.cos(a) * r
		end
		x, z = L.ogranicz(D, x, z, D.formy[forma].r)
		-- ocena: odległość do najbliższego zagrożenia (dla bota: do najbliższego gracza)
		local najbl = 999
		for _, q in S.byty do
			if q.martwyDo == nil then
				local d = dlug(q.x - x, q.z - z)
				if gracz then
					if q.forma > forma then
						najbl = math.min(najbl, d - q.forma * 2)
					end
				elseif q.slot > 0 then
					najbl = math.min(najbl, d)
				end
			end
		end
		if najbl > najlepsze then
			najlepsze, wynik = najbl, { x, z }
		end
		if (gracz and najbl > 45) or (not gracz and najbl > D.boty.od_graczy) then
			break
		end
		local _ = proba
	end
	return wynik[1], wynik[2]
end

function L.dodajByt(S, slot: number, forma: number, x: number?, z: number?)
	local D = S.D
	local px, pz = x, z
	if px == nil then
		px, pz = L.bezpieczneMiejsce(S, forma, slot > 0)
	end
	local b = { id = S.nastId, slot = slot, forma = forma, x = px, z = pz, vx = 0, vz = 0, wx = 0, wz = 0, kier = 0,
		tarczaDo = S.czas + (if slot > 0 then D.smierc.tarcza_s else 0), martwyDo = nil, kokonDo = nil, kokonNowa = false,
		zrywDo = 0, zrywGotowy = 0, gryzGotowy = 0, gryzDo = 0, umGotowy = 0, ogluszonyDo = 0, szarzaDo = 0, szarzaV = 1,
		skok = nil, myslDo = 0, cel = 0, celOd = 0, odpuszcza = 0, odpuszczaDo = 0, zjadl = 0, ostRaport = S.czas,
		wzrost = 0, maxForma = forma, zloto = 0, poziomy = { szczeka = 1, szybkosc = 1, apetyt = 1 },
		laskaDo = if slot > 0 then S.czas + D.boty.laska_s else 0, teraz = S.czas }
	S.nastId += 1
	table.insert(S.byty, b)
	if slot > 0 then
		table.insert(S.strefy, { x = px, z = pz, do_ = S.czas + D.boty.strefa_startu_s })
	end
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

function L.usunByt(S, b)
	local zost = {}
	for _, q in S.byty do
		if q ~= b then
			table.insert(zost, q)
		end
	end
	S.byty = zost
end

------------------------------------------------------------------ wejście gracza (serwer sprawdza typy)
function L.steruj(b, x: any, z: any): boolean
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

local function sterowanyPrzezSerwer(S, b): boolean
	return b.martwyDo ~= nil or b.kokonDo ~= nil or b.skok ~= nil or b.ogluszonyDo > S.czas
end
L.sterowanyPrzezSerwer = sterowanyPrzezSerwer

-- mnożnik prędkości teraz (zryw, szarża)
local function mnoznik(S, b): number
	local D = S.D
	local m = 1
	if S.czas < b.zrywDo then
		m = D.ruch.zryw_v
	end
	if S.czas < b.szarzaDo then
		m = math.max(m, b.szarzaV)
	end
	return m
end
L.mnoznik = mnoznik

-- pozycja od klienta (przewidywanie): przyjęta, jeśli zgadza się z prędkością; inaczej false (serwer poprawi klienta)
function L.pozycjaKlienta(S, b, x: any, z: any): boolean
	local D = S.D
	if type(x) ~= "number" or type(z) ~= "number" or x ~= x or z ~= z or math.abs(x) > 1e4 or math.abs(z) > 1e4 then
		return false
	end
	if sterowanyPrzezSerwer(S, b) then
		return false
	end
	local dt = math.min(1, S.czas - b.ostRaport)
	local maks = L.predkosc(D, b) * math.max(mnoznik(S, b), if S.czas - b.zrywDo < 0.5 then D.ruch.zryw_v else 1,
		if S.czas - b.szarzaDo < 0.5 then b.szarzaV else 1) * (dt + D.siec.tolerancja_s) + D.siec.tolerancja_st
	if dlug(x - b.x, z - b.z) > maks then
		return false
	end
	b.x, b.z = L.ogranicz(D, x, z, L.promien(D, b.forma))
	b.ostRaport = S.czas
	return true
end

function L.zryw(S, b): boolean
	if sterowanyPrzezSerwer(S, b) or S.czas < b.zrywGotowy then
		return false
	end
	b.zrywDo = S.czas + S.D.ruch.zryw_s
	b.zrywGotowy = S.czas + S.D.ruch.zryw_odnowa_s
	if b.wx == 0 and b.wz == 0 then
		b.wx, b.wz = math.sin(b.kier), math.cos(b.kier)
	end
	return true
end

------------------------------------------------------------------ jedzenie
local function zjedzKulke(S, b, i: number, zd)
	local D = S.D
	local typ = D.kulkiPoz[i][3]
	S.kulki[i] = S.czas + (if typ == 2 then D.jedzenie.powrot_duza_s else D.jedzenie.powrot_mala_s)
	if b.slot > 0 then
		L.dodajWzrost(S, b, (if typ == 2 then D.jedzenie.duza else D.jedzenie.mala) * L.apetyt(D, b))
	end
	table.insert(zd, { t = "kulka", i = i, id = b.id, s = b.slot })
end

function L.dodajWzrost(S, b, ile: number)
	local D = S.D
	if b.forma >= #D.formy then
		return
	end
	local p = L.potrzeba(D, b.forma)
	b.wzrost = math.min(p * D.ewolucja.pasek_maks, b.wzrost + ile)
end

function L.pelny(D, b): boolean
	return b.forma < #D.formy and b.wzrost >= L.potrzeba(D, b.forma)
end

local function zgin(S, b, zd)
	local D = S.D
	b.martwyDo = S.czas + (if b.slot > 0 then D.smierc.odrodzenie_s else D.boty.odrodzenie_s)
	b.vx, b.vz, b.wx, b.wz = 0, 0, 0, 0
	b.szarzaDo, b.zrywDo = 0, 0
	b.skok = nil
	table.insert(zd, { t = "smierc", id = b.id, s = b.slot, forma = b.forma })
end

-- a zjada b (sprawdzone wcześniej)
local function zjedz(S, a, b, zd, sposob: string)
	local D = S.D
	local zysk = L.wartosc(D, b) * L.apetyt(D, a)
	if a.slot > 0 then
		L.dodajWzrost(S, a, zysk)
	end
	a.zjadl += 1
	table.insert(zd, { t = "zjedz", a = a.id, b = b.id, x = b.x, z = b.z, f = b.forma, sa = a.slot, sb = b.slot, zysk = math.floor(zysk + 0.5),
		jak = sposob })
	zgin(S, b, zd)
end

-- bot a gracz q formy chronionej (1–2): tylko gdy bot na niego poluje (inaczej przypadkowe zjedzenie przy kulkach)
-- i nikogo w pierwszych laska_s sekundach jego sesji (pierwsze realne zagrożenie ok. 2:00)
local function przypadkiem(D, a, q): boolean
	if a.slot ~= 0 or q.slot == 0 then
		return false
	end
	return (q.laskaDo or 0) > (a.teraz or 0) or (q.forma <= D.smierc.chronione_formy and a.cel ~= q.id)
end
L.przypadkiem = przypadkiem

-- najbliższy jadalny dla a w promieniu zasieg (+ pół promienia ofiary)
local function najblizszaOfiara(S, a, zasieg: number)
	local D = S.D
	local ra = L.promien(D, a.forma)
	local best, bd = nil, math.huge
	for _, q in S.byty do
		if q ~= a and bezbronny(S, q) and L.mozeZjesc(D, a, q) and not przypadkiem(D, a, q) then
			local d = dlug(q.x - a.x, q.z - a.z)
			if d < ra + zasieg + L.promien(D, q.forma) * 0.5 and d < bd then
				best, bd = q, d
			end
		end
	end
	return best
end

-- kulki w promieniu (najbliższe najpierw), najwyżej ile
local function kulkiW(S, x: number, z: number, r: number, ile: number)
	local D = S.D
	local lista = {}
	for i, p in D.kulkiPoz do
		if S.kulki[i] == 0 then
			local d = dlug(p[1] - x, p[2] - z)
			if d < r then
				table.insert(lista, { i = i, d = d })
			end
		end
	end
	table.sort(lista, function(u, w)
		return u.d < w.d
	end)
	local w = {}
	for k = 1, math.min(ile, #lista) do
		table.insert(w, lista[k].i)
	end
	return w
end
L.kulkiW = kulkiW

-- BITE gracza: najbliższy jadalny w zasięgu Szczęki, inaczej do 3 kulek w zasięgu
function L.gryz(S, b, zd): boolean
	local D = S.D
	if sterowanyPrzezSerwer(S, b) or S.czas < b.gryzGotowy then
		return false
	end
	b.gryzGotowy = S.czas + L.przerwaGryzu(D, b)
	b.gryzDo = S.czas + D.gryzienie.slad_s
	local zas = L.zasiegGryzu(D, b)
	local q = najblizszaOfiara(S, b, zas)
	table.insert(zd, { t = "gryz", id = b.id, x = b.x, z = b.z, trafil = q ~= nil })
	if q then
		zjedz(S, b, q, zd, "gryz")
	else
		for _, i in kulkiW(S, b.x, b.z, L.promien(D, b.forma) + zas + D.jedzenie.mala_r, 3) do
			zjedzKulke(S, b, i, zd)
		end
	end
	return true
end

------------------------------------------------------------------ umiejętności (jeden przycisk; każda forma ma swoją)
local function oglusz(S, b, r: number, czas: number, zd)
	local D = S.D
	local n = 0
	for _, q in S.byty do
		if q ~= b and wolny(S, q) and q.tarczaDo <= S.czas and dlug(q.x - b.x, q.z - b.z) < r + L.promien(D, q.forma)
			and not (b.slot > 0 and q.slot > 0 and q.forma <= D.smierc.chronione_formy) then
			q.ogluszonyDo = S.czas + czas
			q.vx, q.vz = 0, 0
			n += 1
			table.insert(zd, { t = "ogluszony", id = q.id, s = q.slot, czas = czas })
		end
	end
	return n
end

function L.umiejetnosc(S, b, zd): boolean
	local D = S.D
	if sterowanyPrzezSerwer(S, b) or S.czas < b.umGotowy then
		return false
	end
	local A = D.formy[b.forma].um
	b.umGotowy = S.czas + A.odnowa_s
	local rb = L.promien(D, b.forma)
	table.insert(zd, { t = "umiejetnosc", id = b.id, s = b.slot, typ = A.typ, x = b.x, z = b.z, r = rb + (A.r or 0), kier = b.kier })
	if A.typ == "wsysanie" then
		for _, i in kulkiW(S, b.x, b.z, rb + A.r, 99) do
			zjedzKulke(S, b, i, zd)
		end
	elseif A.typ == "jezyk" then
		local q = najblizszaOfiara(S, b, A.r)
		if q then
			zjedz(S, b, q, zd, "jezyk")
		else
			for _, i in kulkiW(S, b.x, b.z, rb + A.r, 4) do
				zjedzKulke(S, b, i, zd)
			end
		end
	elseif A.typ == "szarza" then
		b.szarzaDo = S.czas + A.s
		b.szarzaV = A.v
		if b.wx == 0 and b.wz == 0 then
			b.wx, b.wz = math.sin(b.kier), math.cos(b.kier)
		end
	elseif A.typ == "ogluszenie" then
		oglusz(S, b, rb + A.r, A.s, zd)
	elseif A.typ == "skok" then
		local kx, kz = math.sin(b.kier), math.cos(b.kier)
		if b.wx ~= 0 or b.wz ~= 0 then
			local d = dlug(b.wx, b.wz)
			kx, kz = b.wx / d, b.wz / d
		end
		local x1, z1 = L.ogranicz(D, b.x + kx * A.d, b.z + kz * A.d, rb)
		b.skok = { x0 = b.x, z0 = b.z, x1 = x1, z1 = z1, t0 = S.czas, t1 = S.czas + A.s, r = A.r }
		b.kier = math.atan2(kx, kz)
	elseif A.typ == "fala" then
		oglusz(S, b, rb + A.r, A.s, zd)
		for _, i in kulkiW(S, b.x, b.z, rb + A.r, 99) do
			zjedzKulke(S, b, i, zd)
		end
	end
	return true
end

------------------------------------------------------------------ ewolucja, ulepszenia
function L.ewoluuj(S, b, zd): boolean
	local D = S.D
	if not L.pelny(D, b) or sterowanyPrzezSerwer(S, b) then
		return false
	end
	local nowa = b.forma + 1 > b.maxForma
	b.kokonDo = S.czas + (if nowa then D.ewolucja.kokon_s else D.ewolucja.kokon_znana_s)
	b.kokonNowa = nowa
	b.vx, b.vz, b.wx, b.wz = 0, 0, 0, 0
	table.insert(zd, { t = "kokon", id = b.id, s = b.slot, nowa = nowa, forma = b.forma + 1, czas = b.kokonDo - S.czas })
	return true
end

function L.kup(S, b, id: any): (boolean, string?)
	local D = S.D
	if type(id) ~= "string" then
		return false, "typ"
	end
	local U = L.ulepszenie(D, id)
	if not U or b.slot == 0 then
		return false, "brak"
	end
	local p = L.poziom(b, id)
	local cena = U.ceny[p]
	if not cena then
		return false, "maks"
	end
	if b.zloto < cena then
		return false, "zloto"
	end
	b.zloto -= cena
	b.poziomy[id] = p + 1
	return true, nil
end

------------------------------------------------------------------ boty
function L.mysl(S, b)
	local D = S.D
	local B = D.boty
	local r = L.promien(D, b.forma)
	local zagr, dz = nil, math.huge
	local ofiara, dof = nil, math.huge
	for _, q in S.byty do
		if q ~= b and q.martwyDo == nil then
			local d = dlug(q.x - b.x, q.z - b.z)
			local rq = L.promien(D, q.forma)
			if L.mozeZjesc(D, q, b) and wolny(S, q) then
				if d < B.widzi + rq and d < dz then
					zagr, dz = q, d
				end
			elseif L.mozeZjesc(D, b, q) and bezbronny(S, q) then
				local widzi = B.widzi
				if q.slot > 0 and q.forma <= D.smierc.chronione_formy then
					widzi = B.widzi_mlodych
				end
				if (q.id == b.odpuszcza and S.czas < b.odpuszczaDo) or (q.slot > 0 and q.laskaDo > S.czas) then
					widzi = -999
				end
				if d < widzi + r and d < dof then
					ofiara, dof = q, d
				end
			end
		end
	end
	-- świeże miejsca odrodzenia graczy: większe boty nie polują tam i wychodzą
	local strefa = nil
	if b.forma > 1 then
		for _, s in S.strefy do
			if S.czas < s.do_ and dlug(b.x - s.x, b.z - s.z) < B.strefa_startu_r + r then
				strefa = s
			end
		end
	end
	if ofiara and ofiara.slot > 0 then
		for _, s in S.strefy do
			if S.czas < s.do_ and dlug(ofiara.x - s.x, ofiara.z - s.z) < B.strefa_startu_r then
				ofiara = nil
				break
			end
		end
	end
	if zagr then
		local d = math.max(0.1, dz)
		local ux, uz = (b.x - zagr.x) / d, (b.z - zagr.z) / d
		-- przy murze: uciekaj wzdłuż (nie w ścianę)
		local dc = dlug(b.x, b.z)
		if dc > D.pole.r - 20 then
			local tx, tz = -b.z / dc, b.x / dc
			if tx * ux + tz * uz < 0 then
				tx, tz = -tx, -tz
			end
			ux, uz = ux * 0.4 + tx * 0.6 - b.x / dc * 0.3, uz * 0.4 + tz * 0.6 - b.z / dc * 0.3
		end
		local n = math.max(0.01, dlug(ux, uz))
		b.wx, b.wz = ux / n * B.panika, uz / n * B.panika
		if dz < L.promien(D, zagr.forma) + r + 5 and S.los() < B.zryw_szansa then
			L.zryw(S, b)
		end
		b.cel = 0
	elseif strefa then
		local d = math.max(0.1, dlug(b.x - strefa.x, b.z - strefa.z))
		b.wx, b.wz = (b.x - strefa.x) / d, (b.z - strefa.z) / d
		b.cel = 0
	elseif ofiara then
		if b.cel ~= ofiara.id then
			b.cel, b.celOd = ofiara.id, S.czas
		elseif S.czas - b.celOd > B.goni_maks_s then
			b.odpuszcza, b.odpuszczaDo = ofiara.id, S.czas + B.odpuszcza_s
			b.cel = 0
		end
		local d = math.max(0.1, dof)
		b.wx, b.wz = (ofiara.x - b.x) / d, (ofiara.z - b.z) / d
		if dof < r + L.promien(D, ofiara.forma) + 6 and S.los() < B.zryw_szansa then
			L.zryw(S, b)
		end
	else
		b.cel = 0
		local best, bd = nil, 34
		if b.forma <= B.kulki_do then
			for i, p in D.kulkiPoz do
				if S.kulki[i] == 0 then
					local d = dlug(p[1] - b.x, p[2] - b.z)
					if d < bd then
						best, bd = p, d
					end
				end
			end
		end
		if best then
			local d = math.max(0.1, bd)
			b.wx, b.wz = (best[1] - b.x) / d * 0.85, (best[2] - b.z) / d * 0.85
		elseif S.los() < 0.25 or (b.wx == 0 and b.wz == 0) then
			local a = S.los() * 2 * math.pi
			-- spacer: lekko do środka, żeby nie stać pod murem
			b.wx, b.wz = math.sin(a) * 0.6 - b.x / D.pole.r * 0.3, math.cos(a) * 0.6 - b.z / D.pole.r * 0.3
		end
	end
	b.myslDo = S.czas + B.myslenie_s * (0.7 + S.los() * 0.6)
end

------------------------------------------------------------------ krok
local function odrodz(S, b, zd)
	local D = S.D
	if b.slot > 0 then
		b.forma = math.max(1, b.forma - 1)
		b.wzrost = L.potrzeba(D, b.forma) * D.smierc.pasek_po
		b.tarczaDo = S.czas + D.smierc.tarcza_s
	else
		b.tarczaDo = S.czas + 1
	end
	b.martwyDo = nil
	b.ogluszonyDo = 0
	b.x, b.z = L.bezpieczneMiejsce(S, b.forma, b.slot > 0)
	b.ostRaport = S.czas
	if b.slot > 0 then
		table.insert(S.strefy, { x = b.x, z = b.z, do_ = S.czas + D.boty.strefa_startu_s })
	end
	table.insert(zd, { t = "odrodzenie", id = b.id, s = b.slot, x = b.x, z = b.z, forma = b.forma })
end

function L.krok(S, dt: number)
	local D = S.D
	S.czas += dt
	local zd = {}
	-- strefy startu: wygasłe precz
	local st = {}
	for _, s in S.strefy do
		if S.czas < s.do_ then
			table.insert(st, s)
		end
	end
	S.strefy = st
	for _, b in S.byty do
		b.teraz = S.czas
		if b.slot > 0 then
			b.zloto += L.stawka(D, b.maxForma) * dt
		end
		local r = L.promien(D, b.forma)
		if b.martwyDo then
			if S.czas >= b.martwyDo then
				odrodz(S, b, zd)
			end
		elseif b.kokonDo then
			if S.czas >= b.kokonDo then
				local p = L.potrzeba(D, b.forma)
				b.forma += 1
				b.kokonDo = nil
				local nowa = b.forma > b.maxForma
				if nowa then
					b.maxForma = b.forma
				end
				b.wzrost = if b.forma < #D.formy then math.min(math.max(0, b.wzrost - p), L.potrzeba(D, b.forma) * D.ewolucja.nadmiar) else 0
				b.tarczaDo = math.max(b.tarczaDo, S.czas + D.ewolucja.tarcza_po_s)
				b.umGotowy = 0
				b.x, b.z = L.ogranicz(D, b.x, b.z, L.promien(D, b.forma))
				table.insert(zd, { t = "ewolucja", id = b.id, s = b.slot, forma = b.forma, nowa = nowa })
				if b.forma == #D.formy and b.slot > 0 then
					S.olbrzym = b.id
					table.insert(zd, { t = "olbrzym", id = b.id, s = b.slot })
				end
			end
		elseif b.skok then
			local k = b.skok
			local f = math.clamp((S.czas - k.t0) / (k.t1 - k.t0), 0, 1)
			b.x = k.x0 + (k.x1 - k.x0) * f
			b.z = k.z0 + (k.z1 - k.z0) * f
			b.ostRaport = S.czas
			if f >= 1 then
				b.skok = nil
				local zjedzone = 0
				for _, q in S.byty do
					if q ~= b and bezbronny(S, q) and L.mozeZjesc(D, b, q) and zjedzone < 3
						and dlug(q.x - b.x, q.z - b.z) < r + k.r + L.promien(D, q.forma) * 0.5 then
						zjedz(S, b, q, zd, "skok")
						zjedzone += 1
					end
				end
				oglusz(S, b, r + k.r + 4, 1.0, zd)
				for _, i in kulkiW(S, b.x, b.z, r + k.r, 99) do
					zjedzKulke(S, b, i, zd)
				end
				table.insert(zd, { t = "ladowanie", id = b.id, x = b.x, z = b.z, r = r + k.r })
			end
		elseif b.ogluszonyDo > S.czas then
			b.vx, b.vz = b.vx * 0.8, b.vz * 0.8
		else
			if b.slot == 0 and S.czas >= b.myslDo then
				L.mysl(S, b)
			end
			local v = L.predkosc(D, b) * mnoznik(S, b)
			local a = math.min(1, D.ruch.przyspieszenie * dt * (if mnoznik(S, b) > 1 then 3 else 1))
			b.vx += (b.wx * v - b.vx) * a
			b.vz += (b.wz * v - b.vz) * a
			b.x += b.vx * dt
			b.z += b.vz * dt
			if b.wx ~= 0 or b.wz ~= 0 then
				b.kier = math.atan2(b.wx, b.wz)
			end
			b.x, b.z = L.ogranicz(D, b.x, b.z, r)
			-- bot gryzie sam; szarża gracza też gryzie sama
			if (b.slot == 0 or S.czas < b.szarzaDo) and S.czas >= b.gryzGotowy then
				local q = najblizszaOfiara(S, b, if b.slot == 0 then L.zasiegGryzu(D, b) else 2)
				if q then
					b.gryzGotowy = S.czas + L.przerwaGryzu(D, b)
					b.gryzDo = S.czas + D.gryzienie.slad_s
					table.insert(zd, { t = "gryz", id = b.id, x = b.x, z = b.z, trafil = true })
					zjedz(S, b, q, zd, "gryz")
				end
			end
		end
	end
	-- połknięcie dotykiem i odbicia
	local n = #S.byty
	for i = 1, n do
		local a = S.byty[i]
		for j = i + 1, n do
			local b = S.byty[j]
			if wolny(S, a) and wolny(S, b) then
				local ra, rb = L.promien(D, a.forma), L.promien(D, b.forma)
				local dx, dz = b.x - a.x, b.z - a.z
				local d = dlug(dx, dz)
				if d < ra + rb then
					local duzy, maly, rd, rm = a, b, ra, rb
					if b.forma > a.forma then
						duzy, maly, rd, rm = b, a, rb, ra
					end
					local moze = L.mozeZjesc(D, duzy, maly) and not przypadkiem(D, duzy, maly)
					if moze and maly.tarczaDo <= S.czas and d < rd - rm * D.gryzienie.polykanie and duzy.ogluszonyDo <= S.czas then
						zjedz(S, duzy, maly, zd, "dotyk")
					elseif not moze or maly.tarczaDo > S.czas then
						-- odbicie (rozsuń; mniejszy odlatuje mocniej)
						local nx, nz = if d > 0.01 then dx / d else 1, if d > 0.01 then dz / d else 0
						local wnik = ra + rb - d
						local wa = if a.forma > b.forma then 0.25 elseif a.forma < b.forma then 0.75 else 0.5
						a.x -= nx * wnik * wa
						a.z -= nz * wnik * wa
						b.x += nx * wnik * (1 - wa)
						b.z += nz * wnik * (1 - wa)
						local va = a.vx * nx + a.vz * nz
						local vb = b.vx * nx + b.vz * nz
						local imp = math.max(0, va - vb) * 0.6 + 3
						a.vx -= nx * imp
						a.vz -= nz * imp
						b.vx += nx * imp
						b.vz += nz * imp
						if not a.odbicieDo or a.odbicieDo < S.czas then
							a.odbicieDo = S.czas + 0.35
							table.insert(zd, { t = "odbicie", a = a.id, b = b.id, x = (a.x + b.x) / 2, z = (a.z + b.z) / 2 })
						end
					end
				end
			end
		end
	end
	-- kulki: zbieranie dotykiem, powrót
	local zz = D.jedzenie.zasieg_zbierania
	for i, p in D.kulkiPoz do
		if S.kulki[i] == 0 then
			local kr = if p[3] == 2 then D.jedzenie.duza_r else D.jedzenie.mala_r
			for _, b in S.byty do
				if wolny(S, b) and (b.slot > 0 or b.forma <= D.boty.kulki_do) then
					local dx, dz = p[1] - b.x, p[2] - b.z
					local g = L.promien(D, b.forma) + kr + zz
					if dx * dx + dz * dz < g * g then
						zjedzKulke(S, b, i, zd)
						break
					end
				end
			end
		elseif S.czas >= S.kulki[i] then
			S.kulki[i] = 0
		end
	end
	return zd
end

return L
