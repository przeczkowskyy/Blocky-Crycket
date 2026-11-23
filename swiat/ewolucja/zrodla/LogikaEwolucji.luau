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
local function stawkaLinii(D, maxForma: number, trofea, warianty): number
	local G = D.legowisko
	local s = 0
	for f = 1, maxForma do
		s += D.formy[f].trofeum * G.poziomy_x[(trofea and trofea[f]) or 1] * L.wariantX(D, warianty and warianty[f])
	end
	return s
end

-- odrodzenie1: stały mnożnik wzrostu i złota legowiska za każde odrodzenie (× x, najwyżej maks_x)
function L.mnoznikOdr(D, b): number
	local O = D.odrodzenie
	if not O then
		return 1
	end
	return math.min(O.maks_x, O.x ^ (b.odrodzenia or 0))
end

function L.stawkaB(D, b): number
	local G = D.legowisko
	local s = stawkaLinii(D, b.maxForma, b.trofea, b.warianty)
	-- trofea poprzednich linii smoków zostają w legowisku i dalej zarabiają
	if b.linie then
		for _, z in b.linie do
			s += stawkaLinii(D, z.maxForma, z.trofea, z.warianty)
		end
	end
	for t = 1, math.min(b.bossTrofea or 0, #G.boss_trofea) do
		s += G.boss_trofea[t]
	end
	return s * L.mnoznikOdr(D, b) * L.przepustkaX(D, b, "zloto_x")
end

------------------------------------------------------------------ odczucie1: sklep (kod gotowy, flaga wyłączona)
-- mnożnik z posiadanych przepustek (pole „wzrost_x” albo „zloto_x” definicji przepustki)
function L.przepustkaX(D, b, pole: string): number
	local x = 1
	if D.sklep and b.przepustki then
		for _, Pp in D.sklep.przepustki do
			if b.przepustki[Pp.id] and Pp[pole] then
				x *= Pp[pole]
			end
		end
	end
	return x
end

-- produkt po numerze Roblox (0 = ukryty, nigdy nie pasuje)
function L.produktPoId(D, productId: any)
	if not D.sklep or type(productId) ~= "number" or productId <= 0 then
		return nil
	end
	for _, Pr in D.sklep.produkty do
		if Pr.product_id == productId then
			return Pr
		end
	end
	return nil
end

-- nagroda produktu; zwraca zapis do cofnięcia (gdy zapis gracza się nie uda)
function L.przyznajProdukt(D, b, Pr)
	local cofka = { zloto = Pr.zloto or 0, boostS = Pr.boost_s or 0 }
	b.zloto += cofka.zloto
	b.boostS = (b.boostS or 0) + cofka.boostS
	return cofka
end

function L.cofnijProdukt(b, cofka)
	b.zloto -= cofka.zloto
	b.boostS = math.max(0, (b.boostS or 0) - cofka.boostS)
end

-- paragony (PurchaseId) w zapisie gracza: idempotencja ProcessReceipt
function L.paragonZnany(b, pid: string): boolean
	for _, p in b.paragony or {} do
		if p == pid then
			return true
		end
	end
	return false
end

function L.zapamietajParagon(D, b, pid: string)
	b.paragony = b.paragony or {}
	table.insert(b.paragony, pid)
	local maks = (D.sklep and D.sklep.paragony_max) or 200
	while #b.paragony > maks do
		for i = 1, #b.paragony - 1 do
			b.paragony[i] = b.paragony[i + 1]
		end
		b.paragony[#b.paragony] = nil
	end
end

function L.zapomnijParagon(b, pid: string)
	local nowe = {}
	for _, p in b.paragony or {} do
		if p ~= pid then
			table.insert(nowe, p)
		end
	end
	b.paragony = nowe
end

-- czy pokazać przycisk sklepu: flaga i co najmniej jeden numer ≠ 0
function L.sklepWidoczny(D): boolean
	local S = D.sklep
	if not (S and S.wlaczony) then
		return false
	end
	for _, Pp in S.przepustki do
		if (Pp.pass_id or 0) > 0 then
			return true
		end
	end
	for _, Pr in S.produkty do
		if (Pr.product_id or 0) > 0 then
			return true
		end
	end
	return false
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
	-- świat: krąg skał legowiska stoi na promieniu ok. 13,5 (skały r 2,3) — boty trzymają się za nim
	-- (+8: wejście legowiska i kulki startowe przed nim zostają dla graczy, boty nie tarasują wyjścia)
	local poza = D.legowisko.r + (if D.swiat then 8 else 0)
	for _, p in D.legowiska do
		local d = dlug(x - p[1], z - p[2])
		local min = poza + r * 0.7
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
	return b.martwyDo == nil and b.kokonDo == nil and b.skok == nil and b.odrDo == nil
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

------------------------------------------------------------------ mapa2a: mapa v2 na płaskiej ziemi (swiat_mapa2.py)
-- obrys: koło {k = "k", x, z, r} albo prostokąt {k = "p" | "pas", x, z, o, hx, hz}; lokalne z = dx·sin o + dz·cos o
local function lokXZ(dx: number, dz: number, o: number): (number, number)
	local a = math.rad(o)
	local c, s = math.cos(a), math.sin(a)
	return dx * c - dz * s, dx * s + dz * c
end
local function swXZ(lx: number, lz: number, o: number): (number, number)
	local a = math.rad(o)
	local c, s = math.cos(a), math.sin(a)
	return lx * c + lz * s, -lx * s + lz * c
end
L.lokXZ = lokXZ

function L.wObrysie(f, x: number, z: number, m: number?): boolean
	local mm = m or 0
	if f.k == "k" then
		return dlug(x - f.x, z - f.z) <= f.r + mm
	end
	local lx, lz = lokXZ(x - f.x, z - f.z, f.o)
	return math.abs(lx) <= f.hx + mm and math.abs(lz) <= f.hz + mm
end

-- wypchnięcie z prostokąta powiększonego o m — wzdłuż osi najmniejszego zagłębienia
local function wypchnijProst(f, x: number, z: number, m: number): (number, number)
	local lx, lz = lokXZ(x - f.x, z - f.z, f.o)
	local px, pz = f.hx + m - math.abs(lx), f.hz + m - math.abs(lz)
	if px <= 0 or pz <= 0 then
		return x, z
	end
	if px < pz then
		lx = (if lx >= 0 then 1 else -1) * (f.hx + m)
	else
		lz = (if lz >= 0 then 1 else -1) * (f.hz + m)
	end
	local dx, dz = swXZ(lx, lz, f.o)
	return f.x + dx, f.z + dz
end

local function wypchnijKolo(cx: number, cz: number, rr: number, x: number, z: number): (number, number)
	local d = dlug(x - cx, z - cz)
	if d < rr and d > 0.01 then
		return cx + (x - cx) / d * rr, cz + (z - cz) / d * rr
	end
	return x, z
end

-- obszar gry: kształt pomniejszony o 0,6 r (pas — tylko w poprzek, żeby przejścia łączyły się ze strefami)
local function wObszarze(o, x: number, z: number, r: number): boolean
	if o.k == "k" then
		return dlug(x - o.x, z - o.z) <= o.r - r * 0.6
	end
	local lx, lz = lokXZ(x - o.x, z - o.z, o.o)
	local hz = if o.k == "pas" then o.hz else o.hz - r * 0.6
	return math.abs(lx) <= o.hx - r * 0.6 and math.abs(lz) <= hz
end

local function rzutNaObszar(o, x: number, z: number, r: number): (number, number, number)
	if o.k == "k" then
		local R = o.r - r * 0.6
		if R <= 0 then
			return x, z, math.huge
		end
		local d = dlug(x - o.x, z - o.z)
		if d <= R or d < 0.01 then
			return x, z, 0
		end
		return o.x + (x - o.x) / d * R, o.z + (z - o.z) / d * R, d - R
	end
	local hx = o.hx - r * 0.6
	local hz = if o.k == "pas" then o.hz else o.hz - r * 0.6
	if hx <= 0 or hz <= 0 then
		return x, z, math.huge
	end
	local lx, lz = lokXZ(x - o.x, z - o.z, o.o)
	local cx, cz = math.clamp(lx, -hx, hx), math.clamp(lz, -hz, hz)
	local dx, dz = swXZ(cx, cz, o.o)
	return o.x + dx, o.z + dz, dlug(lx - cx, lz - cz)
end

local function maskaPasuje(m: number, o): boolean
	return (m ~= 2 and o.maska == 1) or (m >= 2 and o.maska == 2)
end

-- głębia (jezioro): środek smoka nie wejdzie w głęboką wodę poza brodem i wysepką — najbliższe dozwolone miejsce
local function zGlebi(g, x: number, z: number, r: number): (number, number)
	local G = g.obrys
	local R = G.r - r * 0.3
	local d = dlug(x - G.x, z - G.z)
	if d >= R then
		return x, z
	end
	for _, f in g.wolne do
		if L.wObrysie(f, x, z) then
			return x, z
		end
	end
	local dd0 = math.max(0.01, d)
	local bx, bz, bd = G.x + (x - G.x) / dd0 * (R + 0.01), G.z + (z - G.z) / dd0 * (R + 0.01), R - d
	for _, f in g.wolne do
		local px, pz
		if f.k == "k" then
			local df = math.max(0.01, dlug(x - f.x, z - f.z))
			px, pz = f.x + (x - f.x) / df * f.r * 0.99, f.z + (z - f.z) / df * f.r * 0.99
		else
			local lx, lz = lokXZ(x - f.x, z - f.z, f.o)
			local dx, dz = swXZ(math.clamp(lx, -f.hx * 0.99, f.hx * 0.99), math.clamp(lz, -f.hz * 0.99, f.hz * 0.99), f.o)
			px, pz = f.x + dx, f.z + dz
		end
		local dd = dlug(px - x, pz - z)
		if dd < bd then
			bx, bz, bd = px, pz, dd
		end
	end
	return bx, bz
end

-- prędkość w płytkiej wodzie (rzeka, bród jeziora) × woda_x; mosty i brody rzeki szybkie
function L.wodaX(D, x: number, z: number): number
	local M2 = D.mapa2
	if not M2 then
		return 1
	end
	for _, f in M2.suche do
		if L.wObrysie(f, x, z) then
			return 1
		end
	end
	for _, f in M2.woda do
		if L.wObrysie(f, x, z) then
			return M2.woda_x
		end
	end
	return 1
end

-- wysokość podestu pod punktem (most, wysepka) — tylko obraz u klienta (etap A: ruch płaski)
function L.podestY(D, x: number, z: number): number
	local M2 = D.mapa2
	local y = 0
	if M2 then
		for _, f in M2.podesty do
			if f.y > y and L.wObrysie(f, x, z) then
				y = f.y
			end
		end
	end
	return y
end

-- ograniczenia ruchu: suma dozwolonych kół i przeszkody (wspólne dla serwera i przewidywania u klienta)
function L.ogranicz(D, x: number, z: number, r: number, maska: number?): (number, number)
	local m = maska or 1
	local M2 = D.mapa2
	if M2 then
		local ok = false
		for _, o in M2.obszar do
			if maskaPasuje(m, o) and wObszarze(o, x, z, r) then
				ok = true
				break
			end
		end
		if not ok then
			local bx, bz, bd = x, z, math.huge
			for _, o in M2.obszar do
				if maskaPasuje(m, o) then
					local px, pz, d = rzutNaObszar(o, x, z, r)
					if d < bd then
						bx, bz, bd = px, pz, d
					end
				end
			end
			x, z = bx, bz
		end
		return L.przeszkodyV2(D, x, z, r)
	end
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
	-- przeszkody: tylko z komórki siatki (świat ma ich setki); zapas siatki 12 st. ≥ 0,7 × największy promień
	local G = D.przSiatka
	local lista = nil
	if G then
		local kl = tostring((math.floor(x / G.krok) + 100) * 1000 + (math.floor(z / G.krok) + 100))
		lista = G.komorki[kl]
	end
	if not G or lista then
		for _, i in lista or D.przeszkody do
			local s = if lista then D.przeszkody[i] else i
			if s.k == "p" then
				x, z = wypchnijProst(s, x, z, r * 0.7)
			else
				local ds = dlug(x - s.x, z - s.z)
				local min = s.r + r * 0.7
				if ds < min and ds > 0.01 then
					x = s.x + (x - s.x) / ds * min
					z = s.z + (z - s.z) / ds * min
				end
			end
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

-- mapa v2: przeszkody (siatka), rzeczy do rozbicia (dopóki stoją), bramy rozmiaru (dla większych), głębia, fosa SKY NEST
function L.przeszkodyV2(D, x: number, z: number, r: number): (number, number)
	local M2 = D.mapa2
	local G = D.przSiatka
	local lista = G and G.komorki[tostring((math.floor(x / G.krok) + 100) * 1000 + (math.floor(z / G.krok) + 100))]
	for _, i in lista or {} do
		local s = D.przeszkody[i]
		if s.k == "p" then
			x, z = wypchnijProst(s, x, z, r * 0.7)
		else
			x, z = wypchnijKolo(s.x, s.z, s.r + r * 0.7, x, z)
		end
	end
	for _, q in M2.lamliwe do
		if not M2.rozbite[q.id] and dlug(x - q.x, z - q.z) < q.r + r + 14 then
			for _, c in q.kola do
				x, z = wypchnijKolo(c[1], c[2], c[3] + r * 0.7, x, z)
			end
			for _, f in q.prost do
				x, z = wypchnijProst(f, x, z, r * 0.7)
			end
		end
	end
	for _, b in M2.bramy do
		if r > b.r_maks and dlug(x - b.x, z - b.z) < b.hx + b.hz + r + 2 then
			x, z = wypchnijProst(b, x, z, r * 0.7)
		end
	end
	for _, g in M2.glebia do
		x, z = zGlebi(g, x, z, r)
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

-- kryjówki (mapa v2): smok mieszczący się w kępie (r ≤ r_maks), nie odkryty atakiem — boty dalej niż 8 st. go gubią
function L.ukryty(S, q): boolean
	local M2 = S.D.mapa2
	if not M2 or q.boss or (q.odkrytyDo or 0) > S.czas then
		return false
	end
	if q.ukrytyT == S.czas then
		return q.ukrytyW
	end
	local r = L.promien(S.D, q.forma)
	local w = false
	for _, k in M2.kryjowki do
		if r <= k.r_maks and dlug(q.x - k.x, q.z - k.z) <= k.r then
			w = true
			break
		end
	end
	q.ukrytyT, q.ukrytyW = S.czas, w
	return w
end

-- rzeczy do rozbicia (mapa v2): od stadium q.od; BITE, TAIL ×2, METEOR ×2, ROAR; zero → rozsypka, złoto, odrost po odrost_s
function L.uderzLamliwe(S, b, zas: number, ile: number, jak: string, zd): boolean
	local D = S.D
	local M2 = D.mapa2
	if not M2 or b.slot == 0 then
		return false
	end
	local trafil = false
	for _, q in M2.lamliwe do
		if not M2.rozbite[q.id] and dlug(b.x - q.x, b.z - q.z) < zas + q.r then
			trafil = true
			if b.forma < q.od then
				if (b.lamPodpDo or -1) < S.czas then
					b.lamPodpDo = S.czas + 2
					table.insert(zd, { t = "lamliwa_mala", id = b.id, s = b.slot, l = q.id, od = q.od, x = q.x, z = q.z })
				end
			else
				S.lamHp = S.lamHp or {}
				local rana = math.max(1, math.floor(ile * (M2.lamliwa_x[jak] or 1) + 0.5))
				local hp = (S.lamHp[q.id] or q.hp) - rana
				if hp <= 0 then
					M2.rozbite[q.id] = S.czas + q.odrost_s
					S.lamHp[q.id] = nil
					b.zloto += q.zloto
					table.insert(zd, { t = "lamliwa_rozbita", id = b.id, s = b.slot, l = q.id, zloto = q.zloto, x = q.x, z = q.z, ile = rana })
				else
					S.lamHp[q.id] = hp
					table.insert(zd, { t = "lamliwa_rana", id = b.id, s = b.slot, l = q.id, ile = rana, hp = hp / q.hp, x = q.x, z = q.z })
				end
			end
		end
	end
	return trafil
end

-- odrost rzeczy do rozbicia (czas symulacji); smok w środku zostaje wypchnięty przy następnym ruchu
function L.krokLamliwych(S, zd)
	local M2 = S.D.mapa2
	if not M2 then
		return
	end
	for _, q in M2.lamliwe do
		local do_ = M2.rozbite[q.id]
		if type(do_) == "number" and S.czas >= do_ then
			M2.rozbite[q.id] = nil
			table.insert(zd, { t = "lamliwa_odrost", l = q.id, x = q.x, z = q.z })
		end
	end
end

-- sekrety dnia (mapa v2): dotknięcie = złoto raz na gracza na dzień UTC
function L.krokSekretow(S, b, zd)
	local D = S.D
	local M2 = D.mapa2
	if not (M2 and S.zegar) or b.martwyDo ~= nil then
		return
	end
	local dz = L.dzienUTC(S.zegar)
	if not b.sekrety or b.sekrety.dzien ~= dz then
		b.sekrety = { dzien = dz, lista = {} }
	end
	local r = L.promien(D, b.forma) + M2.sekret_r
	for _, s in M2.sekrety do
		if dlug(b.x - s.x, b.z - s.z) < r then
			local byl = false
			for _, id in b.sekrety.lista do
				if id == s.id then
					byl = true
				end
			end
			if not byl then
				table.insert(b.sekrety.lista, s.id)
				b.zloto += s.zloto
				b.sekretPodpDo = S.czas + 8 -- bez „już znalezione” zaraz po znalezieniu
				table.insert(zd, { t = "sekret", id = b.id, s = b.slot, sid = s.id, zloto = s.zloto, x = s.x, z = s.z })
			elseif (b.sekretPodpDo or -1) < S.czas then
				b.sekretPodpDo = S.czas + 8
				table.insert(zd, { t = "sekret_byl", id = b.id, s = b.slot, sid = s.id })
			end
		end
	end
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
		elseif not gracz and strefa ~= 2 and D.mapa2 and D.mapa2.punktyBotow then
			-- mapa v2: punkt z listy (łąka i nowe strefy), taki, w którym ta forma się mieści
			local PB = D.mapa2.punktyBotow
			local rf = D.formy[forma].r
			for _ = 1, 16 do
				local p = PB[1 + math.floor(S.los() * #PB)]
				if p[3] >= rf then
					x, z = p[1], p[2]
					break
				end
			end
			if not x then
				local a = S.los() * 2 * math.pi
				local r = math.sqrt(S.los()) * (D.pole.r - 14)
				x, z = math.sin(a) * r, math.cos(a) * r
			end
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
		if not gracz then
			-- świat: poza legowiskami i jeszcze raz przeszkody (skały kręgu legowiska stoją blisko siebie)
			x, z = L.pozaLegowiskami(D, x, z, D.formy[forma].r)
			x, z = L.ogranicz(D, x, z, D.formy[forma].r, strefa or 1)
			x, z = L.ogranicz(D, x, z, D.formy[forma].r, strefa or 1)
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
	-- retencja1: boty w kolorach linii smoków (po kolei z numeru bytu, bez losowania), gracz zaczyna linią 1
	b.linia = if slot == 0 and D.odrodzenie then (b.id % #D.odrodzenie.linie) + 1 else 1
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
		local E = S.wyd
		if E and E.rampDo then
			-- rampage: pula skrzyni × pula_x po równo dla każdego, kto trafił (także jeden gracz)
			local trafili = {}
			for _, q in S.byty do
				if q.slot > 0 and (boss.rany[tostring(q.slot)] or 0) > 0 then
					table.insert(trafili, q)
				end
			end
			local dzial = math.floor(skrzynia * D.wydarzenia.rampage.pula_x / math.max(1, #trafili))
			for _, q in trafili do
				q.zloto += dzial
			end
			table.insert(zd, { t = "rampage_skrzynia", ile = #trafili, dzial = dzial, x = boss.x, z = boss.z })
			E.rampDo = S.czas
			skrzynia = 0
		end
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
	return b.martwyDo ~= nil or b.kokonDo ~= nil or b.skok ~= nil or b.odrDo ~= nil or b.ogluszonyDo > S.czas
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
	local deszcz = L.deszczNa(S, i)
	S.kulki[i] = S.czas + (if deszcz then D.wydarzenia.deszcz.powrot_s elseif typ >= 2 then D.jedzenie.powrot_duza_s else D.jedzenie.powrot_mala_s)
	if b.slot > 0 then
		L.dodajWzrost(S, b, (if typ == 3 then D.jedzenie.wielka elseif typ == 2 then D.jedzenie.duza else D.jedzenie.mala) * L.apetyt(D, b)
			* (if deszcz then D.wydarzenia.deszcz.wzrost_x else 1))
		if deszcz then
			b.zloto += D.wydarzenia.deszcz.zloto
		end
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
	if b.slot > 0 then
		ile *= L.mnoznikOdr(D, b) * (if (b.boostS or 0) > 0 and D.seria then D.seria.boost_x else 1) * L.przepustkaX(D, b, "wzrost_x")
	end
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
		kr = kryt, jak = jak, pw = przewrot })
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
	b.odkrytyDo = S.czas + (if D.mapa2 then D.mapa2.odkrycie_s else 0)
	local lam = q == nil and L.uderzLamliwe(S, b, L.promien(D, b.forma) + zas, L.obrazenia(D, b) * W.lancuch_x[k], "gryz", zd)
	table.insert(zd, { t = "gryz", id = b.id, x = b.x, z = b.z, k = k, trafil = q ~= nil or lam })
	if q then
		local d = math.max(0.1, dlug(q.x - b.x, q.z - b.z))
		b.kier = math.atan2(q.x - b.x, q.z - b.z)
		L.ran(S, b, q, L.obrazenia(D, b) * W.lancuch_x[k], zd, "gryz", (q.x - b.x) / d, (q.z - b.z) / d,
			if k == 3 then W.odrzut else W.odrzut_maly, if k == 3 then W.przewrot_s else nil, true)
	elseif b.slot > 0 and not lam then
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
	b.odkrytyDo = S.czas + zs + (if D.mapa2 then D.mapa2.odkrycie_s else 0)
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
		L.uderzLamliwe(S, b, rb + A.r, sila * A.x, "ogon", zd)
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
		L.uderzLamliwe(S, b, rb + A.r, sila * A.x, "ryk", zd)
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
	L.uderzLamliwe(S, b, r + A.r, L.obrazenia(D, b) * A.x, A.typ, zd)
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
				if o.typ ~= "staw" and (if o.k == "p" then L.wObrysie(o, p.x, p.z) else dlug(p.x - o.x, p.z - o.z) < o.r) then
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
				if D.mapa2 and L.ukryty(S, q) and d - r - rq > D.mapa2.ukrycie_bot_st then
					widzi = -999 -- mapa v2: ukryty w wysokiej trawie / paproci
				end
				if d < widzi + r and d < dof then
					ofiara, dof = q, d
				end
			end
		end
	end
	-- odwet (walka1): kto mnie ranił, a jest najwyżej o stadium większy — walczę z nim zamiast uciekać
	local nap = if b.napastnikDo > S.czas then L.bytPoId(S, b.napastnik) else nil
	if nap and D.mapa2 and L.ukryty(S, nap) and dlug(nap.x - b.x, nap.z - b.z) - r - L.promien(D, nap.forma) > D.mapa2.ukrycie_bot_st then
		nap = nil
	end
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
			elseif D.mapa2 then
				-- mapa v2: wokół miejsca odrodzenia (nowe strefy nie pustoszeją)
				if not b.domBX then
					b.domBX, b.domBZ = b.x, b.z
				end
				cx, cz, R = b.domBX, b.domBZ, 45
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
	local szal = S.wyd ~= nil and S.wyd.rampDo ~= nil
	if szal then
		dc = D.boss.widzi * D.wydarzenia.rampage.widzi_x
	end
	for _, q in S.byty do
		if q.slot > 0 and wolny(S, q) and (szal or L.wLesie(D, q.x, q.z)) and not L.wLegowisku(D, q) then
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

------------------------------------------------------------------ owce (swiat1): stadka na łące — pasą się, uciekają, zjedzone dotykiem
function L.dodajOwce(S)
	local D = S.D
	local O = D.swiat and D.swiat.owce
	S.owce = {}
	if not O then
		return S.owce
	end
	for _, st in O.stada do
		for k = 1, O.na_stado do
			local a = k * 2.1
			local x, z = L.ogranicz(D, st[1] + math.sin(a) * 3, st[2] + math.cos(a) * 3, O.r, 1)
			table.insert(S.owce, { i = #S.owce + 1, x = x, z = z, kier = a, wx = 0, wz = 0, domX = st[1], domZ = st[2], martwyDo = nil, myslDo = 0,
				stan = 0 })
		end
	end
	return S.owce
end

local function owcaMysl(S, o)
	local D = S.D
	local O = D.swiat.owce
	o.myslDo = S.czas + O.myslenie_s * (0.7 + S.los() * 0.6)
	local best, bd = nil, O.widzi
	for _, b in S.byty do
		if wolny(S, b) and not b.boss then
			local d = dlug(b.x - o.x, b.z - o.z) - L.promien(D, b.forma)
			if d < bd then
				best, bd = b, d
			end
		end
	end
	if best then
		local d = math.max(0.1, dlug(o.x - best.x, o.z - best.z))
		o.wx, o.wz = (o.x - best.x) / d, (o.z - best.z) / d
		o.stan = 2
	elseif S.los() < 0.45 then
		o.wx, o.wz = 0, 0
		o.stan = 0
	else
		-- spacer przy stadzie
		local a = S.los() * 2 * math.pi
		local dx, dz = o.domX - o.x, o.domZ - o.z
		local dd = math.max(1, dlug(dx, dz))
		o.wx, o.wz = math.sin(a) * 0.7 + dx / dd * math.min(1, dd / 20) * 0.6, math.cos(a) * 0.7 + dz / dd * math.min(1, dd / 20) * 0.6
		local n = math.max(0.01, dlug(o.wx, o.wz))
		o.wx, o.wz = o.wx / n, o.wz / n
		o.stan = 1
	end
end

-- krok owiec: ruch, zjedzenie dotykiem (gracz dowolnego stadium, boty do kulki_do): wzrost i życie jak duża kulka
function L.krokOwiec(S, dt: number, zd)
	local D = S.D
	if not S.owce then
		return
	end
	local O = D.swiat.owce
	for _, o in S.owce do
		if o.martwyDo then
			if S.czas >= o.martwyDo then
				o.martwyDo = nil
				o.x, o.z = L.ogranicz(D, o.domX + (S.los() - 0.5) * 8, o.domZ + (S.los() - 0.5) * 8, O.r, 1)
				o.stan = 0
				table.insert(zd, { t = "owca_wraca", i = o.i, x = o.x, z = o.z })
			end
		else
			if S.czas >= o.myslDo then
				owcaMysl(S, o)
			end
			local v = if o.stan == 2 then O.v_ucieczka elseif o.stan == 1 then O.v else 0
			o.x += o.wx * v * dt
			o.z += o.wz * v * dt
			if o.wx ~= 0 or o.wz ~= 0 then
				o.kier = math.atan2(o.wx, o.wz)
			end
			o.x, o.z = L.ogranicz(D, o.x, o.z, O.r, 1)
			o.x, o.z = L.pozaLegowiskami(D, o.x, o.z, O.r)
			for _, b in S.byty do
				if wolny(S, b) and not b.boss and (b.slot > 0 or b.forma <= D.boty.kulki_do)
					and dlug(b.x - o.x, b.z - o.z) < L.promien(D, b.forma) + O.r + D.jedzenie.zasieg_zbierania then
					o.martwyDo = S.czas + O.powrot_s
					o.stan = 3
					if b.slot > 0 then
						L.dodajWzrost(S, b, O.wzrost * L.apetyt(D, b))
					end
					b.hp = math.min(b.hpMaks, b.hp + b.hpMaks * O.leczy)
					table.insert(zd, { t = "owca", i = o.i, id = b.id, s = b.slot, x = o.x, z = o.z, zysk = O.wzrost })
					break
				end
			end
		end
	end
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
	b.domBX, b.domBZ = nil, nil
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
		if b.odrDo then
			if S.czas >= b.odrDo then
				L.odrodzenieKoniec(S, b, zd)
			end
		elseif b.martwyDo then
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
			local v = L.predkosc(D, b) * mnoznik(S, b) * L.wodaX(D, b.x, b.z)
			local a = math.min(1, D.ruch.przyspieszenie * dt * (if mnoznik(S, b) > 1 then 3 else 1))
			b.vx += (b.wx * v - b.vx) * a
			b.vz += (b.wz * v - b.vz) * a
			b.x += b.vx * dt
			b.z += b.vz * dt
			if b.wx ~= 0 or b.wz ~= 0 then
				b.kier = math.atan2(b.wx, b.wz)
			end
			if b.slot == 0 then
				b.x, b.z = L.pozaLegowiskami(D, b.x, b.z, r)
			end
			b.x, b.z = L.ogranicz(D, b.x, b.z, r, L.maska(D, b))
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
	L.krokOwiec(S, dt, zd)
	krokPlam(S, zd)
	L.krokWydarzen(S, zd)
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
	L.krokZadan(S, dt, zd)
	L.krokLamliwych(S, zd)
	return zd
end

------------------------------------------------------------------ odrodzenie1: odrodzenie, linie smoków, wydarzenia, jajo dnia
-- bajt wariantu w migawce: numer wariantu (0–7) + 8 × (linia − 1)
function L.kodWariantu(nr: number, linia: number): number
	return (nr % 8) + 8 * (math.clamp(linia, 1, 31) - 1)
end

function L.dekodWariantu(bajt: number): (number, number)
	return bajt % 8, bajt // 8 + 1
end

function L.liniaPo(D, linia: number): number
	return linia % #D.odrodzenie.linie + 1
end

function L.mozeOdrodzic(S, b): boolean
	return b.slot > 0 and b.forma >= #S.D.formy and not sterowanyPrzezSerwer(S, b)
end

-- REBIRTH na ANCIENT: ceremonia (nieruchomo, nietykalnie), potem pisklę nowej linii; złoto, ulepszenia i legowisko zostają
function L.odrodzenie(S, b, zd): boolean
	if not L.mozeOdrodzic(S, b) then
		return false
	end
	local D = S.D
	b.odrDo = S.czas + D.odrodzenie.ceremonia_s
	b.zamach, b.kanal = nil, nil
	b.vx, b.vz, b.wx, b.wz = 0, 0, 0, 0
	table.insert(zd, { t = "odr_start", id = b.id, s = b.slot, linia = L.liniaPo(D, b.linia or 1), n = (b.odrodzenia or 0) + 1,
		czas = D.odrodzenie.ceremonia_s, x = math.min(D.odrodzenie.maks_x, D.odrodzenie.x ^ ((b.odrodzenia or 0) + 1)) })
	return true
end

function L.odrodzenieKoniec(S, b, zd)
	local D = S.D
	b.odrDo = nil
	b.linie = b.linie or {}
	local stara = b.linia or 1
	b.linie[stara] = { maxForma = b.maxForma, warianty = b.warianty or {}, trofea = b.trofea or {} }
	local nowa = L.liniaPo(D, stara)
	local z = b.linie[nowa]
	b.linie[nowa] = nil
	b.linia = nowa
	b.maxForma = if z then z.maxForma else 1
	b.warianty = if z then z.warianty else {}
	b.trofea = if z then z.trofea else {}
	b.odrodzenia = (b.odrodzenia or 0) + 1
	b.forma = 1
	b.wzrost = 0
	b.wariantTeraz = nil
	b.skok = nil
	if S.olbrzym == b.id then
		S.olbrzym = 0
	end
	b.olbrzymHp = nil
	b.hpMaks = L.hpMaks(D, b)
	b.hp = b.hpMaks
	b.gotowy = { ogien = 0, moc = 0 }
	b.tarczaDo = math.max(b.tarczaDo, S.czas + D.ewolucja.tarcza_po_s)
	table.insert(zd, { t = "odr_koniec", id = b.id, s = b.slot, linia = nowa, n = b.odrodzenia, x = L.mnoznikOdr(D, b) })
end

-- wydarzenia zegarowe na cały serwer (działają też z jednym graczem): DRAGON RAIN i GOLEM RAMPAGE
local function wyd(S)
	if not S.wyd then
		S.wyd = { deszczNast = math.huge, rampNast = math.huge }
	end
	return S.wyd
end
L.wyd = wyd

function L.deszczNa(S, i: number): boolean
	local E = S.wyd
	if not (E and E.deszczDo) then
		return false
	end
	local p = S.D.kulkiPoz[i]
	return not L.wLesie(S.D, p[1], p[2]) and not L.naWyspie(S.D, p[1], p[2])
end

function L.wymusWydarzenie(S, co: string)
	local E = wyd(S)
	local W = S.D.wydarzenia
	if co == "deszcz" then
		E.deszczWym = S.czas + W.deszcz.trwa_s
	elseif co == "rampage" then
		E.rampWym = S.czas + W.rampage.trwa_s
	end
end

-- retencja1: okno wydarzenia z zegara UTC (os.time) — każdy serwer ma ten sam rozkład, gracz może wrócić na wydarzenie.
-- Aktywne, gdy (teraz − przesun_s) mod co_s < trwa_s. Zwraca: aktywne, s do końca, s do następnego startu, nr cyklu.
function L.oknoWydarzenia(W, teraz: number): (boolean, number, number, number)
	local t = teraz - (W.przesun_s or 0)
	local f = t % W.co_s
	local cykl = math.floor(t / W.co_s)
	if f < W.trwa_s then
		return true, W.trwa_s - f, W.co_s - f, cykl
	end
	return false, 0, W.co_s - f, cykl
end

-- najwyższy stopień golema osiągnięty na serwerze: obecny stopień serwera albo trofea bossa gracza + 1 (najwyżej 5)
function L.stopienRampage(S): number
	local D = S.D
	local st = S.bossStopien or 1
	for _, q in S.byty do
		if q.slot > 0 then
			st = math.max(st, (q.bossTrofea or 0) + 1)
		end
	end
	return math.min(st, #D.boss.stopnie_hp)
end

local function rampageStart(S, zd)
	local D = S.D
	local R = D.wydarzenia.rampage
	local b = L.bytPoId(S, S.boss)
	if not b then
		return false
	end
	S.bossStopien = L.stopienRampage(S)
	b.martwyDo = nil
	b.hpMaks = math.floor(D.boss.stopnie_hp[S.bossStopien] * R.hp_x)
	b.hp = b.hpMaks
	b.rany = {}
	b.strefa = 3
	-- wychodzi z lasu bramą na łąkę (staje tuż za bramą, idzie do domu na łące)
	local d = math.max(1, dlug(D.las.x, D.las.z))
	local brama = D.pole.r - 12
	b.x, b.z = D.las.x / d * brama, D.las.z / d * brama
	b.domX, b.domZ = R.x, R.z
	b.myslDo = 0
	table.insert(zd, { t = "wydarzenie", co = "rampage", start = true, czas = R.trwa_s, stopien = S.bossStopien, id = b.id })
	return true
end

local function rampageKoniec(S, zd)
	local D = S.D
	local b = L.bytPoId(S, S.boss)
	if b then
		b.strefa = 2
		b.domX, b.domZ = D.las.x, D.las.z
		if not b.martwyDo then
			b.x, b.z = D.las.x, D.las.z
			b.hpMaks = D.boss.stopnie_hp[S.bossStopien or 1]
			b.hp = math.min(b.hp, b.hpMaks)
		end
	end
	table.insert(zd, { t = "wydarzenie", co = "rampage", koniec = true })
end

function L.krokWydarzen(S, zd)
	local D = S.D
	if not D.wydarzenia then
		return
	end
	local W = D.wydarzenia
	local E = wyd(S)
	-- bez zegara UTC (testy logiki) albo z wyłączonym rozkładem (próby Play) tylko wydarzenia wymuszone
	local teraz = if S.wydBezZegara then nil else S.zegar
	-- DRAGON RAIN: z zegara UTC albo wymuszony (próby)
	local akt, doK, doN = false, 0, math.huge
	if teraz then
		akt, doK, doN = L.oknoWydarzenia(W.deszcz, teraz)
	end
	if E.deszczWym then
		if S.czas < E.deszczWym then
			akt, doK = true, E.deszczWym - S.czas
		else
			E.deszczWym = nil
		end
	end
	E.deszczNast = S.czas + doN
	if E.deszczDo and (S.czas >= E.deszczDo or not akt) then
		E.deszczDo = nil
		table.insert(zd, { t = "wydarzenie", co = "deszcz", koniec = true })
	end
	if akt and not E.deszczDo and doK > 0.5 then
		E.deszczDo = S.czas + doK
		-- złote kule spadają na całą łąkę: wszystkie kule łąki od razu żywe
		for i in D.kulkiPoz do
			if L.deszczNa(S, i) then
				S.kulki[i] = 0
			end
		end
		table.insert(zd, { t = "wydarzenie", co = "deszcz", start = true, czas = doK })
	end
	-- GOLEM RAMPAGE: z zegara UTC (po pokonaniu golema do końca cyklu spokój) albo wymuszony
	local rakt, rdoK, rdoN, cykl = false, 0, math.huge, -1
	if teraz then
		rakt, rdoK, rdoN, cykl = L.oknoWydarzenia(W.rampage, teraz)
	end
	if E.rampKoniecCykl == cykl then
		rakt = false
	end
	if E.rampWym then
		if S.czas < E.rampWym then
			rakt, rdoK = true, E.rampWym - S.czas
		else
			E.rampWym = nil
		end
	end
	E.rampNast = S.czas + rdoN
	if E.rampDo and (S.czas >= E.rampDo or not rakt) then
		if S.czas >= E.rampDo and rakt then
			-- koniec przez pokonanie golema: ten cykl zegara już się nie wznawia
			E.rampKoniecCykl = cykl
			E.rampWym = nil
		end
		E.rampDo = nil
		rampageKoniec(S, zd)
	elseif rakt and not E.rampDo and rdoK > 0.5 and E.rampKoniecCykl ~= cykl then
		if rampageStart(S, zd) then
			E.rampDo = S.czas + rdoK
		end
	end
end

-- jajo dnia (raz na dzień UTC, w legowisku): darmowe losowanie wariantu trofeum obecnego stadium (tylko na lepsze)
function L.wariantJaja(D, r: number): string
	local J = D.jajo_dnia
	local suma = 0
	for _, w in J.wagi do
		suma += w[2]
	end
	local x, id = r * suma, J.wagi[1][1]
	for _, w in J.wagi do
		if x < w[2] then
			id = w[1]
			break
		end
		x -= w[2]
	end
	return id
end

------------------------------------------------------------------ retencja1: seria logowań i zadania dnia (dzień UTC)
function L.zadanieDef(D, id: string)
	for _, q in D.zadania.pula do
		if q.id == id then
			return q
		end
	end
	return nil
end

-- trzy zadania na dzień: losowanie stałe dla (dzień, ziarno gracza), tylko dostępne od zdobytej formy
function L.losujZadania(D, dzien: number, ziarno: number, maxForma: number)
	local pula = {}
	for _, q in D.zadania.pula do
		if (q.od_formy or 1) <= maxForma then
			table.insert(pula, q)
		end
	end
	local x = (dzien * 7919 + ziarno * 104729 + 1) % 2147483647
	local lista = {}
	for _ = 1, math.min(D.zadania.ile, #pula) do
		x = (x * 48271) % 2147483647
		local i = x % #pula + 1
		local q = pula[i]
		pula[i] = pula[#pula]
		pula[#pula] = nil
		table.insert(lista, { id = q.id, cel = q.cel, postep = 0, gotowe = false })
	end
	return { dzien = dzien, lista = lista }
end

-- wejście gracza: seria (dzień po dniu = dalej, przerwa = od 1), nagroda dnia od razu, zadania na dziś
function L.logowanie(D, b, teraz: number, r: number)
	local d = L.dzienUTC(teraz)
	local s = b.seria or { dzien = -1, dni = 0 }
	local nagroda, wariant, f, lepszy = nil, nil, nil, nil
	if s.dzien ~= d then
		s.dni = if s.dzien == d - 1 then s.dni % #D.seria.nagrody + 1 else 1
		s.dzien = d
		nagroda = D.seria.nagrody[s.dni]
		b.zloto += nagroda.zloto or 0
		b.boostS = (b.boostS or 0) + (nagroda.boost_s or 0)
		if nagroda.jajo then
			f = math.max(1, b.maxForma)
			wariant = L.wariantJaja(D, r)
			b.warianty = b.warianty or {}
			lepszy = L.wariantX(D, wariant) > L.wariantX(D, b.warianty[f])
			if lepszy then
				b.warianty[f] = wariant
			end
		end
	end
	b.seria = s
	if not b.zadania or b.zadania.dzien ~= d then
		b.zadania = L.losujZadania(D, d, b.ziarno or 0, b.maxForma)
	end
	return { dni = s.dni, nagroda = nagroda, wariant = wariant, f = f, lepszy = lepszy }
end

function L.postepZadania(S, b, rodzaj: string, ile: number, zd)
	if b.slot == 0 or not b.zadania then
		return
	end
	local D = S.D
	for _, q in b.zadania.lista do
		if q.id == rodzaj and not q.gotowe then
			q.postep = math.min(q.cel, q.postep + ile)
			if q.postep >= q.cel then
				q.gotowe = true
				local Q = L.zadanieDef(D, rodzaj)
				b.zloto += Q.zloto
				local wz = 0
				if b.forma < #D.formy then
					wz = Q.wzrost * L.potrzeba(D, b.forma)
					b.wzrost = math.min(L.potrzeba(D, b.forma) * D.ewolucja.pasek_maks, b.wzrost + wz)
				end
				table.insert(zd, { t = "zadanie", id = b.id, s = b.slot, zad = rodzaj, zloto = Q.zloto, wzrost = math.floor(wz) })
			end
		end
	end
end

local ZADANIE_ZDARZENIA = { owca = "owce", zamach = "zdolnosci", zebrano = "legowisko", kulka = "kulki", ewolucja = "ewolucja" }

-- co krok: postęp zadań ze zdarzeń tego kroku, wyspa, przyspieszenie, nowy dzień o 00:00 UTC
function L.krokZadan(S, dt: number, zd)
	local D = S.D
	if not D.zadania then
		return
	end
	local poSlocie = {}
	for _, b in S.byty do
		if b.slot > 0 then
			poSlocie[b.slot] = b
			if (b.boostS or 0) > 0 then
				b.boostS = math.max(0, b.boostS - dt)
			end
			if S.zegar and b.zadania and L.dzienUTC(S.zegar) ~= b.zadania.dzien then
				b.zadania = L.losujZadania(D, L.dzienUTC(S.zegar), b.ziarno or 0, b.maxForma)
				table.insert(zd, { t = "zadania_nowe", id = b.id, s = b.slot })
			end
			if b.martwyDo == nil and L.naWyspie(D, b.x, b.z) then
				L.postepZadania(S, b, "wyspa", 1, zd)
			end
			if D.mapa2 then
				L.krokSekretow(S, b, zd)
			end
		end
	end
	local n = #zd
	for i = 1, n do
		local z = zd[i]
		local rodzaj = ZADANIE_ZDARZENIA[z.t]
		if rodzaj and z.s and z.s > 0 and poSlocie[z.s] then
			L.postepZadania(S, poSlocie[z.s], rodzaj, 1, zd)
		elseif z.t == "zjedz" and (z.sa or 0) > 0 and poSlocie[z.sa] then
			L.postepZadania(S, poSlocie[z.sa], "walki", 1, zd)
		elseif z.t == "boss_rana" and (z.s or 0) > 0 and poSlocie[z.s] then
			L.postepZadania(S, poSlocie[z.s], "boss", 1, zd)
		end
	end
end

function L.dzienUTC(t: number): number
	return math.floor(t / 86400)
end

function L.jajoDostepne(D, b, teraz: number): boolean
	return b.slot > 0 and (b.dzienJaja or -1) < L.dzienUTC(teraz)
end

function L.jajoDnia(S, b, teraz: number, r: number): (boolean, string?, boolean?, number?)
	local D = S.D
	if not L.jajoDostepne(D, b, teraz) then
		return false, "jutro"
	end
	if not L.wLegowisku(D, b) then
		return false, "legowisko"
	end
	b.dzienJaja = L.dzienUTC(teraz)
	local f = math.clamp(b.forma, 1, b.maxForma)
	local id = L.wariantJaja(D, r)
	b.warianty = b.warianty or {}
	local lepszy = L.wariantX(D, id) > L.wariantX(D, b.warianty[f])
	if lepszy then
		b.warianty[f] = id
	end
	return true, id, lepszy, f
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
		warianty = {}, trofea = {}, bossTrofea = 0, ostatnio = 0, pierwszy = 0, odrodzenia = 0, linia = 1, linie = {}, dzienJaja = -1,
		seria = { dzien = -1, dni = 0 }, zadania = { dzien = -1, lista = {} }, boostS = 0, paragony = {}, sekrety = { dzien = -1, lista = {} } }
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
	-- retencja1 (zapis w wersji 2; migracja z wersji 1 = wartości domyślne): seria logowań, zadania dnia, przyspieszenie
	if type(dane.seria) == "table" then
		p.seria.dzien = math.floor(liczba(dane.seria.dzien, -1, 1e7, -1))
		p.seria.dni = math.floor(liczba(dane.seria.dni, 0, if D.seria then #D.seria.nagrody else 7, 0))
	end
	p.boostS = liczba(dane.boostS, 0, 86400, 0)
	-- odczucie1: paragony sklepu (PurchaseId jako napisy, najwyżej paragony_max)
	if type(dane.paragony) == "table" then
		local maks = (D.sklep and D.sklep.paragony_max) or 200
		for _, x in dane.paragony do
			if type(x) == "string" and #x <= 64 and #p.paragony < maks then
				table.insert(p.paragony, x)
			end
		end
	end
	-- mapa2a (zapis w wersji 3; migracja z 1–2 = brak znalezionych): sekrety dnia (id napisami, tylko znane z mapy)
	if type(dane.sekrety) == "table" and type(dane.sekrety.lista) == "table" then
		p.sekrety.dzien = math.floor(liczba(dane.sekrety.dzien, -1, 1e7, -1))
		for _, id in dane.sekrety.lista do
			local znany = false
			for _, sk in (D.mapa2 and D.mapa2.sekrety) or {} do
				if sk.id == id then
					znany = true
				end
			end
			if znany and #p.sekrety.lista < 32 then
				table.insert(p.sekrety.lista, id)
			end
		end
	end
	if type(dane.zadania) == "table" and type(dane.zadania.lista) == "table" and D.zadania then
		p.zadania.dzien = math.floor(liczba(dane.zadania.dzien, -1, 1e7, -1))
		for _, q in dane.zadania.lista do
			local Q = type(q) == "table" and type(q.id) == "string" and L.zadanieDef(D, q.id)
			if Q and #p.zadania.lista < D.zadania.ile then
				table.insert(p.zadania.lista, { id = Q.id, postep = math.floor(liczba(q.postep, 0, Q.cel, 0)), gotowe = q.gotowe == true })
			end
		end
	end
	-- odrodzenie1: liczba odrodzeń, obecna linia, postęp pozostałych linii (klucze „1”–„4”), dzień jaja
	local nl = if D.odrodzenie then #D.odrodzenie.linie else 1
	p.odrodzenia = math.floor(liczba(dane.odrodzenia, 0, 1000, 0))
	p.linia = math.floor(liczba(dane.linia, 1, nl, 1))
	p.dzienJaja = math.floor(liczba(dane.dzienJaja, -1, 1e7, -1))
	if type(dane.linie) == "table" then
		for l = 1, nl do
			local z = dane.linie[tostring(l)]
			if l ~= p.linia and type(z) == "table" then
				local q = { maxForma = math.floor(liczba(z.maxForma, 1, nf, 1)), warianty = {}, trofea = {} }
				for f = 1, nf do
					local w = type(z.warianty) == "table" and z.warianty[f]
					q.warianty[f] = if type(w) == "string" and L.wariant(D, w) then w else ""
					q.trofea[f] = math.floor(liczba(type(z.trofea) == "table" and z.trofea[f], 1, #D.legowisko.poziomy_x, 1))
				end
				p.linie[tostring(l)] = q
			end
		end
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
	p.odrodzenia = b.odrodzenia or 0
	p.linia = b.linia or 1
	p.dzienJaja = b.dzienJaja or -1
	p.seria = { dzien = (b.seria and b.seria.dzien) or -1, dni = (b.seria and b.seria.dni) or 0 }
	p.boostS = math.floor(b.boostS or 0)
	for _, x in b.paragony or {} do
		table.insert(p.paragony, x)
	end
	if b.sekrety then
		p.sekrety.dzien = b.sekrety.dzien
		for _, id in b.sekrety.lista do
			table.insert(p.sekrety.lista, id)
		end
	end
	if b.zadania then
		p.zadania.dzien = b.zadania.dzien
		for _, q in b.zadania.lista do
			table.insert(p.zadania.lista, { id = q.id, postep = q.postep, gotowe = q.gotowe })
		end
	end
	for l, z in b.linie or {} do
		local q = { maxForma = z.maxForma, warianty = {}, trofea = {} }
		for f = 1, #D.formy do
			q.warianty[f] = (z.warianty and z.warianty[f]) or ""
			q.trofea[f] = (z.trofea and z.trofea[f]) or 1
		end
		p.linie[tostring(l)] = q
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
	b.odrodzenia = p.odrodzenia or 0
	b.linia = p.linia or 1
	b.dzienJaja = p.dzienJaja or -1
	b.seria = { dzien = p.seria.dzien, dni = p.seria.dni }
	b.boostS = p.boostS or 0
	b.ziarno = math.floor(b.pierwszy or 0) % 100003
	b.paragony = {}
	for _, x in p.paragony or {} do
		table.insert(b.paragony, x)
	end
	b.sekrety = { dzien = (p.sekrety and p.sekrety.dzien) or -1, lista = {} }
	for _, id in (p.sekrety and p.sekrety.lista) or {} do
		table.insert(b.sekrety.lista, id)
	end
	b.zadania = nil
	if p.zadania and p.zadania.dzien >= 0 then
		local lista = {}
		for _, q in p.zadania.lista do
			local Q = L.zadanieDef(D, q.id)
			table.insert(lista, { id = q.id, cel = Q.cel, postep = q.postep, gotowe = q.gotowe })
		end
		b.zadania = { dzien = p.zadania.dzien, lista = lista }
	end
	b.linie = {}
	for k, q in p.linie or {} do
		local l = tonumber(k)
		if l and l ~= b.linia then
			local w = {}
			for f = 1, #D.formy do
				w[f] = if q.warianty[f] ~= "" then q.warianty[f] else nil
			end
			b.linie[l] = { maxForma = q.maxForma, warianty = w, trofea = q.trofea }
		end
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
