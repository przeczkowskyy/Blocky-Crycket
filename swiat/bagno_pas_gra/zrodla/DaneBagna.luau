--[[
	DanePasa (BAGNO) — WYGENEROWANE przez swiat/bagno_pas_gra/generuj_dane.py z planu i mapy Bagna. NIE EDYTUJ RĘCZNIE.
	Liczby świata dla SerwerPasa, KlientPasa i MglaPasa (te same skrypty co las-pas): przybycie, Kamień Powrotu, brama do
	Dżungli i to, co za nią, mgła Bagna, przelot kamery, Strażnik Topieli; pole biom — nazwy i teksty Bagna (uchwyt
	PrzeniesDoBagna, klucze pamięci, prawo wejścia z bramy lasu).
	Prostokąty to { x1, x2, z1, z2 } w poziomie świata; punkty to { x, y, z }.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

return {
	wersja = 1,
	skrot = "27f04979a4a4",
	mapa = {
		nazwa = "BagnoPas",
		zrodlo = "znaczniki",
		X0 = 1100,
		Z0 = -700,
		grupaWrot = "BramaDzungli/Wrota",
		grupaPalisady = "BramaDzungli/Palisada",
		zapowiedz = "ZapowiedzDzungli",
	},
	wejscie = { x1 = 1516, x2 = 1973.92, z1 = -760, z2 = -640 },
	przybycie = { punkt = { 1534, 0, -700 }, patrz = { 1558.79, 0, -700 }, wysokosc = 3.2 },
	przedBrama = { punkt = { 1924, 0, -700 }, patrz = { 1934, 0, -700 } },
	zaBrama = { punkt = { 1946, 0, -700 }, patrz = { 1974, 0, -700 } },
	powrot = { punkt = { 1528.5, 0.1, -717 }, zasieg = 10 },
	miasteczko = {
		punkt = { -63.6, 0, -771.5 },
		patrz = { 0.3, 0, -698.7 },
		teleport = "LasTeleport",
		bazar = { kontener = "MiasteczkoBazarGra", uchwyt = "PrzeniesDoBazaru", punkt = "start" },
	},
	brama = { x = 1934, z1 = -760, z2 = -640, tolerancja = 1.5, glebokosc = 200, otwarcie = { -708, -692 } },
	zapora = { srodek = { 1934, 20, -700 }, rozmiar = { 1, 40, 72 } },
	napisBramy = { punkt = { 1932.4, 6.5, -700 }, tekst = "ZAMKNIĘTE", podpis = "Pokonaj Strażnika Topieli" },
	zabezpieczenie = {
		podloga = { srodek = { 1969, -0.55, -700 }, rozmiar = { 70, 1, 72 } },
		sciana = { srodek = { 2004, 20, -700 }, rozmiar = { 2, 40, 72 } },
	},
	tabliczka = { punkt = { 1952, 0, -700 }, tekst = "DŻUNGLA — WKRÓTCE", podpis = "tu zaczyna się następny biom" },
	ratunek = { x1 = 1514, x2 = 2113.92, z1 = -900, z2 = -500, yMin = -30 },
	mgla = {
		x1 = 1514,
		x2 = 1940,
		z1 = -760,
		z2 = -640,
		pas = 120,
		tempo = 0.8,
		wPrzelocie = 0.5,
		cel = { Density = 0.42, Offset = 0.08, Haze = 2.2, Glare = 0, Color = "9AA58E", Decay = "5E6B4E" },
	},
	przelot = {
		uspokojenie = 0.5,
		ladowanie = 4,
		zapas = 6,
		strumienCo = 1,
		wyprzedzenie = 2.5,
		ponowPoOdmowie = 5,
		rozjasnienie = 0.35,
		czas = 10.17,
		zatrzymanieOd = 7.27,
		rykOd = 7.47,
		rykDl = 2,
		klip = "ryk",
		zaciemnienie = 0.5,
		punkty = {
			{ t = 0, poz = { 1526, 26, -700 }, patrz = { 1563.75, 4, -700 } },
			{ t = 0.83, poz = { 1558.79, 28, -688.57 }, patrz = { 1621.6, 2, -700 } },
			{ t = 1.87, poz = { 1621.6, 25, -714.86 }, patrz = { 1621.6, 2, -700 } },
			{ t = 2.98, poz = { 1648.05, 25, -690.29 }, patrz = { 1691.02, 3, -700 } },
			{ t = 4.22, poz = { 1691.02, 23, -711.43 }, patrz = { 1757.14, 3, -700 } },
			{ t = 5.61, poz = { 1757.14, 21, -690.29 }, patrz = { 1811.69, 6, -706 } },
			{ t = 6.65, poz = { 1849.7, 14, -700 }, patrz = { 1889.37, 11, -700 } },
			{ t = 7.27, poz = { 1867.88, 11, -700 }, patrz = { 1889.37, 11.5, -700 } },
			{ t = 10.17, poz = { 1867.88, 11, -700 }, patrz = { 1889.37, 11.5, -700 } },
		},
		strumien = { { 1622, 0, -700 }, { 1691, 0, -700 }, { 1767, 0, -700 }, { 1889, 0, -700 } },
	},
	straznik = { poz = { 1889.37, 0.3, -700 }, gatunek = "straznik_topieli" },
	biom = {
		id = "bagno",
		nazwa = "Bagno",
		uchwyt = "PrzeniesDoBagna",
		pamiecPrzelot = "widzialPrzelotBagna",
		pamiecStraznik = "pokonalStraznikaBagna",
		atrybutPrzelot = "WidzialPrzelotBagna",
		atrybutStraznik = "PokonalStraznikaBagna",
		atrybutPunktu = "PunktPrzybyciaBagna",
		atrybutPatrz = "PatrzPrzybyciaBagna",
		straznik = "Strażnika Topieli",
		komunikatBramy = "Brama do Dżungli jest zamknięta — pokonaj Strażnika Topieli.",
		przekieruj = false,
		podpisBramy = "Brama do Dżungli otwarta — idź za Topiel",
		banerBramy = "BRAMA DO DŻUNGLI OTWARTA!",
		podpisBanera = "Idź za Topiel — dalej Dżungla",
		podpisBaneraWkrotce = "Za Topielą — Dżungla (wkrótce)",
		nastepny = { mapa = "DzunglaPas", nazwa = "Dżungla" },
		wymaganie = {
			atrybut = "PokonalStraznikaLasu",
			odX = 1714,
			punkt = { 1504, 3.2, -700 },
			patrz = { 1514, 3.2, -700 },
			komunikat = "Bagno jest za bramą lasu — najpierw pokonaj Strażnika Gaju.",
		},
	},
}
