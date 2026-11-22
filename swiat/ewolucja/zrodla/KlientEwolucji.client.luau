--[[
	KlientEwolucji — klient Monster Evolution (Script, RunContext Client, w Workspace/EwolucjaGra). Strażnik „tylko Studio”
	na początku (zbuduj.py --publikacja go usuwa) i wyłącznik kontenera.
	Własny potwór przewidywany od razu (ruch, DASH, szarża; serwer przyjmuje pozycję albo poprawia); BITE gra od razu
	(wynik od serwera). Potwory bez szkieletów — ruch proceduralny (krok-podskok, zgniecenie i rozciągnięcie przesunięciem
	części, pochylenie w biegu i w zakrętach, kiwanie, wypad przy gryzieniu), części przesuwane workspace:BulkMoveTo.
	Ekran (telefon najpierw, wzór 667 × 375 pt): pasek wzrostu, złoto + DEN, drabina z boku, BITE / DASH / umiejętność,
	EVOLVE przy pełnym pasku, odsłona nowej formy, panel legowiska z ulepszeniami.
	Próby: wejście jak z palca przez atrybuty lokalnego gracza (EW_TestSter, EW_TestPrzycisk, EW_TestAuto, EW_TestUklad),
	stan dla prób w atrybutach EW_K_*.
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local GuiService = game:GetService("GuiService")
local HttpService = game:GetService("HttpService")

local gracz = Players.LocalPlayer
local playerGui = gracz:WaitForChild("PlayerGui")
local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DaneEwolucji"))
if kontener:GetAttribute(D.wylacznik) == false then
	return
end
local L = require(Moduly:WaitForChild("LogikaEwolucji"))
local Efekty = require(Moduly:WaitForChild("EfektyEwolucji"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan = Sygnaly:WaitForChild("Stan")
local wzorce = ReplicatedStorage:WaitForChild(D.wzorceRS, 30)
local UI = D.ui
local NF = #D.formy
local C = Vector3.new(D.pole.srodek[1], D.pole.srodek[2], D.pole.srodek[3])
local kamera = workspace.CurrentCamera
local function hex(h: string): Color3
	return Color3.fromHex(h)
end
local tusz, papier, zloto = hex(UI.kolory.tusz), hex(UI.kolory.papier), hex(UI.kolory.zloto)
local czcionka = Enum.Font[UI.czcionka] or Enum.Font.LuckiestGuy
local cyfry = Enum.Font[UI.czcionka_cyfr] or Enum.Font.FredokaOne

local lokalne = Instance.new("Folder")
lokalne.Name = "EwolucjaLokalne"
lokalne.Parent = workspace
local E = Efekty.nowe(lokalne, D)

------------------------------------------------------------------ dźwięki (odcinki arkusza efektów Pet Areny)
local folderDz = Instance.new("Folder")
folderDz.Name = "EwolucjaDzwieki"
folderDz.Parent = SoundService
local pule: { [string]: { Sound } } = {}
local DZ = D.dzwieki
if DZ.arkusz and DZ.arkusz > 0 then
	for rola, e in DZ.efekty do
		local lista = {}
		for _ = 1, 3 do
			local s = Instance.new("Sound")
			s.SoundId = "rbxassetid://" .. tostring(DZ.arkusz)
			s.Volume = e.glosnosc
			s.PlaybackRegionsEnabled = true
			s.PlaybackRegion = NumberRange.new(e.od, e.koniec)
			s.Parent = folderDz
			table.insert(lista, s)
		end
		pule[rola] = lista
	end
end
local function dzwiek(rola: string, ton: number?)
	local p = pule[rola]
	if not p then
		return
	end
	local s = table.remove(p, 1)
	table.insert(p, s)
	s.PlaybackSpeed = ton or 1
	s.TimePosition = DZ.efekty[rola].od
	s:Play()
end

------------------------------------------------------------------ sterowanie awatara wyłączone (gracz jest potworem)
task.spawn(function()
	local ok, m = pcall(function()
		return require(gracz:WaitForChild("PlayerScripts"):WaitForChild("PlayerModule", 10))
	end)
	if ok and m then
		pcall(function()
			m:GetControls():Disable()
		end)
	end
end)

------------------------------------------------------------------ ekran
local gui = Instance.new("ScreenGui")
gui.Name = "Ewolucja"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
gui.Parent = playerGui
E:warstwa2D(gui)

local function nowy(klasa: string, wl, rodzic: Instance?): any
	local o = Instance.new(klasa)
	for k, v in wl do
		o[k] = v
	end
	if rodzic then
		o.Parent = rodzic
	end
	return o
end
local function rog(o: Instance, r: number)
	nowy("UICorner", { CornerRadius = UDim.new(0, r) }, o)
end
local function obrys(o: Instance, g: number, k: Color3)
	return nowy("UIStroke", { Thickness = g, Color = k, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, o)
end
local function napis(o: Instance, t: string, poz: UDim2, roz: UDim2, kolor: Color3?, font: Enum.Font?): TextLabel
	local l = nowy("TextLabel", { BackgroundTransparency = 1, Position = poz, Size = roz, Text = t, TextScaled = true, Font = font or czcionka,
		TextColor3 = kolor or papier }, o)
	nowy("UIStroke", { Thickness = 2, Color = tusz }, l)
	return l
end

-- ekran (w próbach można emulować telefon atrybutem EW_Emulacja = Vector2; zwykle Device Simulator Studio)
local ekran = nowy("Frame", { Name = "Ekran", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1 }, gui)
local ekranSkala = nowy("UIScale", { Scale = 1 }, ekran)
local emulacja: Vector2? = nil
local skale: { UIScale } = {}
local function skalaEkranu(): number
	local v = emulacja or kamera.ViewportSize
	return math.clamp(math.min(v.X / 667, v.Y / 375), 1, 1.8)
end
local function warstwa(nazwa: string, kotwica: Vector2, poz: UDim2, roz: Vector2): Frame
	local f = nowy("Frame", { Name = nazwa, AnchorPoint = kotwica, Position = poz, Size = UDim2.fromOffset(roz.X, roz.Y), BackgroundTransparency = 1 }, ekran)
	table.insert(skale, nowy("UIScale", { Scale = skalaEkranu() }, f))
	return f
end
local function ustawEmulacje()
	local e = gracz:GetAttribute("EW_Emulacja")
	emulacja = if typeof(e) == "Vector2" then e else nil
	local v = kamera.ViewportSize
	if emulacja then
		local k = math.min(v.X / emulacja.X, v.Y / emulacja.Y)
		ekran.Size = UDim2.fromOffset(emulacja.X, emulacja.Y)
		ekran.Position = UDim2.fromOffset((v.X - emulacja.X * k) / 2, (v.Y - emulacja.Y * k) / 2)
		ekranSkala.Scale = k
	else
		ekran.Size = UDim2.fromScale(1, 1)
		ekran.Position = UDim2.new()
		ekranSkala.Scale = 1
	end
	for _, s in skale do
		s.Scale = skalaEkranu()
	end
end
gracz:GetAttributeChangedSignal("EW_Emulacja"):Connect(ustawEmulacje)
kamera:GetPropertyChangedSignal("ViewportSize"):Connect(ustawEmulacje)
local function doEkranu(p: Vector2): Vector2
	return (p - ekran.AbsolutePosition) / ekranSkala.Scale
end

local function przyciskOkragly(rodzic: Instance, nazwa: string, t: string, rozmiar: number, kolor: string)
	local b = nowy("TextButton", { Name = nazwa, Size = UDim2.fromOffset(rozmiar, rozmiar), BackgroundColor3 = hex(kolor), Text = "", AutoButtonColor = true }, rodzic)
	rog(b, rozmiar // 2)
	obrys(b, 3, tusz)
	local cien = nowy("Frame", { Name = "Odnowa", AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0, 1), Size = UDim2.fromScale(1, 0),
		BackgroundColor3 = tusz, BackgroundTransparency = 0.45, BorderSizePixel = 0, ZIndex = 2 }, b)
	rog(cien, rozmiar // 2)
	local l = napis(b, t, UDim2.fromScale(0.1, 0.32), UDim2.fromScale(0.8, 0.36))
	l.ZIndex = 3
	l.Name = "Napis"
	return b, cien, l
end

-- pasek wzrostu (góra, środek)
local ramkaWzrostu = warstwa("Wzrost", Vector2.new(0.5, 0), UDim2.new(0.5, -40, 0, 6), Vector2.new(230, 48))
local nazwaFormy = napis(ramkaWzrostu, "", UDim2.fromOffset(0, 0), UDim2.new(1, 0, 0, 22))
local pasekTlo = nowy("Frame", { Position = UDim2.fromOffset(6, 26), Size = UDim2.new(1, -12, 0, 18), BackgroundColor3 = tusz }, ramkaWzrostu)
rog(pasekTlo, 9)
obrys(pasekTlo, 2, papier)
local pasekW = nowy("Frame", { Size = UDim2.fromScale(0, 1), BackgroundColor3 = hex("6BD66B"), BorderSizePixel = 0 }, pasekTlo)
rog(pasekW, 9)
local pasekNapis = napis(pasekTlo, "", UDim2.fromScale(0, 0.05), UDim2.fromScale(1, 0.9), papier, cyfry)
pasekNapis.ZIndex = 2

-- złoto + DEN (góra, na prawo od paska)
local ramkaZlota = warstwa("Zloto", Vector2.new(0, 0), UDim2.new(0.5, 82, 0, 6), Vector2.new(150, 46))
local bLegowisko = nowy("TextButton", { Name = "Legowisko", Size = UDim2.fromScale(1, 1), BackgroundColor3 = hex("3A2F4A"), Text = "", AutoButtonColor = true }, ramkaZlota)
rog(bLegowisko, 12)
obrys(bLegowisko, 3, zloto)
local moneta = nowy("Frame", { Position = UDim2.fromOffset(6, 9), Size = UDim2.fromOffset(28, 28), BackgroundColor3 = zloto }, bLegowisko)
rog(moneta, 14)
obrys(moneta, 2, tusz)
local zlotoNapis = napis(bLegowisko, "0", UDim2.fromOffset(38, 3), UDim2.new(1, -44, 0, 24), zloto, cyfry)
zlotoNapis.TextXAlignment = Enum.TextXAlignment.Left
local naSNapis = napis(bLegowisko, "", UDim2.fromOffset(38, 26), UDim2.new(1, -44, 0, 17), papier, cyfry)
naSNapis.TextXAlignment = Enum.TextXAlignment.Left

-- toast (dymek pod złotem)
local ramkaToastu = warstwa("Toast", Vector2.new(0, 0), UDim2.new(0.5, 82, 0, 58), Vector2.new(150, 34))
local toastTlo = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = zloto }, ramkaToastu)
rog(toastTlo, 10)
obrys(toastTlo, 2, tusz)
local toastNapis = napis(toastTlo, "", UDim2.fromScale(0.05, 0.1), UDim2.fromScale(0.9, 0.8), tusz, cyfry)
toastNapis:FindFirstChildOfClass("UIStroke"):Destroy()
ramkaToastu.Visible = false
local toastDo = 0
local function toast(t: string, czas: number?)
	toastNapis.Text = t
	ramkaToastu.Visible = true
	toastDo = os.clock() + (czas or 3)
end

-- przyciski akcji (prawy dół)
local ramkaGryz = warstwa("Gryz", Vector2.new(1, 1), UDim2.new(1, -14, 1, -14), Vector2.new(96, 96))
local bGryz, cienGryz = przyciskOkragly(ramkaGryz, "Gryz", UI.gryz, 96, "FF5A5A")
local ramkaZryw = warstwa("Zryw", Vector2.new(1, 1), UDim2.new(1, -122, 1, -14), Vector2.new(68, 68))
local bZryw, cienZryw = przyciskOkragly(ramkaZryw, "Zryw", UI.zryw, 68, "FF9A3D")
local ramkaUm = warstwa("Umiejetnosc", Vector2.new(1, 1), UDim2.new(1, -14, 1, -122), Vector2.new(68, 68))
local bUm, cienUm, napisUm = przyciskOkragly(ramkaUm, "Umiejetnosc", "", 68, "4FB3FF")
napisUm.Position = UDim2.fromScale(0.08, 0.3)
napisUm.Size = UDim2.fromScale(0.84, 0.4)

-- EVOLVE (dół, środek) — tylko przy pełnym pasku
local ramkaEwo = warstwa("Ewolucja", Vector2.new(0.5, 1), UDim2.new(0.5, -40, 1, -16), Vector2.new(176, 62))
local bEwo = nowy("TextButton", { Name = "Ewoluuj", Size = UDim2.fromScale(1, 1), BackgroundColor3 = hex("C27BFF"), Text = "", AutoButtonColor = true }, ramkaEwo)
rog(bEwo, 18)
local obrysEwo = obrys(bEwo, 4, zloto)
napis(bEwo, UI.ewoluuj, UDim2.fromScale(0.06, 0.14), UDim2.fromScale(0.88, 0.72))
local skalaEwo = nowy("UIScale", { Scale = 1 }, bEwo)
ramkaEwo.Visible = false

-- podpowiedź (dół, środek, nad EVOLVE)
local ramkaPodp = warstwa("Podpowiedz", Vector2.new(0.5, 1), UDim2.new(0.5, -40, 1, -86), Vector2.new(250, 30))
local podpTlo = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.3 }, ramkaPodp)
rog(podpTlo, 10)
local podpNapis = napis(podpTlo, UI.podpowiedz_start, UDim2.fromScale(0.04, 0.12), UDim2.fromScale(0.92, 0.76), hex(UI.kolory.ty))

-- baner (duże słowo) i tabliczka odsłony
local ramkaBaneru = warstwa("Baner", Vector2.new(0.5, 0), UDim2.new(0.5, -40, 0, 62), Vector2.new(330, 50))
local baner = napis(ramkaBaneru, "", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
local banerSkala = nowy("UIScale", { Scale = 1 }, baner)
baner.Visible = false
local banerT, banerDo = 0, 0
local function pokazBaner(t: string, kolor: Color3, czas: number?)
	baner.Text = t
	baner.TextColor3 = kolor
	baner.Visible = true
	baner.Rotation = math.random(-3, 3)
	banerT, banerDo = 0, czas or 1.3
end

local ramkaTabl = warstwa("Tabliczka", Vector2.new(0.5, 0), UDim2.new(0.5, -40, 0, 58), Vector2.new(330, 116))
local tablTlo = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.15 }, ramkaTabl)
rog(tablTlo, 16)
obrys(tablTlo, 3, zloto)
local tablGora = napis(tablTlo, "", UDim2.fromOffset(10, 6), UDim2.new(1, -20, 0, 24), hex("9BFFB8"))
local tablNazwa = napis(tablTlo, "", UDim2.fromOffset(10, 30), UDim2.new(1, -20, 0, 46), zloto)
local tablDol = napis(tablTlo, "", UDim2.fromOffset(10, 78), UDim2.new(1, -20, 0, 20), papier, cyfry)
local tablDol2 = napis(tablTlo, "", UDim2.fromOffset(10, 98), UDim2.new(1, -20, 0, 18), zloto, cyfry)
local tablSkala = nowy("UIScale", { Scale = 1 }, tablTlo)
ramkaTabl.Visible = false

-- drążek pod lewym kciukiem
local drazek = warstwa("Drazek", Vector2.new(0.5, 0.5), UDim2.fromOffset(100, 280), Vector2.new(116, 116))
local drazekBaza = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.5 }, drazek)
rog(drazekBaza, 58)
obrys(drazekBaza, 3, hex(UI.kolory.ty))
local galka = nowy("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromOffset(50, 50),
	BackgroundColor3 = hex(UI.kolory.ty) }, drazekBaza)
rog(galka, 25)
drazek.Visible = false

------------------------------------------------------------------ miniatury modeli (ViewportFrame): drabina i legowisko
local function wzorzecModelu(f: number): Model?
	local nazwa = D.formy[f].wzorzec
	return wzorce and wzorce:FindFirstChild(nazwa)
end

local function miniatura(rodzic: Instance, f: number, rozmiar: UDim2, poz: UDim2): ViewportFrame
	local vf = nowy("ViewportFrame", { Size = rozmiar, Position = poz, BackgroundTransparency = 1, Ambient = Color3.fromRGB(190, 190, 190),
		LightColor = Color3.new(1, 1, 1), LightDirection = Vector3.new(-1, -1.4, -1) }, rodzic)
	local wz = wzorzecModelu(f)
	if wz then
		local m = wz:Clone()
		m:PivotTo(CFrame.new(0, 0, 0) * CFrame.Angles(0, math.rad(200), 0))
		m.Parent = vf
		local cf, roz = m:GetBoundingBox()
		local cam = Instance.new("Camera")
		cam.FieldOfView = 40
		local d = math.max(roz.X, roz.Y, roz.Z) * 1.55
		cam.CFrame = CFrame.lookAt(cf.Position + Vector3.new(0, d * 0.25, d), cf.Position)
		cam.Parent = vf
		vf.CurrentCamera = cam
	end
	return vf
end

local function sylwetka(vf: ViewportFrame, ciemna: boolean)
	vf.ImageColor3 = if ciemna then Color3.new(0, 0, 0) else Color3.new(1, 1, 1)
	vf.ImageTransparency = if ciemna then 0.15 else 0
end

-- drabina (lewa krawędź): formy 1..NF-1 od dołu, na szczycie wielki cień Olbrzyma
-- pod strefą górnego paska Roblox (przycisk menu w lewym górnym rogu telefonu)
local ramkaDrabiny = warstwa("Drabina", Vector2.new(0, 0), UDim2.new(0, 8, 0, 62), Vector2.new(50, 262))
local drabinaTlo = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.45 }, ramkaDrabiny)
rog(drabinaTlo, 14)
local szczeble = {}
do
	local wys, krok = 26, 29
	-- szczyt: Olbrzym
	local sz = nowy("Frame", { Name = "Szczebel" .. NF, Position = UDim2.fromOffset(2, 2), Size = UDim2.fromOffset(46, 46), BackgroundColor3 = hex("2A2236"),
		BackgroundTransparency = 0.2 }, drabinaTlo)
	rog(sz, 12)
	local ob = obrys(sz, 2, hex("6A5A7A"))
	local vf = miniatura(sz, NF, UDim2.fromScale(1.25, 1.25), UDim2.fromScale(-0.125, -0.2))
	local q = napis(sz, UI.drabina_szczyt, UDim2.fromScale(0.25, 0.25), UDim2.fromScale(0.5, 0.5), hex("B8A8C8"))
	szczeble[NF] = { ramka = sz, vf = vf, znak = q, obrys = ob }
	for f = NF - 1, 1, -1 do
		local y = 52 + (NF - 1 - f) * krok
		local s = nowy("Frame", { Name = "Szczebel" .. f, Position = UDim2.fromOffset(12, y), Size = UDim2.fromOffset(wys, wys), BackgroundColor3 = hex("2A2236"),
			BackgroundTransparency = 0.2 }, drabinaTlo)
		rog(s, 13)
		local o = obrys(s, 2, hex("6A5A7A"))
		local v = miniatura(s, f, UDim2.fromScale(1.3, 1.3), UDim2.fromScale(-0.15, -0.2))
		local z = napis(s, "?", UDim2.fromScale(0.2, 0.15), UDim2.fromScale(0.6, 0.7), hex("B8A8C8"))
		szczeble[f] = { ramka = s, vf = v, znak = z, obrys = o }
	end
end
local strzalkaDrabiny = napis(drabinaTlo, ">", UDim2.fromOffset(0, 0), UDim2.fromOffset(12, 22), hex(UI.kolory.ty))

------------------------------------------------------------------ panel legowiska (trofea + ulepszenia)
local panel = nowy("Frame", { Name = "PanelLegowiska", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
	Size = UDim2.fromOffset(470, 300), BackgroundColor3 = hex("2A2236"), BackgroundTransparency = 0.04, ZIndex = 20 }, ekran)
table.insert(skale, nowy("UIScale", { Scale = skalaEkranu() }, panel))
rog(panel, 18)
obrys(panel, 3, zloto)
panel.Visible = false
local panelTytul = napis(panel, UI.legowisko_tytul, UDim2.fromOffset(16, 8), UDim2.fromOffset(200, 32), zloto)
panelTytul.TextXAlignment = Enum.TextXAlignment.Left
local panelStawka = napis(panel, "", UDim2.fromOffset(220, 12), UDim2.fromOffset(170, 26), papier, cyfry)
local bZamknij = nowy("TextButton", { Name = "Zamknij", Position = UDim2.new(1, -54, 0, 6), Size = UDim2.fromOffset(46, 46), BackgroundColor3 = hex("FF5A5A"),
	Text = "", AutoButtonColor = true }, panel)
rog(bZamknij, 12)
obrys(bZamknij, 3, tusz)
napis(bZamknij, UI.zamknij, UDim2.fromScale(0.2, 0.15), UDim2.fromScale(0.6, 0.7))
napis(panel, UI.legowisko_opis, UDim2.fromOffset(16, 40), UDim2.fromOffset(380, 16), hex("C8B8D8"), cyfry)
local trofea = {}
for f = 1, NF do
	local x = 14 + (f - 1) * 56
	local t = nowy("Frame", { Name = "Trofeum" .. f, Position = UDim2.fromOffset(x, 60), Size = UDim2.fromOffset(50, 64), BackgroundColor3 = hex("3A2F4A") }, panel)
	rog(t, 10)
	local o = obrys(t, 2, hex("5A4A6A"))
	local v = miniatura(t, f, UDim2.fromOffset(50, 46), UDim2.fromOffset(0, 0))
	local z = napis(t, "?", UDim2.fromOffset(12, 8), UDim2.fromOffset(26, 30), hex("8A7A9A"))
	local s = napis(t, "+" .. D.formy[f].trofeum, UDim2.fromOffset(2, 46), UDim2.fromOffset(46, 16), zloto, cyfry)
	trofea[f] = { ramka = t, vf = v, znak = z, stawka = s, obrys = o }
end
local karty = {}
for i, U in D.ulepszenia do
	local x = 14 + (i - 1) * 150
	local k = nowy("Frame", { Name = "Karta_" .. U.id, Position = UDim2.fromOffset(x, 134), Size = UDim2.fromOffset(142, 156), BackgroundColor3 = hex("3A2F4A") }, panel)
	rog(k, 12)
	obrys(k, 2, hex("6A5A7A"))
	napis(k, U.nazwa, UDim2.fromOffset(8, 6), UDim2.new(1, -16, 0, 24), papier)
	napis(k, U.opis, UDim2.fromOffset(8, 30), UDim2.new(1, -16, 0, 16), hex("C8B8D8"), cyfry)
	local kropki = {}
	for p = 1, #U.ceny + 1 do
		local kr = nowy("Frame", { Position = UDim2.new(0.5, (p - (#U.ceny + 2) / 2) * 22 - 8, 0, 52), Size = UDim2.fromOffset(16, 16), BackgroundColor3 = hex("5A4A6A") }, k)
		rog(kr, 8)
		obrys(kr, 2, tusz)
		kropki[p] = kr
	end
	local wart = napis(k, "", UDim2.fromOffset(8, 72), UDim2.new(1, -16, 0, 20), hex("9BFFB8"), cyfry)
	local b = nowy("TextButton", { Name = "Kup", Position = UDim2.new(0, 10, 1, -56), Size = UDim2.new(1, -20, 0, 48), BackgroundColor3 = hex("3DB36B"),
		Text = "", AutoButtonColor = true }, k)
	rog(b, 12)
	obrys(b, 3, tusz)
	local bn = napis(b, "", UDim2.fromScale(0.06, 0.15), UDim2.fromScale(0.88, 0.7), papier, cyfry)
	karty[U.id] = { ramka = k, kropki = kropki, wart = wart, przycisk = b, napis = bn, U = U }
end

------------------------------------------------------------------ modele: klon, skala, części i przesunięcia (BulkMoveTo)
local function zrobModel(f: number)
	local F = D.formy[f]
	local wz = wzorzecModelu(f)
	local m
	if wz then
		m = wz:Clone()
	else
		m = Instance.new("Model")
		local p = Instance.new("Part")
		p.Size = Vector3.new(3, 3, 3)
		p.Parent = m
		m.PrimaryPart = p
	end
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
		end
	end
	m:PivotTo(CFrame.new())
	pcall(function()
		m:ScaleTo(F.r / F.model_r)
	end)
	local czesci, offs, poz = {}, {}, {}
	local piv = m:GetPivot()
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			table.insert(czesci, d)
			local o = piv:ToObjectSpace(d.CFrame)
			table.insert(offs, o.Rotation)
			table.insert(poz, o.Position)
		end
	end
	m.Parent = lokalne
	return m, czesci, offs, poz
end

local function krazek(r: number): Part
	local k = Instance.new("Part")
	k.Shape = Enum.PartType.Cylinder
	k.Anchored = true
	k.CanCollide = false
	k.CanQuery = false
	k.CanTouch = false
	k.CastShadow = false
	k.Material = Enum.Material.Neon
	k.Color = Color3.new(1, 1, 1)
	k.Size = Vector3.new(0.15, r * 2 + 1, r * 2 + 1)
	k.Parent = lokalne
	return k
end

local function kula(kolor: Color3, mat: Enum.Material, przezr: number): Part
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Material = mat
	p.Color = kolor
	p.Transparency = 1
	p.Size = Vector3.one
	p.Parent = lokalne
	p:SetAttribute("Przezr", przezr)
	return p
end

------------------------------------------------------------------ stan
local widoki: { [number]: any } = {}
local mojId = 0
local olbrzymId = 0
local tGlob = 0
local wstrzas = { sila = 0, do_ = 0 }
local function wstrzasnij(s: number, czas: number)
	wstrzas.sila = math.max(wstrzas.sila, s)
	wstrzas.do_ = math.max(wstrzas.do_, os.clock() + czas)
end
local tStartu = os.clock()
local pierwszaKulka: number? = nil
local kulekZjedzonych = 0
local odslona: any = nil -- { t, czas, nowa, forma, faza }
local liczKorekt, liczSnapow, bladMaks, liczGryzow, liczOdslon, liczZjedzen, liczZjadl = 0, 0, 0, 0, 0, 0, 0
-- przewidywanie własnego potwora (pozycja i prędkość u klienta)
local predX, predZ, predVX, predVZ = 0, 0, 0, 0
local predOK = false

local korona = Instance.new("Model")
do
	local function c(roz: Vector3, cf: CFrame)
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Material = Enum.Material.Neon
		p.Color = zloto
		p.Size = roz
		p.CFrame = cf
		p.Parent = korona
		return p
	end
	korona.PrimaryPart = c(Vector3.new(4, 1, 4), CFrame.new())
	for i = 0, 4 do
		local a = i * math.pi * 2 / 5
		c(Vector3.new(0.9, 2, 0.9), CFrame.new(math.cos(a) * 1.6, 1.4, math.sin(a) * 1.6))
	end
end

-- kulki (stałe miejsca; żywe/zjedzone z bitmapy migawki)
local kulkiCzesci, kulkiCF, kulkiZywe = {}, {}, {}
for i, p in D.kulkiPoz do
	local duza = p[3] == 2
	local k = Instance.new("Part")
	k.Name = "Kulka" .. i
	k.Shape = Enum.PartType.Ball
	k.Anchored = true
	k.CanCollide = false
	k.CanQuery = false
	k.CanTouch = false
	k.CastShadow = false
	k.Material = Enum.Material.Neon
	k.Color = if duza then hex(UI.kolory.kulka_duza) else hex(UI.kolory.kulka_mala)
	k.Size = Vector3.one * (if duza then D.jedzenie.duza_r else D.jedzenie.mala_r) * 2
	k.Position = C + Vector3.new(p[1], 1, p[2])
	k.Parent = lokalne
	kulkiCzesci[i] = k
	kulkiCF[i] = k.CFrame
	kulkiZywe[i] = true
end

local function mojaForma(): number
	return gracz:GetAttribute("EW_Forma") or 1
end
-- byt-atrapa do rachunków przewidywania (prędkość z Szybkości, zasięg Szczęki)
local function ja()
	return { slot = 1, forma = mojaForma(), poziomy = { szczeka = gracz:GetAttribute("EW_Poz_szczeka") or 1,
		szybkosc = gracz:GetAttribute("EW_Poz_szybkosc") or 1, apetyt = gracz:GetAttribute("EW_Poz_apetyt") or 1 } }
end

local function ustawPrzezroczystosc(w, wartosc: number)
	if w.przezr == wartosc then
		return
	end
	w.przezr = wartosc
	for _, p in w.czesci do
		p.LocalTransparencyModifier = wartosc
	end
end

local function zbudujModel(w, f: number)
	if w.model then
		w.model:Destroy()
	end
	w.model, w.czesci, w.offs, w.poz = zrobModel(f)
	w.cf = table.create(#w.czesci)
	w.forma = f
	w.przezr = -1
	if w.id == mojId then
		local hl = Instance.new("Highlight")
		hl.FillTransparency = 1
		hl.OutlineColor = hex(UI.kolory.ty)
		hl.OutlineTransparency = 0.2
		hl.DepthMode = Enum.HighlightDepthMode.Occluded
		hl.Parent = w.model
	end
end

local function nowyWidok(id: number, slot: number, f: number, x: number, z: number)
	local w = { id = id, slot = slot, x = x, z = z, tx = x, tz = z, kier = 0, tkier = 0, flagi = 0, martwy = false, brak = 0,
		faza = math.random() * 6, v = 0, px = x, pz = z, skret = 0, gryzT = 99, pulsT = 99, pulsSila = 0, skokT = 0,
		krazek = krazek(D.formy[f].r), kokon = kula(Color3.new(1, 1, 1), Enum.Material.Neon, 0.05),
		tarcza = kula(hex("7FE9FF"), Enum.Material.ForceField, 0.2), vx = 0, vz = 0 }
	zbudujModel(w, f)
	widoki[id] = w
	return w
end

local function usunWidok(w)
	w.model:Destroy()
	w.krazek:Destroy()
	w.kokon:Destroy()
	w.tarcza:Destroy()
	widoki[w.id] = nil
end

------------------------------------------------------------------ migawki
local czasMigawki = 0
evStan.OnClientEvent:Connect(function(b: buffer)
	if typeof(b) ~= "buffer" then
		return
	end
	local n = buffer.readu16(b, 8)
	olbrzymId = buffer.readu16(b, 10)
	local nk = #D.kulkiPoz
	local nb = math.ceil(nk / 8)
	for i = 0, nb - 1 do
		local bajt = buffer.readu8(b, 12 + i)
		for k = 0, 7 do
			local idx = i * 8 + k + 1
			if idx <= nk then
				local zywa = bit32.band(bajt, 2 ^ k) ~= 0
				if zywa ~= kulkiZywe[idx] then
					kulkiZywe[idx] = zywa
					kulkiCzesci[idx].Transparency = if zywa then 0 else 1
				end
			end
		end
	end
	local widziane = {}
	local o0 = 12 + nb
	for i = 1, n do
		local o = o0 + (i - 1) * 15
		local id = buffer.readu16(b, o)
		local slot = buffer.readu8(b, o + 2)
		local fl = buffer.readu8(b, o + 3)
		local f = buffer.readu8(b, o + 4)
		local x, z = buffer.readf32(b, o + 5), buffer.readf32(b, o + 9)
		widziane[id] = true
		local w = widoki[id] or nowyWidok(id, slot, f, x, z)
		local martwy = bit32.band(fl, 4) ~= 0
		if w.martwy and not martwy then
			w.x, w.z = x, z -- odrodzenie: skok na nowe miejsce
			if id == mojId then
				predOK = false
			end
		end
		if bit32.band(fl, 32) ~= 0 and bit32.band(w.flagi, 32) == 0 then
			w.skokT = 0
		end
		if bit32.band(fl, 64) ~= 0 and bit32.band(w.flagi, 64) == 0 and id ~= mojId then
			w.gryzT = 0 -- cudzy wypad przy gryzieniu
		end
		w.tx, w.tz, w.flagi, w.martwy = x, z, fl, martwy
		w.tkier = if id == mojId and not martwy and bit32.band(fl, 8 + 16 + 32) == 0 then w.tkier else buffer.readi16(b, o + 13) / 1000
		if f ~= w.forma then
			zbudujModel(w, f)
		end
		w.brak = 0
	end
	for id, w in widoki do
		if not widziane[id] then
			w.brak += 1
			if w.brak >= 3 then
				usunWidok(w)
			end
		end
	end
	czasMigawki = os.clock()
end)

------------------------------------------------------------------ sterowanie: drążek / WASD / gałka; przewidywanie
local wektor = Vector3.zero
local dotykDrazka: InputObject? = nil
local drazekSrodek = Vector2.zero
local sterTest: any = nil
local doRuchu, doRaportu = 0, 0
local wyslany: Vector3? = nil
local zrywDo, zrywGotowy, szarzaDo, szarzaV, gryzGotowy, umGotowy = 0, 0, 0, 1, 0, 0

local function serwerSteruje(fl: number): boolean
	return bit32.band(fl, 4 + 8 + 16 + 32) ~= 0
end

local function wejscie(): Vector2
	local x, y = 0, 0
	if UserInputService:IsKeyDown(Enum.KeyCode.W) or UserInputService:IsKeyDown(Enum.KeyCode.Up) then
		y += 1
	end
	if UserInputService:IsKeyDown(Enum.KeyCode.S) or UserInputService:IsKeyDown(Enum.KeyCode.Down) then
		y -= 1
	end
	if UserInputService:IsKeyDown(Enum.KeyCode.D) or UserInputService:IsKeyDown(Enum.KeyCode.Right) then
		x += 1
	end
	if UserInputService:IsKeyDown(Enum.KeyCode.A) or UserInputService:IsKeyDown(Enum.KeyCode.Left) then
		x -= 1
	end
	local v = Vector2.new(x, y)
	for _, s in UserInputService:GetGamepadState(Enum.UserInputType.Gamepad1) do
		if s.KeyCode == Enum.KeyCode.Thumbstick1 and s.Position.Magnitude > 0.2 then
			v = Vector2.new(s.Position.X, s.Position.Y)
		end
	end
	if dotykDrazka then
		local d = Vector2.new(dotykDrazka.Position.X, dotykDrazka.Position.Y) - drazekSrodek
		v = Vector2.new(d.X, -d.Y) / (50 * skalaEkranu() * ekranSkala.Scale)
	end
	if sterTest and os.clock() < sterTest.do_ then
		v = sterTest.v
	end
	if v.Magnitude > 1 then
		v = v.Unit
	end
	return v
end

local function krokSterowania(dt: number)
	local v = if odslona and odslona.faza == "kokon" then Vector2.zero else wejscie()
	-- kamera ma stałą orientację: góra ekranu = +z świata, prawo = −x
	wektor = Vector3.new(-v.X, 0, v.Y)
	galka.Position = UDim2.new(0.5, v.X * 34, 0.5, -v.Y * 34)
	local w = widoki[mojId]
	if not w then
		return
	end
	if not predOK or serwerSteruje(w.flagi) then
		-- serwer prowadzi (śmierć, kokon, ogłuszenie, skok): za serwerem
		predX, predZ, predVX, predVZ = w.tx, w.tz, 0, 0
		predOK = true
	else
		local teraz = os.clock()
		local m = 1
		if teraz < zrywDo then
			m = D.ruch.zryw_v
		end
		if teraz < szarzaDo then
			m = math.max(m, szarzaV)
		end
		local cel = L.predkosc(D, ja()) * m
		local a = math.min(1, D.ruch.przyspieszenie * dt * (if m > 1 then 3 else 1))
		local kx, kz = wektor.X, wektor.Z
		if v.Magnitude <= D.siec.martwa_strefa then
			kx, kz = 0, 0
		end
		if m > 1 and kx == 0 and kz == 0 then
			kx, kz = math.sin(w.kier), math.cos(w.kier)
		end
		predVX += (kx * cel - predVX) * a
		predVZ += (kz * cel - predVZ) * a
		predX += predVX * dt
		predZ += predVZ * dt
		local r = D.formy[w.forma].r
		predX, predZ = L.ogranicz(D, predX, predZ, r)
		-- odbicia od tych, których nie zjem i którzy mnie nie zjedzą (jak na serwerze)
		local mf = w.forma
		for id, q in widoki do
			if id ~= mojId and not q.martwy and bit32.band(q.flagi, 8 + 32) == 0 then
				local rq = D.formy[q.forma].r
				local dx, dz = predX - q.x, predZ - q.z
				local d = math.sqrt(dx * dx + dz * dz)
				local jem = mf >= q.forma + 1 and not (q.slot > 0 and q.forma <= D.smierc.chronione_formy)
				local jedza = q.forma >= mf + 1 and not (q.slot > 0 and mf <= D.smierc.chronione_formy)
				local tarczaQ = bit32.band(q.flagi, 1) ~= 0
				if d < r + rq and d > 0.01 and ((not jem and not jedza) or (jem and tarczaQ)) then
					local wnik = (r + rq - d) * (if mf < q.forma then 0.75 elseif mf > q.forma then 0.25 else 0.5)
					predX += dx / d * wnik
					predZ += dz / d * wnik
				end
			end
		end
		if kx ~= 0 or kz ~= 0 then
			w.tkier = math.atan2(kx, kz)
		end
		-- zgodność z serwerem: duży rozjazd (np. odbicie od cudzego) → łagodnie do serwera
		local ex, ez = w.tx - predX, w.tz - predZ
		local blad = math.sqrt(ex * ex + ez * ez)
		bladMaks = math.max(bladMaks, blad)
		local prog = 6 + cel * 0.5
		if blad > prog * 2.5 then
			predX, predZ = w.tx, w.tz
			liczSnapow += 1
		elseif blad > prog then
			predX += ex * math.min(1, dt * 4)
			predZ += ez * math.min(1, dt * 4)
		end
	end
	-- wysyłka: kierunek + pozycja
	doRuchu -= dt
	doRaportu -= dt
	local aktywny = v.Magnitude > D.siec.martwa_strefa
	local zmiana = not wyslany or (wyslany - wektor).Magnitude > 0.25
	if (aktywny and (doRuchu <= 0 or zmiana)) or (not aktywny and wyslany and wyslany.Magnitude > 0.01) or doRaportu <= 0 then
		doRuchu = D.siec.ruch_co_s
		doRaportu = 0.25
		local kx, kz = if aktywny then wektor.X else 0, if aktywny then wektor.Z else 0
		if serwerSteruje(w.flagi) then
			evAkcja:FireServer("ruch", kx, kz)
		else
			evAkcja:FireServer("ruch", kx, kz, predX, predZ)
		end
		wyslany = Vector3.new(kx, 0, kz)
	end
end

------------------------------------------------------------------ akcje gracza (przycisk = natychmiastowa odpowiedź na ekranie)
local function akcja(rodzaj: string, a: any?)
	local w = widoki[mojId]
	local teraz = os.clock()
	if rodzaj == "gryz" then
		if teraz < gryzGotowy then
			return
		end
		gryzGotowy = teraz + L.przerwaGryzu(D, ja())
		liczGryzow += 1
		gracz:SetAttribute("EW_K_Gryzy", liczGryzow)
		if w then
			w.gryzT = 0 -- wypad od razu, wynik przyjdzie z serwera
		end
		dzwiek("cios", 1.5)
		evAkcja:FireServer("gryz")
	elseif rodzaj == "zryw" then
		if teraz < zrywGotowy then
			return
		end
		zrywGotowy = teraz + D.ruch.zryw_odnowa_s
		zrywDo = teraz + D.ruch.zryw_s
		dzwiek("umiejetnosc", 1.4)
		if w then
			E:pyl(C + Vector3.new(predX, 0.5, predZ), D.formy[w.forma].r, 6)
		end
		evAkcja:FireServer("zryw")
	elseif rodzaj == "umiejetnosc" then
		if teraz < umGotowy or not w then
			return
		end
		local A = D.formy[w.forma].um
		umGotowy = teraz + A.odnowa_s
		if A.typ == "szarza" then
			szarzaDo, szarzaV = teraz + A.s, A.v
		end
		evAkcja:FireServer("umiejetnosc")
	elseif rodzaj == "ewoluuj" then
		evAkcja:FireServer("ewoluuj")
		dzwiek("klik", 1.2)
	elseif rodzaj == "kup" then
		evAkcja:FireServer("kup", a)
		dzwiek("klik", 1)
	end
end
bGryz.Activated:Connect(function()
	akcja("gryz")
end)
bZryw.Activated:Connect(function()
	akcja("zryw")
end)
bUm.Activated:Connect(function()
	akcja("umiejetnosc")
end)
bEwo.Activated:Connect(function()
	akcja("ewoluuj")
end)
local function pokazPanel(tak: boolean)
	panel.Visible = tak
	dzwiek("klik", if tak then 1.1 else 0.9)
end
bLegowisko.Activated:Connect(function()
	pokazPanel(not panel.Visible)
end)
bZamknij.Activated:Connect(function()
	pokazPanel(false)
end)
for id, k in karty do
	k.przycisk.Activated:Connect(function()
		akcja("kup", id)
	end)
end

UserInputService.InputBegan:Connect(function(wej: InputObject, przetworzone: boolean)
	if wej.UserInputType == Enum.UserInputType.Gamepad1 then
		local k = wej.KeyCode
		if k == Enum.KeyCode.ButtonA then
			akcja("gryz")
		elseif k == Enum.KeyCode.ButtonB or k == Enum.KeyCode.ButtonR2 then
			akcja("zryw")
		elseif k == Enum.KeyCode.ButtonX then
			akcja("umiejetnosc")
		elseif k == Enum.KeyCode.ButtonY then
			akcja("ewoluuj")
		elseif k == Enum.KeyCode.ButtonSelect then
			pokazPanel(not panel.Visible)
		end
		return
	end
	if przetworzone then
		return
	end
	local k = wej.KeyCode
	if k == Enum.KeyCode.Space then
		akcja("gryz")
		return
	elseif k == Enum.KeyCode.LeftShift then
		akcja("zryw")
		return
	elseif k == Enum.KeyCode.E or k == Enum.KeyCode.Q then
		akcja("umiejetnosc")
		return
	elseif k == Enum.KeyCode.F or k == Enum.KeyCode.Return then
		akcja("ewoluuj")
		return
	elseif k == Enum.KeyCode.Tab or k == Enum.KeyCode.B then
		pokazPanel(not panel.Visible)
		return
	end
	if wej.UserInputType == Enum.UserInputType.MouseButton1 and not panel.Visible then
		akcja("gryz")
		return
	end
	if wej.UserInputType == Enum.UserInputType.Touch then
		local p = Vector2.new(wej.Position.X, wej.Position.Y)
		if p.X < kamera.ViewportSize.X * 0.55 and not panel.Visible then
			dotykDrazka = wej
			drazekSrodek = p
			local inset = GuiService:GetGuiInset()
			local q = doEkranu(p + Vector2.new(0, inset.Y))
			drazek.Position = UDim2.fromOffset(q.X, q.Y)
			drazek.Visible = true
		end
	end
end)
UserInputService.InputEnded:Connect(function(wej: InputObject)
	if wej == dotykDrazka then
		dotykDrazka = nil
		drazek.Visible = false
	end
end)

------------------------------------------------------------------ rysowanie potworów (ruch proceduralny)
local function wWidoku(p: Vector3, r: number): boolean
	local v, na = kamera:WorldToViewportPoint(p)
	if not na then
		return false
	end
	local m = 80 + r * 10
	local vs = kamera.ViewportSize
	return v.X > -m and v.Y > -m and v.X < vs.X + m and v.Y < vs.Y + m
end

local CZERWONY, ZIELONY, BIALY, MOJ = hex(UI.kolory.zje_cie), hex(UI.kolory.zjesz), Color3.fromRGB(235, 235, 235), hex(UI.kolory.ty)
local nrKlatki = 0

local function rysuj(w, dt: number)
	local moj = w.id == mojId
	local F = D.formy[w.forma]
	local r = F.r
	-- pozycja: własny z przewidywania, cudzy wygładzany do migawki
	local ox, oz = w.x, w.z
	if moj and predOK then
		w.x, w.z = predX, predZ
	else
		local a = 1 - math.exp(-dt * 14)
		local dx, dz = w.tx - w.x, w.tz - w.z
		if dx * dx + dz * dz > 900 then
			w.x, w.z = w.tx, w.tz
		else
			w.x += dx * a
			w.z += dz * a
		end
	end
	local sp = math.sqrt((w.x - ox) ^ 2 + (w.z - oz) ^ 2) / math.max(dt, 1 / 240)
	w.v += (sp - w.v) * math.min(1, dt * 10)
	local dk = (w.tkier - w.kier + math.pi) % (2 * math.pi) - math.pi
	local obrot = dk * math.min(1, dt * 12)
	w.kier += obrot
	w.skret += ((obrot / math.max(dt, 1 / 240)) - w.skret) * math.min(1, dt * 8)
	local widac = not w.martwy and bit32.band(w.flagi, 8) == 0
	-- kokon i tarcza
	local kokon = bit32.band(w.flagi, 8) ~= 0 and not w.martwy
	if kokon then
		local s = r * 2.4 * (1 + math.sin(tGlob * 9) * 0.05)
		w.kokon.Size = Vector3.one * s
		w.kokon.CFrame = CFrame.new(C + Vector3.new(w.x, r * 1.1, w.z))
		w.kokon.Transparency = 0.05
		w.kokon.Color = Color3.fromHSV((tGlob * 0.4) % 1, 0.25, 1)
	elseif w.kokon.Transparency < 1 then
		w.kokon.Transparency = 1
	end
	local tarcza = bit32.band(w.flagi, 1) ~= 0 and widac
	if tarcza then
		w.tarcza.Size = Vector3.one * r * 2.8
		w.tarcza.CFrame = CFrame.new(C + Vector3.new(w.x, r * 0.9, w.z))
		w.tarcza.Transparency = 0.15
	elseif w.tarcza.Transparency < 1 then
		w.tarcza.Transparency = 1
	end
	ustawPrzezroczystosc(w, if widac then 0 else 1)
	-- krążek: zielony zjesz, czerwony zje ciebie, biały ani to, ani to
	w.krazek.Size = Vector3.new(0.15, r * 2 + 0.8, r * 2 + 0.8)
	w.krazek.CFrame = CFrame.new(C + Vector3.new(w.x, 0.14, w.z)) * CFrame.Angles(0, 0, math.pi / 2)
	w.krazek.Transparency = if widac or kokon then (if moj then 0.1 else 0.3) else 1
	if moj then
		w.krazek.Color = MOJ
	else
		local mf = mojaForma()
		local jem = mf >= w.forma + 1 and not (w.slot > 0 and w.forma <= D.smierc.chronione_formy)
		local jedza = w.forma >= mf + 1 and not (w.slot > 0 and mf <= D.smierc.chronione_formy)
		w.krazek.Color = if jem then ZIELONY elseif jedza then CZERWONY else BIALY
	end
	if not widac then
		return
	end
	local poz = C + Vector3.new(w.x, 0, w.z)
	-- daleko poza kadrem: rzadziej (oszczędność na telefonie)
	if not moj and not wWidoku(poz + Vector3.new(0, r, 0), r) and (nrKlatki + w.id) % 6 ~= 0 then
		return
	end
	-- ruch proceduralny
	local vNom = math.max(4, L.predkosc(D, { slot = w.slot, forma = w.forma, poziomy = { szybkosc = 1 } }))
	local mv = math.clamp(w.v / vNom, 0, 1.3)
	w.faza += dt * (2.5 + 11 * mv) / (0.75 + r * 0.09)
	local s = math.abs(math.sin(w.faza))
	local hop = s * r * 0.28 * mv
	local sy = 1 + 0.07 * mv * s - 0.13 * mv * (1 - s) ^ 3 + math.sin(tGlob * 2.3 + w.id) * 0.025 * (1 - math.min(1, mv))
	local pochyl = 0.16 * math.min(1, mv)
	local kiw = math.sin(w.faza) * 0.09 * mv + math.clamp(-w.skret * 0.07, -0.32, 0.32) * math.min(1, mv + 0.3)
	local naprzod = 0
	-- wypad przy gryzieniu
	if w.gryzT < 0.3 then
		w.gryzT += dt
		local k = math.sin(math.clamp(w.gryzT / 0.3, 0, 1) * math.pi)
		naprzod += r * 0.5 * k
		pochyl += 0.4 * k
		sy -= 0.1 * k
	end
	-- puls po zjedzeniu
	local puls = 1
	if w.pulsT < 0.35 then
		w.pulsT += dt
		puls = 1 + math.sin(math.clamp(w.pulsT / 0.35, 0, 1) * math.pi) * w.pulsSila
	end
	-- ogłuszony: chwieje się
	if bit32.band(w.flagi, 16) ~= 0 then
		kiw += math.sin(tGlob * 22) * 0.18
		hop = 0
	end
	-- skok (POUNCE): łuk
	local wysSkoku = 0
	if bit32.band(w.flagi, 32) ~= 0 then
		w.skokT += dt
		wysSkoku = math.sin(math.clamp(w.skokT / 0.55, 0, 1) * math.pi) * (6 + r)
		pochyl += 0.25
	end
	local sxz = 1 / math.sqrt(math.max(0.5, sy))
	local base = CFrame.new(poz + Vector3.new(math.sin(w.kier) * naprzod, hop + wysSkoku + 0.1, math.cos(w.kier) * naprzod))
		* CFrame.Angles(0, w.kier + math.pi, 0) * CFrame.Angles(-pochyl, 0, kiw) -- przód modeli to −Z (układ rigów Pet Areny)
	local skx, sky = sxz * puls, sy * puls
	local cf = w.cf
	for i, o in w.offs do
		local p = w.poz[i]
		cf[i] = base * CFrame.new(p.X * skx, p.Y * sky, p.Z * skx) * o
	end
	workspace:BulkMoveTo(w.czesci, cf, Enum.BulkMoveMode.FireCFrameChanged)
	if w.id == olbrzymId then
		korona.Parent = lokalne
		pcall(function()
			korona:ScaleTo(math.max(0.6, r / 3))
		end)
		korona:PivotTo(CFrame.new(poz + Vector3.new(0, F.model_h * r / F.model_r + 3 + hop, 0)) * CFrame.Angles(0, tGlob * 2, 0))
	end
end

------------------------------------------------------------------ drabina, legowisko, HUD
local function odswiezDrabine()
	local mf = gracz:GetAttribute("EW_MaxForma") or 1
	local f0 = mojaForma()
	local stan = {}
	for f = 1, NF do
		local S = szczeble[f]
		local zdobyta = f <= mf
		local nastepna = f == mf + 1
		S.vf.Visible = zdobyta or nastepna or f == NF
		S.znak.Visible = not S.vf.Visible
		sylwetka(S.vf, not zdobyta)
		S.ramka.BackgroundColor3 = if zdobyta then hex("4A3A5A") else hex("2A2236")
		S.obrys.Color = if f == f0 then hex(UI.kolory.ty) elseif zdobyta then hex("9BFFB8") elseif nastepna then papier else hex("6A5A7A")
		S.obrys.Thickness = if f == f0 then 3 else 2
		table.insert(stan, if zdobyta then "Z" elseif nastepna then "N" elseif f == NF then "C" else "?")
		local T = trofea[f]
		T.vf.Visible = zdobyta
		T.znak.Visible = not zdobyta
		T.ramka.BackgroundColor3 = if zdobyta then hex("4A3A5A") else hex("2F263C")
		T.obrys.Color = if zdobyta then zloto else hex("5A4A6A")
		T.stawka.TextColor3 = if zdobyta then zloto else hex("8A7A9A")
	end
	-- strzałka przy obecnej formie
	local y = if f0 == NF then 14 else 52 + (NF - 1 - f0) * 29 + 2
	strzalkaDrabiny.Position = UDim2.fromOffset(0, y)
	gracz:SetAttribute("EW_K_Drabina", table.concat(stan))
end

local function opisWartosci(U, p: number): string
	local function w(i: number): string
		if U.id == "szczeka" then
			return string.format("%.1f", U.zasieg[i])
		elseif U.id == "apetyt" then
			return string.format("x%.2f", U.wartosci[i])
		end
		return tostring(U.wartosci[i])
	end
	if p > #U.ceny then
		return w(p)
	end
	return w(p) .. " > " .. w(p + 1)
end

local function odswiezPanel()
	local zl = gracz:GetAttribute("EW_Zloto") or 0
	panelStawka.Text = string.format(UI.na_s, gracz:GetAttribute("EW_ZlotoNaS") or 0) .. " gold"
	for id, k in karty do
		local p = gracz:GetAttribute("EW_Poz_" .. id) or 1
		for i, kr in k.kropki do
			kr.BackgroundColor3 = if i <= p then hex("9BFFB8") else hex("5A4A6A")
		end
		k.wart.Text = opisWartosci(k.U, p)
		local cena = k.U.ceny[p]
		if not cena then
			k.napis.Text = UI.maks
			k.przycisk.BackgroundColor3 = hex("6A5A7A")
			k.przycisk.AutoButtonColor = false
		else
			k.napis.Text = UI.kup .. " " .. tostring(cena)
			k.przycisk.BackgroundColor3 = if zl >= cena then hex("3DB36B") else hex("6A5A7A")
			k.przycisk.AutoButtonColor = zl >= cena
		end
	end
end

local function odswiezHUD()
	local f = mojaForma()
	local wz = gracz:GetAttribute("EW_Wzrost") or 0
	local pt = gracz:GetAttribute("EW_Potrzeba") or 1
	local w = widoki[mojId]
	local wForma = if w then w.forma else f
	nazwaFormy.Text = D.formy[wForma].nazwa
	if f >= NF then
		pasekW.Size = UDim2.fromScale(1, 1)
		pasekW.BackgroundColor3 = zloto
		pasekNapis.Text = UI.maks
	else
		local q = math.clamp(wz / math.max(1, pt), 0, 1)
		pasekW.Size = UDim2.fromScale(q, 1)
		pasekW.BackgroundColor3 = if q >= 1 then hex("C27BFF") else hex("6BD66B")
		pasekNapis.Text = if q >= 1 then UI.pelny else string.format("%d / %d", wz, pt)
	end
	local pelny = f < NF and wz >= pt and not (w and serwerSteruje(w.flagi))
	ramkaEwo.Visible = pelny
	zlotoNapis.Text = tostring(gracz:GetAttribute("EW_Zloto") or 0)
	naSNapis.Text = UI.legowisko .. "  " .. string.format(UI.na_s, gracz:GetAttribute("EW_ZlotoNaS") or 0)
	local A = D.formy[wForma].um
	napisUm.Text = A.nazwa
	local teraz = os.clock()
	cienZryw.Size = UDim2.fromScale(1, math.clamp((zrywGotowy - teraz) / D.ruch.zryw_odnowa_s, 0, 1))
	cienUm.Size = UDim2.fromScale(1, math.clamp((umGotowy - teraz) / A.odnowa_s, 0, 1))
	cienGryz.Size = UDim2.fromScale(1, math.clamp((gryzGotowy - teraz) / 0.7, 0, 1))
	-- podpowiedź: na start (do 5 kulek) i przy pełnym pasku
	if pelny then
		podpNapis.Text = UI.podpowiedz_ewo
		ramkaPodp.Visible = true
	else
		podpNapis.Text = UI.podpowiedz_start
		ramkaPodp.Visible = kulekZjedzonych < 5 and (gracz:GetAttribute("EW_MaxForma") or 1) == 1
	end
	if panel.Visible then
		odswiezPanel()
	end
end
for _, n in { "EW_Forma", "EW_MaxForma", "EW_Poz_szczeka", "EW_Poz_szybkosc", "EW_Poz_apetyt" } do
	gracz:GetAttributeChangedSignal(n):Connect(odswiezDrabine)
end
gracz:GetAttributeChangedSignal("EW_Byt"):Connect(function()
	mojId = gracz:GetAttribute("EW_Byt") or 0
	predOK = false
end)
mojId = gracz:GetAttribute("EW_Byt") or 0

------------------------------------------------------------------ strzałka do kulek (pierwsze sekundy)
local strzalka = Instance.new("Part")
strzalka.Name = "Strzalka"
strzalka.Shape = Enum.PartType.Block
strzalka.Anchored = true
strzalka.CanCollide = false
strzalka.CanQuery = false
strzalka.CanTouch = false
strzalka.CastShadow = false
strzalka.Material = Enum.Material.Neon
strzalka.Color = hex(UI.kolory.ty)
strzalka.Size = Vector3.new(0.8, 0.2, 3)
strzalka.Parent = lokalne
local grot = strzalka:Clone()
grot.Size = Vector3.new(2.2, 0.2, 1.2)
grot.Parent = lokalne

local function krokStrzalki()
	local w = widoki[mojId]
	local pokaz = w and kulekZjedzonych < 5 and (gracz:GetAttribute("EW_MaxForma") or 1) == 1 and not w.martwy
	if not pokaz then
		strzalka.Transparency, grot.Transparency = 1, 1
		return
	end
	local best, bd = nil, math.huge
	for i, p in D.kulkiPoz do
		if kulkiZywe[i] then
			local d = (p[1] - w.x) ^ 2 + (p[2] - w.z) ^ 2
			if d < bd and d > 4 then
				best, bd = p, d
			end
		end
	end
	if not best then
		return
	end
	local kier = Vector3.new(best[1] - w.x, 0, best[2] - w.z).Unit
	local r = D.formy[w.forma].r
	local od = C + Vector3.new(w.x, 0.35, w.z) + kier * (r + 2.5 + math.sin(tGlob * 6) * 0.5)
	strzalka.CFrame = CFrame.lookAt(od, od + kier)
	grot.CFrame = CFrame.lookAt(od + kier * 2, od + kier * 3) * CFrame.Angles(0, math.rad(45), 0)
	strzalka.Transparency, grot.Transparency = 0.1, 0.1
end

------------------------------------------------------------------ odsłona nowej formy (kokon → wybuch → tabliczka)
local function tabliczka(f: number, nowa: boolean)
	local F = D.formy[f]
	tablGora.Text = if nowa then UI.nowa_forma else UI.znowu
	tablNazwa.Text = F.nazwa
	tablDol.Text = string.format(UI.zdolnosc, F.um.nazwa)
	tablDol2.Text = if nowa then string.format(UI.trofeum_toast, F.trofeum) else ""
	ramkaTabl.Visible = true
	tablSkala.Scale = 0.3
end

------------------------------------------------------------------ zdarzenia
evZdarzenia.OnClientEvent:Connect(function(lista)
	if type(lista) ~= "table" then
		return
	end
	for _, z in lista do
		if type(z) ~= "table" then
			continue
		end
		local t = z.t
		if t == "kulka" then
			if z.id == mojId then
				kulekZjedzonych += 1
				if not pierwszaKulka then
					pierwszaKulka = os.clock() - tStartu
					gracz:SetAttribute("EW_K_Pierwsza", pierwszaKulka)
				end
				local k = kulkiCzesci[z.i]
				if k then
					k.Transparency = 1
					kulkiZywe[z.i] = false
					E:iskry(k.Position, k.Color, 4, 0.5)
				end
				dzwiek("klik", 1.5 + math.random() * 0.3)
				local w = widoki[mojId]
				if w then
					w.pulsT, w.pulsSila = 0, 0.06
				end
			end
		elseif t == "zjedz" then
			local p = C + Vector3.new(z.x, 2, z.z)
			local b = widoki[z.b]
			if b then
				b.martwy = true
			end
			if z.a == mojId then
				liczZjadl += 1
				dzwiek("plusk", 0.9)
				E:slowo(p + Vector3.new(0, 4, 0), UI.zjedzony, hex(UI.kolory.ty), 0.9, 0.7)
				E:liczba(p + Vector3.new(0, 6, 0), "+" .. tostring(z.zysk), hex("9BFFB8"))
				E:iskry(p, Color3.new(1, 1, 1), 12, 1)
				local w = widoki[mojId]
				if w then
					w.pulsT, w.pulsSila = 0, 0.12
				end
				wstrzasnij(0.35, 0.2)
			elseif z.b == mojId then
				liczZjedzen += 1
				dzwiek("ko", 0.8)
				pokazBaner(UI.zjadl_cie, hex("FF6A6A"), 1.8)
				local nf = math.max(1, z.f - 1)
				toast(string.format(UI.spadasz, D.formy[nf].nazwa), 2.5)
				E:iskry(p, hex("FF8AB0"), 24, 1.6)
				wstrzasnij(1.2, 0.4)
			else
				E:iskry(p, Color3.new(1, 1, 1), 6, 0.6)
			end
			local a = widoki[z.a]
			if a and z.jak == "jezyk" then
				E:jezyk(C + Vector3.new(a.x, D.formy[a.forma].r, a.z), p)
			end
		elseif t == "gryz" then
			local w = widoki[z.id]
			if w and z.id ~= mojId then
				w.gryzT = 0
			end
		elseif t == "odbicie" then
			if z.a == mojId or z.b == mojId then
				dzwiek("cios", 1.1)
				E:pyl(C + Vector3.new(z.x, 0.5, z.z), 3, 6)
				wstrzasnij(0.2, 0.12)
			end
		elseif t == "kokon" then
			local w = widoki[z.id]
			if w then
				w.flagi = bit32.bor(w.flagi, 8)
			end
			if z.id == mojId then
				odslona = { t = 0, czas = z.czas, nowa = z.nowa, forma = z.forma, faza = "kokon" }
				dzwiek("wyklucie", 0.8)
				wstrzasnij(0.3, z.czas)
				ramkaEwo.Visible = false
			end
		elseif t == "ewolucja" then
			local w = widoki[z.id]
			if w then
				w.flagi = bit32.band(w.flagi, 255 - 8)
				if w.forma ~= z.forma then
					zbudujModel(w, z.forma)
				end
				w.pulsT, w.pulsSila = 0, 0.12
				local p = C + Vector3.new(w.x, 2, w.z)
				E:iskry(p + Vector3.new(0, D.formy[z.forma].r, 0), Color3.new(1, 1, 1), if z.id == mojId then 30 else 10, 2)
				E:pierscien(C + Vector3.new(w.x, 0.3, w.z), D.formy[z.forma].r * 2.5, hex("C27BFF"), 0.7)
			end
			if z.id == mojId then
				liczOdslon += 1
				dzwiek("krol", 1)
				wstrzasnij(1.0, 0.4)
				tabliczka(z.forma, z.nowa)
				odslona = { t = 0, czas = D.ewolucja.tabliczka_s, nowa = z.nowa, forma = z.forma, faza = "tabliczka" }
				if z.nowa then
					task.delay(D.ewolucja.tabliczka_s, function()
						toast(string.format(UI.trofeum_toast, D.formy[z.forma].trofeum), 3)
						dzwiek("monety", 1)
					end)
				end
				umGotowy = 0
				odswiezDrabine()
				gracz:SetAttribute("EW_K_Odslon", liczOdslon)
			end
		elseif t == "olbrzym" then
			if z.id == mojId then
				pokazBaner(UI.olbrzym, zloto, 2)
				dzwiek("boss", 1)
			end
		elseif t == "ogloszenie" then
			pokazBaner(z.tekst, zloto, 2.6)
		elseif t == "umiejetnosc" then
			local w = widoki[z.id]
			local p = C + Vector3.new(z.x, 0.4, z.z)
			if z.typ == "wsysanie" then
				E:pierscien(p, z.r, hex(UI.kolory.kulka_mala), 0.4)
			elseif z.typ == "ogluszenie" then
				E:chmura(p + Vector3.new(0, 1.5, 0), z.r)
			elseif z.typ == "fala" then
				E:fala(p, z.r)
				E:pierscien(p, z.r, hex("FFE6A0"), 0.5)
				if z.id == mojId then
					wstrzasnij(1.0, 0.35)
				end
			elseif z.typ == "szarza" and w then
				E:pyl(p, D.formy[w.forma].r, 8)
			end
			if w then
				w.gryzT = 0
			end
			if z.id == mojId then
				dzwiek("umiejetnosc", 1)
			end
		elseif t == "ladowanie" then
			E:fala(C + Vector3.new(z.x, 0.3, z.z), z.r)
			if z.id == mojId then
				wstrzasnij(0.8, 0.3)
				dzwiek("cios", 0.7)
			end
		elseif t == "ogluszony" then
			if z.id == mojId then
				pokazBaner("STUNNED!", hex("C8B8FF"), 1)
			end
		elseif t == "odrodzenie" then
			if z.id == mojId then
				predOK = false
				dzwiek("klik", 0.7)
			end
		elseif t == "korekta" then
			-- serwer nie przyjął pozycji: wracamy do niego
			liczKorekt += 1
			predX, predZ = z.x, z.z
			predVX, predVZ = 0, 0
		elseif t == "kup" then
			if z.ok then
				local U = L.ulepszenie(D, z.id)
				pokazBaner(string.format(UI.kupiono, U and U.nazwa or ""), hex("9BFFB8"), 1.2)
				dzwiek("monety", 1.2)
			elseif z.powod == "zloto" then
				local cena = L.cena(D, ja(), z.id)
				toast(string.format(UI.za_malo, cena or 0), 1.6)
			end
			odswiezPanel()
		end
	end
end)

------------------------------------------------------------------ autopilot prób (EW_TestAuto): jak gracz, który widzi pole
local doAuto = 0
local function krokAutopilota(dt: number)
	if not gracz:GetAttribute("EW_TestAuto") then
		return
	end
	doAuto -= dt
	if doAuto > 0 then
		return
	end
	doAuto = 0.2
	local w = widoki[mojId]
	if not w or w.martwy then
		return
	end
	local mf = w.forma
	local r = D.formy[mf].r
	local zagr, dz, cel, bw = nil, math.huge, nil, 0
	for id, q in widoki do
		if id ~= mojId and not q.martwy then
			local d = math.sqrt((q.x - w.x) ^ 2 + (q.z - w.z) ^ 2)
			local jedza = q.forma >= mf + 1 and not (q.slot > 0 and mf <= D.smierc.chronione_formy)
			local jem = mf >= q.forma + 1 and bit32.band(q.flagi, 1) == 0
			if jedza and d < D.formy[q.forma].r + r + 16 and d < dz then
				zagr, dz = q, d
			elseif jem and d < 44 then
				local wart = D.jedzenie.za_forme[q.forma] / (d + 6)
				if wart > bw then
					cel, bw = { x = q.x, z = q.z, d = d, byt = q }, wart
				end
			end
		end
	end
	for i, p in D.kulkiPoz do
		if kulkiZywe[i] then
			local d = math.sqrt((p[1] - w.x) ^ 2 + (p[2] - w.z) ^ 2)
			if d < 40 then
				local wart = (if p[3] == 2 then D.jedzenie.duza else D.jedzenie.mala) / (d + 6)
				if wart > bw then
					cel, bw = { x = p[1], z = p[2], d = d }, wart
				end
			end
		end
	end
	local kx, kz = 0, 0
	if zagr and bit32.band(w.flagi, 1) == 0 then
		local d = math.max(0.1, dz)
		kx, kz = (w.x - zagr.x) / d - w.x / D.pole.r * 0.6, (w.z - zagr.z) / d - w.z / D.pole.r * 0.6
		if dz < D.formy[zagr.forma].r + r + 4 then
			akcja("zryw")
		end
	elseif cel then
		local d = math.max(0.1, cel.d)
		kx, kz = (cel.x - w.x) / d, (cel.z - w.z) / d
		if cel.byt and d < r + L.zasiegGryzu(D, ja()) + D.formy[cel.byt.forma].r * 0.5 then
			akcja("gryz")
		end
		if cel.byt and d < 16 then
			akcja("umiejetnosc")
		end
	else
		kx, kz = -w.x / D.pole.r, -w.z / D.pole.r + 0.3
	end
	local n = math.max(0.01, math.sqrt(kx * kx + kz * kz))
	-- świat → drążek: prawo = −x, góra = +z
	sterTest = { v = Vector2.new(-kx / n, kz / n), do_ = os.clock() + 0.4 }
	if gracz:GetAttribute("EW_TestAutoEvo") and (gracz:GetAttribute("EW_Wzrost") or 0) >= (gracz:GetAttribute("EW_Potrzeba") or 1) then
		akcja("ewoluuj")
	end
end

------------------------------------------------------------------ układ ekranu (próby): prostokąty i nakładanie
local function uklad(): string
	local nazwy = { Wzrost = ramkaWzrostu, Zloto = ramkaZlota, Drabina = ramkaDrabiny, Gryz = ramkaGryz, Zryw = ramkaZryw,
		Umiejetnosc = ramkaUm, Ewolucja = ramkaEwo, Podpowiedz = ramkaPodp, Toast = ramkaToastu, Tabliczka = ramkaTabl, Panel = panel }
	local pr = {}
	local v = kamera.ViewportSize
	local ins = GuiService:GetGuiInset() -- przy IgnoreGuiInset AbsolutePosition liczy się od dołu górnego paska
	for n, f in nazwy do
		if f.Visible then
			local p, s = f.AbsolutePosition + ins, f.AbsoluteSize
			pr[n] = { p.X, p.Y, p.X + s.X, p.Y + s.Y }
		end
	end
	local naklad, poza = {}, {}
	for a, A in pr do
		if A[1] < -1 or A[2] < -1 or A[3] > v.X + 1 or A[4] > v.Y + 1 then
			table.insert(poza, a)
		end
		for b, B in pr do
			if a < b and a ~= "Panel" and b ~= "Panel" and a ~= "Tabliczka" and b ~= "Tabliczka" then
				local w = math.min(A[3], B[3]) - math.max(A[1], B[1])
				local h = math.min(A[4], B[4]) - math.max(A[2], B[2])
				if w > 2 and h > 2 then
					table.insert(naklad, a .. "+" .. b)
				end
			end
		end
	end
	local male = {}
	for _, b in { bGryz, bZryw, bUm, bEwo, bLegowisko, bZamknij } do
		if b.Visible and b:FindFirstAncestorWhichIsA("GuiObject").Visible then
			local s = b.AbsoluteSize
			if s.X < 44 or s.Y < 44 then
				table.insert(male, b.Name)
			end
		end
	end
	local gora = {}
	for n, A in pr do
		if A[2] < ins.Y and (A[1] < 120 or A[3] > v.X - 120) then
			table.insert(gora, n) -- róg górnego paska Roblox (menu, czat)
		end
	end
	return HttpService:JSONEncode({ okno = { v.X, v.Y }, prostokaty = pr, nakladanie = naklad, poza = poza, male = male, skala = skalaEkranu(),
		inset = ins.Y, rogi_paska = gora })
end

------------------------------------------------------------------ kamera
local camCF: CFrame? = nil
local odlKam = 0
local function celKamery(dt: number): CFrame?
	local w = widoki[mojId]
	if not w then
		return nil
	end
	local f = w.forma
	if odslona and odslona.faza == "kokon" then
		f = odslona.forma
	end
	local K = D.kamera
	local d = K.wys + D.formy[f].r * K.na_r
	if odslona then
		d *= K.kokon_x
	end
	odlKam = if odlKam == 0 then d else odlKam + (d - odlKam) * math.min(1, dt * (if odslona then 1.8 else 2.5))
	local e = math.rad(K.nachylenie_st)
	local cel = C + Vector3.new(w.x, 0, w.z)
	return CFrame.lookAt(cel + Vector3.new(0, odlKam * math.sin(e), -odlKam * math.cos(e)), cel)
end

------------------------------------------------------------------ pętla
odswiezDrabine()
local klatek, suma, okno = 0, 0, 0
local doHUD = 0
RunService.RenderStepped:Connect(function(dt: number)
	tGlob += dt
	nrKlatki += 1
	-- próby: wejście jak z palca (atrybuty lokalnego gracza)
	local ts = gracz:GetAttribute("EW_TestSter")
	if typeof(ts) == "Vector3" then
		sterTest = { v = Vector2.new(ts.X, ts.Y), do_ = os.clock() + ts.Z }
		gracz:SetAttribute("EW_TestSter", nil)
	end
	local tp = gracz:GetAttribute("EW_TestPrzycisk")
	if type(tp) == "string" then
		gracz:SetAttribute("EW_TestPrzycisk", nil)
		if tp == "legowisko" then
			pokazPanel(true)
		elseif tp == "zamknij" then
			pokazPanel(false)
		elseif string.sub(tp, 1, 4) == "kup:" then
			akcja("kup", string.sub(tp, 5))
		else
			akcja(tp)
		end
	end
	if gracz:GetAttribute("EW_TestUklad") then
		gracz:SetAttribute("EW_TestUklad", nil)
		gracz:SetAttribute("EW_K_Uklad", uklad())
	end
	krokAutopilota(dt)
	krokSterowania(dt)
	for _, w in widoki do
		rysuj(w, dt)
	end
	if olbrzymId == 0 or not widoki[olbrzymId] then
		korona.Parent = nil
	end
	-- kulki: lekkie unoszenie (jedno BulkMoveTo)
	local cz, cf = {}, {}
	for i, k in kulkiCzesci do
		if kulkiZywe[i] then
			table.insert(cz, k)
			table.insert(cf, kulkiCF[i] + Vector3.new(0, math.sin(tGlob * 3 + i) * 0.25, 0))
		end
	end
	workspace:BulkMoveTo(cz, cf, Enum.BulkMoveMode.FireCFrameChanged)
	krokStrzalki()
	-- odsłona: tabliczka rośnie i znika
	if odslona then
		odslona.t += dt
		if odslona.faza == "tabliczka" then
			local t = odslona.t
			tablSkala.Scale = if t < 0.15 then 0.3 + t / 0.15 * 0.9 elseif t < 0.27 then 1.2 - (t - 0.15) / 0.12 * 0.2 else 1
			if t > odslona.czas then
				ramkaTabl.Visible = false
				odslona = nil
			end
		elseif odslona.t > odslona.czas + 2 then
			odslona = nil
		end
	end
	if ramkaEwo.Visible then
		skalaEwo.Scale = 1 + math.sin(tGlob * 6) * 0.06
		obrysEwo.Color = Color3.fromHSV((tGlob * 0.5) % 1, 0.5, 1)
	end
	if baner.Visible then
		banerT += dt
		banerSkala.Scale = if banerT < 0.1 then 0.4 + banerT / 0.1 * 0.8 elseif banerT < 0.2 then 1.2 - (banerT - 0.1) / 0.1 * 0.2 else 1
		if banerT > banerDo then
			baner.Visible = false
		end
	end
	if ramkaToastu.Visible and os.clock() > toastDo then
		ramkaToastu.Visible = false
	end
	doHUD -= dt
	if doHUD <= 0 then
		doHUD = 0.1
		odswiezHUD()
	end
	E:krok(dt)
	local cel = celKamery(dt)
	if cel then
		kamera.CameraType = Enum.CameraType.Scriptable
		kamera.FieldOfView = D.kamera.fov
		camCF = if camCF then camCF:Lerp(cel, 1 - math.exp(-dt * 10)) else cel
		local wynik = camCF :: CFrame
		if os.clock() < wstrzas.do_ then
			local s = wstrzas.sila * math.clamp((wstrzas.do_ - os.clock()) / 0.3, 0, 1)
			wynik *= CFrame.new(math.noise(tGlob * 25, 1) * s, math.noise(tGlob * 25, 2) * s, 0)
		else
			wstrzas.sila = 0
		end
		kamera.CFrame = wynik
	end
	-- pomiar dla prób
	klatek += 1
	suma += dt
	okno += dt
	if okno >= 1 then
		gracz:SetAttribute("EW_K_Klatka", suma / klatek * 1000)
		local n = 0
		for _ in widoki do
			n += 1
		end
		gracz:SetAttribute("EW_K_Widokow", n)
		gracz:SetAttribute("EW_K_Korekty", liczKorekt)
		gracz:SetAttribute("EW_K_Snapy", liczSnapow)
		gracz:SetAttribute("EW_K_BladMaks", bladMaks)
		gracz:SetAttribute("EW_K_Gryzy", liczGryzow)
		gracz:SetAttribute("EW_K_Zjedzony", liczZjedzen)
		gracz:SetAttribute("EW_K_Zjadl", liczZjadl)
		gracz:SetAttribute("EW_K_Legowisko", panel.Visible)
		gracz:SetAttribute("EW_K_KameraY", kamera.CFrame.Position.Y)
		gracz:SetAttribute("EW_K_MigawkaS", os.clock() - czasMigawki)
		local w = widoki[mojId]
		if w then
			gracz:SetAttribute("EW_K_MojX", w.x)
			gracz:SetAttribute("EW_K_MojZ", w.z)
		end
		bladMaks = 0
		klatek, suma, okno = 0, 0, 0
	end
end)
-- szybki odczyt pozycji dla próby opóźnienia (co klatkę, tylko gdy próba prosi)
RunService.Heartbeat:Connect(function()
	if gracz:GetAttribute("EW_TestPoz") then
		local w = widoki[mojId]
		if w then
			gracz:SetAttribute("EW_K_PozX", w.x)
			gracz:SetAttribute("EW_K_PozZ", w.z)
		end
	end
end)

kontener:SetAttribute("KlientGotowy", true)
