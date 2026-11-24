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
local HOVER_SCALE, PRESS_SCALE = 1.08, 1.0 -- wciśnięcie nie zmniejsza poniżej 1 (nic spod przycisku nie wychodzi)
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

------------------------------------------------ sloty broni według klasy (Paweł 18.11)
-- Tło okna ma wypalony slot broni z mieczem. Nakładka (obrazek z ramką wyciętą z tego samego tła,
-- tools/slot_placeholders.py) leży w Background nad tłem, pod przyciskami:
--   Wojownik — para: slot broni (miecz) przesunięty w lewo + nowy slot tarczy Slot_OffHand obok, razem na środku;
--   Mag — slot broni z sylwetką kostura; Zwiadowca — z sylwetką procy. Bez klasy: tło jak dawniej.
-- Położenia w pikselach pełnego tła 2048 × 1166 (ramki z czarnym obrysem); przycisk leży 12/7 px w głąb ramki.
local BG_W, BG_H = 2048, 1166
local function px(x, y, w, h)
	return UDim2.fromScale(x / BG_W, y / BG_H), UDim2.fromScale(w / BG_W, h / BG_H)
end
local CLASS_SLOTS = {
	Warrior = { image = "rbxassetid://89240592397124", frame = { 397, 455, 282, 135 }, weaponX = 397, offHandX = 543 },
	Mage = { image = "rbxassetid://127743263185862", frame = { 470, 455, 136, 135 }, weaponX = 470 },
	Scout = { image = "rbxassetid://75330052223718", frame = { 470, 455, 136, 135 }, weaponX = 470 },
}
local SLOT_DX, SLOT_DY, SLOT_SIZE = 12, 7, 116
local weaponSlot = panel.Character.EquipSlots:WaitForChild("Slot_Weapon")
local offHandSlot = panel.Character.EquipSlots:FindFirstChild("Slot_OffHand")
if not offHandSlot then
	offHandSlot = weaponSlot:Clone() -- ta sama budowa (Cover, Icon), przedmioty ze slot = "OffHand" (tarcze)
	offHandSlot.Name = "Slot_OffHand"
	offHandSlot.Visible = false
	offHandSlot.Parent = weaponSlot.Parent
end
local classOverlay = Instance.new("ImageLabel")
classOverlay.Name = "ClassSlots"
classOverlay.BackgroundTransparency = 1
classOverlay.ZIndex = 2 -- nad kafelkami tła (Background, ZIndexBehavior Sibling)
classOverlay.Visible = false
classOverlay.Parent = panel:WaitForChild("Background")
local function applyClassSlots()
	local cfg = CLASS_SLOTS[player:GetAttribute("Class") or ""]
	local slotY = 455 + SLOT_DY
	if not cfg then
		classOverlay.Visible = false
		offHandSlot.Visible = false
		weaponSlot.Position = (px(470 + SLOT_DX, slotY, 0, 0))
		return
	end
	local f = cfg.frame
	classOverlay.Image = cfg.image
	classOverlay.Position, classOverlay.Size = px(f[1], f[2], f[3], f[4])
	classOverlay.Visible = true
	weaponSlot.Position = (px(cfg.weaponX + SLOT_DX, slotY, 0, 0))
	offHandSlot.Visible = cfg.offHandX ~= nil
	if cfg.offHandX then
		offHandSlot.Position, offHandSlot.Size = px(cfg.offHandX + SLOT_DX, slotY, SLOT_SIZE, SLOT_SIZE)
	end
end
applyClassSlots()
player:GetAttributeChangedSignal("Class"):Connect(applyClassSlots)

------------------------------------------------ pasek doświadczenia (Paweł 18.11: wypalony w tle był rozmazany i miał
-- łatę po usuniętym napisie) — natywny pasek na wnętrzu złotej ramki z tła, wypełnienie = XP / XPMax
local expBar = Instance.new("Frame")
expBar.Name = "ExpBar"
expBar.BorderSizePixel = 0
expBar.BackgroundColor3 = Color3.fromRGB(14, 10, 16)
expBar.ZIndex = 3 -- nad ramką rasy (2), pod napisem i ikonką klasy (LevelBadge 4) — Paweł 23.11
expBar.Position, expBar.Size = px(444, 378, 189, 50)
expBar.Parent = panel.Character -- ta sama warstwa co LevelBadge, żeby ikonka klasy była PRZED paskiem
local function corner(parent: Instance, r: number)
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(r, 0)
	c.Parent = parent
end
corner(expBar, 0.3)
local track = Instance.new("Frame")
track.Name = "Track"
track.BorderSizePixel = 0
track.BackgroundColor3 = Color3.fromRGB(36, 38, 60)
track.Position = UDim2.fromScale(0.016, 0.06)
track.Size = UDim2.fromScale(0.968, 0.88)
track.ZIndex = 2
track.ClipsDescendants = true
track.Parent = expBar
corner(track, 0.3)
local fill = Instance.new("Frame")
fill.Name = "Fill"
fill.BorderSizePixel = 0
fill.BackgroundColor3 = Color3.new(1, 1, 1)
fill.Size = UDim2.fromScale(0, 1)
fill.ZIndex = 2
fill.Parent = track
corner(fill, 0.3)
local grad = Instance.new("UIGradient")
grad.Rotation = 90
grad.Color = ColorSequence.new({
	ColorSequenceKeypoint.new(0, Color3.fromRGB(150, 236, 120)),
	ColorSequenceKeypoint.new(0.35, Color3.fromRGB(70, 196, 74)),
	ColorSequenceKeypoint.new(1, Color3.fromRGB(34, 140, 52)),
})
grad.Parent = fill
local shine = Instance.new("Frame") -- połysk w górnej części wypełnienia (styl Glossy Ink)
shine.Name = "Shine"
shine.BorderSizePixel = 0
shine.BackgroundColor3 = Color3.new(1, 1, 1)
shine.BackgroundTransparency = 0.55
shine.Position = UDim2.fromScale(0.04, 0.12)
shine.Size = UDim2.fromScale(0.92, 0.2)
shine.ZIndex = 2
shine.Parent = fill
corner(shine, 0.5)
local function refreshExp(animate: boolean)
	local xp = player:GetAttribute("XP") or 0
	local maxXp = math.max(player:GetAttribute("XPMax") or 100, 1)
	local goal = UDim2.fromScale(math.clamp(xp / maxXp, 0, 1), 1)
	if animate then
		TS:Create(fill, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = goal }):Play()
	else
		fill.Size = goal
	end
end
refreshExp(false)
player:GetAttributeChangedSignal("XP"):Connect(function()
	refreshExp(true)
end)
player:GetAttributeChangedSignal("XPMax"):Connect(function()
	refreshExp(true)
end)

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

------------------------------------------------ przyciski „wypalone” w tle (zakładki, X): bez skalowania i przesuwania
-- Przycisk leży co do piksela na swojej kopii w grafice tła — każde powiększenie, zmniejszenie albo przyciemnienie samego
-- obrazka odsłaniało kopię pod spodem (uwaga Pawła 16–17.11). Reakcja na mysz: nakładka-cień w kształcie przycisku
-- (ten sam obrazek na czarno; dla pola bez obrazka — zaokrąglony prostokąt) i podskok napisu.
-- przezroczystość cienia (1 = brak cienia): spoczynek lekko przygaszony, najechanie = rozjaśnienie (Paweł 18.11: napis
-- się nie animuje — przy skalowaniu wyjeżdżał za przycisk — tylko przycisk się podświetla)
-- Paweł 18.11: bez ciemnej nakładki na przyciskach — aktywny czysty, nieaktywna zakładka tylko lekko przygaszona
local SHADE_ON, SHADE_OFF, SHADE_HOVER_OFF, SHADE_PRESS = 1, 0.8, 0.92, 0.85
local function flatButton(btn: ImageButton, onClick: () -> ()): (boolean) -> ()
	local sc = btn:FindFirstChildWhichIsA("UIScale")
	if sc then
		sc.Scale = 1
	end
	local shade: GuiObject
	if btn.Image ~= "" and btn.ImageTransparency < 1 then
		local img = Instance.new("ImageLabel")
		img.Image = btn.Image
		img.ScaleType = btn.ScaleType
		img.ImageColor3 = Color3.new(0, 0, 0)
		img.ImageTransparency = 1
		img.BackgroundTransparency = 1
		shade = img
	else
		local f = Instance.new("Frame")
		f.BackgroundColor3 = Color3.new(0, 0, 0)
		f.BackgroundTransparency = 1
		f.BorderSizePixel = 0
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.22, 0)
		c.Parent = f
		shade = f
	end
	shade.Name = "Shade"
	shade.Size = UDim2.fromScale(1, 1)
	shade.ZIndex = 1
	shade.Parent = btn
	local label = btn:FindFirstChild("Label")
	local lsc: UIScale? = nil
	if label and label:IsA("GuiObject") then
		label.ZIndex = math.max(label.ZIndex, 2)
		lsc = label:FindFirstChildOfClass("UIScale")
		if not lsc then
			lsc = Instance.new("UIScale")
			lsc.Parent = label
		end
	end
	local base, hovering, pressed = SHADE_ON, false, false
	local function apply()
		local t = base
		if hovering then
			t = (base == SHADE_ON) and 1 or SHADE_HOVER_OFF -- aktywny: pełna jasność; nieaktywny: mniej cienia
		end
		if pressed then
			t = math.min(t, SHADE_PRESS)
		end
		local prop = shade:IsA("ImageLabel") and "ImageTransparency" or "BackgroundTransparency"
		TS:Create(shade, QUICK, { [prop] = t }):Play()
		if lsc then
			lsc.Scale = 1 -- napis bez animacji
		end
	end
	btn.MouseEnter:Connect(function()
		hovering = true
		apply()
	end)
	btn.MouseLeave:Connect(function()
		hovering, pressed = false, false
		apply()
	end)
	btn.MouseButton1Down:Connect(function()
		pressed = true
		apply()
	end)
	btn.MouseButton1Up:Connect(function()
		pressed = false
		apply()
	end)
	btn.Activated:Connect(function()
		pressed = false
		apply()
		onClick()
	end)
	apply() -- stan spoczynku od razu (lekko przygaszony), żeby najechanie było widać jako podświetlenie
	return function(active: boolean)
		base = active and SHADE_ON or SHADE_OFF
		apply()
	end
end

------------------------------------------------ zakładki: prawdziwa animacja (Paweł 23.11)
-- Zakładki są wymazane z tła (tools/eq_wymaz_zakladki.py), więc przycisk może się ruszać. Kotwica na dole (0.5, 1):
-- powiększenie rośnie w górę i na boki, nigdy w dół na ramkę statystyk / plecaka pod zakładką.
-- nigdy poniżej 1: pod przyciskiem w tle jest tylko obrys zakładki (środek wymazany), zmniejszenie by go odsłoniło
local TAB_ON, TAB_OFF, TAB_HOVER, TAB_PRESS = 1.05, 1, 0.03, 0.03
local TAB_IN = TweenInfo.new(0.22, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local TAB_DOWN = TweenInfo.new(0.07, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local function tabButton(btn: ImageButton, onClick: () -> ()): (boolean) -> ()
	local sc = btn:FindFirstChildWhichIsA("UIScale") or Instance.new("UIScale")
	sc.Parent = btn
	local shade = Instance.new("ImageLabel") -- przygaszenie nieaktywnej: ten sam kształt na czarno
	shade.Name = "Shade"
	shade.Image = btn.Image
	shade.ScaleType = btn.ScaleType
	shade.ImageColor3 = Color3.new(0, 0, 0)
	shade.ImageTransparency = 1
	shade.BackgroundTransparency = 1
	shade.Size = UDim2.fromScale(1, 1)
	shade.ZIndex = 1
	shade.Parent = btn
	local label = btn:FindFirstChild("Label")
	if label and label:IsA("GuiObject") then
		label.ZIndex = math.max(label.ZIndex, 2)
	end
	local active, hovering, pressed = false, false, false
	local function apply(info: TweenInfo?)
		local s = active and TAB_ON or TAB_OFF
		if hovering then
			s += TAB_HOVER
		end
		if pressed then
			s = math.max(s - TAB_PRESS, 1)
		end
		TS:Create(sc, info or TAB_IN, { Scale = s }):Play()
		local cien = active and 1 or (hovering and 0.88 or 0.72)
		TS:Create(shade, QUICK, { ImageTransparency = cien }):Play()
	end
	btn.MouseEnter:Connect(function()
		hovering = true
		apply()
	end)
	btn.MouseLeave:Connect(function()
		hovering, pressed = false, false
		apply()
	end)
	btn.MouseButton1Down:Connect(function()
		pressed = true
		apply(TAB_DOWN)
	end)
	btn.MouseButton1Up:Connect(function()
		pressed = false
		apply()
	end)
	btn.Activated:Connect(function()
		pressed = false
		onClick()
		-- sprężyste „kliknięcie”: na chwilę większa, potem na swoje miejsce
		sc.Scale = TAB_ON + 0.06
		apply()
	end)
	apply()
	return function(on: boolean)
		active = on
		btn.ZIndex = on and 3 or 2 -- aktywna nad sąsiadkami (przy powiększeniu lekko na nie zachodzi)
		apply()
	end
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
	local setters = {}
	local function activate(active)
		for _, t in ipairs(tabs) do
			local on = t == active
			-- nieaktywna zakładka: cień-nakładka (nie ImageColor3 — przez miękki brzeg prześwitywała jasna kopia z tła)
			if setters[t] then
				setters[t](on)
			end
			t.ZIndex = on and 2 or 1
			local label = t:FindFirstChild("Label")
			if label then
				label.TextTransparency = on and 0 or 0.25
			end
		end
	end
	for _, t in ipairs(tabs) do
		setters[t] = tabButton(t, function()
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
		-- Paweł 23.11: statystyki rosną tylko z treningu i przedmiotów — przyciski „+” (TEST: +1 bez kosztu) usunięte
		local plus = card:FindFirstChild("PlusButton")
		if plus and plus:IsA("GuiObject") then
			plus.Visible = false
			plus.Active = false
		end
	end
end

------------------------------------------------ przedmioty i przeciąganie (TEST: stan tylko po stronie klienta)
local GuiService = game:GetService("GuiService")
-- stan ekwipunku jest wspólny z oknem sklepu (ShopClient): moduł EkwipunekStan obok tego skryptu
local Stan = require(script.Parent:WaitForChild("EkwipunekStan"))
local DRAG_START = 6 -- px ruchu, po których kliknięcie staje się przeciąganiem
local BAG_TABS = { TabWeapons = "Weapons", TabArmor = "Armor", TabAmulets = "Amulets", TabOthers = "Others" }

local equipFolder, bagFolder = panel.Character.EquipSlots, panel.BackpackGrid
local equip = Stan.equip -- nazwa slotu ("Slot_Trinket") -> id przedmiotu
local bag = Stan.bag -- kategoria -> [numer slotu 1–25] -> id
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
	Stan.rysujIkone(slot.Icon, id)
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
	local d = Stan.definicja(id)
	return id == nil or (d ~= nil and (d.slot == "Any" or "Slot_" .. d.slot == slot.Name))
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
local storeInBag = Stan.doPlecaka

local function hintTab(category)
	local tab = panel.BackpackTabs:FindFirstChild("Tab" .. category)
	if tab then
		pop(tab, 1.2)
	end
end

local function move(from, target)
	local moving, there = get(from), get(target)
	if isBag(target) then
		local cat = Stan.definicja(moving).category
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
		local d = Stan.definicja(get(drag.from))
		g.Image = d and d.icon or ""
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
		Stan.zmieniono() -- przerysowuje to okno (renderAll) i lewą stronę sklepu
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

-- broń startowa klasy (Paweł 18.11): po wyborze klasy trafia do slotu broni (ClassData.Classes[].weapon).
-- Stan tylko po stronie klienta, jak reszta ekwipunku (TEST) — wkładamy ją raz, później gracz może ją przełożyć.
local starterGiven = false
local function giveStarterWeapon()
	if starterGiven then
		return
	end
	local ok, ClassData = pcall(function()
		return require(RS:WaitForChild("Shared"):WaitForChild("ClassData"))
	end)
	local c = ok and ClassData.byId(player:GetAttribute("Class") or "")
	if not (c and c.weapon and Stan.definicja(c.weapon)) then
		return
	end
	starterGiven = true
	if equip.Slot_Weapon == nil then
		equip.Slot_Weapon = c.weapon
	else
		storeInBag(c.weapon)
	end
	Stan.zmieniono()
end
Stan.Zmiana.Event:Connect(renderAll)
player:GetAttributeChangedSignal("Class"):Connect(giveStarterWeapon)
giveStarterWeapon()
renderAll()

local levelLbl = panel.Character.LevelBadge.LevelText
local function refreshLevel()
	levelLbl.Text = "LV " .. tostring(player:GetAttribute("Level") or 1)
end
player:GetAttributeChangedSignal("Level"):Connect(refreshLevel)

------------------------------------------------ znaczek klasy przy poziomie (emblemat z ekranu wyboru klasy)
local function refreshClassBadge(badge: ImageLabel)
	local ok, ClassData = pcall(function()
		return require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("ClassData"))
	end)
	local ok2, Icons = pcall(function()
		return require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("ClassSelectIcons"))
	end)
	local c = ok and ok2 and ClassData.byId(player:GetAttribute("Class") or "")
	badge.Image = c and Icons[c.emblem] or ""
	badge.Visible = c ~= nil
end
do
	local badge = panel.Character.LevelBadge:FindFirstChild("ClassBadge")
	if badge then
		refreshClassBadge(badge)
		player:GetAttributeChangedSignal("Class"):Connect(function()
			refreshClassBadge(badge)
		end)
	end
end
refreshLevel()

------------------------------------------------ portret rasy w ramce (Paweł 23.11)
pcall(function()
	-- ramka z portretem rasy w miejscu starej ramki (wymazanej z EqBg1); poziom i przycisk drzewka na wierzchu
	local ch = panel.Character
	-- ramka rasy w miejscu starej ramki; pasek, napis „LV” i ikonka klasy na jej torze (Paweł 23.11)
	local badge = ch:WaitForChild("LevelBadge")
	local napis = badge:WaitForChild("LevelText") :: TextLabel
	-- ikonka klasy może być większa niż pasek (ScaleWithParentSize ograniczało ją do wysokości LevelBadge)
	local ikonka = badge:WaitForChild("ClassBadge") :: GuiObject
	-- pasek bez własnego ciemnego tła; końce lekko zaokrąglone (Paweł 23.11: „bardziej prosty, żeby na fulla dopełniał”)
	expBar.BackgroundTransparency = 1
	for _, d in ipairs(expBar:GetDescendants()) do
		if d:IsA("UICorner") then
			d.CornerRadius = UDim.new(0.25, 0)
		elseif d.Name == "Track" and d:IsA("Frame") then
			d.BackgroundTransparency = 1
			d.Position, d.Size = UDim2.fromScale(0, 0), UDim2.fromScale(1, 1)
		end
	end
	local proporcje = ikonka:FindFirstChildOfClass("UIAspectRatioConstraint")
	if proporcje then
		proporcje.AspectType = Enum.AspectType.FitWithinMaxSize
	end
	local granica = napis:FindFirstChildOfClass("UITextSizeConstraint")
	if granica then
		granica.MaxTextSize = 60
	end
	local RAMKA_EQ = { 405 / BG_W, 145 / BG_H, 265 / BG_W, 292 / BG_H } -- ramka rasy na tle: px 405–670 × 145–437
	require(RS:WaitForChild("Shared"):WaitForChild("RacePortraitUI")).attach({
		rodzic = ch,
		prostokat = { 0.1981, 0.1246, 0.1296, 0.2508 }, -- stara ramka w EqBg1: px 405–670 × 145–437 z 2045 × 1164
		zindex = 2,
		nad = { badge, ch:WaitForChild("SkillTreeButton") },
		-- zielony pasek i kontener napisu w torze ramki WYBRANEJ rasy — wymiary z Figmy (Shared.RacePortraits.Tor;
		-- prostokąty ExpBar w ramkach RaceFrame<Id>, 4 px od złota obrazka ≈ 1 px w grze; Paweł 23.11)
		pasek = {
			{ obj = expBar, ramka = RAMKA_EQ },
			{ obj = badge, ramka = RAMKA_EQ },
		},
		uklad = {
			-- napis „LV” obniżony o kilka pikseli (Paweł 23.11), dalej w całości w pasku
			{ obj = napis, rect = { 0.03, 0.2, 0.94, 0.75 } },
			-- ikonka klasy: większa, na lewym końcu paska, przed nim (Paweł 23.11)
			{ obj = ikonka, rect = { 0.02, 0.5, 1.3 * 39 / 181, 1.3 } }, -- kwadrat 1,3 × wysokość toru
		},
	})
	badge.ZIndex = 4 -- napis „LV” i ikonka klasy (dziecko LevelBadge) przed paskiem (ExpBar 3)
end)

------------------------------------------------ otwieranie / zamykanie
local isOpen, busy = false, false

local function open()
	if isOpen or busy then
		return
	end
	isOpen = true
	gui.Enabled = true
	rescale()
	-- Paweł 24.11: okno od razu, bez wjazdu (wcześniej skalowanie 0,85 -> 1 przez 0,28 s i migało)
	backdrop.BackgroundTransparency = 0.45
	panelScale.Scale = 1
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

flatButton(panel.CloseButton, close) -- X leży na swojej kopii w tle: bez skalowania
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
