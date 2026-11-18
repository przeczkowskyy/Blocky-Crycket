--[[
	ShopClient — okno sklepu (ScreenGui „Shop”, src/gui/Shop.model.json, generator tools/shop_build_gui.py).
	Dwa wyglądy w jednym oknie: sklep z bronią (Blocky za ladą) i sklep magiczny (Crycket za ladą); po lewej
	ekwipunek gracza, po prawej towar. Projekt: B&C/UI/Sklepy i bronie startowe — prompty.md (propozycja).

	Otwieranie (Paweł 18.11: „okna otwierają się klikając na naszych sklepikarzy”):
	- E przy sprzedawcy: pakiet Karola swiat/miasteczko_bazar_gra wysyła ReplicatedStorage.OknoMiejsca (BindableEvent,
	  tylko klient) z id „zbrojownia” albo „sklep_magiczny” (D-084) — tu je odbieramy;
	- kliknięcie / dotknięcie samego sprzedawcy (Zbrojmistrz, Mag w Workspace/MiasteczkoBazar) z bliska.
	PLACEHOLDER: sloty są puste, towaru, cen i odświeżania jeszcze nie ma (czeka na projekt sklepu).
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("Shop")
local panel = gui:WaitForChild("Panel")
local backdrop = gui:WaitForChild("Backdrop")
local panelScale = panel:WaitForChild("UIScale")

local QUICK = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local ZASIEG_KLIKU = 22 -- studów: sprzedawcę klika się z bliska (jak E)

local SKLEPY = {
	zbrojownia = { art = "ArtBron", tytul = "WEAPON SHOP", model = "Zbrojmistrz", budynek = "Zbrojownia" },
	sklep_magiczny = { art = "ArtMagia", tytul = "MAGIC SHOP", model = "Mag", budynek = "SklepMagiczny" },
}

local function bindable(name: string): BindableEvent
	local e = RS:FindFirstChild(name)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = name
		e.Parent = RS
	end
	return e :: BindableEvent
end

-- okno zgłasza się pakietowi Karola: przy E nie pokaże dymku „sklep w budowie”
local okna = bindable("OknoMiejsca")
okna:SetAttribute("zbrojownia", true)
okna:SetAttribute("sklep_magiczny", true)

------------------------------------------------------------ otwieranie i zamykanie
local otwarte: string? = nil
local zamykanie = false

local function open(id: string)
	local s = SKLEPY[id]
	if not s then
		return
	end
	otwarte = id
	zamykanie = false
	for _, k in pairs(SKLEPY) do
		panel[k.art].Visible = k == s
	end
	panel.TitleRight.Text = s.tytul
	panel.Level.Text = "LV " .. tostring(player:GetAttribute("Level") or 1)
	gui.Enabled = true
	backdrop.BackgroundTransparency = 1
	TS:Create(backdrop, TweenInfo.new(0.2), { BackgroundTransparency = 0.45 }):Play()
	panelScale.Scale = 0.8
	TS:Create(panelScale, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

local function close()
	if zamykanie or not gui.Enabled then
		return
	end
	zamykanie = true
	otwarte = nil
	TS:Create(backdrop, TweenInfo.new(0.15), { BackgroundTransparency = 1 }):Play()
	local t = TS:Create(panelScale, TweenInfo.new(0.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.85 })
	t.Completed:Connect(function()
		if zamykanie then
			gui.Enabled = false
		end
	end)
	t:Play()
end

okna.Event:Connect(function(id)
	if typeof(id) == "string" and SKLEPY[id] then
		open(id)
	end
end)

------------------------------------------------------------ przyciski wypalone w grafice: cień przy najechaniu / wciśnięciu
local function hitButton(btn: GuiButton, onClick: () -> ())
	local shade = Instance.new("Frame")
	shade.Name = "Shade"
	shade.Size = UDim2.fromScale(1, 1)
	shade.BackgroundColor3 = Color3.new(0, 0, 0)
	shade.BackgroundTransparency = 1
	shade.BorderSizePixel = 0
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0.2, 0)
	c.Parent = shade
	shade.Parent = btn
	btn.MouseEnter:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 0.85 }):Play()
	end)
	btn.MouseLeave:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 1 }):Play()
	end)
	btn.MouseButton1Down:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 0.7 }):Play()
	end)
	btn.Activated:Connect(function()
		TS:Create(shade, QUICK, { BackgroundTransparency = 1 }):Play()
		onClick()
	end)
end

hitButton(panel:WaitForChild("CloseButton"), close)
hitButton(panel:WaitForChild("RerollButton"), function()
	-- PLACEHOLDER: odświeżenie towaru — sama animacja przycisku, dopóki nie ma towaru
end)
for i = 1, 6 do
	local s = panel:FindFirstChild("ShopSlot" .. i)
	if s then
		hitButton(s, function() end)
	end
end
backdrop.Activated:Connect(close)
UIS.InputBegan:Connect(function(input, processed)
	if not processed and gui.Enabled and input.KeyCode == Enum.KeyCode.Escape then
		close()
	end
end)

------------------------------------------------------------ kliknięcie na sprzedawcę
local function sklepZModelu(inst: Instance?): string?
	local bazar = workspace:FindFirstChild("MiasteczkoBazar")
	if not (inst and bazar) then
		return nil
	end
	for id, s in pairs(SKLEPY) do
		local b = bazar:FindFirstChild(s.budynek)
		local m = b and b:FindFirstChild(s.model)
		if m and inst:IsDescendantOf(m) then
			return id
		end
	end
	return nil
end

local function kliknij(pos: Vector2)
	if gui.Enabled then
		return
	end
	local cam = workspace.CurrentCamera
	local ray = cam:ScreenPointToRay(pos.X, pos.Y) -- pozycja z InputObject jest bez paska u góry
	local params = RaycastParams.new()
	params.FilterType = Enum.RaycastFilterType.Exclude
	params.FilterDescendantsInstances = { player.Character }
	local hitR = workspace:Raycast(ray.Origin, ray.Direction * 200, params)
	local id = hitR and sklepZModelu(hitR.Instance)
	if not id then
		return
	end
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart")
	if root and (root.Position - hitR.Position).Magnitude <= ZASIEG_KLIKU then
		open(id)
	end
end

UIS.InputEnded:Connect(function(input, processed)
	if processed then
		return
	end
	local t = input.UserInputType
	if t == Enum.UserInputType.MouseButton1 or t == Enum.UserInputType.Touch then
		kliknij(Vector2.new(input.Position.X, input.Position.Y))
	end
end)
