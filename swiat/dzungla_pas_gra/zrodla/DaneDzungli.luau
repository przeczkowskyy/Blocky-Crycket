--[[
	DanePasa (DŻUNGLA) — WYGENEROWANE przez swiat/dzungla_pas_gra/generuj_dane.py z planu i mapy Dżungli. NIE EDYTUJ
	RĘCZNIE. Liczby świata dla SerwerPasa, KlientPasa i MglaPasa (te same skrypty co las-pas i Bagno): przybycie, Kamień
	Powrotu, brama do Pustyni i to, co za nią, mgła Dżungli, przelot kamery, Wąż Stu Lian; pole biom — nazwy i teksty
	Dżungli (uchwyt PrzeniesDoDzungli, klucze pamięci, prawo wejścia z bramy Bagna).
	Prostokąty to { x1, x2, z1, z2 } w poziomie świata; punkty to { x, y, z }.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

return {
	wersja = 1,
	skrot = "5648a060af56",
	mapa = {
		nazwa = "DzunglaPas",
		zrodlo = "znaczniki",
		X0 = 1100,
		Z0 = -700,
		grupaWrot = "BramaPustyni/Wrota",
		grupaPalisady = "BramaPustyni/Palisada",
		zapowiedz = "ZapowiedzPustyni",
	},
	wejscie = { x1 = 1936, x2 = 2396, z1 = -760, z2 = -640 },
	przybycie = { punkt = { 1954, 0, -700 }, patrz = { 1978.79, 0, -700 }, wysokosc = 3.2 },
	przedBrama = { punkt = { 2344, 0, -700 }, patrz = { 2354, 0, -700 } },
	zaBrama = { punkt = { 2366, 0, -700 }, patrz = { 2394, 0, -700 } },
	powrot = { punkt = { 1948.5, 0.1, -717 }, zasieg = 10 },
	miasteczko = {
		punkt = { 990, 0, -697 },
		patrz = { 1000, 0, -697 },
		bazar = { kontener = "MiasteczkoBazarGra", uchwyt = "PrzeniesDoBazaru", punkt = "start" },
	},
	brama = { x = 2354, z1 = -760, z2 = -640, tolerancja = 1.5, glebokosc = 200, otwarcie = { -708, -692 } },
	zapora = { srodek = { 2354, 20, -700 }, rozmiar = { 1, 40, 72 } },
	napisBramy = { punkt = { 2352.4, 6.5, -700 }, tekst = "ZAMKNIĘTE", podpis = "Pokonaj Węża Stu Lian" },
	zabezpieczenie = {
		podloga = { srodek = { 2389, -0.55, -700 }, rozmiar = { 70, 1, 72 } },
		sciana = { srodek = { 2424, 20, -700 }, rozmiar = { 2, 40, 72 } },
	},
	tabliczka = { punkt = { 2372, 0, -700 }, tekst = "PUSTYNIA — WKRÓTCE", podpis = "tu zaczyna się następny biom" },
	ratunek = { x1 = 1934, x2 = 2536, z1 = -900, z2 = -500, yMin = -30 },
	mgla = {
		x1 = 1934,
		x2 = 2360,
		z1 = -760,
		z2 = -640,
		pas = 120,
		tempo = 0.8,
		wPrzelocie = 0.5,
		cel = { Density = 0.38, Offset = 0.1, Haze = 1.8, Glare = 0.1, Color = "8FC79A", Decay = "4E7A52" },
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
			{ t = 0, poz = { 1946, 26, -700 }, patrz = { 1983.75, 4, -700 } },
			{ t = 0.83, poz = { 1978.79, 28, -688.57 }, patrz = { 2041.6, 2, -700 } },
			{ t = 1.87, poz = { 2041.6, 25, -714.86 }, patrz = { 2041.6, 2, -700 } },
			{ t = 2.98, poz = { 2068.05, 25, -690.29 }, patrz = { 2111.02, 3, -700 } },
			{ t = 4.22, poz = { 2111.02, 23, -711.43 }, patrz = { 2177.14, 3, -700 } },
			{ t = 5.61, poz = { 2177.14, 21, -690.29 }, patrz = { 2231.69, 6, -706 } },
			{ t = 6.65, poz = { 2269.7, 14, -700 }, patrz = { 2309.37, 11, -700 } },
			{ t = 7.27, poz = { 2287.88, 11, -700 }, patrz = { 2309.37, 11.5, -700 } },
			{ t = 10.17, poz = { 2287.88, 11, -700 }, patrz = { 2309.37, 11.5, -700 } },
		},
		strumien = { { 2042, 0, -700 }, { 2111, 0, -700 }, { 2187, 0, -700 }, { 2309, 0, -700 } },
	},
	straznik = { poz = { 2309.37, 0.3, -700 }, gatunek = "waz_stu_lian" },
	biom = {
		id = "dzungla",
		nazwa = "Dżungla",
		uchwyt = "PrzeniesDoDzungli",
		pamiecPrzelot = "widzialPrzelotDzungli",
		pamiecStraznik = "pokonalStraznikaDzungli",
		atrybutPrzelot = "WidzialPrzelotDzungli",
		atrybutStraznik = "PokonalStraznikaDzungli",
		atrybutPunktu = "PunktPrzybyciaDzungli",
		atrybutPatrz = "PatrzPrzybyciaDzungli",
		straznik = "Węża Stu Lian",
		komunikatBramy = "Brama do Pustyni jest zamknięta — pokonaj Węża Stu Lian.",
		przekieruj = false,
		podpisBramy = "Brama do Pustyni otwarta — Pustynia wkrótce",
		banerBramy = "BRAMA DO PUSTYNI OTWARTA!",
		podpisBanera = "Idź za Krąg Stu Lian — dalej Pustynia",
		podpisBaneraWkrotce = "Za Kręgiem Stu Lian — Pustynia (wkrótce)",
		nastepny = { mapa = "PustyniaPas", nazwa = "Pustynia" },
		wymaganie = {
			atrybut = "PokonalStraznikaBagna",
			odX = 2134,
			punkt = { 1924, 3.2, -700 },
			patrz = { 1934, 3.2, -700 },
			komunikat = "Dżungla jest za bramą Bagna — najpierw pokonaj Strażnika Topieli.",
		},
	},
}
