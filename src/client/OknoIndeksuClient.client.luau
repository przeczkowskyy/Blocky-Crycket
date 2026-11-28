--!strict
--[[
	OknoIndeksuClient — okno Index (kolekcja) pod przyciskiem „Index” w HUD (Paweł 26.11).
	GUI: src/gui/OknoIndeksu.model.json (tools/okno_indeksu_build_gui.py, grafika tools/okno_indeksu_ui.py).

	Zakładka PETS: wszystkie pety do zdobycia, pogrupowane według krain (las, Bagno, Dżungla — kraina jajka, dane Karola
	przez src/server/Indeks.server.luau). Zdobyte: podobizna 3D w kolorach i ramka w kolorze rzadkości; niezdobyte:
	czarna sylwetka i „???”. Najechanie pokazuje rzadkość i umiejętność.
	Zakładka ITEMS: przedmioty z katalogu Karola (Shared.IndeksPrzedmioty) TYLKO dla klasy gracza (atrybut Class),
	pogrupowane według krain/stopni (Starter, Forest, Swamp, Jungle), z ikoną (Shared.IkonyPrzedmiotow) i poziomem.

	Otwieranie: przycisk „Index” (ReplicatedStorage.HUDButtonPressed). Zamykanie: X, tło, Esc, znów „Index”
	albo inny przycisk HUD.
]]
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")

local player = Players.LocalPlayer
local gui = player:WaitForChild("PlayerGui"):WaitForChild("OknoIndeksu") :: ScreenGui
local panel = gui:WaitForChild("Panel") :: Frame
local lista = panel:WaitForChild("List") :: ScrollingFrame
local postep = panel:WaitForChild("Progress") :: TextLabel
local podpis = panel:WaitForChild("Hint") :: TextLabel
local tabPets = panel:WaitForChild("TabPets") :: ImageButton
local tabItems = panel:WaitForChild("TabItems") :: ImageButton
local art = gui:WaitForChild("Art")
local OBRAZ_AKTYWNA = (art:WaitForChild("TabActive") :: StringValue).Value
local OBRAZ_ZWYKLA = (art:WaitForChild("TabIdle") :: StringValue).Value

local Shared = RS:WaitForChild("Shared")
local Przedmioty = require(Shared:WaitForChild("IndeksPrzedmioty")) :: any
local okIk, Ikony = pcall(function()
	return require(Shared:WaitForChild("IkonyPrzedmiotow"))
end)
if not okIk or type(Ikony) ~= "table" then
	Ikony = {}
end

local Podpowiedz = require(script.Parent:WaitForChild("PodpowiedzPrzedmiotu"))

local CIEMNY = Color3.fromHex("4A2E1A")
local KREMOWY = Color3.fromHex("FCE3B0")
local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local FONT_MALY = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Bold)
local NAZWY_STOPNI = { start = "STARTER", las = "FOREST", bagno = "SWAMP", dzungla = "JUNGLE" }
local KOLOR_STOPNIA = { start = "B8C2CC", las = "6BD66B", bagno = "4FB3FF", dzungla = "FFC23D" }
local SLOTY = { Weapon = "Weapon", OffHand = "Off-hand", Helmet = "Helmet", Chest = "Chest", Gloves = "Gloves",
	Belt = "Belt", Boots = "Boots" }
local KOLEJNOSC_SLOTOW = { Weapon = 1, OffHand = 2, Helmet = 3, Chest = 4, Gloves = 5, Belt = 6, Boots = 7 }

local otwarte = false
local zakladka = "pets"
local danePetow: any = nil

------------------------------------------------------------------ drobne elementy
local function etykieta(rodzic: Instance, tekst: string, rozmiar: UDim2, poz: UDim2, kolor: Color3, maks: number,
	font: Font?, obrys: number?): TextLabel
	local t = Instance.new("TextLabel")
	t.BackgroundTransparency = 1
	t.Size, t.Position = rozmiar, poz
	t.Text = tekst
	t.TextColor3 = kolor
	t.FontFace = font or FONT
	t.TextScaled = true
	t.ZIndex = 8
	local c = Instance.new("UITextSizeConstraint")
	c.MaxTextSize = maks
	c.Parent = t
	if obrys then
		local s = Instance.new("UIStroke")
		s.Thickness = obrys
		s.Color = Color3.fromHex("1A1008")
		s.Parent = t
	end
	t.Parent = rodzic
	return t
end

local function naglowek(tekst: string, kolor: string, kolejnosc: number, dopisek: string?)
	local f = Instance.new("Frame")
	f.Name = "Section_" .. tekst
	f.Size = UDim2.new(1, 0, 0, 38)
	f.BackgroundColor3 = Color3.fromHex("8A5A32")
	f.LayoutOrder = kolejnosc
	f.ZIndex = 6
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0, 10)
	c.Parent = f
	local s = Instance.new("UIStroke")
	s.Thickness = 2
	s.Color = Color3.fromHex("3A2010")
	s.Parent = f
	local pasek = Instance.new("Frame")
	pasek.Size = UDim2.new(0, 10, 1, -10)
	pasek.Position = UDim2.new(0, 6, 0, 5)
	pasek.BackgroundColor3 = Color3.fromHex(kolor)
	pasek.ZIndex = 7
	local pc = Instance.new("UICorner")
	pc.CornerRadius = UDim.new(0, 4)
	pc.Parent = pasek
	pasek.Parent = f
	local t = etykieta(f, tekst, UDim2.new(0.6, 0, 0.78, 0), UDim2.new(0, 24, 0.11, 0), KREMOWY, 26, FONT, 2)
	t.TextXAlignment = Enum.TextXAlignment.Left
	if dopisek then
		local d = etykieta(f, dopisek, UDim2.new(0.38, -12, 0.6, 0), UDim2.new(0.62, 0, 0.2, 0), KREMOWY, 18, FONT_MALY)
		d.TextXAlignment = Enum.TextXAlignment.Right
	end
	f.Parent = lista
end

local function siatka(kolejnosc: number): Frame
	local f = Instance.new("Frame")
	f.Name = "Grid"
	f.BackgroundTransparency = 1
	f.Size = UDim2.new(1, 0, 0, 0)
	f.AutomaticSize = Enum.AutomaticSize.Y
	f.LayoutOrder = kolejnosc
	local g = Instance.new("UIGridLayout")
	g.CellSize = UDim2.new(0.155, 0, 0, 0)
	g.CellPadding = UDim2.new(0.014, 0, 0, 10)
	g.SortOrder = Enum.SortOrder.LayoutOrder
	g.HorizontalAlignment = Enum.HorizontalAlignment.Left
	g.Parent = f
	local function wysokosc()
		local szer = f.AbsoluteSize.X * 0.155
		g.CellSize = UDim2.new(0.155, 0, 0, math.floor(szer * 1.18))
	end
	f:GetPropertyChangedSignal("AbsoluteSize"):Connect(wysokosc)
	task.defer(wysokosc)
	f.Parent = lista
	return f
end

local function kafelek(rodzic: Frame, kolejnosc: number, ramka: Color3, tlo: Color3): (ImageButton, Frame)
	local b = Instance.new("ImageButton")
	b.BackgroundColor3 = tlo
	b.AutoButtonColor = false
	b.LayoutOrder = kolejnosc
	b.ZIndex = 6
	local c = Instance.new("UICorner")
	c.CornerRadius = UDim.new(0.12, 0)
	c.Parent = b
	local s = Instance.new("UIStroke")
	s.Thickness = 3
	s.Color = ramka
	s.ApplyStrokeMode = Enum.ApplyStrokeMode.Border
	s.Parent = b
	local okno = Instance.new("Frame")
	okno.Name = "Picture"
	okno.BackgroundTransparency = 1
	okno.Size = UDim2.new(0.86, 0, 0.66, 0)
	okno.Position = UDim2.new(0.07, 0, 0.05, 0)
	okno.ZIndex = 7
	okno.Parent = b
	b.Parent = rodzic
	return b, okno
end

------------------------------------------------------------------ podobizna peta
local function podobizna(rodzic: Frame, petId: string, mam: boolean)
	local v = Instance.new("ViewportFrame")
	v.BackgroundTransparency = 1
	v.Size = UDim2.fromScale(1, 1)
	v.Ambient = Color3.fromHex("C8C8C8")
	v.LightColor = Color3.new(1, 1, 1)
	v.ZIndex = 7
	if not mam then
		v.ImageColor3 = Color3.new(0, 0, 0) -- sylwetka niezdobytego peta
		v.ImageTransparency = 0.25
	end
	v.Parent = rodzic
	local k = workspace:FindFirstChild("PetyProba")
	local mod = k and k:FindFirstChild("Moduly")
	local rig = mod and mod:FindFirstChild("RigPetow")
	local dane = mod and mod:FindFirstChild("Rig_" .. petId, true)
	if not (rig and rig:IsA("ModuleScript") and dane and dane:IsA("ModuleScript")) then
		return
	end
	local ok, model = pcall(function()
		local R = require(rig) :: any
		return (R.zbuduj(require(dane), 1, "Indeks " .. petId))
	end)
	if not ok or typeof(model) ~= "Instance" then
		return
	end
	local m = model :: Model
	m.Parent = v
	local cf, rozmiar = m:GetBoundingBox()
	local przod, bok = m:GetPivot().LookVector, m:GetPivot().RightVector
	local cam = Instance.new("Camera")
	cam.FieldOfView = 30
	local odl = math.max(rozmiar.X, rozmiar.Y, rozmiar.Z) * 2.3
	cam.CFrame = CFrame.lookAt(cf.Position + (przod * 0.9 + bok * 0.45).Unit * odl + Vector3.new(0, rozmiar.Y * 0.2, 0), cf.Position)
	cam.Parent = v
	v.CurrentCamera = cam
end

------------------------------------------------------------------ rysowanie
local function wyczysc()
	for _, x in ipairs(lista:GetChildren()) do
		if x:IsA("GuiObject") then
			x:Destroy()
		end
	end
	lista.CanvasPosition = Vector2.zero
end

local function rysujPety()
	wyczysc()
	podpis.Text = "Hatch eggs in each land to collect pets"
	if not danePetow then
		postep.Text = "Loading..."
		return
	end
	if not danePetow.ok then
		postep.Text = danePetow.tekst or "Pets are not available yet"
		return
	end
	postep.Text = string.format("PETS COLLECTED %d / %d", danePetow.mam or 0, danePetow.wszystkich or 0)
	local n = 0
	for _, k in ipairs(danePetow.krainy) do
		local mam = 0
		for _, p in ipairs(k.pety) do
			if p.mam then
				mam += 1
			end
		end
		n += 1
		naglowek(k.nazwa, KOLOR_STOPNIA[k.id] or "6BD66B", n, string.format("%d / %d", mam, #k.pety))
		n += 1
		local g = siatka(n)
		for i, p in ipairs(k.pety) do
			local kolor = Color3.fromHex(p.kolor)
			local b, obraz = kafelek(g, i, if p.mam then kolor else Color3.fromHex("6A5040"),
				if p.mam then Color3.fromHex("FFF4DD") else Color3.fromHex("D9C3A0"))
			podobizna(obraz, p.id, p.mam)
			local nazwa = etykieta(b, if p.mam then p.nazwa else "???", UDim2.new(0.92, 0, 0.16, 0),
				UDim2.new(0.04, 0, 0.71, 0), CIEMNY, 16, FONT_MALY)
			nazwa.TextWrapped = true
			local r = etykieta(b, string.upper(p.rzadkoscNazwa), UDim2.new(0.92, 0, 0.11, 0), UDim2.new(0.04, 0, 0.86, 0),
				kolor, 13, FONT, 1)
			r.Name = "Rarity"
			b.MouseEnter:Connect(function()
				podpis.Text = (if p.mam then p.nazwa else "???") .. " — " .. p.rzadkoscNazwa .. ": " .. (p.skill or "")
			end)
		end
	end
end

local function klasaGracza(): string
	local k = player:GetAttribute("Class")
	return if type(k) == "string" and k ~= "" then k else "Warrior"
end

local function rysujPrzedmioty()
	wyczysc()
	local klasa = klasaGracza()
	podpis.Text = "Items for your class: " .. string.upper(klasa)
	local wg: { [string]: { any } } = {}
	local razem = 0
	for _, p in ipairs(Przedmioty.przedmioty) do
		if table.find(p.klasy, klasa) then
			wg[p.stopien] = wg[p.stopien] or {}
			table.insert(wg[p.stopien], p)
			razem += 1
		end
	end
	postep.Text = string.format("%s ITEMS: %d", string.upper(klasa), razem)
	local n = 0
	for _, s in ipairs(Przedmioty.stopnie) do
		local l = wg[s.id]
		if l and #l > 0 then
			table.sort(l, function(a, b)
				return (KOLEJNOSC_SLOTOW[a.slot] or 9) < (KOLEJNOSC_SLOTOW[b.slot] or 9)
			end)
			n += 1
			local poziomy = if s.poziom == s.poziomDo then "Lv " .. s.poziom else ("Lv " .. s.poziom .. "–" .. s.poziomDo)
			naglowek(NAZWY_STOPNI[s.id] or string.upper(s.nazwa), KOLOR_STOPNIA[s.id] or "B8C2CC", n, poziomy)
			n += 1
			local g = siatka(n)
			for i, p in ipairs(l) do
				local kolor = Color3.fromHex(KOLOR_STOPNIA[p.stopien] or "B8C2CC")
				local b, obraz = kafelek(g, i, kolor, Color3.fromHex("FFF4DD"))
				local ikona = (Ikony :: any)[p.id]
				if type(ikona) == "string" and ikona ~= "" then
					local im = Instance.new("ImageLabel")
					im.BackgroundTransparency = 1
					im.Size = UDim2.fromScale(1, 1)
					im.ScaleType = Enum.ScaleType.Fit
					im.Image = ikona
					im.ZIndex = 7
					im.Parent = obraz
				else
					local t = etykieta(obraz, p.nazwa, UDim2.fromScale(1, 1), UDim2.fromScale(0, 0), CIEMNY, 18, FONT_MALY)
					t.TextWrapped = true
				end
				local nazwa = etykieta(b, p.nazwa, UDim2.new(0.92, 0, 0.16, 0), UDim2.new(0.04, 0, 0.71, 0), CIEMNY, 14, FONT_MALY)
				nazwa.TextWrapped = true
				etykieta(b, (SLOTY[p.slot] or p.slot) .. " · Lv " .. tostring(p.poziom), UDim2.new(0.92, 0, 0.11, 0),
					UDim2.new(0.04, 0, 0.86, 0), Color3.fromHex("8A5A32"), 12, FONT_MALY)
				Podpowiedz.podepnij(b, function()
					return p.id, { cena = if p.cena and p.cena > 0 then p.cena else nil }
				end)
			end
		end
	end
end

local function rysuj()
	tabPets.Image = if zakladka == "pets" then OBRAZ_AKTYWNA else OBRAZ_ZWYKLA
	tabItems.Image = if zakladka == "items" then OBRAZ_AKTYWNA else OBRAZ_ZWYKLA
	if zakladka == "pets" then
		rysujPety()
	else
		rysujPrzedmioty()
	end
end

local function pobierzPety()
	local F = RS:FindFirstChild("OknoIndeksu") :: RemoteFunction?
	if not F then
		danePetow = { ok = false, tekst = "Pets are not available yet" }
		return
	end
	local ok, w = pcall(function()
		return (F :: RemoteFunction):InvokeServer("pety")
	end)
	if ok and type(w) == "table" and (w.ok or not danePetow) then
		danePetow = w
	end
end

------------------------------------------------------------------ zakładki, otwieranie i zamykanie
local function wybierz(z: string)
	if zakladka == z then
		return
	end
	zakladka = z
	rysuj()
end
tabPets.Activated:Connect(function()
	wybierz("pets")
end)
tabItems.Activated:Connect(function()
	wybierz("items")
end)

local function zamknij()
	if not otwarte then
		return
	end
	otwarte = false
	gui.Enabled = false
end

local function otworz()
	if otwarte then
		return
	end
	otwarte = true
	gui.Enabled = true
	rysuj()
	task.spawn(function()
		pobierzPety()
		if otwarte and zakladka == "pets" then
			rysuj()
		end
	end)
end

player:GetAttributeChangedSignal("Class"):Connect(function()
	if otwarte and zakladka == "items" then
		rysuj()
	end
end);

(panel:WaitForChild("CloseButton") :: ImageButton).Activated:Connect(zamknij);
(gui:WaitForChild("Backdrop") :: TextButton).Activated:Connect(zamknij)
UIS.InputBegan:Connect(function(wejscie, przetworzone)
	if otwarte and not przetworzone and wejscie.KeyCode == Enum.KeyCode.Escape then
		zamknij()
	end
end)

local hud = RS:WaitForChild("HUDButtonPressed", 120)
if hud and hud:IsA("BindableEvent") then
	hud.Event:Connect(function(nazwa)
		if nazwa == "Index" then
			if otwarte then
				zamknij()
			else
				otworz()
			end
		elseif otwarte then
			zamknij() -- inny przycisk HUD otwiera swoje okno
		end
	end)
end
