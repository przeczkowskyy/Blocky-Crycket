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
U.DZWIEKI_WLACZONE = true
U.DZWIEKI = {
	cios = "rbxasset://sounds/action_jump_land.mp3",
	krytyk = "rbxasset://sounds/impact_explosion_03.mp3",
	upadek = "rbxasset://sounds/action_falling.ogg",
	przycisk = "rbxasset://sounds/volume_slider.ogg",
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
