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

-- złoto na sekundę z legowiska: suma trofeów zdobytych form (1..maxForma), poziom 1, bez wariantów
function L.stawka(D, maxForma: number): number
	local s = 0
	for i = 1, maxForma do
		s += D.formy[i].trofeum
	end
	return s
end

function L.wariant(D, id: any)
	for _, W in D.warianty do
		if W.id == id then
			return W
		end
	end
	return nil
end

function L.wariantX(D, id: any): number
	local W = L.wariant(D, id)
	return if W then W.x else 1
end

-- losowanie wariantu przy ewolucji (r w [0, 1)): rzadsze sprawdzane od najrzadszego
function L.losujWariant(D, r: number): string?
	local x = r
	for i = #D.warianty, 1, -1 do
		local W = D.warianty[i]
		x -= W.szansa
		if x < 0 then
			return W.id
		end
	end
	return nil
end

function L.poziomTrofeum(b, f: number): number
	return (b.trofea and b.trofea[f]) or 1
end

-- pełna stawka gracza: trofea × poziom × najlepszy wariant + trofea bossa
function L.stawkaB(D, b): number
	local G = D.legowisko
	local s = 0
	for f = 1, b.maxForma do
		s += D.formy[f].trofeum * G.poziomy_x[L.poziomTrofeum(b, f)] * L.wariantX(D, b.warianty and b.warianty[f])
	end
	for t = 1, math.min(b.bossTrofea or 0, #G.boss_trofea) do
		s += G.boss_trofea[t]
	end
	return s
end

function L.cenaTrofeum(D, b, f: number): number?
	local p = L.poziomTrofeum(b, f)
	local c = D.legowisko.ceny_x[p]
	if not c then
		return nil
	end
	return math.floor(c * D.formy[f].trofeum)
end

-- legowisko gracza: środek (względem pola) i czy byt stoi we własnym
function L.legowiskoPoz(D, slot: number): (number, number)
	local p = D.legowiska[((slot - 1) % #D.legowiska) + 1]
	return p[1], p[2]
end

function L.wLegowisku(D, b): boolean
	if b.slot == 0 then
		return false
	end
	local x, z = L.legowiskoPoz(D, b.slot)
	return dlug(b.x - x, b.z - z) < D.legowisko.r
end

-- boty nie wchodzą do żadnego legowiska
function L.pozaLegowiskami(D, x: number, z: number, r: number): (number, number)
	for _, p in D.legowiska do
		local d = dlug(x - p[1], z - p[2])
		local min = D.legowisko.r + r * 0.7
		if d < min and d > 0.01 then
			x, z = p[1] + (x - p[1]) / d * min, p[2] + (z - p[2]) / d * min
		end
	end
	return x, z
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
	if a.boss or b.boss or a.forma < b.forma + 1 then
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
	return wolny(S, b) and b.tarczaDo <= S.czas and not (b.slot > 0 and L.wLegowisku(S.D, b))
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

-- strefy ruchu: 1 — łąka, 2 — DEEP WOODS, 3 — obie (gracz z formą od_formy zdobytą); boty i boss tylko swoja strefa
function L.maska(D, b): number
	if b.slot == 0 then
		return b.strefa or 1
	end
	return if b.maxForma >= D.las.od_formy then 3 else 1
end

function L.wLesie(D, x: number, z: number): boolean
	return dlug(x - D.las.x, z - D.las.z) < D.las.r and dlug(x, z) > D.pole.r - 2
end

-- ograniczenia ruchu: suma dozwolonych kół i przeszkody (wspólne dla serwera i przewidywania u klienta)
function L.ogranicz(D, x: number, z: number, r: number, maska: number?): (number, number)
	local m = maska or 1
	local m1 = D.pole.r - r * 0.6
	local m2 = D.las.r - r * 0.6
	local d1 = dlug(x, z)
	local lx, lz = x - D.las.x, z - D.las.z
	local d2 = dlug(lx, lz)
	local ok1 = m ~= 2 and d1 <= m1
	local ok2 = m >= 2 and d2 <= m2
	if not ok1 and not ok2 then
		local e1 = if m ~= 2 then d1 - m1 else math.huge
		local e2 = if m >= 2 then d2 - m2 else math.huge
		if e1 <= e2 then
			x, z = x / d1 * m1, z / d1 * m1
		else
			x, z = D.las.x + lx / d2 * m2, D.las.z + lz / d2 * m2
		end
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
function L.bezpieczneMiejsce(S, forma: number, gracz: boolean, strefa: number?, slot: number?): (number, number)
	local D = S.D
	if gracz and slot and slot > 0 and D.legowiska then
		local x, z = L.legowiskoPoz(D, slot)
		return x * 0.97, z * 0.97
	end
	local najlepsze, wynik = -1, nil
	for proba = 1, 24 do
		local x, z
		if gracz then
			local i = 1 + math.floor(S.los() * #D.kulkiPoz)
			local k = D.kulkiPoz[i]
			x, z = k[1] * 0.97 + 3, k[2] * 0.97 - 3
		elseif strefa == 2 then
			local a = S.los() * 2 * math.pi
			local r = math.sqrt(S.los()) * (D.las.r - 14)
			x, z = D.las.x + math.sin(a) * r, D.las.z + math.cos(a) * r
			if dlug(x, z) < D.pole.r + 6 then
				x, z = D.las.x, D.las.z + D.las.r * 0.4
			end
		else
			local a = S.los() * 2 * math.pi
			local r = math.sqrt(S.los()) * (D.pole.r - 14)
			x, z = math.sin(a) * r, math.cos(a) * r
		end
		x, z = L.ogranicz(D, x, z, D.formy[forma].r, if gracz then 1 else (strefa or 1))
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

function L.dodajByt(S, slot: number, forma: number, x: number?, z: number?, strefa: number?)
	local D = S.D
	local px, pz = x, z
	if px == nil then
		px, pz = L.bezpieczneMiejsce(S, forma, slot > 0, strefa, slot)
	end
	local b = { id = S.nastId, slot = slot, forma = forma, x = px, z = pz, vx = 0, vz = 0, wx = 0, wz = 0, kier = 0,
		tarczaDo = S.czas + (if slot > 0 then D.smierc.tarcza_s else 0), martwyDo = nil, kokonDo = nil, kokonNowa = false,
		zrywDo = 0, zrywGotowy = 0, gryzGotowy = 0, gryzDo = 0, umGotowy = 0, ogluszonyDo = 0, szarzaDo = 0, szarzaV = 1,
		skok = nil, myslDo = 0, cel = 0, celOd = 0, odpuszcza = 0, odpuszczaDo = 0, zjadl = 0, ostRaport = S.czas,
		wzrost = 0, maxForma = forma, zloto = 0, poziomy = { szczeka = 1, szybkosc = 1, apetyt = 1 },
		laskaDo = if slot > 0 then S.czas + D.boty.laska_s else 0, teraz = S.czas, strefa = strefa or 1,
		zlotoLeg = 0, warianty = {}, trofea = {}, bossTrofea = 0, wariantTeraz = nil }
	S.nastId += 1
	table.insert(S.byty, b)
	if slot > 0 then
		table.insert(S.strefy, { x = px, z = pz, do_ = S.czas + D.boty.strefa_startu_s })
	end
	return b
end

-- mini-boss lasu (jeden): bot z ranami, w swojej strefie, z domem
function L.dodajBossa(S)
	local D = S.D
	local B = D.boss
	local b = L.dodajByt(S, 0, B.forma, D.las.x, D.las.z, 2)
	b.boss = true
	S.bossStopien = S.bossStopien or 1
	b.hp, b.hpMaks = B.stopnie_hp[S.bossStopien], B.stopnie_hp[S.bossStopien]
	b.domX, b.domZ = b.x, b.z
	b.rany = {}
	b.ostRana = -99
	S.boss = b.id
	return b
end

-- rana bossa od gracza g; pokonany → skrzynia dla tego, kto zadał najwięcej ran
function L.ranBossa(S, boss, g, ile: number, zd)
	local D = S.D
	if not boss.boss or boss.martwyDo or boss.hp <= 0 then
		return
	end
	boss.hp = math.max(0, boss.hp - ile)
	boss.ostRana = S.czas
	local k = tostring(g.slot)
	boss.rany[k] = (boss.rany[k] or 0) + ile
	table.insert(zd, { t = "boss_rana", id = boss.id, s = g.slot, ile = ile, hp = boss.hp, x = boss.x, z = boss.z })
	if boss.hp <= 0 then
		local naj, najIle = nil, -1
		for _, q in S.byty do
			if q.slot > 0 and (boss.rany[tostring(q.slot)] or 0) > najIle then
				naj, najIle = q, boss.rany[tostring(q.slot)] or 0
			end
		end
		local st = S.bossStopien or 1
		local skrzynia = D.boss.stopnie_skrzynia[st]
		local nowe = false
		if naj then
			naj.zloto += skrzynia
			if (naj.bossTrofea or 0) < st then
				naj.bossTrofea = st
				nowe = true
			end
		end
		table.insert(zd, { t = "boss_pokonany", id = boss.id, s = naj and naj.slot or 0, zloto = skrzynia, x = boss.x, z = boss.z, stopien = st,
			trofeum = nowe })
		S.bossStopien = math.min(#D.boss.stopnie_hp, st + 1)
		boss.martwyDo = S.czas + (if st == 1 then D.boss.odrodzenie_s else D.boss.odrodzenie_dalej_s)
		boss.vx, boss.vz, boss.wx, boss.wz = 0, 0, 0, 0
		boss.rany = {}
	end
end

function L.obrazenia(D, g): number
	local B = D.boss
	return B.gryz_baza + B.gryz_na_forme * math.max(0, g.forma - 3) + 2 * (L.poziom(g, "szczeka") - 1)
end

-- Olbrzym jako boss serwera: inny gracz w zasięgu gryzie go za złoto; zero życia → Olbrzym spada o formę, skrzynia
local function olbrzymW(S, g, zasieg: number)
	local D = S.D
	if g.slot == 0 or (S.graczy or 0) < D.olbrzym.graczy_od then
		return nil
	end
	for _, q in S.byty do
		if q ~= g and q.slot > 0 and q.forma == #D.formy and wolny(S, q) and not L.mozeZjesc(D, g, q)
			and dlug(q.x - g.x, q.z - g.z) < L.promien(D, g.forma) + zasieg + L.promien(D, q.forma) then
			return q
		end
	end
	return nil
end

function L.ranOlbrzyma(S, q, g, zd)
	local D = S.D
	local O = D.olbrzym
	q.olbrzymHp = (q.olbrzymHp or O.hp) - (O.rana_baza + O.rana_na_forme * g.forma)
	g.zloto += O.za_trafienie
	table.insert(zd, { t = "olbrzym_rana", id = q.id, s = g.slot, hp = q.olbrzymHp, x = q.x, z = q.z, zloto = O.za_trafienie })
	if q.olbrzymHp <= 0 then
		q.forma = #D.formy - 1
		q.olbrzymHp = nil
		q.wzrost = 0
		q.tarczaDo = S.czas + 3
		g.zloto += O.skrzynia
		if S.olbrzym == q.id then
			S.olbrzym = 0
		end
		table.insert(zd, { t = "olbrzym_obalony", id = q.id, s = g.slot, sq = q.slot, zloto = O.skrzynia, x = q.x, z = q.z })
	end
end

-- boss w zasięgu gracza (żywy)
local function bossW(S, g, zasieg: number)
	local D = S.D
	local b = S.boss and L.bytPoId(S, S.boss)
	if not b or b.martwyDo or g.slot == 0 then
		return nil
	end
	-- pełny promień bossa: gracz i boss się odbijają, więc stykają się na r + R
	if dlug(b.x - g.x, b.z - g.z) < L.promien(D, g.forma) + zasieg + L.promien(D, b.forma) then
		return b
	end
	return nil
end
L.bossW = bossW

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
	b.x, b.z = L.ogranicz(D, x, z, L.promien(D, b.forma), L.maska(D, b))
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
	S.kulki[i] = S.czas + (if typ >= 2 then D.jedzenie.powrot_duza_s else D.jedzenie.powrot_mala_s)
	if b.slot > 0 then
		L.dodajWzrost(S, b, (if typ == 3 then D.jedzenie.wielka elseif typ == 2 then D.jedzenie.duza else D.jedzenie.mala) * L.apetyt(D, b))
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
	if a.slot > 0 and L.wLegowisku(D, a) then
		return nil
	end
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
	local boss = if q then nil else bossW(S, b, zas)
	local olb = if q or boss then nil else olbrzymW(S, b, zas)
	table.insert(zd, { t = "gryz", id = b.id, x = b.x, z = b.z, trafil = q ~= nil or boss ~= nil or olb ~= nil })
	if q then
		zjedz(S, b, q, zd, "gryz")
	elseif boss then
		L.ranBossa(S, boss, b, L.obrazenia(D, b), zd)
	elseif olb then
		L.ranOlbrzyma(S, olb, b, zd)
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
			q.ogluszonyDo = S.czas + (if q.boss then czas * 0.5 else czas)
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
		local boss = if q then nil else bossW(S, b, A.r)
		if q then
			zjedz(S, b, q, zd, "jezyk")
		elseif boss then
			L.ranBossa(S, boss, b, D.boss.um_obrazenia, zd)
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
		local boss = bossW(S, b, A.r)
		if boss then
			L.ranBossa(S, boss, b, D.boss.um_obrazenia, zd)
		end
	elseif A.typ == "skok" then
		local kx, kz = math.sin(b.kier), math.cos(b.kier)
		if b.wx ~= 0 or b.wz ~= 0 then
			local d = dlug(b.wx, b.wz)
			kx, kz = b.wx / d, b.wz / d
		end
		local x1, z1 = L.ogranicz(D, b.x + kx * A.d, b.z + kz * A.d, rb, L.maska(D, b))
		b.skok = { x0 = b.x, z0 = b.z, x1 = x1, z1 = z1, t0 = S.czas, t1 = S.czas + A.s, r = A.r }
		b.kier = math.atan2(kx, kz)
	elseif A.typ == "podmuch" then
		-- WING GUST: odpycha (i krótko ogłusza) wszystkich w promieniu, poza chronionymi graczami i bossem
		for _, q in S.byty do
			local d = dlug(q.x - b.x, q.z - b.z)
			if q ~= b and wolny(S, q) and q.tarczaDo <= S.czas and not q.boss and d < rb + A.r + L.promien(D, q.forma)
				and not (b.slot > 0 and q.slot > 0 and q.forma <= D.smierc.chronione_formy) then
				d = math.max(0.1, d)
				local nx, nz = (q.x - b.x) / d, (q.z - b.z) / d
				q.x, q.z = L.ogranicz(D, q.x + nx * A.sila, q.z + nz * A.sila, L.promien(D, q.forma), L.maska(D, q))
				q.vx, q.vz = nx * A.sila * 2, nz * A.sila * 2
				q.ogluszonyDo = S.czas + A.s
				table.insert(zd, { t = "ogluszony", id = q.id, s = q.slot, czas = A.s })
			end
		end
	elseif A.typ == "oddech" then
		-- FIRE BREATH: stożek przed pyskiem — do 3 jadalnych, kulki w stożku, rana bossa
		local kx, kz = math.sin(b.kier), math.cos(b.kier)
		local cosK = math.cos(math.rad(A.kat_st / 2))
		local function wStozku(x: number, z: number, zas: number): boolean
			local dx, dz = x - b.x, z - b.z
			local d = dlug(dx, dz)
			return d < zas and (d < 0.5 or (dx * kx + dz * kz) / d >= cosK)
		end
		if not (b.slot > 0 and L.wLegowisku(D, b)) then
			local n = 0
			for _, q in S.byty do
				if n < 3 and q ~= b and bezbronny(S, q) and L.mozeZjesc(D, b, q) and not przypadkiem(D, b, q)
					and wStozku(q.x, q.z, rb + A.r + L.promien(D, q.forma) * 0.5) then
					zjedz(S, b, q, zd, "oddech")
					n += 1
				end
			end
			for i, p in D.kulkiPoz do
				if S.kulki[i] == 0 and wStozku(p[1], p[2], rb + A.r) then
					zjedzKulke(S, b, i, zd)
				end
			end
			local boss = bossW(S, b, A.r)
			if boss and wStozku(boss.x, boss.z, rb + A.r + L.promien(D, boss.forma)) then
				L.ranBossa(S, boss, b, D.boss.um_obrazenia, zd)
			end
		end
	elseif A.typ == "fala" then
		oglusz(S, b, rb + A.r, A.s, zd)
		local boss = bossW(S, b, A.r)
		if boss then
			L.ranBossa(S, boss, b, D.boss.um_obrazenia, zd)
		end
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
	b.kokonWariant = if b.slot > 0 then (S.wymusWariant or L.losujWariant(D, S.los())) else nil
	S.wymusWariant = nil
	b.vx, b.vz, b.wx, b.wz = 0, 0, 0, 0
	table.insert(zd, { t = "kokon", id = b.id, s = b.slot, nowa = nowa, forma = b.forma + 1, czas = b.kokonDo - S.czas, wariant = b.kokonWariant })
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

function L.kupTrofeum(S, b, f: any): (boolean, string?)
	local D = S.D
	if type(f) ~= "number" or f ~= math.floor(f) or f < 1 or f > #D.formy or b.slot == 0 then
		return false, "typ"
	end
	if f > b.maxForma then
		return false, "brak"
	end
	if not L.wLegowisku(D, b) then
		return false, "legowisko"
	end
	local cena = L.cenaTrofeum(D, b, f)
	if not cena then
		return false, "maks"
	end
	if b.zloto < cena then
		return false, "zloto"
	end
	b.zloto -= cena
	b.trofea[f] = L.poziomTrofeum(b, f) + 1
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
		local cx, cz, R = 0, 0, D.pole.r
		if b.strefa == 2 then
			cx, cz, R = D.las.x, D.las.z, D.las.r
		end
		local dc = dlug(b.x - cx, b.z - cz)
		if dc > R - 20 then
			local tx, tz = -(b.z - cz) / dc, (b.x - cx) / dc
			if tx * ux + tz * uz < 0 then
				tx, tz = -tx, -tz
			end
			ux, uz = ux * 0.4 + tx * 0.6 - (b.x - cx) / dc * 0.3, uz * 0.4 + tz * 0.6 - (b.z - cz) / dc * 0.3
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
			local cx, cz, R = 0, 0, D.pole.r
			if b.strefa == 2 then
				cx, cz, R = D.las.x, D.las.z, D.las.r
			end
			b.wx, b.wz = math.sin(a) * 0.6 - (b.x - cx) / R * 0.3, math.cos(a) * 0.6 - (b.z - cz) / R * 0.3
		end
	end
	b.myslDo = S.czas + B.myslenie_s * (0.7 + S.los() * 0.6)
end

-- boss: najbliższy gracz w lesie w zasięgu wzroku, inaczej do domu
function L.myslBossa(S, b)
	local D = S.D
	local cel, dc = nil, D.boss.widzi
	for _, q in S.byty do
		if q.slot > 0 and wolny(S, q) and L.wLesie(D, q.x, q.z) then
			local d = dlug(q.x - b.x, q.z - b.z)
			if d < dc then
				cel, dc = q, d
			end
		end
	end
	if cel then
		b.cel = cel.id
		local d = math.max(0.1, dc)
		b.wx, b.wz = (cel.x - b.x) / d * D.boss.v, (cel.z - b.z) / d * D.boss.v
	else
		b.cel = 0
		local dx, dz = b.domX - b.x, b.domZ - b.z
		local d = dlug(dx, dz)
		if d > 6 then
			b.wx, b.wz = dx / d * D.boss.v * 0.6, dz / d * D.boss.v * 0.6
		elseif S.los() < 0.3 then
			local a = S.los() * 2 * math.pi
			b.wx, b.wz = math.sin(a) * 0.3, math.cos(a) * 0.3
		end
	end
	b.myslDo = S.czas + 0.3
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
	if b.boss then
		b.hpMaks = D.boss.stopnie_hp[S.bossStopien or 1]
		b.hp = b.hpMaks
		b.x, b.z = b.domX, b.domZ
		b.ostRaport = S.czas
		table.insert(zd, { t = "odrodzenie", id = b.id, s = 0, x = b.x, z = b.z, forma = b.forma, boss = true })
		return
	end
	b.x, b.z = L.bezpieczneMiejsce(S, b.forma, b.slot > 0, b.strefa, b.slot)
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
	local graczy = 0
	for _, b in S.byty do
		if b.slot > 0 then
			graczy += 1
		end
	end
	S.graczy = graczy
	for _, b in S.byty do
		b.teraz = S.czas
		if b.slot > 0 then
			b.zlotoLeg += L.stawkaB(D, b) * dt
			if S.olbrzym == b.id and b.forma == #D.formy and graczy >= D.olbrzym.graczy_od then
				b.zloto += D.olbrzym.korona_na_s * dt
			end
			if b.martwyDo == nil and b.zlotoLeg >= 1 and L.wLegowisku(D, b) then
				local ile = math.floor(b.zlotoLeg)
				b.zloto += ile
				b.zlotoLeg -= ile
				if ile >= 5 or not b.wDomu then
					table.insert(zd, { t = "zebrano", id = b.id, s = b.slot, ile = ile })
				end
			end
			b.wDomu = L.wLegowisku(D, b)
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
				b.x, b.z = L.ogranicz(D, b.x, b.z, L.promien(D, b.forma), L.maska(D, b))
				b.wariantTeraz = b.kokonWariant
				local najlepszy = false
				if b.kokonWariant and L.wariantX(D, b.kokonWariant) > L.wariantX(D, b.warianty[b.forma]) then
					b.warianty[b.forma] = b.kokonWariant
					najlepszy = true
				end
				if b.forma == #D.formy then
					b.olbrzymHp = D.olbrzym.hp
				end
				table.insert(zd, { t = "ewolucja", id = b.id, s = b.slot, forma = b.forma, nowa = nowa, wariant = b.kokonWariant, najlepszy = najlepszy })
				if nowa and b.forma == D.las.od_formy and b.slot > 0 then
					table.insert(zd, { t = "las_otwarty", id = b.id, s = b.slot })
				end
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
				local boss = bossW(S, b, k.r + 2)
				if boss then
					L.ranBossa(S, boss, b, D.boss.um_obrazenia, zd)
				end
				for _, i in kulkiW(S, b.x, b.z, r + k.r, 99) do
					zjedzKulke(S, b, i, zd)
				end
				table.insert(zd, { t = "ladowanie", id = b.id, x = b.x, z = b.z, r = r + k.r })
			end
		elseif b.ogluszonyDo > S.czas then
			b.vx, b.vz = b.vx * 0.8, b.vz * 0.8
		else
			if b.boss then
				if S.czas >= b.myslDo then
					L.myslBossa(S, b)
				end
				if S.czas - b.ostRana > D.boss.regen_po_s and b.hp < b.hpMaks then
					b.hp = math.min(b.hpMaks, b.hp + b.hpMaks * D.boss.regen_na_s * dt)
				end
			elseif b.slot == 0 and S.czas >= b.myslDo then
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
			b.x, b.z = L.ogranicz(D, b.x, b.z, r, L.maska(D, b))
			if b.slot == 0 then
				b.x, b.z = L.pozaLegowiskami(D, b.x, b.z, r)
			end
			if b.boss then
				-- boss gryzie: odrzut, krótkie ogłuszenie, kara z paska (nie zjada)
				local q = b.cel ~= 0 and L.bytPoId(S, b.cel)
				if q and S.czas >= b.gryzGotowy and bezbronny(S, q)
					and dlug(q.x - b.x, q.z - b.z) < r + D.boss.zasieg + L.promien(D, q.forma) * 0.5 then
					b.gryzGotowy = S.czas + D.boss.przerwa_s
					b.gryzDo = S.czas + D.gryzienie.slad_s
					local d = math.max(0.1, dlug(q.x - b.x, q.z - b.z))
					local nx, nz = (q.x - b.x) / d, (q.z - b.z) / d
					q.x, q.z = L.ogranicz(D, q.x + nx * 5, q.z + nz * 5, L.promien(D, q.forma), L.maska(D, q))
					q.vx, q.vz = nx * D.boss.odrzut, nz * D.boss.odrzut
					q.ogluszonyDo = S.czas + D.boss.ogluszenie_s
					local kara = if q.forma < #D.formy then L.potrzeba(D, q.forma) * D.boss.kara * D.boss.stopnie_rana_x[S.bossStopien or 1] else 0
					q.wzrost = math.max(0, q.wzrost - kara)
					table.insert(zd, { t = "boss_gryz", id = b.id, cel = q.id, s = q.slot, x = q.x, z = q.z, kara = math.floor(kara) })
				end
			elseif (b.slot == 0 or S.czas < b.szarzaDo) and S.czas >= b.gryzGotowy then
				local q = najblizszaOfiara(S, b, if b.slot == 0 then L.zasiegGryzu(D, b) else 2)
				local boss = if q or b.slot == 0 then nil else bossW(S, b, 2)
				if q or boss then
					b.gryzGotowy = S.czas + L.przerwaGryzu(D, b)
					b.gryzDo = S.czas + D.gryzienie.slad_s
					table.insert(zd, { t = "gryz", id = b.id, x = b.x, z = b.z, trafil = true })
					if q then
						zjedz(S, b, q, zd, "gryz")
					else
						L.ranBossa(S, boss, b, L.obrazenia(D, b), zd)
					end
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
						and not (maly.slot > 0 and L.wLegowisku(D, maly)) and not (duzy.slot > 0 and L.wLegowisku(D, duzy))
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
			local kr = if p[3] == 3 then D.jedzenie.wielka_r elseif p[3] == 2 then D.jedzenie.duza_r else D.jedzenie.mala_r
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

------------------------------------------------------------------ pomiar prób (D-128): anonimowe podsumowanie jednej sesji
-- M: miary sesji z serwera (formy, smierci, po_smierci, ulepszenia, leg, zb, tr, war, bs, sesja_s). Bez identyfikatora
-- ani nazwy gracza; „nowy” i „dni” z jego własnego zapisu. Same liczby, krótkie napisy i krótkie tablice.
function L.podsumowanie(D, M, dzien: string, nowy: boolean, dni: number)
	local function n(x: any, maks: number): number
		if type(x) ~= "number" or x ~= x then
			return 0
		end
		return math.clamp(math.floor(x + 0.5), 0, maks)
	end
	local t, maks = {}, 1
	for f = 1, #D.formy do
		local v = type(M.formy) == "table" and M.formy[tostring(f)]
		if type(v) == "number" then
			t[f] = n(v, 86400)
			maks = math.max(maks, f)
		else
			t[f] = -1
		end
	end
	local dl = n(M.sesja_s, 86400)
	local pierwsza = type(M.po_smierci) == "table" and M.po_smierci[1] or nil
	local war = {}
	for _, W in D.warianty do
		war[W.id] = n(type(M.war) == "table" and M.war[W.id] or 0, 99)
	end
	return { v = 1, d = string.sub(tostring(dzien), 1, 10), dl = dl, maks = maks, t = t, sm = n(M.smierci, 999),
		dalej = if pierwsza then pierwsza.dalej == true else false, po = if pierwsza then n(dl - (pierwsza.t or dl), 86400) else 0,
		leg = n(M.leg, 9999), zb = n(M.zb, 9999), ul = n(type(M.ulepszenia) == "table" and #M.ulepszenia or 0, 99), tr = n(M.tr, 99),
		bs = n(M.bs, #D.boss.stopnie_hp), war = war, nowy = nowy == true, dni = n(dni, 3650) }
end

------------------------------------------------------------------ zapis (profil, nieobecność, blokada sesji)
local function liczba(x: any, min: number, maks: number, dom: number): number
	if type(x) ~= "number" or x ~= x or x == math.huge or x == -math.huge then
		return dom
	end
	return math.clamp(x, min, maks)
end

function L.profilNowy(D)
	return { wersja = D.zapis.wersja, zloto = 0, zlotoLeg = 0, poziomy = { szczeka = 1, szybkosc = 1, apetyt = 1 }, maxForma = 1,
		warianty = {}, trofea = {}, bossTrofea = 0, ostatnio = 0, pierwszy = 0 }
end

-- dane z magazynu → profil (migracja wersji, uzgodnienie z szablonem, walidacja liczb i nazw)
function L.profilZ(D, dane: any)
	local p = L.profilNowy(D)
	if type(dane) ~= "table" then
		return p
	end
	local nf = #D.formy
	p.zloto = liczba(dane.zloto, 0, 1e12, 0)
	p.zlotoLeg = liczba(dane.zlotoLeg, 0, 1e12, 0)
	p.maxForma = math.floor(liczba(dane.maxForma, 1, nf, 1))
	p.bossTrofea = math.floor(liczba(dane.bossTrofea, 0, #D.boss.stopnie_hp, 0))
	p.ostatnio = liczba(dane.ostatnio, 0, 1e11, 0)
	p.pierwszy = liczba(dane.pierwszy, 0, 1e11, 0)
	if type(dane.poziomy) == "table" then
		for _, U in D.ulepszenia do
			p.poziomy[U.id] = math.floor(liczba(dane.poziomy[U.id], 1, #U.ceny + 1, 1))
		end
	end
	for f = 1, nf do
		local w = type(dane.warianty) == "table" and dane.warianty[f]
		if type(w) == "string" and L.wariant(D, w) then
			p.warianty[f] = w
		else
			p.warianty[f] = ""
		end
		local t = type(dane.trofea) == "table" and dane.trofea[f]
		p.trofea[f] = math.floor(liczba(t, 1, #D.legowisko.poziomy_x, 1))
	end
	return p
end

-- byt → profil do zapisu (same liczby, napisy i tablice)
function L.doProfilu(D, b, teraz: number)
	local p = L.profilNowy(D)
	p.zloto = math.floor(b.zloto)
	p.zlotoLeg = math.floor(b.zlotoLeg)
	p.maxForma = b.maxForma
	p.bossTrofea = b.bossTrofea or 0
	p.ostatnio = teraz
	p.pierwszy = b.pierwszy or teraz
	for _, U in D.ulepszenia do
		p.poziomy[U.id] = L.poziom(b, U.id)
	end
	for f = 1, #D.formy do
		p.warianty[f] = b.warianty[f] or ""
		p.trofea[f] = L.poziomTrofeum(b, f)
	end
	return p
end

-- profil → byt (forma od nowa: 1, reszta zostaje) + złoto legowiska za nieobecność (najwyżej nieobecnosc_maks_s)
function L.zProfilu(D, b, p, teraz: number): (number, number)
	b.zloto = p.zloto
	b.zlotoLeg = p.zlotoLeg
	b.maxForma = p.maxForma
	b.bossTrofea = p.bossTrofea
	b.pierwszy = if p.pierwszy > 0 then p.pierwszy else teraz
	b.poziomy = { szczeka = p.poziomy.szczeka, szybkosc = p.poziomy.szybkosc, apetyt = p.poziomy.apetyt }
	b.warianty, b.trofea = {}, {}
	for f = 1, #D.formy do
		b.warianty[f] = if p.warianty[f] ~= "" then p.warianty[f] else nil
		b.trofea[f] = p.trofea[f]
	end
	local sek = 0
	if p.ostatnio > 0 then
		sek = math.clamp(teraz - p.ostatnio, 0, D.zapis.nieobecnosc_maks_s)
	end
	local zarobek = math.floor(L.stawkaB(D, b) * sek)
	b.zlotoLeg += zarobek
	return zarobek, sek
end

local function kopia(x: any): any
	if type(x) ~= "table" then
		return x
	end
	local w = {}
	for k, v in x do
		w[k] = kopia(v)
	end
	return w
end
L.kopia = kopia

-- magazyn w pamięci (zastępstwo DataStore w Studio i w próbach): to samo UpdateAsync / GetAsync
function L.pamiec()
	local m = { dane = {} }
	m.UpdateAsync = function(self, klucz: string, fn)
		local nowy = fn(kopia(self.dane[klucz]))
		if nowy ~= nil then
			self.dane[klucz] = kopia(nowy)
		end
		return kopia(self.dane[klucz])
	end
	m.GetAsync = function(self, klucz: string)
		return kopia(self.dane[klucz])
	end
	return m
end

-- wczytanie z blokadą sesji: (profil, zapisywalny, powód). Cudza świeża blokada → bez zapisu (nie nadpisujemy)
function L.wczytaj(D, magazyn, klucz: string, job: string, teraz: number)
	local zajety = false
	local ok, wynik = pcall(function()
		return magazyn.UpdateAsync(magazyn, klucz, function(stary)
			if type(stary) == "table" and type(stary.sesja) == "table" and stary.sesja.job ~= job
				and teraz - (if type(stary.sesja.t) == "number" then stary.sesja.t else 0) < D.zapis.blokada_s then
				zajety = true
				return nil
			end
			local p = L.profilZ(D, stary)
			p.sesja = { job = job, t = teraz }
			return p
		end)
	end)
	if not ok then
		return L.profilNowy(D), false, "blad"
	end
	if zajety then
		return L.profilNowy(D), false, "zajety"
	end
	return L.profilZ(D, wynik), true, "ok"
end

-- zapis (z odnowieniem albo zwolnieniem blokady); cudza blokada → nie piszemy
function L.zapisz(D, magazyn, klucz: string, job: string, profil, teraz: number, zwolnij: boolean): (boolean, string)
	local cudzy = false
	local ok = pcall(function()
		magazyn.UpdateAsync(magazyn, klucz, function(stary)
			if type(stary) == "table" and type(stary.sesja) == "table" and stary.sesja.job ~= job then
				cudzy = true
				return nil
			end
			local p = kopia(profil)
			p.sesja = if zwolnij then nil else { job = job, t = teraz }
			return p
		end)
	end)
	if not ok then
		return false, "blad"
	end
	if cudzy then
		return false, "cudza_sesja"
	end
	return true, "ok"
end

return L
