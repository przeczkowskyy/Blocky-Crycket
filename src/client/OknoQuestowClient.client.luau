--!strict
--[[
	OknoQuestowClient — okno tablicy questów (Paweł 25.11: tablica w miasteczku zamiast rankingu). Grafika:
	src/gui/OknoQuestow (tools/okno_questow_build_gui.py), serwer: src/server/Questy.server.luau (liczy postęp,
	pilnuje limitu śledzonych i wypłaca nagrody — klient tylko pokazuje i wysyła „sledz” / „odbierz”).

	Otwieranie: E przy tablicy ogłoszeń na bazarze (pakiet Karola woła ReplicatedStorage.OknoMiejsca:Fire("tablica");
	atrybut tablica = true wyłącza jego dymek „ranking wkrótce”). Zamyka X, Esc, tło albo odejście.
	Dwie karty po lewej: DAILY (dzienne) i GOALS (osiągnięcia). Wiersz: nazwa, postęp, nagroda, przycisk
	TRACK / UNTRACK (przypina do szuflady po prawej, do 3) albo CLAIM (gotowy quest) / DONE.

	Ten skrypt karmi też szufladę (ReplicatedStorage.QuestyPanel "ustaw") — także gdy okno jest zamknięte:
	serwer po zmianie postępu wysyła nowy stan przez QuestyZdarzenia.

	Lico tablicy w świecie: u gracza (lokalnie, w czasie gry) ranking Karola na tablicy jest wyłączony i w jego miejscu
	wisi nasz napis „QUEST BOARD”, a podpowiedź E mówi „Quests”. Pliki i obiekty Karola w Studio bez zmian — docelowo
	powinien to przełączyć jego pakiet (pytanie w sejfie).
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("OknoQuestow") :: ScreenGui
local panel = gui:WaitForChild("Panel") :: Frame
local F = RS:WaitForChild("Questy") :: RemoteFunction
local Z = RS:WaitForChild("QuestyZdarzenia") :: RemoteEvent

local tabDaily = panel:WaitForChild("TabDaily") :: ImageButton
local tabGoals = panel:WaitForChild("TabAchievements") :: ImageButton
local trackedL = panel:WaitForChild("Tracked") :: TextLabel
local resetL = panel:WaitForChild("Reset") :: TextLabel
local msg = panel:WaitForChild("Message") :: TextLabel

local WIERSZY = 6
local IKONY = { fish = "rbxassetid://76704302626777", gems = "rbxassetid://130974323293639" }
local wzorWiersza = panel:WaitForChild("Row1") :: ImageLabel
local ZIELONY = ((wzorWiersza:WaitForChild("Button") :: ImageButton).Image)
local IKONA_DZIENNE = (tabDaily:WaitForChild("Icon") :: ImageLabel).Image
local IKONA_CELE = (tabGoals:WaitForChild("Icon") :: ImageLabel).Image
local ZLOTY = (panel:WaitForChild("GoldButtonArt") :: ImageLabel).Image -- ukryta etykieta niesie obraz złotego przycisku

local stan: any = nil
local karta = "dzienne" -- "dzienne" | "osiagniecia"
local otwarte, czeka = false, false
local miejsceOtwarcia: Vector3? = nil
local resetO: number? = nil -- os.clock(), o którym mija doba

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
okna:SetAttribute("tablica", true)

-- szuflada po prawej: śledzone questy w kolejności wyboru
local function doSzuflady()
	if not stan then
		return
	end
	local wszystkie: { [string]: any } = {}
	for _, lista in ipairs({ stan.dzienne, stan.osiagniecia }) do
		for _, q in ipairs(lista) do
			wszystkie[q.id] = q
		end
	end
	local t = {}
	for _, id in ipairs(stan.sledzone) do
		local q = wszystkie[id]
		if q then
			table.insert(t, { nazwa = q.nazwa, opis = q.opis, postep = q.postep, cel = q.cel, nagroda = q.nagroda,
				waluta = q.waluta, gotowe = q.gotowe })
		end
	end
	task.spawn(function()
		local api = RS:WaitForChild("QuestyPanel", 30)
		if api and api:IsA("BindableFunction") then
			api:Invoke("ustaw", t)
		end
	end)
end

local function komunikat(t: string?)
	msg.Text = t or ""
end

local function przygas(b: ImageButton, aktywna: boolean)
	b.ImageColor3 = if aktywna then Color3.new(1, 1, 1) else Color3.fromRGB(150, 150, 150)
	local l = b:FindFirstChild("Label")
	if l and l:IsA("TextLabel") then
		l.TextTransparency = if aktywna then 0 else 0.35
	end
end

local function rysuj()
	przygas(tabDaily, karta == "dzienne")
	przygas(tabGoals, karta == "osiagniecia")
	if not stan then
		return
	end
	local lista = if karta == "dzienne" then stan.dzienne else stan.osiagniecia
	for i = 1, WIERSZY do
		local w = panel:FindFirstChild("Row" .. i) :: ImageLabel
		local q = lista[i]
		w.Visible = q ~= nil
		if q then
			local b = w:FindFirstChild("Button") :: ImageButton
			local bl = b:FindFirstChild("Label") :: TextLabel;
			(w:FindFirstChild("Icon") :: ImageLabel).Image = if karta == "dzienne" then IKONA_DZIENNE else IKONA_CELE;
			(w:FindFirstChild("Icon") :: ImageLabel).ImageTransparency = if q.odebrane then 0.6 else 0;
			(w:FindFirstChild("Check") :: TextLabel).Text = if q.odebrane then "✓" else "";
			(w:FindFirstChild("QuestName") :: TextLabel).Text = q.nazwa;
			(w:FindFirstChild("Progress") :: TextLabel).Text = string.format("%s  %d/%d", q.opis, q.postep, q.cel);
			(w:FindFirstChild("Reward") :: TextLabel).Text = "+" .. q.nagroda;
			(w:FindFirstChild("RewardIcon") :: ImageLabel).Image = IKONY[q.waluta] or ""
			w.ImageTransparency = if q.odebrane then 0.35 else 0
			if q.odebrane then
				bl.Text, b.Image, b.ImageColor3, b.Active = "DONE", ZIELONY, Color3.fromRGB(140, 140, 140), false
			elseif q.gotowe then
				bl.Text, b.Image, b.ImageColor3, b.Active = "CLAIM", ZLOTY, Color3.new(1, 1, 1), true
			elseif q.sledzone then
				bl.Text, b.Image, b.ImageColor3, b.Active = "UNTRACK", ZIELONY, Color3.fromRGB(190, 190, 190), true
			else
				bl.Text, b.Image, b.ImageColor3, b.Active = "TRACK", ZIELONY, Color3.new(1, 1, 1), true
			end
		end
	end
	trackedL.Text = string.format("TRACKED %d/%d", #stan.sledzone, stan.maks)
end

local function rysujReset()
	if karta == "dzienne" and resetO then
		local s = math.max(0, math.floor(resetO - os.clock()))
		resetL.Text = string.format("NEW IN %d:%02d:%02d", s // 3600, s % 3600 // 60, s % 60)
	else
		resetL.Text = ""
	end
end

local function przyjmij(w: any)
	if type(w) == "table" and w.ok then
		stan = w
		resetO = os.clock() + (w.doPolnocy or 0)
		doSzuflady()
		if otwarte then
			rysuj()
			rysujReset()
		end
	end
end

local function zapytaj(akcja: string, id: string?): any
	local ok, w = pcall(function()
		return F:InvokeServer(akcja, id)
	end)
	if not ok or type(w) ~= "table" then
		return nil
	end
	przyjmij(w)
	if w.tekst then
		komunikat(w.tekst)
	end
	return w
end

local function klik(i: number)
	if czeka or not stan then
		return
	end
	local lista = if karta == "dzienne" then stan.dzienne else stan.osiagniecia
	local q = lista[i]
	if not q or q.odebrane then
		return
	end
	czeka = true
	komunikat("")
	local w = zapytaj(if q.gotowe then "odbierz" else "sledz", q.id)
	if w and w.ok and q.gotowe then
		local wiersz = panel:FindFirstChild("Row" .. i) :: ImageLabel
		local sc = (wiersz:FindFirstChild("Button") :: ImageButton):FindFirstChildWhichIsA("UIScale")
		if sc then
			sc.Scale = 1.2
			TS:Create(sc, TweenInfo.new(0.3, Enum.EasingStyle.Back, Enum.EasingDirection.Out), { Scale = 1 }):Play()
		end
	end
	czeka = false
end

local function otworz()
	if otwarte then
		return
	end
	otwarte = true
	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	miejsceOtwarcia = root and root.Position or nil
	komunikat("")
	gui.Enabled = true
	rysuj()
	zapytaj("stan")
end

local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
end

for i = 1, WIERSZY do
	local w = panel:WaitForChild("Row" .. i) :: ImageLabel
	(w:WaitForChild("Button") :: ImageButton).Activated:Connect(function()
		klik(i)
	end)
end
local function ustawKarte(nazwa: string)
	if karta ~= nazwa then
		karta = nazwa
		komunikat("")
		rysuj()
		rysujReset()
	end
end
tabDaily.Activated:Connect(function()
	ustawKarte("dzienne")
end)
tabGoals.Activated:Connect(function()
	ustawKarte("osiagniecia")
end);
(panel:WaitForChild("CloseButton") :: GuiButton).Activated:Connect(zamknij);
(gui:WaitForChild("Backdrop") :: GuiButton).Activated:Connect(zamknij)
UIS.InputBegan:Connect(function(input)
	if otwarte and input.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	end
end)
okna.Event:Connect(function(id)
	if id == "tablica" then
		otworz()
	end
end)
Z.OnClientEvent:Connect(function(co: any, w: any)
	if co == "stan" then
		przyjmij(w)
	end
end)

-- pierwszy stan (szuflada po wejściu do gry), licznik doby i odejście od tablicy
task.spawn(function()
	task.wait(2)
	zapytaj("stan")
	while true do
		task.wait(1)
		if otwarte then
			rysujReset()
			local char = player.Character
			local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
			if root and miejsceOtwarcia and (root.Position - miejsceOtwarcia).Magnitude > 16 then
				zamknij()
			end
		end
	end
end)

-- lico tablicy w świecie (lokalnie): nasz napis zamiast rankingu, „Quests” na podpowiedzi E
task.spawn(function()
	local gra = workspace:WaitForChild("MiasteczkoBazarGra", 120)
	if not gra then
		return
	end
	local tablica = gra:WaitForChild("Tablica", 30)
	local ekran = tablica and tablica:WaitForChild("Ekran", 30)
	if ekran and ekran:IsA("BasePart") then
		local ranking = ekran:FindFirstChildWhichIsA("SurfaceGui")
		local sg = Instance.new("SurfaceGui")
		sg.Name = "QuestBoardFace"
		sg.Face = if ranking then ranking.Face else Enum.NormalId.Front
		sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
		sg.PixelsPerStud = 40
		sg.LightInfluence = 0
		if ranking then
			ranking.Enabled = false
		end
		local function napis(tekst: string, y: number, h: number, kolor: Color3)
			local l = Instance.new("TextLabel")
			l.BackgroundTransparency = 1
			l.Position, l.Size = UDim2.fromScale(0.05, y), UDim2.fromScale(0.9, h)
			l.Text, l.TextColor3, l.TextScaled = tekst, kolor, true
			l.FontFace = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
			local st = Instance.new("UIStroke")
			st.Thickness, st.Color = 3, Color3.fromRGB(26, 20, 16)
			st.Parent = l
			l.Parent = sg
		end
		napis("QUEST BOARD", 0.1, 0.34, Color3.fromRGB(255, 214, 90))
		napis("DAILY QUESTS & GOALS", 0.5, 0.16, Color3.new(1, 1, 1))
		napis("PRESS E", 0.72, 0.16, Color3.fromRGB(252, 227, 176))
		sg.Parent = ekran
	end
	local punkty = gra:FindFirstChild("Punkty")
	local e = punkty and punkty:FindFirstChild("E tablica")
	local pp = e and e:FindFirstChildWhichIsA("ProximityPrompt", true)
	if pp then
		pp.ActionText = "Quests"
		pp.ObjectText = "Quest board"
	end
end)
