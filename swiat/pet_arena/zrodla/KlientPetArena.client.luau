--[[
	KlientPetArena — klient gry Pet Arena (Script, RunContext Client, w Workspace/PetArenaGra). Rysuje to, co liczy
	serwer: pety z wzorców (wygładzanie między migawkami Sygnaly/Stan), lot rzutu po łuku, RING OUT (fosa, plusk,
	gejzer wystrzeliwuje peta w niebo, wraca do właściciela) i KO (gwiazdki, odlot), koronę króla i nagrodę, paski życia
	i napisy nad petami (warstwa 2D), efekty umiejętności, ekran (InterfejsPetArena), kamerę stałą nad areną.

	Wejście: telefon — stuknięcie w arenę, komputer — klik (podgląd celu pod myszą), 1/2/3 — wybór peta, spacja/Q —
	umiejętność; pad — lewa gałka przesuwa celownik, A rzut, X umiejętność, LB/RB wybór peta. Do serwera tylko
	Sygnaly/Akcja. Sterowanie postacią wyłączone (gracz stoi na swoim miejscu na obrzeżu).

	Haczyki prób: Sygnaly/SterowanieKlienta (BindableFunction): "stan", "rzut" (x, z — ta sama droga co stuknięcie),
	"umiejetnosc", "wybierz", "emulacja" (Vector2 | nil), "pomiar_zeruj", "kamera_wolna" (bool), "kadr" (szer, wys).
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local SoundService = game:GetService("SoundService")

local gracz = Players.LocalPlayer
local kontener = script.Parent
local Moduly = kontener:WaitForChild("Moduly")
local D = require(Moduly:WaitForChild("DanePetArena"))
local L = require(Moduly:WaitForChild("LogikaPetArena"))
local Efekty = require(Moduly:WaitForChild("EfektyPetArena"))
local Interfejs = require(Moduly:WaitForChild("InterfejsPetArena"))
local Sygnaly = kontener:WaitForChild("Sygnaly")
local evAkcja = Sygnaly:WaitForChild("Akcja")
local evZdarzenia = Sygnaly:WaitForChild("Zdarzenia")
local evStan = Sygnaly:WaitForChild("Stan")
local sterowanie = Sygnaly:WaitForChild("SterowanieKlienta")
local P = D.prefiks

kontener:SetAttribute("KlientGotowy", false)
if kontener:GetAttribute(D.wylacznik) == false then
	return
end

local wzorce = ReplicatedStorage:WaitForChild(D.folderWzorcow, 20)
local lokalne = Instance.new("Folder")
lokalne.Name = "PetArenaLokalne"
lokalne.Parent = workspace
local E = Efekty.nowe(lokalne, D)
local kamera = workspace.CurrentCamera
local K = D.ui.kolory
local tusz = Color3.fromHex(K.tusz)
local czcionka = Enum.Font[D.ui.czcionka] or Enum.Font.LuckiestGuy
local cyfry = Enum.Font[D.ui.czcionka_cyfr] or Enum.Font.FredokaOne
local R = D.scena.arena_r

local function teraz(): number
	return workspace:GetServerTimeNow()
end

local function mojSlot(): number
	return gracz:GetAttribute("PA_Slot") or 0
end

local function kolorSlotu(slot: number): string
	local s = D.sloty[slot]
	return if s then s.kolor else K.dziki
end

------------------------------------------------------------------ dźwięki (odcinki arkusza efektów)
local folderDzwiekow = Instance.new("Folder")
folderDzwiekow.Name = "PetArenaDzwieki"
folderDzwiekow.Parent = SoundService
local pule: { [string]: { s: { Sound }, i: number } } = {}
local DZ = D.dzwieki
local graneDzwieki = 0
if DZ.arkusz and DZ.arkusz > 0 then
	for rola, e in DZ.efekty do
		local lista = {}
		for i = 1, (if rola == "cios" then 4 else 2) do
			local s = Instance.new("Sound")
			s.Name = rola .. i
			s.SoundId = "rbxassetid://" .. tostring(DZ.arkusz)
			s.Volume = e.glosnosc
			s.PlaybackRegionsEnabled = true
			s.PlaybackRegion = NumberRange.new(e.od, e.koniec)
			s.Parent = folderDzwiekow
			table.insert(lista, s)
		end
		pule[rola] = { s = lista, i = 1 }
	end
end

local function dzwiek(rola: string, wysokosc: number?)
	local p = pule[rola]
	if not p then
		return
	end
	local s = p.s[p.i]
	p.i = (p.i % #p.s) + 1
	s.PlaybackSpeed = wysokosc or 1
	s.TimePosition = DZ.efekty[rola].od
	s:Play()
	graneDzwieki += 1
end

local function dzwiekiZaladowane(): (number, number)
	local n, z = 0, 0
	for _, s in folderDzwiekow:GetChildren() do
		if s:IsA("Sound") then
			n += 1
			if s.IsLoaded and s.TimeLength > 0 then
				z += 1
			end
		end
	end
	return z, n
end

------------------------------------------------------------------ warstwa 2D (napisy nad petami, słowa komiksowe)
local playerGui = gracz:WaitForChild("PlayerGui")
-- w emulacji telefonu napisy nad petami rosną razem z ekranem telefonu (obraz 3D w oknie ma proporcje telefonu)
local function skalaNapisow(): number
	local em = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(em) ~= "Vector2" then
		return 1
	end
	local v = workspace.CurrentCamera.ViewportSize
	return math.min(v.X / em.X, (v.Y - 36) / em.Y)
end
local warstwa = Instance.new("ScreenGui")
warstwa.Name = "PetArenaNapisy"
warstwa.IgnoreGuiInset = true
warstwa.ResetOnSpawn = false
warstwa.DisplayOrder = 3
warstwa.Parent = playerGui
E:warstwa2D(warstwa)

------------------------------------------------------------------ widoki petów
type Widok = { id: number, nr: number, Pd: any, slot: number, model: Model, korzen: BasePart, x: number, z: number,
	tx: number, tz: number, y: number, kier: number, tkier: number, hp: number, hpMax: number, pasek: number, flagi: number,
	zl: number, faza: number, lot: any, odlot: any, skok: any, trafienie: number, krazek: BasePart, hl: Highlight,
	etykieta: Frame, pasekZ: Frame, napis: TextLabel, nagrodaTekst: TextLabel, brak: number, faza0: number, czesci: number }
local widoki: { [number]: Widok } = {}
local czesciWidokow = 0
local krolId, nagrodaKrola = 0, 0
local nazwySlotow: { [number]: string } = {}

local function wzorzec(nr: number): Model
	local Pd = D.pety[nr]
	local wz = wzorce and Pd and wzorce:FindFirstChild(Pd.wzorzec)
	if wz then
		return wz:Clone()
	end
	local m = Instance.new("Model")
	local p = Instance.new("Part")
	p.Name = "Korzen"
	p.Size = Vector3.new(3, 3, 3)
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.Color = Color3.fromRGB(140, 200, 90)
	p.Parent = m
	m.PrimaryPart = p
	return m
end

local function liczCzesci(m: Instance): number
	local n = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			n += 1
		end
	end
	return n
end

local function nowyWidok(id: number, nr: number, slot: number, x: number, z: number): Widok?
	local Pd = D.pety[nr]
	if not Pd then
		return nil
	end
	local m = wzorzec(nr)
	local korzen = m.PrimaryPart :: BasePart
	korzen.Anchored = true
	m.Name = "Pet" .. id
	local moj = slot > 0 and slot == mojSlot()
	local kol = Color3.fromHex(if moj then K.ty elseif slot > 0 then kolorSlotu(slot) else K.dziki)
	local hl = Instance.new("Highlight")
	hl.FillTransparency = 1
	hl.OutlineColor = kol
	hl.OutlineTransparency = if slot > 0 then 0 else 1
	hl.DepthMode = if moj then Enum.HighlightDepthMode.AlwaysOnTop else Enum.HighlightDepthMode.Occluded
	hl.Parent = m
	local kr = Instance.new("Part")
	kr.Name = "Krazek"
	kr.Shape = Enum.PartType.Cylinder
	kr.Anchored = true
	kr.CanCollide = false
	kr.CanQuery = false
	kr.CanTouch = false
	kr.CastShadow = false
	kr.Material = Enum.Material.Neon
	kr.Color = kol
	kr.Transparency = if moj then 0.15 elseif slot > 0 then 0.35 else 0.6
	kr.Size = Vector3.new(0.12, Pd.promien * 2 + 0.8, Pd.promien * 2 + 0.8)
	kr.Parent = m
	m.Parent = lokalne
	-- napis nad petem: imię właściciela / YOU / WILD, pasek życia, nagroda króla
	local et = Instance.new("Frame")
	et.Name = "Etykieta" .. id
	et.AnchorPoint = Vector2.new(0.5, 1)
	local sn = skalaNapisow()
	et.Size = UDim2.fromOffset((if moj then 84 else 66) * sn, (if moj then 34 else 26) * sn)
	et.BackgroundTransparency = 1
	et.Visible = false
	et.Parent = warstwa
	local napis = Instance.new("TextLabel")
	napis.Name = "Napis"
	napis.BackgroundTransparency = 1
	napis.Size = UDim2.new(1, 0, 0.6, 0)
	napis.TextScaled = true
	napis.Font = czcionka
	napis.TextColor3 = kol
	napis.Text = if moj then D.ui.ty elseif slot > 0 then (nazwySlotow[slot] or "") else D.ui.dziki
	napis.Parent = et
	local o = Instance.new("UIStroke")
	o.Thickness = 2
	o.Color = tusz
	o.Parent = napis
	local ramka = Instance.new("Frame")
	ramka.Name = "Zycie"
	ramka.AnchorPoint = Vector2.new(0.5, 1)
	ramka.Position = UDim2.fromScale(0.5, 1)
	ramka.Size = UDim2.new(0.9, 0, 0.3, 0)
	ramka.BackgroundColor3 = tusz
	ramka.BorderSizePixel = 0
	ramka.Parent = et
	local ob = Instance.new("UIStroke")
	ob.Thickness = if moj then 2 else 1
	ob.Color = kol
	ob.Parent = ramka
	local pz = Instance.new("Frame")
	pz.Name = "W"
	pz.Size = UDim2.fromScale(1, 1)
	pz.BackgroundColor3 = Color3.fromHex(K.zycie)
	pz.BorderSizePixel = 0
	pz.Parent = ramka
	local ng = Instance.new("TextLabel")
	ng.Name = "Nagroda"
	ng.BackgroundTransparency = 1
	ng.AnchorPoint = Vector2.new(0.5, 1)
	ng.Position = UDim2.new(0.5, 0, 0, -6 * sn)
	ng.Size = UDim2.fromOffset(150 * sn, 26 * sn)
	ng.TextScaled = true
	ng.Font = cyfry
	ng.TextColor3 = Color3.fromHex(K.zloto)
	ng.Text = ""
	ng.Visible = false
	ng.Parent = et
	local o2 = Instance.new("UIStroke")
	o2.Thickness = 2
	o2.Color = tusz
	o2.Parent = ng
	local n = liczCzesci(m)
	czesciWidokow += n
	local w: Widok = { id = id, nr = nr, Pd = Pd, slot = slot, model = m, korzen = korzen, x = x, z = z, tx = x, tz = z, y = 0,
		kier = 0, tkier = 0, hp = Pd.zycie, hpMax = Pd.zycie, pasek = 0, flagi = 0, zl = 0, faza = 0, lot = nil, odlot = nil,
		skok = nil, trafienie = 0, krazek = kr, hl = hl, etykieta = et, pasekZ = pz, napis = napis, nagrodaTekst = ng, brak = 0,
		faza0 = math.random() * 6, czesci = n }
	widoki[id] = w
	return w
end

local function usunWidok(w: Widok)
	czesciWidokow -= w.czesci
	w.model:Destroy()
	w.etykieta:Destroy()
	if widoki[w.id] == w then
		widoki[w.id] = nil
	end
end

------------------------------------------------------------------ korona króla (bryły, lokalnie)
local korona = Instance.new("Model")
korona.Name = "Korona"
do
	local zloto = Color3.fromHex("FFB000")
	local function c(rozmiar: Vector3, cf: CFrame, ksztalt: Enum.PartType?)
		local p = Instance.new("Part")
		p.Anchored = true
		p.CanCollide = false
		p.CanQuery = false
		p.CanTouch = false
		p.CastShadow = false
		p.Material = Enum.Material.SmoothPlastic
		p.Reflectance = 0
		p.Color = zloto
		p.Size = rozmiar
		p.Shape = ksztalt or Enum.PartType.Block
		p.CFrame = cf
		p.Parent = korona
		return p
	end
	local baza = c(Vector3.new(4.2, 1.1, 4.2), CFrame.new())
	korona.PrimaryPart = baza
	for i = 0, 4 do
		local a = i * math.pi * 2 / 5
		c(Vector3.new(0.9, 2.1, 0.9), CFrame.new(math.cos(a) * 1.7, 1.5, math.sin(a) * 1.7))
		c(Vector3.new(0.85, 0.85, 0.85), CFrame.new(math.cos(a) * 1.7, 2.8, math.sin(a) * 1.7), Enum.PartType.Ball)
	end
end
korona.Parent = nil

------------------------------------------------------------------ ekran
local dotyk = UserInputService.TouchEnabled and not UserInputService.KeyboardEnabled
local ui: any = nil
local wybrany = 1
local ostatniaUmiejetnosc = 0
local uzylUmiejetnosci = false
local wyslane = 0

local function druzynaLista()
	local ids = string.split(gracz:GetAttribute("PA_Druzyna") or "", ",")
	local odp = string.split(gracz:GetAttribute("PA_Odpoczynek") or "", ",")
	local prob = string.split(gracz:GetAttribute("PA_Probny") or "", ",")
	local naArenie = gracz:GetAttribute("PA_NaArenie") or 0
	local tn = teraz()
	local w = {}
	for i, id in ids do
		local nr = L.nrPeta(D, id)
		if nr then
			local Pd = D.pety[nr]
			local doKiedy = tonumber(odp[i]) or 0
			local stan = if naArenie == i then "arena" elseif doKiedy > tn then "odpoczynek" else "gotowy"
			table.insert(w, { id = id, nr = nr, nazwa = Pd.nazwa, kolor = D.rzadkosci[Pd.stopien].kolor, stan = stan,
				zostalo = math.max(0, math.ceil(doKiedy - tn)), probny = prob[i] == "1", wybrany = i == wybrany })
		end
	end
	return w
end

local function wybierz(nr: number)
	wybrany = nr
	evAkcja:FireServer("wybierz", nr)
	wyslane += 1
	dzwiek("klik")
end

local function umiejetnosc()
	if os.clock() - ostatniaUmiejetnosc < 0.25 then
		return
	end
	ostatniaUmiejetnosc = os.clock()
	evAkcja:FireServer("umiejetnosc")
	wyslane += 1
end

local function zbudujUI()
	if ui then
		ui:zniszcz()
	end
	local em = kontener:GetAttribute("EmulacjaEkranu")
	if typeof(em) ~= "Vector2" then
		em = nil
	end
	ui = Interfejs.nowy(playerGui, D, L, { dotyk = dotyk or em ~= nil, emulacja = em, naWybor = wybierz, naUmiejetnosc = umiejetnosc })
end
zbudujUI()

------------------------------------------------------------------ kamera stała nad areną
local kameraWolna = false
local function pozycjaKamery(): (Vector3?, Vector3?)
	local s = D.sloty[mojSlot()]
	if not s then
		return nil, nil
	end
	local KK = D.kamera
	local e = math.rad(KK.nachylenie_st)
	local dx, dz = math.sin(s.katKamery), math.cos(s.katKamery)
	local odl = KK.cel_z + KK.odleglosc * math.cos(e)
	return Vector3.new(dx * odl, KK.odleglosc * math.sin(e), dz * odl), Vector3.new(dx * KK.cel_z, 0, dz * KK.cel_z)
end

local function ustawKamere()
	if kameraWolna then
		return
	end
	local poz, cel = pozycjaKamery()
	if not poz then
		return
	end
	kamera.CameraType = Enum.CameraType.Scriptable
	kamera.FieldOfView = D.kamera.fov
	kamera.CFrame = CFrame.lookAt(poz, cel)
end

-- sterowanie postacią wyłączone: gracz stoi na swoim miejscu, stuknięcia idą w arenę
task.spawn(function()
	local ok, modul = pcall(function()
		return require(gracz:WaitForChild("PlayerScripts"):WaitForChild("PlayerModule", 10))
	end)
	if ok and modul then
		pcall(function()
			modul:GetControls():Disable()
		end)
	end
end)

------------------------------------------------------------------ rzut: ekran → arena
local znacznik = Instance.new("Part")
znacznik.Name = "ZnacznikCelu"
znacznik.Shape = Enum.PartType.Cylinder
znacznik.Anchored = true
znacznik.CanCollide = false
znacznik.CanQuery = false
znacznik.CanTouch = false
znacznik.CastShadow = false
znacznik.Material = Enum.Material.Neon
znacznik.Color = Color3.fromHex(K.ty)
znacznik.Transparency = 0.45
znacznik.Size = Vector3.new(0.15, 3.2, 3.2)
znacznik.Parent = nil
local celPada = Vector2.new(0, 6)
local padAktywny = false

local function naArene(sx: number, sy: number, viewport: boolean?): Vector3?
	local promien = if viewport then kamera:ViewportPointToRay(sx, sy) else kamera:ScreenPointToRay(sx, sy)
	if promien.Direction.Y >= -1e-3 then
		return nil
	end
	local t = -promien.Origin.Y / promien.Direction.Y
	return promien.Origin + promien.Direction * t
end

local function wybierzGotowego(lista): number?
	local w = lista[wybrany]
	if w and w.stan == "gotowy" then
		return wybrany
	end
	for i, x in lista do
		if x.stan == "gotowy" then
			return i
		end
	end
	return nil
end

local function rzutW(x: number, z: number): boolean
	local r = math.sqrt(x * x + z * z)
	if r > R - D.rzut.margines then
		if r < D.scena.obrzeze_r[1] + 4 then
			ui:baner(D.ui.poza, Color3.fromHex("FF9A9A"), 1.1)
		end
		return false
	end
	if (gracz:GetAttribute("PA_Pet") or 0) > 0 then
		return false
	end
	local nr = wybierzGotowego(druzynaLista())
	if not nr then
		ui:baner(D.ui.odpoczywa, Color3.fromHex("FF9A9A"), 1.1)
		return false
	end
	wybrany = nr
	evAkcja:FireServer("rzut", nr, x, z)
	wyslane += 1
	E:pierscien(Vector3.new(x, 0.2, z), 1.8, Color3.fromHex(K.ty), 0.9)
	dzwiek("klik", 1.2)
	return true
end

local function rzutEkran(sx: number, sy: number): boolean
	local p = naArene(sx, sy)
	if not p then
		return false
	end
	return rzutW(p.X, p.Z)
end

UserInputService.InputBegan:Connect(function(wej: InputObject, przetworzone: boolean)
	if przetworzone then
		return
	end
	local typ = wej.UserInputType
	if typ == Enum.UserInputType.MouseButton1 or typ == Enum.UserInputType.Touch then
		padAktywny = false
		rzutEkran(wej.Position.X, wej.Position.Y)
	elseif typ == Enum.UserInputType.Keyboard then
		local k = wej.KeyCode
		if k == Enum.KeyCode.One or k == Enum.KeyCode.Two or k == Enum.KeyCode.Three then
			wybierz(if k == Enum.KeyCode.One then 1 elseif k == Enum.KeyCode.Two then 2 else 3)
		elseif k == Enum.KeyCode.Space or k == Enum.KeyCode.Q then
			umiejetnosc()
		end
	elseif typ == Enum.UserInputType.Gamepad1 then
		local k = wej.KeyCode
		padAktywny = true
		if k == Enum.KeyCode.ButtonA then
			rzutW(celPada.X, celPada.Y)
		elseif k == Enum.KeyCode.ButtonX then
			umiejetnosc()
		elseif k == Enum.KeyCode.ButtonL1 or k == Enum.KeyCode.ButtonR1 then
			local n = #druzynaLista()
			if n > 0 then
				wybierz(((wybrany - 1 + (if k == Enum.KeyCode.ButtonR1 then 1 else -1)) % n) + 1)
			end
		end
	end
end)

------------------------------------------------------------------ migawki stanu
local ostatniaMigawka = 0
local migawek = 0
evStan.OnClientEvent:Connect(function(b: buffer)
	if typeof(b) ~= "buffer" or buffer.len(b) < 14 then
		return
	end
	migawek += 1
	ostatniaMigawka = os.clock()
	local n = buffer.readu16(b, 8)
	krolId = buffer.readu16(b, 10)
	nagrodaKrola = buffer.readu16(b, 12)
	local widziane = {}
	for i = 1, n do
		local o = 14 + (i - 1) * 22
		if o + 22 > buffer.len(b) then
			break
		end
		local id = buffer.readu16(b, o)
		local nr = buffer.readu8(b, o + 2)
		local slot = buffer.readu8(b, o + 3)
		local x, z = buffer.readf32(b, o + 6), buffer.readf32(b, o + 10)
		widziane[id] = true
		local w = widoki[id]
		if not w then
			w = nowyWidok(id, nr, slot, x, z)
		end
		if w and not w.odlot then
			w.faza = buffer.readu8(b, o + 4)
			w.flagi = buffer.readu8(b, o + 5)
			if not w.lot then
				w.tx, w.tz = x, z
			end
			w.hp = buffer.readu16(b, o + 14) / 10
			w.hpMax = math.max(1, buffer.readu16(b, o + 16) / 10)
			w.pasek = buffer.readu8(b, o + 18) / 255
			w.zl = buffer.readu8(b, o + 19)
			w.tkier = buffer.readi16(b, o + 20) / 1000
			w.brak = 0
			if w.slot ~= slot then
				w.slot = slot
			end
		end
	end
	for id, w in widoki do
		if not widziane[id] and not w.odlot and not w.lot then
			w.brak += 1
			if w.brak >= 3 then
				usunWidok(w)
			end
		end
	end
end)

------------------------------------------------------------------ zdarzenia
local liczZdarzen: { [string]: number } = {}

local function slowo(): string
	local s = D.ui.slowa
	return s[math.random(1, #s)]
end

local function pozSlotu(slot: number): Vector3
	local s = D.sloty[slot]
	if s then
		return Vector3.new(s.poz[1], s.poz[2] + 4, s.poz[3])
	end
	return Vector3.new(0, 60, 0)
end

-- RING OUT: zsuwa się do fosy, plusk, gejzer w niebo, łukiem do właściciela (dziki — za trybunę)
local function odlotRingOut(w: Widok, z)
	local start = Vector3.new(z.x, 0, z.z)
	local kier = Vector3.new(z.kx, 0, z.kz)
	if kier.Magnitude < 0.1 then
		kier = Vector3.new(z.x, 0, z.z)
	end
	kier = kier.Unit
	local woda = start + kier * 4.5
	woda = Vector3.new(woda.X, D.scena.woda_y, woda.Z)
	local cel = if z.wl > 0 and not z.dziki then pozSlotu(z.wl) else (start.Unit * 90 + Vector3.new(0, 20, 0))
	local plusk, gejzer = false, false
	local t = 0
	w.odlot = function(dt: number): boolean
		t += dt
		local cf
		if t < 0.45 then
			local f = t / 0.45
			local p = start:Lerp(woda, f)
			p = Vector3.new(p.X, -f * f * (0 - D.scena.woda_y) + 1.2 * math.sin(f * math.pi), p.Z)
			cf = CFrame.new(p) * CFrame.Angles(f * 1.5, 0, f * 0.8)
		elseif t < 0.95 then
			if not plusk then
				plusk = true
				E:plask(woda + Vector3.new(0, 0.3, 0), Color3.fromRGB(150, 220, 255))
				E:slowo(woda + Vector3.new(0, 3, 0), D.ui.plusk, Color3.fromRGB(150, 220, 255), 0.9)
				dzwiek("plusk")
			end
			cf = CFrame.new(woda - Vector3.new(0, 3, 0))
		elseif t < 3.0 then
			if not gejzer then
				gejzer = true
				E:gejzer(woda)
				E:slowo(woda + Vector3.new(0, 8, 0), D.ui.ring_out, Color3.fromHex("FF6A3D"), 1.3)
				dzwiek("kryt", 0.8)
			end
			local f = (t - 0.95) / 2.05
			local p = woda:Lerp(cel, f)
			local h = 26 * math.sin(f * math.pi)
			p = Vector3.new(p.X, p.Y + h, p.Z)
			cf = CFrame.new(p) * CFrame.Angles(t * 9, t * 5, 0)
		else
			E:iskry(cel, Color3.fromRGB(255, 255, 255), 8, 0.6)
			return true
		end
		w.korzen.CFrame = cf
		w.krazek.Transparency = 1
		w.etykieta.Visible = false
		return false
	end
end

-- KO: gwiazdki, wirujący odlot w górę i poza dół
local function odlotKO(w: Widok, z)
	local start = Vector3.new(z.x, 0, z.z)
	local kier = Vector3.new(z.kx, 0, z.kz)
	if kier.Magnitude < 0.1 then
		kier = Vector3.new(math.random() - 0.5, 0, math.random() - 0.5)
	end
	kier = kier.Unit
	local cel = if z.wl > 0 and not z.dziki then pozSlotu(z.wl) else start + kier * 80 + Vector3.new(0, 10, 0)
	E:iskry(start + Vector3.new(0, 3, 0), Color3.fromHex(K.zloto), 16, 1.2)
	E:slowo(start + Vector3.new(0, 6, 0), D.ui.ko, Color3.fromHex("FFE14D"), 1.4)
	dzwiek("ko")
	local t = 0
	w.odlot = function(dt: number): boolean
		t += dt
		if t >= 2.0 then
			E:iskry(cel, Color3.fromRGB(255, 255, 255), 8, 0.6)
			return true
		end
		local f = t / 2.0
		local p = start:Lerp(cel, f)
		p = Vector3.new(p.X, p.Y + 30 * math.sin(f * math.pi), p.Z)
		w.korzen.CFrame = CFrame.new(p) * CFrame.Angles(t * 14, t * 3, t * 7)
		w.krazek.Transparency = 1
		w.etykieta.Visible = false
		return false
	end
end

local function zloteSlowo(poz: Vector3, ile: number)
	E:slowo(poz + Vector3.new(0, 4, 0), "+" .. L.format(ile) .. " G", Color3.fromHex(K.zloto), 1.0)
	local c = gracz.Character
	E:monety(poz, math.clamp(math.floor(ile / 5), 3, 10), c and c:FindFirstChild("HumanoidRootPart"), function()
		dzwiek("monety")
	end)
end

local function poz3(w: Widok?, x: number, z: number): Vector3
	if w then
		return Vector3.new(w.x, w.y, w.z)
	end
	return Vector3.new(x, 0, z)
end

local function zdarzenie(z)
	liczZdarzen[z.t] = (liczZdarzen[z.t] or 0) + 1
	local moj = mojSlot()
	if z.t == "rzut" then
		local w = widoki[z.id] or nowyWidok(z.id, z.nr, if z.dziki then 0 else z.wl, z.x, z.z)
		if w then
			local od = Vector3.new(z.x0, z.y0, z.z0)
			local h = D.rzut.wysokosc + (od - Vector3.new(z.x, 0, z.z)).Magnitude * 0.12
			w.lot = { t = 0, czas = z.czas, od = od, x = z.x, z = z.z, h = h }
			w.tx, w.tz = z.x, z.z
			w.korzen.CFrame = CFrame.new(od)
			if z.dziki then
				E:gejzer(od)
			end
			if z.wl == moj and not z.dziki then
				E:pierscien(Vector3.new(z.x, 0.2, z.z), 2.6, Color3.fromHex(K.ty), z.czas + 0.3)
			end
		end
	elseif z.t == "ladowanie" then
		local w = widoki[z.id]
		E:plask(Vector3.new(z.x, 0.1, z.z), Color3.fromRGB(220, 200, 160))
		if w then
			w.trafienie = 0.2
		end
	elseif z.t == "cios" then
		local w = widoki[z.b]
		local p = poz3(w, z.x, z.z) + Vector3.new(0, 2, 0)
		E:iskry(p, if z.k then Color3.fromHex("FFE14D") else Color3.fromRGB(255, 250, 230), if z.k then 12 else 5, if z.k then 1.2 else 0.7)
		if z.o > 0 then
			E:liczba(p + Vector3.new(0, 1.5, 0), tostring(z.o), if z.k then Color3.fromHex("FFE14D") else Color3.fromRGB(255, 255, 255))
		end
		if z.k then
			E:slowo(p + Vector3.new(0, 3, 0), D.ui.kryt, Color3.fromHex("FFE14D"), 1.0)
			dzwiek("kryt")
		elseif (z.v or 0) > 30 then
			E:slowo(p + Vector3.new(0, 3, 0), slowo(), Color3.fromHex("FF8A3D"), 0.85)
			dzwiek("cios", 0.9)
		else
			dzwiek("cios", 1 + math.random() * 0.25)
		end
		if w then
			w.trafienie = 0.18
		end
	elseif z.t == "umiejetnosc" then
		local w = widoki[z.id]
		local p = poz3(w, z.x, z.z)
		local kol = Color3.fromHex(if w and w.slot == moj and w.slot > 0 then K.ty else "FF8A3D")
		E:slowo(p + Vector3.new(0, 7, 0), z.nazwa .. "!", kol, 1.15)
		dzwiek("umiejetnosc")
		if z.typ == "fala" then
			E:fala(p, z.r)
		elseif z.typ == "ogluszenie" then
			E:chmura(p, z.r)
		elseif z.typ == "zamrozenie" then
			local c = z.cel and widoki[z.cel]
			if c then
				E:lod(Vector3.new(c.x, 0, c.z))
				E:jezyk(p + Vector3.new(0, 3, 0), Vector3.new(c.x, 2.5, c.z))
			end
		elseif z.typ == "podpalenie" then
			E:plomien(p, Vector3.new(z.kx, 0, z.kz), z.zasieg, z.kat)
		elseif z.typ == "jezyk" then
			if z.x1 then
				E:jezyk(p + Vector3.new(0, 2.5, 0), Vector3.new(z.x1, 2, z.z1))
			end
		elseif z.typ == "skorupa" then
			E:pierscien(p, (w and w.Pd.promien or 2) + 1.2, Color3.fromRGB(120, 230, 120), z.czas)
		elseif z.typ == "skok" then
			if w then
				w.skok = { t = 0, czas = z.czas, h = z.wysokosc }
			end
			E:pierscien(Vector3.new(z.x1, 0.2, z.z1), z.r, Color3.fromHex("FF4D4D"), z.czas + 0.2)
		elseif z.typ == "szarza" then
			if w then
				local tr = E:smuga(w.korzen, Color3.fromRGB(255, 230, 160), 1.6)
				task.delay(1.2, function()
					tr:Destroy()
				end)
			end
		end
		if w and w.slot == moj and moj > 0 then
			uzylUmiejetnosci = true
		end
	elseif z.t == "ladowanie_skoku" then
		local p = Vector3.new(z.x, 0, z.z)
		E:fala(p, z.r)
		E:slowo(p + Vector3.new(0, 5, 0), "BOOM!", Color3.fromHex("FF6A3D"), 1.3)
		dzwiek("kryt", 0.7)
	elseif z.t == "odbicie_slime" then
		local w = widoki[z.id]
		if w then
			w.x, w.z, w.tx, w.tz = z.x, z.z, z.x, z.z
			w.trafienie = 0.2
		end
	elseif z.t == "odbicie" then
		E:iskry(Vector3.new(z.x, 2, z.z), Color3.fromRGB(120, 230, 120), 8, 0.8)
	elseif z.t == "ringout" or z.t == "ko" then
		local w = widoki[z.id]
		if w and not w.odlot then
			w.lot = nil
			if z.t == "ringout" then
				odlotRingOut(w, z)
			else
				odlotKO(w, z)
			end
		end
		local p = Vector3.new(z.x, 0, z.z)
		local nazwa = if z.t == "ringout" then D.ui.ring_out else D.ui.ko
		if z.wl == moj and not z.dziki and moj > 0 then
			ui:baner(nazwa, Color3.fromHex("FF6A6A"), 1.6)
		elseif z.przez == moj and moj > 0 and (z.premia + z.nagroda) > 0 then
			ui:baner(if z.nagroda > 0 then D.ui.nagroda .. " +" .. L.format(z.nagroda) .. "!" else nazwa .. " +" .. L.format(z.premia),
				Color3.fromHex(K.zloto), 1.6)
			zloteSlowo(p, z.premia + z.nagroda)
		end
	elseif z.t == "krol" then
		if z.wl == moj and not z.dziki and moj > 0 then
			ui:baner(D.ui.krol, Color3.fromHex(K.zloto), 1.6)
			dzwiek("krol")
		else
			ui:baner(D.ui.nowy_krol, Color3.fromHex(K.zloto), 1.0)
		end
	elseif z.t == "zloto" then
		local w = widoki[z.id]
		if w then
			E:liczba(Vector3.new(w.x, w.y + w.Pd.wysokosc + 1, w.z), "+" .. L.naSekunde(z.ile), Color3.fromHex(K.zloto))
		end
	elseif z.t == "odmowa" then
		if z.powod == "pelna" then
			ui:baner(D.ui.pelna, Color3.fromHex("FF9A9A"), 1.2)
		elseif z.powod == "poza" then
			ui:baner(D.ui.poza, Color3.fromHex("FF9A9A"), 1.2)
		elseif z.powod == "odpoczywa" then
			ui:baner(D.ui.odpoczywa, Color3.fromHex("FF9A9A"), 1.2)
		end
	end
end

evZdarzenia.OnClientEvent:Connect(function(lista)
	if type(lista) ~= "table" then
		return
	end
	for _, z in lista do
		if type(z) == "table" and type(z.t) == "string" then
			local ok, blad = pcall(zdarzenie, z)
			if not ok then
				warn(P .. "zdarzenie " .. z.t .. ": " .. tostring(blad))
			end
		end
	end
end)

------------------------------------------------------------------ pętla rysowania
local pomiar = { klatek = 0, suma = 0, maks = 0, petlaSuma = 0, petlaMaks = 0 }
local doUI = 0
local doNazw = 0
local tGlob = 0

local function odswiezNazwy()
	for _, plr in Players:GetPlayers() do
		local s = plr:GetAttribute("PA_Slot")
		if type(s) == "number" and s > 0 then
			nazwySlotow[s] = plr:GetAttribute("PA_Nazwa") or ""
		end
	end
end

local function rysujWidok(w: Widok, dt: number)
	if w.odlot then
		if w.odlot(dt) then
			usunWidok(w)
		end
		return
	end
	local Pd = w.Pd
	local y = 0
	local obrot = CFrame.new()
	if w.lot then
		local l = w.lot
		l.t += dt
		local f = math.clamp(l.t / l.czas, 0, 1)
		local p = l.od:Lerp(Vector3.new(l.x, 0, l.z), f)
		p += Vector3.new(0, l.h * 4 * f * (1 - f), 0)
		w.x, w.z, y = p.X, p.Z, p.Y
		obrot = CFrame.Angles(-f * math.pi * 2, 0, 0)
		if f >= 1 then
			w.lot = nil
			w.x, w.z = l.x, l.z
		end
	else
		local a = 1 - math.exp(-dt * 14)
		local dx, dz = w.tx - w.x, w.tz - w.z
		if dx * dx + dz * dz > 400 then
			w.x, w.z = w.tx, w.tz
		else
			w.x += dx * a
			w.z += dz * a
		end
		local predkosc = math.sqrt(dx * dx + dz * dz)
		if w.skok then
			local s = w.skok
			s.t += dt
			local f = math.clamp(s.t / s.czas, 0, 1)
			y = s.h * 4 * f * (1 - f)
			obrot = CFrame.Angles(f * math.pi * 2, 0, 0)
			if f >= 1 then
				w.skok = nil
			end
		elseif predkosc > 0.12 and bit32.band(w.flagi, 2) == 0 then
			y = math.abs(math.sin(tGlob * 10 + w.faza0)) * 0.7
		end
		-- kierunek: płynnie do kąta z serwera
		local dk = (w.tkier - w.kier + math.pi) % (2 * math.pi) - math.pi
		w.kier += dk * math.min(1, dt * 10)
	end
	w.y = y
	local cf = CFrame.new(w.x, y, w.z) * CFrame.Angles(0, w.kier + math.pi, 0) * obrot
	if w.trafienie > 0 then
		w.trafienie -= dt
		cf *= CFrame.Angles(-math.sin(math.max(0, w.trafienie) / 0.2 * math.pi) * 0.35, 0, 0)
	end
	if bit32.band(w.flagi, 1) ~= 0 then
		cf *= CFrame.Angles(0, 0, math.sin(tGlob * 18) * 0.25)
	end
	w.korzen.CFrame = cf
	w.krazek.CFrame = CFrame.new(w.x, 0.28, w.z) * CFrame.Angles(0, 0, math.pi / 2)
	w.krazek.Transparency = if w.lot then 1 else (if w.slot > 0 and w.slot == mojSlot() then 0.15 elseif w.slot > 0 then 0.35 else 0.6)
	-- stany: lód, skorupa, ogień, ogłuszenie (wypełnienie obrysu)
	local f = w.flagi
	if bit32.band(f, 2) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(150, 225, 255)
		w.hl.FillTransparency = 0.35
	elseif bit32.band(f, 4) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(110, 230, 110)
		w.hl.FillTransparency = 0.45
	elseif bit32.band(f, 8) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(255, 140, 40)
		w.hl.FillTransparency = 0.45 + math.sin(tGlob * 20) * 0.15
	elseif bit32.band(f, 1) ~= 0 then
		w.hl.FillColor = Color3.fromRGB(255, 240, 120)
		w.hl.FillTransparency = 0.55
	else
		w.hl.FillTransparency = 1
	end
	-- napis i pasek życia (warstwa 2D)
	local top = Vector3.new(w.x, y + Pd.wysokosc + (if krolId == w.id then 5.2 else 0.8), w.z)
	local v, na = kamera:WorldToViewportPoint(top)
	w.etykieta.Visible = na and not w.lot
	if na then
		w.etykieta.Position = UDim2.fromOffset(v.X, v.Y)
		local fz = math.clamp(w.hp / w.hpMax, 0, 1)
		w.pasekZ.Size = UDim2.fromScale(fz, 1)
		w.pasekZ.BackgroundColor3 = Color3.fromHex(if fz < 0.35 then K.zycie_nisko else K.zycie)
		local moj = w.slot > 0 and w.slot == mojSlot()
		if moj then
			w.napis.Text = if w.zl > 0 then D.ui.ty .. "  " .. string.format(D.ui.na_s, L.naSekunde(w.zl)) else D.ui.ty
		elseif w.slot > 0 then
			w.napis.Text = nazwySlotow[w.slot] or ""
		end
		local krol = krolId == w.id
		w.nagrodaTekst.Visible = krol
		if krol then
			w.nagrodaTekst.Text = D.ui.nagroda .. " " .. L.format(nagrodaKrola)
		end
	end
end

RunService.RenderStepped:Connect(function(dt: number)
	local t0 = os.clock()
	tGlob += dt
	ustawKamere()
	for _, w in widoki do
		rysujWidok(w, dt)
	end
	-- korona nad królem
	local k = widoki[krolId]
	if k and not k.odlot and not k.lot then
		if korona.Parent ~= lokalne then
			korona.Parent = lokalne
		end
		korona:PivotTo(CFrame.new(k.x, k.y + k.Pd.wysokosc + 1.6 + math.sin(tGlob * 4) * 0.25, k.z) * CFrame.Angles(0, tGlob * 1.5, 0))
	elseif korona.Parent then
		korona.Parent = nil
	end
	-- celownik pada i podgląd celu pod myszą
	if padAktywny then
		local st = UserInputService:GetGamepadState(Enum.UserInputType.Gamepad1)
		for _, s in st do
			if s.KeyCode == Enum.KeyCode.Thumbstick1 and s.Position.Magnitude > 0.2 then
				local _, cel = pozycjaKamery()
				local poz = select(1, pozycjaKamery())
				if poz and cel then
					local przod = Vector3.new(cel.X - poz.X, 0, cel.Z - poz.Z).Unit
					local prawo = Vector3.new(-przod.Z, 0, przod.X)
					local d = (prawo * s.Position.X + przod * s.Position.Y) * dt * 26
					local n = celPada + Vector2.new(d.X, d.Z)
					if n.Magnitude > R - D.rzut.margines then
						n = n.Unit * (R - D.rzut.margines)
					end
					celPada = n
				end
			end
		end
		znacznik.Parent = lokalne
		znacznik.CFrame = CFrame.new(celPada.X, 0.3, celPada.Y) * CFrame.Angles(0, 0, math.pi / 2)
	elseif not dotyk and (gracz:GetAttribute("PA_Pet") or 0) == 0 then
		local m = UserInputService:GetMouseLocation()
		local p = naArene(m.X, m.Y, true)
		if p and (p.X * p.X + p.Z * p.Z) <= (R - D.rzut.margines) ^ 2 then
			znacznik.Parent = lokalne
			znacznik.CFrame = CFrame.new(p.X, 0.3, p.Z) * CFrame.Angles(0, 0, math.pi / 2)
		else
			znacznik.Parent = nil
		end
	else
		znacznik.Parent = nil
	end
	E:krok(dt)
	ui:krok(dt)
	-- ekran (10 razy na sekundę)
	doUI -= dt
	if doUI <= 0 then
		doUI = 0.1
		doNazw -= 0.1
		if doNazw <= 0 then
			doNazw = 1
			odswiezNazwy()
		end
		ui:zloto(gracz:GetAttribute("PA_Zloto") or 0, gracz:GetAttribute("PA_GS") or 0)
		local lista = druzynaLista()
		ui:druzyna(lista)
		local mojPet = widoki[gracz:GetAttribute("PA_Pet") or 0]
		if mojPet and not mojPet.odlot then
			local A = mojPet.Pd.umiejetnosc
			ui:umiejetnosc(not mojPet.lot, mojPet.pasek, A.nazwa)
			ui:pet(true, mojPet.Pd.nazwa, nil, mojPet.hp, mojPet.hpMax, mojPet.pasek)
		else
			ui:umiejetnosc(false, 0, nil)
			ui:pet(false)
		end
		local gotowych, najblizej = 0, math.huge
		for _, w in lista do
			if w.stan == "gotowy" then
				gotowych += 1
			elseif w.stan == "odpoczynek" then
				najblizej = math.min(najblizej, w.zostalo)
			end
		end
		local bezPeta = (gracz:GetAttribute("PA_Pet") or 0) == 0
		if bezPeta and (gotowych > 0 or not gracz:GetAttribute("PA_Rzucil")) then
			ui:podpowiedz(if padAktywny then D.ui.podpowiedz_pad elseif dotyk or ui.opcje.emulacja then D.ui.podpowiedz_dotyk
				else D.ui.podpowiedz_mysz)
		elseif bezPeta and najblizej < math.huge then
			ui:podpowiedz(string.format(D.ui.nastepny, najblizej))
		elseif mojPet and mojPet.pasek >= 1 and not uzylUmiejetnosci then
			ui:podpowiedz(D.ui.podpowiedz_umiejetnosc)
		else
			ui:podpowiedz(nil)
		end
	end
	local dtP = os.clock() - t0
	pomiar.klatek += 1
	pomiar.suma += dt
	pomiar.maks = math.max(pomiar.maks, dt)
	pomiar.petlaSuma += dtP
	pomiar.petlaMaks = math.max(pomiar.petlaMaks, dtP)
end)

-- napisy stref na podłodze (x5, x2, x1) obrócone do kamery tego gracza (lokalnie)
task.spawn(function()
	while mojSlot() == 0 do
		task.wait(0.2)
	end
	local s = D.sloty[mojSlot()]
	local sc = kontener:FindFirstChild("Scena")
	local ar = sc and sc:FindFirstChild("Arena")
	if s and ar then
		for _, d in ar:GetChildren() do
			if d.Name == "NapisStrefy" and d:IsA("BasePart") then
				d.CFrame = CFrame.new(d.Position) * CFrame.Angles(0, s.katKamery - math.pi / 2, 0)
			end
		end
	end
end)

kontener:SetAttribute("KlientGotowy", true)
print(P .. "klient gotowy")

------------------------------------------------------------------ haczyki prób
-- kadr: rzut 48 punktów krawędzi areny przy obecnej kamerze dla ekranu szer × wys (ułamki 0–1)
local function kadr(szer: number, wys: number)
	local poz, cel = pozycjaKamery()
	if not poz or not cel then
		return nil
	end
	local cf = CFrame.lookAt(poz, cel)
	local t = math.tan(math.rad(D.kamera.fov / 2))
	local asp = szer / wys
	local xs0, xs1, ys0, ys1 = 1, 0, 1, 0
	for i = 0, 47 do
		local a = i / 48 * math.pi * 2
		local p = cf:PointToObjectSpace(Vector3.new(math.sin(a) * R, 0, math.cos(a) * R))
		local x = 0.5 + p.X / (-p.Z * t * asp) / 2
		local y = 0.5 - p.Y / (-p.Z * t) / 2
		xs0, xs1, ys0, ys1 = math.min(xs0, x), math.max(xs1, x), math.min(ys0, y), math.max(ys1, y)
	end
	return { x = { xs0, xs1 }, y = { ys0, ys1 } }
end

sterowanie.OnInvoke = function(polecenie: string, a: any, b: any)
	if polecenie == "stan" then
		local lista = {}
		for id, w in widoki do
			table.insert(lista, { id = id, x = w.x, z = w.z, y = w.y, slot = w.slot, lot = w.lot ~= nil, odlot = w.odlot ~= nil,
				hp = w.hp, etykieta = w.etykieta.Visible, napis = w.napis.Text })
		end
		local z, n = dzwiekiZaladowane()
		local v = kamera.ViewportSize
		return {
			gotowy = true, slot = mojSlot(), widokow = #lista, widoki = lista, czesciWidokow = czesciWidokow, migawek = migawek,
			ui = ui:stan(), kamera = { typ = kamera.CameraType.Name, fov = kamera.FieldOfView, poz = { kamera.CFrame.X, kamera.CFrame.Y, kamera.CFrame.Z } },
			viewport = { v.X, v.Y }, kadr = kadr(v.X, v.Y), zdarzenia = liczZdarzen, efektow = E:ile(), wyslane = wyslane,
			dzwiekow = graneDzwieki, dzwiekiZaladowane = z, dzwiekiRazem = n, krol = krolId, korona = korona.Parent ~= nil,
			klatki = pomiar.klatek, srKlatki = if pomiar.klatek > 0 then pomiar.suma / pomiar.klatek else 0, maksKlatki = pomiar.maks,
			srPetli = if pomiar.klatek > 0 then pomiar.petlaSuma / pomiar.klatek else 0, maksPetli = pomiar.petlaMaks,
			wybrany = wybrany, dotyk = dotyk,
		}
	elseif polecenie == "rzut" then
		-- ta sama droga co stuknięcie: punkt świata → punkt ekranu → promień → arena
		local v, na = kamera:WorldToScreenPoint(Vector3.new(a, 0, b))
		if not na then
			return { wyslano = false, naEkranie = false }
		end
		return { wyslano = rzutEkran(v.X, v.Y), sx = v.X, sy = v.Y }
	elseif polecenie == "umiejetnosc" then
		ostatniaUmiejetnosc = 0
		umiejetnosc()
		return true
	elseif polecenie == "wybierz" then
		wybierz(a)
		return true
	elseif polecenie == "emulacja" then
		kontener:SetAttribute("EmulacjaEkranu", a)
		zbudujUI()
		E.skala = skalaNapisow()
		for _, w in widoki do
			if not w.odlot then
				usunWidok(w)
			end
		end
		return true
	elseif polecenie == "pomiar_zeruj" then
		pomiar = { klatek = 0, suma = 0, maks = 0, petlaSuma = 0, petlaMaks = 0 }
		return true
	elseif polecenie == "kamera_wolna" then
		kameraWolna = a == true
		if not kameraWolna then
			ustawKamere()
		end
		return true
	elseif polecenie == "kadr" then
		return kadr(a, b)
	end
	return nil
end
