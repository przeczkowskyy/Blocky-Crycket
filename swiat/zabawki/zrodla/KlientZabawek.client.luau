--[[
	KlientZabawek — klient dwóch zabawek (Script, RunContext Client, w Workspace/ZabawkiGra). Bez strażnika „tylko Studio”.
	Ekran wyboru (dwa duże przyciski) → zabawka 1 „EAT & EVOLVE” (potwór pod kciukiem: drążek pod lewym kciukiem / WASD /
	gałka, DASH, kamera z góry oddala się, gdy rośniesz; własny potwór przewidywany od razu) albo zabawka 2 „LURE A
	MONSTER” (proca: odciągnij i puść, kropki toru na początku łuku, przynęta leci od razu, zwabiony idzie do zagrody).
	Na ekranie tylko to, bez czego nie da się grać. Próby: wejście jak z palca przez atrybuty lokalnego gracza
	(ZT_TestSter, ZT_TestDash, ZT_TestRzut), stan dla prób w atrybutach ZT_* (żadnej funkcji do wywołania).
]]
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")
local GuiService = game:GetService("GuiService")

local gracz = Players.LocalPlayer
local playerGui = gracz:WaitForChild("PlayerGui")
local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DaneZabawek"))
local L = require(Moduly:WaitForChild("LogikaZabawek"))
local Efekty = require(Moduly:WaitForChild("EfektyZabawek"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan1 = Sygnaly:WaitForChild("Stan1")
local evStan2 = Sygnaly:WaitForChild("Stan2")
local wzorce = ReplicatedStorage:WaitForChild("ZabawkiWzorce", 30)
local Z, W, UI = D.zjadacz, D.wabik, D.ui
local C1 = Vector3.new(Z.srodek[1], Z.srodek[2], Z.srodek[3])
local C2 = Vector3.new(W.srodek[1], W.srodek[2], W.srodek[3])
local kamera = workspace.CurrentCamera
local tusz, papier = Color3.fromHex(UI.kolory.tusz), Color3.fromHex(UI.kolory.papier)
local czcionka = Enum.Font[UI.czcionka] or Enum.Font.LuckiestGuy
local cyfry = Enum.Font[UI.czcionka_cyfr] or Enum.Font.FredokaOne
local KOLORY_SLOTOW = { "FF5A5A", "4DA6FF", "6BD66B", "FFB13D", "C27BFF", "FF7FC8", "3DE0D0", "E0E05A" }

local lokalne = Instance.new("Folder")
lokalne.Name = "ZabawkiLokalne"
lokalne.Parent = workspace
local E = Efekty.nowe(lokalne, D)

------------------------------------------------------------------ dźwięki (odcinki arkusza efektów)
local folderDz = Instance.new("Folder")
folderDz.Name = "ZabawkiDzwieki"
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

------------------------------------------------------------------ sterowanie awatara wyłączone (gracz steruje zabawką)
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
gui.Name = "Zabawki"
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
	nowy("UIStroke", { Thickness = g, Color = k, ApplyStrokeMode = Enum.ApplyStrokeMode.Border }, o)
end
local function napis(o: Instance, t: string, poz: UDim2, roz: UDim2, kolor: Color3?, font: Enum.Font?): TextLabel
	local l = nowy("TextLabel", { BackgroundTransparency = 1, Position = poz, Size = roz, Text = t, TextScaled = true, Font = font or czcionka,
		TextColor3 = kolor or papier }, o)
	nowy("UIStroke", { Thickness = 2, Color = tusz }, l)
	return l
end
-- ekran (w próbach: emulacja telefonu — atrybut ZT_Emulacja = Vector2 punktów; ekran ma wtedy rozmiar telefonu i jest
-- powiększony do okna, a układ liczy się jak na telefonie)
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
	local e = gracz:GetAttribute("ZT_Emulacja")
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
gracz:GetAttributeChangedSignal("ZT_Emulacja"):Connect(ustawEmulacje)
-- punkt ekranu (piksele okna) → punkty warstwy ekranu
local function doEkranu(p: Vector2): Vector2
	local k = ekranSkala.Scale
	return (p - ekran.AbsolutePosition) / k
end
local function przycisk(rodzic: Instance, nazwa: string, t: string, poz: UDim2, roz: UDim2, kolor: string, akcja): TextButton
	local b = nowy("TextButton", { Name = nazwa, Position = poz, Size = roz, BackgroundColor3 = Color3.fromHex(kolor), Text = "", AutoButtonColor = true }, rodzic)
	rog(b, 12)
	obrys(b, 3, tusz)
	local l = napis(b, t, UDim2.fromScale(0.08, 0.14), UDim2.fromScale(0.84, 0.72))
	l.Name = "Napis"
	b.Activated:Connect(akcja)
	return b
end

-- menu wyboru
local menu = nowy("Frame", { Name = "Menu", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.fromHex("2A2236"), BackgroundTransparency = 0.05,
	ZIndex = 1 }, ekran)
local menuSrodek = nowy("Frame", { Name = "Srodek", AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
	Size = UDim2.fromOffset(600, 320), BackgroundTransparency = 1 }, menu)
table.insert(skale, nowy("UIScale", { Scale = skalaEkranu() }, menuSrodek))
napis(menuSrodek, UI.menu_tytul, UDim2.fromOffset(0, 0), UDim2.new(1, 0, 0, 52), Color3.fromHex(UI.kolory.zloto))
local function kartaMenu(nr: number, x: number, tytul: string, opis: string, kolor: string)
	local b = przycisk(menuSrodek, "Zabawka" .. nr, "", UDim2.fromOffset(x, 70), UDim2.fromOffset(286, 230), kolor, function()
		evAkcja:FireServer("wybor", nr)
		dzwiek("klik")
	end)
	b:FindFirstChild("Napis"):Destroy()
	napis(b, tytul, UDim2.fromOffset(14, 26), UDim2.new(1, -28, 0, 58))
	napis(b, opis, UDim2.fromOffset(18, 112), UDim2.new(1, -36, 0, 80), papier, cyfry)
end
kartaMenu(1, 0, UI.z1, UI.z1_opis, "3DB36B")
kartaMenu(2, 314, UI.z2, UI.z2_opis, "4F7CE0")

-- wspólne: MENU (mały, lewy górny róg)
local gora = warstwa("Gora", Vector2.new(0, 0), UDim2.new(0, 8, 0, 6), Vector2.new(88, 46))
local bMenu = przycisk(gora, "Menu", UI.menu, UDim2.fromOffset(0, 0), UDim2.fromOffset(88, 46), "5A5566", function()
	evAkcja:FireServer("menu")
	dzwiek("klik")
end)

-- zabawka 1: pasek formy (góra środek), DASH (prawy dół), drążek pod palcem
local pasekRamka = warstwa("Forma", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 6), Vector2.new(250, 44))
local formaNapis = napis(pasekRamka, "", UDim2.fromOffset(0, 0), UDim2.new(1, 0, 0, 22))
local pasekTlo = nowy("Frame", { Position = UDim2.fromOffset(10, 26), Size = UDim2.new(1, -20, 0, 14), BackgroundColor3 = tusz }, pasekRamka)
rog(pasekTlo, 7)
obrys(pasekTlo, 2, papier)
local pasekW = nowy("Frame", { Size = UDim2.fromScale(0, 1), BackgroundColor3 = Color3.fromHex("6BD66B"), BorderSizePixel = 0 }, pasekTlo)
rog(pasekW, 7)
local dashRamka = warstwa("Dash", Vector2.new(1, 1), UDim2.new(1, -14, 1, -14), Vector2.new(96, 96))
local bDash = nowy("TextButton", { Name = "Dash", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.fromHex("FF7A3D"), Text = "", AutoButtonColor = true }, dashRamka)
rog(bDash, 48)
obrys(bDash, 3, tusz)
local dashCien = nowy("Frame", { Name = "Odnowa", AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0, 1), Size = UDim2.fromScale(1, 0),
	BackgroundColor3 = tusz, BackgroundTransparency = 0.45, BorderSizePixel = 0 }, bDash)
rog(dashCien, 48)
napis(bDash, UI.dash, UDim2.fromScale(0.12, 0.3), UDim2.fromScale(0.76, 0.4))
local drazek = warstwa("Drazek", Vector2.new(0.5, 0.5), UDim2.fromOffset(100, 280), Vector2.new(116, 116))
local drazekBaza = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.5 }, drazek)
rog(drazekBaza, 58)
obrys(drazekBaza, 3, Color3.fromHex(UI.kolory.ty))
local galka = nowy("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromOffset(50, 50),
	BackgroundColor3 = Color3.fromHex(UI.kolory.ty) }, drazekBaza)
rog(galka, 25)
drazek.Visible = false

-- zabawka 2: licznik (góra środek), podpowiedź (dół środek)
local licznikRamka = warstwa("Licznik", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 6), Vector2.new(300, 46))
local licznikNapis = napis(licznikRamka, "", UDim2.fromOffset(0, 0), UDim2.new(1, 0, 0, 26))
local najlepszyNapis = napis(licznikRamka, "", UDim2.fromOffset(20, 26), UDim2.new(1, -40, 0, 18), Color3.fromHex(UI.kolory.zloto), cyfry)
local podpRamka = warstwa("Podpowiedz", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -10), Vector2.new(300, 32))
local podpTlo = nowy("Frame", { Size = UDim2.fromScale(1, 1), BackgroundColor3 = tusz, BackgroundTransparency = 0.3 }, podpRamka)
rog(podpTlo, 10)
napis(podpTlo, UI.kat_mocy, UDim2.fromScale(0.04, 0.12), UDim2.fromScale(0.92, 0.76), Color3.fromHex(UI.kolory.ty))

-- baner (duże słowo na ekranie) i komunikat
local banerRamka = warstwa("Baner", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 60), Vector2.new(320, 54))
local baner = napis(banerRamka, "", UDim2.fromScale(0, 0), UDim2.fromScale(1, 1))
local banerSkala = nowy("UIScale", { Scale = 1 }, baner)
baner.Visible = false
local banerT, banerDo = 0, 0
local function pokazBaner(t: string, kolor: string, czas: number?)
	baner.Text = t
	baner.TextColor3 = Color3.fromHex(kolor)
	baner.Visible = true
	baner.Rotation = math.random(-4, 4)
	banerT, banerDo = 0, czas or 1.3
end

------------------------------------------------------------------ wzorce potworów
local function model(nr: number): Model
	local P = D.pety[nr]
	local wz = wzorce and wzorce:FindFirstChild(P.wzorzec)
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
	m.PrimaryPart.Anchored = true
	return m
end

local function krazek(rodzic: Instance, r: number, kolor: string): Part
	local k = Instance.new("Part")
	k.Shape = Enum.PartType.Cylinder
	k.Anchored = true
	k.CanCollide = false
	k.CanQuery = false
	k.CanTouch = false
	k.CastShadow = false
	k.Material = Enum.Material.Neon
	k.Color = Color3.fromHex(kolor)
	k.Size = Vector3.new(0.15, r * 2 + 1, r * 2 + 1)
	k.Parent = rodzic
	return k
end

------------------------------------------------------------------ stan wspólny
local tryb = "menu"
local mojSlot = 0
local tGlob = 0
local wstrzas = { sila = 0, do_ = 0 }
local function wstrzasnij(s: number, czas: number)
	wstrzas.sila = math.max(wstrzas.sila, s)
	wstrzas.do_ = math.max(wstrzas.do_, os.clock() + czas)
end
local tWyboru = os.clock()
local pierwszaAkcja: number? = nil
local function akcjaGracza()
	if not pierwszaAkcja then
		pierwszaAkcja = os.clock() - tWyboru
		gracz:SetAttribute("ZT_Pierwsza", pierwszaAkcja)
	end
end

------------------------------------------------------------------ zabawka 1: widoki bytów, kulki, sterowanie, kamera
local byty: { [number]: any } = {}
local apexId = 0
local mojByt = 0
local korona = Instance.new("Model")
do
	local function c(roz: Vector3, cf: CFrame)
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.Material = Enum.Material.Neon
		p.Color = Color3.fromHex("FFC83D")
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

local kulkiCzesci = {}
local function zbudujKulki()
	if #kulkiCzesci > 0 then
		return
	end
	for i, p in Z.kulkiPoz do
		local k = Instance.new("Part")
		k.Name = "Kulka" .. i
		k.Shape = Enum.PartType.Ball
		k.Anchored = true
		k.CanCollide = false
		k.CanQuery = false
		k.CanTouch = false
		k.CastShadow = false
		k.Material = Enum.Material.Neon
		k.Color = Color3.fromHSV((i * 0.137) % 1, 0.55, 1)
		k.Size = Vector3.one * Z.kulka_r * 2
		k.Position = C1 + Vector3.new(p[1], 0.9, p[2])
		k.Parent = lokalne
		kulkiCzesci[i] = k
	end
end

local function usunByt(w)
	w.model:Destroy()
	w.krazek:Destroy()
	byty[w.id] = nil
end

local function nowyByt(id: number, slot: number, m: number, x: number, z: number): any
	local f = L.forma(Z, m)
	local nr = Z.formy[f].nr
	local md = model(nr)
	md.Parent = lokalne
	local moj = id == mojByt
	local w = { id = id, slot = slot, m = m, x = x, z = z, tx = x, tz = z, kier = 0, tkier = 0, forma = f, nr = nr, model = md,
		krazek = krazek(lokalne, 2, if moj then UI.kolory.ty elseif slot > 0 then KOLORY_SLOTOW[slot] else "FFFFFF"), flagi = 0,
		puls = nil, skala = 1, martwy = false, brak = 0 }
	if slot == 0 then
		w.krazek.Transparency = 0.6
	end
	if moj then
		local hl = Instance.new("Highlight")
		hl.FillTransparency = 1
		hl.OutlineColor = Color3.fromHex(UI.kolory.ty)
		hl.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop
		hl.Parent = md
	end
	byty[id] = w
	return w
end

local function zmienForme(w, f: number)
	w.forma = f
	w.nr = Z.formy[f].nr
	local stary = w.model
	w.model = model(w.nr)
	for _, d in stary:GetChildren() do
		if d:IsA("Highlight") then
			d.Parent = w.model
		end
	end
	stary:Destroy()
	w.model.Parent = lokalne
	w.skala = -1
end

-- sterowanie: drążek pod lewym kciukiem / WASD / gałka; wysyłka co wysylanie_s
local ster = Vector2.zero
local wektor = Vector3.zero
local dotykDrazka: InputObject? = nil
local drazekSrodek = Vector2.zero
local wyslany: Vector3? = nil
local doRuchu = 0
local sterTest: any = nil
local function krokSterowania(dt: number)
	local v = Vector2.zero
	if tryb == "z1" then
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
		v = Vector2.new(x, y)
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
	end
	ster = v
	-- kamera ma stałą orientację: góra ekranu = +z świata
	wektor = Vector3.new(-v.X, 0, v.Y)
	galka.Position = UDim2.new(0.5, v.X * 34, 0.5, -v.Y * 34)
	if tryb ~= "z1" then
		return
	end
	doRuchu -= dt
	local aktywny = v.Magnitude > Z.martwa_strefa
	if aktywny and (doRuchu <= 0 or not wyslany or (wyslany - wektor).Magnitude > 0.25) then
		doRuchu = Z.wysylanie_s
		evAkcja:FireServer("ruch", wektor.X, wektor.Z)
		wyslany = wektor
	elseif not aktywny and wyslany and wyslany.Magnitude > 0.01 then
		evAkcja:FireServer("ruch", 0, 0)
		wyslany = Vector3.zero
	end
end

local ostDash = -99
local function dash()
	if tryb ~= "z1" or os.clock() - ostDash < Z.dash_odnowa_s then
		return
	end
	ostDash = os.clock()
	evAkcja:FireServer("dash")
	dzwiek("umiejetnosc", 1.3)
	local w = byty[mojByt]
	if w then
		w.puls = { t = 0, czas = 0.3, sila = 0.25 }
		pcall(function()
			local tr = E:smuga(w.model.PrimaryPart, Color3.fromHex("FFE6A0"), 2)
			task.delay(0.6, function()
				tr:Destroy()
			end)
		end)
	end
end
bDash.Activated:Connect(dash)

local czasMigawki1 = 0
evStan1.OnClientEvent:Connect(function(b: buffer)
	if typeof(b) ~= "buffer" or tryb ~= "z1" then
		return
	end
	local n = buffer.readu16(b, 8)
	apexId = buffer.readu16(b, 10)
	local nk = #Z.kulkiPoz
	local nb = math.ceil(nk / 8)
	zbudujKulki()
	for i = 0, nb - 1 do
		local bajt = buffer.readu8(b, 12 + i)
		for k = 0, 7 do
			local idx = i * 8 + k + 1
			if idx <= nk then
				local zywa = bit32.band(bajt, 2 ^ k) ~= 0
				kulkiCzesci[idx].Transparency = if zywa then 0 else 1
			end
		end
	end
	local widziane = {}
	local o0 = 12 + nb
	for i = 1, n do
		local o = o0 + (i - 1) * 18
		local id = buffer.readu16(b, o)
		local slot = buffer.readu8(b, o + 2)
		local f = buffer.readu8(b, o + 3)
		local x, z, m = buffer.readf32(b, o + 4), buffer.readf32(b, o + 8), buffer.readf32(b, o + 12)
		widziane[id] = true
		local w = byty[id] or nowyByt(id, slot, m, x, z)
		w.tx, w.tz, w.m, w.flagi = x, z, m, f
		w.tkier = buffer.readi16(b, o + 16) / 1000
		local martwy = bit32.band(f, 4) ~= 0
		if w.martwy and not martwy then
			-- odrodzenie: skok na nowe miejsce
			w.x, w.z = x, z
		end
		w.martwy = martwy
		w.brak = 0
	end
	for id, w in byty do
		if not widziane[id] then
			w.brak += 1
			if w.brak >= 3 then
				usunByt(w)
			end
		end
	end
	czasMigawki1 = os.clock()
end)

local function rysujByt(w, dt: number)
	local moj = w.id == mojByt
	if moj and not w.martwy and wektor.Magnitude > Z.martwa_strefa then
		-- przewidywanie: własny potwór rusza w tej samej klatce, serwer dociąga łagodnie
		local v = L.predkosc(Z, w.m) * (if os.clock() - ostDash < Z.dash_s then Z.dash_v else 1)
		w.x += wektor.X * v * dt
		w.z += wektor.Z * v * dt
		w.tkier = math.atan2(wektor.X, wektor.Z)
	end
	local a = 1 - math.exp(-dt * (if moj then 5 else 14))
	local dx, dz = w.tx - w.x, w.tz - w.z
	if dx * dx + dz * dz > 400 then
		w.x, w.z = w.tx, w.tz
	else
		w.x += dx * a
		w.z += dz * a
	end
	local dk = (w.tkier - w.kier + math.pi) % (2 * math.pi) - math.pi
	w.kier += dk * math.min(1, dt * 12)
	local f = L.forma(Z, w.m)
	if f ~= w.forma then
		zmienForme(w, f)
	end
	local r = L.promien(Z, w.m)
	local P = D.pety[w.nr]
	local s = r / P.promien
	local puls = 1
	if w.puls then
		w.puls.t += dt
		local q = w.puls.t / w.puls.czas
		if q >= 1 then
			w.puls = nil
		else
			puls = 1 + math.sin(q * math.pi) * w.puls.sila
		end
	end
	if math.abs(s * puls - w.skala) > 0.02 then
		w.skala = s * puls
		pcall(function()
			w.model:ScaleTo(w.skala)
		end)
	end
	local hop = math.abs(math.sin(tGlob * 9 + w.id)) * r * 0.12
	local widac = not w.martwy
	local ukryj = if widac then 0 else 1
	w.model:PivotTo(CFrame.new(C1 + Vector3.new(w.x, hop + 0.1, w.z)) * CFrame.Angles(0, w.kier, 0))
	for _, d in w.model:GetDescendants() do
		if d:IsA("BasePart") and d ~= w.model.PrimaryPart then
			d.LocalTransparencyModifier = if bit32.band(w.flagi, 1) ~= 0 then 0.45 + math.sin(tGlob * 16) * 0.3 else ukryj
		end
	end
	w.krazek.Size = Vector3.new(0.15, r * 2 + 0.8, r * 2 + 0.8)
	w.krazek.CFrame = CFrame.new(C1 + Vector3.new(w.x, 0.12, w.z)) * CFrame.Angles(0, 0, math.pi / 2)
	w.krazek.Transparency = if widac then (if moj then 0.1 else 0.35) else 1
	if not moj then
		-- czytelność: zielony — możesz go zjeść, czerwony — on zje ciebie, biały — odbijecie się
		local ja = byty[mojByt]
		if ja and not ja.martwy then
			local rj = L.promien(Z, ja.m)
			w.krazek.Color = if rj >= r * Z.przewaga then Color3.fromHex("5BFF7A") elseif r >= rj * Z.przewaga then Color3.fromHex("FF4040")
				else Color3.fromHex("FFFFFF")
		end
	end
	if w.id == apexId and widac then
		korona.Parent = lokalne
		pcall(function()
			korona:ScaleTo(math.max(0.6, r / 3))
		end)
		korona:PivotTo(CFrame.new(C1 + Vector3.new(w.x, r * 2.4 + hop + 1, w.z)) * CFrame.Angles(0, tGlob * 2, 0))
	end
end

------------------------------------------------------------------ zabawka 2: potwory łąki, proca, przynęty
local potwory: { [number]: any } = {}
local celowanie: any = nil -- { od = Vector2, teraz = Vector2, wej = InputObject? }
local kropki = {}
local kameraCel2 = 60
local lotPrzynety: any = nil
local ostRzut2 = -99
local zwabien = 0

local function skalaPotwora(strefa: number, f: number): number
	local s = W.skala_strefy[math.clamp(strefa, 1, #W.skala_strefy)] or 1
	for _, O in W.odmiany do
		local fl = if O.id == "giant" then 16 elseif O.id == "golden" then 32 else 8
		if bit32.band(f, fl) ~= 0 then
			s *= O.rozmiar
		end
	end
	return s
end

local function nowyPotwor(id: number, nr: number, strefa: number, f: number, x: number, z: number, wl: number): any
	local md = model(nr)
	local s = skalaPotwora(strefa, f)
	if s ~= 1 then
		pcall(function()
			md:ScaleTo(s)
		end)
	end
	if bit32.band(f, 32) ~= 0 or bit32.band(f, 64) ~= 0 then
		for _, d in md:GetDescendants() do
			if d:IsA("BasePart") and d ~= md.PrimaryPart then
				d.Color = Color3.fromHex("FFC83D"):Lerp(d.Color, 0.35)
				d.Material = Enum.Material.Foil
			end
		end
		local sp = Instance.new("Sparkles")
		sp.SparkleColor = Color3.fromHex("FFE68A")
		sp.Parent = md.PrimaryPart
	end
	md.Parent = lokalne
	local w = { id = id, nr = nr, model = md, x = x, z = z, tx = x, tz = z, kier = 0, tkier = 0, stan = 0, wl = wl, f = f, skala = s, brak = 0,
		krazek = krazek(lokalne, D.pety[nr].promien * s, D.rzadkosci[D.pety[nr].stopien].kolor) }
	w.krazek.Transparency = 0.5
	potwory[id] = w
	return w
end

local function usunPotwora(w)
	w.model:Destroy()
	w.krazek:Destroy()
	potwory[w.id] = nil
end

evStan2.OnClientEvent:Connect(function(b: buffer)
	if typeof(b) ~= "buffer" or tryb ~= "z2" then
		return
	end
	local n = buffer.readu16(b, 8)
	local widziane = {}
	for i = 1, n do
		local o = 10 + (i - 1) * 16
		local id = buffer.readu16(b, o)
		local nr = buffer.readu8(b, o + 2)
		local st = buffer.readu8(b, o + 3)
		local wl = buffer.readu8(b, o + 4)
		local f = buffer.readu8(b, o + 5)
		local x, z = buffer.readf32(b, o + 6), buffer.readf32(b, o + 10)
		widziane[id] = true
		local w = potwory[id]
		if w and w.f ~= f then
			usunPotwora(w)
			w = nil
		end
		w = w or nowyPotwor(id, nr, math.floor(st / 16), f, x, z, wl)
		w.tx, w.tz, w.stan, w.wl = x, z, st % 16, wl
		w.tkier = buffer.readi16(b, o + 14) / 1000
		w.brak = 0
	end
	for id, w in potwory do
		if not widziane[id] then
			w.brak += 1
			if w.brak >= 3 then
				usunPotwora(w)
			end
		end
	end
end)

local function rysujPotwora(w, dt: number)
	local a = 1 - math.exp(-dt * 10)
	local dx, dz = w.tx - w.x, w.tz - w.z
	if dx * dx + dz * dz > 900 then
		w.x, w.z = w.tx, w.tz
	else
		w.x += dx * a
		w.z += dz * a
	end
	local dk = (w.tkier - w.kier + math.pi) % (2 * math.pi) - math.pi
	w.kier += dk * math.min(1, dt * 8)
	local docel = (w.skala0 or w.skala) * (if w.stan == 3 then 0.5 else 1)
	w.skala0 = w.skala0 or w.skala
	if math.abs(docel - w.skala) > 0.01 then
		w.skala = w.skala + (docel - w.skala) * math.min(1, dt * 6)
		pcall(function()
			w.model:ScaleTo(w.skala)
		end)
	end
	local biegnie = w.stan == 1 or w.stan == 2 or bit32.band(w.f, 64) ~= 0
	local hop = math.abs(math.sin(tGlob * (if biegnie then 14 else 6) + w.id)) * (if biegnie then 1.2 else 0.35) * w.skala
	w.model:PivotTo(CFrame.new(C2 + Vector3.new(w.x, hop + 0.1, w.z)) * CFrame.Angles(0, w.kier, 0))
	local r = D.pety[w.nr].promien * w.skala
	w.krazek.Size = Vector3.new(0.15, r * 2 + 1, r * 2 + 1)
	w.krazek.CFrame = CFrame.new(C2 + Vector3.new(w.x, 0.15, w.z)) * CFrame.Angles(0, 0, math.pi / 2)
	w.krazek.Transparency = if w.stan == 3 then 1 else 0.5
end

-- kropki toru (tylko początek łuku)
local function kropka(i: number): Part
	local k = kropki[i]
	if not k then
		k = Instance.new("Part")
		k.Shape = Enum.PartType.Ball
		k.Anchored = true
		k.CanCollide = false
		k.CanQuery = false
		k.CanTouch = false
		k.CastShadow = false
		k.Material = Enum.Material.Neon
		k.Color = Color3.fromHex(UI.kolory.ty)
		k.Size = Vector3.one * 0.9
		k.Parent = lokalne
		kropki[i] = k
	end
	return k
end

local function katMoc(c): (number, number)
	local d = c.od - c.teraz
	local s = skalaEkranu()
	local moc = math.clamp(d.Magnitude / (W.przeciagniecie_pt * s * ekranSkala.Scale), 0, 1)
	-- odciągnięcie w dół = rzut w głąb łąki; w bok = skręt (kamera stoi za zagrodą: prawo ekranu = −x świata)
	local kat = if d.Magnitude > 2 then math.atan2(-d.X, -d.Y) else 0
	kat = math.clamp(kat, -math.rad(W.kat_maks_st), math.rad(W.kat_maks_st))
	return kat, moc
end

local function luk(x0: number, z0: number, x: number, z: number, f: number): Vector3
	local d = math.sqrt((x - x0) ^ 2 + (z - z0) ^ 2)
	local h = 6 + d * 0.18
	return C2 + Vector3.new(x0 + (x - x0) * f, 3 + h * 4 * f * (1 - f), z0 + (z - z0) * f)
end

local function rysujCelowanie()
	if not celowanie or celowanie.moc == nil then
		for _, k in kropki do
			k.Transparency = 1
		end
		return
	end
	local kat, moc = celowanie.kat, celowanie.moc
	local x, z, _, x0, z0 = L.ladowanie(W, math.max(1, mojSlot), kat, moc, gracz:GetAttribute("ZW_Zasieg") or W.zasieg0)
	for i = 1, W.kropek do
		local k = kropka(i)
		k.Transparency = 0.1 + i * 0.08
		k.Position = luk(x0, z0, x, z, i / W.kropek * 0.38)
	end
	kameraCel2 = z
end

local function przynetaLeci(slot: number, x0: number, z0: number, x: number, z: number, czas: number, moja: boolean)
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.one * 1.6
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Material = Enum.Material.Neon
	p.Color = Color3.fromHex(if moja then "FF5A8A" else KOLORY_SLOTOW[slot] or "FFFFFF")
	p.Parent = lokalne
	local tr
	pcall(function()
		tr = E:smuga(p, Color3.fromHex("FFE0F0"), 0.8)
	end)
	local t = 0
	E:dodaj(czas, function(f: number, dt: number)
		t += dt
		p.Position = luk(x0, z0, x, z, math.min(1, t / czas))
		p.CFrame = p.CFrame * CFrame.Angles(t * 9, t * 6, 0)
	end, function()
		E:plask(C2 + Vector3.new(x, 0.3, z), Color3.fromHex("FF8AB0"))
		if moja then
			dzwiek("plusk", 1.1)
		end
		if tr then
			tr:Destroy()
		end
		p:Destroy()
	end)
	if moja then
		lotPrzynety = { x = x, z = z, do_ = os.clock() + czas + 1.1 }
	end
end

local function rzuc(kat: number, moc: number)
	if tryb ~= "z2" or os.clock() - ostRzut2 < W.rzut_przerwa_s then
		return
	end
	ostRzut2 = os.clock()
	evAkcja:FireServer("rzut", kat, moc)
	local x, z, t, x0, z0 = L.ladowanie(W, math.max(1, mojSlot), kat, moc, gracz:GetAttribute("ZW_Zasieg") or W.zasieg0)
	przynetaLeci(mojSlot, x0, z0, x, z, t, true)
	dzwiek("klik", 0.8 + moc * 0.6)
	podpRamka.Visible = false
end

-- scena „LURED!” (krótka: potwór w kole w kolorze rzadkości, tabliczka rzadkości i odmiany)
local scena: any = nil
local function scenaZwabienia(z)
	if scena then
		scena.ramka:Destroy()
	end
	local P = D.pety[z.nr]
	local R = D.rzadkosci[z.rz] or D.rzadkosci[1]
	local O = nil
	for _, o in W.odmiany do
		if o.id == z.odm then
			O = o
		end
	end
	local tlo = nowy("Frame", { Name = "Scena", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.fromRGB(20, 14, 32), BackgroundTransparency = 0.45,
		ZIndex = 30 }, ekran)
	local s = skalaEkranu()
	local kolo = nowy("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.45), Size = UDim2.fromOffset(200 * s, 200 * s),
		BackgroundColor3 = Color3.fromHex(R.kolor), BackgroundTransparency = 0.35, ZIndex = 30 }, tlo)
	rog(kolo, 200)
	local vf = nowy("ViewportFrame", { AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.45), Size = UDim2.fromOffset(230 * s, 230 * s),
		BackgroundTransparency = 1, ZIndex = 31 }, tlo)
	local kam = Instance.new("Camera")
	kam.Parent = vf
	vf.CurrentCamera = kam
	local m = model(z.nr)
	m.Parent = vf
	m:PivotTo(CFrame.new())
	local h = P.wysokosc
	kam.CFrame = CFrame.lookAt(Vector3.new(0, h * 0.55, h * 1.9), Vector3.new(0, h * 0.45, 0))
	local t1 = napis(tlo, UI.zlapany, UDim2.new(0.5, -170 * s, 0.06, 0), UDim2.fromOffset(340 * s, 56 * s), Color3.fromHex(UI.kolory.zloto))
	t1.ZIndex = 32
	local tab = nowy("Frame", { AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.8), Size = UDim2.fromOffset(300 * s, 50 * s),
		BackgroundColor3 = Color3.fromHex(if O then O.kolor else R.kolor), Rotation = -4, ZIndex = 32 }, tlo)
	rog(tab, 12)
	obrys(tab, 3, tusz)
	local tabSkala = nowy("UIScale", { Scale = 3 }, tab)
	local tt = napis(tab, (if O then O.nazwa .. " · " else "") .. string.upper(R.nazwa), UDim2.fromScale(0.05, 0.1), UDim2.fromScale(0.9, 0.8))
	tt.ZIndex = 33
	local nn = napis(tlo, P.nazwa, UDim2.new(0.5, -150 * s, 0.88, 0), UDim2.fromOffset(300 * s, 28 * s))
	nn.ZIndex = 32
	scena = { ramka = tlo, m = m, t = 0, tabSkala = tabSkala, czas = if O or z.rz >= 3 then 2.2 else 1.5 }
	if O or z.rz >= 4 then
		E:iskry(kamera.CFrame.Position + kamera.CFrame.LookVector * 12, Color3.fromHex(if O then O.kolor else R.kolor), 30, 2)
	end
end

local function krokSceny(dt: number)
	if not scena then
		return
	end
	scena.t += dt
	local t = scena.t
	scena.m:PivotTo(CFrame.new(0, math.abs(math.sin(t * 7)) * 1.2, 0) * CFrame.Angles(0, t * 4, 0))
	scena.tabSkala.Scale = if t < 0.15 then 3 - t / 0.15 * 2.2 elseif t < 0.27 then 0.8 + (t - 0.15) / 0.12 * 0.2 else 1
	if t > scena.czas then
		scena.ramka:Destroy()
		scena = nil
	end
end

------------------------------------------------------------------ wejście
UserInputService.InputBegan:Connect(function(wej: InputObject, przetworzone: boolean)
	if wej.UserInputType == Enum.UserInputType.Gamepad1 then
		if wej.KeyCode == Enum.KeyCode.ButtonA or wej.KeyCode == Enum.KeyCode.ButtonR2 then
			dash()
		end
		return
	end
	if przetworzone then
		return
	end
	if wej.KeyCode == Enum.KeyCode.Space or wej.KeyCode == Enum.KeyCode.LeftShift then
		dash()
		return
	end
	local dot = wej.UserInputType == Enum.UserInputType.Touch
	local mysz = wej.UserInputType == Enum.UserInputType.MouseButton1
	if not (dot or mysz) then
		return
	end
	local p = Vector2.new(wej.Position.X, wej.Position.Y)
	if tryb == "z1" and dot and p.X < kamera.ViewportSize.X * 0.55 then
		-- drążek pojawia się pod kciukiem
		dotykDrazka = wej
		drazekSrodek = p
		local inset = GuiService:GetGuiInset()
		local q = doEkranu(p + Vector2.new(0, inset.Y))
		drazek.Position = UDim2.fromOffset(q.X, q.Y)
		drazek.Visible = true
	elseif tryb == "z2" and not scena then
		celowanie = { od = p, teraz = p, wej = wej }
	end
end)

UserInputService.InputChanged:Connect(function(wej: InputObject)
	if celowanie and (wej == celowanie.wej or wej.UserInputType == Enum.UserInputType.MouseMovement) then
		celowanie.teraz = Vector2.new(wej.Position.X, wej.Position.Y)
		celowanie.kat, celowanie.moc = katMoc(celowanie)
	end
end)

UserInputService.InputEnded:Connect(function(wej: InputObject)
	if wej == dotykDrazka then
		dotykDrazka = nil
		drazek.Visible = false
	end
	if celowanie and (wej == celowanie.wej or wej.UserInputType == Enum.UserInputType.MouseButton1) then
		local c = celowanie
		celowanie = nil
		if c.moc and c.moc > 0.05 then
			rzuc(c.kat, c.moc)
		end
	end
end)

------------------------------------------------------------------ zdarzenia
local liczZjedzen, liczZjadl, liczEwolucji = 0, 0, 0
evZdarzenia.OnClientEvent:Connect(function(lista)
	if type(lista) ~= "table" then
		return
	end
	for _, z in lista do
		if type(z) ~= "table" then
			continue
		end
		if z.t == "kulka" then
			local w = byty[z.id]
			if z.id == mojByt then
				akcjaGracza()
				local k = kulkiCzesci[z.i]
				if k then
					E:iskry(k.Position, k.Color, 5, 0.6)
				end
				dzwiek("klik", 1.5 + math.random() * 0.3)
				if w then
					w.puls = { t = 0, czas = 0.18, sila = 0.12 }
				end
			end
		elseif z.t == "zjedz" then
			local a, b = byty[z.a], byty[z.b]
			local p = C1 + Vector3.new(z.x, 2, z.z)
			if z.a == mojByt then
				akcjaGracza()
				liczZjadl += 1
				dzwiek("plusk", 0.9)
				E:slowo(p + Vector3.new(0, 4, 0), UI.zjedzony, Color3.fromHex(UI.kolory.ty), 0.9, 0.7)
				E:iskry(p, Color3.fromHex("FFFFFF"), 12, 1)
				if a then
					a.puls = { t = 0, czas = 0.32, sila = 0.35 }
				end
				wstrzasnij(0.35, 0.2)
			elseif z.b == mojByt then
				liczZjedzen += 1
				dzwiek("ko", 0.8)
				E:slowo(p + Vector3.new(0, 5, 0), "POP!", Color3.fromHex("FF6A6A"), 1.4, 1.0)
				E:iskry(p, Color3.fromHex("FF8AB0"), 24, 1.6)
				wstrzasnij(1.2, 0.4)
			else
				E:iskry(p, Color3.fromHex("FFFFFF"), 6, 0.6)
			end
			if b then
				b.martwy = true
			end
		elseif z.t == "odbicie" then
			if z.a == mojByt or z.b == mojByt then
				dzwiek("cios", 1.1)
				E:pyl(C1 + Vector3.new(z.x, 0.5, z.z), 3, 6)
				wstrzasnij(0.2, 0.12)
				for _, id in { z.a, z.b } do
					local w = byty[id]
					if w then
						w.puls = { t = 0, czas = 0.2, sila = -0.18 }
					end
				end
			end
		elseif z.t == "ewolucja" then
			local w = byty[z.id]
			if z.id == mojByt then
				liczEwolucji += 1
				pokazBaner(UI.ewolucja, "6BFF9A", 1.6)
				dzwiek("wyklucie", 1.1)
				wstrzasnij(0.8, 0.35)
				if w then
					E:pierscien(C1 + Vector3.new(w.x, 0.3, w.z), L.promien(Z, w.m) * 2, Color3.fromHex("6BFF9A"), 0.6)
					E:iskry(C1 + Vector3.new(w.x, 3, w.z), Color3.fromHex("FFFFFF"), 26, 1.8)
					w.puls = { t = 0, czas = 0.45, sila = 0.5 }
				end
			elseif w then
				E:iskry(C1 + Vector3.new(w.x, 3, w.z), Color3.fromHex("9BFFB8"), 8, 0.8)
			end
		elseif z.t == "apex" then
			if z.id == mojByt then
				pokazBaner(UI.apex, UI.kolory.zloto, 1.8)
				dzwiek("krol")
			end
		elseif z.t == "dash" then
			local w = byty[z.id]
			if w and z.id ~= mojByt then
				E:pyl(C1 + Vector3.new(w.x, 0.4, w.z), 2, 4)
			end
		elseif z.t == "odrodzenie" then
			if z.id == mojByt then
				dzwiek("klik", 0.7)
			end
		elseif z.t == "ogloszenie" then
			pokazBaner(z.tekst, UI.kolory.zloto, 2.2)
		elseif z.t == "przyneta" then
			if z.slot ~= mojSlot then
				przynetaLeci(z.slot, z.x0, z.z0, z.x, z.z, z.czas, false)
			end
		elseif z.t == "zwabiony" then
			if z.slot == mojSlot then
				akcjaGracza()
				zwabien += 1
				scenaZwabienia(z)
				dzwiek(if z.odm or z.rz >= 4 then "krol" else "zlapanie")
				wstrzasnij(if z.odm then 0.8 else 0.4, 0.25)
				E:pierscien(C2 + Vector3.new(z.x, 0.3, z.z), 5, Color3.fromHex((D.rzadkosci[z.rz] or D.rzadkosci[1]).kolor), 0.6)
			else
				E:slowo(C2 + Vector3.new(z.x, 6, z.z), UI.zlapany, Color3.fromHex("FFFFFF"), 0.6, 0.6)
			end
		elseif z.t == "pudlo" then
			if z.slot == mojSlot then
				E:slowo(C2 + Vector3.new(z.x, 5, z.z), UI.pudlo, Color3.fromHex("FF9A9A"), 0.8, 0.6)
				E:pyl(C2 + Vector3.new(z.x, 0.4, z.z), 4, 8)
				dzwiek("cios", 0.7)
			end
		elseif z.t == "rzadki" then
			pokazBaner(UI.rzadki, "FFC83D", 1.8)
			dzwiek("boss", 1.3)
		end
	end
end)

------------------------------------------------------------------ tryby: zmiana (serwer ustawia atrybut ZT_Tryb)
local function wyczyscZabawki()
	for _, w in byty do
		usunByt(w)
	end
	for _, w in potwory do
		usunPotwora(w)
	end
	for _, k in kulkiCzesci do
		k:Destroy()
	end
	kulkiCzesci = {}
	korona.Parent = nil
	celowanie = nil
	dotykDrazka = nil
	drazek.Visible = false
	if scena then
		scena.ramka:Destroy()
		scena = nil
	end
	for _, k in kropki do
		k.Transparency = 1
	end
end

local function odswiezTryb()
	local t = gracz:GetAttribute("ZT_Tryb") or "menu"
	mojSlot = gracz:GetAttribute("ZT_Slot") or 0
	mojByt = gracz:GetAttribute("ZT_Byt") or 0
	if t ~= tryb then
		wyczyscZabawki()
		tryb = t
		tWyboru = os.clock()
		pierwszaAkcja = nil
		gracz:SetAttribute("ZT_Pierwsza", nil)
		if t == "z2" then
			podpRamka.Visible = true
			kameraCel2 = 60
		end
	end
	menu.Visible = tryb == "menu"
	gora.Visible = tryb ~= "menu"
	pasekRamka.Visible = tryb == "z1"
	dashRamka.Visible = tryb == "z1"
	licznikRamka.Visible = tryb == "z2"
	if tryb ~= "z2" then
		podpRamka.Visible = false
	end
end
gracz:GetAttributeChangedSignal("ZT_Tryb"):Connect(odswiezTryb)
gracz:GetAttributeChangedSignal("ZT_Byt"):Connect(odswiezTryb)
gracz:GetAttributeChangedSignal("ZT_Slot"):Connect(odswiezTryb)
odswiezTryb()

------------------------------------------------------------------ kamera
local camCF: CFrame? = nil
local function celKamery(): CFrame?
	if tryb == "z1" then
		local w = byty[mojByt]
		local x, z, r = 0, 0, 3
		if w then
			x, z, r = w.x, w.z, L.promien(Z, w.m)
		end
		local d = Z.kamera_wys + r * Z.kamera_na_r
		local e = math.rad(Z.kamera_nachylenie_st)
		local cel = C1 + Vector3.new(x, 0, z)
		return CFrame.lookAt(cel + Vector3.new(0, d * math.sin(e), -d * math.cos(e)), cel)
	elseif tryb == "z2" then
		local zp = W.zagrodyPoz[math.max(1, mojSlot)]
		local celZ = kameraCel2
		if lotPrzynety and os.clock() < lotPrzynety.do_ then
			celZ = lotPrzynety.z
		elseif not celowanie then
			celZ = 60
		end
		celZ = math.clamp(celZ, 40, 230)
		kameraCel2 += (celZ - kameraCel2) * 0.08
		local cel = C2 + Vector3.new(zp[1] * 0.6, 0, kameraCel2)
		local poz = C2 + Vector3.new(zp[1], W.kamera_wys + kameraCel2 * 0.12, zp[2] - W.kamera_za)
		return CFrame.lookAt(poz, cel)
	end
	return nil
end

------------------------------------------------------------------ pętla
local klatek, suma, okno = 0, 0, 0
RunService.RenderStepped:Connect(function(dt: number)
	tGlob += dt
	-- próby: wejście jak z palca (atrybuty lokalnego gracza)
	local ts = gracz:GetAttribute("ZT_TestSter")
	if typeof(ts) == "Vector3" then
		sterTest = { v = Vector2.new(ts.X, ts.Y), do_ = os.clock() + ts.Z }
		gracz:SetAttribute("ZT_TestSter", nil)
	end
	if gracz:GetAttribute("ZT_TestDash") then
		gracz:SetAttribute("ZT_TestDash", nil)
		dash()
	end
	local tc = gracz:GetAttribute("ZT_TestCel")
	if typeof(tc) == "Vector2" then
		-- próby: celowanie jak przy odciągniętej procy (kropki toru, kamera na miejsce lądowania)
		celowanie = { od = Vector2.zero, teraz = Vector2.zero, kat = tc.X, moc = tc.Y }
	elseif tc == false then
		gracz:SetAttribute("ZT_TestCel", nil)
		celowanie = nil
	end
	local tr = gracz:GetAttribute("ZT_TestRzut")
	if typeof(tr) == "Vector2" then
		gracz:SetAttribute("ZT_TestRzut", nil)
		rzuc(tr.X, tr.Y)
	end
	krokSterowania(dt)
	if tryb == "z1" then
		for _, w in byty do
			rysujByt(w, dt)
		end
		if apexId == 0 or not byty[apexId] then
			korona.Parent = nil
		end
		for i, k in kulkiCzesci do
			if k.Transparency < 1 then
				k.Position = C1 + Vector3.new(Z.kulkiPoz[i][1], 0.9 + math.sin(tGlob * 3 + i) * 0.25, Z.kulkiPoz[i][2])
			end
		end
		local w = byty[mojByt]
		if w then
			formaNapis.Text = D.pety[w.nr].nazwa
			pasekW.Size = UDim2.fromScale(L.postepFormy(Z, w.m), 1)
			gracz:SetAttribute("ZT_MojX", w.x)
			gracz:SetAttribute("ZT_MojZ", w.z)
		end
		dashCien.Size = UDim2.fromScale(1, math.clamp(1 - (os.clock() - ostDash) / Z.dash_odnowa_s, 0, 1))
	elseif tryb == "z2" then
		for _, w in potwory do
			rysujPotwora(w, dt)
		end
		rysujCelowanie()
		licznikNapis.Text = string.format(UI.licznik, gracz:GetAttribute("ZW_Ile") or 0)
		local nj = gracz:GetAttribute("ZW_Najlepszy") or ""
		najlepszyNapis.Text = if nj ~= "" then string.format(UI.najlepszy, nj) else ""
	end
	krokSceny(dt)
	if baner.Visible then
		banerT += dt
		banerSkala.Scale = if banerT < 0.1 then 0.4 + banerT / 0.1 * 0.8 elseif banerT < 0.2 then 1.2 - (banerT - 0.1) / 0.1 * 0.2 else 1
		if banerT > banerDo then
			baner.Visible = false
		end
	end
	E:krok(dt)
	local cel = celKamery()
	if cel then
		kamera.CameraType = Enum.CameraType.Scriptable
		kamera.FieldOfView = if tryb == "z1" then Z.fov else W.fov
		camCF = if camCF then camCF:Lerp(cel, 1 - math.exp(-dt * 8)) else cel
		local wynik = camCF :: CFrame
		if os.clock() < wstrzas.do_ then
			local s = wstrzas.sila * math.clamp((wstrzas.do_ - os.clock()) / 0.3, 0, 1)
			wynik *= CFrame.new(math.noise(tGlob * 25, 1) * s, math.noise(tGlob * 25, 2) * s, 0)
		else
			wstrzas.sila = 0
		end
		kamera.CFrame = wynik
	else
		camCF = nil
		kamera.CameraType = Enum.CameraType.Custom
	end
	-- pomiar dla prób
	klatek += 1
	suma += dt
	okno += dt
	if okno >= 1 then
		gracz:SetAttribute("ZT_Klatka", suma / klatek * 1000)
		local n = 0
		for _ in byty do
			n += 1
		end
		for _ in potwory do
			n += 1
		end
		gracz:SetAttribute("ZT_Widokow", n)
		gracz:SetAttribute("ZT_Zjedzen", liczZjedzen)
		gracz:SetAttribute("ZT_Zjadl", liczZjadl)
		gracz:SetAttribute("ZT_Ewolucji", liczEwolucji)
		gracz:SetAttribute("ZT_Zwabien", zwabien)
		gracz:SetAttribute("ZT_KameraY", kamera.CFrame.Position.Y)
		klatek, suma, okno = 0, 0, 0
	end
end)

kontener:SetAttribute("KlientGotowy", true)
local _ = GuiService
