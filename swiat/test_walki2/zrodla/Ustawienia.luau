--[[
	Ustawienia — wspólne stałe prototypu walki v2 (serwer, klient i skrypty budujące czytają je z jednego miejsca).
	Tu NIE ma statystyk: postać wzorcową i przeciwnika buduje serwer z danych silnika (Moduly/Walka/Dane).
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local U = {}

U.WERSJA = "prototyp v2 — etap 2: serwer, odtwarzacz, interfejs (2026-11-14)"
U.NAZWA_KONTENERA = "TestWalki2"

------------------------------------------------------------------ arena
-- Polana w lesie na południe od placu (spawn w (0, 0, 0), las dema kończy się na z ≈ 115). v1 stoi na wschodzie (190, 0, 0).
U.SRODEK = Vector3.new(0, 0, 250) -- środek podestu na poziomie płyty Baseplate
U.PROMIEN_PODESTU = 22
U.WYSOKOSC_PODESTU = 1.0

-- Układ SCENY (lokalny): X = w prawo na ekranie, Y = w górę, Z = do kamery (kamera planu ogólnego patrzy wzdłuż −Z,
-- czyli na południe, ze słońcem za plecami). Gracz stoi po lewej (−X), przeciwnik po prawej (+X).
function U.scena(): CFrame
	local p = U.SRODEK + Vector3.new(0, U.WYSOKOSC_PODESTU, 0)
	return CFrame.lookAt(p, p + Vector3.new(0, 0, 1)) -- LookVector = świat +Z, więc lokalne −Z sceny = południe
end

-- CFrame ZIEMI pod aktorem (tak ustawia się aktora: Aktorzy.nowy / aktor:ustaw), przodem do przeciwnika.
-- odstep = odległość między punktami stania (domyślnie U.ODSTEP); kolejny etap dobierze ją do promieni aktorów.
U.ODSTEP = 10
function U.miejsce(strona: string, odstep: number?): CFrame
	local d = (odstep or U.ODSTEP) / 2
	local znak = if strona == "gracz" then -1 else 1
	return U.scena() * CFrame.lookAt(Vector3.new(znak * d, 0, 0), Vector3.new(0, 0, 0))
end

-- Pudło sceny (to samo, które zbuduj.py sprawdza przed budową — musi być wolne od cudzych obiektów).
U.OBSZAR_SRODEK = Vector3.new(-6, 100, 252)
U.OBSZAR_ROZMIAR = Vector3.new(140, 400, 124)
U.TAG_UKRYJ = "TestWalki2Ukryj"

------------------------------------------------------------------ galeria szablonów aktorów
-- Szablony stoją w rzędzie na północ od podestu, przodem do nadchodzących graczy (na północ). W walce klient klonuje
-- je lokalnie — w kadrze walki ich nie widać (stoją za kamerą planu ogólnego).
U.GALERIA_START = Vector3.new(-62, 0, 214)
U.GALERIA_KROK = 2.5 -- odstęp między krawędziami sąsiednich aktorów (studs)

------------------------------------------------------------------ aktorzy
-- Komiksowy obrys aktorów (opcja prototypu; do porównania w README / klatki/obrys_*):
--   "brak"      — bez obrysu,
--   "highlight" — obiekt Highlight na modelu (cienka czarna linia po sylwetce, 1 instancja na aktora),
--   "skorupa"   — czarna, powiększona kopia każdej bryły-klocka z odwróconymi ścianami (ujemna skala siatki
--                 rbxasset://fonts/leftarm.mesh; grubsza linia, ok. 1,4–1,9× więcej części; kliny i walce bez obrysu).
U.OBRYS = "brak"
U.OBRYS_GRUBOSC = 0.07 -- skorupa: o tyle studów bryła rośnie z każdej strony
U.OBRYS_MIN = 0.12 -- skorupa: bryły cieńsze niż to (oczy, nity) nie dostają skorupy
U.POKAZ_PUNKTOW = false -- true: punkty aktorów (Punkt_*) jako małe świecące kulki — do sprawdzania danych
U.PRZEJSCIE_KLIPOW = 0.15 -- s: domyślne płynne przejście między klipami

------------------------------------------------------------------ dźwięki wbudowane w klienta Roblox (nie są to uploady)
--[[ Klient Roblox ma wbudowanych tylko 11 plików dźwięku (content/sounds; sprawdzone 15.11.2026 w instalacji
	klienta i Studia): action_falling (10 s szumu wiatru), action_footsteps_plastic, action_get_up, action_jump,
	action_jump_land, action_swim, impact_explosion_03, impact_water, oof, ouch, volume_slider (czysty ton ok. 390 Hz).
	Z nich robimy wszystko: różna prędkość odtwarzania (wysokość), krótsze wycięcie (maks = s pliku, potem stop),
	a melodie zwycięstwa i porażki to cztery „nuty” z volume_slider. Głośność wyrównana do szczytów plików
	(jump_land ma szczyt −20 dB, wybuch 0 dB). Pociski, czary i strzała nie mają własnych odgłosów — to świst skoku
	(action_jump) w innej wysokości. ]]
U.DZWIEKI_WLACZONE = true
U.GLOSNOSC = 0.5 -- mnożnik wszystkich dźwięków walki (umiarkowanie)
U.DZWIEKI_NARAZ = 3 -- najwyżej tyle naraz (przy ×4 dźwięki nie zlewają się w hałas)
local S = "rbxasset://sounds/"
U.DZWIEKI = {
	cios = { id = S .. "action_jump_land.mp3", glosnosc = 2.2, szybkosc = 1.0 },
	krytyk = { id = S .. "impact_explosion_03.mp3", glosnosc = 0.34, szybkosc = 1.25, maks = 0.9 },
	blok = { id = S .. "action_jump_land.mp3", glosnosc = 2.4, szybkosc = 1.9 },
	unik = { id = S .. "action_jump.mp3", glosnosc = 1.4, szybkosc = 1.25 },
	strzal = { id = S .. "action_jump.mp3", glosnosc = 1.2, szybkosc = 1.75 },
	czar = { id = S .. "action_get_up.mp3", glosnosc = 1.6, szybkosc = 1.3 },
	wybuch = { id = S .. "impact_explosion_03.mp3", glosnosc = 0.22, szybkosc = 1.6, maks = 0.6 },
	plusk = { id = S .. "impact_water.mp3", glosnosc = 0.5, szybkosc = 1.15, maks = 0.8 },
	upadek = { id = S .. "oof.ogg", glosnosc = 0.32, szybkosc = 1.0 },
	lomot = { id = S .. "action_jump_land.mp3", glosnosc = 2.6, szybkosc = 0.55 },
	nuta = { id = S .. "volume_slider.ogg", glosnosc = 0.55, szybkosc = 1.0, maks = 0.3 },
	przycisk = { id = S .. "volume_slider.ogg", glosnosc = 0.45, szybkosc = 1.0, maks = 0.3 },
	lup = { id = S .. "volume_slider.ogg", glosnosc = 0.4, szybkosc = 2.4, maks = 0.2 },
}
-- melodie finału: prędkości „nuty” (1 = ok. 390 Hz) i odstęp w sekundach
U.MELODIE = {
	zwyciestwo = { nuty = { 1.0, 1.26, 1.5, 2.0 }, odstep = 0.11 },
	porazka = { nuty = { 1.0, 0.84, 0.71, 0.53 }, odstep = 0.17 },
}

------------------------------------------------------------------ kolory (kierunek artystyczny: nasycone barwy, ciemny obrys)
local function hex(h: string): Color3
	return Color3.fromHex(h)
end
U.KOLORY = {
	tusz = hex("#17121F"),
	bialy = hex("#FFFFFF"),
	krem = hex("#FFF3D1"),
	zolty = hex("#FFD23F"),
	pomarancz = hex("#FF8A1F"),
	czerwony = hex("#E8364F"),
	roz = hex("#FF7A8A"),
	turkus = hex("#3FF2D0"),
	blekit = hex("#27B6F2"),
	niebieski = hex("#2F6FE0"),
	zielony = hex("#52D273"),
	fiolet = hex("#7B4DFF"),
	szary = hex("#8D93A6"),
	ciemny = hex("#2B2238"),
	-- rodzaje obrażeń (dziennik v2): fizyczne i magiczne muszą się różnić kolorem
	fizyczne = hex("#FFFFFF"),
	magiczne = hex("#B07CFF"),
}

return U
