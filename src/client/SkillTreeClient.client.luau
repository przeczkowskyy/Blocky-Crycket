--[[
	SkillTreeClient — okno drzewka umiejętności (ScreenGui „SkillTree”, src/gui/SkillTree.model.json).
	Projekt: B&C/UI/Okno drzewka umiejętności.md (propozycja); dane: ReplicatedStorage.Shared.SkillTreeData.

	- Otwiera się przyciskiem drzewa w oknie ekwipunku (EquipmentPanel…Character.SkillTreeButton),
	  zawsze na zakładce PLAYER. Wykrzyknik „Alert” na przycisku = gracza stać na jakiś węzeł.
	- Mapa węzłów: przeciąganie myszką/palcem, kółko myszy = zoom. Stany węzła: kupiony (poziom),
	  dostępny (cena w Diamentach), zakryty „?” (sąsiad dostępnego), reszta niewidoczna.
	- Animacje: okno wyskakuje, węzły pojawiają się od środka na zewnątrz, zakup = puls + nowe węzły wyskakują,
	  wykrzyknik w ekwipunku się kołysze.
	- Ulepszenie (Paweł 17.11): bez przycisku UNLOCK — gracz PRZYTRZYMUJE kółko; Diamenty lecą do kółka, a ono
	  napełnia się jak cieczą. Puszczenie przed końcem cofa ciecz. Kliknięcie pokazuje opis na dole.
	- Jedno tło dla wszystkich zakładek (gwiazdozbiory rycerza i kota-maga).
	- Zakup: RemoteEvent ReplicatedStorage.SkillTreeBuy (serwer sprawdza wszystko, src/server/SkillTree.server.luau).
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local TS = game:GetService("TweenService")
local RunService = game:GetService("RunService")
local HttpService = game:GetService("HttpService")

local Data = require(RS:WaitForChild("Shared"):WaitForChild("SkillTreeData"))
local Icons = require(RS:WaitForChild("Shared"):WaitForChild("SkillTreeIcons"))
local buyEvent = RS:WaitForChild("SkillTreeBuy")

local player = Players.LocalPlayer
local pg = player:WaitForChild("PlayerGui")
local gui = pg:WaitForChild("SkillTree")
local panel = gui:WaitForChild("Panel")
local backdrop = gui:WaitForChild("Backdrop")
local content = panel:WaitForChild("Content")
local map = content:WaitForChild("Map")
local mapScale = map:WaitForChild("UIScale")
local bar = content:WaitForChild("DetailBar")
local holdHint = bar:WaitForChild("HoldHint")
local hint = content:WaitForChild("Hint")
local bgImage = content:WaitForChild("Bg")

local DESIGN_W = 836 -- szerokość obszaru treści w makiecie (px); węzły i linie są w tych jednostkach
local U, S = 104, 72 -- odstęp siatki i średnica węzła (px makiety)
local ZOOM_MIN, ZOOM_MAX = 0.6, 1.5
local HOLD_TIME = 0.85 -- s przytrzymania do ulepszenia
local LIQUID = Color3.fromRGB(70, 205, 255)

local QUICK = TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
local POP = TweenInfo.new(0.32, Enum.EasingStyle.Back, Enum.EasingDirection.Out)
local GOLD = Color3.fromRGB(255, 210, 63)
local GEM_BLUE = Color3.fromRGB(138, 240, 255)
local NO_MONEY = Color3.fromRGB(255, 120, 110)
local INK = Color3.fromRGB(26, 20, 16)
local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")

local cancelHold: (string?) -> ()
local startHold: (string, Frame, UIScale, string) -> ()
local currentTab = "Player"
local selected: string? = nil
local zoom = 1
local levels: { [string]: number } = {}
local shown: { [string]: boolean } = {} -- węzły widoczne przy poprzednim rysowaniu (do animacji nowych)

------------------------------------------------------------ stan gracza
local function readLevels()
	local ok, t = pcall(HttpService.JSONDecode, HttpService, player:GetAttribute("SkillTree") or "{}")
	levels = (ok and type(t) == "table") and t or {}
end

local function gems(): number
	local g = player:GetAttribute("Gems")
	return typeof(g) == "number" and g or 0
end

local function lvl(id: string): number
	return levels[id] or 0
end

-- "own" kupiony · "open" dostępny · "hid" zakryty „?” · nil niewidoczny
local function stateOf(node): string?
	if lvl(node.id) >= 1 then
		return "own"
	end
	if Data.isAvailable(node, levels) then
		return "open"
	end
	local parent = node.parent and Data.Nodes[node.parent]
	if parent and lvl(parent.id) == 0 and Data.isAvailable(parent, levels) then
		return "hid"
	end
	return nil
end

local function canBuy(node): (boolean, number)
	local l = lvl(node.id)
	if l >= node.max or not Data.isAvailable(node, levels) then
		return false, 0
	end
	local cost = Data.cost(node, l + 1)
	return gems() >= cost, cost
end

------------------------------------------------------------ pomocnicze UI
local function text(parent: Instance, s: string, pos: UDim2, size: UDim2, color: Color3, px: number, z: number, anchor: Vector2?)
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.AnchorPoint = anchor or Vector2.new(0.5, 0)
	t.Position = pos
	t.Size = size
	t.FontFace = FONT
	t.Text = s
	t.TextColor3 = color
	t.TextSize = px
	t.TextXAlignment = Enum.TextXAlignment.Center
	t.TextYAlignment = Enum.TextYAlignment.Center
	t.ZIndex = z
	local st = Instance.new("UIStroke")
	st.Color = INK
	st.Thickness = 2
	st.LineJoinMode = Enum.LineJoinMode.Round
	st.Parent = t
	t.Parent = parent
	return t
end

local function line(x1, y1, x2, y2, owned: boolean, animate: boolean)
	local dx, dy = x2 - x1, y2 - y1
	local len = math.sqrt(dx * dx + dy * dy)
	local rot = math.deg(math.atan2(dy, dx))
	for i, spec in ipairs({ { 10, INK }, { 5, owned and GOLD or Color3.fromRGB(138, 122, 102) } }) do
		local f = Instance.new("Frame")
		f.Name = "Link"
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.Position = UDim2.fromOffset((x1 + x2) / 2, (y1 + y2) / 2)
		f.Size = UDim2.fromOffset(animate and 0 or len, spec[1])
		f.Rotation = rot
		f.BackgroundColor3 = spec[2]
		f.BorderSizePixel = 0
		f.ZIndex = i
		local c = Instance.new("UICorner")
		c.CornerRadius = UDim.new(0.5, 0)
		c.Parent = f
		f.Parent = map
		if animate then
			TS:Create(f, TweenInfo.new(0.25, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = UDim2.fromOffset(len, spec[1]) }):Play()
		end
	end
end

------------------------------------------------------------ przeciąganie i zoom
local dragging, dragMoved, dragStart, mapStart = false, false, Vector2.zero, Vector2.zero
local lastDragEnd = 0
local bounds = { minX = 0, maxX = 0, minY = 0, maxY = 0 }

local function scaleNow(): number
	return content.AbsoluteSize.X / DESIGN_W * zoom
end

local function clampMap()
	local sc = scaleNow()
	local view = content.AbsoluteSize
	local m = 70 * sc
	local p = map.Position
	local x = math.clamp(p.X.Offset, m - bounds.maxX * sc, view.X - m - bounds.minX * sc)
	local y = math.clamp(p.Y.Offset, m - bounds.maxY * sc, view.Y - m - bounds.minY * sc)
	map.Position = UDim2.fromOffset(x, y)
end

local function centerMap()
	local view = content.AbsoluteSize
	map.Position = UDim2.fromOffset(view.X / 2, view.Y * 0.45)
end

local function applyScale()
	mapScale.Scale = scaleNow()
end

local function inside(obj: GuiObject, pos: Vector2): boolean
	local a, s = obj.AbsolutePosition, obj.AbsoluteSize
	return pos.X >= a.X and pos.X <= a.X + s.X and pos.Y >= a.Y and pos.Y <= a.Y + s.Y
end

local function screenPos(input: InputObject): Vector2
	return Vector2.new(input.Position.X, input.Position.Y)
end

local function hideHint()
	if hint.Visible and hint.TextTransparency == 0 then
		TS:Create(hint, TweenInfo.new(0.3), { TextTransparency = 1 }):Play()
		local st = hint:FindFirstChildWhichIsA("UIStroke")
		if st then
			TS:Create(st, TweenInfo.new(0.3), { Transparency = 1 }):Play()
		end
	end
end

UIS.InputBegan:Connect(function(input)
	if not gui.Enabled then
		return
	end
	local t = input.UserInputType
	local p = screenPos(input)
	if (t == Enum.UserInputType.MouseButton1 or t == Enum.UserInputType.Touch) and inside(content, p) then
		if bar.Visible and inside(bar, p) then
			return -- pasek szczegółów nie rusza mapy
		end
		dragging, dragMoved = true, false
		dragStart = p
		mapStart = Vector2.new(map.Position.X.Offset, map.Position.Y.Offset)
	end
end)

UIS.InputChanged:Connect(function(input)
	if not gui.Enabled then
		return
	end
	local t = input.UserInputType
	if dragging and (t == Enum.UserInputType.MouseMovement or t == Enum.UserInputType.Touch) then
		local d = screenPos(input) - dragStart
		if d.Magnitude > 6 then
			dragMoved = true
			hideHint()
			cancelHold(nil)
		end
		if dragMoved then
			map.Position = UDim2.fromOffset(mapStart.X + d.X, mapStart.Y + d.Y)
			clampMap()
		end
	elseif t == Enum.UserInputType.MouseWheel and inside(content, screenPos(input)) then
		local old = scaleNow()
		zoom = math.clamp(zoom + (input.Position.Z > 0 and 0.1 or -0.1), ZOOM_MIN, ZOOM_MAX)
		local new = scaleNow()
		local cursor = screenPos(input) - content.AbsolutePosition -- zoom wokół kursora
		local p = Vector2.new(map.Position.X.Offset, map.Position.Y.Offset)
		local q = cursor + (p - cursor) * (new / old)
		map.Position = UDim2.fromOffset(q.X, q.Y)
		applyScale()
		clampMap()
	end
end)

UIS.InputEnded:Connect(function(input)
	local t = input.UserInputType
	if t == Enum.UserInputType.MouseButton1 or t == Enum.UserInputType.Touch then
		cancelHold(nil) -- puszczenie poza kółkiem też przerywa napełnianie
	end
	if dragging and (t == Enum.UserInputType.MouseButton1 or t == Enum.UserInputType.Touch) then
		dragging = false
		if dragMoved then
			lastDragEnd = os.clock()
		end
	end
end)

content:GetPropertyChangedSignal("AbsoluteSize"):Connect(function()
	applyScale()
	clampMap()
end)

------------------------------------------------------------ pasek szczegółów
local barShownFor: string? = nil
local function showDetail()
	local node = selected and Data.Nodes[selected]
	if not node then
		bar.Visible = false
		barShownFor = nil
		return
	end
	if barShownFor ~= selected then -- wjazd paska od dołu przy nowym wyborze
		barShownFor = selected
		local target = bar.Position
		bar.Position = target + UDim2.fromScale(0, 0.06)
		TS:Create(bar, TweenInfo.new(0.18, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Position = target }):Play()
	end
	bar.Visible = true
	local l = lvl(node.id)
	bar.NodeName.Text = node.name .. (node.max > 1 and string.format("  %d/%d", l, node.max) or "")
	bar.NodeDesc.Text = Data.describe(node, l)
	local ok = canBuy(node)
	local maxed = l >= node.max
	holdHint.Text = maxed and "MAX LEVEL" or (ok and "HOLD TO UPGRADE" or "NOT ENOUGH GEMS")
	holdHint.TextColor3 = maxed and GOLD or (ok and GEM_BLUE or NO_MONEY)
end

------------------------------------------------------------ ulepszenie przytrzymaniem: Diamenty lecą, kółko napełnia się cieczą
local pendingPulse: string? = nil
local holdDoneFor: string? = nil
type Hold = { id: string, g: Frame, sc: UIScale, group: CanvasGroup, water: Frame, t0: number, nextGem: number, conn: RBXScriptConnection }
local hold: Hold? = nil

local function shake(g: GuiObject)
	TS:Create(g, TweenInfo.new(0.05, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, 3, true), { Rotation = 8 }):Play()
end

local function flyGem(g: Frame)
	local a = math.random() * math.pi * 2
	local r = 110 + math.random() * 60
	local center = g.Position
	local gem = Instance.new("ImageLabel")
	gem.BackgroundTransparency = 1
	gem.Image = Icons.Gem
	gem.ScaleType = Enum.ScaleType.Fit
	gem.AnchorPoint = Vector2.new(0.5, 0.5)
	gem.Size = UDim2.fromOffset(20, 18)
	gem.Position = center + UDim2.fromOffset(math.cos(a) * r, math.sin(a) * r)
	gem.Rotation = math.random(-30, 30)
	gem.ZIndex = 9
	gem.Parent = map
	local tw = TS:Create(gem, TweenInfo.new(0.32, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
		{ Position = center, Size = UDim2.fromOffset(8, 7), Rotation = gem.Rotation + 120 })
	tw.Completed:Connect(function()
		gem:Destroy()
	end)
	tw:Play()
end

cancelHold = function(id: string?)
	local h = hold
	if not h or (id and h.id ~= id) then
		return
	end
	hold = nil
	h.conn:Disconnect()
	TS:Create(h.sc, QUICK, { Scale = 1 }):Play()
	local tw = TS:Create(h.water, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), { Size = UDim2.fromScale(1, 0) })
	tw.Completed:Connect(function()
		h.group:Destroy()
	end)
	tw:Play()
end

local function completeHold()
	local h = hold
	if not h then
		return
	end
	hold = nil
	h.conn:Disconnect()
	holdDoneFor = h.id
	selected = h.id
	pendingPulse = h.id
	h.water.Size = UDim2.fromScale(1, 1)
	h.sc.Scale = 1.3
	TS:Create(h.sc, POP, { Scale = 1 }):Play()
	for _ = 1, 6 do
		flyGem(h.g)
	end
	buyEvent:FireServer(h.id)
end

startHold = function(id: string, g: Frame, sc: UIScale, st: string)
	cancelHold(nil)
	local node = Data.Nodes[id]
	if st == "hid" or not node or lvl(id) >= node.max then
		return
	end
	local ok = canBuy(node)
	if not ok then
		shake(g)
		return
	end
	-- ciecz: okrągła warstwa (CanvasGroup z UICorner przycina do koła) nad ikoną, poziom rośnie od dołu
	local group = Instance.new("CanvasGroup")
	group.Name = "Liquid"
	group.AnchorPoint = Vector2.new(0.5, 0.5)
	group.Position = UDim2.fromScale(0.5, 0.5)
	group.Size = UDim2.fromScale(0.82, 0.82)
	group.BackgroundTransparency = 1
	group.GroupTransparency = 0.25
	group.ZIndex = 6
	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0.5, 0)
	corner.Parent = group
	local water = Instance.new("Frame")
	water.Name = "Water"
	water.AnchorPoint = Vector2.new(0.5, 1)
	water.Position = UDim2.fromScale(0.5, 1)
	water.Size = UDim2.fromScale(1, 0)
	water.BackgroundColor3 = LIQUID
	water.BorderSizePixel = 0
	water.ZIndex = 6
	water.Parent = group
	local grad = Instance.new("UIGradient")
	grad.Rotation = 90
	grad.Color = ColorSequence.new(Color3.fromRGB(170, 245, 255), Color3.fromRGB(40, 140, 230))
	grad.Parent = water
	local surface = Instance.new("Frame") -- jasna, falująca powierzchnia cieczy
	surface.Name = "Surface"
	surface.AnchorPoint = Vector2.new(0.5, 0.5)
	surface.Position = UDim2.fromScale(0.5, 0)
	surface.Size = UDim2.new(1.6, 0, 0, 6)
	surface.BackgroundColor3 = Color3.fromRGB(220, 252, 255)
	surface.BorderSizePixel = 0
	surface.ZIndex = 7
	surface.Parent = water
	group.Parent = g
	local h: Hold
	h = {
		id = id, g = g, sc = sc, group = group, water = water, t0 = os.clock(), nextGem = 0,
		conn = RunService.RenderStepped:Connect(function()
			local now = os.clock()
			local p = math.clamp((now - h.t0) / HOLD_TIME, 0, 1)
			water.Size = UDim2.fromScale(1, 0.08 + p * 0.92)
			surface.Rotation = math.sin(now * 12) * 7
			sc.Scale = 1.1 + p * 0.08 + math.sin(now * 40) * 0.012 * p
			if now >= h.nextGem then
				h.nextGem = now + 0.07
				flyGem(g)
			end
			if p >= 1 then
				completeHold()
			end
		end),
	}
	hold = h
end

------------------------------------------------------------ rysowanie mapy
local ringTween: Tween? = nil

-- animate: "all" = wszystkie węzły wyskakują od środka (otwarcie, zmiana zakładki),
--          "new" = tylko węzły, których wcześniej nie było (po zakupie); nil = bez animacji
local function render(animate: string?, pulseId: string?)
	cancelHold(nil)
	if ringTween then
		ringTween:Cancel()
		ringTween = nil
	end
	for _, c in ipairs(map:GetChildren()) do
		if not c:IsA("UIScale") then
			c:Destroy()
		end
	end
	local order = Data.Order[currentTab]
	local states = {}
	bounds = { minX = 0, maxX = 0, minY = 0, maxY = 0 }
	for _, id in ipairs(order) do
		local node = Data.Nodes[id]
		local st = stateOf(node)
		states[id] = st
		if st then
			local x, y = node.x * U, node.y * U
			bounds.minX, bounds.maxX = math.min(bounds.minX, x), math.max(bounds.maxX, x)
			bounds.minY, bounds.maxY = math.min(bounds.minY, y), math.max(bounds.maxY, y)
		end
	end
	local isNew = function(id)
		return animate == "all" or (animate == "new" and not shown[id])
	end

	-- linie pod węzłami
	for _, id in ipairs(order) do
		local node = Data.Nodes[id]
		if states[id] and node.parent and states[node.parent] then
			local p = Data.Nodes[node.parent]
			line(p.x * U, p.y * U, node.x * U, node.y * U, states[id] == "own", isNew(id))
		end
	end

	-- nazwy gałęzi (gdy węzeł startowy kupiony)
	local root = Data.Nodes[order[1]]
	if lvl(root.id) >= 1 then
		for _, br in ipairs(Data.Branches[currentTab]) do
			local t = text(map, br.title, UDim2.fromOffset(br.x * U, br.y * U), UDim2.fromOffset(170, 20), GOLD, 14, 7,
				Vector2.new(0.5, 0.5))
			t.Name = "Branch"
			if animate == "all" or (animate == "new" and not shown["branch:" .. br.id]) then
				t.TextTransparency = 1
				TS:Create(t, TweenInfo.new(0.4), { TextTransparency = 0 }):Play()
			end
		end
	end

	-- węzły: grupa (ikona + nazwa + poziom + cena) skalowana razem
	local nowShown = {}
	for _, id in ipairs(order) do
		local node = Data.Nodes[id]
		local st = states[id]
		if st then
			nowShown[id] = true
			local x, y = node.x * U, node.y * U
			local size = node.depth == 0 and S * 1.3 or (st == "hid" and S * 0.8 or S)
			local g = Instance.new("Frame")
			g.Name = id
			g.AnchorPoint = Vector2.new(0.5, 0.5)
			g.Position = UDim2.fromOffset(x, y)
			g.Size = UDim2.fromOffset(size, size)
			g.BackgroundTransparency = 1
			g.ZIndex = 4
			local sc = Instance.new("UIScale")
			sc.Parent = g

			local b = Instance.new("ImageButton")
			b.Name = "Button"
			b.Size = UDim2.fromScale(1, 1)
			b.BackgroundTransparency = 1
			b.AutoButtonColor = false
			b.Image = st == "hid" and Icons.NodeHidden or (Icons[node.icon] or "")
			b.ZIndex = 5
			b.Parent = g


			if st ~= "hid" then
				-- nazwa: wyśrodkowana pod ikoną
				text(g, node.name, UDim2.new(0.5, 0, 1, 2), UDim2.fromOffset(170, 15), Color3.new(1, 1, 1), 12, 7)
				local l = lvl(id)
				if st == "own" and node.max > 1 then
					text(g, l >= node.max and "MAX" or (l .. "/" .. node.max), UDim2.new(1, 2, 0, -2), UDim2.fromOffset(40, 14),
						GOLD, 11, 7, Vector2.new(0.5, 0))
				end
				if l < node.max then
					local ok, cost = canBuy(node)
					if st == "open" or ok then
						-- cena: ikona Diamentu + liczba, razem wyśrodkowane pod nazwą
						local row = Instance.new("Frame")
						row.BackgroundTransparency = 1
						row.AnchorPoint = Vector2.new(0.5, 0)
						row.Position = UDim2.new(0.5, 0, 1, 17)
						row.Size = UDim2.fromOffset(60, 15)
						row.ZIndex = 7
						local list = Instance.new("UIListLayout")
						list.FillDirection = Enum.FillDirection.Horizontal
						list.HorizontalAlignment = Enum.HorizontalAlignment.Center
						list.VerticalAlignment = Enum.VerticalAlignment.Center
						list.Padding = UDim.new(0, 3)
						list.Parent = row
						local gem = Instance.new("ImageLabel")
						gem.BackgroundTransparency = 1
						gem.Image = Icons.Gem
						gem.ScaleType = Enum.ScaleType.Fit
						gem.Size = UDim2.fromOffset(16, 14)
						gem.ZIndex = 7
						gem.LayoutOrder = 1
						gem.Parent = row
						local c = text(row, tostring(cost), UDim2.new(), UDim2.fromOffset(0, 15), ok and GEM_BLUE or NO_MONEY, 12, 7)
						c.AutomaticSize = Enum.AutomaticSize.X
						c.LayoutOrder = 2
						row.Parent = g
					end
				end
			end

			-- hover / przytrzymanie (ulepszenie) / klik (opis)
			b.MouseEnter:Connect(function()
				TS:Create(sc, QUICK, { Scale = 1.1 }):Play()
			end)
			b.MouseLeave:Connect(function()
				TS:Create(sc, QUICK, { Scale = 1 }):Play()
				cancelHold(id)
			end)
			b.MouseButton1Down:Connect(function()
				startHold(id, g, sc, st)
			end)
			b.MouseButton1Up:Connect(function()
				cancelHold(id)
			end)
			b.Activated:Connect(function()
				if holdDoneFor == id then
					holdDoneFor = nil
					return
				end
				if dragMoved or os.clock() - lastDragEnd < 0.15 then
					return
				end
				if st == "hid" then -- zakryty: krótkie potrząśnięcie
					TS:Create(g, TweenInfo.new(0.05, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, 3, true), { Rotation = 8 }):Play()
					return
				end
				selected = (selected == id) and nil or id
				render(nil)
			end)
			g.Parent = map

			-- animacje wejścia
			if pulseId == id then
				sc.Scale = 1.35
				TS:Create(sc, POP, { Scale = 1 }):Play()
			elseif isNew(id) then
				sc.Scale = 0
				local delay = math.sqrt(node.x * node.x + node.y * node.y) * 0.06
				TS:Create(sc, TweenInfo.new(0.32, Enum.EasingStyle.Back, Enum.EasingDirection.Out, 0, false, delay), { Scale = 1 }):Play()
			end
		end
	end
	if lvl(root.id) >= 1 then
		for _, br in ipairs(Data.Branches[currentTab]) do
			nowShown["branch:" .. br.id] = true
		end
	end
	shown = nowShown
	showDetail()
	clampMap()
end

------------------------------------------------------------ wykrzyknik w ekwipunku
local alertIcon: ImageLabel? = nil
local alertTween: Tween? = nil
local function updateAlert()
	if not alertIcon then
		return
	end
	local any = false
	for _, node in pairs(Data.Nodes) do
		if canBuy(node) then
			any = true
			break
		end
	end
	if any and not alertIcon.Visible then
		alertIcon.Visible = true
		alertIcon.Rotation = -12
		alertTween = TS:Create(alertIcon, TweenInfo.new(0.5, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true), { Rotation = 12 })
		alertTween:Play()
	elseif not any and alertIcon.Visible then
		alertIcon.Visible = false
		if alertTween then
			alertTween:Cancel()
			alertTween = nil
		end
	end
end

------------------------------------------------------------ zakładki, otwieranie, zamykanie
local tabs = panel:WaitForChild("Tabs")
local TAB_BY_BUTTON = { TabPlayer = "Player", TabFortress = "Fortress", TabPets = "Pets" }

local function bounce(btn: GuiButton, onClick: () -> ())
	local sc = btn:FindFirstChildWhichIsA("UIScale")
	btn.MouseEnter:Connect(function()
		if sc then
			TS:Create(sc, QUICK, { Scale = 1.06 }):Play()
		end
	end)
	btn.MouseLeave:Connect(function()
		if sc then
			TS:Create(sc, QUICK, { Scale = 1 }):Play()
		end
	end)
	btn.MouseButton1Down:Connect(function()
		if sc then
			TS:Create(sc, QUICK, { Scale = 1 }):Play() -- nie mniej niż 1: spod przycisku nic nie wychodzi
		end
	end)
	btn.Activated:Connect(function()
		if sc then
			TS:Create(sc, POP, { Scale = 1 }):Play()
		end
		onClick()
	end)
end

------------------------------------------------------------ przyciski „wypalone” w tle (zakładki, X): bez skalowania i przesuwania
-- Przycisk leży co do piksela na swojej kopii w grafice tła — każde powiększenie, zmniejszenie albo przyciemnienie samego
-- obrazka odsłaniało kopię pod spodem (uwaga Pawła 16–17.11). Reakcja na mysz: nakładka-cień w kształcie przycisku
-- (ten sam obrazek na czarno; dla pola bez obrazka — zaokrąglony prostokąt) i podskok napisu.
-- przezroczystość cienia (1 = brak cienia): spoczynek lekko przygaszony, najechanie = rozjaśnienie (Paweł 18.11: napis
-- się nie animuje — przy skalowaniu wyjeżdżał za przycisk — tylko przycisk się podświetla)
local SHADE_ON, SHADE_OFF, SHADE_HOVER_OFF, SHADE_PRESS = 0.86, 0.5, 0.72, 0.62
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

-- jedno tło dla wszystkich zakładek (Paweł 17.11) — nic do przełączania
local function showBackground(_tab: string, _instant: boolean) end

local tabSetters: { [string]: (boolean) -> () } = {}
local function selectTab(tab: string, instant: boolean?)
	showBackground(tab, instant == true or currentTab == tab)
	currentTab = tab
	selected = nil
	for name, t in pairs(TAB_BY_BUTTON) do
		local b = tabs:FindFirstChild(name)
		if b then
			local active = t == tab
			if tabSetters[name] then
				tabSetters[name](active) -- cień-nakładka zamiast ImageColor3 (bez prześwitu kopii z ramki)
			end
			b.Label.TextColor3 = active and Color3.new(1, 1, 1) or Color3.fromRGB(205, 205, 205)
		end
	end
	zoom = 1
	applyScale()
	centerMap()
	shown = {}
	render("all")
end

for name, tab in pairs(TAB_BY_BUTTON) do
	local b = tabs:WaitForChild(name)
	tabSetters[name] = flatButton(b, function()
		if currentTab ~= tab then
			selectTab(tab)
		end
	end)
end

local panelScale = panel:WaitForChild("UIScale")
local closing = false
local function open()
	readLevels()
	closing = false
	gui.Enabled = true
	hint.Visible = true
	hint.TextTransparency = 0
	local hs = hint:FindFirstChildWhichIsA("UIStroke")
	if hs then
		hs.Transparency = 0
	end
	backdrop.BackgroundTransparency = 1
	TS:Create(backdrop, TweenInfo.new(0.2), { BackgroundTransparency = 0.45 }):Play()
	panelScale.Scale = 0.8
	TS:Create(panelScale, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	task.defer(selectTab, "Player", true) -- zawsze start na PLAYER (polecenie Pawła 15.11)
end

local function close()
	if closing or not gui.Enabled then
		return
	end
	closing = true
	dragging = false
	cancelHold(nil)
	TS:Create(backdrop, TweenInfo.new(0.15), { BackgroundTransparency = 1 }):Play()
	local t = TS:Create(panelScale, TweenInfo.new(0.15, Enum.EasingStyle.Quad, Enum.EasingDirection.In), { Scale = 0.85 })
	t.Completed:Connect(function()
		if closing then
			gui.Enabled = false
		end
	end)
	t:Play()
end

flatButton(panel:WaitForChild("CloseButton"), close) -- pole kliknięcia nad X wypalonym w ramce
backdrop.Activated:Connect(close)
UIS.InputBegan:Connect(function(input, processed)
	if not processed and gui.Enabled and input.KeyCode == Enum.KeyCode.Escape then
		close()
	end
end)


------------------------------------------------------------ zmiany stanu z serwera
local function refresh()
	readLevels()
	updateAlert()
	if gui.Enabled then
		render("new", pendingPulse)
		pendingPulse = nil
	end
end
player:GetAttributeChangedSignal("SkillTree"):Connect(refresh)
player:GetAttributeChangedSignal("Gems"):Connect(function()
	updateAlert()
	if gui.Enabled then
		render(nil) -- ceny zmieniają kolor (stać / nie stać)
	end
end)

------------------------------------------------------------ przycisk w ekwipunku
task.spawn(function()
	local eq = pg:WaitForChild("EquipmentPanel")
	local btn = eq:WaitForChild("Panel"):WaitForChild("Character"):WaitForChild("SkillTreeButton", 30)
	if not btn then
		warn("[SkillTree] brak przycisku SkillTreeButton w oknie ekwipunku")
		return
	end
	alertIcon = btn:WaitForChild("Alert")
	bounce(btn, open)
	readLevels()
	updateAlert()
end)

------------------------------------------------------------ wczytanie grafik z góry
-- tła zakładek i ikony węzłów ładują się przy starcie gry, więc zmiana zakładki nie czeka na obraz
task.spawn(function()
	local holder = Instance.new("Folder")
	holder.Name = "Preload"
	local list = {}
	table.insert(list, bgImage)
	for _, id in pairs(Icons) do
		local l = Instance.new("ImageLabel")
		l.Image = id
		l.Parent = holder
		table.insert(list, l)
	end
	holder.Parent = gui
	pcall(function()
		game:GetService("ContentProvider"):PreloadAsync(list)
	end)
	holder:Destroy()
end)

readLevels()
