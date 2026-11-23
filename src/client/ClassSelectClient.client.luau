--[[
	ClassSelectClient — ekran wyboru klasy po ekranie ładowania (ScreenGui „ClassSelect”, src/gui/ClassSelect.model.json).
	Projekt: B&C/UI/Selektor bohatera.md (propozycja). Dane: ReplicatedStorage.Shared.ClassData.

	- Kamera stoi w sali Workspace/WyborKlasy (swiat/wybor_klasy) i patrzy na podest.
	- Trzy modele (kopie z ReplicatedStorage.WyborKlasyModele, tylko u tego gracza) stoją na kole na podeście;
	  strzałki / klawisze ←→ (A/D) obracają koło o jedną klasę, wybrana stoi z przodu.
	- Karta statystyk po lewej pokazuje wybraną klasę. PLAY (albo Enter) → serwer ustawia atrybut "Class",
	  ekran znika, kamera wraca do gracza, HUD się pokazuje.
	- Po PLAY ten sam ekran przechodzi w WYBÓR RASY (D-079, Paweł 17.11): znikają strzałki i pozostali bohaterowie,
	  na podeście zostaje jeden goły model, tytuł „CHOOSE YOUR RACE”, karta po lewej pokazuje wybraną klasę, a po prawej
	  panel z siedmioma okrągłymi przyciskami ras (Półbóg — premium, zablokowany). PLAY → serwer ustawia atrybut "Race".
	- Nastrój: na czas ekranu gracz ma u siebie nocne światło sali (ClassData.Scene.mood), ognie migoczą, bohaterowie
	  mają komiksowy obrys, kamera lekko podąża za myszką. Po PLAY wszystko wraca do ustawień miejsca.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local Lighting = game:GetService("Lighting")

local ClassData = require(RS:WaitForChild("Shared"):WaitForChild("ClassData"))
local Icons = require(RS:WaitForChild("Shared"):WaitForChild("ClassSelectIcons"))
local chooseEvent = RS:WaitForChild("ChooseClass")
local RaceData = require(RS:WaitForChild("Shared"):WaitForChild("RaceData"))
local okIcons, RaceIcons = pcall(function()
	return require(RS:WaitForChild("Shared"):WaitForChild("RaceIcons"))
end)

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("ClassSelect")
local card = gui:WaitForChild("StatsCard")
local vignette = gui:WaitForChild("Vignette")
local SC = ClassData.Scene
local CLASSES = ClassData.Classes
local N = #CLASSES
local QUICK = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local POP = TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local LOADING_TIMEOUT = 25

------------------------------------------------------------ klasa już wybrana?
-- Scenę (kamera, modele, nocne światło) skrypt ustawia od razu, jeszcze POD ekranem ładowania — światła sali zdążą się
-- rozjaśnić, zanim gracz ją zobaczy. Sam ekran pokazuje się dopiero po sygnale "LoadingDone".
-- Klasę może przywrócić zapis (StanGracza Karola wczytuje atrybut "Class"), a rasy zapis nie zna — wtedy ekran
-- otwiera się od razu na wyborze rasy, z zapisaną klasą. Bez tego HUD czeka na "Race" w nieskończoność (Paweł 23.11).
local maEkranRas = RS:WaitForChild("ChooseRace", 10) ~= nil -- zdarzenie tworzy serwer w trakcie gry
if player:GetAttribute("Class") and (player:GetAttribute("Race") or not maEkranRas) then
	return -- klasa (i rasa) już wybrane (np. po odrodzeniu skryptu)
end
local tylkoRasa = player:GetAttribute("Class") ~= nil

local modelsFolder = RS:WaitForChild("WyborKlasyModele", 20)
if not modelsFolder then
	warn("[ClassSelect] brak ReplicatedStorage.WyborKlasyModele — wybieram klasę domyślną")
	chooseEvent:FireServer(CLASSES[1].id)
	return
end

------------------------------------------------------------ sala daleko od gracza: przy streamingu trzeba ją wczytać
if workspace.StreamingEnabled then
	pcall(function()
		player:RequestStreamAroundAsync(SC.center, 10)
	end)
	local tw = os.clock()
	while not workspace:FindFirstChild("WyborKlasy") and os.clock() - tw < 10 do
		task.wait(0.1)
	end
end

------------------------------------------------------------ nastrój sali: noc i ogień (tylko u gracza, do PLAY)
local MOOD = SC.mood
local savedLighting: { [any]: any } = {}
local moodEffects: { Instance } = {}
local function applyMood()
	if not MOOD then
		return
	end
	for _, k in ipairs({ "Ambient", "OutdoorAmbient", "EnvironmentDiffuseScale", "EnvironmentSpecularScale", "ExposureCompensation" }) do
		savedLighting[k] = (Lighting :: any)[k]
	end
	Lighting.Ambient = MOOD.ambient
	Lighting.OutdoorAmbient = MOOD.ambient
	Lighting.EnvironmentDiffuseScale = MOOD.envDiffuse
	Lighting.EnvironmentSpecularScale = MOOD.envSpecular
	Lighting.ExposureCompensation = savedLighting.ExposureCompensation + (MOOD.exposure or 0)
	for _, a in ipairs(Lighting:GetChildren()) do
		if a:IsA("Atmosphere") then -- mgła miejsca zszarzałaby głąb sali
			savedLighting[a] = a.Density
			a.Density = 0
		elseif a:IsA("BloomEffect") and MOOD.hidePlaceBloom and a.Enabled then
			-- Bloom miejsca rozlewał poświatę wokół ognia, świec i latarni (Paweł 24.11) — wyłączony do PLAY
			savedLighting[a] = true
			a.Enabled = false
		end
	end
	local cc = Instance.new("ColorCorrectionEffect")
	cc.Name = "ClassSelectKolor"
	cc.TintColor, cc.Contrast, cc.Saturation = MOOD.tint, MOOD.contrast, MOOD.saturation
	cc.Parent = Lighting
	local bloom = Instance.new("BloomEffect")
	bloom.Name = "ClassSelectBlask"
	bloom.Intensity, bloom.Size, bloom.Threshold = MOOD.bloomIntensity, MOOD.bloomSize, MOOD.bloomThreshold
	bloom.Parent = Lighting
	moodEffects = { cc, bloom }
end
local function restoreMood()
	for k, v in pairs(savedLighting) do
		if typeof(k) == "string" then
			(Lighting :: any)[k] = v
		elseif k.Parent then
			if k:IsA("BloomEffect") then
				k.Enabled = v
			else
				k.Density = v
			end
		end
	end
	for _, e in ipairs(moodEffects) do
		e:Destroy()
	end
end

-- ognie w sali migoczą: światła z atrybutem "Migot" (Workspace/WyborKlasy/Efekty, tools/studio/deploy_classselect.py)
type Flicker = { light: Light, base: number, amp: number, seed: number }
local flicker: { Flicker } = {}
do
	local sala = workspace:FindFirstChild("WyborKlasy")
	local efekty = sala and sala:FindFirstChild("Efekty")
	if efekty then
		for _, d in ipairs(efekty:GetDescendants()) do
			local amp = d:IsA("Light") and d:GetAttribute("Migot")
			if amp then
				table.insert(flicker, { light = d :: Light, base = (d :: Light).Brightness, amp = amp, seed = #flicker * 7.31 })
			end
		end
	end
end

------------------------------------------------------------ na czas wyboru: tylko ten ekran (polecenie Pawła 16.11)
-- inne ScreenGui gracza są wyłączane i trzymane wyłączone (także te, które ktoś włączy w trakcie), elementy Robloxa
-- (czat, lista graczy, plecak, pasek u góry) schowane; po PLAY wszystko wraca
local StarterGui = game:GetService("StarterGui")
local pg = player:WaitForChild("PlayerGui")
local hidden: { [ScreenGui]: boolean } = {}
local watchers = {}
local function hideGui(g: Instance)
	if not g:IsA("ScreenGui") or g == gui then
		return
	end
	if g.Enabled then
		hidden[g] = true
		g.Enabled = false
	end
	table.insert(watchers, g:GetPropertyChangedSignal("Enabled"):Connect(function()
		if g.Enabled then
			hidden[g] = true
			g.Enabled = false
		end
	end))
end
local function setCore(on: boolean)
	pcall(function()
		StarterGui:SetCoreGuiEnabled(Enum.CoreGuiType.All, on)
	end)
	pcall(function()
		StarterGui:SetCore("TopbarEnabled", on)
	end)
end
-- podpowiedzi „E” (ProximityPrompt) przy postaci gracza — np. portal obok spawnu — też chowamy do PLAY
local PPS = game:GetService("ProximityPromptService")
local promptsWereEnabled = PPS.Enabled
local function hideOthers()
	promptsWereEnabled = PPS.Enabled
	PPS.Enabled = false
	for _, g in ipairs(pg:GetChildren()) do
		hideGui(g)
	end
	table.insert(watchers, pg.ChildAdded:Connect(hideGui))
	setCore(false)
end
local function restoreOthers()
	PPS.Enabled = promptsWereEnabled
	for _, c in ipairs(watchers) do
		c:Disconnect()
	end
	for g in pairs(hidden) do
		if g.Parent then
			g.Enabled = true
		end
	end
	setCore(true)
end

------------------------------------------------------------ modele na kole
local stage = Instance.new("Folder")
stage.Name = "WyborKlasyLokalne"
stage.Parent = workspace

type Hero = { model: Model, base: CFrame, frontYaw: number, offsetY: number, angle: number }
local heroes: { Hero } = {}

local function yawOf(v: Vector3): number
	return math.atan2(v.X, v.Z)
end

local function makeHero(src: Model, angle: number): Hero
	local m = src:Clone()
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
		elseif d:IsA("Script") or d:IsA("LocalScript") then
			d:Destroy()
		end
	end
	m.Parent = stage
	local hl = Instance.new("Highlight") -- komiksowy obrys sylwetki, jak rekwizyty sali
	hl.Name = "ObrysKomiksowy"
	hl.FillTransparency = 1
	hl.OutlineColor = Color3.fromRGB(24, 20, 18)
	hl.OutlineTransparency = 0
	hl.DepthMode = Enum.HighlightDepthMode.Occluded
	hl.Adornee = m
	hl.Parent = m
	local pivot = m:GetPivot()
	local cf, size = m:GetBoundingBox()
	local hrp = m:FindFirstChild("HumanoidRootPart", true)
	local front = (hrp and hrp:IsA("BasePart") and hrp.CFrame.LookVector) or pivot.LookVector
	-- atrybut na modelu może odwrócić przód (gdy import ma przód na plecach)
	if m:GetAttribute("FrontFlip") then
		front = -front
	end
	return {
		model = m,
		base = pivot - pivot.Position,
		frontYaw = yawOf(Vector3.new(front.X, 0, front.Z)),
		offsetY = pivot.Position.Y - (cf.Position.Y - size.Y / 2),
		angle = angle,
	}
end

for i, c in ipairs(CLASSES) do
	local src = modelsFolder:FindFirstChild(c.model)
	if src and src:IsA("Model") then
		-- 2. klasa (Zwiadowca) po lewej, 3. (Mag) po prawej
		table.insert(heroes, makeHero(src, -(i - 1) * 2 * math.pi / N))
	end
end

local rot, rotTarget, index = 0, 0, 1
local hopAt = -10 -- chwila ostatniej zmiany klasy: wybrany bohater lekko podskakuje
local mode = "class" -- "class" → "race" (ekran wyboru rasy w tej samej sali)
local function place(dt: number?)
	rot += (rotTarget - rot) * math.clamp((dt or 1) * 9, 0, 1)
	local now = os.clock()
	for k, h in ipairs(heroes) do
		local a = h.angle - rot
		a = math.atan2(math.sin(a), math.cos(a)) -- do zakresu ±180° (inaczej po obrocie koła postać staje tyłem)
		local hop = (k == (mode == "race" and 1 or index)) and math.sin(math.clamp((now - hopAt) / 0.34, 0, 1) * math.pi) * 0.45 or 0
		local pos = SC.center + Vector3.new(SC.ringRadius * math.sin(a), h.offsetY + hop, SC.ringRadius * math.cos(a))
		local front = math.abs(math.atan2(math.sin(a), math.cos(a))) < 0.3
		local sway = front and math.sin(now * 1.6) * 0.1 or 0
		-- przód modelu patrzy w stronę kamery (+Z), boczni lekko ku środkowi
		local wantYaw = a * SC.sideTurn + sway
		local delta = wantYaw - h.frontYaw
		h.model:PivotTo(CFrame.new(pos) * CFrame.Angles(0, delta, 0) * h.base)
	end
end

------------------------------------------------------------ karta statystyk
local function showClass(animate: boolean)
	local c = CLASSES[index]
	card.ClassTitle.Text = c.name
	-- kolor klasy: nazwa i paski (Wojownik niebieski, Zwiadowca zielony, Mag fioletowy)
	local top, bottom = c.color[1], c.color[2]
	card.ClassTitle.TextColor3 = top
	local grad = ColorSequence.new(top, bottom)
	card.Subtitle.Text = c.subtitle
	card.Emblem.Image = Icons[c.emblem] or ""
	for s = 1, 6 do
		local fill = card["Bar" .. s].Fill
		local g = fill:FindFirstChildOfClass("UIGradient")
		if g then
			g.Color = grad
		end
		local goal = UDim2.fromScale(math.clamp(c.stats[s] / ClassData.BAR_FULL, 0.04, 1), 1)
		if animate then
			TS:Create(fill, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = goal }):Play()
		else
			fill.Size = goal
		end
	end
	if animate then
		local sc = card:FindFirstChildWhichIsA("UIScale")
		if sc then
			sc.Scale = 0.96
			TS:Create(sc, POP, { Scale = 1 }):Play()
		end
	end
end

-- dir = +1 (strzałka w prawo): na przód wychodzi postać stojąca po prawej
local function step(dir: number)
	index = (index - 1 - dir) % N + 1
	rotTarget += dir * 2 * math.pi / N
	hopAt = os.clock() + 0.12
	showClass(true)
end

------------------------------------------------------------ przyciski
local function bounce(btn: GuiButton, onClick: () -> ())
	local sc = btn:FindFirstChildWhichIsA("UIScale")
	btn.MouseEnter:Connect(function()
		if sc then
			TS:Create(sc, QUICK, { Scale = 1.08 }):Play()
		end
	end)
	btn.MouseLeave:Connect(function()
		if sc then
			TS:Create(sc, QUICK, { Scale = 1 }):Play()
		end
	end)
	btn.MouseButton1Down:Connect(function()
		if sc then
			TS:Create(sc, QUICK, { Scale = 0.92 }):Play()
		end
	end)
	btn.Activated:Connect(function()
		if sc then
			TS:Create(sc, POP, { Scale = 1 }):Play()
		end
		onClick()
	end)
end

local cam = workspace.CurrentCamera
local oldFov = cam.FieldOfView
local renderConn
local finished = false

local raceIndex = 1
local chooseRace = RS:WaitForChild("ChooseRace", 10) :: RemoteEvent
local function finish()
	if finished then
		return
	end
	finished = true
	if mode == "race" then
		local race = RaceData.Races[raceIndex]
		chooseRace:FireServer(race.id)
	else
		chooseEvent:FireServer(CLASSES[index].id)
	end
	-- krótkie zaciemnienie, powrót kamery do gracza, sprzątanie
	vignette.BackgroundTransparency = 1
	local t = TS:Create(vignette, TweenInfo.new(0.25), { BackgroundTransparency = 0 })
	t:Play()
	t.Completed:Wait()
	if renderConn then
		renderConn:Disconnect()
	end
	stage:Destroy()
	restoreMood()
	for _, f in ipairs(flicker) do
		f.light.Brightness = f.base
	end
	cam.FieldOfView = oldFov
	cam.CameraType = Enum.CameraType.Custom
	local char = player.Character
	local hum = char and char:FindFirstChildOfClass("Humanoid")
	if hum then
		cam.CameraSubject = hum
	end
	gui.Enabled = false
	restoreOthers()
	-- odsłonięcie świata: winieta jest częścią tego ekranu, więc krótki czarny ekran robi osobna warstwa
	local fade = Instance.new("ScreenGui")
	fade.Name = "ClassSelectFade"
	fade.IgnoreGuiInset, fade.DisplayOrder = true, 100
	local f = Instance.new("Frame")
	f.Size = UDim2.fromScale(1, 1)
	f.BackgroundColor3 = Color3.new(0, 0, 0)
	f.BorderSizePixel = 0
	f.Parent = fade
	fade.Parent = pg
	TS:Create(f, TweenInfo.new(0.4), { BackgroundTransparency = 1 }):Play()
	task.delay(0.45, function()
		fade:Destroy()
	end)
end

------------------------------------------------------------ ekran wyboru rasy (ta sama sala, D-079)
local racePanel = gui:FindFirstChild("RacePanel")
local raceHero: Hero? = nil
local skinParts: { BasePart } = {}

local function pickSkin(m: Model)
	-- skóra = kolor największej WIDOCZNEJ bryły przy kości głowy (kości rigu Karola są niewidzialne); potem wszystkie
	-- widoczne bryły w tym kolorze. Dopóki nie ma modeli ras, rasa zmienia kolor skóry (D-079)
	local head = m:FindFirstChild("Head", true)
	if not (head and head:IsA("BasePart")) then
		return
	end
	local best, bestVol = nil, 0
	for _, d in ipairs(m:GetDescendants()) do
		local o = d:IsA("BasePart") and head.CFrame:PointToObjectSpace(d.Position) or nil
		local h = head.Size / 2
		if o and d ~= head and (d :: BasePart).Transparency < 1
			and math.abs(o.X) < h.X and math.abs(o.Y) < h.Y and math.abs(o.Z) < h.Z then -- środek bryły w klocku głowy
			local v = d.Size.X * d.Size.Y * d.Size.Z
			if v > bestVol then
				best, bestVol = d, v
			end
		end
	end
	if not best then
		return
	end
	local ref = best.Color
	for _, d in ipairs(m:GetDescendants()) do
		if d:IsA("BasePart") and d.Transparency < 1 then
			local c = d.Color
			if math.abs(c.R - ref.R) + math.abs(c.G - ref.G) + math.abs(c.B - ref.B) < 0.12 then
				table.insert(skinParts, d)
			end
		end
	end
end

-- broń startowa klasy w prawej dłoni figury rasy (Paweł 18.11): model WyborKlasyModele.Weapon_<id klasy> (Handle +
-- części, układ RightGripAttachment; budowa: tools/studio/deploy_classselect.py z swiat/postacie/bronie_startowe.py).
-- Figura stoi zakotwiczona, więc „pozę trzymania” robimy wprost: przedramię (wszystko pod łokciem) obracamy do przodu
-- wokół stawu łokcia, a broń stawiamy na zaczepie dłoni — wtedy stoi pionowo przed postacią.
local HOLD_ELBOW = math.rad(80)
local function holdWeapon(h: Hero)
	local m = h.model
	local w = modelsFolder:FindFirstChild("Weapon_" .. CLASSES[index].id)
	-- koty ras (D-145): kocia wersja broni (krótsza i grubsza, tools/studio/bronie_kot.py), gdy jest
	if m:GetAttribute("BronDoGlowy") then
		w = modelsFolder:FindFirstChild("Weapon_" .. CLASSES[index].id .. "_Kot") or w
	end
	local elbow = m:FindFirstChild("RightElbow", true)
	if elbow and elbow:IsA("Motor6D") and elbow.Part0 and elbow.Part1 then
		-- kości od łokcia w dół (przedramię, dłoń) i bryły do nich przyspawane
		local moving: { [BasePart]: boolean } = { [elbow.Part1 :: BasePart] = true }
		local grew = true
		while grew do
			grew = false
			for _, d in ipairs(m:GetDescendants()) do
				if d:IsA("JointInstance") or d:IsA("WeldConstraint") then
					local a, b = (d :: any).Part0, (d :: any).Part1
					if a and b and d ~= elbow then
						if moving[a] and not moving[b] then
							moving[b] = true
							grew = true
						elseif moving[b] and not moving[a] and d:IsA("WeldConstraint") then
							moving[a] = true
							grew = true
						end
					end
				end
			end
		end
		local pivot = (elbow.Part0 :: BasePart).CFrame * elbow.C0
		-- figura jest zakotwiczona: stawy i spawy wyłączamy, inaczej przesunięcie jednej części ciągnie całe ciało
		for _, d in ipairs(m:GetDescendants()) do
			if d:IsA("JointInstance") or d:IsA("WeldConstraint") then
				(d :: any).Enabled = false
			end
		end
		local root = m:FindFirstChild("HumanoidRootPart")
		local right = if root and root:IsA("BasePart") then root.CFrame.RightVector else m:GetPivot().RightVector
		local turn = CFrame.new(pivot.Position) * CFrame.fromAxisAngle(right, HOLD_ELBOW) * CFrame.new(-pivot.Position)
		for part in pairs(moving) do
			part.CFrame = turn * part.CFrame
		end
	end
	-- zaczep dłoni: RightGripAttachment, a gdy figura go nie ma (wystawa ras) — ten sam układ co u bohaterów Karola:
	-- środek części RightHand, obrót −90° w osi X
	local grip = m:FindFirstChild("RightGripAttachment", true)
	local hand = m:FindFirstChild("RightHand", true)
	local gripCF: CFrame? = nil
	if grip and grip:IsA("Attachment") then
		gripCF = grip.WorldCFrame
	elseif hand and hand:IsA("BasePart") then
		gripCF = hand.CFrame * CFrame.Angles(-math.pi / 2, 0, 0)
	end
	if not (w and w:IsA("Model") and gripCF) then
		return
	end
	local c = w:Clone()
	for _, d in ipairs(c:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
		end
	end
	c:PivotTo(gripCF :: CFrame)
	-- koty ras (Paweł 24.11, D-145): broń z modeli dla ludzików jest za długa — pomniejszamy ją tak, żeby szczyt broni
	-- sięgał najwyżej do czubka głowy kota (jak na referencji). Tylko figury z atrybutem BronDoGlowy.
	if m:GetAttribute("BronDoGlowy") then
		local head = m:FindFirstChild("Head", true)
		if head and head:IsA("BasePart") then
			local szczytGlowy = head.Position.Y + head.Size.Y / 2
			local wcf, ws = c:GetBoundingBox()
			local szczytBroni = wcf.Position.Y + ws.Y / 2
			local chwytY = (gripCF :: CFrame).Position.Y
			if szczytBroni > szczytGlowy and szczytBroni - chwytY > 0.01 then
				local k = math.clamp((szczytGlowy - chwytY) / (szczytBroni - chwytY), 0.3, 1)
				c:ScaleTo(c:GetScale() * k)
				c:PivotTo(gripCF :: CFrame)
			end
		end
		-- Paweł 24.11: broń bliżej końca łapki — odsunięta od głowy w bok (w prawo figury) i lekko do przodu, żeby kostur
		-- nie wchodził w głowę kota. Przesunięcie w układzie figury (prawo, góra, przód) w studach: atrybut
		-- BronPrzesuniecie (Vector3) na modelu rasy, domyślnie (0.55, 0, 0.25).
		local root = m:FindFirstChild("HumanoidRootPart")
		local uklad = if root and root:IsA("BasePart") then root.CFrame else m:GetPivot()
		local przes = m:GetAttribute("BronPrzesuniecie")
		local v = if typeof(przes) == "Vector3" then przes else Vector3.new(0.55, 0, 0.25)
		c:PivotTo(c:GetPivot() + uklad.RightVector * v.X + uklad.UpVector * v.Y + uklad.LookVector * v.Z)
	end
	c.Parent = m
end

local function showRace(animate: boolean)
	local r = RaceData.Races[raceIndex]
	if not racePanel then
		return
	end
	racePanel.RaceName.Text = r.name
	racePanel.RaceName.TextColor3 = r.color
	racePanel.RaceTrait.Text = r.trait
	local btn = racePanel:FindFirstChild("Race" .. r.id)
	if btn then
		local ring = racePanel.SelectedRing
		local goal = { Position = btn.Position }
		if animate then
			TS:Create(ring, QUICK, goal):Play()
		else
			ring.Position = btn.Position
		end
	end
	-- model rasy z wystawy Karola (WyborKlasyModele.Race_<id>); bez niego: goły model w kolorze skóry rasy
	local raceModel = modelsFolder:FindFirstChild("Race_" .. r.id)
	if raceModel and raceModel:IsA("Model") then
		for _, h in ipairs(heroes) do
			h.model:Destroy()
		end
		table.clear(heroes)
		table.clear(skinParts)
		raceHero = makeHero(raceModel, 0)
		holdWeapon(raceHero :: Hero)
		table.insert(heroes, raceHero :: Hero)
		place()
	else
		for _, p in ipairs(skinParts) do
			if animate then
				TS:Create(p, TweenInfo.new(0.25), { Color = r.skin }):Play()
			else
				p.Color = r.skin
			end
		end
	end
	if animate then
		hopAt = os.clock()
		local sc = racePanel.RaceName:FindFirstChildOfClass("UIScale")
		if not sc then
			sc = Instance.new("UIScale")
			sc.Parent = racePanel.RaceName
		end
		sc.Scale = 1.15
		TS:Create(sc, POP, { Scale = 1 }):Play()
	end
end

local function stepRace(dir: number)
	raceIndex = (raceIndex - 1 + dir) % #RaceData.Races + 1
	showRace(true)
end

local function enterRace()
	if mode ~= "class" or finished then
		return
	end
	chooseEvent:FireServer(CLASSES[index].id)
	if not racePanel or not chooseRace then
		finish() -- brak panelu ras w GUI: zachowanie jak dawniej
		return
	end
	mode = "race"
	-- znikają strzałki i bohaterowie klas; na podeście jeden goły model (z kopii WyborKlasyModele.Base)
	for _, name in ipairs({ "ArrowLeft", "ArrowRight" }) do
		local b = gui:FindFirstChild(name)
		local sc = b and b:FindFirstChildWhichIsA("UIScale")
		if sc then
			TS:Create(sc, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.In), { Scale = 0 }):Play()
		end
		task.delay(0.22, function()
			if b then
				b.Visible = false
			end
		end)
	end
	local src = modelsFolder:FindFirstChild("Base") or modelsFolder:FindFirstChild(CLASSES[index].model)
	for _, h in ipairs(heroes) do
		h.model:Destroy()
	end
	table.clear(heroes)
	if src and src:IsA("Model") then
		raceHero = makeHero(src, 0)
		holdWeapon(raceHero :: Hero)
		table.insert(heroes, raceHero :: Hero)
		pickSkin((raceHero :: Hero).model)
	end
	rot, rotTarget = 0, 0
	local title = gui.TitlePlank:FindFirstChild("Title")
	if title then
		title.Text = "CHOOSE YOUR RACE"
	end
	-- panel ras wjeżdża z prawej
	local home = racePanel.Position
	racePanel.Position = home + UDim2.fromScale(0.4, 0)
	racePanel.Visible = true
	TS:Create(racePanel, TweenInfo.new(0.5, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Position = home }):Play()
	for i, r in ipairs(RaceData.Races) do
		local b = racePanel:FindFirstChild("Race" .. r.id)
		if b then
			if okIcons and RaceIcons[r.icon] then
				b.Image = RaceIcons[r.icon]
			end
			local sc = b:FindFirstChildWhichIsA("UIScale")
			if sc then
				sc.Scale = 0
				TS:Create(sc, TweenInfo.new(0.35, Enum.EasingStyle.Back, Enum.EasingDirection.Out, 0, false, 0.2 + 0.05 * i),
					{ Scale = 1 }):Play()
			end
		end
	end
	hopAt = os.clock()
	showRace(false)
end

local function confirmRace()
	local r = RaceData.Races[raceIndex]
	if r.premium then
		-- Półbóg: rasa premium (D-080) — jeszcze nie do kupienia; krótkie potrząśnięcie panelu
		TS:Create(racePanel, TweenInfo.new(0.05, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, 3, true), { Rotation = 3 }):Play()
		return
	end
	finish()
end

if racePanel then
	for i, r in ipairs(RaceData.Races) do
		local b = racePanel:FindFirstChild("Race" .. r.id)
		if b and b:IsA("GuiButton") then
			bounce(b, function()
				if mode == "race" and raceIndex ~= i then
					raceIndex = i
					showRace(true)
				end
			end)
		end
	end
end

bounce(gui:WaitForChild("ArrowLeft"), function()
	step(-1)
end)
bounce(gui:WaitForChild("ArrowRight"), function()
	step(1)
end)
bounce(gui:WaitForChild("PlayButton"), function()
	if mode == "class" then
		enterRace()
	else
		confirmRace()
	end
end)

UIS.InputBegan:Connect(function(input, processed)
	if processed or finished or not gui.Enabled then
		return
	end
	local k = input.KeyCode
	local left = k == Enum.KeyCode.Left or k == Enum.KeyCode.A
	local right = k == Enum.KeyCode.Right or k == Enum.KeyCode.D
	if left or right then
		if mode == "race" then
			stepRace(right and 1 or -1)
		else
			step(right and 1 or -1)
		end
	elseif k == Enum.KeyCode.Return or k == Enum.KeyCode.KeypadEnter then
		if mode == "class" then
			enterRace()
		else
			confirmRace()
		end
	end
end)

------------------------------------------------------------ start
if tylkoRasa then
	for i, c in ipairs(CLASSES) do
		if c.id == player:GetAttribute("Class") then
			index = i
		end
	end
end
cam.CameraType = Enum.CameraType.Scriptable
cam.CFrame = CFrame.lookAt(SC.camPos, SC.camLook)
cam.Focus = CFrame.new(SC.center)
cam.FieldOfView = SC.fov
applyMood()
place()
showClass(false)
-- po CameraModule (priorytet Camera + 1): kamera i punkt skupienia na podeście — Roblox rysuje detale i światła
-- wokół Camera.Focus, więc bez tego sala daleko od postaci się nie pokazuje
local FOCUS = CFrame.new(SC.center)
local BASE = CFrame.lookAt(SC.camPos, SC.camLook)
local PARALLAX = SC.parallax or 0
local par = Vector2.zero
RunService:BindToRenderStep("ClassSelectCam", Enum.RenderPriority.Camera.Value + 1, function(dt)
	local now = os.clock()
	-- kamera: stałe ujęcie + lekkie odsunięcie za myszką i powolne kołysanie (widać głębię sali)
	local want = Vector2.zero
	if PARALLAX > 0 and UIS.MouseEnabled then
		local m, vp = UIS:GetMouseLocation(), cam.ViewportSize
		if vp.X > 0 and vp.Y > 0 then
			want = Vector2.new(math.clamp(m.X / vp.X - 0.5, -0.5, 0.5), math.clamp(m.Y / vp.Y - 0.5, -0.5, 0.5)) * 2
		end
	end
	par = par:Lerp(want, math.clamp(dt * 3, 0, 1))
	local off = BASE.RightVector * (par.X * PARALLAX + math.sin(now * 0.35) * 0.1)
		+ BASE.UpVector * (-par.Y * PARALLAX * 0.5 + math.sin(now * 0.27) * 0.05)
	cam.CameraType = Enum.CameraType.Scriptable
	cam.CFrame = CFrame.lookAt(SC.camPos + off, SC.camLook)
	cam.Focus = FOCUS
	for _, f in ipairs(flicker) do
		local n = math.noise(now * 6, f.seed) + 0.5 * math.noise(now * 17, f.seed + 3.1)
		f.light.Brightness = f.base * (1 + f.amp * n * 1.5)
	end
	place(dt)
end)
renderConn = { Disconnect = function()
	RunService:UnbindFromRenderStep("ClassSelectCam")
end }

------------------------------------------------------------ pokaż ekran po ekranie ładowania
local t0 = os.clock()
while not player:GetAttribute("LoadingDone") and os.clock() - t0 < LOADING_TIMEOUT do
	task.wait(0.1)
end
hideOthers()
vignette.BackgroundTransparency = 0
gui.Enabled = true
TS:Create(vignette, TweenInfo.new(0.6, Enum.EasingStyle.Quad, Enum.EasingDirection.Out, 0, false, 0.35), { BackgroundTransparency = 1 }):Play()

-- wejście elementów: tabliczka z góry, karta z lewej, przyciski wyskakują po kolei
do
	local BACK = Enum.EasingStyle.Back
	local plank = gui:FindFirstChild("TitlePlank")
	if plank and plank:IsA("GuiObject") then
		local home = plank.Position
		plank.Position = home - UDim2.fromScale(0, 0.4)
		TS:Create(plank, TweenInfo.new(0.6, BACK, Enum.EasingDirection.Out, 0, false, 0.15), { Position = home }):Play()
	end
	local homeCard = card.Position
	card.Position = homeCard - UDim2.fromScale(0.4, 0)
	TS:Create(card, TweenInfo.new(0.55, BACK, Enum.EasingDirection.Out, 0, false, 0.25), { Position = homeCard }):Play()
	for i, name in ipairs({ "ArrowLeft", "ArrowRight", "PlayButton" }) do
		local b = gui:FindFirstChild(name)
		local sc = b and b:FindFirstChildWhichIsA("UIScale")
		if sc then
			sc.Scale = 0
			TS:Create(sc, TweenInfo.new(0.4, BACK, Enum.EasingDirection.Out, 0, false, 0.4 + 0.08 * i), { Scale = 1 }):Play()
		end
	end
end

-- klasa z zapisu: od razu wybór rasy (także gdy zapis ustawi klasę chwilę po starcie tego skryptu)
local function naRase()
	if mode ~= "class" or finished or not maEkranRas then
		return
	end
	for i, c in ipairs(CLASSES) do
		if c.id == player:GetAttribute("Class") then
			index = i
		end
	end
	showClass(false)
	enterRace()
end
-- klasa mogła przyjść z zapisu w trakcie ekranu ładowania (przed podłączeniem nasłuchu niżej)
if tylkoRasa or player:GetAttribute("Class") then
	task.wait(0.6)
	naRase()
end
player:GetAttributeChangedSignal("Class"):Connect(function()
	if player:GetAttribute("Class") then
		naRase()
	end
end)
