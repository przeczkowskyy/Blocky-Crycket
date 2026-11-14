--[[
	WyborWalki2 — komiksowy panel wyboru walki przy tablicy (PlayerGui, tworzony w czasie działania).
	Klasa (Wojownik / Zwiadowca / Mag), przeciwnik (pięć pozycji lasu z rangą), poziom (1 / 5 / 10) i duży przycisk
	WALCZ. Duże przyciski i kadr trzymający proporcje — czytelny także na telefonie.

	Panel NIE liczy niczego i nie wysyła liczb: wybór to trzy napisy z zamkniętej listy (klucz klasy, id przeciwnika,
	poziom jako napis "1" / "5" / "10"), który serwer jeszcze raz sprawdza z własną listą.

	API:
		WyborWalki2.pokaz(playerGui, opcje) → panel
			opcje.naWalcz(wybor)  — WALCZ (wybor = { klasa, przeciwnik, poziom })
			opcje.naZamknij()     — krzyżyk albo odejście od tablicy
			opcje.wolnaZa()       — ile sekund do następnej walki (odliczanie na przycisku)
		panel:komunikat(tekst?)  panel:zamknij()   WyborWalki2.otwarty() → panel | nil
	Emulacja ekranu telefonu do testów: atrybut kontenera EmulacjaEkranu (patrz InterfejsWalki2.ekran).
	Ostatni wybór jest pamiętany do końca sesji.
	Nazwy przycisków (dla testów): Ekran.Karta.Klasy.Klasa_<klucz>, Ekran.Karta.Wrogowie.Wrog_<id>,
	Ekran.Karta.Poziomy.Poziom_<n>, Ekran.Karta.Walcz.Przycisk, Ekran.Karta.Zamknij.
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local TweenService = game:GetService("TweenService")

local moduly = script.Parent
local Ustawienia = require(moduly:WaitForChild("Ustawienia"))
local Aktorzy = require(moduly:WaitForChild("Aktorzy"))
local Interfejs = require(moduly:WaitForChild("InterfejsWalki2"))
local Dane = require(moduly:WaitForChild("Walka"):WaitForChild("Dane"))

local K = Ustawienia.KOLORY
local NAGLOWKI = Enum.Font.LuckiestGuy
local KOMIKS = Enum.Font.Bangers

local Wybor = {}
local Panel = {}
Panel.__index = Panel

local otwarty = nil
local pamiec = { klasa = "wojownik", przeciwnik = "lesny_slime", poziom = "5" }

local RANGI = { zwykly = { "ZWYKŁY", "#8D93A6" }, rzadki = { "RZADKI", "#2F6FE0" }, straznik = { "STRAŻNIK", "#E8364F" } }
local POZIOMY = { "1", "5", "10" }

function Panel:_nowy(klasa: string, w: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in w do
		o[k] = v
	end
	o.Parent = rodzic
	return o
end

function Panel:_obrys(o: GuiObject, px: number)
	local jestTekstem = o:IsA("TextLabel") or o:IsA("TextButton")
	local s = self:_nowy("UIStroke", { Color = K.tusz, Thickness = px, LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = if jestTekstem then Enum.ApplyStrokeMode.Contextual else Enum.ApplyStrokeMode.Border }, o)
	table.insert(self.obrysy, { s, px })
	return s
end

function Panel:_tekst(rodzic: Instance, w: { [string]: any }, obrys: number?)
	local t = self:_nowy("TextLabel", w, rodzic)
	t.BackgroundTransparency = 1
	t.TextScaled = true
	if obrys and obrys > 0 then
		self:_obrys(t, obrys)
	end
	return t
end

function Panel:_ikona(rodzic: GuiObject, nazwa: string, w: { [string]: any })
	local def = Interfejs.IKONY[nazwa] or Interfejs.IKONY.oko
	local pole = self:_nowy("Frame", w, rodzic)
	pole.BackgroundTransparency = 1
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
				self:_nowy("Frame", { BackgroundColor3 = Color3.fromHex(def.paleta[znak] or "#FF00FF"), BorderSizePixel = 0,
					Position = UDim2.fromScale((x - 1) / 8, (y - 1) / 8), Size = UDim2.fromScale((koniec - x + 1) / 8 + 0.004, 1 / 8 + 0.004),
					ZIndex = pole.ZIndex }, pole)
			end
			x = koniec + 1
		end
	end
	return pole
end

-- przycisk opcji: ikona z lewej, nazwa, podpis; zaznaczony = żółty
function Panel:_opcja(rodzic: Instance, nazwa: string, ikona: string?, tytul: string, podpis: string?, w: { [string]: any })
	local b = self:_nowy("TextButton", { Name = nazwa, AutoButtonColor = false, BackgroundColor3 = K.bialy, BorderSizePixel = 0,
		Text = "", Size = w.Size, Position = w.Position, AnchorPoint = w.AnchorPoint or Vector2.zero, ZIndex = 5,
		Rotation = w.Rotation or 0 }, rodzic)
	self:_nowy("UICorner", { CornerRadius = UDim.new(0.14, 0) }, b)
	self:_obrys(b, 4)
	local lewo = 0.06
	if ikona then
		self:_ikona(b, ikona, { Name = "Ikona", AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.fromScale(0.05, 0.5),
			Size = UDim2.fromScale(0.8, 0.72), SizeConstraint = Enum.SizeConstraint.RelativeYY, ZIndex = 6 })
		lewo = 0.36
	end
	self:_tekst(b, { Name = "Tytul", Position = UDim2.fromScale(lewo, if podpis then 0.1 else 0.18), Size = UDim2.fromScale(0.96 - lewo, if podpis then 0.5 else 0.64),
		Font = NAGLOWKI, Text = tytul, TextColor3 = K.tusz, TextXAlignment = if ikona then Enum.TextXAlignment.Left else Enum.TextXAlignment.Center,
		ZIndex = 6 }, 0)
	if podpis then
		self:_tekst(b, { Name = "Podpis", Position = UDim2.fromScale(lewo, 0.6), Size = UDim2.fromScale(0.96 - lewo, 0.3),
			Font = KOMIKS, Text = podpis, TextColor3 = K.szary, TextXAlignment = if ikona then Enum.TextXAlignment.Left else Enum.TextXAlignment.Center,
			ZIndex = 6 }, 0)
	end
	local skala = self:_nowy("UIScale", { Scale = 1 }, b)
	table.insert(self.polaczenia, b.MouseEnter:Connect(function()
		TweenService:Create(skala, TweenInfo.new(0.1), { Scale = 1.05 }):Play()
	end))
	table.insert(self.polaczenia, b.MouseLeave:Connect(function()
		TweenService:Create(skala, TweenInfo.new(0.1), { Scale = 1 }):Play()
	end))
	return b
end

function Panel:_naglowekRzedu(rodzic: Instance, tekst: string, y: number)
	self:_tekst(rodzic, { Name = "Naglowek", Position = UDim2.fromScale(0.035, y), Size = UDim2.fromScale(0.3, 0.06), Font = NAGLOWKI,
		Text = tekst, TextColor3 = K.niebieski, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 4 }, 0)
end

function Panel:_odswiez()
	for klucz, b in self.klasy do
		b.BackgroundColor3 = if klucz == self.wybor.klasa then K.zolty else K.bialy
		b:SetAttribute("Wybrany", klucz == self.wybor.klasa)
	end
	for id, b in self.wrogowie do
		b.BackgroundColor3 = if id == self.wybor.przeciwnik then K.zolty else K.bialy
		b:SetAttribute("Wybrany", id == self.wybor.przeciwnik)
	end
	for p, b in self.poziomy do
		b.BackgroundColor3 = if p == self.wybor.poziom then K.zolty else K.bialy
		b:SetAttribute("Wybrany", p == self.wybor.poziom)
	end
	local wk = Aktorzy.wpis(self.wybor.klasa)
	local ww = Aktorzy.wpis(self.wybor.przeciwnik)
	self.podsumowanie.Text = string.format("%s poz. %s  kontra  %s poz. %s%s", wk and wk.nazwa or "?", self.wybor.poziom,
		ww and ww.nazwa or "?", self.wybor.poziom, if ww and ww.zastepczy then " (model zastępczy)" else "")
end

function Panel:_przelicz()
	-- ekran (cały albo emulowany telefon — atrybut EmulacjaEkranu, patrz InterfejsWalki2.ekran)
	local ox, oy, sz, wys = Interfejs.ekran()
	self.ekran.Position = UDim2.fromOffset(ox, oy)
	self.ekran.Size = UDim2.fromOffset(sz, wys)
	local skala = math.max(0.4, wys / 720)
	for _, o in self.obrysy do
		if o[1].Parent then
			o[1].Thickness = math.max(1, o[2] * skala)
		end
	end
end

function Wybor.pokaz(playerGui: Instance, opcje)
	if otwarty then
		otwarty:zamknij()
	end
	local self = setmetatable({}, Panel)
	self.opcje = opcje or {}
	self.obrysy = {}
	self.polaczenia = {}
	self.wybor = table.clone(pamiec)
	self.klasy, self.wrogowie, self.poziomy = {}, {}, {}

	local gui = self:_nowy("ScreenGui", { Name = "TestWalki2Wybor", IgnoreGuiInset = true, ResetOnSpawn = false, DisplayOrder = 102,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, nil)
	self.gui = gui
	self:_nowy("Frame", { Name = "Tlo", BackgroundColor3 = K.tusz, BackgroundTransparency = 0.45, BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1), ZIndex = 1 }, gui)
	local ekran = self:_nowy("Frame", { Name = "Ekran", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), ZIndex = 1 }, gui)
	self.ekran = ekran
	local karta = self:_nowy("Frame", { Name = "Karta", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52),
		Size = UDim2.fromScale(0.96, 0.92), BackgroundColor3 = K.krem, BorderSizePixel = 0, Rotation = -0.6, ZIndex = 2 }, ekran)
	self:_nowy("UIAspectRatioConstraint", { AspectRatio = 1.72 }, karta)
	self:_nowy("UICorner", { CornerRadius = UDim.new(0.04, 0) }, karta)
	self:_obrys(karta, 6)
	self.karta = karta
	self.skalaKarty = self:_nowy("UIScale", { Scale = 0.6 }, karta)

	-- wstęga z tytułem
	local wstega = self:_nowy("Frame", { Name = "Wstega", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.02),
		Size = UDim2.fromScale(0.62, 0.12), BackgroundColor3 = K.zielony, BorderSizePixel = 0, Rotation = 1.2, ZIndex = 3 }, karta)
	self:_nowy("UICorner", { CornerRadius = UDim.new(0.2, 0) }, wstega)
	self:_obrys(wstega, 5)
	self:_tekst(wstega, { Name = "Tytul", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52), Size = UDim2.fromScale(0.92, 0.78),
		Font = NAGLOWKI, Text = "WALKA v2 — WYBIERZ!", TextColor3 = K.bialy, ZIndex = 4 }, 5)

	-- zamknij (krzyżyk)
	local x = self:_nowy("TextButton", { Name = "Zamknij", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.975, 0.03),
		Size = UDim2.fromScale(0.09, 0.09), SizeConstraint = Enum.SizeConstraint.RelativeYY, BackgroundColor3 = K.czerwony, BorderSizePixel = 0,
		Text = "X", Font = NAGLOWKI, TextScaled = true, TextColor3 = K.bialy, AutoButtonColor = false, ZIndex = 6 }, karta)
	self:_nowy("UICorner", { CornerRadius = UDim.new(0.3, 0) }, x)
	self:_obrys(x, 4)
	table.insert(self.polaczenia, x.Activated:Connect(function()
		self:zamknij()
		if self.opcje.naZamknij then
			self.opcje.naZamknij()
		end
	end))

	-- Układ dobrany do telefonu w poziomie (844 × 390 i 667 × 375 punktów, testy/telefon.py): każdy napis ma co
	-- najmniej ok. 12 punktów wysokości — podpisy idą pełną szerokością przycisku pod nazwą, nie obok ikony.
	-- KLASA
	self:_naglowekRzedu(karta, "TWOJA KLASA", 0.095)
	local rzadK = self:_nowy("Frame", { Name = "Klasy", BackgroundTransparency = 1, Position = UDim2.fromScale(0.035, 0.155),
		Size = UDim2.fromScale(0.93, 0.17), ZIndex = 3 }, karta)
	local klasy = {}
	for _, klucz in Aktorzy.kolejnosc do
		local w = Aktorzy.wpis(klucz)
		if w.rola == "klasa" then
			table.insert(klasy, klucz)
		end
	end
	for i, klucz in klasy do
		local w = Aktorzy.wpis(klucz)
		local styl = Dane.klasy[klucz] and Dane.klasy[klucz].styl or ""
		local b = self:_opcja(rzadK, "Klasa_" .. klucz, klucz, string.upper(w.nazwa), styl, {
			Position = UDim2.fromScale((i - 1) * 0.3367, 0), Size = UDim2.fromScale(0.315, 1), Rotation = ({ -1, 0.8, -0.6 })[i] or 0 })
		-- ikona i nazwa u góry, styl klasy pełną szerokością pod spodem (na telefonie obok ikony był za drobny)
		local ik, t, p = b:FindFirstChild("Ikona"), b:FindFirstChild("Tytul"), b:FindFirstChild("Podpis")
		if ik then
			ik.Position, ik.Size = UDim2.fromScale(0.04, 0.35), UDim2.fromScale(0.56, 0.56)
		end
		if t then
			t.Position, t.Size = UDim2.fromScale(0.27, 0.07), UDim2.fromScale(0.7, 0.52)
		end
		if p then
			p.Position, p.Size, p.TextXAlignment = UDim2.fromScale(0.04, 0.64), UDim2.fromScale(0.92, 0.31), Enum.TextXAlignment.Center
		end
		self.klasy[klucz] = b
		table.insert(self.polaczenia, b.Activated:Connect(function()
			self.wybor.klasa = klucz
			self:_odswiez()
		end))
	end

	-- PRZECIWNIK
	self:_naglowekRzedu(karta, "PRZECIWNIK (LAS)", 0.343)
	local rzadW = self:_nowy("Frame", { Name = "Wrogowie", BackgroundTransparency = 1, Position = UDim2.fromScale(0.035, 0.403),
		Size = UDim2.fromScale(0.93, 0.25), ZIndex = 3 }, karta)
	for i, d in Dane.przeciwnicy do
		local w = Aktorzy.wpis(d.id)
		local r = RANGI[d.ranga] or RANGI.zwykly
		local b = self:_opcja(rzadW, "Wrog_" .. d.id, if w then d.id else nil, string.upper(d.nazwa), r[1], {
			Position = UDim2.fromScale((i - 1) * 0.2014, 0), Size = UDim2.fromScale(0.19, 1), Rotation = ({ 0.8, -0.8, 0.6, -1, 1 })[i] or 0 })
		local pasek = self:_nowy("Frame", { Name = "Ranga", AnchorPoint = Vector2.new(0.5, 1), Position = UDim2.fromScale(0.5, 1),
			Size = UDim2.fromScale(1, 0.08), BackgroundColor3 = Color3.fromHex(r[2]), BorderSizePixel = 0, ZIndex = 6 }, b)
		self:_nowy("UICorner", { CornerRadius = UDim.new(0.5, 0) }, pasek)
		-- w wąskim przycisku ikona idzie nad nazwę; nazwa może zawinąć się na dwa wiersze (Cierniowy / Wilk)
		local ik = b:FindFirstChild("Ikona")
		if ik then
			ik.AnchorPoint = Vector2.new(0.5, 0)
			ik.Position = UDim2.fromScale(0.5, 0.04)
			ik.Size = UDim2.fromScale(0.36, 0.36)
		end
		local t, p = b:FindFirstChild("Tytul"), b:FindFirstChild("Podpis")
		if t then
			t.Position, t.Size, t.TextXAlignment = UDim2.fromScale(0.04, 0.41), UDim2.fromScale(0.92, 0.28), Enum.TextXAlignment.Center
			t.TextWrapped = true
		end
		if p then
			p.Position, p.Size, p.TextXAlignment = UDim2.fromScale(0.04, 0.7), UDim2.fromScale(0.92, 0.19), Enum.TextXAlignment.Center
		end
		-- model zastępczy: naklejka nad ikoną (dawniej drobny dopisek w podpisie)
		if w and w.zastepczy then
			local nalepka = self:_nowy("Frame", { Name = "Zastepczy", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.01),
				Size = UDim2.fromScale(0.86, 0.17), BackgroundColor3 = K.zolty, BorderSizePixel = 0, Rotation = -4, ZIndex = 8 }, b)
			self:_nowy("UICorner", { CornerRadius = UDim.new(0.3, 0) }, nalepka)
			self:_obrys(nalepka, 2)
			self:_tekst(nalepka, { Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52),
				Size = UDim2.fromScale(0.92, 0.84), Font = KOMIKS, Text = "ZASTĘPCZY", TextColor3 = K.tusz, ZIndex = 9 }, 0)
		end
		self.wrogowie[d.id] = b
		table.insert(self.polaczenia, b.Activated:Connect(function()
			self.wybor.przeciwnik = d.id
			self:_odswiez()
		end))
	end

	-- POZIOM
	self:_naglowekRzedu(karta, "POZIOM (OBU STRON)", 0.672)
	local rzadP = self:_nowy("Frame", { Name = "Poziomy", BackgroundTransparency = 1, Position = UDim2.fromScale(0.035, 0.732),
		Size = UDim2.fromScale(0.44, 0.12), ZIndex = 3 }, karta)
	for i, p in POZIOMY do
		local b = self:_opcja(rzadP, "Poziom_" .. p, nil, p, nil, {
			Position = UDim2.fromScale((i - 1) * 0.34, 0), Size = UDim2.fromScale(0.3, 1), Rotation = ({ -1.5, 1, -0.8 })[i] })
		self.poziomy[p] = b
		table.insert(self.polaczenia, b.Activated:Connect(function()
			self.wybor.poziom = p
			self:_odswiez()
		end))
	end
	self.podsumowanie = self:_tekst(karta, { Name = "Podsumowanie", Position = UDim2.fromScale(0.035, 0.865), Size = UDim2.fromScale(0.52, 0.06),
		Font = KOMIKS, Text = "", TextColor3 = K.ciemny, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 4 }, 0)
	self.status = self:_tekst(karta, { Name = "Status", Position = UDim2.fromScale(0.035, 0.925), Size = UDim2.fromScale(0.52, 0.055),
		Font = KOMIKS, Text = "", TextColor3 = K.czerwony, TextXAlignment = Enum.TextXAlignment.Left, ZIndex = 4 }, 0)

	-- WALCZ
	local walcz = self:_nowy("Frame", { Name = "Walcz", AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(0.965, 0.95),
		Size = UDim2.fromScale(0.38, 0.24), BackgroundTransparency = 1, Rotation = -2, ZIndex = 4 }, karta)
	local cien = self:_nowy("Frame", { Name = "Cien", BackgroundColor3 = K.tusz, BorderSizePixel = 0, Position = UDim2.fromScale(0.02, 0.08),
		Size = UDim2.fromScale(1, 1), ZIndex = 4 }, walcz)
	self:_nowy("UICorner", { CornerRadius = UDim.new(0.22, 0) }, cien)
	local wb = self:_nowy("TextButton", { Name = "Przycisk", AutoButtonColor = false, BackgroundColor3 = K.czerwony, BorderSizePixel = 0,
		Size = UDim2.fromScale(1, 1), Text = "", ZIndex = 5 }, walcz)
	self:_nowy("UICorner", { CornerRadius = UDim.new(0.22, 0) }, wb)
	self:_obrys(wb, 5)
	self.napisWalcz = self:_tekst(wb, { Name = "Napis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.52),
		Size = UDim2.fromScale(0.86, 0.7), Font = NAGLOWKI, Text = "WALCZ!", TextColor3 = K.zolty, ZIndex = 6 }, 5)
	self.walcz = wb
	table.insert(self.polaczenia, wb.Activated:Connect(function()
		local zostalo = if self.opcje.wolnaZa then self.opcje.wolnaZa() else 0
		if zostalo > 0 then
			self:komunikat(string.format("Poprzednia walka jeszcze trwa — za %d s", math.ceil(zostalo)))
			return
		end
		pamiec = table.clone(self.wybor)
		local wybor = table.clone(self.wybor)
		self:zamknij()
		if self.opcje.naWalcz then
			self.opcje.naWalcz(wybor)
		end
	end))

	-- odliczanie na przycisku, gdy serwer jeszcze nie przyjmie walki
	self.watek = task.spawn(function()
		while gui.Parent do
			local zostalo = if self.opcje.wolnaZa then self.opcje.wolnaZa() else 0
			self.napisWalcz.Text = if zostalo > 0 then string.format("ZA %d s", math.ceil(zostalo)) else "WALCZ!"
			wb.BackgroundColor3 = if zostalo > 0 then K.szary else K.czerwony
			task.wait(0.25)
		end
	end)

	table.insert(self.polaczenia, workspace.CurrentCamera:GetPropertyChangedSignal("ViewportSize"):Connect(function()
		self:_przelicz()
	end))
	table.insert(self.polaczenia, moduly.Parent:GetAttributeChangedSignal("EmulacjaEkranu"):Connect(function()
		self:_przelicz()
	end))
	self:_przelicz()
	self:_odswiez()
	gui.Parent = playerGui
	TweenService:Create(self.skalaKarty, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	otwarty = self
	return self
end

function Panel:komunikat(tekst: string?)
	self.status.Text = tekst or ""
end

function Panel:zamknij()
	if self.zamkniety then
		return
	end
	self.zamkniety = true
	if otwarty == self then
		otwarty = nil
	end
	for _, p in self.polaczenia do
		p:Disconnect()
	end
	self.gui:Destroy()
end

function Wybor.otwarty()
	return otwarty
end

function Wybor.zamknij()
	if otwarty then
		otwarty:zamknij()
	end
end

function Wybor.pamiec()
	return table.clone(pamiec)
end

return Wybor
