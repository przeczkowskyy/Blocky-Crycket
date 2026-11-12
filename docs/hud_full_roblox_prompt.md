# Claude Code → Roblox Studio (MCP): pełny HUD „Blocky&Crycket” (przyciski + panel gracza)

> Ten prompt **zastępuje** `hud_buttons_roblox_prompt.md`. Buduje cały HUD od zera (stary HUD usuwa). Pokazuje się dopiero po zakończeniu loading screena.

## Zadanie
Zbuduj w Roblox Studio (przez Roblox Studio MCP: `run_code` / odpowiednik) HUD 1:1 z Figmy:
- **Panel gracza – lewy górny róg:** ramka portretu z paskiem XP (domyślnie **pusty**), złota cyfra poziomu na środku paska (start **1**); na prawo od ramki **złoto** (ikona + liczba), pod nim **diamenty** (waluta premium).
- **Przyciski (128 px @1080p), przy dolnej krawędzi:**
  - lewa kolumna (od góry): **Teleport, Equipment, Pets**
  - prawa kolumna (od góry): **Quests, Shop, Guilds**
- Cały HUD ukryty do końca loading screena, potem animowane wejście.

## Źródła
- Figma – HUD 1920×1080 (pozycje, źródło prawdy): https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=9-1571
- Figma – komponent Player Panel: https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=14-145
- Figma – przyciski (property `Type`): https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=9-1570
- Assety (`hud_assets_png.zip`, przycięte, przezroczyste tło):
  `Teleport.png, Equipment.png, Pets.png, Quests.png, Shop.png, Guilds.png, PlayerFrame.png, Coin.png, Gem.png`
- Loading screen już jest: `ReplicatedFirst.LoadingScreen` + `ReplicatedFirst.LoadingClient`.

## Kroki
1. **Asset IDs.** Poproś mnie o 9 asset ID (wgrywam PNG przez Asset Manager → Bulk Import → Copy Asset ID). Jeśli dam Open Cloud API key z `asset:write` – wgraj sam przez Assets API. Do tego czasu `rbxassetid://0`.
   - **Ważne:** `PlayerFrame.png` musi być dokładnie ten plik (416×476). Pasek XP jest nakładany w precyzyjnie wyliczonym miejscu na wypalony w PNG zielony pasek – inny crop = rozjazd.
2. **Patch LoadingClient.** Jeśli jeszcze nie ma – w `ReplicatedFirst.LoadingClient` tuż PRZED fade-outem dodaj:
   ```lua
   Players.LocalPlayer:SetAttribute("LoadingDone", true)
   ```
3. **Build.** Uruchom skrypt `BUILD` (niżej). Usuwa stare i tworzy:
   - `StarterGui.HUD` (ScreenGui, `Enabled = false`) → `PlayerPanel`, `LeftColumn`, `RightColumn`
   - `StarterPlayer.StarterPlayerScripts.HUDClient` (LocalScript – pokazanie po loadingu, animacje, bindowanie statów, kliknięcia)
   - `ReplicatedStorage.HUDButtonPressed` (BindableEvent – nazwa klikniętego przycisku)
   - `ServerScriptService.PlayerStatsDefaults` (Script – domyślne atrybuty gracza: `Level=1, XP=0, XPMax=100, Gold=0, Gems=0`; placeholder do czasu DataStore)
4. **Test (Play Solo + Device Emulator telefon):**
   - HUD niewidoczny podczas loadingu; potem panel zjeżdża z góry, przyciski wjeżdżają z boków,
   - pasek XP pusty, poziom „1”, złoto „0”, diamenty „0”,
   - w Command Bar (server): `game.Players:GetPlayers()[1]:SetAttribute("XP", 50)` → pasek animuje się do 50%; `:SetAttribute("Gold", 125430)` → licznik „125 430” z animacją; `:SetAttribute("Level", 2)` → „2”,
   - hover/press na przyciskach, w Output `[HUD] pressed: <Nazwa>`,
   - na telefonie przyciski NIE nachodzą na joystick/jump, panel NIE nachodzi na przyciski Robloxa (menu/czat).
   Screenshot (PC + telefon) + raport.
5. Nie twórz okien Shop/Pets itd. – tylko HUD + event.

## Spec (referencja 1920×1080, wszystko w Scale)
| Element | Pozycja / rozmiar | Uwagi |
|---|---|---|
| ScreenGui | `IgnoreGuiInset=false`, `ScreenInsets=CoreUISafeInsets` | nie wchodzi pod topbar Robloxa ani notch |
| PlayerPanel | x 40, y 30, 470×212 | `UIAspectRatioConstraint 470/212`, wysokość 19.6% ekranu |
| ↳ FrameArt | 0,0,180,206 | `PlayerFrame.png`, ScaleType Fit |
| ↳ PortraitSlot | 17,17,143,130 | pusty – miejsce na avatar (przyszłość) |
| ↳ XPBar | 28.56,160.5,122.9,37.6, r10 | granat #2B3552→#1A2034, obrys #1A1410 3px; przykrywa wypalony zielony pasek |
| ↳ XPFill | szer. = XP/XPMax | zielony #B6F26A→#4CB33C, ukryty przy 0 |
| ↳ Level | środek XPBar | LuckiestGuy, gradient #FFF0A8→#F2C24A→#B8862A, obrys 4.5px |
| ↳ Gold | ikona 190,18,82×81; belka 214,30,244×58 | belka granat + złota obwódka #D9B45A 4px + czarny obrys; tekst #FFD23F |
| ↳ Gems | ikona 188,112,86×76; belka 214,120,244×58 | tekst #8AF0FF |
| Przycisk | 128×128 (11.85% wys.) | min 56 px, max 150 px |
| Kolumny | x 40 od krawędzi, dół 60 px od dołu, odstęp 18 | PC |
| Kolumny – mobile | wyśrodkowane w pionie (55%) | żeby ominąć joystick/jump |
| Liczby | separator tysięcy spacją | „125 430” |

## BUILD (run_code w Studio)
```lua
local StarterGui = game:GetService("StarterGui")
local SPS = game:GetService("StarterPlayer"):WaitForChild("StarterPlayerScripts")
local RS = game:GetService("ReplicatedStorage")
local SSS = game:GetService("ServerScriptService")

for _, o in ipairs({ StarterGui:FindFirstChild("HUD"), SPS:FindFirstChild("HUDClient"),
	RS:FindFirstChild("HUDButtonPressed"), SSS:FindFirstChild("PlayerStatsDefaults") }) do
	if o then o:Destroy() end
end

-- TODO: wklej asset ID
local IMG = {
	Teleport  = "rbxassetid://0",
	Equipment = "rbxassetid://0",
	Pets      = "rbxassetid://0",
	Quests    = "rbxassetid://0",
	Shop      = "rbxassetid://0",
	Guilds    = "rbxassetid://0",
	Frame     = "rbxassetid://0", -- PlayerFrame.png
	Coin      = "rbxassetid://0",
	Gem       = "rbxassetid://0",
}

local INK = Color3.fromHex("1A1410")
local GOLD_RIM = Color3.fromHex("D9B45A")
local WHITE = Color3.new(1, 1, 1)
local LUCKY = Font.fromEnum(Enum.Font.LuckiestGuy)
local REF_H = 1080

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
-- grubosc w px @1080p; HUDClient skaluje do rozdzielczosci
local function stroke(o, px, color, contextual)
	local s = new("UIStroke", { Color = color or INK, Thickness = px, LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = contextual and Enum.ApplyStrokeMode.Contextual or Enum.ApplyStrokeMode.Border }, o)
	s:SetAttribute("BaseThickness", px)
	return s
end
local function grad(o, stops, rot)
	local kp = {}
	for _, s in ipairs(stops) do table.insert(kp, ColorSequenceKeypoint.new(s[1], Color3.fromHex(s[2]))) end
	return new("UIGradient", { Color = ColorSequence.new(kp), Rotation = rot or 90 }, o)
end

new("BindableEvent", { Name = "HUDButtonPressed" }, RS)

local hud = new("ScreenGui", { Name = "HUD", Enabled = false, ResetOnSpawn = false, IgnoreGuiInset = false,
	ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets, ZIndexBehavior = Enum.ZIndexBehavior.Sibling,
	DisplayOrder = 10 }, StarterGui)

----------------------------------------------------------------- PRZYCISKI
local BTN, GAP = 128, 18
local COL_H = BTN * 3 + GAP * 2 -- 420

local function column(name, anchorX, xScale, names)
	local col = new("Frame", { Name = name, BackgroundTransparency = 1, AnchorPoint = Vector2.new(anchorX, 1),
		Position = UDim2.fromScale(xScale, 1 - 60 / REF_H), Size = UDim2.fromScale(0.2, COL_H / REF_H) }, hud)
	new("UIListLayout", { FillDirection = Enum.FillDirection.Vertical, SortOrder = Enum.SortOrder.LayoutOrder,
		VerticalAlignment = Enum.VerticalAlignment.Bottom,
		HorizontalAlignment = anchorX == 0 and Enum.HorizontalAlignment.Left or Enum.HorizontalAlignment.Right,
		Padding = UDim.new(GAP / COL_H, 0) }, col)
	for i, n in ipairs(names) do
		local slot = new("Frame", { Name = n .. "Slot", BackgroundTransparency = 1, LayoutOrder = i,
			Size = UDim2.fromScale(1, BTN / COL_H) }, col)
		new("UIAspectRatioConstraint", { AspectRatio = 1, DominantAxis = Enum.DominantAxis.Height }, slot)
		new("UISizeConstraint", { MinSize = Vector2.new(56, 56), MaxSize = Vector2.new(150, 150) }, slot)
		local b = new("ImageButton", { Name = n, Image = IMG[n], BackgroundTransparency = 1,
			ScaleType = Enum.ScaleType.Fit, AnchorPoint = Vector2.new(0.5, 0.5), Position = UDim2.fromScale(0.5, 0.5),
			Size = UDim2.fromScale(1, 1), AutoButtonColor = false }, slot)
		b:SetAttribute("Side", anchorX == 0 and "Left" or "Right")
		new("UIScale", { Scale = 1 }, b)
	end
end
column("LeftColumn", 0, 40 / 1920, { "Teleport", "Equipment", "Pets" })
column("RightColumn", 1, 1 - 40 / 1920, { "Quests", "Shop", "Guilds" })

----------------------------------------------------------------- PANEL GRACZA
local PW, PH = 470, 212
local panel = new("Frame", { Name = "PlayerPanel", BackgroundTransparency = 1,
	Position = UDim2.fromScale(40 / 1920, 30 / REF_H), Size = UDim2.fromScale(0.5, PH / REF_H) }, hud)
new("UIAspectRatioConstraint", { AspectRatio = PW / PH, DominantAxis = Enum.DominantAxis.Height }, panel)
local function P(o, x, y, w, h) return place(o, PW, PH, x, y, w, h) end

-- ramka (PNG 416x476 -> 180x206)
P(new("ImageLabel", { Name = "FrameArt", Image = IMG.Frame, BackgroundTransparency = 1,
	ScaleType = Enum.ScaleType.Fit, ZIndex = 1 }, panel), 0, 0, 180, 206)
P(new("Frame", { Name = "PortraitSlot", BackgroundTransparency = 1, ZIndex = 2 }, panel), 17, 17, 143, 130)

-- pasek XP nakladany na wypalony pasek z PNG (px w PNG: x66 y371 w284 h87)
local s = 180 / 416
local bx, by, bw, bh = 66 * s, 371 * s, 284 * s, 87 * s
local xpBar = P(new("Frame", { Name = "XPBar", BackgroundColor3 = WHITE, BorderSizePixel = 0, ZIndex = 3,
	ClipsDescendants = true }, panel), bx, by, bw, bh)
corner(xpBar, 10, bh); grad(xpBar, { { 0, "2B3552" }, { 1, "1A2034" } }); stroke(xpBar, 3)
local xpFill = new("Frame", { Name = "XPFill", BackgroundColor3 = WHITE, BorderSizePixel = 0,
	Size = UDim2.fromScale(0, 1), Visible = false, ZIndex = 4 }, xpBar)
corner(xpFill, 8, bh); grad(xpFill, { { 0, "B6F26A" }, { 1, "4CB33C" } })
local hl = new("Frame", { Name = "Highlight", BackgroundColor3 = WHITE, BackgroundTransparency = 0.55,
	BorderSizePixel = 0, Position = UDim2.fromScale(0.04, 0.12), Size = UDim2.fromScale(0.92, 0.22), ZIndex = 5 }, xpFill)
corner(hl, 4, 8)

local level = P(new("TextLabel", { Name = "Level", Text = "1", FontFace = LUCKY, TextScaled = true,
	TextColor3 = WHITE, BackgroundTransparency = 1, ZIndex = 6 }, panel), bx, by + 2, bw, bh - 4)
grad(level, { { 0, "FFF0A8" }, { 0.55, "F2C24A" }, { 1, "B8862A" } })
stroke(level, 4.5, INK, true)

-- waluty
local function currency(y, name, icon, ix, iy, iw, ih, color)
	local ink = P(new("Frame", { Name = name .. "PillInk", BackgroundColor3 = INK, BorderSizePixel = 0, ZIndex = 1 }, panel),
		206, y - 8, 260, 74)
	corner(ink, 37, 74)
	local pill = P(new("Frame", { Name = name .. "Pill", BackgroundColor3 = WHITE, BorderSizePixel = 0, ZIndex = 2 }, panel),
		214, y, 244, 58)
	corner(pill, 29, 58); grad(pill, { { 0, "2B3552" }, { 1, "1A2034" } }); stroke(pill, 4, GOLD_RIM)
	local t = P(new("TextLabel", { Name = name, Text = "0", FontFace = LUCKY, TextScaled = true,
		TextXAlignment = Enum.TextXAlignment.Left, TextColor3 = Color3.fromHex(color),
		BackgroundTransparency = 1, ZIndex = 3 }, panel), 286, y + 9, 165, 40)
	stroke(t, 5, INK, true)
	new("UIScale", { Scale = 1 }, t)
	P(new("ImageLabel", { Name = name .. "Icon", Image = icon, BackgroundTransparency = 1,
		ScaleType = Enum.ScaleType.Fit, ZIndex = 4 }, panel), ix, iy, iw, ih)
end
currency(30, "Gold", IMG.Coin, 190, 18, 82, 81, "FFD23F")
currency(120, "Gems", IMG.Gem, 188, 112, 86, 76, "8AF0FF")

----------------------------------------------------------------- SERVER: domyslne staty
local defaults = new("Script", { Name = "PlayerStatsDefaults" }, SSS)
defaults.Source = [==[
-- PLACEHOLDER: docelowo wartosci z DataStore. HUD czyta atrybuty gracza.
local Players = game:GetService("Players")
local DEFAULTS = { Level = 1, XP = 0, XPMax = 100, Gold = 0, Gems = 0 }
local function init(p)
	for k, v in pairs(DEFAULTS) do
		if p:GetAttribute(k) == nil then p:SetAttribute(k, v) end
	end
end
Players.PlayerAdded:Connect(init)
for _, p in ipairs(Players:GetPlayers()) do init(p) end
]==]

----------------------------------------------------------------- CLIENT
local client = new("LocalScript", { Name = "HUDClient" }, SPS)
client.Source = [==[
local Players = game:GetService("Players")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local RS = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local hud = player:WaitForChild("PlayerGui"):WaitForChild("HUD")
local pressed = RS:WaitForChild("HUDButtonPressed")
local panel = hud:WaitForChild("PlayerPanel")
local xpFill = panel.XPBar.XPFill
local levelLbl, goldLbl, gemsLbl = panel.Level, panel.Gold, panel.Gems

------------------------------------------------ skalowanie obrysow
local function rescale()
	local k = hud.AbsoluteSize.Y / 1080
	if k <= 0 then return end
	for _, d in ipairs(hud:GetDescendants()) do
		if d:IsA("UIStroke") then d.Thickness = math.max((d:GetAttribute("BaseThickness") or 1) * k, 1) end
	end
end
hud:GetPropertyChangedSignal("AbsoluteSize"):Connect(rescale)

------------------------------------------------ staty
local function fmt(n)
	local s = tostring(math.floor(n + 0.5))
	local out = s:reverse():gsub("(%d%d%d)", "%1 "):reverse()
	return (out:gsub("^ ", ""))
end

local function updateXP(instant)
	local xp = player:GetAttribute("XP") or 0
	local max = math.max(player:GetAttribute("XPMax") or 100, 1)
	local p = math.clamp(xp / max, 0, 1)
	local goal = UDim2.fromScale(p, 1)
	if p > 0 then xpFill.Visible = true end
	if instant then
		xpFill.Size = goal
		xpFill.Visible = p > 0
	else
		local t = TS:Create(xpFill, TweenInfo.new(0.4, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = goal })
		t.Completed:Connect(function() xpFill.Visible = p > 0 end)
		t:Play()
	end
end

local function updateLevel()
	levelLbl.Text = tostring(player:GetAttribute("Level") or 1)
end

local shown = { Gold = 0, Gems = 0 }
local function setCurrency(label, key, instant)
	local target = player:GetAttribute(key) or 0
	local from = shown[key]
	shown[key] = target
	if instant or from == target then label.Text = fmt(target) return end
	local nv = Instance.new("NumberValue")
	nv.Value = from
	nv.Changed:Connect(function(v) label.Text = fmt(v) end)
	local t = TS:Create(nv, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Value = target })
	t.Completed:Connect(function() label.Text = fmt(target); nv:Destroy() end)
	t:Play()
	local sc = label:FindFirstChildWhichIsA("UIScale")
	if sc then sc.Scale = 1.18; TS:Create(sc, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play() end
end

player:GetAttributeChangedSignal("XP"):Connect(function() updateXP(false) end)
player:GetAttributeChangedSignal("XPMax"):Connect(function() updateXP(false) end)
player:GetAttributeChangedSignal("Level"):Connect(updateLevel)
player:GetAttributeChangedSignal("Gold"):Connect(function() setCurrency(goldLbl, "Gold") end)
player:GetAttributeChangedSignal("Gems"):Connect(function() setCurrency(gemsLbl, "Gems") end)

------------------------------------------------ czekaj na koniec loadingu (fallback 30 s)
local t0 = os.clock()
while not player:GetAttribute("LoadingDone") and os.clock() - t0 < 30 do task.wait(0.1) end
task.wait(0.7) -- fade loading screena

-- stan poczatkowy bez animacji
updateXP(true); updateLevel()
setCurrency(goldLbl, "Gold", true); setCurrency(gemsLbl, "Gems", true)

------------------------------------------------ mobile: przyciski nad kontrolkami dotykowymi
if UIS.TouchEnabled and not UIS.KeyboardEnabled then
	for _, col in ipairs({ hud.LeftColumn, hud.RightColumn }) do
		col.AnchorPoint = Vector2.new(col.AnchorPoint.X, 0.5)
		col.Position = UDim2.fromScale(col.Position.X.Scale, 0.55)
	end
end

------------------------------------------------ przyciski: stan startowy
local buttons = {}
for _, col in ipairs({ hud.LeftColumn, hud.RightColumn }) do
	for _, slot in ipairs(col:GetChildren()) do
		local b = slot:IsA("Frame") and slot:FindFirstChildWhichIsA("ImageButton")
		if b then
			table.insert(buttons, { btn = b, order = slot.LayoutOrder })
			b.Position = UDim2.fromScale(b:GetAttribute("Side") == "Left" and -1.5 or 2.5, 0.5)
			b.ImageTransparency = 1
		end
	end
end

local panelHome = panel.Position
panel.Position = panelHome - UDim2.fromScale(0, 0.3)

hud.Enabled = true
rescale()

------------------------------------------------ wejscie
TS:Create(panel, TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = panelHome }):Play()
for _, e in ipairs(buttons) do
	task.delay(0.15 + (e.order - 1) * 0.08, function()
		TS:Create(e.btn, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out),
			{ Position = UDim2.fromScale(0.5, 0.5) }):Play()
		TS:Create(e.btn, TweenInfo.new(0.3), { ImageTransparency = 0 }):Play()
	end)
end

------------------------------------------------ hover / press / klik
local quick = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
for _, e in ipairs(buttons) do
	local b = e.btn
	local sc = b:FindFirstChildWhichIsA("UIScale")
	local hovering = false
	local function to(v) TS:Create(sc, quick, { Scale = v }):Play() end
	b.MouseEnter:Connect(function() hovering = true; to(1.08) end)
	b.MouseLeave:Connect(function() hovering = false; to(1) end)
	b.MouseButton1Down:Connect(function() to(0.92) end)
	b.MouseButton1Up:Connect(function() to(hovering and 1.08 or 1) end)
	b.Activated:Connect(function()
		pressed:Fire(b.Name)
		print("[HUD] pressed:", b.Name)
	end)
end
]==]

return "OK: HUD (PlayerPanel + LeftColumn + RightColumn), HUDClient, HUDButtonPressed, PlayerStatsDefaults"
```

## API dla innych skryptów
```lua
-- serwer: zmiana statow (HUD aktualizuje sie sam, z animacja)
player:SetAttribute("XP", 40); player:SetAttribute("XPMax", 100)
player:SetAttribute("Level", 2)
player:SetAttribute("Gold", player:GetAttribute("Gold") + 250)
player:SetAttribute("Gems", 10)

-- klient: klikniecia przyciskow
game:GetService("ReplicatedStorage"):WaitForChild("HUDButtonPressed").Event:Connect(function(name)
	-- "Teleport" | "Equipment" | "Pets" | "Quests" | "Shop" | "Guilds"
end)
```

## Uwagi dla Claude Code
- `Source` skryptów w `run_code` wymaga uprawnień pluginu do skryptów – jeśli blokada, utwórz Script/LocalScript dostępnym narzędziem MCP i wklej treść.
- `XPFill` przy 0 jest ukryty, bo `UICorner` na zerowej szerokości daje artefakt.
- `LuckiestGuy` – cyfry są OK; jeśli coś renderuje się jako kwadraty, zgłoś.
- Atrybuty gracza to tymczasowe źródło danych. Zapis (DataStore) = osobne zadanie – nie implementuj teraz.
- Porównaj wynik ze screenem Figmy (node `9:1571`) i popraw rozjazdy > 2% przed raportem.
