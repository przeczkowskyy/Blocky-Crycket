--[[
	EfektyEwolucji — kopia EfektyZabawek (swiat/zabawki; ta z kolei z EfektyPetArena) dla Monster Evolution (ModuleScript
	w Workspace/EwolucjaGra/Moduly). Wszystko lokalne, tanie na telefonie: zakotwiczone części bez kolizji, dotyku
	i promieni; napisy rysowane na warstwie 2D (rzut ze świata — BillboardGui nie wychodzą w zrzutach z Play);
	jedna pętla krok(dt). Bez zmian w zachowaniu względem oryginału.

	Użycie (klient): local E = Efekty.nowe(folder, D)
		E:warstwa2D(screenGui)   E:slowo(poz, tekst, kolor, wielkosc)   E:liczba(poz, tekst, kolor)
		E:iskry(poz, kolor, ile, sila)   E:monety(poz, ile, cel)   E:plask(poz, kolor)   E:fala(poz, r)
		E:chmura(poz, r)   E:jezyk(od, do)   E:pierscien(poz, r, kolor)   E:pyl(poz, r, ile)   E:krok(dt)   E:wyczysc()
]]
local Efekty = {}
Efekty.__index = Efekty

local MAKS = 140 -- najwięcej naraz (części i napisy); nadmiar = najstarsze kończą się od razu

local function hex(h: string): Color3
	return Color3.fromHex(h)
end

local function czesc(rodzic: Instance, rozmiar: Vector3, kolor: Color3, material: Enum.Material?, ksztalt: Enum.PartType?): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanTouch = false
	p.CanQuery = false
	p.CastShadow = false
	p.Massless = true
	p.Size = rozmiar
	p.Color = kolor
	p.Material = material or Enum.Material.SmoothPlastic
	p.Shape = ksztalt or Enum.PartType.Block
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = rodzic
	return p
end

function Efekty.nowe(folder: Instance, D)
	local self = setmetatable({}, Efekty)
	self.folder = folder
	self.D = D
	self.lista = {} -- { t, czas, krok(f, dt) → bool?, koniec() }
	self.czcionka = Enum.Font[D.ui.czcionka] or Enum.Font.LuckiestGuy
	self.tusz = hex(D.ui.kolory.tusz)
	return self
end

function Efekty:dodaj(czas: number, krok, koniec)
	if #self.lista >= MAKS then
		local stary = table.remove(self.lista, 1)
		if stary.koniec then
			stary.koniec()
		end
	end
	table.insert(self.lista, { t = 0, czas = czas, krok = krok, koniec = koniec })
end

function Efekty:krok(dt: number)
	local i = 1
	while i <= #self.lista do
		local e = self.lista[i]
		e.t += dt
		local f = math.clamp(e.t / e.czas, 0, 1)
		local ok, dalej = pcall(e.krok, f, dt, e)
		if not ok or e.t >= e.czas or dalej == false then
			if e.koniec then
				pcall(e.koniec)
			end
			table.remove(self.lista, i)
		else
			i += 1
		end
	end
end

function Efekty:ile(): number
	return #self.lista
end

function Efekty:wyczysc()
	for _, e in self.lista do
		if e.koniec then
			pcall(e.koniec)
		end
	end
	self.lista = {}
end

-- warstwa napisów: ScreenGui z IgnoreGuiInset (punkty ekranu = punkty kamery); napisy rzutowane co klatkę ze świata.
-- Nie BillboardGui: w zrzutach z trybu Play BillboardGui u klienta się nie pokazują (sprawdzone 19.11.2026), a raporty
-- idą zrzutami. Bez warstwy (gracz poza BONK) napisów nie ma.
function Efekty:warstwa2D(w: Instance?)
	self.warstwa = w
end

local function rzut(poz: Vector3, maks: number): (boolean, number, number)
	local kam = workspace.CurrentCamera
	local v, naEkranie = kam:WorldToViewportPoint(poz)
	if not naEkranie or v.Z > maks then
		return false, 0, 0
	end
	return true, v.X, v.Y
end
Efekty.rzut = rzut

function Efekty:slowo(poz: Vector3, tekst: string, kolor: Color3, wielkosc: number?, czasZycia: number?, poKoncu: (() -> ())?)
	if not self.warstwa then
		if poKoncu then
			poKoncu()
		end
		return
	end
	local w = (wielkosc or 1) * (self.skala or 1)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromOffset(math.floor(230 * w), math.floor(90 * w))
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Text = tekst
	t.TextScaled = true
	t.Font = self.czcionka
	t.TextColor3 = kolor
	t.Rotation = math.random(-10, 10)
	t.Visible = false
	t.ZIndex = 5
	local obrys = Instance.new("UIStroke")
	obrys.Color = self.tusz
	obrys.Thickness = math.max(1.5, 3.5 * w)
	obrys.Parent = t
	local skala = Instance.new("UIScale")
	skala.Scale = 0.2
	skala.Parent = t
	t.Parent = self.warstwa
	local czas = czasZycia or (1.3 + 0.3 * (wielkosc or 1))
	self:dodaj(czas, function(f)
		local s = if f < 0.15 then 0.2 + (f / 0.15) * 1.0 elseif f < 0.28 then 1.2 - (f - 0.15) / 0.13 * 0.2 else 1
		skala.Scale = s
		local jest, x, y = rzut(poz + Vector3.new(0, f * 3, 0), 400)
		t.Visible = jest
		t.Position = UDim2.fromOffset(x, y)
		local zanik = math.clamp((f - 0.6) / 0.4, 0, 1)
		t.TextTransparency = zanik
		obrys.Transparency = zanik
	end, function()
		t:Destroy()
		if poKoncu then
			poKoncu()
		end
	end)
end
function Efekty:liczba(poz: Vector3, tekst: string, kolor: Color3)
	if not self.warstwa then
		return
	end
	local p0 = poz + Vector3.new(math.random() * 2 - 1, 0, math.random() * 2 - 1)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromOffset(110 * (self.skala or 1), 40 * (self.skala or 1))
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Text = tekst
	t.TextScaled = true
	t.Font = Enum.Font.FredokaOne
	t.TextColor3 = kolor
	t.Visible = false
	t.ZIndex = 4
	local obrys = Instance.new("UIStroke")
	obrys.Color = self.tusz
	obrys.Thickness = 2
	obrys.Parent = t
	t.Parent = self.warstwa
	self:dodaj(0.8, function(f)
		local jest, x, y = rzut(p0 + Vector3.new(0, 1 + f * 3.5, 0), 140)
		t.Visible = jest
		t.Position = UDim2.fromOffset(x, y)
		local zanik = math.clamp((f - 0.6) / 0.4, 0, 1)
		t.TextTransparency = zanik
		obrys.Transparency = zanik
	end, function()
		t:Destroy()
	end)
end

function Efekty:iskry(poz: Vector3, kolor: Color3, ile: number, sila: number?)
	local s = sila or 1
	for _ = 1, ile do
		local r = 0.25 + math.random() * 0.35
		local p = czesc(self.folder, Vector3.new(r, r, r), kolor, Enum.Material.Neon)
		p.Position = poz
		local v = Vector3.new(math.random() * 2 - 1, 0.6 + math.random(), math.random() * 2 - 1).Unit * (14 + math.random() * 14) * s
		local pp = poz
		local obrot = CFrame.Angles(math.random() * 6, math.random() * 6, 0)
		self:dodaj(0.45 + math.random() * 0.25, function(f, dt)
			v += Vector3.new(0, -60 * dt, 0)
			pp += v * dt
			p.CFrame = CFrame.new(pp) * obrot
			p.Transparency = f
		end, function()
			p:Destroy()
		end)
	end
end

-- monety: wylatują w górę i same lecą do `cel` (część gracza); poDolocie() po pierwszej, która doleci
function Efekty:monety(poz: Vector3, ile: number, cel: BasePart?, poDolocie: (() -> ())?)
	local zloto = hex(self.D.ui.kolory.zloto)
	local doleciala = false
	for i = 1, ile do
		local m = czesc(self.folder, Vector3.new(0.25, 1.1, 1.1), zloto, Enum.Material.Neon, Enum.PartType.Cylinder)
		local start = poz + Vector3.new(0, 1.5, 0)
		local kat = (i / ile) * math.pi * 2 + math.random()
		local wyrzut = start + Vector3.new(math.cos(kat) * 3.5, 4 + math.random() * 3, math.sin(kat) * 3.5)
		local czas = 0.75 + math.random() * 0.25 + i * 0.04
		self:dodaj(czas, function(f)
			local p
			if f < 0.4 then
				local g = f / 0.4
				p = start:Lerp(wyrzut, 1 - (1 - g) * (1 - g))
			else
				local g = (f - 0.4) / 0.6
				local koniec = if cel and cel.Parent then cel.Position else wyrzut
				p = wyrzut:Lerp(koniec, g * g)
			end
			m.CFrame = CFrame.new(p) * CFrame.Angles(0, f * 18, math.pi / 2)
		end, function()
			m:Destroy()
			if not doleciala and poDolocie then
				doleciala = true
				poDolocie()
			end
		end)
	end
end

function Efekty:plask(poz: Vector3, kolor: Color3)
	local krag = czesc(self.folder, Vector3.new(0.3, 1, 1), kolor, Enum.Material.SmoothPlastic, Enum.PartType.Cylinder)
	local cf = CFrame.new(poz + Vector3.new(0, 0.15, 0)) * CFrame.Angles(0, 0, math.pi / 2)
	krag.CFrame = cf
	self:dodaj(0.55, function(f)
		local r = 2 + f * 14
		krag.Size = Vector3.new(0.3, r, r)
		krag.CFrame = cf
		krag.Transparency = 0.2 + f * 0.8
	end, function()
		krag:Destroy()
	end)
	self:iskry(poz + Vector3.new(0, 0.5, 0), kolor, 12, 1.0)
end

function Efekty:zamach(cf: CFrame)
	local luk = czesc(self.folder, Vector3.new(0.3, 5.5, 0.6), Color3.fromRGB(255, 250, 225), Enum.Material.Neon)
	-- etap 3: łuk z góry w dół przed graczem (jak zamach ręką z pałką), opóźniony do chwili uderzenia
	self:dodaj(0.22, function(f)
		local g = math.clamp((f - 0.3) / 0.7, 0, 1)
		local a = 1.35 - g * 1.9
		luk.CFrame = cf * CFrame.new(0.9, 0.7, 0) * CFrame.Angles(a, 0, 0) * CFrame.new(0, 0, -3.2)
		luk.Transparency = if f < 0.3 then 1 else 0.25 + g * 0.75
	end, function()
		luk:Destroy()
	end)
end

-- tupot Strażnika (etap 3): pierścień fali rozchodzi się po ziemi do promienia r
function Efekty:fala(poz: Vector3, r: number)
	local nos = czesc(self.folder, Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1))
	nos.Transparency = 1
	nos.CFrame = CFrame.new(poz + Vector3.new(0, 0.35, 0))
	local k = Instance.new("CylinderHandleAdornment")
	k.Adornee = nos
	k.Color3 = Color3.fromRGB(255, 236, 190)
	k.Height = 0.5
	k.CFrame = CFrame.Angles(math.pi / 2, 0, 0)
	k.Parent = nos
	self:dodaj(0.6, function(f)
		local e = 1 - (1 - f) * (1 - f)
		k.Radius = 1.5 + e * r
		k.InnerRadius = math.max(0, k.Radius - 1.6)
		k.Transparency = 0.15 + f * 0.85
	end, function()
		nos:Destroy()
	end)
	self:iskry(poz + Vector3.new(0, 0.6, 0), Color3.fromRGB(200, 185, 150), 12, 1.2)
end

-- ślad za lecącym modelem: dwa zaczepy w korzeniu i Trail; zwraca Trail (znika z modelem)
function Efekty:smuga(korzen: BasePart, kolor: Color3, szerokosc: number): Trail
	local a0 = Instance.new("Attachment")
	a0.Position = Vector3.new(0, szerokosc * 0.5, 0)
	a0.Parent = korzen
	local a1 = Instance.new("Attachment")
	a1.Position = Vector3.new(0, szerokosc * 1.3, 0)
	a1.Parent = korzen
	local tr = Instance.new("Trail")
	tr.Attachment0 = a0
	tr.Attachment1 = a1
	tr.Lifetime = 0.35
	tr.Color = ColorSequence.new(Color3.new(1, 1, 1), kolor)
	tr.Transparency = NumberSequence.new(0.15, 1)
	tr.LightEmission = 0.6
	tr.FaceCamera = true
	tr.Parent = korzen
	return tr
end

-- Pet Arena: słup wody gejzeru (rośnie i opada)
function Efekty:gejzer(poz: Vector3)
	local s = czesc(self.folder, Vector3.new(4, 1, 4), Color3.fromRGB(150, 220, 255), Enum.Material.SmoothPlastic, Enum.PartType.Cylinder)
	s.Transparency = 0.25
	local cf = CFrame.new(poz) * CFrame.Angles(0, 0, math.pi / 2)
	self:dodaj(1.6, function(f)
		local h = if f < 0.25 then f / 0.25 * 34 else 34 * (1 - (f - 0.25) / 0.75) ^ 2
		h = math.max(0.5, h)
		local r = 3 + math.sin(f * 30) * 0.3
		s.Size = Vector3.new(h, r, r)
		s.CFrame = cf * CFrame.new(h / 2, 0, 0)
		s.Transparency = 0.25 + f * 0.6
	end, function()
		s:Destroy()
	end)
	self:iskry(poz + Vector3.new(0, 1, 0), Color3.fromRGB(190, 235, 255), 14, 1.4)
end

-- chmura zarodników: zielone kule rosną i gasną
function Efekty:chmura(poz: Vector3, r: number)
	for i = 1, 7 do
		local k = czesc(self.folder, Vector3.new(1, 1, 1), Color3.fromRGB(150, 220, 90), Enum.Material.SmoothPlastic, Enum.PartType.Ball)
		local a = i / 7 * math.pi * 2
		local p = poz + Vector3.new(math.cos(a) * r * 0.45, 1.5 + (i % 3) * 0.8, math.sin(a) * r * 0.45)
		self:dodaj(1.2, function(f)
			local s = r * (0.35 + f * 0.5)
			k.Size = Vector3.new(s, s, s)
			k.Position = p + Vector3.new(0, f * 2, 0)
			k.Transparency = 0.35 + f * 0.65
		end, function()
			k:Destroy()
		end)
	end
end

-- błysk lodu: niebieskie odpryski i kryształ
function Efekty:lod(poz: Vector3)
	self:iskry(poz + Vector3.new(0, 2, 0), Color3.fromRGB(170, 230, 255), 12, 0.9)
	local k = czesc(self.folder, Vector3.new(2, 4, 2), Color3.fromRGB(190, 240, 255), Enum.Material.Glass)
	k.Transparency = 0.3
	self:dodaj(0.5, function(f)
		k.CFrame = CFrame.new(poz + Vector3.new(0, 2, 0)) * CFrame.Angles(0, f * 3, 0.4)
		k.Size = Vector3.new(2 + f * 4, 4 + f * 4, 2 + f * 4)
		k.Transparency = 0.3 + f * 0.7
	end, function()
		k:Destroy()
	end)
end

-- płomień w stożku: pomarańczowe kule lecą w kierunku
function Efekty:plomien(poz: Vector3, kier: Vector3, zasieg: number, kat: number)
	for i = 1, 12 do
		local k = czesc(self.folder, Vector3.new(1, 1, 1), if i % 2 == 0 then Color3.fromRGB(255, 140, 40) else Color3.fromRGB(255, 220, 80),
			Enum.Material.Neon, Enum.PartType.Ball)
		local a = math.rad((math.random() * 2 - 1) * kat / 2)
		local d = Vector3.new(kier.X * math.cos(a) - kier.Z * math.sin(a), 0, kier.X * math.sin(a) + kier.Z * math.cos(a))
		local start = poz + Vector3.new(0, 2, 0)
		local opozn = i * 0.03
		self:dodaj(0.6 + opozn, function(f)
			local g = math.clamp((f * (0.6 + opozn) - opozn) / 0.6, 0, 1)
			k.Position = start + d * zasieg * g + Vector3.new(0, g * 1.5, 0)
			local s = 0.8 + g * 2.2
			k.Size = Vector3.new(s, s, s)
			k.Transparency = if g <= 0 then 1 else 0.1 + g * 0.9
		end, function()
			k:Destroy()
		end)
	end
end

-- język: różowa belka od → do, wysuwa się i chowa
function Efekty:jezyk(od: Vector3, do_: Vector3)
	local b = czesc(self.folder, Vector3.new(0.6, 0.6, 1), Color3.fromRGB(255, 110, 150), Enum.Material.SmoothPlastic)
	self:dodaj(0.45, function(f)
		local g = if f < 0.5 then f / 0.5 else 1 - (f - 0.5) / 0.5
		local cel = od:Lerp(do_, g)
		local dl = math.max(0.2, (cel - od).Magnitude)
		b.Size = Vector3.new(0.6, 0.6, dl)
		b.CFrame = CFrame.lookAt(od:Lerp(cel, 0.5), cel)
	end, function()
		b:Destroy()
	end)
end

-- pierścień na ziemi (cel rzutu, lądowanie skoku, zasięg)
function Efekty:pierscien(poz: Vector3, r: number, kolor: Color3, czas: number?)
	local nos = czesc(self.folder, Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1))
	nos.Transparency = 1
	nos.CFrame = CFrame.new(poz + Vector3.new(0, 0.3, 0))
	local k = Instance.new("CylinderHandleAdornment")
	k.Adornee = nos
	k.Color3 = kolor
	k.Height = 0.3
	k.Radius = r
	k.InnerRadius = math.max(0, r - 0.6)
	k.CFrame = CFrame.Angles(math.pi / 2, 0, 0)
	k.Parent = nos
	self:dodaj(czas or 0.8, function(f)
		k.Transparency = f
	end, function()
		nos:Destroy()
	end)
end
-- v2: krater (ciemny krąg na ziemi), cień spadającego (rośnie), pył (kłęby), trzy pierścienie fali, moneta z ziemi do peta
function Efekty:krater(poz: Vector3, r: number)
	local k = czesc(self.folder, Vector3.new(0.2, r * 2, r * 2), Color3.fromRGB(90, 70, 50), Enum.Material.SmoothPlastic, Enum.PartType.Cylinder)
	k.CFrame = CFrame.new(poz + Vector3.new(0, 0.12, 0)) * CFrame.Angles(0, 0, math.pi / 2)
	self:dodaj(2.2, function(f)
		k.Transparency = 0.25 + f * 0.75
	end, function()
		k:Destroy()
	end)
end

function Efekty:cien(poz: Vector3, r: number, czas: number)
	local k = czesc(self.folder, Vector3.new(0.15, 1, 1), Color3.fromRGB(20, 20, 30), Enum.Material.SmoothPlastic, Enum.PartType.Cylinder)
	local cf = CFrame.new(poz + Vector3.new(0, 0.15, 0)) * CFrame.Angles(0, 0, math.pi / 2)
	self:dodaj(czas, function(f)
		local s = 1 + f * (r * 2 - 1)
		k.Size = Vector3.new(0.15, s, s)
		k.CFrame = cf
		k.Transparency = 0.75 - f * 0.4
	end, function()
		k:Destroy()
	end)
end

function Efekty:pyl(poz: Vector3, r: number, ile: number?)
	for i = 1, (ile or 8) do
		local a = i / (ile or 8) * math.pi * 2 + math.random()
		local k = czesc(self.folder, Vector3.new(1, 1, 1), Color3.fromRGB(225, 200, 160), Enum.Material.SmoothPlastic, Enum.PartType.Ball)
		local start = poz + Vector3.new(math.cos(a) * r * 0.3, 0.8, math.sin(a) * r * 0.3)
		local cel = poz + Vector3.new(math.cos(a) * r, 2.5, math.sin(a) * r)
		self:dodaj(0.7 + math.random() * 0.3, function(f)
			local s = 1.5 + f * r * 0.35
			k.Size = Vector3.new(s, s, s)
			k.Position = start:Lerp(cel, 1 - (1 - f) * (1 - f))
			k.Transparency = 0.2 + f * 0.8
		end, function()
			k:Destroy()
		end)
	end
end

function Efekty:pierscienie(poz: Vector3, r: number)
	for i = 0, 2 do
		task.delay(i * 0.09, function()
			self:fala(poz, r * (1 - i * 0.18))
		end)
	end
	self:pyl(poz, r, 10)
	self:krater(poz, r * 0.35)
end

-- moneta: z ziemi obok peta wylatuje i wpada w peta (część `cel`)
function Efekty:monetaDo(od: Vector3, cel: BasePart)
	local zloto = hex(self.D.ui.kolory.zloto)
	local m = czesc(self.folder, Vector3.new(0.3, 1.4, 1.4), zloto, Enum.Material.Neon, Enum.PartType.Cylinder)
	local szczyt = od + Vector3.new(0, 5 + math.random() * 2, 0)
	self:dodaj(0.7, function(f)
		local p
		if f < 0.45 then
			p = od:Lerp(szczyt, 1 - (1 - f / 0.45) ^ 2)
		else
			local g = (f - 0.45) / 0.55
			p = szczyt:Lerp(if cel.Parent then cel.Position + Vector3.new(0, 2, 0) else szczyt, g * g)
		end
		m.CFrame = CFrame.new(p) * CFrame.Angles(0, f * 14, math.pi / 2)
	end, function()
		m:Destroy()
	end)
end

------------------------------------------------------------------ walka1: ogień (linia FIRE) i moc (linia POWER) — wbudowane części
-- strumień ognia z punktu (kotwica pyska) w kierunku kier: kule rosną i gasną; inferno — szerszy, różowo-pomarańczowy
function Efekty:strumien(od: Vector3, kier: Vector3, zasieg: number, kat: number, inferno: boolean?)
	for i = 1, (if inferno then 11 else 8) do
		local kol = if inferno then (if i % 3 == 0 then Color3.fromRGB(255, 77, 216) elseif i % 2 == 0 then Color3.fromRGB(255, 120, 40) else Color3.fromRGB(255, 220, 90))
			else (if i % 2 == 0 then Color3.fromRGB(255, 140, 40) else Color3.fromRGB(255, 225, 90))
		local k = czesc(self.folder, Vector3.new(1, 1, 1), kol, Enum.Material.Neon, Enum.PartType.Ball)
		local a = math.rad((math.random() * 2 - 1) * kat / 2)
		local d = Vector3.new(kier.X * math.cos(a) - kier.Z * math.sin(a), 0, kier.X * math.sin(a) + kier.Z * math.cos(a))
		local opozn = i * 0.025
		local y0 = od.Y
		self:dodaj(0.45 + opozn, function(f)
			local g = math.clamp((f * (0.45 + opozn) - opozn) / 0.45, 0, 1)
			local p = od + d * zasieg * g
			k.Position = Vector3.new(p.X, y0 + (1.2 - y0) * g * 0.6 + g * 1.2, p.Z)
			local s = 0.9 + g * (if inferno then 4.2 else 3.2)
			k.Size = Vector3.new(s, s, s)
			k.Transparency = if g <= 0 then 1 else 0.05 + g * 0.95
		end, function()
			k:Destroy()
		end)
	end
end

-- płonąca ziemia: żarzący się krąg i unoszące się płomyki przez czas
function Efekty:plama(poz: Vector3, r: number, czas: number, bezKregu: boolean?)
	-- bezKregu: krąg rysuje rekwizyt przypalenia (dane 3), tu tylko płomyki
	local k = czesc(self.folder, Vector3.new(0.18, r * 2, r * 2), Color3.fromRGB(255, 90, 30), Enum.Material.Neon, Enum.PartType.Cylinder)
	k.CFrame = CFrame.new(poz + Vector3.new(0, 0.16, 0)) * CFrame.Angles(0, 0, math.pi / 2)
	if bezKregu then
		k.Transparency = 1
	end
	local nast = 0
	self:dodaj(czas, function(f, dt)
		k.Transparency = if bezKregu then 1 else 0.35 + 0.25 * math.sin(f * czas * 9) * 0.5 + math.max(0, f - 0.8) * 3
		nast -= dt
		if nast <= 0 then
			nast = 0.18
			local a, d = math.random() * math.pi * 2, math.random() * r * 0.8
			local p = poz + Vector3.new(math.cos(a) * d, 0.4, math.sin(a) * d)
			local m = czesc(self.folder, Vector3.new(0.7, 0.7, 0.7), if math.random() < 0.5 then Color3.fromRGB(255, 200, 70) else Color3.fromRGB(255, 110, 40),
				Enum.Material.Neon, Enum.PartType.Ball)
			self:dodaj(0.6, function(g)
				m.Position = p + Vector3.new(0, g * 3, 0)
				local s = 0.7 * (1 - g) + 0.15
				m.Size = Vector3.new(s, s, s)
			end, function()
				m:Destroy()
			end)
		end
	end, function()
		k:Destroy()
	end)
end

-- zapowiedź (zamach): krąg zasięgu wypełnia się od środka przez czas — sygnał dla innych, gdzie uderzy
function Efekty:zapowiedz(poz: Vector3, r: number, kolor: Color3, czas: number)
	local nos = czesc(self.folder, Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1))
	nos.Transparency = 1
	nos.CFrame = CFrame.new(poz + Vector3.new(0, 0.25, 0))
	local brzeg = Instance.new("CylinderHandleAdornment")
	brzeg.Adornee = nos
	brzeg.Color3 = kolor
	brzeg.Height = 0.2
	brzeg.Radius = r
	brzeg.InnerRadius = math.max(0, r - 0.5)
	brzeg.CFrame = CFrame.Angles(math.pi / 2, 0, 0)
	brzeg.Transparency = 0.15
	brzeg.Parent = nos
	local srodek = Instance.new("CylinderHandleAdornment")
	srodek.Adornee = nos
	srodek.Color3 = kolor
	srodek.Height = 0.15
	srodek.Radius = 0.1
	srodek.CFrame = CFrame.Angles(math.pi / 2, 0, 0)
	srodek.Transparency = 0.55
	srodek.Parent = nos
	self:dodaj(czas, function(f)
		srodek.Radius = math.max(0.1, r * f)
	end, function()
		nos:Destroy()
	end)
end

-- kula ognia (EMBER SPIT): leci prosto, iskry za nią; zwraca uchwyt do zgaszenia (trafienie / koniec)
function Efekty:kulaOgnia(od: Vector3, kier: Vector3, v: number, czas: number)
	local k = czesc(self.folder, Vector3.new(1.6, 1.6, 1.6), Color3.fromRGB(255, 150, 40), Enum.Material.Neon, Enum.PartType.Ball)
	local j = czesc(self.folder, Vector3.new(0.9, 0.9, 0.9), Color3.fromRGB(255, 240, 150), Enum.Material.Neon, Enum.PartType.Ball)
	local u = { koniec = false, poz = od }
	local nast = 0
	self:dodaj(czas + 0.3, function(f, dt, e)
		if u.koniec then
			return false
		end
		u.poz = od + kier * v * e.t
		k.Position = u.poz
		j.Position = u.poz
		local s = 1.6 + math.sin(e.t * 30) * 0.2
		k.Size = Vector3.new(s, s, s)
		nast -= dt
		if nast <= 0 then
			nast = 0.05
			local m = czesc(self.folder, Vector3.new(0.6, 0.6, 0.6), Color3.fromRGB(255, 120, 30), Enum.Material.Neon, Enum.PartType.Ball)
			local p = u.poz
			self:dodaj(0.35, function(g)
				m.Position = p + Vector3.new(0, g * 0.8, 0)
				m.Transparency = g
			end, function()
				m:Destroy()
			end)
		end
	end, function()
		k:Destroy()
		j:Destroy()
	end)
	return u
end
return Efekty
