--[[
	KlientStanu — kliencka połowa „stanu gracza” (Script, RunContext = Client, w kontenerze Workspace/StanGracza).
	Niczego nie liczy i nie wysyła liczb (D-016). Trzy rzeczy (trzecia: komunikat "przegrana", kara, doświadczenie →
	napis „Przegrana: −N Złota, +M doświadczenia” na dole ekranu jak premia peta — 17.11.2026, propozycja D-098):
		1. gdy HUD Pawła (PlayerGui.HUD) znów jest włączony — a odtwarzacz walki chowa go na czas walki — zgłasza
		   serwerowi "pokaz": łup z zakończonej walki trafia wtedy do atrybutów i HUD sam go odlicza;
		2. komunikat serwera "awans", poziom, ile → krótki baner „POZIOM N” (własny ScreenGui D.baner.gui, pokazywany
		   dopiero, gdy HUD widać, więc nie wchodzi na ekran walki ani na wybór klasy) i dźwięk awansu: odcinek
		   "awans" z Workspace/DzwiekGra/Moduly/KatalogDzwiekow, gdy arkusz jest wgrany, inaczej wbudowany ton.
	Baner to TYMCZASOWE GUI tego pakietu (docelowe pop-upy projektuje Paweł, D-093). Każdy pokaz to nowy ScreenGui,
	niszczony po czasie — odtwarzacz walki przywraca po walce GUI, które schował, więc wyłączony baner by wrócił.
]]
if not game:GetService("RunService"):IsStudio() then
	return
end

local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local SoundService = game:GetService("SoundService")

local kontener = script.Parent
local D = require(kontener:WaitForChild("Moduly"):WaitForChild("DaneStanu"))
local zdarzenia: RemoteEvent = kontener:WaitForChild("Zdalne"):WaitForChild("ZdarzeniaStanu")
local gracz = Players.LocalPlayer
local playerGui = gracz:WaitForChild("PlayerGui")
local B = D.baner
local P = D.prefiks

local hud: ScreenGui? = nil
local hudSprawdzony = false
local kolejka = {}
local trwa = false

local function hudWidac(): boolean
	if not hudSprawdzony then
		return false
	end
	return hud == nil or (hud.Parent ~= nil and hud.Enabled)
end

------------------------------------------------------------------ dźwięk awansu
local function dzwiekZKatalogu(): boolean
	local k = workspace:FindFirstChild(D.dzwiek.kontener)
	local m = k and k:FindFirstChild("Moduly")
	m = m and m:FindFirstChild(D.dzwiek.modul)
	if not m or not m:IsA("ModuleScript") then
		return false
	end
	local ok, kat = pcall(require, m)
	if not ok or type(kat) ~= "table" or type(kat.arkusz) ~= "table" or type(kat.zdarzenia) ~= "table"
		or type(kat.efekty) ~= "table" then
		return false
	end
	local id = k:GetAttribute("TestArkuszId")
	if id == nil then
		id = kat.arkusz.id
	end
	local adres = if type(id) == "number" and id > 0 then "rbxassetid://" .. tostring(math.floor(id))
		elseif type(id) == "string" and id ~= "" then id
		else nil
	local zd = kat.zdarzenia[D.dzwiek.zdarzenie]
	local e = zd and kat.efekty[zd.efekt]
	if not adres or type(e) ~= "table" or type(e.poczatek) ~= "number" or type(e.koniec) ~= "number" then
		return false
	end
	local s = Instance.new("Sound")
	s.Name = "StanGraczaAwans"
	s.SoundId = adres
	s.Volume = (e.glosnosc or 1) * (kat.arkusz.glosnosc or 1)
	pcall(function()
		s.PlaybackRegionsEnabled = true
		s.PlaybackRegion = NumberRange.new(e.poczatek, e.koniec)
	end)
	s.TimePosition = e.poczatek
	s.Parent = SoundService
	s:Play()
	task.delay(e.koniec - e.poczatek + 0.1, function()
		s:Destroy()
	end)
	return true
end

local function dzwiekWbudowany()
	for i, nuta in D.dzwiek.nuty do
		task.delay((i - 1) * D.dzwiek.odstep_s, function()
			local s = Instance.new("Sound")
			s.Name = "StanGraczaAwans"
			s.SoundId = D.dzwiek.wbudowany
			s.Volume = D.dzwiek.glosnosc
			s.PlaybackSpeed = nuta
			s.Parent = SoundService
			s:Play()
			task.delay(1, function()
				s:Destroy()
			end)
		end)
	end
end

local function zagrajAwans()
	local ok, zagrane = pcall(dzwiekZKatalogu)
	if not ok or not zagrane then
		pcall(dzwiekWbudowany)
	end
end

------------------------------------------------------------------ baner „POZIOM N”
local function napis(rodzic: Instance, nazwa: string, tekst: string, y: number, wys: number, kolor: string): TextLabel
	local l = Instance.new("TextLabel")
	l.Name = nazwa
	l.AnchorPoint = Vector2.new(0.5, 0)
	l.Position = UDim2.fromScale(0.5, y)
	l.Size = UDim2.fromScale(1, wys)
	l.BackgroundTransparency = 1
	l.Font = Enum.Font.LuckiestGuy
	l.TextScaled = true
	l.Text = tekst
	l.TextColor3 = Color3.fromHex(kolor)
	local obrys = Instance.new("UIStroke")
	obrys.Color = Color3.fromHex(B.kolor_obrysu)
	obrys.Thickness = 3
	obrys.Parent = l
	l.Parent = rodzic
	return l
end

local function pokazBaner(poziom: number, ile: number)
	local gui = Instance.new("ScreenGui")
	gui.Name = B.gui
	gui.ResetOnSpawn = false
	gui.IgnoreGuiInset = true
	gui.DisplayOrder = B.kolejnosc
	gui:SetAttribute("Poziom", poziom)
	local ramka = Instance.new("Frame")
	ramka.Name = "Baner"
	ramka.AnchorPoint = Vector2.new(0.5, 0.5)
	ramka.Position = UDim2.fromScale(0.5, B.wysokosc)
	ramka.Size = UDim2.fromOffset(B.szer_px, B.wys_px)
	ramka.BackgroundTransparency = 1
	ramka.Parent = gui
	local skala = Instance.new("UIScale")
	skala.Scale = 0.2
	skala.Parent = ramka
	napis(ramka, "Tytul", string.format(B.tekst, poziom), 0, 0.68, B.kolor_tekstu)
	napis(ramka, "Podpis", if ile > 1 then string.format(B.podpis_wiele, ile) else B.podpis, 0.68, 0.32, B.kolor_podpisu)
	gui.Parent = playerGui
	TweenService:Create(skala, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	zagrajAwans()
	task.delay(B.czas_s, function()
		local znik = TweenService:Create(skala, TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.01 })
		znik:Play()
		znik.Completed:Wait()
		gui:Destroy()
	end)
end

local function nastepny()
	if trwa or #kolejka == 0 or not hudWidac() then
		return
	end
	trwa = true
	local wpis = table.remove(kolejka, 1)
	local ok, blad = pcall(pokazBaner, wpis.poziom, wpis.ile)
	if not ok then
		warn(P .. "baner awansu: " .. tostring(blad))
	end
	task.delay(B.czas_s + 0.4, function()
		trwa = false
		nastepny()
	end)
end

------------------------------------------------------------------ komunikat po przegranej (17.11.2026, propozycja D-098)
-- napis na dole ekranu jak premia peta (swiat/pety_proba), tuż nad nim; własny ScreenGui na każdy pokaz, niszczony po
-- czasie; gdy HUD schowany (walka) — czeka na HUD
local K = D.kara
local czekajacyKomunikat: string? = nil
local ostatniKomunikat: ScreenGui? = nil

local function pokazKomunikat(tekst: string)
	if ostatniKomunikat then
		ostatniKomunikat.Enabled = false -- nowszy zastępuje (stary i tak zniknie po swoim czasie)
	end
	local gui = Instance.new("ScreenGui")
	gui.Name = "StanGraczaKomunikat"
	gui.ResetOnSpawn = false
	gui.DisplayOrder = 26
	local l = Instance.new("TextLabel")
	l.Name = "Tekst"
	l.AnchorPoint = Vector2.new(0.5, 1)
	l.Position = UDim2.new(0.5, 0, 1, -200)
	l.Size = UDim2.fromOffset(0, 44)
	l.AutomaticSize = Enum.AutomaticSize.X
	l.BackgroundColor3 = Color3.fromHex("1D1916")
	l.BackgroundTransparency = 0.15
	l.TextColor3 = Color3.fromHex("FFB4A6")
	l.Font = Enum.Font.GothamBold
	l.TextSize = 20
	l.Text = "  " .. tekst .. "  "
	local obrys = Instance.new("UIStroke")
	obrys.Color = Color3.fromHex("FFC94A")
	obrys.Thickness = 2
	obrys.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	obrys.Parent = l
	l.Parent = gui
	gui.Parent = playerGui
	ostatniKomunikat = gui
	kontener:SetAttribute("KlientOstatniKomunikat", tekst) -- lokalnie u klienta (próby w Play)
	task.delay(K.czas_s, function()
		gui:Destroy()
	end)
end

local function pokazCzekajacy()
	if czekajacyKomunikat and hudWidac() then
		local t = czekajacyKomunikat
		czekajacyKomunikat = nil
		local ok, blad = pcall(pokazKomunikat, t)
		if not ok then
			warn(P .. "komunikat przegranej: " .. tostring(blad))
		end
	end
end

zdarzenia.OnClientEvent:Connect(function(polecenie: any, kara: any, xp: any)
	if polecenie ~= "przegrana" or type(kara) ~= "number" or type(xp) ~= "number" then
		return
	end
	czekajacyKomunikat = if kara > 0 then string.format(K.komunikat, math.floor(kara), math.floor(xp))
		else string.format(K.komunikat_bez_zlota, math.floor(xp))
	pokazCzekajacy()
end)

zdarzenia.OnClientEvent:Connect(function(polecenie: any, poziom: any, ile: any)
	if polecenie ~= "awans" or type(poziom) ~= "number" then
		return
	end
	-- kilka awansów, zanim baner się pokazał: jeden baner z najwyższym poziomem i sumą
	local razem = if type(ile) == "number" and ile >= 1 then math.floor(ile) else 1
	if #kolejka > 0 then
		razem += kolejka[#kolejka].ile
		kolejka[#kolejka] = { poziom = math.floor(poziom), ile = razem }
	else
		table.insert(kolejka, { poziom = math.floor(poziom), ile = razem })
	end
	nastepny()
end)

------------------------------------------------------------------ HUD Pawła: koniec ekranu walki = pokaż łup
task.spawn(function()
	local h = playerGui:WaitForChild(D.hud.gui, D.hud.czekaj_s)
	if h and h:IsA("ScreenGui") then
		hud = h
		h:GetPropertyChangedSignal("Enabled"):Connect(function()
			if h.Enabled then
				zdarzenia:FireServer("pokaz")
				task.delay(B.opoznienie_po_hud_s, nastepny)
				task.delay(B.opoznienie_po_hud_s, pokazCzekajacy)
			end
		end)
	else
		warn(P .. "brak PlayerGui." .. D.hud.gui .. " — łup pokaże się po czasie walki, baner bez czekania na HUD")
	end
	hudSprawdzony = true
	if hud == nil or hud.Enabled then
		zdarzenia:FireServer("pokaz")
	end
	nastepny()
	pokazCzekajacy()
end)

kontener:SetAttribute("KlientStanuGotowy", true)
