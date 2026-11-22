--[[
	LogikaEwolucji — czyste rachunki Monster Evolution (ModuleScript w Workspace/EwolucjaGra/Moduly; też w testach bez Studio).
	Byty (gracze i boty) w 2D na polu-kole: formy 1–8 (stała drabina), jedzenie kulek, pasek wzrostu i EVOLVE z kokonem,
	legowisko (złoto na sekundę za każdą zdobytą formę), ulepszenia (Szczęka, Szybkość, Apetyt), śmierć o formę niżej z tarczą.
	Walka (walka1): jedna zasada dla wszystkich — życie według stadium, BITE w łańcuchu trzech ciosów, dwie linie zdolności
	(FIRE, POWER) ewoluujące ze stadiami, zamach widoczny dla innych, zero życia = zjedzony. Boty walczą tymi samymi zasadami.
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
	return D.walka.lancuch_s[1]
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
	return { D = D, los = los, czas = 0, byty = {}, nastId = 1, kulki = kulki, strefy = {}, olbrzym = 0, pociski = {}, plamy = {}, nastPocisk = 0 }
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
	local WY = D.wyspa
	if WY then
		local dw = dlug(x - WY.x, z - WY.z)
		local wew, zew = math.max(0.5, WY.r_wew - r * 0.6), WY.r_zew + r * 0.6
		if dw > wew and dw < zew and dw > 0.01 then
			local cel = if dw - wew < zew - dw then wew else zew
			x, z = WY.x + (x - WY.x) / dw * cel, WY.z + (z - WY.z) / dw * cel
		end
	end
	return x, z
end

-- czy punkt jest na wyspie (SKY NEST)
function L.naWyspie(D, x: number, z: number): boolean
	local WY = D.wyspa
	return WY ~= nil and dlug(x - WY.x, z - WY.z) < WY.r_wew
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
		if D.wyspa and L.naWyspie(D, x, z) then
			local WY = D.wyspa
			local dw = math.max(0.1, dlug(x - WY.x, z - WY.z))
			local m = WY.r_zew + D.formy[forma].r + 2
			x, z = WY.x + (x - WY.x) / dw * m, WY.z + (z - WY.z) / dw * m
		end
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
		zlotoLeg = 0, warianty = {}, trofea = {}, bossTrofea = 0, wariantTeraz = nil,
		hp = 0, hpMaks = 0, ostRana = -99, lancuch = 0, lancuchDo = 0, gotowy = { ogien = 0, moc = 0 }, zamach = nil, kanal = nil,
		napastnik = 0, napastnikDo = 0, uciekaOd = 0, uciekaDo = 0 }
	b.hpMaks = L.hpMaks(D, b)
	b.hp = b.hpMaks
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

-- siła BITE (przed łańcuchem i rozmiarem): stadium × Szczęka — także podstawa ran zdolności
function L.obrazenia(D, g): number
	local W = D.walka
	local s = W.gryz_baza * W.gryz_wzrost ^ (g.forma - 1)
	if g.slot > 0 then
		s *= W.szczeka_x[L.poziom(g, "szczeka")]
	end
	return s
end
L.silaGryzu = L.obrazenia

-- życie według stadium (boss: stopień)
function L.hpMaks(D, b): number
	if b.boss then
		return b.hpMaks
	end
	return D.walka.hp_baza * D.walka.hp_wzrost ^ (b.forma - 1)
end

-- mnożnik rozmiaru: różnica stadiów atakującego i celu (−3…+3); boss bez mnożnika
function L.rozmiarX(D, a, q): number
	if a.boss or q.boss then
		return 1
	end
	local d = math.clamp(a.forma - q.forma, -3, 3)
	return D.walka.rozmiar_x[d + 4]
end

-- Olbrzym jako boss serwera: inny gracz rani go za złoto (L.ran kieruje tu trafienia); zero życia → Olbrzym spada o formę
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
	if b.zamach or b.kanal then
		m *= D.walka.zamach_v
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
	if not b.boss and b.hp < b.hpMaks then
		b.hp = math.min(b.hpMaks, b.hp + b.hpMaks * D.walka.kulka_leczy[typ])
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
	b.skok, b.zamach, b.kanal, b.bossZamach = nil, nil, nil, nil
	b.lancuch = 0
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

------------------------------------------------------------------ walka (walka1): jedna zasada — życie, BITE w łańcuchu, zdolności
-- czy a może teraz zranić q: żywe, bez tarczy, nie w kokonie ani w locie, gracz nie we własnym legowisku; stadia 1–2 graczy
-- chronione przed graczami (w obie strony); boss rani tylko graczy i tylko gracze ranią bossa; bot nie rani młodego gracza
-- „przypadkiem” (tylko gdy na niego poluje i po łasce nowicjusza). zdalnie: pocisk / płonąca ziemia (stan atakującego bez znaczenia)
function L.mozeRanic(S, a, q, zdalnie: boolean?): boolean
	local D = S.D
	if q == a or not bezbronny(S, q) then
		return false
	end
	if not zdalnie and not wolny(S, a) then
		return false
	end
	if a.boss then
		return q.slot > 0
	end
	if q.boss then
		return a.slot > 0
	end
	if a.slot > 0 and L.wLegowisku(D, a) then
		return false
	end
	if a.slot > 0 and q.slot > 0 and (a.forma <= D.smierc.chronione_formy or q.forma <= D.smierc.chronione_formy) then
		return false
	end
	if przypadkiem(D, a, q) then
		return false
	end
	return true
end

-- rana: rozmiar, kryt, odrzut (z przewrotem przerywa zamach i kanał), zero życia → zjedzony (finisher)
function L.ran(S, a, q, ile: number, zd, jak: string, nx: number?, nz: number?, sila: number?, przewrot: number?, losKryt: boolean?)
	local D = S.D
	local W = D.walka
	ile *= L.rozmiarX(D, a, q)
	local kryt = losKryt == true and S.los() < W.kryt_szansa
	if kryt then
		ile *= W.kryt_x
	end
	ile = math.max(1, math.floor(ile + 0.5))
	if a.slot > 0 and a.tarczaDo > S.czas then
		a.tarczaDo = S.czas -- atak zdejmuje tarczę
	end
	if q.boss then
		L.ranBossa(S, q, a, ile, zd)
		return
	end
	if q.slot > 0 and a.slot > 0 and q.forma == #D.formy and (S.graczy or 0) >= D.olbrzym.graczy_od then
		L.ranOlbrzyma(S, q, a, zd)
		return
	end
	q.hp -= ile
	q.ostRana = S.czas
	q.napastnik, q.napastnikDo = a.id, S.czas + 5
	if sila and sila > 0 and nx and nz then
		q.vx, q.vz = nx * sila, nz * sila
		if przewrot then
			q.ogluszonyDo = math.max(q.ogluszonyDo, S.czas + przewrot)
			q.przewrotDo = S.czas + przewrot
			q.zamach, q.kanal = nil, nil
		end
	end
	table.insert(zd, { t = "rana", a = a.id, id = q.id, s = q.slot, sa = a.slot, ile = ile, hp = math.max(0, q.hp) / q.hpMaks, x = q.x, z = q.z,
		kr = kryt, jak = jak, pw = przewrot ~= nil })
	if q.hp <= 0 then
		zjedz(S, a, q, zd, jak)
	end
end

-- zasięg liczony od brzegu celu (odbicia trzymają stworki na styku r + R)
local function zasiegDo(D, q): number
	return L.promien(D, q.forma)
end

-- cel BITE z lekkim celowaniem: najpierw przed pyskiem (stożek celowanie_st), potem najbliższy w zasięgu;
-- bot gryzie tylko mniejszych, swój cel albo tego, kto go ranił
local function celGryzu(S, b, zas: number)
	local D = S.D
	local ra = L.promien(D, b.forma)
	local cosK = math.cos(math.rad(D.walka.celowanie_st))
	local kx, kz = math.sin(b.kier), math.cos(b.kier)
	local best, bw = nil, math.huge
	for _, q in S.byty do
		if L.mozeRanic(S, b, q) and (b.slot > 0 or q.forma < b.forma or q.id == b.cel or (q.id == b.napastnik and S.czas < b.napastnikDo)) then
			local dx, dz = q.x - b.x, q.z - b.z
			local d = dlug(dx, dz)
			if d < ra + zas + zasiegDo(D, q) then
				local przod = d < 0.5 or (dx * kx + dz * kz) / d >= cosK
				local w = d + (if przod then 0 else 8 + zas)
				if w < bw then
					best, bw = q, w
				end
			end
		end
	end
	return best
end
L.celGryzu = celGryzu

-- BITE: łańcuch trzech ciosów (snap, snap, chomp z odrzutem i przewrotem); bez celu gracz zjada do 3 kulek w zasięgu
function L.gryz(S, b, zd): boolean
	local D = S.D
	local W = D.walka
	if sterowanyPrzezSerwer(S, b) or S.czas < b.gryzGotowy or b.zamach or b.kanal then
		return false
	end
	if S.czas > b.lancuchDo then
		b.lancuch = 0
	end
	local k = b.lancuch % 3 + 1
	b.lancuch = k
	b.gryzGotowy = S.czas + W.lancuch_s[k]
	b.lancuchDo = S.czas + W.lancuch_s[k] + W.lancuch_reset_s
	b.gryzDo = S.czas + D.gryzienie.slad_s
	local zas = L.zasiegGryzu(D, b)
	local q = celGryzu(S, b, zas)
	table.insert(zd, { t = "gryz", id = b.id, x = b.x, z = b.z, k = k, trafil = q ~= nil })
	if q then
		local d = math.max(0.1, dlug(q.x - b.x, q.z - b.z))
		b.kier = math.atan2(q.x - b.x, q.z - b.z)
		L.ran(S, b, q, L.obrazenia(D, b) * W.lancuch_x[k], zd, "gryz", (q.x - b.x) / d, (q.z - b.z) / d,
			if k == 3 then W.odrzut else W.odrzut_maly, if k == 3 then W.przewrot_s else nil, true)
	elseif b.slot > 0 then
		for _, i in kulkiW(S, b.x, b.z, L.promien(D, b.forma) + zas + D.jedzenie.mala_r, 3) do
			zjedzKulke(S, b, i, zd)
		end
	end
	return true
end

------------------------------------------------------------------ zdolności: FIRE (ogien) i POWER (moc), ewoluują ze stadiami
-- działająca wersja linii dla stadium (największe od ≤ forma) i następna (do pokazania w HUD)
function L.zdolnoscFormy(D, linia: string, forma: number)
	local w = nil
	for _, A in D.zdolnosci[linia] or {} do
		if A.od <= forma then
			w = A
		end
	end
	return w
end

function L.nastepnaZdolnosc(D, linia: string, forma: number)
	for _, A in D.zdolnosci[linia] or {} do
		if A.od > forma then
			return A
		end
	end
	return nil
end

-- przycisk FIRE / POWER: najpierw zamach (widoczny dla innych), efekt po zamach_s
function L.zdolnosc(S, b, linia: any, zd): boolean
	local D = S.D
	if (linia ~= "ogien" and linia ~= "moc") or b.boss then
		return false
	end
	if sterowanyPrzezSerwer(S, b) or b.zamach or b.kanal then
		return false
	end
	local A = L.zdolnoscFormy(D, linia, b.forma)
	if not A or S.czas < (b.gotowy[linia] or 0) then
		return false
	end
	if b.slot > 0 and L.wLegowisku(D, b) and A.typ ~= "lot" then
		return false
	end
	local zs = L.zamachS(D, A, b.forma)
	-- boty rzadziej (czytelna łąka): dłuższa odnowa
	b.gotowy[linia] = S.czas + zs + A.odnowa_s * (if b.slot == 0 then D.boty.zdolnosci_odnowa_x or 1 else 1)
	b.zamach = { A = A, t1 = S.czas + zs }
	if b.wx ~= 0 or b.wz ~= 0 then
		b.kier = math.atan2(b.wx, b.wz)
	end
	table.insert(zd, { t = "zamach", id = b.id, s = b.slot, ab = A.id, czas = zs, kier = b.kier, x = b.x, z = b.z })
	return true
end
-- czas zamachu: chwila efektu w klipie stadium (zestaw blender: zdarzenie klipu), inaczej z danych zdolności
function L.zamachS(D, A, forma: number): number
	local F = D.formy[forma]
	return (F and F.czasy and F.czasy[A.id]) or A.zamach_s
end

-- zgodność: dawny jeden przycisk = FIRE
function L.umiejetnosc(S, b, zd, linia: any): boolean
	return L.zdolnosc(S, b, linia or "ogien", zd)
end

local function wStozku(b, x: number, z: number, zas: number, cosK: number): boolean
	local kx, kz = math.sin(b.kier), math.cos(b.kier)
	local dx, dz = x - b.x, z - b.z
	local d = dlug(dx, dz)
	return d < zas and (d < 0.5 or (dx * kx + dz * kz) / d >= cosK)
end

-- efekt po zamachu
local function wykonaj(S, b, A, zd)
	local D = S.D
	local rb = L.promien(D, b.forma)
	local kx, kz = math.sin(b.kier), math.cos(b.kier)
	local sila = L.obrazenia(D, b)
	if A.typ == "pocisk" then
		S.nastPocisk += 1
		local p = { n = S.nastPocisk, w = b.id, x = b.x + kx * rb, z = b.z + kz * rb, kx = kx, kz = kz, v = A.v, do_ = S.czas + A.zasieg / A.v,
			r = A.r, ile = sila * A.x, odrzut = A.odrzut }
		table.insert(S.pociski, p)
		table.insert(zd, { t = "pocisk", n = p.n, id = b.id, x = p.x, z = p.z, kx = kx, kz = kz, v = A.v, czas = A.zasieg / A.v })
	elseif A.typ == "oddech" then
		b.kanal = { A = A, do_ = S.czas + A.trwa_s, tik = S.czas, plama = S.czas }
		table.insert(zd, { t = "oddech", id = b.id, ab = A.id, czas = A.trwa_s })
	elseif A.typ == "ogon" then
		for _, q in S.byty do
			if L.mozeRanic(S, b, q) then
				local d = dlug(q.x - b.x, q.z - b.z)
				if d < rb + A.r + L.promien(D, q.forma) then
					d = math.max(0.1, d)
					L.ran(S, b, q, sila * A.x, zd, "ogon", (q.x - b.x) / d, (q.z - b.z) / d, A.odrzut, A.przewrot_s)
				end
			end
		end
		table.insert(zd, { t = "ogon", id = b.id, x = b.x, z = b.z, r = rb + A.r })
	elseif A.typ == "lot" or A.typ == "meteor" then
		local x1, z1 = L.ogranicz(D, b.x + kx * A.d, b.z + kz * A.d, rb, L.maska(D, b))
		b.skok = { x0 = b.x, z0 = b.z, x1 = x1, z1 = z1, t0 = S.czas, t1 = S.czas + A.s, A = A, r = A.r }
		b.kier = math.atan2(kx, kz)
		table.insert(zd, { t = A.typ, id = b.id, x0 = b.x, z0 = b.z, x1 = x1, z1 = z1, czas = A.s })
	elseif A.typ == "ryk" then
		for _, q in S.byty do
			local d = dlug(q.x - b.x, q.z - b.z)
			if L.mozeRanic(S, b, q) and d < rb + A.r + L.promien(D, q.forma) then
				L.ran(S, b, q, sila * A.x, zd, "ryk")
				if q.martwyDo == nil then
					if q.slot == 0 and not q.boss and q.forma < b.forma then
						q.uciekaOd, q.uciekaDo = b.id, S.czas + A.ucieczka_s
						q.myslDo = 0
					else
						local czas = if q.boss or q.forma > b.forma then A.ogluszenie_s * 0.5 else A.ogluszenie_s
						q.ogluszonyDo = math.max(q.ogluszonyDo, S.czas + czas)
						q.vx, q.vz = 0, 0
						q.zamach, q.kanal = nil, nil
						table.insert(zd, { t = "ogluszony", id = q.id, s = q.slot, czas = czas })
					end
				end
			end
		end
		table.insert(zd, { t = "ryk", id = b.id, x = b.x, z = b.z, r = rb + A.r })
	end
end
L.wykonaj = wykonaj

-- lądowanie po szybowaniu / meteorze: rany w kręgu, odrzut; meteor zbiera kulki w kręgu
local function ladowanie(S, b, k, zd)
	local D = S.D
	local A = k.A
	local r = L.promien(D, b.forma)
	if not A then
		return
	end
	for _, q in S.byty do
		if L.mozeRanic(S, b, q) then
			local d = dlug(q.x - b.x, q.z - b.z)
			if d < r + A.r + L.promien(D, q.forma) then
				d = math.max(0.1, d)
				L.ran(S, b, q, L.obrazenia(D, b) * A.x, zd, A.typ, (q.x - b.x) / d, (q.z - b.z) / d, A.odrzut, A.przewrot_s)
			end
		end
	end
	if A.typ == "meteor" and b.slot > 0 then
		for _, i in kulkiW(S, b.x, b.z, r + A.r, 99) do
			zjedzKulke(S, b, i, zd)
		end
	end
	table.insert(zd, { t = "ladowanie", id = b.id, x = b.x, z = b.z, r = r + A.r, typ = A.typ })
end

-- kanał oddechu: co tik_s stożek przed pyskiem (kierunek = kierunek ruchu), kulki w stożku zjedzone; inferno pali ziemię
local function krokKanalu(S, b, zd)
	local D = S.D
	local K = b.kanal
	if S.czas >= K.do_ then
		b.kanal = nil
		return
	end
	if S.czas < K.tik then
		return
	end
	local A = K.A
	K.tik += A.tik_s
	local rb = L.promien(D, b.forma)
	local cosK = math.cos(math.rad(A.kat_st / 2))
	local sila = L.obrazenia(D, b)
	for _, q in S.byty do
		if L.mozeRanic(S, b, q) and wStozku(b, q.x, q.z, rb + A.zasieg + zasiegDo(D, q), cosK) then
			local d = math.max(0.1, dlug(q.x - b.x, q.z - b.z))
			L.ran(S, b, q, sila * A.x, zd, "ogien", (q.x - b.x) / d, (q.z - b.z) / d, 3, nil)
		end
	end
	if b.slot > 0 then
		for i, p in D.kulkiPoz do
			if S.kulki[i] == 0 and wStozku(b, p[1], p[2], rb + A.zasieg, cosK) then
				zjedzKulke(S, b, i, zd)
			end
		end
	end
	if A.plama_r and S.czas >= K.plama then
		K.plama = S.czas + 0.6
		local kx, kz = math.sin(b.kier), math.cos(b.kier)
		local x, z = b.x + kx * (rb + A.zasieg * 0.65), b.z + kz * (rb + A.zasieg * 0.65)
		table.insert(S.plamy, { w = b.id, x = x, z = z, r = A.plama_r, do_ = S.czas + A.plama_s, nast = S.czas, co = A.plama_co_s, ile = sila * A.plama_x })
		table.insert(zd, { t = "plama", id = b.id, x = x, z = z, r = A.plama_r, czas = A.plama_s })
	end
end

-- pociski (EMBER SPIT): lecą prosto, trafiają pierwszego na drodze, gasną na skale / drzewie albo po zasięgu
local function krokPociskow(S, dt: number, zd)
	local D = S.D
	local zost = {}
	for _, p in S.pociski do
		local w = L.bytPoId(S, p.w)
		local dx, dz = p.kx * p.v * dt, p.kz * p.v * dt
		local traf, ts = nil, math.huge
		if w then
			for _, q in S.byty do
				if L.mozeRanic(S, w, q, true) then
					-- odległość od odcinka lotu w tym kroku
					local qx, qz = q.x - p.x, q.z - p.z
					local t = math.clamp((qx * dx + qz * dz) / math.max(1e-6, dx * dx + dz * dz), 0, 1)
					local ex, ez = qx - dx * t, qz - dz * t
					if dlug(ex, ez) < p.r + L.promien(D, q.forma) * (if q.boss then 1 else 0.8) and t < ts then
						traf, ts = q, t
					end
				end
			end
		end
		if traf and w then
			table.insert(zd, { t = "pocisk_koniec", n = p.n, x = p.x + dx * ts, z = p.z + dz * ts, trafil = true })
			L.ran(S, w, traf, p.ile, zd, "zar", p.kx, p.kz, p.odrzut, nil, true)
		else
			p.x += dx
			p.z += dz
			local kamien = false
			for _, o in D.przeszkody do
				if o.typ ~= "staw" and dlug(p.x - o.x, p.z - o.z) < o.r then
					kamien = true
				end
			end
			if kamien or S.czas >= p.do_ or not w then
				table.insert(zd, { t = "pocisk_koniec", n = p.n, x = p.x, z = p.z, trafil = false })
			else
				table.insert(zost, p)
			end
		end
	end
	S.pociski = zost
end

-- płonąca ziemia (INFERNO): co co_s rani stojących w środku (poza właścicielem)
local function krokPlam(S, zd)
	local D = S.D
	if #S.plamy == 0 then
		return
	end
	local zost = {}
	for _, p in S.plamy do
		if S.czas < p.do_ then
			table.insert(zost, p)
			local w = L.bytPoId(S, p.w)
			if w and S.czas >= p.nast then
				p.nast = S.czas + p.co
				for _, q in S.byty do
					if L.mozeRanic(S, w, q, true) and dlug(q.x - p.x, q.z - p.z) < p.r + L.promien(D, q.forma) * 0.5 then
						L.ran(S, w, q, p.ile, zd, "plama")
					end
				end
			end
		end
	end
	S.plamy = zost
end

-- bot: zdolność swojego stadium przy celu (te same zasady i zamach co u gracza; bez szybowania)
local function botZdolnosc(S, b, q, d: number, zd)
	local D = S.D
	if b.zamach or b.kanal or S.los() > (D.boty.zdolnosci_szansa or 0.45) then
		return
	end
	local rb, rq = L.promien(D, b.forma), L.promien(D, q.forma)
	local A = L.zdolnoscFormy(D, "ogien", b.forma)
	if A and S.czas >= (b.gotowy.ogien or 0) and d > rb + 1 and d < rb + A.zasieg * 0.75 + rq * 0.5 then
		b.kier = math.atan2(q.x - b.x, q.z - b.z)
		L.zdolnosc(S, b, "ogien", zd)
		return
	end
	local M = L.zdolnoscFormy(D, "moc", b.forma)
	if M and S.czas >= (b.gotowy.moc or 0) then
		if (M.typ == "ogon" and d < rb + M.r + rq * 0.5) or (M.typ == "ryk" and d < rb + M.r * 0.6)
			or (M.typ == "meteor" and d > rb + 6 and d < M.d + rb) then
			b.kier = math.atan2(q.x - b.x, q.z - b.z)
			L.zdolnosc(S, b, "moc", zd)
		end
	end
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
	b.zamach, b.kanal = nil, nil
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
function L.mysl(S, b, zd)
	local D = S.D
	local B = D.boty
	zd = zd or {}
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
	-- odwet (walka1): kto mnie ranił, a jest najwyżej o stadium większy — walczę z nim zamiast uciekać
	local nap = if b.napastnikDo > S.czas then L.bytPoId(S, b.napastnik) else nil
	if nap and nap.martwyDo == nil and nap.forma <= b.forma + 1 and bezbronny(S, nap) and not (nap.slot > 0 and nap.laskaDo > S.czas) then
		ofiara, dof = nap, dlug(nap.x - b.x, nap.z - b.z)
		if zagr == nap or (zagr and zagr.forma <= b.forma + 1) then
			zagr = nil
		end
	end
	-- ROAR: uciekam przed tym, kto ryknął
	if b.uciekaDo > S.czas then
		local u = L.bytPoId(S, b.uciekaOd)
		if u and u.martwyDo == nil then
			zagr, dz = u, dlug(u.x - b.x, u.z - b.z)
			ofiara = nil
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
		elseif S.czas - b.celOd > B.goni_maks_s and ofiara.id ~= b.napastnik then
			b.odpuszcza, b.odpuszczaDo = ofiara.id, S.czas + B.odpuszcza_s
			b.cel = 0
		end
		local d = math.max(0.1, dof)
		-- w zasięgu gryzienia: krąży przy celu (nie wchodzi w niego), dalej — goni
		local styk = r + L.promien(D, ofiara.forma) + 0.5
		if dof < styk then
			b.wx, b.wz = (ofiara.x - b.x) / d * 0.3, (ofiara.z - b.z) / d * 0.3
		else
			b.wx, b.wz = (ofiara.x - b.x) / d, (ofiara.z - b.z) / d
		end
		if dof < r + L.promien(D, ofiara.forma) + 6 and dof > styk + 2 and S.los() < B.zryw_szansa then
			L.zryw(S, b)
		end
		botZdolnosc(S, b, ofiara, dof, zd)
	else
		b.cel = 0
		local best, bd = nil, 34
		if b.forma <= B.kulki_do then
			for i, p in D.kulkiPoz do
				if S.kulki[i] == 0 and not L.naWyspie(D, p[1], p[2]) then
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
	b.lancuch, b.zamach, b.kanal = 0, nil, nil
	if not b.boss then
		b.hpMaks = L.hpMaks(D, b)
		b.hp = b.hpMaks
	end
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
	local W = D.walka
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
	-- Olbrzym, który już nie jest na ostatnim stadium (zjedzony, próba), traci koronę
	if S.olbrzym ~= 0 then
		local o = L.bytPoId(S, S.olbrzym)
		if not o or o.forma < #D.formy then
			S.olbrzym = 0
		end
	end
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
		-- życie: maksimum z formy (ewolucja, śmierć, próby), regeneracja bez ran
		if not b.boss then
			local hm = L.hpMaks(D, b)
			if b.hpMaks ~= hm then
				b.hp = math.max(1, b.hp / math.max(1, b.hpMaks) * hm)
				b.hpMaks = hm
			end
			if b.martwyDo == nil and b.hp < b.hpMaks and S.czas - b.ostRana > W.regen_po_s then
				b.hp = math.min(b.hpMaks, b.hp + b.hpMaks * W.regen_na_s * dt)
			end
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
				b.gotowy = { ogien = 0, moc = 0 }
				b.hpMaks = L.hpMaks(D, b)
				b.hp = b.hpMaks
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
				-- nowa wersja linii FIRE / POWER na tym stadium
				local nowe = {}
				for _, linia in { "ogien", "moc" } do
					local A = L.zdolnoscFormy(D, linia, b.forma)
					if A and A.od == b.forma then
						table.insert(nowe, A.id)
					end
				end
				table.insert(zd, { t = "ewolucja", id = b.id, s = b.slot, forma = b.forma, nowa = nowa, wariant = b.kokonWariant, najlepszy = najlepszy,
					zd = nowe })
				if nowa and b.forma == D.las.od_formy and b.slot > 0 then
					table.insert(zd, { t = "las_otwarty", id = b.id, s = b.slot })
				end
				if b.forma == #D.formy and b.slot > 0 then
					S.olbrzym = b.id
					table.insert(zd, { t = "olbrzym", id = b.id, s = b.slot })
				end
			end
		elseif b.skok then
			-- szybowanie / skok meteoru: lot nad wszystkim (nietykalny), lądowanie w kręgu
			local k = b.skok
			local f = math.clamp((S.czas - k.t0) / (k.t1 - k.t0), 0, 1)
			b.x = k.x0 + (k.x1 - k.x0) * f
			b.z = k.z0 + (k.z1 - k.z0) * f
			b.ostRaport = S.czas
			if f >= 1 then
				b.skok = nil
				b.x, b.z = L.ogranicz(D, b.x, b.z, r, L.maska(D, b))
				b.vx, b.vz = 0, 0
				ladowanie(S, b, k, zd)
			end
		elseif b.ogluszonyDo > S.czas then
			-- ogłuszony / przewrócony: leci z odrzutem i hamuje (zamach bossa przerwany)
			b.bossZamach = nil
			b.vx, b.vz = b.vx * 0.82, b.vz * 0.82
			b.x += b.vx * dt
			b.z += b.vz * dt
			b.x, b.z = L.ogranicz(D, b.x, b.z, r, L.maska(D, b))
			b.ostRaport = S.czas
		else
			if b.zamach and S.czas >= b.zamach.t1 then
				local A = b.zamach.A
				b.zamach = nil
				wykonaj(S, b, A, zd)
			end
			if b.boss then
				if S.czas >= b.myslDo then
					L.myslBossa(S, b)
				end
				if S.czas - b.ostRana > D.boss.regen_po_s and b.hp < b.hpMaks then
					b.hp = math.min(b.hpMaks, b.hp + b.hpMaks * D.boss.regen_na_s * dt)
				end
			elseif b.slot == 0 and S.czas >= b.myslDo then
				L.mysl(S, b, zd)
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
			if b.kanal then
				krokKanalu(S, b, zd)
			end
			if b.boss then
				-- boss gryzie: rana z życia, odrzut i krótkie ogłuszenie (zero życia → zjada jak każdy)
				local q = b.cel ~= 0 and L.bytPoId(S, b.cel)
				local zasB = r + D.boss.zasieg + (if q then L.promien(D, q.forma) else 0)
				-- golem: zamach widoczny dla gracza (klip „zamach”), cios w chwili zdarzenia klipu, jeśli cel nadal w zasięgu
				if (D.boss.zamach_s or 0) > 0 and not b.bossZamach and q and S.czas >= b.gryzGotowy and L.mozeRanic(S, b, q)
					and dlug(q.x - b.x, q.z - b.z) < zasB then
					b.bossZamach = S.czas + D.boss.zamach_s
					b.gryzGotowy = S.czas + D.boss.zamach_s + D.boss.przerwa_s
					table.insert(zd, { t = "boss_zamach", id = b.id, cel = q.id, czas = D.boss.zamach_s })
				end
				local gotowyCios = if (D.boss.zamach_s or 0) > 0 then (b.bossZamach ~= nil and S.czas >= b.bossZamach) else S.czas >= b.gryzGotowy
				if gotowyCios then
					b.bossZamach = nil
				end
				if q and gotowyCios and L.mozeRanic(S, b, q)
					and dlug(q.x - b.x, q.z - b.z) < zasB + (if (D.boss.zamach_s or 0) > 0 then 2 else 0) then
					if (D.boss.zamach_s or 0) <= 0 then
						b.gryzGotowy = S.czas + D.boss.przerwa_s
					end
					b.gryzDo = S.czas + D.gryzienie.slad_s
					local d = math.max(0.1, dlug(q.x - b.x, q.z - b.z))
					local nx, nz = (q.x - b.x) / d, (q.z - b.z) / d
					q.x, q.z = L.ogranicz(D, q.x + nx * 1.5, q.z + nz * 1.5, L.promien(D, q.forma), L.maska(D, q))
					table.insert(zd, { t = "boss_gryz", id = b.id, cel = q.id, s = q.slot, x = q.x, z = q.z })
					L.ran(S, b, q, D.boss.stopnie_gryz[S.bossStopien or 1], zd, "boss", nx, nz, D.boss.odrzut, D.boss.ogluszenie_s)
				end
			elseif b.slot == 0 and S.czas >= b.gryzGotowy and not b.zamach and not b.kanal then
				-- bot: BITE łańcuchem, gdy cel w zasięgu (te same zasady co u gracza)
				if celGryzu(S, b, L.zasiegGryzu(D, b)) then
					L.gryz(S, b, zd)
				end
			end
		end
	end
	-- odbicia (walka1: bez połykania dotykiem — zjada się tylko przez życie); mniejszy odlatuje mocniej
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
	krokPociskow(S, dt, zd)
	krokPlam(S, zd)
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
