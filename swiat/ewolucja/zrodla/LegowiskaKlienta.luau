--[[
	LegowiskaKlienta — legowiska graczy w świecie po stronie klienta: cokoły z trofeami (smoki zdobytych stadiów w pozie
	„cokol”, zestaw blender; dawne modele w zestawach smok / potwory), tabliczki poziomów, gniazdo z jajem, kopiec skarbu
	w trzech rozmiarach (rekwizyty z modele/dane). Budowane tylko w zasięgu kamery gracza; przebudowa przy zmianie stanu.
]]
local Lg = {}
Lg.__index = Lg

local function lista(p: Player, n: string): { string }
	local w = {}
	for x in string.gmatch((p:GetAttribute(n) or "") .. ",", "([^,]*),") do
		table.insert(w, x)
	end
	return w
end

function Lg.nowe(c)
	-- c: D, L, C, NF, lokalne, gracz, Players, wzorce, SK (albo nil), wariantD, wyglad, czcionka, tusz, zloto, UI, nowy, hex, mojaPoz()
	local self = setmetatable({}, Lg)
	self.c = c
	self.leg = {}
	self.doKroku = 0
	return self
end

function Lg:czesc3(roz: Vector3, cf: CFrame, kolor: Color3, mat: Enum.Material, ksztalt: Enum.PartType?, rodzic: Instance): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.CanCollide = false
	p.CanQuery = false
	p.CanTouch = false
	p.CastShadow = false
	p.Size = roz
	p.CFrame = cf
	p.Color = kolor
	p.Material = mat
	if ksztalt then
		p.Shape = ksztalt
	end
	p.Parent = rodzic
	return p
end

function Lg:napis(rodzic: BasePart, tekst: string, kolor: Color3)
	local c = self.c
	local sg = Instance.new("SurfaceGui")
	sg.Face = Enum.NormalId.Top
	sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 40
	sg.LightInfluence = 0
	sg.Parent = rodzic
	local l = Instance.new("TextLabel")
	l.BackgroundTransparency = 1
	l.Size = UDim2.fromScale(1, 1)
	l.Text = tekst
	l.TextScaled = true
	l.Font = c.czcionka
	l.TextColor3 = kolor
	l.Parent = sg
	c.nowy("UIStroke", { Thickness = 2, Color = c.tusz }, l)
end

-- trofeum dawnego modelu (zestawy smok / potwory): klon, skala, sylwetka niezdobytych
function Lg:trofeumStare(F, W0, cf: CFrame, ciemny: boolean, rodzic: Instance)
	local c = self.c
	local wz = c.wzorce and c.wzorce:FindFirstChild(F.wzorzec)
	if not wz then
		return
	end
	local m = wz:Clone()
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CanCollide = false
			d.CanQuery = false
			d.CanTouch = false
			d.CastShadow = false
			if ciemny then
				d.Color = Color3.fromRGB(20, 16, 24)
				d.Material = Enum.Material.SmoothPlastic
			end
		end
	end
	if not ciemny then
		c.wyglad(m, W0)
	end
	pcall(function()
		m:ScaleTo(1.4 / F.model_r)
	end)
	m:PivotTo(cf)
	m.Parent = rodzic
end

function Lg:zbuduj(p: Player, slot: number, sig: string)
	local c = self.c
	local D, C = c.D, c.C
	local f0 = Instance.new("Folder")
	f0.Name = "Legowisko" .. slot
	f0.Parent = c.lokalne
	local moj = p == c.gracz
	local mf = p:GetAttribute("EW_MaxForma") or 1
	if moj then
		c.gracz:SetAttribute("EW_K_TrofeaLinia", p:GetAttribute("EW_Linia") or 1)
	end
	local war, tro = lista(p, "EW_Warianty"), lista(p, "EW_Trofea")
	local lx, lz = c.L.legowiskoPoz(D, slot)
	local SK = c.SK
	local cokoly = SK and c.wzorce and c.wzorce:FindFirstChild("Rekwizyt_cokol")
	for f = 1, c.NF do
		local a = (f - 1) * math.pi * 2 / c.NF
		local px, pz = lx + math.sin(a) * 8.5, lz + math.cos(a) * 8.5
		local F = D.formy[f]
		local obrot = CFrame.Angles(0, math.atan2(px - lx, pz - lz) + math.pi, 0)
		local gora = CFrame.new(C + Vector3.new(px, 1.25, pz)) * obrot
		if cokoly then
			local m = SK:rekwizyt("Rekwizyt_cokol", CFrame.new(C + Vector3.new(px, 0, pz)) * obrot, 0.62, f0)
			local at = m and m:FindFirstChild("TrofeumAttachment", true)
			if at then
				gora = CFrame.new(at.WorldPosition) * obrot
			end
		end
		if f <= mf or moj then
			if F.rig and SK then
				SK:trofeum(F, c.wariantD(war[f]), gora, 1.6, f0, f > mf, p:GetAttribute("EW_Linia") or 1)
			else
				self:trofeumStare(F, c.wariantD(war[f]), gora, f > mf, f0)
			end
		end
		if moj and f <= mf then
			local tab = self:czesc3(Vector3.new(2.6, 0.12, 1.1), CFrame.new(C + Vector3.new(lx + math.sin(a) * 11.4, 0.3, lz + math.cos(a) * 11.4))
				* CFrame.Angles(0, a, 0), c.tusz, Enum.Material.SmoothPlastic, nil, f0)
			self:napis(tab, string.format(c.UI.poziom, tonumber(tro[f]) or 1), c.zloto)
		end
	end
	if moj then
		local tab = self:czesc3(Vector3.new(7, 0.12, 1.6), CFrame.new(C + Vector3.new(lx * 0.9, 0.3, lz * 0.9)) * CFrame.Angles(0, math.atan2(lx, lz), 0),
			c.tusz, Enum.Material.SmoothPlastic, nil, f0)
		self:napis(tab, c.UI.twoje_legowisko, c.hex("9BFFB8"))
	end
	-- gniazdo z jajem tam, gdzie gracz się wykluwa (zestaw blender)
	if SK then
		SK:rekwizyt("Rekwizyt_gniazdo", CFrame.new(C + Vector3.new(lx * 0.97, 0, lz * 0.97)) * CFrame.Angles(0, math.atan2(lx, lz), 0), 0.8, f0)
	end
	local kupka = self:czesc3(Vector3.one, CFrame.new(C + Vector3.new(lx, 0, lz)), c.zloto, Enum.Material.Neon, Enum.PartType.Ball, f0)
	self:sztandar(slot, true)
	return { folder = f0, sig = sig, kupka = kupka, x = lx, z = lz, skarb = nil, skarbN = 0, slot = slot }
end

-- sztandar legowiska (świat, rekwizyt w scenie): płat w kolorze właściciela (kolor miejsca), wolne legowisko — kolor z danych
function Lg:sztandar(slot: number, zajete: boolean)
	local c = self.c
	local sw = c.kontener and c.kontener:FindFirstChild("Scena") and c.kontener.Scena:FindFirstChild("Swiat")
	local m = sw and sw:FindFirstChild("legowisko") and sw.legowisko:FindFirstChild("sztandar_" .. slot)
	local kol = c.D.swiat and c.D.swiat.kolory_legowisk and c.D.swiat.kolory_legowisk[((slot - 1) % #c.D.swiat.kolory_legowisk) + 1]
	if not (m and kol) then
		return
	end
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") and d:GetAttribute("Region") == 0 then
			if d:GetAttribute("KolorDanych") == nil then
				d:SetAttribute("KolorDanych", d.Color)
			end
			d.Color = if zajete then Color3.fromHex(kol) else d:GetAttribute("KolorDanych")
			d.Material = if zajete then Enum.Material.SmoothPlastic else d.Material
		end
	end
end

-- kopiec skarbu: rekwizyt 1–3 według zebranego w legowisku złota (zestaw blender), inaczej świecąca kula
function Lg:skarb(d, leg: number, t: number)
	local c = self.c
	local C = c.C
	local n = if leg < 1 then 0 elseif leg < 300 then 1 elseif leg < 3000 then 2 else 3
	if c.SK and c.wzorce and c.wzorce:FindFirstChild("Rekwizyt_skarb_1") then
		d.kupka.Transparency = 1
		if n ~= d.skarbN then
			if d.skarb then
				d.skarb:Destroy()
				d.skarb = nil
			end
			if n > 0 then
				-- świat: kopiec monet i klejnotów (stos_zlota), inaczej dawny skarb
				local nazwa = if c.wzorce:FindFirstChild("Rekwizyt_stos_zlota_" .. n) then "Rekwizyt_stos_zlota_" .. n else "Rekwizyt_skarb_" .. n
				d.skarb = c.SK:rekwizyt(nazwa, CFrame.new(C + Vector3.new(d.x, 0, d.z)), 0.75, d.folder)
			end
			d.skarbN = n
		end
		return
	end
	local s = if leg < 1 then 0.01 else 1.2 + math.min(5, math.log10(leg + 1) * 1.4)
	d.kupka.Size = Vector3.new(s, s * 0.6, s)
	d.kupka.Transparency = if leg < 1 then 1 else 0
	d.kupka.CFrame = CFrame.new(C + Vector3.new(d.x, s * 0.3 + math.sin(t * 2) * 0.1, d.z))
end

function Lg:krok(dt: number, t: number)
	self.doKroku -= dt
	if self.doKroku > 0 then
		return
	end
	self.doKroku = 0.25
	local c = self.c
	local fx, fz = c.mojaPoz()
	local zajete = {}
	for _, p in c.Players:GetPlayers() do
		local slot = p:GetAttribute("EW_Slot") or 0
		if slot > 0 then
			zajete[slot] = true
			local lx, lz = c.L.legowiskoPoz(c.D, slot)
			local d = self.leg[slot]
			if (lx - fx) ^ 2 + (lz - fz) ^ 2 < 170 * 170 then
				local sig = table.concat({ tostring(p:GetAttribute("EW_MaxForma")), p:GetAttribute("EW_Warianty") or "", p:GetAttribute("EW_Trofea") or "",
					tostring(p:GetAttribute("EW_Linia") or 1),
					p.Name }, "|")
				if not d or d.sig ~= sig then
					if d then
						d.folder:Destroy()
					end
					d = self:zbuduj(p, slot, sig)
					self.leg[slot] = d
				end
				self:skarb(d, p:GetAttribute("EW_ZlotoLeg") or 0, t)
			elseif d then
				d.folder:Destroy()
				self:sztandar(slot, false)
				self.leg[slot] = nil
			end
		end
	end
	for slot, d in self.leg do
		if not zajete[slot] then
			d.folder:Destroy()
			self:sztandar(slot, false)
			self.leg[slot] = nil
		end
	end
	local n = 0
	for _ in self.leg do
		n += 1
	end
	c.gracz:SetAttribute("EW_K_Legowisk", n)
end

return Lg
