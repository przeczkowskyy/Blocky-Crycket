-- Podgląd sali wyboru klasy i rasy w stylu „kreskówka low poly” (Paweł 28.11: „dawaj tę salę bardziej low poly,
-- lekko inne tekstury; zrób mi podgląd, na razie nie zmieniaj”). Prawdziwa sala Workspace/WyborKlasy i jej generator
-- (swiat/wybor_klasy) zostają nietknięte — to osobna makieta w kontenerze Workspace/SalaLowPolyPodglad (atrybut
-- Wygenerowane), na północ od podglądu miasteczka. Kamera wyboru klasy: z (X0; +7,5; Z0 + 21) na (X0; +5,5; Z0 − 3).
--   Uruchomienie: python tools/studio_mcp.py luau tools/studio/sala_lowpoly_podglad.luau   (ponowne = odbudowa)
-- Czym różni się od dzisiejszej sali: mniej, ale większych brył (kilka grubych belek zamiast gęstej więźby, gładki
-- ciemny strop), ściany z tynku z łatami cegieł nad kamiennym cokołem zamiast desek, drewno gładkie (bez słojów),
-- podłoga z dużych płyt bez szczelin, te same rekwizyty w mniejszej liczbie, ciemny kontur z trzech grup.
local CHS = game:GetService("ChangeHistoryService")
local NAZWA = "SalaLowPolyPodglad"
local X0, Z0 = 976, -385
local bp = workspace:FindFirstChild("Baseplate")
local Y0 = (bp and bp:IsA("BasePart")) and (bp.Position.Y + bp.Size.Y / 2) or 0
local stary = workspace:FindFirstChild(NAZWA)
if stary and not stary:GetAttribute("Wygenerowane") then
	return "W Workspace jest kontener " .. NAZWA .. " bez atrybutu Wygenerowane — nie ruszam"
end
for _, p in ipairs(workspace:GetPartBoundsInBox(CFrame.new(X0, Y0 + 12, Z0), Vector3.new(60, 22, 62))) do
	if p ~= bp and not (stary and p:IsDescendantOf(stary)) then
		return "Miejsce makiety jest zajęte przez " .. p:GetFullName() .. " — nic nie zbudowane"
	end
end
local rec = CHS:TryBeginRecording("Podgląd sali wyboru low poly")
if stary then
	stary:Destroy()
end
local kont = Instance.new("Folder")
kont.Name = NAZWA
kont:SetAttribute("Wygenerowane", true)
kont:SetAttribute("Autor", "Paweł (Claude Code), 2026-11-28")
kont:SetAttribute("Opis", "Podgląd sali wyboru klasy w stylu low poly; nie jest częścią gry")
kont.Parent = workspace

local function C(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end
local DREWNO, DREWNO_J, DREWNO_C = C(150, 98, 60), C(196, 140, 86), C(92, 60, 44)
local KAMIEN, KAMIEN_C = C(176, 170, 190), C(140, 134, 156)
local OKNO, BIALY, TUSZ = C(255, 208, 104), Color3.new(1, 1, 1), C(46, 32, 34)
local N = Enum.NormalId
local BOKI = { N.Front, N.Back, N.Left, N.Right }
local TEX = { kamien = "rbxassetid://124850720793067", tynk = "rbxassetid://83860363530000", plyty = "rbxassetid://99730536392239",
	deski = "rbxassetid://120082727765133", cegla = "rbxassetid://85599806414499", bruk = "rbxassetid://140378080945883" }
local licznik = 0
local function tex(p: BasePart, id: string, studs: number, sciany: { Enum.NormalId }?, kolor: Color3?, przezr: number?)
	for _, s in ipairs(sciany or BOKI) do
		local t = Instance.new("Texture")
		t.Texture, t.Face, t.StudsPerTileU, t.StudsPerTileV = id, s, studs, studs
		t.Color3, t.Transparency = kolor or BIALY, przezr or 0
		t.Parent = p
	end
end
local function grupa(nazwa: string, zKonturem: boolean): Model
	local m = Instance.new("Model")
	m.Name = nazwa
	if zKonturem then
		local h = Instance.new("Highlight")
		h.Name = "Kontur"
		h.FillTransparency, h.OutlineTransparency, h.OutlineColor = 1, 0.1, TUSZ
		h.DepthMode = Enum.HighlightDepthMode.Occluded
		h.Parent = m
	end
	m.Parent = kont
	return m
end
local G_SALA, G_MEBLE, G_OZDOBY, G_BEZ = grupa("Ściany i belki", true), grupa("Meble i podest", true), grupa("Ozdoby", true), grupa("Bez konturu", false)
local function cz(rodzic: Instance, nazwa: string, sx: number, sy: number, sz: number, x: number, y: number, z: number, kolor: Color3, obrot: CFrame?, mat: Enum.Material?): BasePart
	local p = Instance.new("Part")
	p.Name, p.Size, p.Color = nazwa, Vector3.new(sx, sy, sz), kolor
	p.CFrame = CFrame.new(X0 + x, Y0 + y, Z0 + z) * (obrot or CFrame.new())
	p.Material, p.Anchored = mat or Enum.Material.SmoothPlastic, true
	p.TopSurface, p.BottomSurface = Enum.SurfaceType.Smooth, Enum.SurfaceType.Smooth
	-- ściany i strop nie rzucają cienia: wnętrze oświetla słońce miejsca i ciepłe lampy, jak plac na podglądzie
	-- (pierwsza próba z cieniem stropu wyszła ciemna i niebieska)
	p.CastShadow = rodzic ~= G_SALA and rodzic ~= G_BEZ
	p.Parent = rodzic
	licznik += 1
	return p
end
local function walec(rodzic: Instance, nazwa: string, srednica: number, wys: number, x: number, y: number, z: number, kolor: Color3, mat: Enum.Material?): BasePart
	local p = cz(rodzic, nazwa, wys, srednica, srednica, x, y, z, kolor, CFrame.Angles(0, 0, math.pi / 2), mat)
	p.Shape = Enum.PartType.Cylinder
	return p
end
local function swiatlo(p: BasePart, zasieg: number, moc: number, kolor: Color3?)
	local l = Instance.new("PointLight")
	l.Color, l.Range, l.Brightness = kolor or OKNO, zasieg, moc
	l.Parent = p
end

local W, TYL, WYS = 24, -24, 17 -- połowa szerokości, tylna ściana, wysokość do stropu
-- podłoga: duże płyty bez szczelin
tex(cz(G_BEZ, "Podłoga", 2 * W + 2, 0.6, 52, 0, 0.3, 2, C(206, 196, 190)), TEX.plyty, 8, { N.Top }, C(255, 236, 224))
-- strop: gładkie ciemne deski i trzy grube belki
cz(G_BEZ, "Strop", 2 * W + 2, 0.6, 52, 0, WYS + 0.3, 2, DREWNO_C)
for _, z in ipairs({ -14, 0, 14 }) do
	cz(G_SALA, "Belka stropu", 2 * W, 1.8, 1.8, 0, WYS - 0.9, z, DREWNO)
end
for _, x in ipairs({ -12, 12 }) do
	cz(G_SALA, "Podciąg", 1.6, 1.4, 50, x, WYS - 2.2, 1, DREWNO_J)
end
-- ściany: kamienny cokół, wyżej tynk z łatami cegieł, mur pruski z gładkiego drewna
local function sciana(nazwa: string, dl: number, cf: CFrame)
	local function P(n: string, sx: number, sy: number, sz: number, px: number, py: number, pz: number, kol: Color3, rot: CFrame?): BasePart
		local p = cz(G_SALA, n, sx, sy, sz, 0, 0, 0, kol)
		p.CFrame = cf * CFrame.new(px, py, pz) * (rot or CFrame.new())
		return p
	end
	tex(P(nazwa .. " cokół", dl, 5, 1.4, 0, 2.5, 0.2, KAMIEN), TEX.kamien, 6)
	P(nazwa .. " gzyms", dl, 0.6, 1.9, 0, 5.3, 0.3, KAMIEN_C)
	tex(P(nazwa .. " tynk", dl, WYS - 5.6, 1, 0, 5.6 + (WYS - 5.6) / 2, 0, C(250, 236, 208)), TEX.tynk, 10, BOKI, C(255, 240, 226))
	local n = math.floor(dl / 8)
	for i = 0, n do
		P("Słup", 1.2, WYS - 5.6, 1.4, -dl / 2 + i * dl / n, 5.6 + (WYS - 5.6) / 2, 0.3, DREWNO)
	end
	P("Rygiel", dl, 1, 1.4, 0, 11.4, 0.3, DREWNO)
	P("Oczep", dl, 1.2, 1.5, 0, WYS - 0.6, 0.3, DREWNO)
end
sciana("Tył", 2 * W, CFrame.new(X0, Y0, Z0 + TYL))
sciana("Lewa", 52, CFrame.new(X0 - W, Y0, Z0 + 2) * CFrame.Angles(0, math.pi / 2, 0))
sciana("Prawa", 52, CFrame.new(X0 + W, Y0, Z0 + 2) * CFrame.Angles(0, -math.pi / 2, 0))

-- okno w tylnej ścianie: trzy łuki z nocnym niebem
do
	cz(G_SALA, "Rama okna", 14, 8, 0.8, 0, 9.6, TYL + 0.9, DREWNO_C)
	for i = -1, 1 do
		cz(G_BEZ, "Szyba", 3.6, 6.4, 0.4, i * 4.2, 9.4, TYL + 1.3, C(72, 96, 190), nil, Enum.Material.Neon)
		walec(G_BEZ, "Łuk szyby", 3.6, 0.4, i * 4.2, 12.6, TYL + 1.3, C(72, 96, 190), Enum.Material.Neon).CFrame = CFrame.new(X0 + i * 4.2, Y0 + 12.6, Z0 + TYL + 1.3) * CFrame.Angles(0, math.pi / 2, 0)
		cz(G_SALA, "Szczeblina", 0.3, 6.4, 0.5, i * 4.2, 9.4, TYL + 1.5, DREWNO_C)
	end
	walec(G_BEZ, "Księżyc", 1.5, 0.3, 0.9, 11.4, TYL + 1.55, C(255, 244, 200), Enum.Material.Neon).CFrame = CFrame.new(X0 + 0.9, Y0 + 11.4, Z0 + TYL + 1.55) * CFrame.Angles(0, math.pi / 2, 0)
	cz(G_SALA, "Parapet", 15, 0.6, 1.6, 0, 5.4, TYL + 1.2, DREWNO_J)
end
-- chorągwie po bokach okna
for _, c in ipairs({ { -11, C(206, 70, 66) }, { 11, C(64, 170, 170) } }) do
	cz(G_OZDOBY, "Drążek", 4.4, 0.4, 0.4, c[1], 14, TYL + 1.2, DREWNO_C)
	cz(G_OZDOBY, "Chorągiew", 3.6, 6.4, 0.25, c[1], 10.7, TYL + 1.2, c[2] :: Color3)
	cz(G_OZDOBY, "Chorągiew znak", 1.5, 1.5, 0.3, c[1], 11.2, TYL + 1.3, C(255, 214, 90), CFrame.Angles(0, 0, math.rad(45)))
	cz(G_OZDOBY, "Chorągiew szpic", 2.5, 2.5, 0.25, c[1], 7.5, TYL + 1.2, c[2] :: Color3, CFrame.Angles(0, 0, math.rad(45)))
end
-- kominek w prawym tylnym rogu
do
	local x, z = 15.5, TYL + 2.4
	tex(cz(G_SALA, "Kominek", 9, 8, 3.6, x, 4, z, KAMIEN), TEX.kamien, 5)
	tex(cz(G_SALA, "Komin", 6, WYS - 8, 2.6, x, 8 + (WYS - 8) / 2, z - 0.4, KAMIEN_C), TEX.kamien, 5)
	cz(G_SALA, "Gzyms kominka", 10.4, 0.8, 4.6, x, 8.2, z + 0.2, DREWNO_J)
	cz(G_BEZ, "Palenisko", 5, 4.4, 1, x, 2.6, z + 1.45, C(34, 26, 34))
	local ogien = cz(G_BEZ, "Ogień", 2.2, 2.4, 0.8, x, 1.7, z + 1.5, C(255, 150, 50), CFrame.Angles(0, 0, math.rad(45)), Enum.Material.Neon)
	cz(G_BEZ, "Ogień", 1.2, 1.4, 0.8, x, 2.3, z + 1.6, C(255, 226, 100), CFrame.Angles(0, 0, math.rad(45)), Enum.Material.Neon)
	swiatlo(ogien, 22, 2, C(255, 170, 80))
	walec(G_OZDOBY, "Tarcza", 3.2, 0.5, x, 11.6, z + 1, C(206, 70, 66)).CFrame = CFrame.new(X0 + x, Y0 + 11.6, Z0 + z + 1) * CFrame.Angles(0, math.pi / 2, 0)
	cz(G_OZDOBY, "Tarcza pas", 0.7, 3, 0.6, x, 11.6, z + 1.1, C(255, 214, 90))
end
-- regał z eliksirami i lada po prawej
do
	local x = W - 1.6
	cz(G_MEBLE, "Regał plecy", 1, 9, 12, x, 9.5, -8, DREWNO)
	local kolory = { C(236, 84, 160), C(90, 200, 120), C(96, 150, 240), C(250, 200, 70), C(170, 110, 230) }
	for p = 0, 2 do
		cz(G_MEBLE, "Półka", 2.4, 0.5, 12, x - 0.6, 6 + p * 3, -8, DREWNO_J)
		for i = 0, 4 do
			local k = cz(G_OZDOBY, "Eliksir", 0.9, 1.3, 0.9, x - 0.8, 6.9 + p * 3, -12.6 + i * 2.3 + (p % 2) * 0.6, kolory[(i + p) % 5 + 1])
			k.Shape = Enum.PartType.Ball
		end
	end
	tex(cz(G_MEBLE, "Lada", 3, 4, 16, W - 7, 2, -6, DREWNO), TEX.deski, 6, BOKI, C(230, 200, 170), 0.5)
	cz(G_MEBLE, "Blat lady", 4, 0.6, 17, W - 7, 4.3, -6, DREWNO_J)
	for i = 0, 2 do
		walec(G_MEBLE, "Stołek siedzisko", 2.2, 0.5, W - 10.6, 2.6, -11 + i * 5, DREWNO_J)
		cz(G_MEBLE, "Stołek noga", 0.7, 2.4, 0.7, W - 10.6, 1.2, -11 + i * 5, DREWNO_C)
	end
	cz(G_OZDOBY, "Bochenek", 1.8, 0.9, 1, W - 7, 5, -2, C(214, 160, 90))
	local j = cz(G_OZDOBY, "Jabłko", 0.9, 0.9, 0.9, W - 7.4, 5, -9, C(220, 60, 56))
	j.Shape = Enum.PartType.Ball
end
-- okrągły stół z prawej z przodu
do
	local x, z = 15, 9
	walec(G_MEBLE, "Stół blat", 9, 0.7, x, 4.2, z, DREWNO_J)
	cz(G_MEBLE, "Stół noga", 1.6, 3.8, 1.6, x, 1.9, z, DREWNO_C)
	walec(G_MEBLE, "Stół stopa", 4.4, 0.5, x, 0.85, z, DREWNO_C)
	local swieca = cz(G_OZDOBY, "Świeca", 0.5, 1.4, 0.5, x - 1, 5.2, z, C(250, 244, 226))
	swiatlo(cz(G_BEZ, "Płomyk", 0.35, 0.5, 0.35, x - 1, 6.1, z, OKNO, nil, Enum.Material.Neon), 10, 1)
	local _ = swieca
	cz(G_OZDOBY, "Ser", 1.6, 0.9, 1.2, x + 1.4, 5, z - 1.2, C(250, 206, 84), CFrame.Angles(0, 0.5, 0))
	for i = 0, 1 do
		walec(G_MEBLE, "Stołek siedzisko", 2.4, 0.5, x - 4 + i * 2.5, 2.6, z + 5.5 - i * 11, DREWNO_J)
		cz(G_MEBLE, "Stołek noga", 0.7, 2.4, 0.7, x - 4 + i * 2.5, 1.2, z + 5.5 - i * 11, DREWNO_C)
	end
end
-- beczki i skrzynie po lewej z tyłu
for i, b in ipairs({ { -19, TYL + 4 }, { -15.4, TYL + 3.6 }, { -17.2, TYL + 7 } }) do
	walec(G_MEBLE, "Beczka", 3.4, 4.2, b[1], 2.4, b[2], DREWNO)
	for _, y in ipairs({ 1.2, 3.6 }) do
		walec(G_MEBLE, "Obręcz", 3.6, 0.4, b[1], y, b[2], C(80, 80, 92))
	end
	if i == 1 then
		for k = 0, 3 do
			local j = cz(G_OZDOBY, "Jabłko", 0.9, 0.9, 0.9, b[1] - 0.7 + (k % 2) * 1.2, 4.8, b[2] - 0.6 + (k // 2) * 1.1, C(220, 60, 56))
			j.Shape = Enum.PartType.Ball
		end
	end
end
tex(cz(G_MEBLE, "Skrzynia", 3.6, 3.6, 3.6, -11, 1.8, TYL + 4, C(196, 150, 96), CFrame.Angles(0, 0.2, 0)), "rbxassetid://122070761203947", 3.6, { N.Front, N.Back, N.Left, N.Right, N.Top })
-- pochodnie na lewej ścianie i żyrandole
for _, z in ipairs({ -12, 4 }) do
	cz(G_OZDOBY, "Uchwyt pochodni", 1.6, 0.4, 0.4, -W + 1.6, 9.4, z, C(60, 58, 66))
	cz(G_OZDOBY, "Pochodnia", 0.6, 2.6, 0.6, -W + 2.4, 10.2, z, DREWNO_C, CFrame.Angles(0, 0, math.rad(-18)))
	swiatlo(cz(G_BEZ, "Płomień", 1.1, 1.5, 1.1, -W + 2.8, 11.9, z, C(255, 170, 60), CFrame.Angles(0.5, 0.5, 0.5), Enum.Material.Neon), 20, 1.6, C(255, 180, 90))
end
for _, x in ipairs({ -9, 9 }) do
	cz(G_OZDOBY, "Łańcuch", 0.3, 2.6, 0.3, x, WYS - 2.9, -4, C(60, 58, 66))
	local r = walec(G_OZDOBY, "Żyrandol", 6.4, 0.6, x, WYS - 4.4, -4, C(60, 58, 66))
	swiatlo(r, 26, 1.3)
	for i = 0, 5 do
		local a = i * math.pi / 3
		cz(G_OZDOBY, "Świeca", 0.45, 1.2, 0.45, x + math.cos(a) * 2.7, WYS - 3.6, -4 + math.sin(a) * 2.7, C(250, 244, 226))
		cz(G_BEZ, "Płomyk", 0.3, 0.45, 0.3, x + math.cos(a) * 2.7, WYS - 2.8, -4 + math.sin(a) * 2.7, OKNO, nil, Enum.Material.Neon)
	end
end
-- podest bohaterów: kamienny bęben, złoty pierścień, płyta
tex(walec(G_MEBLE, "Podest bęben", 17, 1.8, 0, 0.9 + 0.6, 0, KAMIEN), TEX.kamien, 5, { N.Front, N.Back, N.Top, N.Bottom })
walec(G_MEBLE, "Podest pierścień", 16.2, 0.4, 0, 2.6, 0, C(255, 204, 64))
tex(walec(G_BEZ, "Podest płyta", 14.8, 0.3, 0, 2.75, 0, C(206, 198, 214)), TEX.bruk, 5, { N.Right, N.Left }, C(240, 232, 226))
-- dywan przy stole
cz(G_BEZ, "Dywan", 12, 0.12, 8, 9, 0.66, 9, C(196, 60, 56), CFrame.Angles(0, 0.35, 0))
cz(G_BEZ, "Dywan wzór", 8, 0.14, 4.4, 9, 0.67, 9, C(250, 200, 80), CFrame.Angles(0, 0.35, 0))
cz(G_BEZ, "Dywan środek", 5, 0.16, 2.2, 9, 0.68, 9, C(196, 60, 56), CFrame.Angles(0, 0.35, 0))
-- trzy manekiny na podeście (bryły zastępcze bohaterów, żeby było widać skalę)
for i, kol in ipairs({ C(200, 90, 80), C(250, 170, 70), C(110, 170, 230) }) do
	local x = (i - 2) * 4.6
	cz(G_MEBLE, "Manekin tułów", 2.2, 2.6, 1.6, x, 2.9 + 1.9, if i == 2 then 1.2 else -0.6, kol)
	cz(G_MEBLE, "Manekin głowa", 2.8, 2.6, 2.6, x, 2.9 + 4.5, if i == 2 then 1.2 else -0.6, C(250, 214, 170))
	cz(G_MEBLE, "Manekin nogi", 2, 1.4, 1.4, x, 2.9 + 0.7, if i == 2 then 1.2 else -0.6, DREWNO_C)
end
-- ciepłe światło wypełniające (niewidoczne punkty pod stropem)
for _, q in ipairs({ { -12, -10 }, { 12, -10 }, { -12, 10 }, { 12, 10 }, { 0, 2 } }) do
	local l = cz(G_BEZ, "Światło sali", 0.2, 0.2, 0.2, q[1], WYS - 4, q[2], BIALY)
	l.Transparency, l.CanCollide = 1, false
	swiatlo(l, 46, 1.5, C(255, 232, 204))
end
if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return string.format("%s: %d części; kamera z (%d; %.1f; %d) na (%d; %.1f; %d)", NAZWA, licznik, X0, Y0 + 7.5, Z0 + 21, X0, Y0 + 5.5, Z0 - 3)
