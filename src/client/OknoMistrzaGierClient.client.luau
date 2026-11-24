--!strict
--[[
	OknoMistrzaGierClient — okno planszy mistrza gier (D-053, Paweł 24.11). Grafika: src/gui/OknoMistrzaGier
	(tools/okna_build_gui.py), serwer: src/server/MistrzGier.server.luau (decyduje o rzucie i nagrodzie).

	Otwieranie: E „Zagraj” przy mistrzu gier w karczmie (pakiet bazaru Karola woła ReplicatedStorage.OknoMiejsca:Fire
	("mistrz_gier"); atrybut mistrz_gier = true wyłącza jego dymek „w budowie”). Zamyka X, Esc albo odejście.
	Pionek to okrągła ikona rasy gracza (kot). Rzut: kostka miga i staje na wyniku, pionek skacze pole po polu,
	nad polem wyskakuje nagroda. Okno otwiera się od razu, bez wjazdu (Paweł 24.11).
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("OknoMistrzaGier") :: ScreenGui
local panel = gui:WaitForChild("Panel") :: Frame
local F = RS:WaitForChild("MistrzGier") :: RemoteFunction
local okRace, RaceIcons = pcall(function()
	return require(RS:WaitForChild("Shared"):WaitForChild("RaceIcons"))
end)

local fields = panel:WaitForChild("Fields") :: Frame
local pawn = panel:WaitForChild("Pawn") :: ImageLabel
local dice = panel:WaitForChild("Dice") :: Frame
local face = dice:WaitForChild("Face") :: TextLabel
local price = panel:WaitForChild("Price") :: TextLabel
local timer = panel:WaitForChild("Timer") :: TextLabel
local msg = panel:WaitForChild("Message") :: TextLabel
local board = panel:WaitForChild("Board") :: TextLabel
local reward = panel:WaitForChild("Reward") :: TextLabel
local rewardIcon = panel:WaitForChild("RewardIcon") :: ImageLabel

-- ikony nagród pól (Paweł 24.11: „plus, liczba i ikonka — rybki, diamenty, przedmiot”) — ID z assets/manifest.json
local IKONY = {
	rybki = "rbxassetid://76704302626777", -- GoldFish
	gwiazda = "rbxassetid://76704302626777",
	diamenty = "rbxassetid://130974323293639", -- Gem
	przedmiot = "rbxassetid://71553702739963", -- NodeIncChest (skrzynka)
}
-- pionek z planszy (wycięty z grafiki, tools/pionek_mistrza.py; Paweł 24.11: po planszy chodzi pionek, nie ikona gracza)
local PIONEK = "rbxassetid://104058018910695" -- PionekMistrza

local function bindable(name: string): BindableEvent
	local e = RS:FindFirstChild(name)
	if not e then
		e = Instance.new("BindableEvent")
		e.Name = name
		e.Parent = RS
	end
	return e :: BindableEvent
end
local okna = bindable("OknoMiejsca")
okna:SetAttribute("mistrz_gier", true)

local stan: any = nil
local otwarte, toczy = false, false
local miejsceOtwarcia: Vector3? = nil

local function pole(i: number): Frame
	return fields:FindFirstChild(string.format("Field%02d", i)) :: Frame
end

local function srodekPola(i: number): UDim2
	local f = pole(i)
	return UDim2.fromScale(f.Position.X.Scale + f.Size.X.Scale / 2, f.Position.Y.Scale + f.Size.Y.Scale * 0.9)
end

local function ustawPionek()
	if typeof(PIONEK) == "string" and PIONEK ~= "" then
		pawn.Image = PIONEK
		return
	end
	local race = player:GetAttribute("Race")
	local id = if typeof(race) == "string" then "Race" .. race else "RaceHuman"
	if okRace and RaceIcons[id] then
		pawn.Image = RaceIcons[id]
	end
end

local function komunikat(t: string)
	msg.Text = t
end

local function rysuj()
	if not stan then
		return
	end
	for i = 1, stan.pol do
		local f = pole(i)
		if f then
			local n = stan.nagrody[i]
			local v = f:FindFirstChild("Value") :: TextLabel
			local ic = f:FindFirstChild("Icon") :: ImageLabel
			if n.typ == "start" then
				v.Text, ic.Image = "", ""
			elseif n.typ == "przedmiot" then
				v.Text, ic.Image = "", IKONY.przedmiot
			else
				v.Text, ic.Image = "+" .. n.ile, IKONY[n.typ] or ""
			end
		end
	end
	pawn.Position = srodekPola(stan.pole)
	board.Text = "BOARD " .. tostring(stan.plansza)
end

local function rysujCene()
	if not stan then
		return
	end
	if stan.darmowyZa <= 0 then
		price.Text = "FREE ROLL"
		timer.Text = "" -- bez odliczania (Paweł 24.11)
	else
		price.Text = tostring(stan.cena) .. " FISH"
		timer.Text = string.format("%d:%02d", stan.darmowyZa // 60, stan.darmowyZa % 60)
	end
end

local function odswiez()
	local ok, w = pcall(function()
		return F:InvokeServer("stan")
	end)
	if ok and type(w) == "table" and w.ok then
		stan = w
		rysuj()
		rysujCene()
		if not w.stanGracza then
			komunikat("Rewards need the player state (Karol) — board works")
		end
	end
end

local function skok(z: number, na: number)
	for i = z + 1, na do
		local cel = srodekPola(i)
		local start = pawn.Position
		local t0 = os.clock()
		local czas = 0.16
		while true do
			local u = math.clamp((os.clock() - t0) / czas, 0, 1)
			local x = start.X.Scale + (cel.X.Scale - start.X.Scale) * u
			local y = start.Y.Scale + (cel.Y.Scale - start.Y.Scale) * u - math.sin(u * math.pi) * 0.04
			pawn.Position = UDim2.fromScale(x, y)
			if u >= 1 then
				break
			end
			task.wait()
		end
	end
end

local function pokazNagrode(ile: number, napis: string?, typ: string?)
	reward.Text = napis or ("+" .. ile)
	local p = pawn.Position
	reward.Position = UDim2.fromScale(p.X.Scale - reward.Size.X.Scale / 2, p.Y.Scale - 0.16)
	rewardIcon.Image = IKONY[typ or "rybki"] or ""
	rewardIcon.Visible = rewardIcon.Image ~= ""
	rewardIcon.ImageTransparency = 0
	rewardIcon.Position = UDim2.fromScale(reward.Position.X.Scale + reward.Size.X.Scale * 0.82, reward.Position.Y.Scale)
	TS:Create(rewardIcon, TweenInfo.new(1.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Position = rewardIcon.Position - UDim2.fromScale(0, 0.08), ImageTransparency = 1 }):Play()
	reward.TextTransparency = 0
	reward.Visible = true
	local sc = reward:FindFirstChildWhichIsA("UIStroke")
	TS:Create(reward, TweenInfo.new(1.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
		{ Position = reward.Position - UDim2.fromScale(0, 0.08), TextTransparency = 1 }):Play()
	if sc then
		sc.Transparency = 0
		TS:Create(sc, TweenInfo.new(1.2), { Transparency = 1 }):Play()
	end
end

local function rzuc()
	if toczy or not stan then
		return
	end
	toczy = true
	komunikat("")
	local ok, w = pcall(function()
		return F:InvokeServer("rzut", stan.darmowyZa > 0)
	end)
	if not ok or type(w) ~= "table" or not w.ok then
		komunikat(if ok and type(w) == "table" and w.tekst then w.tekst else "…")
		toczy = false
		return
	end
	-- kostka: miga przez 0,7 s, staje na wyniku
	local t0 = os.clock()
	while os.clock() - t0 < 0.7 do
		face.Text = tostring(math.random(1, 6))
		dice.Rotation = math.random(-12, 12)
		task.wait(0.06)
	end
	dice.Rotation = 0
	face.Text = tostring(w.kostka)
	skok(w.z, w.na)
	if w.nowaPlansza then
		pokazNagrode(w.nagroda, "STAR! +" .. w.nagroda, "rybki")
		komunikat(string.format("Board %d done! New, better board.", w.planszaRzutu))
		task.wait(1.2)
	elseif w.typ == "przedmiot" then
		pokazNagrode(0, "ITEM!", "przedmiot")
	else
		pokazNagrode(w.nagroda, nil, w.typ)
	end
	if not w.wyplacono and w.nagroda > 0 then
		komunikat("Reward not paid — player state (Karol) not running")
	end
	stan = w
	rysuj()
	rysujCene()
	toczy = false
end

local function otworz()
	if otwarte then
		return
	end
	otwarte = true
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	miejsceOtwarcia = root and root.Position or nil
	ustawPionek()
	komunikat("")
	reward.Visible = false
	face.Text = "?"
	gui.Enabled = true
	odswiez()
end

local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
end

okna.Event:Connect(function(id)
	if id == "mistrz_gier" then
		otworz()
	end
end);
(panel:WaitForChild("CloseButton") :: GuiButton).Activated:Connect(zamknij);
(gui:WaitForChild("Backdrop") :: GuiButton).Activated:Connect(zamknij);
(panel:WaitForChild("RollButton") :: GuiButton).Activated:Connect(rzuc)
UIS.InputBegan:Connect(function(input, processed)
	if not otwarte then
		return
	end
	if input.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	elseif not processed and input.KeyCode == Enum.KeyCode.Space then
		rzuc()
	end
end)

-- licznik darmowego rzutu i odejście od mistrza
task.spawn(function()
	while true do
		task.wait(1)
		if otwarte and stan then
			if stan.darmowyZa > 0 then
				stan.darmowyZa -= 1
				rysujCene()
			end
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root and miejsceOtwarcia and (root.Position - miejsceOtwarcia).Magnitude > 14 then
				zamknij()
			end
		end
	end
end)
