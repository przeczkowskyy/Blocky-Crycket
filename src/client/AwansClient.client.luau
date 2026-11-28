--!strict
--[[
	AwansClient — animacja awansu na poziom (Paweł 26.11: „animacja awansu za poziom, żeby konfetti wyskakiwało”).
	GUI: src/gui/Awans.model.json (tools/okno_indeksu_build_gui.py; grafika: złota wstęga i wybuch światła z
	tools/okno_indeksu_ui.py).

	Nasłuchuje atrybutu gracza „Level” (ustawia go stan gracza Karola). Gdy poziom ROŚNIE w trakcie gry: wybuch
	światła się obraca, wstęga „LEVEL UP!” wyskakuje ze sprężyną, pod nią „LEVEL N”, z góry sypie się kolorowe
	konfetti. Wczytanie zapisu przy wejściu (skok z 1 na zapisany poziom) nie odpala animacji — liczymy dopiero
	po ekranie ładowania (atrybut LoadingDone) i krótkiej chwili spokoju.
]]
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local TS = game:GetService("TweenService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("Awans") :: ScreenGui
local banner = gui:WaitForChild("Banner") :: Frame
local skala = banner:WaitForChild("UIScale") :: UIScale
local blask = banner:WaitForChild("Glow") :: ImageLabel
local wstega = banner:WaitForChild("Ribbon") :: ImageLabel
local tytul = banner:WaitForChild("Title") :: TextLabel
local poziomTxt = banner:WaitForChild("Level") :: TextLabel
local warstwa = gui:WaitForChild("Confetti") :: Frame

local KOLORY = { "FF5A5A", "FFD65A", "5AD17A", "4FB3FF", "C27BFF", "FF9F43", "FFFFFF" }
local ILE_WYBUCH, ILE_DESZCZ = 60, 70 -- kawałki z wybuchu przy wstędze i z deszczu z góry ekranu
local CZAS_POKAZU = 2.8
local SPOKOJ_PO_WCZYTANIU = 4 -- s po ekranie ładowania, zanim liczymy awanse

task.spawn(function()
	pcall(function()
		game:GetService("ContentProvider"):PreloadAsync({ blask, wstega }) -- pierwszy awans bez pustej wstęgi
	end)
end)

local gotowy = false
local ostatni = 0
local pokaz = 0 -- licznik pokazów (nowy awans w trakcie przerywa stary)

------------------------------------------------------------------ konfetti
local function konfetti()
	local ekran = warstwa.AbsoluteSize
	if ekran.X <= 0 then
		return
	end
	local skalaPx = ekran.Y / 1080
	local czesci = {}
	local function kawalek(x0: number, y0: number, vx: number, vy: number)
		local f = Instance.new("Frame")
		local w = math.random(16, 28) * skalaPx
		f.Size = UDim2.fromOffset(w, w * (if math.random() < 0.5 then 0.5 else 1))
		f.AnchorPoint = Vector2.new(0.5, 0.5)
		f.BackgroundColor3 = Color3.fromHex(KOLORY[math.random(#KOLORY)])
		f.BorderSizePixel = 0
		f.ZIndex = 1
		if math.random() < 0.3 then
			local c = Instance.new("UICorner")
			c.CornerRadius = UDim.new(1, 0)
			c.Parent = f
		end
		table.insert(czesci, { f = f, x = x0, y = y0, vx = vx, vy = vy, obrot = math.random(0, 360),
			vo = math.random(-540, 540), zycie = 0 })
		f.Position = UDim2.fromOffset(x0, y0)
		f.Parent = warstwa
	end
	-- wybuch spod wstęgi: szeroko na boki, lekko w górę, potem opada
	for _ = 1, ILE_WYBUCH do
		local kat = math.rad(math.random(195, 345))
		local v = math.random(350, 800) * skalaPx
		kawalek(ekran.X * 0.5 + math.random(-80, 80) * skalaPx, ekran.Y * 0.32, math.cos(kat) * v * 1.4,
			math.sin(kat) * v * 0.6)
	end
	-- deszcz z góry ekranu na całą szerokość (część startuje z opóźnieniem — wyżej nad krawędzią)
	for _ = 1, ILE_DESZCZ do
		kawalek(math.random() * ekran.X, -math.random(20, 420) * skalaPx, math.random(-60, 60) * skalaPx,
			math.random(60, 220) * skalaPx)
	end
	local grawitacja = 700 * skalaPx
	local polaczenie: RBXScriptConnection
	polaczenie = RunService.RenderStepped:Connect(function(dt)
		local zywe = 0
		for _, c in ipairs(czesci) do
			if c.f.Parent then
				c.zycie += dt
				c.vy += grawitacja * dt
				c.vx *= (1 - 1.2 * dt)
				c.vy = math.min(c.vy, 520 * skalaPx) -- opór powietrza: konfetti opada, nie spada jak kamień
				c.x += c.vx * dt
				c.y += c.vy * dt
				c.obrot += c.vo * dt
				c.f.Position = UDim2.fromOffset(c.x, c.y)
				c.f.Rotation = c.obrot
				if c.zycie > 3.2 then
					c.f.BackgroundTransparency = math.clamp((c.zycie - 3.2) / 0.6, 0, 1)
				end
				if c.zycie > 3.8 or c.y > ekran.Y + 40 then
					c.f:Destroy()
				else
					zywe += 1
				end
			end
		end
		if zywe == 0 then
			polaczenie:Disconnect()
		end
	end)
end

------------------------------------------------------------------ wstęga i blask
local function pokazAwans(poziom: number)
	pokaz += 1
	local moj = pokaz
	poziomTxt.Text = "LEVEL " .. tostring(poziom)
	banner.Visible = true
	skala.Scale = 0.2
	blask.Rotation = 0
	blask.ImageTransparency = 0.15
	for _, o in ipairs({ wstega, tytul, poziomTxt }) do
		if o:IsA("ImageLabel") then
			o.ImageTransparency = 0
		elseif o:IsA("TextLabel") then
			o.TextTransparency = 0
			local s = o:FindFirstChildOfClass("UIStroke")
			if s then
				s.Transparency = 0
			end
		end
	end
	TS:Create(skala, TweenInfo.new(0.45, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
	TS:Create(blask, TweenInfo.new(CZAS_POKAZU + 0.5, Enum.EasingStyle.Linear), { Rotation = 120 }):Play()
	konfetti()
	task.delay(CZAS_POKAZU, function()
		if moj ~= pokaz then
			return
		end
		local zanik = TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		TS:Create(skala, zanik, { Scale = 0.85 }):Play()
		TS:Create(blask, zanik, { ImageTransparency = 1 }):Play()
		TS:Create(wstega, zanik, { ImageTransparency = 1 }):Play()
		for _, t in ipairs({ tytul, poziomTxt }) do
			TS:Create(t, zanik, { TextTransparency = 1 }):Play()
			local s = t:FindFirstChildOfClass("UIStroke")
			if s then
				TS:Create(s, zanik, { Transparency = 1 }):Play()
			end
		end
		task.delay(0.5, function()
			if moj == pokaz then
				banner.Visible = false
			end
		end)
	end)
end

------------------------------------------------------------------ nasłuch poziomu
local function poziom(): number
	local l = player:GetAttribute("Level")
	return if type(l) == "number" then l else 0
end

player:GetAttributeChangedSignal("Level"):Connect(function()
	local teraz = poziom()
	if gotowy and teraz > ostatni then
		pokazAwans(teraz)
	end
	ostatni = teraz
end)

task.spawn(function()
	local t0 = os.clock()
	while not player:GetAttribute("LoadingDone") and os.clock() - t0 < 60 do
		task.wait(0.5)
	end
	task.wait(SPOKOJ_PO_WCZYTANIU)
	ostatni = poziom()
	gotowy = true
end)
