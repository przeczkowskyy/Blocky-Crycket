--[[
	EquipmentPanelClient — okno ekwipunku (Character + Backpack).
	GUI: src/gui/EquipmentPanel.model.json (StarterGui.EquipmentPanel, Enabled = false),
	generowane przez tools/eq_build_gui.py z Figmy (strona „Equipment Panel”, node 23:74).

	Otwieranie: przycisk „Equipment” w HUD (ReplicatedStorage.HUDButtonPressed z HUDClient).
	Zamykanie: przycisk X albo kliknięcie w przyciemnione tło.

	Zdarzenia dla innych skryptów (BindableEvent, tylko klient):
		RS.EquipmentPanelAction.Event:Connect(function(action, arg) ... end)
		action: "Opened" | "Closed" | "Tab" (arg = nazwa zakładki) | "Slot" (arg = np. "Slot_Helmet")
		        | "BagSlot" (arg = numer 1–25) | "Potion" (arg = "Potion1") | "AddStat" (arg = "Strength")
		        | "Move" (arg = { from, to, item }) — przeciągnięcie przedmiotu (Shared.Items)

	Dane (tymczasowo, do czasu modułu statystyk): atrybuty gracza Level oraz
	Strength/Constitution/Intelligence/Dexterity/Luck/Armor; brak atrybutu = wartość z projektu.

	Vault: B&C/UI/Okno ekwipunku.md
]]

local Players = game:GetService("Players")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")
local RS = game:GetService("ReplicatedStorage")

local DESIGN_W = 1376 -- szerokość ramki w Figmie; grubości obrysów w modelu są podane dla tej szerokości
local QUICK = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local HOVER_SCALE, PRESS_SCALE = 1.08, 0.92
local INACTIVE_TAB = Color3.fromRGB(150, 150, 150)

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("EquipmentPanel")
local panel = gui:WaitForChild("Panel")
local backdrop = gui:WaitForChild("Backdrop")
local panelScale = panel:WaitForChild("UIScale")

local function bindable(name)
	local e = RS:FindFirstChild(name)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = name
		e.Parent = RS
	end
	return e
end
local hudPressed = bindable("HUDButtonPressed")
local action = bindable("EquipmentPanelAction")

------------------------------------------------ skalowanie obrysów tekstu
local baseThickness = {}
for _, d in ipairs(panel:GetDescendants()) do
	if d:IsA("UIStroke") and d.ApplyStrokeMode == Enum.ApplyStrokeMode.Contextual then
		baseThickness[d] = d.Thickness
	end
end
local function rescale()
	local k = panel.AbsoluteSize.X / DESIGN_W
	if k <= 0 then
		return
	end
	for s, base in pairs(baseThickness) do
		s.Thickness = math.max(base * k, 1)
	end
end
panel:GetPropertyChangedSignal("AbsoluteSize"):Connect(rescale)

------------------------------------------------ przyciski graficzne: hover / wciśnięcie
local useHover = UIS.MouseEnabled
local function bounce(btn, onClick)
	local sc = btn:FindFirstChildWhichIsA("UIScale")
	local hovering = false
	local function to(v)
		if sc then
			TS:Create(sc, QUICK, { Scale = v }):Play()
		end
	end
	if useHover then
		btn.MouseEnter:Connect(function()
			hovering = true
			to(HOVER_SCALE)
		end)
		btn.MouseLeave:Connect(function()
			hovering = false
			to(1)
		end)
	end
	btn.MouseButton1Down:Connect(function()
		to(PRESS_SCALE)
	end)
	btn.MouseButton1Up:Connect(function()
		to(hovering and HOVER_SCALE or 1)
	end)
	btn.Activated:Connect(function()
		to(hovering and HOVER_SCALE or 1)
		onClick()
	end)
end

------------------------------------------------ sloty (hotspoty): niewidoczne, tylko kliknięcie
local function hotspot(slot, kind, arg)
	slot.Activated:Connect(function()
		action:Fire(kind, arg)
	end)
end

for _, slot in ipairs(panel.Character.EquipSlots:GetChildren()) do
	if slot:IsA("GuiButton") then
		hotspot(slot, "Slot", slot.Name)
	end
end
for _, slot in ipairs(panel.BackpackGrid:GetChildren()) do
	if slot:IsA("GuiButton") then
		hotspot(slot, "BagSlot", tonumber(slot.Name:match("%d+")))
	end
end
for _, slot in ipairs(panel.Potions:GetChildren()) do
	if slot:IsA("GuiButton") then
		hotspot(slot, "Potion", slot.Name)
	end
end

------------------------------------------------ zakładki (osobno postać i plecak)
local function tabGroup(folder, default)
	local tabs = {}
	for _, t in ipairs(folder:GetChildren()) do
		if t:IsA("ImageButton") then
			table.insert(tabs, t)
		end
	end
	local function activate(active)
		for _, t in ipairs(tabs) do
			local on = t == active
			t.ImageColor3 = on and Color3.new(1, 1, 1) or INACTIVE_TAB
			t.ZIndex = on and 2 or 1
			local label = t:FindFirstChild("Label")
			if label then
				label.TextTransparency = on and 0 or 0.25
			end
		end
	end
	for _, t in ipairs(tabs) do
		bounce(t, function()
			activate(t)
			action:Fire("Tab", t.Name)
		end)
	end
	activate(folder:FindFirstChild(default))
end
tabGroup(panel.CharacterTabs, "TabAttributes")
tabGroup(panel.BackpackTabs, "TabWeapons")

------------------------------------------------ statystyki
local function pop(obj, peak)
	local sc = obj:FindFirstChildWhichIsA("UIScale")
	if not sc then
		sc = Instance.new("UIScale")
		sc.Parent = obj
	end
	sc.Scale = peak
	TS:Create(sc, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
end

-- PROPOZYCJA: wzory dobrane tak, żeby dawały wartości z projektu graficznego (STR 20 → DMG ~12 itd.).
-- Docelowe wzory: B&C/Gra/System RPG.md.
local DERIVED = {
	Strength = function(v) return "DMG ~" .. math.floor(v * 0.6) end,
	Constitution = function(v) return "HP " .. v * 12 end,
	Intelligence = function(v) return "DEF " .. math.floor(v / 2) end,
	Dexterity = function(v) return "DEF " .. math.floor(v / 2) end,
	Luck = function(v) return string.format("CRIT %.2f%%", v * 1.25) end,
	Armor = function(v) return "DMG RED " .. math.floor(v * 0.44) .. "%" end,
}

local addStat = RS:WaitForChild("AddStatPoint", 10) -- serwer: src/server/StatPoints.server.luau

for _, card in ipairs(panel.Stats:GetChildren()) do
	-- nazwa karty = statystyka: „Card_Strength” -> „Strength” (atrybuty z .model.json nie przechodzą przez Rojo)
	local stat = card.Name:match("^Card_(.+)$")
	if stat then
		local valueLbl, subLbl = card.StatValue, card.StatSub
		local function refresh(animate)
			local v = player:GetAttribute(stat)
			if typeof(v) ~= "number" then
				return
			end
			valueLbl.Text = tostring(v)
			if DERIVED[stat] then
				subLbl.Text = DERIVED[stat](v)
			end
			if animate then
				pop(valueLbl, 1.4)
				pop(subLbl, 1.15)
			end
		end
		player:GetAttributeChangedSignal(stat):Connect(function()
			refresh(gui.Enabled)
		end)
		refresh(false)
		bounce(card.PlusButton, function()
			pop(card.PlusButton, 1.25)
			if addStat then
				addStat:FireServer(stat) -- TEST: +1 bez kosztu
			end
			action:Fire("AddStat", stat)
		end)
	end
end

------------------------------------------------ przedmioty i przeciąganie (TEST: stan tylko po stronie klienta)
local GuiService = game:GetService("GuiService")
local Items = require(RS:WaitForChild("Shared"):WaitForChild("Items"))
local DRAG_START = 6 -- px ruchu, po których kliknięcie staje się przeciąganiem
local BAG_TABS = { TabWeapons = "Weapons", TabArmor = "Armor", TabAmulets = "Amulets", TabOthers = "Others" }

local equipFolder, bagFolder = panel.Character.EquipSlots, panel.BackpackGrid
local equip = {} -- nazwa slotu ("Slot_Trinket") -> id przedmiotu
local bag = { Weapons = {}, Armor = {}, Amulets = {}, Others = {} } -- kategoria -> [numer slotu 1–25] -> id
local bagTab = "Weapons" -- aktywna zakładka plecaka

local allSlots = {}
for _, folder in ipairs({ equipFolder, bagFolder }) do
	for _, s in ipairs(folder:GetChildren()) do
		if s:IsA("GuiButton") then
			table.insert(allSlots, s)
		end
	end
end

local function isBag(slot)
	return slot.Parent == bagFolder
end
local function bagIndex(slot)
	return tonumber(slot.Name:match("%d+"))
end
local function get(slot)
	if isBag(slot) then
		return bag[bagTab][bagIndex(slot)]
	end
	return equip[slot.Name]
end
local function set(slot, id)
	if isBag(slot) then
		bag[bagTab][bagIndex(slot)] = id
	else
		equip[slot.Name] = id
	end
end

local function render(slot)
	local id = get(slot)
	slot.Icon.Image = id and Items[id].icon or ""
	slot.Icon.ImageTransparency = 0
	slot.Icon.Rotation = 0
	-- zasłonka wypalonej sylwetki (hełm, sakiewka…): tylko gdy w slocie leży przedmiot
	local cover = slot:FindFirstChild("Cover")
	if cover then
		cover.Visible = id ~= nil
	end
end
local function renderAll()
	for _, s in ipairs(allSlots) do
		render(s)
	end
end

local function fitsEquip(slot, id)
	return id == nil or Items[id].slot == "Any" or "Slot_" .. Items[id].slot == slot.Name
end

local function shake(obj)
	-- „nie pasuje”: krótkie potrząśnięcie ikoną (bez ramek)
	task.spawn(function()
		for _, r in ipairs({ 12, -10, 7, -4, 0 }) do
			TS:Create(obj, TweenInfo.new(0.05), { Rotation = r }):Play()
			task.wait(0.05)
		end
	end)
end

-- odkłada przedmiot na stronę plecaka jego kategorii (preferowany numer slotu albo pierwszy wolny)
local function storeInBag(id, prefer)
	local page = bag[Items[id].category]
	if prefer and page[prefer] == nil then
		page[prefer] = id
		return prefer
	end
	for i = 1, 25 do
		if page[i] == nil then
			page[i] = id
			return i
		end
	end
	return nil
end

local function hintTab(category)
	local tab = panel.BackpackTabs:FindFirstChild("Tab" .. category)
	if tab then
		pop(tab, 1.2)
	end
end

local function move(from, target)
	local moving, there = get(from), get(target)
	if isBag(target) then
		local cat = Items[moving].category
		if cat ~= bagTab then
			-- inna zakładka: przedmiot trafia na stronę swojej kategorii (tu znika z widoku)
			if not storeInBag(moving, bagIndex(target)) then
				return false
			end
			set(from, nil)
			hintTab(cat)
			return true
		end
		if there and not isBag(from) and not fitsEquip(from, there) then
			return false -- zamiana: przedmiot z plecaka nie pasuje do slotu, z którego przyszliśmy
		end
	elseif not fitsEquip(target, moving) then
		return false
	end
	set(target, moving)
	set(from, nil)
	if there then
		if isBag(from) or fitsEquip(from, there) then
			set(from, there)
		else
			storeInBag(there)
		end
	end
	return true
end

local function screenPos(input)
	-- Uwaga: AbsolutePosition w Roblox jest zawsze liczone POD paskiem Robloxa (także gdy ScreenGui ma
	-- IgnoreGuiInset = true), tak samo jak InputObject.Position. Porównujemy więc wprost, bez insetu.
	return Vector2.new(input.Position.X, input.Position.Y)
end

local function slotAt(pos)
	for _, s in ipairs(allSlots) do
		local p, z = s.AbsolutePosition, s.AbsoluteSize
		if pos.X >= p.X and pos.X <= p.X + z.X and pos.Y >= p.Y and pos.Y <= p.Y + z.Y then
			return s
		end
	end
	return nil
end

local drag -- { from = slot, start = Vector2, ghost = ImageLabel? }

UIS.InputBegan:Connect(function(input)
	local t = input.UserInputType
	if not gui.Enabled or drag or (t ~= Enum.UserInputType.MouseButton1 and t ~= Enum.UserInputType.Touch) then
		return
	end
	local pos = screenPos(input)
	local s = slotAt(pos)
	if s and get(s) then
		drag = { from = s, start = pos }
	end
end)

UIS.InputChanged:Connect(function(input)
	if not drag then
		return
	end
	local t = input.UserInputType
	if t ~= Enum.UserInputType.MouseMovement and t ~= Enum.UserInputType.Touch then
		return
	end
	local pos = screenPos(input)
	if not drag.ghost and (pos - drag.start).Magnitude >= DRAG_START then
		local g = Instance.new("ImageLabel")
		g.Name = "DragGhost"
		g.BackgroundTransparency = 1
		g.Image = Items[get(drag.from)].icon
		g.AnchorPoint = Vector2.new(0.5, 0.5)
		g.Size = UDim2.fromOffset(drag.from.Icon.AbsoluteSize.X * 1.15, drag.from.Icon.AbsoluteSize.Y * 1.15)
		g.ZIndex = 50
		g.Parent = gui
		drag.ghost = g
		drag.from.Icon.ImageTransparency = 0.6
	end
	if drag.ghost then
		-- ScreenGui ignoruje pasek, więc do pozycji rysowania dodajemy jego wysokość
		local inset = GuiService:GetGuiInset()
		drag.ghost.Position = UDim2.fromOffset(pos.X + inset.X, pos.Y + inset.Y)
	end
end)

UIS.InputEnded:Connect(function(input)
	local t = input.UserInputType
	if not drag or (t ~= Enum.UserInputType.MouseButton1 and t ~= Enum.UserInputType.Touch) then
		return
	end
	local d = drag
	drag = nil
	if not d.ghost then
		return -- zwykłe kliknięcie (obsługuje hotspot)
	end
	d.ghost:Destroy()
	local target = slotAt(screenPos(input))
	local item = get(d.from)
	if target and target ~= d.from and move(d.from, target) then
		renderAll()
		if get(target) == item then
			pop(target.Icon, 1.25)
		end
		action:Fire("Move", { from = d.from.Name, to = target.Name, item = item })
	else
		render(d.from)
		if target and target ~= d.from then
			shake(d.from.Icon) -- ten przedmiot tu nie pasuje: wraca i się trzęsie
		end
	end
end)

-- zmiana zakładki plecaka = inna strona plecaka
action.Event:Connect(function(a, name)
	if a == "Tab" and BAG_TABS[name] then
		bagTab = BAG_TABS[name]
		renderAll()
	end
end)

-- przedmiot testowy
equip.Slot_Trinket = "Scrap"
renderAll()

local levelLbl = panel.Character.LevelBadge.LevelText
local function refreshLevel()
	levelLbl.Text = "LV " .. tostring(player:GetAttribute("Level") or 1)
end
player:GetAttributeChangedSignal("Level"):Connect(refreshLevel)
refreshLevel()

------------------------------------------------ otwieranie / zamykanie
local isOpen, busy = false, false

local function open()
	if isOpen or busy then
		return
	end
	isOpen = true
	gui.Enabled = true
	rescale()
	backdrop.BackgroundTransparency = 1
	panelScale.Scale = 0.85
	TS:Create(backdrop, TweenInfo.new(0.2), { BackgroundTransparency = 0.45 }):Play()
	TS:Create(panelScale, TweenInfo.new(0.28, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	action:Fire("Opened")
end

local function close()
	if not isOpen or busy then
		return
	end
	busy = true
	TS:Create(backdrop, TweenInfo.new(0.15), { BackgroundTransparency = 1 }):Play()
	local t = TS:Create(panelScale, TweenInfo.new(0.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.85 })
	t.Completed:Connect(function()
		gui.Enabled = false
		isOpen, busy = false, false
		action:Fire("Closed")
	end)
	t:Play()
end

bounce(panel.CloseButton, close)
backdrop.Activated:Connect(close)

hudPressed.Event:Connect(function(name)
	if name == "Equipment" then
		if isOpen then
			close()
		else
			open()
		end
	end
end)
