--[[
	DanePasa — WYGENEROWANE przez swiat/las_pas_gra/generuj_dane.py z planu pasa (i mapy, gdy jest). NIE EDYTUJ RĘCZNIE.
	Liczby świata dla skryptów pasa (SerwerPasa, KlientPasa, MglaPasa): przybycie, Kamień Powrotu, brama do Bagna i to,
	co za nią, mgła (prostokąt pasa), przelot kamery (punkty Catmull-Rom w ŚWIECIE, ryk, wczytywanie mapy) i Strażnik.
	Prostokąty to { x1, x2, z1, z2 } w poziomie świata; punkty to { x, y, z }.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

return {
	wersja = 1,
	skrot = "e8762ea11804",
	mapa = {
		nazwa = "LasPas",
		zrodlo = "znaczniki",
		X0 = 1100,
		Z0 = -700,
		grupaWrot = "BramaBagna/Wrota",
		grupaPalisady = "BramaBagna/Palisada",
		zapowiedz = "ZapowiedzBagna",
	},
	wejscie = { x1 = 1056, x2 = 2076, z1 = -760, z2 = -640 },
	przybycie = { punkt = { 1114, 0, -700 }, patrz = { 1160, 0, -700 }, wysokosc = 3.2 },
	przedBrama = { punkt = { 2024, 0, -700 }, patrz = { 2034, 0, -700 } },
	zaBrama = { punkt = { 2046, 0, -700 }, patrz = { 2074, 0, -700 } },
	powrot = { punkt = { 1106.5, 0.1, -718.5 }, zasieg = 10 },
	miasteczko = { punkt = { -63.6, 0, -771.5 }, patrz = { 0.3, 0, -698.7 }, teleport = "LasTeleport" },
	brama = { x = 2034, z1 = -760, z2 = -640, tolerancja = 1.5, glebokosc = 200, otwarcie = { -708, -692 } },
	zapora = { srodek = { 2034, 20, -700 }, rozmiar = { 1, 40, 80 } },
	napisBramy = { punkt = { 2032.4, 6.5, -700 }, tekst = "ZAMKNIĘTE", podpis = "Pokonaj Strażnika Gaju" },
	zabezpieczenie = {
		podloga = { srodek = { 2069, -0.55, -700 }, rozmiar = { 70, 1, 80 } },
		sciana = { srodek = { 2104, 20, -700 }, rozmiar = { 2, 40, 80 } },
	},
	tabliczka = { punkt = { 2052, 0, -700 }, tekst = "BAGNO — WKRÓTCE", podpis = "tu zaczyna się następny biom" },
	ratunek = { x1 = 916, x2 = 2216, z1 = -900, z2 = -500, yMin = -30 },
	mgla = {
		x1 = 1076,
		x2 = 2040,
		z1 = -760,
		z2 = -640,
		pas = 120,
		tempo = 0.8,
		wPrzelocie = 0.5,
		cel = { Density = 0.36, Offset = 0.15, Haze = 1.4, Glare = 0, Color = "D6E4DA", Decay = "8FAF9A" },
	},
	przelot = {
		uspokojenie = 0.5,
		ladowanie = 4,
		zapas = 6,
		strumienCo = 1,
		wyprzedzenie = 2.5,
		ponowPoOdmowie = 5,
		rozjasnienie = 0.35,
		czas = 13.4,
		zatrzymanieOd = 10.5,
		rykOd = 10.7,
		rykDl = 2,
		klip = "ryk",
		zaciemnienie = 0.5,
		punkty = {
			{ t = 0, poz = { 1090, 28, -700 }, patrz = { 1160, 4, -700 } },
			{ t = 1.2, poz = { 1150, 30, -688 }, patrz = { 1250, 2, -700 } },
			{ t = 2.7, poz = { 1260, 26, -716 }, patrz = { 1330, 2, -700 } },
			{ t = 4.3, poz = { 1400, 26, -690 }, patrz = { 1480, 3, -700 } },
			{ t = 6.1, poz = { 1570, 24, -712 }, patrz = { 1660, 3, -700 } },
			{ t = 8.1, poz = { 1760, 22, -690 }, patrz = { 1854, 6, -706 } },
			{ t = 9.6, poz = { 1900, 14, -700 }, patrz = { 1974, 11, -700 } },
			{ t = 10.5, poz = { 1948, 10, -700 }, patrz = { 1974, 10.5, -700 } },
			{ t = 13.4, poz = { 1948, 10, -700 }, patrz = { 1974, 10.5, -700 } },
		},
		strumien = { { 1300, 0, -700 }, { 1550, 0, -700 }, { 1800, 0, -700 }, { 1974, 0, -700 } },
	},
	straznik = { poz = { 1974, 0, -700 }, gatunek = "straznik_lasu" },
}
