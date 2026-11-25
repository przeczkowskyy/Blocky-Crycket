--[[
	JajkaBiomowDane — dane animacji jajek Bagna i Dżungli (swiat/jajka_biomow, Karol 25.11.2026; PROPOZYCJA).
	Docelowo ModuleScript w ReplicatedStorage.Shared (src/shared/JajkaBiomowDane.luau) — przenosi etap „Studio”.
	Czytają go: JajkaBiomowSpoczynek (ruch w spoczynku i reakcja ozdób na finał wyklucia) oraz klient scenki wyklucia
	Pawła po uogólnieniu na kilka jajek (src/client/JajkoKoroweClient.client.luau: kolory, rdzeń, kawałki, tempo).

	Jednostki: czas w s, kąty w radianach, odległości w studach PRZED skalą modelu (mnożyć przez model:GetScale(),
	modele stoją w skali 1,5). Wartości „wspolne” to liczby z klienta Pawła dla leśnego jaja (żeby nowe jajka
	pękały tak samo); w „jajka” tylko to, co inne.

	Umowa ze scenką (klient Pawła): na czas scenki ustawia na modelu atrybut Wyklucie = true (spoczynek nie rusza
	wtedy Egg ani blasku), w chwili BOOM zwiększa atrybut Final o 1 (ozdoby grają „ozdobyFinal”), po scenie
	Wyklucie = false.
]]

local D = {}

D.wspolne = {
	kontener = "JajkaBiomowPodglad",
	kawalki = { "ShellBottom", "ShellTopLeft", "ShellTopRight" }, -- w spoczynku Transparency = 1
	jajo = "Egg",
	korzen = "Korzen", -- PrimaryPart, najniższy punkt modelu, LookVector = przód (kamera scenki)
	rdzenY = 1.59, -- środek świecącego rdzenia nad korzeniem (kula 1,35 spłaszczona do połowy)
	rdzenSrednica = 1.35,
	slupOdY = 1.66, -- słup światła od tej wysokości w górę
	slupWys = 7,
	spoczynek = {
		kolysanie = 0.012, -- amplituda bujania jaja wokół korzenia (rad)
		okresZ = 2 * math.pi / 1.6, -- bujanie na boki (sin(t·1,6))
		okresX = 2 * math.pi / 1.1, -- bujanie przód–tył (×0,6 amplitudy)
		blask = 0.55, -- EmissiveStrength żył w spoczynku
		puls = 0.15, -- głębokość pulsu blasku: blask · (0,85 + 0,15·sin(t·(2 + blask·6)))
	},
	wyklucie = {
		kliki = 5, -- 4 szarpnięcia + BOOM
		czekajS = 7, -- bez kliknięcia scenka idzie dalej sama
		naKlik = { trzesienie = 0.008, blask = 0.28, iskry = { 4, 2 } }, -- ×numer kliknięcia (iskry: 4 + 2·i)
		szarpniecieS = 0.35, -- szarpnięcie gaśnie w tym czasie, amplituda +0,07 rad
		final = {
			trzesienie = 0.05,
			blask = 1.65,
			odlotPrawy = { kawalek = "ShellTopRight", wGore = 3.4, wBok = 2.3 }, -- prędkości ×skala, grawitacja 5,2×skala
			przerwaS = 0.95,
			odlotLewy = { kawalek = "ShellTopLeft", wGore = 3.2, wBok = 2.7 },
			iskry = { 18, 45 },
			swiatlo = { 3, 6 }, -- jasność PointLight rdzenia: po pierwszym odlocie, po drugim
			petPoS = 0.45, -- pet wyłania się ze słupa
			wzlotS = 0.9,
			trwaS = 3.1,
			slupGasnieS = 0.5,
			grawitacja = 5.2,
			kawalekZnikaPoS = 1.5, -- potem 0,35 s zanikania
		},
	},
}

-- ruchy ozdób (cała siatka MeshPart rusza się jako jedna bryła; punkt obrotu = środek dolnej ściany jej ramki):
--   wiatr      — obrót wokół osi poziomej prostopadłej do wiatru: amplituda, okres, faza
--   kolysanie  — obrót wokół osi pionowej przez środek siatki: amplituda, okres
--   unoszenie  — przesunięcie w górę i w dół: wysokosc, okres
--   pulsNeonu  — Transparency między przezroczystosc[1] a [2]: okres
--   pulsKoloru — Color rozjaśniany do bieli o „jasniej” (0..1): okres
-- reakcje na finał (czas od BOOM):
--   odchylenie — wychylenie od jaja o kąt w czasie „czas”, powrót sprężyną w „powrotS”
--   pekniecie  — powiększenie o „skala” w „czas”, zniknięcie, powrót po „powrotPoS” (Transparency z tabeli KOLORY)
--   blysk      — Color = kolor rdzenia (rzadkości) lub kolorZyl na „czas”, potem powrót
D.jajka = {
	jajko_bagienne = {
		model = "Jajko Bagna",
		biom = "bagno",
		kolorZyl = Color3.fromRGB(155, 255, 79), -- EmissiveTint pęknięć, iskry, PointLight
		kolorBlasku = Color3.fromHex("F4FFD2"), -- jasny środek rdzenia i słupa
		wiatr = Vector3.new(1, 0, 0.35), -- kierunek wiatru (świat)
		ozdobySpoczynek = {
			{ czesc = "Reeds", ruch = "wiatr", amplituda = 0.03, okres = 3.6, faza = 0 },
			{ czesc = "Lilies", ruch = "kolysanie", amplituda = 0.035, okres = 5.0, faza = 1 },
			{ czesc = "Bubbles", ruch = "unoszenie", wysokosc = 0.05, okres = 2.4, faza = 0.5 },
			{ czesc = "Bubbles", ruch = "pulsNeonu", przezroczystosc = { 0.1, 0.5 }, okres = 1.7, faza = 0 },
			{ czesc = "Crystals", ruch = "pulsKoloru", jasniej = 0.35, okres = 2.9, faza = 0 },
			{ czesc = "Shards", ruch = "pulsKoloru", jasniej = 0.35, okres = 2.9, faza = 1.4 },
			{ czesc = "MushroomSpots", ruch = "pulsKoloru", jasniej = 0.45, okres = 1.9, faza = 0.8 },
		},
		ozdobyFinal = {
			{ czesc = "Bubbles", ruch = "pekniecie", t = 0, czas = 0.22, skala = 1.7, powrotPoS = 4.5 },
			{ czesc = "Reeds", ruch = "odchylenie", t = 0, czas = 0.3, kat = 0.14, powrotS = 1.4 },
			{ czesc = "Crystals", ruch = "blysk", t = 0, czas = 0.8 },
			{ czesc = "MushroomSpots", ruch = "blysk", t = 0.1, czas = 0.8 },
		},
	},
	jajko_dzungli = {
		model = "Jajko Dżungli",
		biom = "dzungla",
		kolorZyl = Color3.fromRGB(255, 95, 168),
		kolorBlasku = Color3.fromHex("FFE6F3"),
		wiatr = Vector3.new(1, 0, -0.25),
		ozdobySpoczynek = {
			{ czesc = "BigLeaves", ruch = "wiatr", amplituda = 0.018, okres = 4.2, faza = 0 },
			{ czesc = "Flowers", ruch = "kolysanie", amplituda = 0.03, okres = 3.1, faza = 0.7 },
			{ czesc = "Crystals", ruch = "pulsKoloru", jasniej = 0.3, okres = 3.3, faza = 0 },
			{ czesc = "Shards", ruch = "pulsKoloru", jasniej = 0.3, okres = 3.3, faza = 1.6 },
		},
		ozdobyFinal = {
			{ czesc = "BigLeaves", ruch = "odchylenie", t = 0, czas = 0.28, kat = 0.1, powrotS = 1.6 },
			{ czesc = "Flowers", ruch = "odchylenie", t = 0.05, czas = 0.25, kat = 0.12, powrotS = 1.2 },
			{ czesc = "Crystals", ruch = "blysk", t = 0, czas = 0.9 },
			{ czesc = "Shards", ruch = "blysk", t = 0.1, czas = 0.9 },
		},
	},
}

return D
