--[[
	InterfejsWalki — interfejs cutscenki walki, tworzony w czasie działania w PlayerGui (nic w StarterGui).

	Wygląd w duchu kierunku artystycznego: gruby ciemny obrys, lekko przekrzywione ramki, żywe kolory,
	komiksowe napisy („−128”, „BLOK!”, „KRYTYK!”), ikony z pikseli w komiksowych ramkach.

	Kadr: scena jest komponowana w proporcjach 16:9. Gdy okno jest wyższe (np. kwadratowy podgląd Studio albo
	telefon trzymany pionowo), u góry i u dołu pojawiają się czarne pasy, a cały interfejs trzyma się środkowego
	prostokąta 16:9. Gdy okno jest szersze (telefon poziomo), kadr zajmuje cały ekran.

	Użycie: local ui = InterfejsWalki.nowy(playerGui, Ustawienia) … ui:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

local InterfejsWalki = {}
InterfejsWalki.__index = InterfejsWalki

local PROPORCJE = 16 / 9
local WYS_ODNIESIENIA = 720 -- grubości obrysów podane w pikselach dla kadru o wysokości 720
local NAGLOWKI = Enum.Font.LuckiestGuy -- ma polskie znaki (sprawdzone na zrzucie)
local KOMIKS = Enum.Font.Bangers -- j.w.

------------------------------------------------------------------ ikony z pikseli (8 × 8)
local IKONY = {
	helm = {
		paleta = { S = "#C9D2DE", s = "#8E99AB", R = "#E0413A", D = "#20242B", B = "#2F6FE0", O = "#8FF6FF" },
		mapa = { "..RRR...", ".SSSSSR.", "SSSSSSSR", "SDODDODS", "SSSsSSSS", "sSSsSSSs", ".sSSSSs.", "..BBBB.." },
	},
	kaptur = {
		paleta = { G = "#1F5A36", g = "#2A7A48", D = "#17121F", W = "#FFFFFF", C = "#8E2F2F" },
		mapa = { "...Gg...", "..GGGg..", ".GGGGGG.", "GGDDDDGG", "GDWDDWDG", "GGCCCCGG", ".GCCCCG.", "..gggg.." },
	},
	moneta = {
		paleta = { Y = "#FFD23F", O = "#E79A12", W = "#FFF3B0", D = "#8A5A0A" },
		mapa = { "..DDDD..", ".DYYYYD.", "DYWYYYOD", "DYWYOYOD", "DYYYOYOD", "DYYYYYOD", ".DOOOOD.", "..DDDD.." },
	},
	gwiazda = {
		paleta = { P = "#7B4DFF", p = "#B79BFF", D = "#2B1A66" },
		mapa = { "...DD...", "..DpPD..", "DDDpPDDD", "DpppPPPD", ".DpPPPD.", ".DpPPPD.", "DpPDDPPD", "DDD..DDD" },
	},
	jajko = {
		paleta = { W = "#FFFFFF", w = "#DCE6F2", C = "#49D6F2", D = "#3A4A66" },
		mapa = { "..DDDD..", ".DWWWWD.", "DWWCWWwD", "DWWWWWwD", "DWCWWCwD", "DWWWWwwD", ".DwwwwD.", "..DDDD.." },
	},
}

------------------------------------------------------------------ pomocnicze
local function gladko(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end

function InterfejsWalki:_nowy(klasa: string, wlasciwosci: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wlasciwosci do
		o[k] = v
	end
	o.Parent = rodzic
	self.utworzono += 1
	return o
end

function InterfejsWalki:_obrys(obiekt: GuiObject, px: number, kolor: Color3?): UIStroke
	local jestTekstem = obiekt:IsA("TextLabel") or obiekt:IsA("TextButton")
	local s = self:_nowy("UIStroke", {
		Color = kolor or self.K.tusz,
		Thickness = px,
		LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = if jestTekstem then Enum.ApplyStrokeMode.Contextual else Enum.ApplyStrokeMode.Border,
	}, obiekt)
	self.obrysy[s] = px
	s.Thickness = math.max(1, px * self.skalaObrysu)
	return s
end

function InterfejsWalki:_rog(obiekt: GuiObject, ulamek: number)
	return self:_nowy("UICorner", { CornerRadius = UDim.new(ulamek, 0) }, obiekt)
end

function InterfejsWalki:_ikona(rodzic: GuiObject, nazwa: string, margines: number?)
	local def = IKONY[nazwa]
	local m = margines or 0.12
	local pole = self:_nowy("Frame", {
		Name = "Ikona",
		BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(1 - 2 * m, 1 - 2 * m),
		ZIndex = rodzic.ZIndex + 1,
	}, rodzic)
	self:_nowy("UIAspectRatioConstraint", { AspectRatio = 1 }, pole)
	for y, wiersz in def.mapa do
		local x = 1
		while x <= 8 do
			local znak = string.sub(wiersz, x, x)
			local koniec = x
			while koniec < 8 and string.sub(wiersz, koniec + 1, koniec + 1) == znak do
				koniec += 1
			end
			if znak ~= "." then
				-- jeden prostokąt na ciąg pikseli tego samego koloru (mniej instancji); lekka zakładka zakrywa szczeliny
				self:_nowy("Frame", {
					BackgroundColor3 = Color3.fromHex(def.paleta[znak]),
					BorderSizePixel = 0,
					Position = UDim2.fromScale((x - 1) / 8, (y - 1) / 8),
					Size = UDim2.fromScale((koniec - x + 1) / 8 + 0.004, 1 / 8 + 0.004),
					ZIndex = pole.ZIndex,
				}, pole)
			end
			x = koniec + 1
		end
	end
	return pole
end

-- ramka komiksowa: cień, obrys, zaokrąglone rogi
function InterfejsWalki:_ramka(rodzic: Instance, wlasciwosci: { [string]: any }, obrysPx: number, rog: number, cien: boolean?)
	if cien then
		local c = self:_nowy("Frame", {
			Name = (wlasciwosci.Name or "Ramka") .. "Cien",
			BackgroundColor3 = self.K.tusz,
			BackgroundTransparency = 0.25,
			BorderSizePixel = 0,
			AnchorPoint = wlasciwosci.AnchorPoint or Vector2.zero,
			Position = (wlasciwosci.Position or UDim2.new()) + UDim2.fromScale(0.006, 0.014),
			Size = wlasciwosci.Size,
			Rotation = wlasciwosci.Rotation or 0,
			ZIndex = (wlasciwosci.ZIndex or 1) - 1,
		}, rodzic)
		self:_rog(c, rog)
	end
	local f = self:_nowy("Frame", wlasciwosci, rodzic)
	f.BorderSizePixel = 0
	self:_rog(f, rog)
	self:_obrys(f, obrysPx)
	return f
end

function InterfejsWalki:_tekst(rodzic: Instance, wlasciwosci: { [string]: any }, obrysPx: number?)
	local t = self:_nowy("TextLabel", wlasciwosci, rodzic)
	t.BackgroundTransparency = 1
	t.TextScaled = true
	if obrysPx and obrysPx > 0 then
		self:_obrys(t, obrysPx)
	end
	return t
end

------------------------------------------------------------------ budowa
function InterfejsWalki.nowy(playerGui: Instance, Ustawienia: any)
	local self = setmetatable({}, InterfejsWalki)
	self.U = Ustawienia
	self.K = Ustawienia.KOLORY
	self.utworzono = 0
	self.obrysy = {} :: { [UIStroke]: number }
	self.skalaObrysu = 1
	self.napisy = {} -- aktywne napisy unoszące się nad postaciami
	self.polaczenia = {} :: { RBXScriptConnection }
	self.paski = {}
	self.wspolczynnikPasa = 1 -- wysokość kadru / wysokość okna (do korekty kąta widzenia kamery)
	self.zniszczony = false

	local gui = self:_nowy("ScreenGui", {
		Name = "TestWalkiCutscenka",
		IgnoreGuiInset = true,
		ResetOnSpawn = false,
		DisplayOrder = 60, -- nad HUD-em gry, pod ekranem ładowania
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	}, nil)
	self.gui = gui

	self.pasGorny = self:_nowy("Frame", { Name = "PasGorny", BackgroundColor3 = Color3.new(0, 0, 0), BorderSizePixel = 0, ZIndex = 1 }, gui)
	self.pasDolny = self:_nowy("Frame", { Name = "PasDolny", BackgroundColor3 = Color3.new(0, 0, 0), BorderSizePixel = 0, ZIndex = 1 }, gui)
	self.warstwaNapisow = self:_nowy("Frame", { Name = "Napisy", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 5 }, gui)
	self.kadr = self:_nowy("Frame", { Name = "Kadr", BackgroundTransparency = 1, ZIndex = 10 }, gui)
	self.zaslona = self:_nowy("Frame", {
		Name = "Zaslona", BackgroundColor3 = Color3.new(0, 0, 0), BackgroundTransparency = 1, BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1), ZIndex = 100, Active = false,
	}, gui)

	self:_zbudujTabliczke("gracz")
	self:_zbudujTabliczke("wrog")
	self:_zbudujVS()
	self:_zbudujBaner()
	self:_zbudujPomin()
	self:_zbudujWynik()

	self.zegar = self:_tekst(self.kadr, {
		Name = "Zegar", Visible = false, AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0.02, 0.97),
		Size = UDim2.fromScale(0.3, 0.05), Font = Enum.Font.Code, TextColor3 = Color3.new(1, 1, 1),
		TextXAlignment = Enum.TextXAlignment.Left, Text = "", ZIndex = 50,
	}, 2)

	local kamera = workspace.CurrentCamera
	table.insert(self.polaczenia, kamera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
		self:_przelicz()
	end))
	self:_przelicz()
	gui.Parent = playerGui
	return self
end

-- prostokąt kadru 16:9 w oknie + czarne pasy + skala obrysów
function InterfejsWalki:_przelicz()
	local okno = workspace.CurrentCamera.ViewportSize
	local sz, wys = okno.X, okno.Y
	if sz <= 0 or wys <= 0 then
		return
	end
	local kadrWys = wys
	if sz / wys < PROPORCJE then
		kadrWys = sz / PROPORCJE
	end
	local pas = (wys - kadrWys) / 2
	self.wspolczynnikPasa = kadrWys / wys
	self.kadrPx = { x = 0, y = pas, sz = sz, wys = kadrWys }
	self.kadr.Position = UDim2.fromOffset(0, pas)
	self.kadr.Size = UDim2.fromOffset(sz, kadrWys)
	self.pasGorny.Position = UDim2.fromOffset(0, 0)
	self.pasGorny.Size = UDim2.fromOffset(sz, math.ceil(pas))
	self.pasDolny.Position = UDim2.fromOffset(0, math.floor(pas + kadrWys))
	self.pasDolny.Size = UDim2.fromOffset(sz, math.ceil(pas) + 1)
	self.pasGorny.Visible = pas > 0.5
	self.pasDolny.Visible = pas > 0.5
	-- bez pasów górną krawędź kadru zajmuje pasek Roblox (menu, czat) — zsuń tabliczki pod niego
	local zajete = 0
	if pas < 1 then
		local ok, wstawka = pcall(function()
			return GuiService.TopbarInset
		end)
		if ok and wstawka then
			zajete = wstawka.Height
		end
	end
	self.gornyMargines = math.max(0.045, (zajete + 4) / kadrWys)
	for strona, p in self.paski do
		p.tabliczka.Position = UDim2.fromScale(if strona == "gracz" then 0.025 else 0.975, self.gornyMargines)
	end
	if self.vs then
		self.vs.Position = UDim2.fromScale(0.5, self.gornyMargines + 0.07)
	end
	self.skalaObrysu = kadrWys / WYS_ODNIESIENIA
	for obrys, px in self.obrysy do
		if obrys.Parent then
			obrys.Thickness = math.max(1, px * self.skalaObrysu)
		else
			self.obrysy[obrys] = nil
		end
	end
end

function InterfejsWalki:_zbudujTabliczke(strona: string)
	local K = self.K
	local lewa = strona == "gracz"
	local ax = if lewa then 0 else 1
	local t = self:_nowy("Frame", {
		Name = if lewa then "TabliczkaGracza" else "TabliczkaWroga",
		BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(if lewa then 0.025 else 0.975, 0.045),
		Size = UDim2.fromScale(0.41, 0.135),
		Rotation = if lewa then -1.5 else 1.5,
		ZIndex = 10,
	}, self.kadr)

	local portret = self:_ramka(t, {
		Name = "Portret",
		AnchorPoint = Vector2.new(ax, 0.5),
		Position = UDim2.fromScale(ax, 0.5),
		Size = UDim2.fromScale(1.02, 1.02),
		SizeConstraint = Enum.SizeConstraint.RelativeYY,
		BackgroundColor3 = if lewa then K.niebieski else K.czerwony,
		Rotation = if lewa then -4 else 4,
		ZIndex = 14,
	}, 4, 0.16, false)
	self:_ikona(portret, if lewa then "helm" else "kaptur", 0.13)

	local nazwa = self:_tekst(t, {
		Name = "Nazwa",
		AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(if lewa then 0.2 else 0.8, -0.02),
		Size = UDim2.fromScale(0.78, 0.46),
		Font = NAGLOWKI,
		TextColor3 = K.bialy,
		TextXAlignment = if lewa then Enum.TextXAlignment.Left else Enum.TextXAlignment.Right,
		Text = "",
		ZIndex = 13,
	}, 3.5)

	local pasek = self:_ramka(t, {
		Name = "Pasek",
		AnchorPoint = Vector2.new(ax, 1),
		Position = UDim2.fromScale(if lewa then 0.14 else 0.86, 0.98),
		Size = UDim2.fromScale(0.86, 0.5),
		BackgroundColor3 = K.ciemny,
		ZIndex = 11,
	}, 4, 0.28, false)
	local wnetrze = self:_nowy("Frame", {
		Name = "Wnetrze", BackgroundTransparency = 1, Position = UDim2.fromScale(if lewa then 0.05 else 0.012, 0.12),
		Size = UDim2.fromScale(0.938, 0.76), ZIndex = 11,
	}, pasek)
	local duch = self:_nowy("Frame", {
		Name = "Duch", BackgroundColor3 = K.bialy, BorderSizePixel = 0, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(ax, 0), Size = UDim2.fromScale(1, 1), ZIndex = 11,
	}, wnetrze)
	self:_rog(duch, 0.3)
	local wypelnienie = self:_nowy("Frame", {
		Name = "Wypelnienie", BackgroundColor3 = K.bialy, BorderSizePixel = 0, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(ax, 0), Size = UDim2.fromScale(1, 1), ZIndex = 12,
	}, wnetrze)
	self:_rog(wypelnienie, 0.3)
	self:_nowy("UIGradient", {
		Rotation = 90,
		Color = if lewa
			then ColorSequence.new(Color3.fromHex("#6BFFE3"), Color3.fromHex("#17B8D9"))
			else ColorSequence.new(Color3.fromHex("#FF9AA5"), Color3.fromHex("#E8364F")),
	}, wypelnienie)
	local polysk = self:_nowy("Frame", {
		Name = "Polysk", BackgroundColor3 = K.bialy, BackgroundTransparency = 0.55, BorderSizePixel = 0,
		Position = UDim2.fromScale(0.02, 0.1), Size = UDim2.fromScale(0.96, 0.26), ZIndex = 12,
	}, wypelnienie)
	self:_rog(polysk, 0.5)
	local liczba = self:_tekst(pasek, {
		Name = "Liczba", Position = UDim2.fromScale(0.05, 0.08), Size = UDim2.fromScale(0.9, 0.84), Font = KOMIKS,
		TextColor3 = K.bialy, Text = "", ZIndex = 13,
	}, 2.5)

	self.paski[strona] = {
		tabliczka = t, nazwa = nazwa, wypelnienie = wypelnienie, duch = duch, liczba = liczba,
		maks = 1, cel = 1, pokazane = 1, duchPokazany = 1, duchCzeka = 0, wstrzas = 0,
		obrotBazowy = t.Rotation,
	}
end

function InterfejsWalki:_zbudujVS()
	local K = self.K
	local vs = self:_nowy("Frame", {
		Name = "VS", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.115),
		Size = UDim2.fromScale(0.1, 0.1), SizeConstraint = Enum.SizeConstraint.RelativeYY, ZIndex = 15,
	}, self.kadr)
	self:_ramka(vs, {
		Name = "Romb", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(0.78, 0.78),
		BackgroundColor3 = K.zolty, Rotation = 45, ZIndex = 15,
	}, 4, 0.14, false)
	self:_tekst(vs, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.9, 0.62),
		Font = NAGLOWKI, Text = "VS", TextColor3 = K.czerwony, Rotation = -6, ZIndex = 16,
	}, 3)
	self.vs = vs
end

function InterfejsWalki:_zbudujBaner()
	local K = self.K
	local baner = self:_nowy("Frame", {
		Name = "Baner", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.31),
		Size = UDim2.fromScale(0.74, 0.2), Rotation = -3, Visible = false, ZIndex = 30,
	}, self.kadr)
	self.banerSkala = self:_nowy("UIScale", { Scale = 1 }, baner)
	self.banerWstega = self:_ramka(baner, {
		Name = "Wstega", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.55), Size = UDim2.fromScale(1.3, 0.62),
		BackgroundColor3 = K.czerwony, ZIndex = 30,
	}, 5, 0.08, true)
	self.banerCien = self:_tekst(baner, {
		Name = "Cien", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.506, 0.535), Size = UDim2.fromScale(0.96, 0.9),
		Font = NAGLOWKI, Text = "", TextColor3 = K.tusz, ZIndex = 31,
	}, 7)
	self.banerNapis = self:_tekst(baner, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(0.96, 0.9),
		Font = NAGLOWKI, Text = "", TextColor3 = K.zolty, ZIndex = 32,
	}, 6)
	self.baner = baner
end

function InterfejsWalki:_przycisk(rodzic: Instance, nazwa: string, tekst: string, kolor: Color3, wlasciwosci: { [string]: any })
	local K = self.K
	local uchwyt = self:_nowy("Frame", {
		Name = nazwa, BackgroundTransparency = 1, AnchorPoint = wlasciwosci.AnchorPoint, Position = wlasciwosci.Position,
		Size = wlasciwosci.Size, Rotation = wlasciwosci.Rotation or 0, ZIndex = wlasciwosci.ZIndex,
	}, rodzic)
	local skala = self:_nowy("UIScale", { Scale = 1 }, uchwyt)
	local cien = self:_nowy("Frame", {
		Name = "Cien", BackgroundColor3 = K.tusz, BorderSizePixel = 0, Position = UDim2.fromScale(0.025, 0.12),
		Size = UDim2.fromScale(1, 1), ZIndex = wlasciwosci.ZIndex,
	}, uchwyt)
	self:_rog(cien, 0.26)
	local p = self:_nowy("TextButton", {
		Name = "Przycisk", AutoButtonColor = false, BackgroundColor3 = kolor, BorderSizePixel = 0, Size = UDim2.fromScale(1, 1),
		Text = "", ZIndex = wlasciwosci.ZIndex + 1,
	}, uchwyt)
	self:_rog(p, 0.26)
	self:_obrys(p, 4)
	self:_nowy("UIGradient", {
		Rotation = 90, Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.new(0.82, 0.82, 0.82)),
	}, p)
	self:_tekst(p, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.86, 0.66),
		Font = NAGLOWKI, Text = tekst, TextColor3 = K.bialy, ZIndex = wlasciwosci.ZIndex + 2,
	}, 3.5)
	local szybko = TweenInfo.new(0.1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	local nad = false
	local function do_(v: number)
		TweenService:Create(skala, szybko, { Scale = v }):Play()
	end
	table.insert(self.polaczenia, p.MouseEnter:Connect(function()
		nad = true
		do_(1.07)
	end))
	table.insert(self.polaczenia, p.MouseLeave:Connect(function()
		nad = false
		do_(1)
	end))
	table.insert(self.polaczenia, p.MouseButton1Down:Connect(function()
		do_(0.93)
	end))
	table.insert(self.polaczenia, p.MouseButton1Up:Connect(function()
		do_(if nad then 1.07 else 1)
	end))
	return uchwyt, p
end

function InterfejsWalki:_zbudujPomin()
	local uchwyt, p = self:_przycisk(self.kadr, "Pomin", "POMIŃ  »", self.K.zolty, {
		AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(0.975, 0.955), Size = UDim2.fromScale(0.2, 0.115),
		Rotation = -2, ZIndex = 40,
	})
	p.Napis.TextColor3 = self.K.tusz
	local obrysNapisu = p.Napis:FindFirstChildOfClass("UIStroke")
	if obrysNapisu then
		self.obrysy[obrysNapisu] = nil
		obrysNapisu:Destroy()
	end
	uchwyt.Visible = false
	self.pomin = uchwyt
	self.pominPrzycisk = p
end

function InterfejsWalki:_zbudujWynik()
	local K = self.K
	local uchwyt = self:_nowy("Frame", {
		Name = "Wynik", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.68, 0.6),
		Size = UDim2.fromScale(0.5, 0.6), Rotation = -1.2, Visible = false, ZIndex = 60,
	}, self.kadr)
	self.wynikSkala = self:_nowy("UIScale", { Scale = 1 }, uchwyt)
	local karta = self:_ramka(uchwyt, {
		Name = "Karta", Size = UDim2.fromScale(1, 1), BackgroundColor3 = K.krem, ZIndex = 61,
	}, 5, 0.06, true)
	-- wstęga z tytułem (wystaje poza kartę)
	local wstega = self:_ramka(uchwyt, {
		Name = "Wstega", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, -0.09), Size = UDim2.fromScale(1.08, 0.27),
		BackgroundColor3 = K.pomarancz, Rotation = 1.6, ZIndex = 63,
	}, 5, 0.14, true)
	local tytulCien = self:_tekst(wstega, {
		Name = "TytulCien", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.505, 0.56), Size = UDim2.fromScale(0.9, 0.78),
		Font = NAGLOWKI, Text = "", TextColor3 = K.tusz, ZIndex = 64,
	}, 6)
	local tytul = self:_tekst(wstega, {
		Name = "Tytul", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.9, 0.78),
		Font = NAGLOWKI, Text = "", TextColor3 = K.zolty, ZIndex = 65,
	}, 5)
	local podtytul = self:_tekst(karta, {
		Name = "Podtytul", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.215), Size = UDim2.fromScale(0.9, 0.09),
		Font = KOMIKS, Text = "", TextColor3 = K.ciemny, ZIndex = 62,
	}, 0)

	-- trzy kafle łupu
	local kafle = {}
	local opisy = { { "moneta", "ZŁOTA" }, { "gwiazda", "DOŚWIADCZENIA" }, { "jajko", "JAJKO" } }
	for i, opis in opisy do
		local kafel = self:_ramka(karta, {
			Name = "Kafel" .. i, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.2 + (i - 1) * 0.3, 0.335),
			Size = UDim2.fromScale(0.26, 0.36), BackgroundColor3 = K.bialy, Rotation = ({ -2.5, 1.5, -1.5 })[i], ZIndex = 62,
		}, 4, 0.1, true)
		local skala = self:_nowy("UIScale", { Scale = 1 }, kafel)
		local poleIkony = self:_nowy("Frame", {
			Name = "PoleIkony", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.05),
			Size = UDim2.fromScale(0.5, 0.42), ZIndex = 62,
		}, kafel)
		self:_ikona(poleIkony, opis[1], 0)
		local wartosc = self:_tekst(kafel, {
			Name = "Wartosc", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.47), Size = UDim2.fromScale(0.92, 0.31),
			Font = KOMIKS, Text = "", TextColor3 = K.tusz, ZIndex = 63,
		}, 0)
		local podpis = self:_tekst(kafel, {
			Name = "Podpis", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.78), Size = UDim2.fromScale(0.92, 0.17),
			Font = KOMIKS, Text = opis[2], TextColor3 = K.szary, ZIndex = 63,
		}, 0)
		kafle[i] = { ramka = kafel, skala = skala, wartosc = wartosc, podpis = podpis, ikona = poleIkony }
	end

	local jeszcze, jeszczePrzycisk = self:_przycisk(karta, "JeszczeRaz", "JESZCZE RAZ", K.zielony, {
		AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.29, 0.945), Size = UDim2.fromScale(0.4, 0.165), Rotation = -1.5, ZIndex = 66,
	})
	local zamknij, zamknijPrzycisk = self:_przycisk(karta, "Zamknij", "ZAMKNIJ", K.czerwony, {
		AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.74, 0.945), Size = UDim2.fromScale(0.32, 0.165), Rotation = 1.5, ZIndex = 66,
	})
	local stopka = self:_tekst(uchwyt, {
		Name = "Stopka", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 1.03), Size = UDim2.fromScale(0.96, 0.05),
		Font = Enum.Font.GothamBold, Text = "", TextColor3 = K.bialy, ZIndex = 62,
	}, 2)

	self.wynik = {
		uchwyt = uchwyt, wstega = wstega, tytul = tytul, tytulCien = tytulCien, podtytul = podtytul, kafle = kafle,
		jeszcze = jeszczePrzycisk, zamknij = zamknijPrzycisk, stopka = stopka, liczniki = {},
	}
end

------------------------------------------------------------------ sterowanie z odtwarzacza
function InterfejsWalki:ustawStrony(strony)
	for strona, dane in strony do
		local p = self.paski[strona]
		if p then
			p.nazwa.Text = string.upper(dane.nazwa) .. "  •  POZ. " .. tostring(dane.poziom)
			p.maks = math.max(1, dane.hp)
			p.hp = dane.hp
			p.cel, p.pokazane, p.duchPokazany, p.duchCzeka, p.wstrzas = 1, 1, 1, 0, 0
			p.liczba.Text = tostring(dane.hp) .. " / " .. tostring(dane.hp)
			p.wypelnienie.Size = UDim2.fromScale(1, 1)
			p.wypelnienie.Visible = true
			p.duch.Size = UDim2.fromScale(1, 1)
			p.tabliczka.Rotation = p.obrotBazowy
		end
	end
end

function InterfejsWalki:ustawZycie(strona: string, hp: number, natychmiast: boolean?)
	local p = self.paski[strona]
	if not p then
		return
	end
	p.hp = hp
	p.cel = math.clamp(hp / p.maks, 0, 1)
	p.liczba.Text = tostring(hp) .. " / " .. tostring(p.maks)
	if natychmiast then
		p.pokazane, p.duchPokazany, p.duchCzeka, p.wstrzas = p.cel, p.cel, 0, 0
	else
		p.duchCzeka = 0.28
		p.wstrzas = 1
	end
end

--[[
	Komiksowy napis nad postacią. styl: "zadane" (białe, trafienie we wroga), "otrzymane" (różowe, trafienie w gracza),
	"blok", "unik", "krytyk" (żółty wybuch) — pozycja śledzi punkt w świecie, więc napis zostaje przy postaci po cięciu kamery.
]]
local STYLE = {
	zadane = { kolor = "#FFFFFF", rozmiar = 0.125, zycie = 0.95 },
	otrzymane = { kolor = "#FF8A9A", rozmiar = 0.115, zycie = 0.95 },
	blok = { kolor = "#7CF3FF", rozmiar = 0.105, zycie = 1.0 },
	unik = { kolor = "#B8FF8A", rozmiar = 0.105, zycie = 1.0 },
	krytyk = { kolor = "#FFE14A", rozmiar = 0.12, zycie = 1.25, gwiazda = true },
	krytykLiczba = { kolor = "#FFE14A", rozmiar = 0.17, zycie = 1.25 },
	lup = { kolor = "#FFE14A", rozmiar = 0.085, zycie = 1.2 },
}

function InterfejsWalki:napis(punkt: Vector3, tekst: string, styl: string, przesuniecie: Vector2?, obrot: number?)
	local def = STYLE[styl] or STYLE.zadane
	local K = self.K
	local wys = def.rozmiar
	local pole = self:_nowy("Frame", {
		Name = "Napis_" .. styl, BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Size = UDim2.fromOffset(100, 100), Rotation = obrot or 0, ZIndex = 20,
	}, self.warstwaNapisow)
	local skala = self:_nowy("UIScale", { Scale = 0.2 }, pole)
	local gwiazda = {}
	if def.gwiazda then
		for i = 1, 2 do
			local g = self:_nowy("Frame", {
				Name = "Gwiazda" .. i, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
				Size = UDim2.fromScale(1.15, 1.15), SizeConstraint = Enum.SizeConstraint.RelativeYY,
				BackgroundColor3 = if i == 1 then K.pomarancz else K.czerwony, BorderSizePixel = 0, Rotation = (i - 1) * 45 + 12, ZIndex = 20,
			}, pole)
			self:_obrys(g, 4)
			gwiazda[i] = g
		end
	end
	local cien = self:_tekst(pole, {
		Name = "Cien", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 3, 0.5, 4), Size = UDim2.fromScale(1, 1),
		Font = KOMIKS, Text = tekst, TextColor3 = K.tusz, ZIndex = 21,
	}, 5)
	local napis = self:_tekst(pole, {
		Name = "Tekst", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(1, 1),
		Font = KOMIKS, Text = tekst, TextColor3 = Color3.fromHex(def.kolor), ZIndex = 22,
	}, 4.5)
	table.insert(self.napisy, {
		pole = pole, skala = skala, cien = cien, napis = napis, gwiazda = gwiazda, punkt = punkt, wiek = 0, zycie = def.zycie,
		wys = wys, szer = wys * (0.62 * math.max(3, utf8.len(tekst) or #tekst)), przesuniecie = przesuniecie or Vector2.zero,
	})
end

-- wysokosc: środek banera jako ułamek kadru (domyślnie 0,31 — nad postaciami w planie ogólnym)
function InterfejsWalki:pokazBaner(tekst: string, kolorNapisu: Color3, kolorWstegi: Color3, wysokosc: number?)
	self.baner.Position = UDim2.fromScale(0.5, wysokosc or 0.31)
	self.banerNapis.Text = tekst
	self.banerCien.Text = tekst
	self.banerNapis.TextColor3 = kolorNapisu
	self.banerWstega.BackgroundColor3 = kolorWstegi
	self.baner.Visible = true
	self.banerSkala.Scale = 0.3
	TweenService:Create(self.banerSkala, TweenInfo.new(0.28, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function InterfejsWalki:ukryjBaner(natychmiast: boolean?)
	if not self.baner.Visible then
		return
	end
	if natychmiast then
		self.baner.Visible = false
		return
	end
	local tw = TweenService:Create(self.banerSkala, TweenInfo.new(0.16, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.01 })
	tw.Completed:Once(function()
		if not self.zniszczony and self.banerSkala.Scale < 0.05 then
			self.baner.Visible = false
		end
	end)
	tw:Play()
end

function InterfejsWalki:pokazPomin(funkcja: () -> ())
	self.pomin.Visible = true
	if self.polaczeniePomin then
		self.polaczeniePomin:Disconnect()
	end
	self.polaczeniePomin = self.pominPrzycisk.Activated:Connect(funkcja)
end

function InterfejsWalki:ukryjPomin()
	self.pomin.Visible = false
end

function InterfejsWalki:pokazWynik(walka, naJeszczeRaz: () -> (), naZamknij: () -> ())
	local K = self.K
	local w = self.wynik
	local wygrana = walka.wynik == "wygrana"
	local tytul = if wygrana then "ZWYCIĘSTWO!" else "PORAŻKA!"
	w.tytul.Text = tytul
	w.tytulCien.Text = tytul
	w.tytul.TextColor3 = if wygrana then K.zolty else K.bialy
	w.wstega.BackgroundColor3 = if wygrana then K.pomarancz else K.fiolet
	local n = #walka.dziennik
	w.podtytul.Text = if wygrana
		then string.format("%s pokonał przeciwnika w %d wymianach", walka.strony.gracz.nazwa, n)
		else string.format("%s był dziś lepszy — spróbuj jeszcze raz", walka.strony.wrog.nazwa)
	local wartosci = { walka.lup.zloto, walka.lup.doswiadczenie, walka.lup.jajko }
	w.liczniki = {}
	for i, kafel in w.kafle do
		local v = wartosci[i] or 0
		local jest = v > 0
		kafel.ramka.BackgroundColor3 = if jest then K.bialy else Color3.fromHex("#D9D3C4")
		kafel.wartosc.TextColor3 = if jest then K.tusz else K.szary
		kafel.wartosc.Text = if jest then "+0" else "—"
		kafel.ikona.Visible = true
		for _, piksel in kafel.ikona:GetDescendants() do
			if piksel:IsA("Frame") and piksel.Name ~= "Ikona" then
				piksel.BackgroundTransparency = if jest then 0 else 0.6
			end
		end
		if jest then
			table.insert(w.liczniki, { etykieta = kafel.wartosc, cel = v, start = 0.25 + (i - 1) * 0.16, trwa = 0.45 })
		end
		kafel.skala.Scale = 0.01
		task.delay(0.12 + (i - 1) * 0.1, function()
			if not self.zniszczony then
				TweenService:Create(kafel.skala, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
			end
		end)
	end
	w.czasPokazania = 0
	w.blokadaPokazana = nil -- odliczanie na „JESZCZE RAZ” ustawi odtwarzacz w najbliższej klatce
	w.stopka.Text = string.format("dziennik policzył serwer  •  ziarno %s  •  %d wymian  •  %.1f s", tostring(walka.ziarno), n, walka.czas)
	if w.polJeszcze then
		w.polJeszcze:Disconnect()
	end
	if w.polZamknij then
		w.polZamknij:Disconnect()
	end
	w.polJeszcze = w.jeszcze.Activated:Connect(naJeszczeRaz)
	w.polZamknij = w.zamknij.Activated:Connect(naZamknij)
	-- panel staje z boku kadru, żeby nie zasłaniać zwycięzcy (po wygranej stoi on po lewej, po przegranej po prawej)
	w.uchwyt.Position = UDim2.fromScale(if wygrana then 0.68 else 0.32, 0.6)
	w.uchwyt.Visible = true
	self.wynikSkala.Scale = 0.55
	TweenService:Create(self.wynikSkala, TweenInfo.new(0.32, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

-- „JESZCZE RAZ” zablokowane, dopóki serwer nie uzna poprzedniej walki za skończoną (np. po „POMIŃ”): szary przycisk z odliczaniem
function InterfejsWalki:ustawBlokadeJeszczeRaz(zostalo: number)
	local w = self.wynik
	local sekundy = if zostalo > 0 then math.ceil(zostalo) else 0
	if w.blokadaPokazana == sekundy then
		return
	end
	w.blokadaPokazana = sekundy
	local napis = w.jeszcze:FindFirstChild("Napis")
	w.jeszcze.BackgroundColor3 = if sekundy > 0 then self.K.szary else self.K.zielony
	if napis then
		napis.Text = if sekundy > 0 then string.format("ZA %d s", sekundy) else "JESZCZE RAZ"
	end
	w.jeszcze:SetAttribute("Zablokowany", sekundy > 0)
end

function InterfejsWalki:ukryjWynik()
	self.wynik.uchwyt.Visible = false
	self.wynik.liczniki = {}
end

function InterfejsWalki:ustawZaslone(krycie: number)
	self.zaslona.BackgroundTransparency = 1 - math.clamp(krycie, 0, 1)
end

function InterfejsWalki:ustawZegar(tekst: string?)
	self.zegar.Visible = tekst ~= nil
	if tekst then
		self.zegar.Text = tekst
	end
end

function InterfejsWalki:pokazPaski(widoczne: boolean)
	for _, p in self.paski do
		p.tabliczka.Visible = widoczne
	end
	self.vs.Visible = widoczne
end

function InterfejsWalki:usunNapisy()
	for _, n in self.napisy do
		n.pole:Destroy()
	end
	table.clear(self.napisy)
end

-- co klatkę: paski życia, napisy nad postaciami, liczniki łupu
function InterfejsWalki:aktualizuj(dt: number, kamera: Camera)
	-- paski życia: wypełnienie dogania cel, biały „duch” czeka chwilę i dopiero wtedy się kurczy
	for _, p in self.paski do
		if p.pokazane ~= p.cel then
			p.pokazane += (p.cel - p.pokazane) * math.min(1, dt * 14)
			if math.abs(p.pokazane - p.cel) < 0.002 then
				p.pokazane = p.cel
			end
			p.wypelnienie.Size = UDim2.fromScale(math.max(p.pokazane, 0.001), 1)
			p.wypelnienie.Visible = p.pokazane > 0.004
		end
		if p.duchCzeka > 0 then
			p.duchCzeka -= dt
		elseif p.duchPokazany ~= p.cel then
			p.duchPokazany += (p.cel - p.duchPokazany) * math.min(1, dt * 7)
			if math.abs(p.duchPokazany - p.cel) < 0.002 then
				p.duchPokazany = p.cel
			end
		end
		p.duch.Size = UDim2.fromScale(math.max(p.duchPokazany, 0.001), 1)
		p.duch.Visible = p.duchPokazany > p.pokazane + 0.003
		if p.wstrzas > 0 then
			p.wstrzas = math.max(0, p.wstrzas - dt * 5)
			p.tabliczka.Rotation = p.obrotBazowy + math.sin(p.wstrzas * 40) * 2.2 * p.wstrzas
		end
	end

	-- napisy
	if #self.napisy > 0 then
		local kadr = self.kadrPx
		for i = #self.napisy, 1, -1 do
			local n = self.napisy[i]
			n.wiek += dt
			local u = n.wiek / n.zycie
			if u >= 1 then
				n.pole:Destroy()
				table.remove(self.napisy, i)
			else
				local ekran, widoczny = kamera:WorldToViewportPoint(n.punkt)
				local wysPx = n.wys * kadr.wys
				local szerPx = n.szer * kadr.wys
				local wznios = (0.02 + 0.075 * (1 - (1 - u) * (1 - u))) * kadr.wys
				-- najpierw ograniczamy punkt zaczepienia (głowę postaci), a dopiero potem dodajemy przesunięcie napisu —
				-- dzięki temu „BLOK!” i liczba obrażeń nie zlewają się w jedno, gdy głowa jest przy górnej krawędzi kadru
				local bazaY = math.clamp(ekran.Y - wznios, kadr.y + kadr.wys * 0.36, kadr.y + kadr.wys * 0.74)
				local x = ekran.X + n.przesuniecie.X * kadr.wys
				local y = bazaY + n.przesuniecie.Y * kadr.wys
				x = math.clamp(x, kadr.x + szerPx * 0.5 + 6, kadr.x + kadr.sz - szerPx * 0.5 - 6)
				n.pole.Visible = ekran.Z > 0
				n.pole.Position = UDim2.fromOffset(x, y)
				n.pole.Size = UDim2.fromOffset(szerPx, wysPx)
				-- wejście „z przytupem”: 0,2 → 1,3 → 1; zejście: zanik w ostatniej ćwiartce życia
				local s
				if n.wiek < 0.1 then
					s = 0.2 + 1.1 * (n.wiek / 0.1)
				elseif n.wiek < 0.2 then
					s = 1.3 - 0.3 * ((n.wiek - 0.1) / 0.1)
				else
					s = 1
				end
				n.skala.Scale = s
				local zanik = math.clamp((u - 0.74) / 0.26, 0, 1)
				if zanik > 0 or n.zanikal then
					n.zanikal = true
					n.napis.TextTransparency = zanik
					n.cien.TextTransparency = zanik
					for _, d in n.pole:GetDescendants() do
						if d:IsA("UIStroke") then
							d.Transparency = zanik
						elseif d:IsA("Frame") then
							d.BackgroundTransparency = zanik
						end
					end
				end
				for j, g in n.gwiazda do
					g.Rotation += dt * (if j == 1 then 40 else -55)
				end
			end
		end
	end

	-- liczniki łupu na panelu wyniku
	local w = self.wynik
	if w.uchwyt.Visible and #w.liczniki > 0 then
		w.czasPokazania += dt
		for i = #w.liczniki, 1, -1 do
			local l = w.liczniki[i]
			local u = (w.czasPokazania - l.start) / l.trwa
			if u >= 1 then
				l.etykieta.Text = "+" .. tostring(l.cel)
				table.remove(w.liczniki, i)
			elseif u > 0 then
				l.etykieta.Text = "+" .. tostring(math.floor(l.cel * gladko(u) + 0.5))
			end
		end
	end
end

function InterfejsWalki:zniszcz()
	if self.zniszczony then
		return
	end
	self.zniszczony = true
	for _, p in self.polaczenia do
		p:Disconnect()
	end
	for _, nazwa in { "polaczeniePomin" } do
		if self[nazwa] then
			self[nazwa]:Disconnect()
		end
	end
	if self.wynik.polJeszcze then
		self.wynik.polJeszcze:Disconnect()
	end
	if self.wynik.polZamknij then
		self.wynik.polZamknij:Disconnect()
	end
	self.gui:Destroy()
end

return InterfejsWalki
