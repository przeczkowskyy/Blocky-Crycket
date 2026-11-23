--!strict
--[[
	TreningAFKDane — ustawienia treningu na stanowiskach AFK (D-141, Paweł 23.11; gałąź pawel/diamenty-afk).
	Wspólne dla serwera (src/server/TreningAFK.server.luau) i klienta (src/client/TreningAFKClient.client.luau).

	Zasada: gracz staje na stanowisku (E / dotknięcie podpowiedzi), pasek sam się napełnia (AFK), tapnięcie /
	kliknięcie przyspiesza go (poprawka agenta 1 z D-141). Pełny pasek = +przyrost do statystyki stanowiska.
	Przyrost rośnie z poziomem gracza (poprawka 2), a pasek wydłuża się wraz z wartością statystyki, więc samo
	stanie nie zmaksuje gry w godzinę. LICZBY ROBOCZE — do kalkulatora balansu.
]]

local D = {}

-- gdzie stoją stanowiska: wolny pas placu w Workspace/MiasteczkoBazar (zmierzone 23.11 w Studio: x 924–1052,
-- z −712…−696 bez przeszkód); jeden rząd wzdłuż północnej krawędzi, przejście od strony południowej zostaje
D.start = Vector3.new(950, 0.1, -699)
D.odstep = 16 -- studów między środkami stanowisk (wzdłuż osi X)
D.obrot = 180 -- stopni: gracz na stanowisku patrzy na plac (−Z → +Z odwrócone)

D.stanowiska = {
	{ id = "Sila", atrybut = "Strength", nazwa = "STRENGTH", skrot = "STR", czynnosc = "DUMBBELLS", kolor = Color3.fromRGB(236, 96, 86) },
	{ id = "Kondycja", atrybut = "Constitution", nazwa = "HEALTH", skrot = "CON", czynnosc = "BENCH PRESS", kolor = Color3.fromRGB(120, 210, 120) },
	{ id = "Pancerz", atrybut = "Armor", nazwa = "ARMOR", skrot = "ARM", czynnosc = "PUNCHING BAG", kolor = Color3.fromRGB(150, 160, 185) },
	{ id = "Zrecznosc", atrybut = "Dexterity", nazwa = "DEXTERITY", skrot = "DEX", czynnosc = "JUMP ROPE", kolor = Color3.fromRGB(255, 192, 90) },
	{ id = "Inteligencja", atrybut = "Intelligence", nazwa = "INTELLIGENCE", skrot = "INT", czynnosc = "BOOKS", kolor = Color3.fromRGB(110, 170, 255) },
	{ id = "Szczescie", atrybut = "Luck", nazwa = "LUCK", skrot = "LCK", czynnosc = "DICE", kolor = Color3.fromRGB(190, 120, 240) },
}

-- pasek
D.afkNaSekunde = 1 -- jednostek paska na sekundę samego stania
D.tapWartosc = 0.5 -- jednostek za jedno tapnięcie
D.tapMaksNaSekunde = 2 -- serwer liczy najwyżej tyle tapnięć na sekundę (aktywny gracz = ×2 względem AFK)
D.pasekBaza = 15 -- jednostek na pełny pasek przy statystyce 0
D.pasekNaPunkt = 0.5 -- + tyle jednostek za każdy punkt statystyki (dłuższy pasek przy wyższej statystyce)
D.pasekMaks = 240
D.przyrostCoPoziomow = 10 -- przyrost za pasek = 1 + floor(poziom / 10)

D.zasieg = 5 -- studów od miejsca stanowiska: dalej trening się kończy (gracz odszedł)
D.krokSerwera = 0.25 -- s między krokami licznika na serwerze

function D.dlugoscPaska(wartosc: number): number
	return math.clamp(D.pasekBaza + D.pasekNaPunkt * math.max(wartosc, 0), D.pasekBaza, D.pasekMaks)
end

function D.przyrost(poziom: number): number
	return 1 + math.floor(math.max(poziom, 0) / D.przyrostCoPoziomow)
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
