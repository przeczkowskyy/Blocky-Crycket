--[[
	OknaPetArena — okna gracza Pet Arena (ModuleScript; w ramce ekranu InterfejsPetArena, więc skalują się razem z nim):
	EGGS (trzy jajka: cena albo FREE, jawne szanse, HATCH), PETS (zakładki TEAM — trzy miejsca drużyny i kolekcja z
	gwiazdkami; INDEX — Księga z sylwetkami i licznikiem), scena wyklucia (jajko trzęsie się, pęka błyskiem w kolorze
	rzadkości, pet wyskakuje: NEW PET! albo +1 STAR!). Modele w ViewportFrame (z wzorców w ReplicatedStorage).

	Użycie: local O = Okna.nowe(ramka, D, L, wzorce, { naJajko(nr), naDruzyne({ id, … }), pad = function(): boolean })
		O:otworz("jajka" | "pety" | "ksiega")   O:zamknij()   O:otwarte()   O:odswiez(st)   O:wyklucie(z)   O:krok(dt)   O:stan()
	st = { zloto, darmowe (bool), kolekcja = { [id] = gwiazdki }, druzyna = { id, … }, ksiega = { [id] = true } }
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local GuiService = game:GetService("GuiService")

local Okna = {}
Okna.__index = Okna

local function nowy(klasa: string, wl: { [string]: any }, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wl do
		(o :: any)[k] = v
	end
	if rodzic then
		o.Parent = rodzic
	end
	return o
end

local function rog(o: Instance, r: number)
	nowy("UICorner", { CornerRadius = UDim.new(0, r) }, o)
end

local function gwiazdki(n: number): string
	return string.rep("★", n)
end

function Okna.nowe(ramka: Instance, D, L, wzorce: Instance?, opcje)
	local self = setmetatable({}, Okna)
	self.D, self.L, self.wzorce, self.opcje = D, L, wzorce, opcje
	local K = D.ui.kolory
	self.tusz, self.papier = Color3.fromHex(K.tusz), Color3.fromHex(K.papier)
	self.czcionka = Enum.Font[D.ui.czcionka] or Enum.Font.LuckiestGuy
	self.cyfry = Enum.Font[D.ui.czcionka_cyfr] or Enum.Font.FredokaOne
	self.ramka = ramka
	self.okno = nil
	self.nazwa = nil
	self.st = { zloto = 0, darmowe = false, kolekcja = {}, druzyna = {}, ksiega = {} }
	self.slotDoZmiany = nil
	self.przyciski = {}
	self.t = 0
	return self
end

function Okna:tekst(rodzic: Instance, t: string, poz: UDim2, roz: UDim2, kolor: Color3?, cyfry: boolean?, nazwa: string?): TextLabel
	local l = nowy("TextLabel", { Name = nazwa or "Tekst", BackgroundTransparency = 1, Position = poz, Size = roz, Text = t,
		TextScaled = true, Font = if cyfry then self.cyfry else self.czcionka, TextColor3 = kolor or self.papier }, rodzic)
	nowy("UIStroke", { Thickness = 1.5, Color = self.tusz }, l)
	return l
end

function Okna:przycisk(rodzic: Instance, t: string, poz: UDim2, roz: UDim2, kolor: string, akcja, nazwa: string?): TextButton
	local b = nowy("TextButton", { Name = nazwa or "Przycisk", Position = poz, Size = roz, BackgroundColor3 = Color3.fromHex(kolor),
		Text = "", AutoButtonColor = true, Selectable = true }, rodzic)
	rog(b, 10)
	nowy("UIStroke", { Thickness = 2.5, Color = self.tusz, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, b)
	self:tekst(b, t, UDim2.fromScale(0.06, 0.12), UDim2.fromScale(0.88, 0.76), nil, false, "Napis")
	b.Activated:Connect(akcja)
	table.insert(self.przyciski, b)
	return b
end

-- model w ViewportFrame (kamera od przodu), czarny = sylwetka
function Okna:scena(rodzic: Instance, wzorzec: string, wys: number, sylwetka: boolean?): (ViewportFrame, Model?)
	local vf = nowy("ViewportFrame", { Name = "Scena", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1),
		Ambient = Color3.fromRGB(190, 190, 200), LightColor = Color3.new(1, 1, 1), LightDirection = Vector3.new(-0.4, -1, 0.6) }, rodzic)
	if sylwetka then
		vf.ImageColor3 = Color3.new(0, 0, 0)
		vf.Ambient = Color3.new(0, 0, 0)
		vf.LightColor = Color3.new(0, 0, 0)
	end
	local kam = nowy("Camera", { FieldOfView = 34 }, vf)
	kam.CFrame = CFrame.lookAt(Vector3.new(0, wys * 0.62, -wys * 2.1), Vector3.new(0, wys * 0.47, 0))
	vf.CurrentCamera = kam
	local wz = self.wzorce and self.wzorce:FindFirstChild(wzorzec)
	local m = nil
	if wz then
		m = wz:Clone()
		m:PivotTo(CFrame.new())
		m.Parent = vf
	end
	return vf, m
end

function Okna:zamknij()
	if self.okno then
		self.okno:Destroy()
	end
	self.okno, self.nazwa = nil, nil
	self.przyciski = {}
	self.obroty = nil
	if GuiService.SelectedObject then
		GuiService.SelectedObject = nil
	end
end

function Okna:otwarte(): string?
	return self.nazwa
end

function Okna:szkielet(tytul: string, szer: number, wys: number): Frame
	self:zamknij()
	local o = nowy("Frame", { Name = "Okno", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.53),
		Size = UDim2.fromOffset(szer, wys), BackgroundColor3 = Color3.fromHex("2A2236"), ZIndex = 20 }, self.ramka)
	rog(o, 16)
	nowy("UIStroke", { Thickness = 3, Color = self.tusz }, o)
	local s = self.opcje.skala and self.opcje.skala() or 1
	nowy("UIScale", { Scale = s }, o)
	self:tekst(o, tytul, UDim2.fromOffset(16, 8), UDim2.fromOffset(120, 32), Color3.fromHex(self.D.ui.kolory.zloto), false, "Tytul")
	self:przycisk(o, self.D.ui.zamknij, UDim2.new(1, -54, 0, 6), UDim2.fromOffset(48, 46), "FF4D4D", function()
		self:zamknij()
	end, "Zamknij")
	self.okno = o
	self.obroty = {}
	return o
end

-- EGGS: trzy karty
function Okna:jajka()
	local D = self.D
	local o = self:szkielet(D.ui.jajka_przycisk, 600, 318)
	self.nazwa = "jajka"
	for i, J in D.jajka do
		local k = nowy("Frame", { Name = "Jajko" .. i, Position = UDim2.fromOffset(12 + (i - 1) * 196, 46), Size = UDim2.fromOffset(188, 262),
			BackgroundColor3 = Color3.fromHex("3A3148") }, o)
		rog(k, 12)
		nowy("UIStroke", { Thickness = 2.5, Color = Color3.fromHex(J.kolor) }, k)
		self:tekst(k, J.nazwa, UDim2.fromOffset(6, 4), UDim2.new(1, -12, 0, 24), Color3.fromHex(J.kolor))
		local scena = nowy("Frame", { Name = "Model", BackgroundTransparency = 1, Position = UDim2.fromOffset(44, 28), Size = UDim2.fromOffset(100, 78) }, k)
		local _, m = self:scena(scena, J.wzorzec, J.wysokosc)
		if m then
			table.insert(self.obroty, m)
		end
		local darmowe = i == 1 and self.st.darmowe
		self:tekst(k, if darmowe then D.ui.darmowe else (self.L.format(J.cena) .. " G"), UDim2.fromOffset(6, 106),
			UDim2.new(1, -12, 0, 24), Color3.fromHex(if darmowe then D.ui.kolory.zycie else D.ui.kolory.zloto), true, "Cena")
		self:tekst(k, D.ui.szanse, UDim2.fromOffset(6, 130), UDim2.new(1, -12, 0, 14), self.papier, false)
		local y = 145
		for r, s in J.szanse do
			if s > 0 then
				local R = D.rzadkosci[r]
				self:tekst(k, string.format("%s  %g%%", R.nazwa, math.floor(s * 1000 + 0.5) / 10), UDim2.fromOffset(10, y), UDim2.new(1, -20, 0, 14),
					Color3.fromHex(R.kolor), true, "Szansa" .. r)
				y += 15
			end
		end
		local stac = self.st.zloto >= J.cena or darmowe
		self:przycisk(k, D.ui.wyklij, UDim2.new(0.5, -70, 1, -52), UDim2.fromOffset(140, 46), if stac then "3DB36B" else "6A6474", function()
			if self.opcje.naJajko then
				self.opcje.naJajko(i)
			end
		end, "Wyklij" .. i)
	end
	self:zaznacz()
end

-- PETS: TEAM (drużyna + kolekcja) albo INDEX
function Okna:pety(zakladka: string?)
	local D = self.D
	zakladka = zakladka or "druzyna"
	local o = self:szkielet(D.ui.pety_przycisk, 600, 318)
	self.nazwa = if zakladka == "ksiega" then "ksiega" else "pety"
	self:przycisk(o, D.ui.druzyna, UDim2.fromOffset(150, 4), UDim2.fromOffset(118, 44), if zakladka == "druzyna" then "FFB13D" else "5A5566",
		function()
			self:pety("druzyna")
		end, "ZakladkaDruzyna")
	self:przycisk(o, D.ui.ksiega, UDim2.fromOffset(274, 4), UDim2.fromOffset(118, 44), if zakladka == "ksiega" then "FFB13D" else "5A5566",
		function()
			self:pety("ksiega")
		end, "ZakladkaKsiega")
	if zakladka == "ksiega" then
		local ile, razem = 0, #D.pety
		for _ in self.st.ksiega do
			ile += 1
		end
		self:tekst(o, string.format(D.ui.ksiega_licznik, ile, razem), UDim2.fromOffset(398, 12), UDim2.fromOffset(140, 26),
			Color3.fromHex(D.ui.kolory.zloto), true, "Licznik")
		for i, Pd in D.pety do
			local c = nowy("Frame", { Name = "Ksiega" .. i, Position = UDim2.fromOffset(12 + ((i - 1) % 6) * 96, 54 + math.floor((i - 1) / 6) * 130),
				Size = UDim2.fromOffset(90, 124), BackgroundColor3 = Color3.fromHex("3A3148") }, o)
			rog(c, 10)
			local zna = self.st.ksiega[Pd.id] == true
			local R = D.rzadkosci[Pd.stopien]
			nowy("UIStroke", { Thickness = 2, Color = if zna then Color3.fromHex(R.kolor) else Color3.fromHex("5A5566") }, c)
			local sc = nowy("Frame", { Name = "Model", BackgroundTransparency = 1, Position = UDim2.fromOffset(4, 4), Size = UDim2.fromOffset(82, 82) }, c)
			self:scena(sc, Pd.wzorzec, Pd.wysokosc, not zna)
			self:tekst(c, if zna then Pd.nazwa else "???", UDim2.fromOffset(4, 88), UDim2.fromOffset(82, 16), self.papier)
			self:tekst(c, R.nazwa, UDim2.fromOffset(4, 104), UDim2.fromOffset(82, 14), Color3.fromHex(R.kolor), true)
		end
		self:zaznacz()
		return
	end
	-- drużyna: trzy miejsca
	local dr = self.st.druzyna
	for s = 1, D.gracz.druzyna_maks do
		local id = dr[s]
		local nr = id and self.L.nrPeta(D, id)
		local Pd = nr and D.pety[nr]
		local b = self:przycisk(o, if Pd then Pd.nazwa .. " " .. gwiazdki(self.st.kolekcja[id] or 1) else "+", UDim2.fromOffset(12 + (s - 1) * 196, 54),
			UDim2.fromOffset(188, 46), if self.slotDoZmiany == s then "FFB13D" elseif Pd then "4A4060" else "3A3148", function()
				self.slotDoZmiany = if self.slotDoZmiany == s then nil else s
				self:pety("druzyna")
			end, "Slot" .. s)
		if Pd then
			b:FindFirstChild("Napis").TextColor3 = Color3.fromHex(D.rzadkosci[Pd.stopien].kolor)
		end
	end
	self:tekst(o, if self.slotDoZmiany then string.format(D.ui.wybierz_slot, self.slotDoZmiany) else D.ui.kolekcja, UDim2.fromOffset(12, 104),
		UDim2.fromOffset(576, 18), self.papier, false, "Podpis")
	-- kolekcja (posiadane, od najrzadszych)
	local lista = {}
	for i, Pd in D.pety do
		if self.st.kolekcja[Pd.id] then
			table.insert(lista, i)
		end
	end
	table.sort(lista, function(a, b)
		return D.pety[a].stopien > D.pety[b].stopien
	end)
	local sf = nowy("ScrollingFrame", { Name = "Kolekcja", Position = UDim2.fromOffset(8, 126), Size = UDim2.fromOffset(584, 184),
		BackgroundTransparency = 1, ScrollBarThickness = 6, CanvasSize = UDim2.fromOffset(0, math.ceil(#lista / 6) * 92), BorderSizePixel = 0 }, o)
	for k, i in lista do
		local Pd = D.pety[i]
		local R = D.rzadkosci[Pd.stopien]
		local wDruzynie = table.find(dr, Pd.id) ~= nil
		local c = nowy("TextButton", { Name = "Pet_" .. Pd.id, Position = UDim2.fromOffset(4 + ((k - 1) % 6) * 96, math.floor((k - 1) / 6) * 92),
			Size = UDim2.fromOffset(90, 88), BackgroundColor3 = Color3.fromHex(if wDruzynie then "4A4060" else "3A3148"), Text = "",
			AutoButtonColor = true, Selectable = true }, sf)
		rog(c, 10)
		nowy("UIStroke", { Thickness = if wDruzynie then 3 else 2, Color = Color3.fromHex(if wDruzynie then D.ui.kolory.ty else R.kolor),
			ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, c)
		local sc = nowy("Frame", { Name = "Model", BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 2), Size = UDim2.fromOffset(70, 54) }, c)
		self:scena(sc, Pd.wzorzec, Pd.wysokosc)
		self:tekst(c, Pd.nazwa, UDim2.fromOffset(3, 56), UDim2.fromOffset(84, 15), Color3.fromHex(R.kolor))
		self:tekst(c, gwiazdki(self.st.kolekcja[Pd.id] or 1) .. (if wDruzynie then "  " .. D.ui.w_druzynie else ""), UDim2.fromOffset(3, 71),
			UDim2.fromOffset(84, 14), Color3.fromHex(D.ui.kolory.zloto), true)
		c.Activated:Connect(function()
			self:wybierzPeta(Pd.id)
		end)
		table.insert(self.przyciski, c)
	end
	self:zaznacz()
end

-- dotknięcie peta w kolekcji: do wybranego miejsca (albo pierwszego wolnego / zamiana z ostatnim)
function Okna:wybierzPeta(id: string)
	local dr = table.clone(self.st.druzyna)
	local juz = table.find(dr, id)
	local s = self.slotDoZmiany
	if juz and not s then
		return
	end
	if not s then
		s = if #dr < self.D.gracz.druzyna_maks then #dr + 1 else #dr
	end
	if juz then
		dr[juz] = dr[s]
	end
	dr[s] = id
	local czyste = {}
	for i = 1, self.D.gracz.druzyna_maks do
		if dr[i] then
			table.insert(czyste, dr[i])
		end
	end
	self.slotDoZmiany = nil
	if self.opcje.naDruzyne then
		self.opcje.naDruzyne(czyste)
	end
	self.st.druzyna = czyste
	self:pety("druzyna")
end

function Okna:otworz(nazwa: string)
	if nazwa == "jajka" then
		self:jajka()
	elseif nazwa == "pety" then
		self:pety("druzyna")
	elseif nazwa == "ksiega" then
		self:pety("ksiega")
	end
end

-- pad: zaznacz pierwszy przycisk (GuiService)
function Okna:zaznacz()
	if self.opcje.pad and self.opcje.pad() and #self.przyciski > 1 then
		GuiService.SelectedObject = self.przyciski[2]
	end
end

function Okna:odswiez(st)
	local zmiana = st.zloto ~= self.st.zloto or st.darmowe ~= self.st.darmowe
	self.st = st
	if self.nazwa == "jajka" and zmiana then
		local zaz = GuiService.SelectedObject
		self:jajka()
		if zaz then
			pcall(function()
				GuiService.SelectedObject = self.okno and self.okno:FindFirstChild(zaz.Name, true)
			end)
		end
	end
end

------------------------------------------------------------ wyklucie
function Okna:wyklucie(z)
	local D = self.D
	if self.scenaW then
		self.scenaW.ramka:Destroy()
	end
	local J = D.jajka[z.jajko]
	local Pd = D.pety[z.pet]
	local R = D.rzadkosci[z.rzadkosc]
	local tlo = nowy("Frame", { Name = "Wyklucie", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.new(0, 0, 0), BackgroundTransparency = 0.45,
		ZIndex = 40 }, self.ramka)
	local pole = nowy("Frame", { Name = "Pole", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.45), Size = UDim2.fromOffset(230, 230),
		BackgroundTransparency = 1, ZIndex = 41 }, tlo)
	local s = self.opcje.skala and self.opcje.skala() or 1
	nowy("UIScale", { Scale = s }, pole)
	local blysk = nowy("Frame", { Name = "Blysk", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(0.2, 0.2),
		BackgroundColor3 = Color3.fromHex(R.kolor), BackgroundTransparency = 1, ZIndex = 41 }, pole)
	rog(blysk, 200)
	local vf, jajko = self:scena(pole, J.wzorzec, J.wysokosc * 1.15)
	vf.ZIndex = 42
	local napis = self:tekst(tlo, "", UDim2.new(0.5, -170 * s, 0.45, 118 * s), UDim2.fromOffset(340 * s, 44 * s), Color3.fromHex(R.kolor))
	napis.ZIndex = 43
	local nazwa = self:tekst(tlo, "", UDim2.new(0.5, -170 * s, 0.45, 160 * s), UDim2.fromOffset(340 * s, 30 * s), self.papier)
	nazwa.ZIndex = 43
	tlo.InputBegan:Connect(function(w: InputObject)
		if self.scenaW and self.scenaW.t > 2.2 and (w.UserInputType == Enum.UserInputType.MouseButton1 or w.UserInputType == Enum.UserInputType.Touch) then
			self.scenaW.t = 99
		end
	end)
	self.scenaW = { t = 0, ramka = tlo, vf = vf, jajko = jajko, pet = nil, z = z, J = J, Pd = Pd, R = R, napis = napis, nazwa = nazwa, blysk = blysk }
end

function Okna:krok(dt: number)
	self.t += dt
	if self.obroty then
		for _, m in self.obroty do
			if m.Parent then
				m:PivotTo(CFrame.Angles(0, math.sin(self.t * 1.4) * 0.5, 0))
			end
		end
	end
	local w = self.scenaW
	if not w then
		return
	end
	w.t += dt
	if w.t < 1.6 then
		local sila = 0.05 + w.t * 0.16
		if w.jajko then
			w.jajko:PivotTo(CFrame.Angles(0, 0, math.sin(w.t * (18 + w.t * 16)) * sila))
		end
	elseif not w.pet and w.t < 90 then
		if w.jajko then
			w.jajko:Destroy()
			w.jajko = nil
		end
		local wz = self.wzorce and self.wzorce:FindFirstChild(w.Pd.wzorzec)
		if wz then
			w.pet = wz:Clone()
			w.pet.Parent = w.vf
			local m = (w.J.wysokosc * 1.15) / math.max(1, w.Pd.wysokosc)
			pcall(function()
				w.pet:ScaleTo(m)
			end)
			w.skalaPeta = m
		end
		w.blysk.BackgroundTransparency = 0
		local D = self.D
		w.napis.Text = if w.z.nowy then D.ui.nowy_pet elseif w.z.maks then string.format(D.ui.maks_gwiazdek, self.L.format(w.z.zwrot))
			else D.ui.gwiazdka .. " " .. gwiazdki(w.z.gwiazdki)
		w.nazwa.Text = w.Pd.nazwa .. "  ·  " .. w.R.nazwa
		if self.opcje.naPekniecie then
			self.opcje.naPekniecie(w.z.rzadkosc)
		end
	end
	if w.t >= 1.6 then
		local tp = w.t - 1.6
		w.blysk.Size = UDim2.fromScale(0.2 + tp * 3, 0.2 + tp * 3)
		w.blysk.BackgroundTransparency = math.clamp(tp / 0.5, 0, 1)
		if w.pet then
			local h = w.J.wysokosc * 1.15
			local skok = if tp < 0.4 then math.sin(tp / 0.4 * math.pi) * h * 0.25 else 0
			w.pet:PivotTo(CFrame.new(0, skok, 0) * CFrame.Angles(0, math.sin(tp * 2.2) * 0.6, 0))
		end
	end
	if w.t > 4.2 then
		w.ramka:Destroy()
		self.scenaW = nil
	end
end

local function prost(o: GuiObject): { number }
	return { o.AbsolutePosition.X, o.AbsolutePosition.Y, o.AbsoluteSize.X, o.AbsoluteSize.Y }
end

function Okna:stan(przelicz)
	local w = { okno = self.nazwa, wyklucie = if self.scenaW then { t = self.scenaW.t, napis = self.scenaW.napis.Text } else nil }
	if self.okno then
		w.ramka = przelicz(self.okno)
		w.przyciski = {}
		for _, b in self.przyciski do
			if b.Parent and b.Visible then
				table.insert(w.przyciski, przelicz(b))
			end
		end
		w.zaznaczony = if GuiService.SelectedObject then GuiService.SelectedObject.Name else nil
	end
	local _ = prost
	return w
end

return Okna
