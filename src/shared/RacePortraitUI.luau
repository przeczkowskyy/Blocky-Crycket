--!strict
-- Ramka portretu z portretem rasy gracza (Paweł 23.11: „wygenerujemy ramki od razu z portretami, z miejscem na
-- pasek z expem, usuwamy totalnie stare i wgrywamy w miejsce nowe”). Grafiki RaceFrame<Id> (Shared.RacePortraits,
-- tools/raceportraits_assets.py): złota ramka jak PlayerFrame, portret rasy w środku, pusty tor paska na dole.
-- - HUD: podmiana obrazka samej ramki (PlayerPanel.FrameArt) — stara ramka znika, bez rasy wraca.
-- - Okno ekwipunku i sklepy: stara ramka jest wymazana z tła okna (tools/wymaz_stare_ramki.py, tools/sklep_okno.py),
--   nowa leży dokładnie w jej prostokącie (ułamki rodzica, zmierzone na grafice tła).
-- Pasek, poziom i znaczki zostają nad ramką (`nad`). Obraz zależy od atrybutu gracza "Race" (D-079).
-- Tylko klient (LocalPlayer).

local Players = game:GetService("Players")

local RacePortraits = require(script.Parent:WaitForChild("RacePortraits"))

local RacePortraitUI = {}

local PUSTA_RAMKA = "rbxassetid://128244393062229" -- PlayerFrame (assets/processed/PlayerFrame.png), pusta ramka HUD

export type Opcje = {
	podmien: ImageLabel?, -- obrazek ramki do podmiany (HUD)
	rodzic: GuiObject?, -- gdzie położyć nową ramkę (okna z ramką wypaloną w tle)
	prostokat: { number }?, -- {x, y, szerokość, wysokość} w ułamkach rodzica — miejsce starej ramki
	zindex: number?,
	nad: { GuiObject }?, -- elementy, które muszą zostać NAD ramką (pasek, poziom, znaczek klasy)
	zastepstwo: GuiObject?, -- chowane, gdy ramka rasy jest widoczna (np. emblemat klasy w sklepie)
	uklad: { { obj: GuiObject, rect: { number } } }?, -- przy ramce rasy: nowe {x, y, w, h} (ułamki rodzica), bez rasy powrót
	wylacz: { Instance }?, -- przy ramce rasy wyłączone (np. UIStroke paska — tor w ramce ma własny brzeg)
	-- pasek i napis według toru wybranej rasy (RacePortraits.Tor, z Figmy): ramka = {x, y, w, h} obrazka ramki
	-- w ułamkach rodzica obiektu, wnetrze = część prostokąta paska (np. napis {0.03, 0.2, 0.94, 0.75}; domyślnie cały)
	pasek: { { obj: GuiObject, ramka: { number }, wnetrze: { number }? } }?,
}

local function idRasy(player: Player): string?
	local race = player:GetAttribute("Race")
	local id = if typeof(race) == "string" then (RacePortraits :: any)[race] else nil
	if typeof(id) == "string" and id ~= "rbxassetid://0" then
		return id
	end
	return nil
end

function RacePortraitUI.attach(opcje: Opcje): ImageLabel?
	local o = opcje
	local player = Players.LocalPlayer
	local img: ImageLabel? = nil
	local oryginal: string? = nil

	if o.podmien then
		img = o.podmien
		oryginal = (o.podmien :: ImageLabel).Image
	elseif o.rodzic and o.prostokat then
		local r = o.prostokat :: { number }
		local nazwa = "RaceFrame"
		local stara = (o.rodzic :: GuiObject):FindFirstChild(nazwa)
		if stara then
			stara:Destroy()
		end
		local i = Instance.new("ImageLabel")
		i.Name = nazwa
		i.BackgroundTransparency = 1
		i.BorderSizePixel = 0
		i.ScaleType = Enum.ScaleType.Stretch
		i.Position = UDim2.fromScale(r[1], r[2])
		i.Size = UDim2.fromScale(r[3], r[4])
		i.ZIndex = o.zindex or 2
		i.Parent = o.rodzic
		img = i
	end
	if not img then
		return nil
	end
	local obraz = img :: ImageLabel
	for k, g in ipairs(o.nad or {}) do
		if g and g.ZIndex <= obraz.ZIndex then
			g.ZIndex = obraz.ZIndex + k
		end
	end

	local stareUklady = {}
	for _, u in ipairs(o.uklad or {}) do
		stareUklady[u.obj] = { u.obj.Position, u.obj.Size }
	end
	for _, u in ipairs(o.pasek or {}) do
		stareUklady[u.obj] = { u.obj.Position, u.obj.Size }
	end
	local tory = (RacePortraits :: any).Tor or {}

	local function odswiez()
		local id = idRasy(player)
		for _, w in ipairs(o.wylacz or {}) do
			(w :: any).Enabled = id == nil
		end
		local tor = id and tory[player:GetAttribute("Race")]
		for _, u in ipairs(o.pasek or {}) do
			if tor then
				local f, w = u.ramka, u.wnetrze or { 0, 0, 1, 1 }
				local bx, by, bw, bh = f[1] + f[3] * tor[1], f[2] + f[4] * tor[2], f[3] * tor[3], f[4] * tor[4]
				u.obj.Position = UDim2.fromScale(bx + bw * w[1], by + bh * w[2])
				u.obj.Size = UDim2.fromScale(bw * w[3], bh * w[4])
			else
				u.obj.Position, u.obj.Size = stareUklady[u.obj][1], stareUklady[u.obj][2]
			end
		end
		for _, u in ipairs(o.uklad or {}) do
			if id then
				u.obj.Position = UDim2.fromScale(u.rect[1], u.rect[2])
				u.obj.Size = UDim2.fromScale(u.rect[3], u.rect[4])
			else
				u.obj.Position, u.obj.Size = stareUklady[u.obj][1], stareUklady[u.obj][2]
			end
		end
		if oryginal ~= nil then
			obraz.Image = id or oryginal -- HUD: bez rasy stara ramka
		else
			obraz.Image = id or PUSTA_RAMKA -- stara ramka jest wymazana z tła, więc bez rasy pusta ramka z HUD
		end
		if o.zastepstwo then
			o.zastepstwo.Visible = id == nil
		end
	end
	player:GetAttributeChangedSignal("Race"):Connect(odswiez)
	odswiez()
	return obraz
end

return RacePortraitUI
