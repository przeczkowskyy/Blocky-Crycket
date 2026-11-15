--[[
	InterfejsWalki2 — interfejs walki v2, tworzony w czasie działania w PlayerGui (nic w StarterGui). Wzór: v1
	(swiat/test_walki_roblox/zrodla/InterfejsWalki.luau) — ten sam komiksowy styl, kadr 16:9 z czarnymi pasami,
	paski życia z „duchem”, komiksowe napisy nad postaciami, baner, „POMIŃ”, panel wyniku z odliczaniem.

	Nowe w v2:
		• tabliczki z nazwą, poziomem i rangą przeciwnika, portret z pikseli dla każdego aktora;
		• pod paskiem ikony aktywnych efektów z licznikiem tur (i zapasem tarczy);
		• licznik tury pod „VS”, wstęga z nazwą użytej umiejętności;
		• przyciski tempa ×1 / ×2 / ×4 (wybór gracza, D-068) obok „POMIŃ” — duże, czytelne na telefonie;
		• panel wyniku z łupem z dziennika: Złoto, doświadczenie, tokeny krainy, Gem, Shard Ewolucji.

	Użycie: local ui = InterfejsWalki2.nowy(playerGui, Ustawienia) … ui:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

local Interfejs = {}
Interfejs.__index = Interfejs

local PROPORCJE = 16 / 9
local WYS_ODNIESIENIA = 720
local kontener = script.Parent.Parent -- Workspace/TestWalki2

--[[ Emulacja ekranu telefonu (tylko testy): atrybut kontenera EmulacjaEkranu = Vector2 (rozmiar ekranu w punktach,
	np. 844 × 390 — telefon w poziomie). Interfejs układa się wtedy w prostokącie o tych proporcjach na środku okna
	(pomniejszonym, gdy okno Studio jest mniejsze), a kamera kadruje tak, jak na tym ekranie. Zrzut tego prostokąta
	pokazuje układ jak na telefonie; wielkość napisów w punktach = piksele ÷ skalaEmulacji. ]]
function Interfejs.ekran(): (number, number, number, number, number)
	local okno = workspace.CurrentCamera.ViewportSize
	local em = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(em) == "Vector2" and em.X > 0 and em.Y > 0 then
		local f = math.min(1, okno.X / em.X, okno.Y / em.Y)
		local sz, wys = em.X * f, em.Y * f
		return (okno.X - sz) / 2, (okno.Y - wys) / 2, sz, wys, f
	end
	return 0, 0, okno.X, okno.Y, 1
end
local NAGLOWKI = Enum.Font.LuckiestGuy
local KOMIKS = Enum.Font.Bangers

------------------------------------------------------------------ ikony z pikseli (8 × 8)
local IKONY = {
	wojownik = {
		paleta = { S = "#C9D2DE", s = "#8E99AB", R = "#E0413A", D = "#20242B", B = "#2F6FE0", O = "#8FF6FF" },
		mapa = { "..RRR...", ".SSSSSR.", "SSSSSSSR", "SDODDODS", "SSSsSSSS", "sSSsSSSs", ".sSSSSs.", "..BBBB.." },
	},
	zwiadowca = {
		paleta = { G = "#1F5A36", g = "#2A7A48", D = "#17121F", W = "#FFFFFF", C = "#F2C9A0" },
		mapa = { "...Gg...", "..GGGg..", ".GGGGGG.", "GGDDDDGG", "GDWDDWDG", "GGCCCCGG", ".GCCCCG.", "..gggg.." },
	},
	mag = {
		paleta = { P = "#7B4DFF", Y = "#FFD23F", O = "#FF9A2E", K = "#17121F", W = "#FFFFFF" },
		mapa = { "...PP...", "..PYPP..", ".PPPPPP.", "PPPPPPPP", ".OOOOOO.", ".OKOOKO.", ".OOWWOO.", "..OOOO.." },
	},
	-- Leśny Slime: kostka galarety z kiełkiem, duże oczy z błyskiem, rumieńce (swiat/postacie/lesny_slime.py)
	lesny_slime = {
		paleta = { G = "#7EDB57", g = "#5CB842", K = "#17121F", W = "#FAFFF0", R = "#FF8DA1", L = "#A6E34F" },
		mapa = { "...LL...", "GGGGGGGG", "GGGGGGGG", "GKWGGKWG", "GKKGGKKG", "RGGGGGGR", "GGGKKGGG", "gggggggg" },
	},
	cierniowy_wilk = {
		paleta = { D = "#4A4252", A = "#FFB52E", B = "#17121F", W = "#FFFFFF", G = "#4CB443" },
		mapa = { "D......D", "DD.GG.DD", "DDDDDDDD", "DADDDDAD", "DDDDDDDD", ".DDBBDD.", "..DWWD..", "...DD..." },
	},
	muchomornik = {
		paleta = { R = "#E5482F", W = "#FFFFFF", C = "#F2EBDC", K = "#17121F", G = "#4E9E3C" },
		mapa = { "..RRRR..", ".RWRRWR.", "RRRRRRRR", "RWRRRWRR", "..CCCC..", "..KCCK..", "..CGGC..", "...GG..." },
	},
	lesny_troll = {
		paleta = { g = "#4E9E3C", B = "#86704F", Y = "#FFE14A", K = "#17121F", T = "#FFFFFF" },
		mapa = { "..gggg..", ".BBBBBB.", "BBBBBBBB", "BBYBBYBB", "BBBBBBBB", "BTBBBBTB", "BBKKKKBB", ".BBBBBB." },
	},
	-- Strażnik Gaju: kamienna głowa, korona z gałęzi, zielone oczy, broda z korzonków (swiat/postacie/straznik_gaju.py)
	straznik_lasu = {
		paleta = { M = "#7DAE3C", B = "#8E5B32", S = "#858074", s = "#57524C", G = "#36EE4E", K = "#2B2428" },
		mapa = { "M.B..B.M", ".BMBBMB.", "SSSSSSSS", "SsGSSGsS", "SSSSSSSS", "SSsKKsSS", "SBSBBSBS", ".B.BB.B." },
	},
	-- efekty
	trucizna = {
		paleta = { G = "#8BEA4E", g = "#3E8C2A", L = "#E8FFD0" },
		mapa = { "...GG...", "..GGGG..", ".GGLGGG.", ".GLGGGG.", "GGGGGGGG", "GGGGGGgG", ".GGGGgG.", "..gggg.." },
	},
	ogien = {
		paleta = { R = "#E8364F", O = "#FF8A1F", Y = "#FFD23F", W = "#FFF3B0" },
		mapa = { "...R....", "..RR..R.", "..ROR.RR", ".RROORRR", "RROYYORR", "ROYYYYOR", "ROYWWYOR", ".RRRRRR." },
	},
	kropla = {
		paleta = { R = "#FF2E45", r = "#9E1020", L = "#FFC0C8" },
		mapa = { "...RR...", "..RRRR..", ".RRLRRR.", ".RLRRRR.", "RRRRRRRR", "RRRRRRrR", ".RRRRrR.", "..rrrr.." },
	},
	gwiazdki = {
		paleta = { Y = "#FFE14A", B = "#7FD8FF", W = "#FFFFFF" },
		mapa = { "...Y....", "..YYY...", "YYYYYYY.", ".YYWYY..", ".YY.YY..", "Y.....B.", "....BBB.", ".....B.." },
	},
	pancerz = {
		paleta = { S = "#B9BEC4", s = "#8D949C", K = "#17121F", O = "#D9A066" },
		mapa = { "SSSSSSSS", "SSSKSSSs", "SSSSKSSs", "SSSKSSSs", ".SSSKSs.", ".SSKSSs.", "..SSSs..", "...OO..." },
	},
	kamien = {
		paleta = { S = "#A9AFB6", s = "#646B73", W = "#E3E7EC" },
		mapa = { "SSSSSSSS", "SWWSSSSs", "SWSSSSSs", "SSSSSSSs", ".SSSSSs.", ".SSSSss.", "..SSss..", "...ss..." },
	},
	banka = {
		paleta = { B = "#6FE3FF", b = "#27B6F2", W = "#FFFFFF" },
		mapa = { "..bbbb..", ".bBBBBb.", "bBWWBBBb", "bBWBBBBb", "bBBBBBBb", "bBBBBBBb", ".bBBBBb.", "..bbbb.." },
	},
	oko = {
		paleta = { Y = "#FFD23F", y = "#E79A12", K = "#17121F", W = "#FFFFFF" },
		mapa = { "........", "..YYYY..", ".YWWWWY.", "YWWKKWWY", "YWKKKKWY", ".YWWWWY.", "..YYYY..", "........" },
	},
	-- łup
	moneta = {
		paleta = { Y = "#FFD23F", O = "#E79A12", W = "#FFF3B0", D = "#8A5A0A" },
		mapa = { "..DDDD..", ".DYYYYD.", "DYWYYYOD", "DYWYOYOD", "DYYYOYOD", "DYYYYYOD", ".DOOOOD.", "..DDDD.." },
	},
	gwiazda = {
		paleta = { P = "#7B4DFF", p = "#B79BFF", D = "#2B1A66" },
		mapa = { "...DD...", "..DpPD..", "DDDpPDDD", "DpppPPPD", ".DpPPPD.", ".DpPPPD.", "DpPDDPPD", "DDD..DDD" },
	},
	zeton = {
		paleta = { G = "#52D273", D = "#1F5A36", L = "#A8F07A" },
		mapa = { "..DDDD..", ".DGGGGD.", "DGGLLGGD", "DGLLLLGD", "DGGLLGGD", "DGGGLGGD", ".DGGGGD.", "..DDDD.." },
	},
	gem = {
		paleta = { P = "#C04DFF", p = "#F0C8FF", D = "#5A1A8A" },
		mapa = { "........", ".DDDDDD.", "DppPPPPD", "DpPPPPPD", ".DPPPPD.", "..DPPD..", "...DD...", "........" },
	},
	shard = {
		paleta = { C = "#49D6F2", c = "#E8FBFF", D = "#1A5A7A" },
		mapa = { "...DD...", "..DcCD..", "..DcCD..", ".DcCCCD.", ".DcCCCD.", ".DCCCCD.", "..DCCD..", "...DD..." },
	},
}
Interfejs.IKONY = IKONY

------------------------------------------------------------------ pomocnicze
local function gladko(x: number): number
	x = math.clamp(x, 0, 1)
	return x * x * (3 - 2 * x)
end

function Interfejs:_nowy(klasa: string, wlasciwosci: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wlasciwosci do
		o[k] = v
	end
	o.Parent = rodzic
	self.utworzono += 1
	return o
end

function Interfejs:_obrys(obiekt: GuiObject, px: number, kolor: Color3?): UIStroke
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

function Interfejs:_rog(obiekt: GuiObject, ulamek: number)
	return self:_nowy("UICorner", { CornerRadius = UDim.new(ulamek, 0) }, obiekt)
end

function Interfejs:_ikona(rodzic: GuiObject, nazwa: string, margines: number?)
	local def = IKONY[nazwa] or IKONY.oko
	local m = margines or 0.12
	local pole = self:_nowy("Frame", {
		Name = "Ikona", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromScale(1 - 2 * m, 1 - 2 * m), ZIndex = rodzic.ZIndex + 1,
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
				self:_nowy("Frame", {
					BackgroundColor3 = Color3.fromHex(def.paleta[znak] or "#FF00FF"), BorderSizePixel = 0,
					Position = UDim2.fromScale((x - 1) / 8, (y - 1) / 8), Size = UDim2.fromScale((koniec - x + 1) / 8 + 0.004, 1 / 8 + 0.004),
					ZIndex = pole.ZIndex,
				}, pole)
			end
			x = koniec + 1
		end
	end
	return pole
end

function Interfejs:_ramka(rodzic: Instance, wlasciwosci: { [string]: any }, obrysPx: number, rog: number, cien: boolean?)
	if cien then
		local c = self:_nowy("Frame", {
			Name = (wlasciwosci.Name or "Ramka") .. "Cien", BackgroundColor3 = self.K.tusz, BackgroundTransparency = 0.25,
			BorderSizePixel = 0, AnchorPoint = wlasciwosci.AnchorPoint or Vector2.zero,
			Position = (wlasciwosci.Position or UDim2.new()) + UDim2.fromScale(0.006, 0.014), Size = wlasciwosci.Size,
			Rotation = wlasciwosci.Rotation or 0, ZIndex = (wlasciwosci.ZIndex or 1) - 1,
		}, rodzic)
		self:_rog(c, rog)
	end
	local f = self:_nowy("Frame", wlasciwosci, rodzic)
	f.BorderSizePixel = 0
	self:_rog(f, rog)
	self:_obrys(f, obrysPx)
	return f
end

function Interfejs:_tekst(rodzic: Instance, wlasciwosci: { [string]: any }, obrysPx: number?)
	local t = self:_nowy("TextLabel", wlasciwosci, rodzic)
	t.BackgroundTransparency = 1
	t.TextScaled = true
	if obrysPx and obrysPx > 0 then
		self:_obrys(t, obrysPx)
	end
	return t
end

------------------------------------------------------------------ budowa
function Interfejs.nowy(playerGui: Instance, Ustawienia: any)
	local self = setmetatable({}, Interfejs)
	self.U = Ustawienia
	self.K = Ustawienia.KOLORY
	self.utworzono = 0
	self.obrysy = {} :: { [UIStroke]: number }
	self.skalaObrysu = 1
	self.napisy = {}
	self.polaczenia = {} :: { RBXScriptConnection }
	self.paski = {}
	self.wspolczynnikPasa = 1
	self.zniszczony = false

	local gui = self:_nowy("ScreenGui", {
		Name = "TestWalki2Cutscenka", IgnoreGuiInset = true, ResetOnSpawn = false, DisplayOrder = 101, -- nad ekranem ładowania gry (100), który zostaje włączony i łapie kliknięcia
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
	self:_zbudujUmiejetnosc()
	self:_zbudujPomin()
	self:_zbudujTempo()
	self:_zbudujWynik()

	self.zegar = self:_tekst(self.kadr, {
		Name = "Zegar", Visible = false, AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0.02, 0.83),
		Size = UDim2.fromScale(0.5, 0.04), Font = Enum.Font.Code, TextColor3 = Color3.new(1, 1, 1),
		TextXAlignment = Enum.TextXAlignment.Left, Text = "", ZIndex = 50,
	}, 2)

	local kamera = workspace.CurrentCamera
	table.insert(self.polaczenia, kamera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
		self:_przelicz()
	end))
	table.insert(self.polaczenia, kontener:GetAttributeChangedSignal("EmulacjaEkranu"):Connect(function()
		self:_przelicz()
	end))
	self:_przelicz()
	gui.Parent = playerGui
	return self
end

function Interfejs:_przelicz()
	local oknoWys = workspace.CurrentCamera.ViewportSize.Y
	local ox, oy, sz, wys, f = Interfejs.ekran()
	if sz <= 0 or wys <= 0 then
		return
	end
	self.skalaEmulacji = f
	local kadrWys = wys
	if sz / wys < PROPORCJE then
		kadrWys = sz / PROPORCJE
	end
	local pas = (wys - kadrWys) / 2
	-- pionowy kąt kamery dotyczy całego okna: kadr (na środku okna) ma mieć kąt ujęcia
	self.wspolczynnikPasa = kadrWys / oknoWys
	self.kadrPx = { x = ox, y = oy + pas, sz = sz, wys = kadrWys }
	self.kadr.Position = UDim2.fromOffset(ox, oy + pas)
	self.kadr.Size = UDim2.fromOffset(sz, kadrWys)
	self.pasGorny.Position = UDim2.fromOffset(ox, oy)
	self.pasGorny.Size = UDim2.fromOffset(sz, math.ceil(pas))
	self.pasDolny.Position = UDim2.fromOffset(ox, oy + math.floor(pas + kadrWys))
	self.pasDolny.Size = UDim2.fromOffset(sz, math.ceil(pas) + 1)
	self.pasGorny.Visible = pas > 0.5
	self.pasDolny.Visible = pas > 0.5
	local zajete = 0
	if pas < 1 then
		local ok, wstawka = pcall(function()
			return GuiService.TopbarInset
		end)
		if ok and wstawka then
			zajete = wstawka.Height * f
		end
	end
	self.gornyMargines = math.max(0.045, (zajete + 4) / kadrWys)
	for strona, p in self.paski do
		p.tabliczka.Position = UDim2.fromScale(if strona == "gracz" then 0.025 else 0.975, self.gornyMargines)
	end
	if self.vs then
		self.vs.Position = UDim2.fromScale(0.5, self.gornyMargines + 0.065)
		self.tura.Position = UDim2.fromScale(0.5, self.gornyMargines + 0.12)
	end
	-- wstęga z nazwą umiejętności: pod licznikiem tury; gdy pasek Roblox u góry (telefon, okno bez pasów) spycha
	-- tabliczki w dół, wstęga idzie na dół ekranu między przyciski tempa a POMIŃ — inaczej zasłaniała paski życia
	if self.umiejetnosc then
		self.wstegaNaDole = self.gornyMargines > 0.08
		self.umiejetnosc.Position = UDim2.fromScale(0.5, if self.wstegaNaDole then 0.905 else 0.272)
		self.umiejetnosc.Size = UDim2.fromScale(if self.wstegaNaDole then 0.34 else 0.44, if self.wstegaNaDole then 0.08 else 0.07)
	end
	-- napisy nad postaciami nie wchodzą na tabliczki ani na wstęgę
	self.gornaGranicaNapisow = math.max(0.33, self.gornyMargines + 0.25)
	self.skalaObrysu = kadrWys / WYS_ODNIESIENIA
	for obrys, px in self.obrysy do
		if obrys.Parent then
			obrys.Thickness = math.max(1, px * self.skalaObrysu)
		else
			self.obrysy[obrys] = nil
		end
	end
end

local RANGI = {
	zwykly = { "ZWYKŁY", "#8D93A6" },
	rzadki = { "RZADKI", "#2F6FE0" },
	straznik = { "STRAŻNIK", "#E8364F" },
	gracz = { "GRACZ", "#52D273" },
}

function Interfejs:_zbudujTabliczke(strona: string)
	local K = self.K
	local lewa = strona == "gracz"
	local ax = if lewa then 0 else 1
	local t = self:_nowy("Frame", {
		Name = if lewa then "TabliczkaGracza" else "TabliczkaWroga", BackgroundTransparency = 1,
		AnchorPoint = Vector2.new(ax, 0), Position = UDim2.fromScale(if lewa then 0.025 else 0.975, 0.045),
		Size = UDim2.fromScale(0.4, 0.13), Rotation = if lewa then -1.5 else 1.5, ZIndex = 10,
	}, self.kadr)
	local portret = self:_ramka(t, {
		Name = "Portret", AnchorPoint = Vector2.new(ax, 0.5), Position = UDim2.fromScale(ax, 0.5), Size = UDim2.fromScale(1.02, 1.02),
		SizeConstraint = Enum.SizeConstraint.RelativeYY, BackgroundColor3 = if lewa then K.niebieski else K.czerwony,
		Rotation = if lewa then -4 else 4, ZIndex = 14,
	}, 4, 0.16, false)
	local nazwa = self:_tekst(t, {
		Name = "Nazwa", AnchorPoint = Vector2.new(ax, 0), Position = UDim2.fromScale(if lewa then 0.2 else 0.8, -0.02),
		Size = UDim2.fromScale(0.78, 0.44), Font = NAGLOWKI, TextColor3 = K.bialy,
		TextXAlignment = if lewa then Enum.TextXAlignment.Left else Enum.TextXAlignment.Right, Text = "", ZIndex = 13,
	}, 3.5)
	local ranga = self:_ramka(t, {
		-- pod paskiem, od strony środka ekranu (ikony efektów rosną od zewnętrznej krawędzi)
		Name = "Ranga", AnchorPoint = Vector2.new(1 - ax, 0), Position = UDim2.fromScale(if lewa then 0.86 else 0.14, 1.1),
		Size = UDim2.fromScale(0.2, 0.36), BackgroundColor3 = K.szary, Rotation = if lewa then 3 else -3, ZIndex = 13,
	}, 3, 0.2, false)
	local rangaNapis = self:_tekst(ranga, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.86, 0.72),
		Font = KOMIKS, TextColor3 = K.bialy, Text = "", ZIndex = 14,
	}, 2)
	local pasek = self:_ramka(t, {
		Name = "Pasek", AnchorPoint = Vector2.new(ax, 1), Position = UDim2.fromScale(if lewa then 0.14 else 0.86, 0.98),
		Size = UDim2.fromScale(0.86, 0.5), BackgroundColor3 = K.ciemny, ZIndex = 11,
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
		Color = if lewa then ColorSequence.new(Color3.fromHex("#6BFFE3"), Color3.fromHex("#17B8D9"))
			else ColorSequence.new(Color3.fromHex("#FF9AA5"), Color3.fromHex("#E8364F")),
	}, wypelnienie)
	local polysk = self:_nowy("Frame", {
		Name = "Polysk", BackgroundColor3 = K.bialy, BackgroundTransparency = 0.55, BorderSizePixel = 0,
		Position = UDim2.fromScale(0.02, 0.1), Size = UDim2.fromScale(0.96, 0.26), ZIndex = 12,
	}, wypelnienie)
	self:_rog(polysk, 0.5)
	-- zapas tarczy (kamienna skóra, bariera): jasnoniebieska nakładka na pasku
	local tarcza = self:_nowy("Frame", {
		Name = "Tarcza", BackgroundColor3 = Color3.fromHex("#9FE8FF"), BackgroundTransparency = 0.15, BorderSizePixel = 0,
		AnchorPoint = Vector2.new(ax, 0), Position = UDim2.fromScale(ax, 0.55), Size = UDim2.fromScale(0, 0.45), ZIndex = 13, Visible = false,
	}, wnetrze)
	self:_rog(tarcza, 0.3)
	local liczba = self:_tekst(pasek, {
		Name = "Liczba", Position = UDim2.fromScale(0.05, 0.08), Size = UDim2.fromScale(0.9, 0.84), Font = KOMIKS,
		TextColor3 = K.bialy, Text = "", ZIndex = 14,
	}, 2.5)
	-- rząd ikon efektów pod tabliczką
	local efekty = self:_nowy("Frame", {
		Name = "Efekty", BackgroundTransparency = 1, AnchorPoint = Vector2.new(ax, 0),
		Position = UDim2.fromScale(if lewa then 0.14 else 0.86, 1.08), Size = UDim2.fromScale(0.86, 0.58), ZIndex = 12,
	}, t)
	self:_nowy("UIListLayout", {
		FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = if lewa then Enum.HorizontalAlignment.Left else Enum.HorizontalAlignment.Right,
		Padding = UDim.new(0.015, 0), SortOrder = Enum.SortOrder.LayoutOrder,
	}, efekty)

	self.paski[strona] = {
		tabliczka = t, nazwa = nazwa, wypelnienie = wypelnienie, duch = duch, liczba = liczba, portret = portret,
		ranga = ranga, rangaNapis = rangaNapis, tarcza = tarcza, efekty = efekty, podpisEfektow = "",
		maks = 1, cel = 1, pokazane = 1, duchPokazany = 1, duchCzeka = 0, wstrzas = 0, obrotBazowy = t.Rotation,
	}
end

function Interfejs:_zbudujVS()
	local K = self.K
	local vs = self:_nowy("Frame", {
		Name = "VS", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.11),
		Size = UDim2.fromScale(0.095, 0.095), SizeConstraint = Enum.SizeConstraint.RelativeYY, ZIndex = 15,
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
	self.tura = self:_tekst(self.kadr, {
		Name = "Tura", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.18), Size = UDim2.fromScale(0.12, 0.04),
		Font = NAGLOWKI, Text = "", TextColor3 = K.bialy, ZIndex = 15,
	}, 3)
end

function Interfejs:_zbudujBaner()
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

-- wstęga z nazwą użytej umiejętności (pod licznikiem tury)
function Interfejs:_zbudujUmiejetnosc()
	local K = self.K
	local u = self:_nowy("Frame", {
		Name = "Umiejetnosc", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.272),
		Size = UDim2.fromScale(0.44, 0.07), Rotation = -2, Visible = false, ZIndex = 28,
	}, self.kadr)
	self.umSkala = self:_nowy("UIScale", { Scale = 1 }, u)
	self.umWstega = self:_ramka(u, {
		Name = "Wstega", Size = UDim2.fromScale(1, 1), BackgroundColor3 = K.niebieski, ZIndex = 28,
	}, 4, 0.18, true)
	self.umNapis = self:_tekst(u, {
		Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.92, 0.78),
		Font = NAGLOWKI, Text = "", TextColor3 = K.bialy, ZIndex = 29,
	}, 4)
	self.umiejetnosc = u
end

function Interfejs:_przycisk(rodzic: Instance, nazwa: string, tekst: string, kolor: Color3, wlasciwosci: { [string]: any })
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
	self:_nowy("UIGradient", { Rotation = 90, Color = ColorSequence.new(Color3.new(1, 1, 1), Color3.new(0.82, 0.82, 0.82)) }, p)
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

function Interfejs:_zbudujPomin()
	local uchwyt, p = self:_przycisk(self.kadr, "Pomin", "POMIŃ  »", self.K.zolty, {
		AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(0.975, 0.955), Size = UDim2.fromScale(0.19, 0.115),
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

-- przyciski tempa: ×1 / ×2 / ×4 (lewy dolny róg; duże, do kciuka na telefonie)
function Interfejs:_zbudujTempo()
	local K = self.K
	local pas = self:_nowy("Frame", {
		Name = "Tempo", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0.025, 0.955),
		Size = UDim2.fromScale(0.3, 0.115), Visible = false, ZIndex = 40,
	}, self.kadr)
	self.tempoPrzyciski = {}
	for i, t in { 1, 2, 4 } do
		local uchwyt, p = self:_przycisk(pas, "Tempo" .. t, "×" .. t, K.szary, {
			AnchorPoint = Vector2.new(0, 0), Position = UDim2.fromScale((i - 1) * 0.34, 0), Size = UDim2.fromScale(0.3, 1),
			Rotation = ({ -2, 1, -1 })[i], ZIndex = 40,
		})
		self.tempoPrzyciski[t] = { uchwyt = uchwyt, przycisk = p }
	end
	self.tempoPas = pas
end

function Interfejs:_zbudujWynik()
	local K = self.K
	local uchwyt = self:_nowy("Frame", {
		Name = "Wynik", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.66, 0.58),
		Size = UDim2.fromScale(0.56, 0.64), Rotation = -1.2, Visible = false, ZIndex = 60,
	}, self.kadr)
	self.wynikSkala = self:_nowy("UIScale", { Scale = 1 }, uchwyt)
	local karta = self:_ramka(uchwyt, { Name = "Karta", Size = UDim2.fromScale(1, 1), BackgroundColor3 = K.krem, ZIndex = 61 }, 5, 0.06, true)
	local wstega = self:_ramka(uchwyt, {
		Name = "Wstega", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, -0.09), Size = UDim2.fromScale(1.06, 0.25),
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
		Name = "Podtytul", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.2), Size = UDim2.fromScale(0.92, 0.085),
		Font = KOMIKS, Text = "", TextColor3 = K.ciemny, ZIndex = 62,
	}, 0)
	local kafle = {}
	local opisy = { { "moneta", "ZŁOTO" }, { "gwiazda", "DOŚWIADCZ." }, { "zeton", "TOKENY LASU" }, { "gem", "GEM" }, { "shard", "SHARD EWOL." } }
	for i, opis in opisy do
		local kafel = self:_ramka(karta, {
			Name = "Kafel" .. i, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.11 + (i - 1) * 0.195, 0.315),
			Size = UDim2.fromScale(0.175, 0.37), BackgroundColor3 = K.bialy, Rotation = ({ -2.5, 1.5, -1.5, 2, -1 })[i], ZIndex = 62,
		}, 4, 0.1, true)
		local skala = self:_nowy("UIScale", { Scale = 1 }, kafel)
		local poleIkony = self:_nowy("Frame", {
			Name = "PoleIkony", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.05),
			Size = UDim2.fromScale(0.62, 0.42), ZIndex = 62,
		}, kafel)
		self:_ikona(poleIkony, opis[1], 0)
		local wartosc = self:_tekst(kafel, {
			Name = "Wartosc", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.48), Size = UDim2.fromScale(0.92, 0.3),
			Font = KOMIKS, Text = "", TextColor3 = K.tusz, ZIndex = 63,
		}, 0)
		local podpis = self:_tekst(kafel, {
			Name = "Podpis", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 0.79), Size = UDim2.fromScale(0.94, 0.16),
			Font = KOMIKS, Text = opis[2], TextColor3 = K.szary, ZIndex = 63,
		}, 0)
		kafle[i] = { ramka = kafel, skala = skala, wartosc = wartosc, podpis = podpis, ikona = poleIkony }
	end
	local _, jeszczePrzycisk = self:_przycisk(karta, "JeszczeRaz", "JESZCZE RAZ", K.zielony, {
		AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.29, 0.95), Size = UDim2.fromScale(0.42, 0.18), Rotation = -1.5, ZIndex = 66,
	})
	local _, zamknijPrzycisk = self:_przycisk(karta, "Zamknij", "ZAMKNIJ", K.czerwony, {
		AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.75, 0.95), Size = UDim2.fromScale(0.34, 0.18), Rotation = 1.5, ZIndex = 66,
	})
	local stopka = self:_tekst(uchwyt, {
		Name = "Stopka", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, 1.03), Size = UDim2.fromScale(0.98, 0.05),
		Font = Enum.Font.GothamBold, Text = "", TextColor3 = K.bialy, ZIndex = 62,
	}, 2)
	self.wynik = {
		uchwyt = uchwyt, wstega = wstega, tytul = tytul, tytulCien = tytulCien, podtytul = podtytul, kafle = kafle,
		jeszcze = jeszczePrzycisk, zamknij = zamknijPrzycisk, stopka = stopka, liczniki = {},
	}
end

------------------------------------------------------------------ sterowanie z odtwarzacza
-- strony: walka.strony; aktorzy: { gracz = klucz aktora, wrog = klucz aktora }
function Interfejs:ustawStrony(strony, aktorzy)
	for strona, dane in strony do
		local p = self.paski[strona]
		if p then
			p.nazwa.Text = string.upper(dane.nazwa) .. "  •  POZ. " .. tostring(dane.poziom)
			p.maks = math.max(1, dane.zycie)
			p.hp = dane.zycie
			p.cel, p.pokazane, p.duchPokazany, p.duchCzeka, p.wstrzas = 1, 1, 1, 0, 0
			p.liczba.Text = tostring(dane.zycie) .. " / " .. tostring(dane.zycie)
			p.wypelnienie.Size = UDim2.fromScale(1, 1)
			p.wypelnienie.Visible = true
			p.duch.Size = UDim2.fromScale(1, 1)
			p.tabliczka.Rotation = p.obrotBazowy
			p.tarcza.Visible = false
			local ikona = p.portret:FindFirstChild("Ikona")
			if ikona then
				ikona:Destroy()
			end
			self:_ikona(p.portret, aktorzy[strona] or "oko", 0.13)
			local r = RANGI[dane.ranga] or RANGI.zwykly
			p.ranga.Visible = strona == "wrog"
			p.rangaNapis.Text = r[1]
			p.ranga.BackgroundColor3 = Color3.fromHex(r[2])
			self:ustawEfekty(strona, {})
		end
	end
	self:ustawTure(0)
end

function Interfejs:ustawZycie(strona: string, hp: number, natychmiast: boolean?)
	local p = self.paski[strona]
	if not p then
		return
	end
	if p.hp == hp and not natychmiast then
		return
	end
	p.hp = hp
	p.cel = math.clamp(hp / p.maks, 0, 1)
	p.liczba.Text = tostring(hp) .. " / " .. tostring(p.maks)
	if natychmiast then
		p.pokazane, p.duchPokazany, p.duchCzeka, p.wstrzas = p.cel, p.cel, 0, 0
		p.wypelnienie.Size = UDim2.fromScale(math.max(p.cel, 0.001), 1)
		p.wypelnienie.Visible = p.cel > 0.004
	else
		p.duchCzeka = 0.28
		p.wstrzas = 1
	end
end

-- zapas tarczy (pochłanianie) jako ułamek życia maksymalnego
function Interfejs:ustawTarcze(strona: string, zapas: number)
	local p = self.paski[strona]
	if not p then
		return
	end
	p.tarcza.Visible = zapas > 0
	p.tarcza.Size = UDim2.fromScale(math.clamp(zapas / p.maks, 0.02, 1), 0.45)
end

-- lista: { { id, ikona, kolor, tury, zapas } } — przebudowa tylko przy zmianie
function Interfejs:ustawEfekty(strona: string, lista)
	local p = self.paski[strona]
	if not p then
		return
	end
	local podpis = {}
	for _, e in lista do
		table.insert(podpis, e.id .. ":" .. tostring(e.tury) .. ":" .. tostring(e.zapas or 0))
	end
	local s = table.concat(podpis, ",")
	if s == p.podpisEfektow then
		return
	end
	p.podpisEfektow = s
	for _, d in p.efekty:GetChildren() do
		if d:IsA("Frame") then
			d:Destroy()
		end
	end
	for i, e in lista do
		local f = self:_ramka(p.efekty, {
			Name = "Efekt_" .. e.id, Size = UDim2.fromScale(1, 1), SizeConstraint = Enum.SizeConstraint.RelativeYY,
			BackgroundColor3 = self.K.ciemny, LayoutOrder = i, ZIndex = 12,
		}, 3, 0.2, false)
		self:_ikona(f, e.ikona, 0.14)
		local licznik = self:_ramka(f, {
			-- licznik tur: na telefonie (390 punktów wysokości) cyfra ma ok. 14 punktów (testy/telefon.py)
			Name = "Licznik", AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(1.16, 1.16), Size = UDim2.fromScale(0.62, 0.62),
			BackgroundColor3 = Color3.fromHex(e.kolor), ZIndex = 15,
		}, 2, 0.5, false)
		self:_tekst(licznik, {
			Name = "Tury", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.88, 0.88),
			Font = NAGLOWKI, Text = tostring(e.tury), TextColor3 = self.K.tusz, ZIndex = 16,
		}, 0)
		if e.zapas and e.zapas > 0 then
			self:_tekst(f, {
				Name = "Zapas", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.fromScale(0.5, -0.42), Size = UDim2.fromScale(1.3, 0.4),
				Font = KOMIKS, Text = tostring(e.zapas), TextColor3 = Color3.fromHex("#9FE8FF"), ZIndex = 16,
			}, 2)
		end
	end
end

function Interfejs:ustawTure(n: number)
	self.tura.Text = if n > 0 then ("TURA " .. tostring(n)) else ""
end

function Interfejs:pokazUmiejetnosc(tekst: string, strona: string)
	local K = self.K
	self.umNapis.Text = string.upper(tekst)
	self.umWstega.BackgroundColor3 = if strona == "gracz" then K.niebieski else K.czerwony
	self.umiejetnosc.Rotation = if strona == "gracz" then -2 else 2
	self.umiejetnosc.Visible = true
	self.umSkala.Scale = 0.4
	TweenService:Create(self.umSkala, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:ukryjUmiejetnosc()
	self.umiejetnosc.Visible = false
end

--[[ Komiksowy napis nad postacią. styl: zadane, otrzymane, magiczne, blok, unik, krytyk, krytykLiczba, efekt (kolor
	z argumentu), info (mały). Pozycja śledzi punkt w świecie. ]]
local STYLE = {
	zadane = { kolor = "#FFFFFF", rozmiar = 0.12, zycie = 0.95 },
	otrzymane = { kolor = "#FF8A9A", rozmiar = 0.11, zycie = 0.95 },
	magiczne = { kolor = "#C08CFF", rozmiar = 0.12, zycie = 0.95 },
	blok = { kolor = "#7CF3FF", rozmiar = 0.1, zycie = 1.0 },
	unik = { kolor = "#B8FF8A", rozmiar = 0.1, zycie = 1.0 },
	krytyk = { kolor = "#FFE14A", rozmiar = 0.115, zycie = 1.25, gwiazda = true },
	krytykLiczba = { kolor = "#FFE14A", rozmiar = 0.165, zycie = 1.25 },
	efekt = { kolor = "#FFFFFF", rozmiar = 0.08, zycie = 1.0 },
	tyk = { kolor = "#FFFFFF", rozmiar = 0.09, zycie = 0.8 },
	info = { kolor = "#E3E7EC", rozmiar = 0.06, zycie = 0.9 },
}

function Interfejs:napis(punkt: Vector3, tekst: string, styl: string, przesuniecie: Vector2?, obrot: number?, kolor: Color3?)
	local def = STYLE[styl] or STYLE.zadane
	local K = self.K
	local wys = def.rozmiar
	-- kilka napisów naraz nad tą samą postacią (cios + efekt + tarcza): każdy kolejny niżej, żeby się nie nakładały
	local zajete = 0
	for _, n in self.napisy do
		if n.wiek < n.zycie * 0.75 and (n.punkt - punkt).Magnitude < 2.5 then
			zajete += 1
		end
	end
	if zajete > 0 then
		przesuniecie = (przesuniecie or Vector2.zero) + Vector2.new(0, 0.085 * math.min(zajete, 3))
	end
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
	}, if styl == "info" then 3 else 5)
	local napis = self:_tekst(pole, {
		Name = "Tekst", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(1, 1),
		Font = KOMIKS, Text = tekst, TextColor3 = kolor or Color3.fromHex(def.kolor), ZIndex = 22,
	}, if styl == "info" then 3 else 4.5)
	table.insert(self.napisy, {
		pole = pole, skala = skala, cien = cien, napis = napis, gwiazda = gwiazda, punkt = punkt, wiek = 0, zycie = def.zycie,
		wys = wys, szer = wys * (0.6 * math.max(3, utf8.len(tekst) or #tekst)), przesuniecie = przesuniecie or Vector2.zero,
	})
end

function Interfejs:pokazBaner(tekst: string, kolorNapisu: Color3, kolorWstegi: Color3, wysokosc: number?)
	self.baner.Position = UDim2.fromScale(0.5, wysokosc or 0.31)
	self.banerNapis.Text = tekst
	self.banerCien.Text = tekst
	self.banerNapis.TextColor3 = kolorNapisu
	self.banerWstega.BackgroundColor3 = kolorWstegi
	self.baner.Visible = true
	self.banerSkala.Scale = 0.3
	TweenService:Create(self.banerSkala, TweenInfo.new(0.28, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:ukryjBaner(natychmiast: boolean?)
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

function Interfejs:pokazPomin(funkcja: () -> ())
	self.pomin.Visible = true
	if self.polaczeniePomin then
		self.polaczeniePomin:Disconnect()
	end
	self.polaczeniePomin = self.pominPrzycisk.Activated:Connect(funkcja)
end

function Interfejs:ukryjPomin()
	self.pomin.Visible = false
end

-- przyciski tempa: aktywne = 1 | 2 | 4; naZmiane(t)
function Interfejs:pokazTempo(aktywne: number, naZmiane: (number) -> ())
	self.tempoPas.Visible = true
	self.polaczeniaTempa = self.polaczeniaTempa or {}
	for _, c in self.polaczeniaTempa do
		c:Disconnect()
	end
	table.clear(self.polaczeniaTempa)
	for t, pr in self.tempoPrzyciski do
		table.insert(self.polaczeniaTempa, pr.przycisk.Activated:Connect(function()
			naZmiane(t)
		end))
	end
	self:ustawTempo(aktywne)
end

function Interfejs:ustawTempo(aktywne: number)
	for t, pr in self.tempoPrzyciski do
		local wl = t == aktywne
		pr.przycisk.BackgroundColor3 = if wl then self.K.zolty else self.K.szary
		local n = pr.przycisk:FindFirstChild("Napis")
		if n then
			n.TextColor3 = if wl then self.K.tusz else self.K.bialy
		end
		pr.przycisk:SetAttribute("Aktywny", wl)
	end
end

function Interfejs:ukryjTempo()
	self.tempoPas.Visible = false
end

-- odmiana liczebnika: 1 tura, 2–4 tury (ale 12–14 tur), 5+ tur; 22 tury, 25 tur
function Interfejs.liczebnik(n: number, jeden: string, kilka: string, wiele: string): string
	local forma
	if n == 1 then
		forma = jeden
	elseif n % 10 >= 2 and n % 10 <= 4 and (n % 100 < 12 or n % 100 > 14) then
		forma = kilka
	else
		forma = wiele
	end
	return tostring(n) .. " " .. forma
end

-- „w 1 turze”, „w 3 turach”
function Interfejs.wTurach(n: number): string
	return if n == 1 then "w 1 turze" else ("w " .. tostring(n) .. " turach")
end

function Interfejs:pokazWynik(walka, naJeszczeRaz: () -> (), naZamknij: () -> ())
	local K = self.K
	local w = self.wynik
	local wygrana = walka.wynik == "wygrana"
	local tytul = if wygrana then "ZWYCIĘSTWO!" else "PORAŻKA!"
	w.tytul.Text = tytul
	w.tytulCien.Text = tytul
	w.tytul.TextColor3 = if wygrana then K.zolty else K.bialy
	w.wstega.BackgroundColor3 = if wygrana then K.pomarancz else K.fiolet
	local wrog = walka.strony.wrog
	w.podtytul.Text = if wygrana
		then string.format("%s (poz. %d) pokonany %s", wrog.nazwa, wrog.poziom, Interfejs.wTurach(walka.tury))
		else string.format("%s (poz. %d) był silniejszy — %s", wrog.nazwa, wrog.poziom, Interfejs.liczebnik(walka.tury, "tura", "tury", "tur"))
	local lup = walka.lup
	local wartosci = { lup.zloto, lup.doswiadczenie, lup.tokeny_krainy, lup.gemy, lup.shard_ewolucji }
	w.liczniki = {}
	for i, kafel in w.kafle do
		local v = wartosci[i] or 0
		local jest = v > 0
		kafel.ramka.BackgroundColor3 = if jest then (if i >= 4 then Color3.fromHex("#FFF6C9") else K.bialy) else Color3.fromHex("#D9D3C4")
		kafel.wartosc.TextColor3 = if jest then K.tusz else K.szary
		kafel.wartosc.Text = if jest then "+0" else "—"
		kafel.ramka:SetAttribute("Wartosc", v)
		for _, piksel in kafel.ikona:GetDescendants() do
			if piksel:IsA("Frame") and piksel.Name ~= "Ikona" then
				piksel.BackgroundTransparency = if jest then 0 else 0.65
			end
		end
		if jest then
			table.insert(w.liczniki, { etykieta = kafel.wartosc, cel = v, start = 0.25 + (i - 1) * 0.14, trwa = if v > 5 then 0.45 else 0.2 })
		end
		kafel.skala.Scale = 0.01
		task.delay(0.12 + (i - 1) * 0.08, function()
			if not self.zniszczony then
				TweenService:Create(kafel.skala, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
			end
		end)
	end
	w.czasPokazania = 0
	w.blokadaPokazana = nil
	w.stopka.Text = string.format("dziennik policzył serwer  •  ziarno %s  •  %s  •  %s  •  %.1f s",
		tostring(walka.ziarno), Interfejs.liczebnik(walka.tury, "tura", "tury", "tur"),
		Interfejs.liczebnik(#walka.dziennik, "zdarzenie", "zdarzenia", "zdarzeń"), walka.czas)
	if w.polJeszcze then
		w.polJeszcze:Disconnect()
	end
	if w.polZamknij then
		w.polZamknij:Disconnect()
	end
	w.polJeszcze = w.jeszcze.Activated:Connect(naJeszczeRaz)
	w.polZamknij = w.zamknij.Activated:Connect(naZamknij)
	w.uchwyt.Position = UDim2.fromScale(if wygrana then 0.66 else 0.34, 0.58)
	w.uchwyt.Visible = true
	self.wynikSkala.Scale = 0.55
	TweenService:Create(self.wynikSkala, TweenInfo.new(0.32, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:ustawBlokadeJeszczeRaz(zostalo: number)
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

function Interfejs:ukryjWynik()
	self.wynik.uchwyt.Visible = false
	self.wynik.liczniki = {}
end

function Interfejs:ustawZaslone(krycie: number)
	self.zaslona.BackgroundTransparency = 1 - math.clamp(krycie, 0, 1)
end

function Interfejs:ustawZegar(tekst: string?)
	self.zegar.Visible = tekst ~= nil
	if tekst then
		self.zegar.Text = tekst
	end
end

function Interfejs:pokazPaski(widoczne: boolean)
	for _, p in self.paski do
		p.tabliczka.Visible = widoczne
	end
	self.vs.Visible = widoczne
	self.tura.Visible = widoczne
end

function Interfejs:usunNapisy()
	for _, n in self.napisy do
		n.pole:Destroy()
	end
	table.clear(self.napisy)
end

function Interfejs:aktualizuj(dt: number, kamera: Camera)
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
				local ekran = kamera:WorldToViewportPoint(n.punkt)
				local wysPx = n.wys * kadr.wys
				local szerPx = n.szer * kadr.wys
				local wznios = (0.02 + 0.075 * (1 - (1 - u) * (1 - u))) * kadr.wys
				local bazaY = math.clamp(ekran.Y - wznios, kadr.y + kadr.wys * 0.42, kadr.y + kadr.wys * 0.74)
				local x = ekran.X + n.przesuniecie.X * kadr.wys
				-- nie wyżej niż pod wstęgą z nazwą umiejętności
				local y = math.max(bazaY + n.przesuniecie.Y * kadr.wys, kadr.y + kadr.wys * (self.gornaGranicaNapisow or 0.33) + wysPx * 0.5)
				x = math.clamp(x, kadr.x + szerPx * 0.5 + 6, kadr.x + kadr.sz - szerPx * 0.5 - 6)
				n.pole.Visible = ekran.Z > 0
				n.pole.Position = UDim2.fromOffset(x, y)
				n.pole.Size = UDim2.fromOffset(szerPx, wysPx)
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

-- liczba obrażeń pokazywana na pasku (do testu zgodności z dziennikiem)
function Interfejs:zycie(strona: string): number?
	local p = self.paski[strona]
	return p and p.hp
end

function Interfejs:zniszcz()
	if self.zniszczony then
		return
	end
	self.zniszczony = true
	for _, p in self.polaczenia do
		p:Disconnect()
	end
	if self.polaczeniePomin then
		self.polaczeniePomin:Disconnect()
	end
	for _, c in self.polaczeniaTempa or {} do
		c:Disconnect()
	end
	if self.wynik.polJeszcze then
		self.wynik.polJeszcze:Disconnect()
	end
	if self.wynik.polZamknij then
		self.wynik.polZamknij:Disconnect()
	end
	self.gui:Destroy()
end

return Interfejs
