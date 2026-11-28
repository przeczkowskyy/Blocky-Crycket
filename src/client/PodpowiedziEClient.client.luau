--!strict
-- Własne okienka podpowiedzi interakcji („E · Zagraj”) zamiast bazowych okienek ProximityPrompt Robloxa
-- (Paweł 28.11: „okna interakcji pod nasz kreskowy styl, z lekką ciemną obwódką, popodmieniać z tych bazowych”).
--
-- Jak to działa: każdy ProximityPrompt w Workspace dostaje u gracza styl Custom (zmiana tylko lokalna, na czas gry —
-- skrypty i części Karola, które tworzą podpowiedzi, nie są zmieniane), a ProximityPromptService.PromptShown /
-- PromptHidden rysuje naszą tabliczkę. Działanie podpowiedzi (klawisz, zasięg, przytrzymanie, Triggered) zostaje
-- silnikowe; dotyk i mysz obsługuje przycisk na tabliczce (InputHoldBegin / InputHoldEnd).
-- Wygląd: kremowa tabliczka z ciemną obwódką, żółty klawisz z literą, nazwa obiektu na ciemnej plakietce nad akcją.
-- Grafiki z Higgsfield (zestaw PodpowiedzE) podmienią rysowane ramki po zgodzie Pawła na wgranie — tabela OBRAZY.
-- Wyłączenie: atrybut gracza PodpowiedziWlasne = false przywraca bazowe okienka Robloxa.
local Players = game:GetService("Players")
local PPS = game:GetService("ProximityPromptService")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")

local player = Players.LocalPlayer
local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local TUSZ = Color3.fromRGB(46, 32, 34)
local KREM = Color3.fromRGB(252, 236, 200)
local ZLOTO = Color3.fromRGB(255, 204, 64)
local DREWNO = Color3.fromRGB(96, 62, 44)

-- po wgraniu grafik: rbxassetid tabliczki, plakietki nazwy, klawisza i przycisku dotyku (puste = rysowane ramki)
local OBRAZY = { tabliczka = "", plakietka = "", klawisz = "", dotyk = "" }

local NAZWY_KLAWISZY: { [Enum.KeyCode]: string } = {
	[Enum.KeyCode.ButtonX] = "X", [Enum.KeyCode.ButtonY] = "Y", [Enum.KeyCode.ButtonA] = "A", [Enum.KeyCode.ButtonB] = "B",
	[Enum.KeyCode.Return] = "↵", [Enum.KeyCode.Space] = "␣",
}

local function wlaczone(): boolean
	return player:GetAttribute("PodpowiedziWlasne") ~= false
end

local function obrys(rodzic: Instance, grubosc: number, kolor: Color3?)
	local s = Instance.new("UIStroke")
	s.Thickness, s.Color = grubosc, kolor or TUSZ
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = rodzic
end
local function rog(rodzic: Instance, promien: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(promien, 0)
	c.Parent = rodzic
end
local function napis(rodzic: Instance, tekst: string, kolor: Color3, obrysTekstu: number): TextLabel
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.FontFace, l.TextScaled, l.TextColor3, l.Text = FONT, true, kolor, tekst
	if obrysTekstu > 0 then
		local s = Instance.new("UIStroke")
		s.Thickness, s.Color = obrysTekstu, TUSZ
		s.Parent = l
	end
	l.Parent = rodzic
	return l
end
local function tlo(rodzic: Instance, obraz: string, kolor: Color3, promien: number): GuiObject
	if obraz ~= "" then
		local i = Instance.new("ImageLabel")
		i.BackgroundTransparency, i.Image, i.ScaleType = 1, obraz, Enum.ScaleType.Stretch
		i.Size = UDim2.fromScale(1, 1)
		i.Parent = rodzic
		return i
	end
	local f = Instance.new("Frame")
	f.BackgroundColor3, f.BorderSizePixel = kolor, 0
	f.Size = UDim2.fromScale(1, 1)
	rog(f, promien)
	obrys(f, 3)
	f.Parent = rodzic
	return f
end

type Okno = { gui: BillboardGui, skala: UIScale, pasek: Frame?, polaczenia: { RBXScriptConnection } }
local okna: { [ProximityPrompt]: Okno } = {}

local function zbuduj(prompt: ProximityPrompt, wejscie: Enum.ProximityPromptInputType): Okno
	local maObiekt = prompt.ObjectText ~= ""
	local gui = Instance.new("BillboardGui")
	gui.Name = "PodpowiedzE"
	gui.AlwaysOnTop, gui.LightInfluence, gui.ResetOnSpawn = true, 0, false
	gui.Size = UDim2.fromOffset(300, if maObiekt then 96 else 66)
	gui.SizeOffset = Vector2.new(prompt.UIOffset.X / 300, 0.5 + prompt.UIOffset.Y / 96)
	gui.Adornee = prompt.Parent
	gui.Active = true
	local skala = Instance.new("UIScale")
	skala.Scale = 0.6
	skala.Parent = gui

	-- plakietka z nazwą obiektu (nad akcją)
	if maObiekt then
		local plak = Instance.new("Frame")
		plak.BackgroundTransparency = 1
		plak.AnchorPoint, plak.Position, plak.Size = Vector2.new(0.5, 0), UDim2.fromScale(0.5, 0), UDim2.new(0.74, 0, 0, 30)
		plak.Parent = gui
		tlo(plak, OBRAZY.plakietka, DREWNO, 0.5)
		local l = napis(plak, prompt.ObjectText, KREM, 0)
		l.AnchorPoint, l.Position, l.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.88, 0.62)
	end

	-- tabliczka akcji: klawisz po lewej, napis po prawej; cała jest przyciskiem (dotyk i mysz)
	local tab = Instance.new("TextButton")
	tab.Name = "Tabliczka"
	tab.Text, tab.BackgroundTransparency, tab.AutoButtonColor = "", 1, false
	tab.AnchorPoint, tab.Position, tab.Size = Vector2.new(0.5, 1), UDim2.fromScale(0.5, 1), UDim2.new(1, -8, 0, 60)
	tab.Parent = gui
	tlo(tab, OBRAZY.tabliczka, KREM, 0.32)
	local klawisz = Instance.new("Frame")
	klawisz.BackgroundTransparency = 1
	klawisz.AnchorPoint, klawisz.Position, klawisz.Size = Vector2.new(0, 0.5), UDim2.new(0, 8, 0.5, 0), UDim2.fromOffset(46, 46)
	klawisz.Parent = tab
	if wejscie == Enum.ProximityPromptInputType.Touch then
		tlo(klawisz, OBRAZY.dotyk, Color3.fromRGB(64, 196, 204), 0.5)
		local l = napis(klawisz, "👆", Color3.new(1, 1, 1), 0)
		l.AnchorPoint, l.Position, l.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.62, 0.62)
	else
		tlo(klawisz, OBRAZY.klawisz, ZLOTO, 0.24)
		local kod = if wejscie == Enum.ProximityPromptInputType.Gamepad then prompt.GamepadKeyCode else prompt.KeyboardKeyCode
		local tekst = NAZWY_KLAWISZY[kod] or UIS:GetStringForKeyCode(kod)
		if tekst == "" then
			tekst = kod.Name
		end
		local l = napis(klawisz, tekst, Color3.new(1, 1, 1), 2.5)
		l.AnchorPoint, l.Position, l.Size = Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), UDim2.fromScale(0.66, 0.66)
	end
	local akcja = napis(tab, if prompt.ActionText ~= "" then prompt.ActionText else "Interact", TUSZ, 0)
	akcja.AnchorPoint, akcja.Position, akcja.Size = Vector2.new(0, 0.5), UDim2.new(0, 64, 0.5, 0), UDim2.new(1, -78, 0.56, 0)
	akcja.TextXAlignment = Enum.TextXAlignment.Left
	local limit = Instance.new("UITextSizeConstraint")
	limit.MaxTextSize, limit.MinTextSize = 28, 10
	limit.Parent = akcja

	-- pasek przytrzymania (tylko gdy podpowiedź wymaga przytrzymania)
	local pasek: Frame? = nil
	if prompt.HoldDuration > 0 then
		local tor = Instance.new("Frame")
		tor.BackgroundColor3, tor.BorderSizePixel = Color3.fromRGB(214, 190, 150), 0
		tor.AnchorPoint, tor.Position, tor.Size = Vector2.new(0, 1), UDim2.new(0, 64, 1, -7), UDim2.new(1, -80, 0, 6)
		rog(tor, 0.5)
		tor.Parent = tab
		local p = Instance.new("Frame")
		p.BackgroundColor3, p.BorderSizePixel = Color3.fromRGB(96, 196, 84), 0
		p.Size = UDim2.fromScale(0, 1)
		rog(p, 0.5)
		p.Parent = tor
		pasek = p
	end

	local okno: Okno = { gui = gui, skala = skala, pasek = pasek, polaczenia = {} }
	local function dodaj(c: RBXScriptConnection)
		table.insert(okno.polaczenia, c)
	end
	dodaj(tab.InputBegan:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then
			prompt:InputHoldBegin()
		end
	end))
	dodaj(tab.InputEnded:Connect(function(input)
		if input.UserInputType == Enum.UserInputType.Touch or input.UserInputType == Enum.UserInputType.MouseButton1 then
			prompt:InputHoldEnd()
		end
	end))
	dodaj(prompt.PromptButtonHoldBegan:Connect(function()
		TS:Create(skala, TweenInfo.new(0.08), { Scale = 0.94 }):Play()
		if pasek then
			pasek.Size = UDim2.fromScale(0, 1)
			TS:Create(pasek, TweenInfo.new(prompt.HoldDuration, Enum.EasingStyle.Linear), { Size = UDim2.fromScale(1, 1) }):Play()
		end
	end))
	dodaj(prompt.PromptButtonHoldEnded:Connect(function()
		TS:Create(skala, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
		if pasek then
			TS:Create(pasek, TweenInfo.new(0.12), { Size = UDim2.fromScale(0, 1) }):Play()
		end
	end))
	gui.Parent = player:WaitForChild("PlayerGui")
	TS:Create(skala, TweenInfo.new(0.2, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	return okno
end

local function zamknij(prompt: ProximityPrompt)
	local okno = okna[prompt]
	if not okno then
		return
	end
	okna[prompt] = nil
	for _, c in ipairs(okno.polaczenia) do
		c:Disconnect()
	end
	local t = TS:Create(okno.skala, TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.5 })
	t:Play()
	task.delay(0.12, function()
		okno.gui:Destroy()
	end)
end

PPS.PromptShown:Connect(function(prompt, wejscie)
	if prompt.Style ~= Enum.ProximityPromptStyle.Custom or not wlaczone() then
		return
	end
	zamknij(prompt)
	okna[prompt] = zbuduj(prompt, wejscie)
end)
PPS.PromptHidden:Connect(zamknij)

-- każda podpowiedź w Workspace dostaje u gracza styl Custom (także te, które powstaną później)
local function przejmij(d: Instance)
	if d:IsA("ProximityPrompt") then
		if wlaczone() then
			if d.Style == Enum.ProximityPromptStyle.Default then
				d:SetAttribute("PodpowiedzBazowa", true)
				d.Style = Enum.ProximityPromptStyle.Custom
			end
		elseif d:GetAttribute("PodpowiedzBazowa") then
			d.Style = Enum.ProximityPromptStyle.Default
		end
	end
end
for _, d in ipairs(workspace:GetDescendants()) do
	przejmij(d)
end
workspace.DescendantAdded:Connect(przejmij)
player:GetAttributeChangedSignal("PodpowiedziWlasne"):Connect(function()
	for _, d in ipairs(workspace:GetDescendants()) do
		przejmij(d)
	end
end)
