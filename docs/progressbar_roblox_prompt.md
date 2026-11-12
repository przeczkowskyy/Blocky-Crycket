# Claude Code → Roblox Studio (MCP): Loading Screen + Progress Bar „Blocky&Crycket”

## Zadanie
Odtwórz w Roblox Studio (przez Roblox Studio MCP: `run_code` / odpowiednik) ekran ładowania z progress barem zaprojektowanym w Figmie. Pasek budujemy NATYWNIE z GUI (Frame/CanvasGroup/UIGradient/UIStroke/UICorner) — skalowalny i animowany, nie jako jeden obrazek. Tło = obraz key-artu wgrany jako asset.

## Źródła
- Figma – komponent paska (źródło prawdy dla wyglądu): https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=2-2
- Figma – kadr ekranu 2752×1536 (pozycja paska): https://www.figma.com/design/BbLd4jDnvxAmOWZN1hAZQJ?node-id=2-75
- Podgląd docelowy: `blocky_crycket_loading_screen.png` (tło + pasek), referencja paska: `progressbar_68.png`
- Jeśli masz Figma MCP: `get_screenshot` na node `2:2` i porównaj z wynikiem w Studio.

## Kroki
1. **Tło:** poproś mnie o asset ID key-artu (wgrywam czysty background przez Asset Manager → Images, kopiuję `rbxassetid://…`). Do tego czasu zostaw `rbxassetid://0`.
2. **Build:** uruchom w Studio skrypt `BUILD` (niżej) przez MCP `run_code`. Tworzy:
   - `ReplicatedFirst.LoadingScreen` (ScreenGui – szablon)
   - `ReplicatedFirst.LoadingClient` (LocalScript – runtime + preload + tween)
3. **Weryfikacja:** Play Solo → screenshot → porównaj z `progressbar_68.png`. Popraw rozjazdy (kolory, proporcje, grubości obrysów).
4. **Sprawdź fonty:** `LuckiestGuy` może nie mieć glifu „Ł” – jeśli brak, ustaw tekst „LADOWANIE PRZYGODY...” albo użyj `FredokaOne`.
5. Nie twórz nic poza tymi 2 obiektami. Raport: co zbudowano + screenshot.

## Spec (design 1600×300 px, wszystko liczone w Scale względem tego)
| Element | x,y,w,h | Styl |
|---|---|---|
| Label „ŁADOWANIE PRZYGODY...” | 0,0,1600,70 | LuckiestGuy, #FFF1BF, obrys #2B1A10 9px, cień |
| Stone Frame | 0,86,1600,144, r30 | gradient pion. #B9BEC8→#8D929E→#5F6470, obrys 8px |
| Nity ×4 | (26,104),(1554,104),(26,192),(1554,192) 20×20 | #E3E6EC→#7C8190, obrys 4px |
| Track (drewno) | 70,118,1460,80, r18 | #6E4627→#4A2D17, obrys 6px, deski co 146px (#2E1A0C 55%) |
| Fill | w = 1460×progress | gradient poz. #1BA9DA→#41F5D6, ukośne paski białe 16% (−30°), highlight biały 50%, cień dół #0B5E86 35% |
| Spark | środek na końcu Fill, 56×56 | pikselowy krzyż 8px biały/#FFE46B, glow cyjan |
| Gemy L/P | środki (4,158),(1596,158) | romb złoty 74px #FFE07A→#D18A12 + ametyst 46px #F2A6FF→#B54BF0→#6A1FB8 |
| Percent | środek tracku | LuckiestGuy, #FFD23F, obrys 8px |
| Tip | 0,250,1600,40 | font pikselowy (Arcade), biały, obrys 5px |
| Pozycja na ekranie | szer. 58% ekranu, wyśrodkowany, dół −2.6% | + winieta dół 30% (#0E0820 do 75%) |

## BUILD (run_code w Studio)
```lua
local RF = game:GetService("ReplicatedFirst")
for _, n in ipairs({"LoadingScreen", "LoadingClient"}) do
	local o = RF:FindFirstChild(n); if o then o:Destroy() end
end

local BG_IMAGE = "rbxassetid://0" -- TODO: asset ID key-artu
local DW, DH = 1600, 300
local INK = Color3.fromRGB(43, 26, 16)
local function rgb(h) return Color3.fromHex(h) end

local function new(class, props, parent)
	local o = Instance.new(class)
	for k, v in pairs(props) do o[k] = v end
	o.Parent = parent
	return o
end
-- design px -> scale wzgledem rodzica o wymiarach pw x ph
local function place(o, pw, ph, x, y, w, h)
	o.Position = UDim2.fromScale(x / pw, y / ph)
	o.Size = UDim2.fromScale(w / pw, h / ph)
	return o
end
local function corner(o, r, shortSide) new("UICorner", { CornerRadius = UDim.new(r / shortSide, 0) }, o) end
local function stroke(o, px, contextual)
	local s = new("UIStroke", { Color = INK, Thickness = px, LineJoinMode = Enum.LineJoinMode.Round,
		ApplyStrokeMode = contextual and Enum.ApplyStrokeMode.Contextual or Enum.ApplyStrokeMode.Border }, o)
	s:SetAttribute("BaseThickness", px) -- skalowane w runtime
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
corner(stone, 30, 144); stroke(stone, 4)
grad(stone, { { 0, "#B9BEC8" }, { 0.5, "#8D929E" }, { 1, "#5F6470" } })
local stoneShadow = frame(bar, DW, DH, 0, 96, 1600, 144, INK, "StoneShadow")
stoneShadow.BackgroundTransparency = 0.45; stoneShadow.ZIndex = 0; corner(stoneShadow, 30, 144)
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

-- Fill (CanvasGroup = przycina obrocone paski)
local fill = new("CanvasGroup", { Name = "Fill", BackgroundColor3 = Color3.new(1, 1, 1), BorderSizePixel = 0,
	Size = UDim2.fromScale(0.68, 1), ZIndex = 4 }, track)
corner(fill, 18, TH)
grad(fill, { { 0, "#1BA9DA" }, { 1, "#41F5D6" } }, 0)
local inner = new("Frame", { Name = "Inner", BackgroundTransparency = 1, Size = UDim2.new(0, 1000, 1, 0) }, fill) -- szer. = px tracku (runtime)
for i = 0, 28 do
	local s = new("Frame", { Name = "Stripe", BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.84,
		BorderSizePixel = 0, Rotation = -30, ZIndex = 5 }, inner)
	s.Position = UDim2.fromScale((i * 56 - 40) / TW, -0.25); s.Size = UDim2.fromScale(22 / TW, 1.6)
end
local hl = new("Frame", { Name = "Highlight", BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.5,
	BorderSizePixel = 0, ZIndex = 6, Position = UDim2.new(0, 0, 9 / TH, 0), Size = UDim2.new(1, 0, 16 / TH, 0) }, fill)
corner(hl, 8, 16)
hl.Position = UDim2.new(0.01, 0, 9 / TH, 0); hl.Size = UDim2.new(0.98, 0, 16 / TH, 0)
local shade = new("Frame", { Name = "Shade", BackgroundColor3 = rgb("#0B5E86"), BackgroundTransparency = 0.65,
	BorderSizePixel = 0, ZIndex = 6, Position = UDim2.fromScale(0, 62 / TH), Size = UDim2.fromScale(1, 18 / TH) }, fill)
local fillStroke = stroke(fill, 2.5)

-- Spark (pixel cross)
local spark = new("Frame", { Name = "Spark", BackgroundTransparency = 1, AnchorPoint = Vector2.new(0.5, 0.5),
	Position = UDim2.fromScale((70 + TW * 0.68) / DW, 158 / DH), Size = UDim2.fromScale(56 / DW, 56 / DH), ZIndex = 8 }, bar)
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

RF:RemoveDefaultLoadingScreen()
local gui = RF:WaitForChild("LoadingScreen"):Clone()
gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")

local bar = gui.ProgressBar
local track, fill, spark = bar.Track, bar.Track.Fill, bar.Spark
local pct, pctShadow, tip, tipShadow = bar.Percent, bar.PercentShadow, bar.Tip, bar.TipShadow
local DW, TW = 1600, 1460

local TIPS = {
	"WSKAZÓWKA: Twierdza produkuje złoto, nawet gdy jesteś w dungeonie!",
	"WSKAZÓWKA: Pety dają bonusy do statystyk – ulepszaj je!",
	"WSKAZÓWKA: Na arenie zdobywasz chwałę i rzadkie nagrody.",
	"WSKAZÓWKA: Sklep z magią odświeża ofertę co jakiś czas.",
}

-- skalowanie obrysow do rozmiaru paska
local function rescale()
	local k = bar.AbsoluteSize.X / DW * 2
	for _, d in ipairs(gui:GetDescendants()) do
		if d:IsA("UIStroke") then d.Thickness = (d:GetAttribute("BaseThickness") or 1) * k end
	end
	fill.Inner.Size = UDim2.new(0, track.AbsoluteSize.X, 1, 0)
end
bar:GetPropertyChangedSignal("AbsoluteSize"):Connect(rescale)
rescale()

local shown = 0
local function setProgress(p)
	p = math.clamp(p, 0, 1)
	local info = TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TS:Create(fill, info, { Size = UDim2.fromScale(math.max(p, 0.02), 1) }):Play()
	TS:Create(spark, info, { Position = UDim2.fromScale((70 + TW * p) / DW, spark.Position.Y.Scale) }):Play()
	local txt = math.floor(p * 100 + 0.5) .. "%"
	pct.Text, pctShadow.Text = txt, txt
	shown = p
end

task.spawn(function()
	local i = 0
	while gui.Parent do
		i = i % #TIPS + 1
		tip.Text, tipShadow.Text = TIPS[i], TIPS[i]
		task.wait(4)
	end
end)

setProgress(0)
CP:PreloadAsync({ gui })
if not game:IsLoaded() then game.Loaded:Wait() end

local assets = RS:GetDescendants()
local total, BATCH = math.max(#assets, 1), 25
for s = 1, #assets, BATCH do
	CP:PreloadAsync(table.move(assets, s, math.min(s + BATCH - 1, #assets), 1, {}))
	setProgress(math.min(s + BATCH - 1, #assets) / total)
end
setProgress(1)
task.wait(0.8)

-- fade out
local cg = Instance.new("CanvasGroup")
cg.Size, cg.BackgroundTransparency = UDim2.fromScale(1, 1), 1
cg.Parent = gui
for _, c in ipairs(gui:GetChildren()) do if c ~= cg then c.Parent = cg end end
TS:Create(cg, TweenInfo.new(0.6), { GroupTransparency = 1 }):Play()
task.wait(0.65)
gui:Destroy()
]==]

return "OK: ReplicatedFirst.LoadingScreen + LoadingClient"
```

## Uwagi dla Claude Code
- `client.Source` w `run_code` wymaga uprawnień pluginu do skryptów – jeśli zablokowane, utwórz LocalScript ręcznie przez dostępne narzędzie MCP i wklej treść.
- Grubości `UIStroke` są w px (bazowe dla ~800px szer. paska), runtime je skaluje → wygląda tak samo na mobile i PC.
- Kolejność warstw (ZIndex): StoneShadow 0 → Stone 1 → Rivets 2 → Track 3 → Fill 4–6 → Spark 8 → Gems 9–11 → Percent 12.
- Po zbudowaniu: Play Solo, screenshot, porównaj z `progressbar_68.png`, popraw, raportuj.
