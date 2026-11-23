--!strict
--[[
	TreningAFKDane — ustawienia treningu na stanowiskach AFK (D-141, Paweł 23.11; gałąź pawel/diamenty-afk).
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

-- skill check
D.skillCheckCoMin = 3.5 -- s między skill checkami (losowo z przedziału)
D.skillCheckCoMaks = 6
D.skillCheckOkno = 1.3 -- s na kliknięcie
D.mnoznikSkillCheck = 2 -- tempo po trafieniu
D.czasPrzyspieszenia = 2.4 -- s przyspieszenia po trafieniu

D.zasieg = 5 -- studów w poziomie od miejsca stanowiska: dalej trening się kończy (gracz odszedł)
D.krokSerwera = 0.2 -- s między krokami licznika na serwerze

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
