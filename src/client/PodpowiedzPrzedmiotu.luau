--!strict
--[[
	PodpowiedzPrzedmiotu — wspólna podpowiedź przy najechaniu na przedmiot (Paweł 26.11) w oknie Index, ekwipunku
	i sklepie. Tło: ta sama tabliczka co podpowiedź peta (PodpowiedzPeta), rozciągana w pionie (Slice).
	Pokazuje: nazwę, rzadkość i krainę (stopień), statystyki przedmiotu, wymagany poziom, a w sklepie cenę z rybką.

	Statystyki: katalog Karola (Shared.IndeksPrzedmioty: baza + poziom ulepszenia × krok — ten sam wzór co kowal).
	Przedmioty spoza katalogu (testowe, startowe z Shared.Items) pokazują samą nazwę.

	Porównanie (przycisk COMPARE w sklepie i ekwipunku): gdy włączone, przy każdej statystyce widać różnicę względem
	przedmiotu założonego w tym samym slocie — zielone +N, czerwone −N, szare 0.

	API:
		P.podepnij(gui, () -> (id?, opcje?))   -- najechanie na gui pokazuje podpowiedź przedmiotu zwróconego przez funkcję
			opcje = { cena: number?, ulepszenie: number?, zalozony: boolean? }
		P.pokaz(id, opcje?), P.schowaj()
		P.porownanie: boolean, P.ustawPorownanie(bool), P.Zmiana (BindableEvent: przełączono porównanie)
		P.staty(id, ulepszenie?) -> { [stat]: number }
		P.podepnijUmiejetnosc(gui, () -> info?), P.pokazUmiejetnosc(info) -- umiejętności (zakładka SKILLS, pas slotów)
]]
local Players = game:GetService("Players")
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local TextService = game:GetService("TextService")

local Dane = require(RS:WaitForChild("Shared"):WaitForChild("IndeksPrzedmioty")) :: any
local Stan = require(script.Parent:WaitForChild("EkwipunekStan")) :: any

local P = {}
P.porownanie = false
local zmiana = Instance.new("BindableEvent")
P.Zmiana = zmiana

local FONT = Font.new("rbxasset://fonts/families/LuckiestGuy.json")
local FONT_MALY = Font.new("rbxasset://fonts/families/GothamSSm.json", Enum.FontWeight.Bold)
local KREMOWY = Color3.fromHex("FCE3B0")
local NAZWY_STOPNI = { start = "STARTER", las = "FOREST", bagno = "SWAMP", dzungla = "JUNGLE" }
local SLOT_EQ = { Weapon = "Slot_Weapon", OffHand = "Slot_OffHand", Helmet = "Slot_Helmet", Chest = "Slot_Chest",
	Gloves = "Slot_Gloves", Belt = "Slot_Belt", Boots = "Slot_Boots" }
local SZER, LINIA = 300, 22

local wgId: { [string]: any } = {}
for _, p in ipairs(Dane.przedmioty) do
	wgId[p.id] = p
end

------------------------------------------------------------------ GUI (budowane raz)
local gui = Instance.new("ScreenGui")
gui.Name = "PodpowiedzPrzedmiotu"
gui.DisplayOrder = 90
gui.IgnoreGuiInset = true
gui.ResetOnSpawn = false
gui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling

local ramka = Instance.new("ImageLabel")
ramka.Name = "Tooltip"
ramka.BackgroundTransparency = 1
ramka.Image = Dane.obrazy.podpowiedz
ramka.ScaleType = Enum.ScaleType.Slice
ramka.SliceCenter = Rect.new(70, 70, 442, 234)
ramka.SliceScale = 0.55
ramka.Visible = false
ramka.Parent = gui
local skala = Instance.new("UIScale")
skala.Parent = ramka

local function etykieta(nazwa: string, font: Font, rozmiar: number, kolor: Color3, obrys: number?): TextLabel
	local t = Instance.new("TextLabel")
	t.Name = nazwa
	t.BackgroundTransparency = 1
	t.FontFace = font
	t.TextSize = rozmiar
	t.TextColor3 = kolor
	t.TextXAlignment = Enum.TextXAlignment.Left
	t.ZIndex = 2
	if obrys then
		local s = Instance.new("UIStroke")
		s.Thickness = obrys
		s.Color = Color3.fromHex("1A1008")
		s.Parent = t
	end
	t.Parent = ramka
	return t
end

local tNazwa = etykieta("ItemName", FONT, 24, Color3.new(1, 1, 1), 2)
tNazwa.TextWrapped = true
local tRzadkosc = etykieta("Rarity", FONT, 16, Color3.new(1, 1, 1), 1.5)
local wiersze: { TextLabel } = {}
local tWymog = etykieta("Req", FONT_MALY, 14, KREMOWY)
local cena = Instance.new("Frame")
cena.Name = "Price"
cena.BackgroundTransparency = 1
cena.ZIndex = 2
cena.Parent = ramka
local rybka = Instance.new("ImageLabel")
rybka.BackgroundTransparency = 1
rybka.Image = Dane.obrazy.rybka
rybka.ScaleType = Enum.ScaleType.Fit
rybka.Size = UDim2.fromOffset(28, 28)
rybka.ZIndex = 3
rybka.Parent = cena
local tCena = etykieta("Amount", FONT, 22, Color3.fromHex("FFD65A"), 2)
tCena.Parent = cena
tCena.Position = UDim2.fromOffset(34, 0)
tCena.Size = UDim2.fromOffset(200, 28)

local function wiersz(i: number): TextLabel
	local w = wiersze[i]
	if not w then
		w = etykieta("Stat" .. i, FONT_MALY, 16, KREMOWY)
		w.RichText = true
		wiersze[i] = w
	end
	return w
end

------------------------------------------------------------------ statystyki
function P.staty(id: string?, ulepszenie: number?): { [string]: number }
	local w: { [string]: number } = {}
	local p = id and wgId[id]
	if not p then
		return w
	end
	local lvl = ulepszenie or 0
	for _, s in ipairs(Dane.statystyki) do
		local v = (p.baza[s.id] or 0) + lvl * (p.krok[s.id] or 0)
		if v ~= 0 then
			w[s.id] = v
		end
	end
	return w
end

local function ulepszenieZeStanu(id: string?): number
	local d = id and Stan.definicja(id)
	return if d and type(d.poziom) == "number" then d.poziom else 0
end

local function liczba(v: number, stat: string): string
	if stat == "tarcza" then
		return string.format("%d%%", math.floor(v * 100 + 0.5))
	end
	return if v == math.floor(v) then tostring(v) else string.format("%.1f", v)
end

------------------------------------------------------------------ pokazywanie
local aktywny: GuiObject? = nil

local function ustawPozycje()
	if not ramka.Visible then
		return
	end
	local m = UIS:GetMouseLocation()
	local ekran = gui.AbsoluteSize
	local w, h = ramka.AbsoluteSize.X, ramka.AbsoluteSize.Y
	local x = m.X + 24
	local y = m.Y - h * 0.3
	if x + w > ekran.X - 8 then
		x = m.X - w - 24
	end
	y = math.clamp(y, 8, math.max(8, ekran.Y - h - 8))
	ramka.Position = UDim2.fromOffset(x, y)
end

function P.pokaz(id: string?, opcje: any?)
	if not id then
		P.schowaj()
		return
	end
	opcje = opcje or {}
	local p = wgId[id]
	local d = Stan.definicja(id)
	local ulep = opcje.ulepszenie or ulepszenieZeStanu(id)
	tNazwa.Text = (if p then p.nazwa elseif d then d.name else id) .. (if ulep > 0 then "  +" .. ulep else "")
	local stopien = p and p.stopien or (d and d.stopien) or nil
	tRzadkosc.Text = "COMMON" .. (if stopien and NAZWY_STOPNI[stopien] then " · " .. NAZWY_STOPNI[stopien] else "")
	tRzadkosc.TextColor3 = (stopien and Stan.KOLORY_STOPNI[stopien]) or Color3.fromHex("B8C2CC")

	-- porównanie z założonym w tym samym slocie
	local porownaj: { [string]: number }? = nil
	local zalozonyId: string? = nil
	if P.porownanie and p and not opcje.zalozony then
		zalozonyId = Stan.equip[SLOT_EQ[p.slot] or ""]
		if zalozonyId and zalozonyId ~= id then
			porownaj = P.staty(zalozonyId, ulepszenieZeStanu(zalozonyId))
		end
	end
	local moje = P.staty(id, ulep)
	local n = 0
	for _, s in ipairs(Dane.statystyki) do
		local v = moje[s.id] or 0
		local inny = if porownaj then (porownaj[s.id] or 0) else nil
		if v ~= 0 or (inny and inny ~= 0) then
			n += 1
			local t = wiersz(n)
			local tekst = s.nazwa .. "  <b>" .. liczba(v, s.id) .. "</b>"
			if inny then
				local r = v - inny
				if r > 0 then
					tekst ..= '  <font color="#6BE36B">(+' .. liczba(r, s.id) .. ")</font>"
				elseif r < 0 then
					tekst ..= '  <font color="#FF6B5A">(−' .. liczba(-r, s.id) .. ")</font>"
				else
					tekst ..= '  <font color="#9AA3B5">(0)</font>'
				end
			end
			t.Text = tekst
			t.Visible = true
		end
	end
	if n == 0 and p then
		n = 1
		local t = wiersz(1)
		t.Text = "No bonus stats"
		t.Visible = true
	end
	for i = n + 1, #wiersze do
		wiersze[i].Visible = false
	end
	-- układ
	local y = 26
	-- długa nazwa łamie się na dwie (albo więcej) linie zamiast ucinać się
	local wys = TextService:GetTextSize(tNazwa.Text, tNazwa.TextSize, Enum.Font.LuckiestGuy, Vector2.new(SZER - 52, 1000)).Y
	wys = math.max(28, wys + 2)
	tNazwa.Position = UDim2.fromOffset(26, y)
	tNazwa.Size = UDim2.fromOffset(SZER - 52, wys)
	y += wys + 2
	tRzadkosc.Position = UDim2.fromOffset(26, y)
	tRzadkosc.Size = UDim2.fromOffset(SZER - 52, 18)
	y += 26
	for i = 1, n do
		wiersze[i].Position = UDim2.fromOffset(30, y)
		wiersze[i].Size = UDim2.fromOffset(SZER - 56, LINIA)
		y += LINIA
	end
	if porownaj and zalozonyId then
		local zd = wgId[zalozonyId]
		tWymog.Text = "vs equipped: " .. (if zd then zd.nazwa else zalozonyId)
	elseif p then
		tWymog.Text = "Requires level " .. tostring(p.poziom)
	else
		tWymog.Text = ""
	end
	y += 6
	tWymog.Position = UDim2.fromOffset(26, y)
	tWymog.Size = UDim2.fromOffset(SZER - 52, 18)
	y += 20
	if opcje.cena and opcje.cena > 0 then
		cena.Visible = true
		tCena.Text = tostring(opcje.cena)
		cena.Position = UDim2.fromOffset(26, y + 2)
		cena.Size = UDim2.fromOffset(SZER - 52, 28)
		y += 34
	else
		cena.Visible = false
	end
	ramka.Size = UDim2.fromOffset(SZER, y + 22)
	skala.Scale = math.clamp(gui.AbsoluteSize.Y / 900, 0.7, 1.25)
	ramka.Visible = true
	ustawPozycje()
end

-- Paweł 26.11: podpowiedź umiejętności z zakładki SKILLS i pasa slotów — co robi, ile many kosztuje, obrażenia
-- info = { nazwa, rodzaj = "ACTIVE"|"PASSIVE", mana, opis = { linie }, drzewko = "…", stopka = "…" }
function P.pokazUmiejetnosc(info: any)
	if not info then
		P.schowaj()
		return
	end
	tNazwa.Text = info.nazwa or "?"
	local mana = tonumber(info.mana) or 0
	tRzadkosc.Text = (info.rodzaj or "SKILL") .. (if mana > 0 then " · " .. mana .. " MANA" else "")
	tRzadkosc.TextColor3 = if info.rodzaj == "PASSIVE" then Color3.fromHex("9FD7FF") else Color3.fromHex("FFB347")
	local linie = table.clone(info.opis or {})
	if info.drzewko and info.drzewko ~= "" then
		table.insert(linie, info.drzewko)
	end
	for i, l in ipairs(linie) do
		local t = wiersz(i)
		t.Text = l
		t.Visible = true
	end
	for i = #linie + 1, #wiersze do
		wiersze[i].Visible = false
	end
	local y = 26
	local wys = TextService:GetTextSize(tNazwa.Text, tNazwa.TextSize, Enum.Font.LuckiestGuy, Vector2.new(SZER - 52, 1000)).Y
	wys = math.max(28, wys + 2)
	tNazwa.Position = UDim2.fromOffset(26, y)
	tNazwa.Size = UDim2.fromOffset(SZER - 52, wys)
	y += wys + 2
	tRzadkosc.Position = UDim2.fromOffset(26, y)
	tRzadkosc.Size = UDim2.fromOffset(SZER - 52, 18)
	y += 26
	for i = 1, #linie do
		local t = wiersze[i]
		local h = TextService:GetTextSize(t.Text, t.TextSize, Enum.Font.GothamBold, Vector2.new(SZER - 56, 1000)).Y
		t.TextWrapped = true
		t.Position = UDim2.fromOffset(30, y)
		t.Size = UDim2.fromOffset(SZER - 56, math.max(LINIA, h + 4))
		y += math.max(LINIA, h + 4)
	end
	tWymog.Text = info.stopka or ""
	y += 6
	tWymog.Position = UDim2.fromOffset(26, y)
	tWymog.Size = UDim2.fromOffset(SZER - 52, 18)
	y += 20
	cena.Visible = false
	ramka.Size = UDim2.fromOffset(SZER, y + 22)
	skala.Scale = math.clamp(gui.AbsoluteSize.Y / 900, 0.7, 1.25)
	ramka.Visible = true
	ustawPozycje()
end

function P.podepnijUmiejetnosc(obiekt: GuiObject, dane: () -> any)
	obiekt.MouseEnter:Connect(function()
		local info = dane()
		if info then
			aktywny = obiekt
			P.pokazUmiejetnosc(info)
		end
	end)
	obiekt.MouseLeave:Connect(function()
		if aktywny == obiekt then
			P.schowaj()
		end
	end)
end

function P.schowaj()
	ramka.Visible = false
	aktywny = nil
end

function P.podepnij(obiekt: GuiObject, dane: () -> (string?, any?))
	obiekt.MouseEnter:Connect(function()
		local id, opcje = dane()
		if id then
			aktywny = obiekt
			P.pokaz(id, opcje)
		end
	end)
	obiekt.MouseLeave:Connect(function()
		if aktywny == obiekt then
			P.schowaj()
		end
	end)
	obiekt.AncestryChanged:Connect(function()
		if aktywny == obiekt and not obiekt:IsDescendantOf(game) then
			P.schowaj()
		end
	end)
end

function P.ustawPorownanie(wl: boolean)
	P.porownanie = wl
	zmiana:Fire(wl)
end

RunService.RenderStepped:Connect(function()
	if ramka.Visible then
		ustawPozycje()
		-- okno, w którym był obiekt, zamknięte -> chowamy
		if aktywny then
			local sg = aktywny:FindFirstAncestorWhichIsA("ScreenGui")
			if not aktywny.Visible or (sg and not sg.Enabled) then
				P.schowaj()
			end
		end
	end
end)

gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")

return P
