--[[
	BLOCKY & CRYCKET — Loading Screen + Progress Bar (build script)
	Run in Roblox Studio (Edit) via MCP execute_luau or the Command Bar.
	Creates ONLY: ReplicatedFirst.LoadingScreen (ScreenGui template) + ReplicatedFirst.LoadingClient (LocalScript).
	ReplicatedFirst is NOT mapped by Rojo — this file is the reproducible source of those two objects.
	Design: Figma BbLd4jDnvxAmOWZN1hAZQJ node 2:2 (bar) / 2:75 (screen). Vault: B&C/UI/Ekran ładowania.md
]]

local RF = game:GetService("ReplicatedFirst")
for _, n in ipairs({ "LoadingScreen", "LoadingClient" }) do
	local o = RF:FindFirstChild(n)
	if o then o:Destroy() end
end

local BG_IMAGE = "rbxassetid://129202798952612" -- key-art (Figma 2:76), wgrany 2026-11-11
local DW, DH = 1600, 300
local INK = Color3.fromRGB(43, 26, 16)
local function rgb(h) return Color3.fromHex(h) end

local function new(class, props, parent)
	local o = Instance.new(class)
	for k, v in pairs(props) do o[k] = v end
	o.Parent = parent
	return o
end
local function place(o, pw, ph, x, y, w, h)
	o.Position = UDim2.fromScale(x / pw, y / ph)
	o.Size = UDim2.fromScale(w / pw, h / ph)
	return o
end
local function corner(o, r, shortSide) new("UICorner", { CornerRadius = UDim.new(r / shortSide, 0) }, o) end
local function stroke(o, px, contextual)
	local s = new("UIStroke", { Color = INK, Thickness = px, LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = contextual and Enum.ApplyStrokeMode.Contextual or Enum.ApplyStrokeMode.Border }, o)
	s:SetAttribute("BaseThickness", px)
	return s
end
local function grad(o, stops, rot)
	local kp = {}
	for _, s in ipairs(stops) do table.insert(kp, ColorSequenceKeypoint.new(s[1], rgb(s[2]))) end
	return new("UIGradient", { Color = ColorSequence.new(kp), Rotation = rot or 90 }, o)
end
local function frame(parent, pw, ph, x, y, w, h, color, name)
	local f = new("Frame", { Name = name or "Frame", BackgroundColor3 = color or Color3.new(1, 1, 1), BorderSizePixel = 0 }, parent)
	return place(f, pw, ph, x, y, w, h)
end
local function label(parent, name, text, font, color, strokePx, x, y, w, h)
	local shadow = new("TextLabel", { Name = name .. "Shadow", Text = text, FontFace = font, TextScaled = true,
		TextColor3 = INK, BackgroundTransparency = 1, TextTransparency = 0.4, ZIndex = 9 }, parent)
	place(shadow, DW, DH, x, y + 6, w, h)
	local t = new("TextLabel", { Name = name, Text = text, FontFace = font, TextScaled = true,
		TextColor3 = color, BackgroundTransparency = 1, ZIndex = 10 }, parent)
	place(t, DW, DH, x, y, w, h)
	stroke(t, strokePx, true)
	return t, shadow
end

-- ScreenGui
local gui = new("ScreenGui", { Name = "LoadingScreen", IgnoreGuiInset = true, ResetOnSpawn = false,
	DisplayOrder = 100, ZIndexBehavior = Enum.ZIndexBehavior.Sibling }, RF)
new("ImageLabel", { Name = "Background", Image = BG_IMAGE, ScaleType = Enum.ScaleType.Crop,
	Size = UDim2.fromScale(1, 1), BackgroundColor3 = rgb("#2A1E4A"), BorderSizePixel = 0 }, gui)
local vig = new("Frame", { Name = "Vignette", BackgroundColor3 = rgb("#0E0820"), BorderSizePixel = 0,
	AnchorPoint = Vector2.new(0, 1), Position = UDim2.fromScale(0, 1), Size = UDim2.fromScale(1, 0.3) }, gui)
new("UIGradient", { Rotation = 90, Transparency = NumberSequence.new({
	NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 0.25) }) }, vig)

-- Bar root
local bar = new("Frame", { Name = "ProgressBar", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 1),
	Position = UDim2.fromScale(0.5, 0.974), Size = UDim2.fromScale(0.58, 0.2) }, gui)
new("UIAspectRatioConstraint", { AspectRatio = DW / DH }, bar)

local LUCKY = Font.fromEnum(Enum.Font.LuckiestGuy)
local PIXEL = Font.fromEnum(Enum.Font.Arcade)

label(bar, "Label", "ŁADOWANIE PRZYGODY...", LUCKY, rgb("#FFF1BF"), 4, 300, 0, 1000, 70)

-- Stone frame
local stone = frame(bar, DW, DH, 0, 86, 1600, 144, Color3.new(1, 1, 1), "StoneFrame")
stone.ZIndex = 1
corner(stone, 30, 144); stroke(stone, 4)
grad(stone, { { 0, "#B9BEC8" }, { 0.5, "#8D929E" }, { 1, "#5F6470" } })
local stoneShadow = frame(bar, DW, DH, 0, 96, 1600, 144, INK, "StoneShadow")
stoneShadow.BackgroundTransparency = 0.45; stoneShadow.ZIndex = 0; corner(stoneShadow, 30, 144)
-- Figma: small dark slots notched into the stone's top and bottom edges
for i, p in ipairs({ { 180, 92 }, { 830, 92 }, { 1020, 92 }, { 340, 218 }, { 580, 218 }, { 1270, 218 } }) do
	local s = frame(bar, DW, DH, p[1], p[2], 30, 8, rgb("#5A5F6B"), "Slot" .. i)
	s.ZIndex = 2; corner(s, 2, 8)
end
for i, p in ipairs({ { 26, 104 }, { 1554, 104 }, { 26, 192 }, { 1554, 192 } }) do
	local r = frame(bar, DW, DH, p[1], p[2], 20, 20, Color3.new(1, 1, 1), "Rivet" .. i)
	r.ZIndex = 2; corner(r, 10, 20); stroke(r, 2)
	grad(r, { { 0, "#E3E6EC" }, { 1, "#7C8190" } })
end

-- Track (wood)
local TW, TH = 1460, 80
local track = frame(bar, DW, DH, 70, 118, TW, TH, Color3.new(1, 1, 1), "Track")
track.ZIndex = 3; track.ClipsDescendants = true; corner(track, 18, TH); stroke(track, 3)
grad(track, { { 0, "#6E4627" }, { 1, "#4A2D17" } })
for i = 1, 9 do
	local p = frame(track, TW, TH, i * 146 - 2, 0, 4, TH, rgb("#2E1A0C"), "Plank" .. i)
	p.BackgroundTransparency = 0.45; p.ZIndex = 3
end

-- Fill
local fill = new("CanvasGroup", { Name = "Fill", BackgroundColor3 = Color3.new(1, 1, 1), BorderSizePixel = 0,
	Size = UDim2.fromScale(0.68, 1), ZIndex = 4 }, track)
corner(fill, 18, TH)
grad(fill, { { 0, "#1BA9DA" }, { 1, "#41F5D6" } }, 0)
local inner = new("Frame", { Name = "Inner", BackgroundTransparency = 1, Size = UDim2.new(0, 1000, 1, 0) }, fill)
for i = 0, 28 do
	local s = new("Frame", { Name = "Stripe", BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.84,
		BorderSizePixel = 0, Rotation = -30, ZIndex = 5 }, inner)
	s.Position = UDim2.fromScale((i * 56 - 40) / TW, -0.25); s.Size = UDim2.fromScale(22 / TW, 1.6)
end
local hl = new("Frame", { Name = "Highlight", BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.5,
	BorderSizePixel = 0, ZIndex = 6 }, fill)
corner(hl, 8, 16)
hl.Position = UDim2.new(0.01, 0, 9 / TH, 0); hl.Size = UDim2.new(0.98, 0, 16 / TH, 0)
new("Frame", { Name = "Shade", BackgroundColor3 = rgb("#0B5E86"), BackgroundTransparency = 0.65,
	BorderSizePixel = 0, ZIndex = 6, Position = UDim2.fromScale(0, 62 / TH), Size = UDim2.fromScale(1, 18 / TH) }, fill)
stroke(fill, 2.5)

-- Spark (pixel cross)
local spark = new("Frame", { Name = "Spark", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
	Position = UDim2.fromScale((70 + TW * 0.68) / DW, 158 / DH), Size = UDim2.fromScale(56 / DW, 56 / DH), ZIndex = 8 }, bar)
new("UIAspectRatioConstraint", { AspectRatio = 1 }, spark)
for _, c in ipairs({ { 3, 0 }, { 3, 1 }, { 3, 2 }, { 0, 3 }, { 1, 3 }, { 2, 3 }, { 3, 3 }, { 4, 3 }, { 5, 3 }, { 6, 3 }, { 3, 4 }, { 3, 5 }, { 3, 6 } }) do
	local d = math.abs(c[1] - 3) + math.abs(c[2] - 3)
	local px = new("Frame", { BorderSizePixel = 0, ZIndex = 8, BackgroundColor3 = d > 2 and rgb("#FFE46B") or Color3.new(1, 1, 1) }, spark)
	px.Position = UDim2.fromScale(c[1] / 7, c[2] / 7); px.Size = UDim2.fromScale(1 / 7, 1 / 7)
end

-- Gems
local function gem(cx, name)
	local g = new("Frame", { Name = name, BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(cx / DW, 158 / DH), Size = UDim2.fromScale(110 / DW, 110 / DH), ZIndex = 9 }, bar)
	new("UIAspectRatioConstraint", { AspectRatio = 1 }, g)
	local function rhomb(sz, stops, sw, z)
		local r = new("Frame", { BackgroundColor3 = Color3.new(1, 1, 1), BorderSizePixel = 0, Rotation = 45, ZIndex = z,
			AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5), Size = UDim2.fromScale(sz / 110, sz / 110) }, g)
		corner(r, sz * 0.16, sz); stroke(r, sw); grad(r, stops)
		return r
	end
	rhomb(74, { { 0, "#FFE07A" }, { 1, "#D18A12" } }, 3.5, 9).Name = "GoldRim"
	rhomb(46, { { 0, "#F2A6FF" }, { 0.5, "#B54BF0" }, { 1, "#6A1FB8" } }, 2, 10).Name = "Amethyst"
	local sh = new("Frame", { Name = "Shine", BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.1,
		BorderSizePixel = 0, Rotation = 45, ZIndex = 11, AnchorPoint = Vector2.new(0.5, 0.5),
		Position = UDim2.fromScale(0.44, 0.4), Size = UDim2.fromScale(12 / 110, 12 / 110) }, g)
	corner(sh, 3, 12)
end
gem(4, "GemL"); gem(1596, "GemR")

local pct = label(bar, "Percent", "68%", LUCKY, rgb("#FFD23F"), 4, 650, 124, 300, 66)
pct.ZIndex = 12; bar:FindFirstChild("PercentShadow").ZIndex = 11
label(bar, "Tip", "WSKAZÓWKA: Twierdza produkuje złoto, nawet gdy jesteś w dungeonie!", PIXEL, Color3.new(1, 1, 1), 2.5, 150, 250, 1300, 42)

-- Runtime LocalScript
local client = new("LocalScript", { Name = "LoadingClient" }, RF)
client.Source = [==[
local RF = game:GetService("ReplicatedFirst")
local Players = game:GetService("Players")
local CP = game:GetService("ContentProvider")
local TS = game:GetService("TweenService")
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

-- === USTAWIENIA ===
local MIN_DURATION = 4.5  -- s: pasek napełnia się co najmniej tyle (nawet gdy wszystko jest już załadowane)
local TIP_INTERVAL = 2.6  -- s: co ile zmienia się tekst pod paskiem
local HOLD_AT_100 = 0.6   -- s: pauza na 100% przed wygaszeniem

-- Treści pod paskiem: losowa kategoria + losowy wpis (bez powtórek, dopóki pula się nie wyczerpie)
local TIPS = {
	["WSKAZÓWKA"] = {
		"Twierdza produkuje złoto, nawet gdy jesteś w dungeonie!",
		"Droppery w Twierdzy dają Złoto i Magiczne Kryształy.",
		"Za surowce z misji zbudujesz w Twierdzy nowe droppery.",
		"Karczmarz zawsze ma dla Ciebie trzy misje do wyboru.",
		"W dungeonie okładaj beczkę, a quest skończy się szybciej!",
		"Pety wykluwają się z jaj. Każde jajo to niespodzianka!",
		"Pety podbijają statystyki. Dobieraj je z głową!",
	},
	["PLOTKA Z KARCZMY"] = {
		"Goblin z piwnicy twierdzi, że to on wymyślił złoto.",
		"Nie jedz grzybów z Lochu. Kot-Mag zjadł i gada po goblińsku.",
		"Karczmarz podobno nigdy nie umył tego jednego kufla.",
		"Rycerz śpi w zbroi. Nikt nie wie, jak ją zdejmuje.",
		"Slime nie gryzie. Najwyżej trochę się klei.",
		"Pies znalazł w lesie miecz i nie chce go oddać.",
		"Gobliny liczą złoto na palcach. Mają ich siedem.",
	},
	["CIEKAWOSTKA"] = {
		"Szata Kota-Maga jest o trzy rozmiary za duża. Celowo.",
		"Księżyc nad Zamkiem patrzy na Ciebie. Zawsze.",
		"Smok jest mały, ale jego ego jest ogromne.",
		"Portal do Lochu świeci, bo ktoś zapomniał zgasić światło.",
		"Najrzadszy grzyb w lesie smakuje jak stare skarpety.",
	},
}

RF:RemoveDefaultLoadingScreen()
local gui = RF:WaitForChild("LoadingScreen"):Clone()
gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")

local bar = gui.ProgressBar
local track, fill, spark = bar.Track, bar.Track.Fill, bar.Spark
local pct, pctShadow, tip, tipShadow = bar.Percent, bar.PercentShadow, bar.Tip, bar.TipShadow
local tipStroke = tip:FindFirstChildOfClass("UIStroke")
local DW, TW = 1600, 1460
local sparkY = spark.Position.Y.Scale

local function rescale()
	local k = bar.AbsoluteSize.X / DW * 2
	for _, d in ipairs(gui:GetDescendants()) do
		if d:IsA("UIStroke") then d.Thickness = (d:GetAttribute("BaseThickness") or 1) * k end
	end
	fill.Inner.Size = UDim2.new(0, track.AbsoluteSize.X, 1, 0)
end
bar:GetPropertyChangedSignal("AbsoluteSize"):Connect(rescale)
rescale()

local function setProgress(p)
	p = math.clamp(p, 0, 1)
	fill.Size = UDim2.fromScale(math.max(p, 0.02), 1)
	spark.Position = UDim2.fromScale((70 + TW * p) / DW, sparkY)
	local txt = math.floor(p * 100 + 0.5) .. "%"
	pct.Text, pctShadow.Text = txt, txt
end

-- === Generator treści ===
local pool = {}
local function refill()
	for cat, list in pairs(TIPS) do
		for _, t in ipairs(list) do table.insert(pool, cat .. ": " .. t) end
	end
end
local last
local function nextTip()
	if #pool == 0 then refill() end
	local i = math.random(#pool)
	if pool[i] == last and #pool > 1 then i = i % #pool + 1 end
	last = table.remove(pool, i)
	return last
end

local fadeInfo = TweenInfo.new(0.25)
local function showTip(text, instant)
	if not instant then
		TS:Create(tip, fadeInfo, { TextTransparency = 1 }):Play()
		TS:Create(tipShadow, fadeInfo, { TextTransparency = 1 }):Play()
		if tipStroke then TS:Create(tipStroke, fadeInfo, { Transparency = 1 }):Play() end
		task.wait(0.25)
	end
	tip.Text, tipShadow.Text = text, text
	TS:Create(tip, fadeInfo, { TextTransparency = 0 }):Play()
	TS:Create(tipShadow, fadeInfo, { TextTransparency = 0.4 }):Play()
	if tipStroke then TS:Create(tipStroke, fadeInfo, { Transparency = 0 }):Play() end
end

showTip(nextTip(), true)
task.spawn(function()
	while gui.Parent do
		task.wait(TIP_INTERVAL)
		if gui.Parent then showTip(nextTip()) end
	end
end)

setProgress(0)
CP:PreloadAsync({ gui }) -- najpierw tło ekranu

-- === Prawdziwe ładowanie (w tle) ===
local real = 0
task.spawn(function()
	if not game:IsLoaded() then game.Loaded:Wait() end
	local assets = RS:GetDescendants()
	local total, BATCH = math.max(#assets, 1), 25
	for s = 1, #assets, BATCH do
		CP:PreloadAsync(table.move(assets, s, math.min(s + BATCH - 1, #assets), 1, {}))
		real = math.min(s + BATCH - 1, #assets) / total
	end
	real = 1
end)

-- === Krzywa "udawanego" postępu: kilka losowych przystanków, płynne zwalnianie między nimi ===
local curve = { { 0, 0 } }
local STEPS = 5
for i = 1, STEPS - 1 do
	local t = i / STEPS + (math.random() - 0.5) * 0.1
	local v = math.clamp(i / STEPS + (math.random() - 0.5) * 0.25, curve[#curve][2] + 0.03, 0.95)
	table.insert(curve, { t, v })
end
table.insert(curve, { 1, 1 })
local function fake(x)
	if x >= 1 then return 1 end
	for i = 2, #curve do
		local a, b = curve[i - 1], curve[i]
		if x <= b[1] then
			local u = (x - a[1]) / (b[1] - a[1])
			u = u * u * (3 - 2 * u) -- smoothstep: przyspiesza i zwalnia przy każdym przystanku
			return a[2] + (b[2] - a[2]) * u
		end
	end
	return 1
end

local t0, shown = os.clock(), 0
while shown < 1 do
	local dt = RunService.RenderStepped:Wait()
	local target = math.min(real, fake((os.clock() - t0) / MIN_DURATION))
	shown += (target - shown) * math.min(1, dt * 10)
	if target >= 1 and shown > 0.995 then shown = 1 end
	setProgress(shown)
end
task.wait(HOLD_AT_100)
Players.LocalPlayer:SetAttribute("LoadingDone", true) -- sygnał dla HUDClient

local cg = Instance.new("CanvasGroup")
cg.Size, cg.BackgroundTransparency = UDim2.fromScale(1, 1), 1
cg.Parent = gui
for _, c in ipairs(gui:GetChildren()) do if c ~= cg then c.Parent = cg end end
TS:Create(cg, TweenInfo.new(0.6), { GroupTransparency = 1 }):Play()
task.wait(0.65)
gui:Destroy()
]==]

return "OK: ReplicatedFirst.LoadingScreen + LoadingClient"
