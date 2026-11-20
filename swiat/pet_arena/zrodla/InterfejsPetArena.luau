--[[
	InterfejsPetArena — ekran gracza Pet Arena (ModuleScript; ScreenGui u klienta). Po angielsku (D-045), czytelny na
	telefonie 667 × 375; etap 2: wszystko w rogach (arena w środku kadru zostaje odkryta):
	lewy górny róg — GOLD, +G/s, poziom trenera z paskiem; lewa krawędź — drużyna (3 karty); prawy górny róg — EGGS,
	PETS, TRAIN; góra środek — odliczanie wydarzenia, pasek bossa, komunikat, napisy zdarzeń; prawy dolny róg — ABILITY
	(≥ 44 pt) i życie własnego peta; dół środek — podpowiedź. Znaczki pada (A, X, Y, B, LB/RB, UP, DOWN) gdy gra pad.

	Użycie: local I = Interfejs.nowy(rodzic, D, L, { dotyk, emulacja, naWybor(nr), naUmiejetnosc(), naJajka(), naPety(), naTrening() })
		I:zloto(n, gs)  I:poziom(lv, x, potrzeba)  I:druzyna(lista)  I:umiejetnosc(jest, pasek, nazwa)  I:pet(…)
		I:podpowiedz(tekst?)  I:baner(tekst, kolor, czas?)  I:wydarzenie(tekst?)  I:boss(nazwa?, hp, hpMax)
		I:ogloszenie(tekst, kolor)  I:przyciski(st)  I:pad(bool)  I:krok(dt)  I:stan()  I:prost(o)  I:zniszcz()
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
	return nowy("UIStroke", { Thickness = grubosc, Color = kolor, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, o)
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
	self.znaczki = {}

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
	local function znaczek(rodzic: Instance, tekst: string, poz: UDim2)
		local z = nowy("TextLabel", { Name = "Znaczek", AnchorPoint = Vector2.new(0.5, 0.5), Position = poz, Size = UDim2.fromOffset(26, 22),
			BackgroundColor3 = Color3.fromHex("FFFFFF"), Text = tekst, TextScaled = true, Font = cyfry, TextColor3 = tusz, Visible = false,
			ZIndex = 8 }, rodzic)
		rog(z, 11)
		obrys(z, 2, tusz)
		table.insert(self.znaczki, z)
		return z
	end

	------------------------------------------------------------ lewy górny róg: złoto i poziom trenera
	local gora = warstwa("Gora", Vector2.new(0, 0), UDim2.new(0, 8, 0, 4), Vector2.new(150, 72))
	local tlo = nowy("Frame", { Name = "Tlo", Size = UDim2.new(1, 0, 0, 30), BackgroundColor3 = tusz, BackgroundTransparency = 0.25 }, gora)
	rog(tlo, 10)
	obrys(tlo, 2.5, Color3.fromHex(K.zloto))
	local moneta = nowy("Frame", { Name = "Moneta", AnchorPoint = Vector2.new(0, 0.5), Position = UDim2.new(0, 6, 0.5, 0),
		Size = UDim2.fromOffset(22, 22), BackgroundColor3 = Color3.fromHex(K.zloto) }, tlo)
	rog(moneta, 11)
	obrys(moneta, 2, tusz)
	nowy("TextLabel", { Name = "G", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "G", TextScaled = true,
		Font = czcionka, TextColor3 = tusz }, moneta)
	self.zlotoTekst = nowy("TextLabel", { Name = "Ile", BackgroundTransparency = 1, Position = UDim2.new(0, 34, 0, 2),
		Size = UDim2.new(1, -40, 1, -4), Text = D.ui.zloto .. " 0", TextScaled = true, Font = cyfry, TextColor3 = papier,
		TextXAlignment = Enum.TextXAlignment.Left }, tlo)
	obrysTekstu(self.zlotoTekst, 2, tusz)
	self.gsTekst = nowy("TextLabel", { Name = "NaSekunde", BackgroundTransparency = 1, Position = UDim2.new(0, 4, 0, 31),
		Size = UDim2.new(1, -8, 0, 16), Text = "", TextScaled = true, Font = cyfry, TextColor3 = Color3.fromHex(K.zloto),
		TextXAlignment = Enum.TextXAlignment.Left }, gora)
	obrysTekstu(self.gsTekst, 2, tusz)
	local lv = nowy("Frame", { Name = "Poziom", Position = UDim2.new(0, 0, 0, 50), Size = UDim2.new(1, 0, 0, 20), BackgroundColor3 = tusz,
		BackgroundTransparency = 0.25 }, gora)
	rog(lv, 8)
	self.lvTekst = nowy("TextLabel", { Name = "Lv", BackgroundTransparency = 1, Position = UDim2.fromOffset(6, 1), Size = UDim2.fromOffset(48, 18),
		Text = "LV 1", TextScaled = true, Font = czcionka, TextColor3 = Color3.fromHex("9BE8FF") }, lv)
	obrysTekstu(self.lvTekst, 1.5, tusz)
	local pas = nowy("Frame", { Name = "Pasek", Position = UDim2.fromOffset(58, 6), Size = UDim2.new(1, -66, 0, 8), BackgroundColor3 = Color3.fromHex("2E2838"),
		BorderSizePixel = 0 }, lv)
	rog(pas, 4)
	self.lvPasek = nowy("Frame", { Name = "W", Size = UDim2.fromScale(0, 1), BackgroundColor3 = Color3.fromHex("9BE8FF"), BorderSizePixel = 0 }, pas)
	rog(self.lvPasek, 4)
	self.gora = gora

	------------------------------------------------------------ góra środek: wydarzenie, boss, komunikat, napisy zdarzeń
	local srodek = warstwa("Srodek", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 2), Vector2.new(260, 40))
	self.wydTekst = nowy("TextLabel", { Name = "Wydarzenie", BackgroundTransparency = 1, Size = UDim2.new(1, 0, 0, 18), Text = "",
		TextScaled = true, Font = czcionka, TextColor3 = Color3.fromHex("FF9A5A"), Visible = false }, srodek)
	obrysTekstu(self.wydTekst, 2, tusz)
	local bb = nowy("Frame", { Name = "Boss", Position = UDim2.fromOffset(20, 20), Size = UDim2.new(1, -40, 0, 14), BackgroundColor3 = tusz,
		Visible = false }, srodek)
	rog(bb, 6)
	obrys(bb, 2, Color3.fromHex("FF4D4D"))
	self.bossW = nowy("Frame", { Name = "W", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.fromHex("FF4D4D"), BorderSizePixel = 0 }, bb)
	rog(self.bossW, 6)
	self.bossNazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "", TextScaled = true,
		Font = czcionka, TextColor3 = papier, ZIndex = 3 }, bb)
	obrysTekstu(self.bossNazwa, 1.5, tusz)
	self.bossRamka = bb
	self.srodek = srodek
	local ogl = warstwa("Ogloszenie", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 38), Vector2.new(330, 18))
	self.oglTekst = nowy("TextLabel", { Name = "Tekst", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "", TextScaled = true,
		Font = cyfry, TextColor3 = papier, Visible = false }, ogl)
	obrysTekstu(self.oglTekst, 2, tusz)
	self.oglDo = 0
	self.oglRamka = ogl
	local baner = warstwa("Baner", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 56), Vector2.new(300, 40))
	self.banerTekst = nowy("TextLabel", { Name = "Tekst", BackgroundTransparency = 1, Size = UDim2.fromScale(1, 1), Text = "",
		TextScaled = true, Font = czcionka, TextColor3 = papier, Visible = false }, baner)
	obrysTekstu(self.banerTekst, 3, tusz)
	self.banerSkala = nowy("UIScale", { Scale = 1 }, self.banerTekst)
	self.banerDo, self.banerT = 0, 0
	self.banerRamka = baner

	------------------------------------------------------------ prawy górny róg: EGGS, PETS, TRAIN
	local pg = warstwa("Przyciski", Vector2.new(1, 0), UDim2.new(1, -8, 0, 4), Vector2.new(208, 50))
	local function przycisk(nazwa: string, tekst: string, x: number, kolor: string, akcja, zn: string)
		local b = nowy("TextButton", { Name = nazwa, Position = UDim2.fromOffset(x, 0), Size = UDim2.fromOffset(66, 46), BackgroundColor3 = Color3.fromHex(kolor),
			Text = "", AutoButtonColor = true }, pg)
		rog(b, 10)
		obrys(b, 2.5, tusz)
		local l = nowy("TextLabel", { Name = "Napis", BackgroundTransparency = 1, Position = UDim2.fromScale(0.08, 0.2), Size = UDim2.fromScale(0.84, 0.6),
			Text = tekst, TextScaled = true, Font = czcionka, TextColor3 = papier }, b)
		obrysTekstu(l, 1.5, tusz)
		b.Activated:Connect(akcja)
		znaczek(b, zn, UDim2.new(0.5, 0, 1, 2))
		return b
	end
	self.bJajka = przycisk("Jajka", D.ui.jajka_przycisk, 0, "3DB36B", function()
		if opcje.naJajka then
			opcje.naJajka()
		end
	end, D.ui.pad.jajka)
	self.bPety = przycisk("Pety", D.ui.pety_przycisk, 71, "4FB3FF", function()
		if opcje.naPety then
			opcje.naPety()
		end
	end, D.ui.pad.pety)
	self.bTrening = przycisk("Trening", D.ui.trening, 142, "8A7AA8", function()
		if opcje.naTrening then
			opcje.naTrening()
		end
	end, D.ui.pad.trening)
	self.jajkaSkala = nowy("UIScale", { Scale = 1 }, self.bJajka)
	self.przyciskiGorne = pg

	------------------------------------------------------------ drużyna (lewa krawędź)
	local druzyna = warstwa("Druzyna", Vector2.new(0, 0.5), UDim2.new(0, 8, 0.47, 0), Vector2.new(124, 3 * 52))
	nowy("UIListLayout", { Padding = UDim.new(0, 4), SortOrder = Enum.SortOrder.LayoutOrder }, druzyna)
	znaczek(druzyna, D.ui.pad.druzyna, UDim2.new(0.5, 0, 0, -12)).Size = UDim2.fromOffset(52, 20)
	self.karty = {}
	for i = 1, D.gracz.druzyna_maks do
		local b = nowy("TextButton", { Name = "Pet" .. i, LayoutOrder = i, Size = UDim2.new(1, 0, 0, 48), BackgroundColor3 = tusz,
			BackgroundTransparency = 0.2, Text = "", AutoButtonColor = true, Visible = false }, druzyna)
		rog(b, 10)
		local ramka = obrys(b, 2, papier)
		local pasR = nowy("Frame", { Name = "Rzadkosc", Size = UDim2.new(0, 6, 1, -10), Position = UDim2.fromOffset(5, 5),
			BackgroundColor3 = papier, BorderSizePixel = 0 }, b)
		rog(pasR, 3)
		local nazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, Position = UDim2.fromOffset(15, 3),
			Size = UDim2.new(1, -19, 0, 20), Text = "", TextScaled = true, Font = czcionka, TextColor3 = papier,
			TextXAlignment = Enum.TextXAlignment.Left }, b)
		obrysTekstu(nazwa, 1.5, tusz)
		local stan = nowy("TextLabel", { Name = "Stan", BackgroundTransparency = 1, Position = UDim2.fromOffset(15, 25),
			Size = UDim2.new(1, -19, 0, 18), Text = "", TextScaled = true, Font = cyfry, TextColor3 = papier,
			TextXAlignment = Enum.TextXAlignment.Left }, b)
		obrysTekstu(stan, 1.5, tusz)
		b.Activated:Connect(function()
			if opcje.naWybor then
				opcje.naWybor(i)
			end
		end)
		self.karty[i] = { przycisk = b, ramka = ramka, pas = pasR, nazwa = nazwa, stan = stan }
	end
	self.druzynaRamka = druzyna

	------------------------------------------------------------ prawy dolny róg: ABILITY i własny pet nad nim
	local prawy = warstwa("Prawy", Vector2.new(1, 1), UDim2.new(1, -10, 1, -10), Vector2.new(124, 158))
	local przycisk = nowy("TextButton", { Name = "Umiejetnosc", AnchorPoint = Vector2.new(1, 1), Position = UDim2.fromScale(1, 1),
		Size = UDim2.fromOffset(104, 104), BackgroundColor3 = Color3.new(1, 1, 1), Text = "", AutoButtonColor = false }, prawy)
	rog(przycisk, 52)
	self.przyciskObrys = obrys(przycisk, 4, tusz)
	self.przyciskGradient = nowy("UIGradient", { Rotation = -90, Color = ColorSequence.new(Color3.fromHex("5A5566")) }, przycisk)
	local napis = nowy("TextLabel", { Name = "Napis", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.42), Size = UDim2.fromScale(0.86, 0.3), Text = D.ui.umiejetnosc, TextScaled = true,
		Font = czcionka, TextColor3 = papier, ZIndex = 3 }, przycisk)
	obrysTekstu(napis, 2.5, tusz)
	self.przyciskNazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.5, 0.68), Size = UDim2.fromScale(0.8, 0.17), Text = "", TextScaled = true, Font = cyfry,
		TextColor3 = papier, ZIndex = 3 }, przycisk)
	obrysTekstu(self.przyciskNazwa, 1.5, tusz)
	self.przyciskSkala = nowy("UIScale", { Scale = 1 }, przycisk)
	znaczek(przycisk, D.ui.pad.umiejetnosc, UDim2.new(0, 10, 0, 10))
	przycisk.Activated:Connect(function()
		if opcje.naUmiejetnosc then
			opcje.naUmiejetnosc()
		end
	end)
	self.przycisk = przycisk
	local pet = nowy("Frame", { Name = "MojPet", AnchorPoint = Vector2.new(1, 1), Position = UDim2.new(1, 0, 1, -110),
		Size = UDim2.fromOffset(124, 44), BackgroundColor3 = tusz, BackgroundTransparency = 0.25, Visible = false }, prawy)
	rog(pet, 10)
	self.petObrys = obrys(pet, 2.5, Color3.fromHex(K.ty))
	self.petNazwa = nowy("TextLabel", { Name = "Nazwa", BackgroundTransparency = 1, Position = UDim2.fromOffset(6, 2),
		Size = UDim2.new(1, -12, 0, 17), Text = "", TextScaled = true, Font = czcionka, TextColor3 = papier,
		TextXAlignment = Enum.TextXAlignment.Left }, pet)
	obrysTekstu(self.petNazwa, 1.5, tusz)
	local function pasek(nazwa: string, y: number, kolor: Color3): Frame
		local r = nowy("Frame", { Name = nazwa, Position = UDim2.fromOffset(6, y), Size = UDim2.new(1, -12, 0, 8), BackgroundColor3 = Color3.fromHex("2E2838"),
			BorderSizePixel = 0 }, pet)
		rog(r, 4)
		local w = nowy("Frame", { Name = "W", Size = UDim2.fromScale(1, 1), BackgroundColor3 = kolor, BorderSizePixel = 0 }, r)
		rog(w, 4)
		return w
	end
	self.petZycie = pasek("Zycie", 21, Color3.fromHex(K.zycie))
	self.petPasek = pasek("Pasek", 32, Color3.fromHex(K.pasek))
	self.petRamka = pet

	------------------------------------------------------------ podpowiedź (dół, środek)
	local pod = warstwa("Podpowiedz", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -8), Vector2.new(296, 38))
	local podTlo = nowy("Frame", { Name = "Tlo", Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.2 }, pod)
	rog(podTlo, 12)
	obrys(podTlo, 2.5, Color3.fromHex(K.ty))
	self.podTekst = nowy("TextLabel", { Name = "Tekst", BackgroundTransparency = 1, Position = UDim2.fromOffset(10, 4),
		Size = UDim2.new(1, -20, 1, -8), Text = "", TextScaled = true, TextWrapped = false, Font = czcionka, TextColor3 = Color3.fromHex(K.ty) }, podTlo)
	obrysTekstu(self.podTekst, 2, tusz)
	znaczek(podTlo, D.ui.pad.rzut, UDim2.new(0, 0, 0.5, 0))
	pod.Visible = false
	self.podpowiedzRamka = pod
	self.t = 0
	return self
end

function Interfejs:zloto(n: number, gs: number)
	self.zlotoTekst.Text = self.D.ui.zloto .. " " .. self.L.format(n)
	self.gsTekst.Text = if gs > 0 then string.format(self.D.ui.na_s, self.L.naSekunde(gs)) else ""
end

function Interfejs:poziom(lv: number, x: number, potrzeba: number)
	self.lvTekst.Text = string.format(self.D.ui.poziom, lv)
	self.lvPasek.Size = UDim2.fromScale(math.clamp(x / math.max(1, potrzeba), 0, 1), 1)
end

-- lista: { { nazwa, kolor, stan = "gotowy" | "arena" | "odpoczynek", zostalo, gwiazdki, wybrany } }
function Interfejs:druzyna(lista)
	local D = self.D
	for i, k in self.karty do
		local w = lista[i]
		k.przycisk.Visible = w ~= nil
		if w then
			k.nazwa.Text = w.nazwa .. (if (w.gwiazdki or 1) > 1 then " " .. string.rep("★", w.gwiazdki) else "")
			k.pas.BackgroundColor3 = Color3.fromHex(w.kolor)
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
			k.ramka.Color = if w.wybrany then Color3.fromHex(D.ui.kolory.ty) else self.papier
			k.ramka.Thickness = if w.wybrany then 3.5 else 2
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
	self.banerTekst.Rotation = math.random(-3, 3)
	self.banerDo = czas or 1.4
	self.banerT = 0
end

function Interfejs:wydarzenie(tekst: string?)
	self.wydTekst.Visible = tekst ~= nil
	if tekst then
		self.wydTekst.Text = tekst
	end
end

function Interfejs:boss(nazwa: string?, hp: number?, hpMax: number?)
	self.bossRamka.Visible = nazwa ~= nil
	if nazwa then
		self.bossNazwa.Text = nazwa
		self.bossW.Size = UDim2.fromScale(math.clamp((hp or 0) / math.max(1, hpMax or 1), 0, 1), 1)
	end
end

function Interfejs:ogloszenie(tekst: string, kolor: string?)
	self.oglTekst.Text = tekst
	self.oglTekst.TextColor3 = Color3.fromHex(kolor or self.D.ui.kolory.papier)
	self.oglTekst.Visible = true
	self.oglDo = 4.5
end

-- st: { trening = bool, jajkoPulsuje = bool }
function Interfejs:przyciski(st)
	self.bTrening.BackgroundColor3 = Color3.fromHex(if st.trening then "3DB36B" else "8A7AA8")
	self.bTrening:FindFirstChild("Napis").Text = if st.trening then self.D.ui.trening_wl else self.D.ui.trening
	self.jajkoPulsuje = st.jajkoPulsuje
end

function Interfejs:pad(wl: boolean)
	for _, z in self.znaczki do
		z.Visible = wl
	end
	self.padWl = wl
end

function Interfejs:krok(dt: number)
	self.t += dt
	if self.banerTekst.Visible then
		self.banerT += dt
		local f = self.banerT
		self.banerSkala.Scale = if f < 0.1 then 0.4 + f / 0.1 * 0.8 elseif f < 0.2 then 1.2 - (f - 0.1) / 0.1 * 0.2 else 1
		self.banerTekst.TextTransparency = math.clamp((f - self.banerDo + 0.3) / 0.3, 0, 1)
		if f >= self.banerDo then
			self.banerTekst.Visible = false
		end
	end
	if self.oglTekst.Visible then
		self.oglDo -= dt
		if self.oglDo <= 0 then
			self.oglTekst.Visible = false
		end
	end
	self.przyciskSkala.Scale = if self.gotowa then 1 + math.sin(self.t * 7) * 0.05 else 1
	self.jajkaSkala.Scale = if self.jajkoPulsuje then 1 + math.abs(math.sin(self.t * 5)) * 0.12 else 1
end

local function prost(o: GuiObject): { number }
	return { o.AbsolutePosition.X, o.AbsolutePosition.Y, o.AbsoluteSize.X, o.AbsoluteSize.Y }
end

-- prostokąt w punktach (w emulacji: względem ramki telefonu, w punktach telefonu)
function Interfejs:prost(o: GuiObject): { number }
	local r = prost(o)
	local s = self.skalaEmulacji
	if not s or o == self.okno then
		return r
	end
	local ok = prost(self.okno :: GuiObject)
	return { (r[1] - ok[1]) / s, (r[2] - ok[2]) / s, r[3] / s, r[4] / s }
end

function Interfejs:stan()
	local karty, teksty = {}, {}
	for _, k in self.karty do
		if k.przycisk.Visible then
			table.insert(karty, self:prost(k.przycisk))
			table.insert(teksty, k.stan.Text)
		end
	end
	local okno = if self.skalaEmulacji then { 0, 0, self.opcje.emulacja.X, self.opcje.emulacja.Y }
		else { 0, 0, self.gui.AbsoluteSize.X, self.gui.AbsoluteSize.Y }
	return {
		okno = okno, gora = self:prost(self.gora), karty = karty, kartyTekst = teksty, przycisk = self:prost(self.przycisk),
		pet = self:prost(self.petRamka), petWidoczny = self.petRamka.Visible,
		podpowiedz = if self.podpowiedzRamka.Visible then self:prost(self.podpowiedzRamka) else nil,
		podpowiedzTekst = if self.podpowiedzRamka.Visible then self.podTekst.Text else nil,
		baner = if self.banerTekst.Visible then self.banerTekst.Text else nil,
		przyciskiGorne = { self:prost(self.bJajka), self:prost(self.bPety), self:prost(self.bTrening) },
		srodek = self:prost(self.srodek), wydarzenie = if self.wydTekst.Visible then self.wydTekst.Text else nil,
		boss = if self.bossRamka.Visible then self.bossNazwa.Text else nil, ogloszenie = if self.oglTekst.Visible then self.oglTekst.Text else nil,
		zloto = self.zlotoTekst.Text, gs = self.gsTekst.Text, poziom = self.lvTekst.Text, przyciskNazwa = self.przyciskNazwa.Text,
		gotowa = self.gotowa == true, dotyk = self.opcje.dotyk == true, skala = self.skala(), pad = self.padWl == true,
	}
end

function Interfejs:zniszcz()
	self.gui:Destroy()
end

return Interfejs
