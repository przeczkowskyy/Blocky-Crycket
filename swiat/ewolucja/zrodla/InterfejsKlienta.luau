--[[
	InterfejsKlienta — ekran gry (interfejs1) według makiet i przewodnika stylu agenta grafiki (modele/README.md, sekcja
	„Interfejs”; podglad/23–25). Wzór: telefon poziomo 844 × 390 pt; każda warstwa skalowana razem (warstwa() klienta).
	- u góry na środku: portret obecnego stadium (żywy rig w pozie „portret” w ViewportFrame), nazwa, STAGE n / 8, pasek
	  wzrostu (żar), następne stadium jako czarna sylwetka, pasek życia; obok liczniki złota i skarbu (przycisk legowiska);
	- drabina przy lewej krawędzi: zdobyte stadia jako portrety, następne jako sylwetka, dalsze „?”; obecne większe z
	  pierścieniem żaru i nazwą;
	- prawy dół: BITE (103 pt) i DASH / FIRE / POWER (68 pt) — płytki w kolorach linii, wewnętrzny pierścień, połysk,
	  wciśnięcie (0,92, ciemniej, 0,08 s), odnowa jako ciemny wycinek od godziny 12 z sekundami i błyskiem żaru na końcu,
	  zamknięty stan (kłódka) i pigułki „<ZDOLNOŚĆ> at <STADIUM>”; lewy dół wolny dla drążka;
	- panel legowiska: trofea (portrety, poziomy, dochód, warianty, zamknięte sylwetki), ulepszenia z ceną, szanse wariantów;
	- odsłona: kokon → nazwa i nowa moc → sylwetka następnego stadium → CONTINUE.
	Ikony z tabeli D.ikony (ustawienia.json → „ikony.id”); bez numeru zastępstwo (IkonyEwolucji): model 3D, rysunek, napis.
]]
local H = {}
H.__index = H

local function rgb(h: string): Color3
	return Color3.fromHex(h)
end

local function czcionka(nazwa: string?, zapas: Enum.Font): Enum.Font
	if not nazwa then
		return zapas
	end
	local ok, f = pcall(function()
		return Enum.Font[nazwa]
	end)
	return if ok and f then f else zapas
end
H.czcionka = czcionka

-- ---------------------------------------------------------------- budowa
function H.nowe(c)
	local self = setmetatable({}, H)
	self.c = c
	local D, UI = c.D, c.D.ui
	self.D, self.UI = D, UI
	local S = UI.styl or {}
	self.S = {}
	for k, v in S do
		self.S[k] = rgb(v)
	end
	self.fTytul = czcionka(UI.czcionka, Enum.Font.FredokaOne)
	self.fLiczby = czcionka(UI.czcionka_cyfr, Enum.Font.FredokaOne)
	self.fEtyk = czcionka(UI.czcionka_etykiet, Enum.Font.GothamBold)
	self.portrety = {} -- ViewportFrame → { f, ciemny }
	self.anim = {}
	self.nPortretow = 0
	self:zbudujGore()
	self:zbudujDrabine()
	self:zbudujPrzyciski()
	self:zbudujPanel()
	self:zbudujOdslone()
	self:zbudujWydarzenia()
	self:zbudujZadania()
	self:zbudujPowitanie()
	self.linia = 1
	return self
end

function H:nowy(klasa: string, wl, rodzic: Instance?): any
	return self.c.nowy(klasa, wl, rodzic)
end

function H:rog(o: Instance, r: number?)
	return self:nowy("UICorner", { CornerRadius = if r then UDim.new(0, r) else UDim.new(0.5, 0) }, o)
end

function H:obrys(o: Instance, g: number, k: Color3?, przez: number?)
	return self:nowy("UIStroke", { Thickness = g, Color = k or self.S.obrys, Transparency = przez or 0, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, o)
end

-- tekst: jasny z ciemnym obrysem (przewodnik); rozmiar w pt wzoru (UIScale warstwy skaluje), dłuższe napisy się zmniejszają
function H:tekst(o: Instance, t: string, poz: UDim2, roz: UDim2, rozmiar: number, kolor: Color3?, font: Enum.Font?, xa: Enum.TextXAlignment?): TextLabel
	local l = self:nowy("TextLabel", { BackgroundTransparency = 1, Position = poz, Size = roz, Text = t, TextScaled = true, Font = font or self.fEtyk,
		TextColor3 = kolor or self.S.tekst, TextXAlignment = xa or Enum.TextXAlignment.Center, ZIndex = 4 }, o)
	self:nowy("UITextSizeConstraint", { MaxTextSize = rozmiar, MinTextSize = math.min(rozmiar, 7) }, l)
	self:nowy("UIStroke", { Thickness = if rozmiar <= 10 then 1.5 else 2, Color = self.S.obrys }, l)
	return l
end

-- płytka z cieniem (ciemna kopia 3 pt niżej)
function H:plytka(rodzic: Instance, nazwa: string, poz: UDim2, roz: UDim2, kolor: Color3, r: number?, obrysG: number?)
	local cien = self:nowy("Frame", { Name = nazwa .. "Cien", Position = poz + UDim2.fromOffset(0, 3), Size = roz, BackgroundColor3 = self.S.cien,
		BackgroundTransparency = 0.6, BorderSizePixel = 0 }, rodzic)
	self:rog(cien, r)
	local f = self:nowy("Frame", { Name = nazwa, Position = poz, Size = roz, BackgroundColor3 = kolor, BorderSizePixel = 0 }, rodzic)
	self:rog(f, r)
	self:obrys(f, obrysG or 2)
	return f, cien
end

function H:gradient(o: Instance, gora: Color3, dol: Color3)
	return self:nowy("UIGradient", { Color = ColorSequence.new(gora, dol), Rotation = 90 }, o)
end

-- ---------------------------------------------------------------- portrety (żywy rig w pozie „portret”)
function H:wzorzec(f: number, pelny: boolean): Model?
	local F = self.D.formy[f]
	local wz = self.c.wzorce
	if not (wz and F) then
		return nil
	end
	if pelny then
		return wz:FindFirstChild(F.wzorzec) or wz:FindFirstChild(F.wzorzecLod or "")
	end
	return wz:FindFirstChild(F.wzorzecLod or F.wzorzec) or wz:FindFirstChild(F.wzorzec)
end

-- wypełnia ViewportFrame portretem stadium f (pełny rig albo uproszczony); kamera z przodu po lewej (trzy czwarte), popiersie
function H:portret(vf: ViewportFrame, f: number, o)
	o = o or {}
	for _, d in vf:GetChildren() do
		if d:IsA("WorldModel") or d:IsA("Camera") or d:IsA("Model") then
			d:Destroy()
		end
	end
	vf.ImageColor3 = if o.ciemny then Color3.new(0, 0, 0) else Color3.new(1, 1, 1)
	vf.ImageTransparency = if o.ciemny then 0.05 else 0
	local wz = self:wzorzec(f, o.pelny == true)
	local SK = self.c.SK
	if not wz then
		return
	end
	local m = wz:Clone()
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.CastShadow = false
		end
	end
	-- wzorzec leży gdzieś w magazynie: najpierw cały model do początku układu (stawy w WorldModel liczą się dopiero później)
	m:PivotTo(CFrame.new())
	if o.linia and SK then
		SK.barwLinii(m, o.linia)
	end
	if o.wariant and SK then
		SK.przemaluj(m, o.wariant.id, self.D.blender.warianty[o.wariant.id])
	end
	local F = self.D.formy[f]
	local Wk = SK and F.rig and SK:klipy(F.rig)
	local wm = Instance.new("WorldModel")
	wm.Parent = vf
	m.Parent = wm
	if Wk then
		local poza = if Wk.klipy.portret then "portret" elseif Wk.klipy.cokol then "cokol" else nil
		local r = SK.Rigi.zamroz(m, Wk, poza or "spoczynek", 0)
		r:ustaw(CFrame.new())
		if poza == "portret" then
			self.nPortretow += 1
		end
	else
		m:PivotTo(CFrame.new())
	end
	local cf, roz = m:GetBoundingBox()
	local glowa = m:FindFirstChild("GlowaAttachment", true)
	local piers = m:FindFirstChild("PiersAttachment", true)
	local cel, s
	if glowa and piers and not o.calosc then
		-- pozycje zaczepów w pozie portretu z łańcucha stawów (korzeń × C0 × Transform × C1⁻¹), bez czekania na silnik
		local g = (H.cfKosci(glowa.Parent, 0) * glowa.CFrame).Position
		local p = (H.cfKosci(piers.Parent, 0) * piers.CFrame).Position
		cel = g:Lerp(p, 0.35)
		s = math.max((g - p).Magnitude * 1.3, 0.4)
	else
		cel = cf.Position
		s = math.max(roz.X, roz.Y, roz.Z) * 0.62
	end
	local cam = Instance.new("Camera")
	cam.FieldOfView = 30
	local kier = Vector3.new(-0.62, 0.28, -0.78).Unit
	local d = s / math.tan(math.rad(15)) * (o.odl or 0.6)
	cam.CFrame = CFrame.lookAt(cel + kier * d, cel)
	cam.Parent = vf
	vf.CurrentCamera = cam
end

function H.cfKosci(b, glebia: number): CFrame
	local m = b:FindFirstChildOfClass("Motor6D")
	if m and m.Part1 == b and m.Part0 and glebia < 12 then
		return H.cfKosci(m.Part0, glebia + 1) * m.C0 * m.Transform * m.C1:Inverse()
	end
	return b.CFrame
end

function H:okno(rodzic: Instance, nazwa: string, poz: UDim2, roz: UDim2): ViewportFrame
	local vf = self:nowy("ViewportFrame", { Name = nazwa, Position = poz, Size = roz, BackgroundTransparency = 1, Ambient = Color3.fromRGB(200, 196, 210),
		LightColor = Color3.new(1, 1, 1), LightDirection = Vector3.new(-0.6, -1.2, -0.8), ZIndex = 3 }, rodzic)
	return vf
end

-- ---------------------------------------------------------------- ikony (obraz albo zastępstwo)
function H:ikona(slot: Instance, nazwa: string, napis: string?, kolorNapisu: Color3?)
	for _, d in slot:GetChildren() do
		if not d:IsA("UIAspectRatioConstraint") then
			d:Destroy()
		end
	end
	local I = self.c.Ikony
	local wz = self.c.wzorce
	local W = I.wybierz(self.D.ikony, nazwa, function(n)
		return wz ~= nil and wz:FindFirstChild(n) ~= nil
	end, napis)
	slot:SetAttribute("Ikona", nazwa)
	slot:SetAttribute("IkonaTyp", W.typ)
	local z = slot.ZIndex or 4
	if W.typ == "obraz" then
		self:nowy("ImageLabel", { Name = "Obraz", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Image = W.wartosc, ScaleType = Enum.ScaleType.Fit,
			ZIndex = z + 1 }, slot)
	elseif W.typ == "wzorzec" or W.typ == "model" then
		local vf = self:okno(slot, "Model", UDim2.fromScale(-0.05, -0.05), UDim2.fromScale(1.1, 1.1))
		vf.ZIndex = z + 1
		local m
		if W.typ == "wzorzec" then
			m = wz:FindFirstChild(W.wartosc):Clone()
		else
			m = self:modelZCzesci(W.wartosc)
		end
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				d.Anchored = true
			end
		end
		m:PivotTo(CFrame.new())
		m.Parent = vf
		local cf, roz = m:GetBoundingBox()
		local cam = Instance.new("Camera")
		cam.FieldOfView = 30
		local d = math.max(roz.X, roz.Y, roz.Z) * 2.1
		cam.CFrame = CFrame.lookAt(cf.Position + Vector3.new(0.35, 0.75, 1).Unit * d, cf.Position)
		cam.Parent = vf
		vf.CurrentCamera = cam
	elseif W.typ == "rysunek" and W.wartosc == "klodka" then
		local kab = self:nowy("Frame", { Name = "Kablak", Position = UDim2.fromScale(0.3, 0.12), Size = UDim2.fromScale(0.4, 0.5), BackgroundTransparency = 1,
			ZIndex = z + 1 }, slot)
		self:rog(kab)
		self:nowy("UIStroke", { Thickness = 4, Color = self.S.tekst }, kab)
		local cialo = self:nowy("Frame", { Name = "Cialo", Position = UDim2.fromScale(0.2, 0.42), Size = UDim2.fromScale(0.6, 0.46), BackgroundColor3 = self.S.tekst,
			ZIndex = z + 2 }, slot)
		self:rog(cialo, 4)
		self:obrys(cialo, 2)
		local dz = self:nowy("Frame", { Position = UDim2.fromScale(0.44, 0.3), Size = UDim2.fromScale(0.12, 0.4), BackgroundColor3 = self.S.obrys, ZIndex = z + 3 }, cialo)
		self:rog(dz)
	elseif W.typ == "rysunek" then
		local r = self:nowy("Frame", { Name = "Romb", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(0.62, 0.62),
			Rotation = 45, BackgroundColor3 = rgb(W.kolor or "FFC934"), ZIndex = z + 1 }, slot)
		self:rog(r, 3)
		self:obrys(r, 2)
		local b = self:nowy("Frame", { Position = UDim2.fromScale(0.18, 0.18), Size = UDim2.fromScale(0.3, 0.3), BackgroundColor3 = Color3.new(1, 1, 1),
			BackgroundTransparency = 0.35, ZIndex = z + 2 }, r)
		self:rog(b, 2)
	else
		local l = self:tekst(slot, W.napis or "", UDim2.fromScale(0.02, 0.22), UDim2.fromScale(0.96, 0.56), 40, kolorNapisu, self.fTytul)
		l.Name = "Napis"
		l:FindFirstChildOfClass("UITextSizeConstraint").MinTextSize = 1
		l.ZIndex = z + 1
	end
	return W.typ
end

-- moneta i korona z części (zastępstwa ikon, gdy obrazu nie ma)
function H:modelZCzesci(nazwa: string): Model
	local m = Instance.new("Model")
	local function cz(roz: Vector3, cf: CFrame, kolor: string, ksztalt: Enum.PartType?, mat: Enum.Material?)
		local p = Instance.new("Part")
		p.Size = roz
		p.CFrame = cf
		p.Color = rgb(kolor)
		p.Shape = ksztalt or Enum.PartType.Block
		p.Material = mat or Enum.Material.SmoothPlastic
		p.Anchored = true
		p.Parent = m
		return p
	end
	if nazwa == "moneta" then
		local obr = CFrame.Angles(0, math.rad(90), 0) * CFrame.Angles(0, 0, math.rad(15))
		cz(Vector3.new(0.35, 2, 2), obr, "E0A020", Enum.PartType.Cylinder)
		cz(Vector3.new(0.4, 1.55, 1.55), obr, "FFC934", Enum.PartType.Cylinder)
		cz(Vector3.new(0.45, 0.7, 0.25), obr * CFrame.new(0, 0, 0), "FFE58A")
	else -- korona
		cz(Vector3.new(1.0, 2.4, 2.4), CFrame.Angles(0, 0, math.rad(90)), "FFC934", Enum.PartType.Cylinder)
		for i = 0, 4 do
			local a = i / 5 * math.pi * 2
			local p = Vector3.new(math.cos(a) * 1.0, 0.85, math.sin(a) * 1.0)
			cz(Vector3.new(0.45, 0.9, 0.45), CFrame.new(p) * CFrame.Angles(0, -a, math.rad(45)), "FFC934")
			cz(Vector3.new(0.3, 0.3, 0.3), CFrame.new(Vector3.new(math.cos(a) * 1.22, 0.1, math.sin(a) * 1.22)), if i % 2 == 0 then "FF3D6A" else "7FF8FF",
				Enum.PartType.Ball, Enum.Material.Neon)
		end
	end
	return m
end

-- ---------------------------------------------------------------- góra: portret, nazwa, pasek wzrostu, życie, złoto
function H:zbudujGore()
	local c, S, UI = self.c, self.S, self.UI
	local W = c.warstwa("Wzrost", Vector2.new(0.5, 0), UDim2.new(0.5, -20, 0, 10), Vector2.new(392, 60))
	self.ramkaWzrostu = W
	-- portret w kole z pierścieniem żaru
	local kolo, _ = self:plytka(W, "Portret", UDim2.fromOffset(0, 4), UDim2.fromOffset(52, 52), S.karta, nil, 3)
	kolo:FindFirstChildOfClass("UIStroke").Color = S.zar
	local kt = self:nowy("Frame", { Name = "Tlo", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.new(1, 1, 1), ZIndex = 2 }, kolo)
	self:gradient(kt, rgb("5A4A78"), S.karta)
	self:rog(kt)
	self.portretHUD = self:okno(kolo, "Okno", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
	self:rog(self.portretHUD)
	self.nazwa = self:tekst(W, "", UDim2.fromOffset(60, 0), UDim2.fromOffset(190, 22), 17, S.tekst, self.fTytul, Enum.TextXAlignment.Left)
	self.etap = self:tekst(W, "", UDim2.fromOffset(250, 4), UDim2.fromOffset(98, 16), 11, S.tekst2, self.fLiczby, Enum.TextXAlignment.Right)
	-- pasek wzrostu 288 × 18
	local tlo = self:nowy("Frame", { Name = "Pasek", Position = UDim2.fromOffset(60, 24), Size = UDim2.fromOffset(288, 18), BackgroundColor3 = S.pas, ZIndex = 2 }, W)
	self:rog(tlo)
	self:obrys(tlo, 2)
	local wyp = self:nowy("Frame", { Name = "Wypelnienie", Size = UDim2.fromScale(0, 1), BackgroundColor3 = Color3.new(1, 1, 1), BorderSizePixel = 0, ZIndex = 3 }, tlo)
	self:rog(wyp)
	self.gradWzrostu = self:gradient(wyp, S.zar_gora, S.zar)
	self.pasekW = wyp
	self.pasekNapis = self:tekst(tlo, "", UDim2.fromScale(0, 0.05), UDim2.fromScale(1, 0.9), 11, S.tekst, self.fLiczby)
	self.pasekNapis.ZIndex = 5
	self.pasekSkala = self:nowy("UIScale", { Scale = 1 }, tlo)
	self.pulsT = 99
	-- następne stadium: czarna sylwetka w kole + „?”
	local nast = self:plytka(W, "Nastepne", UDim2.fromOffset(356, 12), UDim2.fromOffset(36, 36), rgb("6A5C88"))
	self.nastHUD = self:okno(nast, "Okno", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
	self:rog(self.nastHUD)
	local zn = self:tekst(nast, "?", UDim2.fromScale(0.5, 0.45), UDim2.fromScale(0.55, 0.6), 16, S.zar_gora, self.fTytul)
	zn.ZIndex = 6
	self.nastZnak = zn
	-- życie 206 × 12
	local zt = self:nowy("Frame", { Name = "Zycie", Position = UDim2.fromOffset(60, 46), Size = UDim2.fromOffset(206, 12), BackgroundColor3 = S.pas, ZIndex = 2 }, W)
	self:rog(zt)
	self:obrys(zt, 2)
	local zw = self:nowy("Frame", { Name = "Wypelnienie", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.new(1, 1, 1), BorderSizePixel = 0, ZIndex = 3 }, zt)
	self:rog(zw)
	self.gradZycia = self:gradient(zw, S.zycie_gora, S.zycie)
	self.zycieW = zw
	local hp = self:tekst(zt, UI.hp, UDim2.fromOffset(6, 0), UDim2.fromOffset(20, 12), 9, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
	hp.ZIndex = 5
	self.ramkaZycia = zt
	-- złoto i skarb (przycisk legowiska): dwie pigułki
	-- prawy górny róg pusty (przycisk czatu / wcięcie): co najmniej 146 pt od prawej krawędzi
	local Z = c.warstwa("Zloto", Vector2.new(1, 0), UDim2.new(1, -146, 0, 10), Vector2.new(86, 60))
	self.ramkaZlota = Z
	local b = self:nowy("TextButton", { Name = "Legowisko", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Text = "", AutoButtonColor = false }, Z)
	self.bLegowisko = b
	local p1 = self:plytka(b, "PigulkaZlota", UDim2.fromOffset(0, 0), UDim2.fromOffset(86, 28), S.pas)
	local i1 = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(2, 2), Size = UDim2.fromOffset(24, 24), BackgroundTransparency = 1, ZIndex = 4 }, p1)
	self:ikona(i1, "moneta")
	self.zlotoNapis = self:tekst(p1, "0", UDim2.fromOffset(28, 3), UDim2.fromOffset(54, 22), 13, S.tekst, self.fLiczby, Enum.TextXAlignment.Left)
	local p2 = self:plytka(b, "PigulkaSkarbu", UDim2.fromOffset(0, 32), UDim2.fromOffset(86, 28), S.pas)
	local i2 = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(2, 2), Size = UDim2.fromOffset(24, 24), BackgroundTransparency = 1, ZIndex = 4 }, p2)
	self:ikona(i2, "skarb")
	self.skarbNapis = self:tekst(p2, "0", UDim2.fromOffset(28, 1), UDim2.fromOffset(54, 14), 11, S.zloto, self.fLiczby, Enum.TextXAlignment.Left)
	self.naSNapis = self:tekst(p2, "", UDim2.fromOffset(28, 15), UDim2.fromOffset(54, 11), 9, S.kup, self.fLiczby, Enum.TextXAlignment.Left)
	self.formaHUD = 0
end

-- obecne stadium f (portret pełnego rigu) i następne (sylwetka); przebudowa tylko przy zmianie
function H:ustawStadium(f: number, W0)
	local NF = #self.D.formy
	local klucz = tostring(f) .. (if W0 then W0.id else "") .. "/" .. tostring(self.linia)
	if self.formaHUD == klucz then
		return
	end
	self.formaHUD = klucz
	self:portret(self.portretHUD, f, { pelny = true, wariant = W0, linia = self.linia })
	if f < NF then
		self:portret(self.nastHUD, f + 1, { ciemny = true })
		self.nastHUD.Parent.Visible = true
	else
		self.nastHUD.Parent.Visible = false
	end
end

-- ---------------------------------------------------------------- drabina (lewa krawędź, w połowie wysokości)
function H:zbudujDrabine()
	local c, S, D = self.c, self.S, self.D
	local NF = #D.formy
	local wys = 34 + 30 + (NF - 1) * 30 + 30
	local L = c.warstwa("Drabina", Vector2.new(0, 0), UDim2.new(0, 22, 0, 78), Vector2.new(130, wys))
	self.ramkaDrabiny = L
	self.dlugoscDrabiny = wys
	local os_ = self:nowy("Frame", { Name = "Os", Position = UDim2.fromOffset(18, 18), Size = UDim2.fromOffset(4, wys - 36), BackgroundColor3 = S.pas,
		BackgroundTransparency = 0.25, BorderSizePixel = 0 }, L)
	self:rog(os_)
	self.wezly = {}
	for f = 1, NF do
		local y = wys - 19 - (f - 1) * 30
		local k = self:nowy("Frame", { Name = "Szczebel" .. f, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(20, y), Size = UDim2.fromOffset(24, 24),
			BackgroundColor3 = S.karta, ZIndex = 2 }, L)
		self:rog(k)
		local ob = self:obrys(k, 2)
		local vf = self:okno(k, "Okno", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
		self:rog(vf)
		local zn = self:tekst(k, "?", UDim2.fromScale(0.2, 0.15), UDim2.fromScale(0.6, 0.7), 12, S.tekst2, self.fTytul)
		self.wezly[f] = { ramka = k, vf = vf, znak = zn, obrys = ob, y = y, stan = "" }
	end
	-- nazwa obecnego stadium obok węzła
	local pig = self:nowy("Frame", { Name = "NazwaObecnego", AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.fromOffset(40, 0), Size = UDim2.fromOffset(84, 20),
		BackgroundColor3 = S.pas, BackgroundTransparency = 0.1, ZIndex = 2 }, L)
	self:rog(pig)
	self:obrys(pig, 2)
	self.drabinaNazwa = self:tekst(pig, "", UDim2.fromOffset(6, 2), UDim2.new(1, -12, 1, -4), 11, S.tekst, self.fTytul)
	self.drabinaPig = pig
	-- odrodzenie1: następna linia smoków (czarna sylwetka ANCIENT w pierścieniu jej koloru) i liczba odrodzeń
	local k = self:nowy("Frame", { Name = "NastepnaLinia", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(20, 17), Size = UDim2.fromOffset(30, 30),
		BackgroundColor3 = rgb("6A5C88"), ZIndex = 2 }, L)
	self:rog(k)
	self.liniaObrys = self:obrys(k, 3)
	self.liniaOkno = self:okno(k, "Okno", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
	self:rog(self.liniaOkno)
	local lp = self:nowy("Frame", { Name = "LiniaPig", AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.fromOffset(40, 17), Size = UDim2.fromOffset(84, 20),
		BackgroundColor3 = S.pas, BackgroundTransparency = 0.1, ZIndex = 2 }, L)
	self:rog(lp)
	self:obrys(lp, 2)
	self.liniaNapis = self:tekst(lp, "", UDim2.fromOffset(6, 2), UDim2.new(1, -12, 1, -4), 10, S.tekst, self.fTytul)
	self.liniaKlucz = ""
end

-- linia smoków: obecna (kolory portretów) i następna (sylwetka w drabinie), odrodzenia i mnożnik
function H:ustawLinie(linia: number, odrodzenia: number, mnoznik: number)
	local LI = self.D.odrodzenie and self.D.odrodzenie.linie
	if not LI then
		return
	end
	local klucz = string.format("%d/%d", linia, odrodzenia)
	if self.liniaKlucz == klucz then
		return
	end
	self.liniaKlucz = klucz
	if self.linia ~= linia then
		self.linia = linia
		self.formaHUD = ""
		for _, K in self.wezly do
			K.stan = ""
		end
	end
	local nast = LI[linia % #LI + 1]
	self.liniaObrys.Color = rgb(nast.kolor)
	self:portret(self.liniaOkno, #self.D.formy, { ciemny = true })
	self.liniaNapis.Text = if odrodzenia > 0 then string.format("R%d  x%.2f", odrodzenia, mnoznik) else nast.nazwa
	self.liniaNapis.TextColor3 = if odrodzenia > 0 then rgb(LI[linia].kolor) else rgb(nast.kolor)
end

-- stan drabiny: Z zdobyte, N następne (sylwetka), ? dalsze; obecne 36 pt z pierścieniem żaru; zwraca napis stanu dla prób
function H:drabina(mf: number, f0: number, warianty): string
	local D, S = self.D, self.S
	local NF = #D.formy
	local stan = {}
	for f = 1, NF do
		local K = self.wezly[f]
		local zdobyta = f <= mf
		local nastepna = f == mf + 1
		local s = if zdobyta then "Z" elseif nastepna then "N" else "?"
		local rozm = if f == f0 then 38 elseif zdobyta then 27 elseif nastepna then 28 else 20
		K.ramka.Size = UDim2.fromOffset(rozm, rozm)
		local wid = zdobyta or nastepna
		K.vf.Visible = wid
		K.znak.Visible = not wid
		K.ramka.BackgroundColor3 = if zdobyta then S.karta elseif nastepna then rgb("6A5C88") else S.pas
		K.obrys.Color = if f == f0 then S.zar else S.obrys
		K.obrys.Thickness = if f == f0 then 3 else 2
		local W0 = warianty and warianty[f]
		local klucz = s .. (if W0 then W0.id else "")
		if wid and K.stan ~= klucz then
			self:portret(K.vf, f, { ciemny = not zdobyta, wariant = if zdobyta then W0 else nil, linia = self.linia })
		end
		K.stan = klucz
		table.insert(stan, if f == NF and s == "?" then "C" else s)
	end
	local Kf = self.wezly[math.clamp(f0, 1, NF)]
	self.drabinaPig.Position = UDim2.fromOffset(42, Kf.y)
	self.drabinaNazwa.Text = D.formy[math.clamp(f0, 1, NF)].nazwa
	return table.concat(stan)
end

-- ---------------------------------------------------------------- przyciski akcji (prawy dół)
-- wycinek odnowy: dwie połówki z gradientem o twardej krawędzi (UIGradient.Rotation — bez obracania ramek, więc
-- przycinanie działa); wycinek zaczyna się o godzinie 12 i kurczy zgodnie z zegarem
function H:wycinek(rodzic: Instance, z: number)
	local w = {}
	local seq = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.499, 0), NumberSequenceKeypoint.new(0.501, 1),
		NumberSequenceKeypoint.new(1, 1) })
	for i, strona in { "L", "P" } do
		local kont = self:nowy("Frame", { Name = "Odnowa" .. strona, Position = UDim2.fromScale(if i == 1 then 0 else 0.5, 0), Size = UDim2.fromScale(0.5, 1),
			BackgroundTransparency = 1, ClipsDescendants = true, ZIndex = z, Visible = false }, rodzic)
		local dysk = self:nowy("Frame", { Position = UDim2.fromScale(if i == 1 then 0 else -1, 0), Size = UDim2.fromScale(2, 1), BackgroundColor3 = self.S.odnowa,
			BackgroundTransparency = 0.33, ZIndex = z }, kont)
		self:rog(dysk)
		local g = self:nowy("UIGradient", { Transparency = seq, Rotation = 0 }, dysk)
		w[strona] = { k = kont, g = g }
	end
	return w
end

-- ułamek pozostałej odnowy p (0–1): wycinek od godziny 12 przeciwnie do wskazówek o kąt p × 360 (krawędź idzie z zegarem)
function H.ustawWycinek(w, p: number)
	local a = math.clamp(p, 0, 1) * 360
	w.L.k.Visible = a > 0.5
	w.P.k.Visible = a > 180
	w.L.g.Rotation = 180 - math.min(a, 180)
	w.P.g.Rotation = 180 - a
end

function H:przycisk(nazwa: string, srodek: Vector2, d: number, kolor: Color3, ikona: string, podpis: string?)
	local c, S = self.c, self.S
	local R = c.warstwa(nazwa, Vector2.new(1, 1), UDim2.new(1, srodek.X + d / 2, 1, srodek.Y + d / 2), Vector2.new(d, d))
	local b = self:nowy("TextButton", { Name = nazwa, Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Text = "", AutoButtonColor = false }, R)
	local sk = self:nowy("UIScale", { Scale = 1 }, b)
	local cien = self:nowy("Frame", { Name = "Cien", Position = UDim2.fromOffset(0, 3), Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.cien, BackgroundTransparency = 0.6,
		ZIndex = 1 }, b)
	self:rog(cien)
	local pl = self:nowy("Frame", { Name = "Plytka", Size = UDim2.fromScale(1, 1), BackgroundColor3 = kolor, ZIndex = 2 }, b)
	self:rog(pl)
	self:obrys(pl, 3)
	local polysk = self:nowy("Frame", { Name = "Polysk", Position = UDim2.fromScale(0.2, 0.07), Size = UDim2.fromScale(0.6, 0.28), BackgroundColor3 = Color3.new(1, 1, 1),
		BackgroundTransparency = 0.72, ZIndex = 3 }, pl)
	self:rog(polysk)
	local ring = self:nowy("Frame", { Name = "Pierscien", Position = UDim2.fromScale(0.07, 0.07), Size = UDim2.fromScale(0.86, 0.86), BackgroundTransparency = 1, ZIndex = 3 }, pl)
	self:rog(ring)
	self:nowy("UIStroke", { Thickness = math.max(2, d * 0.025), Color = Color3.new(1, 1, 1), Transparency = 0.73 }, ring)
	local slot = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromScale(0.095, 0.095), Size = UDim2.fromScale(0.81, 0.81), BackgroundTransparency = 1, ZIndex = 4 }, pl)
	local wyc = self:wycinek(pl, 6)
	local sek = self:tekst(pl, "", UDim2.fromScale(0.2, 0.26), UDim2.fromScale(0.6, 0.48), math.floor(d * 0.36), S.tekst, self.fLiczby)
	sek.ZIndex = 8
	sek.Visible = false
	local blysk = self:nowy("Frame", { Name = "Blysk", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, ZIndex = 9 }, pl)
	self:rog(blysk)
	local bs = self:nowy("UIStroke", { Thickness = 0, Color = S.zar, Transparency = 1 }, blysk)
	-- podpis pod przyciskiem (tylko gdy jest obraz ikony; zastępstwo ma napis w środku)
	local pod = self:nowy("Frame", { Name = "Podpis", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.new(0.5, 0, 1, -2), Size = UDim2.fromOffset(math.floor(d * 0.62), 15),
		BackgroundColor3 = S.pas, ZIndex = 10, Visible = false }, b)
	self:rog(pod)
	self:obrys(pod, 2)
	local podN = self:tekst(pod, podpis or "", UDim2.fromOffset(4, 1), UDim2.new(1, -8, 1, -2), 9, S.tekst, self.fEtyk)
	podN.ZIndex = 11
	local P = { ramka = R, b = b, skala = sk, cien = cien, plytka = pl, slot = slot, wycinek = wyc, sekundy = sek, blysk = bs, podpis = pod, podpisN = podN, kolor = kolor,
		ikonaNazwa = "", zamkniety = false, wcisniety = 0, blyskT = 99, odnowaByla = false, d = d }
	self:ustawIkone(P, ikona, podpis)
	b.MouseButton1Down:Connect(function()
		self:wcisnij(P, true)
	end)
	b.MouseButton1Up:Connect(function()
		self:wcisnij(P, false)
	end)
	b.MouseLeave:Connect(function()
		self:wcisnij(P, false)
	end)
	table.insert(self.anim, P)
	return P
end

function H:ustawIkone(P, ikona: string, napis: string?)
	if P.ikonaNazwa == ikona .. "|" .. (napis or "") then
		return
	end
	P.ikonaNazwa = ikona .. "|" .. (napis or "")
	local typ = self:ikona(P.slot, ikona, napis, if P.kolor == self.S.gryz then self.S.obrys else nil)
	-- napis w środku płytki BITE (jasna płytka): ciemny tekst
	local l = P.slot:FindFirstChild("Napis")
	if l and P.kolor == self.S.gryz then
		l.TextColor3 = self.S.obrys
		l:FindFirstChildOfClass("UIStroke").Color = self.S.tekst
	end
	P.podpis.Visible = typ == "obraz" and napis ~= nil
	P.podpisN.Text = napis or ""
end

-- wciśnięcie: skala 0,92, płytka o 15% ciemniejsza, bez cienia (0,08 s); z klawiatury / prób — krótki impuls
function H:wcisnij(P, tak: boolean)
	P.trzymany = tak
	if tak then
		P.wcisniety = 0.1
	end
end

-- stan przycisku: odnowa (sekundy pozostałe, całość), zamknięty (kłódka, płytka #463C58), ikona i napis
function H:stanPrzycisku(P, o)
	local S = self.S
	if o.zamkniety then
		P.slot.Visible = true
		if not P.zamkniety then
			P.zamkniety = true
			P.plytka.BackgroundColor3 = S.zamkniety
			self:ustawIkone(P, "zablokowane", nil)
		end
		H.ustawWycinek(P.wycinek, 0)
		P.sekundy.Visible = false
		P.odnowaByla = false
		return
	end
	if P.zamkniety then
		P.zamkniety = false
		P.plytka.BackgroundColor3 = P.kolor
	end
	if o.ikona then
		self:ustawIkone(P, o.ikona, o.napis)
	end
	local pozost = math.max(0, o.odnowa or 0)
	local p = if (o.calosc or 0) > 0 then pozost / o.calosc else 0
	H.ustawWycinek(P.wycinek, p)
	local pokaz = pozost > 0.05 and (o.calosc or 0) >= 1
	P.sekundy.Visible = pokaz
	-- napis zastępczy nie może nachodzić na sekundy odnowy (obraz ikony zostaje pod wycinkiem)
	if P.slot:GetAttribute("IkonaTyp") == "napis" then
		P.slot.Visible = not pokaz
	end
	if pokaz then
		P.sekundy.Text = tostring(math.ceil(pozost))
	end
	if pozost > 0.05 then
		P.odnowaByla = true
	elseif P.odnowaByla then
		P.odnowaByla = false
		P.blyskT = 0 -- koniec odnowy: błysk pierścienia żaru 0,15 s
		self.licznikBlyskow = (self.licznikBlyskow or 0) + 1
	end
	P.p = p
end

function H:zbudujPrzyciski()
	local S, UI, D = self.S, self.UI, self.D
	-- środki przycisków względem prawego dolnego rogu (pt wzoru), łuk wokół BITE; odstępy ≥ 10 pt
	self.gryz = self:przycisk("Gryz", Vector2.new(-78, -84), 103, S.gryz, "bite", UI.gryz)
	self.zryw = self:przycisk("Zryw", Vector2.new(-176, -62), 68, S.zryw, "dash", UI.zryw)
	self.ogien = self:przycisk("Ogien", Vector2.new(-164, -150), 68, S.ogien, "ember_spit", nil)
	self.moc = self:przycisk("Moc", Vector2.new(-73, -180), 68, S.moc, "tail_sweep", nil)
	self.ogien.linia, self.moc.linia = "ogien", "moc"
	-- pigułki „<ZDOLNOŚĆ> at <STADIUM>” nad przyciskami (zamknięta linia albo następna wersja)
	self.nastOgien = self:pigulka("OgienNast", Vector2.new(-112, -194))
	self.nastMoc = self:pigulka("MocNast", Vector2.new(-20, -224))
	local _ = D
end

function H:pigulka(nazwa: string, prawyDol: Vector2)
	local S = self.S
	local R = self.c.warstwa(nazwa, Vector2.new(1, 1), UDim2.new(1, prawyDol.X, 1, prawyDol.Y), Vector2.new(150, 20))
	local t = self:nowy("Frame", { Name = "Tlo", Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.pas, BackgroundTransparency = 0.08 }, R)
	self:rog(t)
	self:obrys(t, 2)
	local slot = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(4, 2), Size = UDim2.fromOffset(16, 16), BackgroundTransparency = 1, ZIndex = 4 }, t)
	self:ikona(slot, "zablokowane")
	local n = self:tekst(t, "", UDim2.fromOffset(23, 2), UDim2.new(1, -28, 1, -4), 9, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
	R.Visible = false
	return { ramka = R, napis = n, n1 = n, n2 = n }
end

-- ---------------------------------------------------------------- panel legowiska
function H:zakladka(rodzic: Instance, x: number, tekst: string, tab: string)
	local S = self.S
	local b = self:nowy("TextButton", { Name = "Zakladka", Position = UDim2.fromOffset(x, 0), Size = UDim2.fromOffset(120, 54), BackgroundTransparency = 1, Text = "",
		AutoButtonColor = false, ZIndex = 5 }, rodzic)
	local p = self:nowy("Frame", { Name = "Pigulka", Position = UDim2.fromOffset(0, 10), Size = UDim2.fromOffset(120, 26), BackgroundColor3 = S.karta, ZIndex = 5 }, b)
	self:rog(p)
	self:obrys(p, 2)
	local l = self:tekst(p, tekst, UDim2.fromOffset(6, 3), UDim2.new(1, -12, 1, -6), 12, S.tekst, self.fTytul)
	l.ZIndex = 6
	b.Activated:Connect(function()
		self:pokazZakladke(tab)
	end)
	return { b = b, p = p }
end

function H:pokazZakladke(tab: string)
	local P = self.panel
	P.tabT.Visible = tab == "T"
	P.tabU.Visible = tab == "U"
	P.zakT.p.BackgroundColor3 = if tab == "T" then self.S.zar else self.S.karta
	P.zakU.p.BackgroundColor3 = if tab == "U" then self.S.zar else self.S.karta
end

function H:zbudujPanel()
	local c, S, UI, D = self.c, self.S, self.UI, self.D
	local NF = #D.formy
	local P = {}
	self.panel = P
	-- panel 697 × 345 pt wzoru (makieta 1280 × 590 px), na środku ekranu
	local R = self:nowy("Frame", { Name = "PanelLegowiska", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromOffset(697, 392),
		BackgroundTransparency = 1, ZIndex = 20, Visible = false }, c.ekran)
	table.insert(c.skale, self:nowy("UIScale", { Scale = c.skalaEkranu() }, R))
	P.ramka = R
	local tlo = self:plytka(R, "Tlo", UDim2.fromOffset(0, 0), UDim2.fromScale(1, 1), S.panel, 16, 3)
	tlo.ZIndex = 20
	-- pas tytułu i linia żaru
	local pas = self:nowy("Frame", { Name = "Pas", Size = UDim2.new(1, 0, 0, 48), BackgroundColor3 = S.pas, ZIndex = 21 }, tlo)
	self:rog(pas, 16)
	self:nowy("Frame", { Name = "PasDol", Position = UDim2.fromOffset(0, 30), Size = UDim2.new(1, 0, 0, 18), BackgroundColor3 = S.pas, BorderSizePixel = 0, ZIndex = 21 }, tlo)
	self:nowy("Frame", { Name = "LiniaZaru", Position = UDim2.fromOffset(0, 48), Size = UDim2.new(1, 0, 0, 4), BackgroundColor3 = S.zar, BorderSizePixel = 0, ZIndex = 22 }, tlo)
	local tyt = self:tekst(tlo, UI.legowisko_tytul, UDim2.fromOffset(18, 8), UDim2.fromOffset(160, 32), 22, S.tekst, self.fTytul, Enum.TextXAlignment.Left)
	tyt.ZIndex = 23
	P.zakT = self:zakladka(tlo, 186, UI.trofea, "T")
	P.zakU = self:zakladka(tlo, 314, UI.ulepszenia, "U")
	for _, z in { P.zakT, P.zakU } do
		z.b.ZIndex = 23
		z.p.ZIndex = 23
		for _, d in z.p:GetDescendants() do
			if d:IsA("GuiObject") then
				d.ZIndex = 24
			end
		end
	end
	-- trofea bossa (korona) i złoto w pasie
	local bossS = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(442, 12), Size = UDim2.fromOffset(24, 24), BackgroundTransparency = 1, ZIndex = 23 }, tlo)
	self:ikona(bossS, "korona")
	P.boss = self:tekst(tlo, "", UDim2.fromOffset(468, 14), UDim2.fromOffset(60, 20), 11, S.tekst2, self.fLiczby, Enum.TextXAlignment.Left)
	P.boss.ZIndex = 23
	local zp = self:plytka(tlo, "PigulkaZlota", UDim2.fromOffset(532, 11), UDim2.fromOffset(96, 26), S.karta)
	zp.ZIndex = 23
	local zi = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(3, 2), Size = UDim2.fromOffset(22, 22), BackgroundTransparency = 1, ZIndex = 24 }, zp)
	self:ikona(zi, "moneta")
	P.zloto = self:tekst(zp, "0", UDim2.fromOffset(28, 3), UDim2.fromOffset(64, 20), 13, S.tekst, self.fLiczby, Enum.TextXAlignment.Left)
	P.zloto.ZIndex = 25
	-- zamknij: kółko 30 pt, pole dotyku 54 pt
	local x = self:nowy("TextButton", { Name = "Zamknij", Position = UDim2.fromOffset(640, -3), Size = UDim2.fromOffset(54, 54), BackgroundTransparency = 1, Text = "",
		AutoButtonColor = false, ZIndex = 23 }, tlo)
	local xk = self:nowy("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromOffset(30, 30), BackgroundColor3 = S.zycie,
		ZIndex = 23 }, x)
	self:rog(xk)
	self:obrys(xk, 2)
	local xl = self:tekst(xk, UI.zamknij, UDim2.fromScale(0.15, 0.1), UDim2.fromScale(0.7, 0.8), 16, S.tekst, self.fTytul)
	xl.ZIndex = 24
	P.zamknij = x
	-- zakładka TROPHIES: karty 4 × 2 i kolumna ulepszeń; linia szans
	P.tabT = self:nowy("Frame", { Name = "TabTrofea", Position = UDim2.fromOffset(0, 52), Size = UDim2.new(1, 0, 1, -52), BackgroundTransparency = 1, ZIndex = 21 }, tlo)
	P.tabU = self:nowy("Frame", { Name = "TabUlepszenia", Position = UDim2.fromOffset(0, 52), Size = UDim2.new(1, 0, 1, -52), BackgroundTransparency = 1, ZIndex = 21,
		Visible = false }, tlo)
	P.trofea = {}
	for f = 1, NF do
		local kol, wie = (f - 1) % 4, (f - 1) // 4
		local k = self:nowy("TextButton", { Name = "Trofeum" .. f, Position = UDim2.fromOffset(14 + kol * 113, 56 + wie * 124), Size = UDim2.fromOffset(105, 116),
			BackgroundColor3 = S.karta, Text = "", AutoButtonColor = false, ZIndex = 22 }, P.tabT)
		self:rog(k, 11)
		local ob = self:obrys(k, 2)
		local vf = self:okno(k, "Okno", UDim2.fromOffset(10, 2), UDim2.fromOffset(85, 64))
		vf.ZIndex = 23
		local zn = self:tekst(k, "?", UDim2.fromOffset(30, 10), UDim2.fromOffset(45, 46), 30, S.tekst2, self.fTytul)
		zn.ZIndex = 24
		local nz = self:tekst(k, "", UDim2.fromOffset(4, 66), UDim2.fromOffset(97, 14), 10, S.tekst, self.fEtyk)
		nz.ZIndex = 24
		local pips = {}
		for i = 1, 5 do
			local p = self:nowy("Frame", { Position = UDim2.fromOffset(8 + (i - 1) * 10, 85), Size = UDim2.fromOffset(7, 7), BackgroundColor3 = S.pas, BorderSizePixel = 0,
				ZIndex = 24 }, k)
			pips[i] = p
		end
		local doch = self:tekst(k, "", UDim2.fromOffset(58, 81), UDim2.fromOffset(43, 14), 10, S.kup, self.fLiczby, Enum.TextXAlignment.Right)
		doch.ZIndex = 24
		local cena = self:nowy("Frame", { Name = "KupPoziom", Position = UDim2.fromOffset(7, 97), Size = UDim2.fromOffset(91, 16), BackgroundColor3 = S.kup, ZIndex = 24 }, k)
		self:rog(cena)
		self:obrys(cena, 2)
		local ci = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(3, 1), Size = UDim2.fromOffset(14, 14), BackgroundTransparency = 1, ZIndex = 25 }, cena)
		self:ikona(ci, "moneta")
		local cn = self:tekst(cena, "", UDim2.fromOffset(18, 1), UDim2.new(1, -22, 1, -2), 10, S.tekst, self.fLiczby)
		cn.ZIndex = 26
		local odz = self:nowy("Frame", { Name = "Wariant", Position = UDim2.fromOffset(84, -5), Size = UDim2.fromOffset(24, 24), BackgroundTransparency = 1, ZIndex = 26,
			Visible = false }, k)
		local zam = self:nowy("Frame", { Name = "Zamek", Position = UDim2.fromOffset(82, 3), Size = UDim2.fromOffset(20, 20), BackgroundTransparency = 1, ZIndex = 26 }, k)
		self:ikona(zam, "zablokowane")
		P.trofea[f] = { ramka = k, kup = k, obrys = ob, vf = vf, znak = zn, nazwa = nz, pips = pips, dochod = doch, cena = cena, cenaN = cn, wariant = odz,
			zamek = zam, stan = "", wariantId = "" }
	end
	-- kolumna ulepszeń (TROPHIES) i duże karty (UPGRADES)
	P.karty = {}
	P.duze = {}
	for i, U in D.ulepszenia do
		P.karty[U.id] = self:kartaUlepszenia(P.tabT, U, UDim2.fromOffset(470, 56 + (i - 1) * 82), false)
		P.duze[U.id] = self:kartaUlepszenia(P.tabU, U, UDim2.fromOffset(14 + (i - 1) * 226, 10), true)
	end
	-- szanse wariantów
	local sz = self:nowy("Frame", { Name = "Szanse", Position = UDim2.fromOffset(14, 306), Size = UDim2.fromOffset(669, 30), BackgroundColor3 = S.pas, ZIndex = 22 }, P.tabT)
	self:rog(sz)
	local st = self:tekst(sz, UI.szanse_tytul or "VARIANT ODDS", UDim2.fromOffset(14, 7), UDim2.fromOffset(100, 16), 10, S.tekst2, self.fEtyk, Enum.TextXAlignment.Left)
	st.ZIndex = 23
	for i, W in D.warianty do
		local x0 = 122 + (i - 1) * 136
		local ik = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(x0, 5), Size = UDim2.fromOffset(20, 20), BackgroundTransparency = 1, ZIndex = 23 }, sz)
		self:ikona(ik, W.ikona or ("wariant_" .. W.id))
		local proc = W.szansa * 100
		local t = string.format("%s %s%%  x%d", W.nazwa, if proc >= 1 then string.format("%d", proc) else string.format("%.1f", proc), W.x)
		local l = self:tekst(sz, t, UDim2.fromOffset(x0 + 24, 7), UDim2.fromOffset(108, 16), 10, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
		l.ZIndex = 23
	end
	P.info = self:tekst(P.tabU, UI.tylko_w_legowisku, UDim2.fromOffset(14, 254), UDim2.fromOffset(669, 18), 11, S.tekst2, self.fEtyk)
	P.info.ZIndex = 23
	-- linie smoków: przyciski z polem dotyku 44 pt, widoczna pigułka 22 pt
	P.chipy = {}
	P.pokazLinia = nil
	for i, LI in (self.D.odrodzenie and self.D.odrodzenie.linie) or {} do
		local b = self:nowy("TextButton", { Name = "Linia_" .. LI.id, Position = UDim2.fromOffset(14 + (i - 1) * 113, 0), Size = UDim2.fromOffset(105, 54),
			BackgroundTransparency = 1, Text = "", AutoButtonColor = false, ZIndex = 23 }, P.tabT)
		local pl = self:nowy("Frame", { Name = "Pigulka", Position = UDim2.fromOffset(0, 14), Size = UDim2.fromOffset(105, 26), BackgroundColor3 = S.karta, ZIndex = 23 }, b)
		self:rog(pl)
		local ob = self:obrys(pl, 2, rgb(LI.kolor))
		local l = self:tekst(pl, LI.nazwa, UDim2.fromOffset(6, 3), UDim2.new(1, -12, 1, -6), 12, rgb(LI.kolor), self.fTytul)
		l.ZIndex = 24
		P.chipy[i] = { b = b, p = pl, obrys = ob, napis = l, LI = LI }
		b.Activated:Connect(function()
			P.pokazLinia = i
			if self.ostatniPanel then
				self:panelOdswiez(self.ostatniPanel)
			end
		end)
	end
	self:pokazZakladke("T")
end

function H:kartaUlepszenia(rodzic: Instance, U, poz: UDim2, duza: boolean)
	local S = self.S
	local roz = if duza then UDim2.fromOffset(216, 236) else UDim2.fromOffset(213, 74)
	local k = self:nowy("Frame", { Name = "Karta_" .. U.id, Position = poz, Size = roz, BackgroundColor3 = S.karta, ZIndex = 22 }, rodzic)
	self:rog(k, 11)
	self:obrys(k, 2)
	local K = { ramka = k, U = U, kropki = {} }
	local ik = self:nowy("Frame", { Name = "Ikona", Position = if duza then UDim2.fromOffset(72, 10) else UDim2.fromOffset(6, 10), Size = if duza
		then UDim2.fromOffset(72, 72) else UDim2.fromOffset(54, 54), BackgroundTransparency = 1, ZIndex = 23 }, k)
	local plyt = self:nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.pas, ZIndex = 23 }, ik)
	self:rog(plyt, 10)
	local slot = self:nowy("Frame", { Name = "Slot", Position = UDim2.fromScale(0.08, 0.08), Size = UDim2.fromScale(0.84, 0.84), BackgroundTransparency = 1, ZIndex = 24 }, ik)
	self:ikona(slot, U.ikona or ("ulepszenie_" .. U.id), nil, S.krysztal)
	if duza then
		K.nazwa = self:tekst(k, U.nazwa, UDim2.fromOffset(8, 86), UDim2.new(1, -16, 0, 24), 18, S.tekst, self.fTytul)
		K.opis = self:tekst(k, U.opis, UDim2.fromOffset(8, 110), UDim2.new(1, -16, 0, 16), 11, S.tekst2, self.fEtyk)
		K.lv = self:tekst(k, "", UDim2.fromOffset(8, 130), UDim2.new(1, -16, 0, 16), 11, S.tekst2, self.fLiczby)
		K.wart = self:tekst(k, "", UDim2.fromOffset(8, 148), UDim2.new(1, -16, 0, 18), 13, S.krysztal, self.fLiczby)
	else
		K.nazwa = self:tekst(k, U.nazwa, UDim2.fromOffset(66, 6), UDim2.fromOffset(90, 18), 14, S.tekst, self.fTytul, Enum.TextXAlignment.Left)
		K.lv = self:tekst(k, "", UDim2.fromOffset(150, 7), UDim2.fromOffset(56, 15), 10, S.tekst2, self.fLiczby, Enum.TextXAlignment.Right)
	end
	for _, d in k:GetDescendants() do
		if d:IsA("TextLabel") then
			d.ZIndex = 24
		end
	end
	local pt = self:nowy("Frame", { Name = "Pasek", Position = if duza then UDim2.fromOffset(18, 170) else UDim2.fromOffset(66, 28), Size = if duza
		then UDim2.fromOffset(180, 9) else UDim2.fromOffset(140, 9), BackgroundColor3 = S.pas, ZIndex = 23 }, k)
	self:rog(pt)
	local pw = self:nowy("Frame", { Size = UDim2.fromScale(0, 1), BackgroundColor3 = S.krysztal, BorderSizePixel = 0, ZIndex = 24 }, pt)
	self:rog(pw)
	K.pasek = pw
	-- przycisk ceny: pole dotyku 54 pt, widoczna pigułka w środku
	local b = self:nowy("TextButton", { Name = "Kup", Position = if duza then UDim2.fromOffset(28, 178) else UDim2.fromOffset(100, 20), Size = if duza
		then UDim2.fromOffset(160, 54) else UDim2.fromOffset(110, 54), BackgroundTransparency = 1, Text = "", AutoButtonColor = false, ZIndex = 25 }, k)
	local p = self:nowy("Frame", { Name = "Pigulka", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, if duza then 0.5 else 0.62),
		Size = if duza then UDim2.fromOffset(150, 34) else UDim2.fromOffset(100, 24), BackgroundColor3 = S.kup, ZIndex = 25 }, b)
	self:rog(p)
	self:obrys(p, 2)
	local ci = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(4, 3), Size = if duza then UDim2.fromOffset(28, 28) else UDim2.fromOffset(18, 18),
		BackgroundTransparency = 1, ZIndex = 26 }, p)
	self:ikona(ci, "moneta")
	local n = self:tekst(p, "", UDim2.fromOffset(if duza then 34 else 24, 2), UDim2.new(1, if duza then -40 else -30, 1, -4), if duza then 16 else 12, S.obrys, self.fLiczby)
	n.ZIndex = 27
	n:FindFirstChildOfClass("UIStroke").Enabled = false
	K.przycisk = b
	K.pigulka = p
	K.napis = n
	return K
end

-- odświeżenie panelu z danych gracza
function H:panelOdswiez(s)
	local D, S, UI = self.D, self.S, self.UI
	local P = self.panel
	local G = D.legowisko
	self.ostatniPanel = s
	P.zloto.Text = H.liczba(s.zl)
	P.boss.Text = string.format("%d/5", s.bossT)
	-- linia w kartach: wybrana przyciskiem albo obecna; inne linie z zapisu (bez zakupu poziomów)
	local obecna = s.linia or 1
	local l = P.pokazLinia or obecna
	local mf, tro, war = s.mf, s.tro, s.warianty
	local inna = l ~= obecna
	if inna then
		local z = s.linie and s.linie[tostring(l)]
		mf, tro, war = if z then z.m else 0, {}, {}
		for f = 1, #D.formy do
			tro[f] = (z and z.t and z.t[f]) or 1
			war[f] = z and z.w and s.wariantD(z.w[f]) or nil
		end
	end
	for i, C in P.chipy do
		local z = s.linie and s.linie[tostring(i)]
		local ma = i == obecna or (z ~= nil and z.m > 0)
		C.p.BackgroundColor3 = if i == l then rgb(C.LI.kolor) else S.karta
		C.napis.TextColor3 = if i == l then S.obrys else rgb(C.LI.kolor)
		C.napis.Text = if ma then C.LI.nazwa else "?"
	end
	P.liniaPokazana = l
	for f, T in P.trofea do
		local zdobyta = f <= mf
		local lv = tro[f] or 1
		local W0 = war[f]
		local klucz = (if zdobyta then "Z" else "?") .. (if W0 then W0.id else "") .. "/" .. tostring(l)
		if T.stan ~= klucz then
			T.stan = klucz
			self:portret(T.vf, f, { ciemny = not zdobyta, wariant = if zdobyta then W0 else nil, linia = l })
			T.ramka.BackgroundColor3 = if zdobyta then S.karta else rgb("241C30")
			T.zamek.Visible = not zdobyta
			T.wariant.Visible = zdobyta and W0 ~= nil
			if W0 then
				self:ikona(T.wariant, W0.ikona or ("wariant_" .. W0.id))
			end
		end
		T.vf.Visible = true
		T.znak.Visible = false
		T.nazwa.Text = if zdobyta then D.formy[f].nazwa else (UI.nieznane or "???")
		for i, p in T.pips do
			p.Visible = zdobyta
			p.BackgroundColor3 = if i <= lv then S.zar_gora else S.pas
		end
		T.dochod.Visible = zdobyta
		T.dochod.Text = "+" .. tostring(math.floor(D.formy[f].trofeum * G.poziomy_x[lv] * (if W0 then W0.x else 1) * 10 + 0.5) / 10) .. "/s"
		local cena = if zdobyta and G.ceny_x[lv] and not inna then math.floor(G.ceny_x[lv] * D.formy[f].trofeum) else nil
		T.cena.Visible = zdobyta and not inna
		T.cenaN.Text = if cena then H.liczba(cena) else UI.maks
		local stac = cena ~= nil and s.wDomu and s.zl >= cena
		T.cena.BackgroundColor3 = if stac then S.kup else S.zamkniety
		T.cenaN.TextColor3 = if stac then S.obrys else S.tekst2
		T.obrys.Color = if stac then S.kup else S.obrys
	end
	for _, zbior in { P.karty, P.duze } do
		for id, K in zbior do
			local p = s.poz[id] or 1
			local U = K.U
			local maks = #U.ceny + 1
			K.pasek.Size = UDim2.fromScale(p / maks, 1)
			K.lv.Text = string.format(UI.lv or "Lv %d", p)
			if K.wart then
				K.wart.Text = s.opisWartosci(U, p)
			end
			local cena = U.ceny[p]
			if not cena then
				K.napis.Text = UI.maks
				K.pigulka.BackgroundColor3 = S.zamkniety
				K.napis.TextColor3 = S.tekst2
			else
				K.napis.Text = H.liczba(cena)
				local stac = s.zl >= cena
				K.pigulka.BackgroundColor3 = if stac then S.kup else S.zamkniety
				K.napis.TextColor3 = if stac then S.obrys else S.tekst2
			end
		end
	end
	P.info.Text = if s.wDomu then UI.w_legowisku else UI.tylko_w_legowisku
end

-- 12450 → „12 450”
function H.liczba(n: number): string
	local s = tostring(math.floor(n))
	local w = string.reverse(s)
	w = string.gsub(w, "(%d%d%d)", "%1 ")
	w = string.reverse(w)
	if string.sub(w, 1, 1) == " " then
		w = string.sub(w, 2)
	end
	return w
end

-- ---------------------------------------------------------------- odsłona ewolucji
function H:zbudujOdslone()
	local c, S, UI = self.c, self.S, self.UI
	local O = {}
	self.odsl = O
	local R = self:nowy("Frame", { Name = "Odslona", Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.cien, BackgroundTransparency = 1, ZIndex = 40, Visible = false,
		Active = false }, c.ekran)
	O.ramka = R
	local srodek = self:nowy("Frame", { Name = "Srodek", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromOffset(844, 390),
		BackgroundTransparency = 1, ZIndex = 40 }, R)
	table.insert(c.skale, self:nowy("UIScale", { Scale = c.skalaEkranu() }, srodek))
	-- poświata za smokiem
	local pos = self:nowy("Frame", { Name = "Poswiata", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(470, 196), Size = UDim2.fromOffset(420, 300),
		BackgroundColor3 = S.zar_gora, BackgroundTransparency = 0.82, ZIndex = 40 }, srodek)
	self:rog(pos)
	O.poswiata = pos
	O.gora = self:tekst(srodek, UI.ewoluowal or "EVOLVED!", UDim2.fromOffset(322, 22), UDim2.fromOffset(200, 24), 18, S.zar_gora, self.fTytul)
	O.nazwa = self:tekst(srodek, "", UDim2.fromOffset(122, 44), UDim2.fromOffset(600, 56), 46, Color3.new(1, 1, 1), self.fTytul)
	self:gradient(O.nazwa, S.tekst, S.zar)
	O.nazwa:FindFirstChildOfClass("UIStroke").Thickness = 3
	O.nazwa:FindFirstChildOfClass("UIStroke").Color = rgb("2B1640")
	O.nazwaSkala = self:nowy("UIScale", { Scale = 1 }, O.nazwa)
	-- kokon (poświata) i strzałki
	local kok = self:nowy("Frame", { Name = "Kokon", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromOffset(212, 220), Size = UDim2.fromOffset(90, 108),
		BackgroundColor3 = rgb("FFF3B0"), ZIndex = 41 }, srodek)
	self:rog(kok, 40)
	O.kokonObrys = self:nowy("UIStroke", { Thickness = 5, Color = S.zar_gora }, kok)
	O.kokonSkala = self:nowy("UIScale", { Scale = 1 }, kok)
	O.kokon = kok
	O.strzalki = self:tekst(srodek, ">>>", UDim2.fromOffset(268, 204), UDim2.fromOffset(60, 30), 28, S.zar_gora, self.fTytul)
	-- portret nowego stadium (pełny rig)
	O.portret = self:okno(srodek, "Portret", UDim2.fromOffset(318, 92), UDim2.fromOffset(330, 214))
	O.portret.ZIndex = 42
	O.portretSkala = self:nowy("UIScale", { Scale = 1 }, O.portret)
	-- tabliczka nowej mocy
	local pl = self:plytka(srodek, "NowaMoc", UDim2.fromOffset(262, 310), UDim2.fromOffset(322, 42), S.pas)
	pl.ZIndex = 43
	O.plytka = pl
	O.mocSlot = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(6, 4), Size = UDim2.fromOffset(34, 34), BackgroundColor3 = S.ogien, ZIndex = 44 }, pl)
	self:rog(O.mocSlot)
	O.mocIkona = self:nowy("Frame", { Name = "Slot", Position = UDim2.fromScale(0.08, 0.08), Size = UDim2.fromScale(0.84, 0.84), BackgroundTransparency = 1, ZIndex = 45 },
		O.mocSlot)
	O.mocGora = self:tekst(pl, UI.nowa_moc or "NEW POWER", UDim2.fromOffset(48, 4), UDim2.fromOffset(200, 13), 9, S.tekst2, self.fEtyk, Enum.TextXAlignment.Left)
	O.mocNapis = self:tekst(pl, "", UDim2.fromOffset(48, 17), UDim2.fromOffset(266, 20), 13, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
	for _, l in { O.mocGora, O.mocNapis } do
		l.ZIndex = 45
	end
	-- następne stadium: sylwetka w kole + „?” + NEXT
	local nk = self:plytka(srodek, "Nastepne", UDim2.fromOffset(600, 308), UDim2.fromOffset(46, 46), rgb("6A5C88"))
	nk.ZIndex = 43
	O.nast = self:okno(nk, "Okno", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
	O.nast.ZIndex = 44
	self:rog(O.nast)
	local q = self:tekst(nk, "?", UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.5, 0.5), 18, S.zar_gora, self.fTytul)
	q.ZIndex = 46
	O.nastKolo = nk
	O.nastNapis = self:tekst(srodek, UI.nastepna or "NEXT", UDim2.fromOffset(650, 322), UDim2.fromOffset(44, 16), 10, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
	-- CONTINUE (pole dotyku 54 pt)
	local b = self:nowy("TextButton", { Name = "Dalej", Position = UDim2.fromOffset(352, 352), Size = UDim2.fromOffset(140, 54), BackgroundTransparency = 1, Text = "",
		AutoButtonColor = false, ZIndex = 47 }, srodek)
	local bp = self:nowy("Frame", { Name = "Pigulka", Position = UDim2.fromOffset(0, 6), Size = UDim2.fromOffset(140, 34), BackgroundColor3 = Color3.new(1, 1, 1), ZIndex = 47 }, b)
	self:rog(bp)
	self:obrys(bp, 2)
	self:gradient(bp, S.zar_gora, S.zar)
	local bl = self:tekst(bp, UI.dalej or "CONTINUE", UDim2.fromOffset(8, 4), UDim2.new(1, -16, 1, -8), 15, S.tekst, self.fTytul)
	bl.ZIndex = 48
	O.dalej = b
	b.Activated:Connect(function()
		self:odslonaKoniec()
	end)
	O.faza = nil
	O.t = 0
end

local function widac(o: GuiObject, t: number, od: number, czas: number?): number
	-- 0 → 1 w czasie od…od+czas
	local f = math.clamp((t - od) / (czas or 0.2), 0, 1)
	o.Visible = f > 0
	return f
end

function H:odslonaKokon(f: number)
	local O = self.odsl
	O.faza = "kokon"
	O.t = 0
	O.ramka.Visible = true
	O.nazwa.Text = ""
	O.gora.Visible = false
	O.strzalki.Visible = false
	O.plytka.Visible = false
	O.nastKolo.Visible = false
	O.nastNapis.Visible = false
	O.dalej.Visible = false
	O.kokon.Visible = true
	O.kokon.Position = UDim2.fromOffset(422, 210)
	O.portret.Visible = false
	local _ = f
end

-- moce: lista zdolności odblokowanych na tym stadium ({ nazwa, opis, ikona, linia }); W0 wariant
function H:odslonaPokaz(f: number, nowa: boolean, W0, moce, czas: number)
	local O, D, UI, S = self.odsl, self.D, self.UI, self.S
	local NF = #D.formy
	O.faza = "pokaz"
	O.t = 0
	O.czas = czas
	O.ramka.Visible = true
	O.gora.Text = if W0 then string.format(UI.wariant, W0.nazwa) elseif nowa then (UI.ewoluowal or "EVOLVED!") else UI.znowu
	O.gora.TextColor3 = if W0 then rgb(W0.kolor) else S.zar_gora
	O.nazwa.Text = D.formy[f].nazwa
	self:portret(O.portret, f, { pelny = true, wariant = W0, calosc = true, odl = 0.62 })
	local A = moce and moce[1]
	if A then
		O.mocGora.Text = UI.nowa_moc or "NEW POWER"
		O.mocNapis.Text = A.nazwa .. (if A.opis then "  -  " .. A.opis else "")
		O.mocSlot.BackgroundColor3 = if A.linia == "moc" then S.moc else S.ogien
		self:ikona(O.mocIkona, A.ikona or "", A.krotko or A.nazwa)
	else
		O.mocGora.Text = UI.legowisko_tytul
		O.mocNapis.Text = string.format(UI.trofeum_toast, D.formy[f].trofeum)
		O.mocSlot.BackgroundColor3 = S.zloto
		self:ikona(O.mocIkona, "skarb")
	end
	if f < NF then
		self:portret(O.nast, f + 1, { ciemny = true })
	end
	O.maNast = f < NF
	O.kokon.Position = UDim2.fromOffset(212, 220)
end

function H:odrodzenieCeremonia(linia: number, n: number, mnoznik: number, czas: number)
	local O, UI, S = self.odsl, self.UI, self.S
	local LI = self.D.odrodzenie.linie[linia]
	O.faza = "odrodzenie"
	O.t = 0
	O.czas = czas + 2.4
	O.ramka.Visible = true
	O.gora.Visible = true
	O.gora.Text = string.format(UI.odrodzenie, n)
	O.gora.TextColor3 = S.zar_gora
	O.nazwa.Text = LI.nazwa .. " LINE"
	O.nazwa.Visible = true
	O.kokon.Visible = true
	O.kokon.Position = UDim2.fromOffset(422, 212)
	O.kokon.BackgroundColor3 = Color3.new(1, 1, 1):Lerp(rgb(LI.kolor), 0.45)
	O.kokonObrys.Color = rgb(LI.kolor)
	O.strzalki.Visible = false
	O.portret.Visible = false
	O.nastKolo.Visible = false
	O.nastNapis.Visible = false
	O.dalej.Visible = false
	O.plytka.Visible = true
	O.mocGora.Text = UI.linia_nast
	O.mocNapis.Text = string.format(UI.odrodzenie_opis, LI.nazwa, mnoznik)
	O.mocSlot.BackgroundColor3 = rgb(LI.kolor)
	self:ikona(O.mocIkona, "korona")
end

function H:zbudujWydarzenia()
	local S = self.S
	local R = self.c.warstwa("Wydarzenie", Vector2.new(1, 0), UDim2.new(1, -146, 0, 76), Vector2.new(150, 24))
	local t = self:nowy("Frame", { Name = "Tlo", Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.pas, BackgroundTransparency = 0.08 }, R)
	self:rog(t)
	self.wydObrys = self:obrys(t, 2)
	self.wydNapis = self:tekst(t, "", UDim2.fromOffset(8, 3), UDim2.new(1, -16, 1, -6), 11, S.tekst, self.fLiczby)
	self.ramkaWyd = R
	R.Visible = false
end

function H:wydarzenie(tekst: string?, kolor: Color3?, aktywne: boolean)
	self.ramkaWyd.Visible = tekst ~= nil
	if tekst then
		self.wydNapis.Text = tekst
		self.wydNapis.TextColor3 = if aktywne then self.S.zar_gora else self.S.tekst
		self.wydObrys.Color = if aktywne then (kolor or self.S.zar) else self.S.obrys
	end
end

-- ---------------------------------------------------------------- retencja1: pigułka zadań dnia i ekran powitania
function H:zbudujZadania()
	local S = self.S
	local R = self.c.warstwa("Zadania", Vector2.new(0.5, 0), UDim2.new(0.5, -20, 0, 72), Vector2.new(230, 22))
	local t = self:nowy("Frame", { Name = "Tlo", Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.pas, BackgroundTransparency = 0.08 }, R)
	self:rog(t)
	self:obrys(t, 2)
	local ik = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(3, 1), Size = UDim2.fromOffset(20, 20), BackgroundColor3 = S.zar, ZIndex = 4 }, t)
	self:rog(ik)
	self.zadIle = self:tekst(ik, "0", UDim2.fromScale(0.1, 0.1), UDim2.fromScale(0.8, 0.8), 11, S.tekst, self.fLiczby)
	self.zadNapis = self:tekst(t, "", UDim2.fromOffset(28, 3), UDim2.new(1, -36, 1, -6), 10, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
	self.ramkaZadan = R
	R.Visible = false
end

-- zadania: [{ id, p, c, g }] → pigułka z pierwszym niegotowym zadaniem i liczbą gotowych
function H:zadania(lista)
	local UI = self.UI
	if not lista or #lista == 0 then
		self.ramkaZadan.Visible = false
		return ""
	end
	local gotowe, pierwsze = 0, nil
	for _, q in lista do
		if q.g then
			gotowe += 1
		elseif not pierwsze then
			pierwsze = q
		end
	end
	self.ramkaZadan.Visible = true
	self.zadIle.Text = string.format("%d/%d", gotowe, #lista)
	if pierwsze then
		local Q = self:zadanieDef(pierwsze.id)
		-- odczucie1: „Collect your hoard %d times” → „Collect your hoard 0/2” (bez osieroconego „times”)
		local t = Q and string.gsub((string.gsub(Q.tekst, " ?%%d times", "")), " ?%%d ?", " ") or pierwsze.id
		self.zadNapis.Text = string.format(UI.zadania_pigulka, t, pierwsze.p, pierwsze.c)
	else
		self.zadNapis.Text = UI.zadania_wszystkie
	end
	return self.zadNapis.Text
end

function H:zadanieDef(id: string)
	for _, q in self.D.zadania.pula do
		if q.id == id then
			return q
		end
	end
	return nil
end

function H:zbudujPowitanie()
	local c, S, UI = self.c, self.S, self.UI
	local P = {}
	self.pow = P
	local R = self:nowy("Frame", { Name = "Powitanie", Size = UDim2.fromScale(1, 1), BackgroundColor3 = S.cien, BackgroundTransparency = 0.4, ZIndex = 50,
		Visible = false, Active = false }, c.ekran)
	P.ramka = R
	local sr = self:nowy("Frame", { Name = "Srodek", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromOffset(620, 330),
		BackgroundTransparency = 1, ZIndex = 50 }, R)
	table.insert(c.skale, self:nowy("UIScale", { Scale = c.skalaEkranu() }, sr))
	local tlo = self:plytka(sr, "Tlo", UDim2.fromOffset(0, 0), UDim2.fromScale(1, 1), S.panel, 16, 3)
	tlo.ZIndex = 50
	local pas = self:nowy("Frame", { Name = "Pas", Size = UDim2.new(1, 0, 0, 46), BackgroundColor3 = S.pas, ZIndex = 51 }, tlo)
	self:rog(pas, 16)
	self:nowy("Frame", { Position = UDim2.fromOffset(0, 30), Size = UDim2.new(1, 0, 0, 16), BackgroundColor3 = S.pas, BorderSizePixel = 0, ZIndex = 51 }, tlo)
	self:nowy("Frame", { Position = UDim2.fromOffset(0, 46), Size = UDim2.new(1, 0, 0, 4), BackgroundColor3 = S.zar, BorderSizePixel = 0, ZIndex = 52 }, tlo)
	P.tytul = self:tekst(tlo, UI.witaj, UDim2.fromOffset(18, 7), UDim2.fromOffset(300, 32), 22, S.tekst, self.fTytul, Enum.TextXAlignment.Left)
	P.seria = self:tekst(tlo, "", UDim2.fromOffset(330, 11), UDim2.fromOffset(272, 24), 16, S.zar_gora, self.fTytul, Enum.TextXAlignment.Right)
	P.tytul.ZIndex, P.seria.ZIndex = 53, 53
	-- kalendarz 7 dni
	P.dni = {}
	for d = 1, 7 do
		local N = self.D.seria.nagrody[d]
		local k = self:nowy("Frame", { Name = "Dzien" .. d, Position = UDim2.fromOffset(16 + (d - 1) * 84, 60), Size = UDim2.fromOffset(78, 92), BackgroundColor3 = S.karta,
			ZIndex = 51 }, tlo)
		self:rog(k, 11)
		local ob = self:obrys(k, 2)
		local dz = self:tekst(k, string.format(UI.dzien, d), UDim2.fromOffset(4, 4), UDim2.new(1, -8, 0, 14), 10, S.tekst2, self.fEtyk)
		local slot = self:nowy("Frame", { Name = "Ikona", Position = UDim2.fromOffset(21, 20), Size = UDim2.fromOffset(36, 36), BackgroundTransparency = 1, ZIndex = 52 }, k)
		self:ikona(slot, if N.jajo then "korona" else "moneta")
		local opis = (if N.zloto then "+" .. H.liczba(N.zloto) else "") .. (if N.boost_s then "\n" .. string.format(UI.boost, N.boost_s // 60) else "")
			.. (if N.jajo then "\nEGG" else "")
		local o = self:tekst(k, opis, UDim2.fromOffset(4, 58), UDim2.new(1, -8, 0, 30), 10, S.zloto, self.fLiczby)
		for _, l in { dz, o } do
			l.ZIndex = 53
		end
		local znak = self:tekst(k, "OK", UDim2.fromOffset(46, -6), UDim2.fromOffset(36, 18), 12, S.kup, self.fTytul)
		znak.ZIndex = 54
		P.dni[d] = { ramka = k, obrys = ob, znak = znak }
	end
	P.nagroda = self:tekst(tlo, "", UDim2.fromOffset(16, 158), UDim2.fromOffset(588, 18), 12, S.kup, self.fEtyk)
	-- zadania dnia
	P.zadTytul = self:tekst(tlo, UI.zadania_tytul, UDim2.fromOffset(16, 180), UDim2.fromOffset(300, 18), 13, S.tekst, self.fTytul, Enum.TextXAlignment.Left)
	P.zad = {}
	for i = 1, 3 do
		local w = self:nowy("Frame", { Name = "Zadanie" .. i, Position = UDim2.fromOffset(16, 202 + (i - 1) * 30), Size = UDim2.fromOffset(588, 26),
			BackgroundColor3 = S.karta, ZIndex = 51 }, tlo)
		self:rog(w, 8)
		local n = self:tekst(w, "", UDim2.fromOffset(10, 4), UDim2.fromOffset(330, 18), 12, S.tekst, self.fEtyk, Enum.TextXAlignment.Left)
		local pt = self:nowy("Frame", { Position = UDim2.fromOffset(350, 9), Size = UDim2.fromOffset(120, 8), BackgroundColor3 = S.pas, ZIndex = 52 }, w)
		self:rog(pt)
		local pw = self:nowy("Frame", { Size = UDim2.fromScale(0, 1), BackgroundColor3 = S.krysztal, BorderSizePixel = 0, ZIndex = 53 }, pt)
		self:rog(pw)
		local nag = self:tekst(w, "", UDim2.fromOffset(480, 4), UDim2.fromOffset(100, 18), 11, S.zloto, self.fLiczby, Enum.TextXAlignment.Right)
		for _, l in { n, nag } do
			l.ZIndex = 53
		end
		P.zad[i] = { ramka = w, napis = n, pasek = pw, nagroda = nag }
	end
	-- CONTINUE (pole dotyku 54 pt)
	local b = self:nowy("TextButton", { Name = "Dalej", Position = UDim2.fromOffset(240, 290), Size = UDim2.fromOffset(140, 54), BackgroundTransparency = 1, Text = "",
		AutoButtonColor = false, ZIndex = 55 }, tlo)
	local bp = self:nowy("Frame", { Name = "Pigulka", Position = UDim2.fromOffset(0, 2), Size = UDim2.fromOffset(140, 32), BackgroundColor3 = Color3.new(1, 1, 1), ZIndex = 55 }, b)
	self:rog(bp)
	self:obrys(bp, 2)
	self:gradient(bp, S.zar_gora, S.zar)
	local bl = self:tekst(bp, UI.dalej or "CONTINUE", UDim2.fromOffset(8, 4), UDim2.new(1, -16, 1, -8), 15, S.tekst, self.fTytul)
	bl.ZIndex = 56
	P.dalej = b
	b.Activated:Connect(function()
		self:powitanieKoniec()
	end)
end

-- dane: { dni, nagroda, wariant, f, lepszy, zarobek, nowy }, zadania: [{ id, p, c, g }]
function H:powitanie(dane, zadania)
	local P, S, UI, D = self.pow, self.S, self.UI, self.D
	P.ramka.Visible = true
	P.t = 0
	P.tytul.Text = if dane.nowy then UI.witaj_nowy else UI.witaj
	P.seria.Text = string.format(UI.seria_dzien, dane.dni or 1)
	for d, K in P.dni do
		local dzis = d == dane.dni
		K.ramka.BackgroundColor3 = if dzis then S.zar else (if d < (dane.dni or 1) then S.pas else S.karta)
		K.obrys.Color = if dzis then S.zar_gora else S.obrys
		K.obrys.Thickness = if dzis then 3 else 2
		K.znak.Visible = d < (dane.dni or 1) or (dzis and dane.nagroda ~= nil)
	end
	local linie = {}
	if dane.nagroda then
		local N = dane.nagroda
		table.insert(linie, string.format(UI.dzien, dane.dni) .. ":")
		if N.zloto then
			table.insert(linie, "+" .. H.liczba(N.zloto) .. " gold")
		end
		if N.boost_s then
			table.insert(linie, string.format(UI.boost, N.boost_s // 60))
		end
		if dane.wariant then
			local W = nil
			for _, x in D.warianty do
				if x.id == dane.wariant then
					W = x
				end
			end
			table.insert(linie, (if W then W.nazwa else dane.wariant) .. " " .. D.formy[dane.f or 1].nazwa .. (if dane.lepszy then "!" else ""))
		end
	end
	if (dane.zarobek or 0) > 0 then
		table.insert(linie, "  " .. string.format(UI.hoard_nieobecny, dane.zarobek))
	end
	P.nagroda.Text = table.concat(linie, "  ")
	self:powitanieZadania(zadania)
end

function H:powitanieZadania(zadania)
	local P = self.pow
	for i, W in P.zad do
		local q = zadania and zadania[i]
		W.ramka.Visible = q ~= nil
		if q then
			local Q = self:zadanieDef(q.id)
			W.napis.Text = (if Q then string.format(Q.tekst, q.c) else q.id) .. string.format("  %d/%d", q.p, q.c)
			W.pasek.Size = UDim2.fromScale(math.clamp(q.p / math.max(1, q.c), 0, 1), 1)
			W.pasek.BackgroundColor3 = if q.g then self.S.kup else self.S.krysztal
			W.nagroda.Text = if Q then "+" .. H.liczba(Q.zloto) .. " gold" else ""
		end
	end
end

function H:powitanieKoniec()
	self.pow.ramka.Visible = false
end

function H:powitanieAktywne(): boolean
	return self.pow.ramka.Visible
end

function H:odslonaKoniec()
	local O = self.odsl
	O.faza = nil
	O.ramka.Visible = false
end

function H:odslonaAktywna(): boolean
	return self.odsl.faza ~= nil
end

-- ---------------------------------------------------------------- animacje (co klatkę)
function H:puls()
	self.pulsT = 0
end

function H:krok(dt: number, t: number)
	-- przyciski: wciśnięcie, błysk końca odnowy
	for _, P in self.anim do
		local w = P.trzymany or P.wcisniety > 0
		if P.wcisniety > 0 then
			P.wcisniety -= dt
		end
		local cel = if w then 0.92 else 1
		P.skala.Scale += (cel - P.skala.Scale) * math.min(1, dt / 0.08 * 1.6)
		local kol = if P.zamkniety then self.S.zamkniety else P.kolor
		P.plytka.BackgroundColor3 = if w then kol:Lerp(Color3.new(0, 0, 0), 0.15) else kol
		P.cien.Visible = not w
		if P.blyskT < 0.15 then
			P.blyskT += dt
			local f = P.blyskT / 0.15
			P.blysk.Thickness = 5 * (1 - f) + 1
			P.blysk.Transparency = f
		elseif P.blysk.Transparency < 1 then
			P.blysk.Transparency = 1
		end
	end
	if self.pulsT < 0.3 then
		self.pulsT += dt
		self.pasekSkala.Scale = 1 + math.sin(math.clamp(self.pulsT / 0.3, 0, 1) * math.pi) * 0.1
	end
	-- odsłona
	local O = self.odsl
	if O.faza then
		O.t += dt
		local tt = O.t
		O.ramka.BackgroundTransparency = 1 - math.clamp(tt / 0.25, 0, 1) * (if O.faza == "kokon" then 0.3 else 0.62)
		O.poswiata.Rotation = math.sin(t * 0.8) * 4
		O.kokonObrys.Thickness = 4 + math.sin(t * 9) * 2.5
		if O.faza == "kokon" then
			O.kokonSkala.Scale = 1 + math.sin(t * 7) * 0.06
		elseif O.faza == "odrodzenie" then
			O.kokonSkala.Scale = math.min(1, 0.3 + tt * 1.4) * (1 + math.sin(t * 9) * 0.07)
			local fN = math.clamp(tt / 0.2, 0, 1)
			O.nazwaSkala.Scale = 0.4 + fN * 0.6
			O.plytka.Position = UDim2.fromOffset(262, 310 + (1 - math.clamp((tt - 0.4) / 0.2, 0, 1)) * 14)
			if tt > O.czas then
				O.kokon.BackgroundColor3 = rgb("FFF3B0")
				O.kokonObrys.Color = self.S.zar_gora
				self:odslonaKoniec()
			end
		else
			local fN = widac(O.nazwa, tt, 0, 0.18)
			O.nazwaSkala.Scale = if fN < 1 then 0.4 + fN * 0.8 else 1 + math.max(0, 0.2 - (tt - 0.18) * 1.5)
			O.gora.Visible = tt > 0.05
			O.strzalki.Visible = tt > 0.25
			O.strzalki.TextTransparency = 0.3 + 0.3 * math.sin(t * 8)
			local fP = widac(O.portret, tt, 0.15, 0.25)
			O.portretSkala.Scale = 0.6 + 0.4 * (1 - (1 - fP) ^ 3)
			O.kokonSkala.Scale = 1 - math.clamp((tt - 0.1) / 0.6, 0, 1) * 0.25
			widac(O.plytka, tt, 0.6)
			O.plytka.Position = UDim2.fromOffset(262, 310 + (1 - math.clamp((tt - 0.6) / 0.2, 0, 1)) * 14)
			local fn = if O.maNast then widac(O.nastKolo, tt, 0.95) else 0
			O.nastNapis.Visible = fn > 0
			widac(O.dalej, tt, 1.25)
			if tt > (O.czas or 3.4) then
				self:odslonaKoniec()
			end
		end
	end
end

-- ---------------------------------------------------------------- odświeżenie góry ekranu
function H:gora(s)
	local D, UI, S = self.D, self.UI, self.S
	local NF = #D.formy
	self:ustawStadium(s.forma, s.wariant)
	self.nazwa.Text = D.formy[s.forma].nazwa
	self.etap.Text = string.format(UI.etap or "STAGE %d / %d", s.forma, NF)
	if s.maks then
		self.pasekW.Size = UDim2.fromScale(1, 1)
		self.pasekNapis.Text = UI.maks
	else
		local q = math.clamp(s.wz / math.max(1, s.pt), 0, 1)
		self.pasekW.Size = UDim2.fromScale(math.max(q, 0.04), 1)
		self.pasekW.Visible = q > 0
		self.pasekNapis.Text = if q >= 1 then UI.pelny else string.format("%s / %s", H.liczba(s.wz), H.liczba(s.pt))
		self.gradWzrostu.Color = if q >= 1 then ColorSequence.new(rgb("FFE58A"), rgb("C27BFF")) else ColorSequence.new(S.zar_gora, S.zar)
	end
	local hp = math.clamp(s.hp, 0, 1)
	self.zycieW.Size = UDim2.fromScale(math.max(hp, 0.03), 1)
	self.zycieW.Visible = hp > 0
	self.zlotoNapis.Text = H.liczba(s.zloto)
	self.skarbNapis.Text = H.liczba(s.skarb)
	self.naSNapis.Text = string.format(UI.na_s, s.naS)
end

return H
