--[[
	KatalogDzwiekow — WYGENEROWANY przez swiat/dzwiek_gra/zbuduj.py z assets/audio/arkusz/sfx_arkusz_a.json
	(odcinki arkusza), swiat/dzwiek_gra/ustawienia.json (głośności, zdarzenia, muzyka stref) i identyfikatory.json.
	NIE EDYTUJ RĘCZNIE: zmień pliki źródłowe i uruchom python -B swiat/dzwiek_gra/zbuduj.py --sucho.

	Czytają go: OdtwarzaczWalki2 (prototyp walki: odcinki arkusza zamiast wbudowanych dźwięków, gdy arkusz.id ≠ 0)
	i MuzykaStref (muzyka bazaru i lasu-pasa). Identyfikator 0 = plik jeszcze nie wgrany (cisza / dźwięki wbudowane).
	Czasy efektów: poczatek / koniec = sekundy w pliku arkusza, atak / szczyt = sekundy od początku odcinka.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

return {
	wersja = 1,
	skrot = "aad4100250ba",
	arkusz = {
		id = 93573204965127,
		plik = "sfx_arkusz_a.ogg",
		wariant = "A",
		sha256 = "7fe60bb9cf95a8de1bc3b102a658e42baa4521a86e5ed3bcf59019f6ac061e15",
		dlugosc = 50.143,
		glosnosc = 0.6,
		naraz = 6,
	},
	efekty = {
		sfx_awans_poziom = {
			poczatek = 0.25,
			koniec = 2.627,
			atak = 0.02,
			szczyt = 0.81,
			glosnosc = 0.8,
		},
		sfx_blok_tarcza = {
			poczatek = 2.977,
			koniec = 5.472,
			atak = 0.13,
			szczyt = 0.23,
			glosnosc = 0.9,
		},
		sfx_cios_krytyczny = {
			poczatek = 5.822,
			koniec = 8.5178,
			atak = 1.36,
			szczyt = 1.44,
			glosnosc = 1.0,
		},
		sfx_cios_trafiony = {
			poczatek = 8.8678,
			koniec = 11.1989,
			atak = 0.92,
			szczyt = 1.08,
			glosnosc = 0.9,
		},
		sfx_fanfara_zwyciestwa = {
			poczatek = 11.5488,
			koniec = 14.692,
			atak = 0.03,
			szczyt = 1.02,
			glosnosc = 0.8,
		},
		sfx_galareta_plusk = {
			poczatek = 15.042,
			koniec = 15.4167,
			atak = 0.02,
			szczyt = 0.06,
			glosnosc = 1.0,
		},
		sfx_klik_przycisk = {
			poczatek = 15.7666,
			koniec = 16.0076,
			atak = 0.01,
			szczyt = 0.01,
			glosnosc = 0.6,
		},
		sfx_kula_ognia = {
			poczatek = 16.3576,
			koniec = 19.3553,
			atak = 0.07,
			szczyt = 1.05,
			glosnosc = 0.9,
		},
		sfx_lodowy_pocisk = {
			poczatek = 19.7053,
			koniec = 21.0173,
			atak = 0.35,
			szczyt = 0.6,
			glosnosc = 0.9,
		},
		sfx_monety = {
			poczatek = 21.3673,
			koniec = 23.047,
			atak = 0.01,
			szczyt = 0.18,
			glosnosc = 0.7,
		},
		sfx_ogluszenie = {
			poczatek = 23.397,
			koniec = 24.2633,
			atak = 0.01,
			szczyt = 0.16,
			glosnosc = 0.8,
		},
		sfx_podpalenie_tik = {
			poczatek = 24.6132,
			koniec = 25.5345,
			atak = 0.01,
			szczyt = 0.22,
			glosnosc = 0.6,
		},
		sfx_porazka = {
			poczatek = 25.8845,
			koniec = 29.326,
			atak = 1.86,
			szczyt = 2.75,
			glosnosc = 0.8,
		},
		sfx_przejscie_chmury = {
			poczatek = 29.676,
			koniec = 32.8937,
			atak = 0.3,
			szczyt = 1.0,
			glosnosc = 0.8,
		},
		sfx_ryk_kolos = {
			poczatek = 33.2437,
			koniec = 36.7778,
			atak = 0.1,
			szczyt = 0.45,
			glosnosc = 0.8,
		},
		sfx_tarcza_magiczna = {
			poczatek = 37.1278,
			koniec = 39.7109,
			atak = 0.05,
			szczyt = 1.17,
			glosnosc = 0.8,
		},
		sfx_troll_chrzakniecie = {
			poczatek = 40.0609,
			koniec = 41.7721,
			atak = 0.06,
			szczyt = 1.27,
			glosnosc = 0.8,
		},
		sfx_trucizna_tik = {
			poczatek = 42.1221,
			koniec = 43.1527,
			atak = 0.04,
			szczyt = 0.08,
			glosnosc = 0.6,
		},
		sfx_umiejetnosc_rzut = {
			poczatek = 43.5027,
			koniec = 44.8285,
			atak = 0.35,
			szczyt = 0.78,
			glosnosc = 0.8,
		},
		sfx_unik = {
			poczatek = 45.1785,
			koniec = 45.8346,
			atak = 0.09,
			szczyt = 0.18,
			glosnosc = 0.8,
		},
		sfx_wilk_warkniecie = {
			poczatek = 46.1846,
			koniec = 48.2576,
			atak = 0.01,
			szczyt = 0.35,
			glosnosc = 0.8,
		},
		sfx_zarodniki = {
			poczatek = 48.6075,
			koniec = 49.7927,
			atak = 0.04,
			szczyt = 0.1,
			glosnosc = 0.8,
		},
	},
	zdarzenia = {
		awans = {
			efekt = "sfx_awans_poziom",
			uderzenie = false,
		},
		blok = {
			efekt = "sfx_blok_tarcza",
			uderzenie = true,
		},
		chmury = {
			efekt = "sfx_przejscie_chmury",
			uderzenie = false,
		},
		cios = {
			efekt = "sfx_cios_trafiony",
			uderzenie = true,
		},
		galareta = {
			efekt = "sfx_galareta_plusk",
			uderzenie = true,
		},
		krytyk = {
			efekt = "sfx_cios_krytyczny",
			uderzenie = true,
		},
		kula_ognia = {
			efekt = "sfx_kula_ognia",
			uderzenie = true,
		},
		lodowy_pocisk = {
			efekt = "sfx_lodowy_pocisk",
			uderzenie = true,
		},
		monety = {
			efekt = "sfx_monety",
			uderzenie = false,
		},
		ogluszenie = {
			efekt = "sfx_ogluszenie",
			uderzenie = false,
		},
		porazka = {
			efekt = "sfx_porazka",
			uderzenie = false,
		},
		przycisk = {
			efekt = "sfx_klik_przycisk",
			uderzenie = false,
		},
		ryk_straznika = {
			efekt = "sfx_ryk_kolos",
			uderzenie = false,
		},
		rzut = {
			efekt = "sfx_umiejetnosc_rzut",
			uderzenie = false,
		},
		tarcza = {
			efekt = "sfx_tarcza_magiczna",
			uderzenie = false,
		},
		tik_podpalenie = {
			efekt = "sfx_podpalenie_tik",
			uderzenie = false,
		},
		tik_trucizna = {
			efekt = "sfx_trucizna_tik",
			uderzenie = false,
		},
		troll = {
			efekt = "sfx_troll_chrzakniecie",
			uderzenie = false,
		},
		unik = {
			efekt = "sfx_unik",
			uderzenie = true,
		},
		wilk = {
			efekt = "sfx_wilk_warkniecie",
			uderzenie = false,
		},
		zarodniki = {
			efekt = "sfx_zarodniki",
			uderzenie = false,
		},
		zwyciestwo = {
			efekt = "sfx_fanfara_zwyciestwa",
			uderzenie = false,
		},
	},
	glosyPotworow = {
		bulgotnik = "zarodniki",
		cierniowy_wilk = "wilk",
		klodoklap = "wilk",
		lesny_slime = "galareta",
		lesny_troll = "troll",
		muchomornik = "zarodniki",
		rechotek = "galareta",
		ropucha_z_chatka = "troll",
		straznik_lasu = "ryk_straznika",
		straznik_topieli = "ryk_straznika",
	},
	muzyka = {
		przejscie = 2.5,
		przyciszenieWalki = 0.6,
		przyciszenieCzas = 0.8,
		strefy = {
			bazar = {
				glosnosc = 0.8,
				podpiete = true,
				utwory = {
					{
						nazwa = "muzyka_02_bazar_targ_petla",
						id = 94425435537814,
					},
					{
						nazwa = "muzyka_03_bazar_rzemieslnicy_petla",
						id = 116217836078354,
					},
					{
						nazwa = "muzyka_04_bazar_wieczor_petla",
						id = 75722490819761,
					},
				},
				kontener = "MiasteczkoBazar",
				prostokaty = {
					{ 882.0, 1066.0, -790.0, -610.0 },
				},
			},
			las = {
				glosnosc = 0.8,
				podpiete = true,
				utwory = {
					{
						nazwa = "muzyka_05_las_a_petla",
						id = 70497074484606,
					},
					{
						nazwa = "muzyka_05_las_b_petla",
						id = 106582652985449,
					},
				},
				kontener = "LasPas",
				prostokaty = {
					{ 1066.0, 1543.92, -784.0, -616.0 },
				},
			},
			bagno = {
				glosnosc = 0.7,
				podpiete = true,
				utwory = {
					{
						nazwa = "muzyka_05_las_a_petla",
						id = 70497074484606,
					},
					{
						nazwa = "muzyka_05_las_b_petla",
						id = 106582652985449,
					},
				},
				kontener = "BagnoPas",
				prostokaty = {
					{ 1543.92, 1966.0, -784.0, -616.0 },
				},
			},
			start = {
				glosnosc = 0.8,
				podpiete = true,
				utwory = {
					{
						nazwa = "muzyka_02_bazar_targ_petla",
						id = 94425435537814,
					},
					{
						nazwa = "muzyka_03_bazar_rzemieslnicy_petla",
						id = 116217836078354,
					},
					{
						nazwa = "muzyka_04_bazar_wieczor_petla",
						id = 75722490819761,
					},
				},
				kontener = "DemoLesnaBaza",
				prostokaty = {
					{ -125.0, 125.0, -125.0, 125.0 },
				},
			},
			miasteczko = {
				glosnosc = 0.8,
				podpiete = true,
				utwory = {
					{
						nazwa = "muzyka_02_bazar_targ_petla",
						id = 94425435537814,
					},
					{
						nazwa = "muzyka_03_bazar_rzemieslnicy_petla",
						id = 116217836078354,
					},
					{
						nazwa = "muzyka_04_bazar_wieczor_petla",
						id = 75722490819761,
					},
				},
				kontener = "KrzyweMiasteczko",
				prostokaty = {
					{ -300.0, 400.0, -960.0, -440.0 },
				},
			},
			bor = {
				glosnosc = 0.8,
				podpiete = true,
				utwory = {
					{
						nazwa = "muzyka_05_las_a_petla",
						id = 70497074484606,
					},
					{
						nazwa = "muzyka_05_las_b_petla",
						id = 106582652985449,
					},
				},
				kontener = "BiomLas",
				prostokaty = {
					{ -700.0, 700.0, -2700.0, -1300.0 },
				},
			},
			menu = {
				glosnosc = 0.35,
				podpiete = false,
				utwory = {
					{
						nazwa = "muzyka_01_menu_a_petla",
						id = 0,
					},
					{
						nazwa = "muzyka_01_menu_b_petla",
						id = 0,
					},
				},
				prostokaty = {  },
			},
		},
	},
}
