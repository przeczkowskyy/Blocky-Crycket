--[[
	Ustawienia — wspólne stałe testu walki 3D (serwer, klient i skrypty budujące czytają je z jednego miejsca).
	Tu NIE ma statystyk postaci: te zna tylko serwer (SerwerWalki), klient dostaje gotowy dziennik.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local U = {}

U.WERSJA = "prototyp 0.2 (2026-11-13)"
U.NAZWA_KONTENERA = "TestWalki"

------------------------------------------------------------------ arena
U.SRODEK = Vector3.new(190, 0, 0) -- środek podestu na poziomie płyty Baseplate (na wschód od dema)
U.BOK_PODESTU = 44
U.WYSOKOSC_PODESTU = 1.2
U.ODSTEP = 9 -- odległość między aktorami w spoczynku (wzdłuż osi Z)
U.BIODRA = 3.0 -- środek HumanoidRootPart nad podłogą (rig R15 z domyślnego opisu)

-- Podłoga podestu jako układ odniesienia sceny: X = wschód, Y = góra, Z = południe.
-- Kamera patrzy od zachodu (od strony placu i słońca), więc na ekranie lewa strona to −Z (Rycerz),
-- a prawa to +Z (Zbir).
function U.podloga(): CFrame
	return CFrame.new(U.SRODEK.X, U.SRODEK.Y + U.WYSOKOSC_PODESTU, U.SRODEK.Z)
end

-- CFrame HumanoidRootPart aktora w spoczynku: stoi przodem do przeciwnika.
function U.miejsce(strona: string): CFrame
	local znak = if strona == "gracz" then -1 else 1
	local p = U.podloga().Position + Vector3.new(0, U.BIODRA, znak * U.ODSTEP / 2)
	return CFrame.lookAt(p, p - Vector3.new(0, 0, znak))
end

U.AKTORZY = { gracz = "Rycerz", wrog = "Zbir" }

-- Obszar sceny: to samo pudło, które zbuduj.py sprawdza przed budową (musi być wolne). Wszystko obce, co w czasie
-- walki znajdzie się w nim (inni gracze, ich pety, pociski), klient chowa lokalnie na czas cutscenki.
U.OBSZAR_PRZESUNIECIE = Vector3.new(4, 100, 0) -- środek pudła względem U.SRODEK
U.OBSZAR_ROZMIAR = Vector3.new(112, 400, 104)
-- Tag CollectionService dla obiektów, które gra chce chować w każdej cutscence, gdziekolwiek są (pety, pociski,
-- efekty z CanQuery = false, których zapytanie przestrzenne nie widzi). Prototyp go tylko czyta.
U.TAG_UKRYJ = "TestWalkiUkryj"

------------------------------------------------------------------ animacje
-- Domyślne animacje R15 — identyfikatory odczytane w trybie Play z Character.Animate (13.11.2026).
-- Odtwarzacz i tak czyta je na żywo ze skryptu Animate postaci gracza; ta tabela to zapas.
U.ANIMACJE = {
	idle = "rbxassetid://507766388",
	toolnone = "rbxassetid://507768375",
	toolslash = "rbxassetid://522635514",
	toollunge = "rbxassetid://522638767",
	cheer = "rbxassetid://507770677",
	laugh = "rbxassetid://507770818",
}

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
	tusz = hex("#17121F"), -- obrysy i cienie interfejsu
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
}

return U
