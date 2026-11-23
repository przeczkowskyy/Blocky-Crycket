--[[
	SmokiKlienta — smoki z modeli Blendera po stronie klienta (zestaw „blender”): klony rigów z Wzorce (pełny i uproszczony),
	przemalowanie regionów (warianty), klipy (RigiEwolucji) podpięte pod stany gry, koszt (pełny rig / uproszczony / rzadziej /
	zamrożony według odległości), światło i żar z zaczepów, ślady, stożek ognia (Beam + cząsteczki), korona, cokoły,
	golem-boss. Wszystko wbudowane (części, Beam, Trail, ParticleEmitter, PointLight) — bez wgrań.
]]
local KL = require(script.Parent:WaitForChild("KlipyEwolucji"))
local Rigi = require(script.Parent:WaitForChild("RigiEwolucji"))

local S = {}
S.__index = S
S.Rigi = Rigi
S.KL = KL

local REGIONY = { "cialo", "luski", "brzuch", "blona", "kolce", "zar", "oko", "stale", "zar_rdzen" }
-- dawne nazwy kotwic (efekty walki) → zaczepy rigu
local ZACZEP = { Pysk = "PyskAttachment", Ogon = "OgonKoniecAttachment", SkrzydloL = "SkrzydloLKoniecAttachment",
	SkrzydloP = "SkrzydloPKoniecAttachment", Brzuch = "BrzuchAttachment", Glowa = "GlowaAttachment", Gardlo = "GardloAttachment",
	Piers = "PiersAttachment", Grzbiet = "GrzbietAttachment" }

function S.nowe(c)
	-- c: D, wzorce, lokalne, Http, kamera
	local self = setmetatable({}, S)
	self.c, self.D = c, c.D
	S.Dlinie = c.D.odrodzenie and c.D.odrodzenie.linie
	self.LOD = (c.D.blender and c.D.blender.lod) or {}
	self.zestawy = {}
	self.swiatla = 0
	self.licznik = 0
	self.wszystkie = {} -- klipy zagrane przez wszystkie stworki w sesji (próby)
	return self
end

function S:klipy(id: string)
	local W = self.zestawy[id]
	if W == nil then
		local f = self.c.wzorce and self.c.wzorce:FindFirstChild("Klipy")
		local v = f and f:FindFirstChild(id)
		W = if v then KL.przygotuj(self.c.Http:JSONDecode(v.Value)) else false
		self.zestawy[id] = W
	end
	return W or nil
end

-- wariant: kolory regionów (części z atrybutem Region; oko i stałe zostają); tęcza — odcienie na ciele i błonie
function S.przemaluj(model: Instance, id: string?, paleta)
	if not (id and paleta) then
		return
	end
	local i = 0
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") then
			local r = d:GetAttribute("Region")
			local nazwa = r and REGIONY[r + 1]
			if nazwa and paleta[nazwa] then
				d.Color = Color3.fromHex(paleta[nazwa])
				if id == "tecza" and (r == 0 or r == 3) then
					i += 1
					d.Color = Color3.fromHSV((i * 0.137) % 1, 0.62, 1)
				elseif id == "krysztal" and (r == 0 or r == 3) then
					d.Material = Enum.Material.Glass
					d.Transparency = math.max(d.Transparency, 0.12)
				elseif id == "zloty" and (r == 0 or r == 1) then
					d.Material = Enum.Material.Metal
				elseif id == "rubin" and r == 0 then
					d.Material = Enum.Material.Glass
				end
			end
		end
	end
end

-- odrodzenie1: kolory linii smoków (regiony z palety linii; bez regionów — części zabarwione kolorem linii)
function S.barwLinii(model: Instance, linia: number?)
	local LI = S.Dlinie and linia and S.Dlinie[linia]
	if not (LI and LI.paleta) then
		return
	end
	local ile = 0
	for _, d in model:GetDescendants() do
		if d:IsA("BasePart") and d:GetAttribute("Region") ~= nil then
			ile += 1
		end
	end
	if ile > 0 then
		S.przemaluj(model, LI.id, LI.paleta)
	else
		local k = Color3.fromHex(LI.kolor)
		for _, d in model:GetDescendants() do
			if d:IsA("BasePart") and d.Transparency < 1 then
				d.Color = d.Color:Lerp(k, 0.6)
			end
		end
	end
end

-- pełny albo uproszczony rig widoku (klon wzorca, wariant, odtwarzacz); zwraca model
function S:zbuduj(w, F, lod: boolean, W0)
	local nazwa = if lod then (F.wzorzecLod or F.wzorzec) else F.wzorzec
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild(nazwa)
	if not wz then
		return nil
	end
	local m = wz:Clone()
	if w.linia and w.linia > 1 then
		S.barwLinii(m, w.linia)
	end
	if W0 then
		S.przemaluj(m, W0.id, self.D.blender.warianty[W0.id])
	end
	local n = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			n += 1
			if lod and d.Transparency < 1 then
				d.CastShadow = false
			end
		end
	end
	m.Parent = self.c.lokalne
	local Wk = self:klipy(F.rig)
	if not Wk then
		m:Destroy()
		return nil
	end
	local stary = w.R
	w.R = Rigi.nowy(m, Wk, 1)
	-- liczniki klipów trwają przez przebudowy modelu (forma, LOD) — próby sprawdzają podpięte stany
	w.grane = w.grane or {}
	w.R.grane = w.grane
	w.R.wspolne = self.wszystkie
	-- ciągłość: ta sama pętla i akcja po zmianie modelu (LOD)
	if stary then
		w.R.loko = stary.loko
		w.R.akcja = stary.akcja
	end
	w.lod = lod
	w.zaczepy = {}
	w.czesciN = n
	w.efekty = nil
	return m
end

-- zaczep po nazwie (dawne nazwy kotwic też); pozycja w świecie
function S.zaczep(w, nazwa: string): Attachment?
	if not w.zaczepy then
		return nil
	end
	local a = w.zaczepy[nazwa]
	if a == nil then
		a = w.model and w.model:FindFirstChild(ZACZEP[nazwa] or nazwa, true) or false
		w.zaczepy[nazwa] = a
	end
	return a or nil
end

-- KNIGHT GOLEM (boss lasu) na stopniu 1–5: rig i klipy z danych
function S:zbudujGolema(w, stopien: number)
	local G = self.D.blender and self.D.blender.golem
	if not G then
		return nil
	end
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild(string.format(G.model, stopien))
	local Wk = self:klipy(string.format(G.klipy, stopien))
	if not (wz and Wk) then
		return nil
	end
	local m = wz:Clone()
	local sk = G.skala or 1
	if sk ~= 1 then
		pcall(function()
			m:ScaleTo(sk)
		end)
	end
	m.Parent = self.c.lokalne
	w.R = Rigi.nowy(m, Wk, sk)
	w.grane = w.grane or {}
	w.R.grane = w.grane
	w.R.wspolne = self.wszystkie
	w.lod = false
	w.zaczepy = {}
	w.golemStopien = stopien
	local n = 0
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			n += 1
		end
	end
	w.czesciN = n
	return m
end

-- poziom kosztu: { lod = bool, co = co ile klatek animacja } z odległości od kamery / gracza, z histerezą
function S:poziom(w, moj: boolean, d: number, widac: boolean)
	local L = self.LOD
	if moj then
		return false, 1
	end
	local prog = if w.slot > 0 then L.odl_pelny_gracz or 90 else L.odl_pelny_bot or 45
	local hist = L.histereza or 8
	local lod = if w.lod then d > prog - hist else d > prog + hist
	local co
	if not widac or d > (L.odl_stop or 170) then
		co = L.co_stop or 12
	elseif d < 45 then
		co = L.co_blisko or 2
	else
		co = L.co_daleko or 4
	end
	return lod, co
end

-- pętla ruchu z prędkości (stopy bez poślizgu w granicach tempa); nadpisanie (ogień, szybowanie, cokół) ma pierwszeństwo
function S:ruch(w, v: number, vMaks: number)
	local R = w.R
	local W = R.W
	if w.petlaNad and W.klipy[w.petlaNad] then
		R:petla(w.petlaNad, 1)
		return
	end
	local L = self.LOD
	-- dane 3: chód 7 i bieg 18 studs/s w każdym stadium; tempo = prędkość po ziemi / predkosc, przełączenie przy
	-- środku geometrycznym (≈11,2) z histerezą, przenikanie pętli w Rigi (0,18 s, faza zachowana)
	local nazwa, tempo = KL.chodBieg(W, v, R:petlaNazwa(), { skala = R.skala, mn = L.tempo_min or 0.1,
		mx = L.tempo_maks or 3, prog = L.bieg_od, hist = L.bieg_hist or 1.5, szybki = w.szybki })
	w.petlaRuchu, w.tempoRuchu = nazwa, tempo
	R:petla(nazwa, tempo)
end

-- start akcji z wyrównaniem do zdarzenia: zdarzenie wypada po `za` sekundach od teraz
function S.grajNa(w, klip: string, zdarzenie: string?, za: number?, o)
	local R = w.R
	if not R then
		return false
	end
	o = o or {}
	if zdarzenie then
		local tz = KL.czasZdarzenia(R.W, klip, zdarzenie, nil)
		if tz then
			o.od = math.max(0, tz - (za or 0))
		end
	end
	return R:graj(klip, o)
end

-- stany gry → klipy (nazwy zgodne z modele/dane)
local KLIP_ZD = { zar = { "splun", "strzal" }, oddech = { "ogien_start", "ogien_start" }, inferno = { "ogien_start", "ogien_start" },
	ogon = { "ogon_zamach", "uderzenie_start" }, ryk = { "ryk", "ryk_start" }, lot = { "szybowanie_start", "odbicie" },
	meteor = { "nurkowanie_skok", "odbicie" } }
S.KLIP_ZD = KLIP_ZD

function S.zamach(w, A)
	local e = KLIP_ZD[A.id]
	if not (e and w.R) then
		return
	end
	if A.id == "lot" or A.id == "meteor" then
		w.bezLotu = -1.2
	end
	-- serwer liczy zamach do zdarzenia klipu (DaneEwolucji: formy[f].czasy) — klip od zera, zdarzenie w tej samej chwili
	w.R:graj(e[1], { trzymaj = A.id == "meteor" or A.id == "lot" })
end

function S.kanal(w, start: boolean)
	if not w.R then
		return
	end
	if start then
		w.petlaNad = "ogien_petla"
	elseif w.petlaNad == "ogien_petla" then
		w.petlaNad = nil
		w.R:graj("ogien_koniec")
	end
end

function S.lot(w, typ: string)
	if not w.R then
		return
	end
	if typ == "lot" then
		w.petlaNad = "szybowanie_petla"
		w.R:przerwij(0.2)
	end
end

function S.ladowanie(w, typ: string)
	if not w.R then
		return
	end
	if w.petlaNad == "szybowanie_petla" then
		w.petlaNad = nil
	end
	if typ == "meteor" then
		S.grajNa(w, "nurkowanie_ladowanie", "uderzenie", 0.02, { wejscie = 0.04 })
	else
		S.grajNa(w, "szybowanie_ladowanie", "ladowanie", 0.02, { wejscie = 0.05 })
	end
end

S.DLUGI_OD = 0.9

function S.rana(w, przewrot: boolean, przewrotS: number)
	if not w.R then
		return
	end
	if przewrot then
		-- dane 3: krótki koziołek (14 klatek, 0,47 s) w tempie 1, ostatnia poza trzymana do końca przewrotu (0,5 s);
		-- długie przewroty (od dlugi_od s) — koziolek_dlugi (1,2 s, z wstawaniem) dopasowany do czasu przewrotu
		local W = w.R.W
		local kd = W.klipy.koziolek_dlugi
		if kd and przewrotS >= S.DLUGI_OD then
			w.R:graj("koziolek_dlugi", { tempo = math.clamp(kd.dl / (przewrotS + 0.35), 0.7, 1.6), wejscie = 0.04 })
		else
			local k = W.klipy.koziolek
			w.R:graj("koziolek", { tempo = if k and k.dl > przewrotS + 0.05 then k.dl / przewrotS else 1, wejscie = 0.04,
				trzymajS = if k then math.max(0, przewrotS - k.dl) else 0 })
		end
	else
		w.R:graj("trafienie", { slaby = true, wejscie = 0.03 })
	end
end

-- ---------------------------------------------------------------- efekty z zaczepów (tylko pełne rigi blisko)
local function emiter(rodzic: Instance, kolor: Color3, rozm: number, tempo: number): ParticleEmitter
	local p = Instance.new("ParticleEmitter")
	p.Color = ColorSequence.new(Color3.new(1, 0.95, 0.6), kolor)
	p.LightEmission = 1
	p.LightInfluence = 0
	p.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, rozm), NumberSequenceKeypoint.new(1, 0) })
	p.Transparency = NumberSequence.new(0.1, 1)
	p.Lifetime = NumberRange.new(0.6, 1.1)
	p.Speed = NumberRange.new(1.5, 3.5)
	p.SpreadAngle = Vector2.new(25, 25)
	p.Acceleration = Vector3.new(0, 4, 0)
	p.Rate = tempo
	p.EmissionDirection = Enum.NormalId.Top
	p.Parent = rodzic
	return p
end

-- żar i światło rosną ze stadium; ślady ogona i skrzydeł (włączane w zrywie i locie)
function S:efekty(w, stadium: number, wlacz: boolean, swiatlo: boolean?)
	if not wlacz then
		if w.efekty then
			for _, o in w.efekty.lista do
				o:Destroy()
			end
			if w.efekty.swiatlo then
				self.swiatla -= 1
			end
			w.efekty = nil
		end
		return
	end
	if w.efekty then
		return
	end
	local E = { lista = {} }
	local kol = Color3.fromRGB(255, 120, 40)
	if stadium >= 3 then
		for _, n in { "Zar1Attachment", "Zar2Attachment", "Zar3Attachment" } do
			local a = w.model:FindFirstChild(n, true)
			if a then
				table.insert(E.lista, emiter(a, kol, 0.12 + stadium * 0.05, 1 + stadium * 0.6))
			end
		end
	end
	local g = w.model:FindFirstChild(if stadium >= 4 then "PiersAttachment" else "GardloAttachment", true)
	if g and stadium >= 2 and swiatlo and self.swiatla < 10 then
		local l = Instance.new("PointLight")
		l.Color = Color3.fromRGB(255, 140, 60)
		l.Range = 3 + stadium * 1.6
		l.Brightness = 0.5 + stadium * 0.18
		l.Shadows = false
		l.Parent = g
		table.insert(E.lista, l)
		E.swiatlo = l
		self.swiatla += 1
	end
	-- ślady: ogon (dwa zaczepy ogona) i końce skrzydeł (zaczep + przesunięty)
	local function slad(a0: Attachment?, a1: Attachment?, kolor: Color3)
		if not (a0 and a1) then
			return nil
		end
		local t = Instance.new("Trail")
		t.Attachment0, t.Attachment1 = a0, a1
		t.Lifetime = 0.3
		t.Color = ColorSequence.new(Color3.new(1, 1, 1), kolor)
		t.Transparency = NumberSequence.new(0.25, 1)
		t.LightEmission = 0.5
		t.FaceCamera = true
		t.Enabled = false
		t.Parent = a0.Parent
		table.insert(E.lista, t)
		return t
	end
	E.slady = {}
	local ogon = w.model:FindFirstChild("OgonKoniecAttachment", true)
	table.insert(E.slady, slad(ogon, w.model:FindFirstChild("ZarOgonAttachment", true), kol))
	for _, n in { "SkrzydloLKoniecAttachment", "SkrzydloPKoniecAttachment" } do
		local a = w.model:FindFirstChild(n, true)
		if a then
			local b = Instance.new("Attachment")
			b.Name = n .. "Slad"
			b.Position = a.Position + Vector3.new(0, -0.35 * stadium, 0)
			b.Parent = a.Parent
			table.insert(E.lista, b)
			table.insert(E.slady, slad(a, b, Color3.fromRGB(220, 240, 255)))
		end
	end
	w.efekty = E
end

function S.slady(w, wlacz: boolean)
	if w.efekty and w.efekty.slady then
		for _, t in w.efekty.slady do
			if t and t.Enabled ~= wlacz then
				t.Enabled = wlacz
			end
		end
	end
end

-- stożek ognia (FIRE BREATH / INFERNO), dane 3: rig `Efekt_ogien_stozek` (28 części, wachlarz ok. 60°, długość 10 wzdłuż −Z)
-- przypięty do PyskAttachment, skala = zasięg / 10, klip „migotanie” w pętli; z pyska dodatkowo żar (cząsteczki).
-- Dawną objętość z kul Neon zostawiamy tylko jako zapas, gdy wzorca rigu nie ma (decyzja: rig czyta się lepiej z kamery gry).
function S:stozek(w, zasieg: number, kat: number, inferno: boolean)
	local pysk = S.zaczep(w, "Pysk")
	if not pysk then
		return nil
	end
	local H = { lista = {}, kule = {}, zasieg = zasieg, szer = 2 * zasieg * math.tan(math.rad(kat / 2)) }
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild("Efekt_ogien_stozek")
	local Wk = wz and self:klipy("ogien_stozek")
	if wz and Wk then
		local m = wz:Clone()
		local sk = zasieg / 10
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") then
				d.CastShadow, d.CanQuery, d.CanTouch, d.CanCollide = false, false, false, false
				if inferno and d.Transparency < 1 then
					d.Color = d.Color:Lerp(Color3.fromRGB(255, 70, 190), 0.3)
				end
			end
		end
		pcall(function()
			m:ScaleTo(sk)
		end)
		m.Parent = self.c.lokalne
		H.R = Rigi.nowy(m, Wk, sk)
		H.R:petla("migotanie", 1)
		H.R.grane = w.grane or H.R.grane
		H.R.wspolne = self.wszystkie
		H.R:licz("migotanie")
		H.m = m
		table.insert(H.lista, m)
		self.licznikOgnia = (self.licznikOgnia or 0) + 1
	else
		local kol = if inferno then { Color3.fromRGB(255, 240, 150), Color3.fromRGB(255, 150, 60), Color3.fromRGB(255, 70, 190) }
			else { Color3.fromRGB(255, 245, 160), Color3.fromRGB(255, 160, 40), Color3.fromRGB(230, 60, 20) }
		for i = 1, 7 do
			local p = Instance.new("Part")
			p.Shape = Enum.PartType.Ball
			p.Anchored, p.CanCollide, p.CanQuery, p.CanTouch, p.CastShadow = true, false, false, false, false
			p.Material = Enum.Material.Neon
			local f = (i - 1) / 6
			p.Color = if f < 0.5 then kol[1]:Lerp(kol[2], f * 2) else kol[2]:Lerp(kol[3], (f - 0.5) * 2)
			p.Transparency = 0.25 + f * 0.4
			p.Parent = w.model
			table.insert(H.kule, p)
			table.insert(H.lista, p)
		end
	end
	local zew = if inferno then Color3.fromRGB(255, 70, 190) else Color3.fromRGB(230, 60, 20)
	local p = emiter(pysk, zew, 0.8 + zasieg * 0.04, 30)
	p.EmissionDirection = Enum.NormalId.Front
	p.Speed = NumberRange.new(zasieg * 1.4, zasieg * 2)
	p.Lifetime = NumberRange.new(0.3, 0.45)
	p.SpreadAngle = Vector2.new(kat / 2.5, kat / 4)
	p.Acceleration = Vector3.new(0, 3, 0)
	p.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, 0.4), NumberSequenceKeypoint.new(1, 1.2 + zasieg * 0.06) })
	table.insert(H.lista, p)
	return H
end

-- co klatkę: rig od pyska w kierunku patrzenia smoka (przód korzenia), lekko w dół ku ziemi na końcu zasięgu
function S.stozekKrok(w, H, t: number, dt: number?)
	local pysk = S.zaczep(w, "Pysk")
	local korzen = w.model and w.model.PrimaryPart
	if not (H and pysk and korzen) then
		return
	end
	local od = pysk.WorldPosition
	local kier = -korzen.CFrame.LookVector
	kier = Vector3.new(-kier.X, 0, -kier.Z)
	kier = if kier.Magnitude > 0.01 then kier.Unit else Vector3.new(0, 0, -1)
	if H.R then
		local wys = math.max(0, od.Y - (korzen.Position.Y - (if w.R then w.R.korzenOff.Y else 0)))
		local opad = math.atan2(wys * 0.6, H.zasieg)
		H.R:ustaw(CFrame.lookAt(od, od + kier) * CFrame.Angles(-opad, 0, 0))
		H.R:krok(dt or 1 / 60)
		return
	end
	local cz, cf = {}, {}
	for i, p in H.kule do
		local f = i / #H.kule
		local d = H.zasieg * (f * 0.92)
		local s = math.max(0.6, H.szer * f * 0.75) * (1 + math.sin(t * 23 + i * 1.7) * 0.08)
		p.Size = Vector3.new(s, s * 0.8, s)
		table.insert(cz, p)
		table.insert(cf, CFrame.new(od + kier * d + Vector3.new(0, -f * 0.6, 0)))
	end
	workspace:BulkMoveTo(cz, cf, Enum.BulkMoveMode.FireCFrameChanged)
end

function S.stozekKoniec(H)
	if H then
		for _, o in H.lista do
			o:Destroy()
		end
	end
end

-- przypalona ziemia INFERNO (dane 3): rekwizyt `Rekwizyt_przypalenie` (promień 10) w skali promień / 10; żar pulsuje i gaśnie
function S:przypalenie(E, poz: Vector3, r: number, czas: number): boolean
	-- wysokość ziemi pod plamą (płaty łąki leżą nad poziomem pola): promień w dół, bez własnych efektów i stworków
	local rp = RaycastParams.new()
	rp.FilterType = Enum.RaycastFilterType.Exclude
	rp.FilterDescendantsInstances = { self.c.lokalne }
	local traf = workspace:Raycast(poz + Vector3.new(0, 12, 0), Vector3.new(0, -24, 0), rp)
	local y = if traf then traf.Position.Y + 0.03 else poz.Y + 0.05
	local m = self:rekwizyt("Rekwizyt_przypalenie", CFrame.new(poz.X, y, poz.Z) * CFrame.Angles(0, math.random() * 6.28, 0), r / 10, self.c.lokalne)
	if not m then
		return false
	end
	local zar = {}
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.CanQuery, d.CanTouch, d.CanCollide = false, false, false
			if d.Material == Enum.Material.Neon then
				table.insert(zar, { d, d.Transparency })
			end
		end
	end
	self.licznikPrzypalen = (self.licznikPrzypalen or 0) + 1
	E:dodaj(czas, function(f)
		local puls = 0.5 + 0.5 * math.sin(f * czas * 7)
		local gas = math.clamp((f - 0.75) / 0.25, 0, 1)
		for _, z in zar do
			z[1].Transparency = math.clamp(z[2] + puls * 0.25 + gas * (1 - z[2]), 0, 1)
		end
	end, function()
		m:Destroy()
	end)
	return true
end

-- cokół trofeum z danych (rekwizyt) i trofeum: uproszczony rig w nieruchomej pozie „cokol”
function S:trofeum(F, W0, cf: CFrame, rozmiar: number, rodzic: Instance, ciemny: boolean, linia: number?)
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild(F.wzorzecLod or F.wzorzec)
	if not wz then
		return nil
	end
	local m = wz:Clone()
	if ciemny then
		for _, d in m:GetDescendants() do
			if d:IsA("BasePart") and d.Transparency < 1 then
				d.Color = Color3.fromRGB(20, 16, 24)
				d.Material = Enum.Material.SmoothPlastic
			end
		end
	else
		-- retencja1: trofea w kolorach linii właściciela (EMBER, FROST, STORM, SHADOW), wariant na wierzchu
		if linia and linia > 1 then
			S.barwLinii(m, linia)
		end
		if W0 then
			S.przemaluj(m, W0.id, self.D.blender.warianty[W0.id])
		end
	end
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.CastShadow = false
		end
	end
	local sk = rozmiar / F.model_r
	pcall(function()
		m:ScaleTo(sk)
	end)
	m.Parent = rodzic
	local Wk = self:klipy(F.rig)
	if Wk then
		local r = Rigi.zamroz(m, Wk, "cokol", 0.4)
		self.licznik += 1 -- trofea w pozie „cokol” (próby)
		r.skala = sk
		r.korzenOff = (m:GetAttribute("KorzenPoz") or Vector3.zero) * sk
		r:zastosuj()
		r:ustaw(cf)
	else
		m:PivotTo(cf)
	end
	return m
end

-- rekwizyt (cokół, skarb, gniazdo): klon w miejscu
function S:rekwizyt(nazwa: string, cf: CFrame, skala: number?, rodzic: Instance)
	local wz = self.c.wzorce and self.c.wzorce:FindFirstChild(nazwa)
	if not wz then
		return nil
	end
	local m = wz:Clone()
	for _, d in m:GetDescendants() do
		if d:IsA("BasePart") then
			d.Anchored = true
			d.CastShadow = false
		end
	end
	if skala and skala ~= 1 then
		pcall(function()
			m:ScaleTo(skala)
		end)
	end
	m:PivotTo(cf)
	m.Parent = rodzic
	return m
end

return S
