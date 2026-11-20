--[[
	InterfejsPetArena — ekran gracza Pet Arena (ModuleScript; ScreenGui u klienta). Po angielsku (D-045), czytelny na
	telefonie 667 × 375: GOLD i +G/s u góry, drużyna (3 przyciski) po lewej, przycisk ABILITY w prawym dolnym rogu
	(≥ 44 pt) z paskiem, nad nim życie i pasek umiejętności własnego peta, podpowiedź u dołu, napisy zdarzeń pod złotem.

	Użycie: local I = Interfejs.nowy(rodzic, D, L, { dotyk, emulacja, naWybor(nr), naUmiejetnosc() })
		I:zloto(n, gs)   I:druzyna(lista)   I:umiejetnosc(jest, pasek, nazwa)   I:pet(jest, nazwa, kolor, hp, hpMax, pasek)
		I:podpowiedz(tekst?)   I:baner(tekst, kolor, czas?)   I:krok(dt)   I:stan()   I:zniszcz()
]]
if not game:GetService("RunService"):IsStudio() then
	return {}
end

local Interfejs = {}
Interfejs.__index = Interfejs

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

local function obrys(o: Instance, grubosc: number, kolor: Color3)
	nowy("UIStroke", { Thickness = grubosc, Color = kolor, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, o)
end

local function obrysTekstu(o: Instance, grubosc: number, kolor: Color3)
	nowy("UIStroke", { Thickness = grubosc, Color = kolor, ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual }, o)
end

local function rog(o: Instance, r: number)
	nowy("UICorner", { CornerRadius = UDim.new(0, r) }, o)
end

function Interfejs.nowy(rodzic: Instance, D, L, opcje)
	local self = setmetatable({}, Interfejs)
	self.D, self.L, self.opcje = D, L, opcje
	local K = D.ui.kolory
	local tusz, papier = Color3.fromHex(K.tusz), Color3.fromHex(K.papier)
	local czcionka = Enum.Font[D.ui.czcionka] or Enum.Font.LuckiestGuy
	local cyfry = Enum.Font[D.ui.czcionka_cyfr] or Enum.Font.FredokaOne
	self.tusz, self.papier, self.czcionka, self.cyfry = tusz, papier, czcionka, cyfry

	local gui = nowy("ScreenGui", { Name = "PetArenaEkran", ResetOnSpawn = false, IgnoreGuiInset = false,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling, DisplayOrder = 5 }, rodzic)
	self.gui = gui
	local ekran: Instance = gui
	local emulacja = opcje.emulacja
	if emulacja then
		-- próby: ekran telefonu (punkty) powiększony do okna — obraz 3D w oknie ma te same proporcje co telefon
		ekran = nowy("Frame", { Name = "EmulacjaTelefonu", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromOffset(emulacja.X, emulacja.Y), BackgroundTransparency = 1, ClipsDescendants = true }, gui)
		local v = workspace.CurrentCamera.ViewportSize
		self.skalaEmulacji = math.min(v.X / emulacja.X, (v.Y - 36) / emulacja.Y)
		nowy("UIScale", { Scale = self.skalaEmulacji }, ekran)
	end
	self.okno = ekran
	local kamera = workspace.CurrentCamera
	local function skala(): number
		local v = if emulacja then emulacja else kamera.ViewportSize
		return math.clamp(math.min(v.X / 667, v.Y / 375), 1, 1.6)
	end
	self.skala = skala

	local function warstwa(nazwa: string, kotwica: Vector2, poz: UDim2, rozmiar: Vector2): Frame
		local f = nowy("Frame", { Name = nazwa, AnchorPoint = kotwica, Position = poz, Size = UDim2.fromOffset(rozmiar.X, rozmiar.Y),
			BackgroundTransparency = 1 }, ekran)
		nowy("UIScale", { Scale = skala() }, f)
		return f
	end

	------------------------------------------------------------ góra: złoto
	local gora = warstwa("Gora", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 3), Vector2.new(200, 48))
	local tlo = nowy("Frame", { Name = "Tlo", Size = UDim2.new(1, 0, 0, 30), BackgroundColor3 = tusz, BackgroundTransparency = 0.25 }, gora)
	rog(tlo, 12)
	obrys(tlo, 2.5, Color3.fromHex(K.zloto))
	local moneta = nowy("Frame", { Name = "Moneta", AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 8, 0.5, 0),
		Size = UDim2.fromOffset(22, 22), BackgroundColor3 = Color3.fromHex(K.zloto) }, tlo)
	rog(moneta, 11)
	obrys(moneta, 2, tusz)
	nowy("TextLabel", { Name = "G", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "G", TextScaled = true,
		Font = czcionka, TextColor3 = tusz }, moneta)
	self.zlotoTekst = nowy("TextLabel", { Name = "Ile", BackgroundTransparency = 1, Position = UDim2.new(0, 36, 0, 2),
		Size = UDim2.new(1, -48, 1, -4), Text = D.ui.zloto .. " 0", TextScaled = true, Font = cyfry, TextColor3 = papier,
		TextXAlignment = Enum.TextXAlignment.Left }, tlo)
	obrysTekstu(self.zlotoTekst, 2, tusz)
	self.gsTekst = nowy("TextLabel", { Name = "NaSekunde", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0),
		Position = UDim2.new(0.5, 0, 0, 30), Size = UDim2.new(0.8, 0, 0, 17), Text = "", TextScaled = true, Font = cyfry,
		TextColor3 = Color3.fromHex(K.zloto) }, gora)
	obrysTekstu(self.gsTekst, 2, tusz)
	self.gora = gora

	------------------------------------------------------------ napis zdarzeń (pod złotem)
	local baner = warstwa("Baner", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 52), Vector2.new(340, 46))
	self.banerTekst = nowy("TextLabel", { Name = "Tekst", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "",
		TextScaled = true, Font = czcionka, TextColor3 = papier, Visible = false }, baner)
	obrysTekstu(self.banerTekst, 3.5, tusz)
	self.banerSkala = nowy("UIScale", { Scale = 1 }, self.banerTekst)
	self.banerDo = 0
	self.banerT = 0
	self.banerRamka = baner

	------------------------------------------------------------ drużyna (lewo)
	local druzyna = warstwa("Druzyna", Vector2.new(0, 0.5), UDim2.new(0, 8, 0.52, 0), Vector2.new(150, 3 * 62))
	nowy("UIListLayout", { Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder }, druzyna)
	self.karty = {}
	for i = 1, D.gracz.druzyna_maks do
		local b = nowy("TextButton", { Name = "Pet" .. i, LayoutOrder = i, Size = UDim2.new(1, 0, 0, 56), BackgroundColor3 = tusz,
			BackgroundTransparency = 0.2, Text = "", AutoButtonColor = true, Visible = false }, druzyna)
		rog(b, 10)
		local ramka = nowy("UIStroke", { Thickness = 2, Color = papier, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, b)
		local pas = nowy("Frame", { Name = "Rzadkosc", Size = UDim2.new(0, 8, 1, -12), Position = UDim2.fromOffset(6, 6),
			BackgroundColor3 = papier, BorderSizePixel = 0 }, b)
		rog(pas, 4)
		local nr = nowy("TextLabel", { Name = "Nr", BackgroundTransparency = 1, Position = UDim2.fromOffset(18, 4),
			Size = UDim2.fromOffset(16, 22), Text = tostring(i), TextScaled = true, Font = cyfry, TextColor3 = Color3.fromHex(K.zloto) }, b)
		obrysTekstu(nr, 1.5, tusz)
		local nazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, Position = UDim2.fromOffset(36, 4),
			Size = UDim2.new(1, -40, 0, 24), Text = "", TextScaled = true, Font = czcionka, TextColor3 = papier,
			TextXAlignment = Enum.TextXAlignment.Left }, b)
		obrysTekstu(nazwa, 1.5, tusz)
		local stan = nowy("TextLabel", { Name = "Stan", BackgroundTransparency = 1, Position = UDim2.fromOffset(20, 30),
			Size = UDim2.new(1, -26, 0, 20), Text = "", TextScaled = true, Font = cyfry, TextColor3 = papier,
			TextXAlignment = Enum.TextXAlignment.Left }, b)
		obrysTekstu(stan, 1.5, tusz)
		b.Activated:Connect(function()
			if opcje.naWybor then
				opcje.naWybor(i)
			end
		end)
		self.karty[i] = { przycisk = b, ramka = ramka, pas = pas, nazwa = nazwa, stan = stan }
	end
	self.druzynaRamka = druzyna

	------------------------------------------------------------ przycisk ABILITY (prawy dół) i własny pet nad nim
	local prawy = warstwa("Prawy", Vector2.new(1, 1), UDim2.new(1, -10, 1, -10), Vector2.new(170, 160))
	local przycisk = nowy("TextButton", { Name = "Umiejetnosc", AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(1, 1),
		Size = UDim2.fromOffset(104, 104), BackgroundColor3 = Color3.fromHex("5A5566"), Text = "", AutoButtonColor = false,
		ClipsDescendants = false }, prawy)
	rog(przycisk, 52)
	self.przyciskObrys = nowy("UIStroke", { Thickness = 4, Color = tusz, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, przycisk)
	-- pasek w przycisku: gradient od dołu (zaokrąglone rogi zostają — ClipsDescendants ich nie respektuje)
	przycisk.BackgroundColor3 = Color3.new(1, 1, 1)
	self.przyciskGradient = nowy("UIGradient", { Rotation = -90 }, przycisk)
	local napis = nowy("TextLabel", { Name = "Napis", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.42), Size = UDim2.fromScale(0.86, 0.3), Text = D.ui.umiejetnosc, TextScaled = true,
		Font = czcionka, TextColor3 = papier, ZIndex = 3 }, przycisk)
	obrysTekstu(napis, 2.5, tusz)
	self.przyciskNazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.68), Size = UDim2.fromScale(0.8, 0.17), Text = "", TextScaled = true, Font = cyfry,
		TextColor3 = papier, ZIndex = 3 }, przycisk)
	obrysTekstu(self.przyciskNazwa, 1.5, tusz)
	self.przyciskSkala = nowy("UIScale", { Scale = 1 }, przycisk)
	przycisk.Activated:Connect(function()
		if opcje.naUmiejetnosc then
			opcje.naUmiejetnosc()
		end
	end)
	self.przycisk = przycisk

	local pet = nowy("Frame", { Name = "MojPet", AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, 0, 1, -110),
		Size = UDim2.fromOffset(170, 46), BackgroundColor3 = tusz, BackgroundTransparency = 0.25, Visible = false }, prawy)
	rog(pet, 10)
	self.petObrys = nowy("UIStroke", { Thickness = 2.5, Color = Color3.fromHex(K.ty), ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, pet)
	self.petNazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, Position = UDim2.fromOffset(8, 2),
		Size = UDim2.new(1, -16, 0, 18), Text = "", TextScaled = true, Font = czcionka, TextColor3 = papier,
		TextXAlignment = Enum.TextXAlignment.Left }, pet)
	obrysTekstu(self.petNazwa, 1.5, tusz)
	local function pasek(nazwa: string, y: number, kolor: Color3): Frame
		local r = nowy("Frame", { Name = nazwa, Position = UDim2.fromOffset(8, y), Size = UDim2.new(1, -16, 0, 9), BackgroundColor3 = Color3.fromHex("2E2838"),
			BorderSizePixel = 0 }, pet)
		rog(r, 4)
		local w = nowy("Frame", { Name = "W", Size = UDim2.fromScale(1, 1), BackgroundColor3 = kolor, BorderSizePixel = 0 }, r)
		rog(w, 4)
		return w
	end
	self.petZycie = pasek("Zycie", 22, Color3.fromHex(K.zycie))
	self.petPasek = pasek("Pasek", 34, Color3.fromHex(K.pasek))
	self.petRamka = pet
	self.prawy = prawy

	------------------------------------------------------------ podpowiedź (dół, środek)
	local pod = warstwa("Podpowiedz", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -8), Vector2.new(296, 40))
	local podTlo = nowy("Frame", { Name = "Tlo", Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.2 }, pod)
	rog(podTlo, 12)
	obrys(podTlo, 2.5, Color3.fromHex(K.ty))
	self.podTekst = nowy("TextLabel", { Name = "Tekst", BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 4),
		Size = UDim2.new(1, -20, 1, -8), Text = "", TextScaled = true, TextWrapped = false, Font = czcionka, TextColor3 = Color3.fromHex(K.ty) }, podTlo)
	obrysTekstu(self.podTekst, 2, tusz)
	pod.Visible = false
	self.podpowiedzRamka = pod
	self.t = 0
	return self
end

function Interfejs:zloto(n: number, gs: number)
	self.zlotoTekst.Text = self.D.ui.zloto .. " " .. self.L.format(n)
	self.gsTekst.Text = if gs > 0 then string.format(self.D.ui.na_s, self.L.naSekunde(gs)) else ""
end

-- lista: { { nazwa, kolor, stan = "gotowy" | "arena" | "odpoczynek", zostalo, probny, wybrany } }
function Interfejs:druzyna(lista)
	local D = self.D
	for i, k in self.karty do
		local w = lista[i]
		k.przycisk.Visible = w ~= nil
		if w then
			k.nazwa.Text = w.nazwa .. (if w.probny then " (" .. D.ui.probny .. ")" else "")
			k.pas.BackgroundColor3 = Color3.fromHex(w.kolor)
			local zolty = Color3.fromHex(D.ui.kolory.ty)
			if w.stan == "odpoczynek" then
				k.stan.Text = string.format("%s %ds", D.ui.odpoczywa, w.zostalo)
				k.stan.TextColor3 = Color3.fromHex("FF9A9A")
				k.przycisk.BackgroundTransparency = 0.45
			elseif w.stan == "arena" then
				k.stan.Text = D.ui.na_arenie
				k.stan.TextColor3 = Color3.fromHex(D.ui.kolory.pasek)
				k.przycisk.BackgroundTransparency = 0.2
			else
				k.stan.Text = D.ui.gotowy
				k.stan.TextColor3 = Color3.fromHex(D.ui.kolory.zycie)
				k.przycisk.BackgroundTransparency = 0.2
			end
			k.ramka.Color = if w.wybrany then zolty else self.papier
			k.ramka.Thickness = if w.wybrany then 4 else 2
		end
	end
end

function Interfejs:umiejetnosc(jest: boolean, pasek: number, nazwa: string?)
	local p = if jest then math.clamp(pasek, 0, 1) else 0
	self.przyciskNazwa.Text = if jest and nazwa then nazwa else ""
	self.gotowa = jest and pasek >= 1
	local szary, czerwony = Color3.fromHex("5A5566"), Color3.fromHex(self.D.ui.kolory.przycisk)
	if self.gotowa then
		self.przyciskGradient.Color = ColorSequence.new(Color3.fromHex("FFB13D"))
	elseif p <= 0.01 then
		self.przyciskGradient.Color = ColorSequence.new(szary)
	else
		local q = math.min(p, 0.985)
		self.przyciskGradient.Color = ColorSequence.new({ ColorSequenceKeypoint.new(0, czerwony), ColorSequenceKeypoint.new(q, czerwony),
			ColorSequenceKeypoint.new(q + 0.01, szary), ColorSequenceKeypoint.new(1, szary) })
	end
	self.przyciskObrys.Color = if self.gotowa then Color3.fromHex(self.D.ui.kolory.ty) else self.tusz
end

function Interfejs:pet(jest: boolean, nazwa: string?, kolor: string?, hp: number?, hpMax: number?, pasek: number?)
	self.petRamka.Visible = jest
	if not jest then
		return
	end
	self.petNazwa.Text = nazwa or ""
	local f = math.clamp((hp or 0) / math.max(hpMax or 1, 1), 0, 1)
	self.petZycie.Size = UDim2.fromScale(f, 1)
	self.petZycie.BackgroundColor3 = if f < 0.35 then Color3.fromHex(self.D.ui.kolory.zycie_nisko) else Color3.fromHex(self.D.ui.kolory.zycie)
	self.petPasek.Size = UDim2.fromScale(math.clamp(pasek or 0, 0, 1), 1)
	if kolor then
		self.petObrys.Color = Color3.fromHex(kolor)
	end
end

function Interfejs:podpowiedz(tekst: string?)
	self.podpowiedzRamka.Visible = tekst ~= nil
	if tekst then
		self.podTekst.Text = tekst
	end
end

function Interfejs:baner(tekst: string, kolor: Color3?, czas: number?)
	self.banerTekst.Text = tekst
	self.banerTekst.TextColor3 = kolor or self.papier
	self.banerTekst.Visible = true
	self.banerTekst.Rotation = math.random(-4, 4)
	self.banerDo = czas or 1.4
	self.banerT = 0
end

function Interfejs:krok(dt: number)
	self.t += dt
	if self.banerTekst.Visible then
		self.banerT += dt
		local f = self.banerT
		self.banerSkala.Scale = if f < 0.1 then 0.4 + f / 0.1 * 0.8 elseif f < 0.2 then 1.2 - (f - 0.1) / 0.1 * 0.2 else 1
		local zanik = math.clamp((f - self.banerDo + 0.3) / 0.3, 0, 1)
		self.banerTekst.TextTransparency = zanik
		if f >= self.banerDo then
			self.banerTekst.Visible = false
		end
	end
	self.przyciskSkala.Scale = if self.gotowa then 1 + math.sin(self.t * 7) * 0.05 else 1
end

local function prost(o: GuiObject): { number }
	return { o.AbsolutePosition.X, o.AbsolutePosition.Y, o.AbsoluteSize.X, o.AbsoluteSize.Y }
end

-- w emulacji: prostokąt w punktach telefonu (względem ramki telefonu)
function Interfejs:prost(o: GuiObject): { number }
	local r = prost(o)
	local s = self.skalaEmulacji
	if not s or o == self.okno then
		return r
	end
	local ok = prost(self.okno :: GuiObject)
	return { (r[1] - ok[1]) / s, (r[2] - ok[2]) / s, r[3] / s, r[4] / s }
end

-- prostokąty w punktach ekranu (próby: w ekranie, ≥ 44 pt, bez nakładania)
function Interfejs:stan()
	local karty, teksty = {}, {}
	for _, k in self.karty do
		if k.przycisk.Visible then
			table.insert(karty, self:prost(k.przycisk))
			table.insert(teksty, k.stan.Text)
		end
	end
	local okno = if self.skalaEmulacji then { 0, 0, self.opcje.emulacja.X, self.opcje.emulacja.Y } elseif self.okno:IsA("GuiObject") then prost(self.okno :: GuiObject)
		else { 0, 0, self.gui.AbsoluteSize.X, self.gui.AbsoluteSize.Y }
	return {
		okno = okno, gora = self:prost(self.gora), karty = karty, kartyTekst = teksty, przycisk = self:prost(self.przycisk), pet = self:prost(self.petRamka),
		petWidoczny = self.petRamka.Visible, podpowiedz = if self.podpowiedzRamka.Visible then self:prost(self.podpowiedzRamka) else nil,
		podpowiedzTekst = if self.podpowiedzRamka.Visible then self.podTekst.Text else nil,
		baner = if self.banerTekst.Visible then self.banerTekst.Text else nil, banerPoz = self:prost(self.banerRamka),
		zloto = self.zlotoTekst.Text, gs = self.gsTekst.Text, przyciskNazwa = self.przyciskNazwa.Text, gotowa = self.gotowa == true,
		dotyk = self.opcje.dotyk == true, skala = self.skala(),
	}
end

function Interfejs:zniszcz()
	self.gui:Destroy()
end

return Interfejs
