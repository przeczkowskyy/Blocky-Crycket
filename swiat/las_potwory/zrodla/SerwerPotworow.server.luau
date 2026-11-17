--[[
	SerwerPotworow — serwerowa połowa pakietu „potwory w ruchu” w Borze Pod Ukłonem (Script, RunContext = Server,
	w kontenerze Workspace/LasPotwory). Kontrakt: swiat/las_potwory/PROJEKT.md (rozdz. 1.3, 3, 4.3, 5, 7, 8.6).

	Serwer jest autorytatywny (D-016): sam przesuwa punkt bazowy każdego potwora po pętli węzłów 4 razy na sekundę,
	sam odradza potwory, sam sprawdza prośbę o walkę, buduje postać wzorcową, liczy walkę silnikiem v2 i łup.
	Klient tylko ogląda atrybuty i odtwarza dziennik walki. Długość walki to wyłącznie wynik silnika (D-068); nic tu
	nie zależy od pary klasa–potwór (D-069).

	Kolejność w tym pliku (jak w rozdz. 12 kontraktu):
		1. strażnik Studio: poza Studio niszczy CAŁY kontener i kończy;
		2. kontrola BiomLas (rozdz. 1.3): Wygenerowane = true i Płyta tam, gdzie mówi DanePotworow.biom.plyta;
		   zła → warn, StanBiomu = "brak_biomu" / "zle_polozenie", zero potworów, zdalna odpowiada „zly_wybor”;
		3. kopie szablonów aktorów do ReplicatedStorage/LasPotworySzablony (rozdz. 4.3; powód: streaming);
		4. start (rozdz. 3.4): potwory od razu na pętli, równo rozstawione;
		5. ruch co Stale.OKRES_RUCHU (rozdz. 3.2–3.3): Logika.krokGrup z odstępem 25, wychodzenie z domu, rezerwacja
		   i wejście na pętlę; koniec zajętości (rozdz. 3.6);
		6. odradzanie co sekundę (rozdz. 3.5): cel z liczby graczy, kolejka, wolny dom (karuzela);
		7. OnServerInvoke zdalnej RozpocznijWalke2 (rozdz. 5.1, kontrole 1–11 w tej kolejności);
		8. PlayerRemoving kończy zajętość od razu;
		9. haczyk Sygnaly/SterowanieSerwera (rozdz. 8.6).
	Stan potworów idzie do klientów WYŁĄCZNIE atrybutami Configuration w LasPotwory/Stan/<id> (rozdz. 3.8).

	Tyknięcie ruchu jest skopiowane 1:1 w testy/test_logiki.py (klasa Symulacja): koniec zajętości → krokGrup →
	członkowie grup → wychodzący → czekający. Zmieniasz kolejność tutaj — zmień ją tam (test pilnuje odstępu 25).
	Zatrzymanie przy graczu (17.11.2026, aktualizujZatrzymania przed krokGrup) działa tylko przy graczu w pobliżu — w
	Symulacji graczy nie ma, a grupa z zatrzymanym członkiem stoi tą samą drogą co grupa z zajętym (już testowaną).

	Odczytania kontraktu (najprostsze; spis w UWAGI_S.md):
		• zajętość nie zmienia stanu wewnętrznego (wychodzi / czeka / chodzi) — to osobne pole `zajety`; po przegranej
		  potwór po prostu wraca do tego stanu;
		• czas „teraz” to workspace:GetServerTimeNow() (ten sam zegar, którego odtwarzacz używa dla nastepnaOd);
		  odstęp między prośbami mierzy os.clock(), jak w SerwerWalki2;
		• Strażnik przechodzi tą samą ścieżką co zwykły potwór, z jednym wyjątkiem (poprawka recenzji): zasada „dom
		  wolny, gdy żaden gracz nie stoi bliżej niż 18” dotyczy domów stref z potwory.json, a Strażnik domu nie ma —
		  jego jedyny punkt to miejsce walki. Dlatego wraca dokładnie po odrodzenieS (120 s), także gdy zwycięzca stoi
		  obok (inaczej tester z 9.2 p. 10, który stoi 13 studów od niego, nigdy by go nie zobaczył, a StraznikWraca
		  pokazywałby czas, który już minął);
		• przy złym biomie SerwerGotowy zostaje false (serwer nie jest gotowy), a powód jest w StanBiomu.

	Atrybuty kontenera tylko do testów (ustawia człowiek w Edit albo z paska poleceń serwera): ZiarnoTestowe,
	TestBezSesji, TestGraczy, TestBezBiomu. Zmiana atrybutu u klienta się nie replikuje, więc klient ich nie nadużyje.

	Drugi kontener (16.11.2026, Workspace/LasPasGra — las-pas, swiat/las_pas_gra; stary las działa jak dotąd):
		• DanePotworow.biom.plyta może być false — wtedy sprawdzamy tylko, czy mapa jest i ma Wygenerowane;
		• strefa z odrodzenieStale = true (Leśny Troll) wraca po odrodzenieS bez skracania, jak Strażnik (ale ma dom
		  i blokadę domu jak zwykła strefa);
		• gracz z atrybutem Stale.ATRYBUT_BLOKADY = true (np. w czasie przelotu kamery) dostaje odmowę „brak_postaci”;
		• gdy w Sygnaly jest BindableEvent Stale.SYGNAL_WYNIKU, po przyjęciu walki serwer strzela nim
		  (gracz, { id, strefa, gatunek, straznik, wynik, poziom, koniec }) — np. brama do Bagna po Strażniku.

	Stan gracza (17.11.2026, swiat/stan_gracza, propozycja): gdy w Workspace jest kontener Stale.KONTENER_STANU, kontrola 7
	bierze bohatera z jego Sygnaly/Bohater (klasa z atrybutu Class, poziom z Level, sześć statystyk gracza; klasy i poziomu
	od klienta wtedy nie słuchamy), a po przyjęciu walki łup idzie do Sygnaly/PrzyznajLup. Atrybut kontenera lasu
	Stale.ATRYBUT_TESTU_BOHATERA = true (ustawiają go próby w Play) przywraca regułę testową T1 i walki bez łupu.
]]
if not game:GetService("RunService"):IsStudio() then
	-- Pakiet działa wyłącznie w Studio (testy). Poza Studio (opublikowane miejsce) serwer usuwa CAŁY kontener —
	-- moduły, kopię silnika, zdalną funkcję i klienta — zanim ktokolwiek dołączy.
	script.Parent:Destroy()
	return
end

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local kontener = script.Parent
local moduly = kontener:WaitForChild("Moduly")
local Stale = require(moduly:WaitForChild("Stale"))
local DanePotworow = require(moduly:WaitForChild("DanePotworow"))
local Logika = require(moduly:WaitForChild("Logika"))
local Wzorcowe = require(moduly:WaitForChild("Wzorcowe"))
local Silnik = require(moduly:WaitForChild("Walka"):WaitForChild("Silnik"))
local folderStanu = kontener:WaitForChild("Stan")
local zdalna = kontener:WaitForChild("Zdalne"):WaitForChild("RozpocznijWalke2") :: RemoteFunction
local sterowanie = kontener:WaitForChild("Sygnaly"):WaitForChild("SterowanieSerwera") :: BindableFunction
-- opcjonalny sygnał wyniku walki (jest tylko w kontenerach, które go zbudowały — stary las go nie ma)
local sygnalWyniku = kontener:WaitForChild("Sygnaly"):FindFirstChild(Stale.SYGNAL_WYNIKU)

local P = Stale.PREFIKS
local ODSTEP = DanePotworow.zasady.odstep
local BLOKADA_DOMU = DanePotworow.zasady.blokadaDomu
local generator = Random.new()

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function gadaj(tekst: string)
	if Stale.GADATLIWY then
		print(P .. tekst)
	end
end

------------------------------------------------------------------ rejestr
--[[ Strefa w pamięci serwera:
	{ d = wpis DanePotworow.strefy, gatunek = DanePotworow.gatunki[...], v = prędkość, L = długość pętli,
	  grupy = { grupa }, potwory = { potwor } (kolejność powstania), kolejka = { czas serwera odrodzenia, ... },
	  licznik, ostatniDom, cel, minLuka, ostrzezono }
	Grupa: { s = czoło na pętli parametru, sStare, dlugosc, rezerwacja = bool, czlonkowie = { [miejsce] = potwor } }
	Potwor: { id, strefa, gatunek, nazwa, wariant, poziom, stan = "wychodzi" | "czeka" | "chodzi", dom,
	          x, y, z, yaw, ruszyl, grupa?, miejsce, rezerwacja?, zajety? = { gracz, wynik, koniec },
	          konfig = Configuration, zapisanaPozycja?, zapisanyKierunek?, zapisanyStan? } ]]
local strefy = {}
local potwory: { [string]: any } = {}
local liczbaZywych = 0
local gotowy = false -- true dopiero po starcie (rozdz. 3.4); wcześniej każda prośba to „zly_wybor”

local function ustawPotworow()
	kontener:SetAttribute("Potworow", liczbaZywych)
end

-- napis Stan dla klienta: "zajety" > "idzie" / "stoi" (rozdz. 3.1)
local function stanAtrybutu(p): string
	if p.zajety then
		return "zajety"
	elseif p.stop then
		return "stoi" -- zatrzymany przy graczu (17.11.2026): klient gra spoczynek
	elseif p.stan == "wychodzi" then
		return "idzie"
	elseif p.stan == "czeka" then
		return "stoi"
	end
	return if p.ruszyl then "idzie" else "stoi"
end

local function roznicaKata(a: number, b: number): number
	local d = (a - b + math.pi) % (2 * math.pi) - math.pi
	return math.abs(d)
end

-- zapis atrybutów tylko przy zmianie (rozdz. 3.8): pozycja > PROG_POZYCJI, kierunek > PROG_KIERUNKU
local function zapiszAtrybuty(p)
	local c = p.konfig
	if not c then
		return
	end
	local poz = Vector3.new(p.x, p.y, p.z)
	if not p.zapisanaPozycja or (poz - p.zapisanaPozycja).Magnitude > Stale.PROG_POZYCJI then
		c:SetAttribute("Pozycja", poz)
		p.zapisanaPozycja = poz
	end
	if not p.zapisanyKierunek or roznicaKata(p.yaw, p.zapisanyKierunek) > Stale.PROG_KIERUNKU then
		c:SetAttribute("Kierunek", p.yaw)
		p.zapisanyKierunek = p.yaw
	end
	local stan = stanAtrybutu(p)
	if stan ~= p.zapisanyStan then
		c:SetAttribute("Stan", stan)
		p.zapisanyStan = stan
	end
end

-- D-096: strefa scalona z trzech kojców (poziomyPoMiejscach) — poziomy rozdane po miejscach, nie losowo. Miejsca w
-- kolejności lo, lo+1, …, hi, lo, lo+1, … (do max); nowy potwór dostaje poziom pierwszego miejsca, którego żywe potwory
-- nie zajmują — najniższy poziom jest zawsze pierwszy (przy 1 graczu w Zagrodzie: 1 i 2, potem 3, potem drugi 1)
local function poziomNaMiejsce(lo: number, hi: number, maks: number, zywe: { number }): number
	local liczba = {}
	for _, poz in zywe do
		liczba[poz] = (liczba[poz] or 0) + 1
	end
	for i = 0, math.max(maks, 1) - 1 do
		local poz = lo + i % (hi - lo + 1)
		if (liczba[poz] or 0) > 0 then
			liczba[poz] -= 1
		else
			return poz
		end
	end
	return lo
end

local function poziomNowego(st): number
	local lo, hi = st.d.poziomy[1], st.d.poziomy[2]
	if not st.d.poziomyPoMiejscach or hi <= lo then
		return generator:NextInteger(lo, hi)
	end
	local zywe = {}
	for _, q in st.potwory do
		table.insert(zywe, q.poziom)
	end
	return poziomNaMiejsce(lo, hi, st.d.max, zywe)
end

-- nowy potwór (bez Configuration — tę tworzy opublikuj, gdy położenie jest już policzone)
local function utworzPotwora(st, stan: string, dom: number)
	st.licznik += 1
	local d = st.d.domy[dom]
	local wariant = st.d.wariant
	local p = {
		id = st.d.id .. "-" .. tostring(st.licznik),
		strefa = st,
		gatunek = st.d.gatunek,
		nazwa = if wariant then wariant.nazwa else st.gatunek.nazwa,
		wariant = if wariant then wariant.id else "",
		poziom = poziomNowego(st),
		stan = stan,
		dom = dom,
		x = d.x,
		y = d.y,
		z = d.z,
		yaw = st.d.trasa.yaw or 0,
		ruszyl = false,
		grupa = nil,
		miejsce = 0,
		rezerwacja = nil,
		zajety = nil,
		konfig = nil,
	}
	table.insert(st.potwory, p)
	potwory[p.id] = p
	liczbaZywych += 1
	return p
end

-- Configuration z kompletem atrybutów PRZED Parent = Stan (klient w ChildAdded ma wszystko)
local function opublikuj(p)
	local c = Instance.new("Configuration")
	c.Name = p.id
	c:SetAttribute("Gatunek", p.gatunek)
	c:SetAttribute("Nazwa", p.nazwa)
	c:SetAttribute("Wariant", p.wariant)
	c:SetAttribute("Strefa", p.strefa.d.id)
	c:SetAttribute("Poziom", p.poziom)
	c:SetAttribute("Straznik", p.strefa.d.straznik == true)
	p.konfig = c
	zapiszAtrybuty(p)
	c.Parent = folderStanu
	ustawPotworow()
end

local function nowaGrupa(s: number, dlugosc: number, rezerwacja: boolean)
	return { s = s, sStare = s, dlugosc = dlugosc, rezerwacja = rezerwacja, czlonkowie = {} }
end

local function grupaZajeta(g): boolean
	for _, p in g.czlonkowie do
		if p.zajety then
			return true
		end
	end
	return false
end

local function usunZListy(lista, element)
	local i = table.find(lista, element)
	if i then
		table.remove(lista, i)
	end
end

-- punkt bazowy członka grupy na pętli
local function ustawNaPetli(st, p)
	local s = Logika.wGrupie(p.grupa.s, p.miejsce, st.d.odstepWGrupie, st.L)
	local x, y, z, yaw = Logika.punktTrasy(st.d.trasa, s)
	local dx, dz = x - p.x, z - p.z
	p.ruszyl = math.sqrt(dx * dx + dz * dz) > Stale.PROG_POZYCJI
	p.x, p.y, p.z, p.yaw = x, y, z, yaw
end

-- potwór znika (wygrana gracza albo haczyk „zabij”): grupa bez watahy znika, miejsce w watasze się zwalnia,
-- rezerwacja przepada; kolejkę odrodzeń uzupełni pętla odradzania (rozdz. 3.5)
local function usunPotwora(p)
	local st = p.strefa
	if p.grupa then
		if st.d.watahy then
			p.grupa.czlonkowie[p.miejsce] = nil
		else
			usunZListy(st.grupy, p.grupa)
		end
		p.grupa = nil
	end
	if p.rezerwacja then
		usunZListy(st.grupy, p.rezerwacja)
		p.rezerwacja = nil
	end
	usunZListy(st.potwory, p)
	if potwory[p.id] == p then
		potwory[p.id] = nil
		liczbaZywych -= 1
	end
	if p.konfig then
		p.konfig:Destroy()
		p.konfig = nil
	end
	ustawPotworow()
end

-- koniec zajętości (rozdz. 3.6): wygrana gracza → usunięty; przegrana → wraca do swojego stanu, grupa rusza
local function zakonczZajetosc(p)
	local z = p.zajety
	if not z then
		return
	end
	if z.wynik == "wygrana" then
		gadaj(string.format("%s pokonany — znika", p.id))
		usunPotwora(p)
	else
		p.zajety = nil
		zapiszAtrybuty(p)
	end
end

------------------------------------------------------------------ wejście na pętlę (rozdz. 3.3)
local function sprobujWejsc(st, p)
	local dom = st.d.domy[p.dom]
	if st.d.watahy then
		-- wolne miejsce dowolnej watahy w chwili, gdy przechodzi przez węzeł domu
		for _, g in st.grupy do
			for j = 1, st.d.miejsc do
				if g.czlonkowie[j] == nil then
					local sS = Logika.wGrupie(g.sStare, j, st.d.odstepWGrupie, st.L)
					local sN = Logika.wGrupie(g.s, j, st.d.odstepWGrupie, st.L)
					for _, sW in dom.s do
						if Logika.minal(sS, sN, sW, st.L) then
							g.czlonkowie[j] = p
							p.grupa, p.miejsce, p.stan = g, j, "chodzi"
							ustawNaPetli(st, p)
							gadaj(string.format("%s wchodzi do watahy (miejsce %d)", p.id, j))
							return
						end
					end
				end
			end
		end
		return
	end
	local sW = dom.s[1]
	-- 1. rezerwacja: jest miejsce na grupę i najbliższe czoło za węzłem jest co najmniej 25 z tyłu
	if not p.rezerwacja then
		local czola = {}
		for k, g in st.grupy do
			czola[k] = g.s
		end
		if #st.grupy < st.d.grupy and Logika.tylDo(sW, czola, st.L) >= ODSTEP then
			local g = nowaGrupa(sW, 0, true)
			table.insert(st.grupy, g)
			p.rezerwacja = g
		end
	end
	-- 2. wejście: ogon najbliższej grupy przed węzłem odszedł o 25
	if p.rezerwacja then
		local s, dl = {}, {}
		for _, g in st.grupy do
			if g ~= p.rezerwacja then
				table.insert(s, g.s)
				table.insert(dl, g.dlugosc)
			end
		end
		if Logika.przodDo(sW, s, dl, st.L) >= ODSTEP then
			local g = p.rezerwacja
			g.rezerwacja = false
			g.czlonkowie[1] = p
			p.grupa, p.miejsce, p.stan, p.rezerwacja = g, 1, "chodzi", nil
			ustawNaPetli(st, p)
			gadaj(string.format("%s wchodzi na pętlę", p.id))
		end
	end
end

------------------------------------------------------------------ tyknięcie ruchu (rozdz. 3.2)
local function lukaTeraz(st): number
	local prawdziwe = {}
	for _, g in st.grupy do
		if not g.rezerwacja then
			table.insert(prawdziwe, g)
		end
	end
	if st.L <= 0 or #prawdziwe == 0 or (#prawdziwe == 1 and prawdziwe[1].dlugosc <= 0) then
		return math.huge
	end
	local najmniej = math.huge
	for _, g in prawdziwe do
		local luka = st.L - g.dlugosc
		for _, k in prawdziwe do
			if k ~= g then
				luka = math.min(luka, Logika.przod(g.s, k.s, st.L) - k.dlugosc)
			end
		end
		najmniej = math.min(najmniej, luka)
	end
	return najmniej
end

------------------------------------------------------------------ zatrzymanie przy graczu (17.11.2026, propozycja)
-- Potwór, do którego gracz podszedł na zasięg podpowiedzi E (+ Stale.ZATRZYMANIE_ZAPAS), staje i obraca się do
-- najbliższego gracza, dopóki ten jest blisko — najwyżej Stale.ZATRZYMANIE_MAKS_S naraz, potem idzie co najmniej
-- Stale.ZATRZYMANIE_PRZERWA_S (nie da się go zamrozić). Grupa z zatrzymanym członkiem stoi jak grupa z zajętym
-- (ta sama droga w Logika.krokGrup, więc odstęp 25 i pętle działają jak przy walce). Strażnik (prędkość 0) — bez zmian.
local function najblizszyGracz(p, gracze, zasieg: number)
	local najlepszy, dNaj = nil, math.huge
	for _, g in gracze do
		local dx, dz = g[1] - p.x, g[2] - p.z
		local d = math.sqrt(dx * dx + dz * dz)
		if d <= zasieg and d < dNaj and math.abs(g[3] - p.y) <= Stale.MAKS_ROZNICA_WYSOKOSCI + Stale.ZATRZYMANIE_ZAPAS then
			najlepszy, dNaj = g, d
		end
	end
	return najlepszy
end

local function aktualizujZatrzymania(st, czas: number, gracze)
	local zasieg = Stale.ZASIEG_E + st.gatunek.promien + Stale.ZATRZYMANIE_ZAPAS
	for _, p in st.potwory do
		if p.zajety or st.v <= 0 or st.d.straznik or #gracze == 0 then
			p.stop = nil
		else
			local cel = najblizszyGracz(p, gracze, zasieg)
			if p.stop and (not cel or czas - p.stop.od >= Stale.ZATRZYMANIE_MAKS_S) then
				if cel then
					p.stopWolnyOd = czas + Stale.ZATRZYMANIE_PRZERWA_S
				end
				p.stop = nil
			elseif cel and not p.stop and czas >= (p.stopWolnyOd or 0) then
				p.stop = { od = czas }
			end
			if p.stop then
				local dx, dz = cel[1] - p.x, cel[2] - p.z
				if dx * dx + dz * dz > 1e-6 then
					p.yaw = Logika.yaw(dx, dz)
				end
			end
		end
	end
end

local function grupaZatrzymana(g): boolean
	for _, p in g.czlonkowie do
		if p.stop then
			return true
		end
	end
	return false
end

local function tyknijStrefe(st, czas: number, dt: number, gracze)
	-- 1. koniec zajętości (zbieramy najpierw, bo usuwanie zmienia listę)
	local konczace = {}
	for _, p in st.potwory do
		if p.zajety and czas >= p.zajety.koniec then
			table.insert(konczace, p)
		end
	end
	for _, p in konczace do
		zakonczZajetosc(p)
	end
	aktualizujZatrzymania(st, czas, gracze)
	local krok = st.v * dt
	-- 2. grupy: jeden krok z odstępem 25; stoi rezerwacja i grupa z zajętym albo zatrzymanym członkiem
	if #st.grupy > 0 then
		local s, dl, stoi = {}, {}, {}
		for k, g in st.grupy do
			s[k] = g.s
			dl[k] = g.dlugosc
			stoi[k] = g.rezerwacja or grupaZajeta(g) or grupaZatrzymana(g)
		end
		local nowe, zbiezne = Logika.krokGrup(s, dl, stoi, st.L, krok, ODSTEP)
		if not zbiezne and not st.ostrzezono then
			st.ostrzezono = true
			warn(P .. "strefa " .. st.d.id .. ": krokGrup się nie zbiegł (złe położenia grup?) — grupy stoją w tym tyknięciu")
		end
		for k, g in st.grupy do
			g.sStare = g.s
			g.s = nowe[k]
		end
	end
	-- 3. członkowie grup: punkt i kierunek z pętli (zajęty stoi tam, gdzie zaczęła się walka)
	for _, g in st.grupy do
		for _, p in g.czlonkowie do
			if p.zajety or p.stop then
				p.ruszyl = false -- zatrzymany: stoi i patrzy na gracza (kierunek z aktualizujZatrzymania)
			else
				ustawNaPetli(st, p)
			end
		end
	end
	-- 4. wychodzący z domu: po prostej do przedpola
	for _, p in st.potwory do
		if p.stan == "wychodzi" and not p.zajety and not p.stop then
			local dom = st.d.domy[p.dom]
			local cx, cz = dom.wejscie[1], dom.wejscie[2]
			local x2, z2, doszedl = Logika.krokDo(p.x, p.z, cx, cz, krok)
			local dx, dz = x2 - p.x, z2 - p.z
			if dx * dx + dz * dz > 1e-6 then
				p.yaw = Logika.yaw(dx, dz)
			end
			p.x, p.z, p.y = x2, z2, dom.y
			if doszedl then
				p.stan = "czeka"
				-- twarzą do węzła
				local wx, wz = st.d.trasa.x[dom.wezel] - cx, st.d.trasa.z[dom.wezel] - cz
				if wx * wx + wz * wz > 1e-6 then
					p.yaw = Logika.yaw(wx, wz)
				end
				gadaj(string.format("%s czeka w przedpolu", p.id))
			end
		end
	end
	-- 5. czekający: rezerwacja i wejście
	for _, p in st.potwory do
		if p.stan == "czeka" and not p.zajety and not p.stop then
			sprobujWejsc(st, p)
		end
	end
	-- 6. atrybuty (tylko zmiany) i kontrola odstępu
	for _, p in st.potwory do
		zapiszAtrybuty(p)
	end
	st.minLuka = math.min(st.minLuka, lukaTeraz(st))
end

-- położenia graczy dla zatrzymań: { x, z, y } (bez graczy zablokowanych, np. w czasie przelotu kamery)
local function graczeDoZatrzyman(): { { number } }
	local lista = {}
	for _, gracz in Players:GetPlayers() do
		local postac = gracz.Character
		local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
		local hum = postac and postac:FindFirstChildOfClass("Humanoid")
		if hrp and hrp:IsA("BasePart") and hum and hum.Health > 0 and gracz:GetAttribute(Stale.ATRYBUT_BLOKADY) ~= true then
			table.insert(lista, { hrp.Position.X, hrp.Position.Z, hrp.Position.Y })
		end
	end
	return lista
end

local function tyknij(dt: number)
	local czas = teraz()
	local gracze = if kontener:GetAttribute(Stale.ATRYBUT_BEZ_ZATRZYMAN) == true then {} else graczeDoZatrzyman()
	for _, st in strefy do
		tyknijStrefe(st, czas, dt, gracze)
	end
end

------------------------------------------------------------------ gracze i odradzanie (rozdz. 3.5)
local function liczbaGraczy(): number
	local test = kontener:GetAttribute("TestGraczy")
	if type(test) == "number" and test >= 1 then
		return math.floor(test)
	end
	return math.max(1, #Players:GetPlayers())
end

-- położenia graczy w poziomie: { {x, z} }
local function graczeXZ(): { { number } }
	local lista = {}
	for _, gracz in Players:GetPlayers() do
		local postac = gracz.Character
		local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
		if hrp and hrp:IsA("BasePart") then
			table.insert(lista, { hrp.Position.X, hrp.Position.Z })
		end
	end
	return lista
end

local function graczeWStrefie(st, gracze: { { number } }): number
	local n = 0
	local cx, cz = st.d.srodek[1], st.d.srodek[3]
	for _, g in gracze do
		local dx, dz = g[1] - cx, g[2] - cz
		if math.sqrt(dx * dx + dz * dz) <= st.d.zasiegGraczy then
			n += 1
		end
	end
	return n
end

local function odradzaj()
	local czas = teraz()
	local G = liczbaGraczy()
	kontener:SetAttribute("Graczy", G)
	local gracze = graczeXZ()
	local wraca = 0
	for _, st in strefy do
		st.cel = if st.d.straznik then 1 else Logika.cel(st.d.naraz, st.d.max, G)
		local brak = st.cel - #st.potwory - #st.kolejka
		if brak > 0 then
			local zaIle = if st.d.straznik or st.d.odrodzenieStale == true
				then st.d.odrodzenieS
				else Logika.czasOdrodzenia(st.d.odrodzenieS, graczeWStrefie(st, gracze))
			for _ = 1, brak do
				table.insert(st.kolejka, czas + zaIle)
			end
			table.sort(st.kolejka)
		end
		while #st.kolejka > 0 and st.kolejka[1] <= czas do
			if #st.potwory >= st.cel then
				table.remove(st.kolejka, 1) -- graczy ubyło: wpis przepada
			else
				-- Strażnik nie ma domu z potwory.json: blokada 0 (wraca zawsze po 120 s; patrz nagłówek)
				local blokada = if st.d.straznik then 0 else BLOKADA_DOMU
				local i = Logika.wolnyDom(st.domyXZ, gracze, st.ostatniDom, blokada)
				if not i then
					break -- każdy dom ma gracza bliżej niż 18: wpis czeka do następnej sekundy
				end
				table.remove(st.kolejka, 1)
				st.ostatniDom = i
				local p = utworzPotwora(st, "wychodzi", i)
				opublikuj(p)
				gadaj(string.format("odrodzenie %s w domu %d strefy %s (poz. %d)", p.id, i, st.d.id, p.poziom))
			end
		end
		if st.d.straznik and #st.kolejka > 0 then
			wraca = st.kolejka[1]
		end
	end
	if kontener:GetAttribute("StraznikWraca") ~= wraca then
		kontener:SetAttribute("StraznikWraca", wraca)
	end
end

------------------------------------------------------------------ start stref (rozdz. 3.4)
local function przygotujStrefy()
	local G = liczbaGraczy()
	kontener:SetAttribute("Graczy", G)
	for _, d in DanePotworow.strefy do
		local gat = DanePotworow.gatunki[d.gatunek]
		local domyXZ = {}
		for i, dom in d.domy do
			domyXZ[i] = { dom.x, dom.z }
		end
		local st = {
			d = d,
			gatunek = gat,
			v = gat.predkosc,
			L = d.trasa.L,
			grupy = {},
			potwory = {},
			kolejka = {},
			domyXZ = domyXZ,
			licznik = 0,
			ostatniDom = 0,
			cel = if d.straznik then 1 else Logika.cel(d.naraz, d.max, G),
			minLuka = math.huge,
			ostrzezono = false,
		}
		table.insert(strefy, st)
		if d.watahy then
			local dlugosc = (d.miejsc - 1) * d.odstepWGrupie
			for _, s in Logika.poczatkowePolozenia(d.grupy, st.L) do
				table.insert(st.grupy, nowaGrupa(s, dlugosc, false))
			end
			for _, para in Logika.rozdzialStartowy(st.cel, d.grupy, d.miejsc) do
				local p = utworzPotwora(st, "chodzi", 1)
				local g = st.grupy[para[1]]
				g.czlonkowie[para[2]] = p
				p.grupa, p.miejsce = g, para[2]
				ustawNaPetli(st, p)
				p.ruszyl = false
				opublikuj(p)
			end
		else
			for _, s in Logika.poczatkowePolozenia(st.cel, st.L) do
				local g = nowaGrupa(s, 0, false)
				table.insert(st.grupy, g)
				local p = utworzPotwora(st, "chodzi", 1)
				g.czlonkowie[1] = p
				p.grupa, p.miejsce = g, 1
				ustawNaPetli(st, p)
				p.ruszyl = false
				opublikuj(p)
			end
		end
	end
end

------------------------------------------------------------------ kontrola BiomLas (rozdz. 1.3)
local function wektor(t): Vector3
	return Vector3.new(t[1], t[2], t[3])
end

local function opisWektora(v: Vector3): string
	return string.format("(%.1f, %.1f, %.1f)", v.X, v.Y, v.Z)
end

-- → (StanBiomu, opis)
local function kontrolaBiomu(): (string, string)
	if kontener:GetAttribute("TestBezBiomu") == true then
		return "ok", "kontrola BiomLas pominięta (TestBezBiomu = true) — potwory chodzą po pustym miejscu"
	end
	local b = DanePotworow.biom
	local biom = workspace:WaitForChild(b.nazwa, 15)
	if not biom then
		return "brak_biomu", "nie ma Workspace/" .. b.nazwa .. " (czekano 15 s) — potwory nie wystartują"
	end
	if biom:GetAttribute("Wygenerowane") ~= true then
		return "brak_biomu", b.nazwa .. " nie ma atrybutu Wygenerowane = true — potwory nie wystartują"
	end
	if not b.plyta then
		return "ok", b.nazwa .. " na miejscu (dane bez Płyty — położenia nie sprawdzam)"
	end
	local plyta: Instance? = biom
	for _, nazwa in string.split(b.plyta.sciezka, "/") do
		plyta = if plyta then plyta:FindFirstChild(nazwa) else nil
	end
	if not plyta or not plyta:IsA("BasePart") then
		return "brak_biomu", "brak " .. b.nazwa .. "/" .. b.plyta.sciezka .. " — potwory nie wystartują"
	end
	local czesc = plyta :: BasePart
	local chcePoz, chceRozm = wektor(b.plyta.pozycja), wektor(b.plyta.rozmiar)
	local poz, rozm = czesc.Position, czesc.Size
	local function blisko(a: Vector3, c: Vector3): boolean
		return math.abs(a.X - c.X) <= 0.5 and math.abs(a.Y - c.Y) <= 0.5 and math.abs(a.Z - c.Z) <= 0.5
	end
	if not blisko(poz, chcePoz) then
		return "zle_polozenie", "Płyta w " .. opisWektora(poz) .. " zamiast " .. opisWektora(chcePoz) .. " — potwory nie wystartują"
	end
	if not blisko(rozm, chceRozm) then
		return "zle_polozenie", "Płyta ma rozmiar " .. opisWektora(rozm) .. " zamiast " .. opisWektora(chceRozm) .. " — potwory nie wystartują"
	end
	if math.abs(math.abs(czesc.Orientation.Y) - b.obrotY) > 1 then
		return "zle_polozenie", string.format("Płyta obrócona o %.1f° zamiast ±%d° — potwory nie wystartują", czesc.Orientation.Y, b.obrotY)
	end
	return "ok", "BiomLas na miejscu"
end

------------------------------------------------------------------ szablony aktorów (rozdz. 4.3)
local function kopiujSzablony(): boolean
	local stary = ReplicatedStorage:FindFirstChild(Stale.NAZWA_SZABLONOW)
	if stary then
		if stary:GetAttribute("Wygenerowane") == true then
			stary:Destroy()
		else
			warn(P .. "ReplicatedStorage/" .. Stale.NAZWA_SZABLONOW .. " istnieje i nie jest nasz (brak Wygenerowane) — nie ruszam go; klient pokaże bryły zastępcze")
			return false
		end
	end
	local proto = workspace:WaitForChild(Stale.NAZWA_PROTOTYPU, 10)
	local aktorzy = if proto then proto:WaitForChild("Aktorzy", 10) else nil
	if not aktorzy then
		warn(P .. "brak Workspace/" .. Stale.NAZWA_PROTOTYPU .. "/Aktorzy — bez szablonów; klient pokaże bryły zastępcze")
		return false
	end
	local folder = Instance.new("Folder")
	folder.Name = Stale.NAZWA_SZABLONOW
	folder:SetAttribute("Wygenerowane", true)
	folder:SetAttribute("Zrodlo", "swiat/las_potwory (kopia " .. Stale.NAZWA_PROTOTYPU .. "/Aktorzy w Play)")
	local brak = {}
	for _, klucz in Stale.SZABLONY do
		local wzor = aktorzy:FindFirstChild(klucz)
		local kopia: Instance? = nil
		if wzor then
			local udalo, wynik = pcall(function()
				return wzor:Clone()
			end)
			if udalo then
				kopia = wynik
			end
		end
		if kopia then
			kopia.Parent = folder
		else
			table.insert(brak, klucz)
		end
	end
	folder.Parent = ReplicatedStorage
	kontener.Destroying:Connect(function()
		folder:Destroy()
	end)
	if #brak > 0 then
		warn(P .. "nie skopiowano szablonów: " .. table.concat(brak, ", ") .. " — klient pokaże bryły zastępcze")
		return false
	end
	return true
end

------------------------------------------------------------------ zgodność logiki (rozdz. 3.7a)
local function sprawdzLogike(): (boolean, number, { string })
	local udalo, ok, n, bledy = pcall(Logika.sprawdzPrzypadki)
	if not udalo then
		return false, 0, { "sprawdzPrzypadki zgłosiło błąd: " .. tostring(ok) }
	end
	return ok, n, bledy
end

------------------------------------------------------------------ walka (rozdz. 5.1)
local KLASY = {}
for _, k in Wzorcowe.KLASY do
	KLASY[k] = true
end
local POZIOMY = {}
for _, p in Stale.POZIOMY_BOHATERA do
	POZIOMY[p] = true
end

local ostatniaProsba: { [Player]: number } = {}
local walkaDo: { [Player]: number } = {}
local arenaDo: { [Player]: number } = {}

-- Poprawka wdrożenia (15.11, Studio): miejsce ma StreamOutBehavior = Opportunistic, więc jedna prośba
-- RequestStreamAroundAsync wczytuje arenę prototypu tylko na chwilę — postać stoi 2000+ studów dalej i silnik
-- zaraz ją wypycha; odtwarzacz pokazywał wtedy walkę na gołej płycie Baseplate (bez podestu, polany i lasu areny).
-- Dlatego serwer ponawia prośbę co PODTRZYMANIE_CO s, dopóki trwa odtwarzanie (walka.czas + PODTRZYMANIE_ARENY).
-- Jeden wątek na gracza; kolejna walka tylko przesuwa koniec.
local function podtrzymajArene(gracz: Player, doKiedy: number)
	local trwa = arenaDo[gracz] ~= nil
	arenaDo[gracz] = math.max(arenaDo[gracz] or 0, doKiedy)
	if trwa then
		return
	end
	task.spawn(function()
		while gracz.Parent and arenaDo[gracz] and teraz() < arenaDo[gracz] do
			task.wait(Stale.PODTRZYMANIE_CO)
			pcall(function()
				gracz:RequestStreamAroundAsync(Stale.ARENA_PROTOTYPU, 2)
			end)
		end
		arenaDo[gracz] = nil
	end)
end

local function wybierzZiarno(): number
	local wymuszone = kontener:GetAttribute("ZiarnoTestowe")
	if type(wymuszone) == "number" and wymuszone >= 1 and wymuszone < 2147483647 then
		return math.floor(wymuszone)
	end
	return generator:NextInteger(1, 2147483646)
end

-- tylko trzy pola, tylko napisy z zamkniętych list (D-016) → (klasa, id potwora, poziom-napis) albo nil
local function sprawdzWybor(wybor: any): (string?, string?, string?)
	if type(wybor) ~= "table" then
		return nil
	end
	local klasa, przeciwnik, poziom = rawget(wybor, "klasa"), rawget(wybor, "przeciwnik"), rawget(wybor, "poziom")
	if type(klasa) ~= "string" or type(przeciwnik) ~= "string" or type(poziom) ~= "string" then
		return nil
	end
	if not KLASY[klasa] or not POZIOMY[poziom] then
		return nil
	end
	if #przeciwnik > 32 or not string.match(przeciwnik, "^[%w_]+%-%d+$") then
		return nil
	end
	return klasa, przeciwnik, poziom
end

local function odmowa(powod: string, ponowZa: number?)
	if ponowZa then
		return { ok = false, powod = powod, ponowZa = ponowZa }
	end
	return { ok = false, powod = powod }
end

------------------------------------------------------------------ stan gracza (17.11.2026, swiat/stan_gracza, propozycja)
-- Gdy w Workspace jest kontener Stale.KONTENER_STANU (Wygenerowane = true), bohater walki jest z danych gracza, a łup
-- trafia do gracza (Sygnaly tego kontenera). Atrybut kontenera lasu Stale.ATRYBUT_TESTU_BOHATERA = true przywraca regułę
-- testową T1 (klasa i poziom z panelu klienta, bez łupu). Bez kontenera albo przy błędzie — wszystko jak dawniej.
local function sygnalStanu(nazwa: string): BindableFunction?
	if kontener:GetAttribute(Stale.ATRYBUT_TESTU_BOHATERA) == true then
		return nil
	end
	local k = workspace:FindFirstChild(Stale.KONTENER_STANU)
	if not k or k:GetAttribute("Wygenerowane") ~= true then
		return nil
	end
	local s = k:FindFirstChild("Sygnaly")
	local f = s and s:FindFirstChild(nazwa)
	if f and f:IsA("BindableFunction") then
		return f
	end
	return nil
end

-- opis bohatera z danych gracza albo nil (wtedy postać wzorcowa z reguły T1)
local function bohaterZeStanu(gracz: Player): any
	local f = sygnalStanu(Stale.SYGNAL_BOHATERA)
	if not f then
		return nil
	end
	local udalo, opis = pcall(function()
		return f:Invoke(gracz)
	end)
	if udalo and type(opis) == "table" and type(opis.klasa) == "string" and type(opis.poziom) == "number" then
		return opis
	end
	warn(P .. "stan gracza nie podał bohatera — postać wzorcowa: " .. tostring(opis))
	return nil
end

-- łup walki do gracza (tylko gdy bohater był z danych gracza); błąd stanu nie psuje walki
local function nagrodaZaWalke(gracz: Player, p: any, walka: any)
	local f = sygnalStanu(Stale.SYGNAL_LUPU)
	if not f then
		return
	end
	local udalo, wynik = pcall(function()
		return f:Invoke(gracz, { lup = walka.lup, wynik = walka.wynik, czas = walka.czas, zrodlo = kontener.Name,
			gatunek = p.gatunek, poziom = p.poziom })
	end)
	if not udalo or type(wynik) ~= "table" or wynik.ok ~= true then
		warn(P .. "stan gracza nie przyjął łupu: " .. tostring(if udalo and type(wynik) == "table" then wynik.powod else wynik))
	end
end

zdalna.OnServerInvoke = function(gracz: Player, wybor: any)
	-- 1. nie częściej niż raz na ODSTEP_PROSB s (także odrzucona)
	local zegar = os.clock()
	local poprzednio = ostatniaProsba[gracz]
	if poprzednio and zegar - poprzednio < Stale.ODSTEP_PROSB then
		return odmowa("za_szybko", Stale.ODSTEP_PROSB - (zegar - poprzednio))
	end
	ostatniaProsba[gracz] = zegar

	-- 2. wybór z listy i żywy potwór z rejestru
	if not gotowy then
		return odmowa("zly_wybor")
	end
	local klasa, id, poziomNapis = sprawdzWybor(wybor)
	if not klasa or not id or not poziomNapis then
		return odmowa("zly_wybor")
	end
	local p = potwory[id]
	if not p then
		return odmowa("zly_wybor")
	end

	-- 3. postać żyje
	local postac = gracz.Character
	local hrp = postac and postac:FindFirstChild("HumanoidRootPart")
	local hum = postac and postac:FindFirstChildOfClass("Humanoid")
	if not hrp or not hrp:IsA("BasePart") or not hum or hum.Health <= 0 then
		return odmowa("brak_postaci")
	end
	-- postać zablokowana przez inny skrypt serwera (np. przelot kamery lasu-pasa) — bez walk
	if gracz:GetAttribute(Stale.ATRYBUT_BLOKADY) == true then
		return odmowa("brak_postaci")
	end

	-- 4. poprzednia walka gracza skończyła się (pełny czas ×1)
	local czas = teraz()
	local koniec = walkaDo[gracz]
	if koniec and czas < koniec and kontener:GetAttribute("TestBezSesji") ~= true then
		return odmowa("walka_trwa", koniec - czas)
	end

	-- 5. zajętość: inny gracz albo ten sam po wygranej → zly_wybor; ten sam po przegranej → rewanż dozwolony
	if p.zajety and (p.zajety.gracz ~= gracz or p.zajety.wynik == "wygrana") then
		return odmowa("zly_wybor")
	end

	-- 6. odległość w poziomie i różnica wysokości (zapas serwera na opóźnienie i ruch 4 Hz)
	local promien = DanePotworow.gatunki[p.gatunek].promien
	local pozGracza = (hrp :: BasePart).Position
	local dx, dz = pozGracza.X - p.x, pozGracza.Z - p.z
	if math.sqrt(dx * dx + dz * dz) > Stale.ZASIEG_E + promien + Stale.ZAPAS_E_SERWER
		or math.abs(pozGracza.Y - p.y) > Stale.MAKS_ROZNICA_WYSOKOSCI
	then
		return odmowa("za_daleko")
	end

	-- 7. bohater z danych gracza (swiat/stan_gracza) albo wzorcowy (reguła testowa T1, rozdz. 5.2); przeciwnik z rejestru
	local poziomBohatera = if poziomNapis == "auto" then p.poziom else (tonumber(poziomNapis) :: number)
	local zeStanu = bohaterZeStanu(gracz)
	local bohater = zeStanu or Wzorcowe.postac(klasa, poziomBohatera)
	if zeStanu then
		klasa, poziomBohatera = zeStanu.klasa, zeStanu.poziom
	end
	local ziarno = wybierzZiarno()

	-- 8. walka silnikiem v2 (łup liczy silnik w tym samym wywołaniu)
	local udalo, walka = pcall(Silnik.symuluj, bohater, { potwor = p.gatunek, poziom = p.poziom }, ziarno)
	if not udalo or type(walka) ~= "table" then
		warn(P .. "silnik walki zgłosił błąd: " .. tostring(walka))
		return odmowa("blad_silnika")
	end

	-- 9. blokada sesji gracza i zajętość potwora (rozdz. 3.6)
	walkaDo[gracz] = czas + walka.czas - Stale.ZAPAS_SESJI
	if kontener:GetAttribute("TestBezSesji") == true then
		walkaDo[gracz] = czas
	end
	p.zajety = { gracz = gracz, wynik = walka.wynik, koniec = czas + walka.czas + Stale.ZAPAS_ZAJETOSCI }
	p.ruszyl = false
	zapiszAtrybuty(p)

	-- Łup (walka.lup) przyznaje stan gracza (swiat/stan_gracza) — tylko bohaterowi z danych gracza; w trybie testowym T1
	-- i bez kontenera StanGracza niczego nie zapisujemy (jak dawniej).
	if zeStanu then
		nagrodaZaWalke(gracz, p, walka)
	end
	local opis =string.format("%s/%s/%s→%d/%s", p.id, klasa, poziomNapis, poziomBohatera, walka.wynik)
	kontener:SetAttribute("SerwerLicznikWalk", (kontener:GetAttribute("SerwerLicznikWalk") or 0) + 1)
	kontener:SetAttribute("SerwerOstatniaWalka", opis)
	kontener:SetAttribute("SerwerOstatnieZiarno", ziarno)
	local sekundy = string.gsub(string.format("%.1f", walka.czas), "%.", ",")
	print(string.format("%swalka %s %s/%s→%d %s %d → %s, %s s", P, p.id, klasa, poziomNapis, poziomBohatera, p.gatunek,
		p.poziom, walka.wynik, sekundy))
	if sygnalWyniku and sygnalWyniku:IsA("BindableEvent") then
		local info = { id = p.id, strefa = p.strefa.d.id, gatunek = p.gatunek, straznik = p.strefa.d.straznik == true,
			wynik = walka.wynik, poziom = p.poziom, koniec = p.zajety.koniec }
		local udaloSie, bladSygnalu = pcall(function()
			sygnalWyniku:Fire(gracz, info)
		end)
		if not udaloSie then
			warn(P .. "sygnał wyniku walki zgłosił błąd: " .. tostring(bladSygnalu))
		end
	end

	-- 10. arena prototypu musi być wczytana u klienta, zanim odtwarzacz ruszy (gracz stoi 2000+ studów dalej)
	pcall(function()
		gracz:RequestStreamAroundAsync(Stale.ARENA_PROTOTYPU, 3)
	end)
	podtrzymajArene(gracz, czas + walka.czas + Stale.PODTRZYMANIE_ARENY)

	-- 11. odpowiedź (jedyne liczby to te, które prototyp już przyjmuje)
	return { ok = true, walka = walka, nastepnaOd = walkaDo[gracz] }
end

------------------------------------------------------------------ wyjście gracza (rozdz. 3.6)
Players.PlayerRemoving:Connect(function(gracz: Player)
	ostatniaProsba[gracz] = nil
	walkaDo[gracz] = nil
	arenaDo[gracz] = nil
	local jego = {}
	for _, p in potwory do
		if p.zajety and p.zajety.gracz == gracz then
			table.insert(jego, p)
		end
	end
	for _, p in jego do
		local udalo, blad = xpcall(function()
			zakonczZajetosc(p)
		end, debug.traceback)
		if not udalo then
			warn(P .. "błąd przy końcu zajętości po wyjściu gracza: " .. tostring(blad))
		end
	end
end)

------------------------------------------------------------------ pomiar kosztu pętli (wdrożenie 15.11; tylko do testów)
-- koszt[nazwa] = { suma, n, maks } w sekundach; haczyk „koszt” zwraca średnią i maksimum w ms, „koszt”, true zeruje
local koszt: { [string]: { number } } = {}
local kosztOd = os.clock()
local function zmierz(nazwa: string, s: number)
	local k = koszt[nazwa]
	if not k then
		k = { 0, 0, 0 }
		koszt[nazwa] = k
	end
	k[1] += s
	k[2] += 1
	if s > k[3] then
		k[3] = s
	end
end

local function opisKosztu(zeruj: any)
	local wynik = { okno = os.clock() - kosztOd }
	for nazwa, k in koszt do
		wynik[nazwa] = { sr = if k[2] > 0 then k[1] / k[2] * 1000 else 0, maks = k[3] * 1000, n = k[2] }
	end
	if zeruj == true then
		table.clear(koszt)
		kosztOd = os.clock()
	end
	return wynik
end

------------------------------------------------------------------ haczyk testowy (rozdz. 8.6)
local function opisStref()
	local wynik = {}
	local czas = teraz()
	for _, st in strefy do
		local grupy = {}
		for _, g in st.grupy do
			table.insert(grupy, { g.s, g.dlugosc, g.rezerwacja or grupaZajeta(g) })
		end
		local kolejka = {}
		for _, t in st.kolejka do
			table.insert(kolejka, math.max(0, t - czas))
		end
		local czekajacy, wychodzacy = 0, 0
		for _, p in st.potwory do
			if p.stan == "czeka" then
				czekajacy += 1
			elseif p.stan == "wychodzi" then
				wychodzacy += 1
			end
		end
		wynik[st.d.id] = {
			cel = st.cel,
			istnieje = #st.potwory,
			kolejka = kolejka, -- sekundy do kolejnych odrodzeń
			grupy = grupy, -- { s, dlugosc, stoi }
			minLuka = st.minLuka, -- najmniejsza luka czoło → ogon od startu (math.huge: brak dwóch grup)
			minLukaTeraz = lukaTeraz(st),
			czekajacy = czekajacy,
			wychodzacy = wychodzacy,
		}
	end
	return wynik
end

local function opisPotwora(id: any)
	local p = potwory[id]
	if not p then
		return nil
	end
	local indeks = 0
	if p.grupa then
		indeks = table.find(p.strefa.grupy, p.grupa) or 0
	end
	return {
		id = p.id,
		strefa = p.strefa.d.id,
		gatunek = p.gatunek,
		poziom = p.poziom,
		stan = p.stan,
		stanAtrybutu = stanAtrybutu(p),
		grupa = indeks,
		miejsce = p.miejsce,
		s = if p.grupa then Logika.wGrupie(p.grupa.s, p.miejsce, p.strefa.d.odstepWGrupie, p.strefa.L) else -1,
		pozycja = Vector3.new(p.x, p.y, p.z),
		zajetyDo = if p.zajety then p.zajety.koniec else 0,
		zajetyPrzez = if p.zajety then p.zajety.gracz.Name else "",
		wynik = if p.zajety then p.zajety.wynik else "",
	}
end

sterowanie.OnInvoke = function(polecenie: string, a: any)
	if polecenie == "strefy" then
		return opisStref()
	elseif polecenie == "potwor" then
		return opisPotwora(a)
	elseif polecenie == "zabij" then
		local p = potwory[a]
		if not p then
			return false
		end
		usunPotwora(p)
		return true
	elseif polecenie == "gracze" then
		kontener:SetAttribute("TestGraczy", if type(a) == "number" then a else nil)
		return liczbaGraczy()
	elseif polecenie == "zgodnosc" then
		local ok, n, bledy = sprawdzLogike()
		return { ok = ok, n = n, bledy = bledy }
	elseif polecenie == "koszt" then
		return opisKosztu(a)
	end
	warn(P .. "SterowanieSerwera: nieznane polecenie " .. tostring(polecenie))
	return nil
end

-- pominięcie walki (D-078, wybór 1 → opcja A, przyjęte na noc 17.11.2026): serwer prototypu woła ten uchwyt
-- (BindableFunction — tylko serwer) po przyjętym pominięciu; gracz i jego potwór są wolni od razu
local zwolnij = kontener:WaitForChild("Sygnaly"):FindFirstChild("ZwolnijPoPominieciu")
if zwolnij and zwolnij:IsA("BindableFunction") then
	zwolnij.OnInvoke = function(gracz: Player)
		if typeof(gracz) ~= "Instance" or not gracz:IsA("Player") then
			return false
		end
		local czas = teraz()
		walkaDo[gracz] = czas
		for _, p in potwory do
			if p.zajety and p.zajety.gracz == gracz then
				p.zajety.koniec = czas -- pętla ruchu zamknie zajętość w ciągu 0,25 s (wygrana: potwór znika)
			end
		end
		return true
	end
end

------------------------------------------------------------------ pętle z ochroną przed błędami (rozdz. 8.5)
local function petla(nazwa: string, okres: number, krok: (number) -> ())
	task.spawn(function()
		local bledyZRzedu = 0
		while kontener.Parent do
			local dt = math.min(task.wait(okres), 0.5)
			local t0 = os.clock()
			local udalo, blad = xpcall(function()
				krok(dt)
			end, debug.traceback)
			zmierz(nazwa, os.clock() - t0)
			if udalo then
				bledyZRzedu = 0
			else
				bledyZRzedu += 1
				warn(P .. "błąd w pętli " .. nazwa .. ": " .. tostring(blad))
				if bledyZRzedu >= 10 then
					warn(P .. "pętla " .. nazwa .. " zatrzymana po 10 błędach z rzędu — nowe walki odrzucane (zly_wybor)")
					-- bez pętli ruchu zajętość nigdy by się nie skończyła: nie przyjmujemy więcej walk
					gotowy = false
					kontener:SetAttribute("SerwerGotowy", false)
					break
				end
			end
		end
	end)
end

------------------------------------------------------------------ start
kontener:SetAttribute("SerwerGotowy", false)
kontener:SetAttribute("SzablonyGotowe", false)
kontener:SetAttribute("StanBiomu", nil)
kontener:SetAttribute("Potworow", 0)
kontener:SetAttribute("Graczy", liczbaGraczy())
kontener:SetAttribute("SerwerLicznikWalk", 0)
kontener:SetAttribute("StraznikWraca", 0)
for _, c in folderStanu:GetChildren() do
	c:Destroy() -- Stan jest nasz i w Edit pusty; resztki po czymkolwiek usuwamy
end

local okLogiki, nLogiki, bledyLogiki = sprawdzLogike()
local zgodnosc = string.format("OK %d/%d", nLogiki, nLogiki)
if not okLogiki then
	zgodnosc = string.format("BŁĄD %d/%d: %s", nLogiki - #bledyLogiki, nLogiki, tostring(bledyLogiki[1]))
	warn(P .. "zgodność logiki: " .. zgodnosc)
end
kontener:SetAttribute("ZgodnoscLogiki", zgodnosc)

local stanBiomu, opisBiomu = kontrolaBiomu()
kontener:SetAttribute("StanBiomu", stanBiomu)
if stanBiomu ~= "ok" then
	warn(P .. opisBiomu)
	return -- zero potworów; zdalna funkcja i haczyk działają (odpowiadają „zly_wybor” / puste strefy)
end
if kontener:GetAttribute("TestBezBiomu") == true then
	warn(P .. opisBiomu)
end

kontener:SetAttribute("SzablonyGotowe", kopiujSzablony())

przygotujStrefy()
gotowy = true

petla("ruchu", Stale.OKRES_RUCHU, tyknij)
petla("odradzania", Stale.OKRES_ODRADZANIA, function(_dt: number)
	odradzaj()
end)

-- nazwa strażnika z danych biomu (17.11.2026: Bagno pisało „Strażnik Gaju”, bo nazwa była wpisana na sztywno)
local zwykle, straznicy = 0, {}
for _, st in strefy do
	if st.d.straznik then
		table.insert(straznicy, if st.d.wariant then st.d.wariant.nazwa else st.gatunek.nazwa)
	else
		zwykle += #st.potwory
	end
end
print(string.format("%sgotowy: %d potworów w %d strefach + %s; zgodność logiki %d/%d", P, zwykle,
	#strefy - #straznicy, if #straznicy > 0 then table.concat(straznicy, ", ") else "bez strażnika",
	nLogiki - #bledyLogiki, nLogiki))
kontener:SetAttribute("SerwerGotowy", true)
