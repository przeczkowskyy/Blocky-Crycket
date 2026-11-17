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
	skrot = "55c50b774178",
	mapa = {
		nazwa = "BagnoPas",
		zrodlo = "znaczniki",
		X0 = 1100,
		Z0 = -700,
		grupaWrot = "BramaDzungli/Wrota",
		grupaPalisady = "BramaDzungli/Palisada",
		zapowiedz = "ZapowiedzDzungli",
	},
	wejscie = { x1 = 2036, x2 = 3016, z1 = -760, z2 = -640 },
	przybycie = { punkt = { 2054, 0, -700 }, patrz = { 2100, 0, -700 }, wysokosc = 3.2 },
	przedBrama = { punkt = { 2964, 0, -700 }, patrz = { 2974, 0, -700 } },
	zaBrama = { punkt = { 2986, 0, -700 }, patrz = { 3014, 0, -700 } },
	powrot = { punkt = { 2048.5, 0.1, -718.5 }, zasieg = 10 },
	miasteczko = {
		punkt = { -63.6, 0, -771.5 },
		patrz = { 0.3, 0, -698.7 },
		teleport = "LasTeleport",
		bazar = { kontener = "MiasteczkoBazarGra", uchwyt = "PrzeniesDoBazaru", punkt = "start" },
	},
	brama = { x = 2974, z1 = -760, z2 = -640, tolerancja = 1.5, glebokosc = 200, otwarcie = { -708, -692 } },
	zapora = { srodek = { 2974, 20, -700 }, rozmiar = { 1, 40, 80 } },
	napisBramy = { punkt = { 2972.4, 6.5, -700 }, tekst = "ZAMKNIĘTE", podpis = "Pokonaj Strażnika Topieli" },
	zabezpieczenie = {
		podloga = { srodek = { 3009, -0.55, -700 }, rozmiar = { 70, 1, 80 } },
		sciana = { srodek = { 3044, 20, -700 }, rozmiar = { 2, 40, 80 } },
	},
	tabliczka = { punkt = { 2992, 0, -700 }, tekst = "DŻUNGLA — WKRÓTCE", podpis = "tu zaczyna się następny biom" },
	ratunek = { x1 = 2034, x2 = 3156, z1 = -900, z2 = -500, yMin = -30 },
	mgla = {
		x1 = 2034,
		x2 = 2980,
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
		czas = 13.4,
		zatrzymanieOd = 10.5,
		rykOd = 10.7,
		rykDl = 2,
		klip = "ryk",
		zaciemnienie = 0.5,
		punkty = {
			{ t = 0, poz = { 2046, 26, -700 }, patrz = { 2110, 4, -700 } },
			{ t = 1.2, poz = { 2092, 28, -688 }, patrz = { 2190, 2, -700 } },
			{ t = 2.7, poz = { 2200, 25, -716 }, patrz = { 2270, 2, -700 } },
			{ t = 4.3, poz = { 2340, 25, -690 }, patrz = { 2420, 3, -700 } },
			{ t = 6.1, poz = { 2510, 23, -712 }, patrz = { 2600, 3, -700 } },
			{ t = 8.1, poz = { 2700, 21, -690 }, patrz = { 2794, 6, -706 } },
			{ t = 9.6, poz = { 2840, 14, -700 }, patrz = { 2914, 11, -700 } },
			{ t = 10.5, poz = { 2886, 11, -700 }, patrz = { 2914, 11.5, -700 } },
			{ t = 13.4, poz = { 2886, 11, -700 }, patrz = { 2914, 11.5, -700 } },
		},
		strumien = { { 2210, 0, -700 }, { 2490, 0, -700 }, { 2740, 0, -700 }, { 2914, 0, -700 } },
	},
	straznik = { poz = { 2914, 0.3, -700 }, gatunek = "straznik_topieli" },
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
		podpisBramy = "Brama do Dżungli otwarta — Dżungla wkrótce",
		banerBramy = "BRAMA DO DŻUNGLI OTWARTA!",
		podpisBanera = "Idź za Topiel — dalej Dżungla",
		podpisBaneraWkrotce = "Za Topielą — Dżungla (wkrótce)",
		nastepny = { mapa = "DzunglaPas", nazwa = "Dżungla" },
		wymaganie = {
			atrybut = "PokonalStraznikaLasu",
			odX = 2234,
			punkt = { 2024, 3.2, -700 },
			patrz = { 2034, 3.2, -700 },
			komunikat = "Bagno jest za bramą lasu — najpierw pokonaj Strażnika Gaju.",
		},
	},
}
