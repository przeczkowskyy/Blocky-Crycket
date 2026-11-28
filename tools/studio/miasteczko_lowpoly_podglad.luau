-- Podgląd stylu „low poly” dla miasteczka (Paweł 28.11: „nowy styl budynków/modeli i powiększony nieco plac”, na wzór
-- jego referencji assets/raw/MiasteczkoMakieta/ref_pawla_1–3.png). To NIE jest przebudowa miasteczka: generator Karola
-- (swiat/miasteczko_bazar) i kontener Workspace/MiasteczkoBazar zostają nietknięte. Skrypt stawia osobny wycinek placu
-- w wolnym miejscu mapy (kontener Workspace/MiasteczkoLowPolyPodglad, atrybut Wygenerowane), żeby obaj mogli ocenić
-- styl w silniku, zanim cokolwiek trafi do generatora (propozycja D-168).
--   Uruchomienie: python tools/studio_mcp.py luau tools/studio/miasteczko_lowpoly_podglad.luau   (ponowne = odbudowa)
--   Usunięcie:    skasować kontener Workspace/MiasteczkoLowPolyPodglad
-- Wersja 2 (Paweł 28.11: „żeby nie był pustymi robloxowymi klockami… ponakładać tekstury albo tak wymodelować, żeby
-- przypominał obrazki z referencji”): bryły low poly jak na referencjach (tynk z łatami cegieł, mur pruski, grube
-- kolorowe dachy z wiatrownicami, lukarny, ceglane kominy, wieża zegarowa, studnia, wóz, płot, świerki) i NASZE tekstury
-- z paczki sali wyboru klasy (CsTex: tynk, kamień, cegła, belka, deski, gont, bruk, skrzynia — już wgrane do Roblox,
-- rejestr assets/manifest.json). Parter każdego domu jest pusty w środku (drzwi 5 × 7): wnętrze i NPC się mieszczą.
local CHS = game:GetService("ChangeHistoryService")
local NAZWA = "MiasteczkoLowPolyPodglad"
local X0, Z0 = 976, -500 -- wolne miejsce na południe od miasteczka (sprawdzone 28.11: tylko Baseplate)

local bp = workspace:FindFirstChild("Baseplate")
local Y0 = (bp and bp:IsA("BasePart")) and (bp.Position.Y + bp.Size.Y / 2) or 0
local stary = workspace:FindFirstChild(NAZWA)
if stary and not stary:GetAttribute("Wygenerowane") then
	return "W Workspace jest kontener " .. NAZWA .. " bez atrybutu Wygenerowane — nie ruszam"
end
for _, p in ipairs(workspace:GetPartBoundsInBox(CFrame.new(X0, Y0 + 30, Z0), Vector3.new(136, 58, 92))) do
	if p ~= bp and not (stary and p:IsDescendantOf(stary)) then
		return "Miejsce podglądu jest zajęte przez " .. p:GetFullName() .. " — nic nie zbudowane"
	end
end

local rec = CHS:TryBeginRecording("Podgląd stylu low poly miasteczka")
if stary then
	stary:Destroy()
end
local kont = Instance.new("Folder")
kont.Name = NAZWA
kont:SetAttribute("Wygenerowane", true)
kont:SetAttribute("Autor", "Paweł (Claude Code), 2026-11-28")
kont:SetAttribute("Opis", "Podgląd stylu low poly — propozycja D-168; nie jest częścią gry")
kont.Parent = workspace

local function C(r: number, g: number, b: number): Color3
	return Color3.fromRGB(r, g, b)
end
local DREWNO, DREWNO_J = C(96, 62, 44), C(168, 116, 72)
local KAMIEN, KAMIEN_C = C(176, 170, 190), C(140, 134, 156)
local CEGLA = C(190, 104, 82)
local OKNO = C(255, 208, 104)
local BIALY = Color3.new(1, 1, 1)
local los = Random.new(2811)
local YB = Y0 + 0.6 -- wierzch bruku
local licznik = 0

-- tekstury z paczki sali wyboru klasy (assets/processed/ClassSelectTextures, status in_roblox)
local TEX = {
	kamien = "rbxassetid://124850720793067", tynk = "rbxassetid://83860363530000", cegla = "rbxassetid://85599806414499",
	belka = "rbxassetid://71241194302925", deski = "rbxassetid://120082727765133", gont = "rbxassetid://114017817423852",
	bruk = "rbxassetid://140378080945883", skrzynia = "rbxassetid://122070761203947",
	plyty = "rbxassetid://99730536392239",
}
local N = Enum.NormalId
local BOKI = { N.Front, N.Back, N.Left, N.Right }
local WSZYSTKIE = { N.Front, N.Back, N.Left, N.Right, N.Top, N.Bottom }
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
	p.CFrame = cf
	p.Color = kolor
	p.Material = mat or Enum.Material.SmoothPlastic
	p.Anchored = true
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = rodzic
	licznik += 1
	return p
end

local function oddaj(m: Instance)
	m.Parent = kont
	task.wait()
end

-- ostrosłup z czterech CornerWedgePart (wierzchołek klina leży nad jego rogiem +X, −Z)
local function ostroslup(m: Instance, nazwa: string, podstawa: CFrame, bok: number, wys: number, kolor: Color3)
	for i = 0, 3 do
		local obr = CFrame.Angles(0, i * math.pi / 2, 0)
		local p = cz(m, nazwa, Vector3.new(bok / 2, wys, bok / 2), podstawa * obr * CFrame.new(-bok / 4, wys / 2, bok / 4), kolor, nil, "CornerWedgePart")
		p.CanCollide = false
	end
end

local function okno(m: Instance, cf: CFrame, sw: number, sh: number, okiennice: boolean?) -- cf: punkt na ścianie, +Z na zewnątrz
	cz(m, "Okno rama", Vector3.new(sw + 0.8, sh + 0.8, 0.3), cf * CFrame.new(0, 0, 0.1), DREWNO)
	cz(m, "Okno szyba", Vector3.new(sw, sh, 0.3), cf * CFrame.new(0, 0, 0.2), OKNO, Enum.Material.Neon)
	cz(m, "Okno szczeblina", Vector3.new(0.25, sh, 0.3), cf * CFrame.new(0, 0, 0.3), DREWNO)
	cz(m, "Okno szczeblina", Vector3.new(sw, 0.25, 0.3), cf * CFrame.new(0, 0, 0.3), DREWNO)
	cz(m, "Parapet", Vector3.new(sw + 1.4, 0.35, 0.8), cf * CFrame.new(0, -sh / 2 - 0.55, 0.4), DREWNO_J)
	if okiennice then
		for _, s in ipairs({ -1, 1 }) do
			local o = cz(m, "Okiennica", Vector3.new(sw * 0.46, sh + 0.5, 0.25), cf * CFrame.new(s * (sw / 2 + 0.4 + sw * 0.23), 0, 0.2), C(86, 128, 96))
			tex(o, TEX.deski, 3, { N.Back }, C(150, 210, 160))
		end
	end
end

local function skrzynkaKwiatow(m: Instance, cf: CFrame, szer: number)
	cz(m, "Skrzynka", Vector3.new(szer, 0.7, 0.9), cf * CFrame.new(0, 0, 0.55), DREWNO)
	local kwiaty = { C(236, 84, 96), C(250, 200, 70), C(246, 240, 236), C(214, 110, 200) }
	local n = math.floor(szer / 0.75)
	for i = 1, n do
		cz(m, "Liście", Vector3.new(0.6, 0.5, 0.6), cf * CFrame.new(-szer / 2 + (i - 0.5) * szer / n, 0.5, 0.55) * CFrame.Angles(0, los:NextNumber(0, 1.5), 0), C(86, 150, 80))
		cz(m, "Kwiat", Vector3.new(0.4, 0.4, 0.4), cf * CFrame.new(-szer / 2 + (i - 0.5) * szer / n, 0.9, 0.55) * CFrame.Angles(0, los:NextNumber(0, 1.5), 0), kwiaty[los:NextInteger(1, 4)])
	end
end

type Opcje = { szczytem: boolean?, szyld: Color3?, markiza: { Color3 }?, komin: boolean?, lukarny: number? }

local function dom(nazwa: string, x: number, z: number, w: number, g: number, h1: number, h2: number, dachH: number,
	kolDachu: Color3, odcienTynku: Color3, opcje: Opcje?)
	local op: Opcje = opcje or {}
	local m = Instance.new("Model")
	m.Name = nazwa
	local o = CFrame.new(X0 + x, YB, Z0 + z)
	local T, J, B = 1, 1, 0.8 -- grubość ściany, wysunięcie piętra, grubość belki
	local TYNK = C(250, 236, 208)
	local function P(n: string, sx: number, sy: number, sz: number, px: number, py: number, pz: number, kol: Color3, rot: CFrame?): BasePart
		return cz(m, n, Vector3.new(sx, sy, sz), o * CFrame.new(px, py, pz) * (rot or CFrame.new()), kol)
	end
	local function tynk(p: BasePart, sciany: { Enum.NormalId }?)
		tex(p, TEX.tynk, 9, sciany, odcienTynku)
	end

	-- parter: tynk z łatami cegieł, pusty w środku, otwór drzwi 5 × 7 od frontu (+Z); dołem kamienny cokół
	local dW, dH = 5, 7
	local bok = (w - dW) / 2
	tex(P("Podłoga", w - 0.2, 0.3, g - 0.2, 0, 0.15, 0, C(170, 128, 88)), TEX.deski, 6, { N.Top })
	tynk(P("Ściana tył", w, h1, T, 0, h1 / 2, -g / 2 + T / 2, TYNK))
	tynk(P("Ściana lewa", T, h1, g - 2 * T, -w / 2 + T / 2, h1 / 2, 0, TYNK))
	tynk(P("Ściana prawa", T, h1, g - 2 * T, w / 2 - T / 2, h1 / 2, 0, TYNK))
	tynk(P("Front lewy", bok, h1, T, -(dW + bok) / 2, h1 / 2, g / 2 - T / 2, TYNK))
	tynk(P("Front prawy", bok, h1, T, (dW + bok) / 2, h1 / 2, g / 2 - T / 2, TYNK))
	tynk(P("Nadproże", dW, h1 - dH, T, 0, dH + (h1 - dH) / 2, g / 2 - T / 2, TYNK))
	local CK, CG = 2.4, 0.4 -- cokół: wysokość i wysunięcie
	local function cokol(sx: number, sz: number, px: number, pz: number)
		local p = P("Cokół", sx, CK, sz, px, CK / 2, pz, KAMIEN)
		tex(p, TEX.kamien, 5, BOKI)
		P("Cokół gzyms", sx + 0.2, 0.3, sz + 0.2, px, CK + 0.15, pz, KAMIEN_C)
	end
	cokol(w + 2 * CG, CG, 0, -g / 2 - CG / 2)
	cokol(CG, g, -w / 2 - CG / 2, 0)
	cokol(CG, g, w / 2 + CG / 2, 0)
	cokol(bok - 0.7, CG, -(dW / 2 + 0.7 + (bok - 0.7) / 2) - CG / 2 + 0.2, g / 2 + CG / 2)
	cokol(bok - 0.7, CG, (dW / 2 + 0.7 + (bok - 0.7) / 2) + CG / 2 - 0.2, g / 2 + CG / 2)
	for _, sx in ipairs({ -1, 1 }) do -- słupy narożne parteru
		for _, sz in ipairs({ -1, 1 }) do
			P("Słup parteru", B, h1 - CK, B, sx * (w / 2 - B / 2 + 0.25), CK + (h1 - CK) / 2, sz * (g / 2 - B / 2 + 0.25), DREWNO)
		end
	end
	P("Futryna L", 0.7, dH, 1.3, -dW / 2 - 0.35, dH / 2, g / 2 - 0.4, DREWNO)
	P("Futryna P", 0.7, dH, 1.3, dW / 2 + 0.35, dH / 2, g / 2 - 0.4, DREWNO)
	P("Futryna góra", dW + 2.2, 0.8, 1.4, 0, dH + 0.4, g / 2 - 0.4, DREWNO)
	for _, s in ipairs({ -1, 1 }) do -- łuk drzwi: dwa zastrzały w rogach otworu
		P("Łuk drzwi", 0.5, 1.9, 0.8, s * (dW / 2 - 0.55), dH - 0.6, g / 2 - 0.4, DREWNO, CFrame.Angles(0, 0, s * math.rad(-42)))
	end
	P("Schodek", dW + 2.4, 0.5, 1.6, 0, 0.25, g / 2 + 0.8, KAMIEN_C)
	local skrzydlo = P("Skrzydło drzwi", 0.4, dH - 0.2, dW - 0.4, -dW / 2 - 0.3, dH / 2, g / 2 + dW / 2, DREWNO_J, CFrame.Angles(0, math.rad(-18), 0))
	tex(skrzydlo, TEX.deski, 4, { N.Left, N.Right })
	P("Okucie", 0.5, 0.3, dW - 0.8, -dW / 2 - 0.3, dH * 0.75, g / 2 + dW / 2, C(60, 60, 70), CFrame.Angles(0, math.rad(-18), 0))
	P("Okucie", 0.5, 0.3, dW - 0.8, -dW / 2 - 0.3, dH * 0.25, g / 2 + dW / 2, C(60, 60, 70), CFrame.Angles(0, math.rad(-18), 0))
	if bok >= 6.5 then -- okna parteru po bokach drzwi, pod nimi skrzynki z kwiatami
		for _, s in ipairs({ -1, 1 }) do
			local cf = o * CFrame.new(s * (dW / 2 + bok / 2 + 0.3), h1 * 0.6, g / 2)
			okno(m, cf, 2.8, 3, true)
			skrzynkaKwiatow(m, cf * CFrame.new(0, -2.5, 0), 3.4)
		end
	end
	local lampa = P("Lampa wnętrza", 0.8, 0.8, 0.8, 0, h1 - 1, 0, OKNO)
	lampa.Material = Enum.Material.Neon
	local swiatlo = Instance.new("PointLight")
	swiatlo.Color, swiatlo.Range, swiatlo.Brightness = OKNO, 18, 1.2
	swiatlo.Parent = lampa

	-- piętro: tynk i mur pruski, wysunięte o J
	local W, G = w + 2 * J, g + 2 * J
	local y1 = h1
	tynk(P("Piętro", W, h2, G, 0, y1 + h2 / 2, 0, TYNK))
	tex(P("Belka dolna", W + 0.5, B, G + 0.5, 0, y1 + B / 2, 0, DREWNO), TEX.belka, 4, BOKI, C(170, 150, 140))
	tex(P("Belka górna", W + 0.5, B, G + 0.5, 0, y1 + h2 - B / 2, 0, DREWNO), TEX.belka, 4, BOKI, C(170, 150, 140))
	for i = 0, math.floor(W / 3) do -- końce belek stropowych pod wysunięciem piętra
		P("Belka stropu", 0.6, 0.6, 0.9, -W / 2 + 0.8 + i * (W - 1.6) / math.floor(W / 3), y1 - 0.3, G / 2 - 0.3, DREWNO)
	end
	for _, sx in ipairs({ -1, 1 }) do
		for _, sz in ipairs({ -1, 1 }) do
			P("Słup narożny", B + 0.1, h2, B + 0.1, sx * (W / 2 - B / 2 + 0.2), y1 + h2 / 2, sz * (G / 2 - B / 2 + 0.2), DREWNO)
		end
	end
	local ph = h2 - 2 * B
	local function sciana(dl: number, cf: CFrame) -- cf: środek ściany piętra na jej powierzchni, +Z na zewnątrz
		local n = math.max(2, math.floor(dl / 6 + 0.5))
		local pw = dl / n
		for i = 1, n - 1 do
			cz(m, "Słupek", Vector3.new(0.6, ph, 0.3), cf * CFrame.new(-dl / 2 + i * pw, 0, 0.12), DREWNO)
		end
		for i = 1, n do
			local px = -dl / 2 + (i - 0.5) * pw
			if (i == 1 or i == n) and n >= 3 then -- skrajne pola: zastrzał
				local kat = math.atan(pw / ph) * (if i == 1 then 1 else -1)
				cz(m, "Zastrzał", Vector3.new(0.5, math.sqrt(pw * pw + ph * ph) * 0.92, 0.25), cf * CFrame.new(px, 0, 0.1) * CFrame.Angles(0, 0, kat), DREWNO)
			elseif pw >= 4.4 then
				okno(m, cf * CFrame.new(px, 0.1, 0), math.min(3, pw - 2), math.min(3.6, ph - 1.2))
			end
		end
	end
	local ys = y1 + h2 / 2
	sciana(W, o * CFrame.new(0, ys, G / 2))
	sciana(W, o * CFrame.new(0, ys, -G / 2) * CFrame.Angles(0, math.pi, 0))
	sciana(G, o * CFrame.new(W / 2, ys, 0) * CFrame.Angles(0, math.pi / 2, 0))
	sciana(G, o * CFrame.new(-W / 2, ys, 0) * CFrame.Angles(0, -math.pi / 2, 0))

	-- dach: dwie grube połacie z okapem i gontem; kalenica wzdłuż X, a przy „szczytem” — wzdłuż Z (szczyt od frontu)
	local Wr, Gr = W, G
	local rama = o * CFrame.new(0, y1 + h2, 0)
	if op.szczytem then
		Wr, Gr = G, W
		rama = rama * CFrame.Angles(0, math.pi / 2, 0)
	end
	local okap, okapX = 1.8, 1.4
	local tg = dachH / (Gr / 2)
	local kat = math.atan(tg)
	local bieg = Gr / 2 + okap
	local dl = bieg / math.cos(kat)
	local ciemny = kolDachu:Lerp(Color3.new(0, 0, 0), 0.32)
	for _, obrot in ipairs({ 0, math.pi }) do -- obie połacie w tym samym układzie: lokalne +Z biegnie w dół połaci
		local f = rama * CFrame.Angles(0, obrot, 0)
		local polac = cz(m, "Połać", Vector3.new(Wr + 2 * okapX, 1.1, dl), f * CFrame.new(0, dachH - bieg * tg / 2 + 0.6, bieg / 2) * CFrame.Angles(kat, 0, 0), kolDachu)
		tex(polac, TEX.gont, 5, { N.Top }, BIALY, 0.5)
		cz(m, "Okap", Vector3.new(Wr + 2 * okapX + 0.3, 0.6, 1.1), f * CFrame.new(0, dachH - bieg * tg + 0.6, bieg - 0.2) * CFrame.Angles(kat, 0, 0), ciemny)
		for _, sx in ipairs({ -1, 1 }) do
			-- wiatrownica: ciemna deska wzdłuż krawędzi szczytu
			cz(m, "Wiatrownica", Vector3.new(0.5, 1.6, dl + 0.3), f * CFrame.new(sx * (Wr / 2 + okapX - 0.05), dachH - bieg * tg / 2 + 0.45, bieg / 2) * CFrame.Angles(kat, 0, 0), ciemny)
			-- szczyt z tynku (klin: wysoka krawędź leży po jego stronie +Z, więc obrót o 180° kieruje ją do kalenicy)
			local szczyt = cz(m, "Szczyt", Vector3.new(T, dachH, Gr / 2), f * CFrame.new(sx * (Wr / 2 - T / 2), dachH / 2, Gr / 4) * CFrame.Angles(0, math.pi, 0), TYNK, nil, "WedgePart")
			tex(szczyt, TEX.tynk, 9, { N.Left, N.Right }, odcienTynku)
		end
	end
	cz(m, "Kalenica", Vector3.new(Wr + 2 * okapX + 0.5, 1.1, 1.1), rama * CFrame.new(0, dachH + 0.95, 0) * CFrame.Angles(math.pi / 4, 0, 0), ciemny)
	for _, sx in ipairs({ -1, 1 }) do -- mur pruski i okienko na szczytach
		local sc = rama * CFrame.new(sx * Wr / 2, 0, 0) * CFrame.Angles(0, sx * math.pi / 2, 0)
		cz(m, "Słupek szczytu", Vector3.new(0.6, dachH * 0.86, 0.3), sc * CFrame.new(0, dachH * 0.43, 0.12), DREWNO)
		cz(m, "Rygiel szczytu", Vector3.new(Gr * 0.52, 0.5, 0.3), sc * CFrame.new(0, dachH * 0.46, 0.12), DREWNO)
		okno(m, sc * CFrame.new(0, dachH * 0.24, 0), 2, 2)
	end
	-- lukarny na przedniej połaci (tylko gdy kalenica biegnie wzdłuż frontu)
	if op.lukarny and not op.szczytem then
		local n = op.lukarny
		for i = 1, n do
			local lx = -Wr / 2 + i * Wr / (n + 1)
			local z0 = Gr * 0.2
			local ysl = dachH - z0 * tg
			local sz, gl = 4.2, 4.6
			local l = rama * CFrame.new(lx, ysl, z0)
			tynk(cz(m, "Lukarna", Vector3.new(sz, 5.4, gl), l * CFrame.new(0, -0.3, gl / 2 - 0.6), TYNK), { N.Back, N.Left, N.Right })
			okno(m, l * CFrame.new(0, 0.9, gl - 0.6), 2, 2.2)
			for _, s in ipairs({ -1, 1 }) do
				-- daszek lukarny: dwa kliny, wysoka krawędź do środka
				cz(m, "Daszek lukarny", Vector3.new(gl + 1.2, 1.9, sz / 2 + 0.7), l * CFrame.new(s * (sz / 4 + 0.35), 3.35, gl / 2 - 0.4) * CFrame.Angles(0, -s * math.pi / 2, 0), kolDachu, nil, "WedgePart")
			end
		end
	end
	if op.komin ~= false then -- ceglany komin z czapą
		local kx, kz = W * 0.27, -G * 0.2
		local wysK = dachH + 3
		tex(P("Komin", 2.6, wysK, 2.6, kx, y1 + h2 + wysK / 2 - 1, kz, CEGLA), TEX.cegla, 4, BOKI)
		P("Komin czapa", 3.3, 0.6, 3.3, kx, y1 + h2 + wysK - 0.7, kz, KAMIEN)
		P("Komin wylot", 1.6, 0.9, 1.6, kx, y1 + h2 + wysK - 0.1, kz, C(70, 60, 64))
	end
	if op.szyld then -- szyld na wysięgniku
		P("Wysięgnik", 0.4, 0.4, 4, -w / 2 + 3, y1 - 0.9, g / 2 + 2 + J, DREWNO)
		tex(P("Szyld", 0.35, 2.6, 3, -w / 2 + 3, y1 - 2.6, g / 2 + 2.6 + J, DREWNO_J), TEX.deski, 3, { N.Left, N.Right })
		P("Szyld znak", 0.45, 1.4, 1.6, -w / 2 + 3, y1 - 2.6, g / 2 + 2.6 + J, op.szyld)
	end
	if op.markiza then -- pasiasta markiza nad wejściem
		local pasy = 6
		local sm = (dW + 6) / pasy
		for i = 1, pasy do
			P("Markiza", sm, 0.3, 4.6, -(dW + 6) / 2 + (i - 0.5) * sm, dH + 1.9, g / 2 + 2 + J, op.markiza[(i % 2) + 1], CFrame.Angles(math.rad(20), 0, 0))
		end
		for _, s in ipairs({ -1, 1 }) do
			P("Słupek markizy", 0.35, dH + 0.6, 0.35, s * (dW / 2 + 2.6), (dH + 0.6) / 2, g / 2 + 3.9 + J, DREWNO)
		end
	end
	oddaj(m)
end

local function drzewo(x: number, z: number, s: number, kol: Color3)
	local m = Instance.new("Model")
	m.Name = "Drzewo"
	local o = CFrame.new(X0 + x, YB, Z0 + z)
	tex(cz(m, "Pień", Vector3.new(1.5 * s, 6 * s, 1.5 * s), o * CFrame.new(0, 3 * s, 0), DREWNO_J), TEX.belka, 3)
	local warstwy = { { 8, 3.4, 6.5, 0 }, { 6.2, 3, 9.2, 45 }, { 4, 2.8, 11.6, 20 } }
	for i, w in ipairs(warstwy) do
		cz(m, "Korona", Vector3.new(w[1] * s, w[2] * s, w[1] * s),
			o * CFrame.new(0, w[3] * s, 0) * CFrame.Angles(math.rad(los:NextNumber(-6, 6)), math.rad(w[4]), math.rad(los:NextNumber(-6, 6))),
			kol:Lerp(Color3.new(1, 1, 0.6), (i - 1) * 0.12))
	end
	oddaj(m)
end

local function swierk(x: number, z: number, s: number)
	local m = Instance.new("Model")
	m.Name = "Świerk"
	local o = CFrame.new(X0 + x, YB, Z0 + z) * CFrame.Angles(0, los:NextNumber(0, 1.5), 0)
	cz(m, "Pień", Vector3.new(1.3 * s, 3.4 * s, 1.3 * s), o * CFrame.new(0, 1.7 * s, 0), C(110, 76, 52))
	local pietra = { { 9, 6, 2.6, C(52, 110, 84) }, { 7.2, 5.6, 6, C(62, 124, 90) }, { 5.2, 5.4, 9.4, C(74, 138, 96) } }
	for _, p in ipairs(pietra) do
		ostroslup(m, "Piętro świerka", o * CFrame.new(0, p[3] * s, 0), p[1] * s, p[2] * s, p[4])
	end
	oddaj(m)
end

local function latarnia(x: number, z: number)
	local m = Instance.new("Model")
	m.Name = "Latarnia"
	local o = CFrame.new(X0 + x, YB, Z0 + z)
	local czarny = C(52, 50, 58)
	cz(m, "Podstawa", Vector3.new(1.4, 0.8, 1.4), o * CFrame.new(0, 0.4, 0), czarny)
	cz(m, "Słup", Vector3.new(0.5, 9, 0.5), o * CFrame.new(0, 4.5, 0), czarny)
	cz(m, "Ramię", Vector3.new(4, 0.35, 0.35), o * CFrame.new(0, 8.8, 0), czarny)
	for _, s in ipairs({ -1, 1 }) do
		local l = cz(m, "Klosz", Vector3.new(1.2, 1.5, 1.2), o * CFrame.new(s * 1.8, 7.8, 0), OKNO, Enum.Material.Neon)
		cz(m, "Daszek", Vector3.new(1.7, 0.35, 1.7), o * CFrame.new(s * 1.8, 8.65, 0), czarny)
		local sw = Instance.new("PointLight")
		sw.Color, sw.Range, sw.Brightness = OKNO, 20, 1.1
		sw.Parent = l
	end
	oddaj(m)
end

------------------------------------------------------------ plac
do
	local m = Instance.new("Model")
	m.Name = "Plac"
	local o = CFrame.new(X0, Y0, Z0)
	cz(m, "Trawa", Vector3.new(132, 0.4, 88), o * CFrame.new(0, 0.2, 0), C(120, 176, 92))
	-- plac z płyt (CsTex02) w ciepłym odcieniu jak szary bruk na referencjach; kocie łby (CsTex09) tylko wokół studni
	tex(cz(m, "Bruk", Vector3.new(116, 0.6, 70), o * CFrame.new(0, 0.3, 2), C(206, 196, 186)), TEX.plyty, 6, { N.Top }, C(255, 240, 220))
	local krag = cz(m, "Bruk przy studni", Vector3.new(0.14, 22, 22), o * CFrame.new(4, 0.64, 16) * CFrame.Angles(0, 0, math.pi / 2), C(190, 184, 190))
	krag.Shape = Enum.PartType.Cylinder
	krag.CanCollide = false
	tex(krag, TEX.bruk, 5, { N.Right, N.Left }, C(230, 222, 214))
	for _ = 1, 26 do -- kępy trawy i krzaczki na obrzeżu
		local kx, kz = los:NextNumber(-64, 64), los:NextNumber(-42, 42)
		if math.abs(kx) > 59 or math.abs(kz - 2) > 36 then
			local s = los:NextNumber(1.6, 3.2)
			cz(m, "Krzak", Vector3.new(s, s * 0.8, s), o * CFrame.new(kx, 0.4 + s * 0.35, kz) * CFrame.Angles(los:NextNumber(-0.2, 0.2), los:NextNumber(0, 1.5), los:NextNumber(-0.2, 0.2)),
				C(96, 160, 84):Lerp(C(140, 196, 96), los:NextNumber())).CanCollide = false
		end
	end
	oddaj(m)
end

------------------------------------------------------------ domy (front do placu, czyli na +Z)
local ROZ, KREM, CHLOD = C(255, 232, 224), C(255, 246, 228), C(240, 238, 250)
dom("Karczma", -36, -19, 30, 22, 9, 8, 11, C(190, 70, 62), ROZ, { szyld = C(255, 196, 64), lukarny = 2 })
dom("Sklep magiczny", -3, -18, 20, 20, 9, 8, 14, C(140, 100, 206), CHLOD, { szczytem = true, szyld = C(120, 220, 255) })
dom("Zbrojownia", 25, -19, 22, 22, 9, 7, 10, C(84, 150, 206), KREM, { markiza = { C(214, 70, 62), C(246, 240, 226) }, lukarny = 1 })
dom("Dom mieszczan", 50, -17, 15, 16, 8, 7, 11, C(110, 160, 92), ROZ, { szczytem = true })

------------------------------------------------------------ wieża zegarowa (za domami, jak na referencjach)
do
	local m = Instance.new("Model")
	m.Name = "Wieża zegarowa"
	local o = CFrame.new(X0 + 11.5, Y0 + 0.4, Z0 - 36)
	local bok, wys = 9, 30
	tex(cz(m, "Trzon", Vector3.new(bok, wys, bok), o * CFrame.new(0, wys / 2, 0), KAMIEN), TEX.kamien, 6)
	cz(m, "Gzyms", Vector3.new(bok + 1.2, 0.8, bok + 1.2), o * CFrame.new(0, wys + 0.4, 0), KAMIEN_C)
	local gb, gw = bok + 2, 9 -- izba zegara: tynk i mur pruski
	tex(cz(m, "Izba zegara", Vector3.new(gb, gw, gb), o * CFrame.new(0, wys + 0.8 + gw / 2, 0), C(250, 236, 208)), TEX.tynk, 9, BOKI, C(255, 240, 228))
	for _, y in ipairs({ wys + 1.2, wys + 0.4 + gw }) do
		cz(m, "Belka", Vector3.new(gb + 0.5, 0.8, gb + 0.5), o * CFrame.new(0, y, 0), DREWNO)
	end
	for _, sx in ipairs({ -1, 1 }) do
		for _, sz in ipairs({ -1, 1 }) do
			cz(m, "Słup", Vector3.new(0.9, gw, 0.9), o * CFrame.new(sx * (gb / 2 - 0.25), wys + 0.8 + gw / 2, sz * (gb / 2 - 0.25)), DREWNO)
		end
	end
	for i = 0, 3 do -- cztery tarcze zegara
		local t = o * CFrame.new(0, wys + 0.8 + gw / 2, 0) * CFrame.Angles(0, i * math.pi / 2, 0) * CFrame.new(0, 0, gb / 2)
		cz(m, "Tarcza obrys", Vector3.new(0.3, 6.2, 6.2), t * CFrame.new(0, 0, 0.1) * CFrame.Angles(0, math.pi / 2, 0), DREWNO).Shape = Enum.PartType.Cylinder
		cz(m, "Tarcza", Vector3.new(0.3, 5.4, 5.4), t * CFrame.new(0, 0, 0.25) * CFrame.Angles(0, math.pi / 2, 0), C(252, 246, 226)).Shape = Enum.PartType.Cylinder
		cz(m, "Wskazówka", Vector3.new(0.3, 2.3, 0.2), t * CFrame.new(0, 0, 0.45) * CFrame.Angles(0, 0, math.rad(-35)) * CFrame.new(0, 1, 0), C(50, 44, 52))
		cz(m, "Wskazówka", Vector3.new(0.3, 1.6, 0.2), t * CFrame.new(0, 0, 0.45) * CFrame.Angles(0, 0, math.rad(70)) * CFrame.new(0, 0.7, 0), C(50, 44, 52))
	end
	for _, sz in ipairs({ -1, 1 }) do -- okienka trzonu
		okno(m, o * CFrame.new(0, wys * 0.55, sz * bok / 2) * CFrame.Angles(0, if sz == 1 then 0 else math.pi, 0), 1.8, 3)
		okno(m, o * CFrame.new(0, wys * 0.25, sz * bok / 2) * CFrame.Angles(0, if sz == 1 then 0 else math.pi, 0), 1.8, 3)
	end
	local yd = wys + 0.8 + gw
	cz(m, "Okap wieży", Vector3.new(gb + 2.6, 0.6, gb + 2.6), o * CFrame.new(0, yd + 0.3, 0), C(120, 44, 44))
	ostroslup(m, "Hełm wieży", o * CFrame.new(0, yd + 0.6, 0), gb + 2.2, 12, C(190, 70, 62))
	cz(m, "Iglica", Vector3.new(0.4, 3, 0.4), o * CFrame.new(0, yd + 13.5, 0), C(60, 56, 64))
	cz(m, "Gałka", Vector3.new(1, 1, 1), o * CFrame.new(0, yd + 15, 0), C(255, 206, 80)).Shape = Enum.PartType.Ball
	oddaj(m)
end

------------------------------------------------------------ studnia
do
	local m = Instance.new("Model")
	m.Name = "Studnia"
	local o = CFrame.new(X0 + 4, YB, Z0 + 16)
	for i = 0, 7 do -- ośmiokątna cembrowina z klocków
		local a = i * math.pi / 4
		tex(cz(m, "Cembrowina", Vector3.new(3.4, 3, 1.2), o * CFrame.Angles(0, a, 0) * CFrame.new(0, 1.5, 3.6), if i % 2 == 0 then KAMIEN else KAMIEN_C), TEX.kamien, 4, { N.Back, N.Top })
	end
	cz(m, "Woda", Vector3.new(0.4, 7, 7), o * CFrame.new(0, 2.1, 0) * CFrame.Angles(0, 0, math.pi / 2), C(86, 176, 226)).Shape = Enum.PartType.Cylinder
	for _, s in ipairs({ -1, 1 }) do
		cz(m, "Słup", Vector3.new(0.7, 8, 0.7), o * CFrame.new(s * 3.9, 4, 0), DREWNO)
		local d = cz(m, "Daszek", Vector3.new(10, 0.7, 4.8), o * CFrame.new(0, 9, s * 1.7) * CFrame.Angles(0, if s == 1 then 0 else math.pi, 0) * CFrame.Angles(math.rad(32), 0, 0), C(190, 70, 62))
		tex(d, TEX.gont, 4, { N.Top }, BIALY, 0.5)
	end
	cz(m, "Wałek", Vector3.new(7.6, 0.6, 0.6), o * CFrame.new(0, 6.4, 0), DREWNO_J)
	cz(m, "Korba", Vector3.new(0.3, 1.6, 0.3), o * CFrame.new(4.4, 6, 0), C(60, 60, 70))
	cz(m, "Wiadro", Vector3.new(1.2, 1.3, 1.2), o * CFrame.new(0.6, 4.2, 0), DREWNO_J)
	cz(m, "Lina", Vector3.new(0.15, 1.9, 0.15), o * CFrame.new(0.6, 5.6, 0), C(224, 206, 160))
	oddaj(m)
end

------------------------------------------------------------ stragan
do
	local m = Instance.new("Model")
	m.Name = "Stragan"
	local o = CFrame.new(X0 - 30, YB, Z0 + 16)
	for _, sx in ipairs({ -1, 1 }) do
		for _, sz in ipairs({ -1, 1 }) do
			cz(m, "Słupek", Vector3.new(0.5, if sz == 1 then 6.2 else 7.6, 0.5), o * CFrame.new(sx * 4.4, if sz == 1 then 3.1 else 3.8, sz * 2.2), DREWNO)
		end
	end
	tex(cz(m, "Lada", Vector3.new(9.6, 0.6, 3.4), o * CFrame.new(0, 3, 1.2), DREWNO_J), TEX.deski, 4, { N.Top })
	tex(cz(m, "Skrzynia lady", Vector3.new(9, 2.6, 2.6), o * CFrame.new(0, 1.4, 1.2), DREWNO_J), TEX.skrzynia, 3, BOKI)
	for i = 1, 6 do
		cz(m, "Daszek", Vector3.new(1.7, 0.3, 6.2), o * CFrame.new(-5.1 + (i - 0.5) * 1.7, 7.1, 0) * CFrame.Angles(math.rad(17), 0, 0),
			if i % 2 == 0 then C(246, 240, 226) else C(240, 168, 52))
	end
	local owoce = { C(226, 64, 58), C(246, 160, 44), C(126, 196, 76), C(238, 210, 70) }
	for i = 1, 8 do
		cz(m, "Towar", Vector3.new(0.9, 0.9, 0.9), o * CFrame.new(-3.8 + i * 0.95, 3.75, 1.2 + los:NextNumber(-0.7, 0.7)) * CFrame.Angles(0, math.rad(los:NextNumber(0, 60)), 0), owoce[(i % 4) + 1])
	end
	oddaj(m)
end

------------------------------------------------------------ wóz z sianem
do
	local m = Instance.new("Model")
	m.Name = "Wóz"
	local o = CFrame.new(X0 + 30, YB, Z0 + 17) * CFrame.Angles(0, math.rad(28), 0)
	tex(cz(m, "Skrzynia wozu", Vector3.new(4, 0.5, 7.4), o * CFrame.new(0, 2.2, 0), DREWNO_J), TEX.deski, 4, { N.Top, N.Bottom })
	for _, s in ipairs({ -1, 1 }) do
		tex(cz(m, "Burta", Vector3.new(0.35, 1.5, 7.4), o * CFrame.new(s * 2, 3.1, 0) * CFrame.Angles(0, 0, s * math.rad(-10)), DREWNO_J), TEX.deski, 4, { N.Left, N.Right })
		cz(m, "Koło", Vector3.new(0.5, 3.6, 3.6), o * CFrame.new(s * 2.5, 1.8, -0.6), DREWNO).Shape = Enum.PartType.Cylinder
		cz(m, "Piasta", Vector3.new(0.7, 1, 1), o * CFrame.new(s * 2.55, 1.8, -0.6), DREWNO_J).Shape = Enum.PartType.Cylinder
		cz(m, "Dyszel", Vector3.new(0.35, 0.35, 5.4), o * CFrame.new(s * 1.5, 1.5, 6) * CFrame.Angles(math.rad(14), 0, 0), DREWNO)
	end
	cz(m, "Siano", Vector3.new(3.4, 1.6, 6.4), o * CFrame.new(0, 3.2, 0) * CFrame.Angles(0, 0.05, 0.04), C(232, 196, 88))
	cz(m, "Siano", Vector3.new(2.6, 1.2, 4.4), o * CFrame.new(0.2, 4.4, -0.4) * CFrame.Angles(0.06, 0.2, 0), C(240, 208, 104))
	oddaj(m)
end

------------------------------------------------------------ płot od strony łąki
do
	local m = Instance.new("Model")
	m.Name = "Płot"
	local function odcinek(x0: number, x1: number, z: number)
		local n = math.floor((x1 - x0) / 4)
		for i = 0, n do
			cz(m, "Słupek płotu", Vector3.new(0.6, 3.2 + los:NextNumber(-0.2, 0.3), 0.6), CFrame.new(X0 + x0 + i * (x1 - x0) / n, YB + 1.5, Z0 + z) * CFrame.Angles(0, 0, los:NextNumber(-0.05, 0.05)), DREWNO_J)
		end
		for _, y in ipairs({ 1.2, 2.4 }) do
			cz(m, "Żerdź", Vector3.new(x1 - x0 + 0.6, 0.35, 0.3), CFrame.new(X0 + (x0 + x1) / 2, YB + y, Z0 + z + 0.1), DREWNO)
		end
	end
	odcinek(-57, -14, 36.5)
	odcinek(14, 57, 36.5)
	oddaj(m)
end

------------------------------------------------------------ drobiazgi
do
	local m = Instance.new("Model")
	m.Name = "Beczki i skrzynie"
	for _, b in ipairs({ { -18, -4 }, { -15.6, -5.2 }, { 39.5, -5 } }) do
		local o = CFrame.new(X0 + b[1], YB, Z0 + b[2])
		cz(m, "Beczka", Vector3.new(3, 2.4, 2.4), o * CFrame.new(0, 1.5, 0) * CFrame.Angles(0, 0, math.pi / 2), DREWNO_J).Shape = Enum.PartType.Cylinder
		for _, y in ipairs({ 0.7, 2.3 }) do
			cz(m, "Obręcz", Vector3.new(0.3, 2.55, 2.55), o * CFrame.new(0, y, 0) * CFrame.Angles(0, 0, math.pi / 2), C(70, 70, 80)).Shape = Enum.PartType.Cylinder
		end
	end
	for _, s in ipairs({ { 12, -5.5, 2.6, 10 }, { 14.4, -4.6, 2, -20 }, { 12.6, -5.2, 1.8, 35 } }) do
		local y = if s[3] == 1.8 then 2.6 + 0.9 else s[3] / 2
		tex(cz(m, "Skrzynia", Vector3.new(s[3], s[3], s[3]), CFrame.new(X0 + s[1], YB + y, Z0 + s[2]) * CFrame.Angles(0, math.rad(s[4]), 0), C(196, 150, 96)), TEX.skrzynia, s[3], WSZYSTKIE)
	end
	oddaj(m)
end
drzewo(-55, 10, 1.15, C(92, 160, 78))
drzewo(57, 20, 1, C(104, 172, 84))
swierk(-58, -30, 1.25)
swierk(-50, -37, 1)
swierk(60, -32, 1.3)
swierk(30, -38, 1.05)
swierk(-12, -38, 0.9)
swierk(44, 31, 0.8)
latarnia(-17, 3)
latarnia(13, 3)
latarnia(-40, 28)
latarnia(22, 30)

if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return string.format("%s: %d części w (%d; %.1f; %d). Kamera: z (%d; 38; %d) na (%d; 9; %d)", NAZWA, licznik, X0, Y0, Z0, X0, Z0 + 72, X0, Z0 - 8)
