-- Makieta planszy lasu w stylu podglądu miasteczka (Paweł 28.11: „przebudujmy planszę lasu pod ten sam styl, dodając
-- do obiektów lekkie ciemne obrysy; nie zmieniajmy tego Karola, zróbmy nową poglądową makietę planszy lasu”).
-- To NIE jest przebudowa lasu: Workspace/LasPas i generator Karola zostają nietknięte. Skrypt stawia osobny wycinek
-- (kontener Workspace/LasLowPolyPodglad, atrybut Wygenerowane) na ZACHÓD od podglądu miasteczka — przez Bramę Leśną
-- z kłódką przechodzi się z placu prosto na leśną ścieżkę, tak jak w propozycji D-170. Nie na wschód: dla x ≥ ok. 1044
-- gra Karola pilnuje pasa prawdziwego lasu i przenosi gracza do niego (sprawdzone 28.11), więc makieta byłaby
-- nie do przejścia. Plan jest rysowany z bramą po zachodniej stronie, a całość obraca OBROT o 180° wokół środka.
--   Uruchomienie: python tools/studio_mcp.py luau tools/studio/las_lowpoly_podglad.luau   (ponowne = odbudowa)
--   Usunięcie:    skasować kontener Workspace/LasLowPolyPodglad
-- Styl jak w tools/studio/miasteczko_lowpoly_podglad.luau: bryły low poly, nasze tekstury z paczki sali wyboru klasy
-- (już wgrane), ciemny kontur z trzech Highlightów na grupach (limit silnika: 31 naraz).
-- Co jest na makiecie: brama z kłódką, kręta ścieżka, ściana świerków i drzew po obu stronach, polana z ogniskiem,
-- kamienny krąg areny, leże potwora, gniazdo z jajem, staw z pomostem, chata leśnika, grzyby, głazy, pniaki, latarnie.
local CHS = game:GetService("ChangeHistoryService")
local NAZWA = "LasLowPolyPodglad"
local X0, Z0 = 826, -500 -- po obrocie wschodni brzeg (x = 901) leży 9 studów od zachodniego brzegu trawnika placu (x = 910)
local SZER, GLEB = 150, 90

local bp = workspace:FindFirstChild("Baseplate")
local Y0 = (bp and bp:IsA("BasePart")) and (bp.Position.Y + bp.Size.Y / 2) or 0
local stary = workspace:FindFirstChild(NAZWA)
if stary and not stary:GetAttribute("Wygenerowane") then
	return "W Workspace jest kontener " .. NAZWA .. " bez atrybutu Wygenerowane — nie ruszam"
end
for _, p in ipairs(workspace:GetPartBoundsInBox(CFrame.new(X0, Y0 + 30, Z0), Vector3.new(SZER + 2, 58, GLEB + 2))) do
	if p ~= bp and not (stary and p:IsDescendantOf(stary)) then
		return "Miejsce makiety jest zajęte przez " .. p:GetFullName() .. " — nic nie zbudowane"
	end
end

local rec = CHS:TryBeginRecording("Makieta lasu low poly")
if stary then
	stary:Destroy()
end
local kont = Instance.new("Folder")
kont.Name = NAZWA
kont:SetAttribute("Wygenerowane", true)
kont:SetAttribute("Autor", "Paweł (Claude Code), 2026-11-28")
kont:SetAttribute("Opis", "Makieta lasu w stylu low poly — propozycja D-171; nie jest częścią gry")
kont.Parent = workspace

local function C(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end
local DREWNO, DREWNO_J = C(96, 62, 44), C(168, 116, 72)
local KAMIEN, KAMIEN_C = C(176, 170, 190), C(140, 134, 156)
local OKNO = C(255, 208, 104)
local BIALY = Color3.new(1, 1, 1)
local TUSZ = C(46, 32, 34)
local los = Random.new(2812)
local YB = Y0 + 0.6
local licznik = 0
local OBROT = CFrame.new(X0, 0, Z0) * CFrame.Angles(0, math.pi, 0) * CFrame.new(-X0, 0, -Z0)
local N = Enum.NormalId
local BOKI = { N.Front, N.Back, N.Left, N.Right }
local TEX = {
	kamien = "rbxassetid://124850720793067", tynk = "rbxassetid://83860363530000", belka = "rbxassetid://71241194302925",
	deski = "rbxassetid://120082727765133", gont = "rbxassetid://114017817423852", bruk = "rbxassetid://140378080945883",
}
local function tex(p: BasePart, id: string, studs: number, sciany: { Enum.NormalId }?, kolor: Color3?, przezr: number?)
	for _, s in ipairs(sciany or BOKI) do
		local t = Instance.new("Texture")
		t.Texture, t.Face = id, s
		t.StudsPerTileU, t.StudsPerTileV = studs, studs
		t.Color3 = kolor or BIALY
		t.Transparency = przezr or 0
		t.Parent = p
	end
end
local function cz(rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3, mat: Enum.Material?, klasa: string?): BasePart
	local p = Instance.new(klasa or "Part") :: BasePart
	p.Name = nazwa
	p.Size = rozmiar
	p.CFrame = OBROT * cf
	p.Color = kolor
	p.Material = mat or Enum.Material.SmoothPlastic
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = rodzic
	licznik += 1
	return p
end
local function walec(rodzic: Instance, nazwa: string, srednica: number, wys: number, cf: CFrame, kolor: Color3): BasePart
	local p = cz(rodzic, nazwa, Vector3.new(wys, srednica, srednica), cf * CFrame.Angles(0, 0, math.pi / 2), kolor)
	p.Shape = Enum.PartType.Cylinder
	return p
end
local function kopula(rodzic: Instance, nazwa: string, rozmiar: Vector3, cf: CFrame, kolor: Color3): BasePart
	local p = cz(rodzic, nazwa, rozmiar, cf, kolor)
	local m = Instance.new("SpecialMesh")
	m.MeshType = Enum.MeshType.Sphere
	m.Parent = p
	return p
end
local function ostroslup(m: Instance, nazwa: string, podstawa: CFrame, bok: number, wys: number, kolor: Color3)
	for i = 0, 3 do -- wierzchołek CornerWedgePart leży nad jego rogiem +X, −Z
		local p = cz(m, nazwa, Vector3.new(bok / 2, wys, bok / 2), podstawa * CFrame.Angles(0, i * math.pi / 2, 0) * CFrame.new(-bok / 4, wys / 2, bok / 4), kolor, nil, "CornerWedgePart")
		p.CanCollide = false
	end
end
local function grupa(nazwa: string): Model
	local m = Instance.new("Model")
	m.Name = nazwa
	return m
end
local function kontur(m: Instance)
	local h = Instance.new("Highlight")
	h.Name = "Kontur"
	h.FillTransparency, h.OutlineTransparency = 1, 0
	h.OutlineColor = TUSZ
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Parent = m
end
-- trzy grupy z konturem: pnie, skały i budowle · korony, dachy, kapelusze · rekwizyty
local G_PNIE, G_KORONY, G_REKW = grupa("Pnie, skały i budowle"), grupa("Korony i dachy"), grupa("Rekwizyty")
for _, g in ipairs({ G_PNIE, G_KORONY, G_REKW }) do
	kontur(g)
	g.Parent = kont
end
local function pkt(x: number, z: number, y: number?): CFrame
	return CFrame.new(X0 + x, YB + (y or 0), Z0 + z)
end
local kroki = 0
local function oddech()
	kroki += 1
	if kroki % 6 == 0 then
		task.wait()
	end
end

------------------------------------------------------------ teren i ścieżka
local SCIEZKA = { { -75, 0 }, { -50, 4 }, { -25, -6 }, { 0, -2 }, { 25, 8 }, { 50, 2 }, { 75, 0 } }
local function zSciezki(x: number): number
	for i = 1, #SCIEZKA - 1 do
		local a, b = SCIEZKA[i], SCIEZKA[i + 1]
		if x >= a[1] and x <= b[1] then
			return a[2] + (b[2] - a[2]) * (x - a[1]) / (b[1] - a[1])
		end
	end
	return 0
end
-- miejsca zajęte (x, z, promień): tam nie rosną drzewa ani nie leżą głazy
local ZAJETE = { { -28, 20, 13 }, { 22, -20, 16 }, { 56, 24, 13 }, { -4, 24, 8 }, { -48, -20, 14 }, { 50, -24, 12 }, { -70, 0, 12 } }
local function wolne(x: number, z: number, margines: number): boolean
	if math.abs(z - zSciezki(x)) < 6.5 + margines then
		return false
	end
	for _, k in ipairs(ZAJETE) do
		if (Vector2.new(x - k[1], z - k[2])).Magnitude < k[3] + margines then
			return false
		end
	end
	return true
end
do
	local m = grupa("Teren")
	local o = CFrame.new(X0, Y0, Z0)
	cz(m, "Trawa", Vector3.new(SZER, 0.6, GLEB), o * CFrame.new(0, 0.3, 0), C(108, 170, 86))
	for _ = 1, 46 do -- jaśniejsze i ciemniejsze płaty trawy
		local s = los:NextNumber(6, 14)
		cz(m, "Płat trawy", Vector3.new(s, 0.1, s * los:NextNumber(0.6, 1)), o * CFrame.new(los:NextNumber(-68, 68), 0.62, los:NextNumber(-40, 40)) * CFrame.Angles(0, los:NextNumber(0, 3), 0),
			if los:NextNumber() < 0.5 then C(124, 184, 94) else C(94, 154, 80)).CanCollide = false
	end
	for i = 1, #SCIEZKA - 1 do -- ścieżka: odcinki ubitej ziemi z kamiennym brzegiem
		local a, b = SCIEZKA[i], SCIEZKA[i + 1]
		local pa, pb = Vector3.new(X0 + a[1], YB + 0.06, Z0 + a[2]), Vector3.new(X0 + b[1], YB + 0.06, Z0 + b[2])
		local dl = (pb - pa).Magnitude
		local cf = CFrame.lookAt((pa + pb) / 2, pb)
		cz(m, "Brzeg ścieżki", Vector3.new(11, 0.1, dl), cf * CFrame.new(0, -0.02, 0), C(150, 130, 100)).CanCollide = false
		cz(m, "Ścieżka", Vector3.new(9.4, 0.14, dl), cf, C(214, 182, 132)).CanCollide = false
		walec(m, "Zakręt", 9.4, 0.14, CFrame.new(pb), C(214, 182, 132)).CanCollide = false
		for _ = 1, 5 do -- płaskie kamienie w ścieżce
			local s = los:NextNumber(1.2, 2.4)
			tex(cz(m, "Kamień ścieżki", Vector3.new(s, 0.12, s * 0.8), cf * CFrame.new(los:NextNumber(-3.4, 3.4), 0.08, los:NextNumber(-dl / 2, dl / 2)) * CFrame.Angles(0, los:NextNumber(0, 3), 0), KAMIEN), TEX.bruk, 3, { N.Top })
		end
	end
	m.Parent = kont
	task.wait()
end

------------------------------------------------------------ drzewa
local function swierk(x: number, z: number, s: number)
	local o = pkt(x, z) * CFrame.Angles(0, los:NextNumber(0, 1.5), 0)
	tex(cz(G_PNIE, "Pień świerka", Vector3.new(1.4 * s, 3.6 * s, 1.4 * s), o * CFrame.new(0, 1.8 * s, 0), C(120, 84, 58)), TEX.belka, 3)
	local odcien = los:NextNumber(-0.12, 0.12)
	for _, p in ipairs({ { 9.4, 6, 2.8, C(52, 110, 84) }, { 7.4, 5.6, 6.2, C(62, 124, 90) }, { 5.2, 5.4, 9.6, C(74, 138, 96) } }) do
		ostroslup(G_KORONY, "Piętro świerka", o * CFrame.new(0, p[3] * s, 0), p[1] * s, p[2] * s, (p[4] :: Color3):Lerp(if odcien > 0 then C(150, 200, 110) else C(30, 70, 60), math.abs(odcien)))
	end
	oddech()
end
local function drzewo(x: number, z: number, s: number)
	local o = pkt(x, z)
	tex(cz(G_PNIE, "Pień", Vector3.new(1.7 * s, 6 * s, 1.7 * s), o * CFrame.new(0, 3 * s, 0), DREWNO_J), TEX.belka, 3)
	cz(G_PNIE, "Konar", Vector3.new(0.8 * s, 3 * s, 0.8 * s), o * CFrame.new(1.4 * s, 5 * s, 0) * CFrame.Angles(0, 0, math.rad(-40)), DREWNO_J)
	local kol = C(96, 164, 80):Lerp(C(150, 196, 84), los:NextNumber())
	for i, w in ipairs({ { 8.4, 3.6, 6.8, 0 }, { 6.4, 3.2, 9.6, 45 }, { 4.2, 2.8, 12, 20 } }) do
		cz(G_KORONY, "Korona", Vector3.new(w[1] * s, w[2] * s, w[1] * s),
			o * CFrame.new(0, w[3] * s, 0) * CFrame.Angles(math.rad(los:NextNumber(-7, 7)), math.rad(w[4] + los:NextNumber(-10, 10)), math.rad(los:NextNumber(-7, 7))),
			kol:Lerp(Color3.new(1, 1, 0.6), (i - 1) * 0.12))
	end
	oddech()
end
do
	local posadzone = {}
	local function sadz(x: number, z: number, gesto: boolean)
		for _, q in ipairs(posadzone) do
			if (q - Vector2.new(x, z)).Magnitude < (if gesto then 6.5 else 9) then
				return
			end
		end
		if not wolne(x, z, 3) then
			return
		end
		table.insert(posadzone, Vector2.new(x, z))
		if los:NextNumber() < 0.68 then
			swierk(x, z, los:NextNumber(0.85, 1.45))
		else
			drzewo(x, z, los:NextNumber(0.85, 1.25))
		end
	end
	for _ = 1, 150 do -- gęste ściany lasu przy północnym i południowym brzegu
		sadz(los:NextNumber(-72, 72), (if los:NextNumber() < 0.5 then -1 else 1) * los:NextNumber(26, 42), true)
	end
	for _ = 1, 60 do -- rzadsze drzewa w środku
		sadz(los:NextNumber(-66, 70), los:NextNumber(-26, 26), false)
	end
end

------------------------------------------------------------ brama leśna z kłódką (zachodni brzeg)
do
	local o = pkt(-73, 0)
	for _, s in ipairs({ -1, 1 }) do
		tex(cz(G_PNIE, "Filar bramy", Vector3.new(4.4, 15, 4.4), o * CFrame.new(0, 7.5, s * 8.2), KAMIEN), TEX.kamien, 5)
		cz(G_PNIE, "Głowica filaru", Vector3.new(5.4, 1, 5.4), o * CFrame.new(0, 15.5, s * 8.2), KAMIEN_C)
		ostroslup(G_KORONY, "Daszek filaru", o * CFrame.new(0, 16, s * 8.2), 6, 4, C(96, 150, 92))
		-- skrzydło wrót otwarte do środka lasu
		local zawias = o * CFrame.new(0.6, 0, s * 6) * CFrame.Angles(0, s * math.rad(72), 0)
		local skrz = cz(G_PNIE, "Skrzydło wrót", Vector3.new(0.7, 11.5, 6.2), zawias * CFrame.new(0, 5.9, -s * 3.1), DREWNO_J)
		tex(skrz, TEX.deski, 5, { N.Left, N.Right })
		for _, y in ipairs({ 2.4, 9.4 }) do
			cz(G_PNIE, "Okucie wrót", Vector3.new(0.9, 0.6, 6.2), zawias * CFrame.new(0, y, -s * 3.1), C(62, 60, 70))
		end
		local l = cz(G_REKW, "Lampa bramy", Vector3.new(1.2, 1.6, 1.2), o * CFrame.new(2.9, 10.5, s * 8.2), OKNO, Enum.Material.Neon)
		local sw = Instance.new("PointLight")
		sw.Color, sw.Range, sw.Brightness = OKNO, 18, 1.1
		sw.Parent = l
	end
	tex(cz(G_PNIE, "Belka bramy", Vector3.new(3.4, 2.2, 21), o * CFrame.new(0, 14.2, 0), DREWNO), TEX.belka, 5, BOKI, C(190, 170, 160))
	for _, s in ipairs({ 1, -1 }) do
		local d = cz(G_KORONY, "Daszek bramy", Vector3.new(24, 0.9, 4.6), o * CFrame.new(0, 17, 0) * CFrame.Angles(0, if s == 1 then math.pi / 2 else -math.pi / 2, 0) * CFrame.new(0, 0, 1.7) * CFrame.Angles(math.rad(34), 0, 0), C(96, 150, 92))
		tex(d, TEX.gont, 4, { N.Top }, BIALY, 0.5)
	end
	-- kłódka na skrzydle wrót (otwarta, wisi na skoblu) i klucz obok — znak pierwszego otwarcia z propozycji D-170
	local k = pkt(-70.4, 7.2, 5.2) * CFrame.Angles(0, math.rad(-18), 0)
	cz(G_REKW, "Kłódka", Vector3.new(2.6, 2.4, 1), k, C(246, 196, 70))
	cz(G_REKW, "Kłódka dziurka", Vector3.new(0.6, 0.9, 1.1), k * CFrame.new(0, -0.2, 0), C(70, 50, 30))
	cz(G_REKW, "Kabłąk", Vector3.new(0.45, 1.8, 0.45), k * CFrame.new(-0.8, 1.9, 0), C(120, 122, 134))
	cz(G_REKW, "Kabłąk", Vector3.new(2.05, 0.45, 0.45), k * CFrame.new(0, 2.8, 0), C(120, 122, 134))
	cz(G_REKW, "Kabłąk", Vector3.new(0.45, 1, 0.45), k * CFrame.new(0.8, 2.5, 0), C(120, 122, 134))
	local kl = pkt(-66.5, 3.4, -4.6) * CFrame.Angles(0, math.rad(30), math.rad(-25))
	walec(G_REKW, "Klucz ucho", 1.8, 0.4, kl * CFrame.Angles(math.pi / 2, 0, 0), C(255, 214, 90))
	cz(G_REKW, "Klucz trzon", Vector3.new(3.4, 0.4, 0.4), kl * CFrame.new(2.4, 0, 0), C(255, 214, 90))
	cz(G_REKW, "Klucz pióro", Vector3.new(0.5, 1, 0.4), kl * CFrame.new(3.7, -0.6, 0), C(255, 214, 90))
	cz(G_REKW, "Klucz pióro", Vector3.new(0.5, 0.7, 0.4), kl * CFrame.new(2.9, -0.45, 0), C(255, 214, 90))
	-- drogowskaz za bramą
	local d = pkt(-62, 8.5)
	cz(G_REKW, "Słup drogowskazu", Vector3.new(0.7, 7.4, 0.7), d * CFrame.new(0, 3.7, 0), DREWNO)
	tex(cz(G_REKW, "Strzałka", Vector3.new(5, 1.4, 0.4), d * CFrame.new(1.4, 6.2, 0.3) * CFrame.Angles(0, math.rad(12), 0), DREWNO_J), TEX.deski, 4, { N.Front, N.Back })
	tex(cz(G_REKW, "Strzałka", Vector3.new(4.4, 1.4, 0.4), d * CFrame.new(-1.2, 4.5, 0.3) * CFrame.Angles(0, math.rad(-20), 0), DREWNO_J), TEX.deski, 4, { N.Front, N.Back })
	task.wait()
end

------------------------------------------------------------ polana z ogniskiem
do
	local o = pkt(-28, 20)
	walec(kont, "Polana", 22, 0.1, o * CFrame.new(0, 0.05, 0), C(140, 196, 104)).CanCollide = false
	for i = 0, 7 do
		local a = i * math.pi / 4
		tex(cz(G_PNIE, "Kamień ogniska", Vector3.new(1.5, 1.1, 1.1), o * CFrame.Angles(0, a, 0) * CFrame.new(0, 0.5, 2.3), if i % 2 == 0 then KAMIEN else KAMIEN_C), TEX.kamien, 3, { N.Back, N.Top })
	end
	for i = 0, 2 do
		cz(G_REKW, "Polano", Vector3.new(0.6, 0.6, 3.2), o * CFrame.new(0, 0.5, 0) * CFrame.Angles(math.rad(22), i * math.pi / 1.5, 0), DREWNO)
	end
	local ogien = cz(kont, "Ogień", Vector3.new(1.6, 2.2, 1.6), o * CFrame.new(0, 1.6, 0) * CFrame.Angles(0, 0.6, 0), C(255, 150, 50), Enum.Material.Neon)
	ogien.CanCollide = false
	cz(kont, "Ogień", Vector3.new(0.9, 1.6, 0.9), o * CFrame.new(0.1, 2.6, 0) * CFrame.Angles(0.2, 0.2, 0.2), C(255, 220, 90), Enum.Material.Neon).CanCollide = false
	local sw = Instance.new("PointLight")
	sw.Color, sw.Range, sw.Brightness = C(255, 170, 80), 26, 2
	sw.Parent = ogien
	for i = 0, 2 do -- kłody do siedzenia
		local a = math.rad(40 + i * 110)
		local kl = o * CFrame.Angles(0, a, 0) * CFrame.new(0, 0.9, 6.4)
		local p = cz(G_PNIE, "Kłoda", Vector3.new(5.4, 1.8, 1.8), kl, DREWNO_J)
		p.Shape = Enum.PartType.Cylinder
		for _, s in ipairs({ -1, 1 }) do
			local sl = cz(G_PNIE, "Słoje", Vector3.new(0.1, 1.4, 1.4), kl * CFrame.new(s * 2.72, 0, 0), C(232, 196, 140))
			sl.Shape = Enum.PartType.Cylinder
		end
	end
	task.wait()
end

------------------------------------------------------------ kamienny krąg areny
do
	local o = pkt(22, -20)
	tex(walec(kont, "Płyta areny", 27, 0.3, o * CFrame.new(0, 0.15, 0), KAMIEN_C), TEX.bruk, 6, { N.Right, N.Left }, C(226, 220, 214))
	walec(kont, "Krąg areny", 14, 0.34, o * CFrame.new(0, 0.17, 0), C(206, 96, 84)).CanCollide = false
	walec(kont, "Krąg areny środek", 11.6, 0.38, o * CFrame.new(0, 0.19, 0), C(190, 184, 196)).CanCollide = false
	for i = 0, 7 do
		local a = i * math.pi / 4 + 0.39
		local h = los:NextNumber(5, 8.5)
		local g = cz(G_PNIE, "Głaz kręgu", Vector3.new(3, h, 2), o * CFrame.Angles(0, a, 0) * CFrame.new(0, h / 2, 12.6) * CFrame.Angles(math.rad(los:NextNumber(-5, 5)), 0, math.rad(los:NextNumber(-6, 6))), KAMIEN)
		tex(g, TEX.kamien, 4)
	end
	for _, s in ipairs({ -1, 1 }) do -- chorągwie przy wejściu od ścieżki
		local p = o * CFrame.new(s * 6, 0, 14.5)
		cz(G_REKW, "Drzewce", Vector3.new(0.6, 12, 0.6), p * CFrame.new(0, 6, 0), DREWNO)
		cz(G_REKW, "Chorągiew", Vector3.new(0.25, 4.6, 3.2), p * CFrame.new(0, 9.4, 1.9), C(206, 70, 66))
		cz(G_REKW, "Chorągiew znak", Vector3.new(0.35, 1.6, 1.6), p * CFrame.new(0, 9.8, 1.9) * CFrame.Angles(math.rad(45), 0, 0), C(255, 214, 90))
	end
	task.wait()
end

------------------------------------------------------------ leże potwora
do
	local o = pkt(56, 24) * CFrame.Angles(0, math.rad(200), 0)
	local glazy = { { -5, 4.5, 0, 7, 9, 8 }, { 5, 4, 0.5, 7, 8, 8 }, { 0, 9.2, 0.6, 14, 4.4, 9 }, { -8.6, 2.4, 2, 5, 4.8, 6 }, { 8.4, 2, 1.6, 4.6, 4, 5 }, { 0, 3, -5.6, 13, 6, 5 } }
	for _, g in ipairs(glazy) do
		local p = cz(G_PNIE, "Skała leża", Vector3.new(g[4], g[5], g[6]), o * CFrame.new(g[1], g[2], g[3]) * CFrame.Angles(math.rad(los:NextNumber(-6, 6)), math.rad(los:NextNumber(-10, 10)), math.rad(los:NextNumber(-6, 6))), if los:NextNumber() < 0.5 then KAMIEN else KAMIEN_C)
		tex(p, TEX.kamien, 6)
	end
	cz(kont, "Wejście do leża", Vector3.new(5.6, 6.4, 3), o * CFrame.new(0, 3.2, 3), C(26, 20, 30)).CanCollide = false
	for _, s in ipairs({ -1, 1 }) do
		cz(kont, "Oko w ciemności", Vector3.new(0.7, 0.45, 0.2), o * CFrame.new(s * 0.9, 3.6, 4.55), C(255, 226, 90), Enum.Material.Neon).CanCollide = false
	end
	for i = 1, 5 do -- kości przed wejściem
		cz(G_REKW, "Kość", Vector3.new(1.8, 0.35, 0.35), o * CFrame.new(los:NextNumber(-4, 4), 0.25, los:NextNumber(6, 9)) * CFrame.Angles(0, los:NextNumber(0, 3), 0), C(240, 234, 214))
	end
	kopula(G_KORONY, "Mech na skale", Vector3.new(9, 2, 6), o * CFrame.new(-1, 11.3, 0.4), C(96, 160, 84))
	task.wait()
end

------------------------------------------------------------ gniazdo z jajem
do
	local o = pkt(-4, 24)
	for i = 0, 9 do
		local a = i * math.pi / 5
		cz(G_REKW, "Gałąź gniazda", Vector3.new(3.2, 1.2, 1.3), o * CFrame.Angles(0, a, 0) * CFrame.new(0, 0.7, 3.4) * CFrame.Angles(0, 0, math.rad(los:NextNumber(-12, 12))), if i % 2 == 0 then DREWNO else DREWNO_J)
	end
	walec(kont, "Wyściółka", 6.4, 0.5, o * CFrame.new(0, 0.5, 0), C(226, 200, 130)).CanCollide = false
	kopula(G_REKW, "Jajo", Vector3.new(4, 5.2, 4), o * CFrame.new(0, 3.2, 0), C(250, 240, 214))
	for _, k in ipairs({ { 1.2, 4.2, 1.3 }, { -1.5, 3, 1 }, { 0.2, 2.2, 1.9 }, { -0.6, 4.6, -1.3 }, { 1.7, 2.6, -0.9 } }) do
		kopula(kont, "Plama jaja", Vector3.new(1, 1, 1), o * CFrame.new(k[1], k[2], k[3]), C(120, 190, 110)).CanCollide = false
	end
	task.wait()
end

------------------------------------------------------------ staw z pomostem
do
	local o = pkt(-48, -20)
	walec(kont, "Brzeg stawu", 25, 0.12, o * CFrame.new(0, 0.06, 0), C(224, 204, 150)).CanCollide = false
	walec(kont, "Woda", 21.5, 0.2, o * CFrame.new(0, 0.1, 0), C(86, 176, 226)).CanCollide = false
	walec(kont, "Woda głębia", 13, 0.24, o * CFrame.new(1.5, 0.12, -1), C(64, 150, 214)).CanCollide = false
	for _ = 1, 6 do
		local a, r = los:NextNumber(0, 6.28), los:NextNumber(3, 8.5)
		walec(kont, "Liść lilii", los:NextNumber(1.6, 2.6), 0.1, o * CFrame.new(math.cos(a) * r, 0.3, math.sin(a) * r), C(96, 170, 90)).CanCollide = false
	end
	kopula(kont, "Kwiat lilii", Vector3.new(0.9, 0.7, 0.9), o * CFrame.new(-4, 0.6, 3), C(250, 190, 214)).CanCollide = false
	for i = 1, 9 do -- trzciny
		local a = math.rad(200 + i * 14)
		local t = o * CFrame.new(math.cos(a) * 10.4, 0, math.sin(a) * 10.4)
		cz(G_REKW, "Trzcina", Vector3.new(0.3, 4 + (i % 3), 0.3), t * CFrame.new(0, 2 + (i % 3) / 2, 0) * CFrame.Angles(0, 0, math.rad(los:NextNumber(-8, 8))), C(110, 160, 80))
		cz(G_REKW, "Pałka", Vector3.new(0.6, 1.3, 0.6), t * CFrame.new(0, 4.2 + (i % 3), 0), C(120, 80, 50))
	end
	local p = o * CFrame.new(0, 0, 12.5) -- pomost od strony ścieżki
	tex(cz(G_PNIE, "Pomost", Vector3.new(5, 0.5, 9), p * CFrame.new(0, 1.3, -3), DREWNO_J), TEX.deski, 4, { N.Top })
	for _, s in ipairs({ -1, 1 }) do
		for _, z in ipairs({ 1, -3, -7 }) do
			cz(G_PNIE, "Pal pomostu", Vector3.new(0.7, 2.6, 0.7), p * CFrame.new(s * 2.4, 0.9, z), DREWNO)
		end
	end
	task.wait()
end

------------------------------------------------------------ chata leśnika
do
	local o = pkt(50, -24) * CFrame.Angles(0, math.rad(-20), 0)
	local w, g, h = 13, 11, 8
	tex(cz(G_PNIE, "Podmurówka", Vector3.new(w + 0.8, 2, g + 0.8), o * CFrame.new(0, 1, 0), KAMIEN), TEX.kamien, 5)
	tex(cz(G_PNIE, "Ściany chaty", Vector3.new(w, h, g), o * CFrame.new(0, 2 + h / 2, 0), C(250, 236, 208)), TEX.tynk, 9, BOKI, C(255, 240, 226))
	for _, sx in ipairs({ -1, 1 }) do
		for _, sz in ipairs({ -1, 1 }) do
			cz(G_PNIE, "Słup chaty", Vector3.new(0.9, h, 0.9), o * CFrame.new(sx * (w / 2 - 0.2), 2 + h / 2, sz * (g / 2 - 0.2)), DREWNO)
		end
	end
	cz(G_PNIE, "Belka chaty", Vector3.new(w + 0.6, 0.8, g + 0.6), o * CFrame.new(0, 2 + h - 0.4, 0), DREWNO)
	local dachH = 7
	local kat = math.atan(dachH / (g / 2))
	local bieg = g / 2 + 1.8
	local dl = bieg / math.cos(kat)
	for _, obrot in ipairs({ 0, math.pi }) do
		local f = o * CFrame.new(0, 2 + h, 0) * CFrame.Angles(0, obrot, 0)
		local polac = cz(G_KORONY, "Połać chaty", Vector3.new(w + 3, 1.1, dl), f * CFrame.new(0, dachH - bieg * math.tan(kat) / 2 + 0.6, bieg / 2) * CFrame.Angles(kat, 0, 0), C(104, 150, 92))
		tex(polac, TEX.gont, 5, { N.Top }, BIALY, 0.5)
		for _, sx in ipairs({ -1, 1 }) do
			tex(cz(G_PNIE, "Szczyt chaty", Vector3.new(1, dachH, g / 2), f * CFrame.new(sx * (w / 2 - 0.5), dachH / 2, g / 4) * CFrame.Angles(0, math.pi, 0), C(250, 236, 208), nil, "WedgePart"), TEX.tynk, 9, { N.Left, N.Right }, C(255, 240, 226))
		end
	end
	cz(G_KORONY, "Kalenica chaty", Vector3.new(w + 3.4, 1.1, 1.1), o * CFrame.new(0, 2 + h + dachH + 0.95, 0) * CFrame.Angles(math.pi / 4, 0, 0), C(70, 104, 66))
	tex(cz(G_REKW, "Drzwi chaty", Vector3.new(3.4, 6, 0.4), o * CFrame.new(-2, 5, g / 2 + 0.1), DREWNO_J), TEX.deski, 4, { N.Back })
	cz(G_REKW, "Okno rama", Vector3.new(3.4, 3.4, 0.3), o * CFrame.new(3, 6.4, g / 2 + 0.1), DREWNO)
	cz(kont, "Okno szyba", Vector3.new(2.6, 2.6, 0.3), o * CFrame.new(3, 6.4, g / 2 + 0.2), OKNO, Enum.Material.Neon)
	cz(kont, "Okno szczeblina", Vector3.new(0.25, 2.6, 0.3), o * CFrame.new(3, 6.4, g / 2 + 0.3), DREWNO)
	cz(kont, "Okno szczeblina", Vector3.new(2.6, 0.25, 0.3), o * CFrame.new(3, 6.4, g / 2 + 0.3), DREWNO)
	tex(cz(G_PNIE, "Komin chaty", Vector3.new(2.4, 8, 2.4), o * CFrame.new(3.4, 2 + h + 4, -1.6), C(190, 104, 82)), "rbxassetid://85599806414499", 4)
	for i = 0, 5 do -- stos drewna przy ścianie
		local d = cz(G_REKW, "Polano", Vector3.new(3.4, 1.1, 1.1), o * CFrame.new(-w / 2 - 2.2, 0.6 + (i // 3) * 1.1, -2 + (i % 3) * 1.15 + (i // 3) * 0.55), DREWNO_J)
		d.Shape = Enum.PartType.Cylinder
	end
	task.wait()
end

------------------------------------------------------------ grzyby, głazy, pniaki, krzaki, kwiaty, latarnie
local function gdzie(margines: number): (number, number)
	for _ = 1, 40 do
		local x, z = los:NextNumber(-68, 70), los:NextNumber(-26, 26)
		if wolne(x, z, margines) then
			return x, z
		end
	end
	return 0, 30
end
for _ = 1, 16 do -- muchomory
	local x, z = gdzie(0)
	local s = los:NextNumber(0.7, 1.5)
	local o = pkt(x, z)
	cz(G_REKW, "Nóżka grzyba", Vector3.new(0.7 * s, 1.5 * s, 0.7 * s), o * CFrame.new(0, 0.75 * s, 0), C(250, 240, 220))
	kopula(G_KORONY, "Kapelusz grzyba", Vector3.new(2.6 * s, 1.5 * s, 2.6 * s), o * CFrame.new(0, 1.7 * s, 0), C(220, 64, 58))
	for i = 0, 3 do
		local a = i * 1.6 + x
		kopula(kont, "Kropka", Vector3.new(0.5 * s, 0.3 * s, 0.5 * s), o * CFrame.new(math.cos(a) * 0.7 * s, 2.25 * s, math.sin(a) * 0.7 * s), BIALY).CanCollide = false
	end
	oddech()
end
for _ = 1, 18 do -- głazy
	local x, z = gdzie(1)
	local s = los:NextNumber(1.6, 4.2)
	local p = cz(G_PNIE, "Głaz", Vector3.new(s * 1.3, s, s * 1.1), pkt(x, z, s * 0.4) * CFrame.Angles(math.rad(los:NextNumber(-14, 14)), los:NextNumber(0, 3), math.rad(los:NextNumber(-14, 14))), if los:NextNumber() < 0.5 then KAMIEN else KAMIEN_C)
	tex(p, TEX.kamien, 4, { N.Front, N.Back, N.Left, N.Right, N.Top })
	oddech()
end
for _ = 1, 7 do -- pniaki
	local x, z = gdzie(1)
	local o = pkt(x, z)
	local r = los:NextNumber(2, 3)
	walec(G_PNIE, "Pniak", r, 1.5, o * CFrame.new(0, 0.75, 0), DREWNO_J)
	walec(G_PNIE, "Słoje pniaka", r * 0.82, 0.1, o * CFrame.new(0, 1.52, 0), C(232, 196, 140)).CanCollide = false
	oddech()
end
for _ = 1, 30 do -- krzaki
	local x, z = gdzie(0)
	local s = los:NextNumber(1.8, 3.6)
	local kol = C(86, 150, 80):Lerp(C(130, 190, 96), los:NextNumber())
	cz(G_KORONY, "Krzak", Vector3.new(s, s * 0.8, s), pkt(x, z, s * 0.34) * CFrame.Angles(math.rad(los:NextNumber(-10, 10)), los:NextNumber(0, 3), math.rad(los:NextNumber(-10, 10))), kol).CanCollide = false
	if los:NextNumber() < 0.5 then
		for i = 1, 3 do
			cz(kont, "Jagoda", Vector3.new(0.4, 0.4, 0.4), pkt(x + los:NextNumber(-s / 3, s / 3), z + los:NextNumber(-s / 3, s / 3), s * 0.76), C(226, 70, 96)).CanCollide = false
		end
	end
	oddech()
end
do
	local m = grupa("Kwiaty")
	local barwy = { C(250, 220, 90), C(246, 240, 236), C(236, 120, 170), C(150, 130, 240) }
	for _ = 1, 60 do
		local x, z = gdzie(-2)
		cz(m, "Łodyga", Vector3.new(0.15, 0.9, 0.15), pkt(x, z, 0.45), C(90, 150, 80)).CanCollide = false
		cz(m, "Kwiat", Vector3.new(0.5, 0.35, 0.5), pkt(x, z, 1) * CFrame.Angles(0, los:NextNumber(0, 1.5), 0), barwy[los:NextInteger(1, 4)]).CanCollide = false
	end
	m.Parent = kont
	task.wait()
end
for _, x in ipairs({ -52, -14, 14, 40, 64 }) do -- latarnie przy ścieżce
	local z = zSciezki(x) + (if x % 4 == 0 then 7 else -7)
	local o = pkt(x, z)
	local czarny = C(52, 50, 58)
	cz(G_REKW, "Podstawa latarni", Vector3.new(1.4, 0.8, 1.4), o * CFrame.new(0, 0.4, 0), czarny)
	cz(G_REKW, "Słup latarni", Vector3.new(0.5, 8, 0.5), o * CFrame.new(0, 4, 0), czarny)
	cz(G_REKW, "Ramię latarni", Vector3.new(2.2, 0.35, 0.35), o * CFrame.new(0.9, 7.8, 0), czarny)
	local l = cz(G_REKW, "Klosz", Vector3.new(1.2, 1.5, 1.2), o * CFrame.new(1.8, 6.8, 0), OKNO, Enum.Material.Neon)
	cz(G_REKW, "Daszek latarni", Vector3.new(1.7, 0.35, 1.7), o * CFrame.new(1.8, 7.7, 0), czarny)
	local sw = Instance.new("PointLight")
	sw.Color, sw.Range, sw.Brightness = OKNO, 22, 1.3
	sw.Parent = l
end

if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return string.format("%s: %d części w (%d; %.1f; %d)", NAZWA, licznik, X0, Y0, Z0)
