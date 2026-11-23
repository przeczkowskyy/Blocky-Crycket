--[[
	TreningAFKClient — pasek treningu AFK (D-141; gałąź pawel/diamenty-afk). Serwer: src/server/TreningAFK.server.luau.
	Okno budowane w kodzie (TYMCZASOWE — docelowy wygląd z Figmy, jak inne okna Pawła): na dole ekranu nazwa
	statystyki, pasek postępu, „+N STR” po pełnym pasku, podpowiedź „TAP TO TRAIN FASTER” i przycisk STOP.
	Tapnięcie / kliknięcie gdziekolwiek (poza innymi przyciskami) albo spacja wysyła "tap" (serwer liczy najwyżej
	D.tapMaksNaSekunde na sekundę). Rekwizyt stanowiska lekko podskakuje w rytm treningu (tylko u gracza).
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
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

local tytul = napis(panel, "Tytul", UDim2.fromScale(0.04, 0.06), UDim2.fromScale(0.62, 0.3), Color3.fromRGB(252, 227, 176))
tytul.TextXAlignment = Enum.TextXAlignment.Left
local przyrostL = napis(panel, "Przyrost", UDim2.fromScale(0.62, 0.06), UDim2.fromScale(0.34, 0.3), Color3.fromRGB(140, 232, 101))
przyrostL.TextXAlignment = Enum.TextXAlignment.Right

local tor = Instance.new("Frame")
tor.Name = "Tor"
tor.Position = UDim2.fromScale(0.04, 0.42)
tor.Size = UDim2.fromScale(0.74, 0.28)
tor.BackgroundColor3 = Color3.fromRGB(14, 10, 16)
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
local liczba = napis(tor, "Liczba", UDim2.fromScale(0, 0.05), UDim2.fromScale(1, 0.9), Color3.new(1, 1, 1))
liczba.ZIndex = 3

local stop = Instance.new("TextButton")
stop.Name = "Stop"
stop.Position = UDim2.fromScale(0.81, 0.4)
stop.Size = UDim2.fromScale(0.16, 0.32)
stop.BackgroundColor3 = Color3.fromRGB(236, 96, 86)
stop.Text = "STOP"
stop.FontFace = FONT
stop.TextScaled = true
stop.TextColor3 = Color3.new(1, 1, 1)
stop.Parent = panel
rog(stop, 0.3)
obrys(stop, 2).ApplyStrokeMode = Enum.ApplyStrokeMode.Border

local podp = napis(panel, "Podpowiedz", UDim2.fromScale(0.04, 0.76), UDim2.fromScale(0.92, 0.2), Color3.new(1, 1, 1))
podp.Text = if UIS.TouchEnabled then "TAP THE SCREEN TO TRAIN FASTER" else "CLICK OR PRESS SPACE TO TRAIN FASTER"

gui.Parent = player:WaitForChild("PlayerGui")

------------------------------------------------------------ stan
local aktywne: string? = nil
local postep, dlugosc = 0, 1
local naPasek = 1

local function rysuj(anim: boolean)
	local f = math.clamp(postep / math.max(dlugosc, 0.001), 0, 1)
	if anim then
		TS:Create(wyp, TweenInfo.new(0.24, Enum.EasingStyle.Linear), { Size = UDim2.fromScale(f, 1) }):Play()
	else
		wyp.Size = UDim2.fromScale(f, 1)
	end
	liczba.Text = string.format("%d%%", math.floor(f * 100))
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

------------------------------------------------------------ rekwizyt podskakuje (tylko u gracza)
local podskok = 0
RunService.RenderStepped:Connect(function(dt)
	if not aktywne then
		return
	end
	podskok += dt
end)

local function stanowisko()
	local k = workspace:FindFirstChild("TreningAFK")
	return k and aktywne and k:FindFirstChild(aktywne)
end

local bazowe: { [BasePart]: CFrame } = {}
local function zapamietaj()
	bazowe = {}
	local m = stanowisko()
	if not m then
		return
	end
	for _, p in ipairs(m:GetDescendants()) do
		if p:IsA("BasePart") and not p.Name:find("Mata") and not p.Name:find("Tabliczka") and not p.Name:find("Noga")
			and not p.Name:find("Słup") and not p.Name:find("Stojak") and not p.Name:find("Ławka") and not p.Name:find("Pulpit")
			and not p.Name:find("Stolik") and not p.Name:find("Wysięgnik") then
			bazowe[p] = p.CFrame
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
RunService.RenderStepped:Connect(function()
	if not aktywne then
		return
	end
	local y = math.abs(math.sin(podskok * 3)) * 0.6
	for p, cf in pairs(bazowe) do
		if p.Parent then
			p.CFrame = cf + Vector3.new(0, y, 0)
		end
	end
end)

------------------------------------------------------------ zdarzenia z serwera
Z.OnClientEvent:Connect(function(akcja, a, b, c, d)
	if akcja == "start" then
		przywroc()
		aktywne = a
		local s = D.stanowisko(a)
		postep, dlugosc, naPasek = b or 0, c or 1, d or 1
		tytul.Text = s and (s.nazwa .. " · " .. s.czynnosc) or "TRAINING"
		przyrostL.Text = s and ("+" .. naPasek .. " " .. s.skrot .. " / BAR") or ""
		wyp.BackgroundColor3 = s and s.kolor or wyp.BackgroundColor3
		rysuj(false)
		gui.Enabled = true
		zapamietaj()
	elseif akcja == "postep" then
		postep, dlugosc = a, b
		rysuj(true)
	elseif akcja == "punkt" then
		local s = aktywne and D.stanowisko(aktywne)
		postep, dlugosc = 0, c or dlugosc
		rysuj(false)
		wyskok("+" .. tostring(b) .. " " .. (s and s.skrot or ""), s and s.kolor or Color3.new(1, 1, 1))
	elseif akcja == "koniec" then
		przywroc()
		aktywne = nil
		gui.Enabled = false
	end
end)

------------------------------------------------------------ tapnięcia
local ostatni = 0
local function tap()
	if not aktywne then
		return
	end
	local t = os.clock()
	if t - ostatni < 0.12 then
		return
	end
	ostatni = t
	Z:FireServer("tap")
	-- natychmiastowa reakcja u gracza (serwer i tak przyśle prawdziwy stan za chwilę)
	postep = math.min(postep + D.tapWartosc, dlugosc)
	rysuj(true)
	local sc = panel:FindFirstChildOfClass("UIScale") or Instance.new("UIScale")
	sc.Parent = panel
	sc.Scale = 1.04
	TS:Create(sc, TweenInfo.new(0.12), { Scale = 1 }):Play()
end

UIS.InputBegan:Connect(function(input, processed)
	if processed or not aktywne then
		return
	end
	local t = input.UserInputType
	if t == Enum.UserInputType.MouseButton1 or t == Enum.UserInputType.Touch or input.KeyCode == Enum.KeyCode.Space then
		tap()
	end
end)
stop.Activated:Connect(function()
	Z:FireServer("stop")
end)
