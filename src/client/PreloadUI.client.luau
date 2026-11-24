--!strict
--[[
	PreloadUI — wczytuje z wyprzedzeniem wszystkie grafiki interfejsu (Paweł 24.11: przyciski i ramki okien mają się
	pokazywać natychmiast, bez „migania”).

	Dlaczego: ekran ładowania (ReplicatedFirst) wczytuje tylko zawartość ReplicatedStorage. Okna z PlayerGui są
	wyłączone (Enabled = false), więc Roblox ściąga ich obrazki dopiero przy pierwszym otwarciu — okno stało przez
	chwilę puste i grafiki „wskakiwały”. To samo z ikonami ustawianymi z kodu (moduły ID: AssetIds, RaceIcons,
	RacePortraits, ikony przedmiotów…).

	Pomiar 24.11: po samym PreloadAsync obrazki w wyłączonych oknach nadal mają IsLoaded = false — Roblox ściąga plik,
	ale teksturę przygotowuje dopiero przy pierwszym narysowaniu. Dlatego po wczytaniu każdy obrazek jest RAZ rysowany
	jako prawie przezroczysty piksel w rogu ekranu (ScreenGui „PodgrzewanieGrafik”, kilka sekund), a potem usuwany.

	Co robi: zaraz po starcie zbiera wszystkie ImageLabel/ImageButton z PlayerGui (także w oknach wyłączonych) i wszystkie
	napisy „rbxassetid://…” z modułów ReplicatedStorage.Shared (tabele z ID), usuwa powtórki i woła
	ContentProvider:PreloadAsync partiami. Okna dodane później (np. po wdrożeniu) też są wczytywane.
]]

local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local CP = game:GetService("ContentProvider")

local player = Players.LocalPlayer
local pg = player:WaitForChild("PlayerGui")

local widziane: { [string]: boolean } = {}

local function dodaj(lista: { string }, id: any)
	if typeof(id) == "string" and id ~= "" and id ~= "rbxassetid://0" and not widziane[id] then
		widziane[id] = true
		table.insert(lista, id)
	end
end

local function zObiektu(lista: { string }, o: Instance)
	if o:IsA("ImageLabel") or o:IsA("ImageButton") then
		dodaj(lista, (o :: any).Image)
		if o:IsA("ImageButton") then
			dodaj(lista, (o :: ImageButton).HoverImage)
			dodaj(lista, (o :: ImageButton).PressedImage)
		end
	elseif o:IsA("Decal") or o:IsA("Texture") then
		dodaj(lista, (o :: any).Texture)
	end
end

local function zTabeli(lista: { string }, t: any, glebokosc: number)
	if glebokosc > 4 or typeof(t) ~= "table" then
		return
	end
	for _, v in pairs(t) do
		if typeof(v) == "string" then
			if v:sub(1, 13) == "rbxassetid://" then
				dodaj(lista, v)
			end
		elseif typeof(v) == "table" then
			zTabeli(lista, v, glebokosc + 1)
		end
	end
end

local function podgrzej(lista: { string })
	-- każdy obrazek narysowany raz (1 × 1 px, prawie przezroczysty) — tekstura gotowa przed otwarciem okna
	local g = Instance.new("ScreenGui")
	g.Name = "PodgrzewanieGrafik"
	g.ResetOnSpawn = false
	g.DisplayOrder = -1000
	g.IgnoreGuiInset = true
	local etykiety = {}
	for _, id in ipairs(lista) do
		local l = Instance.new("ImageLabel")
		l.BackgroundTransparency = 1
		l.Size = UDim2.fromOffset(1, 1)
		l.Position = UDim2.fromOffset(0, 0)
		l.ImageTransparency = 0.99
		l.Image = id
		l.Parent = g
		table.insert(etykiety, l)
	end
	g.Parent = pg
	local koniec = os.clock() + 8
	while os.clock() < koniec do
		local gotowe = true
		for _, l in ipairs(etykiety) do
			if not l.IsLoaded then
				gotowe = false
				break
			end
		end
		if gotowe then
			break
		end
		task.wait(0.25)
	end
	g:Destroy()
end

local function wczytaj(lista: { string })
	local PARTIA = 40
	for s = 1, #lista, PARTIA do
		local czesc = table.move(lista, s, math.min(s + PARTIA - 1, #lista), 1, {})
		pcall(function()
			CP:PreloadAsync(czesc)
		end)
	end
	podgrzej(lista)
end

-- 1) okna i HUD (wszystkie ScreenGui, także wyłączone)
local lista: { string } = {}
for _, o in ipairs(pg:GetDescendants()) do
	zObiektu(lista, o)
end
-- 2) ID z modułów w Shared (tylko te, które wyglądają na tabele z ID — inne moduły pomijamy, żeby nic nie odpalać)
local shared = RS:FindFirstChild("Shared")
if shared then
	for _, m in ipairs(shared:GetDescendants()) do
		if m:IsA("ModuleScript") then
			local ok, nazwa = pcall(function()
				return m.Name
			end)
			if ok and (nazwa:find("Ikon") or nazwa:find("Icon") or nazwa:find("Asset") or nazwa:find("Portrait")
				or nazwa:find("Race") or nazwa:find("Item")) then
				local ok2, t = pcall(require, m)
				if ok2 then
					zTabeli(lista, t, 0)
				end
			end
		end
	end
end
task.spawn(wczytaj, lista)

-- 3) okna dodane później
pg.DescendantAdded:Connect(function(o)
	local nowe: { string } = {}
	zObiektu(nowe, o)
	if #nowe > 0 then
		task.spawn(wczytaj, nowe)
	end
end)
