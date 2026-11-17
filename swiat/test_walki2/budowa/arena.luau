--[[
	Budowa areny prototypu walki v2 (tryb Edit, przez zbuduj.py → execute_luau).
	Tworzy WYŁĄCZNIE Workspace/TestWalki2/Arena. Kontener musi istnieć i mieć atrybut Wygenerowane.

	Leśna polana na południe od placu: okrągły podest z ubitej ziemi z obręczą kamieni, za nim (na południu, w tle
	ujęć) las z sosen, wielkich muchomorów, głazów, krzaków i pni; tablica z podpowiedzią i zielony świecący słup
	po północnej stronie (od strony placu). Układ: X = wschód, Z = południe; kamera planu ogólnego patrzy na południe.
	Podpowiedź powstaje WYŁĄCZONA (włączy ją serwer w kolejnym etapie, tylko w Studio).
]]
local kontener = workspace:FindFirstChild("TestWalki2")
if not kontener or kontener:GetAttribute("Wygenerowane") ~= true then
	return "STOP: brak kontenera Workspace/TestWalki2 z atrybutem Wygenerowane"
end
local U = require(kontener.Moduly.Ustawienia)

local stara = kontener:FindFirstChild("Arena")
if stara then
	stara:Destroy()
end

local O = CFrame.new(U.SRODEK)
local R = U.PROMIEN_PODESTU
local H = U.WYSOKOSC_PODESTU
local M = Enum.Material
local licznik = 0
local los = Random.new(2611) -- stałe ziarno: arena wygląda tak samo po każdej budowie

local arena = Instance.new("Model")
arena.Name = "Arena"

local function grupa(nazwa: string): Model
	local m = Instance.new("Model")
	m.Name = nazwa
	m.Parent = arena
	return m
end

-- opcje: k = false → bez kolizji i zapytań; c = false → bez cienia; t = przezroczystość
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
-- walec stojący (oś pionowa): średnica d, wysokość h, środek w poz
local function walec(rodzic, nazwa, d: number, h: number, poz: Vector3, kolor, material, opcje)
	local p = czesc(rodzic, "Part", nazwa, Vector3.new(h, d, d), CFrame.new(poz) * CFrame.Angles(0, 0, math.rad(90)), kolor, material, opcje)
	p.Shape = Enum.PartType.Cylinder
	return p
end
local function kula(rodzic, nazwa, d: number, poz: Vector3, kolor, material, opcje)
	local p = czesc(rodzic, "Part", nazwa, Vector3.one * d, CFrame.new(poz), kolor, material, opcje)
	p.Shape = Enum.PartType.Ball
	return p
end

local TUSZ = "#2B2238"
local KAMIEN, KAMIEN_J, KAMIEN_C = "#8D949C", "#A9AFB6", "#646B73"
local DREWNO, DREWNO_J = "#5A3A22", "#8A5A34"
local ZIEMIA, ZIEMIA_J = "#8B6A43", "#B08A58"

------------------------------------------------------------------ podłoże i podest (polana)
local podloze = grupa("Podloze")
blok(podloze, "Trawa", Vector3.new(136, 0.2, 120), CFrame.new(-6, 0.1, 2), "#4FA341", M.Grass, { c = false })
blok(podloze, "Sciezka", Vector3.new(8, 0.24, 30), CFrame.new(10, 0.12, -38), ZIEMIA_J, M.Ground, { c = false })

local podest = grupa("Podest")
walec(podest, "Cokol", 2 * R + 1.2, H - 0.2, Vector3.new(0, (H - 0.2) / 2, 0), TUSZ, M.Slate)
walec(podest, "Plyta", 2 * R, 0.2, Vector3.new(0, H - 0.1, 0), ZIEMIA, M.Ground)
walec(podest, "KragJasny", 2 * R - 6, 0.06, Vector3.new(0, H + 0.03, 0), ZIEMIA_J, M.Sand, { k = false, c = false })
walec(podest, "KragSrodek", 2 * R - 9, 0.08, Vector3.new(0, H + 0.04, 0), ZIEMIA, M.Ground, { k = false, c = false })
-- obręcz z kamieni na krawędzi (przerwa od północy = wejście)
local ile = 22
for i = 0, ile - 1 do
	local kat = (i + 0.5) / ile * math.pi * 2
	local x, z = math.sin(kat) * (R + 0.2), -math.cos(kat) * (R + 0.2)
	if z < -R + 4 and math.abs(x) < 6 then
		continue -- wejście od północy (od placu)
	end
	local s = los:NextNumber(1.3, 2.1)
	blok(podest, "Kamien", Vector3.new(s * 1.3, s * 0.8, s), CFrame.new(x, H + s * 0.25, z) * CFrame.Angles(0, -kat + los:NextNumber(-0.3, 0.3), los:NextNumber(-0.15, 0.15)),
		if i % 3 == 0 then KAMIEN_J else KAMIEN, M.Slate)
end
-- znaczniki miejsc (niebieski = gracz po lewej, czerwony = przeciwnik po prawej; patrz Ustawienia.miejsce)
for _, s in { { "gracz", "#2F6FE0" }, { "wrog", "#D9483B" } } do
	local lok = U.miejsce(s[1]).Position - U.SRODEK
	walec(podest, "Znak_" .. s[1], 4.4, 0.1, Vector3.new(lok.X, H + 0.07, lok.Z), s[2], M.SmoothPlastic, { k = false, c = false })
	walec(podest, "Znak_" .. s[1] .. "_srodek", 3.4, 0.12, Vector3.new(lok.X, H + 0.08, lok.Z), ZIEMIA_J, M.Sand, { k = false, c = false })
end

------------------------------------------------------------------ las (tło ujęć: południe, wschód, zachód)
local las = grupa("Las")
-- sosna jak w v1: pień i trzy piętra igieł z klinów narożnych
local function sosna(x: number, z: number, skala: number, obrot: number)
	walec(las, "SosnaPien", 1.7 * skala, 4.2 * skala, Vector3.new(x, 2.1 * skala, z), DREWNO, M.Wood)
	local bazaCf = CFrame.new(x, 0, z) * CFrame.Angles(0, math.rad(obrot), 0)
	local function pietro(y: number, bok: number, wys: number, kolor: string)
		local h = bok / 2
		for k = 0, 3 do
			local cf = bazaCf * CFrame.new(0, y + wys / 2, 0) * CFrame.Angles(0, math.rad(90 * k), 0) * CFrame.new(-h / 2, 0, h / 2)
			czesc(las, "CornerWedgePart", "SosnaIgly", Vector3.new(h, wys, h), cf, kolor, M.Grass, { k = false })
		end
	end
	pietro(3.2 * skala, 9 * skala, 7.5 * skala, "#1F5C30")
	pietro(7.6 * skala, 7 * skala, 7 * skala, "#277039")
	pietro(11.8 * skala, 4.8 * skala, 6 * skala, "#318545")
end
-- wielki muchomor: trzon, czerwony kapelusz z białymi kropkami
local function muchomor(x: number, z: number, s: number, swieci: boolean?)
	walec(las, "MuchomorTrzon", 1.1 * s, 2.6 * s, Vector3.new(x, 1.3 * s, z), "#F2EBDC", M.SmoothPlastic)
	walec(las, "MuchomorKolnierz", 1.6 * s, 0.25 * s, Vector3.new(x, 1.9 * s, z), "#E6DCC6", M.SmoothPlastic, { k = false })
	walec(las, "MuchomorKapelusz", 3.6 * s, 0.9 * s, Vector3.new(x, 2.95 * s, z), if swieci then "#9B4DFF" else "#E5482F", if swieci then M.Neon else M.SmoothPlastic)
	walec(las, "MuchomorCzubek", 2.4 * s, 0.6 * s, Vector3.new(x, 3.5 * s, z), if swieci then "#B98CFF" else "#E5482F", M.SmoothPlastic)
	for k = 0, 4 do
		local kat = k / 5 * math.pi * 2 + x
		kula(las, "MuchomorKropka", 0.45 * s, Vector3.new(x + math.cos(kat) * 1.2 * s, 3.45 * s, z + math.sin(kat) * 1.2 * s), "#FFFFFF", M.SmoothPlastic, { k = false, c = false })
	end
end
local function glaz(x: number, z: number, s: number, obrot: number)
	blok(las, "Glaz", Vector3.new(s * 1.5, s, s * 1.2), CFrame.new(x, s / 2 - 0.2, z) * CFrame.Angles(math.rad(6), math.rad(obrot), math.rad(-5)), KAMIEN, M.Slate)
	blok(las, "GlazMaly", Vector3.new(s * 0.7, s * 0.55, s * 0.7), CFrame.new(x + s * 0.9, s * 0.25, z + s * 0.5) * CFrame.Angles(0, math.rad(obrot + 30), math.rad(8)), KAMIEN_C, M.Slate)
	blok(las, "GlazMech", Vector3.new(s * 1.2, 0.25, s * 0.9), CFrame.new(x - s * 0.1, s - 0.25, z) * CFrame.Angles(math.rad(6), math.rad(obrot), math.rad(-5)), "#4E9E3C", M.Grass, { k = false })
end
local function krzak(x: number, z: number, kolor: string)
	blok(las, "Krzak", Vector3.new(3.4, 2.4, 3.4), CFrame.new(x, 1.2, z) * CFrame.Angles(0, math.rad(25), 0), kolor, M.Grass, { k = false })
	blok(las, "KrzakGora", Vector3.new(2.2, 1.6, 2.2), CFrame.new(x + 0.3, 2.9, z - 0.2) * CFrame.Angles(0, math.rad(50), 0), kolor, M.Grass, { k = false })
end
local function pien(x: number, z: number, s: number)
	walec(las, "Pniak", 2.2 * s, 1.4 * s, Vector3.new(x, 0.7 * s, z), DREWNO_J, M.Wood)
	walec(las, "PniakSloje", 1.7 * s, 0.06, Vector3.new(x, 1.42 * s, z), "#D9B27A", M.Wood, { k = false, c = false })
end
local function kloda(x: number, z: number, dl: number, obrot: number)
	local p = czesc(las, "Part", "Kloda", Vector3.new(dl, 1.6, 1.6), CFrame.new(x, 0.8, z) * CFrame.Angles(0, math.rad(obrot), 0), DREWNO, M.Wood)
	p.Shape = Enum.PartType.Cylinder
	czesc(las, "Part", "KlodaMech", Vector3.new(dl * 0.6, 0.3, 1.2), CFrame.new(x, 1.62, z) * CFrame.Angles(0, math.rad(obrot), 0), "#4E9E3C", M.Grass, { k = false })
end

-- łuk sosen od wschodu przez południe do zachodu (północ zostaje otwarta: tam kamera, tablica i galeria)
local sosny = {
	{ 34, -8, 1.1, 10 }, { 40, 8, 1.3, 40 }, { 36, 24, 1.15, 75 }, { 26, 36, 1.35, 20 }, { 12, 44, 1.2, 55 },
	{ -4, 47, 1.4, 5 }, { -20, 43, 1.2, 65 }, { -33, 33, 1.3, 30 }, { -42, 18, 1.1, 80 }, { -45, 2, 1.25, 50 },
	{ -40, -12, 1.05, 15 }, { 50, 30, 1.25, 35 }, { 2, 56, 1.3, 60 }, { -30, 52, 1.2, 25 }, { 28, 52, 1.15, 45 },
	{ -54, 30, 1.2, 70 }, { 54, -4, 1.1, 20 },
}
for _, s in sosny do
	sosna(s[1], s[2], s[3], s[4])
end
for _, m in { { 27, 18, 1.0 }, { 30, 22, 0.6 }, { -26, 26, 1.2 }, { -30, 22, 0.7, true }, { 8, 34, 0.9 }, { 14, 33, 0.55, true },
	{ -12, 36, 0.8 }, { 33, -2, 0.7, true } } do
	muchomor(m[1], m[2], m[3], m[4])
end
for _, g in { { 22, 30, 3.0, 20 }, { -18, 30, 2.6, 50 }, { -36, 6, 3.2, 35 }, { 36, 12, 2.4, 10 } } do
	glaz(g[1], g[2], g[3], g[4])
end
for _, k in { { 18, 27, "#3F9B3A" }, { -6, 32, "#4E9E3C" }, { 32, 4, "#3F9B3A" }, { -32, 14, "#56B84A" }, { 4, 30, "#56B84A" }, { -28, -4, "#3F9B3A" } } do
	krzak(k[1], k[2], k[3])
end
pien(-22, 18, 1.0)
pien(24, -12, 0.8)
kloda(-6, 28, 7, 15)
kloda(30, 30, 6, -40)

------------------------------------------------------------------ tablica z podpowiedzią i świecący słup (północ, od placu)
local tablica = grupa("Tablica")
local tx, tz = 16, -30 -- względem środka podestu
blok(tablica, "NogaLewa", Vector3.new(0.6, 5.2, 0.6), CFrame.new(tx - 3.1, 2.6, tz), DREWNO, M.Wood)
blok(tablica, "NogaPrawa", Vector3.new(0.6, 5.2, 0.6), CFrame.new(tx + 3.1, 2.6, tz), DREWNO, M.Wood)
blok(tablica, "DeskaObrys", Vector3.new(7.6, 4.2, 0.4), CFrame.new(tx, 3.7, tz + 0.05), TUSZ, M.Wood)
local deska = blok(tablica, "Deska", Vector3.new(7.0, 3.6, 0.5), CFrame.new(tx, 3.7, tz - 0.1), "#F7F2E6", M.SmoothPlastic)
blok(tablica, "Daszek", Vector3.new(8.4, 0.5, 1.6), CFrame.new(tx, 6.05, tz), "#3F9B3A", M.SmoothPlastic)
blok(tablica, "DaszekObrys", Vector3.new(8.7, 0.3, 1.9), CFrame.new(tx, 5.7, tz), TUSZ, M.SmoothPlastic)

local sg = Instance.new("SurfaceGui")
sg.Name = "Napis"
sg.Face = Enum.NormalId.Front -- ściana zwrócona na północ (−Z), do nadchodzących graczy
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
napis("PRÓBA WALKI", 0.06, 0.46, Enum.Font.LuckiestGuy, "#7ED957", 5)
napis("klasa, przeciwnik, poziom  •  podejdź i naciśnij E", 0.58, 0.2, Enum.Font.Bangers, "#2F6FE0", 0)
napis("prototyp: serwer liczy, klient odtwarza", 0.8, 0.13, Enum.Font.Bangers, "#6C727A", 0)

local podpowiedz = Instance.new("ProximityPrompt")
podpowiedz.Name = "PodpowiedzWalki2"
podpowiedz.ObjectText = "Próba walki (prototyp)"
podpowiedz.ActionText = "Wybierz walkę"
podpowiedz.KeyboardKeyCode = Enum.KeyCode.E
podpowiedz.HoldDuration = 0
podpowiedz.MaxActivationDistance = 14
podpowiedz.RequiresLineOfSight = false
podpowiedz.Enabled = false -- włącza ją dopiero serwer w Studio (kolejny etap); poza Studio kontenera i tak nie ma
podpowiedz.Parent = deska
licznik += 2

local slup = grupa("Slup")
local sx, sz = tx + 6.5, tz - 1
blok(slup, "CokolObrys", Vector3.new(5, 0.8, 5), CFrame.new(sx, 0.4, sz), TUSZ, M.Slate)
blok(slup, "Cokol", Vector3.new(4, 0.8, 4), CFrame.new(sx, 1.2, sz), KAMIEN_J, M.Cobblestone)
blok(slup, "Swiatlo", Vector3.new(1.8, 150, 1.8), CFrame.new(sx, 1.6 + 75, sz), "#7CFF9B", M.Neon, { k = false, c = false, t = 0.15 })
for i, y in { 14, 30, 46 } do
	blok(slup, "Romb" .. i, Vector3.new(4.4 - i * 0.5, 4.4 - i * 0.5, 4.4 - i * 0.5), CFrame.new(sx, y, sz) * CFrame.Angles(math.rad(45), math.rad(35), 0), "#3FD46A", M.Neon, { k = false, c = false })
end

arena.Parent = kontener
return "OK arena: " .. licznik .. " instancji"
