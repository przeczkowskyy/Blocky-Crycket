--[[
	KlientEwolucji — klient Monster Evolution (Script, RunContext Client, w Workspace/EwolucjaGra). Strażnik „tylko Studio”
	na początku (zbuduj.py --publikacja go usuwa) i wyłącznik kontenera.
	Własny potwór przewidywany od razu (ruch, DASH, szarża; serwer przyjmuje pozycję albo poprawia); BITE gra od razu
	(wynik od serwera). Potwory bez szkieletów — ruch proceduralny (krok-podskok, zgniecenie i rozciągnięcie przesunięciem
	części, pochylenie w biegu i w zakrętach, kiwanie, wypad przy gryzieniu), części przesuwane workspace:BulkMoveTo.
	Ekran (telefon najpierw, wzór 667 × 375 pt): pasek wzrostu i życia, złoto + HOARD, drabina z boku, BITE / DASH / FIRE / POWER
	(zamknięte i następne wersje linii jako ciemne sylwetki „at <STADIUM>”), EVOLVE przy pełnym pasku, odsłona nowej formy,
	panel legowiska z ulepszeniami. Walka (walka1): WK.paski życia nad stworkami, liczby ran, błysk trafionego, zatrzymanie
	klatki przy trafieniu, wstrząs według siły, spowolnienie przy zjedzeniu gracza, zamachy widoczne dla wszystkich.
	Efekty zdolności zaczepione w nazwanych punktach modelu (Pysk, Ogon, SkrzydloL/P, Brzuch): Attachment albo Bone o tej
	nazwie w modelu (modele z Blendera), inaczej atrybut modelu Kotwica_<Nazwa>, inaczej zapas z promienia.
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
local function wariantD(id: string?)
	for _, W in D.warianty do
		if W.id == id then
			return W
		end
	end
	return nil
end
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
-- warstwa HUD: rozmiar i odsunięcie od kotwicy w punktach wzoru 667 × 375, skalowane razem (bez nakładania na dużych ekranach)
local function warstwa(nazwa: string, kotwica: Vector2, poz: UDim2, roz: Vector2): Frame
	local sk = skalaEkranu()
	local f = nowy("Frame", { Name = nazwa, AnchorPoint = kotwica, Position = UDim2.new(poz.X.Scale, poz.X.Offset * sk, poz.Y.Scale, poz.Y.Offset * sk),
		Size = UDim2.fromOffset(roz.X, roz.Y), BackgroundTransparency = 1 }, ekran)
	f:SetAttribute("Poz", poz)
	table.insert(skale, nowy("UIScale", { Scale = sk }, f))
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
	local sk = skalaEkranu()
	for _, s in skale do
		s.Scale = sk
		local f = s.Parent
		local poz = f and f:GetAttribute("Poz")
		if typeof(poz) == "UDim2" and f.Name ~= "Drazek" then
			f.Position = UDim2.new(poz.X.Scale, poz.X.Offset * sk, poz.Y.Scale, poz.Y.Offset * sk)
		end
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

local pasekSkala = nowy("UIScale", { Scale = 1 }, pasekTlo)
local pulsPaska = 99

-- pasek bossa (pod paskiem wzrostu, gdy boss blisko)
local ramkaBossa = warstwa("Boss", Vector2.new(0.5, 0), UDim2.new(0.5, -40, 0, 74), Vector2.new(250, 34))
local bossNazwa = napis(ramkaBossa, D.boss.nazwa, UDim2.fromOffset(0, 0), UDim2.new(1, 0, 0, 16), hex("FF9AD8"))
local bossTlo = nowy("Frame", { Position = UDim2.fromOffset(6, 17), Size = UDim2.new(1, -12, 0, 14), BackgroundColor3 = tusz }, ramkaBossa)
rog(bossTlo, 7)
obrys(bossTlo, 2, hex("FF9AD8"))
local bossW = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = hex("FF4D8A"), BorderSizePixel = 0 }, bossTlo)
rog(bossW, 7)
ramkaBossa.Visible = false

-- błysk ekranu przy ewolucji
local blysk = nowy("Frame", { Name = "Blysk", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 1,
	ZIndex = 30, Active = false }, gui)
local blyskT = 99

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
-- FIRE i POWER (walka1): dwie linie zdolności ewoluujące ze stadiami; zamknięta linia — ciemny przycisk z „at <STADIUM>”
-- walka1: stan i przyciski klienta w jednej tabeli (limit 200 zmiennych lokalnych skryptu)
local WK = {}
function WK.przyciskZd(nazwa: string, poz: UDim2, kolor: string, linia: string)
	local ramka = warstwa(nazwa, Vector2.new(1, 1), poz, Vector2.new(68, 68))
	local b, cien, l = przyciskOkragly(ramka, nazwa, "", 68, kolor)
	l.Position = UDim2.fromScale(0.08, 0.34)
	l.Size = UDim2.fromScale(0.84, 0.3)
	local typ = napis(b, if linia == "ogien" then UI.ogien else UI.moc, UDim2.fromScale(0.18, 0.1), UDim2.fromScale(0.64, 0.2), papier, cyfry)
	typ.ZIndex = 3
	local od = napis(b, "", UDim2.fromScale(0.08, 0.66), UDim2.fromScale(0.84, 0.18), hex("D8C8E8"), cyfry)
	od.ZIndex = 3
	return { ramka = ramka, b = b, cien = cien, napis = l, od = od, kolor = hex(kolor), linia = linia }
end
WK.zdOgien = WK.przyciskZd("Ogien", UDim2.new(1, -14, 1, -122), "FF7A2E", "ogien")
WK.zdMoc = WK.przyciskZd("Moc", UDim2.new(1, -110, 1, -110), "4FB3FF", "moc")
-- następna wersja linii: ciemna sylwetka z nazwą i „at <STADIUM>” nad przyciskiem
function WK.pigulka(nazwa: string, poz: UDim2)
	local ramka = warstwa(nazwa, Vector2.new(1, 1), poz, Vector2.new(110, 30))
	local tlo = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.2 }, ramka)
	rog(tlo, 10)
	obrys(tlo, 1.5, hex("6A5A7A"))
	local syl = nowy("Frame", { Position = UDim2.fromOffset(5, 5), Size = UDim2.fromOffset(20, 20), BackgroundColor3 = hex("1B1424") }, tlo)
	rog(syl, 10)
	obrys(syl, 1.5, hex("8A7A9A"))
	napis(syl, "?", UDim2.fromScale(0.15, 0.1), UDim2.fromScale(0.7, 0.8), hex("8A7A9A"))
	local n1 = napis(tlo, "", UDim2.fromOffset(29, 2), UDim2.new(1, -33, 0, 14), hex("B8A8C8"), cyfry)
	local n2 = napis(tlo, "", UDim2.fromOffset(29, 15), UDim2.new(1, -33, 0, 13), papier, cyfry)
	n1.TextXAlignment = Enum.TextXAlignment.Left
	n2.TextXAlignment = Enum.TextXAlignment.Left
	ramka.Visible = false
	return { ramka = ramka, n1 = n1, n2 = n2 }
end
WK.nastOgien = WK.pigulka("OgienNast", UDim2.new(1, -14, 1, -194))
WK.nastMoc = WK.pigulka("MocNast", UDim2.new(1, -130, 1, -182))

-- życie (pod paskiem wzrostu)
WK.ramkaZycia = warstwa("Zycie", Vector2.new(0.5, 0), UDim2.new(0.5, -40, 0, 56), Vector2.new(230, 14))
WK.zycieTlo = nowy("Frame", { Position = UDim2.fromOffset(16, 0), Size = UDim2.new(1, -32, 1, 0), BackgroundColor3 = tusz }, WK.ramkaZycia)
rog(WK.zycieTlo, 7)
obrys(WK.zycieTlo, 2, hex("FF8A8A"))
WK.zycieW = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = hex("6BD66B"), BorderSizePixel = 0 }, WK.zycieTlo)
rog(WK.zycieW, 7)
WK.zycieNapis = napis(WK.zycieTlo, UI.hp, UDim2.fromScale(0.03, 0), UDim2.fromScale(0.16, 1), papier, cyfry)
WK.zycieNapis.ZIndex = 2

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
local ramkaBaneru = warstwa("Baner", Vector2.new(0.5, 0), UDim2.new(0.5, -40, 0, 76), Vector2.new(330, 50))
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

-- zakładki panelu (etap 3): TROPHIES (poziomy trofeów w legowisku, warianty, szanse) i UPGRADES
local tabT = nowy("Frame", { Name = "TabTrofea", Position = UDim2.fromOffset(0, 52), Size = UDim2.new(1, 0, 1, -52), BackgroundTransparency = 1 }, panel)
local tabU = nowy("Frame", { Name = "TabUlepszenia", Position = UDim2.fromOffset(0, 52), Size = UDim2.new(1, 0, 1, -52), BackgroundTransparency = 1,
	Visible = false }, panel)
panelStawka.Visible = false
for _, d in panel:GetChildren() do
	if d:IsA("TextLabel") and d.Text == UI.legowisko_opis then
		d.Visible = false
	end
end
local function zakladka(x: number, tekst: string, tab: Frame)
	local b = nowy("TextButton", { Name = "Zakladka", Position = UDim2.fromOffset(x, 5), Size = UDim2.fromOffset(100, 44), BackgroundColor3 = hex("4A3A5A"),
		Text = "", AutoButtonColor = true }, panel)
	rog(b, 10)
	obrys(b, 2, tusz)
	napis(b, tekst, UDim2.fromScale(0.06, 0.18), UDim2.fromScale(0.88, 0.64))
	b.Activated:Connect(function()
		tabT.Visible = tab == tabT
		tabU.Visible = tab == tabU
	end)
	return b
end
zakladka(196, UI.trofea, tabT)
zakladka(302, UI.ulepszenia, tabU)
for f, T in trofea do
	T.ramka.Parent = tabT
	T.ramka.Position = UDim2.fromOffset(14 + (f - 1) * 56, 2)
	T.ramka.Size = UDim2.fromOffset(50, 144)
	T.poziom = napis(T.ramka, "", UDim2.fromOffset(2, 60), UDim2.fromOffset(46, 14), papier, cyfry)
	T.wariant = napis(T.ramka, "", UDim2.fromOffset(2, 74), UDim2.fromOffset(46, 12), zloto, cyfry)
	T.kup = nowy("TextButton", { Name = "KupPoziom", Position = UDim2.fromOffset(2, 92), Size = UDim2.fromOffset(46, 48), BackgroundColor3 = hex("3DB36B"),
		Text = "", AutoButtonColor = true }, T.ramka)
	rog(T.kup, 10)
	obrys(T.kup, 2, tusz)
	T.kupNapis = napis(T.kup, "", UDim2.fromScale(0.06, 0.12), UDim2.fromScale(0.88, 0.76), papier, cyfry)
end
local szanseNapis = napis(tabT, UI.szanse, UDim2.fromOffset(14, 150), UDim2.new(1, -28, 0, 16), hex("C8B8D8"), cyfry)
local bossTrofNapis = napis(tabT, "", UDim2.fromOffset(14, 170), UDim2.new(1, -28, 0, 16), hex("FF9AD8"), cyfry)
local legInfo = napis(tabT, UI.tylko_w_legowisku, UDim2.fromOffset(14, 190), UDim2.new(1, -28, 0, 16), zloto, cyfry)
for _, k in karty do
	k.ramka.Parent = tabU
	k.ramka.Position = UDim2.new(0, k.ramka.Position.X.Offset, 0, 30)
end

------------------------------------------------------------------ modele: klon, skala, części i przesunięcia (BulkMoveTo)
-- opis modelu: forma z drabiny albo boss lasu — wszystko z danych (wzorzec, skala, chód, opcjonalne animacje)
local function spec(f: number, boss: boolean?)
	if boss then
		local B = D.boss
		return { wzorzec = B.wzorzec, model_r = B.model_r, model_h = B.model_h, r = D.formy[B.forma].r * B.skala, chod = B.chod,
			podskok = B.podskok, pochyl = B.pochyl, krok = B.krok, anim = B.anim }
	end
	return D.formy[f]
end

-- grupy części do ruchu kończyn (z geometrii, według typu chodu): 1–4 nogi, 5 ogon, 6 głowa (przód to −Z)
local function grupy(F, poz)
	local g, pv = {}, {}
	local x0, x1, y0, y1, z0, z1 = math.huge, -math.huge, math.huge, -math.huge, math.huge, -math.huge
	for _, p in poz do
		x0, x1, y0, y1, z0, z1 = math.min(x0, p.X), math.max(x1, p.X), math.min(y0, p.Y), math.max(y1, p.Y), math.min(z0, p.Z), math.max(z1, p.Z)
	end
	local cx, cz, H, Gz = (x0 + x1) / 2, (z0 + z1) / 2, math.max(0.1, y1 - y0), math.max(0.1, z1 - z0)
	local chod = F.chod or "skok"
	local nogi = if chod == "klus" then y0 + 0.32 * H elseif chod == "dwunozny" then y0 + 0.28 * H else -math.huge
	local sumy = {}
	for i, p in poz do
		local k = 0
		if p.Y < nogi then
			if chod == "klus" then
				k = (if p.X < cx then 1 else 2) + (if p.Z < cz then 0 else 2)
			else
				k = if p.X < cx then 1 else 2
			end
		elseif chod == "klus" and p.Z > z1 - 0.2 * Gz and p.Y > nogi then
			k = 5
		elseif p.Z < z0 + 0.3 * Gz and p.Y > y0 + 0.4 * H then
			k = 6
		end
		g[i] = k
		if k > 0 then
			local s = sumy[k] or { z = 0, n = 0 }
			s.z += p.Z
			s.n += 1
			sumy[k] = s
		end
	end
	for k, s in sumy do
		local y = if k <= 4 then nogi elseif k == 5 then y0 + 0.55 * H else y0 + 0.5 * H
		local z = if k == 5 then z1 - 0.2 * Gz elseif k == 6 then z0 + 0.3 * Gz else s.z / s.n
		pv[k] = Vector3.new(cx, y, z)
	end
	return g, pv, (z1 - z0)
end

local function zrobModel(F)
	local wz = wzorce and wzorce:FindFirstChild(F.wzorzec)
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
	-- grupy ruchu z modelu: atrybut części „Grupa” i atrybuty modelu „Pivot<k>” (w skali 1)
	local grupyM, pivotyM = nil, nil
	for i, d in czesci do
		local k = d:GetAttribute("Grupa")
		if k then
			grupyM = grupyM or {}
			grupyM[i] = k
		end
	end
	if grupyM then
		local sk = m:GetScale()
		pivotyM = {}
		for i = 1, #czesci do
			grupyM[i] = grupyM[i] or 0
		end
		for n, v in m:GetAttributes() do
			local k = tonumber(string.match(n, "^Pivot(%d+)$"))
			if k and typeof(v) == "Vector3" then
				pivotyM[k] = v * sk
			end
		end
	end
	-- model ze szkieletem i animacjami w danych: odtwarzane klipy zamiast ruchu części
	local rig = nil
	if F.anim then
		local an = m:FindFirstChildWhichIsA("Animator", true)
		if an then
			rig = {}
			for nazwa, id in F.anim do
				local a = Instance.new("Animation")
				a.AnimationId = "rbxassetid://" .. tostring(id)
				local ok, tr = pcall(function()
					return an:LoadAnimation(a)
				end)
				if ok then
					rig[nazwa] = tr
				end
			end
			if rig.chod then
				rig.chod.Looped = true
				rig.chod:Play()
			end
		end
	end
	return m, czesci, offs, poz, rig, grupyM, pivotyM
end

-- wygląd wariantu (części: kolor i materiał) — ten sam dla potworów graczy i trofeów w legowisku
local function wyglad(m: Instance, W)
	if not W then
		return
	end
	local i = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") and d.Transparency < 1 and d.Name ~= "Oko" then
			i += 1
			if W.id == "tecza" then
				d.Color = Color3.fromHSV((i * 0.137) % 1, 0.65, 1)
				d.Material = if i % 4 == 0 then Enum.Material.Neon else Enum.Material.SmoothPlastic
			elseif W.id == "krysztal" then
				d.Color = d.Color:Lerp(hex(W.kolor), 0.7)
				d.Material = Enum.Material.Glass
				d.Transparency = math.max(d.Transparency, 0.15)
			elseif W.id == "rubin" then
				d.Color = d.Color:Lerp(hex(W.kolor), 0.75)
				d.Material = Enum.Material.Glass
			else
				d.Color = d.Color:Lerp(hex(W.kolor), 0.75)
				d.Material = Enum.Material.Metal
			end
		end
	end
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
WK.liczKorekt, WK.liczSnapow, WK.bladMaks, WK.liczGryzow, WK.liczOdslon, WK.liczZjedzen, WK.liczZjadl = 0, 0, 0, 0, 0, 0, 0
for k, v in { liczRanZad = 0, liczRanOtrz = 0, liczZamachow = 0, liczPociskow = 0, liczPrzewrotow = 0, liczSpowolnien = 0, zwolnienieDo = 0,
	wolnoDo = 0, lancuchK = 0, lancuchDoL = 0, gryzOdnowa = 0.42 } do
	WK[k] = v
end
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
	local wielka = p[3] == 3
	local k = Instance.new("Part")
	k.Name = "Kulka" .. i
	k.Shape = Enum.PartType.Ball
	k.Anchored = true
	k.CanCollide = false
	k.CanQuery = false
	k.CanTouch = false
	k.CastShadow = false
	k.Material = Enum.Material.Neon
	k.Color = if wielka then hex("FFC83D") elseif duza then hex(UI.kolory.kulka_duza) else hex(UI.kolory.kulka_mala)
	k.Size = Vector3.one * (if wielka then D.jedzenie.wielka_r elseif duza then D.jedzenie.duza_r else D.jedzenie.mala_r) * 2
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
-- kulka osiągalna dla mnie (las zamknięty → kulki lasu się nie liczą)
local function osiagalna(p): boolean
	return (gracz:GetAttribute("EW_MaxForma") or 1) >= D.las.od_formy or not L.wLesie(D, p[1], p[2])
end

local function mojSlot(): number
	return gracz:GetAttribute("EW_Slot") or 0
end
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
	w.F = spec(f, w.boss)
	local gM, pM
	w.model, w.czesci, w.offs, w.poz, w.rig, gM, pM = zrobModel(w.F)
	if gM then
		w.grupa, w.pivoty = gM, pM
	else
		w.grupa, w.pivoty, w.dl = grupy(w.F, w.poz)
	end
	wyglad(w.model, D.warianty[w.wariant or 0])
	-- kotwice zdolności z atrybutów modelu (w skali 1; model z Blendera może mieć Attachment o tej nazwie)
	w.kotwice = {}
	local skM = w.model:GetScale()
	for n, v in w.model:GetAttributes() do
		local k = string.match(n, "^Kotwica_(.+)$")
		if k and typeof(v) == "Vector3" then
			w.kotwice[k] = v * skM
		end
	end
	w.skrz = 0
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

local function nowyWidok(id: number, slot: number, f: number, x: number, z: number, boss: boolean?)
	local w = { id = id, slot = slot, x = x, z = z, boss = boss == true, sOst = 1, tx = x, tz = z, kier = 0, tkier = 0, flagi = 0, martwy = false, brak = 0,
		faza = math.random() * 6, v = 0, px = x, pz = z, skret = 0, gryzT = 99, pulsT = 99, pulsSila = 0, skokT = 0,
		krazek = krazek(D.formy[f].r), kokon = kula(Color3.new(1, 1, 1), Enum.Material.Neon, 0.05),
		tarcza = kula(hex("7FE9FF"), Enum.Material.ForceField, 0.2), vx = 0, vz = 0, hp = 1, akcja = 0, ranaT = -99, przewT = 99, spinT = 99,
		lotT = 99, lotCzas = 0.8, lotTyp = "lot", gryzK = 1 }
	zbudujModel(w, f)
	widoki[id] = w
	return w
end

local function usunWidok(w)
	if w.zar then
		w.zar:Destroy()
	end
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
		local o = o0 + (i - 1) * 18
		local id = buffer.readu16(b, o)
		local slot = buffer.readu8(b, o + 2)
		local fl = buffer.readu8(b, o + 3)
		local f = buffer.readu8(b, o + 4)
		local x, z = buffer.readf32(b, o + 5), buffer.readf32(b, o + 9)
		widziane[id] = true
		local w = widoki[id] or nowyWidok(id, slot, f, x, z, bit32.band(fl, 128) ~= 0)
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
		w.hp = buffer.readu8(b, o + 16) / 255
		local ak = buffer.readu8(b, o + 17)
		if bit32.band(ak, 64) ~= 0 and bit32.band(w.akcja, 64) == 0 then
			w.przewT = 0 -- przewrót: bezwładny obrót po ciosie z odrzutem
		end
		w.akcja = ak
		local wr = buffer.readu8(b, o + 15)
		if wr ~= (w.wariant or 0) then
			w.wariant = wr
			zbudujModel(w, w.forma)
		end
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
local zdGotowy = { ogien = 0, moc = 0 }

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
		local cel = L.predkosc(D, ja()) * m * (if teraz < WK.wolnoDo then D.walka.zamach_v else 1)
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
		predX, predZ = L.ogranicz(D, predX, predZ, r, if (gracz:GetAttribute("EW_MaxForma") or 1) >= D.las.od_formy then 3 else 1)
		-- odbicia od wszystkich (jak na serwerze: zjada się tylko przez życie)
		local mf = w.forma
		for id, q in widoki do
			if id ~= mojId and not q.martwy and bit32.band(q.flagi, 8 + 32) == 0 then
				local rq = D.formy[q.forma].r
				local dx, dz = predX - q.x, predZ - q.z
				local d = math.sqrt(dx * dx + dz * dz)
				if d < r + rq and d > 0.01 then
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
		WK.bladMaks = math.max(WK.bladMaks, blad)
		local prog = 6 + cel * 0.5
		if blad > prog * 2.5 then
			predX, predZ = w.tx, w.tz
			WK.liczSnapow += 1
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
		if teraz > WK.lancuchDoL then
			WK.lancuchK = 0
		end
		WK.lancuchK = WK.lancuchK % 3 + 1
		WK.gryzOdnowa = D.walka.lancuch_s[WK.lancuchK]
		gryzGotowy = teraz + WK.gryzOdnowa
		WK.lancuchDoL = gryzGotowy + D.walka.lancuch_reset_s
		WK.liczGryzow += 1
		gracz:SetAttribute("EW_K_Gryzy", WK.liczGryzow)
		if w then
			w.gryzT = 0 -- wypad od razu, wynik przyjdzie z serwera
			w.gryzK = WK.lancuchK
		end
		dzwiek(if WK.lancuchK == 3 then "zlapanie" else "cios", if WK.lancuchK == 3 then 1.15 else 1.45 + WK.lancuchK * 0.12)
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
		akcja("ogien")
	elseif rodzaj == "ogien" or rodzaj == "moc" then
		if not w then
			return
		end
		local A = L.zdolnoscFormy(D, rodzaj, w.forma)
		if not A then
			local N = L.nastepnaZdolnosc(D, rodzaj, w.forma)
			if N then
				toast(N.nazwa .. " " .. string.format(UI.od_stadium, D.formy[N.od].nazwa), 1.6)
			end
			return
		end
		if teraz < zdGotowy[rodzaj] then
			return
		end
		zdGotowy[rodzaj] = teraz + 0.35 -- pełna odnowa po potwierdzeniu (zamach) z serwera
		WK.wolnoDo = teraz + A.zamach_s -- zamach spowalnia jak na serwerze (bez poprawek pozycji)
		evAkcja:FireServer("umiejetnosc", rodzaj)
	elseif rodzaj == "ewoluuj" then
		evAkcja:FireServer("ewoluuj")
		dzwiek("klik", 1.2)
	elseif rodzaj == "kup" then
		evAkcja:FireServer("kup", a)
		dzwiek("klik", 1)
	elseif rodzaj == "kup_trofeum" then
		evAkcja:FireServer("kup_trofeum", a)
		dzwiek("klik", 1.1)
	end
end
bGryz.Activated:Connect(function()
	akcja("gryz")
end)
bZryw.Activated:Connect(function()
	akcja("zryw")
end)
WK.zdOgien.b.Activated:Connect(function()
	akcja("ogien")
end)
WK.zdMoc.b.Activated:Connect(function()
	akcja("moc")
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
for f, T in trofea do
	T.kup.Activated:Connect(function()
		akcja("kup_trofeum", f)
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
			akcja("ogien")
		elseif k == Enum.KeyCode.ButtonR1 or k == Enum.KeyCode.ButtonL1 then
			akcja("moc")
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
	elseif k == Enum.KeyCode.E then
		akcja("ogien")
		return
	elseif k == Enum.KeyCode.Q or k == Enum.KeyCode.R then
		akcja("moc")
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

local function pivotyNazwane(w): boolean
	return w.pivoty ~= nil and w.pivoty[7] ~= nil
end

------------------------------------------------------------------ walka1: zdolności z danych, kotwice, błyski, WK.paski życia
WK.ZD = {}
WK.nr = {}
do
	local i = 0
	for _, linia in { "ogien", "moc" } do
		for _, A in D.zdolnosci[linia] do
			i += 1
			WK.ZD[A.id] = A
			WK.nr[i] = A
			A.linia = linia
		end
	end
end
WK.pociski = {}

-- kotwice zdolności: Attachment / Bone o nazwie (modele z Blendera), atrybut Kotwica_<Nazwa>, inaczej zapas (× promień)
WK.zapas = { Pysk = Vector3.new(0, 0.7, -1.05), Brzuch = Vector3.new(0, 0.35, 0), Ogon = Vector3.new(0, 0.4, 1.2),
	SkrzydloL = Vector3.new(-0.9, 1.0, 0), SkrzydloP = Vector3.new(0.9, 1.0, 0) }
function WK.kotwica(w, nazwa: string): Vector3
	if w.rig and w.model then
		local a = w.model:FindFirstChild(nazwa, true)
		if a and (a:IsA("Attachment") or a:IsA("Bone")) then
			return a.WorldPosition
		end
	end
	local v = (w.kotwice and w.kotwice[nazwa]) or (WK.zapas[nazwa] or Vector3.zero) * w.F.r
	local cf = w.cfBase or (CFrame.new(C + Vector3.new(w.x, 0, w.z)) * CFrame.Angles(0, w.kier + math.pi, 0))
	return cf:PointToWorldSpace(v)
end

-- błysk trafionego (pula Highlight — wbudowane, bez wgrań)
WK.blyski = {}
for i = 1, 8 do
	local h = Instance.new("Highlight")
	h.FillColor = Color3.new(1, 1, 1)
	h.FillTransparency = 0.1
	h.OutlineTransparency = 1
	h.DepthMode = Enum.HighlightDepthMode.Occluded
	h.Enabled = false
	h.Parent = lokalne
	WK.blyski[i] = { h = h, do_ = 0 }
end
function WK.blysnij(w, kolor: Color3)
	if not w or not w.model then
		return
	end
	local b = WK.blyski[1]
	for _, x in WK.blyski do
		if x.do_ < b.do_ then
			b = x
		end
	end
	b.h.Adornee = w.model
	b.h.FillColor = kolor
	b.h.Enabled = true
	b.do_ = os.clock() + 0.11
end
function WK.krokBlyskow()
	local t = os.clock()
	for _, b in WK.blyski do
		if b.h.Enabled and t > b.do_ then
			b.h.Enabled = false
		end
	end
end

-- WK.paski życia nad zranionymi (najbliższe do 14), w warstwie 2D jak napisy
WK.paski = {}
for i = 1, 14 do
	local f = nowy("Frame", { Name = "PasekZycia", Size = UDim2.fromOffset(44, 7), AnchorPoint = Vector2.new(0.5, 1), BackgroundColor3 = tusz,
		BorderSizePixel = 0, Visible = false, ZIndex = 2 }, gui)
	rog(f, 3)
	local pw = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = hex("6BD66B"), BorderSizePixel = 0, ZIndex = 3 }, f)
	rog(pw, 3)
	WK.paski[i] = { f = f, w = pw }
end
function WK.krokPaskow()
	local ja0 = widoki[mojId]
	local lista = {}
	if ja0 then
		local t = os.clock()
		for id, w in widoki do
			if id ~= mojId and not w.boss and not w.martwy and w.hp < 0.995 and t - w.ranaT < 8 and bit32.band(w.flagi, 8) == 0 then
				local d = (w.x - ja0.x) ^ 2 + (w.z - ja0.z) ^ 2
				if d < 8100 then
					table.insert(lista, { w = w, d = d })
				end
			end
		end
		table.sort(lista, function(a, b)
			return a.d < b.d
		end)
	end
	local sk = skalaEkranu() * ekranSkala.Scale
	for i, P in WK.paski do
		local e = lista[i]
		local widac = false
		if e then
			local w = e.w
			local top = C + Vector3.new(w.x, (w.F.model_h or 2) * w.F.r / math.max(0.1, w.F.model_r or 1) + 1.2, w.z)
			local v, na = kamera:WorldToViewportPoint(top)
			if na then
				widac = true
				P.f.Position = UDim2.fromOffset(v.X, v.Y)
				P.f.Size = UDim2.fromOffset(math.floor((30 + w.F.r * 3) * sk), math.floor(6 * sk))
				P.w.Size = UDim2.fromScale(math.clamp(w.hp, 0, 1), 1)
				P.w.BackgroundColor3 = if w.hp > 0.5 then hex("6BD66B") elseif w.hp > 0.25 then hex("FFC83D") else hex("FF4A4A")
			end
		end
		P.f.Visible = widac
	end
end

local function rysuj(w, dt: number)
	if w.stopDo and os.clock() < w.stopDo then
		return -- zatrzymanie klatki przy trafieniu
	end
	local moj = w.id == mojId
	local F = w.F
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
		local W = wariantD(w.kokonWariant)
		w.kokon.Color = if W and W.id == "tecza" then Color3.fromHSV((tGlob * 0.8) % 1, 0.6, 1) elseif W then hex(W.kolor)
			else Color3.fromHSV((tGlob * 0.4) % 1, 0.25, 1)
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
	-- ruch proceduralny z parametrów formy: chód, podskok, pochylenie, tempo kroku
	w.faza += dt * (2.5 + 11 * mv) * (F.krok or 1) / (0.75 + r * 0.09)
	local s = math.abs(math.sin(w.faza))
	local hop = s * r * (F.podskok or 0.2) * mv
	local sy = 1 + 0.07 * mv * s - 0.13 * mv * (1 - s) ^ 3 + math.sin(tGlob * 2.3 + w.id) * 0.03 * (1 - math.min(1, mv))
	local pochyl = (F.pochyl or 0.12) * math.min(1, mv)
	-- kurz przy stawianiu kroku (tylko blisko kamery)
	if s < 0.2 and w.sOst >= 0.2 and mv > 0.35 and (moj or (nrKlatki + w.id) % 2 == 0) then
		local ja2 = widoki[mojId]
		if moj or (ja2 and (w.x - ja2.x) ^ 2 + (w.z - ja2.z) ^ 2 < 3600) then
			E:pyl(poz + Vector3.new(0, 0.3, 0), r * 0.45, 2)
		end
	end
	w.sOst = s
	local kiw = math.sin(w.faza) * 0.09 * mv + math.clamp(-w.skret * 0.07, -0.32, 0.32) * math.min(1, mv + 0.3)
	local naprzod = 0
	-- wypad przy gryzieniu (trzeci cios łańcucha — wyraźny wypad z chrupnięciem)
	if w.gryzT < 0.3 then
		w.gryzT += dt
		local k = math.sin(math.clamp(w.gryzT / 0.3, 0, 1) * math.pi)
		local mocny = if w.gryzK == 3 then 1.8 else 1
		naprzod += r * 0.5 * k * mocny
		pochyl += 0.4 * k * mocny
		sy -= 0.1 * k
	end
	-- przewrót (po trzecim ciosie łańcucha, ogonie, meteorze): bezwładny przechył na bok i powrót
	local przewKat, przewY = 0, 0
	if w.przewT < 0.6 then
		w.przewT += dt
		local f = math.clamp(w.przewT / 0.55, 0, 1)
		przewKat = math.sin(f * math.pi) * 1.45 * (if w.id % 2 == 0 then 1 else -1)
		przewY = math.sin(f * math.pi) * r * 0.35
		hop = 0
	end
	-- TAIL SWEEP: pełny obrót wokół osi
	local obrotOgona = 0
	if w.spinT < 0.32 then
		w.spinT += dt
		obrotOgona = math.clamp(w.spinT / 0.3, 0, 1) * math.pi * 2
	end
	-- zamach i kanał oddechu: pozy czytelne dla innych (sygnał, zanim uderzy)
	local skrzydlaZamach = false
	local Az = WK.nr[bit32.band(w.akcja, 15)]
	local wZamachu = bit32.band(w.akcja, 16) ~= 0 and Az ~= nil
	local wKanale = bit32.band(w.akcja, 32) ~= 0 and Az ~= nil
	if moj and w.kanalDo and os.clock() < w.kanalDo then
		wKanale = true
		Az = Az or WK.ZD[w.kanalAb]
	end
	if wZamachu then
		if Az.typ == "pocisk" or Az.typ == "oddech" then
			pochyl -= 0.3 -- głowa w górę: nabiera ognia
		elseif Az.typ == "ogon" then
			kiw += math.sin(tGlob * 26) * 0.12
			sy -= 0.08
		elseif Az.typ == "lot" then
			skrzydlaZamach = true
			sy -= 0.1
		elseif Az.typ == "ryk" then
			pochyl -= 0.45
			sy += 0.08
		elseif Az.typ == "meteor" then
			sy -= 0.22
			pochyl += 0.15
		end
	elseif wKanale then
		pochyl += 0.12
	end
	-- żar w pysku przy zamachu linii FIRE i w czasie oddechu
	local ogienPysk = Az ~= nil and ((wZamachu and (Az.typ == "pocisk" or Az.typ == "oddech")) or wKanale)
	if ogienPysk then
		if not w.zar then
			local p = Instance.new("Part")
			p.Shape = Enum.PartType.Ball
			p.Anchored = true
			p.CanCollide = false
			p.CanQuery = false
			p.CanTouch = false
			p.CastShadow = false
			p.Material = Enum.Material.Neon
			p.Color = Color3.fromRGB(255, 160, 50)
			p.Parent = lokalne
			w.zar = p
		end
		w.zar.Transparency = 0.1
		w.zar.Color = if Az.id == "inferno" then Color3.fromRGB(255, 90, 200) else Color3.fromRGB(255, 160, 50)
		local sz = math.max(0.5, r * (0.24 + 0.08 * math.sin(tGlob * 22)) * (if Az.id == "inferno" then 1.3 else 1))
		w.zar.Size = Vector3.new(sz, sz, sz)
		w.zar.Position = WK.kotwica(w, "Pysk")
	elseif w.zar and w.zar.Transparency < 1 then
		w.zar.Transparency = 1
	end
	-- kanał: strumień ognia z pyska w kierunku patrzenia (sterowany ruchem)
	if wKanale and Az then
		w.ogienT = (w.ogienT or 0) - dt
		if w.ogienT <= 0 and (moj or wWidoku(poz, r)) then
			w.ogienT = 0.07
			E:strumien(WK.kotwica(w, "Pysk"), Vector3.new(math.sin(w.kier), 0, math.cos(w.kier)), r * 0.4 + Az.zasieg, Az.kat_st, Az.id == "inferno")
		end
		w.ogienDz = (w.ogienDz or 0) - dt
		if w.ogienDz <= 0 and moj then
			w.ogienDz = 0.35
			dzwiek("plusk", 0.55 + math.random() * 0.1)
		end
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
	-- lot (WING GLIDE: niski łuk, METEOR DIVE: wysoki)
	local wysSkoku = 0
	if bit32.band(w.flagi, 32) ~= 0 then
		w.skokT += dt
		local f = math.clamp(w.skokT / math.max(0.2, w.lotCzas), 0, 1)
		wysSkoku = math.sin(f * math.pi) * (if w.lotTyp == "meteor" then 9 + r * 0.8 else 2.5 + r * 0.35)
		pochyl += if w.lotTyp == "meteor" then (if f < 0.5 then -0.3 else 0.5) else 0.12
	end
	local sxz = 1 / math.sqrt(math.max(0.5, sy))
	local base = CFrame.new(poz + Vector3.new(math.sin(w.kier) * naprzod, hop + wysSkoku + 0.1 + przewY, math.cos(w.kier) * naprzod))
		* CFrame.Angles(0, w.kier + math.pi + obrotOgona, 0) * CFrame.Angles(-pochyl, 0, kiw + przewKat) -- przód modeli to −Z (układ rigów Pet Areny)
	w.cfBase = base
	local skx, sky = sxz * puls, sy * puls
	if w.rig then
		w.model:PivotTo(base)
		-- modele ze szkieletem: klipy zdolności z danych (anim.ogien, anim.moc, anim.przewrot), jeśli są
		if w.rig.ogien and w.akcjaPop ~= w.akcja and bit32.band(w.akcja, 16 + 32) ~= 0 then
			local nr = bit32.band(w.akcja, 15)
			local tr = if nr <= #D.zdolnosci.ogien then w.rig.ogien else w.rig.moc
			if tr then
				tr:Play()
			end
		end
		if w.rig.przewrot and przewKat ~= 0 and w.przewT < dt * 2 then
			w.rig.przewrot:Play()
		end
		w.akcjaPop = w.akcja
		if w.rig.chod then
			w.rig.chod:AdjustSpeed(0.2 + mv)
		end
		if w.gryzT == 0 and w.rig.gryz then
			w.rig.gryz:Play()
		end
	else
		-- kończyny: nogi w parach (kłus: po przekątnej), ogon macha, głowa kłapie przy gryzieniu
		local T = {}
		local kat = math.sin(w.faza) * 0.55 * math.min(1, mv) * (if przewKat ~= 0 then 0.1 else 1)
		local kGryz = if w.gryzT < 0.3 then math.sin(math.clamp(w.gryzT / 0.3, 0, 1) * math.pi) else 0
		local otw = bit32.band(w.flagi, 2 + 32) ~= 0 or (moj and os.clock() < zrywDo) or skrzydlaZamach
		w.skrz = (w.skrz or 0) + ((if otw then 1 else 0) - (w.skrz or 0)) * math.min(1, dt * 8)
		local maxOgon = 0
		for k, pv in w.pivoty do
			local ax, ay, az = 0, 0, 0
			if k <= 4 then
				ax = if k == 1 or k == 4 then kat else -kat
			elseif k == 5 then
				ay = math.sin(w.faza * 2 + tGlob) * 0.35 * (0.3 + math.min(1, mv))
			elseif k == 6 then
				ax = (if w.grupa and pivotyNazwane(w) then 0.15 else -0.5) * kGryz + math.sin(tGlob * 2 + w.id) * 0.04
			elseif k == 7 then
				ax = -0.65 * kGryz + math.abs(math.sin(tGlob * 1.3 + w.id)) * 0.04
			elseif k == 8 or k == 9 then
				local s = if k == 8 then -1 else 1
				-- spoczynek: skrzydła półuniesione (czytelne z kamery z góry); zryw / szybowanie: rozłożone i bijące
				local o = 0.32 + w.skrz * 0.68
				ay = s * (o * 1.35 + math.sin(tGlob * 2 + w.id) * 0.04)
				az = -s * (0.25 + w.skrz * (0.1 + math.sin(tGlob * 14) * 0.35) + 0.05 * math.sin(tGlob * 1.7 + w.id))
			elseif k >= 11 then
				ay = math.sin(w.faza * 1.1 + tGlob * 1.4 - (k - 11) * 0.7) * 0.16 * (0.35 + math.min(1, mv))
				maxOgon = math.max(maxOgon, k)
			end
			local pS = pv * Vector3.new(skx, sky, skx)
			T[k] = CFrame.new(pS) * CFrame.Angles(0, 0, az) * CFrame.Angles(ax, ay, 0) * CFrame.new(-pS)
		end
		for k = 12, maxOgon do
			if T[k] and T[k - 1] then
				T[k] = T[k - 1] * T[k] -- ogon łańcuchem: każdy segment niesie następne
			end
		end
		local fala = if F.chod == "pelzanie" then r * 0.12 * (0.3 + math.min(1, mv)) else 0
		local cf = w.cf
		local gr = w.grupa
		for i, o in w.offs do
			local p = w.poz[i]
			local x = p.X * skx
			if fala > 0 then
				x += math.sin(w.faza + p.Z * 0.35) * fala
			end
			local t = T[gr[i]]
			if t then
				cf[i] = base * t * CFrame.new(x, p.Y * sky, p.Z * skx) * o
			else
				cf[i] = base * CFrame.new(x, p.Y * sky, p.Z * skx) * o
			end
		end
		workspace:BulkMoveTo(w.czesci, cf, Enum.BulkMoveMode.FireCFrameChanged)
	end
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

local function csv(n: string): { string }
	local w = {}
	for x in string.gmatch((gracz:GetAttribute(n) or "") .. ",", "([^,]*),") do
		table.insert(w, x)
	end
	return w
end

local function odswiezPanel()
	local zl = gracz:GetAttribute("EW_Zloto") or 0
	local mf = gracz:GetAttribute("EW_MaxForma") or 1
	local wDomu = gracz:GetAttribute("EW_WDomu") == true
	local war, tro = csv("EW_Warianty"), csv("EW_Trofea")
	for f, T in trofea do
		local lv = tonumber(tro[f]) or 1
		local W = wariantD(war[f])
		local G = D.legowisko
		T.poziom.Text = if f <= mf then string.format(UI.poziom, lv) else ""
		T.wariant.Text = if W then W.nazwa else ""
		T.wariant.TextColor3 = if W then hex(W.kolor) else zloto
		T.stawka.Text = "+" .. tostring(math.floor(D.formy[f].trofeum * G.poziomy_x[lv] * (if W then W.x else 1) * 10 + 0.5) / 10)
		T.vf.ImageColor3 = if f > mf then Color3.new(0, 0, 0) elseif W then Color3.new(1, 1, 1):Lerp(hex(W.kolor), 0.55) else Color3.new(1, 1, 1)
		local cena = if f <= mf and G.ceny_x[lv] then math.floor(G.ceny_x[lv] * D.formy[f].trofeum) else nil
		T.kup.Visible = f <= mf
		T.kupNapis.Text = if cena then tostring(cena) else UI.maks
		local stac = cena ~= nil and wDomu and zl >= cena
		T.kup.BackgroundColor3 = if stac then hex("3DB36B") else hex("6A5A7A")
		T.kup.AutoButtonColor = stac
	end
	local bt = gracz:GetAttribute("EW_BossTrofea") or 0
	local bs = 0
	for i = 1, bt do
		bs += D.legowisko.boss_trofea[i]
	end
	bossTrofNapis.Text = string.format(UI.boss_trofea, bt, bs)
	legInfo.Text = if wDomu then UI.w_legowisku else UI.tylko_w_legowisku
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

-- czy iść do legowiska po złoto: zebranego za mało na najtańszy zakup, z legowiskiem starczy
local function doDomu(): boolean
	local zl = gracz:GetAttribute("EW_Zloto") or 0
	local leg = gracz:GetAttribute("EW_ZlotoLeg") or 0
	local naj = math.huge
	for _, U in D.ulepszenia do
		local c = U.ceny[gracz:GetAttribute("EW_Poz_" .. U.id) or 1]
		if c then
			naj = math.min(naj, c)
		end
	end
	return zl < naj and zl + leg >= naj and leg >= 20
end

local brama = nil
local bramaOtwarta: boolean? = nil
local function odswiezBrame()
	local otw = (gracz:GetAttribute("EW_MaxForma") or 1) >= D.las.od_formy
	if otw == bramaOtwarta then
		return
	end
	bramaOtwarta = otw
	brama = brama or (kontener:FindFirstChild("Scena") and kontener.Scena:FindFirstChild("Brama"))
	if brama then
		for _, d in brama:GetDescendants() do
			if d:IsA("BasePart") and d.Name == "Plot" then
				d.LocalTransparencyModifier = if otw then 0.85 else 0
			end
		end
	end
	gracz:SetAttribute("EW_K_Las", otw)
end

-- przycisk linii FIRE / POWER: działająca wersja (z odnową) albo zamknięta (ciemna, „at <STADIUM>”); nad nim następna wersja
WK.stanZd = {}
function WK.zdHUD(P, NB, linia: string, wForma: number, teraz: number)
	local A = L.zdolnoscFormy(D, linia, wForma)
	local N = L.nastepnaZdolnosc(D, linia, wForma)
	WK.stanZd[linia] = { nazwa = if A then A.id else "", zamkniete = A == nil, od = P.od.Text, nast = if N then N.id else "", pigulka = NB.ramka.Visible }
	if A then
		P.napis.Text = A.krotko or A.nazwa
		P.napis.TextColor3 = papier
		P.od.Text = ""
		P.b.BackgroundColor3 = P.kolor
		P.cien.Size = UDim2.fromScale(1, math.clamp((zdGotowy[linia] - teraz) / (A.zamach_s + A.odnowa_s), 0, 1))
	else
		P.napis.Text = if N then (N.krotko or N.nazwa) else ""
		P.napis.TextColor3 = hex("8A7A9A")
		P.od.Text = if N then string.format(UI.od_stadium, D.formy[N.od].nazwa) else ""
		P.b.BackgroundColor3 = hex("2A2236")
		P.cien.Size = UDim2.fromScale(1, 0)
	end
	NB.ramka.Visible = A ~= nil and N ~= nil and odslona == nil
	if N then
		NB.n1.Text = string.format(UI.nastepna_zd, N.krotko or N.nazwa)
		NB.n2.Text = string.format(UI.od_stadium, D.formy[N.od].nazwa)
	end
end

local function odswiezHUD()
	odswiezBrame()
	local bossId = kontener:GetAttribute("BossId") or 0
	local bossHP = kontener:GetAttribute("BossHP") or 0
	local bw, jw = widoki[bossId], widoki[mojId]
	ramkaBossa.Visible = bossHP > 0 and bw ~= nil and jw ~= nil and odslona == nil and (bw.x - jw.x) ^ 2 + (bw.z - jw.z) ^ 2 < 90 * 90
	bossW.Size = UDim2.fromScale(bossHP, 1)
	bossNazwa.Text = D.boss.nazwa .. " " .. string.rep("*", kontener:GetAttribute("BossStopien") or 1)
	local skB = skalaEkranu()
	ramkaBaneru.Position = UDim2.new(0.5, -40 * skB, 0, (if ramkaBossa.Visible then 112 else 76) * skB)
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
	naSNapis.Text = UI.skarb .. " " .. tostring(gracz:GetAttribute("EW_ZlotoLeg") or 0) .. "  " .. string.format(UI.na_s, gracz:GetAttribute("EW_ZlotoNaS") or 0)
	local teraz = os.clock()
	cienZryw.Size = UDim2.fromScale(1, math.clamp((zrywGotowy - teraz) / D.ruch.zryw_odnowa_s, 0, 1))
	cienGryz.Size = UDim2.fromScale(1, math.clamp((gryzGotowy - teraz) / math.max(0.1, WK.gryzOdnowa), 0, 1))
	WK.zdHUD(WK.zdOgien, WK.nastOgien, "ogien", wForma, teraz)
	WK.zdHUD(WK.zdMoc, WK.nastMoc, "moc", wForma, teraz)
	local hpJa = if w then w.hp else 1
	WK.zycieW.Size = UDim2.fromScale(math.clamp(hpJa, 0, 1), 1)
	WK.zycieW.BackgroundColor3 = if hpJa > 0.5 then hex("6BD66B") elseif hpJa > 0.25 then hex("FFC83D") else hex("FF4A4A")
	-- podpowiedź: na start (do 5 kulek), przy pełnym pasku i po otwarciu lasu
	if gracz:GetAttribute("EW_WDomu") and not pelny then
		podpNapis.Text = UI.w_legowisku
		ramkaPodp.Visible = true
	elseif lasPodp and os.clock() < lasPodp and not pelny then
		podpNapis.Text = UI.las_podp
		ramkaPodp.Visible = true
	elseif doDomu() and not pelny then
		podpNapis.Text = UI.do_legowiska
		ramkaPodp.Visible = true
	elseif pelny then
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
local lasPodp: number? = nil
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
	local doLasu = w and lasPodp and os.clock() < lasPodp and not L.wLesie(D, w.x, w.z)
	local domu = w and not doLasu and doDomu() and not gracz:GetAttribute("EW_WDomu")
	local pokaz = w and (doLasu or domu or (kulekZjedzonych < 5 and (gracz:GetAttribute("EW_MaxForma") or 1) == 1)) and not w.martwy
	if not pokaz then
		strzalka.Transparency, grot.Transparency = 1, 1
		return
	end
	local best, bd = nil, math.huge
	if doLasu then
		best = { 0, D.pole.r - 10 }
	elseif domu then
		local x, z = L.legowiskoPoz(D, mojSlot())
		best = { x, z }
	else
		for i, p in D.kulkiPoz do
			if kulkiZywe[i] and osiagalna(p) then
				local d = (p[1] - w.x) ^ 2 + (p[2] - w.z) ^ 2
				if d < bd and d > 4 then
					best, bd = p, d
				end
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

------------------------------------------------------------------ wykluwanie na starcie (jajko w legowisku, 2,5 s, ruch pomija)
local jajko: any = nil
local jajkoBylo = false
local function krokJajka(dt: number)
	local w = widoki[mojId]
	if not jajkoBylo and w and (gracz:GetAttribute("EW_Forma") or 1) == 1 then
		jajkoBylo = true
		local p = Instance.new("Part")
		p.Name = "Jajko"
		p.Shape = Enum.PartType.Ball
		p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch = true, false, false, false
		p.Color = hex("FFF6E0")
		p.Material = Enum.Material.SmoothPlastic
		p.Size = Vector3.new(4.2, 5.2, 4.2)
		p.Parent = lokalne
		local pas = p:Clone()
		pas.Name = "JajkoPas"
		pas.Shape = Enum.PartType.Cylinder
		pas.Color = hex("8FD86B")
		pas.Size = Vector3.new(0.6, 4.3, 4.3)
		pas.Parent = lokalne
		jajko = { t = 0, czas = 2.6, p = p, pas = pas }
		gracz:SetAttribute("EW_K_Jajko", "start")
	end
	if not jajko then
		return
	end
	jajko.t += dt
	local koniec = jajko.t >= jajko.czas or wektor.Magnitude > 0.2 or not w
	if w then
		local c = C + Vector3.new(w.x, 2.6, w.z)
		local trzes = math.sin(jajko.t * (8 + jajko.t * 10)) * math.min(0.35, jajko.t * 0.15)
		jajko.p.CFrame = CFrame.new(c) * CFrame.Angles(0, 0, trzes)
		jajko.pas.CFrame = CFrame.new(c + Vector3.new(0, 0.3, 0)) * CFrame.Angles(0, 0, math.pi / 2 + trzes)
		ustawPrzezroczystosc(w, 1)
	end
	if koniec then
		if w then
			local c = C + Vector3.new(w.x, 2.6, w.z)
			E:iskry(c, hex("FFF6E0"), 26, 2)
			E:iskry(c, hex("8FD86B"), 10, 1.4)
			E:pierscien(C + Vector3.new(w.x, 0.3, w.z), 6, hex("FFE14D"), 0.5)
			w.przezr = -1
			w.pulsT, w.pulsSila = 0, 0.15
		end
		jajko.p:Destroy()
		jajko.pas:Destroy()
		jajko = nil
		pokazBaner("HATCHED!", hex("9BFFB8"), 1.4)
		dzwiek("wyklucie", 1.2)
		gracz:SetAttribute("EW_K_Jajko", "wyklute")
	end
end

------------------------------------------------------------------ odsłona nowej formy (kokon → wybuch → tabliczka)
local function tabliczka(f: number, nowa: boolean)
	local F = D.formy[f]
	tablGora.Text = if nowa then UI.nowa_forma else UI.znowu
	tablNazwa.Text = F.nazwa
	local nowe = {}
	for _, linia in { "ogien", "moc" } do
		local A = L.zdolnoscFormy(D, linia, f)
		if A then
			table.insert(nowe, A.nazwa)
		end
	end
	tablDol.Text = if #nowe > 0 then table.concat(nowe, " + ") else UI.gryz
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
					E:iskry(k.Position, k.Color, 5, 0.6)
					local typ = D.kulkiPoz[z.i][3]
					local ile = (if typ == 3 then D.jedzenie.wielka elseif typ == 2 then D.jedzenie.duza else D.jedzenie.mala) * L.apetyt(D, ja())
					E:liczba(k.Position + Vector3.new(0, 2, 0), "+" .. tostring(math.floor(ile + 0.5)), k.Color)
				end
				pulsPaska = 0
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
			local a0 = widoki[z.a]
			if a0 then
				a0.gryzT, a0.gryzK = 0, 3 -- chrupnięcie na koniec
			end
			if z.sb and z.sb > 0 then
				local ja0 = widoki[mojId]
				if z.a == mojId or z.b == mojId or (ja0 and (ja0.x - z.x) ^ 2 + (ja0.z - z.z) ^ 2 < 2500) then
					WK.zwolnienieDo = os.clock() + 0.7
					WK.liczSpowolnien += 1
					E:slowo(p + Vector3.new(0, 6, 0), "CHOMP!", hex("FF6A3D"), 1.1, 0.9)
				end
			end
			if z.a == mojId then
				WK.liczZjadl += 1
				pulsPaska = 0
				dzwiek("kryt", 1.4)
				E:iskry(p, hex("C8A070"), 16, 1.4)
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
				WK.liczZjedzen += 1
				dzwiek("ko", 0.8)
				dzwiek("krol", 0.6)
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
				w.gryzK = z.k or 1
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
			if w then
				w.kokonWariant = z.wariant
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
				WK.liczOdslon += 1
				dzwiek("krol", 1)
				blyskT = 0
				wstrzasnij(0.9 + D.formy[z.forma].r * 0.12, 0.55)
				tabliczka(z.forma, z.nowa)
				local W = wariantD(z.wariant)
				if W then
					tablGora.Text = string.format(UI.wariant, W.nazwa)
					tablGora.TextColor3 = hex(W.kolor)
					E:iskry(C + Vector3.new(predX, 4, predZ), hex(W.kolor), 40, 2.4)
					dzwiek("boss", 1.4)
				else
					tablGora.TextColor3 = hex("9BFFB8")
				end
				gracz:SetAttribute("EW_K_Wariant", z.wariant or "")
				odslona = { t = 0, czas = D.ewolucja.tabliczka_s, nowa = z.nowa, forma = z.forma, faza = "tabliczka" }
				if z.nowa then
					task.delay(D.ewolucja.tabliczka_s, function()
						toast(string.format(UI.trofeum_toast, D.formy[z.forma].trofeum), 3)
						dzwiek("monety", 1)
					end)
				end
				umGotowy = 0
				zdGotowy = { ogien = 0, moc = 0 }
				if type(z.zd) == "table" and #z.zd > 0 then
					local nazwy = {}
					for _, id in z.zd do
						if WK.ZD[id] then
							table.insert(nazwy, WK.ZD[id].nazwa)
						end
					end
					task.delay(D.ewolucja.tabliczka_s + 0.3, function()
						pokazBaner(string.format(UI.nowa_zdolnosc, table.concat(nazwy, " + ")), hex("FFB347"), 2.4)
						dzwiek("boss", 1.3)
					end)
				end
				odswiezDrabine()
				gracz:SetAttribute("EW_K_Odslon", WK.liczOdslon)
			end
		elseif t == "zebrano" then
			if z.id == mojId and z.ile > 0 then
				pokazBaner(string.format(UI.zebrano, z.ile), zloto, 1.4)
				dzwiek("monety", 1.1)
				local w = widoki[mojId]
				if w then
					E:iskry(C + Vector3.new(w.x, 2, w.z), zloto, 14, 1.2)
				end
			end
		elseif t == "powrot" then
			tablGora.Text = "WELCOME BACK!"
			tablGora.TextColor3 = hex("9BFFB8")
			tablNazwa.Text = "+" .. tostring(z.ile) .. " GOLD"
			tablDol.Text = string.format(UI.powrot, z.ile)
			tablDol2.Text = ""
			ramkaTabl.Visible = true
			tablSkala.Scale = 0.3
			odslona = { t = 0, czas = 3.5, faza = "tabliczka" }
			dzwiek("monety", 0.9)
			gracz:SetAttribute("EW_K_Powrot", z.ile)
		elseif t == "olbrzym_rana" then
			E:liczba(C + Vector3.new(z.x, 10, z.z), "+" .. tostring(z.zloto), zloto)
		elseif t == "las_otwarty" then
			if z.id == mojId then
				task.delay(D.ewolucja.tabliczka_s + 0.2, function()
					pokazBaner(UI.las_otwarty, hex("9BFFB8"), 2.2)
					dzwiek("boss", 1.2)
				end)
				lasPodp = os.clock() + 45
			end
		elseif t == "boss_rana" then
			local p = C + Vector3.new(z.x, D.formy[D.boss.forma].r * 1.5, z.z)
			E:liczba(p, "-" .. tostring(z.ile), hex("FF7AA8"))
			E:iskry(p, hex("FF9AD8"), 8, 1)
			local bw = widoki[z.id]
			if bw then
				bw.pulsT, bw.pulsSila = 0, -0.08
				WK.blysnij(bw, Color3.new(1, 1, 1))
			end
			if z.s == mojSlot() then
				dzwiek("kryt", 0.9)
				wstrzasnij(0.3, 0.15)
				WK.liczRanZad += 1
			end
		elseif t == "boss_gryz" then
			local bw = widoki[z.id]
			if bw then
				bw.gryzT = 0
			end
			if z.cel == mojId then
				pokazBaner(UI.au, hex("FF6A6A"), 0.9)
				dzwiek("ko", 1.3)
				wstrzasnij(1.0, 0.3)
				predOK = false
			end
		elseif t == "boss_pokonany" then
			local p = C + Vector3.new(z.x, 3, z.z)
			E:iskry(p, zloto, 40, 2.2)
			E:pierscien(C + Vector3.new(z.x, 0.3, z.z), 20, zloto, 0.8)
			if z.s == mojSlot() then
				pokazBaner(string.format(UI.skrzynia, z.zloto), zloto, 2.4)
				dzwiek("monety", 1)
				wstrzasnij(0.8, 0.4)
			end
		elseif t == "olbrzym" then
			if z.id == mojId then
				pokazBaner(UI.olbrzym, zloto, 2)
				dzwiek("boss", 1)
			end
		elseif t == "ogloszenie" then
			pokazBaner(z.tekst, zloto, 2.6)
		elseif t == "rana" then
			-- walka1: liczba ran, błysk, zatrzymanie klatki i wstrząs (gdy dotyczy mnie), przewrót
			local q, a = widoki[z.id], widoki[z.a]
			local p = C + Vector3.new(z.x, 0, z.z)
			local wys = if q then q.F.r * 1.5 + 1 else 3
			local jaA, jaQ = z.a == mojId, z.id == mojId
			local ja0 = widoki[mojId]
			local blisko = ja0 ~= nil and (ja0.x - z.x) ^ 2 + (ja0.z - z.z) ^ 2 < 3600
			if q then
				q.hp = z.hp
				q.ranaT = os.clock()
				q.pulsT, q.pulsSila = 0, -0.07
				if jaA or jaQ or blisko then
					WK.blysnij(q, if jaQ then hex("FF5A5A") else Color3.new(1, 1, 1))
				end
			end
			if jaA or jaQ or blisko then
				local kol = if jaQ then hex("FF6A6A") elseif z.kr then zloto elseif jaA then papier else hex("C8C0D0")
				E:liczba(p + Vector3.new(0, wys, 0), tostring(z.ile), kol)
				if z.kr and (jaA or jaQ) then
					E:slowo(p + Vector3.new(0, wys + 2.5, 0), UI.kryt, zloto, 0.5, 0.6)
				end
				local ogien = z.jak == "ogien" or z.jak == "zar" or z.jak == "plama"
				E:iskry(p + Vector3.new(0, wys * 0.55, 0), if ogien then Color3.fromRGB(255, 150, 50) else Color3.new(1, 1, 1), if z.kr then 10 else 5, 0.8)
			end
			if jaA or jaQ then
				local frac = math.clamp(z.ile / (D.walka.hp_baza * 0.6), 0, 1)
				local stop = os.clock() + 0.04 + 0.07 * frac + (if z.kr then 0.03 else 0)
				if q then
					q.stopDo = stop
				end
				if a then
					a.stopDo = stop
				end
				wstrzasnij(if jaQ then 0.45 + frac * 1.5 else 0.2 + frac * 0.9, 0.12 + frac * 0.2)
				if z.jak == "gryz" or z.jak == "boss" then
					dzwiek(if z.kr then "kryt" else "cios", (if jaQ then 0.85 else 1.05) + math.random() * 0.15)
				elseif z.jak ~= "ogien" and z.jak ~= "plama" then
					dzwiek("kryt", 0.75 + math.random() * 0.1)
				end
				if jaA then
					WK.liczRanZad += 1
				else
					WK.liczRanOtrz += 1
				end
			end
			if z.pw and q then
				q.przewT = 0
				if jaQ then
					WK.liczPrzewrotow += 1
					pokazBaner(UI.przewrot, hex("C8B8FF"), 0.8)
				end
			end
		elseif t == "zamach" then
			-- zamach zdolności: zapowiedź zasięgu na ziemi (fair: widać, gdzie uderzy)
			local A = WK.ZD[z.ab]
			local w = widoki[z.id]
			if A then
				local rb = if w then w.F.r else 2
				local p = C + Vector3.new(z.x, 0, z.z)
				if A.typ == "ogon" then
					E:zapowiedz(p, rb + A.r, hex("BFE8FF"), A.zamach_s)
				elseif A.typ == "ryk" then
					E:zapowiedz(p, rb + A.r, hex("FFB347"), A.zamach_s)
				elseif A.typ == "meteor" then
					local cel = p + Vector3.new(math.sin(z.kier or 0), 0, math.cos(z.kier or 0)) * A.d
					E:zapowiedz(cel, rb + A.r, hex("FF4A4A"), A.zamach_s + A.s)
				elseif A.typ == "lot" then
					E:pyl(p + Vector3.new(0, 0.3, 0), rb, 6)
				end
				if w then
					w.zamachT = 0
				end
				local ja0 = widoki[mojId]
				if z.id == mojId then
					WK.liczZamachow += 1
					zdGotowy[A.linia] = os.clock() + A.zamach_s + A.odnowa_s
					WK.wolnoDo = os.clock() + A.zamach_s
					dzwiek("klik", 0.65)
				elseif ja0 and (ja0.x - z.x) ^ 2 + (ja0.z - z.z) ^ 2 < 2500 then
					dzwiek("klik", 0.55)
				end
			end
		elseif t == "pocisk" then
			local w = widoki[z.id]
			local kier = Vector3.new(z.kx, 0, z.kz)
			local od = C + Vector3.new(z.x, 2, z.z)
			if w then
				local k = WK.kotwica(w, "Pysk")
				od = Vector3.new(od.X, math.min(k.Y, C.Y + 2.5 + w.F.r * 0.3), od.Z)
			end
			WK.pociski[z.n] = E:kulaOgnia(od, kier, z.v, z.czas)
			if z.id == mojId then
				WK.liczPociskow += 1
				dzwiek("umiejetnosc", 1.6)
			end
		elseif t == "pocisk_koniec" then
			local u = WK.pociski[z.n]
			WK.pociski[z.n] = nil
			local p = if u then u.poz else C + Vector3.new(z.x, 2, z.z)
			if u then
				u.koniec = true
			end
			E:iskry(p, Color3.fromRGB(255, 140, 40), if z.trafil then 12 else 5, 0.9)
			if z.trafil then
				E:pierscien(Vector3.new(p.X, C.Y, p.Z), 3, Color3.fromRGB(255, 170, 60), 0.35)
				dzwiek("plusk", 1.3)
			end
		elseif t == "oddech" then
			local w = widoki[z.id]
			if w then
				w.kanalDo, w.kanalAb = os.clock() + z.czas, z.ab
			end
			if z.id == mojId then
				WK.wolnoDo = os.clock() + z.czas
				dzwiek("umiejetnosc", 0.8)
			end
		elseif t == "plama" then
			E:plama(C + Vector3.new(z.x, 0, z.z), z.r, z.czas)
		elseif t == "ogon" then
			local w = widoki[z.id]
			local p = C + Vector3.new(z.x, 0.3, z.z)
			if w then
				w.spinT = 0
			end
			E:pierscien(p, z.r, Color3.new(1, 1, 1), 0.45)
			E:pyl(p, z.r * 0.8, 10)
			dzwiek("zlapanie", 0.85)
			if z.id == mojId then
				wstrzasnij(0.5, 0.25)
			end
		elseif t == "lot" or t == "meteor" then
			local w = widoki[z.id]
			if w then
				w.skokT, w.lotCzas, w.lotTyp = 0, z.czas, t
				local korzen = w.model and (w.model.PrimaryPart or w.model:FindFirstChildWhichIsA("BasePart"))
				if korzen and (z.id == mojId or wWidoku(C + Vector3.new(w.x, 0, w.z), w.F.r)) then
					local tr = E:smuga(korzen, if t == "meteor" then Color3.fromRGB(255, 120, 40) else Color3.fromRGB(200, 240, 255), w.F.r * 0.8)
					task.delay(z.czas + 0.4, function()
						for _, x in { tr.Attachment0, tr.Attachment1, tr } do
							if x then
								x:Destroy()
							end
						end
					end)
				end
				if t == "meteor" then
					E:cien(C + Vector3.new(z.x1, 0, z.z1), w.F.r * 1.5, z.czas)
				end
			end
			if z.id == mojId then
				dzwiek(if t == "meteor" then "boss" else "wyklucie", if t == "meteor" then 0.8 else 1.5)
			end
		elseif t == "ryk" then
			local p = C + Vector3.new(z.x, 0.3, z.z)
			E:pierscienie(p, z.r)
			E:pierscien(p, z.r, hex("FF9A3D"), 0.6)
			local ja0 = widoki[mojId]
			if ja0 then
				local d = math.sqrt((ja0.x - z.x) ^ 2 + (ja0.z - z.z) ^ 2)
				if d < z.r * 2.5 then
					wstrzasnij(1.0 * (1 - d / (z.r * 2.5)) + 0.2, 0.4)
					dzwiek("boss", 0.65)
				end
			end
		elseif t == "ladowanie" then
			local p = C + Vector3.new(z.x, 0.3, z.z)
			if z.typ == "meteor" then
				E:pierscienie(p, z.r)
				E:krater(p, z.r * 0.6)
				E:iskry(p + Vector3.new(0, 2, 0), Color3.fromRGB(255, 130, 40), 22, 1.6)
				local ja0 = widoki[mojId]
				if ja0 and (ja0.x - z.x) ^ 2 + (ja0.z - z.z) ^ 2 < (z.r * 3) ^ 2 then
					wstrzasnij(if z.id == mojId then 1.6 else 1.0, 0.45)
					dzwiek("trzesienie", 1)
				end
			else
				E:pierscien(p, z.r, Color3.fromRGB(210, 240, 255), 0.5)
				E:pyl(p, z.r * 0.7, 8)
				if z.id == mojId then
					wstrzasnij(0.5, 0.2)
					dzwiek("cios", 0.8)
				end
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
			WK.liczKorekt += 1
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
			local jedza = q.forma >= mf + 1 and not (q.slot > 0 and mf <= D.smierc.chronione_formy) and not q.boss
			local jem = mf >= q.forma + 1 and bit32.band(q.flagi, 1) == 0 and not q.boss
				and not (q.slot > 0 and (q.forma <= D.smierc.chronione_formy or mf <= D.smierc.chronione_formy))
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
		if kulkiZywe[i] and osiagalna(p) then
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
		if cel.byt and d < r + L.zasiegGryzu(D, ja()) + D.formy[cel.byt.forma].r then
			akcja("gryz")
		end
		if cel.byt and d < r + 14 then
			akcja("ogien")
		end
		if cel.byt and d < r + 7 then
			akcja("moc")
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
	local nazwy = { Boss = ramkaBossa, Wzrost = ramkaWzrostu, Zloto = ramkaZlota, Drabina = ramkaDrabiny, Gryz = ramkaGryz, Zryw = ramkaZryw,
		Ogien = WK.zdOgien.ramka, Moc = WK.zdMoc.ramka, OgienNast = WK.nastOgien.ramka, MocNast = WK.nastMoc.ramka, Zycie = WK.ramkaZycia, Ewolucja = ramkaEwo, Podpowiedz = ramkaPodp, Toast = ramkaToastu, Tabliczka = ramkaTabl, Panel = panel }
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
	local przyciski = { bGryz, bZryw, WK.zdOgien.b, WK.zdMoc.b, bEwo, bLegowisko, bZamknij }
	for _, d in panel:GetDescendants() do
		if d:IsA("TextButton") and d.Visible then
			table.insert(przyciski, d)
		end
	end
	for _, b in przyciski do
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

------------------------------------------------------------------ legowiska w świecie (trofea na cokołach, kupka złota)
local legowiska: { [number]: any } = {}
local function lista(p: Player, n: string): { string }
	local w = {}
	for x in string.gmatch((p:GetAttribute(n) or "") .. ",", "([^,]*),") do
		table.insert(w, x)
	end
	return w
end

local function czesc3(roz: Vector3, cf: CFrame, kolor: Color3, mat: Enum.Material, ksztalt: Enum.PartType?, rodzic: Instance): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Size = roz
	p.CFrame = cf
	p.Color = kolor
	p.Material = mat
	if ksztalt then
		p.Shape = ksztalt
	end
	p.Parent = rodzic
	return p
end

local function napisNaGorze(rodzic: BasePart, tekst: string, kolor: Color3)
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40
	sg.LightInfluence = 0
	sg.Parent = rodzic
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Text = tekst
	l.TextScaled = true
	l.Font = czcionka
	l.TextColor3 = kolor
	l.Parent = sg
	nowy("UIStroke", { Thickness = 2, Color = tusz }, l)
end

local function zbudujLegowisko(p: Player, slot: number, sig: string)
	local f0 = Instance.new("Folder")
	f0.Name = "Legowisko" .. slot
	f0.Parent = lokalne
	local moj = p == gracz
	local mf = p:GetAttribute("EW_MaxForma") or 1
	local war, tro = lista(p, "EW_Warianty"), lista(p, "EW_Trofea")
	local lx, lz = L.legowiskoPoz(D, slot)
	for f = 1, NF do
		local a = (f - 1) * math.pi * 2 / NF
		local px, pz = lx + math.sin(a) * 8.5, lz + math.cos(a) * 8.5
		local F = D.formy[f]
		local wz = (f <= mf or moj) and wzorce and wzorce:FindFirstChild(F.wzorzec)
		if wz then
			local m = wz:Clone()
			local W = wariantD(war[f])
			local i = 0
			for _, d in m:GetDescendants() do
				if d:IsA("BasePart") then
					i += 1
					d.Anchored = true
					d.CanCollide = false
					d.CanQuery = false
					d.CanTouch = false
					d.CastShadow = false
					if f > mf then
						d.Color = Color3.fromRGB(20, 16, 24)
						d.Material = Enum.Material.SmoothPlastic
					end
				end
			end
			if f <= mf then
				wyglad(m, W)
			end
			pcall(function()
				m:ScaleTo(1.4 / F.model_r)
			end)
			m:PivotTo(CFrame.new(C + Vector3.new(px, 1.25, pz)) * CFrame.Angles(0, math.atan2(px - lx, pz - lz) + math.pi, 0))
			m.Parent = f0
		end
		if moj and f <= mf then
			local tab = czesc3(Vector3.new(2.6, 0.12, 1.1), CFrame.new(C + Vector3.new(lx + math.sin(a) * 11.4, 0.3, lz + math.cos(a) * 11.4))
				* CFrame.Angles(0, a, 0), tusz, Enum.Material.SmoothPlastic, nil, f0)
			napisNaGorze(tab, string.format(UI.poziom, tonumber(tro[f]) or 1), zloto)
		end
	end
	if moj then
		local tab = czesc3(Vector3.new(7, 0.12, 1.6), CFrame.new(C + Vector3.new(lx * 0.9, 0.3, lz * 0.9)) * CFrame.Angles(0, math.atan2(lx, lz), 0), tusz,
			Enum.Material.SmoothPlastic, nil, f0)
		napisNaGorze(tab, UI.twoje_legowisko, hex("9BFFB8"))
	end
	local kupka = czesc3(Vector3.one, CFrame.new(C + Vector3.new(lx, 0, lz)), zloto, Enum.Material.Neon, Enum.PartType.Ball, f0)
	return { folder = f0, sig = sig, kupka = kupka, x = lx, z = lz }
end

local doLeg = 0
local function krokLegowisk(dt: number)
	doLeg -= dt
	if doLeg > 0 then
		return
	end
	doLeg = 0.25
	local ja2 = widoki[mojId]
	local fx, fz = if ja2 then ja2.x else 0, if ja2 then ja2.z else 0
	local zajete = {}
	for _, p in Players:GetPlayers() do
		local slot = p:GetAttribute("EW_Slot") or 0
		if slot > 0 then
			zajete[slot] = true
			local lx, lz = L.legowiskoPoz(D, slot)
			local d = legowiska[slot]
			if (lx - fx) ^ 2 + (lz - fz) ^ 2 < 170 * 170 then
				local sig = table.concat({ tostring(p:GetAttribute("EW_MaxForma")), p:GetAttribute("EW_Warianty") or "", p:GetAttribute("EW_Trofea") or "",
					p.Name }, "|")
				if not d or d.sig ~= sig then
					if d then
						d.folder:Destroy()
					end
					d = zbudujLegowisko(p, slot, sig)
					legowiska[slot] = d
				end
				local leg = p:GetAttribute("EW_ZlotoLeg") or 0
				local s = if leg < 1 then 0.01 else 1.2 + math.min(5, math.log10(leg + 1) * 1.4)
				d.kupka.Size = Vector3.new(s, s * 0.6, s)
				d.kupka.Transparency = if leg < 1 then 1 else 0
				d.kupka.CFrame = CFrame.new(C + Vector3.new(lx, s * 0.3 + math.sin(tGlob * 2) * 0.1, lz))
			elseif d then
				d.folder:Destroy()
				legowiska[slot] = nil
			end
		end
	end
	for slot, d in legowiska do
		if not zajete[slot] then
			d.folder:Destroy()
			legowiska[slot] = nil
		end
	end
	gracz:SetAttribute("EW_K_Legowisk", (function()
		local n = 0
		for _ in legowiska do
			n += 1
		end
		return n
	end)())
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
RunService.RenderStepped:Connect(function(dtPrawdziwe: number)
	-- spowolnienie (zjedzenie gracza): animacje i efekty wolniej przez chwilę
	local dt = if os.clock() < WK.zwolnienieDo then dtPrawdziwe * 0.3 else dtPrawdziwe
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
		elseif string.sub(tp, 1, 8) == "trofeum:" then
			akcja("kup_trofeum", tonumber(string.sub(tp, 9)))
		elseif tp == "zakladka_u" then
			tabT.Visible, tabU.Visible = false, true
		elseif tp == "zakladka_t" then
			tabT.Visible, tabU.Visible = true, false
		else
			akcja(tp)
		end
	end
	if gracz:GetAttribute("EW_TestUklad") then
		gracz:SetAttribute("EW_TestUklad", nil)
		gracz:SetAttribute("EW_K_Uklad", uklad())
	end
	krokAutopilota(dtPrawdziwe)
	krokSterowania(dtPrawdziwe)
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
	krokLegowisk(dt)
	krokJajka(dt)
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
	if pulsPaska < 0.3 then
		pulsPaska += dt
		pasekSkala.Scale = 1 + math.sin(math.clamp(pulsPaska / 0.3, 0, 1) * math.pi) * 0.12
	end
	if blyskT < 0.5 then
		blyskT += dt
		blysk.BackgroundTransparency = math.clamp(0.15 + blyskT / 0.5 * 0.85, 0, 1)
	elseif blysk.BackgroundTransparency < 1 then
		blysk.BackgroundTransparency = 1
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
	WK.krokBlyskow()
	WK.krokPaskow()
	local cel = celKamery(dtPrawdziwe)
	if cel then
		kamera.CameraType = Enum.CameraType.Scriptable
		kamera.FieldOfView = D.kamera.fov - (if os.clock() < WK.zwolnienieDo then 7 else 0)
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
	suma += dtPrawdziwe
	okno += dtPrawdziwe
	if okno >= 1 then
		gracz:SetAttribute("EW_K_Klatka", suma / klatek * 1000)
		local n = 0
		for _ in widoki do
			n += 1
		end
		gracz:SetAttribute("EW_K_Widokow", n)
		gracz:SetAttribute("EW_K_Korekty", WK.liczKorekt)
		gracz:SetAttribute("EW_K_Snapy", WK.liczSnapow)
		gracz:SetAttribute("EW_K_BladMaks", WK.bladMaks)
		gracz:SetAttribute("EW_K_Gryzy", WK.liczGryzow)
		gracz:SetAttribute("EW_K_Zjedzony", WK.liczZjedzen)
		gracz:SetAttribute("EW_K_Zjadl", WK.liczZjadl)
		gracz:SetAttribute("EW_K_RanyZad", WK.liczRanZad)
		gracz:SetAttribute("EW_K_RanyOtrz", WK.liczRanOtrz)
		gracz:SetAttribute("EW_K_Zamachy", WK.liczZamachow)
		gracz:SetAttribute("EW_K_Pociski", WK.liczPociskow)
		gracz:SetAttribute("EW_K_Przewroty", WK.liczPrzewrotow)
		gracz:SetAttribute("EW_K_Spowolnienia", WK.liczSpowolnien)
		gracz:SetAttribute("EW_K_Efekty", E:ile())
		gracz:SetAttribute("EW_K_Zd", HttpService:JSONEncode(WK.stanZd))
		gracz:SetAttribute("EW_K_Legowisko", panel.Visible)
		gracz:SetAttribute("EW_K_Korona", korona.Parent ~= nil)
		gracz:SetAttribute("EW_K_KameraY", kamera.CFrame.Position.Y)
		gracz:SetAttribute("EW_K_MigawkaS", os.clock() - czasMigawki)
		local w = widoki[mojId]
		if w then
			gracz:SetAttribute("EW_K_Flagi", w.flagi)
			gracz:SetAttribute("EW_K_HP", w.hp)
			gracz:SetAttribute("EW_K_Odslona", if odslona then tostring(odslona.faza) else "")
			gracz:SetAttribute("EW_K_Ster", if sterTest then tostring(sterTest.v) .. "/" .. string.format("%.1f", sterTest.do_ - os.clock()) else "")
			gracz:SetAttribute("EW_K_MojX", w.x)
			gracz:SetAttribute("EW_K_MojZ", w.z)
		end
		WK.bladMaks = 0
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
