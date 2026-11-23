--[[
	TreningAFKClient — okno treningu AFK (D-141; gałąź pawel/diamenty-afk). Serwer: src/server/TreningAFK.server.luau.
	Druga wersja (Paweł 23.11): postać sama robi powtórzenia, pasek = D.powtorzenNaPasek powtórzeń (podziałki),
	po pełnym pasku od razu „+N STR”. Klikać nie trzeba. Co kilka sekund wyskakuje skill check (okrągły przycisk
	w losowym miejscu) — kliknięty na czas daje chwilowe ×2 (decyduje serwer).
	Okno budowane w kodzie (TYMCZASOWE — docelowy wygląd z Figmy). Rekwizyt stanowiska (hantle, sztanga, księga…)
	unosi się i opada w rytm powtórzeń — tylko u gracza.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")

local D = require(RS:WaitForChild("Shared"):WaitForChild("TreningAFKDane"))
local Z = RS:WaitForChild("TreningAFK") :: RemoteEvent
local player = Players.LocalPlayer

local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local CIEMNY = Color3.fromRGB(26, 20, 16)

local function obrys(rodzic: Instance, grubosc: number)
	local s = Instance.new("UIStroke")
	s.Color = CIEMNY
	s.Thickness = grubosc
	s.Parent = rodzic
	return s
end
local function rog(rodzic: Instance, r: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r, 0)
	c.Parent = rodzic
end
local function napis(rodzic: Instance, nazwa: string, pos: UDim2, size: UDim2, kolor: Color3): TextLabel
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.Position, t.Size = pos, size
	t.FontFace = FONT
	t.TextScaled = true
	t.TextColor3 = kolor
	t.Text = ""
	obrys(t, 2)
	t.Parent = rodzic
	return t
end

------------------------------------------------------------ okno
local gui = Instance.new("ScreenGui")
gui.Name = "TreningAFK"
gui.ResetOnSpawn = false
gui.IgnoreGuiInset = true
gui.DisplayOrder = 15
gui.Enabled = false

local panel = Instance.new("Frame")
panel.Name = "Panel"
panel.AnchorPoint = Vector2.new(0.5, 1)
panel.Position = UDim2.new(0.5, 0, 1, -16)
panel.Size = UDim2.fromScale(0.42, 0.17)
panel.BackgroundColor3 = Color3.fromRGB(58, 40, 30)
panel.BackgroundTransparency = 0.08
panel.Parent = gui
rog(panel, 0.18)
obrys(panel, 3)
local ar = Instance.new("UIAspectRatioConstraint")
ar.AspectRatio = 4.2
ar.Parent = panel
local mx = Instance.new("UISizeConstraint")
mx.MinSize = Vector2.new(300, 0)
mx.MaxSize = Vector2.new(620, 160)
mx.Parent = panel

local tytul = napis(panel, "Tytul", UDim2.fromScale(0.04, 0.07), UDim2.fromScale(0.56, 0.28), Color3.fromRGB(252, 227, 176))
tytul.TextXAlignment = Enum.TextXAlignment.Left
local przyrostL = napis(panel, "Przyrost", UDim2.fromScale(0.62, 0.07), UDim2.fromScale(0.34, 0.28), Color3.fromRGB(140, 232, 101))
przyrostL.TextXAlignment = Enum.TextXAlignment.Right

local tor = Instance.new("Frame")
tor.Name = "Tor"
tor.Position = UDim2.fromScale(0.04, 0.42)
tor.Size = UDim2.fromScale(0.74, 0.3)
tor.BackgroundColor3 = Color3.fromRGB(14, 10, 16)
tor.ClipsDescendants = true
tor.Parent = panel
rog(tor, 0.4)
obrys(tor, 2)
local wyp = Instance.new("Frame")
wyp.Name = "Wypelnienie"
wyp.Size = UDim2.fromScale(0, 1)
wyp.BackgroundColor3 = Color3.fromRGB(120, 210, 120)
wyp.Parent = tor
rog(wyp, 0.4)
local polysk = Instance.new("Frame")
polysk.BackgroundColor3 = Color3.new(1, 1, 1)
polysk.BackgroundTransparency = 0.6
polysk.Position = UDim2.fromScale(0.03, 0.14)
polysk.Size = UDim2.fromScale(0.94, 0.22)
polysk.Parent = wyp
rog(polysk, 0.5)
-- podziałki powtórzeń
for i = 1, D.powtorzenNaPasek - 1 do
	local k = Instance.new("Frame")
	k.Name = "Podzialka"
	k.AnchorPoint = Vector2.new(0.5, 0)
	k.Position = UDim2.fromScale(i / D.powtorzenNaPasek, 0)
	k.Size = UDim2.new(0, 3, 1, 0)
	k.BackgroundColor3 = CIEMNY
	k.BorderSizePixel = 0
	k.ZIndex = 2
	k.Parent = tor
end
local liczba = napis(tor, "Liczba", UDim2.fromScale(0, 0.05), UDim2.fromScale(1, 0.9), Color3.new(1, 1, 1))
liczba.ZIndex = 3

local stop = Instance.new("TextButton")
stop.Name = "Stop"
stop.Position = UDim2.fromScale(0.81, 0.4)
stop.Size = UDim2.fromScale(0.16, 0.34)
stop.BackgroundColor3 = Color3.fromRGB(236, 96, 86)
stop.Text = "STOP"
stop.FontFace = FONT
stop.TextScaled = true
stop.TextColor3 = Color3.new(1, 1, 1)
stop.Parent = panel
rog(stop, 0.3)
obrys(stop, 2).ApplyStrokeMode = Enum.ApplyStrokeMode.Border

local podp = napis(panel, "Podpowiedz", UDim2.fromScale(0.04, 0.78), UDim2.fromScale(0.92, 0.18), Color3.new(1, 1, 1))
podp.Text = "HIT THE SKILL CHECKS FOR 2X SPEED!"

-- skill check: okrągły przycisk z kurczącym się pierścieniem
local check = Instance.new("TextButton")
check.Name = "SkillCheck"
check.AnchorPoint = Vector2.new(0.5, 0.5)
check.Size = UDim2.fromScale(0.09, 0.09)
check.BackgroundColor3 = Color3.fromRGB(255, 214, 90)
check.Text = "!"
check.FontFace = FONT
check.TextScaled = true
check.TextColor3 = CIEMNY
check.Visible = false
check.AutoButtonColor = false
check.ZIndex = 20
check.Parent = gui
rog(check, 0.5)
obrys(check, 3).ApplyStrokeMode = Enum.ApplyStrokeMode.Border
local ca = Instance.new("UIAspectRatioConstraint")
ca.Parent = check
local mc = Instance.new("UISizeConstraint")
mc.MinSize = Vector2.new(64, 64) -- duży cel także na telefonie
mc.Parent = check
local pierscien = Instance.new("Frame")
pierscien.Name = "Pierscien"
pierscien.AnchorPoint = Vector2.new(0.5, 0.5)
pierscien.Position = UDim2.fromScale(0.5, 0.5)
pierscien.BackgroundTransparency = 1
pierscien.ZIndex = 19
pierscien.Parent = check
rog(pierscien, 0.5)
local ps = Instance.new("UIStroke")
ps.Color = Color3.new(1, 1, 1)
ps.Thickness = 3
ps.Parent = pierscien

gui.Parent = player:WaitForChild("PlayerGui")

------------------------------------------------------------ stan
local aktywne: string? = nil
local postep = 0 -- w powtórzeniach, płynnie liczony u gracza między wiadomościami serwera
local tempo = 1

local function rysuj()
	local f = math.clamp(postep / D.powtorzenNaPasek, 0, 1)
	wyp.Size = UDim2.fromScale(f, 1)
	liczba.Text = string.format("REP %d/%d", math.min(math.floor(postep) + 1, D.powtorzenNaPasek), D.powtorzenNaPasek)
		.. (if tempo > 1 then "  x" .. tostring(tempo) else "")
end

local function wyskok(tekst: string, kolor: Color3)
	local t = napis(gui, "Wyskok", UDim2.new(0.5, 0, 0.72, 0), UDim2.fromScale(0.3, 0.08), kolor)
	t.AnchorPoint = Vector2.new(0.5, 0.5)
	t.Text = tekst
	t.Rotation = math.random(-6, 6)
	TS:Create(t, TweenInfo.new(1.1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Position = UDim2.new(0.5, 0, 0.58, 0), TextTransparency = 1 }):Play()
	task.delay(1.2, function()
		t:Destroy()
	end)
end

------------------------------------------------------------ rekwizyt w rytm powtórzeń (tylko u gracza)
local RUCHOME = { "Hantla", "Krążek", "Sztanga", "Worek", "Lina", "Skakanka", "Uchwyt", "Księga", "Blat", "Kość" }
local bazowe: { [BasePart]: CFrame } = {}
local function zapamietaj()
	bazowe = {}
	local k = workspace:FindFirstChild("TreningAFK")
	local m = k and aktywne and k:FindFirstChild(aktywne)
	if not m then
		return
	end
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") then
			for _, n in ipairs(RUCHOME) do
				if p.Name:find(n, 1, true) == 1 then
					bazowe[p] = p.CFrame
					break
				end
			end
		end
	end
end
local function przywroc()
	for p, cf in pairs(bazowe) do
		if p.Parent then
			p.CFrame = cf
		end
	end
	bazowe = {}
end

RunService.RenderStepped:Connect(function(dt)
	if not aktywne then
		return
	end
	-- płynny pasek między wiadomościami serwera (serwer i tak koryguje co 0,2 s)
	postep = math.min(postep + dt * tempo / D.czasPowtorzenia, D.powtorzenNaPasek - 0.001)
	rysuj()
	-- jedno powtórzenie = podniesienie i opuszczenie (sinus po fazie powtórzenia)
	local faza = postep % 1
	local y = math.sin(faza * math.pi) * 1.4
	for p, cf in pairs(bazowe) do
		if p.Parent then
			p.CFrame = cf + Vector3.new(0, y, 0)
		end
	end
end)

------------------------------------------------------------ skill check
local numerCheck: number? = nil
local function schowajCheck()
	numerCheck = nil
	check.Visible = false
end
check.Activated:Connect(function()
	if numerCheck then
		Z:FireServer("check", numerCheck)
		schowajCheck()
	end
end)

------------------------------------------------------------ zdarzenia z serwera
Z.OnClientEvent:Connect(function(akcja, a, b, c, d)
	if akcja == "start" then
		przywroc()
		aktywne = a
		local s = D.stanowisko(a)
		postep, tempo = b or 0, 1
		tytul.Text = s and (s.nazwa .. " · " .. s.czynnosc) or "TRAINING"
		przyrostL.Text = s and ("+" .. tostring(c or 1) .. " " .. s.skrot .. " / BAR") or ""
		wyp.BackgroundColor3 = s and s.kolor or wyp.BackgroundColor3
		rysuj()
		gui.Enabled = true
		zapamietaj()
	elseif akcja == "postep" then
		postep, tempo = a, b or 1
	elseif akcja == "punkt" then
		local s = aktywne and D.stanowisko(aktywne)
		postep = c or 0
		wyskok("+" .. tostring(b) .. " " .. (s and s.skrot or ""), s and s.kolor or Color3.new(1, 1, 1))
		local sc = panel:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
		sc.Parent = panel
		sc.Scale = 1.06
		TS:Create(sc, TweenInfo.new(0.18), { Scale = 1 }):Play()
	elseif akcja == "skillcheck" then
		numerCheck = a
		local okno = b or 1.2
		check.Position = UDim2.fromScale(0.3 + math.random() * 0.4, 0.25 + math.random() * 0.3)
		check.Visible = true
		pierscien.Size = UDim2.fromScale(2.2, 2.2)
		TS:Create(pierscien, TweenInfo.new(okno, Enum.EasingStyle.Linear), { Size = UDim2.fromScale(1, 1) }):Play()
		local moj = a
		task.delay(okno + 0.1, function()
			if numerCheck == moj then
				schowajCheck()
			end
		end)
	elseif akcja == "trafiony" then
		tempo = D.mnoznikSkillCheck
		wyskok("x" .. tostring(D.mnoznikSkillCheck) .. " SPEED!", Color3.fromRGB(255, 214, 90))
	elseif akcja == "koniec" then
		przywroc()
		schowajCheck()
		aktywne = nil
		gui.Enabled = false
	end
end)

stop.Activated:Connect(function()
	Z:FireServer("stop")
end)
