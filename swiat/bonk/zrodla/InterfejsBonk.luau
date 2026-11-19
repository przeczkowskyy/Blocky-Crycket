--[[
	InterfejsBonk — ekran gracza w BONK (ModuleScript w Workspace/BonkGra/Moduly). Tylko to, co w projekcie etapu 1:
	Moc i monety na górze, przycisk BONK (telefon: duży, prawy dolny róg, nad skokiem; komputer: mniejszy, z podpowiedzią
	„E”), trzy krótkie podpowiedzi startowe, nazwa krainy przy wejściu, napis HOME RUN!. Teksty po angielsku (D-045).

	Ekran (ScreenGui „BonkEkran”) leży w folderze PlayerGui/BonkUI — nie bezpośrednio w PlayerGui, bo ekran wyboru klasy
	obecnej gry wyłącza każdy nowy ScreenGui dodany wprost do PlayerGui. Skala z rozmiaru okna (wzór: 667 × 375).

	Użycie: local ui = Interfejs.nowy(rodzic, D, L, { dotyk = bool })
		ui:moc(n, przyrost?)  ui:monety(n, przyrost?)  ui:podpowiedz(i | nil)  ui:kraina(nazwa)  ui:homeRun()
		ui.przycisk (TextButton)  ui:krok(dt)  ui:stan() → tabela do prób  ui:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local TweenService = game:GetService("TweenService")

local Interfejs = {}
Interfejs.__index = Interfejs

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

function Interfejs.nowy(rodzic: Instance, D, L, opcje)
	local self = setmetatable({}, Interfejs)
	self.D, self.L = D, L
	self.dotyk = opcje and opcje.dotyk == true
	local U = D.ui
	local K = U.kolory
	local tusz = Color3.fromHex(K.tusz)
	local papier = Color3.fromHex(K.papier)
	local czcionka = Enum.Font[U.czcionka] or Enum.Font.LuckiestGuy
	local cyfry = Enum.Font[U.czcionka_cyfr] or Enum.Font.FredokaOne
	self.tusz, self.czcionka = tusz, czcionka

	local ekranGui = nowy("ScreenGui", { Name = "BonkEkran", ResetOnSpawn = false, IgnoreGuiInset = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling, DisplayOrder = 5 }, rodzic)
	self.ekran = ekranGui
	local ekran: Instance = ekranGui
	local emulacja = opcje and opcje.emulacja
	if emulacja then
		-- próby: prostokąt telefonu (punkty) na środku okna; wszystko w nim, jak na telefonie
		ekran = nowy("Frame", { Name = "EmulacjaTelefonu", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromOffset(emulacja.X, emulacja.Y), BackgroundTransparency = 1, ClipsDescendants = true }, ekranGui)
		obrys(ekran, 2, Color3.fromRGB(255, 255, 255))
	end
	self.okno = ekran

	-- skala: wzór 667 × 375 (telefon poziomo) → 1; większe okna większe elementy (do 1,5)
	local kamera = workspace.CurrentCamera
	local function skala(): number
		local v = if emulacja then emulacja else kamera.ViewportSize
		return math.clamp(math.min(v.X / 667, v.Y / 375), 0.8, 1.5)
	end

	------------------------------------------------------------ góra: Moc i monety
	local gora = nowy("Frame", { Name = "Gora", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 6), Size = UDim2.fromOffset(330, 44) }, ekran)
	self.skalaGory = nowy("UIScale", {}, gora)
	nowy("UIListLayout", { FillDirection = Enum.FillDirection.Horizontal, HorizontalAlignment = Enum.HorizontalAlignment.Center,
		Padding = UDim.new(0, 10), SortOrder = Enum.SortOrder.LayoutOrder }, gora)
	local function pigulka(nazwa: string, etykieta: string, kolor: Color3, kolejnosc: number)
		local f = nowy("Frame", { Name = nazwa, LayoutOrder = kolejnosc, BackgroundColor3 = kolor, Size = UDim2.fromOffset(158, 42) }, gora)
		nowy("UICorner", { CornerRadius = UDim.new(0.5, 0) }, f)
		obrys(f, 3, tusz)
		nowy("TextLabel", { Name = "Etykieta", BackgroundTransparency = 1, Position = UDim2.fromOffset(12, 2),
			Size = UDim2.new(0, 60, 1, -4), Text = etykieta, TextScaled = true, Font = czcionka, TextColor3 = papier,
			TextXAlignment = Enum.TextXAlignment.Left }, f)
		local w = nowy("TextLabel", { Name = "Wartosc", BackgroundTransparency = 1, Position = UDim2.new(0, 70, 0, 3),
			Size = UDim2.new(1, -80, 1, -6), Text = "0", TextScaled = true, Font = cyfry, TextColor3 = papier,
			TextXAlignment = Enum.TextXAlignment.Right }, f)
		tekstObrys(w, 2, tusz)
		local s = nowy("UIScale", {}, f)
		return f, w, s
	end
	self.ramkaMocy, self.wartoscMocy, self.skalaMocy = pigulka("Moc", U.moc, Color3.fromHex(K.moc), 1)
	self.ramkaMonet, self.wartoscMonet, self.skalaMonet = pigulka("Monety", U.monety, Color3.fromHex(K.monety), 2)

	------------------------------------------------------------ podpowiedź (pod górą)
	local pod = nowy("Frame", { Name = "Podpowiedz", AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 0, 58),
		Size = UDim2.fromOffset(330, 34), BackgroundColor3 = papier, Visible = false }, ekran)
	nowy("UICorner", { CornerRadius = UDim.new(0, 10) }, pod)
	obrys(pod, 2.5, tusz)
	self.skalaPodpowiedzi = nowy("UIScale", {}, pod)
	self.tekstPodpowiedzi = nowy("TextLabel", { BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 3),
		Size = UDim2.new(1, -20, 1, -6), TextScaled = true, Font = czcionka, TextColor3 = tusz, Text = "" }, pod)
	self.podpowiedzRamka = pod

	------------------------------------------------------------ nazwa krainy (środek, znika)
	local kr = nowy("TextLabel", { Name = "Kraina", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.3),
		Size = UDim2.fromOffset(420, 70), BackgroundTransparency = 1, Text = "", TextScaled = true, Font = czcionka,
		TextColor3 = papier, TextTransparency = 1 }, ekran)
	self.obrysKrainy = tekstObrys(kr, 4, tusz)
	self.obrysKrainy.Transparency = 1
	self.skalaKrainy = nowy("UIScale", {}, kr)
	self.napisKrainy = kr

	------------------------------------------------------------ HOME RUN! (środek)
	local hr = nowy("TextLabel", { Name = "HomeRun", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.42),
		Size = UDim2.fromOffset(460, 90), BackgroundTransparency = 1, Text = U.home_run, TextScaled = true, Font = czcionka,
		TextColor3 = Color3.fromHex(K.monety), Visible = false, Rotation = -6 }, ekran)
	tekstObrys(hr, 5, tusz)
	self.skalaHr = nowy("UIScale", {}, hr)
	self.napisHr = hr

	------------------------------------------------------------ przycisk BONK
	local rozm = if self.dotyk then 104 else 84
	local b = nowy("TextButton", { Name = "PrzyciskBonk", AnchorPoint = Vector2.new(1, 1),
		Position = if self.dotyk then UDim2.new(1, -112, 1, -96) else UDim2.new(1, -24, 1, -28),
		Size = UDim2.fromOffset(rozm, rozm), BackgroundColor3 = Color3.fromHex(K.przycisk), AutoButtonColor = false,
		Text = U.przycisk, TextScaled = true, Font = czcionka, TextColor3 = papier }, ekran)
	nowy("UICorner", { CornerRadius = UDim.new(0.5, 0) }, b)
	obrys(b, 4, tusz)
	tekstObrys(b, 2.5, tusz)
	nowy("UIPadding", { PaddingLeft = UDim.new(0.14, 0), PaddingRight = UDim.new(0.14, 0), PaddingTop = UDim.new(0.24, 0),
		PaddingBottom = UDim.new(0.24, 0) }, b)
	self.skalaPrzycisku = nowy("UIScale", {}, b)
	self.przycisk = b
	if not self.dotyk then
		local e = nowy("TextLabel", { Name = "KlawiszE", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 1, 14),
			Size = UDim2.fromOffset(34, 34), BackgroundColor3 = papier, Text = "E", TextScaled = true, Font = czcionka,
			TextColor3 = tusz }, b)
		nowy("UICorner", { CornerRadius = UDim.new(0.3, 0) }, e)
		obrys(e, 2.5, tusz)
	end

	self.przyrosty = {}
	self.wcisniety = 0
	self.czasKrainy, self.czasHr = -1, -1
	self.zegar = 0
	self.wartosci = { moc = -1, monety = -1 }
	local function przeskaluj()
		local s = skala()
		for _, u in { self.skalaGory, self.skalaPodpowiedzi, self.skalaKrainy, self.skalaHr, self.skalaPrzycisku } do
			u.Scale = s
		end
		self.s = s
	end
	przeskaluj()
	self.polaczenie = kamera:GetPropertyChangedSignal("ViewportSize"):Connect(przeskaluj)
	return self
end

-- „+12” przy liczbie, unosi się i gaśnie
function Interfejs:przyrost(ramka: Frame, tekst: string, kolor: Color3)
	local t = nowy("TextLabel", { BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0), Position = UDim2.new(0.5, 0, 1, 2),
		Size = UDim2.fromOffset(120, 28), Text = tekst, TextScaled = true, Font = self.czcionka, TextColor3 = kolor }, ramka)
	tekstObrys(t, 2, self.tusz)
	table.insert(self.przyrosty, { o = t, t = 0 })
end

local function puls(s: UIScale)
	s.Scale = 1.18
	TweenService:Create(s, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

function Interfejs:moc(n: number, przyrost: number?)
	if self.wartosci.moc ~= n then
		self.wartosci.moc = n
		self.wartoscMocy.Text = self.L.format(n)
	end
	if przyrost and przyrost > 0 then
		puls(self.skalaMocy)
		self:przyrost(self.ramkaMocy, "+" .. self.L.format(przyrost), Color3.fromHex(self.D.ui.kolory.moc))
	end
end

function Interfejs:monety(n: number, przyrost: number?)
	if self.wartosci.monety ~= n then
		self.wartosci.monety = n
		self.wartoscMonet.Text = self.L.format(n)
	end
	if przyrost and przyrost > 0 then
		puls(self.skalaMonet)
		self:przyrost(self.ramkaMonet, "+" .. self.L.format(przyrost), Color3.fromHex(self.D.ui.kolory.monety))
	end
end

-- i = 1…3 (teksty z danych; druga zależy od urządzenia), nil = schowaj
function Interfejs:podpowiedz(i: number?)
	if self.nrPodpowiedzi == i then
		return
	end
	self.nrPodpowiedzi = i
	if not i then
		self.podpowiedzRamka.Visible = false
		return
	end
	local U = self.D.ui
	local tekst = U.podpowiedzi[i]
	if i == 2 and not self.dotyk then
		tekst = U.podpowiedz_pc
	end
	self.tekstPodpowiedzi.Text = tekst
	self.podpowiedzRamka.Visible = true
	self.skalaPodpowiedzi.Scale = (self.s or 1) * 0.6
	TweenService:Create(self.skalaPodpowiedzi, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
		{ Scale = self.s or 1 }):Play()
end

function Interfejs:kraina(nazwa: string)
	self.napisKrainy.Text = nazwa
	self.czasKrainy = 0
end

function Interfejs:homeRun()
	self.czasHr = 0
	self.napisHr.Visible = true
end

-- naciśnięty przycisk (wygląd), ustawia klient
function Interfejs:wcisnij(tak: boolean)
	self.przycisk.BackgroundColor3 = if tak then Color3.fromHex(self.D.ui.kolory.przycisk_cien) else Color3.fromHex(self.D.ui.kolory.przycisk)
	if tak then
		self.skalaPrzycisku.Scale = (self.s or 1) * 0.92
	else
		self.skalaPrzycisku.Scale = self.s or 1
	end
end

function Interfejs:krok(dt: number)
	local i = 1
	while i <= #self.przyrosty do
		local p = self.przyrosty[i]
		p.t += dt
		local f = p.t / 0.9
		if f >= 1 then
			p.o:Destroy()
			table.remove(self.przyrosty, i)
		else
			p.o.Position = UDim2.new(0.5, 0, 1, 2 + f * 22)
			p.o.TextTransparency = math.clamp((f - 0.5) / 0.5, 0, 1)
			i += 1
		end
	end
	if self.czasKrainy >= 0 then
		self.czasKrainy += dt
		local t = self.czasKrainy
		local wid = if t < 0.3 then t / 0.3 elseif t < 2.3 then 1 else 1 - (t - 2.3) / 0.6
		wid = math.clamp(wid, 0, 1)
		self.napisKrainy.TextTransparency = 1 - wid
		self.obrysKrainy.Transparency = 1 - wid
		self.skalaKrainy.Scale = (self.s or 1) * (0.85 + 0.15 * math.min(1, t / 0.3))
		if t > 2.9 then
			self.czasKrainy = -1
		end
	end
	if self.czasHr >= 0 then
		self.czasHr += dt
		local t = self.czasHr
		local s = if t < 0.15 then 0.3 + t / 0.15 * 1.0 elseif t < 0.3 then 1.3 - (t - 0.15) / 0.15 * 0.3 else 1
		self.skalaHr.Scale = (self.s or 1) * s
		self.napisHr.TextTransparency = math.clamp((t - 1.1) / 0.4, 0, 1)
		if t > 1.5 then
			self.czasHr = -1
			self.napisHr.Visible = false
		end
	end
end

function Interfejs:stan()
	return {
		moc = self.wartoscMocy.Text, monety = self.wartoscMonet.Text,
		podpowiedz = if self.podpowiedzRamka.Visible then self.tekstPodpowiedzi.Text else nil,
		przycisk = self.przycisk.Visible and self.ekran.Enabled, dotyk = self.dotyk, skala = self.s,
		okno = { self.okno.AbsolutePosition.X, self.okno.AbsolutePosition.Y, self.okno.AbsoluteSize.X, self.okno.AbsoluteSize.Y },
		przyciskPoz = { self.przycisk.AbsolutePosition.X, self.przycisk.AbsolutePosition.Y,
			self.przycisk.AbsoluteSize.X, self.przycisk.AbsoluteSize.Y },
		goraPoz = { self.ramkaMocy.AbsolutePosition.X, self.ramkaMocy.AbsolutePosition.Y,
			self.ramkaMonet.AbsolutePosition.X + self.ramkaMonet.AbsoluteSize.X, self.ramkaMocy.AbsoluteSize.Y },
		kraina = if self.czasKrainy >= 0 then self.napisKrainy.Text else nil,
	}
end

function Interfejs:zniszcz()
	if self.polaczenie then
		self.polaczenie:Disconnect()
	end
	self.ekran:Destroy()
end

return Interfejs
