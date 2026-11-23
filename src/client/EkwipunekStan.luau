--!strict
--[[
	EkwipunekStan — wspólny stan ekwipunku gracza po stronie klienta (ModuleScript w StarterPlayerScripts.Client).
	Ten sam stan czytają okno ekwipunku (EquipmentPanelClient) i okno sklepu (ShopClient), więc sklep po lewej
	pokazuje dokładnie to samo co EQ: te same przedmioty w tych samych slotach i na tych samych miejscach plecaka.

	Stan (TEST, jak dotąd — tylko po stronie klienta, bez zapisu):
		Stan.equip[nazwaSlotu]            -- "Slot_Helmet" … "Slot_Weapon" -> id przedmiotu
		Stan.bag[kategoria][numer 1–25]   -- kategorie: Weapons, Armor, Amulets, Others
	Zakładka plecaka jest osobna w każdym oknie. Kto zmienia stan, woła Stan.zmieniono() — wtedy oba okna rysują się od nowa (Stan.Zmiana.Event).

	Przedmioty: Shared.Items (przedmioty testowe i bronie startowe) + przedmioty kowala Karola
	(swiat/kowal_proba, katalog swiat/postacie/sklep_przedmioty.json), które gracz posiada — dopisuje je
	Stan.zKowala(oferta) z oferty sklepu (SklepProba/Zdalne/Sklep "oferta"). Ikony przedmiotów kowala:
	Shared.IkonyPrzedmiotow (puste, dopóki ikony z Blendera nie są wgrane) — bez ikony okna rysują kolorowy
	kafelek stopnia z nazwą.

	Projekt: B&C/UI/Okno ekwipunku.md, B&C/UI/Sklepy i bronie startowe — prompty.md.
]]

local RS = game:GetService("ReplicatedStorage")

local Items = require(RS:WaitForChild("Shared"):WaitForChild("Items"))
local okIkony, Ikony = pcall(function()
	return require(RS:WaitForChild("Shared"):WaitForChild("IkonyPrzedmiotow"))
end)
if not okIkony then
	Ikony = {}
end

export type Definicja = {
	name: string,
	slot: string,
	category: string,
	icon: string,
	stopien: string?,
	kolor: Color3?,
	poziom: number?, -- poziom ulepszenia u kowala (+N)
	kowal: boolean?,
}

local Stan = {}

Stan.KATEGORIE = { "Weapons", "Armor", "Amulets", "Others" }
Stan.ROZMIAR_PLECAKA = 25

Stan.equip = {} :: { [string]: string }
Stan.bag = { Weapons = {}, Armor = {}, Amulets = {}, Others = {} } :: { [string]: { [number]: string } }

local zmiana = Instance.new("BindableEvent")
Stan.Zmiana = zmiana

-- kolory stopni jak w sklepie Karola (swiat/sklep_proba/ustawienia.json, kolory_stopni)
local KOLORY_STOPNI = {
	start = Color3.fromHex("9AA3B5"),
	las = Color3.fromHex("5FB85A"),
	bagno = Color3.fromHex("4FA39A"),
	dzungla = Color3.fromHex("E0A030"),
}
Stan.KOLORY_STOPNI = KOLORY_STOPNI

-- przedmioty kowala, które gracz posiada: id -> definicja
local zKowala: { [string]: Definicja } = {}

function Stan.definicja(id: string?): Definicja?
	if id == nil then
		return nil
	end
	local i = (Items :: any)[id]
	if i then
		return i
	end
	return zKowala[id]
end

function Stan.kategoriaSlotu(slot: string): string
	if slot == "Weapon" or slot == "OffHand" then
		return "Weapons"
	elseif slot == "Amulet" or slot == "Ring" or slot == "Trinket" then
		return "Amulets"
	end
	return "Armor"
end

function Stan.zmieniono()
	zmiana:Fire()
end

--[[
	Rysuje przedmiot w ikonie slotu (ImageLabel „Icon” w slocie EQ albo sklepu). Bez ikony w Roblox: kolorowy
	kafelek stopnia z nazwą (dziecko „Kafelek”). Poziom ulepszenia u kowala > 0: plakietka „+N” (dziecko „Plus”).
]]
local CZCIONKA = Font.new("rbxasset://fonts/families/LuckiestGuy.json")

local function napis(rodzic: Instance, nazwa: string, tekst: string, rozmiar: UDim2, pozycja: UDim2, z: number): TextLabel
	local t = rodzic:FindFirstChild(nazwa) :: TextLabel?
	if not t then
		local n = Instance.new("TextLabel")
		n.Name = nazwa
		n.BackgroundTransparency = 1
		n.FontFace = CZCIONKA
		n.TextScaled = true
		n.TextColor3 = Color3.new(1, 1, 1)
		n.TextWrapped = true
		local s = Instance.new("UIStroke")
		s.Color = Color3.fromRGB(26, 20, 16)
		s.Thickness = 1.5
		s.Parent = n
		n.Parent = rodzic
		t = n
	end
	local l = t :: TextLabel
	l.Text = tekst
	l.Size = rozmiar
	l.Position = pozycja
	l.ZIndex = z
	return l
end

function Stan.rysujIkone(icon: ImageLabel, id: string?)
	Stan.rysujDefinicje(icon, Stan.definicja(id))
end

-- to samo z gotowej definicji (sklep rysuje tak towar, którego gracz jeszcze nie ma)
function Stan.rysujDefinicje(icon: ImageLabel, d: Definicja?)
	icon.Image = d and d.icon or ""
	local kafelek = icon:FindFirstChild("Kafelek") :: Frame?
	local bezIkony = d ~= nil and d.icon == ""
	if bezIkony and d then
		if not kafelek then
			local k = Instance.new("Frame")
			k.Name = "Kafelek"
			k.Size = UDim2.fromScale(1, 1)
			k.BorderSizePixel = 0
			local c = Instance.new("UICorner")
			c.CornerRadius = UDim.new(0.18, 0)
			c.Parent = k
			local s = Instance.new("UIStroke")
			s.Color = Color3.fromRGB(26, 20, 16)
			s.Thickness = 2
			s.Parent = k
			k.Parent = icon
			kafelek = k
		end
		local k = kafelek :: Frame
		k.Visible = true
		k.ZIndex = icon.ZIndex
		k.BackgroundColor3 = d.kolor or Color3.fromRGB(154, 163, 181)
		napis(k, "Nazwa", d.name, UDim2.fromScale(0.92, 0.8), UDim2.fromScale(0.04, 0.1), icon.ZIndex + 1)
	elseif kafelek then
		kafelek.Visible = false
	end
	local plus = d and d.poziom and d.poziom > 0
	local p = icon:FindFirstChild("Plus") :: TextLabel?
	if plus and d then
		local l = napis(icon, "Plus", "+" .. tostring(d.poziom), UDim2.fromScale(0.5, 0.34), UDim2.fromScale(0.52, -0.04), icon.ZIndex + 2)
		l.TextColor3 = Color3.fromRGB(255, 214, 90)
		l.TextXAlignment = Enum.TextXAlignment.Right
		l.Visible = true
	elseif p then
		p.Visible = false
	end
end

-- odkłada przedmiot na stronę plecaka jego kategorii (preferowany numer slotu albo pierwszy wolny)
function Stan.doPlecaka(id: string, prefer: number?): number?
	local d = Stan.definicja(id)
	if not d then
		return nil
	end
	local page = Stan.bag[d.category]
	if prefer and page[prefer] == nil then
		page[prefer] = id
		return prefer
	end
	for i = 1, Stan.ROZMIAR_PLECAKA do
		if page[i] == nil then
			page[i] = id
			return i
		end
	end
	return nil
end

local function gdzieJest(id: string): (string?, string?, number?)
	for slot, v in pairs(Stan.equip) do
		if v == id then
			return "equip", slot, nil
		end
	end
	for kat, page in pairs(Stan.bag) do
		for i, v in pairs(page) do
			if v == id then
				return "bag", kat, i
			end
		end
	end
	return nil
end
Stan.gdzieJest = gdzieJest

local function wyjmij(id: string)
	local gdzie, a, b = gdzieJest(id)
	if gdzie == "equip" and a then
		Stan.equip[a] = nil
	elseif gdzie == "bag" and a and b then
		Stan.bag[a][b] = nil
	end
end

--[[
	Przedmioty kowala z oferty sklepu: wiersz { id, nazwa, slot, stopien, cena, stan, ulepszenie, … },
	stan = kup | za_drogie | za_niski_poziom | masz | zalozone. Posiadane (masz, zalozone) trafiają do ekwipunku:
	założone — do swojego slotu (to, co tam leżało, idzie do plecaka), posiadane — do plecaka swojej kategorii.
	Pomijamy broń z zestawu podstawowego (cena 0): w EQ jest już broń startowa klasy (Shared.Items, Paweł 18.11).
]]
function Stan.zKowala(oferta: { any })
	local zmienione = false
	for _, w in ipairs(oferta) do
		if type(w) ~= "table" or type(w.id) ~= "string" or type(w.slot) ~= "string" then
			continue
		end
		local posiada = w.stan == "masz" or w.stan == "zalozone"
		if not posiada or (w.slot == "Weapon" and (w.cena or 0) == 0) then
			continue
		end
		local stary = zKowala[w.id]
		local def: Definicja = {
			name = tostring(w.nazwa or w.id),
			slot = w.slot,
			category = Stan.kategoriaSlotu(w.slot),
			icon = (Ikony :: any)[w.id] or "",
			stopien = w.stopien,
			kolor = KOLORY_STOPNI[w.stopien or ""] or KOLORY_STOPNI.start,
			poziom = tonumber(w.ulepszenie) or 0,
			kowal = true,
		}
		zKowala[w.id] = def
		if not stary or stary.poziom ~= def.poziom then
			zmienione = true
		end
		local gdzie, a = gdzieJest(w.id)
		local slotEq = "Slot_" .. w.slot
		if w.stan == "zalozone" then
			if not (gdzie == "equip" and a == slotEq) then
				wyjmij(w.id)
				local tam = Stan.equip[slotEq]
				Stan.equip[slotEq] = w.id
				if tam then
					Stan.doPlecaka(tam)
				end
				zmienione = true
			end
		elseif gdzie == nil then
			Stan.doPlecaka(w.id)
			zmienione = true
		end
	end
	if zmienione then
		Stan.zmieniono()
	end
end

return Stan
