--[[
	HUDClient — pełny HUD: panel gracza (Figma 14:145) + przyciski (Figma 9:1570), layout Figma 9:1571.
	GUI: src/gui/HUD.model.json (StarterGui.HUD, Enabled = false).

	Pokazuje HUD po loading screenie (atrybut gracza "LoadingDone" z ReplicatedFirst.LoadingClient).
	Dane: atrybuty gracza Level, XP, XPMax, Gold, Gems, Fish (serwer: src/server/PlayerStatsDefaults.server.luau).
	Kliknięcia: ReplicatedStorage.HUDButtonPressed (BindableEvent, tylko klient):

		RS:WaitForChild("HUDButtonPressed").Event:Connect(function(name) ... end)
		-- "Teleport" | "Equipment" | "Pets" | "Index" | "Shop" | "Guilds"

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
-- Paweł 24.11 (z Karolem): Rybki zamiast złotej monety — licznik Rybek (Fish) z HUD usunięty, ikona Złota to rybka
local levelLbl, goldLbl, gemsLbl = panel.Level, panel.Gold, panel.Gems
local fishLbl = panel:FindFirstChild("Fish")

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

------------------------------------------------ znaczek klasy przy poziomie (emblemat z ekranu wyboru klasy)
local function refreshClassBadge(badge: ImageLabel)
	local ok, ClassData = pcall(function()
		return require(RS:WaitForChild("Shared"):WaitForChild("ClassData"))
	end)
	local ok2, Icons = pcall(function()
		return require(RS:WaitForChild("Shared"):WaitForChild("ClassSelectIcons"))
	end)
	local c = ok and ok2 and ClassData.byId(player:GetAttribute("Class") or "")
	badge.Image = c and Icons[c.emblem] or ""
	badge.Visible = c ~= nil
end
do
	local badge = panel:FindFirstChild("ClassBadge")
	if badge then
		refreshClassBadge(badge)
		player:GetAttributeChangedSignal("Class"):Connect(function()
			refreshClassBadge(badge)
		end)
	end
end

------------------------------------------------ portret rasy w ramce (Paweł 23.11)
pcall(function()
	-- ramka z portretem rasy przykrywa górną część grafiki ramki (FrameArt); pasek i poziom zostają na wierzchu
	-- Tor paska w ramce rasy (RaceFrame 512 × 556): x 0,158–0,843, y 0,832–0,966 obrazka. FrameArt (0,38298 × 0,9717
	-- panelu, proporcje 0,874) skaluje obrazek przez Fit, a ramka rasy ma proporcje 0,921 — obrazek jest niższy
	-- o 5 % i wyśrodkowany w pionie, stąd przesunięcie. Pasek o 1 px węższy od toru z każdej strony, bez obrysu.
	local fa = panel:WaitForChild("FrameArt") :: ImageLabel
	local rama = fa.Size
	local wys = 0.874 / 0.921 -- część wysokości FrameArt zajęta przez obrazek (Fit przy szerszym obrazku)
	local gora = (1 - wys) / 2
	local TOR = {
		fa.Position.X.Scale + rama.X.Scale * 0.158 + 0.0034,
		fa.Position.Y.Scale + rama.Y.Scale * (gora + 0.832 * wys) + 0.0076,
		rama.X.Scale * 0.685 - 0.0069,
		rama.Y.Scale * 0.134 * wys - 0.0152,
	}
	local xp = panel:WaitForChild("XPBar")
	-- cyferka poziomu: wyśrodkowana i w całości wewnątrz toru paska (Paweł 23.11), zapas na obrys liter
	local NAPIS = { TOR[1], TOR[2] + TOR[4] * 0.08, TOR[3], TOR[4] * 0.84 }
	levelLbl.TextXAlignment = Enum.TextXAlignment.Center
	levelLbl.TextYAlignment = Enum.TextYAlignment.Center
	require(RS:WaitForChild("Shared"):WaitForChild("RacePortraitUI")).attach({
		podmien = fa,
		uklad = {
			{ obj = xp, rect = TOR },
			{ obj = levelLbl, rect = NAPIS },
			-- ikonka klasy (kotwica w środku, rozmiar z wysokości): większa, na lewym końcu paska (Paweł 23.11)
			{ obj = panel:WaitForChild("ClassBadge") :: GuiObject, rect = { TOR[1] + 0.004, TOR[2] + TOR[4] / 2, 0, TOR[4] * 1.6 } },
		},
		wylacz = { xp:FindFirstChildOfClass("UIStroke") },
	})
	-- ikonka klasy przed paskiem i liczbą poziomu (Paweł 23.11)
	local znak = panel:FindFirstChild("ClassBadge") :: GuiObject?
	if znak then
		znak.ZIndex = math.max(xp.ZIndex, levelLbl.ZIndex) + 2
	end
end)

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
	if not fishLbl then
		return
	end
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

-- ekran wyboru klasy i rasy (ClassSelectClient): HUD dopiero po wyborze (atrybut "Race", a bez ekranu ras — "Class");
-- bez ekranu — po 10 min mimo to
if game:GetService("ReplicatedStorage"):FindFirstChild("WyborKlasyModele") then
	local tc = os.clock()
	local key = game:GetService("ReplicatedStorage"):FindFirstChild("ChooseRace") and "Race" or "Class"
	while not player:GetAttribute(key) and os.clock() - tc < 600 do
		task.wait(0.1)
	end
	task.wait(0.5)
end

-- stan początkowy bez animacji
updateXP(true)
updateLevel(false)
setCurrency(goldLbl, "Gold", true)
setCurrency(gemsLbl, "Gems", true)
if fishLbl then
	setCurrency(fishLbl, "Fish", true)
end

------------------------------------------------ telefon: kolumny wyżej, nad kontrolkami dotykowymi
-- Paweł 25.11: wszystkie przyciski po lewej w dwóch rzędach po 3, mniejsze niż dawniej; Index zamiast Quests (questy
-- siedzą w wysuwanej szufladzie po prawej — QuestyClient). Górny rząd nazywa się nadal LeftColumn (ścieżka, której
-- szukają wskazówki Karola: HUD/LeftColumn/TeleportSlot/Teleport), dolny BottomRow.
local columns = { hud:WaitForChild("LeftColumn"), hud:WaitForChild("BottomRow") }
if UIS.TouchEnabled and not UIS.KeyboardEnabled then
	local gora, dol = columns[1] :: Frame, columns[2] :: Frame
	local odstep = dol.Position.Y.Scale - dol.Size.Y.Scale - gora.Position.Y.Scale
	gora.Position = UDim2.fromScale(gora.Position.X.Scale, COLUMN_Y_MOBILE - odstep / 2)
	dol.Position = UDim2.fromScale(dol.Position.X.Scale, COLUMN_Y_MOBILE + odstep / 2 + dol.Size.Y.Scale)
end

------------------------------------------------ przyciski i panel: od razu na miejscu
-- Paweł 24.11: „żeby się wyświetlały natychmiast, a nie ze spowolnieniem” — dawniej panel zjeżdżał z góry (0,5 s),
-- a przyciski wlatywały z boków po kolei i rozjaśniały się z przezroczystości, co przy wejściu wyglądało jak miganie.
local buttons = {}
for _, row in ipairs(columns) do
	for _, slot in ipairs(row:GetChildren()) do
		local b = slot:IsA("Frame") and slot:FindFirstChildWhichIsA("ImageButton")
		if b then
			table.insert(buttons, { btn = b, order = slot.LayoutOrder })
			b.Position = UDim2.fromScale(0.5, 0.5)
			b.ImageTransparency = 0
		end
	end
end

hud.Enabled = true
rescale()
ready = true

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
