--[[
	LogikaBonk — czyste rachunki gry BONK (ModuleScript w Workspace/BonkGra/Moduly). Bez instancji Roblox: liczby,
	napisy i tabele, więc ten sam kod wykonuje bez Studio interpreter tools/walka/luau_mini.py (testy/test_bonk.py).
	Używają go serwer (prawda o grze) i klient (rysunek tego, co policzył serwer).

	Etap 2: pałki (L.kupPalke, L.mnoznikPalki), jajka i pety (L.losujPeta, L.wyklujJajko, L.najlepszePety,
	L.mnoznikPetow = 1 + suma premii), Księga (L.ksiega), Strażnik i brama (L.mozePrzejsc: Moc i profil.straznicy[nr] > 0,
	L.nagrodaStraznika), dzienny prezent (L.prezent, L.odbierzPrezent — opuszczony dzień nie zeruje serii), profil v2
	z migracją z v1 (L.profil). Bez table.sort / table.clone / math.clamp (interpreter testów ich nie ma).
	Etap 3: L.mnoznikTekst (mnożnik dokładnie: „x1.5 POWER”), L.stos (kolejka napisów u góry ekranu bez nakładania).
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

-- mnożnik dokładnie (etap 3): 1.5 → "1.5", 2 → "2", 1.35 → "1.35", 1.3 → "1.3", 28 → "28"; od 1000 jak L.format
function L.mnoznikTekst(n: number): string
	if n ~= n or n < 0 then
		return "1"
	end
	if n >= 1000 then
		return L.format(n)
	end
	local c = math.floor(n * 100 + 0.5)
	local calk = math.floor(c / 100)
	local reszta = c - calk * 100
	if reszta == 0 then
		return tostring(calk)
	elseif reszta % 10 == 0 then
		return tostring(calk) .. "." .. tostring(math.floor(reszta / 10))
	elseif reszta < 10 then
		return tostring(calk) .. ".0" .. tostring(reszta)
	end
	return tostring(calk) .. "." .. tostring(reszta)
end

-- stos napisów u góry ekranu (etap 3): wysokości widocznych elementów (punkty, już ze skalą) → górne krawędzie
-- kolejno od `start` z odstępem; zwraca listę pozycji i dół stosu (pierwszy wolny punkt pod nim)
function L.stos(wysokosci: { number }, start: number, odstep: number): ({ number }, number)
	local poz = {}
	local y = start
	for i, h in wysokosci do
		poz[i] = y
		y = y + h + odstep
	end
	return poz, y
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

-- czy gracz pokonał już Strażnika krainy nr (profil.straznicy[nr] = liczba pokonań)
function L.pokonal(profil, nr: number): boolean
	return profil ~= nil and type(profil.straznicy) == "table" and (tonumber(profil.straznicy[nr]) or 0) > 0
end

-- czy gracz może przejść bramę krainy `nr` (z krainy nr do nr + 1): Moc bramy i pokonany Strażnik tej krainy
function L.mozePrzejsc(nr: number, moc: number, D, profil): boolean
	local K = D.krainy[nr]
	if not K or nr >= #D.krainy then
		return false -- za ostatnią bramą nie ma jeszcze krainy
	end
	return moc >= K.brama.wymagana and L.pokonal(profil, nr)
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

-- profil wersji 2: palka = najwyższa kupiona pałka (0 = bez pałki), pety = { [id] = kopie }, aktywne = lista id
-- (kopie tego samego peta mogą iść kilka razy), autoPety = najlepsze same, ksiega = { [id] = true } (odkryte),
-- straznicy = { pokonań w krainie 1, 2, 3 } (gęsta lista — bezpieczna w magazynie), prezent = { dzien, seria }, jajek
function L.nowyProfil(D)
	local straznicy = {}
	for i = 1, #D.krainy do
		straznicy[i] = 0
	end
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
		palka = 0,
		pety = {},
		aktywne = {},
		autoPety = true,
		ksiega = {},
		straznicy = straznicy,
		prezent = { dzien = -1, seria = 0 },
		jajek = 0,
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

-- profil z magazynu → sprawdzony profil bieżącej wersji (zła wartość = domyślna; nieznane pola znikają).
-- Migracja v1 → v2: pałka z v1 (1 = brak pałki) → 0, pety i Strażnicy od zera (w v1 ich nie było), prezent nowy.
function L.profil(s, D)
	local p = L.nowyProfil(D)
	if type(s) ~= "table" then
		return p
	end
	local wersja = math.floor(liczba(s.v, 1, 1, 1000))
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
	if wersja < 2 then
		return p -- v1: reszta pól nowa (pałka 0, bez petów, Strażnicy 0, prezent od nowa)
	end
	p.palka = math.floor(liczba(s.palka, 0, 0, #D.palki))
	p.jajek = math.floor(liczba(s.jajek, 0, 0, DUZO))
	local pety = if type(s.pety) == "table" then s.pety else {}
	local ksiega = if type(s.ksiega) == "table" then s.ksiega else {}
	for _, id in D.petyKolejnosc do
		local n = math.floor(liczba(pety[id], 0, 0, 1e9))
		if n > 0 then
			p.pety[id] = n
		end
		if n > 0 or ksiega[id] == true then
			p.ksiega[id] = true
		end
	end
	p.autoPety = s.autoPety ~= false
	p.aktywne = L.aktywneZListy(s.aktywne, p.pety, D)
	if p.autoPety then
		p.aktywne = L.najlepszePety(p.pety, D)
	end
	local st = if type(s.straznicy) == "table" then s.straznicy else {}
	for i = 1, #D.krainy do
		p.straznicy[i] = math.floor(liczba(st[i], 0, 0, 1e9))
	end
	if type(s.prezent) == "table" then
		p.prezent.dzien = math.floor(liczba(s.prezent.dzien, -1, -1, 1e7))
		p.prezent.seria = math.floor(liczba(s.prezent.seria, 0, 0, 1e6))
	end
	return p
end

------------------------------------------------------------------ pałki
function L.mnoznikPalki(nr: number, D): number
	local P = D.palki[nr]
	return if P then P.mnoznik else D.moc.mnoznik_palki
end

-- zakup pałki nr (po kolei: nr = palka + 1); zmienia profil przy powodzeniu → (ok, powód: "kolejnosc" | "monety")
function L.kupPalke(profil, nr: number, D): (boolean, string?)
	local P = D.palki[nr]
	if type(nr) ~= "number" or not P or nr ~= profil.palka + 1 then
		return false, "kolejnosc"
	end
	if profil.monety < P.cena then
		return false, "monety"
	end
	profil.monety -= P.cena
	profil.palka = nr
	return true, nil
end

------------------------------------------------------------------ jajka i pety
-- pet z jajka J dla liczby losowej r ∈ [0, 1): szanse rzadkości po kolei (jawne, D.rzadkosci)
function L.losujPeta(J, r: number, D): string
	local suma = 0
	for i, R in D.rzadkosci do
		suma += R.szansa
		if r < suma then
			return J.pety[i]
		end
	end
	return J.pety[#J.pety]
end

function L.premiaPeta(id: string, D): number
	local P = D.pety[id]
	return if P then P.premia else 0
end

-- najlepsze `maks` petów z posiadanych (kopie liczą się osobno): premia malejąco, przy równej — późniejszy w Księdze
function L.najlepszePety(pety, D, maks: number?): { string }
	local m = maks or D.petyUst.maks_aktywnych
	local kand = {}
	for i, id in D.petyKolejnosc do
		local n = math.min(tonumber(pety[id]) or 0, m)
		for _ = 1, n do
			table.insert(kand, { id = id, premia = L.premiaPeta(id, D), nr = i, uzyty = false })
		end
	end
	local wynik = {}
	for _ = 1, m do
		local naj = nil
		for _, k in kand do
			if not k.uzyty and (naj == nil or k.premia > naj.premia or (k.premia == naj.premia and k.nr > naj.nr)) then
				naj = k
			end
		end
		if not naj then
			break
		end
		naj.uzyty = true
		table.insert(wynik, naj.id)
	end
	return wynik
end

-- lista wybrana przez gracza → poprawna (znane pety, nie więcej kopii niż ma, najwyżej maks)
function L.aktywneZListy(lista, pety, D, maks: number?): { string }
	local m = maks or D.petyUst.maks_aktywnych
	local wynik, uzyte = {}, {}
	if type(lista) ~= "table" then
		return wynik
	end
	for _, id in lista do
		if #wynik >= m then
			break
		end
		if type(id) == "string" and D.pety[id] and (uzyte[id] or 0) < (tonumber(pety[id]) or 0) then
			uzyte[id] = (uzyte[id] or 0) + 1
			table.insert(wynik, id)
		end
	end
	return wynik
end

-- mnożnik petów = 1 + suma premii aktywnych (liniowo — nie wybucha jak iloczyn)
function L.mnoznikPetow(aktywne, D): number
	local s = 0
	for _, id in aktywne do
		s += L.premiaPeta(id, D)
	end
	return math.floor((1 + s) * 1000 + 0.5) / 1000
end

-- zakup i wyklucie jajka krainy nr (r = liczba losowa z serwera); zmienia profil → (ok, wynik albo powód)
function L.wyklujJajko(profil, nr: number, r: number, D)
	local J = D.jajka[nr]
	if type(nr) ~= "number" or not J then
		return false, "brak"
	end
	if nr > profil.odblokowane then
		return false, "kraina"
	end
	if profil.monety < J.cena then
		return false, "monety"
	end
	profil.monety -= J.cena
	local id = L.losujPeta(J, r, D)
	local bylo = tonumber(profil.pety[id]) or 0
	profil.pety[id] = bylo + 1
	profil.ksiega[id] = true
	profil.jajek += 1
	if profil.autoPety then
		profil.aktywne = L.najlepszePety(profil.pety, D)
	end
	return true, { pet = id, nowy = bylo == 0, kopie = bylo + 1, rzadkosc = D.pety[id].rzadkosc }
end

-- Księga: (odkryte, wszystkie)
function L.ksiega(profil, D): (number, number)
	local n = 0
	for _, id in D.petyKolejnosc do
		if profil.ksiega[id] == true then
			n += 1
		end
	end
	return n, #D.petyKolejnosc
end

------------------------------------------------------------------ Strażnik
-- nagroda dla gracza, który zadał `udzial` (0…1) obrażeń: (monety, Moc); najmniej udzial_min całej nagrody
function L.nagrodaStraznika(S, udzial: number, D): (number, number)
	local u = math.max(D.straznik.udzial_min, math.min(1, udzial))
	return math.floor(S.monety * u + 1e-9), math.max(1, math.floor(S.moc * u + 1e-9))
end

------------------------------------------------------------------ dzienny prezent
function L.dzien(t: number): number
	return math.floor(t / 86400)
end

-- (czy można odebrać dziś, nagroda w monetach, numer dnia serii 1…7); opuszczony dzień nie zeruje serii
function L.prezent(profil, dzien: number, D): (boolean, number, number)
	local N = D.prezent.nagrody
	local k = math.min(profil.prezent.seria + 1, #N)
	local MK = D.prezent.mnoznik_krainy
	local mk = MK[math.max(1, math.min(profil.odblokowane, #MK))]
	return dzien > profil.prezent.dzien, N[k] * mk, k
end

function L.odbierzPrezent(profil, dzien: number, D): (boolean, number, number)
	local mozna, nagroda, k = L.prezent(profil, dzien, D)
	if not mozna then
		return false, 0, k
	end
	profil.monety += nagroda
	profil.prezent.dzien = dzien
	profil.prezent.seria += 1
	return true, nagroda, k
end

return L
