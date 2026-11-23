--[[
	SwiatKlienta — świat (swiat1) po stronie klienta: światło i niebo z liczb modele/README (ustawiane w grze, nie w trybie Edit;
	tylko lokalnie u gracza), nastrój stref (DEEP WOODS, wyspa lawy) z płynnym przejściem, kule z modeli danych (trzy rozmiary,
	unoszenie blisko gracza), owce z migawki serwera (rig i klipy: spoczynek, chod, ucieczka, zjedzona).
]]
local Lighting = game:GetService("Lighting")

local SW = {}
SW.__index = SW

local function rgb(t)
	return Color3.fromRGB(t[1], t[2], t[3])
end

function SW.nowe(c)
	-- c: D, wzorce, lokalne, C, SK, L
	local self = setmetatable({}, SW)
	self.c = c
	self.D = c.D
	self.kule = {}
	self.krople = {}
	self.zloteKule = 0
	self.owce = {}
	self.blisko = {}
	self.doBliskich = 0
	self.nastroj = { las = 0, lawa = 0 }
	self:swiatlo()
	return self
end

-- światło i niebo: liczby z ustawienia.json → swiat.swiatlo (z modele/README), tylko u tego klienta, od startu gry
function SW:swiatlo()
	local S = self.D.swiat and self.D.swiat.swiatlo
	if not S then
		return
	end
	pcall(function()
		Lighting.ClockTime = S.ClockTime
		Lighting.GeographicLatitude = S.GeographicLatitude
		Lighting.Brightness = S.Brightness
		Lighting.ExposureCompensation = S.ExposureCompensation
		Lighting.ShadowSoftness = S.ShadowSoftness
		Lighting.EnvironmentDiffuseScale = S.EnvironmentDiffuseScale
		Lighting.EnvironmentSpecularScale = S.EnvironmentSpecularScale
		Lighting.Ambient = rgb(S.Ambient)
		Lighting.OutdoorAmbient = rgb(S.OutdoorAmbient)
		Lighting.ColorShift_Top = rgb(S.ColorShift_Top)
	end)
	local function jeden(klasa: string, nazwa: string, rodzic: Instance)
		for _, d in rodzic:GetChildren() do
			if d:IsA(klasa) and d.Name ~= nazwa then
				d.Parent = nil -- inne tego typu (z miejsca) wyłączone na czas gry u tego gracza
			end
		end
		local o = rodzic:FindFirstChild(nazwa) or Instance.new(klasa)
		o.Name = nazwa
		o.Parent = rodzic
		return o
	end
	local A = jeden("Atmosphere", "EwolucjaAtmosfera", Lighting)
	A.Density, A.Offset, A.Color, A.Decay, A.Glare, A.Haze = S.atmosfera.Density, S.atmosfera.Offset, rgb(S.atmosfera.Color), rgb(S.atmosfera.Decay),
		S.atmosfera.Glare, S.atmosfera.Haze
	self.atm = A
	local niebo = jeden("Sky", "EwolucjaNiebo", Lighting)
	niebo.SunAngularSize = S.SunAngularSize
	niebo.StarCount = 0
	local ok = pcall(function()
		local ch = workspace.Terrain:FindFirstChildOfClass("Clouds") or Instance.new("Clouds")
		ch.Cover, ch.Density, ch.Color = S.chmury.Cover, S.chmury.Density, rgb(S.chmury.Color)
		ch.Parent = workspace.Terrain
	end)
	local _ = ok
	local B = jeden("BloomEffect", "EwolucjaBloom", Lighting)
	B.Intensity, B.Size, B.Threshold = S.bloom.Intensity, S.bloom.Size, S.bloom.Threshold
	local K = jeden("ColorCorrectionEffect", "EwolucjaKorekta", Lighting)
	K.Saturation, K.Contrast, K.TintColor = S.korekta.Saturation, S.korekta.Contrast, rgb(S.korekta.TintColor)
	local P = jeden("SunRaysEffect", "EwolucjaPromienie", Lighting)
	P.Intensity, P.Spread = S.promienie.Intensity, S.promienie.Spread
	self.S = S
end

-- nastrój strefy (las, wyspa lawy) — płynnie, według pozycji własnego smoka
function SW:krokNastroju(dt: number, ja)
	local S = self.S
	if not (S and self.atm and ja) then
		return
	end
	local D = self.D
	local L = self.c.L
	local wLesie = L.wLesie(D, ja.x, ja.z)
	local WY = D.wyspa
	local wLawie = WY and math.sqrt((ja.x - WY.x) ^ 2 + (ja.z - WY.z) ^ 2) < WY.r_zew + 12
	local a = math.min(1, dt * 1.5)
	self.nastroj.las += ((if wLesie then 1 else 0) - self.nastroj.las) * a
	self.nastroj.lawa += ((if wLawie then 1 else 0) - self.nastroj.lawa) * a
	local fl, fw = self.nastroj.las, self.nastroj.lawa
	local A = S.atmosfera
	local gest = A.Density + (S.las.Density - A.Density) * fl + (S.lawa.Density - A.Density) * fw
	local kol = rgb(A.Color):Lerp(rgb(S.las.Color), fl):Lerp(rgb(S.lawa.Color), fw)
	local haze, decay, tint = A.Haze, rgb(A.Decay), rgb(S.korekta.TintColor)
	-- mapa2a: nastrój stref v2 (Ukryta Polana, Lily Lake, Sealed Gate, Szlak Popiołu) — płynnie jak las i lawa
	local N2 = D.mapa2 and D.mapa2.nastroj
	if N2 then
		self.wagi = self.wagi or {}
		local tu = nil
		for _, o in D.mapa2.obszar do
			if N2[o.s] and L.wObrysie(o, ja.x, ja.z) then
				tu = o.s
				break
			end
		end
		for sid, n in N2 do
			local wg = (self.wagi[sid] or 0) + ((if sid == tu then 1 else 0) - (self.wagi[sid] or 0)) * a
			self.wagi[sid] = wg
			if wg > 0.001 then
				if n["Atmosphere.Density"] then
					gest += (n["Atmosphere.Density"] - gest) * wg
				end
				if n["Atmosphere.Color"] then
					kol = kol:Lerp(rgb(n["Atmosphere.Color"]), wg)
				end
				if n["Atmosphere.Haze"] then
					haze += (n["Atmosphere.Haze"] - haze) * wg
				end
				if n["Atmosphere.Decay"] then
					decay = decay:Lerp(rgb(n["Atmosphere.Decay"]), wg)
				end
				if n["ColorCorrection.TintColor"] then
					tint = tint:Lerp(rgb(n["ColorCorrection.TintColor"]), wg)
				end
			end
		end
		self.atm.Haze = haze
		self.atm.Decay = decay
		local K = Lighting:FindFirstChild("EwolucjaKorekta")
		if K then
			K.TintColor = tint
		end
		self.strefaNastroju = tu
	end
	self.atm.Density = gest
	self.atm.Color = kol
	Lighting.Brightness = S.Brightness + (S.las.Brightness - S.Brightness) * fl
end

-- kule z modeli danych (kula_mala / duza / wielka); część główna zostaje w tablicach klienta (pozycja, kolor efektów)
local WZOR_KULI = { [1] = "Rekwizyt_kula_mala", [2] = "Rekwizyt_kula_duza", [3] = "Rekwizyt_kula_wielka" }
function SW:ubierzKule(i: number, glowna: BasePart, typ: number): boolean
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild(WZOR_KULI[typ] or "")
	if not wz then
		return false
	end
	local m = wz:Clone()
	local czesci, offs, przez = {}, {}, {}
	local baza = CFrame.new(glowna.Position - Vector3.new(0, 1, 0))
	m:PivotTo(baza)
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			if d.Transparency < 1 then
				d.Anchored, d.CanCollide, d.CanQuery, d.CanTouch, d.CastShadow = true, false, false, false, false
				table.insert(czesci, d)
				table.insert(offs, baza:ToObjectSpace(d.CFrame))
				table.insert(przez, d.Transparency)
			else
				d:Destroy()
			end
		end
	end
	for _, d in m:GetDescendants() do
		if d:IsA("JointInstance") or d:IsA("WeldConstraint") then
			d:Destroy()
		end
	end
	m.Parent = self.c.lokalne
	glowna.Transparency = 1
	self.kule[i] = { m = m, czesci = czesci, offs = offs, przez = przez, baza = baza, zywa = true }
	return true
end

function SW:kula(i: number, zywa: boolean): boolean
	local k = self.kule[i]
	if not k then
		return false
	end
	if k.zywa ~= zywa then
		k.zywa = zywa
		for j, p in k.czesci do
			p.Transparency = if zywa then k.przez[j] else 1
		end
		if zywa and self.deszczTeraz and k.lakowa then
			self:kropla(k.baza.Position)
		end
	end
	return true
end

-- odrodzenie1: DRAGON RAIN — kule łąki złote (Neon), nowa kula spada z nieba złotą kroplą
function SW:deszcz(tak: boolean)
	if self.deszczTeraz == tak then
		return
	end
	self.deszczTeraz = tak
	local L, D = self.c.L, self.c.D
	local zlote = 0
	for i, k in self.kule do
		local p = D.kulkiPoz[i]
		k.lakowa = p ~= nil and not L.wLesie(D, p[1], p[2]) and not L.naWyspie(D, p[1], p[2])
		if k.lakowa then
			k.kolory = k.kolory or {}
			for j, c in k.czesci do
				if tak then
					k.kolory[j] = k.kolory[j] or { c.Color, c.Material }
					c.Color = Color3.fromRGB(255, 201, 52)
					c.Material = Enum.Material.Neon
				elseif k.kolory[j] then
					c.Color, c.Material = k.kolory[j][1], k.kolory[j][2]
				end
			end
			zlote += 1
		end
	end
	self.zloteKule = if tak then zlote else 0
end

function SW:kropla(cel: Vector3)
	if #self.krople > 24 then
		return
	end
	local p = Instance.new("Part")
	p.Shape = Enum.PartType.Ball
	p.Size = Vector3.new(1.1, 1.1, 1.1)
	p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
	p.Material = Enum.Material.Neon
	p.Color = Color3.fromRGB(255, 214, 90)
	p.Position = cel + Vector3.new(0, 30, 0)
	p.Parent = self.c.lokalne
	table.insert(self.krople, { p = p, t = 0, cel = cel })
end

function SW:krokKropli(dt: number)
	for i = #self.krople, 1, -1 do
		local q = self.krople[i]
		q.t += dt
		local f = math.min(1, q.t / 0.55)
		q.p.Position = q.cel + Vector3.new(0, 30 * (1 - f * f), 0)
		if f >= 1 then
			q.p:Destroy()
			table.remove(self.krople, i)
		end
	end
end

-- unoszenie i obrót kul blisko gracza (lista bliskich odświeżana co 0,5 s)
function SW:krokKul(dt: number, t: number, ja)
	if not ja then
		return
	end
	self.doBliskich -= dt
	if self.doBliskich <= 0 then
		self.doBliskich = 0.5
		table.clear(self.blisko)
		local C = self.c.C
		for i, k in self.kule do
			local p = k.baza.Position - C
			if (p.X - ja.x) ^ 2 + (p.Z - ja.z) ^ 2 < 85 * 85 then
				table.insert(self.blisko, i)
			end
		end
	end
	local cz, cf = {}, {}
	for _, i in self.blisko do
		local k = self.kule[i]
		if k.zywa then
			local b = k.baza * CFrame.new(0, math.sin(t * 3 + i) * 0.25, 0) * CFrame.Angles(0, t * 0.8 + i, 0)
			for j, p in k.czesci do
				table.insert(cz, p)
				table.insert(cf, b * k.offs[j])
			end
		end
	end
	if #cz > 0 then
		workspace:BulkMoveTo(cz, cf, Enum.BulkMoveMode.FireCFrameChanged)
	end
end

-- owce z migawki: bufor od offsetu (liczba u8, potem po 11 bajtów)
function SW:owceZMigawki(b: buffer, o: number)
	if buffer.len(b) <= o then
		return
	end
	local n = buffer.readu8(b, o)
	for i = 1, n do
		local q = o + 1 + (i - 1) * 11
		local x, z = buffer.readf32(b, q), buffer.readf32(b, q + 4)
		local kier = buffer.readi16(b, q + 8) / 1000
		local stan = buffer.readu8(b, q + 10)
		local w = self.owce[i]
		if not w then
			w = self:nowaOwca(i, x, z)
		end
		if w then
			if (w.stan == 3) ~= (stan == 3) and stan ~= 3 then
				w.x, w.z = x, z -- wróciła: skok na nowe miejsce
				w.zjedzonaDo = nil
			end
			w.tx, w.tz, w.tkier, w.stan = x, z, kier, stan
		end
	end
end

function SW:nowaOwca(i: number, x: number, z: number)
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild("Stwor_owca")
	local W = self.c.SK and self.c.SK:klipy("owca")
	if not (wz and W) then
		return nil
	end
	local m = wz:Clone()
	m.Parent = self.c.lokalne
	local R = self.c.SK.Rigi.nowy(m, W, 1)
	R.wspolne = self.c.SK.wszystkie
	local w = { m = m, R = R, x = x, z = z, tx = x, tz = z, kier = 0, tkier = 0, stan = 0, ukryta = false, n = i % 2 }
	self.owce[i] = w
	return w
end

function SW:owcaZjedzona(i: number)
	local w = self.owce[i]
	if w then
		w.R:graj("zjedzona", { wejscie = 0.03, trzymaj = true })
		w.zjedzonaDo = os.clock() + 0.75
	end
end

local function ukryj(w, tak: boolean)
	if w.ukryta == tak then
		return
	end
	w.ukryta = tak
	for _, d in w.m:GetDescendants() do
		if d:IsA("BasePart") then
			d.LocalTransparencyModifier = if tak then 1 else 0
		end
	end
end

function SW:krokOwiec(dt: number, ja)
	local C = self.c.C
	for _, w in self.owce do
		local a = 1 - math.exp(-dt * 10)
		local ox, oz = w.x, w.z
		w.x += (w.tx - w.x) * a
		w.z += (w.tz - w.z) * a
		local dk = (w.tkier - w.kier + math.pi) % (2 * math.pi) - math.pi
		w.kier += dk * math.min(1, dt * 10)
		local martwa = w.stan == 3 and not (w.zjedzonaDo and os.clock() < w.zjedzonaDo)
		local daleko = ja and ((w.x - ja.x) ^ 2 + (w.z - ja.z) ^ 2 > 140 * 140)
		ukryj(w, martwa or daleko)
		if not (martwa or daleko) then
			w.R:ustaw(CFrame.new(C + Vector3.new(w.x, 0, w.z)) * CFrame.Angles(0, w.kier + math.pi, 0))
			local sp = math.sqrt((w.x - ox) ^ 2 + (w.z - oz) ^ 2) / math.max(dt, 1 / 240)
			w.v = (w.v or 0) + (sp - (w.v or 0)) * math.min(1, dt * 10)
			if w.R:akcjaNazwa() == nil then
				-- tempo z prędkości po ziemi / predkosc klipu (owca: chód 1,76, ucieczka 5,0 studs/s)
				local KL = self.c.SK.KL
				local W = w.R.W
				if w.stan == 2 and W.klipy.ucieczka then
					w.R:petla("ucieczka", KL.tempo(W.klipy.ucieczka, math.max(w.v, 2), 1, 0.3, 3))
				elseif w.v > 0.5 then
					w.R:petla("chod", KL.tempo(W.klipy.chod, w.v, 1, 0.3, 3))
				else
					w.R:petla("spoczynek", 1)
				end
				w.tempoRuchu = w.R.loko.tempo
			end
			w.n += 1
			w.dt = (w.dt or 0) + dt
			if w.n % 2 == 0 then
				w.R:krok(w.dt)
				w.dt = 0
			end
		elseif w.stan ~= 3 and w.R:akcjaNazwa() == "zjedzona" then
			w.R:przerwij(0.01)
		end
	end
end

function SW:krok(dt: number, t: number, ja)
	self:krokNastroju(dt, ja)
	self:krokKul(dt, t, ja)
	self:krokOwiec(dt, ja)
	self:krokKropli(dt)
end

return SW
