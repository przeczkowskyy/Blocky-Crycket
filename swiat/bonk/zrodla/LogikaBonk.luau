--[[
	LogikaBonk — czyste rachunki gry BONK (ModuleScript w Workspace/BonkGra/Moduly). Bez instancji Roblox: liczby,
	napisy i tabele, więc ten sam kod wykonuje bez Studio interpreter tools/walka/luau_mini.py (testy/test_bonk.py).
	Używają go serwer (prawda o grze) i klient (rysunek tego, co policzył serwer).

	Haczyki etapu 2 (pałki, pety, Strażnik, sklep): L.moc bierze mnożnik pałki i petów (dziś 1), L.mozePrzejsc
	dostaje profil gracza (pole `straznicy` — pokonani Strażnicy; dziś brama patrzy tylko na Moc).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local L = {}

------------------------------------------------------------------ liczby
local PRZYROSTKI = { "K", "M", "B", "T", "Qa", "Qi", "Sx", "Sp" }

-- 999 → "999", 1234 → "1.2K", 12345 → "12.3K", 123456 → "123K", 3.4e6 → "3.4M" (ucięte, nie zaokrąglone w górę)
function L.format(n: number): string
	if n ~= n then
		return "0"
	end
	local znak = ""
	if n < 0 then
		znak = "-"
		n = -n
	end
	if n < 1000 then
		return znak .. tostring(math.floor(n))
	end
	local i = 0
	while n >= 1000 and i < #PRZYROSTKI do
		n = n / 1000
		i += 1
	end
	local tekst
	if n >= 100 then
		tekst = tostring(math.floor(n))
	else
		local d = math.floor(n * 10 + 1e-9) / 10
		if d == math.floor(d) then
			tekst = tostring(math.floor(d))
		else
			tekst = string.format("%.1f", d)
		end
	end
	return znak .. tekst .. PRZYROSTKI[i]
end

-- Moc = Moc z uderzeń × mnożnik pałki × mnożnik petów (etap 2); najmniej 1
function L.moc(baza: number, palka: number?, pety: number?): number
	local m = math.floor((baza or 1) * (palka or 1) * (pety or 1) + 1e-9)
	if m < 1 then
		return 1
	end
	return m
end

------------------------------------------------------------------ krainy i bramy
-- numer krainy, w której leży x (krainy ułożone wzdłuż osi X)
function L.kraina(x: number, D): number
	local K = D.krainy
	for i = 1, #K do
		if x < K[i].xDo then
			return i
		end
	end
	return #K
end

-- czy gracz może przejść bramę krainy `nr` (z krainy nr do nr + 1). Haczyk etapu 2: profil.straznicy[nr].
function L.mozePrzejsc(nr: number, moc: number, D, profil): boolean
	local K = D.krainy[nr]
	if not K or nr >= #D.krainy then
		return false -- za ostatnią bramą nie ma jeszcze krainy
	end
	return moc >= K.brama.wymagana
end

-- ile krain gracz ma otwartych (1…#krainy); otwartej bramy już się nie zamyka
function L.odblokowane(moc: number, D, profil, stare: number?): number
	local n = 1
	while n < #D.krainy and L.mozePrzejsc(n, moc, D, profil) do
		n += 1
	end
	if stare and stare > n then
		n = math.min(stare, #D.krainy)
	end
	return n
end

------------------------------------------------------------------ tempo uderzeń (serwer)
-- wiadro: `stan` = { zapas, czas }; zwraca (czy przyjąć, nowy stan)
function L.wiadro(stan, teraz: number, naSekunde: number, pojemnosc: number)
	local zapas = pojemnosc
	local czas = teraz
	if stan then
		zapas = math.min(pojemnosc, stan.zapas + (teraz - stan.czas) * naSekunde)
	end
	if zapas >= 1 then
		return true, { zapas = zapas - 1, czas = czas }
	end
	return false, { zapas = zapas, czas = czas }
end

------------------------------------------------------------------ potwory
-- pozycja wędrującego potwora: z (ox, oz) do (cx, cz) od chwili t0 z prędkością pr
function L.pozycja(ox: number, oz: number, cx: number, cz: number, t0: number, pr: number, teraz: number)
	local dx, dz = cx - ox, cz - oz
	local dl = math.sqrt(dx * dx + dz * dz)
	if dl < 1e-6 or pr <= 0 then
		return cx, cz
	end
	local f = (teraz - t0) * pr / dl
	if f <= 0 then
		return ox, oz
	elseif f >= 1 then
		return cx, cz
	end
	return ox + dx * f, oz + dz * f
end

-- najbliższy żywy potwór w zasięgu: lista { x, z, promien, zywy }; → indeks albo nil
function L.wybierzCel(px: number, pz: number, lista, zasieg: number): number?
	local najlepszy, odl = nil, math.huge
	for i, p in lista do
		if p.zywy then
			local dx, dz = p.x - px, p.z - pz
			local d = math.sqrt(dx * dx + dz * dz) - (p.promien or 0)
			if d <= zasieg and d < odl then
				najlepszy, odl = i, d
			end
		end
	end
	return najlepszy
end

function L.zycie(G, rzadki: boolean, D): number
	return G.hp * (if rzadki then D.rzadki.hp_x else 1)
end

-- nagroda za BONK: monety i Moc
function L.nagroda(G, rzadki: boolean, homeRun: boolean, D)
	local monety = G.monety * (if rzadki then D.rzadki.monety_x else 1) * (if homeRun then D.lot.home_run_monety_x else 1)
	local moc = G.moc * (if rzadki then D.rzadki.moc_x else 1)
	return monety, moc
end

------------------------------------------------------------------ lot
-- odległość, wysokość łuku, czas lotu i HOME RUN z nadwyżki Mocy nad życiem potwora
function L.lot(moc: number, zycieMax: number, P)
	local r = moc / math.max(1, zycieMax)
	local odl = P.baza + P.na_log2 * math.log(1 + r) / math.log(2)
	if odl > P.max then
		odl = P.max
	end
	local wys = P.wysokosc_baza + P.wysokosc_x * odl
	local czas = P.czas_baza + P.czas_na_stud * odl
	return { odl = odl, wys = wys, czas = czas, homeRun = odl >= P.home_run }
end

-- koniec lotu: od potwora w kierunku (dx, dz) od gracza, obrócony o kąt (stopnie)
function L.koniecLotu(ox: number, oz: number, dx: number, dz: number, odl: number, katStopnie: number)
	local dl = math.sqrt(dx * dx + dz * dz)
	if dl < 1e-6 then
		dx, dz, dl = 1, 0, 1
	end
	dx, dz = dx / dl, dz / dl
	local a = math.rad(katStopnie)
	local c, s = math.cos(a), math.sin(a)
	local rx, rz = dx * c - dz * s, dx * s + dz * c
	return ox + rx * odl, oz + rz * odl
end

-- punkt łuku w ułamku f (0…1): liniowo w poziomie, parabola w pionie (szczyt = wys nad wyższym końcem)
function L.punktLotu(ox: number, oy: number, oz: number, kx: number, ky: number, kz: number, wys: number, f: number)
	local x = ox + (kx - ox) * f
	local z = oz + (kz - oz) * f
	local y = oy + (ky - oy) * f + 4 * wys * f * (1 - f)
	return x, y, z
end

------------------------------------------------------------------ profil (zapis)
-- który magazyn otworzyć: (nazwa albo nil, opis stanu). Znacznik próby (tools/zapis_prob.py stawia ZapisProbaDo
-- = os.time() końca na Workspace/BonkGra przed Play) → nil: prawdziwego zapisu NIE czytamy i NIE piszemy;
-- z ZapisProbaMagazyn = true → osobny magazyn próby (…_Studio_Proba). Poza Studio znacznik nic nie znaczy.
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

function L.nowyProfil(D)
	return {
		v = D.zapis.wersja_profilu,
		moc = D.moc.start,
		monety = 0,
		bonki = 0,
		najdalej = 0,
		homeRuny = 0,
		rzadkie = 0,
		odblokowane = 1,
		kraina = 1,
		samouczek = false,
		palka = 1,
		pety = {},
		straznicy = {},
	}
end

local function liczba(v, domyslna: number, min: number, max: number): number
	if type(v) ~= "number" or v ~= v or v == math.huge or v == -math.huge then
		return domyslna
	end
	if v < min then
		return min
	elseif v > max then
		return max
	end
	return v
end

-- profil z magazynu → sprawdzony profil bieżącej wersji (zła wartość = domyślna; nieznane pola znikają)
function L.profil(s, D)
	local p = L.nowyProfil(D)
	if type(s) ~= "table" then
		return p
	end
	local DUZO = 1e300
	p.moc = liczba(s.moc, p.moc, 1, DUZO)
	p.monety = liczba(s.monety, 0, 0, DUZO)
	p.bonki = math.floor(liczba(s.bonki, 0, 0, DUZO))
	p.najdalej = liczba(s.najdalej, 0, 0, 100000)
	p.homeRuny = math.floor(liczba(s.homeRuny, 0, 0, DUZO))
	p.rzadkie = math.floor(liczba(s.rzadkie, 0, 0, DUZO))
	p.odblokowane = math.floor(liczba(s.odblokowane, 1, 1, #D.krainy))
	p.kraina = math.floor(liczba(s.kraina, 1, 1, p.odblokowane))
	p.samouczek = s.samouczek == true
	p.palka = math.floor(liczba(s.palka, 1, 1, 1000))
	if type(s.pety) == "table" then
		p.pety = s.pety
	end
	if type(s.straznicy) == "table" then
		p.straznicy = s.straznicy
	end
	return p
end

return L
