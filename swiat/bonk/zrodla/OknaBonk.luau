--[[
	OknaBonk — okna i nakładki etapu 2 gry BONK (ModuleScript w Workspace/BonkGra/Moduly), u klienta. Teksty po
	angielsku (D-045), skala z okna jak InterfejsBonk (wzór 667 × 375, telefon poziomo).

	Przyciski z boku (PETS, INDEX, GIFT z kropką, gdy prezent czeka), przycisk przy stoisku / inkubatorze na dole
	(OPEN SHOP / HATCH z ceną i jawnymi szansami nad nim — D-015), okna: sklep pałek, pety (AUTO BEST albo wybór ręczny),
	Księga petów (15 miejsc, nieodkryte jako czarne sylwetki, licznik „7/15”), dzienny prezent (CLAIM). Nakładki:
	komunikat serwera (pasek u góry), krótki dymek, pasek życia Strażnika (wspólny), napisy wyklucia.
	Nic nie liczy: stan z atrybutów gracza (serwer), akcje przez `akcja(rodzaj, arg)` (Sygnaly/Akcja — sprawdza serwer).

	Etap 3: napis bramy na ekranie (pasek w stosie u góry, gdy gracz stoi przy bramie — klient chowa wtedy tablicę nad
	bramą), mnożniki dokładnie („x1.5 POWER”), przyciski ≥ 44 pt (cała karta sklepu klikalna, X 46 × 46, AUTO BEST 44),
	pad: B zamyka okno, LB = PETS, RB = INDEX, krzyżak w górę = GIFT, Y = przycisk przy stoisku / inkubatorze; okno
	otwarte padem zaznacza pierwszy przycisk (GuiService.SelectedObject) — dalej krzyżak i A; znaczki LB / RB / UP / Y / B
	widać, gdy gracz gra na padzie.

	Użycie: local o = Okna.nowe(rodzic, D, L, { dotyk, emulacja }, akcja, wzorce)
		o:otworz("sklep" | "pety" | "ksiega" | "prezent")  o:zamknij()  o:odswiez()  o:kontekst(rodzaj?, nr?)
		o:toast(tekst, kolor?)  o:ogloszenie(tekst, kolor?)  o:straznik(dane?)  o:wyklucie(dane?)  o:krok(dt)
		o:brama(tekst?, kolor?)  o:pad(KeyCode) → bool  o:trybPada(bool)  o:stan()  o:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

local Okna = {}
Okna.__index = Okna

local function nowy(klasa: string, wl: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wl do
		o[k] = v
	end
	if rodzic then
		o.Parent = rodzic
	end
	return o
end

local function obrys(rodzic: Instance, grubosc: number, kolor: Color3)
	return nowy("UIStroke", { Thickness = grubosc, Color = kolor, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, rodzic)
end

local function tekstObrys(rodzic: Instance, grubosc: number, kolor: Color3)
	return nowy("UIStroke", { Thickness = grubosc, Color = kolor, ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual }, rodzic)
end

local function rogi(rodzic: Instance, r: number)
	return nowy("UICorner", { CornerRadius = UDim.new(0, r) }, rodzic)
end

local function hex(h: string): Color3
	return Color3.fromHex(h)
end

-- znaczek przycisku pada (LB, RB, UP, Y, B) w rogu przycisku; widać tylko przy grze na padzie
local function znaczek(rodzic: Instance, tekst: string, tusz: Color3, papier: Color3, czcionka: Enum.Font): TextLabel
	local z = Instance.new("TextLabel")
	z.Name = "ZnaczekPada"
	z.AnchorPoint = Vector2.new(0.5, 0.5)
	z.Position = UDim2.new(1, -2, 1, -2)
	z.Size = UDim2.fromOffset(if #tekst > 1 then 30 else 22, 22)
	z.BackgroundColor3 = tusz
	z.Text = tekst
	z.TextScaled = true
	z.Font = czcionka
	z.TextColor3 = papier
	z.ZIndex = 14
	z.Visible = false
	local r = Instance.new("UICorner")
	r.CornerRadius = UDim.new(0.5, 0)
	r.Parent = z
	z.Parent = rodzic
	return z
end

-- „id:kopie,…” → { [id] = kopie }, kolejność
local function czytajPety(napis: any): { [string]: number }
	local w = {}
	if type(napis) ~= "string" then
		return w
	end
	for kawalek in string.gmatch(napis, "[^,]+") do
		local id, n = string.match(kawalek, "^([%w_]+):(%d+)$")
		if id then
			w[id] = tonumber(n) or 0
		end
	end
	return w
end

local function czytajListe(napis: any): { string }
	local w = {}
	if type(napis) ~= "string" then
		return w
	end
	for kawalek in string.gmatch(napis, "[^,]+") do
		table.insert(w, kawalek)
	end
	return w
end

-- podgląd modelu z wzorca w ViewportFrame (cien = czarna sylwetka — nieodkryty pet)
local function podglad(rodzic: Instance, wzorce: Instance?, nazwa: string, rozmiar: UDim2, pozycja: UDim2, cien: boolean)
	local vf = nowy("ViewportFrame", { BackgroundTransparency = 1, Size = rozmiar, Position = pozycja,
		Ambient = Color3.fromRGB(175, 175, 175), LightColor = Color3.new(1, 1, 1), LightDirection = Vector3.new(-1, -2, 1.5) }, rodzic)
	local wz = wzorce and wzorce:FindFirstChild(nazwa)
	if wz then
		local m = wz:Clone()
		m:PivotTo(CFrame.new())
		m.Parent = vf
		local cf, roz = m:GetBoundingBox()
		local r = math.max(roz.X, roz.Y, roz.Z)
		local kam = Instance.new("Camera")
		kam.FieldOfView = 32
		local d = r * 1.9
		kam.CFrame = CFrame.lookAt(cf.Position + Vector3.new(d * 0.35, d * 0.22, -d), cf.Position)
		kam.Parent = vf
		vf.CurrentCamera = kam
	end
	if cien then
		vf.ImageColor3 = Color3.new(0, 0, 0)
	end
	return vf
end

function Okna.nowe(rodzic: Instance, D, L, opcje, akcja: (string, any) -> (), wzorce: Instance?)
	local self = setmetatable({}, Okna)
	self.D, self.L, self.akcja, self.wzorce = D, L, akcja, wzorce
	self.gracz = Players.LocalPlayer
	self.dotyk = opcje and opcje.dotyk == true
	local U = D.ui
	local tusz, papier = hex(U.kolory.tusz), hex(U.kolory.papier)
	self.tusz, self.papier = tusz, papier
	self.czcionka = Enum.Font[U.czcionka] or Enum.Font.LuckiestGuy
	self.cyfry = Enum.Font[U.czcionka_cyfr] or Enum.Font.FredokaOne
	local gui = nowy("ScreenGui", { Name = "BonkOkna", ResetOnSpawn = false, IgnoreGuiInset = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling, DisplayOrder = 6 }, rodzic)
	self.gui = gui
	local ekran: Instance = gui
	local emulacja = opcje and opcje.emulacja
	if emulacja then
		ekran = nowy("Frame", { Name = "EmulacjaTelefonu", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromOffset(emulacja.X, emulacja.Y), BackgroundTransparency = 1, ClipsDescendants = true }, gui)
	end
	self.ekran = ekran
	local kamera = workspace.CurrentCamera
	self.skale = {}
	local function skala(): number
		local v = if emulacja then emulacja else kamera.ViewportSize
		return math.clamp(math.min(v.X / 667, v.Y / 375), 0.8, 1.5)
	end
	local function skalowany(o: Instance)
		local s = nowy("UIScale", {}, o)
		table.insert(self.skale, s)
		return s
	end
	self.skalowany = skalowany

	------------------------------------------------------------ przyciski z boku
	local kol = nowy("Frame", { Name = "Boczne", AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 8, 0.4, 0),
		Size = UDim2.fromOffset(66, 196), BackgroundTransparency = 1 }, ekran)
	skalowany(kol)
	nowy("UIListLayout", { Padding = UDim.new(0, 8), SortOrder = Enum.SortOrder.LayoutOrder }, kol)
	self.boczne = kol
	self.przyciski = {}
	local function boczny(nazwa: string, tekst: string, kolor: string, nr: number)
		local b = nowy("TextButton", { Name = nazwa, LayoutOrder = nr, Size = UDim2.fromOffset(66, 58), BackgroundColor3 = hex(kolor),
			AutoButtonColor = true, Text = tekst, TextScaled = true, Font = self.czcionka, TextColor3 = papier }, kol)
		rogi(b, 14)
		obrys(b, 3, tusz)
		tekstObrys(b, 2, tusz)
		nowy("UIPadding", { PaddingLeft = UDim.new(0, 6), PaddingRight = UDim.new(0, 6), PaddingTop = UDim.new(0, 14),
			PaddingBottom = UDim.new(0, 14) }, b)
		b.Activated:Connect(function()
			if self.otwarte == nazwa then
				self:zamknij()
			else
				self:otworz(nazwa)
			end
		end)
		self.przyciski[nazwa] = b
		return b
	end
	boczny("pety", U.pety, "4FB3FF", 1)
	boczny("ksiega", U.ksiega, "C27BFF", 2)
	local bp = boczny("prezent", U.prezent, "FF8A3D", 3)
	self.znaczki = {}
	for nazwa, b in self.przyciski do
		table.insert(self.znaczki, znaczek(b, U.pad[nazwa] or "?", tusz, papier, self.czcionka))
	end
	self.kropka = nowy("Frame", { Name = "Kropka", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(1, 1, 0, -1),
		Size = UDim2.fromOffset(16, 16), BackgroundColor3 = hex("FF3B3B"), Visible = false, ZIndex = 3 }, bp)
	rogi(self.kropka, 9)
	obrys(self.kropka, 2, tusz)

	------------------------------------------------------------ przycisk przy stoisku / inkubatorze (dół, środek) + szanse
	local kont = nowy("Frame", { Name = "Kontekst", AnchorPoint = Vector2.new(0.5, 1),
		Position = UDim2.new(0.5, 0, 1, if self.dotyk then -14 else -18), Size = UDim2.fromOffset(240, 60),
		BackgroundTransparency = 1, Visible = false }, ekran)
	skalowany(kont)
	self.kontekstRamka = kont
	local kb = nowy("TextButton", { Name = "Przycisk", Size = UDim2.fromScale(1, 1), BackgroundColor3 = hex("3DBE5A"),
		AutoButtonColor = true, Text = "", TextScaled = true, Font = self.czcionka, TextColor3 = papier }, kont)
	rogi(kb, 16)
	obrys(kb, 4, tusz)
	tekstObrys(kb, 2.5, tusz)
	nowy("UIPadding", { PaddingLeft = UDim.new(0, 12), PaddingRight = UDim.new(0, 12), PaddingTop = UDim.new(0, 10),
		PaddingBottom = UDim.new(0, 10) }, kb)
	self.kontekstPrzycisk = kb
	table.insert(self.znaczki, znaczek(kont, U.pad.kontekst, tusz, papier, self.czcionka))
	kb.Activated:Connect(function()
		if self.kontekstRodzaj == "sklep" then
			self:otworz("sklep")
		elseif self.kontekstRodzaj == "jajko" and self.kontekstNr then
			self.akcja("jajko", self.kontekstNr)
		end
	end)
	-- szanse jajka nad przyciskiem (jawne, D-015)
	local sz = nowy("Frame", { Name = "Szanse", AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 0, -8),
		Size = UDim2.fromOffset(300, 116), BackgroundColor3 = papier, Visible = false }, kont)
	rogi(sz, 12)
	obrys(sz, 3, tusz)
	nowy("TextLabel", { Name = "Tytul", BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 4), Size = UDim2.new(1, -20, 0, 20),
		Text = U.szanse, TextScaled = true, Font = self.czcionka, TextColor3 = tusz }, sz)
	local lst = nowy("Frame", { Name = "Lista", BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 26),
		Size = UDim2.new(1, -20, 1, -30) }, sz)
	nowy("UIListLayout", { Padding = UDim.new(0, 1), SortOrder = Enum.SortOrder.LayoutOrder }, lst)
	self.szanseRamka, self.szanseLista = sz, lst

	------------------------------------------------------------ dymek (krótki napis nad przyciskiem kontekstu)
	local toast = nowy("TextLabel", { Name = "Dymek", AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.new(0.5, 0, 1, -150),
		Size = UDim2.fromOffset(360, 34), BackgroundTransparency = 1, Text = "", TextScaled = true, Font = self.czcionka,
		TextColor3 = papier, Visible = false, ZIndex = 14 }, ekran)
	tekstObrys(toast, 3, tusz)
	skalowany(toast)
	self.dymek, self.czasDymka = toast, -1

	------------------------------------------------------------ komunikat serwera (pasek u góry)
	local ogl = nowy("Frame", { Name = "Ogloszenie", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 178),
		Size = UDim2.fromOffset(470, 40), BackgroundColor3 = tusz, BackgroundTransparency = 0.15, Visible = false, ZIndex = 7 }, ekran)
	rogi(ogl, 12)
	self.obrysOgl = obrys(ogl, 3, papier)
	self.tekstOgl = nowy("TextLabel", { BackgroundTransparency = 1, Position = UDim2.fromOffset(12, 5), Size = UDim2.new(1, -24, 1, -10),
		Text = "", TextScaled = true, Font = self.czcionka, TextColor3 = papier, ZIndex = 7 }, ogl)
	self.skalaOgl = skalowany(ogl)
	self.ogl, self.kolejkaOgl, self.czasOgl = ogl, {}, -1

	------------------------------------------------------------ napis bramy (u góry, w stosie; gracz przy bramie)
	local br = nowy("Frame", { Name = "NapisBramy", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 150),
		Size = UDim2.fromOffset(330, 34), BackgroundColor3 = tusz, BackgroundTransparency = 0.1, Visible = false, ZIndex = 6 }, ekran)
	rogi(br, 10)
	self.obrysBramy = obrys(br, 2.5, papier)
	self.tekstBramy = nowy("TextLabel", { BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 3), Size = UDim2.new(1, -20, 1, -6),
		Text = "", TextScaled = true, Font = self.czcionka, TextColor3 = papier, ZIndex = 6 }, br)
	skalowany(br)
	self.bramaRamka = br

	------------------------------------------------------------ pasek życia Strażnika (wspólny, u góry)
	local ps = nowy("Frame", { Name = "Straznik", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 104),
		Size = UDim2.fromOffset(420, 44), BackgroundTransparency = 1, Visible = false }, ekran)
	skalowany(ps)
	self.nazwaStraznika = nowy("TextLabel", { BackgroundTransparency = 1, Size = UDim2.new(1, 0, 0, 18), Text = "",
		TextScaled = true, Font = self.czcionka, TextColor3 = papier }, ps)
	tekstObrys(self.nazwaStraznika, 2, tusz)
	local tlo = nowy("Frame", { Name = "Tlo", Position = UDim2.fromOffset(0, 20), Size = UDim2.new(1, 0, 0, 22),
		BackgroundColor3 = tusz }, ps)
	rogi(tlo, 8)
	obrys(tlo, 2, papier)
	self.wypelnienieStraznika = nowy("Frame", { Position = UDim2.fromOffset(3, 3), Size = UDim2.new(1, -6, 1, -6),
		BackgroundColor3 = hex("E8433B") }, tlo)
	rogi(self.wypelnienieStraznika, 6)
	self.liczbyStraznika = nowy("TextLabel", { BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "", TextScaled = true,
		Font = self.cyfry, TextColor3 = papier, ZIndex = 2 }, tlo)
	tekstObrys(self.liczbyStraznika, 2, tusz)
	self.pasekStraznika = ps

	------------------------------------------------------------ scena wyklucia (środek): przyciemnienie, błysk, jajko i pet, napisy
	self.przyciemnienie = nowy("Frame", { Name = "Przyciemnienie", Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz,
		BackgroundTransparency = 0.45, Visible = false, ZIndex = 8 }, ekran)
	local wy = nowy("Frame", { Name = "Wyklucie", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(460, 330), BackgroundTransparency = 1, Visible = false, ZIndex = 9 }, ekran)
	self.skalaWyklucia = skalowany(wy)
	self.blyskWyklucia = nowy("Frame", { Name = "Blysk", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(0, 0), BackgroundColor3 = papier, BackgroundTransparency = 1, ZIndex = 9 }, wy)
	nowy("UICorner", { CornerRadius = UDim.new(0.5, 0) }, self.blyskWyklucia)
	self.vfWyklucia = nowy("ViewportFrame", { Name = "Scena", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
		Size = UDim2.fromOffset(250, 250), BackgroundTransparency = 1, Ambient = Color3.fromRGB(180, 180, 180),
		LightColor = Color3.new(1, 1, 1), LightDirection = Vector3.new(-1, -2, 1.5), ZIndex = 10 }, wy)
	self.napisWyklucia = nowy("TextLabel", { BackgroundTransparency = 1, Size = UDim2.new(1, 0, 0, 52), Text = "", TextScaled = true,
		Font = self.czcionka, TextColor3 = hex("FFC83D"), Rotation = -4, ZIndex = 11 }, wy)
	tekstObrys(self.napisWyklucia, 4, tusz)
	self.petWyklucia = nowy("TextLabel", { BackgroundTransparency = 1, Position = UDim2.new(0, 0, 1, -40), Size = UDim2.new(1, 0, 0, 38),
		Text = "", TextScaled = true, Font = self.czcionka, TextColor3 = papier, ZIndex = 11 }, wy)
	self.obrysPeta = tekstObrys(self.petWyklucia, 3, tusz)
	self.wyklucieRamka = wy

	self.otwarte = nil
	self.zegar = 0
	local function przeskaluj()
		local s = skala()
		for _, u in self.skale do
			u.Scale = s
		end
		self.s = s
	end
	self.przeskaluj = przeskaluj
	przeskaluj()
	self.polaczenie = kamera:GetPropertyChangedSignal("ViewportSize"):Connect(przeskaluj)
	self:odswiez()
	return self
end

------------------------------------------------------------------ okna
function Okna:okno(nazwa: string, tytul: string, szer: number, wys: number)
	self:zamknij()
	local tusz, papier = self.tusz, self.papier
	local f = nowy("Frame", { Name = "Okno_" .. nazwa, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 0.5, 8),
		Size = UDim2.fromOffset(szer, wys), BackgroundColor3 = papier, ZIndex = 10 }, self.ekran)
	rogi(f, 18)
	obrys(f, 4, tusz)
	local s = nowy("UIScale", { Scale = self.s or 1 }, f)
	table.insert(self.skale, s)
	self.skalaOkna = s
	local t = nowy("TextLabel", { Name = "Tytul", BackgroundTransparency = 1, Position = UDim2.fromOffset(16, 8),
		Size = UDim2.new(1, -150, 0, 30), Text = tytul, TextScaled = true, Font = self.czcionka, TextColor3 = tusz,
		TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 11 }, f)
	local x = nowy("TextButton", { Name = "Zamknij", AnchorPoint = Vector2.new(1, 0), Position = UDim2.new(1, 10, 0, -10),
		Size = UDim2.fromOffset(46, 46), BackgroundColor3 = hex("E8433B"), Text = self.D.ui.zamknij, TextScaled = true,
		Font = self.czcionka, TextColor3 = papier, ZIndex = 12 }, f)
	rogi(x, 12)
	obrys(x, 3, tusz)
	nowy("UIPadding", { PaddingTop = UDim.new(0, 9), PaddingBottom = UDim.new(0, 9) }, x)
	x.Activated:Connect(function()
		self:zamknij()
	end)
	local zx = znaczek(x, self.D.ui.pad.zamknij, tusz, papier, self.czcionka)
	zx.Visible = self.padWlaczony == true
	local tresc = nowy("Frame", { Name = "Tresc", BackgroundTransparency = 1, Position = UDim2.fromOffset(12, 44),
		Size = UDim2.new(1, -24, 1, -54), ZIndex = 10 }, f)
	self.oknoRamka, self.otwarte, self.tytulOkna = f, nazwa, t
	s.Scale = (self.s or 1) * 0.85
	TweenService:Create(s, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = self.s or 1 }):Play()
	return f, tresc
end

function Okna:zamknij()
	if self.oknoRamka then
		for i, s in self.skale do
			if s == self.skalaOkna then
				table.remove(self.skale, i)
				break
			end
		end
		local zazn = GuiService.SelectedObject
		if zazn and zazn:IsDescendantOf(self.oknoRamka) then
			pcall(function()
				GuiService.SelectedObject = nil
			end)
		end
		self.oknoRamka:Destroy()
	end
	self.oknoRamka, self.otwarte, self.skalaOkna = nil, nil, nil
end

local function karta(rodzic: Instance, nazwa: string, kolor: Color3, tusz: Color3, nr: number)
	local k = nowy("Frame", { Name = nazwa, LayoutOrder = nr, BackgroundColor3 = kolor, ZIndex = 10 }, rodzic)
	rogi(k, 12)
	obrys(k, 2.5, tusz)
	return k
end

function Okna:etykieta(rodzic: Instance, tekst: string, poz: UDim2, roz: UDim2, kolor: Color3?, cyfry: boolean?)
	local t = nowy("TextLabel", { BackgroundTransparency = 1, Position = poz, Size = roz, Text = tekst, TextScaled = true,
		Font = if cyfry then self.cyfry else self.czcionka, TextColor3 = kolor or self.tusz, ZIndex = 11 }, rodzic)
	return t
end

function Okna:przycisk(rodzic: Instance, tekst: string, poz: UDim2, roz: UDim2, kolor: string, akcja: (() -> ())?)
	local b = nowy("TextButton", { Position = poz, Size = roz, BackgroundColor3 = hex(kolor), Text = tekst, TextScaled = true,
		Font = self.czcionka, TextColor3 = self.papier, AutoButtonColor = akcja ~= nil, ZIndex = 11 }, rodzic)
	rogi(b, 10)
	obrys(b, 2.5, self.tusz)
	tekstObrys(b, 2, self.tusz)
	nowy("UIPadding", { PaddingTop = UDim.new(0, 4), PaddingBottom = UDim.new(0, 4), PaddingLeft = UDim.new(0, 4),
		PaddingRight = UDim.new(0, 4) }, b)
	if akcja then
		b.Activated:Connect(akcja)
	end
	return b
end

-- sklep pałek: 4 × 2 karty (podgląd, nazwa, mnożnik, BUY / OWNED / EQUIPPED / LOCKED)
function Okna:sklep()
	local D, U, L = self.D, self.D.ui, self.L
	local _, tresc = self:okno("sklep", U.sklep, 580, 300)
	nowy("UIGridLayout", { CellSize = UDim2.fromOffset(134, 120), CellPadding = UDim2.fromOffset(6, 6),
		SortOrder = Enum.SortOrder.LayoutOrder }, tresc)
	local mam = tonumber(self.gracz:GetAttribute("BonkPalka")) or 0
	local monety = tonumber(self.gracz:GetAttribute("BonkMonety")) or 0
	for nr, P in D.palki do
		local k = karta(tresc, "Palka" .. nr, if nr <= mam then hex("FFF0C2") else hex("FFFFFF"), self.tusz, nr)
		podglad(k, self.wzorce, P.wzorzec, UDim2.new(1, 0, 0, 52), UDim2.fromOffset(0, 2), false)
		self:etykieta(k, P.nazwa, UDim2.fromOffset(4, 54), UDim2.new(1, -8, 0, 18))
		self:etykieta(k, string.format(U.mnoznik, L.mnoznikTekst(P.mnoznik)), UDim2.fromOffset(4, 72), UDim2.new(1, -8, 0, 14),
			hex(U.kolory.moc), true)
		local tekst, kolor, akcja = "", "9A9AA6", nil
		if nr == mam then
			tekst, kolor = U.w_dloni, "3DBE5A"
		elseif nr < mam then
			tekst, kolor = U.masz, "7A8C99"
		elseif nr == mam + 1 then
			tekst = U.kup .. " " .. L.format(P.cena)
			kolor = if monety >= P.cena then "FFB21C" else "B05A5A"
			akcja = function()
				if (tonumber(self.gracz:GetAttribute("BonkMonety")) or 0) < P.cena then
					self:toast(U.za_malo, "FF8A8A")
				else
					self.akcja("palka", nr)
				end
			end
		else
			tekst = U.zablokowane
		end
		local b = self:przycisk(k, tekst, UDim2.new(0, 6, 1, -30), UDim2.new(1, -12, 0, 26), kolor, nil)
		b.Name = "Przycisk"
		b.AutoButtonColor = false
		b.Selectable = false
		-- cała karta to jeden przycisk (palec / pad): 134 × 120 pt
		local klik = nowy("TextButton", { Name = "Karta", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "",
			ZIndex = 13, Selectable = true }, k)
		if akcja then
			klik.Activated:Connect(akcja)
		end
	end
end

-- pety: nagłówek (EQUIPPED n/3, mnożnik, AUTO BEST) i siatka posiadanych (klik = załóż / zdejmij jedną kopię)
function Okna:pety()
	local D, U, L = self.D, self.D.ui, self.L
	local _, tresc = self:okno("pety", U.pety, 580, 300)
	local mam = czytajPety(self.gracz:GetAttribute("BonkPetyMam"))
	local aktywne = czytajListe(self.gracz:GetAttribute("BonkPety"))
	local auto = self.gracz:GetAttribute("BonkAutoPety") ~= false
	local maks = D.petyUst.maks_aktywnych
	local gora = nowy("Frame", { BackgroundTransparency = 1, Size = UDim2.new(1, 0, 0, 44), ZIndex = 10 }, tresc)
	self:etykieta(gora, string.format(U.aktywne, #aktywne, maks), UDim2.fromOffset(0, 8), UDim2.fromOffset(170, 28))
	self:etykieta(gora, string.format(U.mnoznik, L.mnoznikTekst(tonumber(self.gracz:GetAttribute("BonkMnoznikPetow")) or 1)),
		UDim2.fromOffset(176, 10), UDim2.fromOffset(170, 24), hex(U.kolory.moc), true)
	local ba = self:przycisk(gora, U.auto, UDim2.new(1, -150, 0, 0), UDim2.fromOffset(150, 44), if auto then "3DBE5A" else "9A9AA6",
		function()
			self.akcja("auto", not auto)
		end)
	ba.Name = "Auto"
	local siatka = nowy("ScrollingFrame", { Name = "Siatka", BackgroundTransparency = 1, Position = UDim2.fromOffset(0, 50),
		Size = UDim2.new(1, 0, 1, -50), CanvasSize = UDim2.new(), AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollBarThickness = 6, BorderSizePixel = 0, ZIndex = 10 }, tresc)
	nowy("UIGridLayout", { CellSize = UDim2.fromOffset(102, 102), CellPadding = UDim2.fromOffset(6, 6),
		SortOrder = Enum.SortOrder.LayoutOrder }, siatka)
	local zalozone = {}
	for _, id in aktywne do
		zalozone[id] = (zalozone[id] or 0) + 1
	end
	local ile = 0
	for nr, id in D.petyKolejnosc do
		local n = mam[id]
		if n and n > 0 then
			ile += 1
			local P = D.pety[id]
			local R = D.rzadkosci[P.rzadkosc]
			local k = karta(siatka, "Pet_" .. id, if zalozone[id] then hex("D8F5D0") else hex("FFFFFF"), self.tusz, -nr)
			podglad(k, self.wzorce, P.wzorzec, UDim2.new(1, 0, 0, 58), UDim2.fromOffset(0, 2), false)
			self:etykieta(k, P.nazwa, UDim2.fromOffset(3, 60), UDim2.new(1, -6, 0, 16))
			self:etykieta(k, R.nazwa .. "  +" .. L.format(P.premia), UDim2.fromOffset(3, 77), UDim2.new(1, -6, 0, 13), hex(R.kolor))
			self:etykieta(k, string.format(U.kopie, n), UDim2.new(1, -40, 0, 2), UDim2.fromOffset(36, 16), self.tusz, true)
			if zalozone[id] then
				local z = nowy("TextLabel", { BackgroundColor3 = hex("3DBE5A"), Position = UDim2.fromOffset(4, 4), Size = UDim2.fromOffset(28, 18),
					Text = string.format("%d", zalozone[id]), TextScaled = true, Font = self.cyfry, TextColor3 = self.papier, ZIndex = 12 }, k)
				rogi(z, 6)
			end
			local b = nowy("TextButton", { Name = "Karta", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "", ZIndex = 13 }, k)
			b.Activated:Connect(function()
				self:przelaczPeta(id, aktywne, mam)
			end)
		end
	end
	if ile == 0 then
		self:etykieta(siatka, U.wyklij .. " " .. D.jajka[1].nazwa .. "!", UDim2.fromOffset(0, 40), UDim2.new(1, 0, 0, 40))
	end
end

-- ręczny wybór: klik na założonym zdejmuje jedną kopię, na niezałożonym zakłada (pełne — zastępuje najsłabszego)
function Okna:przelaczPeta(id: string, aktywne: { string }, mam: { [string]: number })
	local D = self.D
	local nowe = table.clone(aktywne)
	local zal = 0
	for _, x in nowe do
		if x == id then
			zal += 1
		end
	end
	if zal > 0 and (zal >= (mam[id] or 0) or #nowe >= D.petyUst.maks_aktywnych) then
		for i = #nowe, 1, -1 do
			if nowe[i] == id then
				table.remove(nowe, i)
				break
			end
		end
	else
		if #nowe >= D.petyUst.maks_aktywnych then
			local najslabszy, p = 1, math.huge
			for i, x in nowe do
				if D.pety[x].premia < p then
					najslabszy, p = i, D.pety[x].premia
				end
			end
			table.remove(nowe, najslabszy)
		end
		table.insert(nowe, id)
	end
	self.akcja("pety", nowe)
end

-- Księga petów: 3 rzędy (jajka) po 5, nieodkryte = czarna sylwetka i „???”, licznik „7/15”
function Okna:ksiega()
	local D, U = self.D, self.D.ui
	local odkryte = {}
	for _, id in czytajListe(self.gracz:GetAttribute("BonkKsiega")) do
		odkryte[id] = true
	end
	local n = 0
	for _, id in D.petyKolejnosc do
		if odkryte[id] then
			n += 1
		end
	end
	local _, tresc = self:okno("ksiega", string.format("%s  %d/%d", U.ksiega_tytul, n, #D.petyKolejnosc), 580, 316)
	self.licznikKsiegi = string.format("%d/%d", n, #D.petyKolejnosc)
	for r, J in D.jajka do
		local rzad = nowy("Frame", { Name = "Rzad" .. r, BackgroundTransparency = 1, Position = UDim2.fromOffset(0, (r - 1) * 86),
			Size = UDim2.new(1, 0, 0, 82), ZIndex = 10 }, tresc)
		self:etykieta(rzad, J.nazwa, UDim2.fromOffset(0, 26), UDim2.fromOffset(66, 26))
		for i, id in J.pety do
			local P = D.pety[id]
			local R = D.rzadkosci[P.rzadkosc]
			local jest = odkryte[id] == true
			local k = karta(rzad, "Pet_" .. id, if jest then hex("FFFFFF") else hex("D9D2C3"), self.tusz, i)
			k.Position = UDim2.fromOffset(72 + (i - 1) * 96, 0)
			k.Size = UDim2.fromOffset(90, 80)
			podglad(k, self.wzorce, P.wzorzec, UDim2.new(1, 0, 0, 52), UDim2.fromOffset(0, 2), not jest)
			self:etykieta(k, if jest then P.nazwa else U.nieznany, UDim2.fromOffset(3, 53), UDim2.new(1, -6, 0, 14))
			local pas = nowy("Frame", { BackgroundColor3 = hex(R.kolor), Position = UDim2.new(0, 6, 1, -10), Size = UDim2.new(1, -12, 0, 6),
				ZIndex = 11 }, k)
			rogi(pas, 3)
		end
	end
end

-- dzienny prezent: 7 dni, dzień serii podświetlony, CLAIM albo „wróć jutro”; opuszczony dzień nie zeruje serii
function Okna:prezent()
	local D, U, L = self.D, self.D.ui, self.L
	local _, tresc = self:okno("prezent", U.prezent_tytul, 560, 260)
	local mozna = self.gracz:GetAttribute("BonkPrezentMozna") == true
	local dzien = tonumber(self.gracz:GetAttribute("BonkPrezentDzien")) or 1
	local nagroda = tonumber(self.gracz:GetAttribute("BonkPrezentNagroda")) or 0
	local mk = nagroda / math.max(1, D.prezent.nagrody[dzien] or 1)
	for i, n in D.prezent.nagrody do
		local biez = i == dzien
		local k = karta(tresc, "Dzien" .. i, if biez then hex("FFE08A") elseif i < dzien then hex("E6E1D4") else hex("FFFFFF"),
			self.tusz, i)
		k.Position = UDim2.fromOffset((i - 1) * 76, 0)
		k.Size = UDim2.fromOffset(70, 84)
		self:etykieta(k, string.format(U.prezent_dzien, i), UDim2.fromOffset(4, 6), UDim2.new(1, -8, 0, 20))
		self:etykieta(k, L.format(n * mk), UDim2.fromOffset(4, 34), UDim2.new(1, -8, 0, 24), hex("C98A00"), true)
		self:etykieta(k, D.ui.monety, UDim2.fromOffset(4, 60), UDim2.new(1, -8, 0, 14))
	end
	self:etykieta(tresc, U.prezent_opis, UDim2.fromOffset(0, 94), UDim2.new(1, 0, 0, 24), hex("3D7A3D"))
	local b = self:przycisk(tresc, if mozna then U.odbierz .. "  +" .. L.format(nagroda) else U.prezent_jutro,
		UDim2.new(0.5, -130, 0, 128), UDim2.fromOffset(260, 56), if mozna then "3DBE5A" else "9A9AA6", if mozna then function()
			self.akcja("prezent", nil)
		end else nil)
	b.Name = "Odbierz"
end

function Okna:otworz(nazwa: string)
	if nazwa == "sklep" then
		self:sklep()
	elseif nazwa == "pety" then
		self:pety()
	elseif nazwa == "ksiega" then
		self:ksiega()
	elseif nazwa == "prezent" then
		self:prezent()
	end
	if self.padWlaczony and self.oknoRamka and not self.bezZaznaczenia then
		self:zaznacz()
	end
end

-- pad: pierwszy sensowny przycisk okna zaznaczony (krzyżak przesuwa, A klika); klucz = nazwa przycisku po odświeżeniu
function Okna:zaznacz(klucz: string?)
	local f = self.oknoRamka
	if not f then
		return
	end
	local cel: Instance? = nil
	if klucz then
		local o = f:FindFirstChild(klucz, true)
		if o and o:IsA("GuiButton") then
			cel = o
		end
	end
	if not cel and self.otwarte == "sklep" then
		local mam = tonumber(self.gracz:GetAttribute("BonkPalka")) or 0
		local k = f:FindFirstChild("Palka" .. math.min(#self.D.palki, mam + 1), true)
		cel = k and k:FindFirstChild("Karta")
	elseif not cel and self.otwarte == "pety" then
		cel = f:FindFirstChild("Auto", true)
	elseif not cel and self.otwarte == "prezent" then
		cel = f:FindFirstChild("Odbierz", true)
	end
	if not cel then
		cel = f:FindFirstChild("Zamknij")
	end
	pcall(function()
		GuiService.SelectedObject = cel
	end)
end

-- przycisk pada → true, gdy obsłużony (B zamyka, LB / RB / w górę — okna, Y — przycisk przy stoisku / inkubatorze)
function Okna:pad(kod: Enum.KeyCode): boolean
	if kod == Enum.KeyCode.ButtonB then
		if self.otwarte then
			self:zamknij()
			return true
		end
		return false
	end
	local nazwa = if kod == Enum.KeyCode.ButtonL1 then "pety" elseif kod == Enum.KeyCode.ButtonR1 then "ksiega"
		elseif kod == Enum.KeyCode.DPadUp then "prezent" else nil
	if nazwa then
		self:trybPada(true)
		if self.otwarte == nazwa then
			self:zamknij()
		else
			self:otworz(nazwa)
		end
		return true
	end
	if kod == Enum.KeyCode.ButtonY and self.kontekstRodzaj then
		self:trybPada(true)
		if self.kontekstRodzaj == "sklep" then
			if self.otwarte == "sklep" then
				self:zamknij()
			else
				self:otworz("sklep")
			end
		elseif self.kontekstRodzaj == "jajko" and self.kontekstNr then
			self.akcja("jajko", self.kontekstNr)
		end
		return true
	end
	return false
end

-- znaczki przycisków pada widać tylko przy grze na padzie
function Okna:trybPada(tak: boolean)
	if self.padWlaczony == tak then
		return
	end
	self.padWlaczony = tak
	for _, z in self.znaczki do
		z.Visible = tak
	end
	if self.oknoRamka then
		local zx = self.oknoRamka:FindFirstChild("ZnaczekPada", true)
		if zx then
			zx.Visible = tak
		end
	end
	if not tak then
		pcall(function()
			GuiService.SelectedObject = nil
		end)
	end
end

-- odświeżenie po zmianie atrybutów gracza: kropka prezentu, otwarte okno od nowa
function Okna:odswiez()
	self.kropka.Visible = self.gracz:GetAttribute("BonkPrezentMozna") == true
	if self.otwarte then
		local s = self.skalaOkna
		local nazwa = self.otwarte
		local zazn = GuiService.SelectedObject
		local klucz = nil
		if zazn and self.oknoRamka and zazn:IsDescendantOf(self.oknoRamka) then
			klucz = if zazn.Name == "Karta" and zazn.Parent then zazn.Parent.Name else zazn.Name
		end
		self.bezZaznaczenia = true -- bez zaznaczania w otworz: niżej po kluczu
		self:otworz(nazwa)
		self.bezZaznaczenia = false
		if self.padWlaczony and self.oknoRamka then
			local k = klucz and self.oknoRamka:FindFirstChild(klucz, true)
			if k and not k:IsA("GuiButton") then
				k = k:FindFirstChild("Karta")
			end
			if k and k:IsA("GuiButton") then
				pcall(function()
					GuiService.SelectedObject = k
				end)
			else
				self:zaznacz()
			end
		end
		if self.skalaOkna and s then
			self.skalaOkna.Scale = self.s or 1
		end
	end
	if self.kontekstRodzaj then
		self:kontekst(self.kontekstRodzaj, self.kontekstNr, true)
	end
end

------------------------------------------------------------------ przycisk kontekstu (stoisko / inkubator)
function Okna:kontekst(rodzaj: string?, nr: number?, wymus: boolean?)
	if rodzaj == self.kontekstRodzaj and nr == self.kontekstNr and not wymus then
		return
	end
	local D, U, L = self.D, self.D.ui, self.L
	self.kontekstRodzaj, self.kontekstNr = rodzaj, nr
	self.kontekstRamka.Visible = rodzaj ~= nil
	self.szanseRamka.Visible = rodzaj == "jajko"
	if rodzaj == nil and self.otwarte == "sklep" then
		self:zamknij()
	end
	if rodzaj == "sklep" then
		self.kontekstPrzycisk.Text = U.otworz_sklep
		self.kontekstPrzycisk.BackgroundColor3 = hex("FFB21C")
	elseif rodzaj == "jajko" and nr then
		local J = D.jajka[nr]
		local monety = tonumber(self.gracz:GetAttribute("BonkMonety")) or 0
		self.kontekstPrzycisk.Text = string.format("%s  %s", U.wyklij, L.format(J.cena))
		self.kontekstPrzycisk.BackgroundColor3 = if monety >= J.cena then hex("3DBE5A") else hex("B05A5A")
		for _, d in self.szanseLista:GetChildren() do
			if d:IsA("TextLabel") then
				d:Destroy()
			end
		end
		self.szanseRamka.Tytul.Text = J.nazwa .. " · " .. U.szanse
		for i, id in J.pety do
			local P = D.pety[id]
			local R = D.rzadkosci[i]
			local t = nowy("TextLabel", { Name = "Szansa" .. i, LayoutOrder = i, BackgroundTransparency = 1, Size = UDim2.new(1, 0, 0, 16),
				Text = string.format("%s — %s  %g%%", P.nazwa, R.nazwa, R.szansa * 100), TextScaled = true, Font = self.cyfry,
				TextColor3 = hex(R.kolor), TextXAlignment = Enum.TextXAlignment.Left }, self.szanseLista)
			tekstObrys(t, 1.5, self.tusz)
		end
	end
end

------------------------------------------------------------------ nakładki
function Okna:toast(tekst: string, kolor: string?)
	self.dymek.Text = tekst
	self.dymek.TextColor3 = if kolor then hex(kolor) else self.papier
	self.dymek.Visible = true
	self.dymek.TextTransparency = 0
	self.czasDymka = 0
end

function Okna:ogloszenie(tekst: string, kolor: string?)
	table.insert(self.kolejkaOgl, { tekst = tekst, kolor = kolor })
	if #self.kolejkaOgl > 4 then
		table.remove(self.kolejkaOgl, 1)
	end
end

-- napis bramy w stosie u góry (gracz przy zamkniętej bramie) albo nil
function Okna:brama(tekst: string?, kolor: string?)
	self.bramaRamka.Visible = tekst ~= nil
	if tekst then
		self.tekstBramy.Text = tekst
		self.obrysBramy.Color = if kolor then hex(kolor) else self.papier
	end
	self.bramaStan = tekst
end

-- dane: { nazwa, hp, hpMax, zywy, powrotZa } albo nil (gracz daleko od Strażnika)
function Okna:straznik(d)
	if not d then
		self.pasekStraznika.Visible = false
		self.straznikStan = nil
		return
	end
	self.pasekStraznika.Visible = true
	local L, U = self.L, self.D.ui
	self.nazwaStraznika.Text = d.nazwa
	if d.zywy then
		self.wypelnienieStraznika.Size = UDim2.new(math.clamp(d.hp / math.max(1, d.hpMax), 0, 1), -6, 1, -6)
		self.liczbyStraznika.Text = L.format(d.hp) .. " / " .. L.format(d.hpMax)
	else
		self.wypelnienieStraznika.Size = UDim2.new(0, 0, 1, -6)
		self.liczbyStraznika.Text = string.format(U.straznik_wroci, math.max(0, math.ceil(d.powrotZa or 0)))
	end
	self.straznikStan = { nazwa = d.nazwa, tekst = self.liczbyStraznika.Text, zywy = d.zywy }
end

-- scena wyklucia: tak → pokazana, pusta; zwraca ViewportFrame (model w środku układu, przodem do kamery) albo nil
function Okna:scena(tak: boolean): ViewportFrame?
	for _, d in self.vfWyklucia:GetChildren() do
		d:Destroy()
	end
	self.przyciemnienie.Visible = tak
	self.wyklucieRamka.Visible = tak
	self.napisWyklucia.Text, self.petWyklucia.Text = "", ""
	self.blyskWyklucia.BackgroundTransparency = 1
	if not tak then
		self.wyklucieStan = nil
		return nil
	end
	local kam = Instance.new("Camera")
	kam.FieldOfView = 30
	kam.CFrame = CFrame.lookAt(Vector3.new(0, 2.5, -13), Vector3.new(0, 2.3, 0))
	kam.Parent = self.vfWyklucia
	self.vfWyklucia.CurrentCamera = kam
	self.skalaWyklucia.Scale = (self.s or 1) * 0.5
	TweenService:Create(self.skalaWyklucia, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Scale = self.s or 1 }):Play()
	self.wyklucieStan = { scena = true }
	return self.vfWyklucia
end

-- błysk w kolorze rzadkości (pęknięcie jajka)
function Okna:blysk(kolor: string)
	local b = self.blyskWyklucia
	b.BackgroundColor3 = hex(kolor)
	b.BackgroundTransparency = 0.05
	b.Size = UDim2.fromOffset(40, 40)
	TweenService:Create(b, TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Size = UDim2.fromOffset(420, 420), BackgroundTransparency = 0.55 }):Play()
end

-- napisy wyklucia: d = { nowy, nazwa, rzadkosc (nazwa), kolor, kopie }
function Okna:wyklucie(d)
	if not d then
		self:scena(false)
		return
	end
	local U = self.D.ui
	self.napisWyklucia.Text = if d.nowy then U.nowy_pet else U.kopia .. "  " .. string.format(U.kopie, d.kopie)
	self.napisWyklucia.TextColor3 = if d.nowy then hex("FFC83D") else hex("9FD8FF")
	self.petWyklucia.Text = string.format("%s · %s", d.nazwa, d.rzadkosc)
	self.petWyklucia.TextColor3 = hex(d.kolor)
	self.wyklucieStan = { napis = self.napisWyklucia.Text, pet = self.petWyklucia.Text }
end

function Okna:krok(dt: number)
	if self.czasDymka >= 0 then
		self.czasDymka += dt
		local t = self.czasDymka
		self.dymek.TextTransparency = math.clamp((t - 1.6) / 0.5, 0, 1)
		if t > 2.1 then
			self.czasDymka = -1
			self.dymek.Visible = false
		end
	end
	if self.czasOgl >= 0 then
		self.czasOgl += dt
		if self.czasOgl > 4.2 then
			self.czasOgl = -1
			self.ogl.Visible = false
		end
	elseif #self.kolejkaOgl > 0 then
		local o = table.remove(self.kolejkaOgl, 1)
		self.tekstOgl.Text = o.tekst
		self.obrysOgl.Color = if o.kolor then hex(o.kolor) else self.papier
		self.ogl.Visible = true
		self.czasOgl = 0
		self.ostatnieOgl = o.tekst
		self.skalaOgl.Scale = (self.s or 1) * 0.6
		TweenService:Create(self.skalaOgl, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
			{ Scale = self.s or 1 }):Play()
	end
end

local function prostokat(o: GuiObject?): { number }?
	if not o then
		return nil
	end
	return { o.AbsolutePosition.X, o.AbsolutePosition.Y, o.AbsoluteSize.X, o.AbsoluteSize.Y }
end

function Okna:stan()
	local przyciski = {}
	for n, b in self.przyciski do
		przyciski[n] = prostokat(b)
	end
	local kart = 0
	if self.oknoRamka then
		for _, d in self.oknoRamka:GetDescendants() do
			if d:IsA("ViewportFrame") then
				kart += 1
			end
		end
	end
	-- wszystkie widoczne przyciski (do próby: ≥ 44 pt, w ekranie); przycisk z przezroczystym tłem = cała karta
	local guziki = {}
	for _, d in self.gui:GetDescendants() do
		if d:IsA("GuiButton") and d.Visible and d.Selectable and d.AbsoluteSize.X > 0 then
			local widac = true
			local o: Instance? = d.Parent
			while o and o ~= self.gui do
				if o:IsA("GuiObject") and not o.Visible then
					widac = false
					break
				end
				o = o.Parent
			end
			if widac and (d.BackgroundTransparency < 1 or d.Name == "Karta") then
				table.insert(guziki, { d.Name, d.AbsolutePosition.X, d.AbsolutePosition.Y, d.AbsoluteSize.X, d.AbsoluteSize.Y })
			end
		end
	end
	local zazn = GuiService.SelectedObject
	return {
		stos = {
			straznik = if self.pasekStraznika.Visible then prostokat(self.pasekStraznika) else nil,
			brama = if self.bramaRamka.Visible then prostokat(self.bramaRamka) else nil,
			ogloszenie = if self.ogl.Visible then prostokat(self.ogl) else nil,
			dymek = if self.dymek.Visible then prostokat(self.dymek) else nil,
			szanse = if self.szanseRamka.Visible and self.kontekstRamka.Visible then prostokat(self.szanseRamka) else nil,
			kontekst = if self.kontekstRamka.Visible then prostokat(self.kontekstPrzycisk) else nil,
		},
		guziki = guziki, pad = self.padWlaczony == true, zaznaczony = if zazn then zazn.Name else nil, brama = self.bramaStan,
		otwarte = self.otwarte, okno = prostokat(self.oknoRamka), przyciski = przyciski, kropka = self.kropka.Visible,
		kontekst = self.kontekstRodzaj, kontekstNr = self.kontekstNr, kontekstPoz = if self.kontekstRodzaj then prostokat(self.kontekstPrzycisk) else nil,
		szanse = if self.szanseRamka.Visible then prostokat(self.szanseRamka) else nil, podgladow = kart,
		straznik = self.straznikStan, wyklucie = self.wyklucieStan, ogloszenie = self.ostatnieOgl, ksiega = self.licznikKsiegi,
		ekran = prostokat(if self.ekran:IsA("GuiObject") then self.ekran else nil),
	}
end

function Okna:zniszcz()
	if self.polaczenie then
		self.polaczenie:Disconnect()
	end
	self.gui:Destroy()
end

return Okna
