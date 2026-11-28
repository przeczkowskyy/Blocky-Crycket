-- Podgląd stylu „low poly” dla miasteczka (Paweł 28.11: „nowy styl budynków/modeli i powiększony nieco plac”, na wzór
-- jego referencji assets/raw/MiasteczkoMakieta/ref_pawla_1–3.png). To NIE jest przebudowa miasteczka: generator Karola
-- (swiat/miasteczko_bazar) i kontener Workspace/MiasteczkoBazar zostają nietknięte. Skrypt stawia osobny wycinek placu
-- w wolnym miejscu mapy (kontener Workspace/MiasteczkoLowPolyPodglad, atrybut Wygenerowane), żeby obaj mogli ocenić
-- styl w silniku, zanim cokolwiek trafi do generatora (propozycja D-168).
--   Uruchomienie: python tools/studio_mcp.py luau tools/studio/miasteczko_lowpoly_podglad.luau   (ponowne = odbudowa)
--   Usunięcie:    skasować kontener Workspace/MiasteczkoLowPolyPodglad
-- Styl: proste bryły, gładkie kolory bez tekstur, kamienny parter, piętro z muru pruskiego wysunięte nad parter,
-- strome kolorowe dachy z okapem, świecące okna. Parter każdego domu jest pusty w środku (drzwi 5 × 7), więc dzisiejsze
-- wnętrze i NPC mieszczą się w nim bez zmian.
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
local DREWNO, DREWNO_J = C(88, 60, 44), C(150, 104, 66)
local KAMIEN, KAMIEN_C = C(168, 170, 178), C(132, 134, 146)
local OKNO = C(255, 208, 104)
local los = Random.new(2811)
local YB = Y0 + 0.6 -- wierzch bruku
local licznik = 0

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

local function okno(m: Instance, cf: CFrame, sw: number, sh: number) -- cf: punkt na ścianie, +Z na zewnątrz
	cz(m, "Okno rama", Vector3.new(sw + 0.8, sh + 0.8, 0.3), cf * CFrame.new(0, 0, 0.1), DREWNO)
	cz(m, "Okno szyba", Vector3.new(sw, sh, 0.3), cf * CFrame.new(0, 0, 0.2), OKNO, Enum.Material.Neon)
	cz(m, "Okno szczeblina", Vector3.new(0.25, sh, 0.3), cf * CFrame.new(0, 0, 0.3), DREWNO)
	cz(m, "Okno szczeblina", Vector3.new(sw, 0.25, 0.3), cf * CFrame.new(0, 0, 0.3), DREWNO)
	cz(m, "Parapet", Vector3.new(sw + 1.4, 0.35, 0.8), cf * CFrame.new(0, -sh / 2 - 0.55, 0.4), DREWNO_J)
end

type Opcje = { szczytem: boolean?, szyld: Color3?, markiza: { Color3 }?, komin: boolean? }

local function dom(nazwa: string, x: number, z: number, w: number, g: number, h1: number, h2: number, dachH: number,
	kolDachu: Color3, kolTynku: Color3, opcje: Opcje?)
	local op: Opcje = opcje or {}
	local m = Instance.new("Model")
	m.Name = nazwa
	local o = CFrame.new(X0 + x, YB, Z0 + z)
	local T, J, B = 1, 1, 0.8 -- grubość ściany, wysunięcie piętra, grubość belki
	local function P(n: string, sx: number, sy: number, sz: number, px: number, py: number, pz: number, kol: Color3, rot: CFrame?): BasePart
		return cz(m, n, Vector3.new(sx, sy, sz), o * CFrame.new(px, py, pz) * (rot or CFrame.new()), kol)
	end

	-- parter: kamień, pusty w środku, otwór drzwi 5 × 7 od frontu (+Z)
	local dW, dH = 5, 7
	local bok = (w - dW) / 2
	P("Podłoga", w - 0.2, 0.3, g - 0.2, 0, 0.15, 0, C(170, 128, 88))
	P("Ściana tył", w, h1, T, 0, h1 / 2, -g / 2 + T / 2, KAMIEN)
	P("Ściana lewa", T, h1, g - 2 * T, -w / 2 + T / 2, h1 / 2, 0, KAMIEN)
	P("Ściana prawa", T, h1, g - 2 * T, w / 2 - T / 2, h1 / 2, 0, KAMIEN)
	P("Front lewy", bok, h1, T, -(dW + bok) / 2, h1 / 2, g / 2 - T / 2, KAMIEN)
	P("Front prawy", bok, h1, T, (dW + bok) / 2, h1 / 2, g / 2 - T / 2, KAMIEN)
	P("Nadproże", dW, h1 - dH, T, 0, dH + (h1 - dH) / 2, g / 2 - T / 2, KAMIEN)
	P("Cokół", w + 0.6, 1.2, g + 0.6, 0, 0.6, 0, KAMIEN_C).CanCollide = false
	-- cokół nie może zatkać drzwi: próg wycięty jaśniejszą płytą
	P("Próg", dW, 1.25, 1.2, 0, 0.62, g / 2 - 0.2, C(120, 92, 70)).CanCollide = false
	for _ = 1, 7 do -- pojedyncze wystające kamienie na froncie
		local sx, sy = los:NextNumber(1.6, 3), los:NextNumber(1, 1.8)
		local strona = if los:NextNumber() < 0.5 then -1 else 1
		local px = strona * (dW / 2 + 1 + los:NextNumber(0, math.max(0.1, bok - 3.2)))
		P("Kamień", sx, sy, 0.3, px, los:NextNumber(1.8, h1 - 1.6), g / 2 + 0.1, if los:NextNumber() < 0.5 then KAMIEN_C else C(190, 192, 200))
	end
	P("Futryna L", 0.7, dH, 1.3, -dW / 2 - 0.35, dH / 2, g / 2 - 0.4, DREWNO)
	P("Futryna P", 0.7, dH, 1.3, dW / 2 + 0.35, dH / 2, g / 2 - 0.4, DREWNO)
	P("Futryna góra", dW + 2.2, 0.8, 1.4, 0, dH + 0.4, g / 2 - 0.4, DREWNO)
	P("Skrzydło drzwi", 0.4, dH - 0.2, dW - 0.4, -dW / 2 - 0.3, dH / 2, g / 2 + dW / 2, DREWNO_J, CFrame.Angles(0, math.rad(-18), 0))
	if bok >= 6.5 then -- okna parteru po bokach drzwi
		for _, s in ipairs({ -1, 1 }) do
			okno(m, o * CFrame.new(s * (dW / 2 + bok / 2 + 0.3), h1 * 0.56, g / 2), 2.8, 3.2)
		end
	end
	local swiatlo = Instance.new("PointLight")
	swiatlo.Color, swiatlo.Range, swiatlo.Brightness = OKNO, 18, 1.2
	local lampa = P("Lampa wnętrza", 0.8, 0.8, 0.8, 0, h1 - 1, 0, OKNO)
	lampa.Material = Enum.Material.Neon
	swiatlo.Parent = lampa

	-- piętro: tynk i mur pruski, wysunięte o J
	local W, G = w + 2 * J, g + 2 * J
	local y1 = h1
	P("Piętro", W, h2, G, 0, y1 + h2 / 2, 0, kolTynku)
	P("Belka dolna", W + 0.5, B, G + 0.5, 0, y1 + B / 2, 0, DREWNO)
	P("Belka górna", W + 0.5, B, G + 0.5, 0, y1 + h2 - B / 2, 0, DREWNO)
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

	-- dach: dwie połacie z okapem; kalenica wzdłuż X, a przy „szczytem” — wzdłuż Z (szczyt od frontu)
	local Wr, Gr = W, G
	local rama = o * CFrame.new(0, y1 + h2, 0)
	if op.szczytem then
		Wr, Gr = G, W
		rama = rama * CFrame.Angles(0, math.pi / 2, 0)
	end
	local okap, okapX = 1.6, 1.3
	local tg = dachH / (Gr / 2)
	local kat = math.atan(tg)
	local bieg = Gr / 2 + okap
	local dl = bieg / math.cos(kat)
	local ciemny = kolDachu:Lerp(Color3.new(0, 0, 0), 0.28)
	for _, s in ipairs({ 1, -1 }) do
		cz(m, "Połać", Vector3.new(Wr + 2 * okapX, 0.9, dl),
			rama * CFrame.new(0, dachH - bieg * tg / 2 + 0.5, s * bieg / 2) * CFrame.Angles(s * kat, 0, 0), kolDachu)
		cz(m, "Okap", Vector3.new(Wr + 2 * okapX + 0.3, 0.5, 1),
			rama * CFrame.new(0, dachH - bieg * tg + 0.55, s * (bieg - 0.2)) * CFrame.Angles(s * kat, 0, 0), ciemny)
		-- szczyty z tynku (kliny): wysoka krawędź klina leży po jego stronie +Z
		for _, sx in ipairs({ -1, 1 }) do
			cz(m, "Szczyt", Vector3.new(T, dachH, Gr / 2),
				rama * CFrame.new(sx * (Wr / 2 - T / 2), dachH / 2, s * Gr / 4) * CFrame.Angles(0, if s == 1 then math.pi else 0, 0), kolTynku, nil, "WedgePart")
		end
	end
	cz(m, "Kalenica", Vector3.new(Wr + 2 * okapX + 0.4, 1, 1), rama * CFrame.new(0, dachH + 0.75, 0) * CFrame.Angles(math.pi / 4, 0, 0), ciemny)
	for _, sx in ipairs({ -1, 1 }) do -- mur pruski i okienko na szczytach
		local sc = rama * CFrame.new(sx * Wr / 2, 0, 0) * CFrame.Angles(0, sx * math.pi / 2, 0)
		cz(m, "Słupek szczytu", Vector3.new(0.6, dachH * 0.86, 0.3), sc * CFrame.new(0, dachH * 0.43, 0.12), DREWNO)
		cz(m, "Rygiel szczytu", Vector3.new(Gr * 0.52, 0.5, 0.3), sc * CFrame.new(0, dachH * 0.46, 0.12), DREWNO)
		okno(m, sc * CFrame.new(0, dachH * 0.24, 0), 2, 2)
	end
	if op.komin ~= false then
		local kx, kz = W * 0.26, -G * 0.18
		P("Komin", 2.4, dachH + 2.5, 2.4, kx, y1 + h2 + (dachH + 2.5) / 2 - 1, kz, KAMIEN_C)
		P("Komin czapa", 3, 0.6, 3, kx, y1 + h2 + dachH + 1.6, kz, KAMIEN)
	end
	if op.szyld then -- szyld na wysięgniku
		P("Wysięgnik", 0.4, 0.4, 4, -w / 2 + 3, y1 - 0.6, g / 2 + 2 + J, DREWNO)
		P("Szyld", 0.35, 2.6, 3, -w / 2 + 3, y1 - 2.3, g / 2 + 2.6 + J, DREWNO_J)
		P("Szyld znak", 0.45, 1.4, 1.6, -w / 2 + 3, y1 - 2.3, g / 2 + 2.6 + J, op.szyld)
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
	cz(m, "Pień", Vector3.new(1.5 * s, 6 * s, 1.5 * s), o * CFrame.new(0, 3 * s, 0), DREWNO_J)
	local warstwy = { { 8, 3.4, 6.5, 0 }, { 6.2, 3, 9.2, 45 }, { 4, 2.8, 11.6, 20 } }
	for i, w in ipairs(warstwy) do
		cz(m, "Korona", Vector3.new(w[1] * s, w[2] * s, w[1] * s),
			o * CFrame.new(0, w[3] * s, 0) * CFrame.Angles(math.rad(los:NextNumber(-6, 6)), math.rad(w[4]), math.rad(los:NextNumber(-6, 6))),
			kol:Lerp(Color3.new(1, 1, 0.6), (i - 1) * 0.12))
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
	cz(m, "Ramię", Vector3.new(2.2, 0.35, 0.35), o * CFrame.new(0.9, 8.8, 0), czarny)
	local l = cz(m, "Klosz", Vector3.new(1.2, 1.5, 1.2), o * CFrame.new(1.8, 7.8, 0), OKNO, Enum.Material.Neon)
	cz(m, "Daszek", Vector3.new(1.7, 0.35, 1.7), o * CFrame.new(1.8, 8.7, 0), czarny)
	local sw = Instance.new("PointLight")
	sw.Color, sw.Range, sw.Brightness = OKNO, 22, 1.4
	sw.Parent = l
	oddaj(m)
end

------------------------------------------------------------ plac
do
	local m = Instance.new("Model")
	m.Name = "Plac"
	local o = CFrame.new(X0, Y0, Z0)
	cz(m, "Trawa", Vector3.new(132, 0.4, 88), o * CFrame.new(0, 0.2, 0), C(120, 176, 92))
	cz(m, "Bruk", Vector3.new(116, 0.6, 70), o * CFrame.new(0, 0.3, 2), C(202, 186, 158))
	for _ = 1, 70 do -- pojedyncze płyty bruku
		local s = los:NextNumber(2.4, 5.2)
		local jasny = los:NextNumber() < 0.5
		local p = cz(m, "Płyta", Vector3.new(s, 0.12, s * los:NextNumber(0.7, 1.1)),
			o * CFrame.new(los:NextNumber(-54, 54), 0.62, los:NextNumber(-6, 34)) * CFrame.Angles(0, math.rad(los:NextNumber(0, 90)), 0),
			if jasny then C(216, 202, 176) else C(184, 168, 142))
		p.CanCollide = false
	end
	oddaj(m)
end

------------------------------------------------------------ domy (front do placu, czyli na +Z)
dom("Karczma", -36, -19, 30, 22, 9, 8, 11, C(198, 76, 62), C(242, 228, 198), { szyld = C(255, 196, 64) })
dom("Sklep magiczny", -3, -18, 20, 20, 9, 8, 14, C(128, 92, 196), C(234, 226, 242), { szczytem = true, szyld = C(120, 220, 255) })
dom("Zbrojownia", 25, -19, 22, 22, 9, 7, 10, C(60, 132, 172), C(240, 232, 208), { markiza = { C(214, 70, 62), C(246, 240, 226) } })
dom("Dom mieszczan", 50, -17, 15, 16, 8, 7, 11, C(232, 146, 60), C(238, 222, 200), { szczytem = true, komin = false })

------------------------------------------------------------ studnia
do
	local m = Instance.new("Model")
	m.Name = "Studnia"
	local o = CFrame.new(X0 + 4, YB, Z0 + 16)
	for i = 0, 7 do -- ośmiokątna cembrowina z klocków
		local a = i * math.pi / 4
		cz(m, "Cembrowina", Vector3.new(3.4, 3, 1.2), o * CFrame.Angles(0, a, 0) * CFrame.new(0, 1.5, 3.6), if i % 2 == 0 then KAMIEN else KAMIEN_C)
	end
	cz(m, "Woda", Vector3.new(0.4, 7, 7), o * CFrame.new(0, 2.1, 0) * CFrame.Angles(0, 0, math.pi / 2), C(86, 176, 226), nil, "Part").Shape = Enum.PartType.Cylinder
	for _, s in ipairs({ -1, 1 }) do
		cz(m, "Słup", Vector3.new(0.7, 8, 0.7), o * CFrame.new(s * 3.9, 4, 0), DREWNO)
		cz(m, "Daszek", Vector3.new(10, 0.6, 4.6), o * CFrame.new(0, 9, s * 1.7) * CFrame.Angles(s * math.rad(32), 0, 0), C(198, 76, 62))
	end
	cz(m, "Wałek", Vector3.new(7.6, 0.6, 0.6), o * CFrame.new(0, 6.4, 0), DREWNO_J)
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
	cz(m, "Lada", Vector3.new(9.6, 0.6, 3.4), o * CFrame.new(0, 3, 1.2), DREWNO_J)
	cz(m, "Skrzynia lady", Vector3.new(9, 2.6, 2.6), o * CFrame.new(0, 1.4, 1.2), DREWNO)
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
		cz(m, "Skrzynia", Vector3.new(s[3], s[3], s[3]), CFrame.new(X0 + s[1], YB + y, Z0 + s[2]) * CFrame.Angles(0, math.rad(s[4]), 0), C(176, 128, 78))
	end
	oddaj(m)
end
drzewo(-55, 10, 1.15, C(92, 160, 78))
drzewo(57, 20, 1, C(104, 172, 84))
drzewo(40, 30, 0.85, C(86, 150, 90))
drzewo(-48, 32, 0.9, C(110, 178, 88))
latarnia(-17, 3)
latarnia(13, 3)
latarnia(-40, 28)
latarnia(30, 28)

if rec then
	CHS:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
end
return string.format("%s: %d części w (%d; %.1f; %d). Kamera: z (%d; 38; %d) na (%d; 9; %d)", NAZWA, licznik, X0, Y0, Z0, X0, Z0 + 72, X0, Z0 - 8)
