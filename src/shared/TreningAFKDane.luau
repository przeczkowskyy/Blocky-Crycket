--!strict
--[[
	TreningAFKDane — ustawienia treningu na stanowiskach AFK (D-141, Paweł 23.11; na main od 24.11).
	Wspólne dla serwera (src/server/TreningAFK.server.luau) i klienta (src/client/TreningAFKClient.client.luau).

	Zasada (Paweł 23.11, druga wersja): gracz staje na stanowisku (E) i postać sama robi powtórzenia — podnosi hantle,
	wyciska sztangę, czyta… Pasek = kilka powtórzeń (3–4), po pełnym pasku od razu bonus do statystyki. Klikać nie
	trzeba, każda seria trwa tyle samo. Co kilka sekund na ekranie pojawia się skill check: kto go kliknie na czas,
	ten przez chwilę trenuje 2× szybciej. LICZBY ROBOCZE — do kalkulatora balansu.
]]

local D = {}

-- gdzie stoją stanowiska: wolny pas placu w Workspace/MiasteczkoBazar (zmierzone 23.11 w Studio: x 924–1052,
-- z −712…−696 bez przeszkód); jeden rząd, przejście od strony południowej zostaje
D.start = Vector3.new(950, 0.1, -699)
D.odstep = 16 -- studów między środkami stanowisk (wzdłuż osi X)
D.obrot = 180 -- stopni: obrót stanowiska (gracz patrzy na rekwizyt)

-- agent Karola, sesja 25.11: stanowiska stoją w sali treningowej Training Center (rozbudowa budynku „w lewo”,
-- swiat/miasteczko_bazar/budynki/training_center.py → znaczniki.json, blok „trening_afk”). pozycja = środek maty na
-- posadzce sali, obrot = stopnie jak D.obrot. Stanowisko bez wpisu staje w dawnym rzędzie od D.start.
-- agent Karola, 26.11: prośba Pawła — sala dłuższa, dwa rzędy po trzy wzdłuż boków sali i wolne przejście pośrodku
-- (od placyku do tylnej ściany). Lewy rząd od frontu: Pancerz twarzą do placyku (NPC z pomidorami 11 st przed graczem
-- stoi na placyku), Szczęście i Zręczność twarzą do lewej ściany; prawy rząd: Siła, Inteligencja, Kondycja twarzą
-- do tylnej ściany.
-- agent Karola, 27.11 (polecenie Pawła: „hala ze sprzętami powinna zajmować mniej więcej taki obszar, żeby było tam dużo
-- przestrzeni”): duża sala 40 × 22 st z korytarzem 9,3 st pośrodku, maty co 9 st. Tylny rząd: Siła, Inteligencja twarzą
-- do tylnej ściany, Szczęście bokiem (stolik ku zachodniej ścianie); przedni rząd: Pancerz twarzą do okna na placyk
-- (NPC 11 st przed graczem stoi na placyku), Kondycja i Zręczność bokiem (ławka i bieżnia wzdłuż ściany) — żaden
-- rekwizyt z kolizją nie wystaje za matę w stronę korytarza. zejscie = gdzie staje gracz po treningu, w układzie
-- stanowiska (gracz patrzy w −Z, +X po jego prawej): zawsze w korytarz. Bez zejscie — 3 st za matą, jak dotąd.
D.miejsca = {
	Sila = { pozycja = Vector3.new(908.082, 0.5, -731.275), obrot = 3, zejscie = Vector3.new(0, 0, 3.4) },
	Inteligencja = { pozycja = Vector3.new(899.094, 0.5, -730.804), obrot = 3, zejscie = Vector3.new(0, 0, 3.4) },
	Szczescie = { pozycja = Vector3.new(890.106, 0.5, -730.333), obrot = 93, zejscie = Vector3.new(-3.4, 0, 0) },
	Pancerz = { pozycja = Vector3.new(908.799, 0.5, -717.594), obrot = 183, zejscie = Vector3.new(0, 0, 3.4) },
	Kondycja = { pozycja = Vector3.new(899.811, 0.5, -717.123), obrot = 93, zejscie = Vector3.new(3.4, 0, 0) },
	Zrecznosc = { pozycja = Vector3.new(890.823, 0.5, -716.652), obrot = 93, zejscie = Vector3.new(3.4, 0, 0) },
}
-- agent Karola, 27.11: podpowiedź E stanowiska wisi tyle studów nad środkiem maty (na wysokości bioder), nie w macie —
-- zasięg 4,5 (Paweł 26.11) liczy się wtedy prawie w poziomie: E sięga z krawędzi maty od strony korytarza, a sąsiednia
-- mata (≥ 9 st dalej) jest poza zasięgiem
D.podpowiedzWysokosc = 1.5

-- agent Karola, 26.11 (polecenie Karola: „podchodzimy do trenera, klikamy E i klikamy, w co chcemy wejść — i nas
-- teleportuje”): E przy trenerze w Training Center otwiera okno sześciu ćwiczeń; klik = serwer stawia gracza na
-- stanowisku i zaczyna trening tak samo jak E przy macie. Tabliczek z nazwami przy stanowiskach już nie ma.
D.trener = {
	miejsce = "training_center", -- id miejsca bazaru (swiat/miasteczko_bazar_gra/miejsca.json); po E przy trenerze
	-- bazar woła :Fire(miejsce) na zdarzeniu okien w ReplicatedStorage (klient: bindable jak w innych oknach Pawła)
	punkt = "MiasteczkoBazarGra/Punkty/E training_center", -- część z podpowiedzią E trenera (w Workspace)
	pozycja = Vector3.new(942.323, 5.1, -729.465), -- zapas, gdy punktu nie ma (znaczniki.json bazaru → training_center)
	zasieg = 16, -- studów w poziomie od punktu E (podpowiedź sięga 10): dalej serwer odmawia, a okno samo się zamyka
	odstep = 0.5, -- s między prośbami gracza o stanowisko (częstsze serwer pomija)
}

D.stanowiska = {
	{ id = "Sila", ikona = "rbxassetid://80829675491231", atrybut = "Strength", nazwa = "STRENGTH", skrot = "STR", czynnosc = "DUMBBELLS", kolor = Color3.fromRGB(236, 96, 86) },
	{ id = "Kondycja", ikona = "rbxassetid://129848880606537", atrybut = "Constitution", nazwa = "HEALTH", skrot = "CON", czynnosc = "BENCH PRESS", kolor = Color3.fromRGB(120, 210, 120) },
	{ id = "Pancerz", ikona = "rbxassetid://121315147202267", atrybut = "Armor", nazwa = "ARMOR", skrot = "ARM", czynnosc = "SHIELD BLOCK", kolor = Color3.fromRGB(150, 160, 185) },
	{ id = "Zrecznosc", ikona = "rbxassetid://121602116084315", atrybut = "Dexterity", nazwa = "DEXTERITY", skrot = "DEX", czynnosc = "TREADMILL", kolor = Color3.fromRGB(255, 192, 90) },
	{ id = "Inteligencja", ikona = "rbxassetid://137985641979179", atrybut = "Intelligence", nazwa = "INTELLIGENCE", skrot = "INT", czynnosc = "BOOKS", kolor = Color3.fromRGB(110, 170, 255) },
	{ id = "Szczescie", ikona = "rbxassetid://87096405792117", atrybut = "Luck", nazwa = "LUCK", skrot = "LCK", czynnosc = "DICE", kolor = Color3.fromRGB(190, 120, 240) },
}

-- grafiki ekranu treningu (Higgsfield, Glossy Ink, wgrane 23.11 po „tak” Pawła; assets/manifest.json, Trening*)
D.obrazy = {
	panel = "rbxassetid://113367842595549", -- 1024 × 404
	stop = "rbxassetid://136347965162300",
	skillCheck = "rbxassetid://87414657975804", -- moneta z pięścią, napis „2X” natywnie
}

-- seria
D.powtorzenNaPasek = 4 -- tyle powtórzeń zapełnia pasek
D.czasPowtorzenia = 1.2 -- s na jedno powtórzenie (pełny pasek ≈ 4,8 s)
D.przyrostNaPasek = 1 -- + tyle do statystyki za pełny pasek
D.przyrostCoPoziomow = 0 -- 0 = stały przyrost; np. 10 = +1 za każde 10 poziomów gracza

-- agent Karola, 27.11 (Karol: „w gierce szczęścia w sali AFK niech też rzuca się prawdziwymi kośćmi, wypadają prawdziwe
-- wyniki — i tyle szczęścia dostajemy, ile wypadnie”; liczby wybrał Karol 27.11): stanowisko Szczęścia na końcu paska
-- rzuca `liczba` kości o `scianki` ściankach (losuje serwer) — przyrost = suma oczek × zwykły przyrost za pasek
-- (poziom gracza, wzmacniacz ×2 ze sklepu). Kości to sześciany, więc scianki 2…6 (wynik pokazuje górna ścianka);
-- liczba 1…4 (tyle mieści stolik).
-- mnoznikPaska = ile razy dłuższy pasek Szczęścia niż pozostałych: przy 1 kości k6 i 3,5 średnio tyle samo punktów na
-- minutę co inne statystyki. Limit treningu (D.pasekPrzyLimicie) liczy się od faktycznego przyrostu.
D.kosci = {
	stanowisko = "Szczescie",
	liczba = 1,
	scianki = 6,
	mnoznikPaska = 3.5,
	bok = 0.6, -- studów: bok kości (wygląd)
	-- ścianki w układzie kości: wartość w, normalna n, osie u i v na ściance (przeciwne ścianki dają 7); te same dla
	-- serwera (oczka z klocków) i klienta (obrót, który kładzie ściankę wyniku do góry)
	sciany = {
		{ w = 1, n = Vector3.yAxis, u = Vector3.xAxis, v = Vector3.zAxis },
		{ w = 6, n = -Vector3.yAxis, u = Vector3.xAxis, v = Vector3.zAxis },
		{ w = 2, n = -Vector3.zAxis, u = Vector3.xAxis, v = Vector3.yAxis },
		{ w = 5, n = Vector3.zAxis, u = Vector3.xAxis, v = Vector3.yAxis },
		{ w = 3, n = Vector3.xAxis, u = Vector3.zAxis, v = Vector3.yAxis },
		{ w = 4, n = -Vector3.xAxis, u = Vector3.zAxis, v = Vector3.yAxis },
	},
	oczka = { -- położenie oczek na ściance (u, v w jednostkach odstępu oczek)
		[1] = { { 0, 0 } },
		[2] = { { -1, -1 }, { 1, 1 } },
		[3] = { { -1, -1 }, { 0, 0 }, { 1, 1 } },
		[4] = { { -1, -1 }, { 1, -1 }, { -1, 1 }, { 1, 1 } },
		[5] = { { -1, -1 }, { 1, -1 }, { 0, 0 }, { -1, 1 }, { 1, 1 } },
		[6] = { { -1, -1 }, { -1, 0 }, { -1, 1 }, { 1, -1 }, { 1, 0 }, { 1, 1 } },
	},
}

-- agent Karola, 27.11 (Karol: „A + B”, swiat/przejscie_gry/BALANS_2711.md, pytanie 117; czeka na Pawła): limit treningu
-- zależny od poziomu. Dopóki gracz ma w tej statystyce WYTRENOWANE mniej niż limitNaPoziom × poziom, pasek jak dotąd;
-- powyżej pasek trwa 1 / ponadLimitem razy dłużej (0.1 = 10× wolniej). Wytrenowane punkty pisze stan gracza
-- (swiat/stan_gracza) w atrybutach gracza prefiksWytrenowanych .. atrybut (np. WytrenowaneStrength).
-- Wyłączenie limitu: limitNaPoziom = 0.
D.limitNaPoziom = 2
D.ponadLimitem = 0.1
D.prefiksWytrenowanych = "Wytrenowane"
D.tekstLimitu = "LIMIT: LEVEL UP TO TRAIN FASTER"

-- skill check
D.skillCheckCoMin = 3.5 -- s między skill checkami (losowo z przedziału)
D.skillCheckCoMaks = 6
D.skillCheckOkno = 1.3 -- s na kliknięcie
D.mnoznikSkillCheck = 2 -- tempo po trafieniu
D.czasPrzyspieszenia = 2.4 -- s przyspieszenia po trafieniu

D.zasieg = 5 -- studów w poziomie od miejsca stanowiska: dalej trening się kończy (gracz odszedł)
D.krokSerwera = 0.2 -- s między krokami licznika na serwerze

-- sklep trenera (agent Karola, 27.11; Paweł 27.11: „u trenera nie tyle co się wybierało trening, ale też był panel
-- sklepu/ulepszeń, gdzie np. gracz może ulepszyć bieżnię, żeby dawała więcej na powtórzenie, albo kupić jakieś
-- wzmacniacze na trening, np. siła ×2 na 10 min”). LICZBY ROBOCZE — rachunek i tabela:
-- swiat/trening_proba/ekonomia_sklepu_afk.py. Płaci się Rybkami (atrybut Gold) przez stan gracza (Sygnaly/WydajZloto,
-- źródło D.sklep.zrodlo — musi być na liście PAKIETY_WYDATKOW w swiat/stan_gracza/dane.py); poziomy i koniec
-- wzmacniaczy zapisuje profil gracza (Sygnaly/DanePakietu, pakiet D.sklep.pakiet). BEZ Robuxów: sprzedaż za Robuxy to
-- osobna decyzja — w serwerze są dwa miejsca przyznania (przyznajUlepszenie, przyznajWzmacniacz), które zawołałby też
-- przyszły ProcessReceipt.
D.sklep = {
	ulepszenia = {
		maks = 5, -- poziomy 0 … 5, osobno dla każdego gracza i stanowiska
		premia = 0.10, -- +10% tempa na poziom: pasek = D.powtorzenNaPasek / (1 + premia × poziom) powtórzeń („więcej na powtórzenie”)
		ceny = { 300, 700, 1600, 3600, 8400 }, -- Rybki za poziom 1, 2, 3, 4, 5
	},
	wzmacniacze = {
		mnoznik = 2, -- × statystyki za pełny pasek tego stanowiska
		czas = 600, -- s (10 min) czasu rzeczywistego od zakupu — wyjście z gry go nie zatrzymuje; jeden na statystykę
		cena = 600, -- Rybki
	},
	odstep = 0.4, -- s między zakupami gracza (częstsze serwer pomija)
	zrodlo = "TreningAFK", -- źródło wydatku w stanie gracza
	pakiet = "TreningAFK", -- klucz danych w profilu: { u = { [id stanowiska] = poziom }, w = { [atrybut] = koniec (os.time) } }
	cele = { ulepszenie = "trening_ulepszenie", wzmacniacz = "trening_wzmacniacz" }, -- liczniki wydatków w profilu
}

-- powtórzeń na pełny pasek przy danym poziomie ulepszenia stanowiska
function D.powtorzenDla(poziom: number): number
	local p = math.clamp(math.floor(poziom), 0, D.sklep.ulepszenia.maks)
	return D.powtorzenNaPasek / (1 + D.sklep.ulepszenia.premia * p)
end

-- agent Karola, 27.11: powtórzeń na pełny pasek tego stanowiska (Szczęście: × D.kosci.mnoznikPaska)
function D.powtorzenStanowiska(id: string, poziom: number): number
	local p = D.powtorzenDla(poziom)
	if id == D.kosci.stanowisko then
		p *= math.max(D.kosci.mnoznikPaska, 0.05)
	end
	return p
end

-- agent Karola, 27.11: liczba kości i ścianek w bezpiecznych granicach (sześcian: 2…6 ścianek)
function D.kosciRzutu(): (number, number)
	return math.clamp(math.floor(D.kosci.liczba), 1, 4), math.clamp(math.floor(D.kosci.scianki), 2, 6)
end

-- cena następnego poziomu (z poziomu `poziom` na poziom + 1); nil = już najwyższy
function D.cenaUlepszenia(poziom: number): number?
	return D.sklep.ulepszenia.ceny[math.floor(poziom) + 1]
end

-- agent Karola, 27.11: pasek (powtórzenia) po limicie treningu → (pasek, czy ponad limitem)
function D.pasekPrzyLimicie(pasek: number, wytrenowane: number, poziom: number): (number, boolean)
	if D.limitNaPoziom <= 0 or wytrenowane < D.limitNaPoziom * math.max(poziom, 1) then
		return pasek, false
	end
	return pasek / math.max(D.ponadLimitem, 0.001), true
end

function D.przyrost(poziom: number): number
	if D.przyrostCoPoziomow <= 0 then
		return D.przyrostNaPasek
	end
	return D.przyrostNaPasek + math.floor(math.max(poziom, 0) / D.przyrostCoPoziomow)
end

function D.stanowisko(id: string)
	for _, s in ipairs(D.stanowiska) do
		if s.id == id then
			return s
		end
	end
	return nil
end

return D
