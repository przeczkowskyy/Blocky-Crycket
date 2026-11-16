--[[
	HUDClient — pełny HUD: panel gracza (Figma 14:145) + przyciski (Figma 9:1570), layout Figma 9:1571.
	GUI: src/gui/HUD.model.json (StarterGui.HUD, Enabled = false).

	Pokazuje HUD po loading screenie (atrybut gracza "LoadingDone" z ReplicatedFirst.LoadingClient).
	Dane: atrybuty gracza Level, XP, XPMax, Gold, Gems, Fish (serwer: src/server/PlayerStatsDefaults.server.luau).
	Kliknięcia: ReplicatedStorage.HUDButtonPressed (BindableEvent, tylko klient):

		RS:WaitForChild("HUDButtonPressed").Event:Connect(function(name) ... end)
		-- "Teleport" | "Equipment" | "Pets" | "Quests" | "Shop" | "Guilds"

	Vault: B&C/UI/HUD.md
]]

local Players = game:GetService("Players")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local RS = game:GetService("ReplicatedStorage")

-- === USTAWIENIA ===
local REF_H = 1080 -- grubości obrysów w modelu są podane w px @1080p
local COLUMN_Y_MOBILE = 0.55 -- telefon: kolumny wyśrodkowane, nad joystickiem / przyciskiem skoku
local LOADING_TIMEOUT = 30
local AFTER_LOADING_FADE = 0.7 -- s: loading screen kończy fade-out (0.6 s)
local QUICK = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local HOVER_SCALE, PRESS_SCALE = 1.08, 0.92

local player = Players.LocalPlayer
local hud = player:WaitForChild("PlayerGui"):WaitForChild("HUD")
local panel = hud:WaitForChild("PlayerPanel")
local xpFill = panel.XPBar.XPFill
local levelLbl, goldLbl, gemsLbl, fishLbl = panel.Level, panel.Gold, panel.Gems, panel:WaitForChild("Fish")

local pressed = RS:FindFirstChild("HUDButtonPressed")
if not pressed then
	pressed = Instance.new("BindableEvent")
	pressed.Name = "HUDButtonPressed"
	pressed.Parent = RS
end

------------------------------------------------ skalowanie obrysów (model: px @1080p)
local baseThickness = {}
for _, d in ipairs(hud:GetDescendants()) do
	if d:IsA("UIStroke") then
		baseThickness[d] = d.Thickness
	end
end
local function rescale()
	local k = hud.AbsoluteSize.Y / REF_H
	if k <= 0 then
		return
	end
	for s, base in pairs(baseThickness) do
		s.Thickness = math.max(base * k, 1)
	end
end
hud:GetPropertyChangedSignal("AbsoluteSize"):Connect(rescale)

------------------------------------------------ staty
local function fmt(n)
	local s = tostring(math.floor(n + 0.5))
	local out = s:reverse():gsub("(%d%d%d)", "%1 "):reverse()
	return (out:gsub("^ ", ""))
end

local function pop(label)
	local sc = label:FindFirstChildWhichIsA("UIScale")
	if sc then
		sc.Scale = 1.18
		TS:Create(sc, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	end
end

local xpTween
local function updateXP(instant)
	local xp = player:GetAttribute("XP") or 0
	local max = math.max(player:GetAttribute("XPMax") or 100, 1)
	local p = math.clamp(xp / max, 0, 1)
	local goal = UDim2.fromScale(p, 1)
	if xpTween then
		xpTween:Cancel()
	end
	if instant then
		xpFill.Size = goal
		xpFill.Visible = p > 0 -- przy 0 ukryty: UICorner na zerowej szerokości daje artefakt
		return
	end
	if p > 0 then
		xpFill.Visible = true
	end
	xpTween = TS:Create(xpFill, TweenInfo.new(0.4, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = goal })
	xpTween.Completed:Connect(function(state)
		if state == Enum.PlaybackState.Completed then
			xpFill.Visible = p > 0
		end
	end)
	xpTween:Play()
end

local function updateLevel(animate)
	levelLbl.Text = tostring(player:GetAttribute("Level") or 1)
	if animate then
		pop(levelLbl)
	end
end

local shown = { Gold = 0, Gems = 0, Fish = 0 }
local counters = {}
local function setCurrency(label, key, instant)
	local target = player:GetAttribute(key) or 0
	local from = shown[key]
	if counters[key] then
		counters[key].tween:Cancel()
		from = counters[key].nv.Value
		counters[key].nv:Destroy()
		counters[key] = nil
	end
	shown[key] = target
	if instant or from == target then
		label.Text = fmt(target)
		return
	end
	local nv = Instance.new("NumberValue")
	nv.Value = from
	nv.Changed:Connect(function(v)
		label.Text = fmt(v)
	end)
	local t = TS:Create(nv, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Value = target })
	counters[key] = { tween = t, nv = nv }
	t.Completed:Connect(function(state)
		if state == Enum.PlaybackState.Completed then
			label.Text = fmt(target)
			nv:Destroy()
			counters[key] = nil
		end
	end)
	t:Play()
	pop(label)
end

local ready = false -- przed pokazaniem HUD zmiany ustawiamy bez animacji
player:GetAttributeChangedSignal("XP"):Connect(function()
	updateXP(not ready)
end)
player:GetAttributeChangedSignal("XPMax"):Connect(function()
	updateXP(not ready)
end)
player:GetAttributeChangedSignal("Level"):Connect(function()
	updateLevel(ready)
end)
player:GetAttributeChangedSignal("Gold"):Connect(function()
	setCurrency(goldLbl, "Gold", not ready)
end)
player:GetAttributeChangedSignal("Gems"):Connect(function()
	setCurrency(gemsLbl, "Gems", not ready)
end)
player:GetAttributeChangedSignal("Fish"):Connect(function()
	setCurrency(fishLbl, "Fish", not ready)
end)

------------------------------------------------ czekaj na koniec loadingu
local t0 = os.clock()
while not player:GetAttribute("LoadingDone") and os.clock() - t0 < LOADING_TIMEOUT do
	task.wait(0.1)
end
if not player:GetAttribute("LoadingDone") then
	warn("[HUD] Brak sygnału LoadingDone po", LOADING_TIMEOUT, "s — pokazuję HUD mimo to")
end
task.wait(AFTER_LOADING_FADE)

-- ekran wyboru klasy (ClassSelectClient): HUD dopiero po wyborze (atrybut "Class"); bez ekranu — po 10 min mimo to
if game:GetService("ReplicatedStorage"):FindFirstChild("WyborKlasyModele") then
	local tc = os.clock()
	while not player:GetAttribute("Class") and os.clock() - tc < 600 do
		task.wait(0.1)
	end
	task.wait(0.5)
end

-- stan początkowy bez animacji
updateXP(true)
updateLevel(false)
setCurrency(goldLbl, "Gold", true)
setCurrency(gemsLbl, "Gems", true)
setCurrency(fishLbl, "Fish", true)

------------------------------------------------ telefon: kolumny wyżej, nad kontrolkami dotykowymi
local columns = { hud.LeftColumn, hud.RightColumn }
if UIS.TouchEnabled and not UIS.KeyboardEnabled then
	for _, col in ipairs(columns) do
		col.AnchorPoint = Vector2.new(col.AnchorPoint.X, 0.5)
		col.Position = UDim2.fromScale(col.Position.X.Scale, COLUMN_Y_MOBILE)
	end
end

------------------------------------------------ przyciski: stan startowy (poza ekranem, przezroczyste)
local buttons = {}
for _, col in ipairs(columns) do
	local left = col.Name == "LeftColumn"
	for _, slot in ipairs(col:GetChildren()) do
		local b = slot:IsA("Frame") and slot:FindFirstChildWhichIsA("ImageButton")
		if b then
			table.insert(buttons, { btn = b, order = slot.LayoutOrder })
			b.Position = UDim2.fromScale(left and -1.5 or 2.5, 0.5)
			b.ImageTransparency = 1
		end
	end
end

local panelHome = panel.Position
panel.Position = panelHome - UDim2.fromScale(0, 0.3)

hud.Enabled = true
rescale()
ready = true

------------------------------------------------ wejście: panel z góry, przyciski z boków (stagger)
TS:Create(panel, TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = panelHome }):Play()
for _, e in ipairs(buttons) do
	task.delay(0.15 + (e.order - 1) * 0.08, function()
		TS:Create(e.btn, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
			{ Position = UDim2.fromScale(0.5, 0.5) }):Play()
		TS:Create(e.btn, TweenInfo.new(0.3), { ImageTransparency = 0 }):Play()
	end)
end

------------------------------------------------ hover / wciśnięcie / klik
local useHover = UIS.MouseEnabled
for _, e in ipairs(buttons) do
	local b = e.btn
	local sc = b:FindFirstChildWhichIsA("UIScale")
	local hovering = false
	local function to(v)
		TS:Create(sc, QUICK, { Scale = v }):Play()
	end
	if useHover then
		b.MouseEnter:Connect(function()
			hovering = true
			to(HOVER_SCALE)
		end)
		b.MouseLeave:Connect(function()
			hovering = false
			to(1)
		end)
	end
	b.MouseButton1Down:Connect(function()
		to(PRESS_SCALE)
	end)
	b.MouseButton1Up:Connect(function()
		to(hovering and HOVER_SCALE or 1)
	end)
	b.Activated:Connect(function()
		to(hovering and HOVER_SCALE or 1)
		pressed:Fire(b.Name)
		print("[HUD] pressed:", b.Name)
	end)
end
