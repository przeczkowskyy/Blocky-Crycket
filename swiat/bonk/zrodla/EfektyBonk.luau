--[[
	EfektyBonk — efekty w świecie u klienta gry BONK (ModuleScript w Workspace/BonkGra/Moduly). Wszystko lokalne
	(nic nie wraca na serwer), tanie na telefonie: zakotwiczone części bez kolizji, dotyku i promieni, napisy jako
	BillboardGui o stałej wielkości na ekranie, jedna pętla krok(dt) dla wszystkich efektów.

	Użycie (klient): local E = Efekty.nowe(folder, D)
		E:slowo(poz, tekst, kolor, wielkosc)   -- komiksowy napis „BONK!” / „HOME RUN!” / „SPLAT!”
		E:liczba(poz, tekst, kolor)            -- liczba obrażeń, unosi się i gaśnie
		E:iskry(poz, kolor, ile, sila)         -- odpryski
		E:monety(poz, ile, cel)                -- monety wylatują i lecą do części `cel` (HumanoidRootPart)
		E:plask(poz, kolor)                    -- plaśnięcie: płaski krąg i kurz
		E:zamach(cf)                           -- łuk zamachu przed graczem
		E:smuga(model, kolor)                  -- ślad (Trail) za lecącym modelem
		E:krok(dt)   E:ile()   E:wyczysc()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Efekty = {}
Efekty.__index = Efekty

local MAKS = 90 -- najwięcej naraz (części i napisy); nadmiar = najstarsze kończą się od razu

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

-- kotwica napisu: niewidzialna część (BillboardGui potrzebuje rodzica w świecie)
function Efekty:kotwica(poz: Vector3): Part
	local a = czesc(self.folder, Vector3.new(0.2, 0.2, 0.2), Color3.new(1, 1, 1))
	a.Transparency = 1
	a.Position = poz
	return a
end

function Efekty:slowo(poz: Vector3, tekst: string, kolor: Color3, wielkosc: number?)
	local w = wielkosc or 1
	local a = self:kotwica(poz)
	local b = Instance.new("BillboardGui")
	b.AlwaysOnTop = true
	b.LightInfluence = 0
	b.Size = UDim2.fromOffset(math.floor(230 * w), math.floor(90 * w))
	b.MaxDistance = 400
	b.Parent = a
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 1)
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Position = UDim2.fromScale(0.5, 0.5)
	t.Text = tekst
	t.TextScaled = true
	t.Font = self.czcionka
	t.TextColor3 = kolor
	t.Rotation = math.random(-12, 12)
	t.Parent = b
	local obrys = Instance.new("UIStroke")
	obrys.Color = self.tusz
	obrys.Thickness = 3.5 * w
	obrys.Parent = t
	local skala = Instance.new("UIScale")
	skala.Scale = 0.2
	skala.Parent = t
	local czas = 0.9 + 0.25 * w
	self:dodaj(czas, function(f)
		local s = if f < 0.12 then 0.2 + (f / 0.12) * 1.0 elseif f < 0.22 then 1.2 - (f - 0.12) / 0.1 * 0.2 else 1
		skala.Scale = s
		b.StudsOffsetWorldSpace = Vector3.new(0, f * 3, 0)
		local zanik = math.clamp((f - 0.7) / 0.3, 0, 1)
		t.TextTransparency = zanik
		obrys.Transparency = zanik
	end, function()
		a:Destroy()
	end)
end

function Efekty:liczba(poz: Vector3, tekst: string, kolor: Color3)
	local a = self:kotwica(poz + Vector3.new(math.random() * 2 - 1, 0, math.random() * 2 - 1))
	local b = Instance.new("BillboardGui")
	b.AlwaysOnTop = true
	b.LightInfluence = 0
	b.Size = UDim2.fromOffset(110, 40)
	b.MaxDistance = 140
	b.Parent = a
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size = UDim2.fromScale(1, 1)
	t.Text = tekst
	t.TextScaled = true
	t.Font = Enum.Font.FredokaOne
	t.TextColor3 = kolor
	t.Parent = b
	local obrys = Instance.new("UIStroke")
	obrys.Color = self.tusz
	obrys.Thickness = 2
	obrys.Parent = t
	self:dodaj(0.8, function(f)
		b.StudsOffsetWorldSpace = Vector3.new(0, 1 + f * 3.5, 0)
		local zanik = math.clamp((f - 0.6) / 0.4, 0, 1)
		t.TextTransparency = zanik
		obrys.Transparency = zanik
	end, function()
		a:Destroy()
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
	local zloto = hex(self.D.ui.kolory.monety)
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
		local r = 2 + f * 9
		krag.Size = Vector3.new(0.3, r, r)
		krag.CFrame = cf
		krag.Transparency = 0.2 + f * 0.8
	end, function()
		krag:Destroy()
	end)
	self:iskry(poz + Vector3.new(0, 0.5, 0), Color3.fromRGB(200, 185, 150), 6, 0.6)
end

function Efekty:zamach(cf: CFrame)
	local luk = czesc(self.folder, Vector3.new(0.3, 5.5, 0.6), Color3.fromRGB(255, 250, 225), Enum.Material.Neon)
	self:dodaj(0.16, function(f)
		local a = -1.2 + f * 2.4
		luk.CFrame = cf * CFrame.Angles(0, a, 0) * CFrame.new(0, 0, -3) * CFrame.Angles(0, 0, math.rad(55))
		luk.Transparency = 0.3 + f * 0.7
	end, function()
		luk:Destroy()
	end)
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

return Efekty
