--[[
	Budowa areny testowej (uruchamiane w Roblox Studio, tryb Edit, przez zbuduj.py → execute_luau).
	Tworzy WYŁĄCZNIE Workspace/TestWalki/Arena. Kontener musi już istnieć i mieć atrybut Wygenerowane.

	Układ: środek podestu w Ustawienia.SRODEK; X = wschód, Z = południe. Wejście, tablica i świecący słup
	są po stronie zachodniej (od placu), tło — murek, baszty z chorągwiami i drzewa — po wschodniej.

	Poza Studio arena nie przetrwa startu serwera: SerwerWalki usuwa wtedy cały kontener (patrz README, Bezpieczeństwo).
]]
local kontener = workspace:FindFirstChild("TestWalki")
if not kontener or kontener:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera Workspace/TestWalki z atrybutem Wygenerowane"
end
local U = require(kontener.Moduly.Ustawienia)

local stara = kontener:FindFirstChild("Arena")
if stara then
	stara:Destroy()
end

local O = CFrame.new(U.SRODEK) -- poziom płyty Baseplate
local B = U.BOK_PODESTU / 2
local H = U.WYSOKOSC_PODESTU
local M = Enum.Material
local licznik = 0

local arena = Instance.new("Model")
arena.Name = "Arena"

local function grupa(nazwa: string): Model
	local m = Instance.new("Model")
	m.Name = nazwa
	m.Parent = arena
	return m
end

-- opcje: k = false → bez kolizji; c = false → bez cienia; t = przezroczystość
local function czesc(rodzic: Instance, klasa: string, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: string, material: Enum.Material?, opcje: any?)
	local p = Instance.new(klasa) :: BasePart
	p.Name = nazwa
	p.Anchored = true
	p.Size = rozmiar
	p.CFrame = O * cf
	p.Color = Color3.fromHex(kolor)
	p.Material = material or M.SmoothPlastic
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.CanTouch = false
	if opcje then
		if opcje.k == false then
			p.CanCollide = false
			p.CanQuery = false
		end
		if opcje.c == false then
			p.CastShadow = false
		end
		if opcje.t then
			p.Transparency = opcje.t
		end
	end
	p.Parent = rodzic
	licznik += 1
	return p
end
local function blok(rodzic, nazwa, rozmiar, cf, kolor, material, opcje)
	return czesc(rodzic, "Part", nazwa, rozmiar, cf, kolor, material, opcje)
end
-- walec leżący płasko (oś pionowa): średnica d, grubość g
local function krazek(rodzic, nazwa, d: number, g: number, poz: Vector3, kolor, material, opcje)
	local p = czesc(rodzic, "Part", nazwa, Vector3.new(g, d, d), CFrame.new(poz) * CFrame.Angles(0, 0, math.rad(90)), kolor, material, opcje)
	p.Shape = Enum.PartType.Cylinder
	return p
end
-- walec stojący bokiem (oś wzdłuż X): tarcza na ścianie zwrócona na zachód
local function tarcza(rodzic, nazwa, d: number, g: number, poz: Vector3, kolor, material, opcje)
	local p = czesc(rodzic, "Part", nazwa, Vector3.new(g, d, d), CFrame.new(poz), kolor, material, opcje)
	p.Shape = Enum.PartType.Cylinder
	return p
end

local TUSZ = "#2B2238"
local KAMIEN, KAMIEN_J, KAMIEN_C = "#9AA0A8", "#B4B9BF", "#6C727A"
local DREWNO, DREWNO_J = "#5A3A22", "#8A5A34"

------------------------------------------------------------------ podłoże i podest
local podloze = grupa("Podloze")
blok(podloze, "Trawa", Vector3.new(104, 0.2, 96), CFrame.new(4, 0.1, 0), "#5FB548", M.Grass, { c = false })
blok(podloze, "Sciezka", Vector3.new(14, 0.24, 8), CFrame.new(-31, 0.12, 0), "#C9A66B", M.Ground, { c = false })

local podest = grupa("Podest")
blok(podest, "Cokol", Vector3.new(2 * B, H - 0.3, 2 * B), CFrame.new(0, (H - 0.3) / 2, 0), TUSZ, M.Slate)
blok(podest, "Plyta", Vector3.new(2 * B - 1.2, 0.3, 2 * B - 1.2), CFrame.new(0, H - 0.15, 0), "#EBC873", M.Sand)
krazek(podest, "KragObrys", 25, 0.06, Vector3.new(0, H + 0.03, 0), TUSZ, M.SmoothPlastic, { k = false, c = false })
krazek(podest, "KragCzerwony", 23.6, 0.08, Vector3.new(0, H + 0.04, 0), "#D9483B", M.SmoothPlastic, { k = false, c = false })
krazek(podest, "KragSrodek", 20, 0.1, Vector3.new(0, H + 0.05, 0), "#F6DD9A", M.Sand, { k = false, c = false })
-- znaczniki miejsc startowych (lewy niebieski, prawy czerwony)
krazek(podest, "ZnakGracza", 4.6, 0.12, Vector3.new(0, H + 0.06, -U.ODSTEP / 2), "#2F6FE0", M.SmoothPlastic, { k = false, c = false })
krazek(podest, "ZnakWroga", 4.6, 0.12, Vector3.new(0, H + 0.06, U.ODSTEP / 2), "#D9483B", M.SmoothPlastic, { k = false, c = false })
krazek(podest, "ZnakGraczaSrodek", 3.6, 0.14, Vector3.new(0, H + 0.07, -U.ODSTEP / 2), "#F6DD9A", M.Sand, { k = false, c = false })
krazek(podest, "ZnakWrogaSrodek", 3.6, 0.14, Vector3.new(0, H + 0.07, U.ODSTEP / 2), "#F6DD9A", M.Sand, { k = false, c = false })
-- schodki od zachodu
blok(podest, "SchodekGorny", Vector3.new(1.2, 0.8, 10), CFrame.new(-B - 0.6, 0.4, 0), KAMIEN_J, M.Cobblestone)
blok(podest, "SchodekDolny", Vector3.new(1.2, 0.4, 10), CFrame.new(-B - 1.8, 0.2, 0), KAMIEN, M.Cobblestone)

------------------------------------------------------------------ murek (północ, wschód, południe) z blankami
local murek = grupa("Murek")
local function sciana(nazwa: string, wzdluzX: boolean, stala: number, wys: number)
	local dl = 2 * B - 4.4 -- między basztami / słupkami
	local grub = 1.4
	local rozm = if wzdluzX then Vector3.new(dl, wys, grub) else Vector3.new(grub, wys, dl)
	local poz = if wzdluzX then Vector3.new(0, H + wys / 2, stala) else Vector3.new(stala, H + wys / 2, 0)
	blok(murek, nazwa, rozm, CFrame.new(poz), KAMIEN, M.Cobblestone)
	local rozmCz = if wzdluzX then Vector3.new(dl + 0.3, 0.35, grub + 0.4) else Vector3.new(grub + 0.4, 0.35, dl + 0.3)
	blok(murek, nazwa .. "Czapa", rozmCz, CFrame.new(poz + Vector3.new(0, wys / 2 + 0.175, 0)), TUSZ, M.Slate)
	local ile = 8
	for i = 1, ile do
		local u = -dl / 2 + (i - 0.5) * dl / ile
		local p = if wzdluzX then Vector3.new(u, H + wys + 0.35 + 0.45, stala) else Vector3.new(stala, H + wys + 0.35 + 0.45, u)
		blok(murek, nazwa .. "Blanka", Vector3.new(1.5, 0.9, 1.5), CFrame.new(p), KAMIEN_J, M.Cobblestone)
	end
end
sciana("ScianaPolnocna", true, -B + 0.9, 1.5)
sciana("ScianaPoludniowa", true, B - 0.9, 1.5)
sciana("ScianaWschodnia", false, B - 0.9, 2.6)

-- kolorowe tarcze na wschodniej ścianie (tło planu ogólnego)
local kolory = { "#D9483B", "#2F6FE0", "#F5B82E", "#3F9B3A", "#8B5CF6" }
for i, kolor in kolory do
	local z = -14 + (i - 1) * 7
	tarcza(murek, "TarczaObrys", 3.1, 0.2, Vector3.new(B - 1.75, H + 1.6, z), TUSZ, M.SmoothPlastic, { k = false })
	tarcza(murek, "Tarcza", 2.6, 0.24, Vector3.new(B - 1.85, H + 1.6, z), kolor, M.SmoothPlastic, { k = false })
	tarcza(murek, "TarczaGuz", 0.8, 0.3, Vector3.new(B - 1.95, H + 1.6, z), "#FFD76A", M.Metal, { k = false })
end

-- słupki przy wejściu (zachód)
for _, z in { -B + 1.1, B - 1.1 } do
	blok(murek, "Slupek", Vector3.new(2.2, 3.0, 2.2), CFrame.new(-B + 1.1, H + 1.5, z), KAMIEN, M.Cobblestone)
	blok(murek, "SlupekCzapa", Vector3.new(2.7, 0.4, 2.7), CFrame.new(-B + 1.1, H + 3.2, z), TUSZ, M.Slate)
	blok(murek, "SlupekKula", Vector3.new(1.3, 1.3, 1.3), CFrame.new(-B + 1.1, H + 4.05, z) * CFrame.Angles(0, math.rad(45), 0), "#F5B82E", M.Metal)
end

------------------------------------------------------------------ baszty z chorągwiami (narożniki wschodnie)
local choragwie = grupa("Choragwie")
local function baszta(nazwa: string, z: number, kolorFlagi: string, kolorZnaku: string)
	local x = B - 1.2
	blok(choragwie, nazwa .. "Baszta", Vector3.new(4.2, 4.6, 4.2), CFrame.new(x, H + 2.3, z), KAMIEN, M.Cobblestone)
	blok(choragwie, nazwa .. "BasztaCzapa", Vector3.new(4.9, 0.5, 4.9), CFrame.new(x, H + 4.85, z), TUSZ, M.Slate)
	for _, d in { Vector3.new(-1.7, 0, -1.7), Vector3.new(1.7, 0, -1.7), Vector3.new(-1.7, 0, 1.7), Vector3.new(1.7, 0, 1.7) } do
		blok(choragwie, nazwa .. "BasztaBlanka", Vector3.new(1.3, 0.9, 1.3), CFrame.new(x + d.X, H + 5.55, z + d.Z), KAMIEN_J, M.Cobblestone)
	end
	local yMaszt = H + 5.1
	blok(choragwie, nazwa .. "Maszt", Vector3.new(0.5, 11, 0.5), CFrame.new(x, yMaszt + 5.5, z), DREWNO, M.Wood)
	blok(choragwie, nazwa .. "MasztKula", Vector3.new(0.95, 0.95, 0.95), CFrame.new(x, yMaszt + 11.4, z) * CFrame.Angles(0, math.rad(45), 0), "#F5B82E", M.Metal)
	blok(choragwie, nazwa .. "Poprzeczka", Vector3.new(0.4, 0.4, 4.4), CFrame.new(x - 0.45, yMaszt + 10.3, z), DREWNO, M.Wood)
	-- płat chorągwi zwrócony na zachód: ciemny podkład jako obrys + barwny płat + znak
	local yFlagi = yMaszt + 10.1 - 3.2
	blok(choragwie, nazwa .. "FlagaObrys", Vector3.new(0.12, 6.9, 4.3), CFrame.new(x - 0.5, yFlagi, z), TUSZ, M.Fabric, { k = false })
	blok(choragwie, nazwa .. "Flaga", Vector3.new(0.16, 6.4, 3.8), CFrame.new(x - 0.58, yFlagi, z), kolorFlagi, M.Fabric, { k = false })
	blok(choragwie, nazwa .. "FlagaPas", Vector3.new(0.18, 0.7, 3.8), CFrame.new(x - 0.6, yFlagi - 2.4, z), "#FFD23F", M.Fabric, { k = false, c = false })
	blok(choragwie, nazwa .. "FlagaZnak", Vector3.new(0.18, 1.9, 1.9), CFrame.new(x - 0.62, yFlagi + 0.6, z) * CFrame.Angles(math.rad(45), 0, 0), kolorZnaku, M.Fabric, { k = false, c = false })
end
baszta("ChoragiewRycerza", -B + 1.2, "#2F6FE0", "#FFD23F")
baszta("ChoragiewZbira", B - 1.2, "#D9483B", "#2B2238")

------------------------------------------------------------------ tablica z podpowiedzią (na zachód od podestu, obok schodków)
local tablica = grupa("Tablica")
local tx, tz = -B - 4.2, -9.5
blok(tablica, "NogaLewa", Vector3.new(0.6, 5.2, 0.6), CFrame.new(tx, 2.6, tz - 3.1), DREWNO, M.Wood)
blok(tablica, "NogaPrawa", Vector3.new(0.6, 5.2, 0.6), CFrame.new(tx, 2.6, tz + 3.1), DREWNO, M.Wood)
blok(tablica, "DeskaObrys", Vector3.new(0.4, 4.2, 7.6), CFrame.new(tx + 0.05, 3.7, tz), TUSZ, M.Wood)
local deska = blok(tablica, "Deska", Vector3.new(0.5, 3.6, 7.0), CFrame.new(tx - 0.1, 3.7, tz), "#F7F2E6", M.SmoothPlastic)
blok(tablica, "Daszek", Vector3.new(1.6, 0.5, 8.4), CFrame.new(tx, 6.05, tz), "#D9483B", M.SmoothPlastic)
blok(tablica, "DaszekObrys", Vector3.new(1.9, 0.3, 8.7), CFrame.new(tx, 5.7, tz), TUSZ, M.SmoothPlastic)

local sg = Instance.new("SurfaceGui")
sg.Name = "Napis"
sg.Face = Enum.NormalId.Left -- ściana zwrócona na zachód (−X)
sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
sg.PixelsPerStud = 60
sg.LightInfluence = 0.4
sg.Parent = deska
local function napis(tekst: string, y: number, wys: number, czcionka: Enum.Font, kolor: string, obrys: number)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(0.92, wys)
	t.Position = UDim2.fromScale(0.04, y)
	t.Font = czcionka
	t.Text = tekst
	t.TextScaled = true
	t.TextColor3 = Color3.fromHex(kolor)
	t.Rotation = -1.5
	local s = Instance.new("UIStroke")
	s.Thickness = obrys
	s.Color = Color3.fromHex("#17121F")
	s.Parent = t
	t.Parent = sg
	licznik += 2
	return t
end
napis("TEST WALKI 3D", 0.08, 0.46, Enum.Font.LuckiestGuy, "#FFD23F", 5)
napis("prototyp cutscenki  •  podejdź i naciśnij E", 0.6, 0.2, Enum.Font.Bangers, "#2F6FE0", 0)
napis("serwer liczy walkę, klient ją tylko odtwarza", 0.8, 0.13, Enum.Font.Bangers, "#6C727A", 0)

local podpowiedz = Instance.new("ProximityPrompt")
podpowiedz.Name = "PodpowiedzWalki"
podpowiedz.ObjectText = "Test walki 3D (prototyp)"
podpowiedz.ActionText = "Walcz!"
podpowiedz.KeyboardKeyCode = Enum.KeyCode.E
podpowiedz.HoldDuration = 0
podpowiedz.MaxActivationDistance = 14
podpowiedz.RequiresLineOfSight = false
-- Zbudowana jako WYŁĄCZONA: włącza ją dopiero SerwerWalki w Studio. Poza Studio serwer i tak usuwa cały kontener,
-- a gdyby jego skrypt z jakiegoś powodu nie ruszył, podpowiedź, która nic nie robi, po prostu się nie pokaże.
podpowiedz.Enabled = false
podpowiedz.Parent = deska
licznik += 2

------------------------------------------------------------------ świecący słup (żeby arenę było widać z placu)
local slup = grupa("Slup")
local sx, sz = -B - 6, -B + 1
blok(slup, "CokolObrys", Vector3.new(5, 0.8, 5), CFrame.new(sx, 0.4, sz), TUSZ, M.Slate)
blok(slup, "Cokol", Vector3.new(4, 0.8, 4), CFrame.new(sx, 1.2, sz), KAMIEN_J, M.Cobblestone)
blok(slup, "Swiatlo", Vector3.new(1.8, 150, 1.8), CFrame.new(sx, 1.6 + 75, sz), "#FFD76A", M.Neon, { k = false, c = false, t = 0.15 })
for i, y in { 14, 30, 46 } do
	blok(slup, "Romb" .. i, Vector3.new(4.4 - i * 0.5, 4.4 - i * 0.5, 4.4 - i * 0.5), CFrame.new(sx, y, sz) * CFrame.Angles(math.rad(45), math.rad(35), 0), "#FFB703", M.Neon, { k = false, c = false })
end

------------------------------------------------------------------ otoczenie: sosny, głazy i krzaki za murkiem (tło ujęć)
local otoczenie = grupa("Otoczenie")
-- Sosna jak w demie: pień (walec) i trzy piętra igieł; każde piętro to ostrosłup z czterech klinów narożnych,
-- których wierzchołki (lokalnie +X, +Y, −Z) spotykają się na osi drzewa.
local function sosna(x: number, z: number, skala: number, obrot: number)
	local pien = czesc(otoczenie, "Part", "SosnaPien", Vector3.new(4.2 * skala, 1.7 * skala, 1.7 * skala),
		CFrame.new(x, 2.1 * skala, z) * CFrame.Angles(0, 0, math.rad(90)), DREWNO, M.Wood)
	pien.Shape = Enum.PartType.Cylinder
	local baza = CFrame.new(x, 0, z) * CFrame.Angles(0, math.rad(obrot), 0)
	local function pietro(y: number, bok: number, wys: number, kolor: string)
		local h = bok / 2
		for k = 0, 3 do
			local cf = baza * CFrame.new(0, y + wys / 2, 0) * CFrame.Angles(0, math.rad(90 * k), 0) * CFrame.new(-h / 2, 0, h / 2)
			czesc(otoczenie, "CornerWedgePart", "SosnaIgly", Vector3.new(h, wys, h), cf, kolor, M.Grass, { k = false })
		end
	end
	pietro(3.2 * skala, 9 * skala, 7.5 * skala, "#236533")
	pietro(7.6 * skala, 7 * skala, 7 * skala, "#2C7A3D")
	pietro(11.8 * skala, 4.8 * skala, 6 * skala, "#37904A")
end
-- łuk od północy przez wschód do południa
local sosny = {
	{ -6, -31, 1.0, 10 }, { 8, -34, 1.25, 40 }, { 21, -31, 1.05, 75 }, { 32, -23, 1.3, 20 }, { 37, -9, 1.1, 55 },
	{ 39, 6, 1.35, 5 }, { 34, 21, 1.1, 65 }, { 23, 31, 1.25, 30 }, { 9, 35, 1.05, 80 }, { -5, 31, 1.15, 50 },
	{ 46, -18, 1.2, 15 }, { 48, 14, 1.15, 70 },
}
for _, s in sosny do
	sosna(s[1], s[2], s[3], s[4])
end
local glazy = { { 28, -29, 3.2, "#8D949C", 20 }, { 31, 28, 2.6, "#9AA0A8", 50 }, { -12, -27, 2.2, "#A7ADB4", 35 }, { -13, 27.5, 2.8, "#8D949C", 10 }, { 42, -2, 3.4, "#9AA0A8", 65 } }
for _, g in glazy do
	blok(otoczenie, "Glaz", Vector3.new(g[3] * 1.5, g[3], g[3] * 1.2), CFrame.new(g[1], g[3] / 2 - 0.2, g[2]) * CFrame.Angles(math.rad(6), math.rad(g[5]), math.rad(-5)), g[4], M.Slate)
	blok(otoczenie, "GlazMaly", Vector3.new(g[3] * 0.7, g[3] * 0.55, g[3] * 0.7), CFrame.new(g[1] + g[3] * 0.9, g[3] * 0.25, g[2] + g[3] * 0.5) * CFrame.Angles(0, math.rad(g[5] + 30), math.rad(8)), KAMIEN_C, M.Slate)
end
local krzaki = { { 26, -17, "#3F9B3A" }, { 27, 15, "#4E9E3C" }, { 3, -26.5, "#3F9B3A" }, { 14, 26.5, "#4E9E3C" }, { 18, -27, "#56B84A" }, { -2, 26.5, "#56B84A" } }
for _, k in krzaki do
	blok(otoczenie, "Krzak", Vector3.new(3.4, 2.4, 3.4), CFrame.new(k[1], 1.2, k[2]) * CFrame.Angles(0, math.rad(25), 0), k[3], M.Grass, { k = false })
	blok(otoczenie, "KrzakGora", Vector3.new(2.2, 1.6, 2.2), CFrame.new(k[1] + 0.3, 2.9, k[2] - 0.2) * CFrame.Angles(0, math.rad(50), 0), k[3], M.Grass, { k = false })
end

arena.Parent = kontener
return "OK arena: " .. licznik .. " instancji"
